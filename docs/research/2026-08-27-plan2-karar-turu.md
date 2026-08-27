---
title: Plan 2 karar turu — kapanan kararlar
status: done
date: 2026-08-27
kaynak: docs/research/2026-08-27-spec-input-bosluk-raporu.md
yontem: Her soru önce spec-input + spec + kaynak sözleşme dosyalarından doğrulanır,
  sonra somut akış/senaryo düzeyinde sunulur (Eray talimatı 2026-08-27).
---

# Plan 2 karar turu

## K-84 — Kalıp kimliği sürümler arası korunacak mı? → **A: KORUNUR**

**Karar (Eray, 2026-08-27):** Sabit kimlik alanı üretilir ve sürümler arası korunur.

**Kararın dayandığı akış:** Kuyumculuk v1'de N kalıp var. Tur koşuyor; sentez ajanı
aktif paketin HER kalıbı için karar üretmek zorunda (sentez sözleşmesi ADIM 2). Ajan
birkaç kalıbı hiç anmazsa — girdinin R-29 riski, *"geçerli sektör hafızası sessizce
kaybolur"* — bunu yakalayacak tek mekanizma motorun karar-kapsamı kontrolüdür. O kontrol
kalıpları sayabilmeyi gerektirir; sayma kimliğe dayanır. Girdi bağı açıkça kuruyor:
*"kimlik yoksa 'tam kapsam' güvenilir biçimde sayılamaz"* (işletime hazırlık listesi md. 8).

**Kararın DEĞİŞTİRMEDİĞİ şey (yanlış çerçeveleme düzeltmesi):** Eşleştirmenin kendisi
zaten tanımlı ve yürürlükte —
- *ölçüt:* denetçi sözleşmesi ADIM 2, "eş anlamlı ifadeleri aynı iddia say
  (makro çekim = macro shot)";
- *yöntem:* sentez sözleşmesi ADIM 1-2, iddia bazında eşleştirme + dört karar.
Eşleştirmeyi sentez ajanı anlam düzeyinde yapıyor. Kimliğin işlevi eşleştirmek değil,
**sentez ajanını bağımsız denetlemek**.

**Doğurduğu teknik kalemler (plan bağlar, Eray onayına sunulmaz — kart hükmü):**
- K-151 kimliğin biçimi · K-152 üretim yöntemi (metin özeti kimlik OLAMAZ — girdi hükmü)
- K-86 kimliğin hangi değişiklik seviyesine kadar korunacağı (`guncelle` ↔ `cikar+ekle`)
- K-154 bu ayrımın karar günlüğünde temsili

**Dürüst not:** Sabit kimlik ve "karar birimi" kavramı dokuz kaynak dosyanın hiçbirinde
yok; sonraki bir ölçeklenebilirlik analizinden geliyor ve yalnız bir hakem belgesinde
bulunuyor (girdi §6.3 statü uyarısı). Karar bu bilgiyle verildi.

## K-23 — Motorun karar veremediği maddeler → **B: güvenli varsayılan + rapor**

**Karar (Eray, 2026-08-27):** Kararsız madde güvenli varsayılana düşer — mevcut kalıp
korunur, madde koşu raporunda ve onay özetinde görünür, aktivasyonu bloklamaz.

**Karar önce A seçilip sonra B'ye çevrildi.** Sebep: ilk sunumum girdinin ÜÇ KADEMELİ
yapısını göstermiyordu. Eray'ın "K-71 zaten blokluyorken girdi neden sormadan geçiyor?"
sorusu eksiği ortaya çıkardı.

**Üç kademe (girdi §7.7 + §19.7 + sentez sözleşmesi çıktı md. 3):**

| Kademe | Ne | Sonuç |
|---|---|---|
| 1 | Mevzuat/güvenlik öğesi doğrulanamıyor veya çelişkili | Koşu bloklanır (ayrı karar — **K-128**, hâlâ açık) |
| 2 | Gerçek çelişki: denetçi uyuşmazlığı · geri-ekleme çelişkisi | Sentez AÇIK SORU üretir → K-71 gereği aktivasyonu bloklar |
| 3 | Motorun sıradan kararsızlığı | Güvenli varsayılan (koru) + rapor — bloklamaz |

**Gerekçe:** 3. kademedeki maddenin zaten güvenli bir çözümü var (kalıbı koru); sessiz
değişiklik oluşmaz, bilgi kaybolmaz. İnsana sormak güvenlik eklemez, yalnız iş ekler.
2. kademede güvenli varsayılan YOKTUR — geçen tur çıkarılmış kalıp için yeni kanıt
geldiğinde korumak da eklemek de esaslı bir seçimdir.

**Kaynağın kendi kaydı:** K-71 kartı bu gerilimi biliyor ve çözmüyor —
*"ikinci hüküm kendi belgesinde K-23 ile gerilimlidir ve orada çözülmez."*

**Yürürlüğe giren varsayılan tablosu (girdi §7.7):** yeni kanıt yok → koru · güncelleme
mutabakatı yok → eski biçimi koru · çıkarma mutabakatı yok → koru · yeni öğe eşiği
geçmiyor → ekleme. Tablonun son iki satırı (mevzuat/güvenlik bloklaması · karar kapsamı
eksikliği) K-23'ün kapsamında DEĞİL: birincisi K-128'e, ikincisi K-84'e bağlı — ikincisi
K-84=A ile artık yürürlükte.

**Ölçülmemiş (İlke 9):** motorun tur başına kaç kararsız üreteceği hiç ölçülmedi; açık
soruların ≤10 tasarım değeri de girdide "ölçülmemiş tasarım değeri" etiketli. Hiçbiri
kapı yapılmadı.

## K-125 — İki denetçi mutabakat kapısı → **BENİMSENDİ** (K-100 ile birlikte)

**Karar (Eray, 2026-08-27):** Kapı benimsenir; bağlı ek görev de alınır.

**Değişen akış:** Bugün denetçiler yalnız yeni araştırma çıktılarını denetliyor; aktif
paket denetim adımına hiç girmiyor (ona ilk kez sentez bakıyor). Kapıyla birlikte
denetçiler her periyodik turda aktif paketin HER karar birimini de tarar ve beş statüden
birini üretir: `supported` · `not_observed` (geçersizlik kanıtı DEĞİL) · `needs_update` ·
`contradicted` · `risk_unverified`. Motor `guncelle`/`cikar` için iki denetçi uyumu arar;
uyuşmazlıkta normal içerikte kalıp korunur, mevzuat/güvenlikte koşu bloklanır.

**Kazanç:** tek denetçinin hatası bir kalıbı paketten çıkaramaz (bugün çıkarabilir —
`cikar` için tek pozitif kanıt satırı yetiyor).

**Yük:** aktif paketin birim sayısı × 2 denetçi × her tur. **Ölçülmemiştir** ve hiçbir
eşiğe çevrilmedi. Yük otomatik denetçi oturumlarına (Claude Code + Codex) biner,
operatörün elle işine değil.

**Bağlı ikili — ikisi birlikte alındı:** K-125 (kapının benimsenmesi) + K-100 (envanterin
denetçi sözleşmesindeki adı ve şeması). Kapı girdisiz kalırsa fiilen çalışmaz; ek görev
kapısız alınırsa boşuna yük olur. K-100 teknik — planın işi.

**Ön koşulu K-84=A ile karşılandı:** ek görev "karar birimi" kavramına dayanıyor.

**Doğurduğu sözleşme işi:** denetçi görev sözleşmesinin YENİ SÜRÜMÜ — beş statülü tablo
mevcut dört bölümlü çıktı sözleşmesine dâhil değil, ayrıca tanımlanmalı.

## K-133 — Kuru mod → **KURULMASIN** (çözüm K-106'ya bağlandı)

**Karar (Eray, 2026-08-27):** Ayrı bir kuru koşu kipi yazılmaz.

**Provenans (Eray sorusu üzerine ölçüldü):** Kuru mod dokuz kaynak dosyanın HİÇBİRİNDE
yok. `claude-sektor-bilgi-paketi-mimari.md:2630`'da `[2026-08-11]` etiketiyle doğuyor —
politika motorunun kendisiyle aynı partiden. İki hakem belgesinden yalnız birinde
(Claude'unkinde) var; Codex'inkinde yok. Girdi bunu R-20 satırında zaten etiketlemiş:
*"Yalnız bir hakemde, sonradan eklenen analiz."*

**Senaryo karşılaştırması (kararın dayanağı):** Kuru modlu ve kuru modsuz akışta
yöneticinin GÖRDÜĞÜ şey aynıdır — iki durumda da aynı özet farka bakıp aynı kararı verir.
Fark yalnız arkada: kuru modsuz akışta reddedilen her tur bir sürüm numarası tüketir ve
akıbeti belirsiz bir `draft` satırı bırakır. Yani kuru mod bir güvenlik önlemi değil,
temizlik önlemidir.

**Gerekçenin Faz 1'de geçersizliği:** Girdinin yazdığı gerekçe R-20 — *"yanlış kural
bütün sektörlere yayılır."* Faz 1'de tek pilot sektör var; motor `active`'e dokunamıyor
(K-28) ve son onay operatörde. R-20'nin diğer iki önlemi (pilotta kalibrasyon, kademeli
genişleme) kuru mod olmadan da duruyor.

**Bağlanan çözüm:** Kuru modun çözdüğü temizlik sorunu **K-106** ile kapatılır. K-106'nın
kartı şunu soruyor: *"Düzeltme yeni bir taslak sürüm mü açacak, mevcut taslağı yerinde mi
güncelleyecek?"* — **yerinde güncelleme** dalı sürüm yakma ve artık-taslak sorununu
doğrudan çözer. K-106 **teknik sahip** kalemidir: planın bağlayacağı karardır, Eray'a
sorulmaz (İlke 8).

**Yeniden açılma koşulu:** Motor ikinci sektöre yayıldığında — o an R-20'nin öncülü
gerçekleşir.

## K-130 · K-131 · K-132 — Üç durdurma bariyeri → **ÜÇÜ DE KURULUR, EŞİKLER BOŞ**

**Karar (Eray, 2026-08-27):** Üç bariyerin de mekanizması Plan 2'de kodlanır; eşik
değerleri politika yapılandırmasında **boş/pasif** kalır ve pilot kalibrasyonundan sonra
doldurulur. Kalibrasyon günü yalnız sayı girilir, kod yazılmaz.

**Üçünün ölçtüğü ayrı şeyler (girdi §7.7):**
- **K-130 değişim büyüklüğü:** `(guncelle + cikar + runtime-etkili-kirp) / mevcut_karar_birimi_sayisi`.
  İlk paket koşusunda payda 0 → oran hesaplanmaz, mutlak limitler kullanılır.
- **K-131 ekleme oranı:** paketin ŞİŞMESİ. K-130'un yakalayamadığı "hiç çıkarma yok ama
  paket büyüyor" vakası. Codex hakem belgesinde `max_add_ratio` diye ADLANDIRILMIŞ,
  değeri verilmemiş.
- **K-132 kararsızlık oranı:** motorun ACZİ. K-23=B ile birlikte anlamlı — tek tek
  kararsızlar operatörü bloklamıyor, motorun toptan çalışmadığı durumu bu yakalar.

**Ölçüm (Eray sorusu üzerine, üç kaynakta arandı — İlke 9):** Hiçbir yerde önerilmiş
sayısal eşik YOK.
- Girdi §7.7: *"Bu bölümde hiçbir sayısal eşik tanımlanmamıştır."*
- Codex hakem 7.7.4: yalnız formül; *"Kesin eşikler kanıtsız seçilmez; kuyumculuk pilotu
  ve ilk kontrollü sektör koşularındaki gerçek diff dağılımıyla kalibre edilir."*
- Claude hakem: *"Motorun kendi karar eşikleri HENÜZ TANIMLANMAMIŞTIR → K-24. Eşik
  uydurulmamalı."* Kök sebep aynı belgede: *"Kaynak dokümanlarda motor hiç yok,
  dolayısıyla hiçbir eşik ölçülmüş değil."*

Sistemdeki tek sayılar sözleşmelerin TASARIM değerleri (mutabakat eşiği `2-3`+, alan
boyut hedefleri, ~6.000 karakter tavanı) — Claude hakem bunları da *"ölçülmüş değil"*
diye etiketliyor. Hiçbiri bariyer eşiği değil.

**K-24 buna bağlı kalır:** eşik değerleri pilot kalibrasyonunda konur; bu karar
değerleri KAPSAMIYOR (İlke 9 — ölçülmemiş sayı kapı yapılmaz).

## K-41 — Onay ekranında çıkarılanlar eşiği → **EŞİK YOK, tam liste ayrıntıda**

**Karar (Eray, 2026-08-27):** Özet "Çıkarılanlar: N" der; bir tık derinde tam liste
gerekçeleriyle açılır. Eşik konmaz.

**Ölçüm:** *"eşik-üstü çıkarmalar"* ifadesi hakem belgelerinde altı yerde geçiyor ama
**bir çıkarmayı ne zaman "eşik üstü" saydığımızı tanımlayan hüküm hiçbir katmanda yok** —
ne boyut (mutabakat gücü / alanın mevzuat hassasiyeti / kalıbın yaşı) ne değer. Eşik
seçmek ikisini birden uydurmayı gerektirirdi (İlke 9).

**Faz 1 gerçeği:** pilot paketinde kalıp sayısı düşük; tam liste zaten kısa. Eşik fikri
ölçek modelinden geliyor.

## K-42 — Sinyal odaklı özet → **SIRALAMA İLKESİ + AKTİVASYON SÜRESİ METRİĞİ**

**Karar (Eray, 2026-08-27):** (a) Özet, riskli sınıfları — geri-ekleme çelişkileri ·
motor kararsızları · çıkarmalar — nötr sayıların ÖNÜNE koyacak biçimde tasarlanır.
(b) Onaya kaç saniyede basıldığı kaydedilir.

**Kaynak:** R-21 riski — *"yönetici özet diff'i onay tıklamasına indirger; tek insan
checkpoint'i işlevsiz kalır."* Karşı önlem *"sayı değil sinyal"*; tespit göstergesi
*"aktivasyon süresi metriği (saniyeler → rubber-stamp sinyali)."*

**Bilinçle DIŞARIDA bırakılan:** geçmişe karşı anormallik tespiti ("çıkarma sayısı son
dört turun ortalamasının üç katı" gibi). Gerekçe ölçülmüş: karşılaştırma geçmiş ister;
ilk turda geçmiş yok, tur periyodu 6 ay (K-149). Sabit eşik alternatifi ölçülmemiş.
**Yeniden açılma koşulu:** yeterli tur geçmişi biriktiğinde.
**Not:** K-41=B kararıyla "eşik-üstü çıkarmalar" sinyal kümesinden zaten düştü.

## K-134 — Motor devreye girerken eski onay akışı → **PİLOTTA PARALEL, SONRA TEK GEÇİŞ**

**Karar (Eray, 2026-08-27):** Pilot turlarında operatör önce sentezin kendi çıktısına
(karar günlüğü + açık sorular) bakıp yargısını kaydeder, sonra motor koşar ve ikisi
karşılaştırılır. Kalibrasyon kanıtı yeterli görülünce paralel akış kalkar, motor tek yol olur.

**Neden gerekli:** Spec §15.2 pilotun ölçüm yükümlülükleri arasında *"motor kalibrasyon
karşılaştırma verisi — motorun kararları × insan yargısı"* sayıyor. Paralel akış o veriyi
üreten mekanizmadır; tek geçişte kalibrasyon yükümlülüğü mekanizmasız kalırdı.

**Not:** Ortada korunacak canlı bir "eski akış" YOK — sistem hiç tur koşmadı. "Eski akış"
sözleşmelerin tarif ettiği motorsuz modeldir. **Bu karar spec'e hiç geçmemişti** (boşluk
raporu, A grubu).

**Bağlandığı açık kapı:** K-37 (kalibrasyon kanıtı ölçeğe geçişin koşulu olacak mı) —
genişleme turunda kapanır.

## K-01a · K-146 · K-147 — Takvim eklemeleri → **ÜÇÜ DE EKLENSİN**

**Karar (Eray, 2026-08-27):** 10 Kasım · 24 Kasım Öğretmenler Günü · okula dönüş dönemi
sistem takvimine eklenir.

**Neden karar gerekliydi:** Motorun zorunlu kontrolü — *"Özel gün anahtarı: sistem
listesinde karşılığı yoksa pakete girmez, günlüğe notlanır."* Üçü de bugün takvimde YOK
(ölçülmüş olgu, üç katmanda kayıtlı), dolayısıyla araştırma önerse bile pakete giremezlerdi.

**Kalemler:**
- **K-01a — 10 Kasım:** `anma` türünün kaynaktaki ana örneği. Eklenmesiyle `anma`
  davranışı (kutlama ve satış dili yasak; yalnız saygı çerçevesi veya `içerik-önerilmez`)
  gerçek bir günle gösterilebilir hale gelir.
- **K-146 — 24 Kasım Öğretmenler Günü:** sabit gün, `anma` bağı yok. Takvime tek satır.
- **K-147 — okula dönüş:** **gün değil DÖNEM.** Takvim kaydının dönem taşıyabilmesi
  gerekiyor → Plan 2'de migration kalemi. Şema değişikliği tüm sektörlere yarar.

**Vade (kartlarda yazılı):** "Paket taslağı yazılmadan önce" — pilot ilk `draft`ı yazmadan
kapanmaları gerekiyordu, kapandı.

**Ek iş:** K-01a kartı not düşüyor — eklenirse takvim beslemesinin yıllık işine de işlenmeli.

---

# Karar turu kapanışı

**Kapanan Eray-seviyesi kararlar (13):** K-84 · K-23 · K-125 · K-133 · K-130 · K-131 ·
K-132 · K-41 · K-42 · K-134 · K-01a · K-146 · K-147

**Sorulmayan, çünkü cevabı kaynakta bağlı (6):**
- K-11(a) · K-11(b) · K-12 · K-13 — spec §1.3 isim isim sayıyor: *"Ölçülmemiş ve kapıya
  çevrilmeyecek değerler (İlke 9) … Hiçbiri kabul kriteri, eşik veya ölçüm kapısı
  yapılmaz."* Pilotta ölçülür, kapı yapılmaz.
- K-17 — kart blok sınıfı *"Spec içinde teknik olarak çözülür — dizin ve dosya
  sözleşmesidir"*, önerisi A. Plan bağlar.
- K-14 — kart blok sınıfı *"resmî hakem turu yordamı yazılırken gerekli; veri modelini ve
  üretim hattını etkilemez."* Plan bağlar.

**Sorulmayan, çünkü Plan 2'yi etkilemiyor (6):** K-32 · K-33 · K-34 · K-35 · K-36 · K-37 —
altısının da blok sınıfı *"Bloklamaz — Faz 2'ye geçiş kapısıdır; Faz 1 spec'ini
etkilemez."* Pilot sonrası genişleme turunda kapanır.

**Verilen cevapların kaynakla tutarlılığı (ölçüldü):** 13 kararın hiçbiri kaynakta yazan
bir öneriyle çelişmiyor. Kartların çoğunda öneri alanı boş ve *"bu sentez taraf tutmaz"*
yazılı; K-23 ise kaynağın kendi önerisiyle birebir aynı çıktı. Çelişseydi karar yine
geçerli olurdu — emsali K-22 ve K-71'de var: *"Yön, belgedeki önerinin tersidir; öneri
sentez değerlendirmesiydi, karar ürün sahibinindir."*

**Plan 2'nin bağlayacağı teknik kalemler (Eray onayına sunulmaz — İlke 8):** K-151 · K-152 ·
K-86 · K-154 (kalıp kimliği ailesi, K-84=A ile doğdu) · K-100 (denetçi envanteri şeması) ·
K-106 (yerinde güncelleme — kuru modun yerine) · K-17 · K-14 · K-24 (ölçüm mekanizması,
değer değil) · K-74 · K-75 · K-76 · K-78 · K-83 · K-87 · K-88 · K-89 · K-90 · K-91 · K-92 ·
K-93 · K-94 · K-95 · K-96 · K-97 · K-98 · K-99 · K-103 · K-107 · K-108
