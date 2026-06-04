---
title: Codex Review Scope Contract + Structured Recommendation + execute-plan 8.6 Auto-Continue
status: plan-approved
date: 2026-06-04
source_spec: docs/specs/2026-06-04-codex-review-scope-contract.md
source_spec_unapproved_override: false
noisy_review_override: false
unresolved_high_severity_override: false
codex_plan_review_status: approved
codex_plan_review_iterations: 4
codex_plan_targeted_fixes: 2
codex_plan_review_log: docs/reviews/codex/2026-06-04-codex-review-scope-contract-plan.md
---

# Codex Review Scope Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a 7-way byte-identical `CODEX-REVIEW-SCOPE-CONTRACT` block (pinned scope + per-command requirement-source binding + dependency scope + command-policy external-overlay + coverage statement + structured-fix-per-finding) to the claude-codex command family, locked by a new two-layer drift Check E; change AUTO-FIX to every-turn structured recommendation (4-way); rewrite execute-plan Adım 8.6 to clean-checkpoint auto-continue.

**Architecture:** Canonical-authored byte-identical block (text fixed once in `spec-claude-codex`), **per-command co-located** placement + binding/call-site rewrite (block lands adjacent to and before each command's actual Codex call), then mechanical `cmp` byte-lock. Check E is two-layer: **hard gate** = byte-lock (7-way `cmp` + tokens) + statically-provable section-anchored assertions (modeled on the existing `check_s1_literal_regression`); **advisory tripwire** = prose/semantic coverage that awk cannot prove (documented residual, mirroring `check_reviewer_forbidden`). TDD **RED-first**: each drift-check increment is added and shown failing before the external command edits make it pass.

**Tech Stack:** Bash + awk (drift-check), markdown command files at `~/.claude/commands/*-claude-codex.md` (repo-EXTERNAL deliverable), repo-internal tools `docs/tools/claude-codex-drift-check.sh` + `docs/tools/codex-scan-substrate-harness.sh`.

---

## Deliverable & commit boundary (read before starting)

- **Repo-EXTERNAL (NOT committed):** the 7 command files `~/.claude/commands/{spec,write-plan,execute-plan,simplify,review,security-review,finish-branch}-claude-codex.md`. These are edited and verified, never committed to this repo. Pre-edit backups go to `~/.claude/command-backups/`.
- **Repo-INTERNAL (committed):** `docs/tools/claude-codex-drift-check.sh` (Check E additions) + this plan + the Codex review log + later review/security docs. Commits use `docs:` prefix, **push gated** (no push).
- **`plan-claude-codex.md` is the deprecated alias — it is NOT part of the 7-way set. Never edit it for this work.**
- **Existing markers MUST be preserved:** `CODEX-CALL-PROTOCOL` (7-way), `CODEX-SCAN-SUBSTRATE` (4-way), `AUTO-FIX-REVIEW-POLICY` (4-way). Only the AUTO-FIX *Tur yapısı* subsection changes (Task 5), byte-identically across its 4 members.

---

### Task 1: Backups + baseline green

**Files:**
- Create: `~/.claude/command-backups/review-scope-<ts>/` (external backups)
- Read: `docs/tools/claude-codex-drift-check.sh`, `docs/tools/codex-scan-substrate-harness.sh`

- [ ] **Step 1: Back up all command files (external, before any edit)**

```bash
TS=$(date -u +%Y%m%dT%H%M%SZ)
BK=~/.claude/command-backups/review-scope-$TS
mkdir -p "$BK"
cp -p ~/.claude/commands/*-claude-codex.md "$BK"/
ls -1 "$BK"
```
Expected: 8 files copied (the 7 + deprecated `plan-claude-codex.md`; backup is broad, edits are not).

- [ ] **Step 2: Baseline drift-check PASS (A/B/C/D)**

Run: `bash docs/tools/claude-codex-drift-check.sh; echo "exit=$?"`
Expected: ends `PASS: claude-codex drift check clean`, `exit=0`.

- [ ] **Step 3: Baseline S-1 harness PASS**

Run: `bash docs/tools/codex-scan-substrate-harness.sh; echo "exit=$?"`
Expected: harness PASS, `exit=0`. (If the harness needs args, read its header first.)

- [ ] **Step 4: No commit** — backups are external, verification is read-only. Proceed to Task 2.

---

### Task 2: Add Check E byte-lock to drift-check.sh (RED)

**Files:**
- Modify: `docs/tools/claude-codex-drift-check.sh`

- [ ] **Step 1: Add Check E config + markers + tokens**

After the `AUTO_FIX_EXPECTED` / `REVIEWER_EXPECTED` declarations (near line 22), add:

```bash
REVIEW_SCOPE_EXPECTED=(spec write-plan execute-plan simplify review security-review finish-branch)
REVIEW_SCOPE_BEGIN='<!-- CODEX-REVIEW-SCOPE-CONTRACT:BEGIN'
REVIEW_SCOPE_END='<!-- CODEX-REVIEW-SCOPE-CONTRACT:END'
REVIEW_SCOPE_TOKENS=(
  'Pinned target'
  'Requirement sources'
  'Dependency scope'
  'Command-policy external-files'
  'Coverage statement'
  'fix recommendation'
  'context-only overlay'
)
```

- [ ] **Step 2: Wire Check E byte-lock calls**

After the `check_s1_literal_regression` invocation (near line 340, before the final `if [ "$FAIL" -eq 0 ]`), add:

```bash
check_expected_blocks "Check E CODEX-REVIEW-SCOPE-CONTRACT" "$REVIEW_SCOPE_BEGIN" "$REVIEW_SCOPE_END" "revscope" "${REVIEW_SCOPE_EXPECTED[@]}"
check_unexpected_markers "Check E CODEX-REVIEW-SCOPE-CONTRACT" "$REVIEW_SCOPE_BEGIN" "${REVIEW_SCOPE_EXPECTED[@]}"
check_tokens "Check E CODEX-REVIEW-SCOPE-CONTRACT" "revscope" "${REVIEW_SCOPE_TOKENS[@]}"
```

- [ ] **Step 3: Run to verify RED**

Run: `bash docs/tools/claude-codex-drift-check.sh; echo "exit=$?"`
Expected: FAIL — `Check E ... missing` / marker-count failures for all 7 (block absent), `exit=1`. This proves Check E catches absence. **Do NOT commit yet** (test is RED; commit lands with GREEN in Task 3).

---

### Task 3: Author canonical block + propagate 7-way co-located → byte-lock GREEN

**Files:**
- Modify (external): all 7 `~/.claude/commands/*-claude-codex.md`
- Modify: `docs/tools/claude-codex-drift-check.sh` (commit point only)

- [ ] **Step 1: Author the canonical block in `spec-claude-codex.md`**

Insert this EXACT block as a new top-level policy section `## Codex Review Scope Contract (aile ortak)` immediately **after** the `## Auto-Fix Review Policy` section and **before** `## Adım 0`. This is the canonical source; every other command gets a byte-identical copy.

````markdown
## Codex Review Scope Contract (aile ortak)

<!-- CODEX-REVIEW-SCOPE-CONTRACT:BEGIN (canonical: spec-claude-codex; 7-way byte-identical — biri değişirse diğerleri de; drift-check Check E) -->
> **Codex Review Scope Contract (aile ortak — her review/audit-emitting komut).** Her Codex
> review/audit çağrısı bu sözleşmeyi taşır. Blok yalnız **değişmez requirement**'ları tanımlar;
> her komut **değişkenleri** (primary artifact, requirement sources, pinned ref, overlay mekanizması,
> finding/recommendation vokabüleri) kendi **binding prose**'unda doldurur — binding sözleşmeyi
> ZAYIFLATAMAZ, yalnız nasıl doldurulacağını söyler. Binding bloğu **fiilî Codex çağrısının hemen
> ÖNÜNDE** (co-located) doldurur.

### Review scope (Codex çağrısından ÖNCE kurulur, prompt'a explicit girer)
- **Pinned target:** review aralığı çağrıdan önce **somut SHA**'lara çözülür (base..HEAD;
  "şu anki HEAD" semi-dynamic bırakılmaz — HEAD fix'ler sırasında ilerlese de review pinli kalır).
- **Requirement sources (per-command binding):** ilgili requirement kaynakları **explicit declare**
  edilir ve **CURRENT** içeriği requirement olarak okutulur (implementation değil); yok/uygulanamaz
  kaynak coverage statement'ta `not present` / `not applicable (intentional)` raporlanır — sessizce
  atlanmaz. Hangi kaynaklar: komutun binding'inde (blok set'i hardcode ETMEZ).
- **Dependency scope:** her değişen public function / API route / command branch / schema / migration /
  config contract için direct callers/callees + adjacent tests + sibling command files finding/
  recommendation finalize edilmeden önce incelenir.
- **Command-policy external-files (conditional):** review command-policy ilgilendiriyorsa canlı
  `~/.claude/commands/*-claude-codex.md` external-overlay guard ile scan root'a alınır — allowlist
  ADAY listesidir (trust boundary değil): pre-copy regular-file + realpath-under-`~/.claude/commands/`
  validation, secret-scan kopyadan önce, symlink no-follow. Overlay **context-only overlay** olarak
  işaretlenir (reviewed diff DEĞİL); coverage'da hem gerçek hem scan-root path raporlanır; post-overlay
  coverage accounting overlay'i reviewed-diff dışında tutar. git'siz export modunda overlay AYRI
  sanitized temp root'a gider (export snapshot saf kalır).

### Required Codex output (her review/audit)
- **Coverage statement (zorunlu):** files inspected / requirement files inspected / related files
  inspected / files not inspected and why (+ context-only overlay dosyaları ayrı işaretli).
- **Structured fix recommendation — HER finding için, severity fark etmez (canonical 7-alan format;
  `AUTO-FIX-REVIEW-POLICY` bu formatı REFERANS eder, tekrar tanımlamaz):**
  `root cause / minimal fix strategy / exact affected files+functions / related files w/ same pattern /
  verification command / risk if recommendation wrong / fallback if minimal fix does not close`.
  *Codex read-only kalır — yalnız metin önerir, dosya YAZMAZ; uygulayan Claude.*
<!-- CODEX-REVIEW-SCOPE-CONTRACT:END -->
````

- [ ] **Step 2: Extract the canonical block to a temp file (propagation source)**

```bash
awk '/<!-- CODEX-REVIEW-SCOPE-CONTRACT:BEGIN/,/<!-- CODEX-REVIEW-SCOPE-CONTRACT:END/' \
  ~/.claude/commands/spec-claude-codex.md > /tmp/revscope.block
wc -l /tmp/revscope.block   # sanity: ~30 lines, non-empty
```

- [ ] **Step 3: Insert the byte-identical block into the other 6, co-located before each Codex review call**

For EACH of `write-plan execute-plan simplify review security-review finish-branch`: paste the contents of `/tmp/revscope.block` as a `## Codex Review Scope Contract (aile ortak)` section placed so it sits **before** that command's actual Codex review/audit call section (co-location invariant). Recommended anchor per command:
- `write-plan`, `execute-plan`, `simplify`: immediately after their `## Auto-Fix Review Policy` section.
- `review`: after the `CODEX-CALL-PROTOCOL` section, before Adım 4 (the 4b adversarial-review call).
- `security-review`: after the `CODEX-CALL-PROTOCOL` section, before the Adım 4 mode-aware call.
- `finish-branch`: after the `CODEX-CALL-PROTOCOL` section, before Adım 5 (the task --fresh closure-audit).

Use byte-identical paste (do not retype). After all 6, verify identity:

```bash
for c in write-plan execute-plan simplify review security-review finish-branch; do
  awk '/<!-- CODEX-REVIEW-SCOPE-CONTRACT:BEGIN/,/<!-- CODEX-REVIEW-SCOPE-CONTRACT:END/' \
    ~/.claude/commands/$c-claude-codex.md | cmp -s - /tmp/revscope.block \
    && echo "ok $c" || echo "DRIFT $c"
done
```
Expected: `ok` for all 6.

- [ ] **Step 4: Add a content-free co-located binding-marker region at each call-site**

In each of the 7, immediately before the Codex review/audit call, add an EMPTY delimited binding region (machine-checkable co-location anchor). **Deliberately omit** the ask/pinned-ref/overlay tokens — they are filled in Task 4 so the binding assertion is genuinely RED until then:

```markdown
<!-- REVIEW-SCOPE-BINDING:<slug> -->
> **Review Scope Contract binding (bkz. "## Codex Review Scope Contract").** <Task 4 doldurur.>
<!-- /REVIEW-SCOPE-BINDING -->
```
(`<slug>` = the command's slug, e.g. `spec`, `execute-plan`.) Verify each region is present + empty of the Task-4 tokens:
```bash
for c in spec write-plan execute-plan simplify review security-review finish-branch; do
  grep -cF "<!-- REVIEW-SCOPE-BINDING:$c -->" ~/.claude/commands/$c-claude-codex.md
done   # each → 1
```

- [ ] **Step 5: Run Check E byte-lock → GREEN; re-verify A/B/C/D**

Run: `bash docs/tools/claude-codex-drift-check.sh; echo "exit=$?"`
Expected: Check E block-present + byte-identical + tokens PASS for all 7; **Check A/B/C/D still PASS**; `exit=0`.

- [ ] **Step 6: Commit drift-check.sh (byte-lock layer GREEN)**

```bash
git add docs/tools/claude-codex-drift-check.sh
git commit -m "feat: add drift-check Check E byte-lock for CODEX-REVIEW-SCOPE-CONTRACT"
```
(Command files are external — not in this commit.)

---

### Task 4: Per-command binding (section-anchored) + prompt wiring + Check E assertions (RED→GREEN)

**Files:**
- Modify (external): all 7 command files (fill the `REVIEW-SCOPE-BINDING` regions + prompt bodies)
- Modify: `docs/tools/claude-codex-drift-check.sh` (section-anchored hard-gate assertions)

> **Design note (Codex plan-review T1 P1/P2/P3 + T2 P4):** Check E's section-anchored layer keys on the
> **`REVIEW-SCOPE-BINDING:<slug>` marker region** (introduced Task 3 Step 4), NOT file-wide tokens.
> This makes the assertions genuinely section-anchored: the block being byte-identical does NOT satisfy
> them (the binding region is a distinct region), and an empty Task-3 stub is genuinely RED.
> **Hard-gate (statically provable, per spec §6/§7):** (a) binding region present; (b) inside the region:
> coverage-ask + structured-rec-ask + **concrete** pinned-ref token (not the bare `pinned target` label) +
> overlay guard terms (`external-overlay`/`realpath`/`regular-file`/`secret-scan`/`context-only`) + **no
> unfilled `<...>` placeholders / stub text**; (c) **co-location + pinned-ref-before-call** — a Codex call
> token appears after the binding-END within the SAME section, so the binding (carrying the concrete
> pinned-ref + asks) provably precedes the call; (c2) **prompt-body asks** — the actual Codex prompt (in the
> same post-binding section, not the binding comment) literally asks for coverage statement + structured-rec
> (Codex T4 P8); (d) 8.6 delimited clean-no-gate (Task 6). **Advisory
> (genuinely unprovable — static ceiling):** ref *correctness* (is the named ref the semantically-right base)
> + overlay *procedure correctness* (does the guard actually run right) — spec §6 Katman 6 allocates both to
> per-command Codex review at /execute time; Task 4 Step 5 records the manual ref-correctness check. This
> restores all spec §6/§7 WIRING hard-gates; only procedure-correctness (never statically provable) is advisory.

- [ ] **Step 1: Add the section-anchored binding assertion to drift-check.sh (RED)**

Place after `check_s1_literal_regression`:

```bash
check_review_scope_binding() {
  # F1 hard-gate (section-anchored to the REVIEW-SCOPE-BINDING:<slug> region — NOT file-wide, NOT the
  # contract block). Proves each command's co-located binding actually carries the asks + pinned-ref +
  # overlay tokens, i.e. the call path is wired, not just the block pasted.
  local slug file b e region miss
  say "--- Check E review-scope binding (section-anchored per command) ---"
  for slug in "${REVIEW_SCOPE_EXPECTED[@]}"; do
    file=$(cmd_path "$slug")
    [ -f "$file" ] || { fail "Check E binding missing file: $file"; continue; }
    b=$(grep -cF "<!-- REVIEW-SCOPE-BINDING:$slug -->" "$file")
    e=$(grep -cF "<!-- /REVIEW-SCOPE-BINDING -->" "$file")
    if [ "$b" -ne 1 ] || [ "$e" -ne 1 ]; then
      fail "Check E binding marker count $slug: begin=$b end=$e (need 1/1)"; continue
    fi
    region=$(awk -v s="<!-- REVIEW-SCOPE-BINDING:$slug -->" '
      index($0,s){f=1} f{print} index($0,"<!-- /REVIEW-SCOPE-BINDING -->"){f=0}' "$file")
    miss=0
    # --- WIRING tokens (section-scoped to the binding region) ---
    printf '%s\n' "$region" | grep -qF 'coverage statement'   || { fail "Check E binding $slug: no coverage-ask";        miss=1; }
    printf '%s\n' "$region" | grep -qF 'fix recommendation'    || { fail "Check E binding $slug: no structured-rec-ask";  miss=1; }
    # CONCRETE pinned-ref token — NOT the 'pinned target' label (Codex T3 P6: label is always present
    # in the template → trivially passable). Require an actual ref/SHA identifier.
    printf '%s\n' "$region" | grep -qE 'RESOLVED_BASE|BASE_REF|--base|REVIEW_BASE_SHA|HEAD_SHA|REVIEW_WT' || { fail "Check E binding $slug: no CONCRETE pinned-ref token (label alone insufficient)"; miss=1; }
    # Overlay-setup hard-gate (Codex T3 P7 / spec §7): concrete guard terms, not just the 'external-overlay' label.
    printf '%s\n' "$region" | grep -qF 'external-overlay'      || { fail "Check E binding $slug: no overlay marker";       miss=1; }
    printf '%s\n' "$region" | grep -qE 'realpath'              || { fail "Check E binding $slug: no overlay realpath guard"; miss=1; }
    printf '%s\n' "$region" | grep -qE 'regular[- ]file'       || { fail "Check E binding $slug: no overlay regular-file guard"; miss=1; }
    printf '%s\n' "$region" | grep -qE 'secret[- ]scan'        || { fail "Check E binding $slug: no overlay secret-scan guard"; miss=1; }
    printf '%s\n' "$region" | grep -qF 'context-only'          || { fail "Check E binding $slug: no overlay context-only label"; miss=1; }
    # Placeholder reject (Codex T3 P6): no unfilled template tokens. Comment markers start "<!" so they
    # are excluded; a placeholder like <slug>/<tablo>/<...> or the stub text "Task 4 doldurur" → RED.
    printf '%s\n' "$region" | grep -qE '<[A-Za-z.]' && { fail "Check E binding $slug: unfilled placeholder (<...>) in binding"; miss=1; }
    printf '%s\n' "$region" | grep -qF 'Task 4 doldurur' && { fail "Check E binding $slug: empty Task-3 stub not filled"; miss=1; }
    # --- co-location + pinned-ref-before-call HARD-GATE (Codex T2 P4): a Codex call token must appear
    # after the binding-END within the SAME section (terminated by the next ##/### heading). Proves the
    # binding (carrying the in-region CONCRETE pinned-ref + asks) precedes the actual call.
    # Section-bounded → does not match the bottom CODEX-SCAN-SUBSTRATE definition.
    post=$(awk '/<!-- \/REVIEW-SCOPE-BINDING -->/{f=1; next} f && (/^### / || /^## /){exit} f{print}' "$file")
    printf '%s\n' "$post" | grep -qE 'run_codex_scan|node "\$COMPANION"|adversarial-review|task --fresh' \
      || { fail "Check E binding $slug: no Codex call after binding in same section (co-location/pinned-ref-before-call)"; miss=1; }
    # PROMPT-BODY wiring HARD-GATE (Codex T4 P8): the actual Codex prompt — in the SAME post-binding
    # section, NOT the binding comment — must literally ask for the coverage statement + structured-rec.
    # Proves the heredoc/companion prompt carries the asks, not just the binding prose (the predecessor
    # binding-declared-not-prompt-wired class for OUTPUT requirements).
    printf '%s\n' "$post" | grep -qF 'coverage statement' || { fail "Check E binding $slug: prompt body (post-binding section) lacks coverage-ask"; miss=1; }
    printf '%s\n' "$post" | grep -qF 'fix recommendation' || { fail "Check E binding $slug: prompt body (post-binding section) lacks structured-rec-ask"; miss=1; }
    [ "$miss" -eq 0 ] && ok "Check E binding + prompt-body wired + co-located: $slug"
  done
}
# NOTE: Check E hard-gates WIRING (concrete tokens, section-anchored, no placeholders, co-located).
# PROCEDURE CORRECTNESS (is the ref the semantically-right base; does the overlay guard actually run
# correctly) is NOT statically provable → execution Codex review (spec §6 Katman 6) + Task 4 Step 5
# manual ref-correctness. This is the deliberate static ceiling, not an advisory downgrade of the
# wiring gates.
```
Wire it after the Check E token call (Task 3 Step 2 region):
```bash
check_review_scope_binding
```
Run: `bash docs/tools/claude-codex-drift-check.sh; echo "exit=$?"`
Expected: RED — every command's binding region is the empty Task-3 stub (no asks/pinned-ref/overlay tokens), so the assertion FAILS for all 7. `exit=1`. This is the genuine RED (the byte-identical block does NOT satisfy it because the check is region-scoped to the binding, not the block).

- [ ] **Step 2: Fill each command's `REVIEW-SCOPE-BINDING` region (section-anchored content)**

Replace each command's empty binding region body with the full binding. **Every `<...>` placeholder MUST be replaced with a concrete value** (Check E rejects any remaining `<...>` and the stub text). The region MUST contain (Check E hard-gate tokens): a **concrete** pinned-ref token (`RESOLVED_BASE`/`BASE_REF`/`--base`/`REVIEW_BASE_SHA`/`HEAD_SHA`/`REVIEW_WT` — NOT the bare label `pinned target`), the requirement-sources, the **overlay guard terms** (`external-overlay` + `realpath` + `regular-file` + `secret-scan` + `context-only`), and the two asks (`coverage statement`, `structured fix recommendation` → contains `fix recommendation`).

Concrete template — example shown for `spec` (the overlay-guard line + asks are IDENTICAL across all 7; only the pinned-ref token + requirement-sources change per the table):

```markdown
<!-- REVIEW-SCOPE-BINDING:spec -->
> **Review Scope Contract binding (bkz. "## Codex Review Scope Contract").**
> pinned target: RESOLVED_BASE (clean) / --scope working-tree (dirty) — concrete ref resolved before the call;
> requirement sources: mevcut mimari/vault/kod referansları.
> command-policy (conditional): external-overlay guard — allowlist aday + pre-copy regular-file +
> realpath under ~/.claude/commands/ + secret-scan + symlink no-follow; context-only overlay (reviewed
> diff DEĞİL) + post-overlay coverage accounting.
> Codex prompt'u ZORUNLU ister: coverage statement (files inspected / requirement files / related files /
> not inspected+why) + her finding için structured fix recommendation (root cause / minimal fix /
> affected files+functions / related files / verification / risk / fallback).
<!-- /REVIEW-SCOPE-BINDING -->
```

Per-command fills — **replace the pinned-ref token + requirement-sources** from this table (overlay-guard line + asks stay verbatim; the binding must contain a concrete ref token, not the `pinned target` label):

| slug | concrete pinned-ref token | requirement sources | vocab/notes |
|---|---|---|---|
| spec | `RESOLVED_BASE` (clean) / `--scope working-tree` (dirty) | mevcut mimari/vault/kod referansları | — |
| write-plan | `RESOLVED_BASE` (clean) / `--scope working-tree` (dirty, `$PLAN_PATH`) | linked spec (`$SPEC_PATH`) | — |
| execute-plan | `--base $BASE_REF` (`BASE_REF`=`last_checkpoint_ref`>`execute_start_ref`) | `$PLAN_PATH` + linked spec + TASK/HANDOFF | — |
| simplify | `RESOLVED_BASE` (clean) / `--scope working-tree` (dirty) | davranış baseline (public API/caller/test) | spec-alignment N/A |
| review | `REVIEW_WT` @ `HEAD_SHA` (`REVIEW_BASE_SHA`..`HEAD_SHA`) | spec/plan requirement snapshot (identical iki hakeme) | report-only (no auto-fix) |
| security-review | `REVIEW_WT`/export @ `HEAD_SHA` (mode-aware) | güvenlik kategori checklist'i + proje güvenlik konteksti | **spec/plan/TASK/HANDOFF = `not applicable (intentional)`**; report-only |
| finish-branch | `REVIEW_BASE_SHA`/closure snapshot pinned refs | review/security reports + active-layer + branch/closure state | finding vocab **closure-blocker/warning/note**; advisory (NOT auto-fix) |

> **security-review export note:** for git-less export mode the overlay-guard line additionally states the overlay goes to a **separate sanitized temp root** (not the export snapshot). Keep the `external-overlay`/`realpath`/`regular-file`/`secret-scan`/`context-only` terms.

**Also wire the actual prompt body (Codex T4 P8 — hard-gated):** the binding declares the asks, but Check E separately requires the real Codex prompt to literally request them. Append to each command's review/audit prompt heredoc tail (the prompt must live in the SAME section as its binding, after it, so the post-binding check sees it):
> `Provide a coverage statement (files inspected / requirement files inspected / related files inspected / files not inspected and why). For every finding include a structured fix recommendation (root cause / minimal fix strategy / exact affected files+functions / related files w/ same pattern / verification command / risk if wrong / fallback).`

- [ ] **Step 3: Run — binding assertion GREEN**

Run: `bash docs/tools/claude-codex-drift-check.sh; echo "exit=$?"`
Expected: `check_review_scope_binding` PASS for all 7; Check A/B/C/D + Check E byte-lock still PASS. (The 8.6 assertion is added in Task 6, not here.) `exit=0`.

- [ ] **Step 4: Commit drift-check.sh (binding assertion layer)**

```bash
git add docs/tools/claude-codex-drift-check.sh
git commit -m "feat: add Check E section-anchored binding assertion (per-command wiring)"
```

- [ ] **Step 5: Manual acceptance — ref CORRECTNESS only (the one genuine advisory residual)**

Co-location + pinned-ref-before-call are now HARD-GATED (Step 1 co-location check). The only residual is **ref correctness** — whether the ref/SHA named in each binding is the *semantically right* base for that command's topology (e.g. execute-plan uses `execute_start_ref`/`last_checkpoint_ref`, review uses `REVIEW_BASE_SHA..HEAD_SHA`). This is not statically provable; manually confirm per command and record in HANDOFF during execution. Covered also by Task 8.5 scenario trace + per-command Codex review at /execute time (spec §6 Katman 6).

---

### Task 5: AUTO-FIX 4-way every-turn edit + stale sweep (Check D stays GREEN)

**Files:**
- Modify (external): `spec`, `write-plan`, `execute-plan`, `simplify` (AUTO-FIX block + binding prose)

- [ ] **Step 1: Rewrite the AUTO-FIX *Tur yapısı* subsection in canonical (`spec-claude-codex.md`)**

Replace the two bullets:
```
- **Tur 1–3:** Claude kendi fix yaklaşımıyla düzeltir → verify → Codex re-review.
- **Tur 4+:** Codex çağrısı bulgunun yanında **zorunlu yapılandırılmış çözüm önerisi** döner:
  `root cause / minimal fix strategy / etkilenen dosya·fonksiyonlar / verification komutu /
  yanlışsa risk / fallback`. Claude değerlendirip uygular (kullanıcı onayı yok). *Codex
  read-only kalır — yalnız metin önerir, dosya YAZMAZ; uygulayan Claude.*
```
with:
```
- **Her review turunda:** Codex çağrısı bulgunun yanında **zorunlu yapılandırılmış çözüm önerisi**
  döner (format `CODEX-REVIEW-SCOPE-CONTRACT`'ta tanımlı 7-alan — burada tekrar tanımlanmaz). Claude
  tahkim eder (root cause doğru mu / doğru dosya·invariant mı / minimal mi / aynı pattern sibling'larda
  var mı / carve-out / verification kanıtlıyor mu), kapsam içi + doğruysa uygular (kullanıcı onayı yok),
  verification'ı taze çalıştırır, Codex re-review ile kapanışı doğrular. *Codex read-only kalır — yalnız
  metin önerir, dosya YAZMAZ; uygulayan Claude.*
```
(The `6-tavan` bullet and `"max review 3 geçersiz"` negation line stay UNCHANGED — the negation is correct and deliberate.)

- [ ] **Step 2: Propagate the AUTO-FIX block byte-identical to the other 3**

```bash
awk '/<!-- AUTO-FIX-REVIEW-POLICY:BEGIN/,/<!-- AUTO-FIX-REVIEW-POLICY:END/' \
  ~/.claude/commands/spec-claude-codex.md > /tmp/autofix.block
for c in write-plan execute-plan simplify; do
  awk '/<!-- AUTO-FIX-REVIEW-POLICY:BEGIN/,/<!-- AUTO-FIX-REVIEW-POLICY:END/' \
    ~/.claude/commands/$c-claude-codex.md | cmp -s - /tmp/autofix.block && echo "ok $c" || echo "NEEDS-SYNC $c"
done
```
For each `NEEDS-SYNC`, replace that command's AUTO-FIX block region with `/tmp/autofix.block` contents (byte-identical), then re-run until all `ok`.

- [ ] **Step 3: Sweep the per-command binding "tur≥4" prose (NOT in the block)**

These per-file lines still describe Tur-4+ timing; reword each to "her turda" (every turn):
- `spec-claude-codex.md:555` (Mode A "tur≥4 Codex yapılandırılmış çözüm önerisi döner")
- `write-plan-claude-codex.md:412`
- `execute-plan-claude-codex.md:517`, `:531`, `:705`, `:728`
- `simplify-claude-codex.md:613`, `:626`

Reword pattern: "tur≥4 Codex ... çözüm önerisi döner" → "her review turunda Codex ... çözüm önerisi döner (CODEX-REVIEW-SCOPE-CONTRACT garantisi)". (Line numbers are pre-edit anchors; re-grep after the block edit since numbers shift.)

- [ ] **Step 4: Verify stale sweep + Check D byte-identical**

```bash
grep -rnE 'Tur 4\+|Tur≥4|tur≥4|Tur 1–3|Tur 1-3' ~/.claude/commands/*-claude-codex.md; echo "timing-hits-above"
grep -rn 'max review 3' ~/.claude/commands/*-claude-codex.md
bash docs/tools/claude-codex-drift-check.sh; echo "exit=$?"
```
Expected: zero timing-phrase hits; `max review 3` only as the 4 "geçersiz" negations inside the AUTO-FIX block; **Check D byte-identical 4-way PASS** (tokens claude-confirmed/cluster-key/finding-id/global cap/reopen/6-tavan intact). **The 8.6 assertion does NOT exist yet (added in Task 6), so the full check must be GREEN here: `exit=0`.** A non-zero exit at this point means a real Check A/B/C/D or binding regression — investigate, do not carry forward (Codex plan-review T2 P5).

---

### Task 6: execute-plan 8.6 rewrite + 8.5/final-guard timing + 8.6 assertion GREEN

**Files:**
- Modify (external): `execute-plan-claude-codex.md` (Adım 8.6, 8.5 guard, final guard)
- Modify: `docs/tools/claude-codex-drift-check.sh` (commit point)

- [ ] **Step 1: Add the delimited 8.6 clean-path assertion to drift-check.sh (RED)**

Place after `check_review_scope_binding`. It is scoped to the **delimited** `8.6-CLEAN-PATH` region (not a historical-phrase proxy and not the whole 8.6 section — the DUR subsection legitimately asks):

```bash
check_execute_plan_clean_continue() {
  # execute-plan 8.6 CLEAN-PATH (delimited subsection) must contain NO user gate
  # (AskUserQuestion / "Devam edelim mi"). The separate DUR-PATH subsection MAY ask — so the
  # check is region-scoped to the delimited clean subsection (machine-checkable; Codex T1 P3).
  local file region; file=$(cmd_path "execute-plan")
  say "--- Check E execute-plan 8.6 clean-path (delimited region, no user gate) ---"
  [ -f "$file" ] || { fail "Check E 8.6 missing file: $file"; return; }
  grep -qF '<!-- 8.6-CLEAN-PATH -->'  "$file" || { fail "Check E 8.6: CLEAN-PATH begin marker missing"; return; }
  grep -qF '<!-- /8.6-CLEAN-PATH -->' "$file" || { fail "Check E 8.6: CLEAN-PATH end marker missing"; return; }
  region=$(awk '/<!-- 8.6-CLEAN-PATH -->/{f=1} f{print} /<!-- \/8.6-CLEAN-PATH -->/{f=0}' "$file")
  if printf '%s\n' "$region" | grep -qE 'AskUserQuestion|Devam edelim mi'; then
    fail "Check E 8.6 clean-path has user gate: $(printf '%s\n' "$region" | grep -nE 'AskUserQuestion|Devam edelim mi' | head -3)"
  else
    ok "Check E 8.6 clean-path delimited region has no user gate"
  fi
}
```
Wire after `check_review_scope_binding`:
```bash
check_execute_plan_clean_continue
```
Run: `bash docs/tools/claude-codex-drift-check.sh; echo "exit=$?"`
Expected: RED — the `8.6-CLEAN-PATH` markers don't exist yet (8.6 not rewritten). `exit=1`.

- [ ] **Step 2: Rewrite Adım 8.6 with delimited CLEAN / DUR subsections (GREEN)**

Replace the current 8.6 body (the "Devam edelim mi?" report + "Kullanıcı onay vermeden ... geçme" + post-approval write) with:

```markdown
### 8.6 Checkpoint sonucu → deterministik aksiyon

Codex çıktısı tahkim edilir (claude-confirmed C/H/M · low · non-claude-confirmed/advisory). Aksiyon
matrix (spec §5.1):

<!-- 8.6-CLEAN-PATH -->
**Clean / low-only auto-continue — bu dalda kullanıcıya soru SORULMAZ:**
- **Clean** (tests PASS + Codex approve + 0 bulgu + unresolved C/H/M yok + low yok) → kısa
  bilgilendirme → §3.5 mutation protokolü → sonraki batch (Adım 7) otomatik başlar.
- **Yalnız non-claude-confirmed / advisory bulgu** → audit'e yaz, sormadan devam.
- **Low, turn ≥4 ve C/H/M yok** → audit-ignore, sormadan devam.
<!-- /8.6-CLEAN-PATH -->

**Fix dalı (sormadan otonom):** Low turn ≤3 → düzelt + verify + Codex re-review. claude-confirmed
C/H/M → Adım 8.5 otonom fix döngüsü (zaten wire'lı).

<!-- 8.6-DUR-PATH -->
**DUR — YALNIZ burada kullanıcıya gidilir (`AskUserQuestion`):** 6-tavan / global cap=10 / 2.-reopen /
Codex degradation / carve-out / ilgisiz dirty `docs/active` (§3.5 Adım 0) → kullanıcıya somut rapor +
`AskUserQuestion` (devam / kapsam daralt / manuel düzelt / Durdur).
<!-- /8.6-DUR-PATH -->

**last_checkpoint_ref mutation protokolü (mechanical execution-state write; spec §3.5; clean dalında çalışır):**
0. **Pre-mutation guard:** `git status --porcelain -- docs/active` temiz olmalı (tek-alan patch'imiz
   dışında ilgisiz dirty YOK). İlgisiz dirty → DUR dalına git (yukarıdaki DUR; mutation/commit/auto-continue YOK).
1. **Capture:** `POST_CP_HEAD=$(git rev-parse HEAD)` (write'tan ÖNCE).
2. **RMW tek alan:** HANDOFF.md `Verification.last_checkpoint_ref = POST_CP_HEAD` (başka alan yok; section yoksa ekle).
3. **Mechanical docs commit:** `docs/active/` write'ı commit'le (otonom local commit cadence; push gate).
4. **Re-verify:** `git status` temiz → sonraki 3-task batch otomatik başlar.

(Ref = `POST_CP_HEAD` = task HEAD; commit-sonrası HEAD DEĞİL — kendi commit SHA'sına eşit olamaz, circular.)
```
**Note:** the mutation protocol sits OUTSIDE the `8.6-CLEAN-PATH` markers (shared machinery); its pre-mutation-guard DUR routes to the DUR subsection. The CLEAN-PATH delimited region therefore contains no `AskUserQuestion`/`Devam edelim mi`.

- [ ] **Step 3: Reword 8.5 guard + final guard timing (from Task 5 Step 3 sweep)**

Confirm `execute-plan-claude-codex.md` (formerly lines ~517/531/705/728) now read "her review turunda" (not "Tur≥4"). Re-grep (numbers shifted after the 8.6 rewrite): `grep -nE 'Tur≥4|tur≥4|Tur 4\+' ~/.claude/commands/execute-plan-claude-codex.md` → 0.

- [ ] **Step 4: Run — 8.6 assertion GREEN, full A/B/C/D/E GREEN**

Run: `bash docs/tools/claude-codex-drift-check.sh; echo "exit=$?"`
Expected: `check_execute_plan_clean_continue` PASS (CLEAN-PATH delimited region has no user gate); Check A/B/C/D/E all PASS; `exit=0`.

- [ ] **Step 5: Commit drift-check.sh (8.6 assertion layer GREEN)**

```bash
git add docs/tools/claude-codex-drift-check.sh
git commit -m "feat: add Check E delimited 8.6 clean-path assertion"
```

---

### Task 7: External-overlay guard binding + S-1 harness re-verify

**Files:**
- Modify (external): the 7 command files (external-files binding) — primarily the call-site bindings
- Read/Run: `docs/tools/codex-scan-substrate-harness.sh`

- [ ] **Step 1: Confirm per-substrate overlay specifics (the guard terms are already hard-gated in Task 4)**

The overlay guard terms (`external-overlay`/`realpath`/`regular-file`/`secret-scan`/`context-only`) already land in each `REVIEW-SCOPE-BINDING` region in Task 4 Step 2 and are **hard-gated** by `check_review_scope_binding`. Here, confirm each command's binding states the correct **per-substrate** specifics (no new drift-check assertion needed — the terms are gated; this is the procedure-correctness confirmation). Reference spec §3.4:
- fix-commands (spec/write-plan/execute-plan/simplify) + reviewer worktree (review): overlay into `<scan-dir>/claude-commands/`, reuse `_css_secret_scan` where the command carries CODEX-SCAN-SUBSTRATE, else an equivalent pre-copy secret guard; pre-copy regular-file + realpath-under-`~/.claude/commands/` validation; symlink no-follow; **context-only label**; post-overlay coverage accounting.
- `security-review` git'siz export (full/path): overlay into a **separate sanitized temp root**, never the export snapshot.
- `finish-branch`: same guard; command-policy closures only.
- All: **conditional** — only when the reviewed artifact concerns command policy.

- [ ] **Step 2: Confirm overlay prose does not weaken the S-1 secret boundary**

Re-read each binding: the overlay must (a) secret-scan before copy, (b) validate regular-file + realpath, (c) never place live home-dir files into a committed/export snapshot. No binding may instruct copying without these.

- [ ] **Step 3: Re-run the S-1 harness (no regression)**

Run: `bash docs/tools/codex-scan-substrate-harness.sh; echo "exit=$?"`
Expected: PASS, `exit=0` (the overlay binding is prose-level guidance; the harness-tested substrate helpers are unchanged, so this confirms no accidental helper edit weakened S-1).

- [ ] **Step 4: No new repo commit** (only external bindings changed; drift-check already committed). Proceed to Task 8.

---

### Task 8: Full verification + scenario traces + docs commit

**Files:**
- Create: `docs/reviews/codex/2026-06-04-codex-review-scope-contract-plan.md` is the plan-review log (written by /write-plan flow, not here)
- Run: drift-check, S-1 harness, smoke-parse, grep sweeps

- [ ] **Step 1: Full drift-check GREEN (A/B/C/D/E)**

Run: `bash docs/tools/claude-codex-drift-check.sh; echo "exit=$?"`
Expected: `PASS: claude-codex drift check clean`, `exit=0`. Includes Check E byte-lock (7-way) + `check_review_scope_binding` (section-anchored, 7) + `check_execute_plan_clean_continue` (delimited 8.6).

- [ ] **Step 2: Stale sweep = 0**

Run: `grep -rnE 'Tur 4\+|Tur≥4|tur≥4|Tur 1–3|Tur 1-3' ~/.claude/commands/*-claude-codex.md; echo "done"`
Expected: no timing hits.

- [ ] **Step 3: 7-command markdown smoke-parse**

Run:
```bash
for c in spec write-plan execute-plan simplify review security-review finish-branch; do
  f=~/.claude/commands/$c-claude-codex.md
  awk 'BEGIN{cp=ac=rs=0} /<!-- CODEX-CALL-PROTOCOL:BEGIN/{cp++} /<!-- CODEX-REVIEW-SCOPE-CONTRACT:BEGIN/{rs++} END{printf "%s call-proto=%d revscope=%d\n", FILENAME, cp, rs}' "$f"
done
```
Expected: each command `call-proto=1 revscope=1`; file loads/parses with no broken markdown fences.

- [ ] **Step 4: S-1 harness PASS**

Run: `bash docs/tools/codex-scan-substrate-harness.sh; echo "exit=$?"`
Expected: PASS, `exit=0`.

- [ ] **Step 5: Scenario trace (prose, anchored to sections) — record in HANDOFF/review during execution**

Walk each scenario against the edited files and confirm the matrix outcome:
- clean checkpoint → auto-continue (execute-plan 8.6) · C/H/M finding → 8.5 auto-fix loop · low ≤3 → fix · low ≥4-only → audit-ignore+continue · 6-tavan/cap/2.-reopen → user DUR · command-policy review → external overlay context-only + coverage · security git-less export → overlay in separate temp root, not snapshot.

- [ ] **Step 6: Final commit (repo-internal only)**

```bash
git add docs/tools/claude-codex-drift-check.sh
git commit -m "test: finalize Check E full drift contract for review-scope" --allow-empty
```
(If drift-check.sh already fully committed in Task 6, this may be empty — that's fine; the command markdown stays external/uncommitted by design.)

---

## Self-review notes (author)

- **Spec coverage:** §3.1 block→Task 3; §3.2 requirement-source binding→Task 4 Step 2 (binding region + table); §3.3 membership/co-location→Tasks 3-4 (REVIEW-SCOPE-BINDING markers) + Check E; §3.4 external-overlay→Task 4 (token) + Task 7 (mechanism); §3.5 last_checkpoint protocol→Task 6 Step 2; §3.6 finish-branch advisory→Task 4 Step 2 table; §4 AUTO-FIX+sweep→Task 5; §5 8.6→Task 6; §6 layered verification→Tasks 2/4/6/8; §7 acceptance→Task 8.
- **RED-first honored (each drift-check increment fails before the external edit makes it pass):** Check E byte-lock RED (Task 2) → GREEN (Task 3); `check_review_scope_binding` RED (Task 4.1, empty Task-3 stub) → GREEN (Task 4.3, binding filled); `check_execute_plan_clean_continue` RED (Task 6.1, no delimited markers) → GREEN (Task 6.4, 8.6 rewritten with markers).
- **Section-anchored, not file-wide (Codex T1 P1/P2):** assertions key on the `REVIEW-SCOPE-BINDING:<slug>` region + the delimited `8.6-CLEAN-PATH` region — the byte-identical block does NOT satisfy them, and the empty stub is genuine RED.
- **Commit boundary:** only `docs/tools/claude-codex-drift-check.sh` + docs committed; 7 command files external/uncommitted; `plan-claude-codex.md` untouched.
- **Residual (honest, made explicit — Codex T2 P4 / T3 P6+P7):** the static ceiling is **procedure correctness** — ref *correctness* (is the named ref the semantically-right base) + overlay *procedure correctness* (does the guard actually run right). Neither is statically provable → **advisory**, covered by Task 4 Step 5 manual ref-check + Task 7 per-substrate confirmation + Task 8.5 scenario trace + per-command Codex review at /execute time (spec §6 Katman 6). All WIRING invariants are HARD-GATED: byte-lock (7-way), binding region present, in-region asks + **concrete** pinned-ref + overlay guard terms (realpath/regular-file/secret-scan/context-only) + no placeholders, **co-location + pinned-ref-before-call**, **prompt-body asks (post-binding section, not just the binding comment — Codex T4 P8)**, 8.6 delimited clean-no-gate.
