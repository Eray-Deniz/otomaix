# 05 — CRM Admin Paneli
> **Süre:** Phase 2 sonrasında paralel geliştirilebilir (Ay 3+)  
> **Ön koşul:** `01-social-phase1.md` tamamlanmış olmalı (PostgreSQL şeması var)  
> **URL:** crm.otomaix.com — sadece Otomaix ekibi erişir  
> **Not:** CRM tüm Otomaix uygulamalarına hizmet eder, sadece Social'a değil

---

## CRM Nedir, Ne Değildir?

**CRM:** Otomaix **ekibinin** müşterileri yönettiği dahili admin paneli.  
**Müşteri dashboard'u değil:** Müşteri kendi verilerini `app.otomaix.com`'da görür.

CRM şunları kapsar:
- Tüm müşterilerin listesi, plan ve ödeme durumu
- Müşteri bazlı kullanım metrikleri
- Churn riski uyarıları
- Operasyonel sorunların takibi (başarısız yayınlar, ödeme hataları)
- İletişim geçmişi ve iç notlar
- Genel iş metrikleri (MRR, churn rate, plan dağılımı)

---

## Klasör Yapısı

```
/home/eray/otomaix/
└── apps/
    └── crm/
        ├── CLAUDE.md
        ├── app/
        │   ├── (auth)/
        │   │   └── login/
        │   │       └── page.tsx   # Şifre korumalı giriş
        │   ├── (dashboard)/
        │   │   ├── layout.tsx
        │   │   ├── page.tsx       # Genel metrikler
        │   │   ├── musteriler/
        │   │   │   ├── page.tsx   # Müşteri listesi
        │   │   │   └── [id]/
        │   │   │       └── page.tsx  # Müşteri detay
        │   │   ├── operasyon/
        │   │   │   └── page.tsx   # Sorun takibi
        │   │   └── raporlar/
        │   │       └── page.tsx   # Aylık raporlar
        │   └── layout.tsx
        ├── lib/
        └── components/
```

---

## Adım 1: CRM Projesi Kurulumu

**Claude Code session:** `~/otomaix/apps/crm/` dizininde başlat.

### 1a. CLAUDE.md oluştur

**Claude Code'a ver:**
```
Create CLAUDE.md in the current directory:

# CRM Admin Paneli — CLAUDE.md

## Proje Amacı
Otomaix ekibinin müşterileri yönettiği dahili admin paneli.
crm.otomaix.com'da çalışır. Dışarıya açık değil, şifre korumalı.

## VPS Bilgileri
- IP: 178.104.7.200
- Deploy: Coolify (servis adı: otomaix-crm)
- URL: https://crm.otomaix.com

## Bağımlılıklar
- PostgreSQL: internal, schema: social (okuma) + crm (yazma)
- Social backend API: https://api.otomaix.com (bazı veriler için)
- Paddle webhooks: plan/ödeme verileri için

## Gerekli .env.local Değişkenleri
NEXT_PUBLIC_API_URL=https://api.otomaix.com
DATABASE_URL= (direkt PostgreSQL bağlantısı)
CRM_PASSWORD= (basit şifre koruması için)
TELEGRAM_BOT_TOKEN= (bildirimler için)

## Tamamlanan İşler
- [ ] Proje kurulumu

## Devam Eden İş
- Proje kurulumu başlıyor

## Önemli Kararlar
- CRM direkt PostgreSQL'e bağlanır (API katmanı bypass)
- Basit session-based auth (Supabase değil, çok basit tutulacak)
- Ek maliyet yok: aynı VPS, aynı PostgreSQL
```

### 1b. PostgreSQL — CRM ek tabloları

**Claude Code'a ver (CRM session'ında ya da shared/db session'ında):**
```
Create migration file: ~/otomaix/shared/db/migrations/005_crm_tables.sql

Create schema and tables:

CREATE SCHEMA IF NOT EXISTS crm;

CREATE TABLE crm.account_notes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID NOT NULL,  -- references social.accounts
  note TEXT NOT NULL,
  created_by TEXT NOT NULL,  -- Otomaix ekip üyesinin adı
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE crm.account_tags (
  account_id UUID NOT NULL,
  tag TEXT NOT NULL,  -- VIP / Churn Riski / Pilot / Agency / Sorunlu
  added_by TEXT NOT NULL,
  added_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (account_id, tag)
);

CREATE TABLE crm.account_communications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID NOT NULL,
  channel TEXT NOT NULL,  -- email/telefon/toplanti/telegram
  direction TEXT NOT NULL,  -- inbound/outbound
  subject TEXT,
  note TEXT,
  created_by TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE crm.monthly_usage (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID NOT NULL,
  brand_id UUID,
  year_month TEXT NOT NULL,  -- '2026-04'
  posts_generated INTEGER DEFAULT 0,
  posts_published INTEGER DEFAULT 0,
  credits_used INTEGER DEFAULT 0,
  storage_used_mb INTEGER DEFAULT 0,
  fal_cost_usd DECIMAL(10,4) DEFAULT 0,
  UNIQUE(account_id, brand_id, year_month)
);

-- View for easy customer overview (combines social + crm schemas)
CREATE OR REPLACE VIEW crm.customer_overview AS
SELECT 
  a.id,
  a.email,
  a.name,
  a.plan_id,
  a.created_at,
  a.last_login_at,
  COUNT(DISTINCT b.id) as brand_count,
  ARRAY_AGG(DISTINCT t.tag) FILTER (WHERE t.tag IS NOT NULL) as tags,
  SUM(mu.posts_generated) as total_posts_generated,
  SUM(mu.posts_published) as total_posts_published,
  MAX(mu.year_month) as last_active_month
FROM social.accounts a
LEFT JOIN social.workspaces w ON w.account_id = a.id
LEFT JOIN social.brands b ON b.workspace_id = w.id
LEFT JOIN crm.account_tags t ON t.account_id = a.id
LEFT JOIN crm.monthly_usage mu ON mu.account_id = a.id
GROUP BY a.id, a.email, a.name, a.plan_id, a.created_at, a.last_login_at;
```

### 1c. CRM Next.js Projesi

**Claude Code'a ver:**
```
Create a Next.js 14 project for the CRM admin panel.

Same tech stack as Social frontend (shadcn/ui + Tailwind).

Simple authentication:
- Login page: single password field (stored in env as CRM_PASSWORD)
- No Supabase — just a simple server action that sets a cookie
- Middleware: check cookie on all /dashboard routes

CRM-specific design:
- Sidebar: narrower (200px), dark background (#1a1a2e)
- Dense data tables (more information density than user-facing app)
- Turkish language throughout
- No animations (speed over aesthetics)

Navigation items:
- 📊 Genel Bakış
- 👥 Müşteriler
- ⚠️ Operasyon
- 📈 Raporlar
- 🔔 Bildirimler
```

---

## Adım 2: Genel Bakış Dashboard'u

**Ne yapılıyor:** İş metriklerinin tek bakışta görüldüğü ana sayfa.

**Claude Code'a ver:**
```
Create the main dashboard at app/(dashboard)/page.tsx

Connect directly to PostgreSQL using a server component (not API).

Display these metric cards (top row):
- Toplam Aktif Müşteri: COUNT from social.accounts where has active subscription
- Bu Ay Yeni Müşteri: new accounts this month + MoM growth %
- MRR (₺): sum of active subscription amounts (from subscriptions table)
- Churn Bu Ay: accounts cancelled this month

Second row (charts using recharts):
- Plan Dağılımı: Donut chart (Starter/Pro/Business/Agency counts)
- MRR Trendi: Line chart last 6 months
- Üretilen İçerik: Bar chart last 30 days (posts_generated per day)

Third row (tables):
- Son Kayıt Olanlar: last 10 new accounts (name, email, plan, registered_at)
- Churn Riski: accounts with tag='Churn Riski' or 14+ days no login
- Ödeme Sorunları: accounts with past_due subscription status

Each row item in the tables should be clickable → goes to customer detail page.

Auto-refresh every 60 seconds (use Next.js revalidate or client polling).
```

---

## Adım 3: Müşteri Listesi

**Ne yapılıyor:** Tüm müşterilerin listelendiği, filtrelendiği ve arandığı sayfa.

**Claude Code'a ver:**
```
Create customer list page at app/(dashboard)/musteriler/page.tsx

Data source: SELECT from crm.customer_overview view

Table columns:
- Ad / Email
- Plan (colored badge: Starter=gray, Pro=blue, Business=purple, Agency=gold)
- Marka Sayısı
- Bu Ay İçerik
- Son Giriş (relative: "2 gün önce", colored red if >14 days)
- Etiketler (VIP/Churn Riski/etc as small badges)
- Durum (Active/Trial/Past Due/Cancelled)
- İşlemler (Görüntüle button)

Filters (filter bar above table):
- Plan filter: Tümü / Starter / Pro / Business / Agency
- Durum: Tümü / Aktif / Deneme / Ödeme Sorunu / İptal
- Etiket: Tümü / VIP / Churn Riski / Pilot / Sorunlu
- Son giriş: Tümü / Son 7 gün / 7-30 gün / 30+ gün (churn risk)

Search: real-time search by name or email

Pagination: 25 per page, server-side

Export button: "CSV İndir" → export all filtered results
```

---

## Adım 4: Müşteri Detay Sayfası

**Ne yapılıyor:** Tek müşteriye dair tüm bilgilerin görüldüğü detay sayfası.

**Claude Code'a ver:**
```
Create customer detail page at app/(dashboard)/musteriler/[id]/page.tsx

Layout: 2 columns (left 2/3, right 1/3)

LEFT COLUMN:

Section 1: Müşteri Bilgileri
- Name, email, phone (if available)
- Plan + status + renewal date
- Registered date, last login
- Stripe/Paddle customer link

Section 2: Kullanım İstatistikleri (last 3 months)
- Monthly bar chart: posts generated vs published
- Platform breakdown table: Instagram: X posts, TikTok: Y posts...
- fal.ai cost per month (USD)
- R2 storage used (MB)

Section 3: Markalar
- List of brands with: name, connected platforms, posts this month
- Each brand: "Detay" link

Section 4: İletişim Geçmişi
- Chronological list of notes and communications
- Add new communication form:
  Channel: Email/Telefon/Toplantı/Telegram
  Direction: Gelen/Giden
  Subject + Note textareas
  "Kaydet" button

RIGHT COLUMN:

Section 1: Hızlı Aksiyonlar
- "Plan Değiştir" → select new plan + confirm
- "Kredi Ekle" → add bonus credits
- "Şifre Sıfırlama Gönder" → trigger Supabase password reset
- "Hesabı Askıya Al" → disable account (with confirmation)

Section 2: Etiketler
- Current tags shown as removable chips
- Add tag dropdown: VIP / Churn Riski / Pilot / Agency / Sorunlu / VIP
- Tags are added/removed instantly (PostgreSQL update)

Section 3: İç Notlar
- List of notes with author + date
- "Not Ekle" form → textarea + "Kaydet"
- Notes are private (only visible in CRM)
```

---

## Adım 5: Operasyon Sayfası

**Ne yapılıyor:** Sorunların gerçek zamanlı takip edildiği sayfa.

**Claude Code'a ver:**
```
Create operations page at app/(dashboard)/operasyon/page.tsx

This page shows active issues that need attention.

Section 1: Yayın Hataları (Publishing Failures)
- Query: SELECT from social.posts where status='failed' and created_at > now()-'7 days'
- Table: Brand name, platform, error time, "Yeniden Dene" button
- Group by: error type (auth_error / rate_limit / media_error)

Section 2: Ödeme Sorunları
- Accounts with subscription status = 'past_due'
- Days since payment failed
- "Müşteriye Ulaş" quick action button

Section 3: fal.ai Üretim Hataları
- Failed content generation jobs from last 24 hours
- Error message, brand name, content type
- "Yeniden Üret" button → calls POST /posts/{id}/regenerate

Section 4: Churn Riski Erken Uyarı
- Accounts with 14+ days no login (not already tagged as Churn Risk)
- "Churn Riski Etiketi Ekle" button
- "İletişime Geç" button → opens communication form

Section 5: Depolama Uyarıları
- Accounts at 80%+ storage limit
- Storage used / limit visualization
- "Upgrade Emaili Gönder" button

Auto-refresh every 5 minutes. Show badge on sidebar nav with issue count.
```

---

## Adım 6: Raporlar Sayfası

**Claude Code'a ver:**
```
Create reports page at app/(dashboard)/raporlar/page.tsx

Monthly Business Report:
- Month selector (default: current month)
- Generate report button → runs queries

Report sections:
1. Büyüme Metrikleri
   - New customers: N (vs last month: +X%)
   - Churned: N (churn rate: X%)
   - Net new: N
   - MRR: ₺X (vs last month)
   - ARPU (Average Revenue Per User): ₺X

2. Ürün Kullanımı
   - Total posts generated: N
   - Total posts published: N
   - Publish rate: X%
   - Most used content type: Image/Video/Carousel
   - Most used platform: Instagram/TikTok/etc

3. Maliyet Analizi
   - fal.ai total cost: $X
   - R2 storage cost: $X
   - Total infrastructure cost: $X (Hetzner + R2 + other)
   - Revenue: ₺X
   - Margin: X%

4. En Aktif Müşteriler
   - Top 10 by posts generated
   - Top 10 by storage used

"PDF İndir" button → generates a simple PDF report
"CSV İndir" → raw data export
```

---

## Adım 7: n8n CRM Otomasyonları

**Ne yapılıyor:** Manuel müşteri takibi yerine n8n otomatik bildirimler gönderiyor.

**Claude Code'a ver:**
```
Create n8n workflow "CRM Otomasyonları" using n8n MCP.

This is a collection of automated CRM alerts sent to Telegram.

Sub-workflow 1: Yeni Müşteri Bildirimi
Trigger: Webhook POST /webhook/new-customer
Message: "🎉 Yeni müşteri! {name} ({email}) - Plan: {plan}"

Sub-workflow 2: Plan Yükseltme Bildirimi  
Trigger: Paddle webhook - subscription.updated (plan change up)
Message: "⬆️ Plan yükseltme! {name}: {old_plan} → {new_plan} (+₺{revenue_diff}/ay)"

Sub-workflow 3: Ödeme Başarısız
Trigger: Paddle webhook - subscription.payment_failed
Steps:
1. Add 'Ödeme Sorunu' tag to account in PostgreSQL
2. Telegram: "⚠️ Ödeme başarısız: {name} ({email}) - Plan: {plan}"
3. Wait 2 days
4. If still unpaid: send reminder email to customer

Sub-workflow 4: Churn Riski Taraması
Trigger: Schedule - every day at 09:00
Steps:
1. Query: accounts with last_login_at < now() - interval '14 days'
2. For each: add 'Churn Riski' tag if not already tagged
3. Send Telegram summary: "⚠️ Churn riski: {count} müşteri 14+ gündür giriş yapmadı"
4. List the accounts in message

Sub-workflow 5: Deneme Süresi Bitiyor
Trigger: Schedule - every day at 10:00
Steps:
1. Query: trial accounts where trial_ends_at = today + 2 days
2. For each: send upgrade reminder email
3. Telegram: "📅 {count} deneme hesabı 2 gün içinde bitiyor"

Sub-workflow 6: Aylık Gelir Raporu
Trigger: Schedule - 1st of each month at 09:00
Steps:
1. Calculate MRR, new customers, churn
2. Send Telegram summary with key metrics
3. Post to a dedicated Telegram channel (if exists)

Export all to ~/otomaix/shared/n8n-workflows/crm-automations.json
```

---

## Adım 8: Coolify Deploy

**Claude Code'a ver (CRM session'ında):**
```
Create Dockerfile for CRM Next.js app (same pattern as social frontend).
Create .dockerignore file.

The CRM should have an additional security layer:
- Add HTTP Basic Auth at Nginx/Traefik level (Coolify config)
- Or implement simple middleware password check
- Do NOT expose to public without authentication

In Coolify:
- Service name: otomaix-crm
- Domain: crm.otomaix.com
- Add basic auth or IP restriction (only office/VPN IPs)
```

---

## CRM Aşamalı Geliştirme

CRM'i aşamalı olarak hayata geçirebilirsin:

| Aşama | Müşteri Sayısı | Yaklaşım |
|---|---|---|
| **Aşama 1** (0-50 müşteri) | PostHog + HubSpot Free + n8n otomasyonları | Sıfır geliştirme süresi |
| **Aşama 2** (50-200 müşteri) | Bu kılavuzdaki tam CRM | Phase 2 social tamamlandıktan sonra |
| **Aşama 3** (200+ müşteri) | CRM'e segmentasyon + kampanya + churn tahmin | Gerektiğinde ekle |

---

## CRM Tamamlanma Kontrol Listesi

- [ ] CRM Next.js projesi Coolify'da deploy edildi
- [ ] Login sayfası çalışıyor (şifre korumalı)
- [ ] Genel bakış dashboard'u metrikleri doğru gösteriyor
- [ ] Müşteri listesi filtreleme ve arama çalışıyor
- [ ] Müşteri detay sayfası iç not ekleme çalışıyor
- [ ] Etiket sistemi çalışıyor (VIP, Churn Riski vb.)
- [ ] Operasyon sayfası yayın hatalarını gösteriyor
- [ ] Raporlar sayfası aylık metrik üretiyor
- [ ] n8n CRM otomasyonları Telegram'a bildirim gönderiyor
- [ ] Yeni müşteri kaydolunca Telegram bildirimi geliyor
- [ ] Churn riski taraması günlük çalışıyor

---

*CRM tamamlandıktan sonra → `00-platform-mimari.md`'yi güncelleyerek yeni Otomaix uygulamaları için hazırlan*
