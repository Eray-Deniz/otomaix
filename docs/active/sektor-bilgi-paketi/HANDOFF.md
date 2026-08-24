# Handoff

> ⚠️ YÜRÜTME AÇIK — bu anlatı oturum sonuna aittir; canlı yürütme durumu TASK.md
> "Execution State" + git defterinden okunur, çelişkide onlar esastır.

## Context
- Task: sektor-bilgi-paketi — Plan 1 yürütmesi açık (`/execute-plan-claude-codex` protokolü)
- Last updated: 2026-08-24 (sekizinci oturum — Task 5 ve Task 6)
- Plan: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (`plan-approved`)
- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Dal: `feat/sektor-bilgi-paketi` (**upstream YOK — hiç push edilmedi**)
- Codex ham review log'u: `/root/.claude/logs/otomaix--ffc87809/2026-08-24-feat-sektor-bilgi-paketi-execute.md`

## Current State
- **Biten:** Task 1 (pytest altyapısı) · Task 2 (migration 032) · Task 3 (runner + geri alma +
  R-17 ölçümü) · Task 4 (R-01/R-02 kök kova korumaları) · Task 5 (veri/API regresyon + sweep) ·
  Task 6 (Katman-1 yakalama altyapısı + fixture'lar). **16 task'ın 6'sı.**
- **Devralınan borç KAPANDI:** Task 4'ün doğrulanmamış `afc8daf` commit'i checkpoint 5 tur 1'de
  kapanış titizliğiyle incelendi ve kapalı bulundu. Bu oturuma açık kapı DEVRETMİYOR.
- **Mod:** inline (Eray talebi). `execute_mode: subagent-driven` kaydı BİLEREK değiştirilmedi
  (Task 1-2'yi doğru anlatıyor). **inline YALNIZ task yazımını kapsar; review/checkpoint kapıları
  normal koştu.**
- **Checkpoint:** `cp_count: 6`. Checkpoint 5 (Task 5) beş turda **override** ile kapandı —
  `approve` ALINMADI, Eray kararıyla döngü kapatıldı; audit satırı review log'unda. Checkpoint 6
  (Task 6) tek turda **`verdict: approve`**, kritik/yüksek bulgu yok.
- **Ortam (yeni oturumda TEKRAR KURMA — duruyor):** `apps/social/backend/.venv`.
  Komut daima `.venv/bin/python`; makinede `python` komutu YOK.

## Resume From (sıra)
1. **Task 7** — `### Task 7: Katman-1 kısa video + legacy yüzeyleri — fixture seti tamamlanır`.
   **Bu bir FREEZE kapısıdır:** Katman-1 fixture seti tam yeşil olmadan Task 8'e GEÇİLMEZ.
2. Task 7'ye başlamadan ÖNCE, aşağıdaki Risks'teki **birinci** maddeye bak: harness'ın metin
   olmayan blokları kayıplı işlemesi. Task 7 kısa video yüzeylerini ekliyor ve zengin blok
   kullanan ilk tüketici orası olabilir. Fail-closed hâle getirmek (metin olmayan bloğu tip
   işaretiyle geçmek yerine REDDETMEK) birkaç satır; Task 7'nin ilk adımı olarak yapılması
   önerilir.
3. Sonra Task 8 → 16.

## Verification (bu oturum)
- **Koşan komutlar / taze çıktı:**
  - `cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → **78 passed**
    (son koşum Task 6 commit'inden önce; commit sonrası dosya değişmedi).
  - `ec_ledger_view <execute_start_ref> <root> - --post-window` → **rc=0**, her satır etiketli.
  - `scripts/sector_sweep.py` canlı `otomaix`e karşı → `brands_total: 2`,
    `brands_root_anchored: 2`, `differences: 0`, rc=0; baseline akışı `remapped: 0 / removed: 0 /
    added: 0`, rc=0.
  - Canlı gösterim: `otomaix_test` tabanı `otomaix`e verilince **rc=2**, iki kimlik de mesajda.
  - Belirsiz bağlantı dizesinin beş biçimi → **rc=2**, parola stdout/stderr'de **YOK** (ölçüldü).
  - Fixture alarmı: dondurulmuş dosyaya tek satır eklenince ilgili test **kırmızı**.
- **Pozitif kontrol disiplini:** bu oturumun her düzeltmesi, düzeltmeden ÖNCEKİ sürüme karşı düşen
  bir testle kanıtlandı — Task 5 zincirinde beş tur, Task 6'da fixture alarmı. TEK istisna bilinçli:
  `test_sweep_accepts_new_brands_on_same_target` ve
  `test_brand_sector_mappings_full_sweep_unchanged` hata düzeltmiyor, sınır pinliyor; ikisi de
  öncesinde ve sonrasında geçer ve bu commit mesajlarında YAZILI.
- **Codex:** checkpoint 5 → 5 tur, override ile kapandı (`approve` yok). checkpoint 6 → 1 tur,
  **`approve`**, iki orta bulgu.
- **DENENMEYEN / kapsanmayan:**
  - Canlıya (`otomaix`) hiçbir migration uygulanmadı — 032 canlı uygulaması manuel adım, Task 16.
  - Frontend hiç çalıştırılmadı (`npx next build` koşmadı — ilk gerektiği yer Task 12).
  - Sweep script'i GERÇEK üretim sunucusunda değil, lokal 5433'teki canlı kopyada koşuldu.
  - Alt sektör satırı OLAN bir canlı veritabanında sweep hiç koşulmadı (bugün canlıda alt satır
    yok — o yol yalnız testte kanıtlı).
  - Fixture'lar YALNIZ caption tekli/carousel + fikir yüzeyini kapsıyor; kısa video ve legacy
    yüzeyler Task 7'de gelecek — Katman-1 seti bugün EKSİK, freeze kapısı henüz KAPALI DEĞİL.
  - `capture.py` metin olmayan blokla hiç sınanmadı (bugünkü dört fixture tamamen metin).
  - PostgreSQL 18 dışında hiçbir sürümde test koşulmadı.

## Risks
- **[medium, accepted_risk — Task 7 başında ele alınması ÖNERİLİR]** `capture.py::rendered`
  kayıplı: metin olmayan bloklar yalnız `<tip>` işaretine, `cache_control` yalnız `type` alanına
  iner. Bugünkü dört fixture tamamen metin olduğu için mevcut kanıt etkilenmiyor, AMA harness
  K-20 genel arayüzü olarak ilan edildi ve zengin blok kullanan ilk tüketici sessizce aynı
  fixture'ı paylaşabilir. Fail-closed karşılığı ucuz: metin olmayan bloğu tip işaretiyle geçmek
  yerine REDDET. Evi: Task 7'nin ilk adımı (zengin blok kullanan ilk yüzey orada).
- **[medium, accepted_risk]** İki pytest oturumu aynı anda koşarsa biri diğerinin `otomaix_test`
  veritabanını DROP eder (kilit yok).
- **[medium, accepted_risk]** Migration keşfi tekrarlı numarayı reddetmiyor (`032_a` + `032_b`
  ikisi de 32 sayılır).
- **[medium, accepted_risk]** `db` fixture'ının testler-arası geri sarma garantisini kanıtlayan
  test yok.
- **[medium, accepted_risk]** `sector_research_artifacts` TRUNCATE korumasının regresyon testi yok.
- **[medium, accepted_risk]** Geri alma red testi iki korunan tabloyu AYNI anda dolduruyor;
  preflight'ın OR kapısının bir ayağı silinse test yine yeşil kalır.
- **[medium, accepted_risk — Eray kararı]** On-prem paketi PostgreSQL 16 imajını pinliyor, 032
  PG18 kolonu okuyor. **Dürüst etiket: ÇÖZÜLMEDİ + park edildi.** Ayrıntı TASK.md Open Problems.
- **[low, accepted_risk]** `idx_brands_sub_sector_id` planın Task 2 sözleşmesinde yazılı değil.
- **F17 (Eray risk-kabulü):** damga = edited-lineage atfı. **Yeniden açtırma.**
- **[checkpoint-override, checkpoint 5]** Sweep tabanının kökeni — TASK.md Open Problems'ta tam
  gerekçesiyle. Adım 11 final review'a `checkpoint_overrides` olarak taşınır; artık kritik değilse
  temizlenir, hâlâ kritikse final guard'ında ele alınır.
- **Residual (evi Task 16):** geri alma ile ileri 032 arasında ortak kilit yok.
- **Temizlik borçları (evi: yürütme sonrası `/simplify-claude-codex`):** `test_migration_032.py` ve
  `test_infra.py`'de kullanılmayan `pytest` importu · `brands.py`'deki artık ulaşılamaz
  `resolved if resolved else (...)` dalı.
- **Etiketler (evi: `/finish-branch-claude-codex`):** `backup/pre-footer-fix` ve
  `backup/pre-t3-kind-fix` merge/PR kararından sonra silinir.

## Notes For Claude
- **TAVANDA DUR — bu oturumun en pahalı dersi.** Checkpoint 5 tek bir dosyada BEŞ tur döndü ve
  Eray haklı olarak "daha kaç review gerekecek" diye sordu. Dördüncü turda tavan kuralı gereği
  durup rapor edildi, ama "ucuz kapanışı var" diye bir tur daha önerildi; öneri kabul edildi ve
  döngü uzadı. **Ucuz bir düzeltmenin varlığı tavan kuralını geçersiz kılmaz.** Bulgu kümesi tek
  eksende dönmeye başladıysa (her tur bir öncekinden dar varyant) o eksen kapanmıyor demektir —
  DUR, raporla, kararı Eray'a bırak.
- **`Exec-Kind` etiketini yazmadan ÖNCE commit'in path kümesine BAK.** Defter `tests/` altındaki
  HER ŞEYİ test sayar — `capture.py` bile. Yani yalnız `tests/` dokunan bir commit `code` DEĞİL,
  `red-only`'dir. `.sql` de "impl" SAYILMAZ (test + yalnız `.sql` = `migration`). Bu hata iki
  oturum üst üste defteri kırmıştı; bu oturumda önceden kontrol edilerek önlendi.
- **`last_checkpoint_ref` TAM SHA olmalı (40 hane).** Kısa SHA yazınca Codex substratı
  `couldn't find remote ref` ile düşer; çağrı hiç yapılmaz.
- **Pozitif kontrolü atlama.** Her düzeltmede yeni testi düzeltme ÖNCESİ sürüme karşı koştur
  (`git show HEAD:<path>` ile geri al, koş, geri yükle). Hata düzeltmeyen bir test yazdıysan bunu
  commit mesajında AÇIKÇA söyle — sessiz bırakmak sahte kanıt üretir.
- **Sessiz-yeşil avı.** Bu kod tabanında iki yüzey her istisnayı yutup fallback'e düşüyor
  (`generate_captions` anahtar yoksa, `suggest_ideas` her hatada). Böyle bir yüzeyi test ediyorsan
  "çağrı gerçekten yapıldı mı"yı AYRICA doğrula.
- **Codex çağrılarında kapsamı daralt.** Prompt'ta hangi bölümlerin okunacağını AÇIKÇA yaz; uzun
  koşum gerekirse `CSS_CALL_TIMEOUT=1200s` + arka plan. Kapatılmış kümeleri ("bunu açma") ve
  dispositioned maddeleri prompt'a YAZ.
- **Sır tarayıcısı yanlış pozitif veriyor:** `tests/test_data_api_regression.py` substrattan
  eleniyor (içindeki `PASSWORD = "..."` — testin açtığı atılabilir salt-okunur rolün şifresi).
  Codex'e "git nesnelerinden oku" diye söyle, yoksa kanıtı görmez.
- **Kota kapısı `SOFT` derse** sessizce devam etme — Eray'a sor (bu oturumda bir kez oldu, "koş"
  dedi).
- Push henüz hiç yapılmadı ve completion gate'e kadar yapılmayacak.

## Notes For Codex
- Kapsam daraltma prompt'ta veriliyor; sanitize substratta `.env`, `config.py`, `caption_generator.py`,
  `ai.py` gibi dosyalar hariç tutuluyor — **yokluklarını bulgu sayma**, git nesnelerinden oku.
- Sanitize substratta pytest/psql koşamıyorsun; runtime ölçümleri prompt'ta veriliyor, koda karşı
  doğrula.
- Dispositioned `accepted_risk` maddeleri **yeniden açma** (yukarıdaki Risks listesi).
  F17 Eray-tahkimli.
- **Sweep tabanının kökeni (F1 kümesi) KAPALIDIR** — beş tur döndü, Eray kararıyla kapatıldı,
  iki mekanizma (imzalı özet · dışarıdan sağlanan kimlik) gerekçeli olarak reddedildi. Yeniden
  açma; kalıntı final review'da ele alınacak.
