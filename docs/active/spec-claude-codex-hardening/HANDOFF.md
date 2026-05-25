# Handoff

## Context
- Task: spec-claude-codex Robustness Hardening
- Canonical komut: ~/.claude/commands/spec-claude-codex.md (global, repo dışı)
- Amendment hedefi: docs/specs/2026-05-20-spec-claude-codex-command.md
- Branch: main
- Last updated: 2026-05-25

## Current State
- Summary: 6 edit + drift kapatma + spec amendment UYGULANDI ve doğrulandı.
  Tasarım Codex review sonrası background → uniform foreground+timeout'a çevrildi.
- Blocked: Hayır. Kalan: /review + /commit (kullanıcı onayı).

## Resume From
- Start here: /commit (review bitti, merge-ready).
- Relevant files:
  - ~/.claude/commands/spec-claude-codex.md (6 edit + 2 review fix uygulandı)
  - docs/specs/2026-05-20-spec-claude-codex-command.md (§11 amendment, timeout 480s)
  - docs/reviews/2026-05-25-spec-claude-codex-hardening.md (review kaydı)
- Next command: /commit.
- Not: komut dosyası git'te DEĞİL (global ~/.claude/) — commit yalnız repo docs'unu kapsar.

## Verification
- Passed: companion kodu doğrulandı (handleReviewCommand --background kullanmıyor
  682-709, handleTask kullanıyor 758, timeout coreutils 9.4, adversarial read-only
  hardcoded). Edit sonrası: bash -n 3 fonksiyonel blok placeholder doldurularak temiz;
  Adım no 0-12 sırada; stale token (`--wait`/eski çağrı/"Companion script'i bul") yok;
  yeni yapı (protokol, <CALL>, <DROPPED_ALT>, timeout 240s) yerinde.
- Failed: _(yok)_
- Not run: komutun canlı end-to-end denemesi (dummy fikir) — opsiyonel

## Risks
- Edit sonrası iç içe markdown fence bozulması (Codex flag etti) — uygularken
  yapı temiz tutulacak, `bash -n` ile snippet'ler doğrulanacak.
- Placeholder drift (`<SPEC_PATH>`, `<DROPPED_ALT>`) — literal placeholder konvansiyonu korunacak.

## Notes For Claude
- Codex bloklayıcı itirazı (adversarial-review background yok) doğrulandı + çözüldü.
- AskUserQuestion max 4 seçenek — EDIT 3 tam 4'e sığıyor (öneri+2 yön+Hiçbiri).
- Companion'a dokunma (vendored).
- Review'ın özellikle dikkat çektiği: dış `timeout` Codex'in iç poll bütçesinden (240s)
  büyük olmalı ki normal uzun review kesilmesin → 480s yapıldı. İleride review'lar
  düzenli 480s'i aşarsa değer tekrar gözden geçirilebilir (tunable).

## Notes For Codex
- Bu edit'ler global ~/.claude/commands/ dosyasında — Codex sandbox writable root
  dışı, tek başına uygulayamaz; patch önerir, Claude uygular.
- Önce okunması gereken: bu TASK.md + ~/.claude/commands/spec-claude-codex.md
