# 00 — Otomaix Platform Mimarisi
> Bu dosyayı bir kez oku. Yeni bir uygulama başlatmadan önce buraya bak.
> Tüm uygulamalara ortak kararlar burada yazılıdır.

---

## Otomaix Nedir?

Otomaix, Türk KOBİ ve orta ölçekli şirketlere yönelik AI otomasyon uygulamaları sunan bir platformdur.
Her uygulama bağımsız bir servis olarak çalışır, ancak ortak altyapıyı (veritabanı, workflow engine, auth) paylaşır.

**Mevcut uygulamalar:**
- `social` → AI Sosyal Medya Otomasyonu *(aktif geliştirme)*
- `crm` → Admin & Müşteri Yönetimi Paneli *(aktif geliştirme)*
- *(gelecekteki uygulamalar buraya eklenecek)*

---

## VPS Bilgileri

| Bilgi | Değer |
|---|---|
| Sunucu | Hetzner VPS |
| IP | 178.104.7.200 |
| OS | Ubuntu 24 |
| Yönetim | Coolify |
| n8n | https://n8n.otomaix.com |

---

## Klasör Yapısı — VPS Üzerinde

```
/home/eray/
└── otomaix/
    ├── apps/
    │   ├── social/          # AI Sosyal Medya uygulaması
    │   │   ├── frontend/    # Next.js (app.otomaix.com)
    │   │   └── backend/     # FastAPI (api.otomaix.com)
    │   ├── crm/             # CRM Admin paneli (crm.otomaix.com)
    │   └── [yeni-uygulama]/ # Gelecekteki uygulamalar aynı pattern'i izler
    ├── shared/
    │   ├── db/              # PostgreSQL migration dosyaları (tüm uygulamalar)
    │   └── n8n-workflows/   # n8n workflow JSON'ları (export/versiyon)
    └── docs/                # Bu MD dosyaları buraya kopyalanır
```

**Kural:** Her yeni uygulama `apps/` altına kendi klasörüyle girer.
Ortak altyapı (PostgreSQL, Redis, n8n) `shared/` altında yönetilir.

---

## Subdomain Haritası

| Subdomain | Uygulama | Açıklama |
|---|---|---|
| `app.otomaix.com` | social/frontend | Kullanıcı arayüzü |
| `api.otomaix.com` | social/backend | REST API |
| `assets.otomaix.com` | Cloudflare R2 | Medya CDN |
| `crm.otomaix.com` | crm | Admin paneli |
| `n8n.otomaix.com` | n8n | Workflow engine |

---

## Ortak Altyapı — Tüm Uygulamalar Bunları Paylaşır

```
PostgreSQL  → Tek veritabanı, her uygulama kendi schema'sını kullanır
Redis       → Session, rate limiting, job queue
n8n         → Workflow engine (tüm uygulamaların otomasyon katmanı)
Coolify     → Tüm servislerin deploy ve yönetimi
Cloudflare  → CDN, WAF, R2 storage
```

---

## Coolify Servis İsimlendirme Standardı

Her Coolify servisi şu formatı izler: `otomaix-[uygulama]-[katman]`

```
otomaix-social-frontend    → app.otomaix.com
otomaix-social-backend     → api.otomaix.com
otomaix-crm                → crm.otomaix.com
otomaix-n8n                → n8n.otomaix.com
otomaix-postgres           → internal (dışa açık değil)
otomaix-redis              → internal (dışa açık değil)
```

---

## Teknoloji Stack — Genel Karar Tablosu

| Katman | Teknoloji | Neden? |
|---|---|---|
| Frontend framework | Next.js 14 (App Router) | SSR + SEO + API routes |
| UI kütüphanesi | shadcn/ui + Tailwind CSS | Radix tabanlı, erişilebilir |
| State management | Zustand | Az boilerplate |
| Backend API | FastAPI (Python) | Async, otomatik Swagger |
| Workflow engine | n8n (self-hosted) | Görsel workflow, Türk KOBİ otomasyonu |
| Ana veritabanı | PostgreSQL | İlişkisel, pgvector desteği |
| Cache / Queue | Redis | Session, job queue |
| Auth | Supabase Auth | Google OAuth + JWT hazır |
| Medya depolama | Cloudflare R2 | Egress ücreti sıfır |
| AI medya üretimi | fal.ai | 600+ model, webhook callback |
| Sosyal medya yayını | Upload-Post.com | Agency JWT onboarding |
| AI medya üretimi (caption) | Anthropic Claude | Opus 4.6 caption, Haiku analiz/vision |
| Video TTS | Azure TTS | Opsiyonel, Faceless video ses |
| Instagram scraping | Apify | Opsiyonel, rakip analizi |
| Ödeme | Paddle | Türkiye vergi/fatura yönetimi |
| Analytics | PostHog (self-host) | GDPR uyumlu |
| Error monitoring | Sentry | Standart |
| Canlı destek | Crisp Chat | Free plan yeterli |
| Tarih işleme | date-fns + date-fns-tz | Timezone dönüşümü |

---

## PostgreSQL — Veritabanı Organizasyonu

Her uygulama kendi şemasını kullanır, aynı PostgreSQL instance'ında:

```sql
-- Social uygulaması
schema: social

-- CRM
schema: crm

-- Platform geneli (ortak tablolar)
schema: platform
```

**Önemli kural:** Uygulamalar birbirinin şemasına doğrudan bağlanmaz.
Gerekirse FastAPI üzerinden API çağrısı yapılır.

---

## CLAUDE.md Şablonu — Her Projeye Eklenir

Her yeni uygulama/servis klasörüne `CLAUDE.md` dosyası oluşturulur.
Bu dosya Claude Code'un session başında okuduğu "hafıza" dosyasıdır.

```markdown
# [Servis Adı] — CLAUDE.md

> **DRIFT KORUMA**
> Bu dosya YALNIZCA: proje yapısı, env, deploy, konvansiyonlar.
> Sprint logları → git commit.
> Kararlar → memory/decisions_*.md.
> Aktif iş → Tasks (oturum içi).
> Bu dosyaya changelog EKLENMEZ.

## Proje Amacı
[Kısa açıklama]

## Deploy
- Coolify servis adı: otomaix-[uygulama]-[katman]
- URL: https://[subdomain].otomaix.com

## Bağımlılıklar
- PostgreSQL: schema: [schema_adı]
- [diğer servisler]

## .env Değişkenleri
[Gerekli env var listesi]

## Klasör Yapısı
[Dizin ağacı]

## Konvansiyonlar
[Bu projeye özel kurallar]
```

---

## Kesin Kurallar

- `social/frontend` session'ında `social/backend` kodu yazma
- Her servis kendi CLAUDE.md'sine sahip olmalı
- n8n workflow'ları her zaman `shared/n8n-workflows/` klasörüne JSON olarak export edilir

---

## Yeni Uygulama Başlatırken Kontrol Listesi

Otomaix'e yeni bir uygulama eklendiğinde:

- [ ] `apps/[yeni-uygulama]/` klasörü oluşturuldu
- [ ] Bu dosyada (`00-platform-mimari.md`) uygulama listeye eklendi
- [ ] Subdomain haritasına eklendi
- [ ] Coolify'da servis ismi tanımlandı
- [ ] PostgreSQL'de yeni schema oluşturuldu
- [ ] CLAUDE.md şablonu uygulandı
- [ ] Yeni uygulama için kılavuz MD dosyası oluşturuldu

---

*Son güncelleme: Nisan 2026*
*Bir sonraki dosya: `01-social-phase1.md`*
