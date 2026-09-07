-- Migration 036 — koşu kaydı · politika raporu · onay anlık görüntüsü · atama geçmişi
--
-- NE EKLİYOR:
--   * `social.sector_package_runs` — bir denemenin KANONİK kaydı (K-82 · K-83 ·
--     K-90 · K-92 · K-95 · K-96 · K-97 · K-98 · K-106 · F18 · F19 · K-24).
--   * `social.package_rollback_plans` (K-145) — olay başına geri alma planı;
--     kimliği BİLEŞİKtir (`incident_id`, `package_id`), `id` kolonu YOKTUR.
--   * `social.brand_sub_sector_history` (K-45) + onu YAZAN tetikleyici.
--   * `sector_research_artifacts` üstünde `UNIQUE (run_id, source, kind)` (K-09).
--   * `package_events` olay kümesi `approval` ve `rejection` ile genişler (K-99).
--
-- BAĞLAYICI INVARIANTLAR (plan Task 6 + bağlayıcı arayüz eki):
--
--   * **`run_id` deneme başına KANONİK ve BENZERSİZDİR.** Koşu satırı, artefakt,
--     klasör adı ve paket `run_id` bağı hep aynı değeri taşır. İkinci bir
--     `attempt` kimlik uzayı YOKTUR; yeniden koşum yeni `run_id` +
--     `parent_run_id` alır (teknik karar 23).
--   * **`durum` ve `sonuc` AYRI kolonlardır:** `durum` yürütmenin hâli, `sonuc`
--     motorun çıktısı. `durum != 'tamamlandi'` iken `sonuc` NULL olmak ZORUNDA.
--     `sonuc` üç değerle kapalıdır (K-90 birleştirmesi — dördüncü değer yok).
--   * **K-24:** `durum='tamamlandi'` ise `barrier_report` NULL OLAMAZ — üç
--     sonucun ÜÇÜNDE de. Kolon yalnız nullable olsaydı tamamlanmış bir koşu hiç
--     metrik yazmadan kaydedilebilirdi; mevcut testler verilen değerin
--     saklandığını kanıtlıyordu, EKSİK değerin reddedildiğini değil.
--   * **F19 — karar günlüğü kökeninden okunur.** `final_decision_log` ve
--     `decision_log_sha` BİRLİKTE dolar, BİRLİKTE boşalır; `final_candidate`
--     günlüksüz YAZILAMAZ. İki CHECK, iki ayrı kusuru kapatır: kopuk hash ve
--     günlüksüz içerik.
--   * **F18 — kapı tasdikleri KANITTIR, boolean değil.** `katman1_attestation` ·
--     `readiness_attestation` · `katman2_attestation` "hangi koşum, hangi sonuç,
--     kim, ne zaman" sorusunu kalıcı kılar. Katman-2'nin SONUCU kapı DEĞİLDİR
--     (spec §10.2: koşulması ve sunulması ön koşul); şema o yüzden onun
--     içeriğini kısıtlamaz, yalnız varlığını kaydeder.
--   * **K-98 — `approval_snapshot` DEĞİŞMEZDİR.** Tetikleyici, kolon DOLUYKEN
--     onun değiştirilmesini (ve NULL'lanmasını) reddeder; `approval_karar` ·
--     `approved_at` · `approval_seconds` güncellenebilir.
--   * **`package_id` BENZERSİZ DEĞİLDİR (tur 4 düzeltmesi).** Bir koşu satırı
--     zaten en fazla bir `package_id` taşır; `UNIQUE` "bir koşu → bir taslak"
--     değil "bir TASLAK → bir koşu" demek olurdu ve K-106'yı İMKÂNSIZ kılardı
--     (düzeltme turu yeni bir koşudur, yeni `run_id` alır, ama AYNI taslağı
--     günceller). Tekilliği kısıt değil KİLİT + DOLU KOLON sağlar (Task 15).
--   * **Düzeltme soyağacı:** `kosu_turu='duzeltme'` ⇔ `duzeltilen_run_id` dolu.
--     `parent_run_id` ile KARŞILIKLI DIŞLAMA YOKTUR (tur 5 düzeltmesi): yarıda
--     kalmış bir düzeltmenin yeniden koşumu İKİ bağı da taşımak zorundadır.
--   * **K-145 `hedefsiz`in AÇIK veri karşılığı:** `durum='hedefsiz'` ⇔
--     `target_version IS NULL`, İKİ YÖNLÜ. Hedefsizlik KALICI bir kayıttır,
--     çalışma zamanı sezgisi değil.
--   * **AÇIK-1 (kontrolör kararı 2026-08-30):** onay üçlüsü BİRLİKTE dolar
--     (`num_nonnulls ∈ {0,3}`) ve boş/yalnız-boşluk kimlik onay SAYILMAZ. Tek
--     CHECK (`(onay_actor IS NULL) = (onaylandi_at IS NULL)`) ölçüldü ki
--     `onay_actor = ''` değerini KABUL EDER; `onay_kapsam_sha` onayı onayladığı
--     satır KÜMESİNE bağlar.
--   * **AYAK (d) — ONAYLANMIŞ plan satırının kimlik/hedef alanları
--     DEĞİŞMEZDİR.** Tetikleyici, `onay_actor` DOLUYKEN `incident_id` ·
--     `package_id` · `observed_active_version` · `target_version` ·
--     `evidence_class` değişimini reddeder. AŞIRI KİLİTLEME YOKTUR: `durum` ·
--     `reason` · `onay_*` · `kanit_jetonu_*` onaydan sonra da güncellenir
--     (yeniden mühürleme dahil).
--   * **R8(c) — jeton dörtlüsü İKİ tabloda da AYNI.** Jetonun TÜRÜ kolonda
--     taşınmaz, türünü taşıdığı TABLO belirler; ikinci bir enum AÇILMAZ.
--   * **K-45 üretici ZORUNLU.** Geçmiş tablosunu hiçbir şey yazmıyorsa Task 16
--     onu maruziyet kanıtı olarak tüketemez. Tetikleyici `brands.sub_sector_id`
--     değişimini AYNI İŞLEMDE yakalar — atama yolu hangi koddan geçerse geçsin.
--     GERİ DOLDURMA YOKTUR: bilinmeyen geçmiş retroaktif "bakım tamamlandı"
--     üretmez, geçmişsiz marka bildirim almaz.
--
-- DONMUŞ SÖZLEŞMELERE DOKUNUŞ — ölçülmüş ve bilinçli:
--   032 `sector_research_artifacts` kısıt/indeks kümesini, 033 `package_events`
--   CHECK metnini TAM METİNLE pinliyor. Her ikisi de SÜRÜM-FARKINDA hâle
--   getirildi: eski beklenti (o migration TEK BAŞINA uygulandığında) geçerli
--   KALIR, 036 sonrası genişlemiş hâl de kabul edilir. Kabul EXACT-MATCH bir
--   POZİTİF SÖZLEŞMEdir, "şunu içeriyor mu" değil — adı geçmeyen fazladan
--   indeks ve tanınmayan olay türü hâlâ REDDEDİLİR.
--
-- TRANSACTION SAHİPLİĞİ: bu dosya KENDİ `BEGIN/COMMIT`ini TAŞIMAZ (035 ile aynı
-- sözleşme). Dağıtım runner'ı ve testler her migration'ı `--single-transaction`
-- ile uygular.
--
--   ATOMİKLİK SARMALAYICIYA BAĞLI DEĞİLDİR (035 fix turu 6, F3'ün taşınması):
--   `ON_ERROR_STOP` olmadan psql hatadan SONRA devam eder, yani AYRI bir
--   deyimdeki her şey kendi transaction'ında commit edilir ve düşen bir adım
--   şemayı YARIM UYGULANMIŞ bırakır. Bu yüzden KALICI olan her şey — kapılar,
--   fonksiyonlar, tablolar, indeksler, tetikleyiciler, `ALTER`ler ve garanti
--   doğrulaması — TEK `DO $apply_036$` deyiminin İÇİNDEDİR. Bir `DO` bloğu tek
--   deyimdir: autocommit altında bile ya tamamı uygulanır ya hiçbiri.
--
-- GERİ ALMA: `rollback/036_down.sql`. F20 gereği Plan 2 verisi VARKEN
-- fail-closed durur; pilot sonrası dönüş şema geri alması değil, veri-koruyan
-- ileri düzeltme migration'ıdır.

DO $apply_036$
DECLARE
    -- Kanonik tanımlar TEK YERDE: hem kapı hem garanti doğrulaması buradan okur,
    -- yani ıraksayamazlar (035'in `canonical` deseni).
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

    -- TETİKLEYİCİ TANIMLARI `pg_get_triggerdef`in ÜRETTİĞİ BİÇİMDEDİR ve
    -- ÖLÇÜLEREK pinlenmiştir (tahmin değil). Tek metin ÜÇ işi birden görür:
    -- (1) KAPI 4 kimlik karşılaştırması, (2) tetikleyicinin YARATILMASI
    -- (`EXECUTE <sabit>` — `pg_get_triggerdef` çıktısı geçerli DDL'dir),
    -- (3) kapalı manifestin beklentisi. İkinci bir kopya YOKTUR, dolayısıyla
    -- ıraksama da yoktur; biçim sürümle değişirse manifest AYNI koşumda
    -- gürültüyle düşer.
    trg_brands_kanonik CONSTANT TEXT :=
        'CREATE TRIGGER brands_sub_sector_history AFTER INSERT OR UPDATE ON social.brands FOR EACH ROW EXECUTE FUNCTION social.track_brand_sub_sector_history()';
    trg_kosu_kanonik CONSTANT TEXT :=
        'CREATE TRIGGER sector_package_runs_approval_snapshot_immutable BEFORE UPDATE ON social.sector_package_runs FOR EACH ROW EXECUTE FUNCTION social.reject_approval_snapshot_mutation()';
    trg_plan_kanonik CONSTANT TEXT :=
        'CREATE TRIGGER package_rollback_plans_approved_immutable BEFORE UPDATE ON social.package_rollback_plans FOR EACH ROW EXECUTE FUNCTION social.reject_approved_rollback_plan_mutation()';

    -- FONKSİYON GÖVDELERİ BURADA — çünkü kimlik kapısı kalıcı DDL'den ÖNCE
    -- koşmak ZORUNDA ve aynı metni okumalı. `prosrc` bu sabitin BİREBİR
    -- kendisidir (`%L` ile yazılır), yani karşılaştırma bayt-bayttır.
    fn_track_govde CONSTANT TEXT := $track_history$
        DECLARE
            yeni UUID;
            eski UUID;
        BEGIN
            IF NOT (to_jsonb(NEW) ? 'sub_sector_id') THEN
                RAISE EXCEPTION
                    'K-45 uretici KIRIK: social.brands.sub_sector_id kolonu YOK '
                    '(dusurulmus ya da yeniden adlandirilmis). Atama gecmisi '
                    'yazilamaz; sessizce devam etmek maruziyet kanitini bos '
                    'birakirdi.'
                    USING ERRCODE = 'integrity_constraint_violation',
                          HINT = 'Kolonu eski adiyla geri getirin ya da '
                                 'rollback/036_down.sql ile ureticiyi kaldirin. '
                                 'Kolon adi degistiyse bu fonksiyon da '
                                 'guncellenmelidir.';
            END IF;

            yeni := NEW.sub_sector_id;
            IF TG_OP = 'UPDATE' THEN
                eski := OLD.sub_sector_id;
            END IF;

            -- Değişmeyen atama yeni aralık ÜRETMEZ: maruziyet kanıtı, her
            -- marka güncellemesinde tekrarlanan bir gürültü olamaz.
            IF yeni IS NOT DISTINCT FROM eski THEN
                RETURN NULL;
            END IF;

            UPDATE social.brand_sub_sector_history
               SET unassigned_at = now()
             WHERE brand_id = NEW.id AND unassigned_at IS NULL;

            IF yeni IS NOT NULL THEN
                INSERT INTO social.brand_sub_sector_history (brand_id, sub_sector_id)
                VALUES (NEW.id, yeni);
            END IF;

            RETURN NULL;
        END
        $track_history$;
    fn_snapshot_govde CONSTANT TEXT := $reject_snapshot$
        BEGIN
            IF OLD.approval_snapshot IS NOT NULL
               AND NEW.approval_snapshot IS DISTINCT FROM OLD.approval_snapshot THEN
                RAISE EXCEPTION
                    'approval_snapshot DEGISMEZDIR (K-98): dolu bir anlik goruntu '
                    'degistirilemez ve silinemez (run_id=%)', OLD.run_id
                    USING ERRCODE = 'integrity_constraint_violation',
                          HINT = 'approval_karar / approved_at / approval_seconds '
                                 'guncellenebilir; anlik goruntunun kendisi hayir.';
            END IF;
            RETURN NEW;
        END
        $reject_snapshot$;
    fn_plan_govde CONSTANT TEXT := $reject_rollback_plan$
        BEGIN
            -- MÜHÜR SİLİNEMEZ. Kilit aşağıda `OLD.onay_actor IS NOT NULL`
            -- yüklemine dayanır; onay üçlüsü birlikte NULL yapılabilseydi
            -- değişmezlik İKİ ADIMDA atlatılırdı (temizle → hedefi değiştir →
            -- yeniden mühürle) ve `num_nonnulls ∈ {0,3}` CHECK'i buna izin
            -- verirdi. Ölçüldü 2026-09-07: zincir target_version'i 3'ten 99'a
            -- taşıyordu. Yeniden mühürleme (dolu → dolu) BİLEREK açık kalır;
            -- kapanan yalnız dolu → BOŞ geçişidir.
            IF OLD.onay_actor IS NOT NULL AND NEW.onay_actor IS NULL THEN
                RAISE EXCEPTION
                    'onaylanmış geri alma planının onay mührü SİLİNEMEZ'
                    USING ERRCODE = 'integrity_constraint_violation',
                          HINT = 'Muhru silmek, kimlik/hedef kilidini bir '
                                 'sonraki UPDATE icin kaldirirdi. Kapsam '
                                 'degistiyse YENIDEN MUHURLEYIN (onay_* ucusu '
                                 'dolu kalir); hedef degisecekse yeni bir plan '
                                 'satiri yazin.';
            END IF;

            IF OLD.onay_actor IS NOT NULL AND (
                   NEW.incident_id             IS DISTINCT FROM OLD.incident_id
                OR NEW.package_id              IS DISTINCT FROM OLD.package_id
                OR NEW.observed_active_version IS DISTINCT FROM OLD.observed_active_version
                OR NEW.target_version          IS DISTINCT FROM OLD.target_version
                OR NEW.evidence_class          IS DISTINCT FROM OLD.evidence_class
            ) THEN
                RAISE EXCEPTION
                    'onaylanmış geri alma planı satırının kimlik/hedef alanları değiştirilemez'
                    USING ERRCODE = 'integrity_constraint_violation',
                          HINT = 'durum / reason / onay_* / kanit_jetonu_* '
                                 'guncellenebilir (yeniden muhurleme dahil); '
                                 'onayin TANIMLADIGI kimlik/hedef alanlari '
                                 'hayir. Hedef degisecekse once yeni bir plan '
                                 'satiri yazin.';
            END IF;
            RETURN NEW;
        END
        $reject_rollback_plan$;

    kayit RECORD;

    bagimli TEXT;
    mevcut_def TEXT;
    mevcut_tur "char";
    mevcut_valid BOOLEAN;
    problems TEXT;
BEGIN
    -- ── KAPI 1 — ÖNKOŞUL İLİŞKİLER ──────────────────────────────────────────
    -- 036 üç ilişkiye yaslanır (`sectors` · `sector_packages` · `brands`) ve
    -- ikisinin sözleşmesini genişletir (`sector_research_artifacts` ·
    -- `package_events`). Biri yoksa yabancı anahtar ya da `ALTER` sessizce
    -- BAŞKA bir hata üretirdi; girişte adıyla DURur.
    SELECT string_agg(ad, ', ' ORDER BY ad) INTO bagimli
      FROM unnest(ARRAY['social.sectors', 'social.sector_packages',
                        'social.brands', 'social.sector_research_artifacts',
                        'social.package_events']) AS t(ad)
     WHERE to_regclass(ad) IS NULL;

    IF bagimli IS NOT NULL THEN
        RAISE EXCEPTION
            'migration 036: onkosul iliskiler EKSIK (%)', bagimli
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = '036, 032 ve 033 uygulanmis bir sema uzerinde kosar. '
                         'Migration lari numara sirasinda uygulayin.';
    END IF;

    -- ── KAPI 2 — OLAY CHECK'İNİN KİMLİĞİ ADdan DEĞİL TANIMdan ────────────────
    -- `DROP CONSTRAINT` nesneyi yalnız ADIYLA arar. Aynı adı taşıyan İLGİSİZ
    -- (ya da elle gevşetilmiş) bir kısıt sessizce düşürülüp yerine bizimki
    -- konsaydı, 033'ün kapalı-küme vaadi bu migration'ın eliyle kaybolurdu.
    -- Kabul edilen İKİ tanım vardır: 036 öncesi dar küme ve 036 sonrası geniş
    -- küme (ikinci koşum). Üçüncü bir metin fail-closed reddedilir.
    SELECT pg_get_constraintdef(c.oid), c.contype, c.convalidated
      INTO mevcut_def, mevcut_tur, mevcut_valid
      FROM pg_constraint c
     WHERE c.conrelid = 'social.package_events'::regclass
       AND c.conname = 'package_events_type_check';

    IF mevcut_def IS NULL
       OR mevcut_tur <> 'c'
       OR NOT mevcut_valid
       OR mevcut_def NOT IN (olay_check_dar, olay_check_genis) THEN
        RAISE EXCEPTION
            'migration 036: package_events_type_check adini KANONIK OLMAYAN bir kisit tutuyor (contype=%, convalidated=%, tanim=%)',
            coalesce(mevcut_tur::text, '<yok>'),
            coalesce(mevcut_valid::text, '<yok>'),
            coalesce(mevcut_def, '<yok>')
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Beklenen: 033 un dar kumesi ya da 036 nin genis kumesi. '
                         'Baska bir metni genisletmek kapali-kume vaadini yok '
                         'ederdi; kisiti elle cozup migration i yeniden kosturun.';
    END IF;

    -- ── KAPI 3 — K-09 KISIT KİMLİĞİ ─────────────────────────────────────────
    -- `ADD CONSTRAINT`in `IF NOT EXISTS` biçimi YOKTUR; varlık katalogdan
    -- okunur. Ad DOLU ama tanım BAŞKAysa ekleme `duplicate_object` ile düşer;
    -- burada anlaşılır bir mesajla DURulur.
    SELECT pg_get_constraintdef(c.oid), c.contype, c.convalidated
      INTO mevcut_def, mevcut_tur, mevcut_valid
      FROM pg_constraint c
     WHERE c.conrelid = 'social.sector_research_artifacts'::regclass
       AND c.conname = 'sector_research_artifacts_run_source_kind_key';

    IF mevcut_def IS NOT NULL
       AND (mevcut_tur <> 'u' OR NOT mevcut_valid OR mevcut_def <> k09_kanonik) THEN
        RAISE EXCEPTION
            'migration 036: sector_research_artifacts_run_source_kind_key adini KANONIK OLMAYAN bir kisit tutuyor (contype=%, convalidated=%, tanim=%)',
            mevcut_tur, mevcut_valid, mevcut_def
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Beklenen tanim: UNIQUE (run_id, source, kind).';
    END IF;

    -- ── KAPI 4 — FONKSİYON VE TETİKLEYİCİ KİMLİĞİ ADdan DEĞİL TANIMdan ─────
    -- `CREATE OR REPLACE FUNCTION` ve `DROP TRIGGER IF EXISTS` nesneyi yalnız
    -- ADIYLA arar. Aynı adı taşıyan YABANCI bir fonksiyon sessizce EZİLİRDİ ve
    -- ona bağlı BAŞKA bir tetikleyici, fonksiyon kimliği (oid) korunduğu için
    -- ANINDA bizim gövdemizi çalıştırmaya başlardı. Kapalı manifest bunu
    -- YAKALAYAMAZ: manifest ezme İŞLEMİNDEN SONRAKİ (kanonik görünen) durumu
    -- okur. KAPI 2/KAPI 3 bu disiplini kısıtlar için zaten uyguluyordu;
    -- fonksiyon/tetikleyici sınıfı dışarıda kalmıştı.
    --
    -- KABUL EDİLEN İKİ DURUM: nesne YOK, ya da tanımı BİREBİR kanonik (ikinci
    -- koşum). Üçüncü her durum fail-closed reddedilir.
    --
    -- KAPSAM SINIRI (ölçülmüş, iddia edilmeyen): kapı SIFIR argümanlı adı
    -- denetler (`to_regprocedure('<ad>()')`). Aynı adı taşıyan FARKLI imzalı
    -- bir aşırı yükleme bizim yazdığımızı EZMEZ — `CREATE OR REPLACE` onu
    -- görmez bile — dolayısıyla kapının konusu değildir.
    FOR kayit IN
        SELECT * FROM (VALUES
            ('social.track_brand_sub_sector_history', fn_track_govde),
            ('social.reject_approval_snapshot_mutation', fn_snapshot_govde),
            ('social.reject_approved_rollback_plan_mutation', fn_plan_govde)
        ) AS t(ad, govde)
    LOOP
        SELECT format('%s|%s|%s', l.lanname, format_type(p.prorettype, NULL),
                      CASE WHEN p.prosrc = kayit.govde THEN 'kanonik'
                           ELSE 'YABANCI-GOVDE' END)
          INTO mevcut_def
          FROM pg_proc p
          JOIN pg_language l ON l.oid = p.prolang
         WHERE p.oid = to_regprocedure(kayit.ad || '()');

        IF mevcut_def IS NOT NULL AND mevcut_def <> 'plpgsql|trigger|kanonik' THEN
            RAISE EXCEPTION
                'migration 036: %() adini KANONIK OLMAYAN bir fonksiyon tutuyor (%)',
                kayit.ad, mevcut_def
                USING ERRCODE = 'integrity_constraint_violation',
                      HINT = 'Ad SAHIPLIK DEGILDIR: bu fonksiyonu ezmek, ona '
                             'bagli baska bir tetikleyiciyi sessizce bizim '
                             'govdemize baglardi. Yabanci nesneyi elle cozup '
                             'migration i yeniden kosturun.';
        END IF;
    END LOOP;

    FOR kayit IN
        SELECT * FROM (VALUES
            ('social.brands', 'brands_sub_sector_history', trg_brands_kanonik),
            ('social.sector_package_runs', 'sector_package_runs_approval_snapshot_immutable', trg_kosu_kanonik),
            ('social.package_rollback_plans', 'package_rollback_plans_approved_immutable', trg_plan_kanonik)
        ) AS t(tablo, ad, tanim)
    LOOP
        -- Tablo HENÜZ YOKSA (ilk kurulum) o adda bir tetikleyici de olamaz.
        CONTINUE WHEN to_regclass(kayit.tablo) IS NULL;

        SELECT format('%s|%s', pg_get_triggerdef(t.oid), t.tgenabled)
          INTO mevcut_def
          FROM pg_trigger t
         WHERE t.tgrelid = kayit.tablo::regclass
           AND t.tgname = kayit.ad
           AND NOT t.tgisinternal;

        IF mevcut_def IS NOT NULL AND mevcut_def <> kayit.tanim || '|O' THEN
            RAISE EXCEPTION
                'migration 036: % adini KANONIK OLMAYAN bir tetikleyici tutuyor (%)',
                kayit.ad, mevcut_def
                USING ERRCODE = 'integrity_constraint_violation',
                      HINT = 'DROP TRIGGER IF EXISTS adiyla arar; baskasinin '
                             'tetikleyicisini dusurmek onun tablosunu sessizce '
                             'korumasiz birakirdi.';
        END IF;
    END LOOP;

    -- ═══ BURADAN SONRASI KALICI — ve hepsi BU deyimin içinde ════════════════

    -- ── 1. Koşu kaydı ───────────────────────────────────────────────────────
    EXECUTE $ddl$
        CREATE TABLE IF NOT EXISTS social.sector_package_runs (
            id                       UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            run_id                   TEXT        NOT NULL,
            parent_run_id            TEXT,
            sector_id                UUID        NOT NULL,
            durum                    TEXT        NOT NULL,
            sonuc                    TEXT,
            sebep                    TEXT,
            engine_version           TEXT,
            engine_config_sha        TEXT,
            policy_report            JSONB,
            barrier_report           JSONB,
            final_candidate          JSONB,
            final_decision_log       JSONB,
            decision_log_sha         TEXT,
            engine_diff              JSONB,
            content_sha              TEXT,
            approval_snapshot        JSONB,
            approval_karar           TEXT,
            approved_at              TIMESTAMPTZ,
            approval_seconds         INT,
            katman1_attestation      JSONB,
            readiness_attestation    JSONB,
            katman2_attestation      JSONB,
            snapshot_sha             TEXT,
            package_id               UUID,
            duzeltilen_run_id        UUID,
            kosu_turu                TEXT        NOT NULL,
            kanit_jetonu             TEXT,
            kanit_jetonu_parmakizi   TEXT,
            kanit_jetonu_basildi_at  TIMESTAMPTZ,
            kanit_jetonu_harcandi_at TIMESTAMPTZ,
            created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),

            CONSTRAINT sector_package_runs_run_id_key UNIQUE (run_id),
            CONSTRAINT sector_package_runs_sector_id_fkey
                FOREIGN KEY (sector_id) REFERENCES social.sectors(id),
            -- BENZERSİZ DEĞİL (tur 4): bkz. başlık.
            CONSTRAINT sector_package_runs_package_id_fkey
                FOREIGN KEY (package_id) REFERENCES social.sector_packages(id),

            CONSTRAINT sector_package_runs_durum_check
                CHECK (durum IN ('calisiyor', 'tamamlandi', 'tamamlanmadi')),
            CONSTRAINT sector_package_runs_sonuc_check
                CHECK (sonuc IS NULL
                       OR sonuc IN ('activation_eligible', 'no_change', 'blocked')),
            CONSTRAINT sector_package_runs_sonuc_yalniz_tamamlandi
                CHECK (sonuc IS NULL OR durum = 'tamamlandi'),
            CONSTRAINT sector_package_runs_barrier_report_zorunlu
                CHECK (durum <> 'tamamlandi' OR barrier_report IS NOT NULL),
            CONSTRAINT sector_package_runs_approval_karar_check
                CHECK (approval_karar IS NULL OR approval_karar IN ('onay', 'ret')),
            CONSTRAINT sector_package_runs_kosu_turu_check
                CHECK (kosu_turu IN ('ilk', 'periyodik', 'duzeltme')),
            CONSTRAINT sector_package_runs_duzeltme_soyagaci
                CHECK ((kosu_turu = 'duzeltme') = (duzeltilen_run_id IS NOT NULL)),
            CONSTRAINT sector_package_runs_karar_gunlugu_cifti
                CHECK ((final_decision_log IS NULL) = (decision_log_sha IS NULL)),
            CONSTRAINT sector_package_runs_icerik_gunluksuz_yazilmaz
                CHECK (final_candidate IS NULL OR final_decision_log IS NOT NULL),
            CONSTRAINT sector_package_runs_kanit_jetonu_butun
                CHECK (kanit_jetonu IS NULL
                       OR (kanit_jetonu_parmakizi IS NOT NULL
                           AND kanit_jetonu_basildi_at IS NOT NULL))
        )
    $ddl$;

    EXECUTE $ddl$
        CREATE INDEX IF NOT EXISTS idx_sector_package_runs_sector_created
            ON social.sector_package_runs (sector_id, created_at DESC)
    $ddl$;

    -- ── 2. Geri alma planları (K-145) ───────────────────────────────────────
    -- `id` kolonu YOKTUR: kimlik bileşiktir. İkinci bir vekil anahtar, aynı
    -- olay+paket için iki satır yazılabilmesi demek olurdu ve tekrar
    -- güvenliğinin VERİ karşılığı kaybolurdu.
    EXECUTE $ddl$
        CREATE TABLE IF NOT EXISTS social.package_rollback_plans (
            incident_id              TEXT        NOT NULL,
            package_id               UUID        NOT NULL,
            observed_active_version  INT         NOT NULL,
            target_version           INT,
            evidence_class           TEXT        NOT NULL,
            reason                   TEXT        NOT NULL,
            durum                    TEXT        NOT NULL,
            onay_actor               TEXT,
            onaylandi_at             TIMESTAMPTZ,
            onay_kapsam_sha          TEXT,
            kanit_jetonu             TEXT,
            kanit_jetonu_parmakizi   TEXT,
            kanit_jetonu_basildi_at  TIMESTAMPTZ,
            kanit_jetonu_harcandi_at TIMESTAMPTZ,
            created_at               TIMESTAMPTZ NOT NULL DEFAULT now(),

            CONSTRAINT package_rollback_plans_incident_id_package_id_key
                UNIQUE (incident_id, package_id),
            CONSTRAINT package_rollback_plans_durum_check
                CHECK (durum IN ('bekliyor', 'tamamlandi', 'hata', 'hedefsiz')),
            CONSTRAINT package_rollback_plans_hedefsiz_butun
                CHECK ((durum = 'hedefsiz') = (target_version IS NULL)),
            CONSTRAINT package_rollback_plans_onay_butun
                CHECK (num_nonnulls(onay_actor, onaylandi_at, onay_kapsam_sha)
                       IN (0, 3)),
            CONSTRAINT package_rollback_plans_onay_actor_dolu
                CHECK (onay_actor IS NULL OR btrim(onay_actor) <> ''),
            CONSTRAINT package_rollback_plans_kanit_jetonu_butun
                CHECK (kanit_jetonu IS NULL
                       OR (kanit_jetonu_parmakizi IS NOT NULL
                           AND kanit_jetonu_basildi_at IS NOT NULL))
        )
    $ddl$;

    -- ── 3. Atama geçmişi + ÜRETİCİSİ (K-45) ────────────────────────────────
    -- `sub_sector_id` üstünde yabancı anahtar YOKTUR ve bu bilinçlidir
    -- (`package_events.sector_id` ile aynı gerekçe): maruziyet kanıtı, işaret
    -- ettiği satır silinse bile AYAKTA kalmalıdır. `brand_id` ise FK +
    -- CASCADE'dir — F18 marka silme sözleşmesi korunur.
    EXECUTE $ddl$
        CREATE TABLE IF NOT EXISTS social.brand_sub_sector_history (
            id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            brand_id      UUID        NOT NULL,
            sub_sector_id UUID        NOT NULL,
            assigned_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
            unassigned_at TIMESTAMPTZ,

            CONSTRAINT brand_sub_sector_history_brand_id_fkey
                FOREIGN KEY (brand_id) REFERENCES social.brands(id) ON DELETE CASCADE,
            CONSTRAINT brand_sub_sector_history_aralik_check
                CHECK (unassigned_at IS NULL OR unassigned_at >= assigned_at)
        )
    $ddl$;

    -- Marka başına EN FAZLA BİR açık aralık — kısmi benzersiz indeks. Kapanış
    -- SAYARAK değil YAPIYLA: "iki açık aralık" hücresi doğamaz, tetikleyicinin
    -- doğru davrandığını ayrıca saymak gerekmez.
    EXECUTE $ddl$
        CREATE UNIQUE INDEX IF NOT EXISTS uq_brand_sub_sector_history_acik
            ON social.brand_sub_sector_history (brand_id)
         WHERE unassigned_at IS NULL
    $ddl$;

    EXECUTE $ddl$
        CREATE INDEX IF NOT EXISTS idx_brand_sub_sector_history_brand
            ON social.brand_sub_sector_history (brand_id, assigned_at DESC)
    $ddl$;

    -- ÜRETİCİ SESSİZCE DURAMAZ — ve buradaki gerekçe bir DÜZELTMEDİR (fix turu
    -- 1, I1). Önceki yazım kolonu `to_jsonb(NEW) ->> 'sub_sector_id'` ile
    -- okuyor ve bunu "doğrudan alan erişimi kolona KATALOG BAĞIMLILIĞI kurar,
    -- o bağımlılık `032_down.sql`in `DROP COLUMN` adımını kırardı" diye
    -- gerekçelendiriyordu. O cümle `ÖLÇÜLDÜ` etiketi taşıyordu ama
    -- ÇALIŞTIRILMAMIŞTI ve YANLIŞTI. Bugün ölçüldü (PG 18.3, üç kollu prob):
    --   * gövdede `NEW.sub_sector_id` + tetikleyicide kolon listesi YOK
    --     → `ALTER TABLE ... DROP COLUMN` **rc=0**. plpgsql gövdesi GEÇ BAĞLANIR;
    --       katalog bağımlılığı YARATMAZ.
    --   * tetikleyici `AFTER UPDATE OF sub_sector_id` (KOLON LİSTESİ)
    --     → `rc=1`, `cannot drop column ... depends on column`.
    -- Yani iddianın yalnız İKİNCİ yarısı doğrudur: bağımlılığı kolon listesi
    -- kurar, gövde kurmaz. Bu 036'nın tetikleyicisinde zaten kolon listesi
    -- olmadığı için kısıtlayıcı değildir (ölçüm:
    -- `test_column_dependency_is_created_only_by_a_trigger_column_list`).
    --
    -- YANLIŞ ÖNCÜLÜN BEDELİ FAIL-OPEN'DI, ölçüldü: `->>` kolon YOKSA ya da
    -- YENİDEN ADLANDIRILMIŞSA `NULL` döner, `yeni IS NOT DISTINCT FROM eski`
    -- doğru olur, tetikleyici `RETURN NULL` ile çıkar ve K-45 üreticisi
    -- SESSİZCE yazmayı bırakır — marka yazımları `rc=0` ile geçmeye devam eder.
    -- Ölçüm (taze scratch, tüm migration'lar): kolon `sub_sector_id_v2`ye
    -- yeniden adlandırıldı → INSERT `rc=0`, geçmiş satırı 1'de KALDI. Aynısı
    -- kolon düşürüldüğünde. Sessizlik, K-45'in var olma sebebinin KARŞITIDIR
    -- (plan: "geçmiş tablosunu hiçbir şey yazmıyorsa Task 16 onu maruziyet
    -- kanıtı olarak tüketemez").
    --
    -- BUGÜNKÜ YAPI: önce YAPISAL KAPI (`to_jsonb(NEW) ? 'sub_sector_id'` —
    -- kolonun VARLIĞINI sorar, DEĞERİNİ değil), sonra DOĞRUDAN alan okuması.
    -- Kapı `?` ile kurulur çünkü doğrudan erişimin kendi hatası
    -- (`record "new" has no field ...`) gürültülüdür ama K-45'ten hiç söz
    -- etmez; kapı, operatöre neyin kırıldığını söyler. Doğrudan okuma ayrıca
    -- metin→uuid dönüşümünü ortadan kaldırır ve kapı atlansa bile ikinci bir
    -- gürültülü savunma bırakır. Kapı katalog bağımlılığı KURMAZ (ölçüldü:
    -- kapı yerindeyken `DROP COLUMN` hâlâ `rc=0`).
    -- GÖVDE, KANONİK SABİTTEN GELİR (KAPI 4 ile TEK KAYNAK): kapı da
    -- yazım da aynı metni kullanır, ıraksayamazlar.
    EXECUTE format(
        'CREATE OR REPLACE FUNCTION %s() RETURNS trigger AS %L LANGUAGE plpgsql',
        'social.track_brand_sub_sector_history', fn_track_govde);

    EXECUTE 'DROP TRIGGER IF EXISTS brands_sub_sector_history ON social.brands';
    EXECUTE trg_brands_kanonik;

    -- ── 4. K-98 — onay anlık görüntüsü DEĞİŞMEZ ─────────────────────────────
    -- `IS DISTINCT FROM` ZORUNLUDUR, `<>` DEĞİL: kolonu NULL'a çekmek de bir
    -- DEĞİŞTİRMEdir ve `<>` onu yakalamazdı (NULL karşılaştırması NULL'dır).
    -- Kanıtı silmek, kanıtı değiştirmekten daha zararsız değildir.
    -- GÖVDE, KANONİK SABİTTEN GELİR (KAPI 4 ile TEK KAYNAK): kapı da
    -- yazım da aynı metni kullanır, ıraksayamazlar.
    EXECUTE format(
        'CREATE OR REPLACE FUNCTION %s() RETURNS trigger AS %L LANGUAGE plpgsql',
        'social.reject_approval_snapshot_mutation', fn_snapshot_govde);

    EXECUTE 'DROP TRIGGER IF EXISTS sector_package_runs_approval_snapshot_immutable '
            'ON social.sector_package_runs';
    EXECUTE trg_kosu_kanonik;

    -- ── 4b. AYAK (d) — ONAYLANMIŞ geri alma planı satırı DEĞİŞMEZ ───────────
    -- Onay, onayladığı satır KÜMESİNE mühürlenir (`onay_kapsam_sha`). Mühür
    -- basıldıktan sonra satırın kimlik/hedef alanları değişirse "yönetici bunu
    -- onayladı" iddiası sessizce BAŞKA bir işe taşınırdı — R11'in yasakladığı
    -- uydurulmuş boolean'ın veri katmanından gelen hâli. Servis yolu üyeliği
    -- zaten kapatıyor (`amend_rollback_plan` penceresi); bu tetikleyici servis
    -- DIŞI yazımın (elle SQL, gelecekteki ikinci çağıran) son savunmasıdır.
    --
    -- AŞIRI KİLİTLEME YOK (ekin bağlayıcı sınırı): `durum` · `reason` ·
    -- `onay_*` · `kanit_jetonu_*` onaydan SONRA da güncellenebilir — yürütücü
    -- onları yazar. Üyelik değiştiğinde YENİDEN MÜHÜRLEME (`onay_actor` ·
    -- `onaylandi_at` · `onay_kapsam_sha` üçünün YENİDEN yazılması) MEŞRUDUR ve
    -- burası onu engellemez; engelleseydi kapsamı değişen bir olay bir daha
    -- asla onaylanamaz, acil geri alma kolu ölürdü. Kilitlenen yalnız NEYİN
    -- onaylandığını tanımlayan alanlardır — kümesi aşağıdaki koşulda YAZILIDIR
    -- ve bağlayıcı ekten türetilen kapıyla karşılaştırılır (sayı burada
    -- tekrarlanmaz: tekrarlanan sayı bayatlar).
    --
    -- `IS DISTINCT FROM` ZORUNLUDUR, `<>` DEĞİL: `target_version` `hedefsiz`
    -- durumda NULL'dır ve `<>` NULL karşılaştırmasını yakalamazdı — hedefi
    -- NULL'a çekmek de bir DEĞİŞTİRMEdir.
    -- GÖVDE, KANONİK SABİTTEN GELİR (KAPI 4 ile TEK KAYNAK): kapı da
    -- yazım da aynı metni kullanır, ıraksayamazlar.
    EXECUTE format(
        'CREATE OR REPLACE FUNCTION %s() RETURNS trigger AS %L LANGUAGE plpgsql',
        'social.reject_approved_rollback_plan_mutation', fn_plan_govde);

    EXECUTE 'DROP TRIGGER IF EXISTS package_rollback_plans_approved_immutable '
            'ON social.package_rollback_plans';
    EXECUTE trg_plan_kanonik;

    -- ── 5. K-09 — artefakt benzersizliği ────────────────────────────────────
    -- Ad SÖZLEŞMEYLE SABİTTİR (katalogdan tahmin edilmez): 032 manifestinin
    -- muafiyeti tam da bu ada yazılıdır.
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint c
         WHERE c.conrelid = 'social.sector_research_artifacts'::regclass
           AND c.conname = 'sector_research_artifacts_run_source_kind_key'
    ) THEN
        EXECUTE 'ALTER TABLE social.sector_research_artifacts '
                'ADD CONSTRAINT sector_research_artifacts_run_source_kind_key '
                'UNIQUE (run_id, source, kind)';
    END IF;

    -- ── 6. K-99 — olay kümesi genişler ──────────────────────────────────────
    -- Yalnız DB CHECK'ini genişletmek onay/ret olayını YAZILABİLİR YAPMAZ:
    -- `app/services/package_events.py` bilinmeyen türü SQL'e VARMADAN reddeder.
    -- Python üreticisi aynı görevde `APPROVAL_EVENTS` ile genişletildi; iki
    -- kapının tek küme olduğu `test_db_check_and_python_gate_agree` ile ölçülür.
    IF (SELECT pg_get_constraintdef(c.oid)
          FROM pg_constraint c
         WHERE c.conrelid = 'social.package_events'::regclass
           AND c.conname = 'package_events_type_check') = olay_check_dar THEN
        EXECUTE 'ALTER TABLE social.package_events '
                'DROP CONSTRAINT package_events_type_check';
        EXECUTE 'ALTER TABLE social.package_events '
                'ADD CONSTRAINT package_events_type_check CHECK (event_type IN ('
                '''mismatch_fallthrough'', ''package_read_error'', '
                '''stale_assignment_fallback'', ''stamp_missing'', '
                '''stamp_invalid'', ''stamp_stale_at_persist'', ''activation'', '
                '''rollback'', ''deactivation'', ''approval'', ''rejection''))';
    END IF;

    -- ── 7. Belgeleme ────────────────────────────────────────────────────────
    EXECUTE $ddl$
        COMMENT ON TABLE social.sector_package_runs IS
            'Sektor bilgi paketi KOSU kaydi (plan Task 6). run_id deneme basina KANONIK ve BENZERSIZ; yeniden kosum yeni run_id + parent_run_id alir. durum yurutmenin hali, sonuc motorun ciktisi — AYRI kolonlar. package_id BENZERSIZ DEGIL (K-106 duzeltme turu ayni taslagi hedefler).'
    $ddl$;
    EXECUTE $ddl$
        COMMENT ON COLUMN social.sector_package_runs.barrier_report IS
            'K-24 — motorun ham degisim sayi/oranlari. durum=tamamlandi iken NULL OLAMAZ (sonucun ucunde de).'
    $ddl$;
    EXECUTE $ddl$
        COMMENT ON COLUMN social.sector_package_runs.approval_snapshot IS
            'K-98 — DEGISMEZ. Dolu iken degistirilemez ve silinemez (tetikleyici). Onay karari/zamani/suresi ayri kolonlardadir ve guncellenebilir.'
    $ddl$;
    EXECUTE $ddl$
        COMMENT ON COLUMN social.sector_package_runs.katman2_attestation IS
            'F18 — KOSULDU + SUNULDU kanitidir; sonucu KAPI DEGILDIR (spec 10.2).'
    $ddl$;
    EXECUTE $ddl$
        COMMENT ON TABLE social.package_rollback_plans IS
            'K-145 — olay basina geri alma plani. Kimlik BILESIK: (incident_id, package_id); id kolonu YOKTUR. hedefsiz durumu ile target_version IS NULL IKI YONLU esdegerdir; hedefsizlik KALICI kayittir.'
    $ddl$;
    EXECUTE $ddl$
        COMMENT ON TABLE social.brand_sub_sector_history IS
            'K-45 maruziyet kanidi. Satirlari brands_sub_sector_history TETIKLEYICISI yazar — atama yolu hangi koddan gecerse gecsin. GERI DOLDURMA YOKTUR: gecmissiz marka bildirim almaz.'
    $ddl$;

    -- ── 8. GARANTİ DOĞRULAMASI — fail-closed ────────────────────────────────
    --
    -- `CREATE ... IF NOT EXISTS` yalnız o ADDA bir nesne var mı diye bakar,
    -- TANIMINI doğrulamaz: aynı adda yanlış tanımlı bir tablo önceden duruyorsa
    -- DDL sessizce atlanır ve migration BAŞARIYLA biter. 032/033 bu modu zaten
    -- tehlikeli sayıp katalogdan doğruluyor; 036 aynı sınıftadır.
    --
    -- Kısıt · tetikleyici · indeks kümeleri TAM eşleşmedir (KAPALI MANİFEST):
    -- eksik olan da FAZLA olan da bulgudur. `NOT NULL` kısıtları (contype='n')
    -- DIŞARIDA — PG17+ onları satır olarak gösterir, PG16 göstermez;
    -- null'lanabilirlik zaten kolon imzasında denetleniyor.
    WITH expected(label, want) AS (
        VALUES
            ('sector_package_runs tablo imzası',
             'relkind=r relpersistence=p partition=f rls=f force_rls=f'),
            ('sector_package_runs kolon imzası',
             'id:uuid:nn:gen_random_uuid() && run_id:text:nn:- && parent_run_id:text:null:- && sector_id:uuid:nn:- && durum:text:nn:- && sonuc:text:null:- && sebep:text:null:- && engine_version:text:null:- && engine_config_sha:text:null:- && policy_report:jsonb:null:- && barrier_report:jsonb:null:- && final_candidate:jsonb:null:- && final_decision_log:jsonb:null:- && decision_log_sha:text:null:- && engine_diff:jsonb:null:- && content_sha:text:null:- && approval_snapshot:jsonb:null:- && approval_karar:text:null:- && approved_at:timestamp with time zone:null:- && approval_seconds:integer:null:- && katman1_attestation:jsonb:null:- && readiness_attestation:jsonb:null:- && katman2_attestation:jsonb:null:- && snapshot_sha:text:null:- && package_id:uuid:null:- && duzeltilen_run_id:uuid:null:- && kosu_turu:text:nn:- && kanit_jetonu:text:null:- && kanit_jetonu_parmakizi:text:null:- && kanit_jetonu_basildi_at:timestamp with time zone:null:- && kanit_jetonu_harcandi_at:timestamp with time zone:null:- && created_at:timestamp with time zone:nn:now()'),
            ('sector_package_runs kısıt kümesi (kapalı)',
             'sector_package_runs_approval_karar_check|CHECK (((approval_karar IS NULL) OR (approval_karar = ANY (ARRAY[''onay''::text, ''ret''::text])))) && sector_package_runs_barrier_report_zorunlu|CHECK (((durum <> ''tamamlandi''::text) OR (barrier_report IS NOT NULL))) && sector_package_runs_durum_check|CHECK ((durum = ANY (ARRAY[''calisiyor''::text, ''tamamlandi''::text, ''tamamlanmadi''::text]))) && sector_package_runs_duzeltme_soyagaci|CHECK (((kosu_turu = ''duzeltme''::text) = (duzeltilen_run_id IS NOT NULL))) && sector_package_runs_icerik_gunluksuz_yazilmaz|CHECK (((final_candidate IS NULL) OR (final_decision_log IS NOT NULL))) && sector_package_runs_kanit_jetonu_butun|CHECK (((kanit_jetonu IS NULL) OR ((kanit_jetonu_parmakizi IS NOT NULL) AND (kanit_jetonu_basildi_at IS NOT NULL)))) && sector_package_runs_karar_gunlugu_cifti|CHECK (((final_decision_log IS NULL) = (decision_log_sha IS NULL))) && sector_package_runs_kosu_turu_check|CHECK ((kosu_turu = ANY (ARRAY[''ilk''::text, ''periyodik''::text, ''duzeltme''::text]))) && sector_package_runs_package_id_fkey|FOREIGN KEY (package_id) REFERENCES social.sector_packages(id) && sector_package_runs_pkey|PRIMARY KEY (id) && sector_package_runs_run_id_key|UNIQUE (run_id) && sector_package_runs_sector_id_fkey|FOREIGN KEY (sector_id) REFERENCES social.sectors(id) && sector_package_runs_sonuc_check|CHECK (((sonuc IS NULL) OR (sonuc = ANY (ARRAY[''activation_eligible''::text, ''no_change''::text, ''blocked''::text])))) && sector_package_runs_sonuc_yalniz_tamamlandi|CHECK (((sonuc IS NULL) OR (durum = ''tamamlandi''::text)))'),
            ('sector_package_runs indeks kümesi (kapalı)',
             'CREATE INDEX idx_sector_package_runs_sector_created ON social.sector_package_runs USING btree (sector_id, created_at DESC)|f|live && CREATE UNIQUE INDEX sector_package_runs_pkey ON social.sector_package_runs USING btree (id)|t|live && CREATE UNIQUE INDEX sector_package_runs_run_id_key ON social.sector_package_runs USING btree (run_id)|t|live'),
            ('sector_package_runs tetikleyici kümesi (kapalı)',
             'sector_package_runs_approval_snapshot_immutable|enabled'),

            ('package_rollback_plans tablo imzası',
             'relkind=r relpersistence=p partition=f rls=f force_rls=f'),
            ('package_rollback_plans kolon imzası',
             'incident_id:text:nn:- && package_id:uuid:nn:- && observed_active_version:integer:nn:- && target_version:integer:null:- && evidence_class:text:nn:- && reason:text:nn:- && durum:text:nn:- && onay_actor:text:null:- && onaylandi_at:timestamp with time zone:null:- && onay_kapsam_sha:text:null:- && kanit_jetonu:text:null:- && kanit_jetonu_parmakizi:text:null:- && kanit_jetonu_basildi_at:timestamp with time zone:null:- && kanit_jetonu_harcandi_at:timestamp with time zone:null:- && created_at:timestamp with time zone:nn:now()'),
            ('package_rollback_plans kısıt kümesi (kapalı)',
             'package_rollback_plans_durum_check|CHECK ((durum = ANY (ARRAY[''bekliyor''::text, ''tamamlandi''::text, ''hata''::text, ''hedefsiz''::text]))) && package_rollback_plans_hedefsiz_butun|CHECK (((durum = ''hedefsiz''::text) = (target_version IS NULL))) && package_rollback_plans_incident_id_package_id_key|UNIQUE (incident_id, package_id) && package_rollback_plans_kanit_jetonu_butun|CHECK (((kanit_jetonu IS NULL) OR ((kanit_jetonu_parmakizi IS NOT NULL) AND (kanit_jetonu_basildi_at IS NOT NULL)))) && package_rollback_plans_onay_actor_dolu|CHECK (((onay_actor IS NULL) OR (btrim(onay_actor) <> ''''::text))) && package_rollback_plans_onay_butun|CHECK ((num_nonnulls(onay_actor, onaylandi_at, onay_kapsam_sha) = ANY (ARRAY[0, 3])))'),
            ('package_rollback_plans indeks kümesi (kapalı)',
             'CREATE UNIQUE INDEX package_rollback_plans_incident_id_package_id_key ON social.package_rollback_plans USING btree (incident_id, package_id)|t|live'),
            ('package_rollback_plans tetikleyici kümesi (kapalı)',
             'package_rollback_plans_approved_immutable|enabled'),

            ('brand_sub_sector_history tablo imzası',
             'relkind=r relpersistence=p partition=f rls=f force_rls=f'),
            ('brand_sub_sector_history kolon imzası',
             'id:uuid:nn:gen_random_uuid() && brand_id:uuid:nn:- && sub_sector_id:uuid:nn:- && assigned_at:timestamp with time zone:nn:now() && unassigned_at:timestamp with time zone:null:-'),
            ('brand_sub_sector_history kısıt kümesi (kapalı)',
             'brand_sub_sector_history_aralik_check|CHECK (((unassigned_at IS NULL) OR (unassigned_at >= assigned_at))) && brand_sub_sector_history_brand_id_fkey|FOREIGN KEY (brand_id) REFERENCES social.brands(id) ON DELETE CASCADE && brand_sub_sector_history_pkey|PRIMARY KEY (id)'),
            ('brand_sub_sector_history indeks kümesi (kapalı)',
             'CREATE UNIQUE INDEX brand_sub_sector_history_pkey ON social.brand_sub_sector_history USING btree (id)|t|live && CREATE INDEX idx_brand_sub_sector_history_brand ON social.brand_sub_sector_history USING btree (brand_id, assigned_at DESC)|f|live && CREATE UNIQUE INDEX uq_brand_sub_sector_history_acik ON social.brand_sub_sector_history USING btree (brand_id) WHERE (unassigned_at IS NULL)|t|live'),
            ('brand_sub_sector_history tetikleyici kümesi (kapalı)',
             '<yok>'),

            ('brands_sub_sector_history tetikleyicisi',
             trg_brands_kanonik || '|enabled=O'),
            ('sector_package_runs_approval_snapshot_immutable tetikleyicisi',
             trg_kosu_kanonik || '|enabled=O'),
            ('package_rollback_plans_approved_immutable tetikleyicisi',
             trg_plan_kanonik || '|enabled=O'),
            ('sector_research_artifacts K-09 kısıtı',
             'u|UNIQUE (run_id, source, kind)|enforced=true validated=true'),
            ('package_events.event_type CHECK (genişlemiş)',
             'c|CHECK ((event_type = ANY (ARRAY[''mismatch_fallthrough''::text, ''package_read_error''::text, ''stale_assignment_fallback''::text, ''stamp_missing''::text, ''stamp_invalid''::text, ''stamp_stale_at_persist''::text, ''activation''::text, ''rollback''::text, ''deactivation''::text, ''approval''::text, ''rejection''::text])))')
    ),
    observed(label, got) AS (
        VALUES
            ('sector_package_runs tablo imzası',
             (SELECT format('relkind=%s relpersistence=%s partition=%s rls=%s force_rls=%s',
                            c.relkind, c.relpersistence,
                            CASE WHEN c.relispartition THEN 't' ELSE 'f' END,
                            CASE WHEN c.relrowsecurity THEN 't' ELSE 'f' END,
                            CASE WHEN c.relforcerowsecurity THEN 't' ELSE 'f' END)
                FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
               WHERE n.nspname = 'social' AND c.relname = 'sector_package_runs')),
            ('sector_package_runs kolon imzası',
             (SELECT string_agg(format('%s:%s:%s:%s', a.attname,
                                       format_type(a.atttypid, a.atttypmod),
                                       CASE WHEN a.attnotnull THEN 'nn' ELSE 'null' END,
                                       coalesce(pg_get_expr(d.adbin, d.adrelid), '-')),
                                ' && ' ORDER BY a.attnum)
                FROM pg_attribute a
                LEFT JOIN pg_attrdef d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
               WHERE a.attrelid = 'social.sector_package_runs'::regclass
                 AND a.attnum > 0 AND NOT a.attisdropped)),
            ('sector_package_runs kısıt kümesi (kapalı)',
             (SELECT coalesce(string_agg(format('%s|%s', k.conname,
                                                pg_get_constraintdef(k.oid)),
                                         ' && ' ORDER BY k.conname), '<yok>')
                FROM pg_constraint k
               WHERE k.conrelid = 'social.sector_package_runs'::regclass
                 AND k.contype <> 'n')),
            ('sector_package_runs indeks kümesi (kapalı)',
             (SELECT coalesce(string_agg(format('%s|%s|%s',
                                                pg_get_indexdef(i.indexrelid),
                                                i.indisunique,
                                                CASE WHEN i.indisvalid AND i.indisready
                                                      AND i.indislive
                                                     THEN 'live' ELSE 'BROKEN' END),
                                         ' && ' ORDER BY c.relname), '<yok>')
                FROM pg_index i JOIN pg_class c ON c.oid = i.indexrelid
               WHERE i.indrelid = 'social.sector_package_runs'::regclass)),
            ('sector_package_runs tetikleyici kümesi (kapalı)',
             (SELECT coalesce(string_agg(format('%s|%s', t.tgname,
                                                CASE WHEN t.tgenabled = 'O'
                                                     THEN 'enabled' ELSE 'DISABLED' END),
                                         ' && ' ORDER BY t.tgname), '<yok>')
                FROM pg_trigger t
               WHERE t.tgrelid = 'social.sector_package_runs'::regclass
                 AND NOT t.tgisinternal)),

            ('package_rollback_plans tablo imzası',
             (SELECT format('relkind=%s relpersistence=%s partition=%s rls=%s force_rls=%s',
                            c.relkind, c.relpersistence,
                            CASE WHEN c.relispartition THEN 't' ELSE 'f' END,
                            CASE WHEN c.relrowsecurity THEN 't' ELSE 'f' END,
                            CASE WHEN c.relforcerowsecurity THEN 't' ELSE 'f' END)
                FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
               WHERE n.nspname = 'social' AND c.relname = 'package_rollback_plans')),
            ('package_rollback_plans kolon imzası',
             (SELECT string_agg(format('%s:%s:%s:%s', a.attname,
                                       format_type(a.atttypid, a.atttypmod),
                                       CASE WHEN a.attnotnull THEN 'nn' ELSE 'null' END,
                                       coalesce(pg_get_expr(d.adbin, d.adrelid), '-')),
                                ' && ' ORDER BY a.attnum)
                FROM pg_attribute a
                LEFT JOIN pg_attrdef d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
               WHERE a.attrelid = 'social.package_rollback_plans'::regclass
                 AND a.attnum > 0 AND NOT a.attisdropped)),
            ('package_rollback_plans kısıt kümesi (kapalı)',
             (SELECT coalesce(string_agg(format('%s|%s', k.conname,
                                                pg_get_constraintdef(k.oid)),
                                         ' && ' ORDER BY k.conname), '<yok>')
                FROM pg_constraint k
               WHERE k.conrelid = 'social.package_rollback_plans'::regclass
                 AND k.contype <> 'n')),
            ('package_rollback_plans indeks kümesi (kapalı)',
             (SELECT coalesce(string_agg(format('%s|%s|%s',
                                                pg_get_indexdef(i.indexrelid),
                                                i.indisunique,
                                                CASE WHEN i.indisvalid AND i.indisready
                                                      AND i.indislive
                                                     THEN 'live' ELSE 'BROKEN' END),
                                         ' && ' ORDER BY c.relname), '<yok>')
                FROM pg_index i JOIN pg_class c ON c.oid = i.indexrelid
               WHERE i.indrelid = 'social.package_rollback_plans'::regclass)),
            ('package_rollback_plans tetikleyici kümesi (kapalı)',
             (SELECT coalesce(string_agg(format('%s|%s', t.tgname,
                                                CASE WHEN t.tgenabled = 'O'
                                                     THEN 'enabled' ELSE 'DISABLED' END),
                                         ' && ' ORDER BY t.tgname), '<yok>')
                FROM pg_trigger t
               WHERE t.tgrelid = 'social.package_rollback_plans'::regclass
                 AND NOT t.tgisinternal)),

            ('brand_sub_sector_history tablo imzası',
             (SELECT format('relkind=%s relpersistence=%s partition=%s rls=%s force_rls=%s',
                            c.relkind, c.relpersistence,
                            CASE WHEN c.relispartition THEN 't' ELSE 'f' END,
                            CASE WHEN c.relrowsecurity THEN 't' ELSE 'f' END,
                            CASE WHEN c.relforcerowsecurity THEN 't' ELSE 'f' END)
                FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
               WHERE n.nspname = 'social' AND c.relname = 'brand_sub_sector_history')),
            ('brand_sub_sector_history kolon imzası',
             (SELECT string_agg(format('%s:%s:%s:%s', a.attname,
                                       format_type(a.atttypid, a.atttypmod),
                                       CASE WHEN a.attnotnull THEN 'nn' ELSE 'null' END,
                                       coalesce(pg_get_expr(d.adbin, d.adrelid), '-')),
                                ' && ' ORDER BY a.attnum)
                FROM pg_attribute a
                LEFT JOIN pg_attrdef d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
               WHERE a.attrelid = 'social.brand_sub_sector_history'::regclass
                 AND a.attnum > 0 AND NOT a.attisdropped)),
            ('brand_sub_sector_history kısıt kümesi (kapalı)',
             (SELECT coalesce(string_agg(format('%s|%s', k.conname,
                                                pg_get_constraintdef(k.oid)),
                                         ' && ' ORDER BY k.conname), '<yok>')
                FROM pg_constraint k
               WHERE k.conrelid = 'social.brand_sub_sector_history'::regclass
                 AND k.contype <> 'n')),
            ('brand_sub_sector_history indeks kümesi (kapalı)',
             (SELECT coalesce(string_agg(format('%s|%s|%s',
                                                pg_get_indexdef(i.indexrelid),
                                                i.indisunique,
                                                CASE WHEN i.indisvalid AND i.indisready
                                                      AND i.indislive
                                                     THEN 'live' ELSE 'BROKEN' END),
                                         ' && ' ORDER BY c.relname), '<yok>')
                FROM pg_index i JOIN pg_class c ON c.oid = i.indexrelid
               WHERE i.indrelid = 'social.brand_sub_sector_history'::regclass)),
            ('brand_sub_sector_history tetikleyici kümesi (kapalı)',
             (SELECT coalesce(string_agg(format('%s|%s', t.tgname,
                                                CASE WHEN t.tgenabled = 'O'
                                                     THEN 'enabled' ELSE 'DISABLED' END),
                                         ' && ' ORDER BY t.tgname), '<yok>')
                FROM pg_trigger t
               WHERE t.tgrelid = 'social.brand_sub_sector_history'::regclass
                 AND NOT t.tgisinternal)),

            ('brands_sub_sector_history tetikleyicisi',
             (SELECT format('%s|enabled=%s', pg_get_triggerdef(t.oid), t.tgenabled)
                FROM pg_trigger t
               WHERE NOT t.tgisinternal
                 AND t.tgrelid = 'social.brands'::regclass
                 AND t.tgname = 'brands_sub_sector_history')),
            ('sector_package_runs_approval_snapshot_immutable tetikleyicisi',
             (SELECT format('%s|enabled=%s', pg_get_triggerdef(t.oid), t.tgenabled)
                FROM pg_trigger t
               WHERE NOT t.tgisinternal
                 AND t.tgrelid = 'social.sector_package_runs'::regclass
                 AND t.tgname = 'sector_package_runs_approval_snapshot_immutable')),
            ('package_rollback_plans_approved_immutable tetikleyicisi',
             (SELECT format('%s|enabled=%s', pg_get_triggerdef(t.oid), t.tgenabled)
                FROM pg_trigger t
               WHERE NOT t.tgisinternal
                 AND t.tgrelid = 'social.package_rollback_plans'::regclass
                 AND t.tgname = 'package_rollback_plans_approved_immutable')),
            ('sector_research_artifacts K-09 kısıtı',
             (SELECT format('%s|%s|enforced=%s validated=%s',
                            k.contype, pg_get_constraintdef(k.oid),
                            COALESCE(to_jsonb(k)->>'conenforced', 'true'),
                            CASE WHEN k.convalidated THEN 'true' ELSE 'false' END)
                FROM pg_constraint k
               WHERE k.conrelid = 'social.sector_research_artifacts'::regclass
                 AND k.conname = 'sector_research_artifacts_run_source_kind_key')),
            ('package_events.event_type CHECK (genişlemiş)',
             (SELECT format('%s|%s', k.contype, pg_get_constraintdef(k.oid))
                FROM pg_constraint k
               WHERE k.conrelid = 'social.package_events'::regclass
                 AND k.conname = 'package_events_type_check'))
    )
    SELECT string_agg(
               format('%s -> beklenen [%s] · gorulen [%s]',
                      e.label, e.want, coalesce(o.got, '<nesne yok>')),
               E'\n  - ' ORDER BY e.label)
      INTO problems
      FROM expected e
      LEFT JOIN observed o ON o.label = e.label
     WHERE o.got IS DISTINCT FROM e.want;

    IF problems IS NOT NULL THEN
        RAISE EXCEPTION 'migration 036 garanti dogrulamasi BASARISIZ:%',
            E'\n  - ' || problems
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Ayni adda YANLIS TANIMLI bir nesne var; IF NOT EXISTS '
                         'onu DEGISTIRMEZ. Nesneyi elle dusurup migration i '
                         'yeniden uygulayin.';
    END IF;
END
$apply_036$;
