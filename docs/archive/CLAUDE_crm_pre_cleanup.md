# CRM Admin Paneli — CLAUDE.md

## 2026-04-16 — Phase 6 Sprint 6: Trend maliyet kolonu (raporlar sayfası)

`app/(dashboard)/raporlar/page.tsx` → `social.trend_usage` tablosundan aylık Layer B/C kullanım ve maliyet verileri çekilip yeni "Trend Kullanımı & Maliyet" bölümüne eklendi. 4 MetricCard: Layer B tetik sayısı, Layer C rapor sayısı, Layer B maliyet ($), Layer C maliyet ($) + toplam trend maliyeti satırı.

## 2026-04-14 — N8N-4: CRM-4 Churn Tarama `COUNT(*)` type mismatch fix

Analiz raporundaki P0 bulgusu N8N-4 (CRM Postgres connection / execution hatası) çözüldü.

**Bulunan kök neden:** CRM-4 "Churn Riski Taraması" workflow'u her gün 09:00 UTC'de fail ediyordu. Execution #55 incelendi:
- `Count Churn Risk` node'u: `SELECT COUNT(*) AS count FROM ...` çalıştırıyor. PostgreSQL `COUNT(*)` → BIGINT döndürür; n8n Postgres node'u BIGINT'i JavaScript number precision kaybı riskine karşı **string** olarak serialize eder (`'0'`).
- `Has Churn Risk?` IF node'u: `{{ $json.count }} > 0` kontrolü yapıyor, `typeValidation: strict` + `operator.type: number`. String `'0'`'ı reddediyor → "Wrong type: '0' is a string but was expecting a number".
- Sonuç: Workflow asla "Send Churn Alert" branch'ına ulaşamıyor, ekip uyarısı gitmiyor.

**Fix:** SQL'de `COUNT(*)::int AS count` — int4 küçük sayılar için n8n tarafında native number olarak serialize edilir. Analiz raporu bunu "Postgres connection" olarak isimlendirmişti ama gerçek sebep type serialization idi. CRM-5 "Get Expiring Trials" execution'ı dünkü gerçek "Connection refused" network glitch'iydi ve bugün kendiliğinden çalıştı (#56 success) — aksiyon gerektirmiyor.

**Değişiklikler:**
- n8n workflow `os5XonE1TtptDPBC` → `Count Churn Risk` node SQL'e `::int` cast eklendi
- Local kopya: `shared/n8n-workflows/crm-automations.json` senkronize edildi (bundle içinde CRM-4 entry)

**Doğrulama:** Direkt DB'de `SELECT COUNT(*)::int, pg_typeof(...)` → `count=0, pg_typeof=integer`. n8n public API manuel execute desteklemediği için canlı doğrulama yarın 09:00 UTC schedule tetiğinde yapılacak.

**Not:** CRM-1/2/3/6 workflow'ları incelendi; benzer bir bug yok (CRM-5 IF'i `$items().length` kullandığı için native number, sorun yok).



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
- n8n'de 6 workflow API ile import edildi ve aktif edildi ✅
- Webhook body path: `$json.body.*` (n8n webhook node v2 body'yi $json.body altında döndürür)
- Telegram Bot Token: `8604791076:AAGxu_XtypVCcr7fX1HxDlbIceRXbP_8JPY`
- Telegram Chat ID: `1634464595`
- n8n API Key: `apps/social/backend/.env` → `N8N_API_KEY`
- n8n PostgreSQL credential ID: `LRCmorU07F9lRpjV` (ad: "Postgres account")
- n8n Workflow ID'leri:
  - CRM-1: `UzNjZDghyfJq2vYA`
  - CRM-2: `VoYuC8AGwtT0NpZR`
  - CRM-3: `tDnbM6NNy3a3xHdD`
  - CRM-4: `os5XonE1TtptDPBC`
  - CRM-5: `KOsqeGIkrnKIX6rl`
  - CRM-6: `9esToZdZIeevp0UF`

### Adım 8 — Coolify Deploy ✅
- Coolify'da `otomaix-crm` servisi oluşturuldu
  - GitHub repo: Eray-Deniz/otomaix, Base directory: `apps/crm`
  - Domain: crm.otomaix.com
  - Port: 3000
- Environment Variables Coolify'a eklendi:
  - `DATABASE_URL=postgresql://otomaix:Otomaix541851!@10.0.1.8:5432/otomaix` ← Docker network IP (127.0.0.1 container içinden çalışmaz)
  - `CRM_PASSWORD=Otomaix541851!`
  - `NEXT_PUBLIC_API_URL=https://api.otomaix.com`
- Social backend Coolify'da `N8N_BASE_URL=https://n8n.otomaix.com` eklendi → redeploy edildi
- GoDaddy'de `crm.otomaix.com → 178.104.7.200` A kaydı eklendi
- Dockerfile fix: `public/` klasörü oluşturuldu (COPY hatası giderildi)
- Production DB'ye `012_crm_tables.sql` migration çalıştırıldı (`psql ... -f shared/db/migrations/012_crm_tables.sql`)
- Bug fix: `musteriler/[id]` sayfasında `social.posts LEFT JOIN` eksikti → düzeltildi

## Bir Sonraki Adım
**CRM Adım 1-8 tamamlandı ✅ — crm.otomaix.com canlıda**
Tüm fazlar tamamlandı. Yeni bir geliştirme başlatılacaksa `00-platform-mimari.md`'ye bak.

## Önemli Kararlar ve Teknik Notlar
- CRM direkt PostgreSQL'e bağlanır — API katmanı yok (sosyal backend bypass)
- `crm.customer_overview` view tüm müşteri verilerini birleştirir
- No Supabase, no Zustand, no complex state — basitlik öncelikli
- Tüm sayfalar Server Component + küçük Client Component'lar (sadece interaktif kısımlar)
- `export const dynamic = 'force-dynamic'` — build zamanı prerender engeli (DB yokken hata verirdi)
- `useFormState` from `react-dom` kullanıldı (React 18 uyumlu — `useActionState` React 19'da)
- recharts Tooltip `formatter` tipi: `(value, name)` — `ValueType | undefined` olabilir, null check gerekli
- `pg` paketi Next.js 14'te `experimental.serverComponentsExternalPackages` ile bildirilmeli
