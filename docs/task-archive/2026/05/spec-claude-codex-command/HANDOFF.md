# Handoff

## Context
- Task: spec-claude-codex Komutu (plan-claude-codex rename + akış refactor)
- Linked spec: docs/specs/2026-05-20-spec-claude-codex-command.md
- Linked plan: docs/plans/2026-05-20-spec-claude-codex-command.md
- Branch: main
- Last updated: 2026-05-20 (closure)

## Current State
- Summary: **TAMAMLANDI (2026-05-20).** spec-claude-codex komutu inşa edildi
  (cp + transform, 401 satır), eski plan-claude-codex stub, canlı + vault
  ref'ler güncel, rollout gate kapandı. Fresh review: 0 critical, 0 açık.
- Blocked: Hayır.

## Resume From
- Start here: Loose end yok — task tamamlandı, arşivleniyor.
- Relevant files:
  - ~/.claude/commands/spec-claude-codex.md (canlı komut)
  - docs/reviews/2026-05-20-spec-claude-codex-command.md (review)
- Next command: (opsiyonel) yeni komutu dummy fikirle canlı dene; aksi halde yok.

## Verification
- Passed: Faz A-F implementation; rg anti-drift + yapı (14 adım, self-ref 0,
  HEAD~1 0, task mekaniği verbatim); fresh review 0 critical/0 açık; DoD ✓
- Failed: _(yok)_
- Not run: Yeni komutun canlı end-to-end denemesi (dummy fikir) — opsiyonel

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
