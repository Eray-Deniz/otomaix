---
title: spec-claude-codex Komutu (plan-claude-codex rename + akış refactor)
status: proposed
started: 2026-05-20
last-touched: 2026-05-20
blocked-by: null
---

# Goal

`/plan-claude-codex` komutunu `/spec-claude-codex` olarak yeniden adlandır;
approved spec'teki akış delta'larını (Adım 0 active context, full_design_iteration
sayacı, consistency sweep, frontmatter lifecycle draft→spec-approved, atomik reopen,
koşullu adversarial scope) yeni canonical komuta işle; eskiyi deprecated stub yap;
3 canlı komut referansını güncelle; vault'u rollout gate olarak ayrı onaylı adımda
kapat. **Başarı:** `rg plan-claude-codex` yalnız kasıtlı kalanları (stub + donmuş
2026-05-19 docs + vault `log.md`) gösterir.

# References

- Spec: `docs/specs/2026-05-20-spec-claude-codex-command.md`
- Plan: `docs/plans/2026-05-20-spec-claude-codex-command.md`
- Codex review log: `docs/reviews/codex/2026-05-20-spec-claude-codex-command.md`
- Review: _(yok)_

# Current Status

Plan onaylandı ve commit edildi (`b2943df`), henüz başlanmadı.
`/execute-plan` başında active'e geçilecek.

# Open Problems

_(yok)_

# Decisions Log

Tam tasarım gerekçesi spec/plan'da. Execution'ı bağlayan kilit kararlar:
- 2026-05-20: Rename + deprecated stub (silme YOK) — referans bütünlüğü kalkanı
- 2026-05-20: Anti-drift **dar** — yalnız Adım 2 task çağrısı verbatim; Adım 6
  adversarial scope/çağrı kasıtlı değişir (Bulgu 2 miras bug fix)
- 2026-05-20: Vault ayrı **rollout gate** — vault güncellenip doğrulanmadan rename
  "done" sayılmaz
- 2026-05-20: Codex bu planı **tek başına uygulayamaz** (global command dosyaları
  sandbox writable root dışı) — patch önerir, Claude/kullanıcı uygular
