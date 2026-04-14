-- Migration: 016_post_publications.sql
-- B-9: Platform-bazında yayın durumu tracking'i.
-- Bir post birden fazla platforma yayınlandığında (Instagram + TikTok + LinkedIn),
-- her platform için ayrı kayıt tutulur. Posts.status üst seviye özeti:
--   'published'           → tüm platformlar başarılı
--   'partially_published' → en az bir başarılı, en az bir başarısız
--   'failed'              → hiçbiri başarılı değil

CREATE TABLE IF NOT EXISTS social.post_publications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id UUID NOT NULL REFERENCES social.posts(id) ON DELETE CASCADE,
  platform TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  external_id TEXT,
  error_message TEXT,
  upload_post_response JSONB,
  published_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (post_id, platform)
);

-- Geçerli status değerleri: 'pending' | 'publishing' | 'published' | 'failed'

CREATE INDEX IF NOT EXISTS idx_post_publications_post_id
  ON social.post_publications(post_id);

CREATE INDEX IF NOT EXISTS idx_post_publications_failed
  ON social.post_publications(post_id, platform)
  WHERE status = 'failed';
