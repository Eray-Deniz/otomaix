-- Migration: 012_crm_tables.sql
-- CRM Admin Paneli — dahili schema ve tablolar

CREATE SCHEMA IF NOT EXISTS crm;

-- Hesap notları (iç notlar, müşteriye görünmez)
CREATE TABLE IF NOT EXISTS crm.account_notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID NOT NULL,  -- references social.accounts
  note TEXT NOT NULL,
  created_by TEXT NOT NULL,  -- Otomaix ekip üyesinin adı
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Hesap etiketleri (VIP, Churn Riski, Pilot, Agency, Sorunlu)
CREATE TABLE IF NOT EXISTS crm.account_tags (
  account_id UUID NOT NULL,
  tag TEXT NOT NULL,
  added_by TEXT NOT NULL,
  added_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (account_id, tag)
);

-- İletişim geçmişi
CREATE TABLE IF NOT EXISTS crm.account_communications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID NOT NULL,
  channel TEXT NOT NULL,    -- email / telefon / toplanti / telegram
  direction TEXT NOT NULL,  -- inbound / outbound
  subject TEXT,
  note TEXT,
  created_by TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Aylık kullanım istatistikleri
CREATE TABLE IF NOT EXISTS crm.monthly_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID NOT NULL,
  brand_id UUID,
  year_month TEXT NOT NULL,           -- '2026-04'
  posts_generated INTEGER DEFAULT 0,
  posts_published INTEGER DEFAULT 0,
  credits_used INTEGER DEFAULT 0,
  storage_used_mb INTEGER DEFAULT 0,
  fal_cost_usd DECIMAL(10,4) DEFAULT 0,
  UNIQUE(account_id, brand_id, year_month)
);

-- Müşteri genel görünüm (social + crm schema birleşik)
CREATE OR REPLACE VIEW crm.customer_overview AS
SELECT
  a.id,
  a.email,
  a.name,
  a.plan_id,
  a.created_at,
  a.last_login_at,
  a.trial_ends_at,
  COALESCE(s.status, 'none') AS subscription_status,
  s.current_period_end,
  s.paddle_customer_id,
  COUNT(DISTINCT b.id) AS brand_count,
  ARRAY_AGG(DISTINCT t.tag) FILTER (WHERE t.tag IS NOT NULL) AS tags,
  COALESCE(SUM(mu.posts_generated), 0) AS total_posts_generated,
  COALESCE(SUM(mu.posts_published), 0) AS total_posts_published,
  MAX(mu.year_month) AS last_active_month
FROM social.accounts a
LEFT JOIN social.subscriptions s ON s.account_id = a.id
LEFT JOIN social.workspaces w ON w.account_id = a.id
LEFT JOIN social.brands b ON b.workspace_id = w.id AND b.is_active = true
LEFT JOIN crm.account_tags t ON t.account_id = a.id
LEFT JOIN crm.monthly_usage mu ON mu.account_id = a.id
GROUP BY a.id, a.email, a.name, a.plan_id, a.created_at, a.last_login_at,
         a.trial_ends_at, s.status, s.current_period_end, s.paddle_customer_id;

-- İndeksler
CREATE INDEX IF NOT EXISTS idx_crm_notes_account_id ON crm.account_notes(account_id);
CREATE INDEX IF NOT EXISTS idx_crm_tags_account_id ON crm.account_tags(account_id);
CREATE INDEX IF NOT EXISTS idx_crm_comms_account_id ON crm.account_communications(account_id);
CREATE INDEX IF NOT EXISTS idx_crm_usage_account_month ON crm.monthly_usage(account_id, year_month);
