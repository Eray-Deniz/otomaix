---
task: sektor-bilgi-paketi-plan2
written: 2026-09-19
---

# Resume From

**Task 19 Step 8 BİTTİ — motor koştu, sonuç `blocked`, karşılaştırma yazıldı.**

**SIRADAKİ İŞ: dört kusurun düzeltilmesi. İŞ CLAUDE'DA, doğrudan başlanır.**

**Eray kararı (2026-09-19): tören YOK.** Spec seansı açılmayacak, plan yazılmayacak.
Kusurlar adlandırılmış ve ölçülmüş; düzeltme doğrudan başlar. **Review gerekirse
düzeltme sırasında çağrılır** — önden zorunlu kapı YOK.

Okunacak iki yer:
- **`K134-MOTOR-KARSILASTIRMA.md`** (bu klasörde) — motorun sonucu, nedensel zincir,
  mutasyon ölçümleri, kör yargı karşılaştırması.
- **`TASK.md` → `# Open Problems`** ilk kalemi — dört kusur, her birinin ölçümü ve
  önerilen çözüm yönü.

**Dört kusur, tek satırla:** (1) sentez ham kaynakları görmediği için `kaynak_iddia`
numaralarını tahmin ediyor → 8 red · (2) yetkilendirilemeyen dönem adaya boş kabuk
olarak yazılıyor → şema reddi · (3) iki bayrak kapısı birbirini kilitliyor → bayraklı
kalem içeren paket aktive edilemez · (4) plan sırası `katman1`'i motordan sonraya
koyuyor, motor onu kapı olarak okuyor. Bunlardan bağımsız beşinci kalem: ölü koşu iş
kabul etmeye devam ediyor.

**İlk üçü birlikte kapatılınca koşu YEŞİL** (mutasyonla ölçüldü: `activation_eligible`,
46 karar uygulanıyor, açık soru 0). Düzeltme bittikten sonra **yeni koşu** açılır —
bu koşu tükendi.

**Koşu `kosu-222706dc…` TÜKENDİ.** Satır `durum='tamamlandi', sonuc='blocked'`.
`motor` karşılaştır-ve-yaz olduğu için ikinci kez yazmaz; `yazim` ise
`sonuc='activation_eligible'` ister. **Bu koşudan taslak çıkmaz.** Yeni koşu
açmak `denetim` (956 sn) + `sentez` (941 sn) turlarını yeniden koşturmak demektir
ve K-134 körlük tabanı (zaten kullanıldı) tekrar kurulamaz.

**Kusurların ayrıntısı — kanonik yer `TASK.md` Open Problems; buradaki özet
düzeltmeye başlarken elde durması içindir:**

1. **Sentez ham kaynakları görmüyor** → `kaynak_iddia` numaralarını tahmin ediyor
   → **8 karar** alan-eşleşmemesinden düşüyor (`ton_ve_dil`, `yasaklar[1]`,
   `yasaklar[4]` ve beş video sahnesi). Çözüm yönü: iddia→alan dizinini sentez
   paketine makine-üretimi EK olarak vermek (dizin motorda zaten üretiliyor,
   `engine.py:821 _arastirma_iddialari`). **Sözleşme değişikliği gerektirir.**
   Yanında küçük bir kalem: motorun `iddia-arastirmada-yok` etiketi yanıltıcı,
   gerçek sebep "alan tutmuyor".
2. **Yetkilendirilemeyen dönem adaya boş kabuk olarak yazılıyor** → 10 Kasım tek
   kaynaklı, beş anahtarı da `cogunluk-yok` ile düştü, geriye boş `ozel_gun`
   girdisi kaldı ve şema kapısı reddetti. Çoğunluk yetkisi olmayan dönem adaya
   HİÇ yazılmamalı.
3. **Bayrak kapıları birbirini kilitliyor** → biri sentezin düz yazısını, diğeri
   denetçinin tipli sütununu okuyor; bayraklı kalemi anan her karar açık soru
   üretiyor ve açık soru blokluyor. Bu hâliyle bayraklı kalem içeren paket
   `activation_eligible` OLAMAZ. Çözüm yönü: tüketimi düz yazıdan değil yapısal
   bir alandan oku, iki kapıyı tek kaynağa bağla.
4. **Sıra kusuru (küçük)** → motor Katman-1 tasdikini kapı olarak okuyor ama plan
   sırası `motor → yazım → katman1`. `attest_katman1`'in taslak ön koşulu yok;
   sıra `katman1 → motor` olmalı.

**Bu dörtten BAĞIMSIZ beşinci kalem:** ölü koşu iş kabul ediyor — `mark_incomplete`
koşulsuz ve terminal; hiçbir adım başlarken koşunun canlı olup olmadığına bakmıyor,
geri açma yolu yok. Bu oturumda satır elle onarıldı (Eray onayı), **kusur DURUYOR.**

# Verification

**Bu oturumda ÜRETİM KODU DEĞİŞMEDİ.** Yazılanlar: `K134-MOTOR-KARSILASTIRMA.md`
(yeni), `TASK.md`, `HANDOFF.md`. Test takımı koşulmadı — değişen kod olmadığı için
gerekmedi.

**Koşan komutlar ve taze çıktıları:**

| Ne | Sonuç |
|---|---|
| `motor --run-id kosu-222706dc…` (1. deneme) | **rc=1** — `koşu sonucu ZATEN yazılmış … durum='tamamlanmadi'` |
| koşu satırı onarımı (`UPDATE … WHERE durum='tamamlanmadi' AND sonuc IS NULL`) | `UPDATE 1` |
| `motor --run-id kosu-222706dc…` (2. deneme) | **rc=0, 0,47 sn, `sonuc: blocked`** |
| `psql` koşu satırı | `durum=tamamlandi`, `sonuc=blocked`, `engine_version=2.15.0` |
| `psql` artefaktlar | `review` ×2 (25682 + 11690), `synthesis` ×1 (40671) |
| `engine_diff` | `uygulanan_karar_sayisi: 0`, `dusen_birim_sayisi: 14`, `yazim_hatalari: 3` |
| `barrier_report` | `payda: 0`, eşikler `null` (K-24 pasif) |
| Araştırma evreni yeniden kuruldu | K1 17 · K2 39 · K3 42 iddia; anılan 19 etiketin 19'u VAR |
| `engine.decide` mutasyon probu (bellekte, DB'ye yazmadan) | taban varyantı canlı koşumu BİREBİR üretti |

**Ölçülen mekanizmalar (hepsi dosya açılarak):**
- `runs.py:837` — `record_result` yalnız `durum='calisiyor' AND sonuc IS NULL` satıra yazar.
- `runs.py` yedi kapı — `yazim`/`onay`/`aktive-et` `sonuc='activation_eligible'` ister.
- `engine.py:1047` — `any(bağsız) → reddet`; bir tek komşu-alan atıfı kararı düşürür.
- `engine.py:1180` — bayrak, **denetçi satırının tipli sütunundan** okunur.
- `engine.py:_bayrak_tuketimi` — bayrak, **sentezin `kanit`+`gerekce` düz yazısından** okunur.
- `engine.py:2372-2379` — yazım kapısı düşerse aday TÜMÜYLE atılır.
- `hakem-sentez-gorevi.md:112-128` — ek listesi; ham araştırma raporları listede YOK.
- `runs.py` `_write_attestation` — katman1 tasdikinin taslak ön koşulu YOK.

**DENENMEYEN / DOĞRULANMAYAN — yeşil sayılmaz:**
- **`yazim` · `katman1/2` · `onay` · `aktive-et` ayakları HÂLÂ hiç koşmadı.**
- **ÖLÇÜLDÜ, ama mutasyonla:** üç kusur birlikte kapatıldığında `engine.decide`
  **`activation_eligible`** veriyor (46 karar uygulanıyor, açık soru 0, yazım
  hatası 0). Bu, düzeltmelerin GERÇEK kodda aynı sonucu vereceğinin kanıtı
  DEĞİLDİR — girdi elle kırpıldı, kod değişmedi.
- Kusur 1'in çözüm yönü (iddia→alan dizini) **denenmedi**; sözleşmeye eklenince
  sentezin doğru numarayı seçeceği bir VARSAYIMDIR, ölçüm değil.
- **Prob bir kez kirletti:** ilk mutasyon varyantı atıfları kırparken denetçi
  satırlarını bırakmış, `ton_ve_dil` için sahte bir "daha derin kanıt sorunu"
  üretmişti. Bağın çift yönlü olduğu görülünce düzeltildi. Sonraki oturum
  mutasyon kurarken kırpılan şeyin KARŞI ucunu da kırpsın.
- `ozel_gun` ve `takvim_temalari` alanlarının çalışma anında içerik üretimini nasıl
  beslediği hâlâ ölçülmedi (önceki oturumdan devrediyor).

# Risks

- **Yeni koşu açmak pahalıdır ve körlük tabanını geri getirmez.** İki model turu
  (~32 dk, ölçülmüş) + para; K-134 kalibrasyonu bir kez alınabilirdi, alındı.
- **Kusur 2 (bayrak kilidi) kapatılmadan hiçbir koşu aktivasyona ulaşamaz** —
  denetçiler rutin olarak bayrak koyuyor (bu koşuda 5 birim).
- **Kusur 3 duruyor:** bir sonraki koşuda da düşen bir adım koşuyu sessizce
  öldürebilir ve sonraki adımlar bunu fark etmeden çalışmaya devam eder.
- **SPK kararı bilinçli risk kabulüdür** (önceki oturumdan devrediyor): paket
  doğrulanmamış bir hukuki iddia taşıyacak, gerekçe `K134-KOR-YARGI.md`'de.
- **Operatör eklemeleri** (yerel görsel kodlar · Ramazan/Kurban · yılbaşı ·
  23 Nisan/29 Ekim) mekanik kaynak bağı OLMAYAN kalemlerdir; Step 9'a taşındılar
  ve paketin "her kalem bir kaynağa bağlıdır" garantisini zayıflatırlar.
- **Sentez klasörü doluysa tur koşmaz** (`mkdir` `exist_ok` kullanmıyor). Düşen
  denemeler `DUSMUS-<tarih>-<sebep>-<koşu>` adıyla duruyor; silme YOK.

# Notes For Claude

- **Bu oturumun dersi: "kalıcı zarar YOK" diye devredilen beklentiyi ÖLÇ.** Geçen
  HANDOFF "motor koşumu durumu düzeltir" diyordu; motor o satıra hiç ulaşamıyordu.
  Devralınan her beklenti, üzerine iş kurulmadan önce koşulur.
- **Motorun red etiketine güvenme, mekanizmayı aç.** `iddia-arastirmada-yok`
  "numara yok" diyor; numaraların hepsi vardı, sorun alan eşleşmesiydi. Etiket
  yanlış kapıyı gösteriyor.
- **Mutasyon probu ucuzdu ve işe yaradı** (`decide` saf, 0,47 sn, DB'ye yazmıyor).
  Taban varyantının canlı koşumu birebir ürettiği ÖNCE doğrulandı — prob kendi
  hatasını ölçmesin diye.
- **Eray ham kanıt istiyor, özet değil** (önceki oturumdan, hâlâ geçerli).
- **Model turundan ÖNCE offline replay yap** (hâlâ geçerli).
- **Kendi önerine İlke 7'yi uygula:** aşağıdaki üç kusur için "düzeltelim" demeden
  önce her birinin tarihli evi var mı, over-bundle mı diye bak.

# Notes For Codex

Codex bu oturumda **koşmadı**. Bu dalda `/review-claude-codex` ve
`/security-review-claude-codex` **hâlâ koşmadı** — zincirin yeri Task 19 sonrasıdır.

**Eray kararı (2026-09-19):** dört kusurun düzeltilmesi için önden zorunlu bir review
kapısı YOK; **gerekirse düzeltme sırasında çağrılır.** Kusur 1 donmuş sözleşmeye ve
kusur 3 motorun kapı anlamına dokunuyor — review çağırmak için en makul iki yer bunlar.
Çalışma ağacı review'dan önce temiz olmalı; kirli ağaçta review koşturma.
