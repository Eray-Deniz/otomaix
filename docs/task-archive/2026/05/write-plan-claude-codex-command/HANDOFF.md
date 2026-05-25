# Handoff

## Context
- Task: /write-plan-claude-codex komutu
- Linked spec: `docs/specs/2026-05-25-write-plan-claude-codex-command.md`
- Linked plan: `docs/plans/2026-05-25-write-plan-claude-codex-command.md`
- Branch: main (design commit `f9c53d2`, push edilmedi)
- Last updated: 2026-05-25

## Current State
- Summary: Spec + plan onaylandı; **implementation tamamlandı (Task 0→5)**. Komut yazıldı,
  drift-check diff=0, sweep temiz, stub yerinde. Codex bağımsız doğrulama: blocking yok.
- Blocked: hayır

## Resume From
- Start here: otomaix repo commit (3 dosya) + vault commit/push (claude-code-workflow.md),
  sonra /simplify → /review → /security-review.
- Relevant files: değişen global `~/.claude/` komutları (repo dışı, commit yok, backup
  `/tmp/spec-claude-codex.md.bak`); repo: `CLAUDE.md`, bu TASK/plan; vault: `claude-code-workflow.md`.
- Next command: `/commit` (otomaix) → vault commit/push (onayla) → `/simplify`.

## Verification
- Passed: drift Check A (diff=0, iki blok 45 satır) + Check B (token + 3 degradation);
  7 canlı yüzeyde bare /write-plan = 0; stub `[DEPRECATED]` + eski içerik temiz; not-run yok;
  Task 0 behavior-preservation (canonical bozulmadı). Codex bağımsız doğrulama geçti.
- Failed: _(yok)_
- Not run: end-to-end komut çalıştırması (yeni `/write-plan-claude-codex` gerçek bir spec'le
  henüz invoke edilmedi — skills listesi kaydı + içerik doğru, ama canlı akış denenmedi).

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
