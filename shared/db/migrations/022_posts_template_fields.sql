-- Phase 7 — Sprint 1: Sektör-Spesifik Şablon Sistemi için posts tablosuna kolon ekleme
-- Mevcut akışları bozmamak için hepsi NULL'lanabilir additive kolonlar.
-- template_id=NULL yolunda special_day/quote/video/autoposting/serbest içerik aynen çalışır.

ALTER TABLE social.posts
  ADD COLUMN IF NOT EXISTS template_id TEXT,
  ADD COLUMN IF NOT EXISTS template_fields JSONB,
  ADD COLUMN IF NOT EXISTS platform_captions JSONB,
  ADD COLUMN IF NOT EXISTS slides JSONB;

-- Şablon bazlı analytics ve filtreleme için partial index (NULL satırları index'lemez)
CREATE INDEX IF NOT EXISTS idx_posts_template_id
  ON social.posts(template_id)
  WHERE template_id IS NOT NULL;

COMMENT ON COLUMN social.posts.template_id IS 'Phase 7 — şablon ID (templates_data.py). NULL ise serbest içerik/özel akış.';
COMMENT ON COLUMN social.posts.template_fields IS 'Phase 7 — yapısal form verisi (ör. {product_name, price, discount}).';
COMMENT ON COLUMN social.posts.platform_captions IS 'Phase 7 — platform-özel caption''lar (caption-gen endpoint''inden).';
COMMENT ON COLUMN social.posts.slides IS 'Phase 7 scaffold — v2 carousel slayt verisi. v1''de her zaman NULL.';
