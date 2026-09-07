---
title: Araştırma sözleşmesinin çıktı biçimi makine-okunur kesinliğe getirilsin
status: proposed
started: 2026-09-07
last-touched: 2026-09-07
blocked-by: null
source_task: docs/active/sektor-bilgi-paketi-plan2/TASK.md
---

# Goal

Araştırma görev sözleşmesinin **çıktı biçimini** mekanik olarak denetlenebilir kesinliğe getirmek.
Bugün sözleşme bu bölüm için **ne istediğini** söylüyor (`alan/dönem → iddia → kaynak` eşlemesi,
açılabilir tam adres) ama **hangi biçimde yazılacağını** söylemiyor. Serbest düzyazı da uyuyor,
tablo da. Mekanik girdi kapısı bu yüzden serbest düzyazıdan *"bu bir eşleme DEĞİL"* sonucunu
çıkaramıyor — ve çıkaramaz: bu bir semantik-negatif sınıfıdır.

Kapanış yönü: sözleşme bu bölümü **sabit sütunlu bir tablo** olarak istesin. O zaman kapı olumsuz
çıkarım yapmaz, **olumlu bir yapısal sözleşme** sayar (sütun sayısı · hücre doluluğu · adres
biçimi). Emsal: sözleşme özel gün seçimleri için ZATEN tablo istiyor, yani araçlardan tablo
istemek yeni bir kalıp değil.

# Neden ŞİMDİ — zamanlanmış yuva ve iki son tarih

Bu görev bir "son tarih"e değil, **adlandırılmış bir yuvaya** oturur:

**YUVA: Plan 2'nin Task 8'i ile Task 9'u ARASINDA.**

İki bağımsız son tarih var ve ikisi de bu yuvadan sonra geliyor:

1. **Task 9 / Task 10 — denetçi katmanı.** Sözleşme değişikliği denetçi görev metnine de dokunuyor
   (o metin kaynak bölümüne atıf yapıyor). Denetçi girdi paketleyicisi Task 9'da, iki kör denetçi
   orkestrasyonu Task 10'da doğuyor. Sözleşme onlardan SONRA değişirse o görevlerin yazdığı koda
   geri dönmek gerekir.
2. **Task 19 Step 5 — üç araştırmanın tek seferde yeniden üretimi.** Ölçüldü (2026-09-07): bugün
   şu anki sözleşme biçiminde üretilmiş **gerçek çıktı YOK** (dış depodaki dosyalar 2026-07-11
   tarihli, sözleşmenin yürürlükteki sürümü 2026-08-30). Yani değişiklik şu an hiçbir işi çöpe
   atmıyor. Task 19'dan sonra yapılırsa araştırmalar **ikinci kez** ürettirilmek zorunda kalır.

# Current Status

**proposed.** Eray onayı alındı (2026-09-07): "sözleşme değişikliğini ayrı ve küçük bir iş olarak
yapabiliriz". Henüz hiçbir dosyaya dokunulmadı.

**Giriş kapısı bir TASARIM kararıdır, yürütücü işi DEĞİLDİR.** Aşağıdaki iki bedel ürün kararı
taşıyor ve karara bağlanmadan sözleşme metni yazılamaz (bkz. Open Problems).

# Kapsam

**KAPSAM GENİŞLETİLDİ (2026-09-07, checkpoint 6'nın beş turluk zincirinden sonra).**
İlk yazımda kapsam yalnız **Bölüm C** idi. Ölçüldü ki aynı hastalık Bölüm B'de ve belgenin genel
yapısında da var: sözleşme NE istediğini söylüyor, HANGİ KESİNLİKTE yazılacağını söylemiyor;
mekanik kapı tahmin etmek zorunda kalıyor ve tahmin eden her kural kandırılabiliyor. Beş sınır
kuralı beş kez yenildi (2026-09-07, checkpoint 6 tur 1-8) — kapının kendisi kötü olduğu için
değil, dayandığı sözleşme yeterince kesin olmadığı için.

**Eksik olan BİÇİM değil KESİNLİK — dört cümle.** Sözleşme zaten Bölüm B'nin tablosunu
sütunlarıyla tarif ediyor ("dönem + karar + tür etiketi + gerekçe", önce tablo sonra dönemler).
Yazılı OLMAYAN:

1. **Gerekçe tablosunun BAŞLIK SATIRI nasıl yazılacak.** Bugün kapı hangi tablonun o tablo
   olduğunu sezgiselle buluyor; sezgisel yem tabloyla kandırılabiliyor (beş turun konusu).
2. **Bölüm B'de kaç tablo olabilir.** "Tek gerekçe tablosu" yazılı değil; ikincisi konursa
   hangisinin gerçek olduğu doğrulanamıyor.
3. **Markdown BAŞLIK DÜZEYLERİ.** Bölüm B'nin içine konan `##` bir satır bölümü fiilen kesiyor
   (ölçüldü); sözleşme düzey dayatmadığı için kapı bunu meşru bölüm sonu saymak zorunda.
4. **Bölüm C'nin biçimi.** Hiç yazılı değil — serbest düzyazı da sözleşmeye uyuyor, ve
   "bu bir eşleme DEĞİL" sonucu serbest yazıdan makineyle çıkarılamaz. (İlk kayıt bu maddeydi.)

Dördü de aynı türden: **kapının tahmin etmesini bırakıp olumlu bir yapısal sözleşmeyi
doğrulamasını sağlar.** Dördü birlikte yapılmazsa aynı sınıf kalan bölümden yeniden çıkar.

**Bu genişletmenin ek maliyeti ölçüldü ve DÜŞÜK:** dördü de aynı sözleşme dosyasının aynı
"ÇIKTI FORMATI" bölümüne dokunuyor, aynı yeniden-pinleme turunda iniyor ve aynı araştırma
yeniden-üretimini bekliyor. Dar tutup sonra genişletmek araştırmaları ÜÇÜNCÜ kez ürettirir.

Ayaklar — hepsi bu görevin içinde, parçalanmaz:

1. **Dış depodaki araştırma görev sözleşmesi** (`/root/otomaix-sosyal-medya-arastirmasi`):
   kaynak bölümünün biçimi sabit sütunlu tabloya çevrilir.
2. **Denetçi görev metni**: kaynak bölümüne yaptığı atıf yeni biçimle hizalanır.
3. **Monorepo pin manifesti**: sözleşme değişince parmak izi yenilenir ve fail-closed
   doğrulayıcı yeni sürüme bağlanır.
4. **Mekanik girdi kapısı**: kaynak bölümü ailesi olumsuz çıkarımdan **olumlu yapısal sözleşmeye**
   çevrilir; Task 7'de konulan "makineyle doğrulanmadı" kapsam beyanı bu ayak kapanınca KALKAR
   (kalkmazsa beyan bayatlar — bayat beyan, beyan olmamaktan kötüdür).

# Decisions Log

- **2026-09-07 — Eray onayı: sözleşme değiştirilecek, ama Task 7'nin İÇİNDE değil.** Gerekçe:
  Task 7 bir yürütme görevidir ve yürütücü sözleşme metnini yeniden yazmaz; bu tasarım katmanının
  işidir.
- **2026-09-07 — kapının SERTLEŞTİRİLMESİ reddedildi (ölçümle).** Checkpoint 6'nın üç turunda
  ayıraç vekilini sertleştirme yakınsamadı; her tur yeni bir kaçış verdi (son ölçüm:
  `- Düz yazı, devamı https://example.com/kaynak` → `gecti`, 0 not). Serbest düzyazıdan olumsuz
  kanıtlamaya çalışan kapı, bypass ile yanlış-pozitif arasında salınır. Dördüncü bir nokta
  düzeltmesi AÇILMADI.
- **2026-09-07 — "doğrulanmadı" ilanı tek başına yeterli sayılmadı (ölçümle).** Devrin nereye
  gittiği ölçüldü: denetçi sözleşmesinin ilk adımı kaynak başına 3 iddia örnekleyip bağlantıyı
  GERÇEKTEN açıyor — makinenin yapamayacağı, daha güçlü bir kontrol. **Ama örnekleme, mekanik
  kapının işi olan BÜTÜNLÜK sorusunu ("her alan için kaynak gösterilmiş mi") cevaplamıyor.**
  Ayrıca spec'in "mekanik iş dil modeline verilmez" hükmüyle gerilim doğuyor. Bu yüzden ilan
  edildi AMA kök çözüm ertelenmedi, bu göreve bağlandı.

# Open Problems

- **ÜRÜN KARARI — tablo tekrarı ve rapor uzunluğu.** Tablo, aynı kaynağın N iddiayı desteklediği
  yerde N satır ister; rapor uzar. Sözleşme başka bir yerde *"kısa ve yoğun yaz; makale/rapor
  formatına kayma"* diyor. Bu gerilim tasarım turunda karara bağlanmalı — çözüm biçimi (ör. kaynak
  başına gruplama) sözleşme metnini belirler.
- **ÜRÜN KARARI — katı biçim, kalıba oturmayan bulgunun düşürülmesine davet eder.** Sözleşme başka
  bir yerde *"hiçbir başlığa oturmayan ama değerli bulduğun gözlemleri ATMA"* diyor. Tablo dışında
  kalan bir kaynak notunun nereye yazılacağı sözleşmede AÇIKÇA gösterilmeli, yoksa araç sessizce
  düşürür.
- **ÖLÇÜLMEMİŞ, ETİKETLİ — araçların tabloyu ne kadar düzgün ürettiği DOĞRULANMADI.** Şu anki
  sözleşme biçiminde üretilmiş gerçek çıktı olmadığı için ölçülemedi. "Tablo işe yarıyor" İDDİA
  EDİLMİYOR; yalnız "sözleşme zaten bir yerde tablo istiyor, ikincisi yeni bir kalıp değil"
  denebiliyor. İlk gerçek ölçüm Task 19 Step 5'te doğacak.
