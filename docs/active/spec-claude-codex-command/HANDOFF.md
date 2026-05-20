# Handoff

## Context
- Task: spec-claude-codex Komutu (plan-claude-codex rename + akış refactor)
- Linked spec: docs/specs/2026-05-20-spec-claude-codex-command.md
- Linked plan: docs/plans/2026-05-20-spec-claude-codex-command.md
- Branch: main
- Last updated: 2026-05-20 17:56

## Current State
- Summary: Spec (2f00b6b/9c86093) + plan (b2943df) onaylandı ve commit edildi.
  Implementation başlamadı (status TASK.md frontmatter'da).
- Blocked: Hayır.

## Resume From
- Start here: Plan Faz A, Task 1 (`cp plan-claude-codex.md → spec-claude-codex.md`)
- Relevant files:
  - docs/plans/2026-05-20-spec-claude-codex-command.md
  - ~/.claude/commands/plan-claude-codex.md (kaynak mekanik)
- Next command: /execute-plan docs/plans/2026-05-20-spec-claude-codex-command.md

## Verification
- Passed: Spec Codex adversarial review (1 full design iteration) + 2 tur insan
  review; plan 2 tur insan review (toplam 5 bulgu işlendi)
- Failed: _(yok)_
- Not run: Implementation hiç çalıştırılmadı

## Risks
- Faz A çok edit'li (cp + ~9 task) — anti-drift sadece Adım 2 task bloğuna; her
  edit sonrası `rg` token doğrulaması şart, yoksa bash mekaniği drift'e açık

## Notes For Claude
- Fresh review (2026-05-20): yeni komut dosyası ↔ spec — 2 Important fix (yanlış
  adım çapraz-referansları, biri kaynaktan miras), 0 açık. Rapor:
  docs/reviews/2026-05-20-spec-claude-codex-command.md
- Codex'in özellikle dikkat çektiği bulgular: rollout gate, HEAD~1 miras bug,
  atomik reopen — hepsi spec/plan'a işlendi
- Claude'un sonraki session'da işlemesi gereken şeyler: Faz A→F sırayla; **B (stub)
  A'dan SONRA** (içerik kaybı riski)
- Vault'a yazılması gerekebilecek kalıcı kararlar: Faz E (rollout gate) — ayrı onay
  + `last-verified` bump; Codex vault'a yazmaz
- Spec/plan güncellemesi gerektiren noktalar: _(yok)_
- Kullanıcıdan karar bekleyen konular: execution modu (subagent/inline); vault push onayı

## Notes For Codex
- Codex'in review ederken özellikle bakması gereken alanlar: Faz A edit'lerinde
  Adım 2 `task` bloğunun verbatim kaldığı (find pattern, --fresh --wait, --cwd, positional)
- Bilinen riskler: **Codex bu planı tek başına UYGULAYAMAZ** — `~/.claude/commands/`
  sandbox writable root dışı; sadece patch öner
- Dokunmaması gereken alanlar: vault (Faz E Claude/kullanıcı), memory, donmuş
  2026-05-19 docs
- Önce okunması gereken dosyalar: docs/specs/ + docs/plans/ 2026-05-20-spec-claude-codex-command.md
