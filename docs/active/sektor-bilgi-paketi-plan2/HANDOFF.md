---
task: sektor-bilgi-paketi-plan2
written: 2026-09-25 20:24 UTC (on yedinci oturum kapanışı)
---

# Context

Görev: `sektor-bilgi-paketi-plan2` · dal `feat/sektor-bilgi-paketi-plan2` (push durumu `git status -sb` ile ölçülür;
2026-09-25 20:3x UTC'de `9e22790`'a kadar push edildi — Eray onayı).
Madde 0 tasarımı: `docs/specs/2026-09-25-paket-zorunlu-kurallar-ve-gonderi-turu.md` (spec-approved).
Madde 0 planı: `docs/plans/2026-09-25-paket-zorunlu-kurallar-ve-gonderi-turu.md` (`plan-approved`, `fbd3d4e`; 22 görev,
iki aşama). Hat planı (yarım): `docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`. Last updated: 2026-09-25 20:24 UTC.

# Current State

Bu oturumda uygulama planı yazıldı ve onaylandı; **kod DEĞİŞMEDİ**. Kuyumculuk paketi 1. sürüm canlıda aktif, markaya
atanmamış. **Blocked: evet — tek karar:** yürütücü görev başına TEK plan izliyor (aşağıda); Eray kararı gerek.

# Resume From

**İlk iş — Eray'a sor (yürütme durumu çakışması, ölçüldü 20:2x):** `/execute-plan-claude-codex` planı görevin
`TASK.md` frontmatter'ındaki `source_plan`'dan okur (`ec_plan_path`) ve `docs/active` altında `- execute_start_ref:`
taşıyan TAM BİR `TASK.md` ister (`ec_state_dir`). Bu görevin `TASK.md`'si Plan 2'yi gösteriyor ve Plan 2'nin yürütme
durumunu taşıyor (`# Execution State` bölümü: `execute_mode` · `execute_started` · `execute_start_ref` ·
`ledger_window_ref` · `execute_review_log` · `execute_branch` · `cp_count` · `last_checkpoint_ref`; 2026-08-30'dan). Eray bugün
"plan mevcut görevde kalsın" dedi — bu öneri Claude'undu ve bu kısıt kontrol EDİLMEDEN verildi. Seçenekler:
- **(Öneri) Ayrı aktif görev:** `docs/active/paket-zorunlu-kurallar-ve-gonderi-turu/` (source_plan = yeni plan);
  Plan 2'nin `# Execution State` satırları bu `TASK.md`'den çıkarılıp Decisions Log'a "duraklatıldı, geri konacak
  satırlar" olarak yazılır (Plan 2'nin kalanı zaten Eray'ın video sistemi değişikliğine bağlı).
- Aynı görev: `source_plan` geçici olarak yeni plana, Plan 2 satırları park — geri dönüşte iki yönlü elle değişim.
Karar sonrası: `/execute-plan-claude-codex docs/plans/2026-09-25-paket-zorunlu-kurallar-ve-gonderi-turu.md`
(öneri: görev başına alt ajan — 2026-09-08 "bölerek dispatch" kararı). Task 1–2 commit'siz, Task 3'ün atomik
commit'inde iner (`merged-into T3`).

İlgili dosyalar: plan · spec · `apps/social/backend/app/services/{sector_content_schema,sector_packages}.py` ·
`app/core/{prompt_builder,caption_generator}.py` · `app/routers/posts.py` · `app/services/short_video.py` ·
`shared/db/migrations/` (sıradaki 038) · `shared/n8n-workflows/telegram-content-approval.json`.

# Verification

| Ne | Taze çıktı (bu oturum) |
|---|---|
| Plan kapıları | `_ec_plan_header_gate <plan>` → 22, rc=0, bozuk başlık yok · `plan-lint.sh` temiz · `command-blocks-maint.sh verify` PASS · 22 görevin hepsinde commit ya da `merged-into` |
| Codex | ön-analiz 19:04–19:08 (rc=0) + 4 review turu (19:35–41 · 19:53–58 · 20:05–09 · 20:11–13, hepsi rc=0); 13 bulgu (1C·9H·3M), 12 hakem teyitli kapalı, X2 kapsamı daraltıldı (Eray); log `~/.claude/logs/otomaix--ffc87809/2026-09-25-paket-zorunlu-kurallar-ve-gonderi-turu-plan.md` |
| DB (psql salt-okuma) | paketli gönderi 0/81 · `generation_stamps` 0 · atanmış marka 0 · otomatik yayın ayarı 0 · 1. sürüm gün türleri karma 9 / kutlama 2 / ticari-firsat 5 · `brand_products.type` + `is_active` var |
| Sınav verisi | paketli çıktı 472–717 jeton (ort. 594; `olcum/sonuc-sinav/b-sonuc.json`) |

**KOŞULMADI:** kod yok → test, tam takım, Katman-1 koşulmadı. Telegram sınırları (1024/4096) belge değeri, ölçülmedi.

# Risks

- **X2 (makbuz yarışı) plan düzeyinde hakem teyitsiz** — `unresolved_high_severity_override: true`; Task 13'te zorunlu
  gerçek veritabanı yarış testi + checkpoint'te Codex sınar.
- D13 kullanıcıya görünür değişiklik: makbuzu kaybolan paketli metin kaydedilemez (422), yeniden üretilir.
- Aşama B: yeni koşu açık soruyla durmazsa operatör yolu açılmaz (planın DUR-1'i).
- Kota okuması bayat kalıyor (12 %/6 %): `adversarial-review` çağrıları okumayı tazelemiyor.
- Önceki devirden sürenler: K-A (istek yasal yasakları da ezer; müşteri öncesi yeniden bak) · atama madde 0'dan önce
  YAPILMAZ · yetki belgesi no (G8) · madde 12 · iki eski Anthropic anahtarı · sızmış anahtarlar (Plan 2 sonrası ilk iş).

# Notes For Claude

- **Eray kararları (2026-09-25, bu oturum) — `TASK.md` Decisions Log'a HENÜZ yazılmadı** (yalnız madde 0 "Ev" satırında):
  (1) 2. sürüm yeni tam koşuyla, planın Aşama B'si; (2) X2: "Kuralı yaz, kilidi koda bırak"; (3) plan mevcut görevde
  kalsın — yukarıdaki kısıtla YENİDEN sorulacak.
- Codex substratı 7 ana dosyayı sır taramasıyla dışlıyor (`caption_generator.py`, `posts.py`, `ai.py`, `short_video.py`,
  `runs.py`, `writeback.py`, n8n `telegram-content-approval.json`) → checkpoint'lerde ilgili kesitleri `sed` ile çıkar,
  sır tara, prompt sonuna VERİ olarak `cat` ile ekle (oturum karalama dosyası kalıcı değil; yeniden üret).
- Güvenlik denetimi `rm -f -- "$DEĞİŞKEN"` biçimini engelliyor → prompt dosyası ve trap'te sabit tam yol kullan.
- `_ec_plan_*` yardımcıları argümanı değil aktif `TASK.md`'nin `source_plan`'ını okur; başka planı denetlemek için
  `_ec_plan_header_gate "<mutlak yol>"`.
- Codex tur süresi bu oturumda 2,5–6 dk; ikinci turdan önce maliyeti tek satırla bildir.

# Notes For Codex

Plan checkpoint'lerinde: planın sonundaki "Codex plan review kayıtları" kapalı bulguları yeniden açma; X2 Task 13
checkpoint'inde gerçek veritabanı yarış testiyle doğrulanacak (tek kazanan, kaybeden için ücretli çağrı 0); paketsiz yol
bayt-bayt (13 golden) korunmalı; dışlanan dosyalar prompta VERİ olarak eklenir.
