-- Migration 033 GERİ ALMA — kalıcı paket olay kaydı
--
-- BU DOSYA PLAN 1'DEN DEVRALINAN BİR BOŞLUĞU KAPATIR. Ölçüldü (2026-09-06):
-- `shared/db/migrations/rollback/` yalnız `032_down.sql` ve `035_down.sql`
-- taşıyordu; Plan 2'nin geri alma anlatısı (Task 18 runbook'u) 033 ve 034'ün
-- geri alınabilirliğine dayanıyor.
--
-- KULLANIM:  psql -f 033_down.sql
--            Script `ON_ERROR_STOP`u KENDİ açar ve tüm gövdeyi TEK
--            transaction'a sarar. `-1` / `--single-transaction` GEÇMEYİN.
--
-- ÇAĞIRANIN OTURUMU BOZULMAZ: önceki `ON_ERROR_STOP` değeri saklanır ve
-- SONUNDA geri yüklenir (hiç ayarlanmamışsa `\unset`). Ret yolunun ölçülmüş
-- sınırı `rollback/036_down.sql` başlığında yazılıdır ve burada da geçerlidir.
--
-- SÖZLEŞME (032'nin veri-varken-REDDET modeli, aynı sınıf):
--
--   `package_events` bir DENETİM İZİdir. Tek satır bile içeriyorsa script
--   HİÇBİR değişiklik yapmadan hata ile DURur: "bu markanın üretimi şu tarihte
--   paketsiz yola düştü" cevabı bir geri alma script'iyle silinmez.
--
--   Preflight EN BAŞTADIR ve sayım tablo ACCESS EXCLUSIVE kilidi ALTINDAYKEN
--   yapılır; sayımdan sonra araya giren bir yazar OLAMAZ.
--
-- SIRA KAPISI — 036 HÂLÂ UYGULIYSA DUR:
--   036 bu tablonun `event_type` CHECK'ini genişletir. Tabloyu 036 ayaktayken
--   düşürmek, 036'nın geri almasını (CHECK'i daraltma adımı) uygulanamaz hâle
--   getirir ve `log_package_event` çalışma zamanında olmayan tabloya yazmaya
--   çalışır. Runbook sırası 036 → 033'tür; kapı o sırayı ZORLAR, hatırlatmaz.

-- ÖLÇÜLDÜ (psql 16.15): `ON_ERROR_STOP` psql'in YERLEŞİK değişkenidir ve HER
-- ZAMAN tanımlıdır — `-v ON_ERROR_STOP=1` verilmemiş taze bir oturumda bile
-- `:{?ON_ERROR_STOP}` DOĞRU döner ve değeri `off`tur; `\unset` onu tanımsız
-- yapmaz, varsayılana (`off`) döndürür. Bu yüzden koşullu bir dal YOKTUR:
-- değer koşulsuz saklanır, sonunda koşulsuz geri yüklenir. Ölçülmemiş bir
-- `\else` dalı taşımak, hiç koşulmayan bir kurtarma yolu taşımak olurdu.
\set OTOMAIX_DOWN_OES_ONCE :ON_ERROR_STOP

\set ON_ERROR_STOP on

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

DO $preflight$
DECLARE
    olay_satir BIGINT := 0;
BEGIN
    IF to_regclass('social.package_events') IS NULL THEN
        RAISE EXCEPTION
            'migration 033 geri alma REDDEDILDI: social.package_events tablosu YOK'
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Olmayan tablo kilitlenemez; koruma kurulamaz. Geri alma '
                         'ikinci kez kosturulmaz.';
    END IF;

    IF to_regclass('social.sector_package_runs') IS NOT NULL THEN
        RAISE EXCEPTION
            'migration 033 geri alma REDDEDILDI: migration 036 hala uygulanmis '
            '(social.sector_package_runs duruyor)'
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Sira 036 -> 033 tur: once rollback/036_down.sql i '
                         'kosturun. 036 bu tablonun CHECK ini genisletir; tabloyu '
                         'once dusurmek 036 nin geri almasini uygulanamaz kilar.';
    END IF;

    EXECUTE 'LOCK TABLE social.package_events IN ACCESS EXCLUSIVE MODE';
    EXECUTE 'SELECT count(*) FROM social.package_events' INTO olay_satir;

    IF olay_satir > 0 THEN
        RAISE EXCEPTION
            'migration 033 geri alma REDDEDILDI: veri var (package_events=%)',
            olay_satir
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Denetim izi script ile imha edilmez. Canlida yol ileri '
                         'duzeltme (forward-fix) migration idir.';
    END IF;
END
$preflight$;

-- Tabloyla birlikte üstündeki indeksler de gider; ayrıca düşürmeye gerek yok.
-- `CASCADE` KULLANILMAZ: bu tabloya dayanan bir nesne varsa onu sessizce yok
-- etmek yerine DURmak doğrudur (fail-closed).
DROP TABLE IF EXISTS social.package_events;

DO $verify_down$
DECLARE
    leftovers TEXT;
BEGIN
    SELECT string_agg(label, E'\n  - ' ORDER BY label)
      INTO leftovers
      FROM (
        SELECT 'tablo social.package_events' AS label
         WHERE to_regclass('social.package_events') IS NOT NULL
        UNION ALL
        SELECT 'indeks ' || indexname
          FROM pg_indexes
         WHERE schemaname = 'social'
           AND indexname IN ('idx_package_events_brand_created',
                             'idx_package_events_sector_created')
      ) AS remaining;

    IF leftovers IS NOT NULL THEN
        RAISE EXCEPTION 'migration 033 geri alma EKSIK kaldi:%',
            E'\n  - ' || leftovers
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Kalan nesneyi elle dusurup script i yeniden kosturun.';
    END IF;
END
$verify_down$;

COMMIT;

\set ON_ERROR_STOP :OTOMAIX_DOWN_OES_ONCE
\unset OTOMAIX_DOWN_OES_ONCE
