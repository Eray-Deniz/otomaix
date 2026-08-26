-- Migration 033: Sektör bilgi paketi — kalıcı olay kaydı
--
-- Kapsam (spec §14.4, plan Task 12):
--   1. social.package_events — kapalı olay kümesi, iki kapsam sınıfı (F21)
--
-- `generation_stamps` bu migration'da DEĞİL 032'de kuruldu: Task 10 (üretici
-- ucu) o tabloya Task 12'den ÖNCE muhtaçtı, o yüzden sıralama böyle.
--
-- Bu tablo bir DENETİM İZİDİR. İki tasarım sonucu buradan çıkar:
--   * Sürüm alanları (`from_version` / `to_version`) sentinel değer taşımaz —
--     "yok" NULL'dır. Sınır geçişleri (ilk aktivasyon, deaktivasyon) uydurma
--     bir sürüm numarasıyla temsil edilseydi denetim izi yalan söylerdi.
--   * `detail` skaler değerli kısa bir sözlüktür (şekil kapısı serviste).
--     Paket İÇERİĞİ buraya basılmaz; olay kaydı bir kopya deposu değildir.

-- ---------------------------------------------------------------------------
-- 1. Olay tablosu
-- ---------------------------------------------------------------------------
--
-- `event_type` CHECK ile kapalıdır: kümeyi genişletmek migration ister. Yeni
-- bir olay türünü sessizce yazabilmek, "kapalı başlangıç kümesi" hükmünü
-- (spec §14.4) uygulamada boşa çıkarırdı.
--
-- `sector_id` / `package_id` FK DEĞİLDİR ve bu bilinçlidir: denetim izi,
-- işaret ettiği satır silinse bile AYAKTA kalmalıdır (paket satırının silinmesi
-- olayın olmadığı anlamına gelmez). `brand_id` ise FK + CASCADE'dir — marka
-- silme sözleşmesi (F18) korunur, markaya ait iz markayla birlikte gider.

CREATE TABLE IF NOT EXISTS social.package_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    sector_id UUID,
    brand_id UUID REFERENCES social.brands(id) ON DELETE CASCADE,
    package_id UUID,
    from_version INT,
    to_version INT,
    actor TEXT,
    detail JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT package_events_type_check CHECK (event_type IN (
        'mismatch_fallthrough',
        'package_read_error',
        'stale_assignment_fallback',
        'stamp_missing',
        'stamp_invalid',
        'stamp_stale_at_persist',
        'activation',
        'rollback',
        'deactivation'
    ))
);

-- Marka panosu ve olay süpürücüsü aynı iki eksenden okur: "bu markanın
-- olayları, en yeniden eskiye" ve "bu sektörün yaşam döngüsü".
CREATE INDEX IF NOT EXISTS idx_package_events_brand_created
    ON social.package_events (brand_id, created_at DESC)
    WHERE brand_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_package_events_sector_created
    ON social.package_events (sector_id, created_at DESC)
    WHERE sector_id IS NOT NULL;

-- ---------------------------------------------------------------------------
-- 2. Belgeleme
-- ---------------------------------------------------------------------------

COMMENT ON TABLE social.package_events IS
    'Sektor bilgi paketi — kalici olay kaydi (spec 14.4). Kapali olay kumesi CHECK ile zorlanir. Iki kapsam sinifi (F21): marka-kapsamli olaylar brand_id ISTER, yasam-dongusu olaylari sector_id+package_id+actor ISTER.';
COMMENT ON COLUMN social.package_events.from_version IS
    'Kaynak surum. NULL = yok (ilk aktivasyon) — sentinel deger KULLANILMAZ.';
COMMENT ON COLUMN social.package_events.to_version IS
    'Hedef surum. NULL = yok (deaktivasyon) — sentinel deger KULLANILMAZ.';
COMMENT ON COLUMN social.package_events.detail IS
    'Skaler degerli kisa sozluk (sekil kapisi: services/package_events.py). Paket icerigi buraya BASILMAZ.';
COMMENT ON COLUMN social.package_events.sector_id IS
    'FK DEGIL — denetim izi, isaret ettigi satir silinse bile ayakta kalir.';

-- ---------------------------------------------------------------------------
-- 3. Garanti doğrulaması — fail-closed (032'nin F7 kapısıyla AYNI sınıf)
-- ---------------------------------------------------------------------------
--
-- `CREATE TABLE / INDEX IF NOT EXISTS` yalnız o ADDA bir nesne var mı diye
-- bakar, TANIMINI doğrulamaz. Aynı adda ama yanlış tanımlı bir nesne önceden
-- duruyorsa DDL sessizce atlanır ve migration BAŞARIYLA biter — kapalı olay
-- kümesi CHECK'i düşmüş, marka FK'sının CASCADE'i değişmiş ya da bir indeks
-- yarım kalmış olabilir. 032 bu modu zaten tehlikeli sayıp katalogdan
-- doğruluyor; 033 aynı sınıftadır ve aynı kapıyı kurar. Temiz bir test
-- veritabanına uygulamak YALNIZ mutlu yolu koşturur, bu davranışı ölçmez.
--
-- TANIM ≠ UYGULANMA: imzanın yanında uygulanma durumu da okunur — indekslerde
-- `indisvalid/indisready/indislive`, FK'da `conenforced`/`convalidated` ve
-- kısıtı fiilen yürüten iç tetikleyiciler.
-- `conenforced` PostgreSQL 18 kolonudur ve DOĞRUDAN okunmaz: kolon adını
-- ayrıştırma anında taşıyan bir sorgu PG16'da "column does not exist" ile
-- düşerdi ve bu paket PG16 imajına pinlidir (review 2026-08-26, H1 — dağıtım
-- yolu kesin bozuktu). Bunun yerine satır jsonb'ye çevrilip anahtar ADIYLA
-- okunur: `COALESCE(to_jsonb(k)->>'conenforced', 'true')`.
-- Anahtar YOKSA (PG<18) 'true' döner ve bu bir gevşetme DEĞİLDİR: `NOT
-- ENFORCED` kısıtlar PostgreSQL 18'de geldi, öncesinde her kısıt zaten
-- uygulanır. ÖLÇÜLDÜ (18.3): gerçekten `NOT ENFORCED` bir FK'da jsonb yolu da
-- doğrudan okuma da 'false' verir — maskeleme yok.
--
-- Otomatik adlandırılan kısıtlar KOLONLA aranır; kolon bazlı arama birden çok
-- eşleşmeyi tek imzada birleştirir, böylece eksik VEYA fazla kısıt yakalanır.
--
-- ELLE UYGULARKEN: psql'i `-v ON_ERROR_STOP=1` ile çağırın.

DO $verify033$
DECLARE
    failures TEXT;
BEGIN
    WITH expected(label, want) AS (
        VALUES
            ('package_events.event_type CHECK',
             'c|CHECK ((event_type = ANY (ARRAY[''mismatch_fallthrough''::text,'
             ' ''package_read_error''::text, ''stale_assignment_fallback''::text,'
             ' ''stamp_missing''::text, ''stamp_invalid''::text,'
             ' ''stamp_stale_at_persist''::text, ''activation''::text,'
             ' ''rollback''::text, ''deactivation''::text])))'),

            ('package_events.brand_id FK',
             'f|ondelete=c|FOREIGN KEY (brand_id) REFERENCES social.brands(id)'
             ' ON DELETE CASCADE|enforced=true validated=true trig=4 enabled=4'),

            -- İndeks imzası ELLE KURULMAZ: `pg_get_indexdef` kanonik tanımın
            -- TAMAMINI taşır (benzersizlik · erişim yöntemi · kolon sırası ve
            -- yönü · predicate). Elle kurulan imzada unutulan her alan sessiz
            -- bir atlatma kapısıdır — ölçüldü (checkpoint 12 tur 2): aynı adda
            -- UNIQUE bir indeks eksik imzayı birebir üretiyor, `IF NOT EXISTS`
            -- onu atlıyor ve migration başarıyla bitiyordu. Uygulanma durumu
            -- tanımda YOKTUR, o yüzden ayrıca eklenir.
            ('idx_package_events_brand_created',
             'CREATE INDEX idx_package_events_brand_created ON'
             ' social.package_events USING btree (brand_id, created_at DESC)'
             ' WHERE (brand_id IS NOT NULL)|valid=true ready=true live=true'),
            ('idx_package_events_sector_created',
             'CREATE INDEX idx_package_events_sector_created ON'
             ' social.package_events USING btree (sector_id, created_at DESC)'
             ' WHERE (sector_id IS NOT NULL)|valid=true ready=true live=true'),

            -- ---------------------------------------------------------------
            -- TABLO + KOLON İMZASI + BİRİNCİL ANAHTAR (final review, 2026-08-25)
            --
            -- Yukarıdaki CHECK/indeks kontrolleri tablonun sözleşmesinin TAMAMI
            -- DEĞİLDİR. 034'te ÖLÇÜLDÜ: kolonu yanlış tipte ve birincil anahtarsız
            -- ama CHECK'leri ve indeksleri birebir doğru sahte bir tablo rc=0 ile
            -- geçiyordu; `UNLOGGED` bir tablo da diğer bütün imzaları AYNEN
            -- üretir ve temiz olmayan bir kapanışta TRUNCATE edilir — olay
            -- geçmişi (kim, ne zaman, hangi sürüm) sessizce yok olurdu.
            -- İmza attnum sırasındadır ve TAM eşleşmedir.
            -- ---------------------------------------------------------------
            ('package_events tablo imzası',
             'relkind=r relpersistence=p partition=f rls=f force_rls=f'),

            ('package_events kolon imzası',
             'id:uuid:nn:gen_random_uuid() && event_type:text:nn:- && sector_id:uuid:null:- && brand_id:uuid:null:- && package_id:uuid:null:- && from_version:integer:null:- && to_version:integer:null:- && actor:text:null:- && detail:jsonb:null:- && created_at:timestamp with time zone:nn:now()'),

            ('package_events PRIMARY KEY',
             'p|PRIMARY KEY (id)|enforced=true validated=true'),

            -- ---------------------------------------------------------------
            -- KAPALI MANİFEST (final review tur 2 — FAZLADAN nesne de bulgudur)
            --
            -- Yukarıdaki madde madde kontroller POZİTİF bir izin listesidir:
            -- adı geçen nesnenin doğru tanımlı olduğunu söyler, ama adı GEÇMEYEN
            -- bir nesnenin varlığı hakkında hiçbir şey söylemez. Ölçülen boşluk:
            -- aynı adda, beklenen kolonları ve kısıtları taşıyan ama ÜSTÜNE bir
            -- `CHECK (false)`, fazladan bir UNIQUE ya da yazımı reddeden bir
            -- tetikleyici eklenmiş tablo, izin listesinden GEÇER ve her geçerli
            -- yazımı reddeder. Migration "başarılı" der, uygulama yazamaz.
            --
            -- Bu yüzden kısıt · tetikleyici · indeks kümeleri TAM eşleşmedir.
            -- Eksik olan da fazla olan da aynı mesajda raporlanır.
            --
            -- `NOT NULL` kısıtları (contype='n') DIŞARIDA: PostgreSQL 17'den
            -- itibaren pg_constraint'te satır olarak görünürler, 16'da
            -- görünmezler. Null'lanabilirlik zaten kolon imzasında denetleniyor.
            --
            -- İndeks satırı benzersizliği VE fiilen uygulanma durumunu taşır:
            -- yarım kalmış (invalid) bir indeks `indisunique=true` kalır ama
            -- hiçbir şeyi zorlamaz.
            -- ---------------------------------------------------------------
            ('package_events kısıt kümesi (kapalı)',
             'package_events_brand_id_fkey|FOREIGN KEY (brand_id) REFERENCES social.brands(id) ON DELETE CASCADE && package_events_pkey|PRIMARY KEY (id) && package_events_type_check|CHECK ((event_type = ANY (ARRAY[''mismatch_fallthrough''::text, ''package_read_error''::text, ''stale_assignment_fallback''::text, ''stamp_missing''::text, ''stamp_invalid''::text, ''stamp_stale_at_persist''::text, ''activation''::text, ''rollback''::text, ''deactivation''::text])))'),

            ('package_events tetikleyici kümesi (kapalı)',
             '<yok>'),

            ('package_events indeks kümesi (kapalı)',
             'CREATE INDEX idx_package_events_brand_created ON social.package_events USING btree (brand_id, created_at DESC) WHERE (brand_id IS NOT NULL)|f|live && CREATE INDEX idx_package_events_sector_created ON social.package_events USING btree (sector_id, created_at DESC) WHERE (sector_id IS NOT NULL)|f|live && CREATE UNIQUE INDEX package_events_pkey ON social.package_events USING btree (id)|t|live')
    ),
    observed(label, got) AS (
        VALUES
            ('package_events kısıt kümesi (kapalı)',
             (SELECT coalesce(string_agg(format('%s|%s', k.conname,
                                                pg_get_constraintdef(k.oid)),
                                         ' && ' ORDER BY k.conname), '<yok>')
                FROM pg_constraint k
               WHERE k.conrelid = 'social.package_events'::regclass
                 AND k.contype <> 'n')),

            ('package_events tetikleyici kümesi (kapalı)',
             (SELECT coalesce(string_agg(format('%s|%s', t.tgname,
                                                CASE WHEN t.tgenabled = 'O'
                                                     THEN 'enabled'
                                                     ELSE 'DISABLED' END),
                                         ' && ' ORDER BY t.tgname), '<yok>')
                FROM pg_trigger t
               WHERE t.tgrelid = 'social.package_events'::regclass
                 AND NOT t.tgisinternal)),

            ('package_events indeks kümesi (kapalı)',
             -- ADI değil TAM TANIMI karşılaştırılır. Ölçüldü (final review tur 3):
             -- ada göre eşleyen bir kontrol, aynı ADDA ama başka tabloya/kolona
             -- kurulmuş GEÇERLİ bir indeksi kabul eder — `IF NOT EXISTS` o adı
             -- görüp DDL'i atlar ve migration "başarılı" der.
             (SELECT coalesce(string_agg(format('%s|%s|%s',
                                                pg_get_indexdef(i.indexrelid),
                                                i.indisunique,
                                                CASE WHEN i.indisvalid
                                                      AND i.indisready
                                                      AND i.indislive
                                                     THEN 'live'
                                                     ELSE 'BROKEN' END),
                                         ' && ' ORDER BY c.relname), '<yok>')
                FROM pg_index i
                JOIN pg_class c ON c.oid = i.indexrelid
               WHERE i.indrelid = 'social.package_events'::regclass)),
            ('package_events tablo imzası',
             (SELECT format('relkind=%s relpersistence=%s partition=%s'
                            ' rls=%s force_rls=%s',
                            c.relkind, c.relpersistence,
                            CASE WHEN c.relispartition THEN 't' ELSE 'f' END,
                            CASE WHEN c.relrowsecurity THEN 't' ELSE 'f' END,
                            CASE WHEN c.relforcerowsecurity THEN 't' ELSE 'f' END)
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
               WHERE n.nspname = 'social' AND c.relname = 'package_events')),

            ('package_events kolon imzası',
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
               WHERE a.attrelid = 'social.package_events'::regclass
                 AND a.attnum > 0
                 AND NOT a.attisdropped)),

            ('package_events PRIMARY KEY',
             (SELECT string_agg(format('%s|%s|enforced=%s validated=%s',
                                       k.contype, pg_get_constraintdef(k.oid),
                                       COALESCE(to_jsonb(k)->>'conenforced', 'true'),
                                       CASE WHEN k.convalidated
                                            THEN 'true' ELSE 'false' END),
                                ' && ')
                FROM pg_constraint k
               WHERE k.conrelid = 'social.package_events'::regclass
                 AND k.contype = 'p')),
            ('package_events.event_type CHECK',
             (SELECT string_agg(format('%s|%s', k.contype,
                                       pg_get_constraintdef(k.oid)),
                                ' && ' ORDER BY k.conname)
                FROM pg_constraint k
               WHERE k.conrelid = 'social.package_events'::regclass
                 AND k.contype = 'c'
                 AND k.conkey = ARRAY[
                         (SELECT a.attnum FROM pg_attribute a
                           WHERE a.attrelid = 'social.package_events'::regclass
                             AND a.attname = 'event_type')]::int2[])),

            ('package_events.brand_id FK',
             (SELECT string_agg(format('%s|ondelete=%s|%s|enforced=%s'
                                       ' validated=%s trig=%s enabled=%s',
                                       k.contype,
                                       k.confdeltype,
                                       pg_get_constraintdef(k.oid),
                                       COALESCE(to_jsonb(k)->>'conenforced', 'true'),
                                       CASE WHEN k.convalidated
                                            THEN 'true' ELSE 'false' END,
                                       (SELECT count(*) FROM pg_trigger t
                                         WHERE t.tgconstraint = k.oid),
                                       (SELECT count(*) FROM pg_trigger t
                                         WHERE t.tgconstraint = k.oid
                                           AND t.tgenabled = 'O')),
                                ' && ' ORDER BY k.conname)
                FROM pg_constraint k
               WHERE k.conrelid = 'social.package_events'::regclass
                 AND k.contype = 'f'
                 AND k.conkey = ARRAY[
                         (SELECT a.attnum FROM pg_attribute a
                           WHERE a.attrelid = 'social.package_events'::regclass
                             AND a.attname = 'brand_id')]::int2[])),

            ('idx_package_events_brand_created',
             (SELECT format('%s|valid=%s ready=%s live=%s',
                            pg_get_indexdef(c.oid),
                            CASE WHEN i.indisvalid THEN 'true' ELSE 'false' END,
                            CASE WHEN i.indisready THEN 'true' ELSE 'false' END,
                            CASE WHEN i.indislive THEN 'true' ELSE 'false' END)
                FROM pg_index i
                JOIN pg_class c ON c.oid = i.indexrelid
                JOIN pg_namespace n ON n.oid = c.relnamespace
               WHERE n.nspname = 'social'
                 AND c.relname = 'idx_package_events_brand_created'
                 AND i.indrelid = 'social.package_events'::regclass)),

            ('idx_package_events_sector_created',
             (SELECT format('%s|valid=%s ready=%s live=%s',
                            pg_get_indexdef(c.oid),
                            CASE WHEN i.indisvalid THEN 'true' ELSE 'false' END,
                            CASE WHEN i.indisready THEN 'true' ELSE 'false' END,
                            CASE WHEN i.indislive THEN 'true' ELSE 'false' END)
                FROM pg_index i
                JOIN pg_class c ON c.oid = i.indexrelid
                JOIN pg_namespace n ON n.oid = c.relnamespace
               WHERE n.nspname = 'social'
                 AND c.relname = 'idx_package_events_sector_created'
                 AND i.indrelid = 'social.package_events'::regclass))
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
        RAISE EXCEPTION 'migration 033 garanti dogrulamasi BASARISIZ:%',
            E'\n  - ' || failures
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Ayni adda YANLIS TANIMLI bir nesne var; IF NOT EXISTS '
                         'onu DEGISTIRMEZ. Nesneyi elle dusurup migration i '
                         'yeniden uygulayin.';
    END IF;
END
$verify033$;
