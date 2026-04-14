-- Migration 014: Add upload_post_username to brands
-- Each brand corresponds to one Upload-Post.com user profile.
-- Format: "brand_<first-8-chars-of-uuid>" (e.g. "brand_89e7d966")

ALTER TABLE social.brands
    ADD COLUMN IF NOT EXISTS upload_post_username TEXT;

CREATE INDEX IF NOT EXISTS idx_brands_upload_post_username
    ON social.brands(upload_post_username)
    WHERE upload_post_username IS NOT NULL;
