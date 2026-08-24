-- Migration 032 GERİ ALMA — sektör bilgi paketi şeması
--
-- KULLANIM:  psql -v ON_ERROR_STOP=1 -f 032_down.sql
--            (bayrak olmadan psql hatayı basar ama SIFIR döner — geri alma
--             yarım kalır ve "başarılı" görünür.)
--
-- SÖZLEŞME (plan Task 3, F4 tahkimi — veri-varken-REDDET modeli):
--
--   Bu script YALNIZ boş-veri yolunda koşar. `sector_packages` veya
--   `sector_research_artifacts` tek satır bile içeriyorsa HİÇBİR değişiklik
--   yapmadan hata ile DURur: süresiz-saklama rejimindeki (K-140/141) paket ve
--   ham kanıt verisi bir script'le imha edilmez. Canlıda veri varken yol
--   GERİ ALMA DEĞİL, ileri düzeltme (forward-fix) migration'ıdır.
--
--   Preflight EN BAŞTADIR: reddetme durumunda hiçbir DDL çalışmamış olur —
--   transaction sarmalayıcısına bağımlı değildir.
--
--   `generation_stamps` ve `posts` damgaları ayrıca sayılmaz: ikisi de
--   `sector_packages`e FK'lıdır, paket tablosu boşsa damga da yoktur.
--
-- SIRA (spec §6.2'nin üçlü sırası (3)-(5) çekirdeğidir; paket-FK gerçeği
-- (1)-(2)'yi öne zorunlu kılar):
--   1. posts damga kolonları + bileşik FK
--   2. generation_stamps · sector_packages · sector_research_artifacts tabloları
--   3. brands.sub_sector_id bağları + indeks + kolon
--   4. YALNIZ bu işin açtığı alt sektör satırları (kök seed'e dokunulmaz)
--   5. tetikleyiciler + fonksiyonlar
--
-- Her adım `IF EXISTS` taşır: yarım kalmış bir geri alma tekrar koşturulabilir.

-- ---------------------------------------------------------------------------
-- 0. PREFLIGHT — veri varsa hiçbir şey yapmadan DUR
-- ---------------------------------------------------------------------------

DO $preflight$
DECLARE
    package_rows BIGINT := 0;
    artifact_rows BIGINT := 0;
BEGIN
    IF to_regclass('social.sector_packages') IS NOT NULL THEN
        EXECUTE 'SELECT count(*) FROM social.sector_packages' INTO package_rows;
    END IF;

    IF to_regclass('social.sector_research_artifacts') IS NOT NULL THEN
        EXECUTE 'SELECT count(*) FROM social.sector_research_artifacts'
            INTO artifact_rows;
    END IF;

    IF package_rows > 0 OR artifact_rows > 0 THEN
        RAISE EXCEPTION
            'migration 032 geri alma REDDEDILDI: veri var '
            '(sector_packages=%, sector_research_artifacts=%)',
            package_rows, artifact_rows
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Suresiz-saklama verisi script ile imha edilmez. '
                         'Canlida yol ileri duzeltme (forward-fix) '
                         'migration idir.';
    END IF;
END
$preflight$;

-- ---------------------------------------------------------------------------
-- 1. K-07 damga temsili — posts kolonları + bileşik FK
-- ---------------------------------------------------------------------------

ALTER TABLE social.posts DROP CONSTRAINT IF EXISTS posts_package_stamp_fkey;
ALTER TABLE social.posts DROP COLUMN IF EXISTS package_id;
ALTER TABLE social.posts DROP COLUMN IF EXISTS package_version;

-- ---------------------------------------------------------------------------
-- 2. Tablolar (makbuz → paket → ham kanıt: FK yönünün tersi)
-- ---------------------------------------------------------------------------
--
-- Tabloyla birlikte üstündeki tetikleyiciler ve indeksler de gider. Salt-ekleme
-- tetikleyicisi UPDATE/DELETE/TRUNCATE'i reddeder, DROP TABLE'ı engellemez.

DROP TABLE IF EXISTS social.generation_stamps;
DROP TABLE IF EXISTS social.sector_packages;
DROP TABLE IF EXISTS social.sector_research_artifacts;

-- ---------------------------------------------------------------------------
-- 3. brands.sub_sector_id — bağları boşalt, sonra kolonu kaldır
-- ---------------------------------------------------------------------------
--
-- Tetikleyici KOLONDAN ÖNCE düşürülür: `require_sub_sector_reference`
-- TG_ARGV[0] ile kolon adını okur; kolon olmadan her INSERT/UPDATE patlardı.

DROP TRIGGER IF EXISTS brands_sub_sector_must_be_sub ON social.brands;

DO $brands$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
         WHERE table_schema = 'social'
           AND table_name = 'brands'
           AND column_name = 'sub_sector_id'
    ) THEN
        EXECUTE 'UPDATE social.brands SET sub_sector_id = NULL '
                'WHERE sub_sector_id IS NOT NULL';
    END IF;
END
$brands$;

DROP INDEX IF EXISTS social.idx_brands_sub_sector_id;
ALTER TABLE social.brands DROP COLUMN IF EXISTS sub_sector_id;

-- ---------------------------------------------------------------------------
-- 4. Alt sektör satırları — YALNIZ bu işin açtıkları
-- ---------------------------------------------------------------------------
--
-- Kök seed (019/021) satırlarının `parent_sector_id`si NULL'dur; hiyerarşinin
-- alt katmanı yalnız bu işle doğdu. Başka bir satır (örn. `brands.sector_id`)
-- bir alt sektöre bağlıysa FK bu silmeyi REDDEDER — fail-closed, sessiz veri
-- kaybı yok.

DELETE FROM social.sectors WHERE parent_sector_id IS NOT NULL;

-- ---------------------------------------------------------------------------
-- 5. Tetikleyiciler + fonksiyonlar
-- ---------------------------------------------------------------------------

DROP TRIGGER IF EXISTS sectors_reject_reparenting ON social.sectors;

DROP FUNCTION IF EXISTS social.reject_sector_reparenting();
DROP FUNCTION IF EXISTS social.require_sub_sector_reference();
DROP FUNCTION IF EXISTS social.reject_research_artifact_mutation();

-- ---------------------------------------------------------------------------
-- 6. Kalıntı doğrulaması — fail-closed
-- ---------------------------------------------------------------------------
--
-- `DROP ... IF EXISTS` bir nesneyi ADIYLA arar; ad tutmuyorsa sessizce geçer.
-- Bu blok katalogtan GERÇEK durumu okur: 032'nin açtığı hiçbir nesne ayakta
-- kalmamalıdır. Kalan varsa hepsi tek mesajda raporlanır ve script DURur.

DO $verify_down$
DECLARE
    leftovers TEXT;
BEGIN
    SELECT string_agg(label, E'\n  - ' ORDER BY label)
      INTO leftovers
      FROM (
        SELECT 'tablo social.' || relname AS label
          FROM pg_class c
          JOIN pg_namespace n ON n.oid = c.relnamespace
         WHERE n.nspname = 'social'
           AND c.relkind = 'r'
           AND c.relname IN ('sector_packages', 'sector_research_artifacts',
                             'generation_stamps')
        UNION ALL
        SELECT 'kolon social.' || table_name || '.' || column_name
          FROM information_schema.columns
         WHERE table_schema = 'social'
           AND (table_name, column_name) IN
               (('brands', 'sub_sector_id'), ('posts', 'package_id'),
                ('posts', 'package_version'))
        UNION ALL
        SELECT 'tetikleyici ' || tgname
          FROM pg_trigger
         WHERE NOT tgisinternal
           AND tgname IN ('brands_sub_sector_must_be_sub',
                          'sectors_reject_reparenting',
                          'sector_packages_sector_must_be_sub',
                          'sector_research_artifacts_append_only',
                          'sector_research_artifacts_no_truncate')
        UNION ALL
        SELECT 'fonksiyon social.' || p.proname
          FROM pg_proc p
          JOIN pg_namespace n ON n.oid = p.pronamespace
         WHERE n.nspname = 'social'
           AND p.proname IN ('reject_sector_reparenting',
                             'require_sub_sector_reference',
                             'reject_research_artifact_mutation')
        UNION ALL
        SELECT 'indeks ' || indexname
          FROM pg_indexes
         WHERE schemaname = 'social'
           AND indexname = 'idx_brands_sub_sector_id'
        UNION ALL
        SELECT 'alt sektor satiri ' || slug
          FROM social.sectors
         WHERE parent_sector_id IS NOT NULL
      ) AS remaining;

    IF leftovers IS NOT NULL THEN
        RAISE EXCEPTION 'migration 032 geri alma EKSIK kaldi:%',
            E'\n  - ' || leftovers
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Kalan nesneyi elle dusurup script i yeniden kosturun.';
    END IF;
END
$verify_down$;
