---
title: Codex Review Scope Contract + Structured Recommendation + execute-plan 8.6 Auto-Continue
status: proposed     # proposed | active | blocked | waiting-review | done | archived | cancelled
started: 2026-06-04
last-touched: 2026-06-04
blocked-by: null
source_spec: docs/specs/2026-06-04-codex-review-scope-contract.md
source_plan: docs/plans/2026-06-04-codex-review-scope-contract.md
---

# Goal

claude-codex komut ailesine 7-way byte-identical `CODEX-REVIEW-SCOPE-CONTRACT` bloğu ekle (pinned
scope + per-command requirement-source binding + dependency scope + command-policy external-overlay +
coverage statement + her finding'e structured fix recommendation), yeni iki-katmanlı drift **Check E**
ile kilitle; AUTO-FIX'i **her turda** structured recommendation'a çevir (4-way); execute-plan
**Adım 8.6**'yı clean-checkpoint auto-continue'ya yeniden yaz. **Başarı kriteri:** Check A/B/C/D + yeni
Check E PASS (byte-lock + section-anchored marker hard-gates), stale "Tur 4+/max review 3" sweep=0,
7 komut smoke-parse, S-1 harness PASS, scenario trace tutarlı. **Ana invariant:** predecessor'ın
"binding≠procedure" hatasını tekrar etme — blok deklare edip prosedürü/prompt gövdesini wire'lamamak
yasak (Check E marker-anchored hard-gate bunu kanıtlar).

# References

- Spec: `docs/specs/2026-06-04-codex-review-scope-contract.md` — **spec-approved / codex_review_status: approved** (Codex 5 tur, F1-F6 çözüldü)
- Plan: `docs/plans/2026-06-04-codex-review-scope-contract.md` — **plan-approved / approved** (Codex plan-review 5 tur, P1-P8 çözüldü; finalize 2026-06-04)
- Codex review logları: `docs/reviews/codex/2026-06-04-codex-review-scope-contract.md` (spec, 5 tur) + `...-codex-review-scope-contract-plan.md` (plan, 5 tur)
- Review/Security: _(yok — execution sonrası /review-claude-codex + /security-review-claude-codex)_

# Current Status

**Spec + Plan FINALIZE edildi + commit edildi; execute bekliyor.** Bu oturumda: `/spec-claude-codex`
(5 Codex turu → spec-approved/approved) → `/write-plan-claude-codex` (5 Codex turu → turn 5 approve) →
kullanıcı onayıyla plan finalize (`plan-approved` + `approved`, 2026-06-04) → commit (docs-only, **push
YOK**). Komut dosyaları (deliverable, repo-DIŞı `~/.claude/commands/*.md`) HENÜZ DEĞİŞMEDİ — execution
başlamadı. **Sonraki adım:** `/execute-plan-claude-codex <plan>` (status proposed → active execute başında).

# Open Problems

- **[residual — static ceiling, kabul edildi]** Check E WIRING'i hard-gate'liyor (concrete token,
  section-anchored, no placeholder, co-located, prompt-body asks, 8.6 clean-no-gate). **Procedure
  correctness** (ref-correctness + overlay-procedure-correctness) statik kanıtlanamaz → execution
  Codex review (spec §6 Katman 6) + plan Task 4 Step 5 manuel + Task 7 confirmation. Bu bilinçli
  tavan, advisory downgrade değil.

# Decisions Log

- 2026-06-04: **A1 mimarisi** seçildi (kullanıcı explicit): yeni `CODEX-REVIEW-SCOPE-CONTRACT` 7-way
  byte-identical blok + yeni Check E. Red: A2 (mevcut blokları genişlet — CALL-PROTOCOL review-olmayan
  task --fresh'te de kullanılıyor, enforcement bölünür), A3 (prose-only — binding≠procedure riski).
- 2026-06-04: **3 kullanıcı refinement'ı** spec'e işlendi: (1) external-overlay secret-scan helper
  komut-bazlı (SCAN-SUBSTRATE taşıyan `_css_secret_scan` reuse; taşımayan reviewer eşdeğer guard) +
  reviewer overlay context-only işaretli; (2) `last_checkpoint_ref` DAR mechanical exemption (yalnız
  HANDOFF Verification.last_checkpoint_ref = POST_CP_HEAD; lifecycle/status/decision DEĞİL); (3)
  finish-branch advisory/report-only vocab (closure-blocker/warning/note; auto-fix'e dönüşmez).
- 2026-06-04: **Check E iki katmanlı** (kullanıcı onayı): byte-lock (7-way cmp + token) hard-gate +
  **marker-anchored section assertions** hard-gate (`REVIEW-SCOPE-BINDING:<slug>` region: concrete
  pinned-ref + overlay guard terms + asks + no-placeholder + co-location + prompt-body asks; delimited
  `8.6-CLEAN-PATH` no-user-gate). Prose/semantic → advisory-tripwire. Marker-anchoring, predecessor'ın
  "blok var ama prosedür eski" hatasının plan-seviyesinde tekrarını (Codex plan-review P1-P8) çözdü.
- 2026-06-04: **AUTO-FIX değişikliği:** "Tur 4+" → **her review turunda** structured recommendation;
  7-alan format yalnız CONTRACT bloğunda tanımlı, AUTO-FIX referans eder (format drift imkânsız). 4-way
  byte-identical korunur (Check D re-verify). Stale "Tur 4+/Tur 1-3" sweep (spec/write-plan 3'er,
  execute 6, simplify 4; reviewer'lar 0). "max review 3" yalnız AUTO-FIX bloğundaki "geçersiz" negation.
- 2026-06-04: **Commit boundary:** deliverable repo-DIŞı (`~/.claude/commands/*.md`, uncommitted);
  repo-içi committable = `docs/tools/claude-codex-drift-check.sh` + docs (spec/plan/review/active).
  `plan-claude-codex.md` (deprecated alias) 7-way sete DAHİL DEĞİL.
- 2026-06-04: **Plan finalize = `approved`** (kullanıcı onayı, "finalize as approved"). `iterations=4`
  (≥3) olmasına rağmen `approved-by-iteration-limit` DEĞİL — Codex turn 5 temiz approve verdi, 4 iterasyon
  fix-required otonom döngü kaynaklı (Auto-Fix policy: 3-limit fix-required'a uygulanmaz). unresolved
  critical/high = none. Ardından docs-only commit (push YOK).
- 2026-06-04: Vault promotion YAPILMADI — closure'a (P1) bırakıldı.
