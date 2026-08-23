# Handoff

## Context
- Task: sektor-bilgi-paketi — **faz: spec ONAYLI + sentez deposu sweep borcu
  kapsam daraltmasıyla kapandı; sırada sıfırdan plan**
- Last updated: 2026-08-23 (üçüncü oturum — sweep kapanışı)
- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (status: `spec-approved`;
  tüm K-ID satırları kapanış statüsünde)
- Karar listesi: `docs/active/sektor-bilgi-paketi/KARAR-KAPANIS-LISTESI.md` (arşivlik)
- Review log: `docs/reviews/codex/2026-08-23-sektor-bilgi-paketi-spec.md` (3 tur SHIP)
- ⚠️ Eski spec (2026-07-11) ve plan (2026-07-12) **superseded** — dikkate alınmaz.

## Current State
- **Sweep borcu kapandı (kapsam daraltması, Eray):** kapanan 51 kararın (45 tur +
  K-57 · K-70 · K-83 · K-143 bağlı + K-20 · K-21) araştırma deposuna geriye dönük
  işlenmesi İPTAL edildi. Yerine kaynak belgeye (`/root/otomaix-sosyal-medya-arastirmasi/
  sektor-bilgi-paketi-spec-input.md`) iki statü notu eklendi: belge başı (51 kapanışın
  ID listesi + kanonik kayıt işaretçileri + "çelişkide spec esastır") ve Bölüm 17
  başlığı (kısa ayna not). Snapshot (`docs/research/2026-08-21-sektor-bilgi-paketi-
  spec-input.md`) notlu kaynakla yeniden eşitlendi.
- **K-57 tespiti:** K-56 kapanışı ("rol sorusu da kapandı") K-57'yi fiilen kapatıyor;
  TASK "Ek kapanışlar" listesine eklendi.
- Başlanıp geri alınan tam sweep'in düzenlemeleri hiçbir commit'e girmedi; geri alım
  sonrası kaynak sha baseline ile birebir doğrulandı.

## Resume From (sıra)
1. **`/write-plan-claude-codex`** — plan SIFIRDAN (eski plan superseded). Girdi:
   yeni spec + snapshot. **Karar statüsünde spec esastır** — snapshot'taki `[AÇIK]`
   ifadeleri 51 kapanış için bayattır (statü notu belge başında). K-32…K-37 (pilot
   genişleme şartları) plan sırasında ayrıca gelecek.

## Verification (bu oturum)
- **Passed:** geri alım sonrası kaynak sha = `f056988d…` (snapshot baseline ile
  birebir; `sha256sum` ile doğrulandı) · statü notundaki 45'lik ID listesi
  KARAR-KAPANIS-LISTESI + TASK Decisions Log'a karşı bire bir sayıldı (45 + 4 bağlı
  + K-20/K-21 = 51) · notlu kaynak commit'lendi (`b356033`, 3145 satır, sha
  `efe21707…`) ve snapshot yeniden eşitlendi — `tail -n +7 | sha256sum` kaynak
  sha'sıyla birebir (bayt-özdeşlik PASS).
- **Not run:** Codex doğrulaması bu oturumda koşulmadı (statü notu tek elden yazıldı) ·
  spec'in ~45 kapanış metni hâlâ review zincirinden geçmedi (önceki oturumdan kalan
  risk — plan öncesi hızlı kapanış-sweep'i hâlâ değerli) · canlı hiçbir şey çalıştırılmadı.
- **Kalan risk:** snapshot gövdesi bilinçli olarak bayat — plan yazımı/Codex review
  sırasında snapshot'tan alıntılanan bir "açık karar" ifadesi statü notuna karşı
  kontrol edilmeli; çelişkide spec esastır.

## Notes For Claude
- HANDOFF rolling; karar izi TASK Decisions Log'da.
- Karar sorma formatı kalıcı: tek karar/soru + somut akış-senaryo özeti
  (hafıza: decision-review-one-by-one).
- K-56 olay-bazlı model (eşik YOK) — plan yazarken alarm tasarımını eşiksiz kur.
- Sweep'in yeniden açılma koşulu: arşiv belgesi yeniden canlı girdi olursa
  (TASK Decisions Log 2026-08-23 kaydı).

## Notes For Codex
- Plan review'ında eski planın hiçbir hükmü referans alınmaz; kaynak yalnız yeni
  spec (spec-approved) + snapshot. Snapshot'ın Bölüm 17/gövde statüleri 51 kapanış
  için bayattır — statü notu (belge başı) bağlayıcıdır, çelişkide spec esastır.
- Spec'teki ~45 kapanış eki tek elden yazıldı — plan öncesi kapanış-sweep
  doğrulaması değerli (occurrence tutarlılığı + K-ID çapraz atıfları).
