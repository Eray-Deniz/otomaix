# Ölçüm ölçütleri — ayar koşusundan sonra SABİTLENDİ (2026-09-25)

Ayar koşusu: `senaryolar-ayar.json` (20, Claude yazdı) · A + B (40 çağrı, 1,41 USD) · kör hakem Codex
(`sonuc-ayar/hakem-codex.json`). Bu dosya sınav kümesi (`senaryolar-sinav.json`, 20, bağımsız ajan
yazdı) koşulmadan ÖNCE yazıldı; sınavdan sonra DEĞİŞTİRİLMEZ. Değişirse sınav tekrarlanır.

## Ayar koşusunun ham sonucu (kör hakem, anahtar sonradan açıldı)

| | Paketli | Paketsiz |
|---|---|---|
| Hakem tercihi | 15 | 2 (3 eşit) |
| Ölçüt hatası | 2 | 8 |
| Beklenen karşılama | 20/25 | 13/25 |
| Ek hata (hakem) | 11 | 14 |

## Ayar koşusunda düzeltilenler

- **Kural taraması:** "getiri" deseni "getirin"i yakalıyordu (kelime sınırı eklendi); "TL" kelime içini
  yakalıyordu; Yılbaşı `national` diye satış yasağına düşüyordu (paket türü üstündür, K-03).
- **Olumsuz cümle regex'lenemez:** "garanti taşımaz" getiri dili sayılıyordu. Getiri dili kuralı artık
  yalnız ADAY işaretidir; karar hakemindir.
- **Senaryo ölçütü metin düzeyinde olmalı:** K09/K10'un ölçütü talimat düzeyindeydi ("CTA talimatta yok");
  hakem bunu metne uyguladı. Talimat ölçütleri A'da kalır, B hakemine verilmez.

## Sınav için sabit kurallar

1. **Instagram DM / yorum her profilde vardır.** "Bize yazın / mesaj atın / yorumda sorun" kanal hatası
   DEĞİLDİR. Kanal hatası = markada OLMAYAN mağaza, site, WhatsApp veya randevuya yönlendirme.
   (Ayar koşusunda hakem 8 DM çağrısını kanal hatası saydı.) **Eray kararı 2026-09-25: hata sayılmaz.**
2. **Kritik hata ayrı sayılır, ortalamaya karışmaz:** getiri/yatırım dili · sentetik taşı gizleme ·
   uydurma fiyat/indirim/eski fiyat · uydurma ürün niteliği (ayar, gram, taş, sertifika) · markada olmayan
   kanal · kişisel veri · anma gününde satış · yazım bozukluğu (sözlük dışı kelime).
3. **Hakemin "ek hata"ları ADAYDIR:** hakem mevzuat bağlamı taşımaz (ayar K18: doğru olan "yönetmelik gereği
   sentetik" ibaresini dayanaksız saydı). Ek hatalar Claude tarafından alıntıya karşı tek tek doğrulanır;
   düşürülen her aday gerekçesiyle yazılır.
4. **Metrikler (dördü ayrı raporlanır):** hakem tercihi · ölçüt hatası (paketli/paketsiz) · kritik hata
   (paketli/paketsiz) · beklenen karşılama oranı. C (Eray'ın kör okuması) ayrı satırdır.
5. **Eşik — Eray kararı 2026-09-25, sınav sonucundan SONRA değiştirilmez.** Paket yeterli sayılır ancak
   İKİSİ birden sağlanırsa:
   - (a) kör hakem 20 sınav senaryosunun **en az 15'inde** paketli metni paketsizden iyi buluyor
     ("eşit" paketli lehine sayılmaz);
   - (b) paketli metinlerde **kritik hata 0** (madde 2'deki liste; Claude'un doğrulamasından geçen hâli).
   Ölçüt hatası sayısı ve beklenen karşılama raporlanır, eşiğe GİRMEZ. Eray'ın kör okuması (C) ayrı satırdır;
   hakemle yön ayrılırsa ayrıca konuşulur.

## Açık gözlem (ayar koşusu)

- **K09 paketli metinde "ysatisfa" bozukluğu 2 koşunun 2'sinde** (duman denemesi + ayar koşusu), diğer 19
  paketli metinde 0. Aday kaynak: talimattaki ASCII etiketler (`tür: satis`, `ticari-firsat`) — ama K10/K11
  aynı etiketleri taşıyıp bozulmadı. **Neden belirlenmedi.**
- Paketin "ayar, gramaj açıkça söylenir" kuralı metne yansımıyor: ayar/gram eksikliği paketli 9 · paketsiz
  9 senaryoda (kural taraması). A'daki gramaj çelişkisiyle (madde 2) tutarlı.
- Bayram (K12): iki metin de paketin "çeyrek/gram hediye geleneği" mesajını işlemedi.
