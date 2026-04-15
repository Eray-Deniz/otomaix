-- Phase 6 — Trend Sistemi Yenileme
-- Sprint 1: Hiyerarşik sektör tablosu + brands.sector_id dual-write
-- Geri uyumluluk: social.brands.sector (TEXT) kolonu korunur, yeni sector_id eklenir.

CREATE TABLE IF NOT EXISTS social.sectors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    parent_sector_id UUID REFERENCES social.sectors(id) ON DELETE RESTRICT,
    keywords TEXT[] NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sectors_parent ON social.sectors(parent_sector_id);
CREATE INDEX IF NOT EXISTS idx_sectors_slug ON social.sectors(slug);

-- 11 ana sektör seed (idempotent — ON CONFLICT slug)
INSERT INTO social.sectors (slug, display_name, keywords) VALUES
    ('teknoloji',   'Teknoloji',          ARRAY['teknoloji','yazılım','yapay zeka','dijital','siber']),
    ('e-ticaret',   'E-Ticaret',          ARRAY['e-ticaret','online alışveriş','kargo','mağaza','satış']),
    ('yemek',       'Yemek & İçecek',     ARRAY['restoran','yemek','mutfak','tarif','gastronomi']),
    ('saglik',      'Sağlık & Wellness',  ARRAY['sağlık','hastane','ilaç','wellness','fitness']),
    ('egitim',      'Eğitim',             ARRAY['eğitim','üniversite','kurs','öğrenci','diploma']),
    ('moda',        'Moda & Stil',        ARRAY['moda','giyim','trend','stil','koleksiyon']),
    ('turizm',      'Turizm & Otelcilik', ARRAY['turizm','tatil','otel','seyahat','destinasyon']),
    ('finans',      'Finans',             ARRAY['finans','borsa','yatırım','döviz','ekonomi']),
    ('gayrimenkul', 'Gayrimenkul',        ARRAY['gayrimenkul','konut','inşaat','kira','tapu']),
    ('otomotiv',    'Otomotiv',           ARRAY['otomotiv','araç','elektrikli araç','trafik','galeri']),
    ('genel',       'Genel',              ARRAY['Türkiye','gündem','sosyal medya'])
ON CONFLICT (slug) DO NOTHING;

-- brands tablosuna sector_id kolonu (eski text sector kalır, geri uyumluluk)
ALTER TABLE social.brands ADD COLUMN IF NOT EXISTS sector_id UUID REFERENCES social.sectors(id);
CREATE INDEX IF NOT EXISTS idx_brands_sector_id ON social.brands(sector_id);

-- Mevcut text sector değerlerini slug eşleşmesiyle map et
-- Eşleşme yoksa 'genel'e düşer
UPDATE social.brands
SET sector_id = COALESCE(
    (SELECT id FROM social.sectors WHERE slug = lower(regexp_replace(COALESCE(social.brands.sector, ''), '\s+', '-', 'g')) LIMIT 1),
    (SELECT id FROM social.sectors WHERE slug = 'genel' LIMIT 1)
)
WHERE sector_id IS NULL;

COMMENT ON COLUMN social.brands.sector IS 'DEPRECATED Phase 6 — frontend yazmaya devam eder, yeni kod sector_id kullanır. Dual-write ile senkron tutulur.';
COMMENT ON TABLE social.sectors IS 'Phase 6 — hiyerarşik sektör tablosu. parent_sector_id ile alt sektörler eklenebilir.';
