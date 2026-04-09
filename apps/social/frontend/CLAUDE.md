# Social Frontend — CLAUDE.md

## Proje Amacı
Otomaix Social uygulamasının Next.js 14 frontend'i. app.otomaix.com'da çalışır.

## VPS Bilgileri
- IP: 178.104.7.200
- Deploy: Coolify (servis adı: otomaix-social-frontend)
- URL: https://app.otomaix.com

## Bağımlılıklar
- Backend API: https://api.otomaix.com
- Supabase Auth: JWT authentication
- Cloudflare R2: assets.otomaix.com

## Gerekli .env.local Değişkenleri
NEXT_PUBLIC_SUPABASE_URL=https://sqplkkivtkfyozrvnybe.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=  ← BU DOLDURULMALI (Supabase dashboard'dan al)
NEXT_PUBLIC_API_URL=https://api.otomaix.com
NEXT_PUBLIC_ASSETS_URL=https://assets.otomaix.com

## Tamamlanan İşler
- [x] Phase 1 Step 4 — Next.js 14 projesi kuruldu
  - shadcn/ui (base-nova theme) + Tailwind CSS
  - Zustand store (user, currentWorkspace, currentBrand)
  - Supabase auth (Google OAuth + email/password)
  - 250px sabit sidebar layout
  - Dashboard iskelet sayfası
  - Dockerfile (multi-stage, standalone output)
  - middleware.ts (auth koruması)
- [x] Phase 2 Adım 1b — Marka Ayarları frontend (5 sekme)
  - app/(dashboard)/marka-ayarlari/page.tsx
  - 5 sekme: Marka Bilgileri, Marka Kimliği, Görseller, Sosyal Hesaplar, Dokümanlar
  - Debounce ile otomatik kaydetme (1.5s)
  - Logo upload (light/dark), intro video upload
  - Renk seçici, font seçici, hashtag girişi
  - sonner toast entegrasyonu
  - SidebarNav Türkçe route'larla güncellendi

## Devam Eden İş
Phase 1 Step 5c — Coolify UI'da manuel servis kurulumu (MANUEL)

## Bir Sonraki Adım
1. Coolify'da deploy yap
2. Phase 2 Adım 2: İçerik Oluşturma Wizard (icerik-olustur)
3. Phase 2 Adım 3: İçerik Kütüphanesi (icerik-kutuphanesi)

## Teknik Notlar
- @base-ui/react Select'in onValueChange callback'i string | null döner
  → onSelect() helper kullanılıyor (null'ı filtreler)
- BrandKit'te CSS `case` keyword çakışması nedeniyle `letterCase` kullanıldı
- Fonts deepMerge: backend JSONB'den gelen `case` alanı `letterCase`'e map ediliyor

## Önemli Kararlar
- Tüm tarihler UTC olarak saklanır
- App Router kullanılıyor (Next.js 14)
- Türkçe varsayılan dil
- next-intl kurulmadı (tr.json manuel yönetiliyor — basit tutmak için)
- Supabase client SSR'da no-op, yalnızca client-side çalışıyor
