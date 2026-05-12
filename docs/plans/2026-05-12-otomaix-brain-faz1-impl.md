# Otomaix Brain Faz 1 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Workflow override:** Otomaix CLAUDE.md "Skill Chain Override Notları" gereği `executing-plans` skill'inin auto-chain'leri (finishing-a-development-branch, using-git-worktrees) **bilinçli olarak çağrılmayacak.** Bu plan kendi içinde yeterli, dış chain'e ihtiyacı yok.

**Goal:** Otomaix'in cross-project beynini (Obsidian wiki vault) `/root/otomaix-brain/`'de ayağa kaldırmak ve 13 dosyalık ilk migration'ı tamamlamak.

**Architecture:** Karpathy LLM Wiki pattern. Markdown + Obsidian + git. Vault VPS'te canonical, Mac/Windows'tan SSHFS+Obsidian ile bakılır. Original docs `docs/_archive/`'e taşınır.

**Tech Stack:** Bash, git, GitHub private repo, Obsidian (görüntüleme tarafı, implementation'a dahil değil).

**Spec referansı:** [`docs/specs/2026-05-12-otomaix-brain-faz1.md`](../specs/2026-05-12-otomaix-brain-faz1.md)

---

## File Structure (oluşturulacak)

### Vault root (`/root/otomaix-brain/`)
```
CLAUDE.md                           # schema, brain-CLAUDE.md'den kopya
index.md                            # sayfa kataloğu
log.md                              # ingest/query/lint log
.git/                               # ayrı git repo (GitHub: otomaix-brain-private)
.gitignore                          # standart Obsidian ignores

cross-project/                      # umbrella bilgi
apps/social/                        # social-spesifik
  pipeline/
  templates/                        # 6 aktif şablon + deprecated/
  architecture/
    history/                        # phase 1-6 raporları
apps/crm/                           # Task 16'da açılır
decisions/                          # ADR'lar
research/                           # filed-back queries
sources/                            # frozen referanslar
  research/                         # marketingskills.md
inbox/                              # Faz 2 için, README.md placeholder
```

### Otomaix repo değişiklikleri
```
docs/_archive/                      # Task 22'de oluşturulur
  README.md                         # arşiv açıklaması
  [migrated *.md]                   # 10 dosya taşınır

~/.claude/commands/commit.md        # Task 23'te güncellenir (vault check satırı)

~/.claude/projects/-root-otomaix/memory/
  decisions_backend.md              # Task 5: FROZEN notu eklenir
  decisions_frontend.md             # Task 6: FROZEN notu eklenir
  decisions_crm.md                  # Task 7: FROZEN notu eklenir
  MEMORY.md                         # decisions açıklamaları güncellenir
```

---

# PHASE A — Vault Setup

## Task 1: Vault iskeleti + git init

**Files:**
- Create: `/root/otomaix-brain/` (yeni dizin)
- Create: `/root/otomaix-brain/.gitignore`

- [ ] **Step 1: Pre-check (vault olmamalı)**

```bash
test ! -d /root/otomaix-brain && echo "OK: vault yok"
```
Expected: `OK: vault yok`. Eğer `Test failed` çıkarsa dur, var olan vault'a dokunma — kullanıcıya sor.

- [ ] **Step 2: Vault iskeleti oluştur**

```bash
mkdir -p /root/otomaix-brain/{cross-project,apps/social/pipeline,apps/social/templates/deprecated,apps/social/architecture/history,decisions,research,sources/research,inbox}
```

- [ ] **Step 3: `.gitignore` yaz**

`/root/otomaix-brain/.gitignore`:
```
# Obsidian
.obsidian/workspace*
.obsidian/cache
.obsidian/appearance.json
.trash/

# OS
.DS_Store
Thumbs.db

# Editor
*.swp
*~
```

- [ ] **Step 4: git init + ilk commit**

```bash
cd /root/otomaix-brain && git init && git add .gitignore && git commit -m "vault: initial scaffold"
```

- [ ] **Step 5: Verification**

```bash
test -d /root/otomaix-brain/.git && echo "OK: git başlatıldı"
ls /root/otomaix-brain | sort
git -C /root/otomaix-brain log --oneline | head -1
```
Expected: 10+ klasör listesi, 1 commit `vault: initial scaffold`.

---

## Task 2: Schema (`CLAUDE.md`) yerleştir

**Files:**
- Create: `/root/otomaix-brain/CLAUDE.md` (kopya from `/root/otomaix/docs/brain-CLAUDE.md`)

- [ ] **Step 1: Schema'yı kopyala**

```bash
cp /root/otomaix/docs/brain-CLAUDE.md /root/otomaix-brain/CLAUDE.md
```

- [ ] **Step 2: Verification**

```bash
head -3 /root/otomaix-brain/CLAUDE.md
grep -c "Karpathy" /root/otomaix-brain/CLAUDE.md
```
Expected: `# Otomaix Brain — Wiki Schema` başlığı, `Karpathy` 2-3 kez geçer.

- [ ] **Step 3: Commit**

```bash
cd /root/otomaix-brain && git add CLAUDE.md && git commit -m "vault: add schema (Karpathy LLM Wiki, Otomaix-adapted)"
```

---

## Task 3: `index.md` ve `log.md` placeholder

**Files:**
- Create: `/root/otomaix-brain/index.md`
- Create: `/root/otomaix-brain/log.md`
- Create: `/root/otomaix-brain/inbox/README.md`

- [ ] **Step 1: `index.md` placeholder yaz**

`/root/otomaix-brain/index.md`:
```markdown
# Otomaix Brain Index

Bu vault'un sayfa kataloğu. Her ingest sonrası güncellenir.

## Cross-project

_(Henüz sayfa yok — migration sonrası dolacak)_

## Apps / Social

_(Henüz sayfa yok)_

## Apps / CRM

_(Henüz sayfa yok)_

## Decisions

_(Henüz sayfa yok)_

## Research

_(Henüz sayfa yok)_

## Sources

_(Henüz sayfa yok)_
```

- [ ] **Step 2: `log.md` placeholder yaz**

`/root/otomaix-brain/log.md`:
```markdown
# Otomaix Brain Log

Append-only, chronological. Format: `## [YYYY-MM-DD HH:MM] <action> | <konu>`.

## [2026-05-12 HH:MM] init | vault başlatıldı
- Schema yerleştirildi
- Klasör iskeleti kuruldu
- index.md ve log.md placeholder
```

(Zaman gerçek implementation anında doldurulacak.)

- [ ] **Step 3: `inbox/README.md` placeholder yaz**

`/root/otomaix-brain/inbox/README.md`:
```markdown
# Inbox

**Faz 1'de boş.** Faz 2'de Hermes (background agent) buraya yazacak — Telegram quick capture, günlük dış dünya tarama, haftalık git log farkları vb.

Şu an **dokunulmaz.** Bu klasöre manuel yazma.
```

- [ ] **Step 4: Verification**

```bash
test -f /root/otomaix-brain/index.md && echo "OK: index"
test -f /root/otomaix-brain/log.md && echo "OK: log"
test -f /root/otomaix-brain/inbox/README.md && echo "OK: inbox readme"
```
Expected: 3 satır `OK:`.

- [ ] **Step 5: Commit**

```bash
cd /root/otomaix-brain && git add index.md log.md inbox/README.md && git commit -m "vault: add index.md, log.md, inbox placeholder"
```

---

# PHASE B — Decisions Migration

## Task 4: `decisions_backend.md` → vault parçalama

**Source:** `/root/.claude/projects/-root-otomaix/memory/decisions_backend.md`
**Target:** `/root/otomaix-brain/decisions/YYYY-MM-DD-<konu>.md` (N dosya, her karar ayrı)

- [ ] **Step 1: Source dosyayı oku**

```bash
cat /root/.claude/projects/-root-otomaix/memory/decisions_backend.md
```
Kararları say (genelde `##` başlıkla ayrılır), her birinin: tarih, konu, gerekçe alanlarını çıkar.

- [ ] **Step 2: Her karar için ayrı sayfa oluştur**

Pattern: Her karar `/root/otomaix-brain/decisions/YYYY-MM-DD-<slug>.md` olur. Tarih kararın alındığı tarih, slug konunun 2-4 kelimelik özeti.

Frontmatter template:
```yaml
---
title: <Karar başlığı>
type: decision
area: backend
status: active
last-verified: 2026-05-12
sources:
  - "@/root/.claude/projects/-root-otomaix/memory/decisions_backend.md"
tags: [<ilgili-tag-1>, <ilgili-tag-2>]
---
```

Body yapısı:
```markdown
# <Karar başlığı>

## Karar
<1-2 cümlelik özet>

## Gerekçe
<Neden bu seçildi, alternatifler, trade-off'lar>

## İlişkili
- [[<diğer-karar-veya-konu>]]
- [[<diğer-karar-veya-konu>]]
```

- [ ] **Step 3: Sayım verification**

```bash
ls /root/otomaix-brain/decisions/*.md 2>/dev/null | wc -l
grep -l "area: backend" /root/otomaix-brain/decisions/*.md 2>/dev/null | wc -l
```
Expected: backend kararları sayısına eşit (MEMORY.md özetinden tahmin: ~15-20 karar).

- [ ] **Step 4: Frontmatter kontrolü**

```bash
head -10 /root/otomaix-brain/decisions/*.md 2>/dev/null | grep -E "^title:|^type: decision|^area:" | head -30
```
Expected: her sayfada title, type, area satırları var.

- [ ] **Step 5: Source dosyaya FROZEN notu ekle**

`/root/.claude/projects/-root-otomaix/memory/decisions_backend.md` dosyasının **en üstüne** (frontmatter'dan sonra, body'nin başına) şu satırı ekle:

```markdown
> **FROZEN SNAPSHOT (2026-05-12)** — Yeni kararlar artık `/root/otomaix-brain/decisions/` altında. Bu dosya tarihsel snapshot olarak yerinde kalıyor (Claude session başı auto-load değeri için). Güncelleme yapma.
```

- [ ] **Step 6: Commit (vault)**

```bash
cd /root/otomaix-brain && git add decisions/ && git commit -m "vault: migrate decisions_backend.md (N pages)"
```
(N = oluşan sayfa sayısı, commit mesajında belirt.)

---

## Task 5: `decisions_frontend.md` → vault parçalama

**Source:** `/root/.claude/projects/-root-otomaix/memory/decisions_frontend.md`
**Target:** `/root/otomaix-brain/decisions/YYYY-MM-DD-<konu>.md`

- [ ] **Step 1: Source oku, kararları say**

```bash
cat /root/.claude/projects/-root-otomaix/memory/decisions_frontend.md
```

- [ ] **Step 2: Her karar için ayrı sayfa oluştur**

Aynı frontmatter pattern (Task 4 Step 2), ama `area: frontend`. Source link `decisions_frontend.md`'ye.

- [ ] **Step 3: Verification**

```bash
grep -l "area: frontend" /root/otomaix-brain/decisions/*.md | wc -l
```
Expected: frontend kararları sayısı (~15-20).

- [ ] **Step 4: Source dosyaya FROZEN notu ekle**

Task 4 Step 5 ile aynı format, hedef: `decisions_frontend.md`.

- [ ] **Step 5: Commit**

```bash
cd /root/otomaix-brain && git add decisions/ && git commit -m "vault: migrate decisions_frontend.md (N pages)"
```

---

## Task 6: `decisions_crm.md` → vault parçalama

**Source:** `/root/.claude/projects/-root-otomaix/memory/decisions_crm.md`

- [ ] **Step 1: Source oku**

```bash
cat /root/.claude/projects/-root-otomaix/memory/decisions_crm.md
```

- [ ] **Step 2: Sayfalar oluştur, `area: backend` veya `area: infrastructure` (CRM-spesifik karar tiplerine göre)**

CRM kararları genelde direkt PostgreSQL bağlantısı, cookie auth, Coolify deploy gibi infrastructure / backend konuları kapsıyor. Tag'leme: `tags: [crm, ...]`.

- [ ] **Step 3: Verification**

```bash
grep -l "tags:.*crm" /root/otomaix-brain/decisions/*.md | wc -l
```
Expected: ~5-10 CRM-tag'li karar.

- [ ] **Step 4: FROZEN notu ekle (`decisions_crm.md`)**

- [ ] **Step 5: MEMORY.md index güncelle**

`~/.claude/projects/-root-otomaix/memory/MEMORY.md` dosyasında `decisions_*.md` satırlarının sonuna `(FROZEN, yeni kararlar: vault)` ekle.

Örnek değişiklik:
```
ESKİ: - [Backend mimari kararları](decisions_backend.md) — 3-tier prompt cache, media adapter registry, ...
YENİ: - [Backend mimari kararları (FROZEN, yeni kararlar: vault)](decisions_backend.md) — 3-tier prompt cache, media adapter registry, ...
```

- [ ] **Step 6: Commit (vault)**

```bash
cd /root/otomaix-brain && git add decisions/ && git commit -m "vault: migrate decisions_crm.md (N pages)"
```

---

# PHASE C — Cross-project Migration

## Task 7: `00-platform-mimari.md` → `cross-project/` ana sayfaları

**Source:** `/root/otomaix/docs/00-platform-mimari.md` (6 KB, kısa ve net yapı)
**Target:** `/root/otomaix-brain/cross-project/<alt-klasör>/<sayfa>.md`

- [ ] **Step 1: Source oku, ana bölümleri çıkar**

```bash
cat /root/otomaix/docs/00-platform-mimari.md
grep "^##" /root/otomaix/docs/00-platform-mimari.md
```
Bu dosya genelde: monorepo yapısı, çapraz app kuralları, infrastructure, deploy, environment vb. bölümler içeriyor.

- [ ] **Step 2: İlk alt-klasörleri aç (YAGNI, sadece kullanılacaklar)**

```bash
mkdir -p /root/otomaix-brain/cross-project/{infrastructure,databases,integrations}
```
(Diğerleri — vendors, copywriting, regulation — sonraki task'larda gerektiğinde açılır.)

- [ ] **Step 3: Sayfaları oluştur**

Tahmini sayfa yapısı:
- `cross-project/infrastructure/monorepo-yapisi.md`
- `cross-project/infrastructure/coolify-deploy.md`
- `cross-project/infrastructure/cloudflare-r2.md`
- `cross-project/databases/postgres-multi-app-pattern.md`
- `cross-project/integrations/n8n.md`
- `cross-project/integrations/upload-post.md`

Her sayfa frontmatter:
```yaml
---
title: <başlık>
type: concept
status: active
last-verified: 2026-05-12
sources:
  - "@/root/otomaix/docs/_archive/00-platform-mimari.md"
tags: [<ilgili>]
---
```

İçerik source'taki ilgili bölüm + çapraz link.

- [ ] **Step 4: Verification**

```bash
find /root/otomaix-brain/cross-project -name "*.md" | wc -l
```
Expected: 5-8 sayfa.

- [ ] **Step 5: Commit**

```bash
cd /root/otomaix-brain && git add cross-project/ && git commit -m "vault: migrate 00-platform-mimari (N pages)"
```

---

## Task 8: `11-social-marketingskills.md` → copywriting + architecture

**Source:** `/root/otomaix/docs/11-social-marketingskills.md` (55 KB, tamamlanmış implementation spec)
**Target:**
- `/root/otomaix-brain/cross-project/copywriting/<sayfa>.md` (hook, psikoloji, görsel açı)
- `/root/otomaix-brain/apps/social/architecture/marketingskills-entegrasyon.md` (Otomaix entegrasyon mimarisi)

- [ ] **Step 1: Source oku**

```bash
cat /root/otomaix/docs/11-social-marketingskills.md | head -100
grep "^##" /root/otomaix/docs/11-social-marketingskills.md
```

- [ ] **Step 2: copywriting/ alt-klasörü aç**

```bash
mkdir -p /root/otomaix-brain/cross-project/copywriting
```

- [ ] **Step 3: copywriting sayfaları oluştur**

- `cross-project/copywriting/somutluk-kurali.md` — SOMUTLUK psikoloji prensibi
- `cross-project/copywriting/loss-aversion.md` — Loss Aversion prensibi
- `cross-project/copywriting/social-proof.md` — Social Proof prensibi
- `cross-project/copywriting/hook-formulleri-yasak-karari.md` — Hook kurallarının NEDEN kaldırıldığı (önemli karar, gelecek-Eray "neden zorunlu hook yok" sorusu için)
- `cross-project/copywriting/gorsel-aci-7-kategori.md` — Görsel açı kategorileri (lifestyle, outcome, identity, vb.)
- `cross-project/copywriting/jtbd-neden-kaldirildi.md` — JTBD prensibi fabrication riski nedeniyle kaldırıldı kararı

- [ ] **Step 4: architecture sayfası oluştur**

`/root/otomaix-brain/apps/social/architecture/marketingskills-entegrasyon.md`:

Frontmatter:
```yaml
---
title: Marketing Skills Entegrasyonu (Phase 11)
type: concept
status: active
last-verified: 2026-05-12
sources:
  - "@/root/otomaix/docs/_archive/11-social-marketingskills.md"
  - "@/root/otomaix/docs/_archive/marketingskills.md"
tags: [social, prompt-engineering, marketing]
---
```

İçerik: Tier 1/2/3 prompt mimarisi, hangi skill nereye gitti, Sprint 1-3 özet.

- [ ] **Step 5: Verification**

```bash
ls /root/otomaix-brain/cross-project/copywriting/ | wc -l
test -f /root/otomaix-brain/apps/social/architecture/marketingskills-entegrasyon.md && echo "OK"
```
Expected: 6 dosya copywriting'de, 1 dosya architecture'da.

- [ ] **Step 6: Commit**

```bash
cd /root/otomaix-brain && git add cross-project/copywriting/ apps/social/architecture/ && git commit -m "vault: migrate 11-marketingskills (copywriting + architecture)"
```

---

# PHASE D — Apps/Social Migration

## Task 9: `12-social-carousel.md` → pipeline + architecture

**Source:** `/root/otomaix/docs/12-social-carousel.md` (18 KB)
**Target:**
- `/root/otomaix-brain/apps/social/pipeline/carousel.md`
- `/root/otomaix-brain/apps/social/architecture/carousel-design.md`

- [ ] **Step 1: Source oku, bölümlere ayır**

```bash
cat /root/otomaix/docs/12-social-carousel.md
```

- [ ] **Step 2: pipeline/carousel.md oluştur**

İçerik: carousel pipeline'ı (slider polling, image dağıtım, primary_only/auto modu, R2 download timeout/retry). Operasyonel detaylar.

- [ ] **Step 3: architecture/carousel-design.md oluştur**

İçerik: tasarım kararları (neden carousel ayrı, slide sayısı, görsel modu seçimi). "Neden" odaklı.

- [ ] **Step 4: Cross-link**

İki sayfa birbirine `[[apps/social/pipeline/carousel]]` ve `[[apps/social/architecture/carousel-design]]` ile bağlı olsun. Ayrıca `[[cross-project/copywriting/gorsel-aci-7-kategori]]`'ye link (carousel'de görsel açı kritik).

- [ ] **Step 5: Verification**

```bash
test -f /root/otomaix-brain/apps/social/pipeline/carousel.md && echo "OK: pipeline"
test -f /root/otomaix-brain/apps/social/architecture/carousel-design.md && echo "OK: arch"
grep -c "\[\[" /root/otomaix-brain/apps/social/pipeline/carousel.md
```
Expected: 2 OK, 2+ wikilinks içerik.

- [ ] **Step 6: Commit**

```bash
cd /root/otomaix-brain && git add apps/social/ && git commit -m "vault: migrate 12-carousel (pipeline + architecture)"
```

---

## Task 10: `07-social-template-system.md` Bölüm 1 — Deprecated 22-sektör kararı

**Source:** `/root/otomaix/docs/07-social-template-system.md` (155 KB devasa, **bu task sadece bir bölümü kapsıyor**)
**Target:** `/root/otomaix-brain/apps/social/templates/deprecated/22-sektor-sablonlari-terk-karari.md`

- [ ] **Step 1: Source'ta deprecated kısmı bul**

```bash
grep -n "sektör\|kuyumcu\|eticaret-urun-karti\|saglik\|hukuk" /root/otomaix/docs/07-social-template-system.md | head -20
```

- [ ] **Step 2: 22-sektor-sablonlari-terk-karari.md oluştur**

Frontmatter:
```yaml
---
title: 22 Sektör Şablonları — Terk Kararı
type: decision
area: product
status: superseded
last-verified: 2026-05-12
superseded-by: "[[apps/social/architecture/template-system-design]]"
sources:
  - "@/root/otomaix/docs/_archive/07-social-template-system.md"
tags: [templates, deprecated, history]
---
```

İçerik: Neden 22 sektör-spesifik şablon terk edildi, hangi tarih, neyle değiştirildi (genel + özel gün şablonları). Tarihsel bağlamı koruyan ADR.

- [ ] **Step 3: Verification**

```bash
test -f /root/otomaix-brain/apps/social/templates/deprecated/22-sektor-sablonlari-terk-karari.md
grep "status: superseded" /root/otomaix-brain/apps/social/templates/deprecated/22-sektor-sablonlari-terk-karari.md
```
Expected: dosya var, superseded status mevcut.

- [ ] **Step 4: Commit**

```bash
cd /root/otomaix-brain && git add apps/social/templates/deprecated/ && git commit -m "vault: 07-template-system part 1 - deprecated 22-sektor decision"
```

---

## Task 11: `07-social-template-system.md` Bölüm 2 — Template-system-design

**Target:** `/root/otomaix-brain/apps/social/architecture/template-system-design.md`

- [ ] **Step 1: Source'tan tasarım kararlarını çıkar**

Genel şablon mimarisi (template_data.py yapısı, prompt builder Tier 1/2/3, şablon-vendor eşleşmeleri).

- [ ] **Step 2: template-system-design.md oluştur**

Frontmatter `type: concept`, `area: backend`, içerik: mimari kararlar (templates_data.py tek dosyada neden, 3-tier prompt cache, genel vs özel gün ayrımı, vb.).

- [ ] **Step 3: Verification**

```bash
test -f /root/otomaix-brain/apps/social/architecture/template-system-design.md
wc -l /root/otomaix-brain/apps/social/architecture/template-system-design.md
```
Expected: dosya var, ~50-150 satır.

- [ ] **Step 4: Commit**

```bash
cd /root/otomaix-brain && git add apps/social/architecture/ && git commit -m "vault: 07-template-system part 2 - design"
```

---

## Task 12: `07-social-template-system.md` Bölüm 3 — 6 aktif şablon (her biri ayrı sayfa)

**Target:**
- `/root/otomaix-brain/apps/social/templates/genel-gorsel-sablon.md`
- `/root/otomaix-brain/apps/social/templates/carousel-genel-sablon.md`
- `/root/otomaix-brain/apps/social/templates/shortvideo-genel-sablon.md`
- `/root/otomaix-brain/apps/social/templates/ozelgun-gorsel-sablon.md`
- `/root/otomaix-brain/apps/social/templates/ozelgun-carousel-sablon.md`
- `/root/otomaix-brain/apps/social/templates/ozelgun-shortvideo.md`

- [ ] **Step 1: Source'tan her şablonun bölümlerini bul**

```bash
grep -n "genel-gorsel-sablon\|carousel-genel-sablon\|shortvideo-genel-sablon\|ozelgun-gorsel-sablon\|ozelgun-carousel-sablon\|ozelgun-shortvideo" /root/otomaix/docs/07-social-template-system.md | head -30
```

- [ ] **Step 2: Her şablon için sayfa oluştur**

Sayfa yapısı (her biri için):
```yaml
---
title: <Şablon adı>
type: template
status: active
last-verified: 2026-05-12
sources:
  - "@/root/otomaix/docs/_archive/07-social-template-system.md"
tags: [social, template, <gorsel|carousel|shortvideo>, <genel|ozelgun>]
---
```

Body bölümleri:
- **Açıklama** — ne yapar
- **Prompt Guidance** — guidance metni (templates_data.py'deki karşılığı)
- **Vendor / Model** — hangi model kullanılıyor (Nano Banana, Kling, vb.)
- **İlgili kararlar** — `[[decisions/...]]` linkleri
- **Bilinen kısıtlar** — varsa

- [ ] **Step 3: Verification**

```bash
ls /root/otomaix-brain/apps/social/templates/*.md | wc -l
```
Expected: 6 (deprecated/'nin altındaki sayılmıyor, sadece root templates).

- [ ] **Step 4: Cross-link şablon ↔ design**

Her şablon sayfası `[[apps/social/architecture/template-system-design]]`'e link versin. design sayfası da 6 şablonu listelesin.

- [ ] **Step 5: Commit**

```bash
cd /root/otomaix-brain && git add apps/social/templates/ apps/social/architecture/ && git commit -m "vault: 07-template-system part 3 - 6 active templates"
```

---

## Task 13: `07-social-template-system.md` Bölüm 4 — Vendor sayfaları (cross-project/vendors/)

**Target:**
- `/root/otomaix-brain/cross-project/vendors/fal-ai-models.md`
- `/root/otomaix-brain/cross-project/vendors/nano-banana.md`
- `/root/otomaix-brain/cross-project/vendors/kling.md`
- `/root/otomaix-brain/cross-project/vendors/wan.md`
- `/root/otomaix-brain/cross-project/vendors/elevenlabs.md` (sources: decisions + 07 + memory feedback)
- `/root/otomaix-brain/cross-project/vendors/anthropic-claude.md` (Opus 4.6, Haiku 4.5, prompt caching)

- [ ] **Step 1: vendors/ klasörünü aç**

```bash
mkdir -p /root/otomaix-brain/cross-project/vendors
```

- [ ] **Step 2: Source'tan vendor bilgilerini çıkar**

`07-template-system.md` ve `decisions_backend.md`'den her vendor hakkında: hangi model, ne için kullanılıyor, neden seçildi, alternatifler, fiyat (varsa), bilinen kısıtlar.

- [ ] **Step 3: Vendor sayfaları oluştur**

Pattern (her vendor için):
```yaml
---
title: <Vendor adı>
type: vendor
status: active
last-verified: 2026-05-12
sources:
  - "@/root/otomaix/docs/_archive/07-social-template-system.md"
  - "@/root/.claude/projects/-root-otomaix/memory/decisions_backend.md"
tags: [vendor, <video|image|tts|llm>]
---
```

Body:
- Hangi modeller, hangi use case
- Seçilme gerekçesi
- Alternatifler (denenmiş, terk edilmiş)
- Maliyet notu (varsa)
- İlgili kararlar `[[decisions/...]]`

- [ ] **Step 4: Verification**

```bash
ls /root/otomaix-brain/cross-project/vendors/ | wc -l
```
Expected: 6 vendor sayfası.

- [ ] **Step 5: Commit**

```bash
cd /root/otomaix-brain && git add cross-project/vendors/ && git commit -m "vault: 07-template-system part 4 - vendor pages"
```

---

# PHASE E — Phase Reports History

## Task 14: `01-04 + 06 social-phase*.md` → architecture/history/

**Sources:**
- `/root/otomaix/docs/01-social-phase1.md` (22 KB)
- `/root/otomaix/docs/02-social-phase2.md` (20 KB)
- `/root/otomaix/docs/03-social-phase3.md` (19 KB)
- `/root/otomaix/docs/04-social-phase4.md` (14 KB)
- `/root/otomaix/docs/06-social-trends-phase6.md` (29 KB)

**Target:** `/root/otomaix-brain/apps/social/architecture/history/phase-<N>-<konu>.md`

- [ ] **Step 1: Her phase için bir sayfa**

Her dosya tek bir sayfa olabilir (zaten phase raporu, holistic okunmak için). Parçalamaya gerek yok — özet + ana kararlar + source link.

Frontmatter:
```yaml
---
title: Phase <N> — <konu>
type: history
status: completed
last-verified: 2026-05-12
sources:
  - "@/root/otomaix/docs/_archive/0<N>-social-phase<N>.md"
tags: [social, history, phase-<N>]
---
```

Body:
- Phase hedefi
- Ana kararlar (özet, detay için source link)
- Tamamlanma durumu
- Sonraki phase'e geçiş bağlamı

- [ ] **Step 2: 5 sayfa oluştur**

`phase-1-<konu>.md`, `phase-2-<konu>.md`, `phase-3-<konu>.md`, `phase-4-<konu>.md`, `phase-6-<konu>.md`.

(05 yok docs/'ta — direkt `05-crm-admin.md` farklı dosya, Task 16'da.)

- [ ] **Step 3: Verification**

```bash
ls /root/otomaix-brain/apps/social/architecture/history/ | wc -l
```
Expected: 5 dosya.

- [ ] **Step 4: Commit**

```bash
cd /root/otomaix-brain && git add apps/social/architecture/history/ && git commit -m "vault: migrate phase 1-4,6 reports"
```

---

# PHASE F — Apps/CRM Migration

## Task 15: `05-crm-admin.md` → apps/crm/

**Source:** `/root/otomaix/docs/05-crm-admin.md` (16 KB)
**Target:** `/root/otomaix-brain/apps/crm/` (klasör burada açılır)

- [ ] **Step 1: Klasörü aç**

```bash
mkdir -p /root/otomaix-brain/apps/crm/architecture
```

- [ ] **Step 2: Source oku ve bölümlere ayır**

```bash
cat /root/otomaix/docs/05-crm-admin.md
```

Tahmini bölümler: admin yapısı, n8n entegrasyonu, dashboard, auth, deploy.

- [ ] **Step 3: Sayfaları oluştur**

- `apps/crm/architecture/admin-yapisi.md` — genel mimari
- `apps/crm/architecture/n8n-entegrasyon.md` — n8n workflow'ları ve credential pattern
- `apps/crm/architecture/auth-akisi.md` — cookie sha256 salt auth (decisions_crm'den çapraz link)
- `apps/crm/architecture/deploy.md` — Coolify, Docker network IP

- [ ] **Step 4: Cross-link**

CRM decisions sayfaları (`decisions/...`) buraya bağlansın, buradan da onlara `[[decisions/...]]` link.

- [ ] **Step 5: Verification**

```bash
find /root/otomaix-brain/apps/crm -name "*.md" | wc -l
```
Expected: 4-5 sayfa.

- [ ] **Step 6: Commit**

```bash
cd /root/otomaix-brain && git add apps/crm/ && git commit -m "vault: migrate 05-crm-admin"
```

---

# PHASE G — Sources

## Task 16: `marketingskills.md` (research) → sources/research/

**Source:** `/root/otomaix/docs/marketingskills.md` (9 KB, raw analiz)
**Target:** `/root/otomaix-brain/sources/research/2026-04-marketing-skills-analizi.md` (raw kopya)

- [ ] **Step 1: Olduğu gibi kopyala (parçalama YOK)**

```bash
cp /root/otomaix/docs/marketingskills.md /root/otomaix-brain/sources/research/2026-04-marketing-skills-analizi.md
```

- [ ] **Step 2: Frontmatter ekle (en başa)**

Mevcut dosyanın başına şu satırları ekle:
```yaml
---
title: Marketing Skills Repo Analizi
type: research
status: frozen
captured-date: 2026-04-22
sources:
  - "https://github.com/coreyhaines31/marketingskills"
tags: [research, marketing, prompt-engineering]
---

> **FROZEN** — 22 Nisan 2026 itibariyle. Sonuçları `apps/social/architecture/marketingskills-entegrasyon.md`'de implement edildi.

```

- [ ] **Step 3: Verification**

```bash
head -15 /root/otomaix-brain/sources/research/2026-04-marketing-skills-analizi.md
test -f /root/otomaix-brain/sources/research/2026-04-marketing-skills-analizi.md
```
Expected: frontmatter görünür, dosya mevcut.

- [ ] **Step 4: Commit**

```bash
cd /root/otomaix-brain && git add sources/ && git commit -m "vault: capture marketingskills.md analysis (sources/research)"
```

---

# PHASE H — Finalization

## Task 17: `index.md` doldur

**Target:** `/root/otomaix-brain/index.md`

- [ ] **Step 1: Tüm wiki sayfalarını listele**

```bash
find /root/otomaix-brain -name "*.md" -not -path "*/.git/*" -not -name "CLAUDE.md" -not -name "index.md" -not -name "log.md" -not -name "README.md" | sort
```

- [ ] **Step 2: `index.md`'yi kategoriye göre güncelle**

Her sayfa için `[[path/to/page]] — 1-satırlık özet` formatında. Kategoriler:

```markdown
# Otomaix Brain Index

## Cross-project / Infrastructure
- [[cross-project/infrastructure/monorepo-yapisi]] — Otomaix monorepo katmanları ve sınırları
- [[cross-project/infrastructure/coolify-deploy]] — Coolify üzerinden deploy akışı
- [[cross-project/infrastructure/cloudflare-r2]] — R2 bucket'lar, prefix yapısı

## Cross-project / Databases
- [[cross-project/databases/postgres-multi-app-pattern]] — schema ayrımı, çapraz okuma kuralı

## Cross-project / Integrations
- [[cross-project/integrations/n8n]] — n8n workflow pattern'leri
- [[cross-project/integrations/upload-post]] — Upload-Post Agency JWT akışı

## Cross-project / Vendors
- [[cross-project/vendors/fal-ai-models]] — fal.ai üzerinde Otomaix'in kullandığı modeller
- [[cross-project/vendors/nano-banana]] — Nano Banana 2 image gen
- [[cross-project/vendors/kling]] — Kling V3/2.5 video
- [[cross-project/vendors/wan]] — Wan video adapter
- [[cross-project/vendors/elevenlabs]] — Türkçe TTS sesleri
- [[cross-project/vendors/anthropic-claude]] — Opus 4.6, Haiku 4.5, prompt caching

## Cross-project / Copywriting
- [[cross-project/copywriting/somutluk-kurali]] — Somutluk psikoloji prensibi
- [[cross-project/copywriting/loss-aversion]] — Loss Aversion prensibi
- [[cross-project/copywriting/social-proof]] — Social Proof prensibi
- [[cross-project/copywriting/hook-formulleri-yasak-karari]] — Hook formülü neden kaldırıldı
- [[cross-project/copywriting/gorsel-aci-7-kategori]] — 7 görsel açı kategorisi
- [[cross-project/copywriting/jtbd-neden-kaldirildi]] — JTBD prensibi fabrication riski

## Apps / Social / Architecture
- [[apps/social/architecture/template-system-design]] — Genel + özel gün şablon mimarisi
- [[apps/social/architecture/marketingskills-entegrasyon]] — Phase 11 prompt entegrasyonu
- [[apps/social/architecture/carousel-design]] — Carousel tasarım kararları

## Apps / Social / Architecture / History
- [[apps/social/architecture/history/phase-1-...]] — Phase 1 raporu
- [[apps/social/architecture/history/phase-2-...]] — Phase 2 raporu
- [[apps/social/architecture/history/phase-3-...]] — Phase 3 raporu
- [[apps/social/architecture/history/phase-4-...]] — Phase 4 raporu
- [[apps/social/architecture/history/phase-6-...]] — Phase 6 raporu (trends)

## Apps / Social / Pipeline
- [[apps/social/pipeline/carousel]] — Carousel operasyon pipeline'ı

## Apps / Social / Templates (active)
- [[apps/social/templates/genel-gorsel-sablon]]
- [[apps/social/templates/carousel-genel-sablon]]
- [[apps/social/templates/shortvideo-genel-sablon]]
- [[apps/social/templates/ozelgun-gorsel-sablon]]
- [[apps/social/templates/ozelgun-carousel-sablon]]
- [[apps/social/templates/ozelgun-shortvideo]]

## Apps / Social / Templates (deprecated)
- [[apps/social/templates/deprecated/22-sektor-sablonlari-terk-karari]] — Neden 22 sektör şablonu terk edildi

## Apps / CRM
- [[apps/crm/architecture/admin-yapisi]] — CRM admin genel mimari
- [[apps/crm/architecture/n8n-entegrasyon]] — n8n workflow pattern (CRM)
- [[apps/crm/architecture/auth-akisi]] — Cookie sha256 salt auth
- [[apps/crm/architecture/deploy]] — Coolify Docker network

## Decisions
_(Decisions/ altındaki tüm sayfalar, tarih sırasına göre — bash ile generate edilir)_

## Research
_(research/ altı — Faz 1'de boş başlar, query file-back ile dolacak)_

## Sources
- [[sources/research/2026-04-marketing-skills-analizi]] — Marketing skills repo analizi (frozen)
```

- [ ] **Step 3: Decisions bölümünü bash ile generate et**

```bash
for f in /root/otomaix-brain/decisions/*.md; do
  title=$(grep "^title:" "$f" | head -1 | sed 's/title: *//')
  rel=$(basename "$f" .md)
  echo "- [[decisions/$rel]] — $title"
done | sort
```

Çıktıyı `index.md`'nin Decisions bölümüne yapıştır.

- [ ] **Step 4: Verification**

```bash
grep -c "^\- \[\[" /root/otomaix-brain/index.md
```
Expected: 30-50 satır (tüm sayfa sayısına eşit).

- [ ] **Step 5: Commit**

```bash
cd /root/otomaix-brain && git add index.md && git commit -m "vault: populate index.md catalog"
```

---

## Task 18: `log.md` doldur

**Target:** `/root/otomaix-brain/log.md`

- [ ] **Step 1: Tüm önceki commit'leri log formatına dönüştür**

```bash
git -C /root/otomaix-brain log --pretty=format:"## [%ai] %s%n" --reverse
```

- [ ] **Step 2: `log.md`'yi yeniden yaz**

Format:
```markdown
# Otomaix Brain Log

Append-only, chronological. Format: `## [YYYY-MM-DD HH:MM] <action> | <konu>`.

## [2026-05-12 HH:MM] init | vault başlatıldı
- Schema yerleştirildi
- Klasör iskeleti kuruldu

## [2026-05-12 HH:MM] ingest | decisions_backend.md (N pages)
- N karar sayfası oluşturuldu (decisions/)
- Source dosyaya FROZEN notu eklendi

## [2026-05-12 HH:MM] ingest | decisions_frontend.md (N pages)
...

(devamı her commit'e karşılık gelen entry)
```

- [ ] **Step 3: Verification**

```bash
grep -c "^## \[" /root/otomaix-brain/log.md
```
Expected: 12-15 entry.

- [ ] **Step 4: Commit**

```bash
cd /root/otomaix-brain && git add log.md && git commit -m "vault: populate log.md from commit history"
```

---

## Task 19: GitHub private repo + remote setup + push

**USER ACTION REQUIRED:** GitHub'da private repo oluştur (`eraydeniz/otomaix-brain-private` veya başka bir isim). Boş, README olmadan. Sonra "oluştu" de.

- [ ] **Step 1: Kullanıcıdan repo URL'sini al**

Konuşmadan: `git@github.com:<kullanici>/otomaix-brain-private.git` formatında.

- [ ] **Step 2: Remote ekle**

```bash
cd /root/otomaix-brain
git remote add origin git@github.com:<kullanici>/otomaix-brain-private.git
git remote -v
```
Expected: 2 satır (fetch + push), doğru URL.

- [ ] **Step 3: İlk push**

```bash
cd /root/otomaix-brain && git push -u origin main
```

Eğer branch adı `master` ise:
```bash
git branch -m master main && git push -u origin main
```

- [ ] **Step 4: Verification**

```bash
git -C /root/otomaix-brain branch -vv | grep "origin/main"
```
Expected: branch tracking origin/main gösteriyor.

---

## Task 20: Otomaix repo'da `docs/_archive/` taşıması

**Otomaix repo değişiklikleri** (vault değil — buradaki commit'ler Otomaix kod repo'sunda olacak):

- Create: `/root/otomaix/docs/_archive/`
- Create: `/root/otomaix/docs/_archive/README.md`
- Move: 10 migrate edilmiş `.md` dosya `_archive/`'e

- [ ] **Step 1: `_archive/` klasörü oluştur**

```bash
mkdir -p /root/otomaix/docs/_archive
```

- [ ] **Step 2: README.md yaz**

`/root/otomaix/docs/_archive/README.md`:
```markdown
# Docs Archive

Bu dosyalar `/root/otomaix-brain/` vault'una migrate edildi. **Tek hakikat artık vault.**

Burası tarihsel arşiv — dosyalara dokunma, güncelleme yapma. Yeni karar / sprint çıktısı doğrudan vault'a yazılır (sprint sonu `/commit` skill'i hatırlatır).

Migrate tarihi: 2026-05-12

## Vault'a referans

Her vault sayfası frontmatter'da bu klasördeki orijinal dosyaya `@/root/otomaix/docs/_archive/<dosya>.md` ile link veriyor. Tarihsel iz takibi için orijinaller burada saklanıyor.
```

- [ ] **Step 3: Dosyaları taşı**

```bash
cd /root/otomaix/docs
git mv 00-platform-mimari.md _archive/
git mv 01-social-phase1.md _archive/
git mv 02-social-phase2.md _archive/
git mv 03-social-phase3.md _archive/
git mv 04-social-phase4.md _archive/
git mv 05-crm-admin.md _archive/
git mv 06-social-trends-phase6.md _archive/
git mv 07-social-template-system.md _archive/
git mv 11-social-marketingskills.md _archive/
git mv 12-social-carousel.md _archive/
```

**Not:** `marketingskills.md` (research) **silinir** — sources/'a tam kopya alındı (Task 16), canonical orası. Spec section 2 row 5 gereği.

```bash
git rm /root/otomaix/docs/marketingskills.md
```

**Not:** `brain-CLAUDE.md` arşive **gitmez** — yerinde kalır (CLAUDE.md drift koruma uyarınca schema'nın kaynak yeri otomaix repo'sunda, vault'a sadece kopyası).

- [ ] **Step 4: Verification**

```bash
ls /root/otomaix/docs/_archive/ | wc -l
ls /root/otomaix/docs/*.md 2>/dev/null
```
Expected: 11 dosya `_archive/`'de (10 numaralı + README), root'ta sadece `brain-CLAUDE.md`, `claude-code-kullanim-kilavuzu.md`, `FEATURE_SPEC_intro_outro.md`, `multi-shot-video-pipeline.md` kalır.

- [ ] **Step 5: Commit (Otomaix repo)**

```bash
cd /root/otomaix
git add docs/_archive/README.md
git commit -m "$(cat <<'EOF'
docs: archive migrated files (vault is canonical now)

Vault is at /root/otomaix-brain/. These files moved to docs/_archive/ as
historical snapshot. New decisions/specs go directly to vault.

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)"
```

---

## Task 21: `/commit` skill'i güncelle (vault check sorusu)

**Target:** `~/.claude/commands/commit.md`

- [ ] **Step 1: Mevcut commit.md'yi oku**

```bash
cat ~/.claude/commands/commit.md
```

- [ ] **Step 2: Vault check satırı ekle**

Dosyanın sonuna (commit yapıldıktan SONRA çalışacak adım olarak) şu bölümü ekle:

```markdown

## Adım N+1: Vault check (Otomaix Brain)

Commit oluşturulduktan sonra, kullanıcıya şu soruyu sor:

> "Bu commit'te kalıcı bir mimari karar / yeni vendor / yeni kural var mı? `/root/otomaix-brain/` vault'una yazılması gereken bir şey? (e/h)"

**Eğer evet:**
- Vault'ta uygun sayfayı bul (`decisions/`, `cross-project/`, `apps/...`).
- Yeni karar → `decisions/YYYY-MM-DD-<konu>.md` aç (frontmatter zorunlu).
- Mevcut sayfa güncelleniyorsa `last-verified` tarihini bugüne çek.
- Vault repo'sunda ayrı commit: `cd /root/otomaix-brain && git add . && git commit -m "vault: <açıklama>"`.
- Kullanıcıya `git push` önerir.

**Eğer hayır:** atla, friction sıfır.

**Önemli:** Vault canonical'dır. Yeni karar otomaix repo'sunda commit'lenip vault'a yazılmazsa, gelecek-Claude o kararı bilemez. Disiplin burada hayati.
```

- [ ] **Step 3: Verification**

```bash
grep -c "vault" ~/.claude/commands/commit.md
grep "otomaix-brain" ~/.claude/commands/commit.md
```
Expected: 5+ "vault" geçişi, `otomaix-brain` referansı var.

- [ ] **Step 4: NOT — bu skill dosyası git'lenmiyor (~/.claude/commands)**

Bu dosya kullanıcı-level skill, Otomaix repo'sunda değil. Manuel değişiklik kalıcı, ayrıca commit gerekmez.

---

## Task 22: Test query — vault çalışıyor mu

**Smoke test:** "FLUX neden seçilmedi" sorusu vault'a sorulduğunda doğru cevap geliyor mu?

- [ ] **Step 1: Test sorgusunu hazırla**

Konuşmadan, gerçek bir query çalıştır:

> "FLUX 2 Pro neden seçilmedi, hangi karar?"

- [ ] **Step 2: Claude Code'un vault'a bakmasını bekle**

Beklenen davranış:
1. `index.md`'ye bakar
2. `cross-project/vendors/fal-ai-models.md` veya `decisions/<tarih>-flux-ideogram-karari.md` bulur (eğer böyle bir karar varsa)
3. Cevap verir, `[[wikilink]]` ile citation

- [ ] **Step 3: Cevap kalitesi**

Kabul kriterleri:
- Cevap vault'taki sayfaya referansla geliyor
- Halüsinasyon yok (sadece vault içeriği)
- 3+ sayfa birleştirildiyse, file-back protokolüne uygun olarak Claude Code "bu cevabı `research/` altına alalım mı?" diye soruyor (schema'da yazılı)

- [ ] **Step 4: Sonuç notu**

Eğer cevap **iyi:** Faz 1 başarılı sayılır.
Eğer cevap **eksik:** ilgili sayfalar boş veya cross-link eksik demektir → lint operasyonu çalıştır, eksiklikleri tespit et.

(Bu task'ın commit'i yok — verification adımı.)

---

## Task 23: "Bitti" kriteri doğrulaması

**Spec section 9'daki 8 maddenin verification'ı.**

- [ ] **Madde 1: Vault iskeleti var, git geçmişi 10+ commit**

```bash
test -d /root/otomaix-brain/.git && git -C /root/otomaix-brain log --oneline | wc -l
```
Expected: 10-15 commit.

- [ ] **Madde 2: Sayfa sayısı 250-400 aralığında**

```bash
find /root/otomaix-brain -name "*.md" -not -path "*/.git/*" -not -name "CLAUDE.md" -not -name "README.md" | wc -l
```
Expected: 80-150 sayfa (tahmin: spec'in 250-400 tahmini iyimser olabilir, gerçek migration sırasında doğru sayım çıkar; 80 altı çok az, 400 üstü over-fragmentation).

- [ ] **Madde 3: `index.md` ve `log.md` doldurulmuş**

```bash
grep -c "^- \[\[" /root/otomaix-brain/index.md
grep -c "^## \[" /root/otomaix-brain/log.md
```
Expected: 30+ index entry, 12+ log entry.

- [ ] **Madde 4: SSHFS mount + Obsidian açılıyor**

USER ACTION: Mac/Windows'tan terminal:
```bash
mkdir -p ~/otomaix-brain-mount
sshfs root@<vps-ip>:/root/otomaix-brain ~/otomaix-brain-mount
```
Sonra Obsidian'da "Open folder as vault" → `~/otomaix-brain-mount`. Graph view dolu görünmeli.

Yapıldı mı: e/h kullanıcı doğrular.

- [ ] **Madde 5: GitHub'a push edildi**

```bash
git -C /root/otomaix-brain branch -vv | grep "origin/main"
```
Expected: tracking origin/main, son commit aynı.

- [ ] **Madde 6: `/commit` skill'i vault check içeriyor**

```bash
grep "vault" ~/.claude/commands/commit.md | head -5
```
Expected: 5+ satır.

- [ ] **Madde 7: Test query başarılı (Task 22'de)**

Yapıldı mı: e/h kullanıcı doğrular.

- [ ] **Madde 8: `docs/_archive/` var ve doğru**

```bash
ls /root/otomaix/docs/_archive/ | wc -l
test -f /root/otomaix/docs/_archive/README.md && echo "OK"
```
Expected: 11 dosya (10 migrated + README).

- [ ] **Step (final): Memory'ye Faz 1 tamamlanma notu**

`/root/.claude/projects/-root-otomaix/memory/project_otomaix_brain_phases.md` dosyasında Faz 1 durumunu güncelle: `Faz 1 TAMAMLANDI ✅ (2026-05-XX)`. Memory index güncellenmez (yeni dosya yok).

---

## Final özet (plan kullanıcısı için)

23 task, ~3 ana faz:

| Phase | Tasks | Tahmini süre |
|---|---|---|
| A — Setup | 1-3 | 30-45 dk |
| B — Decisions | 4-6 | 1.5-2 saat (3 dosya × ~30 dk) |
| C — Cross-project | 7-8 | 1.5-2 saat (00 + 11) |
| D — Apps/Social | 9-13 | 5-7 saat (12-carousel + 4-parça 07) |
| E — History | 14 | 30-45 dk (5 phase report) |
| F — Apps/CRM | 15 | 30-45 dk |
| G — Sources | 16 | 10 dk |
| H — Finalization | 17-23 | 1-1.5 saat |

**Toplam: ~10-15 saat aktif iş.** 2-3 oturuma yayılabilir.

---

## Self-Review notları

Plan yazıldıktan sonra spec ile karşılaştırma:

✅ **Spec coverage:**
- Section 1 (bağlam) — Goal/Architecture'da
- Section 2 (mimari kararları) — Task 1, 2 (vault location, schema)
- Section 3 (hiyerarşi) — Task 1 (klasör), File Structure (üst)
- Section 4 (migration kapsamı) — Tasks 4-16
- Section 5 (sıra) — Phase A-G sırası spec ile aynı
- Section 6 (canonical) — Task 20 (_archive/)
- Section 7 (update disiplini) — Task 21 (/commit skill)
- Section 8 (backup) — Task 19 (GitHub push)
- Section 9 (bitti kriteri) — Task 23

✅ **No placeholders:** "TBD" / "implement here" yok. Migration content task'larında "Claude Code parses source" kabul edilebilir çünkü içerik önceden bilinmez — yapı (frontmatter, target path, verification) net.

✅ **Type consistency:** vault paths, frontmatter alanları, commit prefix'leri (`vault:` ve `docs:`) tüm task'larda tutarlı.

**Bilinen sınır:** Migration task'ları gerçek "code" değil "content parsing" olduğu için klasik TDD failing-test akışı uygulanamadı; pre-check + action + post-check verification ile uyarlandı. Skill'in TDD ruhu (her adım doğrulanabilir, hiçbir adım kör değil) korunmuştur.
