# Social Backend — CLAUDE.md

## Proje Amacı
Otomaix Social uygulamasının FastAPI backend'i. api.otomaix.com'da çalışır.

## Proje Kılavuzları (DEĞİŞTİRME)

Genel mimari: ~/otomaix/docs/00-platform-mimari.md
Phase 1: ~/otomaix/docs/01-social-phase1.md
Phase 2: ~/otomaix/docs/02-social-phase2.md
Phase 3: ~/otomaix/docs/03-social-phase3.md
Phase 4: ~/otomaix/docs/04-social-phase4.md
CRM: ~/otomaix/docs/05-crm-admin.md

Her session başında ~/otomaix/docs içerisindeki 00-platform-mimari.md dosyasını oku ve kaç numaralı fazda çalışıyorsan o faz numaralı md dosyasını da oku.

## VPS Bilgileri
- IP: 178.104.7.200
- Deploy: Coolify (servis adı: otomaix-social-backend)
- URL: https://api.otomaix.com

## Veritabanı
- Host: 127.0.0.1
- Port: 5433
- Database: otomaix
- User: otomaix

## Bağımlılıklar
- PostgreSQL: 127.0.0.1:5433
- Redis: internal
- n8n: https://n8n.otomaix.com
- fal.ai, Cloudflare R2, Upload-Post.com, Supabase Auth, Anthropic Claude

## Gerekli .env Değişkenleri
```
DATABASE_URL=
REDIS_URL=redis://localhost:6379
SUPABASE_URL=https://sqplkkivtkfyozrvnybe.supabase.co
SUPABASE_SERVICE_KEY=
FAL_KEY=
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
R2_PUBLIC_URL=https://assets.otomaix.com
UPLOAD_POST_API_KEY=
ANTHROPIC_API_KEY=   ✅ Coolify'a eklendi
INTERNAL_API_KEY=    ✅ .env'de mevcut — Coolify'a da ekle, sonra redeploy!
```

Not: Telegram bot token ve chat ID artık .env'de tutulmuyor.
Her müşteri kendi bot token'ını Otomatik Yayın wizard'ına girer →
`social.autoposting_configs.telegram_bot_token` / `telegram_chat_id` kolonlarında saklanır.

## Tamamlanan İşler

### Phase 1
- [x] FastAPI proje yapısı kuruldu
  - app/main.py, core/, routers/, models/, services/ oluşturuldu
  - Supabase JWT middleware (JWKS tabanlı)
  - Cloudflare R2 storage abstraction
  - fal.ai async generation + webhook
  - Upload-Post.com OAuth + publish
  - Dockerfile + .dockerignore
- [x] Coolify deploy yapılandırması ✅
- [x] Test scripti: `~/otomaix/shared/test_phase1.sh`

### Phase 2
- [x] Adım 1a — Brand Kit endpoint'leri (`app/routers/brands.py`)
  - `PATCH /brands/{brand_id}/kit` → brand_kit JSONB deep merge
  - `POST /brands/{brand_id}/logo` → light/dark logo upload → R2
  - `POST /brands/{brand_id}/intro-video` → video upload → R2

- [x] Adım 2a — İçerik üretim endpoint'leri (`app/routers/posts.py`)
  - `POST /posts/generate` → post oluştur + fal.ai tetikle
  - `POST /posts/{post_id}/regenerate` → yeniden üretim (JWT veya X-Internal-Key)
  - `POST /posts/{post_id}/publish` → yayınla (JWT)
  - `POST /posts/{post_id}/publish-now` → yayınla (X-Internal-Key, n8n için)
  - `GET /posts` → sayfalama + filtre

- [x] AI endpoint'leri (`app/routers/ai.py`)
  - `POST /ai/suggest-ideas` → Claude Haiku ile içerik fikir önerileri
  - `POST /ai/analyze-website` → Claude Haiku ile marka bilgisi çıkar
  - API key yoksa fallback öneriler döner

- [x] Takvim endpoint'leri (`app/routers/calendar.py`)
  - `GET /calendar/posts?brand_id&start&end`
  - `PATCH /calendar/schedule/{post_id}`
  - `GET /calendar/holidays?year`

- [x] Otomatik yayın endpoint'leri (`app/routers/autoposting.py`)
  - `GET /autoposting/config?brand_id`
  - `POST /autoposting/config` → telegram_bot_token + telegram_chat_id dahil
  - `POST /autoposting/toggle?brand_id`
  - `GET /autoposting/upcoming?brand_id`

- [x] Internal endpoint'leri (`app/routers/internal.py`) — X-Internal-Key korumalı, n8n için
  - `GET  /internal/autoposting/due` — timezone-aware, duplicate guard
  - `POST /internal/autoposting/trigger` — post üret + fal.ai tetikle
  - `GET  /internal/posts/{id}` — post detayı (JWT'siz)
  - `PATCH /internal/posts/{id}/status` — durum güncelle (rejected vb.)

- [x] OAuth Callback (`app/routers/social.py`)
  - `GET /social/oauth-link?brand_id&platform` → JWT link üret
  - `GET /social/callback?state&access_token&account_name`
    - State JWT doğrular, brand_social_accounts'a upsert yapar
    - Başarıda → `app.otomaix.com/marka-ayarlari?tab=sosyal&connected={platform}`

- [x] Servis kimlik doğrulaması (`app/core/security.py`)
  - `get_service_auth` dependency → X-Internal-Key header kontrolü
  - INTERNAL_API_KEY config'de tanımlı

- [x] n8n Auto Posting Scheduler (ID: `Nz4651wCfBHP4G9l`)
  - Her 30dk schedule trigger
  - GET /internal/autoposting/due → zamanı gelen configler
  - Her config için rastgele topic/type/category seçer
  - POST /internal/autoposting/trigger → post üretir
  - Telegram onayı gerekiyorsa → 3dk bekler → Telegram Onay webhook'unu tetikler

- [x] n8n Telegram İçerik Onay (ID: `D49KNE35cONz2APb`)
  - Webhook trigger: `POST /webhook/telegram-content-approval`
  - 2dk bekler (fal.ai üretimi) → post detayını alır
  - Müşterinin kendi bot token'ı ile Telegram'a mesaj gönderir (HTTP Request, statik credential yok)
  - Inline keyboard: ✅ Onayla / ❌ Reddet / 🔄 Yeniden Üret
  - 24sa callback bekler → karara göre publish/reject/regenerate

## Migrations
- `001_initial_social.sql` — temel şema ✅
- `002_autoposting.sql` — autoposting_configs + public_holidays ✅
- `003_social_account_unique.sql` — brand_social_accounts UNIQUE(brand_id, platform) ✅
- `004_telegram_chat_id.sql` — autoposting_configs.telegram_chat_id ✅
- `005_telegram_bot_token.sql` — autoposting_configs.telegram_bot_token ✅
- `006_document_rag.sql` — brand_documents.raw_text + brand_document_chunks (pgvector) ✅

## Router Kayıt Sırası (main.py)
```python
app.include_router(auth.router)
app.include_router(ai.router)
app.include_router(internal.router)
app.include_router(autoposting.router)
app.include_router(brands.router)
app.include_router(calendar.router)
app.include_router(documents.router)   # Phase 3 — eklendi
app.include_router(posts.router)
app.include_router(storage.router)
app.include_router(social.router)
app.include_router(webhooks.router)
```

## n8n Workflow'ları
- **Auto Posting Scheduler** — ID: `Nz4651wCfBHP4G9l` | `shared/n8n-workflows/auto-posting-scheduler.json`
- **Telegram İçerik Onay** — ID: `D49KNE35cONz2APb` | `shared/n8n-workflows/telegram-content-approval.json`
- Her ikisi de n8n'de mevcut ama **inactive** — aktif etmek için aşağıya bak.

## requirements.txt (önemli eklemeler)
```
anthropic==0.40.0
python-multipart==0.0.12
pypdf==4.3.1           # Phase 3 — PDF metin çıkarma
python-docx==1.1.2     # Phase 3 — Word metin çıkarma
openpyxl==3.1.5        # Phase 3 — Excel metin çıkarma
openai==1.57.0         # Phase 3 — RAG chunk embedding (opsiyonel, OPENAI_API_KEY gerekli)
```

## Phase 3

### Tamamlanan
- [x] Adım 1a — Doküman RAG Backend
  - `app/services/document_processor.py` → PDF/Word/Excel metin çıkarma + chunking
  - `app/routers/documents.py` → POST /documents, GET /documents, DELETE /documents/{id}
  - `shared/db/migrations/006_document_rag.sql` → brand_document_chunks + raw_text kolonu
  - config.py: OPENAI_API_KEY opsiyonel eklendi (varsa vektör embedding aktif olur)

- [x] Adım 1b — RAG entegrasyonu (posts.py)
  - `_build_prompt_with_rag()` helper → doküman bağlamını prompt'a enjekte eder
  - `get_document_context()` → küçük dokümanlar raw_text, büyükler chunk retrieval
  - document_ids artık posts tablosuna kaydediliyor

- [x] Adım 2a — Türkçe Faceless Video backend pipeline
  - `app/services/faceless_video.py`
    - `generate_script()` → Claude Haiku ile Türkçe script (30-60 sn, ~75-150 kelime)
    - `text_to_speech()` → Azure TTS REST API → R2'ye mp3 (AZURE_TTS_KEY yoksa atlanır)
    - `generate_background_video()` → fal-ai/hunyuan-video (async, webhook)
    - `run_faceless_video_pipeline()` → tam pipeline, post kaydı oluşturur
  - `POST /posts/generate-faceless-video` → brand_id, prompt, voice, aspect_ratio
  - `GET /posts/voices/turkish` → sabit Türkçe ses listesi
  - `POST /ai/generate-script` → sadece script üretimi (frontend'den çağrılır)
  - `config.py`: AZURE_TTS_KEY + AZURE_TTS_REGION eklendi

### Bir Sonraki Adım — Phase 3 Adım 3a
**AI Avatar backend (HeyGen entegrasyonu):**
- `app/services/avatar.py` oluştur
- `POST /avatar/create` → kullanıcı fotoğrafından HeyGen avatar
- `GET /avatar/stock` → hazır HeyGen avatar listesi
- `POST /posts/generate-ugc` → avatar + script → UGC video
- Yeni .env: `HEYGEN_API_KEY`
