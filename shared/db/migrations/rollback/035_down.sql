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
-- SEED MANİFESTİ TEK YERDE (fix turu 1, M1): üç satırın değerleri aşağıda
-- `m035_seed_down` geçici tablosunda BİR KEZ tanımlanır; silme ve kalıntı
-- doğrulaması ikisi de o tablodan okur. Önceki yazımda aynı literal blok iki kez
-- kopyalanmıştı ve birini düzeltip diğerini unutmak, kalıntı doğrulamasının
-- silmenin sildiğinden BAŞKA bir şeyi denetlemesine yol açardı — sessizce.
--
-- MANİFEST ADI BU DOSYAYA ÖZELDİR VE KURULUMU İDEMPOTENTTİR (fix turu 3).
-- Arka arkaya iki tur AYNI eksende kusur üretti — manifest ömrü × oturum
-- paylaşımı × ad çakışması — çünkü her tur eksenin başka bir NOKTASINI seçti.
-- Eksen artık yük taşımıyor, çünkü iki bağımsız özellik birden sağlanıyor:
--   (1) KAYNAK PAYLAŞILMAZ: ileri dosya `m035_seed_up`, bu dosya
--       `m035_seed_down` kullanır. İki dosya tek ad için yarışmaz; hangi
--       sırayla, aynı oturumda kaç kez koşulursa koşulsun.
--   (2) KURULUM ÖMÜRDEN BAĞIMSIZ İDEMPOTENTTİR: aşağıdaki kapı adı tutan
--       nesneyi TÜRÜNE göre düşürür (tablo · bölümlenmiş tablo · view ·
--       materialized view · sequence · bileşik tür · foreign table), bilinmeyen
--       türde ise TAHMİN ETMEZ, DURur. Bu enumerasyon fix turu 5'te
--       DÜZELTİLDİ (F4): önceki yazım "tablo · view · materialized view ·
--       sequence · foreign table" diyordu; gerçekte `f` REDDEDİLİYOR, buna
--       karşılık sayılmayan `p` ve `c` ELE ALINIYORDU. Bugün `f` de ele alınır
--       ve liste `CASE` dallarıyla birebir aynıdır.
-- Bu yüzden `ON COMMIT DROP` de KALDIRILDI: manifestin ömrü artık hiçbir
-- şeyin doğruluk koşulu değil, iki dosya da aynı kuralla çalışıyor.
-- Kanıt elle seçilmiş örnek değil, üretilmiş çapraz çarpım:
-- `tests/test_migration_035.py::test_manifest_squatter_matrix` (dosya × çağrı
-- biçimi × adı tutan nesne) ve `::test_manifest_lifetime_matrix` (24 hücre).
--
-- SAHİPLİK SINIRI (planın geri-alma hükmü) — KÖKENDEN, ŞEKİLDEN DEĞİL:
--
--   Bu script YALNIZ 035'in KENDİ yazdığı üç satırı siler. "Kendi yazdığı" =
--   satırın `id`si 035'in bastığı SABİT köken izini taşıyor VE beş alan
--   (year, date, name_tr, name_en, category) seed değerine birebir eşit.
--
--   KÖKEN İZİ NEDEN GEREKTİ (fix turu 5, F1). Önceki yazım sahipliği YALNIZ
--   beş-alan eşitliğinden türetiyordu, yani "içeriği seed'e benzeyen" her satır
--   035'in sayılıyordu. ÖLÇÜLDÜ: 035'ten ÖNCE aynı içerikle var olan bir satırı
--   `up` atlıyor (`ON CONFLICT DO NOTHING`; satırın `id`si değişmiyor, yani 035
--   yazmadı) ama bu dosyanın silmesi onu SİLİYORDU — planın "önceden var olan
--   satırlara dokunmaz" hükmünün doğrudan ihlali. `INSERT` gerçekten satırı
--   yarattıysa köken izi basılır, atladıysa BASILMAZ; belirsizlik kalmaz.
--
--   İÇERİK EŞİTLİĞİ DE KORUNUR (daraltıcıdır, genişletici değil): seed satırı
--   sonradan yıllık takvim işi tarafından düzeltilmişse (ad/kategori) artık
--   beş-alan eşitliği tutmaz ve satır BURADA KALIR. Bu bilinçlidir — düzeltilmiş
--   satır artık 035'in yazdığı satır değil, takvim beslemesinin bakımını
--   üstlendiği bir satırdır.
--
-- DÖNEM SATIRI SESSİZCE DÜZLEŞEMEZ — ŞEKİL SEZGİSELİ KALDIRILDI:
--
--   Kolon düşünce `end_date` taşıyan her satırın ANLAMI değişir: bir dönem,
--   035 ÖNCESİNDE VAR OLMAYAN bir hâle — "tek günlük" bir kayda — dönüşür.
--   035'in kendi üç satırı için bu bir sorun değil; onları zaten siliyoruz.
--   BAŞKASININ dönem satırı için sessiz ve GERİ ALINAMAZ bir anlam kaybıdır.
--
--   Kapı artık "bu satır kimin?" sorusunu satırın GÖRÜNÜŞÜNDEN cevaplamıyor.
--   Ölçülen kusur (fix turu 5, F1-b): tur 1'de muafiyet `year = 2026`e
--   çivilenmişti; aynı tur onu "üreticinin yazdığı ŞEKLE" bakan bir muafiyete
--   çevirdi ki geri alma kendi üreticisi tarafından tetiklenmesin (Q1). O
--   muafiyetin bedeli ÖLÇÜLDÜ ve SESSİZDİ: üretici şekline uyan 2027 dönemi
--   MUAF tutuluyor, geri alma `rc=0` ile geçiyor, kolon düşüyor ve satır
--   hiçbir uyarı olmadan tek günlük kayda dönüşüyordu — dosyanın kendi HINT'i
--   tam da bunu önlemeyi vaat ederken.
--
--   Yerine KAPANIŞ ÖZELLİĞİ konur, silmeden SONRA ölçülür ve şekilden
--   bağımsızdır:
--
--       Silme bittiğinde `end_date` taşıyan HİÇBİR satır kalmamalıdır.
--
--   Kalıyorsa kolon düşürülmez; transaction geri alınır ve script hangi
--   satırların zarar göreceğini ADLANDIRARAK durur. Kapı fail-closed'dır ve
--   ikinci bir sahiplik kopyası taşımaz — silmenin BIRAKTIĞINI okur.
--
--   BEDELİ DÜRÜSTÇE: 1 Ocak'ta yıllık iş koştuktan sonra 035'i geri almak bir
--   OPERATÖR ADIMI ister — ilgili `end_date`leri elle boşaltmak. Bilinçli bir
--   takastır: sessiz ve geri alınamaz bir kayıp yerine görünür ve elle
--   çözülebilir bir duraklama. Zaten 035'i geri almak dönem yeteneğini tümden
--   kaldırır; dönem verisiyle ne yapılacağı operatörün kararıdır.
--
-- KISIT KİMLİĞİ ADdan DEĞİL TANIMdan (fix turu 5, F2): `DROP CONSTRAINT IF
-- EXISTS` nesneyi yalnız ADIYLA arar, yani aynı adı taşıyan İLGİSİZ bir kısıtı
-- sessizce düşürürdü. Aşağıdaki ön kontrol kısıtın GERÇEK tanımını okur ve
-- kanonik değilse hiçbir şey yapmadan DURur.
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
-- 0. SEED MANİFESTİ — üç satırın değerleri + köken izi, TEK tanım
-- ---------------------------------------------------------------------------
--
-- Ömür OTURUMdur (bkz. başlık): kapı adı tutan her nesneyi türüne göre
-- düşürdüğü için manifestin ne zaman öldüğü doğruluk koşulu DEĞİLDİR.

DO $prepare_manifest$
DECLARE
    held_kind "char";
    drop_stmt TEXT;
BEGIN
    SELECT c.relkind INTO held_kind
      FROM pg_class c
     WHERE c.oid = to_regclass('pg_temp.m035_seed_down');

    IF held_kind IS NULL THEN
        RETURN;                       -- ad boş: yapacak bir şey yok
    END IF;

    -- ELE ALINAN KİNDLER = `pg_temp`te YARATILABİLDİĞİ ÖLÇÜLENLER (PG 18.3).
    -- Enumerasyon ölçüme eşittir: her dalın kendi test hücresi vardır
    -- (`test_manifest_squatter_matrix`), yani hiçbir dal ölçülmemiş değildir.
    -- `f` (foreign table) DE ele alınır (fix turu 5, F4): önceki yazım "bu
    -- kurulumda yaratılamıyor (ölçüldü: FDW sunucusu yok)" diyordu, oysa
    -- ölçülen şey "şu an tanımlı FDW SUNUCUSU yok"tu. Ölçüldü ki yaratılabilir:
    -- `CREATE EXTENSION file_fdw` → `CREATE SERVER …` → `CREATE FOREIGN TABLE
    -- pg_temp.m035_seed_down (…)` → `relkind='f'`.
    -- `CASCADE` ZORUNLU: bağımlısı olan bir nesnede CASCADE'siz `DROP`
    -- patlıyordu (ölçüldü, bağımsız hakem F2; fix turu 5'te yedi kindin
    -- yedisinde de ölçüldü ve her birinin bağımlı-nesne hücresi var).
    drop_stmt := CASE held_kind
        WHEN 'r' THEN 'DROP TABLE pg_temp.m035_seed_down CASCADE'
        WHEN 'p' THEN 'DROP TABLE pg_temp.m035_seed_down CASCADE'
        WHEN 'v' THEN 'DROP VIEW pg_temp.m035_seed_down CASCADE'
        WHEN 'm' THEN 'DROP MATERIALIZED VIEW pg_temp.m035_seed_down CASCADE'
        WHEN 'S' THEN 'DROP SEQUENCE pg_temp.m035_seed_down CASCADE'
        WHEN 'c' THEN 'DROP TYPE pg_temp.m035_seed_down CASCADE'
        WHEN 'f' THEN 'DROP FOREIGN TABLE pg_temp.m035_seed_down CASCADE'
    END;

    IF drop_stmt IS NULL THEN
        -- ELE ALINMAYAN, BİLEREK: `i`/`I` (indeks) o adı taşısa bile BİZİM
        -- OLMAYAN bir tabloya aittir — düşürmek ad rezervasyonunun ötesine,
        -- başkasının nesnesine uzanırdı. Kalanı tahmin etmek yerine DUR.
        RAISE EXCEPTION
            'migration 035: pg_temp.m035_seed_down adini beklenmeyen turde bir nesne tutuyor (relkind=%)',
            held_kind
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Bu ad bu migration a ayrilmistir; nesneyi elle kaldirip '
                         'yeniden kosturun.';
    END IF;

    EXECUTE drop_stmt;
END
$prepare_manifest$;

CREATE TEMP TABLE m035_seed_down (
    id       UUID    NOT NULL,
    year     INTEGER NOT NULL,
    date     DATE    NOT NULL,
    name_tr  TEXT    NOT NULL,
    name_en  TEXT,
    category TEXT,
    end_date DATE
);

INSERT INTO pg_temp.m035_seed_down (id, year, date, name_tr, name_en, category, end_date) VALUES
  ('03500000-0000-4035-8035-000000000001', 2026, DATE '2026-11-10', '10 Kasım Atatürk''ü Anma Günü', 'Atatürk Memorial Day', 'national',   NULL),
  ('03500000-0000-4035-8035-000000000002', 2026, DATE '2026-11-24', '24 Kasım Öğretmenler Günü',     'Teachers'' Day',       'commercial', NULL),
  ('03500000-0000-4035-8035-000000000003', 2026, DATE '2026-08-15', 'Okula Dönüş',                   'Back to School',       'commercial', DATE '2026-09-15');

-- ---------------------------------------------------------------------------
-- 1. PREFLIGHT — tabloyu kilitle, sonra oku; kısıt kimliğini doğrula
-- ---------------------------------------------------------------------------
--
-- Kilit ÖNCE, okuma SONRA: sayımdan sonra araya giren bir yazar olamaz. Kilit
-- transaction sonuna kadar tutulur, yani silme ve kolon düşürme boyunca.
--
-- `end_date`e dokunan her sorgu EXECUTE ile koşar: kolon yoksa dosya PARSE
-- aşamasında değil, kendi kapısında ve anlaşılır bir mesajla durmalıdır.

DO $preflight$
DECLARE
    canonical CONSTANT TEXT := 'CHECK (((end_date IS NULL) OR (end_date >= date)))';
    found_def TEXT;
    found_type "char";
    found_valid BOOLEAN;
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

    -- KISIT KİMLİĞİ (fix turu 5, F2): aynı adı taşıyan İLGİSİZ bir kısıt
    -- düşürülmez. Yoksa sorun değil — `DROP … IF EXISTS` zaten sessiz geçer.
    SELECT pg_get_constraintdef(c.oid), c.contype, c.convalidated
      INTO found_def, found_type, found_valid
      FROM pg_constraint c
     WHERE c.conrelid = 'social.public_holidays'::regclass
       AND c.conname = 'public_holidays_end_date_check';

    IF found_def IS NOT NULL
       AND (found_type <> 'c' OR NOT found_valid OR found_def <> canonical) THEN
        RAISE EXCEPTION
            'migration 035 geri alma REDDEDILDI: public_holidays_end_date_check adini KANONIK OLMAYAN bir kisit tutuyor (contype=%, convalidated=%, tanim=%)',
            found_type, found_valid, found_def
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Beklenen tanim: CHECK (((end_date IS NULL) OR (end_date >= date))). '
                         'Bu kisit 035 in DEGILDIR; dusurmek baskasinin nesnesini '
                         'yok etmek olurdu.';
    END IF;
END
$preflight$;

-- ---------------------------------------------------------------------------
-- 2. YALNIZ 035'in yazdığı üç satır — köken izi + beş alan BİREBİR eşleşmeli
-- ---------------------------------------------------------------------------

DELETE FROM social.public_holidays h
 WHERE (h.id, h.year, h.date, h.name_tr, h.name_en, h.category) IN (
        SELECT s.id, s.year, s.date, s.name_tr, s.name_en, s.category FROM pg_temp.m035_seed_down s
       );

-- ---------------------------------------------------------------------------
-- 3. KAPANIŞ ÖZELLİĞİ — silmeden SONRA hiçbir dönem satırı kalmamalı
-- ---------------------------------------------------------------------------
--
-- Bu kapı ikinci bir sahiplik kopyası TAŞIMAZ: silmenin BIRAKTIĞINI okur. Bir
-- satır burada duruyorsa 035 onun sahibi değildir; kolon düşerse dönemi sessizce
-- yok olurdu. Fail-closed.

DO $period_flattening_guard$
DECLARE
    doomed BIGINT := 0;
    sample TEXT;
BEGIN
    EXECUTE $q$
        SELECT count(*),
               string_agg(format('(%s, %s, %L)', h.year, h.date, h.name_tr),
                          ', ' ORDER BY h.year, h.date)
          FROM social.public_holidays h
         WHERE h.end_date IS NOT NULL
    $q$ INTO doomed, sample;

    IF doomed > 0 THEN
        RAISE EXCEPTION
            'migration 035 geri alma REDDEDILDI: % donem satiri sessizce tek gune donusurdu: %',
            doomed, sample
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Bu satirlarin sahibi 035 DEGILDIR (yillik takvim isi ya da '
                         'elle giris). Kolon dusunce donem bilgileri GERI ALINAMAZ '
                         'sekilde kaybolurdu. Once end_date lerini elle bosaltin, '
                         'sonra geri almayi kosturun.';
    END IF;
END
$period_flattening_guard$;

-- ---------------------------------------------------------------------------
-- 4. Kısıt + kolon
-- ---------------------------------------------------------------------------

ALTER TABLE social.public_holidays
    DROP CONSTRAINT IF EXISTS public_holidays_end_date_check;
ALTER TABLE social.public_holidays DROP COLUMN IF EXISTS end_date;

-- ---------------------------------------------------------------------------
-- 5. Kalıntı doğrulaması — fail-closed
-- ---------------------------------------------------------------------------
--
-- `DROP ... IF EXISTS` bir nesneyi ADIYLA arar; ad tutmuyorsa sessizce geçer.
-- Bu blok katalogtan GERÇEK durumu okur. Seed satırı sorgusu yukarıdaki
-- silmeyle AYNI manifestten okur — ikisi ayrışamaz.

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
        SELECT '035 seed satiri ' || h.name_tr
          FROM social.public_holidays h
         WHERE (h.id, h.year, h.date, h.name_tr, h.name_en, h.category) IN (
                SELECT s.id, s.year, s.date, s.name_tr, s.name_en, s.category FROM pg_temp.m035_seed_down s
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
