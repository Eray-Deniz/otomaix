-- Migration 031: brand_products.highlight (kısa pazarlama vurgusu)
-- Scope: ürün/hizmet için ayrı bir "Öne Çıkan Vurgu" alanı.
--   - description: uzun teknik bilgi (hammadde, ölçü, materyal) — AI bağlamına gider
--   - highlight: kısa pazarlama mesajı — görsel overlay'ine basılır + caption'da öne çıkar
-- Additive — mevcut satırlar NULL kalır, eski caption/görsel davranışı bozulmaz.
-- maxLength enforcement Pydantic tarafında (60 char); DB'de soft TEXT.

ALTER TABLE social.brand_products
    ADD COLUMN IF NOT EXISTS highlight TEXT;
