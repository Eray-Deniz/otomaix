---
task: sektor-bilgi-paketi-plan2
written: 2026-09-20
---

# Resume From

**Kusur 1 ve Kusur 2 KAPANDI. SIRADAKİ İŞ: Kusur 3 — bayrak kilidi. İŞ CLAUDE'DA.**

**Eray kararı (2026-09-19, hâlâ geçerli): tören YOK.** Spec seansı açılmaz, plan yazılmaz;
düzeltme doğrudan başlar. Review gerekirse düzeltme SIRASINDA çağrılır. Kusur 3 hem sözleşmeye
hem motorun kapı anlamına dokunduğu için review çağırmanın en makul yeri orasıdır.

Okunacak yer: **`TASK.md` → `# Open Problems`** ilk kalemi (3. ve 4. maddeler + ölü-koşu kalemi
+ "yeni pilot koşusu" kalemi). Ölçüm dosyası `K134-MOTOR-KARSILASTIRMA.md` 2026-09-19'un
fotoğrafıdır; red etiketleri o günkü adlarıyla durur (`iddia-arastirmada-yok` artık ikiye ayrıldı).

**Kusur 3, tek paragraf:** motorda iki bayrak kontrolü var ve aynı kalem için ikisi birden
kaçınılmaz. `bayrak_tuketimi` sentezin kendi `kanit`+`gerekce` DÜZ YAZISINI tarıyor;
`yeni_oge_cogunlugu` ise denetçi satırının TİPLİ `bayraklar` sütununu okuyor ve sentezin o sütuna
erişimi yok. Bayrağı gerekçede açıklarsan birinci kapı, açıklamazsan ikinci kapı açık soru
üretiyor; satırı hiç anmazsan `referans-yok` ile red düşüyor. Açık soru BLOKLUYOR — yani
denetçinin bayrakladığı bir kalemi içeren paket bugün `activation_eligible` OLAMAZ.
**Yön:** tüketimi düz yazıdan değil YAPISAL bir alandan oku, iki kapıyı tek kaynağa bağla.

**Kusur 3'e girmeden önce iki ders (ikisi de bu oturumda ölçümle çıktı):**
- **Mekanizmayı aç, kaydın teşhisine güvenme.** Kusur 1'de kök teşhis ölçünce DEĞİŞTİ: sözleşmenin
  kuralı zaten doğruydu, eksik olan veriydi. Kusur 2'de kusur kayıttakinden GENİŞ çıktı (boş kabuk
  değil, tek yuva bile yetiyordu) ama kapsam DARALDI (üç şekil hatasının yalnız biri motor kusuru).
- **Sınıfı ölç, varyantı yamama.** Kusur 3'ün sınıfı ("serbest düz yazıdan negatif kanıtlama") bu
  projede daha önce yakınsamadığı ölçülmüş bir desendir. Regex'le kapatmaya çalışma.

# Verification

**Bu oturumda ÜRETİM KODU DEĞİŞTİ.** Dört commit bu dalda, bir commit dış sözleşme deposunda.

| Ne | Taze çıktı |
|---|---|
| Tam takım (kusur 1 sonrası) | **4613 passed / 0 failed**, 337,96 s |
| Tam takım (etiket ayrımı sonrası) | **4614 passed / 0 failed**, 335,75 s |
| Tam takım (kusur 2 sonrası, SON) | **4618 passed / 0 failed**, 334,08 s |
| Motor sürümü | `2.15.0` → **`2.17.0`** (iki ayrı uygulama-kuralı değişikliği) |
| Sözleşme | 2.5 → **2.6**, dış depo `d907e05`; pin tazelendi (üç dosyanın hash'i + HEAD) |
| Başlangıç taban | 4607 — **önceki oturumun kaydından, bu oturumda taze ölçülmedi**; eklenen test sayısı 11, toplam tutuyor |

**Mutasyonla ölçülen kapılar (hepsi yedekten geri alındı, bayt-eşit doğrulandı):**
- EK-M istemden çıkarıldı → 3 test kırmızı.
- Sözleşmeden EK-M girdi maddesi silindi → kırmızı. EK-L maddesi silindi → kırmızı.
- Atomik dönem kuralı motordan kaldırıldı → 2 test kırmızı, pozitif kontrol YEŞİL kaldı
  (kural aşırı geniş değil).

**KENDİ TESTİM YANLIŞ ÇIKTI ve mutasyon yakaladı.** Sözleşme–kod bağını ölçen ilk yazım,
EK-M maddesi TAMAMEN silindiğinde YEŞİL kalıyordu: komşu bir cümle de adı anıyordu. Test artık
liste MADDESİNİ ölçüyor. Ders: kapıyı yazdıktan sonra mutasyonla sına, yoksa tespit edemediği
bir garantiyi onaylayan bir test kalır.

**PROB İKİ KEZ KİRLENDİ, ikisi de düzeltildi.** (1) İlk prob motorun bağ kuralını KOPYALAMIŞTI ve
`ozel_gun` satırlarını yanlış "bağsız" sayıyordu → motorun kendi fonksiyonu çağrıldı. (2) İkinci
prob sentezin HAM çıktısını okuyordu; motor DB'ye yazılan İŞLENMİŞ karar günlüğünü okuyor →
ölçüm motorun gerçek girdisine taşındı. Sonraki oturum: probu yazınca önce taban varyantının
canlı sonucu birebir ürettiğini doğrula.

**DENENMEYEN / DOĞRULANMAYAN — yeşil sayılmaz:**
- **Modelin EK-M'yi gerçekten doğru kullanacağı ÖLÇÜLMEDİ.** Yapısal körlük kalktı; 8 vakanın
  8'inde dizin tahmini yalanlıyor ve doğru atıf zaten mevcut. Davranış iddiası GERÇEK bir sentez
  turu ister. Evi: kusur 3 kapandıktan sonraki yeni koşu (ayrı tur harcanmaz).
- **`yazim` · `katman1/2` · `onay` · `aktive-et` ayakları HÂLÂ hiç koşmadı.**
- **Sürüm kapısının kör noktası, dürüst etiketle kayıtlı:** `test_engine_version_is_pinned_to_the_
  RULE_SURFACE` ADAY KURMA kuralını ölçmez (parmak izi sebep kümesi · kural kimlikleri · kontrol
  adları · not sınıfları). Kusur 2'nin damga artışı bu yüzden ELLE yapıldı. Sınır damganın yanına
  yazıldı; regex'le kapatılmaya ÇALIŞILMADI.
- `ozel_gun` ve `takvim_temalari` alanlarının çalışma anında içerik üretimini nasıl beslediği
  hâlâ ölçülmedi (önceki oturumlardan devrediyor).
- Bu oturumda **DB'ye hiçbir şey yazılmadı**; koşu satırlarına dokunulmadı.

# Risks

- **Kusur 3 kapanmadan hiçbir koşu aktivasyona ulaşamaz** — denetçiler rutin olarak bayrak
  koyuyor (son koşuda 5 birim, 8 bulgu).
- **Ölü koşu kusuru DURUYOR:** düşen bir adım koşuyu sessizce öldürebilir ve sonraki adımlar bunu
  fark etmeden çalışmaya devam eder. Geri açma yolu yok.
- **Yeni koşu pahalı ve körlük tabanını geri getirmez:** `denetim` 956 sn + `sentez` 941 sn + para;
  K-134 kalibrasyonu bir kez alınabilirdi.
- **SPK kararı bilinçli risk kabulüdür** (önceki oturumlardan): paket doğrulanmamış bir hukuki
  iddia taşıyacak, gerekçe `K134-KOR-YARGI.md`'de.
- **Operatör eklemeleri** (yerel görsel kodlar · Ramazan/Kurban · yılbaşı · 23 Nisan/29 Ekim)
  mekanik kaynak bağı OLMAYAN kalemlerdir ve paketin "her kalem bir kaynağa bağlıdır" garantisini
  zayıflatırlar.
- **Sentez klasörü doluysa tur koşmaz** (`mkdir` `exist_ok` kullanmıyor). Düşen denemeler
  `DUSMUS-<tarih>-<sebep>-<koşu>` adıyla duruyor; silme YOK.

# Notes For Claude

- **Eray ham kanıt istiyor, özet değil** (hâlâ geçerli).
- **Model turundan ÖNCE offline replay yap** (hâlâ geçerli — bu oturumda EK-M'nin gerçek gövdesi
  böyle görüldü, 1551 bayt, tur harcanmadı).
- **CEVAP BEKLEYEN SORU — Eray'a soruldu, yanıt gelmedi.** Araştırma deposunun
  (`otomaix-sosyal-medya-arastirmasi`) çalışma ağacında **42 dosya silinmiş ama commit edilmemiş**
  duruyor (SWEEP-*, TASLAK-*, `kuyumculuk.md`). Bu oturumdan ÖNCE de vardı; dokunulmadı, sözleşme
  commit'i yalnız kendi dosyasıyla atıldı. Pin'i etkilemiyor (pin üç dosyanın hash'i + HEAD).
  **Koşul:** yanıt gelmeden bu dosyalara dokunulmaz; o depoda commit atılacaksa yine yalnız
  hedef dosya adlandırılarak atılır.
- **Kendi önerine İlke 7'yi uygula:** kusur 3 için "şunu da düzeltelim" demeden önce her birinin
  tarihli evi var mı, over-bundle mı diye bak.

# Notes For Codex

Codex bu oturumda **koşmadı**. Bu dalda `/review-claude-codex` ve
`/security-review-claude-codex` **hâlâ koşmadı** — zincirin yeri Task 19 sonrasıdır.

**Review için en makul yer kusur 3'ün içidir:** sözleşmeye ve motorun kapı anlamına dokunuyor.
Çalışma ağacı review'dan önce TEMİZ olmalı; kirli ağaçta review koşturma.
