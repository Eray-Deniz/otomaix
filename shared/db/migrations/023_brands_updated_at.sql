-- Migration 023: add updated_at column + trigger to social.brands
-- Fixes: 500 error on logo/intro video uploads (brands.py:187, brands.py:215)
-- Root cause: UPDATE queries reference updated_at but column never existed on social.brands.

ALTER TABLE social.brands
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

-- ── KAPI: NESNE KİMLİĞİ — ad SAHİPLİK DEĞİLDİR ─────────────────────────────
-- `CREATE OR REPLACE FUNCTION` ve `DROP TRIGGER IF EXISTS` katalog nesnesini
-- yalnız ADIYLA arar. Aynı adı taşıyan YABANCI bir fonksiyon sessizce EZİLİR ve
-- ona bağlı BAŞKA bir tetikleyici, fonksiyon kimliği (oid) korunduğu için ANINDA
-- bizim gövdemizi çalıştırmaya başlar; aynı adı taşıyan yabancı bir tetikleyici
-- ise sessizce DÜŞÜRÜLÜR ve başkasının tablosu korumasız kalır. Yazımdan SONRA
-- koşan bir doğrulama bunu YAKALAYAMAZ — ezme işleminden sonraki (kanonik
-- görünen) durumu okur.
--
-- KABUL EDİLEN İKİ DURUM: nesne YOK, ya da tanımı BİREBİR kanonik (ikinci
-- koşum). Üçüncü her durum fail-closed reddedilir.
--
-- KAPSAM SINIRI (ölçülmüş, iddia edilmeyen): kapı SIFIR argümanlı adı denetler
-- (`to_regprocedure('<ad>()')`). Aynı adı taşıyan FARKLI imzalı bir aşırı
-- yükleme bizim yazdığımızı EZMEZ — `CREATE OR REPLACE` onu görmez bile.
--
-- Sınıfın kaynağı: `036_package_runs.sql` KAPI 4 (checkpoint 4, tur 2).
DO $kimlik$
DECLARE
    kayit RECORD;
    mevcut_def TEXT;
    fn_set_updated_at CONSTANT TEXT := $set_updated_at$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$set_updated_at$;
BEGIN
    FOR kayit IN
        SELECT * FROM (VALUES
            ('social.set_updated_at', fn_set_updated_at)
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
                'migration 023: %() adini KANONIK OLMAYAN bir fonksiyon tutuyor (%)',
                kayit.ad, mevcut_def
                USING ERRCODE = 'integrity_constraint_violation',
                      HINT = 'Ad SAHIPLIK DEGILDIR: bu fonksiyonu ezmek ya da ona '
                             'baglanmak, yabanci govdeyi bizim tetikleyicimize '
                             'baglardi. Yabanci nesneyi elle cozup migration i '
                             'yeniden kosturun.';
        END IF;
    END LOOP;

    FOR kayit IN
        SELECT * FROM (VALUES
            ('social.brands', 'brands_updated_at',
             'CREATE TRIGGER brands_updated_at BEFORE UPDATE ON social.brands FOR EACH ROW EXECUTE FUNCTION social.set_updated_at()')
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
                'migration 023: % adini KANONIK OLMAYAN bir tetikleyici tutuyor (%)',
                kayit.ad, mevcut_def
                USING ERRCODE = 'integrity_constraint_violation',
                      HINT = 'DROP TRIGGER IF EXISTS adiyla arar; baskasinin '
                             'tetikleyicisini dusurmek onun tablosunu sessizce '
                             'korumasiz birakirdi.';
        END IF;
    END LOOP;
END
$kimlik$;

DROP TRIGGER IF EXISTS brands_updated_at ON social.brands;
CREATE TRIGGER brands_updated_at
    BEFORE UPDATE ON social.brands
    FOR EACH ROW EXECUTE FUNCTION social.set_updated_at();
