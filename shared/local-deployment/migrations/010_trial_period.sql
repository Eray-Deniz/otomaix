-- Migration: 010_trial_period.sql
-- Hesaplara 14 günlük deneme süresi alanı ekle

ALTER TABLE social.accounts
  ADD COLUMN IF NOT EXISTS trial_ends_at TIMESTAMPTZ
    DEFAULT (now() + INTERVAL '14 days');

-- Mevcut hesaplar için created_at + 14 gün olarak set et
UPDATE social.accounts
SET trial_ends_at = created_at + INTERVAL '14 days'
WHERE trial_ends_at IS NULL;
