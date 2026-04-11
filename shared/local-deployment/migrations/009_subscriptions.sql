-- Migration: 009_subscriptions.sql
-- Paddle abonelik yönetimi tabloları

CREATE TABLE IF NOT EXISTS social.subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES social.accounts(id) ON DELETE CASCADE,
  paddle_subscription_id TEXT UNIQUE,
  paddle_customer_id TEXT,
  plan_id TEXT NOT NULL DEFAULT 'starter',
  status TEXT NOT NULL DEFAULT 'active',  -- active | cancelled | past_due | trialing
  current_period_end TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_account_id
  ON social.subscriptions(account_id);

CREATE INDEX IF NOT EXISTS idx_subscriptions_paddle_sub_id
  ON social.subscriptions(paddle_subscription_id);

-- Plan limitleri
CREATE TABLE IF NOT EXISTS social.plan_limits (
  plan_id TEXT PRIMARY KEY,
  max_brands INTEGER,           -- NULL = sınırsız
  max_posts_per_month INTEGER,  -- NULL = sınırsız
  max_storage_gb INTEGER,
  can_use_video BOOLEAN DEFAULT false,
  can_use_avatar BOOLEAN DEFAULT false,
  price_try INTEGER NOT NULL DEFAULT 0
);

INSERT INTO social.plan_limits (plan_id, max_brands, max_posts_per_month, max_storage_gb, can_use_video, can_use_avatar, price_try)
VALUES
  ('free',     1,    10,   1,  false, false,    0),
  ('starter',  1,    50,   1,  false, false,  499),
  ('pro',      3,   200,   5,  true,  false,  999),
  ('business', 10,  NULL,  20, true,  true,  2499),
  ('agency',   NULL, NULL, 50, true,  true,  4999)
ON CONFLICT (plan_id) DO NOTHING;

-- accounts.plan_id zaten var, indeks ekle
CREATE INDEX IF NOT EXISTS idx_accounts_plan_id ON social.accounts(plan_id);
