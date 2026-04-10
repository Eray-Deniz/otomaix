# Social Frontend — CLAUDE.md

## Proje Amacı
Otomaix Social uygulamasının Next.js 14 frontend'i. app.otomaix.com'da çalışır.

## Proje Kılavuzları (DEĞİŞTİRME)

Genel mimari: ~/otomaix/docs/00-platform-mimari.md
Phase 1: ~/otomaix/docs/01-social-phase1.md
Phase 2: ~/otomaix/docs/02-social-phase2.md  ← AKTİF
Phase 3: ~/otomaix/docs/03-social-phase3.md
Phase 4: ~/otomaix/docs/04-social-phase4.md
CRM: ~/otomaix/docs/05-crm-admin.md

Her session başında 00-platform-mimari.md ve ← AKTİF olan dosyayı oku.
Phase tamamlanınca sadece ← AKTİF etiketini bir sonraki satıra taşı.

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
  - middleware.ts (auth koruması)

### Phase 2
- [x] Adım 1b — Marka Ayarları (`/marka-ayarlari`)
  - 5 sekme: Marka Bilgileri, Marka Kimliği, Görseller, Sosyal Hesaplar, Dokümanlar
  - Debounce otomatik kaydetme (1.5s) + "Kaydedildi ✓" göstergesi
  - Renk seçici, font seçici (letterCase), hashtag tag-input
  - Logo upload (light/dark) + intro video upload → R2
  - Sonner toast provider entegre edildi

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
  - Telegram onay toggle + bot kurulum talimatları
  - Aktif/Pasif toggle, sonraki yayın listesi

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
  - middleware.ts → `/onboarding/*` auth koruması eklendi
  - `StepIndicator` bileşeni (nokta + çizgi + label)

## Tamamlanan Deploy Adımları
- [x] Migration 002 çalıştırıldı (`002_autoposting.sql`)
- [x] Coolify deploy yapıldı (frontend + backend)

## Bir Sonraki Adım
1. **Phase 2 Adım 6** — n8n Telegram onay workflow'u (n8n-mcp ile)
2. **Phase 2 Adım 5c** — n8n Auto Posting Scheduler workflow'u
3. **Phase 2 kontrol listesini tamamla** → `~/otomaix/docs/02-social-phase2.md`
4. **Phase 3'e geç** — Rakip analizi, raporlama, fatura/abonelik

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
- Tiptap yerine Textarea kullanıldı (caption editörü) — daha az bağımlılık
