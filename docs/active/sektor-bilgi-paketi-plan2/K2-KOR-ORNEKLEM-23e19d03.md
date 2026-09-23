---
task: sektor-bilgi-paketi-plan2
adim: Katman-2 kör örneklem (spec §2 / §14.2 — kapı DEĞİL, onayın girdisi)
kosu: kosu-23e19d0382b945a1bee2176239185b91
paket: 66654971-d90e-4cec-92da-61e723a8ec8f (taslak, sürüm 1)
marka: Deniz Kuyumculuk (TEST) cb1dd79e-5ed4-452e-90cb-9ae1e88a5319
tarih: 2026-09-23
---

# Katman-2 kör örneklem — kosu-23e19d03

**Protokol:** aynı marka + aynı konu için `generate_captions` (claude-opus-4-6, temperature 1.0,
platform instagram) iki kez çağrıldı: `package_context` = taslak paket / `None` (paketsiz yol).
A/B sırası konu başına rastgele (seed 20260923); operatör anahtarı görmeden seçti. Örneklem boyutu
(K-11 a) karara bağlı değildi — 4 konu × 2 önerildi, Eray onayladı. **Maliyet ölçüldü:** 8 çağrı,
0,273 USD (girdi 5 $/M · önbellek yazma 6,25 $/M · okuma 0,5 $/M · çıktı 25 $/M; token sayıları
`usage`'tan).

| Konu | Seçim | Paketli | Sonuç |
|---|---|---|---|
| Normal gün (alyans) | B | A | paketsiz seçildi |
| Anneler Günü | A | B | paketsiz seçildi |
| 8 Mart (kutlama) | A | A | paketli seçildi |
| Kurban Bayramı 1. gün | A | A | paketli seçildi |

**Paketli seçim 2/4.** Örneklem küçük; oran bir ölçüt değildir (eşik yok, K-11 b).

**Gözlemler (ölçülen, yorum değil):**
- Paketli alyans metni "📌 Yetki belgesi ve işletme bilgilerimiz mağazamızda mevcuttur." satırını
  ekledi — yasak olarak yazılan yetki belgesi maddesini (operatör eklemesi, S3) model cümle ekleyerek
  karşıladı; marka kayıtlarında numara olmadığı için numarasız bir ibare doğdu.
- Paketli Anneler Günü metni ürün adı (kolye · inci · bilezik) ve "hatıra" vurgusu taşıdı; seçilen
  paketsiz metin genel kutlamaydı.
- 8 Mart paketli metni satış çağrısı İÇERMEDİ (kutlama kuralı); etiketleme daveti operatörün CTA'sıdır.
- Kurban paketli metni satış çağrısı içermedi ("karma" tür satışa izin verir, model kullanmadı).

## Metinler (kör sırayla, sunulduğu gibi)

## 1) Normal gün — alyans tanıtımı

**A:**

Birlikte atacağınız her adımı taşıyacak bir alyans seçmek, aslında o anın hissini parmağınıza taşımaktır. 💍

Alyans koleksiyonumuzda farklı ayar ve gramaj seçeneklerini yan yana inceleyerek size en uygun modeli bulabilirsiniz.

✨ Klasik düz banttan işlemeli modellere kadar geniş bir yelpaze sizi bekliyor.

Hangi ayar ve gramajın sizin için doğru olduğunu merak ediyorsanız, bize yazın — birlikte karar verelim. 📩

📌 Yetki belgesi ve işletme bilgilerimiz mağazamızda mevcuttur.

_Hashtag:_ ['alyans', 'düğün', 'nişan', 'kuyumculuk', 'altın', 'evlilik', 'düğünhazırlıkları', 'takı', 'alyansmodelleri', 'gelin', 'damat', 'nikah', 'özelgün', 'düğünsezonu', 'mutluluk']

**B:**

Birlikte atacağınız her adımı taçlandıran alyanslar ✨

Hayatınızın en özel kararını simgeleyen alyans koleksiyonumuzu keşfedin. Her bir parça, iki kişinin ortak hikayesini parmağında taşıması için özenle hazırlandı.

💍 Koleksiyonu yakından görmek için mağazamızı ziyaret edin ya da bize yazın — size özel randevu ayarlayalım.

👇 Beğendiğiniz modeli yorumlarda paylaşın!

_Hashtag:_ ['alyans', 'evlilik', 'nikah', 'nişan', 'düğün', 'kuyumculuk', 'altın', 'alyansmodelleri', 'evlilikhazirliklari', 'söz', 'düğünhazırlıkları', 'gelinlik', 'damat', 'çift', 'takı']

## 2) Anneler Günü

**A:**

Bizi hayata getiren, sevgiyle büyüten, her düştüğümüzde ilk koşan… 💛

Bir annenin eli değdiği her şey altına döner.

Bugün tüm annelerin Anneler Günü kutlu olsun. Sevginiz daim, gülüşünüz hiç solmasın. 🌸

Deniz Kuyumculuk olarak bu özel günde tüm anneleri sevgiyle kucaklıyoruz.

_Hashtag:_ ['annelergünü', 'annelergünükutluolsun', 'anne', 'anneye', 'annesevgisi', 'kuyumculuk', 'hediye', 'özelgün', 'sevgi', 'altın', 'kuyumcu', 'anneyehediye', 'anneiçin', 'değerlisinanne', 'canımannem']

**B:**

Ellerinden hiç eksik olmayan o sıcaklık, saçlarını taradığı sabahlar, kulağına fısıldadığı "her şey güzel olacak"…

Bazı anılar, kelimelerle anlatılmaz — ama bir kolye, bir inci, bir bilezik o anıyı her dokunuşta hatırlatır. 💛

Annelerimiz bize sevgiyi öğretti; biz de o sevgiyi kuşaktan kuşağa taşıyacak bir hatırayla taçlandıralım.

Tüm annelerin Anneler Günü kutlu olsun. 🌷

Deniz Kuyumculuk

_Hashtag:_ ['AnnelerGünü', 'Anne', 'Annem', 'Kolye', 'İnci', 'Takı', 'Hatıra', 'Kuyumculuk', 'Sevgi', 'AileBağı', 'Minnet', 'ÖzelGün', 'KuşaktanKuşağa', 'AnneyeHediye', 'DenizKuyumculuk']

## 3) 8 Mart Dünya Kadınlar Günü

**A:**

Hayatımıza güç katan, yol gösteren, emekleriyle bize ilham veren tüm kadınların Dünya Kadınlar Günü kutlu olsun. 💜

Bir annenin eli, bir kız kardeşin omzu, bir arkadaşın sözü… Her biri hayatımızda taşıdığımız en değerli hatıra.

Bugün, ilham aldığınız kadını düşünün. Ona bu gücü hissettirin — bir mesajla, bir sarılmayla, bir bakışla. 🌿

Hayatınıza anlam katan kadını etiketleyin, ona olan takdirinizi gösterin. ✨

Deniz Kuyumculuk

_Hashtag:_ ['DünyaKadınlarGünü', '8Mart', 'KadınlarGünü', 'KadınınGücü', 'İlhamVerenKadınlar', 'Takdir', 'Emek', 'Güç', 'Hatıra', 'KuşaktanKuşağa', 'KadınlarGünüKutluOlsun', 'Kadın', 'DenizKuyumculuk', 'Kuyumculuk', 'Kutlama']

**B:**

Hayatın her alanında iz bırakan, ilham veren, güçlü kadınlar… 💜

Bugün ve her gün, cesaretiniz, emeğiniz ve varlığınız için teşekkür ederiz.

Dünya Kadınlar Günü kutlu olsun. ✨

— Deniz Kuyumculuk

_Hashtag:_ ['DünyaKadınlarGünü', '8Mart', 'KadınlarGünü', 'KadınaDeğer', 'GüçlüKadınlar', 'İlhamVerenKadınlar', 'KadınOlmak', 'KadınlarGünüKutluOlsun', '8MartDünyaKadınlarGünü', 'Kutlama']

## 4) Kurban Bayramı 1. gün

**A:**

Kurban Bayramınız mübarek olsun. 🌙

Bu bayram da sevdiklerinizle bir arada olmanın, sofralar kurmanın, kapıları çalmanın güzelliği ayrı.

Büyüklerin elini öpen çocukların gözlerindeki ışıltı, kuşaktan kuşağa aktarılan sevgi ve saygı… Bayramı bayram yapan işte bu anlar.

Deniz Kuyumculuk ailesi olarak tüm sevenlerimizin bayramını en içten dileklerimizle kutlarız. Sağlık, huzur ve bereket dolu nice bayramlar dileriz. ✨🤲

_Hashtag:_ ['KurbanBayramı', 'BayramMübarekOlsun', 'Bayram', 'KurbanBayramıKutluOlsun', 'İyiBayramlar', 'BayramSevinci', 'Kuyumculuk', 'DenizKuyumculuk', 'Altın', 'Takı', 'BayramKutlaması']

**B:**

Kurban Bayramınız mübarek olsun 🌙✨

Sevdiklerinizle paylaştığınız her anın, sofranızdaki her sohbetin, kapınızı çalan her misafirin bayramınıza güzellik katmasını diliyoruz.

Bu mübarek günlerde sevgi ve huzur evinizden eksik olmasın. 🤲

Deniz Kuyumculuk ailesi olarak tüm sevenlerimizin bayramını en içten dileklerimizle kutluyoruz.

Hayırlı bayramlar! 🐑

_Hashtag:_ ['KurbanBayramı', 'BayramMübarekOlsun', 'HayırlıBayramlar', 'Bayram', 'MübarekGünler', 'KurbanBayramıKutluOlsun', 'Kuyumculuk', 'BayramSevinci', 'BayramKutlaması', 'HuzurluBayramlar']
