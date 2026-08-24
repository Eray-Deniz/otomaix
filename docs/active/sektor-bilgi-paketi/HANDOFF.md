# Handoff

> ⚠️ YÜRÜTME AÇIK — bu anlatı oturum sonuna aittir; canlı yürütme durumu TASK.md
> "Execution State" + git defterinden okunur, çelişkide onlar esastır.

## Context
- Task: sektor-bilgi-paketi — Plan 1 yürütmesi açık (`/execute-plan-claude-codex` protokolü)
- Last updated: 2026-08-24 (on birinci oturum — Task 10, Task 11, Task 8 revizyonu, K-02/K-113 kapanışı)
- Plan: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (`plan-approved`)
- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Spec girdisi: `docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md` — **bu oturumun dersi:
  spec eksik yazılmıştı, cevaplar input'taydı. Karar sorusu çıkarsa ÖNCE input'a bak.**
- Dal: `feat/sektor-bilgi-paketi` (**upstream YOK — hiç push edilmedi**)
- Codex ham review log'u: `/root/.claude/logs/otomaix--ffc87809/2026-08-24-feat-sektor-bilgi-paketi-execute.md`

## Current State
- **Biten:** Task 1–10 · **Task 11 kodu yazıldı ama checkpoint'i KAPANMADI.** Task 8 bu oturumda
  K-02 kapanışı nedeniyle revize edildi.
- **Tek açık kapı:** Task 11'in son düzeltmesi (`419eb21`) bağımsız hakemden geçmedi. Ayrıntı ve
  evi TASK.md "Open Problems"ta.
- **Mod:** inline. `execute_mode: subagent-driven` kaydı BİLEREK değiştirilmedi (Task 1-2'yi doğru
  anlatıyor). inline YALNIZ task yazımını kapsar; review/checkpoint kapıları normal koştu.
- **Checkpoint:** `cp_count: 10`, `last_checkpoint_ref` checkpoint 10'da (`c7de397`).
  **Checkpoint 11 approve almadığı için ref İLERLETİLMEDİ** — §8.6 mutation protokolü yalnız
  Clean/Accepted-risk dallarında çalışır. Tavan 8, yani her riskli task `CEILING_RISK` dalına
  düşüyor; Eray bu oturum boyunca RUN-anyway izni verdi (audit `ceiling-exceed`).
- **İNCELEME BÜTÇESİ TÜKENDİ + rezerveden bir tur kullanıldı.** Bütçe oturum başına sıfırlanır;
  yeni oturum tam payla başlar.
- **Ortam (yeni oturumda TEKRAR KURMA — duruyor):** `apps/social/backend/.venv`.
  Komut daima `.venv/bin/python`; makinede `python` komutu YOK.

## Resume From (sıra)
1. **Checkpoint 11'i kapat.** Kapsam `--base c7de39751793e02823ddeae77cf7c9d1b6e58887`.
   Ledger'a şunlar yazılır (yeniden açtırma): F1 ve F2 **hakem tarafından KAPALI doğrulandı**
   (tur 2); F3'ün dört kök nedeni ve dördüncü düzeltmesi (`419eb21` — yinelenme yüklemi
   KALDIRILDI, kalıp her zaman eklenir). Yalnız `419eb21` yeni delta'dır.
2. Approve gelirse §8.6 mutation protokolü: `last_checkpoint_ref = <o anki HEAD>` **ve**
   `cp_count = 11`, tek commit'te.
3. **Sonra Task 12** (K-07 damga yazımı + gözlemlenebilirlik log çekirdeği). Eray bu oturumda
   "Task 12'ye geçince dur" dedi; o sınır bu oturuma aitti, yeni oturumda geçerli DEĞİL.
4. Sonra Task 13 → 16.
5. **Task 8'den sonraki HER task'ın son adımı tam sweep'tir:**
   `.venv/bin/python -m pytest tests/prompt_regression/ -q` yeşil olmadan ilerlenmez (Task 7 freeze hükmü).
6. **Frontend'e dokunulduysa `npx next build` KOŞULUR.** Bu oturumda ilk kez koşuldu ve geçti.

## Verification (bu oturum)
- **Koşan komutlar / taze çıktı:**
  - `cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → **296 passed**
    (oturum başında 232).
  - `.venv/bin/python -m pytest tests/prompt_regression/ -q` → **71 passed** (byte-exact freeze
    kapısı; her düzeltme turundan sonra tekrar koşuldu, donmuş fixture'lar bayt değişmedi).
  - `cd apps/social/frontend && npx next build` → **geçti** (bu daldaki ilk frontend derlemesi).
  - Canlı veritabanı ölçümü (salt okuma, taze): `social.sector_packages` **YOK**
    (`to_regclass` → `f`) — 032 canlıya uygulanmadı, yani bugün üretimde tek paket bile yok.
  - Doküman değişikliğinin ekleme-yönü mekanik doğrulandı: `git diff --stat` → **108 satır
    eklendi, 0 silindi** (spec+plan eksik kaydı), sonra **85 satır eklendi, 0 silindi**
    (K-02/K-113 kapanışı).
- **Pozitif kontrol disiplini:** her düzeltme, düzeltmeden ÖNCEKİ sürüme karşı düşen bir testle
  kanıtlandı. Ölçülen "önce" davranışları: caption rotası `_write_generation_stamp`'e bağlıydı ·
  yedek çıktı paket damgası alıyordu · `"   "`/`"..."` gün adı işlenmemiş 500 üretiyordu ·
  alternatif taşıyan paket yazılamıyordu · uydurulmuş `template_fields.motion_prompt` ücretli
  video modeline ulaşıyordu · İngilizce hazır istem sahne havuzunu hiç görmüyordu ·
  `"."` havuz öğesi zenginleştirmeyi atlatıyordu · `"ring" in "spring"`.
- **Codex:** checkpoint 10 → 2 tur (approve). Checkpoint 11 → **4 tur, approve YOK**.
  Toplam 11 bulgu; **11'i de bağımsız sondajla doğrulandı**, hiçbiri sondaj koşmadan kabul veya
  reddedilmedi. Bir bulgunun severity'si Codex'in dediğinden yükseltildi (`medium → high`:
  genel kullanıcı girdisinden işlenmemiş sunucu hatası).
- **DENENMEYEN / kapsanmayan:**
  - **Task 11'in son düzeltmesi (`419eb21`) hakemden geçmedi** — bu oturumun tek açık kapısı.
  - Frontend yalnız DERLENDİ; gerçek arayüzde tek bir video üretimi denenmedi. Hareket seçiminin
    uçtan uca (caption → istemci → stage-1 → stage-2) gerçek akışta taşındığı ÖLÇÜLMEDİ;
    kanıt birim ve yapısal testlerdir.
  - Canlıya hiçbir migration uygulanmadı — 032 canlı uygulaması manuel adım, Task 16.
  - Gerçek bir sektör paketi hiç yazılmadı; tüm ölçümler fixture üstünde. Paketi ÜRETEN hat
    (araştırma → brief → sentez) Plan 2'nin işi.
  - `IS JSON OBJECT` yüklemi yalnız PostgreSQL 18.3'te ölçüldü; PG16'da varlığı belgeye dayanıyor,
    BU MAKİNEDE ÖLÇÜLMEDİ.
  - Kısa video stage-2 gerçek bir fal.ai çağrısıyla koşulmadı (dış dünya kesildi).

## Risks

**Bu oturumun kalemleri:**
- **[açık borç — evi: yeni oturumun ilk işi]** Task 11'in son düzeltmesi (`419eb21`) hakemden
  geçmedi. Ayrıntı TASK.md Open Problems.
- **[bilinçli tasarım — dört turluk dersin sonucu]** Sahne zenginleştirmesinde yinelenme kontrolü
  YOK; kalıp zaten varsa metin tekrar eder. Tekrar görsel modelde zararsız ve GÖRÜNÜR, eksiklik
  sessizdi. Yeniden açılma: tekrarın görsel kaliteyi bozduğu gerçek üretimde ölçülürse.
- **[bilinçli tasarım]** Hareket ve sahne geri düşüşü havuzdan RASTGELE seçer; sabit öğe o
  sektörün her videosunu aynı kalıba düşürürdü.
- **[bilinçli tasarım]** Damga yazımı başarısızsa `generation_id` null döner (eksik-atıf yönü);
  üretim düşürülmez. Ters yön var olmayan kayda işaret ettirirdi.
- **[doğrulama boşluğu — evi VAR: pilot]** Hareket/sahne seçiminin uçtan uca gerçek akışta
  taşındığı ölçülmedi; kanıt birim ve yapısal testler. Gerçek ölçüm ancak canlı bir paket
  varken mümkün (bugün `sector_packages` tablosu canlıda YOK — ölçüldü), o yüzden evi
  **kuyumculuk pilotu**: pilotun ilk paketli videosunda hareketin havuzdan geldiği ve sahne
  dilinin uygulandığı elle doğrulanır. Bu, evsiz bir park DEĞİL — pilot planlı bir fazdır.
- **[Plan 2 teslim kalemi — evi VAR: plan "Plan 2'ye teslim edilen arayüzler", Task 16 doğrular]**
  Brief/sentez hattı `video_kodlar` için İKİ HAVUZ üretmeli (`hareket`, `sahne`; ikisi de liste).
  Asgari eleman sayısı **kapı YAPILMADI** (İlke 9).

**Devralınan, değişmeyen kalemler** (ayrıntı TASK.md Open Problems + önceki oturum kayıtları):
- `accepted_risk` (checkpoint 9): CTA içinde serbest köşeli ayraç yok · `brand_kit` anahtarı
  silinemez.
- Belgeli sınırlar (testle pinli, borç DEĞİL): ayraçsız kanal işareti yakalanmaz · tam genişlikli
  ayraçlı etiket tanınır ama basımdan çıkarılamaz (kozmetik).
- `accepted_risk` (test altyapısı): eşzamanlı iki pytest oturumu `otomaix_test`'i düşürür ·
  migration keşfi tekrarlı numarayı reddetmiyor · `db` fixture geri sarma testi yok ·
  `sector_research_artifacts` TRUNCATE regresyonu yok · `idx_brands_sub_sector_id` plan
  sözleşmesinde yazılı değil (low).
- **[Eray risk kabulü]** On-prem PG16 ↔ 032'nin PG18 kolonu: **çözülmedi + park edildi.**
- **F17 (Eray):** damga = edited-lineage atfı. **Yeniden açtırma.**
- **[checkpoint-override, checkpoint 5]** Sweep tabanının kökeni — kapalı.
- **Residual (evi Task 16):** geri alma ile ileri 032 arasında ortak kilit yok.
- **Temizlik borçları (evi: `/simplify-claude-codex`):** iki dosyada kullanılmayan `pytest`
  importu · `brands.py`'de kullanılmayan `BrandOut`.
- **Etiketler (evi: `/finish-branch-claude-codex`):** `backup/pre-footer-fix`,
  `backup/pre-t3-kind-fix` merge/PR kararından sonra silinir.

## Notes For Claude
- **Karar sorusu çıkarsa ÖNCE spec-input'a bak.** Bu oturumun en pahalı dersi: Task 11'de "iki alt
  yapıdan hangisi sahne" diye takıldım ve bunu yeni bir tasarım kararı gibi sundum. Cevap
  input'ta yazılıydı (öneri · sahip · "spec içinde teknik olarak çözülür"). Spec'i ben yazmıştım
  ve eksik taşımıştım. **Spec bir özet; kanonik ayrıntı input'ta.**
- **Test yaprağa değil YOLA bakmalı.** Checkpoint bulgularının çoğu "yardımcıyı test ettim, ürün
  yolu yönlendiricide ayrılıyordu" sınıfındandı. Rota kaydı, istemci taşıması, kalıcı kayıt —
  ayrı ayrı sınanmalı; kaynak-dizesi iddiası entegrasyon deliğini göremez.
- **Serbest metinden "bu zaten yeterli mi" sorusunu cevaplayan yüklem yakınsamaz.** Turlar
  daralarak geliyorsa yamalamayı bırak: ya yüklemi sil (tekrar pahasına her zaman uygula), ya iki
  tarafı TEK ortak ölçüye bağla (K-01b disiplini).
- **Güven sınırını "kökeni şu olmalı" ile kurma.** Sunucu kökeni doğrulayamıyorsa o varsayımdır.
  İki bulgu bundan doğdu: istemci sözlüğünü sunucu kaydı sanmak; İngilizce metni "caption
  modelinden gelmiştir" saymak.
- **Kör `replace` yapma — legacy uç aynı desenleri taşıyor.** `brand_kit["sector"]` ve
  `template_fields is None` hem legacy `run_short_video_pipeline`'da hem stage-1'de eşleşiyor.
  Tek-eşleşme iddiası (`count == 1`) bunu iki kez yakaladı; K-06 ihlali önlendi.
- **`Exec-Kind`'ı yazmadan ÖNCE commit'in path kümesine BAK.** `last_checkpoint_ref` TAM SHA
  (40 hane) ve YALNIZ §8.6 mutation protokolüyle değişir.
- **Codex prompt'u SHELL heredoc'uyla YAZILMAZ** — SETUP fence + Write tool ile `$CODEX_LOG`
  türevli yola. Timeout 124'te refleksle degradation'a düşme: önce 120s canlılık sondası, sağlamsa
  `CSS_CALL_TIMEOUT=1200s` ile TEK tekrar (bu oturumda bir kez oldu, tekrar başarılı).
- **Kota `SOFT` derse sebebi oku.** Bu oturumda hep "ölçüm bayat (>900s)", kullanım %1–6;
  tek-çağrı dalı "uyar + devam".

## Notes For Codex
- Kapsam daraltma prompt'ta veriliyor; sanitize substratta üretim dosyaları hariç tutuluyor —
  **yokluklarını bulgu sayma**, git nesnelerinden oku.
- Sanitize substratta pytest/npx koşamıyorsun; runtime ölçümleri prompt'ta veriliyor, koda karşı
  doğrula.
- Dispositioned `accepted_risk` maddeleri **yeniden açma** (yukarıdaki Risks listesi).
  F17 Eray-tahkimli. Sweep tabanının kökeni KAPALIDIR.
- **Task 9/10'un kapalı sınırlarını yeniden açma:** ayraçsız işaret yakalanmaz · CTA DIŞINDA
  serbest ayraç serbesttir · CTA İÇİNDE ayraç yalnız bayraktır · kit anahtarı silinemez · tam
  genişlikli ayraçlı etiket basımdan çıkarılamaz · checkpoint 10'un F1-F4'ü kapalı.
- **Bu oturumda tahkim edilen üç tasarım kararını bulgu sayma:** sahne zenginleştirmesinde
  yinelenme kontrolü YOK (tekrar kabul edilen bedel) · hareket/sahne geri düşüşü havuzdan
  RASTGELE seçer · damga yazımı başarısızsa `generation_id` null döner.
- **K-06 açık:** legacy kısa video ucu pakete bilerek bağlanmadı.
- **K-15(a)** alan-düzeyi atlama dalı bilinçle YOK.
