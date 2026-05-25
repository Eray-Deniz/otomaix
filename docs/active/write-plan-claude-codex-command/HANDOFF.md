# Handoff

## Context
- Task: /write-plan-claude-codex komutu
- Linked spec: `docs/specs/2026-05-25-write-plan-claude-codex-command.md`
- Linked plan: `docs/plans/2026-05-25-write-plan-claude-codex-command.md`
- Branch: main (design commit `f9c53d2`, push edilmedi)
- Last updated: 2026-05-25

## Current State
- Summary: Spec (5 turn Codex review, approved-by-iteration-limit) + plan (2 turn, plan-approved)
  yazıldı ve commit'lendi. Implementation başlanmadı.
- Blocked: hayır

## Resume From
- Start here: Plan Task 0 (canonical `spec-claude-codex.md`'ye CODEX-CALL-PROTOCOL marker'ları — ÖNCE backup).
- Relevant files: `~/.claude/commands/spec-claude-codex.md` (canonical, normalize edilecek),
  `~/.claude/commands/write-plan.md` (stub'a çevrilecek — SADECE plan-approved sonrası, sağlandı),
  7 sweep yüzeyi (plan Bölüm/Task 3), vault `cross-project/infrastructure/claude-code-workflow.md`.
- Next command: Plan Task 0'ı uygula (backup → marker ekle → semantic verify → rollback gerekirse).

## Verification
- Passed: spec drift-check tasarımı (Check A/B), plan sweep regex (temiz form 21 canlı ref buldu — doğru çalışıyor).
- Failed: _(yok)_
- Not run: gerçek implementation doğrulamaları (Task 0-5 henüz çalışmadı); drift-check Check A
  canonical marker'lar eklenince çalıştırılacak.

## Risks
- Task 0 canlı `/spec-claude-codex`'i bozabilir → backup + post-edit semantic check + rollback (plan'da var).
- Sweep'te aynı satırda hem yeni hem çıplak `/write-plan` olabilir → PCRE negative-lookahead kullan (line-filter YOK).
- Yeni komut restart sonrası yüklenir (slash command'lar başlangıçta taranır).

## Notes For Claude
- Codex'in özellikle dikkat çektiği bulgular: protokol "synchronized-wrongness" (directional canonical ile çözüldü);
  Task 0 rollback; sweep occurrence-level.
- Sonraki session'da işlenecek: Task 0→5 sırasıyla; her task'ın doğrulama komutunu çalıştır (doc işi → test = grep/diff/awk).
- Vault'a yazılabilecek kalıcı kararlar: TASK Decisions Log'daki maddeler — closure'da `/commit` P1 ile değerlendir.
- Kullanıcıdan karar bekleyen: push zamanlaması; implementation'a ne zaman geçileceği.

## Notes For Codex
- Review ederken bakılacak alanlar: drift-check'in gerçekten enforce edilip edilmediği; sweep'in occurrence-level tamlığı; stub sırası.
- Bilinen riskler: canonical normalizasyonun /spec-claude-codex davranışını koruması.
- Dokunmaması gereken: tarihli docs/specs|plans|reviews, vault decisions/2026-05-19, exclude-list örnekleri.
- Önce okunması gereken: spec Bölüm 2 (drift) + Bölüm 8 (sweep) + plan Task 0/3.
