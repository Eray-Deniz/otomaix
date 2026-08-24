-- Migration 032 GERİ ALMA — sektör bilgi paketi şeması
--
-- KULLANIM:  psql -f 032_down.sql
--            Script `ON_ERROR_STOP`u KENDİ açar ve tüm gövdeyi TEK transaction'a
--            sarar — çağıranın bayrağına muhtaç değildir. Hata hâlinde hiçbir
--            adım kalıcı olmaz.
--
--            `-1` / `--single-transaction` GEÇMEYİN ve dosyayı açık bir
--            transaction'ın içinden `\i` ile çağırmayın: transaction sahipliği
--            bu dosyadadır. Sarmalanmış çağrıda içerideki `BEGIN` savepoint
--            YARATMAZ, dosyanın `COMMIT`i ÇAĞIRANIN transaction'ını erken kapatır
--            ve çağıranın atomik sandığı toplu iş yıkım kalıcı olduktan sonra
--            yarıda kalabilir. Aşağıdaki kapı bu durumu SAPTAR ve durdurur.
--
-- SÖZLEŞME (plan Task 3, F4 tahkimi — veri-varken-REDDET modeli):
--
--   Bu script YALNIZ boş-veri yolunda koşar. `sector_packages` veya
--   `sector_research_artifacts` tek satır bile içeriyorsa HİÇBİR değişiklik
--   yapmadan hata ile DURur: süresiz-saklama rejimindeki (K-140/141) paket ve
--   ham kanıt verisi bir script'le imha edilmez. Canlıda veri varken yol
--   GERİ ALMA DEĞİL, ileri düzeltme (forward-fix) migration'ıdır.
--
--   Preflight EN BAŞTADIR ve sayım YALNIZ korunan iki tablo ACCESS EXCLUSIVE
--   kilidi ALTINDAYKEN yapılır. Kilitler transaction sonuna kadar tutulur:
--   sayımdan sonra, silmeden önce araya giren bir yazar OLAMAZ. Kilitsiz sürümde
--   bu pencere gerçekti — eşzamanlı bir INSERT sayımdan sonra commit edip
--   DROP TABLE ile yok edilebilirdi (Codex checkpoint 3, yüksek bulgu).
--
--   Kilit sırası SABİTTİR (önce sector_packages, sonra sector_research_artifacts):
--   aynı script'in iki koşumu birbirini kilitlemez, deadlock üretmez.
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

\set ON_ERROR_STOP on

-- ---------------------------------------------------------------------------
-- -1. Sarmalayıcı-transaction kapısı — sahiplik çakışmasını SAPTA
-- ---------------------------------------------------------------------------
--
-- `DO ... COMMIT` üst düzeyde (autocommit) geçerlidir, açık bir transaction
-- bloğunun içinde `invalid transaction termination` ile durur. Ölçüldü (PG 18.3):
-- düz `psql -f` → rc=0 · `psql -1 -f` → rc=3. Kapı hiçbir şeye dokunmadan,
-- BEGIN'den ÖNCE çalışır.

\echo 'Not: bir sonraki adim "invalid transaction termination" derse, bu dosya'
\echo '     sarmalayici bir transaction icinden cagrilmistir (ornegin psql -1).'
\echo '     Dosya kendi transaction ini sahiplenir; sarmalamadan cagirin.'

DO $nesting_guard$
BEGIN
    COMMIT;
END
$nesting_guard$;

BEGIN;

-- Yalıtım seviyesi SABİTLENİR — çağıranın oturum varsayılanına bırakılmaz.
-- REPEATABLE READ'de snapshot transaction'ın İLK deyiminde donar: kilit
-- beklenirken commit edilen satır sayıma GÖRÜNMEZ ve teardown onu yok eder.
-- Ölçüldü: kilit tek başına o seviyede yetmiyordu (Codex checkpoint 3, tur 2).
-- Bu deyim, dışarıda sorgu çalıştırmış bir transaction'ın içinde HATA verir —
-- yani o durumda da yıkımdan önce durulur (fail-closed).
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- ---------------------------------------------------------------------------
-- 0. PREFLIGHT — korunan tabloları kilitle, sonra say; veri varsa DUR
-- ---------------------------------------------------------------------------

DO $preflight$
DECLARE
    package_rows BIGINT := 0;
    artifact_rows BIGINT := 0;
BEGIN
    -- Kilit ÖNCE, sayım SONRA: aradaki pencere kapanır. Kilitler bu
    -- transaction commit/rollback edilene kadar tutulur, yani teardown boyunca.
    IF to_regclass('social.sector_packages') IS NOT NULL THEN
        EXECUTE 'LOCK TABLE social.sector_packages IN ACCESS EXCLUSIVE MODE';
    END IF;

    IF to_regclass('social.sector_research_artifacts') IS NOT NULL THEN
        EXECUTE 'LOCK TABLE social.sector_research_artifacts '
                'IN ACCESS EXCLUSIVE MODE';
    END IF;

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

COMMIT;
