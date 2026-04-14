-- Migration: 018_drop_autoposting_telegram_cols.sql
-- B-3: Telegram ayarları workspace seviyesine taşındı (commit 58af268).
-- autoposting_configs'teki eski telegram kolonları artık ölü.
-- internal.py `w.telegram_bot_token`/`w.telegram_chat_id` kullanıyor (workspaces JOIN),
-- autoposting.py ve frontend hiçbir yerde bu iki kolonu okumuyor. Güvenli drop.

ALTER TABLE social.autoposting_configs
  DROP COLUMN IF EXISTS telegram_bot_token,
  DROP COLUMN IF EXISTS telegram_chat_id;
