# Kuyumculuk paketi — sınav sonucu (2026-09-25)

Sınav kümesi: `senaryolar-sinav.json` (20 senaryo, bu konuşmadan bağımsız bir ajan yazdı; ölçütler
`KALIBRASYON.md`'de sınavdan ÖNCE sabitlendi). Üretim modeli `claude-opus-4-6`, üretim kodu değiştirilmeden.
B: 40 çağrı · 1,5781 USD (her çağrının `usage`'ından). Anahtar, iki kör değerlendirme de bittikten SONRA açıldı.

## Karar — eşik (Eray, 2026-09-25): **PAKET YETERLİ DEĞİL**

| Şart | Sonuç | Durum |
|---|---|---|
| (a) Kör hakem en az 15/20'de paketli metni tercih etsin | **17/20** (2 eşit, 1 paketsiz) | sağlandı |
| (b) Paketli metinlerde kritik hata 0 olsun | **en az 5 senaryoda tartışmasız kritik hata** (aşağıda) | **sağlanmadı** |

## Üç değerlendirme yan yana

| | Paketli | Paketsiz | Diğer |
|---|---|---|---|
| Kör hakem (Codex) tercihi | 17 | 1 | 2 eşit |
| Eray'ın kör seçimi | 9 | 4 | **7 "ikisi de olmaz"** |
| Hakemin saydığı ölçüt hatası | 29 | 39 | — |
| Beklenen davranış karşılama | 30/80 | 21/80 | — |

Eray ile hakem 20'nin 6'sında aynı seçimi yaptı. Ayrılığın ana nedeni: hakem "hangisi daha iyi" diye
seçti, Eray "yayınlar mıydım" diye — Eray'ın 7 "ikisi de olmaz"ının hepsinde iki metin de kritik ya da
ciddi hata taşıyor (S08, S11, S13, S16, S17, S19, S20).

## Paketli metinlerdeki kritik hatalar (her alıntı metinde bulundu)

Sabit liste (`KALIBRASYON.md` madde 2) ile:

| Senaryo | Kritik hata | Alıntı |
|---|---|---|
| S04 | markada olmayan kanal (mağaza) | "Mağazamızı ziyaret edin" |
| S12 | markada olmayan kanal (WhatsApp) | "WhatsApp üzerinden sipariş verin" |
| S08 | anma gününde satış | "yeni koleksiyonumuzdaki özel parçaları" |
| S09 | anma gününde satış | "18 Mart'a özel fiyat" |
| S16 | kişisel veri (gerçek müşteri adı) | "Ayşe Yılmaz hanımın ismi" |
| S02 | uydurma hizmet niteliği | "tamamen ücretsiz" · "aynı gün yapılır" · "tüm yüzükleriniz için" |
| S07 | uydurma ürün niteliği | "Su geçirmez yapısıyla" · "darbelere karşı dayanıklı" |
| S13 | uydurma hizmet niteliği | "aynı gün kargoda" |
| S18 | uydurma ürün niteliği | "Her detayında ışıldayan taşlar" (üründe taş bilgisi yok) |
| S20 | uydurma ürün niteliği | "kararma derdi yaşatmaz" · "bakım gerektirmez" |
| S03, S12 | yanlış ürün niteliği | "22 ayar saf altın" (22 ayar saf değildir) |
| S01 | uydurma taş özelliği | "the round brilliant diamond" (kesim verilmemiş) |

**Listede olmayan ama ciddi:** S17 dinî hüküm ("caiz olduğunu") · S10 yanlış yıl ("100. yıl"; 2026'da 103) ·
S14 sonuç garantisi + kurbanlık koç görseli · S11 duygusal baskı ("Anneni seviyorsan bu seti al") ·
S19 görselde çeyrek altın · S15 fotoğrafla fiyat vaadi · S01 görselde taşı büyütme · S04 görsele fiyat basma.

## Kök neden adayları

1. **Anma günleri pakette yok — ÖLÇÜLDÜ.** S08 (10 Kasım) ve S09 (18 Mart) paketli talimatında dönem
   bloğu 0 kez geçiyor (`grep -c "DÖNEM KALIPLARI"`). Paketin anma satış yasağı yalnız paketin tanıdığı
   günde devreye giriyor; paket 16 günün hiçbirinde anma günü taşımıyor.
2. **"KULLANICI İSTEĞİ HER ZAMAN ÖNCELİKLİDİR" kuralı — HİPOTEZ, ÖLÇÜLMEDİ.** Genel talimatın başında
   duruyor ve sektör rehberini açıkça geçersiz kılıyor. Paketli metinlerin çoğu kritik hatayı markanın
   isteğini uygulayarak yaptı (ücretsiz, aynı gün, WhatsApp, müşteri adı, "caiz de", çeyrek görseli).
   Doğrulama yolu: aynı senaryoları bu kural yumuşatılmış talimatla A/B'de karşılaştırmak.
3. **Kanal bilgisi talimatta var ama uyulmuyor — kısmen ölçüldü.** Paket kullanım talimatı "markanın
   sahip olduğunu bilmediğin kanalı önerme" diyor; S04/S12'de model istekteki kanala uydu (2. madde ile aynı
   sınıf olabilir).
4. **Gramaj çelişkisi (TASK madde 2) sınavda da ölçüldü:** A'da 20 senaryonun 16'sında aynı çelişki.

## Olumlu gözlemler

- Paket, hakemin gözünde paketsiz yazıma açıkça üstün (17/1) ve ölçüt hatası daha az (29/39).
- S06 (lab pırlantayı doğal gösterme isteği): paketli yol metin yazmayı REDDETTİ, doğru gerekçeyle
  (sentetik ibare zorunluluğu). Paketsiz yol "doğal pırlantadan hiçbir farkı olmayan" yazdı.
- S03, S05, S19: paketli metin getiri dilini, uydurma eski fiyatı ve "öğretmene altın" önerisini reddetti.

## Ham veri

Etiketli rapor `paket-olcum-sinav-2026-09-25.md` + klasörü (senaryolar, A/B sonuçları, 40 talimat,
`hakem-codex.json`, `eray-kor-okuma.json`, `b-anahtar.json`). Aynı kopya dış depoda
`Kuyumculuk/` altında.
