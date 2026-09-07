---
task: brief-sozlesmesi-kaynak-bolumu-makine-okunur
written: 2026-09-07
---

# Resume From

**DÖRT AYAKTAN ÜÇÜ İNDİ. Kalan tek iş: 4. ayak — mekanik girdi kapısının Bölüm C ailesi.**

- Ayak 1+2 — dış depo `7964ed6`: sözleşmenin `═══ 5. ÇIKTI FORMATI ═══` bölümü yapısal
  sözleşmeye çevrildi (başlık düzeyleri bağlayıcı · gerekçe tablosunun başlık satırı birebir ·
  dönem başlıklarından önce TEK tablo · Bölüm C sabit sütunlu tablo), denetçi görev metni
  yeni biçimle hizalandı.
- Ayak 3 — monorepo `868f50a`: pin manifesti yenilendi, fail-closed doğrulayıcı yeni sürüme
  bağlı, testin sütun türetmesi düzyazıdan birebir başlık satırına taşındı.
- **Ayak 4 — AÇIK.** `brief_doctor.py` Bölüm C'ye hâlâ bir **ayıraç vekiliyle** (`_C_AYIRAC_RE`)
  bakıyor: serbest düzyazıdan *"bu bir eşleme DEĞİL"* çıkarımı yapmaya çalışıyor ve yapamıyor.
  Sözleşme artık sabit sütunlu tablo istediği için kapı **olumlu** doğrulayabilir:
  birebir başlık satırı · 6 sütun · hücre doluluğu · `https://` adres biçimi · `tarih`
  yazımı (`YYYY-AA` / `YYYY-AA-GG` / `tarih-yok`) · `tek kaynak` ∈ {`evet`,`hayır`} ·
  `iddia` ≤ 15 kelime · `alan/dönem` hücresinin kanonik alan/dönem adı olması.

**Kapanış koşulu — kod düzeltmesi tek başına YETMEZ:** Task 7'de konulan *"makineyle
DOĞRULANMADI"* kapsam beyanı `brief_doctor.py` modül docstring'inden KALKMALI (bugün üç ayrı
yerde geçiyor: docstring kapsam listesi · Bölüm C kontrolünün kendi docstring'i · aile raporu
metni). Kalkmazsa beyan bayatlar ve bayat beyan, beyan olmamaktan kötüdür.

**Sıra:** bu ayak → Plan 2 Task 8 → Task 9. Yuva hâlâ **Task 9'dan ÖNCE**; gerekçesi TASK.md'de.

**Bu ayak yürütme işidir, tasarım turu DEĞİL.** Metin kararları (dört soru) 2026-09-07'de
CEVAPLANDI ve sözleşmeye indi; yürütücünün karar sorması gereken bir şey kalmadı.

# Verification

**Koşulan komutlar ve TAZE çıktıları (2026-09-07, kontrolörün kendi koşumları):**

- `pytest tests/test_contract_pin.py` → **32 passed**, yeni sözleşme sürümüne bağlı.
- `pytest tests/ -q` (tam küme, HEAD `cad705c`) → **5349 passed in 669.10s**, exit 0, temiz ağaç.
- Sözleşme pin doğrulayıcısı: sıfır sapma; dış depo `7964ed6` ↔ monorepo manifesti hizalı.
- Kapının bugünkü açığı ölçüldü: `- Düz yazı, devamı https://example.com/kaynak` → **`gecti`,
  0 not**. Üç hakem turunda vekili sertleştirme yakınsamadı; nokta düzeltmesi AÇILMADI.

**Bu görev kapanırken doğrulanması ZORUNLU olanlar:**

- Bölüm C ailesi olumlu yapısal sözleşmeye çevrildi ve yukarıdaki açık probu artık **not
  düşüyor** (kapanış, seçilmiş örnekle değil **üretilmiş matrisle** kanıtlanır — kap çarpımını
  değil ayırt eden ekseni büyüt).
- **"Makineyle doğrulanmadı" kapsam beyanı üç yerden de KALDIRILDI** (grep ile sweep et,
  gördüğün örnekten deseni türetme).
- Tam test kümesi düşmedi: **taban 5349**.
- Denetçi görev metninin Bölüm C'ye atfı yeni biçimle hâlâ hizalı.
- Yeni kontrolün kendi yan etkisi ölçüldü: eski sürüm `git show` ile çıkarılıp yeni sürümle
  yan yana koşuldu, kaybolan gerçek not sayısı raporlandı.

**Doğrulanmamış — dürüst liste:**

- **Sözleşmenin YENİ biçiminde üretilmiş gerçek araştırma çıktısı YOK** (dış depodaki dosyalar
  2026-07-11 tarihli). Araçların tabloyu ne kadar düzgün ürettiği ve katı biçimin yanlış-pozitif
  oranı **ÖLÇÜLMEDİ**; ilk gerçek ölçüm Plan 2 Task 19 Step 5'te doğacak.
- İki ürün gerilimi (tablo tekrarı ↔ rapor uzunluğu; katı biçim ↔ oturmayan bulgunun düşmesi)
  sözleşme metninde ÇÖZÜLDÜ (15 kelime sınırı · Bölüm D'ye yönlendirme) ama **gerçek çıktıyla
  sınanmadı** — aynı yuvada ölçülecek.

# Risks

- **SON TARİH KAÇIRILIRSA maliyet ikiye katlanır.** Task 19 Step 5 üç araştırmayı tek seferde
  yeniden üretir; sözleşme ondan sonra değişirse araştırmalar ikinci kez ürettirilmek zorunda.
- **Task 9/10'dan sonra yapılırsa denetçi koduna geri dönmek gerekir.**
- **Katı biçim yanlış-pozitif üretebilir.** Bugün girdi kapısında hiçbir kontrol ELEME yapmıyor
  (hepsi not), yani maliyet gürültü — ama gürültü de denetçinin işini bozar.
- **Dış depo ve monorepo iki ayrı depodur.** Bu ayak yalnız monorepo'ya dokunuyor; sözleşme
  metni değişMEYECEK. Değişirse sıra yeniden: önce sözleşme, sonra pin, sonra kod.
- **`_C_AYIRAC_RE` yalnız Bölüm C'de kullanılmıyor olabilir** — sökmeden önce çağrı yerlerini
  tara; komşu aileyi bayatlatan bir düzeltme bu görevde daha önce olmadı ama sınıfı biliniyor.

# Notes For Claude/Codex

- **Spec değil, spec-input kanoniktir** — Bölüm C'nin kontrol tanımı orada (§7.3 tablosu).
- Sözleşmenin bağlayıcı metni: dış depo `_SABLON.md`, `═══ 5. ÇIKTI FORMATI ═══`. Kapının
  beklentisi o metinden **birebir** türetilir, düzyazı özetinden değil (Ayak 3'ün dersi).
- **Kod çiti KULLANIMI sözleşmede YASAKLANDI** — kapı çit içini içerik saymaz; bu, üç turluk
  çit zincirinin doğrudan çıktısıdır, yeniden açma.
- **Tehdit modeli:** girdi Gemini/Claude/ChatGPT araştırma çıktısıdır — ÖZENSİZ olabilir,
  SALDIRGAN değil. "Derin iç içe yapı" gerçekçi bir arıza biçimi değildir; oraya tur harcama.
- Bu görevin doğduğu yer: Plan 2 Task 7 / checkpoint 6, `[checkpoint-override turn 3]` etiketli
  Open Problems kalemi. **Bu görev kapanınca o kalem de kapatılmalı** — iki yerde birden
  yaşamasın.
