# Social Frontend — CLAUDE.md

> **DRIFT KORUMA**
> Bu dosya YALNIZCA: proje yapısı, env, deploy, konvansiyonlar.
> Sprint logları → git commit.
> Kararlar → memory/decisions_*.md.
> Aktif iş → Tasks (oturum içi).
> Bu dosyaya changelog EKLENMEZ.

## Proje Amacı

Otomaix Social uygulamasının Next.js 14 (App Router) frontend'i. `app.otomaix.com`'da çalışır.
AI destekli sosyal medya içerik üretimi, takvim, otomatik yayın, trend/rakip analizi, fiyatlandırma ve onboarding.

## Proje Kılavuzları

- Genel mimari: `~/otomaix/docs/00-platform-mimari.md`
- Phase kılavuzları: `~/otomaix/docs/01-social-phase1.md` ... `04-social-phase4.md`

## Deploy

- IP: 178.104.7.200
- Coolify servis adı: `otomaix-social-frontend`
- URL: https://app.otomaix.com
- Dockerfile: multi-stage, node:20-alpine, standalone output

## Bağımlılıklar

- Backend API: https://api.otomaix.com
- Supabase Auth: JWT authentication (Google OAuth + email/password)
- Cloudflare R2: assets.otomaix.com (medya CDN)

## .env.local Değişkenleri

```
NEXT_PUBLIC_SUPABASE_URL=https://sqplkkivtkfyozrvnybe.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
NEXT_PUBLIC_API_URL=https://api.otomaix.com
NEXT_PUBLIC_ASSETS_URL=https://assets.otomaix.com

# Opsiyonel
NEXT_PUBLIC_POSTHOG_KEY=
NEXT_PUBLIC_POSTHOG_HOST=
NEXT_PUBLIC_SENTRY_DSN=
NEXT_PUBLIC_CRISP_WEBSITE_ID=
```

## Klasör Yapısı

```
app/
├── page.tsx                          # Public landing page
├── globals.css                       # Tailwind + FullCalendar override'ları
├── (auth)/
│   ├── login/page.tsx                # Google OAuth + email/password
│   └── kayit/page.tsx                # Kayıt + email doğrulama
├── auth/callback/page.tsx            # OAuth callback handler
├── (onboarding)/
│   └── onboarding/page.tsx           # 7 adımlı wizard
├── (dashboard)/
│   ├── layout.tsx                    # Auth koruması + /auth/init + providers
│   ├── dashboard/page.tsx            # Genel bakış + trend widget + stats
│   ├── icerik-olustur/page.tsx       # 3 adımlı içerik üretim wizard
│   ├── icerik-kutuphanesi/page.tsx   # Masonry grid + detail modal + carousel slider
│   ├── takvim/page.tsx               # FullCalendar + drag&drop + tatil gösterimi
│   ├── otomatik-yayin/page.tsx       # 4 adımlı autoposting wizard
│   ├── marka-ayarlari/page.tsx       # 6 sekmeli marka yönetimi
│   ├── markalar/page.tsx             # Çoklu marka grid + CRUD
│   ├── trendler/page.tsx             # 3 sekmeli trend sayfası (Gündem/Sektör/Kişisel)
│   ├── rakip-analizi/page.tsx        # Rakip kartları + analiz detay
│   ├── fiyatlandirma/page.tsx        # 4 plan kartı (Paddle checkout)
│   ├── faturalandirma/page.tsx       # Mevcut plan + kullanım + portal
│   └── ayarlar/page.tsx              # Kullanıcı ayarları

components/
├── billing/
│   └── UpgradeModal.tsx              # 402 plan limit modal
├── competitors/                      # Rakip analizi bileşenleri
├── content/
│   └── ContentCard.tsx               # İçerik kartı (carousel badge dahil)
├── layout/
│   ├── Sidebar.tsx                   # 250px sidebar + BrandSwitcher + TrialBanner
│   └── BrandSwitcher.tsx             # Marka dropdown
├── products/                         # Ürün/Hizmet CRUD bileşenleri
├── providers/
│   ├── Providers.tsx                 # PostHog + Crisp sarmalayıcı
│   ├── PostHogProvider.tsx           # PostHog init + pageview
│   └── CrispProvider.tsx             # Crisp chat widget
├── templates/
│   ├── TemplateCard.tsx
│   ├── TemplateGrid.tsx              # (aktif kullanılmıyor — auto-select devrede)
│   ├── DynamicForm.tsx               # 6 field tipi + gruplandırma + text overlay toggle
│   └── CaptionEditor.tsx             # Platform sekmeli caption + hashtag editörü
└── ui/                               # shadcn/ui (base-nova theme, @base-ui/react)

lib/
├── api.ts                            # apiFetch + ApiResponse<T> + 402/429 handling
├── api/                              # API client modülleri
├── store.ts                          # Zustand (user, workspace, brands, currentBrand)
├── supabase.ts                       # Supabase client
├── analytics.ts                      # PostHog typed event wrapper
├── utils.ts                          # Yardımcı fonksiyonlar
├── templates.types.ts                # Template TypeScript interface'leri (1:1 backend Pydantic)
└── products.types.ts                 # Ürün/Hizmet TypeScript interface'leri
```

## Önemli Paketler

- `@base-ui/react` — shadcn base-nova UI primitives (Select, Sheet, Dialog vb.)
- `@fullcalendar/react` + daygrid + timegrid + interaction — takvim
- `recharts` — dashboard + CRM grafikleri
- `sonner` — toast bildirimleri
- `zustand` — global state
- `posthog-js` — analytics
- `@sentry/nextjs` — error monitoring

## İçerik Üretim Akışı (icerik-olustur)

- **Wizard state machine:** `mode: 'template'|'free'`, `phase: 'pick'|'form'|'caption'`
- **Image/Carousel:** Caption-first Akış C → pick → form → caption → görsel üret → Step 3
- **Video/Special Day/Quote:** Tek-tık akış (caption ayrı değil)
- **Şablon stratejisi:** Genel şablonlar auto-select (sektör şablonları terk edildi)
  - Image: `genel-gorsel-sablon`, Carousel: `carousel-genel-sablon`
  - TemplateGrid + sektör filtreleme altyapısı mevcut ama aktif kullanılmıyor
- **Ürün/Hizmet:** `imageSubType: 'general'|'product'` → ürün seçilince form pre-fill + product_id gönderilir

## Konvansiyonlar

### Auth

- Supabase session **localStorage**'da (cookie değil) → middleware no-op
- `onAuthStateChange` ile `INITIAL_SESSION` event'ı beklenir — `getSession()` kullanılmaz (race condition)
- Auth koruması `layout.tsx`'te, middleware değil

### State & Navigation

- Brand switching: `switchBrand()` + `router.push()` — `<Link>` değil (state sıralaması belirsizliği)
- Brand seçimi `localStorage`'da persist edilir (`otomaix_selected_brand_id`)
- Publish guard: `useRef` senkron guard (`publishingRef`) — `useState` async race condition'a açık

### UI

- Blob URL preview → `<img>` tag; R2 URL → `<Image>` (next/image blob'u sunucudan fetch etmeye çalışır)
- SSR hydration: `new Date()` komponent body'sinde kullanılmaz → `useEffect` + `useState`
- Select.Value: `{(value) => labels[value]}` pattern (raw slug render engellenir)
- Tailwind data-attribute variant: `data-[orientation=horizontal]:flex-col` (köşeli parantez zorunlu)
- FullCalendar + recharts → `next/dynamic` lazy loading

### API

- `ApiResponse<T>` discriminated union: `plan_limit?: PlanLimitInfo` (402), `retry_after` (429)
- `extractErrorMessage()` obje detail'lerden `message` çıkarır
- TagInput: `split(/[,;\n\t]+/)` + case-insensitive dedup + auto-commit

### Aspect Ratio

- Backend `/media-models/active`'ten curated list intersection
- contentType geçişinde desteklenmeyen ratio → `availableAspectRatios[0].id`'ye sıfırlama
- Image: 5 ratio (1:1, 9:16, 4:5, 2:3, 16:9), Video: 3 ratio

### Carousel

- `activeSlideIndex` + büyük önizleme + thumbnail strip + per-slide download
- Polling: 3sn'de bir `slides` JSONB okunur
- IIFE pattern: JSX içinde `(() => { ... })()` ile sorted slides

### Pinterest

- Frontend 4 sayfada platform desteği var
- Backend `PLATFORM_DEFAULTS` destekliyor
- **Kısıt:** `upload_post.py`'de Pinterest yayınlama desteği yok — üretilebilir ama otomatik yayınlanamaz
