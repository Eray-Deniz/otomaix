---
title: Denetçi atfı ADAYA bağlansın (alan düzeyi yetmiyor)
status: done
started: 2026-09-11
finished: 2026-09-12
last-touched: 2026-09-12
blocked-by: null
source_task: docs/active/denetci-denetim-tablosu-tipli-okuma/TASK.md
---

# Goal

Sentezin `D1#<no>` atfını, o kararın YETKİLENDİRDİĞİ ADAYA bağlamak. Bugün bağ ALAN
düzeyindedir: `kanca_kaliplari` eklemesi `kanca_kaliplari` hakkındaki HERHANGİ bir denetçi
satırına dayanabilir; Görev B'de `ozel_gun` eklemesi HERHANGİ bir dönemin satırına dayanabilir.

# Neden ayrı görev — çerçeve teşhisi (ölçüldü)

Aynı eksen ÜÇ turda ÜÇ varyant üretti ve her seferinde bir katman daha daraldı:

1. **Tur 1 (yüksek):** bağ HİÇ YOKTU — motor yalnız `kaynaklar` ve `sinif` okuyordu, başka
   alanın satırı ekleme yetkilendirebiliyordu. → alan bağı + öneri bağı eklendi.
2. **Kapanış turu (yüksek):** alan bağı var ama YOL bağı yok — Ramazan eklemesi
   `ozel_gun/yilbasi/kanca` satırını gösterebiliyor. → bu görev.
3. Aynı bulgunun ikinci ayağı: sıradan liste alanlarında aynı listedeki HERHANGİ bir iddia
   diğerini yetkilendirebiliyor.

Varyant yamamak DURDURULDU (İlke: varyantı değil sınıfı kapat). Sınıfın kökü şudur:
**sözleşme, bir denetçi satırını belirli bir ADAYA bağlayan makine-okunur hiçbir kimlik
taşımıyor.** `iddia_ozeti` serbest metindir (≤15 kelime), `no` satırın kimliğidir — iddianın
adayla ilişkisinin DEĞİL.

**Ölçülen iki engel:**

- **Görev B:** `hakem-denetci-gorevi.md` satır 234 yalnız `alan = "ozel_gun/{dönem}/{başlık}"`
  der; dönem adının EK-J slug'ı olduğunu SÖYLEMEZ. Sentez sözleşmesi (satır 365-366) paket
  anahtarları için slug ZORUNLU kılar, denetçi tablosu için kılmaz. Bu yüzden tam `oge_yolu`
  bağı bugünkü sözleşmeyle kurulamaz — kurulursa meşru satırlar reddedilir.
- **Liste alanları:** iddiayı adaya bağlayacak kimlik HİÇ YOK; kurulması yeni bir sözleşme
  kavramı ister (denetçi satırında kalıp/iddia kimliği + sentezin o kimliğe atıf yapması).

# Kapanış yönü

1. Denetçi sözleşmesi: Görev B satırında dönem adı EK-J slug'ı olarak DAYATILIR (küçük ek).
2. Liste alanları için kimlik kavramı: denetçi satırı kalıbın kimliğini taşır ve sentez ona
   atıf yapar. Tasarım turu ister — kimliği kim üretir, sentez onu nasıl doğrular.
3. Motor tarafı: `_alan_bagi_var` yerine tam `oge_yolu` / kimlik karşılaştırması.

# Yuva ve son tarih

**SERT SON TARİH: Task 19 (kuyumculuk pilotunun resmî turu).** Sözleşme/çıktı tarafı pilottan
sonra değişirse araştırmalar İKİNCİ KEZ ürettirilir. Kardeş görevlerin gerekçesiyle aynı.

**Yuva: Task 16'dan önce tercih edilir** (motorun üretim çağıranı orada doğuyor); zorunlu
değildir, çünkü değişecek yer motorun İÇİDİR, çağıran arayüzü değil.

# Current Status

**KAPANDI (2026-09-12).** Sözleşme ayağı 2026-09-11'de indi (dış depo `12beec1`, pin
`4636847`; aynı turun devamında `d9dc289` / pin `2739797`), kod ayağı `4cf6aa3` ile indi ve
hakem turunun düzeltmeleriyle (`171c1e5`, `90aee2c`) sağlamlaştı. **Bu blok 2026-09-12'de
DÜZELTİLDİ:** kod ayağı 2026-09-11 gecesi inmiş olmasına rağmen kayıt bir gün boyunca
"hiç yazılmadı" diyordu ve bir oturum açılışını yanılttı.

Eray kararı: **tam bağ** — yetkilendirme araştırma iddiasının NUMARASINA kadar izlenir.
Reddedilen iki ucuz seçenek kayıtta (aşağıda).

**İnen (sözleşme):**
1. `_SABLON.md` Bölüm C tablosu `no` sütunu kazandı — her iddia o raporda KALICI kimlik taşır.
2. Denetçi tablosu `kaynak-iddialari` sütunu kazandı (`K<kaynak>#<iddia>`), `kaynaklar`
   sütunuyla tutarlılık zorunlu.
3. Sentezin `karar="ekle"` satırı `kaynak_iddia` alanı kazandı.
4. **Ölçülen engel kalktı:** Görev B satırlarında `{dönem}` artık EK-J sistem adının SLUG'ı.
   Bu hüküm olmadan tam yol bağı meşru satırları reddederdi.

**Bağ İKİ UÇLU tasarlandı — ve bu bilinçli:** (a) numaranın gösterdiği satır araştırma
raporunda GERÇEKTEN var ve alanı kararın alanıyla örtüşüyor (**mekanik ayrıştırıcı**
doğrular, beyan değil); (b) atıf yapılan denetçi satırı aynı numarayı taşıyor. Tek uçlu
olsaydı bağ kendini onaylardı: iki beyanı da aynı model yazıyor ve sentez denetçi raporunu
okuyabiliyor, yani numarayı kopyalayıp her zaman eşleştirebilirdi. Üçüncü taraf (ayrıştırıcı)
zinciri kırar.

**İNEN — kod ayağı** (dördü de 2026-09-12'de kaynaktan tek tek ölçüldü; commit `4cf6aa3`):

1. **`brief_doctor` Bölüm C'yi SATIR düzeyinde okuyor.** `no` sütunu tipli okunuyor ve o
   raporda kimlik olarak zorlanıyor: tekrar eden numara ve 1'den boşluksuz artmayan dizi ayrı
   ayrı ihlal. Satır başına hücre sözleşmesi de ölçülüyor (alan/dönem · iddia kelime tavanı ·
   `https://` URL · tarih biçimi · tek-kaynak kapalı kümesi).
2. **`auditors` `kaynak-iddialari` sütununu tipli okuyor.** Denetim tablosu dokuz sütun;
   `K<kaynak>#<iddia>` TEK ayrıştırıcıdan (`kaynak_iddialari_coz`) geçiyor ve `kaynaklar`
   sütunuyla ÇİFT YÖNLÜ tutarlılık zorunlu. Satır `kaynak_iddialari` alanını `frozenset`
   olarak taşıyor.
3. **Motor bağı İDDİA düzeyinde kuruyor.** `_alan_bagi_var` silinmedi ama artık TEK
   yetkilendirici değil: ilk kapı (önek eşleşmesi) → `kaynak_iddia` çözümü → iki uçlu bağ
   (her iddia bir denetçi satırında geçmeli VE atıf yapılan her satır en az bir iddiayı
   taşımalı) → Görev B'de ayrıca dönem bağı (`_denetci_donem_bagi_var`). Yeni uygulanmama
   sebepleri: `kaynak-iddia-yok` · `donem-kimligi-cozulemedi`.
4. **`EngineInputs` veriyi taşıyor — YENİ ALAN GEREKMEDİ.** İddia evreni mevcut
   `mekanik_eleme.raporlar` üzerinden geliyor (`_arastirma_iddialari`; kaynak numarası
   KONUMDAN türer, `build_packet` sıra kaymasını fail-closed durdurur). R5 alan kümesi
   revizyonu arayüz ekinde ayrıca kayıtlı (R-H5 · R-H8, revizyon kaydı 2026-09-11/d).

**İki kırmızı test KALMADI.** Taze ölçüm (2026-09-12,
`cd apps/social/backend && .venv/bin/python -m pytest tests/ -q`):
**`4379 passed in 319.80s`, 0 failed.** Kırmızılar pinin bıraktığı Bölüm B sütun alarmıydı;
`4cf6aa3` onları kapattı.

**Dürüst etiket — bu görev kapandı, ama şunlar bu göreve DEĞİL ana göreve yazılı:**
- **N1/1** (aday-dışı günün adı ile anahtarı arasındaki bağ ölçülemiyor) — koşullu
  `accepted_risk`, evi ana görevin `# Open Problems`'ı.
- **Uçtan uca CLI koşumu YOK**; bu bağ gerçek araştırma çıktısıyla hiç çalışmadı — ilk gerçek
  ölçüm Task 19 pilotu.
- Kapanış hakem turu bu partide **tek hakemli** kaldı (Codex kotaya takıldı; Eray kararı
  yalnız o parti için). Ayrıntı ana görevde.

# Decisions Log

- **2026-09-12 — görev KAPATILDI (defter düzeltmesi).** Kod ayağı 2026-09-11 gecesi inmişti;
  bu dosya bir gün boyunca "hiç yazılmadı" diyordu. Kapanış iddiası değil ÖLÇÜM üzerine
  yazıldı: dört ayağın dördü kaynaktan tek tek doğrulandı, tam takım taze koşuldu
  (`4379 passed`, 0 failed). Kalan kalemler uydurma eve değil ana görevin kendi
  `# Open Problems`'ına bağlandı.

- **2026-09-11 — Eray kararı: TAM BAĞ.** Araştırma satırına kadar izleme seçildi; "iki ucuz
  ayak" (özel gün yol bağı + bir satır bir ekleme) ve "yalnız özel gün ayağı" REDDEDİLDİ.
  Gerekçe ölçülmüş: araştırmalar bu biçimde henüz üretilmedi, yani biçim değişikliği bugün
  bedelsiz; Task 19 pilotundan sonra aynı değişiklik bütün araştırmaları ikinci kez
  ürettirirdi.
- **2026-09-11 — `oge_yolu` bağı ELENDİ (ölçüm).** İlk tasarım denetçinin sentezin
  `oge_yolu`'na atıf yapmasıydı; ölçüldü ki `oge_yolu` KONUMSALDIR ve ADAY PAKETE aittir —
  denetçi aday paketi hiç görmez, yeni öğe denetçi çalışırken henüz YOKTUR. Yol kapalı.
- **2026-09-10 — görev AÇILDI.** Kapanış turunun yüksek bulgusunun KALAN ayağı. Kontrolör
  yamamayı bıraktı ve çerçeve teşhisini kullanıcıya götürdü; bu dosya o teşhisin EVİDİR.
  Dürüst etiket: **çözülmedi, ertelendi, evi BURASI.**

# Open Problems

- ~~Sözleşme revizyonu İKİ dosyaya dokunur (denetçi + sentez) ve pin yenilenmesi ister; bu
  görevle aynı turda yapılmalı, ayrı ayrı iki pin turu israftır.~~ — **KAPANDI (2026-09-11).**
  Üç borç TEK dış-depo revizyonunda kapandı, pin bir kez ilerledi. Ayrı tur israfı olmadı.

**Bu görevin kendi açık kalemi YOK.** Bağın gerçek araştırma çıktısıyla ilk sınavı (Task 19
pilotu) ve N1/1 koşullu riski ana görevin defterinde yaşıyor — buraya ikinci kopya YAZILMAZ.
