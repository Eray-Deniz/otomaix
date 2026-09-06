-- Migration 036 GERİ ALMA — koşu kaydı · geri alma planları · atama geçmişi
--
-- KULLANIM:  psql -f 036_down.sql
--            Script `ON_ERROR_STOP`u KENDİ açar ve tüm gövdeyi TEK
--            transaction'a sarar. `-1` / `--single-transaction` GEÇMEYİN ve
--            dosyayı açık bir transaction'ın içinden `\i` ile çağırmayın:
--            transaction sahipliği bu dosyadadır.
--
-- ÇAĞIRANIN OTURUMU BOZULMAZ (kontrolör kararı, bu görevde doğan ÜÇ script
-- için bağlayıcı). `032_down.sql` ve `035_down.sql` `\set ON_ERROR_STOP on`u
-- DOSYA KAPSAMINDA bırakır ve değer çağıranın psql oturumuna SIZAR. Bu dosya
-- önceki değeri saklar ve SONUNDA geri yükler; hiç ayarlanmamışsa `\unset`
-- eder. Ölçüm: `tests/test_migration_036.py::test_down_scripts_restore_caller_on_error_stop`
-- (3 script × 3 önceki durum = 9 hücre).
--
--   DÜRÜST SINIR — ölçülmüş: geri yükleme dosyanın SONUNDA koşar. RET yolunda
--   psql `ON_ERROR_STOP` yüzünden girdi işlemeyi keser ve o satıra ULAŞILMAZ;
--   çağıranın oturumunda değer `on` kalır. Bunu psql içinde kapatmanın yolu
--   YOKTUR: sıfır-dışı çıkış kodu (`rc=3`) yalnızca `ON_ERROR_STOP` açıkken
--   üretilir, yani "önce geri yükle, sonra hata ver" sırası ret'i sessiz
--   (`rc=0`) hâle getirirdi ve F20'nin fail-closed vaadi düşerdi. Sızan değer
--   `on`dur — çağıran DAHA KATI olur; davranış sürprizi, güvenlik açığı değil.
--   032/035 ile fark KAYIT ALTINDADIR, süpürülmemiştir.
--
-- F20 — GERİ ALMA VERİ VARKEN FAIL-CLOSED DURUR:
--
--   İlk yazım yalnız "şekil geri dönüyor mu" diye soruyordu. Ama pilot bir
--   `approval`/`rejection` olayı ürettikten sonra `package_events` CHECK'ini
--   daraltmak mevcut satır yüzünden ZATEN başarısız olur, satırları silmek ise
--   denetim izini yok eder. Aynısı koşu kayıtları, geri alma planları ve atama
--   geçmişi için geçerlidir — üçü de süresiz-saklama sınıfındaki KANITTIR.
--
--   Bu yüzden başta ATOMİK bir ön kontrol koşar: Plan 2 verisi VARSA `rc≠0` ile
--   DURur ve hiçbir şeye dokunmaz. Kilit ÖNCE, sayım SONRA — sayımdan sonra
--   araya giren bir yazar OLAMAZ (032'nin ölçülmüş dersi). Kilit sırası
--   SABİTTİR (iki koşum birbirini kilitlemez) ve ÜRETİCİ bağımlılık yönünü
--   izler, ad sırasını değil — gerekçe §0'da, kapı testtedir.
--
--   Pilot sonrası geri dönüş ŞEMA GERİ ALMASI DEĞİL, veri-koruyan İLERİ
--   DÜZELTME migration'ıdır; runbook (Task 18) ikisini ayrı başlıkta yazar.
--
-- KİMLİK KAPISI (F7): `DROP` ADIN gördüğünü düşürür. Preflight, düşürülecek
-- HER fonksiyon ve tetikleyici için katalogdan tanım okur; YOK ya da BİREBİR
-- KANONİK dışındaki her durumda fail-closed DURur. İleri dosyadaki KAPI 4'ün
-- aynadaki eşidir.
--
-- SIRA (036'nın açılış sırasının TERSİ):
--   1. `brands` tetikleyicisi (geçmiş tablosundan ÖNCE gider — tablo
--      düşerken tetikleyici ayakta kalsaydı bir sonraki marka yazımı
--      olmayan tabloya INSERT denerdi. Sebep KOLON BAĞIMLILIĞI DEĞİLDİR:
--      ölçüldü ki 036'nın tetikleyicisi kolon listesi taşımadığı için
--      `brands.sub_sector_id` üstünde katalog bağımlılığı KURMAZ.)
--   2. koşu + geri alma planı tetikleyicileri, sonra üç tablo
--   3. K-09 kısıtı  →  4. `package_events` CHECK'i daraltılır
--   5. fonksiyonlar  →  6. kalıntı doğrulaması
--
-- ÜRETİCİ DE SÜRÜMLENİR: `app/services/package_events.py` `APPROVAL_EVENTS` ile
-- genişledi. Geri alma o modülün önceki sürümüne dönmeyi de KAPSAR; yoksa
-- daraltılmış CHECK'e onay/ret yazmaya çalışan bir kod kalır.

-- ÖLÇÜLDÜ (psql 16.15): `ON_ERROR_STOP` psql'in YERLEŞİK değişkenidir ve HER
-- ZAMAN tanımlıdır — `-v ON_ERROR_STOP=1` verilmemiş taze bir oturumda bile
-- `:{?ON_ERROR_STOP}` DOĞRU döner ve değeri `off`tur; `\unset` onu tanımsız
-- yapmaz, varsayılana (`off`) döndürür. Bu yüzden koşullu bir dal YOKTUR:
-- değer koşulsuz saklanır, sonunda koşulsuz geri yüklenir. Ölçülmemiş bir
-- `\else` dalı taşımak, hiç koşulmayan bir kurtarma yolu taşımak olurdu.
\set OTOMAIX_DOWN_OES_ONCE :ON_ERROR_STOP

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
-- 0. PREFLIGHT — kilitle, say, Plan 2 verisi varsa DUR
-- ---------------------------------------------------------------------------

DO $preflight$
DECLARE
    olay_check_dar CONSTANT TEXT :=
        'CHECK ((event_type = ANY (ARRAY[''mismatch_fallthrough''::text,'
        ' ''package_read_error''::text, ''stale_assignment_fallback''::text,'
        ' ''stamp_missing''::text, ''stamp_invalid''::text,'
        ' ''stamp_stale_at_persist''::text, ''activation''::text,'
        ' ''rollback''::text, ''deactivation''::text])))';
    olay_check_genis CONSTANT TEXT :=
        'CHECK ((event_type = ANY (ARRAY[''mismatch_fallthrough''::text,'
        ' ''package_read_error''::text, ''stale_assignment_fallback''::text,'
        ' ''stamp_missing''::text, ''stamp_invalid''::text,'
        ' ''stamp_stale_at_persist''::text, ''activation''::text,'
        ' ''rollback''::text, ''deactivation''::text, ''approval''::text,'
        ' ''rejection''::text])))';
    k09_kanonik CONSTANT TEXT := 'UNIQUE (run_id, source, kind)';

    -- KİMLİK SABİTLERİ (F7). Tetikleyici tanımı `pg_get_triggerdef` biçiminde,
    -- ÖLÇÜLEREK pinlenmiştir — ileri dosyadaki sabitlerle AYNI metin.
    trg_brands_kanonik CONSTANT TEXT :=
        'CREATE TRIGGER brands_sub_sector_history AFTER INSERT OR UPDATE ON social.brands FOR EACH ROW EXECUTE FUNCTION social.track_brand_sub_sector_history()';
    trg_kosu_kanonik CONSTANT TEXT :=
        'CREATE TRIGGER sector_package_runs_approval_snapshot_immutable BEFORE UPDATE ON social.sector_package_runs FOR EACH ROW EXECUTE FUNCTION social.reject_approval_snapshot_mutation()';
    trg_plan_kanonik CONSTANT TEXT :=
        'CREATE TRIGGER package_rollback_plans_approved_immutable BEFORE UPDATE ON social.package_rollback_plans FOR EACH ROW EXECUTE FUNCTION social.reject_approved_rollback_plan_mutation()';

    -- FONKSİYON KİMLİĞİ GÖVDENİN ÖZETİYLE pinlenir, gövdenin İKİNCİ BİR
    -- KOPYASIYLA değil (SQL dosyaları birbirini içeremez; ileri dosyanın
    -- gövde sabitleri buraya kopyalansaydı iki metin sessizce ıraksardı).
    -- Özet CANLI katalogtan ölçülür ve `test_down_function_pins_match_the_live_catalog`
    -- ileri dosya değiştiği gün bu pini KIRMIZI düşürür.
    fn_track_ozet CONSTANT TEXT := 'acbbdd0d3cd2909368002b2a1e658c21';      -- len=1583
    fn_snapshot_ozet CONSTANT TEXT := '6b35399e0c93667855d214accb485d00';   -- len=641
    fn_plan_ozet CONSTANT TEXT := 'ed12ac9a70491e686620af7c7a6b687f';       -- len=1124

    kayit RECORD;

    eksik TEXT;
    kosu BIGINT := 0;
    plan BIGINT := 0;
    gecmis BIGINT := 0;
    onay BIGINT := 0;
    dolu TEXT;
    mevcut_def TEXT;
BEGIN
    -- KORUNAN TABLOLAR VAR OLMAK ZORUNDA (032'nin ölçülmüş dersi): olmayan bir
    -- tablo KİLİTLENEMEZ, yani koruma kurulamaz. "Yoksa atla" davranışı YOKTUR
    -- — sessizce devam eden bir koşumda, preflight ile `DROP` arasında başka
    -- biri 036'yı ileri uygularsa READ COMMITTED altında DROP o YENİ tabloyu
    -- görür ve kalıcı olarak yok ederdi.
    SELECT string_agg(ad, ', ' ORDER BY ad) INTO eksik
      FROM unnest(ARRAY['social.sector_package_runs',
                        'social.package_rollback_plans',
                        'social.brand_sub_sector_history',
                        'social.package_events',
                        'social.sector_research_artifacts',
                        'social.brands']) AS t(ad)
     WHERE to_regclass(ad) IS NULL;

    IF eksik IS NOT NULL THEN
        RAISE EXCEPTION
            'migration 036 geri alma REDDEDILDI: korunan tablolar eksik (%)', eksik
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Olmayan tablo kilitlenemez; koruma kurulamaz. 036 tam '
                         'uygulanmis bir sema uzerinde kosturun. Geri alma '
                         'ikinci kez kosturulmaz.';
    END IF;

    -- Kilit ÖNCE, sayım SONRA. Kilitler transaction sonuna kadar tutulur —
    -- yani yıkım boyunca.
    --
    -- SIRA ÜRETİCİ BAĞIMLILIK YÖNÜNDEDİR, AD SIRASINDA DEĞİL (Codex
    -- checkpoint, F3). Ad sırası `brand_sub_sector_history`yi ÖNCE, `brands`ı
    -- SONRA kilitliyordu; oysa normal yazım yolu TERS yöndedir: `brands`
    -- güncellenir, `brands_sub_sector_history` tetikleyicisi AYNI işlemde
    -- geçmiş tablosuna yazar (036, `track_brand_sub_sector_history`). İki
    -- işlem kilitleri zıt yönlerde alırsa deadlock penceresi açılır;
    -- PostgreSQL birini abort eder — tutarlılık için güvenli, ama ACİL geri
    -- almanın koşabilirliği belirsizleşir ve operatör "neden düştü"yü geri
    -- alma script'inde arar.
    --
    -- Sıra hâlâ SABİTTİR (iki geri alma koşumu birbirini kilitlemez): önce
    -- üretici tablolar bağımlılık yönünde, sonra kalanlar ad sırasında. Kalan
    -- tablolar arasında tetikleyici-yazım kenarı YOKTUR (ölçüldü: 036'da
    -- yalnız `brands` tetikleyicisi başka bir tabloya yazıyor; kapı
    -- `test_down_lock_order_follows_the_producer_direction`, kenarlar ve sıra
    -- dosyalardan TÜRETİLİR).
    EXECUTE 'LOCK TABLE social.brands IN ACCESS EXCLUSIVE MODE';
    EXECUTE 'LOCK TABLE social.brand_sub_sector_history IN ACCESS EXCLUSIVE MODE';
    EXECUTE 'LOCK TABLE social.package_events IN ACCESS EXCLUSIVE MODE';
    EXECUTE 'LOCK TABLE social.package_rollback_plans IN ACCESS EXCLUSIVE MODE';
    EXECUTE 'LOCK TABLE social.sector_package_runs IN ACCESS EXCLUSIVE MODE';
    EXECUTE 'LOCK TABLE social.sector_research_artifacts IN ACCESS EXCLUSIVE MODE';

    EXECUTE 'SELECT count(*) FROM social.sector_package_runs' INTO kosu;
    EXECUTE 'SELECT count(*) FROM social.package_rollback_plans' INTO plan;
    EXECUTE 'SELECT count(*) FROM social.brand_sub_sector_history' INTO gecmis;
    EXECUTE 'SELECT count(*) FROM social.package_events '
            'WHERE event_type IN (''approval'', ''rejection'')' INTO onay;

    -- YALNIZ DOLU sınıflar raporlanır: her koşumda tüm tablo adlarını basan bir
    -- mesaj, "hangi sınıf yüzünden durdu" sorusunu cevaplamaz ve testleri de
    -- yanlış sebeple yeşil yapardı.
    SELECT string_agg(satir, ', ' ORDER BY satir) INTO dolu
      FROM (VALUES ('sector_package_runs=' || kosu, kosu),
                   ('package_rollback_plans=' || plan, plan),
                   ('brand_sub_sector_history=' || gecmis, gecmis),
                   ('package_events onay/ret=' || onay, onay)) AS t(satir, adet)
     WHERE adet > 0;

    IF dolu IS NOT NULL THEN
        RAISE EXCEPTION
            'migration 036 geri alma REDDEDILDI: Plan 2 verisi var (%)', dolu
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Kosu kaydi, geri alma plani, atama gecmisi ve onay/ret '
                         'olaylari KANITTIR; script ile imha edilmez. Pilot '
                         'sonrasi yol GERI ALMA degil, veri-koruyan ILERI '
                         'DUZELTME migration idir.';
    END IF;

    -- KISIT KİMLİĞİ ADdan DEĞİL TANIMdan (035 fix turu 5, F2'nin taşınması):
    -- `DROP CONSTRAINT IF EXISTS` nesneyi yalnız ADIYLA arar, yani aynı adı
    -- taşıyan İLGİSİZ bir kısıtı sessizce düşürürdü.
    SELECT pg_get_constraintdef(c.oid) INTO mevcut_def
      FROM pg_constraint c
     WHERE c.conrelid = 'social.sector_research_artifacts'::regclass
       AND c.conname = 'sector_research_artifacts_run_source_kind_key';

    IF mevcut_def IS NOT NULL AND mevcut_def <> k09_kanonik THEN
        RAISE EXCEPTION
            'migration 036 geri alma REDDEDILDI: sector_research_artifacts_run_source_kind_key adini KANONIK OLMAYAN bir kisit tutuyor (tanim=%)',
            mevcut_def
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Beklenen tanim: UNIQUE (run_id, source, kind). Bu kisit '
                         '036 nin DEGILDIR; dusurmek baskasinin nesnesini yok '
                         'etmek olurdu.';
    END IF;

    SELECT pg_get_constraintdef(c.oid) INTO mevcut_def
      FROM pg_constraint c
     WHERE c.conrelid = 'social.package_events'::regclass
       AND c.conname = 'package_events_type_check';

    IF mevcut_def IS NULL
       OR mevcut_def NOT IN (olay_check_dar, olay_check_genis) THEN
        RAISE EXCEPTION
            'migration 036 geri alma REDDEDILDI: package_events_type_check adini KANONIK OLMAYAN bir kisit tutuyor (tanim=%)',
            coalesce(mevcut_def, '<yok>')
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Beklenen: 033 un dar kumesi ya da 036 nin genis kumesi.';
    END IF;

    -- ── KİMLİK KAPISI (F7) — `DROP` ADIN gördüğünü düşürür ──────────────────
    -- İleri dosyadaki KAPI 4'ün aynadaki eşi. `DROP FUNCTION IF EXISTS` ve
    -- `DROP TRIGGER IF EXISTS` nesneyi yalnız ADIYLA arar; aynı adı taşıyan
    -- YABANCI bir fonksiyonu düşürmek, ona bağlı başka bir tetikleyiciyi
    -- sessizce kırardı. Kabul edilen iki durum: nesne YOK, ya da tanımı
    -- BİREBİR kanonik. Üçüncü her durum fail-closed reddedilir.
    FOR kayit IN
        SELECT * FROM (VALUES
            ('social.track_brand_sub_sector_history', fn_track_ozet),
            ('social.reject_approval_snapshot_mutation', fn_snapshot_ozet),
            ('social.reject_approved_rollback_plan_mutation', fn_plan_ozet)
        ) AS t(ad, ozet)
    LOOP
        SELECT format('%s|%s|%s', l.lanname, format_type(p.prorettype, NULL),
                      CASE WHEN md5(p.prosrc) = kayit.ozet THEN 'kanonik'
                           ELSE 'YABANCI-GOVDE' END)
          INTO mevcut_def
          FROM pg_proc p
          JOIN pg_language l ON l.oid = p.prolang
         WHERE p.oid = to_regprocedure(kayit.ad || '()');

        IF mevcut_def IS NOT NULL AND mevcut_def <> 'plpgsql|trigger|kanonik' THEN
            RAISE EXCEPTION
                'migration 036 geri alma REDDEDILDI: %() adini KANONIK OLMAYAN bir fonksiyon tutuyor (%)',
                kayit.ad, mevcut_def
                USING ERRCODE = 'integrity_constraint_violation',
                      HINT = 'Ad SAHIPLIK DEGILDIR. Bu fonksiyon 036 nin '
                             'yazdigi degildir; dusurmek baskasinin nesnesini '
                             'yok etmek olurdu.';
        END IF;
    END LOOP;

    FOR kayit IN
        SELECT * FROM (VALUES
            ('social.brands', 'brands_sub_sector_history', trg_brands_kanonik),
            ('social.sector_package_runs', 'sector_package_runs_approval_snapshot_immutable', trg_kosu_kanonik),
            ('social.package_rollback_plans', 'package_rollback_plans_approved_immutable', trg_plan_kanonik)
        ) AS t(tablo, ad, tanim)
    LOOP
        CONTINUE WHEN to_regclass(kayit.tablo) IS NULL;

        SELECT format('%s|%s', pg_get_triggerdef(t.oid), t.tgenabled)
          INTO mevcut_def
          FROM pg_trigger t
         WHERE t.tgrelid = kayit.tablo::regclass
           AND t.tgname = kayit.ad
           AND NOT t.tgisinternal;

        IF mevcut_def IS NOT NULL AND mevcut_def <> kayit.tanim || '|O' THEN
            RAISE EXCEPTION
                'migration 036 geri alma REDDEDILDI: % adini KANONIK OLMAYAN bir tetikleyici tutuyor (%)',
                kayit.ad, mevcut_def
                USING ERRCODE = 'integrity_constraint_violation',
                      HINT = 'Bu tetikleyici 036 nin yazdigi degildir; '
                             'dusurmek baskasinin tablosunu sessizce '
                             'korumasiz birakirdi.';
        END IF;
    END LOOP;
END
$preflight$;

-- ---------------------------------------------------------------------------
-- 1. Tetikleyiciler + tablolar
-- ---------------------------------------------------------------------------
--
-- `brands` tetikleyicisi tablodan ÖNCE gider: geçmiş tablosu düşerken hâlâ
-- ayakta olsaydı bir sonraki marka yazımı olmayan tabloya INSERT denerdi.

DROP TRIGGER IF EXISTS brands_sub_sector_history ON social.brands;
DROP TRIGGER IF EXISTS sector_package_runs_approval_snapshot_immutable
    ON social.sector_package_runs;
DROP TRIGGER IF EXISTS package_rollback_plans_approved_immutable
    ON social.package_rollback_plans;

DROP TABLE IF EXISTS social.brand_sub_sector_history;
DROP TABLE IF EXISTS social.package_rollback_plans;
DROP TABLE IF EXISTS social.sector_package_runs;

-- ---------------------------------------------------------------------------
-- 2. K-09 kısıtı + `package_events` CHECK'inin daraltılması
-- ---------------------------------------------------------------------------
--
-- Daraltma yalnız GENİŞ hâl duruyorsa yapılır; zaten dar ise dokunulmaz
-- (ikinci koşum yolu). Kimlik doğrulaması preflight'ta yapıldı.

ALTER TABLE social.sector_research_artifacts
    DROP CONSTRAINT IF EXISTS sector_research_artifacts_run_source_kind_key;

DO $narrow_events$
DECLARE
    olay_check_genis CONSTANT TEXT :=
        'CHECK ((event_type = ANY (ARRAY[''mismatch_fallthrough''::text,'
        ' ''package_read_error''::text, ''stale_assignment_fallback''::text,'
        ' ''stamp_missing''::text, ''stamp_invalid''::text,'
        ' ''stamp_stale_at_persist''::text, ''activation''::text,'
        ' ''rollback''::text, ''deactivation''::text, ''approval''::text,'
        ' ''rejection''::text])))';
BEGIN
    IF (SELECT pg_get_constraintdef(c.oid)
          FROM pg_constraint c
         WHERE c.conrelid = 'social.package_events'::regclass
           AND c.conname = 'package_events_type_check') = olay_check_genis THEN
        EXECUTE 'ALTER TABLE social.package_events '
                'DROP CONSTRAINT package_events_type_check';
        EXECUTE 'ALTER TABLE social.package_events '
                'ADD CONSTRAINT package_events_type_check CHECK (event_type IN ('
                '''mismatch_fallthrough'', ''package_read_error'', '
                '''stale_assignment_fallback'', ''stamp_missing'', '
                '''stamp_invalid'', ''stamp_stale_at_persist'', ''activation'', '
                '''rollback'', ''deactivation''))';
    END IF;
END
$narrow_events$;

-- ---------------------------------------------------------------------------
-- 3. Fonksiyonlar
-- ---------------------------------------------------------------------------

DROP FUNCTION IF EXISTS social.track_brand_sub_sector_history();
DROP FUNCTION IF EXISTS social.reject_approval_snapshot_mutation();
DROP FUNCTION IF EXISTS social.reject_approved_rollback_plan_mutation();

-- ---------------------------------------------------------------------------
-- 4. Kalıntı doğrulaması — fail-closed
-- ---------------------------------------------------------------------------
--
-- `DROP ... IF EXISTS` bir nesneyi ADIYLA arar; ad tutmuyorsa sessizce geçer.
-- Bu blok katalogtan GERÇEK durumu okur: 036'nın açtığı hiçbir nesne ayakta
-- kalmamalı ve 033'ün CHECK'i tam metinle geri dönmüş olmalıdır.

DO $verify_down$
DECLARE
    olay_check_dar CONSTANT TEXT :=
        'CHECK ((event_type = ANY (ARRAY[''mismatch_fallthrough''::text,'
        ' ''package_read_error''::text, ''stale_assignment_fallback''::text,'
        ' ''stamp_missing''::text, ''stamp_invalid''::text,'
        ' ''stamp_stale_at_persist''::text, ''activation''::text,'
        ' ''rollback''::text, ''deactivation''::text])))';
    leftovers TEXT;
BEGIN
    SELECT string_agg(label, E'\n  - ' ORDER BY label)
      INTO leftovers
      FROM (
        SELECT 'tablo social.' || c.relname AS label
          FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
         WHERE n.nspname = 'social'
           AND c.relkind = 'r'
           AND c.relname IN ('sector_package_runs', 'package_rollback_plans',
                             'brand_sub_sector_history')
        UNION ALL
        SELECT 'tetikleyici ' || tgname
          FROM pg_trigger
         WHERE NOT tgisinternal
           AND tgname IN ('brands_sub_sector_history',
                          'sector_package_runs_approval_snapshot_immutable',
                          'package_rollback_plans_approved_immutable')
        UNION ALL
        SELECT 'fonksiyon social.' || p.proname
          FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
         WHERE n.nspname = 'social'
           AND p.proname IN ('track_brand_sub_sector_history',
                             'reject_approval_snapshot_mutation',
                             'reject_approved_rollback_plan_mutation')
        UNION ALL
        SELECT 'kisit ' || conname
          FROM pg_constraint
         WHERE conrelid = 'social.sector_research_artifacts'::regclass
           AND conname = 'sector_research_artifacts_run_source_kind_key'
        UNION ALL
        SELECT 'package_events.event_type CHECK daraltilmadi: '
               || coalesce(
                    (SELECT pg_get_constraintdef(c.oid)
                       FROM pg_constraint c
                      WHERE c.conrelid = 'social.package_events'::regclass
                        AND c.conname = 'package_events_type_check'),
                    '<yok>')
         WHERE NOT EXISTS (
            SELECT 1 FROM pg_constraint c
             WHERE c.conrelid = 'social.package_events'::regclass
               AND c.conname = 'package_events_type_check'
               AND c.contype = 'c'
               AND c.convalidated
               AND pg_get_constraintdef(c.oid) = olay_check_dar
         )
      ) AS remaining;

    IF leftovers IS NOT NULL THEN
        RAISE EXCEPTION 'migration 036 geri alma EKSIK kaldi:%',
            E'\n  - ' || leftovers
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Kalan nesneyi elle dusurup script i yeniden kosturun.';
    END IF;
END
$verify_down$;

COMMIT;

-- ---------------------------------------------------------------------------
-- 5. Çağıranın `ON_ERROR_STOP` ayarı GERİ YÜKLENİR
-- ---------------------------------------------------------------------------

\set ON_ERROR_STOP :OTOMAIX_DOWN_OES_ONCE
\unset OTOMAIX_DOWN_OES_ONCE
