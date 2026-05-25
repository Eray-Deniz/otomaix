# Codex Adversarial Plan Review Log — /write-plan-claude-codex bootstrap plan

## Turn 1 — 2026-05-25 (working-tree)

Verdict: needs-attention

NO-SHIP: the plan mutates the live canonical /spec-claude-codex command before creating the replacement, but its acceptance checks do not prove the existing command still works. Verification gaps can let stale /write-plan refs or incomplete protocol degradation ship unnoticed.

Findings:
- [high] Task 0 can break the live canonical command without a real rollback or behavior check (plan:36-61)
  Task 0 edits global, already-live spec-claude-codex.md before the new command exists, replacing command-specific protocol refs with placeholders. Only verification is non-empty extraction + token count; doesn't prove /spec-claude-codex still binds <CALL>/<STEP_A>/<STEP_B>, preserves Adım 2/6 semantics, or degradation routing. No backup/diff/smoke/rollback.
  Recommendation: pre-edit backup + post-edit semantic verification (exactly one marker block; binding values for Adım 2 and Adım 6; preserved task/adversarial-review usage; preserved degradation choices) + rollback restoring backup on failure.
- [medium] Drift Check B omits the spec-required degradation-options check (plan:103-108)
  Spec Check B = required tokens PLUS the 3 degradation options; Task 2 only greps 5 tokens. A copied block could lose AskUserQuestion degradation choices and still pass.
  Recommendation: verify all three degradation choices explicitly (Claude-only continue / retry / stop); fail on any missing.
- [medium] Occurrence sweep verification can miss retained live /write-plan references (plan:131-140)
  Acceptance grep drops any line containing write-plan-claude-codex; a line with both the new command and a bare /write-plan hides the stale ref. Also no retained-occurrence classification.
  Recommendation: occurrence-level extraction; classify each match live/example/dated/stub; fail if any live remains; don't filter whole lines just because they also contain the new command.

Next steps:
- Block approval until Task 0 has rollback + behavior-preservation checks; tighten Task 2/3 verification to prove acceptance criteria.

---
## Fixes applied (turn 1 findings → plan v2) — 2026-05-25

- [high] Task 0: added pre-edit backup (/tmp/spec-claude-codex.md.bak) + post-edit behavior
  checks (single marker block; tokens; 3 degradation options; binding Adım 2/6; task+adversarial
  preserved) + rollback (restore backup on any FAIL).
- [medium] Task 2 Check B: added the 3 degradation-option grep (Claude-only / Tekrar dene / durdur).
- [medium] Task 3: replaced line-filtering grep -v with PCRE negative-lookahead
  `/write-plan(?!-claude-codex)\b` (occurrence-level; catches bare ref even on lines with the new
  command); example/dated files deliberately excluded from the live-surface assertion.

Note: bootstrap was scoped by the user to 1 Codex review. These fixes implement Codex's exact
recommendations but were NOT re-reviewed (turn 2 skipped per scope). Plan finalized:
plan-approved, codex_plan_review_iterations: 1.

---
## Turn 2 — 2026-05-25 (relayed Codex review; Claude verified each finding)

Findings (3) and Claude's verified disposition:
- [high] Task 3 verification regex "won't catch refs" — VERIFIED OVERSTATED + cleaned up.
  Test: the eval+literal-quote form actually matched all 5 current /write-plan refs (eval
  consumes the quotes on second parse). Claim "won't catch most" is technically false. BUT the
  eval + nested-quote + tilde-in-$LIVE form is fragile/unreadable → adopted the clean form
  `grep -rnoP '/write-plan(?!-claude-codex)\b' "$HOME/..."` (no eval, $HOME not ~).
  Disposition: targeted fix applied (codex_plan_targeted_fixes 0→1).
- [medium] plan-approved on a needs-attention review without re-review.
  Disposition: this relayed Codex pass IS effectively the re-review; it surfaced only the
  (functional) regex fragility + one false positive — no blocking issue. plan-approved holds.
- [medium] Plan precondition vs spec frontmatter drift (spec still "approved").
  VERIFIED FALSE POSITIVE: actual spec line 6 = codex_review_status: approved-by-iteration-limit
  (changed in the spec's earlier post-finalization correction); plan precondition also says
  approved-by-iteration-limit. No drift. Codex read a stale version. No action.

Net: 1 of 3 actionable (regex cleanup). Plan remains plan-approved, iterations 1, targeted-fixes 1.

---
