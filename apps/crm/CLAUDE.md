# CRM Admin Paneli — CLAUDE.md

## Proje Amacı
Otomaix ekibinin müşterileri yönettiği dahili admin paneli.
crm.otomaix.com'da çalışır. Dışarıya açık değil, şifre korumalı.

## Proje Kılavuzları
Genel mimari: ~/otomaix/docs/00-platform-mimari.md
CRM Kılavuzu: ~/otomaix/docs/05-crm-admin.md

## VPS Bilgileri
- IP: 178.104.7.200
- Deploy: Coolify (servis adı: otomaix-crm)
- URL: https://crm.otomaix.com

## Bağımlılıklar
- PostgreSQL: 127.0.0.1:5433, schema: crm (yazma) + social (okuma)
- Social backend API: https://api.otomaix.com
- n8n: https://n8n.otomaix.com (bildirim workflow'ları)

## Gerekli .env Değişkenleri
```
DATABASE_URL=postgresql://otomaix:PASSWORD@127.0.0.1:5433/otomaix
CRM_PASSWORD=Otomaix541851!
TELEGRAM_BOT_TOKEN=         (opsiyonel, Adım 7)
TELEGRAM_CHAT_ID=           (opsiyonel, Adım 7)
NEXT_PUBLIC_API_URL=https://api.otomaix.com
```

## Auth Sistemi
- Basit şifre koruması — Supabase yok
- Login: `app/actions.ts` → `login()` server action → `crm-auth` cookie set
- Cookie değeri: sha256(CRM_PASSWORD + 'otomaix-crm-salt-2026') — httpOnly, secure
- `middleware.ts` → cookie doğrular, yoksa /login'e yönlendirir
- Web Crypto API kullanılıyor (Edge runtime uyumlu — Node crypto değil)
- Logout: `app/actions.ts` → `logout()` → cookie siler → /login

## Veritabanı Bağlantısı
- `lib/db.ts` → pg Pool singleton (max 10 bağlantı)
- Tüm sayfalar Server Component → direkt DB sorgusu (API katmanı yok)
- `export const dynamic = 'force-dynamic'` — DB'li tüm sayfalarda (build zamanı prerender engellenir)
- CRM tabloları: `crm.account_notes`, `crm.account_tags`, `crm.account_communications`, `crm.monthly_usage`
- View: `crm.customer_overview` (social.accounts + social.subscriptions + crm tabloları birleşik)

## Klasör Yapısı
```
apps/crm/
├── app/
│   ├── actions.ts                     # login() + logout() server actions
│   ├── customer-actions.ts            # addNote, addCommunication, addTag, removeTag, changePlan
│   ├── layout.tsx                     # root layout (Inter font, noindex)
│   ├── globals.css                    # Tailwind + dense table stiller
│   ├── (auth)/
│   │   └── login/page.tsx             # Şifre korumalı giriş (useFormState)
│   └── (dashboard)/
│       ├── layout.tsx                 # Sidebar + main wrapper
│       ├── page.tsx                   # Genel Bakış
│       ├── musteriler/
│       │   ├── page.tsx               # Müşteri listesi (filtreli, sayfalı)
│       │   └── [id]/page.tsx          # Müşteri detay
│       ├── operasyon/page.tsx         # Sorun takibi
│       ├── raporlar/page.tsx          # Aylık raporlar
│       └── bildirimler/page.tsx       # n8n yönlendirme
├── components/
│   ├── layout/Sidebar.tsx             # 200px, #1a1a2e, nav + logout
│   ├── charts/
│   │   ├── PlanDistributionChart.tsx  # recharts Donut (client)
│   │   └── ContentBarChart.tsx        # recharts Bar (client)
│   ├── customers/
│   │   ├── CustomerFilters.tsx        # useRouter filter push (client)
│   │   ├── CustomerActions.tsx        # Plan değiştir, Paddle link (client)
│   │   ├── TagManager.tsx             # Etiket ekle/kaldır (client)
│   │   ├── AddNoteForm.tsx            # İç not (client)
│   │   └── AddCommunicationForm.tsx   # İletişim kaydı (client)
│   ├── operations/
│   │   └── MarkChurnRisk.tsx          # Tek tıkla Churn Riski etiketi (client)
│   └── reports/
│       └── MonthSelector.tsx          # Ay seçici (client, useRouter)
├── lib/
│   ├── db.ts                          # pg Pool singleton + query/queryOne helpers
│   └── utils.ts                       # cn, relativeTime, formatDate, formatCurrency, PLAN_*, STATUS_*
├── middleware.ts                      # Cookie auth kontrolü (Edge runtime, Web Crypto)
├── next.config.mjs                    # standalone output, pg external package
├── Dockerfile                         # multi-stage, node:20-alpine
└── .env.example
```

## Migrations
- `shared/db/migrations/012_crm_tables.sql` — crm schema + 4 tablo + customer_overview view ✅

## Tamamlanan Adımlar

### Adım 1 — CRM Projesi Kurulumu ✅
- 012_crm_tables.sql migration oluşturuldu
- Next.js 14 projesi kuruldu (bare Tailwind, yoğun tablo UI, animasyon yok)
- Cookie-based auth (login/logout server actions + middleware)
- Sidebar (200px, koyu #1a1a2e)
- Dockerfile + .dockerignore + .env.example
- `lib/db.ts` + `lib/utils.ts`

### Adım 2 — Genel Bakış Dashboard'u ✅
- `app/(dashboard)/page.tsx` — `force-dynamic`
  - 4 metrik kartı: Aktif Müşteri, Bu Ay Yeni, MRR (₺), Churn Bu Ay
  - Plan Dağılımı donut chart + Son 30 Gün içerik bar chart (recharts)
  - Son Kayıt Olanlar tablosu (son 10)
  - Churn Riski tablosu (14+ gün giriş yok, aktif üye, etiketsiz)
  - Ödeme Sorunları tablosu (past_due)
  - Her tablo satırı → müşteri detay sayfasına link

### Adım 3 — Müşteri Listesi ✅
- `app/(dashboard)/musteriler/page.tsx` — `force-dynamic`
  - `crm.customer_overview` view'dan sorgu
  - Filtreler: Plan / Durum / Etiket / Son Giriş (useRouter ile anlık)
  - Metin araması: ad + email ILIKE
  - 25/sayfa, sunucu taraflı sayfalama
  - CSV export butonu (link hazır, API route Adım 3+ için bekliyor)
- `components/customers/CustomerFilters.tsx` — client component

### Adım 4 — Müşteri Detay Sayfası ✅
- `app/(dashboard)/musteriler/[id]/page.tsx` — `force-dynamic`
  - Sol: müşteri bilgileri, markalar listesi, aylık kullanım (son 3 ay), iletişim geçmişi
  - Sağ: Hızlı Aksiyonlar (plan değiştir, Paddle link, şifre sıfırlama), Etiketler
- `app/customer-actions.ts` — addNote, addCommunication, addTag, removeTag, changePlan
- `components/customers/AddNoteForm.tsx`
- `components/customers/AddCommunicationForm.tsx`
- `components/customers/TagManager.tsx`
- `components/customers/CustomerActions.tsx`

### Adım 5 — Operasyon Sayfası ✅
- `app/(dashboard)/operasyon/page.tsx` — `force-dynamic`
  - Yayın Hataları: social.posts status=failed, son 7 gün
  - Ödeme Sorunları: subscriptions status=past_due
  - fal.ai Üretim Hataları: failed + fal_job_id var, son 24 saat
  - Churn Riski Adayları: 14+ gün giriş yok, aktif, etiketsiz
- `components/operations/MarkChurnRisk.tsx` — tek tıkla Churn Riski etiketi ekler

### Adım 6 — Raporlar Sayfası ✅
- `app/(dashboard)/raporlar/page.tsx` — `force-dynamic`
  - Ay seçici (son 12 ay, MonthSelector client component)
  - Büyüme Metrikleri: yeni müşteri, churn, MRR, ARPU, MoM büyüme %
  - Ürün Kullanımı: içerik tipi breakdown + platform breakdown
  - Plan Dağılımı (anlık)
  - Top 10 en aktif müşteriler (bu ay)
- `components/reports/MonthSelector.tsx` — client component

### Adım 7 — n8n CRM Otomasyonları ✅
- `shared/n8n-workflows/crm-automations.json` — 6 workflow JSON (n8n'e import edilecek)
  - CRM-1: Yeni Müşteri Bildirimi (webhook: `crm/new-customer`)
  - CRM-2: Plan Yükseltme Bildirimi (webhook: `crm/plan-upgrade`)
  - CRM-3: Ödeme Başarısız + 2 gün sonra hatırlatma (webhook: `crm/payment-failed`)
  - CRM-4: Churn Riski Taraması — her gün 09:00, 14+ gün giriş yok → etiket ekle + Telegram
  - CRM-5: Deneme Süresi Bitiyor — her gün 10:00, 2 gün kalan trial'lar → Telegram
  - CRM-6: Aylık Gelir Raporu — her ayın 1'i 09:00, MRR + büyüme → Telegram
- `social/backend/app/routers/billing.py` güncellendi:
  - `_notify_crm_n8n()` helper — fire-and-forget n8n webhook çağrısı
  - `PLAN_ORDER` dict — plan yükseltme tespiti için (starter < pro < business < agency)
  - `subscription.created` → `crm/new-customer` webhook
  - `subscription.updated` (plan yükseltme) → `crm/plan-upgrade` webhook
  - `subscription.payment_failed` / `transaction.payment_failed` → DB'de past_due + `crm/payment-failed` webhook
- `social/backend/app/core/config.py` güncellendi: `N8N_BASE_URL` eklendi
- **Manuel yapılacak:** n8n'de "PostgreSQL Otomaix" credential oluştur, sonra 6 workflow'u import et

### Adım 8 — Coolify Deploy
- [ ] Henüz yapılmadı
- Coolify'da `otomaix-crm` servisi oluşturulacak
- Domain: crm.otomaix.com
- .env değişkenleri Coolify'a eklenecek

## Bir Sonraki Adım
**Adım 8: Coolify Deploy**
- Coolify'da `otomaix-crm` servisi oluştur (GitHub repo, apps/crm klasörü)
- Domain: crm.otomaix.com
- .env değişkenlerini Coolify'a ekle (DATABASE_URL, CRM_PASSWORD, vb.)
- n8n'de PostgreSQL Otomaix credential oluştur
- crm-automations.json'u n8n'e import et (6 workflow)

## Önemli Kararlar ve Teknik Notlar
- CRM direkt PostgreSQL'e bağlanır — API katmanı yok (sosyal backend bypass)
- `crm.customer_overview` view tüm müşteri verilerini birleştirir
- No Supabase, no Zustand, no complex state — basitlik öncelikli
- Tüm sayfalar Server Component + küçük Client Component'lar (sadece interaktif kısımlar)
- `export const dynamic = 'force-dynamic'` — build zamanı prerender engeli (DB yokken hata verirdi)
- `useFormState` from `react-dom` kullanıldı (React 18 uyumlu — `useActionState` React 19'da)
- recharts Tooltip `formatter` tipi: `(value, name)` — `ValueType | undefined` olabilir, null check gerekli
- `pg` paketi Next.js 14'te `experimental.serverComponentsExternalPackages` ile bildirilmeli
