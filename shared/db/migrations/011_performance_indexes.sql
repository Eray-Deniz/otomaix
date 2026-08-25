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

-- RAG chunk erişimi: brand bazlı chunk listesi (tablo mevcutsa)
-- CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_doc_chunks_brand
--     ON social.brand_document_chunks (brand_id);

-- Trend cache: son getirme zamanı (fetched_at)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_trend_cache_fetched
    ON social.trend_cache (fetched_at DESC);

-- ---------------------------------------------------------------------------
-- YENİDEN KOŞUM GÜVENLİĞİ (final review, 2026-08-25)
-- ---------------------------------------------------------------------------
-- Bu dosya, tek transaction'a SARILAMAYAN tek migration'dır: `CREATE INDEX
-- CONCURRENTLY` transaction bloğunda koşamaz. Bedeli yalnız "atomik değil"
-- DEĞİLDİR — sessiz bir kalıntı sınıfı da doğurur:
--
--   Eşzamanlı indeks kurulumu yarıda kesilirse (iptal, çakışma, çökme)
--   PostgreSQL katalogda GEÇERSİZ (`indisvalid=false`) bir indeks bırakır.
--   Sonraki koşumda `IF NOT EXISTS` o ADI görüp DDL'i ATLAR — yani migration
--   BAŞARILI biter, indeks ise hâlâ kullanılamaz durumdadır. Planlayıcı onu
--   kullanmaz; semptom "sorgu yavaşladı"dır ve hiçbir hata görünmez.
--
-- Bu blok o sessizliği kapatır: beklenen indekslerin varlığını VE fiilen
-- uygulanır durumda olduğunu denetler. Onarım OTOMATİK YAPILMAZ — geçersiz bir
-- indeksi düşürmek üretimde bilinçli bir karardır; blok ne yapılacağını
-- söyleyerek DURUR (fail-closed).
--
-- ELLE UYGULARKEN: psql'i `-v ON_ERROR_STOP=1` ile çağırın.

DO $verify011$
DECLARE
    broken TEXT;
    missing TEXT;
BEGIN
    WITH expected(name) AS (
        VALUES ('idx_posts_brand_created'),
               ('idx_posts_brand_scheduled'),
               ('idx_posts_brand_published'),
               ('idx_trend_cache_fetched')
    ),
    actual AS (
        SELECT c.relname AS name,
               i.indisvalid AND i.indisready AND i.indislive AS usable
          FROM pg_index i
          JOIN pg_class c ON c.oid = i.indexrelid
          JOIN pg_namespace n ON n.oid = c.relnamespace
         WHERE n.nspname = 'social'
    )
    SELECT string_agg(e.name, ', ' ORDER BY e.name)
      INTO missing
      FROM expected e
      LEFT JOIN actual a ON a.name = e.name
     WHERE a.name IS NULL;

    WITH expected(name) AS (
        VALUES ('idx_posts_brand_created'),
               ('idx_posts_brand_scheduled'),
               ('idx_posts_brand_published'),
               ('idx_trend_cache_fetched')
    ),
    actual AS (
        SELECT c.relname AS name,
               i.indisvalid AND i.indisready AND i.indislive AS usable
          FROM pg_index i
          JOIN pg_class c ON c.oid = i.indexrelid
          JOIN pg_namespace n ON n.oid = c.relnamespace
         WHERE n.nspname = 'social'
    )
    SELECT string_agg(e.name, ', ' ORDER BY e.name)
      INTO broken
      FROM expected e
      JOIN actual a ON a.name = e.name
     WHERE NOT a.usable;

    IF missing IS NOT NULL THEN
        RAISE EXCEPTION 'migration 011 dogrulamasi BASARISIZ: eksik indeks: %',
            missing
            USING ERRCODE = 'integrity_constraint_violation';
    END IF;

    IF broken IS NOT NULL THEN
        RAISE EXCEPTION 'migration 011 dogrulamasi BASARISIZ: GECERSIZ indeks: %',
            broken
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Yarim kalmis CONCURRENTLY kurulumunun kalintisi. '
                         'IF NOT EXISTS bu adi gorup DDL i ATLAR, yani yeniden '
                         'kosum onu ONARMAZ. Elle: DROP INDEX CONCURRENTLY '
                         '<ad>; sonra migration i tekrar uygulayin.';
    END IF;
END
$verify011$;
