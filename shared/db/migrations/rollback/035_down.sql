-- Migration 035 GERİ ALMA — takvim dönem desteği + üç takvim kalemi
--
-- KULLANIM:  psql -f 035_down.sql
--            Script `ON_ERROR_STOP`u KENDİ açar ve tüm gövdeyi TEK
--            transaction'a sarar. `-1` / `--single-transaction` GEÇMEYİN ve
--            dosyayı açık bir transaction'ın içinden `\i` ile çağırmayın:
--            transaction sahipliği bu dosyadadır (aynı sözleşme
--            `rollback/032_down.sql`de de yazılı; ölçüldü PG 18.3:
--            düz `psql -f` → rc=0, `psql -1 -f` → rc=3).
--
-- SAHİPLİK SINIRI (planın geri-alma hükmü):
--
--   Bu script YALNIZ 035'in KENDİ yazdığı üç satırı siler. "Kendi yazdığı" =
--   beş alanın da (year, date, name_tr, name_en, category) seed değerine
--   BİREBİR eşit olması. Aynı `(year, date)` anahtarında oturan ama içeriği
--   farklı bir satır 035'in DEĞİLDİR (`ON CONFLICT DO NOTHING` onu ezmedi) ve
--   dokunulmaz. Anahtara göre silmek, sahibi başkası olan bir satırı yok
--   ederdi.
--
--   Bir de TERS yön var: seed satırı sonradan yıllık takvim işi tarafından
--   düzeltilmişse (ad/kategori) artık beş-alan eşitliği tutmaz ve satır
--   BURADA KALIR. Bu bilinçlidir — düzeltilmiş satır artık 035'in yazdığı
--   satır değil, takvim beslemesinin bakımını üstlendiği bir satırdır.
--
-- NEDEN YABANCI DÖNEM SATIRI GERİ ALMAYI DURDURUR:
--
--   Kolon düşünce `end_date` taşıyan her satırın ANLAMI değişir: bir dönem,
--   035 ÖNCESİNDE VAR OLMAYAN bir hâle — "tek günlük" bir kayda — dönüşür.
--   035'in kendi üç satırı için bu bedel yoktur (onlar zaten siliniyor). Başka
--   birinin dönem satırı için sessiz bir ANLAM KAYBI olurdu. Bu yüzden kapı
--   fail-closed'dır: yabancı dönem satırı varsa HİÇBİR ŞEY yapmadan durur.
--   İşletim yolu açık: o satırların dönemini önce elle boşaltın, sonra geri
--   almayı koşturun.
--
-- ÜRETİCİ DE SÜRÜMLENİR: `shared/n8n-workflows/turkey-calendar-update.json`
-- dönem-farkında yazıma geçti. Geri alma o workflow'un ÖNCEKİ sürümüne dönmeyi
-- de kapsar; yoksa eski şemaya `end_date` yazmaya çalışan bir iş kalır.

\set ON_ERROR_STOP on

-- ---------------------------------------------------------------------------
-- -1. Sarmalayıcı-transaction kapısı — sahiplik çakışmasını SAPTA
-- ---------------------------------------------------------------------------

\echo 'Not: bir sonraki adim "invalid transaction termination" derse, bu dosya'
\echo '     sarmalayici bir transaction icinden cagrilmistir (ornegin psql -1).'
\echo '     Dosya kendi transaction ini sahiplenir; sarmalamadan cagirin.'

DO $nesting_guard$
BEGIN
    COMMIT;
END
$nesting_guard$;

BEGIN;

SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- ---------------------------------------------------------------------------
-- 0. PREFLIGHT — tabloyu kilitle, sonra oku; yabancı dönem varsa DUR
-- ---------------------------------------------------------------------------
--
-- Kilit ÖNCE, okuma SONRA: sayımdan sonra araya giren bir yazar olamaz. Kilit
-- transaction sonuna kadar tutulur, yani silme ve kolon düşürme boyunca.
--
-- `end_date`e dokunan her sorgu EXECUTE ile koşar: kolon yoksa dosya PARSE
-- aşamasında değil, kendi kapısında ve anlaşılır bir mesajla durmalıdır.

DO $preflight$
DECLARE
    foreign_periods BIGINT := 0;
    sample TEXT;
BEGIN
    IF to_regclass('social.public_holidays') IS NULL THEN
        RAISE EXCEPTION 'migration 035 geri alma REDDEDILDI: social.public_holidays tablosu YOK'
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Olmayan tablo kilitlenemez; koruma kurulamaz.';
    END IF;

    EXECUTE 'LOCK TABLE social.public_holidays IN ACCESS EXCLUSIVE MODE';

    IF NOT EXISTS (
        SELECT 1 FROM pg_attribute a
         WHERE a.attrelid = 'social.public_holidays'::regclass
           AND a.attname = 'end_date'
           AND a.attnum > 0
           AND NOT a.attisdropped
    ) THEN
        RAISE EXCEPTION 'migration 035 geri alma REDDEDILDI: end_date kolonu YOK'
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = '035 uygulanmamis (ya da zaten geri alinmis) bir sema. '
                         'Geri alma ikinci kez kosturulmaz.';
    END IF;

    -- Yabancı dönem = `end_date` dolu VE 035'in üç satırından biri DEĞİL.
    EXECUTE $q$
        SELECT count(*), string_agg(DISTINCT format('(%s, %s, %L)', year, date, name_tr), ', ')
          FROM social.public_holidays h
         WHERE h.end_date IS NOT NULL
           AND NOT (h.year = 2026 AND h.date = DATE '2026-08-15'
                    AND h.name_tr = 'Okula Dönüş'
                    AND h.name_en IS NOT DISTINCT FROM 'Back to School'
                    AND h.category IS NOT DISTINCT FROM 'commercial'
                    AND h.end_date = DATE '2026-09-15')
    $q$ INTO foreign_periods, sample;

    IF foreign_periods > 0 THEN
        RAISE EXCEPTION
            'migration 035 geri alma REDDEDILDI: sahibi 035 OLMAYAN % donem satiri var: %',
            foreign_periods, sample
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Kolon dusunce o satirlar sessizce tek gunluk kayda donusurdu. '
                         'Once end_date lerini elle bosaltin, sonra geri almayi kosturun.';
    END IF;
END
$preflight$;

-- ---------------------------------------------------------------------------
-- 1. YALNIZ 035'in yazdığı üç satır — beş alan BİREBİR eşleşmeli
-- ---------------------------------------------------------------------------

DELETE FROM social.public_holidays h
 WHERE (h.year, h.date, h.name_tr, h.name_en, h.category) IN (
        (2026, DATE '2026-11-10', '10 Kasım Atatürk''ü Anma Günü',
         'Atatürk Memorial Day', 'national'),
        (2026, DATE '2026-11-24', '24 Kasım Öğretmenler Günü',
         'Teachers'' Day', 'commercial'),
        (2026, DATE '2026-08-15', 'Okula Dönüş',
         'Back to School', 'commercial')
       );

-- ---------------------------------------------------------------------------
-- 2. Kısıt + kolon
-- ---------------------------------------------------------------------------

ALTER TABLE social.public_holidays
    DROP CONSTRAINT IF EXISTS public_holidays_end_date_check;
ALTER TABLE social.public_holidays DROP COLUMN IF EXISTS end_date;

-- ---------------------------------------------------------------------------
-- 3. Kalıntı doğrulaması — fail-closed
-- ---------------------------------------------------------------------------
--
-- `DROP ... IF EXISTS` bir nesneyi ADIYLA arar; ad tutmuyorsa sessizce geçer.
-- Bu blok katalogtan GERÇEK durumu okur.

DO $verify_down$
DECLARE
    leftovers TEXT;
BEGIN
    SELECT string_agg(label, E'\n  - ' ORDER BY label)
      INTO leftovers
      FROM (
        SELECT 'kolon social.public_holidays.end_date' AS label
          FROM pg_attribute a
         WHERE a.attrelid = 'social.public_holidays'::regclass
           AND a.attname = 'end_date'
           AND a.attnum > 0
           AND NOT a.attisdropped
        UNION ALL
        SELECT 'kisit ' || conname
          FROM pg_constraint
         WHERE conrelid = 'social.public_holidays'::regclass
           AND conname = 'public_holidays_end_date_check'
        UNION ALL
        SELECT '035 seed satiri ' || name_tr
          FROM social.public_holidays h
         WHERE (h.year, h.date, h.name_tr, h.name_en, h.category) IN (
                (2026, DATE '2026-11-10', '10 Kasım Atatürk''ü Anma Günü',
                 'Atatürk Memorial Day', 'national'),
                (2026, DATE '2026-11-24', '24 Kasım Öğretmenler Günü',
                 'Teachers'' Day', 'commercial'),
                (2026, DATE '2026-08-15', 'Okula Dönüş',
                 'Back to School', 'commercial')
               )
      ) AS remaining;

    IF leftovers IS NOT NULL THEN
        RAISE EXCEPTION 'migration 035 geri alma EKSIK kaldi:%',
            E'\n  - ' || leftovers
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Kalan nesneyi elle dusurup script i yeniden kosturun.';
    END IF;
END
$verify_down$;

COMMIT;
