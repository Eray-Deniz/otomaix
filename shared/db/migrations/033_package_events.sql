-- Migration 033: Sektör bilgi paketi — kalıcı olay kaydı
--
-- Kapsam (spec §14.4, plan Task 12):
--   1. social.package_events — kapalı olay kümesi, iki kapsam sınıfı (F21)
--
-- `generation_stamps` bu migration'da DEĞİL 032'de kuruldu: Task 10 (üretici
-- ucu) o tabloya Task 12'den ÖNCE muhtaçtı, o yüzden sıralama böyle.
--
-- Bu tablo bir DENETİM İZİDİR. İki tasarım sonucu buradan çıkar:
--   * Sürüm alanları (`from_version` / `to_version`) sentinel değer taşımaz —
--     "yok" NULL'dır. Sınır geçişleri (ilk aktivasyon, deaktivasyon) uydurma
--     bir sürüm numarasıyla temsil edilseydi denetim izi yalan söylerdi.
--   * `detail` skaler değerli kısa bir sözlüktür (şekil kapısı serviste).
--     Paket İÇERİĞİ buraya basılmaz; olay kaydı bir kopya deposu değildir.

-- ---------------------------------------------------------------------------
-- 1. Olay tablosu
-- ---------------------------------------------------------------------------
--
-- `event_type` CHECK ile kapalıdır: kümeyi genişletmek migration ister. Yeni
-- bir olay türünü sessizce yazabilmek, "kapalı başlangıç kümesi" hükmünü
-- (spec §14.4) uygulamada boşa çıkarırdı.
--
-- `sector_id` / `package_id` FK DEĞİLDİR ve bu bilinçlidir: denetim izi,
-- işaret ettiği satır silinse bile AYAKTA kalmalıdır (paket satırının silinmesi
-- olayın olmadığı anlamına gelmez). `brand_id` ise FK + CASCADE'dir — marka
-- silme sözleşmesi (F18) korunur, markaya ait iz markayla birlikte gider.

CREATE TABLE IF NOT EXISTS social.package_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type TEXT NOT NULL,
    sector_id UUID,
    brand_id UUID REFERENCES social.brands(id) ON DELETE CASCADE,
    package_id UUID,
    from_version INT,
    to_version INT,
    actor TEXT,
    detail JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT package_events_type_check CHECK (event_type IN (
        'mismatch_fallthrough',
        'package_read_error',
        'stale_assignment_fallback',
        'stamp_missing',
        'stamp_invalid',
        'stamp_stale_at_persist',
        'activation',
        'rollback',
        'deactivation'
    ))
);

-- Marka panosu ve olay süpürücüsü aynı iki eksenden okur: "bu markanın
-- olayları, en yeniden eskiye" ve "bu sektörün yaşam döngüsü".
CREATE INDEX IF NOT EXISTS idx_package_events_brand_created
    ON social.package_events (brand_id, created_at DESC)
    WHERE brand_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_package_events_sector_created
    ON social.package_events (sector_id, created_at DESC)
    WHERE sector_id IS NOT NULL;

-- ---------------------------------------------------------------------------
-- 2. Belgeleme
-- ---------------------------------------------------------------------------

COMMENT ON TABLE social.package_events IS
    'Sektor bilgi paketi — kalici olay kaydi (spec 14.4). Kapali olay kumesi CHECK ile zorlanir. Iki kapsam sinifi (F21): marka-kapsamli olaylar brand_id ISTER, yasam-dongusu olaylari sector_id+package_id+actor ISTER.';
COMMENT ON COLUMN social.package_events.from_version IS
    'Kaynak surum. NULL = yok (ilk aktivasyon) — sentinel deger KULLANILMAZ.';
COMMENT ON COLUMN social.package_events.to_version IS
    'Hedef surum. NULL = yok (deaktivasyon) — sentinel deger KULLANILMAZ.';
COMMENT ON COLUMN social.package_events.detail IS
    'Skaler degerli kisa sozluk (sekil kapisi: services/package_events.py). Paket icerigi buraya BASILMAZ.';
COMMENT ON COLUMN social.package_events.sector_id IS
    'FK DEGIL — denetim izi, isaret ettigi satir silinse bile ayakta kalir.';
