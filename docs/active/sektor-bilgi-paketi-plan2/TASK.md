---
title: Sektör Bilgi Paketi — Plan 2 (işletim hattı)
status: active
started: 2026-08-27
last-touched: 2026-08-30
blocked-by: null
source_plan: docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md
---

# Goal

Sektör bilgi paketini ÜRETEN ve AKTİVE EDEN işletim hattını kurmak: sözleşme düzeltmeleri →
`brief-doctor` → iki kör denetçi orkestrasyonu → sentez → politika motoru → onay yüzeyi →
komut ailesi → migration'lar → kuyumculuk pilotu. Plan 1 runtime çekirdeğini kurdu ve
main'de; Plan 2 onun "Plan 2'ye teslim edilen arayüzler" listesini tüketir.

Şu anki aşama: **plan ONAYLI, yürütme bekliyor.** Onay hakem zinciriyle değil **Eray'ın risk
kabulüyle** alındı (2026-08-27); son iki düzeltme partisi incelenmedi.

# Execution State

- execute_mode: subagent-driven
- execute_started: 2026-08-30 11:36
- execute_start_ref: a806e29a1ea6a2f82e097fb90fe9c6b8c07b7fb9
- ledger_window_ref: a806e29a1ea6a2f82e097fb90fe9c6b8c07b7fb9
- execute_review_log: /root/.claude/logs/otomaix--ffc87809/2026-08-30-feat-sektor-bilgi-paketi-plan2-execute.md
- execute_branch: feat/sektor-bilgi-paketi-plan2
- cp_count: 1
- last_checkpoint_ref: c7be18fb523118ea9d9d0ea90d4152ecdd2a74a2

# References

- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Spec girdisi: `docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md` — **kanonik**;
  spec damıtmadır, çelişkide girdi esastır
- Plan 1: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (`plan-approved`, yürütüldü, arşiv
  `docs/task-archive/2026/08/sektor-bilgi-paketi/`)
- **Boşluk raporu:** `docs/research/2026-08-27-spec-input-bosluk-raporu.md` (`d16f228`)
- **Karar turu:** `docs/research/2026-08-27-plan2-karar-turu.md` (`a1bdc0c`, `cb7accf`)
- Codex ön-analizi: `~/.claude/logs/otomaix--ffc87809/2026-08-27-sektor-bilgi-paketi-plan2.md`
- Kanonik sözleşmeler (ayrı depo): `/root/otomaix-sosyal-medya-arastirmasi/` —
  `_SABLON.md` · `hakem-denetci-gorevi.md` · `hakem-sentez-gorevi.md`

# Current Status

**YÜRÜTME BAŞLADI (2026-08-30).** Plan onaylıydı; yürütme öncesi ön-tarama planda kapatılmamış
çapraz-görev sözleşmeleri buldu, onlar bir **arayüz eki** ile kapatıldı, sonra Task 1 indi.

- **Arayüz eki KAPANDI:** `docs/plans/2026-08-27-sektor-bilgi-paketi-plan2-arayuz-eki.md`
  (bağlayıcı; çelişkide EK geçerlidir). 17 hüküm — R1–R14 + AÇIK-1 · AÇIK-2 · AÇIK-3.
  Üç Codex karşıt-hakem turundan geçti (high sayısı 7 → 4 → 2); doktrin delikleri kapandı,
  zincir kontrolör kararıyla bitirildi (dördüncü tur AÇILMADI).
- **Task 1 TAMAM** — sözleşme pin doğrulayıcısı, commit `32791b1`. Hakem: spec ✅, kalite onaylı.
- **Task 2 TAMAM** — dış depodaki altı bloklayıcı sözleşme düzeltmesi + 13 kalemlik yansıma
  sweep'i + gerçek pin. Monorepo `1186d44` + `cf7ee31`; **dış depo** (`/root/otomaix-sosyal-
  medya-arastirmasi`) `6d2a033` + `d901eb4`. Hakem: spec ✅; bir Important + beş Minor düzeltme
  turunda kapandı, yeniden inceleme altısını da ADDRESSED verdi. Task 1'in üç Minor bulgusu
  burada kapandı.
- **Checkpoint 1 KOŞTU** (Codex karşıt-hakem, taban `a806e29`): bir **high** buldu — bozuk
  manifest, fail-closed doğrulayıcıyı geçirebiliyordu (üç yol: hata-işareti commit değeri ·
  mutlak yol anahtarı · `..` gezinmesi). Üçü de ölçümle doğrulandı ve `c7be18f` ile kapatıldı;
  kapanış turu **approve** verdi. Kalan tek medium kabul edilmiş risk (aşağıda).
- **Sıradaki: Task 3** — kalıp kimliği + karar günlüğü şeması (K-84 ailesi).

Yürütme defteri (kanonik ilerleme + tüm kararlar):
`.superpowers/sdd/2026-08-27-sektor-bilgi-paketi-plan2/progress.md`

# Decisions Log

- **2026-08-27 — K-84 = A:** kalıp kimliği sürümler arası korunur. Değeri eşleştirmek
  değil, sentez ajanının atladıklarını motorun yakalayabilmesi. Doğurduğu teknik kalemler
  K-151/K-152/K-86/K-154 planın işi.
- **2026-08-27 — K-23 = B:** motorun kararsız kaldığı madde güvenli varsayılana düşer
  (kalıp korunur) + rapora yazılır; aktivasyonu bloklamaz. Gerçek çelişkiler zaten sentezin
  açık soruları olarak gelip K-71 gereği bloklar. Önce A seçildi, üç kademeli yapı
  gösterilince B'ye çevrildi.
- **2026-08-27 — K-125 + K-100 = benimsendi:** denetçiler her turda aktif paketin her karar
  birimini de tarar (beş statü); motor `guncelle`/`cikar` için iki denetçi uyumu arar.
  Denetçi sözleşmesinin yeni sürümü gerekiyor.
- **2026-08-27 — K-133 = kurulmasın:** kuru mod ayrı koşu kipi olarak yazılmaz. Provenans
  ölçüldü: dokuz kaynak dosyanın hiçbirinde yok, tek hakemden geliyor. Çözdüğü temizlik
  sorunu K-106 (yerinde güncelleme) ile kapatılır. Yeniden açılma: motor ikinci sektöre
  yayıldığında.
- **2026-08-27 — K-130 · K-131 · K-132 = mekanizma kurulsun, eşik boş:** üç bariyerin kodu
  yazılır, değerleri pilot kalibrasyonunda konur. Ölçüldü: hiçbir kaynakta önerilmiş sayısal
  eşik YOK.
- **2026-08-27 — K-41 = eşik yok:** onay özeti "Çıkarılanlar: N" der, tam liste bir tık
  derinde. "Eşik üstü" boyutu hiçbir katmanda tanımlı değil.
- **2026-08-27 — K-42 = sıralama + aktivasyon süresi metriği:** özet riskli sınıfları nötr
  sayıların önüne koyar; onaya kaç saniyede basıldığı kaydedilir (R-21 tespit göstergesi).
  Geçmişe karşı anormallik tespiti dışarıda — geçmiş birikince.
- **2026-08-27 — K-134 = pilotta paralel, sonra tek geçiş:** pilot turlarında operatör önce
  sentez çıktısına bakıp yargısını kaydeder, sonra motorla karşılaştırılır — spec §15.2'nin
  istediği kalibrasyon verisi böyle doğar.
- **2026-08-27 — K-01a · K-146 · K-147 = üçü de eklensin:** 10 Kasım · 24 Kasım Öğretmenler
  Günü · okula dönüş. Sebep mekanik: sistem takviminde olmayan dönem pakete giremiyor.
  K-147 dönem taşıdığı için migration gerektiriyor.
- **2026-08-27 — Plan 2 tek planda yazılır.** Codex'in kademeli bölme önerisi reddedildi;
  ama kuralı korundu: sentez tek başına `draft` yazamaz, kanonik sıra sentez → motor → draft.
- **2026-08-27 — Komut ailesi: iş mantığı repoda CLI, `~/.claude/commands/` ince çağırıcı.**
  Kaynak sözleşmeler araştırma deposunda kalır; monorepo tarafında pin manifesti.

- **2026-08-27 — Genel review turu DURDURULDU.** Plan yeni bir kapsamlı hakem turuna
  sokulmuyor; yalnız iki kök tasarım sorunu (K-145 sözleşmesi · Task 12/13 sonuç sahipliği)
  uçtan uca kapatıldı. **Kalan risk ölçülmedi, bilinçle kabul edildi** — durdurmak kapanmak
  değildir.
- **2026-08-27 — Plan RİSK KABULÜYLE ONAYLANDI (Eray).** Son iki düzeltme partisi hiçbir
  hakem görmedi; zincirin son yargısı `needs-attention`'dı. Onay bu bilgiyle verildi.
  Frontmatter bunu yansıtır: `approved-by-iteration-limit` + `unresolved_high_severity_override: true`.

- **2026-08-30 — Yürütme öncesi ön-tarama koşuldu ve arayüz eki yazıldı (Eray onayı).**
  66 görev çifti tarandı: 8 çelişki · 12 boşluk · 20 görevin 18'inde iç tutarsızlık. Sebep
  yapısal: her görev KENDİ brief'ine karşı incelenir, komşusuna karşı değil — iki görevin
  farklı icat edeceği bir sözleşme görev-başı review'a görünmez. Eray "ek + tek hakem turu"
  seçti (ben karara bağlayıp yürütmek ve planı tam onarım turuna sokmak reddedildi).
- **2026-08-30 — AÇIK-1: geri alma onayı, onayladığı plan satırının yanında saklanır.**
  Bildirim kuyruğu seçilmedi (kuyruğun temizlik döngüsü onayı silebilir; yürütücü zaten
  kilitlediği satırın yanında ikinci tablo okumak zorunda kalırdı). Onay OLAY düzeyindedir,
  paket düzeyinde değil — K-145 N paketi birden geri alır, paket başına onay tek operatörde
  taşınamaz. Maliyet ölçüldü: migration henüz yazılmadığı için alanlar bedava.
- **2026-08-30 — AÇIK-2: tek-paketlik geri alma da olay kimliği ister.** İlk içgüdüm "acilde
  üç komut fazla" diye tersiydi; ölçünce döndüm — acil kol (deaktive-et) kanıt zinciri
  istemez ve bu karardan ETKİLENMEZ. Kapanan tek şey "önceki sürüme kanıtsız dönme", ki o
  acil değil düşünülmüş bir hamledir. Örtük olay üretmek kalıcı kirlilik yaratırdı.
- **2026-08-30 — AÇIK-3: parmak izi yardımcıları Task 8'de, Plan 1 modülünde doğar.**
  **Verdiğim gerekçe YANLIŞTI ve düzeltildi:** "bağımlılık yönü hiç ters çevrilmedi" dedim,
  ölçüldü ki bir tur önceki kendi metnim onu zaten çevirmişti. Karar geçerli, sebep düzeltildi,
  tek izinli kenar açıkça yazılı ve yapısal testi var.
- **2026-08-30 — Hakem zinciri kontrolör kararıyla BİTİRİLDİ (dördüncü tur yok).** Doktrin
  delikleri kapandı; kalan bulgular henüz var olmayan kodun davranışı. Bir belge çalışma
  zamanı kuralını uygulayamaz, yalnız anlatır — devamı Türkçe kod yazmak olurdu. Çıkış
  koşulu olarak mekanik öz-denetim koşuldu (50 hüküm→görev çifti, 0 eksik).

# Open Problems

- **Task 1'in üç Minor bulgusu Task 2'de KAPANDI** (`1186d44`): depo-yok kapısı artık kendi
  sebebine assert ediyor · `_head_commit` çözümlemeyi verilen köke sabitliyor · hiçbir sözleşme
  dosyası adlandırmayan manifest `load_pin`'de reddediliyor (kapı kümesi DÖRT kaldı — ek R14).
- **Hakemin doğrulayamadığı iki durum EV BULDU (2026-08-30 kapanış sweep'i): Task 18 Step 8b.**
  `git` ikilisi olmayan ortamda davranış ve `GIT_DIR`/`GIT_WORK_TREE` ezilmesi. Neden orası:
  pin doğrulayıcısı commit'i `git rev-parse` ile okur, yani ikili yoksa resmî koşuyu başlatan
  HER CLI alt komutu ilk adımda patlar — bu bir **dağıtım** sorusudur, kod sorusu değil.
  Tarih: Task 18 koşana kadar yok; yürütme oraya varmadı. Dürüst etiket: *doğrulanmadı; evi ve
  adımı var.*
- **KABUL EDİLMİŞ RİSK (arayüz eki, tur 3 sonrası):** "annotation çalışma zamanı zorlaması
  değildir" sınıfının kalıntısı ve kimlik karşılaştırmalarındaki hoşgörülü normalleştirme.
  Dördüncü hakem turuyla kovalanmadı; kod yazılırken kırmızı-yeşil döngüsüne ve görev-başı
  review'a devredildi. Bu bir **kabul**, sınıfın kapandığı iddiası DEĞİL.
- **Ortam gerçeği (ölçüldü, plandan farklı):** planın yazdığı `python -m pytest` bu makinede
  çalışmaz — `python` PATH'te yok. Her test komutu
  `cd apps/social/backend && source .venv/bin/activate && python -m pytest …` biçiminde koşar.
- **Task 5 ve Task 19 Eray kararı bekliyor** (o görevlere gelindiğinde sorulacak, şimdi değil):
  takvim satırlarının yılı · kategorisi · kanonik adı · "okula dönüş" tarihleri; ve dört
  operatör kararı.
- **30 teknik kalem BAĞLANDI** (plan yazımında); kapanış görevi (Task 20) 30 teknik + 13 ürün
  kararını tek tek sweep eder.
- **§8.7'nin sözleşme düzeltmeleri KAPANDI** (Task 2, dış depo `6d2a033`+`d901eb4`): altı kalem
  + yedi yansıma kalemi, sweep 13/13 "var". Resmî turu artık bloklamıyorlar.
- **Task 2'den Task 4'e devredilen üç sözleşme kalemi** (park değil — Task 4 aynı dosyalara
  dokunuyor ve sürümlerini zaten artırıyor): (a) iki farklı bayt kümesi aynı sürüm damgasını
  taşıyor (`6d2a033` ve `d901eb4` ikisi de "Sürüm 1.3"/"Sürüm 1.2") — kapı sha256'ya baktığı
  için mekanik risk yok, izlenebilirlik pürüzü; (b) iki genel hüküm kanal-bayrağı maddesinin
  içine yerleşmiş (28 satırlık madde), içerik doğru yer yanıltıcı; (c) `hakem-sentez-gorevi.md`
  satır 100 `[muhtemel-uydurma]`yı bayrak biçiminde anıyor ama kapalı bayrak kümesi sekiz üye
  ve onu içermiyor.
- **CTA köşeli ayraç çelişkisi — ÇÖZÜLMEDİ, park edildi, tetiği var:** yazım kapısı
  `cta_kaliplari` ve `ozel_gun[*].cta` içinde bayrak olmayan HER ayracı reddediyor, ama
  `_SABLON.md` araştırmacıya CTA kalıplarını ayraçlı değişkenlerle soyutlatıyor. Task 2 bunu
  sözleşme metninde **açıkça açık** bıraktı ("BİLİNEN ve AÇIK bir kalem"), gizlice çözmedi.
  Task 2'nin ürünü DEĞİL, önceden var. Tetik: ilk kuru koşum (Task 11 veya Task 19), ya da
  `_check_channel_markers`'a dokunan herhangi bir değişiklik.
- **Task 15'in elle arayüz doğrulaması** Task 19 Step 11'de; plan onaylı, tarih pilot görevinin
  koşmasına bağlı. Dürüst etiket: *çözülmedi; evi var.*
- **n8n hata bildirimi** Task 16 Step 7/7b'de; kapsam bilinçle dar (yalnız sektör paketi
  zinciri), kalan workflow'lar CRM turunda.
- Plan 1 bölümlerinin kart geçişi taranmadı (boşluk raporu kapsam sınırı) — Plan 1 alanında
  kusur çıkarsa koşulur.
