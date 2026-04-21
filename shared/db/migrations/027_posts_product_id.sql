-- Phase 9 Sprint 6 — posts.product_id kolonu
-- Ürün/hizmet image-edit akışı için post'un hangi brand_products kaydından
-- üretildiğini bağlar. NULL = ürün-bağımsız post (mevcut tüm akışlar).
-- ON DELETE SET NULL — ürün silinse bile post kaydı kaybolmasın (görsel zaten R2'de).

ALTER TABLE social.posts
  ADD COLUMN IF NOT EXISTS product_id UUID NULL
  REFERENCES social.brand_products(id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_posts_product_id
  ON social.posts(product_id)
  WHERE product_id IS NOT NULL;
