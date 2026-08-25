# Handoff

> ⚠️ YÜRÜTME AÇIK — bu anlatı oturum sonuna aittir; canlı yürütme durumu TASK.md
> "Execution State" + git defterinden okunur, çelişkide onlar esastır.

## Context
- Task: sektor-bilgi-paketi — Plan 1 yürütmesi açık (`/execute-plan-claude-codex` protokolü)
- Last updated: 2026-08-25 (on dördüncü oturum — Task 14 yazıldı, checkpoint 14 kapandı)
- Plan: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (`plan-approved`)
- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Spec girdisi: `docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md` — **karar sorusu
  çıkarsa ÖNCE buraya bak; spec bir özet, kanonik ayrıntı input'ta.**
- Dal: `feat/sektor-bilgi-paketi` (**upstream YOK — hiç push edilmedi**)
- Codex ham review log'u: `/root/.claude/logs/otomaix--ffc87809/2026-08-24-feat-sektor-bilgi-paketi-execute.md`

## Current State
- **Biten:** Task 1–14 (16'nın 14'ü). **Checkpoint 14 KAPANDI. Açık kapı YOK.**
- **Checkpoint:** sayaç ve ref TASK.md "Execution State"ten okunur — burada TEKRARLANMAZ
  (türetilebilir değer iki yerde tutulunca ıraksar). Son checkpoint §8.6 Clean dalında kapandı.
- **Mod:** inline. `execute_mode: subagent-driven` kaydı BİLEREK değiştirilmedi (Task 1-2'yi
  doğru anlatıyor). inline YALNIZ task yazımını kapsar; review/checkpoint kapıları normal koştu.
- **Tavan:** 8; sayaç tavanın ÜSTÜNDE olduğu için her riskli task `CEILING_RISK` dalına düşüyor.
  Eray bu oturumda tavan iznini AÇIKÇA verdi; **o izin BU OTURUMA aitti**, yeni oturumda
  tekrar sorulmalı.
- **Ortam (yeni oturumda TEKRAR KURMA — duruyor):** `apps/social/backend/.venv`.
  Komut daima `.venv/bin/python`; makinede `python` komutu YOK.

## Resume From (sıra)
1. **Task 15** — atama akışı (aday küme, öneri, teyit UI). Aday küme teslimi plan
   §"bağladığı teknik kararlar" 7'de yazılı: öneri çağrısına **kapalı liste prompt'a gömülür**
   + dönüş doğrulaması listede-veya-boş; açılır listeye teslim
   `GET /sectors/sub-sector-candidates` (canlı sorgu, kopya TUTULMAZ).
   **Yeniden tasarlanmaz, oradan okunur.**
2. Sonra Task 16 (arayüz-sözleşme doğrulaması + manuel adımlar).
3. **Task 8'den sonraki HER task'ın son adımı tam sweep'tir:**
   `.venv/bin/python -m pytest tests/prompt_regression/ -q` yeşil olmadan ilerlenmez
   (Task 7 freeze hükmü).
4. **Frontend'e dokunulduysa `npx next build` KOŞULUR.** (Task 15 önyüze dokunacak.)
5. Oturum başında tavan-aşımı için Eray'dan izin iste (yukarıdaki not).

## Verification (bu oturum)

**Koşan komutlar / taze çıktı:**
- `cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → **502 passed**
  (oturum başında 459; Task 14 yazımından sonra 481; checkpoint 14 düzeltmelerinden sonra 502).
- `.venv/bin/python -m pytest tests/prompt_regression/ -q` → **121 passed**
  (byte-exact freeze kapısı; donmuş fixture'lar bayt DEĞİŞMEDİ).
- `.venv/bin/python -m pytest tests/test_notifications.py tests/test_migration_034.py -q`
  → **43 passed** (Codex'in tur 3'te istediği doğrulama; taze koşuldu).
- `cd apps/social/frontend && npx next build` → **başarılı** (önyüz bandı eklendi).
- `ec_ledger_view --post-window` → **rc=0**, T14 ve fix commit'leri etiketli.
- `command-blocks-maint.sh verify` → **PASS**.
- Uygulama ayağa kalkıyor: `app.main` import edildi, iki yeni rota kayıtlı ve
  `/brands/{brand_id}/package-status` `/brands/{brand_id}`'den ÖNCE geliyor (ölçüldü).

**Pozitif kontroller (kapıların gerçekten ölçtüğünü kanıtlayanlar — hepsi taze):**
- Task 14 yazımında **7 mutasyon**, hepsi ilgili testi DÜŞÜRDÜ: claim'deki sayaç artışı (F19) ·
  süpürücünün kira koşulu (F20) · finalize'ın jeton kapısı · `ON CONFLICT` dedupe · K-56 tek
  kapı bağlaması · bildirim sarmalayıcısının `try`'ı · sahiplik kapısı.
- Checkpoint 14 düzeltmelerinin **hepsi önce KIRMIZI görüldü** (F1/F2 beş test, F3 iki test,
  F4 dört + iki bozulma vakası) ve ancak düzeltmeden sonra yeşile döndü.
- `UNLOGGED` sahte tablosunun migration'dan rc=0 ile GEÇTİĞİ ayrıca elle ölçüldü — bulgu
  Codex tarafından "çıkarım" diye işaretlenmişti, kabul edilmeden önce doğrulandı.

**ÇÜRÜTÜLEN VARSAYIM (kayda değer):** "indeks düşerse migration DURur" varsayımı YANLIŞTI.
`CREATE INDEX IF NOT EXISTS` eksik indeksi GERÇEKTEN geri getirir (kısıtların aksine — çünkü
`CREATE TABLE IF NOT EXISTS` bütün ifadeyi atlar). Kapının sözü daraltıldı ve iki ayrı testle
pinlendi: eksik indeks ONARILIR, yanlış tanımlı indeks REDDEDİLİR.

**Codex:** checkpoint 14 → **3 tur** (tur 1: 4 high · tur 2: 3'ü kapalı + F4 yeniden açıldı ·
tur 3: approve, bulgu yok). Tur 1 ilk çağrısı 480s'de timeout'a düştü; canlılık yoklaması
companion'ın sağlam olduğunu gösterdi ve protokolün öngördüğü tek tekrar 1200s ile koştu.

**DENENMEYEN / kapsanmayan:**
- **Canlı n8n importu ve gerçek Telegram teslimi DENENMEDİ** — Task 16 manuel adımı. Workflow
  JSON'ının yapısı ve sır içermediği ölçüldü; canlıda çalıştığı ölçülmedi.
- `N8N_ADMIN_EVENT_SECRET` canlıya KURULMADI; kurulmadan bildirim gönderimi fail-closed durur
  (satır `pending`de birikir, kaybolmaz).
- Canlıya hiçbir migration uygulanmadı (032 · 033 · 034) — manuel adım, Task 16.
- Gerçek arayüzde tek bir üretim denenmedi; gerçek bir sektör paketi hiç yazılmadı.
- `IS JSON OBJECT` yüklemi ve `conenforced` yalnız PostgreSQL 18.3'te ölçüldü; PG16'da
  varlıkları BELGEYE dayanıyor.
- Kısa video stage-2 gerçek bir fal.ai çağrısıyla koşulmadı (dış dünya kesildi).
- **Eşzamanlılık testi `SKIP LOCKED`'in bloklamama özelliğini KANITLAMAZ** — ipucu kaldırılınca
  test yine geçiyor (READ COMMITTED yeniden değerlendirmesi doğruluğu koruyor). Ölçülen
  doğruluk (tek teslim), ölçülmeyen throughput.
- Hızlı yolun havuz DAVRANIŞI tek bağlantılık gerçek havuzla ölçüldü; ÇOK bağlantılı bir
  patlama senaryosu (20 bağlantı, N eşzamanlı olay) ölçülmedi.

## Risks

**Bilinçli tasarım kararları (bulgu SAYILMAZ):**
- Sahne zenginleştirmesinde yinelenme kontrolü YOK; hareket/sahne geri düşüşü RASTGELE seçer.
- Damga yazımı başarısızsa `generation_id` null döner; üretim düşürülmez.
- Model çağrısı yapan yolda havuz BAĞLAM olarak verilir (spec §4.3).
- `stamp_missing` yalnız makbuz BEKLENEN akışlarda yazılır (`RECEIPTLESS_CONTENT_TYPES`).
- `insert_draft` yasak marka adlarını TÜM markalardan türetir; yanlış-pozitif bilinçlidir.
- **Bildirim teslimi EN-AZ-BİR-KEZ'dir**; yinelenen yönetici uyarısı gürültüdür, veri kaybı
  değil. n8n tarafındaki tekilleştirme static data'ya dayanır ve o BELGELERDE DENEYSEL'dir —
  yani BEST-EFFORT, tek-teslim garantisi DEĞİL.
- **Hızlı yol genel bir "commit sonrası" kancası DEĞİLDİR:** açık transaction içinde yazan
  çağıranlar için hiç koşmaz; teslimi kurtarma yolu (n8n schedule) üstlenir. Teslim garantisi
  hızlı yola DAYANMAZ.
- Kira süresi (300 sn) ÖLÇÜLMEMİŞ bir tahmindir ve hiçbir kapının eşiği DEĞİLDİR.

**Açık kalemler — hepsinin evi VAR:**
- **[Eray tetikledi]** Süpürücü "başarısız" derken webhook aynı satırı "hazır" yapabiliyor;
  arka uçta `failed` terminal DEĞİL ve 10 dakikalık eşiğin ölçülmüş dayanağı YOK.
  Ev: `docs/active/CURRENT.md` → `stale-sweeper-vs-late-webhook-terminality`.
  **Tetik: sektör bilgi paketi işi TAMAMEN bittikten sonra**, fal.ai model değişikliğiyle.
- **[çözülmedi + park edildi, TETİKLİ]** `sector_packages.sector_id` yazımdan sonra DEĞİŞMEZ
  değil. Ev: `CURRENT.md` → `sector-package-sector-id-immutability`.
- **[YENİ — tetikli kayıt]** Migration **032 ve 033**'ün garanti blokları kolon imzasını ve
  tablo katalog imzasını doğrulaMIYOR; 034'te kapatılan sınıfın aynısı. Bu partinin ürünü
  DEĞİL (önceden var olan borç), o yüzden sessizce düzeltilmedi.
  Ev: `CURRENT.md` → `migration-guarantee-block-signature-gap`.
- **[Manuel adım — evi Task 16]** `N8N_ADMIN_EVENT_SECRET` canlıya kurulmalı · n8n'de
  "Otomaix Admin Event Key" header-auth kimlik bilgisi yaratılmalı ve workflow'daki
  `REPLACE_WITH_ADMIN_EVENT_KEY_CREDENTIAL` yer tutucusu gerçek kimlikle değiştirilmeli ·
  `OTOMAIX_ADMIN_TELEGRAM_BOT_TOKEN` + `OTOMAIX_ADMIN_TELEGRAM_CHAT_ID` env'leri kurulmalı ·
  workflow import edilip TEK Telegram teslimi smoke'u koşulmalı.
- **[Manuel adım — evi Task 16]** `apps/social/backend/.env.example`'a `N8N_ADMIN_EVENT_SECRET`
  satırı ELLE eklenmeli: sır-dosyası yazma kapısı (global `permissions.deny`) bu dosyayı
  koruyor, agent yazamaz. Backend `CLAUDE.md`'ye işlendi.
- **[accepted_risk, checkpoint 12]** Kütüphane yoklaması terminal başarısız satırları sınırsız
  yokluyor. ÖLÇÜLDÜ: bu partinin ürünü DEĞİL.
- **[doğrulama boşluğu — evi: kuyumculuk pilotu]** Uçtan uca gerçek akış ölçümü.
- **[Plan 2 teslim kalemi — evi: plan "Plan 2'ye teslim edilen arayüzler", Task 16 doğrular]**
  Brief/sentez hattı `video_kodlar` için İKİ HAVUZ üretmeli (`hareket`, `sahne`).
- **[Plan 2 teslim kalemi]** `recovered` modu + geri-dönüş mesajı Plan 2'dedir (F23 kapanışı).
  `package-status` ucunun durum modeli kapalı enum DEĞİL, düz metin — yeni mod şemayı kırmaz.
- **[Residual — evi Task 16]** 033 ve **034** için geri alma script'i YOK (plan istemedi).
- **[Temizlik borçları — evi `/simplify-claude-codex`]** İki dosyada kullanılmayan `pytest`
  importu · `brands.py`'de kullanılmayan `BrandOut`.
- **[Etiketler — evi `/finish-branch-claude-codex`]** `backup/pre-footer-fix`,
  `backup/pre-t3-kind-fix` merge/PR kararından sonra silinir.

**Devralınan, değişmeyen kalemler:**
- `accepted_risk` (checkpoint 9): CTA içinde serbest köşeli ayraç yok · `brand_kit` anahtarı
  silinemez.
- Belgeli sınırlar (testle pinli, borç DEĞİL): ayraçsız kanal işareti yakalanmaz · tam
  genişlikli ayraçlı etiket tanınır ama basımdan çıkarılamaz (kozmetik).
- `accepted_risk` (test altyapısı): eşzamanlı iki pytest oturumu `otomaix_test`'i düşürür ·
  migration keşfi tekrarlı numarayı reddetmiyor · `db` fixture geri sarma testi yok ·
  `sector_research_artifacts` TRUNCATE regresyonu yok · `idx_brands_sub_sector_id` plan
  sözleşmesinde yazılı değil (low).
- **[Eray risk kabulü]** On-prem PG16 ↔ 032'nin PG18 kolonu: **çözülmedi + park edildi.**
- **F17 (Eray):** damga = edited-lineage atfı. **Yeniden açtırma.**
- **[checkpoint-override, checkpoint 5]** Sweep tabanının kökeni — kapalı.

## Notes For Claude

- **ARAÇ TUZAĞI — tekrarlama.** `run_codex_scan` `$COMPANION` ve `$PROMPT` değişkenlerini
  KULLANIR ama TANIMLAMAZ; ikisini de çağıran kurar (CODEX-CALL-PROTOCOL preflight +
  `PROMPT=$(cat -- "$CODEX_PROMPT_FILE")`). Kurulmazsa `node ""` koşar: arka planda sessizce
  exit 0 + boş çıktı, ön planda ASILI kalır. Teşhis kısayolu: stderr'de `[codex]` işareti
  YOKSA çağrı kurulmamıştır — kotaya, substrata, timeout'a bakma.
- **Codex 480s'de timeout verirse reflekssel degradation'a düşme:** önce 120s canlılık
  yoklaması ("reply OK, do not read files"), companion sağlamsa `CSS_CALL_TIMEOUT=1200s` ile
  BİR tekrar. Bu oturumda tam olarak bu oldu ve tekrar başarılı koştu.
- **Codex'in "inferred / could not run" etiketli bulgusunu sonda koşmadan kabul etme.**
  Bu oturumda F4'ün yeniden açılışı böyle geldi; ölçüldü ve DOĞRU çıktı — ama ölçüm kararı
  değiştirebilirdi ve o ölçüm yapılmadan fix yazılsaydı gerekçe uydurma olurdu.
- **Aynı sınıf iki tur üst üste çıkarsa yamamayı bırak.** Checkpoint 14'te tur 1 ve tur 2
  aynı sınıfa çarptı ("doğrulayıcı tanımın tamamını görmüyor"); tur 2 fix'i varyantı değil
  sınıfı kapattı ve kapanış elle seçilmiş örnekle değil MATRİSLE kanıtlandı. Tur 3 prompt'una
  "bu sınıfın dar bir varyantı daha çıkarsa yama kalemi olarak değil, sayarak-kapanmaz
  teşhisi olarak raporla" kısıtı yazıldı. Bu kalıp işe yaradı — tekrarla.
- **Kendi düzeltmenin yan etkisini ölç.** Checkpoint 13'te F4 düzeltmenin KENDİ ürünüydü;
  checkpoint 14'te F3 fix'i iki dosyada sınıf-süpürmesi gerektirdi (hızlı yol + iç uç nokta).
  Tek yeri düzeltip geçmek, sonraki turun garantili kardeş bulgusudur.
