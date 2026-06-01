# Handoff

## Context
- Task: review-claude-codex-command
- Linked spec: docs/specs/2026-06-01-review-claude-codex-command.md
- Linked plan: docs/plans/2026-06-01-review-claude-codex-command.md
- Branch: main
- Last updated: 2026-06-01 (paused after batch 1 / Task 3; resume at Task 4)

## Current State
- Summary: Execution **active**, batch 1 (Task 1-3) tamam, cross-session resume için duruldu (2026-06-01). Komut dosyası `~/.claude/commands/review-claude-codex.md` diskte Task 3 sonuna kadar mevcut (138 satır, downstream notuyla bitiyor).
- Blocked: hayır

## Resume From
- Start here: `/execute-plan-claude-codex docs/plans/2026-06-01-review-claude-codex-command.md` → Adım 3 **active dalı** (status=active) → mode/cadence/execute_start_ref TASK.md Current Status'tan okunur (Adım 4'ü atla) → doğrudan Adım 7, **Task 4'ten devam**.
- **Resume noktası: Task 4** (spec Adım 1 + Adım 2 bölümlerini komut dosyasına append). Dosya şu an downstream notuyla bitiyor; Adım 1 oraya eklenir.
- execute state: inline + standard; execute_start_ref=`21e3c86` (TASK.md Current Status'ta)
- Relevant files: plan (15 task, source-of-truth sıra), spec (byte-near append kaynağı), `~/.claude/commands/spec-claude-codex.md` (canonical CODEX-CALL-PROTOCOL); backup'lar `/tmp/*.md.bak` (5 dosya)

## Verification
- Passed: spec review (4 tur) + plan review (2 tur) + pre-exec review (clean); EXECUTE batch 1: Task 1-3 + checkpoint 1 (canonical byte-diff=0, marker count 2, STEP_A-unused notu marker dışında, frontmatter quoted; 1 medium "flow step 5 ledger drift" → fixed)
- Failed: —
- Not run: Task 4-15 (Adım 1-9 gövdeleri, Sözleşme+Drift, spec-section diff gate, 5-way propagation, /review sweep, stub, final Check A/B + smoke + audit commit) + checkpoint'ler (Task 6/9/12/15 sonrası) + final execution review (Adım 11)
- last_checkpoint_ref: yok — batch 1 repo commit üretmedi (komut dosyası repo-DIŞI); checkpoint/final base = execute_start_ref (`21e3c86`)

## Risks
- 5-way byte-drift: canonical blok byte-identical kalmalı; `<STEP_A> unused` notu marker DIŞINDA (yoksa Check A kırılır)
- `/review` sweep false hits: regex artık command-token-aware (`/review([^a-zA-Z0-9_/-]|$)`) — `docs/reviews/` path'leri eşleşmez; yine de hit-by-hit classify (blind sed YASAK)
- Precedent'siz bölümler (worktree teardown timing, disposition ledger, reviewer-status matris, no-review branch, chain-advance) — implementer "basitleştirip" zayıflatabilir; explicit grep verification var
- Repo-dışı deliverable: `~/.claude/commands/*.md` repo commit'i değil; /tmp backup + restart-to-activate

## Notes For Claude
- Codex bulguları (plan fazı): T1-1/T1-2/T1-3/T2-1 hepsi çözüldü + truth-table
- **RESUME — kalan task sırası (checkpoint'ler her 3 task'ta, Standard):**
  - Task 4: spec Adım 1 (scope/ref) + Adım 2 (dirty-tree) append
  - Task 5: spec Adım 3 (bağlam + REQUIREMENT_SNAPSHOT + log + pinli worktree) append
  - Task 6: spec Adım 4 (4a subagent + 4b Codex + reviewer-status matris) append **→ checkpoint 2**
  - Task 7: spec Adım 5 (sentez + disposition ledger) + Adım 6 (push-back) append
  - Task 8: spec Adım 7 (rapor template + ledger) + Adım 8 (active layer) append
  - Task 9: spec Adım 9 (no-review branch + commit + chain-advance + teardown EN SON + Şablon A/B/C) append **→ checkpoint 3**
  - Task 10: Sözleşme Notları + Drift Sözleşmesi 5-way append
  - Task 11: spec-section diff verification matrix **HARD GATE** (FAIL → rebuild-from-clean Task 2'den)
  - Task 12: 5-way propagation (spec/write-plan/execute/simplify; "dört"→"beş", Check A +1 diff, Check B "beş dosya"; **marker bloğu İÇİNE DOKUNMA**) **→ checkpoint 4**
  - Task 13: `/review` → `/review-claude-codex` sweep (robust regex `/review([^a-zA-Z0-9_/-]|$)`, hit-by-hit, blind sed YASAK)
  - Task 14: review.md → deprecated stub (EN SON; description **quoted**)
  - Task 15: final Check A 5-way (4 diff=0) + Check B (8 token × 5 dosya) + smoke (YAML-parse) + audit commit (docs-only) **→ final review Adım 11**
- Her append task sonu: plan header'daki drift-prevention diff pattern (spec vs cmd section). Task 11 konsolide hard gate.
- Vault promotion: closure'da ZORUNLU (aile 5-way; decision doc genişlet) — atlanmaz
- Kullanıcıdan karar bekleyen: yok (mode=inline+standard seçildi; resume otomatik active dalı)

## Notes For Codex
- Codex'in review ederken özellikle bakması gereken alanlar: execute sırasında yeni komut dosyasını DOĞRUDAN oku (repo-dışı, git-diff değil)
- Bilinen riskler: yukarıdaki Risks
- Dokunmaması gereken alanlar: companion (vendored), canonical CODEX-CALL-PROTOCOL marker bloğunun içi
- Önce okunması gereken dosyalar: plan + spec + canonical spec-claude-codex.md
