---
title: review-claude-codex Komutu — /review'ın claude-codex aile eşi
status: proposed
started: 2026-06-01
last-touched: 2026-06-01
blocked-by: null
---

# Goal

`~/.claude/commands/review-claude-codex.md` yeni custom slash command'i onaylı plana göre uygula: mevcut tek-aktörlü `/review`'ı iki bağımsız hakem (fresh Claude subagent + Codex adversarial-review, pinli worktree @ HEAD_SHA) + ana Claude sentez modeline taşı; aileyi 4-way → 5-way drift contract'a genişlet; `review.md`'yi deprecated stub'a çevir. **Başarı:** Check A 5-way (4 diff=0) + Check B (8 token × 5 dosya) + spec-section diff + pre-commit smoke geçiyor; `/review` sweep canlı referans bırakmıyor.

# References

- Spec: `docs/specs/2026-06-01-review-claude-codex-command.md` (spec-approved, Codex 4 tur)
- Plan: `docs/plans/2026-06-01-review-claude-codex-command.md` (plan-approved, Codex 2 tur)
- Plan review log: `docs/reviews/codex/2026-06-01-review-claude-codex-command-plan.md`
- Review: _(yok — komut bu)_

# Current Status

_Plan onaylandı, henüz başlanmadı. Sonraki: `/execute-plan-claude-codex docs/plans/2026-06-01-review-claude-codex-command.md` (Subagent-Driven önerilir, 15 task)._

# Open Problems

_(yok)_

# Decisions Log

_Kanonik kararlar spec Decisions Log'unda (23 satır) — burada tekrarlanmaz. Yük taşıyan iki çapa:_
- Topoloji: iki bağımsız hakem + sentez (Codex meta-review / tek-hakem reddedildi). → spec Decision 1.
- Drift 5-way: CODEX-CALL-PROTOCOL byte-identical 5 dosyada; review yalnız STEP_B kullanır, blok bütün kopyalanır. → spec Decision 16.
_(execute sırasında çıkan yeni kararlar buraya; promote edilenler `→ Vault: [[decisions/...]]`)_
