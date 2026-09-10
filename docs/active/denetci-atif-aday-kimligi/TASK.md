---
title: Denetçi atfı ADAYA bağlansın (alan düzeyi yetmiyor)
status: proposed
started: null
finished: null
last-touched: 2026-09-10
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

# Decisions Log

- **2026-09-10 — görev AÇILDI.** Kapanış turunun yüksek bulgusunun KALAN ayağı. Kontrolör
  yamamayı bıraktı ve çerçeve teşhisini kullanıcıya götürdü; bu dosya o teşhisin EVİDİR.
  Dürüst etiket: **çözülmedi, ertelendi, evi BURASI.**

# Open Problems

- Sözleşme revizyonu İKİ dosyaya dokunur (denetçi + sentez) ve pin yenilenmesi ister; bu
  görevle aynı turda yapılmalı, ayrı ayrı iki pin turu israftır.
