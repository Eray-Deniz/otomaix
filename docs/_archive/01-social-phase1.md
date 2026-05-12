# 01 — Social Uygulaması: Phase 1 — Altyapı Kurulumu
> **Süre:** Ay 1–2  
> **Ön koşul:** `00-platform-mimari.md` okunmuş olmalı  
> **Hedef:** Çalışan bir iskelet — auth, veritabanı, storage, ilk API endpoint'leri ve boş frontend

---

## Bu Phase'de Ne Yapılıyor?

Phase 1 sonunda elimizde şunlar olacak:
- VPS'te klasör yapısı kurulu
- PostgreSQL şeması oluşturulmuş (temel tablolar)
- FastAPI backend çalışıyor, Supabase Auth doğruluyor
- Cloudflare R2 bağlı, dosya upload/download çalışıyor
- fal.ai entegrasyonu var, test görsel üretilebiliyor
- Upload-Post.com bağlı, test yayın yapılabiliyor
- Next.js frontend iskelet çalışıyor, login sayfası var
- Coolify'da tüm servisler deploy edilmiş

---

## Klasör Yapısı — Phase 1 Sonunda

```
/home/eray/otomaix/
├── apps/
│   └── social/
│       ├── frontend/          # Next.js uygulaması
│       │   ├── CLAUDE.md
│       │   ├── app/
│       │   ├── components/
│       │   ├── lib/
│       │   └── .env.local
│       └── backend/           # FastAPI uygulaması
│           ├── CLAUDE.md
│           ├── app/
│           │   ├── main.py
│           │   ├── routers/
│           │   ├── models/
│           │   ├── services/
│           │   └── core/
│           ├── requirements.txt
│           └── .env
├── shared/
│   ├── db/
│   │   └── migrations/
│   │       └── 001_initial.sql
│   └── n8n-workflows/
└── docs/
```

---

## Adım 1: VPS Klasör Yapısını Oluştur

**Ne yapılıyor:** VPS üzerinde temel dizin yapısını oluşturuyoruz. Bu bir kerelik işlemdir.

**Claude Code session:** Herhangi bir dizinde çalışabilir.

```bash
# Terminal'de (Claude Code olmadan, direkt SSH ile yap)
ssh eray@178.104.7.200
mkdir -p ~/otomaix/apps/social/frontend
mkdir -p ~/otomaix/apps/social/backend
mkdir -p ~/otomaix/shared/db/migrations
mkdir -p ~/otomaix/shared/n8n-workflows
mkdir -p ~/otomaix/docs
```

**Beklenen çıktı:** Hata vermeden tamamlanır.

---

## Adım 2: PostgreSQL Şeması — Temel Tablolar

**Ne yapılıyor:** Social uygulamasının ihtiyaç duyduğu tüm tabloları oluşturuyoruz. Schema adı `social`, CRM tabloları `crm` schema'sına ayrı oluşturulacak.

**Claude Code session:** `~/otomaix/shared/db/` dizininde başlat.

### 2a. Migration dosyasını oluştur

**Claude Code'a ver:**
```
Create a PostgreSQL migration file at migrations/001_initial_social.sql

Create the following tables in the 'social' schema:

1. accounts
   - id UUID PRIMARY KEY DEFAULT gen_random_uuid()
   - email TEXT UNIQUE NOT NULL
   - name TEXT
   - plan_id TEXT DEFAULT 'starter' (starter/pro/business/agency)
   - created_at TIMESTAMPTZ DEFAULT now()
   - last_login_at TIMESTAMPTZ

2. workspaces
   - id UUID PRIMARY KEY DEFAULT gen_random_uuid()
   - account_id UUID REFERENCES social.accounts(id) ON DELETE CASCADE
   - name TEXT NOT NULL
   - created_at TIMESTAMPTZ DEFAULT now()

3. workspace_members
   - workspace_id UUID REFERENCES social.workspaces(id) ON DELETE CASCADE
   - account_id UUID REFERENCES social.accounts(id) ON DELETE CASCADE
   - role TEXT DEFAULT 'owner' (owner/admin/editor/viewer)
   - PRIMARY KEY (workspace_id, account_id)

4. brands
   - id UUID PRIMARY KEY DEFAULT gen_random_uuid()
   - workspace_id UUID REFERENCES social.workspaces(id) ON DELETE CASCADE
   - name TEXT NOT NULL
   - description TEXT
   - website_url TEXT
   - sector TEXT
   - brand_kit JSONB DEFAULT '{}'
   - logo_light_url TEXT
   - logo_dark_url TEXT
   - intro_video_url TEXT
   - is_active BOOLEAN DEFAULT true
   - created_at TIMESTAMPTZ DEFAULT now()

5. brand_documents
   - id UUID PRIMARY KEY DEFAULT gen_random_uuid()
   - brand_id UUID REFERENCES social.brands(id) ON DELETE CASCADE
   - name TEXT NOT NULL
   - file_url TEXT NOT NULL
   - file_type TEXT (pdf/word/excel/image)
   - category TEXT (product/service/corporate/price_list/other)
   - description TEXT
   - file_size_kb INTEGER
   - created_at TIMESTAMPTZ DEFAULT now()

6. brand_media
   - id UUID PRIMARY KEY DEFAULT gen_random_uuid()
   - brand_id UUID REFERENCES social.brands(id) ON DELETE CASCADE
   - name TEXT
   - file_url TEXT NOT NULL
   - media_type TEXT (image/video)
   - description TEXT
   - created_at TIMESTAMPTZ DEFAULT now()

7. brand_social_accounts
   - id UUID PRIMARY KEY DEFAULT gen_random_uuid()
   - brand_id UUID REFERENCES social.brands(id) ON DELETE CASCADE
   - platform TEXT NOT NULL (instagram/facebook/linkedin/tiktok/youtube/twitter/pinterest/google_business)
   - account_name TEXT
   - upload_post_token TEXT
   - is_active BOOLEAN DEFAULT true
   - connected_at TIMESTAMPTZ DEFAULT now()

8. posts
   - id UUID PRIMARY KEY DEFAULT gen_random_uuid()
   - brand_id UUID REFERENCES social.brands(id) ON DELETE CASCADE
   - content_type TEXT (image/video/carousel/faceless_video/ugc/meme/quote/special_day)
   - content_category TEXT (product/service/corporate)
   - status TEXT DEFAULT 'draft' (draft/generating/generated/scheduled/publishing/published/failed/rejected)
   - prompt TEXT
   - user_text TEXT
   - document_ids UUID[]
   - media_ids UUID[]
   - output_url TEXT
   - thumbnail_url TEXT
   - caption TEXT
   - hashtags TEXT[]
   - aspect_ratio TEXT (1:1/9:16/4:5/2:3)
   - platforms TEXT[]
   - scheduled_at TIMESTAMPTZ
   - published_at TIMESTAMPTZ
   - fal_job_id TEXT
   - created_at TIMESTAMPTZ DEFAULT now()
   - updated_at TIMESTAMPTZ DEFAULT now()

9. public_holidays
   - id UUID PRIMARY KEY DEFAULT gen_random_uuid()
   - year INTEGER NOT NULL
   - date DATE NOT NULL
   - name_tr TEXT NOT NULL
   - name_en TEXT
   - category TEXT (national/religious/commercial/special)
   - UNIQUE(year, date)

Enable pgvector extension and add a vector column to brand_documents for future RAG use:
   ALTER TABLE social.brand_documents ADD COLUMN IF NOT EXISTS embedding vector(1536);

Add updated_at trigger for posts table.
Add indexes on: brands(workspace_id), posts(brand_id), posts(status), posts(scheduled_at).
```

**Beklenen çıktı:** `migrations/001_initial_social.sql` dosyası oluşur.

### 2b. Migration'ı çalıştır

```bash
# SSH ile VPS'te
psql $DATABASE_URL -f ~/otomaix/shared/db/migrations/001_initial_social.sql
```

**Kontrol:**
```sql
-- psql'de kontrol et
\dn  -- social schema görünmeli
\dt social.*  -- tüm tablolar listelenmeli
```

---

## Adım 3: FastAPI Backend Kurulumu

**Ne yapılıyor:** `api.otomaix.com` adresinde çalışacak backend'i kuruyoruz.

**Claude Code session:** `~/otomaix/apps/social/backend/` dizininde başlat.

### 3a. CLAUDE.md oluştur (önce bunu yap)

**Claude Code'a ver:**
```
Create a CLAUDE.md file in the current directory with this content:

# Social Backend — CLAUDE.md

## Proje Amacı
Otomaix Social uygulamasının FastAPI backend'i. api.otomaix.com'da çalışır.

## VPS Bilgileri
- IP: 178.104.7.200
- Deploy: Coolify (servis adı: otomaix-social-backend)
- URL: https://api.otomaix.com

## Bağımlılıklar
- PostgreSQL: internal, schema: social
- Redis: internal
- n8n: https://n8n.otomaix.com
- fal.ai: AI medya üretimi
- Cloudflare R2: medya depolama
- Upload-Post.com: sosyal medya yayını
- Supabase Auth: JWT doğrulama

## Gerekli .env Değişkenleri
DATABASE_URL=
REDIS_URL=
SUPABASE_URL=
SUPABASE_SERVICE_KEY=
FAL_KEY=
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
R2_PUBLIC_URL=
UPLOAD_POST_API_KEY=

## Tamamlanan İşler
- [ ] Proje kurulumu

## Devam Eden İş
- Proje kurulumu başlıyor

## Önemli Kararlar
- Tüm tarihler UTC olarak saklanır
- Storage abstraction: storage.py → CloudflareR2Provider
- JWT doğrulama Supabase üzerinden yapılır
```

### 3b. Proje yapısını oluştur

**Claude Code'a ver:**
```
Set up a FastAPI project with the following structure:

app/
├── main.py              # FastAPI app, CORS, routers
├── core/
│   ├── config.py        # Settings from env vars using pydantic-settings
│   ├── database.py      # Async PostgreSQL connection with asyncpg
│   ├── redis.py         # Redis connection
│   └── security.py      # Supabase JWT verification middleware
├── routers/
│   ├── auth.py          # GET /auth/me — return current user info
│   ├── brands.py        # CRUD /brands
│   ├── posts.py         # POST /posts/create, GET /posts
│   └── storage.py       # POST /storage/upload — presigned URL generator
├── models/
│   └── schemas.py       # Pydantic models for all endpoints
├── services/
│   ├── storage.py       # Cloudflare R2 abstraction (upload, get, delete)
│   ├── fal_ai.py        # fal.ai image/video generation trigger
│   └── upload_post.py   # Upload-Post.com social media publishing
└── requirements.txt

Requirements:
fastapi, uvicorn, asyncpg, pydantic-settings, python-dotenv,
boto3 (for R2), fal-client, httpx, redis, python-jose

Rules:
- All responses use consistent JSON: {"success": true, "data": {...}} or {"success": false, "error": "..."}
- All datetime fields returned as ISO 8601 UTC strings
- Use async/await throughout
- Add docstrings to all endpoints (shown in Swagger)
```

**Beklenen çıktı:** Tam klasör yapısı ve tüm dosyalar oluşur.

### 3c. Supabase JWT Middleware

**Claude Code'a ver:**
```
Implement Supabase JWT verification in app/core/security.py

The middleware should:
1. Extract Bearer token from Authorization header
2. Verify it against Supabase JWKS endpoint
3. Return the decoded user payload (sub = user UUID, email)
4. Raise HTTP 401 if token is missing or invalid

Create a FastAPI dependency called get_current_user() that routers can use.
Also create get_current_user_optional() for public endpoints.

Test it in app/routers/auth.py:
GET /auth/me → returns {id, email} of authenticated user
```

### 3d. Storage Abstraction

**Claude Code'a ver:**
```
Implement Cloudflare R2 storage service in app/services/storage.py

The R2 storage path structure for social app is:
- brands/{brand_id}/kit/logo_light.{ext}
- brands/{brand_id}/kit/logo_dark.{ext}
- brands/{brand_id}/kit/intro.mp4
- brands/{brand_id}/documents/{doc_id}_{filename}.{ext}
- brands/{brand_id}/media/{media_id}_{filename}.{ext}
- brands/{brand_id}/posts/generated/{post_id}.{ext}
- brands/{brand_id}/posts/thumbnails/{post_id}_thumb.jpg

Implement these methods:
- upload(file_bytes, path, content_type) → public URL
- get_presigned_upload_url(path, content_type, expires=3600) → presigned URL
- delete(path) → bool
- copy(source_path, dest_path) → public URL (used for fal.ai → R2)

Use boto3 with R2 endpoint: https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com
Public URL format: {R2_PUBLIC_URL}/{path}

Add a router endpoint POST /storage/presigned-url that frontend can call
to get an upload URL directly to R2 (bypassing the API for large files).
```

### 3e. fal.ai Entegrasyonu

**Claude Code'a ver:**
```
Implement fal.ai integration in app/services/fal_ai.py

Requirements:
- Use fal-client Python SDK
- Support async generation with webhook callback
- Webhook URL: https://api.otomaix.com/webhooks/fal

## fal.ai Model Seçimleri

| Tip | Model ID | Açıklama |
|-----|----------|----------|
| Görsel (image) | `fal-ai/flux-2-pro` | FLUX.2 [pro] — yüksek kalite görsel üretimi |
| Video (text-to-video) | `fal-ai/kling-video/v3/pro/text-to-video` | Kling 3.0 Pro — metinden video üretimi |
| Görsel→Video (image-to-video) | `fal-ai/kling-video/v2.5-turbo/pro/image-to-video` | Kling 2.5 Turbo Pro — fotoğraftan video üretimi |

Implement:
1. generate_image(prompt, aspect_ratio, brand_kit) → fal_job_id
   - Model: fal-ai/flux-2-pro
   - Include brand colors and style from brand_kit in the prompt
   - Return the fal job ID immediately (don't wait for result)

2. generate_video(prompt, aspect_ratio, brand_kit) → fal_job_id
   - Model: fal-ai/kling-video/v3/pro/text-to-video
   - Metinden video üretimi

3. generate_video_from_image(prompt, image_url, brand_kit) → fal_job_id
   - Model: fal-ai/kling-video/v2.5-turbo/pro/image-to-video
   - Kullanıcının yüklediği ürün görseli + prompt → video
   - image_url: R2'ye yüklenen geçici görsel URL'i

4. A webhook router at POST /webhooks/fal
   - Receives fal.ai callback when generation is complete
   - Downloads the file from fal's temporary URL
   - Uploads to R2 using storage service: brands/{brand_id}/posts/generated/{post_id}.jpg
   - Updates post record in PostgreSQL: status='generated', output_url=R2 URL
   - fal URLs expire in 24-72h so R2 copy is critical

Add the webhook router to main.py
```

### 3f. Upload-Post.com Entegrasyonu

**Claude Code'a ver:**
```
Implement Upload-Post.com integration in app/services/upload_post.py

Upload-Post.com is used for social media publishing.
API docs: https://upload-post.com/api

Implement:
1. get_oauth_link(brand_id, platform) → JWT link URL
   - Generates a JWT-authenticated link for the client to connect their social account
   - platform options: instagram, facebook, linkedin, tiktok, youtube, twitter, pinterest

2. publish_post(post_id) → {"success": bool, "platform_post_id": str}
   - Fetches post data from PostgreSQL
   - Gets the brand's social account token for each platform
   - Uploads media from R2 URL
   - Posts to specified platforms
   - Updates post status to 'published' or 'failed'

Add router endpoints:
- GET /social/oauth-link?platform={platform} → returns OAuth link for brand
- POST /posts/{post_id}/publish → triggers publishing
```

**Kontrol:**
```bash
# Backend'i test et
cd ~/otomaix/apps/social/backend
uvicorn app.main:app --reload --port 8000

# Swagger UI aç
# http://178.104.7.200:8000/docs
```

---

## Adım 4: Next.js Frontend Kurulumu

**Ne yapılıyor:** `app.otomaix.com` adresinde çalışacak frontend iskeleti kuruyoruz.

**Claude Code session:** `~/otomaix/apps/social/frontend/` dizininde başlat.

### 4a. CLAUDE.md oluştur

**Claude Code'a ver:**
```
Create CLAUDE.md in the current directory:

# Social Frontend — CLAUDE.md

## Proje Amacı
Otomaix Social uygulamasının Next.js frontend'i. app.otomaix.com'da çalışır.

## VPS Bilgileri
- IP: 178.104.7.200
- Deploy: Coolify (servis adı: otomaix-social-frontend)
- URL: https://app.otomaix.com

## Bağımlılıklar
- Backend API: https://api.otomaix.com
- Supabase Auth: JWT authentication
- Cloudflare R2: assets.otomaix.com

## Gerekli .env.local Değişkenleri
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
NEXT_PUBLIC_API_URL=https://api.otomaix.com
NEXT_PUBLIC_ASSETS_URL=https://assets.otomaix.com

## Tamamlanan İşler
- [ ] Proje kurulumu

## Devam Eden İş
- Proje kurulumu başlıyor

## Önemli Kararlar
- App Router kullanılıyor (Next.js 14)
- Türkçe varsayılan dil (next-intl)
- shadcn/ui + Tailwind CSS
- Zustand global state
- 250px sabit sidebar + main content layout
```

### 4b. Next.js Projesi Oluştur

**Claude Code'a ver:**
```
Create a Next.js 14 project with App Router in the current directory.

Install and configure:
- shadcn/ui (with Tailwind CSS)
- Zustand for state management
- next-intl for i18n (Turkish as default language)
- @supabase/supabase-js and @supabase/auth-helpers-nextjs
- date-fns and date-fns-tz
- lucide-react for icons

Project structure:
app/
├── (auth)/
│   ├── login/
│   │   └── page.tsx
│   └── layout.tsx
├── (dashboard)/
│   ├── dashboard/
│   │   └── page.tsx
│   ├── layout.tsx          # Sidebar + main content layout
│   └── loading.tsx
├── layout.tsx              # Root layout with providers
└── page.tsx                # Redirect to /dashboard or /login

components/
├── layout/
│   ├── Sidebar.tsx         # 250px fixed sidebar
│   ├── SidebarNav.tsx      # Navigation items
│   └── TopBar.tsx
├── ui/                     # shadcn components go here
└── providers/
    └── Providers.tsx       # Supabase + Zustand providers

lib/
├── api.ts                  # API client (fetch wrapper with auth header)
├── supabase.ts             # Supabase client
└── store.ts                # Zustand store (user, currentBrand)

messages/
└── tr.json                 # Turkish translations

Rules:
- Background color: #F6F7F9
- Sidebar: 250px fixed width, white, subtle shadow
- Use Inter font (Turkish character support)
- All text content in tr.json (Turkish)
```

### 4c. Auth Akışı

**Claude Code'a ver:**
```
Implement Supabase authentication flow:

1. Login page (app/(auth)/login/page.tsx):
   - Google OAuth button (primary)
   - Email + password form (secondary)
   - Otomaix logo at top
   - Turkish text throughout
   - Redirect to /dashboard after login

2. Auth middleware (middleware.ts):
   - Protect all /dashboard/* routes
   - Redirect unauthenticated users to /login
   - Refresh session token automatically

3. After login, call GET /auth/me on the backend API
   - Store user data in Zustand store
   - If user has no workspace yet, redirect to /onboarding

4. Zustand store (lib/store.ts):
   interface AppStore {
     user: { id: string; email: string; name: string } | null
     currentWorkspace: Workspace | null
     currentBrand: Brand | null
     setUser: (user) => void
     setCurrentBrand: (brand) => void
   }
```

### 4d. Dashboard İskeleti

**Claude Code'a ver:**
```
Create the main dashboard layout and a skeleton dashboard page.

Layout (app/(dashboard)/layout.tsx):
- Left sidebar: 250px fixed, white background
- Sidebar top: Otomaix logo + brand selector dropdown
- Sidebar nav items: Dashboard, İçerik Oluştur, İçerik Kütüphanesi, 
  Takvim, Otomatik Yayın, Marka Ayarları, Rakip Analizi
- Sidebar bottom: user avatar + name + logout button
- Main content: remaining width, #F6F7F9 background, overflow-y auto

Dashboard page (app/(dashboard)/dashboard/page.tsx):
- Greeting: "Günaydın, [name]!" (changes by time of day)
- Posting Streak widget (placeholder, 7-day grid)
- Quick stats: Bu ay üretilen içerik, Yayınlanan içerik, Bağlı platform sayısı
- "Hesabınızı Bağlayın" CTA cards for Instagram, TikTok, LinkedIn
- All text in Turkish
- Use shadcn Card components for widgets
```

**Kontrol:**
```bash
cd ~/otomaix/apps/social/frontend
npm run dev
# http://178.104.7.200:3000 — login sayfası görünmeli
```

---

## Adım 5: Coolify'da Deploy Yapılandırması

**Ne yapılıyor:** Her servisi Coolify üzerinden deploy ediyoruz.

**Claude Code session:** `~/otomaix/apps/social/backend/` için backend, `~/otomaix/apps/social/frontend/` için frontend.

### 5a. Backend Dockerfile

**Claude Code'a ver (backend session'ında):**
```
Create a Dockerfile for the FastAPI backend:

- Base image: python:3.12-slim
- Working directory: /app
- Copy requirements.txt, install dependencies
- Copy app/ directory
- Expose port 8000
- CMD: uvicorn app.main:app --host 0.0.0.0 --port 8000

Also create a .dockerignore file (exclude: .env, __pycache__, .git, venv)
```

### 5b. Frontend Dockerfile

**Claude Code'a ver (frontend session'ında):**
```
Create a production Dockerfile for Next.js:

- Multi-stage build
- Stage 1 (deps): node:20-alpine, install dependencies
- Stage 2 (builder): build the Next.js app
- Stage 3 (runner): node:20-alpine, copy built files, run
- Expose port 3000
- Use Next.js standalone output mode

Add to next.config.js: output: 'standalone'
Create .dockerignore: node_modules, .next, .env.local, .git
```

### 5c. Coolify'da Servis Oluştur

**Bu adımı Coolify UI'da manuel yap:**

1. Coolify'a giriş yap → New Service
2. Backend için:
   - Name: `otomaix-social-backend`
   - Source: Git repository
   - Domain: `api.otomaix.com`
   - Port: `8000`
   - Env vars: `.env` dosyasındaki tüm değerleri ekle
3. Frontend için:
   - Name: `otomaix-social-frontend`
   - Domain: `app.otomaix.com`
   - Port: `3000`
   - Env vars: `.env.local` değerlerini ekle

---

## Adım 6: İlk Uçtan Uca Test

**Ne yapılıyor:** Tüm bileşenlerin birbirine bağlandığını doğruluyoruz.

### Test senaryosu — sırasıyla kontrol et:

```
1. app.otomaix.com → Login sayfası görünüyor mu?
2. Google OAuth → Dashboard'a yönlendiriyor mu?
3. api.otomaix.com/docs → Swagger UI açılıyor mu?
4. GET /auth/me → Kullanıcı bilgisi dönüyor mu?
5. POST /brands → Yeni marka oluşturuluyor mu?
6. POST /storage/presigned-url → R2 presigned URL alınıyor mu?
7. fal.ai test → Görsel üretimi başlatılıyor mu?
8. n8n.otomaix.com → Giriş yapılabiliyor mu?
```

**Claude Code'a ver (herhangi bir session'da):**
```
Create a test script at ~/otomaix/shared/test_phase1.sh

The script should test all Phase 1 endpoints:
1. Health check: GET https://api.otomaix.com/health
2. Check PostgreSQL connection
3. Check Redis connection
4. Check R2 connection (list bucket)
5. Print PASS/FAIL for each check
```

---

## Phase 1 Tamamlanma Kontrol Listesi

Phase 2'ye geçmeden önce bunların hepsi ✅ olmalı:

- [ ] VPS klasör yapısı kuruldu
- [ ] PostgreSQL `social` schema'sı ve tüm tablolar oluşturuldu
- [ ] FastAPI çalışıyor, Swagger UI açılıyor (`api.otomaix.com/docs`)
- [ ] Supabase Auth JWT doğrulaması çalışıyor
- [ ] GET /auth/me kullanıcı bilgisi dönüyor
- [ ] Cloudflare R2 bağlı, presigned URL alınabiliyor
- [ ] fal.ai görsel üretimi tetiklenebiliyor
- [ ] fal.ai webhook → R2 kopyalama çalışıyor
- [ ] Upload-Post.com OAuth link alınabiliyor
- [ ] Next.js login sayfası çalışıyor (`app.otomaix.com`)
- [ ] Google OAuth login ve dashboard yönlendirmesi çalışıyor
- [ ] Sidebar layout ve dashboard iskelet görünüyor
- [ ] Her iki servis Coolify'da deploy edilmiş

---

*Tamamlandı mı? → `02-social-phase2.md` ile devam et*
