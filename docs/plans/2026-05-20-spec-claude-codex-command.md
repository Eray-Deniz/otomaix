# spec-claude-codex Komutu Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Workflow override:** Otomaix `/root/otomaix/CLAUDE.md` "Skill Chain Override Notları" gereği `executing-plans`'in auto-chain'leri (`finishing-a-development-branch`, `using-git-worktrees`) **bilinçli çağrılmaz.** Bu plan kendi içinde yeterli.

**Goal:** `/plan-claude-codex` komutunu `/spec-claude-codex` olarak yeniden adlandırmak ve approved spec'teki (`docs/specs/2026-05-20-spec-claude-codex-command.md`) akış delta'larını yeni canonical komuta işlemek; eskiyi deprecated stub yapmak; canlı referansları güncellemek; vault'u rollout gate olarak ayrı onaylı adımda kapatmak.

**Architecture:** Komut dosyaları `~/.claude/commands/` altında — **otomaix git'inin dışında, global** (commit yok). Faz A yeni dosyayı `cp` + hedefli edit'lerle kurar; anti-drift kapsamı **dar**: yalnız Adım 2 Codex `task` çağrısı verbatim korunur, Adım 6 adversarial-review scope/çağrı bloğu spec §3 İstisna (Bulgu 2) gereği kasıtlı değiştirilir. Vault `/root/otomaix-brain/` kendi git'i; Codex vault'a yazmaz, sadece patch önerir. Rollout gate: vault güncellenip doğrulanmadan rename "done" sayılmaz.

**Tech Stack:** Markdown, shell (`cp`, `rg`, git), Codex companion (`codex-companion.mjs`). Kod yok → TDD yerine her task'ta `rg`/davranış doğrulaması.

**Spec referansı:** [`docs/specs/2026-05-20-spec-claude-codex-command.md`](../specs/2026-05-20-spec-claude-codex-command.md)

---

## Preflight — İlk Task'tan Önce

```bash
git -C /root/otomaix status --short
git -C /root/otomaix-brain status --short
ls -la ~/.claude/commands/plan-claude-codex.md ~/.claude/commands/spec-claude-codex.md 2>&1
```

- Repo/vault'ta plan'la ilgisiz dirty dosya varsa kullanıcıya sor (ayrı commit / stash).
- `spec-claude-codex.md` **zaten varsa** dur — bu plan onu sıfırdan kuruyor; mevcutsa kullanıcıya sor (üzerine mi yazılsın).
- Bu plan otomaix repo'suna **yeni commit üretmez** (komut dosyaları global). Tek repo commit'i: bu plan dosyasının kendisi (Adım 5, /write-plan akışı). Vault commit'i Faz E'de, push kullanıcı onayıyla.

## Tool Policy — Codex vs Claude

- **Claude (default):** dosya işlemleri `cp` + Write/Edit ile.
- **Codex CLI:** Bu planın ana dosyaları `~/.claude/commands/` altında — Codex sandbox'ının writable root'u **dışında**. Codex global command dosyalarına, vault'a ve memory'ye **yazamaz**; yalnızca patch/diff **önerir** (stdout). Uygulamayı Claude veya kullanıcı yapar. Yani **bu planı Codex tek başına uygulayamaz** — Claude-driven (veya kullanıcı) gerekir.

---

## Implementation Progress

| Phase | Tasks | Durum | Not |
|---|---|---|---|
| **A — Yeni komut (`spec-claude-codex.md`)** | 1–9 | ⬜ | cp + hedefli edit; bash blokları verbatim |
| **B — Eski komutu stub yap** | 10 | ⬜ | A bittikten SONRA (sıra kritik) |
| **C — Canlı referans güncelleme** | 11–13 | ⬜ | handoff, sync-agents-md, init |
| **D — Repo doğrulama** | 14 | ⬜ | rg sweep |
| **E — Vault (ROLLOUT GATE)** | 15–16 | ⬜ | ayrı onay + last-verified bump; Codex yazmaz |
| **F — Closure** | 17 | ⬜ | rollout gate doğrulama |

---

## File Structure

### Oluşturulacak
```
~/.claude/commands/spec-claude-codex.md      # yeni canonical komut (cp tabanlı)
```

### Değiştirilecek
```
~/.claude/commands/plan-claude-codex.md      # → deprecated stub (içerik tamamen değişir)
~/.claude/commands/handoff.md                # 2 referans (satır 41, 58)
~/.claude/commands/sync-agents-md.md         # 1 referans (satır 170)
~/.claude/commands/init.md                   # 2 referans (satır 120, 135)
/root/otomaix-brain/cross-project/infrastructure/codex-entegrasyonu.md  # sources + inline (Faz E)
/root/otomaix-brain/decisions/2026-05-19-claude-codex-aktif-task-layer.md  # workflow satırı (Faz E)
```

### Dokunulmayan
```
/root/otomaix/docs/specs/2026-05-19-*, docs/plans/2026-05-19-*   # donmuş tarihi kayıt
/root/otomaix-brain/log.md                                       # tarihsel log
~/.claude/CLAUDE.md, ~/.codex/AGENTS.md                          # global
```

---

# PHASE A — Yeni Komut Dosyası

**Strateji:** `cp` ile kaynaktan başla (tüm içerik verbatim gelir), sonra yapıyı approved spec §4/§5'e göre hedefli edit'lerle dönüştür.

**Anti-drift kapsamı dar — sadece bir blok:** yalnız Adım 2'nin Codex `task` çağrı mekaniği (companion `find`, `--fresh --wait`, `--cwd "$PROJECT_ROOT"`, positional prompt) **verbatim korunur**; bu blok edit'lerle yeniden yazılmaz, yalnız prompt metnine active task özeti eklenir.

**Kasıtlı değişen yerler (verbatim DEĞİL):** (a) self-reference `/plan-claude-codex → /spec-claude-codex` her yerde; (b) Adım 6 adversarial-review **scope handling + çağrısı** (Bulgu 2 miras bug fix — koşullu scope, `HEAD~1` kaldırılır); (c) karar/lifecycle bölümleri (Adım 7-12 yeni model, eski `<TURN>` tabanlı akış tamamen kaldırılır).

## Task 1: Kaynaktan kopyala

**Files:** Create `~/.claude/commands/spec-claude-codex.md`

- [ ] **Step 1: cp**

```bash
cp ~/.claude/commands/plan-claude-codex.md ~/.claude/commands/spec-claude-codex.md
```

- [ ] **Step 2: Doğrula (kaynakla birebir aynı olmalı şu an)**

```bash
diff ~/.claude/commands/plan-claude-codex.md ~/.claude/commands/spec-claude-codex.md && echo "IDENTICAL ✓"
wc -l ~/.claude/commands/spec-claude-codex.md   # ~293
```

Beklenen: `IDENTICAL ✓`. (Commit yok — global dosya.)

## Task 2: Frontmatter + Görev + Akış Genel Bakış

**Files:** Modify `~/.claude/commands/spec-claude-codex.md`

- [ ] **Step 1: Frontmatter description'ı güncelle**

old:
```yaml
description: Çift-perspektif plan tasarımı (Claude + Codex ön-scoping → /brainstorm → Codex adversarial review döngüsü, max 3 turn)
argument-hint: <fikir cümlesi>
```
new:
```yaml
description: Çift-perspektif spec/tasarım üretimi (Claude + Codex ön-scoping → /brainstorm → Codex adversarial review; spec/tasarım üretir, plan DEĞİL — plan için /write-plan)
argument-hint: <fikir cümlesi>
```

- [ ] **Step 2: "## Akış Genel Bakış" bloğunu yeni 12-adım akışıyla değiştir**

old:
```
0. Fikri teslim al
1. Ön-scoping (Claude + Codex paralel)
2. /brainstorm (sokratik tasarım — Skill tool ile)
3. Codex adversarial review (spec markdown'ı üstünde)
4. Karar: onayla → biter, güncelle → 2'ye dön (max 3 turn)
```
new:
```
0.   Active context read (koşullu — docs/active/ varsa)
1.   Fikri teslim al
1.5  Resume kontrolü (açık draft/pending spec taraması)
2.   Ön-scoping (Claude + Codex paralel; active task özeti enjekte)
3.   Kullanıcı yön seçer
4.   /brainstorm ile spec draft (draft frontmatter + codex_review_*)
5.   Consistency sweep (Codex öncesi)
6.   Codex adversarial review (spec içeriği doğrudan; verbatim + log append)
7.   Karar: onayla → 9; güncelle → 4'e dön (full_design_iteration sayacı)
8.   (sayaç — Adım 5/7'ye gömülü)
9.   Final consistency sweep
10.  Finalizasyon (status: spec-approved)
11.  Active task hatırlatması (vault YOK)
12.  Final rapor (+ /write-plan yönlendirmesi)
```

- [ ] **Step 3: Doğrula**

```bash
rg -n "spec/tasarım üretir, plan DEĞİL|Active context read" ~/.claude/commands/spec-claude-codex.md
```

## Task 3: Adım 0 (active context) + Adım 1 (fikri al) + Adım 1.5 (resume)

**Files:** Modify `~/.claude/commands/spec-claude-codex.md`

Kaynaktaki `## Adım 0: Fikri Teslim Al` bölümünü bul. **Öncesine** yeni Adım 0 ekle, eski Adım 0'ı Adım 1 yap, sonrasına Adım 1.5 ekle.

- [ ] **Step 1: "## Adım 0: Fikri Teslim Al" başlığını ve gövdesini değiştir**

old:
```
## Adım 0: Fikri Teslim Al

`$ARGUMENTS` doluysa onu fikir olarak kullan.

Boşsa kullanıcıya sor:
> "Hangi fikir/özellik için tasarım istiyorsun? Tek-iki cümlelik özet ver."

Fikri `<IDEA>` olarak sakla.
```
new (tam içerik — spec §4 Adım 0 + 1 + 1.5'ten):
```
## Adım 0: Active Context Read (koşullu)

- `docs/active/CURRENT.md` yoksa/boşsa (`_(no active tasks)_`) → sessizce atla.
- Varsa active-layer session-start protokolü: fikirle ilgili tek task → otomatik;
  birden fazla → kullanıcıya sor (numbered list); hiçbiri ilgisiz → atla.
- Seçilen task için `docs/active/<slug>/TASK.md` + `HANDOFF.md` oku.
- **Sadece bağlam** — bu komut active layer dosyalarını değiştirmez.

## Adım 1: Fikri Teslim Al

`$ARGUMENTS` doluysa onu fikir olarak kullan.

Boşsa kullanıcıya sor:
> "Hangi fikir/özellik için tasarım istiyorsun? Tek-iki cümlelik özet ver."

Fikri `<IDEA>` olarak sakla.

## Adım 1.5: Resume Kontrolü

Fikir alındıktan hemen sonra. Slug henüz yok → eşleştirme açık-statü taraması +
kullanıcı onayı ile. `docs/specs/` altında `status: draft` veya
`codex_review_status: pending` spec'leri tara:

- Açık spec(ler) varsa ve fikir biriyle örtüşüyorsa → başlıkları listele, sor:
  "Bu fikir bunlardan birinin devamı mı, yoksa yeni mi?" Devam → seçilen
  `<SPEC_PATH>` ile çalış, sayaçları frontmatter'dan oku.
- Kullanıcı `spec-approved` bir spec'i devam ettirmek isterse → reopen
  **atomiktir**: "Review'ı yeniden açmak status'u `spec-approved → draft` geri
  çevirir. Onaylıyor musun?" Onayda **aynı anda** `status: draft` +
  `codex_review_status: pending`. "approved + pending" ara durumu asla oluşmaz.
- Açık spec yok / "yeni" → yeni akış (Adım 2).
```

- [ ] **Step 2: Doğrula**

```bash
rg -n "^## Adım (0|1|1.5):" ~/.claude/commands/spec-claude-codex.md
```
Beklenen: Adım 0 (Active Context Read), Adım 1 (Fikri Teslim Al), Adım 1.5 (Resume) sırayla.

## Task 4: Adım 2 — Ön-Scoping (bash verbatim, prompt'a active task enjeksiyonu)

**Files:** Modify `~/.claude/commands/spec-claude-codex.md`

Kaynaktaki `## Adım 1: Ön-Scoping (Paralel İki Perspektif)` → `## Adım 2: Ön-Scoping`. **Bash bloğuna (companion find + `node ... task --fresh --wait`) DOKUNMA.** Yalnız başlığı değiştir ve prompt bloğuna active task özeti ekle.

- [ ] **Step 1: Başlığı değiştir**

old: `## Adım 1: Ön-Scoping (Paralel İki Perspektif)`
new: `## Adım 2: Ön-Scoping (Paralel İki Perspektif)`

- [ ] **Step 2: Prompt bloğuna active task özeti ekle (bash'e değil, prompt metnine)**

Kaynaktaki prompt bloğunda `IDEA: <IDEA>` satırından sonra, `Recent decisions from this Claude session` satırından ÖNCE şunu ekle:

```
Active task (context only, do not modify; Adım 0'da bulunduysa — yoksa bu blok hiç eklenmez):
- Task: <title> (<status>)
- Goal: <1 satır>
- Open Problems: <sayı> — <en kritik 1>
- Son kararlar: <Decisions Log'dan max 2 bullet>
```

- [ ] **Step 3: Bash bloğunun ZARAR GÖRMEDİĞİNİ doğrula (kritik anti-drift)**

```bash
rg -n "find ~/.claude/plugins/cache/openai-codex -name codex-companion.mjs|task --fresh --wait --cwd|positional" ~/.claude/commands/spec-claude-codex.md
```
Beklenen: companion find + `task --fresh --wait --cwd "$PROJECT_ROOT"` satırları kaynaktaki gibi durur.

## Task 5: Adım 3 — Kullanıcı Yön Seçer

**Files:** Modify `~/.claude/commands/spec-claude-codex.md`

Kaynakta yön seçimi eski Adım 1'in sonundaki "Çıktı sun + AskUserQuestion" bloğunda. Onu ayrı `## Adım 3: Kullanıcı Yön Seçer` başlığına taşı.

- [ ] **Step 1: "### Çıktı sun" bloğundan önce yeni başlık ekle**

Kaynaktaki `### Çıktı sun` satırının yerine:
```
## Adım 3: Kullanıcı Yön Seçer

### Çıktı sun
```

- [ ] **Step 2: Yön seçimi sonrası referansı güncelle**

old: `Diğer seçenekler → seçilen yönü `<SCOPE>` olarak sakla, Adım 2'ye geç.`
new: `Diğer seçenekler → seçilen yönü `<SCOPE>` olarak sakla, Adım 4'e geç.`
old: `"Hiçbiri" → Adım 0'a dön (yeni fikir cümlesi al).`
new: `"Hiçbiri" → Adım 1'e dön (yeni fikir cümlesi al).`

- [ ] **Step 3: Doğrula**

```bash
rg -n "^## Adım 3: Kullanıcı Yön Seçer|Adım 4'e geç" ~/.claude/commands/spec-claude-codex.md
```

## Task 6: Adım 4 — Brainstorm Draft + frontmatter lifecycle

**Files:** Modify `~/.claude/commands/spec-claude-codex.md`

Kaynaktaki `## Adım 2: /brainstorm Çağrısı (Skill tool)` → `## Adım 4`. Frontmatter standardını güncelle (title/status:draft/date/tags + codex_review_* + tarih önekli log path).

- [ ] **Step 1: Başlık**

old: `## Adım 2: /brainstorm Çağrısı (Skill tool)`
new: `## Adım 4: Brainstorm ile Spec Draft (Skill tool)`

- [ ] **Step 2: Frontmatter metadata bloğunu değiştir**

old:
```yaml
---
codex_review_status: pending
codex_review_iterations: 0
codex_review_log: docs/reviews/codex/<SLUG>.md
---
```
new:
```yaml
---
title: <başlık>
status: draft
date: YYYY-MM-DD
tags: [...]
codex_review_status: pending
codex_review_iterations: 0
codex_review_log: docs/reviews/codex/YYYY-MM-DD-<SLUG>.md
---
```

- [ ] **Step 3: Sayaç başlatma satırını güncelle**

old: `\`<TURN> = 1\``
new: `\`full_design_iteration_count = 0\`, \`targeted_consistency_fix_count = 0\` (frontmatter \`codex_review_iterations\` source-of-truth).`

- [ ] **Step 4: Doğrula**

```bash
rg -n "status: draft|full_design_iteration_count = 0|YYYY-MM-DD-<SLUG>.md" ~/.claude/commands/spec-claude-codex.md
```

## Task 7: Adım 5 (consistency sweep) ekle + Adım 6 (adversarial review, Bulgu 2 fix)

**Files:** Modify `~/.claude/commands/spec-claude-codex.md`

- [ ] **Step 1: Adım 4'ün sonuna yeni Adım 5 ekle (kaynaktaki "## Adım 3: Codex Adversarial Review" başlığından ÖNCE)**

`## Adım 3: Codex Adversarial Review` satırından önce şunu ekle:
```
## Adım 5: Consistency Sweep (Codex öncesi)

§ Consistency Checklist'i (aşağıda) çalıştır. Targeted fix uygulanır,
`targeted_consistency_fix_count` artar. Temel tasarım sorunu çıkarsa Adım 4'e
(brainstorm refine) dön, `full_design_iteration_count` artar.

```

- [ ] **Step 2: "## Adım 3: Codex Adversarial Review" başlığını Adım 6 yap**

old: `## Adım 3: Codex Adversarial Review`
new: `## Adım 6: Codex Adversarial Review`

- [ ] **Step 3: Scope handling'i Bulgu 2 fix'iyle değiştir (KASITLI mekanik değişikliği)**

Kaynaktaki `### Spec'in working-tree'de olduğunu doğrula` bloğunu değiştir:

old:
```
### Spec'in working-tree'de olduğunu doğrula

`git status --short <SPEC_PATH>` çalıştır:
- Çıktı boş değilse (uncommitted) → `--scope working-tree` uygun, devam
- Çıktı boşsa (commit'lenmiş) → uyarı düş, `--base HEAD~1` ile devam et
```
new:
```
### Review hedefini belirle (Bulgu 2 — miras bug düzeltmesi)

**Birincil hedef: `<SPEC_PATH>` içeriği doğrudan.** Tek-spec review'da
source-of-truth dosyanın kendisidir; prompt "Focus on <SPEC_PATH>" der, Codex
dosyayı read-only sandbox'ta okur (git diff'e bağımlı değil).

`git status --short <SPEC_PATH>`:
- uncommitted → `--scope working-tree`
- commit'li + working-tree temiz → kullanıcıdan **açık base/ref** iste (spec
  commit hash'i); **implicit base fallback (önceki-commit varsayımı)
  KULLANILMAZ.** Kullanıcı ref vermezse dosya içeriği doğrudan (diff'siz)
  review edilir.
```

- [ ] **Step 4: adversarial-review çağrısını koşullu scope ile yeniden tanımla (Bulgu 2 — KASITLI değişiklik, verbatim DEĞİL)**

Kaynaktaki hardcoded `--scope working-tree` içeren çağrı **korunmaz**; scope, Step 3 kararına göre çağrı anında kurulur. Çağrıyı şununla değiştir:

```bash
# Step 3 kararına göre SCOPE:
if [ -n "$(git status --short <SPEC_PATH>)" ]; then
  SCOPE="--scope working-tree"                       # uncommitted
else
  SCOPE="${USER_BASE_REF:+--base $USER_BASE_REF}"    # clean: base ref varsa onu; yoksa scope flag'siz
fi
node "$COMPANION" adversarial-review \
  "$SCOPE --wait challenge this spec's design choices, hidden assumptions, and dependencies. Read and assess the CURRENT content of <SPEC_PATH> directly (do not rely solely on a git diff). List failure scenarios. Categorize findings critical | high | medium | low. Focus on <SPEC_PATH>."
```

Anahtar: (a) clean spec'te `--scope working-tree` **kullanılmaz**, (b) prompt "read CURRENT content directly" davranışını zorunlu kılar, (c) base/ref varsa açıkça `--base <ref>`, **implicit base fallback asla** (yeni komut dosyasına bu yasak literal yazılmaz — paraphrase).

- [ ] **Step 5: Doğrula — koşullu scope + anti-drift ayrımı**

```bash
rg -c "Read and assess the CURRENT content" ~/.claude/commands/spec-claude-codex.md   # >=1
rg -c "HEAD~1" ~/.claude/commands/spec-claude-codex.md || echo "0 ✓"                  # 0 beklenir
rg -n 'task --fresh --wait --cwd "\$PROJECT_ROOT"' ~/.claude/commands/spec-claude-codex.md
```
Beklenen: "read CURRENT content directly" >=1; **`HEAD~1` 0 ✓** (yeni komutta yasak literal yok); Adım 2 `task` çağrısı verbatim duruyor (anti-drift yalnız buraya).

- [ ] **Step 6: Log path'i tarih önekli yap**

old (Adım 6 içinde): `Aynı çıktıyı `docs/reviews/codex/<SLUG>.md` dosyasına append et:`
new: `Aynı çıktıyı `docs/reviews/codex/YYYY-MM-DD-<SLUG>.md` dosyasına append et:`
old: `Klasör yoksa: `mkdir -p docs/reviews/codex``  (değişmez — anchor doğrula)

## Task 8: Adım 7 (Karar, full_design_iteration) + Adım 8-12

**Files:** Modify `~/.claude/commands/spec-claude-codex.md`

- [ ] **Step 1: "## Adım 4: Karar" → "## Adım 7: Karar"**

old: `## Adım 4: Karar`
new: `## Adım 7: Karar — Onayla / Güncelle`

- [ ] **Step 2: Sayaç koşullarını full_design_iteration modeline çevir (>= 3)**

old:
```
**`<TURN> < 3` ise** (`AskUserQuestion` ile iki seçenek):
- **Onayla** — Bulguları gördüm, kabul ediyorum, spec final
- **Spec'i güncelle** — Bulgular spec'e işlenmeli (→ /brainstorm refine)

**`<TURN> == 3` ise** (limit dolu, sadece bir seçenek sun — kullanıcı
bilinçli kapatsın):
- **Onayla** — Limit doldu, spec final (status `approved-by-iteration-limit`)
```
new:
```
**`full_design_iteration_count < 3` ise** (iki seçenek):
- **Onayla** → Adım 9 (final sweep)
- **Spec'i güncelle** → critical/high özetlenir, kullanıcı ek girdi, brainstorm
  refine (Adım 4), Adım 6'ya dön. Değişiklik temel tasarıma dokunuyorsa
  `full_design_iteration_count` artar; sadece path/wording/frontmatter ise
  `targeted_consistency_fix_count` artar (conservative: ikisine de dokunan →
  full_design_iteration).

**`full_design_iteration_count >= 3` ise** (limit dolu — `==` değil `>=`:
resume'da elle değişmiş sayaç 3'ü aşmış olabilir):
- **Onayla** → `codex_review_status: approved-by-iteration-limit`
- **Kabul etmem** → unresolved kararlar listelenir + yeni scoped
  /spec-claude-codex önerilir.
```

- [ ] **Step 3: Eski "Onayla/Güncelle" alt bölümlerini KALDIR (koru DEĞİL), Adım 8-12'yi tek lifecycle olarak yaz**

Kaynaktaki `### "Onayla" seçilirse` ve `### "Spec'i güncelle" seçilirse` alt bölümleri **tamamen kaldırılır** — içlerindeki `<TURN>`, eski finalizasyon (yalnız `codex_review_status`), "komut biter", "Adım 3'e dön" gibi miras davranışlar yeni modelle çelişir; aynı dosyada iki lifecycle bırakmak Bulgu 2'nin (Codex review) ta kendisidir. Karar mantığı zaten Step 2'de (Adım 7), finalizasyon Adım 10'da, güncelle döngüsü Adım 4/6 referansıyla tanımlı. Bu eski bölümlerin yerine, `## Sözleşme Notları`'ndan ÖNCE şu Adım 8-12 yazılır:

```
## Adım 8: Sayaç (Adım 5/7'ye gömülü)

Sayaç ayrı adım değil; Adım 5 ve 7'de işletilir. Kaynak-of-truth frontmatter
`codex_review_iterations` (full design iteration). Targeted fix sayısı raporda
ayrı gösterilir, frontmatter'a yazılmaz.

## Adım 9: Final Consistency Sweep

§ Consistency Checklist'i tekrar çalıştır (onay öncesi zorunlu). Küçük
düzeltmeler `targeted_consistency_fix_count`'a yazılır. **Yeni temel karar
açılırsa** spec approve edilmez — Adım 7'ye dön.

## Adım 10: Finalizasyon

Frontmatter: `status: spec-approved`, `codex_review_status: approved` (veya
limit ile `approved-by-iteration-limit`), `codex_review_iterations:
<full_design_iteration_count>`, `codex_review_log: ...`.

## Adım 11: Active Task Hatırlatması

Adım 0'da ilgili active task bulunduysa: *"Spec final kararlarını TASK.md
Decisions Log / Open Problems'a işleyelim mi?"* **Vault promotion bu komutta
YAPILMAZ** — /commit veya closure P1'e bırakılır. Yeni active task yaratılmaz
(/write-plan'a ait).

## Adım 12: Final Rapor

\`\`\`
Spec final.
- Path: docs/specs/YYYY-MM-DD-<slug>.md
- Codex review log: docs/reviews/codex/YYYY-MM-DD-<slug>.md
- Full design iterations: N/3
- Targeted consistency fixes: M
- Status: spec-approved
- Codex review status: approved | approved-by-iteration-limit
- Sonraki adım: /write-plan docs/specs/YYYY-MM-DD-<slug>.md
\`\`\`
```

- [ ] **Step 4: Doğrula**

```bash
rg -n "^## Adım (7|8|9|10|11|12):" ~/.claude/commands/spec-claude-codex.md
```

## Task 9: Consistency Checklist bölümü + Sözleşme Notları + self-reference temizliği

**Files:** Modify `~/.claude/commands/spec-claude-codex.md`

- [ ] **Step 1: Dosyanın sonuna (Sözleşme Notları'ndan önce) Consistency Checklist bölümü ekle**

```
## Consistency Checklist (tek liste, iki kullanım: Adım 5 + Adım 9)

**Genel (her zaman):**
- Summary/decisions/schema/lifecycle/implementation notes aynı kararları mı söylüyor?
- Path/komut/flag/dosya adları birebir doğru mu? (referans bütünlüğü)
- Repo/vault/global ayrımı doğru mu?
- Kullanıcı onayı gereken yerde otomatik işlem var mı?
- Out-of-scope, kararlarla çelişiyor mu?
- (status, codex_review_status) çifti izinli mi? İzinli: `draft+pending`,
  `spec-approved+approved`, `spec-approved+approved-by-iteration-limit`.
  Yasak: `spec-approved+pending`.

**Koşullu (konu workflow/active-layer/agent-rol/vault ise — şüphede çalıştır):**
- Codex read-only kuralı korunuyor mu?
- Active state vault'a konmuyor mu?
- TASK.md/HANDOFF.md canonical ayrımı karışıyor mu?
- CURRENT.md sadece pointer/memo mu (status değil)?
```

- [ ] **Step 2: "## Sözleşme Notları" içinde kalan iç referansları güncelle**

old: `- Adım 1b → \`Bash(node companion task --fresh --wait ...)\``
new: `- Adım 2 → \`Bash(node companion task --fresh --wait ...)\``
old: `- Adım 3 → \`Bash(node companion adversarial-review ...)\``
new: `- Adım 6 → \`Bash(node companion adversarial-review ...)\``

Ayrıca "Path konvensiyonu" notunu güncelle:
old: `**Path konvensiyonu:** CLAUDE.md global kural — \`docs/specs/\`, \`docs/reviews/codex/\`.`
new: `**Path konvensiyonu:** CLAUDE.md global kural — \`docs/specs/YYYY-MM-DD-<slug>.md\`, \`docs/reviews/codex/YYYY-MM-DD-<slug>.md\` (tarih önekli).`

- [ ] **Step 3: Son self-reference temizliği — KRİTİK**

```bash
rg -n "plan-claude-codex" ~/.claude/commands/spec-claude-codex.md
```
Çıkan her satırdaki `/plan-claude-codex` → `/spec-claude-codex` (Adım 1b kaynak notundaki "mevcut /plan-claude-codex pattern'iyle uyumlu" gibi anmalar dahil). Tekrar çalıştır, **0 sonuç** kalmalı:
```bash
rg -c "plan-claude-codex" ~/.claude/commands/spec-claude-codex.md || echo "0 ✓ (self-ref temiz)"
```

- [ ] **Step 4: Bütünsel doğrulama**

```bash
rg -n "^## Adım (0|1|1.5|2|3|4|5|6|7|8|9|10|11|12):" ~/.claude/commands/spec-claude-codex.md   # 14 başlık sırayla
rg -n 'task --fresh --wait --cwd|adversarial-review' ~/.claude/commands/spec-claude-codex.md   # bash mekanik intact
```
Beklenen: 14 adım başlığı sırayla; iki Codex bash mekaniği duruyor.

---

# PHASE B — Eski Komutu Stub Yap

> **SIRA KRİTİK:** Faz A tamamlanmadan bu task çalıştırılamaz (içerik kaybı).

## Task 10: plan-claude-codex.md'yi deprecated stub'a çevir

**Files:** Modify `~/.claude/commands/plan-claude-codex.md` (içerik tamamen değişir)

- [ ] **Step 1: Önce spec-claude-codex.md'nin var ve dolu olduğunu doğrula**

```bash
test -s ~/.claude/commands/spec-claude-codex.md && wc -l ~/.claude/commands/spec-claude-codex.md && echo "yeni dosya hazır ✓"
```

- [ ] **Step 2: Stub içeriğini yaz (Write ile tüm dosyayı değiştir)**

```markdown
---
description: "[DEPRECATED] use /spec-claude-codex"
argument-hint: <fikir cümlesi>
---

## Deprecated

Bu komut `spec-claude-codex` olarak yeniden adlandırıldı.

Yeni kullanım:
`/spec-claude-codex <fikir>`

Bu komut spec/tasarım dokümanı üretir, implementation planı **değil**.
Spec final olduktan sonra: `/write-plan <SPEC_PATH>`

(Eski ad referans bütünlüğü için stub korunuyor — vault `sources:` ve
2026-05-19 tarihli dokümanlar buraya işaret ediyor. Silme.)
```

- [ ] **Step 3: Doğrula**

```bash
rg -n "DEPRECATED|spec-claude-codex" ~/.claude/commands/plan-claude-codex.md
wc -l ~/.claude/commands/plan-claude-codex.md   # ~16
```
Beklenen: stub içeriği, eski akış yok.

---

# PHASE C — Canlı Referans Güncelleme

## Task 11: handoff.md (2 referans)

**Files:** Modify `~/.claude/commands/handoff.md`

- [ ] **Step 1: Satır 41 referansı**

old: `1. Codex companion path'ini dinamik bul ve çağır (`/plan-claude-codex`'in pattern'i):`
new: `1. Codex companion path'ini dinamik bul ve çağır (`/spec-claude-codex`'in pattern'i):`

- [ ] **Step 2: Satır 58 referansı**

old: `mevcut `/plan-claude-codex` pattern'iyle uyumlu.`
new: `mevcut `/spec-claude-codex` pattern'iyle uyumlu.`

- [ ] **Step 3: Doğrula**

```bash
rg -c "plan-claude-codex" ~/.claude/commands/handoff.md || echo "0 ✓"
```

## Task 12: sync-agents-md.md (1 referans)

**Files:** Modify `~/.claude/commands/sync-agents-md.md`

- [ ] **Step 1: Satır 170**

old: `> Codex bir sonraki çağrıda (örn. /plan-claude-codex) damıtılmış`
new: `> Codex bir sonraki çağrıda (örn. /spec-claude-codex) damıtılmış`

- [ ] **Step 2: Doğrula**

```bash
rg -c "plan-claude-codex" ~/.claude/commands/sync-agents-md.md || echo "0 ✓"
```

## Task 13: init.md (2 referans)

**Files:** Modify `~/.claude/commands/init.md`

- [ ] **Step 1: Satır 120**

old: `çağrıda (örn. /plan-claude-codex) bu projeyi tanır.`
new: `çağrıda (örn. /spec-claude-codex) bu projeyi tanır.`

- [ ] **Step 2: Satır 135**

old: `> /plan-claude-codex (Claude+Codex çift perspektif), veya doğrudan kod."`
new: `> /spec-claude-codex (Claude+Codex çift perspektif), veya doğrudan kod."`

- [ ] **Step 3: Doğrula**

```bash
rg -c "plan-claude-codex" ~/.claude/commands/init.md || echo "0 ✓"
```

---

# PHASE D — Repo Doğrulama

## Task 14: rg sweep — yalnız kasıtlı referanslar kalmalı

**Files:** yok (doğrulama)

- [ ] **Step 1: Global komut dizininde sweep**

```bash
rg -n "plan-claude-codex" ~/.claude/commands/
```
Beklenen: **yalnız** `plan-claude-codex.md` stub gövdesindeki kendi adı (frontmatter description + stub metni). Başka canlı komutta 0.

- [ ] **Step 2: Repo'da sweep**

```bash
rg -n "plan-claude-codex" /root/otomaix/docs/
```
Beklenen: yalnız donmuş tarihi docs (`specs/2026-05-19-*`, `plans/2026-05-19-*`) + bu spec/plan'ın kendi blast-radius tabloları. **Bunlara dokunulmaz.**

- [ ] **Step 3: Yeni komutta self-ref olmadığını teyit**

```bash
rg -c "plan-claude-codex" ~/.claude/commands/spec-claude-codex.md || echo "0 ✓"
```

---

# PHASE E — Vault (ROLLOUT GATE)

> **Codex notu:** Bu faz vault yazımı içerir. Codex uyguluyorsa: dosyayı
> değiştirme, patch'i stdout'a öner — Claude/kullanıcı yazar, commit/push eder.
>
> **Rollout gate (spec §7):** Bu faz bitip doğrulanmadan rename "canonical
> rollout tamamlandı" sayılmaz. CLAUDE.md "bilgi sorgusu önce vault" der; vault
> eski adı canonical gösterdiği sürece rollout partial'dır.

## Task 15: codex-entegrasyonu.md — sources + inline

**Files:** Modify `/root/otomaix-brain/cross-project/infrastructure/codex-entegrasyonu.md`

**Uygulayıcı:** Claude veya kullanıcı (Codex patch önerir, yazmaz).

- [ ] **Step 1: `sources:` frontmatter pointer'ı yeni dosyaya çevir**

old: `  - "@/root/.claude/commands/plan-claude-codex.md"`
new: `  - "@/root/.claude/commands/spec-claude-codex.md"`

(Stub canonical source değil — spec §6 kararı.)

- [ ] **Step 2: Satır ~95 inline anmasını güncelle**

old: `   (örn. `/plan-claude-codex`, gelecekte Codex'e geçen `/review`) →`
new: `   (örn. `/spec-claude-codex`, gelecekte Codex'e geçen `/review`) →`

- [ ] **Step 3: `last-verified` bump**

old: `last-verified: 2026-05-19`
new: `last-verified: 2026-05-20`

- [ ] **Step 4: Doğrula**

```bash
rg -n "spec-claude-codex|last-verified" /root/otomaix-brain/cross-project/infrastructure/codex-entegrasyonu.md
```

## Task 16: decisions/2026-05-19 workflow satırı + vault commit

**Files:** Modify `/root/otomaix-brain/decisions/2026-05-19-claude-codex-aktif-task-layer.md`

- [ ] **Step 1: Satır ~64 workflow satırı**

old: `1. `/plan-claude-codex <fikir>` veya `/brainstorm <konu>` ile spec çıkar`
new: `1. `/spec-claude-codex <fikir>` veya `/brainstorm <konu>` ile spec çıkar`

(Not: `log.md` tarihsel kayıt — **dokunulmaz**.)

- [ ] **Step 2: Vault commit (kullanıcı onayıyla)**

```bash
cd /root/otomaix-brain
git add cross-project/infrastructure/codex-entegrasyonu.md decisions/2026-05-19-claude-codex-aktif-task-layer.md
git commit -m "docs(codex): rename plan-claude-codex -> spec-claude-codex in canonical refs"
```
> Kullanıcıya sor: *"Vault commit edildi. Push edelim mi? (`git push origin main`)"*

- [ ] **Step 3: Vault sweep**

```bash
rg -n "plan-claude-codex" /root/otomaix-brain/
```
Beklenen: yalnız `log.md` (tarihsel, kasıtlı bırakıldı). Başka 0.

---

# PHASE F — Closure

## Task 17: Rollout gate doğrulama

**Files:** yok (doğrulama)

- [ ] **Step 1: Definition of Done kontrol listesi**

```bash
echo "1) Yeni komut:"; test -s ~/.claude/commands/spec-claude-codex.md && echo "  ✓ var"
echo "2) Stub:"; rg -q DEPRECATED ~/.claude/commands/plan-claude-codex.md && echo "  ✓ stub"
echo "3) Canlı ref temiz:"; rg -L "plan-claude-codex" ~/.claude/commands/{handoff,sync-agents-md,init}.md >/dev/null 2>&1 && echo "  ✓"
echo "4) Vault canonical güncel:"; rg -q "spec-claude-codex" /root/otomaix-brain/cross-project/infrastructure/codex-entegrasyonu.md && echo "  ✓"
```

- [ ] **Step 2: Davranış spot-check**

`/spec-claude-codex <dummy fikir>` çağrısının Adım 0'da CURRENT.md'yi okuduğunu, `/plan-claude-codex` çağrısının stub yönlendirmesi gösterdiğini elle doğrula.

- [ ] **Step 3: Rollout = done**

Faz A-E hepsi ✓ ise rename canonical-tamamlandı. Vault eksikse (Faz E yapılmadıysa) rollout **partial** — done deme.

---

## Self-Review Notları

**Spec coverage:** spec §3 (korunan mekanik + Bulgu 2 istisna) → Task 1/4/7; §4 (12 adım) → Task 2-8; §5 (checklist + state pairs) → Task 7/9; §6 (stub) → Task 10; §7 (blast-radius + uygulama sırası + rollout gate) → Task 11-17; §8 (out-of-scope) → vault ayrı faz, tarihi docs dokunulmaz. Hepsi karşılandı.

**Placeholder scan:** `<IDEA>`, `<SPEC_PATH>`, `<slug>`, `<title>`, `N/3`, `M` — komut şablon placeholder'ları (kasıtlı, komutun kendi davranışı). Plan adımlarında TBD/TODO yok.

**Anti-drift:** Codex bash blokları (companion `task`, `adversarial-review`) `cp` ile verbatim gelir; edit'ler yalnız self-ref + Bulgu 2 scope prose'unu değiştirir. Task 4/7 doğrulama adımları bash tokenlarının intact kaldığını `rg` ile kanıtlar.

**Type/isim tutarlılığı:** `full_design_iteration_count` / `targeted_consistency_fix_count` / `codex_review_iterations` tüm task'larda aynı; adım numaraları (0,1,1.5,2-12) tutarlı; izinli state pair listesi spec §5.2 ile birebir.

**TDD esnetmesi:** Markdown/slash-command/config; kod birimi yok. "Test" = her task'ın `rg`/davranış doğrulaması.

**Commit sınırları:** Faz A-D global dosyalar → git commit yok. Faz E vault → vault git commit + push (onayla). Repo'da tek commit: bu plan dosyası (Adım 5).

---

## İlgili Dosyalar

- **Spec:** `docs/specs/2026-05-20-spec-claude-codex-command.md`
- **Codex review log:** `docs/reviews/codex/2026-05-20-spec-claude-codex-command.md`
- **Kaynak mekanik:** `~/.claude/commands/plan-claude-codex.md` (rename öncesi)
- **Aktif task layer:** `docs/specs/2026-05-19-claude-codex-aktif-katman.md`
