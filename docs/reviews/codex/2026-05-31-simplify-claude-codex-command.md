# Codex Review Log — simplify-claude-codex command spec

Spec: `docs/specs/2026-05-31-simplify-claude-codex-command.md`

---

## Pre-scoping Turn — 2026-05-31 (Adım 2)

(Codex'in 1b çıktısı; tasarım yönü seçiminden önce paralel perspektif.)

### 1. Alternative Approaches

**A. Full execute-plan-style mirror**

Main shape: new `/simplify-claude-codex` becomes a proper gated workflow: scope selection, mode choice, optional Codex pre-scan, Claude applies fixes, test/verification loop, mandatory Codex final adversarial review, critical/high guard, then one local commit.

Trade-offs:
- Best matches the existing command family and invariant discipline.
- Easier to reason about final-review-not-run vs final-review-stopped exits.
- Heavier than old `/simplify`; may feel overbuilt for small cleanup.
- Needs careful scope/base tracking because simplify is not plan-backed.

**B. Minimal Codex graft on existing `/simplify`**

Main shape: keep the current 5-category scanner mostly intact, add optional `task --fresh` before fixes and mandatory `adversarial-review` before commit.

Trade-offs:
- Lowest migration cost.
- Preserves fast inline-refactor ergonomics.
- Riskier: old command has loose state, loose scope accounting, and per-fix testing assumptions.
- Harder to enforce "no commit unless final Codex review ran" without bolting on a mini state machine.

**C. Simplify orchestrator / wrapper**

Main shape: `/simplify-claude-codex` only orchestrates: scope, risk class, Codex calls, gates, commit. The actual scan/fix behavior is delegated to reusable sections copied from deprecated `/simplify`.

Trade-offs:
- Clean separation between "scanner policy" and "Claude+Codex governance."
- Makes future drift easier: old `/simplify` can become a stub, scanner rules live in one place.
- More abstract than needed unless more commands will reuse the pattern.
- Must avoid making the wrapper so generic that simplification-specific risks get diluted.

Recommendation: **A with selective reuse from old `/simplify`**. Treat this as a small execution workflow, not a patch to the old command.

### 2. Top Risks / Unknowns

**Risk 1: Two Codex turns can turn a fast cleanup into a fuzzy execution workflow.**

The old command acts immediately on a bounded diff. Adding optional pre-scan plus mandatory final review creates state questions: what is the base ref, what exact diff does Codex review, what happens after fixes from final review, and whether the final review must rerun after every change. Without explicit loop rules, the invariant can be bypassed accidentally.

**Risk 2: "Do not apply" as high-risk escalation is useful but semantically sharp.**

Interpreting Codex "do not apply" as high-risk, not veto, keeps Claude in control. But it needs a strict rule: the item must not be applied unless the user explicitly approves that specific item. Otherwise "high-risk escalation" becomes a label with no blocking force.

**Risk 3: Cross-file "noted, not fixed" can create false completeness.**

DRY findings often cross the selected scope boundary. If out-of-scope duplication is only noted, the final report must distinguish:
- fixed simplifications inside scope
- noted external duplication
- intentionally deferred risk

Otherwise the command may claim simplification while leaving the actual abstraction pressure unresolved elsewhere.

Specific concern: **no-test-suite + high-risk default block with override** is reasonable, but the override text must be loud and narrow. It should approve named changes, not "continue anyway" globally.

### 3. Key Questions Before Design

1. **Should `/simplify-claude-codex` be idempotent by contract?**

If yes: after a completed run, rerunning on the same scope should find no same-class fixable issues except explicitly deferred items. That requires a stronger final sweep and clearer "deferred/noted" recording. If no: it can remain opportunistic cleanup, but reports must avoid implying exhaustive simplification.

2. **Can the command rewrite tests, or only production code?**

If tests are in scope, simplification may delete duplicated test setup, rename helpers, or consolidate fixtures, which raises regression risk and requires test-specific review criteria. If tests are read-only except for mechanical updates, the command is safer but may leave a lot of cleanup untouched.

3. **If a fix creates a new file, does that file enter the same run's simplification scope?**

Example: extracting a helper to remove duplication. The new helper may itself be over-abstracted, badly named, or unused after later edits. If new files enter scope, the command needs an intra-run rescan rule. If not, final Codex review must explicitly check new-helper-call-count and over-abstraction before commit.

---

## Final Adversarial Review Turn 1 — 2026-05-31 (Adım 6)

Target: working tree diff
Verdict: **needs-attention**

No-ship: the spec still has behavior-level contradictions that can silently drop Codex vetoes, misreport dirty working trees, and promise resume behavior it explicitly does not implement.

### Findings

- **[high] Codex veto token is not stable across prompt, synthesis, and decision log** (spec lines 177-204)
  Step 5 tells Codex to emit `DO_NOT_APPLY: <candidate-id>`, Step 6 defines synthesis for `DO_NOT_APPLY: <claude-id>`, while the decision log says the canonical format is `DO_NOT_APPLY: <id>`. This is exactly the kind of transcription drift the spec says it is avoiding: an implementation that keys matching on the written token can fail to bind a Codex veto to the Claude candidate, allowing a blocked simplification to proceed as ordinary low/medium/high work.
  Recommendation: Use one canonical token everywhere, preferably `DO_NOT_APPLY: <id>`, and state that `<id>` must equal the Step 3 candidate id format such as `DRY-1`. Add a synthesis rule for malformed or unknown ids: default block, not ignore.

- **[high] No-fixes branch can falsely claim no working-tree changes when the command was invoked on an existing dirty tree** (spec lines 303-332)
  The main scope default is `git diff` when uncommitted changes exist, but the no-fixes edge case says Step 7-8-9 are skipped and reports `Final Codex review: not-run (no working-tree changes to review)` and `Commit: NOT performed (nothing to commit)`. That only holds if the tree was clean before the command. Failure scenario: user runs simplify on a dirty working tree, rejects all candidates, and gets a report saying there are no working-tree changes and next step is `/review` on current HEAD, even though the original uncommitted diff still exists and was never final-reviewed by Codex in this flow.
  Recommendation: Track initial dirty state and applied-fix count separately. Only use the current no-fixes template when both initial and final working trees are clean; otherwise report `no simplification fixes applied; existing working-tree changes unchanged`, include the dirty file count, and avoid claiming nothing to review/commit.

- **[high] B1/B2 tell users to resume, but the implementation notes say resume does not exist** (spec lines 432-465)
  The failure templates and next-step rules repeatedly say `/simplify-claude-codex <SCOPE>` is a `resume`, including after final review did not run or after unresolved critical/high findings. Later the spec says simplify has no resume concept and a repeat invocation starts from scratch, treating half-applied fixes as normal uncommitted scope. That is a real recovery-path bug: after a timeout or guard stop, the next run may discard the prior review context, approvals, dropped candidates, and audit trail while presenting itself as continuation.
  Recommendation: Either implement durable resume state for B1/B2 or remove all `resume` language. If rerun-from-scratch is intentional, templates must say so and require preserving/linking the previous review log and unresolved findings before any later commit gate.

- **[medium] Y2/B rejection is not supported by the spec's own blast radius** (spec line 35)
  The spec rejects the minimal graft partly because it would lose family consistency, but the chosen Y1/A path stubs the existing `/simplify`, creates a new ~500-line command, and edits three existing family commands plus a 4-file exact-block drift contract. That increases cross-command migration and drift risk, while the stated 100-150 line saving dismissal is not backed by any implementation constraint in the spec. The dropped alternative may actually have lower user-visible risk if `/simplify` remains the stable entry point with final review and commit gate grafted on.
  Recommendation: Re-open Y2/B with an explicit tradeoff table: files changed, compatibility behavior for existing `/simplify` users, required gates, and drift checks. If Y1/A remains chosen, make `/simplify` delegate to the new command instead of becoming a no-op stub.

- **[medium] No-test PASS discipline leaks through the final report template** (spec lines 282-295)
  Step 7 says when `<TEST_SUITE_PRESENT> = false`, scoped verification degrades to lint/format only and no `PASS` claim is allowed. The completed report still prints `Scoped verification (per-batch): <PASS/FAIL özet>` next to `Final tests: PASS | not-run`, which invites exactly the forbidden shorthand in no-test runs. This weakens the spec's verification contract and can produce a misleading completed report for untested high-risk mechanical rewrites.
  Recommendation: Split verification labels by test-suite state: use `scoped checks: lint/format OK; tests not-run` when no suite exists, and reserve `PASS` only for actual test command output that was run and read.

### Next steps (Codex'in özeti)

- Fix the token contract before implementation; it is the highest-risk silent failure.
- Resolve the no-fixes and B1/B2 lifecycle contradictions before writing the command.
- Re-open or strengthen the Y1/A vs Y2/B decision with concrete blast-radius evidence.

---

## Final Adversarial Review Turn 2 — 2026-05-31 (Adım 6, post-refine)

Target: working tree diff
Verdict: **needs-attention**

No-ship: the refine fixed several textual drifts (turn-1 H1/H3/M1/M2 substantially closed; H2 partially closed at report layer but operational gate missing), but it still leaves executable contradictions around no-fixes dirty trees, no-test reporting, and review-log chaining that can mislead recovery/audit flows.

### Findings

- **[high] Initial dirty + no fixes still routes through the dirty working-tree review path** (spec lines 337-351)
  The H2 fix says no-fixes handling must branch on `<INITIAL_TREE_DIRTY>`, and Variant B reports that final Codex review did not run because this simplify run produced no changes. But Step 9's actual scope decision still keys only on current `git status --short`; for an initially dirty tree with `<FIXES_APPLIED>=0`, that condition is true and sets `SCOPE="--scope working-tree"`. That makes the operational path contradict the Variant B report and can either review/block unrelated pre-existing work or produce the wrong final report depending on which paragraph the implementer follows.
  Recommendation: Make the first Step 9 branch explicit: if `<FIXES_APPLIED> = 0`, skip Codex final review and jump to the correct Variant A/B report before checking `git status`; only prepare `--scope working-tree` when this run applied at least one fix.

- **[medium] B2 still leaks unconditional PASS when no test suite exists** (spec lines 507-520)
  The completed template was made test-suite-aware, but the stopped-after-final-review template still prints `Final tests: PASS` unconditionally. In a repo with `<TEST_SUITE_PRESENT> = false`, Step 8 is skipped and must report `not-run`; B2 is a real report path after final review ran and the user stopped at the guard, so this still violates the no-test PASS discipline.
  Recommendation: Make B2 use the same test-suite-aware wording as Şablon A: `Final tests: PASS` only when tests actually ran, otherwise `Final tests: not-run (no test suite detected)`.

- **[medium] Previous-attempt log chaining cannot work with the specified deterministic log filename** (spec lines 617-623)
  B1/B2 say the next run creates a new log file and preserves the previous attempt by adding `Previous attempt: ...` at the top. But the implementation notes define the log as `docs/reviews/codex/<DATE>-simplify-<SCOPE_SLUG>.md`, and Step 5/9 append turns into that same path. Running simplify multiple times on the same date and scope therefore reuses the same file, so the 'new log file' either does not exist or links to itself. That breaks the audit trail the B1/B2 fix relies on.
  Recommendation: Add a unique attempt component to the log filename, such as timestamp or monotonic attempt number, and define how the new file resolves and links the immediately previous attempt for the same scope.

- **[low] Review metadata undercounts the refine pass it claims to summarize** (spec lines 6-8)
  The frontmatter says `codex_targeted_fixes: 2`, but the Decisions Log row #9 explicitly says the refine addressed H1, H2, H3, M1, and M2. If downstream review bookkeeping trusts this metadata, the spec under-reports the targeted fix count and weakens the audit trail for this turn.
  Recommendation: Set `codex_targeted_fixes` to match the five turn-1 findings addressed, or rename the field so `2` clearly means review iteration/turn rather than targeted fixes.

### Next steps (Codex'in özeti)

- Resolve the Step 9 `<FIXES_APPLIED>` gate before implementation.
- Sweep all final report templates for test-suite-aware PASS/not-run wording, not just Şablon A.
- Make Codex review log filenames unique per attempt before relying on previous-attempt links.

---

## Final Adversarial Review Turn 3 — 2026-05-31 (Adım 6, post-turn-2-refine)

Target: working tree diff
Verdict: **needs-attention** (no critical/high — first turn with no blocking findings)

No-ship: turn-2 fixes mostly landed, but the refine introduced/left audit-path drift and an executable log-initialization gap that can break override traceability and previous-attempt chaining.

### Findings

- **[medium] Override audit still writes to the old non-attempt log path** (spec line ~454)
  The new canonical review log path includes `-<ATTEMPT>.md`, but the critical/high override branch still writes the explicit audit line to `docs/reviews/codex/<DATE>-simplify-<SCOPE_SLUG>.md`. In an unresolved critical/high override, the commit message points users to the review log while the required override audit entry can land in a different file from the final review log. That breaks the traceability needed to justify shipping with unresolved high-severity findings.
  Recommendation: Change the override audit path to `docs/reviews/codex/<DATE>-simplify-<SCOPE_SLUG>-<ATTEMPT>.md` and make the commit `override-note` reference that exact attempted log path.

- **[medium] Previous-attempt first-line chaining is not operationally tied to log creation** (spec lines ~649-655)
  The spec defines ATTEMPT counting and says a rerun's new log file must start with `Previous attempt: ...`, but Step 5 and Step 9 only say to append review sections to the log. There is no required log-initialization step before the first append, no mkdir step, and no guard that writes the first-line link before `## Pre-scan Turn` or `## Final Review Turn`. On a missing `docs/reviews/codex` directory the append can fail; on B1/B2 reruns the first append can create a file whose first line is the turn heading instead of the previous-attempt link, silently breaking the audit chain F3 was meant to fix.
  Recommendation: Add an explicit early log setup step before any Codex call: `mkdir -p docs/reviews/codex`, compute ATTEMPT, create the log file, and if `ATTEMPT > 1` write the `Previous attempt:` header before any later append.

- **[low] B1 allows a `ran-FAIL` state that the flow does not define as reachable** (spec lines ~511-516)
  B1 is the final-review-not-run template, but its final-tests enum includes `ran-FAIL`. Step 8 says final test failure routes back to Step 7 problem handling and does not proceed to final review; the B1 reason list also does not include final-test failure. This leaves implementers two inconsistent choices: emit B1 for a failed-test stop without a defined reason, or keep looping and never use `ran-FAIL`. The impact is recovery ambiguity after a failed final test, especially because B1's next step says run from scratch rather than describing the failed verification state.
  Recommendation: Remove `ran-FAIL` from B1, or add an explicit Step 8 stop/report path with a matching B1 reason such as `final-tests-failed-user-stop` and a recovery instruction that preserves the failed verification details.

### Next steps (Codex'in özeti)

- Fix the remaining old log path at line ~454.
- Add an explicit log initialization step before Step 5/Step 9 append behavior.
- Clarify or remove the B1 `ran-FAIL` state.

---
