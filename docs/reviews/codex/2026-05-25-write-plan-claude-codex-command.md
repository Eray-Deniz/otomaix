# Codex Adversarial Review Log — /write-plan-claude-codex spec

## Turn 1 — 2026-05-25 (working-tree)

# Codex Adversarial Review

Target: working tree diff
Verdict: needs-attention

No-ship: the spec’s chosen architecture still has unclosed bootstrap, drift, fallback, and resume hazards that can produce stale or duplicate planning artifacts while appearing review-gated.

Findings:
- [high] Chosen approach C is specified without an actual embedded protocol or enforceable canonical marker (docs/specs/2026-05-25-write-plan-claude-codex-command.md:56-63)
  The spec rejects shared protocol extraction because runtime file references can silently break, then chooses embedded protocol plus drift-sweep. But the spec only records a note/checklist item, not the full protocol body to embed or any machine-checkable source marker. This leaves implementers dependent on copying unstated details from `/spec-claude-codex`, so the first command can ship with a partial or stale Codex call protocol while still satisfying the written spec. Inference: this directly undercuts the stated reason for rejecting approach B and makes C not defensible as written.
  Recommendation: Either include the full Codex Call Protocol verbatim in this spec with explicit allowed adaptations, or switch to approach B with an explicit runtime read/preflight. Add a concrete drift check such as comparing a marked protocol block hash or running a scripted diff between the two command files before finalization.
- [high] Small-scope fallback points users at a command the same spec deprecates into a stub (docs/specs/2026-05-25-write-plan-claude-codex-command.md:71-72)
  The flow includes an overkill pre-check asking whether to run the full flow or plain `/write-plan`, but the core decision and stub section say the old `/write-plan` will become only a deprecated redirect to `/write-plan-claude-codex`. A user choosing the lightweight path after migration can land in a circular redirect or lose the only lightweight implementation-planning route. This is a user-visible workflow regression hidden inside the happy-path full command design.
  Recommendation: Define the lightweight path as an explicit mode inside `/write-plan-claude-codex`, or keep `/write-plan` as a functional legacy implementation planner instead of a pure stub. Update the flow and stub contract so there is exactly one non-circular behavior.
- [high] Resume-safe state machine lacks discovery rules, so reruns can duplicate or reopen the wrong plan (docs/specs/2026-05-25-write-plan-claude-codex-command.md:128-168)
  The spec claims resume-safe frontmatter, but the flow only says “Resume kontrolü” and the schema only defines fields after a new plan exists. It does not say how to locate an existing plan for the same `source_spec`, how to handle old `/write-plan` plans with no `status` or `codex_plan_*` fields, or how to choose between multiple drafts for one spec. A retry after bootstrap, interruption, or manual edits can create a second plan or reset counters incorrectly while still appearing compliant.
  Recommendation: Add a resume discovery algorithm: scan `docs/plans/` by `source_spec`, slug, and status; classify missing-frontmatter legacy plans; require user selection on multiple matches; and define atomic migration of legacy plan metadata before any new draft is written.
- [medium] The 7-surface sweep is not complete enough to prevent stale live guidance (docs/specs/2026-05-25-write-plan-claude-codex-command.md:198-217)
  The sweep lists only files, not the individual references inside them, and the immutable list only explicitly classifies two example references. Tool output shows several live references in the listed workflow page and command files that use `/write-plan` as an active next step or command table entry. Without a per-reference classification, the implementation can update some occurrences, leave others as deprecated live guidance, and still claim the 7 files were swept.
  Recommendation: Replace the file-level sweep with an occurrence-level table: path, line/pattern, classification `live|stub|dated|example`, desired replacement, and reason for every retained `/write-plan` reference. Include `~/.claude/commands/write-plan.md` as the stub surface in the same checklist.
- [medium] Bootstrap is left unresolved even though the available bootstrap path lacks the new spec’s safety guarantees (docs/specs/2026-05-25-write-plan-claude-codex-command.md:249-253)
  The spec says the plan that creates this command will be written by old `/write-plan` before stubbing or manually, and that details will be clarified during plan/execution. The current old command does not enforce approved-spec metadata, plan review frontmatter, Codex plan review, source override audit, or the new state machine. That means the first artifact implementing the safety-critical command can be produced through the exact weak path this spec is intended to retire.
  Recommendation: Close bootstrap in the spec before approval: require a one-off manual bootstrap checklist that applies the new frontmatter, approval check, Codex adversarial review, and audit log to the bootstrap plan, or temporarily run old `/write-plan` only under documented extra gates.
- [medium] `--scope working-tree` tolerates noisy dirty state that can mask plan-specific review failures (docs/specs/2026-05-25-write-plan-claude-codex-command.md:108-114)
  G15 assumes the plan is normally uncommitted and therefore uses `--scope working-tree`, while unrelated dirty files are merely warned about and tolerated. In a real implementation session, command edits, vault docs, stub changes, and the plan can all be dirty together. The review context can then be dominated by unrelated diffs, or Codex can spend review budget on non-plan changes, while the command still treats the plan as reviewed. The prompt focus on `<PLAN_PATH>` reduces but does not remove this failure mode.
  Recommendation: Require isolation before plan review: either stage/review only `<PLAN_PATH>` plus its review log, use an explicit path-scoped review mechanism if the companion supports it, or block and ask the user to commit/stash unrelated dirty files instead of only warning.

Next steps:
- Block approval until the spec defines the embedded protocol concretely, resolves the `/write-plan` fallback contradiction, and adds resume/bootstrap acceptance criteria.
- Run an occurrence-level `/write-plan` reference sweep before implementation planning, not as a best-effort closure note.

---

## Turn 2 — 2026-05-25 (working-tree, revision addressing turn-1 findings)

# Codex Adversarial Review

Target: working tree diff
Verdict: needs-attention

No-ship: prior findings 2, 3, 4, and 5 are materially resolved; finding 1 is only partially resolved because byte-identical drift can still be byte-identical wrong; finding 6 is not fully resolved because noisy working-tree review remains an allowed approval path. The revision also introduces state-machine and lightweight-path holes that can produce unreviewed or corrupt plans while appearing command-compliant.

Findings:
- [high] Byte-identical protocol drift check can pass with a truncated or non-operational protocol (sec 2:63-77)
  diff=0 only compares the two command files to each other; both could copy the same incomplete block (no timeout/exit-code/AGENTS preflight/degradation) and still pass. Same failure mode as turn 1, reduced from unmarked drift to synchronized wrongness.
  Recommendation: Put the full required CODEX-CALL-PROTOCOL body in this spec, or define a concrete validator checking required markers/commands/exit-code branches in addition to byte equality. Include the exact extraction command.
- [high] Lightweight path produces reviewless plans without a valid state-machine outcome (sec Adım 4:115-119)
  Fast plan has no codex_plan_review_* gating, but the state machine only defines reviewed approval states; plan-approved means Codex reviewed. Spec doesn't define the fast plan's frontmatter, executability, whether it stays plan-draft+pending, or how hardening resumes it. The canonical command can emit a usable-looking plan outside its own approval invariant.
  Recommendation: Define a separate explicit status/review state (e.g., codex_plan_review_status: not-run, execute disabled) or remove the lightweight output path.
- [medium] Resume classification accepts forbidden metadata pairs instead of repairing or blocking them (sec 5:176-199)
  Resume marks any file with codex_plan_review_status: pending as resumable regardless of status, so plan-approved+pending (and plan-draft+approved) silently resume from an invalid state.
  Recommendation: Make allowed-pair validation the first resume step; illegal pair → block + explicit atomic repair before classifying.
- [medium] Noisy working-tree review remains an approval path (sec 4 R1:131-139)
  Isolation is only an option; user can continue noisy and still reach plan-approved. Final state records only that Codex reviewed, not whether review was isolated.
  Recommendation: Make isolation mandatory when unrelated dirty files exist, or record review_scope/isolation metadata and forbid plan-approved from noisy review unless an explicit risk override is stored in frontmatter/audit.

Next steps:
- Block approval until protocol validation, lightweight-plan state, illegal-pair resume handling, and review isolation semantics are tightened.
- After edits, rerun a line-referenced review against the full spec.

---

## Turn 3 — 2026-05-25 (working-tree, revision addressing turn-2 findings)

# Codex Adversarial Review
Verdict: needs-attention

No-ship. Finding 4 resolved. Finding 3 resolved for explicit forbidden pairs but new validation order regresses legacy migration. Findings 1 and 2 only partially resolved.

Findings:
- [high] Token checklist still allows synchronized non-operational Codex protocol (sec 2:56-77)
  Check B only requires strings to appear; tokens can sit in comments/dead prose and still pass A+B. Spec lacks the actual protocol body or an executable validator.
  Recommendation: embed the full canonical body, or replace grep-only completeness with a concrete structural validator.
- [high] Lightweight path still produces executable unreviewed plans (sec Adım 4:112-121)
  not-run fixes the label, but the plan is executable and /execute-plan is unchanged, so a user can run a not-run plan with no Codex gate — runnable instructions through the weak path the command is meant to retire.
  Recommendation: make not-run non-executable (block before /execute-plan), or remove the lightweight output, or stop presenting the workflow as review-gated.
- [medium] Resume pair-validation conflicts with legacy migration (sec 5:190-201)
  Legacy files (missing codex_plan_* fields) have no valid pair, so pair-validation can block them before the legacy-migration branch is reached.
  Recommendation: classify legacy BEFORE pair-validation; define exact atomic migration target.

Next steps:
- Block approval until protocol validation is structural; decide not-run executability; reorder resume so legacy precedes pair-validation.

---

## Turn 4 — 2026-05-25 (working-tree, final iteration; spec iteration limit reached)

# Codex Adversarial Review
Verdict: needs-attention

NOT SHIPPABLE: turn-3 findings 2 and 3 resolved in spec text; finding 1 still blocks because the directional-canonical check depends on a live canonical marker block that does not currently exist.

Findings:
- [high] Directional drift check is non-actionable against the current canonical command (sec 2:56-69)
  Check A depends on extracting a delimited CODEX-CALL-PROTOCOL block from ~/.claude/commands/spec-claude-codex.md, but the current canonical command has NO CODEX-CALL-PROTOCOL:BEGIN/END markers (verified via rg: protocol content like codex-companion.mjs and timeout 480s present, markers absent). Primary guarantee cannot pass unless implementers silently mutate the canonical first; spec does not list canonical normalization as an in-scope step/acceptance item.
  Recommendation: Add an explicit in-scope prerequisite to normalize spec-claude-codex.md with the exact CODEX-CALL-PROTOCOL markers before creating the new command, and an acceptance check that canonical extraction returns a non-empty block before diffing.

Resolved confirmations:
- Turn-3 finding 2 (lightweight executable plan): removal complete; no not-run executable path remains.
- Turn-3 finding 3 (resume legacy ordering): legacy-before-pair-validation now correct.

Next steps:
- Add canonical marker normalization (in-scope) + non-empty extraction acceptance, then Check A is actionable.

---

## Turn 5 — 2026-05-25 (working-tree, final verification)

# Codex Adversarial Review
Verdict: approve

SHIPPABLE: no critical/high findings. Turn-4 high closed: section 2 makes canonical marker normalization in-scope before new command creation and gates Check A on non-empty canonical extraction; section 8 includes the same-package note. No new contradiction with out-of-scope (/spec-claude-codex behavior unchanged; marker normalization is an implementation/sweep edit). Turn-3 finding 2 resolved (lightweight exits without artifact). Turn-3 finding 3 resolved (legacy precedes pair-validation).

No material findings.

---
## Post-finalization correction — 2026-05-25 (Codex consistency catch)

- [medium] Frontmatter codex_review_status: approved + codex_review_iterations: 3 violated the
  /spec-claude-codex rule (iteration >= 3 → approved-by-iteration-limit). Iteration count
  re-verified = 3 (correct). Fix: codex_review_status → approved-by-iteration-limit
  (codex_targeted_fixes 1 → 2). Note: turn-5 verdict was a clean "approve" (no critical/high);
  the by-iteration-limit label marks that all 3 design iterations were used, not that issues remain.

---
