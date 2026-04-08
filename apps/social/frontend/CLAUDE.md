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
  - shadcn/ui + Tailwind CSS
  - Zustand store (user, currentWorkspace, currentBrand)
  - Supabase auth (Google OAuth + email/password)
  - 250px sabit sidebar layout
  - Dashboard iskelet sayfası
  - Dockerfile (multi-stage, standalone output)
  - middleware.ts (auth koruması)

## Devam Eden İş
Phase 1 Step 5 — Coolify'da deploy yapılandırması

## Bir Sonraki Adım
1. NEXT_PUBLIC_SUPABASE_ANON_KEY'i .env.local'e ekle
2. Coolify'da otomaix-social-frontend servisini oluştur
3. ~/otomaix/docs/01-social-phase1.md Step 5'ten devam et

## Önemli Kararlar
- Tüm tarihler UTC olarak saklanır
- App Router kullanılıyor (Next.js 14)
- Türkçe varsayılan dil
- next-intl kurulmadı (tr.json manuel yönetiliyor — basit tutmak için)
- Supabase client SSR'da no-op, yalnızca client-side çalışıyor
