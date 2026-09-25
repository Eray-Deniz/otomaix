---
task: paket-zorunlu-kurallar-ve-gonderi-turu
written: 2026-09-25 22:05 UTC (ilk yürütme oturumu kapanışı)
---

> ⚠️ YÜRÜTME AÇIK (başlangıç: 2026-09-25 20:33) — güncel durum TASK.md + git defterinden okunur, çelişkide onlar esastır.

# Context

Plan: `docs/plans/2026-09-25-paket-zorunlu-kurallar-ve-gonderi-turu.md` (22 görev, iki aşama; spec aynı adla
`docs/specs/`). Dal `feat/sektor-bilgi-paketi-plan2` — push durumu `git status -sb` ile ölçülür (bu oturumda HİÇ
push yapılmadı; son push `2e17cf1`). Dış depo `/root/otomaix-sosyal-medya-arastirmasi` iki commit aldı (`e7e66a4`,
`5ecf2d9`; upstream'i yok). Yürütme: inline (Eray seçimi). Codex log: `execute_review_log` (TASK.md).

# Current State

Task 1–6 commit'li. Eray talimatı: "Task 6 tamamlandıktan sonra dur ve onay bekle" → duruldu. Checkpoint 2 açık
(F2); Eray F2 kararını verdi (dar muafiyet), uygulama bu devirle sıradaki oturuma kaldı. Task 7 BAŞLAMADI.

# Resume From

1. **F2 düzeltmesi (Eray onaylı, yeniden sorma):** `sektor_gercekleri` alanında yalnız birebir `içerik-önerilmez`
   öğesi kaynak bağı istemez; gerçek doğrularda bağ aynen. Dokunulacak yerler ve kabul testi TASK.md Open
   Problems F2'de. TDD: önce aktif paket yok + aktif şema-1 uçtan uca kırmızı test (sentez→motor→operatör),
   sonra negatif test (muafiyet gerçek doğruya genişlemez). Commit `Exec-Task: T4-fix2` (ya da `T0-f2`).
2. Checkpoint 2 kapanış turu (tur 3) — CLOSURE-VERIFICATION prompt'u, F2 ledger'ı; approve gelirse §8.6 mutation
   protokolü (`last_checkpoint_ref` + `cp_count` ilk kez yazılır).
3. **Eray onayı sonrası** Task 7 (seçmeli dağarcık). Resume `/execute-plan-claude-codex <plan>` → Adım 3 `active`
   dalı: devam (a).

# Verification

| Ne | Taze çıktı (bu oturum) |
|---|---|
| Tam takım | `98a355f`'te **5147 passed / 0 failed** (415 s). Sonraki `531ef92` yalnız pin: ilgili 5 dosya 2029 passed |
| Defter | `ec_ledger_view ... --post-window` rc=0 (T4 footer `docs-only`→`green-only` düzeltildi, amend, push'suz) |
| Codex | ön-analiz rc=0 · checkpoint 1: 3 tur (F1 → override) · checkpoint 2: 2 tur (F2 açık); her tur ~3,5–5 dk |
| Mutasyonlar | her yeni kapı için kırmızıya döndü, dosya yedeğiyle geri alındı (commit mesajlarında) |

**KOŞULMADI / DENENMEDİ:** Katman-1 paketli golden'lar (Task 9'da doğar) · canlıya hiçbir şey · gerçek sentez
koşusu (F2'nin uçtan uca kanıtı henüz yok) · frontend.

# Risks

- F1 override (kanca etiketi `Mn` işaretle gizlenebilir) — final incelemede yeniden değerlendirilir.
- F2 kapanmadan Task 19 (yeni tam koşu) motorda `blocked` olur — ücretli koşudan önce MUTLAKA kapanmalı.
- Kota okuması bayat kaldı (12 %/6 %, "stale"); uzun Codex turundan önce tazelenmedi.
- Dış depoda benden önce var olan 41 silinmiş dosya (`kuyumculuk.md` dahil) duruyor — dokunulmadı, sahibi belirsiz.

# Notes For Claude

- Codex prompt dosyası: `/root/.claude/tmp/2026-09-25-feat-sektor-bilgi-paketi-plan2-execute.prompt` — `rm -f` sabit
  yolla, sonra Write; çağrı `run_in_background` + `run_codex_scan "base-review" adversarial-review --base <ec_state_base_ref>`.
  Sonuç çıktıda değil log dosyasında: son `## Codex call (base-review)` bölümü.
- Substrat dışlaması: `writeback.py`, `runs.py`, `caption_generator.py`, `posts.py`, `ai.py`, `short_video.py`,
  n8n JSON, bazı testler → ilgili farkı sır taramasından geçirip prompt'a VERİ olarak ekle. Dış depo farkı da öyle.
- `Exec-Kind`: JSON pin "çalıştırılabilir yol" sayılır → `green-only`, `docs-only` DEĞİL.
- Kenara alma gerekirse `git stash push -- <yollar>`; checkpoint ağacı temiz ister.
- `normalize_special_day_key` büyük `İ`yi bölüyor (`ti-cari`) — iki taraf aynı fonksiyonu kullandığı için zararsız,
  dokunulmadı; tür katlamada leaf `_fold_turkish` kullanıldı.

# Notes For Codex

Checkpoint 2 tur 3: yalnız F2 düzeltme commit(ler)i + onların taradığı çağrı yerleri; F1 override yeniden açılmaz.
