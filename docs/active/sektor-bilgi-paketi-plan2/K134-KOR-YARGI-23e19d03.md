---
task: sektor-bilgi-paketi-plan2
adim: K-134 kör yargı (ikinci koşu, yeni araştırmalar)
kosu: kosu-23e19d0382b945a1bee2176239185b91
sektor: kuyumculuk
tarih: 2026-09-23
kaynak: sentez/kosu-23e19d03.../01-SENTEZ-CIKTISI.md §3 AÇIK SORULAR (10 soru)
onceki_yargi: K134-KOR-YARGI.md (kosu-222706dc, 2026-09-19)
---

# Operatörün kör yargısı — kosu-23e19d03

**Körlük koşulu:** motor bu yargı kaydedilmeden KOŞMADI. Sorular operatöre tek tek, K1/K2/K3
etiketiyle (model adı verilmeden) soruldu; sentezin eğilimi "doğru cevap değil" etiketiyle
gösterildi; Claude öneri VERMEDİ. Operatörün isteğiyle (2026-09-23) her soru, paketin üretimde
nasıl kullanıldığını gösteren örnek senaryoyla soruldu — senaryo `sector_packages.render_package_block`
/ `render_special_day_lines`'tan okundu; modelin satırlara uyumu ÖLÇÜLMEDİ.

**Bu koşunun bağlamı:** aynı gün ilk koşu (`kosu-2851dc22…`) sayaç kusuru yüzünden bırakıldı
(10 soru 30 sayılmıştı; düzeltme `3fc7ad8`). Bu koşu aynı brief ve aynı üç kaynakla açıldı.

---

## Soru 1 — İndirim öncesi fiyatın referans süresi

**Yargı: `Süre yazılmasın`.** Madde genel kalır: indirim öncesi fiyat mevzuata uygun gösterilir,
gün sayısı verilmez.

Kanıt (soruda gösterilen): K1 30 gün (2024 kılavuzu) · K2 ve K3 10 gün (1 Ağustos 2026'dan
itibaren). D1#50: "K2#29 resmî ve tarihli (2026-09-02) Bakanlık yayınında 10 gün kuralı
doğrulandı; K1'in 30 günü 2024 kılavuzundan geliyor ve güncel değil." (uyarla) · D2#59: Bakanlık
açıklaması "1 Ağustos 2026'dan itibaren 10 günü doğrular." (uyarla). Sentezin eğilimi: 10 gün.
Pakette yazılı olan (`yasaklar_ve_hassasiyetler[3]`): 10 gün.

**Karşılaştırma notu:** operatör iki denetçinin de doğruladığı değeri değil, daha genel bir
biçimi seçti; motor bu satırda çelişki sınıfı yüzünden açık soru açarsa fark bu tercihten doğar.

---

## Soru 2 — Getiri dili yasağının hukuki dayanağı

**Yargı: `SPK çerçevesi`** — dil kuralı kalır VE "izinsiz yatırım tavsiyesi SPK mevzuatınca suç
sayılabilir" çerçevesi eklenir, **doğrulanmadığı notuyla birlikte** (19 Eylül Soru 1 ile aynı yön).

Kanıt (soruda gösterilen): dil kuralının kendisi 3-3 (D1#52 `al`, D2#60 `uyarla`). Dayanak
çelişki sınıfında: K1#21 (avukatlık bürosu blogu, tarih-yok) ve K3#5 (SPK "İzinsiz Sermaye
Piyasası Faaliyetleri" sayfası, tarih-yok) SPK suçu der; K2#33 SPK duyurusunun hisseye özgü
olduğunu, K2#32 yanıltıcı reklamı (Reklam Kurulu 371. toplantı) dayanak gösterir. D1#53
(açık-soru): "fiziki altına uygulanabilirlik doğrulanmadı." · D2#61 (açık-soru): "K2'nin kapsam
ayrımı daha sağlamdır." Sentezin eğilimi: dayanak adı vermeden kalsın.

**Karara eşlik etmesi ZORUNLU zayıflık:** iki denetçi de SPK kuralının fiziki altına
uygulandığını doğrulayamadı; paket bu cümleyi taşıyacaksa yanında doğrulanmamışlığı da durur.

---

## Soru 3 — Bekleyen hukuki kalemler (dört ayrı yargı)

| Kalem | Yargı | Soruda gösterilen kanıt |
|---|---|---|
| 3a birim/gram fiyatı görünürlüğü | **Girsin** | Yalnız K3#6 (Bakanlık sayfası, tarih-yok, URL örneklenmedi). D1#55 `uyarla` · D2#66 `açık-soru` |
| 3b MASAK 185.000 TL kimlik tespiti | **Paket dışı** (işletme uyumu) | Yalnız K1#22-23. D1#56 `alma` ("işletme uyum yükümlülüğü") · D2#62-63 `açık-soru` (URL açılamadı, muhtemel-uydurma) |
| 3c online satışta 14 gün cayma + kişiye özel istisnası | **Girmesin** | Yalnız K1#24-25 (hukuk bürosu blogu, tarih-yok, muhtemel-uydurma). D1#57 `açık-soru` ("fiyatı finansal piyasaya bağlı mal" istisnası yok) · D2#64-65 `açık-soru` |
| 3d ceza aralığı 108.370–39.916.524 TL indirim maddesine | **Eklenmesin** | K3#34; D1#51 `uyarla` (aralık doğrulandı; marka adlı emsal ham katmanda) · D2#68 `uyarla` · D2#67/69 `açık-soru` |

Sentezin eğilimi: MASAK paket dışı; cayma ve birim fiyat asıl kaynakla yeniden doğrulansın;
ceza aralığı teyit edilirse eklensin.

**Kalibrasyon notu:** 3a'da operatör tek kaynaklı (`tekil`) ve bir denetçinin açık soru saydığı
maddeyi pakete aldı — motor tekil birimi kabul eşiğinden geçirmezse fark bu tercihten doğar.
Senaryoda gösterilen ölçülmüş olgu: `yasaklar_ve_hassasiyetler` kanal süzgecinden GEÇMEZ
(`render_package_block` yalnız `cta_kaliplari`'nı süzer) — giren her yasak satırı her markaya gider.

---

## Soru 4 — 8 Mart Dünya Kadınlar Günü

**Yargı: `Kutlama olarak girsin`.** Paket `dunya-kadinlar-gunu` anahtarını `kutlama` türüyle
taşır; satış çağrısı yasağı kullanıcı isteğinin üstündedir (`render_special_day_lines`, K-119).
**Görsel vurgu yuvası:** kaynaksız (iki denetçide tekil) — operatör eklemesi mi boş mu,
SORULMADI; düzeltme turunda ele alınır.

Kanıt (soruda gösterilen): K1 ve K2 `kutlama`, K3 `ticari-firsat` (gerekçe K3#19, bir marka
kampanya sayfası). D1#70 (açık-soru): "İki rapor satış baskısını uygunsuz buluyor … kutlama ya
da karma etiketi önerilir." · D2#87 (açık-soru): "Kutlama ve ticari fırsat tercihleri ayrışır."
· D2#88 (kanca, 3-3, uyarla): "kadın gücünü satın alma eylemiyle özdeşleştirme çıkarılmalıdır."
Sentezin eğilimi: `kutlama`, satışsız CTA. Paketteki üç dönem (anneler-gunu · sevgililer-gunu ·
yilbasi) `ticari-firsat`.

---

## Soru 5 — Ramazan ve Kurban Bayramı

**Yargı: `İkisi de girsin (karma)` — operatör eklemesi olarak.** Tür `karma` (satış yasağı
YOK; yasak yalnız `kutlama`/`anma`'da çalışır — `_RESPECT_TYPES`, ölçüldü). Kaynak bağı
kurulamaz; kayıt "operatör eklemesi, kaynak bağı zayıf" olarak durur.

Kanıt (soruda gösterilen): yalnız K3 seçti (`karma`), tek dayanak K3#30 — tarih-yok AA haberi,
URL başlığı düğün sezonu. K2 ikisini de eledi ("Kuyumculuğa özgü doğal bir karar anı
değildir"); K1 değerlendirmedi. D1#45/#90 (açık-soru): "muhtemel-uydurma notu … 'birikim'
ifadesi yatırım dili riski"; D1#92-93 Kurban `alma` ("kendi Bölüm C satırı yok"). D2#106-111
hepsi `açık-soru`, muhtemel-uydurma. 19 Eylül yargısı: "İKİSİ DE GİRSİN — operatör eklemesi".
Sentezin eğilimi: hedefli kaynak araştırması; "birikim" dışarıda kalsın.

**Açık kalan ayrıntı (SORULMADI):** "birikim" ifadesinin dışarıda kalıp kalmayacağı; 19 Eylül'de
kaydedilen "görsel kurgu yazısız" kısıtı (`caption_generator` metin yasağı) bu turda da geçerli.

---

## Soru 6 — 24 Kasım Öğretmenler Günü

**Yargı: `Ticari fırsat olarak girsin`** (K1'in seçtiği tür; satış serbest).

Kanıt (soruda gösterilen): yalnız K1 seçti (`ticari-firsat`), tek dayanak K1#16 — "Anneler Günü"
etiketli kuyumcu satış sayfası. K2 eledi ("yüksek değerli hediye çağrısı ayrıca etik hassasiyet
yaratabilir"); K3 seçmedi. D1#47/#94 `açık-soru` ("güçlü değil"), D1#95 CTA `alma` ("Kamu
görevlisine değerli hediyeyi teşvik etmek etik risk taşıyor"). D2#116-120 muhtemel-uydurma;
D2#119 veli ortak hediye CTA'sı `alma`. Sentezin eğilimi: elensin ya da yalnız satışsız
`kutlama` ile yeniden araştırılsın.

**Açık kalan ayrıntı (SORULMADI):** denetçilerin `alma` dediği iki CTA (D1#95 e-ticaret/WhatsApp
sınıf hediyesi · D2#119 velilerin ortak mücevher hediyesi) dönem girerse hangi CTA'yla girer —
düzeltme turunda ele alınır. **Kalibrasyon notu:** operatör iki denetçinin de etik risk işaretlediği
dönemi ticari türle aldı; motor tekil/kanıtsız dönemi almazsa fark bu tercihten doğar.

---

## Soru 7 — Babalar Günü ve 29 Ekim (iki yargı)

**7a Babalar Günü — Yargı: `Özel gün olarak girsin`** (`ticari-firsat`; bugün yalnız takvim teması).
Görsel vurgu kaynaksız — operatör eklemesi mi boş mu SORULMADI. Kanıt: K2 ve K3 `ticari-firsat`
seçti, K1 değerlendirmedi; görsel vurgu D1#86 `uyarla` ("K3'ün kodları bağsız … gravür yazısı
nedeniyle metin-öğesi riski") · D2#104 muhtemel-uydurma.

**7b 29 Ekim — Yargı: `Kutlama olarak girsin`** (satışsız; sikke yazısız/kenardan — D1#89).
19 Eylül Soru 7 ile aynı yön. Kanıt: yalnız K2 seçti (`kutlama`), dayanak K2#45 resmî ve tarihli
ama URL örneklenmedi → K-126 istisnası açılmadı. D1#88 satışsız CTA `al` ("Kutlama türünde CTA
sızması yok"); D2#112-115 `uyarla`, muhtemel-uydurma. Sentezin eğilimi: K2#45 canlı
doğrulansın; doğrulanırsa satışsız `kutlama`.

**Kalibrasyon notu:** iki dönem de tekil kaynaklı; motor K-126'yı açamadığı için bunları almazsa
fark operatörün tekil kanıtı yeterli saymasından doğar (19 Eylül'de de aynı yön).

---

## Soru 8 — Duygusal açılış kancaları

**Yargı: `İkisi de girsin`** — kanca listesi 2 teknik açılış + tören/teslim anı + kararsızlıktan
stil/kategori seçimine geçiş.

Kanıt (soruda gösterilen): denetçiler hangi kancanın güçlü olduğunda TERS düştü. Tören/teslim:
D1#16 2-3 `al` ("K3#12 takı töreni kaynağı yerel ve özgü") · D2#25 tekil `uyarla` (tarihsiz,
muhtemel-uydurma, sosyal kanıt koşullu). Kararsızlık: D1#19 tekil `uyarla` ("başka sektörde
sırıtmaz; AA haberi güçlü değil") · D2#21 3-3 `uyarla` ("garantili duygusal sonuç iddiasından
arındırılmalıdır"). Sentezin eğilimi: ikisi birlikte.

---

## Soru 9 — İki CTA kalıbı

**Yargı: `İkisi de girsin`** — bütçe/ayar/gramaj karşılaştırması (aciliyet ve yatırım dili
ayıklanmış) + özel gün için kişiye özel tasarım ve erken sipariş. Havuz 4 → 6.

Kanıt (soruda gösterilen): iki kalıpta da denetçiler aynı biçimde ayrıştı (D1 tekil, D2 2-3).
Karşılaştırma: D1#11 `uyarla` ("K2#7 … AA haberi (2025-02), güçlü değil → muhtemel-uydurma") ·
D2#17 `uyarla` ("sınırlı işçilik fırsatı ve güvenli yatırım vaadi çıkarılmalıdır"). Tasarım/erken
sipariş: D1#10 `uyarla` ("Güçlü kaynak yok … kalıp yine de sektörde makul") · D2#18 `uyarla`
("hizmet ve teslim süresi doğrulanarak … soyut değişkenlere çevrilmelidir"). Sentezin eğilimi:
karşılaştırma alınsın, tasarım/erken sipariş beklesin.

Senaryoda gösterilen ölçülmüş olgu: bugünkü 4 CTA'nın 3'ü kanal etiketli; kanal kaydı olmayan
bir markaya YALNIZ 1 CTA gider (`filter_channel_dependent`). İki yeni kalıp kanal etiketsiz.
**CTA havuzu ölçümü (Open Problems "ilk turda ölçülecekler"):** sentez adayı 4 kalıp
(brief ≥ 5 ister); aynı girdiyle sabahki sentez (`kosu-2851dc22`) 6 üretmişti.

---

## Soru 10 — Kuyuma özgü ama dış kanıtsız kalıplar (iki yargı)

**10a hizmet CTA'ları — Yargı: DÖRDÜ DE girsin, operatör eklemesi olarak:** ölçülendirme ·
taklas · bakım/onarım ("ücretsiz" vaadi OLMADAN) · doğum/mevlüt için kulplu çeyrek/bebek altını
danışması. Hepsi kanal etiketli (mağaza / WhatsApp / randevu) — yalnız o kanalı kayıtlı markaya
gider. Kanıt: D1#6/#7/#8 2-3 `uyarla` "dış kanıt yok" (taklas: "brief'te geçen, kuyuma çok özgü
bir hizmet"; bakım: "'ücretsiz' vaadi markanın gerçek hizmetine bağlanmalı") · D1#13 tekil
`uyarla` ("Türkiye'ye özgü güçlü bir kültürel kalıp; ancak kaynaklar zayıf") · D2#12/#13/#14/#16
`açık-soru` · D2#15 "ücretsiz bakım" `alma`.

**10b görsel kodlar — Yargı: ÜÇÜ DE girsin, operatör eklemesi olarak:** telkari/ajur işçilik +
22 ayarın sıcak tonu · Darphane damgalı ziynet/çeyrek (YAZISIZ açıdan — kenar/yüzey) ·
doğal–laboratuvar pırlanta karşılaştırması. Kanıt: D1#31 tekil `uyarla` ("Türkiye'ye özgü bir
ürün dokusu") · D1#32/D2#41 tekil `uyarla` (damga görselde metin üretir → yazısız) · D1#30 tekil
`açık-soru` ("24.06.2026 ibare zorunluluğu varken, etiketsiz karşılaştırma görseli ayrımı
gösteremez") · D2#38 tekil `uyarla`. 19 Eylül Soru 3 ile aynı yön (yerel görsel kodlar operatör
eliyle). Bağlam: paketin bugünkü `gorsel_kodlar` metni tümüyle uluslararası katalog terimi.

**Karara eşlik etmesi ZORUNLU zayıflık:** doğal–lab karşılaştırma sahnesinde "sentetik" ibaresi
görselde YAZILAMAZ (metin yasağı) — D1'in itirazı yerinde durur; ibare gönderi metninde taşınmalı.

**SORULMADI — araştırma katmanının kusuru, operatör kararı değil (19 Eylül Soru 9 gibi):** K3'ün
Bölüm C'ye bağlı olmayan görsel/video/görsel-vurgu kodları; 10 Kasım ve Kurban için C satırı
yok (Kurban Soru 5'te operatör eklemesi olarak karara bağlandı). Operatör itiraz etmedi.

---

# Özet

| # | Konu | Yargı |
|---|---|---|
| 1 | İndirim öncesi fiyat referansı | Süre yazılmasın |
| 2 | Getiri dili dayanağı | SPK çerçevesi (doğrulanmadı notuyla) |
| 3a | Birim/gram fiyatı görünürlüğü | Girsin |
| 3b | MASAK 185.000 TL | Paket dışı |
| 3c | Online cayma hakkı | Girmesin |
| 3d | Ceza aralığı | Eklenmesin |
| 4 | 8 Mart | Kutlama olarak girsin |
| 5 | Ramazan + Kurban | İkisi de girsin (karma, operatör eklemesi) |
| 6 | 24 Kasım Öğretmenler Günü | Ticari fırsat olarak girsin |
| 7a | Babalar Günü | Özel gün olarak girsin (ticari-firsat) |
| 7b | 29 Ekim | Kutlama olarak girsin (sikke yazısız) |
| 8 | Duygusal kancalar | İkisi de girsin |
| 9 | Karşılaştırma + tasarım/erken sipariş CTA | İkisi de girsin |
| 10a | Hizmet CTA'ları (4) | Dördü de girsin (operatör eklemesi) |
| 10b | Görsel kodlar (3) | Üçü de girsin (operatör eklemesi) |

**Açık kalan ayrıntılar (SORULMADI, düzeltme turunda):** 8 Mart ve Babalar Günü görsel vurgu
yuvası (operatör eklemesi mi boş mu) · Ramazan/Kurban'da "birikim" ifadesi · Öğretmenler
Günü'nde denetçilerin `alma` dediği iki CTA.

# Kapanış

**K-134 körlük koşulu KARŞILANDI:** yargılar motor çıktısı MEVCUT DEĞİLKEN verildi (2026-09-23).
**Sıradaki iş:** `katman1` → `motor --run-id kosu-23e19d03…`, ardından bu yargılarla motorun
kararlarının karşılaştırması (`K134-MOTOR-KARSILASTIRMA.md` biçiminde).

**Karşılaştırmayı okurken dikkat:** yargıların çoğu motorun göremeyeceği girdiye dayanıyor —
operatör eklemeleri (5, 10a, 10b), tekil kanıtı yeterli sayma (3a, 6, 7a, 7b) ve operatör tercihi
(1, 2, 4). Motor bu satırlarda `açık-soru` ya da ret üretirse bu motorun HATASI DEĞİLDİR; fark
raporunda sebep ayrıca yazılmalıdır.

---

# Motor karşılaştırması (yargı kaydedildikten SONRA koşuldu, 2026-09-23)

**Sıra:** `katman1` PASS (`pytest tests/prompt_regression/ -q @ 1892375` — 124 passed; actor
`eray`, Eray onayıyla) → `motor --run-id kosu-23e19d03…` (politika ayarı YOK, K-24) → **`blocked`**.

**Motorun raporu:** 14 bulgu (9 `bayrak_kaydi` — operatör denetimi için, bloklamaz · 5
`acik_soru`) · 15 açık soru kimliği (5 motor birimi + sentezin 10 sorusu) · 14 uygulanmayan karar.

| Alan | Sentez kararı | Motorun uygulamadığı | Sebep |
|---|---|---|---|
| `cta_kaliplari` | 4 | 2 (`cta[2]` karar sorusu+ayar/gramaj · `cta[3]` ürün+ayar/gram) | `kanit-turu-yetersiz` (K-129 risk sınıfı) |
| `kanca_kaliplari` | 2 | 1 (`kanca[0]` 14 ayar mı 22 ayar mı) | `kanit-turu-yetersiz` (K-129) |
| `video_kodlar` | 8 | **8 (tamamı)** | `referans-uyusmuyor` |
| `yasaklar_ve_hassasiyetler` | 4 | 2 (yetki belgesi m.11/2-b · indirim 10 gün) | `iddia-alani-uyusmuyor` · `celiski` |
| `ozel_gun` | 15 | 1 (`sevgililer-gunu/cta`) | `kanit-turu-yetersiz` (K-129) |
| kapsam · ton · görsel · takvim | 1·1·1·5 | 0 | — |

**Yargıyla karşılaştırma:**
- **Tek doğrudan örtüşme — Soru 1 (indirim):** motor `celiski` ile açık soru açtı (sentez önceden
  bildirmişti); operatör "süre yazılmasın" dedi. İkisi de maddeyi operatöre bıraktı; operatör
  somut bir düzeltme seçti.
- **Ters yön — Soru 8/9:** operatör kanca ve CTA havuzunu BÜYÜTTÜ (+2 kanca, +2 CTA, +4 hizmet
  CTA'sı); motor mevcutları "ayar" kelimesi yüzünden DÜŞÜRDÜ (CTA 4 → 2, kanca 2 → 1). Kalan iki
  CTA kanal etiketli (mağaza · randevu) → kanal kaydı olmayan markaya motor sonrası **0 CTA**.
- **Operatör eklemeleri (motorun göremeyeceği girdi):** Soru 4, 5, 6, 7a, 7b, 10a, 10b, 3a — motor
  bunlar hakkında karar üretmedi (sentez adayında yoktular); fark motorun hatası DEĞİL.
- **Motorun operatöre sorulmadan düşürdükleri:** yetki belgesi maddesi (iki denetçi de canlı
  DOĞRULADI, D1 3-3 · D2 2-3) `iddia-alani-uyusmuyor` ile; 8 video kodu `referans-uyusmuyor` ile.

**"İlk turda ölçülecekler" (Open Problems) — dördü de ölçüldü:**
1. **9 sütun / `[C: …]` geri bağlantı isabeti:** brief-doctor geri bağlantı notları 25 · 5 · 28
   (K1 · K2 · K3). Aşağı akış etkisi ÖLÇÜLDÜ: 8 video kodu + yetki belgesi maddesi atıf/alan
   uyuşmazlığıyla uygulanmadı — aynı kök (madde başka alanın kaynak satırını gösteriyor).
2. **brief-doctor not sayısı:** 29 · 5 · 33 (22 Eylül ile birebir — kaynaklar aynı, kontrol deterministik).
3. **K-129 risk sınıfı:** 20 içerik maddesinden **4'ü** (cta[2] · cta[3] · kanca[0] ·
   sevgililer-gunu/cta) — **dördü de "ayar" anahtar kelimesiyle**, yalnız biri ayrıca rakam taşıyor.
   Beklenti "rakam kuralı" idi; ölçülen tetik kelime listesidir (`MEVZUAT_ANAHTAR_KELIMELERI`
   içinde `ayar`). Bu turda kelime-parçası (substring) yanlış eşleşmesi GÖRÜLMEDİ; eşleşme alt-dizi
   araması olduğu için ("hazırlayarak" ⊃ "ayar") risk olarak durur — ölçülmedi.
4. **CTA havuzu ≥ 5:** sentez adayı 4 (sabahki sentez aynı girdiyle 6); motor sonrası 2.

---

# Düzeltmelerden sonra (aynı gün, yazmadan yeniden oynatma)

Yukarıdaki motor karşılaştırması `218c886` · `f9443c7` · `6fd7416`'dan ÖNCEKİ motorla yapıldı (DB'deki
sonuç da o motorun ürünüdür). Üç düzeltmeden sonra bu koşunun girdileriyle motor, veritabanına
YAZILMADAN yeniden oynatıldı:

| | Önce (DB'deki özgün sonuç) | Sonra |
|---|---|---|
| `referans-uyusmuyor` (8 video kodu) | 8 | 0 (7'si uygulandı; 8.'si "360-degree" K-129 revizyonuyla uygulandı) |
| `kanit-turu-yetersiz` (K-129) | 4 | 0 |
| Motorun kendi açık sorusu | 5 | 1 (indirim maddesi çelişkisi — Soru 1) |
| Uygulanmayan karar | 14 | 2 (yetki belgesi bağ hatası · indirim çelişkisi) |

**Karşılaştırmaya etkisi:** "Ters yön — Soru 8/9" satırı artık geçersiz: motor 'ayar' yüzünden CTA ve
kanca DÜŞÜRMÜYOR; kanal kaydı olmayan markaya giden CTA sayısı da 0 değil. Yetki belgesi maddesi yeni
sentez kapısıyla düzeltme hakkını kullandırır (bu koşu o kapıdan önce üretildi).
