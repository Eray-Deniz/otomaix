---
title: review-claude-codex Komutu — /review'ın claude-codex aile eşi
status: waiting-review
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

_Execution **complete** (2026-06-01) → status **waiting-review**. Tüm 15 task uygulandı (batch 1-5). Deliverable repo-DIŞI (`~/.claude/commands/`), Claude Code restart ile aktif._

**Closure chain ilerleme (2026-06-01):**
- `/simplify-claude-codex`: **no-op** (markdown slash-command; kod-kalite modeli uygulanmıyor — aile sözleşmesi). FIXES_APPLIED=0.
- `/review-claude-codex`: **dual review tamam** — 1 high + 1 low, both-agree yok. Objektif drift Check A/B PASS. **high (C1) bu oturum DÜZELTİLDİ**: `BASE_REF="${ARG:-...}"` → `$ARGUMENTS` binding (spec:96 + komut:151 identical edit); `$ARG` tanımsızdı → explicit base sessizce yutuluyordu. low (L1, cannot-verify matris sınırı) da bu oturum düzeltildi (matrise netleştirme notu, spec+komut identical edit). Açık bulgu 0. Rapor: `docs/reviews/2026-06-01-review-claude-codex-command.md`.
- Sırada: `/security-review` → closure (`/finish-branch`).

**Execution State (audit):**
- execute_mode: inline · checkpoint_cadence: standard
- execute_started: 2026-06-01 12:35 UTC · execute_completed: 2026-06-01 14:24 UTC
- execute_start_ref: 21e3c86 · audit_commit: 0a7143c (docs-only, repo-side)
- Checkpoints: cp1-4 hepsi ran, 0 skipped (standard cadence); cp4 [high] (Check B "beş dosyada" tutarsızlığı) FIXED
- Final Codex review: ran → procedural [high] resolved (audit commit yapıldı) + 1 out-of-scope [medium] (/execute-plan → /execute-plan-claude-codex staleness) FIXED; no critical/high
- not: komut dosyaları repo-DIŞI; repo commit yalnız docs audit trail

# Open Problems

_(yok)_

# Decisions Log

_Kanonik kararlar spec Decisions Log'unda (23 satır) — burada tekrarlanmaz. Yük taşıyan iki çapa:_
- Topoloji: iki bağımsız hakem + sentez (Codex meta-review / tek-hakem reddedildi). → spec Decision 1.
- Drift 5-way: CODEX-CALL-PROTOCOL byte-identical 5 dosyada; review yalnız STEP_B kullanır, blok bütün kopyalanır. → spec Decision 16.
_(execute sırasında çıkan yeni kararlar buraya; promote edilenler `→ Vault: [[decisions/...]]`)_
