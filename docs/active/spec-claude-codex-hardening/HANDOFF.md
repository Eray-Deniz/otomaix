# Handoff

## Context
- Task: spec-claude-codex Robustness Hardening
- Canonical komut: ~/.claude/commands/spec-claude-codex.md (global, repo dışı)
- Amendment hedefi: docs/specs/2026-05-20-spec-claude-codex-command.md
- Branch: main
- Last updated: 2026-05-25

## Current State
- Summary: Round-1 `5e23c04` + Round-2 `bc17e27` push edildi. Round-3 (Küme C: #5 sayaç
  persist, #6 kapsam ön-kontrolü, #8 araştırıldı/kaldırılmadı) uygulandı.
- Blocked: Hayır. Kalan: round-3 doc commit (kullanıcı onayı).

## Resume From
- Start here: round-3 doc commit. Sonrası: task kapanış/arşiv (kullanıcı kararı) + opsiyonel vault promotion.
- Relevant files:
  - ~/.claude/commands/spec-claude-codex.md (round-1/2/3 hepsi uygulandı)
  - docs/specs/2026-05-20-spec-claude-codex-command.md (§11 10 madde + §3 supersede, timeout 480s)
  - docs/reviews/2026-05-25-spec-claude-codex-hardening.md (review kaydı)
- Next command: round-3 doc commit.
- Not: komut dosyası git'te DEĞİL (global ~/.claude/) — commit yalnız repo docs'unu kapsar.

## Verification
- Passed (round-1): companion kodu doğrulandı (handleReviewCommand --background kullanmıyor
  682-709, handleTask kullanıyor 758, timeout coreutils 9.4, adversarial read-only hardcoded).
  bash -n 3 fonksiyonel blok temiz; Adım no 0-12 sırada; stale token yok; yeni yapı
  (protokol, <CALL>, <DROPPED_ALT>, timeout 480s) yerinde. Fresh review merge-ready.
- Round-2: Codex 2-3. review bulguları doğrulandı + düzeltildi (degradation downstream
  Adım 3/7; review'sız final yasak = Option 1; §3 supersede; active-doc drift). Adım no
  0-12 sırada, degradation gate'leri yerinde, 240s drift yok (re-check geçti).
- Round-3: #8 companion doğrulandı (resolveReviewTarget git.mjs:134 auto→clean=branch;
  collectReviewContext :299 scope→diff bağlamı). codex_targeted_fixes 8 yerde tutarlı;
  scope bash `bash -n` temiz; Adım no 14; §11 10 madde sıralı; eski yanlış yorum yok.
- Round-3 (Codex 4. review): 3 doc drift düzeltildi — yanlış "diff'siz" iddiası 0 (cmd+spec);
  spec body frontmatter `codex_targeted_fixes` hizalı (draft+final); backward-compat notu
  (alan yoksa 0, ilk write'ta ekle); §11.8/§11.10 cross-ref.
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
