-- Migration 003: Add UNIQUE constraint on brand_social_accounts(brand_id, platform)
-- Required for ON CONFLICT upsert in /social/callback OAuth flow.
-- If duplicate rows already exist, this removes them first (keeps the most recently connected).

-- 1. Remove duplicate rows (keep latest connected_at per brand+platform)
DELETE FROM social.brand_social_accounts a
USING social.brand_social_accounts b
WHERE a.id <> b.id
  AND a.brand_id = b.brand_id
  AND a.platform = b.platform
  AND a.connected_at < b.connected_at;

-- 2. Add unique constraint
ALTER TABLE social.brand_social_accounts
    ADD CONSTRAINT uq_brand_social_accounts_brand_platform
    UNIQUE (brand_id, platform);
