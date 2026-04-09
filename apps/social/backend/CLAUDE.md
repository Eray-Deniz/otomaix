# Social Backend — CLAUDE.md

## Proje Amacı
Otomaix Social uygulamasının FastAPI backend'i. api.otomaix.com'da çalışır.

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
- fal.ai, Cloudflare R2, Upload-Post.com, Supabase Auth

## Tamamlanan İşler
- [x] Phase 1 Step 3 — FastAPI proje yapısı kuruldu
  - app/main.py, core/, routers/, models/, services/ oluşturuldu
  - Supabase JWT middleware (JWKS tabanlı)
  - Cloudflare R2 storage abstraction
  - fal.ai async generation + webhook
  - Upload-Post.com OAuth + publish
  - Dockerfile + .dockerignore
- [x] Phase 1 Step 5 — Coolify deploy yapılandırması
  - 5a: Backend Dockerfile ✅ (zaten mevcut)
  - 5c: Coolify UI'da servis oluşturma (MANUEL — yapılması gerekiyor)
- [x] Phase 1 Step 6 — Test scripti oluşturuldu
  - ~/otomaix/shared/test_phase1.sh

## Devam Eden İş
Phase 1 Step 5c — Coolify UI'da manuel servis kurulumu (MANUEL)

## Bir Sonraki Adım
1. Coolify UI'da `otomaix-social-backend` ve `otomaix-social-frontend` servislerini oluştur
2. Deploy sonrası: `bash ~/otomaix/shared/test_phase1.sh` ile test et
3. Tüm testler geçince → ~/otomaix/docs/02-social-phase2.md ile devam et
