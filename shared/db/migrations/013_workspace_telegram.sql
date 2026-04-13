-- Migration: 013_workspace_telegram.sql
-- Telegram bilgilerini autoposting_configs'ten workspaces'e taşı

-- 1. workspaces tablosuna Telegram kolonları ekle
ALTER TABLE social.workspaces
    ADD COLUMN IF NOT EXISTS telegram_bot_token TEXT,
    ADD COLUMN IF NOT EXISTS telegram_chat_id TEXT;

-- 2. Mevcut autoposting_configs verilerini workspace'e taşı
--    (brand → workspace üzerinden eşleştir, ilk bulunan token geçerli)
UPDATE social.workspaces w
SET
    telegram_bot_token = subq.telegram_bot_token,
    telegram_chat_id   = subq.telegram_chat_id
FROM (
    SELECT DISTINCT ON (b.workspace_id)
        b.workspace_id,
        ac.telegram_bot_token,
        ac.telegram_chat_id
    FROM social.autoposting_configs ac
    JOIN social.brands b ON b.id = ac.brand_id
    WHERE ac.telegram_bot_token IS NOT NULL
       OR ac.telegram_chat_id IS NOT NULL
    ORDER BY b.workspace_id, ac.updated_at DESC
) subq
WHERE w.id = subq.workspace_id;

-- 3. autoposting_configs'ten Telegram kolonlarını kaldır
ALTER TABLE social.autoposting_configs
    DROP COLUMN IF EXISTS telegram_approval,
    DROP COLUMN IF EXISTS telegram_bot_token,
    DROP COLUMN IF EXISTS telegram_chat_id;
