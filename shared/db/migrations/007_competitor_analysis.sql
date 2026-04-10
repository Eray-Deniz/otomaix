-- Migration: 007_competitor_analysis.sql
-- Rakip analizi tabloları

CREATE TABLE IF NOT EXISTS social.competitor_analyses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID REFERENCES social.brands(id) ON DELETE CASCADE,
  competitor_name TEXT NOT NULL,
  instagram_handle TEXT,
  tiktok_handle TEXT,
  website_url TEXT,
  last_analyzed_at TIMESTAMPTZ,
  analysis_data JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_competitor_analyses_brand_id
  ON social.competitor_analyses(brand_id);

CREATE INDEX IF NOT EXISTS idx_competitor_analyses_last_analyzed
  ON social.competitor_analyses(last_analyzed_at);
