---
title: Denetçi atfı ADAYA bağlansın (alan düzeyi yetmiyor)
status: active
started: 2026-09-11
finished: null
last-touched: 2026-09-11
blocked-by: sözleşme revizyonu (iki dosya) — kod tarafı tek başına kapatamaz
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

**SÖZLEŞME AYAĞI İNDİ (2026-09-11, dış depo `12beec1`); KOD AYAĞI AÇIK.**

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

**KALAN — kod ayağı, hiç yazılmadı:**
- `brief_doctor` Bölüm C'yi satır düzeyinde okumalı (`no` + `alan`), bugün yalnız yapısal
  sözleşmeyi doğruluyor.
- `auditors.validate_report` `kaynak-iddialari` sütununu tipli okumalı.
- Motor `_alan_bagi_var` yerine iddia bağı kurmalı.
- `EngineInputs` bu veriyi taşımalı (R5 alan kümesi değişikliği → arayüz eki).
- **Ağaçta iki kırmızı test var** (sapma alarmı); ayrıntı ana görevin Open Problems'ında.

**Dürüst etiket:** bu görev KAPANMADI. Sözleşme penceresi kapandı (pin `4636847`), kod
penceresi açık — ama artık pilotu ikinci kez ürettirmeden çalışılabilir.

# Decisions Log

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

- Sözleşme revizyonu İKİ dosyaya dokunur (denetçi + sentez) ve pin yenilenmesi ister; bu
  görevle aynı turda yapılmalı, ayrı ayrı iki pin turu israftır.
