-- Phase 6 — Trend Sistemi Yenileme
-- Sprint 1: Üç katmanlı trend mimarisi için tablolar
-- Layer A: sector_trend_cache (paylaşılan, her sektör için tek satır)
-- Layer B: brand_trend_cache (marka bazlı, kısa TTL)
-- Usage sayaçları + Layer C rapor metadata

-- Layer A: Sektör paylaşımlı nightly cache (ayrıca Layer C de burada tutulabilir)
CREATE TABLE IF NOT EXISTS social.sector_trend_cache (
    sector_id UUID NOT NULL REFERENCES social.sectors(id) ON DELETE CASCADE,
    layer TEXT NOT NULL CHECK (layer IN ('A','C')),
    trends JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    source_summary JSONB,
    PRIMARY KEY (sector_id, layer)
);

CREATE INDEX IF NOT EXISTS idx_sector_trend_cache_fetched ON social.sector_trend_cache(fetched_at);

-- Layer B: Marka-bazlı kişisel trend cache (en son tetikleme sonucu)
CREATE TABLE IF NOT EXISTS social.brand_trend_cache (
    brand_id UUID PRIMARY KEY REFERENCES social.brands(id) ON DELETE CASCADE,
    trends JSONB NOT NULL,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    prompt_tokens INT,
    completion_tokens INT,
    serper_queries INT
);

-- Layer B & C kullanım sayaçları (aylık reset)
CREATE TABLE IF NOT EXISTS social.trend_usage (
    account_id UUID NOT NULL REFERENCES social.accounts(id) ON DELETE CASCADE,
    year_month TEXT NOT NULL, -- 'YYYY-MM'
    layer_b_count INT NOT NULL DEFAULT 0,
    layer_c_count INT NOT NULL DEFAULT 0,
    layer_b_cost_usd NUMERIC(10,4) NOT NULL DEFAULT 0,
    layer_c_cost_usd NUMERIC(10,4) NOT NULL DEFAULT 0,
    PRIMARY KEY (account_id, year_month)
);

CREATE INDEX IF NOT EXISTS idx_trend_usage_month ON social.trend_usage(year_month);

-- Layer C raporlarının metadata + R2 path
CREATE TABLE IF NOT EXISTS social.sector_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    account_id UUID NOT NULL REFERENCES social.accounts(id) ON DELETE CASCADE,
    brand_id UUID REFERENCES social.brands(id) ON DELETE SET NULL,
    sector_id UUID NOT NULL REFERENCES social.sectors(id),
    pdf_url TEXT,
    status TEXT NOT NULL DEFAULT 'generating' CHECK (status IN ('generating','ready','failed')),
    error_message TEXT,
    generated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    apify_cost_usd NUMERIC(10,4),
    claude_cost_usd NUMERIC(10,4)
);

CREATE INDEX IF NOT EXISTS idx_sector_reports_account ON social.sector_reports(account_id, generated_at DESC);
CREATE INDEX IF NOT EXISTS idx_sector_reports_status ON social.sector_reports(status) WHERE status = 'generating';

-- Eski tablo deprecation notu
COMMENT ON TABLE social.trend_cache IS 'DEPRECATED — Phase 6 öncesi (6 saatlik sektör cache). Yeni kod social.sector_trend_cache ve social.brand_trend_cache kullanır. Tablo rollback için tutuluyor.';
