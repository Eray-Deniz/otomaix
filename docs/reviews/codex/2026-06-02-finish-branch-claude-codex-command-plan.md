# Codex Adversarial Plan Review — finish-branch-claude-codex

Plan: docs/plans/2026-06-02-finish-branch-claude-codex-command.md
Spec: docs/specs/2026-06-02-finish-branch-claude-codex-command.md

## Turn 1 — 2026-06-02

Target: working tree diff
Verdict: needs-attention

No-ship: the plan can produce a repo-external destructive/outward-facing command while its own verification can false-pass missing security mechanics.

Findings:
- [high] Spec-fidelity check is too weak to catch missing destructive-safety mechanics (Task 4, :186-191)
  Task 4 requires translating high-risk spec mechanics into a 600+ line repo-external command, but the only
  coverage gate is a whole-file grep count of eight broad tokens. That can pass if tokens appear in summaries,
  drift prose, or repeated invariant text while the command omits section-specific behavior: deterministic mode
  ambiguity handling, real `task --fresh --cwd $SCAN_ROOT` binding, pre/post HEAD guards, exact range-containment,
  pinned push/merge targets, D=sil reclassification. The final smoke suite can report fresh evidence even when
  the command is missing the safeguards meant to prevent stale-audit push/merge or irreversible branch deletion.
  Recommendation: section-scoped verification commands for every critical mechanic (model after sibling plan):
  extract Adım 1/5/8 sections and assert concrete predicates — mode detection, worktree pinning, Codex invocation,
  report_HEAD==audit_HEAD + merge-base ancestry, pre-op guard, pinned refspecs, update-ref -d old-value delete,
  upgraded discard text. Any miss fails the task before final smoke.
- [medium] Docs-only audit commit can accidentally capture unrelated documentation state (Task 8, :297-303)
  Final commit uses `git add docs/`. In a dirty worktree this stages unrelated docs/ changes (active-layer,
  other plans/reviews), making the audit commit non-reproducible and potentially mutating task state outside
  this plan's scope. Repo already has an untracked docs plan -> not a no-op risk.
  Recommendation: explicit allowlist for plan/spec/review-log files + verify staged set with
  git diff --cached --name-only before committing.

Next steps:
- Strengthen Task 4 and Task 8 verification gates before implementation.
- Constrain the audit commit staging set to explicit docs paths.

---

## Turn 2 — 2026-06-02

Target: working tree diff
Verdict: needs-attention

No-ship: Turn 1 high only partially fixed; plan can still report section-gate PASS while omitting isolation/CWD mechanics.

Findings:
- [high] Section gates still false-pass missing worktree isolation and Codex CWD binding (Task 4, :197-204)
  Step 7 scopes Adım 1/5/8 but never extracts Adım 4, never asserts `git worktree add --detach $HEAD_SHA` or
  `--cwd $SCAN_ROOT`/`--cwd $WT`. The Adım 5 HEAD guard predicate passes on prose like `HEAD_SHA pin` without the
  executable guard form. A command could pass ALL SECTION GATES PASS while Codex audits the live project root
  instead of the pinned detached worktree, reopening the stale/dirty HEAD race before push/merge/delete.
  Recommendation: section gates for Adım 4 + Adım 5 requiring `git worktree add --detach $HEAD_SHA`, selected
  SCAN_ROOT/WT, `task --fresh` with `--cwd $SCAN_ROOT`, explicit `git rev-parse HEAD == HEAD_SHA` post-call/pre-op
  guard. Avoid prose-only `HEAD_SHA.*pin`.
- [medium] Staged-set verification is observational, not a hard commit gate (Task 8, :324-330)
  Allowlist fixes broad add risk, but `git diff --cached --name-only` only prints before commit. If the index
  already has unrelated staged docs or the agent misses a mismatch, the commit includes them. Plan says stop on
  unexpected, but the command sequence does not enforce it.
  Recommendation: hard allowlist assertion before commit — compare staged set against the four expected paths,
  exit nonzero on any extra/missing path.

Resolution of Turn 1:
- T1 high (broad grep -> section-scoped): partial — sections added but Adım 4 isolation + executable HEAD/CWD ungated.
- T1 medium (git add docs/ -> allowlist): mostly resolved, but staged check is print-only not fail-closed.

---

## Turn 3 — 2026-06-02

Target: working tree diff
Verdict: needs-attention

No-ship: staged-set gate now fail-closed, but the isolation gate can still pass a command that creates a detached worktree and then audits the live root.

Findings:
- [high] Isolation gate still does not prove the pinned worktree is the Codex CWD (:197-204)
  Adım 4/5 gates require `worktree add --detach`, some SCAN_ROOT/--cwd token, and `cwd.*SCAN_ROOT`, but never assert
  the critical binding: normal mode must set SCAN_ROOT=$WT and create the worktree at $HEAD_SHA. A command could
  pass while doing `git worktree add --detach "$WT"` (no HEAD_SHA), SCAN_ROOT=$PROJECT_ROOT, `--cwd $SCAN_ROOT` —
  auditing the live root while the pinned worktree is unused, preserving the stale/dirty HEAD race.
  Recommendation: require explicit normal-mode binding: `worktree add --detach.*HEAD_SHA`, `SCAN_ROOT=.*WT`, and
  Adım 5 `--cwd "$SCAN_ROOT"`. Keep mainline as the separate allowed SCAN_ROOT=$PROJECT_ROOT branch.

Resolution of Turn 2:
- T2 high (Adım 4 isolation + CWD/HEAD gates): partial — gates added but normal-mode SCAN_ROOT=$WT + worktree@HEAD_SHA binding still not proven.
- T2 medium (fail-closed staged set): RESOLVED (git reset -q + hard allowlist assertion, exit 1 on mismatch).

---

## Turn 4 — 2026-06-02

Target: working tree diff
Verdict: approve

APPROVE: Turn 3 high resolved. Task 4 Step 2 now explicitly binds normal mode to worktree@HEAD_SHA + SCAN_ROOT=$WT,
mainline to SCAN_ROOT=$PROJECT_ROOT, Codex to --cwd $SCAN_ROOT; the section gate separately requires
`worktree add --detach.*HEAD_SHA`, `SCAN_ROOT=.*WT`, `SCAN_ROOT=.*PROJECT_ROOT`, plus Adım 5 `cwd.*SCAN_ROOT`.
A normal-mode implementation auditing PROJECT_ROOT instead of pinned WT would fail the gated chain. Awk ranges
section-bound, spec alignment intact, restart-required honesty preserved.

No material findings. APPROVED.

Convergence: Turn 1 (2 findings) -> Turn 2 (2) -> Turn 3 (1) -> Turn 4 (0, approve).

---
