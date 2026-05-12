# 04 — Social Uygulaması: Phase 4 — SaaS Hazırlık
> **Süre:** Ay 4–6  
> **Ön koşul:** `03-social-phase3.md` tamamlanmış ve kontrol listesi ✅  
> **Hedef:** Ürün self-serve çalışıyor, SaaS olarak yeni müşteri alınabiliyor, izleme ve gözlemlenebilirlik tam

---

## Bu Phase'de Ne Yapılıyor?

Phase 4 sonunda elimizde şunlar olacak:
- Self-serve onboarding — müşteri kendi kaydolup ürünü kullanabiliyor
- PostHog analytics entegrasyonu
- Sentry error monitoring
- Docker Compose paketi — local/on-premise kurulum seçeneği
- Crisp Chat canlı destek
- Redis ile tam cache ve rate limiting
- Performance optimizasyonu ve load testing
- Ürün gerçek anlamda SaaS'a hazır

---

## Adım 1: Self-Serve Onboarding Optimizasyonu

**Ne yapılıyor:** Phase 2'de yapılan onboarding'i self-serve'e uygun hale getiriyoruz. Müşteri artık Otomaix ekibine ihtiyaç duymadan kaydolup kullanmaya başlayabiliyor.

**Claude Code'a ver (frontend session'ında):**
```
Optimize the onboarding flow for self-serve SaaS:

1. Public landing page at app/page.tsx (unauthenticated):
   - Hero section: "Türk KOBİ'ler için AI Sosyal Medya Otomasyonu"
   - 3 feature highlights
   - Pricing section (embed from /fiyatlandirma)
   - "Ücretsiz Dene" CTA → /kayit
   - "Giriş Yap" link → /login
   
2. Registration page at app/(auth)/kayit/page.tsx:
   - Google OAuth (primary)
   - Email + password form
   - "Zaten hesabınız var mı? Giriş yapın"
   - After registration: create account in DB + send welcome email via n8n

3. Email verification flow:
   - Supabase handles email verification
   - After verify: redirect to onboarding wizard

4. Improve onboarding completion rate:
   - Add progress bar at top ("3/7 tamamlandı")
   - Allow "Daha Sonra Atla" for optional steps
   - Show value proposition at each step
   - After onboarding: show "İlk İçeriğinizi Üretin" immediate CTA

5. Trial period display:
   - Show trial days remaining in sidebar: "🎁 Deneme: 14 gün kaldı"
   - After trial ends: redirect to /fiyatlandirma
```

### n8n — Onboarding Email Otomasyonu

**Claude Code'a ver:**
```
Create n8n workflow "Kullanıcı Onboarding Email Serisi" using n8n MCP.

Trigger: Webhook POST /webhook/new-user (called after registration)
Input: {account_id, email, name}

Email series:
Day 0: Hoş geldiniz emaili
  - Welcome + "Otomaix nasıl çalışır?" video linki
  - "Başlayın" CTA button

Day 2: If onboarding not completed:
  - "Markanızı henüz kurmadınız" reminder
  - Link to continue onboarding

Day 5: If no content generated:
  - "İlk içeriğinizi üretin" email
  - Show sample content examples

Day 12 (2 days before trial ends):
  - Trial ending reminder
  - Pricing with "En Popüler" plan highlighted
  - Limited time offer if any

Use n8n's wait nodes between emails.
Check actual user status before each email (skip if already completed action).

Export to ~/otomaix/shared/n8n-workflows/onboarding-email-series.json
```

---

## Adım 2: PostHog Analytics Entegrasyonu

**Ne yapılıyor:** Kullanıcı davranışlarını izliyoruz — hangi özellikler kullanılıyor, nerede drop-off oluyor, conversion oranları.

### 2a. Frontend — PostHog kurulumu

**Claude Code'a ver (frontend session'ında):**
```
Install and configure PostHog analytics.

Install: posthog-js posthog-node

Configure in app/providers/Providers.tsx:
- Initialize PostHog with project API key from env
- Identify users after login: posthog.identify(user.id, {email, plan, sector})
- Auto-capture pageviews

Track these key events throughout the app:

Onboarding funnel:
- onboarding_started
- onboarding_step_completed {step: 1-7}
- onboarding_completed
- onboarding_skipped {at_step: N}

Content creation:
- content_creation_started {content_type}
- idea_suggestion_used
- document_reference_used
- content_generated {content_type, generation_time_seconds}
- content_regenerated
- content_published {platform}
- content_scheduled

Feature adoption:
- calendar_opened
- autoposting_configured
- competitor_added
- trend_post_created
- avatar_created
- telegram_approval_enabled

Conversion:
- pricing_page_viewed
- plan_selected {plan_id}
- checkout_started
- subscription_created {plan_id}
- plan_upgraded {from_plan, to_plan}
- trial_expired_converted (bool)

Create PostHog dashboard screenshots target:
- DAU/WAU/MAU
- Onboarding completion rate (funnel)
- Content generation by type (bar chart)
- Feature adoption rates
- Trial to paid conversion rate
```

### 2b. Backend — Server-side analytics

**Claude Code'a ver (backend session'ında):**
```
Add server-side PostHog tracking for backend events.

Install: posthog-python

Track in app/services/analytics.py:
- content_generation_failed {content_type, error}
- fal_api_latency {model, duration_ms}
- publishing_failed {platform, error}
- document_processed {file_type, chunks_created}
- competitor_analysis_completed {duration_seconds}

Create a background task that sends daily metrics to PostHog:
- Total posts generated today
- Total posts published today
- fal.ai cost today (USD)
- R2 storage used (GB)
```

---

## Adım 3: Sentry Error Monitoring

**Ne yapılıyor:** Frontend ve backend hataları gerçek zamanlı izleniyor.

**Claude Code'a ver (frontend session'ında):**
```
Install and configure Sentry for Next.js frontend.

Install: @sentry/nextjs

Run: npx @sentry/wizard@latest -i nextjs

Configure:
- DSN from environment variable SENTRY_DSN
- Enable session replay (for debugging UX issues)
- Set tracesSampleRate: 0.1 (10% of transactions)
- Add user context after login: Sentry.setUser({id, email})
- Tag environment: development/production

Add to next.config.js: withSentryConfig wrapper

Test: trigger a test error to confirm Sentry receives it
```

**Claude Code'a ver (backend session'ında):**
```
Install and configure Sentry for FastAPI backend.

Install: sentry-sdk[fastapi]

Configure in app/main.py:
import sentry_sdk
sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=0.1,
    environment=settings.ENVIRONMENT,
    integrations=[FastApiIntegration()]
)

Add custom error tracking in:
- fal.ai failures: capture_exception + add context (post_id, brand_id)
- Upload-Post.com failures: capture with platform context
- Paddle webhook failures: capture with subscription context

Set up Sentry alerts:
- Alert if error rate > 5% in 5 minutes
- Alert if fal.ai failures > 10 in 1 hour
```

---

## Adım 4: Redis Cache ve Rate Limiting

**Ne yapılıyor:** Performance iyileştirmesi ve API koruma. SaaS ölçeğinde şart.

**Claude Code'a ver (backend session'ında):**
```
Implement Redis caching and rate limiting in FastAPI.

Install: redis[hiredis] fastapi-limiter

1. Rate Limiting (app/core/redis.py):
   Set up fastapi-limiter with Redis backend.
   
   Limits per authenticated user:
   - POST /posts/generate: 20 requests per hour
   - POST /ai/suggest-ideas: 30 requests per hour  
   - POST /competitors: 10 requests per hour
   - General API: 200 requests per minute
   
   Return HTTP 429 with {"error": "rate_limit", "retry_after": 60}

2. Caching (using redis-py):
   Cache these responses (TTL in seconds):
   - GET /brands (brand list): 300s (invalidate on brand update)
   - GET /calendar/holidays: 86400s (24 hours)
   - GET /trends: 3600s (1 hour)
   - GET /avatar/stock: 3600s (1 hour)
   
   Use cache key pattern: "otomaix:social:{endpoint}:{user_id}:{params_hash}"
   
   Add cache invalidation:
   - On PATCH /brands/{id}: delete "otomaix:social:brands:{user_id}:*"

3. Session caching:
   After JWT verification, cache user data:
   Key: "otomaix:social:user:{user_id}"
   TTL: 300s
   (Avoid hitting Supabase on every request)
```

---

## Adım 5: Docker Compose — Local Kurulum Paketi

**Ne yapılıyor:** Kullanıcı Otomaix'i kendi sunucusuna kurabilecek. Bu özellikle B2B enterprise müşterilere cazip gelir.

**Claude Code'a ver (herhangi bir session'da):**
```
Create a Docker Compose package for local/on-premise deployment.

Create directory: ~/otomaix/shared/local-deployment/

Files to create:

1. docker-compose.yml:
services:
  frontend:
    image: otomaix-social-frontend:latest
    ports: ["3000:3000"]
    env_file: .env
    depends_on: [backend]

  backend:
    image: otomaix-social-backend:latest
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [postgres, redis]

  postgres:
    image: pgvector/pgvector:pg16
    volumes: [postgres_data:/var/lib/postgresql/data]
    environment:
      POSTGRES_DB: otomaix
      POSTGRES_USER: otomaix
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}

  redis:
    image: redis:7-alpine
    volumes: [redis_data:/data]

  n8n:
    image: n8nio/n8n
    ports: ["5678:5678"]
    volumes: [n8n_data:/home/node/.n8n]
    environment:
      DB_TYPE: postgresdb
      DB_POSTGRESDB_HOST: postgres
      (other n8n env vars)

volumes:
  postgres_data:
  redis_data:
  n8n_data:

2. .env.example:
   All required environment variables with placeholder values
   Include: DATABASE_URL, REDIS_URL, SUPABASE_*, FAL_KEY, 
   R2_*, UPLOAD_POST_API_KEY, PADDLE_*, SENTRY_DSN

3. setup.sh:
   #!/bin/bash
   echo "Otomaix kurulumu başlıyor..."
   cp .env.example .env
   echo "Lütfen .env dosyasını düzenleyin"
   # Check Docker is installed
   # Run migrations
   # Pull images
   # Start services

4. README-local.md:
   Step-by-step Turkish installation guide
   Requirements, troubleshooting section

5. migrations/run-migrations.sh:
   Script to run all SQL migrations against the local PostgreSQL
```

---

## Adım 6: Crisp Chat Entegrasyonu

**Ne yapılıyor:** Kullanıcılar uygulamadan direkt destek alabilecek.

**Claude Code'a ver (frontend session'ında):**
```
Add Crisp Chat live support widget.

Install: @danestves/react-crisp

Add to app/providers/Providers.tsx:
- Initialize Crisp with CRISP_WEBSITE_ID from env
- After user login: identify user in Crisp
  crisp.user.setEmail(user.email)
  crisp.user.setNickname(user.name)
  crisp.session.setData({plan: user.plan, brands_count: N})

Configure Crisp appearance:
- Position: bottom right
- Color: match Otomaix brand color
- Turkish as default language

Hide on mobile (responsive: only show on desktop or minimize by default on mobile)

In Crisp dashboard (manual step): 
- Set up auto-reply for common questions
- Set business hours (Turkish working hours)
- Create saved replies in Turkish for common issues
```

---

## Adım 7: Performance Optimizasyonu

**Ne yapılıyor:** Ürün production'a hazır hale getiriliyor.

**Claude Code'a ver (frontend session'ında):**
```
Perform Next.js performance optimizations:

1. Image optimization:
   - Use next/image for all content thumbnails
   - Add blur placeholder for content library images
   - Configure domains in next.config.js for R2 public URL

2. Code splitting:
   - Lazy load FullCalendar (only on calendar page)
   - Lazy load Fabric.js canvas editor
   - Lazy load Lottie animations

3. API response caching:
   - Add React Query (TanStack Query) for client-side caching
   - Cache GET /brands, GET /posts, GET /calendar/posts
   - Optimistic updates for post status changes

4. Bundle analysis:
   Run: ANALYZE=true npm run build
   Identify and fix any large bundles (target: < 250KB initial JS)

5. Core Web Vitals targets:
   - LCP < 2.5s
   - CLS < 0.1
   - FID < 100ms
```

**Claude Code'a ver (backend session'ında):**
```
FastAPI performance optimizations:

1. Database connection pooling:
   Configure asyncpg pool: min_size=5, max_size=20

2. Slow query detection:
   Add logging for queries taking > 100ms
   Add these indexes if missing:
   - posts(brand_id, scheduled_at) for calendar queries
   - posts(brand_id, created_at DESC) for content library
   - brand_document_chunks(brand_id) for RAG queries

3. Background tasks:
   Move these operations to FastAPI BackgroundTasks:
   - Sending notification emails
   - Updating analytics
   - Generating thumbnails

4. Health check endpoint:
   GET /health → {"status": "ok", "db": "ok", "redis": "ok", "timestamp": "..."}
   Used by Coolify for health monitoring
```

---

## Adım 8: Load Testing

**Ne yapılıyor:** Ürünün kaç kullanıcıya dayanabileceğini test ediyoruz.

**Claude Code'a ver:**
```
Create a load test script using locust.

Install: locust

Create locustfile.py at ~/otomaix/shared/load-tests/locustfile.py

Test scenarios:
class OtomaixUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login and get JWT token
        
    @task(3)
    def view_dashboard(self):
        # GET /brands, GET /calendar/posts
        
    @task(2)  
    def browse_content_library(self):
        # GET /posts?page=1, GET /posts?page=2
        
    @task(1)
    def generate_content(self):
        # POST /posts/generate (mock fal.ai in test env)

Target: 50 concurrent users, < 500ms average response time

Run: locust -f locustfile.py --host=https://api.otomaix.com
```

---

## Phase 4 Tamamlanma Kontrol Listesi — SaaS Hazır

Ürün SaaS olarak yayına alınabilir mi? Bunların hepsi ✅ olmalı:

- [ ] Landing page yayında (app.otomaix.com anasayfası)
- [ ] Kullanıcı kendi başına kaydolabiliyor
- [ ] Email doğrulama çalışıyor
- [ ] Onboarding wizard sorunsuz tamamlanıyor (5/5 test kullanıcısı)
- [ ] Onboarding email serisi n8n'den gönderiliyor
- [ ] PostHog eventi'leri geliyor (kontrol: PostHog dashboard)
- [ ] Sentry hataları yakalanıyor (kontrol: test hatası gönder)
- [ ] Redis rate limiting çalışıyor (429 dönüyor limit aşılınca)
- [ ] Redis cache çalışıyor (brand listesi cache'leniyor)
- [ ] Docker Compose paketi test edildi (local'de sorunsuz kuruldu)
- [ ] Crisp Chat çalışıyor (test mesajı gönder)
- [ ] /health endpoint sağlıklı dönüyor
- [ ] Load test geçildi (50 concurrent, <500ms)
- [ ] Bundle size < 250KB initial JS
- [ ] Coolify'da tüm servisler kararlı (son 7 gün restart yok)

---

## 🎉 Phase 4 Tamamlandı — Ürün SaaS'ta!

**Buraya geldiğinde:**
1. `05-crm-admin.md` ile CRM'i geliştirmeye devam edebilirsin
2. İlk self-serve müşterileri kabul etmeye başlayabilirsin
3. Gelecekteki Otomaix uygulamaları için `00-platform-mimari.md`'yi güncelle

---

*Tamamlandı mı? → `05-crm-admin.md` ile devam et*
