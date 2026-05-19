# AGENTS.md

> Bu dosyanın marker'lı bloğu `/sync-agents-md` komutu tarafından
> Codex'in CLAUDE.md damıtması ile üretilir. Marker dışına manuel
> içerik ekleyebilirsin — korunur.

<!-- BEGIN CODEX-DISTILLED -->
> Bu icerik Codex CLI icin /root/otomaix/apps/social/frontend/CLAUDE.md'den damitilmistir.

## Proje Amacı

Otomaix Social uygulamasının Next.js 14 App Router frontendidir. `app.otomaix.com` üzerinde çalışır.

Uygulama kapsamı:

- AI destekli sosyal medya içerik üretimi
- İçerik takvimi
- Otomatik yayın
- Trend ve rakip analizi
- Fiyatlandırma
- Onboarding

## Proje Kılavuzları

- Genel mimari: `~/otomaix/docs/00-platform-mimari.md`
- Phase kılavuzları: `~/otomaix/docs/01-social-phase1.md` ... `04-social-phase4.md`

## Deploy

- IP: `178.104.7.200`
- Coolify servis adı: `otomaix-social-frontend`
- URL: `https://app.otomaix.com`
- Dockerfile: multi-stage, `node:20-alpine`, standalone output

## Bağımlılıklar

- Backend API: `https://api.otomaix.com`
- Supabase Auth: JWT authentication, Google OAuth ve email/password
- Cloudflare R2 CDN: `assets.otomaix.com`

## Environment Değişkenleri

Gerekli public env değişkenleri:

```env
NEXT_PUBLIC_SUPABASE_URL=https://sqplkkivtkfyozrvnybe.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=...
NEXT_PUBLIC_API_URL=https://api.otomaix.com
NEXT_PUBLIC_ASSETS_URL=https://assets.otomaix.com
```

Opsiyonel değişkenler:

```env
NEXT_PUBLIC_POSTHOG_KEY=
NEXT_PUBLIC_POSTHOG_HOST=
NEXT_PUBLIC_SENTRY_DSN=
NEXT_PUBLIC_CRISP_WEBSITE_ID=
```

## Klasör Yapısı

Ana App Router yapısı:

- `app/page.tsx`: public landing page
- `app/globals.css`: Tailwind ve FullCalendar override’ları
- `app/(auth)/login/page.tsx`: Google OAuth ve email/password login
- `app/(auth)/kayit/page.tsx`: kayıt ve email doğrulama
- `app/auth/callback/page.tsx`: OAuth callback handler
- `app/(onboarding)/onboarding/page.tsx`: 7 adımlı onboarding wizard
- `app/(dashboard)/layout.tsx`: auth koruması, `/auth/init`, providers
- `app/(dashboard)/dashboard/page.tsx`: genel bakış, trend widget, stats
- `app/(dashboard)/icerik-olustur/page.tsx`: 3 adımlı içerik üretim wizard
- `app/(dashboard)/icerik-kutuphanesi/page.tsx`: masonry grid, detail modal, carousel slider
- `app/(dashboard)/takvim/page.tsx`: FullCalendar, drag/drop, tatil gösterimi
- `app/(dashboard)/otomatik-yayin/page.tsx`: 4 adımlı autoposting wizard
- `app/(dashboard)/marka-ayarlari/page.tsx`: 6 sekmeli marka yönetimi
- `app/(dashboard)/markalar/page.tsx`: çoklu marka grid ve CRUD
- `app/(dashboard)/trendler/page.tsx`: Gündem, Sektör, Kişisel sekmeleri
- `app/(dashboard)/rakip-analizi/page.tsx`: rakip kartları ve analiz detayları
- `app/(dashboard)/fiyatlandirma/page.tsx`: Paddle checkout plan kartları
- `app/(dashboard)/faturalandirma/page.tsx`: mevcut plan, kullanım, portal
- `app/(dashboard)/ayarlar/page.tsx`: kullanıcı ayarları

Önemli component alanları:

- `components/billing/UpgradeModal.tsx`: 402 plan limit modalı
- `components/content/ContentCard.tsx`: içerik kartı, carousel badge dahil
- `components/layout/Sidebar.tsx`: 250px sidebar, BrandSwitcher, TrialBanner
- `components/layout/BrandSwitcher.tsx`: marka dropdown
- `components/providers/`: PostHog ve Crisp provider’ları
- `components/templates/DynamicForm.tsx`: 6 field tipi, gruplandırma, text overlay toggle
- `components/templates/CaptionEditor.tsx`: platform sekmeli caption ve hashtag editörü
- `components/ui/`: shadcn/ui, base-nova theme, `@base-ui/react`

Önemli lib alanları:

- `lib/api.ts`: `apiFetch`, `ApiResponse<T>`, 402/429 handling
- `lib/api/`: API client modülleri
- `lib/store.ts`: Zustand state, user/workspace/brands/currentBrand
- `lib/supabase.ts`: Supabase client
- `lib/analytics.ts`: typed PostHog event wrapper
- `lib/templates.types.ts`: backend Pydantic modelleriyle birebir TypeScript interface’leri
- `lib/products.types.ts`: ürün/hizmet TypeScript interface’leri

## Önemli Paketler

- `@base-ui/react`: shadcn base-nova UI primitives
- `@fullcalendar/react`, daygrid, timegrid, interaction: takvim
- `recharts`: dashboard ve CRM grafikleri
- `sonner`: toast bildirimleri
- `zustand`: global state
- `posthog-js`: analytics
- `@sentry/nextjs`: error monitoring

## İçerik Üretim Akışı

`icerik-olustur` sayfasında wizard state machine kullanılır:

- `mode: 'template' | 'free'`
- `phase: 'pick' | 'form' | 'caption'`

Akış kuralları:

- Image ve Carousel için caption-first Akış C kullanılır: pick → form → caption → görsel üret → Step 3
- Video, Special Day ve Quote tek-tık akıştır; caption ayrı değildir
- Genel şablonlar auto-select edilir
- Sektör şablonları terk edilmiştir
- Image template: `genel-gorsel-sablon`
- Carousel template: `carousel-genel-sablon`
- `TemplateGrid` ve sektör filtreleme altyapısı mevcut ama aktif kullanılmaz
- Ürün/Hizmet akışı: `imageSubType: 'general' | 'product'`
- Ürün seçilince form pre-fill yapılır ve `product_id` gönderilir

## Auth Kuralları

- Supabase session `localStorage`’da tutulur, cookie kullanılmaz
- Middleware auth için kullanılmaz, no-op kabul edilir
- `onAuthStateChange` içinde `INITIAL_SESSION` event’ı beklenir
- `getSession()` kullanılmaz; race condition riski vardır
- Auth koruması `layout.tsx` içinde yapılır, middleware’de değil

## State ve Navigation Kuralları

- Brand switching için `switchBrand()` ardından `router.push()` kullanılır
- Brand switching sırasında `<Link>` kullanılmaz; state sıralaması belirsiz olabilir
- Seçili marka `localStorage` içinde `otomaix_selected_brand_id` anahtarıyla persist edilir
- Publish guard için `useRef` senkron guard kullanılmalıdır: `publishingRef`
- Publish guard için yalnızca `useState` kullanmak async race condition riski taşır

## UI Kuralları

- Blob URL preview için `<img>` kullanılmalıdır
- R2 URL için `<Image>` / `next/image` kullanılmalıdır
- `next/image`, blob URL’leri sunucudan fetch etmeye çalıştığı için blob preview’da kullanılmaz
- SSR hydration sorunlarını önlemek için `new Date()` component body’sinde kullanılmaz
- Tarih gibi dinamik değerler için `useEffect` + `useState` pattern’i kullanılır
- Select label rendering için `Select.Value` içinde `{(value) => labels[value]}` pattern’i kullanılır
- Raw slug render edilmemelidir
- Tailwind data-attribute variant yazımında köşeli parantez zorunludur: `data-[orientation=horizontal]:flex-col`
- FullCalendar ve Recharts `next/dynamic` ile lazy load edilmelidir

## API Kuralları

- `ApiResponse<T>` discriminated union pattern’i kullanılır
- 402 plan limit bilgisi `plan_limit?: PlanLimitInfo` ile taşınır
- 429 rate limit bilgisi `retry_after` ile taşınır
- `extractErrorMessage()` obje detail alanlarından `message` çıkarır
- TagInput split pattern’i: `split(/[,;\n\t]+/)`
- TagInput case-insensitive dedup yapar
- TagInput auto-commit davranışı destekler

## Aspect Ratio Kuralları

- Desteklenen aspect ratio listesi backend `/media-models/active` endpoint’inden gelen curated list intersection ile belirlenir
- `contentType` değiştiğinde mevcut ratio desteklenmiyorsa `availableAspectRatios[0].id` değerine sıfırlanır
- Image için 5 ratio vardır: `1:1`, `9:16`, `4:5`, `2:3`, `16:9`
- Video için 3 ratio vardır

## Carousel Kuralları

- Carousel görüntülemede `activeSlideIndex`, büyük önizleme, thumbnail strip ve per-slide download bulunur
- Polling her 3 saniyede bir `slides` JSONB alanını okur
- JSX içinde sorted slides gibi lokal hesaplar için IIFE pattern’i kullanılabilir: `(() => { ... })()`

## Pinterest Kısıtı

- Frontend içinde 4 sayfada Pinterest platform desteği vardır
- Backend `PLATFORM_DEFAULTS` Pinterest’i destekler
- Ancak `upload_post.py` içinde Pinterest yayınlama desteği yoktur
- Pinterest içeriği üretilebilir, fakat otomatik yayınlanamaz

## Dokümantasyon ve Drift Koruma

Bu tür proje talimat dosyaları yalnızca şu bilgileri içermelidir:

- Proje yapısı
- Env bilgisi
- Deploy bilgisi
- Konvansiyonlar

Bu dosyalara sprint logu, aktif iş kaydı, karar geçmişi veya changelog eklenmemelidir.

Kalıcı kayıt yerleri:

- Kararlar: `/root/otomaix-brain/decisions/`
- Değişiklik/query/ingest/lint kayıtları: `/root/otomaix-brain/log.md`
- Değerli sentez ve araştırma sonuçları: `/root/otomaix-brain/research/`
<!-- END CODEX-DISTILLED -->
