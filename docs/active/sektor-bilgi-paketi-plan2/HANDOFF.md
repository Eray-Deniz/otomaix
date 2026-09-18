---
task: sektor-bilgi-paketi-plan2
written: 2026-09-18
---

# Resume From

**Zincir `sentez`e kadar TAMAM. Sıradaki iş ERAY'DA: Plan Task 19 Step 7 — K-134 kör yargı.**

Motor, operatörün yalnız-sentez yargısı kaydedilmeden **KOŞMAZ** (körlük kalibrasyonun ön
koşuludur; plan satır 2169). Eray sentez çıktısına bakar, 10 açık soru için yargısını verir,
yargı kaydedilir — ancak ondan sonra `motor` koşar ve fark koşu raporuna yazılır (Step 8).

- Aktif koşu: **`kosu-222706dc643b4b64b66a1f3826f02c1b`** (sektör `kuyumculuk`).
- Sentez çıktısı: `<araştırma deposu>/sentez/kosu-222706dc…/01-SENTEZ-CIKTISI.md`
  (4 bölüm: aday paket · 74 satırlık karar günlüğü · 10 açık soru · özet).
- 10 sorunun konuları: SPK kapsamı/yatırım dili · Ramazan-Kurban · yılbaşı · 23 Nisan ve
  29 Ekim · kuyumda taksit sınırı · Türkiye'ye özgü görsel kodlar · sistem anahtarı olmayan
  dönemler (düğün-nişan, mevlüt) · KAYNAK-1'in kaynaksız alanları · kök rehber nüanslarının
  kaybı · CTA kalıp sayısının brief alt sınırının altında kalması.
- Sentez her soruda **kendi eğilimini** yazmıştır; kör yargı o eğilimden BAĞIMSIZ alınmalıdır.

**Motor komutu (yargı kaydedildikten SONRA):**
`motor --run-id kosu-222706dc…` — `--politika-ayari` verilmezse eşikler PASİF kalır (K-24:
eşik pilot kanıtından sonra belirlenir, uydurulmaz).

# Verification

**Bu oturumda koşan komutlar ve TAZE çıktıları:**

| Ne | Sonuç |
|---|---|
| Tam takım — oturum başı | **4573 passed** / 338,49 s / rc=0 |
| Tam takım — oturum sonu | **4607 passed / 0 failed / 337,55 s / rc=0** (+34 test) |
| `denetim` (ilk deneme) | `rc=1` REDDEDİLDİ, 1342 sn — biçim kapısı |
| `denetim` (yeni koşu) | **`rc=0`, 956 sn, `denetci_sayisi: 2`** |
| Denetim artefaktları (DB) | iki `review` satırı, K-80 damgalı, 25.682 + 11.690 karakter |
| `sentez` 1-4. denemeler | `rc=1`/`rc=2`: yol · plan kipi · CTA şekli · JSONL (hepsi kayıtlı) |
| `sentez` (5. deneme) | **`rc=0`, 941 sn, karar 74 · açık soru 10 · taşma yok** |
| Sentez artefaktı (DB) | `synthesis`, 40.671 karakter, K-80 damgalı |
| Kodlayıcı testi mutasyonu | düzeltme sökülünce test **KIRMIZI**, geri konunca yeşil |
| Sözleşme pini | `require_contract_pin()` geçti (dış depo HEAD `aa52191`) |

**DENENMEYEN / DOĞRULANMAYAN — yeşil sayılmaz:**

- **`motor` · yazım kapısı · `katman1/2` · `onay` · `aktive-et` ayakları HİÇ koşmadı.**
- **Denetçi ve sentez çıktılarının İÇERİĞİNİ hiçbir insan okumadı** — ölçülen şey kapılardan
  geçtiğidir, doğru olduğu değil. Kör yargı adımı tam da bunun içindir.
- Koşu satırı **`tamamlanmadi` görünüyor**: dördüncü deneme işaretledi, beşinci başarı geri
  almıyor. `runs.py:836` motorun başarılı koşumunda `tamamlandi` yazacağı için kalıcı zarar
  beklenmiyor — ama **bu yol ölçülmedi.**
- Çalışma ağacı **KİRLİ** (12 dosya) ve dal `feat/sektor-bilgi-paketi-plan2` **28+ commit
  push EDİLMEDİ**. Kirli ağaçta review güvenilmez — bir sonraki adım önce commit.
- Dış sözleşme deposunda bugün **üç commit** atıldı (`d894cd9` · `1174fb8` · `aa52191`);
  pin her seferinde tazelendi ama dış depo da push edilmedi.

# Risks

- **F1/F5/F6 koşullu kabul edilmiş risk** (kardeş görev): ağa çıkabilen denetçi okuduğunu
  gönderebilir. **Yeniden açılma koşulu: pakete üçüncü taraftan ham içerik girdiği gün.**
- **Kör yargı kirlenebilir.** Sentez her soruda kendi eğilimini yazdı; yargıyı alan taraf o
  eğilimi "doğru cevap" gibi sunarsa K-134'ün ölçtüğü şey kaybolur.
- **Biçim toleransları gevşetildi** (başlık süsü, markdown başlığı, JSONL). Her biri negatif
  kontrollüdür ama tolerans yönü tek yönlüdür: bir daha gevşetmeden önce "bu gerçekten yazım
  farkı mı, anlam farkı mı" sorulmalı.
- **Sentez klasörü doluysa tur koşmaz** (`mkdir` `exist_ok` kullanmıyor). Düşen denemeler
  `DUSMUS-<tarih>-<sebep>-<koşu>` adıyla kenara alındı; desen korunmalı, silme YOK.

# Notes For Claude

- **Model turundan ÖNCE offline replay yap.** Kaydedilmiş çıktı + sahte runner + DB'ye yazmayan
  işaretleyici ile tüm zincir koşturulur. Bu oturumda üç kez yapıldı ve en az iki boş tur
  (~15 dk + jeton) önledi; altıncı duvarın olmadığı da böyle ölçüldü.
- **Testin gerçek API'yi çağırdığından emin ol.** `asyncpg.connect`'i sahteyle değiştiren test
  `init=` argümanını yuttu ve YEŞİL kaldı; üretim `TypeError` verdi (`init` havuz parametresi).
  Taklit, ölçmesi gereken şeyi gizledi. Düzeltme gerçek bağlantıyla yeniden yazıldı ve
  mutasyonla sınandı.
- **Genel `except` arıza sebebini siler.** `komut koşulamadı (DataError)` satırının arkasında
  asıl sebep vardı; jsonb kodlayıcısı kurulmadığı için işaretleme de düşüyordu. Kusur, arızayı
  gizleyerek ikinci kez zarar verdi.
- **Sözleşme↔kod sapması tek tek yamanmaz.** Aynı gün üç sapma çıktı; kapanış EK-L'yi şema
  modülünden ÜRETMEK oldu. Yeni bir alan şekli eklenirse yeri orasıdır, düz yazı değil.
- **Düşen turun çıktısı kanıttır.** Silme; `DUSMUS-…` adıyla kenara al.

# Notes For Codex

Bu oturumda Codex **hakem olarak koşmadı**; yalnız `denetci-2` rolünde denetim turunda koştu
(kutulu kullanıcı, ağ açık, `rc=0`). Bu dalda `/review-claude-codex` ve
`/security-review-claude-codex` **hâlâ koşmadı** — zincirin yeri Plan Task 19 sonrasıdır ve
kirli ağaçta koşturulmamalıdır.
