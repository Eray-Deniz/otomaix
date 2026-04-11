-- Migration: 006_document_rag.sql
-- Add raw_text to brand_documents, create brand_document_chunks for RAG

ALTER TABLE social.brand_documents ADD COLUMN IF NOT EXISTS raw_text TEXT;

CREATE TABLE IF NOT EXISTS social.brand_document_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID REFERENCES social.brand_documents(id) ON DELETE CASCADE,
  brand_id UUID REFERENCES social.brands(id) ON DELETE CASCADE,
  chunk_index INTEGER NOT NULL,
  content TEXT NOT NULL,
  embedding vector(1536),
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_brand_doc_chunks_document_id
  ON social.brand_document_chunks(document_id);

CREATE INDEX IF NOT EXISTS idx_brand_doc_chunks_brand_id
  ON social.brand_document_chunks(brand_id);

-- ivfflat index for cosine similarity search (used when embeddings are populated)
CREATE INDEX IF NOT EXISTS idx_brand_doc_chunks_embedding
  ON social.brand_document_chunks USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);
