# Codex Review Log — security-review-claude-codex spec (spec-claude-codex Adım 6)

Spec: docs/specs/2026-06-01-security-review-claude-codex-command.md
Scope: --scope working-tree

## Turn 1 — 2026-06-01

# Codex Adversarial Review

Target: working tree diff
Verdict: needs-attention

No-ship: the spec still has design-level holes that can leak excluded secrets, run Codex against the wrong tree, and mark metadata-only output as a completed review.

Findings:
- [high] Pinned-worktree binding conflicts with the byte-identical CODEX-CALL-PROTOCOL (docs/specs/2026-06-01-security-review-claude-codex-command.md:260-273)
  The spec requires the canonical CODEX-CALL-PROTOCOL block to remain byte-identical while also saying Codex must run with `--cwd $REVIEW_WT`. The verified canonical block in the sibling commands still invokes Codex with `--cwd "$PROJECT_ROOT"`; if the new command copies it literally, Codex reviews the main repo rather than the pinned, secret-excluded worktree. If the implementer edits the block to use `$REVIEW_WT`, the 6-way byte-identical drift contract is broken. Impact: dirty-tree isolation, HEAD pinning, and physical secret-exclusion can silently fail in the implementation path.
  Recommendation: Make the canonical protocol accept an explicit `CODEX_CWD`/`CALL_CWD` variable and update all family commands atomically, or state a precise wrapper that preserves the canonical block while overriding cwd before invocation. Add a drift check that asserts the security command actually passes `$REVIEW_WT`.
- [high] Physical `rm` does not actually exclude committed secrets from Codex (docs/specs/2026-06-01-security-review-claude-codex-command.md:190-211)
  The full/path exclusion design assumes removing files from the linked worktree removes Codex's raw access. In a Git worktree, the `.git` file still points to the repository object database; a read-only Codex run can plausibly recover an excluded committed file with commands such as `git show HEAD:path` or by reading Git objects through the worktree gitdir. This is especially dangerous because the spec frames physical `rm` as enforcing access loss and symmetry. Impact: users may choose "Exclude from Codex" believing secrets cannot be sent externally, while the model can still access them through Git metadata.
  Recommendation: For full/path secret exclusion, run Codex in a Git-free exported tree, e.g. `git archive HEAD_SHA` into a temp directory, remove secret paths there, and ensure no `.git` pointer/object database is present. Treat linked worktrees as unsuitable for hard secret exclusion.
- [high] Path confinement validates the user token, not every tracked file it expands to (docs/specs/2026-06-01-security-review-claude-codex-command.md:125-139)
  The path-mode guard checks `realpath -e` on each original token, but directory tokens are allowed via `git ls-files -- "$TOKEN"`. A repo-internal directory can pass realpath confinement while containing tracked symlinks that resolve outside the repo; those expanded files can then be included in `<PATH_SET>` and handed to Claude/Codex. This does not satisfy the stated symlink-escape guarantee and creates a repo-escape/read-leak path under path mode.
  Recommendation: Expand every accepted token to the exact tracked file list first, then run confinement checks on each resolved file path. Reject symlinks in scope or require their resolved targets to remain under `PROJECT_ROOT`; store `<PATH_SET>` as normalized file paths, not raw directory tokens.
- [medium] Metadata-only reviews can still fall through templates that say complete and suggest finish (docs/specs/2026-06-01-security-review-claude-codex-command.md:402-440)
  Adım 3 and Adım 9 say `coverage_gap=true` is not a successful review and should route to re-run, not override. But the reviewer matrix makes coverage_gap orthogonal to A/B/C, and Template A still says "Security review complete (dual)" with a clean-path next step of `/finish-branch`; it only prints `coverage_gap` as a field. A dual run where all raw code was secret-excluded can therefore produce a "complete" final report whose template contains a finish path, contradicting the hard re-run rule. Impact: an operator can close the branch after zero raw code was reviewed.
  Recommendation: Make `coverage_gap=true` a separate terminal template/branch, not an orthogonal flag in Template A/B. Remove any "complete" wording and `/finish-branch` next step from metadata-only output; require re-run with a raw-code scope before chain completion.

Next steps:
- Resolve the cwd/protocol contradiction before implementing the command.
- Redesign secret exclusion around a Git-free exported tree, then update the path-confinement algorithm and metadata-only final templates.

---

## Turn 2 — 2026-06-01 (refined spec re-review)

# Codex Adversarial Review

Target: working tree diff
Verdict: needs-attention

No-ship: Turn 1's cwd/protocol issue is resolved, and the .git object-DB vector is addressed for ordinary files, but the refined spec still overclaims hard isolation for git-archive exports and still contains a stale coverage_gap routing contradiction.

Findings:
- [high] Git-free export still allows symlink escape from the scan root (docs/specs/2026-06-01-security-review-claude-codex-command.md:204-215)
  The spec treats `git archive` into `$EXPORT_DIR` plus absence of `.git` as hard exclusion. That only closes the object-DB vector. `git archive` preserves tracked symlinks, and the path confinement rule only rejects symlinks whose target resolves outside `PROJECT_ROOT`, not symlinks that resolve outside `$EXPORT_DIR`. A tracked symlink to an ignored/local secret under the repo, or an absolute path under `/root/otomaix`, can pass the PROJECT_ROOT check but still let a reviewer in the export follow the link back into the live repo. Impact: full/path mode can leak untracked or secret-excluded files despite the report saying `git-free export` and `hard rm` made raw access impossible.
  Recommendation: For full/path exports, either reject all symlinks in scope, materialize symlinks only after verifying their resolved target is a tracked file inside the exported tree, or run a post-export sweep that removes/rejects any symlink whose `realpath` leaves `$EXPORT_DIR`. State the invariant as `SCAN_ROOT` confinement, not `PROJECT_ROOT` confinement.
- [medium] Path-mode archive pathspec is not shell-safe and can widen or break scope (docs/specs/2026-06-01-security-review-claude-codex-command.md:207-208)
  The path-mode export uses `git archive "$HEAD_SHA" -- $PATH_SET_OR_ALL`. Earlier sections require normalized tracked file paths, but this call expands them through normal shell word splitting and globbing. A tracked path containing whitespace can be split into multiple pathspecs; if one split component is a valid directory/pathspec, the archive can include files outside the approved `<PATH_SET>`, or fail unpredictably.
  Recommendation: Represent `PATH_SET` as a NUL-delimited list or shell array and pass pathspecs without word splitting. If `git archive` cannot safely consume the list, export the full tree into a temp dir, then delete everything not in the verified file allowlist using NUL-safe tooling.
- [medium] Reviewer matrix still routes coverage_gap through A/B/C despite later terminal Şablon D rule (docs/specs/2026-06-01-security-review-claude-codex-command.md:325-336)
  The refined terminal branch says `coverage_gap == true` must not fall into Şablon A/B. But the reviewer-status matrix still says `coverage_gap` is orthogonal to A/B/C and is just a metadata-only banner. An implementer following the matrix can still emit `Security review complete (dual|single)` for a metadata-only run.
  Recommendation: Change the matrix note to say it only applies when `coverage_gap=false`, and add an explicit pre-matrix guard/row: `coverage_gap=true -> Şablon D terminal`, before any dual/single classification.

Next steps:
- Fix export-root symlink confinement before relying on hard secret exclusion.
- Make path-mode archive construction NUL-safe or avoid pathspec archive for allowlisted scopes.
- Remove the stale coverage_gap orthogonal-matrix wording so Şablon D is the only metadata-only route.

---

## Turn 3 — 2026-06-01 (second refine re-review)

# Codex Adversarial Review

Target: working tree diff
Verdict: needs-attention

No-ship: Turn 2's pathspec quoting and coverage_gap matrix wording are resolved, and the symlink sweep itself fails closed for broken/absolute escaping links. But the sweep now creates an unaccounted empty-scope path: path mode can delete the only raw file from the export and still proceed as a completed non-metadata review.

Findings:
- [medium] Symlink sweep can remove all path-mode raw content without setting coverage_gap (docs/specs/2026-06-01-security-review-claude-codex-command.md:216-224)
  The post-export sweep deletes symlinks whose realpath leaves $SCAN_ROOT, but the later coverage_gap rule only treats an empty PATH_SET or all-secret-excluded files as metadata-only. In path mode, a verified tracked symlink can pass the initial PROJECT_ROOT check, be archived as the only PATH_SET entry, then be removed here because it resolves outside the export. PATH_SET remains non-empty and no secret exclusion occurred, so the run can continue with coverage_gap=false even though the scoped raw file is absent from $SCAN_ROOT.
  Recommendation: Record every symlink removed by the sweep, then recompute the inspectable path allowlist from files that still exist under $SCAN_ROOT. If the recomputed allowlist is empty, force coverage_gap=true/Şablon D; alternatively fail closed for path mode when any requested PATH_SET entry is removed by the sweep.

Next steps:
- Resolved: Turn 1 #1, #2, #3, #4 are addressed in the current spec text.
- Resolved: Turn 2 #2 is addressed by quoted PATH_SET array use; no remaining unquoted PATH_SET_OR_ALL-style expansion.
- Resolved: Turn 2 #3 is addressed in Adım 4b, Adım 9, Şablon A/B/D, and the report template at the routing level.
- Partially unresolved: Turn 2 #1's sweep fail-closed logic is sound for broken and absolute escaping symlinks, but its removals are not integrated into coverage_gap accounting.

### Claude disposition (Turn 3)
T3-1 (medium) adreslendi: coverage_gap artık sweep+rm SONRASI $SCAN_ROOT'ta fiilen var olan dosyalardan hesaplanır; path-modunda silinen PATH_SET girdisi fail-closed coverage_gap'e dahil (Adım 3 coverage_gap kontrolü). 0 critical/high kaldı.

---

## Turn 4 — 2026-06-01 (confirmation)

# Codex Adversarial Review

Target: working tree diff
Verdict: approve

Ship-ready from the current spec text: no defensible critical/high/medium blocker found. T3-1 is closed for the path-mode single-symlink case because coverage_gap is recomputed after symlink sweep and secret-rm from files actually present under $SCAN_ROOT, with path-mode removals counted fail-closed. Coverage routing is consistent through Adım 3, Adım 4b pre-matrix guard, Adım 9 0.5, Şablon A/B, Şablon D, and the report template. Prior Turn 1/2/3 findings are stated as resolved and I found no contradictory live body text. The 6-way drift contract math is coherent: 6 files, 5 canonical-vs-mirror diffs, Check B says "altı dosyada", and the spec explicitly uses both STEP_A for full/path and STEP_B for diff while keeping CODEX-CALL-PROTOCOL byte-identical.

No material findings.

Next steps:
- Implementation should preserve the exact post-sweep/post-rm recompute semantics.
- When command files are edited under ~/.claude/commands/, run the specified 6-way drift checks before shipping.

### Claude disposition (Turn 4)
APPROVE — 0 critical/high/medium. Spec finalize: status=spec-approved, codex_review_status=approved (full design iterations 2/3, targeted fixes 1).

---
