---
task: sektor-bilgi-paketi-plan2
adim: Plan Task 19 Step 7 (K-134 kalibrasyon tabanı)
kosu: kosu-222706dc643b4b64b66a1f3826f02c1b
sektor: kuyumculuk
tarih: 2026-09-19
kaynak: sentez/kosu-222706dc.../01-SENTEZ-CIKTISI.md §3 AÇIK SORULAR
---

# Operatörün kör yargısı

**Körlük koşulu:** motor bu yargı kaydedilmeden KOŞMADI. Yargı yalnız sentez
çıktısına bakılarak verildi. Sentezin her sorudaki kendi eğilimi operatöre
"doğru cevap" olarak sunulmadı (HANDOFF risk maddesi).

**Kapsam ayrımı (2026-09-19 oturumu):** sentezin 10 açık sorusu kapsamlarına göre
üçe ayrıldı. Yalnız Grup A gerçekten bu sektörün kararıdır.

- **Grup A — kuyumculuğa özel (4):** SPK/yatırım dili · taksit sınırı · yerel görsel
  kodlar · düğün-nişan ve mevlüt dönemleri.
- **Grup B — Türkiye takvimi, tüm sektörleri ilgilendirir (3):** Ramazan-Kurban ·
  yılbaşı · 23 Nisan ve 29 Ekim. Bir kez karar verilir; bugün bu kararın oturacağı
  ortak bir ev YOKTUR (ölçüldü: `policy_config.PolicyConfig` yalnız oran/limit
  eşikleri ve `block_on_legislation` taşır; duran cevap alanı yok).
- **Grup C — hattın kusuru, operatör kararı değil (3):** kaynağın boş bıraktığı
  alanlar · CTA alt sınırı · kök rehber nüanslarının kaybı (bu üçüncüsü içinde bir
  ürün kararı taşır, ayrıca sorulacak).

---

## Soru 1 — SPK kapsamı / yatırım dili

**Yargı: `Dil kuralı + geniş çerçeve`.**

Dil kuralı ("kazandırır / değer kaybetmez / yatırımdır" kullanılmaz) pakette kalır
VE Kaynak-1'in geniş hukuki çerçevesi (SPKn m.109 kuyum reklamını kapsar, 2-5 yıl
hapis) `yasaklar_ve_hassasiyetler` alanına yazılır.

**Karara eşlik etmesi ZORUNLU zayıflık — karar günlüğüne birlikte işlenir:**

- Kaynak-1'in dayanağı `K1#6` (avukatlık bürosu blogu, `tarih-yok`). Denetçi-1 o
  sayfayı CANLI açtı ve `KAYNAKTA YOK` yazdı: sayfa m.109'u "izinsiz faaliyet,
  2-5 yıl hapis" olarak anlatıyor; iddianın **"izinsiz yatırım tavsiyesi" çerçevesi**
  ve **5.000-10.000 gün adli para cezası** sayfada GEÇMİYOR.
- Kaynak-2 sınırı daraltıyor (yanıltıcı reklam riski; SPK ancak kişiye özel
  danışmanlıkta) ve dayanağı düzenleyicinin KENDİ sayfası (`spk.gov.tr`).
- Kaynak-3: kuyumculara özel emsal ceza **doğrulanamadı**.
- İki denetçi de `çelişki` + `uyarla` dedi; Denetçi-2: "geniş yorum
  **doğrulanmamıştır**".

**Operatör bunu bilerek seçti** (daha temkinli yön tercihi). Paket bu iddiayı
taşıyacaksa yanında doğrulanmamışlığı da duracaktır.

---

## Soru 2 — Kuyum harcamasında taksit sınırı

**Yargı: yasak satırı GİRER (operatör doğrulamasıyla), taksit CTA kalıbı GİRMEZ.**

**Açık soru operatör tarafından KAPATILDI.** İki denetçi de `K1#13`
(`https://www.bddk.org.tr/Mevzuat/DokumanGetir/16`) bağlantısını açamamıştı
(biri sertifika hatası, biri 502). Operatör 2026-09-19'da hem adresin hem
iddia metninin DOĞRU olduğunu teyit etti: külçe/basılı yatırımlık altında
taksit yasak (0), işçilikli kuyum harcamasında yasal tavan en fazla 4 ay.

**Kalibrasyon notu — motorun görmediği kanıt:** bu doğrulama operatörün alan
bilgisidir, sentez çıktısında YOKTUR. Motor aynı satırda `açık-soru` üretirse
fark BUNDAN doğar; karşılaştırma raporunda bu sebep ayrıca yazılmalıdır,
yoksa motorun hatası gibi görünür.

**Yanlış işaretlenmiş iç gerilim:** Kaynak-1 Bölüm E'de "fiilen en fazla 3
taksit uygulanıyor" diyor ve denetçi bunu iç gerilim saydı. Gerilim DEĞİLDİR:
4 ay yasal TAVAN, 3 taksit bankanın POS'ta fiilen sunduğu. Tavanın altında
kalmak aykırılık değildir.

**CTA kalıbı girmez.** Denetçi-1'in "alma" gerekçesi iki ayaklıydı; kaynak
ayağı düştü, mevzuat riski ayağı durdu. Sistem sınırı bilir ve aşan vaatleri
engeller, ama taksit konusunu kendisi açmaz.

---

## Soru 3 — Türkiye yerelliği taşıyan görsel kodlar

**Yargı: GİRSİN — operatör eliyle eklenir.**

Trabzon hasırı · ziynet · beşi bir yerde · kulplu çeyrek `gorsel_kodlar` alanına
girer. Mekanik kaynak bağı KURULAMAZ; kayıt "operatör eklemesi, kaynak bağı yok"
olarak durur ve bu zayıflık kararın yanında kalır.

**Sentezin gerekçesi yanlıştı, doğrusu sözleşmeden okundu.** Sentez "iddia
numarası kapsam alanında kullanıldığı için bağ kurulamıyor" diyor — numara
tükenmesi gibi. Gerçek kural (`hakem-sentez-gorevi.md`, `kaynak_iddia` maddesi):
bağ İKİ UÇLUdur ve (a) ayağı, numaranın gösterdiği araştırma satırının
**`alan` hücresinin kararın alanıyla örtüşmesini** şart koşar; mekanik ayrıştırıcı
doğrular, beyan geçmez, fail-closed. `K3#42`'nin alan hücresi `kapsam`'dır.
**Sonuç aynı, sebep farklı — ve fark önemli:** çözüm yeni kaynak bulmak DEĞİL,
bir sonraki araştırma turunda bu kodların `gorsel_kodlar` alanına kaydedilmesidir.

**Karar sebebi:** paketin görsel dili aksi hâlde tümüyle uluslararası katalog
sözlüğünde kalıyor (mevcut alan baştan sona İngilizce fotoğraf terimleri;
D1#35 `[yerel-değil]`).

---

## Soru 4 — Düğün-nişan ve yeni doğan/mevlüt dönemleri

**Yargı: ŞİMDİKİ HÂLİ KALSIN.** Takvim tablosuna satır açılmaz.

- Düğün-nişan: `takvim_temalari` içinde serbest cümle olarak kalır
  ("Mayıs-Ekim düğün-nişan sezonu…"). Sistem anahtarı açılmaz.
- Yeni doğan / mevlüt: yalnız ham katmanda kalır.

**Ölçülmüş yan olgu:** denetçinin "üretim hattı görselde metni yasaklıyor"
iddiası DOĞRUdur — `app/core/caption_generator.py:443`: *"LOGO/ROZET/METİN
KATMANI YASAK … 'text overlay', 'caption text' ASLA tarif etme."* Yani
"üzerinde maşallah yazan bebek altını" sahnesi zaten tarif edilemezdi.

**ÖLÇÜLMEDİ:** `ozel_gun` ve `takvim_temalari` alanlarının çalışma anında
içerik üretimini tam olarak nasıl beslediği bu oturumda ölçülmedi; yukarıdaki
ayrım paketin ŞEMA yapısına dayanır (`sector_content_schema.py`).

---

# GRUP B — Türkiye takvimi (kapsam: TÜM SEKTÖRLER)

> Bu üç yargı kuyumculuğa özel DEĞİLDİR. Bugün oturacakları ortak bir ev YOKTUR;
> bu dosyada durmaları geçici çözümdür. Ev sorusu oturum sonunda ayrıca ele alındı.

## Soru 5 — Ramazan ve Kurban bayramları

**Yargı: İKİSİ DE GİRSİN — operatör eklemesi olarak.**

Mekanik durum: Kurban için hiçbir araştırma iddiası yetkilendirme sağlamıyor —
iki denetçi de aynı şeyi söylüyor (D1: "KAYNAK-3'te Bölüm C satırı da yok, yani
seçilmiş olmasına rağmen hiçbir iddiası yetkilendirilemez"; D2: "döneme özgü ayrı
C satırı bulunmamıştır", karar `alma`). Ramazan'da iki denetçi de `uyarla`/
`açık-soru`. Kaynak-2 İKİ dönemi de "kuyumculuk-özgül güncel kaynak bulunamadı"
diyerek elemiş; Kaynak-1 dokuz dönemi hiç değerlendirmemiş.

**Kaynak bağı kurulamaz; kayıt "operatör eklemesi, kaynak bağı yok" olarak durur.**
Ramazan görselinde `[metin-öğesi]` uyarısı var (çeyrek altın üzerinde yazı) —
görsel kurgusu yazısız olmak zorunda.

## Soru 6 — Yılbaşı

**Yargı: `ticari-firsat` türüyle anahtarlı dönem olarak GİRSİN.**

Tür etiketi kaynaklarda bölünmüştü (K1 `karma`, K2/K3 `ticari-firsat`); operatör
`ticari-firsat` yönünde karar verdi. Takvim teması ayağı zaten güçlüydü (D1 `al`,
K2#14 güncel Türkiye verisi 2026-02-11); anahtarlı dönem ayağı zayıftı (D1
`açık-soru` — yalnız K2'de Bölüm C satırı var; D2 `uyarla`).

**Bilinen zayıflık:** görsel dayanağı uluslararası bir yılbaşı mücevher içeriği,
`[yerel-değil]` + `[genel-geçer]` — D1: "kodlar sektörler arası ayrışma sağlamıyor".

## Soru 7 — 23 Nisan ve 29 Ekim

**Yargı: İKİSİ DE saf kutlama olarak GİRSİN.**

İki denetçi ters düştü: D1 23 Nisan'a `al` (CTA'lara satış dili sızmamış),
29 Ekim'e `uyarla`; D2 ikisine de `alma` ("ürün varlığı günün sektörel kullanımını
kanıtlamaz" · "yatırım ürünü bilgisi milli gün iletişimini desteklemez").
Operatör D1 yönünde karar verdi.

**Bağlayıcı kısıt:** 29 Ekim görseli Cumhuriyet altını sikkesi üzerinden
kurulamaz — sikke yazı/kabartma taşır, görsel hattı metni yasaklıyor
(`caption_generator.py:443`, ölçüldü). Sahne yazısız kurgulanacak.

---

# GRUP C — hattın kusurları (operatör kararı DEĞİL)

## Soru 8 — Kök rehber nüanslarının kaybı

**Ölçülmüş mekanizma (sentezin iddiası DOĞRU):** `app/routers/ai.py:505-518` —
aktif paket varken `SECTOR_GUIDANCE` HİÇ basılmaz, paket onun yerine geçer.
Yasak iki çağrı yerinde uygulanır (`ai.py`, `core/prompt_builder.py:202`) ve
bir regresyon testiyle korunur (`tests/prompt_regression/test_packaged_caption.py:161`
— *"yan-yana basım yasağı ihlal edildi"*).

**Kök rehber nedir (ölçüldü):** `app/core/templates_data.py` içinde elle yazılmış
`SECTOR_GUIDANCE` sözlüğü; Eray, `9761faf`, 2026-04-18. 12 girdi, yalnız 4'ü dolu
(saglik 665 · e-ticaret-perakende 623 · hizmet 620 · yemek-gida 615 karakter);
7'si tek cümle (81-114 karakter); `genel` kendi ağzıyla "sektör-spesifik guidance
yok" diyor. **Kuyumculuk `e-ticaret-perakende`'nin alt sektörü** (DB `social.sectors`,
`parent_sector_id`) — yani kaybolan metin o 623 karakterlik perakende rehberi:
sosyal kanıt · platform öncelikleri · caption formülü · fiyat-indirim vurgusu.

**İki iş ayrıldı (ilk sunumda over-bundle edilmişti — Eray yakaladı, İlke 7):**

- **İş 1 — gerileme onarımı.** Genel kısım ayrı sabite çıkarılır ve paket varken de
  basılır. Dokunulacak: spec §4.1 cümlesi · iki çağrı yeri · bir regresyon testi.
  **Yargı: Plan 2 KAPANINCA, kendi tarihli task'ı olarak.** Ara dönemde test markası
  caption formülünü ve platform önceliklerini kaybetmiş olarak çalışır — BİLİNÇLİ.
- **İş 2 — sektörler üstü karar katmanı.** **EV YOK. Dürüst etiket: çözülmedi +
  park edildi.** Yeniden açılma koşulu: **ikinci sektörün koşusunda aynı takvim
  soruları yeniden çıkarsa.**

**Geri alınan iddia (İlke 9):** ilk sunumda "ortak katman kurulursa gelecek
sektörlerde bu sorular tekrar sorulmaz" dendi — ÖLÇÜLMEDİ ve muhtemelen yanlış.
Ramazan'ın kuyumcu için anlamı ile yazılım firması için anlamı aynı değildir;
taşınabilecek şey cevap değil, "bu soru soruldu, varsayılanı şu" olurdu.

## Soru 9 — KAYNAK-1'in kaynaksız alanları (SORULMADI)

Operatör kararı değil, kaynak kusuru kaydı. KAYNAK-1'in `cta_kaliplari` ·
`kanca_kaliplari` · `video_kodlar` · `takvim_temalari` ve tüm GÖREV B dönemleri
için Bölüm C'de tek satırı yok; aday takvimin 9 dönemini hiç değerlendirmemiş
(D1 açık soru 2). Bu alanlarda KAYNAK-1 mutabakat sayımında "yok" sayılır —
denetçilerin fiilen yaptığı da budur. Yeniden araştırma, Ramazan/Kurban
hedefli turuyla BİRLİKTE tek seferde yapılır.

## Soru 10 — CTA alt sınırı (SORULMADI — kendiliğinden çözüldü)

Brief en az 5 CTA kalıbı istiyor, eşikleri geçen 4 kaldı (bakım-parlatma,
yetki belgesi ve taksit kalıpları düştü). **Soru 2'nin kararı bunu kapattı:**
düşen kalıplardan biri taksit CTA'sıydı ve operatör onu BİLEREK dışarıda
bıraktı. Dolayısıyla 4 kalıp artık kaza değil, karar sonucudur. Paket bu hâliyle
şema kapısından geçer (alt sınır araştırma raporunun sınırıdır, şemanın değil).

---

# Kapanış

**10 açık sorunun tamamı karara bağlandı.** Motorun koşmasının önündeki K-134
körlük koşulu KARŞILANDI: bu yargılar motor çıktısı MEVCUT DEĞİLKEN verildi.

**Sıradaki iş:** Plan Task 19 Step 8 — `motor --run-id kosu-222706dc…`
(`--politika-ayari` verilmez; K-24 gereği eşikler pasif kalır), ardından bu
yargılarla motorun kararlarının karşılaştırması koşu raporuna yazılır.

**Karşılaştırmayı okurken dikkat:** dört yargı motorun göremeyeceği girdiye
dayanıyor (Soru 2 operatör doğrulaması · Soru 3, 5 operatör eklemeleri · Soru 6/7
operatör tercihi). Motor bu satırlarda `açık-soru` üretirse bu motorun HATASI
DEĞİLDİR; fark raporunda sebep ayrıca yazılmalıdır.
