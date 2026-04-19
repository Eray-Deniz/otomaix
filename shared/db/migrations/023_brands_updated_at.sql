-- Migration 023: add updated_at column + trigger to social.brands
-- Fixes: 500 error on logo/intro video uploads (brands.py:187, brands.py:215)
-- Root cause: UPDATE queries reference updated_at but column never existed on social.brands.

ALTER TABLE social.brands
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();

DROP TRIGGER IF EXISTS brands_updated_at ON social.brands;
CREATE TRIGGER brands_updated_at
    BEFORE UPDATE ON social.brands
    FOR EACH ROW EXECUTE FUNCTION social.set_updated_at();
