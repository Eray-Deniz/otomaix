---
title: Sektör paketi — zorunlu kurallar, türe göre seçim, gönderi türü (madde 0 uygulaması)
status: active
started: 2026-09-25
last-touched: 2026-09-25
blocked-by: null
source_plan: docs/plans/2026-09-25-paket-zorunlu-kurallar-ve-gonderi-turu.md
source_task: docs/active/sektor-bilgi-paketi-plan2/TASK.md
---

# Goal

Sektör paketinin kuralları modele bağlayıcı gitsin (zorunlu blok), kalıplar gönderi türüne göre seçilsin, model
basılan her kural için karar beyan etsin ve kullanıcı onay verirken çiğnenen kuralı görsün; paketin 2. sürümü yeni
tam koşuyla üretilip sınavdan geçtikten sonra etkinleşsin. Spec: `docs/specs/2026-09-25-paket-zorunlu-kurallar-ve-gonderi-turu.md`
(spec-approved). Kaynak: Plan 2 görevinin Open Problems madde 0'ı.

# Execution State

- execute_mode: inline
- execute_started: 2026-09-25 20:33
- execute_start_ref: 2e17cf1285f99e93909d2ddc2fc228effbf5f3ec
- ledger_window_ref: 2e17cf1285f99e93909d2ddc2fc228effbf5f3ec
- execute_review_log: /root/.claude/logs/otomaix--ffc87809/2026-09-25-feat-sektor-bilgi-paketi-plan2-execute.md
- execute_branch: feat/sektor-bilgi-paketi-plan2

# Current Status

Yürütme açık (2026-09-25). "Nerede kalındı" git defterinden okunur (`ec_ledger_view`, commit footer'ları).

# Decisions Log

## Görev açıldı (2026-09-25, Eray kararı)

- Plan ayrı aktif görevde yürür (Plan 2 görevinin Decisions Log'u "Madde 0 ayrı göreve alındı"). Plan 2'nin
  yürütme satırları orada girintili park edildi.
- Yürütme biçimi: inline (Eray seçimi; alt ajan önerilmişti).
- Checkpoint 1 (Task 1–3): Codex 3 tur, F1 (kanca etiketi) iki düzeltmeyle daraldı, üçüncü turda aynı sınıf
  yeniden açıldı → sistemik-sınıf DUR → Eray: riski kabul et, devam (override; Open Problems'ta).
- Task 4 kararı (yürütücü): araştırma şablonuna 9. alan BAŞLIĞI açılmadı — `brief_doctor` alan başlıklarını ve
  Bölüm C iddia hücrelerini 8 alanlık kapalı kümeye bağlar (`test_temel_alanlar_pinlenmis_sablondan_okunur`),
  mevcut üç kaynak raporda alan yok; şablon adı bir notla taşır, sentez alanı kaynaklı iddialardan türetir.
- Plandan devralınan kararlar: 2. sürüm yeni tam koşuyla (Aşama B) · X2 "Kuralı yaz, kilidi koda bırak"
  (`unresolved_high_severity_override: true`; Task 13 gerçek veritabanı yarış testi zorunlu).

# Open Problems

- **X2 — makbuz yarışı plan düzeyinde hakem teyitsiz.** Ev: Task 13 + onun checkpoint'i.
- **[checkpoint-override turn 3] F1 (high, Codex) — kanca tür etiketi görünmez birleşen işaretle gizlenebilir.**
  `(tü\u034fr: hizmet)` kancası sessizce `satis` sayılır; aynı işaret `ton (yumuşak):` önekini de gizler. İki
  düzeltme indi (`47deb9f` bitişik parantez/ortada/çift etiket; `bb0283f` `Cf` görünmez karakter + NFKC); üçüncü
  tur `Mn` sınıfını açtı. Eray kararı (2026-09-25): **riski kabul et, devam** (önerilen izin listesi — kanca/ton
  metninde yalnız Latin harf·rakam·noktalama·sembol·boşluk; canlı paketin 15.157 karakterinin 0'ı dışında —
  seçilmedi). Ev: final Codex incelemesi (Adım 11) bu override'ı yeniden değerlendirir; yeniden açılma koşulu:
  paket içeriğine üçüncü taraf ham metni girdiği gün ya da sınavda tür uyuşmazlığı görülürse.
- **Task 19 ön koşulu — CLI aktif paket biçimi (plan dışı kusur, 2026-09-25).** `sector_pipeline_cli._aktif_paket`
  aktif paketi yalnız içerik olarak veriyordu; sentez (`_aktif_birimler`, EK-H'deki `unit_id`'ler) ve motor
  (`_aktif_ozel_gunler`) `{schema_version, content, decision_log}` sarmalı okur → aktif paket varken ikinci koşu
  sentezde düşerdi. Düzeltme ayrı commit (`T0-aktifsarmal`); denetçi paketi yalnız içeriği almaya devam eder.
  Ek (Codex tur 1 notu): aktif şema-1 + yeni aday şema-2 yolunun uçtan uca motor testi yok — Task 19'dan ÖNCE eklenir.
