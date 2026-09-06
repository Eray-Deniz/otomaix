-- Migration 034 GERİ ALMA — yönetici bildirim OUTBOX'ı
--
-- BU DOSYA DA PLAN 1'DEN DEVRALINAN BİR BOŞLUĞU KAPATIR (bkz. `033_down.sql`
-- başlığı; ikisi aynı turda yazıldı).
--
-- KULLANIM:  psql -f 034_down.sql
--            Script `ON_ERROR_STOP`u KENDİ açar ve tüm gövdeyi TEK
--            transaction'a sarar. `-1` / `--single-transaction` GEÇMEYİN.
--
-- ÇAĞIRANIN OTURUMU BOZULMAZ: önceki `ON_ERROR_STOP` değeri saklanır ve
-- SONUNDA geri yüklenir. Ret yolunun ölçülmüş sınırı `036_down.sql`
-- başlığında yazılıdır ve burada da geçerlidir.
--
-- SÖZLEŞME (032'nin veri-varken-REDDET modeli):
--
--   `admin_events` bir TRANSACTIONAL OUTBOX'tır: satır, onu tetikleyen işin
--   transaction'ıyla BİRLİKTE commit edilir, iletim commit SONRASI ayrı bir
--   adımdır. Tek satır bile duruyorsa tabloyu düşürmek, HENÜZ İLETİLMEMİŞ bir
--   yönetici bildirimini sessizce yok etmek olurdu — teslim garantisinin tam
--   tersine. Terminal (`sent`/`failed`) satırlar da denetim izidir.
--
--   Bu yüzden kapı DURUM AYRIMI YAPMAZ: herhangi bir satır varsa DUR. "Yalnız
--   `sent` olanları say" gibi bir incelik, kurtarma yolunun (`dispatch-pending`)
--   claim edilmiş ama süresi dolmuş satırlarını da kapsam dışı bırakırdı.
--
--   Preflight EN BAŞTADIR ve sayım tablo ACCESS EXCLUSIVE kilidi ALTINDAYKEN
--   yapılır.
--
-- 036 İLE SIRA BAĞIMLILIĞI YOKTUR: 036 `admin_events`e dokunmaz. Yine de Task
-- 18 runbook'u geri alma sırasını 036 → 034 → 033 → 032 olarak yazar.

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
    outbox_satir BIGINT := 0;
BEGIN
    IF to_regclass('social.admin_events') IS NULL THEN
        RAISE EXCEPTION
            'migration 034 geri alma REDDEDILDI: social.admin_events tablosu YOK'
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Olmayan tablo kilitlenemez; koruma kurulamaz. Geri alma '
                         'ikinci kez kosturulmaz.';
    END IF;

    EXECUTE 'LOCK TABLE social.admin_events IN ACCESS EXCLUSIVE MODE';
    EXECUTE 'SELECT count(*) FROM social.admin_events' INTO outbox_satir;

    IF outbox_satir > 0 THEN
        RAISE EXCEPTION
            'migration 034 geri alma REDDEDILDI: veri var (admin_events=%)',
            outbox_satir
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Iletilmemis bir bildirimi script ile yok etmek teslim '
                         'garantisinin tersidir. Canlida yol ileri duzeltme '
                         '(forward-fix) migration idir.';
    END IF;
END
$preflight$;

DROP TABLE IF EXISTS social.admin_events;

DO $verify_down$
DECLARE
    leftovers TEXT;
BEGIN
    SELECT string_agg(label, E'\n  - ' ORDER BY label)
      INTO leftovers
      FROM (
        SELECT 'tablo social.admin_events' AS label
         WHERE to_regclass('social.admin_events') IS NOT NULL
        UNION ALL
        SELECT 'indeks ' || indexname
          FROM pg_indexes
         WHERE schemaname = 'social' AND indexname = 'idx_admin_events_claimable'
      ) AS remaining;

    IF leftovers IS NOT NULL THEN
        RAISE EXCEPTION 'migration 034 geri alma EKSIK kaldi:%',
            E'\n  - ' || leftovers
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Kalan nesneyi elle dusurup script i yeniden kosturun.';
    END IF;
END
$verify_down$;

COMMIT;

\set ON_ERROR_STOP :OTOMAIX_DOWN_OES_ONCE
\unset OTOMAIX_DOWN_OES_ONCE
