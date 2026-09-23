-- Migration 037 GERİ ALMA — operatör kararları tablosu
--
-- KULLANIM:  psql -f 037_down.sql
--            Gövde TEK transaction'dadır; `-1` / `--single-transaction` GEÇMEYİN.
--
-- VERİ VARKEN FAIL-CLOSED DURUR: tabloyu düşürmek operatörün kararlarını ve
-- motorun ilk sonucunu — ikisi de denetim kanıtıdır — geri dönülmez biçimde
-- siler. Veri varsa geri dönüş şema geri alması değil, veri-koruyan ileri
-- düzeltmedir.

\set ON_ERROR_STOP on

BEGIN;

DO $$
DECLARE
    dolu bigint;
BEGIN
    IF to_regclass('social.sector_run_operator_decisions') IS NULL THEN
        RETURN;
    END IF;
    LOCK TABLE social.sector_run_operator_decisions IN ACCESS EXCLUSIVE MODE;
    SELECT count(*) INTO dolu FROM social.sector_run_operator_decisions;
    IF dolu > 0 THEN
        RAISE EXCEPTION '037 geri alma DURDU: % koşu operatör kararı taşıyor — veri silinmez', dolu;
    END IF;
END
$$;

DROP TABLE IF EXISTS social.sector_run_operator_decisions;

COMMIT;
