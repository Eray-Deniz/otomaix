# Handoff

> ⚠️ YÜRÜTME AÇIK — bu anlatı oturum sonuna aittir; canlı yürütme durumu TASK.md
> "Execution State" + git defterinden okunur, çelişkide onlar esastır.

## Context
- Task: sektor-bilgi-paketi — Plan 1 yürütmesi açık (`/execute-plan-claude-codex` protokolü)
- Last updated: 2026-08-24 (onuncu oturum — YALNIZ Task 9)
- Plan: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (`plan-approved`)
- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Dal: `feat/sektor-bilgi-paketi` (**upstream YOK — hiç push edilmedi**)
- Codex ham review log'u: `/root/.claude/logs/otomaix--ffc87809/2026-08-24-feat-sektor-bilgi-paketi-execute.md`

## Current State
- **Biten:** Task 1–8 (önceki oturumlar) · **Task 9** (kanal envanteri + deterministik CTA
  filtresi). **16 task'ın 9'u.**
- **Devralınan borç YOK, devreden borç YOK.** Açık kapı bırakılmıyor; iki kalıntı Open Problems'ta
  dürüst etiketiyle ve yeniden-açılma koşuluyla yazılı.
- **Mod:** inline (Eray talebi). `execute_mode: subagent-driven` kaydı BİLEREK değiştirilmedi
  (Task 1-2'yi doğru anlatıyor). inline YALNIZ task yazımını kapsar; review/checkpoint kapıları
  normal koştu.
- **Checkpoint:** `cp_count: 9` (tavan 8 — **aşıldı**, Eray oturum başında açıkça izin verdi,
  audit `ceiling-exceed`). Checkpoint 9 **altı** turda kapandı.
- **İNCELEME BÜTÇESİ BU OTURUMDA TÜKENDİ** — tavan 8, en az 3'ü finale rezerve; 6 tur koşuldu ve
  tur 6 Eray kararıyla rezervden fonlandı. **Bütçe oturum başına sıfırlanır**, yeni oturum tam
  payla başlar. Oturumun burada kapatılma sebebi budur.
- **Ortam (yeni oturumda TEKRAR KURMA — duruyor):** `apps/social/backend/.venv`.
  Komut daima `.venv/bin/python`; makinede `python` komutu YOK.

## Resume From (sıra)
1. **Task 10** — `### Task 10: Tek-kapı enjeksiyon — caption + fikir önerme`. Bu, işin en kritik
   adımı: paket ÇÖZÜMLEYİCİSİ ilk kez gerçek üretim akışına bağlanıyor ve dört alanlık dönüş
   sözleşmesi orada sınanıyor. **Ara inceleme olmadan yürütme** — bu yüzden taze oturum gerekti.
2. Task 10 riskli sınıflanırsa checkpoint kararı yine TAVAN-AŞIMI dalına düşer (`cp_count` 9 >
   tavan 8). Eray'ın izni bu iş için verilmiş durumda, ama aşımı **görünür şekilde bildir** —
   sessizce geçme; audit satırı `ceiling-exceed`.
3. Sonra Task 11 → 16.
4. **Task 8'den sonraki HER task'ın son adımı tam sweep'tir:**
   `.venv/bin/python -m pytest tests/prompt_regression/ -q` yeşil olmadan ilerlenmez (Task 7
   freeze hükmü).
5. Task 10 yazarken Task 9'un teslim ettiği filtre çağrılacak — `[kanal-bağımlı: X]` etiketli CTA
   kalıpları basılmadan ÖNCE ondan geçirilir (plan Task 10 bağlayıcı invariantı).

## Verification (bu oturum)
- **Koşan komutlar / taze çıktı:**
  - `cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → **232 passed**
    (oturum başında 185).
  - `.venv/bin/python -m pytest tests/prompt_regression/ -q` → **25 passed** (freeze kapısı,
    her düzeltme turundan sonra tekrar koşuldu).
  - `.venv/bin/python -m pytest tests/test_channel_inventory.py -q` → **47 passed**.
  - Kapanış matrisi: CTA öğesi içinde reddedilmesi gereken **21** yazımın 21'i kapalı (dört turun
    TÜM sondaları + sentezde tüketilmesi gereken bayraklar + düz yazı ayracı); kabul edilmesi
    gereken **8** biçimin 8'i geçiyor; CTA DIŞINDA serbest ayraç temiz.
  - Etiket yazım matrisi: 9 yazım × 4 anahtar biçimi × 8 kanal değeri, kapalı kümedeki her anahtar
    için → **kaçan 0**.
  - Eşzamanlılık ölçümü: düzeltmeden ÖNCE 4 eşzamanlı yazımın **3'ü kayboldu**; sonra 4/4 korunuyor
    (regresyon testi iki bağlantıyla koşuyor ve ürettiği satırları siliyor).
  - Çift kodlama ölçümü: düzeltmeden ÖNCE tek alanlık güncelleme kitin TÜM alanlarını siliyordu;
    sonra hepsi korunuyor.
  - Canlı veritabanı ölçümü (salt okuma): `social.sector_packages` **YOK** (032 canlıya
    uygulanmadı), 2 markanın **0'ında** nesne-olmayan `brand_kit`.
- **Pozitif kontrol disiplini:** her düzeltme, düzeltmeden ÖNCEKİ sürüme karşı düşen bir testle
  kanıtlandı. Yapısal (AST) taramanın kendisi de eski koda karşı pozitif kontrol edildi — iki
  ihlali yakalıyor, yani boşa çıkmış bir tarama değil.
- **Codex:** checkpoint 9 → **6 tur**. Tur 1-2 dört bulgu, tur 3-4 sınıf-teşhisiyle DURDURULDU ve
  Eray'a soruldu, tur 5 iki yeni bulgu (ikisi de önceki düzeltmelerin yan etkisi), tur 6 iki
  medium (ikisi de yeniden-açma). **Yedi bulgunun yedisi de bağımsız sondajla doğrulandı.**
- **DENENMEYEN / kapsanmayan:**
  - Canlıya (`otomaix`) hiçbir migration uygulanmadı — 032 canlı uygulaması manuel adım, Task 16.
  - Frontend hiç çalıştırılmadı (`npx next build` koşmadı — ilk gerektiği yer Task 12).
  - `sector_packages` modülünün HÂLÂ hiçbir tüketicisi yok — üretim yolu onu çağırmıyor (Task 10).
    Kanal filtresi de bugün hiçbir üretim akışından çağrılmıyor.
  - `IS JSON OBJECT` yüklemi **yalnız PostgreSQL 18.3'te ölçüldü**. PG16'da var olduğu bilgisi
    belgeye dayanıyor, BU MAKİNEDE ÖLÇÜLMEDİ — on-prem paketi PG16 pinlediği için not düşülüyor.
  - Avatar yazıcılarının yeni birleştirmesi HeyGen akışıyla uçtan uca koşulmadı (SQL değişikliği
    testlerle kapsandı, gerçek avatar akışı denenmedi).
  - `ozel_gun` CTA'sının çalışma zamanında filtreden geçip geçmeyeceği Task 10'un kararı; yazım
    kapısı onu şimdiden kapsıyor (fazla-kapsama, emniyetli yön).

## Risks
- **[medium, accepted_risk — checkpoint 9]** CTA öğesi içinde serbest köşeli ayraç kullanılamaz.
  Ayrıntı + yeniden açılma koşulu TASK.md Open Problems'ta. Evi: denetçi/brief sözleşmesi
  (spec §8.7 listesi), Task 16'da Plan 2 teslim kalemi olarak doğrulanır.
- **[medium, accepted_risk — checkpoint 9]** `brand_kit` anahtarı silinemez, yalnız üzerine
  yazılabilir. Ayrıntı TASK.md Open Problems'ta.
- **[belgeli sınır, borç DEĞİL]** Ayraçsız yazılmış kanal işareti (`kanal-bağımlı whatsapp_hatti`)
  YAKALANMAZ ve yakalanması hedeflenmiyor — ayraç, bayrağı bayrak yapan şeydir. Sınır kendi
  testiyle pinli, sessizce kaybolamaz.
- **[bilinçli tasarım]** Etiket TANIMA geniş (her Unicode/büyük-küçük yazımı), kanal DOĞRULAMASI
  dar (tam `True`). İkisi de atlama yönüne çalışır. Yazım kapısı okuma tarafından kasıtlı olarak
  daha katıdır; asimetrinin yönü emniyetlidir.
- **[bilinçli tasarım — kod belgesinde yazılı]** Marka adı eşleşmesi SOL sınır arar, sağ taraf
  serbesttir (Türkçe eklemeli). Kısa bir marka adı sıradan bir sözcükse paket REDDEDİLİR. Yazım
  kapısında yanlış-pozitif, yanlış-negatiften iyidir. Yeniden açılma: gerçek bir meşru paket bu
  yüzden bloklanırsa.
- **[bilinçli tasarım]** Katlama Türkçe dışı aksanları da düşürür; eşleşmeyi genişletir, yani
  reddetme yönüne çalışır.
- **[gözlem, borç DEĞİL]** `sector_resolver._normalize_slug` bilinçle DEĞİŞTİRİLMEDİ (başka bir
  task'ın artefaktı); tutarlıdır, K-01b ihlali YOK.
- **[medium, accepted_risk]** İki pytest oturumu aynı anda koşarsa biri diğerinin `otomaix_test`
  veritabanını DROP eder (kilit yok).
- **[medium, accepted_risk]** Migration keşfi tekrarlı numarayı reddetmiyor.
- **[medium, accepted_risk]** `db` fixture'ının testler-arası geri sarma garantisini kanıtlayan
  test yok.
- **[medium, accepted_risk]** `sector_research_artifacts` TRUNCATE korumasının regresyon testi yok.
- **[medium, accepted_risk]** Geri alma red testi iki korunan tabloyu AYNI anda dolduruyor.
- **[medium, accepted_risk — Eray kararı]** On-prem paketi PostgreSQL 16 imajını pinliyor, 032
  PG18 kolonu okuyor. **ÇÖZÜLMEDİ + park edildi.** Ayrıntı TASK.md Open Problems.
- **[low, accepted_risk]** `idx_brands_sub_sector_id` planın Task 2 sözleşmesinde yazılı değil.
- **F17 (Eray risk-kabulü):** damga = edited-lineage atfı. **Yeniden açtırma.**
- **[checkpoint-override, checkpoint 5]** Sweep tabanının kökeni — TASK.md Open Problems'ta.
  Adım 11 final review'a `checkpoint_overrides` olarak taşınır.
- **Residual (evi Task 16):** geri alma ile ileri 032 arasında ortak kilit yok.
- **Temizlik borçları (evi: yürütme sonrası `/simplify-claude-codex`):** `test_migration_032.py` ve
  `test_infra.py`'de kullanılmayan `pytest` importu · `brands.py`'deki `BrandOut` importu artık
  kullanılmıyor (bu oturumdan önce de öyleydi).
- **Etiketler (evi: `/finish-branch-claude-codex`):** `backup/pre-footer-fix` ve
  `backup/pre-t3-kind-fix` merge/PR kararından sonra silinir.

## Notes For Claude
- **Bir kapı serbest metinden "X DEĞİLDİR"i kanıtlamaya çalışıyorsa regex'le yakınsamaz.** Bu
  oturumun en pahalı dersi ve dördüncü tekrarı. Sinyal nettir: her tur bir öncekinden DAR bir vaka
  açıyorsa yamalıyorsun demektir. Çıkış yamalamak değil, POZİTİF SÖZLEŞMEYE geçmek — "şu biçime
  uyacak" (kapsama), "şuna benzemeyecek" (tahmin) değil.
- **Sözleşmeyi uydurmadan önce kaynağı sonuna kadar oku.** Kapalı bayrak listesini "spec saymıyor"
  diye yazılamaz sanmıştım; §8.5'in tüketim hükmü listeyi zaten belirliyordu. Uydurma ile türetme
  arasındaki fark bir aramalık mesafedeydi.
- **Kendi düzeltmenin yan etkisini ölç.** Tur 5'in iki bulgusu da benim düzeltmelerimdi: biri
  sessiz veri kaybı açtı, biri kuralı aşırı genişletti. Bir sınıfı kapatırken yenisini açmak
  gerçek ve sık bir sonuç.
- **Kapsamı okuma tarafıyla hizala.** Yazım kapısı, okumanın taradığı birimi kapsamalı — ne eksik
  (okuma denetlenmemiş bir şey görür) ne fazla (zararsız içerik reddedilir).
- **Codex'i olduğu gibi kabul etme, ama ciddiye al.** Yedi bulgunun yedisi de sondajla DOĞRULANDI.
  Sondaj koşmadan ne kabul et ne reddet. Tur 6'da iki madde yeniden açıldı — yeniden-açma
  `RE-LITIGATED` olarak log'a yazılır, fix'e beslenmez; ama içindeki YENİ unsur ölçülür (ölçtüm,
  boş çıktı).
- **Severity Codex'in değil senin kararın.** Tur 1'in medium bulgusu high'dı (görevin tek bağlayıcı
  invariantını gerçekçi girdiyle deliyordu) ve öyle işlendi; gerekçe commit mesajında yazılı.
- **Eray'a teknik cümle onaylatma.** Bu oturumda İlke-8 kapısı bir soruyu geri çevirdi (seçenek
  metninde proje-lokal kod terimi vardı). Soruyu tradeoff seviyesine yeniden yaz; kod-okuma
  gerektiren doğrulama review zincirinin işidir.
- **`Exec-Kind` etiketini yazmadan ÖNCE commit'in path kümesine BAK.** Geçerli küme:
  `code|docs-only|migration|red-only|green-only|merge`. `tests/` altındaki HER ŞEY test sayılır.
- **Codex çağrısı için `COMPANION` kurulmalı** ve prompt SHELL heredoc'uyla YAZILMAZ — SETUP fence
  + Write tool ile `$CODEX_LOG` türevli yola.
- **`last_checkpoint_ref` TAM SHA olmalı (40 hane).**
- **Kota kapısı `SOFT` derse sebebi oku.** Bu oturumda sebep "ölçüm bayat (>900s)", kullanım
  %1.0'dı; tek-çağrı dalı "uyar + devam" diyor.
- **Sır tarayıcısı çok dosya eliyor** — Codex'e "git nesnelerinden oku" diye AÇIKÇA söyle.

## Notes For Codex
- Kapsam daraltma prompt'ta veriliyor; sanitize substratta üretim dosyaları hariç tutuluyor —
  **yokluklarını bulgu sayma**, git nesnelerinden oku.
- Sanitize substratta pytest/psql koşamıyorsun; runtime ölçümleri prompt'ta veriliyor, koda karşı
  doğrula.
- Dispositioned `accepted_risk` maddeleri **yeniden açma** (yukarıdaki Risks listesi).
  F17 Eray-tahkimli.
- **Sweep tabanının kökeni (checkpoint 5 F1 kümesi) KAPALIDIR** — yeniden açma.
- **Task 8'in üç bilinçli tasarım kararını bulgu sayma:** ~6.000 karakter tavanı UYARI'dır ·
  `video_kodlar` alan adları K-02 açık olduğu için bağlanmadı · K-15(a) alan-düzeyi atlama dalı
  bilinçle YOK.
- **Task 9'un dört kapalı maddesini yeniden açma:** (a) ayraçsız işaret yakalanmaz — belgeli,
  testle pinli sınır; (b) CTA DIŞINDA serbest ayraç serbesttir, bu bilinçli daraltmadır;
  (c) CTA İÇİNDE ayraç yalnız bayraktır — kabul edilen içerik kısıtı, evi denetçi sözleşmesi;
  (d) kit anahtarı silinemez — F3 düzeltmesinin kayıtlı bedeli. Dördü de Open Problems/Risks'te
  dürüst etiketiyle yazılı.
