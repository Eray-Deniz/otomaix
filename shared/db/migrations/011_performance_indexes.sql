-- 011: Performance indexes
-- Takvim sorguları, içerik kütüphanesi ve RAG chunk erişimi için bileşik index'ler.
-- CONCURRENTLY: production'da tablo kilitlemeden oluşturulur.

-- İçerik kütüphanesi: brand bazlı liste (created_at DESC)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_posts_brand_created
    ON social.posts (brand_id, created_at DESC);

-- Takvim görünümü: brand bazlı tarih aralığı sorguları
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_posts_brand_scheduled
    ON social.posts (brand_id, scheduled_at)
    WHERE scheduled_at IS NOT NULL;

-- Otomatik yayın: son yayın zamanı sorgulama
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_posts_brand_published
    ON social.posts (brand_id, published_at DESC)
    WHERE published_at IS NOT NULL;

-- RAG chunk erişimi: brand bazlı chunk listesi
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_doc_chunks_brand
    ON social.brand_document_chunks (brand_id);

-- Trend cache: son güncelleme zamanı
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trend_cache_updated
    ON social.trend_cache (updated_at DESC);
