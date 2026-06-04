# Handoff

## Context
- Task: codex-review-scope-contract
- Linked spec: `docs/specs/2026-06-04-codex-review-scope-contract.md` (spec-approved / approved)
- Linked plan: `docs/plans/2026-06-04-codex-review-scope-contract.md` (plan-draft / pending — Codex turn-5 approve, finalize bekliyor)
- Branch: main
- Last updated: 2026-06-04 (oturum kapanışı; spec+plan üretildi, execute edilmedi)

## Current State
- Summary: `/spec-claude-codex` → spec-approved/approved (Codex 5 tur, F1-F6 çözüldü). `/write-plan-claude-codex`
  → plan Codex plan-review turn 5'te **approve** (P1-P8 çözüldü). Plan **finalize edildi**
  (`plan-approved` + `approved`, kullanıcı onayı 2026-06-04). **Commit edildi** (docs-only: spec + plan +
  2 codex log + active task + CURRENT.md; **push YOK** — git log). Komut dosyaları (deliverable) HENÜZ
  DEĞİŞMEDİ — execution başlamadı.
- Blocked: no

## Resume From
- **Start here (SIRA, kritik):**
  1. **Execute:** `/execute-plan-claude-codex docs/plans/2026-06-04-codex-review-scope-contract.md`
     (Subagent-Driven önerilen / Inline). TASK.md status → `active` (execute başında). Spec + plan zaten
     finalize + commit; **Codex'i plan için tekrar ÇALIŞTIRMA** (converged).
  2. (Execution sonrası) `/review-claude-codex` + `/security-review-claude-codex` → closure.
- **Relevant files:**
  - Plan = tek doğruluk kaynağı: 8 task, RED-first, tam kod (block text + drift-check Check E awk +
    AUTO-FIX edit + 8.6 rewrite + per-command binding tablosu).
  - `docs/tools/claude-codex-drift-check.sh` (Check A/B/C/D mevcut; Check E EKLENECEK — plan Task 2/4/6).
  - `docs/tools/codex-scan-substrate-harness.sh` (S-1 davranış testi; Task 7/8'de re-run).
- **Next command:** (finalize+commit sonrası) `/execute-plan-claude-codex <plan>`.

## Verification
- Passed:
  - Spec Codex review: 5 tur, turn 5 = **approve** (`docs/reviews/codex/2026-06-04-codex-review-scope-contract.md`).
    F1 (wiring-proof), F2 (security-review requirement-source independence), F3 (external-overlay realpath/
    git-less-export), F4 (dirty-active hard-DUR), F6 (last_checkpoint POST_CP_HEAD single SHA) — hepsi closed.
  - Plan Codex review: 5 tur, turn 5 = **approve** (`...-codex-review-scope-contract-plan.md`). P1-P8 closed
    (P8 = prompt-body asks hard-gate, son wiring location). Konverjans: 5→2→2→1→0 bulgu.
  - Spec final consistency sweep: clean (section/cross-ref/status-pair). Plan final sweep: clean; live
    drift-check baseline PASS (plan canlı state değiştirmedi).
- Failed: none.
- Not run: execution (komut dosyaları henüz düzenlenmedi); /review + /security-review (execution sonrası);
  drift-check Check E (henüz yok — execution'da eklenecek).

## Risks
- **Deliverable repo-DIŞı:** `~/.claude/commands/*.md` repo'da değil; bir repo diff bunları GÖSTERMEZ —
  diskten doğrudan incele. Edit ÖNCESİ backup ZORUNLU (plan Task 1: `~/.claude/command-backups/`).
  Komut değişikliği aktif olması için Claude Code RESTART gerekir.
- **/tmp throwaway:** Bu oturumun `/tmp/css.sh` (substrate extract) + `/tmp/codex_*.sh` runner'ları
  sonraki oturumda YOK. Codex çağrısı tekrar gerekirse (execution checkpoint review) substrate'ı yeniden
  kur: `awk '/# CODEX-SCAN-SUBSTRATE:BEGIN/,/# CODEX-SCAN-SUBSTRATE:END/' ~/.claude/commands/spec-claude-codex.md > /tmp/css.sh`
  → source → `run_codex_scan "<kind>" <CALL>` (REQUIRED_CURRENT_FILES + RESOLVED_BASE set; COMPANION+PROJECT_ROOT+SCAN_WT_DIRS trap). Bu oturumda böyle yapıldı, çalıştı.
- **Check E arms-race riski:** plan-review'da P1→P4→P6→P7→P8 hep "static check too weak" idi — token-presence
  procedure'ü kanıtlayamaz. Çözüm marker-anchored hard-gate + procedure-correctness'i execution review'a
  bırakmak oldu. Execution'da Check E yazarken bu tavanı koru — sonsuz "daha sıkı" kovalama YAPMA.
- Commit boundary: repo commit'leri docs/tools + docs (audit). `plan-claude-codex.md` dokunma (deprecated).

## Notes For Claude
- **next:** finalize plan (status etiketi onayı: `approved` öneriliyor) → commit (push-gated) → /execute-plan-claude-codex.
- **Codex'in dikkat çektiği (çözüldü, ama execution'da koru):** F1/P1-P8 hepsi "binding≠procedure / static check too weak". Check E iki katmanı (byte-lock + marker-anchored) execution'da AYNEN uygulanmalı; advisory residual = sadece procedure-correctness.
- **Vault'a yazılabilecek kalıcı kararlar (closure'da promote):** A1 mimari kararı + "marker-anchored Check E binding≠procedure'ü plan-seviyesinde de çözer" dersi (predecessor auto-fix-review-policy dersinin devamı).
- **Kullanıcıdan karar bekleyen:** plan finalize status etiketi (`approved` vs `approved-by-iteration-limit`) — Claude `approved` öneriyor; finalize + commit açık onay bekliyor.
- **execute mode:** kullanıcı Subagent vs Inline seçecek (plan Adım 19 / execute-plan Adım 4).

## Notes For Codex
- Review ederken: Check E'nin section-anchored hard-gate'leri gerçekten call-path'i kanıtlıyor mu (binding region + prompt-body + co-location); 7-way byte-identical bozulmamış mı; Check A/C/D regresyon yok mu.
- Bilinen riskler: procedure-correctness statik kanıtlanamaz (kabul edilen tavan — bunu tekrar "too weak" diye flag etme); deliverable repo-dışı.
- Dokunmaması gereken: CODEX-CALL-PROTOCOL (7-way) + CODEX-SCAN-SUBSTRATE (4-way) mevcut blokları; `plan-claude-codex.md`.
- Önce okunması gereken: plan dosyası (8 task) + spec §3-§7 + `docs/tools/claude-codex-drift-check.sh` (mevcut Check A/B/C/D pattern'i, Check E onun aynası).
