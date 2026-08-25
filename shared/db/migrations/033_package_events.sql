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
-- kısıtı fiilen yürüten iç tetikleyiciler. `conenforced` PostgreSQL 18
-- kolonudur; daha eski sunucuda blok "column does not exist" ile DURUR
-- (fail-closed, sessiz geçiş yok) — 032 ile aynı belgeli sınır.
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

            ('idx_package_events_brand_created',
             'cols=brand_id,created_at pred=(brand_id IS NOT NULL)'
             ' valid=true ready=true live=true'),
            ('idx_package_events_sector_created',
             'cols=sector_id,created_at pred=(sector_id IS NOT NULL)'
             ' valid=true ready=true live=true')
    ),
    observed(label, got) AS (
        VALUES
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
                                       CASE WHEN k.conenforced
                                            THEN 'true' ELSE 'false' END,
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
             (SELECT format('cols=%s pred=%s valid=%s ready=%s live=%s',
                            (SELECT string_agg(a.attname, ',' ORDER BY k.ord)
                               FROM unnest(i.indkey) WITH ORDINALITY AS k(attnum, ord)
                               JOIN pg_attribute a
                                 ON a.attrelid = i.indrelid AND a.attnum = k.attnum),
                            coalesce(pg_get_expr(i.indpred, i.indrelid),
                                     '<kismi degil>'),
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
             (SELECT format('cols=%s pred=%s valid=%s ready=%s live=%s',
                            (SELECT string_agg(a.attname, ',' ORDER BY k.ord)
                               FROM unnest(i.indkey) WITH ORDINALITY AS k(attnum, ord)
                               JOIN pg_attribute a
                                 ON a.attrelid = i.indrelid AND a.attnum = k.attnum),
                            coalesce(pg_get_expr(i.indpred, i.indrelid),
                                     '<kismi degil>'),
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
