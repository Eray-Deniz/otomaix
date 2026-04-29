# CRM Admin Paneli — CLAUDE.md

> **DRIFT KORUMA**
> Bu dosya YALNIZCA: proje yapısı, env, deploy, konvansiyonlar.
> Sprint logları → git commit.
> Kararlar → memory/decisions_*.md.
> Aktif iş → Tasks (oturum içi).
> Bu dosyaya changelog EKLENMEZ.

## Proje Amacı

Otomaix ekibinin müşterileri yönettiği dahili admin paneli. Next.js 14 (App Router).
`crm.otomaix.com`'da çalışır. Dışarıya açık değil, şifre korumalı.

## Proje Kılavuzları

- Genel mimari: `~/otomaix/docs/00-platform-mimari.md`
- CRM kılavuzu: `~/otomaix/docs/05-crm-admin.md`

## Deploy

- IP: 178.104.7.200
- Coolify servis adı: `otomaix-crm`
- URL: https://crm.otomaix.com
- Dockerfile: multi-stage, node:20-alpine, standalone output
- GitHub repo: Eray-Deniz/otomaix, Base directory: `apps/crm`

## Veritabanı

- PostgreSQL: `10.0.1.8:5432` (Docker network IP — container içinden `127.0.0.1` çalışmaz)
- Database: `otomaix`
- Schema: `crm` (yazma) + `social` (okuma)
- `crm.customer_overview` view: social.accounts + subscriptions + crm tabloları birleşik
- CRM tabloları: `account_notes`, `account_tags`, `account_communications`, `monthly_usage`
- Migration: `shared/db/migrations/012_crm_tables.sql`

## Bağımlılıklar

- PostgreSQL: direkt bağlantı (`lib/db.ts` pg Pool) — API katmanı yok
- Social backend API: https://api.otomaix.com (sadece `NEXT_PUBLIC_API_URL` olarak)
- n8n: https://n8n.otomaix.com (bildirim workflow'ları CRM-1..6)

## .env Değişkenleri

```
DATABASE_URL=postgresql://otomaix:PASSWORD@10.0.1.8:5432/otomaix
CRM_PASSWORD=
NEXT_PUBLIC_API_URL=https://api.otomaix.com

# Opsiyonel
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

## Auth Sistemi

- Basit şifre koruması — Supabase yok, Zustand yok
- Login: `app/actions.ts` → `login()` server action → `crm-auth` cookie set
- Cookie: `sha256(CRM_PASSWORD + 'otomaix-crm-salt-2026')` — httpOnly, secure
- Web Crypto API (Edge runtime uyumlu)
- `middleware.ts` → cookie doğrular, yoksa `/login`'e yönlendirir

## Klasör Yapısı

```
apps/crm/
├── app/
│   ├── actions.ts                     # login() + logout() server actions
│   ├── customer-actions.ts            # addNote, addCommunication, addTag, removeTag, changePlan
│   ├── layout.tsx                     # Root layout (Inter font, noindex)
│   ├── globals.css                    # Tailwind + dense table stiller
│   ├── (auth)/
│   │   └── login/page.tsx             # Şifre korumalı giriş (useFormState)
│   └── (dashboard)/
│       ├── layout.tsx                 # Sidebar + main wrapper
│       ├── page.tsx                   # Genel Bakış (metrikler + grafikler + tablolar)
│       ├── musteriler/
│       │   ├── page.tsx               # Müşteri listesi (filtreli, sayfalı, CSV export)
│       │   └── [id]/page.tsx          # Müşteri detay (bilgiler + aksiyonlar + etiketler)
│       ├── operasyon/page.tsx         # Yayın hataları + ödeme sorunları + churn riski
│       ├── raporlar/page.tsx          # Aylık büyüme + kullanım + plan dağılımı + trend maliyeti
│       └── bildirimler/page.tsx       # n8n yönlendirme
├── components/
│   ├── layout/Sidebar.tsx             # 200px, #1a1a2e, nav + logout
│   ├── charts/
│   │   ├── PlanDistributionChart.tsx  # recharts Donut
│   │   └── ContentBarChart.tsx        # recharts Bar
│   ├── customers/
│   │   ├── CustomerFilters.tsx        # useRouter filter push
│   │   ├── CustomerActions.tsx        # Plan değiştir, Paddle link
│   │   ├── TagManager.tsx             # Etiket ekle/kaldır
│   │   ├── AddNoteForm.tsx            # İç not
│   │   └── AddCommunicationForm.tsx   # İletişim kaydı
│   ├── operations/
│   │   └── MarkChurnRisk.tsx          # Tek tıkla Churn Riski etiketi
│   └── reports/
│       └── MonthSelector.tsx          # Ay seçici
├── lib/
│   ├── db.ts                          # pg Pool singleton (max 10) + query/queryOne helpers
│   └── utils.ts                       # cn, relativeTime, formatDate, formatCurrency, PLAN_*, STATUS_*
├── middleware.ts                      # Cookie auth kontrolü (Edge runtime)
├── next.config.mjs                    # standalone output, pg external package
├── Dockerfile
└── .env.example
```

## n8n CRM Workflow'ları

| Workflow | ID | Tetik |
|---|---|---|
| CRM-1: Yeni Müşteri | `UzNjZDghyfJq2vYA` | Webhook: `crm/new-customer` |
| CRM-2: Plan Yükseltme | `VoYuC8AGwtT0NpZR` | Webhook: `crm/plan-upgrade` |
| CRM-3: Ödeme Başarısız | `tDnbM6NNy3a3xHdD` | Webhook: `crm/payment-failed` |
| CRM-4: Churn Taraması | `os5XonE1TtptDPBC` | Günlük 09:00 UTC |
| CRM-5: Deneme Bitiyor | `KOsqeGIkrnKIX6rl` | Günlük 10:00 UTC |
| CRM-6: Aylık Rapor | `9esToZdZIeevp0UF` | Ayın 1'i 09:00 UTC |

JSON export: `shared/n8n-workflows/crm-automations.json`

## Konvansiyonlar

- **Tüm sayfalar Server Component** — küçük Client Component'lar sadece interaktif kısımlar için
- **`export const dynamic = 'force-dynamic'`** — DB'li tüm sayfalarda (build zamanı prerender engeli)
- **`pg` paketi:** `next.config.mjs`'de `experimental.serverComponentsExternalPackages: ['pg']`
- **`useFormState`** from `react-dom` (React 18 — `useActionState` React 19'da)
- **recharts Tooltip:** `formatter` tipi `(value, name)` — `ValueType | undefined` olabilir, null check
- **Coolify deploy:** `DATABASE_URL` container içinden Docker network IP kullanmalı (localhost değil)
- **n8n COUNT(*):** IF node'da strict type validation varsa SQL'de `::int` cast kullan (BIGINT → string serialization sorunu)
