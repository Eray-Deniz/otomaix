-- Migration 002: Auto posting configs + public holidays
-- Run: psql -h 127.0.0.1 -p 5433 -U otomaix -d otomaix -f 002_autoposting.sql

CREATE TABLE IF NOT EXISTS social.autoposting_configs (
  id                 UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id           UUID        UNIQUE REFERENCES social.brands(id) ON DELETE CASCADE,
  is_enabled         BOOLEAN     DEFAULT false,
  frequency          TEXT,
  time_slots         JSONB       DEFAULT '[]',
  content_types      TEXT[]      DEFAULT '{}',
  content_categories TEXT[]      DEFAULT '{}',
  topics             TEXT[]      DEFAULT '{}',
  platforms          TEXT[]      DEFAULT '{}',
  telegram_approval  BOOLEAN     DEFAULT false,
  created_at         TIMESTAMPTZ DEFAULT now(),
  updated_at         TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS social.public_holidays (
  id       UUID  PRIMARY KEY DEFAULT gen_random_uuid(),
  year     INT   NOT NULL,
  date     DATE  NOT NULL,
  name_tr  TEXT  NOT NULL,
  name_en  TEXT,
  category TEXT  DEFAULT 'national',
  UNIQUE (year, date)
);

INSERT INTO social.public_holidays (year, date, name_tr, name_en, category) VALUES
  (2026,'2026-01-01','Yılbaşı','New Year''s Day','national'),
  (2026,'2026-04-23','Ulusal Egemenlik ve Çocuk Bayramı','National Sovereignty Day','national'),
  (2026,'2026-05-01','Emek ve Dayanışma Günü','Labour Day','national'),
  (2026,'2026-05-19','Atatürk''ü Anma, Gençlik ve Spor Bayramı','Youth Day','national'),
  (2026,'2026-07-15','Demokrasi ve Millî Birlik Günü','Democracy Day','national'),
  (2026,'2026-08-30','Zafer Bayramı','Victory Day','national'),
  (2026,'2026-10-29','Cumhuriyet Bayramı','Republic Day','national'),
  (2026,'2026-02-14','Sevgililer Günü','Valentine''s Day','commercial'),
  (2026,'2026-03-08','Dünya Kadınlar Günü','International Women''s Day','commercial'),
  (2026,'2026-11-27','Black Friday','Black Friday','commercial')
ON CONFLICT (year, date) DO NOTHING;
