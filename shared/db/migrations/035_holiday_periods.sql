-- Migration 035 — takvim DÖNEM desteği + üç takvim kalemi (plan Task 5)
--
-- NE EKLİYOR:
--   `social.public_holidays.end_date DATE NULL` — dolu ise kayıt bir DÖNEMdir
--   (`date`..`end_date`), boş ise tek gündür. Üç yeni takvim kalemi de burada
--   seed edilir.
--
-- BAĞLAYICI INVARIANTLAR (plan Task 5):
--   * `end_date IS NULL OR end_date >= date` — CHECK kısıtı. Ters dönem
--     yorumla değil veritabanıyla engellenir.
--   * `UNIQUE(year, date)` KORUNUR: dönemin BAŞLANGICI hâlâ benzersiz
--     anahtardır, yani bir güne iki dönem başlayamaz.
--   * `normalize_special_day_key` davranışı DEĞİŞMEZ — paket eşleşmesi ADA
--     dayanır, tarihe değil. Dönem desteği yalnız takvim beslemesini ve gün
--     seçimini ilgilendirir.
--
-- SEED DEĞERLERİ UYDURULMAMIŞTIR. Beşi de operatör kararıdır (2026-09-02,
-- `331fe7a`, `docs/active/sektor-bilgi-paketi-plan2/TASK.md` Decisions Log):
-- yıl 2026 (tabloda bugün TEK yıl bu; yıllık n8n işi `new Date().getFullYear()`
-- kullanır, yani 2027 satırları kendi turunda doğar — migration onları YAZMAZ),
-- 10 Kasım `national` (emsal: "Çanakkale Şehitlerini Anma Günü"), Öğretmenler
-- Günü ve Okula Dönüş `commercial`. Kategori sözlüğü tam olarak
-- {national, religious, commercial}; DÖRDÜNCÜ değer yoktur.
--
-- TRANSACTION SAHİPLİĞİ: bu dosya KENDİ `BEGIN/COMMIT`ini TAŞIMAZ. Dağıtım
-- runner'ı (`shared/local-deployment/migrations/run-migrations.sh`) ve testler
-- her migration'ı `--single-transaction` ile uygular; kendi transaction'ını
-- açan dosyalar `SELF_MANAGED_TX` / `NON_TRANSACTIONAL_MIGRATIONS` listelerine
-- girmek zorundadır ve 035'in buna ihtiyacı yoktur.
--
--   Sarmalanmış koşum ATOMİKLİK için ÖNERİLİR (yarım uygulanan bir şema
--   istemezsiniz), ama DOĞRULUK için ŞART DEĞİLDİR: dosya sarmalanmamış
--   `psql -f` altında da tam uygulanır ve bu iki biçimde de ÖLÇÜLÜR
--   (`tests/test_migration_035.py::test_bare_psql_apply_is_complete`, çıplak ve
--   `ON_ERROR_STOP=1` varyantları). Aşağıdaki seed manifestinin ömrü bu yüzden
--   OTURUMdur, transaction değil — ayrıntı ve ölçüm manifestin başında.
--
-- GERİ ALMA: `rollback/035_down.sql`. Geri alma sahiplik sınırı taşır — YALNIZ
-- bu migration'ın yazdığı üç satırı kaldırır. Üretici (n8n takvim işi) şemayla
-- BİRLİKTE sürümlenir: geri alma o workflow'un önceki sürümüne dönmeyi de
-- kapsar, yoksa eski şemaya dönem-farkında bir üretici yazmaya çalışır.
-- Dağıtım/geri alma sırası Task 18'de listelenir.

-- ---------------------------------------------------------------------------
-- 1. Dönem kolonu
-- ---------------------------------------------------------------------------

ALTER TABLE social.public_holidays ADD COLUMN IF NOT EXISTS end_date DATE;

-- ---------------------------------------------------------------------------
-- 2. Ters dönem kısıtı
-- ---------------------------------------------------------------------------
--
-- `ADD CONSTRAINT`in `IF NOT EXISTS` biçimi YOKTUR; varlık katalogdan okunur.
-- Aksi hâlde ikinci koşum `duplicate_object` ile DURur ve ondan sonraki hiçbir
-- migration uygulanmazdı.

DO $end_date_check$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
         WHERE conrelid = 'social.public_holidays'::regclass
           AND conname = 'public_holidays_end_date_check'
    ) THEN
        ALTER TABLE social.public_holidays
            ADD CONSTRAINT public_holidays_end_date_check
            CHECK (end_date IS NULL OR end_date >= date);
    END IF;
END
$end_date_check$;

-- ---------------------------------------------------------------------------
-- 3. Üç takvim kalemi (emsal: `002_autoposting.sql:29-40`)
-- ---------------------------------------------------------------------------
--
-- `DO NOTHING` bilinçlidir ve DEĞİŞMEDİ: aynı `(year, date)` anahtarında ZATEN
-- bir satır varsa o satır bu migration'ın DEĞİLDİR ve ezilmez. Ad/kategori
-- düzeltme hakkı takvim beslemesinindir (yıllık n8n işi), bir seed bloğunun
-- değil.
--
-- ATLAMA ARTIK GÖRÜNÜR (fix turu 1, Q2). Ölçülen boşluk: aşağıdaki fail-closed
-- doğrulama üç anahtarın yalnızca VAR OLDUĞUNU ölçüyor — bilinçli olarak, çünkü
-- içeriği pinlemek beslemenin meşru düzeltmesini migration hatasına çevirirdi.
-- Sonucu şuydu: hedef veritabanı o anahtarlardan birini zaten tutuyorsa
-- migration BAŞARILI rapor ediyor, operatör kararındaki değerler hiç yazılmıyor
-- ve kimse haberdar olmuyordu — yani "migration bu değerleri SABİT yazar"
-- hükmü tam da önemli olduğu vakada ölçüsüz kalıyordu. Aşağıdaki blok gerçekten
-- kaç satır yazıldığını sayar ve içeriği operatör kararından FARKLI olan dolu
-- anahtarları NOTICE ile duyurur. NOTICE'tir, EXCEPTION değil: dolu anahtar bir
-- şema hatası değil, insan gözü isteyen bir veri durumudur.
--
-- Değerler `m035_seed_up`de TEK KEZ tanımlanır; hem yazım hem karşılaştırma oradan
-- okur, yani ikisi ayrışamaz.

-- MANİFESTİN ÖMRÜ OTURUMDUR, TRANSACTION DEĞİL (fix turu 2, N1 — bu yürütmenin
-- KENDİ ürettiği gerilemenin düzeltmesi). İlk yazım `ON COMMIT DROP` taşıyordu;
-- bu dosya kendi transaction'ını taşımadığı için autocommit altında her deyim
-- kendi transaction'ıdır ve manifest KENDİ `CREATE`inin commit'inde düşerdi.
-- ÖLÇÜLDÜ (çıplak `psql -f`, taze veritabanı): `rc=0`, stderr'de üç kez
-- `relation "m035_seed_up" does not exist`, kolon + CHECK commit edilmiş, SIFIR
-- seed satırı — üstelik hata fail-closed garanti bloğunun İÇİNDE de patladığı
-- için tam da bunu yakalaması gereken kapı hiç değerlendirilemedi. Fail-OPEN.
--
-- Geçici tablo zaten oturumla birlikte ölür; psql süreci bittiğinde gider.
-- Önden düşürme, aynı oturumda dosyanın ikinci kez `\i` edilmesini destekler.
--
-- AD BU DOSYAYA ÖZELDİR (fix turu 3): `m035_seed_up` — geri alma dosyası
-- `m035_seed_down` kullanır. İlk yazımda İKİSİ DE `m035_seed` idi ve N1'in
-- oturum-ömrü düzeltmesinden sonra aynı oturumda `up` ardından `down`
-- koşmak geri almayı `relation already exists` ile düşürüyordu. İki bağımsız
-- özellik birden kapatır: kaynak PAYLAŞILMAZ (ayrı adlar) ve kurulum
-- ÖMÜRDEN BAĞIMSIZ İDEMPOTENTTİR (aşağıdaki tür-farkında kapı). Kanıt:
-- `tests/test_migration_035.py::test_manifest_lifetime_matrix` (96 hücre).
-- `to_regclass` KULLANILIR, `DROP TABLE IF EXISTS pg_temp.…` DEĞİL: ölçüldü,
-- ikincisi henüz temp şeması olmayan taze bir oturumda her koşumda
-- `NOTICE: schema "pg_temp" does not exist, skipping` basar ve aşağıdaki
-- ANLAMLI uyarının sinyalini gürültüye boğardı. `to_regclass` sessizdir.

DO $prepare_manifest$
DECLARE
    held_kind "char";
    drop_verb TEXT;
BEGIN
    SELECT c.relkind INTO held_kind
      FROM pg_class c
     WHERE c.oid = to_regclass('pg_temp.m035_seed_up');

    IF held_kind IS NULL THEN
        RETURN;                       -- ad boş: yapacak bir şey yok
    END IF;

    drop_verb := CASE held_kind
                     WHEN 'r' THEN 'TABLE'
                     WHEN 'p' THEN 'TABLE'
                     WHEN 'f' THEN 'FOREIGN TABLE'
                     WHEN 'v' THEN 'VIEW'
                     WHEN 'm' THEN 'MATERIALIZED VIEW'
                     WHEN 'S' THEN 'SEQUENCE'
                 END;

    IF drop_verb IS NULL THEN
        -- Bilinmeyen tür: TAHMİN ETME, DUR. Yanlış `DROP` fiili ya patlar ya
        -- da başka bir nesneyi hedefler; ikisi de sessiz olmamalı.
        RAISE EXCEPTION
            'migration 035: pg_temp.m035_seed_up adini beklenmeyen turde bir nesne tutuyor (relkind=%)',
            held_kind
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Bu ad bu migration a ayrilmistir; nesneyi elle kaldirip '
                         'yeniden kosturun.';
    END IF;

    EXECUTE format('DROP %s pg_temp.m035_seed_up', drop_verb);
END
$prepare_manifest$;

CREATE TEMP TABLE m035_seed_up (
    year     INTEGER NOT NULL,
    date     DATE    NOT NULL,
    name_tr  TEXT    NOT NULL,
    name_en  TEXT,
    category TEXT,
    end_date DATE
);

INSERT INTO m035_seed_up (year, date, name_tr, name_en, category, end_date) VALUES
  (2026, DATE '2026-11-10', '10 Kasım Atatürk''ü Anma Günü', 'Atatürk Memorial Day', 'national',   NULL),
  (2026, DATE '2026-11-24', '24 Kasım Öğretmenler Günü',     'Teachers'' Day',       'commercial', NULL),
  (2026, DATE '2026-08-15', 'Okula Dönüş',                   'Back to School',       'commercial', DATE '2026-09-15');

-- UYARI SEVİYESİ PİNLENİR (fix turu 2, N2). Q2'nin tüm görünürlüğü aşağıdaki
-- NOTICE'e dayanıyor ve onun yayınlanıp yayınlanmayacağını bu depoda YAŞAMAYAN
-- bir ayar belirliyor. ÖLÇÜLDÜ: sunucu varsayılanı `notice` ve mesaj çıkıyor;
-- `PGOPTIONS='-c client_min_messages=warning'` altında AYNI `RAISE NOTICE` boş
-- stderr + `rc=0` üretiyor. Rol/veritabanı düzeyinde
-- `ALTER … SET client_min_messages='warning'` sıradan bir üretim
-- sıkılaştırmasıdır — yani kapattığımız Q2 koşulu, kontrol etmediğimiz bir
-- ortamca sessizce geri açılabilirdi.
--
-- `SET LOCAL` DEĞİL, düz `SET`: `SET LOCAL` transaction bloğu dışında
-- `WARNING: SET LOCAL can only be used in transaction blocks` verir ve HİÇBİR
-- ŞEY yapmaz — yani tam da N1'in kurtardığı çıplak `psql -f` yolunda pini
-- düşürürdü. Düz `SET`in sızma yüzeyi bu psql sürecinin geri kalanıdır ve
-- dosya hemen ardından biter.
--
-- DÜRÜST SINIR: bu pin sunucunun mesajı YAYINLAMASINI garanti eder, operatörün
-- onu GÖRMESİNİ değil (çıktı yönlendirilmiş olabilir). Sunucu tarafındaki yarıyı
-- kapatır; kalan yarı işletim disiplinidir.

SET client_min_messages = 'notice';

DO $seed_035$
DECLARE
    written INT := 0;
    occupied_count INT := 0;
    occupied TEXT;
BEGIN
    WITH ins AS (
        INSERT INTO social.public_holidays
            (year, date, name_tr, name_en, category, end_date)
        SELECT s.year, s.date, s.name_tr, s.name_en, s.category, s.end_date
          FROM m035_seed_up s
        ON CONFLICT (year, date) DO NOTHING
        RETURNING 1
    )
    SELECT count(*) INTO written FROM ins;

    IF written < (SELECT count(*) FROM m035_seed_up) THEN
        -- Sessiz kalınacak tek durum: anahtar dolu AMA içerik operatör
        -- kararıyla AYNI (yani bu migration'ın ikinci koşumu). Farklıysa
        -- duyurulur; "içerik farklı" ifadesi beslemenin meşru düzeltmesini de
        -- kapsar ve mesaj bunu söyler.
        SELECT count(*),
               string_agg(
                   format('(%s, %s) anahtarini tutan satir: %L / %L / %L',
                          s.year, s.date, h.name_tr, h.name_en, h.category),
                   E'\n  - ' ORDER BY s.date)
          INTO occupied_count, occupied
          FROM m035_seed_up s
          JOIN social.public_holidays h
            ON h.year = s.year AND h.date = s.date
         WHERE (h.name_tr, h.name_en, h.category, h.end_date)
               IS DISTINCT FROM (s.name_tr, s.name_en, s.category, s.end_date);

        IF occupied_count > 0 THEN
            RAISE NOTICE
                'migration 035: takvim anahtari ZATEN DOLU (% adet), operator karari YAZILMADI:%',
                occupied_count, E'\n  - ' || occupied
                USING HINT = 'Hata degildir: ON CONFLICT DO NOTHING sozlesmesi geregi '
                             'mevcut satir EZILMEDI. Satiri takvim beslemesi duzeltmis '
                             'olabilir; degilse operator karari (2026-09-02) bu '
                             'veritabaninda yururlukte DEGIL, gozden gecirin.';
        END IF;
    END IF;
END
$seed_035$;

-- ---------------------------------------------------------------------------
-- 4. Garanti doğrulaması — fail-closed
-- ---------------------------------------------------------------------------
--
-- `IF NOT EXISTS` / `DO NOTHING` sessizce atlar; bu blok katalogtan ve tablodan
-- GERÇEK durumu okur. Kapsam DAR tutulmuştur: yalnız 035'in kendi açtıkları
-- ölçülür (kolon imzası · kısıt · üç anahtarın varlığı). Satırların İÇERİĞİ
-- pinlenmez — takvim beslemesinin ad/kategori düzeltme hakkı vardır ve pinli
-- bir tuple o meşru düzeltmeden sonra migration'ı düşürürdü.

DO $verify_035$
DECLARE
    problems TEXT;
    manifest_rows INT;
BEGIN
    -- PAYDA ÖNCE (fix turu 2, N3). Anahtar kontrolü artık literal bir liste
    -- yerine `m035_seed_up` üzerinde dönüyor; manifest boşsa blok hiçbir sorun
    -- BULAMAZ ve migration hiçbir şey seed etmemiş olarak "başarılı" raporlar.
    -- Veriye dayalı bir payda kendini doğrulamak zorundadır, yoksa garanti boş
    -- kümede vakum olarak sağlanır. (Sarmalayıcı altında boş manifeste giden bir
    -- yol ÖLÇÜLMEDİ — kapı yine de konur, çünkü maliyeti bir satır.)
    SELECT count(*) INTO manifest_rows FROM m035_seed_up;
    IF manifest_rows <> 3 THEN
        RAISE EXCEPTION
            'migration 035 garanti dogrulamasi BASARISIZ: seed manifesti % satir '
            'tasiyor (beklenen 3)', manifest_rows
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Manifest bu dosyanin TEK seed tanimidir; bos/eksik '
                         'manifest butun kapilari vakuma cevirir.';
    END IF;

    SELECT string_agg(label, E'\n  - ' ORDER BY label)
      INTO problems
      FROM (
        SELECT 'kolon imzası: end_date ' ||
               coalesce(format_type(a.atttypid, a.atttypmod), '<yok>') ||
               CASE WHEN a.attnotnull THEN ' NOT NULL' ELSE ' NULL' END AS label
          FROM pg_attribute a
         WHERE a.attrelid = 'social.public_holidays'::regclass
           AND a.attname = 'end_date'
           AND a.attnum > 0
           AND NOT a.attisdropped
           AND (format_type(a.atttypid, a.atttypmod) <> 'date' OR a.attnotnull)
        UNION ALL
        SELECT 'kolon imzası: end_date kolonu YOK'
         WHERE NOT EXISTS (
            SELECT 1 FROM pg_attribute a
             WHERE a.attrelid = 'social.public_holidays'::regclass
               AND a.attname = 'end_date'
               AND a.attnum > 0
               AND NOT a.attisdropped
         )
        UNION ALL
        SELECT 'kısıt: public_holidays_end_date_check YOK'
         WHERE NOT EXISTS (
            SELECT 1 FROM pg_constraint
             WHERE conrelid = 'social.public_holidays'::regclass
               AND conname = 'public_holidays_end_date_check'
               AND contype = 'c'
         )
        UNION ALL
        -- Anahtarlar da `m035_seed_up`den okunur: dosyada seed değerlerinin TEK
        -- tanımı vardır, doğrulama kendi kopyasını taşımaz.
        SELECT 'takvim kalemi YOK: (' || s.year || ', ' || s.date || ')'
          FROM m035_seed_up s
         WHERE NOT EXISTS (
            SELECT 1 FROM social.public_holidays h
             WHERE h.year = s.year AND h.date = s.date
         )
      ) AS findings;

    IF problems IS NOT NULL THEN
        RAISE EXCEPTION 'migration 035 garanti dogrulamasi BASARISIZ:%',
            E'\n  - ' || problems
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Kalan kalemi elle duzeltip migration i yeniden kosturun.';
    END IF;
END
$verify_035$;
