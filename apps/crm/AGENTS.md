# AGENTS.md

> Bu dosyanın marker'lı bloğu `/sync-agents-md` komutu tarafından
> Codex'in CLAUDE.md damıtması ile üretilir. Marker dışına manuel
> içerik ekleyebilirsin — korunur.

<!-- BEGIN CODEX-DISTILLED -->
> Bu icerik Codex CLI icin /root/otomaix/apps/crm/CLAUDE.md'den damitilmistir.

## Proje Amacı

CRM, Otomaix ekibinin müşterileri yönettiği dahili admin panelidir.

- Next.js 14 App Router kullanır.
- `crm.otomaix.com` üzerinde çalışır.
- Dışarıya açık değildir; basit şifre koruması vardır.

## Dokümantasyon

- Genel mimari: `~/otomaix/docs/00-platform-mimari.md`
- CRM kılavuzu: `~/otomaix/docs/05-crm-admin.md`

## Deploy

- IP: `178.104.7.200`
- Coolify servis adı: `otomaix-crm`
- URL: `https://crm.otomaix.com`
- Dockerfile: multi-stage, `node:20-alpine`, standalone output
- GitHub repo: `Eray-Deniz/otomaix`
- Base directory: `apps/crm`

## Veritabanı

- PostgreSQL host: `10.0.1.8:5432`
- Container içinden `127.0.0.1` kullanılmaz; Docker network IP kullanılmalıdır.
- Database: `otomaix`
- CRM yazma schema’sı: `crm`
- Social okuma schema’sı: `social`
- `crm.customer_overview` view, `social.accounts`, subscriptions ve CRM tablolarını birleştirir.
- CRM tabloları:
  - `account_notes`
  - `account_tags`
  - `account_communications`
  - `monthly_usage`
- Migration dosyası: `shared/db/migrations/012_crm_tables.sql`

## Bağımlılıklar ve Entegrasyonlar

- PostgreSQL’e doğrudan bağlanılır.
- DB bağlantısı `lib/db.ts` içindeki `pg Pool` ile yapılır.
- CRM için ayrı API katmanı yoktur.
- Social backend API yalnızca `NEXT_PUBLIC_API_URL` olarak kullanılır.
- Social backend URL: `https://api.otomaix.com`
- n8n URL: `https://n8n.otomaix.com`
- CRM bildirim workflow’ları `CRM-1..6` kapsamındadır.

## Ortam Değişkenleri

Zorunlu:

```env
DATABASE_URL=postgresql://otomaix:PASSWORD@10.0.1.8:5432/otomaix
CRM_PASSWORD=
NEXT_PUBLIC_API_URL=https://api.otomaix.com
```

Opsiyonel:

```env
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

## Auth Sistemi

- Basit şifre koruması kullanılır.
- Supabase kullanılmaz.
- Zustand kullanılmaz.
- Login akışı: `app/actions.ts` içindeki `login()` server action.
- Login başarılı olduğunda `crm-auth` cookie set edilir.
- Cookie değeri: `sha256(CRM_PASSWORD + 'otomaix-crm-salt-2026')`
- Cookie `httpOnly` ve `secure` olmalıdır.
- Hash için Web Crypto API kullanılır; Edge runtime uyumluluğu korunmalıdır.
- `middleware.ts`, cookie doğrulaması yapar.
- Cookie yoksa kullanıcı `/login` sayfasına yönlendirilir.

## Klasör Yapısı

CRM app kökü: `apps/crm/`

Önemli alanlar:

- `app/actions.ts`: `login()` ve `logout()` server actions
- `app/customer-actions.ts`: müşteri aksiyonları
- `app/layout.tsx`: root layout, Inter font, noindex
- `app/globals.css`: Tailwind ve dense table stilleri
- `app/(auth)/login/page.tsx`: şifreli giriş
- `app/(dashboard)/layout.tsx`: sidebar ve main wrapper
- `app/(dashboard)/page.tsx`: genel bakış
- `app/(dashboard)/musteriler/page.tsx`: müşteri listesi
- `app/(dashboard)/musteriler/[id]/page.tsx`: müşteri detayı
- `app/(dashboard)/operasyon/page.tsx`: operasyon ekranı
- `app/(dashboard)/raporlar/page.tsx`: raporlar
- `app/(dashboard)/bildirimler/page.tsx`: n8n yönlendirme
- `components/layout/Sidebar.tsx`: sidebar
- `components/charts/`: recharts grafikleri
- `components/customers/`: müşteri filtreleri, aksiyonları, etiketler, not ve iletişim formları
- `components/operations/MarkChurnRisk.tsx`: churn riski etiketi
- `components/reports/MonthSelector.tsx`: ay seçici
- `lib/db.ts`: `pg Pool` singleton ve query helper’ları
- `lib/utils.ts`: format/helper sabitleri
- `middleware.ts`: cookie auth kontrolü
- `next.config.mjs`: standalone output ve `pg` external package ayarı

## n8n CRM Workflow’ları

JSON export dosyası:

- `shared/n8n-workflows/crm-automations.json`

Workflow’lar:

| Workflow | ID | Tetik |
|---|---|---|
| CRM-1: Yeni Müşteri | `UzNjZDghyfJq2vYA` | Webhook: `crm/new-customer` |
| CRM-2: Plan Yükseltme | `VoYuC8AGwtT0NpZR` | Webhook: `crm/plan-upgrade` |
| CRM-3: Ödeme Başarısız | `tDnbM6NNy3a3xHdD` | Webhook: `crm/payment-failed` |
| CRM-4: Churn Taraması | `os5XonE1TtptDPBC` | Günlük 09:00 UTC |
| CRM-5: Deneme Bitiyor | `KOsqeGIkrnKIX6rl` | Günlük 10:00 UTC |
| CRM-6: Aylık Rapor | `9esToZdZIeevp0UF` | Ayın 1’i 09:00 UTC |

## Kod Konvansiyonları

- Tüm sayfalar varsayılan olarak Server Component olmalıdır.
- Client Component yalnızca küçük ve interaktif parçalar için kullanılmalıdır.
- DB kullanan tüm sayfalarda `export const dynamic = 'force-dynamic'` eklenmelidir.
- `pg` paketi için `next.config.mjs` içinde `experimental.serverComponentsExternalPackages: ['pg']` ayarı bulunmalıdır.
- React 18 kullanıldığı için form state tarafında `react-dom` içinden `useFormState` kullanılmalıdır.
- React 19 API’si olan `useActionState` kullanılmamalıdır.
- Recharts `Tooltip` formatter tipi `(value, name)` şeklindedir.
- Recharts formatter’da `ValueType | undefined` gelebilir; null/undefined check yapılmalıdır.
- Coolify deploy’da `DATABASE_URL`, container içinden Docker network IP kullanmalıdır; `localhost` kullanılmamalıdır.
- n8n `COUNT(*)` sonuçlarında IF node strict type validation varsa SQL tarafında `::int` cast kullanılmalıdır. BIGINT string serialization sorununa yol açabilir.
<!-- END CODEX-DISTILLED -->
