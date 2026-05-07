-- Migration 029: Brand reference images
-- Sprint 3 (Özel Gün) — Marka referans görsel kütüphanesi
--
-- Scope: kullanıcı kendi referans görsellerini (Atatürk fotoğrafı, kurucu portre vb.)
-- yükler, içerik üretirken Nano Banana 2 edit'e ref olarak verilir.
-- Identity-preserving görsel üretim için kullanılır (FLUX text-to-image kişi tanımıyor).
--
-- Limit: marka başına max 20 görsel — application layer'da kontrol edilir
-- (brand_products pattern'iyle tutarlı).
-- Cascade: brand silinirse referans görseller de silinir; R2 temizliği app layer'da
-- best-effort.

CREATE TABLE IF NOT EXISTS social.brand_reference_images (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES social.brands(id) ON DELETE CASCADE,
  image_url TEXT NOT NULL,
  image_key TEXT NOT NULL,       -- R2 object key (silme için); image_url ile senkron
  label TEXT,                    -- opsiyonel etiket (örn. "Atatürk 1923 portre")
  mime_type TEXT,                -- image/jpeg, image/png, image/webp
  size_kb INT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Listeleme için genel index (yeni eklenen önce)
CREATE INDEX IF NOT EXISTS idx_brand_reference_images_brand
  ON social.brand_reference_images(brand_id, created_at DESC);
