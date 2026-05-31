---
title: simplify-claude-codex.md Implementation Plan
status: plan-approved
date: 2026-05-31
source_spec: docs/specs/2026-05-31-simplify-claude-codex-command.md
source_spec_unapproved_override: false
noisy_review_override: false
unresolved_high_severity_override: false
codex_plan_review_status: approved-by-iteration-limit
codex_plan_review_iterations: 3
codex_plan_targeted_fixes: 13
codex_plan_review_log: docs/reviews/codex/2026-05-31-simplify-claude-codex-command-plan.md
---

# simplify-claude-codex Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Override note (CLAUDE.md):** Bu plan `/execute-plan-claude-codex` üzerinden uygulanmalıdır. Skill chain'in auto `finishing-a-development-branch`/`using-git-worktrees` önerileri ignore — bizim akışımız `/execute-plan-claude-codex` → `/simplify-claude-codex` → `/review` → `/security-review` → `/finish-branch`.

**Goal:** Spec `docs/specs/2026-05-31-simplify-claude-codex-command.md` (spec-approved) implement et — yeni custom slash command `~/.claude/commands/simplify-claude-codex.md` yarat ve claude-codex ailesinin (spec/write-plan/execute-plan) 4-way drift contract'ına entegre et.

**Architecture:** Atomic-one-pass, **iki ayrı dosya kümesi**: (1) Global slash command dosyaları `~/.claude/commands/*.md` — bu repo'nun (`/root/otomaix`) DIŞINDA, repo commit'i değil; her kritik task öncesi `cp X /tmp/X.bak` backup, FAIL durumunda rollback (önceki 2026-05-25-write-plan-claude-codex-command plan'ının pattern'ı). (2) Repo-local audit dosyaları `docs/plans/...-command.md` + `docs/reviews/codex/...-command-plan.md` (+ spec zaten orada) — bunlar normal repo commit'i (`docs:` prefix). Canonical CODEX-CALL-PROTOCOL bloğu spec-claude-codex.md'den byte-exact kopyalanır (Task 3 erken). 3 ayna komut (spec/write-plan/execute) Sözleşme Notları'nda dosyaya özgü stale-text düzeltmeleri (Task 12). execute-plan'da /simplify referansı sweep manuel hit-by-hit (Task 13, blind sed yasak). simplify.md DEPRECATED stub'a en son çevrilir (Task 14). Drift Check A 4-way diff=0 + Check B 8 tripwire token grep zorunlu doğrulama (Task 15).

**Tech Stack:** Markdown frontmatter (YAML), bash (awk/grep/diff for drift verification), git.

**Verification model:** Bu plan markdown spec (slash command) implementasyonudur — production kod değil. Her task `tdd: skip`. Verification = drift Check A (4-way diff=0) + Check B (8 tripwire token presence in all 4 files) + structural integrity (BEGIN/END marker count, frontmatter parse, Adım numaralandırma tutarlılığı, canonical `<id>` token kullanımı) + best-effort runtime smoke.

**Source-of-truth referans (F2 düzeltmesi):** Spec dosyası (`docs/specs/2026-05-31-simplify-claude-codex-command.md`) yetkili kaynaktır. Bölüm bazlı "Spec Adım N metnini birebir append et" diyen task'lar executor'ı oraya yönlendirir (DRY). **Drift önleyici verification pattern (her ilgili task sonunda zorunlu):**

```bash
# Sed extract — spec'ten ilgili bölümü ham metin olarak çıkar
sed -n '/^## Adım <N>:/,/^## Adım <NEXT>/{/^## Adım <NEXT>/!p}' docs/specs/2026-05-31-simplify-claude-codex-command.md > /tmp/spec-section-<N>.txt

# Yeni komuttaki aynı bölümü çıkar
sed -n '/^## Adım <N>:/,/^## Adım <NEXT>/{/^## Adım <NEXT>/!p}' ~/.claude/commands/simplify-claude-codex.md > /tmp/cmd-section-<N>.txt

# Diff — kabul edilebilir farklar: yalnız "spec" → "komut" terminoloji uyarlaması (örn. "spec'in" → "komutun") veya path referansı (örn. log path örnekleri). Anlam, kural, sıralama, format zorunluluk değişmemeli.
diff /tmp/spec-section-<N>.txt /tmp/cmd-section-<N>.txt
```

Diff çıktısı manuel inspect — anlamsal eşdeğerlik (kural/format/sıra/zorunluluk birebir) doğrulanmalı. Pure paraphrase YASAK; "spec'ten birebir" = bölüm içeriği byte-yakın, sadece self-referans terminolojisi yumuşatılabilir (`spec'in Adım 5 prompt'u` → `Adım 5 prompt'u`).

Bu pattern Task 4, 5, 7, 8, 9, 10, 11 her "Spec'in Adım N'i birebir append et" step'inden sonra koşulur. Plan'da bireysel task'larda inline tekrarlanmaz — bu blok referans alınır.

---

## Task 1: Pre-flight Inventory ve Snapshot

**tdd: skip** (read-only inventory; hiçbir dosya değişmiyor)

**Files (read only):**
- `~/.claude/commands/spec-claude-codex.md` (canonical CODEX-CALL-PROTOCOL block + Sözleşme Notları)
- `~/.claude/commands/write-plan-claude-codex.md` (Sözleşme Notları stale text)
- `~/.claude/commands/execute-plan-claude-codex.md` (Sözleşme Notları stale text + `/simplify` references)
- `~/.claude/commands/simplify.md` (eski içerik referans için)
- `docs/specs/2026-05-31-simplify-claude-codex-command.md` (target spec)

- [ ] **Step 1: BEGIN/END marker integrity on canonical**

Run:
```bash
grep -c "CODEX-CALL-PROTOCOL:BEGIN\|CODEX-CALL-PROTOCOL:END" ~/.claude/commands/spec-claude-codex.md
```
Expected: `2` (1 BEGIN + 1 END; aksi halde canonical kirli, plan durdur).

- [ ] **Step 2: Canonical block extraction snapshot**

Run:
```bash
awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' ~/.claude/commands/spec-claude-codex.md > /tmp/codex-call-protocol.snapshot
wc -l /tmp/codex-call-protocol.snapshot
```
Expected: 40+ satır (canonical blok). Snapshot dosyası Task 3'te kullanılır.

- [ ] **Step 3: Tripwire 8 token presence on canonical**

Run:
```bash
for token in "codex-companion.mjs" "git rev-parse" "AGENTS.md" "timeout 480s" "124" "Claude-only devam et" "Tekrar dene" "Komutu durdur"; do
  count=$(grep -c -F "$token" /tmp/codex-call-protocol.snapshot)
  echo "$token: $count"
done
```
Expected: Her token >= 1. Sıfır olan token varsa canonical kirli, plan durdur.

- [ ] **Step 4: Sözleşme Notları stale text inventory (3 ayna komut için referans katalog)**

Run:
```bash
echo "--- spec-claude-codex ---"
grep -n "biri değişirse\|write-plan-claude-codex.*ile\|drift\|Check A\|Check B" ~/.claude/commands/spec-claude-codex.md | head -20
echo "--- write-plan-claude-codex ---"
grep -n "biri değişirse\|iki komut\|drift\|Check A\|Check B" ~/.claude/commands/write-plan-claude-codex.md | head -20
echo "--- execute-plan-claude-codex ---"
grep -n "biri değişirse\|üç komut\|3-way\|drift\|Check A\|Check B" ~/.claude/commands/execute-plan-claude-codex.md | head -20
```
Expected: Stale numerals catalog. Beklenen pattern'ler:
- spec: binding "`/write-plan-claude-codex` ile birebir aynıdır" (1 komut adresi)
- write-plan: "iki komutta birebir" benzeri
- execute-plan: "3-way" + "spec vs write-plan + spec vs execute"

Catalog'u not al — Task 12'de dosyaya özgü güncelleme için kullanılacak.

- [ ] **Step 5: /simplify references in execute-plan-claude-codex**

Run:
```bash
grep -n "/simplify" ~/.claude/commands/execute-plan-claude-codex.md
```
Expected: Tüm hit'lerin listesi. Her hit Task 13'te classify edilir (active next-step reference vs decisions-log/historical).

- [ ] **Step 6: awk reuse search in existing plans (Codex önerisi)**

Run:
```bash
grep -n "awk.*CODEX-CALL-PROTOCOL\|extracted block\|spec vs write-plan" docs/plans/2026-05-25-write-plan-claude-codex-command.md 2>/dev/null || echo "no prior awk pattern"
```
Expected: Mevcut plan'da benzer awk extraction varsa Task 15 verification command'ı reuse eder; yoksa Task 15'teki tam komut kullanılır.

- [ ] **Step 7: Backup global komut dosyaları (F1 düzeltmesi — rollback path her kritik task için)**

Modifiye edilecek 3 mevcut dosya + 1 stub'lanacak dosya = 4 dosya backup:

Run:
```bash
cp ~/.claude/commands/spec-claude-codex.md /tmp/spec-claude-codex.md.bak
cp ~/.claude/commands/write-plan-claude-codex.md /tmp/write-plan-claude-codex.md.bak
cp ~/.claude/commands/execute-plan-claude-codex.md /tmp/execute-plan-claude-codex.md.bak
cp ~/.claude/commands/simplify.md /tmp/simplify.md.bak
ls -la /tmp/*.bak
```
Expected: 4 .bak dosyası listede; her biri non-zero size.

Rollback policy: Task 12-13-14'te bir doğrulama FAIL ederse:
- Etkilenen dosyayı backup'tan geri yükle: `cp /tmp/<name>.md.bak ~/.claude/commands/<name>.md`
- İlgili task'a dön, hatayı düzelt, tekrar dene
- Backup'lar Task 15 commit sonrası `/tmp`'de kalır (manual cleanup veya OS auto-clean'a bırak)

- [ ] **Step 8: No commit (inventory + backup only — repo'da değişiklik yok)**

Bu task hiçbir repo dosyasını değiştirmedi (yalnız /tmp backup'lar oluşturdu); commit yok.

---

## Task 2: simplify-claude-codex.md İskelet — Frontmatter + Görev + Akış Genel Bakış

**tdd: skip**

**Files:**
- Create: `~/.claude/commands/simplify-claude-codex.md`

- [ ] **Step 1: Yeni dosyayı oluştur**

Write to `~/.claude/commands/simplify-claude-codex.md`:

````markdown
---
description: Codex pre-scan + final adversarial review + commit-gated simplification; eski /simplify'ın claude-codex ailesi eşi (custom, drift-check 4-way)
argument-hint: [SCOPE]
---

## Görev

Yakın zamanda değişen kodu tara, basitleştirme fırsatları bul, **Claude uygular + Codex iki noktada review eder** (opsiyonel pre-scan + zorunlu final adversarial review). Eski single-actor `/simplify`'ın claude-codex ailesi (spec/write-plan/execute-plan) eşi. Tek commit (push YOK). Sonraki adım: `/review`.

**İnvariant:** Codex final simplification review çalışmadan ve unresolved critical/high bulgular çözülmeden veya açık override edilmeden commit önerilmez.

**Sonraki adım zinciri:** `/execute-plan-claude-codex` → `/simplify-claude-codex` → `/review` → `/security-review` → `/finish-branch` (closure).

## Akış Genel Bakış

```
1.  Scope belirle (arg | git diff | origin/main..HEAD | son 5 commit kullanıcı seçimi); INITIAL_TREE_DIRTY flag
2.  Test suite preflight (komut + test dosyası varlığı)
3.  Claude ön tarama (5 kategori + Other; scope dışı dosyalar read-only context)
4.  Mode seçimi: Standard (Recommended) / Light + log dosyası setup (ayrıntı Adım 4.5)
4.5 Log dosyası setup (mkdir + ATTEMPT counter + previous-attempt link first line)
5.  (Yalnız Standard) Codex pre-scan — task --fresh; hibrit prompt (DO_NOT_APPLY / CANDIDATE / Other)
6.  Sentez + risk yükseltme + kullanıcı onayı sınıfa göre (Kural A-F)
7.  Fix uygulama (Claude yazar; scoped verification per batch; new-file rule; test rewrite scope)
8.  Final tests (full/declared test suite taze)
9.  Codex final adversarial review — adversarial-review $SCOPE; 8 maddelik prompt; FIXES_APPLIED gate
10. Critical/high guard (Düzelt / Override [audit -<ATTEMPT>.md] / Durdur)
11. Commit gate + final rapor (Şablon A test-suite-aware / B1 / B2); push YOK; sonraki adım /review

(Codex çağrıları — Adım 5, 9 — "Codex Çağrı Protokolü"nü izler.)
```
````

- [ ] **Step 2: Verify file created**

Run: `head -30 ~/.claude/commands/simplify-claude-codex.md`
Expected: Frontmatter (description + argument-hint) + Görev + Akış Genel Bakış görünür.

- [ ] **Step 3: No commit (Task 15 final atomic commit)**

---

## Task 3: Canonical CODEX-CALL-PROTOCOL Bloğu Byte-Exact Kopya + Binding/Downstream

**tdd: skip; CRITICAL — drift contract'ın merkezi**

**Files:**
- Modify: `~/.claude/commands/simplify-claude-codex.md` (append after Akış Genel Bakış)

- [ ] **Step 1: Binding/intro çerçeve metnini append**

Append to `~/.claude/commands/simplify-claude-codex.md` (Akış Genel Bakış'tan sonra, canonical bloğun ÖNÜ):

````markdown

## Codex Çağrı Protokolü (ortak — Adım 5 + Adım 9)

Adım 5 ve Adım 9'daki **tüm** Codex çağrıları bu protokolü izler. Amaç: companion
yoksa, Codex çöker/hata verir veya çağrı asılırsa komut **sessizce kırılmaz** —
kullanıcıya seçenek sunar.

> **Binding (simplify-claude-codex):** İki çağrı noktası var; marker bloğu iki çağrı
> tipi tanımlar. Eşleştirme:
> · `<STEP_A>` (`<CALL>` = `task --fresh`) = **Adım 5** (pre-scan; yalnız Standard mode)
> · `<STEP_B>` (`<CALL>` = `adversarial-review $SCOPE`) = **Adım 9** (final review; her iki mode'da zorunlu)
>
> Aşağıdaki `CODEX-CALL-PROTOCOL` bloğu **canonical** `spec-claude-codex` ile birebir
> aynıdır (drift-check: diff=0; bkz. Sözleşme Notları). Bloğu değiştirirsen canonical'ı,
> `write-plan-claude-codex`'i ve `execute-plan-claude-codex`'i de senkronla (4-way).

````

- [ ] **Step 2: Canonical bloğu byte-exact append (F6 düzeltmesi — inline recompute, /tmp snapshot'a bağımlı değil)**

Snapshot fragility (Codex F6 bulgusu): `/tmp/codex-call-protocol.snapshot` session crash'te silinebilir. Bunun yerine **her kullanım öncesi inline recompute** + spec'te marker count guard:

```bash
# Guard: spec'te canonical block sağlam mı?
spec_markers=$(grep -c "CODEX-CALL-PROTOCOL:BEGIN\|CODEX-CALL-PROTOCOL:END" ~/.claude/commands/spec-claude-codex.md)
if [ "$spec_markers" -ne 2 ]; then
  echo "FAIL — spec marker count $spec_markers (expected 2). Canonical kirli; durdur."
  exit 1
fi

# Inline append — snapshot'a bağımlı değil
awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' ~/.claude/commands/spec-claude-codex.md >> ~/.claude/commands/simplify-claude-codex.md
echo "" >> ~/.claude/commands/simplify-claude-codex.md
```

(Task 1 Step 2 snapshot yine yapılır audit için ama Task 3 onu kullanmaz; recompute deterministik.)

- [ ] **Step 3: Downstream notunu append (canonical bloğun ARDI)**

Append:

````markdown

> **Downstream (simplify-claude-codex):** Claude-only seçilirse, hangi adımdayız önemli:
> · **Adım 5** Claude-only → pre-scan yapılmaz; Codex'in DO_NOT_APPLY/CANDIDATE sinyalleri yok; Adım 6 sentez yalnız Claude bulgularıyla işler.
> · **Adım 9** Claude-only → **commit ÜRETİLMEZ**; Adım 11 Şablon B1 raporlanır (review-gated invariant rapor seviyesinde de korunur).

````

- [ ] **Step 4: Byte-exact verification (drift contract garantisi — CRITICAL gate)**

Run:
```bash
diff <(awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' ~/.claude/commands/spec-claude-codex.md) \
     <(awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' ~/.claude/commands/simplify-claude-codex.md)
echo "Exit: $?"
```
Expected: `Exit: 0` (sıfır diff). FAIL → kopya bozuk, Task 3 baştan (snapshot'ı yeniden al).

- [ ] **Step 5: BEGIN/END marker unique count**

Run: `grep -c "CODEX-CALL-PROTOCOL:BEGIN\|CODEX-CALL-PROTOCOL:END" ~/.claude/commands/simplify-claude-codex.md`
Expected: `2` (1 BEGIN + 1 END; canonical bloğu 1 kez içeri).

- [ ] **Step 6: No commit**

---

## Task 4: Adım 1 (Scope + INITIAL_TREE_DIRTY) + Adım 2 (Test preflight) + Adım 3 (Claude scan 5 kategori)

**tdd: skip**

**Files:**
- Modify: `~/.claude/commands/simplify-claude-codex.md` (append after Codex Çağrı Protokolü)
- Read: `docs/specs/2026-05-31-simplify-claude-codex-command.md` (Adım 1, 2, 3 source-of-truth)

- [ ] **Step 1: Adım 1 (Scope Belirleme) bölümünü append**

Spec'in "Adım 1: Scope Belirleme" bölümünü (default sıralama 1-2-3, kapsam gösterimi, `<SCOPE_FILES>`, INITIAL_TREE_DIRTY flag bash bloğu, INITIAL_DIRTY_FILE_COUNT) **birebir** append et.

Source: `docs/specs/2026-05-31-simplify-claude-codex-command.md` — "Adım 1: Scope Belirleme" bölümü.

- [ ] **Step 2: Adım 2 (Test Suite Preflight) bölümünü append**

Spec'in "Adım 2: Test Suite Preflight" bölümünü (test komutu tespit kaynakları, test dosyası grep'i, TEST_SUITE_PRESENT=true/false dalları + 3 downstream etkisi) **birebir** append et.

- [ ] **Step 3: Adım 3 (Claude Ön Tarama) bölümünü append**

Spec'in "Adım 3: Claude Ön Tarama (5 Kategori)" bölümünü (A DRY, B YAGNI, C Naming, D File size, E Dead/debug + cross-file NOTED_EXTERNAL + aday min field listesi + canonical `<KATEGORI>-N` format örnekleri DRY-1/YAGNI-2/OTHER-1) **birebir** append et.

- [ ] **Step 4: Adım numaralandırma tutarlılık check**

Run: `grep -n "^## Adım [0-9]" ~/.claude/commands/simplify-claude-codex.md`
Expected: Adım 1, 2, 3 sıralı görünür.

- [ ] **Step 5: Canonical id format drift check**

Run:
```bash
grep -n "<candidate-id>\|<claude-id>" ~/.claude/commands/simplify-claude-codex.md
```
Expected: SIFIR (boş çıktı). Yalnız `<id>` canonical token kullanılır.

Run:
```bash
grep -n "DRY-1\|YAGNI-2\|OTHER-1\|<KATEGORI>-N" ~/.claude/commands/simplify-claude-codex.md
```
Expected: Adım 3'te canonical id format örnekleri görünür.

- [ ] **Step 6: No commit**

---

## Task 5: Adım 4 (Mode seçimi)

**tdd: skip**

**Files:**
- Modify: `~/.claude/commands/simplify-claude-codex.md`
- Read: `docs/specs/2026-05-31-simplify-claude-codex-command.md` (Adım 4 source-of-truth)

- [ ] **Step 1: Adım 4 bölümünü append**

Spec'in "Adım 4: Mode Seçimi" bölümünü (Standard Recommended / Light AskUserQuestion 2-seçenek + `<MODE>` saklama + final review her iki mode'da zorunlu vurgusu) **birebir** append et.

- [ ] **Step 2: AskUserQuestion semantiği check**

Run: `grep -A 3 "AskUserQuestion" ~/.claude/commands/simplify-claude-codex.md | head -10`
Expected: Standard (Recommended) ilk seçenek + Light ikinci olarak görünür.

- [ ] **Step 3: No commit**

---

## Task 6: Adım 4.5 — Log Dosyası Setup (AYRI Task; Codex'in kritik F6 düzeltmesi)

**tdd: skip**

**Files:**
- Modify: `~/.claude/commands/simplify-claude-codex.md`
- Read: `docs/specs/2026-05-31-simplify-claude-codex-command.md` (Adım 4.5 source-of-truth)

- [ ] **Step 1: Adım 4.5 bash setup bloğunu append**

Spec'in "Adım 4.5: Log Dosyası Setup" bölümünü **birebir** append et. İçerik:
- mkdir -p docs/reviews/codex
- DATE / LOG_DIR / LOG_PREFIX / ATTEMPT counter formülü
- ls $LOG_PREFIX-*.md 2>/dev/null | wc -l
- LOG_FILE composition
- if ATTEMPT > 1: previous-attempt link first line + ortak header (Scope/Mode/Initial tree state)
- else: ortak header (no previous-attempt link)
- `<LOG_FILE>` değişkenini Adım 5/9/10/11'in kullandığı not

- [ ] **Step 2: Bash bloğu syntax visual check**

Run: `grep -A 35 "## Adım 4.5" ~/.claude/commands/simplify-claude-codex.md | head -40`
Expected: mkdir + DATE + LOG_PREFIX + ATTEMPT formülü + LOG_FILE + ATTEMPT > 1 dalı + ortak header tam görünür.

- [ ] **Step 3: Adım 4.5'in Adım 4'ten sonra geldiği numaralandırma teyidi**

Run: `grep -n "^## Adım" ~/.claude/commands/simplify-claude-codex.md`
Expected: Adım 1, 2, 3, 4, 4.5 sıralı.

- [ ] **Step 4: No commit**

---

## Task 7: Adım 5 (Codex pre-scan hibrit prompt) + Adım 6 (Sentez Kural A-F)

**tdd: skip**

**Files:**
- Modify: `~/.claude/commands/simplify-claude-codex.md`
- Read: `docs/specs/2026-05-31-simplify-claude-codex-command.md` (Adım 5, 6 source-of-truth)

- [ ] **Step 1: Adım 5 (Codex Pre-scan) bölümünü append**

Spec'in "Adım 5: Codex Pre-scan (Yalnız Standard)" bölümünü **birebir** append et. İçerik:
- Light mode atlama notu
- CODEX-CALL-PROTOCOL ile `task --fresh` referansı
- Pre-scan Prompt Kuralı (Hibrit):
  - 5 kategori sınıflandırma + Other bucket
  - Canonical token format zorunlu açıklama (`<KATEGORI>-N`, `DRY-1` örneği)
  - DO_NOT_APPLY: `<id>` + reason + unless 3-satırlı format
  - Format ihlali → default block notu (Kural F'ye işaret)
  - CANDIDATE: unlisted:`<short-title>` + category + risk + rationale
  - DO_NOT_APPLY: unlisted:`<short-title>` (veto + bilinmeyen aday)
  - Max 5 aday + 5 veto + 5 unlisted CANDIDATE limiti
- Stdout verbatim + log append başlığı

- [ ] **Step 2: Adım 6 (Sentez) bölümünü append**

Spec'in "Adım 6: Sentez + Risk Yükseltme + Onay" bölümünü **birebir** append et. İçerik:
- Kural A: Eşleşme + onay
- Kural B: Codex DO_NOT_APPLY: `<id>` — canonical format zorunlu, high-risk-blocked, per-item explicit
- Kural C: Codex DO_NOT_APPLY: unlisted:... — bağımsız risk satırı, uygulanmaz
- Kural D: Codex CANDIDATE: unlisted:... — best-fit eşleme, risk sınıfı, normal onay döngüsü
- Kural E: Test-suite-yok override — default block + named override + toplu "continue anyway" yasak
- Kural F: Malformed/unknown id — default block + 3-seçenek AskUserQuestion (manuel eşle / bilgi göster uygulama / yoksay explicit)
- Risk sınıfı → onay döngüsü tablosu (low toplu / medium plan / high tek tek)
- Test rewrite scope (mekanik default + assertion/fixture/setup otomatik high-risk + per-item explicit)
- Sentez onayı konsolide rapor formatı

- [ ] **Step 3: Token canonical drift check**

Run:
```bash
grep -n "<candidate-id>\|<claude-id>" ~/.claude/commands/simplify-claude-codex.md
```
Expected: SIFIR. Yalnız `<id>` kullanılmalı.

- [ ] **Step 4: Kural F malformed-block presence check**

Run: `grep -n "Kural F\|Malformed\|malformed" ~/.claude/commands/simplify-claude-codex.md`
Expected: Kural F: Malformed veya Unknown `<id>` — Default Block bölümü görünür; 3-seçenek `AskUserQuestion` referansıyla.

- [ ] **Step 5: No commit**

---

## Task 8: Adım 7 (Fix uygulama scoped verification per batch) + Adım 8 (Final tests)

**tdd: skip**

**Files:**
- Modify: `~/.claude/commands/simplify-claude-codex.md`
- Read: `docs/specs/2026-05-31-simplify-claude-codex-command.md` (Adım 7, 8 source-of-truth)

- [ ] **Step 1: Adım 7 (Fix Uygulama) bölümünü append**

Spec'in "Adım 7: Fix Uygulama" bölümünü **birebir** append et. İçerik:
- Uygulama sırası: low → medium → high
- Per-sınıf akış (low toplu fix + mantıksal batch sonu scoped verification; medium plan sonrası scoped; high tek tek + scoped + per-onay)
- **Scoped verification ≠ full test suite** açıklaması (lint + format + test alt-kümesi etkilenen dosyalar için)
- FAIL davranışı (otomatik ilerleme YOK + 3 seçenek: undo+next / undo+stop / manuel düzelt)
- `<TEST_SUITE_PRESENT> = false` durumunda scoped "lint + format only" + PASS iddiası yasak
- FIXES_APPLIED counter (her uygulanan aday için sayıyı artır; low_applied_count + medium_applied_count + high_applied_count toplam = FIXES_APPLIED)
- Adım 7 sonu: tüm onaylanan uygulanmıştır veya explicit drop edilmiştir

- [ ] **Step 2: Adım 8 (Final Tests) bölümünü append**

Spec'in "Adım 8: Final Tests" bölümünü **birebir** append et. İçerik:
- Full/declared test suite taze çalıştırma
- PASS iddiası yalnız çıktı okunduktan sonra
- TEST_SUITE_PRESENT=false → atlanır + rapor "not-run (no test suite detected)"
- FAIL → Adım 7 sorun yönetimi modeline geri dön; Adım 9'a FAIL ile geçilmez

- [ ] **Step 3: FIXES_APPLIED counter tanımı görünür mü check**

Run: `grep -n "FIXES_APPLIED" ~/.claude/commands/simplify-claude-codex.md`
Expected: Adım 7'de counter tanımı, Adım 9'da gate'te kullanım.

- [ ] **Step 4: No commit**

---

## Task 9: Adım 9 (Codex final review + FIXES_APPLIED gate) + Adım 10 (Critical/high guard)

**tdd: skip; CRITICAL — F1 düzeltmesi içerir**

**Files:**
- Modify: `~/.claude/commands/simplify-claude-codex.md`
- Read: `docs/specs/2026-05-31-simplify-claude-codex-command.md` (Adım 9, 10 source-of-truth)

- [ ] **Step 1: Adım 9 (Codex Final Adversarial Review) bölümünü append**

Spec'in "Adım 9: Codex Final Adversarial Review (Zorunlu — koşullu skip)" bölümünü **birebir** append et. İçerik (KRİTİK SIRA):
- Pre-flight: FIXES_APPLIED Gate bash bloğu (ilk kontrol, scope hesabından ÖNCE):
  ```bash
  if [ "${FIXES_APPLIED:-0}" -eq 0 ]; then
    goto step_11_no_fixes_variant
  fi
  ```
- Gate açıklama (mevcut git status fallback yanlış pozitif vurgusu, operasyonel kararın simplify state'ine bağlı olduğu)
- Scope Hazırla (yalnız FIXES_APPLIED > 0 dalı) — SCOPE="--scope working-tree" default
- Pre-existing dirty + fixes-applied durumu (working-tree diff'i hem pre-existing hem simplify; rapor'da INITIAL_DIRTY_FILE_COUNT ayrı satır)
- Codex Final Review Çağrısı (CODEX-CALL-PROTOCOL ile)
- 8 maddelik prompt (semantic regression / real simplification / over-abstraction / public API / test sufficiency / referential integrity / complexity-pushed / new helper)
- Cross-file scope check (scope dışı dokunma + NOTED_EXTERNAL kontrolü)
- Stdout verbatim + log append başlığı (`<LOG_FILE>` path)
- Degradation davranışı (Claude-only → commit ÜRETİLMEZ → Adım 10 review-not-run dalı → Şablon B1)

- [ ] **Step 2: Adım 10 (Critical/High Guard) bölümünü append**

Spec'in "Adım 10: Critical/High Guard" bölümünü **birebir** append et. İçerik:
- Critical/high YOK dalı (Adım 11'e geç + opsiyonel Düzelt mini-batch)
- Critical/high VAR dalı 3 seçenek:
  - Düzelt → Adım 7'ye dön (mini-batch + Adım 8 + Adım 9 tekrar)
  - Risk kabulüyle override (Recommended değil):
    - Audit path: `docs/reviews/codex/<DATE>-simplify-<SCOPE_SLUG>-<ATTEMPT>.md` (F5 düzeltmesi — `<LOG_FILE>` aynı)
    - Commit mesajına override-note + path
    - Şablon A `Unresolved critical/high:` açık liste
    - `unresolved_high_severity_override: true`
  - Durdur → commit yok; Şablon B2; tüm uncommitted fix'ler working-tree'de
- Final Codex review çalışmadıysa (degradation) dalı (Codex'i tekrar dene / Durdur)

- [ ] **Step 3: Override audit path drift check**

Run: `grep -n "UNRESOLVED OVERRIDE\|override-note" ~/.claude/commands/simplify-claude-codex.md`
Expected: Audit path birebir `<DATE>-simplify-<SCOPE_SLUG>-<ATTEMPT>.md` (eski `-<SCOPE_SLUG>.md` yok).

- [ ] **Step 4: FIXES_APPLIED gate bash bloğu visual check**

Run: `grep -B 1 -A 5 "FIXES_APPLIED" ~/.claude/commands/simplify-claude-codex.md | head -15`
Expected: Adım 9 başında pre-flight gate görünür.

- [ ] **Step 5: No commit**

---

## Task 10: Adım 11 (Commit Gate + 3 Şablon test-suite-aware)

**tdd: skip; CRITICAL — F2/M2 sweep + F1 H2 fix + F3 path + F7 B1 sebep listesi**

**Files:**
- Modify: `~/.claude/commands/simplify-claude-codex.md`
- Read: `docs/specs/2026-05-31-simplify-claude-codex-command.md` (Adım 11 source-of-truth)

- [ ] **Step 1: Adım 11 (Commit Gate + Final Rapor) bölümünü append**

Spec'in "Adım 11: Commit Gate + Final Rapor" bölümünü **birebir** append et. İçerik:

**Commit Gate:**
- Şartlar AND (final tests PASS + Final Codex review approved|override)
- Onay sorusu + Conventional Commits refactor: prefix + push YOK

**Şablon A — Completed** (test-suite-aware verification — F2 düzeltmesi):
- Tüm satırlar (Scope, Mode, Test suite, Initial tree state, Adaylar sayım, Test-no override, Fixed inside scope, Noted external, Intentionally deferred, Verification test-suite-aware, Pre-scan/Final Codex review, override flag'leri, Unresolved critical/high, Codex review log path `<DATE>-...-<ATTEMPT>.md`, Sonraki adım /review)
- Verification satırı 2 dal: test_suite_present=true → "tests PASS/FAIL" + "Final tests: PASS"; false → "tests not-run" + "Final tests: not-run (no test suite)" + "PASS" kelimesi YASAK

**No-fixes-applied Edge Case Variant A + Variant B** (F1 H2 düzeltmesi):
- Variant A (initial clean + no fixes): "Final Codex review: not-run (no working-tree changes...)" + nothing to commit + /review önerisi
- Variant B (initial dirty + no fixes): "no simplification fixes applied; existing uncommitted changes unchanged" + INITIAL_DIRTY_FILE_COUNT pre-existing + Codex review SIMPLIFY ÇIKMADIĞINDAN GÖRMEDİ + kullanıcı pre-existing'i manuel ele alır

**Şablon B1 — review-not-run:**
- Sebep listesi: `degradation|companion-missing|timeout|user-stop-pre-scan|user-stop-synthesis|user-stop-after-test-fail` (F7 — son sebep eklendi)
- Final tests: 4 enum değer + PASS kuralı (F2 + F7 — ran-FAIL kaldırıldı)
- Previous Codex review log path `<DATE>-...-<ATTEMPT>.md` (F3)
- Sonraki adım: /simplify-claude-codex (run-from-scratch, "resume" DEĞİL — H3 düzeltmesi)

**Şablon B2 — review ran stopped:**
- Test suite: present | absent
- Final tests: test_suite_present=true PASS | false not-run (F2 sweep)
- Previous Codex review log path `<DATE>-...-<ATTEMPT>.md` (F3)
- Sonraki adım: /simplify-claude-codex (run-from-scratch)

**B1 / B2 / no-fixes B Çıkışlarında Sonraki Adım Kuralları:**
- ÖNERME: /review, /security-review, /finish-branch, /execute-plan-claude-codex
- YALNIZ ÖNER: /simplify-claude-codex (run-from-scratch + previous-attempt log link mekanizması)
- Şablon A'da ÖNER: /review

**`Unresolved critical/high:` Satırı Zorunlu** (5 senaryo için kural tablosu).

- [ ] **Step 2: PASS leak verification (M2 sweep tam)**

Run:
```bash
grep -B 2 -A 2 "Final tests: PASS" ~/.claude/commands/simplify-claude-codex.md
```
Expected: Her "PASS" yalnız `test_suite_present=true` koşullu satırda; hard-coded YOK. Şablon A + B2'de aynı disiplin.

- [ ] **Step 3: Şablon path consistency (F3 sweep tam)**

Run:
```bash
grep -n "docs/reviews/codex/<DATE>" ~/.claude/commands/simplify-claude-codex.md
```
Expected: Hepsi `<DATE>-simplify-<SCOPE_SLUG>-<ATTEMPT>.md` formatında; eksik `-<ATTEMPT>` yok.

- [ ] **Step 4: B1 sebep listesi check (F7 sweep tam)**

Run:
```bash
grep -n "user-stop-after-test-fail" ~/.claude/commands/simplify-claude-codex.md
```
Expected: B1 sebep listesinde görünür (en az 1 hit).

Run:
```bash
grep -n "ran-FAIL" ~/.claude/commands/simplify-claude-codex.md
```
Expected: SIFIR (B1'den çıkarıldı; Adım 7'de "FAIL → Adım 7 sorun yönetimi" yolu kalır).

- [ ] **Step 5: "resume" dili sweep (H3 sweep tam)**

Run:
```bash
grep -n "resume; review'a\|resume; düzelt\|(resume;" ~/.claude/commands/simplify-claude-codex.md
```
Expected: SIFIR (B1/B2'de "resume" yerine "run-from-scratch").

- [ ] **Step 6: No commit**

---

## Task 11: simplify-claude-codex — Korunan + Sözleşme Notları + Implementation Notes + Drift Sözleşmesi 4-way

**tdd: skip**

**Files:**
- Modify: `~/.claude/commands/simplify-claude-codex.md`
- Read: `docs/specs/2026-05-31-simplify-claude-codex-command.md` (ilgili 4 bölüm)

- [ ] **Step 1: "Mevcut simplify.md'den Korunan" bölümünü append**

Spec'in "Mevcut simplify.md'den Korunan" bölümünü **birebir** append et (5 kategori, 3 risk sınıflaması, test preflight, no-PASS-without-tests, no-push, /review).

- [ ] **Step 2: "Sözleşme Notları" bölümünü append**

Spec'in "Implementation Notes" + write-plan/execute-plan'ın Sözleşme Notları formatına paralel olarak yeni komut için Sözleşme Notları yaz. İçerik:
- **Manuel mod:** Her aşamada (Adım 1 scope onay, Adım 4 mode, Adım 6 sentez, Adım 7 high-risk per-item, Adım 10 guard, Adım 11 commit) kullanıcı kararı
- **Review-gated commit invariant:** simplify commit = full tests PASS (veya TEST_SUITE_PRESENT=false ile not-run notu) + final Codex review approved/override
- **Codex araç ayrımı:** Adım 5 `task --fresh` (read-only, pre-scan); Adım 9 `adversarial-review $SCOPE` (read-only sandbox hardcoded); foreground + dış `timeout 480s`
- **Companion path:** dinamik `find` (hardcoded sürüm yok)
- **Drift enforcement:** 4 komut listesi + Check A 4-way + Check B 8 token + "biri değişirse diğeri de" 4'ü sayar
- **Skill workflow override:** Simplify Superpowers backed değil; ama global skill chain (örn. /review auto-suggestion) ignore — manuel kullanıcı tetikler
- **Active task sahipliği:** Bu komut active layer'ı (TASK.md/HANDOFF.md/CURRENT.md) **hiç değiştirmez**; lifecycle yönetimi /execute-plan-claude-codex'in işidir
- **Codex read-only:** Codex hiçbir aşamada plan/spec/vault/active dosyası yazmaz; bulgu stdout, Claude `<LOG_FILE>` veya komut metnine işler
- **Vault promotion bu komutta YAPILMAZ** (/commit veya closure P1'e bırakılır)
- **Iteration-limit kavramı YOK** (execute-plan'la tutarlı; Adım 10 Düzelt döngüsü TDD-fix mini-batch, sayaç tutulmaz)

- [ ] **Step 3: Implementation Notes bölümünü append**

Spec'in "Implementation Notes" alt bölümlerini **birebir** append et:
- Boyut tahmini (~500 satır)
- CODEX-CALL-PROTOCOL bloğu canonical referans (spec-claude-codex'ten birebir kopyala)
- Log dosyası adı F3 formatı (mkdir + ATTEMPT + previous-attempt link + chain integrity)
- Resume davranışı YOK açıklama (sıfırdan başlar; previous-attempt log link mekanizması ile audit korunur; execute-plan'daki execute_start_ref yok)

- [ ] **Step 4: Drift Sözleşmesi 4-way bölümünü append**

Spec'in "Drift Sözleşmesi (4-way)" bölümünü **birebir** append et:
- 4 komut listesi (spec canonical + write-plan + execute + simplify)
- Check A 4-way: 3 diff (spec vs write-plan, spec vs execute, spec vs simplify); hepsi 0
- Check B tripwire 8 token (codex-companion.mjs, git rev-parse, AGENTS.md, timeout 480s, 124, "Claude-only devam et", "Tekrar dene", "Komutu durdur")
- "biri değişirse diğeri de" 4 komutu sayar

- [ ] **Step 5: Marker count final check (simplify-claude-codex)**

Run: `grep -c "CODEX-CALL-PROTOCOL:BEGIN\|CODEX-CALL-PROTOCOL:END" ~/.claude/commands/simplify-claude-codex.md`
Expected: `2`

- [ ] **Step 6: Toplam satır sayısı (spec tahmin aralığı)**

Run: `wc -l ~/.claude/commands/simplify-claude-codex.md`
Expected: ~450-550 satır.

- [ ] **Step 7: No commit**

---

## Task 11.5: Spec Section Diff Verification Matrix (F7 düzeltmesi — hard gate Task 12 öncesi)

**tdd: skip; CRITICAL — F2 + F7 birleşik gate; bireysel task'larda atlanan verification burada hard-stop ile yakalanır**

**Files:**
- Read: `docs/specs/2026-05-31-simplify-claude-codex-command.md` (source-of-truth)
- Read: `~/.claude/commands/simplify-claude-codex.md` (Task 2-11 sonucu)
- Write: `/tmp/spec-sections/*.txt`, `/tmp/cmd-sections/*.txt` (geçici)

Codex turn 2 F7 bulgusu: üst-blokta tarif edilen verification pattern bireysel task'larda hard-stop olarak invoke edilmiyordu. Bu task **konsolide gate** olarak Task 4-11'in append'lerini tek seferde diff'ler; herhangi bir bölümde anlamsal sapma (kural/format/sıra zorunluluk değişikliği) → hard stop + ilgili task'a rollback.

- [ ] **Step 1: Sed range matrix — her bölüm için spec'ten + komuttan extract**

Spec ve komut dosyasındaki Adım başlıklarını sed range ile çıkar; her bölüm ayrı dosyaya:

```bash
SPEC=docs/specs/2026-05-31-simplify-claude-codex-command.md
CMD=~/.claude/commands/simplify-claude-codex.md
mkdir -p /tmp/spec-sections /tmp/cmd-sections

# Adım range'leri (next Adım başlığına kadar; başlık dahil değil)
declare -A RANGES=(
  ["adim-1"]='/^## Adım 1:/,/^## Adım 2:/'
  ["adim-2"]='/^## Adım 2:/,/^## Adım 3:/'
  ["adim-3"]='/^## Adım 3:/,/^## Adım 4:/'
  ["adim-4"]='/^## Adım 4:/,/^## Adım 4\.5:/'
  ["adim-4_5"]='/^## Adım 4\.5:/,/^## Adım 5:/'
  ["adim-5"]='/^## Adım 5:/,/^## Adım 6:/'
  ["adim-6"]='/^## Adım 6:/,/^## Adım 7:/'
  ["adim-7"]='/^## Adım 7:/,/^## Adım 8:/'
  ["adim-8"]='/^## Adım 8:/,/^## Adım 9:/'
  ["adim-9"]='/^## Adım 9:/,/^## Adım 10:/'
  ["adim-10"]='/^## Adım 10:/,/^## Adım 11:/'
  ["adim-11"]='/^## Adım 11:/,/^## Mevcut /'
)

for key in "${!RANGES[@]}"; do
  range="${RANGES[$key]}"
  sed -n "${range}{/^## Adım/!{/^## Mevcut/!p}}" $SPEC > /tmp/spec-sections/$key.txt
  sed -n "${range}{/^## Adım/!{/^## Mevcut/!p}}" $CMD > /tmp/cmd-sections/$key.txt
done

ls -la /tmp/spec-sections /tmp/cmd-sections
```
Expected: Her dizinde 12 dosya (Adım 1-11 + 4.5); spec ve cmd dizinleri eşit dosya sayısına sahip.

- [ ] **Step 2: Per-section diff + manuel semantic inspect (F11 düzeltmesi — full diff, no truncation)**

Run:
```bash
mkdir -p /tmp/section-diffs
> /tmp/section-diffs/_accept-reject-log.txt

for key in adim-1 adim-2 adim-3 adim-4 adim-4_5 adim-5 adim-6 adim-7 adim-8 adim-9 adim-10 adim-11; do
  echo "=== $key ===" | tee -a /tmp/section-diffs/_accept-reject-log.txt
  diff /tmp/spec-sections/$key.txt /tmp/cmd-sections/$key.txt > /tmp/section-diffs/$key.diff
  size=$(wc -l < /tmp/section-diffs/$key.diff)
  echo "diff size: $size lines (full content: /tmp/section-diffs/$key.diff)"
done

# Diff dosyalarını tek tek manuel oku — head TRUNCATION YOK
echo ""
echo "Manuel review checklist:"
ls /tmp/section-diffs/*.diff | while read f; do echo "- [ ] $(basename $f)"; done
```

**Manuel inspect protokolü:**
1. Her `/tmp/section-diffs/<key>.diff` dosyasını TAMAMEN oku (`less` veya `cat`; `head` YASAK)
2. Diff size > 200 satır ise özellikle dikkat — büyük drift sinyali
3. Her bölüm için aşağıdaki tabloyu doldur (`/tmp/section-diffs/_accept-reject-log.txt`'ye append):

```
adim-1: accept | reject (sebep: <kısa açıklama>)
adim-2: accept | reject (...)
...
adim-11: accept | reject (...)
```

Tüm bölümler accept ise Step 3'e (Step 3 OK dalı). Herhangi biri reject ise Step 3 hard stop dalı.

**Kabul edilebilir farklar:**
- Self-referans terminoloji yumuşatma (`spec'in Adım X prompt'u` → `Adım X prompt'u`)
- Plan-bazlı düzeltme referansı not (örn. "F1 düzeltmesi", "F5 düzeltmesi") — eğer komuta eklendiyse
- Path örnekleri (örn. log path örnekleri spec'te `<DATE>` placeholder, komutta concrete)

**Hard stop — kabul edilemez farklar:**
- Kural eksikliği (Kural F yok, KURAL B canonical token açıklaması yok, vb.)
- Sıra değişikliği (Adım 9 FIXES_APPLIED gate scope hesabından SONRA gelirse — F1 H2 fix bozulur)
- Format zorunluluk değişikliği (DO_NOT_APPLY token format gevşemesi)
- Anlamsal paraphrase (örn. "default block" → "user warning")

Manuel inspect: her bölüm için kabul/red kararı; reddedilen bölümler için ilgili task (`adim-N` → Task M mapping aşağıda) rollback edilir.

**Task mapping (rollback için):**
- adim-1, adim-2, adim-3 → Task 4
- adim-4 → Task 5
- adim-4_5 → Task 6
- adim-5, adim-6 → Task 7
- adim-7, adim-8 → Task 8
- adim-9, adim-10 → Task 9
- adim-11 → Task 10

- [ ] **Step 3: Hard stop — rebuild-from-clean semantik (F10 düzeltmesi)**

**Problem:** Tasks 4-11 hepsi `~/.claude/commands/simplify-claude-codex.md`'ye append yapıyor; Task 1 Step 7 backup'ı yalnız mevcut 4 dosyayı yedekledi (yeni dosyanın eski hâli YOK). Per-section rollback imkansız; rebuild-from-clean tek yol.

**Recovery — explicit replay listesi:**

Step 2 manuel inspect bir veya birden fazla bölümü reddederse:

```bash
# 1. Kirli dosyayı sil — clean state'e dön
rm ~/.claude/commands/simplify-claude-codex.md
echo "Task 11.5 BLOCKED — rebuild required"

# 2. Hangi task'ların yeniden koşulması gerektiğini hesapla:
# adim-N reddedildi → Task mapping'inden Task M'i bul
# Task M ve M sonrası TÜM task'lar yeniden koşulur (cascade rebuild)
# Yeniden koş listesi:
#   Task 2 (iskelet + frontmatter) — her zaman ilk
#   Task 3 (canonical block)
#   Task 4 → Task 11 (sırayla, hepsi)
# Aslında: Task 2-11 zinciri yeniden koşulur (clean rebuild)

exit 1
```

**Replay matrix (FAIL bölümü → minimum replay başlangıcı):**

| Reddedilen adim | Affected Task | Replay başlangıcı |
|---|---|---|
| adim-1 | Task 4 | Task 2 (rebuild from clean) |
| adim-2 | Task 4 | Task 2 |
| adim-3 | Task 4 | Task 2 |
| adim-4 | Task 5 | Task 2 |
| adim-4_5 | Task 6 | Task 2 |
| adim-5 / adim-6 | Task 7 | Task 2 |
| adim-7 / adim-8 | Task 8 | Task 2 |
| adim-9 / adim-10 | Task 9 | Task 2 |
| adim-11 | Task 10 | Task 2 |

Tüm cases'te replay = Task 2'den itibaren clean rebuild. Cascade kabul; kompleks per-section snapshot maliyeti kabul edilmedi (Codex turn 3 önerisinden seçim).

Hiçbir bölüm reddedilmediyse: `echo "Spec section diff verification: ALL OK"` + Task 12'ye devam.

- [ ] **Step 4: No commit**

---

## Task 12: 3 Ayna Komut — Sözleşme Notları Dosyaya Özgü Stale-Text Düzeltme

**tdd: skip; CRITICAL — 3 dosyada AYRI metinler var (Codex'in "stale numerals catalog" uyarısı)**

**Files:**
- Modify: `~/.claude/commands/spec-claude-codex.md` (binding + Sözleşme Notları drift section)
- Modify: `~/.claude/commands/write-plan-claude-codex.md` (Sözleşme Notları drift section)
- Modify: `~/.claude/commands/execute-plan-claude-codex.md` (Sözleşme Notları drift section)

Source for changes: Task 1 Step 4 inventory'sinin katalog çıktısı. Her dosyada **mevcut numeral** (1/2/3) → **4** olarak güncellenir, drift-check Check A directional → 4-way.

- [ ] **Step 0: Catalog hard-stop gate (F3 düzeltmesi)**

Task 1 Step 4 inventory'sini tekrar koş ve doğrula (hard-stop):

```bash
echo "=== spec catalog ==="
spec_hits=$(grep -c "biri değişirse\|write-plan-claude-codex.*ile\|drift\|Check A\|Check B" ~/.claude/commands/spec-claude-codex.md)
echo "hits: $spec_hits"

echo "=== write-plan catalog ==="
wp_hits=$(grep -c "biri değişirse\|iki komut\|drift\|Check A\|Check B" ~/.claude/commands/write-plan-claude-codex.md)
echo "hits: $wp_hits"

echo "=== execute-plan catalog ==="
ep_hits=$(grep -c "biri değişirse\|üç komut\|3-way\|drift\|Check A\|Check B" ~/.claude/commands/execute-plan-claude-codex.md)
echo "hits: $ep_hits"

# Hard stop: her dosyada en az 1 hit gerek
if [ "$spec_hits" -eq 0 ] || [ "$wp_hits" -eq 0 ] || [ "$ep_hits" -eq 0 ]; then
  echo "CATALOG EMPTY in one or more files — STOP. Re-inspect manually before Task 12."
  exit 1
fi
echo "CATALOG OK — proceed to Step 1"
```
Expected: `CATALOG OK`. Catalog boşsa veya beklenen pattern eksikse Task 12 baştan başlamaz; manuel inspect + plan'ı update et (catalog beklenmedik formatta).

- [ ] **Step 1: spec-claude-codex.md güncellemesi**

Binding satırında (canonical block ÖNCE):
- Mevcut: "...; `/write-plan-claude-codex` ile birebir aynıdır (drift-check: diff=0)"
- Yeni: "...; `/write-plan-claude-codex`, `/execute-plan-claude-codex`, `/simplify-claude-codex` ile birebir aynıdır (drift-check 4-way: 3 diff'in hepsi 0)"

Sözleşme Notları "Drift enforcement" bölümünde:
- Mevcut: "Protokol bloğu iki komutta birebir." benzeri → "Protokol bloğu **dört komutta** birebir: spec-claude-codex (canonical), write-plan-claude-codex (ayna), execute-plan-claude-codex (ayna), simplify-claude-codex (ayna)."
- "Check A (directional)" → "Check A (4-way): spec vs write-plan diff=0 AND spec vs execute diff=0 AND spec vs simplify diff=0"
- Tripwire token listesi aynı kalır (8 token); açıkça **dört dosyada** mevcut olmalı vurgusu
- "biri değişirse diğeri de" — açıklamada 4 komutu sayar (spec, write-plan, execute, simplify)

Edit komutu: `Edit` tool ile mevcut metni bul + dosyaya özgü yeni metinle değiştir (Task 1 Step 4 inventory katalog'undan exact match string'i al).

- [ ] **Step 2: write-plan-claude-codex.md güncellemesi**

Binding ve Sözleşme Notları'nda mevcut "iki komut" benzeri ifadeler → "**dört komutta** birebir; spec canonical, write-plan + execute-plan + simplify ayna".

Check A directional → 4-way (3 diff). Tripwire 8 token. "biri değişirse diğeri de" 4'ü sayar.

Edit komutu: aynı mantık, dosyaya özgü exact match.

- [ ] **Step 3: execute-plan-claude-codex.md güncellemesi**

Sözleşme Notları "Drift enforcement (canonical = spec-claude-codex):" bölümünde mevcut "**üç komutta** birebir: spec-claude-codex (canonical), write-plan-claude-codex (ayna), execute-plan-claude-codex (ayna)." → "**dört komutta** birebir: + simplify-claude-codex (ayna)".

"Check A 3-way" → "Check A 4-way": eklenen `AND spec vs simplify diff=0`.

Tripwire 8 token vurgusu (listede zaten var). "biri değişirse diğeri de" — 4 komutu sayar.

Edit komutu: aynı.

- [ ] **Step 4: Drift block invariance verification (F6 + F8 düzeltmeleri — marker count guard + inline recompute)**

Snapshot dosyasına bağlanmak yerine spec doğrudan referans, marker count guard her awk öncesi:

Run:
```bash
SPEC=~/.claude/commands/spec-claude-codex.md

# F8 guard: tüm karşılaştırılan dosyalarda marker count = 2
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex; do
  m=$(grep -c "CODEX-CALL-PROTOCOL:BEGIN\|CODEX-CALL-PROTOCOL:END" ~/.claude/commands/$f.md)
  if [ "$m" -ne 2 ]; then
    echo "FAIL — $f marker count $m (expected 2). Marker integrity bozuk; Task 12 baştan."
    exit 1
  fi
done
echo "Marker guard OK"

# Recompute + diff
for f in write-plan-claude-codex execute-plan-claude-codex; do
  diff <(awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' $SPEC) \
       <(awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' ~/.claude/commands/$f.md)
  echo "spec vs $f exit: $?"
done
```
Expected: `Marker guard OK` + 2 satır `exit: 0`.

- [ ] **Step 5: 4-way "biri değişirse" sweep (4 komut adı her dosyada görünmeli)**

Run:
```bash
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex; do
  echo "--- $f ---"
  grep -n "simplify-claude-codex" ~/.claude/commands/$f.md | head -5
done
```
Expected: Her dosyada en az 1 hit (drift section "+simplify" referansı).

- [ ] **Step 6: Negatif sweep — stale terimler KALMAMALI (F3 düzeltmesi)**

Run:
```bash
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex; do
  echo "--- $f stale check ---"
  # Stale numerals
  grep -n "iki komut\|üç komut\|3-way\|directional" ~/.claude/commands/$f.md && echo "STALE HIT in $f" || true
done
```
Expected: SIFIR `STALE HIT` satırı. Stale terim varsa Step 1-3 eksik kaldı; rollback (`cp /tmp/$f.md.bak ~/.claude/commands/$f.md`) + tekrar dene.

- [ ] **Step 7: No commit**

---

## Task 13: execute-plan-claude-codex.md — `/simplify` Reference Sweep MANUEL HIT-BY-HIT

**tdd: skip; CRITICAL — blind sed YASAK, her hit ayrı classify**

**Files:**
- Modify: `~/.claude/commands/execute-plan-claude-codex.md` (only active next-step references)

- [ ] **Step 1: Hit listesi taze grep + sabit referans tablosu (F4 düzeltmesi — line numara'lı)**

Run: `grep -n "/simplify" ~/.claude/commands/execute-plan-claude-codex.md`

**Plan yazıldığı anda (2026-05-31) tespit edilen 7 hit (whitelist BOŞ — hepsi active, hepsi `/simplify-claude-codex`'e çevrilecek):**

| Line (yaklaşık) | Bağlam | Aksiyon |
|---|---|---|
| ~29 | Akış genel bakış "16. Koşullu final/draft rapor (approved → /simplify; ...)" | → `/simplify-claude-codex` |
| ~262 | "`/simplify` önerisi yalnız Adım 16 Şablon A raporda görünür" | → `/simplify-claude-codex` |
| ~708 | HANDOFF Notes For Claude template "next: /simplify → /review → /security-review" | → `/simplify-claude-codex` |
| ~759 | Şablon A "Sonraki adım: /simplify  (sonra /review, /security-review, closure)" | → `/simplify-claude-codex` |
| ~841 | "B1 / B2a / B2b'de ÖNERME: `/simplify`, `/review`, ..." | → `/simplify-claude-codex` |
| ~843 | "Şablon A'da ÖNER: `/simplify` (sonra zincir ...)" | → `/simplify-claude-codex` |
| ~921 | Skill workflow override "Auto `/review`, `/security-review`, `/finish-branch`, `/simplify`, push — **YOK**" | → `/simplify-claude-codex` |

**Whitelist (DOKUNULMAYACAK historical/decisions-log hit'leri):** **BOŞ.** Tüm 7 hit active (kullanıcının göreceği akış/sözleşme metinleri). Decisions log / archive history içinde `/simplify` yok (Task 1 Step 5 sonucu).

**Line numara'lar yaklaşık** (refine sırasında dosya satır sayısı değişebilir); Step 2'de her hit context-unique edit ile yapılır, line numara değil bağlam string'i ile.

Hit sayısı doğrulama:
```bash
hit_count=$(grep -c "/simplify[^-]" ~/.claude/commands/execute-plan-claude-codex.md)
echo "current /simplify hits: $hit_count"
```
Expected: 7 (plan yazıldığı andaki sayı). Sapma varsa (8+ veya 6-): tablo güncel değil, Task 1 Step 5 inventory'sini yeniden koş + tabloyu plan'da update et.

- [ ] **Step 2: Her active hit için ayrı Edit komutu**

Her active reference için `Edit` tool ile unique context replace_all=false:

Örnek edit 1 (Şablon A son satır):
```
old_string: "- Sonraki adım: /simplify  (sonra /review, /security-review, closure)"
new_string: "- Sonraki adım: /simplify-claude-codex  (sonra /review, /security-review, closure)"
```

Örnek edit 2 (Skill workflow override listesi):
```
old_string: "Auto `/review`, `/security-review`, `/finish-branch`, `/simplify`, push — **YOK**"
new_string: "Auto `/review`, `/security-review`, `/finish-branch`, `/simplify-claude-codex`, push — **YOK**"
```

Inventory'deki diğer hit'lere göre Edit komutları eklenir.

- [ ] **Step 3: Sweep sonrası verification — non-whitelisted `/simplify` hit'i FAIL (F4 düzeltmesi)**

Whitelist BOŞ olduğundan: hiçbir `/simplify` (`/simplify-` olmayan) hit kabul edilemez.

Run:
```bash
remaining=$(grep -c "/simplify[^-]" ~/.claude/commands/execute-plan-claude-codex.md)
echo "remaining /simplify hits: $remaining"
if [ "$remaining" -ne 0 ]; then
  echo "FAIL — Task 13 incomplete; non-whitelisted hits exist:"
  grep -n "/simplify[^-]" ~/.claude/commands/execute-plan-claude-codex.md
  exit 1
fi
echo "Step 3 OK — all 7 hits converted"
```
Expected: `Step 3 OK`. FAIL → Step 2 eksik kaldı; rollback (`cp /tmp/execute-plan-claude-codex.md.bak ~/.claude/commands/execute-plan-claude-codex.md`) + tekrar dene.

- [ ] **Step 4: simplify-claude-codex referans pozitif sweep**

Run: `grep -n "/simplify-claude-codex" ~/.claude/commands/execute-plan-claude-codex.md`
Expected: En az 2 hit (Şablon A + Skill workflow override; inventory'ye göre artabilir).

- [ ] **Step 5: No commit**

---

## Task 14: simplify.md → DEPRECATED Stub (EN SON — Codex'in sıra önerisi)

**tdd: skip**

**Files:**
- Modify (overwrite): `~/.claude/commands/simplify.md`

- [ ] **Step 1: Eski içeriğin son okuması (kayıt için)**

Run: `head -10 ~/.claude/commands/simplify.md`
Expected: Mevcut description + Görev satırı görünür (referans için son okuma).

- [ ] **Step 2: Stub içeriğine overwrite**

Write to `~/.claude/commands/simplify.md`:

```markdown
---
description: [DEPRECATED] use /simplify-claude-codex
---

Bu komut `/simplify-claude-codex` ile değiştirildi (Codex pre-scan + final adversarial review + commit gate; review-gated invariant).

**Neden değişti:** Tek-aktörlü Claude scan + Claude fix modeli, claude-codex aile mimarisi (spec/write-plan/execute-plan) yanında tutarsızdı; refactor disiplini Codex adversarial review olmadan eksikti. Yeni komut aile pattern'ına entegre, drift-check 4-way contract'a tabi.

**Kullanım:** `/simplify-claude-codex [SCOPE]` (boş scope: working-tree veya origin/main..HEAD).
```

- [ ] **Step 3: Stub kontrol**

Run: `wc -l ~/.claude/commands/simplify.md && head -10 ~/.claude/commands/simplify.md`
Expected: ~10 satır stub; description "[DEPRECATED]" ile başlar.

- [ ] **Step 4: No commit**

---

## Task 15: Drift Verification + Smoke + Final Audit Commit (REPO ONLY)

**tdd: skip; FINAL VERIFICATION — drift contract'ı validate eder + repo audit log commit'i**

**Önemli (F1 düzeltmesi):** `~/.claude/commands/*.md` dosyaları **bu repo'nun DIŞINDA** (global). Bu task'ta `git add ~/.claude/commands/...` YASAK — çalışmaz. Repo commit'i yalnız audit log (`docs/plans/` + `docs/reviews/codex/`) için yapılır. Global komut dosyaları **kullanıcının manual install/restart**'ıyla aktif olur; backup'lar `/tmp/*.bak`'ta tutulur, rollback gerekirse oradan geri yüklenir.

**Files:**
- Global (NOT committed; backup'lı install): `~/.claude/commands/simplify-claude-codex.md` (new), `~/.claude/commands/simplify.md` (stub), `~/.claude/commands/spec-claude-codex.md` (modified), `~/.claude/commands/write-plan-claude-codex.md` (modified), `~/.claude/commands/execute-plan-claude-codex.md` (modified)
- Repo audit (committed): `docs/plans/2026-05-31-simplify-claude-codex-command.md`, `docs/reviews/codex/2026-05-31-simplify-claude-codex-command-plan.md`

- [ ] **Step 1: Check A 4-way (3 diff hepsi 0; F8 düzeltmesi — marker guard önce)**

Run:
```bash
SPEC=~/.claude/commands/spec-claude-codex.md

# F8 guard: 4 dosyanın hepsinde marker count = 2
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex; do
  m=$(grep -c "CODEX-CALL-PROTOCOL:BEGIN\|CODEX-CALL-PROTOCOL:END" ~/.claude/commands/$f.md)
  if [ "$m" -ne 2 ]; then
    echo "FAIL — $f marker count $m (expected 2). Check A invalid."
    exit 1
  fi
done
echo "Marker guard OK"

# Check A 4-way
for target in write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex; do
  diff <(awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' $SPEC) \
       <(awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' ~/.claude/commands/$target.md)
  echo "spec vs $target exit: $?"
done
```
Expected: `Marker guard OK` + 3 satır `exit: 0`. FAIL → ilgili dosyada canonical block kirli; Task 3 (simplify) veya Task 12 (3 ayna) yeniden çalıştır.

- [ ] **Step 2: Check B 8 tripwire token (her 4 dosyada >= 1)**

Run:
```bash
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex; do
  block=$(awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' ~/.claude/commands/$f.md)
  for token in "codex-companion.mjs" "git rev-parse" "AGENTS.md" "timeout 480s" "124" "Claude-only devam et" "Tekrar dene" "Komutu durdur"; do
    count=$(echo "$block" | grep -c -F "$token")
    [ "$count" -ge 1 ] || echo "MISSING in $f: $token"
  done
done
```
Expected: SIFIR `MISSING` satırı.

- [ ] **Step 3: Structural integrity check**

Run:
```bash
# Frontmatter check (simplify-claude-codex)
head -5 ~/.claude/commands/simplify-claude-codex.md
echo "---"
# BEGIN/END marker count per file
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex; do
  count=$(grep -c "CODEX-CALL-PROTOCOL:BEGIN\|CODEX-CALL-PROTOCOL:END" ~/.claude/commands/$f.md)
  echo "$f markers: $count"
done
```
Expected: simplify-claude-codex.md frontmatter `description` + `argument-hint` ile başlar; her dosya `markers: 2`.

- [ ] **Step 4: Adım numaralandırma tutarlılığı (simplify-claude-codex)**

Run: `grep -n "^## Adım" ~/.claude/commands/simplify-claude-codex.md`
Expected: Adım 1, 2, 3, 4, 4.5, 5, 6, 7, 8, 9, 10, 11 sıralı (12 başlık).

- [ ] **Step 5: Canonical `<id>` token tutarlılığı (simplify-claude-codex)**

Run:
```bash
grep -n "<candidate-id>\|<claude-id>" ~/.claude/commands/simplify-claude-codex.md
```
Expected: SIFIR (drift YOK; yalnız `<id>` canonical).

- [ ] **Step 6: PASS leak final sweep (test-suite-aware Final tests)**

Run:
```bash
grep -B 1 -A 2 "Final tests:" ~/.claude/commands/simplify-claude-codex.md
```
Manuel inspect: her "PASS" yalnız `test_suite_present=true` koşullu satırda mı (Şablon A + B1 + B2 hepsinde)?

- [ ] **Step 7: `/simplify` reference sweep verification (execute-plan)**

Run:
```bash
grep -cn "/simplify[^-]" ~/.claude/commands/execute-plan-claude-codex.md
grep -cn "/simplify-claude-codex" ~/.claude/commands/execute-plan-claude-codex.md
```
Expected:
- İlk grep: SIFIR active hit (yalnız historical varsa kalır)
- İkinci grep: >= 2 hit (Şablon A + Sözleşme Notları)

- [ ] **Step 8: Smoke verification — 3-state (F5 düzeltmesi)**

Smoke 3 state, FAIL kabul edilmez:

- **not-run:** Slash command runtime mevcut DEĞİL (örn. Claude Code restart yapılamadı). Yalnız structural verification (Step 1-7) yeterli; Step 9 commit'e geç.
- **pass:** Runtime mevcut, `/simplify-claude-codex` çağrıldı, Adım 1 scope sorması göründü (en azından komut yüklendi + frontmatter parse ediliyor). Step 9 commit'e geç.
- **fail:** Runtime mevcut, ama `/simplify-claude-codex` çağrıldığında hata (komut tanınmıyor / parse error / immediate crash). **Step 9 BLOK** — Task 2-14'te hata var; ilgili task'a dön, fix uygula, tekrar dene. Eğer mecbur "ship it as-is" denirse: kullanıcı **explicit override** verir + Step 9 commit mesajına `smoke: fail (override: <gerekçe>)` satırı + audit log'a UNRESOLVED OVERRIDE.

Smoke sonucu shell variable olarak sakla (F9 düzeltmesi — Step 9 commit mesajında variable substitution + placeholder guard):

```bash
# Smoke state'i shell variable olarak set et (executor manuel doldurur):
SMOKE_STATE="not-run"   # veya "pass" veya "fail-override-<gerekçe>"
echo "SMOKE_STATE=$SMOKE_STATE"
```

Step 9'da bu variable commit mesajına embed edilir + placeholder güvenliği için post-check.

- [ ] **Step 9: Repo audit log commit (yalnız docs/; F9 düzeltmesi — SMOKE_STATE binding + placeholder guard)**

**F1 düzeltmesi:** `~/.claude/commands/*.md` repo dışında — bu task'ta `git add ~/.claude/commands/...` YOK. Repo commit'i yalnız audit log için:

Run:
```bash
git status --short
```
Expected: `docs/plans/2026-05-31-simplify-claude-codex-command.md` (?? untracked) + `docs/reviews/codex/2026-05-31-simplify-claude-codex-command-plan.md` (?? untracked) + `docs/specs/2026-05-31-simplify-claude-codex-command.md` (zaten Adım 11 spec onayında değişmiş, untracked olabilir).

Run:
```bash
git add docs/plans/2026-05-31-simplify-claude-codex-command.md \
        docs/reviews/codex/2026-05-31-simplify-claude-codex-command-plan.md \
        docs/reviews/codex/2026-05-31-simplify-claude-codex-command.md \
        docs/specs/2026-05-31-simplify-claude-codex-command.md
git status
```
Expected: 4 dosya staged (varsa).

**F12 düzeltmesi — tek geçit commit flow (literal-placeholder commit bloğu kaldırıldı):**

Önce `${SMOKE_STATE}` substitution ile `COMMIT_BODY` kur, validate et, sonra commit:

```bash
# 1) Commit body'yi shell variable substitution ile inşa et (literal placeholder YOK)
COMMIT_BODY=$(cat <<EOF
docs(simplify-claude-codex): add spec, plan, and codex review logs

Spec (3 Codex turn + 13 targeted fix → spec-approved):
- docs/specs/2026-05-31-simplify-claude-codex-command.md
- docs/reviews/codex/2026-05-31-simplify-claude-codex-command.md

Plan (write-plan-claude-codex flow → plan-approved):
- docs/plans/2026-05-31-simplify-claude-codex-command.md
- docs/reviews/codex/2026-05-31-simplify-claude-codex-command-plan.md

Implementation files (NOT in this commit — outside repo):
- ~/.claude/commands/simplify-claude-codex.md (new)
- ~/.claude/commands/simplify.md (DEPRECATED stub)
- ~/.claude/commands/spec-claude-codex.md (drift 4-way update)
- ~/.claude/commands/write-plan-claude-codex.md (drift 4-way update)
- ~/.claude/commands/execute-plan-claude-codex.md (drift 4-way update + /simplify sweep)

Backups: /tmp/<name>.md.bak (rollback için; Task 1 Step 7 + Task 11.5 rebuild-from-clean)

Drift verification:
- Check A 4-way diff=0 (spec vs write-plan, spec vs execute, spec vs simplify)
- Check B tripwire 8 token presence in all 4 files
- BEGIN/END marker count: 2 per file (Task 12 Step 4 + Task 15 Step 1 marker guards)
- Structural integrity: frontmatter parses, Adım numbering sequential
- Canonical \`<id>\` token consistent
- Spec section diff (Task 11.5): ALL OK

Smoke runtime: ${SMOKE_STATE}

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>
EOF
)

# 2) Pre-commit guard — placeholder/unresolved string KALMAMALI
if echo "$COMMIT_BODY" | grep -qE "__SMOKE_STATE_PLACEHOLDER__|<not-run\\s*\\||<pass\\s*\\||<fail-override"; then
  echo "FAIL — placeholder unresolved in COMMIT_BODY; commit YAPMA"
  echo "$COMMIT_BODY" | grep -E "__SMOKE_STATE_PLACEHOLDER__|<not-run|<pass|<fail-override"
  exit 1
fi

if [ -z "$SMOKE_STATE" ]; then
  echo "FAIL — SMOKE_STATE variable boş; Step 8'i tamamla, sonra Step 9'a dön"
  exit 1
fi
echo "Pre-commit guard OK; SMOKE_STATE=$SMOKE_STATE"

# 3) Tek commit
git commit -m "$COMMIT_BODY"

# 4) Post-commit guard — commit message'da sorun var mı?
if git log -1 --format=%B | grep -qE "__SMOKE_STATE_PLACEHOLDER__|<not-run\\s*\\||<pass\\s*\\||<fail-override"; then
  echo "FAIL — commit message contains unresolved placeholder."
  echo "Recovery: git commit --amend ile düzelt."
  exit 1
fi
echo "Step 9 OK — audit commit created with SMOKE_STATE=$SMOKE_STATE"
```

Bu flow yalnız tek `git commit` üretir, `${SMOKE_STATE}` substitution garantili, double-guard (pre + post).

- [ ] **Step 10: Commit verification**

Run: `git log -1 --stat`
Expected: 4 dosya commit'li (docs/ only); `~/.claude/commands/` PATH YOK (repo dışı).

- [ ] **Step 11: Global komut dosyaları kullanıcıya bilgi**

Step 9 commit'i **audit log**; gerçek slash command kullanımı için kullanıcı:
1. Claude Code restart eder (yeni komut dosyaları taranır)
2. `/simplify-claude-codex` slash command'ı slash menüsünde görünür
3. Backup'lar (`/tmp/*.bak`) — rollback gerekirse `cp /tmp/X.bak ~/.claude/commands/X`

Push YAPMA — kullanıcı manuel push veya `/finish-branch` ile zinciri kapatır.

---

## Self-Review Notları

**Toplam task sayısı:** 16 (Task 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 11.5, 12, 13, 14, 15).

**Spec coverage check:**
- Akış 11 adım + Adım 4.5 → Task 2-10
- Mevcut /simplify'dan korunan → Task 11 Step 1
- Sözleşme Notları + Implementation Notes + Drift Sözleşmesi 4-way → Task 11 Step 2-4
- Spec section diff verification gate (F7) → Task 11.5
- 3 ayna komut drift-check güncellemesi → Task 12 (catalog hard-stop + negatif sweep F3 dahil)
- execute-plan /simplify sweep manuel hit-by-hit + line-table (F4) → Task 13
- simplify.md DEPRECATED stub → Task 14
- Check A 4-way + Check B 8 token verification + marker guards (F8) → Task 15 Step 1-2
- Structural + canonical token + PASS leak sweep'leri → Task 15 Step 3-6
- Smoke 3-state (F5: not-run/pass/fail-override) → Task 15 Step 8
- Audit commit (yalnız docs/; ~/.claude/commands repo dışı, F1) + SMOKE_STATE variable substitution + placeholder guard (F9/F12) → Task 15 Step 9
- Global komut dosyaları manual install (restart sonrası), backup'lar /tmp'de (F1) → Task 15 Step 11

**Placeholder scan:**
- "Spec'in Adım N bölümünü birebir append et" — placeholder DEĞİL, **kaynak attribution**; executor source-of-truth spec dosyasını okur, drift riskini düşürür (spec değişirse plan da revize edilir). Writing-plans "no placeholders" kuralı TBD/TODO/"similar to Task N" gibi belirsizlik kastediyor; bu açık kaynak referansıdır.
- Tüm bash blokları + verification command'ları + Edit örnek string'leri tam içerikle yazılmış.
- "Tipik" yerine "beklenen Task 1 Step 5 inventory'siyle eşleşmeli" gibi cross-reference verildi.

**Type/method/path consistency:**
- Canonical `<id>` token (örn. `DRY-1`) Task 4 + Task 7 + Task 10'da tutarlı.
- Log dosyası path `<DATE>-simplify-<SCOPE_SLUG>-<ATTEMPT>.md` Task 6 + Task 9 + Task 10'da tutarlı.
- `FIXES_APPLIED` counter Task 8 (tanım) + Task 9 (gate) tutarlı.
- `INITIAL_TREE_DIRTY` flag Task 4 (tanım) + Task 10 (Variant A/B rapor) tutarlı.
- `<LOG_FILE>` değişkeni Task 6 (setup) + Task 9 (Codex log append) + Task 10 (rapor path) tutarlı.

**Risk reminder:**
- R1 drift: Task 3 Step 4 (byte-exact verification) + Task 15 Step 1 (Check A 4-way) iki kez koşulur. İlk pass Task 3 sonrası "early fail-fast", ikinci Task 15 final. Marker count guard her awk recompute öncesi (F8).
- R2 sweep: Task 13 hit-by-hit + Task 15 Step 7 verification; sabit line-numara tablo (F4); whitelist boş. Blind sed yok.
- R3 smoke: Task 15 Step 8 3-state (F5); fail durumunda commit BLOK + override path; runtime mevcutsa pass/fail kesin; mevcut değilse not-run kabul.
- R4 (F1) commit modeli: Audit commit yalnız docs/; ~/.claude/commands/ global, manual install + backup-rollback. `git add ~/.claude/commands/...` YOK.
- R5 (F7) spec append drift: Task 11.5 konsolide section diff matrix + full diff (no truncation F11) + manuel accept/reject log + rebuild-from-clean rollback (F10).
- R6 (F9/F12) audit commit integrity: SMOKE_STATE variable substitution + pre-commit guard + post-commit grep guard; literal placeholder commit yolu YOK.

**Task ordering rationale (Codex önerileri uygulandı):**
- Task 3 (canonical block) Task 4-11 (body) öncesi — fail-fast drift.
- Task 14 (simplify.md stub) en son — eski içerik build sırasında referans kaynağı (Task 4-10'da spec yetkili ama eski simplify cross-check için açık kalır).
- Task 13 (/simplify sweep) Task 14 öncesi — sweep yapılırken yeni komut var, stub henüz değil; "intermediate broken state" yok.
- Task 12 (3 ayna Sözleşme Notları) Task 13 öncesi — drift section önce 4-way'e güncellensin, sonra execute-plan /simplify referansları çevrilsin (ikisi farklı sweep, ama 4-way drift sözleşmesi semantik öncelik).

**Acceptance command (tek satırla CI-friendly özet — execute-plan-claude-codex tarafı kullanırsa):**

```bash
# Drift contract acceptance — herhangi bir refine PR'ında koşulur
SPEC=~/.claude/commands/spec-claude-codex.md
diff_count=0
for target in write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex; do
  diff -q <(awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' $SPEC) \
          <(awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' ~/.claude/commands/$target.md) >/dev/null || diff_count=$((diff_count + 1))
done
token_missing=0
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex; do
  block=$(awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' ~/.claude/commands/$f.md)
  for token in "codex-companion.mjs" "git rev-parse" "AGENTS.md" "timeout 480s" "124" "Claude-only devam et" "Tekrar dene" "Komutu durdur"; do
    echo "$block" | grep -q -F "$token" || token_missing=$((token_missing + 1))
  done
done
echo "diff_count=$diff_count (must be 0); token_missing=$token_missing (must be 0)"
[ "$diff_count" -eq 0 ] && [ "$token_missing" -eq 0 ] && echo "DRIFT CONTRACT: OK" || echo "DRIFT CONTRACT: FAIL"
```

Bu komut Task 15 Step 1-2 yerine tek seferde koşulabilir; sonuç `DRIFT CONTRACT: OK` olmalı.
