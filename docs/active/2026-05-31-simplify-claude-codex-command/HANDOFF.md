# Handoff

## Context
- Task: simplify-claude-codex.md komut implementasyonu
- Linked spec: `docs/specs/2026-05-31-simplify-claude-codex-command.md` (spec-approved, codex_review_status: approved)
- Linked plan: `docs/plans/2026-05-31-simplify-claude-codex-command.md` (plan-approved, codex_plan_review_status: approved-by-iteration-limit)
- Branch: main
- Last updated: 2026-05-31

## Current State
- Summary: Plan onaylandı (16 task, 3 Codex turn + 13 targeted fix). İmplementasyon `/execute-plan-claude-codex` ile başlatılır.
- Blocked: hayır

## Resume From
- Start here: `/execute-plan-claude-codex docs/plans/2026-05-31-simplify-claude-codex-command.md`
- Relevant files: spec, plan, plan review log; mevcut 4 komut dosyası (`~/.claude/commands/{spec,write-plan,execute-plan,simplify}-claude-codex.md` — execute-plan'da `/simplify` 7 hit sweep edilecek)
- Next command: `/execute-plan-claude-codex docs/plans/2026-05-31-simplify-claude-codex-command.md`

## Verification
- Passed: spec finalize (3 turn + 13 fix), plan finalize (3 turn + 13 fix), audit commit (b5c9b33)
- Failed: yok
- Not run: implementation (Task 1-15 henüz başlamadı)

## Risks
- R1 drift: CODEX-CALL-PROTOCOL bloğu byte-exact kopya (Task 3 fail-fast + Task 15 final). Marker count guard her awk öncesi.
- R2 sweep: execute-plan'da `/simplify` 7 hit listesi line-table'lı; whitelist boş; non-whitelisted hit FAIL.
- R3 smoke: 3-state (not-run/pass/fail); runtime mevcutsa pass/fail kesin; mevcut değilse not-run.
- R4 commit modeli: docs/ commit + ~/.claude/commands/ manual install + /tmp backup. `git add ~/.claude/commands/...` YOK.
- R5 spec append drift: Task 11.5 full diff matrix + manuel accept/reject; FAIL → rebuild-from-clean (Task 2'den).
- R6 audit commit integrity: SMOKE_STATE variable substitution + pre+post placeholder guard.

## Notes For Claude
- Codex'in özellikle dikkat çektiği bulgular: F1 (repo path mismatch), F7 (spec append drift), F10 (rebuild semantik) — hepsi adreslendi.
- Claude'un sonraki session'da işlemesi gereken şeyler: /execute-plan-claude-codex çağrısı (active task `proposed → active` flip onayı, mode + cadence seçimi, execute_start_ref kaydı).
- Vault'a yazılması gerekebilecek kalıcı kararlar: yok şu an (claude-codex aile mimarisi vault'a `[[cross-project/infrastructure/codex-entegrasyonu]]` altında zaten var; bu komut o mimarinin bir parçası).
- Spec/plan güncellemesi gerektiren noktalar: yok şu an.
- Kullanıcıdan karar bekleyen konular: yok (plan onaylandı, executor başlayabilir).

## Notes For Codex
- Codex'in review ederken özellikle bakması gereken alanlar: drift Check A 4-way + Check B 8 token; spec section diff Task 11.5; /simplify sweep 7 hit; audit commit SMOKE_STATE binding.
- Bilinen riskler: ~/.claude/commands/ outside-repo (commit yok); rebuild-from-clean cascade (Task 11.5 FAIL); smoke runtime mevcut olmayabilir.
- Dokunmaması gereken alanlar: docs/ commit'i (audit log; ek commit yapılırsa orijinal commit hash kayıt için kaybolur — sadece amend gerek).
- Önce okunması gereken dosyalar: plan (`docs/plans/2026-05-31-simplify-claude-codex-command.md`), spec (`docs/specs/2026-05-31-simplify-claude-codex-command.md`), Codex review log'lar.
