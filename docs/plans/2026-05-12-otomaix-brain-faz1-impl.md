# Otomaix Brain Faz 1 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Workflow override:** Otomaix CLAUDE.md "Skill Chain Override Notları" gereği `executing-plans` skill'inin auto-chain'leri (finishing-a-development-branch, using-git-worktrees) **bilinçli olarak çağrılmayacak.** Bu plan kendi içinde yeterli, dış chain'e ihtiyacı yok.

**Goal:** Otomaix'in cross-project beynini (Obsidian wiki vault) `/root/otomaix-brain/`'de ayağa kaldırmak ve 13 dosyalık ilk migration'ı tamamlamak.

**Architecture:** Karpathy LLM Wiki pattern. Markdown + Obsidian + git. Vault VPS'te canonical, Mac/Windows'tan SSHFS+Obsidian ile bakılır. Original docs `docs/_archive/`'e taşınır.

**Tech Stack:** Bash, git, GitHub private repo, Obsidian (görüntüleme tarafı, implementation'a dahil değil).

**Spec referansı:** [`docs/specs/2026-05-12-otomaix-brain-faz1.md`](../specs/2026-05-12-otomaix-brain-faz1.md)

---

## Implementation Progress

| Phase | Tasks | Durum |
|---|---|---|
| **A — Setup** | 1, 2, 3 | ✅ TAMAMLANDI (vault commit'leri: `d55394f`, `d286d4c`, `d1aa199`) |
| **B — Decisions** | 4, 5, 6 | ✅ TAMAMLANDI (commit'ler: `7962c7e` backend 36p, `572978c` frontend 29p, `f5ce138` crm 7p) |
| **C — Cross-project** | 7, 8 | ✅ TAMAMLANDI (Task 7 commit `ce35796` 7 page; Task 8 commit `5e5c8be` 7 page = copywriting 6 + apps/social/architecture 1) |
| **D — Apps/Social** | 9, 10, 11, 12, 13 | ✅ TAMAMLANDI (Task 9 `ff1bbbc` 2p, Task 10 `f923f5e` 1p, Task 11 `4f2f2fa` 1p, Task 12 `9196f8e` 6p, Task 13 `bdbe9d7` 6p) |
| **E — History** | 14 | ✅ TAMAMLANDI (commit `e9e5726`, 5 phase report özet — phase-1/2/3/4/6) |
| **F — Apps/CRM** | 15 | ✅ TAMAMLANDI (commit `d471596`, 4 page — admin-yapisi, n8n-entegrasyon, auth-akisi, deploy) |
| **G — Sources** | 16 | ✅ TAMAMLANDI (commit `f58e996`, raw research frozen kopyalandı + frontmatter) |
| **H — Finalization** | 17, 18, 19, 20, 21, 22, 23 | 🟡 17 ✅ (`c50616d` index 112p) + 18 ✅ (`2de0196` log 18 entry) + 19 ✅ (push) + 20 ✅ (`980a1d9` otomaix archive, brain-CLAUDE.md silindi) + 21 ✅ (commit.md Adım 8 Vault check eklendi); 22-23 sıradaki |
| **I — Post-Faz 1 ek sayfalar** | 24, 25 | ✅ TAMAMLANDI (3 sayfa: claude-code-workflow + economics stub'ları) — vault 115 sayfa, "Stub Pages" discovery mekanizması kuruldu |

**Son güncelleme:** 2026-05-13, Task 24 + Task 25 eklendi ✅. Vault 112 → 115 sayfa, Cross-project / Economics bölümü açıldı, stub keşif mekanizması (frontmatter + log + index kuyruk) devreye alındı. Task 22-23 hâlâ kullanıcı doğrulaması (Madde 4 Obsidian lokal açılış + Madde 7 cold session test query) bekliyor.

**Önceki:** 2026-05-12 (gece), Task 22 ✅ + Task 23 verification kısmen bitti. Vault: 19 commit, 112 sayfa, GitHub push edildi (`Eray-Deniz/otomaix-brain-private`). Task 20 Otomaix repo `docs/_archive/` taşıması bitti (commit `980a1d9`, brain-CLAUDE.md silindi). Task 21 commit.md "Adım 8 Vault check" eklendi.

**Yarın (2026-05-13+) resume:**

1. **Task 23 Madde 4 — Lokal Obsidian (Windows, kullanıcı işi):**
   - Git for Windows kur → Git Bash
   - `cd ~/Documents && git clone https://github.com/Eray-Deniz/otomaix-brain-private.git`
   - Obsidian (https://obsidian.md) indir + "Open folder as vault" → clone klasörü
   - `Ctrl+G` Graph view aç, 112 sayfa + wikilink ağı doğrula
   - Kullanıcı "açıldı" deyince Madde 4 ✅

2. **Task 23 Madde 7 — Test query (kullanıcı onayı):**
   - "FLUX neden seçilmedi" cevabı simüle edildi (context'imde vault dolu)
   - Cold session test daha gerçekçi: yeni session aç, vault sayfalarını sıfırdan keşfederek aynı sorguyu çöz
   - Cevap vault'taki sayfalardan çıktıysa Madde 7 ✅

3. **Final adım:** Memory `project_otomaix_brain_phases.md` "Faz 1 TAMAMLANDI ✅ (2026-05-13)" işaretle, plan dosyasında Phase H tablosu ✅. Task 23 step "Memory'ye Faz 1 tamamlanma notu" tamamlanır.

**Cleanup (opsiyonel, kullanıcı kararı):**
- Coolify panel'den Silverbullet Compose servisini sil — kurulum vazgeçildi, çalışan container çöp halde (yanlış routing, sslip.io fallback). Lokal Obsidian seçildiği için bu servise gerek yok.

**Vault canlı durum:** GitHub'a son push edilmiş commit `2de0196` (Task 18 log populate). Sonraki push gerekmedi (Task 19'dan sonra vault'a commit eklenmedi). Otomaix repo'da son commit `980a1d9` (archive) — push edilmedi (kullanıcı onayı yok).

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

## Task 24: Claude Code workflow sayfası ✅

**Faz 1 kapsamı dışında, post-faz ek sayfa.** Sebep: vault ingest tamamlandıktan sonra geriye dönüp bakınca "meta-sistem (slash command + Superpowers manual mode + kategori 1-4 disiplini) cross-project altında canonical bir referans olmalı" sonucuna varıldı. Bilgi `~/.claude/CLAUDE.md`'de canlı kaynaktan yükleniyor, vault sayfası gelecek-Claude için statik referans + wikilink ağına bağlanma noktası.

- [x] **Step 1: Sayfa yaz** — `cross-project/infrastructure/claude-code-workflow.md` (197 satır, status: active)
- [x] **Step 2: index.md güncelle** — Cross-project / Infrastructure altına 6. madde ekle
- [x] **Step 3: Commit (vault)** — birleştirilmiş commit Task 25 ile (aşağıda)

---

## Task 25: Economics stub sayfaları ✅

**Faz 1 kapsamı dışında, post-faz stub sayfa.** Sebep: vendor pricing ve per-feature cost bilgileri henüz yok (uygulama test aşamasında), ama yapıyı şimdi kurmak ve "doldurma tetiği"ni 3 yerde işaretlemek lazım — yoksa unutulur veya hallucination üretilir.

**Stub discovery mekanizması (Karpathy pattern uyarlaması):**
1. Frontmatter `status: stub` + `needs: [...]` + `when-to-fill: "..."` — Obsidian YAML search ile listelenir
2. `log.md` entry'si — chronological hatırlatıcı
3. `index.md` altında "🚧 Stub Pages (doldurulması bekleniyor)" bölümü — gözle görülür liste

- [x] **Step 1: `cross-project/economics/` klasörü aç** + 2 stub sayfa yaz
  - `vendor-pricing.md` — fal.ai + Anthropic + ElevenLabs + R2 fiyatlandırması (when-to-fill: ilk gerçek aylık faturalar)
  - `per-feature-cost.md` — 1 carousel / video / image / caption üretim maliyeti (when-to-fill: ilk 10-20 gerçek üretim log ortalaması)
- [x] **Step 2: index.md güncelle** — Cross-project / Economics yeni bölümü + "🚧 Stub Pages" en alt bölümü
- [x] **Step 3: log.md entry** — `[2026-05-13 14:20] add | claude-code-workflow + economics stub (3 pages)`
- [x] **Step 4: Commit (vault)** — Task 24 ile birleşik: `vault: add claude-code-workflow + economics stubs (3 pages)`

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

---

# Faz I — B+A Re-migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Workflow override:** Otomaix CLAUDE.md "Skill Chain Override Notları" gereği `executing-plans` skill'inin auto-chain'leri (`finishing-a-development-branch`, `using-git-worktrees`) bilinçli olarak çağrılmayacak.

**Goal:** Faz 1 migration sırasında yapılan attribution hatalarını sistematik temizle. Bilinen Phase 6 hatasını + olası diğer hataları (HIGH + MID tier 38 sayfa) B+A pipeline ile düzelt; LOW tier (77 sayfa) bilinçli olarak skip.

**Architecture:** B (parçalı yaz + hibrit quote-back) + A (fresh-context subagent doğrulama). Tier-based kapsam (15 HIGH B+A / 23 MID sadece A / 77 LOW skip). Severity-tier mismatch handling (critical→sor, minor→otomatik, cosmetic→sessiz). `verification-status` frontmatter alanı ile state tracking.

**Tech Stack:** Bash (script), `Agent` tool (subagent dispatch, `general-purpose` tipi), git (vault commit), Read/Edit/Write tools.

**Spec referansı:** [`docs/specs/2026-05-13-vault-bplus-a-remigration.md`](../specs/2026-05-13-vault-bplus-a-remigration.md)

---

## Implementation Progress (Faz I)

| Aşama | Tasks | Tahmini süre | Durum |
|---|---|---|---|
| **Hazırlık** | H1, H2 | ~1.5 saat | (sıradaki) |
| **HIGH B+A** | T1, T2, T3, T4 | ~7-10 saat | |
| **MID sadece A** | T5, T6, T7, T8 | ~3-4 saat | |
| **Verification** | T9 (cold test) | ~30 dk | |

**Toplam:** 10-15 saat aktif iş, 2-3 oturuma yayılabilir.

**Son güncelleme:** 2026-05-13, Faz I planlandı (spec `a868a99`).

---

## File Structure (Faz I'de dokunulacak dosyalar)

### Vault — değişecek
```
CLAUDE.md                          # H1: schema'ya verification-status alanı eklenir
[115 wiki sayfası]                 # H2: hepsine verification-status: unverified eklenir

# HIGH (15 sayfa — B+A baştan yazılır):
apps/social/architecture/history/phase-1-altyapi-kurulumu.md
apps/social/architecture/history/phase-2-temel-ozellikler.md
apps/social/architecture/history/phase-3-gelismis-ozellikler.md
apps/social/architecture/history/phase-4-saas-hazirlik.md
apps/social/architecture/history/phase-6-trend-sistemi.md
apps/social/architecture/template-system-design.md
apps/social/architecture/carousel-design.md
apps/social/architecture/marketingskills-entegrasyon.md
apps/social/pipeline/carousel.md
apps/social/templates/genel-gorsel-sablon.md
apps/social/templates/carousel-genel-sablon.md
apps/social/templates/shortvideo-genel-sablon.md
apps/social/templates/ozelgun-gorsel-sablon.md
apps/social/templates/ozelgun-carousel-sablon.md
apps/social/templates/ozelgun-shortvideo-sablon.md

# MID (23 sayfa — sadece A doğrulama):
cross-project/infrastructure/{platform-overview,monorepo-yapisi,coolify-deploy,tech-stack,claudemd-template}.md
cross-project/databases/postgres-multi-app-pattern.md
cross-project/integrations/n8n.md
cross-project/copywriting/{somutluk-kurali,loss-aversion,social-proof,gorsel-aci-7-kategori,hook-formulleri-yasak-karari,jtbd-neden-kaldirildi}.md
cross-project/vendors/{fal-ai-models,nano-banana,wan,kling,elevenlabs,anthropic-claude}.md
apps/crm/architecture/{admin-yapisi,n8n-entegrasyon,auth-akisi,deploy}.md

log.md                             # her task sonunda entry
```

### Otomaix repo — değişecek
```
docs/plans/2026-05-12-otomaix-brain-faz1-impl.md   # bu plan dosyası (Faz I bölümü)
```

### Kaynak (read-only, _archive)
```
docs/_archive/01-social-phase1.md
docs/_archive/02-social-phase2.md
docs/_archive/03-social-phase3.md
docs/_archive/04-social-phase4.md
docs/_archive/06-social-trends-phase6.md
docs/_archive/07-social-template-system.md
docs/_archive/11-social-marketingskills.md
docs/_archive/12-social-carousel.md
docs/_archive/00-platform-mimari.md
docs/_archive/05-crm-admin.md
```

---

## Sayfa İşlem Şablonları (her task'ta referans)

### Şablon B+A (HIGH-tier sayfa için)

Her HIGH sayfa için aşağıdaki 10 step uygulanır:

```
1. Kaynak section'lara böl (Read + Grep ile `^## ` başlıkları bul)
2. Mevcut vault sayfasını sil (overwrite için)
3. Frontmatter yaz (title, type, status, last-verified, verification-status: b-written, sources, tags)
4. Her section için B süreci:
   a. Kaynak section'ı oku (satır aralığı)
   b. Vault sayfasına `## başlık` yaz
   c. Attribution-prone bilgi var mı? → varsa verbatim quote bloğu ekle
       Format: `> **Kaynak alıntı** (\`@docs/_archive/<file>.md:NN-MM\`):\n> <verbatim metin>`
   d. Yoksa line-number referans: `> Kaynak: <file>.md:NN-MM`
   e. Paraphrase paragraf/bullet yaz (kaynak gözümün önünde tutarak)
5. İlişkili sayfalar bölümü ekle (en az 1 inbound link için wikilink listesi)
6. Frontmatter `verification-status: b-written` doğrula
7. Subagent dispatch: Agent tool, general-purpose, prompt template (aşağıda)
8. Rapor parse: severity-tier protokolü uygula
   - critical → dur, kullanıcıya özet + öneri → onay → düzelt
   - minor → otomatik düzelt (her birini Edit ile)
   - cosmetic → otomatik düzelt (sessiz)
9. Frontmatter `verification-status: a-verified` set et
10. Vault commit (kaynak başına 1 commit, multiple sayfa içerebilir)
```

### Şablon A-only (MID-tier sayfa için)

```
1. Mevcut vault sayfasını oku (overwrite yok, doğrulama)
2. Subagent dispatch: Agent tool, general-purpose, prompt template
3. Rapor parse: severity-tier protokolü uygula
4. Mismatch varsa düzelt (Edit ile)
5. Frontmatter `verification-status: a-verified` set et
6. Vault commit
```

### Şablon: Subagent prompt template

Her A çağrısında `Agent` tool'a aşağıdaki prompt verilir (placeholder'lar her sayfa için doldurulur):

```
Görev: Vault sayfasını kaynak dosya ile karşılaştır, attribution hatası ara.

Sayfa (oku): {{vault_page_path}}
Kaynak (oku): {{source_file_path}}
Tier: {{HIGH | MID}}

Attribution-prone kategoriler (bunlarda kaynakla eşleşmeyen iddia = critical):
- Numaralı/harfli listelerin atamaları (Layer A/B/C içeriği, Phase X sırası, vendor → model eşlemesi)
- Sayısal değerler (fiyat, kota, eşik, satır sayısı, tarih)
- Model/vendor/SKU/API adları
- Karar verilen seçenek vs reddedilen alternatif
- Kronolojik/numaralı sıra bilgisi

Adımlar:
1. Kaynak dosyayı oku (tamamı)
2. Vault sayfasını oku (tamamı)
3. Sayfadaki her attribution-prone iddia için kaynakta eşleşme ara
4. Mismatch bul → severity belirle:
   - critical = attribution hatası (atama/sıra/sayı/model yanlış)
   - minor = yazım, eksik wikilink, kelime farkı, eksik referans
   - cosmetic = frontmatter alanı eksik, başlık tutarsızlığı, format
5. Mismatch raporu çıkar (markdown numbered list)

Çıktı format:
- Mismatch yoksa: tek satır "OK — sayfa kaynakla tutarlı"
- Aksi halde:
  1. **[critical]** <kısa başlık>
     - Vault iddia: "..."
     - Kaynak (satır N): "..."
     - Tutarsızlık: <açıklama>
  2. **[minor]** ...

ÖNEMLİ: Sadece raporla. Sayfayı DÜZELTME, vault'a YAZMA. Bu salt-okunur audit.
```

---

## Hazırlık — H1: Vault CLAUDE.md schema update

**Files:**
- Modify: `/root/otomaix-brain/CLAUDE.md`

- [ ] **Step 1: Pre-check — mevcut schema'da `verification-status` yok mu doğrula**

```bash
grep -n "verification-status" /root/otomaix-brain/CLAUDE.md
```
Expected: çıktı yok (boş). Eğer satır dönerse alan zaten var, ekleme atlanır.

- [ ] **Step 2: Mevcut schema'da "Frontmatter (her sayfada)" bölümünü bul**

```bash
grep -n "Frontmatter (her sayfada)" /root/otomaix-brain/CLAUDE.md
```
Expected: 1 satır numarası dönüyor.

- [ ] **Step 3: Frontmatter YAML örneğine `verification-status` satırı ekle**

Edit ile mevcut frontmatter blok örneğine bir satır ekle. Eski:

```yaml
---
title: fal.ai Models
type: vendor | decision | template | concept | research | policy | runbook
status: active | superseded | draft
last-verified: 2026-05-12
sources:
  - "[[sources/articles/2026-04-fal-blog]]"
  - "[[sources/research/fal-model-comparison]]"
tags: [video-gen, vendor]
---
```

Yeni (eklenen satır: `verification-status`):

```yaml
---
title: fal.ai Models
type: vendor | decision | template | concept | research | policy | runbook
status: active | superseded | draft
last-verified: 2026-05-12
verification-status: unverified | b-written | a-verified | conflict
sources:
  - "[[sources/articles/2026-04-fal-blog]]"
  - "[[sources/research/fal-model-comparison]]"
tags: [video-gen, vendor]
---
```

- [ ] **Step 4: Schema'ya "Verification status" alt-bölümü ekle**

"Çapraz bağlantı disiplini" bölümünden ÖNCE, "Frontmatter (her sayfada)" bölümünün altına aşağıdaki alt-bölüm eklenir:

```markdown
### Verification status (Faz I'den sonra)

`verification-status` alanı sayfanın doğrulama durumunu işaretler:
- `unverified` — re-migration yapılmadı, audit edilmemiş (default; LOW tier kalıcı bu durumda)
- `b-written` — B parçalı yazıldı, A bekliyor (HIGH için ara state, kalıcı kalmamalı)
- `a-verified` — kaynakla yan yana doğrulandı (Faz I — Re-migration kapsamında)
- `conflict` — critical mismatch bulundu, kullanıcı kararı bekliyor (kalıcı kalmamalı)

Re-migration süreci ve protokol: bkz `@/root/otomaix/docs/specs/2026-05-13-vault-bplus-a-remigration.md`.
```

- [ ] **Step 5: Post-check — schema güncellemesi doğrula**

```bash
grep -n "verification-status" /root/otomaix-brain/CLAUDE.md | wc -l
```
Expected: ≥ 3 satır (YAML örneğinde 1 + alt-bölüm başlığında 1 + 4 değer açıklaması 4 = toplam ≥ 6, ama minimum 3).

- [ ] **Step 6: Commit (vault)**

```bash
cd /root/otomaix-brain
git add CLAUDE.md
git commit -m "vault: add verification-status field to schema (Faz I prep)"
```

- [ ] **Step 7: log.md entry**

`/root/otomaix-brain/log.md` sonuna ekle:

```markdown
## [2026-05-XX HH:MM] schema | verification-status alanı (Faz I prep)
- CLAUDE.md frontmatter şemasına `verification-status` alanı eklendi (4 değer: unverified | b-written | a-verified | conflict)
- "Verification status (Faz I'den sonra)" alt-bölümü yazıldı
- Re-migration süreci referansı `@/root/otomaix/docs/specs/2026-05-13-vault-bplus-a-remigration.md`
- Vault commit: <Step 6 hash>
```

Sonra:
```bash
cd /root/otomaix-brain
git add log.md
git commit -m "vault: log H1 schema update entry"
```

---

## Hazırlık — H2: Batch frontmatter ekleme

**Files:**
- Modify: 115 vault sayfası (frontmatter)

- [ ] **Step 1: Pre-check — kaç sayfada `verification-status` alanı yok say**

```bash
cd /root/otomaix-brain
find . -name "*.md" -not -path "./.git/*" -not -name "CLAUDE.md" -not -name "README.md" -not -name "index.md" -not -name "log.md" | wc -l
```
Expected: 115 sayfa (Faz 1 sonu durumu + 3 yeni).

```bash
find . -name "*.md" -not -path "./.git/*" -not -name "CLAUDE.md" -not -name "README.md" -not -name "index.md" -not -name "log.md" -exec grep -L "^verification-status:" {} \; | wc -l
```
Expected: 115 (hiçbirinde yok).

- [ ] **Step 2: Python script yaz — batch frontmatter ekleme**

`/root/otomaix-brain/scripts/add_verification_status.py` (geçici, faz sonu silinir):

```python
#!/usr/bin/env python3
"""Batch insert `verification-status: unverified` after `last-verified:` in YAML frontmatter."""
import re
from pathlib import Path

VAULT = Path("/root/otomaix-brain")
EXCLUDE = {"CLAUDE.md", "README.md", "index.md", "log.md"}

def add_field(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    if re.search(r"^verification-status:", text, re.MULTILINE):
        return False  # already has it
    # frontmatter must be at top, between --- delimiters
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not m:
        print(f"SKIP (no frontmatter): {path}")
        return False
    fm = m.group(1)
    # insert after `last-verified:` line if present, else before closing ---
    if "last-verified:" in fm:
        new_fm = re.sub(
            r"(last-verified:\s*\S+)",
            r"\1\nverification-status: unverified",
            fm,
            count=1,
        )
    else:
        new_fm = fm + "\nverification-status: unverified"
    new_text = text.replace(f"---\n{fm}\n---\n", f"---\n{new_fm}\n---\n", 1)
    path.write_text(new_text, encoding="utf-8")
    return True

modified = 0
skipped = 0
for md in VAULT.rglob("*.md"):
    if any(part == ".git" for part in md.parts):
        continue
    if md.name in EXCLUDE:
        continue
    if add_field(md):
        modified += 1
    else:
        skipped += 1
print(f"\nModified: {modified}, Skipped: {skipped}, Total: {modified + skipped}")
```

```bash
mkdir -p /root/otomaix-brain/scripts
# (scripts dizini olmasa da python script /tmp'ye yazılabilir)
```

- [ ] **Step 3: Script'i çalıştır**

```bash
cd /root/otomaix-brain
python3 scripts/add_verification_status.py
```
Expected: `Modified: 115, Skipped: 0, Total: 115` (veya yakın — bazı sayfalarda frontmatter eksikse skip artar, o sayfalar tek tek elle düzeltilir).

- [ ] **Step 4: Post-check — kaç sayfada eklendi**

```bash
cd /root/otomaix-brain
find . -name "*.md" -not -path "./.git/*" -not -name "CLAUDE.md" -not -name "README.md" -not -name "index.md" -not -name "log.md" -exec grep -l "^verification-status: unverified" {} \; | wc -l
```
Expected: 115 (veya Step 3 Modified sayısı kadar).

- [ ] **Step 5: Spot-check — bir sayfada nasıl göründüğüne bak**

```bash
head -12 /root/otomaix-brain/apps/social/architecture/history/phase-6-trend-sistemi.md
```
Expected: frontmatter'da `verification-status: unverified` satırı görünmeli.

- [ ] **Step 6: Script'i sil (geçici)**

```bash
rm /root/otomaix-brain/scripts/add_verification_status.py
rmdir /root/otomaix-brain/scripts 2>/dev/null || true
```

- [ ] **Step 7: Commit (vault)**

```bash
cd /root/otomaix-brain
git add -A
git commit -m "vault: batch verification-status: unverified to 115 pages"
```

- [ ] **Step 8: log.md entry**

```markdown
## [2026-05-XX HH:MM] schema | batch unverified (115 pages)
- 115 vault sayfasının frontmatter'ına `verification-status: unverified` eklendi
- Python script ile batch insert (sonra silindi, geçiciydi)
- Vault commit: <Step 7 hash>
```

```bash
git add log.md && git commit -m "vault: log H2 batch frontmatter entry"
```

---

## Task 1: Phase 6 (HIGH, B+A pipeline test + bilinen hata düzeltmesi)

**Files:**
- Modify: `/root/otomaix-brain/apps/social/architecture/history/phase-6-trend-sistemi.md`
- Read: `/root/otomaix/docs/_archive/06-social-trends-phase6.md`

**Bu task pipeline'ın ilk canlı testi.** Phase 6'da bilinen 3 Layer attribution hatası var (kaynak yanıltıcı kanıt: Layer A/B/C atamaları yanlış). Sayfa baştan yazılır, sonra subagent doğrular. Pipeline doğru çalışırsa subagent "OK" döner; çalışmazsa critical mismatch'ler bulur.

- [ ] **Step 1: Pre-check — mevcut sayfanın hatası teyit**

```bash
grep -A 5 "Üç katmanlı yeni mimari" /root/otomaix-brain/apps/social/architecture/history/phase-6-trend-sistemi.md
```
Expected: "Layer A: ... RSS + pytrends evrimi" gibi satır görünür (hatalı atama).

- [ ] **Step 2: Kaynak dosyanın section yapısını çıkar**

```bash
grep -n "^## " /root/otomaix/docs/_archive/06-social-trends-phase6.md
```
Expected: 8-15 arası `##` başlık (hedef, problem, üç katman, layer detayları, kotalar, maliyet, UI, sonuç).

- [ ] **Step 3: Mevcut sayfayı overwrite için Read et (yedek için)**

```
Read /root/otomaix-brain/apps/social/architecture/history/phase-6-trend-sistemi.md
```
(Mevcut içerik referans olmasın diye — yeni yazımı kaynaktan yapacağız.)

- [ ] **Step 4: Yeni sayfa yaz — frontmatter**

Write ile `/root/otomaix-brain/apps/social/architecture/history/phase-6-trend-sistemi.md`:

```yaml
---
title: Phase 6 — Trend Sistemi Yenileme
type: history
status: completed
last-verified: 2026-05-13
verification-status: b-written
sources:
  - "@/root/otomaix/docs/_archive/06-social-trends-phase6.md"
tags: [social, history, phase-6, trends, apify, serper]
---

# Phase 6 — Trend Sistemi Yenileme
```

(Sayfa içeriği Step 5-12'de section section eklenir.)

- [ ] **Step 5: Section "Süre" yaz**

Kaynak satır aralığı: `grep -n "^## Süre\|^## Hedef" /root/otomaix/docs/_archive/06-social-trends-phase6.md` ile bul. Section yaz:

```markdown
## Süre

> Kaynak: `@docs/_archive/06-social-trends-phase6.md:5-10`

~3–4 hafta.
```

- [ ] **Step 6: Section "Hedef" yaz**

Read kaynak satır aralığı (Hedef bölümü). Attribution-prone değil → line-number referans:

```markdown
## Hedef

> Kaynak: `@docs/_archive/06-social-trends-phase6.md:NN-MM`

`/trendler` sayfasını yüzeysel RSS + pytrends mantığından çıkarıp **üç katmanlı, sosyal-medya odaklı, kişiselleşmiş** trend sistemine çevirmek.
```

- [ ] **Step 7: Section "Problem (önceki durum)" yaz**

Kaynak satır aralığı oku. Sayısal değer ("3 gazete RSS", "6 saat cache") → **attribution-prone**, verbatim quote zorunlu:

```markdown
## Problem (önceki durum)

> **Kaynak alıntı** (`@docs/_archive/06-social-trends-phase6.md:NN-MM`):
> - 3 gazete RSS + pytrends
> - Sektör-bazlı 6 saatlik cache
> - Tüm aynı sektördeki kullanıcılar aynı 6 sonucu görüyordu
> - pytrends 429 sonrası fallback'lere düşüyordu
> - Sosyal medya verisi (TikTok, Reddit, YouTube, Twitter, Instagram) yoktu

Mevcut `app/services/trend_analyzer.py` yukarıdaki problemleri taşıyordu. Cache stratejisi kullanıcılar arası farklılaşmayı imkânsız kılıyordu.
```

- [ ] **Step 8: Section "Üç katmanlı yeni mimari" yaz (KRİTİK — attribution hatası burada oldu)**

Kaynak satır aralığını dikkatle oku, Layer A/B/C atamalarını **verbatim quote ile** yapıştır:

```markdown
## Üç katmanlı yeni mimari

> **Kaynak alıntı** (`@docs/_archive/06-social-trends-phase6.md:NN-MM`):
> - Layer A — Ücretsiz gece taraması (cron 06:00 Istanbul)
>   - 7 kaynak paralel: Google News, Google Trends, YouTube, Reddit, trends24.in, Pinterest Trends, TCMB EVDS
>   - Sektör başına paylaşılan cache (`sector_trend_cache`)
>   - Sıfıra yakın maliyet, herkese garantili dolu sayfa
> - Layer B — Kullanıcı tetikli, kişisel
>   - Marka RAG belgeleri + geçmiş postlar → arama sorguları üretilir
>   - Serper.dev (canlı Google TR) + Claude Haiku sentezi
>   - Tetik başı ~$0.005, aylık kota: Starter 5 / Pro 10 / Business 20 / Agency 50
>   - Karar: Claude'un yerleşik web_search'ü değil Serper kullanıldı — ~10x ucuz
> - Layer C — Pro+ aylık rapor
>   - Apify aktörleri: 11 aktör (TikTok, Instagram, Twitter, Trendyol, Hepsiburada, Yemeksepeti, Booking, Sahibinden, vb.)
>   - SECTOR_ACTOR_MAP ile sektöre göre 4-6 aktör seçilir
>   - Çıktı: WeasyPrint PDF → R2'ye yüklenir
>   - Aylık kota: Pro 1 / Business 3 / Agency 10 (Starter kilitli — upgrade funnel)
>   - ~$0.55/rapor

- **Layer A** — Ücretsiz gece taraması: cron 06:00 (`/internal/trends/nightly-sweep`) ile 7 kaynak paralel scrape, sektör-bazlı paylaşılan cache. Maliyet ~$0/ay.
- **Layer B** — Kullanıcı tetikli kişiselleştirme: marka RAG + geçmiş post analizi → Serper.dev + Claude Haiku ile arama+sentez. Tetik başı ~$0.005, plan-bazlı kota.
- **Layer C** — Pro+ aylık rapor: Apify 11 aktörden sektör-spesifik 4-6 aktör → WeasyPrint PDF. ~$0.55/rapor, plan-bazlı kota.
- `trend_analyzer.py` üç katmanı orkestre eden orkestrator olarak refactor edildi.
```

- [ ] **Step 9: Section "Ana kararlar" yaz**

Read kaynak ilgili bölümü. Karar atamaları **attribution-prone** → verbatim quote:

```markdown
## Ana kararlar

> **Kaynak alıntı** (`@docs/_archive/06-social-trends-phase6.md:NN-MM`):
> - Apify sosyal medya scraping için
> - Üç katman ayrılması (concern separation, monolit reddedildi)
> - Personalization brand sector + RAG bağlamı ile
> - Cache layer-bazlı TTL
> - Temperature kuralı: analitik görevler düşük temperature
> - Serper.dev seçildi, Claude web_search reddedildi (~10x maliyet farkı)
> - WeasyPrint PDF üretimi, alternatif (Puppeteer) kullanılmadı
> - Apify aylık plan, ücretli ama predictable

- Apify ile sosyal medya scraping (Instagram, TikTok, Reddit, YouTube, Twitter + e-ticaret aktörleri)
- Üç katman ayrılması — tek monolit `trend_analyzer.py` reddedildi, concern separation tercih edildi
- Personalization — brand sector + RAG bağlamı her kullanıcıya farklı sıralama
- Cache stratejisi — layer-bazlı TTL (A uzun, C kısa)
- Temperature kuralı — analitik görevler default, [[2026-02-15-temperature-kurali]]
- Serper.dev — Claude'un yerleşik web_search'ü yerine seçildi (~10x maliyet farkı + predictable fatura)
```

- [ ] **Step 10: Section "Veritabanı" + "Maliyet (100 kullanıcı senaryosu)" + "Frontend" + "Tamamlanma" + "Sonraki phase" + "İlişkili" yaz**

Aynı disiplin: kaynak satır aralığını oku, attribution-prone içerik var mı kontrol et, varsa verbatim quote yapıştır, yoksa line-number referans.

```markdown
## Veritabanı

> Kaynak: `@docs/_archive/06-social-trends-phase6.md:NN-MM`

Yeni migration (`019_sectors_hierarchy.sql`) hiyerarşik sektör tablosu ekledi: 11 sektör seed, `parent_sector_id` ile alt kırılım için hazır. `brands.sector` text alanı geri-uyumluluk için kaldı, `sector_id` UUID eklendi.

Yeni tablolar: `sector_trend_cache`, `brand_trend_cache`, `trend_usage` (aylık sayaç), `sector_reports` (PDF metadata).

Eski `trend_analyzer.py` DEPRECATED — silinmedi, geri-uyumluluk shim olarak kaldı.

## Maliyet (100 kullanıcı senaryosu)

> **Kaynak alıntı** (`@docs/_archive/06-social-trends-phase6.md:NN-MM`):
> - Layer A: ~$5/ay (toplam, herkese paylaşımlı)
> - Layer B: ~$5/ay (kullanıcı tetik başı ortalama)
> - Layer C: ~$80/ay (Pro+ kullanıcılar arası dağılım)
> - Toplam: ~$90/ay
> - Dağılım: %85 Apify, %10 Haiku, %5 Serper. Layer A ücretsiz.

(Yukarıdaki rakamlar 100 kullanıcı + ortalama tetik senaryosu içindir; gerçek değerler kullanıcı planı dağılımına bağlı.)

## Frontend

> Kaynak: `@docs/_archive/06-social-trends-phase6.md:NN-MM`

`/trendler` sayfası 3-sekmeli yapıya geçti: **Sektör Trendleri** (Layer A) / **Bana Özel** (Layer B) / **Aylık Rapor** (Layer C). Kontör barı + 402 (Payment Required) → toast + `/fiyatlandirma` yönlendirmesi. UpgradeModal düşünüldü ama toast tercih edildi (daha az friction).

## Tamamlanma

✅ Phase 6 sonu (2026-04-16): 3-katmanlı trend sistemi canlıda, Apify scraping aktif, Serper Layer B çalışıyor, kişiselleşmiş öneriler her kullanıcıya farklı sıralama veriyor.

## Sonraki phase'e geçiş

Phase 7 ([[template-system-design]]) — sektör şablonlarından genel şablon stratejisine geçiş ve `caption-first` akış.

## İlişkili

- [[phase-4-saas-hazirlik]] — Paddle kotalandırma altyapısı (Layer B/C kota tabanı)
- [[2026-02-15-temperature-kurali]] — Layer B Haiku sentez sıcaklığı
- [[template-system-design]] — Phase 7'ye geçiş
- [[fal-ai-models]] — vendor ekosistemi (trend'lerden ayrı çalışır)
- [[anthropic-claude]] — Haiku 4.5 Layer B'de
```

(Satır aralıkları kaynaktan grep ile çıkarılır; placeholder `NN-MM` her step'te gerçek satır numarasıyla doldurulur.)

- [ ] **Step 11: Post-check — sayfa yapısı**

```bash
grep -c "^## " /root/otomaix-brain/apps/social/architecture/history/phase-6-trend-sistemi.md
```
Expected: 8-10 section.

```bash
grep -c "Kaynak alıntı\|^> Kaynak:" /root/otomaix-brain/apps/social/architecture/history/phase-6-trend-sistemi.md
```
Expected: ≥ 6 (her section için 1 quote/referans).

- [ ] **Step 12: Subagent dispatch — A doğrulama**

`Agent` tool, `subagent_type: general-purpose`, prompt:

```
Görev: Vault sayfasını kaynak dosya ile karşılaştır, attribution hatası ara.

Sayfa (oku): /root/otomaix-brain/apps/social/architecture/history/phase-6-trend-sistemi.md
Kaynak (oku): /root/otomaix/docs/_archive/06-social-trends-phase6.md
Tier: HIGH

Attribution-prone kategoriler (bunlarda kaynakla eşleşmeyen iddia = critical):
- Numaralı/harfli listelerin atamaları (Layer A/B/C içeriği)
- Sayısal değerler (fiyat, kota, eşik)
- Model/vendor/SKU adları
- Karar verilen seçenek vs reddedilen alternatif

Adımlar:
1. Kaynak dosyayı oku (tamamı)
2. Vault sayfasını oku (tamamı)
3. Sayfadaki her attribution-prone iddia için kaynakta eşleşme ara
4. Mismatch bul → severity belirle (critical | minor | cosmetic)
5. Mismatch raporu çıkar

Çıktı format:
- Mismatch yoksa: "OK — sayfa kaynakla tutarlı"
- Aksi halde: numbered list, her madde [severity] + vault iddia + kaynak satır + tutarsızlık açıklaması

ÖNEMLİ: Sadece raporla. Sayfayı DÜZELTME, vault'a YAZMA.
```

Expected: subagent raporu döner (~30-60 sn). Pipeline doğru çalıştıysa "OK" veya sadece minor/cosmetic.

- [ ] **Step 13: Rapor parse — severity-tier protokolü uygula**

Subagent raporunu oku:
- **Critical mismatch varsa** (Step 8'deki Layer atamalarının yanlış olduğunu raporlarsa pipeline işe yaramıyor demektir — Step 8'i yeniden gözden geçir):
  - Frontmatter `verification-status: conflict` set et (`Edit`)
  - Kullanıcıya özet:
    ```
    ⚠️ Critical mismatch: phase-6-trend-sistemi
    Subagent raporu: <kısa özet>
    Önerim: <düzeltme önerisi>
    Onay? [e/h]
    ```
  - Onay → Edit ile düzelt → tekrar Step 12 (A doğrulama)
- **Sadece minor varsa:** her minor için `Edit`, log.md'de kümülatif sayaç
- **Sadece cosmetic varsa:** her cosmetic için `Edit`, sessiz
- **OK döndüyse:** doğrudan Step 14

- [ ] **Step 14: Frontmatter `verification-status: a-verified` set et**

```
Edit /root/otomaix-brain/apps/social/architecture/history/phase-6-trend-sistemi.md
  old_string: verification-status: b-written
  new_string: verification-status: a-verified
```

- [ ] **Step 15: Post-check — verification-status doğrula**

```bash
grep "verification-status:" /root/otomaix-brain/apps/social/architecture/history/phase-6-trend-sistemi.md
```
Expected: `verification-status: a-verified`

- [ ] **Step 16: Commit (vault)**

```bash
cd /root/otomaix-brain
git add apps/social/architecture/history/phase-6-trend-sistemi.md
git commit -m "vault: re-migrate phase-6-trend-sistemi (B+A, Faz I Task 1)"
```

- [ ] **Step 17: log.md entry**

```markdown
## [2026-05-XX HH:MM] re-migrate | phase-6-trend-sistemi (HIGH, B+A)
- Bilinen 3 Layer attribution hatası düzeltildi (Layer A/B/C içerikleri doğru atandı)
- Section sayısı: ~9, verbatim quote: ~5, line-number referans: ~4
- Subagent raporu: <OK | N minor düzeltme | N critical (düzeltildi)>
- Vault commit: <hash>
```

```bash
cd /root/otomaix-brain && git add log.md && git commit -m "vault: log Task 1 phase-6 re-migration"
```

---

## Task 2: 07-template-system Bölüm 2+3 (HIGH, 7 sayfa)

**Files:**
- Modify (7):
  - `/root/otomaix-brain/apps/social/architecture/template-system-design.md`
  - `/root/otomaix-brain/apps/social/templates/genel-gorsel-sablon.md`
  - `/root/otomaix-brain/apps/social/templates/carousel-genel-sablon.md`
  - `/root/otomaix-brain/apps/social/templates/shortvideo-genel-sablon.md`
  - `/root/otomaix-brain/apps/social/templates/ozelgun-gorsel-sablon.md`
  - `/root/otomaix-brain/apps/social/templates/ozelgun-carousel-sablon.md`
  - `/root/otomaix-brain/apps/social/templates/ozelgun-shortvideo-sablon.md`
- Read: `/root/otomaix/docs/_archive/07-social-template-system.md`

- [ ] **Step 1: Kaynak yapısını çıkar**

```bash
grep -n "^## \|^### " /root/otomaix/docs/_archive/07-social-template-system.md | head -50
```
Expected: kaynak çok bölümlü (~30-50 başlık); template-system-design + 6 şablon detayı + vendor bölümleri içerir.

- [ ] **Step 2: Her sayfa için B+A grubu — "Sayfa İşlem Şablonu B+A" uygulanır**

Aşağıdaki 7 sayfa için sırayla Şablon B+A'nın 10 step'i uygulanır:

**Sayfa 1: `template-system-design.md`** (mimari panoraması, en uzun)
- Kaynak section: Bölüm 2 (template-system-design + tasarım kararları)
- Attribution-prone içerikler: 3-Tier prompt cache mimarisi, backend-driven tek kaynak kararı, Pydantic 1:1 TS senkron, PLATFORM_DEFAULTS merge sıralaması
- Frontmatter: `type: concept`, `status: active`, `verification-status: b-written → a-verified`
- B süreci uygulanır → Subagent dispatch → Severity-tier handling → `a-verified`

**Sayfa 2: `genel-gorsel-sablon.md`**
- Kaynak: Bölüm 3'ün "Genel görsel" alt-bölümü
- Attribution-prone: vendor seçimleri (FLUX → fallback hierarchy), aspect ratio default'ları, prompt komponentleri (system + brand + dynamic + user)
- Frontmatter: `type: template`, `status: active`
- Şablon B+A uygulanır

**Sayfa 3: `carousel-genel-sablon.md`**
- Kaynak: Bölüm 3'ün "Carousel genel" alt-bölümü
- Attribution-prone: slide sayısı default, Nano Banana 2 edit, overlay kuralı, R2 path naming pattern
- Şablon B+A uygulanır

**Sayfa 4: `shortvideo-genel-sablon.md`**
- Kaynak: Bölüm 3'ün "Short video genel" alt-bölümü
- Attribution-prone: Stage 1/2 split, FLUX still + Wan I2V, ElevenLabs Flash 2.5, kota refund yok kararı, awaiting_approval state
- Şablon B+A uygulanır

**Sayfa 5: `ozelgun-gorsel-sablon.md`**
- Kaynak: Bölüm 3'ün "Özel gün görsel" alt-bölümü
- Attribution-prone: brand_reference_images (max 20), scene_reference, Nano Banana edit
- Şablon B+A uygulanır

**Sayfa 6: `ozelgun-carousel-sablon.md`**
- Kaynak: Bölüm 3'ün "Özel gün carousel" alt-bölümü
- Attribution-prone: tatil hikayesi yapısı, slide tutarlılığı (reference image), Nano Banana
- Şablon B+A uygulanır

**Sayfa 7: `ozelgun-shortvideo-sablon.md`**
- Kaynak: Bölüm 3'ün "Özel gün video" alt-bölümü
- Attribution-prone: Kling 2.5 Turbo Pro (premium, sadece bu şablonda), crossfade loop, brand_reference
- Şablon B+A uygulanır

Her sayfa için Subagent dispatch ayrı çağrı (7 dispatch).

- [ ] **Step 3: Post-check — 7 sayfada `verification-status: a-verified`**

```bash
for f in template-system-design.md \
         templates/genel-gorsel-sablon.md \
         templates/carousel-genel-sablon.md \
         templates/shortvideo-genel-sablon.md \
         templates/ozelgun-gorsel-sablon.md \
         templates/ozelgun-carousel-sablon.md \
         templates/ozelgun-shortvideo-sablon.md; do
  grep "verification-status:" /root/otomaix-brain/apps/social/architecture/$f 2>/dev/null || \
  grep "verification-status:" /root/otomaix-brain/apps/social/$f
done
```
Expected: 7 satır, hepsi `a-verified`.

- [ ] **Step 4: Commit (vault, 1 commit 7 sayfa)**

```bash
cd /root/otomaix-brain
git add apps/social/architecture/template-system-design.md apps/social/templates/
git commit -m "vault: re-migrate 07-template-system Bölüm 2+3 (7 pages, B+A)"
```

- [ ] **Step 5: log.md entry**

```markdown
## [2026-05-XX HH:MM] re-migrate | 07-template-system Bölüm 2+3 (7 HIGH pages, B+A)
- Sayfalar: template-system-design + 6 active template
- Critical mismatch: <N> (düzeltildi)
- Minor: <N>, Cosmetic: <N>
- Vault commit: <hash>
```

```bash
git add log.md && git commit -m "vault: log Task 2 template-system re-migration"
```

---

## Task 3: Phase 1-4 reports (HIGH, 4 sayfa)

**Files:**
- Modify (4):
  - `/root/otomaix-brain/apps/social/architecture/history/phase-1-altyapi-kurulumu.md`
  - `/root/otomaix-brain/apps/social/architecture/history/phase-2-temel-ozellikler.md`
  - `/root/otomaix-brain/apps/social/architecture/history/phase-3-gelismis-ozellikler.md`
  - `/root/otomaix-brain/apps/social/architecture/history/phase-4-saas-hazirlik.md`
- Read (4):
  - `/root/otomaix/docs/_archive/01-social-phase1.md`
  - `/root/otomaix/docs/_archive/02-social-phase2.md`
  - `/root/otomaix/docs/_archive/03-social-phase3.md`
  - `/root/otomaix/docs/_archive/04-social-phase4.md`

- [ ] **Step 1: Her phase report için kaynak yapısını çıkar**

```bash
for n in 01 02 03 04; do
  echo "=== ${n} ==="
  grep -n "^## " /root/otomaix/docs/_archive/${n}-social-phase*.md
done
```
Expected: her dosyada ~5-10 section.

- [ ] **Step 2: Phase 1 — Şablon B+A uygula**

- Kaynak: `01-social-phase1.md` (Ay 1-2: VPS, FastAPI, Next.js, Coolify)
- Attribution-prone: tech stack seçimleri (FastAPI vs Flask, Next.js 14 App Router vs Pages, Coolify vs Docker Swarm), VPS sağlayıcı, ilk subdomain'ler
- Şablon B+A 10 step'i uygulanır → Subagent dispatch → handling → `a-verified`

- [ ] **Step 3: Phase 2 — Şablon B+A uygula**

- Kaynak: `02-social-phase2.md` (Ay 2-3: içerik üretimi, takvim, brand kit, auto posting)
- Attribution-prone: Upload-Post API kararı, brand kit veri modeli, takvim default'ları, auto-posting cron
- Şablon B+A uygulanır

- [ ] **Step 4: Phase 3 — Şablon B+A uygula**

- Kaynak: `03-social-phase3.md` (Ay 3-4: RAG, faceless video, rakip, Paddle)
- Attribution-prone: RAG embedding modeli, faceless pipeline ilk versiyonu, Paddle webhook event'ları, rakip analizi vendor
- Şablon B+A uygulanır

- [ ] **Step 5: Phase 4 — Şablon B+A uygula**

- Kaynak: `04-social-phase4.md` (Ay 4-6: self-serve, izleme, gözlemlenebilirlik)
- Attribution-prone: Sentry kararı, Paddle plan'ların kotaları, self-serve onboarding adımları
- Şablon B+A uygulanır

- [ ] **Step 6: Post-check — 4 sayfada `a-verified`**

```bash
for n in 1 2 3 4; do
  grep "verification-status:" /root/otomaix-brain/apps/social/architecture/history/phase-${n}-*.md
done
```
Expected: 4 satır, hepsi `a-verified`.

- [ ] **Step 7: Commit + log**

```bash
cd /root/otomaix-brain
git add apps/social/architecture/history/
git commit -m "vault: re-migrate phase 1-4 history (4 pages, B+A)"
```

log.md entry:
```markdown
## [2026-05-XX HH:MM] re-migrate | phase 1-4 history (4 HIGH pages, B+A)
- Critical mismatch: <N>, Minor: <N>, Cosmetic: <N>
- Vault commit: <hash>
```

```bash
git add log.md && git commit -m "vault: log Task 3 phase 1-4 re-migration"
```

---

## Task 4: Carousel + marketingskills-entegrasyon (HIGH, 3 sayfa)

**Files:**
- Modify (3):
  - `/root/otomaix-brain/apps/social/pipeline/carousel.md`
  - `/root/otomaix-brain/apps/social/architecture/carousel-design.md`
  - `/root/otomaix-brain/apps/social/architecture/marketingskills-entegrasyon.md`
- Read (2):
  - `/root/otomaix/docs/_archive/12-social-carousel.md`
  - `/root/otomaix/docs/_archive/11-social-marketingskills.md`

- [ ] **Step 1: Kaynak yapısını çıkar**

```bash
grep -n "^## " /root/otomaix/docs/_archive/12-social-carousel.md
grep -n "^## " /root/otomaix/docs/_archive/11-social-marketingskills.md
```

- [ ] **Step 2: `pipeline/carousel.md` — Şablon B+A**

- Kaynak: `12-social-carousel.md` operasyonel akış bölümü
- Attribution-prone: pipeline adımları (caption → slide bölme → görsel üretim → overlay → R2 → publish), Nano Banana edit kullanımı, slide naming pattern
- Şablon B+A uygulanır

- [ ] **Step 3: `architecture/carousel-design.md` — Şablon B+A**

- Kaynak: `12-social-carousel.md` 9 tasarım kararı bölümü
- Attribution-prone: 9 kararın sırası ve içeriği (caption-first, slide auto bölme, reference image tutarlılığı, polling pattern, vb.), her kararın gerekçesi
- Şablon B+A uygulanır

- [ ] **Step 4: `architecture/marketingskills-entegrasyon.md` — Şablon B+A**

- Kaynak: `11-social-marketingskills.md` Phase 11 entegrasyon bölümü
- Attribution-prone: Phase 11 tier mapping (hangi psikoloji prensibi hangi şablon tier'ı), post-spec kararları, prompt blok yapısı
- Şablon B+A uygulanır

- [ ] **Step 5: Post-check**

```bash
grep "verification-status:" \
  /root/otomaix-brain/apps/social/pipeline/carousel.md \
  /root/otomaix-brain/apps/social/architecture/carousel-design.md \
  /root/otomaix-brain/apps/social/architecture/marketingskills-entegrasyon.md
```
Expected: 3 satır `a-verified`.

- [ ] **Step 6: Commit + log**

```bash
cd /root/otomaix-brain
git add apps/social/pipeline/carousel.md apps/social/architecture/carousel-design.md apps/social/architecture/marketingskills-entegrasyon.md
git commit -m "vault: re-migrate carousel + marketingskills-entegrasyon (3 pages, B+A)"
git add log.md && git commit -m "vault: log Task 4"
```

log.md entry standart formatta.

---

## Task 5: 00-platform-mimari türevleri (MID, 7 sayfa, sadece A)

**Files:**
- Modify (7):
  - `cross-project/infrastructure/platform-overview.md`
  - `cross-project/infrastructure/monorepo-yapisi.md`
  - `cross-project/infrastructure/coolify-deploy.md`
  - `cross-project/infrastructure/tech-stack.md`
  - `cross-project/infrastructure/claudemd-template.md`
  - `cross-project/databases/postgres-multi-app-pattern.md`
  - `cross-project/integrations/n8n.md`
- Read: `/root/otomaix/docs/_archive/00-platform-mimari.md`

- [ ] **Step 1: Her sayfa için Şablon A-only uygula**

Şablon A-only'nin 6 step'i her sayfa için tekrarlanır:

```
Sayfa N için:
1. Mevcut vault sayfasını oku
2. Subagent dispatch (general-purpose, prompt template, source: 00-platform-mimari.md, page: <N>)
3. Rapor parse, severity-tier handling
4. Mismatch varsa Edit ile düzelt
5. Frontmatter `verification-status: a-verified`
6. (Commit toplu Step 2 sonunda)
```

Subagent dispatch'leri paralel yapılabilir (Agent tool tek mesajda multiple call) — 7 sayfa eşzamanlı doğrulama: süreyi ~7 dk → ~2 dk'ya indirir.

- [ ] **Step 2: Post-check**

```bash
for f in \
  cross-project/infrastructure/platform-overview.md \
  cross-project/infrastructure/monorepo-yapisi.md \
  cross-project/infrastructure/coolify-deploy.md \
  cross-project/infrastructure/tech-stack.md \
  cross-project/infrastructure/claudemd-template.md \
  cross-project/databases/postgres-multi-app-pattern.md \
  cross-project/integrations/n8n.md; do
  echo -n "$f: "
  grep "verification-status:" /root/otomaix-brain/$f
done
```
Expected: 7 satır `a-verified`.

- [ ] **Step 3: Commit + log**

```bash
cd /root/otomaix-brain
git add cross-project/
git commit -m "vault: verify 00-platform-mimari derivatives (7 pages, A-only)"
git add log.md && git commit -m "vault: log Task 5"
```

log.md entry:
```markdown
## [2026-05-XX HH:MM] verify | 00-platform-mimari derivatives (7 MID pages, sadece A)
- Subagent paralel dispatch (7 eşzamanlı)
- Critical mismatch: <N> (düzeltildi), Minor: <N>, Cosmetic: <N>
- Vault commit: <hash>
```

---

## Task 6: 11-marketingskills copywriting (MID, 6 sayfa, sadece A)

**Files:**
- Modify (6):
  - `cross-project/copywriting/somutluk-kurali.md`
  - `cross-project/copywriting/loss-aversion.md`
  - `cross-project/copywriting/social-proof.md`
  - `cross-project/copywriting/gorsel-aci-7-kategori.md`
  - `cross-project/copywriting/hook-formulleri-yasak-karari.md`
  - `cross-project/copywriting/jtbd-neden-kaldirildi.md`
- Read: `/root/otomaix/docs/_archive/11-social-marketingskills.md`

- [ ] **Step 1: Şablon A-only uygula her sayfa için (6 dispatch, paralel)**

- [ ] **Step 2: Post-check**

```bash
for f in somutluk-kurali loss-aversion social-proof gorsel-aci-7-kategori hook-formulleri-yasak-karari jtbd-neden-kaldirildi; do
  echo -n "$f: "
  grep "verification-status:" /root/otomaix-brain/cross-project/copywriting/$f.md
done
```
Expected: 6 satır `a-verified`.

- [ ] **Step 3: Commit + log**

```bash
cd /root/otomaix-brain
git add cross-project/copywriting/
git commit -m "vault: verify copywriting pages (6 pages, A-only)"
git add log.md && git commit -m "vault: log Task 6"
```

---

## Task 7: 07-template-system vendors (MID, 6 sayfa, sadece A)

**Files:**
- Modify (6):
  - `cross-project/vendors/fal-ai-models.md`
  - `cross-project/vendors/nano-banana.md`
  - `cross-project/vendors/wan.md`
  - `cross-project/vendors/kling.md`
  - `cross-project/vendors/elevenlabs.md`
  - `cross-project/vendors/anthropic-claude.md`
- Read: `/root/otomaix/docs/_archive/07-social-template-system.md` (Bölüm 4 — vendor pages)

- [ ] **Step 1: Şablon A-only her sayfa için (6 dispatch, paralel)**

Subagent'a kaynak olarak `07-social-template-system.md`'nin Bölüm 4'ünü (vendor pages) işaret et. Subagent kaynak okurken Bölüm 4'e odaklanır.

- [ ] **Step 2: Post-check**

```bash
for f in fal-ai-models nano-banana wan kling elevenlabs anthropic-claude; do
  echo -n "$f: "
  grep "verification-status:" /root/otomaix-brain/cross-project/vendors/$f.md
done
```
Expected: 6 satır `a-verified`.

- [ ] **Step 3: Commit + log**

```bash
cd /root/otomaix-brain
git add cross-project/vendors/
git commit -m "vault: verify vendor pages (6 pages, A-only)"
git add log.md && git commit -m "vault: log Task 7"
```

---

## Task 8: 05-crm-admin (MID, 4 sayfa, sadece A)

**Files:**
- Modify (4):
  - `apps/crm/architecture/admin-yapisi.md`
  - `apps/crm/architecture/n8n-entegrasyon.md`
  - `apps/crm/architecture/auth-akisi.md`
  - `apps/crm/architecture/deploy.md`
- Read: `/root/otomaix/docs/_archive/05-crm-admin.md`

- [ ] **Step 1: Şablon A-only her sayfa için (4 dispatch, paralel)**

- [ ] **Step 2: Post-check**

```bash
for f in admin-yapisi n8n-entegrasyon auth-akisi deploy; do
  echo -n "$f: "
  grep "verification-status:" /root/otomaix-brain/apps/crm/architecture/$f.md
done
```
Expected: 4 satır `a-verified`.

- [ ] **Step 3: Commit + log**

```bash
cd /root/otomaix-brain
git add apps/crm/architecture/
git commit -m "vault: verify crm-admin pages (4 pages, A-only)"
git add log.md && git commit -m "vault: log Task 8"
```

---

## Task 9: Spot cold test (3 random HIGH sayfa, kullanıcı işi)

**Files:**
- Read: Faz I HIGH listesinden 3 random sayfa
- Modify: `/root/otomaix-brain/log.md` (sonuç)

- [ ] **Step 1: Pre-check — tüm HIGH + MID `a-verified` mi**

```bash
cd /root/otomaix-brain

# HIGH paths
HIGH=(
  apps/social/architecture/history/phase-1-altyapi-kurulumu.md
  apps/social/architecture/history/phase-2-temel-ozellikler.md
  apps/social/architecture/history/phase-3-gelismis-ozellikler.md
  apps/social/architecture/history/phase-4-saas-hazirlik.md
  apps/social/architecture/history/phase-6-trend-sistemi.md
  apps/social/architecture/template-system-design.md
  apps/social/architecture/carousel-design.md
  apps/social/architecture/marketingskills-entegrasyon.md
  apps/social/pipeline/carousel.md
  apps/social/templates/genel-gorsel-sablon.md
  apps/social/templates/carousel-genel-sablon.md
  apps/social/templates/shortvideo-genel-sablon.md
  apps/social/templates/ozelgun-gorsel-sablon.md
  apps/social/templates/ozelgun-carousel-sablon.md
  apps/social/templates/ozelgun-shortvideo-sablon.md
)
for f in "${HIGH[@]}"; do grep -L "verification-status: a-verified" "$f"; done
```
Expected: çıktı boş (hepsi a-verified).

```bash
# MID paths benzer kontrol (Task 5-8'in toplamı, 23 sayfa)
# Hepsi a-verified olmalı
grep -r "verification-status: conflict" /root/otomaix-brain/
```
Expected: çıktı boş (hiç conflict yok).

- [ ] **Step 2: 3 random HIGH sayfa seç + farklı kaynak grubundan**

```bash
# Manuel seçim (script ile rastgele de yapılabilir):
echo "1. Phase report: phase-3-gelismis-ozellikler.md"
echo "2. Template: shortvideo-genel-sablon.md (Stage 1/2 split kararları)"
echo "3. Architecture: carousel-design.md (9 tasarım kararı)"
```

- [ ] **Step 3: Her sayfa için bir soru hazırla**

Sayfada cevabı olan ama doğrudan başlık olmayan sorular:

1. **Phase 3:** *"Faceless video pipeline'ın ilk versiyonu hangi modelleri kullanıyordu?"*
2. **Short video şablonu:** *"Stage 1 ve Stage 2 arasında kullanıcı reject ederse ne oluyor — kota geri verilir mi, audio silinir mi?"*
3. **Carousel design:** *"Carousel'de slide'lar arası görsel tutarlılığı nasıl sağlanıyor?"*

- [ ] **Step 4: Kullanıcı yeni Claude Code oturumu açar**

Sen, kullanıcı olarak:
```bash
# Mac/Windows terminal veya VPS'te yeni session:
cd /root/otomaix && claude
```

Yeni oturumda her soruyu sırayla sor. Cevapları yapıştır.

- [ ] **Step 5: Her cevap için değerlendirme**

Her cevap için 3 kriter:
- ✅ Vault'tan geldi mi? (Read tool ile vault sayfası okundu — *"Read 1 file"* gibi sinyal)
- ✅ `[[wikilink]]` citation içeriyor mu?
- ✅ İçerik kaynakla (orijinal `_archive`) tutarlı mı — attribution doğru mu?

3/3 hepsi tik → o sayfa için ✅.

- [ ] **Step 6: Sonuç matrisi uygulama**

| Sonuç | Yorum | Aksiyon |
|---|---|---|
| 3/3 sayfa ✅ | Vault güvenilir | Faz I tamamlandı |
| 2/3 sayfa ✅ | 1 kaçak hata | Bulunan hatayı düzelt (Şablon B+A tek sayfa); sonra 2 yeni random sayfa ile re-test |
| 1/3 veya 0/3 ✅ | Sistemik problem | Faz I tekrar açılır, kök sebep analizi yapılır |

- [ ] **Step 7: log.md entry — cold test sonucu**

```markdown
## [2026-05-XX HH:MM] cold-test | Faz I verification (3 HIGH sayfa)
- Test sayfaları: phase-3, shortvideo-sablon, carousel-design
- Sorular: <her birinin kısa özeti>
- Sonuç: <3/3 ✅ | 2/3 ✅ | <2 ❌>
- Aksiyon: <Faz I tamamlandı | düzeltme yapıldı + retest | faz tekrar açıldı>
- Test yapılan oturumu link: yeni claude session, lokal
```

```bash
cd /root/otomaix-brain
git add log.md
git commit -m "vault: log Task 9 cold test result"
```

- [ ] **Step 8: 3/3 ✅ ise — Faz I tamamlama commit'i**

```bash
cd /root/otomaix-brain
git commit --allow-empty -m "vault: Faz I re-migration complete (38 pages verified)"
```

- [ ] **Step 9: Memory güncelle — `project_otomaix_brain_phases.md`**

`/root/.claude/projects/-root-otomaix/memory/project_otomaix_brain_phases.md` dosyasında Faz 1 + Faz I durumunu güncelle:

```markdown
- Faz 1 TAMAMLANDI ✅ (2026-05-13)
- Faz I (Re-migration) TAMAMLANDI ✅ (2026-05-XX): 38 sayfa B+A doğrulandı (15 HIGH + 23 MID), cold test 3/3 geçti
- Sıradaki: Faz 2 (Hermes Coolify entegrasyonu) — başlama tarihi belirsiz
```

- [ ] **Step 10: Plan dosyası Implementation Progress (Faz I) tablosu güncelle**

`/root/otomaix/docs/plans/2026-05-12-otomaix-brain-faz1-impl.md` dosyasında Faz I tablosunda son sütun (Durum) ✅ olarak işaretle. Otomaix repo commit:

```bash
cd /root/otomaix
git add docs/plans/2026-05-12-otomaix-brain-faz1-impl.md
git commit -m "docs: mark Faz I complete in implementation plan"
```

---

## Self-Review notları (Faz I)

Plan yazıldıktan sonra spec ile karşılaştırma:

✅ **Spec coverage:**
- Section 1 (bağlam) — Goal'da özet, Task 1 ile bilinen hata düzeltmesi
- Section 2 (tasarım özeti) — Architecture'da, Implementation Progress tablosunda
- Section 3 (somut sayfa listesi) — File Structure'da tam liste, her Task'ta dosya path'leri
- Section 4 (B süreci) — Şablon B+A 10-step'inde tam tanım, Task 1 örnekli, Task 2-4 referans
- Section 5 (A süreci) — Şablon B+A Step 7'de subagent dispatch, Subagent prompt template ayrı bölümde
- Section 6 (mismatch handling) — Şablon B+A Step 8'de severity-tier protokolü, Task 1 Step 13'te uygulanmış
- Section 7 (state tracking) — H1 Schema update, H2 Batch frontmatter, her Task `b-written → a-verified` set
- Section 8 (hazırlık + sıra) — H1, H2, Task 1-9 sırayla
- Section 9 (çıkış kriteri) — Task 9 Step 1 (mekanik) + Step 5-6 (cold test)
- Section 10 (plan yapısı) — Bu plan zaten Section 10'a uygun
- Section 11 (risk değerlendirmesi) — Implicit, her Task'ta verification adımı
- Section 12 (out of scope) — Plan kapsamı dışında yeni sayfa yazma, LOW tier, vb. (zaten plan içinde uygulanmıyor)

✅ **No placeholders:** `TBD`, `// implement here` yok. `<N>` ve `<hash>` log entry'lerinde gerçek değer execution sırasında doldurulur (template-style placeholder, intentional). `<NN-MM>` satır aralığı placeholder'ları execution sırasında `grep -n` ile gerçek değere çevrilir — her Step'te bu yöntem açıklanır.

✅ **Type consistency:** `verification-status` 4 değer her yerde aynı (`unverified`, `b-written`, `a-verified`, `conflict`). Şablon B+A 10 step, Şablon A-only 6 step — sayılar tutarlı. Subagent prompt template tek tanım, her Task'ta referans.

**Bilinen sınır:** Migration task'ları "content parsing" olduğu için klasik TDD failing-test akışı yine uygulanamadı; pre-check + action + post-check verification ile uyarlandı (Faz 1 ile aynı konvansiyon). Skill'in TDD ruhu (her adım doğrulanabilir, hiçbir adım kör değil) korunmuştur.

**Spec referansı:** Spec dosyası ile plan dosyası ayrı (`docs/specs/2026-05-13-...` ve `docs/plans/2026-05-12-...`). Plan, spec'in operationalizasyonudur.
