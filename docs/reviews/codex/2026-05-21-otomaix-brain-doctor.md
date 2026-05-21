# Codex Adversarial Review Log — Otomaix Brain Doctor v1

## Özet (run sonucu — self-contained audit)

| Alan | Değer | Kaynak |
|---|---|---|
| Review turları | 4 | bu log (Turn 1–4) |
| Final verdict | `approve` (Turn 4) | bu log |
| Full design iterations | 2 | spec frontmatter `codex_review_iterations: 2` (source-of-truth) |
| Targeted consistency fixes | 1 | bu log: Turn 3→4 arası tek odaklı link-resolution (basename-only) fix; frontmatter'a yazılmaz (komut Adım 8) |
| İterasyon limiti | 3 | /spec-claude-codex politika sabiti (dosya alanı değil) |
| Bulgu trendi | T1: 5 (1H/3M/1L) → T2: 3 (1H/2M) → T3: 1 (1M) → T4: 0 | aşağıdaki turlar |

> Not: "Full design iteration" (mimari/lifecycle/schema/rol değişikliği) ile "targeted fix"
> (tek kontrol logic/wording) ayrımı Claude'un sınıflandırmasıdır. Round A (5 fix) + Round B
> (3 fix) = full iteration; Round C (basename-only) = targeted. Frontmatter sadece full
> iteration sayar.

---

## Turn 1 — 2026-05-21 (working-tree, draft)

Target: working tree diff
Verdict: needs-attention

No-ship: the spec has blocking design contradictions around write behavior, category IDs, and link resolution, plus its "grounded" vault baseline does not match the real vault read during review.

Findings:
- [high] Default execution is not read-only despite the stated decision (spec:49-183)
  Section 3 says v1 is read-only because there is no --fix, but Section 8 defaults --output-dir to <vault>/_health and writes report.md/report.json. Recommendation: default truly non-writing (stdout / outside vault), explicit flag for vault file output.
- [medium] Config category ID does not match the checks table (spec:105-135)
  Config defines index_mismatch_missing_file, checks table names it index_mismatch (eksik dosya). Severity map miss → false-negative. Recommendation: one canonical category ID everywhere + test.
- [medium] Basename fallback can silently resolve a link to the wrong page (spec:152-156)
  First-match basename lookup unsafe for growing taxonomy. Recommendation: basename match valid only when unique; emit ambiguous_link when >1 page shares basename.
- [medium] The "grounded" vault baseline is stale against the real vault (spec:57-67)
  Fresh read: 123 md, 118 frontmatter, vendor=7, active=107, unverified=77, last-verified=117. Spec claimed vendor=9, active=109, unverified=79, 120 frontmatter, last-verified=119. Recommendation: regenerate; mark counts non-invariant.
- [low] Test plan hides external dependency while claiming zero deps (spec:195-201)
  "zero dependency → python -m pytest" but pytest is not stdlib. Recommendation: stdlib unittest or declare dev dep.

Next steps: fix write-boundary; normalize category IDs + test; refresh/remove grounded counts.

---

## Turn 2 — 2026-05-21 (working-tree, revised after 5 fixes)

Target: working tree diff
Verdict: needs-attention

No-ship: the five prior issues are mostly addressed, but the write-boundary fix is still vulnerable because the default repo report path is relative, and link/category rules still contain drift that can produce false failures or missed severity mapping.

Findings:
- [high] Relative default report path can still write into the vault (spec:82-85)
  default_report_dir and CLI default are relative paths. If brain-doctor is run from /root/otomaix-brain or any other cwd, tooling/brain-doctor/reports resolves under that cwd, not necessarily under /root/otomaix → reintroduces the trust-boundary failure. Recommendation: resolve default_report_dir relative to config file/repo root or absolute; add a guard rejecting any resolved output path under vault_path unless explicit --allow-vault-output.
- [medium] Extensionless full-path wikilinks can become ambiguous before exact .md resolution (spec:164-168)
  Resolution tries basename matching before the .md appended attempt. A fully qualified link like [[apps/crm/architecture/deploy]] can be reported ambiguous_link before exact apps/crm/architecture/deploy.md is tried → blocking false positives. Recommendation: try exact/source-relative paths as-written and with .md appended before any basename fallback; ambiguous_link only for basename-only candidates.
- [medium] Stale index_mismatch name still contradicts the canonical category ID (spec:220-223)
  Config + checks table use index_mismatch_missing_file, but the risk section still names index_mismatch. Spec says emitted categories must match config.severity → stale label can cause an unmapped category. Recommendation: rename open-point to index_mismatch_missing_file + test extracting every category-like identifier and verifying it exists in severity.

Next steps: fix default output path anchoring + vault-output guard; correct link resolution ordering; remove remaining index_mismatch drift from Section 11.

---

## Turn 3 — 2026-05-21 (working-tree, revised after Turn-2 fixes)

Target: working tree diff
Verdict: needs-attention

No-ship: two Turn-2 fixes are resolved, but the link-resolution fix still leaves a false-negative path where wrong fully qualified links can be accepted by basename fallback.

Findings:
- [medium] Path-qualified broken links can still be silently accepted by basename fallback (spec:168-174)
  Section 7 now tries exact and .md-appended paths before basename fallback and avoids ambiguous_link before exact resolution. But it still sends any unresolved target to basename fallback. A path-qualified typo like [[apps/crm/wrong/deploy]] can fail exact/source-relative checks, then resolve to a unique deploy.md elsewhere and be treated valid. Recommendation: basename fallback only when target has no path separator; if a target contains / and exact/source-relative fail, emit broken_wikilink/broken_md_link; reserve ambiguous_link for basename-only targets with multiple matches.

Confirmed resolved: repo-root default report path + vault-output guard (Turn-2 write-boundary); canonical index_mismatch_missing_file (no stale index_mismatch found).

Next steps: tighten basename fallback to basename-only targets before shipping as v1 design spec.

---

## Turn 4 — 2026-05-21 (working-tree, revised after Turn-3 fix)

Target: working tree diff
Verdict: approve

Ship as a v1 DESIGN spec. The Turn-3 issue is genuinely resolved: section 7 now limits basename fallback to targets with no `/`, reports path-qualified failures as broken_wikilink/broken_md_link, and reserves ambiguous_link for basename-only collisions. Final sweep found no material config/checks/link/CLI transcription drift.

No material findings.

Evidence: direct read of untracked spec; section 5 severity JSON parsed; section 6 table categories match config.severity 16/16 with no severity mismatches; no stale bare index_mismatch references remain.

---

