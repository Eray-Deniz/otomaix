---
task: brief-sozlesmesi-kaynak-bolumu-makine-okunur
written: 2026-09-07
---

# Resume From

**GÖREV KAPANDI — dört ayağın dördü de indi. Devam edilecek bir iş YOK.**

- Ayak 1+2 — dış depo `7964ed6`: sözleşmenin `═══ 5. ÇIKTI FORMATI ═══` bölümü yapısal
  sözleşmeye çevrildi; denetçi görev metni hizalandı.
- Ayak 3 — monorepo `868f50a`: pin manifesti yenilendi, testin sütun türetmesi düzyazıdan
  birebir başlık satırına taşındı.
- Ayak 4 — monorepo `854373d`: mekanik kapı olumsuz çıkarımdan **olumlu yapısal sözleşmeye**
  geçti; ayıraç vekili (`_C_AYIRAC_RE`) söküldü; BÜTÜNLÜK kontrolü eklendi; Task 7'nin
  "makineyle DOĞRULANMADI" kapsam beyanı ÜÇ yerden de kalktı.

**Bu görevi doğuran Plan 2 kalemi de KAPATILDI** (`docs/active/sektor-bilgi-paketi-plan2/TASK.md`,
Decisions Log'daki `url-bicimi` kalemi) — iki yerde birden yaşamıyor.

**Sıradaki iş bu görevde değil, Plan 2'de:** Task 8 → (Eray onayı) → Task 9.

# Verification

**Koşulan komutlar ve TAZE çıktıları (2026-09-07, kontrolörün KENDİ koşumları):**

- `cd apps/social/backend && source .venv/bin/activate && python -m pytest tests/ -q`
  → **5913 passed in 697.50s**, exit 0, temiz ağaçta.
  Taban 5349'du; +564 = 540 yeni çit hücresi (altıncı gövde) + 24 yeni Bölüm C testi.
  **Hiçbir test silinmedi, hiçbir davranış iddiası kaybolmadı.**
- `pytest tests/test_contract_pin.py` → **32 passed** (ayak 3 oturumunda; sözleşme bu oturumda
  DEĞİŞMEDİ, pin dokunulmadı).
- **Kaçış kapandı, mesaj KÜMESİ farkıyla:** `- Düz yazı, devamı https://example.com/kaynak`
  → önce `gecti / 0 not`, şimdi `notlu-gecti / 1 not`
  (*"Bölüm C sözleşmenin başlık satırını taşımıyor"*). Kaçışı ilan eden TRIPWIRE testi
  ateşlendi ve artık TERSİNİ ölçüyor.
- **Kapanış ÜRETİLMİŞ matrisle:** 21 hücre — 6'sı doluluk ekseni ve **sözleşmenin sütun
  listesinden TÜRER** (sütun eklenirse hücre kendiliğinden doğar), 7 değer, 8 şekil.
  Mutasyon kolu ÜÇ ayrı seam'e basıyor: `_c_satir_ihlalleri` · `_c_kapsama_ihlalleri` ·
  `C_TABLOSU_SUTUNLARI` sabitinin kendisi. Boş-küme kolu temiz kaynağın izlerin HİÇBİRİNİ
  üretmediğini ölçüyor.
- **Dört sabit de PİNDEN okunuyor** (`test_bolum_c_sabitleri_pinlenmis_sablondan_okunur`):
  başlık satırı · 15 kelime sınırı · `tarih-yok` yazımı · `evet`/`hayır` kümesi.
- **DÜZELTMENİN KENDİ YAN ETKİSİ ÖLÇÜLDÜ.** Eski modül `git show HEAD:` ile çıkarıldı ve 24
  hücrede yan yana koşuldu: eski sürümün not ürettiği **tek** hücrede yeni sürüm susuyor ve o
  hücre **TEMİZ kaynaktır** — eski kapı sözleşmenin KENDİ başlık satırını *"tam bağlantı
  taşımıyor"* diye yanlışlıyordu. Kaybedilen tek şey bir YANLIŞ POZİTİF.
- **İKİ PROB KİRLENMESİ bulundu ve düzeltildi:** `tablo_sutunlarini_boz` ve
  `gerekce_tablosunu_boz` bütün belgeye uygulanıyordu; sözleşme Bölüm C'yi de tabloya çevirince
  aynı prob iki ailenin notunu birbirine karıştırdı (ölçüldü: `_tablo_sekli_ihlalleri`
  sökülünce `sütun` izi Bölüm C'nin notundan geliyordu). İkisi de Bölüm B'ye daraltıldı.
- **ÇAKILI SAYILAR TEK GEÇİŞTE ölçüldü** (geçen oturumun dersi): dolu 368→392 · boş 64→40 ·
  bloğa-ait 320→392 · CIT_BICIMLERI 540→648 · CIT_MATRISI 2700→3240 · dilli kayıp 1056→1140 ·
  vacuous 810→1080 · dilsiz kırmızı 720→696 · yeşil 630→924.

**Denenmemiş / doğrulanmamış — dürüst liste:**

- **Sözleşmenin YENİ biçiminde üretilmiş gerçek araştırma çıktısı YOK** (dış depodaki dosyalar
  2026-07-11 tarihli). Araçların tabloyu ne kadar düzgün ürettiği ve **katı biçimin
  yanlış-pozitif oranı ÖLÇÜLMEDİ**. Ev: Plan 2 **Task 19 Step 5**.
- **BÜTÜNLÜK kontrolü sözleşmenin yazılı harfinden bir adım ÖNDE** — sözleşme her alan için
  kaynak satırını kelimesi kelimesine ZORUNLU kılmıyor ("en az 2 bağımsız kaynak HEDEFLE").
  Bugün hiçbir kontrol ELEMEDİĞİ için bedel gürültüdür. **Eray veto ederse geri alınır:** tek
  fonksiyon (`_c_kapsama_ihlalleri`) ve kendi mutasyon kolu var.
- **Bağımsız hakem bu commit'i GÖRMEDİ.** Ev uydurulmadı: Plan 2'nin final inceleme tabanı
  `a806e29` olduğu için commit oraya kendiliğinden girer.
- Kapı hâlâ **anlam** ölçmüyor: bağlantının gerçekten açıldığı ve `iddia` hücresinin kaynağı
  gerçekten özetlediği doğrulanmıyor. İkisi de denetçi katmanının işi ve kapsam beyanında
  dürüstçe yazılı.

# Risks

- **Katı biçim yanlış-pozitif üretebilir** ve bu ÖLÇÜLMEDİ (yukarıda). Maliyet bugün gürültü;
  gürültü de denetçinin işini bozar.
- **Task 19 Step 5 sözleşmeyi ilk kez gerçek çıktıyla sınayacak.** Orada tablo düzgün
  üretilmezse sözleşme metni revize edilir ve pin + kapı ÜÇÜNCÜ kez dokunur.
- Dış depo ve monorepo iki ayrı depodur; bu oturumda yalnız monorepo'ya dokunuldu, pin
  DEĞİŞMEDİ.

# Notes For Claude/Codex

- **Spec değil, spec-input kanoniktir.**
- Kapının beklentisi sözleşmeden **birebir** türetilir, düzyazı özetinden değil. Dört sabit de
  pinlenmiş `_SABLON.md`'den okunuyor; sözleşme değişirse testler kırılır.
- **Kod çiti KULLANIMI sözleşmede YASAKLANDI** — çit zincirini yeniden açma.
- **Prob KİRLENEBİLİR.** Bu oturumda iki prob (`tablo_sutunlarini_boz`, `gerekce_tablosunu_boz`)
  yeni tablo yüzünden yanlış aileyi ölçüyordu ve ikisi de İNANDIRICI sonuç veriyordu.
  Ölçüm beklenmedik çıkınca önce PROBU sorgula.
- **Çakılı sayıları teker teker ölçme** — bu oturumda dokuz sayı tek betikle çıkarıldı ve tek
  seferde yazıldı; geçen oturum aynı işi teker teker yapıp saatler yemişti.
