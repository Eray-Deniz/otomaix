# Codex Adversarial Review — finish-branch-claude-codex spec

Spec: docs/specs/2026-06-02-finish-branch-claude-codex-command.md

## Turn 1 — 2026-06-02

Target: working tree diff
Verdict: needs-attention

No-ship: the spec leaves destructive delete and mainline push paths exposed to stale or mis-scoped audit evidence, and the rejected STEP_B rationale is not strong enough to justify losing diff-bound symmetry.

Findings:
- [high] Coverage check can falsely mark a whole branch reviewed when only HEAD matches (:112-121)
  Reports carry REVIEW_BASE_SHA..HEAD_SHA, but the decisive check parses only report_HEAD and compares ancestry/equality with audit_HEAD. That proves the report reached the same tip, not that it covered the audit range. A report for HEAD~1..HEAD would pass equality against audit_HEAD even if finish-branch scope is origin/main..HEAD or merge-base(BASE,HEAD)..HEAD, leaving earlier branch commits unreviewed while closure proceeds as covered.
  Recommendation: Require range containment: parse report_BASE and report_HEAD, then prove report_HEAD == audit_HEAD and report_BASE is ancestor-of-or-equal audit_BASE. If either SHA absent or bases incomparable, emit coverage-uncertain.
- [high] D=sil blocker upgrade depends on an action unknown when blockers are classified (:120-218)
  Audit runs before option selection, but closure-blocker definitions include action-dependent cases (coverage-uncertain + destructive action; unmerged/unpushed in D=sil). At audit time destructive action is unknown, so the same condition may be emitted as warning. Adım 8 only upgrades confirmation if a closure-blocker was already detected, no reclassification after user chooses D. Failure: audit reports coverage-uncertain as warning, user selects D=sil, standard 'discard' remains accepted despite the intended exception.
  Recommendation: Two-phase blocker derivation: Codex emits action-neutral facts, Claude reclassifies against selected action before confirmation. Define coverage-uncertain/unmerged/unpushed as D=sil confirmation blockers regardless of Codex's original label.
- [high] Mainline mode still has a live-HEAD race despite claiming no worktree needed (:96-103)
  task --fresh has no --head and reads live HEAD; spec exempts mainline from pinned worktree because finish-branch does not run merge/checkout there. That does not close the race: a user/hook/background tool/second terminal can commit/amend/rebase while Codex runs (up to timeout) or between evidence collection and push. Evidence, Codex audit, and pushed HEAD can diverge.
  Recommendation: Use pinned worktree OR explicit pre/post HEAD_SHA equality guard for mainline. If HEAD changes after evidence collection or Codex returns, invalidate audit and recompute before any push/PR/destructive action.
- [medium] Mode detection relies on undefined session concept, can choose wrong closure topology (:179-188)
  Mainline = branch==main/default and 'no separate feature branch', example tied to this session. 'No separate feature branch' is not a deterministic git predicate. Long-lived integration branch, stale origin default, renamed default, default-branch hotfix could misclassify, changing isolation, scope, and available branch ops. Misclassification expensive (mainline removes pinned worktree).
  Recommendation: Replace session-semantic test with explicit git predicates: current branch, upstream, remote default ref, ahead/behind, whether current == configured default branch. When ambiguous, stop and ask user.
- [medium] Rejecting STEP_B is under-argued, sacrifices the only base-bound diff primitive (:69-81)
  Dropped because adversarial-review sees only diff and uses severity vocabulary, but chosen design already injects task-state evidence into a prompt and asks Codex to inspect hygiene/divergence. STEP_B could receive closure-only instructions + task-state evidence while retaining base-bound diff symmetry. Dropping it relies on prompt discipline + Claude-computed summaries — weaker for the exact failure class (unreviewed/out-of-range changes).
  Recommendation: Reopen as hybrid OR documented proof that STEP_A receives exact diff/range snapshot and reports only over that range. If STEP_B stays rejected, add explicit compensating controls for diff-bound scope and output vocabulary enforcement.

Next steps:
- Fix range-coverage proof before relying on report freshness.
- Make destructive-action blocker reclassification deterministic after user selection.
- Reconsider mainline isolation and STEP_B rejection.

---

## Turn 2 — 2026-06-02

Target: working tree diff
Verdict: needs-attention

No-ship: Turn 1 #1, #2 core reclassification, #4, #5 materially resolved; revised spec still leaves destructive discard and mainline push exposed through audit-skip and live-HEAD TOCTOU. Turn 1 #3 only partially resolved.

Findings:
- [high] Pre-selection C(tut) audit skip can bypass D=sil blocker upgrade (:229-230)
  Adım 5 allows audit skip when a pre-selection C(tut) tendency is "clear", before the user actually selects. If user later chooses D=sil, Adım 8 falls back to standard `discard` with only a 'blocker kontrol edilmedi' note. Real path where coverage-uncertain/unmerged/unpushed facts are never collected and destructive discard gets normal confirmation despite blockers likely existing. Two-phase fix is airtight only when facts were collected.
  Recommendation: Remove the pre-selection C(tut) audit skip, or make it conditional on an explicit user choice of C before audit. If audit skipped for any non-explicit reason and user later chooses D=sil, require upgraded destructive confirmation or rerun audit before D.
- [high] Mainline HEAD guard is still a check-then-act race before push/PR/destructive (:119-125)
  Pin HEAD_SHA + equality check before push fixes stale evidence detected before the check, but does not bind the subsequent operation to the pinned SHA. Another terminal/hook can commit/amend/rebase after the equality check but before live-branch `git push`, so the command acts on a different HEAD than audited. Same failure class as Turn 1 #3, narrowed to the final check-then-act window.
  Recommendation: Outward/destructive ops must target the pinned object, not live HEAD: push `${HEAD_SHA}:<upstream-branch>` after guard; PR/branch metadata use pinned SHA. Else pinned worktree for mainline too, or repeat equality check inside the action sequence.

Resolution of Turn 1 findings:
- #1 range containment: RESOLVED (incl. absent-SHA + incomparable-base -> coverage-uncertain).
- #2 two-phase classification: resolved when facts exist, but blocked by new pre-selection audit-skip path.
- #3 mainline guard: PARTIAL; stale evidence invalidated, final live-HEAD TOCTOU remains.
- #4 mode detection: RESOLVED (stop-and-ask on ambiguity).
- #5 STEP_B rejection: RESOLVED (schema vocab control + range snapshot compensation; no blocking finding).

---

## Turn 3 — 2026-06-02

Target: working tree diff
Verdict: needs-attention

No-ship: Turn 2 audit-skip resolved, push/merge targeting improved, but destructive discard is still not pinned; branch deletion can act on a live ref after the audited SHA changes.

Findings:
- [high] Destructive discard still deletes a live branch ref instead of the audited object (:276-289)
  Spec claims all outward/destructive ops target pinned HEAD_SHA, but the concrete binding only names push,
  merge, PR/metadata. Adım 8 branch-op binding narrows to merge/push/PR then proceeds to D=sil confirmation
  without an atomic delete bound to HEAD_SHA. Preserved finish-branch behavior still uses checkout + branch
  delete by name. If another terminal advances the feature branch after the pre-op guard but before deletion,
  D=sil can delete unaudited/unclassified commits with only standard confirmation when original audited facts
  had no blockers. Same check-then-act class for the highest-risk path: irreversible discard.
  Recommendation: Define D=sil as old-value-bound ref op, not branch-name delete. Normal branches: delete only
  if refs/heads/<branch> still equals HEAD_SHA (e.g. git update-ref -d refs/heads/<branch> $HEAD_SHA after
  checkout); abort/recompute if diverged. State detached behavior separately.

Resolution of Turn 2 findings:
- T2 #1 pre-selection audit-skip bypass: RESOLVED (C-skip removed; degrade+D=sil defensive retry/warning).
- T2 #2 push/merge TOCTOU: RESOLVED for push & merge (pinned-target refspec); discard binding was MISSED -> this finding.

---

## Turn 4 — 2026-06-02

Target: working tree diff
Verdict: approve

Ship: the Turn 3 discard TOCTOU is closed. Karar 3 and Adım 8 both bind D=sil to `git update-ref -d refs/heads/<branch> $HEAD_SHA`, abort/recompute on divergence, detached stated separately. No remaining high/critical live-ref destructive or outward path across push/merge/PR/discard.

No material findings. APPROVED.

Convergence: Turn 1 (5 findings) -> Turn 2 (2) -> Turn 3 (1) -> Turn 4 (0, approve).

---
