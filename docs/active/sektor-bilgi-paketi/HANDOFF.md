# Handoff

> ⚠️ YÜRÜTME AÇIK — bu anlatı oturum sonuna aittir; canlı yürütme durumu TASK.md
> "Execution State" + git defterinden okunur, çelişkide onlar esastır.

## Context
- Task: sektor-bilgi-paketi — Plan 1 yürütmesi açık (`/execute-plan-claude-codex` protokolü)
- Last updated: 2026-08-25 (on ikinci oturum — checkpoint 11 kapandı, Task 12 yazıldı, checkpoint 12 kapandı)
- Plan: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (`plan-approved`)
- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Spec girdisi: `docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md` — **karar sorusu
  çıkarsa ÖNCE buraya bak; spec bir özet, kanonik ayrıntı input'ta.**
- Dal: `feat/sektor-bilgi-paketi` (**upstream YOK — hiç push edilmedi**)
- Codex ham review log'u: `/root/.claude/logs/otomaix--ffc87809/2026-08-24-feat-sektor-bilgi-paketi-execute.md`

## Current State
- **Biten:** Task 1–12 (16'nın 12'si). **Checkpoint 11 ve 12 KAPANDI. Açık kapı YOK.**
- **Checkpoint:** `cp_count: 12`, `last_checkpoint_ref` = `532825e`. §8.6 Clean (cp 11) ve
  Accepted-risk (cp 12) dalları ateşlendi; iki alan da tek commit'te ilerledi.
- **Mod:** inline. `execute_mode: subagent-driven` kaydı BİLEREK değiştirilmedi (Task 1-2'yi
  doğru anlatıyor). inline YALNIZ task yazımını kapsar; review/checkpoint kapıları normal koştu.
- **Tavan:** 8; `cp_count` 12 olduğu için her riskli task `CEILING_RISK` dalına düşüyor.
  Eray bu oturumda tur sayısı kısıtını AÇIKÇA kaldırdı; **o izin BU OTURUMA aitti**, yeni
  oturumda tekrar sorulmalı.
- **Ortam (yeni oturumda TEKRAR KURMA — duruyor):** `apps/social/backend/.venv`.
  Komut daima `.venv/bin/python`; makinede `python` komutu YOK.
- **Global araç değişikliği (bu oturum, Eray onaylı):** `_ec_is_executable_path` artık
  `.tsx`/`.jsx`'i kod sayıyor (`~/.claude` reposunda `cb8c1c1`). **Davranış sonucu: yalnız
  önyüze dokunan diff artık RISKY sayılır ve checkpoint tetikler** (ölçüldü). Öncesinde o
  dosyalar sınıflandırmaya HİÇ girmiyordu ve türetilmiş defterde görünmüyordu; Adım 11'in
  mekanik kapısı bu yüzden kırmızıydı. Düzeltme sonrası ölçüm: sweep rc=0, MECH-FAIL 0.

## Resume From (sıra)
1. **Task 13** — yaşam döngüsü servis fonksiyonları (aktivasyon / rollback / deaktivasyon).
   Task 12'nin `log_package_event`'i HAZIR ve yaşam-döngüsü olaylarının şekil sözleşmesi (F22)
   test edilmiş durumda; Task 13 onu `_apply_status_transition` ile **AYNI transaction'da**
   çağıracak (F24).
2. Sonra Task 14 → 16.
3. **Task 8'den sonraki HER task'ın son adımı tam sweep'tir:**
   `.venv/bin/python -m pytest tests/prompt_regression/ -q` yeşil olmadan ilerlenmez
   (Task 7 freeze hükmü).
4. **Frontend'e dokunulduysa `npx next build` KOŞULUR.**
5. Oturum başında tavan-aşımı için Eray'dan izin iste (yukarıdaki not).

## Verification (bu oturum)

**Koşan komutlar / taze çıktı:**
- `cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → **405 passed**
  (oturum başında 296; checkpoint 11 kapanışında 345).
- `.venv/bin/python -m pytest tests/prompt_regression/ tests/test_migration_033.py -q`
  → **131 passed** (byte-exact freeze kapısı + yeni migration kapısı; donmuş fixture'lar
  bayt DEĞİŞMEDİ).
- `cd apps/social/frontend && npx next build` → **exit=0** (lockfile-patch TypeError uyarısı
  ortam gürültüsü, derleme hatası değil — ölçüldü).
- `ec_ledger_view` → **rc=0, MECH-FAIL 0**; `ec_mechanical_sweep` → **çıktı boş, rc=0**.
- `command-blocks-maint.sh verify` → **PASS**; T5 pin 7 komutta da hizalı.

**Pozitif kontroller (kapıların gerçekten ölçtüğünü kanıtlayanlar):**
- 033 doğrulayıcısı: **dokuz bozulma vakasının dokuzu da** migration'ı DURDURUYOR
  (CHECK düşük · CHECK genişletilmiş · FK CASCADE'siz · FK kapalı · iki indeks yanlış tanımlı ·
  aynı-adda UNIQUE · ters sıralama · predicate düşük) ve temiz şemada SESSİZ.
- M1 kapısı: `AND status = 'generating'` kaldırılınca test DÜŞÜYOR, geri konunca geçiyor.
- Her checkpoint bulgusu, düzeltmeden ÖNCEKİ sürüme karşı düşen bir testle kanıtlandı.

**Codex:** checkpoint 11 → 6 tur (tur 6 approve, bulgu yok). Checkpoint 12 → **5 tur**
(tur 3'ten itibaren approve). Bu oturumda **7 tur** koşuldu. Bütün bulgular bağımsız sondajla
doğrulandı; hiçbiri sondaj koşmadan kabul veya reddedilmedi.

**DENENMEYEN / kapsanmayan (bu oturumda değişmedi):**
- Gerçek arayüzde tek bir üretim denenmedi. Damga taşımasının ve hareket/sahne seçiminin
  uçtan uca gerçek akışta taşındığı ÖLÇÜLMEDİ; kanıt birim + yapısal testlerdir.
  Önyüz kapıları **yapısal**, davranışsal DEĞİL (test docstring'lerinde böyle etiketli).
- Canlıya hiçbir migration uygulanmadı (032 ve 033) — manuel adım, Task 16.
- Gerçek bir sektör paketi hiç yazılmadı; tüm ölçümler fixture üstünde.
- `IS JSON OBJECT` yüklemi yalnız PostgreSQL 18.3'te ölçüldü; PG16'da varlığı BELGEYE dayanıyor.
- Kısa video stage-2 gerçek bir fal.ai çağrısıyla koşulmadı (dış dünya kesildi).
- Eşzamanlı süpürücü↔stage-1 yarışı GERÇEK iki bağlantıyla değil, tek bağlantıda araya-girme
  ile ölçüldü.

## Risks

**Bilinçli tasarım kararları (bulgu SAYILMAZ):**
- Sahne zenginleştirmesinde yinelenme kontrolü YOK — tekrar kabul edilen bedel, sessiz
  eksiklik değil. Yeniden açılma: tekrarın görsel kaliteyi bozduğu gerçek üretimde ölçülürse.
- Hareket ve sahne geri düşüşü havuzdan RASTGELE seçer.
- Damga yazımı başarısızsa `generation_id` null döner; üretim düşürülmez.
- Model çağrısı yapan yolda havuz BAĞLAM olarak verilir (spec §4.3); modelin dağarcığı
  kullanıp kullanmadığı fail-closed bir soru DEĞİLDİR.
- `stamp_missing` yalnız makbuz BEKLENEN akışlarda yazılır (`RECEIPTLESS_CONTENT_TYPES`);
  bilinmeyen içerik türü BEKLENİR tarafına düşer.

**Açık kalemler — hepsinin evi VAR:**
- **[Eray tetikledi]** Süpürücü "başarısız" derken webhook aynı satırı "hazır" yapabiliyor;
  arka uçta `failed` terminal DEĞİL ve **10 dakikalık eşiğin ölçülmüş dayanağı YOK** (vault
  kararı gerekçeyi "webhook kaybı güvenlik ağı" diyor, model süresine dayanmıyor; kayıt
  `verification-status: unverified`). Bu oturumda YALNIZ arayüz tutarlı hâle getirildi.
  Ev: `docs/active/CURRENT.md` → `stale-sweeper-vs-late-webhook-terminality`.
  **Tetik: sektör bilgi paketi işi TAMAMEN bittikten sonra**, fal.ai model değişikliğiyle
  birlikte. Kapanışta (`/finish-branch-claude-codex`) Eray'a hatırlatılacak.
- **[accepted_risk, checkpoint 12]** Kütüphane yoklaması terminal başarısız satırları
  sınırsız yokluyor. **ÖLÇÜLDÜ: bu partinin ürünü DEĞİL** — `0c19d83` sürümünde de aynı yük
  vardı (eski kod durumu hiç birleştirmediği için satır yerel olarak `generating` kalıyordu,
  üstelik kart yanlış gösteriyordu). Gerçek çözüm arka uçtan türetilmiş bir uzlaştırma
  sinyalidir → yukarıdaki açık kalemin içinde.
- **[doğrulama boşluğu — evi: kuyumculuk pilotu]** Uçtan uca gerçek akış ölçümü. Canlıda
  paket YOK (ölçüldü), o yüzden ancak pilotta ölçülebilir. Pilot planlı bir fazdır, evsiz
  park DEĞİL.
- **[Plan 2 teslim kalemi — evi: plan "Plan 2'ye teslim edilen arayüzler", Task 16 doğrular]**
  Brief/sentez hattı `video_kodlar` için İKİ HAVUZ üretmeli (`hareket`, `sahne`). Asgari
  eleman sayısı kapı YAPILMADI (İlke 9).
- **[Residual — evi Task 16]** 033 için geri alma script'i YOK (plan istemedi; olay tablosu
  denetim izidir ve 032'nin veri-varken-REDDET modeliyle aynı soruyu doğurur). Ayrıca geri
  alma ile ileri 032 arasında ortak kilit yok.
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

- **Turlar daralarak geliyorsa yamalamayı BIRAK, çıkış uzayını SAY.** Bu oturumun iki büyük
  dersi de bu: F3 (checkpoint 11) beş turda beş kök nedenle geldi, kapanış ancak dal
  uzayının tamamını üreten bir matrisle geldi. Checkpoint 12'de aynı desen iki kez tekrarladı
  — ilk düzeltmelerim varyantı kapatıp sınıfı açık bıraktı.
- **Eksik imzayı ALAN EKLEYEREK kapatma, TAM ölçüye bağla.** 033 indeks kapısı elle kurulmuş
  alanlardan oluşuyordu ve `indisunique` unutulmuştu; çözüm `pg_get_indexdef` (kanonik tanımın
  tamamı) oldu. Elle kurulan her imzada unutulan alan sessiz bir atlatma kapısıdır.
- **Cevabı yalnız kaynağın bildiği soruyu yüklemle çözme.** Kütüphane yoklamasında "bu satır
  daha değişecek mi" sorusu istemcide CEVAPLANAMAZ; üç tur üç varyant üretti. Altıncı yama
  açılmadı, soru sahibine (arka uç sözleşmesi) devredildi.
- **Düzeltmenin kendi yan etkisini ÖLÇ.** F4 damgayı INSERT'ten UPDATE'e taşıdı ve yapısal
  kapıyı sahte yeşile döndürdü (kapı yalnız INSERT tarıyordu). M2'nin tur-3 düzeltmesi de
  komşu deliği açtı. İkisi de ölçülünce görüldü.
- **Bir partinin KENDİ açtığı medium'u "kabul edilen risk" diye park etme.** Politika
  medium'u advisory sayıyor; ama gerileme senin ürünündeyse düzeltilir. Önceden var olan
  borç ise kabul edilebilir — farkı ÖLÇEREK göster (`git show <base>:<dosya>`).
- **`Exec-Kind` yazmadan ÖNCE commit'in path kümesine BAK.** Trailer bloğuna boş satır
  koyma: `Co-Authored-By` ayrı paragrafa düşerse `Exec-*` alanları footer'sız sayılır
  (bu oturumda bir kez oldu, amend ile düzeltildi).
- **Codex prompt'u SHELL heredoc'uyla YAZILMAZ** — SETUP fence + Write tool ile
  `$CODEX_LOG` türevli yola.
- **Kota `SOFT` derse sebebi oku.** Bu oturumda hep "ölçüm bayat (>900s)", kullanım %6;
  tek-çağrı dalı "uyar + devam".

## Notes For Codex

- Kapsam daraltma prompt'ta veriliyor; sanitize substratta üretim dosyaları hariç tutuluyor —
  **yokluklarını bulgu sayma**, git nesnelerinden oku.
- Sanitize substratta pytest/npx koşamıyorsun; runtime ölçümleri prompt'ta veriliyor.
- **Dispositioned maddeleri yeniden açma** (yukarıdaki Risks listesi). F17 Eray-tahkimli.
  Sweep tabanının kökeni KAPALIDIR.
- **Task 9/10/11/12'nin kapalı sınırlarını yeniden açma:** ayraçsız işaret yakalanmaz ·
  CTA içinde ayraç yalnız bayraktır · kit anahtarı silinemez · sahne zenginleştirmesinde
  yinelenme kontrolü YOK · hareket/sahne geri düşüşü RASTGELE · damga yazımı başarısızsa
  `generation_id` null.
- **Süpürücü↔webhook terminal-durum tutarsızlığı KAPSAM DIŞI** ve Eray'ın parkında; bulgu
  sayma. Task 12 yalnız arayüzü arka uçla tutarlı hâle getirdi.
- **033 için geri alma script'i YOK** — plan istemedi, evi Task 16. Eksik adım sayma.
- Önyüz kapıları **yapısal** olduklarını docstring'lerinde SÖYLÜYOR; "davranışsal değil"
  diye bulgu yazma — etiket zaten dürüst.
- **K-06 açık:** legacy kısa video ucu pakete bilerek bağlanmadı.
- **K-15(a)** alan-düzeyi atlama dalı bilinçle YOK.
