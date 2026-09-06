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
--   SARMALI KOŞUM ATOMİKLİK İÇİN ŞARTTIR — ve bu cümle bir düzeltmedir (fix
--   turu 5, F3). Önceki yazım "dosya sarmalanmamış `psql -f` altında da TAM
--   uygulanır" diyordu; ÖLÇÜLDÜ ki yanlıştı: çıplak `psql` (ON_ERROR_STOP yok)
--   + `m035_seed_up` adını tutan bir indeks squatter'ı ile `rc=0`, kolon VE
--   kısıt commit edilmiş, seed satırı 0 — yarım uygulanmış bir şema "başarılı"
--   raporlanıyordu. Üstelik testin kendi matrisi o hücrede `kolon=var, seed=0`
--   BEKLİYORDU, yani sevk edilen dosya kendi testiyle çelişiyordu.
--
--   Bugün geçerli olan iki AYRI ve DAR iddia:
--     (1) Bu dosyanın DÜŞEBİLEN KAPILARI (manifest kurulumu · kısıt kimliği)
--         kalıcı DDL ile AYNI DEYİMDEDİR. Kapıyı yukarı taşımak yetmezdi:
--         ölçüldü ki `ON_ERROR_STOP` olmadan psql hatadan sonra DEVAM eder,
--         yani ayrı bir deyimdeki `ALTER TABLE` yine koşar ve commit edilir.
--         Kapı reddederse sarmalanmamış yolda da geride kolon/kısıt KALMAZ —
--         ölçüm: `test_no_permanent_ddl_lands_before_the_droppable_gate` ve
--         `test_manifest_squatter_matrix`in `up` hücreleri.
--     (2) Hatasız yolda çıplak `psql -f` de dosyayı tam uygular — ölçüm:
--         `test_bare_psql_apply_is_complete` (çıplak ve `ON_ERROR_STOP=1`).
--   İkisi ATOMİKLİK DEĞİLDİR: kapılardan SONRA doğan bir hata (örneğin garanti
--   doğrulaması) sarmalanmamış koşumda kolonu ve kısıtı commit edilmiş bırakır.
--   Atomiklik isteniyorsa dosya sarmalanır; onaylı yolların hepsi sarmalar.
--   Aşağıdaki seed manifestinin ömrü bu yüzden OTURUMdur, transaction değil —
--   ayrıntı ve ölçüm manifestin başında.
--
-- GERİ ALMA: `rollback/035_down.sql`. Geri alma sahiplik sınırı taşır — YALNIZ
-- bu migration'ın yazdığı üç satırı kaldırır ve sahiplik KÖKENden okunur (aşağı
-- bakın: sabit `id`). Üretici (n8n takvim işi) şemayla BİRLİKTE sürümlenir:
-- geri alma o workflow'un önceki sürümüne dönmeyi de kapsar, yoksa eski şemaya
-- dönem-farkında bir üretici yazmaya çalışır. Dağıtım/geri alma sırası Task
-- 18'de listelenir.

-- ---------------------------------------------------------------------------
-- 0. SEED MANİFESTİ — düşebilen KAPI, her kalıcı DDL'den ÖNCE
-- ---------------------------------------------------------------------------
--
-- SIRA BİLİNÇLİDİR (fix turu 5, F3): bu bölüm reddedebilir, o yüzden hiçbir
-- kalıcı değişikliğin ARDINDAN gelmez. Kolon ve kısıt aşağıda, tüm kapılar
-- geçtikten sonra eklenir.
--
-- Değerler `m035_seed_up`de TEK KEZ tanımlanır; yazım, karşılaştırma ve garanti
-- doğrulaması üçü de oradan okur, yani ayrışamazlar.
--
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
-- `tests/test_migration_035.py::test_manifest_squatter_matrix`.
-- `to_regclass` KULLANILIR, `DROP TABLE IF EXISTS pg_temp.…` DEĞİL: ölçüldü,
-- ikincisi henüz temp şeması olmayan taze bir oturumda her koşumda
-- `NOTICE: schema "pg_temp" does not exist, skipping` basar ve aşağıdaki
-- ANLAMLI uyarının sinyalini gürültüye boğardı. `to_regclass` sessizdir.

DO $prepare_manifest$
DECLARE
    held_kind "char";
    drop_stmt TEXT;
BEGIN
    SELECT c.relkind INTO held_kind
      FROM pg_class c
     WHERE c.oid = to_regclass('pg_temp.m035_seed_up');

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
    -- pg_temp.m035_seed_up (…)` → `relkind='f'`, `relnamespace='pg_temp_26'`.
    -- `CASCADE` ZORUNLU: bağımlısı olan bir tabloda `DROP` CASCADE'siz
    -- patlıyordu (ölçüldü, bağımsız hakem F2). Ölçüldü ki bu yedi kindin
    -- YEDİSİNDE de geçerli — her birinin bağımlı-nesne hücresi vardır (fix
    -- turu 5, F5). Bağımlı nesne bizim ayrılmış adımıza dayanmayı seçmiştir;
    -- onunla birlikte gider.
    drop_stmt := CASE held_kind
        WHEN 'r' THEN 'DROP TABLE pg_temp.m035_seed_up CASCADE'
        WHEN 'p' THEN 'DROP TABLE pg_temp.m035_seed_up CASCADE'
        WHEN 'v' THEN 'DROP VIEW pg_temp.m035_seed_up CASCADE'
        WHEN 'm' THEN 'DROP MATERIALIZED VIEW pg_temp.m035_seed_up CASCADE'
        WHEN 'S' THEN 'DROP SEQUENCE pg_temp.m035_seed_up CASCADE'
        WHEN 'c' THEN 'DROP TYPE pg_temp.m035_seed_up CASCADE'
        WHEN 'f' THEN 'DROP FOREIGN TABLE pg_temp.m035_seed_up CASCADE'
    END;

    IF drop_stmt IS NULL THEN
        -- ELE ALINMAYAN, BİLEREK: `i`/`I` (indeks) o adı taşısa bile BİZİM
        -- OLMAYAN bir tabloya aittir — düşürmek ad rezervasyonunun ötesine,
        -- başkasının nesnesine uzanırdı. Kalanı tahmin etmek yerine DUR.
        RAISE EXCEPTION
            'migration 035: pg_temp.m035_seed_up adini beklenmeyen turde bir nesne tutuyor (relkind=%)',
            held_kind
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Bu ad bu migration a ayrilmistir; nesneyi elle kaldirip '
                         'yeniden kosturun.';
    END IF;

    EXECUTE drop_stmt;
END
$prepare_manifest$;

-- KÖKEN İZİ (fix turu 5, F1): `id` operatör kararı DEĞİL, teknik kimliktir.
-- Sahiplik artık İÇERİKTEN türetilmez, KÖKENden okunur. Ölçülen kusur:
-- geri alma "beş alanı seed'e birebir eşit olan" satırı 035'in sayıyordu; oysa
-- 035'ten ÖNCE aynı içerikle var olan bir satırı `up` atlar (`DO NOTHING`,
-- ölçüldü: satırın `id`si değişmiyor) ve `down` onu yine de SİLİYORDU — planın
-- "önceden var olan satırlara dokunmaz" hükmünün doğrudan ihlali.
-- Sabit `id` bu belirsizliği kaldırır: satır bu id'yi taşıyorsa onu bu
-- migration'ın `INSERT`i yaratmıştır, taşımıyorsa yaratmamıştır.
CREATE TEMP TABLE m035_seed_up (
    id       UUID    NOT NULL,
    year     INTEGER NOT NULL,
    date     DATE    NOT NULL,
    name_tr  TEXT    NOT NULL,
    name_en  TEXT,
    category TEXT,
    end_date DATE
);

INSERT INTO pg_temp.m035_seed_up (id, year, date, name_tr, name_en, category, end_date) VALUES
  ('03500000-0000-4035-8035-000000000001', 2026, DATE '2026-11-10', '10 Kasım Atatürk''ü Anma Günü', 'Atatürk Memorial Day', 'national',   NULL),
  ('03500000-0000-4035-8035-000000000002', 2026, DATE '2026-11-24', '24 Kasım Öğretmenler Günü',     'Teachers'' Day',       'commercial', NULL),
  ('03500000-0000-4035-8035-000000000003', 2026, DATE '2026-08-15', 'Okula Dönüş',                   'Back to School',       'commercial', DATE '2026-09-15');

-- ---------------------------------------------------------------------------
-- 1. ŞEMA — kapılar ve kalıcı DDL, TEK deyimde
-- ---------------------------------------------------------------------------
--
-- NİÇİN TEK BLOK (fix turu 5, F3). Kapıyı yukarı taşımak YETMEDİ: ölçüldü ki
-- `ON_ERROR_STOP` OLMADAN psql bir hatadan SONRA devam eder, yani manifest
-- kapısı reddetse bile bir sonraki `ALTER TABLE` yine koşar ve kendi
-- transaction'ında COMMIT edilir. (Ölçüm: çıplak `psql` + indeks squatter'ı →
-- `rc=0`, kolon+kısıt commit, seed 0.) Kapı ile kalıcı DDL AYNI DEYİMDE
-- olmadıkça "kapı önce koşar" bir şey garanti etmez.
--
-- Bir `DO` bloğu tek deyimdir: autocommit altında bile ya tamamı uygulanır ya
-- hiçbiri. Kapılar bloğun BAŞINDA, kalıcı DDL SONUNDA.
--
-- KAPI 1 — MANİFEST GERÇEKTEN KURULDU MU. `to_regclass` yalnız adın DOLU
-- olduğunu söyler; adı bir İNDEKS tutuyorsa da doludur. Bu yüzden `relkind`
-- okunur ve satır sayısı doğrulanır: manifest yoksa 035 hiçbir kalıcı iz
-- bırakmaz.
--
-- KAPI 2 — KISIT KİMLİĞİ ADdan DEĞİL TANIMdan. ÖLÇÜLEN KUSUR (fix turu 5, F2):
-- kurulum bloğu yalnız `conname`e, garanti doğrulaması yalnız
-- `conname + contype='c'`ye bakıyordu; hiçbiri TANIMI okumuyordu. Ölçüldü:
-- 035'ten ÖNCE aynı adla `CHECK (true)` konursa migration `rc=0` ile BAŞARILI
-- dönüyor ve `end_date < date` olan satır YAZILABİLİYOR — yani "ters dönem
-- veritabanıyla engellenir" hükmü, tam da engellemesi gereken vakada boş bir
-- addı. Pozitif kontrol kolunda gerçek kısıt aynı satırı reddediyor.
--
-- Karşılaştırma EXACT-MATCH POZİTİF SÖZLEŞMEdir, "şunu içeriyor mu" değil:
-- serbest metinden "bu kısıt yanlış DEĞİL" kanıtlanamaz. Deparse edilmiş metin
-- PG sürümüne bağlıdır; başka bir sürümde farklıysa migration SESSİZ GEÇMEZ,
-- burada DURur ve insan literal'i günceller. Fail-closed.
--
-- `ADD CONSTRAINT`in `IF NOT EXISTS` biçimi YOKTUR; varlık katalogdan okunur.
-- Aksi hâlde ikinci koşum `duplicate_object` ile DURur ve ondan sonraki hiçbir
-- migration uygulanmazdı.

DO $apply_schema$
DECLARE
    canonical CONSTANT TEXT := 'CHECK (((end_date IS NULL) OR (end_date >= date)))';
    held_kind "char";
    manifest_rows INT;
    found_def TEXT;
    found_type "char";
    found_valid BOOLEAN;
BEGIN
    SELECT c.relkind INTO held_kind
      FROM pg_class c
     WHERE c.oid = to_regclass('pg_temp.m035_seed_up');

    IF held_kind IS DISTINCT FROM 'r' THEN
        RAISE EXCEPTION
            'migration 035: seed manifesti kurulamadi (pg_temp.m035_seed_up relkind=%)',
            coalesce(held_kind::text, '<yok>')
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Manifest kurulmadan hicbir kalici DDL uygulanmaz. '
                         'Onceki hatayi cozup migration i yeniden kosturun.';
    END IF;

    SELECT count(*) INTO manifest_rows FROM pg_temp.m035_seed_up;
    IF manifest_rows <> 3 THEN
        RAISE EXCEPTION
            'migration 035: seed manifesti % satir tasiyor (beklenen 3)', manifest_rows
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Manifest bu dosyanin TEK seed tanimidir; bos/eksik '
                         'manifest butun kapilari vakuma cevirir.';
    END IF;

    SELECT pg_get_constraintdef(c.oid), c.contype, c.convalidated
      INTO found_def, found_type, found_valid
      FROM pg_constraint c
     WHERE c.conrelid = 'social.public_holidays'::regclass
       AND c.conname = 'public_holidays_end_date_check';

    IF found_def IS NOT NULL
       AND (found_type <> 'c' OR NOT found_valid OR found_def <> canonical) THEN
        RAISE EXCEPTION
            'migration 035: public_holidays_end_date_check adini KANONIK OLMAYAN bir kisit tutuyor (contype=%, convalidated=%, tanim=%)',
            found_type, found_valid, found_def
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Beklenen tanim: CHECK (((end_date IS NULL) OR (end_date >= date))). '
                         'Ayni adi tasiyan ilgisiz kisiti elle cozup migration i '
                         'yeniden kosturun.';
    END IF;

    -- Buradan sonrası KALICI. Yukarıdaki kapıların hepsi geçti.
    EXECUTE 'ALTER TABLE social.public_holidays ADD COLUMN IF NOT EXISTS end_date DATE';

    IF found_def IS NULL THEN
        EXECUTE 'ALTER TABLE social.public_holidays '
                'ADD CONSTRAINT public_holidays_end_date_check '
                'CHECK (end_date IS NULL OR end_date >= date)';
    END IF;
END
$apply_schema$;

-- ---------------------------------------------------------------------------
-- 2. Üç takvim kalemi (emsal: `002_autoposting.sql:29-40`)
-- ---------------------------------------------------------------------------
--
-- `DO NOTHING` bilinçlidir ve DEĞİŞMEDİ: aynı `(year, date)` anahtarında ZATEN
-- bir satır varsa o satır bu migration'ın DEĞİLDİR ve ezilmez. Ad/kategori
-- düzeltme hakkı takvim beslemesinindir (yıllık n8n işi), bir seed bloğunun
-- değil. Atlanan satıra köken izi de BASILMAZ — sahiplik tam da buradan doğar.
--
-- ATLAMA GÖRÜNÜRDÜR (fix turu 1, Q2). Ölçülen boşluk: fail-closed doğrulama üç
-- anahtarın yalnızca VAR OLDUĞUNU ölçüyor — bilinçli olarak, çünkü içeriği
-- pinlemek beslemenin meşru düzeltmesini migration hatasına çevirirdi. Sonucu
-- şuydu: hedef veritabanı o anahtarlardan birini zaten tutuyorsa migration
-- BAŞARILI rapor ediyor, operatör kararındaki değerler hiç yazılmıyor ve kimse
-- haberdar olmuyordu. Aşağıdaki blok gerçekten kaç satır yazıldığını sayar ve
-- içeriği operatör kararından FARKLI olan dolu anahtarları NOTICE ile duyurur.
-- NOTICE'tir, EXCEPTION değil: dolu anahtar bir şema hatası değil, insan gözü
-- isteyen bir veri durumudur.

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
            (id, year, date, name_tr, name_en, category, end_date)
        SELECT s.id, s.year, s.date, s.name_tr, s.name_en, s.category, s.end_date
          FROM pg_temp.m035_seed_up s
        ON CONFLICT (year, date) DO NOTHING
        RETURNING 1
    )
    SELECT count(*) INTO written FROM ins;

    IF written < (SELECT count(*) FROM pg_temp.m035_seed_up) THEN
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
          FROM pg_temp.m035_seed_up s
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
-- 3. Garanti doğrulaması — fail-closed
-- ---------------------------------------------------------------------------
--
-- `IF NOT EXISTS` / `DO NOTHING` sessizce atlar; bu blok katalogtan ve tablodan
-- GERÇEK durumu okur. Kapsam DAR tutulmuştur: yalnız 035'in kendi açtıkları
-- ölçülür (kolon imzası · kısıtın GERÇEK TANIMI · üç anahtarın varlığı).
-- Satırların İÇERİĞİ pinlenmez — takvim beslemesinin ad/kategori düzeltme hakkı
-- vardır ve pinli bir tuple o meşru düzeltmeden sonra migration'ı düşürürdü.
--
-- MANİFEST OKUMALARI `pg_temp.` İLE NİTELENİR (fix turu 4, F3): niteliksiz bir
-- ad düşman bir `search_path` altında KALICI bir tablodan okunurdu ve bu blok
-- yanlış paydayı doğrular, yanlış anahtarları arardı. Ölçüm:
-- `test_manifest_is_read_from_pg_temp_not_search_path` (tuzak BEŞ satırlıdır,
-- yani niteliksiz bir payda okuması `5 <> 3` ile DURur).

DO $verify_035$
DECLARE
    canonical CONSTANT TEXT := 'CHECK (((end_date IS NULL) OR (end_date >= date)))';
    problems TEXT;
    manifest_rows INT;
BEGIN
    -- PAYDA ÖNCE (fix turu 2, N3). Anahtar kontrolü literal bir liste yerine
    -- `m035_seed_up` üzerinde dönüyor; manifest boşsa blok hiçbir sorun
    -- BULAMAZ ve migration hiçbir şey seed etmemiş olarak "başarılı" raporlar.
    -- Veriye dayalı bir payda kendini doğrulamak zorundadır, yoksa garanti boş
    -- kümede vakum olarak sağlanır. (Sarmalayıcı altında boş manifeste giden bir
    -- yol ÖLÇÜLMEDİ — kapı yine de konur, çünkü maliyeti bir satır.)
    SELECT count(*) INTO manifest_rows FROM pg_temp.m035_seed_up;
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
        -- KISIT ADdan değil TANIMdan doğrulanır (fix turu 5, F2).
        SELECT 'kısıt: public_holidays_end_date_check kanonik DEĞİL ya da YOK ('
               || coalesce(
                    (SELECT pg_get_constraintdef(c.oid)
                            || ', contype=' || c.contype::text
                            || ', convalidated=' || c.convalidated::text
                       FROM pg_constraint c
                      WHERE c.conrelid = 'social.public_holidays'::regclass
                        AND c.conname = 'public_holidays_end_date_check'),
                    '<yok>')
               || ')'
         WHERE NOT EXISTS (
            SELECT 1 FROM pg_constraint c
             WHERE c.conrelid = 'social.public_holidays'::regclass
               AND c.conname = 'public_holidays_end_date_check'
               AND c.contype = 'c'
               AND c.convalidated
               AND pg_get_constraintdef(c.oid) = canonical
         )
        UNION ALL
        -- Anahtarlar da `m035_seed_up`den okunur: dosyada seed değerlerinin TEK
        -- tanımı vardır, doğrulama kendi kopyasını taşımaz.
        SELECT 'takvim kalemi YOK: (' || s.year || ', ' || s.date || ')'
          FROM pg_temp.m035_seed_up s
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
