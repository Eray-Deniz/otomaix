-- Migration 005: Add telegram_bot_token to autoposting_configs
-- Her müşteri kendi Telegram botunu kullanır.
-- telegram_chat_id zaten 004'te eklendi.

ALTER TABLE social.autoposting_configs
    ADD COLUMN IF NOT EXISTS telegram_bot_token TEXT;
