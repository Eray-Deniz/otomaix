# Handoff

## Context
- Task: claude-codex ailesi — Codex --cwd untracked-secret exposure hardening
- Status: **proposed** (başlanmadı)
- Keşif: finish-branch-claude-codex security review (2026-06-02), bulgu S-1

## Current State
- Summary: Henüz başlanmadı. Bulgu + 4 etkilenen komut + 3 fix opsiyonu TASK.md'de. İş başlayınca bu HANDOFF rolling devir için dolar.
- Blocked: hayır (sadece henüz başlanmadı)

## Resume From
- Start here: Karar ver (TASK.md Decisions Log 3 aday: a/b/c) → kapsamlıysa `/spec-claude-codex`.
- İlk okunacak: `docs/security-reviews/2026-06-02-finish-branch-claude-codex.md` (S-1 detayı + referans izolasyon desenleri).

## Notes For Claude
- Bu süreç-içkin bir bulgu (İlke 6): kök neden canonical blok template `--cwd "$PROJECT_ROOT"` + 4 komutun override etmemesi.
- finish-branch/review/security-review ZATEN izole — bu task yalnız spec/write-plan/execute-plan/simplify içindir.
- Drift contract: call-site `--cwd` override marker DIŞINDA tutulmalı (Check A `c7b5976c` bozulmasın).

## Notes For Codex
- Codex active layer'a YAZMAZ. Bu task'ta Codex'e iş verilirse bulgu/öneri stdout → Claude işler.
