# Claude–Codex Aktif Task Layer — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Workflow override:** Otomaix `/root/otomaix/CLAUDE.md` "Skill Chain Override Notları" gereği `executing-plans` skill'inin auto-chain'leri (`finishing-a-development-branch`, `using-git-worktrees`) **bilinçli olarak çağrılmayacak.** Bu plan kendi içinde yeterli.

**Goal:** Spec'te (`docs/specs/2026-05-19-claude-codex-aktif-katman.md`) kararlaştırılan Claude–Codex Aktif Task Layer'ı repo'ya kurmak — klasör iskeleti, schema template'leri, yeni `/handoff` slash command, mevcut 5 slash command'in hatırlatma entegrasyonu, root CLAUDE.md güncellemesi, AGENTS.md damıtması, vault doc çapraz referansı ve end-to-end smoke test.

**Architecture:** Repo'ya overlay. **Active state vault'a konmaz; vault sadece kullanıcı onaylı promotion (P1) veya çapraz referans güncellemesiyle değişir** (Phase G ve closure'daki vault yazımları bu kapsama girer). `docs/active/<slug>/{TASK,HANDOFF}.md` canlı state, `docs/task-archive/YYYY/MM/<slug>/` kapalı geçmiş. Manuel mod — slash command'ler **task aware ama task driven değil**, hatırlatma soruları (y/n) ile çalışır.

**Tech Stack:** Markdown, shell (`/sync-agents-md` Codex CLI), git. Kod yok.

**Spec referansı:** [`docs/specs/2026-05-19-claude-codex-aktif-katman.md`](../specs/2026-05-19-claude-codex-aktif-katman.md)

---

## Preflight — İlk Task'tan Önce Çalıştır

Plan uygulamaya başlamadan ÖNCE:

```bash
git -C /root/otomaix status --short
git -C /root/otomaix-brain status --short
```

- Repo veya vault'ta **unrelated dirty file** varsa (bu plan'a ait olmayan değişiklikler), kullanıcıya sor: *"Bu dosyalar plan'la ilgisiz, ayrı commit edilmeli mi yoksa stash mi?"* — net karar alınmadan plan task'larını commit etmeye başlama.
- Bu plan'ın yarattığı yeni dosyalar (örn. `docs/active/CURRENT.md`, `templates/...`) ayrı, izole commit'lerle gider.
- Vault dirty ise: vault commit/push işleri Phase G'ye kadar ertelenir; vault disiplini bozulmamalı.

## Tool Policy — Codex ve Claude Farklılığı

**Bu plan iki ajan tarafından uygulanabilir:**

- **Claude Code (default):** HEREDOC blokları doğrudan `cat > file <<'EOF' ... EOF` ile uygulanabilir; ya da Write/Edit tool ile.
- **Codex CLI:** Codex shell-based dosya yazımını kullanmaz; her dosya değişikliği `apply_patch` ile yapılır. Bu plandaki **HEREDOC blokları "yazılacak içerik"in referansıdır** — Codex bu içeriği `apply_patch` formatına çevirerek uygulamalı.

**Memory ve vault yazımları için kritik kural:**

- Codex **memory'ye yazmaz** (`~/.claude/projects/-root-otomaix/memory/`). Phase I'daki memory adımları Codex tarafından uygulanırsa: dosyaları yaratma/değiştirme yerine **stdout olarak öneri çıkarır** — Claude veya kullanıcı manuel uygular.
- Codex **vault'a yazmaz** (`/root/otomaix-brain/`). Phase G ve Phase H'deki vault adımları Codex tarafından uygulanırsa: önerilen değişikliği stdout'a basar, Claude veya kullanıcı vault'a yazar.

Bu kurallar `[[codex-entegrasyonu]]` (vault) ve `/root/otomaix-brain/AGENTS.md` "Kapsam Dışı" bölümüyle uyumludur.

---

## Implementation Progress

| Phase | Tasks | Durum |
|---|---|---|
| **A — Skeleton** | 1 | ⬜ |
| **B — Templates** | 2 | ⬜ |
| **C — /handoff komutu** | 3 | ⬜ |
| **D — Mevcut command entegrasyonu** | 4–8 (5 ayrı edit) | ⬜ |
| **E — Root CLAUDE.md** | 9 | ⬜ |
| **F — AGENTS.md sync** | 10 | ⬜ |
| **G — Vault çapraz referans** | 11 | ⬜ |
| **H — End-to-end smoke test** | 12 | ⬜ |
| **I — Memory + closure** | 13 | ⬜ |

---

## File Structure (oluşturulacak / değiştirilecek)

### Yeni dosyalar
```
/root/otomaix/docs/active/CURRENT.md                  # boş template
/root/otomaix/docs/task-archive/.gitkeep              # boş dir commit için
/root/otomaix/templates/TASK.md.template              # task şablonu
/root/otomaix/templates/HANDOFF.md.template           # handoff şablonu
~/.claude/commands/handoff.md                         # yeni slash command
```

### Düzenlenecek dosyalar
```
/root/otomaix/CLAUDE.md                               # active task layer bölümü + protokol
/root/otomaix/AGENTS.md                               # /sync-agents-md project çıktısı
~/.claude/commands/write-plan.md                      # Adım 5 sonu hatırlatma
~/.claude/commands/execute-plan.md                    # başlangıç hatırlatması
~/.claude/commands/commit.md                          # TASK update + vault promotion check
~/.claude/commands/review.md                          # high/critical → Open Problems hatırlatması
~/.claude/commands/finish-branch.md                   # conditional matrix (PR/merge/sil/tut)
/root/otomaix-brain/cross-project/infrastructure/codex-entegrasyonu.md  # vault doc referansı
```

### Dokunulmayan
```
/root/otomaix-brain/AGENTS.md                         # vault scope, repo workflow oraya gömülmez
/root/otomaix-brain/CLAUDE.md                         # vault schema, değişmez
~/.claude/CLAUDE.md                                   # global, bu spec Otomaix repo'suna özgü
~/.codex/AGENTS.md                                    # global
~/.claude/commands/{brainstorm,debug,simplify,security-review,init,council,plan-claude-codex,sync-agents-md,worktree}.md  # task layer'a dokunmaz
```

---

# PHASE A — Skeleton

## Task 1: Active layer ve archive klasörlerini oluştur

**Files:**
- Create: `docs/active/CURRENT.md`
- Create: `docs/task-archive/.gitkeep`

- [ ] **Step 1: CURRENT.md yaz**

```markdown
# Active Tasks

_(no active tasks)_
```

```bash
mkdir -p /root/otomaix/docs/active
cat > /root/otomaix/docs/active/CURRENT.md <<'EOF'
# Active Tasks

_(no active tasks)_
EOF
```

- [ ] **Step 2: task-archive/.gitkeep yarat**

```bash
mkdir -p /root/otomaix/docs/task-archive
touch /root/otomaix/docs/task-archive/.gitkeep
```

- [ ] **Step 3: Doğrulama**

```bash
ls -la /root/otomaix/docs/active/ /root/otomaix/docs/task-archive/
cat /root/otomaix/docs/active/CURRENT.md
```

Beklenen: `CURRENT.md` görünür (3 satır), `task-archive/.gitkeep` boş dosya olarak görünür.

- [ ] **Step 4: Commit**

```bash
cd /root/otomaix
git add docs/active/CURRENT.md docs/task-archive/.gitkeep
git commit -m "feat: scaffold active task layer directories"
```

---

# PHASE B — Templates

## Task 2: TASK.md ve HANDOFF.md template'lerini yaz

**Files:**
- Create: `templates/TASK.md.template`
- Create: `templates/HANDOFF.md.template`

- [ ] **Step 1: TASK.md.template yaz**

```bash
mkdir -p /root/otomaix/templates
cat > /root/otomaix/templates/TASK.md.template <<'EOF'
---
title: <task adı>
status: proposed     # proposed | active | blocked | waiting-review | done | archived | cancelled
started: YYYY-MM-DD
last-touched: YYYY-MM-DD
blocked-by: null
---

# Goal

<1-3 cümle: ne yapılacak + neden + başarı kriteri. Constraint'ler burada eritilir.>

# References

- Spec: `docs/specs/YYYY-MM-DD-<slug>.md`
- Plan: `docs/plans/YYYY-MM-DD-<slug>.md`
- Review: _(yok)_

# Current Status

_(başlangıçta: "Plan onaylandı, henüz başlanmadı")_

# Open Problems

_(yok)_

# Decisions Log

_(boş — kararlar geldikçe eklenecek; promote edilenler `→ Vault: [[decisions/...]]` formatıyla)_
EOF
```

- [ ] **Step 2: HANDOFF.md.template yaz**

```bash
cat > /root/otomaix/templates/HANDOFF.md.template <<'EOF'
# Handoff

## Context
- Task:
- Linked spec:
- Linked plan:
- Branch:
- Last updated:

## Current State
- Summary:
- Blocked:

## Resume From
- Start here:
- Relevant files:
- Next command:

## Verification
- Passed:
- Failed:
- Not run:

## Risks
-

## Notes For Claude
- Codex'in özellikle dikkat çektiği bulgular:
- Claude'un sonraki session'da işlemesi gereken şeyler:
- Vault'a yazılması gerekebilecek kalıcı kararlar:
- Spec/plan güncellemesi gerektiren noktalar:
- Kullanıcıdan karar bekleyen konular:

## Notes For Codex
- Codex'in review ederken özellikle bakması gereken alanlar:
- Bilinen riskler:
- Dokunmaması gereken alanlar:
- Önce okunması gereken dosyalar:
EOF
```

- [ ] **Step 3: Doğrulama**

```bash
ls /root/otomaix/templates/
wc -l /root/otomaix/templates/*.template
```

Beklenen: 2 dosya — `TASK.md.template` (~22 satır), `HANDOFF.md.template` (~30 satır).

- [ ] **Step 4: Commit**

```bash
cd /root/otomaix
git add templates/TASK.md.template templates/HANDOFF.md.template
git commit -m "feat: add TASK and HANDOFF templates"
```

---

# PHASE C — /handoff Slash Command

## Task 3: Yeni `/handoff` komutunu yaz

**Files:**
- Create: `~/.claude/commands/handoff.md`

Davranış: default Claude tek başına HANDOFF.md yazar; `--with-codex` flag'i Codex'i read-only review için çağırır.

- [ ] **Step 1: handoff.md yaz**

```bash
cat > ~/.claude/commands/handoff.md <<'EOF'
## Görev

Aktif task için HANDOFF.md'yi günceller (session boundary devir teslim).

İki mod:
- **Default:** Claude tek başına HANDOFF.md'yi rolling olarak günceller
- **--with-codex:** Codex'i read-only review için çağırır, bulguları HANDOFF.md "Notes For Claude" bölümüne işler

## Adım 1: Aktif Task'ı Bul

`docs/active/CURRENT.md` oku:

- Listede tek task varsa otomatik seç
- Birden fazlaysa kullanıcıya sor: *"Hangi task için handoff yazıyoruz?"* (numbered list)
- Liste boş (`_(no active tasks)_`) ise: *"Aktif task yok. Önce /write-plan ile task yarat veya doğrudan elle TASK.md oluştur."* — dur

## Adım 2: Mevcut TASK.md + HANDOFF.md Oku

`docs/active/<slug>/TASK.md` ve `docs/active/<slug>/HANDOFF.md` oku. Mevcut state'i anla:
- TASK.md `status`, `Current Status`, `Open Problems`, `Decisions Log` ne durumda
- HANDOFF.md son güncelleme ne zaman, hangi bölümler dolu/boş

## Adım 3a (Default): Claude Tek Başına Yazar

HANDOFF.md'yi tamamen yeniden yaz (rolling overwrite). Bölümler:

- **Context** — Task adı, spec/plan linkleri, branch (`git branch --show-current`), `Last updated: $(date '+%Y-%m-%d %H:%M')`
- **Current State** — Summary: tek paragrafta nereden devam edileceği; Blocked: evet/hayır + tek satır
- **Resume From** — Start here (dosya/fonksiyon/komut); Relevant files (liste); Next command (önerilen sıradaki slash command)
- **Verification** — Passed / Failed / Not run (yapılanlar + kalanlar)
- **Risks** — bu session'da farkına vardığın kalıcı olmayan riskler (kalıcı risk → TASK.md Decisions Log)
- **Notes For Claude** — sonraki Claude session'ı için işlenecek şeyler
- **Notes For Codex** — Codex review için pointer'lar (dokunmaması gereken alanlar, bilinen riskler, önce okunacak dosyalar)

Boş bölüm varsa `_(yok)_` yaz, atlama.

## Adım 3b (--with-codex): Codex Review Çağrısı

Argümanlarda `--with-codex` varsa:

1. Codex companion path'ini dinamik bul ve çağır (`/plan-claude-codex`'in pattern'i):
   ```bash
   COMPANION=$(find ~/.claude/plugins/cache/openai-codex -name codex-companion.mjs -type f 2>/dev/null | head -1)
   if [ -z "$COMPANION" ]; then
     COMPANION=$(find ~/.claude -name codex-companion.mjs -type f 2>/dev/null | head -1)
   fi
   [ -z "$COMPANION" ] && { echo "codex-companion.mjs bulunamadı — Codex CLI plugin yüklü değil"; exit 1; }

   node "$COMPANION" task --fresh --wait --cwd /root/otomaix \
     "Read docs/active/<slug>/TASK.md and HANDOFF.md. Provide a read-only review focused on:
     - Eksik veya çelişkili kararlar
     - Açık problemlerin doğruluğu
     - Vault'a promote edilmesi gerekebilecek kararlar
     - Sonraki session için dikkat edilmesi gerekenler
     Output as structured findings (numbered list, severity tag)."
   ```

   **Not:** Prompt **positional argüman** olarak verilir (`--prompt` flag'i değil) — mevcut `/plan-claude-codex` pattern'iyle uyumlu.
2. Codex stdout'unu **kullanıcıya göster** — onaylı bulguları al
3. Onaylı bulguları HANDOFF.md "Notes For Claude → Codex'in özellikle dikkat çektiği bulgular" satırına ekle
4. Sonra Adım 3a'daki gibi diğer bölümleri tamamla

## Adım 4: Commit Onayı

```
HANDOFF.md güncellendi: docs/active/<slug>/HANDOFF.md
Commit edelim mi? Mesaj: `docs(handoff): update <slug> handoff`
```

Onay gelirse: Conventional Commits, push YAPMA.

## Notlar

- Bu komut `status` ve **TASK.md'ye dokunmaz** — sadece HANDOFF.md güncellenir. Bu spec §5.2 transition tablosuyla uyumludur (`session end | /handoff | TASK: dokunmaz | HANDOFF: full güncelleme`). TASK.md `last-touched` güncellemesi `/commit` veya `/execute-plan` gibi TASK.md'yi düzenleyen akışlarda yapılır.
- Status değişimi (`blocked`, `waiting-review`) manuel TASK.md edit ile yapılır, /handoff'la değil.
- `/finish-branch` ile karıştırma — /handoff session boundary, /finish-branch task closure/branch lifecycle.
- Otomatik Codex çağrısı YOK — opt-in (`--with-codex`).

ARGUMENTS: $ARGUMENTS
EOF
```

- [ ] **Step 2: Doğrulama**

```bash
ls ~/.claude/commands/handoff.md && wc -l ~/.claude/commands/handoff.md
```

Beklenen: dosya var, ~75 satır.

- [ ] **Step 3: Commit yok bu adımda**

Slash command'ler `~/.claude/commands/` altında — bu Otomaix repo'su dışında, global. Otomaix git'inden bağımsız. Commit gerekmez.

---

# PHASE D — Mevcut Slash Command Entegrasyonu

Bu phase'de 5 mevcut komut edit edilir. Her edit ayrı task, her birinde minimal hatırlatma adımı eklenir. **Tüm hatırlatmalar conditional** — `docs/active/CURRENT.md` boşsa ("_(no active tasks)_") atlanır.

## Task 4: `/write-plan` — TASK.md + HANDOFF.md yaratma hatırlatması

**Files:**
- Modify: `~/.claude/commands/write-plan.md` (Adım 5 sonu)

- [ ] **Step 1: Mevcut write-plan.md'yi oku, Adım 5/6 sınırını bul**

```bash
grep -n "## Adım" ~/.claude/commands/write-plan.md
```

- [ ] **Step 2: Adım 5'in sonuna yeni alt-adım ekle**

Hedef konum: "Plan kaydedildi" commit onayı sonrası, "Adım 6"dan önce.

Eklenecek metin (Edit tool ile, "Adım 5" bölümünün sonuna):

```markdown
### Aktif Task Layer Hatırlatması (opsiyonel)

Commit'ten sonra:

> "Bu plan için `docs/active/<slug>/` altında TASK.md ve boş HANDOFF.md yaratıp `CURRENT.md`'ye satır ekleyeyim mi? (y/n)"

- Onaylı ise:
  1. `templates/TASK.md.template`'i kopyala → `docs/active/<slug>/TASK.md`; frontmatter doldur (title, status=proposed, started=bugün, last-touched=bugün)
  2. `templates/HANDOFF.md.template`'i kopyala → `docs/active/<slug>/HANDOFF.md`; Context bölümünü doldur (Task adı, spec link, plan link, branch, last updated)
  3. `docs/active/CURRENT.md`'ye satır ekle: `- \`<slug>/\` — <kısa memo>`
  4. Ayrı commit: `docs: add active task entry for <slug>`
- Hayır ise: hiçbir şey yapma, devam et.
```

- [ ] **Step 3: Doğrulama**

```bash
grep -A 12 "Aktif Task Layer Hatırlatması" ~/.claude/commands/write-plan.md
```

Beklenen: eklenen blok aynen görünür.

- [ ] **Step 4: Commit yok (~/.claude/ scope)**

## Task 5: `/execute-plan` — status=active hatırlatması

**Files:**
- Modify: `~/.claude/commands/execute-plan.md`

- [ ] **Step 1: Mevcut execute-plan.md başlangıç akışını bul**

```bash
head -40 ~/.claude/commands/execute-plan.md
```

- [ ] **Step 2: "Plan oku" adımından sonra hatırlatma ekle**

Eklenecek metin (Edit tool ile, plan okuma adımı sonrası):

```markdown
### Aktif Task Layer Hatırlatması

`docs/active/CURRENT.md` oku. Eşleşen task slug var mı?

- Eşleşme varsa:
  > "Aktif task `<slug>` bulundu. TASK.md status'u `proposed` → `active` yapayım mı? (y/n)"
  - Onaylı ise TASK.md frontmatter: `status: active`, `last-touched: <bugün>`
  - Hayır ise atla
- Eşleşme yoksa: aktif task layer kullanılmıyor, atla.
```

- [ ] **Step 3: Doğrulama**

```bash
grep -A 8 "Aktif Task Layer Hatırlatması" ~/.claude/commands/execute-plan.md
```

- [ ] **Step 4: Commit yok**

## Task 6: `/commit` — TASK Current Status + Vault promotion check

**Files:**
- Modify: `~/.claude/commands/commit.md`

- [ ] **Step 1: Mevcut commit.md son adımını bul**

```bash
grep -n "## Adım\|## Step" ~/.claude/commands/commit.md | tail -5
```

- [ ] **Step 2: Son adıma (commit gerçekleşmeden hemen önce VEYA sonra — mevcut yapıya göre) iki alt-adım ekle**

Eklenecek metin (Edit tool ile):

```markdown
### Aktif Task Layer — TASK Update Hatırlatması

`docs/active/CURRENT.md` oku. Eşleşen task varsa:

> "Bu commit için TASK.md'yi güncelleyelim mi?
> - Current Status: <önerilen tek satır>
> - last-touched: <bugün>
> (y/n)"

Onaylı ise TASK.md edit; ayrı commit gerekmez, bu commit'e dahil edilebilir.

### Vault Promotion Check (P1)

Aynı task için TASK.md `# Decisions Log`'u oku. Heuristic:

- **Promote candidate:** mimari karar, workflow/agent responsibility değişikliği, path/schema/lifecycle/naming standardı, vendor/model/altyapı kararı, cross-app etki, tekrar eden hata modu, gelecekte başka task'larda kullanılacak sentez
- **Task-scope-only:** geçici progress, bu task'a özel implementation detayı, tek seferlik workaround, sadece bu task'a ait test sonucu

Candidate kararları **numbered liste** olarak göster:

```
Promote adayları:
1. <karar> — <neden candidate>
2. <karar> — <neden candidate>

Hangileri vault'a? (örn: "1, 3 — 2 kalsın", "hepsi", "atla")
```

Seçilenler için her biri için:
1. Hedef öner: `decisions/YYYY-MM-DD-<slug>.md` (yeni) veya `<existing-page>.md` (güncelleme)
2. Kullanıcı onayı sonrası Claude vault'a Write
3. TASK.md Decisions Log'daki ilgili karara `→ Vault: [[decisions/...]]` ekle

Vault yazımı zorunlu olarak vault frontmatter disiplinine uyar (verification-status, sources, last-verified, type, status, tags).
```

- [ ] **Step 3: Doğrulama**

```bash
grep -A 5 "Vault Promotion Check" ~/.claude/commands/commit.md
```

- [ ] **Step 4: Commit yok**

## Task 7: `/review` — high/critical → Open Problems + Notes For Claude

**Files:**
- Modify: `~/.claude/commands/review.md`

- [ ] **Step 1: Mevcut review.md çıktı/sonuç bölümünü bul**

```bash
tail -40 ~/.claude/commands/review.md
```

- [ ] **Step 2: Review tamamlanma sonrası hatırlatma ekle**

Eklenecek metin (Edit tool ile, dosyanın sonuna):

```markdown
## Aktif Task Layer Entegrasyonu

Review tamamlanınca `docs/active/CURRENT.md` oku. Eşleşen task varsa:

1. Review çıktısındaki **high / critical** bulguları sırala:
   > "Bu bulguları TASK.md `# Open Problems` bölümüne işleyeyim mi?
   > - [ ] <bulgu 1>
   > - [ ] <bulgu 2>
   > (y/n / seç)"

2. Review özetini (1-2 cümle) HANDOFF.md `## Notes For Claude → Codex'in/Review'ın özellikle dikkat çektiği bulgular` satırına ekle hatırlatması:
   > "Review özetini HANDOFF.md Notes For Claude'a ekleyeyim mi? (y/n)"

**Önemli:** Bu adım `status` değiştirmez. `waiting-review`'a geçiş kullanıcı manuel kararı.
```

- [ ] **Step 3: Doğrulama**

```bash
grep -A 10 "Aktif Task Layer Entegrasyonu" ~/.claude/commands/review.md
```

- [ ] **Step 4: Commit yok**

## Task 8: `/finish-branch` — Conditional matrix (PR/merge/sil/tut)

**Files:**
- Modify: `~/.claude/commands/finish-branch.md`

- [ ] **Step 1: Mevcut 4-seçenek bölümünü bul**

```bash
grep -n "merge\|PR\|tut\|sil\|seçenek" ~/.claude/commands/finish-branch.md
```

- [ ] **Step 2: Her seçim sonrası task layer davranışını ekle**

Eklenecek metin (Edit tool ile, kullanıcı seçimi sonrası — branch işleminden önce):

```markdown
## Aktif Task Layer — Closure Matrix

Kullanıcı seçimine göre `docs/active/<slug>/`'ye davran. Önce `docs/active/CURRENT.md` oku, eşleşen task slug yoksa bu blok atlanır.

### Seçim: MERGE veya SİL → Full Closure

1. **TASK.md final güncellemesi**
   - `status: done` (merge) veya `cancelled` (sil)
   - `last-touched: <bugün>`
   - `Current Status`: son özet (1-2 cümle)
2. **HANDOFF.md closure summary**
   - `## Current State → Summary`: task ne ile bitti
   - `## Resume From → Next command`: vault promotion durumu / loose end notu
   - `## Verification`: final pass/fail
3. **Vault promotion check** çalıştır (bkz. `/commit` Vault Promotion Check bloğu — aynı P1 akışı)
4. Onaylı kararlar vault'a yazılır
5. TASK.md Decisions Log vault linkleriyle güncellenir
6. **TASK.md frontmatter: `status: archived`** (move'dan önce — bu sıra zorunlu)
7. Move: `docs/active/<slug>/` → `docs/task-archive/YYYY/MM/<slug>/` (YYYY/MM = bugünün yıl/ay)
   ```bash
   YYYY=$(date +%Y); MM=$(date +%m)
   mkdir -p "/root/otomaix/docs/task-archive/$YYYY/$MM"
   git mv "docs/active/<slug>" "docs/task-archive/$YYYY/$MM/<slug>"
   ```
8. `docs/active/CURRENT.md`'den ilgili satırı sil; liste boş kalırsa `_(no active tasks)_` yaz
9. Ayrı commit: `docs: archive task <slug>`

### Seçim: PR → waiting-review + Rolling Update (Archive YOK)

1. TASK.md: `status: waiting-review`, `last-touched: <bugün>`
2. HANDOFF.md rolling güncelle (closure değil) — Current State'e: "PR #N açıldı, review bekleniyor"
3. **Archive yapma, vault promotion check çalıştırma**
4. Opsiyonel: kullanıcı "PR sonrası otomatik kapatma" derse not düş (manuel hatırlatma için)

### Seçim: TUT → No-op

TASK ve HANDOFF.md aktif kalır, dokunulmaz.
```

- [ ] **Step 3: Doğrulama**

```bash
grep -A 5 "Closure Matrix" ~/.claude/commands/finish-branch.md
```

- [ ] **Step 4: Commit yok**

---

# PHASE E — Root CLAUDE.md

## Task 9: `/root/otomaix/CLAUDE.md`'ye active task layer bölümü + session başlangıç protokolü ekle

**Files:**
- Modify: `/root/otomaix/CLAUDE.md`

- [ ] **Step 1: Mevcut CLAUDE.md'yi oku**

```bash
cat /root/otomaix/CLAUDE.md
```

22 satır, "Drift koruma" ve "Çapraz app kuralları" bölümlerinden oluşuyor.

- [ ] **Step 2: Sonuna yeni bölüm ekle**

Eklenecek metin (Edit tool ile, dosyanın sonuna):

```markdown

## Aktif Task Layer

Canlı task state ve devir teslim için repo overlay'i. Detaylar:
[`docs/specs/2026-05-19-claude-codex-aktif-katman.md`](docs/specs/2026-05-19-claude-codex-aktif-katman.md).

**Path konvensiyonu:**
- `docs/active/CURRENT.md` — aktif task pointer'ı (her zaman var)
- `docs/active/<slug>/TASK.md` — canonical task state (status, decisions, open problems)
- `docs/active/<slug>/HANDOFF.md` — rolling session-boundary devir teslim
- `docs/task-archive/YYYY/MM/<slug>/` — kapanmış task'lar (bitiş tarihine göre)

**Canonical ayrım:**
- **Status**, **Decisions Log**, **Open Problems** → TASK.md
- **Verification**, **Risks**, **Notes For Claude/Codex** → HANDOFF.md
- **Mimari kararlar** (promote edilenler) → Vault `decisions/`

**Manuel mod:** Tüm transition'lar (proposed → active → blocked → waiting-review → done → archived/cancelled) manuel TASK.md edit ile yapılır. Slash command hatırlatmaları sadece "unuttum" friction'ını azaltır — otomatik state mutation yok.

**Codex:** Active layer'a yazma yetkisi yok. Bulgu/öneriyi stdout olarak döner, Claude HANDOFF.md "Notes For Claude"a işler.

### Aktif Task Layer — Session Başlangıç Protokolü

Bir kullanıcı sorusu/task geldiğinde:

1. `docs/active/CURRENT.md` oku (her zaman var; boş olabilir)
2. Listelenen task'lardan kullanıcı sorusuyla alakalı olanı seç
   - Tek aktif task varsa otomatik
   - Birden fazlaysa kullanıcıya sor
   - Hiçbiri uymuyorsa active layer'ı atla
3. Seçilen task için: `docs/active/<slug>/TASK.md` ve `HANDOFF.md` oku
4. Vault sorgusu gerekiyorsa: `/root/otomaix-brain/index.md` → ilgili wiki sayfaları
5. Cevap ver / aksiyon al

### Yeni slash command

- `/handoff` — Claude tek başına HANDOFF.md yazar
- `/handoff --with-codex` — Codex read-only review çağrılır, Notes For Claude'a işlenir

### Mevcut slash command entegrasyonu (özet)

- `/write-plan` sonu → TASK + HANDOFF yaratma sorusu
- `/execute-plan` başı → status=active sorusu
- `/commit` → Current Status update + Vault promotion check
- `/review` → high/critical → Open Problems + Notes For Claude
- `/finish-branch` → seçime göre matrix (merge/sil = closure+archive, PR = waiting-review, tut = no-op)
```

- [ ] **Step 3: Doğrulama**

```bash
grep -c "Aktif Task Layer" /root/otomaix/CLAUDE.md
wc -l /root/otomaix/CLAUDE.md
```

Beklenen: "Aktif Task Layer" 2 (başlık + alt başlık), satır sayısı ~70.

- [ ] **Step 4: Commit**

```bash
cd /root/otomaix
git add CLAUDE.md
git commit -m "docs: add active task layer section to project CLAUDE.md"
```

---

# PHASE F — AGENTS.md Sync

## Task 10: `/sync-agents-md project` ile `/root/otomaix/AGENTS.md` damıtmasını güncelle

**Files:**
- Modify: `/root/otomaix/AGENTS.md` (otomatik, marker bloğu içinde)

- [ ] **Step 1: Mevcut AGENTS.md durumu**

```bash
wc -l /root/otomaix/AGENTS.md
grep -c "BEGIN CODEX-DISTILLED\|END CODEX-DISTILLED" /root/otomaix/AGENTS.md
```

Beklenen: 2 marker bulunur.

- [ ] **Step 2: /sync-agents-md project çağır**

Bu komut Codex'i çağırır (~30sn-2dk):

```
/sync-agents-md project
```

Komut `node codex-companion.mjs task --fresh --wait --cwd /root/otomaix` ile Codex'i çalıştırır. Codex `/root/otomaix/CLAUDE.md`'yi okur, AI-agnostic kısımları damıtır, marker bloğunu yeniler.

- [ ] **Step 3: Çıktıyı incele**

```bash
git diff /root/otomaix/AGENTS.md | head -100
```

Doğrula:
- Marker dışı içerik korunmuş
- "Active Task Layer" bölümü AGENTS.md damıtmasında var
- "Session Başlangıç Protokolü" var
- Path konvensiyonu listelenmiş
- Slash command listesi (Claude'a özel) DAHİL EDİLMEMİŞ (AI-agnostic değil)

**Sorun varsa:** Codex çıktısı yanlış damıtıyorsa, CLAUDE.md'yi düzelt, tekrar çağır. Otomatik olmadığı için iterasyon serbest.

- [ ] **Step 4: Vault AGENTS.md'ye dokunulmadığını doğrula**

```bash
git -C /root/otomaix-brain status AGENTS.md
git -C /root/otomaix-brain log --oneline -3 AGENTS.md
```

Beklenen: vault AGENTS.md değişmedi. Eğer yanlışlıkla `/sync-agents-md global` veya vault'a yazım olduysa, geri al.

- [ ] **Step 5: Commit**

```bash
cd /root/otomaix
git add AGENTS.md
git commit -m "docs: sync AGENTS.md with active task layer additions"
```

---

# PHASE G — Vault Çapraz Referans

> **Codex notu:** Bu phase vault yazımı içerir. Codex uyguluyorsa:
> dosyayı **değiştirme**, önerilen değişikliği stdout olarak rapor et —
> Claude veya kullanıcı vault'a yazar ve commit/push eder. Bu kural
> "Codex vault'a yazmaz" prensibinin uygulamasıdır (`AGENTS.md` Kapsam
> Dışı bölümü).

## Task 11: `cross-project/infrastructure/codex-entegrasyonu.md`'ye active task layer referansı ekle

**Files:**
- Modify: `/root/otomaix-brain/cross-project/infrastructure/codex-entegrasyonu.md`

**Uygulayıcı:** Claude veya kullanıcı (Codex bu phase'de yazmaz, sadece patch önerir).

- [ ] **Step 1: Mevcut sınırlamalar bölümünü bul**

```bash
grep -n "Conversation history\|Sınırlamalar" /root/otomaix-brain/cross-project/infrastructure/codex-entegrasyonu.md
```

- [ ] **Step 2: "Conversation history aktarımı yok" notunun yanına partial mitigation cümlesi ekle**

Eklenecek metin (Edit tool ile, ilgili madde sonuna):

```markdown
  **Partial mitigation (2026-05-19+):** Otomaix repo'sunda `docs/active/<slug>/HANDOFF.md` ile session-boundary devir teslim mekanizması var. Codex `--cwd /root/otomaix` çağrıldığında bu dosyayı okuyarak önceki session'ın durumunu kısmen yeniden yapılandırabilir. Tam conversation history değil — Claude tarafından yazılmış yapılandırılmış özet. Detaylar: `/root/otomaix/docs/specs/2026-05-19-claude-codex-aktif-katman.md` (spec dosyası repo'da; vault'a promote edilirse buraya `[[decisions/2026-05-19-claude-codex-aktif-katman]]` wikilink'i eklenebilir).
```

- [ ] **Step 3: Doğrulama**

```bash
grep -A 2 "Partial mitigation" /root/otomaix-brain/cross-project/infrastructure/codex-entegrasyonu.md
```

- [ ] **Step 4: Vault commit + push**

```bash
cd /root/otomaix-brain
git add cross-project/infrastructure/codex-entegrasyonu.md
git commit -m "docs(codex): note HANDOFF.md partial mitigation for conversation history gap"
# Push: vault ayrı private repo, kullanıcı onayı ile
```

> Kullanıcıya sor: *"Vault commit edildi. Push edelim mi? (`git push origin main`)"*

---

# PHASE H — End-to-End Smoke Test

## Task 12: Dummy task ile lifecycle walkthrough

**Amaç:** Sistemin gerçek bir task üzerinde çalıştığını kanıtlamak. Test task: bu plan'ın kendisi (`claude-codex-aktif-katman`). Plan tamamlandıktan sonra closure akışını çalıştırarak hem doğrulama hem demo yapılır.

**Files:**
- Create (geçici): `docs/active/claude-codex-aktif-katman/TASK.md`
- Create (geçici): `docs/active/claude-codex-aktif-katman/HANDOFF.md`
- Modify: `docs/active/CURRENT.md`

- [ ] **Step 1: Dummy task yarat (gerçek task — bu plan)**

```bash
mkdir -p /root/otomaix/docs/active/claude-codex-aktif-katman
cp /root/otomaix/templates/TASK.md.template /root/otomaix/docs/active/claude-codex-aktif-katman/TASK.md
cp /root/otomaix/templates/HANDOFF.md.template /root/otomaix/docs/active/claude-codex-aktif-katman/HANDOFF.md
```

TASK.md'yi Edit ile doldur:
- `title: Claude-Codex Aktif Task Layer`
- `status: active` (Phase A-G yapıldı, smoke test bizzat bu task üzerinde)
- `started: 2026-05-19`
- `last-touched: 2026-05-19`
- Goal: spec'ten 1-2 cümle özet
- References: spec ve plan path'leri
- Current Status: "Phase A-G tamamlandı, smoke test (Phase H) yürütülüyor"
- Decisions Log: bu seansta alınan 14 ana karar (özet — detay spec'te)

HANDOFF.md Context bölümünü doldur (Task, spec, plan, branch=main, last updated).

CURRENT.md'yi güncelle:

```markdown
# Active Tasks

- `claude-codex-aktif-katman/` — smoke test aşamasında
```

- [ ] **Step 2: `/handoff` çalıştır (default mode)**

Komut:
```
/handoff
```

Beklenen:
- Claude HANDOFF.md'yi tüm 7 bölümle doldurur
- TASK.md'ye dokunmaz (spec §5.2 uyumu)
- Commit onayı sorar (onaylama, smoke test'in sonunda toplu commit edilecek)

Doğrula: HANDOFF.md `## Resume From → Next command` "Task 12 Step 3 (--with-codex test)" benzeri net bir pointer içerir. TASK.md `last-touched` değişmemiş olmalı.

- [ ] **Step 3: `/handoff --with-codex` çalıştır**

Komut:
```
/handoff --with-codex
```

Beklenen:
- Codex çağrılır (~30sn-2dk)
- Codex stdout bulguları gösterilir
- Onaylı bulgular `## Notes For Claude → Codex'in özellikle dikkat çektiği bulgular` satırına eklenir

**Olası başarısızlık:** Codex çağrı pattern'i hatalıysa (yanlış `--cwd` veya prompt formatı), düzelt; `/handoff.md`'yi (Task 3) güncelle.

Doğrula: HANDOFF.md'de Codex bulgu listesi görünür.

- [ ] **Step 4: Vault promotion check'i tetikle (manuel simülasyon)**

TASK.md Decisions Log'a sahte karar ekle:

```markdown
- 2026-05-19: Dummy karar — smoke test için, promote edilmemeli (task-scope-only)
```

`/commit` çalıştırıldığında promotion check'in bu kararı "task-scope-only" olarak işaretlemesi, listede göstermemesi beklenir. Eğer "promote candidate" olarak işaretlerse heuristic dokümantasyonu (Task 6 metni) eksiktir; düzelt.

- [ ] **Step 5: `/finish-branch` SİL (cancelled) closure simülasyonu — vault yazımı YOK**

> **Önemli:** Burada gerçek branch silme yapılmaz (zaten main'deyiz). Sadece task layer **akışını** doğruluyoruz. Vault'a gerçek yazım smoke test'in parçası DEĞİL — vault canonical knowledge, test mutation'ı oraya gitmemeli.

Manuel olarak Phase D Task 8 metnindeki closure adımlarını yürüt:
1. TASK.md `status: cancelled`, `last-touched: 2026-05-19`, Current Status: "Smoke test tamamlandı"
2. HANDOFF.md closure summary doldur (Current State → Summary: "Aktif task layer canlıya alındı, smoke test geçti", Verification: "Phase A-G implementation + lifecycle walkthrough — passed")
3. **Vault promotion check — sadece doğrulama, yazım YOK:**
   - TASK.md'deki gerçek kararlardan promote candidate listesi üret
   - Her candidate için hedef öner (örn. `decisions/2026-05-19-<slug>.md`)
   - Listeyi kullanıcıya göster, doğrula: heuristic doğru ayrıştırıyor mu? Hedef önerileri makul mü?
   - **Vault'a YAZILMAZ** bu adımda. Smoke test bu kadar — heuristic + öneri akışı doğrulanır.
4. *(Atlandı)* — TASK.md Decisions Log link enjeksiyonu da ayrı, gerçek closure'da yapılır
5. TASK.md `status: archived`
6. `git mv docs/active/claude-codex-aktif-katman docs/task-archive/2026/05/claude-codex-aktif-katman`
7. CURRENT.md'yi boşalt → `_(no active tasks)_`

**Vault'a gerçek yazım istenirse — ayrı, opsiyonel adım:**

> Smoke test PASS sonrası, kullanıcı isterse aktif task layer'ı vault'ta da kayıt altına almak için ayrı bir akış başlatabilir:
> - `/commit`'in Vault Promotion Check bloğu manuel tetiklenir
> - Promote edilecek kararlar (örn. "Z hibrit slash command entegrasyonu", "P1 vault promotion mekanizması") seçilir
> - Claude vault'a `decisions/2026-05-19-claude-codex-aktif-katman.md` yazar (kullanıcı onayıyla)
>
> Bu adım plan'ın zorunlu task'ı **değildir** — kullanıcı tercihi.

- [ ] **Step 6: Final doğrulamalar**

```bash
ls /root/otomaix/docs/active/                                    # sadece CURRENT.md
cat /root/otomaix/docs/active/CURRENT.md                         # boş hal
ls /root/otomaix/docs/task-archive/2026/05/claude-codex-aktif-katman/  # TASK.md + HANDOFF.md
cat /root/otomaix/docs/task-archive/2026/05/claude-codex-aktif-katman/TASK.md | head -10  # status: archived
```

- [ ] **Step 7: Smoke test commit**

```bash
cd /root/otomaix
git add docs/active/ docs/task-archive/
git commit -m "test: end-to-end smoke test for active task layer

Dummy task created, /handoff and /handoff --with-codex exercised,
vault promotion check validated, closure flow (sil) walked through,
archive move verified."
```

---

# PHASE I — Closure + Memory Önerisi

> **Codex notu:** Bu phase memory write içerir. Codex memory'ye yazmaz
> (`~/.claude/projects/-root-otomaix/memory/` Codex Kapsam Dışı).
> Codex uyguluyorsa: memory entry'yi **stdout olarak öneri** çıkar —
> Claude veya kullanıcı manuel uygular. Plan progress tablosu repo'da
> olduğu için Codex onu güncelleyebilir.

## Task 13: Plan progress kapanışı + memory entry önerisi

**Files:**
- Modify: `docs/plans/2026-05-19-claude-codex-aktif-katman.md` (bu dosya — progress tablosu ✅)
- *(Öneri olarak)*: `~/.claude/projects/-root-otomaix/memory/project_claude_codex_active_layer.md` — Claude/kullanıcı uygular
- *(Öneri olarak)*: `~/.claude/projects/-root-otomaix/memory/MEMORY.md` — Claude/kullanıcı uygular

- [ ] **Step 1: Plan progress tablosunu kapat**

Edit tool (Codex: `apply_patch`) ile bu plan dosyasındaki "Implementation Progress" tablosunda tüm satırları `⬜` → `✅` yap.

- [ ] **Step 2: Memory entry önerisi üret (yazma)**

Aşağıdaki içeriği **stdout/rapor olarak** kullanıcıya sun. **Dosyaya yazma** — bu Claude'un veya kullanıcının manuel uygulayacağı bir öneridir:

```
ÖNERİ — Memory entry yaratılmalı:

Dosya: ~/.claude/projects/-root-otomaix/memory/project_claude_codex_active_layer.md
İçerik:
---
name: claude-codex-active-layer
description: Aktif task layer canlıya alındı (2026-05-19) — docs/active/<slug>/TASK.md + HANDOFF.md, CURRENT.md pointer, /handoff slash command, hibrit slash command entegrasyonu
metadata:
  type: project
---

**Durum:** Canlı (2026-05-19).

**Ne kuruldu:**
- docs/active/<slug>/TASK.md (canonical state) + HANDOFF.md (rolling session-boundary)
- docs/active/CURRENT.md pointer (branch-agnostic, insan memo)
- docs/task-archive/YYYY/MM/<slug>/ (bitiş tarihine göre)
- /handoff ve /handoff --with-codex slash command'leri
- 5 mevcut slash command'e (write-plan, execute-plan, commit, review, finish-branch) hatırlatma entegrasyonu
- Root CLAUDE.md'ye session başlangıç protokolü
- /sync-agents-md project ile repo AGENTS.md damıtması güncel

**Canonical ayrım:** Status & Decisions Log & Open Problems = TASK.md; Verification & Risks & Notes For Claude/Codex = HANDOFF.md; mimari kararlar (promote edilmiş) = Vault decisions/.

**Active state vault'a konmadı.** Vault sadece onaylı çapraz referans/promotion kapsamında güncellendi veya güncellenmesi önerildi (Phase G: `codex-entegrasyonu.md` partial mitigation notu; closure'daki opsiyonel decision promotion).

**Detaylar:**
- Spec: docs/specs/2026-05-19-claude-codex-aktif-katman.md
- Plan: docs/plans/2026-05-19-claude-codex-aktif-katman.md
- Archive: docs/task-archive/2026/05/claude-codex-aktif-katman/

VE: MEMORY.md indexine satır eklenmeli:
- [Claude-Codex aktif task layer canlıda](project_claude_codex_active_layer.md) — docs/active/<slug>/TASK+HANDOFF, /handoff komutu, hibrit slash command entegrasyonu
```

**Uygulayıcı:** Claude veya kullanıcı. Codex bu adımda dosya yaratmaz/değiştirmez.

- [ ] **Step 3: Final commit (plan progress için)**

```bash
cd /root/otomaix
git add docs/plans/2026-05-19-claude-codex-aktif-katman.md
git commit -m "docs(plan): mark active task layer implementation complete"
```

Memory dosyaları `~/.claude/projects/` altında — Otomaix git'inin dışında, ayrıca commit gerekmez. Step 2'deki öneri Claude/kullanıcı tarafından uygulandıktan sonra memory sistemine dahil olur (sıradaki session'larda otomatik yüklenir).

---

## Self-Review Notları (plan yazıldıktan sonra)

**Spec coverage:** Spec §3 (file layout), §4 (schemas), §5 (lifecycle), §6 (slash command integration), §7 (vault promotion), §8 (closure), §9 (session protocol), §10 (implementation notes) — hepsi plan task'larında karşılanıyor. §11 (out-of-scope) bilinçli atlananlar; plan'a girmedi.

**Placeholder scan:** Plan boyunca "TBD" / "TODO" yok. Tüm dosyalar tam içerikli HEREDOC'lar. Slash command edit'leri için eklenecek metin tam yazılı.

**Type consistency:** "status" enum tüm dosyalarda tutarlı (7 değer). "CURRENT.md" pattern tüm referanslarda aynı. "task-archive/YYYY/MM/<slug>/" path konsistent.

**TDD esnetmesi:** Bu plan markdown + slash command + config kapsıyor; kod birimi yok. "Test" Phase H'de end-to-end smoke walkthrough — TDD'nin red→green→commit ritmi doğrudan uygulanmıyor, ama her task'ın "Doğrulama" adımı verification disiplini sağlıyor.

**Atlanan otomatik chain:** `executing-plans` skill'i normalde `finishing-a-development-branch` ve `using-git-worktrees`'i auto-chain'ler. Bu plan main'de çalıştığı ve closure adımı Phase I Task 13'te zaten ele alındığı için chain bilinçli olarak kırılır (CLAUDE.md Skill Chain Override kuralı).

---

## İlgili Dosyalar

- **Spec:** `docs/specs/2026-05-19-claude-codex-aktif-katman.md`
- **Girdi özeti:** `/root/sonkonusmaozeti.md` (bu plan'ın doğduğu seansın özeti)
- **Mevcut workflow:** `~/.claude/commands/{brainstorm,write-plan,execute-plan,commit,review,finish-branch,handoff}.md`
- **Codex sync sistemi:** `~/.claude/commands/sync-agents-md.md`, `/root/otomaix-brain/cross-project/infrastructure/codex-entegrasyonu.md`
- **Vault scope:** `/root/otomaix-brain/{AGENTS,CLAUDE}.md` (dokunulmayan)
