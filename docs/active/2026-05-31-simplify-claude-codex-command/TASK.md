---
title: simplify-claude-codex.md komut implementasyonu
status: waiting-review
started: 2026-05-31
last-touched: 2026-05-31
blocked-by: null
source_plan: docs/plans/2026-05-31-simplify-claude-codex-command.md
---

# Goal

Eski single-actor `/simplify` komutunu Claude-Codex ailesine entegre eden yeni `~/.claude/commands/simplify-claude-codex.md` komutunu implement et — Codex pre-scan + final adversarial review + commit-gated invariant. 5 dosya değişikliği (yeni komut + 3 ayna drift-check 4-way + 1 stub). Başarı kriteri: drift Check A 4-way diff=0 + Check B 8 token presence + structural integrity + smoke pass-or-not-run.

# References

- Spec: `docs/specs/2026-05-31-simplify-claude-codex-command.md` (status: spec-approved, codex_review_status: approved, 3 turn + 13 targeted fix)
- Plan: `docs/plans/2026-05-31-simplify-claude-codex-command.md` (status: plan-approved, codex_plan_review_status: approved-by-iteration-limit, 3 turn + 13 targeted fix)
- Review: `docs/reviews/codex/2026-05-31-simplify-claude-codex-command.md` (spec) + `docs/reviews/codex/2026-05-31-simplify-claude-codex-command-plan.md` (plan)

# Current Status

Execution tamamlandı (16 task, inline + standard). Final Codex review **approved** (0 critical/high). `/review` (merge-ready) + `/security-review` (0 kritik) yapıldı; çıkan **6 maddelik bulgu kümesi (Yüksek #1-2, Orta #1-2, R-kuralF, Minor #1) tamamı düzeltildi + doğrulandı** (kullanıcı "tüm bulguları düzelt"). Ardından kullanıcı ayrı bir **Codex re-review** yaptırdı → 3 yeni bulgu (commit-scope FIXED_FILES, SCOPE_SLUG→Adım 1, B2 FAIL); üçü de doğrulanıp düzeltildi (A: FIXED_FILES takibi seçildi). Status `waiting-review` — commit + closure bekliyor. Komut dosyaları `~/.claude/commands/` (repo dışı); slash menüsünde aktif olması için Claude Code restart gerekir.

# Open Problems

_(yok — execution tamamlandı; spec-refine adayları HANDOFF Risks'te.)_

**Çözülen (Drift 1, pre-exec):** spec/plan/review-log zaten `b5c9b33`'te commit'liydi; audit commit yalnız bu session'ın değişikliklerini (active-layer + execute-log) kapsadı — plan Step 9 `git add docs/specs|plans` no-op'tu, commit içeriği buna göre uyarlandı.

# Decisions Log

- **Y1/A — execute-plan-style küçük kuzen** (spec brainstorm): atomic-one-pass, canonical CODEX-CALL-PROTOCOL erken kopya (Task 3), simplify.md stub en son (Task 14), /simplify sweep manuel hit-by-hit (Task 13).
- **Mode default: Standard** (spec Q1): pre-scan + final review default; Light opt-in.
- **Idempotency: Fırsatçı** (spec Q2): "Fixed / Noted external / Intentionally deferred" üçlüsü dürüst rapor.
- **Test rewrite scope: Mekanik update + assertion/fixture/setup high-risk + per-item explicit** (spec Q3).
- **New-file rescan: Girmez** + final review 3 sıkı madde (spec Q4).
- **"Yapma" sinyali formatı: `DO_NOT_APPLY: <id>` + reason + unless + `unlisted:` fallback** (spec Q5).
- **Pre-scan scope: Hibrit** — 5 kategori + Other + `CANDIDATE: unlisted:` bağımsız aday (spec Q6).
- **Commit modeli: İki dosya kümesi** (plan F1): docs/ repo audit + ~/.claude/commands/ global manual install + /tmp backup.
- **Rebuild-from-clean rollback** (plan F10): Task 11.5 fail durumunda Task 2'den itibaren tüm replay.
- **Post-review hardening pass** (2026-05-31, /review + /security-review sonrası): 6 bulgu sistemik (canonical blok 4-way + frozen spec mirror). Manuel inline edit yerine mekanik propagation (canonical 1 kez düzenlenip script'le 4 dosyaya kopya) + body-mirror için spec doc & command identical edit + her adımda Check A/B + body-diff yeniden doğrulama. **Frozen spec artık refine edildi** (R-kuralF relabel + Orta#1 slugify spec doc'a da işlendi → byte-freeze kalktı; yeni baseline). Canonical CODEX-CALL-PROTOCOL bloğu 45→66 satır (md5 `2503b639`).

# Notes For Claude

Execution state (`/execute-plan-claude-codex` Adım 4 — resume bu alandan okur):

- execute_mode: inline
- checkpoint_cadence: standard
- execute_started: 2026-05-31 17:51
- execute_start_ref: 500541bc7f2f289116aa66087c2c55ff231ba875
