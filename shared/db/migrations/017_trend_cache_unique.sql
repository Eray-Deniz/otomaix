-- Migration: 017_trend_cache_unique.sql
-- B-6: trend_cache.sector üzerinde UNIQUE constraint — UPSERT için gerekli.
-- Mevcut duplicate satırlar önce dedup edilmeli (her sector için en yeni row korunur).

BEGIN;

DELETE FROM social.trend_cache a
USING social.trend_cache b
WHERE a.sector = b.sector
  AND a.fetched_at < b.fetched_at;

ALTER TABLE social.trend_cache
  ADD CONSTRAINT trend_cache_sector_unique UNIQUE (sector);

COMMIT;
