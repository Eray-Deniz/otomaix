# AGENTS.md

> Bu dosyanın marker'lı bloğu `/sync-agents-md` komutu tarafından
> Codex'in CLAUDE.md damıtması ile üretilir. Marker dışına manuel
> içerik ekleyebilirsin — korunur.

<!-- BEGIN CODEX-DISTILLED -->
> Bu icerik Codex CLI icin /root/otomaix/apps/social/backend/CLAUDE.md'den damitilmistir.

## Proje Amacı

Otomaix Social backend, FastAPI tabanlıdır ve `api.otomaix.com` üzerinde çalışır.

Kapsam:

- AI destekli sosyal medya içerik üretimi: görsel, carousel, video, özel gün, alıntı
- Otomatik yayınlama
- Trend analizi
- Rakip analizi
- RAG doküman bağlamı
- Ödeme yönetimi

## Proje Kılavuzları

Mimari, karar, vendor ve geçmiş bilgi için önce `/root/otomaix-brain/index.md` kontrol edilir. Aşağıdaki eski dokümanlar yalnızca vault'ta bilgi yoksa veya tarihsel bağlam gerekiyorsa kullanılır.

- Genel mimari: `~/otomaix/docs/00-platform-mimari.md`
- Phase kılavuzları: `~/otomaix/docs/01-social-phase1.md` ... `04-social-phase4.md`
- CRM: `~/otomaix/docs/05-crm-admin.md`

## Deploy

- Sunucu IP: `178.104.7.200`
- Coolify servis adı: `otomaix-social-backend`
- Public URL: `https://api.otomaix.com`
- Dockerfile multi-stage yapıdadır.
- Docker image içinde `ffmpeg` apt paketi bulunur.

## Veritabanı ve Altyapı

- PostgreSQL:
  - Host: `127.0.0.1:5433`
  - Database: `otomaix`
  - Schema: `social`
- Coolify container içinden PostgreSQL bağlantısı Docker network IP üzerinden yapılır: `10.0.1.8:5432`
- Redis için Coolify internal DNS hostname kullanılmalıdır; `localhost` kullanılmaz.

## Ana Bağımlılıklar

- PostgreSQL `asyncpg`
- Redis `hiredis`
- n8n: `https://n8n.otomaix.com`
- fal.ai: görsel/video üretimi ve webhook callback
- Cloudflare R2: medya depolama, `assets.otomaix.com`
- Upload-Post.com: sosyal medya yayını, Agency JWT
- Supabase Auth: JWT doğrulama, ES256/JWKS
- Anthropic Claude: caption üretimi ve analiz
- Paddle: ödeme ve webhook

## Önemli Env Değişkenleri

Zorunlu/temel değişkenler:

- `DATABASE_URL`
- `REDIS_URL`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`
- `FAL_KEY`
- `R2_ACCOUNT_ID`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_BUCKET_NAME`
- `R2_PUBLIC_URL`: `https://assets.otomaix.com`
- `UPLOAD_POST_API_KEY`
- `ANTHROPIC_API_KEY`
- `INTERNAL_API_KEY`

Önemli örnek değerler:

- `REDIS_URL`: `redis://default:<pass>@<coolify-redis-hostname>:6379/0`
- `SUPABASE_URL`: `https://sqplkkivtkfyozrvnybe.supabase.co`

Opsiyonel entegrasyonlar:

- `OPENAI_API_KEY`: RAG chunk embedding
- `ELEVENLABS_KEY`: kısa video TTS
- `HEYGEN_API_KEY`: AI avatar
- `APIFY_API_KEY`: Instagram rakip analizi
- `PADDLE_API_KEY`
- `PADDLE_WEBHOOK_SECRET`
- `POSTHOG_API_KEY`
- `SENTRY_DSN`
- `SERPER_API_KEY`: Layer B Google Search
- `YOUTUBE_API_KEY`: Layer A
- `EVDS_API_KEY`: Layer A finans

Media adapter model seçimi env ile yapılır:

- `IMAGE_MODEL=flux-2-pro`
- `VIDEO_MODEL=kling-v3-pro`
- `IMAGE_TO_VIDEO_MODEL=kling-v25-turbo-pro`
- `SHORT_VIDEO_BACKGROUND_MODEL=wan-i2v-flash`
- `IMAGE_EDIT_MODEL=nano-banana-2-edit`

## Klasör Yapısı

Ana uygulama `app/` altındadır.

Önemli çekirdek modüller:

- `app/main.py`: lifespan, router kayıtları, Sentry init
- `app/core/config.py`: settings ve env değişkenleri
- `app/core/database.py`: asyncpg pool ve jsonb codec
- `app/core/redis.py`: Redis bağlantısı
- `app/core/security.py`: JWT doğrulama ve `X-Internal-Key`
- `app/core/cache.py`: cache helperları
- `app/core/rate_limit.py`: rate limit dependency
- `app/core/caption_generator.py`: Claude caption üretimi
- `app/core/prompt_builder.py`: template-aware prompt building
- `app/core/templates_data.py`: şablon kataloğu ve startup validation

Router’lar `app/routers/` altında, servisler `app/services/` altında tutulur.

## Migration Kuralları

Migration dosyaları `shared/db/migrations/` altında numaralandırılır.

Mevcut önemli migration aralıkları:

- `001–011`: Phase 1–4
- `012`: CRM tabloları
- `013–018`: Telegram, Upload-Post username, competitor status, publications, trend unique, autoposting cleanup
- `019–021`: sectors hierarchy ve unified yapı
- `022`: `posts.template_fields` ve `posts.slides`
- `023`: `brands.updated_at`
- `024`: `posts.use_logo_overlay`
- `025`: `posts.image_text_fields`
- `026`: `brand_products`, `product_documents`, `product_document_chunks`
- `027`: `posts.product_id` FK

## Router Kayıt Sırası

`main.py` içinde router kayıt sırası:

`auth → ai → billing (+webhooks) → internal → autoposting → avatar → brands → competitors → calendar → documents → media_models → posts → product_documents → products → sectors → settings → storage → social → templates → trends → webhooks`

Statik path’ler dinamik path’lerden önce declare edilmelidir.

Örnekler:

- `/posts/stats/summary`, `/posts/scheduled-due`, `/posts/fail-stale` path’leri `/{post_id}` öncesinde olmalı.
- `/trends/personal`, `/{trend_index}` öncesinde olmalı.

## n8n Workflow Bilgileri

Önemli workflow’lar:

- Auto Posting Scheduler: `Nz4651wCfBHP4G9l`, her 30 dakikada schedule
- Telegram İçerik Onay: `D49KNE35cONz2APb`, webhook
- Telegram Onayla: `aQ8neGzs3PQp8DMl`, webhook GET
- Telegram Reddet: `9kp6bCFl0ys6TbVu`, webhook GET
- Türkiye Takvimi: `tTk1VroTh4AS8lxI`, yıllık cron
- CRM workflow’ları `reference_n8n_api.md` içinde belgelenir.

n8n workflow yazarken `splitInBatches` kullanılmaz. Code node içinde `$input.all().map()` pattern’i tercih edilir.

## Kod Konvansiyonları

- `asyncpg` jsonb codec otomatik çalışır.
- JSONB alanlara dict/list doğrudan parametre geçilmelidir.
- `json.dumps()` + `$N::jsonb` cast kullanılmamalıdır.
- Sahiplik kontrollerinde şu helper’lar kullanılır:
  - `assert_brand_owned`
  - `assert_post_owned`
  - `assert_product_owned`
- Sahiplik uyuşmazlığında `404` dönülür, `403` değil.
- DB tarafında `ON DELETE CASCADE` güvence olarak kullanılır.
- R2 silmeleri best-effort yapılır; `try/except` ile ele alınır.
- `_validate_templates()` lifespan sırasında çalışır; hata varsa uygulama başlamamalıdır.
- Yaratıcı görevlerde `temperature=1.0` kullanılır.
- Analitik görevlerde varsayılan temperature tercih edilir.

## AI ve Medya Üretim Kuralları

- Caption modeli: `claude-opus-4-6`
- Vision overlay için model: `claude-haiku-4-5-20251001`
- Vision overlay görevi: görselde en boş köşeyi tespit etmek.
- Overlay sırası:
  1. fal.ai üretim
  2. logo overlay
  3. text overlay
  4. R2 upload
- Carousel’de logo tüm slide’larda uygulanır.
- Carousel’de text overlay yalnızca ilk ve son slide’da uygulanır.
- Carousel R2 path formatı: `{post_id}_slide_{N}_logo.jpg`
- Tekli görsel R2 path formatı: `{post_id}_logo.jpg`

## Background Job ve Stale Durum Kuralları

- Stale-job sweeper endpoint’i: `/internal/posts/fail-stale`
- 10 dakikadan eski `generating` durumundaki post’lar `failed` yapılır.

## Domain Kuralları

- Ürün ve hizmetler tek tabloda tutulur: `brand_products`
- Ayrım için `type IN ('product','service')` discriminator kullanılır.
- Media adapter sistemi Protocol tabanlıdır.
- Model seçimi env var üzerinden yapılır.
- Yeni media modeli eklemek için tek adapter sınıfı ve registry satırı ekleme pattern’i izlenir.

## Dokümantasyon Hijyeni

Bu proje talimat dosyalarına yalnızca şu tür bilgiler eklenmelidir:

- Proje yapısı
- Env bilgisi
- Deploy bilgisi
- Konvansiyonlar

Şunlar eklenmemelidir:

- Sprint logları
- Aktif iş kayıtları
- Karar geçmişi
- Changelog kayıtları

Kalıcı kayıt yerleri:

- Kararlar: `/root/otomaix-brain/decisions/`
- Değişiklik/query/ingest/lint kayıtları: `/root/otomaix-brain/log.md`
- Değerli sentez ve araştırma sonuçları: `/root/otomaix-brain/research/`
<!-- END CODEX-DISTILLED -->
