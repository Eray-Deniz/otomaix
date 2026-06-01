# Handoff

## Context
- Task: review-claude-codex-command
- Linked spec: docs/specs/2026-06-01-review-claude-codex-command.md
- Linked plan: docs/plans/2026-06-01-review-claude-codex-command.md
- Branch: main
- Last updated: 2026-06-01

## Current State
- Summary: Spec + plan onaylandı (Codex 4 + 2 tur, 0 unresolved critical/high). Execution başlamadı.
- Blocked: hayır

## Resume From
- Start here: `/execute-plan-claude-codex docs/plans/2026-06-01-review-claude-codex-command.md`
- Relevant files: plan (15 task), spec (source-of-truth), `~/.claude/commands/spec-claude-codex.md` (canonical CODEX-CALL-PROTOCOL)
- Next command: `/execute-plan-claude-codex` → Subagent-Driven mod (15 task, izole)

## Verification
- Passed: spec Codex review (4 tur) + plan Codex review (2 tur), self-sweep + regex truth-table
- Failed: —
- Not run: command build verification (Check A/B 5-way, spec-section diff, smoke) — execute aşamasında

## Risks
- 5-way byte-drift: canonical blok byte-identical kalmalı; `<STEP_A> unused` notu marker DIŞINDA (yoksa Check A kırılır)
- `/review` sweep false hits: regex artık command-token-aware (`/review([^a-zA-Z0-9_/-]|$)`) — `docs/reviews/` path'leri eşleşmez; yine de hit-by-hit classify (blind sed YASAK)
- Precedent'siz bölümler (worktree teardown timing, disposition ledger, reviewer-status matris, no-review branch, chain-advance) — implementer "basitleştirip" zayıflatabilir; explicit grep verification var
- Repo-dışı deliverable: `~/.claude/commands/*.md` repo commit'i değil; /tmp backup + restart-to-activate

## Notes For Claude
- Codex'in özellikle dikkat çektiği bulgular: T1-1 sweep filtresi (çözüldü), T1-2 self-contained audit (çözüldü), T1-3 smoke gate (çözüldü), T2-1 regex overmatch (çözüldü + truth-table)
- Claude'un sonraki session'da işlemesi gereken şeyler: plan Task sırasını izle; review.md stub EN SON
- Vault'a yazılması gerekebilecek kalıcı kararlar: closure'da aile/workflow değişikliği vault'a girer (decision doc genişlet + 5-way pattern) — ZORUNLU, atlanmaz
- Spec/plan güncellemesi gerektiren noktalar: —
- Kullanıcıdan karar bekleyen konular: execute modu (Subagent vs Inline)

## Notes For Codex
- Codex'in review ederken özellikle bakması gereken alanlar: execute sırasında yeni komut dosyasını DOĞRUDAN oku (repo-dışı, git-diff değil)
- Bilinen riskler: yukarıdaki Risks
- Dokunmaması gereken alanlar: companion (vendored), canonical CODEX-CALL-PROTOCOL marker bloğunun içi
- Önce okunması gereken dosyalar: plan + spec + canonical spec-claude-codex.md
