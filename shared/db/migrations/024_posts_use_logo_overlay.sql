-- Phase 8 Sprint 1 Part 2: Per-post logo overlay override
-- NULL = marka default'una uy (brand_kit.logo_overlay.enabled)
-- true  = bu post için logo BAS (marka default'unu override et)
-- false = bu post için logo BASMA (marka default'unu override et)

ALTER TABLE social.posts
  ADD COLUMN IF NOT EXISTS use_logo_overlay BOOLEAN DEFAULT NULL;
