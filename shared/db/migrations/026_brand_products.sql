-- Migration 026: Brand products + product documents + product document chunks
-- Phase 9 Sprint 1 — Ürün/Hizmet Kütüphanesi
--
-- Scope: marka ürün/hizmet kütüphanesi + ürüne bağlı RAG dokümanları
-- Additive migration — mevcut tabloları değiştirmez
-- Cascade delete: brand → products → documents → chunks

-- =====================================================================
-- brand_products: Marka ürün/hizmet kütüphanesi
-- =====================================================================
CREATE TABLE IF NOT EXISTS social.brand_products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID NOT NULL REFERENCES social.brands(id) ON DELETE CASCADE,
  type TEXT NOT NULL CHECK (type IN ('product', 'service')),
  name TEXT NOT NULL,
  description TEXT,
  tags TEXT[] NOT NULL DEFAULT '{}',
  image_url TEXT,       -- nullable: hizmet kayıtları için görsel opsiyonel
  image_key TEXT,       -- R2 object key (silme için); image_url ile senkron
  is_active BOOLEAN NOT NULL DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Quota sorgusu için partial index (is_active=true satırları)
CREATE INDEX IF NOT EXISTS idx_brand_products_brand_active
  ON social.brand_products(brand_id) WHERE is_active = true;

-- Listeleme için genel index (yeni eklenen önce)
CREATE INDEX IF NOT EXISTS idx_brand_products_brand
  ON social.brand_products(brand_id, created_at DESC);

DROP TRIGGER IF EXISTS brand_products_updated_at ON social.brand_products;
CREATE TRIGGER brand_products_updated_at
  BEFORE UPDATE ON social.brand_products
  FOR EACH ROW EXECUTE FUNCTION social.set_updated_at();

-- =====================================================================
-- product_documents: Ürüne bağlı dokümanlar (cascade delete)
-- =====================================================================
CREATE TABLE IF NOT EXISTS social.product_documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID NOT NULL REFERENCES social.brand_products(id) ON DELETE CASCADE,
  filename TEXT NOT NULL,
  file_url TEXT NOT NULL,
  file_key TEXT NOT NULL,       -- R2 object key
  file_type TEXT,               -- mime type veya uzantı
  file_size BIGINT,
  raw_text TEXT,                -- küçük dokümanlar için tam metin
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_product_documents_product
  ON social.product_documents(product_id, created_at DESC);

-- =====================================================================
-- product_document_chunks: RAG embedding chunks (pgvector)
-- =====================================================================
CREATE TABLE IF NOT EXISTS social.product_document_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES social.product_documents(id) ON DELETE CASCADE,
  chunk_index INT NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536),       -- OpenAI text-embedding-3-small (brand_document_chunks ile tutarlı)
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_product_chunks_document
  ON social.product_document_chunks(document_id, chunk_index);

-- Vector similarity search için IVFFlat index (brand_document_chunks deseni)
CREATE INDEX IF NOT EXISTS idx_product_chunks_embedding
  ON social.product_document_chunks
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);
