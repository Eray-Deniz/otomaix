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
-- `DO NOTHING` bilinçlidir: aynı `(year, date)` anahtarında ZATEN bir satır
-- varsa o satır bu migration'ın DEĞİLDİR ve ezilmez. Ad/kategori düzeltme hakkı
-- takvim beslemesinindir (yıllık n8n işi), bir seed bloğunun değil.

INSERT INTO social.public_holidays (year, date, name_tr, name_en, category, end_date) VALUES
  (2026, '2026-11-10', '10 Kasım Atatürk''ü Anma Günü', 'Atatürk Memorial Day', 'national',   NULL),
  (2026, '2026-11-24', '24 Kasım Öğretmenler Günü',     'Teachers'' Day',       'commercial', NULL),
  (2026, '2026-08-15', 'Okula Dönüş',                   'Back to School',       'commercial', '2026-09-15')
ON CONFLICT (year, date) DO NOTHING;

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
BEGIN
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
        SELECT 'takvim kalemi YOK: (' || k.year || ', ' || k.day || ')'
          FROM (VALUES (2026, DATE '2026-11-10'),
                       (2026, DATE '2026-11-24'),
                       (2026, DATE '2026-08-15')) AS k(year, day)
         WHERE NOT EXISTS (
            SELECT 1 FROM social.public_holidays h
             WHERE h.year = k.year AND h.date = k.day
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
