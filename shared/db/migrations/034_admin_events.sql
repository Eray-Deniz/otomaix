-- Migration 034: Sektör bilgi paketi — yönetici bildirim OUTBOX'ı
--
-- Kapsam (plan Task 14; bağlanan teknik karar 6):
--   1. social.admin_events — transactional outbox + kira protokolü
--
-- Neden outbox, neden doğrudan webhook DEĞİL: bildirim, haber verdiği İŞLE
-- aynı kaderi paylaşmalıdır. Doğrudan gönderimde geri alınan bir işin bildirimi
-- yola çıkmış olurdu; outbox satırı iş transaction'ıyla BİRLİKTE commit edilir,
-- iletim commit SONRASI ayrı bir adımdır.
--
-- Kira (`lease_expires_at`) neden var: `sending` kalıcı bir durum değil, SÜRELİ
-- bir sahiplik iddiasıdır. Kirasız bir "işleniyor" durumu, çöken bir işçinin
-- satırı sonsuza dek askıda bırakmasına izin verirdi.
--
-- Kira JETONU ayrı bir kolon DEĞİLDİR: `(attempt_count, lease_expires_at)`
-- çifti jetondur. Her claim `attempt_count`'u atomik artırdığı için yeniden
-- claim edilen satırın çifti kesin olarak değişir ve bayat işçinin finalize'ı
-- eşleşmez. Ayrı bir jeton kolonu aynı işi yapardı ama plan şemasında yoktur;
-- zaman damgası TEK BAŞINA jeton olamaz (iki claim aynı mikrosaniyeye düşerse
-- ayırt edilemez).

-- ---------------------------------------------------------------------------
-- 1. Outbox tablosu
-- ---------------------------------------------------------------------------
--
-- `kind` CHECK ile KAPATILMAZ ve bu bilinçlidir — `package_events.event_type`in
-- aksine. Sebep: bu tablo genel bir yönetici bildirim taşıyıcısıdır ve Plan 2
-- (K-26 vade bildirimi) aynı altyapıyı yeni bir `kind` ile çağırır. Kümeyi
-- CHECK'e almak, her yeni bildirim türü için migration zorunlu kılardı; olay
-- kaydının aksine burada kapalılık bir GÜVENCE değil, sürtünme olurdu.
--
-- `delivery_state` ise kapalıdır: dört durumun dışında bir değer, kira
-- protokolünün sorgularını sessizce boşa çıkarır (claim yüklemi eşleşmez,
-- satır görünmez olur).
--
-- `idempotency_key` UNIQUE: alıcı tarafın (n8n) dedupe girdisi ve yazım
-- tarafının tekrar-koruması aynı anahtardır. İki ayrı anahtar olsaydı
-- "yazıldı ama başka anahtarla gönderildi" penceresi doğardı.

CREATE TABLE IF NOT EXISTS social.admin_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kind TEXT NOT NULL,
    payload JSONB NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    delivery_state TEXT NOT NULL DEFAULT 'pending',
    lease_expires_at TIMESTAMPTZ,
    attempt_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT admin_events_delivery_state_check CHECK (delivery_state IN (
        'pending', 'sending', 'sent', 'failed'
    )),
    -- Kira YALNIZ `sending` durumunda anlamlıdır. `sent`/`failed`/`pending` bir
    -- satırın üstünde duran kira, "bu satırın sahibi var" diye okunabilecek
    -- yetim bir iddiadır; kısıt o durumu doğmadan keser.
    CONSTRAINT admin_events_lease_state_check CHECK (
        (delivery_state = 'sending') = (lease_expires_at IS NOT NULL)
    ),
    CONSTRAINT admin_events_attempt_count_check CHECK (attempt_count >= 0)
);

-- Claim sorgusunun tek erişim yolu: teslim edilmemiş satırlar, en eskiden yeniye.
-- Terminal satırlar (`sent`/`failed`) indekse HİÇ girmez — outbox büyüdükçe
-- claim maliyeti açık iş sayısıyla sınırlı kalır.
CREATE INDEX IF NOT EXISTS idx_admin_events_claimable
    ON social.admin_events (created_at)
    WHERE delivery_state IN ('pending', 'sending');

-- ---------------------------------------------------------------------------
-- 2. Belgeleme
-- ---------------------------------------------------------------------------

COMMENT ON TABLE social.admin_events IS
    'Yonetici bildirim OUTBOX u (plan Task 14). Satir, tetikleyen is transaction iyla BIRLIKTE commit edilir; iletim commit SONRASI ayri dispatch adimidir. kind KAPALI DEGIL (Plan 2 yeni turler ekler), delivery_state KAPALI.';
COMMENT ON COLUMN social.admin_events.delivery_state IS
    'pending -> sending (kira) -> sent | failed. sending SURELI bir sahiplik iddiasidir.';
COMMENT ON COLUMN social.admin_events.lease_expires_at IS
    'Kira bitisi. YALNIZ delivery_state = sending iken dolu (kisitla zorlanir). Suresi dolmus sending satiri yeniden claim edilebilir.';
COMMENT ON COLUMN social.admin_events.attempt_count IS
    'Deneme butcesi CLAIM aninda tukenir (F19) — finalize da DEGIL. Crash/kira dolumu butceyi harcar; boylece fiziksel gonderim sayisi her kosulda sinirlidir.';
COMMENT ON COLUMN social.admin_events.idempotency_key IS
    'Alici taraf (n8n) dedupe girdisi + yazim tarafi tekrar-korumasi — TEK anahtar.';

-- ---------------------------------------------------------------------------
-- 3. Garanti doğrulaması — fail-closed (032/033 ile AYNI sınıf)
-- ---------------------------------------------------------------------------
--
-- `CREATE TABLE / INDEX IF NOT EXISTS` yalnız o ADDA bir nesne var mı diye
-- bakar, TANIMINI doğrulamaz. Aynı adda ama yanlış tanımlı bir nesne önceden
-- duruyorsa DDL sessizce atlanır ve migration BAŞARIYLA biter — teslim durumu
-- CHECK'i düşmüş, kira tutarlılığı kısıtı yok olmuş ya da claim indeksi yarım
-- kalmış olabilir. Temiz bir test veritabanına uygulamak YALNIZ mutlu yolu
-- koşturur, bu davranışı ölçmez.
--
-- TANIM ≠ UYGULANMA: imzanın yanında uygulanma durumu da okunur — indekste
-- `indisvalid/indisready/indislive`, kısıtta `conenforced`/`convalidated`.
-- `conenforced` PostgreSQL 18 kolonudur; daha eski sunucuda blok "column does
-- not exist" ile DURUR (fail-closed, sessiz geçiş yok) — 032/033 ile aynı
-- belgeli sınır.
--
-- ELLE UYGULARKEN: psql'i `-v ON_ERROR_STOP=1` ile çağırın.

DO $verify034$
DECLARE
    failures TEXT;
BEGIN
    WITH expected(label, want) AS (
        VALUES
            -- TABLO İMZASI: nesnenin KENDİ katalog özellikleri. Kolon/kısıt/
            -- indeks imzası tablonun tamamı DEĞİLDİR — ÖLÇÜLDÜ (checkpoint 14,
            -- tur 2): `UNLOGGED` bir tablo bunların HEPSİNİ birebir aynı üretir
            -- ve doğrulamadan geçiyordu. Oysa temiz olmayan bir kapanışta
            -- UNLOGGED tablo TRUNCATE edilir; commit edilmiş outbox satırları
            -- yok olur ve transactional outbox'ın tek varlık sebebi ("bildirim,
            -- haber verdiği işle aynı kaderi paylaşır") sessizce ortadan kalkar.
            --   relkind='r'        -> sıradan tablo (görünüm/yabancı tablo değil)
            --   relpersistence='p' -> KALICI (unlogged/temp değil)
            --   relispartition='f' -> bölüm değil
            --   rls=f force_rls=f  -> satır güvenliği KAPALI. Açık bir RLS +
            --      kısıtlayıcı politika, kira sorgularına outbox'ı BOŞ
            --      gösterirdi: satırlar yazılır ama hiç teslim edilmez ve
            --      hiçbir hata da görünmez. Dayanıklılıkla aynı sınıf —
            --      nesnenin kendi özellikleri de sözleşmenin parçası.
            ('admin_events tablo imzası',
             'relkind=r relpersistence=p partition=f rls=f force_rls=f'),

            -- KOLON İMZASI: ad · tip ·
            -- null'lanabilirlik · kanonik varsayılan, attnum sırasında.
            -- Yalnız kısıt ve indeks doğrulamak YETMEZ (checkpoint 14, F4):
            -- ÖLÇÜLDÜ — `payload` TEXT olan, `id`'si PK'sız ve varsayılansız,
            -- ama CHECK'leri ve indeksi birebir doğru olan sahte bir tablo
            -- migration'dan rc=0 ile geçiyordu. Kısıtlar tablonun sözleşmesinin
            -- TAMAMI değildir; eksik doğrulanan her alan sessiz bir atlatma
            -- kapısıdır. Fazla kolon da yakalanır (imza tam eşleşmedir).
            ('admin_events kolon imzası',
             'id:uuid:nn:gen_random_uuid() && kind:text:nn:- &&'
             ' payload:jsonb:nn:- && idempotency_key:text:nn:- &&'
             ' delivery_state:text:nn:''pending''::text &&'
             ' lease_expires_at:timestamp with time zone:null:- &&'
             ' attempt_count:integer:nn:0 &&'
             ' created_at:timestamp with time zone:nn:now()'),

            ('admin_events PRIMARY KEY',
             'p|PRIMARY KEY (id)|enforced=true validated=true'),

            ('admin_events.delivery_state CHECK',
             'c|CHECK ((delivery_state = ANY (ARRAY[''pending''::text,'
             ' ''sending''::text, ''sent''::text, ''failed''::text])))'
             '|enforced=true validated=true'),

            ('admin_events lease/state CHECK',
             'c|CHECK (((delivery_state = ''sending''::text) ='
             ' (lease_expires_at IS NOT NULL)))|enforced=true validated=true'),

            ('admin_events.attempt_count CHECK',
             'c|CHECK ((attempt_count >= 0))|enforced=true validated=true'),

            ('admin_events.idempotency_key UNIQUE',
             'u|UNIQUE (idempotency_key)|enforced=true validated=true'),

            -- İndeks imzası ELLE KURULMAZ: `pg_get_indexdef` kanonik tanımın
            -- TAMAMINI taşır (benzersizlik · erişim yöntemi · kolon sırası ve
            -- yönü · predicate). Elle kurulan imzada unutulan her alan sessiz
            -- bir atlatma kapısıdır (033'te ölçüldü).
            ('idx_admin_events_claimable',
             'CREATE INDEX idx_admin_events_claimable ON social.admin_events'
             ' USING btree (created_at) WHERE (delivery_state = ANY'
             ' (ARRAY[''pending''::text, ''sending''::text]))'
             '|valid=true ready=true live=true')
    ),
    observed(label, got) AS (
        VALUES
            ('admin_events tablo imzası',
             (SELECT format('relkind=%s relpersistence=%s partition=%s'
                            ' rls=%s force_rls=%s',
                            c.relkind, c.relpersistence,
                            CASE WHEN c.relispartition THEN 't' ELSE 'f' END,
                            CASE WHEN c.relrowsecurity THEN 't' ELSE 'f' END,
                            CASE WHEN c.relforcerowsecurity THEN 't' ELSE 'f' END)
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
               WHERE n.nspname = 'social' AND c.relname = 'admin_events')),

            ('admin_events kolon imzası',
             (SELECT string_agg(format('%s:%s:%s:%s',
                                       a.attname,
                                       format_type(a.atttypid, a.atttypmod),
                                       CASE WHEN a.attnotnull
                                            THEN 'nn' ELSE 'null' END,
                                       coalesce(pg_get_expr(d.adbin, d.adrelid),
                                                '-')),
                                ' && ' ORDER BY a.attnum)
                FROM pg_attribute a
                LEFT JOIN pg_attrdef d
                       ON d.adrelid = a.attrelid AND d.adnum = a.attnum
               WHERE a.attrelid = 'social.admin_events'::regclass
                 AND a.attnum > 0
                 AND NOT a.attisdropped)),

            ('admin_events PRIMARY KEY',
             (SELECT string_agg(format('%s|%s|enforced=%s validated=%s',
                                       k.contype, pg_get_constraintdef(k.oid),
                                       CASE WHEN k.conenforced
                                            THEN 'true' ELSE 'false' END,
                                       CASE WHEN k.convalidated
                                            THEN 'true' ELSE 'false' END),
                                ' && ' ORDER BY k.conname)
                FROM pg_constraint k
               WHERE k.conrelid = 'social.admin_events'::regclass
                 AND k.contype = 'p')),

            ('admin_events.delivery_state CHECK',
             (SELECT string_agg(format('%s|%s|enforced=%s validated=%s',
                                       k.contype, pg_get_constraintdef(k.oid),
                                       CASE WHEN k.conenforced
                                            THEN 'true' ELSE 'false' END,
                                       CASE WHEN k.convalidated
                                            THEN 'true' ELSE 'false' END),
                                ' && ' ORDER BY k.conname)
                FROM pg_constraint k
               WHERE k.conrelid = 'social.admin_events'::regclass
                 AND k.contype = 'c'
                 AND k.conkey = ARRAY[
                         (SELECT a.attnum FROM pg_attribute a
                           WHERE a.attrelid = 'social.admin_events'::regclass
                             AND a.attname = 'delivery_state')]::int2[])),

            ('admin_events lease/state CHECK',
             (SELECT string_agg(format('%s|%s|enforced=%s validated=%s',
                                       k.contype, pg_get_constraintdef(k.oid),
                                       CASE WHEN k.conenforced
                                            THEN 'true' ELSE 'false' END,
                                       CASE WHEN k.convalidated
                                            THEN 'true' ELSE 'false' END),
                                ' && ' ORDER BY k.conname)
                FROM pg_constraint k
               WHERE k.conrelid = 'social.admin_events'::regclass
                 AND k.contype = 'c'
                 AND k.conkey @> ARRAY[
                         (SELECT a.attnum FROM pg_attribute a
                           WHERE a.attrelid = 'social.admin_events'::regclass
                             AND a.attname = 'lease_expires_at')]::int2[])),

            ('admin_events.attempt_count CHECK',
             (SELECT string_agg(format('%s|%s|enforced=%s validated=%s',
                                       k.contype, pg_get_constraintdef(k.oid),
                                       CASE WHEN k.conenforced
                                            THEN 'true' ELSE 'false' END,
                                       CASE WHEN k.convalidated
                                            THEN 'true' ELSE 'false' END),
                                ' && ' ORDER BY k.conname)
                FROM pg_constraint k
               WHERE k.conrelid = 'social.admin_events'::regclass
                 AND k.contype = 'c'
                 AND k.conkey = ARRAY[
                         (SELECT a.attnum FROM pg_attribute a
                           WHERE a.attrelid = 'social.admin_events'::regclass
                             AND a.attname = 'attempt_count')]::int2[])),

            ('admin_events.idempotency_key UNIQUE',
             (SELECT string_agg(format('%s|%s|enforced=%s validated=%s',
                                       k.contype, pg_get_constraintdef(k.oid),
                                       CASE WHEN k.conenforced
                                            THEN 'true' ELSE 'false' END,
                                       CASE WHEN k.convalidated
                                            THEN 'true' ELSE 'false' END),
                                ' && ' ORDER BY k.conname)
                FROM pg_constraint k
               WHERE k.conrelid = 'social.admin_events'::regclass
                 AND k.contype = 'u'
                 AND k.conkey = ARRAY[
                         (SELECT a.attnum FROM pg_attribute a
                           WHERE a.attrelid = 'social.admin_events'::regclass
                             AND a.attname = 'idempotency_key')]::int2[])),

            ('idx_admin_events_claimable',
             (SELECT format('%s|valid=%s ready=%s live=%s',
                            pg_get_indexdef(c.oid),
                            CASE WHEN i.indisvalid THEN 'true' ELSE 'false' END,
                            CASE WHEN i.indisready THEN 'true' ELSE 'false' END,
                            CASE WHEN i.indislive THEN 'true' ELSE 'false' END)
                FROM pg_index i
                JOIN pg_class c ON c.oid = i.indexrelid
                JOIN pg_namespace n ON n.oid = c.relnamespace
               WHERE n.nspname = 'social'
                 AND c.relname = 'idx_admin_events_claimable'
                 AND i.indrelid = 'social.admin_events'::regclass))
    )
    SELECT string_agg(
               format('%s -> beklenen [%s] · gorulen [%s]',
                      e.label, e.want, coalesce(o.got, '<nesne yok>')),
               E'\n  - ' ORDER BY e.label)
      INTO failures
      FROM expected e
      LEFT JOIN observed o ON o.label = e.label
     WHERE o.got IS DISTINCT FROM e.want;

    IF failures IS NOT NULL THEN
        RAISE EXCEPTION 'migration 034 garanti dogrulamasi BASARISIZ:%',
            E'\n  - ' || failures
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Ayni adda YANLIS TANIMLI bir nesne var; IF NOT EXISTS '
                         'onu DEGISTIRMEZ. Nesneyi elle dusurup migration i '
                         'yeniden uygulayin.';
    END IF;
END
$verify034$;
