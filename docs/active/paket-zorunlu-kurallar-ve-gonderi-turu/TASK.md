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
- Plandan devralınan kararlar: 2. sürüm yeni tam koşuyla (Aşama B) · X2 "Kuralı yaz, kilidi koda bırak"
  (`unresolved_high_severity_override: true`; Task 13 gerçek veritabanı yarış testi zorunlu).

# Open Problems

- **X2 — makbuz yarışı plan düzeyinde hakem teyitsiz.** Ev: Task 13 + onun checkpoint'i.
