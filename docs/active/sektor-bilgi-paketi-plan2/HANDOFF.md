---
task: sektor-bilgi-paketi-plan2
written: 2026-09-19
---

# Resume From

**Task 19 Step 7 BİTTİ — K-134 kör yargı alındı. Sıradaki iş Claude'da: Step 8, `motor` koşumu.**

Eray sentezin 10 açık sorusunun tamamını cevapladı; motorun önündeki körlük koşulu
karşılandı. Yargı kaydı: **`K134-KOR-YARGI.md`** (bu klasörde) — her kararın yanında
dayandığı ham kanıt ve bilinen zayıflığı duruyor.

- Aktif koşu: **`kosu-222706dc643b4b64b66a1f3826f02c1b`** (sektör `kuyumculuk`).
- Motor komutu: `motor --run-id kosu-222706dc…` — `--politika-ayari` VERİLMEZ
  (K-24: eşikler pilot kanıtından sonra belirlenir, uydurulmaz).
- Sonra: motorun kararlarıyla kayıtlı yargının farkı koşu raporuna yazılır (spec §15.2).

**Karşılaştırmayı okurken ZORUNLU uyarı — yoksa motor haksız yere hatalı görünür.**
Dört yargı motorun göremeyeceği girdiye dayanıyor:
- **Soru 2:** BDDK taksit sınırını Eray doğruladı (iki denetçi de sayfayı açamamıştı).
- **Soru 3 ve 5:** yerel görsel kodlar + Ramazan/Kurban **operatör eklemesi**; mekanik
  kaynak bağı KURULAMAZ (sözleşmenin `kaynak_iddia` iki-uçlu bağı, fail-closed).
- **Soru 6 ve 7:** yılbaşı tür etiketi ve milli günler saf operatör tercihi.

Motor bu satırlarda `açık-soru` üretirse **hata değildir**; fark raporu sebebi ayrıca yazmalı.

**Step 9'a taşınan elle iş (unutulursa paket eksik çıkar):**
- Yerel görsel kodlar `gorsel_kodlar` alanına elle eklenir, kayıt "kaynak bağı yok" der.
- Ramazan + Kurban dönem olarak elle eklenir (Kurban'ın hiçbir iddia satırı yok).
- **29 Ekim görseli sikke üzerinden KURULAMAZ** — sikke yazı taşır, görsel hattı metni
  yasaklıyor (`caption_generator.py:443`, ölçüldü). Sahne yazısız kurgulanacak.
- Ramazan görselinde aynı kısıt (`[metin-öğesi]`, çeyrek altın üzerinde yazı).

# Verification

**Bu oturumda KOD DEĞİŞMEDİ.** Yalnız `K134-KOR-YARGI.md` yazıldı, `TASK.md`
güncellendi. Test takımı koşulmadı — değişen kod olmadığı için gerekmedi.

**Koşan komutlar ve taze çıktıları:**

| Ne | Sonuç |
|---|---|
| `git status --porcelain` | **temiz** (0 satır) |
| `git log @{u}..HEAD` | **0** — dal uzak kopyasıyla eşit |
| `psql social.sectors` | `kuyumculuk` → `parent_sector_id` = `e-ticaret-perakende` |
| `SECTOR_GUIDANCE` ölçümü | 12 girdi; 4'ü dolu (615-665 krk), 7'si tek cümle (81-114 krk) |
| Sentez çıktısı diskte | `01-SENTEZ-CIKTISI.md`, 40.900 bayt, 18.09 18:10 |

**Devralınan iki iddia YANLIŞ ÇIKTI (bir önceki HANDOFF):** "çalışma ağacı kirli
(12 dosya)" ve "28+ commit push edilmedi" — ikisi de ölçümle düştü. Ağaç temiz,
dal eşit.

**Ölçülen mekanizmalar (hepsi dosya açılarak):**
- `ai.py:505-518` — aktif paket varken kök rehber HİÇ basılmaz (if/else, tek kapı).
- `caption_generator.py:443` — görsel istemde metin/logo katmanı tarif etmek YASAK.
- `engine.py:2338` — motorun açık soru kimlikleri = kendi bulguları **+ sentezin
  açık sorularının TAMAMI**.
- `approval.py:327-334` — açık soru varken onay BLOKLANIR (ikinci kapı).
- `policy_config.py` — ayar yüzeyi yalnız oran/limit + `block_on_legislation`;
  **duran cevap alanı YOK.**
- `hakem-sentez-gorevi.md` `kaynak_iddia` — bağ İKİ UÇLU; (a) ayağı araştırma
  satırının `alan` hücresinin kararın alanıyla örtüşmesini şart koşar, fail-closed.

**DENENMEYEN / DOĞRULANMAYAN — yeşil sayılmaz:**
- **`motor` · yazım kapısı · `katman1/2` · `onay` · `aktive-et` ayakları HÂLÂ hiç koşmadı.**
- Motorun koşum SÜRESİ ölçülmedi (bu ayak hiç koşmadı) — tahmin verilmedi.
- Koşu satırı hâlâ **`tamamlanmadi`** görünüyor. `runs.py:836`'nın başarılı motor
  koşumunda `tamamlandi` yazacağı beklentisi **ÖLÇÜLMEDİ**.
- `ozel_gun` ve `takvim_temalari` alanlarının çalışma anında içerik üretimini nasıl
  beslediği ölçülmedi; paket şema yapısına dayanan ifadeler kullanıldı.

# Risks

- **Kör yargı artık ALINDI — kirlenme riski geçti.** Ama fark raporu yazılırken
  yukarıdaki "motorun göremeyeceği dört girdi" uyarısı atlanırsa kalibrasyon yanlış
  okunur ve motor haksız yere hatalı görünür.
- **SPK kararı bilinçli bir risk kabulüdür.** Eray geniş çerçeveyi seçti; denetçi o
  çerçeveyi kaynak sayfasında BULAMAMIŞTI (`KAYNAKTA YOK`). Paket doğrulanmamış bir
  hukuki iddia taşıyacak — gerekçe kayıtta, gizlenmiş değil.
- **Operatör eklemeleri mekanik bağı olmayan kalemlerdir.** Sayıları arttıkça paketin
  "her kalem bir kaynağa bağlıdır" garantisi zayıflar; kayıt bunu görünür tutuyor.
- **F1/F5/F6 koşullu kabul edilmiş risk** (kardeş görev): ağa çıkabilen denetçi
  okuduğunu gönderebilir. Yeniden açılma koşulu: pakete üçüncü taraftan ham içerik
  girdiği gün.
- **Sentez klasörü doluysa tur koşmaz** (`mkdir` `exist_ok` kullanmıyor). Düşen
  denemeler `DUSMUS-<tarih>-<sebep>-<koşu>` adıyla duruyor; desen korunmalı, silme YOK.

# Notes For Claude

- **Eray ham kanıt istiyor, özet değil.** "Şu kaynak şöyle diyor" özeti yetmedi; kanun
  maddesi numarası, birebir alıntı ve denetçinin canlı kontrol sonucu istendi. Karar
  sorusu sorulacaksa kanıt ÖNCE gelir. İki soru bu yüzden geri geldi.
- **Soru sayısı şikâyeti meşruydu ve ölçümle karşılandı.** "Her sektörde onlarca soru mu
  cevaplayacağım" sorusu, soruları KAPSAMA göre ayırınca çözüldü (4 sektör + 3 takvim +
  3 hat kusuru). Sayıyı azaltan şey cevap vermek değil, hangi sorunun gerçekten bu
  sektöre ait olduğunu ayırmaktı.
- **Kendi önerine de İlke 7'yi uygula.** "Ortak taban katmanı kurulsun" önerisi evsizdi
  ve iki ayrı işi (küçük gerileme onarımı + yeni alt sistem) tek pakete bağlamıştı —
  **Eray yakaladı**, ben değil. Öneri sunmadan önce: evi var mı, over-bundle mı?
- **Ölçülmemiş fayda iddiası etme.** "Gelecek sektörlerde bu sorular tekrar sorulmaz"
  dendi ve geri alındı; Ramazan'ın anlamı sektöre göre değişir.
- **Sentezin gerekçesi yanlış olabilir, sözleşmeyi aç.** Sentez yerel görsel kodları
  "numara kapsam alanında kullanıldı" diye eleyip geçmişti; gerçek kural alan-eşleşmesi.
  Fark önemli: çözüm yeni kaynak değil, doğru alanla kaydetmek.
- **Model turundan ÖNCE offline replay yap** (önceki oturumun notu, hâlâ geçerli).

# Notes For Codex

Codex bu oturumda **koşmadı**. Bu dalda `/review-claude-codex` ve
`/security-review-claude-codex` **hâlâ koşmadı** — zincirin yeri Plan Task 19 sonrasıdır.
Çalışma ağacı şu an temiz; bir sonraki oturum kirli ağaçta review koşturmamalı.
