# Otomaix Social — Yerel / On-Premise Kurulum Kılavuzu

Bu paket, Otomaix Social uygulamasını kendi sunucunuzda veya local makinenizde çalıştırmanızı sağlar.

---

## Gereksinimler

| Araç | Minimum Sürüm | Kontrol |
|---|---|---|
| Docker | 24.0+ | `docker --version` |
| Docker Compose | v2 (plugin) | `docker compose version` |
| RAM | 4 GB | — |
| Disk | 20 GB | — |

> **Not:** Docker Desktop (Mac/Windows) kuruluysa Compose otomatik gelir.

---

## Hızlı Kurulum

```bash
# 1. Bu klasöre gelin
cd local-deployment

# 2. Setup scriptini çalıştırın
bash setup.sh
```

Script ilk çalışmada `.env.example` dosyasını `.env` olarak kopyalar ve sizi durdurur.
`.env` dosyasını doldurup scripti tekrar çalıştırın — geri kalan her şeyi otomatik yapar.

---

## Manuel Kurulum Adımları

### 1. .env dosyasını hazırlayın

```bash
cp .env.example .env
nano .env   # veya istediğiniz editörle açın
```

**Mutlaka doldurulması gerekenler:**

| Değişken | Nereden alınır |
|---|---|
| `POSTGRES_PASSWORD` | Kendiniz belirleyin (güçlü bir şifre) |
| `SUPABASE_URL` | Supabase Dashboard → Settings → API |
| `SUPABASE_SERVICE_KEY` | Supabase Dashboard → Settings → API → service_role |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase URL ile aynı |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Supabase Dashboard → Settings → API → anon public |
| `FAL_KEY` | [fal.ai](https://fal.ai) Dashboard |
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) |
| `INTERNAL_API_KEY` | Kendiniz belirleyin (rastgele 32 karakter) |
| `N8N_ENCRYPTION_KEY` | Kendiniz belirleyin (rastgele 32+ karakter, **bir kez ayarlayın**) |

### 2. Servisleri başlatın

```bash
# PostgreSQL ve Redis'i başlat
docker compose up -d postgres redis

# Migration'ları çalıştır
bash migrations/run-migrations.sh

# Tüm servisleri başlat
docker compose up -d
```

### 3. Servislerin durumunu kontrol edin

```bash
docker compose ps
docker compose logs -f
```

---

## Servis URL'leri

| Servis | URL | Açıklama |
|---|---|---|
| Frontend | http://localhost:3000 | Uygulama arayüzü |
| Backend API | http://localhost:8000/docs | Swagger dokümantasyonu |
| n8n | http://localhost:5678 | İş akışı otomasyonu |
| PostgreSQL | localhost:5432 | Veritabanı (direct) |
| Redis | localhost:6379 | Cache ve rate limiting |

---

## n8n Workflow'larını İçe Aktarma

1. http://localhost:5678 adresini açın
2. İlk girişte bir admin hesabı oluşturun
3. **Settings → Import** menüsünden aşağıdaki dosyaları içe aktarın:
   - `../n8n-workflows/auto-posting-scheduler.json`
   - `../n8n-workflows/telegram-content-approval.json`
4. Her workflow'u açıp webhook URL'lerini local adresinize göre güncelleyin
5. Workflow'ları aktifleştirin

---

## Güncelleme

```bash
# Yeni image'ları çek
docker compose pull

# Servisleri yeniden başlat
docker compose up -d

# Yeni migration varsa çalıştır
bash migrations/run-migrations.sh
```

---

## Durdurma ve Yedekleme

```bash
# Servisleri durdur (veriler korunur)
docker compose down

# Servisleri durdur ve tüm verileri sil (DİKKAT!)
docker compose down -v

# PostgreSQL yedeği al
docker compose exec postgres pg_dump -U otomaix otomaix > yedek_$(date +%Y%m%d).sql
```

---

## Sorun Giderme

### Backend başlamıyor

```bash
docker compose logs backend
```

Sık karşılaşılan nedenler:
- `DATABASE_URL` yanlış → `.env` dosyasındaki `POSTGRES_PASSWORD` kontrol edin
- Migration eksik → `bash migrations/run-migrations.sh` tekrar çalıştırın

### Görsel üretimi çalışmıyor

- `FAL_KEY` değerinin doğru girildiğini kontrol edin
- fal.ai hesabınızda kredi olduğundan emin olun

### n8n webhook'ları çalışmıyor

- `N8N_WEBHOOK_URL` değerini sunucunuzun dışarıdan erişilebilir adresine ayarlayın
- Örnek: `N8N_WEBHOOK_URL=https://n8n.sizin-domain.com`

### PostgreSQL'e bağlanamıyorum

```bash
# Container içinden test
docker compose exec postgres psql -U otomaix -d otomaix -c "SELECT version();"
```

---

## Üretim Ortamı İçin Ek Öneriler

- Reverse proxy olarak **Nginx** veya **Traefik** kullanın
- SSL sertifikası için **Let's Encrypt** + Certbot kurun
- `.env` dosyasını asla Git'e commit etmeyin
- `POSTGRES_PASSWORD`, `INTERNAL_API_KEY`, `N8N_ENCRYPTION_KEY` için güçlü rastgele değerler kullanın:
  ```bash
  openssl rand -hex 32
  ```
- Düzenli PostgreSQL yedekleri için bir cron job kurun
