## Plan Review Turn 1 — 2026-06-04 (working-tree scope)

# Codex Adversarial Review
Verdict: needs-attention (No-ship)
Coverage: inspected plan + spec + CURRENT.md; external command files outside sandbox (reasoned from plan).

Findings:
- [high] P1 Check E omits mandatory hard-gated assertions from spec (plan §Self-review/Task4). Spec §6 requires section-anchored co-location/pinned-ref/overlay/coverage-rec/8.6 assertions; plan downgraded pinned-ref + prose to advisory and only check_review_scope_wiring counts file-wide tokens → predecessor binding≠procedure failure mode. Fix: concrete per-command awk that extracts the review-call section, locates contract/binding before invocation, asserts pinned ref before call + overlay in command-policy sections; keep only truly-unprovable as advisory. Fallback: if awk can't prove, drop hard-gate claim + add manual acceptance steps.
- [high] P2 Wiring RED test invalid — Task 3 stub satisfies Task 4 check (plan Task3 Step4 / Task4 Step1). Stub contains both 'coverage statement' + 'structured fix recommendation'; check counts file-wide outside-block → passes on stub before prompt wired → RED→GREEN unsound. Fix: remove ask tokens from stub OR make check section-anchored to actual prompt body (prefer latter). 
- [high] P3 8.6 clean-path check can miss forbidden gate (plan Task4 Step3/Task6). Greps only 'Devam edelim mi'; renamed/AskUserQuestion gate passes. Fix: delimited Clean/Low/DUR markers in 8.6, assert no AskUserQuestion/user-prompt in Clean (+Low-only) while allowing in DUR.

Next: rewrite Task 4 RED tests genuine; add branch/section markers; re-run plan review.

---
## Plan Review Turn 2 — 2026-06-04 (working-tree scope, re-review)

# Codex Adversarial Review
Verdict: needs-attention
P2 CLOSED (content-free stub + region-scoped check = genuine RED). P3 sound (delimited clean/DUR).
Findings:
- [high] P4 Spec-required procedure hard gates still downgraded to advisory (plan Task4 Step1/Step5 + self-review). Spec §6/§7 mandate co-location-before-call + pinned-ref-before-call as hard-gate; plan made them advisory → plan/spec mismatch. Fix: restore as hard-gate (parse review-call section, assert contract/binding before invocation + pinned ref before invocation) OR amend spec to allow advisory split. 
- [medium] P5 Task 5 Step 4 tolerates nonexistent RED 8.6 check (plan Task5 Step4). 8.6 assertion now added in Task 6, not Task 4; Task 5 should be fully GREEN/exit=0. Stale expectation from rework → could mask a real Check D/E regression. Fix: Task 5 Step 4 expected = exit=0.

Resolution (Claude): P4 → strengthen check_review_scope_binding with co-location hard-gate (Codex call
token after binding-END within same section → binding precedes call; pinned-ref token in binding →
pinned-ref-before-call). Only ref-CORRECTNESS stays advisory (spec §6 Katman 6 = execution review).
P5 → Task 5 Step 4 expected GREEN/exit=0.

---
## Plan Review Turn 3 — 2026-06-04 (working-tree scope, re-review)

# Codex Adversarial Review
Verdict: needs-attention
P5 CLOSED (Task 5 Step 4 = GREEN/exit=0). P4 partial.
Findings:
- [high] P6 pinned-ref-before-call gate passes on label/prose not concrete pin (plan Task4 check). Check accepts 'pinned target' label alone (template always has it) → trivially passable. Fix: drop label from pin alternation, require concrete ref token (RESOLVED_BASE/BASE_REF/--base/REVIEW_BASE_SHA/HEAD_SHA/REVIEW_WT) + reject angle-bracket/stub placeholders.
- [medium] P7 overlay-setup not hard-gated (plan Task4 check + Task7). Spec §7 lists overlay-setup as Check E assertion; plan only greps 'external-overlay' label + defers guard terms to Task7 prose/manual. Fix: require concrete overlay guard terms (realpath / regular-file / secret-scan / context-only) in binding region.

Resolution (Claude): same cluster "check-e-hardgate-strength" (turns 1/2/3). Apply P6 (concrete ref
token + placeholder reject) + P7 (overlay guard terms in binding) as WIRING hard-gates. Frame:
Check E hard-gates WIRING (concrete tokens, section-anchored, no placeholders, co-located);
PROCEDURE CORRECTNESS (ref-correctness, overlay-procedure-correctness) = execution Codex review
(spec §6 Katman 6). One verify turn (turn 4); if still "too weak" → DUR to user (static ceiling).

---
## Plan Review Turn 4 — 2026-06-04 (working-tree scope, convergence check)

# Codex Adversarial Review
Verdict: needs-attention
P6 + P7 CLOSED (binding-region hard gate: concrete ref token, placeholder reject, overlay guard terms).
Finding:
- [medium] P8 Check E gates binding prose but not the actual Codex prompt-body asks (plan Task4 check vs Task4 Step2 prompt instruction + spec §6/§7). A command could put coverage/fix terms in the binding comment while leaving the heredoc/companion prompt unchanged → binding-declared-not-prompt-wired. Codex: this is a residual WIRING gap (type-a, statically closeable), NOT procedure-correctness ceiling. Fix: add a section-scoped assertion on the actual prompt body (post-binding call section) requiring coverage statement + fix recommendation; RED on stub/old prompts, GREEN after prompt bodies updated.

Resolution (Claude): add coverage+fix-recommendation requirement to the post-binding section ($post)
in check_review_scope_binding → proves the prompt body (after binding, same section) carries the asks,
distinct from the binding region. Last wiring location; convergence healthy (Codex confirmed P6/P7
closed + distinguished wiring from procedure ceiling). One verify turn (turn 5).

---
## Plan Review Turn 5 — 2026-06-04 (working-tree scope, final convergence)

# Codex Adversarial Review
Verdict: approve
P8 CLOSED at the intended static ceiling: Check E gates binding region + separately gates post-binding
same-section prompt-body asks (coverage statement + fix recommendation). Remaining risk = procedure
correctness (NOT a statically-closable wiring gap). No critical/high/medium findings remain. No material findings.

---
