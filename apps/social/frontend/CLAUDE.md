# Social Frontend — CLAUDE.md

## Proje Amacı
Otomaix Social uygulamasının Next.js 14 frontend'i. app.otomaix.com'da çalışır.

## 2026-04-14 — F-2 rev-3: Publish butonları yarış koşulu fix

Canlı test: tek "Şimdi Yayınla" tıklamasına Instagram 4 post yayınladı. Sebep: `useState` tabanlı `publishing` guard'ı async — React state update tamamlanmadan önce gelen ikinci click geçip yeni HTTP isteği fırlatıyor. Hızlı birkaç tıklama (veya kullanıcı mashlaması) birden çok publish çağrısına dönüşüyor.

Fix: tüm publish handler'larına `useRef` tabanlı **senkron** guard eklendi:
- `icerik-kutuphanesi/page.tsx` — `publishingRef` (modal), `publishInFlightRef: Set<string>` (kart hover butonu için per-post kilit)
- `icerik-olustur/page.tsx` — `publishingRef`
- `takvim/page.tsx` — `publishingRef`
- `STATUS_LABEL` sözlüklerine yeni `'publishing'` durumu eklendi → "Yayınlanıyor"

Backend tarafında asıl düzeltme `publish_post` içinde `SELECT FOR UPDATE` + intermediate `status='publishing'` ile idempotency. Frontend guard'ları UX (spinner görünsün, buton disabled olsun) için, backend guard ise veri bütünlüğü için.

## 2026-04-14 — F-2 rev-2: Upload-Post backend refactor (frontend değişmedi)

Mevcut F-2 frontend'i (dashboard + marka-ayarlari) hiçbir değişiklik gerektirmedi — aynı API sözleşmesi (`GET /social/oauth-link`, `GET /social/accounts`) korundu. Semantik değişiklik sadece backend'de:
- `oauth-link` response'u artık Upload-Post'un kendi `access_url`'sini içeriyor (`https://app.upload-post.com/connect?token=...`). Bu URL `window.open()` ile popup olarak açılıyor, kullanıcı bağlama işlemini Upload-Post arayüzünde tamamlıyor, işlem bitince `redirect_url` ile `marka-ayarlari?tab=sosyal&connected=1`'e geri dönüyor.
- `accounts` endpoint'i her çağrıda Upload-Post'tan sync yapıyor — dashboard açılınca veya sosyal sekmesi açılınca güncel durum görünüyor (cache gecikmesi yok).

## 2026-04-14 — F-2: Dashboard "Bağla" butonları + marka-ayarlari OAuth fix

### dashboard/page.tsx
- `PLATFORMS` dizisine `key` alanı eklendi (`instagram`, `tiktok`, `linkedin`).
- `connectedPlatforms: string[]` state + `useEffect` ile `GET /social/accounts?brand_id=...` çağrılıyor — aktif marka değişince yeniden yüklenir.
- "Bağla" butonu artık `handleConnectPlatform()` çağırır → `GET /social/oauth-link?brand_id=...&platform=...` → `window.open(url, '_blank', 'noopener')`.
- Bağlı platformlar için buton "Bağlı ✓" (secondary variant); değilse "Bağla" (outline). Loading'de spinner.
- "Bağlı Platform" stat kartı artık `connectedPlatforms.length` gösterir (önceden hardcoded 0).

### marka-ayarlari/page.tsx
- **KRİTİK FIX**: `connectSocialAccount()` `brand_id` parametresini gönderiyordu — backend `oauth_link` endpoint'i `brand_id`'yi zorunlu UUID query param olarak istediği için her çağrı 422 dönüyordu (özellik tamamen kırıktı).
- Şimdi `?brand_id=${brand.id}&platform=${platform}` formatında gönderiliyor; `noopener` flag eklendi.
- Yeni state: `connectedAccounts`, `connectingPlatform`. Sosyal sekmesi açıldığında `GET /social/accounts` çağrılır.
- Bağlı platformlar için yeşil ✓ + `account_name` gösterilir; buton "Hesabı Bağla" yerine "Yeniden Bağla" yazar.
- Loading state'i butonda spinner ile gösterilir.

## 2026-04-14 — F-3: İçerik Oluştur Step 3 butonları aktive edildi

`icerik-olustur/page.tsx` Step 3'te daha önce stub olan iki buton artık çalışıyor:
- **Şimdi Yayınla** → `persistCaption()` (PATCH /posts/{id}) → `POST /posts/{id}/publish` → `/icerik-kutuphanesi`'ne yönlendir
- **Takvime Ekle** → custom date dialog (datetime-local input) → caption kaydet → `PATCH /calendar/schedule/{id}` → `/takvim`'e yönlendir
- Buton state'leri: `publishing`, `scheduling`, `showScheduleDialog`, `scheduleAt`. Hepsi loading spinner ile disable olur. `output_url` yokken her iki buton disable.
- Plan limit dönerse `UpgradeModal` gösterilir (publish endpoint'i de check_plan_limit'e tabi değil ama yine de güvenlik için).
- Geçmiş tarih validasyonu client-side yapılıyor; backend zaten `assert_post_owned` ile sahiplik kontrolü yapıyor.
- `useRouter` import'u eklendi (`next/navigation`).

## 2026-04-14 — Plan limit (HTTP 402) handling

`lib/api.ts` HTTP 402 yanıtlarını artık özel olarak yakalıyor:
- Backend'in `detail: { error, message, upgrade_url, current_plan }` objesi `ApiResponse.plan_limit` alanına mapleniyor.
- `ApiResponse<T>` discriminated union'a `plan_limit?: PlanLimitInfo` eklendi.
- Daha önce `body.detail` bir obje olduğunda string concat → `"[object Object]"` yazıyordu. Yeni `extractErrorMessage()` helper'ı obje detail'lerden `message` alanını çıkarır.

Paywall modal entegrasyonu yapılan sayfalar:
- `markalar/page.tsx` — yeni marka oluştururken brand limit aşımında `UpgradeModal`
- `marka-ayarlari/page.tsx` — avatar oluştururken avatar limit aşımında `UpgradeModal`
- `icerik-olustur/page.tsx` — image/video/special_day/quote üretirken post/video limit aşımında `UpgradeModal` (4 dalın hepsi)
- `trendler/page.tsx`, `dashboard/page.tsx` — trend kartından içerik üretirken plan_limit toast mesajı
- `onboarding/page.tsx` — first brand create için plan_limit toast (genelde isabet etmez)

`UpgradeModal` zaten mevcuttu (`components/billing/UpgradeModal.tsx`).

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
- Deploy: Coolify (servis adı: otomaix-social-frontend)
- URL: https://app.otomaix.com

## Bağımlılıklar
- Backend API: https://api.otomaix.com
- Supabase Auth: JWT authentication
- Cloudflare R2: assets.otomaix.com

## Gerekli .env.local Değişkenleri
```
NEXT_PUBLIC_SUPABASE_URL=https://sqplkkivtkfyozrvnybe.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...  ← Dolu ✅
NEXT_PUBLIC_API_URL=https://api.otomaix.com
NEXT_PUBLIC_ASSETS_URL=https://assets.otomaix.com
```

## Tamamlanan İşler

### Phase 1
- [x] Next.js 14 projesi kuruldu
  - shadcn/ui (base-nova theme) + Tailwind CSS
  - Zustand store (user, currentWorkspace, currentBrand)
  - Supabase auth (Google OAuth + email/password)
  - 250px sabit sidebar layout + SidebarNav (Türkçe route'lar)
  - Dashboard iskelet sayfası
  - Dockerfile (multi-stage, standalone output)
  - middleware.ts (auth koruması — sonradan kaldırıldı, layout'a taşındı)
  - `app/auth/callback/page.tsx` — Google OAuth callback handler

### Phase 2
- [x] Adım 1b — Marka Ayarları (`/marka-ayarlari`)
  - 5 sekme: Marka Bilgileri, Marka Kimliği, Görseller, Sosyal Hesaplar, Dokümanlar
  - Debounce otomatik kaydetme (1.5s) + "Kaydedildi ✓" göstergesi
  - Renk seçici, font seçici (letterCase), hashtag tag-input
  - Logo upload (light/dark) + intro video upload → R2
  - Sonner toast provider entegre edildi
  - **OAuth callback handling**: `useSearchParams` ile `?connected=platform` ve `?error=...` query parametreleri işlenir
    - Başarılı bağlantı → success toast + "sosyal" sekmesine otomatik geçiş
    - Hata → error toast
    - URL `window.history.replaceState` ile temizlenir
    - `<Tabs value={activeTab} onValueChange={setActiveTab}>` (controlled)

- [x] Adım 2b — İçerik Oluşturma Wizard (`/icerik-olustur`)
  - 3 adımlı React state machine (URL değişmez)
  - Adım 1: 5 içerik tipi kartı (tümü aktif), kategori seçimi (special_day/quote için gizlenir)
    - `image`, `carousel`, `video` → mevcut pipeline
    - `special_day` → `/calendar/holidays` API'den tatil listesi, kullanıcı seçer
    - `quote` → alıntı metni + opsiyonel yazar alanı
  - Adım 2 sıralaması: En-Boy Oranı → Platformlar → Dokümanlar → İçerik Açıklaması → Bana Fikir Öner → İçerik Üret
  - Adım 2 (type'a göre farklı UI):
    - `image`/`carousel`: En-Boy Oranı + Platformlar + Dokümanlar + İçerik Açıklaması + "Bana fikir öner" (3 öneri)
    - `video`: İçerik Açıklaması + Script editörü + ses seçimi (mor tema)
    - `special_day`: Tatil grid (scrollable, geçmiş tatiller soluk) + opsiyonel not alanı (sarı tema)
    - `quote`: Alıntı textarea + yazar inputu (mor tema)
  - "Kendi metnini ekle" toggle kaldırıldı — tek alan: İçerik Açıklaması
  - **"Bana fikir öner"**: `POST /ai/suggest-ideas` → sabit **3 öneri** döner
    - Gönderilen bağlam: `content_type`, `content_category`, `prompt`, `document_ids`, `platforms`
    - Backend RAG ile seçili doküman içeriğini de prompt'a dahil eder
    - İçerik tipine özel talimat: video için senaryo fikirleri, görsel için tasarım fikirleri vb.
  - Adım 3: Üretim animasyonu, görsel önizleme, caption + hashtag editörü, eylem butonları
  - **Validasyon**: `special_day` → selectedHoliday zorunlu; `quote` → quoteText zorunlu; diğerleri → prompt zorunlu
  - **State**: `holidays[]`, `selectedHoliday`, `quoteText`, `quoteAuthor` eklendi
  - **Backend**: `POST /posts/generate` → `content_type: 'special_day' | 'quote'` ile çağrılır

- [x] Adım 3 — İçerik Kütüphanesi (`/icerik-kutuphanesi`)
  - ContentCard bileşeni (`components/content/ContentCard.tsx`)
    - `onPublish` prop: hover "Yayınla" butonunu bağlar → `POST /posts/{id}/publish`
  - CSS columns masonry grid (3 sütun)
  - IntersectionObserver ile infinite scroll
  - Filter Sheet (sağdan, tip/durum/platform)
  - Post detail Dialog
    - "Şimdi Yayınla" → `POST /posts/{id}/publish` (loading state, toast, status güncelleme)
    - "Onay İste" → `POST /posts/{id}/request-approval` (loading state, toast, status → 'reviewing')
    - Butonlar sadece ready/failed/rejected durumlarında aktif
  - Freemium watermark + "Filigranı Kaldır" CTA

- [x] Adım 4 — İçerik Takvimi (`/takvim`)
  - FullCalendar (dayGrid + timeGrid + interaction, Türkçe locale)
  - Aylık / Haftalık toggle
  - Durum renkleri + legend (milli tatil mor, dini bayram amber)
  - Tatil gösterimi: **her tatil için 2 event** ekleniyor
    - `holiday-bg-{date}`: `display:'background'` → renkli arka plan (milli: #7C3AED, dini: #F59E0B)
    - `holiday-label-{date}`: transparent event → `extendedProps.isHolidayLabel: true` → isim yazısı
    - ⚠️ `display:'background'` event başlık gösteremiyor — bu yüzden ayrı label event şart
    - `globals.css` → `.fc-bg-event { opacity: 0.5 }` (0.25 çok düşüktü, görünmüyordu)
  - Drag & drop → PATCH /calendar/schedule
  - Geçmiş tarih koruması + yeni içerik dialog
  - Post detay modal
    - "Şimdi Yayınla" → `POST /posts/{id}/publish` (loading, toast, event rengi güncelleme)
    - "Onay İste" → `POST /posts/{id}/request-approval` (loading, toast)

- [x] Adım 5b — Otomatik Yayın Wizard (`/otomatik-yayin`)
  - Config yoksa setup CTA, varsa Summary Dashboard
  - 4 adımlı wizard: Konular → Platformlar → Program → Özet
  - "Bana konu öner" AI butonu (Claude'dan 5 öneri)
  - Sıklık seçimi + saat dilimi picker
  - Telegram onay toggle + **müşteriye özel** Bot Token + Chat ID alanları
    - @BotFather kurulum talimatları (token için)
    - @userinfobot yönlendirmesi (chat ID için)
    - Her müşteri kendi botunu kullanır (global token yok)
  - Aktif/Pasif toggle, sonraki yayın listesi
  - `AutopostingConfig` interface: `telegram_bot_token` + `telegram_chat_id` alanları eklendi
  - `handleSave` → her iki alan API'ye gönderilir

- [x] Adım 7 — Onboarding Akışı (`/onboarding`)
  - `app/(onboarding)/layout.tsx` — koyu tam ekran layout, header logo
  - `app/(onboarding)/onboarding/page.tsx` — 7 adımlı wizard
    - Adım 1: Hoş Geldiniz kartı (3 özellik özeti)
    - Adım 2: Web Sitesi URL → `POST /ai/analyze-website` → otomatik doldur
    - Adım 3: Marka bilgileri formu (isim, açıklama, sektör, renk önizleme)
    - Adım 4: Kullanıcı tipi (Küçük İşletme / Ajans / Serbest Çalışan / Kurumsal)
    - Adım 5: Sosyal medya hedefleri (çoklu seçim)
    - Adım 6: Platform seçimi (bağlantı daha sonra)
    - Adım 7: Özet + `POST /brands` + `PATCH /brands/{id}/kit` → `/dashboard`
  - middleware.ts → artık no-op (sadece `NextResponse.next()` döner)
  - `StepIndicator` bileşeni (nokta + çizgi + label)

## Tamamlanan Deploy Adımları
- [x] Migration 002 çalıştırıldı (`002_autoposting.sql`)
- [x] Coolify deploy yapıldı (frontend + backend)

### Phase 3

#### Tamamlanan
- [x] Adım 1 — Doküman yönetimi UI
  - `app/(dashboard)/marka-ayarlari/page.tsx` → Dokümanlar sekmesi tamamen işlevsel
    - Upload (drag/click), dosya tipi kısıtı (.pdf,.doc,.docx,.xls,.xlsx,.txt)
    - Yüklenen doküman listesi (isim, boyut, RAG mod gösterimi)
    - Silme butonu + confirm dialog
  - `app/(dashboard)/icerik-olustur/page.tsx` → Step 2'de "Dokümanlardan Bağlam Ekle" bölümü
    - Markanın dokümanları listelenir, çoklu seçim mümkün
    - `selectedDocIds` → `document_ids` olarak API'ye gönderilir
  - `BrandDocument` interface eklendi (her iki sayfada)

- [x] Adım 2b — Faceless Video frontend
  - `app/(dashboard)/icerik-olustur/page.tsx` içinde "Video (Faceless)" kartı aktif edildi
  - Step 2'de video kartı seçildiğinde mor tema ile script editörü + ses seçici gösteriliyor
    - "Script Üret" butonu → `POST /ai/generate-script`
    - Script textarea (düzenlenebilir)
    - Ses seçici (`GET /posts/voices/turkish`) — default Emel (Kadın)
    - Süre tahmini göstergesi
  - Step 3'te video için ayrı önizleme:
    - Video player (output_url hazırsa) veya render-loading state
    - Script gösterimi + ses dosyası `<audio>` player
  - `TurkishVoice`, `GeneratedPost` interface'leri genişletildi
  - Video generate → `POST /posts/generate-faceless-video`

- [x] Adım 3b — AI Avatar frontend
  - `app/(dashboard)/marka-ayarlari/page.tsx` → yeni "AI Avatar" sekmesi (6. sekme)
    - Aktif avatar özet kartı (isim, tip, preview + "Video Üret" butonu)
    - Kendi avatarı: dashed upload area → `POST /avatar/create` (multipart)
    - Hazır avatarlar grid (2×4): `GET /avatar/stock` → kart tıkla → `POST /avatar/select-stock`
    - Seçili avatar üzerinde violet check işareti
  - `StockAvatar`, `ActiveAvatar` interface'leri eklendi
  - `BrandKit.avatar` alanı eklendi

- [x] Adım 4b — Rakip analizi frontend
  - `app/(dashboard)/rakip-analizi/page.tsx` oluşturuldu
    - Sol kolon: rakip kartları listesi (yenile + sil butonları)
    - Sağ kolon: analiz detay paneli (Instagram metrikleri, PieChart, web analizi)
    - "Rakip Ekle" modal → `POST /competitors`
    - "Özet Rapor" butonu → `GET /competitors/report/summary`
    - AI rapor kartı (fırsatlar + öneriler)
    - recharts PieChart (içerik dağılımı)
  - `recharts` paketi eklendi (`package.json`)

- [x] Adım 5b — Trend Analizi Frontend
  - `app/(dashboard)/trendler/page.tsx` — tam trendler sayfası
    - Kaynak filtresi (Tümü / Haber / Google Trends / Genel)
    - Trend kartları (başlık, kaynak, uyum skoru, içerik fırsatı, öneri prompt)
    - "İçerik Üret" butonu → `/trends/{index}/create-post` → kütüphaneye yönlendir
    - "Yenile" butonu → `/trends/refresh`
  - Dashboard'a "Bu Hafta Sektörünüzde Trendler" widget eklendi
    - Top 5 trend listesi, hover'da "İçerik Üret" butonu
    - "Tüm Trendler →" linki
  - SidebarNav'a "Trendler" linki eklendi (TrendingUp ikonu)

- [x] Adım 6b — Logo Overlay + Intro Video UI
  - Marka Ayarları → Görseller sekmesi zaten tamamdı:
    - Logo Filigran toggle + konum seçici + opaklık slider
    - Intro/Outro video yükleme + pozisyon seçici (Başında/Sonunda/Her İkisi)
  - Backend işleme otomatik (fal.ai webhook'ta)

- [x] Adım 7b — Paddle Ödeme Frontend
  - `app/(dashboard)/fiyatlandirma/page.tsx` — 4 plan kartı (Starter/Pro/Business/Agency)
    - Mevcut plan vurgusu, "En Popüler" badge
    - "Planı Seç" → `/billing/checkout` → Paddle'a yönlendir
  - `app/(dashboard)/faturalandirma/page.tsx`
    - Mevcut plan + durum + yenileme tarihi
    - Kullanım progress bar'ları (içerik + marka)
    - "Faturalar & Yönetim" → Paddle customer portal
    - Plan özellikleri (video/avatar aktif mi)
  - `components/billing/UpgradeModal.tsx` — 402 hatalarında gösterilecek modal
  - SidebarNav'a "Faturalandırma" linki eklendi (CreditCard ikonu)

- [x] Adım 8b — Çoklu Marka Brand Switcher
  - `lib/store.ts` → `brands[]`, `setBrands()`, `switchBrand()` eklendi; tipler export edildi
  - `app/(dashboard)/layout.tsx` → `/auth/init` ile tek çağrıda user+workspace+brands yüklendi
    - `currentBrand` otomatik olarak ilk markaya set edilir
  - `components/layout/BrandSwitcher.tsx` — sidebar dropdown bileşeni
    - Logo/avatar + marka adı + sektör gösterimi
    - Tüm markaları listeler, aktif olanı işaretler
    - "Yeni Marka Ekle" → `/markalar` sayfasına yönlendirir
  - `components/layout/Sidebar.tsx` → BrandSwitcher logo ile nav arasına eklendi
  - `app/(dashboard)/markalar/page.tsx` — marka yönetim sayfası
    - Grid görünüm, aktif marka vurgusu
    - "Yeni Marka Ekle" modal (isim, sektör, açıklama)
    - "Düzenle" → marka ayarlarına; "Sil" → confirm modal
  - SidebarNav'a "Markalar" (Building2) linki eklendi

### Phase 4

#### Tamamlanan
- [x] Adım 1b — Self-Serve Onboarding Frontend
  - `app/page.tsx` — Tam public landing page (unauthenticated)
    - Sticky header: logo + nav + "Giriş Yap" + "Ücretsiz Dene" CTA'ları
    - Hero: "Türk KOBİ'ler için AI Sosyal Medya Otomasyonu" + 14 gün ücretsiz badge
    - 6 özellik kartı (AI Görsel, Faceless Video, AI Avatar, Otomatik Yayın, Rakip Analizi, Trend Takibi)
    - İstatistik bandı (10K+ içerik, 500+ marka, 4.9★, 6 saat tasarruf)
    - 4 plan kartı (Starter/Pro/Business/Agency), "En Popüler" badge
    - Footer + final CTA bölümü
  - `app/(auth)/kayit/page.tsx` — Kayıt sayfası
    - Google OAuth (primary) + email/şifre formu
    - Email doğrulama bekle ekranı (success state)
    - "Zaten hesabınız var mı? Giriş yapın" linki
  - `components/layout/Sidebar.tsx` — Trial banner eklendi
    - `trial_ends_at` varsa "🎁 Deneme: X gün kaldı" banner gösteriliyor
    - Tıklanınca `/fiyatlandirma`'ya yönlendiriyor
    - `TrialBanner` bileşeni: kalan gün hesaplama + 0'a düşünce gizlenme
  - `lib/store.ts` — `User.trial_ends_at?: string | null` eklendi
  - `app/(onboarding)/onboarding/page.tsx` — Adım 4'e "Daha Sonra Atla" eklendi
    - Kullanıcı tipi seçilmediyse "Daha Sonra Atla →" butonu gösteriliyor
    - Seçim yapılınca normal "Devam →" butonu çıkıyor

- [x] Adım 2b — PostHog Analytics Frontend
  - `posthog-js` paketi kuruldu
  - `lib/analytics.ts` — typed event wrapper (identify/reset + 20+ typed helper, no-op key yoksa)
  - `components/providers/PostHogProvider.tsx` — PostHog init + `usePathname` pageview tracking
  - `components/providers/Providers.tsx` — PostHogProvider ile sarmalandı
  - `app/(dashboard)/layout.tsx` — `/auth/init` sonrası `posthog.identify(userId, {email, plan})`
  - `components/layout/Sidebar.tsx` — logout'ta `posthog.reset()`
  - Eventler eklenen sayfalar:
    - `fiyatlandirma/page.tsx`: `pricing_page_viewed`, `plan_selected`, `checkout_started`
    - `takvim/page.tsx`: `calendar_opened`
    - `trendler/page.tsx`: `trend_post_created`
    - `icerik-olustur/page.tsx`: `content_creation_started`, `idea_suggestion_used`, `document_reference_used`, `content_generated`
    - `onboarding/page.tsx`: `onboarding_started`, `onboarding_step_completed`, `onboarding_completed`
  - Env değişkeni: `NEXT_PUBLIC_POSTHOG_KEY`, `NEXT_PUBLIC_POSTHOG_HOST`

- [x] Adım 3b — Sentry Error Monitoring (frontend)
  - `@sentry/nextjs@8.55.1` kuruldu
  - `sentry.client.config.ts` — client init (replay entegrasyonu dahil, %5 session / %100 error)
  - `sentry.server.config.ts` — server-side init
  - `sentry.edge.config.ts` — edge runtime init
  - `instrumentation.ts` — Next.js 14 register() hook → server/edge init
  - `next.config.mjs` — `withSentryConfig` wrapper (source map upload kapalı)
  - `app/(dashboard)/layout.tsx` — `/auth/init` sonrası `Sentry.setUser({id, email})`
  - Env değişkeni: `NEXT_PUBLIC_SENTRY_DSN`

- [x] Adım 4b — Redis Cache ve Rate Limiting (frontend)
  - `lib/api.ts` → HTTP 429 yakalanıyor: `{ success: false, error: 'rate_limit', retry_after: N }`
  - `lib/api.ts` → `apiFetch` ve `apiUpload` try-catch ile sarmalandı — `TypeError: Failed to fetch` artık `{ success: false, error: message }` döndürür (sayfa donmaz)
  - `lib/api.ts` → `!res.ok` kontrolü eklendi — 401/403/500 vb. HTTP hataları da `success: false` olarak döner
  - `ApiResponse<T>` discriminated union tipi export edildi
  - `icerik-olustur/page.tsx` → rate_limit hatasında adım 2'ye geri döner + kaç saniye bekleyeceğini söyleyen toast
  - `icerik-olustur/page.tsx` → doküman bölümü her zaman gösterilir; yüklü belge yoksa Marka Ayarları → Dokümanlar linkine yönlendiren mesaj gösterilir

- [x] Adım 6 — Crisp Chat Entegrasyonu
  - `components/providers/CrispProvider.tsx` — Crisp script yükleme (vanilla JS, ekstra paket yok)
    - Türkçe locale, violet tema rengi, sağ alt köşe
    - `crispIdentify(user)` — login sonrası kimlik gönderir (email, nickname, plan, brands_count)
    - `crispReset()` — logout'ta oturum sıfırlar
  - `components/providers/Providers.tsx` — CrispProvider eklendi
  - `app/(dashboard)/layout.tsx` — `/auth/init` sonrası `crispIdentify()` çağrısı
  - `components/layout/Sidebar.tsx` — logout'ta `crispReset()` çağrısı
  - `app/globals.css` — mobilde (< 768px) Crisp widget gizlendi
  - Env değişkeni: `NEXT_PUBLIC_CRISP_WEBSITE_ID`

- [x] Adım 7 — Performance Optimizasyonu
  - DB pool min_size=5 / max_size=20
  - /health endpoint DB + Redis kontrol
  - 011_performance_indexes.sql — posts/chunks/trend_cache CONCURRENTLY index'ler
  - FullCalendar + recharts → next/dynamic lazy loading (ayrı chunk)
  - FullCalendar ref: CalendarApi ref (dynamic component compat)

- [x] Adım 8 — Load Testing
  - `shared/load-tests/locustfile.py` — 6 senaryo, JWT/HealthOnly modları
  - Smoke test geçti: /health 5ms, /billing/plans 5ms, 0 hata

### Phase 4 Tamamlandı ✅

## Mevcut Durum
- Social Frontend: **Tüm fazlar tamamlandı** (Phase 1–4) ✅
- CRM Admin Paneli: **Tüm adımlar tamamlandı** (Adım 1–8) ✅
  - https://crm.otomaix.com canlıda
  - Social frontend'de yapılacak iş yok

## Paket Listesi (önemli)
- `@fullcalendar/react` + daygrid + timegrid + interaction + core
- `sonner` (toast)
- `@base-ui/react` (shadcn base-nova — Select, Sheet, Dialog, vb.)

## Teknik Notlar
- `@base-ui/react` Select `onValueChange` → `string | null` döner
  → `onSelect(v, fn)` helper kullanılıyor (`null` filtreler)
- BrandKit `case` alanı TypeScript keyword çakışması nedeniyle `letterCase` olarak yeniden adlandırıldı
  → Backend JSONB'deki eski `case` değerleri deepMerge'de her ikisi de okunuyor
- `api.patch()` ve `api.upload()` (multipart) `lib/api.ts`'e eklendi
- FullCalendar CSS override'ları `app/globals.css`'e eklendi

## Önemli Kararlar
- Tüm tarihler UTC olarak saklanır
- App Router kullanılıyor (Next.js 14)
- Türkçe varsayılan dil
- next-intl kurulmadı (tr.json manuel yönetiliyor — basit tutmak için)
- Supabase client SSR'da no-op, yalnızca client-side çalışıyor
- Supabase session **localStorage**'da tutulur (cookie değil) → middleware'den okunamaz
  - Auth koruması `app/(dashboard)/layout.tsx`'te `onAuthStateChange` ile yapılır
    - `getSession()` **kullanılmıyor** — Google OAuth hash fragment işlenmeden önce null dönebilir (race condition)
    - `onAuthStateChange` mount anında `INITIAL_SESSION` event'ı ile hemen tetiklenir; session varsa `/auth/init` çağrılır, yoksa `/login`'e yönlendirir
  - Google OAuth sonrası `/auth/callback` sayfası `onAuthStateChange` ile session'ı bekler, sonra `/dashboard`'a yönlendirir
  - `login/page.tsx`'te `redirectTo: window.location.origin + '/auth/callback'` kullanılır
- SSR hydration: `new Date()` / `Date.now()` komponent body'sinde kullanılmaz, `useEffect` içinde `useState` ile alınır
  - `getGreeting()` (dashboard/page.tsx) ve `TrialBanner` (Sidebar.tsx) bu kurala göre düzenlendi
- Tiptap yerine Textarea kullanıldı (caption editörü) — daha az bağımlılık
