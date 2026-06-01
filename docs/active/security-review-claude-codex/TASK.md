---
title: security-review-claude-codex komutu
status: proposed
started: 2026-06-01
last-touched: 2026-06-01
blocked-by: null
---

# Goal

Eski tek-aktörlü `/security-review`'ı claude-codex ailesine entegre eden `~/.claude/commands/security-review-claude-codex.md` komutunu oluştur (iki bağımsız güvenlik hakemi + ana Claude sentezi); aile drift contract'ını 5-way → 6-way büyüt; chain referanslarını süpür; eski komutu deprecate et. Başarı kriteri: 6-way drift Check A/B geçer, chain sweep temiz, frontmatter parse, restart sonrası komut yüklenir.

# References

- Spec: `docs/specs/2026-06-01-security-review-claude-codex-command.md` (spec-approved, 4 Codex turu)
- Plan: `docs/plans/2026-06-01-security-review-claude-codex-command.md` (plan-approved, 5 Codex turu)
- Review: _(yok — execution sonrası /review-claude-codex + /security-review-claude-codex)_

# Current Status

Plan onaylandı, henüz başlanmadı. Sonraki adım: `/execute-plan-claude-codex docs/plans/2026-06-01-security-review-claude-codex-command.md`.

# Open Problems

_(yok — spec + plan review'larında tüm critical/high çözüldü)_

# Decisions Log

- Topoloji: iki bağımsız güvenlik hakemi + ana Claude sentez (review-claude-codex aynası, üretici+hakem değil) → Vault promote adayı (closure P1)
- Mode-aware Codex binding: diff→STEP_B (`adversarial-review --base`); full/path→STEP_A (`task --fresh`)
- İzolasyon: diff→pinli worktree, full/path→git'siz export (committed secret `git show` sızıntısına karşı); fiziksel secret-exclusion (export rm) + post-export symlink sweep
- İki-katmanlı chain gate (security-risk + dual-review ayrı override, non-directive ton); coverage_gap→Şablon D metadata-only
- Drift contract 5-way → 6-way (closure'da vault decision doc `2026-05-26-...hardening` 6-komuta genişlet)
