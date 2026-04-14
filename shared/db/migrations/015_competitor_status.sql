-- Migration: 015_competitor_status.sql
-- Rakip analizi asenkron duruma (B-5 fix): status + error_message sütunları.
-- Mevcut satırlar 'ready' kabul edilir (zaten senkron tamamlanmışlardı).

ALTER TABLE social.competitor_analyses
  ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'ready',
  ADD COLUMN IF NOT EXISTS error_message TEXT;

-- Geçerli değerler: 'analyzing' | 'ready' | 'failed'
-- analyzing: background task çalışıyor, analysis_data henüz NULL
-- ready: analiz tamamlandı, analysis_data dolu
-- failed: analiz hata verdi, error_message doldu

CREATE INDEX IF NOT EXISTS idx_competitor_analyses_status
  ON social.competitor_analyses(status)
  WHERE status = 'analyzing';
