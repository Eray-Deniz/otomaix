---
task: sektor-bilgi-paketi-plan2
adim: Plan Task 19 Step 8 (motor koşumu + K-134 kalibrasyon karşılaştırması)
kosu: kosu-222706dc643b4b64b66a1f3826f02c1b
sektor: kuyumculuk
tarih: 2026-09-19
taban: K134-KOR-YARGI.md (motor koşmadan ÖNCE yazıldı)
---

# Motorun sonucu

| Ne | Ölçüm |
|---|---|
| Komut | `motor --run-id kosu-222706dc…` (`--politika-ayari` VERİLMEDİ) |
| Çıkış | `rc=0`, **0,47 sn** |
| Sonuç | **`blocked`** |
| Sebepler | `acik-soru-var` · `ilk-kosuda-degisiklik-yok-gecersiz` · `uygulanan-aday-yazim-kapisini-gecmiyor` |
| Motor sürümü | `2.15.0`, ayar sha `c15d1c45…` |
| Uygulanan karar | **0** (`engine_diff.uygulanan_karar_sayisi`) |
| Bariyer | `payda: 0`; eşikler `null` (K-24 gereği pasif) |

**Koşumdan önce elle yapılan onarım (Eray onayı ile):** koşu satırı
`durum='tamamlanmadi'` idi — sentezin 4. denemesi 18.09 17:20'de düşüp satırı
işaretlemiş, 18:10'da BAŞARILI olan 5. deneme işareti geri almamıştı. Satır
`durum='calisiyor', sebep=NULL` yapıldı (tek satırlık koşullu güncelleme;
`sonuc IS NULL` şartıyla). Alternatif, `denetim` (956 sn) + `sentez` (941 sn)
turlarını yeni bir koşuda tekrarlamaktı; bu, K-134 körlük tabanını da
geçersiz kılardı.

---

# Nedensel zincir — ölçülmüş

Motorun `blocked` demesi tek bir yargı değil, üç halkalı bir zincirdir:

**1. 52 `ekle` kararının 14'ü reddedildi.**

| alan | geçen | reddedilen | red sebebi |
|---|---:|---:|---|
| ozel_gun | 20 | 5 | `cogunluk-yok` (10 Kasım'ın beş anahtarı) |
| video_kodlar | 5 | 5 | `iddia-arastirmada-yok` (sahne havuzunun tamamı) |
| yasaklar_ve_hassasiyetler | 3 | 2 | `iddia-arastirmada-yok` |
| ton_ve_dil | 0 | 1 | `iddia-arastirmada-yok` |
| takvim_temalari | 1 | 1 | `referans-uyusmuyor` (düğün-nişan) |
| cta_kaliplari · gorsel_kodlar · kanca_kaliplari · kapsam | 9 | 0 | — |
| **TOPLAM** | **38** | **14** | |

**2. Kalan 38 karardan kurulan paket YAZIM KAPISINDAN geçmedi** — üç şekil hatası,
üçü de doğrudan yukarıdaki redlerin sonucu:

- `eksik alan(lar): ['ton_ve_dil']` ← o alanın TEK kararı reddedildi
- `video_kodlar['sahne'] boş havuz` ← beş sahnenin beşi de reddedildi
- `ozel_gun['10-kasim-ataturk-u-anma-gunu']` boş anahtar kümesi ← beş anahtarın beşi de reddedildi

**3. Yazım kapısı düşünce motor adayın TAMAMINI atar** (`engine.py:2372-2379` —
"yazılamayan bir çifti koşu satırına basmak, hatayı bir katman ileri taşımaktır").
Uygulanan karar 0 olur; ilk koşuda değişiklik yoksa sonuç `blocked` (K-91).

Bunların üzerine **`acik-soru-var`** bağımsız olarak zaten bloklardı: 18 açık
soru kimliği = sentezin 10 sorusu + motorun beş birimde ürettiği 8 bayrak
bulgusu (iki ayrı kontrol aynı birime dokunabiliyor).

---

# Redlerin kökü: sentez ham kaynakları GÖREMİYOR

`iddia-arastirmada-yok` etiketi **yanıltıcıdır**. Ölçüldü: reddedilen sekiz
kararın andığı iddia numaralarının **hepsi** araştırma evreninde VAR
(evren `brief-doctor` raporlarından yeniden kuruldu: K1 17, K2 39, K3 42 iddia;
anılan 19 etiketin 19'u bulundu). Red sebebi numaranın yokluğu değil,
**alan eşleşmemesi**:

| karar | alanı | anılan iddia | iddianın alanı | bağ |
|---|---|---|---|---|
| ton_ve_dil | `ton_ve_dil` | K1#3, K2#3, K2#4, K3#1, K3#2 | `ton_ve_dil` | bağlı |
| | | K1#6, K2#24, K3#22 | `yasaklar_ve_hassasiyetler` | **bağsız** |
| yasaklar[1] | `yasaklar_ve_hassasiyetler` | K2#18, K3#20, K3#21 | `yasaklar…` | bağlı |
| | | K1#5 | `ton_ve_dil` | **bağsız** |
| video sahne ×5 | `video_kodlar` | K2#12 | `video_kodlar` | bağlı |
| | | K3#7 | `kanca_kaliplari` | **bağsız** |

Motor kuralı `any(bağsız) → reddet`'tir (`engine.py:1047`): **anılan iddialardan
BİRİ bile komşu alandan geliyorsa karar tümüyle düşer** — o kararda geçerli,
alanı tutan iddialar da olsa.

**Sentez bunu neden yaptı — kendi ağzıyla, çıktının ilk cümlesi:**

> "Ham kaynaklara (KAYNAK-1/2/3 raporları) bu koşuda erişim yok — çalışma
> dizininde yalnız görev dosyası var. … Aynı sebeple `kaynak_iddia`
> numaralarının Bölüm C `alan/dönem` hücrelerini göremedim; numaraları, iki
> denetçinin o alan altında kullandığı numaralardan seçtim (çoğunluk
> kullanımına göre) — kalan risk fail-closed'dur."

**Sözleşme bunu doğruluyor:** sentez paketinin ek listesi EK-A · EK-F/G · EK-H ·
EK-I · EK-J · EK-K · EK-L'dir (`hakem-sentez-gorevi.md:112-128`). **Ham araştırma
raporları listede YOKTUR** — yani sentezin iddia→alan hücresini görmesi tasarım
gereği mümkün değil. Buna rağmen sözleşme `kaynak_iddia` alanını zorunlu tutuyor
ve motor onu alan eşleşmesiyle mekanik doğruluyor.

**Sınıf tanıdık:** bu, `oge_sha` bulgusunun (sözleşme izolasyonun yasakladığı
bir şeyi istiyor) ve Soru 3'ün (sentez doğru sonucu yanlış gerekçeyle verdi)
aynı sınıfıdır — sözleşme yapısal bir bağ istiyor, paket o bağı kurmak için
gereken yapıyı taşımıyor.

Dizinin kendisi motorda zaten üretiliyor (`engine.py:821 _arastirma_iddialari`).

## Mutasyon ölçümü — hangi kusur neyi taşıyor

Motorun girdileri canlı koşudan yeniden kuruldu ve `engine.decide` **bellekte**
(DB'ye yazmadan) varyantlarla koşuldu. Taban varyantı canlı koşumu birebir
üretti — prob sadık:

| varyant | sonuç | uygulanan | red | açık soru | yazım hatası |
|---|---|---:|---:|---:|---:|
| **A — taban** (canlı koşumun aynısı) | `blocked` | 0 | 14 | 18 | 3 |
| **B2 —** alan-dışı atıf + ona bağlı denetçi satırı birlikte kırpıldı | `blocked` | 0 | **6** | 24 | **1** |
| **C2 —** B2 + 10 Kasım adaydan çıktı + bayraklar temiz + sentez açık sorusu yok | **`activation_eligible`** | **46** | **1** | **0** | **0** |

**B2'nin öğrettiği:** alan-dışı atıf tek başına **8 reddi** taşıyor — `ton_ve_dil`,
`yasaklar[1]`, `yasaklar[4]` ve `video_kodlar` sahne havuzunun beşi. Düzeltilince
üç yazım hatasından İKİSİ kapanıyor; geriye yalnız 10 Kasım kalıyor.

**C2'nin öğrettiği — en önemli ölçüm:** üç kusur birlikte kapatıldığında koşu
**`activation_eligible`** oluyor: 46 karar uygulanıyor, açık soru sıfır, yazım
hatası yok. Yani **hat çalışıyor; bu koşuyu bloklayan şey üç adlandırılmış
kusurdur, tasarımın kendisi değil.** (Kalan tek red düğün-nişan satırının
`referans-uyusmuyor`'u; paketi bloklamıyor, yalnız o cümle girmiyor.)

**Prob kusuru — düzeltildi, kayda geçiyor.** İlk B varyantı atıfları kırpıp
**denetçi satırlarına dokunmamıştı**; bu, atıfsız kalan denetçi satırları
yüzünden `ton_ve_dil` ve `yasaklar[4]`'ü `iddia-denetcide-yok` ile düşürdü ve
"atıf muhasebesinden daha derin bir kanıt sorunu var" sonucuna götürdü. O sonuç
**probun kendi eseriydi** — bağ çift yönlüdür (her iddia bir satırda geçmeli VE
atıf yapılan her satır en az bir iddiayı taşımalı, `engine.py:1108-1126`), yani
atıf kırpılırken ona bağlı satır da kırpılmalıydı. Düzeltilmiş B2 ölçümü
yukarıdadır.

**Bayrak ayağı (C2 içinde, iki yönlü):** motorun kendi 18 açık sorusunun
**tamamı** bayrak kontrollerinden geliyor — bayraklar temizlenince bulgu sayısı
sıfıra iniyor, geri konunca 18'e çıkıyor.

## Bayrak kapılarının birbirini kilitlemesi — ölçüldü

Motorda iki ayrı bayrak kontrolü var ve **aynı kalem için ikisi birden
kaçınılmaz**:

- `bayrak_tuketimi` (`engine.py:_bayrak_tuketimi`) sentezin **kendi `kanit` +
  `gerekce` düz yazısını** tarar. Sentez bayrağı adıyla anıp "tükettim" diye
  açıkladığı için kontrol onu "tüketilmemiş bayrak motora ulaştı" sayıyor.
- `yeni_oge_cogunlugu` ise **denetçi satırının tipli `bayraklar` sütununu**
  okur (`engine.py:1180`). Sentezin o sütuna erişimi yoktur.

Yani bayraklı bir denetçi satırını anan karar için: bayrağı gerekçede AÇIKLARSA
birinci kontrol, AÇIKLAMAZSA ikinci kontrol açık soru üretir; satırı hiç
anmazsa `referans-yok` ile reddedilir. **Açık soru bloklar** (`BULGU_ETKILERI`,
`acik_soru → ETKI_BLOKLAR`). Bu hâliyle, denetçinin bayrakladığı bir kalemi
içeren paket `activation_eligible` olamaz.

**Sınıf:** serbest düz yazıdan "X tüketildi" negatifini kalıp eşleştirmeyle
kanıtlama denemesi — daha önce de yakınsamadığı ölçülmüş bir desen.

---

# Kör yargı ↔ motor karşılaştırması (spec §15.2)

**Okuma uyarısı:** dört yargı motorun göremeyeceği girdiye dayanır. Motorun o
satırlarda `açık-soru` üretmesi HATA DEĞİLDİR.

| # | Konu | Operatörün kör yargısı | Motorun davranışı | Fark sınıfı |
|---|---|---|---|---|
| 1 | SPK / yatırım dili | Dil kuralı KALSIN + geniş çerçeve `yasaklar`'a | `ton_ve_dil` kararı REDDEDİLDİ, alan pakete hiç girmedi; `yasaklar`ın 2 satırı da düştü | **Mekanizma** — yargı uyuşmazlığı değil, atıf muhasebesi |
| 2 | Taksit sınırı | Yasak satırı GİRSİN (operatör doğrulaması), CTA GİRMESİN | Açık soru olarak taşındı | **Beklenen** — doğrulama motorun girdisinde yok |
| 3 | Yerel görsel kodlar | GİRSİN (operatör eklemesi) | `gorsel_kodlar` kararı GEÇTİ ama "tüketilmemiş bayrak" bulgusuyla açık soru işaretlendi | **Beklenen + yeni bilgi** |
| 4 | Düğün-nişan / mevlüt | Şimdiki hâli KALSIN (takvim özetinde serbest cümle) | `takvim_temalari[1]` REDDEDİLDİ (`referans-uyusmuyor`) → cümle pakete girmiyor | **GERÇEK ÇELİŞKİ** |
| 5 | Ramazan + Kurban | İKİSİ DE girsin (operatör eklemesi) | Adayda yok; motor işlem yapmadı | **Beklenen** |
| 6 | Yılbaşı | `ticari-firsat` olarak girsin | Adayda yok | **Beklenen** |
| 7 | 23 Nisan + 29 Ekim | İkisi de saf kutlama olarak girsin | Adayda yok | **Beklenen** |
| 8 | Kök rehber kaybı | Hat kusuru; iş 1 tarihli eve, iş 2 düşürüldü | Motorun konusu değil | — |
| 9 | Kaynak-1'in boş alanları | Kaynak kusuru kaydı | 10 Kasım'ın 5 anahtarı `cogunluk-yok` ile düştü — aynı kusurun ölçülmüş yüzü | **Doğrulandı** |
| 10 | CTA alt sınırı | 4 kalıpla ilerlensin | 4 CTA kararının 4'ü de geçti | **Uyum** |

**Sayısal özet:** 10 sorunun 1'inde gerçek çelişki (#4), 1'inde mekanizma kaynaklı
sapma (#1), 4'ünde beklenen körlük farkı (#2, 5, 6, 7), 1'inde uyum (#10),
1'inde doğrulama (#9), 2'si motorun konusu dışı (#3 kısmen, #8).

## Motorun operatörde OLMAYAN katkısı — bayrak bulguları (5 birim, 8 bulgu)

Motor, sentezin "bayrağı tükettim" beyanını mekanik olarak sınadı ve beş birimde
**denetçi satırının tipli sütununda bayrağın HÂLÂ durduğunu** ölçtü:

| birim | alan | duran bayraklar |
|---|---|---|
| ku-3335fef2cbff | `gorsel_kodlar` | eski-kaynak, kaynak-bagimli, metin-ogesi, yerel-degil |
| ku-006f6d1b827b | `kanca_kaliplari[2]` | kaynak-bagimli |
| ku-f578eaa92003 | `ozel_gun/sevgililer-gunu/gorsel_vurgu` | genel-gecer |
| ku-7f5c1f423ff4 | `ozel_gun/dunya-kadinlar-gunu/gorsel_vurgu` | yerel-degil |
| ku-64c2743e30af | `video_kodlar/sahne[0]` | kaynak-bagimli |

Operatörün kör yargısı bu beş kalemi görmüyordu; motorun kattığı bilgi budur.
Ne var ki yukarıda ölçüldüğü gibi, bu bulgular sentezin bir kusurundan değil,
iki bayrak kapısının birbirini kilitlemesinden doğuyor.

---

# Bu koşunun durumu

**Koşu 222706dc TÜKENDİ.** `motor` karşılaştır-ve-yaz'dır (`runs.py:837`) — satır
artık `durum='tamamlandi', sonuc='blocked'` ve **ikinci bir motor koşumu kabul
edilmez**. `yazim` ise `sonuc='activation_eligible'` ister (`runs.py` yedi kapı) —
bu koşudan taslak ÇIKMAZ.

**Ayrıca ölçüldü — sıra kusuru:** motor, Katman-1 tasdikini otomatik kapı olarak
okuyor (`sector_pipeline_cli.py:958`) ve tasdik yokken `regresyon_kapisi` bulgusu
üretiyor. Plan Task 19 sırası ise `motor → yazım → katman1`. `attest_katman1`'in
taslak ön koşulu YOKTUR (`runs.py`, `_write_attestation`) — yani katman1 motordan
ÖNCE tasdiklenebilir ve plan sırası bu kapıyla çelişiyor. Bu koşuda etkisi
ikincildi (`regresyon_kapisi` yalnız aktivasyonu engeller, değişiklik yokken
sebep listesine bile girmedi), ama bir sonraki koşuda sıra düzeltilmezse aynı
bulgu tekrar çıkar.

---

# Bayrak kapılarının iki ölçümü — uzlaştırma (2026-09-20)

**Neden iki ölçüm var:** bu dosyanın yukarıdaki gövdesi **2026-09-19**'un fotoğrafıdır ve
motor **2.15.0** ile alınmıştır. Kusur 1 ve 2 düzeltmeleri (`c64861f` · `9e4e21a` · `16ae7c6`)
ret yollarını değiştirdi: EK-M iddia dizini bağlandıktan sonra satırlar **daha erken** düşüyor
(`iddia-alani-uyusmuyor`), yani çoğunluk kontrolünün bayrak bloğuna **daha az satır ulaşıyor**.
Bu yüzden aynı koşu kimliği iki farklı sayı verir. İkisi de doğrudur; **karşılaştırma yapan
okuyucu motor sürümünü birlikte okumalıdır.**

| Ölçüm | Motor | Açık soru (motorun kendi bulgusu) | Bayrak bulgusu | Bayraklı satır / pakete girecek metni kirli olan |
|---|---|---|---|---|
| 2026-09-19 (yukarıdaki gövde) | 2.15.0 | **18** | 18 (5 birim · 8 bulgu tablosu §"Motorun operatörde OLMAYAN katkısı") | ölçülmedi |
| 2026-09-20 (kusur 3 turu) | 2.17.0 | **8** | 8 → kapı A 5 · kapı B 3 | **11 / 0** |

**`11` sayısı nedir:** karar günlüğünde ÜÇ yüzeyden herhangi birinde bayrak taşıyan karar
satırı sayısı (A: sentezin `kanit`+`gerekce` düz yazısı = 5 · B: denetçinin tipli `bayraklar`
sütunu = 10 · C: pakete girecek öğe metni = **0**). Birleşimi 11 satırdır. Yukarıdaki gövdenin
"5 birim" tablosu yalnız **kapı B'nin bulgu ürettiği** birimleri sayar — farklı bir küme,
çelişki değil.

**Yazım kapısı kapsamı (aynı gün, aynı koşunun gerçek adayı):** 60 metin hücresine tek tek
`[eski-kaynak]` konduğunda `structural_errors` **17**'sini reddetti, **43**'ünü geçirdi;
reddedilenlerin tamamı CTA yüzeyleri (`cta_kaliplari` 12 + `ozel_gun[*].cta` 5).

**Kanal etiketi yüzey dağılımı (daraltma kararının faturası):** aday içerikte sağ çıkan kanal
bayrağını taşıyan **7** birimin **6**'sı filtreli yüzeyde (CTA), **1**'i değil
(`gorsel_kodlar` → `[kanal-bağımlı: fiziksel_magaza]`).

## Üreten komut — dürüst etiket

Sayılar **commit'li bir test değil**, tek kullanımlık problarla alındı; probların kendisi
korunmadı (scratchpad). Yeniden üretmek için gereken şey şudur ve bağlayıcı olan budur:

1. Motorun gerçek girdisini kur — `sector_pipeline_cli` içindeki `_kosu_satiri` ·
   `_aktif_paket` · `_klasor_girdileri` · `_takvim` çağrılarıyla ve DB'deki `synthesis`
   artefaktından `SynthesisResult` ile, `_kos_motor`'un yaptığı sırayla. **`record_result`
   ÇAĞRILMAZ** (ölçüm salt-okunur).
2. `engine.decide(girdiler, PolicyConfig())` → `policy_report.bulgular` sayılır.
3. Üç yüzey: `engine._bayraklar` sırayla (a) satırın `kanit`+`gerekce` birleşimine,
   (b) `engine._denetci_satirlari(girdiler)[<atıf>].bayraklar`'a, (c) aday içerik biriminin
   değerine uygulanır; `SAG_CIKAN_BAYRAK` çıkarılır.
4. Yazım kapısı kapsamı: aday içeriğin her yaprak metnine tek tek bayrak eklenip
   `sector_content_schema.structural_errors` çağrılır.

**Prob kirlenmesi ölçüldü ve üç kez düzeltildi** (bu oturum): (a) `final_candidate` blocked
sonuçta boştur → nihai içerik `engine._nihai_icerik`ten okunmalı, (b) taban içerik şema-geçersiz
olursa her mutasyon alakasız sebeple reddedilir → taban gerçek aday olmalı, (c) prob motorun
kendi yüklemini kopyalamamalı, çağırmalı. Prob yazan sonraki oturum: **önce taban varyantının
canlı sonucu birebir ürettiğini doğrula.**
