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
    failures TEXT;
BEGIN
    -- Kimlik ADA değil TAM TANIMA bağlıdır. Ölçüldü (final review tur 3): ada
    -- göre eşleyen bir kontrol, aynı ADDA ama BAŞKA TABLOYA / başka kolona /
    -- başka predicate'e kurulmuş GEÇERLİ bir indeksi kabul eder. O durumda
    -- `CREATE INDEX CONCURRENTLY IF NOT EXISTS` adı görüp DDL'i ATLAR ve
    -- migration "başarılı" der; beklenen indeks hiç var olmaz. Benzersiz bir
    -- taklit ayrıca meşru yazımları REDDEDER.
    WITH expected(name, want) AS (
        VALUES
            ('idx_posts_brand_created',
             'CREATE INDEX idx_posts_brand_created ON social.posts'
             ' USING btree (brand_id, created_at DESC)|f|live'),
            ('idx_posts_brand_scheduled',
             'CREATE INDEX idx_posts_brand_scheduled ON social.posts'
             ' USING btree (brand_id, scheduled_at)'
             ' WHERE (scheduled_at IS NOT NULL)|f|live'),
            ('idx_posts_brand_published',
             'CREATE INDEX idx_posts_brand_published ON social.posts'
             ' USING btree (brand_id, published_at DESC)'
             ' WHERE (published_at IS NOT NULL)|f|live'),
            ('idx_trend_cache_fetched',
             'CREATE INDEX idx_trend_cache_fetched ON social.trend_cache'
             ' USING btree (fetched_at DESC)|f|live')
    ),
    observed(name, got) AS (
        SELECT c.relname,
               format('%s|%s|%s',
                      pg_get_indexdef(i.indexrelid),
                      i.indisunique,
                      CASE WHEN i.indisvalid AND i.indisready AND i.indislive
                           THEN 'live' ELSE 'BROKEN' END)
          FROM pg_index i
          JOIN pg_class c ON c.oid = i.indexrelid
          JOIN pg_namespace n ON n.oid = c.relnamespace
         WHERE n.nspname = 'social'
    )
    SELECT string_agg(
               format('%s -> beklenen [%s] · gorulen [%s]',
                      e.name, e.want, coalesce(o.got, '<indeks yok>')),
               E'\n  - ' ORDER BY e.name)
      INTO failures
      FROM expected e
      LEFT JOIN observed o ON o.name = e.name
     WHERE o.got IS DISTINCT FROM e.want;

    IF failures IS NOT NULL THEN
        RAISE EXCEPTION 'migration 011 dogrulamasi BASARISIZ:%',
            E'\n  - ' || failures
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Ayni ADDA yanlis tanimli ya da yarim kalmis (invalid) '
                         'bir indeks var. CONCURRENTLY + IF NOT EXISTS o adi '
                         'gorup DDL i ATLAR, yani yeniden kosum ONARMAZ. Elle: '
                         'DROP INDEX CONCURRENTLY <ad>; sonra migration i '
                         'tekrar uygulayin.';
    END IF;
END
$verify011$;
