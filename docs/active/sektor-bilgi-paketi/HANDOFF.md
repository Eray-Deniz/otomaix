# Handoff

> ⚠️ YÜRÜTME AÇIK — bu anlatı oturum sonuna aittir; canlı yürütme durumu TASK.md
> "Execution State" + git defterinden okunur, çelişkide onlar esastır.

## Context
- Task: sektor-bilgi-paketi — Plan 1 yürütmesi açık (`/execute-plan-claude-codex` protokolü)
- Last updated: 2026-08-25 (on üçüncü oturum — Task 13 yazıldı, checkpoint 13 kapandı)
- Plan: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (`plan-approved`)
- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Spec girdisi: `docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md` — **karar sorusu
  çıkarsa ÖNCE buraya bak; spec bir özet, kanonik ayrıntı input'ta.**
- Dal: `feat/sektor-bilgi-paketi` (**upstream YOK — hiç push edilmedi**)
- Codex ham review log'u: `/root/.claude/logs/otomaix--ffc87809/2026-08-24-feat-sektor-bilgi-paketi-execute.md`

## Current State
- **Biten:** Task 1–13 (16'nın 13'ü). **Checkpoint 13 KAPANDI. Açık kapı YOK.**
- **Checkpoint:** `cp_count: 13`, `last_checkpoint_ref` = `926e7c6`. §8.6 Clean dalı ateşlendi
  (tur 3 `approve`, bulgu yok); ref ve sayaç birlikte ilerledi.
- **Mod:** inline. `execute_mode: subagent-driven` kaydı BİLEREK değiştirilmedi (Task 1-2'yi
  doğru anlatıyor). inline YALNIZ task yazımını kapsar; review/checkpoint kapıları normal koştu.
- **Tavan:** 8; `cp_count` 13 olduğu için her riskli task `CEILING_RISK` dalına düşüyor.
  Eray bu oturumda tavan iznini AÇIKÇA verdi; **o izin BU OTURUMA aitti**, yeni oturumda
  tekrar sorulmalı.
- **Ortam (yeni oturumda TEKRAR KURMA — duruyor):** `apps/social/backend/.venv`.
  Komut daima `.venv/bin/python`; makinede `python` komutu YOK.

## Resume From (sıra)
1. **Task 14** — bildirim mekanizması (K-45 devre-dışı ayağı + K-56 olay-bazlı + K-44 işaret).
   Kapsam bu planın en genişi: `migration 034_admin_events.sql` · `services/notifications.py`
   (transactional outbox) · `shared/n8n-workflows/sector-package-admin-events.json` ·
   `GET /brands/{brand_id}/package-status` · `POST /internal/admin-events/dispatch-pending`
   (X-Internal-Key; mevcut `/internal/posts/fail-stale` deseninin eşi) · önyüz panel bandı.
   Deneme muhasebesi F19 ve süpürücü uygunluk kuralı F20 plan §"bağladığı teknik kararlar" 6'da
   yazılı — **kira/claim semantiği oradan okunmalı, yeniden tasarlanmamalı.**
2. Sonra Task 15 → 16.
3. **Task 8'den sonraki HER task'ın son adımı tam sweep'tir:**
   `.venv/bin/python -m pytest tests/prompt_regression/ -q` yeşil olmadan ilerlenmez
   (Task 7 freeze hükmü).
4. **Frontend'e dokunulduysa `npx next build` KOŞULUR.** (Bu oturumda önyüze DOKUNULMADI,
   o yüzden derleme koşulmadı — Task 14'te koşulacak.)
5. Oturum başında tavan-aşımı için Eray'dan izin iste (yukarıdaki not).

## Verification (bu oturum)

**Koşan komutlar / taze çıktı:**
- `cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → **459 passed**
  (oturum başında 405; Task 13 yazımından sonra 436; F1-F3 düzeltmesinden sonra 457).
- `.venv/bin/python -m pytest tests/prompt_regression/ tests/test_migration_033.py -q`
  → **131 passed** (byte-exact freeze kapısı; donmuş fixture'lar bayt DEĞİŞMEDİ).
- `ec_ledger_view --post-window` → **rc=0**, T1–T13 tamamı etiketli, etiketsiz commit yok.
- `command-blocks-maint.sh verify` → **PASS** (T3/T4/T5 + S4 1-way).
- `npx next build` → **KOŞULMADI** (önyüze dokunulmadı; kapı tetiklenmedi).

**Pozitif kontroller (kapıların gerçekten ölçtüğünü kanıtlayanlar — 8 tane, hepsi taze):**
- Devir-teslim ölçüsü `active` → `archived`'a geri alınınca deaktivasyon-sonrası aktivasyon
  testi DÜŞÜYOR.
- `event_id is None` kapısı kaldırılınca sessiz-None dalı DÜŞÜYOR.
- Transaction sarmalayıcılarının **İKİSİ de** kaldırılınca atomiklik testi düşüyor; **biri**
  kalırsa geçiyor — iki katman da tek başına yeterli (ölçüldü, varsayılmadı).
- Kanıt tip zorlaması kaldırılınca bypass testlerinin 6'sı DÜŞÜYOR.
- Karşılaştır-ve-yaz koşulsuza dönünce eşzamanlı-aynı-taslak testi DÜŞÜYOR.
- Sektör kilidi kaldırılınca eşzamanlı-farklı-taslak testi DÜŞÜYOR (kaybeden ham kısıt
  ihlaliyle ölüyor).
- Tam eşleşme eski asimetrik kurala dönünce uydurma-kaynak-sürüm testi DÜŞÜYOR.
- Sektör bağlama kaldırılınca iki yeniden-atama yarış testi de DÜŞÜYOR.

**Codex:** checkpoint 13 → **3 tur** (tur 1: 2 high + 1 medium · tur 2: üçü kapalı + 1 YENİ
high · tur 3: approve, bulgu yok). Bütün bulgular bağımsız sondajla doğrulandı; hiçbiri
sondaj koşmadan kabul veya reddedilmedi.

**DENENMEYEN / kapsanmayan:**
- Gerçek arayüzde tek bir üretim denenmedi (bu oturumda önyüze hiç dokunulmadı).
- Canlıya hiçbir migration uygulanmadı (032 ve 033) — manuel adım, Task 16.
- Gerçek bir sektör paketi hiç yazılmadı; tüm ölçümler fixture üstünde.
- `IS JSON OBJECT` yüklemi yalnız PostgreSQL 18.3'te ölçüldü; PG16'da varlığı BELGEYE dayanıyor.
- Kısa video stage-2 gerçek bir fal.ai çağrısıyla koşulmadı (dış dünya kesildi).
- Yaşam döngüsü fonksiyonlarının HTTP ucu YOK (plan açmıyor) — yalnız servis düzeyi ölçüldü.
- Rollback ve deaktivasyon için eşzamanlı-farklı-taslak (serileştirilebilirlik) testi YAZILMADI;
  ölçülen aktivasyon dalı, kilit yardımcısı ve sırası üçünde de AYNI. Dürüst etiket: kilit
  sözleşmesi ölçüldü, rollback/deaktivasyon dalları o ölçüme MİRAS yoluyla dayanıyor.

## Risks

**Bilinçli tasarım kararları (bulgu SAYILMAZ):**
- Sahne zenginleştirmesinde yinelenme kontrolü YOK; hareket/sahne geri düşüşü RASTGELE seçer.
- Damga yazımı başarısızsa `generation_id` null döner; üretim düşürülmez.
- Model çağrısı yapan yolda havuz BAĞLAM olarak verilir (spec §4.3).
- `stamp_missing` yalnız makbuz BEKLENEN akışlarda yazılır (`RECEIPTLESS_CONTENT_TYPES`).
- `insert_draft` yasak marka adlarını TÜM markalardan türetir; yanlış-pozitif bilinçlidir
  (yazım kapısında yanlış-pozitif, yanlış-negatiften iyidir — doğrulayıcının kendi hükmü).

**Açık kalemler — hepsinin evi VAR:**
- **[Eray tetikledi]** Süpürücü "başarısız" derken webhook aynı satırı "hazır" yapabiliyor;
  arka uçta `failed` terminal DEĞİL ve **10 dakikalık eşiğin ölçülmüş dayanağı YOK**.
  Ev: `docs/active/CURRENT.md` → `stale-sweeper-vs-late-webhook-terminality`.
  **Tetik: sektör bilgi paketi işi TAMAMEN bittikten sonra**, fal.ai model değişikliğiyle
  birlikte. Kapanışta (`/finish-branch-claude-codex`) Eray'a hatırlatılacak.
- **[çözülmedi + park edildi, evi Task 16 DEĞİL — yeni]** `sector_packages.sector_id`
  yazımdan sonra DEĞİŞMEZ değil. Yaşam döngüsü artık uyuşmazlıkta fail-closed durur
  (checkpoint 13 F4), ama pencerenin kendisi kapanmadı — kapanması bir migration ister
  (kolonu değişmez kılan tetikleyici/kısıt) ve Task 13'ün dosya kapsamında değildi.
  Bugün hiçbir üretim yolu bu kolonu güncellemiyor (depo genelinde arandı, yazıcı yok).
  **Yeniden açılma koşulu:** sektör yeniden-atama özelliği istenirse ya da Plan 2 bir
  yazıcı eklerse — o zaman migration ZORUNLU olur. Şimdilik aktif borç değil, tetikli kayıt.
- **[accepted_risk, checkpoint 12]** Kütüphane yoklaması terminal başarısız satırları
  sınırsız yokluyor. **ÖLÇÜLDÜ: bu partinin ürünü DEĞİL** (`0c19d83` sürümünde de aynı yük
  vardı). Gerçek çözüm yukarıdaki park edilmiş ürün kararının içindedir.
- **[doğrulama boşluğu — evi: kuyumculuk pilotu]** Uçtan uca gerçek akış ölçümü.
- **[Plan 2 teslim kalemi — evi: plan "Plan 2'ye teslim edilen arayüzler", Task 16 doğrular]**
  Brief/sentez hattı `video_kodlar` için İKİ HAVUZ üretmeli (`hareket`, `sahne`). Asgari
  eleman sayısı kapı YAPILMADI (İlke 9).
- **[Residual — evi Task 16]** 033 için geri alma script'i YOK (plan istemedi).
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

- **ARAÇ TUZAĞI — bu oturumda 7 Codex çağrısı yaktı, tekrarlama.** `run_codex_scan`
  `$COMPANION` ve `$PROMPT` değişkenlerini KULLANIR ama TANIMLAMAZ; ikisini de çağıran
  kurar (CODEX-CALL-PROTOCOL preflight + `PROMPT=$(cat -- "$CODEX_PROMPT_FILE")`).
  Kurulmazsa `node ""` koşar: **arka planda stdin hemen kapandığı için sessizce exit 0 +
  boş çıktı (rc=5), ön planda stdin açık kaldığı için ASILI kalır (rc=124).** Yani semptom
  "Codex bozuk" gibi görünür, oysa çağrı hiç yapılmamıştır. Teşhis kısayolu: stderr'de
  `[codex]` işareti YOKSA çağrı kurulmamıştır — kotaya, substrata, timeout'a bakma.
- **Düzeltmenin kendi yan etkisini ÖLÇ.** Bu oturumun en pahalı dersi: F2'yi kapatmak için
  serileştirme çapasını sektör satırına taşımak YENİ bir high açtı (F4) — paket kilitlenmeden
  önce okunmak zorunda olduğu için sektör penceresi doğdu. Tur 2 onu yakaladı.
- **Ölçülmemiş makine bırakma.** Sektör kilidi ilk yazımda hiçbir testin ölçmediği bir
  katmandı (pozitif kontrol yeşil kaldı = kilit gereksiz görünüyordu). Ya ölç ya çıkar:
  ölçülebilir farkı (kilitsizken kaybeden ham kısıt ihlaliyle ölür) teste bağlandı.
- **Kendi testinin sahte yeşilini ara.** F4 deaktivasyon yarış testi ilk yazımda hedefi
  yanlış durumda kuruyordu; fonksiyon zaten başka gerekçeyle düşüyor, sektör penceresi hiç
  ölçülmüyordu. Test "geçti" diyordu. Kırmızının DOĞRU SEBEPLE geldiğini doğrula.
- **Bir partinin KENDİ açtığı medium'u park etme.** F3 medium'du ve politika onu advisory
  sayar; ama sıra bağımlılığını bu parti getirmişti, düzeltildi.
- **`isinstance` bool için YETMEZ** — `bool` bir `int` alt sınıfıdır; tip kapılarında
  `type(x) is bool` gerekir. Aynı sebeple `False == 0` ve `True == 1` sayaç kapılarını açar.
- **Transaction içinde `now()` sabittir.** Tek dış transaction'da koşan testte bütün
  `created_at` damgaları aynıdır; olay sıralaması iddiası orada hiçbir şey ölçmez. Delta
  (kimlik farkı) al.
- **`Exec-Kind` yazmadan ÖNCE commit'in path kümesine BAK.** Trailer bloğuna boş satır koyma.
- **Codex prompt'u SHELL heredoc'uyla YAZILMAZ** — SETUP fence + Write tool ile
  `$CODEX_LOG` türevli yola.
- **Kota `SOFT` derse sebebi oku.** Bu oturumda hep "ölçüm bayat (>900s)"; okuma hiç
  tazelenmedi (%10'da donuk). Tek-çağrı dalı "uyar + devam".

## Notes For Codex

- Kapsam daraltma prompt'ta veriliyor; sanitize substratta üretim dosyaları hariç tutuluyor —
  **yokluklarını bulgu sayma**, git nesnelerinden oku.
- Sanitize substratta pytest/npx koşamıyorsun; runtime ölçümleri prompt'ta veriliyor.
- **Dispositioned maddeleri yeniden açma** (yukarıdaki Risks listesi). F17 Eray-tahkimli.
  Sweep tabanının kökeni KAPALIDIR.
- **Task 13'ün kapalı sınırlarını yeniden açma:** `sector_id` değişmezliği bir MIGRATION işidir
  ve kapsam dışı olduğu belgelendi (yaşam döngüsü uyuşmazlıkta fail-closed durur) · yaşam
  döngüsünün HTTP ucu YOK (plan açmıyor) · `insert_draft` yasak adları tüm markalardan türetir
  ve yanlış-pozitif bilinçlidir · geçişten sonra `from_version=None` ile yazılan olay meşru ilk
  aktivasyondan tablo durumuyla ayırt EDİLEMEZ (belgeli sınır).
- **Task 9/10/11/12'nin kapalı sınırlarını yeniden açma:** ayraçsız işaret yakalanmaz ·
  CTA içinde ayraç yalnız bayraktır · kit anahtarı silinemez · sahne zenginleştirmesinde
  yinelenme kontrolü YOK · hareket/sahne geri düşüşü RASTGELE · damga yazımı başarısızsa
  `generation_id` null.
- **Süpürücü↔webhook terminal-durum tutarsızlığı KAPSAM DIŞI** ve Eray'ın parkında.
- **033 için geri alma script'i YOK** — plan istemedi, evi Task 16. Eksik adım sayma.
- Önyüz kapıları **yapısal** olduklarını docstring'lerinde SÖYLÜYOR.
- **K-06 açık** · **K-15(a)** alan-düzeyi atlama dalı bilinçle YOK · **K-94** açık
  (`expected_active_version` opsiyonel; mekanizma kurulu, kural bekletiliyor).
