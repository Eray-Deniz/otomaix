-- Migration 030: Product images (1→N görsel desteği)
-- Sprint 1 (Çoklu Ürün Görseli) — brand_products için ek görsel tablosu
--
-- Scope: brand_products tablosu şu anda tek görsel tutuyor (image_url, image_key).
-- Ürün başına max 5 görsel (Nano Banana 2/edit sweet spot) eklenebilmesi için
-- yeni product_images tablosu eklenir. brand_products.image_url/image_key
-- ANA görselin denormalize kopyası olarak kalır — mevcut SELECT image_url FROM
-- brand_products çağrılarını bozmaz, geriye dönük uyumluluk bedava gelir.
--
-- Cascade: product silinirse görseller de silinir; R2 temizliği app layer'da
-- (brand_reference_images ve product_documents paterniyle tutarlı).
--
-- Backfill: mevcut image_url IS NOT NULL ürünleri için tek product_images
-- satırı (is_primary=true, position=0) oluşturulur — kullanıcı veri kaybetmez.

CREATE TABLE IF NOT EXISTS social.product_images (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID NOT NULL REFERENCES social.brand_products(id) ON DELETE CASCADE,
  image_url TEXT NOT NULL,
  image_key TEXT NOT NULL,         -- R2 object key (silme için); image_url ile senkron
  is_primary BOOLEAN NOT NULL DEFAULT false,
  position INT NOT NULL DEFAULT 0, -- drag-drop sıralama; ana görsel hariç sıra
  label TEXT,                      -- opsiyonel etiket (örn. "Ön açı", "Yan açı")
  mime_type TEXT,                  -- image/jpeg, image/png, image/webp
  size_kb INT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Listeleme için: ürünün görselleri sırayla
CREATE INDEX IF NOT EXISTS idx_product_images_product
  ON social.product_images(product_id, position);

-- Ürün başına en fazla 1 ana görsel garantisi
CREATE UNIQUE INDEX IF NOT EXISTS idx_product_images_one_primary
  ON social.product_images(product_id) WHERE is_primary = true;

-- =====================================================================
-- Backfill: mevcut tek görselleri product_images'a kopyala
-- =====================================================================
-- Var olan ürünlerin image_url'ı ana görsel olarak product_images'a yazılır.
-- Idempotent: aynı migration tekrar çalıştırılırsa duplicate yapmaz
-- (çünkü id PRIMARY KEY ve INSERT...WHERE NOT EXISTS koruması).
INSERT INTO social.product_images (product_id, image_url, image_key, is_primary, position)
SELECT
  bp.id,
  bp.image_url,
  COALESCE(bp.image_key, ''),
  true,
  0
FROM social.brand_products bp
WHERE bp.image_url IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM social.product_images pi WHERE pi.product_id = bp.id
  );
