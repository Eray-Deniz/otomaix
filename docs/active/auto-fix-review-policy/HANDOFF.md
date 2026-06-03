# Handoff

## Context
- Task: Auto-Fix Review Policy — claude-codex aile geneli
- Linked spec: docs/specs/2026-06-03-auto-fix-review-policy.md
- Linked plan: docs/plans/2026-06-03-auto-fix-review-policy.md
- Branch: main
- Last updated: 2026-06-03

## Current State
- Summary: Plan onaylandı (approved-by-iteration-limit, Codex 4 tur). Henüz execution başlamadı.
- Blocked: hayır

## Resume From
- Start here: `/execute-plan-claude-codex docs/plans/2026-06-03-auto-fix-review-policy.md`
- Relevant files: ~/.claude/commands/{spec,write-plan,execute-plan,simplify,review,security-review}-claude-codex.md (repo-DIŞI); docs/tools/claude-codex-drift-check.sh (repo-İÇİ, Check D burada)
- Next command: /execute-plan-claude-codex

## Verification
- Passed: plan-writing aşaması — Codex 4 tur review; negatif check 8-case ampirik doğrulandı; F7 bypass kapalı; gerçek kanonik prose false-positive yok
- Failed: —
- Not run: Check D'nin gerçek implementasyonu (execution'da); 6 komut smoke parse; prose senaryo trace

## Risks
- Byte-identical 4-way drift: blok awk-extract byte-copy ile yayılmalı (hand-retype YASAK); Task 4 Step 4 cmp ile doğrula
- Deliverable repo-DIŞI → repo commit yalnız drift-check.sh Check D'yi kapsar; .bak yedek her edit öncesi zorunlu
- Reviewer prose yazım kuralı (F9): hard-block satırı self-contained critical/high, medium ayrı advisory cümlesinde

## Notes For Claude
- Codex'in özellikle dikkat çektiği bulgular: F1 worktree-safe $REPO; F2/F5/F7 reviewer negatif check (enumeration-scoped tripwire); F3 gerçek CLAUDE_CODEX_COMMAND_DIR fixture regresyonu; F4/F8 active-layer onay kapısı; F6 clean-tree assertion; F9 wrapped-prose residual (dokümante)
- Claude'un sonraki session'da işlemesi gereken şeyler: execution Task 1-8; reviewer prose yazarken F9 yazım kuralına uy
- Vault'a yazılması gerekebilecek kalıcı kararlar: Auto-Fix Policy davranışı (P1'de promote — /commit veya closure'da)
- Spec/plan güncellemesi gerektiren noktalar: —
- Kullanıcıdan karar bekleyen konular: — (commit + active task onaylandı)

## Notes For Codex
- Codex'in review ederken özellikle bakması gereken alanlar: Check D byte-identical 4-way; reviewer negatif check'in execution'daki gerçek reviewer-edit'e karşı davranışı (F9 residual'ı manuel kapatılıyor mu)
- Bilinen riskler: prose-regex non-convergence (F5/F7/F9) — tripwire kabul edildi, daha fazla regex epicycle ÖNERME
- Dokunmaması gereken alanlar: CODEX-CALL-PROTOCOL + CODEX-SCAN-SUBSTRATE blokları (Check A/B/C tetiklenmez); finish-branch (kapsam dışı)
- Önce okunması gereken dosyalar: docs/plans/2026-06-03-auto-fix-review-policy.md; docs/tools/claude-codex-drift-check.sh
