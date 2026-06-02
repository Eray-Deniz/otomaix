---
title: finish-branch-claude-codex komutu
status: proposed
started: 2026-06-02
last-touched: 2026-06-02
blocked-by: null
---

# Goal

Mevcut tek-aktörlü `/finish-branch`'i claude-codex ailesine entegre eden `~/.claude/commands/finish-branch-claude-codex.md` komutunu oluştur: tek Codex `task --fresh` **advisory closure-readiness audit** (gate DEĞİL); aile drift contract'ını 6-way → 7-way büyüt; eski `/finish-branch`'i deprecated stub'a indirge. Başarı kriteri: 7-way Check A/B geçer, mevcut finish-branch closure matrix bozulmadan korunur, section-scoped fidelity gates PASS, restart sonrası komut yüklenir.

# References

- Spec: `docs/specs/2026-06-02-finish-branch-claude-codex-command.md` (spec-approved, Codex 4 tur)
- Plan: `docs/plans/2026-06-02-finish-branch-claude-codex-command.md` (plan-approved, Codex 4 tur)
- Review: _(yok — execution sonrası)_

# Current Status

**proposed — plan onaylandı (2026-06-02), execute YENİ OTURUMA bırakıldı.** Spec + plan ikisi de Codex adversarial review'dan geçti (her biri 4 tur, approve). Plan: 1/3 full iteration + 3 targeted fix. Execute henüz başlamadı; yeni oturumda `/execute-plan-claude-codex docs/plans/2026-06-02-finish-branch-claude-codex-command.md` + mod seçimi (Inline/Subagent) ile başlanacak.

# Open Problems

_(yok — spec + plan review'larında tüm critical/high çözüldü)_

# Decisions Log

- Topoloji: tek Codex `task --fresh` **advisory** closure-readiness audit (kod/güvenlik review DEĞİL — zincirde yapıldı); fresh Claude subagent YOK (review'ın iki-hakem modeli overkill)
- Advisory ilkesinin TEK istisnası: *"closure-blocker is not a gate, except it upgrades destructive discard confirmation text"* — yalnız D=sil'de `discard despite closure blockers` upgrade
- İki-fazlı blocker: Codex aksiyon-nötr facts emit → Claude seçilen aksiyona göre Adım 8'de reclassify
- Mode-aware: normal (pinli worktree @ HEAD_SHA) / mainline (worktree yok + HEAD guard) / detached; deterministik git mode-detection (belirsiz → DUR, sor)
- Pinned-target tüm outward/destructive ops: push `${HEAD_SHA}:branch`, merge `${HEAD_SHA}`, **D=sil old-value-bound** `git update-ref -d refs/heads/<branch> $HEAD_SHA`; SCAN_ROOT=$WT (normal) / $PROJECT_ROOT (mainline), Codex `--cwd $SCAN_ROOT`
- Evidence range-containment: `report_HEAD==audit_HEAD` AND `report_BASE` ⊑ `audit_BASE` → coverage-uncertain
- Implementation: hibrit (finish-branch closure semantics base + security-review repo-external delivery scaffold); topoloji security-review'dan KOPYALANMAZ
- Drift contract 6-way → 7-way (execute Task 5 sibling bump + closure'da vault decision doc genişlet)
