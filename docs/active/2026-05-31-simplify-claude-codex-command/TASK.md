---
title: simplify-claude-codex.md komut implementasyonu
status: proposed
started: 2026-05-31
last-touched: 2026-05-31
blocked-by: null
source_plan: docs/plans/2026-05-31-simplify-claude-codex-command.md
---

# Goal

Eski single-actor `/simplify` komutunu Claude-Codex ailesine entegre eden yeni `~/.claude/commands/simplify-claude-codex.md` komutunu implement et — Codex pre-scan + final adversarial review + commit-gated invariant. 5 dosya değişikliği (yeni komut + 3 ayna drift-check 4-way + 1 stub). Başarı kriteri: drift Check A 4-way diff=0 + Check B 8 token presence + structural integrity + smoke pass-or-not-run.

# References

- Spec: `docs/specs/2026-05-31-simplify-claude-codex-command.md` (status: spec-approved, codex_review_status: approved, 3 turn + 13 targeted fix)
- Plan: `docs/plans/2026-05-31-simplify-claude-codex-command.md` (status: plan-approved, codex_plan_review_status: approved-by-iteration-limit, 3 turn + 13 targeted fix)
- Review: `docs/reviews/codex/2026-05-31-simplify-claude-codex-command.md` (spec) + `docs/reviews/codex/2026-05-31-simplify-claude-codex-command-plan.md` (plan)

# Current Status

Plan onaylandı, implementasyon henüz başlanmadı. 16 task (Task 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 11.5, 12, 13, 14, 15) sıralı.

# Open Problems

_(yok)_

# Decisions Log

- **Y1/A — execute-plan-style küçük kuzen** (spec brainstorm): atomic-one-pass, canonical CODEX-CALL-PROTOCOL erken kopya (Task 3), simplify.md stub en son (Task 14), /simplify sweep manuel hit-by-hit (Task 13).
- **Mode default: Standard** (spec Q1): pre-scan + final review default; Light opt-in.
- **Idempotency: Fırsatçı** (spec Q2): "Fixed / Noted external / Intentionally deferred" üçlüsü dürüst rapor.
- **Test rewrite scope: Mekanik update + assertion/fixture/setup high-risk + per-item explicit** (spec Q3).
- **New-file rescan: Girmez** + final review 3 sıkı madde (spec Q4).
- **"Yapma" sinyali formatı: `DO_NOT_APPLY: <id>` + reason + unless + `unlisted:` fallback** (spec Q5).
- **Pre-scan scope: Hibrit** — 5 kategori + Other + `CANDIDATE: unlisted:` bağımsız aday (spec Q6).
- **Commit modeli: İki dosya kümesi** (plan F1): docs/ repo audit + ~/.claude/commands/ global manual install + /tmp backup.
- **Rebuild-from-clean rollback** (plan F10): Task 11.5 fail durumunda Task 2'den itibaren tüm replay.
