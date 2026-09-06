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
--   ATOMİKLİK SARMALAYICIYA BAĞLI DEĞİLDİR — ve bu bir DÜZELTMEDİR (fix turu
--   6, F3). Önceki yazım sarmalanmamış yol için yalnız İKİ DAR iddia taşıyordu
--   (düşebilen KAPILAR kalıcı DDL ile aynı deyimde · hatasız yolda tam
--   uygulama) ve "atomiklik isteniyorsa dosya sarmalanır" diyordu. O sınır
--   ÖLÇÜLDÜ ve yetmedi: kapılardan SONRA düşen bir adım şemayı commit edilmiş
--   bırakıyordu. Üstelik düşebilen o adımı bir önceki turun KENDİ çözümü açtı —
--   sabit köken izi (fix turu 5, F1) seed `INSERT`ine bir BİRİNCİL ANAHTAR
--   çakışması yüzeyi ekledi. Ölçüm (çıplak `psql`, ayrılmış UUID'lerden biri
--   BAŞKA bir tatil satırında): `rc=0`, kolon=1, kısıt=1, seed=1 — YARIM
--   UYGULAMA, üstelik "başarılı" raporlanmış.
--
--   Kapanış artık SAYIM değil YAPIdır: KALICI olan her şey — kolon, kısıt, seed
--   `INSERT`i ve garanti doğrulaması — TEK `DO $apply_035$` deyiminin İÇİNDEDİR.
--   Bir `DO` bloğu tek deyimdir: autocommit altında bile ya tamamı uygulanır ya
--   hiçbiri. Bloğun içine yeni bir düşebilen adım eklemek artık yeni bir
--   yarım-uygulama yolu AÇMAZ; "şu kapıyı da yukarı taşı" turunun kendisi biter.
--
--   Bloktan ÖNCE koşan üç deyim (manifest kapısı · `CREATE TEMP TABLE` ·
--   manifest `INSERT`i) KALICI HİÇBİR ŞEY yazmaz — hepsi `pg_temp`tedir ve psql
--   oturumuyla ölür. Düşerlerse blok kendi kapısında (manifest relkind / satır
--   sayısı) DURur ve geride iz kalmaz.
--
--   Kanıt elle seçilmiş örnek değil ÜRETİLMİŞ çapraz çarpımdır:
--   `test_no_partial_apply_under_any_invocation` — 4 çağrı biçimi (çıplak ·
--   `ON_ERROR_STOP=1` · `--single-transaction` · ikisi birlikte) × 5 arıza
--   (arızasız · ayrılmış UUID başka satırda · manifest adını tutan indeks ·
--   kanonik olmayan aynı adlı kısıt · garanti doğrulamasının düşürülmesi) = 20
--   hücre. Her hücrede iddia AYNI: ret geldiyse kalıcı durum ÖNCESİNE eşit.
--
--   Aşağıdaki seed manifestinin ömrü OTURUMdur, transaction değil — ayrıntı ve
--   ölçüm manifestin başında.
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
-- `tests/test_migration_035.py::test_manifest_squatter_matrix` (136 hücre:
-- 2 dosya × 4 çağrı biçimi × 17 adı-tutan-nesne; ölçüldü, çarpılmadı).
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
--
-- BU DÜZELTMENİN KENDİ YAN ETKİSİ, ÖLÇÜLDÜ. Sabit `id` yeni bir çakışma yüzeyi
-- açar: bir seed satırının TARİHİ elle değiştirilirse (id sabit kalarak),
-- ikinci koşumun `INSERT`i o id'yi yeni bir `(year, date)` için yazmaya çalışır
-- ve `ON CONFLICT (year, date)` arbiter'ı bir BİRİNCİL ANAHTAR çakışmasını
-- yakalamaz. Ölçüldü (035 uygulanmış scratch veritabanı, seed satırının tarihi
-- 2026-11-11'e kaydırıldı, sonra `--single-transaction` ile ikinci koşum):
--   * bu dosya (arbiter `(year, date)`) → `rc=3`,
--     `ERROR: duplicate key value violates unique constraint
--     "public_holidays_pkey"`, hiçbir şey uygulanmadı.
--   * arbiter'sız (`ON CONFLICT DO NOTHING`) alternatif → yine `rc=3`, bu kez
--     `migration 035 garanti dogrulamasi BASARISIZ` (anahtar gerçekten YOK).
-- Yani senaryo İKİ biçimde de FAIL-CLOSED ve GÜRÜLTÜLÜdür; fark yalnız mesajın
-- okunaklığıdır. Arbiter DEĞİŞTİRİLMEDİ, çünkü `ON CONFLICT (year, date)`
-- sözleşmesi plan ve testlerde adıyla yazılıdır ve ölçülen davranış farkı yok.
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
-- 1. KALICI OLAN HER ŞEY — kapılar · kolon · kısıt · seed · garanti, TEK deyim
-- ---------------------------------------------------------------------------
--
-- NİÇİN TEK BLOK (fix turu 6, F3). İki tur boyunca aynı eksende nokta düzeltmesi
-- yapıldı: önce "kapıyı yukarı taşı" (fix turu 5), sonra kapıyı kalıcı DDL ile
-- aynı deyime al. İkisi de DÜŞEBİLEN ADIMLARI SAYIYORDU ve her tur sayının
-- eksik olduğunu keşfetti — çünkü `ON_ERROR_STOP` olmadan psql hatadan SONRA
-- devam eder, yani AYRI bir deyimdeki her şey kendi transaction'ında commit
-- edilir. Sayım yerine yapı: kalıcı ne varsa bu tek `DO` bloğunun içinde.
--
-- BLOĞUN SIRASI: önce DÜŞEBİLEN KAPILAR, sonra KALICI DDL, sonra seed, en sonda
-- garanti doğrulaması. Sıra artık bir GÜVENLİK koşulu değil, okunabilirlik
-- tercihidir — nerede düşerse düşsün blok bütünüyle geri alınır.
--
-- KAPI 1 — MANİFEST GERÇEKTEN KURULDU MU. `to_regclass` yalnız adın DOLU
-- olduğunu söyler; adı bir İNDEKS tutuyorsa da doludur. Bu yüzden `relkind`
-- okunur ve satır sayısı doğrulanır: manifest yoksa 035 hiçbir kalıcı iz
-- bırakmaz. Payda kendini doğrulamak ZORUNDADIR (fix turu 2, N3): veriye dayalı
-- bir garanti boş kümede vakum olarak "sağlanır".
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
--
-- YAZILAN ALAN KÜMESİ MANİFESTTEN TÜRETİLİR (fix turu 6, F1). `INSERT`in ve
-- atlama raporunun kolon listeleri elle SAYILMAZ, `pg_attribute`den okunur:
-- manifeste bir alan eklenirse yazma ve raporlama onu kendiliğinden kapsar.
-- Elle yazılmış bir liste, tam da bu turun düzelttiği kusurun ("bir alan
-- atlanmış") kaynağıydı. Geri alma dosyası sahiplik yüklemini AYNI kuralla
-- kurar; iki dosyanın kolon kümesi eşitliği katalogdan ölçülür
-- (`test_ownership_predicate_covers_every_manifest_column`).
--
-- `end_date`e dokunan sorgular `EXECUTE` ile koşar: kolon bu bloğun İÇİNDE
-- eklenir, yani statik SQL'in ilk ayrıştırılma anına güvenmek gerekmesin
-- (aynı desen `rollback/035_down.sql` §1'de).
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
--
-- KARŞILAŞTIRMA ARTIK KÖKEN İZİNİ DE İÇERİR (fix turu 6, F1'in ölçülmüş yan
-- etkisi): karşılaştırılan alan kümesi "manifestin tüm kolonları eksi çakışma
-- anahtarı `(year, date)`"dir, yani `id` de içeridedir. Sonuç: anahtarı tutan
-- satır 035'in KENDİ satırıysa (ikinci koşum) id eşleşir ve uyarı ÇIKMAZ;
-- içeriği birebir aynı olsa bile BAŞKASININ satırıysa id eşleşmez ve uyarı
-- ÇIKAR. İkincisi daha dürüsttür: operatör kararı gerçekten yazılmamıştır.
--
-- GARANTİ DOĞRULAMASI (fail-closed): `IF NOT EXISTS` / `DO NOTHING` sessizce
-- atlar; son bölüm katalogtan ve tablodan GERÇEK durumu okur. Kapsam DAR
-- tutulmuştur: yalnız 035'in kendi açtıkları ölçülür (kolon imzası · kısıtın
-- GERÇEK TANIMI · üç anahtarın varlığı). Satırların İÇERİĞİ pinlenmez — takvim
-- beslemesinin ad/kategori düzeltme hakkı vardır ve pinli bir tuple o meşru
-- düzeltmeden sonra migration'ı düşürürdü. Manifest okumaları `pg_temp.` ile
-- NİTELENİR (fix turu 4, F3): niteliksiz bir ad düşman bir `search_path`
-- altında KALICI bir tablodan okunurdu.

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
-- dosya hemen ardından biter. Deyim kalıcı hiçbir şey yazmaz, yani atomiklik
-- bloğunun DIŞINDA durması bir yarım-uygulama yolu açmaz.
--
-- DÜRÜST SINIR: bu pin sunucunun mesajı YAYINLAMASINI garanti eder, operatörün
-- onu GÖRMESİNİ değil (çıktı yönlendirilmiş olabilir). Sunucu tarafındaki yarıyı
-- kapatır; kalan yarı işletim disiplinidir.

SET client_min_messages = 'notice';

DO $apply_035$
DECLARE
    canonical CONSTANT TEXT := 'CHECK (((end_date IS NULL) OR (end_date >= date)))';
    -- `ON CONFLICT` arbiter'ı: dosyada ADIYLA yazılı sözleşme. Atlama raporu
    -- "içerik" karşılaştırmasından bu iki alanı dışlar, çünkü onlar zaten
    -- eşittir (satırlar o anahtarda çakışmıştır).
    arbiter CONSTANT TEXT[] := ARRAY['year', 'date'];
    held_kind "char";
    manifest_rows INT;
    ins_cols TEXT;
    cmp_h TEXT;
    cmp_s TEXT;
    show_row TEXT;
    found_def TEXT;
    found_type "char";
    found_valid BOOLEAN;
    written INT := 0;
    occupied_count INT := 0;
    occupied TEXT;
    problems TEXT;
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

    -- Alan kümesi KATALOGDAN — elle sayılmaz (fix turu 6, F1).
    SELECT string_agg(quote_ident(a.attname), ', ' ORDER BY a.attnum),
           string_agg('h.' || quote_ident(a.attname), ', ' ORDER BY a.attnum)
             FILTER (WHERE NOT (a.attname = ANY (arbiter))),
           string_agg('s.' || quote_ident(a.attname), ', ' ORDER BY a.attnum)
             FILTER (WHERE NOT (a.attname = ANY (arbiter))),
           string_agg(quote_literal(a.attname) || ', h.' || quote_ident(a.attname),
                      ', ' ORDER BY a.attnum)
             FILTER (WHERE NOT (a.attname = ANY (arbiter)))
      INTO ins_cols, cmp_h, cmp_s, show_row
      FROM pg_attribute a
     WHERE a.attrelid = 'pg_temp.m035_seed_up'::regclass
       AND a.attnum > 0
       AND NOT a.attisdropped;

    IF ins_cols IS NULL OR cmp_h IS NULL THEN
        RAISE EXCEPTION
            'migration 035: seed manifestinin kolon kumesi okunamadi'
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Manifest kolonlari bu dosyanin yazdigi alan kumesidir; '
                         'okunamiyorsa hicbir sey yazilmaz.';
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

    -- Buradan sonrası KALICI — ve hepsi BU deyimin içinde.
    EXECUTE 'ALTER TABLE social.public_holidays ADD COLUMN IF NOT EXISTS end_date DATE';

    IF found_def IS NULL THEN
        EXECUTE 'ALTER TABLE social.public_holidays '
                'ADD CONSTRAINT public_holidays_end_date_check '
                'CHECK (end_date IS NULL OR end_date >= date)';
    END IF;

    EXECUTE format(
        'WITH ins AS ('
        '    INSERT INTO social.public_holidays (%1$s) '
        '    SELECT %1$s FROM pg_temp.m035_seed_up '
        '    ON CONFLICT (year, date) DO NOTHING '
        '    RETURNING 1'
        ') SELECT count(*) FROM ins', ins_cols)
      INTO written;

    IF written < manifest_rows THEN
        -- Sessiz kalınacak tek durum: anahtar dolu AMA satır 035'in KENDİ
        -- satırı (köken izi + içerik birebir aynı). Farklıysa duyurulur;
        -- "farklı" ifadesi beslemenin meşru düzeltmesini de kapsar.
        EXECUTE format(
            'SELECT count(*), string_agg('
            '    format(''(%%s, %%s) anahtarini tutan satir: %%s'', '
            '           s.year, s.date, jsonb_build_object(%2$s)::text), '
            '    %1$L ORDER BY s.date) '
            '  FROM pg_temp.m035_seed_up s '
            '  JOIN social.public_holidays h '
            '    ON h.year = s.year AND h.date = s.date '
            ' WHERE (%3$s) IS DISTINCT FROM (%4$s)',
            E'\n  - ', show_row, cmp_h, cmp_s)
          INTO occupied_count, occupied;

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

    -- ── GARANTİ DOĞRULAMASI — fail-closed ───────────────────────────────────
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
$apply_035$;
