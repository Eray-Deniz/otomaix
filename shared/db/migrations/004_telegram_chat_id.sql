-- Migration 004: Add telegram_chat_id to autoposting_configs
-- Required for Telegram approval workflow to know which chat to send messages to.

ALTER TABLE social.autoposting_configs
    ADD COLUMN IF NOT EXISTS telegram_chat_id TEXT;
