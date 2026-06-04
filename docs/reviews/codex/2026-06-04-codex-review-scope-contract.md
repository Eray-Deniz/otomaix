## Turn 1 — 2026-06-04 (working-tree scope)

# Codex Adversarial Review
Target: working tree diff
Verdict: needs-attention

No-ship: the spec still leaves the same declared-but-not-wired failure mode open, and its cross-command contract collides with security-review isolation/independence assumptions.

Findings:
- [high] F1 Per-command wiring tripwire still cannot prove the procedures were rewired (§6/§7). Check E byte-locks block + greps tokens; can PASS while call path computes no pinned SHA, skips overlay/dependency, leaves 8.6 old question. Fix: command-specific checks asserting pinned-ref before Codex invocation, overlay setup in command-policy mode, 8.6 no AskUserQuestion on clean/low paths.
- [high] F2 Security-review forced into requirement sources it explicitly rejected (§3.2 requirement-sources). security-review design says active-task open problems NOT injected upfront + spec/plan NOT inputs. Literal 7-way block breaks independence OR bindings mark N/A weakening invariant. Fix: contract requires per-command requirement-source BINDING + coverage; security-review binds to security scope, documents spec/plan as intentionally N/A. Fallback: split into common review-output contract + per-archetype scope contracts.
- [high] F3 External command overlay reintroduces live untracked state into isolated substrates (§3.4). security full/path git-less export (committed HEAD snapshot) would include live home-dir command files (secrets/stale), coverage reports pinned/context-only. No hard guard for export mode, no coverage_gap recompute, only worktree overlays labeled. Fix: one reusable external-overlay guard (allowlist + secret scan + symlink confinement + dest for $SCAN_ROOT & $REVIEW_WT + export-mode labeling + post-overlay coverage accounting). Fallback: don't copy for security full/path export; separate command-policy mode with own sanitized temp root.
- [medium] F4 last_checkpoint_ref exemption can dirty/race active layer (§3.5/§5.2). Doesn't define committed-vs-uncommitted, unrelated-HANDOFF protection, tree-clean-after. Uncommitted→next batch dirty+ref-before-mutation; committed→HEAD≠reviewed code. Fix: exact pre/postconditions (task unchanged, no unrelated dirty HANDOFF, patch only Verification.last_checkpoint_ref, decide committed-vs-uncommitted, re-run git status, define HEAD/ref after write).
- [medium] F5 4th 7-way block not justified vs extending CALL-PROTOCOL (§3.1). Increases drift surface; Check A & Check E pass independently while block far from actual call. Fix: explicit decision table A1 vs extend-CALL-PROTOCOL vs A2/A3 + Check E verify co-location/order with Codex call at each call-site.

Next steps: block plan generation until wiring-verification, security-review requirement-source, external-overlay, last_checkpoint_ref gaps closed.

---
## Turn 2 — 2026-06-04 (working-tree scope, re-review)

# Codex Adversarial Review
Verdict: needs-attention
F1, F2, F5 materially CLOSED. F3 OPEN (symlink/realpath). F4 OPEN (dirty active-layer contradiction).

Findings:
- [high] F3(cont) External overlay allowlist bypassable via symlinked command files (§3.4:178-185). Glob allowlist treated as trust boundary without source realpath/type validation. A symlink matching `*-claude-codex.md` can point outside the commands dir; post-copy symlink-sweep is too late. Fix: pre-copy source validation — non-following glob, reject non-regular-file, require realpath under ~/.claude/commands/, THEN secret-scan + copy (no symlink follow). Verify: temp symlink fake-claude-codex.md → outside; helper must exclude/report, not copy target bytes. Fallback: don't overlay; pass sanitized content as context-only prompt text after validation.
- [medium] F4(cont) last_checkpoint_ref protocol cannot both preserve unrelated dirty HANDOFF edits AND end clean (§3.5:218-232). If unrelated dirty edits exist: commit includes them (violates single-field carve-out) OR they stay dirty (violates clean-tree). Active-layer integrity hole. Fix: unrelated dirty docs/active = hard DUR before mutation; require `git status --porcelain -- docs/active` clean except intended patch, then stage/commit only that, re-check clean. Verify: add unrelated HANDOFF edit before 8.6 → expect stop/report, no commit, no auto-continue. Fallback: skip auto mutation, ask user whenever docs/active not clean.

Next: §3.4 pre-copy realpath/regular-file validation; §3.5/§5.2 unrelated-dirty → hard DUR.

---
## Turn 3 — 2026-06-04 (working-tree scope, re-review)

# Codex Adversarial Review
Verdict: needs-attention
F3 CLOSED (all 3 substrate topologies). F4 dirty-contradiction CLOSED. No critical/high remain.
NEW:
- [medium] F6 last_checkpoint_ref defined as two different SHAs → next-batch scope ambiguous (§3.5:216-244). Exemption box + step1 capture = post-checkpoint HEAD (POST_CP_HEAD, pre-docs-write); step4 = "commit sonrası HEAD". Different commits. Fix: choose one canonical value, name consistently. (Note: field cannot equal its own commit SHA — circular.) Verify: rg ref terminology, all occurrences same semantics. Fallback: two fields checkpoint_task_head + last_checkpoint_ref.

Next: fix SHA semantics §3.5/§7, re-run ref-terminology sweep.

---
## Turn 4 — 2026-06-04 (working-tree scope, convergence check)

# Codex Adversarial Review
Verdict: needs-attention
F1-F5 confirmed NOT regressed (layered verification, per-command requirement binding + security
independence, external-overlay realpath/regular-file/export isolation, dirty-active hard DUR,
block-justification + co-location all present). No critical/high remain.
NEW (same cluster F6 residual):
- [medium] F6(residual) §5.2 still says "ref = commit-sonrası HEAD" — stale sibling site not swept
  after §3.5 F6 rewrite → reintroduces two-SHA ambiguity. Fix: §5.2 → POST_CP_HEAD. (Claude note:
  my earlier sweep grep used "commit sonrası" space-variant; §5.2 had hyphen "commit-sonrası" → missed.)

Fixed §5.2 → POST_CP_HEAD; full hyphen+space ref sweep = 0 stale ref-value assignments.

---
## Turn 5 — 2026-06-04 (working-tree scope, confirmation)

# Codex Adversarial Review
Verdict: approve
No critical/high/medium findings remain. F6 closed (§3.5/§5.2/§7 all POST_CP_HEAD, non-circular,
captured-before-write, committed-after). F1-F5 not regressed. No material findings.
Note: implementation review must still verify the actual 7 command files (this pass = spec only).

---
