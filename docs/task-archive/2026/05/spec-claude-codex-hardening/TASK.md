---
title: spec-claude-codex Robustness Hardening
status: archived
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

Round-1 (6 edit + drift kapatma + spec Amendment + fresh review) commit `5e23c04`,
origin/main'e push edildi. Fresh review merge-ready, 0 critical, 2 Important düzeltildi
(240s→480s, `$SCOPE` notu). Review kaydı: `docs/reviews/2026-05-25-spec-claude-codex-hardening.md`.

Round-2 (Codex 2-3. review) commit `bc17e27`, push edildi: degradation downstream Adım 3/7'ye
bağlandı (High); review'sız final YASAKLANDI (Option 1); spec §3 supersede; active-doc drift.

Round-3 (Küme C): #5 sayaç frontmatter persist (`codex_targeted_fixes`), #6 kapsam ön-kontrolü
(Adım 2 başı, overkill önleme), #8 araştırıldı → kaldırılMADI (scope diff bağlamı besliyor;
yalnız yanıltıcı clean-dalı yorumu düzeltildi). Spec §11 (10 madde) + §3 güncel. Uygulandı.
Codex 4. review 3 drift yakaladı (clean-dalı "diff'siz" iddiası, spec body frontmatter'da
`codex_targeted_fixes` eksik, backward-compat belirsiz) → hepsi düzeltildi.

**KAPANIŞ (2026-05-25):** Tüm turlar canlı (`5e23c04`, `bc17e27`, `1f4ad48`). Vault promote
edildi: `[[cross-project/infrastructure/codex-entegrasyonu]]` (Sınırlamalar — companion
background/`--wait` gerçeği). Task archived.

# Open Problems

_(yok)_

# Decisions Log

- 2026-05-25: Background lifecycle TERK → uniform `timeout 480s node companion <call>`
  (ilk değer 240s; review'da 480s'e çıkarıldı — normal uzun review kesilmesin).
  Sebep: `handleReviewCommand` `--background`'u parse edip kullanmıyor (koşulsuz
  `runForegroundCommand`), job-lifecycle yalnız `task`'ta. Dış `timeout` her iki
  çağrı için uniform, job-id parsing yok (kırılganlık elenir). Kod doğrulandı.
  → Vault: [[cross-project/infrastructure/codex-entegrasyonu]] (Sınırlamalar, 2026-05-25)
- 2026-05-25 (round-2): Degradation "Claude-only" downstream'e bağlandı — Adım 3 Codex
  yoksa tek-perspektif (öneri/sentez/dropped-alt atla); Adım 7 Codex review yoksa
  findings-döngüsü geçersiz. (Codex 2. review High bulgusu.)
- 2026-05-25 (round-2b): Review'sız final YASAK (Option 1) — Adım 7 degradation yalnız
  "tekrar dene (Recommended)" / "durdur (draft kalır)"; Adım 10'a invariant notu.
  Değişmez kural: `codex_review_status: approved` = Codex gerçekten review etti. Sebep:
  ilk fix "review'sız onayla" eklemişti → Adım 10 yine `approved` yazıp audit yalanı
  üretiyordu (Codex 3. review). Option 2 (skipped-degraded status) reddedildi — yüzey
  büyütür, invariant gevşetir.
- 2026-05-25: Companion'a background eklemek REDDEDİLDİ — vendored plugin dosyası,
  güncellemede ezilir. Komut tarafında çözüm.
- 2026-05-25: #4 (sentez yanlılığı) ekstra Codex çağrısı ALMAZ — "açık muhasebe"
  zaten Adım 3'te var; bias guard'lar: steelman kuralı + downstream Adım 6 +
  dropped-alternative'i Adım 6 prompt'una geçirme.
- 2026-05-25 (round-3): #5 UYGULANDI — `targeted_consistency_fix_count` frontmatter
  `codex_targeted_fixes`'e persist (Adım 5/7/9 yazar, Adım 1.5 okur). Önce review-log
  düşünülmüştü; Adım 9 artışının ardından review-log turn'ü olmadığı için frontmatter
  seçildi (`codex_review_iterations` deseni).
- 2026-05-25 (round-3): #6 UYGULANDI — `--light` modu REDDEDİLDİ (yüzey ikiye katlar);
  yerine Adım 2 başında kapsam ön-kontrolü (küçük fikirde /brainstorm öner, vazgeçilebilir).
- 2026-05-25 (round-3): #8 ARAŞTIRILDI → kaldırılMADI. `collectReviewContext(scope)`
  (git.mjs:299) diff bağlamı besliyor (working-tree→uncommitted, clean→branch); scope ölü
  değil ama prompt odağı yanında ikincil. Tek kusur: "boşsa scope'suz" yorumu yanlıştı
  (companion auto→default branch diff) → yorum düzeltildi, mekanik korundu.
- 2026-05-25: Yeni spec AÇILMADI — tasarım bu konuşmada yapıldı; mevcut 2026-05-20
  spec'e "Amendment 2026-05-25" bölümü (drift kapatma + WHY kalıcılığı).

# Scope (bu tur — Küme A + B)

- A: #1 Codex-failure degradation + #2 timeout → Codex Çağrı Protokolü (EDIT 1, 2, 4)
- B: #3 menü→gerekçeli öneri+steelman (EDIT 3), dropped-alternative Adım 6 prompt
  (EDIT 5), #7 bağımsızlık kuralı (EDIT 2), #9 AGENTS.md preflight (EDIT 1),
  #10 active-layer sözleşme (EDIT 6)
- Küme C (round-3): #5 sayaç persist ✓, #6 kapsam ön-kontrolü ✓, #8 araştırıldı (kaldırılmadı)
- Atlandı: #4 açık muhasebe (zaten Adım 3'te mevcut)
