---
title: spec-claude-codex Robustness Hardening
status: active
started: 2026-05-25
last-touched: 2026-05-25
blocked-by: null
---

# Goal

`/spec-claude-codex` komutuna dayanıklılık sertleştirmesi: Codex çağrıları
çökerse/asılırsa komut sessizce kırılmasın, Adım 3 nötr menü yerine gerekçeli
öneri sunsun, sentez yanlılığı görünür olsun. Claude + Codex ortak review'ından
geçmiş 6 edit + spec amendment. **Başarı:** komut dosyasına 6 edit uygulanmış,
eklenen bash `bash -n` temiz, komutun kendi Consistency Checklist'i (referans
bütünlüğü: adım no, flag, path) geçiyor, mevcut spec'te drift kapatılmış.

# References

- Canonical komut: `~/.claude/commands/spec-claude-codex.md` (global, repo dışı)
- Mevcut spec (amendment hedefi): `docs/specs/2026-05-20-spec-claude-codex-command.md`
- Companion (vendored, dokunulmaz): `~/.claude/plugins/cache/openai-codex/codex/1.0.4/scripts/codex-companion.mjs`

# Current Status

Uygulama + review tamam (2026-05-25). 6 edit + drift kapatma + spec Amendment işlendi.
Fresh subagent review: **merge-ready**, companion iddiası kaynak koddan doğrulandı,
0 critical. 2 Important (timeout 240s→480s, `$SCOPE` tırnaksız notu) düzeltildi.
Review kaydı: `docs/reviews/2026-05-25-spec-claude-codex-hardening.md`.
**Kalan:** /commit (kullanıcı onayı).

# Open Problems

_(yok)_

# Decisions Log

- 2026-05-25: Background lifecycle TERK → uniform `timeout 240s node companion <call>`.
  Sebep: `handleReviewCommand` `--background`'u parse edip kullanmıyor (koşulsuz
  `runForegroundCommand`), job-lifecycle yalnız `task`'ta. Dış `timeout` her iki
  çağrı için uniform, job-id parsing yok (kırılganlık elenir). Kod doğrulandı.
- 2026-05-25: Companion'a background eklemek REDDEDİLDİ — vendored plugin dosyası,
  güncellemede ezilir. Komut tarafında çözüm.
- 2026-05-25: #4 (sentez yanlılığı) ekstra Codex çağrısı ALMAZ — "açık muhasebe"
  zaten Adım 3'te var; bias guard'lar: steelman kuralı + downstream Adım 6 +
  dropped-alternative'i Adım 6 prompt'una geçirme.
- 2026-05-25: #6 `--light` modu REDDEDİLDİ (yüzey ikiye katlar) — yerine komut başı
  hafif sınıflandırma/kaçış önerisi (bu turda kapsam dışı, Küme C).
- 2026-05-25: #8 git-scope sadeleştirme ERTELENDİ (Küme C) — adversarial-review
  context'i `collectReviewContext(scope)` ile git-diff'ten besleniyor, scope ölü değil.
- 2026-05-25: Yeni spec AÇILMADI — tasarım bu konuşmada yapıldı; mevcut 2026-05-20
  spec'e "Amendment 2026-05-25" bölümü (drift kapatma + WHY kalıcılığı).

# Scope (bu tur — Küme A + B)

- A: #1 Codex-failure degradation + #2 timeout → Codex Çağrı Protokolü (EDIT 1, 2, 4)
- B: #3 menü→gerekçeli öneri+steelman (EDIT 3), dropped-alternative Adım 6 prompt
  (EDIT 5), #7 bağımsızlık kuralı (EDIT 2), #9 AGENTS.md preflight (EDIT 1),
  #10 active-layer sözleşme (EDIT 6)
- Ertelendi (Küme C): #5 sayaç persist, #6 lightweight kaçış, #8 git-scope sadeleştirme
- Atlandı: #4 açık muhasebe (zaten Adım 3'te mevcut)
