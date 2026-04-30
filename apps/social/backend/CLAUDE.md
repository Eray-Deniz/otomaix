# Social Backend — CLAUDE.md

> **DRIFT KORUMA**
> Bu dosya YALNIZCA: proje yapısı, env, deploy, konvansiyonlar.
> Sprint logları → git commit.
> Kararlar → memory/decisions_*.md.
> Aktif iş → Tasks (oturum içi).
> Bu dosyaya changelog EKLENMEZ.

## Proje Amacı

Otomaix Social uygulamasının FastAPI backend'i. `api.otomaix.com`'da çalışır.
AI destekli sosyal medya içerik üretimi (görsel, carousel, video, özel gün, alıntı),
otomatik yayınlama, trend analizi, rakip analizi, RAG doküman bağlamı ve ödeme yönetimi.

## Proje Kılavuzları

- Genel mimari: `~/otomaix/docs/00-platform-mimari.md`
- Phase kılavuzları: `~/otomaix/docs/01-social-phase1.md` ... `04-social-phase4.md`
- CRM: `~/otomaix/docs/05-crm-admin.md`

## Deploy

- IP: 178.104.7.200
- Coolify servis adı: `otomaix-social-backend`
- URL: https://api.otomaix.com
- Dockerfile: multi-stage, `ffmpeg` apt paketi dahil

## Veritabanı

- PostgreSQL: `127.0.0.1:5433`, database: `otomaix`, schema: `social`
- Coolify container içinden: Docker network IP (`10.0.1.8:5432`)
- Redis: Coolify internal DNS hostname (localhost değil)

## Bağımlılıklar

- PostgreSQL (asyncpg) + Redis (hiredis)
- n8n: https://n8n.otomaix.com (otomasyon workflow'ları)
- fal.ai (görsel/video üretimi, webhook callback)
- Cloudflare R2 (medya depolama, assets.otomaix.com)
- Upload-Post.com (sosyal medya yayını, Agency JWT)
- Supabase Auth (JWT doğrulama, ES256/JWKS)
- Anthropic Claude (caption üretimi, analiz)
- Paddle (ödeme, webhook)

## .env Değişkenleri

```
DATABASE_URL=
REDIS_URL=redis://default:<pass>@<coolify-redis-hostname>:6379/0
SUPABASE_URL=https://sqplkkivtkfyozrvnybe.supabase.co
SUPABASE_SERVICE_KEY=
FAL_KEY=
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
R2_PUBLIC_URL=https://assets.otomaix.com
UPLOAD_POST_API_KEY=
ANTHROPIC_API_KEY=
INTERNAL_API_KEY=

# Opsiyonel
OPENAI_API_KEY=          # RAG chunk embedding
AZURE_TTS_KEY=           # Faceless video TTS
HEYGEN_API_KEY=          # AI Avatar
APIFY_API_KEY=           # Instagram rakip analizi
PADDLE_API_KEY=
PADDLE_WEBHOOK_SECRET=
POSTHOG_API_KEY=
SENTRY_DSN=
SERPER_API_KEY=          # Layer B Google Search
YOUTUBE_API_KEY=         # Layer A
EVDS_API_KEY=            # Layer A finans

# Media adapter model seçimi (env ile değiştirilebilir)
IMAGE_MODEL=flux-2-pro
VIDEO_MODEL=kling-v3-pro
IMAGE_TO_VIDEO_MODEL=kling-v25-turbo-pro
FACELESS_BACKGROUND_MODEL=wan-i2v-flash
IMAGE_EDIT_MODEL=nano-banana-2-edit
```

## Klasör Yapısı

```
app/
├── main.py                    # Lifespan, router kayıt, Sentry init
├── core/
│   ├── config.py              # Settings (env var'lar)
│   ├── database.py            # asyncpg pool (jsonb codec)
│   ├── redis.py               # Redis bağlantısı
│   ├── security.py            # JWT doğrulama (PyJWT + JWKS), X-Internal-Key
│   ├── cache.py               # get_cached / set_cached / invalidate
│   ├── rate_limit.py          # limiter(max_req, window_sec) dependency
│   ├── caption_generator.py   # Claude caption üretimi (3-tier prompt cache)
│   ├── prompt_builder.py      # Template-aware prompt building + PLATFORM_DEFAULTS
│   ├── templates_data.py      # Şablon kataloğu + startup validation
│   └── utils.py
├── models/
│   ├── schemas.py             # Pydantic request/response modelleri
│   └── templates.py           # Template Pydantic modelleri
├── routers/
│   ├── ai.py                  # suggest-ideas, analyze-website
│   ├── auth.py                # /auth/init (user+workspace+brands tek çağrı)
│   ├── autoposting.py         # config CRUD, toggle, upcoming
│   ├── avatar.py              # HeyGen stock/create/generate-ugc
│   ├── billing.py             # Paddle checkout/portal/plans + CRM webhook notify
│   ├── brands.py              # CRUD + brand_kit JSONB deep merge + logo/intro upload
│   ├── calendar.py            # posts by date range, schedule, holidays
│   ├── competitors.py         # CRUD + analiz + sentez raporu
│   ├── documents.py           # Marka doküman CRUD + RAG
│   ├── internal.py            # X-Internal-Key korumalı (n8n için)
│   ├── media_models.py        # /media-models/active (adapter registry)
│   ├── posts.py               # generate (image/carousel/special_day/quote) + publish
│   ├── product_documents.py   # Ürün doküman CRUD + RAG
│   ├── products.py            # Ürün/Hizmet CRUD + quota
│   ├── sectors.py             # Sektör listesi
│   ├── settings.py            # Kullanıcı ayarları
│   ├── social.py              # Upload-Post OAuth link + callback
│   ├── storage.py             # R2 pre-signed URL
│   ├── templates.py           # Şablon kataloğu API
│   ├── trends.py              # Layer A/B/C trend pipeline
│   └── webhooks.py            # fal.ai webhook + Paddle webhook
├── services/
│   ├── analytics.py           # PostHog server-side
│   ├── apify_client.py        # Instagram scraping
│   ├── avatar.py              # HeyGen entegrasyonu
│   ├── competitor_analyzer.py # Website + Instagram analizi
│   ├── document_processor.py  # PDF/Word/Excel çıkarma + chunking
│   ├── faceless_video.py      # Script + TTS + video pipeline
│   ├── fal_ai.py              # fal.ai async generation + webhook submit
│   ├── media_adapters.py      # Protocol-based adapter registry (5 modalite)
│   ├── media_processor.py     # Logo overlay + text overlay + brand processing
│   ├── pdf_renderer.py        # PDF rapor render
│   ├── sector_resolver.py     # Sektör çözümleme
│   ├── storage.py             # R2 upload/download/delete
│   ├── trend_analyzer.py      # Eski trend sistemi (deprecated)
│   ├── trends/                # Layer A/B/C trend pipeline
│   │   ├── layer_a.py         # Nightly sweep (Google Trends, RSS, Reddit, YouTube)
│   │   ├── layer_b.py         # Serper.dev + Claude Haiku derinleştirme
│   │   ├── layer_c.py         # Apify + Claude rapor
│   │   └── serper_client.py
│   └── upload_post.py         # Upload-Post.com yayınlama (tekli + carousel)
```

## Migrations (shared/db/migrations/)

001–011: Phase 1–4 (initial, autoposting, RAG, competitors, trends, subscriptions, trial, indexes)
012: CRM tables
013–018: Telegram, Upload-Post username, competitor status, publications, trend unique, autoposting cleanup
019–021: Sectors hierarchy + unified
022: posts.template_fields + posts.slides JSONB
023: brands.updated_at
024: posts.use_logo_overlay
025: posts.image_text_fields
026: brand_products + product_documents + product_document_chunks
027: posts.product_id FK

## Router Kayıt Sırası (main.py)

```
auth → ai → billing (+webhooks) → internal → autoposting → avatar →
brands → competitors → calendar → documents → media_models → posts →
product_documents → products → sectors → settings → storage → social →
templates → trends → webhooks
```

**Kural:** Statik path'ler (`/posts/stats/summary`, `/posts/scheduled-due`, `/posts/fail-stale`)
dinamik path'lerden (`/{post_id}`) ÖNCE deklare edilmeli. Aynı şekilde `/trends/personal` → `/{trend_index}`'den önce.

## n8n Workflow'ları

| Workflow | ID | Tetik |
|---|---|---|
| Auto Posting Scheduler | `Nz4651wCfBHP4G9l` | Her 30dk schedule |
| Telegram İçerik Onay | `D49KNE35cONz2APb` | Webhook |
| Telegram Onayla | `aQ8neGzs3PQp8DMl` | Webhook GET |
| Telegram Reddet | `9kp6bCFl0ys6TbVu` | Webhook GET |
| Türkiye Takvimi | `tTk1VroTh4AS8lxI` | Yıllık cron |
| CRM-1..6 | `reference_n8n_api.md`'de | Webhook + schedule |

## Konvansiyonlar

- **asyncpg jsonb codec:** `json.dumps()` + `$N::jsonb` cast KULLANMA — codec otomatik çalışır, dict/list'i doğrudan parametre geç
- **Sahiplik kontrolü:** `assert_brand_owned`, `assert_post_owned`, `assert_product_owned` → eşleşmezse 404 (403 değil)
- **ON DELETE CASCADE + R2 best-effort:** DB cascade güvence, R2 silme try/except
- **Startup validation:** `_validate_templates()` lifespan'de çalışır, kırılırsa uygulama başlamaz
- **Temperature:** Yaratıcı görevler (suggest_ideas, generate_script) → `temperature=1.0`; analitik → default
- **Caption modeli:** `claude-opus-4-6` (Opus 4.7 constraint-heavy görevde fabrication yapıyordu)
- **Vision overlay:** `claude-haiku-4-5-20251001` ile en boş köşe tespiti (~$0.001/görsel)
- **Overlay sırası:** fal.ai üretim → logo overlay → text overlay → R2 upload
- **Carousel text overlay:** Logo tüm slide'larda, text yalnızca ilk ve son slide'da
- **Carousel R2 path:** `{post_id}_slide_{N}_logo.jpg` (tekli: `{post_id}_logo.jpg`)
- **Stale-job sweeper:** `/internal/posts/fail-stale` — 10dk'dan eski `generating` post'ları `failed` yapar
- **n8n:** splitInBatches kullanma → Code node `$input.all().map()` pattern
- **Ürün/Hizmet:** Tek tablo `brand_products`, `type IN ('product','service')` discriminator
- **Media adapter:** Protocol tabanlı, env var ile model seçimi, yeni model = tek adapter sınıfı + registry satırı
