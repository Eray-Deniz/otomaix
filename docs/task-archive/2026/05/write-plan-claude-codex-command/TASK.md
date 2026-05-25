---
title: /write-plan-claude-codex komutu
status: done             # proposed | active | blocked | waiting-review | done | archived | cancelled
started: 2026-05-25
last-touched: 2026-05-25
blocked-by: null
---

# Goal

`/spec-claude-codex` ile aynı sağlamlık barında, çift-perspektif (Claude + Codex),
adversarial-review'lı, metadata'lı + resume-safe yeni bir implementation-plan komutu
(`/write-plan-claude-codex`) kur; eski `/write-plan`'i deprecated stub'a çevir; `/write-plan`'e
işaret eden canlı yüzeyleri yeni komuta yönlendir. Başarı: yeni komut yerinde, drift-check
geçiyor, canlı yüzeylerde çıplak `/write-plan` kalmıyor, stub yerinde.

# References

- Spec: `docs/specs/2026-05-25-write-plan-claude-codex-command.md` (spec-approved / approved-by-iteration-limit)
- Plan: `docs/plans/2026-05-25-write-plan-claude-codex-command.md` (plan-approved)
- Review: `docs/reviews/codex/2026-05-25-write-plan-claude-codex-command.md` (spec, 5 turn) +
  `...-command-plan.md` (plan, 2 turn)

# Current Status

Implementation **tamamlandı** (Task 0→5, 2026-05-25). Canonical `spec-claude-codex.md`
normalize edildi (CODEX-CALL-PROTOCOL marker'ları), `write-plan-claude-codex.md` yazıldı,
drift Check A **diff=0** + Check B tam, 7 canlı yüzey sweep'lendi (bare /write-plan = 0),
`write-plan.md` stub'a çevrildi. Codex bağımsız doğrulama: blocking yok.
**KAPANDI (2026-05-25):** otomaix commit+push (`4169537`), vault commit+push (`0bbc9fb`),
global `~/.claude/` edit'leri diskte (repo-dışı, backup `/tmp/spec-claude-codex.md.bak`).
/simplify temiz; /review no-critical (2 important çözüldü: vault accuracy + /spec-claude-codex
eklendi); /security-review atlandı (markdown, kod/secret yok). Yeni komut canlı, drift-check diff=0.

# Open Problems

- **Bootstrap sırası:** Task 4 (stub'a çevirme) yalnız plan-approved sonrası — sağlandı.
  Canonical normalizasyon (Task 0) canlı `spec-claude-codex.md`'yi değiştiriyor → backup+rollback şart.
- **Vault closure:** `claude-code-workflow.md` güncellemesi Claude tarafından, ayrı zorunlu
  closure adımı (Codex vault'a yazamaz); push kullanıcı onayıyla.

# Decisions Log

_(promote edilenler `→ Vault: [[decisions/...]]` formatıyla; closure'da değerlendirilecek)_

- Authoring yaklaşımı **C (hybrid)**: gömülü protokol + canonical-source marker + makine-kontrollü
  drift-check (B/extract-shared elendi: slash command'da include yok).
- Drift enforcement: `CODEX-CALL-PROTOCOL` delimited blok + Check A (directional diff=0 vs canonical) + Check B (token tripwire).
- Hafif/overkill yol **artefakt üretmez** (lightweight/not-run kaldırıldı) → komuttan çıkan her plan review-gated.
- Active-task yaratım sahipliği `/write-plan-claude-codex`'e taşındı (`/spec-claude-codex` değil).
- Unapproved-spec override kalıcı: frontmatter `source_spec_unapproved_override` + audit.
- Referans sweep occurrence-level (live/example/dated/stub); tarihli kayıtlar + exclude-list örnekleri korunur.
