---
title: /write-plan-claude-codex komutu
status: proposed     # proposed | active | blocked | waiting-review | done | archived | cancelled
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

Spec + plan onaylandı ve commit'lendi (design commit `f9c53d2`). Implementation **henüz
başlanmadı** — Task 0→5 bekliyor. Push yapılmadı.

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
