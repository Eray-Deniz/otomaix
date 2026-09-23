-- Migration 037 — operatör kararları (açık soruların kapanış yolu)
--
-- NE EKLİYOR:
--   `social.sector_run_operator_decisions` — koşu başına EN FAZLA bir satır:
--     * `kararlar` — operatörün açık sorulara verdiği cevaplar ve pakete
--       uyguladığı işlemler (hangi soru · hangi işlem · hangi birim · hukuki mi).
--     * `motor_ilk_sonucu` — operatör kararları yazılmadan ÖNCE koşu satırında
--       duran motor sonucunun birebir kopyası. Denetim izi: motorun kendi
--       söylediği ezilip kaybolmaz.
--   Satır varsa koşu satırındaki sonuç, operatör kararları uygulanmış sonuçtur.
--
-- NEDEN (ölçüldü, 2026-09-23): motor sentezin her açık sorusunda koşuyu
-- `blocked` yapar (K-71) ama cevabı geri alan bir yol yoktu; `blocked` koşu
-- taslak yazmaz, düzeltme turu ise yalnız reddedilmiş taslaktan açılır.
-- `kosu-23e19d03` koşusunu durduran TEK sebep 11 açık soruydu. Karar (Eray,
-- 2026-09-23): operatör cevapları ve eklemeleri pakete "operatör kararı"
-- etiketiyle girer; kaynaksız eklemeye izin vardır.
--
-- NEDEN AYRI TABLO: 036 `sector_package_runs`'ın kolon ve kısıt kümesini KAPALI
-- tutar ve yeniden uygulamada doğrular; o tabloya kolon eklemek 036'nın
-- yeniden uygulanma garantisini bozar (ölçüldü:
-- `test_036_reapply_after_036_passes`).
--
-- TRANSACTION SAHİPLİĞİ: kendi `BEGIN/COMMIT`ini TAŞIMAZ; runner ve testler
-- `--single-transaction` ile uygular. Fonksiyon ve tetikleyici YAZMAZ.

-- YABANCI ANAHTAR YOK — bilinçli: 036'nın geri alma yolu `sector_package_runs`'ı
-- düşürür ve bağımlı bir kısıt onu durdururdu (ölçüldü: 036_down testleri).
-- Bağ yazım yolunda kurulur: satır YALNIZ koşu satırından `INSERT … SELECT`
-- ile doğar (`runs.record_operator_resolution`), olmayan koşuya yazılamaz.
CREATE TABLE IF NOT EXISTS social.sector_run_operator_decisions (
    run_id           TEXT PRIMARY KEY,
    kararlar         JSONB NOT NULL,
    motor_ilk_sonucu JSONB NOT NULL,
    actor            TEXT NOT NULL CHECK (btrim(actor) <> ''),
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);
