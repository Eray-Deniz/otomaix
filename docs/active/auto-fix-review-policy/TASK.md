---
title: Auto-Fix Review Policy — claude-codex aile geneli
status: proposed     # proposed | active | blocked | waiting-review | done | archived | cancelled
started: 2026-06-03
last-touched: 2026-06-03
blocked-by: null
source_plan: docs/plans/2026-06-03-auto-fix-review-policy.md
---

# Goal

claude-codex fix-yapan komutlarına (spec, write-plan, execute-plan, simplify) `claude-confirmed` C/H/M bulgular için kullanıcı-onaysız otonom fix döngüsü ekle (6-tur tavan + global cap=10 backstop); reviewer komutlarını (review, security) report-only disposition/chain-gate diliyle hizala; hepsini `claude-codex-drift-check.sh` Check D (4-way byte-identical AUTO-FIX bloğu + reviewer token + negatif tripwire) ile kilitle. Başarı kriteri: Check A/B/C hâlâ PASS + yeni Check D PASS (byte-for-byte cmp), 6 komut markdown smoke parse, prose senaryo trace tutarlı.

# References

- Spec: `docs/specs/2026-06-03-auto-fix-review-policy.md` (spec-approved, Codex 4 tur)
- Plan: `docs/plans/2026-06-03-auto-fix-review-policy.md` (plan-approved / approved-by-iteration-limit, Codex 4 tur)
- Review: _(yok — execution sonrası /review-claude-codex + /security-review-claude-codex)_

# Current Status

Plan onaylandı (approved-by-iteration-limit), henüz başlanmadı. Sonraki: `/execute-plan-claude-codex docs/plans/2026-06-03-auto-fix-review-policy.md`.

# Open Problems

- **F9 (bilinçli residual):** `check_reviewer_forbidden` wrapped-prose hard-block enumerasyonunu (`hard-block:` + sonraki prose satırı `…/medium`) yakalamıyor. Negatif check spec-ötesi tripwire; residual REPLACE-not-append + manual scenario trace + execution'da Codex reviewer-edit review ile kapsanır. Execution sırasında reviewer prose'u yazarken **hard-block satırı self-contained `hard-block … critical/high` olmalı, medium ayrı `advisory` cümlesinde**.

# Decisions Log

- 2026-06-03: Canonical block = `spec-claude-codex` (mevcut CODEX-CALL-PROTOCOL/SCAN-SUBSTRATE konvansiyonu, drift-check referans-[0]). Strateji: canonical-block-first + awk-extract byte-copy.
- 2026-06-03: Reviewer-negatif-check TRIPWIRE olarak kabul edildi (spec-ötesi gold-plating); F9 wrapped-prose residual dokümante (kullanıcı kararı). `unresolved_high_severity_override: true`.
