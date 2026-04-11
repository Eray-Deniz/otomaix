-- Migration: 008_trend_cache.sql
-- Trend analizi önbellek tablosu

CREATE TABLE IF NOT EXISTS social.trend_cache (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sector TEXT NOT NULL,
  trends JSONB,
  fetched_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_trend_cache_sector
  ON social.trend_cache(sector);

CREATE INDEX IF NOT EXISTS idx_trend_cache_fetched_at
  ON social.trend_cache(fetched_at DESC);
