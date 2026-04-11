# Social Frontend — CLAUDE.md

## Proje Amacı
Otomaix Social uygulamasının Next.js 14 frontend'i. app.otomaix.com'da çalışır.

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
  - Adım 1: 5 içerik tipi kartı (Görsel/Carousel aktif, 3 "Yakında"), kategori seçimi
  - Adım 2: Prompt, "Bana fikir öner" AI butonu, aspect ratio, platform seçimi
  - Adım 3: Üretim animasyonu, görsel önizleme, caption + hashtag editörü, eylem butonları

- [x] Adım 3 — İçerik Kütüphanesi (`/icerik-kutuphanesi`)
  - ContentCard bileşeni (`components/content/ContentCard.tsx`)
  - CSS columns masonry grid (3 sütun)
  - IntersectionObserver ile infinite scroll
  - Filter Sheet (sağdan, tip/durum/platform)
  - Post detail Dialog
  - Freemium watermark + "Filigranı Kaldır" CTA

- [x] Adım 4 — İçerik Takvimi (`/takvim`)
  - FullCalendar (dayGrid + timeGrid + interaction, Türkçe locale)
  - Aylık / Haftalık toggle
  - Durum renkleri + legend
  - Resmi tatil background events
  - Drag & drop → PATCH /calendar/schedule
  - Geçmiş tarih koruması + yeni içerik dialog
  - Post detay modal

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

#### Bir Sonraki Adım — Phase 3 Adım 6 (Logo Overlay + Intro Video UI)
**Marka Kit güncelleme:**
- Marka Ayarları → Logo Overlay sekmesi/bölümü
  - Logo bindirme konumu seçici (köşeler)
  - Opaklık slider
- Video içeriklerinde intro video ekleme toggle'ı

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
  - Auth koruması `app/(dashboard)/layout.tsx`'te client-side `getSession()` ile yapılır
  - Google OAuth sonrası `/auth/callback` sayfası `onAuthStateChange` ile session'ı bekler, sonra `/dashboard`'a yönlendirir
  - `login/page.tsx`'te `redirectTo: window.location.origin + '/auth/callback'` kullanılır
- Tiptap yerine Textarea kullanıldı (caption editörü) — daha az bağımlılık
