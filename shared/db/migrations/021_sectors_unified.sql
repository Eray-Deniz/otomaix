-- Phase 6 — Sprint 1.5: Birleşik 12 sektör listesi
-- Frontend (Tekstil, Gıda, İnşaat, Perakende, Hizmet, Diğer) ve DB (e-ticaret, yemek, moda, gayrimenkul)
-- ayrı listelerini tek bir kaynağa indiriyoruz. Tek doğruluk kaynağı: social.sectors.
--
-- Strateji:
--   1. Yeni birleşik slug'ları ekle (e-ticaret-perakende, yemek-gida, moda-tekstil,
--      insaat-gayrimenkul, hizmet)
--   2. Mevcut markaları eski slug'lardan yeni slug'lara map et
--   3. Eski tek-anlamlı slug'ları sil (e-ticaret, yemek, moda, gayrimenkul)
--   4. turizm display_name güncelle, genel display_name güncelle

-- 1. Yeni birleşik sektörler
INSERT INTO social.sectors (slug, display_name, keywords) VALUES
    ('e-ticaret-perakende',  'E-Ticaret & Perakende',
        ARRAY['e-ticaret','online alışveriş','perakende','mağaza','satış','kargo']),
    ('yemek-gida',           'Yemek & Gıda',
        ARRAY['restoran','yemek','mutfak','tarif','gastronomi','gıda','market']),
    ('moda-tekstil',         'Moda & Tekstil',
        ARRAY['moda','giyim','tekstil','trend','stil','koleksiyon','konfeksiyon']),
    ('insaat-gayrimenkul',   'İnşaat & Gayrimenkul',
        ARRAY['inşaat','gayrimenkul','konut','kira','tapu','proje','yapı']),
    ('hizmet',               'Hizmet & Danışmanlık',
        ARRAY['hizmet','danışmanlık','b2b','servis','outsourcing'])
ON CONFLICT (slug) DO NOTHING;

-- 2. Mevcut markaları eski slug'lardan yeni birleşik slug'lara taşı
UPDATE social.brands SET sector_id = (SELECT id FROM social.sectors WHERE slug = 'e-ticaret-perakende')
    WHERE sector_id = (SELECT id FROM social.sectors WHERE slug = 'e-ticaret');

UPDATE social.brands SET sector_id = (SELECT id FROM social.sectors WHERE slug = 'yemek-gida')
    WHERE sector_id = (SELECT id FROM social.sectors WHERE slug = 'yemek');

UPDATE social.brands SET sector_id = (SELECT id FROM social.sectors WHERE slug = 'moda-tekstil')
    WHERE sector_id = (SELECT id FROM social.sectors WHERE slug = 'moda');

UPDATE social.brands SET sector_id = (SELECT id FROM social.sectors WHERE slug = 'insaat-gayrimenkul')
    WHERE sector_id = (SELECT id FROM social.sectors WHERE slug = 'gayrimenkul');

-- 3. Eski tek-anlamlı slug'ları temizle (artık birleşik versiyonları var)
DELETE FROM social.sectors WHERE slug IN ('e-ticaret','yemek','moda','gayrimenkul');

-- 4. Display name güncellemeleri
UPDATE social.sectors SET display_name = 'Turizm & Konaklama' WHERE slug = 'turizm';
UPDATE social.sectors SET display_name = 'Diğer / Genel' WHERE slug = 'genel';

-- Sonuç: 12 sektör
-- teknoloji, e-ticaret-perakende, yemek-gida, saglik, egitim, moda-tekstil,
-- turizm, finans, insaat-gayrimenkul, otomotiv, hizmet, genel

COMMENT ON TABLE social.sectors IS 'Phase 6 — birlesik 12 sektor. Frontend ve backend tek kaynagi. Migration 019+021.';
