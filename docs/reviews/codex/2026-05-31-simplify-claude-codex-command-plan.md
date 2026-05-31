# Codex Plan Review Log — simplify-claude-codex implementation plan

Plan: `docs/plans/2026-05-31-simplify-claude-codex-command.md`
Source spec: `docs/specs/2026-05-31-simplify-claude-codex-command.md`

---

## Pre-Plan-Analysis Turn — 2026-05-31 (Adım 6 of write-plan-claude-codex)

(Codex'in implementation strategy + risk + task-order ön analizi; plan iskeleti seçimi için.)

**Strategies:**
- atomic-one-pass: Edit all 5 files in one implementation turn, then run Check A/B and reference sweep verification once. Fastest, matches spec "atomik tek tur"; risk is large markdown diff with several independent failure modes.
- contract-first-test-first: First extract canonical CODEX-CALL-PROTOCOL, create/update all 4 protocol mirrors and Sözleşme Notları, run 4-way Check A/B, then write new command body and stub. Best for fail-fast drift control; avoids building a new command around a bad copied block.
- mirror-first-then-graft: Create simplify-claude-codex.md skeleton by mirroring execute-plan style, graft canonical block byte-exact early, then fill simplify-specific steps from spec. Best balance: new command has stable shape before content detail, but drift still tested before final body polish.

Recommendation: **contract-first-test-first + mirror-first body build**. Canonical block should be copied early, not late.

**Top Risks:**
- Drift contract risk (4-way diff, tripwire tokens, BEGIN/END marker integrity)
- Four-command touch risk (execute-plan /simplify in different semantic contexts; blind sed yasak)
- Markdown slash command smoke risk (no runtime test harness; verification = structural + behavioral simulation)

**Must not forget:**
- Check A concrete: awk extraction pattern (4 dosya, 3 diff hepsi 0)
- Check B 8 token (codex-companion.mjs, git rev-parse, AGENTS.md, timeout 480s, 124, "Claude-only devam et", "Tekrar dene", "Komutu durdur")
- Adım 4.5 ayrı implementation task
- Mevcut Sözleşme Notları stale: write-plan "two commands", execute-plan "three commands", spec binding "write-plan only" → all 4-way
- Reuse awk extraction; smoke best-effort + structural verification

---

## Plan Review Turn 1 — 2026-05-31 (Adım 12)

Target: working tree diff
Verdict: **needs-attention**

No-ship: the plan still has execution-path failures that can leave the command uncommitted, mis-copied from spec, or runtime-broken while reporting success.

### Findings

- **[high] F1: Final commit cannot stage the planned command files from this repo** (plan lines 873-880)
  Task 15 runs `git add ~/.claude/commands/...` and expects 5 staged files, but the current repo is `/root/otomaix` and those targets live under `/root/.claude/commands`, outside the worktree. Inference from the current environment: this commit step cannot create the claimed atomic repo commit for the actual command changes, so rollback/audit/deploy state becomes false even if the markdown edits are made.
  Recommendation: Either move the command sources into a tracked repo-local path and install/sync them separately, or explicitly define this as a global-files change with backups and no repo commit claim. Do not leave `Expected: 5 dosya staged` for paths outside the repository.

- **[high] F2: Spec append pattern is not verified byte-for-byte, so executor drift can pass** (plan lines 243-255)
  The plan defends `Spec'in Adım N bölümünü birebir append et` as source attribution, but the implementation steps give prose instructions rather than extraction boundaries or diff checks against the spec body. The later checks only grep for headings/tokens, so an executor can omit or paraphrase detailed rules in Tasks 4-11 and still pass Task 15. This is a real drift risk for a markdown slash command where the prose is the implementation.
  Recommendation: Add deterministic section extraction markers or commands for every copied spec section and verify the generated command sections against the spec with `diff`, not just greps. Otherwise inline the exact text in the plan.

- **[medium] F3: Task 12 has no fallback if the stale-text catalog is empty or incomplete** (plan lines 72-88)
  Task 12 depends on Task 1 Step 4's grep catalog, but Task 1 only says to note the catalog and Task 12 proceeds with fuzzy phrases like `benzeri` and `dosyaya özgü exact match`. If the expected substring is absent or the grep misses a stale `iki/üç/3-way` reference, the plan does not stop or require a broader sweep; the final positive grep for `simplify-claude-codex` would not prove stale text was removed.
  Recommendation: Make an empty or incomplete catalog a hard stop, then add negative sweeps after Task 12 for stale terms such as `iki komut`, `üç komut`, `3-way`, and old directional Check A wording in all three mirror files.

- **[medium] F4: Manual `/simplify` sweep can leave spec-required active references stale** (plan lines 696-730)
  The plan says historical/negative references should be left untouched, but the spec says execute-plan should update `Adım 16 Şablon A` and all other `/simplify` references. Current execute-plan hits include overview/contract/notes references beyond the two examples, so the plan's loose classification plus `yalnız historical varsa kalır` escape hatch can leave user-facing references to the deprecated command while still passing the positive `/simplify-claude-codex` hit check.
  Recommendation: Inventory the exact current hit line numbers in the plan and provide an explicit whitelist for any allowed residual `/simplify` references. Make Task 15 fail on every non-whitelisted `/simplify` hit.

- **[medium] F5: Runtime smoke failure is allowed to collapse into `SMOKE_RAN=no` and still commit** (plan lines 860-867)
  Task 15 treats smoke as best-effort and only records `SMOKE_RAN=yes/no`; it does not define a failing runtime invocation as a blocking state. If the command appears after restart but fails before scope/mode prompts, the plan can still proceed to the commit message with `Smoke runtime: no` or an ambiguous value, shipping a slash command that structurally greps correctly but does not run.
  Recommendation: Split smoke into `not-run`, `pass`, and `fail`. If the runtime is available and invocation fails, block Task 15 Step 9 until the failure is fixed or explicitly documented as an override with a recovery path.

- **[medium] F6: /tmp snapshot is a fragile cross-task dependency** (plan lines 52-59)
  Task 1 stores the canonical protocol in `/tmp/codex-call-protocol.snapshot`, Task 3 appends from it, and Task 12 diffs against it. If the executor session restarts or `/tmp` is cleaned, `cat`/`diff` fail or compare against a missing file, and the plan only mentions re-snapshotting after a diff failure in Task 3. This undermines the claimed contract-first defense because the early canonical copy depends on ephemeral state.
  Recommendation: Recompute the canonical block inline before each use or store the snapshot in a task-local repo path with an existence/marker-count guard. Add `test -s` and marker-count checks before every `cat` or `diff` that consumes the snapshot.

### Next steps (Codex'in özeti)

- Fix the commit path model first; the current plan cannot produce the claimed atomic commit.
- Replace prose-only spec appends with extract-and-diff verification.
- Harden Task 12, Task 13, smoke, and snapshot failure paths before execution.

---

## Plan Review Turn 2 — 2026-05-31 (Adım 12, post-turn-1-refine)

Target: working tree diff
Verdict: **needs-attention**

No-ship: the refine closes the repo/global commit split and several sweep gates, but the main drift-prevention and audit claims still have executable gaps.

### Findings

- **[high] F7: Spec append drift check is still policy text, not a task gate** (plan lines 29-44)
  The plan defines a sed+diff pattern with `<N>`/`<NEXT>` placeholders, then explicitly says individual tasks do not repeat it. The affected append tasks, for example Task 4, only require appending spec sections and then run grep-based checks; there is no checklist step that executes the section diff after each append. An executor can complete Task 4/5/7/8/9/10/11 while never proving the copied prose matches the spec, which is the same failure mode F2 was meant to block.
  Recommendation: Add explicit verification substeps inside each affected task with concrete sed ranges for that task's Adım numbers, and make any diff or unreviewed semantic delta a hard stop before the next task.

- **[medium] F8: Inline recompute paths lack marker-count guards before awk extraction** (plan lines 732-744)
  Task 12 Step 4 switched from the /tmp snapshot to inline awk, but it does not guard that spec/write-plan/execute each have exactly one BEGIN and one END marker before extracting. If a marker is missing or duplicated, awk extraction can produce empty or malformed comparison input, and this task can report the wrong failure surface or pass a bad invariant until a later structural sweep. This does not satisfy the F6 requirement to guard marker counts before each recompute.
  Recommendation: Prepend a marker-count loop to every inline awk recompute block, including Task 12 Step 4 and Task 15 Check A, and exit nonzero unless each compared file reports exactly 2 markers.

- **[medium] F9: Smoke result can remain a literal placeholder in the final audit commit** (plan lines 973-1032)
  Step 8 says to store `<SMOKE_STATE>`, but Step 9's commit command embeds a static heredoc containing `Smoke runtime: <not-run | pass | fail-override-<gerekçe>>`. There is no command substitution, required manual replacement, or post-commit assertion that the placeholder was resolved. The audit commit can therefore claim all drift verification ran while leaving the runtime smoke state unknown, which weakens the fail/override trail F5 was intended to create.
  Recommendation: Make Step 9 construct the commit message from the actual SMOKE_STATE variable or require replacing the placeholder plus a grep guard that fails if `<not-run | pass | fail-override` remains in the commit message template.

### Next steps (Codex'in özeti)

- Make the section-diff checks concrete and task-local.
- Add marker guards before all awk-based recomputes.
- Bind the smoke state into the commit/audit text with a hard placeholder check.

---

## Plan Review Turn 3 — 2026-05-31 (Adım 12, post-turn-2-refine)

Target: working tree diff
Verdict: **needs-attention**

No-ship: F8 is operationally closed, but F7 and F9 still have executable gaps. The plan can miss section drift, has a non-operational rollback path for the shared generated command file, and still instructs a literal smoke placeholder commit before showing the corrected command.

### Findings

- **[high] F10: Task 11.5 rollback path cannot restore only the failed Adım section** (plan lines 741-749)
  Task 11.5 says to roll back the affected task and rebuild only that task, but Tasks 4-11 all append into the same `~/.claude/commands/simplify-claude-codex.md` file, and the pre-flight backups only cover the four pre-existing command files, not this new generated file. Inference: if `adim-5` fails, `cp /tmp/<command>.bak ~/.claude/commands/<command>` is either undefined for `simplify-claude-codex.md` or restores a coarse file snapshot, forcing cascade rebuild and risking loss of prior accepted sections.
  Recommendation: Create per-task or per-section snapshots of `simplify-claude-codex.md` before each append task, or replace rollback with an explicit rebuild-from-clean procedure that names exactly which completed tasks must be replayed after a failed section.

- **[medium] F11: Section diff gate truncates evidence before manual classification** (plan lines 711-728)
  The new F7 gate pipes each section diff through `head -50`. For long Adım sections, any unacceptable drift after the first 50 diff lines is not shown to the executor, yet the next step relies on manual accept/reject classification. That leaves the same class of prose drift F7 was meant to block, especially because the markdown prose is the implementation.
  Recommendation: Write full per-section diffs to files, require each diff file to be fully reviewed, and record an accept/reject line per section. Avoid `head` in the blocking gate.

- **[medium] F12: Commit step still runs the placeholder commit before the fixed SMOKE_STATE flow** (plan lines 1130-1164)
  Step 9 first presents a runnable `git commit` block whose message contains `Smoke runtime: __SMOKE_STATE_PLACEHOLDER__`. Only after that commit and post-check does the plan introduce the corrected `COMMIT_BODY` flow using `${SMOKE_STATE}`. An executor following the Run blocks in order will create a bad audit commit and then fail after the damage, weakening the F9 closure.
  Recommendation: Remove the literal-placeholder commit block entirely. Make the only executable commit path build `COMMIT_BODY` from `${SMOKE_STATE}`, validate it before `git commit`, then run the post-commit grep as a second guard.

### Next steps (Codex'in özeti)

- Replace Task 11.5 rollback with precise per-section recovery semantics.
- Make the section diff gate non-truncated and auditable.
- Collapse Task 15 Step 9 to one pre-validated `SMOKE_STATE` commit command.

---
