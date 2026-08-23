> ⚠️ **SALT-OKUNUR KOPYA (snapshot) — DÜZENLENMEZ.** Spec yazımı için Otomaix'e alınan kanonik girdi kopyasıdır.
> Kanonik kaynak: `/root/otomaix-sosyal-medya-arastirmasi/sektor-bilgi-paketi-spec-input.md` — commit `b356033` (2026-08-23), 3145 satır.
> Kaynak sha256: `efe217073b67bfc753a438e7938bc62dd8fb11446b53d91e9ffafb2c47b50b4d`
> Doğrulama: `tail -n +7 <bu dosya> | sha256sum` kaynak sha'sını verir — ilk 6 satır (bu blok + boş satır) hariç bayt-özdeş kopyadır.
> Kaynak depoda yeni değişiklik koşulursa bu kopya yeniden eşitlenir; spec kalıcı atıfları bu kopyanın satırlarına değil karar ID'lerine (K-xx) yapar. Bu sürüm, 2026-08-23 statü notu eklendikten sonra alınmıştır: 51 teslim-sonrası kapanış (45 karar turu + K-57 · K-70 · K-83 · K-143 bağlı + K-20 · K-21) belge başındaki notta listelidir; gövde geriye dönük GÜNCELLENMEMİŞTİR — karar statüsünde çelişki hâlinde spec (`docs/specs/2026-08-21-sektor-bilgi-paketi.md`) esastır.

# [Proje / Özellik Adı]

> ⚠️ **STATÜ NOTU — 2026-08-23 (teslim sonrası kapanışlar; bu belge geriye dönük GÜNCELLENMEDİ).**
> Bu belge sentez arşividir. Teslimden sonra, Otomaix spec seansında şu kararlar Eray'la tek tek **KAPANDI**:
> 45 "spec öncesi kullanıcı kararı" turu — K-10 · K-16 · K-19 · K-26 · K-29 · K-31 · K-38 · K-39 · K-40 · K-43 · K-44 · K-45 · K-54 · K-56 · K-69 · K-71 · K-72 · K-73 · K-77 · K-79 · K-80 · K-81 · K-82 · K-105 · K-118 · K-119 · K-120 · K-121 · K-122 · K-123 · K-124 · K-126 · K-127 · K-129 · K-135 · K-136 · K-137 · K-138 · K-139 · K-140 · K-141 · K-142 · K-144 · K-149 · K-150 —
> bağlı kapanışlar: K-57 · K-70 · K-83 · K-143; ayrıca **K-20** (kaynak-kanıtlı) ve **K-21** (C — ölçek gerekçesi 22'ye dayandırılmaz).
> **Kanonik kayıt:** `otomaix` deposu — `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (spec-approved, K-ID kapanış satırlarıyla) + `docs/active/sektor-bilgi-paketi/TASK.md` Decisions Log. Kapanış listesi: `docs/active/sektor-bilgi-paketi/KARAR-KAPANIS-LISTESI.md`.
> Bu belgedeki Bölüm 17 satırları ve gövdedeki `[AÇIK]` / "açık karardır" ifadeleri **yukarıdaki kararlar için BAYATTIR; çelişkide spec esastır.** Belgenin gövdesine geriye dönük sweep bilinçli olarak yapılmamıştır (2026-08-23 kapsam kararı, Eray).

## Spec öncesi girdi dosyası

<!--
KULLANIM

Bu dosya bir implementation spec değildir. Spec yazılmadan önce ürün,
işleyiş, veri, entegrasyon ve doğrulama ihtiyaçlarını tek yerde toplamak için
kullanılır.

1. Dosyanın bir kopyasını oluştur ve köşeli parantezli alanları doldur.
2. Uygulanmayan başlıklara "Uygulanmıyor — [gerekçe]" yaz; sessizce silme.
3. Bilinmeyen konuları tahmin etme. "Açık karar" olarak Bölüm 17'ye taşı.
4. Mevcut sistemi ilgilendiren iddialara dosya, tablo, servis veya doküman
   referansı ekle.
5. Ürün/kapsam kararları ile teknik çözüm önerilerini birbirinden ayır.
6. Bu girdi üzerinde mutabakat sağlandıktan sonra ayrı bir spec hazırlanır.

Doluluk işaretleri (isteğe bağlı):
- [ZORUNLU] Spec öncesinde yanıtlanmalı.
- [GEREKİRSE] Yalnız ilgili projelerde doldurulmalı.
- [AÇIK] Henüz kararlaştırılmadı; Bölüm 17'de sahibi bulunmalı.
-->

```text
Belge amacı : Spec hazırlanması için gerekli girdileri toplamak
Belge türü  : Spec input / keşif ve karar girdisi
Proje       : [proje, ürün veya özellik adı]
Sahip       : [ürün sahibi / teknik sorumlu]
Tarih       : [YYYY-MM-DD]
Durum       : [taslak | incelemede | spec'e hazır]
İlgili alan : [ürünler, servisler, ekipler]
```

> Kısa bağlam: [Bu çalışmanın neden şimdi yapıldığını 2–4 cümleyle anlat.]

---

## 1. Yönetici özeti

[ZORUNLU]

- **Ne yapılacak?** Alt sektör düzeyinde, araştırma ve **çift kör hakem denetiminden** geçmiş, **sürümlü** sektör bilgi paketleri kurulacak; bu paketler üretim prompt'larına **koşullu** enjekte edilecek. Sistem mevcut davranışın **yerine geçmez, yanına eklenir**: iki yeni tablo (ham araştırma artefaktları + paketler), mevcut sektör taksonomisi içinde alt sektör hiyerarşisi, marka kaydında bir alt sektör bağı ve genişletilen enjeksiyon yüzeyleri — caption, görsel, kısa video ve fikir önerme; legacy kısa video yolunun akıbeti **K-06**'da açıktır.
- **Kim için, hangi problemi çözecek?** İki rol için. **Otomaix müşterisi:** postun kendi sektörüne ait hissettirmemesi. **Otomaix yöneticisi / ürün sahibi:** yeniden kullanılabilir bir sektörel bilgi katmanı bulunmadığından, özel ayrışma gerektiğinde manuel prompt müdahalesine ihtiyaç doğması (Bölüm 2.1); yerine sürümlü, izlenebilir ve evrilen bir bilgi katmanı. Bugün marka tek bir kök sektör kovasına atanıyor (tabloda 12 kök satır `[AKT·KAYNAK · 2026-07-11]`); kuyumculuk gibi bir alt sektör bu kovada eriyebiliyor ve görsel/video tarafına sektör tek satır olarak gidiyor (Bölüm 2.1).
- **Önerilen çalışma biçimi:** Turu **Otomaix yöneticisi** koşar; **Otomaix müşterisi bu sürecin katılımcısı değildir** — yalnız kendi markasının alt sektörünü teyit eder (Bölüm 9, 15). Yönetici bir alt sektör için üç bağımsız araştırma çıktısını yükler → iki **kör ve bağımsız** hakem çıktıları iddia düzeyinde denetler → sentez, denetimleri **yürürlükteki paket varsa** onunla karşılaştırıp sürümlü bir `draft` üretir. ⚠️ **İlk pakette aktif paket yoktur**; `koru` / `guncelle` / `cikar` uygulanmaz, bütün kararlar `ekle` evrenindedir (Bölüm 7.5).

  ⚠️ **Bundan sonrası tek bir akış değildir — K-22'ye bağlı iki model olarak yazılmıştır ve bu belge ikisini de taşır.** ✅ **K-22 KAPANDI — A** (2026-08-21, kullanıcı kararı — Ek B): politika motoru **Faz 1'e girer**; yürürlükteki model **motorlu modeldir**, motorsuz anlatım sentez kaydı olarak korunur (Bölüm 5.2, 7.7):
  - **Motorlu model (yürürlükte — K-22=A):** `draft` içeriğini **politika motoru** üretir (sentez çıktısı motorun girdisidir); yönetici koşu sonucunu, değişim oranlarını ve özet diff'i görür.
  - **Motorsuz model (K-22 kapanışıyla yürürlük dışı):** aday paketi **sentez** üretir ve `draft` doğrudan sentez çıktısından yazılır; motor koşu raporu üretilmez, yönetici **sentezin özetini, karar günlüğünü, açık soruları ve kapı sonuçlarını** görür.

  **İki modelde de ortak:** `content` doğrulayıcısı **veri tabanına yazımdan önce** çalışır ve reddederse yazım olmaz; kayda **yalnız `draft`** yazılır; aktivasyon **yalnız yöneticinin onayıyla** gerçekleşir. ⚠️ Motorun **fazı** (**K-22**) ile **işlevsel kapsamı ve mekaniği** (Bölüm 7.7; **K-23 · K-24 · K-25 · K-28**) ayrı karar kümeleridir ve karıştırılmaz.
- **En önemli kapsam, risk veya bağımlılık:**
  - *Sistemin iki taşıyıcı güvencesi — ikisi de ortak hükümdür.* **(a)** Paket yoluna girmeyen üretimlerde **modele gönderilen mevcut prompt parçaları byte-exact değişmez**; kapsanan yüzeyler caption, görsel, kısa video, fikir önerme ve legacy yollardır (Bölüm 3.1, 4). Ölçüldüğü yer **Katman-1** prompt kapısıdır (Bölüm 13). **(b)** *"Yeni araştırmada görülmedi"* tek başına çıkarma gerekçesi olamaz — araştırma araçlarının dönemsel ve tesadüfi kapsam farkı paket hafızasını kendiliğinden silemez (Bölüm 7.3).
  - *Kapsam:* Faz 1'de desteklenecek alt sektör sayısı **açık karardır**; ≤5 tavanı **ölçülmemiş bir tahmindir** (**K-13**) ve hedef sektör sayısı **K-21**'e bağlıdır `[ÖLÇÜLMEMİŞ VARSAYIM]`. Pilot alanı kuyumculuktur (Bölüm 16).
  - *Risk — regresyon:* Sektör tablosuna alt sektör satırı eklemek, çözücünün tam eşleşmesi nedeniyle mevcut markaların kök sektör atamasını bozabilir (**R-01**, Bölüm 13.3).
  - *Risk — enjeksiyon haritasının eksik kapsanması:* Kök sektör rehberinin yerine-geçme kuralı **üç tüketiciye birden** uygulanmalıdır; kapsanmazsa ürün davranışı kendi içinde tutarsızlaşır (Bölüm 5.1, 10.3).
  - *Bağımlılık:* Özel gün akışı canlı takvim verisinin şekline bağlıdır; bugünkü veri ile paket anahtar sözleşmesi arasındaki eşleme **K-01b**'de açıktır.
- **Kullanıcı açısından beklenen sonuç:** Paketi ve alt sektör ataması olan bir markada üretilen postun dili, çağrı kalıbı, görsel dağarcığı ve özel gün yaklaşımı sektöre özgüleşir; paket yoluna girmeyen üretimde mevcut prompt parçaları byte-exact korunur.

**Tek cümlelik işleyiş:**

> Otomaix yöneticisi bir alt sektör için üç bağımsız araştırma çıktısını yükler → iki kör hakem denetler ve sentez, yürürlükteki paket varsa onunla karşılaştırarak alan alan sürümlü bir `draft` üretir → aday paketi **motorun fazına göre** (**K-22**) ya politika motoru ya sentezin kendisi üretir → `content` doğrulayıcısı yazımdan önce koşar ve yalnız `draft` yazılır → yönetici modelin ürettiği koşu yüzeyine bakıp yalnız aktivasyonu onaylar → `active` paket, yalnız o alt sektöre atanmış markaların üretim prompt'larına koşullu girer → sektöre ayrışmış post ve posta işlenen paket sürüm damgası.

#### Bu belgenin statüsü — implementation spec DEĞİLDİR

⚠️ **Bu dosya spec öncesi girdi belgesidir.** Yukarıda tarif edilen işleyiş **hedeflenen** modeldir; kurulmuş bir sistem veya kesinleşmiş bir sözleşme değildir. Paket bakım hattı henüz işletimde değildir (Bölüm 2.1, 16).

**Karar durumu — Bölüm 17'nin 2026-08-21 ölçümü** (dört kapanış — K-22 · K-27 · K-30 · K-05 — ve gövde sweep'i sonrası):

| Karar durumu | Sayı |
|---|---:|
| Kayıtlı karar | **162** |
| `[AÇIK]` | **153** |
| Kapanmış (**K-03 · K-04 · K-05 · K-18 · K-22 · K-27 · K-28 · K-30 · K-145**) | **9** |
| **`Spec öncesi kullanıcı kararı`** — spec yazılmadan kapanmalı | **43** |
| Yalnız belirli bir spec / faz / kapsam seçilirse gerekli | 47 |
| Spec içinde teknik olarak çözülür | 35 |
| Bu spec'i bloklamaz (2026-08-21'de kapanan dört karar bu sınıfa taşındı) | 36 |
| Blok durumu ölçülmedi | 1 |

⚠️ **Kırk üç açık karar amaç, kapsam, maliyet, operasyon yükü, politika ve risk kabulü tartar; bunlar spec yazarının çözebileceği kalemler değildir** (sınıfın dört üyesi — K-22 · K-27 · K-30 · K-05 — 2026-08-21'de kullanıcı kararıyla kapandı). Sahiplik tek elde değildir: **39'unda ürün sahibi** (kimisinde teknik sahiple paylaşımlı), **4'ünde yönetici / operatör** (**K-10 · K-16 · K-43 · K-44**). Kayıtlı kararların evi **Bölüm 17**'dir; kapanmış kararların günlüğü **Ek B**'de tamamlanacaktır; spec yazarına devir notu **Ek C**'dedir.

⚠️ **Karar evreni Bölüm 17 ile kapanmış değildir.** Gövdede henüz ID verilmemiş açık kararlar vardır ve *"karar ID'si Bölüm 17 sweep'inde verilecektir"* biçiminde işaretlidir — **26 geçiş**, on bölümde: Bölüm 2 (1) · 3 (4) · 4 (5) · 6 (3) · 8 (5) · 9 (2) · 10 (2) · 12 (2) · 14 (1) · 21 (1). ⚠️ **Bu geçişlerin kaç ayrı karara karşılık geldiği ölçülmemiştir ve 26'dan fazladır:** dört işaret çoğuldur (*"karar ID'**leri** … verilecektir"*) ve her biri birden çok kararı taşır. Sayım Bölüm 17 final sweep'inde kesinleşir.

---

## 2. Problem, hedef ve başarı tanımı

### 2.1 Problem

[ZORUNLU]

#### Birinci problem — sektörel ayrışmama (mevcut sistem olgusu)

- **Bugünkü durum:** Marka bir kök sektör kovasına atanıyor (`brands.sector_id` → `social.sectors`) `[AKT·2H · 2026-07-11]`; tabloda 12 kök satır var `[AKT·KAYNAK · 2026-07-11]`. Üretimde Tier 2 bağlamına bu kovaya ait `SECTOR_GUIDANCE` metni giriyor `[AKT·2H · 2026-07-11]`. Görsel/video director'a sektör **tek satır** olarak gidiyor — olgunun kendisi `[AKT·2H · 2026-07-11]`, satır konumu (`short_video.py:128-129`, `Industry: {sector}`) `[AKT·KAYNAK · 2026-07-11]`.
- **Sorun yaşayan roller:** (a) **Otomaix müşterisi** — postu kendi sektörüne ait hissetmiyor; (b) **operatör / ürün sahibi** — yeniden kullanılabilir bir sektörel bilgi katmanı bulunmadığından, özel ayrışma gerektiğinde manuel prompt müdahalesine ihtiyaç doğuyor.
- **Sıklık ve etki:** Sistemik — mevcut genel sektör yolunu kullanan markaların üretimleri bu çözünürlük ve derinlik sınırından etkileniyor. **Ölçülmedi:** ayrışma eksikliğinin oranı veya müşteri etkisi sayısal olarak ölçülmemiştir; kanıt gözleme ve 2026-07-11 kök-neden taramasına dayanır.
- **Kök nedenler:**
  1. **Çözünürlük düşüklüğü** — Kuyumculuk ayrı bir alt-sektör karşılığı bulunmadığı için geniş kök kovada eriyebiliyor veya `genel` davranışa düşebiliyor; ayakkabıcılık geniş `e-ticaret-perakende` kovasında. İki farklı iş aynı rehberi alıyor.
  2. **Derinlik yetersizliği** — `SECTOR_GUIDANCE` caption yönelimli; görsel kod, sektörel CTA, **video hareket ve sahne dili** ve özel gün kalıbı içermiyor.
  3. **Görsel yüzeye taşınmama** — sektör bilgisi görsel/video prompt'una tek satır olarak gidiyor; görsel dil sektörden bağımsız kalıyor.
- **Hiçbir şey yapılmazsa:** Sektör sayısı arttıkça ayrışma sorunu ölçekleniyor; sektörel bilgi kurumsal hafızaya dönüşmüyor; her yeni müşteri segmenti manuel prompt müdahalesi gerektiriyor (operasyonel borç).

#### İkinci problem — hedef işletim modelindeki sürdürülebilir bakım riski `[SEA-2026-08-11]`

> Bu bir mevcut sistem olgusu **değildir.** Paket bakım hattı henüz işletimde değildir; aşağıdaki risk, **hedef işletim modelinin** kurulma biçimine ilişkindir.

- **Kaynak belgelerdeki ilk işletim tasarımı:** Paket güncellemesi her kalıp için ayrı bir karar (`koru` / `guncelle` / `cikar` / `ekle` / `kirp`) gerektiriyor; bu kararların incelenmesi operatöre bırakılmıştı.
- **Riskin muhatabı rol:** **Otomaix yöneticisi** — turu koşacak, araştırma raporlarını yükleyecek ve paketi güncelleyecek Otomaix personeli. **Otomaix müşterilerinin bu süreçle ilgisi yoktur** (Bölüm 9, 15).
- **Riskin büyüklüğü `[ÖLÇÜLMEMİŞ VARSAYIM]`:** İnceleme yükü sektör sayısı × alan sayısı × kalıp sayısı × tur sıklığı ile artar. "İnsan eliyle aylar sürer" iddiası **ölçülmemiştir**; pilotta yöneticinin tur başına gerçek süresi ölçülecektir (Bölüm 13.6). Bu tahmin hiçbir katmanda eşik, kabul kriteri veya ölçüm kapısı yapılmaz.
- ⚠️ **Sayısal / kapsamsal belirsizlik `[ÖLÇÜLMEMİŞ VARSAYIM]`:** Hedef sektör sayısı olarak **22** anılıyor; aynı kaynaklarda **12 kök sektör** ve **Faz 1 için ≤5 aktif paket** tavanı yazılı. Bu üç rakamın **neyi saydığı ve hangi zaman ufkuna ait olduğu tanımlı değildir** — 22 alt-sektörü, 12 kök sektörü, ≤5 ise Faz 1'de eşzamanlı işletilecek paketi sayıyor olabilir; bu okumada üçü **çelişmez**. **Uyuşmazlık kanıtlanmış değildir**; belirsiz olan referans ve ufuktur → **K-21 açık kalır.** Ölçek gerekçesi bu sayıya dayandığı için, K-21 kapanmadan gerekçe ölçülemez.
- **Risk gerçekleşirse beklenen etki `[ÖLÇÜLMEMİŞ]`:** İnceleme yükü öngörülen ölçeğe çıkarsa turların gecikmesi, paketlerin bayatlaması ve mevzuat değişikliklerinin geç yansıması **olasıdır**. Bu bir kesin sonuç değil, **ölçülmemiş bir ölçek riskidir**; büyüklüğü K-21 ve tur süresi ölçümüne bağlıdır.
- **Ele alınma yönü:** Kalıp-başına karar kontrolünün bir **politika motoruna** devredilmesi, insan onayının yalnız aktivasyonda kalması (Bölüm 4.5, 7.7, 15). İki ayrı karar kümesi vardır ve karıştırılmamalıdır:
  - **Motorun fazı** → ✅ **K-22 KAPANDI — A** (2026-08-21, Ek B): motor **Faz 1'e girer** (pilotla birlikte).
  - **Motorun işlevsel kapsamı ve mekaniği** (karar kapsamı sözleşmesi, kanıt/mutabakat kapıları, eşikler, kararsızlık davranışı, izlenebilirlik, yetki sınırı) → **Bölüm 7.7** ve ilgili Bölüm 17 kararları (**K-23**, **K-24**, **K-25**, **K-28** ve Bölüm 17 sweep'inde numaralanacak ek maddeler).

### 2.2 Hedef

[ZORUNLU]

- **Ana hedef:** Aynı ürün sınıfı için paketli/paketsiz üretim yan yana konduğunda **sektörel ayrışma gözlenebilir olmalı**; paketsiz markada **modele gönderilen mevcut prompt parçaları byte-exact değişmemeli**.
- **Kullanıcı değeri:** Sektörüne ait hissettiren; **mevzuat hassasiyetlerini dikkate almayı ve özel günlerde kültürel uygunluğu hedefleyen** içerik.
- **İş değeri:** Sektörel bilgi sürümlü bir varlığa dönüşür; yeni sektör eklemek prompt cerrahisi değil veri işi olur; kalite regresyonları paket sürümüne izlenebilir (sürüm ilişkisinin fiziksel temsili **K-07**'de açık).
- **Teknik hedef:** Mevcut Tier 1/2/3 katman yapısını koruyarak, gerekli enjeksiyon yüzeylerini **koşullu biçimde genişleten** ve **geri alınabilir** bir bilgi katmanı eklemek. **Cache anahtarı ve aktivasyon sonrası geçersiz kılma davranışı açık karardır**; Bölüm 10.5'te ele alınacak, karar ID'si Bölüm 17 sweep'inde verilecektir.

**Hedeflenen paketin nitelikleri —** her desteklenen alt sektör için:

Türkiye pazarına uygun · kaynakları izlenebilir · iki bağımsız denetimden geçmiş · sürümlü ve geri alınabilir · caption, fikir, görsel ve video üretiminde kullanılabilen · özel günlerde koşullu derinleşebilen.

> **Kapsam bağımlılığı:** **Faz 1'de desteklenecek alt-sektör sayısı açık karardır** — Faz 1 tavanı ≤5 önerisi **ölçülmemiş bir tahmindir** (**K-13**); hedef sektör sayısı **K-21**'e bağlıdır. Kapsam Bölüm 3.1 / 3.4 ve 16.2 / 16.3'te tanımlanır.

### 2.3 Başarı ölçütleri ve kabul kapıları

[ZORUNLU]

Başarı **iki ayrı katmanda** ölçülür; katmanlar birbirinin yerine geçmez:

- **Katman-1 — deterministik prompt kapısı.** Modele giden prompt parçaları yakalanır ve **değişiklik öncesinde dondurulmuş prompt fixture'ı** ile **byte-exact** karşılaştırılır. Karşılaştırılan şey **LLM çıktısı değil, modele gönderilen prompt metnidir.** Zorunlu ve otomatiktir.
- **Katman-2 — çıktı-düzeyi kör örneklem.** Aynı ürün ve istekle üretilmiş paketli/paketsiz çıktılar kör olarak değerlendirilir. **Operatör onayının girdisidir, otomatik kapı değildir.**

Gerekçe: LLM çıktısı stokastiktir (`temperature=1.0`, seed yok `[AKT·KAYNAK · 2026-07-11]`) → byte-düzeyi değişmezlik üretilen postta değil, **modele giden prompt'ta** aranır.

*(Kaynak belgeler bu iki katmanlı kapıyı kendi kısaltmasıyla anar; bu belgede "Katman-1 / Katman-2" kullanılır — kaynak adı Ek A terimler sözlüğündedir.)*

| Ölçüt | Başlangıç değeri | Hedef | Ölçüm yöntemi | Kabul eşiği |
|---|---|---|---|---|
| Paketsiz markada prompt değişmezliği | değişiklik öncesi dondurulmuş **prompt fixture'ı** | fixture ile %100 aynı | **Katman-1**: Tier 1/2/3 + video still bağlamı + motion havuzu prompt metinlerinin byte-exact karşılaştırması | **Tek bayt fark = RED** |
| Paketli markada Tier 2 içeriği | paket yok | paket bloğu var, `SECTOR_GUIDANCE` yok | **Katman-1** prompt yakalama | İkisi birden sağlanmalı |
| Özel gün enjeksiyonu | mekanizma var, içerik yok | eşleşen günde dönem kalıpları Tier 3'te | **Katman-1** prompt yakalama + eşleşmezlik log'u | Eşleşen günde blok zorunlu — anahtar sözleşmesi **K-01b**'ye bağlı |
| **Görsel dağarcığı — prompt yapısı** | yok | `image_prompt` çıktı talimatında sektör görsel dili bloğu **bulunur** | **Katman-1** prompt yakalama | Blok var / yok — **deterministik** |
| **Görsel dağarcığı — çıktı kalitesi** | yok | dağarcık **seçilerek** yansımış (tamamı değil) | **Katman-2** kör değerlendirme | **Eşik yok — pilot kanıtından sonra belirlenecek (K-11 (b))** |
| Sektörler arası ayrışma | ayrışmıyor (gözlem) | kör değerlendirmede ayırt edilebilir | **Katman-2**, içerik tipi başına küçük örneklem | **Eşik yok — pilot kanıtından sonra belirlenecek (K-11 (b))** |
| Paket sürüm ilişkisi | yok | paketli üretim, kullanılan paket kimliği ve sürümüyle ilişkili; paketsiz üretimde geçerli paket ilişkisi yok | DB kaydı kontrolü | İlişkinin kurulmuş / kurulmamış olması — fiziksel temsil **K-07**'de açık |
| Tur maliyeti (operasyon) | ölçülmedi | ölçülecek | ilk turda süre kaydı | **Kabul eşiği değil — ölçüm kalemi.** Paket tavanı kararı Bölüm 3.4 / 16.3 / **K-13** |

> **Başlangıç değeri sütununun kanıt statüsü:** Bu sütundaki mevcut-durum iddiaları
> **bu sentezde ölçülmemiştir.**
> - Özel gün mekanizmasının **var** olması ve sektör görsel dağarcığının **bulunmaması**
>   → `[AKT·2H · 2026-07-11]` — 2026-07-11 taramasından aktarılmış, yeniden ölçülmedi.
> - "paket yok" ve "paket sürüm ilişkisi yok" → sistem henüz kurulmadığı için
>   **kendinden apaçık**; doğrulama iddiası değildir.
> - "ayrışmıyor" → kaynak belgelerin kendi ifadesiyle **ölçüm değil gözlemdir**.
> - "ölçülmedi" satırlarının **taban değeri yoktur**; ilk turda ölçülecektir.

**Deterministik kabul koşulları:**

1. Ham artefakt tablosunda `UPDATE` / `DELETE` hata fırlatır.
2. Sektör başına ikinci `active` paket kısmi benzersiz indeksle reddedilir.
3. Koşu artefaktları `run_id` altında sorgulanabilir.
4. Paketsiz markada tüm prompt yüzeylerinde fixture'a karşı byte-exact eşitlik.

**Çıktı / kalite kabul koşulu:** Katman-2 kör örneklemi **operatör onayının girdisidir**; otomatik geçme/kalma kapısı değildir.

**Başarısız sayılacağı durumlar (kesin):**

- Paketsiz markanın prompt'unda fixture'a göre tek bayt fark (regresyon).
- Paketli markada paket bloğu ile `SECTOR_GUIDANCE`'ın birlikte basılması.
- Alt-sektör satırı eklendikten sonra mevcut bir markanın `sector_id` değerinin değişmesi.

**Kalite sinyali (kesin başarısızlık değil):** Kör değerlendirmede sektörel ayrışmanın gözlenmemesi **aktivasyon kararında olumsuz kalite sinyalidir**; **otomatik red eşiği K-11 (b) kapanmadan tanımlanmaz.**

**Ölçülemeyen veya sonra izlenecek sonuçlar:** Paketin gerçek pazarlama etkisi (etkileşim/dönüşüm) — müşteri etkileşim verisiyle kanıt döngüsü bilinçli olarak Faz 2'dedir (Bölüm 3.2). Bu yüzden Faz 1'de paket sürüm ilişkisi zorunludur: **damga olmadan geçmiş üretimlerin belirli paket sürümleriyle güvenilir biçimde geriye dönük ilişkilendirilmesi mümkün olmaz.**

**Ölçülmemiş ve kapıya çevrilmeyecek değerler:** Faz 1 paket tavanı (≤5) · tur süresi · Katman-2 örneklem boyutu ve eşiği · hedef sektör sayısı · "insan eliyle aylar sürer" iddiası. Hiçbiri kabul kriteri, eşik veya ölçüm kapısı yapılmaz.

---

## 3. Sistem sınırı

### 3.1 Kapsam içinde

[ZORUNLU]

**Veri ve taksonomi katmanı**

- Alt sektör taksonomisi: yeni bir alt sektör tablosu kurulmaz; `social.sectors` içinde alt-sektör satırları, mevcut `parent_sector_id` kolonu kullanılarak `[AKT·2H · 2026-07-11]` (kolonun veri durumu için bkz. 3.4); kök kova invariantının koruma noktalarıyla birlikte.
- `brands.sub_sector_id` (yeni, null olabilir FK) — paket yolunun anahtarı. Kesin FK ve adlandırma migration spec'inde kararlaştırılacaktır.
- Marka → alt-sektör ataması: LLM önerir, kullanıcı teyit eder (`analyze-website` sözleşmesine alan eklenmesi + ekran bileşeni). LLM **yalnız aktif paketi olan alt sektörlerden** birini önerebilir veya boş döner; serbest metin dönüşü kabul edilmez.
- Ham araştırma, denetim ve sentez artefaktlarının saklanması: `social.sector_research_artifacts` (salt-ekleme).
- Sürümlü paketler: `social.sector_packages` — tek JSONB `content` + karar günlüğü; `draft` / `active` / `archived` yaşam döngüsü.

**Üretim hattı**

- Araştırma brief'i ve brief üzerinde biçimsel/mekanik eleme (`brief-doctor`).
- İki bağımsız hakem denetimi (çift kör).
- Alan bazlı, evrimsel paket sentezi ve `draft` üretimi.
- Kalıp-başına değişim kararlarının otomatik kontrolü — **politika motoru** `[SEA-2026-08-11]`. Girdisi sentez çıktısı, aktif paket ve çıkarılanlar listesi; çıktısı uygulanmış karar seti, özet diff ve koşu raporu.
- Sürümler arası **özet diff** üretimi — aktivasyon kararının girdisi (kalıp-kalıp liste değil, özet).
- Yönetici koşu yüzeyi: sektör seçimi → KAYNAK-1/2/3 yüklemesi → koşunun tek giriş noktasından tetiklenmesi.

**Enjeksiyon yüzeyleri**

- Caption ve fikir üretimine sektör bağlamının Tier 2 gövdesi olarak enjeksiyonu (mevcut `SECTOR_GUIDANCE` metninin yerine).
- Görsel ve kısa video bağlamına sektör görsel dilinin enjeksiyonu: caption director görsel dağarcığı ve kısa video director'ın iki modu.
- Özel gün kalıplarının Tier 3'te koşullu enjeksiyonu.

**İzlenebilirlik ve doğrulama**

- Üretilen postun, üretimde kullanılan paket sürümüne izlenebilir biçimde bağlanması — ilişkinin fiziksel temsili **K-07**'de açıktır.
- İki katmanlı doğrulama altyapısı: **Katman-1** prompt kapısı (byte-exact prompt regresyonu) ve **Katman-2** çıktı örneklemi (kör değerlendirme).

**Pilot**

- Kuyumculuk pilotu: paket üretimi ve kapı testi.

**Sınır durumu — marka kanal envanteri.** ✅ **K-05 KAPANDI — B** (2026-08-21, kullanıcı kararı — Ek B): kanal envanteri **bu işin Faz 1 kapsamında** kurulur — sentezdeki değerlendirme (*doğal ev Marka DNA'sı, tam çözüm kapsam dışı*, 3.2) bu kararla **tersine döndü**. `[kanal-bağımlı: X]` kalıplar için kullanım-talimatı düzeyindeki hafif önlem korunur; deterministik filtrenin envantere bağlanma biçimi ve **Marka DNA işiyle sınır** spec'te tanımlanır.

**Kapsamın açık kararlara bağlı kenarları — üç madde.** Politika motoru, özet diff ve yönetici koşu yüzeyi hedef kapsamın parçasıdır; üç kenarı açıktır ve bu üç karar **bu sırayla** değerlendirilir:

1. **Motorun fazı — ✅ K-22 KAPANDI — A** (2026-08-21, kullanıcı kararı — Ek B). Motor **Faz 1'e girer** (pilotla birlikte kurulur); motor kararları (**K-23 · K-24 · K-25 · K-133**) Faz 1 spec gündemindedir. Karar öncesi değerlendirme, elle inceleme yükünün ölçeğine ilişkin **ölçülmemiş** bir gerekçeye dayanıyordu (Bölüm 2.1; **K-21**, **K-13**) — kapanışla **K-21'in netleştirme koşulu tetiklenmiştir**.
2. **Kalıp kimliği sözleşmesi `[AÇIK]`.** Sürümler arası kalıp kimliğinin (kalıcı kimlik alanı, üretim yöntemi, sürümler arası koruma kuralları) nasıl kurulacağı açıktır; bir hakem kalıcı kimliği zorunlu sayar, diğeri kalıp düzeyinde kalıcı kimlik öngörmez ve sürekliliği karar günlüğü üzerinden metinsel eşleşmeyle kurar. Motor **Faz 1'de** olduğundan (✅ **K-22 KAPANDI — A**, Ek B) bu sözleşme motor spec'inin **ön koşuludur**. Karar ID'si Bölüm 17 sweep'inde verilecektir.
3. **Yönetici koşu yüzeyi — ✅ K-27 KAPANDI — A** (2026-08-21, kullanıcı kararı — Ek B). Koşu **Claude Code komut ailesi** üzerinden işletilir; yönetici paneli geliştirilmez. ⚠️ Komut ailesinin **bugünkü varlığı doğrulanmamıştır** — spec seansında taze doğrulanır; yoksa kurulum işi bu seçeneğin maliyetine eklenir (karar bununla yeniden açılmaz). Yüzey seçimi işletim prosedürünü (Bölüm 14) ve rol/yetki tasarımını (Bölüm 15) belirler.

### 3.2 Kapsam dışında

[ZORUNLU]

- **Sosyal platformlardan otomatik veri/içerik toplama (tarayıcı ajanı)** — hukuki değerlendirme gerekiyor; araştırma kuralları platform kazımayı da yasaklıyor. *Yeniden ele alma koşulu:* hukuki görüş alındığında.
- **Marka örnek postlarının otomatik toplanması** (yayınlanan içerikten geri besleme) — **evi vardır: Marka DNA karar dokümanı, Faz 2.** Hakem belgeleri bu evi taşımamış, kaynak doküman taşımaktadır; bu sentezde kaynağa karşı doğrulanmıştır. Bölüm 17'ye kapsam kararı olarak taşınmaz.
- **pgvector tabanlı örnek havuzu / embedding** — bilinçli sınır: erişim deterministik tutuluyor. *Koşul:* örnek-tabanlı few-shot ihtiyacı ölçülürse (Faz 2).
- **Araştırmanın uçtan uca tam otomatikleşmesi** — araştırma girdisinin toplanması elde kalıyor: KAYNAK-1/2/3'ü yönetici üretip yükler. *Koşul:* tur maliyeti ölçüldükten sonra. ⚠️ **Sınır netleştirmesi `[SEA-2026-08-11]`:** bu madde **girdi toplamanın** otomatikleşmesini dışarıda tutar. **Kalıp kararlarının kontrolü kapsam dışı değildir** — politika motoru olarak kapsama alınmıştır (3.1). İki otomasyon ayrı tutulur: *girdi toplama* elde, *karar kontrolü* otomatik.
- **Müşteri etkileşim verisiyle otomatik paket öğrenme / kanıt döngüsü** — Faz 2. *Koşul:* paket sürüm damgasının (**K-07**) Faz 1'de kurulmuş olması.
- **Paketlerin ürünleştirilip ayrıca satılması** — hukuki görüş eşiği.
- **Kök sektör trend sorgularının alt-sektör anahtar kelimeleriyle zenginleştirilmesi** — trend sistemi bu işte dokunulmaz kalıyor. **Evi vardır: sektör karar dokümanının "Kapsam dışı (bilinçli, Faz 2)" listesi.** Hakem belgeleri koşulu taşımamış, kaynak doküman taşımaktadır. Bölüm 17'ye kapsam kararı olarak taşınmaz.
- **Marka kanal envanterinin tam çözümü (K-05)** — ✅ **KAPANDI — B** (2026-08-21, kullanıcı kararı — Ek B): bu madde **artık kapsam dışı değildir** — kanal envanteri **bu işin Faz 1 kapsamına çekildi**. Marka DNA dokümanındaki `channels` alan adayıyla sınır spec'te yeniden çizilir; kullanım-talimatı düzeyindeki önlem korunur (3.1 sınır durumu).
- **Marka DNA alanları** (`voice_profile`, `banned_words`, `target_audience`, `example_posts`) — **ertelenmiş sektör işi değildir; ayrı ve onaylı Marka DNA sisteminin işidir.** Dördü de Marka DNA karar dokümanının G1 alan önerisinde somut alan tanımlarıyla (tip, boyut, enjeksiyon noktası) bulunur — K-05'in `channels` alanıyla aynı ev. Bu işle iki noktada kesişir: bağlam hiyerarşisi (Bölüm 4.6) ve kontrast referansı (Bölüm 12). Bölüm 17'ye kapsam kararı olarak taşınmaz.
- **Bakım borçları:** `brands.sector` TEXT kolonunun tekilleştirilmesi, LinkedIn `long` sürüklenmesi ve legacy şablonların `active` statüsü — bu işte dokunulmaz (Bölüm 16.1). **Çözülmemiş kapsam kararı:** Bölüm 16.1 bu maddeleri *kaydeder*, ele alınacakları bir hedef göstermez; koşul uydurulmamıştır, madde Bölüm 17'ye taşınır. Legacy şablon sayısı olarak anılan **22**, hedef sektör sayısı olarak anılan 22 ile **aynı şeyi saymamaktadır**; bu ayrım **K-21**'in kontrol maddesidir.

### 3.3 Etkilenen kullanıcılar ve kullanım yüzeyleri

| Kullanıcı / aktör | İhtiyaç | Etkilenen yüzey | Beklenen değişiklik |
|---|---|---|---|
| Marka sahibi (KOBİ) | Sektörüne ait içerik | Üretim akışı | Çıktı sektörelleşir; **içerik üretirken kullanıcıya yeni soru eklenmez** (sürtünme yasağı) |
| Marka sahibi | Doğru alt-sektöre atanmak | Onboarding + marka ayarları ekranı | Önceden seçili alt-sektör önerisi; değiştirilebilir veya boş bırakılabilir. Aday listesinde **yalnız aktif paketi olan alt sektörler** bulunur |
| **Koşu ve aktivasyon rolü** (Otomaix yöneticisi / operatör) `[SEA-2026-08-11]` | Turu koşmak: sektör seç, KAYNAK-1/2/3 yükle, brief'i doldur, koşuyu tetikle, **özet diff'e bakıp aktive et** | Yönetici koşu yüzeyi (✅ **K-27 KAPANDI — A**: Claude Code komut ailesi) + özet diff ekranı | Kalıp-kalıp karar **vermez**; koşu sonucuna **yalnız aktivasyon/ret ve rollback onayı** verir; politika motorunu atlayarak aktive edemez. Tur periyodu 3 **veya** 6 ay — **K-26** |
| **Kapsam ve politika karar yetkisi** | Kapsamı, tradeoff'ları, risk kabulünü ve takvim politikasını belirlemek; açık kararları kapatmak | Bölüm 17 karar listesi; brief kapsamı | Bu sorumluluk **her iki seçenekte de durur**, yalnız yeri değişir: tek-rol seçeneğinde yukarıdaki rolle aynı kişide, bölünmüş seçenekte ayrı bir **ürün sahibi** yetkisinde. ⚠️ **Bölünüp bölünmeyeceği açık karardır** — ayrım yalnız bir hakem belgesinde bulunur, diğeri tek operasyon rolü tanımlar ve açık kararların muhatabı olarak da aynı rolü gösterir; karar ID'si Bölüm 17 sweep'inde verilecektir, yetki dağılımı Bölüm 15'te kesinleşir |
| **Politika motoru** `[SEA-2026-08-11]` | Kalıp-başına değişim kararlarını otomatik kontrol edip uygulamak | Sentez çıktısı + aktif paket + çıkarılanlar listesi | Uygulanmış karar seti + özet diff + koşu raporu; `active`'e geçirme yetkisi yoktur. Kapsama girme fazı **K-22**'ye bağlıdır |
| Otomaix müşterisi (paket bakımı açısından) | **Yok — bu süreçle ilgisi bulunmaz** | — | Müşteri yalnız kendi markasının alt-sektörünü teyit eder (Bölüm 9); paket bakımını görmez, tetiklemez, onaylamaz |
| Denetçi-1 | Bağımsız iddia denetimi | Koşu akışının denetim adımı | Yeni rol; nihai paket kararı vermez |
| Denetçi-2 | Bağımsız ve kör iddia denetimi | Koşu akışının ikinci denetim adımı | Yeni rol. Ortamında web erişiminin bulunup bulunmadığı ve **koşu öncesi ön kontrol** **K-14**'te açıktır; erişim yoksa kanıt ağırlığının nasıl ayarlanacağı ise **yürürlükteki sentez görev sözleşmesinde tanımlıdır** (Bölüm 7.4). **İki denetimin paralel mi sıralı mı yürütüleceği, oturum izolasyonunun ve aynı girdi anlık görüntüsünün teknik garantisi açık karardır**; karar ID'si Bölüm 17 sweep'inde verilecektir |
| Sentez rolü | Alan-alan karar | Koşu akışının sentez adımı | Yeni rol; adayı doğrudan aktive edemez |
| Frontend: sektör listesi | Alt-sektör satırlarının kök listesine sızmaması | `GET /sectors` tüketen 3 sayfa | Endpoint'e kök-seviye filtresi eklenmesi (**henüz uygulanmadı**). Sayfa ve satır konumları (`onboarding/page.tsx:129`, `markalar/page.tsx:56`, `marka-ayarlari/page.tsx:434`) `[AKT·KAYNAK · 2026-07-11]` |
| Trend sistemi (Layer A) | Kök kovadan çalışmaya devam | Trend kök sektör sorgusu | **Değişiklik yok** — mevcut kök-seviye filtresi zaten koruyor `[AKT·2H · 2026-07-11]`; satır konumu (`layer_a.py:263`) `[AKT·KAYNAK · 2026-07-11]` |
| `sector_resolver` | Kök kova invariantını korumak | Sektör çözümleme yolu | **Zorunlu değişiklik (hedef karar, iki belgede ortak):** alt sektör satırları kök sektör olarak çözülmemeli — kök-seviye filtresi + regresyon testi. Filtre ve test **henüz yazılmamıştır**; doğrulama etiketi taşımaz. Mevcut kod konumu (`sector_resolver.py:59`) `[AKT·KAYNAK · 2026-07-11]` |

### 3.4 Varsayımlar ve kısıtlar

**Varsayımlar**

- **Varsayım:** `sectors.parent_sector_id` kolonu şemada **bulunur** `[AKT·2H · 2026-07-11]` — iki hakem belgesi de kolonu mevcut tablonun parçası sayar ve yeni bir alt sektör tablosu kurmaz. **Verinin boş olması** (12 kök satır, hepsinde NULL) yalnız bir belgede aktarılmıştır `[AKT·KAYNAK · 2026-07-11]`.
- **Varsayım:** `social` şemasında birincil anahtarlar uuid'dir; migration düzeni `shared/db/migrations/` 001-030 `[AKT·KAYNAK · 2026-07-11]`. uuid yönü iki belgede de görünür; kesin FK ve adlandırma kararları migration spec'ine bırakılmıştır.
- **Varsayım:** DB'de mevcut marka sayısı düşüktür (iki marka) `[AKT·KAYNAK · 2026-07-11]`. Bundan çıkan işletim sonucu ortaktır: markalar elle atanır, **toplu geriye dönük atama başlangıç kapsamına alınmaz**.
- **Varsayım `[ÖLÇÜLMEMİŞ VARSAYIM]`:** Paket bloğunun Tier 2'ye eklenmesinin maliyeti ~1,2–1,5K token ve üretim başına ~1 cent düzeyindedir. Aynı kaynaklarda paket için ~6.000 karakter ≈ 2.000 token'lık bir hedef tavan da yazılıdır; **iki rakam uzlaştırılmamıştır** ve ikisi de ölçüm değildir → **K-12**. Bu değerler eşik, kabul kriteri veya ölçüm kapısı yapılmaz.
- **Varsayım `[VARSAYIM]`:** Paket bloğunun Tier 2'yi önbellek minimum eşiğinin üstüne taşıyıp önbelleği açması lehte yan etki olarak öngörülür; ölçülmemiştir. **Önbellek anahtarı ve aktivasyon sonrası geçersiz kılma davranışı açık karardır** — bir hakem anahtarın paket kimliği/sürümünü içermesini ya da aktivasyonda önbelleğin geçersiz kılınmasını şart koşar, diğeri paket Tier 2 bloğunun içinde yaşadığı için ek mekanizma gerekmediğini varsayar. Bölüm 10.5'te ele alınacak; karar ID'si Bölüm 17 sweep'inde verilecektir.

> **Çürütülmüş iki varsayım** (özel gün anahtarının sistem gün adının slug hâli olduğu; video hareket dilinin `Industry` satırıyla etkilendiği) bu bölümde tekrarlanmaz: yerlerine geçen açık kararlar **K-01b** ve **K-02**'dir, geçmişleri Ek B'de tutulur.

**Kısıtlar**

- **Kısıt:** Araştırma adımı elle işletilir ve maliyetlidir (üç ayrı arayüzden derin araştırma); bu yüzden girdi/çıktı sözleşmeleri donmadan araştırma yeniden koşulmaz (**K-18**). Maliyetin büyüklüğü `[ÖLÇÜLMEMİŞ]`.
- **Kısıt:** Görsel üretimiyle test etmek harici sağlayıcı kredisi harcar → hat doğrulaması canlı görsel üretimiyle değil, yerel/ucuz katmanla yapılır `[BU SENTEZDE DOĞRULANMADI]`.
- **Kısıt:** LLM çıktısı stokastiktir → değişmezlik üretilen postta değil, **modele gönderilen prompt metninde** aranır (Katman-1). Stokastikliğin kod tarafındaki gerekçesi (`temperature=1.0`, seed yok) `[AKT·KAYNAK · 2026-07-11]`.
- **Kısıt:** Üretim hattı görsel içinde metni yasaklar. Yasağın kanonik biçimi araştırma brief'i şablonundadır ve **kapalı bir küme değildir**: İngilizce görsel/video alanlarında (GÖREV A alan 5 ve 6, GÖREV B `gorsel_vurgu`) **yazı/metin/logo/etiket/watermark** içeren öğe önerilemez — *üzerinde yazı olan* **tabela, menü, gravür**, ayrıca **altyazı**, **marka rozeti** **vb.** dâhil. Öğeler sayılıp tüketilmez; ölçüt öğenin görselde **metin taşıyıp taşımadığıdır**. Yasak iki hakem belgesinde de vardır (biri listenin bir bölümünü, diğeri başka bir bölümünü aktarır); tam liste **kaynak şablona karşı bu sentezde doğrulanmıştır.** Üretim hattının bu yasağı fiilen uyguladığı `[BU SENTEZDE DOĞRULANMADI]`.
- **Kısıt `[ÖLÇÜLMEMİŞ VARSAYIM]`:** Faz 1'de eşzamanlı işletilecek aktif paket tavanı olarak ≤5 önerilir; gerekçesi elle işletme yüküdür ve ölçülmemiştir. İlk tur süresi ölçüldükten sonra revize edilecektir (**K-13**); hedef sektör sayısı ayrıca **K-21**'e bağlıdır. Bu değer kabul kriteri veya kapı yapılmaz.

---

## 4. Temel tasarım ilkeleri

[ZORUNLU]

Bu bölüm çözümün vazgeçilmez davranış kurallarını tanımlar; ayrıntılı teknik tasarım değildir. Anlatılan **hedef işletim modelidir** — mevcut üretim yolunun korunmasına ilişkin hükümler dışında, kurulmuş bir sistemin bugünkü davranışı değildir.

### 4.1 Geriye uyumluluk ve kademeli geçiş

**Devreye girme koşulu — tek ve ortak.** Paket yolu yalnız iki koşul birlikte sağlandığında çalışır: `brands.sub_sector_id` dolu **VE** atanan alt sektörün `active` paketi var. İkisinden biri eksikse mevcut üretim yolu kullanılır.

**Mevcut davranışın korunması.** Paket yoluna girmeyen üretimlerde **modele gönderilen mevcut prompt parçaları byte-exact değişmez.** Kapsanan yüzeyler: caption, görsel, kısa video, fikir önerme ve legacy yollar. Bu, bölümler boyunca tekrarlanan kademeli geçiş ilkesidir; ölçüldüğü yer **Katman-1** prompt kapısıdır (Bölüm 13). *Terim notu:* bir hakem belgesi bunu "bit-düzeyinde aynı çalışır" diye yazar; sistem davranışı için bit değişmezliği ileri sürülemeyeceğinden ifade yukarıdaki biçimde kullanılmıştır. Diğer hakem aynı hükmü zaten "mevcut `SECTOR_GUIDANCE` yolu byte-exact korunur" biçiminde yazar.

**Ayrı bir feature flag öngörülmez.** Paketin varlığı doğal bayraktır; geçiş veri tabanlıdır. Pilot kuyumculuktur, genişleme paket sayısı artırılarak yapılır. Bu tespit yalnız bir hakem belgesindedir; diğeri aynı iki koşullu kapıyı kurar ama bayrak sorusunu ele almaz — reddetmez.

**Paralel çalışma yasağı — ortak hüküm.** Aktif paket varken kök `SECTOR_GUIDANCE` bloğu paketle **yan yana basılmaz**; paket onun yerine geçer. Gerekçe ortaktır: iki blok çelişen talimat üretebilir (ör. kök rehber aciliyet dilini serbest bırakırken alt sektör paketi onu kısıtlayabilir). Aynı yerine-geçme kuralı fikir önerme yoluna da uygulanır; aksi hâlde fikir önerisi genel rehberle, gerçek üretim paketle çalışır ve ürün davranışı ayrışır.

### 4.2 Kaynak veri ile türetilmiş çıktının ayrımı

[GEREKİRSE]

**Kritik ayrım: ham katman kanıt, paket üründür.** Ham artefaktlar prompt'a doğrudan girmez; prompt'a yalnız boyutlandırılmış aktif paket girer.

| Katman | İşlev | Doğruluk kaynağı | Yaşam döngüsü |
|---|---|---|---|
| Ham artefakt (`sector_research_artifacts`) | Araştırma, denetim ve sentezin kanıt ve izlenebilirlik tabanı | Araştırma araçları ve hakem hattı; içerik olduğu gibi saklanır | **Salt-ekleme** — değiştirilmez ve silinmez |
| Sektör paketi (`sector_packages.content`) | Prompt'a enjekte edilecek damıtılmış bilgi | Sentez kararları + politika motoru kontrolü + yönetici aktivasyon onayı | **Sürümlü**; sektör başına tek `active`; `draft → active → archived` |
| Karar günlüğü (`decision_log`) | Her kalıbın niçin korunduğu, güncellendiği veya çıkarıldığı; kanıt referansı zorunlu | Sentez ve politika motoru kararları | Paketle birlikte sürümlenir (paketin parçası) |

Kırpılan veya çıkarılan içerik paketten çıkar, ham katmanda durur — bilgi kaybolmaz.

**Salt-ekleme yalnız kural değil, teknik olarak zorlanan bir karardır.** Ham artefakt tablosunda `UPDATE` ve `DELETE` veri tabanı düzeyinde reddedilir. Bu **açık karar değildir**: kaynak karar dokümanı bunu "onaylı karar — uygulama disiplinine bırakılmaz" diye kaydeder ve iki hakem belgesi de tetikleyiciyle reddi aynen taşır. Uygulama spec'ine kalan yalnız tetikleyicinin kesin biçimi ve migration sırasıdır.

### 4.3 Güncelleme ve geçmişi koruma ilkesi

[GEREKİRSE]

**Evrimsel model.** Yeni sürüm sıfırdan yazılmaz: **yeni sürüm = aktif paket + yeni araştırma + kalıp-başına açık karar.** Aktif paket, yeni araştırma ve eski çıkarma kararları birlikte değerlendirilir; her kalıp için aşağıdaki kararlardan biri ve onu destekleyen izlenebilir bir gerekçe üretilir.

| Karar | Uygulanma koşulu |
|---|---|
| `koru` | Kalıp hâlâ geçerliyse ve geçersiz olduğuna dair pozitif kanıt yoksa. Yeni araştırmada anılmaması çıkarma nedeni değildir |
| `guncelle` | Yeni araştırma kalıbın içeriğini değiştiren güvenilir kanıt getiriyorsa — özellikle mevzuat, tarih, sayı ve sektör pratiği değişikliklerinde; kuralın konusu korunur, güncel değeri ve yürürlük tarihi değişir |
| `cikar` | Kalıbın yanlış, geçersiz, riskli veya kullanılamaz olduğunu gösteren **pozitif kanıt** varsa. Kanıt satırı zorunludur (denetçi satırı `D1#<no>` / `D2#<no>`, `KAYNAK-N` veya doğrulanmış URL) |
| `ekle` | Yeni kalıp üç araştırmanın en az ikisinde bulunuyorsa (`2-3`). Tekil kaynaklı kalıp ancak güçlü kaynaklıysa ve `[yerel-değil]` / `[muhtemel-uydurma]` bayrağı taşımıyorsa gerekçeyle eklenebilir |
| `kirp` | Kalıp geçerli olmasına rağmen paket boyut bütçesine sığmıyorsa. Öğe ham katmandan silinmez; `karar='kirp'` olarak günlüğe yazılır |

**"Yeni araştırmada görülmedi" tek başına `cikar` gerekçesi olamaz** — ortak ve açıkça gerekçelendirilmiş hüküm: araştırma araçlarının dönemsel ve tesadüfi kapsam farkı paket hafızasını kendiliğinden silemez. Aynı yönde ikinci ortak hüküm: müşteri beğenisi, marka başına ton/CTA takibi ve müşteri etkileşimi bu karar matrisinin girdisi değildir; sistem sektör düzeyindeki kaynak, mutabakat, güncellik, risk ve özgüllük sinyallerini kullanır.

**`uyarla` ve `alma` bu beş kararın üyesi değildir.** Uyarlanarak alınan kalıbın nihai kararı `ekle` veya `guncelle` olur; gerekçede özgün kalıbın nasıl ve niçin uyarlandığı yazılır. `alma` bir denetçi/sentez eleme önerisidir. **Reddedilen yeni adayın kalıcı karar izinde nasıl temsil edileceği açık karardır** — bir hakem bunu açık karar olarak kaydeder, diğeri konuyu ele almaz; karar ID'si Bölüm 17 sweep'inde verilecektir.

**Sürüm, denetim izi ve geri alma.** Her paket sürümü kendi karar günlüğünü taşır ve koşu kimliği üzerinden ham artefaktlara bağlanır; eski sürümler `archived` olarak durur, silinmez — geri alma bu sayede mümkündür (Bölüm 8.3).

**Kırpma önceliği çözülmemiştir.** Kırpmanın hangi kalıpları eleyeceği doğrudan paket içeriğini belirlediği için burada görünür kalır. Bir hakem kaynak dokümanların üçlüsünü (sektöre özgülük → mutabakat gücü → yerellik) korur; diğeri bu sıralamayı **bilinçli olarak değiştirdiğini yazar** ve mevzuat/güvenlik bilgisini en üste, mevcut pakette doğrulanmış sektöre özgü kalıpları ikinci sıraya alır (churn koruması). Bu superseded bir hüküm değil, açık bir öncelik çelişkisidir. Ayrıntı Bölüm 7.6'da ele alınacak; karar ID'si Bölüm 17 sweep'inde verilecektir.

**Karar semantiğinin tanımsız kalan ölçütleri.** Bu karar sistemi kanıt ve eşiklerle sınırlandırılmıştır ama bütünüyle deterministik değildir. Dört ölçüt tanımsızdır: "güçlü kaynak" sınıfının ölçütleri · iki kalıbın **semantik olarak aynı** sayılması · `cikar` için pozitif kanıtın yeterlilik eşiği · `guncelle` ile `cikar + ekle` ayrımı. Bir hakem bunları uygulama öncesi açık karar olarak kaydeder; diğeri "güçlü kaynak" terimini tanımlamadan kullanır ve semantik eşleşme sorununu tanıyıp sonraki faza bırakır. Dördü **dört ayrı karar olarak** Bölüm 17'ye taşınır — tek bileşik madde değildir; karar ID'leri sweep'te verilecektir. Dördü kapanana kadar geçerli olan ortak davranış: sentez gerekçe yazar ve çözülemeyen uyuşmazlık güvenli tarafa düşer. Aynı yerde bir hakem üçüncü bir ayak daha ekler — mevzuat/güvenlik uyuşmazlığının koşuyu bloklaması; **bu ayak ortak değildir** ve 4.5'teki bloklama kapısı kararına bağlıdır.

**Motorun karar veremediği maddeler** `[SEA-2026-08-11]`**.** Yön ortaktır: değişiklik yapılmaz, mevcut kalıp korunur ve durum koşu raporuna yazılır. **Statü farklıdır:** bir hakem bunu deterministik bir güvenli varsayılan tablosu olarak karara bağlar — belirsiz eski kalıp → koru · belirsiz yeni kalıp → ekleme · belirsiz güncelleme → eski biçimi koru · belirsiz çıkarma → çıkarma · **belirsiz mevzuat/güvenlik → koşuyu blokla**; diğeri aynı yönü eğilim olarak yazar ve kararı **K-23**'te açık bırakır. Kararsızlık oranının tur durdurma eşiği **K-24**'te açıktır ve ölçülmeden eşik konmayacaktır — bu bölümde de eşik tanımlanmamıştır.

**Yalnız bir hakemde bulunan ikinci kapı: iki denetçi mutabakatı.** O belgede motor katmanında `guncelle` ve `cikar` için iki denetçinin uyuşması şart koşulur (uyuşmazlık → eski kalıbı koru; uyuşmazlık mevzuat veya güvenlik iddiasındaysa → koşuyu blokla); yeni kalıpta `2-3` eşiğinin üstüne iki denetçi kabulü eklenir ve tek resmî/birincil kaynak istisnası ancak iki denetçinin URL doğrulamasıyla kullanılabilir. Diğer belgede pozitif kanıt satırı gerekli koşuldur, ikinci bir mutabakat kapısı tanımlı değildir — açıkça reddedilmiş de değildir. Yeni bir kapı olduğu için tek hakem beyanıyla çözülmüş sayılmaz. **Bağlı karar kümesi olarak Bölüm 17'ye taşınır — iki ayrı karar:** (i) mutabakat kapısının benimsenip benimsenmeyeceği, (ii) benimsenirse denetçi görev sözleşmesine aktif paketin yeniden doğrulama envanterinin hangi ek adı ve şemasıyla ekleneceği. İkisi ayrı ayrı karara bağlanamaz: (i) alınıp (ii) alınmazsa kapı girdisiz kalır ve fiilen çalışmaz.

### 4.4 Alan/ürün özgüllüğü

**Paketin varlık nedeni sektörler arası ayrışmadır** (ortak hüküm). Çapraz sektör testi: bir ifade başka bir sektörün paketine konduğunda sırıtmıyorsa ana paket öğesi olamaz; yalnız sektöre bağlanarak yeniden yazılmış hâliyle girebilir. Denetim tarafında bu, iki belgede de bulunan `[genel-geçer]` bayrağıyla işaretlenir; `[yerel-değil]` ve `[muhtemel-uydurma]` bayraklarıyla birlikte `ekle` kararını doğrudan etkiler (4.3).

**Varyasyonun oluştuğu boyutlar** — derli toplu liste yalnız bir hakemdedir, diğeri reddetmez: (1) alt sektör; (2) içerik türü (satış / tanıtım / bilgi / özel gün); (3) üretim yüzeyi (caption ≠ görsel ≠ video hareketi); (4) takvim dönemi ve tür etiketi (`kutlama` / `anma` / `ticari-firsat` / `karma`); (5) **marka düzeyi sapma — bu boyut pakete değil Marka DNA'sına aittir.**

**Çift enjeksiyon yasağı — ortak hüküm.** Sektör ortalaması pakette, markaya özgü sapma DNA'da yaşar; aynı bilgi iki katmandan basılmaz. Karşı yön de yazılıdır: sektör paketindeki genel bilgi DNA'ya kopyalanmaz ve DNA çıkarımı yapılırken aktif paket yalnız kontrast referansıdır (Bölüm 12).

### 4.5 İnsan onayı ve otomasyon sınırı

**Otomasyon sınırı kaynak dokümanlardaki modelden kaydırılmıştır — iki belgede de** `[SEA-2026-08-11]`**.** Kaynak model "operatör kalıp kararlarını tek tek inceler" varsayımına dayanıyordu; her iki hakem de bunu ölçek gerekçesiyle bırakır. Gerekçenin kendisi **ölçülmemiştir** ve bu bölümde eşik veya kabul kriteri yapılmaz; `[ÖLÇÜLMEMİŞ VARSAYIM]` olarak beslediği kararların gerekçesine bağlıdır — **K-21** (hedeflenen sektör ölçeği) ve **K-22** (motorun fazı); ek bağ **K-13** (Faz 1 aktif paket tavanı). Ölçümü pilotta yöneticinin tur başına gerçek süresidir (Bölüm 13, Bölüm 2.1). Yerini alan hüküm kesinleştiği için eski model burada tekrarlanmaz; geçmişi Ek B'de tutulur.

**Otomatik verilen kararlar** (ortak): biçimsel eleme (`brief-doctor`, LLM'siz) · denetçilerin iddia sınıflandırması ve bayraklaması (**karar vermez, önerir**) · alan-alan hizalama, evrimsel kararlar ve boyut kırpması (sentez) · kalıp-başına değişim kararlarının kontrolü ve uygulanması (**politika motoru**) · çalışma zamanında paket seçimi ve enjeksiyon.

**İnsan onayı gerektiren kararlar** (ortak):

1. **`draft → active` aktivasyonu** — insan checkpoint'inin kural olarak korunduğu noktadır.
2. **Marka → alt sektör ataması** — LLM aday listeden önerir veya boş döner, **son sözü marka sahibi (kullanıcı) söyler**; bu ortak ve karara bağlanmış hükümdür (Bölüm 3.3, Bölüm 9). Bir hakem bu bölümde teyidi "marka sahibi **veya** operatör" diye yazar; aynı belgenin atama akışı son sözü kullanıcıya verdiği için bu **genel bir sahiplik ayrışması değildir.** Ortak kaynak karar dokümanı da bu maddeyi "LLM önerir, **kullanıcı teyit eder**" başlığı altında kurar. Mevcut markaların "elle atanması", toplu geriye dönük atamanın kapsam dışı olmasının operasyonel sonucudur (Bölüm 3.4); kullanıcı kararını geçersiz kılma yetkisi değildir. **Bu yüzden burada yeni bir karar açılmamıştır**; atama akışı Bölüm 9'da yazılırken yeniden kontrol edilecektir.
3. **Tur başına değil, bir kez verilen politika kararları** — takvime gün ekleme (**K-01a**) ve paket `tur` ↔ DB `category` çakışma politikası (**K-03**); motor bunları uygular.

> ⚠️ **"Tek nokta" nitelemesi K-23 kapanana kadar koşulludur.** K-23'ün seçeneklerinden biri, motorun kararsız bıraktığı maddelerin **yöneticiye açık soru olarak düşmesidir**; bu seçenek benimsenirse aktivasyonun yanında ikinci bir insan müdahale noktası doğar. Kaynak dokümanların kalıp-kalıp inceleme modeline dönüş söz konusu değildir — açık kalan yalnız **motorun kararsız bıraktığı istisnaların** insan müdahalesi gerektirip gerektirmediğidir.

**Yönetici neyi görür, hangi seviyede karar verir.** Yönetici kalıpları tek tek değerlendirmez. Gördüğü iki şey vardır: **koşu sonucu** ve **özet diff**. Koşu sonucu üç değerlidir — `activation_eligible` · `no_change` · `blocked` — ve yalnız `activation_eligible` koşuda aktivasyon onayı verilebilir; bu sonuç otomatik aktivasyon anlamına gelmez. Kalıp-kalıp liste **zorunlu değildir**; istenirse açılabilir olmalıdır, ama onay bu listenin okunmasına bağlanamaz. Karar seviyesi **ürün seviyesidir** (kapsam, tradeoff, risk kabulü); şema, imza ve algoritma doğruluğu onay yüzeyine değil inceleme zincirine aittir.

> **Seviye ayrımı — üç ayrı seviye karıştırılmaz.** Yukarıdaki üçlü **koşu** seviyesidir. **Kalıp-kararı** seviyesinin sonuçları ayrıdır (`uygulandı` · `uygulanmadı (kanıt yetersiz)` · `motor kararsız`) ve yalnız diğer hakemde tanımlıdır. **Paket statüsü** (`draft` / `active` / `archived`) üçüncü ve ayrı seviyedir. Aynı hakemde koşu seviyesine ait bir öğe daha vardır (`tur durduruldu`) ve `blocked` ile aynı yeri doldurur; ikisinin birleştirilip birleştirilmeyeceği açık karardır — karar ID'si Bölüm 17 sweep'inde verilecektir.

**Otomatik çözülemeyen politika çatışmasında ne olacağı açık karardır.** Bir hakem bunu bir **bloklama kapısı** yapar: mevzuat, kategori çatışması ve kapsam tercihi gibi kararlar otomatik çözülemiyorsa koşu bloklanır ve konu istisna olarak yöneticiye çıkarılır. Diğer hakemde böyle bir kapı bulunmaz: paket `tur` ↔ DB `category` çelişkisinde sentez karar vermez, konuyu **açık soruya düşürür**; o belgede turu durduran tek mekanizma motorun **kararsızlık oranının** eşiği aşmasıdır (**K-24**, eşik tanımsız). İki mekanizma farklı şeyi ölçer ve bloklama tetikleyicilerinin kümesi ortak değildir. Yeni bir kapı tek hakem beyanıyla kurulamayacağı için gövdede tek taraf yazılmaz; **açık karar olarak Bölüm 17'ye taşınır** — **K-23** ile ilişkilidir, karar ID'si sweep'te verilecektir. ⚠️ **K-03'ün kapanması bu kapıyı KAPATMAZ ve gerekçesini de daraltır:** kategori çatışması artık politikayla çözüldüğü için (paket türü üstündür — Bölüm 11.2) kapının bu çatışmadan doğan tetikleyicisi düşer; **mevzuat ve kapsam tercihi tetikleyicileri yerinde kalır** ve kapı kendi başına açık bir karardır.

**Arşiv güvencesi otomasyonla düşmez.** Motor bir kalıbı çıkarıyorsa karar günlüğüne **pozitif kanıt satırı** yazmak zorundadır; kanıt yoksa çıkarma uygulanmaz ve kalıp korunur. Özet diff, çıkarılan kalıp **sayısını** ve eşik-üstü olanları gösterir; **bu eşik iki belgede de tanımlı değildir ve bu sentezde uydurulmamıştır.** İlke ortaktır: geçersizlik veya güncelleme mutabakatı yoksa otomasyon eski kalıbı yeni aday pakete taşır. Aksi hâlde otomasyon, bilgi kaybı güvencesini sessizce boşaltır; risk kaydı Bölüm 18'de tutulacaktır.

**Güvencenin sınırı da normatiftir — over-claim yapılmaz.** Verilen garanti şudur: *"gözlemlenebilir değeri olan hiçbir kalıp sessizce kaybolamaz."* **Sıfır-kayıp garantisi verilmez** — izlenebilir değeri olmayan bir kalıp arşivde kalabilir. İkinci sınır: geri-ekleme tespiti **kalıp metnine dayanır**, bu yüzden **metni değişmiş bir kalıp çıkarılanlar listesiyle eşleşmeyebilir** ve çelişki tetiklenmeden yeniden eklenebilir. Bu, kaynaklarda **kabul edilmiş** bir zayıflıktır. Zayıflığı kapatacak olan **kalıcı kalıp kimliği ise açık karardır** (kalıp kimliği sözleşmesi, Bölüm 3.1): bir hakem kalıcı kimliği motor için zorunlu sayar, diğeri kalıp düzeyinde kalıcı kimlik öngörmez ve konuyu sonraki faza bırakır. Bu bölümde taraf tutulmaz ve **yeni karar açılmaz** — mevcut açık karara bağlanır (Bölüm 8.4).

> ⚠️ **Belge-içi gerilim — bu bölümde çözülmez.** Bir hakem belgesi insan onayını yalnız aktivasyona indirirken, aynı belgenin aktivasyon ön koşulları arasında hâlâ "açık soruların tamamı operatörce kapatılmış" maddesi durur; motorun kararsız bıraktıklarının akıbeti ise **K-23**'te açıktır. Belge bunu kendi içinde çözmez. Diğer hakemin aktivasyon ön koşulları kapalı bir liste olarak sayılır ve bu maddeyi içermez. İkisi Bölüm 8'de birlikte ele alınacaktır.

### 4.6 Öncelik ve bağlam hiyerarşisi

[GEREKİRSE]

**Ortak çekirdek — tartışmasız uçlar:**

1. En üstte **mutlak güvenlik, mevzuat ve fabrication kuralları**; sektör paketi bunları geçersiz kılmaz.
2. **Sektör paketi markanın gerçeği değildir**, sektörel bir dağarcıktır; kullanıcının somut içerik isteğinin ve gerçek ürün bilgisinin altındadır.
3. Marka DNA'sı ile sektör paketi çatıştığında **DNA kazanır.**
4. En altta **platform tonu ve kök sektör rehberi**; aktif paket varken kök rehber paketle yan yana basılmaz, paket onun yerine geçer (4.1).

**Açık karar — orta basamakların sırası.** İki belge 2.–4. basamaklarda ayrışır ve gövdede tek sıra yazılamaz. Ortak olan: markaya özgü **yasak kelime/ifade** kısıtları kullanıcının somut isteğinin üstündedir (bir belge bunu ayrı bir basamak yapar, diğerinde aynı kısıt Marka DNA'sının içinde "mutlak kısıt" olarak aynı yerde durur). Ayrışan: Marka DNA'sının **yasak kelime dışındaki** kısmının (ör. ses/üslup profili) kullanıcının somut isteğine göre nerede durduğu — bir belge onu isteğin **altına**, diğeri **üstüne** koyar. İkinci ayrışma: bir belge "gerçek ürün bilgisi"ni kullanıcı isteğiyle aynı basamakta ayrıca adlandırır, diğeri hiyerarşide ayrı basamak olarak adlandırmaz ve bu korumayı dağarcık kullanım talimatında taşır. Kararın belirlediği davranış: aynı üretimde kullanıcının somut isteği ile markanın ses/üslup profili çatıştığında hangisinin kazanacağı.

**Açık karar — paketin geçersiz-kılıcı yetkisi (`anma`).** Bir belge, özel gün `anma` türündeki içerik kısıtını (satış dili yasağı) paketin **tek** geçersiz-kılıcı yetkisi sayar ve kullanıcı satış dili istese bile kısıtın üstün olduğunu yazar. Diğer belge `anma` akışında satış ve kutlama dilini koşulsuz yasaklar, ancak öncelik düzeninde kullanıcının somut isteğini paketin üstüne koyar ve pakete istisna tanımaz; **bu belge bu noktada kendi içinde tutarsızdır** ve bu yüzden konu iki pozisyon olarak taşınamaz. Kararın belirlediği davranış: kullanıcı `anma` günü için satış postu istediğinde sistemin ne üreteceği.

**Dağarcık kullanım kuralı — K-04.** Paketin liste alanları modelde "listeyi tamamlama" refleksini tetikler ve bu refleks fabrication yasağıyla doğrudan çatışır. Bu yüzden **her enjeksiyon bloğunun başına sabit bir kullanım talimatı yazılır:**

> *"Bu dağarcıktan içeriğe uyan 2-3 öğeyi seç; listeyi tamamlamaya çalışma; ürün veya marka bilgisiyle çelişen kalıbı kullanma; markanın sahip olduğunu bilmediğin kanalı veya hizmeti önerme."*

Kural ve talimatın içeriği iki belgede de aynıdır; **statüsü farklıdır:** bir belge kararı verilmiş sayar ve açık karar listesinde satır tutmaz, diğeri **kendi açık karar satırını** korur (bu belgedeki karşılığı **K-04**), yönün netleştiğini ama kesin prompt şablonu ile test fixture'larının uygulama spec'ine ait olduğunu yazar. Bu belgede kural normatiftir; kesin şablon ve fixture uygulama spec'ine bırakılır. Talimatın son cümlesi aynı zamanda kanal-bağımlı kalıplar için hafif önlemdir (**K-05**, Bölüm 3.1). Refleksin kaynağı olan liste alt sınırları (görsel kod, CTA ve kanca alanlarının asgari öğe sayıları) girdi kapısının şablon eşikleridir; **ölçülmüş değil tasarım kararıdır** ve burada kabul kriteri yapılmaz (Bölüm 7.3).

**Çift enjeksiyon yasağı** bu hiyerarşinin tamamlayıcısıdır ve 4.4'te tanımlanmıştır.

---

## 5. Üst düzey mimari

[ZORUNLU]

**Mimarinin örgütleyici ilkesi — iki ayrı çalışma zamanı** (ortak hüküm; bu adlandırma bir hakem belgesinden gelir, diğeri aynı ayrımı akışını ikiye bölerek kurar):

- **Bilgi üretim zamanı** — araştırma, denetim, sentez, politika kontrolü ve aktivasyon. **Seyrek çalışan operasyonel süreçtir** (tur periyodu 3 **veya** 6 ay — **K-26**).
- **İçerik üretim zamanı** — aktif paket, her üretim isteğinde **deterministik kurallarla** seçilip prompt'a eklenir.

İki zaman arasındaki tek bağ **aktif pakettir**: bilgi üretim zamanı onu üretir, içerik üretim zamanı onu okur. Bu ayrım bölüm boyunca korunur; bileşenler, akışlar ve entegrasyon noktaları bu iki kümeye göre yazılmıştır.

> **Statü uyarısı `[SEA-2026-08-11]`:** politika motoru, `no_change` sonucu ve yöneticinin yalnız koşu sonucuna verdiği son onay **kaynak dokümanlardan gelmez**; sonraki ölçeklenebilirlik analizinden gelir. Motorun bu mimariye giriş fazı karara bağlandı: ✅ **K-22 KAPANDI — A** (2026-08-21, Ek B) — motor **Faz 1'de** hattadır (Bölüm 3.1, 4.5).

### 5.1 Bileşenler

**Bilgi üretim zamanı**

| Bileşen | Sorumluluk | Girdi | Çıktı | Mevcut / yeni |
|---|---|---|---|---|
| Araştırma brief şablonu | Üç araca verilen tek metin; yalnız sektör bloğu doldurulur | Sektör bloğu | Doldurulmuş brief | **Mevcut** (dosya, kanonik) |
| Araştırma araçları (3 adet) | Bağımsız derin araştırma koşusu | Aynı brief | KAYNAK-1/2/3 ham rapor | **Mevcut** — dış ve **elle** işletilir |
| `brief-doctor` | Mekanik/biçimsel eleme — **LLM yok** | KAYNAK-1/2/3 + şablonun biçim kuralları | Elenen/notlu kaynak raporu | **Yeni** |
| Denetçi-1 | İddia düzeyi denetim; **karar vermez, önerir** | Brief, kaynaklar, eleme raporu | Yapılandırılmış denetim tablosu | **Yeni** |
| Denetçi-2 | Aynı görev, **bağımsız ve kör** | Aynı girdiler | Yapılandırılmış denetim tablosu | **Yeni** |
| Sentez | Alan-alan hizalama + kalıp-başına evrimsel karar + boyut kırpma; **karar mercii** | Brief, iki denetim tablosu, aktif paket, çıkarılanlar listesi, sistem özel gün listesi, **kök sektör rehberi** | Aday paket JSON + karar günlüğü + açık sorular | **Yeni** |
| **Politika motoru** `[SEA-2026-08-11]` | Kalıp-başına kararları **otomatik kontrol edip uygulamak**; kararsızları ayırmak | Sentez çıktısı, aktif paket, çıkarılanlar listesi, politika kuralları | Uygulanmış karar seti + özet diff + koşu raporu | **Yeni** — fazı **K-22** |
| Özet diff üretici `[SEA-2026-08-11]` | Sürümler arası farkın **özetlenmesi** (kalıp-kalıp liste değil) | Aktif paket + yeni `draft` + karar günlüğü | Yöneticinin aktivasyon kararını verdiği görünüm | **Yeni** |
| `content` doğrulayıcı | Alan şeması, boyut tavanı ve özel gün anahtarı normalizasyonunun zorlanması | `draft` JSON | Kabul / red | **Yeni** |
| Yönetici koşu yüzeyi | Sektör seçimi, kaynak yükleme, turu tetikleme, sonucu görme, aktivasyon | Yönetici girdileri | Koşu tetiklemesi + onay eylemi | **Yeni** ⚠️ *(bu satırda `Yeni` sınıflandırması **tek hakemden** gelir ve bu sentezde doğrulanmamıştır — Bölüm 17'nin ⑤ kalemi: yönetici koşu yüzeyinin bugünkü varlık durumu)* — yüzey karara bağlandı: ✅ **K-27 KAPANDI — A** (2026-08-21, Ek B): Claude Code komut ailesi |
| Ham artefakt deposu | Kanıt katmanı; **salt-ekleme** (güncelleme/silme veri tabanı düzeyinde reddedilir) | Koşunun bütün metin çıktıları | Sorgulanabilir kanıt tabanı | **Yeni tablo** |
| Paket deposu | Sürümlü paket; sektör başına **tek** `active` | Doğrulayıcıdan geçmiş `draft` içerik (üreticisi **K-22**'ye bağlı) + yönetici aktivasyon onayı | `active` paket | **Yeni tablo** |

⚠️ **`Mevcut / yeni` sütununun statüsü tek bir katmandan gelmez — üç sınıf ayrı tutulur:**

1. **Kaynak katmanında karşılığı olan bileşenler** (`brief-doctor` · iki denetçi · sentez ·
   `content` doğrulayıcı · ham artefakt deposu · paket deposu · mevcut şablon ve araçlar):
   sınıflandırma **2026-07-11 taramasından aktarımdır** `[AKT·KAYNAK · 2026-07-11]` ve **bu
   sentezde canlı kod/veri tabanına karşı yeniden doğrulanmamıştır** (2.1 md.2).
   *"Bugün yok"* değil, **"aktarılan son duruma göre yok"** okunur.
2. ⚠️ **`[SEA-2026-08-11]` bileşenleri — politika motoru ve özet diff üretici:** bunların
   `Yeni` statüsü **`[AKT·KAYNAK]` DEĞİLDİR** ve *"aktarılan son duruma göre yok"* kümesinin
   **üyesi değildirler**: 2026-07-11 taraması bu bileşenleri **aramamıştır** — kavram
   **2026-08-11 analizinde doğmuştur**, taramadan sonra. **İki iddia ayrı tutulur:**
   *(i)* **kaynak katmanında bulunmadıkları ÖLÇÜLDÜ** (dokuz kaynak dosyada *politika
   motoru* **0 isabet**) — bu bir **provenans olgusudur**; *(ii)* **güncel sistemde var
   olup olmadıkları bu sentezde ÖLÇÜLMEMİŞTİR** → `[BU SENTEZDE DOĞRULANMADI]`.
   ⚠️ **Birincisi ikincisini kanıtlamaz:** kaynakta önerilmemiş olmak, bugün kurulmamış
   olduğunun kanıtı değildir.
3. ⚠️ **Yönetici koşu yüzeyi:** sınıflandırma **tek hakemdedir** ve Bölüm 17'de bir
   **⑤ doğrulama kalemine** bağlanmıştır.

**İçerik üretim zamanı**

| Bileşen | Sorumluluk | Girdi | Çıktı | Mevcut / yeni |
|---|---|---|---|---|
| Alt sektör taksonomisi | Mevcut sektör tablosunda parent'lı satırlar | — | Alt sektör kimlikleri | **Mevcut kolon, yeni veri** |
| Alt sektör öneri (LLM) | Site analizi sözleşmesine alan ekleme; **yalnız aktif paketli listeden** seçim | Site metni veya marka adı/açıklaması + aday liste | Aday alt sektör **veya boş** | Mevcut uç `[AKT·KAYNAK · 2026-07-11]`, **genişletme** |
| Alt sektör teyit bileşeni | Önceden seçili açılır liste | LLM önerisi | `brands.sub_sector_id` | **Yeni arayüz** — yerleşimi **K-19** |
| Paket çözücü | `sub_sector_id` + `active` paket araması | Marka kaydı | Paket içeriği **veya yok** | **Yeni** |
| Tier 2 enjektörü | Kök rehber yerine paket bloğu | Paket içeriği | Marka bağlamı metni | Mevcut `build_brand_context` 232-235 `[AKT·KAYNAK · 2026-07-11]`, **genişletme** |
| Fikir önerme yolu enjektörü | Aynı yerine-geçme kuralının fikir önerme ucunda uygulanması | Paket içeriği | Fikir önerme marka bağlamı | Mevcut uç `ai.py:275-277` `[AKT·KAYNAK · 2026-07-11]`, **genişletme** |
| Tier 3 özel gün enjektörü | Eşleşen günün kalıplarını ekler | Paketin özel gün bloğu + seçili gün | Özel gün bağlamı bloğu | Mevcut blok, **genişletme** |
| Caption görsel director enjektörü | Görsel dağarcığının çıktı talimatına eklenmesi | Paket | Görsel prompt eki | Mevcut `caption_generator._build_output_format_instruction` 353-359 `[AKT·KAYNAK · 2026-07-11]`, **genişletme** |
| Kısa video director enjektörü | Sektör görsel dili — **iki mod** (metinden görsele ve ürün referanslı) | Paket | Durağan kare prompt eki | Mevcut `short_video.py` 128-129 + 187-231 `[AKT·KAYNAK · 2026-07-11]`, **genişletme** |
| Motion havuzu seçici | Paket yolunda sektör havuzundan, mevcut yolda bugünkü sabit listeden | Paketin video hareket alt listesi | Hareket prompt'u | Mevcut `_MOTION_PROMPTS` 263-277 `[AKT·KAYNAK · 2026-07-11]` — **K-02'ye bağlı** |
| Sürüm damgalayıcı | Üretimi kullanılan paket sürümüne bağlamak | Paket | Post kaydındaki ilişki | **Yeni** — fiziksel temsil **K-07** |
| Legacy kısa video yolu | Sektör rehberini slug yerine **görünen adla** arar → rehberin boş dönmesine yol açar; ön yüzün bu yolu çağırmadığı aktarılmıştır `[AKT·KAYNAK · 2026-07-11]` | Marka kaydı | (aktarıma göre boş sektör bağlamı) | **Mevcut, sessiz hata** — yerine-geçme kuralının bu yola uygulanıp uygulanmayacağı **K-06** |

**İki zamanı kesen bileşen**

| Bileşen | Sorumluluk | Girdi | Çıktı | Mevcut / yeni |
|---|---|---|---|---|
| Prompt yakalama düzeneği | **Katman-1** byte-exact prompt regresyonu | Üretim çağrısı | Prompt metin anlık görüntüleri | **Yeni.** Marka DNA işiyle **ortak kullanımı K-20**'de açıktır; kaynak DNA dokümanı kendi hiyerarşi testini bu protokole bağlar |

> **Bileşen envanterinin sınırı.** Ayrıştırma büyük ölçüde bir hakem belgesinden gelir; diğeri aynı mimariyi **akış düğümleri** olarak verir ve ayrı bir bileşen tablosu taşımaz. Düğümler tek tek eşlenmiştir; eşleşmeyen tek nokta **fikir önerme yolunun** ilk belgede bileşen satırı olarak bulunmamasıdır — o belge yolu kendi enjeksiyon haritasında ele alır, dolayısıyla **kapsam dışı bırakılmış değildir**.

> **`draft` içeriğini kim üretir — modele bağlıdır; yürürlükteki cevap politika motorudur** (✅ **K-22 KAPANDI — A**, Ek B). Motorsuz modelde (yürürlük dışı) aday paketi **sentez** üretir ve `draft` doğrudan sentez çıktısından yazılır; motorlu modelde `draft` içeriğini **politika motoru** üretir (sentezin çıktısı o modelde motorun girdisidir). **İki modelde de ortak olan iki hüküm:** `content` doğrulayıcısı **veri tabanına yazımdan önce** çalışır ve reddederse yazım olmaz; kayda **yalnız `draft`** yazılır. Bu bölüm iki modeli de taşır; ✅ **K-22 KAPANDI — A** (2026-08-21, Ek B) — yürürlükteki model **motorlu modeldir**: `draft` içeriğini **politika motoru** üretir.

> **Enjeksiyon yüzeylerinin bütünlüğü — üç tüketici.** Kök sektör rehberinin yerine-geçme kuralı **üç** tüketiciye birden uygulanmalıdır: ana üretim yolu, fikir önerme yolu ve legacy kısa video yolu. İlk ikisi ortak hükümdür. Üçüncüsü **K-06**'da açıktır: kaynak doküman ve iki hakem belgesi aynı şeyi söyler — yol **ya düzeltilir ya açıkça kapsam dışı notlanır, sessiz bırakılmaz.** Seçim ürün/kapsam seviyesinde bir karardır ve bu bölümde kapatılmaz; Bölüm 4'ün kademeli geçiş ilkesi legacy yolları kapsadığı için burada **görünür kalır**.

### 5.2 Uçtan uca akış

**A) Bilgi üretim zamanı — tur akışı**

```text
[Yönetici: sektör seçimi + brief doldurma + KAYNAK-1/2/3 yükleme]
      ↓                         (Otomaix müşterisi bu akışta yer almaz)
[brief-doctor — mekanik eleme, LLM yok]
      ↓  elenen / notlu kaynak raporu
[Denetçi-1]  ‖  [Denetçi-2]      (bağımsız ve kör)
      ↓  iki yapılandırılmış denetim tablosu — karar yok, öneri var
[Sentez — alan alan hizalama + kalıp-başına evrimsel karar]
      ↓  girdiler: brief · aktif paket · çıkarılanlar listesi · sistem özel gün listesi
                 · kök sektör rehberi (nüans kaybına karşı — onaylı karar)
[Sentez raporu ham katmana yazılır]
      ↓
[POLİTİKA MOTORU — kararları kontrol eder, uygular, kararsızları ayırır]
      ↓          ⚠️ bu adımın hatta bulunup bulunmaması K-22'ye bağlıdır;
                    motorsuz modelde aday paketi sentez üretir ve akış
                    doğrudan doğrulayıcıya geçer
      ├─ değişiklik yok ────► koşu kapatılır; yeni sürüm oluşturulmaz
      ├─ bloklandı ─────────► mevcut aktif paket korunur; nedenler raporlanır
      └─ aktivasyona uygun ─► [content doğrulayıcısı — DB yazımından ÖNCE]
                                    ↓  (reddederse yazım olmaz)
                              [yalnız draft yazılır]
                                    ↓
                              [Katman-1 byte-exact + Katman-2 kör örneklem]
                                    ↓
                              [YÖNETİCİ: koşu sonucu + özet diff]
                                    ├─ Onay ──► eski sürüm archived → draft active
                                    └─ Ret ───► mevcut aktif paket korunur
```

Akışın üç hükmü **ortak**: denetçiler karar vermez, sentez karar mercii, aktivasyon insana aittir. Kalıp-kalıp inceleme **zorunlu değildir**; ayrıntı istenirse açılabilir olmalıdır (Bölüm 4.5).

⚠️ **Akışta görünen ama yeri kapanmamış üç nokta.** (a) `değişiklik yok` ve `bloklandı` koşularının **nerede kayıtlandığı** — paket satırı oluşturmadan durumlandırılmaları açık karardır ve yalnız bir hakemde ele alınmıştır. (b) `Ret` yolu yalnız bir hakemde **adlandırılmıştır**; diğerinde aynı sonuç, aktivasyon yapılmadığında aktif paketin dokunulmadan kalmasıyla örtük olarak sağlanır — çelişki yoktur, adlandırma farkıdır. (c) İki denetimin **paralel mi sıralı mı** yürütüleceği ve oturum izolasyonunun teknik garantisi açık karardır (Bölüm 3.3); yukarıdaki `‖` işareti iki belgenin de **çizdiği** topolojiyi gösterir, teknik garantiyi değil.

**B) İçerik üretim zamanı — üretim anı**

```text
[İçerik üretim isteği (+ istenirse özel gün seçimi)]
      ↓
[Marka yüklenir: kök sektör + alt sektör]
      ↓
[alt sektör boş mu?] ──EVET──► [mevcut yol — prompt parçaları byte-exact değişmez]
      ↓ HAYIR
[aktif paket var mı?] ──HAYIR──► [mevcut yol — prompt parçaları byte-exact değişmez]
      ↓ EVET
[Tier 2: paket bloğu basılır; kök sektör rehberi ATLANIR — yan yana yasak]
      ↓
[özel gün seçili ve paketle eşleşiyor mu?]
      ├─ eşleşti  → Tier 3 özel gün bloğuna dönem kalıpları
      └─ eşleşmedi→ SESSİZ DÜŞME + LOG (sessiz regresyon görünürlüğü)
      ↓
[Görsel ve video yüzeyleri: görsel dağarcığı → caption director;
 video: durağan kare (iki mod) + hareket havuzu (K-02)]
      ↓
[Üretim → post kaydı, kullanılan paket sürümüne bağlanır (K-07)]
```

Bu hattın **hedeflenen** davranış sözleşmesi **fail-safe**'tir: paket yoksa, bozuksa veya çözülemezse üretim bloklanmaz, mevcut yola düşer ve durum log'lanır. **Paketin bulunmadığı** hâl iki belgede de kapanmış hükümdür. **Bozuk veya eksik paket içeriğinde** runtime davranışı ise **K-15 (a)**'da açıktır — bir hakem yalnız "beklenmeyen eksiklik log üretmeli" der, davranış canlı sistemde doğrulanmamıştır. Fail-safe burada **hedef davranıştır, mevcut sistem olgusu değildir**; kapanması spec yazımını değil **uygulama/aktivasyonu** bekletir.

### 5.3 Entegrasyon noktaları

| Kaynak sistem | Hedef sistem | Veri / olay | Protokol / yöntem | Hata davranışı |
|---|---|---|---|---|
| Araştırma araçları (dış, elle) | Dosya sistemi | KAYNAK-1/2/3 | Elle teslim; koşu başına tek klasör (`research-runs/<run_id>/`) — **kaynak dokümanda öneri, spec'te kesinleşir → K-17** | Eksik dosya → eleme raporunda görünür; koşu kalan kaynaklarla **kısmi devam eder** |
| `brief-doctor` | Denetçiler | Eleme ve not raporu | Koşu yüzeyi otomatik ekler | Elenen kaynak denetim dışıdır; denetçi kalan kaynak sayısına göre sınıflandırmayı uyarlar |
| Denetçi-2 | Web (URL doğrulama) | Getirme isteği | Ortam yeteneğine bağlı | **Erişim yoksa uydurma yasak** — "doğrulanamadı (ortam kısıtı)" yazılır; ikisi de yapamazsa iddia doğrulanmamış işaretlenir. Erişimin bulunup bulunmadığı ve **koşu öncesi ön kontrol** **K-14**'te açıktır; kanıt ağırlığı kuralı sentez görev sözleşmesinde tanımlıdır (Bölüm 7.4) |
| Sentez **veya** politika motoru (**K-22**) | Paket deposu | `draft` satırı | Koşu yüzeyi → veri tabanı | **Yalnız `draft` yazılır**; `content` doğrulayıcısı **yazımdan önce** çalışır, reddederse yazım olmaz. Satırın sahibi K-22'ye bağlıdır |
| Politika motoru | Paket deposu | Uygulanmış karar seti + koşu raporu | Koşu yüzeyi → veri tabanı | `active`'e geçirme yetkisi **yoktur** (**K-28**); `bloklandı` sonuç aktivasyon üretemez. `değişiklik yok` ve `bloklandı` koşularının nerede kayıtlandığı açık karardır |
| Yönetici | Paket deposu | Durum geçişi | Onay akışı | Tek-aktif kısmi indeks ikinci `active`'i reddeder — yanlış sıra veri bozmaz, hata verir |
| Sistem özel gün takvimi | Sentez girdisi + Tier 3 | Gün adı ve kategorisi | Veri tabanı okuma | Takvimde karşılığı olmayan dönem pakete **girmez**; üretimde eşleşmezse sessiz düşme + log. Anahtar sözleşmesi **K-01b**, kategori-tür önceliği **K-03** |
| Site analizi ucu | Alt sektör öneri alanı | Aday liste → seçim veya boş | Mevcut JSON sözleşmesine alan ekleme `[AKT·KAYNAK · 2026-07-11]` | **Serbest metin dönüşü yasak** (halüsinasyon kapısı); site yoksa marka adı/açıklamasından fallback |
| Paket çözücü | Prompt yüzeyleri | Paket alanları | İç fonksiyon çağrısı | **Paket yoksa** → mevcut yol (fail-safe, sessiz + log) — kapanmış hüküm. **Paket bozuk/eksikse** davranış **K-15 (a)**'da açıktır; yukarıdaki fail-safe o dal için hedef davranıştır |
| Üretim | Post kaydı | Paket sürüm ilişkisi | Veri tabanı yazımı | Paket yolu dışındaki üretimde **geçerli bir paket ilişkisi bulunmaz**; fiziksel temsil **K-07**'de açıktır |
| Marka DNA sistemi | Aynı Tier 2 bloğu | DNA alanları | `build_brand_context` | İki sistem **aynı bloğu ve aynı token bütçesini** paylaşır; toplam bütçe ölçümü **K-12** (Bölüm 12) |

**Takvim beslemesinin işletim biçimi** (yıllık zamanlanmış iş) yalnız bir hakem belgesinde anlatılır, ancak **kaynak dokümanda karşılığı bulunmaktadır** `[AKT·KAYNAK · 2026-07-11]`: kaynak, takvimin yıllık zamanlanmış bir işle dolduğunu ve eksik günlerin eklenmesi kararı alınırsa (**K-01a**) eklemenin oraya da işlenmesi gerektiğini yazar. Takvimin **sistem tarafı doğruluk kaynağı olması** ise ortaktır ve kaynakta da bulunur.

**Kök sektör rehberi sentezin girdisidir — onaylı karar, açık karar değil.** Kök rehber metni hem paketsiz yolun bileşenidir hem de **damıtma adımının girdisidir**; gerekçe kök rehberdeki nüansların pakete geçerken kaybolmamasıdır. Bu, ortak kaynak karar dokümanında **onaylı kararlar başlığı altında** yazılıdır ve bu sentezde kaynağa karşı doğrulanmıştır. Bir hakem belgesi bunu taşır, diğerinin girdi listesinde bulunmaz — bu **karşı pozisyon değil, kaynak maddesinin o belgede düşmesidir**; kullanıcı kararı gerekmez.

⚠️ **Sözleşme drifti — resmî sentez görev sözleşmesinin girdi listesi eksiktir.** Sözleşme sentezin girdilerini ek ek sayar (brief · iki denetçi çıktısı · aktif paket · çıkarılanlar listesi · sistem özel gün listesi) ve **kök rehberi içermez.** Onaylı karar ile yürürlükteki sözleşme arasındaki bu fark bir tasarım tercihi değil, bir **drift**tir; sözleşmeye karşılık gelen ek eklenene kadar **resmî hakem turu bu nedenle bloklanır**. Yeni karar açılmaz — düzeltme kalemidir.

---

## 6. Veri mimarisi

[ZORUNLU]

**Veri mimarisinin örgütleyici ilkesi — iki katman** (ortak hüküm; Bölüm 4.2'deki "kaynak veri ile türetilmiş çıktının ayrımı" ilkesinin veri karşılığıdır):

- **Ham kanıt katmanı** — araştırma, denetim ve sentez çıktılarının değiştirilmeden saklandığı yer. **Salt-ekleme**; güncelleme ve silme veri tabanı düzeyinde reddedilir.
- **Türetilmiş paket katmanı** — ham katmandan damıtılmış, **sürümlü** ve durum taşıyan operasyonel paket. Prompt'a giren tek şey budur.

İki katman arasındaki bağ **koşu kimliğidir** (`run_id`): paket satırı, kendisini üreten koşunun ham artefaktlarına bu alanla bağlanır. ⚠️ **Bağın zorunlu olup olmadığı kapanmamıştır** — iki belgenin şema taslağında da alan paket tarafında **zorunlu değildir**, oysa provenans bağının güvencesi zorunluluğa dayanır. Gerilim 6.2'de işaretlenmiştir; teknik akıbeti açıktır ve bu bölümde çözülmemiştir.

**Katman ayrımı ve tablo düzeyindeki şema kararları** iki hakem belgesinde de aynı biçimde kurulur ve **ortak kaynak karar dokümanında onaylanmış kararlar** olarak yazılıdır; bu bölümde kaynağa karşı denetlenmiştir. **Kimlik kuralları bu ortaklığın dışındadır:** sürümler arası kalıp kimliğinde iki belge **karşıt konumdadır** (6.3).

> **Bu bölümün kapsam sınırı.** Aşağıdaki şema taslakları `[TASLAK]` statüsündedir — kaynak doküman da onları taslak olarak verir ve "PK tipi ve adlandırma mevcut konvansiyona uyarlanacak" kaydını düşer. Şema **kesinleştirilmiş uygulama sözleşmesi değildir**; açık karara bağlı alanlar normatif hüküm yapılmamıştır (Bölüm 17'ye taşınanlar her alt başlıkta işaretlidir).

### 6.1 Varlıklar ve ilişkiler

| Varlık | Amaç | Sahip sistem | Temel ilişki |
|---|---|---|---|
| `social.sectors` — **kök satır** | Kök sektör kovası; trend katmanının ve marka atamasının tabanı | **Mevcut** | 1─N alt sektör (`parent_sector_id`) |
| `social.sectors` — **alt sektör satırı** | Paketin bağlandığı çözünürlük düzeyi | **Mevcut kolon, yeni veri** | N─1 kök; 1─N paket sürümü |
| `social.sector_research_artifacts` | Ham araştırma / denetim / sentez kayıtları — kanıt zinciri | **Yeni tablo** | Sektöre `sector_slug` ile, koşuya `run_id` ile bağlı |
| `social.sector_packages` | Sürümlü paket | **Yeni tablo** | N─1 alt sektör; sektör başına **tek** `active` |
| `brands` | Marka; kök kova + alt sektör bağı | **Mevcut** | N─1 kök (`sector_id`), N─1 alt sektör (`sub_sector_id`, null olabilir) |
| `social.public_holidays` | Sistem özel gün takvimi (gün adı + kategori) | **Mevcut** | Paketin özel gün anahtarlarının **doğruluk kaynağı** |
| `posts` | Üretilen içerik | **Mevcut** | Paketli üretimde kullanılan paket sürümüne bağlanır — fiziksel temsil **K-07** |

**Taksonomi kararı ortaktır ve kaynakta onaylıdır:** ayrı bir alt sektör tablosu **kurulmaz**; alt sektörler mevcut tabloya `parent_sector_id` dolu satırlar olarak girer. Kolonun şemada bulunması `[AKT·2H · 2026-07-11]`, verinin bugün boş olması `[AKT·KAYNAK · 2026-07-11]`.

**Kök kova invariantının koruma noktaları** (sektör listeleme ucu, kök sektör çözücü, trend önbelleği) Bölüm 3.1 ve 3.3'te ele alınmıştır; burada tekrar edilmez. Veri mimarisi açısından tek bağlayıcı hüküm şudur: **`brands.sector_id` kök kova anlamını korur**, alt sektör bağı **ayrı ve null olabilir bir kolonla** taşınır.

**`brands.sector` (TEXT) bu işte dokunulmazdır.** "Migration kalıntısı" olmadığı, video director'ın sektör satırı, fikir önerme, rakip analizi ve legacy yollar tarafından okunduğu aktarılmıştır; okuma noktası sayısı olarak anılan **7+** yalnız bir belgede ve kaynak dokümanda geçer. Spec bu kolonu **aktif girdi olarak bilmelidir**; TEXT ve UUID taşıyıcıların tekilleştirilmesi bakım borcudur ve **kapsam dışıdır** (Bölüm 3.2 — çözülmemiş kapsam kararı olarak Bölüm 17'ye taşındı).

### 6.2 Veri alanları ve şema ihtiyaçları

#### Ham artefakt tablosu — `social.sector_research_artifacts` `[TASLAK]`

| Alan | Tip/biçim | Zorunlu mu? | Kaynak | Açıklama / kural |
|---|---|---|---|---|
| `id` | uuid PK | evet | sistem | Kaynak taslağı `BIGSERIAL` yazar ve düzeltme notunu kendisi taşır: mevcut şemada PK'lar uuid'dir |
| `run_id` | metin | evet | operatör / koşu yüzeyi | Koşu kimliği. Koşu klasörü adıyla **aynı olması önerilmiştir**; teslim ve klasör sözleşmesi **K-17**'de açıktır — kaynak da bunu öneri statüsünde bırakır, bu sentezde kesinleştirilmemiştir |
| `sector_slug` | metin | evet | sektör | Sektör tablosuna FK olup olmayacağı **açık — K-08 (a)** |
| `kind` | metin | evet | koşu yüzeyi | `research` · `review` · `synthesis` — denetçi ve sentez çıktıları **aynı tabloda**; kaynakta gerekçesiyle onaylı karardır (ayrı tablo aynı kolonları kopyalardı) |
| `source` | metin | evet | koşu yüzeyi | Üreten araç veya rol. Kaynak sözleşmesi bugünkü koşu düzeninin araç kümesini sayar: araştırma için üç araç, denetim için iki denetçi rolü, sentez için tek rol. **Değerlerin kalıcı kayda yazılması bir açık karardır** — aşağıdaki nota bakınız |
| `brief_ref` | metin | hayır | koşu yüzeyi | Brief dosyası + sürüm/tarih referansı |
| `content_md` | metin | evet | araç / hakem | Ham Markdown; **değiştirilemez** |
| `created_at` | zaman damgası | evet | sistem | Oluşturulma anı |

Ek yapı — **üçü de kaynakta onaylı karardır**, bu sentezde denetlenmiştir:

- `(sector_slug, run_id)` üzerinde indeks.
- **Salt-ekleme tetikleyicisi:** `UPDATE` ve `DELETE` veri tabanı düzeyinde reddedilir; uygulama disiplinine bırakılmaz.
- **Embedding kolonu yoktur** — bilinçli; erişim deterministiktir.

> **Araç ↔ kaynak eşlemesinin kalıcı kaydı açık karardır.** Bir hakem belgesi `source` kolonunu kalıcı kayıt yaparak eşlemeyi veri tabanına yazar; diğeri eşlemenin **yalnız operatörde** kalmasını, koşu klasöründe tutulmamasını ister. İki konum **zorunlu olarak birbirini dışlamaz**: körlük gereksinimi denetçinin *bağlamına* ilişkindir, kalıcı kaydın kendisine değil. ⚠️ **İKİ AYRI KARARDIR ve Bölüm 17'de ayrı satırlar taşır:** *(a)* eşlemenin **kalıcı olarak kaydedilip kaydedilmeyeceği* — **K-138**; *(b)* **ham katmanın okuma yetkisi**, yani eşlemenin kimlere görünür olacağı — **K-139**. **Biri alınıp diğeri reddedilebilir:** eşleme kaydedilip erişim dar tutulabilir ya da tersi. Bu bölümde çözülmez. Denetçi bağımsızlığının kendisi ortak hükümdür (Bölüm 7.4).

#### Paket tablosu — `social.sector_packages` `[TASLAK]`

| Alan | Tip/biçim | Zorunlu mu? | Kaynak | Açıklama / kural |
|---|---|---|---|---|
| `id` | uuid PK | evet | sistem | Konvansiyon gereği uuid `[AKT·KAYNAK · 2026-07-11]` |
| `sector_id` | uuid FK → sektör tablosu | evet | taksonomi | **Alt sektör satırını** işaret eder |
| `version` | tam sayı | evet | koşu yüzeyi | Sektör içinde artan; `(sector_id, version)` benzersiz |
| `status` | metin | evet | süreç | `draft` · `active` · `archived`; varsayılan `draft` |
| `schema_version` | tam sayı | evet | sistem | Paketin **alan şemasının** sürümü — içerik sürümünden ayrıdır |
| `content` | JSONB | evet | sentez **veya** politika motoru (**K-22**) | Tek JSONB; alan şeması evrilebilir |
| `decision_log` | JSONB | evet | sentez **veya** politika motoru (**K-22**) | Varsayılan boş dizi; kalıp başına karar satırları (6.5) |
| `run_id` | metin | hayır | koşu yüzeyi | Ham artefaktlara bağ. ⚠️ **İki taslakta da zorunlu değildir**; bu hâliyle provenans bağı garanti edilmez. Alanın zorunlu kılınıp kılınmayacağı, sürüm oluşturmayan koşuların kaydı sorusuyla birlikte (6.4) **açıktır** — karar ID'si Bölüm 17 sweep'inde verilecektir |
| `created_at` | zaman damgası | evet | sistem | — |
| `activated_at` | zaman damgası | hayır | operatör | Yalnız aktive edilmiş sürümde dolu |

İki DB düzeyi garanti **ortaktır ve kaynakta onaylıdır**: `(sector_id, version)` benzersizliği ve **sektör başına tek `active`** (kısmi benzersiz indeks). Salt-ekleme tetikleyicisi bu tabloya **bilinçli olarak konmaz** — durum geçişleri meşru güncellemelerdir.

#### `content` alan şeması

Paketin içerik şeması, araştırma brief'inin çıktı sözleşmesiyle **aynı alan kümesidir**; hakem sentez sözleşmesi de aday paketi bu şemaya birebir üretmek zorundadır. Küme, brief'in yürürlükteki biçim sözleşmesinde **kapalıdır** (sekiz temel alan, adları yeniden adlandırılamaz) ve özel gün bloğu bunlara eklenir; **şemanın kendisinin değişmesi `schema_version` ile taşınır.**

| Alan | Tip | Boyut hedefi | Kural |
|---|---|---|---|
| `kapsam` | metin | ~200 karakter | Alt sektörün tanımı ve kapsadığı ürün/hizmet tipleri |
| `ton_ve_dil` | metin | ~300 karakter | Sektöre özgü güven/duygu unsurlarına bağlanır; genel-geçer sıfat yetmez |
| `cta_kaliplari` | dizi {kalıp, tür, gerekçe} | ~600 karakter | Kanal bağımlılığı etiketi **taşınır, silinmez** — çalışma zamanındaki marka-gerçeği filtresi bu etikete dayanır |
| `kanca_kaliplari` | dizi | ~400 karakter | Dağarcıktır, formül değil |
| `gorsel_kodlar` | metin (İngilizce) | ~500 karakter | Anahtar ifadeler; fiziksel çekim parametresi ve görsel içi metin öğesi yasak |
| `video_kodlar` | **iki alt yapı** (İngilizce) | ~300 karakter (ikisi toplam) | Hareket kodları ve sahne kodları **ayrı tutulur**; iki yüzeye gider. **Nihai alan adları K-02**'ye bağlıdır |
| `takvim_temalari` | dizi | ~400 karakter | Yıllık ritmin özeti; dönem ayrıntısı özel gün bloğundadır |
| `yasaklar_ve_hassasiyetler` | dizi | ~400 karakter | Mevzuat maddeleri **yürürlük tarihiyle** yazılır |
| `ozel_gun` | nesne {anahtar: {tür, mesaj ekseni, kanca, cta, görsel vurgu}} | dönem başına ~600 karakter | Anahtarlar **sistem takvimine karşı** doğrulanır; uydurma anahtar üretilmez. Ayrı tablo değildir — paket ve özel gün **atomik sürümlenir**. Sistemde karşılığı olmayan dönem **pakete girmez ve karar günlüğüne notlanır** (6.5). Anahtar sözleşmesi **K-01b**, kategori ↔ tür önceliği **K-03** |

**Toplam tavan:** `content` bütünü için ~6.000 karakter (≈2.000 token) hedefi; alan başı hedeflere **ek olarak** şemaya yazılır. Bu bir **tasarım hedefidir, ölçüm değildir**; kaynak sözleşmesinde de hedef olarak verilir.

> ⚠️ **İki rakam yan yana duruyor ve birbirini tutmuyor.** Aynı belgelerde paket için ~2.000 token'lık tavan ile ~1,2–1,5 bin token'lık maliyet tahmini birlikte geçer. **İkisi de ölçüm değildir**; hangisinin geçerli olduğu ölçülmemiştir. Paket ve marka DNA'sının **aynı bağlam bloğunu ve aynı token bütçesini** paylaştığı gerçeğiyle birlikte, toplam bütçe ölçümü **K-12**'ye bağlıdır (Bölüm 12). Bu sentezde tavan **kapı olarak kullanılmamıştır**.

Alan başına **asgari öğe sayıları** (en az kaç CTA, kanca, görsel/video ifadesi, dönem) araştırma brief'inin biçim sözleşmesinde tanımlıdır ve **mekanik eleme adımının** girdisidir; biçimsel doğrulama Bölüm 7.3'te ele alınır. Bunlar **ölçülmüş eşikler değil, sözleşme kurallarıdır**.

#### `decision_log` satır yapısı

Her satır bir kalıp kararıdır: **alan · kalıp · karar · gerekçe · kanıt**. Ayrıntı ve kanıt biçimi 6.5'tedir.

#### Mevcut tablolarda gereken değişiklikler

| Tablo / alan | Değişiklik | Not |
|---|---|---|
| `brands.sector_id` | **Değişmez** | Kök kova anlamı korunur |
| `brands.sub_sector_id` | **Yeni**, null olabilir FK | Dolu → paket yolu; boş → mevcut yol. ⚠️ Alanın **yalnız alt sektör satırlarını kabul etmesinin** veri tabanında mı uygulamada mı zorlanacağı **K-08 (b)'dir ve açıktır**; sektör tablosuna FK vermek tek başına bunu sağlamaz (kök satırlar da aynı tablodadır) |
| `brands.sector` (TEXT) | **Dokunulmaz** | Canlı taşıyıcı (6.1) |
| `posts` — paket sürüm ilişkisi | **Yeni** | Paketli üretim, kullanılan paket kimliği ve sürümüyle ilişkilendirilir. **Ayrı kolon mu mevcut bir JSONB alan içinde mi — K-07 açıktır.** Paket yolu dışındaki üretimde **geçerli bir paket ilişkisi bulunmaz**; ilişkinin kurulmaması, mevcut prompt parçalarının **byte-exact** değişmezliğinin veri tarafındaki karşılığıdır |

### 6.3 Kimlik ve referans bütünlüğü

- **Kimlik üretimi:** uuid; mevcut şema konvansiyonu budur `[AKT·KAYNAK · 2026-07-11]`. Kaynak taslaklarındaki `BIGSERIAL` uyarlanacaktır.
- **Benzersizlik kuralları:** paket tablosunda `(sector_id, version)`; ayrıca sektör başına tek `active` kısmi benzersiz indeksle. Özel gün anahtarları paket içinde doğal olarak benzersizdir (JSON nesnesi zorlar).
- **Foreign key / ilişki davranışı:** paket satırı alt sektör satırına, marka kaydı alt sektöre FK ile bağlanır. **K-08 iki ayrı açıklığı birlikte taşır ve ikisi de burada kapatılmaz:** (a) ham artefaktın sektöre bağının FK olarak mı serbest metin olarak mı kurulacağı — iki belge de bağın `sector_slug` ve `run_id` üzerinden kurulmasını **öneri** olarak verir, kesin FK ve adlandırmayı migration spec'ine bırakır; (b) `brands.sub_sector_id`'nin **yalnız alt sektör satırlarını kabul etmesinin** veri tabanında mı uygulama katmanında mı zorlanacağı. Kök ve alt satırlar aynı tabloda yaşadığı için (b) **FK ile kendiliğinden çözülmez**; kısıt yazılmazsa kök kova invariantı veri tarafından korunmaz.
- **Adlandırma uyarısı:** şemada `sector_reports` ve `sector_trend_cache` adlı tablolar hâlihazırda bulunmaktadır `[AKT·KAYNAK · 2026-07-11]`; yeni tablo adları bunlarla karışıklık yaratmamalıdır.

**Sürümler arasında kimlik sürekliliği — açık karar, bu bölümde kapatılmaz.** İki belge burada **karşıt konumdadır**:

- Bir hakem, liste niteliğindeki her öğenin sürümler arasında **sabit bir kalıp kimliği** taşımasını zorunlu sayar; metin hash'inin tek başına kimlik olamayacağını, küçük yazım değişikliğinin yeni kalıp yaratmaması gerektiğini söyler. Aynı belge kimliği, sabit alanları ve özel gün alt alanlarını kapsayan bir **karar birimi** kavramı kurar ve otomatik motorun tam kapsam kontrolünü buna dayandırır.
- Diğer hakem, kalıp düzeyinde **kalıcı kimlik öngörmez**; sürekliliği karar günlüğü üzerinden **metinsel eşleşmeyle** kurar ve kalıp kimliğini sonraki faza bırakır.

Bu ayrışmanın **doğrudan davranışsal sonucu** Bölüm 4'te kaydedilmiştir: geri-ekleme tespiti kalıp metnine dayandığı için **metni değişmiş bir kalıp çıkarılanlar listesiyle eşleşmeyebilir**; bu, kaynaklarda kabul edilmiş bir zayıflıktır. Kalıcı kimlik bu zayıflığı kapatır, ama **kalıp kimliği sözleşmesi açık karardır** (Bölüm 3.1). Bu bölümde taraf tutulmaz, yeni karar açılmaz.

> **Statü uyarısı `[SEA-2026-08-11]`:** sabit kalıp kimliği ve karar birimi kavramı **kaynak dokümanlardan gelmez** — belge bunu kendisi de not eder; bu sentezde dokuz kaynak dosya bu terimler ve eş anlamlıları için tarandı ve **karşılığı bulunamadı**. Sonraki ölçeklenebilirlik analizinden gelen bir gereksinimdir ve **yalnız bir hakem belgesinde** bulunur. Taze birincil kanıtla doğrulanmadığı için çözülmüş teknik karar sayılamaz.

### 6.4 Durum, sürüm ve zaman bilgisi

- **Durumlar:** `draft` → `active` → `archived`. Küme kaynakta bu üç değerle kapalıdır.
- **Sürümleme:** alt sektör içinde artan paket sürümü; içerik alan şemasının kendi sürümü ayrıdır (`schema_version`).
- **Zaman damgaları:** her satırda oluşturulma anı; aktivasyon anı yalnız aktive edilmiş sürümde.
- **Yazım sınırı:** koşu, veri tabanına **yalnız `draft`** yazar; `active`'e geçirme kararı ve işlemi operatöre aittir. `content` doğrulayıcısı **yazımdan önce** çalışır ve reddederse yazım olmaz (Bölüm 5.3). `draft` içeriğinin üreticisi **K-22**'ye bağlıdır.
- **Aktivasyon sırası veri tabanı tarafından zorlanır:** tek-aktif kısmi indeks nedeniyle **önce mevcut aktif sürüm arşivlenir, sonra yeni sürüm aktive edilir**. Yanlış sıra veriyi bozmaz, hata verir. Geri alma da aynı sırayı izler (Bölüm 8.3).
- **Eşzamanlılık / idempotency:** tek-aktif garantisi **DB seviyesindedir**, uygulama mantığına bırakılmaz. Ham katmanda idempotency'nin koşu kimliği + üreten kaynak + tür üçlüsüyle ele alınması önerilmiştir; **aynı koşunun iki kez yüklenmesinin engellenip engellenmeyeceği açıktır — K-09.** Aynı sorunun orkestrasyon tarafı (zaman aşımı, kısmi başarısızlık, yeniden koşunun yeni bir deneme kimliği üretmesi) yalnız bir belgede ayrıca açık madde olarak durur ve **K-09'un kapsamından geniştir**; bu sentezde birleştirilmemiştir, karar ID'si Bölüm 17 sweep'inde verilecektir.

> **Sürüm oluşturmayan koşuların kaydı — açık.** Bir hakem, çalışma zamanı içeriği ve şema aynıysa **yeni sürüm oluşturulmamasını** (`değişiklik yok`) ve bloklanan koşuların paket satırı üretmeden durumlandırılmasını ister; karşılaştırmayı **canonical içerik hash'ine** dayandırır. Bu bölüm iki sonucu da normatif şema hâline getirmez: `değişiklik yok` ve `bloklandı` koşularının **nerede kayıtlandığı** Bölüm 5.2'de görünür kılınan açık noktadır, kararı Bölüm 17'dedir. Aynı kaynak, ilk koşuda `değişiklik yok` sonucunun **geçersiz** sayılmasını da ister (veri veya süreç hatası göstergesi); bu hüküm de tek belgededir. `[SEA-2026-08-11]`

**Üretim sürüm damgası.** Paketli üretimde oluşan post, kullanılan paket kimliğini ve sürümünü taşımalıdır; gerekçe ortaktır ve kaynakta onaylıdır: kötü çıktı doğru sürüme bağlanabilsin, işlevsel kapı örnekleri eşleştirilebilsin, ileride etkileşim verisiyle paket kalitesi ilişkilendirilebilsin. **Fiziksel temsil K-07'de açıktır.** Damganın maliyetinin sıfıra yakın olduğu ve şimdi atlanırsa sonraki fazda telafisinin bulunmadığı **kaynak beyanıdır, ölçüm değildir** `[ÖLÇÜLMEMİŞ VARSAYIM]`; bu sentezde **öncelik veya bloklama gerekçesi yapılmamıştır**.

### 6.5 Karar ve denetim günlüğü

**Kaydedilecek kararlar.** Her kalıp için beş değerden biri: **koru · güncelle · çıkar · ekle · kırp**. Küme, hakem sentez sözleşmesinde bu beş değerle **kapalıdır** — bu yüzden reddedilen bir adayın karar izinde nasıl temsil edileceği ayrı bir açık karardır (Bölüm 4'ten devreden; altıncı bir değer seçilirse çıktı sözleşmesi revize edilir). Yalnız özel gün turu koşulduğunda taşınan temel paket alanları da **birer `koru` satırı** olarak yazılır — sessiz taşıma yoktur.

> ⚠️ **Kapalı enum ile sözleşmenin ikinci yazım yükümlülüğü arasında yapısal açıklık var.** Resmî sentez sözleşmesi, sistemde karşılığı bulunmayan bir dönemin **pakete alınmamasını ve karar günlüğüne notlanmasını** ister. Bu not bir kalıp kararı değildir: **beş değerli kapalı enum içinde onu temsil edecek bir değer yoktur** (`kirp` kırpılan öğe içindir, `cikar` aktif pakette bulunan öğe içindir). Aynı boşluk reddedilen aday temsilinde de görülür (Bölüm 4'ten devreden karar). İki gereklilik bugünkü sözleşmede aynı anda karşılanamaz; bu bölümde uzlaşma cümlesi üretilmemiş, **yapısal açıklık olarak Bölüm 17'ye taşınmıştır**. Çözüm bir altıncı değer, ayrı bir not alanı veya günlük dışı bir kayıt olabilir — üçü de **resmî sentez görev sözleşmesinin revizyonunu gerektirir**; dolayısıyla açıklık resmî hakem turunu doğrudan ilgilendirir (blok kapsamı Bölüm 17'de işaretlenir).

**Kararı veren aktör.** Denetçiler **karar vermez, önerir**; sentez karar merciidir; **aktivasyon operatöre** aittir. Motorun hatta bulunduğu modelde kararların uygulanması motora geçer, ancak motorun `active`'e dokunma yetkisi **yoktur** (**K-28**); fazı karara bağlandı — ✅ **K-22 KAPANDI — A** (2026-08-21, Ek B), motor **Faz 1'de** hattadır.

> **Aktörün kayda yazılması — iki granülerlik, tamamlayıcı.** Bir belge **karar satırı seviyesinde** kararı motorun mu insanın mı verdiğinin ayırt edilebilmesini ister; diğeri motor **sürümünün ve yapılandırmasının koşu seviyesinde** damgalanmasını ister. İkisi birbirini dışlamaz, birlikte alınabilir; hangisinin veya ikisinin birden benimseneceği Bölüm 17'dedir.

**Gerekçe ve kanıt referansı.** `gerekçe` serbest metindir; `kanit` standart biçimlidir: denetçi satır referansı, ham kaynak referansı veya doğrudan URL. Denetçi satır numarasının **satır kimliği** olduğu ve sonradan değiştirilemeyeceği **denetçi görev sözleşmesinde yazılıdır** ve bu sentezde kaynağa karşı denetlenmiştir — kanıt zincirinin bütünlüğü buna dayanır.

**`çıkar` kararında pozitif kanıt satırı zorunludur.** "Yeni araştırmada geçmiyor" tek başına çıkarma gerekçesi değildir; kanıt yoksa kalıp korunur. Bu, Bölüm 4.3'teki bilgi kaybı korumasının veri tarafındaki zorlamasıdır. **Kanıt yeterliliğinin eşiği ise tanımsızdır ve bu sentezde uydurulmamıştır** (Bölüm 4'ten devreden açık karar).

**Saklama ve değiştirilebilirlik.** Karar günlüğü paketin parçasıdır: paketle birlikte sürümlenir ve arşivlenir. Ham katman değiştirilemez (salt-ekleme tetikleyicisi). Yanlış bilgi düzeltmesi **silmeyle değil yeni sürümle** yapılır.

> **Politika değerlendirme kaydı — yalnız bir hakemde, yeri açık.** `[SEA-2026-08-11]` Bir belge, motorun her koşuda kalıcı ve sorgulanabilir bir değerlendirme kaydı üretmesini ister: koşu sonucu, aktif paketteki karar birimi sayısı ile kapsanan karar sayısı, eklenen/güncellenen/çıkarılan/kırpılan sayıları, değişim oranı, bloklama nedenleri ve aday ile aktif içeriğin hash'leri. Kaydın **nerede tutulacağı** (ham katmanda yeni bir tür mü, paket tablosunda bir alan mı, ayrı tablo mu) belgenin kendisinde de **açık bırakılmıştır**. Bu sentezde dokuz kaynak dosya tarandı; kaydın ve içerik hash'inin **kaynakta karşılığı bulunamadı**. Yeni artefakt ve yeni şema alanı yarattığı için çözülmüş teknik karar sayılamaz; Bölüm 17'ye taşınır, karar ID'si sweep'te verilecektir. **Motorun sayı ve oran eşikleri bu bölümde tanımlanmaz** — ölçülecek ve pilot kanıtından sonra belirlenecektir (**K-24**).

### 6.6 Veri saklama, gizlilik ve silme

> **Kaynak durumu — iki farklı katman, karıştırılmamalı.** Ancak **saklama ve silme davranışının çekirdeği kaynakta yazılıdır ve onaylı karardır:** ham katman "salt-ekleme; asla değişmez/silinmez" olarak tanımlanır ve bunu zorlayan veri tabanı tetikleyicisi onaylı üç karardan biridir. Kaynak taramasında bulunamayan şey **davranışın tamamı değil, üç boşluktur:** (1) saklama süresinin **değeri**, (2) anonimleştirme, (3) kapsamlı **erişim/yetkilendirme politikası**. Aşağıda birinci küme ortak ve kaynak destekli, ikinci küme tek hakem beyanı olarak ayrı ayrı işaretlenmiştir.

- **Veri sınıfı:** operasyonel içerik ve kamuya açık kaynaklardan derlenmiş araştırma. Kişisel veri içermediği beyan edilmiştir `[BU SENTEZDE DOĞRULANMADI]`. ⚠️ **Bu iddianın akıbeti taze doğrulamadır ve doğrulanmadan saklama, anonimleştirme ve erişim politikası uygulanamaz** — uygulanırsa risk kabulü örtük yapılmış olur. Doğrulama **spec yazımını bloklamaz**; gerçek veri yazımı ve aktivasyon öncesinde koşulması gerekir. Ham raporlarda gerçek firma adları geçebilir (örneğin mevzuat emsalleri); bunlar **ham katmanda kalır**. Marka adı bayrağı taşıyan hiçbir metnin pakete giremeyeceği kuralı ise **kaynakta yazılıdır** ve ortaktır.
- **Saklama süresi:** ham katman kalıcıdır (salt-ekleme). Paketler de kalıcıdır — arşiv güvencesi, çıkarılan bilginin geri getirilebilmesini gerektirir (Bölüm 4.3). **Bir saklama süresi politikası, iki hakem belgesinde ve dokuz kaynak dosyada arandı ve bulunamadı**; "sınırsız" bir varsayım olarak beyan edilmiştir `[VARSAYIM]`. Politikanın belirlenmesi bu bölümde kapatılmaz; kapsam kararı olarak Bölüm 17'ye taşınır. ⚠️ **TEK POLİTİKA DEĞİL, AYRI KARARLARDIR ve Bölüm 17'de ayrı satırlar taşır:** *ham araştırma katmanı* — **K-140**; *aktive edilmiş paket sürümleri* — **K-141**; *aktive edilmeden kalan taslaklar* — kural kaynağı **K-142**, süresi **K-143** (koşullu). **Bağımlılık zincirleri farklıdır:** ham katman **salt-ekleme tetikleyicisine**, paket sürümleri **arşiv güvencesine** dayanır ve arşiv güvencesi **hiç aktive edilmemiş taslağı kapsamaz**; süreleri ayrı seçilebilir. ⚠️ **Ham katman kararı, kaynakta onaylı olan "asla değişmez/silinmez" kararına bağımlıdır ve ondan bağımsız alınamaz:** sonlu bir saklama süresi seçilirse salt-ekleme tetikleyicisi ve kalıcılık kararı **yeniden açılmak zorunda kalır** — arşiv güvencesi (Bölüm 4.3) de aynı kararın üzerinde durur. Bağımlılık burada kayıt altına alınır; "süre gerekirse şema eklenir" biçiminde teknik bir yan etki olarak sunulamaz.
- **Silme veya anonimleştirme:** ham katmanda silme **teknik olarak engellidir** — ortak hüküm, kaynakta onaylı karar. Yanlış bilgi, silme yerine yeni sürümle düzeltilir. **Anonimleştirme** ihtiyacı, taranan belgelerin hiçbirinde ele alınmamıştır (aynı arama kapsamı) — boşluk olarak kaydedilir, bu sentezde politika üretilmez.
- **Erişim yetkisi — büyük ölçüde açık.** Kapanmış tek hüküm tüketim yönüdür: marka, atandığı alt sektörün paketini yalnız **üretim çıktısı üzerinden dolaylı olarak** tüketir; paket metninin son kullanıcıya doğrudan gösterilmesi kapsam dışıdır (Bölüm 3.2). Bunun dışındakiler açıktır: **paket içeriğinin API üzerinden okunabilirliği K-16**'dadır; **aktivasyon/geri alma işleminin yetkilendirme modeli** yalnız bir belgede açık madde olarak durur ve bu sentezde kapatılmamıştır; ham katmanın okuma yetkisi ile araç eşlemesinin kimlere görünür olacağı 6.2'deki erişim/yetkilendirme kararına bağlıdır. ⚠️ Yazma yetkisinin **operatör ve koşu yüzeyinde toplandığı** bu belgelerin ortak çalışma varsayımıdır `[VARSAYIM]`; **yetkilendirme modeli olarak kesinleşmiş değildir** ve normatif hüküm yapılmamıştır. `blocked` sonucun hiçbir yetki veya uç nokta üzerinden aktive edilememesini sağlayacak **sunucu tarafı zorlama** yalnız bir belgede istenir ve **K-28**'in uygulama ayağıdır.

### 6.7 İlişki şeması

```text
                     social.sectors
        ┌──────────────────────────────────────┐
        │ id · slug · ad                       │
        │ parent_sector_id ────────────────────┼──┐ (kendine FK)
        └──────────────────────────────────────┘  │
              ▲                    ▲              │
   kök satır  │                    │  alt sektör  │
              │                    │  satırı ─────┘
              │                    │
              │                    │ 1
   brands ────┘                    │
   ├─ sector_id      (kök kova — anlamı korunur)
   ├─ sub_sector_id  (YENİ, null olabilir) ──────┐
   └─ sector (TEXT)  (canlı taşıyıcı, dokunulmaz)│
                                                 │ N
                                    social.sector_packages
                                    ├─ sector_id (FK → alt sektör)
                                    ├─ version           ┐ (sector_id, version) benzersiz
                                    ├─ status            ┘ sektör başına TEK active
                                    ├─ schema_version
                                    ├─ content       (JSONB)
                                    ├─ decision_log  (JSONB)
                                    └─ run_id ──────────┐
                                                        │
   social.sector_research_artifacts ◄───────────────────┘
   ├─ run_id       (koşu kimliği)        [SALT-EKLEME — DB düzeyinde zorlanır]
   ├─ sector_slug  (FK kararı açık — K-08 (a))
   ├─ kind         (research · review · synthesis)
   └─ source       (üreten araç veya rol — kalıcı kayıt kararı açık)

   social.public_holidays ──(gün adı + kategori)──► content.ozel_gun anahtarları
                                                   (sistem takvimi = doğruluk kaynağı;
                                                    anahtar sözleşmesi K-01b)

   posts ──(paket sürüm ilişkisi — fiziksel temsil K-07)──► social.sector_packages
```

**Şemanın okunma sınırı:** yukarıdaki diyagram iki belgenin ilişki modelinin birleşimidir ve **kesinleşmiş migration sözleşmesi değildir**. Ham artefakt bağının FK olarak kurulup kurulmayacağı (**K-08 (a)**), post damgasının fiziksel temsili (**K-07**) ve motorun koşu kaydının yeri açık kararlardır; diyagram bunları **ilişki olarak gösterir, biçim olarak kesinleştirmez**.

---

## 7. Ana oluşturma / işleme hattı

[ZORUNLU]

Bu bölümün konusu **bilgi üretim zamanının tur akışıdır** (Bölüm 5.2/A); içerik üretim zamanı Bölüm 10'dadır.

**Hattın omurgası:** doldurulmuş brief → üç bağımsız araştırma → mekanik eleme → iki bağımsız denetim → alan bazlı sentez → yönetici onayı.

⚠️ **Politika motoru bu omurganın parçası değildir.** Sentez ile onay arasına yerleşen ayrı bir katmandır; hatta giriş fazı karara bağlandı — ✅ **K-22 KAPANDI — A** (2026-08-21, Ek B), motor **Faz 1'de** hattadır. Motorsuz modelde (K-22 kapanışıyla yürürlük dışı) aday paketi sentez üretir ve akış doğrudan biçim doğrulayıcısına geçer (Bölüm 5.2).

Hattın **üç sözleşmesi** vardır ve bu bölümün hükümlerinin bir kısmı doğrudan onlardan gelir: **brief şablonu · denetçi görev metni · sentez görev metni.** Aşağıda bu sözleşmelerin değiştirilmesini gerektiren noktalar ayrıca işaretlenmiştir.

### 7.1 Girdi ve brief

**Zorunlu girdi tek bir metindir: doldurulmuş araştırma brief'i.** Kanonik şablon kopyalanır, **yalnız sektör bloğu** doldurulur, kalan bölümler sabit kalır ve **üç araştırma aracının üçüne de aynı metin** verilir.

Sektör bloğunun alanları: sektör adı · kapsam (neyi kapsar / neyi kapsamaz) · tipik ürün/hizmetler (3–6 örnek) · bilinen hassasiyet ipuçları — *araştırmacıya başlangıç noktası, sınırlayıcı değil* · **koşu kapsamı**: `GÖREV A + GÖREV B` veya `yalnız GÖREV B`. Koşu kapsamı yalnız brief'in kapsamını değil, sentez adımının **koşu modunu** da belirler (Bölüm 7.5).

**Girdi sahibi:** sektör bloğunu **koşuyu koşan yönetici/operatör** doldurur (rolün ikiye bölünüp bölünmeyeceği açıktır — Bölüm 15). Denetim adımında brief, denetçi görevine **eki olarak komutça otomatik eklenir** ve ekleri koşu yüzeyi toplar (Bölüm 5.3); gerekçe insan hatasının kapatılmasıdır. ⚠️ Bu **hedef işletim davranışıdır, bugünkü sistem olgusu değildir**: ekleri toplayan komut ailesinin bugün var olup olmadığı **doğrulanmamıştır** ve komutun kendisi **K-27**'ye bağlıdır.

#### Brief'in iki görev bloğu

**GÖREV A — temel paket.** Sekiz alanı araştırır: `kapsam` · `ton_ve_dil` · `cta_kaliplari` · `kanca_kaliplari` · `gorsel_kodlar` · `video_kodlar` · `takvim_temalari` · `yasaklar_ve_hassasiyetler`. Küme brief'in biçim sözleşmesinde **kapalıdır** ve alan adları yeniden adlandırılamaz; paket içerik şemasıyla aynı alan kümesidir (Bölüm 6.2). `video_kodlar` sözleşmede **iki alt listeye ayrılmıştır** — hareket kodları ve sahne kodları; ikisi üretim hattında **farklı yüzeylere** gider (Bölüm 5.1), nihai alan adları **K-02**'ye bağlıdır.

**GÖREV B — özel gün kalıpları.** Üç adımlıdır:

1. **Dönem seçimi:** sözleşmedeki Türkiye aday takviminden sektör için ticari/iletişimsel anlamı olanlar **gerekçeli seçilir**, anlamı olmayanlar **gerekçeli elenir**; aday listede bulunmayan sektöre özgü dönemler (sezon, kültürel pratik, sektörel gün) **gerekçeli eklenebilir**. Aday takvim bir başlangıç listesidir, kapalı küme değildir.
2. **Tür etiketi:** her seçilen döneme **tek** etiket verilir. Küme dört değerle kapalıdır ve ASCII yazımı zorunludur: `kutlama` · `anma` · `ticari-firsat` · `karma`. Alan çalışma zamanında içerik türünü belirlediği için tek değerli olmak zorundadır; **kararsızlık hâlinde bile etiket tek seçilir ve tereddüt gerekçe metnine yazılır.**
3. **Dört başlık:** `mesaj_ekseni` (Türkçe) · `kanca` (Türkçe, köşeli parantezli değişkenlerle) · `cta` (Türkçe) · `gorsel_vurgu` (İngilizce).

**Tür etiketinin davranışsal karşılığı:** `kutlama` türünde satış çağrısı kültürel olarak eğreti kaçar, `cta` yerine **kutlama kalıbı** yazılır; `anma` türünde kutlama **ve** satış dilinin ikisi de uygunsuzdur — yalnız **saygı çerçevesi** yazılır **veya "içerik önerilmez" denir**; `ticari-firsat` satış odaklı iletişimi doğal karşılar; `karma` kutlama ile ölçülü ticariyi birlikte taşır. ⚠️ `anma` türündeki **"içerik önerilmez" dalı** ile mekanik eleme adımı arasındaki gerilim Bölüm 7.3'te açık karar olarak işaretlenmiştir.

**Alan başına asgari öğe sayıları** (kaç CTA, kanca, görsel/video ifadesi, dönem) sözleşmede tanımlıdır ve **mekanik eleme adımının girdisidir**; ölçülmüş eşikler değil sözleşme kurallarıdır ve bu belgede kabul kriteri yapılmaz. Sayılar ve kapı davranışı Bölüm 7.3'tedir.

#### Biçim ve kalite koşulları — brief'in mutlak kuralları

1. **Yalnız kaynakta desteklenen bilgi yazılır.** Kaynak bulunamayan başlığa "kaynak bulunamadı" yazılır ve **tahmin üretilmez**.
2. **Kalıp düzeyinde yazım.** Hiçbir markanın cümlesi aynen alınmaz; yapı köşeli parantezli değişkenlerle soyutlanır.
3. **Sosyal medya platformlarından içerik toplama/kopyalama yasaktır**; yalnız yayımlanmış analiz ve rehberlerden çalışılır. Marka postu kopyalamak ve kaynaksız tahmin üretmek de bu yasağın kapsamındadır.
4. **Kaynak önceliği:** Türkçe kaynaklar önce; yetersizse İngilizce kaynak kullanılır ama bulgu **Türkiye pazarına uyarlanarak** yazılır.
5. **Bağımlılık etiketleri eleme değil işaretlemedir.** `[kaynak-bağımlı]` (ünlü yüz, sponsorluk, fiziksel etkinlik/prodüksiyon, ajans operasyonu, özel yazılım) ve `[kanal-bağımlı: X]` (WhatsApp hattı, fiziksel mağaza, randevu sistemi, e-ticaret sitesi) taşıyan kalıp **yine yazılır**; uygunluk filtresi sonraki aşamaya aittir. Kanal etiketi pakete **taşınır, silinmez** — çalışma zamanındaki marka-gerçeği filtresi (**K-05**) doğrudan bu etikete dayanır (Bölüm 7.5).
6. **Önem sırası — brief katmanı:** (1) sektöre özgülük *(başka sektöre taşınsa sırıtır mı)* · (2) **kaynak sayısı ve gücü** · (3) Türkiye yerelliği. ⚠️ **Bu sıralama sentezin kırpma sıralaması değildir** — kırpma katmanında ikinci ölçüt **mutabakat gücüdür** (Bölüm 7.6). Tek bir araştırma koşusu üç aracın mutabakatını **göremez**; iki ölçüt farklı katmanlara aittir ve birbirinin yerine kullanılamaz.
7. **Alt sınırlar vardır, üst sınır yoktur.** Hiçbir başlığa oturmayan değerli gözlem atılmaz — brief'in **EK BULGULAR** bölümüne konur.
8. **Dil kuralı:** görsel/video alanları (GÖREV A alan 5–6) ve GÖREV B `gorsel_vurgu` **İngilizce** (görsel üretim modeline gider), diğer alanlar Türkçe.
9. **Görselde metin yasağı.** Kanonik biçimi ve **kapalı küme olmadığı** Bölüm 3.4'tedir. Denetim adımındaki karşılığı `[metin-öğesi]` bayrağıdır (Bölüm 7.4).
10. **Güncellik:** iddiaların kaynak yayın tarihi brief'in kaynak eşlemesi bölümünde belirtilir; 2–3 yıldan eski pazarlama/trend iddiaları `[eski-kaynak]` olarak işaretlenir; mevzuatta **en güncel düzenleme, yürürlük tarihiyle** esas alınır.
11. **Kaynak eşlemesi:** her alan ve dönem için **en az iki bağımsız kaynak hedeflenir**; URL'ler **açılabilir tam bağlantı** olmalıdır.
12. **Tek kaynaklı iddialar brief'in kaynak eşlemesinde "tek kaynak" olarak işaretlenir.** Bu işaret denetim adımının girdisidir: bir `tekil` iddianın "tekil-kaynaklı" mı "muhtemel-uydurma" mı sayılacağı buna bakar (Bölüm 7.4).
13. **Yüksek prodüksiyon değerli görsel/video estetik referansları serbesttir** — görseli yapay zeka ürettiği için prodüksiyon maliyeti kısıtı yoktur. Bu muafiyet `[kaynak-bağımlı]` etiketinin "fiziksel etkinlik/prodüksiyon" tanımını **görsel kodlar için sınırlar**.
14. **Hareket kodları kısa ve döngüye (loop) uygun yazılır** — kamera hareketi ve tempo düzeyinde.
15. **Sahne kodları görsel kodların tekrarı olamaz** — hareketli çekime uygun, videoya özgü sahne/atmosfer yazılır. İki alan aynı içerikle doldurulursa iki ayrı üretim yüzeyine aynı dağarcık gider.
16. **Araştırmanın kaynak tabanı herkese açık pazarlama literatürüdür** — sektörel rehberler, ajans yazıları, sektör yayınları, kampanya analizleri. Bu bir dışlama listesi değildir; mevzuat alanında güncel resmî düzenleme yürürlük tarihiyle esas alınır (md.10).
17. **Yazım kısa ve yoğun olur**; makale veya rapor formatına kayılmaz.

#### Brief'in çıktı biçimi

Çıktı **beş bölümle** sabitlenir: **A** GÖREV A paketi (sekiz alan, sırayla, alan adı başlık olarak) · **B** GÖREV B çıktısı (önce seçim/eleme/ekleme gerekçeleri tablosu, sonra dönem dönem dört başlık) · **C** kaynak eşlemesi (alan/dönem → iddia → kaynak) · **D** ek bulgular · **E** güven notu (en fazla beş madde; zayıf kaynaklı başlıklar, Türkiye-yereli olmayan uyarlamalar, emin olunmayan güncel mevzuat — dürüst öz-değerlendirme).

**Bölüm C ayrı bir görev değildir** — GÖREV A/B iddialarının kaynak eşlemesidir. **Bu beş bölüm dışında bölüm eklenmesi yasaktır** (TL;DR, yönetici özeti, giriş dâhil); mekanik eleme adımı bunu kontrol eder (Bölüm 7.3).

### 7.2 Bağımsız üretim / toplama adımları

**Üç bağımsız araştırma koşusu.** Aynı brief metni üç ayrı araştırma aracına verilir; koşular birbirinin çıktısını görmez. Araştırma adımı **elle işletilir ve sistemin dışındadır** (Bölüm 5.1); hattın geri kalanının otomatikleştirilmesi hedef modeldir, bu adımın elle kalması bilinçli bir tercihtir.

**Üçün gerekçesi mimarinin taşıyıcı nedenidir:** üç koşu **mutabakat sinyali** üretmek içindir — denetim adımının sınıflandırması (`3-3` / `2-3` / `tekil`) doğrudan buna dayanır ve tek kaynakla "muhtemel-uydurma" ayrımı yapılamaz.

> ⚠️ **Mutabakat sinyalinin sınırı ölçülmemiştir.** Bağımsızlık **araç düzeyindedir**; üç aracın aynı yayımlanmış kaynak havuzunu okuması ortak-mod hatasını dışlamaz. Bu sınır **ölçülmemiştir** ve bu belgede eşiğe veya kabul ölçütüne çevrilmemiştir. Aynı sınırın denetim katmanındaki karşılığı risk olarak kayıtlıdır (Bölüm 18).

**Kör adlandırma.** Çıktılar araç kimliğini gizleyecek biçimde `KAYNAK-1/2/3` olarak adlandırılır. Üç kural birlikte çalışır: **kör adlandırma dosya adında başlar** (araç adı dosyaya yazılmaz) · **gerçek eşleme yalnız operatörde kalır** · denetçilerin üslup veya biçim ipucundan **kimlik çıkarımı yapması yasaktır** (Bölüm 7.4). Amaç, denetim adımında **araç itibarının değerlendirmeyi kirletmesini** önlemektir.

Araç kimlikleri bu belgede adlarıyla sayılmaz; küme ham artefakt satırının kaynak alanı için önerilen değerlerdir (Bölüm 6.2). ⚠️ **Eşlemenin kalıcı kayda yazılıp yazılmayacağı açık karardır** (**K-138**) ve **kimlerin okuyabileceği ayrı bir açık karardır** (**K-139**). Kayıt ile körlük birbirini zorunlu olarak dışlamaz — körlük gereksinimi **denetçinin bağlamına** ilişkindir, kaydın kendisine değil; kalan soru bir **erişim ve yetkilendirme tasarımı** sorusudur (Bölüm 6.2).

#### Çıktıların saklanması — iki katman

**Dosya çalışma kopyasıdır, veri tabanı kalıcı kanıt katmanıdır.** Koşu başına tek klasör tutulur ve aynı içerik `run_id` altında ham artefakt tablosuna yazılır; tablo salt-eklemedir (Bölüm 6.2).

```text
research-runs/<run_id>/          (ör. <sektör>-<dönem>)
├── brief.md                     koşuda verilen brief kopyası
├── KAYNAK-1.md / -2.md / -3.md  kör adlandırılmış araç çıktıları
├── brief-doctor-raporu.md       mekanik eleme raporu
├── denetci-1-raporu.md          birinci denetçi çıktısı
├── denetci-2-raporu.md          ikinci denetçi çıktısı
└── birlesik-taslak.md           sentez çıktısı (aday JSON + karar günlüğü
                                 + açık sorular + onay özeti)
```

Klasördeki dosyalar aynı zamanda **denetim ve sentez görevlerinin ekleridir**: komut ailesi ekleri bu yoldan otomatik toplar; kör adlandırma dosya adında başladığı için araç kimliği ek toplama sırasında da açılmaz.

⚠️ **Klasör ve teslim sözleşmesi açık karardır — K-17.** Yukarıdaki yapı **öneri** statüsündedir; klasör adının `run_id` ile aynı olması da öneri düzeyindedir (Bölüm 6.2). ⚠️ **Klasörün dosya kümesi kapalı değildir:** motorlu modelde aynı klasöre koşunun **politika raporu** ve motorun **nihai adayı** da eklenir (Bölüm 14). Bunların klasörde yer alması motorun hattaki varlığına bağlıdır — motor **Faz 1'de** olduğundan (✅ **K-22 KAPANDI — A**, Ek B) ikisi de Faz 1 gündemindedir; ancak **kesin dosya ve veri tabanı yerleşimleri bundan ayrı ve kendi başına açık bir karardır** ve motorun kapanışına rağmen ayrıca kararlaştırılmalıdır. **Yerleşim açıklığı tek değil, ikidir; birleştirilemezler:**

- **(i) Politika sonucunun / koşu kaydının nerede tutulacağı** — ham katmanda yeni bir tür mü, paket tablosunda bir alan mı, ayrı bir değerlendirme tablosu mu (**K-95**, Bölüm 6.5).
- **(ii) Motor sentez kararını güvenli fallback ile değiştirdiğinde özgün sentezin, motorun nihai adayının ve gerekçeli diff'in ayrı saklanma biçimi — K-96.** İlkesi hüküm olarak yazılıdır — sentez raporunun özgün hâli korunur, motorun fallback ve ret kararları ayrı tutulur, motor nihai adayı yerinde değiştirmeden ayrı üretir (Bölüm 7.7) — **açık olan, bu ayrılığın saklama biçimidir.** Biçim kapanmazsa motorun bir sentez kararını ezmesi hâlinde sentezin ne dediği geri okunamaz hâle gelir; bu, karar izinin doğrudan kaybıdır.

#### Bugün elde bulunan ham çıktıların statüsü

Bugünkü `KAYNAK-1/2/3` çıktıları ve doldurulmuş brief örnekleri **güncel biçim sözleşmesinden önce** üretilmiştir: güncel sözleşmeyi taşımayan noktaları olabilir, **doğrudan aktif paket girdisi değildirler**, ham artefakt kaydı ve **mekanik eleme adımının test verisi** olarak saklanırlar — **silinmezler**.

**Yeniden üretim zamanlaması karardır (K-18), açık soru değildir:** brief'ler ve araştırma çıktıları **spec ve uygulama sonrasına, resmî hakem turundan hemen öncesine** ertelenmiştir ve o noktada **tek seferde** üretilecektir. ⚠️ Şart **spec'in kesinleşmesi değil, spec + uygulamanın tamamlanmasıdır**; "sözleşmeler donar donmaz" biçiminde daraltılamaz. Üç gerekçe: (1) spec seansı ve inceleme turları sözleşmeleri hâlâ değiştirebilir — araştırma koşuları sözleşmeler donduktan sonra tek sefer koşulur; koşuların hattın **en pahalı elle adımı** olduğu bir beyandır, **ölçülmemiştir**; (2) spec'in girdisi mimari ve koddur, içerik değildir — eski çıktılar "araçlar gerçekte nasıl dönüyor" biçim kanıtı olarak yeterlidir; (3) veriler paket aktivasyonuna en yakın anda en tazedir.

⚠️ **Bugünkü ham çıktıların üretildiği brief elde yoktur.** O brief şablonun **ilk sürümüydü** (özel gün bloğu eklenmeden önceki, yalnız temel paketli sürüm); mevcut çıktıların farklı bölüm düzeni bundandır ve **sözleşme ihlali değildir**. Elde bulunmadığı sürece denetim şu notla koşulur: **ilk sürüm brief elde olmadığı için v1 sözleşmesine biçim uyumu denetlenmez, yalnız içerik ve iddia doğruluğu denetlenir.** Bu istisna **bugünkü test girdisine** aittir; resmî turda brief koşuyla birlikte üretilir ve denetim görevine eki olarak otomatik eklenir (Bölüm 7.1).

**Tur dışı acil güncelleme ayrı bir mekanizma gerektirmez.** Periyodun dışında bir güncelleme gerektiğinde (örneğin mevzuat değişikliği) aynı hat ve aynı `draft → active` mekanizması her an koşulabilir. Periyodun kendisi 3 **veya** 6 ay olarak açıktır (**K-26**, Bölüm 14).

### 7.3 Biçimsel doğrulama

Hatta **iki deterministik biçim kapısı** vardır ve ikisi de LLM'siz çalışır: **(a) girdi kapısı** — üç araştırma çıktısı geldikten sonra, denetim adımından önce koşan `brief-doctor`; **(b) yazım kapısı** — aday paket veri tabanına yazılmadan önce koşan `content` doğrulayıcısı (Bölüm 5.3). Bu alt başlığın konusu birincisidir; ikincisinin kontrol kümesi ve sonuç tipleri Bölüm 7.7'de, boyut sayıları Bölüm 7.6'dadır.

**Mekanik iş dil modeline verilmez.** Kapının çıktısı **denetim görevinin ekidir**: elenen kaynak denetim dışıdır, notla geçen kaynağın notlarını denetçi dikkate alır.

#### Kontrol kümesi

⚠️ **Bu küme kapalı değildir ve sınırı kesinleşmemiştir.** Kümenin üst sınırını brief sözleşmesinin **mekanik olarak taranabilir** kuralları çizer — ama bu kuralların **hangilerinin betiğe gireceği madde madde sabitlenmemiştir**. **Kontrol kümesinin sözleşmede sabitlenmesi açık karardır — K-89.**

| Kontrol | Sözleşmedeki karşılığı | Not |
|---|---|---|
| Bölüm varlığı ve alan tamlığı | Beş bölümlü çıktı biçimi + sekiz temel alan (Bölüm 7.1) | Sözleşme dışı bölüm eklenmesi de burada yakalanır |
| **Adet alt sınırları** | `cta` ≥5 · `kanca` ≥3 · görsel kod ≥20 · video kodu ≥10 (5 hareket + 5 sahne) · dönem ≥6; özel gün bloğunda dönem başına `kanca` ≥2, `cta` ≥2, `gorsel_vurgu` ≥5 | **Ölçülmüş eşik değil, tasarım kararıdır**; bu belgede kabul kriterine çevrilmez |
| Dil kuralı | Görsel/video alanları ve özel gün görsel vurgusu İngilizce, diğerleri Türkçe | Bölüm 7.1 md.8 ile aynı kural |
| URL biçimi | `https://` ile başlayan açılabilir tam bağlantı; oturum-içi atıf kodu, dipnot numarası, alan adı kısaltması kabul edilmez | — |
| Tür etiketi | Küme dörtle kapalı, **tek değerli**, ASCII yazım | Bölüm 7.1'deki tür sözleşmesinin mekanik karşılığı |
| Özel gün gerekçe tablosunun varlığı | Seçim / eleme / ekleme gerekçeleri tablosu | — |
| **40+ kelime kesintisiz alıntı bloğu** | Kopya şüphesi — **elemez, not düşer** | Seviyesi **açıkça yazılı olan tek kontrol** |
| Biçim kuralları | Tam alan adı başlıkları · sözleşme dışı bölüm yok · her kalıp ayrı madde işareti (**adet sayımı bozulmasın**) · gövdede dipnot/atıf işareti yok · bağımlılık ve güncellik etiketlerinin varlığı | Mekanik kontrole dâhildir |
| Görsel/video/özel gün görsel vurgu alanlarında metin unsuru | ⚠️ Bugün **mekanik kapının değil, denetçinin kuralıdır** — karşılığı `[metin-öğesi]` bayrağıdır (Bölüm 7.4). Yasağın kapsadığı **üç yüzey**: temel paketin görsel ve video alanları **ve** özel gün `gorsel_vurgu` alanı | Anahtar sözcük düzeyinde taranabilir, ama mekanik katmanın kapsama oranı **ölçülmemiştir**; kapıya konulup konulmayacağı yukarıdaki kapsam kararına bağlıdır |

#### Hatalı girdinin davranışı — iki seviye

Kapı iki seviye üretir — **eleme** (kaynak denetim dışı kalır) ve **not** (kaynak denetime girer, denetçi notu dikkate alır). Sonuç tipleri: `geçti` · `notlu geçti` · `elendi`. Elenen kaynak varsa **denetçi sınıflandırmasını kalan kaynak sayısına uyarlar** (örneğin iki kaynakla `2-2`, `1-2`) ve bunu raporunun başında belirtir. Koşu kalan kaynaklarla **devam eder**; kısmi koşu ham artefakt katmanında doğal olarak temsil edilir (Bölüm 6.2).

⚠️ **Açık karar (K-88) — hangi kontrol eler, hangisi yalnız not düşer?** Sözleşme yalnız **bir** eşlemeyi yazar (40+ kelime alıntı → notlar); kalan kontrollerin hangi seviyeye düştüğü **tanımsızdır**. Buna bağlı iki davranış vardır: **(a)** denetim sınıflandırmasının paydası — `3-3` sınıfı ancak üç kaynak da denetime girerse üretilebilir, **(b)** URL örnekleminin satır sayısı (Bölüm 7.4).

⚠️ **Açık karar (K-127) — koşu en az kaç kaynakla devam edebilir?** Sözleşme elemenin *sonucunu* tarif eder ama **bir taban koymaz**. Tek kaynak kalırsa mutabakat sinyali ilkece üretilemez (Bölüm 7.2) ve denetim `tekil` sınıfından başka bir şey üretemez. Bu, eleme seviyesi kararından **ayrı bir karardır**: biri kapının şiddetini, bu ise koşunun geçerlilik tabanını belirler; **kalite/risk kabulü** boyutu taşır.

⚠️ **Açık karar (K-120) — `anma` türünün "içerik önerilmez" dalı ile `cta` alt sınırı arasındaki gerilim.** Aynı sözleşme iki şeyi birden ister: dönem başına en az iki `cta` kalıbı (kutlama ve anma türünde kutlama-saygı kalıbı olarak) **ve** anma türünde "yalnız saygı çerçevesi yaz **veya** 'içerik önerilmez' de" seçeneği. İkinci dal seçildiğinde alan boş kalır ve mekanik kapı, **sözleşmenin izin verdiği bir çıktıyı eksik alan sayar**. Gerilim yalnız bu dala özgüdür: `kutlama` türünde alan kutlama kalıbıyla dolduğu için doğmaz. Kapının bugünkü tarifiyle davranışı belirsizdir. Karar, muafiyet · boş alanın ayrı temsili · dalın sözleşmeden kaldırılması seçenekleri arasındadır ve **brief sözleşmesinin sonraki sürümünü doğrudan ilgilendirir**.

### 7.4 Kalite denetimi / hakemlik

#### Denetleyen aktörler

**İki denetçi aynı görev metnini, aynı ekleri ve aynı koşu tarihini alır; ayrı oturumlarda, birbirinin çıktısını görmeden çalışır.** Kaynaklar kör adlandırılmıştır (Bölüm 7.2). **Denetçiler karar mercii değildir** — iddiaları sınıflandırır, bayraklar ve öneri sunarlar; nihai kararlar sentez adımına ve yöneticiye aittir. Sözleşme iki denetçiyi **araçlarıyla** bağlar: birinci denetçi Claude Code, ikinci denetçi Codex ortamında koşar. Bu bağ, web erişimi sorusunun (**K-14**) niçin yalnız ikinci denetçiyi ilgilendirdiğini de açıklar.

⚠️ **Denetimi başlatan orkestrasyon hedef işletim modelidir, bugünkü sistem olgusu değildir.** Koşunun tek bir komut ailesiyle yönetilmesi öngörülür; **gerçek komutun, bir aracın diğerini çağırma yönteminin ve bağlantı sözleşmesinin bugün mevcut olup olmadığı doğrulanmamıştır; hiçbiri uygulanmış kabul edilmez.** Yüzeyin kendisi karara bağlandı: ✅ **K-27 KAPANDI — A** (2026-08-21, Ek B) — Claude Code komut ailesi (Bölüm 3.3); varlık doğrulaması yukarıdaki uyarıyla birlikte spec seansına düşer.

#### Koşturma akışı — hedef model

1. Yönetici, araştırma koşusunun kimliğini vererek koşu yüzeyini başlatır.
2. Koşu yüzeyi ilgili koşu klasöründen **aynı girdi anlık görüntüsünü** toplar: brief kopyası, kör adlandırılmış üç araştırma çıktısı ve mekanik eleme raporu. *(Periyodik güncellemede aktif paketin karar birimi envanterinin de aynı anlık görüntüyle verilmesi bu bölümün sonundaki bağlı karar kümesine bağlıdır.)*
3. Aynı denetçi görev metni, aynı koşu tarihi ve aynı ekler **iki ayrı oturuma** verilir; bir denetçinin bağlamına diğerinin raporu eklenmez.
4. İki denetim birbirinden bağımsız tamamlanır. **Paralel mi sıralı mı yürütüleceği sonuç sözleşmesini değiştirmez**; yürütme tercihi **K-78**'de, oturum izolasyonunun ve aynı anlık görüntünün **teknik garantisi** **K-79**'da açıktır (Bölüm 3.3).
5. Her denetçi zorunlu dört bölümlü çıktısını **ayrı dosyaya** yazar.
6. Koşu yüzeyi çıktı biçimini doğrular. İki geçerli rapor hazır olmadan sentez adımına geçilmemesi **hedeflenir**; biçim kontrolünün otomatikleştirilmesi (**K-81**), tek geçerli raporla sentezin engellenip engellenmeyeceği (**K-150**), zaman aşımı ve kısmi başarısızlık davranışı (**K-82**) ve yeniden koşumun üreteceği kimlik (**K-83**) **açık kararlardır** (aşağıda).

#### Bağımsızlık garantileri

Bunlar **mimari bağımsızlık gereksinimleridir**; oturum izolasyonunun ve aynı girdi anlık görüntüsünün teknik olarak garanti edilip edilmeyeceği **K-79**'da açıktır (Bölüm 3.3).

- İki denetçi **aynı** brief'i, aynı kaynak dosyaları, aynı eleme raporunu ve aynı koşu tarihini görür.
- Denetçiler birbirlerinin ara mesajlarını, raporlarını veya önerilerini **görmez**.
- Kaynak dosyaların hangi araştırma aracına ait olduğu **açıklanmaz**; gerçek eşleme yalnız yöneticide kalır.
- Denetçiler dosya üslubundan **araç/model kimliği tahmin etmeye çalışmaz** — açık yasaktır.
- URL örneklem kontrollerini **birbirinden bağımsız** yaparlar; web erişimi yoksa doğrulama yapmış gibi sonuç yazmazlar.
- İki rapor **ayrı dosya ve ayrı artefakt** olarak saklanır; sentez öncesinde birleştirilmez ve bir rapor diğerine tamamlattırılmaz.

Körlüğün gerekçesi: iki denetçinin mutabakatı bir kalite sinyalidir, kaynak kimliği bilinirse **araç itibarı değerlendirmeyi kirletir**. Körlüğün **ortak-mod hatasını azaltması** beklenen bir etkidir, **ölçülmemiştir**; iki denetçinin aynı yanlışı birlikte yapabilmesi risk olarak kayıtlıdır (Bölüm 18).

⚠️ **Körlük araştırma araçlarının kimliğine ilişkindir, hakem rolüne değil.** İki denetçi raporu ham artefakt katmanına **ayrı satırlar** olarak, denetim türü ve hakem rolü kaynak değeriyle yazılır (Bölüm 6.2); bu satırlar kör değildir ve olmaları da beklenmez. Salt-ekleme kuralı gereği raporlar sonradan güncellenmez veya silinmez.

#### Denetim ölçütleri

**Birinci adım — URL örneklem doğrulaması.** Her kaynaktan, **paket kararını değiştirebilecek** üç yüksek etkili iddia seçilir; gösterilen URL **gerçekten açılır** ve iddianın kaynakta geçip geçmediği kontrol edilir. Sonuç üç değerden biridir — `DOĞRULANDI` · `KAYNAKTA YOK` · `URL AÇILMADI` — ve tek cümle not taşır. Mevzuat, tarih ve sayı içeren iddialar örnekleme **öncelikle** alınır. **Web erişimi yoksa getirme denenmez**; bölüm "yapılamadı (ortam kısıtı)" olarak doldurulur ve kısıt kaynak profilinde de belirtilir — **doğrulama yapmış gibi sonuç yazmak yasaktır.**

⚠️ **"Dokuz satır" koşulludur.** Üç kaynak da denetime girdiğinde örneklem 3 × 3 = dokuz olur; **eleme varsa örneklem yalnız kalan kaynaklardan seçilir** ve satır sayısı düşer. Sözleşmenin çıktı bölümü ise satır sayısını **sabit dokuz** olarak yazar. Bu **sözleşme-içi bir tutarsızlıktır**, yeni karar açmaz — sözleşmenin sonraki sürümünde giderilecek bir düzeltme kalemidir.

**İkinci adım — iddia düzeyinde denetim.** Her alanın (ve her özel gün döneminin) içeriği iddia/kalıp düzeyine ayrılır; **eş anlamlı ifadeler aynı iddia sayılır** ("makro çekim" = "macro shot"). Sınıflar: `3-3` (üç kaynakta da var — en yüksek güven) · `2-3` · `tekil` · `çelişki`. `çelişki` sınıfında iki taraf da yazılır ve **kaynağı veya gerekçesi güçlü olan** belirtilir.

⚠️ **`tekil` iddianın akıbeti tek bir ölçüte bağlıdır ve o ölçüt tanımsızdır.** Tekil bir iddianın "tekil-kaynaklı" mı **"muhtemel-uydurma"** mı sayılacağı, brief'in kaynak eşlemesinde **güçlü kaynak** bulunup bulunmamasına bağlanır. Girdi tarafında eksik yoktur: tek kaynaklı iddiaların işaretlenmesi zorunludur (Bölüm 7.1 md.12). Açık olan tek şey ölçüttür: **"güçlü kaynak" sınıfının ölçütleri** (resmî/birincil kaynak önceliği, bağımsız kaynak sayısı, güncellik, yerellik ağırlığı) **tanımlı değildir** ve açık karardır — **K-123**. Ayrımın sonucu doğrudan ekleme eşiğine girer (Bölüm 7.5) — "muhtemel-uydurma" notu almış iddia tekil istisnadan yararlanamaz.

**Bayraklar.** Sekiz bayrak vardır ve küme **kapalıdır**. Üç bayrakta, araştırmacı etiketlememişse **denetçinin kendisi ekler**.

| Bayrak | Anlamı |
|---|---|
| `[kaynak-bağımlı]` | Ünlü yüz, sponsorluk, fiziksel etkinlik/prodüksiyon, ajans operasyonu veya özel yazılım gerektirir. **Denetçi ekler** |
| `[genel-geçer]` | Çapraz sektör testi: başka bir sektörün paketine konsa sırıtmıyorsa işaretlenir — paketin varlık nedeni sektörler arası ayrışmadır |
| `[yerel-değil]` | Türkiye pazarına özgü olması gereken yerde çeviri kokan genel batı pazarı bilgisi; takvim ve yasaklar alanlarında özellikle |
| `[kopya-şüphesi]` | Soyut kalıp değil, marka cümlesi görünümü |
| `[marka-adı]` | Gerçek marka/firma adı içeriyor — pakete giremez, emsal olarak ham katmanda kalır |
| `[kanal-bağımlı: X]` | Kalıp markadan belirli bir kanal/altyapı bekliyor. **Denetçi ekler.** Etiket pakete taşınır ve çalışma zamanı marka-gerçeği filtresinin dayanağıdır (**K-05**, Bölüm 7.1) |
| `[eski-kaynak]` | Pazarlama/trend iddiasının kaynağı 2–3 yıldan eski; **koşu tarihine göre** değerlendirilir. **Denetçi ekler** |
| `[metin-öğesi]` | **Görsel, video veya özel gün görsel vurgu** kodu yazı/metin/logo/etiket/filigran içeren öğe öneriyor — üretim hattı görselde metni yasaklar; yasak bu **üç yüzeyi birlikte** kapsar (Bölüm 3.4, Bölüm 7.1). Uyarlama veya eleme kararı **senteze aittir** |

**Öneri.** Her satır için dört değerden biri ve tek cümle gerekçe: `al` · `uyarla` · `alma` · `açık-soru`. Bu bir öneridir, karar değildir; karar tipleriyle karıştırılmaz (Bölüm 7.5).

**Üçüncü adım — özel gün bloğunun özel denetimi.** Dönem seçim ve eleme gerekçeleri makul mü · bariz eksik dönem var mı · aday listesi dışından eklenen dönemlerin gerekçesi ve kaynağı yeterli mi · tür etiketleri tanımlara uygun mu (uygunsuzluk **etiket değişikliği önerisi** olarak işaretlenir) · **kutlama ve anma türüne satış çağrısı sızmış mı**.

#### Web erişimi ve K-14'ün kapsamı

**K-14'ün üç ayağından ikisi yürürlükteki sözleşmelerde zaten karşılanmıştır:**

- **Bildirim yükümlülüğü** — denetçinin web erişimi yoksa bunu raporunda ve kaynak profilinde açıkça belirtmesi **yazılıdır**.
- **Kanıt ağırlığı kuralı** — bir denetçi ortam kısıtıyla getirme yapamamışsa diğerinin doğrulaması **normal kanıt sayılır**; ikisi de yapamamışsa mevzuat/tarih/sayı iddiaları "doğrulanmamış" işaretlenir ve paket kararını değiştirebilecek olanlar açık soruya düşürülür.
- **Açık kalan ayak:** ikinci denetçinin ortamında web erişiminin **bulunup bulunmadığı** (ölçülecek) ve **koşu öncesi ön kontrol** (preflight) adımı. **K-14 bu kapsamla açıktır.**

#### Çıktı sözleşmesi

Denetçi çıktısı **dört bölümdür** ve küme **kapalıdır** — serbest metin rapor yazılması ve dört bölümün dışına çıkılması yasaktır.

1. **Denetim tablosu** — markdown tablo; sütunlar: `no` · alan · iddia özeti (en fazla 15 kelime) · kaynaklar · sınıf · bayraklar · öneri · gerekçe (tek cümle). `no` artan tam sayıdır ve **satır kimliğidir**: sentez kararları bu numaraya referans verir ve numaralandırma sonradan değiştirilemez — **kanıt zincirinin bütünlüğü buna dayanır** (Bölüm 6.5). Özel gün satırlarında alan adı `ozel_gun/{dönem}/{başlık}` biçimindedir.
2. **URL örneklem sonucu** — iddia · kaynak · sonuç · not. Satır sayısı için yukarıdaki koşullu ölçüme bakınız.
3. **Kaynak profili** — kaynak başına 2–3 cümle: kaynak gösterme disiplini, yerellik, özgüllük, iç tutarlılık; **kimlik tahmini yapmadan**.
4. **Açık soru önerileri** — insan kararı gerektirdiği düşünülenler, en fazla beş.

#### Denetim katmanının açık kararları

| Açıklık | Buna bağlı davranış |
|---|---|
| Bir aracın diğerinin denetimini hangi **bağlantı yöntemiyle** (**K-76**) ve hangi **kimlik doğrulama/yetki modeliyle** (**K-77**) başlatacağı | Koşturma akışının 1. ve 3. adımı; yüzey kararıyla (**K-27**) birlikte değerlendirilmelidir |
| Denetçi model/sürüm bilgisinin, görev metni sürümünün, koşu tarihinin ve girdi hash'lerinin **tekrar üretilebilirlik damgası** olarak zorunlu olup olmayacağı (**K-80**) | Bir denetim sonucunun sonradan yeniden üretilebilmesi; bugün ham artefakt satırı yalnız koşu ve brief bağını taşır (Bölüm 6.2). ⚠️ Bu, paket sürüm damgasından (**K-07**) farklıdır |
| Zaman aşımı ve kısmi başarısızlıkta ne yapılacağı (**K-82**) ve yeniden koşumun **dosyayı ezmek yerine hangi deneme kimliğini üreteceği** (**K-83**) | Koşturma akışının 6. adımı; teslim ve klasör sözleşmesiyle (**K-17**) bağlıdır. ⚠️ Ham katman idempotency kararından (**K-09**) **ayrıdır** ve birleştirilmez: K-09 ham katmanda aynı koşunun iki kez yüklenmesini sorar, bu satır orkestrasyon düzeyinde yeniden koşumun kimliğini sorar (Bölüm 6.5) |
| Denetçi çıktısının dört bölüm ve tablo şemasına **otomatik uygunluk kontrolü** (**K-81**); tek geçerli raporla sentezin engellenip engellenmeyeceği (**K-150**) | Koşturma akışının 6. adımı. Sözleşme biçimi tanımlar, **kontrolü tanımlamaz** |
| Orkestrasyon günlüklerinde **gizli bilgi/kimlik bilgisi saklanmaması** (**K-136**) **ve** araç–kaynak eşlemesinin kör denetçi bağlamına **sızmaması** (**K-137**) | Bağımsızlık garantilerinin teknik ayağı. ⚠️ **İKİ AYRI KARARDIR:** kimlik bilgisi hijyeni ile körlük bütünlüğü **farklı şeyleri korur** ve biri alınıp diğeri reddedilebilir. Eşlemenin **kalıcı kaydı** (**K-138**) ve **okuma yetkisi** (**K-139**) Bölüm 7.2'dedir |

#### Aktif paketin yeniden doğrulanması — bağlı karar kümesi

**Bugünkü sözleşme hattı:** denetçiler **yalnız yeni araştırma çıktılarını** denetler; aktif paket denetim adımına **hiç girmez** — pakete ilk kez sentez adımında bakılır, çünkü aktif paket **sentez** görev sözleşmesinin girdisidir.

Önerilen **ek görev:** her periyodik koşuda iki denetçi, yeni araştırma denetiminden sonra **aynı aktif paket anlık görüntüsündeki bütün karar birimlerini** ayrıca tarar ve her birim için beş statüden birini üretir:

| Statü | Anlamı |
|---|---|
| `supported` | Yeni kanıt öğeyi **destekliyor** |
| `not_observed` | Yeni araştırmada **geçmiyor** — ⚠️ *geçersizlik kanıtı değildir* |
| `needs_update` | Yeni kanıt öğenin **içeriğini veya tarihini** değiştirmeyi gerektiriyor |
| `contradicted` | **Pozitif kanıt** öğeyle çelişiyor |
| `risk_unverified` | **Mevzuat/güvenlik iddiası** güncel kanıtla doğrulanamadı |

Her satır karar birimi anahtarı, denetçi statüsü, kanıt referansı ve tek cümle gerekçe taşır. Bu tablo **mevcut dört bölümlü çıktı sözleşmesine dâhil değildir**; uygulanmadan önce denetçi görev sözleşmesinin yeni bir sürümünde tanımlanmalıdır.

⚠️ **Bu tek başına karara bağlanamaz — bağlı bir karar kümesidir.** Ek görev, motor katmanındaki **iki denetçi mutabakatı kapısının** girdisidir: kapı benimsenir ve ek görev alınmazsa kapı **girdisiz kalır ve fiilen çalışmaz**; ek görev alınır ve kapı benimsenmezse iki denetçiye **ölçülmemiş bir iş yükü** eklenmiş olur. Kümenin iki satırı — kapının benimsenip benimsenmeyeceği (**K-125**) ve benimsenirse envanterin sözleşmeye hangi ek adı ve şemasıyla ekleneceği (**K-100**) — Bölüm 4'ün kararlarında kayıtlıdır. **Motor tarafındaki kontrol kuralları Bölüm 7.7'de bu kümeye bağlanır, orada yeniden açılmaz.**

Üç bağımlılık kayıt altındadır:

- Kümenin gerekçesi **motorun fazına bağlıdır** — motor **Faz 1'de** olduğundan (✅ **K-22 KAPANDI — A**, Ek B) kapı sorusu Faz 1 gündemindedir (motorsuz fazda kapı da olmazdı). Ek görev ise her turda iki denetçiye yük ekler.
- Ek görev **karar birimi** kavramına dayanır; **kalıcı kalıp kimliği açık karardır** (**K-84**; biçimi **K-151**, üretim yöntemi **K-152**; Bölüm 6.3). Kimlik sözleşmesi kapanmadan "aynı birimi" turlar arasında güvenilir biçimde izlemek mümkün olmaz.
- Ek görevin iş yükü (aktif paketin bütün birimleri × iki denetçi × her tur) **ölçülmemiştir**; bu belgede eşiğe, kabul ölçütüne veya iptal gerekçesine çevrilmez.

#### Uyuşmazlık çözümü

**Denetim katmanında çözülmez.** İki rapor sentez öncesinde birleştirilmez; uyuşmazlık **sentez adımının** işidir: aynı sınıf + uyumlu öneri → otomatik kabul havuzu; farklı sınıf veya öneri → **uyuşmazlık listesi**, iki gerekçesiyle birlikte. **Bir denetçinin görüp diğerinin hiç anmadığı iddia otomatik açık soru değildir** — önce ham kaynağa bakılır; iddia gerçekten varsa gerekçesi yazılarak kabul havuzuna alınabilir, ham kaynakta yoksa açık soruya düşer. Ayrıntı ve karar tipleri Bölüm 7.5'tedir.

### 7.5 Birleştirme / sentez

Sentez adımı iki denetçi tablosunu **aynı alandaki iddialar üzerinden hizalar** ve aktif pakete karşı evrimsel kararları üretir. Kararların anlamı ve uygulanma koşulları Bölüm 4.3'te tanımlıdır; bu bölüm o kuralların **denetçi çıktıları üzerinde nasıl uygulandığını** yazar.

**Girdiler:** brief · iki denetçi raporu · **varsa aktif paket** · son turların çıkarma kararları · sistemin güncel özel gün adları ve kategorileri · yalnız gerektiğinde ilgili ham kaynak kesiti. Son kalem bir bağlam disiplini kuralıdır: ham kaynak **bütün hâlinde** bağlama alınmaz.

⚠️ **Yedinci girdi: kök sektör rehberi.** Damıtma adımının kök rehberi de girdi alması onaylı bir karardır; gerekçesi kök rehberdeki nüansların pakete geçerken kaybolmamasıdır (Bölüm 5.3). **Sentez görev sözleşmesinin girdi listesi bu kalemi bugün taşımaz** ve sözleşmeye eklenmelidir; **eklenene kadar resmî hakem turu bu nedenle bloklanır.** Yeni karar açmaz.

#### Birleştirme birimi ve bağlam disiplini

**Birleştirme birimi alandır** — sekiz temel alan ve **her özel gün dönemi tek tek** işlenir. Her adımda bağlamda yalnız o alanın iki denetçi tablosu, gerektiğinde o alana ait ham kaynak kesiti bulunur. **Serbest metin birleştirme yoktur:** her karar iki denetçi satırına veya uyuşmazlık listesine izlenebilir olmalıdır.

Gerekçe tasarımın taşıyıcı nedenidir: **uzun bağlamda kaçırma riski.** Alan bazlı ilerleme bu riske karşı iki düzeltmeden biridir; diğeri denetçi çıktısının yapılandırılmış tablo olmasıdır (Bölüm 7.4). ⚠️ Kaçırma riskinin büyüklüğü ve düzeltmenin etkisi **ölçülmemiştir**; bu belgede kabul ölçütüne çevrilmez.

#### Koşu modları — önce belirlenir

Mod, brief'in koşu kapsamı alanından türetilir (Bölüm 7.1) ve sentezin hangi kararları üretebileceğini belirler.

| Mod | Sentezin davranışı |
|---|---|
| **`GÖREV A + GÖREV B`** (tam koşu) | Sekiz temel alan ve özel gün dönemleri birlikte işlenir |
| **`yalnız GÖREV B`** | Sekiz temel alan aktif paketten **aynen taşınır**; her biri alan başına `koru` kararı ve *"B-only koşu"* gerekçesiyle günlüğe yazılır. Hizalama ve evrimsel karar adımları **yalnız özel gün dönemleri için** koşulur |
| **İlk paket** (aktif paket yok) | `koru` / `guncelle` / `cikar` uygulanmaz — bütün kararlar **`ekle` evrenindedir**; çıkarılanlar listesi de doğal olarak boştur |

#### Karar akışı

**Aynı iddia iki denetçide uyumlu sınıf ve öneri taşıyorsa kabul havuzuna**, uyumsuzsa **uyuşmazlık listesine** gider. **Yalnız bir denetçinin gördüğü iddia otomatik açık soru değildir** — ham kaynakta gerçekten varsa kabul havuzuna alınabilir, yoksa açık soruya düşer (Bölüm 7.4). Kabul havuzundaki her öğe ile aktif paketteki her kalıp, Bölüm 4.3'ün beş kararından biriyle sonuçlandırılır; ardından **boyut kontrolü** koşar (Bölüm 7.6) ve aday paket üretilir.

#### Çelişki çözme kuralları — bayrak tüketimi

Denetim bayraklarının pakete geçişte ne anlama geldiği **sentez görev sözleşmesinde** tanımlıdır. Sekiz bayraktan **yedisinin** pakete geçiş davranışı tanımlıdır:

| Bayrak | Pakete geçişte |
|---|---|
| `[genel-geçer]` | **Ana kalıp olarak giremez**; yalnız sektöre bağlanmış hâliyle yeniden yazılırsa girebilir |
| `[marka-adı]` | İçeren hiçbir metin **giremez**; emsal/kanıt olarak ham katmanda kalır |
| `[metin-öğesi]` | Görsel/video/özel gün görsel vurgu kodu **giremez**; metin öğesi çıkarılarak **uyarlanabilir** |
| `[kanal-bağımlı: X]` | **Etiketiyle birlikte taşınır, etiket silinmez** — çalışma zamanı marka-gerçeği filtresi (**K-05**) buna dayanır. Kalıp kanal-nötr hâle getirilirse etiket kalkar |
| `[eski-kaynak]` | `ekle` eşiğinde **dezavantajlıdır**: taze kaynak yoksa tekil iddia gibi işlenir, mutabakat eşiğini tek başına geçemez |
| `[kaynak-bağımlı]` | Gir / uyarla / ele kararı **gerekçelendirilir**; uyarlanıyorsa uyarlanmış hâlini sentez yazar |
| `[yerel-değil]` | Tekil istisnayı kapatır (Bölüm 4.3) |

⚠️ **`[kopya-şüphesi]` için bayrağa özgü tüketim satırı yoktur — ama davranış sınırı üst kuraldan bellidir.** Brief sözleşmesinin mutlak kuralları arasında *"hiçbir markanın cümlesi aynen alınmaz; yapı köşeli parantezli değişkenlerle soyutlanır"* zaten yazılıdır (Bölüm 7.1 md.2). Bayrağın işaretlediği şey tam olarak bu kuralın ihlal edilmiş olabileceğidir; yürürlükteki hüküm bellidir — **kalıp değişmeden pakete giremez, ancak soyutlanarak uyarlanabilir.** Düşen şey hükmün kendisi değil, **sentez çıktı sözleşmesindeki karşılığıdır**: kural bayrak bazlı bir satır olarak yazılmadığı için işaretli kalıp normal `ekle` yolundan geçebilir. Bu bir **sözleşme düzeltmesidir**; yeni karar açmaz.

İki kural daha aynı katmanda çalışır: **URL kanıt ağırlığı** (Bölüm 7.4) ve **paket tür etiketi ile sistem kategorisinin çeliştiği durum**. ⚠️ İkincisinde **K-03 kapandığı için** sentez artık politikayı uygular — **paketin tür etiketi üstündür** ve çatışma karar günlüğüne yazılır (Bölüm 11.2). ⚠️ **Sentez görev sözleşmesinin metni bu kararı henüz yansıtmamaktadır** (hâlâ "kararı verme, açık soruya düşür" der); düzeltme **sürümlü supersession** olarak Bölüm 14.4'te kayıtlıdır ve **yeni kullanıcı kararı değildir**.

#### Mevcut durumla karşılaştırma ve geri-ekleme

Kabul havuzu ile aktif paketin her kalıbı yan yana değerlendirilir. **Geri-ekleme kontrolü:** kabul havuzundaki bir kalıp son turların çıkarılanlar listesiyle eşleşiyorsa normal `ekle` değil **"geri-ekleme önerisi"** olarak işaretlenir; eski çıkarma gerekçesi ile yeni kanıt yan yana konur ve **çelişki açık soru yapılır** (arşiv güvencesinin üç katmanından biri — Bölüm 4.5). ⚠️ Tespitin **kalıp metnine dayandığı** ve metni değişmiş kalıbı kaçırabildiği Bölüm 4.5'te kabul edilmiş sınırdır; kapatıcı olan kalıcı kalıp kimliği açık karardır (**K-84**, Bölüm 6.3).

#### Sentezin çıktısı ve statüsü

Sentez **dört çıktı** üretir: **(1)** paket içerik şemasına birebir uyan **aday JSON** · **(2)** **karar günlüğü** — her karar için bir satır (alan, kalıp, karar, gerekçe, kanıt referansı — Bölüm 6.5) · **(3)** **en fazla on açık soru** (her biri: konu, iki taraf, sentezin eğilimi) · **(4)** **özet** — *"operatör onay ekranı için"* tanımlıdır ve **ilk bölümü çıkarılanların tam listesidir** (gerekçeleriyle); ardından eklenen/çıkarılan/güncellenen sayıları ve son dört turun çıkarılanlar özeti gelir.

⚠️ **Günlüğün "her karar" kapsamı kesinleşmemiştir.** Karar kümesi **beş değerle kapalıdır** ve iki durum bu kümede karşılıksızdır: **reddedilen yeni adayın** (`alma`) karar izindeki temsili ve **sistemde karşılığı bulunmayan bir dönemin** günlüğe notlanması — ikincisini aynı sözleşme ayrıca **ister**. İkisi de kayıtlı açık karardır — reddedilen aday temsili **K-87**, eşleşmeyen özel gün notu **K-108** (Bölüm 4.3, Bölüm 6.5) — ve **ayrı ayrı** karara bağlanır. Etkileri aynı değildir: sistemde eşleşmeyen dönemin notlanması **sözleşmenin hâlihazırda istediği** bir yazımdır ve kapalı enumla bugün karşılanamaz; reddedilen aday temsilinde ise sözleşme etkisi **seçilecek temsile bağlıdır** (altıncı bir enum değeri seçilirse çıktı sözleşmesi revize edilir, karar izine gerekçe alanından bağlanırsa edilmez).

⚠️ **Sentez özeti ile yönetici onay yüzeyi arasındaki ilişki çözülmemiştir.** Yürürlükteki sözleşme bu çıktıyı **onay ekranının kendisi** gibi tanımlar ve tam listeyi ilk bölüm yapar; ölçeklenebilirlik modeli ise yöneticinin gördüğü yüzeyi **sayı ve eşik-üstü görünümüne** indirir, tam listeyi isteğe bağlı derinleşmeye bırakır (Bölüm 4.5). **Artefakt ile ekranın ayrı sözleşmeler olduğu hiçbir yerde yazılı değildir** ve bu belgede de kurulmaz; fark **açık kalır.** Onay yüzeyinin içeriği Bölüm 7.8'dedir.

**Yazım sınırı ve statü:** sentez çıktısı **değiştirilemez artefakt** olarak kaydedilir; veri tabanına yalnız `draft` yazılır ve aktivasyon kararı yöneticiye aittir (Bölüm 5.3, Bölüm 6.2).

⚠️ **Sentezin karar yetkisi motorun fazına bağlıdır — sözleşme revizyonu gerektirir.** Yürürlükteki sentez görev sözleşmesi sentezciyi **karar mercii** yapar (aktivasyon hariç). Motorlu modelde ise sentez raporu **aday değişiklik setidir**: motor sentezin kararlarını kendi kontrolleriyle sınar, reddedebilir ve nihai adayı ayrı üretir (Bölüm 7.7). İkisi aynı anda yürüyemez. Bu **yeni bir karar açmaz** — motorun fazı karara bağlandı: ✅ **K-22 KAPANDI — A** (2026-08-21, Ek B), motor **Faz 1'de** hattadır — ve sonucu artık koşulsuz gündemdir: **sentez görev sözleşmesinin rol hükmü revize edilmelidir.**

⚠️ **Açık karar (K-74) — sentezin on açık soru sınırı aşıldığında ne olur?** Uyuşmazlık sayısı sınırı aştığında ne olacağı — hangi ölçüte göre önceliklendirileceği, taşanların karar günlüğüne yazılıp yazılmayacağı, sınırın koşuyu durdurup durdurmayacağı — **tanımsızdır**. Sınırın **gerekçesi de hiçbir yerde yazılı değildir** ve bu belgede gerekçe atfedilmez. Davranış tanımlanmazsa **çözülmemiş uyuşmazlık sessizce düşebilir**.

⚠️ **Ayrı açık karar (K-75) — denetçinin beş açık soru önerisi sınırı aşıldığında ne olur?** Aynı boşluk denetim katmanında da vardır (Bölüm 7.4) ama **ayrı bir sözleşmeye aittir** ve ayrı seçilebilir: denetçinin taşan maddeleri denetim tablosunun satırlarına mı düşeceği, sentezin bunları görüp görmeyeceği ve sınırın kendisinin korunup korunmayacağı, sentez tarafındaki seçimden bağımsızdır. İkisi tek karara bağlanmaz.

### 7.6 Boyutlandırma ve limitler

**Damıtmanın iki gerekçesi:** paketin **prompt maliyeti** ve modelin **listedeki her şeyi kullanma eğilimi** — ikincisi paketin dağarcık olarak kullanılmasını sağlayan sabit talimatla (**K-04**) aynı sorunun iki ucudur (Bölüm 4.4, Bölüm 10). **Boyut disiplini sentezin sorumluluğudur:** araştırma tarafında üst sınır yoktur ve bu bilinçlidir — bilgi önce toplanır, sonra damıtılır (Bölüm 7.1 md.7).

#### Alan hedefleri ve toplam tavan

Değerler **hedeftir**; ölçülmüş eşik değildir ve bu belgede kabul kriterine çevrilmez.

| Alan | Hedef (karakter) |
|---|---:|
| `kapsam` | ~200 |
| `ton_ve_dil` | ~300 |
| `cta_kaliplari` | ~600 |
| `kanca_kaliplari` | ~400 |
| `gorsel_kodlar` | ~500 |
| `video_kodlar` | ~300 — **iki alt listenin toplamıdır** (hareket + sahne) |
| `takvim_temalari` | ~400 |
| `yasaklar_ve_hassasiyetler` | ~400 |
| özel gün, **dönem başına** | ~600 |

**Toplam tavan:** paket içeriğinin bütünü **~6.000 karakter ≈ 2.000 token**. Tavan şema doğrulayıcısında yazım anında zorlanır (Bölüm 5.3, Bölüm 7.7).

⚠️ **Hedeflerin toplamı tavanın üstündedir.** Sekiz temel alanın hedefleri toplandığında **3.100 karakter** eder; brief sözleşmesi **en az altı dönem** ister ve dönem başına hedef ~600 karakterdir, yani altı dönemde **3.600 karakter** daha eklenir — toplam **6.700 karakter**, tavanın **~700 karakter (≈%12) üstünde**; sekiz dönemde fark ~1.900 karaktere çıkar.

**Bundan çıkarılan tam olarak şudur:** *bütün yaklaşık hedefler aynı anda karşılanırsa toplam tavan aşılır.* Fazlası çıkarılamaz. Alan hedefleri ve dönem başı değer **yaklaşık hedeflerdir, alt sınır değildir**; alt sınır yalnız dönem sayısındadır (≥6) ve hiçbir hüküm alanların hedefe kadar doldurulmasını **istemez**. Sözleşme **iki bağımsız tetikleyicili** bir limit kurar ve ikisi birlikte çalışır: **yerel hedefi** aşan alan kendi içinde önem sırasına göre kırpılır; **global tavan** ise paketin bütününe ayrıca uygulanır. Biri diğerinin yerine geçmez — bir paket global tavanın altında kalırken tek bir alanı hedefini aşıyor olabilir, ya da bütün alanlar hedefinin altındayken toplam tavanı zorlayabilir. **Bu yüzden hesap bir sözleşme tutarsızlığı değildir** ve düzeltme kalemi açmaz; "kırpma her geçerli pakette olağandır" sonucu da **türetilemez** ve bu belgede iddia edilmez. Kaydın işlevi şudur: hedeflerin toplamı tavanın üstünde olduğu için **iki tetikleyicinin birlikte devreye girdiği koşullar gerçekçidir** ve aşağıdaki öncelik kararı bu yüzden etkilidir. Gerçek dağılım pilot paketinden ölçülecek ve token bütçesi ölçümüne (**K-12**) girdi olacaktır.

⚠️ **İkinci sayısal gerilim korunur:** ~6.000 karakter ≈ 2.000 token hedefi ile paketin çalışma zamanı maliyeti için verilen ~1,2–1,5K token tahmini birbirini tutmaz; **hiçbiri ölçüm değildir** (Bölüm 6.2, Bölüm 10). Ölçüm **K-12**'ye bağlıdır ve paket ile marka bilgi katmanının **toplamını** kapsamalıdır.

#### Aşımda öncelik ve kırpma kuralı

⚠️ **Kırpma önceliği açık karardır — K-121** (Bölüm 4.3'ten devreder; burada iki sıralama karşılaştırılır, taraf tutulmaz).

| | Yürürlükteki sözleşme sırası | Önerilen sıra |
|---|---|---|
| 1 | Sektöre özgülük | **Zorunlu mevzuat ve güvenlik bilgisi** |
| 2 | **Mutabakat gücü** | **Mevcut pakette doğrulanmış, sektöre özgü kalıplar** |
| 3 | Türkiye yerelliği | Üç araştırmada ortaklaşan yeni kalıplar |
| 4 | — | İki araştırmada ortaklaşan yeni kalıplar |
| 5 | — | Tek güçlü kaynağa dayanan yeni kalıplar |
| 6 | — | Genel-geçer, zayıf veya birbirini tekrar eden kalıplar |

**Statü asimetriktir ve bu ayrım korunur:** soldaki sıra **yürürlükteki sentez görev sözleşmesinin hükmüdür**; sağdaki bir **öneridir**. Öneri, sıralamanın kendisiyle birlikte **mevzuat/güvenliğin en üste alınmasını** getirir; bu ikisi aynı listenin parçalarıdır. Karar, **kırpılan kalıpların kümesini doğrudan değiştirir** ve benimsenirse **sentez görev sözleşmesinin ilgili adımı revize edilir**.

⚠️ **Churn koruması ayrı bir karardır — K-122 — ve sıralamayla birlikte alınmak zorunda değildir.** Koruma şudur: *"yeni fakat daha zayıf bir öğe, yalnız yeni olduğu için mevcut doğrulanmış kalıbı paketten çıkaramaz."* Yürürlükteki üçlü sıra korunurken churn korumasının benimsenmesi **mantıken mümkündür**: koruma bir sıralama ölçütü değil, kırpmanın **sonucuna** konan bir kısıttır. İkisi ayrı ayrı karara bağlanır.

**Önem sırasının iki katmanda farklı olması çelişki değildir** (Bölüm 7.1'den devreden kalem). Brief katmanının ikinci ölçütü *kaynak sayısı ve gücü*, kırpma katmanının ikinci ölçütü *mutabakat gücüdür*; tek bir araştırma koşusu üç aracın mutabakatını **göremez**. Yukarıdaki açık karar **yalnız kırpma katmanının sırasını** ilgilendirir.

#### Ham bilginin korunma biçimi

**Kırpılan öğe pakete girmez; kanıt zincirinden silinmez.** Boyut nedeniyle elenen kalıp **aday pakete alınmaz**, ama `kirp` kararıyla **karar günlüğüne** yazılır ve ham artefakt katmanında (salt-ekleme) durur; günlük hangi kalıbın **niçin** dışarıda kaldığını taşır (Bölüm 4.3, Bölüm 6.5). Ayrım şudur: kırpma **paketten çıkarır, kayıttan çıkarmaz**.

⚠️ **Bu, Bölüm 4.5'teki güvencenin sınırını genişletmez.** Verilen garanti "gözlemlenebilir değeri olan hiçbir kalıp **sessizce** kaybolamaz"dır; **sıfır-kayıp garantisi değildir.** ⚠️ Güvencenin **bağlayıcı garanti mi hedef mi** olduğu açık karardır — **K-40**. Kırpılan öğe ham katmanda durur, ama pakete geri girmesi **sonraki turun kararına** bağlıdır ve geri-ekleme tespitinin metin eşleşmesine dayanan sınırı burada da geçerlidir.

### 7.7 Otomatik politika ve kalite motoru

[GEREKİRSE]

⚠️ **Bu alt başlığın tamamı hedef modeldir.** Motor, kalıp-başına insan kararının ölçeklenmeyeceği analizinden doğan bir katmandır ve sentez ile aktivasyon arasına yerleşir. Hattaki fazı karara bağlandı: ✅ **K-22 KAPANDI — A** (2026-08-21, Ek B) — motor **Faz 1'de** hattadır (Bölüm 4.5, Bölüm 7.1). **Motorsuz modelde (K-22 kapanışıyla yürürlük dışı) bu alt başlığın hükümleri uygulanmaz:** aday paketi sentez üretir, akış doğrudan biçim doğrulayıcısına ve yönetici onayına geçer.

Motorun konumu: **girdi kapısı** ve **biçim kapısı** deterministiktir ve içerikle ilgilenmez (Bölüm 7.3); motor ise **karar kapısıdır** — sentezin ürettiği kalıp-başına kararları kontrol eder ve uygular. Karar tiplerinin tanımı ve otomasyon sınırı Bölüm 4.3 ile 4.5'tedir; burada yalnız **motor katmanının mekaniği** yazılır.

> **Dürüst sınır.** Motor bir **kural motorudur, kalite yargısı değildir**: bir kalıbın "iyi" olup olmadığını değerlendirmez, kanıt/bayrak/eşik/boyut kurallarını uygular. İçerik kalitesinin insan yargısı gerektirdiği yer aktivasyon öncesi **kör değerlendirme örneklemidir** (Katman-2) ve bu katman otomasyonla **ikame edilmez**. Örneklem boyutu **K-11 (a)**'da, geçme eşiği **K-11 (b)**'de açıktır; bu belgede eşik tanımlanmaz (Bölüm 13).

#### Girdiler

**Sentezin aday paketi ve karar günlüğü** (kalıp-başına karar + gerekçe + kanıt + denetçi bayrakları + sınıf) · **aktif paket ve şema sürümü** — evrimsel karşılaştırmanın tabanı · **son turların çıkarma kararları** — geri-ekleme çelişkisi tespiti · **iki denetçi tablosu ve URL örneklem sonuçları** · **mekanik eleme sonucu** · **sistemin güncel özel gün listesi** — anahtar doğrulaması · **politika yapılandırması** (bir kez konur, her turda uygulanır: çakışma politikası, bayrak tüketim kuralları, değişim sınırları, yüksek risk alanları, güncellik kuralları) · **otomatik kalite kapılarının sonuçları**.

⚠️ **Bu kümenin bir kalemi açık karara bağlıdır:** denetçi tablolarının motora doğrudan girdi sayılması, mutabakat kapısının benimsenmesine bağlıdır (**K-125**, aşağıda). **Prompt regresyonu açık karar değildir — zorunlu kapıdır:** regresyon geçmeden koşu `activation_eligible` sayılamaz (Bölüm 13).

#### Zorunlu kontroller

⚠️ **Küme kapalı değildir**; kesin küme uygulama spec'inde sabitlenecektir.

| Kontrol | İçeriği |
|---|---|
| **Şema** | Aday JSON'un alan tipleri, özel gün anahtarları ve boyut sınırları geçerli olmalı; biçim kapısıyla örtüşür (Bölüm 7.3) |
| **Karar kapsamı** | Aktif paketteki **her karar birimi** için tam olarak bir sonuç bulunmalı (`koru`/`guncelle`/`cikar`/`kirp`) |
| **Yeni kimlik** | Her `ekle` kararı yeni ve benzersiz bir kalıp kimliği taşımalı |
| **Kanıt** | `guncelle` ve `cikar` kararları denetçi satırı veya doğrulanmış URL referansı taşımalı; kanıt yoksa **karar uygulanmaz, kalıp korunur** |
| **Mutabakat** | `guncelle`/`cikar` için iki denetçi uyumu; yeni öğede eşiğin üstüne iki denetçi kabulü — ⚠️ **kapının benimsenmesi açık karardır (K-125)**; bağlı karar kümesi aşağıda |
| **Yeni öğe eşiği** | `2-3` ve üzeri; tekil istisna yalnız güçlü kaynaklı ve *muhtemel-uydurma*/`[yerel-değil]` bayrağı yoksa (Bölüm 4.3) |
| **Bayrak tüketimi** | Bölüm 7.5'teki kurallar motor katmanında da uygulanır |
| **Geri-ekleme** | Çıkarılanlar listesiyle eşleşme → çelişki işaretlenir, açık soruya düşer |
| **Kategori çakışması** | Paket tür etiketi ile sistem kategorisi çeliştiğinde **politika uygulanır: paket türü üstündür** (**K-03**) ve çatışma karar günlüğüne yazılır. ⚠️ *"Motor kararsız"* dalı **bu çatışma için düşmüştür**; başka belirsizlik türleri için geçerliliğini korur. Uygulama ayağı Bölüm 14.4'teki sözleşme düzeltmesine bağlıdır |
| **Özel gün anahtarı** | Sistem listesinde karşılığı yoksa pakete girmez, günlüğe notlanır; günlükteki temsili açık (Bölüm 6.5) |
| **Boyut** | Alan hedefleri + toplam tavan; aşımda önem sırasına göre `kirp` (Bölüm 7.6) |
| **Diff** | Ekleme/güncelleme/çıkarma/kırpma sayıları alan bazında ve toplamda hesaplanır |
| **Değişim bariyeri** | Yapılandırılmış sınır aşılırsa koşu aktive edilemez — ⚠️ bariyerin kurulması açık karardır (**K-130**), aşağıda |
| **Regresyon** | Zorunlu prompt testleri geçmeden koşu `activation_eligible` sayılamaz; kapı protokolüne bağlı (Bölüm 13) |
| **Tek aktif sürüm** | Aktivasyon işleminin veri tabanı değişmezini koruyacağı **önceden** kontrol edilir (Bölüm 8) |

#### Güvenli fallback

**Yön Bölüm 4.5'te kayıtlıdır:** motor belirsizliği **yeni içeriğin lehine yorumlamaz** — karar veremediği yerde değişiklik yapmaz, mevcut kalıp korunur ve durum koşu raporuna yazılır. Gerekçe evrimsel modelin temel ilkesidir: *kanıt yoksa koru*; belirsizlikte sessizce çıkarma bilgi kaybı üretir.

⚠️ **Aşağıdaki tablonun deterministik bir varsayılan kümesi olarak benimsenmesi açıktır (K-23).** Benimsenirse uygulanacak biçimi şudur:

| Belirsizlik | Uygulanacak sonuç |
|---|---|
| Eski öğe hakkında yeni kanıt yok | Eski öğeyi **koru** |
| Güncelleme mutabakatı yok | Eski biçimi **koru** |
| Çıkarma mutabakatı yok | Öğeyi **koru** |
| Yeni öğe kabul eşiğini geçmiyor | Aday pakete **ekleme** |
| Mevzuat/güvenlik öğesi doğrulanamıyor veya çelişkili | **Koşuyu blokla** |
| Karar kapsamı eksik veya aynı kimlikte iki karar | **Koşuyu blokla** |

**Son iki satır aynı yere ait değildir.** Mevzuat/güvenlik uyuşmazlığında bloklama, açık olan **politika çatışması kapısının** konusudur (**K-128**, Bölüm 4.5). *Karar kapsamı eksikliği veya aynı kimlikte iki karar* ise bir politika tercihi değil, motorun **yapısal bütünlük kontrolüdür**: karar kapsamı sözleşmesi ve benzersiz kalıp kimliği sağlanmadan motor güvenilir sonuç üretemez — bu satır **karar kapsamı ve kalıcı kalıp kimliği** (**K-84**) kararlarına bağlıdır (Bölüm 6.3), bloklama kapısı kararına değil.

**Fallback'ler sentez raporunu yerinde değiştirmez:** motor nihai adayı **ayrı** üretir ve hangi sentez kararını niçin reddettiğini politika raporuna yazar — özgün sentez korunur. Bu üçlünün **ayrı saklanma biçimi** açık karardır (**K-96**, Bölüm 7.2).

#### Durdurma bariyerleri — üçü ayrı, biri diğerini ikame etmez

**(a) Değişim büyüklüğü bariyeri — K-130.** Motor en az şu oranı hesaplar: `değişim oranı = (güncelle + çıkar + çalışma zamanını etkileyen kırpma) / mevcut karar birimi sayısı`. Sınır aşılırsa yöneticiye kalıp bazlı liste yüklenmez, koşu bloklanır ve aktif paket değişmez. **İlk paket koşusunda payda sıfır olduğu için oran hesaplanmaz;** ilk paket alan/adet sınırları, toplam boyut, kanıt eşikleri ve ekleme sayısı için **mutlak limitlerle** kontrol edilir. Formülün "en az" diye kurulması bilinçlidir: hesaplanacak oran kümesi kapalı değildir.

**(b) Ekleme oranı bariyeri — K-131.** Yeni öğe sayısı raporlanır ve alan/toplam boyutun yanında **ayrı bir ekleme oranı bariyeri** öngörülür. Bu, değişimin büyüklüğünden farklı bir şeyi ölçer — paketin **şişmesini**.

**(c) Kararsızlık oranı bariyeri — K-132.** Motorun karar veremediği madde oranı eşiği aşarsa tur durur. Bu, değişimin büyüklüğünü değil **motorun aczini** ölçer; otomasyonun işi insana geri devretme oranıdır. Eşiği **tanımsızdır** ve **K-24**'e bağlıdır; risk kaydı Bölüm 18'dedir.

⚠️ **Üç bariyer birbirinin yerine geçmez ve hiçbiri kesinleşmiş hüküm değildir. Üçünün de kurulup kurulmayacağı ayrı ayrı açık karardır — K-130 · K-131 · K-132** — biri alınıp diğeri reddedilebilir, çünkü farklı şeyleri ölçerler: değişimin büyüklüğü, paketin şişmesi ve motorun aczi. ⚠️ **K-24'ün kapsamı:** o karar motorun **eşik ve limit değerlerini** kapsar — otomatik red eşiği, kararsızlık oranının değeri, bariyerler benimsenirse değişim ve ekleme oranı sınırları **ve ilk paket koşusunda uygulanacak mutlak limitlerin değerleri**; **bariyerlerin kurulup kurulmayacağı ondan ayrı üç karardır.**

**Eşik ilkesi korunur:** kesin eşikler **kanıtsız seçilmez**; pilot ve ilk kontrollü koşulardaki gerçek dağılımla kalibre edilip politika yapılandırmasına yazılır. Bu bölümde **hiçbir sayısal eşik tanımlanmamıştır**.

#### Kuru mod

Motorun kararlarını **uygulamadan önce yalnız raporladığı** bir kuru mod (dry-run) öngörülür; gerekçesi motor kurallarının yanlış olması riskidir — yanlış bir kural motorlu modelde bütün sektörlere aynı anda yayılabilir.

⚠️ Kuru mod **yeni bir koşu kipidir**: koşu sonucu, kayıt yeri ve yöneticiye gösterimi bakımından kendi sözleşmesini gerektirir. **Zorunlu olup olmadığı açık karardır — K-133 — ve motorun fazından (K-22) ayrıdır** — motor benimsense de kuru mod ayrıca kararlaştırılmalıdır.

#### Mutabakat kapısı — bağlı karar kümesinin motor ayağı

Motor katmanında ikinci bir kapı öngörülür: `guncelle` ve `cikar` için **iki denetçi uyumu** aranır (uyuşmazlıkta normal içerikte eski kalıp korunur, mevzuat/güvenlikte koşu bloklanır); yeni öğede `2-3` eşiğinin üstüne **iki denetçi kabulü** eklenir; tek resmî/birincil kaynak istisnasında ise iki denetçinin URL doğrulaması aranır. **Kapının benimsenmesi açık karardır — K-125**; alternatif modelde pozitif kanıt satırı gerekli koşuldur ve ikinci bir kapı tanımlı değildir.

⚠️ **Kapı benimsense bile iki sözleşme kalemi ayrıca kesinleştirilmelidir; ikisi de bağlı kümenin mevcut iki kararına indirgenemez:**

- **Mevzuat/güvenlik sayılan alanların ve bu alanlarda koşuyu bloklayan uyuşmazlıkların kesin listesi — K-129.** Bugün tanımsızdır ve fallback tablosunun bloklama satırının **kapsamını doğrudan belirler**: hangi alanın "mevzuat/güvenlik" sayıldığı kapının ne sıklıkla devreye gireceğini tayin eder.
- **Tek resmî/birincil kaynak istisnasının kesin sözleşmesi — K-126** — iki denetçi URL doğrulamasının ve kaynak önceliğinin nasıl tanımlanacağı. ⚠️ Yukarıdaki tarif bu istisnanın **kesinleşmiş davranışı değildir**.

⚠️ **Bu küme Bölüm 7.4'te açılmıştır ve burada yeniden açılmaz — yalnız motor ayağı bağlanır.** Kapının girdisi, iki denetçinin aktif paketi yeniden doğrulamasıyla üretilir; o ek görev alınmazsa kapı **girdisiz kalır ve fiilen çalışmaz**. Kümenin iki satırı (kapının benimsenmesi **K-125** · benimsenirse denetçi görev sözleşmesine eklenecek envanterin adı ve şeması **K-100**) Bölüm 4.3'te kayıtlıdır. **Kapının motor tarafındaki karşılığı** yukarıdaki kontrol tablosunun "Mutabakat" satırı ile fallback tablosunun ilgili satırlarıdır; bunlar kapı benimsenmezse uygulanmaz.

#### Sonuç tipleri ve izlenebilirlik

**Seviye ayrımı Bölüm 4.5'te kurulmuştur:** koşu seviyesi (`activation_eligible` · `no_change` · `blocked`), kalıp-kararı seviyesi (`uygulandı` · `uygulanmadı (kanıt yetersiz)` · `motor kararsız`) ve paket statüsü ayrı seviyelerdir; `tur durduruldu` öğesinin `blocked` ile birleştirilip birleştirilmeyeceği açık karardır — **K-90**.

⚠️ **Koşu seviyesinin veri tarafı sonuçları normatif değildir.** `no_change` ve `blocked` koşularının **paket satırı oluşturmadan nerede kayıtlanacağı** (**K-93**) ve karşılaştırmanın dayandığı **canonical üretim kuralı** (**K-92**) **kesinleşmemiştir**; Bölüm 6.4 bunu açık olarak kaydeder ve bu bölüm de kapatmaz. `no_change`'in **ilk koşuda geçersiz sayılması** ayrıca açık karardır — **K-91**.

**Motorun yetki sınırı — K-28.** Motor `active` satırına **dokunamaz**: bloklanan bir sonuç hiçbir yol üzerinden aktive edilemez ve aktivasyon yalnız yöneticinin onayıyla gerçekleşir. İlke kesindir; **sunucu tarafında nasıl zorlanacağı** ayrı ve açık bir teknik karardır — **K-103**.

**İzlenebilirlik.** ⚠️ **İki ayrı açık karardır ve burada birleştirilmez:** karar satırına **aktör alanı** eklenmesi — kararı motorun mu insanın mı verdiğinin ayırt edilebilmesi — **K-25**'te açıktır; motorun **sürümünün ve yapılandırmasının** her koşuya damgalanması **K-97**'de açıktır. Aktör alanı benimsenirse motorun verdiği her karar, insanın verdiği kararla **aynı biçimde** karar günlüğüne yazılır (kanıt alanı dâhil). İki granülerlik **birbirini dışlamaz ve birlikte alınabilir** (Bölüm 6.5). Hiçbiri alınmazsa kötü bir paket sürümünün kaynağının (motor kuralı mı, sentez mi) teşhisi **zorlaşır** — bu bir gerekçedir, karar değildir.

### 7.8 Aday çıktı ve son onay

#### Onay öncesi gösterilecek özet

**Yöneticinin gördüğü yüzey motorlu modelde kalıp listesi değildir** — Bölüm 4.5'in otomasyon sınırı orada uygulanır. ⚠️ **Motorsuz modelde aynı şey söylenemez:** yürürlükteki sentez sözleşmesi çıkarılanların **tam listesini** onay ekranının ilk bölümü yapar ve yönetici sentezin karar günlüğüne bakar (Bölüm 7.5). *"Kalıp listesi görülmez"* hükmü bu yüzden modele bağlıdır; yürürlükteki model **motorlu modeldir** (✅ **K-22 KAPANDI — A**, Ek B) — ancak sözleşme drifti kapanana kadar (Bölüm 14.4) yürürlükteki sözleşme metni hâlâ tam listeyi gösterir.

⚠️ **Aşağıdaki tablo motorlu modelin yüzeyidir — yürürlükteki modeldir** (✅ **K-22 KAPANDI — A**, 2026-08-21, Ek B). Motorsuz modelde (K-22 kapanışıyla yürürlük dışı) koşu sonucu, değişim oranları, motorun kararsız kaldıkları ve motor koşu raporu **üretilmez**; o modelde yönetici **sentezin özetini, karar günlüğünü, açık soruları ve kapı sonuçlarını** görür ve onay bu kümeye dayanır (Bölüm 7.5).

| Bileşen | İçeriği |
|---|---|
| **Koşu sonucu** *(motorlu)* | Üç değerden biri; yalnız `activation_eligible` sonucunda onay verilebilir |
| **Sayılar** | Eklenen · güncellenen · çıkarılan · kırpılan öğe sayıları; **alan bazında ve toplamda** |
| **Değişim oranları** *(motorlu)* | Toplam ve alan bazlı *(bariyer kararına bağlı — 7.7)* |
| **Çıkarılanlar** | Sayı ve eşik-üstü olanlar; tam liste derinleşmede. ⚠️ **Eşiğin kendisi açık karardır (K-41)** — tanımlı değildir ve bu belgede uydurulmamıştır; değer, yöneticinin hangi riskli çıkarmayı **göreceğini** doğrudan belirlediği için ürün ve risk kararıdır (Bölüm 4.5) |
| **Son dört turun çıkarılanlar özeti** | Korunur — insan hafızasına dayanmayan geri-ekleme tetikleyicisi |
| **Motorun kararsız kaldıkları** *(motorlu)* **ve geri-ekleme çelişkileri** | Sayı ve liste; kararsızların akıbeti **K-23**'e bağlıdır |
| **Açık sorular** | Sentezin listesi (≤10); taşma davranışı açık karardır (**K-74**, Bölüm 7.5) |
| **Kapı sonuçları** | Değişiklik öncesinde dondurulmuş prompt fixture'ıyla karşılaştırma (deterministik) **ve** kör değerlendirme örneklemi. ⚠️ İkincisi **kalite sinyalidir, otomatik geçme/kalma kapısı değildir** — örneklem boyutu **K-11 (a)**'da, eşik **K-11 (b)**'de açıktır (Bölüm 2.3, Bölüm 13) |
| **Uyarılar** | Varsa |
| **İçerik hash'leri** | Aday ve aktif paket için *(canonical üretim kuralı açık karardır — **K-92**, Bölüm 6.5)* |
| **Motor koşu raporu** *(motorlu)* | Kaç karar uygulandı, kaç reddedildi, kaç kararsız kaldı |

⚠️ **Sentez özetinin ilk bölümü ile bu yüzey arasındaki ilişki Bölüm 7.5'te açık bırakılmıştır** ve burada kapatılmaz: yürürlükteki sentez sözleşmesi çıkarılanların **tam listesini** doğrudan onay ekranının ilk bölümü yapar; ölçeklenebilirlik modeli aynı listeyi sayı ve eşik-üstü görünümüne indirir. Yukarıdaki tablo **ikinci modeli** tarif eder; **sözleşme ayağı düzeltilmedikçe** fark açık kalır.

⚠️ **Özet diff'in "sinyal odaklı" tasarlanması bir risk kontrolü önerisidir, yükümlülük değildir.** Yöneticinin özeti "onay tıklamasına" indirgemesi risk olarak kayıtlıdır; karşı önlem diff'in sinyal odaklı tasarlanması, tespit göstergesi ise aktivasyon süresi metriğidir. **Benimsenip benimsenmeyeceği açık karardır — K-42 — ve ürün/risk seviyesindedir** — yöneticinin hangi riskleri göreceğini ve onayın bir tıklamaya dönüşüp dönüşmeyeceğini belirler; etkisi **ölçülmemiştir**; risk kaydı Bölüm 18'dedir.

⚠️ **Yöneticiye gösterilen anlık görüntünün değiştirilemez olması açık karardır — K-98.** Önerilen gereksinim: politika raporu üretildikten sonra yöneticinin gördüğü görüntü üzerinde değişiklik yapılamaz; benimsenirse zorunlu testle sınanır. İçerik hash'i ve aşağıdaki base sürüm kontrolü bunu **ikame etmez** — biri içeriğin kimliğini, diğeri tabanın tazeliğini denetler; bu ise **gösterilenin sonradan değişmemesidir**. Kaydın nerede tutulacağı politika değerlendirme kaydına bağlıdır (**K-95**, Bölüm 6.5).

#### Onay anında base sürüm kontrolü

Motorun değerlendirme yaptığı **base `active` paket sürümü** ile **onay anındaki** `active` sürüm farklıysa politika sonucunun **otomatik geçersiz** sayılması öngörülür; koşu ile onay arasında sürüm değişirse yönetici **yanlış tabana** dayanan bir diff onaylar (risk kaydı Bölüm 18'dedir).

⚠️ **Aday ve aktif içerik hash'ini yöneticiye göstermek bu korumanın yerine geçmez:** hash bir *gösterim*, geçersizlik kuralı ise bir *kapıdır* — biri yöneticinin fark etmesine, diğeri sistemin reddetmesine dayanır. **Kuralın benimsenip benimsenmeyeceği açık karardır — K-94.**

#### Aktivasyon ön koşulu olarak açık sorular — çözülmemiş çatışma

Bir aktivasyon ön koşulu listesi **"açık soruların tamamı operatörce kapatılmış olması"** maddesini taşır; başka bir liste aktivasyon ön koşullarını **kapalı** sayar ve bu maddeyi **içermez**. Çatışma çözülmemiştir.

⚠️ **Bu, K-23'e indirgenemez:** K-23 motorun *kararsız bıraktığı maddelerin nereye düşeceğini* sorar; buradaki soru, **açık soru kalmışken aktivasyona izin verilip verilmeyeceğidir**. İkisi birlikte alınırsa aktivasyon fiilen bloklanabilir, ayrı alınırsa yönetici açık sorularla birlikte aktive edebilir. Yukarıdaki onay yüzeyi açık soruları **gösterir** ama kapatılmalarını ön koşul yapmaz. **Açık soruların tamamının kapatılmış olmasının aktivasyon ön koşulu sayılıp sayılmayacağı açık karardır — K-71.** Aktivasyon ön koşullarının tam listesi Bölüm 8'de yazılacaktır.

#### Onay yetkisi

Son onay **yöneticiye/operatöre** aittir ve tek bir sorunun cevabıdır — *"bu sürüm aktive edilsin mi?"* Sentez ve politika motoru karar mercii olabilir, **aktivasyon mercii değildir**; `activation_eligible` sonucu **otomatik aktivasyon anlamına gelmez**. Kalıp düzeyindeki doğruluk yöneticinin gözüne değil, kural ve inceleme zincirine emanet edilmiştir. Rolün ikiye bölünüp bölünmeyeceği (turu koşan yönetici ↔ kapsam ve risk kabulünü koyan ürün sahibi) açık karardır — **K-54** (Bölüm 7.2, Bölüm 15).

#### Red veya düzeltme akışı

Reddedilen aday **`draft` olarak veri tabanında kalır**. ⚠️ **Düzeltmenin yeni bir taslak sürüm mü açacağı, yoksa mevcut taslağı yerinde mi güncelleyeceği açık karardır — K-106**; taslak satırında güncelleme teknik olarak serbesttir, çünkü salt-ekleme kısıtı **ham artefakt katmanına** aittir, paket tablosuna değil (Bölüm 6.2). ⚠️ **Yöneticinin reddinin bir düzeltme turu başlatıp başlatmayacağı ayrıca açık karardır — K-72.**

⚠️ **Son onay veya ret olayının kimlik ve zaman damgasıyla kaydedilmesi açık karardır — K-99.** Benimsenirse yöneticiye gösterilen politika anlık görüntüsü ile son onay/ret olayı birlikte loglanır. Kaydın **nerede tutulacağı** politika değerlendirme kaydına bağlıdır (**K-95**, Bölüm 6.5, Bölüm 7.2).

#### Aktivasyonun atomiklik beklentisi

**Sıra zorunludur:** **önceki aktif sürüm varsa** önce eski `active` → `archived`, sonra taslak → `active`; tek aktif sürüm değişmezi bunu gerektirir (ilk pakette yalnız ikinci adım koşar — Bölüm 8.2, 14.1). ⚠️ **Önceki sürümün arşivlenmesi ile adayın etkinleştirilmesinin tek işlem olup olmayacağı açık karardır — K-101** (geri alma tarafının karşılığı **K-102**'dir). Tek işlem beklentisi bir **varsayımdır** ve spec'te kesinleşmelidir. Motor kontrol listesinde karşılığı *"aktivasyon işleminin değişmezi koruyacağı önceden doğrulanmalıdır"* maddesidir.

**Atomiklik sağlanmazsa** arada sektörün hiç aktif paketi olmadığı bir pencere doğar; o pencerede üretim yapan marka **sessizce paketsiz yola düşer** — güvenli taraftır ama gözlenmesi gerekir. ⚠️ **Ara pencerede başlayan üretimin hangi sürüme bağlanacağı (K-104) ve okuyucu davranışı testinin aktivasyon öncesi zorunlu olup olmayacağı (K-105) açık kararlardır.** Aktivasyon ve geri alma prosedürünün kendisi Bölüm 8'de yazılacaktır; **yetkilendirmenin teknik olarak nasıl zorlanacağı açık karardır** (**K-103**, Bölüm 4.3).

---

## 8. Yaşam döngüsü

[GEREKİRSE]

**Bu bölüm yalnız paket sürümünün yaşam döngüsünü yazar.** Durum kümesi `draft` → `active` → `archived`'dır ve sektör başına tek `active` sürüm veri tabanı düzeyinde garantilidir; ikisi de iki hakem belgesinde ortak, ortak kaynak karar dokümanında **onaylı karardır** ve Bölüm 6.4'te kayıtlıdır — burada tekrar edilmez, üzerine geçişler yazılır.

⚠️ **Koşu seviyesi sonuçları paket statüsü değildir** (Bölüm 4.5, 6.4, 7.7): `activation_eligible` · `no_change` · `blocked` bir koşunun sonucudur, bir satırın durumu değil. Bunların veri tarafındaki karşılığı — sürüm oluşturmayan koşuların nerede kayıtlandığı — açık karardır ve bu bölümde de kapatılmaz.

⚠️ **Motorlu ↔ motorsuz ikiliği bu bölümde de kayıtlıdır; yürürlükteki model motorlu modeldir** (✅ **K-22 KAPANDI — A**, Ek B). Aşağıdaki geçişlerin ve ön koşulların bir kısmı politika motorunun varlığını varsayar ve motor Faz 1'de olduğundan **Faz 1 gündemindedir**; motora bağlı olanlar ayrı ayrı işaretlenmiştir.

### 8.1 Durumlar ve geçişler

| Mevcut durum | Olay / koşul | Yeni durum | Yetkili aktör | Yan etki |
|---|---|---|---|---|
| (yok) | Sentezin aday paketi biçim doğrulayıcısından geçti | `draft` | Koşuyu yürüten komut ailesi | `version` = sektördeki son sürüm + 1. **Ortak ve kaynakta onaylı:** koşu veri tabanına **yalnız `draft`** yazar. ⚠️ Satır, kendisini üreten koşuya koşu kimliğiyle bağlanır; **bu bağın zorunlu olup olmadığı açık karardır** (Bölüm 6.1, 6.2) — zorunlu değilse provenans bağı garanti edilmez |
| (yok) | *(motorlu)* Sentez raporu kaydedildi → motor kararları uyguladı → doğrulayıcı geçti | `draft` | Politika motoru | Motorun her kararı karar günlüğüne kanıt satırıyla yazılır; özet diff ve koşu raporu üretilir. `[SEA-2026-08-11]` — **K-22**'ye bağlı |
| `draft` | *(motorlu)* Motor karar veremediği madde bıraktı | `draft` (bekler) | Yönetici **veya** güvenli varsayılan | Kararsız maddeler koşu raporunda taşınır; akıbetleri **K-23**'te açıktır. `[SEA-2026-08-11]` |
| `draft` | Red veya düzeltme istendi | `draft` (güncellenmiş) | Yönetici + komut ailesi | ⚠️ **Yalnız bir hakem belgesinde; diğerinde ele alınmamıştır** (Bölüm 7.8): reddedilen aday `draft` olarak kalır. Kısıt tarafı ortaktır — salt-ekleme **ham katmana** aittir, paket tablosuna değil (Bölüm 6.2). ⚠️ **Burada iki ayrı açık karar vardır:** *(a)* akışın benimsenmesi · *(b)* düzeltmenin **sürümleme biçimi** — yeni bir taslak sürüm yazmak mı, mevcut taslağı yerinde güncellemek mi; kaynak hakem ikisini de mümkün sayar, seçmez. Motorlu modelde *(b)*'nin ek bir sonucu vardır: **yerinde güncellemeden sonra motor kontrollerinin ve biçim doğrulayıcısının yeniden koşulup koşulmayacağı**, iki hakem belgesinde ve dokuz kaynak dosyada **harf duyarsız arandı, tanımlayan hüküm bulunamadı** — bulunan *"tekrar koşulur"* hükümlerinin tamamı tur ve denetim düzeyindedir, taslak düzeltmesi düzeyinde değil |
| `active` | Yeni sürüm aktive ediliyor — **adım 1** | `archived` | Yönetici | Tek `active` değişmezi bu sırayı zorunlu kılar |
| `draft` | Yeni sürüm aktive ediliyor — **adım 2** | `active` | Yönetici | `activated_at` yazılır; alt sektördeki markalar paket yoluna geçer. İki adımın **tek işlem** olması beklenir (8.2) |
| `active` | Geri alma — **adım 1** | `archived` | Yönetici | Kötü sürüm önce arşivlenir (8.3) |
| `archived` | Geri alma — **adım 2** | `active` | Yönetici | Önceki sürüm yeniden yürürlüğe girer; ters sıra indeks tarafından reddedilir (8.3) |
| `active` | **Yerine yeni sürüm konmadan paketin geri çekilmesi (deaktivasyon)** | `archived` | Yönetici | Alt sektördeki markalar **sessizce paketsiz yola döner**. ⚠️ **Yalnız bir hakem belgesinde; diğer hakemde ve dokuz kaynak dosyada karşılığı bulunamadı** (harf duyarsız tarama) — reddedilmiş değil, ele alınmamıştır. Aşağıdaki nota bakınız |
| Ham artefakt satırı | Herhangi bir `UPDATE` / `DELETE` | **geçiş yok** | — | Veri tabanı işlemi reddeder. **Ortak ve kaynakta onaylı karar** (Bölüm 4.2, 6.2) |

⚠️ **Yetkili aktör sütunu tek bir rolü isimlendirmez.** Aktivasyon ve geri alma kararının **yöneticiye/operatöre** ait olması iki hakem belgesinde de ortaktır; bu rolün ikiye bölünüp bölünmeyeceği (turu koşan yönetici ↔ kapsam ve risk kabulünü koyan ürün sahibi) **açık karardır** (Bölüm 7.2, Bölüm 15). Yetkinin teknik olarak nasıl zorlanacağı ayrıca açıktır (8.2).

> **Deaktivasyon — çözülmemiş.** Bir hakem belgesi, aktif paketin yerine yeni bir sürüm konmadan geri çekilmesini desteklenen bir geçiş olarak yazar ve olay müdahalesinde *"en ucuz acil kol"* sayar. Geçişin kendisi yeni bir şema alanı veya yeni bir durum yaratmaz — mevcut `archived` değerini kullanır; **yeni olan, yöneticiye verilen operasyonel yetkidir** ve sonucu bir ürün davranışıdır: o alt sektördeki bütün markalar tek işlemle paketsiz yola döner. Tek hakem beyanıyla çözülmüş sayılamaz (yeni rol yükümlülüğü); **açık karardır** ve seviyesi ürün/risktir. **Geri almadan ayrı bir karardır:** geri alma bir önceki sürüme dönerken deaktivasyon paketli yolu tamamen kapatır; biri benimsenip diğeri reddedilebilir.

> **Bu tablonun dışında kalanlar.** `no_change` ve `blocked` sonuçlanan koşular, bir hakem belgesine göre **paket satırı üretmeden** durumlandırılır — yani yukarıdaki geçişlerin hiçbirini tetiklemezler; aynı belge `no_change` karşılaştırmasını **canonical içerik hash'ine** dayandırır ve ilk paket koşusunda `no_change` sonucunu **geçersiz** sayar. Diğer hakem belgesinde bu kavramların karşılığı **yoktur** — reddedilmiş değil, hiç ele alınmamıştır; o belgede her koşu bir sonraki sürüm numarasıyla taslak üretir. Üç nokta da **ayrı ayrı açık karardır** ve Bölüm 6.4'te kayıtlıdır; bu bölüm de kapatmaz — **kaydın yeri** (ham katmanda tür mü, paket tablosunda alan mı, ayrı tablo mu) · **eşdeğerliği hesaplayan canonical hash kuralı** · **ilk koşuda geçersizlik**. İlk ikisi tek kaleme bağlanamaz: kaydın nereye yazılacağını seçmek ile iki içeriğin ne zaman "aynı" sayılacağını seçmek farklı sorulardır ve o hakemin kendi açık karar listesinde de **ayrı maddelerdir**; biri benimsenip diğeri reddedilebilir. `[SEA-2026-08-11]`

### 8.2 Aktivasyon / yayımlama

#### Ön koşullar

⚠️ **İki belgenin ön koşul listeleri aynı değildir ve biri kendini kapalı ilan eder.** Bir hakem *"yeni sürüm yalnız aşağıdaki koşulların tamamında aktivasyona adaydır"* diyerek altı maddelik **kapalı** bir liste verir; diğerinin beş maddelik listesi kapalı ilan edilmez. Aşağıda üç küme ayrı tutulmuştur.

**(a) Ortak ve kaynak destekli çekirdek:**

1. **Taslak biçim doğrulayıcısından geçmiş olmalıdır** — alan şeması, boyut sınırları ve özel gün anahtarları. Doğrulayıcı yazımdan önce çalışır ve reddederse taslak hiç yazılmaz (Bölüm 5.3, 6.4). Anahtar biçiminin kendisi **K-01b**'de açıktır.
2. **İşlevsel kapının prompt ayağı geçmiş olmalıdır** — paketsiz markada, **değişiklik öncesinde dondurulmuş prompt fixture'ı** ile karşılaştırma; modele gönderilen mevcut prompt parçaları byte-exact değişmemiş olmalıdır (**Katman-1**). Kaynak karar dokümanı kapı testini operatör onayının **önüne** koyar; yürürlükteki sentez görev sözleşmesi de kapı testini *"o onayın girdisi"* olarak tanımlar.
3. **Yöneticinin son onayı** — Bölüm 7.8'deki tek soru: *bu sürüm aktive edilsin mi?*

⚠️ **Katman-2 (çıktı örneklemi) bu listeye kapı olarak girmez.** Kör değerlendirme örnekleminin yöneticiye sunulması bir hakem belgesinde ön koşul olarak sayılır; ancak aynı belge bu katmanın **otomatik geçme/kalma kapısı olmadığını** yazar. ⚠️ **K-11 tek ID altında iki ayrı kararı taşır ve ikisi ayrı seçilebilir:** *(a)* örneklemin **boyutu** — operasyonel yük · *(b)* bir **geçme eşiği** konup katmanın kapıya çevrilip çevrilmeyeceği. Boyut belirlenip eşik tamamen reddedilebilir; eşik konursa katman kabul kriterine dönüşür (Bölüm 2.3, 13). Bu bölüm eşik tanımlamaz ve katmanı başarısızlık koşulu hâline getirmez: **sunulması** bir ön koşul olarak taşınır, **sonucu** kapı değildir (Bölüm 2.3, Bölüm 13).

**(b) Yalnız motorlu modelde geçerli olan ek koşullar** `[SEA-2026-08-11]` **— K-22'ye bağlı, tek hakem belgelerinde:**

4. Koşu sonucu `activation_eligible` olmalıdır.
5. Aktif paketteki bütün kalıplar için **karar kapsamı tam** olmalıdır.
6. Şema, kanıt, mutabakat, değişim bariyeri ve regresyon kontrolleri geçmiş olmalıdır *(bu maddelerin her biri kendi açık kararına bağlıdır — Bölüm 7.7)*.
7. Bloklayıcı mevzuat/güvenlik uyuşmazlığı bulunmamalıdır *(bu alanların kesin listesi açıktır — Bölüm 7.7)*.
8. Motor koşusu tamamlanmış, özet diff ve koşu raporu üretilmiş, motorun kararsız bıraktıkları **K-23** politikasına göre çözülmüş olmalıdır. ⚠️ Aynı belge buraya bir **durdurucu** ekler: motorun **kararsızlık oranı eşik-üstüyse tur durur ve aktivasyon yapılmaz**. Bu maddenin iki ayağı da açıktır ve **ayrı ayrı seçilebilir** — bariyerin kurulup kurulmayacağı (Bölüm 7.7'deki üç bariyerden biri) ile eşiğin değeri (**K-24**) ayrı kararlardır; bu bölümde eşik tanımlanmamıştır.

⚠️ **Bu kümenin kapsamı dar okunmamalıdır:** kapalı listeyi veren belgede **altı koşulun beşi** motorun varlığını varsayar. Motorsuz modelde o liste **uygulanamaz**; geriye (a) kümesi ile aşağıdaki (c) maddesi kalır. **(a) kümesi keyfî bir kalıntı değildir:** ortak kaynak karar dokümanı pilotun zincirini *"taslak → işlevsel kapı testi → operatör onayı → `active`"* olarak yazar; motorsuz modelin ön koşulları bu zincirdir.

**(c) Çözülmemiş çatışma — açık sorular ön koşul mudur?**

Bir hakem belgesi ön koşulları arasında **"açık soruların tamamı operatörce kapatılmış olması"** maddesini taşır; aynı belge motorlu modelde kararsızların akıbetini **K-23**'te açık bırakır ve bu gerilimi kendi içinde çözmez. Diğer hakemin **kapalı** listesi bu maddeyi **içermez** — burada sessizlik, listenin kapalı ilan edilmiş olması nedeniyle dışlama etkisi taşır.

⚠️ **Bu çatışma Bölüm 4.5'te bu bölüme ertelenmişti; burada kapanmaz, ancak tam kapsamıyla görünür kılınmıştır.** Karar **K-23'e indirgenemez** (Bölüm 7.8): K-23 kararsız maddelerin nereye düşeceğini sorar, buradaki soru **açık soru kalmışken aktivasyona izin verilip verilmeyeceğidir**. İki taraf gövdede yazılmaz; **açık karardır**, seviyesi ürün/risktir ve karar ID'si Bölüm 17 sweep'inde verilecektir. Onay yüzeyi açık soruları **gösterir** ama kapatılmalarını ön koşul yapmaz (Bölüm 7.8).

#### Aktivasyon işlemi

**Sıra ortaktır ve zorunludur:** **önceki aktif sürüm varsa** önce mevcut `active` → `archived`, sonra taslak → `active`; ikinci adımda `activated_at` yazılır. Sırayı zorunlu kılan şey tek `active` kısmi benzersiz indeksidir. ⚠️ **İlk koşul teknik bir tutarlılık düzeltmesidir, açık karar değildir:** bir alt sektörün **ilk** paketinde arşivlenecek bir sürüm bulunmaz ve yalnız ikinci adım koşar (Bölüm 14.1).

**İki adımın tek işlem içinde yürümesi iki belgede de beklenir; statüleri farklıdır** (Bölüm 7.8'de kaydedilmiştir, burada tekrarlanmaz): biri bunu `[VARSAYIM]` etiketiyle yazar ve spec'te tek adımlık akış olarak kesinleşmesini ister; diğeri motorun zorunlu kontrol listesine *"aktivasyon işleminin veri tabanı değişmezini koruyacağı önceden doğrulanmalıdır"* maddesini koyar. ⚠️ **Burada iki ayrı açık karar vardır ve tek kaleme bağlanamaz.** Bir hakem ikisini kendi listesinde tek satırda anar (*"aktivasyon/rollback transaction ve yetkilendirme modeli"*); **ayrı seçilebilirler**, çünkü farklı şeyleri belirlerler: **(a) atomiklik** — iki adımın veri tabanında tek işlem olup olmayacağı, bir **teknik veri bütünlüğü** kararıdır; **(b) yetkilendirme modeli** — aktivasyon ve geri alma yetkisinin kime ait olduğu ve sunucu tarafında nasıl zorlanacağı, bir **rol, ürün ve risk** kararıdır. Biri alınıp diğeri açık bırakılabilir; ikisi de Bölüm 7.8'de görünür kılınmış, prosedürleri buraya bırakılmıştır. (b), rolün ikiye bölünmesi kararıyla **ilişkilidir ama aynı değildir**: orada rollerin **sayısı**, burada yetkinin **teknik olarak zorlanması** sorulur.

⚠️ **Onay anında base sürüm kontrolü ayrı bir karardır ve burada tekrar açılmaz** (Bölüm 7.8): motorun değerlendirdiği base `active` sürüm ile onay anındaki `active` sürüm farklıysa politika sonucunun **otomatik geçersiz** sayılması yalnız bir hakem belgesindedir. Kural benimsenirse aktivasyon işleminin **önüne** bir kontrol daha girer; benimsenmezse yukarıdaki iki adım değişmez. Transaction/yetkilendirme kararıyla **birlikte alınmak zorunda değildir**: biri işlemin bütünlüğünü, diğeri tabanın tazeliğini denetler.

#### Cache, indeks ve bağımlı çıktı etkisi

- **İndeks.** Tek `active` kısmi benzersiz indeksi yalnız bir garanti değil, aynı zamanda bir **sıra zorlayıcısıdır**: ters sırada denenen aktivasyon veya geri alma indeks ihlaliyle **reddedilir**. Bir hakem bunu açıkça yazar — yanlış sıra veri bozmaz, hata verir; diğeri aynı invariantı *"ihlal etmemek için işlem atomik olmalıdır"* biçiminde kurar. **Yön ortaktır.**
- **Önbellek.** Paket gövdesi marka başına sabit metin olarak Tier 2 bağlamında yaşar ve yalnız sürüm aktivasyonunda değişir; bu **ortaktır ve ortak kaynak karar dokümanında önbellek notu olarak yazılıdır**. ⚠️ **Aktivasyon sonrası geçersiz kılma davranışı açık karardır ve bu bölümde kapatılmaz:** bir hakem önbellek anahtarının paket kimliği/sürümünü içermesini **ya da** aktivasyonda ilgili önbelleğin kesin olarak geçersiz kılınmasını şart koşar (iş gerektirdiğini de yazar); diğeri paket Tier 2 bloğunun içinde yaşadığı için içerik değiştiğinde önbelleğin doğal olarak ıskalayacağını, **ek mekanizma gerekmediğini** `[VARSAYIM]` etiketiyle yazar ve ölçmediğini belirtir. İki konum **karşıttır**; Bölüm 10.5'te ele alınacak, karar ID'si Bölüm 17 sweep'inde verilecektir.
- **Paketsiz yol.** Paketsiz yolun önbellek anahtarı ve metni değişmemelidir — yalnız bir hakem belgesinde bu cümleyle yazılıdır; diğerinde ele alınmamıştır. İçerik olarak (a)/2'deki prompt kapısıyla aynı yöne bakar: paketsiz markada **modele gönderilen mevcut prompt parçaları byte-exact değişmez**.
- **Bağımlı çıktı — üretim sürüm damgası.** Aktivasyondan sonra üretilen postlar **yeni** sürüm damgasını taşır. Damganın gerekliliği ve gerekçesi **ortaktır**: kötü çıktının doğru paket sürümüne bağlanabilmesi. ⚠️ **Daha önce üretilmiş postların eski damgayla kalması ve geriye dönük değişmemesi ise yalnız bir hakem belgesindedir** — diğeri damganın izlenebilirlik gerekçesini taşır, **geçmiş postların değiştirilmezliği aynı hüküm değildir** ve o belgede ele alınmamıştır. Hiçbir katmanda geriye dönük yeniden yazma mekanizması tarif edilmemiştir. ⚠️ **Bu, K-07'ye indirgenemez:** K-07 damganın **veri yerini** sorar; buradaki soru, geçmiş postların geriye dönük **değiştirilip değiştirilemeyeceğidir** — bağımsız bir ürün ve veri davranışı kararıdır, ayrı seçilebilir ve **açık karardır**; karar ID'si Bölüm 17 sweep'inde verilecektir. **Damganın veri yeri — ayrı kolonlar mı mevcut bir JSONB alan mı — açık karardır (K-07)**; paketsiz üretimde ise geçerli bir paket ilişkisi bulunmaz, fiziksel temsili aynı karara bağlıdır.

#### Başarısızlıkta geri dönüş

İki adımın ilki başarılı olup ikincisi başarısız olursa sektörün **hiç aktif paketi olmadığı bir pencere** doğar; o pencerede üretim yapan marka paketsiz yola düşer. Paketsiz yolun kendisi ortak ve kaynak destekli bir emniyet davranışıdır (Bölüm 5, Bölüm 7) — **veri kaybı yoktur**.

⚠️ **İki belge bu pencereyi aynı biçimde değerlendirmez ve bu sentez ikisini tek cümleye indirmez:**

- Bir hakem sonucu **kabul eder ve gözlemeye bağlar**: davranış güvenlidir, ancak durumun loglanması gerekir.
- Diğeri sonucun **oluşmamasını** ister: *"ara durumda üretimin paketsiz yola düşmemesi için okuyucu davranışı ayrıca test edilmelidir."*

İkisi birbirini dışlamaz — biri gözlemlenebilirlik, diğeri test yükümlülüğü getirir; ikisi de tek hakem beyanıdır ve diğerinde ele alınmamıştır. **Bu bölüm ikisini de taşır, ama ikisi aynı statüde değildir.** ⚠️ Okuyucu davranışının test edilmesi **yeni bir doğrulama yükümlülüğüdür** ve tek hakem beyanıyla benimsenmiş sayılamaz: **benimsenip benimsenmeyeceği açık teknik karardır**, benimsenirse kapsamı Bölüm 13'te yazılır; karar ID'si Bölüm 17 sweep'inde verilecektir. Olay kaydı ise Bölüm 13.6'ya bağlanır. **Aktivasyon ve geri alma olayının loglanması ortaktır** — iki belge de zorunlu log listesine koyar; biri satırı *"aktivasyon ve rollback olayı"* olarak anar, diğeri alanlarını da yazar (*kim, ne zaman, hangi sürümden hangisine*). ⚠️ Bu **ortak** yükümlülük, onay/ret olayının **kimlik ve zaman damgasının** açık kararıyla (Bölüm 7.8) karıştırılmamalıdır: biri yürürlükteki bir gereksinim, diğeri henüz alınmamış bir karardır. Yarıda kalan aktivasyon riski Bölüm 18'de kayıtlıdır. **Ne testin kapsamı ne de log alanları bu bölümde tanımlanmamıştır.**

### 8.3 Rollback

- **Geri alınabilen birim: paket sürümü** — deploy değil, veri tabanı kaydı. **Yön ortaktır**, ve bu mimarinin geri alma maliyetini düşük tutan asıl özelliğidir: kod dağıtımı gerekmez.
- **Prosedür — ortak ve kaynakta karara bağlı:** (1) kötü sürüm `active` → `archived`, (2) önceki iyi sürüm `archived` → `active`. Sırayı tek `active` indeksi zorlar; ters sıra **indeks ihlaliyle reddedilir**. Ortak kaynak karar dokümanı bu prosedürü ilk sürümünde **tanımsız** bırakmış, 2026-07-11 ekinde bu sırayla yazmış ve *"spec'te tek adımlık akış olarak yazılmalı"* notunu düşmüştür — yerine geçen hüküm kesinleştiği için eski boşluk burada tekrar edilmez, karar geçmişinde tutulur (Ek B). ⚠️ **Geri almanın tek transaction olması ortak hüküm değildir:** yalnız bir hakem *"geri alma da tek operasyon/transaction olarak tasarlanmalıdır"* der; diğeri sırayı taşır ama **tek işlem** beklentisini açıkça **aktivasyon** için yazar. Kaynağın *"spec'te tek adımlık akış olarak yazılmalı"* notu da bununla aynı iddia değildir — biri **belgede tek akış**, diğeri **veri tabanında tek işlem** demektir. **Sonuç olarak burada üç ayrı açık karar vardır:** aktivasyonun atomikliği (8.2) · **geri almanın atomikliği** — tek hakem beyanı olduğu için aktivasyondan **ayrı seçilebilir** · yetkilendirme modeli (8.2).
- **Tetikleyici ve yetki.** Karar **yöneticiye/operatöre** aittir — **ortaktır**: bir belge bunu prosedürün içinde, diğeri rol tablosunda *"son aktivasyon/ret ve rollback kararı vermek"* satırıyla yazar. Tetikleyicinin **adlandırılması** yalnız bir hakemdedir: aktive edilmiş sürümün kötü çıktı üretmesi veya mevzuat hatası tespiti; aynı belge paketsiz markada tespit edilen bir prompt farkını *"pazarlıksız derhal geri al"* ölçütü yapar. Diğer belge geri almayı *"kötü bir sürümden geri dönüş"* ifadesiyle anar — yani tetikleyici kavramı orada da vardır, **adlandırılmış bir küme hâlinde yazılmamıştır**. **Bu bölümde tetikleyici kümesi kapalı ilan edilmez.**
- **Veri ve bağlı çıktılar ne olur?** Paket sürümleri **silinmez**; ham kanıt katmanı geri almadan hiç etkilenmez (salt-ekleme) — ikisi de ortak ve kaynakta onaylıdır. ⚠️ *Zaten üretilmiş postların geriye dönük değişmemesi* buna dâhil değildir: **yalnız bir hakem belgesinde** yazılıdır, diğerinde ele alınmamıştır ve **kendi açık kararıdır** (8.2). Kötü sürümle üretilmiş postların tespiti **üretim sürüm damgasına** bağlıdır: damga yoksa hangi postun hangi sürümden geldiği geriye dönük olarak güvenilir biçimde bulunamaz. Damganın gerekliliği iki belgede de yazılıdır; **veri yeri K-07'de açıktır** ve bir hakem bu bağı damganın Faz 1 gerekçesi olarak kaydeder.
- ⚠️ **Geri alma ile deaktivasyon aynı işlem değildir** (8.1): geri alma bir önceki **sürüme** döner ve paketli yol açık kalır; deaktivasyon paketli yolu kapatır. Deaktivasyonun desteklenen bir geçiş olup olmadığı açık karardır.

### 8.4 Bilgi kaybı ve geri ekleme

**Üç katmanlı güvence — ortak ve kaynakta yazılı** (kaynak karar dokümanının arşiv ve geri-ekleme bölümü, iki hakem belgesinde de aynı üç katmanla taşınmıştır):

1. **Yanlış çıkarma zorlaştırılır.** `cikar` kararı **pozitif kanıt + gerekçe** ister; kanıt yoksa karar uygulanmaz ve kalıp korunur (Bölüm 4.3, 7.7). ⚠️ Bu katmanın üçüncü ayağı — *onay ekranının ilk bölümünün çıkarılanların tam listesi olması* — yürürlükteki sentez görev sözleşmesinde **aynen** yazılıdır, ancak Bölüm 7.8'de tarif edilen onay yüzeyi aynı listeyi sayı ve eşik-üstü görünümüne indirir. **Fark Bölüm 7.8'de açık bırakılmıştır ve burada kapatılmaz;** eşik-üstü çıkarılanların eşiği de açık karardır.
2. **Tetikleyiciler insan hafızasına dayanmaz.** Her turda çıkarılanlar listesi hakem girdisine eklenir; daha önce çıkarılmış bir kalıp yeniden bulunursa **otomatik eklenmez** — eski çıkarma gerekçesi ile yeni kanıt yan yana **açık soruya** düşer. Onay yüzeyinde **son dört turun** çıkarılanlar özeti bulunur ve sürümler arası kalıp farkını gösteren bir teşhis yolu öngörülür. Son turların çıkarılanları **her senteze girdi olur** (Bölüm 7.5).
3. **Dürüst sınır — sıfır kayıp garantisi verilmez.** Verilen güvence, gözlemlenebilir değeri olan hiçbir kalıbın **sessizce** kaybolmamasıdır; izlenebilir değeri olmayan bir kalıp arşivde kalabilir. ⚠️ **Statü farkı kayda geçirilir:** kaynak doküman ve bir hakem bunu *garanti verilir* biçiminde yazar, diğer hakem aynı cümleyi *hedeflenir* biçiminde kurar. Bu sentez ikisini tek biçime indirmez. ⚠️ **Fark kayıt altına alınmakla kapanmaz:** bağlayıcı bir **garanti** ile bir **hedef** ürün ve risk seviyesinde farklı sonuç doğurur — biri kabul kriteri ve kanıt yükü üretir, diğeri üretmez. Hangisinin verileceği **açık karardır**, seviyesi ürün/risktir; karar ID'si Bölüm 17 sweep'inde verilecektir.

**Geri getirme yolu silme değil sürümdür.** Paket sürümleri ve karar günlüğü paketle birlikte arşivlenir; yanlış çıkarılmış bir kalıp geri getirilecekse bu, arşiv satırının değiştirilmesiyle değil **yeni bir sürümle** yapılır (Bölüm 6.5, 6.6). ⚠️ **Aktive edilmeden kalan taslakların akıbeti AYRI KARARLARDIR** — ***"bu bölümde ayrı bir karar açılmaz"** hükmü 2026-08-17'de **geri çekilmiştir**, çünkü **arşiv güvencesi hiç aktive edilmemiş taslağı kapsamaz** ve bağımlılık zinciri aktif sürümlerinkinden farklıdır.* Taslaklar **ayrı bir saklama kuralına mı bağlanır** — **K-142**; **o kuralın süresi** — **K-143** (koşullu). Aktif paket sürümlerinin süresi ayrıca **K-141**'dedir.

⚠️ **Güvencenin bilinen sınırı — iki belge karşıt konumdadır.** Geri-ekleme tespiti çıkarılanlar listesindeki **kalıp metnine** dayanır; metni değişmiş bir kalıp listeyle eşleşmeyebilir ve çelişki tetiklenmeden yeniden eklenebilir. Bir hakem bunu **kabul edilmiş bir zayıflık** olarak yazar ve kalıcı kalıp kimliğini kendi belgesinde sonraki faza bırakır; diğeri tam da bu nedenle sürümler arası **sabit kalıp kimliğini zorunlu** sayar ve metin hash'inin kimlik olamayacağını söyler. **Karşıtlık Bölüm 6.3'te kayıtlıdır ve açık karardır;** bu bölüm taraf tutmaz — ancak sonucu burada görünür olmalıdır: **ikinci katmanın tespit gücü doğrudan o karara bağlıdır.**

**Yöneticinin bu katmandaki rolü motorlu modelde değişir** `[SEA-2026-08-11]`**.** Bir hakem belgesi, yöneticinin çıkarılanlar listesini kalıp bazında yeniden sentezlemek zorunda olmadığını, özet diff ve kapı sonuçlarına bakarak **koşunun tamamını** onayladığını veya reddettiğini yazar; motorun kararları zaten kontrol etmiş olması varsayılır. Motorsuz modelde bu varsayım geçerli değildir — o modelde yönetici sentezin karar günlüğüne ve çıkarılanların tam listesine bakar (Bölüm 7.5, 7.8). Yürürlükteki model **motorlu modeldir** — ✅ **K-22 KAPANDI — A** (2026-08-21, Ek B).

---

## 9. Atama / yapılandırma akışı

[GEREKİRSE — kullanıcı, hesap, marka, tenant veya başka bir hedefe atama]

**Bu bölümün çekirdeği ortak ve kaynakta onaylı bir karardır:** *LLM önerir, kullanıcı teyit eder.* Ortak kaynak karar dokümanı bunu başlık düzeyinde **C kararı** olarak kaydeder ve iki hakem belgesi de akışı aynı kurulumla taşır. Bu bölümde ayrışma **karşıt konum düzeyinde değil, granülerlik ve statü düzeyindedir**; gerçek çelişki bulunmamıştır.

⚠️ **Kök kova invariantının koruma noktaları burada tekrar edilmez** — sektör listeleme ucunun kök-seviye filtresi, kök sektör çözücüsünün filtresi ve regresyon testi, trend katmanının mevcut bağışıklığı Bölüm 3.1 ve 3.3'te ele alınmıştır. Bu bölüm yalnız **atama akışının kendisini** yazar ve o korumalara **bağımlı** olduğu yerde atıf verir.

#### Atamayı kim, nereden yapar?

**Son sözü kullanıcı (marka sahibi) söyler; öneri modelden gelir.** Yüzey, marka oluşturma (ilk kurulum) ve marka ayarları ekranıdır; öneri **önceden seçili açılır liste** olarak gösterilir. İki hakem belgesi ve kaynak bu üçünde de aynıdır.

- **Bileşenin ekranlardaki kesin yerleşimi ve etkileşim tasarımı açık karardır (K-19)** — bir hakem bunu *"spec seansına"* bırakır, diğeri kendi açık karar listesinde ayrı madde olarak tutar, kaynak da *"ekran/uç nokta yerleşimi frontend'e göre"* der. Üç katman da **aynı yönde açıktır**; bu bölümde kapatılmaz.
- **Operatörün elle ataması ayrı bir yetki değil, kapsam kararının sonucudur:** mevcut markalar düşük hacimde elle atanır (aşağıda). Akışın kendisinde teyit mercii **kullanıcıdır**; bir hakem belgesinin ilkeler bölümünde geçen *"marka sahibi veya operatör"* ifadesi, aynı belgenin atama akışında **kullanıcı teyidine** indirgenir.
- **Sürtünme yasağı — ortak ve kaynakta yazılı:** içerik üretim akışına **soru eklenmez**. Atama yalnız kurulum ve ayarlar yüzeyinde yaşar.

#### Geçerli seçenekler nereden gelir?

**Aday listesi = yalnız `active` paketi olan alt sektörler.** Liste sorgudan gelir; modelin **serbest metin dönmesi yasaktır** — halüsinasyon kapısı bu kısıtla kapatılır. Öneri, mevcut web sitesi analiz çağrısına eklenecek bir alanla üretilir; çağrının kendisi ve sözleşmesi mevcuttur `[AKT·KAYNAK · 2026-07-11]`, eklenecek alan **yeni iştir**.

Model iki şey döndürebilir: **listeden bir aday** veya **boş**. Üçüncü bir dönüş biçimi yoktur.

⚠️ **Listenin büyümesiyle ilgili bir risk yalnız bir hakem belgesinde kayıtlıdır**, diğerinde ele alınmamıştır: alt sektör listesi büyüdükçe modelin aday listeden **seçim kalitesi** yeniden değerlendirilmelidir. Bu, hedeflenen sektör ölçeğine (**K-21**) bağlıdır ve **ölçülmemiştir**; bu bölümde eşik veya kabul kriteri üretilmemiştir, risk kaydı Bölüm 18'dedir.

⚠️ **Bu kısıtın bir yan sonucu vardır ve aşağıda ayrıca ele alınmıştır:** aday listesi aktif pakete bağlı olduğu için, paketi arşivlenmiş bir alt sektör listede **görünmez**.

**Web sitesi olmayan marka** (küçük işletmelerde yaygın) analiz çağrısından öneri alamaz. Geri düşüş yolu **ortak ve kaynakta yazılıdır**: kök sektör + marka adı ve açıklamasından aday önerilir — yine kullanıcı teyitli, yine yalnız aktif-paketli listeden, yine serbest metin yok. ⚠️ **Statü farkı:** bir hakem bu yolu karar verilmiş sayar (kaynak da öyle yazar), diğeri **uç nokta akışını** kendi açık karar listesinde tutar. Açık olan davranışın kendisi değil, **hangi uç noktanın nasıl çağrılacağıdır**; bu bölümde uç nokta akışı kesinleştirilmemiştir.

#### Varsayılan değer ve boş değer davranışı

**Varsayılan boştur.** Boş `sub_sector_id` mevcut üretim yolunu verir; paket yoluna girmeyen üretimlerde **modele gönderilen mevcut prompt parçaları byte-exact değişmez** (Bölüm 4.1). Kullanıcı öneriyi değiştirebilir veya alanı boş bırakabilir — **ortak**.

Devreye girme koşulu Bölüm 4.1'de yazılıdır ve burada tekrar edilmez: alan dolu **ve** atanan alt sektörün `active` paketi var. ⚠️ **Bu iki koşulun ikinci ayağı atama akışını doğrudan etkiler:** dolu bir alan tek başına paket yolunu garanti etmez.

⚠️ **Alanın yalnız alt sektör satırlarını kabul etmesinin veri tabanında mı uygulama katmanında mı zorlanacağı açıktır (K-08 (b)).** Kök ve alt satırlar aynı tabloda yaşadığı için bu, yabancı anahtarla kendiliğinden çözülmez (Bölüm 6.3); atama akışı bu kısıtın yokluğunda kök satır yazılmasına karşı korunmasızdır.

#### Bayat atama — paketi arşivlenmiş alt sektöre işaret eden kayıt

⚠️ **Bu bölümde ortaya çıkan çözülmemiş nokta.** İki hüküm ortaktır ve birlikte bir boşluk üretir: *(a)* aday listesi yalnız aktif paketli alt sektörleri içerir · *(b)* paket arşivlenirse üretim sessizce mevcut yola düşer (emniyet davranışı, Bölüm 4.1). Ancak **atama kaydının kendisine ne olacağı** — korunur mu, işaretlenir mi, kullanıcıya bildirilir mi — iki hakem belgesinde ve dokuz kaynak dosyada **arandı, tanımlayan hüküm bulunamadı** (harf duyarsız).

Sonucu somuttur: paketi arşivlenmiş bir alt sektöre atanmış marka çalışırken **emniyetli** davranır, ama kullanıcı alanı bir kez boşaltırsa **aynı alt sektörü yeniden seçemez** — liste onu artık içermez.

⚠️ **Bunlar tek karar değil, ayrı ayrı seçilebilen üç karardır** — biri alınıp diğeri reddedilebilir:

1. **Kaydın akıbeti** — `sub_sector_id` olduğu gibi **korunur mu**, yoksa boşaltılır mı? (Veri davranışı. Hiçbir katman söylemiyor; korunması bugünkü hükümlerden *çıkarsanabilir* ama **yazılı değildir**.)
2. **Bayat durumun sistemde işaretlenmesi** — kayıt korunuyorsa, işaret ettiği alt sektörün aktif paketi olmadığı **görünür kılınır mı**? (Teşhis ve gözlemlenebilirlik; 1 alınmadan anlamsızdır ama 1 alınıp bu reddedilebilir.)
3. **Kullanıcıya bildirim** — marka sahibine durum **bildirilir mi**? (Ürün/UX; 2'den bağımsız seçilebilir — içeride işaretlenip dışarıya hiç yansıtılmayabilir.)

Üçü de **açık karardır** ve **K-19'a indirgenemez:** K-19 bileşenin *nerede duracağını* sorar; bunlar *listede olmayan bir değere atanmış kaydın ne olacağını*. Karar ID'leri Bölüm 17 sweep'inde **ayrı ayrı** verilecektir.

⚠️ **Bu nokta Bölüm 8'in deaktivasyon kararına bağımlıdır:** deaktivasyon desteklenen bir geçiş olarak benimsenirse bayat atama **olağan bir durum** hâline gelir; benimsenmezse yalnız sürüm geçişleri sırasında ortaya çıkar. İki karar ayrı seçilebilir ama **birlikte değerlendirilmelidir**.

#### Toplu değişiklik / migration gerekir mi?

**Hayır — ortak ve kaynakta karara bağlı.** Veri tabanında bugün iki marka bulunduğu aktarılmaktadır `[AKT·KAYNAK · 2026-07-11]`; bunlar **elle** atanır. **Toplu geriye dönük atama başlangıç kapsamına alınmaz.**

**Yeniden ele alma koşulu yazılıdır ve korunur:** ölçek gerektirdiğinde **aynı model çağrısı toplu koşulur** — yani kapsam dışı bırakma kalıcı bir dışlama değil, ertelenmiş bir iştir. ⚠️ **Tetikleyici burada marka sayısı ve elle atama yüküdür, sektör sayısı değil**; eşiği **ölçülmemiştir** `[ÖLÇÜLMEMİŞ VARSAYIM]` ve bu bölümde uydurulmamıştır.

⚠️ **Dürüst kayıt — bu kalem çözülmedi ve adlandırılmış evi yok.** Ne marka sayısının veya elle atama eforunun **nerede ölçüleceği**, ne eşiğin **hangi belgede/fazda belirleneceği** hiçbir katmanda yazılıdır; pilotun ölçtüğü şey **tur başına yönetici süresidir**, marka atama eforu değil. *"Karar verilmiş kalemin ölçülmemiş tetikleyicisidir"* demek bu boşluğu kapatmaz. Kalem, **evsiz kapsam maddesi** olarak kaydedilir ve mevcut emsale göre (bakım borçları) Bölüm 17'de **kapsam kararı** olarak listelenir; ev verilip verilmeyeceği kullanıcı kararıdır.

#### Yanlış atama nasıl düzeltilir ve izlenir?

**Düzeltme yolu — yalnız bir hakem belgesinde açıkça yazılı, diğerinde ele alınmamıştır** (o belge de kullanıcının öneriyi değiştirebilmesini ve boş bırakabilmesini yazar, ama düzeltme akışını ayrıca tarif etmez): kullanıcı marka ayarları ekranından değeri değiştirir veya boşaltır; **sonraki üretim** yeni yola geçer. Geriye dönük bir işlem yoktur.

**İzleme, üretim sürüm damgasına dayanır:** hangi üretimin hangi paket sürümüyle yapıldığı damgadan okunur. ⚠️ Damganın **veri yeri K-07'de açıktır** (Bölüm 8.2); damga konmazsa yanlış atamanın geçmiş üretimlere etkisi geriye dönük olarak güvenilir biçimde izlenemez. Yanlış atamayı **tespit eden** bir sinyal veya metrik iki belgede de tanımlı değildir — düzeltme kullanıcının fark etmesine bağlıdır; bu bölümde ölçüt veya eşik üretilmemiştir.

#### Akış

```text
[Marka sahibi] → [site analizi VEYA marka adı + açıklaması]
      ↓
[Model: aktif paketli alt sektör listesinden SEÇ veya BOŞ dön — serbest metin yok]
      ↓
[Ekran: önceden seçili açılır liste — kullanıcı onaylar / değiştirir / boşaltır]   ← yerleşim K-19
      ↓
[brands.sub_sector_id yazılır veya NULL kalır]
      ↓
[Çalışma zamanı: alan dolu VE alt sektörün active paketi varsa paket yolu; aksi hâlde mevcut yol]
```

⚠️ **Diyagramdaki aday liste, Bölüm 3.3'teki kök-seviye filtresiyle karşılanmaz — ikisi ters kümelerdir.** O filtre mevcut **kök sektör** alanlarını korur (alt sektör satırları kök listesine sızmasın); buradaki aday liste ise **aktif paketi olan alt sektörlerdir**. Üç katman da listenin içeriğini aynı cümleyle tanımlar (*"yalnız aktif paketi olan alt sektörler; sorgudan gelir"*) ama **hangi sorgunun, hangi uç noktanın ve hangi veri sözleşmesinin bu listeyi üreteceği hiçbirinde yazılı değildir** (harf duyarsız tarandı). Bu **açık teknik karardır** ve **K-19'a da web sitesiz akışın uç nokta kararına da indirgenemez:** K-19 bileşenin yerini, diğeri öneri çağrısının akışını sorar; buradaki soru **listenin kendisinin nereden geldiğidir**.

⚠️ **Burada da tek soru yoktur, iki ayrı karar vardır:**

1. **Aday kümesinin kanonik üretimi** — kümeyi hangi sorgu/veri kaynağı **yetkili olarak** belirler (canlı sorgu mu, türetilmiş bir görünüm mü).
2. **Kümenin öneri çağrısına teslimi** — model, aday kümeyi hangi uç nokta ve hangi veri biçimiyle alır (mevcut site analizi sözleşmesinin genişletilmesi bu ayağa girer).
3. **Kümenin ekrandaki açılır listeye teslimi** — aynı küme kullanıcı yüzeyine hangi uç nokta ve biçimle taşınır.

⚠️ **2 ve 3 tek karar değildir:** iki tüketicinin **aynı taşıma mekanizmasını kullanması zorunlu değildir** ve hiçbir katman ikisini birbirine bağlamaz; biri mevcut sözleşmeye alan ekleyerek, diğeri ayrı bir liste ucuyla çözülebilir. Üçü de ayrı seçilebilir — kanonik küme tanımlanıp teslim ayakları uygulama spec'ine bırakılabilir. Karar ID'leri Bölüm 17 sweep'inde **ayrı ayrı** verilecektir.

---

## 10. Çalışma zamanı akışı

[GEREKİRSE]

**Bu bölüm içerik üretimi sırasındaki davranışı yazar.** Yolun karar diyagramı Bölüm 5.2'de, enjeksiyon yüzeylerinin bileşen envanteri ve kod çıpaları Bölüm 5.1'dedir; burada tekrar edilmez. Bu bölümün konusu o yüzeylerin **çalışma zamanındaki sırası, sınır durumları ve önbellek/maliyet davranışıdır**.

⚠️ **Kaynak statüsü dar tutulur.** Ortak kaynak karar dokümanında **onaylı karar olarak** yazılı olan, yerine-geçme kuralı ile `sub_sector_id` boş veya aktif paket bulunmayan hâlde bugünkü yolun aynen sürmesidir. **Okuma veya çözme hatasındaki geri düşüş bu kapsamın dışındadır:** iki hakemin ortak hükmüdür ama dokuz kaynak dosyada doğrulanmamıştır.

### 10.1 Seçim ve yükleme

**Seçim kuralı — ortak, üç adım.** Marka yüklenirken `sub_sector_id` okunur; boşsa mevcut yol kullanılır. Doluysa o sektör için `status = 'active'` paket okunur; paket bulunamazsa yine mevcut yol kullanılır.

**Sonuç en fazla tek satırdır.** Sektör başına tek `active` kısmi benzersiz indeksi (Bölüm 6.3) bunu **veri tabanı düzeyinde** garanti eder; *"hangi aktif sürüm"* belirsizliği çalışma zamanında oluşmaz.

**`draft` ve `archived` sürümler çalışma zamanında hiç okunmaz.** Bu cümleyle yalnız bir hakemde bulunur; diğerinde seçim koşulu `status = 'active'` olduğu için aynı sonuç **dolaylı olarak** doğar.

**Okuma başarısızlığında güvenli geri düşüş mevcut yoldur — iki hakemin ortak hükmü, kaynakta doğrulanmadı** `[BU SENTEZDE DOĞRULANMADI]`. Üretim bloklanmaz. **Paket atanmış** markada beklenmeyen eksiklik **gözlemlenebilir bir log** üretir; bu da ortaktır (bir belge *"gözlemlenebilir bir log üretmelidir"*, diğeri *"log'lanır — üretim durdurulmaz"* der).

⚠️ **Bozuk veya eksik paket içeriği — K-15 (a) açık; iki dal tarif edilmiş, aralarındaki sınır tanımsız.**

1. **Paket okunamıyor** (`content` bozuk veya sorgu başarısız) → **tüm yol** mevcut yola düşer, üretim bloklanmaz, log'a satır düşer.
2. **Çalışma zamanında bir alan eksikse** → yalnız **o alanın enjeksiyonu atlanır**, paket yolu sürer. Bu **yalnız bir hakemdedir** ve o hakem hükmü kendisi `[VARSAYIM]` etiketler: davranışın kaynak dokümanlarda yazılı olmadığını, fail-safe ilkesinden türetildiğini yazar ve K-15 (a)'ya bağlar.

Sınır sorusu şudur: şema doğrulayıcısı **yazımdan önce** çalışıyorsa (Bölüm 6.2), çalışma zamanında eksik bulunan bir alan zaten şema dışıdır — yani 2'nin tarif ettiği hâl 1'in tanımına da girer. **İki dalın sınırını tanımlayan hüküm bulunamadı** — iki hakem ve dokuz kaynak dosya harf duyarsız tarandı; bu sentezde davranış uydurulmamıştır. **K-15 üç atomik konu taşır**; ikisi bu bölümde ele alınır — bozuk/eksik içerik davranışı (burada) ve carousel'in ayrı yüzey olup olmadığı (10.3). **Üçüncüsü bir enjeksiyon yüzeyi sorusu değildir ve Bölüm 13'e devredilir:** gerçek marka/firma adı içerdiği için işaretlenmiş metnin **pakete girmemesi** kuralı ortaktır ve hakem görev sözleşmelerinde yazılıdır; açık olan, bu kuralın **otomatik denetiminin doğrulayıcıya eklenip eklenmeyeceğidir** — bir hakem bunu `[öneri]` olarak sızıntı testleri altında kaydeder. Burada ele alınmadığı için düşürülmemiş, evi adlandırılarak kayda geçirilmiştir.

**Bayat atama — çalışma zamanı tarafı kapalı, kayıt tarafı açık.** Paketi arşivlenmiş bir alt sektöre atanmış markada **dolu alan tek başına paket yolunu vermez**: aktif paket bulunamadığı için sistem mevcut yola düşer. Bu **emniyetli davranıştır ve ortaktır**; çalışma zamanı tarafında açık bir nokta bırakmaz. Kaydın akıbeti, bayat durumun işaretlenmesi ve kullanıcıya bildirimi Bölüm 9'da **üç ayrı açık karar** olarak kaydedilmiştir; burada tekrar edilmez.

### 10.2 Ana kullanım yolu

Karar diyagramı Bölüm 5.2'dedir. Aşağıdaki dizi, **paket yoluna girildikten sonraki enjeksiyon sırasını** verir:

```text
[Üretim isteği + (istenirse) özel gün seçimi]
      ↓
[Marka taze okunur → paket çözücü (10.1)]
      ↓
TIER 2  · paket bloğu kök sektör rehberinin YERİNE girer — yan yana yasak (4.1)
          bloğun başında dağarcık kullanım talimatı (Bölüm 4.6)
      ↓
TIER 3  · özel gün seçiliyse ve pakette karşılığı varsa dönem kalıpları eklenir
          eşleşmezse sessiz düşme + log   ← anahtar sözleşmesi K-01b
      ↓
GÖRSEL  · caption director'ın çıktı talimatına sektör görsel dili eklenir
          eşleşen özel günde günün görsel vurgusu aynı yolla koşullu eklenir
      ↓
VİDEO   · durağan kare: İKİ mod (metinden görsele + ürün referanslı düzenleme)
          hareket: paket havuzu ↔ mevcut sabit liste — K-02 açık
      ↓
[Üretim → post kaydı kullanılan paket sürümüne bağlanır — fiziksel temsil K-07]
```

**Dağarcık kullanım talimatı ortaktır ve kaynakta yazılıdır**: iki hakem de talimatın **bloğun başına** konmasını yazar. Talimatın metni ve gerekçesi Bölüm 4.6'dadır (**K-04**), burada tekrar edilmez.

**Marka-gerçeği filtresinin çalışma zamanı ayağı K-05'e bağlıdır — ✅ K-05 KAPANDI — B** (2026-08-21, kullanıcı kararı — Ek B). Kalıplardaki kanal bağımlılığı etiketi pakete taşınır ve silinmez (Bölüm 7.5); kullanım talimatının son satırı korunur ve **kanal envanteri Faz 1'de bu işte kurulur** — deterministik filtrenin envantere bağlanma biçimi spec'te tanımlanır (Bölüm 3.2).

**Hareket yüzeyi ayrıdır — ortak ve kaynakta düzeltme maddesi olarak yazılı.** Video hareket dilini `Industry` satırına yazmak videonun **hareketini etkilemez**; hareket komutu director'dan geçmez. ⚠️ **Seçenek kümesi korunur:** ortak kaynak doküman K-02 için **üç** teknik seçenek taşır — (a) paketli markada paket hareket havuzu, paketsizde mevcut sabit liste aynen *(kaynak önerisi)*; (b) hareket komutunu modele ürettirmek *(ek çağrı — maliyet ve gecikme yükü)*; (c) hareket dilini sonraki faza bırakıp paketin video kodlarını yalnız durağan kareye uygulamak. Küme Bölüm 17'ye üçüyle birlikte taşınır.

**Özel gün görsel vurgusunun koşulluluğu ortaktır** ve kaynakta *"yalnız gün eşleştiğinde aynı yolla"* biçiminde yazılıdır.

### 10.3 Alternatif kullanım yolları

**Fikir önerme ucu — ortak hüküm.** Aynı yerine-geçme kuralı bu uca da uygulanır; kapsanmazsa fikir önerileri kök rehberle, gerçek üretim paketle çalışır ve **aynı marka için iki farklı sektör sesi** doğar. Üç katman da aynı yöndedir; kural Bölüm 4.1'de yazılmıştır, çıpası Bölüm 5.1'dedir.

**Kısa video director'ın iki modu — ortak hüküm.** Sektör görsel dili hem metinden görsele hem de ürün referanslı düzenleme moduna eklenir. Kaynak bunu ayrıca **uyarı** olarak yazar; tek moda uygulamak yarım ayrışma üretir.

⚠️ **Carousel'in ayrı bir prompt yüzeyi olup olmadığı açıktır — K-15 (b).** Yalnız bir hakem bu satırı açar ve carousel'in caption/görsel hattını paylaştığını `[VARSAYIM]` etiketiyle, *"kaynak dokümanlarda ayrı yüzey olarak anılmıyor"* notuyla yazar. Diğer hakem carousel'i yalnız **çıktı örneklemi sınıfı** olarak anar — caption, carousel/görsel ve kısa video için ayrı küçük örneklem ister (Bölüm 13) — yani ayrı bir **üretim türü** olduğunu kabul eder ama ayrı bir **enjeksiyon yüzeyi** olduğunu söylemez. İki belge çelişmez; soru açık kalır ve bu sentezde yüzey uydurulmamıştır.

**Aday kümesinin iki teslim ucu — atama yüzeyinin çalışma zamanı.** Bölüm 9, aday alt sektör kümesi için üç ayrı açık karar kaydetti; kümenin **kanonik üretimi** orada kalır, **iki teslim ayağının uygulama tarafı** buraya düşer:

| Teslim ucu | Çalışma zamanı davranışı | Statü |
|---|---|---|
| **Öneri çağrısı** — model aday kümeyi alır | Küme çağrıya girer; model **listeden bir aday veya boş** döner, serbest metin yasaktır. Mevcut site analizi sözleşmesinin genişletilmesi bu ayağa girer | Davranış **ortak**; **hangi uç nokta ve hangi veri biçimiyle** taşınacağı açık karardır (Bölüm 9) |
| **Açılır liste** — kullanıcı yüzeyi aynı kümeyi alır | Öneri önceden seçili gelir; kullanıcı değiştirebilir veya boşaltabilir | Davranış **ortak**; taşıma sözleşmesi açık karardır. ⚠️ **Öneri çağrısıyla aynı mekanizmayı kullanması zorunlu değildir** — ayrı bir liste ucuyla da çözülebilir (Bölüm 9) |

⚠️ **İkisi de içerik üretim hattının dışındadır** — içerik üretim akışına soru eklenmez (sürtünme yasağı, Bölüm 9), bu yüzden üretim yolu aday kümesini hiç okumaz. Buraya **bu bölümün kapsamında** girmelerinin nedeni ikisinin de çalışma zamanı yüzeyi olmasıdır. Karar ID'leri Bölüm 17 sweep'inde verilecek; uç nokta tasarımı uygulama spec'ine aittir.

### 10.4 Legacy / fallback yolu

**Mevcut yolun çalıştığı üç koşul — birleşik küme.** (a) `sub_sector_id` boş; (b) atanan alt sektörün aktif paketi yok; (c) paket okuma veya çözme hatası. İlk ikisi iki belgede de sayılır; üçüncüsünü bir belge ayrı koşul olarak sayar, diğeri *"paket okuma başarısızlığında güvenli fallback mevcut yol olmalıdır"* biçiminde yazar — **aynı hüküm**.

**Eski davranışın değişmediği Katman-1 prompt kapısıyla kanıtlanır.** Karşılaştırma **değişiklik öncesinde dondurulmuş prompt fixture'ına** karşı, byte-exact yapılır; kanıtlanan şey LLM çıktısı değil, modele gönderilen prompt metnidir (Bölüm 2.3, Bölüm 13).

⚠️ **Kapının kapsadığı yüzey kümesi iki belgede aynı değildir — üç katman hâlinde taşınır ve hiçbiri düşürülmez:**

| Küme | İçerik | Statü |
|---|---|---|
| **Ortak çekirdek** | Tier 1/2/3 caption parçaları · görsel director talimatı · video durağan karenin **iki modu** · hareket havuzu · **fikir önerme ucu** | İki belgede de |
| **İki belgede de var — farklı listede: post kaydı** | Paket yoluna girmeyen üretimde **geçerli bir paket ilişkisinin kurulmaması** | hüküm **iki belgede de** yazılıdır ve **kaynakta karara bağlıdır**; biri onu Katman-1 regresyon listesine, diğeri **başarı ölçütü ve iş kuralı** olarak yerleştirir. |
| **İki belgede de var — farklı listede: API/veri kontrolleri** | `GET /sectors` yanıtının kök listesi (filtre eklendikten sonra da aynı kök satırlar) · kök sektör çözücüsünün mevcut marka eşlemeleri · trend katmanının alt sektör satırlarına bağışıklığı | üçü **ilk belgede de vardır** — orada *regresyon* listesinde değil, **veri bütünlüğü testleri** arasında sayılır. Çerçeveleme tamamlayıcıdır: ilk belge **kuralı** yazar (*"sızmaz · yalnız kök sektörleri eşler"*), diğeri **invariantı** (*"kök liste ve mevcut marka eşlemeleri değişmemeli"*). |

⚠️ **Bu bir katman sorusudur; bu bölümde çözülmez.** Son iki kümenin maddeleri **prompt metni karşılaştırması değildir** — biri veri tabanı kaydını, diğeri API yanıtını ve sorgu davranışını denetler. Kapının bu maddeleri **aynı byte-exact katmanda mı yoksa ayrı bir regresyon katmanında mı** taşıyacağı **Bölüm 13'ün konusudur**. Burada **kümelerin farklı listelendiği** kayda geçirilir; birleşik küme ve katman ataması **Bölüm 13.3'te sonuçlandırılmıştır.**

**Legacy kısa video yolu bu listeye K-06 sonucuna bağlı olarak girer — iki hakemde de koşullu.** Biri *"kapsama alınırsa"*, diğeri *"(K-06 kararına göre)"* yazar. ⚠️ **Ortak kaynak karar dokümanı ise koşul koymaz:** regresyon kapsamına fikir önerme ve legacy kısa video yollarının **ikisi de girmelidir** — ve aynı maddeyi **açık iş** olarak işaretler, yalnız **test tasarımını** spec seansına bırakır. **Bu bir kullanıcı kararı değildir:** kaynak gereksinimi ile iki hakemin koşullu yazımı arasındaki fark, K-06 kapandığında ve test tasarımı yazıldığında kapanır. ⚠️ **Ayrışma yalnız fixture listesindedir, ilkede değil:** Bölüm 4.1 mevcut davranışın korunmasını legacy yolları da kapsayacak biçimde **koşulsuz** kurar; buradaki koşulluluk yalnız **hangi yüzeyin kapı fixture'ına gireceğine** ilişkindir. Ayrışma **Bölüm 13'e** devredilir; bu bölümde yeni karar açılmamıştır.

⚠️ **Legacy kısa video yolunun akıbeti açıktır — K-06.** Yol bugün sektör rehberini slug yerine görünen adla aradığı için **zaten hep boş dönmektedir** ve ön yüz bu yolu çağırmamaktadır (çıpa: `posts.py:846-847`). Üç katman da aynı hükmü verir: yol **ya düzeltilir ya açıkça kapsam dışı notlanır — sessiz bırakılmaz.** Seçim ürün ve kapsam seviyesinde bir karardır; bu bölümde kapatılmaz.

**Kök rehber yolunun kaldırılma koşulu bu işin kapsamında tanımlı değildir.** ⚠️ Hüküm **yalnız bir hakem belgesindedir**, diğerinde ele alınmamıştır ve o belge de **kesinlik iddia etmez:** yol paketsiz markaların yoludur ve *"paket tüm sektörleri kapsayana kadar — **ve muhtemelen sonrasında da**"* yaşar. **Bu belgede kesinleştirilmez:** kapsamın tamamlanmasına kadar yolun yaşadığı ortak yöndür; **tam kapsam sonrasındaki akıbeti açık bir ürün/kapsam kararıdır.** Ölçüldü: dokuz kaynak dosya ve diğer hakem belgesi harf duyarsız tarandı — kök rehber yolunun kaldırılmasına ilişkin **tek isabet bu hedgeli cümledir**, karara bağlayan hüküm bulunamadı. Legacy kısa video yolunun akıbeti bundan ayrıdır ve **K-06**'dadır.

### 10.5 Önbellek ve performans

**Ortak ve kaynakta yazılı çekirdek**: paket gövdesi marka başına **sabit metin** olarak Tier 2 bağlamında yaşar ve **yalnız sürüm aktivasyonunda** değişir; Tier 2 bugün **tek önbelleklenen blok** olarak kurulmuştur.

⚠️ **Önbellek anahtarı ve aktivasyon sonrası geçersiz kılma — gerçek çelişki, açık karar.** Bölüm 4.4 ve Bölüm 8.2 bu kalemi buraya işaret etmişti; evi burasıdır ve **burada da kapatılmaz.** İki konum:

- **Konum A:** paket seçimi veya render edilmiş bağlam önbelleğe alınıyorsa, önbellek anahtarı **paket kimliği/sürümünü içermeli** ya da aktivasyonda ilgili önbellek **kesin olarak geçersiz kılınmalıdır**; bu belge bunun **iş gerektirdiğini** de yazar.
- **Konum B:** paket Tier 2 bloğunun içinde yaşadığı için içerik değişince önbellek **doğal olarak ıskalar**, **ek mekanizma gerekmez**. Bu belge hükmü `[VARSAYIM]` etiketler ve **ölçmediğini kendisi yazar**.

**Bu sentezde ölçülen — B'nin dayanağı paket hâlini kapsamıyor.** Konum B, adını verdiği bir kaynak bulgusuna dayanır; o bulgu kaynak dokümanda bulundu ve **iki önbellek katmanı** sayar: (1) marka önbelleği — **her marka/kit güncellemesinde** geçersiz kılınıyor ve üretim çağrısı markayı zaten taze okuyor; (2) model tarafındaki istem önbelleği — **içerik değişince kendiliğinden ıskalıyor**. ⚠️ **Birinci katmanın geçersiz kılma tetikleyicisi bir marka/kit güncellemesidir; paket sürümü aktivasyonu ise paket tablosunda iki adımlı bir durum güncellemesidir (Bölüm 8.2) ve marka satırına dokunmaz.** Bu, belgelerdeki aktivasyon adımlarından **okunan** bir sonuçtur; canlı sistemde ölçülmemiştir. Bulgunun doğduğu Marka DNA işinde bu boşluk oluşmuyordu, çünkü orada değişen alanlar **markanın kendi alanlarıydı**. Sonuç: B'nin ikinci katman için kurduğu argüman ayakta kalır, **birinci katman için devraldığı bulgu paket hâlini kapsamamaktadır.**

**Kararı belirleyecek olgu hiçbir katmanda yazılı değildir:** paket okuma sorgusunun veya render edilmiş Tier 2 bağlamının uygulama katmanında önbelleklenip önbelleklenmediği ve aktivasyonun herhangi bir geçersiz kılma yolunu tetikleyip tetiklemediği — iki hakem ve dokuz kaynak dosya tarandı, tanımlayan hüküm bulunamadı (harf duyarsız). Bu **ölçüm ihtiyacıdır ve ayrı bir karar açmaz**; açık kararın gerekçesine bağlanır. **Uzlaşma cümlesi üretilmemiştir**; iki pozisyon Bölüm 17'ye taşınır, karar ID'si sweep'te verilecektir.

**Paketsiz yolun önbelleği.** Paketsiz yolun mevcut önbellek anahtarı ve metni **değişmemelidir** — ⚠️ bu cümleyle **yalnız bir hakemde** bulunur, diğerinde ele alınmamıştır. İçerik olarak Katman-1 prompt kapısıyla aynı yöne bakar (10.4) ve Bölüm 8.2'de de kaydedilmiştir.

**Performans — tek hakem, ölçülmemiş.** Paketli yolda **üretim başına bir ek veri tabanı sorgusu** (paket okuma) bulunduğu ve paket metni sabit olduğu için **ek model çağrısı olmadığı** yalnız bir hakem belgesinde yazılıdır; diğeri performans başlığını hiç açmaz. İki hüküm de bu sentezde doğrulanmamıştır `[BU SENTEZDE DOĞRULANMADI]`.

⚠️ **Gecikme hedefi hiçbir katmanda yoktur — ölçüldü.** İki hakem ve dokuz kaynak dosya harf duyarsız tarandı; tek isabet, K-02'nin (b) seçeneğinin **maliyet ve gecikme** yükünü anan cümledir. Bir **hedef**, eşik veya bütçe hiçbir belgede bulunmamaktadır. Bu sentezde hedef uydurulmamıştır: **ölçülecek, eşik pilot kanıtından sonra belirlenecektir.**

⚠️ **Aşırı yük davranışı `[ÖLÇÜLMEMİŞ VARSAYIM]`.** Mevcut üretim hattının hız sınırı ve kuyruk davranışının değişmediği, paket okumanın ek yük yaratmadığı **yalnız bir hakem belgesinde** yazılıdır; diğer belgede ve dokuz kaynak dosyada karşılığı yoktur (0 isabet). Ölçülmemiştir ve bu bölümde kabul kriteri yapılmamıştır.

**Maliyet ölçümü — K-12.** Paket gövdesinin token maliyeti, paket için yazılan tavan ve önbellek eşiği lehte yan etkisi Bölüm 4.4'te `[ÖLÇÜLMEMİŞ VARSAYIM]` olarak kayıtlıdır; burada tekrar edilmez. ⚠️ **Bu bölümün eklediği kapsam:** bir hakem ölçüm ihtiyacını yalnız maliyetle değil, **önbellek eşiğiyle birlikte** ve *"uygulamada kullanılacak güncel model ve sağlayıcı üzerinden"* koşuluyla yazar. Ölçüm kapsamı K-12'ye bu genişlikte bağlanır; paket ve Marka DNA'sının **aynı bloğu ve aynı token bütçesini** paylaştığı ortak hükmü Bölüm 5.3'tedir.

---

## 11. Koşullu / özel akışlar

[GEREKİRSE]

Şablonun tekrarlanabilir **özel akış** bloğu aşağıda **altı akış** için açılmıştır.

Kaynak katmanı bu bölümde **belirleyicidir**: dört tür etiketinin davranış tanımı, eşleşmezlik kuralı ve acil güncelleme hükmü **kaynakta yazılıdır**; iki hakemin aynı cümleyi taşıması bağımsız doğrulama değildir.

### 11.1 Özel gün akışı (Tier 3)

- **Tetikleyici:** Kullanıcı üretim ekranında bir özel gün seçer. Ön yüzün gün adını göndermesi, kaynak tablo ve kategori kümesi `[AKT·KAYNAK · 2026-07-11]`; takvimde **yalnız 2026 yüklüdür ve 22 kayıt vardır** `[AKT·KAYNAK · 2026-07-11]`.
- **Ek girdiler:** Paketin özel gün bloğundan o dönemin alanları — tür etiketi, mesaj ekseni, kanca kalıpları, CTA kalıpları ve görsel vurgu. *(Ortak; alan kümesi Bölüm 6.2'de.)*
- **Ana akıştan farkı:** Mevcut özel gün bağlamı bloğuna **dönemin kalıpları eklenir**; **blok yapısı değişmez.** *(Ortak.)*
- **Çakışma/öncelik kuralı:** Tür etiketi ile sistemin mevcut kategori-ton mekanizması üst üste biner — **K-03 kapandı: paket türü üstündür**; ayrıntı 11.2'de.
- **Fallback:** Anahtar eşleşmezse **sessiz düşme + log kaydı.** Ortak ve **kaynakta onaylı karar**; **log zorunluluğu da ortaktır** — bir belge *"sessizce kaybolmamalı, log üretmelidir"*, diğeri *"sessiz düşme + log kaydı"* der.
- **Kabul senaryosu:** Eşleşen günde Tier 3'te dönem kalıpları görünür; eşleşmeyen günde blok değişmez ve log'a bir eşleşmezlik satırı düşer.

**Anahtar sözleşmesi — K-01b.** Tasarım varsayımı *"anahtar = sistem gün adının slug hâli, ayrı eşleme tablosu kurulmaz"* idi ve **canlı veriyle çakıştığı için çürütüldü** (geçmişi Ek B'dedir). Dört veri sorunu **üç katmanda da** kayıtlıdır — biri somut örneklerle, diğeri liste hâlinde:

| # | Sorun | Örnek |
|---|---|---|
| 1 | Bayramlar **gün bazlı ayrı satırlar** | arife ve numaralı günler ayrı kayıtlar |
| 2 | Adlar **resmî uzun formda** | ulusal bayramların tam resmî adları |
| 3 | Sistemdeki ad ile brief'teki dönem adı **ayrışıyor** | kasım indirim dönemi sistemde farklı adla |
| 4 | Bazı aday dönemler takvimde **hiç yok** | 10 Kasım · Öğretmenler Günü · okula dönüş |

⚠️ **Özelliğin ön koşulu — çelişkinin bir ayağı KAPANDI.** Bir hakem *"normalize/slug sözleşmesi **ve** kategori–tür önceliği kesinleşmeden özel gün eşleşmesi **uygulanmamalıdır**"* demişti; diğeri yalnız **anahtar sözleşmesini** bloklayıcı sayıyordu. **Kategori–tür önceliği 2026-08-17'de karara bağlandı (K-03, yukarıda)**, dolayısıyla iki pozisyon arasındaki fark bu ayakta **konusuz kalmıştır**. ⚠️ **Ön koşul tümüyle kalkmaz:** özel gün eşleşmesinin uygulanabilmesi **yalnız K-01b'ye** bağlıdır ve o karar **hâlâ açıktır**.

**Dört tür etiketinin dalları — kaynakta tanımlı**. Dördü de kaynakta (brief şablonunda) tanımlı olduğu için **kayıp riski burada kapatılır:**

| Tür | Davranış |
|---|---|
| `ticari-firsat` | Satış odaklı iletişim doğal karşılanır — ticari mesaj, kanca, CTA ve görsel vurgu |
| `karma` | Kutlama ile ölçülü ticari birlikte işler |
| `kutlama` | Satış çağrısı kültürel olarak eğreti kaçar → **CTA yerine kutlama kalıbı** |
| `anma` | Kutlama **ve** satış dili ikisi de uygunsuz → yalnız saygı çerçevesi, ya da *"içerik önerilmez"* |

Etiket **tektir**; kararsızlıkta bile tek etiket seçilir ve tereddüt gerekçeye yazılır *(kaynakta yazılı brief kuralı; girdi kapısı tarafı Bölüm 7.3'te)*.

### 11.2 Tür etiketi ↔ kategori-ton çakışması

- **Tetikleyici:** Gün eşleşti **ve** pakette o dönemin tür etiketi var.
- **Ek girdiler:** Sistem takviminden günün **kategorisi**; paketten o dönemin **tür etiketi**. Tür etiketi paket içerik sözleşmesinde **her dönem için zorunludur ve tektir** — üç katmanda da yazılı.
- **Ana akıştan farkı:** Sistem bugün **gün kategorisine göre** bir ton talimatı basmaktadır `[AKT·KAYNAK · 2026-07-11]`; paket tür etiketi **ikinci bir ton sürücüsü** olur ve iki mekanizma üst üste biner.
- **Çakışma/öncelik kuralı — K-03 KAPANDI, kullanıcı kararı (2026-08-17).** **Gün eşleşmesi olan bir dönemde paketin tür etiketi üretim davranışında üstündür.** Sistemin takvim **kategorisi korunur** ve günün **kimliği ile doğrulanması** için kullanılır; kategori bloğu **basılmaya devam eder**, paket kısıtı üstündür. ⚠️ **Karar, üç katmanın da taşıdığı öneriyle aynı yöndedir — ama artık öneri değil, karardır.** Ortak-mod uyarısı (2.1 md.1) kararın kendisini değil, **önerinin kanıt ağırlığını** ilgilendirir: kararın dayanağı üç katmanın hemfikirliği değil, **kullanıcı tercihidir**. ⚠️ **Kararın kapsamı dardır:** yalnız tür ↔ kategori çatışmasını çözer. **Mevzuat çatışması, kapsam tercihi ve motorun karar veremediği öteki maddeler bundan etkilenmez**; genel bir *"koşuyu blokla"* kuralı kurulmaz ve **K-23 kapanmaz.** ⚠️ **Sözleşme ayağı henüz yansımamıştır** — yürürlükteki sentez görev sözleşmesi bu çatışmada hâlâ *"kararı verme, açık soruya düşür"* der; düzeltme **sürümlü bir supersession** olarak Bölüm 14.4'te kayıtlıdır.
- **Fallback:** ⚠️ **Tür etiketinin eksik olduğu hâl bu bölümde kesinleştirilmez — K-15 (a)'nın kapsamındadır.** Etiket sözleşmede zorunlu olduğu için, çalışma zamanında bulunmaması **eksik/bozuk paket içeriği** hâlidir ve Bölüm 10.1'de iki dalın sınırı **açık karar** olarak kaydedilmiştir: paket okunamıyorsa tüm yol geri düşer, yalnız bir alan eksikse o alanın enjeksiyonu atlanır. Bir hakem bu akış için *"tür etiketi yoksa mevcut kategori-ton mekanizması tek başına çalışır"* der — bu, iki daldan **ikincisinin** bu alana uygulanmış hâlidir; **yalnız o hakemdedir** (diğer hakemde ve dokuz kaynak dosyada **0 isabet**, harf duyarsız) ve **K-15 (a) kapanmadan bugünkü davranış diye normatifleştirilemez.**
- **Kabul senaryosu:** Eşleşen ve tür etiketi taşıyan bir günde üretilen içerikte tür etiketinin gerektirdiği dil gözlenir. ⚠️ **Etiketsiz gün için kabul senaryosu yazılmamıştır** — davranışı K-15 (a)'ya bağlıdır ve o karar kapanmadan ölçüt üretilemez.

⚠️ **Mevcut bir veri tutarsızlığı pakete miras kalır — kaynakta ve yalnız bir hakemde; diğer hakemde ele alınmamıştır.** Yılbaşı sistem takviminde **ulusal** kategoriyle kayıtlıdır, oysa prompt katmanındaki örnekler o günü **ticari** anlatmaktadır `[AKT·KAYNAK · 2026-07-11]`. Kaynak bunun düzeltilmesini **ayrı bir bakım maddesi** sayar. ⚠️ **Dürüst kayıt — ölçüldü:** bu bakım maddesinin **adlandırılmış evi yoktur.** Dokuz kaynak dosya, iki hakem belgesi ve çalışma dosyası harf duyarsız tarandı: kalem kaynakta ve **yalnız bir hakemde** kayıtlıdır (diğer hakemde **0 isabet**), ikisi de yalnız *"ayrı bakım maddesi"* der; onu bir faza, plana veya iş kalemine bağlayan hüküm **bulunamadı** ve Bölüm 3.2'nin üç maddelik bakım borçları listesinde **yer almamaktadır**. **Evsiz kapsam maddesi olarak kaydedilir** ve mevcut emsale göre Bölüm 17'de **kapsam kararı** olarak listelenir; ev verilip verilmeyeceği kullanıcı kararıdır.

### 11.3 `anma` ve `kutlama` kısıtı — paketin geçersiz-kılıcı yetkisi

- **Tetikleyici:** Eşleşen günün tür etiketi `anma` veya `kutlama`.
- **Ek girdiler:** Dönemin **tür etiketi** ve CTA alanı — ⚠️ bu iki türde CTA alanı **kutlama-saygı kalıbını taşır**; alanın kendisi kaybolmaz, içeriği değişir. Kural brief biçim sözleşmesinde yazılıdır.
- **Ana akıştan farkı:** İkisinde de CTA yerine **kutlama-saygı kalıbı** ve *"satış çağrısı kullanma"* satırı gelir; `anma`da ayrıca **içerik kısıtı** vardır. *(Ortak ve kaynakta yazılı.)*
- **Çakışma/öncelik kuralı:** ⚠️ **Açık karardır ve Bölüm 4.6'da kaydedilmiştir; burada yeniden açılmaz.** Bir belge bu kısıtı paketin **tek** geçersiz-kılıcı yetkisi sayar ve kullanıcı satış dili istese bile üstün tutar; diğeri kısıtı koşulsuz yazar ama öncelik düzeninde kullanıcının somut isteğini paketin üstüne koyar ve pakete istisna tanımaz — **o belge bu noktada kendi içinde tutarsızdır**, bu yüzden konu iki pozisyon olarak taşınamaz.
- **Fallback:** Tür etiketi yoksa 11.2'nin fallback'i geçerlidir.
- **Kabul senaryosu:** `anma` etiketli bir dönem eşleştiğinde üretilen içerikte satış **ve** kutlama dili bulunmaz; yalnız saygı çerçevesi görülür veya içerik önerilmez. ⚠️ **Senaryonun gerçek takvim günüyle kurulabilirliği sınırlıdır** — aşağıya bakınız.

⚠️ **Bilinen boşluk — kaynakta verilen ana örnek bugünkü veriyle tetiklenemez.** `anma` türünün kaynaktaki örneği **10 Kasım**'dır; bu gün ile Öğretmenler Günü ve okula dönüş **sistem takviminde bulunmamaktadır** (11.1, sorun 4) — bu **ölçülmüş bir olgudur** ve üç katmanda da kayıtlıdır. **Buradan akışın tümüyle tetiklenemez olduğu sonucu ÇIKMAZ:** hiçbir katman `anma` etiketinin yalnız bu günlere verilebileceğini söylemez (harf duyarsız tarandı, **dışlayan hüküm bulunamadı**); sentez mevcut takvimdeki başka bir dönemi de `anma` etiketleyebilir ve doğrulama fixture üzerinden kurulabilir. **Ölçülmüş olan dar iddiadır:** kaynağın verdiği ana örnek bugünkü takvim verisiyle **çalışma zamanında oluşmaz**. **K-01a** — takvime bu günlerin eklenip eklenmeyeceği — kaynakta açıkça sorulan bir **operatör kararıdır** ve eklenirse takvim beslemesinin yıllık işine de işlenmesi gerekir; bu karar **ana örneğin gerçek günle gösterilebilmesini** belirler, `anma` akışının test edilebilirliğinin tamamını değil (Bölüm 13).

### 11.4 Görsel ve video dağarcığı akışı

- **Tetikleyici:** Paketli markada görsel veya kısa video üretimi.
- **Ek girdiler:** Görsel kodlar, video kodları (hareket ve sahne alt listeleri) ve gün eşleştiyse dönemin **görsel vurgusu**.
- **Ana akıştan farkı:** Dağarcık, caption director'ın çıktı talimatına ve kısa video durağan kare prompt'una **iki modda da** eklenir; enjeksiyon yüzeyleri ve çıpalar Bölüm 5.1'de, sıra Bölüm 10.2'dedir. **Görsel vurgu yalnız gün eşleştiğinde aynı yolla eklenir** — ortak ve kaynakta yazılı.
- **Çakışma/öncelik kuralı:** Dağarcık **ek bağlamdır, geçersiz-kılıcı değildir**; tek istisna 11.3'tür. Bu ilkenin tek başına iki riski önlemediği — listeyi tamamlama refleksi (**K-04**) ve marka-gerçeği filtresinin yokluğu (**K-05**) — Bölüm 4.6'da işlenmiştir.
- **Fallback:** Faz 1 önlemi, her enjeksiyon bloğunun başına konan sabit kullanım talimatıdır (Bölüm 4.6). ⚠️ **Dürüst sınır — iki hakemde de yazılı:** bu bir **talimattır, deterministik filtre değildir**. ✅ **K-05 KAPANDI — B** (2026-08-21, Ek B): kanal envanteri **Faz 1'de bu işte kurulur**; filtrenin envantere bağlanma biçimi spec'te tanımlanır.
- **Kabul senaryosu:** Görsel prompt çıktısında sektör dağarcığı gözlenir; dağarcığın **tamamı değil bir alt kümesi** kullanılmıştır ve markanın sahip olmadığı bir kanal önerilmemiştir. ⚠️ **Bu bir Katman-2 gözlemidir, otomatik kapı değildir:** prompt'ta bloğun **bulunup bulunmadığı** deterministiktir ve Katman-1'e aittir (Bölüm 13); alt küme kullanımı ve kanal uygunluğu **kalite sinyalidir** ve otomatik red eşiği **K-11 (b)** kapanmadan tanımlanmaz.

### 11.5 Video hareket dili akışı

- **Tetikleyici:** Paketli markada kısa video üretiminin hareket aşaması.
- **Ek girdiler:** Paketin **video kodları** alanının **hareket alt listesi**; sahne alt listesi bu akışa değil durağan kare yüzeyine gider (11.4). İki alt listenin ayrımı ve nihai alan adları **K-02**'ye bağlıdır (Bölüm 6.2).
- **Bugünkü durum:** Hareket komutu **director'dan geçmez**; sabit bir havuzdan rastgele seçilir. `Industry` satırına yazılan hareket dili yalnız **durağan kareyi** etkiler. *(Ortak ve kaynakta düzeltme maddesi olarak yazılı.)*
- **Ana akıştan farkı ve seçenek kümesi:** **K-02** açıktır; üç seçenek Bölüm 10.2'de korunmuştur, burada tekrar edilmez.
- **Çakışma/öncelik kuralı:** Paket hareket havuzu ile mevcut sabit liste arasındaki seçim **yalnız paket yoluna girildiğinde** doğar; paket yoluna girmeyen üretimde mevcut liste **aynen** korunur (Bölüm 4.1) — bu öncelik **ortaktır ve kaynakta yazılıdır**. Havuzlar **birlikte kullanılmaz**; ikisinden biri seçilir. ⚠️ Seçimin hangi yönde yapılacağı **K-02**'de açıktır.
- **Fallback:** Paket hareket havuzu **boşsa mevcut sabit listeye düşülür.** ⚠️ Bu kural **yalnız bir hakemdedir**; diğer hakem belgesinde ve dokuz kaynak dosyada **0 isabet** (harf duyarsız). Yönü fail-safe ilkesiyle uyumludur ama **çözülmüş sayılamaz** (2.6 ikinci sınırı) — K-02'nin (a) seçeneği benimsenirse bu dalın da karara bağlanması gerekir.
- **Kabul senaryosu:** Paket yoluna girmeyen üretimde hareket havuzu **byte-exact** aynıdır; bu, Katman-1'in ortak çekirdeğindedir (Bölüm 10.4).

### 11.6 Tur dışı acil güncelleme

- **Tetikleyici:** Periyodu bekleyemeyecek bir olay — kaynakta verilen örnek **mevzuat değişikliğidir**.
- **Ek girdiler:** ⚠️ **Ayrı bir girdi kümesi hiçbir katmanda tanımlanmamıştır** (harf duyarsız tarandı). Akış mevcut aktif paketi ve değişikliğin kanıtını kullanır; **karar günlüğünün kanıt satırını taşıması** yalnız bir hakem belgesinde yazılıdır.
- **Ana akıştan farkı — ortak çekirdek dardır:** ⚠️ **Ayrı bir mekanizma gerekmez** ve güncelleme **periyodun dışında** yapılabilir; aynı taslak → aktif mekanizması her an koşulabilir. Bu **kaynakta onaylı karardır** ve kaynak *"spec'te bir cümleyle anılması yeterli"* der. Bir hakem bunun **aşağı akışını** ayrıca yazar: **sentez → politika motoru → yönetici son onayı → aktif** zinciri tur dışında koşturulabilir — yani **sentez zincirin içinde kalır**. *"Tur dışı"* burada **periyodu beklememek** demektir.
- ⚠️ **Tam araştırma turunun atlanabilmesi ortak hüküm DEĞİLDİR — açık karardır.** Yalnız bir hakem, tam tur (üç araç araştırması) koşulmadan da sentezin **elle düzeltilmiş** bir taslak üretebileceğini yazar ve karar günlüğünün kanıt satırını taşımasını ister. **Kaynak bunu söylemez** (yalnız mekanizmanın periyot dışında yeniden kullanılabildiğini söyler) ve diğer hakem **ele almaz** — sessizlik karşı görüş olmadığı gibi onay da değildir. Açık olan soru şudur: **acil güncellemede tam araştırma turu zorunlu mudur?** Bu, motorun atlanması sorusu değildir ve **K-22'den ayrı seçilebilir** — motor ilk fazda olsa da olmasa da araştırma turunun zorunluluğu ayrıca kararlaştırılır.
- **Çakışma/öncelik kuralı:** Acil olmak **onay kapısını ve sıra kuralını kaldırmaz**; taslak → aktif sırası ile yönetici son onayı korunur. *(Bir belge onay adımını bu akış için açıkça yazar; diğeri akışı aynı taslak → aktif mekanizmasına bağlar ve o mekanizmanın onay kapısı Bölüm 8'de ortak hükümdür.)* ⚠️ **Aşağı akış motoru içerir** — motor **Faz 1'de** olduğundan (✅ **K-22 KAPANDI — A**, Ek B) motorlu ön koşul zinciri geçerlidir (Bölüm 8; motorsuz zincir K-22 kapanışıyla yürürlük dışıdır). Bu, K-22'nin sonucudur; **bu bölümde yeni bir karar açılmamıştır.**
- **Fallback:** ⚠️ **Yukarıdaki açık karara bağlıdır ve burada kesinleştirilmez.** Kesin olan: hangi yol seçilirse seçilsin **sürüm yine taslak olarak yazılır ve onaydan geçer** — mekanizma atlanmaz. Turun atlanabildiği dal **tek hakemin hükmüdür**; benimsenirse kanıtın karar günlüğünde nasıl taşınacağı da o kararla birlikte belirlenir.
- **Kabul senaryosu:** Kuyumculuk mevzuatındaki tarihli değişiklik — kaynak, pakete **iki tarihli** yazıldığını ve yürürlük tarihinden sonra sadeleştirileceğini kaydeder. Bir hakem bunu **sürüm mekaniğinin ilk gerçek kullanımı** olarak öngörür; bu bir beklentidir, ölçüm değildir `[ÖLÇÜLMEMİŞ VARSAYIM]`.

---

## 12. İlişkili sistemler ve veri sahipliği

[GEREKİRSE]

#### Sistem sınırı — Marka DNA'sı ayrı ve onaylı bir iştir

**İki sistem iki ayrı soruyu yanıtlar:** sektör paketi *"bu sektörde genellikle nasıl konuşulur ve nasıl görünür"*, Marka DNA'sı *"bu marka sektör ortalamasından nasıl ayrılır"*. Ayrım kaynakta ilke düzeyinde yazılıdır ve iki hakem belgesinde de aynıdır.

Bu ayrımın iki yönlü sonucu **ortak hükümdür** ve Bölüm 4.4'te yazılmıştır; burada yalnız sınır olarak anılır:

- Markaya özgü sapma DNA'da, sektör ortalaması pakette yaşar — aynı bilgi iki katmandan basılmaz.
- Ters yön de yazılıdır: sektör paketindeki genel bilgi DNA'ya **kopyalanmaz**, ve DNA çıkarımı yapılırken aktif paket **yalnız kontrast referansıdır, içerik kaynağı değildir**. Kaynak bunu *"onaylandı"* başlıklı bir karar olarak taşır.

⚠️ **Marka DNA'sının kendi alan kararları bu belgeye ait değildir.** Alan seti, doldurma akışı ve enjeksiyon ayrıntısı ayrı ve onaylı bir işin kararlarıdır (Bölüm 3.2); bu sentezde **kapsam kararı olarak Bölüm 17'ye taşınmazlar**. Bu bölüm yalnız **iki sistemin temas yüzeyini** yazar. Bir hakem belgesinin bu bölümde verdiği **alan-bazlı ev tablosu** (marka sesi nüansı, yasak kelimeler, hedef kitle, örnek postlar) Bölüm 3.2'de listelenmiştir ve burada tekrar edilmez.

⚠️ **Bağımlılık yönü — yalnız bir hakem belgesinde açıkça yazılı, diğerinde ele alınmamıştır:** DNA alanlarının doldurulmuş olması sektör paketi sisteminin kurulması veya paket güncellenmesi için **ön koşul değildir**. Hüküm kaynağın kendi tasarımıyla tutarlıdır (DNA alanlarının tamamı isteğe bağlıdır ve boş alan enjekte edilmez), fakat bu bölümde **tek hakem hükmü** olarak taşınır.

#### Sahiplik tablosu

| Bilgi / yetenek | Doğal sahibi | Bu projedeki kullanım | Senkronizasyon |
|---|---|---|---|
| Sektör taksonomisi (kök + alt sektör) | `social.sectors` (mevcut) | Alt sektör satırları **aynı tabloya** eklenir; ayrı tablo kurulmaz | Anlık — tek tablo |
| Marka → kök sektör eşlemesi | Kök sektör çözücü (mevcut kod) | **Kök seviyede kalır**; kök-seviye filtresi + regresyon testi **zorunlu iştir, henüz yazılmamıştır** (Bölüm 3.3) | Anlık |
| Trend katmanı | Trend önbelleği + Katman A sorgusu | **Dokunulmaz**; alt sektör satırı girmez | Değişiklik yok — mevcut kök-seviye filtresi zaten koruyor |
| Özel gün takvimi | `social.public_holidays` | `ozel_gun` anahtarlarının **tek doğruluk kaynağı**; **hedef modelde** çalışma zamanı eşleşmesinin dayanağı | Takvim **yıllık zamanlanmış bir iş** ile doluyor; **K-01a** alınırsa ekleme oraya da işlenir |
| Marka kimliği ve tonu | `brands.brand_kit` + **Marka DNA sistemi** | Paket sektör ortalaması, DNA marka sapması — **çift enjeksiyon yasağı** | Ayrı iş; **ortak Tier 2 bloğu ve ortak token bütçesi** (Bölüm 5.3) |
| Marka kanal envanteri | ✅ **K-05 KAPANDI — B** (2026-08-21, Ek B): envanter **bu işin Faz 1 kapsamında** kurulur; Marka DNA `channels` alan adayıyla sınır spec'te çizilir | Kanal-bağımlı kalıpların güvencesi; kullanım-talimatı düzeyi önlem korunur | Bu işin spec'i belirler |
| Prompt-düzeyi regresyon altyapısı | Bu işte kurulur; **paylaşımı açık karardır (K-20)** | Katman-1 kapısı. Kaynak, DNA tarafındaki regresyon işini *"bu altyapı kapsamalı, ikinci altyapı kurulmaz"* diye **bu yöne bağlar**; ⚠️ **hüküm burada kesinleştirilmez** — paylaşımın bağlayıcı olup olmayacağı **K-20**'de açıktır | Paylaşım benimsenirse ortak kod yolu — **K-20**'ye bağlı |
| Kök sektör rehberi metni | Prompt katmanı (mevcut) | Paketsiz markaların yolu; ayrıca **sentezin girdisi** (nüans kaybı önlemi) | Elle |
| `brands.sector` (TEXT) | Mevcut kod — **7+ okuma noktası** | Bu işte **dokunulmaz**; ama spec onun **canlı bir girdi** olduğunu bilmelidir | Yok |
| Post kayıtları | `posts` | **Hedef karar:** üretim anında paket sürüm damgası yazılır; **damganın veri yeri K-07'de açıktır** ve damga bugün kurulmamıştır | Üretim anında (hedef) |
| Uzun / zengin marka bilgisi (ürün detayı, marka hikâyesi) | Doküman + geri getirme katmanı | Ne pakete ne DNA alanlarına taşınır — kaynakta ilke düzeyinde yazılı | Yok |
| Araştırma artefaktı ↔ araç/kaynak eşlemesi | **AÇIK** — bir hakem *"yalnız operatörde"*, diğeri kalıcı veri alanı der | ⚠️ **Tek tasarım kararı DEĞİL, iki ayrı karardır:** kalıcı kayıt **K-138** · okuma yetkisi **K-139** (Bölüm 6.2 ve 7.4'te işlendi) | Karara bağlı |

⚠️ **Bu tablo yeni koruma veya yeni iş üretmez.** Kök kova invariantının koruma noktaları Bölüm 3.1/3.3'te, veri modeli Bölüm 6'da, çalışma zamanı yolu Bölüm 10'da yazılmıştır; buradaki satırlar **sahiplik ve senkronizasyon açısından** aynı hükümlere işaret eder.

⚠️ **Tablo kapalı bir küme değildir** — iki hakem belgesi de kendi tablosunu temas yüzeyinin örnekleriyle kurar, sınırlayıcı bir sayım vermez. Aşağıdaki iki liste için de aynısı geçerlidir.

#### Tek doğruluk kaynağı çakışmaları

**1. Özel gün adları — sistem kazanır.** Brief'in aday takvimi **günlük dildedir**, sistemdeki adlar resmî/farklı biçimdedir. Doğruluk kaynağı **sistem takvimidir**; sentez **uydurma anahtar üretemez** ve sistemde karşılığı olmayan dönemi pakete koyamaz — yalnız karar günlüğüne notlar. Üç katmanda da yazılıdır. ⚠️ Anahtarın **biçimi** (normalize/eşleme sözleşmesi) **K-01b**'de açıktır; notun karar günlüğünde nasıl temsil edileceği Bölüm 6.5'te açık kararlardan biridir.

**2. Ton sürücüsü — iki sürücü, kural KARARA BAĞLANDI.** Sistemdeki dönem kategorisi ile paketteki tür etiketi aynı üretimi iki yönden sürükleyebilir; **çatışmada paketin tür etiketi üstündür** (**K-03**, 2026-08-17 kullanıcı kararı — Bölüm 11.2). Kategori korunur ve günün kimliği ile doğrulanması için kullanılır. ⚠️ **Kapanmayan tek ayak sözleşme metnidir:** yürürlükteki sentez görev sözleşmesi çelişki hâlinde sentezciye hâlâ **karar vermeyi yasaklar** ve açık soruya düşürtür; bu **drift'tir, açık karar değildir** ve düzeltmesi Bölüm 14.4'te kayıtlıdır. ⚠️ Sistemin **kendi içinde** de bir tutarsızlık kayıtlıdır — Yılbaşı takvimde bir kategoriyle, prompt katmanındaki örneklerde başka bir anlamda geçer; kaynak ve bir hakem bunu *"ayrı bakım maddesi"* der, **hiçbiri bir faza, plana veya iş kalemine bağlamaz** (Bölüm 11.4). **Kalem çözülmemiştir**; belge akıbeti **kullanıcı onaylıdır** — Bölüm 17'de **kapsam kararı** olarak taşınır. Bu akıbet ona bir ev verir; **alttaki bakım kararını kesinleştirmez.**

**3. Sektör bilgisi — paket varsa tek kaynak pakettir.** Kök rehber ile paketin **yan yana enjeksiyonu yasaktır**; kaynak bunu gerekçesiyle birlikte onaylı karar olarak yazar (Bölüm 4.1, 10.2). ⚠️ **Kök rehberin sentezin girdisi olması da onaylı bir karardır**, ancak yürürlükteki sentez görev sözleşmesinin girdi listesinde **bulunmaz**; bu bir **sözleşme driftidir**, yeni karar değildir ve karşılık gelen ek eklenene kadar resmî hakem turunu bloklar (Bölüm 7.5).

**4. Marka sesi — DNA kazanır.** DNA ile paket çatıştığında **DNA kazanır**; kaynak bunu ilke düzeyinde yazar ve iki hakem belgesi de aynıdır. Markaya özgü **yasak kelimeler** hiyerarşinin de üstünde **mutlak kısıttır**. ⚠️ **Hiyerarşinin orta basamaklarının sırası açık karardır** (Bölüm 4.6) — bu bölüm o sırayı kesinleştirmez; burada kesin olan yalnız **DNA > paket** ilişkisidir, iki belgenin sıralamaları bu ilişkide ayrışmaz.

#### Sahip sistem erişilemezse davranış

- **Paket okunamıyorsa → mevcut yol.** Emniyetli geri düşüş **iki hakemin ortak hükmüdür**, dokuz kaynak dosyada doğrulanmamıştır `[BU SENTEZDE DOĞRULANMADI]` (Bölüm 10.1). ⚠️ **Bozuk veya eksik içerikte iki dalın sınırı K-15 (a)'da açıktır** — geri düşüşün nerede biteceği bu bölümde kesinleştirilmemiştir.
- **Özel gün takvimi okunamıyorsa → özel gün bloğu bugünkü gibi davranır.** ⚠️ **Yalnız bir hakem belgesinde yazılıdır;** diğer hakemde ve dokuz kaynak dosyada arandı, **tanımlayan hüküm bulunamadı** (harf duyarsız). `[BU SENTEZDE DOĞRULANMADI]` **Tek hakemde bulunan bir çalışma zamanı davranışı ortak yol yapılamaz** — bu nedenle **açık karar olarak kaydedilir**; emsali Bölüm 11'de aynı sınıftan iki fallback'in (tür etiketi yoksa davranış, hareket havuzu boşsa geri düşüş) açık karara taşınmasıdır.
- ⚠️ **Genel bir *"hiçbir durumda üretim bloklanmaz"* güvencesi bu bölümde normatif hüküm yapılmamıştır.** Ortak olan dar hüküm şudur: **paket yolunun bulunamaması üretimi durdurmaz, mevcut yola düşürür.** Politika motoru tarafındaki bloklama kapıları bundan ayrı bir mekanizmadır ve koşuyu durdurur, üretimi değil (Bölüm 7.7).

#### Bu projede kopyalanmaması gereken veri

1. **Özel gün adları ve kategorileri** — pakete **kopya liste** yazılmaz; yalnız anahtar referansı taşınır. Kaynak sözleşmesinde yazılı.
2. **Markaya özgü bilgi** (kanal, ton nüansı, yasak kelime) — **Marka DNA'sının işidir**; pakete girmez.
3. **Gerçek marka/firma adları** — içeriğinde gerçek marka adı geçen metin **pakete giremez**, emsal olarak ham katmanda kalır. **İki hakem görev sözleşmesinde de yazılıdır**. ⚠️ **Kural yürürlüktedir; açık olan yalnız otomatik denetimin kurulmasıdır** (**K-15**'in üçüncü bileşeni, Bölüm 13). Bu bir **teknik iş kalemidir, açık karar değildir** — kullanıcı kararı açılmaz; blok etkisi sweep'te izlenir.
4. **Uzun / zengin marka bilgisi** — geri getirme katmanının işidir; yapılandırılmış alanlar *"kısa ve her üretimde zorunlu"* bilgi içindir.
5. **Ters yön:** sektör paketindeki genel bilgi DNA'ya kopyalanmaz (yukarıda, sistem sınırı).
6. ⚠️ **Örnek postlardaki ürün, fiyat ve kampanya iddiaları** — bir hakem bunları *"gerçek marka bilgisi sayılmaz, yalnız üslup referansıdır"* diye **hüküm** olarak yazar. **Kaynakta bu bir öneridir** (DNA tarafında, enjeksiyon bloğuna eklenecek tek satır olarak); diğer hakem ele almaz. **Ortak veya kararlaştırılmış hüküm değildir** ve **evi DNA işidir** — bu belgede kapsam kararı açılmaz.

#### Müşteri yüzeyi ile paket bakımının ayrılması

**Her alt sektör için tek aktif paket vardır ve o alt sektörün bütün markaları aynı paketi kullanır** — marka veya müşteri başına ayrı sektör kalıbı tutulmaz. Paket evrimi **sektör araştırması ve kanıt hattı üzerinden** yürür (Bölüm 7) ve **yönetici son onayına** bağlıdır (Bölüm 8.2); **müşteri tarafından tetiklenmez**. ⚠️ Bu hattın **hangi kapılardan** oluşacağı — özellikle iki denetçi mutabakatı kapısının benimsenip benimsenmeyeceği — açık karardır ve burada kesinleştirilmez; politika motorunun fazı ise karara bağlandı (✅ **K-22 KAPANDI — A**, 2026-08-21, Ek B — motor **Faz 1'de**).

- **Müşteri beğenisi, marka başına ton/CTA takibi ve müşteri etkileşimi karar matrisinin girdisi değildir** — ortak hüküm, Bölüm 7.7'de yazılmıştır.
- **Müşteri etkileşim verisiyle kanıt döngüsü** bilinçli olarak sonraki faza bırakılmıştır ve kaynakta kapsam-dışı listesindedir; ön koşulu paket sürüm damgasıdır (**K-07**).
- ⚠️ **Marka DNA verisinin politika motoruna girdi olup olmayacağı açık karardır.** Hüküm — *DNA verisi motorun `koru`/`guncelle`/`cikar`/`ekle`/`kirp` kararlarına girmez* — yalnız bir hakem belgesinde ve **sonradan eklenen analiz** statüsüyle yazılıdır `[SEA-2026-08-11]`; **motor kavramı dokuz kaynak dosyanın hiçbirinde geçmez** (harf duyarsız tarandı, 0 isabet). ⚠️ **Yukarıdaki ortak hüküm bu boşluğu kapatmaz:** ortak hüküm müşteri **beğeni/etkileşim** verisini dışlar, bu hüküm **marka DNA alanlarının tamamını** dışlar — kapsamlar farklıdır ve ikincisi ortak değildir. ⚠️ **K-22'ye de indirgenemez:** K-22 motorun **hangi fazda** bulunacağını sorar, bu karar **motor varsa hangi veriyi kullanabileceğini** sorar; motor ilk faza alınıp DNA girdisi kabul de edilebilir reddedilebilir de. İki sistemin **veri sahipliği sınırını** belirlediği için **kullanıcı seviyesindedir**; karar ID'si Bölüm 17 sweep'inde verilecektir.
- ⚠️ **Paket içeriğinin uygulama arayüzü üzerinden okunabilirliği açık karardır (K-16)** — yalnız iç kullanım mı, yönetici arayüzüne mi, müşteriye görünür mü. Müşteri yüzeyi ile yönetici yüzeyinin yetkilendirmede ayrılması ise **risk kaydı ve yetki testi** olarak Bölüm 13.7 ve Bölüm 18'e aittir.

#### Post veri sözleşmesi — geçmiş üretimlerin akıbeti

Paket sürüm damgası `posts` tarafında yaşar (**K-07**). ⚠️ **Bölüm 8'den bu bölüme devreden nokta:** yeni bir paket sürümü aktifleştiğinde **geçmiş postların içeriğinin geriye dönük değiştirilip değiştirilemeyeceği** açık karardır ve yalnız bir hakem belgesinde ele alınmıştır. **K-07'ye indirgenemez** — K-07 damganın *veri yerini* sorar, bu karar *geçmiş üretim kaydının değişmezliğini* sorar. Kararın sonucu doğrudan bu bölümü ilgilendirir: geçmiş postlar değiştirilebilir sayılırsa `posts` kaydı artık üretim anının **değişmez kanıtı** olmaktan çıkar ve sürüm damgasının izleme değeri düşer. Bu bölümde kesinleştirilmemiştir; karar ID'si Bölüm 17 sweep'inde verilecektir.

---

## 13. Doğrulama ve kalite kapıları

[ZORUNLU]

**Bu bölüm eşik üretmez.** Eşiği açık olan hiçbir katman kabul kriteri, başarısızlık koşulu veya iptal ölçütü hâline getirilmemiştir; ölçülmemiş alanlarda kullanılan biçim *"ölçülecek; eşik pilot kanıtından sonra belirlenecek"*tir. ⚠️ **Bir adım daha var:** bazı yerlerde **eşiğin konulup konulmayacağı da açıktır** (Katman-2 için **K-11 (b)**, alarmlar için 13.6). Oralarda *"sonra belirlenecek"* demek bile fazladır — çünkü eşiğin **geleceğini** varsayar.

### 13.1 Veri ve migration doğrulaması

**Ortak ve kaynakta karara bağlı deterministik kontroller.** Aşağıdaki dördü iki hakem belgesinde de, uçtan uca başarı kriteri olarak kaynakta da yazılıdır `[AKT·KAYNAK · 2026-07-11]`:

1. Ham araştırma artefaktı tablosunda `UPDATE` **ve** `DELETE` istisna fırlatır.
2. `INSERT` başarılıdır ve koşu artefaktları `run_id` altında sorgulanabilir.
3. Aynı sektör için ikinci `active` paket satırı **indeks hatasıyla** reddedilir.
4. Aday paket, veri tabanına yazılmadan önce **şema ve boyut tavanına** karşı doğrulanır (yazım kapısı, Bölüm 5.3 · sayılar Bölüm 7.6).

**Kök kova invariantının veri tarafı — üçü de iki hakemde ortak, kaynakta zorunlu iş.** Alt sektör satırı kök sektör listesine sızmaz · kök sektör çözücüsü yalnız kök sektörleri eşler · trend katmanı alt sektör satırlarından etkilenmez. ⚠️ **İkisi henüz yazılmamış iştir, biri ise mevcut kodda zaten karşılanmaktadır:** liste ucunun ve çözücünün kök-seviye filtreleri **kurulacaktır** (kaynak bunu *"spec'e zorunlu iş: filtre + regresyon testi"* diye yazar `[AKT·KAYNAK · 2026-07-11]`); trend katmanının bağışıklığı ise mevcut kök-seviye filtresi sayesinde **ek iş gerektirmez** ve yalnız doğrulanır `[AKT·KAYNAK · 2026-07-11]`. Bu üç kontrolün **hangi katmanda** koşacağı 13.3'te ele alınmıştır.

5. `UNIQUE (sektör, sürüm)` ihlali hata verir.
6. Marka tablosundaki alt sektör alanı `NULL` bırakılabilir (varsayılan davranış).
7. **Geri doldurma yoktur** — mevcut markalar elle atanır, alt sektör alanı varsayılan olarak boştur. Bu, *"migration sonrası davranış değişmez"* güvencesinin veri tarafındaki ayağıdır.
8. **Migration geri alınabilir olmalıdır**; alt sektör satırları silinecekse marka bağının önce boşaltılması gerekir — **sıra spec'te tanımlanacaktır**, bu belgede tanımlanmamıştır.
9. **Veri bütünlüğü tam sweep'i:** alt sektör satırları eklendikten **sonra**, mevcut bütün markaların kök sektör değerleri ekleme öncesindeki değerleriyle karşılaştırılır. **Spot kontrol yeterli sayılmaz.**

⚠️ **Açık karara bağlı iki kontrol.** *(a)* Alt sektör alanına kök sektör kimliğinin yazılabilir olup olmadığı — kısıtın veri tabanında mı uygulamada mı zorlanacağı **K-08 (b)**'de açıktır; test ancak karar kapandıktan sonra beklenen sonucunu alabilir. *(b)* **Aktivasyon ve geri alma işleminin transaction davranışının test edilmesi ortaktır**, fakat testin neyi doğrulayacağı transaction ve yetkilendirme modelinin açık kararına bağlıdır (Bölüm 8.2).

**Adlandırma uyarısı** `[AKT·KAYNAK · 2026-07-11]`: yeni tabloların adları mevcut `sector_reports` ve `sector_trend_cache` ile karışmayacak biçimde seçilmelidir; birincil anahtar konvansiyonu `uuid`'dir.

### 13.2 İş kuralı / politika doğrulaması

Bu alt başlık **iki ayrı doğrulama kümesi** taşır ve ikisi aynı statüde değildir: **(a)** yürürlükteki iş kurallarının pozitif/negatif/sınır senaryoları, **(b)** politika motorunun fixture testleri — motor benimsendiğine göre (✅ **K-22 KAPANDI — A**, 2026-08-21, Ek B) ikincisi **Faz 1 gündemidir**; içeriği motorun kendi açık kararlarına bağlıdır.

#### (a) İş kuralı doğrulaması

| Kural | Pozitif | Negatif | Sınır |
|---|---|---|---|
| Paket yerine-geçme | Paketli markada Tier 2'de paket bloğu bulunur | Kök sektör rehberi **aynı prompt'ta bulunmaz** | Alt sektör atanmış ama paket `draft` → mevcut yol |
| Yan yana enjeksiyon yasağı | — | İkisinin birlikte basıldığı hiçbir birleşim yok | Paket aktive edilirken (geçiş anı) |
| Özel gün eşleşmesi | Anahtar eşleşti → dönem kalıpları Tier 3'e girdi | Eşleşmedi → blok değişmedi **ve log satırı düştü** | Gün-bazlı bayram satırı (*"… 2. Gün"*) |
| `anma` kısıtı | `anma` gününde satış çağrısı üretilmiyor | ⚠️ *Kullanıcı satış istese bile kısıt üstün* — **kısıtın geçersiz-kılıcı yetkisi hâlâ açık karardır** (Bölüm 4.6); beklenen sonuç o karara bağlıdır. ⚠️ **K-03'ten ayrıdır ve onun kapanmasıyla kapanmaz:** K-03 paket türü ile takvim kategorisi arasındaki çatışmayı çözer, buradaki soru kısıtın **kullanıcı isteği karşısındaki** yetkisidir | Dönem türü ile sistem kategorisi çelişiyor → **K-03 kapandı: paket türü üstündür**; `anma` davranışı bu kararla **korunur** |
| Aday listenin kapalılığı | Öneri yalnız aktif paketli alt sektörlerden geliyor | **Serbest metin dönüşü reddediliyor** | Hiç aktif paket yoksa → boş dönmeli |
| Üretim akışının sürtünmesizliği | Üretimde alt sektör sorusu **hiç sorulmuyor** | — | Atamasız markada da sorulmuyor |
| Dağarcık kullanım talimatı (**K-04**) | Blok başında talimat satırı var | Dağarcığın tamamı çıktıya kopyalanmıyor | Çok öğeli görsel dağarcığı |
| Kanal-bağımlı kalıp (**K-05**) | Etiket pakete taşınmış | Etiketi silinmiş kalıp yok | Kanal-nötr uyarlanmış kalıpta etiket yok |
| Üretim sürüm ilişkisi | Paketli üretim, kullanılan paket kimliği ve sürümüyle ilişkili | Paket yolu dışındaki üretimde **geçerli bir paket ilişkisi bulunmaz** | ⚠️ **Aktivasyon anına denk gelen üretim hangi sürümle ilişkilendirilir? — açık karar** (aşağıda) |
| Tek aktif sürüm | Aktivasyon sonrası tek `active` satır | İki `active` satır veri tabanında oluşamaz | Geri alma sırasındaki ara durum |

⚠️ **Özel gün testlerinin iki açık karara bağlılığı.** *(a)* **Anahtar biçimi K-01b**'de açıktır; bu nedenle *"anahtar eşleşti"* satırının **beklenen anahtarı** ve gün-bazlı bayram satırlarının sınır senaryosu ancak o karar kapandığında somutlaşır. *(b)* **`anma` türünün ana örneği bugün gerçek bir günle tetiklenemez** — ilgili günlerin sistem takviminde bulunmadığı üç katmanda da kayıtlı bir olgudur `[AKT·KAYNAK · 2026-07-11]` ve eksik günlerin takvime eklenmesi **K-01a**'da açıktır. ⚠️ **Bundan akışın test edilemez olduğu sonucu çıkmaz:** başka bir dönemin `anma` etiketlenmesini veya fixture üzerinden test edilmesini **dışlayan hüküm yoktur** (tarandı, Bölüm 11.1). **K-01a alınmazsa test fixture üzerinden koşulur; alınırsa gerçek günle koşulabilir hâle gelir** — testin varlığı karara bağlı değildir, **biçimi bağlıdır**.

⚠️ **Yeni açık karar — aktivasyon ara penceresinde başlayan üretimin sürüm ilişkisi.** Bir üretim isteği paket sürümü aktive edilmeden **önce** başlayıp aktivasyondan **sonra** kayda yazılırsa, kaydın hangi sürümle ilişkilendirileceği tanımlı değildir. ⚠️ **Üç komşu kararın hiçbirine indirgenemez:** **K-07** ilişkinin *fiziksel temsilini* sorar · geçmiş postların geriye dönük değiştirilebilirliği (Bölüm 12) *sonradan yeniden yazmayı* sorar · ara pencerede okuyucu davranışı testi (aşağıda) *üretimin paketsiz yola düşüp düşmediğini* sorar. Bu karar, **hangi anın esas alınacağını** sorar — isteğin başlangıcı mı, kaydın yazılması mı.

⚠️ **Ara pencerede okuyucu davranışı testi — benimsenmesi hâlâ açıktır, kapsamı burada yazılmıştır.** Bölüm 8'den devreden yükümlülük şudur: aktivasyonun iki adımlı penceresinde üretimin **paketsiz yola düşmediğinin** ayrıca test edilmesi. Test **yalnız bir hakem belgesinde** istenmiştir ve tek hakem beyanıyla benimsenmiş sayılamaz; **benimsenirse** kapsamı paket çözücüsünün ara durumdaki davranışıdır ve doğrulama yöntemi 13.1'in transaction testiyle aynı senaryoyu paylaşır. Benimsenmezse ara pencerenin tek görünürlük mekanizması aktivasyon olay kaydıdır (13.6).

⚠️ **Takvim erişilemezliğinde özel gün bloğunun davranışı açık karardır** (Bölüm 12); bu nedenle o senaryo için **beklenen sonuç yazılamaz** ve kabul matrisine satır açılmamıştır. Karar kapandığında satırı 13.7'ye eklenir.

#### (b) Politika motoru doğrulaması

> **Motor kavramı dokuz kaynak dosyada geçmez** (harf duyarsız, 0 isabet); motorun kuruluş fazı karara bağlandı — ✅ **K-22 KAPANDI — A** (2026-08-21, Ek B), motor **Faz 1'de** kurulur. Bu 13 madde bir gereksinim listesi değil, motor benimsendiğine göre **Faz 1'de koşulacak** testlerin kaydıdır. ⚠️ **Bağımlılık topluca değil, test bazında belirlenmiştir:** bir kısmı **yürürlükteki ortak veya kaynakta karara bağlı kurala** dayanır ve doğruluğu motor kararından bağımsızdır (yalnız *"motorun bunu uyguladığının"* testi motora bağlıdır); bir kısmı ise **kendi açık kararı kapanmadan beklenen sonucunu alamaz**. Her madde kendi bağını satırında taşır. ⚠️ **Liste kapalı bir küme değildir** — kaynak hakem belgesi onu *"en az şu testler gerekir"* diye açar.

1. Aktif paketteki her karar birimi için karar üretilmemişse koşu **bloklanır**. *(Kalıcı kalıp kimliği açık kararına bağlı — Bölüm 6.3.)*
2. Aynı kalıp kimliği veya aynı sabit alan yolu için birden fazla nihai karar varsa koşu **bloklanır**.
3. Eski öğe yeni araştırmada geçmiyorsa ve ters kanıt yoksa öğe **korunur**. *(Kaynakta karara bağlı ortak kural.)*
4. Uyuşmazlıklı güncelleme/çıkarma kararı eski öğeyi **korur**. ⚠️ **Bu deterministik çözüm yalnız bir hakemdedir;** diğer hat uyuşmazlığı **açık soruya** düşürür — motorun kararsız bıraktıklarının akıbeti **K-23**'te açıktır (Bölüm 4.5).
5. Uyuşmazlıklı mevzuat/güvenlik kararı koşuyu **bloklar**. *(Bloklayıcı alan kümesinin kesin listesi açık karardır — Bölüm 7.7.)*
6. Mutabakat eşiğini geçmeyen yeni öğe nihai adaya **alınmaz**. *(Eşiğin kendisi sentez görev sözleşmesinde yazılıdır ve motordan bağımsız olarak yürürlüktedir.)*
7. Eşiği geçen yeni öğe **ve** iki denetçinin kabulü adaya **alır**. *(İki denetçi mutabakatı kapısının benimsenmesi açık karardır — Bölüm 7.7.)*
8. Tek resmî/birincil kaynak istisnası **yalnız iki URL doğrulamasıyla** kabul edilir. ⚠️ Bu istisnanın kesin sözleşmesi açık karardır ve **yürürlükteki denetçi sözleşmesinde iki-denetçi URL şartı bulunmaz**; test bugünkü sözleşmeyi değil, **önerilen** kapıyı doğrular.
9. Çalışma zamanı içeriği ve şema özeti aynıysa sonuç **`değişiklik yok`**. *(Sabit biçimli özet üretim kuralı açık karardır — Bölüm 6.5.)*
10. Değişim oranı yapılandırılmış sınırı aşarsa koşu **bloklanır**. *(Üç bariyerin benimsenmesi ayrı açık kararlardır — Bölüm 7.7.)*
11. `bloklandı` ve `değişiklik yok` sonuçları veri tabanında `active` geçişi **üretemez**. *(İlke ortaktır — **K-28**; sunucu tarafı zorlamanın uygulama ayağı açıktır.)*
12. Aynı girdi anlık görüntüsü ve aynı politika sürümü **aynı nihai adayı** üretir. ⚠️ *Aynı girdi anlık görüntüsünün **teknik garantisi** orkestrasyon tarafında açık karardır (Bölüm 7.4); test bu garanti kurulmadan koşulamaz.*
13. Politika raporu üretildikten sonra yöneticiye gösterilen anlık görüntü **değiştirilemez**. ⚠️ **Bu hüküm yalnız bir hakem belgesindedir**, diğerinde ele alınmamıştır; ortak veya kararlaştırılmış kural değildir (Bölüm 7.8).

**Aynı belgenin kendi koyduğu sınır korunur:** bu testler **semantik doğruluğu yeniden üretmez** — iki denetçinin yapılandırılmış kararlarını deterministik biçimde uygular ve eksik/çelişkili durumlarda güvenli geri düşüşü seçer. Kalite yargısının yeri 13.4'tür.

### 13.3 Regresyon doğrulaması

**Korunması gereken mevcut davranış — birleşik küme.** ⚠️ **Küme kapalı değildir:** kaynak, fikir önerme ve legacy yolların *"da girmesi"* gerektiğini söyleyerek listeyi **ekleyerek** tarif eder ve maddeyi **açık iş** olarak işaretler; test tasarımı spec seansına bırakılmıştır.

1. Tier 1 sistem prompt'u.
2. Tier 2 marka bağlamı — paket yoluna girmeyen markada.
3. Tier 3 bağlam bloğu (özel günlü ve günsüz).
4. Görsel director'ın çıktı biçimi talimatı bloğu.
5. Kısa video durağan kare prompt'u — **iki mod ayrı ayrı** (metinden görsel + ürün referanslı görsel düzenleme).
6. Hareket kodu havuzu ve seçim davranışı.
7. Fikir önerme ucunun prompt'u.

8. **Legacy kısa video yolu.** ⚠️ İki hakem de bu satırı **K-06'ya bağlayarak koşullu** yazar; **ortak kaynak karar dokümanı ise koşul koymaz** — regresyon kapsamına fikir önerme **ve** legacy yolun ikisi de girmelidir ve madde **açık iş** olarak işaretlidir `[AKT·KAYNAK · 2026-07-11]`. **Ayrışma ilkede değil, yalnız fixture listesindedir** (Bölüm 10.4). **Satır listeye koşulsuz girer** — bu, kaynaktaki koşulsuz gereksinimin taşınmasıdır, **yeni bir karar veya öneri değildir ve kullanıcı kararına çevrilmez** (Bölüm 10.4'te de böyle kayıtlıdır). **K-06 sonucu listeye girip girmeyeceğini değil, fixture'ın beklenen değerini belirler** — yol düzeltilirse beklenen değer düzeltilmiş davranıştır, kapsam dışı notlanırsa bugünkü davranışın değişmediğidir.
9. **Üretimde paket sürüm ilişkisinin kurulmaması.** Paket yoluna girmeyen üretimde **geçerli bir paket ilişkisi bulunmaz**; kaynak bu kontrolü açıkça prompt kapısına bağlar `[AKT·KAYNAK · 2026-07-11]`. ⚠️ Kontrolün **somut biçimi K-07'ye bağlıdır** (ilişkinin fiziksel temsili açıktır). Diğer hakem aynı hükmü **iş kuralı** olarak test eder (13.2) — kural ortaktır, **katmanı farklıdır**.

10. Sektör listeleme ucunun yanıtı — kök liste **değişmemeli** (filtre eklendikten sonra kök satırlar aynen dönmeli).
11. Kök sektör çözücüsünün mevcut marka eşlemeleri — alt sektör satırları eklendikten sonra **değişmemeli**.
12. Trend katmanı sorgusu — alt sektör satırlarına **bağışık kalmalı**.

**Katman ataması.** **Üçü de deterministik regresyon kontrolüdür ama prompt metni karşılaştırması değildir** — biri API yanıtını, biri sorgu çözümlemesini, biri sorgu davranışını denetler. Bu nedenle **Katman-1'in byte-exact prompt karşılaştırmasının içine değil, onunla aynı zorunluluk seviyesinde bir veri/API regresyon kümesine** yerleştirilirler. Ayrım anlamlıdır: byte-exact karşılaştırmanın kabul ölçütü *"tek bayt fark = RED"*tir; bu üçünün ölçütü ise **eşitliğin ilgili alan bazında** kurulmasıdır. ⚠️ **Bu bir kullanıcı kararı değildir ve öneri olarak da sunulmaz:** atama, protokolün katman kuralının (prompt'ta var/yok → Katman-1) iki hakemin **mevcut içeriğine** uygulanmasıdır; doğruluğu **teknik tutarlılık incelemesiyle** denetlenir, kullanıcı onayıyla değil.

**Karşılaştırma yöntemi — Katman-1.** Modele giden prompt parçaları yakalanır ve **değişiklik öncesinde dondurulmuş prompt fixture'ı** ile **byte-exact** karşılaştırılır. Karşılaştırılan şey LLM çıktısı değil, **modele gönderilen prompt metnidir**. Gerekçe üç ayaklıdır ve kaynakta karara bağlıdır `[AKT·KAYNAK · 2026-07-11]`: *(a)* LLM çıktısı stokastiktir (`temperature=1.0`, seed yok) → çıktıdaki farkın kaynağı ayırt edilemez; *(b)* görsel üretimle test **dış sağlayıcı kredisi yakar** → hat değişiklikleri canlı üretimle değil lokal/ucuz katmanla doğrulanır; *(c)* doğrulama standardı **yeniden koşulabilir + byte-exact**tir. Katman **zorunlu, otomatik ve ücretsizdir; tek bayt fark = RED.**

**Paketli fixture'da yapısal kontroller** — yalnız bir hakem belgesindedir ve **doğru katmandadır**: bunlar prompt'ta bir bloğun bulunup bulunmadığını sorar, dolayısıyla deterministiktir ve Katman-1'e aittir (bkz. 13.7'deki düzeltme):

- Paket bloğu **bulunur**.
- Kök sektör rehberi **bulunmaz**.
- Görsel dağarcığı **doğru yüzeye** eklenmiştir.
- Özel gün bloğu **yalnız eşleştiğinde** eklenmiştir.
- Anma/kutlama kısıtları **doğru yerdedir**.
- Hareket kodları, karara bağlanan yapıya göre **paket havuzundan** kullanılır (**K-02**).

**Kapsanacak varyasyonlar:** paket yoluna girmeyen marka × (caption / görsel / carousel / kısa video / fikir önerme) × (özel günlü / günsüz) × (ürün referanslı / referanssız video modu). ⚠️ **Carousel'in ayrı bir prompt yüzeyi olup olmadığı K-15 (b)**'de açıktır; varyasyon kümesinin bu ayağı o karara bağlıdır.

**Ortak altyapı — bağlayıcılığı açıktır (K-20).** Marka DNA işi de aynı regresyon koşumuna ihtiyaç duyar ve **kaynak DNA karar dokümanı** hem *"iki sistem aynı regresyon koşumunu paylaşır, ikinci altyapı kurulmaz"* der hem de kendi hiyerarşi testini bu kapı protokolüne bağlar `[AKT·KAYNAK · 2026-07-11]`. ⚠️ **Hüküm burada kesinleştirilmez:** kaynağın kendi maddesi **açık iş** olarak işaretlidir ve paylaşımın bağlayıcı olup olmadığı **K-20**'de açıktır. Paylaşım benimsenirse Katman-1'in fixture kümesi DNA tarafının boş-alan senaryosunu da kapsayacak biçimde genişler; **o kapsamın içeriği DNA işinin kendi kararıdır**, bu belgede yazılmaz.

### 13.4 Çıktı kalitesi değerlendirmesi

[GEREKİRSE]

**Katman-2 — operatör onayının girdisidir, otomatik kapı değildir.**

- **Örneklem:** az sayıda gerçek üretim, **içerik tipi başına küçük örneklem**. İki hakem de aynı ayrımı yapar; biri sınıfları adlandırır: caption · carousel/görsel · kısa video. ⚠️ **Kesin sayı belirlenmemiştir** — **K-11 (a)**.
- **Kör değerlendirme:** vardır. Protokol: paketli ve paket yoluna girmeyen çıktılar yan yana, hangisinin hangisi olduğu gizli; soru *"hangisi bu sektörün postu?"*. Çapraz test kaynakta da yazılıdır: iki farklı sektörün üretimi birbirinden ayrışıyor mu.
- **Rubrik** — yalnız bir hakem belgesinde yazılıdır; ölçütler kaynağın kendi kararlarından türetilmiştir, ayrı bir kaynak hükmü değildir:
  - Sektörel ayrışma gözlenebiliyor mu?
  - Dağarcık **seçilerek** mi kullanılmış, yoksa liste tamamlanmış mı (**K-04** sinyali)?
  - Markanın sahip olduğu bilinmeyen bir kanal veya hizmet önerilmiş mi (**K-05** sinyali)?
  - Mevzuat hassasiyetleri ihlal edilmiş mi?
  - `anma`/`kutlama` gününde satış dili sızmış mı?
- **Geçme eşiği: yoktur.** Kaynak bu katmanı *"operatör onayının girdisi"* olarak tanımlar ve **sayısal eşik vermez**. ⚠️ **Eşiğin konulup konulmayacağı da açıktır — K-11 (b);** bu belge *"eşik sonra belirlenecek"* demez, çünkü bu, eşiğin geleceğini varsayardı. Doğru ifade: **eşik konulmasına karar verilirse** değeri ancak pilot kanıtından sonra ölçülebilir; **konulmamasına karar verilirse katman eşiksiz kalır** ve kalite sinyali olmayı sürdürür.

⚠️ **K-11 tek ID altında iki ayrı kararı taşır ve ikisi ayrı seçilebilir:** *(a)* örneklemin **boyutu** — operasyonel yük kararıdır · *(b)* bir **geçme eşiği** konup katmanın kapıya çevrilip çevrilmeyeceği. Boyut belirlenip eşik tamamen reddedilebilir.

⚠️ **Bu katman başarısızlık koşulu üretmez.** Kör değerlendirmede sektörel ayrışmanın gözlenmemesi **aktivasyon kararında olumsuz kalite sinyalidir**; otomatik red eşiği K-11 (b) kapanmadan tanımlanmaz. Katmanın **koşulması ve sonucunun yöneticiye sunulması** bir ön koşuldur; **sonucu kapı değildir** (Bölüm 2.3, Bölüm 8.2).

### 13.5 Güvenlik, gizlilik ve kötüye kullanım testleri

> ⚠️ Aşağıdaki maddelerin bir kısmı **başka bölümlerde karara bağlanmış kuralların test karşılığıdır** — o kurallar ortaktır; tek hakem katkısı olan şey **bunların bir test kategorisi olarak toplanmasıdır**.

**Yetkilendirme sınırları — üç statü ayrı tutulur; model bütün olarak kapanmış değildir.**

- **Kapanmış:** müşteri paket bakım akışını görmez, tetikleyemez, onaylayamaz (Bölüm 12) · marka kullanıcısı yalnız hangi alt sektöre atandığını seçer (Bölüm 9, kaynakta karara bağlı) · motorun kendi başına `active`'e geçirememesi **ilke olarak** ortaktır (**K-28**).
- ⚠️ **Varsayım:** yazma yetkisinin **operatör ve koşu yüzeyinde toplanması** iki belgenin **ortak çalışma varsayımıdır** `[VARSAYIM]`, karara bağlanmış bir yetkilendirme modeli değildir (Bölüm 6.6).
- ⚠️ **Açık:** aktivasyon/geri alma işleminin **yetkilendirme modeli** (Bölüm 8.2) · **K-28**'in sunucu tarafı zorlama ayağı · paket içeriğinin uygulama arayüzü üzerinden okunabilirliği (**K-16**) · ham katmanın okuma yetkisi ve araç eşlemesinin görünürlüğü (Bölüm 6.2).

⚠️ **Sonuç:** yalnız birinci gruptaki sınırlar için beklenen sonuç yazılabilir. İkinci ve üçüncü gruptakiler test edilebilir hâle gelmeden önce **varsayımın karara, açık kararların sonuca** bağlanması gerekir; bu bölüm onları kesinleştirmez.

**Hassas veri sızıntısı.**

- *"Paket kişisel veri içermez"* iddiası **bu sentezde doğrulanmamıştır** `[BU SENTEZDE DOĞRULANMADI]`; doğrulanmadan saklama ve erişim politikası uygulanırsa risk kabulü örtük yapılmış olur (Bölüm 6.6).
- İçeriğinde **gerçek marka/firma adı geçen metnin pakete girmemesi** kuralı **yürürlüktedir** — iki hakem görev sözleşmesinde de yazılıdır `[AKT·KAYNAK · 2026-07-11]`. ⚠️ Açık olan yalnız **bu kuralın otomatik denetiminin yazım kapısına eklenmesidir**; bu bir **teknik iş kalemidir, açık karar değildir** (**K-15**'in üçüncü bileşeni). Sözleşme düzeyindeki karşılığı sentez çıktı kontrolüdür; **otomatik denetim bugün kurulmamıştır.**

**Prompt enjeksiyonu ve zararlı girdi.**

- Araştırma çıktısı LLM üretimidir ve dış web kaynaklıdır → paket metnine **dolaylı talimat sızabilir**. **Hedef hatta** bu riske dolaylı olarak temas eden üç adım bulunur: mekanik biçim kapısı, iki bağımsız denetçinin iddia düzeyinde incelemesi, yönetici onayı. ⚠️ **Dürüst sınır — üçü de bugün kurulmamıştır ve hiçbiri prompt enjeksiyonuna özel değildir**; bu, kaynak dokümanlarda ele alınmamış bir risktir ve **K-10**'da açık karardır (risk kaydı Bölüm 18).
- Alt sektör öneri çağrısında **serbest metin dönüşü yasaktır** (yalnız listeden seçim) → bu yüzey yapısal olarak kapalıdır. Kural ortaktır ve Bölüm 9'da yazılıdır.

**Kötüye kullanım.** Marka kullanıcısının kendini yanlış alt sektöre atayarak başka bir sektörün paketini alması mümkündür. ⚠️ Etkinin *"düşük"* sayılması **yalnız bir hakem belgesinin değerlendirmesidir ve ölçülmemiştir** `[ÖLÇÜLMEMİŞ VARSAYIM]`; bu belgede kontrol önerilmemiş, **risk kaydına** bırakılmıştır (Bölüm 18).

### 13.6 Gözlemlenebilirlik

⚠️ **Aşağıdaki log kümesi kapalı değildir** — bir hakem belgesi listesini *"en az şu olaylar loglanmalıdır"* diye açar; ikisi de sınırlayıcı bir sayım vermez.

**Zorunlu log olayları — ortak çekirdek** (iki hakem belgesinde de; ilki kaynakta da karara bağlıdır):

1. **Özel gün anahtarı normalize edildiği hâlde eşleşmedi** — sessiz düşme ile birlikte log zorunludur `[AKT·KAYNAK · 2026-07-11]`.
2. **Kullanılan paket kimliği ve sürümü** (hangi marka, hangi paket, hangi sürüm).
3. **Paket okuma veya şema doğrulama hatası** ve mevcut yola düşüş.
4. **Aktivasyon ve geri alma olayı.** Biri satırı olay olarak anar, diğeri alanlarını da yazar (kim, ne zaman, hangi sürümden hangisine) — **tamamlayıcıdır**. ⚠️ Bu ortak yükümlülük, **onay/ret olayının kimlik ve zaman damgası** açık kararıyla karıştırılmamalıdır (Bölüm 7.8).

5. Alt sektör atanmış olduğu hâlde aktif paket bulunamamış marka.
6. Araştırma koşusu, denetim ve sentez artefaktlarının kimlikleri.
7. Yazım kapısının **red kayıtları** (aday paketin yazımı engellendi).

**Politika motoruna bağlı olaylar** — motor benimsendiğine göre (✅ **K-22 KAPANDI — A**, Ek B) Faz 1 gündemidir; yalnız bir hakem belgesinde: motor sürümü ve sonuç durumu · içerik özetleri · karar kapsamı, değişim oranları ve blok nedenleri · yöneticiye gösterilen anlık görüntü ve son onay/ret olayı.

**Hassas veri kuralı — iki kural tamamlayıcıdır ve ikisi de geçerlidir:** kişisel veya hassas veri loglara taşınmaz (birinci belge) **ve** paket içeriği log'lara tam olarak basılmaz, anahtar/kimlik yeterlidir (ikinci belge).

**Metrikler.**

- Paketli / paket yoluna girmeyen üretim sayısı.
- Özel gün eşleşme oranı (eşleşen / seçilen).
- Sürüm başına üretim sayısı — **K-07**'ye bağlıdır (ilişki kurulmazsa türetilemez).
- **Tur başına operasyon süresi** — ⚠️ **bu metrik kaynakta karara bağlıdır** `[AKT·KAYNAK · 2026-07-11]`: kaynak, Faz 1 paket tavanının ilk turda ölçülecek tur süresine göre revize edileceğini yazar (**K-13**). **Ölçülmemiştir; hedef değeri belirlenmemiştir** ve kapıya çevrilmez.
- Politika motoru metrikleri `[SEA-2026-08-11]` — koşu başına uygulanan/reddedilen/kararsız karar sayıları · **kararsızlık oranı** · geri-ekleme çelişkisi sayısı · motor koşu süresi · **yöneticinin tur başına harcadığı süre**. Sonuncusu *"insan eliyle aylar sürer"* iddiasının ölçüm noktasıdır; iddia `[ÖLÇÜLMEMİŞ VARSAYIM]` olarak kalır ve kapıya çevrilmez.

⚠️ **Yeni açık karar — alarm katmanının benimsenmesi ve sorumlusu.** Eşiğe bağlı uyarı üretimi (*özel gün eşleşmezlik oranı yüksekse* · *paketli olması gereken markada sürekli paket bulunamıyorsa*) **yalnız bir hakem belgesinde** önerilmiştir; diğer hakemde ve dokuz kaynak dosyada **0 isabettir** (harf duyarsız). Alarm bir **operasyonel yükümlülük ve rol ataması** doğurur (kim uyarıyı alır, kim müdahale eder) ve **eşik değerleri hiçbir katmanda tanımlı değildir**. Tek hakem beyanıyla benimsenmiş sayılamaz. ⚠️ **Eşik bu kararın parçası değil, sonucudur:** benimsenirse eşikler **ölçülecek, pilot kanıtından sonra belirlenecektir**; bu belgede eşik üretilmemiştir.

**İzlenebilirlik kimliği.** Zincir üç kimlikten kurulur: araştırma turu kimliği · kullanılan paket kimliği ve sürümü · karar günlüğündeki kanıt referansı (denetçi tablosunun satır numarası / kaynak / URL). ⚠️ **Zincirin iki ucu kaynak sözleşmelerinde tanımlıdır** `[AKT·KAYNAK · 2026-07-11]`: denetçi tablosundaki satır numarası **satır kimliğidir** ve sentez kararları ona referans verir; kanıt alanının biçimi sentez sözleşmesinde sabitlenmiştir. Zincirin kapattığı yol **doğrusal değildir, son halkada dallanır:** **üretilen post → paket sürümü → karar → kanıt referansı**, ve kanıt referansı sözleşmede **üç eşdeğer daldan biri** olabilir — *(i)* denetçi tablosunun satır numarası → oradan ham kaynağa · *(ii)* **doğrudan ham kaynak** · *(iii)* **URL**. ⚠️ **Denetçi satırı zorunlu bir ara halka değildir;** onu tek yol gibi göstermek sözleşmenin izin verdiği iki dalı görünmez kılar. ⚠️ İlk halka **K-07**'ye (ilişkinin fiziksel temsili), kararın **kim tarafından verildiğinin ayırt edilmesi** ise **K-25**'e bağlıdır.

### 13.7 Kabul matrisi

> ⚠️ **"Zorunlu mu?" sütunu Katman-2 satırlarında** testin koşulmasını ve sonucunun sunulmasını zorunlu kılar, **sonucunu otomatik kapı yapmaz.**

| Senaryo | Beklenen sonuç | Doğrulama yöntemi | Zorunlu mu? |
|---|---|---|---|
| Paket yoluna girmeyen marka, caption üretimi | Prompt'lar fixture ile byte-exact aynı | **Katman-1** | **Evet** |
| Paket yoluna girmeyen marka, kısa video (iki mod) | Durağan kare prompt'u + hareket havuzu byte-exact aynı | **Katman-1** | **Evet** |
| Paket yoluna girmeyen marka, fikir önerme | Prompt byte-exact aynı | **Katman-1** | **Evet** |
| Paket yoluna girmeyen marka, legacy kısa video yolu | Prompt byte-exact aynı — **beklenen değer K-06 sonucuna bağlı** | **Katman-1** | **Evet** (kapsam kaynakta koşulsuz) |
| Paket yoluna girmeyen üretimin kaydı | Geçerli bir paket ilişkisi **kurulmaz** — biçim **K-07**'ye bağlı | Veri tabanı kaydı kontrolü | **Evet** |
| Paketli marka, caption | Tier 2'de paket bloğu var, kök rehber yok | **Katman-1** prompt yakalama | **Evet** |
| Paketli marka + eşleşen özel gün | Tier 3'te dönem kalıpları var | **Katman-1** prompt yakalama | **Evet** |
| Paketli marka + eşleşmeyen gün | Blok değişmedi **ve log satırı düştü** | Log kontrolü | **Evet** |
| **Paketli marka, görsel — prompt yapısı** | Görsel talimatında sektör dağarcığı bloğu **bulunur** | **Katman-1** prompt yakalama *(deterministik)* | **Evet** |
| **Paketli marka, görsel — çıktı kalitesi** | Dağarcık **seçilerek** yansımış | **Katman-2** kör örneklem | Koşulması ve sunulması **evet** — **sonucu otomatik kapı değil (K-11 (b))** |
| İki farklı sektörün çapraz üretimi | Kör değerlendirmede ayrışıyor | **Katman-2** | Koşulması ve sunulması **evet** — **sonucu otomatik kapı değil (K-11 (b))** |
| Alt sektör satırları eklendi | Mevcut markaların kök sektör değeri **değişmedi** | **Tam sweep** karşılaştırma | **Evet** |
| Sektör listeleme ucu | Kök liste aynen dönüyor; alt sektör **sızmıyor** | Veri/API regresyon kontrolü *(3 ön yüz tüketicisi)* | **Evet** |
| Kök sektör çözücüsü | Mevcut marka eşlemeleri **değişmedi** | Veri/API regresyon kontrolü | **Evet** |
| Trend katmanı | Alt sektör satırlarına bağışık | Sorgu testi | **Evet** |
| Ham artefakt `UPDATE`/`DELETE` | **İstisna** | Veri tabanı testi | **Evet** |
| İkinci `active` paket | **İndeks hatası** | Veri tabanı testi | **Evet** |
| Geri alma (kötü sürüm) | Önceki sürüm aktif; postlar sürüm ilişkisiyle ayrışıyor — **ilişki K-07'ye bağlı** | Prosedür testi | **Evet** |
| Paket **okunamıyor** (içerik bozuk veya sorgu başarısız) | **Tüm yol** mevcut yola düşer, üretim **bloklanmıyor**, log var — iki hakemde de bu yönde | Hata enjeksiyonu | **Evet** |
| Paket okunuyor ama **bir alan eksik** | ⚠️ **Beklenen sonuç yazılamaz — K-15 (a) açık.** Tek hakemdeki hüküm *(yalnız o alanın enjeksiyonu atlanır, paket yolu sürer)* kendi belgesinde `[VARSAYIM]` etiketlidir; **iki dalın sınırını tanımlayan hüküm bulunamadı** (Bölüm 10.1) | — | Karar kapandığında |
| Alt sektör önerisi | Yalnız aktif paketli listeden; serbest metin reddediliyor | Sözleşme testi | **Evet** |
| Web sitesi olmayan marka | Geri düşüş önerisi çalışıyor (yine listeden) | Senaryo testi | **Evet** |
| İkinci denetçi web erişimsiz | *"Yapılamadı"* raporlanıyor, **uydurma yok**; sentez tek denetçi kanıtını normal sayıyor | Kuru koşum | **Evet** — ön kontrol **K-14**'te açık |
| Dönem türü ile sistem kategorisi çelişiyor | ✅ **K-03 KAPANDI (2026-08-17, kullanıcı kararı): sentez politikayı uygular — paketin tür etiketi üstündür**, kategori korunur ve çatışma karar günlüğüne yazılır (Bölüm 7.5, 11.2). ⚠️ **Yürürlükteki sentez görev sözleşmesi bu kararı henüz yansıtmamaktadır** — metin hâlâ *"kararı VERME — iki tarafı ve eğilimini yazarak açık soruya düşür"* der `[AKT·KAYNAK · 2026-07-11]`; düzeltme **sürümlü supersession** olarak Bölüm 14.4'te kayıtlıdır ve **yeni bir kullanıcı kararı değildir** | Kuru koşum | **Evet** — ⚠️ **beklenen sonuç sözleşme düzeltmesine bağlıdır**; düzeltme yansımadan koşulan kuru koşum **eski davranışı** üretebilir |
| Gerçek marka adı içeren kalıp | Pakete **girmiyor** | Sentez çıktı kontrolü — otomatik denetim **iş kalemi (K-15'in üçüncü bileşeni)** | **Evet** |
| Boyut tavanı aşımı | Kırpma yapılıyor ve karar günlüğüne kırpma kaydı düşüyor | Yazım kapısı testi | **Evet** |
| Motor: kanıtsız çıkarma kararı | **Uygulanmıyor — kalıp korunuyor**; koşu raporunda *"kanıt yetersiz"* | Politika motoru testi | **Motor benimsendi (✅ K-22 KAPANDI — A) — Faz 1 testi** |
| Motor: çıkarılanlar listesiyle eşleşen kalıp | **Geri-ekleme çelişkisi** olarak işaretleniyor, sessizce eklenmiyor | Politika motoru testi | **Motor benimsendi (✅ K-22 KAPANDI — A) — Faz 1 testi** |
| Motor: karar veremediği kalıp | Değişiklik yok + *"motor kararsız"* raporlanıyor | Politika motoru testi | **K-22** *(motor)* **+ K-23** — kararsız maddenin yöneticiye mi güvenli varsayılana mı düşeceği ayrıca açıktır; beklenen sonuç ona bağlıdır |
| Motor kararının karar günlüğündeki temsili | Kanıt satırı var **ve** kararın motor tarafından verildiği ayırt edilebiliyor | Kayıt kontrolü | **K-22** *(motor)* **+ K-25** — satır düzeyinde aktör alanı **ayrı bir açık karardır**; koşu seviyesi damgasıyla birlikte veya ayrı alınabilir (Bölüm 7.7) |
| Özet diff | Çıkarılan kalıp **sayısı** ve eşik-üstü olanlar görünüyor; ayrıntı tam listeyi açıyor | Arayüz/çıktı testi | **K-22** *(motor)* **+ eşik-üstü eşiği** (Bölüm 7.8) **+ sözleşme drifti** — yürürlükteki sentez sözleşmesi **tam listeyi** onay ekranının ilk bölümü yapar; özet modeli ile arasındaki fark açıktır (Bölüm 7.5) |
| Aktivasyon yetkisi | **Yalnız yönetici** yapabiliyor; motor kendi başına `active`'e geçiremiyor (**K-28**) | Yetki testi | **Evet** |
| Müşteri yüzeyi | Müşteri paket bakım akışını **görmüyor, tetikleyemiyor, onaylayamıyor** | Yetki testi | **Evet** |

⚠️ **Matrise satır açılamayan iki senaryo:** *(a)* **takvim erişilemezliğinde** özel gün bloğunun davranışı — davranışın kendisi açık karardır (Bölüm 12) · *(b)* **aktivasyon ara penceresinde** başlayan üretimin sürüm ilişkisi — 13.2'de açılan yeni karardır. İkisi de karar kapandığında satır alır; **beklenen sonuç uydurulmamıştır.**

---

## 14. Uçtan uca işletim prosedürü

[GEREKİRSE]

⚠️ **Aşağıdaki yordamlar hedef işletim modelini tarif eder, bugünkü durumu değil.** Zincirin en pahalı adımı (üç araç araştırması) hedef modelde de elle işletilir ve **kaynakta bilinçli olarak öyle bırakılmıştır**; geri kalanını koşacak komut ailesinin **henüz bulunmadığı** ise **tek hakemden aktarımdır** `[BU SENTEZDE DOĞRULANMADI]` — doğrulaması Bölüm 17'nin ⑤ kalemine bağlanmıştır (*yönetici koşu yüzeyinin bugünkü varlık durumu*) — yöneticinin koşu yüzeyi ise karara bağlandı: ✅ **K-27 KAPANDI — A** (2026-08-21, Ek B) — Claude Code komut ailesi (Bölüm 5.1, 7.4). Adımlar *"bugün böyle işliyor"* diye okunamaz. ⚠️ **İstisna 14.4'tedir:** orada bugün elde bulunan dosyaların ve yürürlükteki sözleşme sürümlerinin **mevcut durumu** anlatılır — o satırlar hedef model değil, olgu kaydıdır.

⚠️ **Bu bölüm eşik üretmez ve rol ataması yapmaz.** Eşiği açık olan hiçbir katman kabul kriteri ya da kapatma ölçütü hâline getirilmemiş, kim hangi uyarıyı alır sorusu bu bölümde kapatılmamıştır (Bölüm 13.6, Bölüm 15).

#### İşletime hazırlık kontrol listesi — aktivasyon öncesi işaretleme yordamı

⚠️ **Liste, hazırlık koşullarının kapalı bir kümesi değildir** — o belgenin kendi listesidir ve aşağıdaki tablo onu **birebir** taşır; başka bir katmandan gelen bir hazırlık koşulunun bu listede bulunmaması, koşulun düştüğü anlamına gelmez. Maddelerin **büyük kısmı yeni yükümlülük getirmez** — her biri kendi evindeki ortak hükme, kaynakta karara bağlanmış bir gereksinime ya da hâlihazırda kayıtlı bir açık karara işaret eder. **Yeni olan, bunların aktivasyon öncesinde tek tek işaretlenen bir onay yordamına dönüştürülmesidir.**

| # | Madde | Evi ve statüsü |
|---:|---|---|
| 1 | Alt sektör kapsamı ve kök sektörü onaylandı | Bölüm 9 — atama modeli kaynakta onaylı karar |
| 2 | Bloklayıcı politika/teknik kararlar kapatıldı | **K-01a/K-01b · K-02** açık; ✅ **K-03 KAPANDI** (2026-08-17 kullanıcı kararı — paket türü üstündür). ⚠️ Kapanışın **sözleşme ayağı** Bölüm 14.4'te düzeltme kalemi olarak açıktır |
| 3 | Güncel brief üç araçta **aynı metinle** çalıştırıldı | Bölüm 7.1–7.2 — ortak, kaynakta karara bağlı |
| 4 | Mekanik kapı raporu üretildi | Bölüm 7.3 — ortak; kontrol kümesinin kesinleştirilmesi açık |
| 5 | İki bağımsız ve **kör** hakem raporu üretildi | Bölüm 7.4 — ortak, görev sözleşmesinde yazılı |
| 6 | URL örneklem kısıtları **dürüstçe** raporlandı | Denetçi sözleşmesinde yazılı; ortam ön kontrolü **K-14**'te açık |
| 7 | Alan bazlı sentez ve karar günlüğü üretildi | Bölüm 7.5 — ortak, sözleşmede yazılı |
| 8 | Aktif paketteki **bütün kalıplar** için karar kapsamı tam | ⚠️ Ölçülebilirliği **kalıcı kalıp kimliği** kararına bağlıdır (Bölüm 6.3) — kimlik yoksa "tam kapsam" güvenilir biçimde sayılamaz |
| 9 | Motor şema, kanıt, mutabakat ve güvenli fallback kontrollerini tamamladı | **K-22**'ye bağlı; kontrollerin her biri kendi açık kararına bağlı (Bölüm 7.7) |
| 10 | Canonical diff, değişim oranları ve bariyer sonuçları üretildi | **K-22** (✅ KAPANDI — A: motor Faz 1'de) + üç bariyerin ayrı ayrı benimsenmesi + canonical hash kuralı — bariyer ve hash kararları açıktır (Bölüm 6.4, 7.7) |
| 11 | Koşu sonucu `activation_eligible`; `blocked` veya `no_change` değil | **K-22**; sonuç tiplerinin kaydının yeri açık (Bölüm 6.5, 8.1) |
| 12 | Aday paket şema ve boyut doğrulamasından geçti | Bölüm 5.3, 7.6, 13.1 — ortak yazım kapısı |
| 13 | Paketsiz prompt regresyonu **byte-exact** geçti | Bölüm 13.3 — ortak, kaynakta zorunlu; fixture kümesinde legacy yolun koşulluluğu **K-06**'ya bağlı |
| 14 | Paketli prompt yapısal kontrolleri geçti | Bölüm 13.3 — tek hakemin katkısı, katman ayrımını düzelten kayıt |
| 15 | Kör çıktı değerlendirmesinde sektörel ayrışma gözlendi | ⚠️ **Bu madde bir sonuç iddia eder; katman ise otomatik kapı değildir.** Eşik konup konmayacağı **K-11 (b)**'de açıktır — bu belgede kapıya çevrilmez (Bölüm 8.2, 13.4) |
| 16 | Bloklayıcı mevzuat/güvenlik uyuşmazlığı veya eksik karar yok | Bloklayıcı alanların kesin listesi açık (Bölüm 7.7); *"eksik karar"* ölçütü 8. maddeyle aynı bağımlılığı taşır |
| 17 | Post sürüm damgası doğrulandı | Damganın gerekliliği ortak; **veri yeri K-07'de açık** (Bölüm 8.2) |
| 18 | Aktivasyon ve geri alma prosedürü test edildi | Test ortak (Bölüm 13.1); testin neyi doğrulayacağı **atomiklik ve yetkilendirme** açık kararlarına bağlı (Bölüm 8.2, 8.3) |
| 19 | Yönetici koşu özetini ve anlık görüntüyü **görerek** onayladı | Bölüm 7.8 — özetin içeriği ortak; onay/ret damgası ve snapshot'ın değiştirilemezliği açık |
| 20 | Onay anındaki aktif sürüm, motorun değerlendirdiği sürümle aynı | Base sürüm koruması — **yalnız bir hakemde**, açık karar (Bölüm 7.8, 8.2) |

⚠️ **Buradan iki ayrı açık karar doğar; tek kaleme bağlanamazlar.** Liste, dağınık duran yükümlülükleri **aktivasyon öncesi bir imza yüzeyine** çevirir; bu **yeni bir rol yükümlülüğüdür** ve tek hakem beyanıyla benimsenmiş sayılamaz. İkisi de **kullanıcı seviyesindedir:**

- **(a) Listenin işletim yordamına dâhil edilmesi** — aktivasyon öncesinde böyle bir işaretleme kapısı olacak mı; operasyon yükü ↔ unutma riski tradeoff'u.
- **(b) İşaretleme sorumlusu** — kapı kurulursa maddeleri kimin işaretleyeceği (turu koşan yönetici · teknik sahip · ikisi birlikte). **(a) alınıp (b) açık bırakılabilir; (a) reddedilirse (b) düşer** — ama (b)'nin cevabı (a)'nın içinde yazılı değildir ve rol tablosunu doğrudan ilgilendirir (Bölüm 15).

⚠️ **Maddelerin içeriği bu iki kararın kapsamında değildir:** her madde kendi evindeki statüsünü korur.

### 14.1 İlk kurulum / ilk yayımlama

**İki ayrı yordam vardır ve birbirinin yerine geçmez:** sistemin kurulumu **bir kez**, bir alt sektörün ilk paket koşusu ise **her yeni alt sektörde** yapılır.

#### (a) Sistemin kurulumu — bir kez

1. **Şema değişiklikleri** (teknik sahip) — iki yeni tablo, ham katmanın salt-ekleme tetikleyicisi, sektör başına tek aktif sürüm kısmi indeksi ve marka tablosundaki alt sektör alanı. Alan şeması Bölüm 6.2'de `[TASLAK]` statüsündedir; alt sektör kısıtının veri tabanında mı uygulamada mı zorlanacağı **K-08 (b)**'de açıktır.
2. **Veri ve migration doğrulaması** — Bölüm 13.1'in deterministik kontrolleri; kontrollerin dördü kaynakta uçtan uca başarı kriteri olarak yazılıdır.
3. **Kök kova korumaları** (teknik sahip) — sektör listesi ucunun ve kök sektör çözücüsünün kök-seviye filtreleri **ve** regresyon testleri. Kaynak bunu *"spec'e zorunlu iş"* olarak yazar. ⚠️ **Sıra bağlayıcıdır ve gerekçesi kaynakta ölçülmüştür:** çözücü haritası bugün bütün satırları içerir ve alt sektör satırı **tam eşleşmeyle de** yakalanır; koruma kurulmadan alt sektör satırı açılırsa kök kova invariantı bozulur.
4. **Alt sektör satırlarının açılması** (operatör) — mevcut sektör tablosunun içine, doğru kökün altına. Pilot kapsamı Bölüm 16'dadır.
5. **Tam sweep** — alt sektör satırları eklendikten sonra mevcut bütün markaların kök sektör değerleri ekleme öncesiyle karşılaştırılır; **spot kontrol yeterli sayılmaz** (Bölüm 13.1).
6. **Enjeksiyon çıpalarının bağlanması** (teknik sahip) — beş yüzey, kullanım talimatı satırı ve üretim sürüm damgası (Bölüm 5.3, 10.2). Damganın veri yeri **K-07**'de açıktır.
7. **Prompt yakalama düzeneğinin kurulması ve dondurulmuş fixture'ın alınması** — paketsiz markada **Katman-1** tam sweep'i byte-exact geçmeden hatta devam edilmez. Zorunluluk kaynakta karara bağlıdır; *"geçmeden devam yok"* biçimindeki kesin ifade yalnız bir hakemdedir, ancak aynı gereksinim diğer belgede işletime hazırlık maddesi olarak taşınır — **tamamlayıcıdır**. ⚠️ Bu altyapının Marka DNA işiyle **paylaşılıp paylaşılmayacağı K-20**'de açıktır (Bölüm 12).
8. **Veri/API regresyon kümesinin kurulması** — Bölüm 13.3'te ayrıştırılan üç kontrol (liste ucunun yanıtı, çözücünün eşlemesi, trend katmanının sorgu davranışı) prompt metni içermez ve Katman-1'in byte-exact karşılaştırmasının içine konulamaz. ⚠️ **Bu bir teknik iş kalemidir, açık karar değildir** — test tasarımı henüz yazılmamıştır ve kurulum sırasında yazılması gerekir (Bölüm 13.3'ten devreden kalem).

#### (b) Bir alt sektörün ilk paket koşusu

1. **Kapsam ve alt sektör adı** operatörce belirlenir (Bölüm 9).
2. **Brief güncel şablondan türetilir ve ilk koşuda temel paket + özel gün görevlerinin ikisi birden seçilir.** ⚠️ **Yalnız özel gün modu ilk pakette geçerli değildir** — sentez görev sözleşmesi o modda temel paketin sekiz alanını **mevcut paketten veya taslaktan** taşımayı şart koşar ve aktif paket boşsa `koru`/`guncelle`/`cikar` kararlarının hiçbirini uygulamaz: ilk koşuda bütün kararlar **ekle** evrenindedir. Kural sözleşmede yazılıdır ve bir hakem belgesi ilk koşuyu doğrudan iki görevle başlatır. *(Pilotun yalnız özel gün modunda olması bu kuralın istisnası değildir — orada temel paket araştırması hâlihazırda mevcuttur.)* Brief'lerin ve ham çıktıların yeniden üretimi **kaynakta karara bağlıdır (K-18)**: spec **ve** uygulama tamamlandıktan sonra, resmî hakem turundan hemen önce, tek seferde (Bölüm 7.2).
3. **Aynı brief metni üç araştırma aracında elle koşulur**; çıktılar kör adlandırmayla teslim edilir (Bölüm 7.2).
4. **Koşu dosyaları tek klasöre alınır** — klasör ve teslim sözleşmesi **K-17**'de açıktır (14.4).
5. **Mekanik kapı** koşar (Bölüm 7.3); elenen kaynak denetim dışıdır, notlu geçenin notları denetime girer.
6. **İki bağımsız kör denetçi** koşar (Bölüm 7.4).
7. **Alan bazlı sentez** aday paketi ve karar günlüğünü üretir; özgün sentez artefakt olarak saklanır. ⚠️ **İlk koşuda sözleşme modu farklıdır ve bu kaynakta yazılıdır:** aktif paket bulunmadığı için `koru`/`guncelle`/`cikar` uygulanmaz, bütün kararlar **ekle** evrenindedir ve çıkarılanlar listesi doğal olarak boştur. Özgün sentezin, motorun nihai adayının ve gerekçeli diff'in **ayrı saklanma biçimi** açıktır (Bölüm 7.2).
8. *(motorlu — **K-22**)* **Politika motoru** şema, karar kapsamı, kanıt, mutabakat, diff ve kalite kapılarını otomatik kontrol eder. `blocked` ise paket oluşturulmaz ve nedenler kaydedilir. ⚠️ **İlk paket koşusunda `no_change` sonucunun geçersiz sayılması ve veri/süreç hatası olarak işlenmesi yalnız bir hakemdedir** ve kendi açık kararıdır (Bölüm 6.4, 8.1).
9. **Yazım kapısı** — aday paket şema ve boyut doğrulamasından geçerse veri tabanına **yalnız `draft`** olarak yazılır (ortak, kaynakta karara bağlı).
10. **İşlevsel kapı** — **Katman-1** (paketsiz markada byte-exact prompt karşılaştırması) ve **Katman-2** (kör çıktı örneklemi). Katman-2 yöneticiye sunulur; **sonucu otomatik kapı değildir** ve bu belgede eşiğe çevrilmez (**K-11 (b)**).
11. **Yönetici onayı → aktivasyon** (Bölüm 8.2). ⚠️ **İlk pakette arşivlenecek önceki aktif sürüm bulunmaz.** Bölüm 8.2 iki adımlı sırayı **istisnasız** yazar; iki hakem belgesi de sırayı yalnız genel hâliyle verir ve ilk paketi ayrıca ele almaz. Sıra, ilk adımı **"önceki aktif sürüm varsa"** koşuluyla taşır; ilk pakette yalnız ikinci adım koşar. ⚠️ **Bu bir açık karar değildir:** ilk sürüm hâlini uygulanabilir kılan **teknik tutarlılık düzeltmesidir** ve Bölüm 8.2'ye de **geriye dönük olarak işlenmiştir** — iki bölüm arasında çelişki bırakılmamıştır. Bölüm 17'de bu nedenle karar satırı açılmaz.
12. **İlgili markalara alt sektör önerilir; kullanıcı teyidiyle atanır** — kaynakta onaylı karar (Bölüm 9).
13. **İlk üretimlerin gözlemi** — eşleşme, damga ve paket seçimi log'ları (Bölüm 13.6).

### 14.2 Periyodik güncelleme

- **Tetikleyici ve sıklık.** Kaynakta periyot **3 aydır**; iki hakem belgesi de **3 veya 6 ay** esnetmesini kaydeder ve ikisi de kesin değeri spec'e bırakır. **Periyodun global mi sektör bazlı mı yapılandırılacağı K-26'da açıktır.** Turu koşan **yöneticidir**; koşu yüzeyi karara bağlandı — ✅ **K-27 KAPANDI — A** (2026-08-21, Ek B): Claude Code komut ailesi.
- **Ortak çekirdek adımlar.** Yeni koşu kimliği açılır → güncel brief üç araçta yeniden koşulur → mekanik kapı ve iki denetçi turu tekrarlanır → **senteze aktif paket ve geçmiş çıkarma kararları da girdi olarak verilir** (görev sözleşmesinde yazılı) → aktif paketin her kalıbı ve her yeni aday için evrimsel karar üretilir → sentez adayı ve karar günlüğü ham katmana yazılır; katmanın **salt-ekleme** olması ortak ve kaynakta onaylı karardır (Bölüm 6.2).
- **Motorlu modelin ek adımları** `[SEA-2026-08-11]` **— K-22'ye bağlı:** motor kararları otomatik doğrular, güvenli fallback'leri uygular ve nihai diff'i üretir → sonuç `no_change` ise yeni sürüm oluşturulmaz ve koşu artefaktları saklanır → `blocked` ise aktif sürüm değişmez → `activation_eligible` ise aday `draft` yazılır ve özet yöneticiye sunulur → yönetici **tek kararla** aktivasyonu onaylar. Yöneticinin bu modelde yapmadığı şey, kalıpları tek tek incelemektir; bir hakem bunu değişikliğin **varlık nedeni** olarak kaydeder. ⚠️ **Zincirin son halkasını motorun devralmaması ilke olarak ortaktır (K-28):** motor yalnız taslak üretir, aktif sürüme dokunamaz — açık olan, bu sınırın **sunucu tarafında nasıl zorlanacağıdır** (Bölüm 7.7, 8.2).
- ⚠️ **Motorsuz modelde bu adımların yerini ne alır — kısmen çözülmemiştir.** Motorsuz zincir kaynakta yazılıdır (taslak → işlevsel kapı testi → operatör onayı → aktif) ve Bölüm 8.2'de kayıtlıdır; ancak o modelde sentez **açık sorular** üretir ve bunları operatöre çıkarır. **Operatörün kalıp-kalıp inceleme yükümlülüğü** yerine geçen hüküm kesinleştiği için karar geçmişine taşınmıştır (Ek B); buna karşılık **açık soruların operatörce tek tek kapatılmasının aktivasyon ön koşulu olup olmadığı çözülmemiştir** ve Bölüm 8.2'de kayıtlıdır. Bu bölüm o boşluğu kapatmaz.
- **Yeniden doğrulama kapsamı.** Her turda **Katman-1 yeniden koşulur** — paket içeriği değişse de paketsiz markanın prompt'u değişmemelidir. Gereksinim bir belgede bu cümleyle, diğerinde her aktivasyon öncesi işaretlenen hazırlık maddesi olarak taşınır; **tamamlayıcıdır.** Katman-2 örnekleminin **yeni sürüm için yenilenmesi** yalnız bir hakemdedir ve eşiği açıktır (**K-11 (b)**). **Mevzuat, tarih veya sayı içeren iddiaların URL örneklemine öncelikle alınması** denetçi görev sözleşmesinde yazılıdır.
- **Koşu maliyeti — ölçülmemiştir.** İlk turda **tur başına operasyon süresi** kaydedilecek ve Faz 1 aktif paket tavanı (başlangıç önerisi **en fazla beş paket**) bu ölçümden sonra revize edilecektir; bağ kaynakta karara bağlıdır **(K-13)**. **Hedef değeri belirlenmemiştir ve bu belgede kapıya çevrilmemiştir.**
- **Tur dışı acil güncelleme ayrı bir mekanizma gerektirmez** — aynı taslak → aktif hattı periyot dışında da koşulabilir; kaynakta onaylı karardır ve akışın kendisi Bölüm 11.6'dadır.

### 14.3 Kısmi güncelleme

**Bağımsız güncellenebilen iki parça vardır; statüleri aynı değildir.**

**(a) Yalnız özel gün turu — kaynak sözleşmesinde yazılı koşu modu.** Brief'te yalnız özel gün görevi seçilir; temel paketin sekiz alanı araştırılmaz ve aktif paketten **aynen taşınır**. ⚠️ Taşınan her alan için karar günlüğüne **`koru` satırı zorunludur** ve gerekçesi bu koşu moduna işaret eder — kural sentez görev sözleşmesinde yazılıdır, iki hakem belgesi de aynı modu taşır. Sistemde karşılığı olmayan dönem **pakete alınmaz, karar günlüğüne notlanır** (ortak ve sözleşmede yazılı); notun günlükteki temsili açık kararlardan biridir (Bölüm 6.5). Anahtar biçimi **K-01b**'de, takvime eksik gün eklenmesi **K-01a**'da açıktır.

**(b) Tek bir dönem veya alan düzeltmesi** (örneğin mevzuat değişikliği) — yeni bir sürüm olarak, karar günlüğünde yalnız değişen satırlarla. ⚠️ **Yalnız bir hakem belgesindedir** ve **yeni bir karar açmaz:** bu dalın varlığı, *"acil güncellemede tam araştırma turu zorunlu mudur?"* açık kararına bağlıdır (Bölüm 11.6) — tam tur zorunlu tutulursa (a) dışında bir kısmi mod kalmaz. ⚠️ Benimsenirse **alternatif kanıt ve denetim yolunun tanımlanması gerekir**: tur atlandığında karar günlüğünün kanıt satırını neyin dolduracağı ve denetçi turunun hangi girdiyle koşulacağı **Bölüm 11.6'da ölçülmüş bir boşluktur** (acil güncellemenin ayrı girdi kümesi hiçbir katmanda tanımlanmamıştır) ve bu bölümde de doldurulmaz. *"Tur atlanırsa denetçi turu da atlanır"* **hiçbir katmanın hükmü değildir** — denetçiler eski veya yeni kanıtla yeniden koşturulabilir.

⚠️ **Bu dal, aynı belgenin içinde bir tutarsızlık üretir ve tutarsızlık kaydedilmiştir.** Aynı hakem (b) dalını *"karar günlüğünde **yalnız değişen satırlarla**"* diye yazar; hemen ardından **kısmi güncellemenin tutarlılık kuralları** başlığı altında — yani her iki dalı kapsayan bir yerde — **taşınan alanlar için `koru` satırını zorunlu** tutar ve gerekçesini *"izlenebilirlik boşluğu kalmasın"* diye koyar. (b) dalında değişmeyen alanlar **taşınan alanlardır**; iki hüküm aynı anda uygulanamaz. Kuralın kaynağı olan sözleşme maddesi ise yalnız **özel gün moduna** özgüdür ve (b) dalını hiç tanımaz. **Tek belgenin kendi içinde kararsızlığıdır; iki pozisyon olarak taşınamaz** (2.3).

⚠️ **Buradan doğan açık karar, 11.6'nınkinden ayrıdır ve ona indirgenemez:** *"acil güncellemede tam araştırma turu zorunlu mudur?"* turun **koşulup koşulmayacağını** sorar; buradaki soru **kısmi bir sürümde değişmeyen alanların karar günlüğünde temsil edilip edilmeyeceğidir.** Tam tur zorunlu tutulsa bile bu soru cevapsız kalır — yalnız özel gün turunda da aynı temsil sorusu vardır ve orada sözleşme `koru` satırını zorunlu tutar. **Seviyesi tekniktir** (izlenebilirlik ↔ günlük hacmi); karar ID'si Bölüm 17 sweep'inde verilecektir.

**Tutarlılık kuralları:**

- **Kısmi güncelleme de bütün bir sürüm üretir.** Özel gün blokları ayrı bir tabloda yaşamadığı ve paket içeriği tek satırda bütün olarak sürümlendiği için, paketin bir bölümünün bir sürümde, başka bir bölümünün başka bir sürümde bulunduğu bir durum bu veri modelinde oluşmaz (Bölüm 6.2, 6.4). *Kuralı yalnız bir hakem yazar; dayandığı veri modeli ortaktır ve alan şeması `[TASLAK]` statüsündedir.*
- **Boyut tavanı her sürümde bütün olarak yeniden denetlenir** — yazım kapısı aday paketin tamamına bakar (Bölüm 5.3, 7.6).
- **Onay kapısı ve sıra kuralı kısmi güncellemede de korunur** (Bölüm 8.2).

### 14.4 Çalışma artefaktları ve klasörleme

**Koşu klasörünün yapısı ve teslim sözleşmesi Bölüm 7.2'de yazılmıştır ve burada tekrar edilmez** — klasör adının koşu kimliğiyle aynı olması dâhil, tamamı **K-17** kapsamında **öneri** statüsündedir. Bu alt başlık yalnız işletim tarafını ekler:

- **Motorlu modelde klasöre iki dosya daha girer** — koşunun **politika raporu** ve motorun **nihai adayı**. ⚠️ İkisi de yalnız bir hakemdedir, `[SEA-2026-08-11]` statüsündedir ve **kesin dosya/veri tabanı yerleşimleri iki ayrı açık karardır** (politika sonucunun/koşu kaydının yeri · özgün sentez ile nihai adayın ayrı saklanma biçimi — Bölüm 6.5, 7.2). Motorun kapanışına (✅ K-22 KAPANDI — A) rağmen yerleşim ayrıca kararlaştırılmalıdır.
- **Yeniden koşum dosyayı ezmemelidir.** Zaman aşımı, kısmi başarısızlık ve yeniden deneme hâlinde **yeni bir deneme kimliği mi yoksa yeni bir artefakt mı** üretileceği açıktır ve teslim sözleşmesinin parçasıdır (**K-17** ile bağlı, Bölüm 7.4). Ham katmandaki tekilleştirme kısıtı (**K-09**) bundan **ayrı bir karardır**.
- **Koşu klasörünün yanında iki kalıcı küme durur** — ikisi de kaynakta klasör envanteri olarak yazılıdır: kanonik brief şablonu ve ondan türetilmiş **donmuş** örnek brief'ler (yeni sektörde yalnız şablonun sektör bölümü doldurulur; türetilmiş örnekler kanonik değildir) · **hakem görev sözleşmesi dosyaları** — denetçi görevi **v1.1**, sentez görevi **v1.2**. Sürüm numaraları bir hakem belgesinin beyanıdır ve kaynakta da aynı sürümlerle anılır; bu sentezde dosyaların kendisine karşı denetlenmiştir.
- **Bugün elde bulunan ham çıktıların statüsü ve ilk-sürüm brief'in bulunmaması** Bölüm 7.2'de işlenmiştir; burada tekrar edilmez.

#### Görev sözleşmelerinin bilinen düzeltme kalemleri

⚠️ **Aşağıdakiler açık karar değil, düzeltme kalemidir** — alınmış kararların veya yürürlükteki hükümlerin görev sözleşmelerine yansımamasıdır. **Yeni karar ID'si verilmez ve kullanıcı kararına çevrilmezler**; sözleşmelerin sonraki sürümünde kapanırlar. Dördü de Bölüm 7'de doğdu ve evleri buradadır:

1. **Kök sektör rehberinin sentez girdisi olması** onaylı bir karardır, ancak yürürlükteki sentez sözleşmesinin girdi listesinde bulunmaz; karşılık gelen ek eklenene kadar açık kalır (Bölüm 7.5, 12). Aşağıdaki dördü de resmî hakem turunu bloklar; bu kalemin ayrıcalığı bloklayıcı olmasında değil, **alınmış bir kararın** sözleşmeye yansımamasında — kalan üçü sözleşmenin kendi iç boşluklarıdır.
2. **URL örnekleminin "sabit dokuz satır" yazımı**, eleme hâlinde düşen satır sayısıyla uyumlu değildir; sözleşme metni içi tutarsızlıktır (Bölüm 7.4).
3. **`[kopya-şüphesi]` bayrağının tüketim satırı** sentez sözleşmesinde yoktur; üst kural (marka cümlesinin aynen alınmaması) yürürlüktedir (Bölüm 7.5).
4. **Sentez özeti ile yönetici onay yüzeyi arasındaki ilişki** yazılı değildir: sözleşme çıktıyı *"onay ekranı için"* tanımlar, sonraki karar yüzeyi ise aynı listeyi sayı ve eşik-üstü görünümüne indirir; **artefakt ile ekran ayrımı hiçbir katmanda yazılı değildir** (Bölüm 7.8, 8.4).

5. 🆕 **Tür ↔ kategori çatışmasında karar yasağı — K-03 kapandı, sözleşme yansıtmıyor** *(2026-08-17)*. Yürürlükteki sentez görev sözleşmesi bu çatışmada sentezciye *"kararı VERME — iki tarafı ve eğilimini yazarak açık soruya düşür"* der. **K-03 kullanıcı kararıyla kapandı:** paketin tür etiketi üretim davranışında üstündür, kategori korunur (Bölüm 11.2). Sözleşmenin bir sonraki sürümünde uygulanacak beş adım şudur:
   *(a)* çatışma **algılanır** · *(b)* **K-03 politikası uygulanır** · *(c)* şemadaki zorunlu dönem türü alanı **paketin değeriyle** doldurulur · *(d)* çatışma ve uygulanan politika **karar günlüğüne** yazılır · *(e)* vaka **artık açık soru olarak sunulmaz**.
   ⚠️ **Kapsam sınırı bağlayıcıdır:** düzeltme **yalnız** tür ↔ kategori çatışmasını çözer. **Mevzuat çatışması, kapsam tercihi ve öteki çözülemeyen uyuşmazlıklar otomatik çözülmüş sayılmaz**; bütün çatışmalar için genel bir *"koşuyu blokla"* kuralı **kurulmaz**; motorun kararsız bıraktığı öğelerin akıbetini soran **K-23 kapanmaz**.
   ⚠️ **Yürürlükteki sözleşmede sessiz değişiklik yapılmaz** — düzeltme **sürümlü bir supersession kaydıyla** işlenir (mevcut sürüm arşivlenir, yeni sürüm K-03 atfını taşır). **Yeni karar ID'si verilmez ve kullanıcı kararına çevrilmez** — bu, alınmış bir kararın sözleşmeye yansıtılmasıdır.

⚠️ **Altıncı bir revizyon ihtiyacı karar sonucudur, drift değildir:** politika motoru benimsendiğine göre (✅ **K-22 KAPANDI — A**, 2026-08-21, Ek B) sentez sözleşmesinin *"karar merci sensin"* rol hükmü **revize edilmelidir** — motor kararları doğrulayan bir katman olarak sentezin üstüne biner.

### 14.5 Olay müdahalesi

**Hata nasıl fark edilir?** *(Dördü de zaten kurulmuş ya da kurulması kararlaştırılmış mekanizmaların iç ayrıntısıdır; bu nedenle gövdeye kaynaştırılmıştır. Sinyal kümesi kapalı ilan edilmez.)*

- **Paketsiz markada prompt farkı** — Katman-1 kırmızı. Deterministik olduğu için en güçlü sinyaldir; *"en güçlü sinyal"* nitelemesi tek hakemindir, kapının deterministikliği ortaktır (Bölüm 13.3).
- **Özel gün kalıplarının hiç görünmemesi** — eşleşmezlik log'unda yığılma. Log zorunluluğu ortak ve kaynakta karara bağlıdır; ⚠️ **yığılmayı eşiğe bağlayan bir uyarı katmanı yoktur** ve alarm katmanının benimsenmesi ile sorumlusu **açık karardır** (Bölüm 13.6).
- **Kötü veya yanlış içerik** — operatör ya da müşteri geri bildirimi. Hangi paket sürümünden geldiğinin bulunabilmesi **üretim sürüm damgasına** bağlıdır; damganın veri yeri **K-07**'de açıktır.
- **Markanın yanlış sektöre çözülmesi** — kök sektör çözücüsünün regresyon testi ya da marka listesinde gözlem (14.1 a/3).

**İlk güvenli aksiyon: paketi geri çekmek (deaktivasyon).** Alt sektördeki markalar tek işlemle paketsiz yola döner; kod dağıtımı gerekmez ve veri kaybı olmaz. ⚠️ **Bu prosedür bir açık karara bağlıdır:** deaktivasyonun desteklenen bir geçiş olup olmadığı Bölüm 8.1'de açıktır ve **tek hakem beyanıyla çözülmüş sayılamaz.** ⚠️ **Kararın kapsamı bu bölümde genişler:** bir alt sektörün **ilk** paketinde geri dönülecek önceki sürüm bulunmadığı için geri alma uygulanamaz; o durumda paketli yoldan çıkışın tek yolu deaktivasyondur. *(Türetilmiş sonuç: iki hakem belgesi ve dokuz kaynak dosya harf duyarsız tarandı — `önceki sürüm yok` · `geri alınacak sürüm` · `ilk sürümde geri` · `ilk pakette geri/rollback` kalıpları için **0 isabet**; sonuç iki mekanizmanın Bölüm 8'deki tanımlarından çıkarılmıştır, devralınmamıştır.)*

**Kim bilgilendirilir?** Tek hakem belgesi ürün ve operasyon sahibi olan operatörü, teknik hatada ise teknik sahibi adlandırır. ⚠️ **Bu bölüm rol ataması yapmaz:** koşu ve aktivasyon rolünün ikiye bölünüp bölünmeyeceği açık karardır (Bölüm 7.2, 15) ve alarm katmanı benimsenirse uyarıyı kimin alacağı da onun parçasıdır (Bölüm 13.6). **İkisi ayrı kararlardır ve ayrı ayrı seçilebilirler.**

**Geri alma veya kapatma ölçütü:**

- **Paketsiz markada tek bayt fark → pazarlıksız geri alma.** Ölçüt yalnız bir hakemdedir ve Bölüm 8.3'te tetikleyici olarak kayıtlıdır; bu bölümde yeniden açılmaz.
- **Paketli markada kalite düşüşü → önceki sürüme geri alma veya deaktivasyon**; kararı yönetici verir. ⚠️ **Kalite düşüşünün ölçütü ölçülmemiş ve tanımlanmamıştır** — terim iki hakem belgesi ve dokuz kaynak dosya içinde harf duyarsız tarandığında **yalnız bir belgede, üç satırda** geçer ve üçünde de bir **tespit sinyali** olarak, eşiksiz kullanılır. Çıktı kalitesi katmanının eşiği zaten açıktır (**K-11 (b)**); bu belgede buradan bir kapatma eşiği türetilmez.
- **Mevzuat hatası → acil.** Paket geri çekilir ve tur dışı düzeltme koşulur (Bölüm 11.6). Tur dışı koşumun **tam araştırma turunu atlayıp atlayamayacağı** açık karardır.

⚠️ **Olay müdahalesinde geri alınan birim paket sürümüdür, dağıtım değildir** (Bölüm 8.3) — bu mimarinin acil durum maliyetini düşük tutan özelliği budur ve iki belgede de aynı yöndedir.

---

## 15. Rol ve sorumluluklar

[ZORUNLU]

**Tablo kapalı bir rol kümesi ilan etmez.**

⚠️ **Bu tablo hedef işletim modelinin rol dağılımıdır, bugünkü sistem olgusu değildir.** Mekanik kapı, iki denetçi, sentez ve içerik doğrulayıcı **aktarılan son duruma göre kurulmamıştır** — Bölüm 5.1'de *yeni* olarak işaretlidirler; ⚠️ *"bugün kurulmamıştır"* diye okunamaz. ⚠️ **Politika motoru bu listeye AYNI statüyle girmez:** o bir `[SEA-2026-08-11]` bileşenidir ve **aktarılan kümenin üyesi değildir** — 2026-07-11 taraması onu **aramamıştır** (kavram taramadan sonra, 2026-08-11'de doğdu). Kaynak katmanında bulunmadığı **ölçülmüştür** (provenans olgusu); **güncel sistemde var olup olmadığı bu sentezde ölçülmemiştir** → `[BU SENTEZDE DOĞRULANMADI]`. ⚠️ *"Kaynakta yok"* → *"bugün kurulmamış"* **çıkarımı yapılamaz**. ⚠️ **Yönetici koşu yüzeyi** için iddia **tek hakemden** gelir → Bölüm 17'nin **⑤ doğrulama kalemi** `[BU SENTEZDE DOĞRULANMADI]`. Bugüne kadar fiilen koşmuş olan roller araştırma araçları ve operatördür; ayrıca **gayriresmî bir ön hakem turu** koşulmuştur. **Resmî denetim ve sentez turu henüz koşulmamıştır** (Bölüm 16).

⚠️ **İşaretlenmiş şablon sapması — tabloya iki sütun eklenmiştir.** Şablonun tablosu `| Rol / sistem | Sorumluluk | Karar yetkisi | Teslim / çıktı |` sütunlarına sahiptir. **`Yapamayacağı şey`** sütunu yalnız bir hakem belgesinde bulunur ve kayıp kontrolünde korunması zorunlu sayılmıştır; içeriği karar yetkisiyle **aynı eksende değildir** (*"marka cümlesini aynen almak"* bir yetki sınırı değil, brief sözleşmesinde yazılı bir yasaktır), bu yüzden karar yetkisi sütununa katlanamaz. **`Kaynak statüsü`** sütunu ise her hükmün **tek hakemde mi, iki hakemde mi, kaynakta mı** olduğunu satırın kendi içinde taşır. Sapma bilinçlidir ve **sessizce değil, işaretlenerek** yapılmıştır.

| Rol / sistem | Sorumluluk | Karar yetkisi | Yapamayacağı şey | Teslim / çıktı | Kaynak statüsü |
|---|---|---|---|---|---|
| **Yönetici / operatör** | Sektör seçimi · brief'in sektör bloğunu doldurma · üç araştırma koşusunu **elle** yürütme ve çıktıları yükleme · turu tetikleme · koşu sonucunu ve özet diff'i inceleme · aktivasyon, ret ve geri alma | **Son aktivasyon / ret ve geri alma kararı.** ⚠️ Motorlu modelde kalıp-başına karar yetkisi motordadır (**K-22**) | *Normal koşuda* yüzlerce kalıbı **tek tek** sentezlemek · politika motorunu **atlayarak** aktive etmek | Doldurulmuş brief · yüklenen üç ham rapor · onay / ret kararı | **Ortak · kaynakta karara bağlı** (*veri tabanına yalnız taslak yazılır; aktife geçiş operatör onayıyla*). ⚠️ **Yapamayacağı-şey sütunu yalnız bir hakemdedir** ve *normal koşu* nitelemesi de onundur; **motorsuz modelde sentezin operatöre çıkardığı açık soruların akıbeti çözülmemiştir** (Bölüm 8.2). ⚠️ **Rolün ikiye bölünmesi açık karardır** — tablonun altına bakınız |
| **Araştırma araçları (3 adet)** | Aynı brief'le **bağımsız** derin araştırma koşusu; her bulguyu kaynak göstererek yazmak | Karar yetkisi **yok** | **Kaynaksız tahmin üretmek** · bir markanın cümlesini **aynen almak** · sosyal platformlardan içerik toplamak veya kopyalamak | Üç ham araştırma raporu | ⚠️ **Rol satırı yalnız bir hakemde.** Buna karşılık **üç yasağın üçü de brief sözleşmesinde yazılıdır** ve bileşen olarak iki belgede de vardır (Bölüm 5.1) |
| **Mekanik kapı (`brief-doctor`)** | Biçim ve sözleşme kurallarının **dil modeli olmadan** kontrolü | Deterministik **eleme / not** kararı | **İçerik doğruluğuna hakemlik etmek** | Eleme ve not raporu — denetim adımının girdisi | **Ortak · kaynakta karara bağlı** (*mekanik kontroller dil modeline verilmez*) |
| **Denetçi-1 / Denetçi-2** | Kaynakların **iddia düzeyinde** bağımsız denetimi · URL örneklemi · risk bayraklama | **Karar YOK** — sınıflandırır, bayraklar ve öneri sunar | **Nihai paket kararı vermek** · birbirinin çıktısını görmek · hangi raporun hangi araca ait olduğunu **tahmin etmek** | Yapılandırılmış denetim tablosu | **Ortak · kaynakta karara bağlı** — denetçi görev sözleşmesi *"karar vermezsin"* der ve körlüğü aynı yerde kurar |
| **Sentez** | İki denetim tablosunu **alan alan** hizalamak · kalıp-başına evrimsel karar · boyut disiplini · aday paket ve gerekçeli karar günlüğü üretmek | **Karar mercii — aktivasyon hariç**; sözleşme cümlesi birebir budur | Adayı **doğrudan** `active` yapmak · *(motorlu modelde)* politika motorunu atlamak | Aday paket JSON · karar günlüğü · açık sorular · onay özeti | **Ortak · kaynakta karara bağlı.** ⚠️ Adayı **doğrudan `draft` yapamaması** yalnız bir hakemdedir; ortak olan `active`e geçirememesidir. ⚠️ **Motor benimsendi (✅ K-22 KAPANDI — A, Ek B) — bu rol hükmü revize edilmelidir** (Bölüm 14.4) |
| **İçerik doğrulayıcı** | Alan şeması, boyut tavanı ve özel gün anahtarı uyumunun zorlanması | **Kabul / red** (deterministik) | *(iki belgede de yazılı değil)* | Yazım izni veya hata listesi | Bileşen **ortak** (Bölüm 5.1); **rol satırı yalnız bir hakemde.** Doğrulayıcının betik değil şema modeli olması karar geçmişindedir (Ek B) |
| **Politika motoru** `[SEA-2026-08-11]` | Karar kapsamı, kanıt, mutabakat, diff, değişim bariyeri ve kalite kapılarının otomatik doğrulanması; güvenli fallback ile nihai adayın üretilmesi | Kural sınırları içinde **karar uygulama**; **`active`e geçirme yetkisi YOK** (**K-28**) | **Yeni semantik kanıt uydurmak** · yönetici son onayı olmadan `active` yapmak | Yeni taslak · karar günlüğü · özet diff · koşu raporu | **İki hakemde de var ve ikisinde de sonradan eklenen analiz statüsünde** — motor kavramı dokuz kaynak dosyanın hiçbirinde geçmez (harf duyarsız tarandı, **0 isabet**). **Fazı K-22**; yetki sınırının **sunucu tarafı zorlaması açıktır** |
| **Uygulama / arka uç katmanı** | Veri bütünlüğü · paket seçimi · enjeksiyon · izlenebilirlik | *(rol tablosunda yazılı değil)* | **Eksik marka gerçeğini uydurmak** | Çalışan seçim ve enjeksiyon yolu | ⚠️ **Rol satırı yalnız bir hakemde.** Uydurma yasağının kendisi iki belgede de en üst öncelik kuralıdır (Bölüm 4.6) |
| **Teknik sahip** | Migration · koruma noktaları · enjeksiyon · üretim sürüm damgası · kapı koşum altyapısı | **Teknik tasarım** — doğruluğu **inceleme zinciriyle** belirlenir, operatör onayıyla değil (Bölüm 4.5) | *(yazılı değil)* | Kod · testler · regresyon raporu | **Rolün kendisi açık değildir:** şablon bu alanı zorunlu tutar ve Bölüm 14.1 rolü üç kurulum adımında **fiilen kullanır**. ⚠️ Açık olan **atamadır** — *kim / hangi ekip*; tek hakemin somut önerisi aşağıdaki sahiplik satırındadır ve diğer hakemde karşılığı yoktur (*teknik sahip* **0 isabet**) |
| **İnceleme (review) zinciri** | Teknik doğruluğun bağımsız denetimi. ⚠️ **Zincirin bileşenleri tek hakemde adlandırılmıştır:** Codex adversarial review · `/review-claude-codex` · `/security-review-claude-codex` — **öneri olarak korunur, kesinleşmiş tasarım değildir** | Bulgu üretir. ⚠️ ***"Bulguların kabulü teknik sahiptedir"* yalnız bir hakemdedir** — kabul yetkisinin kimde olduğu **açık karardır**, aşağıya bakınız | *(yazılı değil)* | İnceleme raporları *(tek hakemde adlandırılmış)* | **İlke normatiftir ve bu belgede zaten yazılıdır** (Bölüm 4.5: *şema, imza ve algoritma doğruluğu onay yüzeyine değil inceleme zincirine aittir*) — **kullanıcı kararına çevrilmez.** ⚠️ Zincirin **rol satırı**, **bileşen adları** ve **kabul yetkisi** yalnız bir hakemdedir: `/review-claude-codex` ve `/security-review-claude-codex` diğer hakemde ve dokuz kaynakta **0 isabet** verir (harf duyarsız) |
| **Takvim beslemesi (yıllık iş akışı)** | Sistem özel gün tablosunun doldurulması | — | *(yazılı değil)* | Takvim satırları | Beslemenin **varlığı kaynakta yazılıdır**; **rol satırı yalnız bir hakemde.** **K-01a** ile takvime eklenecek günler bu beslemeye de işlenir |
| **Marka kullanıcısı (Otomaix müşterisi)** | Onboarding'de önerilen **alt sektörü teyit etmek** | Yalnız **kendi markasının ataması** | **Sektör paketi kalıplarını değerlendirmek** · sürümleme kararına katılmak · aktivasyon onayı vermek · paket bakımını görmek veya tetiklemek | `brands.sub_sector_id` | **Ortak** — iki hakem aynı sınırı iki ayrı biçimde yazar: biri yasak listesi olarak, diğeri *"müşterinin bu süreçte hiçbir rolü yoktur"* cümlesiyle. Teyit akışı **kaynakta karara bağlıdır** (Bölüm 9); teyit bileşeninin **yeri K-19'da açıktır** |

#### Koşu ve aktivasyon rolünün bölünmesi — açık karar

- Bir hakem **tek rol** yazar (*Otomaix yöneticisi / operatör*) ve açık kararların muhatabı olarak da aynı rolü adlandırır. Diğeri rolü ikiye ayırır: **turu koşan ve aktive eden yönetici** ↔ **kapsam, politika ve risk kabulünü bir kez koyan ürün sahibi**; *"aynı kişi olabilirler, ama yetkileri farklıdır."*
- **Ortak olan, insan yetkisinin son onaya indirilmesidir;** bölünme bu ortak hükmü değiştirmez, yalnız onayın **kime** ait olduğunu böler.
- **Karara bağlı davranışlar:** Bölüm 8.1'in *yetkili aktör* sütunu · olay müdahalesinde kimin bilgilendirileceği (Bölüm 14.5) · görev sözleşmelerindeki **operatör** teriminin karşılığı · alarm katmanı benimsenirse uyarıyı kimin alacağı (Bölüm 13.6).

⚠️ **Belge-içi tutarsızlık kaydı.** Bölmeyi yazan hakemin **kendi rol tablosunda iki satır aynı işi taşır:** biri hem ürün ve politika kararlarını hem aktivasyonu üstlenir ve *"aktivasyon yalnız burada"* der; diğeri — sonradan eklenen analizle gelen satır — yine sektör seçimi ve aktivasyon taşır ama *"yalnız aktivasyon onayı"* der. Eski tablo satırı ile sonraki rol netleştirmesi **kendi içinde çatışır.** Bu bir hakemler-arası karşıtlık değildir ve **iki pozisyon olarak taşınamaz**: kaynağın kendisi kararsızdır. Yukarıdaki tablo bu nedenle **tek bir yönetici / operatör satırı** taşır ve bölünmeyi karar olarak dışarıda bırakır.

#### Karar zinciri

Motorlu modelde zincir şudur `[SEA-2026-08-11]`: **denetçiler (öneri) → sentez (karar) → politika motoru (kontrol ve uygulama) → yönetici (yalnız aktivasyon)**; insan denetim noktası zincirin **sonunda tek noktada** kalır. ⚠️ **Zinciri bu diziliş hâlinde yalnız bir hakem yazar**, ancak halkaların hepsi iki belgede de vardır ve **son halkanın motora devredilememesi ortaktır** (**K-28**). Motorsuz modelde zincir **sentez → işlevsel kapı → operatör onayı → aktif**'tir ve kaynakta karara bağlıdır. Yürürlükteki model **motorlu modeldir** — ✅ **K-22 KAPANDI — A** (2026-08-21, Ek B). ⚠️ Motorsuz modelde sentezin ürettiği **açık soruların operatörce kapatılmasının aktivasyon ön koşulu olup olmadığı çözülmemiştir** (Bölüm 8.2); bu bölüm o boşluğu kapatmaz.

#### Körlüğün rol karşılığı

**Araştırma aracı ile ham rapor arasındaki eşleme yalnız operatörde kalır** — kaynakta ve denetçi görev sözleşmesinde yazılıdır; denetçiler üsluptan kimlik çıkarımı yapmaz. Bu, operatörün **rol yükümlülüğüdür**: körlüğü koruyan taraf odur. ⚠️ Eşlemenin **kalıcı bir kayda** yazılıp yazılmayacağı ve kimin okuyabileceği açık karardır (Bölüm 6.2) — bir **erişim ve yetkilendirme tasarımı** sorusudur ve körlük gereksinimiyle zorunlu olarak çelişmez.

#### Sahiplik

- **Ürün sahibi:** Eray. Kaynak, operatörü **adıyla** anar ve operatör kararlarını ona bağlar. ⚠️ **Ayrı bir *ürün sahibi* rolü yalnız bir hakemdedir** — terim diğer hakemde ve dokuz kaynak dosyada **0 isabet** verir (harf duyarsız); rolün bölünmesi açık karardır.
- **Teknik sahibi:** rolün **varlığı** açık değildir — şablon bu alanı zorunlu tutar ve Bölüm 14.1 rolü üç kurulum adımında (şema değişiklikleri · kök kova korumaları · enjeksiyon çıpaları) **fiilen kullanır**. ⚠️ Açık olan **atamadır:** *kim / hangi ekip*. **Tek hakemin somut önerisi: spec → plan → uygulama hattını yürüten Claude Code hattı, adversarial review ile birlikte.** Bu öneri diğer hakemde ve dokuz kaynak dosyada **karşılıksızdır**; atama **kullanıcı seviyesinde açık karardır** ve öneri korunur.
- **Operasyon sahibi:** üç aylık turun **elle** koşulan araştırma adımı dâhil operatördedir. **Araştırmanın manuel olması ve operatörde durması kaynakta yazılıdır**; ⚠️ *"operasyon sahibi"* adlandırması yalnız bir hakemdedir. **Tur başına operasyon süresi ölçülmemiştir** ve Faz 1 aktif paket tavanı (**K-13**) bu ölçüme bağlıdır.
- **Güvenlik / hukuk / veri onayı:** paketlerin **ürünleştirilip satılması** ve **sosyal platformlardan veri toplama** kaynakta **kapsam dışıdır** ve ikisi de hukuki görüş veya değerlendirme eşiğine bağlanmıştır. ⚠️ Buna karşılık *"Faz 1'de ayrı hukuk onayı gerekmiyor; yalnız kamuya açık yayımlanmış kaynaklardan derleme yapılıyor"* değerlendirmesi **yalnız bir hakemdedir** ve `[BU SENTEZDE DOĞRULANMADI]`. Bu bir **risk kabulüdür**; benimsenmesi **açık karardır** ve seviyesi ürün/risktir.
- **On-call / olay sahibi:** ⚠️ *"ayrı bir nöbet düzeni yoktur; olay müdahalesi operatördedir"* **yalnız bir hakemdedir** — *on-call* kalıbı diğer hakemde ve dokuz kaynakta **0 isabet** verir (harf duyarsız). ⚠️ **Nöbet düzeninin bulunmaması bir yükümlülük yaratmaz, ama *"olay müdahalesi operatördedir"* bir rol atamasıdır** ve rolün ikiye bölünmesi kararına bağlıdır; **kimin bilgilendirileceği ise ayrı bir açık karardır** (aşağıya bakınız). En ucuz acil kolun **paketi geri çekmek** olduğu aynı belgededir; **deaktivasyonun desteklenen bir geçiş olup olmadığı Bölüm 8.1'de açık karardır** ve bu satır o karar kapanmadan kesinleşmez.

#### Yetki seviyesi ayrımı — açık karar değildir

Operatöre **ürün seviyesinde** karar sorulur (kapsam, politika, risk kabulü, iş yükü); **şema, imza ve algoritma doğruluğu onay yüzeyine değil inceleme zincirine aittir.** ⚠️ **Bu ayrım burada açılmaz — Bölüm 4.5'te normatif olarak zaten yazılıdır** ve teknik doğruluk kullanıcı onayıyla değil kanıt, test ve teknik incelemeyle belirlenir. Ayrımın **kullanıcı kararına çevrilmesi** yanlış olurdu: bu bölüm onu yalnız **rol karşılığıyla** görünür kılar — doğruluğu üreten taraf teknik sahiptir, denetleyen taraf inceleme zinciridir, operatör ikisinin de onay mercii değildir.

⚠️ **Ayrımın ikinci yarısı düşürülemez: operatöre FYI.** Aynı hüküm, doğruluğun onaya sunulmamasının yanında sonucun **operatöre bilgi olarak geçilmesini** de yazar. ⚠️ **Hükmün sınırı aynen korunur:** kaynak yalnız **geçirmeyi** yazar — operatörün bunu **okumasını zorunlu tutmaz**, ve buradan bir okuma yükümlülüğü **türetilmez**. Hüküm **yalnız bir hakemdedir** (`fyi` kalıbı diğer hakemde ve dokuz kaynak dosyada **0 isabet**, harf duyarsız); **benimsenmiş sayılamaz, ama sessizce de düşürülemez.**

⚠️ **Yüzey bağı açık kalır ve kararın kapsamındadır.** Bölüm 4.5 operatörün gördüğünü **iki şeyle** sınırlar: koşu sonucu ve özet diff. FYI **ayrı bir teslim yüzeyi** olacaksa o sözleşmenin genişletilmesi gerekir; **mevcut iki çıktıdan birinin içinde** taşınacaksa operatör tarafında yeni bir yüzey de, yeni bir yükümlülük de doğmaz. İki hakem belgesinde de dokuz kaynak dosyada da bu bağı kuran hüküm **bulunamadı**. **Seviyesi kullanıcıdır** — gerekçe operatörün iş yükü değil, **operatör yüzeyinin kapsamıdır**: karar Bölüm 4.5'in yüzey sözleşmesine dokunur.

⚠️ **Bulguların kabul yetkisi ayrı ve açık bir karardır.** *"Bulguların kabulü teknik sahiptedir"* hükmü yalnız bir hakemdedir ve **teknik sahip atamasına indirgenemez:** atama kabul edilip kabul yetkisinin başka bir yerde (ör. operatörde ya da zincirin kendisinde) durması istenebilir; tersi de mümkündür. Yetki dağılımı sorusu olduğu için **kullanıcı seviyesindedir**.

⚠️ **Geriye kalan tek kalem teknik tasarımdır ve kullanıcı kararı değildir:** zincirin ürettiği **inceleme raporlarının nerede saklanacağı** ve izlenebilirlik zincirine bağlanıp bağlanmayacağı için **iki hakem belgesinde ve dokuz kaynak dosyada saklama hükmü bulunamadı**. ⚠️ **Ham kanıt katmanındaki `review` türüyle karıştırılmamalıdır:** o tür **denetçi** çıktısını taşır (Bölüm 6.2), inceleme zincirinin raporunu değil. **Teknik iş kalemidir**, karar sayımına girmez; evi spec seansıdır.

#### Olay müdahalesinde bilgilendirme hedefi — açık karar

Bölüm 14.5 bu kalemi buraya devretti ve **kendi rol atamasını yapmadı.** Tek hakem belgesi hedefi adlandırır: **ürün ve operasyon sahibi olan operatör**, *teknik hatada* ise **teknik sahip**. Tek hakem beyanıyla benimsenmiş sayılamaz.

⚠️ **Bu kalem başka kararların sonucuna indirgenemez ve ayrı bir kullanıcı kararıdır.** Rol ikiye bölünmese bile hedefin adlandırılması gerekir; bölünürse hedefin hangi role (ya da ikisine birden) gideceği ayrıca seçilir. Alarm katmanının sorumlusundan da ayrıdır: alarm **eşik aşımında uyarı üretimini**, bu karar **olay anında kimin haberdar edileceğini** sorar; biri benimsenip diğeri reddedilebilir. Teknik hata dalı ise **teknik sahip atamasına** bağlıdır ama onunla aynı soru değildir.

#### Bu bölümde kapanmayanlar

| Kalem | Durum |
|---|---|
| Koşu ve aktivasyon rolünün ikiye bölünmesi | **Açık** — tek hakemde; ortak olan yalnız son onaya indirgeme |
| **Teknik sahip ataması** — kim / hangi ekip | **Açık** — rol zorunlu ve kullanımda; açık olan yalnız **atama**. Tek hakemin somut önerisi korunmuştur |
| Olay müdahalesinde bilgilendirme hedefi | **Açık** — tek hakemde adlandırılmış; rol bölünmesinden ve alarm sorumlusundan **ayrı seçilebilir** |
| **İnceleme bulgularının kabul yetkisi** — kimde | **Açık** — tek hakemde; **teknik sahip atamasından ayrı seçilebilir** |
| **Teknik doğruluk sonucunun operatöre FYI olarak geçilmesi** | **Açık** — tek hakemde; **okuma yükümlülüğü yazılı değildir.** Kapsamında **yüzey bağı** vardır: ayrı yüzey mi, Bölüm 4.5'in iki çıktısının içinde mi |
| İnceleme raporlarının saklanması ve izlenebilirliğe bağlanması | **Açık ama kullanıcı kararı DEĞİL** — teknik iş kalemi; ilkenin kendisi Bölüm 4.5'te normatiftir |
| *"Faz 1'de ayrı hukuk onayı gerekmiyor"* değerlendirmesinin benimsenmesi | **Açık** — tek hakemde, risk kabulü |
| İşletime hazırlık listesinin işaretleme sorumlusu | Bölüm 14'te açıldı; **rol ayağı buradadır**, yeni karar açılmaz |
| Alarm katmanının benimsenmesi ve sorumlusu | Bölüm 13'te açıldı; **rol ayağı buradadır**, yeni karar açılmaz |
| Aktivasyon ve geri alma yetkisinin teknik olarak zorlanması | Bölüm 8.2'de açık; rol tablosu yetkiyi **kime** verdiğini yazar, **nasıl zorlandığını** yazmaz |
| Motorun yetki sınırının sunucu tarafında zorlanması (**K-28**) | İlke ortak; **zorlama ayağı açık** |
| Yönetici koşu yüzeyi (**K-27**) | ✅ **KAPANDI — A** (2026-08-21, Ek B): Claude Code komut ailesi; ⚠️ ailenin bugünkü varlığı doğrulanmamıştır |
| Paket içeriğini kimin okuyabileceği (**K-16**) | Açık — **rol tablosu okuma yetkisi atamaz**; ham katmanın okuma yetkisi de açıktır (Bölüm 6.2) |

⚠️ **Rol tablosu bu kararların hiçbirini kapatmaz.** Tablo, kapanmış hükümleri normatif olarak yazar; kapanmamış olanları **satırın kendi içinde** işaretler ve karar olarak Bölüm 17'ye taşır.

---

## 16. Pilot ve mevcut durum

[GEREKİRSE]

⚠️ **Bu bölümde risk ters yönde işler.** Belgenin diğer bütün bölümlerinde tehlike hedef modeli bugünkü olgu gibi yazmaktı; **bu bölüm zaten bugünkü olguyu yazar**, dolayısıyla tehlike hedef modelden gelen hükümleri (politika motoru · kalıcı kalıp kimliği · koşu sonucu değerleri · komut ailesi · yeni tablolar) mevcut duruma **karıştırmaktır**. Bir hakem bu ayrımı kendi metninde açıkça yapar: politika motoru, sabit kalıp kimliği ve koşu sonuçları **bu pilot dosyalarında yoktur** ve **pilotta doğrulanmış sayılamazlar** `[SEA-2026-08-11]`. Bu belge o ayrımı korur: kurulmamış bileşenler bu bölümde **mevcut sayılmaz**, hazırlık durumları Bölüm 5.1'in *mevcut / yeni* işaretine bağlanır.

⚠️ **Bu bölümde iki iddia sınıfı ayrı statü taşır ve ayrım kaynağın kendisinde yazılıdır.** Ortak kaynak doküman, 2026-07-11 kod/DB taramasının kapsamını tarif ederken **pilotun içerik ve mevzuat iddialarını kapsamın dışında bıraktığını** açıkça yazar (*"kod/DB'ye karşı test edilemez — hakem hattının konusu"*). Sonuç:

- **altyapı, şema ve kod olguları** → `[AKT·KAYNAK · 2026-07-11]`; 2.1 md.2 aynen geçerlidir, bu sentezde canlı sistem yeniden taranmamıştır;
- **pilotun içerik ve mevzuat bulguları** → `[BU SENTEZDE DOĞRULANMADI]`; bunlar yalnız taze doğrulanmamış değildir, **kaynağın kendi taramasının da dışındadır** ve doğrulanacakları yer **resmî denetim turudur**.

### 16.1 Mevcut sistem / hazırlık durumu

#### Bileşen hazırlığı — envanteri Bölüm 5.1'dedir

Hangi bileşenin mevcut, hangisinin yeni olduğu Bölüm 5.1'in bileşen tablosunda **satır satır** işaretlidir ve burada tekrar edilmez. Bu bölümün eklediği üç kayıt şudur:

- ⚠️ **Hazırlık envanterinin kendisi yalnız bir hakemdedir** — diğer belgede karşılık gelen liste yoktur. Buna karşılık **satırlarının içeriği** kendi bölümlerinde ortak ya da kaynak hükümdür; envanterin katkısı yeni bir olgu değil, olguların **hazırlık ekseninde toplanmasıdır**.
- ⚠️ **Aynı envanter, koşu yüzeyini bir komut ailesinin adıyla eksikler arasında sayar.** Yüzeyin ne olacağı karara bağlandı: ✅ **K-27 KAPANDI — A** (2026-08-21, Ek B) — Claude Code komut ailesi. Sentez sırasında bir hakem komut ailesini varsayıyor, diğeri açık karar olarak kaydediyordu. **Aktarılan son duruma göre** eksik olan **koşu yüzeyidir** `[BU SENTEZDE DOĞRULANMADI]` — iddia bu sentezde ölçülmemiştir ve Bölüm 17'nin ⑤ kalemine bağlanmıştır; belirli bir komut ailesinin eksikliği bu belgede olgu olarak yazılmaz.
- ⚠️ **Zorunlu iş ile karara bağlı iş ayrılmalıdır.** **Aktarılan son duruma göre** kurulmamış bileşenlerin bir kısmı açık kararlara bağlıdır — alt sektör teyit bileşeninin **yerleşimi** **K-19**'da, üretim sürüm damgasının **veri yeri** **K-07**'de açıktır; koşu yüzeyi ise karara bağlandı — ✅ **K-27 KAPANDI — A** (2026-08-21, Ek B): Claude Code komut ailesi (**bugünkü varlığı doğrulanmamıştır**, spec seansında taze doğrulanır). ⚠️ **Politika motoru bu aktarılan kümenin üyesi DEĞİLDİR** — `[SEA-2026-08-11]` bileşenidir ve 2026-07-11 taraması onu **aramamıştır**; kaynakta bulunmadığı ölçülmüştür (provenans), **güncel varlığı bu sentezde ölçülmemiştir** `[BU SENTEZDE DOĞRULANMADI]`. Fazı karara bağlandı: ✅ **K-22 KAPANDI — A** (2026-08-21, Ek B) — motor **Faz 1'de** kurulur. **Buna karşılık iki bileşenin kurulması karara bağlı değildir, zorunludur** (Bölüm 5.1'de *Yeni*): içerik doğrulayıcısının kendisi zorunludur — **K-01b'ye bağlı olan yalnız özel gün anahtar kuralıdır**; prompt yakalama düzeneğinin kurulması da zorunludur — **K-20 düzeneğin varlığını değil, Marka DNA işiyle paylaşılmasını belirler**. Zorunlu iş açık kararın sonucuna çevrilmez.

⚠️ **Bir *hazır* kaydı koşulsuz taşınamaz.** Tek hakem Tier 2 önbellek yapısını hazır sayar. **Yapının kendisi ortaktır ve kaynakta yazılıdır** — Tier 2 bugün tek önbelleklenen bloktur `[AKT·KAYNAK · 2026-07-11]`; ama bundan çıkarılan *"ek iş gerekmez"* sonucu **gerçek çelişkidir ve açık karardır** (Bölüm 10.5). Bu bölüm olguyu taşır, sonucu taşımaz.

#### Görev dosyaları — yürürlükte, ama düzeltme kalemleri açık

Araştırma brief şablonu, denetçi görev dosyası **v1.1** ve sentez görev dosyası **v1.2** yürürlüktedir. ⚠️ **Sürüm numaraları ve tarihler bu sentezde dosyaların kendi başlıklarına karşı denetlenmiştir** — v1.1 ve v1.2 ikisi de 2026-07-11 tarihiyle dosyanın içinde yazılıdır, brief şablonu ise *son güncelleme 2026-07-07* damgasını taşır ve kendini **genel şablon** olarak tanımlar; *"kanonik"* nitelemesi ise hakem beyanıdır ve öyle taşınır. ⚠️ ***Hazır* nitelemesi tek hakemindir ve koşulsuz değildir;** bu sentezde sözleşmelere karşı ölçülmüş iki kalem vardır:

- **Dört düzeltme kalemi — dördü de resmî hakem turunu bloklar** ve **yeni karar açmazlar**; alınmış kararların ya da yürürlükteki hükümlerin görev sözleşmelerine yansımamasıdır. **Dördü de Bölüm 7'de doğmuştur ve ortak evleri Bölüm 14.4'tür**; tekil kökenleri şunlardır: *(i)* **kök sektör rehberinin** sentez görev sözleşmesinin girdi listesinde bulunmaması (Bölüm 7.5) · *(ii)* URL örnekleminin **"sabit dokuz satır"** yazımının eleme hâlinde düşen satır sayısıyla uyuşmaması (Bölüm 7.4) · *(iii)* **kopya şüphesi bayrağının** tüketim satırının sentez sözleşmesinde bulunmaması (Bölüm 7.5) · *(iv)* **sentez özeti ile yönetici onay yüzeyi** arasındaki ilişkinin yazılı olmaması (Bölüm 7.8, 8.4). ⚠️ **Dördü de bu bölümün hazırlık tablosuna aittir:** *"görev dosyaları hazır"* hükmü bunlar kapanmadan verilemez.
- **Diğer hakemin tespiti:** denetçi görev dosyasının **yeni sürümünde** çıktı sözleşmesi ile aktif paket yeniden doğrulama ekinin tanımlanması gerektiği. ⚠️ **Bağlı bir karar kümesidir ve iki kararlıdır** (Bölüm 7.4): *(i)* motor katmanındaki **iki denetçi mutabakatı kapısı benimsenecek mi** · *(ii)* **benimsenirse** ekin **adı ve şeması** ne olacak. ⚠️ **Ek için ayrı bir *"benimsensin mi"* tercihi yoktur** — ek, kapının **girdisidir**: kapı benimsenip ek alınmazsa kapı **girdisiz kalır**, ek kapı benimsenmeden alınırsa denetçilere **ölçülmemiş bir iş yükü** eklenir. İkisi birlikte görünür kılınır; küme Bölüm 17'de **tek bağlı küme** olarak açılacaktır.

Dosyalar **yürürlüktedir**; *"resmî tura hazır"* hükmü bu iki kalem kapanmadan verilemez.

#### Kuyumculuk pilot dosyasının bugünkü durumu

- **Temel paket (sekiz alan) için üç bağımsız araç araştırması tamamlanmıştır**; çıktılar dosyada durmaktadır. Ortak hüküm, kaynakta yazılı `[AKT·KAYNAK · 2026-07-11]`.
- **Üç çıktının içerik ekseni.** Bir hakem, çıktıların şu eksenlerde *"önemli ölçüde ortaklaştığını"* yazar: güven ve şeffaflık · duygusal özel an dili · sektöre özgü çağrı kalıpları ve kültürel dönemler · makro/lüks görsel dil · mevzuat riskleri. **İçerik düzeyinde mutabakat ölçülmemiştir** — *"önemli ölçüde ortaklaşma"* bir hakem beyanıdır `[BU SENTEZDE DOĞRULANMADI]` ve iddia düzeyinde mutabakatı ölçmek **resmî denetim turunun işidir** (Bölüm 7.5).
- **Üç çıktı brief şablonunun ilk sürümüyle üretilmiştir:** yalnız temel paket görevini içerir, özel gün görevinin sözleşmesini taşımaz ve çıktı düzeni farklıdır. ⚠️ **Kaynak bu düzen farkının ihlal olmadığını açıkça yazar** `[AKT·KAYNAK · 2026-07-11]`; iki hakem de eskimişliği kaydeder, **ihlal-değildir kaydı yalnız kaynaktadır** ve denetimde korunmalıdır.
- **İlk sürüm brief elde yoktur ve bunun denetimdeki karşılığı kaynakta karara bağlanmıştır** `[AKT·KAYNAK · 2026-07-11]`: brief operatörde bulunursa koşu klasörüne eklenir; elde yoksa denetim *"ilk sürüm eki elde yok — v1 sözleşmesine biçim uyumu denetlenmez, yalnız içerik ve iddia doğruluğu denetlenir"* notuyla koşulur. Bir hakem kuralı aynen taşır. **Yeniden üretimde sorun ortadan kalkar** — brief kopyası koşu klasörüne yazılır (**K-17**, Bölüm 7.2).
- **Özel gün görevi için brief hazırdır, koşu beklemektedir.** Bu brief **donmuş bir türevdir**, araştırma sonucu değildir ve kanonik sayılmaz — ortak hüküm.
- ⚠️ **Gayriresmî ön hakem turu ile resmî tur karıştırılmamalıdır.** İki hakem turu koşulmuştur; **gayriresmîdir** ve birleşik ön taslak o oturumda üretilmiştir — kaynakta ve bir hakemde yazılıdır `[AKT·KAYNAK · 2026-07-11]`, diğer hakemde **0 isabet** (harf duyarsız). Kaynak resmî turun nasıl koşulacağını da netleştirmiştir: **güncel görev dosyalarıyla, bu klasörde**; çıktıları (iki denetçi raporu + birleşik taslak) buraya yazılır; **veri tabanına taslak yazımı ve aktivasyon ondan sonra gelir.**
- **Zincirin neresindeyiz.** Bir hakemin özeti şudur: pilot **araştırma ve mimari doğrulama kanıtına sahiptir**, fakat **resmî hakemlik → sentez → veri tabanına taslak → işlevsel kapı → aktivasyon** zinciri **tamamlanmış sayılamaz**.
- **Pilotun içerik ve mevzuat bulguları.** Kaynak, örneklemde doğrulanmış saydığı bulguları adlandırır: reklamlarda **yetki belgesi numarası** zorunluluğu, bir **emsal reklam cezası** ve indirim öncesi fiyat penceresinin **30 günden 10 güne** inmesi (yürürlük **2026-08-01**). ⚠️ **Statüleri yukarıdaki ayrıma tabidir:** kaynağın kod/DB taramasının **dışındadır** ve bu sentezde de doğrulanmamıştır `[BU SENTEZDE DOĞRULANMADI]`. Aynı hassasiyetler pilot brief'inde zaten **"bilinen hassasiyet ipuçları"**, yani **araştırma girdisi** olarak yazılıdır; **girdi ile bulgu karıştırılmamalıdır.** Tarihli değişikliğin pakete **iki tarihli** yazılması ve yürürlükten sonra sadeleştirilmesi **Bölüm 11.6'da kabul senaryosu** olarak kayıtlıdır. ⚠️ **Gözlem:** bu sentezin koşulduğu tarihte yürürlük tarihi **geçmiştir**; ortada henüz aktif paket bulunmadığı için gözlem yeni bir karar açmaz — ham çıktıların eskimesine (**K-18**) ve ilk resmî turun girdisine ilişkin bir kayıttır.

#### Bakım borçları — bu işte dokunulmaz

Bu bölümün kaynaklarında **beş kalem** sayılmaktadır — kapalı bir küme ilan edilmez — ve **hepsi kaynakta yazılıdır** `[AKT·KAYNAK · 2026-07-11]`.

| Kalem | Kayıt | Akıbet |
|---|---|---|
| `brands.sector` (TEXT) ↔ `sector_id` (uuid) **çift yazımı** | Soru *"silinebilir mi"* değil, ***"ne zaman tekilleşir"*** | Bölüm 3.2 kapsam dışı — **çözülmemiş kapsam kararı**, Bölüm 17 |
| Platform uzunluk ayarının sürüklenmesi | **Altı legacy şablonda**; aktif şablonlarda platform geçersiz kılması hiç bulunmadığı için merkezî varsayılan geçerlidir → **sapma gerçek, üretim etkisi sıfır** | aynı |
| Legacy şablonların `active` statüde ölü kod duruşu | Kullanımdan kaldırma işareti, açılış doğrulamasının **kontrol değişikliğini** de gerektirir | aynı |
| Legacy kısa video yolunun sessiz hatası | Rehberi slug yerine görünen adla arar → hep boş döner; ön yüz bu yolu çağırmaz | **K-06** — ayrı açık karar (Bölüm 5.1, 10.4) |
| Yılbaşı'nın takvimde **ulusal**, prompt örneklerinde **ticari** anlatılması | Mevcut veri tutarsızlığı; **pakete miras kalır** | **Çözülmemiş kapsam kararı** — belge akıbeti kullanıcı onaylıdır, Bölüm 17'de barındırılır (Bölüm 11.4) |

⚠️ **Beş kalem beş ayrı karardır.** Kullanıcının onayladığı şey **belge akıbetinin ortaklığıdır** — üçünün de Bölüm 17'de kapsam kararı olarak barındırılması; **alttaki kapsam kararlarının birleştirildiğine ilişkin bir hüküm bu sentezde bulunamadı.** Kolon tekilleştirme, platform uzunluk sapması ve legacy şablonların statüsü **ayrı ayrı seçilebilir**: biri ele alınıp diğeri bırakılabilir.

⚠️ **Bu bölüm hiçbirini kapatmaz — kaydeder.** İlk üç kalemin **bakım işinin** ele alınacağı **adlandırılmış ve tarihli bir hedef hiçbir katmanda yoktur** (Bölüm 3.2'de ölçüldü); kaynak yalnız *"ayrıca ele alınmalı"* der. ⚠️ **Belge akıbetleri kullanıcı onaylıdır ve beş kalemin hepsine bir ev verir** — Bölüm 17'de kapsam kararı olarak barındırılırlar; **hiçbiri "evsiz" değildir.** Ev sahibi olmak **alttaki bakım kararını kapatmaz**: kalemler **çözülmemiştir**. ⚠️ Legacy şablon sayısı olarak anılan **22**, hedef sektör sayısı olarak anılan 22 ile **aynı şeyi saymamaktadır**; ayrım **K-21**'in kontrol maddesidir (Bölüm 3.2).

#### Bu bölümde ölçülmemiş olanlar

**Tur başına operasyon süresi** — Faz 1 aktif paket tavanının (**K-13**) dayanağıdır — ve **Tier 2 token bütçesi** (**K-12**) ölçülmemiştir; ikisi de pilottan gelecektir. **Bu bölüm eşik, tavan veya süre üretmez.**

### 16.2 Pilot kapsamı

⚠️ **Bu alt başlık yalnız bir hakem belgesindedir** — diğer hakemde `ön koşul` · `genişleme` · `kapsamadığı` · `gerçek müşteri`/`trafik` kalıpları harf duyarsız tarandığında **0 isabet** verir (pozitif kontrol: `kuyumculuk` 25 ↔ 28). **2.6'nın ikinci sınırı devrededir: tek hakem beyanıyla çözülmüş sayılamaz.** ⚠️ Ters yön de geçerlidir — **kaynakta karara bağlanmış pilot hükümleri yeni kullanıcı kararına çevrilmez.**

- **Pilot alanı: kuyumculuk alt sektörü.** Alanın sınırı **kaynakta, pilot brief'inin sektör bloğunda yazılıdır** `[AKT·KAYNAK · 2026-07-11]`: altın, pırlanta, gümüş ve değerli taşlı takı perakendesi ile kişiye özel tasarım, ölçülendirme, bakım-onarım ve tamir hizmetleri; **saat hariç**. ⚠️ **Ayrım korunmalıdır: brief'in araştırma kapsamı ile paketin kapsamı aynı şey değildir** — gümüş araştırma kapsamına alınmıştır, **pakete girip girmeyeceği açık operatör kararıdır** (aşağıya bakınız).
- **Neden temsil edici.** Altı gerekçe sayılır: kök kovada karşılıksız olması (problemin en saf hâli) · mevzuat yoğunluğu, yasaklar alanının gerçek testi · kültürel takvim zenginliği, özel gün mekanizmasının gerçek testi · belirgin görsel dil · üç araştırma çıktısının hâlihazırda mevcut olması, hakem hattının gerçek veriyle denenebilmesi · pilotun bugün *yalnız özel gün* modunda olması, dolayısıyla kısmi güncelleme yolunu da sınaması. ⚠️ Gerekçelerin **dayanakları** kaynakta ve pilot brief'inde bulunur; ***temsil edici* değerlendirmesinin kendisi yalnız bir hakemdedir** `[BU SENTEZDE DOĞRULANMADI]`.
- **Trafik ve kapsam — kısıt kaydedilir, öncülü ölçülür.** ⚠️ **Kaynakta doğrulanan tam olarak şudur:** veri tabanında **iki marka** kayıtlıdır ve **kök kovaları** adlandırılmıştır `[AKT·KAYNAK · 2026-07-11]`. **Kaynak, bu iki markanın kuyumcu olmadığını ayrıca kanıtlamaz** — kuyumculuğun kök kovada karşılığı bulunmadığı için bir kuyumcu marka bugün başka bir kovada durabilirdi. *"İkisi de kuyumcu değildir"* hükmü **yalnız bir hakemdedir** `[BU SENTEZDE DOĞRULANMADI]`; taze doğrulaması pilot koşumundan önce yapılmalıdır. ⚠️ Aynı hakem buradan **iki ayrı hüküm** çıkarır — pilotun **kontrollü bir test markasıyla** koşulacağı ve **gerçek kullanım sinyalinin Faz 1'de elde edilemeyeceği**. İkisi **ayrı ayrı seçilebilir** ve aşağıda ayrı kararlar olarak taşınır.
- ⚠️ **Pilotun süresi hiçbir katmanda yazılı değildir.** **Bu belge süre uydurmaz**; şablonun alanı boş bırakılmaz, **açık kalem** olarak işaretlenir. ⚠️ Turun periyodu (üç **veya** altı ay — **K-26**) pilotun süresi değildir; ikisi karıştırılmamalıdır.
- **Başarı ölçütünün çekirdeği kaynakta karara bağlıdır** `[AKT·KAYNAK · 2026-07-11]`: aynı ürün sınıfı için paketli ve paketsiz üretim yan yana konduğunda **sektörel ayrışma gözlenebilir olmalı**, paketsiz markada **modele gönderilen mevcut prompt parçaları byte-exact değişmemeli** ve **operatör onayı** alınmalıdır. *(Kaynak burada "bit-düzeyinde değişmezlik" ifadesini kullanır; bu belgede düzeltilmiş biçim geçerlidir — Bölüm 13.)* Zincirin kendisi Bölüm 8.2 ve Bölüm 13'te yazılıdır. ⚠️ **Ölçütün iki ayağı aynı statüde değildir:** paketsiz markadaki değişmezlik **Katman-1**'de deterministik olarak ölçülür ve kapıdır; **sektörel ayrışmanın gözlenmesi Katman-2'ye aittir ve kalite sinyalidir** — geçme eşiği **K-11 (b)**'de açıktır ve bu belgede eşiğe çevrilmez (Bölüm 13.4). ⚠️ **Katman-2'nin pilotta nasıl koşulacağı ayrıca açıktır: örneklem boyutu K-11 (a)'dadır** ve **(b)'den ayrı seçilebilir** — boyut belirlenip eşik tümüyle reddedilebilir (Bölüm 13.4). Pilotun başarı ölçütü bu katmanın **koşulmasını** gerektirdiği için **K-11 (a) bu bölümün karar evrenindedir.**
- ⚠️ **İptal ölçütü — bu belgede eşiğe çevrilmez.** Tek hakem iki iptal ölçütü yazar. Birincisi — **paketsiz markada herhangi bir regresyon** — ortak çekirdekle uyumludur: **Katman-1** deterministiktir ve paketsiz markada tek bayt fark **pazarlıksız geri alma** tetikleyicisidir (Bölüm 8.3, 13.3). ⚠️ İkincisi — **kör değerlendirmede paketli/paketsizin ayırt edilememesi** — aynı belgenin **kendi içinde çatıştığı** noktadır: aynı belge **Katman-2**'yi *"operatör onayının girdisidir, otomatik kapı değildir"* diye tanımlar ve eşiğini `[AÇIK]` bırakır. Eşiği açık bir katmanı iptal ölçütü yapmak **örtülü eşik üretir**. **Bu belgede kör değerlendirme sonucu, aktivasyon kararında olumsuz kalite sinyalidir; otomatik red veya iptal ölçütü K-11 (b) kapanmadan tanımlanmaz** (Bölüm 2.3, 13.4). Hakemin kendisi de sayısal eşiği `[AÇIK]` işaretleyip **K-11**'e bağlar. ⚠️ **Belge-içi tutarsızlık burada evine gelmiştir ve kapatılmamıştır** — kaynağın kendisi kararsızdır, iki pozisyon olarak taşınamaz (2.3).

#### Pilot paketinin içerik kapsamına ilişkin dört operatör kararı

**Dördü de iki hakem belgesinde ve kaynakta açıktır; ayrışma yalnız statüdedir** — bir hakem dördünü öneri vermeden sayar, diğeri her birine öneri yazar. Kaynak, dördünü de *"veri tabanına yazımdan önce kapatılmalı"* diyerek operatör kararı olarak kaydeder `[AKT·KAYNAK · 2026-07-11]`. **Bu belgede önerileri korunur, kararları kapatılmaz.** ⚠️ **ID uyarısı: `K-04` ile `K-04a–d` farklı şeylerdir** — `K-04` dağarcık kullanım kuralıdır (kapalı karar), aşağıdakiler kapsam kararlarıdır.

| ID | Karar | Kaynaktaki öneri |
|---|---|---|
| **K-04a** | Gümüş, paket kapsamına girsin mi? | **Girsin** — araştırma kapsamına zaten alınmıştır |
| **K-04b** | Kasım indirim dönemi pakete girsin mi? | **Girmesin** — ileride kampanya içerik türü ele alınırsa oraya. ⚠️ Dönem sistem takviminde farklı bir adla kayıtlıdır; ad eşleşmesi **K-01b**'ye bağlıdır |
| **K-04c** | Kampanya-aciliyet istisnası eklensin mi? | **Eklenmesin** — sistem talimatındaki sahte-kıtlık yasağı sınırı zaten çizer |
| **K-04d** | Görsel kodlara kültürel sahne eklentisi Faz 1'e alınsın mı? | **Faz 2** — kaynaklarda yoktur, üretim gerektirir |

⚠️ **Dördü ayrı ayrı seçilebilir** ve tek kaleme bağlanamaz. ⚠️ **K-04d'nin bir ek sınırı vardır:** kaynaklarda karşılığı olmayan sahne kodlarının pakete alınması, brief sözleşmesinin **kaynaksız üretim yasağıyla** doğrudan karşılaşır (Bölüm 7.1); Faz 1'e alınması hâlinde içeriğin nereden geleceği ayrıca kararlaştırılmalıdır. **Bu belge o yolu açmaz.**

#### Pilot kapsamının yeni açık kararları

*(Bölümün kalan yeni kararları 16.3'tedir — **beş genişleme kapısı ve kalibrasyon kapısı**; toplam **dokuz** yeni karar Bölüm 17'ye taşınır.)*

- **Pilotun kontrollü bir test markasıyla koşulması.** Marka sayısı ve kovaları kaynaktadır; **kontrollü test markası çözümü yalnız bir hakemdedir.** ⚠️ **Bağımlılık koşulludur, kesin değildir:** pilot ancak **kayıtlı markalar arasında uygun bir kuyumcu marka bulunmuyorsa** bu karara bağlıdır — ve o öncül (*"ikisi de kuyumcu değil"*) **doğrulanmamıştır**.
- **Gerçek kullanım sinyali elde edilmeden ilerlenmesi — risk kabulü.** ⚠️ **Yukarıdaki karardan ayrı seçilebilir:** kontrollü test markası kabul edilip aktivasyon **gerçek bir kuyumcu marka gelene kadar bekletilebilir**, ya da sinyalsiz ilerleme kabul edilebilir. ⚠️ *"Faz 1 boyunca sinyal elde edilemez"* hükmü **ölçülmemiş bir öngörüdür** `[ÖLÇÜLMEMİŞ VARSAYIM]` — kaynak yalnız bugünkü marka kaydını doğrular, Faz 1 boyunca yeni marka gelip gelmeyeceğine ilişkin bir hüküm taşımaz.
- **Pilota takvim tabanlı bir süre tanımlanacak mı?** Hiçbir katmanda süre yazılı değildir. Tek hakemin modeli genişlemeyi **süreye değil ön koşullara** bağlar; bu belge süre uydurmaz. ⚠️ **Yukarıdaki karardan ayrı seçilebilir:** kontrollü test markası kabul edilip süre tanımsız bırakılabilir, tersi de mümkündür.

### 16.3 Pilot sonrası genişleme

Aşağıdaki ön koşulların her biri **yeni bir kapı** yaratır; 2.6'nın ikinci sınırı gereği **çözülmüş sayılamazlar** ve burada **öneri statüsünde** taşınırlar — **her biri ayrı bir açık karardır.**

**Genişleme ön koşulları** *(öneri, tek hakemde; her biri ayrı karar)*:

1. **Katman-1 prompt yakalama düzeneğinin bütün yüzeylerde çalışır ve yeşil olması.** Düzenek Bölüm 5.1'de **yenidir**; Marka DNA işiyle ortak kullanımı **K-20**'de açıktır.
2. **İlk turun operasyon süresinin ölçülmüş olması.** ⚠️ Bu ayak **kaynakta karara bağlıdır:** Faz 1 aktif paket tavanı (**≤5**) ilk turda ölçülen tur başına süreyle revize edilecektir (**K-13**) `[AKT·KAYNAK · 2026-07-11]`. **Süre ölçülmemiştir** ve bu belgede hedef değere çevrilmez.
3. **Özel gün anahtar sözleşmesinin (K-01b) kapanmış olması.**
4. **Video hareket yüzeyinin (K-02) kapanmış olması.** ⚠️ Hakem 3 ve 4'ü **tek koşulda** yazar ve çıplak `K-01` biçimini kullanır; **kastedilen K-01b'dir** — takvime gün eklenmesi kararı **K-01a**'dır. Ortak gerekçesi *"ikisi de brief şablonuna geri yansıyabilir"*dir ve yalnız o hakemdedir.
5. **Alt sektör atama akışının gerçek kullanıcıyla en az bir kez denenmiş olması.** Teyit bileşeninin yerleşimi **K-19**'da açıktır.

⚠️ **Beş kapının her biri ayrı bir açık karardır — tek kaleme bağlanamaz.** Kapıların **içerikleri** kendi kararlarında zaten kayıtlıdır (K-20 · K-13 · K-01b · K-02 · K-19); **yeni ve ayrı seçilebilir olan, her birinin genişleme kapısı yapılıp yapılmayacağıdır.** Biri benimsenip diğeri reddedilebilir; birden fazlası tek karar sayılırsa **karar kimliği silinir**. ⚠️ **Hakemin üçüncü koşulu bu nedenle iki kapıya bölünmüştür** (3 ve 4): K-01b'nin kapanması kapı yapılıp K-02'ninki reddedilebilir.

> ⚠️ **Kapıların içeriği kapanmadır, brief güncellemesi değildir.** Hakem *"K-01b/K-02 kapanmış olmalı"* der; *"şablona geri yansıyabilir"* ifadesi **onun gerekçesidir, kapının içeriği değildir.** İkisi aynı karar sayılamaz: kapanmanın brief şablonuna yansıması hâlinde **brief'in ne zaman yeniden üretileceği K-18'in zamanlama hükmüne** dokunur. **Bu belge kapıyı kaynağın yazdığı gibi taşır** ve brief-güncelleme kapısı türetmez; kesişim kayda geçirilir.
>
> ⚠️ **Ayrı bir ölçüm — kapıların pratik etkisi ölçülmedi.** K-01b ve K-02 blok profillerinde **sistem spec'ini zaten kesin bloklarlar**; buradan *"kapı fiilen kendiliğinden sağlanır"* sonucu **çıkarılmamıştır** — çıkarmak, iki kararın spec'ten önce kapanacağını varsaymak olurdu ve o **zamanlama iddiası ölçülmemiştir**.

⚠️ **Kalibrasyon kanıtının ölçeğe geçiş koşulu olması ayrı bir açık karardır.** Aynı hakem, motorun kalibrasyonunun pilotta yapılmasını ve **ölçeğe geçişin kalibrasyon kanıtına bağlanmasını** kendi risk listesinde yazar; ancak bunu ön koşul listesine **bağlamaz**. ⚠️ **Bu karar K-22'ye indirgenemez:** K-22 motorun **hangi fazda** geleceğini sorar; bu karar, motor gelirse **ölçeğe geçişin bir kanıt kapısına bağlanıp bağlanmayacağını** sorar — motor Faz 1'e alınsa da alınmasa da ayrıca seçilir ve **ürün/risk seviyesindedir**. ⚠️ **Kanıtın içeriği en az iki ayaklıdır.** *(a)* **Motorun kararlarının insan yargısıyla karşılaştırılması** — hakem, pilotta tek sektörde motorun kararlarının elle doğrulanabileceğini yazar ve kalibrasyonu buna dayandırır; *(b)* **eşik ve limit değerleri** — bunlar **K-24**'ün konusudur ve aynı hakemin risk kaydı kalibrasyonu doğrudan K-24'e bağlar. ⚠️ **K-24 kapanmış değildir:** hakem tablosunda *"şimdi belirle"* ↔ *"pilotta ölç, sonra belirle"* seçenekleriyle **açık karardır** ve *"ölçülmeden eşik konmaz"* onun **önerisidir**; diğer hakem de kalibrasyon biçimini açık bırakır. Ortak ve bu belgede korunan tek hüküm **eşik ilkesidir**: kanıtsız eşik seçilmez (Bölüm 7.7). ⚠️ **Kanıtın *kabul ölçütü* tanımlı değildir — ama karşılaştırmanın kendisi kaynakta yazılıdır.** Eksik olan, karşılaştırmanın **ne kadarının yeterli sayılacağıdır**; bu, kullanıcı onayına sunulacak bir ayrıntı değil, **teknik bir kabul sözleşmesidir** ve kapı kararından ayrı bir kalem olarak taşınır.

> ⚠️ **Kapının benimsenmesi ile kabul sözleşmesi aynı karar değildir.** *Kapı olsun mu* bir **ürün/risk** kararıdır ve kullanıcıya aittir; *hangi karşılaştırma hangi kapsamda yeterli sayılır* bir **teknik kabul sözleşmesidir** — doğruluğu kullanıcı onayıyla değil, kanıt ve inceleme zinciriyle belirlenir (Bölüm 4.5). **Kapı benimsenip kabul sözleşmesi açık kalabilir**; ikisi ayrı ayrı sonuçlanır. Sözleşme **teknik iş kalemidir**, karar sayımına girmez ve blok sweep'inde **ayrı satır** olarak değerlendirilir.
>
> ⚠️ **Karşılaştırma verisinin yükü her iki motor fazında da doğar.** Kaynak hakem, motoru **pilot sonrasına bırakan** seçenekte bile *"motorun kurallarını kalibre etmek için insan kararlarıyla karşılaştırma verisi gerekir; o veri pilottan gelir"* der. Yük bu nedenle **K-22'nin Faz 1 dalına özgü değildir**: motor sonraya bırakılsa da pilot bu veriyi **üretmek ve saklamak** durumundadır. ⚠️ **Mevcut artefakt katmanının bu veriyi yeterli biçimde üretip üretmediği bu sentezde doğrulanmamıştır** ve kabul sözleşmesi kaleminin kapsamındadır.

**Pilotun kapsamadığı varyasyonlar** *(tek hakemin sayımı; bu sentezde listenin tamlığı ölçülmemiştir)*:

- **Hizmet sektörleri** — ürün fotoğrafı olmayan, görsel dili soyut alt sektörler; görsel kod yaklaşımının orada çalışıp çalışmadığı **bilinmemektedir**.
- **Web sitesi olmayan marka** ile atama geri düşüşü — kuralın kendisi Bölüm 9'da karara bağlıdır, **pilot onu sınamaz**.
- Aynı kök kovada **iki alt sektörün birlikte** yaşadığı durum.
- **Gerçek müşteri trafiği ve etkileşim verisi** — 16.2'deki kısıtın doğal sonucudur.
- **`anma` türü akışı** — bu türün ana örneği olan gün sistem takviminde yoktur; eklenmesi **K-01a**'ya bağlıdır (⚠️ hakem burada da çıplak `K-01` yazar). Kısıtın kendisi Bölüm 11.3'te yazılıdır.

**Genişlemede yeniden değerlendirilecek riskler** *(risk kaydının kendisi Bölüm 18'dedir; burada yalnız genişlemeye bağlı olanlar anılır)*:

- **Operasyon yükü** paket sayısıyla artar (üç aylık tur × paket sayısı). ⚠️ Büyüklüğü **ölçülmemiştir**; *"insan eliyle aylar sürer"* iddiası `[ÖLÇÜLMEMİŞ VARSAYIM]` olarak **K-21** ve **K-22**'nin gerekçesine bağlıdır ve **kapıya çevrilmez** (Bölüm 2.1).
- Alt sektör listesi büyüdükçe **modelin aday listeden seçim kalitesi**.
- **Tier 2 token bütçesi** — paket ile Marka DNA bloklarının **toplam bütçesinin birlikte hesaplanmamış olduğu** hükmü bir hakem belgesindedir ve **K-12**'nin gerekçesidir; ölçüm Bölüm 4.4 ve 10.5'te de `[ÖLÇÜLMEMİŞ VARSAYIM]` olarak kayıtlıdır.
- `[SEA-2026-08-11]` **Motorun karar kalitesi ölçekte.** Hakem, pilotta tek sektörde motorun kararlarının elle doğrulanabileceğini, ölçekte doğrulanamayacağını yazar. ⚠️ **Bu bir ölçüm değil, ölçülmemiş bir öngörüdür** `[ÖLÇÜLMEMİŞ VARSAYIM]`: elle doğrulama yükü sektör sayısı × kalıp sayısı ile artar, ama **eşiği ölçülmemiştir** ve bu belgede kapıya çevrilmez (**K-21** · **K-13** · Bölüm 2.1). Aynı hakem buradan kalibrasyonun pilotta yapılmasını ve ölçeğe geçişin **kalibrasyon kanıtına** bağlanmasını önerir — **öneri açık karar olarak yukarıda taşınmıştır**. ⚠️ Hedef sektör sayısı olarak anılan 22 ile kaynak dokümanların 12 kök sektör ve **≤5** Faz 1 tavanı rakamları **aynı şeyi sayıyor olmayabilir**; *"uyuşmuyor"* nitelemesi bu belgede kullanılmaz — **referansları tanımsızdır ve uyuşmazlık kanıtlanmış değildir** (**K-21**).

---

## 17. Uygulama öncesi açık kararlar

> ⚠️ **Statü notu (ayrıntı belge başında):** aşağıdaki satırların 51'i (45 kullanıcı kararı + K-57 · K-70 · K-83 · K-143 bağlı kapanışları + K-20 · K-21) 2026-08-23'te Otomaix spec seansında **kapandı**; satırlar geriye dönük güncellenmedi. Karar statüsünde kanonik kaynak Otomaix spec + TASK Decisions Log'dur; çelişkide **spec esastır**.

[ZORUNLU — boşsa "Açık karar yok" yaz]

**162 açık karar.** `Spec'i bloklar mı?` hücresi çıplak Evet/Hayır değildir; beş sınıftan
birini + kısa gerekçesini taşır:

| Sınıf | Anlamı |
|---|---|
| **Spec öncesi kullanıcı kararı** | Amaç · kapsam · maliyet · operasyon yükü · politika · risk kabulü tartılıyor. Spec yazılmadan kapanmalı |
| **Spec içinde teknik olarak çözülür** | Ürün davranışını, kapsamı veya yükü değiştirmiyor. Spec yazarı / teknik sahip çözer; gerekiyorsa önce taze doğrulama yapar |
| **Koşullu** | Yalnız belirli bir spec / faz / kapsam seçilirse gerekli |
| **Bloklamaz** | Bu spec'in dışında; ait olduğu yer belirtilir |
| **Ölçülmedi** | Blok durumu iddia edilemez; ne ölçüleceği yazılır |

Kapanmış kararlar silinmez: satırları `KAPANDI` olarak kalır, kararın kendisi tarihi ve
gerekçesiyle **Ek B**'dedir.

---

### 17.1 Ürün ve kapsam kararları — 39 karar

| ID | Soru / karar | Seçenekler | Öneri | Karar sahibi | Son tarih | Spec'i bloklar mı? |
|---|---|---|---|---|---|---|
| **K-21** | Kaç sektör/paket hedefleniyor? Kaynaklarda 12 kök sektör, Faz 1 için ≤5 paket ve 22 sektör birlikte geçiyor | A) 22 hedef, tavan kalkar / B) ≤5 ile başla, 22'ye kademeli / C) 22 farklı bir şeyi sayıyor — netleştirilir | **[AÇIK] — öneri:** **Netleştirilmeli** — üç rakamın neyi saydığı tanımsızdır; uyuşmazlık kanıtlanmış değildir. Motorun ölçek gerekçesi bu sayıya dayandığı için ürün kararıdır | Yönetici / ürün sahibi | Spec kapsamı sabitlenmeden önce | **Koşullu** — politika motoru Faz 1'de olduğundan (✅ K-22 KAPANDI — A) ölçek gerekçesi bu sayıya dayanır; tek sektörlü pilot spec'i bu karar olmadan yazılabilir |
| **K-22** | Politika motoru Faz 1'e mi girer, pilot sonrasına mı? | A) Faz 1 — pilotla birlikte / B) Pilot sonrası — önce elle koş, kalibre et | ✅ **KAPANDI — A** (2026-08-21, kullanıcı kararı). ⚠️ Yön, belgedeki önerinin (*B'ye eğilim — kalibrasyon verisi pilottan gelir*) **tersidir**; öneri sentez değerlendirmesiydi, karar ürün sahibinindir. Kalibrasyon ihtiyacı ortadan kalkmaz: eşikler uydurulmaz, ölçümle kalibre edilir (**K-24**) | — (kapandı) | — (kapandı) | **Bloklamaz** — karar kapanmıştır; kaydı Ek B'dedir. Sonuçlar: spec motor alt sistemini **Faz 1 kapsamında** yazar; motor kararları (**K-23 · K-24 · K-25 · K-133**) Faz 1 spec gündemine girer; **K-21'in netleştirme koşulu tetiklenmiştir** |
| **K-13** | Faz 1'de eşzamanlı işletilecek aktif paket tavanı | A) ≤5 ile başla / B) Tavan koyma | **[AÇIK] — öneri:** **≤5 önerisi bir tahmindir** — tur başına süre ölçülmemiştir; kapı veya kabul kriteri yapılamaz | Yönetici / ürün sahibi | Pilot sonrası | **Bloklamaz** — işletim tavanıdır, spec içeriğini değiştirmez; ilk tur süresi ölçüldükten sonra konur |
| **K-27** | Yönetici turu hangi yüzeyden koşulacak? | A) Claude Code komut ailesi / B) Otomaix'te yönetici paneli | ✅ **KAPANDI — A** (2026-08-21, kullanıcı kararı): Claude Code komut ailesi; yönetici paneli geliştirilmez. ⚠️ Komut ailesinin bugün var olup olmadığı **doğrulanmamıştır** — spec seansına taze doğrulama görevi doğar; aile yoksa kurulum işi A'nın maliyetine eklenir (maliyet belirsizliği kabul edildi; karar bununla yeniden açılmaz) | — (kapandı) | — (kapandı) | **Bloklamaz** — karar kapanmıştır; kaydı Ek B'dedir. İşletim prosedürü (14) ve rol tasarımı (15) komut ailesi yüzeyine dayanır |
| **K-29** | Pilot kontrollü bir test markasıyla mı koşulur? | A) Kontrollü test markası / B) Mevcut kayıtlı markalarla | **[AÇIK]** — *"kayıtlı iki markanın ikisi de kuyumcu değil"* öncülü doğrulanmadı; doğrulanmadan seçenekler tartılamaz | Yönetici / ürün sahibi | `[TANIMSIZ]` | **Koşullu** — pilot yürütme planı yazılırken gerekli; veri modelini ve üretim hattını etkilemez |
| **K-30** | Gerçek kullanım sinyali elde edilmeden ilerlenecek mi? | A) Sinyalsiz ilerlenir / B) Aktivasyon gerçek marka gelene kadar bekletilir | ✅ **KAPANDI — A** (2026-08-21, kullanıcı kararı): sinyal beklenmez, aktivasyon Faz 1'de yapılır — **risk kabulüdür**. **K-29'dan bağımsızdır** (K-29 açık kalır). *"Faz 1 boyunca sinyal elde edilemez"* iddiası ölçülmemiş bir tahmindi; karar o tahmine değil, risk kabulüne dayanır | — (kapandı) | — (kapandı) | **Bloklamaz** — karar kapanmıştır; kaydı Ek B'dedir |
| **K-31** | Pilota takvim tabanlı bir süre tanımlanacak mı? | A) Süre tanımlanır / B) Süre yerine ön koşullar | **[AÇIK]** — hiçbir katmanda yazılı süre yok ve uydurulmadı. Alternatif model genişlemeyi süreye değil ön koşullara bağlar | Ürün sahibi | `[TANIMSIZ]` | **Bloklamaz** — pilotun yönetim kararıdır; genişleme ön koşulları K-32…K-37'de ayrıca ele alınır |
| **K-32** | Katman-1 düzeneğinin bütün yüzeylerde yeşil olması genişleme kapısı mı? | A) Kapı / B) Kapı değil, izleme sinyali | **[AÇIK]** — kapının içeriği K-20'nin kapsamındadır; burada açık olan yalnız kapı yapılıp yapılmayacağı | Ürün sahibi | `[TANIMSIZ]` | **Bloklamaz** — Faz 2'ye geçiş kapısıdır; Faz 1 spec'i yazıldıktan sonra kapanabilir |
| **K-33** | İlk turun operasyon süresinin ölçülmüş olması genişleme kapısı mı? | A) Kapı / B) Kapı değil | **[AÇIK]** — ölçümün kendisi K-13'ün girdisidir; kapı olması ayrı karardır | Ürün sahibi | `[TANIMSIZ]` | **Bloklamaz** — Faz 2'ye geçiş kapısıdır; ölçüm pilot sonrasında yapılır |
| **K-34** | K-01b'nin kapanmış olması genişleme kapısı mı? | A) Kapı / B) Kapı değil | **[AÇIK]** — kapının içeriği K-01b'nin kapanmasıdır; ayrı bir brief-güncelleme kapısı türetilmedi | Ürün sahibi | `[TANIMSIZ]` | **Bloklamaz** — Faz 2'ye geçiş kapısıdır |
| **K-35** | K-02'nin kapanmış olması genişleme kapısı mı? | A) Kapı / B) Kapı değil | **[AÇIK]** — K-34'ten ayrı seçilebilir: biri kapı yapılıp diğeri yapılmayabilir | Ürün sahibi | `[TANIMSIZ]` | **Bloklamaz** — Faz 2'ye geçiş kapısıdır |
| **K-36** | Atama akışının gerçek kullanıcıyla en az bir kez denenmiş olması genişleme kapısı mı? | A) Kapı / B) Kapı değil | **[AÇIK]** — içeriği K-19'un kapsamındadır | Ürün sahibi | `[TANIMSIZ]` | **Bloklamaz** — Faz 2'ye geçiş kapısıdır |
| **K-37** | Kalibrasyon kanıtı ölçeğe geçişin koşulu olacak mı? | A) Koşul / B) Koşul değil | **[AÇIK]** — K-22'ye indirgenemez (faz ≠ kanıt kapısı); kanıtın teknik kabul ölçütü ayrı bir iştir | Ürün sahibi | `[TANIMSIZ]` | **Bloklamaz** — ölçeğe geçiş kapısıdır; Faz 1 spec'ini etkilemez |
| **K-11 (a)** | Kör değerlendirme örnekleminin boyutu | A) Sayısal boyut şimdi belirlensin / B) İlk koşumda kaydedilip sonra konsun | **[AÇIK] — öneri:** **B + ilk turda ölçüm** — eşik uydurmak ölçülmemiş sayı iddiasıdır | Yönetici / operatör | Kapı testinden önce | **Bloklamaz** — sayı ilk turda ölçülüp konur; spec'e sayı yazılmaz |
| **K-11 (b)** | Katman-2 için geçme eşiği konulacak mı? | A) Sayısal eşik / B) Eşik yok, operatör yargısı | **[AÇIK]** — Katman-2 otomatik kapı değildir; eşik kapanmadan kabul kriteri veya iptal ölçütü yapılamaz | Yönetici / operatör | Kapı testinden önce | **Bloklamaz** — eşik pilot kanıtından sonra konur; Katman-2'nin kapı olmadığı hükmü zaten yazılı |
| **K-38** | Aktif paket, yerine yeni sürüm konmadan geri çekilebilir mi? | A) Desteklenen geçiş / B) Desteklenmez | **[AÇIK]** — kaynak katmanında tanımlı değil | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — paket yaşam döngüsünün desteklenen geçişlerini belirler; şema ve akış buna bağlıdır |
| **K-39** | Geçmiş postlar geriye dönük değiştirilebilir mi? | A) Post kaydı değişmez kanıttır / B) Sonradan yeniden yazılabilir | **[AÇIK]** — K-07'ye indirgenemez: K-07 damganın yerini sorar, bu karar kaydın değişmezliğini sorar | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — izlenebilirliğin ve arşiv davranışının temelidir; veri sözleşmesini belirler |
| **K-40** | Arşiv güvencesi bağlayıcı bir garanti mi, hedef mi? | A) Garanti / B) Hedef | **[AÇIK]** — kaynak katmanları aynı cümleyi farklı bağlayıcılıkla taşır | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — taahhüdün derecesi kabul kriterine dönüşür |
| **K-41** | Özet farkta "eşik-üstü çıkarılanlar" için eşik konulacak mı? | A) Sayısal eşik / B) Eşik yok, tam liste ayrıntı görünümünde | **[AÇIK]** — yöneticinin hangi riskli çıkarmayı göreceğini belirler | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — özet diff yüzeyi tasarlanırken gerekli; motor fazıyla (K-22) birlikte değerlendirilir |
| **K-42** | Sinyal odaklı özet kontrolü benimsenecek mi? | A) Benimsenir / B) Benimsenmez | **[AÇIK]** — tek katmanda önerilmiştir, yükümlülüğe çevrilmedi | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — özet diff yüzeyi benimsenirse gerekli |
| **K-43** | Alt sektörü arşivlenmiş markanın bayat atama kaydı korunur mu, boşaltılır mı? | A) Korunur / B) Boşaltılır | **[AÇIK]** — hiçbir katmanda tanımlayan hüküm yok | Yönetici / operatör | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — atama akışının ve veri yaşam döngüsünün davranışını belirler |
| **K-44** | Bayat durum sistemde işaretlenecek mi? | A) İşaretlenir / B) İşaretlenmez | **[AÇIK]** — K-43'ten ayrı seçilebilir: kayıt korunup işaretlenmeyebilir | Yönetici / operatör | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — işaretleme yeni bir durum alanı ve operasyon yükü doğurur |
| **K-45** | Bayat durum kullanıcıya bildirilecek mi? | A) Bildirilir / B) Bildirilmez | **[AÇIK]** — bağımsız karardır, K-43/K-44'ün sonucu değildir | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — müşteriye görünen davranıştır; sürtünme yasağıyla birlikte tartılır |
| **K-46** | Toplu marka atamasının yeniden açılma eşiği tanımlanacak mı? | A) Eşik tanımlanır / B) Kapsam dışı kalır, koşulla yeniden açılır | **[AÇIK]** — eşik ölçülmemiştir; ölçüm noktası ve sahibi hiçbir katmanda yazılı değil, uydurulmadı | Ürün sahibi | `[TANIMSIZ]` | **Bloklamaz** — kapsam dışıdır; marka sayısı ölçek gerektirdiğinde yeniden açılır |
| **K-01a** | Takvime 10 Kasım eklensin mi? | A) Eklensin (yıllık takvime de işlenir) / B) Eklenmesin | **[AÇIK]** — `anma` türünün kaynaktaki ana örneğidir. *"Eklenmezse `anma` türü hiç tetiklenemez"* dayanağı 2026-07-11 aktarımıdır, güncel gerçek olarak taşınamaz | Yönetici / operatör | Paket taslağı yazılmadan önce | **Bloklamaz** — takvim veri kararıdır; paket taslağı yazılırken kapanır |
| **K-146** | Takvime 24 Kasım Öğretmenler Günü eklensin mi? | A) Eklensin / B) Eklenmesin | **[AÇIK]** — K-01a'dan ayrı seçilebilir: sabit bir gündür ve `anma` bağı yoktur | Yönetici / operatör | Paket taslağı yazılmadan önce | **Bloklamaz** — takvim veri kararıdır |
| **K-147** | Okula dönüş dönemi takvime eklensin mi? | A) Eklensin / B) Eklenmesin | **[AÇIK]** — K-01a ve K-146'dan ayrı seçilebilir; yapısı da farklıdır: gün değil dönemdir | Yönetici / operatör | Paket taslağı yazılmadan önce | **Koşullu** — eklenecekse takvim kaydı bir gün değil dönem taşımalıdır; şema buna göre yazılır |
| **K-04a** | Gümüş kuyumculuk paketi kapsamına girsin mi? | A) Girsin / B) Girmesin | **[AÇIK] — öneri:** **Girsin** — araştırma kapsamına zaten alınmıştır. Araştırma kapsamında olmak pakete girmek değildir; ikisi ayrı şeydir | Yönetici / operatör | Paket taslağı yazılmadan önce | **Bloklamaz** — paket içeriği kararıdır; paket taslağı yazılırken kapanır |
| **K-04b** | Kasım indirim dönemi pakete girsin mi? | A) Girsin / B) Girmesin | **[AÇIK] — öneri:** **Girmesin** — kampanya içerik türü ele alınırsa oraya taşınır. Sistemde *"Black Friday"* adıyla kayıtlıdır | Yönetici / operatör | Paket taslağı yazılmadan önce | **Bloklamaz** — paket içeriği kararıdır |
| **K-04c** | Kampanya-aciliyet istisnası tanımlanacak mı? | A) Tanımlansın / B) Tanımlanmasın | **[AÇIK] — öneri:** **Tanımlanmasın** — sistem istemindeki sahte-kıtlık yasağı sınırı çiziyor | Yönetici / operatör | Paket taslağı yazılmadan önce | **Bloklamaz** — paket içeriği kararıdır |
| **K-04d** | Kaynaksız kültürel sahne eklentileri Faz 1'e alınacak mı? | A) Faz 1 / B) Faz 2 | **[AÇIK] — öneri:** **Faz 2** — kaynaklarda yoktur, üretim gerektirir; ham çıktıların güven notları bunu kendileri yazar | Yönetici / operatör | `[TANIMSIZ]` | **Bloklamaz** — paket içeriği kararıdır |
| **K-47** | Yılbaşı takvim kaydı düzeltilecek mi? | A) Takvim kaydı düzeltilir / B) Kapsam dışı kalır, koşulla yeniden açılır | **[AÇIK]** — K-03 kapandıktan sonra öncelik sorusu kalkmıştır; geriye veri doğruluğu kalır: takvimde `national`, istem örneklerinde ticari | Yönetici / operatör | `[TANIMSIZ]` | **Bloklamaz** — veri doğruluğu bakım kalemidir; spec içeriğini belirlemez |
| **K-48** | Bakım borcu: `brands.sector` ↔ `sector_id` tekilleştirmesi bu işin kapsamına alınsın mı? | A) Kapsama alınır / B) Kapsam dışı, koşulla yeniden açılır | **[AÇIK]** — kaynak yalnız *"ayrıca ele alınmalı"* der; adlandırılmış ve tarihli bir ev yoktur | Ürün sahibi | `[TANIMSIZ]` | **Bloklamaz** — bu işin bilinçli kapsam sınırıdır; ayrı bir bakım işine aittir |
| **K-49** | Bakım borcu: platform uzunluk ayarının sürüklenmesi kapsama alınsın mı? | A) Kapsama alınır / B) Kapsam dışı, koşulla yeniden açılır | **[AÇIK]** — K-48'den ayrı seçilebilir | Ürün sahibi | `[TANIMSIZ]` | **Bloklamaz** — ayrı bir bakım işine aittir |
| **K-50** | Bakım borcu: legacy şablonların `active` statüde durması kapsama alınsın mı? | A) Kapsama alınır / B) Kapsam dışı, koşulla yeniden açılır | **[AÇIK]** — K-06'ya indirgenemez: K-06 tek bir yolu, bu kalem 22 şablonun statüsünü sorar | Ürün sahibi | `[TANIMSIZ]` | **Bloklamaz** — ayrı bir bakım işine aittir |
| **K-51** | Kök rehber yolu tam kapsam sağlandıktan sonra kaldırılacak mı? | A) Kaldırılır / B) Korunur | **[AÇIK]** — tek geçen ifade koşullu bir cümledir ve kalıcı davranışa çevrilmedi | Ürün sahibi | `[TANIMSIZ]` | **Bloklamaz** — tam kapsam sonrasına aittir; Faz 1'de kök rehber yolu zaten korunur |
| **K-52** | Marka DNA verisi politika motoruna girdi olacak mı? | A) Girdi olur / B) Olmaz — motor yalnız sektör katmanını görür | **[AÇIK]** — K-22'ye indirgenemez (faz ≠ girdi kümesi); müşteri beğenisini dışlayan hüküm DNA alanlarını kapsamaz | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — motor Faz 1'de olduğundan (✅ K-22 KAPANDI — A) girdi kümesi bu karar olmadan yazılamaz |
| **K-53** | Ölçeklenebilirlik analizinin birincil artefaktı kanonik kaynak sayılıp kayda alınsın mı? | A) Kanonik sayılır ve kayda alınır / B) Mevcut mimari belgelerdeki hâli yeterli sayılır, artefakt kayıtsız kalır | **[AÇIK]** — tartılan şey izlenebilirliktir. Artefakt kanonik sayılıp içeriği ayrıca denetlenmeyebilir (K-148) | Ürün sahibi | `[TANIMSIZ]` | **Bloklamaz** — kaynak izlenebilirliği kararıdır; spec'in içeriğini belirlemez |
| **K-148** | Aynı artefaktın içeriği denetlenecek mi? | A) İçerik denetlenir / B) Denetlenmez | **[AÇIK]** — K-53'ten ayrı seçilebilir. Burada tartılan maliyettir: 3,7 MB'lık bir oturum kaydını denetleme yükü | Ürün sahibi | `[TANIMSIZ]` | **Bloklamaz** — denetim iş yükü kararıdır; spec içeriğini belirlemez |

---

### 17.2 Operasyon kararları — 36 karar

| ID | Soru / karar | Seçenekler | Öneri | Karar sahibi | Son tarih | Spec'i bloklar mı? |
|---|---|---|---|---|---|---|
| **K-54** | Koşu ve aktivasyon rolü ikiye bölünecek mi? — turu koşan yönetici ↔ kapsam/politika/risk kabulünü koyan ürün sahibi | A) İki rol, yetkileri farklı (aynı kişi olabilir) / B) Tek rol | **[AÇIK]** — yetkinin son onaya indirilmesi her katmanda ortaktır; açık olan yalnız bölünme. Kaynak rol tablosu aynı yetkiyi iki farklı yere koyar ve bu kararsızlık iki pozisyon olarak taşınamaz | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — yetki modeli rol tasarımını (15) ve aktivasyon akışını belirler; Bölüm 17'nin `Karar sahibi` sütunu da buna bağlıdır |
| **K-55** | Teknik sahip kim / hangi ekip olacak? | A) Adlandırılmış kişi veya ekip / B) Atama yapılmaz, yetki yöneticide kalır | **[AÇIK]** — rolün varlığı açık değildir; işletim yordamı rolü üç kurulum adımında kullanır. Açık olan yalnız atamadır | Ürün sahibi | `[TANIMSIZ]` | **Bloklamaz** — kişi/ekip atamasıdır; spec'in içeriğini belirlemez, işletim kurulurken yapılır |
| **K-56** | Alarm katmanı benimsenecek mi? | A) Benimsenir / B) Benimsenmez | **[AÇIK]** — tek katmanda önerilmiştir. Eşikler kararın parçası değil sonucudur: benimsenirse ölçülür, şimdi konmaz | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — yeni bir gözlemlenebilirlik bileşenidir; kapsamı ve kurulum yükünü belirler |
| **K-57** | Alarmı kim izler, kim müdahale eder? | A) Yönetici / B) Teknik sahip / C) İkisi birlikte | **[AÇIK]** — K-56'dan ayrı seçilebilir: katman benimsenip sorumlusu açık bırakılabilir | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — alarm katmanı benimsenirse (K-56) gerekli |
| **K-58** | Olay müdahalesinde kim bilgilendirilir? | A) Operatör; teknik hatada teknik sahip / B) Hedef adlandırılmaz | **[AÇIK]** — K-54 ve K-56'ya indirgenemez: rol bölünmese de hedef adlandırılmalıdır. Alarm eşik aşımında uyarır, bu karar olay anında bilgilendirir | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — yalnız uygulama/aktivasyon aşamasında iş doğurur (Bölüm 14.5 olay müdahalesi yordamı); sistem spec'ine ve motor katmanına dokunmaz |
| **K-59** | İnceleme bulgularını kabul etme yetkisi kimde? | A) Teknik sahipte / B) Operatörde / C) İnceleme zincirinin kendisinde | **[AÇIK]** — tek katmanda geçen bir ifadedir, normatif hüküm olarak yazılamaz. K-55'e indirgenemez: atama yapılıp kabul yetkisi başka yerde bırakılabilir | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — uygulama/aktivasyon aşamasını bloklar, sistem spec'ini koşullu etkiler; bütün spec'i bloklamaz. Bölüm 15 rol tablosunda yazılıdır ve seviyesi kullanıcıdır |
| **K-60** | Teknik doğruluk sonucu operatöre bilgi olarak geçilecek mi? | A) Geçilir / B) Geçilmez | **[AÇIK]** — hükmün sınırı: kaynak yalnız geçirmeyi yazar, okumayı zorunlu tutmaz; buradan bir operatör okuma yükü türetilmedi | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — operatör yüzeyinin kapsamı (*"operatör iki şey görür"* sözleşmesi) buna dokunur; sistem spec'i ve uygulama aşaması koşullu etkilenir |
| **K-61** | Paket türü ↔ takvim kategorisi çatışması riskinin (R-25) sahibi kim? | A) Operatör / B) Teknik sahip / C) Ürün sahibi | **[AÇIK]** — K-03 kapandı ama riskin sahipliği açık kaldı; kapanan karar riski düşürmez | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — uygulama/aktivasyon aşamasını bloklar; sistem spec'i ve kuyumculuk pilot spec'i koşullu etkilenir. Sekiz sahiplik kararı ayrı ayrı seçilebilir; ortak koşul karar kimliklerini birleştirmez |
| **K-62** | Motorun kararsız bıraktığı eski öğeler riskinin (R-29) sahibi kim? | A) Operatör / B) Teknik sahip / C) Ürün sahibi | **[AÇIK]** — K-54 ve K-22'ye bağlıdır, ikisine de indirgenemez | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — uygulama/aktivasyon aşamasını bloklar; sistem spec'i ve kuyumculuk pilot spec'i koşullu etkilenir. Sekiz sahiplik kararı ayrı ayrı seçilebilir; ortak koşul karar kimliklerini birleştirmez |
| **K-63** | Girdi kaymasından doğan toplu değişim riskinin (R-30) sahibi kim? | A) Operatör / B) Teknik sahip / C) Ürün sahibi | **[AÇIK]** — K-54 ve K-22'ye bağlıdır | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — uygulama/aktivasyon aşamasını bloklar; sistem spec'i ve kuyumculuk pilot spec'i koşullu etkilenir. Sekiz sahiplik kararı ayrı ayrı seçilebilir; ortak koşul karar kimliklerini birleştirmez |
| **K-64** | İçerik aynıyken yeni sürüm açılması riskinin (R-31) sahibi kim? | A) Operatör / B) Teknik sahip / C) Ürün sahibi | **[AÇIK]** — K-54 ve K-22'ye bağlıdır | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — uygulama/aktivasyon aşamasını bloklar; sistem spec'i ve kuyumculuk pilot spec'i koşullu etkilenir. Sekiz sahiplik kararı ayrı ayrı seçilebilir; ortak koşul karar kimliklerini birleştirmez |
| **K-65** | Politika sonucu ile onay arasında sürüm değişimi riskinin (R-32) sahibi kim? | A) Operatör / B) Teknik sahip / C) Ürün sahibi | **[AÇIK]** — K-54 ve K-22'ye bağlıdır | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — uygulama/aktivasyon aşamasını bloklar; sistem spec'i ve kuyumculuk pilot spec'i koşullu etkilenir. Sekiz sahiplik kararı ayrı ayrı seçilebilir; ortak koşul karar kimliklerini birleştirmez |
| **K-66** | Müşteri tercihinin sektör evrimine karışması riskinin (R-33) sahibi kim? | A) Operatör / B) Teknik sahip / C) Ürün sahibi | **[AÇIK]** — kuralın kendisi her katmanda ortaktır; açık olan yalnız ihlali kimin izleyeceğidir | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — uygulama/aktivasyon aşamasını bloklar; sistem spec'i ve kuyumculuk pilot spec'i koşullu etkilenir. Sekiz sahiplik kararı ayrı ayrı seçilebilir; ortak koşul karar kimliklerini birleştirmez |
| **K-67** | Uzun bağlamlı sentezin kaçırması riskinin (R-34) sahibi kim? | A) Operatör / B) Teknik sahip / C) Ürün sahibi | **[AÇIK]** — motor katmanından ve rol bölünmesinden bağımsızdır; kontrol tanımlı, risk satırının sahibi tanımsız | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — uygulama/aktivasyon aşamasını bloklar; sistem spec'i ve kuyumculuk pilot spec'i koşullu etkilenir. Sekiz sahiplik kararı ayrı ayrı seçilebilir; ortak koşul karar kimliklerini birleştirmez |
| **K-68** | Kişisel veri doğrulamasını (R-35) kim yürütür? | A) Operatör / B) Teknik sahip / C) Ürün sahibi | **[AÇIK]** — doğrulama kaleminin kendisinden ayrıdır: o *neyin*, bu *kimin* doğrulayacağını sorar | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — uygulama/aktivasyon aşamasını bloklar; sistem spec'i ve kuyumculuk pilot spec'i koşullu etkilenir. Sekiz sahiplik kararı ayrı ayrı seçilebilir; ortak koşul karar kimliklerini birleştirmez |
| **K-69** | İşletime hazırlık listesi aktivasyon öncesi imza yüzeyi olacak mı? | A) Aktivasyon öncesi imza yüzeyi olur / B) Yalnız kontrol listesi kalır | **[AÇIK]** — listenin maddeleri kendi bölümlerinde zaten yazılıdır; yeni olan, listeyi bir imza kapısına çevirmektir | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — aktivasyon akışına yeni bir kapı ve operasyon yükü ekler |
| **K-70** | Hazırlık listesini kim işaretler? | A) Yönetici / B) Teknik sahip / C) İkisi birlikte | **[AÇIK]** — K-69'dan ayrı seçilebilir: kapı kurulsa bile kimin işaretleyeceği hiçbir katmanda yazılı değildir | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — imza yüzeyi benimsenirse (K-69) gerekli |
| **K-71** | Açık soruların tamamının kapatılmış olması aktivasyonun ön koşulu mu? | A) Tamamı kapatılmış olmalı / B) Ön koşul değil | **[AÇIK]** — bir katman bunu ön koşul listesinin dışında bırakır, diğeri içine alır; ikinci hüküm kendi belgesinde K-23 ile gerilimlidir ve orada çözülmez. K-23'e indirgenemez | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — aktivasyon kapısının içeriğini ve turun kapanma koşulunu belirler |
| **K-72** | Yöneticinin reddi bir düzeltme turu başlatacak mı? | A) Ret bir düzeltme turu başlatır / B) Ret yalnız turu kapatır | **[AÇIK]** — akış tek katmanda tanımlıdır. Düzeltmenin nasıl sürümleneceği ayrı bir karardır (K-105) ve buna bağlıdır, ama bununla aynı değildir | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — turun akış şemasına yeni bir döngü ekler; operasyon yükünü belirler |
| **K-26** | Tur periyodu global mi, sektör bazlı mı yapılandırılacak? | A) Global tek periyot / B) Sektör başına | **[AÇIK] — öneri:** **B'ye eğilim** — mevzuat yoğun sektör kısa, durağan sektör uzun periyot. K-149'dan (periyodun değeri) bağımsız seçilebilir; K-21 ile birlikte değerlendirilmelidir | Ürün sahibi | Spec kapsamı sabitlenmeden önce | **Spec öncesi kullanıcı kararı** — sektör bazlı seçilirse yapılandırmaya sektör başına bir alan girer; operasyon yükünü de belirler |
| **K-149** | Tur periyodu üç ay mı, altı ay mı olacak? | A) Üç ay / B) Altı ay *(kaynak katmanının saydığı iki değer; üçüncü değer uydurulmadı)* | **[AÇIK]** — operasyon yükü periyotla doğru orantılıdır; iş yükü tercihidir. K-26'dan bağımsız seçilebilir; sektör bazlı seçilirse değer sektör başına belirlenir | Ürün sahibi | Spec kapsamı sabitlenmeden önce | **Bloklamaz** — yapılandırma değeridir; şemayı K-26 belirler, değer sonradan konur |
| **K-73** | Acil güncellemede tam araştırma turu zorunlu mu? | A) Zorunlu / B) Atlanabilir | **[AÇIK]** — kaynak yalnız güncellemenin periyot dışında aynı mekanizmayla yapılabileceğini söyler; tam turun atlanabilmesi ek bir hükümdür ve ortak yol yapılmadı. K-22'den ayrı seçilebilir | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — acil yolun hattaki tanımını ve operasyon yükünü belirler |
| **K-17** | Araştırma çıktıları hangi teslim yapısına yazılacak? | A) `research-runs/<run_id>/` sabit yapı / B) Serbest | **[AÇIK] — öneri:** **A** — mekanik kapı ve koşu yüzeyi bu yoldan okur. Kaynak da bunu *"spec'te kesinleşir"* diye erteler | Yönetici / operatör + teknik sahip | Koşu yüzeyi yazılmadan önce | **Spec içinde teknik olarak çözülür** — dizin ve dosya sözleşmesidir; ürün davranışını, kapsamı veya yükü değiştirmez |
| **K-18** | Brief'ler ve ham araştırma çıktıları ne zaman yeniden üretilecek? | A) Şimdi / B) Spec ve uygulama sonrası, resmî turdan hemen önce | ✅ **KAPANDI — B.** Sözleşmeler donmadan en pahalı manuel adım tekrarlanmaz; eski dosyalar silinmez. Zamanlama *"spec + uygulama sonrasına, resmî hakem turundan hemen öncesine"*dir — *"sözleşmeler donar donmaz"* biçiminde daraltılamaz | — (kapandı) | — (kapandı) | **Bloklamaz** — karar kapanmıştır; kaydı Ek B'dedir |
| **K-74** | Sentezin on açık soru sınırı aşılırsa ne olacak? | A) Tur durur / B) Fazlası özetlenir / C) Sınır kaldırılır | **[AÇIK]** — sözleşme sınırı koyar, taşma davranışını tanımlamaz; tanımsız kalırsa karar izi kaybı riski doğar | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — sözleşmenin taşma davranışıdır; karar izini koruyacak biçim spec'te tanımlanır |
| **K-75** | Denetçinin beş öneri sınırı aşılırsa ne olacak? | A) Tur durur / B) Fazlası özetlenir / C) Sınır kaldırılır | **[AÇIK]** — K-74'ten ayrı seçilebilir: iki sözleşme ayrı katmandır | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — sözleşmenin taşma davranışıdır |
| **K-14** | Koşu öncesi ön kontrol kurulacak mı? — denetçi-2 ortamının web erişimi her turdan önce sınanacak mı | A) Ön kontrol koşu yordamına konur / B) Konmaz | **[AÇIK]** — her turdan önce bir adım ekler; konmazsa tur erişimsiz denetçiyle koşulup kanıt tabanı sessizce daralabilir. Erişimin bugün var olup olmadığı bir ölçüm kalemidir ve bu satırdan ayrılmıştır. Bu ayağın karar mı teknik iş kalemi mi olduğu sonuçlandırılmamıştır | Teknik sahip · Ürün sahibi *(risk/yük ayağı)* | Resmî hakem turundan önce | **Koşullu** — resmî hakem turu yordamı yazılırken gerekli; veri modelini ve üretim hattını etkilemez |
| **K-76** | Denetim hangi bağlantı yöntemiyle başlatılacak? | A) Komut satırı / B) API / C) Bağlayıcı | **[AÇIK]** — hiçbir katmanda karara bağlanmamıştır | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — entegrasyon biçimidir; ürün davranışını değiştirmez |
| **K-77** | Denetimi başlatan kimlik ve yetki modeli ne olacak? | A) Paylaşılan kimlik / B) Ayrı kimlik ve dar yetki / C) Model seçilmez, koşum operatör oturumunda | **[AÇIK]** — K-76'dan ayrı seçilebilir: bağlantı yöntemi seçilip yetki modeli açık bırakılabilir | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(risk kabulü)* | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — paylaşılan kimlik bir güvenlik riski kabulüdür; ayrı kimlik ve dar yetki kurulum işi doğurur |
| **K-78** | İki denetim paralel mi sıralı mı yürütülecek? | A) Paralel / B) Sıralı | **[AÇIK]** — bir katmanda paralellik varsayılır ama karar olarak yazılmaz; diğeri ele almaz | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — yürütme düzenidir; bağımsızlık garantisi ayrı karardır (K-79) |
| **K-79** | İki denetçinin oturum izolasyonu ve aynı girdi anlık görüntüsünü kullanması teknik olarak garanti edilecek mi? | A) Garanti mekanizması kurulur / B) İlke düzeyinde bırakılır | **[AÇIK]** — K-78'den ayrı seçilebilir: sıralı koşumda da aynı garanti gerekir. İzolasyon bugün ilke olarak yazılıdır, teknik garantisi yoktur | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(risk kabulü)* | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — garanti kurulmazsa iki denetimin bağımsızlığı güvenceye bağlanmamış olur; kurulursa geliştirme işi doğar |
| **K-80** | Tekrar üretilebilirlik damgası zorunlu olacak mı? — denetçi model/sürüm, görev metni sürümü, koşu tarihi, girdi özetleri | A) Damga zorunlu / B) Zorunlu değil | **[AÇIK]** — yapısı K-79 ile aynıdır: izlenebilirlik güvencesi ↔ kurulum işi | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(risk kabulü)* | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — damga zorunlu değilse denetimin tekrar üretilemezliği kabul edilir; zorunluysa şema ve kurulum işi doğar |
| **K-81** | Denetçi çıktısının otomatik biçim kontrolü kurulacak mı? | A) Otomatik kontrol kurulur / B) Kurulmaz | **[AÇIK]** — çıktı sözleşmesi tanımlıdır, otomatik kontrolü yoktur. K-150'den ayrı seçilebilir | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(risk kabulü)* | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — kurulum yükü ↔ sözleşmeye uymayan raporun sessizce geçmesi riski |
| **K-150** | Tek geçerli raporla sentez engellenecek mi? | A) Tek raporda tur durur / B) Tek raporla devam edilir | **[AÇIK]** — K-81'den ayrı seçilebilir: biçim kontrolü kurulmadan da tek raporda durulabilir, ya da kontrol kurulup tek raporla devam edilebilir | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(risk kabulü)* | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — turu tek denetçi arızasına bağlama riski ↔ eksik kanıtla ilerleme riski |
| **K-82** | Zaman aşımı ve kısmi başarısızlıkta ne yapılacak? | A) Tur durur / B) Kısmi çıktıyla devam / C) Yeniden dener | **[AÇIK]** — hiçbir katmanda tanımlı değildir | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(risk kabulü)* | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — kısmi çıktıyla devam, eksik kanıtla ilerlemenin kabulüdür |
| **K-83** | Yeniden koşumda hangi deneme veya artefakt kimliği üretilecek? | A) Yeni deneme kimliği / B) Yeni artefakt / C) Dosya ezilir | **[AÇIK]** — K-82'den ayrı seçilebilir (politika seçilip kimlik şeması açık kalabilir); K-09'dan da ayrıdır: K-09 ham katman tekilleştirmesini, bu karar orkestrasyon yeniden koşumunu sorar | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — artefakt kimlik şemasıdır; *"dosya ezilir"* seçeneği salt-ekleme kuralıyla birlikte değerlendirilir |

---

### 17.3 Teknik ve spec kararları — 51 karar

| ID | Soru / karar | Seçenekler | Öneri | Karar sahibi | Son tarih | Spec'i bloklar mı? |
|---|---|---|---|---|---|---|
| **K-01b** | Özel gün anahtarları canlı takvim verisiyle nasıl eşleşecek? | A) Slugify öncesi normalize adımı (gün/arife eki kırpma) / B) Anahtarları sistem adlarıyla gün bazlı yazmak / C) Dar eşleme sözlüğü | **[AÇIK] — öneri:** **A** — her iki kaynak katmanı da aynı yönü gösterir: gün/arife eklerini kırpan ortak bir normalize işlevi. Ek koşul: yazım ve okuma aynı normalize kod yolunu paylaşmalı | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — önce canlı takvim verisindeki gün adları ile paket anahtarlarının bugünkü biçimi taze doğrulanır; normalize adımı bu ölçümle boyutlanır. Kullanıcıya ek içerik üretim yükü seçtirilmez |
| **K-02** | Video hareket dili hangi yüzeyden enjekte edilecek? | A) Paket `video_kodlar`'ından sektöre özgü hareket havuzu; paketsizde mevcut liste aynen kalır / B) Hareket istemini modele ürettirmek (ek çağrı) / C) Sonraki faza bırakılır, yalnız durağan kareye uygulanır | **[AÇIK] — öneri:** **A** — her iki kaynak katmanı da aynı yönü gösterir. Gerekçe: paketsiz üretimde modele giden prompt parçaları değişmez ve ek model çağrısı doğmaz | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(maliyet/kapsam ayağı — yalnız (A) elenirse)* | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — önce mevcut hareket listesinin enjeksiyon noktası taze doğrulanır. Paketsiz prompt değişmeden havuz beslenebiliyorsa (A) seçenek tartışması düşer; beslenemiyorsa ek model maliyeti ↔ kapsam daraltması tercihi kullanıcıya çıkar |
| **K-84** | Kalıp kimliği sürümler arası nasıl korunacak? | A) Sabit kimlik alanı üretilir ve sürümler arası korunur / B) Kalıcı kimlik kurulmaz, süreklilik metinsel eşleşmeyle kurulur / C) Sonraki faza bırakılır | **[AÇIK]** — gerçek çelişki: bir katman sabit kimliği zorunlu sayar ve metin özetinin kimlik olamayacağını yazar; diğeri kalıcı kimlik öngörmez ve bunu kabul edilmiş bir zayıflık olarak kaydeder. Bu sentez taraf tutmaz | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(risk kabulü)* | `[TANIMSIZ]` | **Koşullu** — politika motoru Faz 1'de olduğundan (✅ K-22 KAPANDI — A) motorun kimlik ve karar kapsamı buna dayanır |
| **K-151** | Kalıcı kalıp kimliğinin biçimi sözleşmede sabitlenecek mi? | A) Biçim sabitlenir / B) Sabitlenmez | **[AÇIK]** — yalnız K-84'ün (A) dalı seçilirse doğar. K-152'den ayrı seçilebilir | Teknik sahip | `[TANIMSIZ]` | **Koşullu** — K-84'te sabit kimlik seçilirse doğar; doğduğunda spec içinde teknik olarak çözülür, kullanıcı onayına sunulmaz |
| **K-152** | Kalıcı kalıp kimliğinin üretim yöntemi tanımlanacak mı? | A) Üretim yöntemi sözleşmede tanımlanır / B) Tanımlanmaz | **[AÇIK]** — yalnız K-84'ün (A) dalı seçilirse doğar. K-151'den ayrı seçilebilir: biçim sabitlenip üretim yöntemi açık bırakılabilir. Metin özetinin kimlik olamayacağı bu satırın girdisidir | Teknik sahip | `[TANIMSIZ]` | **Koşullu** — K-84'te sabit kimlik seçilirse doğar; doğduğunda spec içinde teknik olarak çözülür |
| **K-85** | İki kalıbın semantik olarak aynı sayılma ölçütü tanımlanacak mı? | A) Ölçüt sözleşmede tanımlanır / B) Tanımlanmaz | **[AÇIK]** — ölçüt tanımlanmazsa iki kalıbın aynı sayılıp sayılmaması yargısal kalır ve arşiv güvencesi bundan etkilenir. Ölçüt tanımlanıp eşleştirme yöntemi (K-153) açık bırakılabilir; K-84'ten de ayrı seçilebilir | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(kalite/risk ayağı)* | `[TANIMSIZ]` | **Koşullu** — motor Faz 1'de olduğundan (✅ K-22 KAPANDI — A) evrimsel kalıp kararı bu ölçüte dayanır |
| **K-153** | Eş anlamlı veya yeniden yazılmış kalıplar hangi yöntemle eşleştirilecek? | A) Deterministik eşleştirme / B) Hakemli eşleştirme *(kaynak katmanının saydığı iki seçenek)* | **[AÇIK]** — K-85'ten ayrı seçilebilir: ölçüt *neyin aynı sayıldığını*, yöntem *eşleşmenin nasıl bulunacağını* belirler | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(operasyon yükü ayağı)* | `[TANIMSIZ]` | **Koşullu** — motor Faz 1'de olduğundan (✅ K-22 KAPANDI — A) K-85 kapanınca gerekli. *Hakemli* dal seçilirse kalıp başına insan kararı doğar; o yük kullanıcıya çıkar |
| **K-86** | Kalıp kimliği hangi değişiklik seviyesine kadar korunacak? — `guncelle` ile `cikar + ekle` ayrımı | A) Kimliğin korunduğu değişiklik seviyesi tanımlanır / B) Tanımlanmaz | **[AÇIK]** — kalıcı kimlik öngörmeyen modelde bu soru sorulmuyor bile. K-84'ten ayrı seçilebilir ve K-85'e indirgenemez | Teknik sahip | `[TANIMSIZ]` | **Koşullu** — K-84'te sabit kimlik seçilirse doğar |
| **K-154** | `guncelle` ↔ `cikar + ekle` ayrımı karar izinde nasıl temsil edilecek? | A) Temsil sözleşmede tanımlanır / B) Tanımlanmaz | **[AÇIK]** — kaynak kendi içinde çelişir ve bu çelişki burada açık kalır: kimlik kuralları bölümü temsili bir kural olarak yazar, açık karar listesi aynı temsili çözülmemiş sayar. Bu sentez taraf tutmaz. K-86'dan ayrı seçilebilir | Teknik sahip | `[TANIMSIZ]` | **Koşullu** — K-84'te sabit kimlik seçilirse doğar |
| **K-87** | Pakete hiç girmeyen aday, karar izinde nasıl temsil edilecek? | A) Yalnız denetim/sentez raporunda kalır / B) Karar günlüğü şemasına ayrı bir karar değeri olarak eklenir / C) Mevcut gerekçe alanına bağlanır | **[AÇIK]** — B seçilirse karar alanının değer kümesi genişler ve görev sözleşmesi revize edilir; A ve C mevcut şemayla çalışır | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — karar günlüğünün iç temsilidir; ürün davranışını, kapsamı veya operasyon yükünü değiştirmez |
| **K-88** | Biçimsel-mekanik elemenin hangi bulgusu *eleme*, hangisi *not* üretecek? | A) Eşleme sözleşmede sabitlenir / B) Sabitlenmez | **[AÇIK]** — akış betiğin çıktısını *"biçimsel eleme/notlar"* diye yazar ve denetçi sözleşmesi bunu ek rapor olarak ister; eşlemeyi tanımlayan hüküm hiçbir katmanda bulunamadı. Kavram vardır, seviye eşlemesi yoktur | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — mekanik kapının çıktı sınıflamasıdır |
| **K-89** | Mekanik kapının kontrol kümesi sözleşmede sabitlenecek mi? | A) Küme sabitlenir / B) Sabitlenmez | **[AÇIK]** — küme kapalı değildir: kaynak listesi örnekleyicidir, *"toplam N kontrol"* biçimi kullanılamaz; ölçüt listenin ardındaki kuraldır | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — kapının kontrol sözleşmesidir |
| **K-24** | Motorun eşik ve limit değerleri ne zaman belirlenecek? — değişim oranı, alan bazlı sınırlar, ekleme oranı tavanı | A) Şimdi belirle / B) Pilotta ölç, sonra belirle | **[AÇIK] — öneri:** **B'ye eğilim** — ortak olan yalnız ilkedir: kanıtsız eşik seçilmez. Değerler ölçülmemiştir; eşik kapanmadan kabul kriteri, otomatik red ölçütü veya iptal koşulu yapılamaz | Teknik sahip | Motor kalibrasyonundan sonra | **Bloklamaz** — eşikler pilot kalibrasyonundan sonra konur; spec'e sayı yazılmaz |
| **K-90** | `tur durduruldu` öğesi `bloklandı` ile birleştirilecek mi? | A) Birleştirilir / B) Ayrı kalır | **[AÇIK]** — iki kaynak katmanı sonucu farklı seviyelerde modeller (biri koşu seviyesi, diğeri kalıp-kararı seviyesi); tamamlayıcıdır, karşıt değildir — ama birleştirme kararı açıktır | Teknik sahip | `[TANIMSIZ]` | **Koşullu** — politika motoru Faz 1'de olduğundan (✅ K-22 KAPANDI — A) gerekli |
| **K-91** | İlk paket koşusunda `değişiklik yok` sonucu geçersiz sayılacak mı? | A) Geçersiz sayılır / B) Sayılmaz | **[AÇIK]** — tek katmanda ele alınmıştır; diğerinde kavramın karşılığı yoktur — reddedilmiş değil, hiç ele alınmamıştır | Teknik sahip | `[TANIMSIZ]` | **Koşullu** — politika motoru Faz 1'de olduğundan (✅ K-22 KAPANDI — A) gerekli |
| **K-92** | Sıra ve biçim farklarının yanlış değişiklik sayılmasını önleyecek canonical üretim kuralı tanımlanacak mı? | A) Kural tanımlanır / B) Tanımlanmaz | **[AÇIK]** — tek katmanda ele alınmıştır. K-93'ten ayrı seçilebilir: kayıt yeri seçilip bu kural açık bırakılabilir | Teknik sahip | `[TANIMSIZ]` | **Koşullu** — politika motoru Faz 1'de olduğundan (✅ K-22 KAPANDI — A) gerekli |
| **K-93** | `değişiklik yok` ve `bloklandı` koşuları paket satırı oluşturmadan nerede kayıtlanacak ve nasıl sorgulanacak? | A) Durum kaydı için bir yer sözleşmede tanımlanır / B) Tanımlanmaz | **[AÇIK]** — alternatif modelde her koşu bir taslak sürüm üretir, dolayısıyla *"aday sürüm taslak olarak yazılır"* koşulsuz değildir. `bloklandı` ayağı düşerse açık bir karar sessizce kapanır | Teknik sahip | `[TANIMSIZ]` | **Koşullu** — politika motoru Faz 1'de olduğundan (✅ K-22 KAPANDI — A) gerekli |
| **K-94** | Motorun değerlendirdiği base sürüm ile onay anındaki aktif sürüm farklıysa sonuç geçersiz sayılacak mı? | A) Geçersiz sayılır (onay anında kontrol) / B) Sayılmaz | **[AÇIK]** — tek katmanda ele alınmıştır; kaynak katmanına da bu sentezde taşınmıştır, *"kaynakta yazılı"* denemez | Teknik sahip | `[TANIMSIZ]` | **Koşullu** — politika motoru Faz 1'de olduğundan (✅ K-22 KAPANDI — A) gerekli |
| **K-95** | Politika sonucu ve koşu kaydı nerede tutulacak? | A) Artefakt tablosunda yeni tür / B) Paket tablosunda JSONB / C) Ayrı değerlendirme tablosu | **[AÇIK]** — raporun varlığı motorlu modelde ortaktır, yeri açıktır | Teknik sahip | `[TANIMSIZ]` | **Koşullu** — motor Faz 1'de olduğundan (✅ K-22 KAPANDI — A) veri yeri spec'te tanımlanır |
| **K-96** | Motor sentez kararını değiştirdiğinde özgün sentez, nihai aday ve gerekçeli fark ayrı mı saklanacak? | A) Ayrı saklama sözleşmesi tanımlanır / B) Sentez raporu ham katmana tek artefakt olarak yazılır, ayrım tutulmaz | **[AÇIK]** — iki konum birbirini dışlamaz; bu sentez birini seçmez | Teknik sahip | `[TANIMSIZ]` | **Koşullu** — motor Faz 1'de olduğundan (✅ K-22 KAPANDI — A) gerekli |
| **K-25** | Karar satırına aktör alanı eklenecek mi? — kararı motor mu insan mı verdi | A) Eklensin / B) Eklenmesin | **[AÇIK] — öneri:** **A** — maliyet yok denecek kadar az; olmadan kötü bir sürümün kaynağı (motor kuralı mı sentez mi) teşhis edilemez. K-97'den ayrı karardır; ikisi tamamlayıcıdır ama birlikte alınmaları kesinleşmemiştir | Teknik sahip | Şema yazımında | **Koşullu** — politika motoru Faz 1'de olduğundan (✅ K-22 KAPANDI — A) gerekli |
| **K-97** | Motorun sürümü ve yapılandırması her koşuya damgalanacak mı? | A) Damgalanır / B) Damgalanmaz | **[AÇIK]** — alternatif model aynı ihtiyacı karar satırı seviyesinde karşılar. K-25'e indirgenemez | Teknik sahip | `[TANIMSIZ]` | **Koşullu** — motor Faz 1'de olduğundan (✅ K-22 KAPANDI — A) gerekli |
| **K-98** | Yöneticiye gösterilen anlık görüntü değiştirilemez olacak mı? | A) Değiştirilemez anlık görüntü zorunlu / B) Zorunlu değil | **[AÇIK]** — tek katmanda ele alınmıştır, ortak kural değildir. Diğer katmandaki *"değiştirilemez"* kullanımları ham artefakt ve denetçi kaydı içindir, yöneticiye gösterilen görünüm için değil | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — onay anındaki bütünlük garantisidir; K-94 ile birlikte tasarlanır |
| **K-99** | Son onay veya ret olayı kimlik ve zaman damgasıyla kaydedilecek mi? | A) Kaydedilir / B) Kaydedilmez | **[AÇIK]** — tek katmanda ele alınmıştır. İki komşuya karıştırılmaz: aktivasyon/geri alma olayının loglanması zaten her katmanda zorunludur ve açık karar değildir; yöneticinin göreceği özetin içeriği ise K-41'dir | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — olay kaydı şemasıdır |
| **K-100** | Denetçi sözleşmesine eklenecek yeniden doğrulama envanterinin adı ve şeması tanımlanacak mı? | A) Ad ve şema sözleşmede tanımlanır / B) Tanımlanmaz | **[AÇIK]** — karar *ad ve şemadır*, *benimseme* değildir: ekin ayrıca benimsenmesi diye bir tercih kaynakta bulunamadı. Ek, iki denetçi mutabakat kapısının girdisidir; kapı alınıp bu satır alınmazsa kapı girdisiz kalır | Teknik sahip | `[TANIMSIZ]` | **Koşullu** — mutabakat kapısı benimsenirse (K-125) gerekli |
| **K-07** | Üretim sürüm damgası nerede tutulacak? | A) Ayrı kolon / B) Mevcut JSONB alanının içinde | **[AÇIK]** — her iki kaynak katmanı da bu soruyu açık bırakır. Maliyet yok denecek kadar az; şimdi atlanırsa sonradan telafisi yoktur. Paketsiz üretimde geçerli bir paket ilişkisi bulunmaz; fiziksel temsil bu kararda açıktır | Teknik sahip | Şema yazımında | **Spec içinde teknik olarak çözülür** — veri yerleşimi kararıdır. Damganın Faz 1'de kurulması zorunludur (Bölüm 2.3); açık olan yalnız yeri |
| **K-101** | Önceki sürümün arşivlenmesi ve adayın etkinleştirilmesi tek işlem mi olacak? | A) Tek işlem / B) İki ayrı işlem | **[AÇIK]** — hüküm her iki kaynak katmanında da vardır, ayrım statüdedir: biri tek işlemi doğrudan yazar, diğeri aynı beklentiyi varsayım olarak taşır ve aktivasyonun veri tabanı değişmezini koruduğunun önceden doğrulanmasını ister. Açık olan hükmün varlığı değil, spec'te kesinleşmesidir | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — işlem sınırı tasarımıdır; her iki katman da aynı yönü gösterir |
| **K-102** | Geri alma tek işlem mi olacak? | A) Tek işlem / B) İki ayrı işlem | **[AÇIK]** — tek katmanda ele alınmıştır; diğeri tek-işlem beklentisini yalnız aktivasyon için yazar. K-101'den ayrı seçilebilir: aktivasyon atomik alınıp bu reddedilebilir | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — işlem sınırı tasarımıdır |
| **K-103** | Aktivasyon ve geri alma yetkisi teknik olarak nasıl zorlanacak? | A) Sunucu tarafı zorlama kurulur / B) Rol tablosu düzeyinde bırakılır | **[AÇIK]** — rol tablosu yetkiyi *kime* verdiğini yazar, *nasıl zorlandığını* yazmaz. K-54'e indirgenemez: rol bölünmese de zorlama modeli ayrıca seçilmelidir | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — yetkilendirmenin zorlanma biçimi güvenlik tasarımıdır; rol dağılımı ayrı karardır (K-54) |
| **K-104** | Aktivasyon ara penceresinde başlayan üretim hangi sürüme bağlanacak? | A) Üretimin başladığı andaki sürüm / B) Üretimin tamamlandığı andaki sürüm | **[AÇIK]** — tek katmanda ele alınmıştır ve orada da açıktır. Üç komşuya indirgenemez: K-07 (fiziksel temsil), K-39 (geçmiş postların değiştirilebilirliği), K-105 (okuyucu davranışı testi). Bu satır hangi anın esas alınacağını sorar | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — sürüm çözümleme anının tanımıdır |
| **K-105** | Ara pencerede okuyucu davranışı testi aktivasyon öncesi zorunlu olacak mı? | A) Benimsenir / B) Benimsenmez | **[AÇIK]** — tek katmanda ele alınmıştır. Kapsamı yazılmıştır (paket çözücüsünün ara durumdaki davranışı), benimsenmesi açıktır | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(operasyon yükü ayağı)* | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — aktivasyon öncesine yeni bir zorunlu test yükümlülüğü ekler; operasyon yükü tercihidir |
| **K-106** | Düzeltme yeni bir taslak sürüm mü açacak, mevcut taslağı yerinde mi güncelleyecek? | A) Yeni taslak sürüm / B) Yerinde güncelleme | **[AÇIK]** — kaynak katmanı ikisini de mümkün sayar ve seçmez. K-72'ye bağlıdır ama ondan ayrı seçilebilir: akış benimsenip sürümleme biçimi açık bırakılabilir | Teknik sahip | `[TANIMSIZ]` | **Koşullu** — red/düzeltme akışı benimsenirse (K-72) gerekli |
| **K-107** | Kısmi sürümde değişmeyen alanlar karar günlüğünde nasıl temsil edilecek? | A) Yalnız değişen satırlar yazılır / B) Taşınan alanlar için de *koru* satırı zorunlu | **[AÇIK]** — kaynak katmanının kendi içinde kararsız kaldığı noktadır; iki pozisyon olarak taşınamaz. K-73'e indirgenemez: o turun koşulup koşulmayacağını, bu satır günlük temsilini sorar | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — karar günlüğünün yazım kuralıdır |
| **K-108** | Eşleşmeyen özel gün notu karar günlüğünde nasıl temsil edilecek? | A) Mevcut gerekçe alanına yazılır / B) Karar kümesine yeni bir değer eklenir | **[AÇIK]** — sözleşme notlamayı hâlihazırda istemektedir, ama karar alanının kapalı değer kümesi bunu karşılamaz; temsil seçilmeden günlüğe gerçek veri yazılamaz | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — karar günlüğü şemasının değer kümesidir |
| **K-109** | Paket aktive edilince önbellek nasıl tazelenecek? | A) Önbellek anahtarı paket kimliği/sürümünü içerir / B) Aktivasyonda önbellek geçersiz kılınır / C) Ek mekanizma gerekmez — *(A ve B alternatiftir, birlikte gereken iki şart değil)* | **[AÇIK]** — yanlış seçimin sonucu somuttur: aktive edilen paket üretime hiç yansımayabilir. Mevcut önbelleğin aktivasyonda kendiliğinden tazelenip tazelenmediği bilinmiyor | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — önce paket aktivasyonunun mevcut önbellek geçersiz kılma yolunu tetikleyip tetiklemediği taze doğrulanır. Aktif paketin üretime yansıması zorunlu kabul kriteridir; kullanıcıya sessiz eski paket riski seçtirilmez |
| **K-110** | Paket satırında üretildiği koşuya bağ zorunlu olacak mı? | A) Zorunlu — alan boş bırakılamaz / B) Zorunlu değil | **[AÇIK]** — zorunluluk kapanmadan gerçek paket verisi yazılamaz; geri doldurma yalnız yan etkidir, kararın kendisi değildir | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — şema kısıdıdır; izlenebilirliğin Faz 1'de kurulması zaten zorunludur (Bölüm 2.3) |
| **K-08 (a)** | Araştırma artefaktındaki sektör ilişkisi hangi modelle kurulacak? | A) Sektör tablosuna yabancı anahtar / B) Serbest metin | **[AÇIK]** — migration ile birlikte kararlaştırılır; her iki kaynak katmanı da aynı konuyu taşır | Teknik sahip | Migration yazımında | **Spec içinde teknik olarak çözülür** — şema kararıdır |
| **K-08 (b)** | `brands.sub_sector_id`'nin yalnız alt sektör satırlarını kabul etmesi nerede zorlanacak? | A) Veri tabanı kısıtı / B) Uygulama katmanı doğrulaması | **[AÇIK]** — yabancı anahtarla kendiliğinden çözülmez; kısıt yazılmazsa atama akışı kök satır yazılmasına karşı korunmasız kalır | Teknik sahip | Migration yazımında | **Spec içinde teknik olarak çözülür** — kısıt yerleşimi kararıdır |
| **K-09** | Aynı koşunun iki kez yüklenmesi engellenecek mi? | A) Koşu + kaynak + tür üçlüsünde benzersizlik / B) Serbest, tekrar yükleme serbest | **[AÇIK]** — orkestrasyon yeniden koşumundan (K-83) ayrıdır: bu satır ham katman kısıdını, o satır yeniden koşumun kimliğini sorar | Teknik sahip | Migration yazımında | **Spec içinde teknik olarak çözülür** — benzersizlik kısıdıdır |
| **K-111** | Paket JSON doğrulayıcı şemasının kesin biçimi ne olacak? | A) Şema spec seansında sabitlenir / B) Mevcut alan tablosu taslak hâliyle uygulanır | **[AÇIK]** — doğrulayıcının bir şema modeli olması kaynak katmanında kararlaştırılmıştır (Ek B); açık olan şemanın kesin biçimidir. Alan tablosu diğer katmanda taslak olarak vardır | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — şema tanımıdır |
| **K-06** | Eski kısa video yolu düzeltilecek mi, açıkça kapsam dışı mı notlanacak? | A) Düzeltilir — sektör anahtarıyla aranır / B) Açıkça kapsam dışı diye notlanır | **[AÇIK] — öneri:** **B veya A — sessiz bırakma yasak.** Yolun bugün boş döndüğü ve arayüzden çağrılmadığı 2026-07-11 aktarımıdır, güncel gerçek olarak taşınamaz. Bu satır tek bir yolu sorar; iki katmanlı kapı protokolü ayrı bir konudur | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(kapsam ayağı — yol bugün çağrılıyorsa)* | Spec yazımında | **Spec içinde teknik olarak çözülür** — önce yolun bugün çağrılıp çağrılmadığı taze doğrulanır. Çağrılmıyorsa kapsam dışı notu teknik bir kayıttır; çağrılıyorsa düzeltme ↔ kaldırma tercihi kullanıcıya çıkar |
| **K-15 (a)** | Bozuk veya eksik paket içeriğinde çalışma zamanı nasıl davranacak? | A) Her iki dalda da emniyetli geri düşüş / B) *Alan eksik* dalında farklı davranış | **[AÇIK]** — *okunamıyor* dalı ortak hükümdür; yalnız bir alanın eksik olduğu hâlin davranışı hiçbir katmanda yazılı değildir ve uydurulmamıştır | Teknik sahip | Spec seansında | **Spec içinde teknik olarak çözülür** — hata yolu tanımıdır |
| **K-15 (b)** | Carousel ayrı bir prompt yüzeyi mi? | A) Ayrı yüzey / B) Mevcut yüzeyin varyantı | **[AÇIK]** — tek katmanda tespit edilmiştir; kaynak dokümanlarda yazılı değildir ve koda karşı doğrulanmalıdır | Teknik sahip | Spec seansında | **Spec içinde teknik olarak çözülür** — önce koda karşı taze doğrulanır, sonra yüzey listesine yazılır |
| **K-112** | Takvim erişilemezse özel gün bloğu nasıl davranacak? | A) Blok bugünkü gibi davranır — emniyetli geri düşüş / B) Farklı bir hata yolu tanımlanır | **[AÇIK]** — *"bugünkü gibi davranır"* bugünkü çalışma zamanı davranışına ilişkin bir iddiadır ve taze doğrulanmamıştır. Tek katmanda ele alınmıştır; ortak yol yapılamaz. Kabul matrisine satır açılamamıştır, beklenen sonuç uydurulmadı | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — önce bugünkü davranış taze doğrulanır, sonra hata yolu yazılır |
| **K-113** | Hareket havuzu boşsa ne olacak? | A) Mevcut listeye geri düşülür / B) Farklı bir davranış tanımlanır | **[AÇIK]** — tek katmanda ele alınmıştır. K-02'den ayrı seçilebilir: havuz yolu benimsense bile boş havuz dalı ayrıca karara bağlanmalıdır | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — geri düşüş yolu tanımıdır |
| **K-19** | Alt sektör teyit bileşeni hangi ekranda yer alacak? | A) Marka oluşturma / B) Markalar / C) Marka ayarları *(üç aday yüzey kaynakta adlarıyla sayılıdır)* | **[AÇIK]** — üç katman da aynı yönde açıktır. Veri tarafı tek noktadır: üç sayfa aynı liste ucunu çeker (2026-07-11 aktarımı, taze doğrulanmadı), dolayısıyla teknik maliyet farkı değil ürün tercihi tartılır | **Ürün sahibi** *(yerleşim)* · Teknik sahip *(mekanizma)* | Spec seansında | **Spec öncesi kullanıcı kararı** — hangi ekranda görüneceği bir ürün ve kullanıcı akışı kararıdır; sürtünme yasağıyla birlikte tartılır |
| **K-114** | Aday alt sektör kümesini hangi sorgu yetkili olarak üretecek? | A) Tek yetkili sorgu tanımlanır / B) Tüketici başına ayrı üretim | **[AÇIK]** — kök seviye filtresi bunu karşılamaz: ters kümedir. O filtre kök satırları eler, bu karar aday kümesini üretir | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — veri erişim sözleşmesidir |
| **K-115** | Aday küme öneri çağrısına nasıl teslim edilecek? | A) Mevcut site analizi sözleşmesi genişletilir / B) Ayrı bir uç tanımlanır | **[AÇIK]** — K-116'dan ayrı seçilebilir: iki tüketici aynı taşıma mekanizmasını kullanmak zorunda değildir | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — arayüz sözleşmesidir |
| **K-116** | Aday küme açılır listeye nasıl teslim edilecek? | A) Ayrı bir liste ucu / B) Mevcut uçtan türetme | **[AÇIK]** — K-115'ten ayrı seçilebilir (aynı gerekçe, ters yön) | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — arayüz sözleşmesidir |
| **K-117** | Web sitesi olmayan marka için öneri hangi uçtan çağrılacak? | A) Mevcut uç aynı akışla çağrılır / B) Ayrı bir akış tanımlanır | **[AÇIK]** — geri düşüş davranışı ortaktır ve kaynak katmanında karara bağlanmıştır; açık olan hangi ucun nasıl çağrılacağıdır | Teknik sahip | `[TANIMSIZ]` | **Spec içinde teknik olarak çözülür** — arayüz akışıdır |
| **K-20** | Katman-1 prompt yakalama düzeneği Marka DNA işiyle ortak mı kullanılacak? | A) Aynı koşum paylaşılır / B) Ayrı koşum | **[AÇIK] — öneri:** **A** — kaynak *"ikinci altyapı kurulmaz"* der ama maddesi açık iş işaretlidir; hüküm kesinleştirilmemiştir. Düzeneğin kurulması zorunludur; bu karar yalnız paylaşımı belirler | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(maliyet ayağı)* | Düzenek yazımından önce | **Spec öncesi kullanıcı kararı** — ikinci bir doğrulama altyapısının kurulup kurulmayacağı bir maliyet ve iş yükü tercihidir |

---

### 17.4 Politika, güvenlik ve uyumluluk kararları — 36 karar

| ID | Soru / karar | Seçenekler | Öneri | Karar sahibi | Son tarih | Spec'i bloklar mı? |
|---|---|---|---|---|---|---|
| **K-03** | Dönem tür etiketi ile takvim kategorisi çatıştığında hangisi üretim davranışını belirler? | A) Paketin tür etiketi üstündür; kategori korunur ve günün kimliğiyle doğrulanması için kullanılır / B) Kategori üstündür | ✅ **KAPANDI — A** (2026-08-17, kullanıcı kararı). Kapsam dardır: yalnız tür ↔ kategori çatışması; genel bir *"koşuyu blokla"* kuralı kurulmaz ve K-23 kapanmaz. Kapanışın iki artefaktı vardır: yürürlükteki sentez görev sözleşmesi hâlâ *"kararı verme, açık soruya düşür"* der — düzeltmesi Bölüm 14.4'te sürümlü supersession olarak kayıtlıdır; bu belgenin kendi kabul matrisi (13.7) aynı turda hizalanmıştır | — (kapandı) | — (kapandı) | **Bloklamaz** — karar kapanmıştır; kaydı Ek B'dedir. Sözleşme supersession'ı ayrı bir iş kalemidir |
| **K-118** | Kullanıcının somut isteği ile markanın ses/üslup profili çatışırsa hangisi kazanır? *(Yasak kelime kısıtı bu sorunun dışındadır — o zaten isteğin üstündedir)* | A) Ses/üslup profili üstte / B) Kullanıcı isteği üstte | **[AÇIK]** — sıranın uçları kapalıdır: en üstte güvenlik/mevzuat, marka DNA'sı paketin üstünde, en altta platform tonu ve kök rehber. Açık olan yalnız bu orta basamak | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — her üretimde işleyen öncelik kuralıdır; çalışma zamanı bağlam birleştirme kuralı bu sıra yazılmadan tanımlanamaz |
| **K-119** | Anma günlerinde satış dili yasağı, kullanıcının somut isteğini geçersiz kılabilir mi? | A) Yasak üstündür — paketin kullanıcı isteğini ezebildiği tek yer / B) Kullanıcı isteği üstündür, pakete istisna tanınmaz | **[AÇIK]** — tartılan şey kültürel ve itibar riskinin kabulü ile kullanıcı kontrolü arasındaki tercihtir. K-118 ve K-03'ten ayrı seçilebilir; onların kapanmasıyla kapanmaz | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — anma günü üretiminin davranışını ve kabul kriterini belirler |
| **K-120** | `anma` türünün *"içerik önerilmez"* dalı ile dönem başına en az iki çağrı kalıbı isteyen alt sınır arasındaki gerilim nasıl çözülecek? | A) Muafiyet tanımlanır / B) Boş alan ayrı temsil edilir / C) Dal sözleşmeden kaldırılır | **[AÇIK]** — iki sözleşme hükmü aynı anda sağlanamıyor; çözüm seçilmeden `anma` dönemi için paket üretilemez | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — anma dönemlerinde ne üretileceğini belirler; içerik politikası kararıdır |
| **K-04** | Paketin liste alanlarının tetiklediği *"listeyi tamamlama"* refleksine karşı sabit kullanım talimatı yazılacak mı? | A) Her enjeksiyon bloğunun başına sabit talimat yazılır / B) Yazılmaz | ✅ **KAPANDI — A** | — (kapandı) | — (kapandı) | **Bloklamaz** — karar kapanmıştır; kaydı Ek B'dedir |
| **K-05** | Kanal-bağımlı kalıplar için Faz 1'de hangi önlem alınacak? | A) Faz 1: kullanım talimatına tek satır / B) Faz 1'de kanal envanteri de kurulsun | ✅ **KAPANDI — B** (2026-08-21, kullanıcı kararı): Faz 1'de kanal envanteri de kurulur. ⚠️ Yön, belgedeki önerinin (*A'ya eğilim — envanterin doğal evi Marka DNA işidir*) **tersidir**. Kullanım talimatı satırı (**K-04** bağlantısı) korunur | — (kapandı) | — (kapandı) | **Bloklamaz** — karar kapanmıştır; kaydı Ek B'dedir. Sonuç: Marka DNA işinde alan adayı olarak tanımlı kanal envanteri **bu işin Faz 1 kapsamına çekilir**; Faz 1 kapsamı büyür ve **Marka DNA işiyle sınır yeniden çizilir — spec bu sınırı tanımlamalıdır** |
| **K-121** | Global tavan aşıldığında hangi kalıplar önce elenecek? | A) Sektöre özgülük → mutabakat gücü → yerellik / B) Zorunlu mevzuat ve güvenlik bilgisi en üstte, mevcut pakette doğrulanmış sektöre özgü kalıplar ikinci sırada | **[AÇIK]** — superseded bir hüküm değil, açık bir öncelik çelişkisidir: bir katman kaynak sıralamasını korur, diğeri sıralamayı bilinçli olarak değiştirdiğini kendisi yazar | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — kırpmanın hangi kalıpları eleyeceği doğrudan paket içeriğini belirler |
| **K-122** | Churn koruması benimsenecek mi? — *"yeni fakat daha zayıf bir öğe, yalnız yeni olduğu için mevcut doğrulanmış kalıbı paketten çıkaramaz"* | A) Benimsenir / B) Benimsenmez | **[AÇIK]** — K-121'den ayrı seçilebilir: kırpma önceliği seçilip churn koruması reddedilebilir | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — paket evrim politikasıdır; benimsenirse hem elle hem motorlu turda uygulanır |
| **K-123** | *"Güçlü kaynak"* sınıfının ölçütleri tanımlanacak mı? — resmî/birincil kaynak önceliği, bağımsız kaynak sayısı, güncellik, Türkiye yerelliği | A) Ölçüt tanımlanır / B) Tanımlanmaz | **[AÇIK]** — ölçüt taranan katmanların hiçbirinde tanımlı bulunamadı. Girdi tarafında eksik yoktur: brief sözleşmesi tek kaynaklı iddiaların işaretlenmesini zorunlu tutar; açık olan yalnız ölçüttür | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(kalite/risk ayağı)* | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — ölçüt tanımlanmazsa tekil kaynaklı iddianın pakete girmesi yargısal kalır; tanımlanırsa araştırma ve denetimde ek yük doğar |
| **K-124** | `cikar` için gereken pozitif kanıtın yeterlilik eşiği tanımlanacak mı? | A) Eşik sözleşmede tanımlanır / B) Tanımlanmaz *(kaynak katmanı seçenek saymaz; kararın kendi iki kutbu yazılmıştır)* | **[AÇIK]** — tek doğrulanmış birincil kaynak, iki denetçi mutabakatı ve yüksek etkili risklerde operatör onayı arasındaki ilişki yazılı değildir | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(risk/yük ayağı)* | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — kanıt eşiği doğru bilginin paketten çıkarılma riskini belirler; yükseltmek denetim yükünü artırır |
| **K-125** | Motor katmanında `guncelle` ve `cikar` için iki denetçi mutabakatı kapısı benimsenecek mi? | A) Benimsenir / B) Benimsenmez | **[AÇIK]** — kapı benimsenirse yeniden doğrulama envanterinin adı ve şeması (K-100) da gerekli olur. **K-100 ayrı bir karardır:** birlikte seçilebilirler, ama tek karara birleştirilemezler. Bağ tek yönlüdür — K-100'ün benimsenmesi bu kapıyı gerektirmez | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — politika motoru spec'ini bloklar (K-22). Kapı benimsenirse resmî hakem tur sözleşmesi de revize edilir; reddedilirse bu nedenle bloklanmaz. Pilot spec'i ve aktivasyon koşullu etkilenir |
| **K-126** | Tek resmî/birincil kaynak istisnasının kesin sözleşmesi tanımlanacak mı? | A) Sözleşme tanımlanır / B) Tanımlanmaz | **[AÇIK]** — iki denetçi URL doğrulaması ve kaynak önceliği arasındaki ilişki yazılı değildir | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(kapsam/risk ayağı)* | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — istisnanın sınırı, tek kaynağa dayanan mevzuat bilgisinin pakete girip girmeyeceğini belirler |
| **K-127** | Koşu en az kaç kaynakla devam edebilir? | A) Taban tanımlanır / B) Tanımlanmaz | **[AÇIK]** — taban hiçbir katmanda yazılı değildir ve uydurulmadı | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — kanıt kalitesi ↔ turun tamamlanabilirliği tercihidir |
| **K-23** | Motorun karar veremediği maddeler ne olacak? | A) Yöneticiye açık soru olarak düşer / B) Güvenli varsayılana düşer — mevcut kalıp korunur, rapora yazılır / C) Tur durur | **[AÇIK] — öneri:** **B + rapor** — evrimsel modelin *"kanıt yoksa koru"* ilkesiyle tutarlıdır; (A) ölçekte insana iş geri yükler, (C) tek maddede turu bloklar. Bir kaynak katmanı güvenli varsayılanı karara bağlar, diğeri aynı yönü eğilim olarak yazar — bu belge taraf tutmaz. Kararsızlık ORANININ tur durdurması ayrı karardır (K-132), eşiğin değeri K-24'tedir. K-03'ün kapanması bu kararı kapatmaz | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — motor Faz 1'de olduğundan (✅ K-22 KAPANDI — A) gerekli |
| **K-128** | Otomatik çözülemeyen politika çatışmasında koşu bloklanacak mı? | A) Bloklama kapısı kurulur, konu istisna olarak yöneticiye çıkarılır / B) Kurulmaz, konu açık soruya düşer | **[AÇIK]** — K-23'ten ayrı seçilebilir: açık soru yolu seçilip bloklama kapısı ayrıca kurulabilir | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — motor Faz 1'de olduğundan (✅ K-22 KAPANDI — A) gerekli |
| **K-129** | Mevzuat/güvenlik sayılan alanların ve koşuyu bloklayan uyuşmazlıkların kesin listesi sabitlenecek mi? | A) Liste sözleşmede sabitlenir / B) Sabitlenmez | **[AÇIK]** — liste sabitlenmezse hangi uyuşmazlığın turu durduracağı yargısal kalır | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — hangi alanların bloklayıcı sayılacağı bir politika ve risk kararıdır |
| **K-130** | Değişim büyüklüğü bariyeri benimsenecek mi? | A) Benimsenir / B) Benimsenmez | **[AÇIK]** — eşik değeri kararın parçası değil sonucudur; benimsenirse pilotta ölçülür (K-24) | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — motor Faz 1'de olduğundan (✅ K-22 KAPANDI — A) gerekli |
| **K-131** | Ekleme oranı bariyeri benimsenecek mi? | A) Benimsenir / B) Benimsenmez | **[AÇIK]** — K-130'dan ayrı seçilebilir | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — motor Faz 1'de olduğundan (✅ K-22 KAPANDI — A) gerekli |
| **K-132** | Kararsızlık oranı bariyeri benimsenecek mi? — motorun kararsız bıraktığı madde oranı eşiği aşarsa tur durur | A) Benimsenir / B) Benimsenmez | **[AÇIK]** — K-130 ve K-131'den ayrı seçilebilir | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — motor Faz 1'de olduğundan (✅ K-22 KAPANDI — A) gerekli |
| **K-133** | Kuru mod zorunlu olacak mı? — motorun kararlarını uygulamadan önce yalnız raporlaması | A) Zorunlu / B) Zorunlu değil | **[AÇIK]** — bariyerlerden ayrı seçilebilir | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — motor Faz 1'de olduğundan (✅ K-22 KAPANDI — A) gerekli |
| **K-134** | Motor işletime alınırken eski doğrudan operatör-onay akışı ne olacak? | A) Eski akış motor kanıtlanana kadar paralel korunur / B) Motor işletime alınırken eski akış kaldırılır *(kaynak katmanı seçenek saymaz; kararın kendi iki kutbu yazılmıştır)* | **[AÇIK]** — paralel koşum operasyon yükü doğurur, tek geçiş ise motorun kanıtlanmadan tek yol olmasını kabul eder | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — motor Faz 1'de olduğundan (✅ K-22 KAPANDI — A) gerekli; geçiş planının parçasıdır |
| **K-28** | Motor `active` satırına dokunabilir mi? | A) Yalnız taslak üretir, `active`'e asla dokunamaz / B) Belirli koşullarda otomatik aktive edebilir | **A — kesin.** İlke her iki kaynak katmanında da yazılıdır: motor `active`'e dokunamaz, `bloklandı` sonuç hiçbir yol üzerinden aktive edilemez, aktivasyon yalnız yöneticinin onayıyla gerçekleşir. Açık olan ilke değil, sunucu tarafında nasıl zorlanacağıdır; o ayak K-103'ün kapsamındadır | Ürün sahibi | `[TANIMSIZ]` | **Bloklamaz** — (A) kaynaklarda çözülmüş ilkedir: motor `active`'e dokunamaz. Sunucu tarafında nasıl zorlanacağı **K-103'tür ve ayrı bir teknik karardır**; bu satırın açıklığına veya sahipliğine birleştirilmez |
| **K-135** | Yazma yetkisinin operatör ve koşu yüzeyinde toplanması karara bağlanacak mı? | A) Yetkilendirme modeli olarak karara bağlanır / B) Çalışma varsayımı olarak bırakılır | **[AÇIK]** — varsayım olarak bırakılırsa yetki sınırı yazılı bir kural olmaz | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(risk ayağı)* | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — yetkilendirme modelinin yazılı kural olup olmayacağı bir güvenlik riski kabulüdür |
| **K-10** | Paket içeriğinde prompt-injection riskine karşı ek savunma kurulacak mı? | A) Ek savunma — talimat-benzeri metin taraması / B) Mevcut üç savunma yeterli sayılsın | **[AÇIK]** — paket içeriği araştırma çıktısından türer ve denetimden geçer; ek tarama kurulum yükü doğurur | Yönetici / operatör + teknik sahip | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — güvenlik riski kabulü ile kurulum yükü arasında tercihtir |
| **K-136** | Orkestrasyon günlüklerinde gizli bilgi ve kimlik bilgisi saklanmaması için kural ve teknik önlem tanımlanacak mı? | A) Kural ve teknik önlem tanımlanır / B) Tanımlanmaz | **[AÇIK]** — koruma tanımlanmazsa günlüklerde kimlik bilgisi tutulması riski kabul edilmiş olur; tanımlanırsa maskeleme ve saklama kuralı işi doğar. K-137'den ayrı seçilebilir: kimlik bilgisi hijyeni ile körlük bütünlüğü farklı şeyleri korur | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(risk kabulü)* | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — güvenlik riski kabulü ile maskeleme/saklama kurulum yükü arasında tercihtir |
| **K-137** | Araç–kaynak eşlemesinin kör denetçi bağlamına sızmaması teknik olarak garanti edilecek mi? | A) Sızmayı önleyen teknik garanti tanımlanır / B) İlke düzeyinde bırakılır | **[AÇIK]** — yapısı K-79 ile aynıdır: körlüğün teknik güvencesi ↔ kurulum işi. K-138'den ayrı seçilebilir | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(risk kabulü)* | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — garanti kurulmazsa çift kör denetimin körlüğü güvenceye bağlanmamış olur |
| **K-16** | Paket içeriği uygulama arayüzü üzerinden okunabilir olacak mı? | A) Yalnız iç kullanım / B) Yönetici arayüzüne açık / C) Müşteriye görünür | **[AÇIK] — öneri:** **A veya B** — paket ticari sır değildir, ama ürünleştirme kapsam dışı olduğundan müşteriye açmanın gerekçesi yoktur. K-138 ve K-139'dan ayrıdır: bu satır paket içeriğinin, onlar ham kanıt katmanının okunabilirliğini sorar | Yönetici / operatör | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — görünürlük seviyesi bir ürün kararıdır ve arayüz kapsamını belirler |
| **K-138** | Araç ↔ ham rapor eşlemesi kalıcı olarak kaydedilecek mi? | A) Kaydedilir / B) Kaydedilmez | **[AÇIK]** — K-137 ve K-139'dan ayrı seçilebilir: eşleme kaydedilip erişimi dar tutulabilir, ya da tersi | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — izlenebilirlik ile körlüğün korunması arasında tercihtir |
| **K-139** | Ham kanıt katmanı ve araç eşlemesi kimlere görünür olacak? | A) Erişim ve yetkilendirme modeli tanımlanır / B) Tanımlanmaz | **[AÇIK]** — K-138'den ayrı seçilebilir | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — erişim politikasıdır; körlüğün fiilen korunmasını belirler |
| **K-140** | Ham araştırma katmanı ne kadar süre saklanacak? | A) Sonlu bir süre tanımlanır / B) Sınırsız saklama sürdürülür | **[AÇIK]** — süre hiçbir katmanda yazılı değildir ve uydurulmadı | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — veri yaşam döngüsü, maliyet ve kanıt saklama tercihidir |
| **K-141** | Aktive edilmiş paket sürümleri ne kadar süre saklanacak? | A) Sonlu bir süre tanımlanır / B) Sınırsız saklama sürdürülür | **[AÇIK]** — K-140'tan ayrı seçilebilir. Arşiv güvencesinin bağlayıcılığı (K-40) bu kararla birlikte tartılır | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — arşiv taahhüdünü ve maliyeti belirler |
| **K-142** | Aktive edilmeden kalan taslaklar ayrı bir saklama kuralına mı bağlanacak? | A) Taslaklar için ayrı bir kural tanımlanır / B) Taslaklar aktif sürümlerin kuralına tabidir | **[AÇIK]** — K-141'den ayrı seçilebilir | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — veri yaşam döngüsü kararıdır |
| **K-143** | Taslaklara özgü saklama kuralının süresi ne olacak? | A) Sonlu bir süre tanımlanır / B) Sınırsız saklama sürdürülür | **[AÇIK]** — süre bir veri yaşam döngüsü ve maliyet tercihidir; *"kararın sonucu"* diye teknik ayrıntıya indirilemez | Ürün sahibi | `[TANIMSIZ]` | **Koşullu** — K-142'de ayrı kural seçilirse doğar |
| **K-144** | *"Faz 1'de ayrı hukuk onayı gerekmiyor; yalnız kamuya açık yayımlanmış kaynaklardan derleme yapılıyor"* değerlendirmesi benimsenecek mi? | A) Benimsenir, risk kabulü kaydedilir / B) Benimsenmez, ayrı değerlendirme istenir | **[AÇIK]** — değerlendirme bir hukuk görüşü değildir; benimsenmesi bir risk kabulüdür | Ürün sahibi | `[TANIMSIZ]` | **Spec öncesi kullanıcı kararı** — hukuki risk kabulüdür; (B) seçilirse dış görüş beklenir ve takvim etkilenir |
| **K-12** | Tier 2 belirteç bütçesi paket bloğu ile Marka DNA blokları için birlikte mi yönetilecek? | A) Birlikte ölçülüp tavan konsun / B) Ayrı ayrı yönetilsin | **[AÇIK] — öneri:** **A — ama önce ölçülmeli.** Kaynaklarda iki farklı boyut hedefi yazılıdır (~1,2–1,5K belirteç / ~1 cent ile ~6.000 karakter ≈ 2.000 belirteç) ve birbirini tutmaz; ikisi de ölçüm değildir ve kapı, kabul kriteri veya ölçüm kapısı yapılamaz. Ölçüm yalnız maliyeti değil önbellek eşiğini de kapsar ve uygulamada kullanılacak güncel model üzerinden yapılır | Teknik sahip *(mekanizma)* · **Ürün sahibi** *(maliyet ayağı)* | `[TANIMSIZ]` | **Ölçülmedi** — blok durumu iddia edilemez. Önce ölçülecek: paket bloğu ile Marka DNA bloklarının güncel model üzerindeki gerçek belirteç maliyeti ve önbellek eşiğine etkisi. İki yazılı boyut hedefi uzlaşmaz ve ikisi de ölçüm değildir |
| **K-145** | Kural hatasında etkilenen paketlerin tümü koşulsuz mu geri alınır? | A) Koşulsuz toplu geri alma / B) Vaka bazında geri alma | ✅ **KAPANDI — B** (2026-08-17, kullanıcı kararı): vaka bazında geri alma, güvenli varsayılanla. Etkisi kanıtlananlar geri alınır; etki alanı güvenilir ayrılamıyorsa kuralın uygulandığı tümü geri alınır; etkilenmediği kanıtlananlar geri alınmaz. Ölçütler tanımsızdır ve uydurulmamıştır | — (kapandı) | — (kapandı) | **Bloklamaz** — karar kapanmıştır; kaydı Ek B'dedir. Ölçüt tanımı ayrı bir teknik iş kalemidir |

> Kararlaştırılan maddeleri silme; kararı, tarihini ve gerekçesini yazarak
> "Karar günlüğü"ne (Ek B) dönüştür.

---

## 18. Riskler ve kontroller

[ZORUNLU]

#### Bu tablonun okunma kuralları — dört sınır

1. ⚠️ **Olasılık ve etki dereceleri ölçülmemiştir ve kapıya çevrilmez.** `D/O/Y` sütunları **şablondan** gelir; **değerler yalnız bir hakem belgesinin değerlendirmesidir** — `olasılık` kalıbı diğer hakemde ve dokuz kaynak dosyada **0 isabet** verir (harf duyarsız; pozitif kontrol `risk` 16 ↔ 5/1/2/0/1/2/5/2/2). Değerler `[ÖLÇÜLMEMİŞ VARSAYIM]`'dır ve **eşik, kabul kriteri, önceliklendirme kapısı veya iptal ölçütü hâline getirilmemiştir** (Bölüm 2.1). **Derecelendirilmemiş satırlarda hücre `—`'dir; bu belge derece uydurmaz.**
2. ⚠️ **Tespit yöntemi yazmak, alarm katmanını benimsemek değildir.** Tespit hücreleri **mevcut ve önerilmiş gözlem noktalarına** işaret eder (Bölüm 13.6 log ve metrikleri, Bölüm 13.7 kabul matrisi, Katman-1/Katman-2). **Eşiğe bağlı uyarı üretiminin benimsenmesi ve sorumlusu açık karardır** (Bölüm 13.6); bu tablo o kararı ne kapatır ne de ima eder.
3. ⚠️ **Sahip sütunu yeni rol ataması üretmez — ama boş da bırakılmaz.** Roller Bölüm 15'te yazılmıştır ve **beş kullanıcı kararı açıktır**. Tabloda üç ad geçer: **Operatör** (ortak ve kaynakta karara bağlı) · **Teknik sahip** (rol kullanımdadır, **ataması açıktır**) · **Ürün sahibi** (⚠️ **yalnız bir hakemde**; koşu/aktivasyon rolünün ikiye bölünmesi açık karardır). Sahip hücresindeki `⚠️` bu iki açıklığa işaret eder. ⚠️ **Sekiz satırda sahip `[AÇIK]`'tır: sahiplik iki hakem belgesinde de yazılı değildir** — bu satırların karşılığı diğer hakemde yoktur ve o belgede zaten `Sahip` sütunu bulunmaz; dokuz kaynak dosyada da bir risk tablosu yoktur. **Sekizi ayrı ayrı seçilebildiği için sekiz ayrı açık karardır** — aşağıya bakınız. **Şablonun zorunlu alanı boş bırakılmaz, açık kalem olarak işaretlenir** (Bölüm 16'daki pilot süresi emsali). ⚠️ **Sahibi yazılı olan üç satırda bağ kurulmuştur ve bağın türü satırında işaretlidir.**
4. ⚠️ **Açık karara bağlı kontrol normatif hüküm yapılmaz.** Bazı satırların kontrolü henüz kapanmamış bir karara dayanır (kalıcı kalıp kimliği · üretim sürüm damgasının veri yeri · değişim bariyerleri · kuru mod · sinyal odaklı özet · temel sürüm kontrolü · motorun fazı). O hücreler kontrolü **öneri statüsünde** taşır ve bağlı olduğu kararı adlandırır (Bölüm 2.5 md.8).

⚠️ **İşaretlenmiş şablon sapması — tabloya üç sütun eklenmiştir.** Şablonun tablosu `| Risk | Olasılık | Etki | Önleyici kontrol | Tespit yöntemi | Gerçekleşirse aksiyon | Sahip |` sütunlarına sahiptir. Eklenenler: **`ID`** — belgenin sekiz ayrı yerinden bu kayda atıf yapılır ve atıf ID'siz kurulamaz; **`Etki ve sonuç`** — bir hakemin `Sonuç` sütunu şablonda karşılıksızdır ve kayıp kontrolünde korunması gerekir, derece harfiyle aynı hücrede birleştirilmiştir; **`Kaynak statüsü`** — her satırın **iki hakemde mi, bir hakemde mi, kaynakta mı** bulunduğunu satırın kendi içinde taşır. Sapma bilinçlidir ve **sessizce değil, işaretlenerek** yapılmıştır (Bölüm 15 ve Bölüm 17 tablosu emsali).

#### Risk kaydı

> **Derece:** D = düşük · O = orta · Y = yüksek · `—` = **iki hakem belgesinde de derecelendirilmemiştir** (bu belge derece uydurmaz).

| ID | Risk | Olasılık | Etki ve sonuç | Önleyici kontrol | Tespit yöntemi | Gerçekleşirse aksiyon | Sahip | Kaynak statüsü |
|---|---|---|---|---|---|---|---|---|
| **R-01** | Sektör çözücüsü alt sektör satırını tam eşleşmeyle yakalar → *"Kuyumculuk"* yazan markanın sektör kimliği alt sektöre çözülür | **Y** | **Y** — kök kova değişmezi bozulur; trend, şablon ve rehber seçimi yanlış katmandan gelir | Çözücüde kök seviye (`parent IS NULL`) filtresi + regresyon testi — **zorunlu iş** | Alt sektör satırı eklenmeden önce ve sonra tam karşılaştırma | Filtreyi ekle; etkilenen markaları geri düzelt | Teknik sahip ⚠️ | **Ortak + kaynakta karara bağlı** — kaynak riski *"GERÇEK ve kısmi eşleşmeden derin"* diye kaydeder ve filtreyi zorunlu iş sayar |
| **R-02** | Alt sektör, marka kayıt ekranının açılır listesine sızar → kullanıcı kök yerine alt sektör seçer | O | O | Sektör listeleme ucuna kök filtresi — **tek nokta, üç ön yüz sayfasını birden kapatır** | Uygulama arayüzü testi | Filtreyi ekle; yanlış atanmış markayı düzelt | Teknik sahip ⚠️ | ⚠️ **Risk satırı yalnız bir hakemde, ama koruma noktası kaynakta yazılıdır** — *"yalnız bir hakemde"* demek yanlış olurdu |
| **R-03** | Yerine-geçme kuralı delinir — **iki mod:** *(a)* bir tüketici hâlâ kök rehberi okur, üretim paketi okur; *(b)* kök rehber ile paket **yan yana** basılır | **Y** ⚠️ *(gerekçe: enjeksiyon çıpası bugün eksiktir. **Ayrışmanın kendisi ilk paket etkinleşmeden gerçekleşemez** — bugün aktif paket yoktur, Bölüm 16)* | O — aynı marka için iki farklı sektör sesi; çelişen talimat | Aktif pakette **yerine-geçme** kuralı; kuralı **her üç tüketiciye** uygula; yan yana enjeksiyon **yasak**; legacy kısa video yolunun akıbeti (**K-06**) açıkça yazılır | Prompt yakalama karşılaştırması (**Katman-1**) | Eksik yüzeyi kapsama al | Teknik sahip ⚠️ | **Ortak** — iki mod iki ayrı hakemde adlandırılmıştır; **yan yana yasağı ve gerekçesi kaynakta karara bağlıdır** |
| **R-04** | Özel gün anahtarı normalize edildiği hâlde eşleşmez (gün bazlı satır · resmî uzun ad · sistemde başka adla kayıtlı dönem) | **Y** | O — paketin özel gün katmanı sessizce çalışmaz | **K-01b** normalize adımı; yazım ve okumanın **ortak kod yolu**; paket anahtarlarının sistem takvim listesine karşı doğrulanması | **Eşleşmezlik günlüğü — zorunlu** (Bölüm 13.6) | Normalize'ı düzelt; paketi yeni sürümle güncelle | Teknik sahip ⚠️ | **Ortak + kaynakta karara bağlı** — kaynak çakışmayı kanıtıyla kaydeder ve **K-01b**'yi oradan açar |
| **R-05** | Video hareket dili hiç sektörelleşmez — sektör satırına yazmak hareket istemini etkilemez | **Y** | O — video hareketi değişmez; kod yanlış yüzeye yazılır | **K-02** kararı; hareket havuzunun regresyon kapsamına **açıkça** alınması | **Katman-1** (hareket havuzu anlık görüntüsü) | **K-02**'nin bir seçeneğini uygula ya da **açıkça** Faz 2'ye park et | Teknik sahip ⚠️ | **Ortak + kaynakta karara bağlı** — ayrı yüzey tespiti kaynakta kanıtıyla yazılıdır |
| **R-06** | *"Listeyi tamamlama"* tuzağı → uydurma içerik; model dağarcığın tamamını kullanmaya çalışır | **Y** | **Y** — en üst öncelikteki uydurma yasağıyla doğrudan çatışır | Blok başına sabit kullanım talimatı (*2-3 öğe seç, listeyi tamamlama*) + boyut tavanı (**K-04**) | **Katman-2** kör örneklem değerlendirmesi — ⚠️ **kalite sinyalidir; geçme eşiği K-11 (b)'de açıktır** | Talimatı sıkılaştır; dağarcık boyutunu kırp | Teknik sahip ⚠️ | **Ortak + kaynakta karara bağlı**. ⚠️ **Kanıt vakası da kaynaktadır** (önceki bir entegrasyonda beş prensibin listeyi-tamamlama refleksiyle üçe indirilmesi) — diğer hakemde **0 isabet**, ama *"yalnız bir hakemde"* demek yanlış olurdu |
| **R-07** | Marka gerçeği ihlali — sahip olmadığı kanala ait çağrı kalıbı markaya basılır | **Y** | **Y** — sahte yönlendirme; uydurma yasağının ihlali | Kanal bağımlılığı etiketinin pakete taşınması + talimat satırı; tam çözüm kanal envanteridir — ✅ **K-05 KAPANDI — B** (2026-08-21, Ek B): envanter Faz 1'de bu işte kurulur | Kör örneklem değerlendirmesi — ⚠️ eşik açık (**K-11 (b)**) | Kalıbı kanal nötr uyarla; kanal alanı işini öne al | Operatör + teknik sahip ⚠️ | **Ortak + kaynakta karara bağlı** |
| **R-08** | **Paket yoluna girmeyen markada regresyon** — modele giden istem parçaları değişir | O | **Y** — belgenin en temel garantisi çöker | **Katman-1** byte-exact karşılaştırma, **zorunlu ve otomatik**; *boş alan = satır hiç enjekte edilmez* deseni | Byte-exact karşılaştırma — **tek bayt fark = RED** | **Derhal geri al**, pazarlık yok | Teknik sahip ⚠️ | **Ortak + kaynakta karara bağlı**. *(Kaynak burada "bit-düzeyinde" ifadesini kullanır; bu belgede düzeltilmiş biçim geçerlidir — Bölüm 13.)* |
| **R-09** | **İstem enjeksiyonu** — paket metni dil modeli üretimidir ve dış web kaynaklıdır; talimat benzeri metin isteme girebilir | O | **Y** | Hedef hattaki üç dolaylı savunma: mekanik biçim kapısı · iki bağımsız denetçinin iddia düzeyinde incelemesi · operatör onayı. ⚠️ **Üçü de bugün kurulmamıştır ve üçü de enjeksiyona özgü değildir** | ⚠️ **Tanımlı değildir — K-10** | Paketi devre dışı bırak; içerik taraması ekle. ⚠️ Devre dışı bırakmanın **desteklenen bir geçiş olup olmadığı Bölüm 8.1'de açıktır** | Operatör + teknik sahip ⚠️ | ⚠️ **Yalnız bir hakemde ve dokuz kaynak dosyada 0 isabet** (harf duyarsız, taze ölçüm) — kaynak katmanında hiç ele alınmamış tek risktir; **K-10** açık karardır |
| **R-10** | Değerli kalıp sessizce kaybolur — yanlış `cikar` kararı; yeni araştırma eski bilgiyi unutur | O | O — paket hafızası aşınır | `cikar` = **pozitif kanıt + kanıt satırı**; çıkarılanların özet farkta **sayı ve eşik üstü olanlar** hâlinde gösterilmesi (⚠️ eşik açık, Bölüm 7.8); geri-ekleme tetikleyicileri: her turda çıkarılanlar listesi hakem girdisine eklenir · son dört turun özeti · sürümler arası fark komutu | Sürümler arası fark komutu; çıkarma sayısı metriği | Geri ekle; karar günlüğüne çelişki notu yaz | Operatör | **Ortak + kaynakta karara bağlı** — kaynağın **üç katmanlı arşiv güvencesi**. ⚠️ Güvencenin **garanti mi hedef mi** olduğu açık karardır (Bölüm 7.6) |
| **R-11** | Geri-ekleme tetikleyicisi kaçırır — kalıp metni değiştiği için eski kayıtla eşleşmez | O | D | ⚠️ **Önleyici kontrol açık karara bağlıdır ve iki belge karşıt konumdadır** (Bölüm 6.3): biri bunu **kabul edilmiş zayıflık** sayar ve kalıcı kalıp kimliğini sonraki faza bırakır; diğeri **tam da bu nedenle** sürümler arası sabit kalıp kimliğini zorunlu sayar ve metin özetinin kimlik olamayacağını söyler. **Bu satır taraf tutmaz.** Kaynak yalnız dürüst sınırı yazar: gözlemlenebilir değeri olan kalıp **sessizce** kaybolmaz, sıfır kayıp garanti edilmez | Sürümler arası fark komutu | Elle fark edilirse karar günlüğüne not | Operatör | **Risk satırı yalnız bir hakemde; dürüst sınır kaynakta yazılıdır**; **karşıtlık iki hakemdedir** ve açık karardır |
| **R-12** | Mevzuat bilgisi eskir — tarihli düzenleme değişikliği pakette eski hâliyle kalır | **Y** | **Y** — yanlış hukuki yönlendirme | Yürürlük tarihli yazım; **tur dışı acil güncelleme kolu**; denetimde mevzuat iddialarına örneklem önceliği | Operatör gözlemi; tur denetimi | Paketi devre dışı bırak ya da tur dışı düzeltme koş | Operatör | **Ortak + kaynakta ve iki görev sözleşmesinde**. ⚠️ Bu riskin pilot örneği **bu sentezin tarihinde yürürlüğe girmiştir**; ortada aktif paket bulunmadığı için yeni karar açmaz (Bölüm 16.1) |
| **R-13** | Hakem hattı ortak mod hatası — iki denetçi aynı yanlışı birlikte yapar | O | O | Farklı model ve ortam · kör kaynak adlandırma · araç kimliği tahmini yasağı · yapılandırılmış çıktı | ⚠️ **Dürüst sınır: yakalanmayabilir.** Sentezin *"ikisi de aynı şeyi kaçırdı"* tespiti yapısal olarak zordur | Üçüncü göz — operatörün onay yüzeyindeki incelemesi | Operatör | **Risk satırı yalnız bir hakemde; sayılan dört kontrolün dördü de kaynakta ya da denetçi görev sözleşmesinde yazılıdır**. ⚠️ **Araştırma katmanındaki karşılığı ölçülmemiştir** — üç aracın aynı yayımlanmış kaynak havuzunu okuması ortak mod hatasını dışlamaz `[ÖLÇÜLMEMİŞ VARSAYIM]` (Bölüm 7.2) |
| **R-14** | Adres doğrulaması hiç yapılamaz — iki denetçi de web erişimsiz kalır | O | O — yanlış doğrulama güveni | Denetçi metninde dürüst raporlama zorunluluğu; sentezde *doğrulanmamış* işaretlemesi; koşu öncesi erişim kontrolü (**K-14** açık) | Denetim raporunun ilk adımı | Mevzuat ve sayı iddialarını açık soruya düşür; pakete alma | Teknik sahip ⚠️ | **Ortak** — bir hakem risk satırı, diğeri açık karar olarak yazar |
| **R-15** | Operasyon yükü ölçeklenmez — üç aylık tur × paket sayısı elle koşuluyor | **Y** | O — turlar aksar, paketler bayatlar | Faz 1 aktif paket tavanı (**≤5**) — ⚠️ **kaynakta öneridir**, ilk turda ölçülüp revize edilecektir (**K-13**) | Tur başına operasyon süresi metriği (Bölüm 13.6) | Tavanı düşür ya da otomasyonu öne al — motorun fazı karara bağlandı (✅ **K-22 KAPANDI — A**, 2026-08-21, Ek B: motor **Faz 1'de**) | Operatör | **Ortak + kaynakta karara bağlı**. ⚠️ *"İnsan eliyle aylar sürer"* gerekçesi `[ÖLÇÜLMEMİŞ VARSAYIM]`'dır, **kapıya çevrilmez ve ayrı karar açmaz** (Bölüm 2.1) |
| **R-16** | Belirteç bütçesi ve maliyet öngörüsü tutmaz — paket ile Marka DNA blokları aynı katmanı birlikte şişirir | O | O | Paket için ~6.000 karakter tavanı şemada yazılıdır | Gerçek belirteç ölçümü (**K-12**) | Tavanı düşür; alan kırpması uygula | Teknik sahip ⚠️ | **Ortak + kaynakta maliyet notu olarak**. ⚠️ **İki rakam iki belgede birlikte durur** (~2.000 belirteç hedefi ↔ ~1,2–1,5K tahmini) ve **iki sistemin toplamı hesaplanmamıştır** `[ÖLÇÜLMEMİŞ VARSAYIM]` |
| **R-17** | Aktivasyon yarıda kalır — eski sürüm arşivlendi, yeni sürüm etkinleşmedi | D | O | İki adımın **tek işlem** içinde yürümesi `[VARSAYIM — spec'te netleşecek]` | Aktivasyon günlüğü; *paket bulunamadı* metriği | Aktivasyonu tamamla; sistem bu arada güvenlidir (mevcut yola düşer) | Teknik sahip ⚠️ | **Risk satırı yalnız bir hakemde; tek işlem gerekliliği iki hakemde de yazılıdır** (biri test listesinde, diğeri prosedürde). ⚠️ Yetkilendirme modeli açıktır (Bölüm 8.2) |
| **R-18** | Pilot temsil etmez — ürün görselli bir alt sektörde çalışan görsel kod yaklaşımı hizmet sektörlerinde çalışmayabilir | O | O | ⚠️ **Önerilen kontrol, genişlemede hizmet sektörünün ayrı değerlendirilmesidir; bu bir kapı değildir** — Bölüm 16.3'ün beş genişleme kapısı arasında yer almaz | İkinci paket denemesinde gözlem | Alan şemasını hizmet sektörü için gözden geçir | Operatör | ⚠️ **Yalnız bir hakemde** — `hizmet sektör` · `temsil etme` kalıpları diğer hakemde ve dokuz kaynakta **0 isabet** (harf duyarsız) |
| **R-19** | Otomasyon arşiv güvencesini sessizce boşaltır — motor kalıpları çıkarır, kimse kalıp kalıp bakmaz | **Y** | **Y** — belgenin en açık yazılı garantisi çöker | Motor için de **pozitif kanıt zorunlu**; kanıtsızsa çıkarma uygulanmaz, kalıp korunur · özet farkta çıkarılan sayısı ve eşik üstü olanlar (⚠️ eşik açık) · geri-ekleme tetikleyicilerinin korunması | Sürümler arası fark komutu; çıkarma sayısı metriği | Motor kurallarını sıkılaştır; çıkarma yetkisini geçici olarak insana geri al | Ürün sahibi ⚠️ | ⚠️ **Yalnız bir hakemde ve sonradan eklenen analiz statüsünde**; politika motoru kavramı dokuz kaynak dosyada **0 isabet** verir |
| **R-20** | Motorun yanlış kuralı bütün paketlere birden yayılır — insan hatası bir pakette kalırdı, kural hatası hepsinde tekrarlanır | O | **Y** | Pilotta kalibrasyon (**K-24** açık) · kademeli genişleme · **kuru mod** (motorun kararları uygulanmadan önce raporlanır) — ⚠️ **kuru modun zorunlu olup olmadığı açık karardır** (Bölüm 7.7) | Özet farkta beklenmedik toplu değişim; **Katman-2** kalite düşüşü (⚠️ eşik açık) | Etkilenen paketleri önceki sürüme geri al; kuralı düzelt | Teknik sahip ⚠️ | ⚠️ **Yalnız bir hakemde**, sonradan eklenen analiz |
| **R-21** | Yönetici özet farkı bir *onay tıklamasına* indirger — tek insan denetim noktası işlevsiz kalır | **Y** | **Y** | Özet farkın **karar verdirici / sinyal odaklı** tasarlanması — ⚠️ **benimsenmesi açık karardır** (Bölüm 7.8) · **Katman-2** örnekleminin onay girdisi olarak korunması | Aktivasyon süresi metriği — ⚠️ **eşik yoktur ve eşiğe bağlı uyarı katmanı açık karardır** (Bölüm 13.6) | Özet farkı yeniden tasarla; kritik sınıflarda zorunlu inceleme | Ürün sahibi ⚠️ | ⚠️ **Yalnız bir hakemde**, sonradan eklenen analiz |
| **R-22** | Motorun kararsızlık oranı yüksek çıkar — iş insana geri döner, otomasyon kazancı buharlaşır | O | O | Kararsızlık oranı metriği · motorun karar veremediği maddede güvenli varsayılan (**K-23** açık) · kalibrasyon. ⚠️ **Kararsızlık oranı bariyerinin benimsenmesi de açık karardır** (Bölüm 7.7) | Koşu raporu metriği | Kuralları genişlet ya da kapsamı daralt; motoru sonraki faza almak **kapanmış K-22'nin (✅ A, Ek B) kullanıcı kararıyla yeniden açılmasını gerektirir** | Teknik sahip ⚠️ | ⚠️ **Yalnız bir hakemde**, sonradan eklenen analiz |
| **R-23** | Ölçek gerekçesi doğrulanmamış — motorun varlık gerekçesi ölçülmemiş iki iddiaya dayanır | O | O — yanlış önceliklendirme | Pilotta **yöneticinin tur başına gerçek süresinin** ölçülmesi (Bölüm 13.6); hedef sektör sayısındaki belirsizliğin çözülmesi (**K-21**) | İlk turun süre kaydı | Ölçüm gerekçeyi desteklemiyorsa motorun kapsamı ve fazı yeniden değerlendirilir — faz değişikliği **kapanmış K-22'nin (✅ A, Ek B) kullanıcı kararıyla yeniden açılması** demektir | Ürün sahibi ⚠️ | ⚠️ **Yalnız bir hakemde**, sonradan eklenen analiz. **`[ÖLÇÜLMEMİŞ VARSAYIM]` — kapıya çevrilmez ve ayrı karar ID'si almaz** (Bölüm 2.1); besledigi kararlar **K-21** ve **K-22**'dir |
| **R-24** | Müşteri yüzeyi ile yönetici yüzeyi yetkilendirmede ayrılmazsa müşteri paket bakımına erişebilir | D | O | Rol ayrımının **yetkilendirmede zorlanması** — ⚠️ **zorlama ayağı açıktır** (Bölüm 15); kuralın kendisi ortaktır (Bölüm 12) | Yetki testleri (Bölüm 13.7) | Yetkileri ayır; erişim günlüğünü incele | Teknik sahip ⚠️ | ⚠️ **Risk satırı yalnız bir hakemde**, sonradan eklenen analiz; **kural ortaktır** |
| **R-25** | Paketin dönem türü ile takvim kategorisi çelişir → uygunsuz satış veya kutlama dili | — | — — uygunsuz dil üretimi | Önceden tanımlı öncelik politikası — ✅ **K-03 KAPANDI (2026-08-17): paketin tür etiketi üretim davranışında üstündür**, kategori korunur ve doğrulama için kullanılır (Bölüm 11.2). ⚠️ **Kontrol kesinleşti, risk DÜŞMEDİ:** politika yanlış uygulanırsa ya da sözleşme ayağı yansımazsa uygunsuz dil yine üretilir; **uygulama ayağı Bölüm 14.4'teki sözleşme düzeltmesine bağlıdır.** ⚠️ **Çözülemeyen çatışmada koşuyu bloklama kapısı yalnız bir hakemdedir ve yeni bir kapıdır** — diğer hakemde çatışma **açık soruya** düşer; kapı Bölüm 4.5'te açık karar olarak kayıtlıdır | Kabul matrisinin çatışma senaryosu (Bölüm 13.7) | ⚠️ **İki belgede de yazılı değildir** — kapı kararına bağlıdır | **[AÇIK]** ⚠️ | ⚠️ **Risk satırı yalnız bir hakemde; K-03 iki belgede de açıktır** |
| **R-26** | Aynı alt sektörde iki aktif sürüm oluşur | — | — — hangi paketin seçileceği belirsizleşir | **Kısmi benzersiz veri tabanı indeksi** — ikinci aktif paket yazımı reddedilir | Kurulum sonrası doğrulama; aktivasyon testi | ⚠️ **Yazılı değildir** | Teknik sahip ⚠️ | ⚠️ **Risk satırı yalnız bir hakemde; kontrol ortak ve kaynakta karara bağlıdır**. **Sahip bağı türetilmiştir:** Bölüm 15 teknik sahibe *migration* sorumluluğunu verir, indeks bir migration işidir — ⚠️ **risk sahibi olarak ayrıca yazılmamıştır** |
| **R-27** | Kötü sürümün kaynağı izlenemez | — | — — kök neden analizi yapılamaz | Üretilen post üzerinde **paket sürüm damgası** — ⚠️ **damganın veri yeri K-07'de açıktır** | Bölüm 13.6 izlenebilirlik zinciri | ⚠️ **Yazılı değildir** | Teknik sahip ⚠️ | ⚠️ **Risk satırı yalnız bir hakemde; damga gerekliliği ortak ve kaynakta karara bağlıdır**. **Sahip bağı açıktır:** Bölüm 15 teknik sahibin sorumlulukları arasında *üretim sürüm damgasını* birebir sayar |
| **R-28** | Sentez adayı doğrudan uygulanır — kanıtsız ya da eksik karar etkinleşir | — | — — denetlenmemiş içerik üretime girer | Veri tabanına **yalnız taslak** yazılır; etkinleştirme operatör onayıyla olur (**ortak + kaynakta**). ⚠️ Aynı hakemin eklediği ikinci kontrol — **politika motorunun zorunlu kapısı + arka uç yetkilendirmesi** — motorun fazına (**K-22**) ve yetki sınırının zorlanmasına (**K-28**, zorlama ayağı açık) bağlıdır | Yazım kapısının red kayıtları (Bölüm 13.6) | ⚠️ **Yazılı değildir** | Operatör | ⚠️ **Risk satırı yalnız bir hakemde; temel kontrol ortak ve kaynakta karara bağlıdır**. **Sahip bağı açıktır:** aktivasyon ve ret yetkisi operatördedir (ortak + kaynakta) |
| **R-29** | Eski öğelerin bir bölümü **kararsız bırakılır** — motor o kalıplar için hiç karar üretmez | — | — — geçerli sektör hafızası sessizce kaybolur | Kalıp kimliği bazlı **tam karar kapsamı** — ⚠️ **kalıcı kalıp kimliği gerçek çelişkidir ve açık karardır** (Bölüm 6.3); kontrol o karar kapanmadan normatif yapılamaz | ⚠️ **Yazılı değildir** | ⚠️ **Yazılı değildir** | **[AÇIK]** ⚠️ | ⚠️ **Yalnız bir hakemde**, sonradan eklenen analiz. ⚠️ **R-19'dan ayrıdır:** R-19 üretilmiş kararın **denetlenmemesi**, bu satır kararın **hiç üretilmemesidir** |
| **R-30** | Tek koşuda olağan dışı büyük değişim — araştırma ya da model kayması paketi topluca bozar | — | — — paket bir turda topluca değişir | Toplam ve alan bazlı **değişim büyüklüğü bariyeri** — ⚠️ **benimsenmesi açık karardır** (Bölüm 7.7); ilk koşuda oran hesaplanamaz, mutlak sınırlar uygulanır | ⚠️ **Yazılı değildir** — bariyerin kendisi hem kontrol hem sinyaldir | Koşu bloklanır (bariyer benimsenirse) | **[AÇIK]** ⚠️ | ⚠️ **Yalnız bir hakemde**, sonradan eklenen analiz. ⚠️ **R-20'den ayrıdır:** R-20 motorun **kural hatası**, bu satır **girdi kaymasıdır** |
| **R-31** | İçerik aynıyken yeni sürüm açılır | — | — — gereksiz sürüm ve geri alma karmaşası | İçerik hash'i karşılaştırması + **değişiklik yok** koşu sonucu — ⚠️ **canonical hash üretim kuralı açık karardır** (Bölüm 6.5). ⚠️ Aynı hakem **ilk koşuda bu sonucun geçersiz** sayılmasını da yazar | ⚠️ **Yazılı değildir** | Yeni sürüm satırı oluşturulmaz | **[AÇIK]** ⚠️ | ⚠️ **Yalnız bir hakemde.** Diğer hakemin modelinde **her koşu yeni taslak sürüm üretir** |
| **R-32** | Politika sonucu ile onay arasında aktif sürüm değişir → yanlış temel sürüme fark uygulanır | — | — — onaylanan fark, gerçekte başka bir sürümün üzerine biner | Temel paket kimliği ve sürümünün onay anında karşılaştırılması; **farklıysa** sonucun **geçersiz** sayılması — ⚠️ **yalnız bir hakemdedir ve yeni bir kapıdır**; **açık karardır** (Bölüm 7.8, 8.2) | Onay yüzeyinde sürüm karşılaştırması (kapı benimsenirse) | Sonuç geçersiz kılınır; koşu yenilenir | **[AÇIK]** ⚠️ | ⚠️ **Yalnız bir hakemde**, sonradan eklenen analiz |
| **R-33** | Müşteri ya da marka tercihi sektör evrimine karışır | — | — — ortak sektör paketi parçalanır, ölçek kaybolur | Müşteri sinyallerinin motor girdilerinden **dışlanması** — **kural ortaktır** (Bölüm 12: müşteri beğenisi, marka başına ton takibi ve etkileşim verisi karar matrisinin girdisi değildir) | ⚠️ **Yazılı değildir** | ⚠️ **Yazılı değildir** | **[AÇIK]** ⚠️ | ⚠️ **Risk satırı yalnız bir hakemde; kural ortaktır** |
| **R-34** | Uzun bağlamlı sentez kaçırır — iki denetim tablosunun bir bölümü sentezde hiç değerlendirilmez | — | — — denetlenmiş kanıt karar aşamasına ulaşmaz | **Alan alan hizalama** (uzun metin birleştirme yapılmaz; sekiz alan ve her özel gün ayrı işlenir) · çift bağımsız denetçi · yapılandırılmış çıktı sözleşmesi | ⚠️ **Yazılı değildir** | ⚠️ **Yazılı değildir** | **[AÇIK]** ⚠️ | ⚠️ **Risk ve kontrol kaynakta karara bağlıdır** — hakem mimarisinin **iki düzeltmesinin gerekçesi** budur ve **iki hakem belgesi de kontrolü aynı gerekçeyle taşır** (biri karar günlüğünde, diğeri alan bazlı sentez bölümünde). ⚠️ **Buna karşılık iki hakemin risk tablosunda da satırı yoktur;** kontrol benimsenmiş, **artık risk kaydedilmemiştir. Satır bu sentezde kayda alınmıştır** |
| **R-35** | **Paketin kişisel veri içermediği doğrulanmamıştır** — ham raporlarda gerçek firma adları geçebilir (örneğin mevzuat emsalleri) | — | — — doğrulanmadan saklama, anonimleştirme ve erişim politikası uygulanırsa **risk kabulü örtük yapılmış olur** | Marka adı bayrağı taşıyan metnin pakete girememesi **kaynakta yazılıdır** ve ortaktır; gerçek adlar **ham katmanda kalır**. ⚠️ **Üç ayağın statüsü aynı değildir** (Bölüm 6.6): **saklama süresi politikası** açık karardır · **erişim politikası** ⚠️ **iki değil ÜÇ açık karara** bağlanır — *paket içeriğinin* okunabilirliği **K-16** · *araç ↔ ham rapor eşlemesinin kalıcı kaydı* **K-138** · *ham katmanın okuma yetkisi* **K-139** · **anonimleştirme** ise **açık karar değildir: taranan belgelerin hiçbirinde ele alınmamış bir boşluktur** ve bu belgede politika üretilmez | ⚠️ **Doğrulamanın kendisi tespit yöntemidir; yazılı bir sinyal yoktur** | Doğrulama olumsuz çıkarsa saklama ve erişim politikası doğrulama sonucuna göre yazılır | **[AÇIK]** ⚠️ | ⚠️ **`[BU SENTEZDE DOĞRULANMADI]` — akıbeti ⑤ taze doğrulamadır.** İddia Bölüm 6.6'da beyan olarak kayıtlıdır. **Spec yazımını bloklamaz; gerçek veri yazımı ve aktivasyon öncesinde koşulmalıdır** — envanterde **B5 koşullu blok** profiliyle zaten kayıtlıdır |

#### Şablonun özellikle sorduğu yedi başlığın karşılığı

| Şablon başlığı | Karşılık gelen satırlar |
|---|---|
| Geriye uyumluluk ve regresyon | **R-01 · R-02 · R-03 · R-05 · R-08** |
| Veri kaybı veya yanlış veri sahipliği | **R-10 · R-11 · R-29 · R-34** — ⚠️ ham kanıt katmanı **salt ekleme** olduğu için veri kaybı riski **yapısal olarak düşüktür**; bu bir tasarım sonucudur, ölçüm değildir |
| Yetkisiz erişim / gizlilik | **R-09 · R-24 · R-35** + **K-16** (paket içeriğinin okunabilirliği açık). ⚠️ **R-35 bu kovanın taze doğrulama kalemidir:** *"paket kişisel veri içermez"* beyanı `[BU SENTEZDE DOĞRULANMADI]`'dır ve **doğrulanmadan saklama ve erişim politikası uygulanamaz** (Bölüm 6.6); *anonimleştirme* orada **açık karar değil, kayıtlı bir boşluktur* |
| Dış servis ve model bağımlılığı | **R-05 · R-13 · R-14** (video üretim servisi · denetçi ortamı · araştırma araçları) |
| Maliyet, gecikme ve ölçek | **R-15 · R-16 · R-23** |
| Yanlış otomatik karar / insan onayı yetersizliği | **R-06 · R-07 · R-10** *(üç kademeli yapı: denetçiler karar vermez, sentez karar verir, aktivasyon operatördedir)* + **motorlu modelde R-19 · R-21 · R-28 · R-29 · R-30 · R-31 · R-32** |
| Operasyonel yük ve sahiplik boşluğu | **R-15** + ⚠️ **bu bölümün sekiz sahiplik kararı** (aşağıya bakınız) + **teknik sahip ataması** (Bölüm 15). ⚠️ **Bölüm 15'in kalan üç rol kararı — bildirim hedefi · bulguların kabul yetkisi · operatöre bilgi geçişi — kendi bölümünde kayıtlıdır ve burada tekrar edilmez;** bu tablonun hiçbir hücresi onlara bağlı değildir. |

#### Bu bölümün açtığı ve açmadığı kararlar

**Sekiz yeni açık karar — sekizi de kullanıcı seviyesi.** ⚠️ **Kaynağı şablonun zorunlu `Sahip` alanıdır:** diğer hakemin risk tablosunda karşılığı olmayan sekiz satırda sahiplik **iki hakem belgesinde de** yazılı değildir ve dokuz kaynak dosyada bir risk tablosu bulunmaz. **Şablonun zorunlu alanı boş bırakılmaz, uydurulmaz da — açık kalem olarak işaretlenir** (Bölüm 16'daki pilot süresi emsali; Bölüm 15'te *teknik sahip ataması* aynı testle açılmıştır).

⚠️ **Sekizi ayrı ayrı seçilebilir, bu yüzden sekiz ayrı karardır.** Sahipliği ortak bir politikaya bağlayan hüküm **iki hakem belgesinde de, dokuz kaynak dosyada da bulunmaz**; biri atanıp diğeri açık bırakılabilir — örneğin **R-25**'in sahibi belirlenirken **R-35** açık kalabilir. **Tek kaleme bağlamak karar kimliğini silerdi.**

| # | Karar | Bağlı olduğu (ama indirgenemediği) kalem |
|---|---|---|
| 1 | **R-25**'in sahipliği — tür ↔ kategori çatışması | ✅ **K-03 kapandı**; çatışma kapısı **hâlâ açıktır**. ⚠️ **Sahiplik kararı K-03'ün kapanmasıyla kapanmaz** — *kimin sahiplendiği* baştan beri ayrı sorudur |
| 2 | **R-29**'un sahipliği — kararsız bırakılan eski öğeler | rol bölünmesi · **K-22** |
| 3 | **R-30**'un sahipliği — girdi kaymasından toplu değişim | değişim büyüklüğü bariyeri · **K-22** |
| 4 | **R-31**'in sahipliği — içerik aynıyken yeni sürüm | `değişiklik yok` kaydı · **K-22** |
| 5 | **R-32**'nin sahipliği — temel sürüm değişimi | temel sürüm kontrolü kapısı · **K-22** |
| 6 | **R-33**'ün sahipliği — müşteri tercihinin evrime karışması | ⚠️ **kural ortaktır** (Bölüm 12); açık olan yalnız ihlali kimin izleyeceğidir |
| 7 | **R-34**'ün sahipliği — uzun bağlamlı sentezin kaçırması | ⚠️ **motor katmanından ve rol bölünmesinden bağımsızdır** |
| 8 | **R-35**'in sahipliği — kişisel veri doğrulamasının yürütülmesi | saklama süresi politikası · **K-16**; ⚠️ **doğrulama kaleminin kendisinden ayrıdır** — o *neyin*, bu *kimin* doğrulayacağını sorar |

⚠️ **Sahiplik kararı bir rol *yaratmaz*.** Bölüm 15'in rol kümesi kapalı ilan edilmemiştir; bu sekiz karar yalnız **mevcut rollerden hangisinin bu satırları üstleneceğini** sorar.

**Bunların dışında bu bölüm yeni karar açmaz.**

- **Sekiz yeni sahiplik kararı** (yukarıdaki tablo).
- **Bir doğrulama kalemi:** *"paket kişisel veri içermez"* beyanının doğrulanması (**R-35**) — **karar değildir**, akıbeti ⑤'tir ve karar sayımına girmez.
- **On sekiz mevcut karar ID'si:** **K-01b · K-02 · ~~K-03~~ · K-04 · K-05 · K-06 · K-07 · K-10 · K-11 (b) · K-12 · K-13 · K-14 · K-16 · K-21 · K-22 · K-23 · K-24 · K-28**. ⚠️ **K-03 ve K-04 artık KAPALI kararlardır** — sweep satırları kayıttan düşmez, statüleri değişir; yeni durum **Bölüm 17 final sweep'inde** ölçülecektir.
- **On dokuz ID'siz mevcut açık karar:** kalıcı kalıp kimliği sözleşmesi · değişim büyüklüğü bariyeri · kararsızlık oranı bariyeri · kuru modun zorunluluğu · sinyal odaklı özet kontrolü · özet farkta eşik üstü çıkarılanlar eşiği · onay anında temel sürüm kontrolü · çatışmada bloklama kapısı · `değişiklik yok` kaydının yeri ve canonical hash kuralı · ilk koşuda `değişiklik yok` geçersizliği · arşiv güvencesinin garanti/hedef statüsü · alarm katmanının benimsenmesi ve sorumlusu · deaktivasyonun desteklenen geçiş olması · aktivasyon ve geri alma yetkisinin teknik zorlanması · koşu ve aktivasyon rolünün ikiye bölünmesi · teknik sahip ataması · *"Faz 1'de ayrı hukuk onayı gerekmiyor"* değerlendirmesi · saklama süresi politikası · **araç ↔ ham rapor eşlemesinin kalıcı kaydı ve okuma yetkisi**.

⚠️ **Bölüm 15'in beş yeni kararından yalnız ikisi bu evrendedir** — *teknik sahip ataması* (Sahip sütununda on beş satır bu role işaret eder) ve *hukuk değerlendirmesi*. ⚠️ **İkincisinin bağı TÜRETİLMİŞTİR:** kaynak, *ayrı hukuk onayı gerekmiyor* değerlendirmesini **kamuya açık kaynaklardan derleme** gerekçesine dayanan **genel bir risk kabulü** olarak taşır ve **R-35'in artık riskiyle özdeş olduğunu söylemez**; ortak zemin derlemenin **kaynağıdır**, R-35 ise derlemenin **içeriğine** ilişkindir. Bağ **sentezci çıkarımıdır**, kaynak hükmü değildir. **Diğer üçü — olay müdahalesinde bildirim hedefi · inceleme bulgularının kabul yetkisi · operatöre FYI — bu bölümün tablosunda hiçbir hücreye dokunmaz ve evrene alınmamıştır.** *(Bildirim hedefi riskin **sahibinden** ayrı bir sorudur; Bölüm 15 bu ayrımı zaten kurar.)*

⚠️ **Bir risk satırı yazmak, bağlı olduğu kararı kapatmaz.**

- ⚠️ **Taze doğrulamaya bırakılanlar (akıbet ⑤) — beş kalem:** olasılık ve etki dereceleri · *"insan eliyle aylar sürer"* · hedef sektör sayısı · belirteç bütçesi · **paketin kişisel veri içermediği beyanı (R-35)**. İlk dördü `[ÖLÇÜLMEMİŞ VARSAYIM]`, beşincisi `[BU SENTEZDE DOĞRULANMADI]`'dır; ölçüm ve doğrulama noktaları Bölüm 13.6 ve 6.6'dadır. ⚠️ **R-35 spec yazımını bloklamaz; gerçek veri yazımı ve aktivasyon öncesinde koşulmalıdır.**
- ⚠️ **Kapsam dışı bırakılan bir kalem — dürüst etiketle.** Risk kaydının **periyodik gözden geçirme ritmi ve o gözden geçirmenin sahibi** bu belgede **açılmamıştır.** **Kısmi bir ev zaten vardır:** genişleme anında risklerin yeniden değerlendirilmesi Bölüm 16.3'te yazılıdır. **Periyodik tur içindeki karşılığını bu belge üretmez** — ne iki hakem belgesi ne de dokuz kaynak dosya böyle bir yükümlülük yazar; **yokluk ölçümünden yükümlülük türetmek kapsam genişletmesi olurdu.** ⚠️ **Satır bazlı sahiplik kararlarıyla karıştırılmamalıdır:** onların kaynağı şablonun zorunlu alanıdır, bunun kaynağı yoktur. **Yeniden açılma koşulu:** spec seansında Bölüm 14 işletim yordamı yazılırken tur adımlarına risk kaydı gözden geçirmesi eklenecekse oradan açılır.

---

## 19. Örnek senaryolar

[ZORUNLU — en az bir normal, bir fallback/hata senaryosu]

#### Bu bölümün okunma kuralları — dört sınır

1. ⚠️ **Senaryoların tamamı hedef işletim modelini anlatır; hiçbirinin bugün uçtan uca koşturulabildiği doğrulanmamıştır.** *Then* satırları **beklenen davranışı** yazar, gözlenmiş davranışı değil. ⚠️ **Hazırlık durumunun kaydı tek tip değildir, üç sınıf ayrılır:**
   - **Alt sektör satırı · aktif paket · enjeksiyon çıpaları · prompt yakalama düzeneği** — 2026-07-11 taramasına göre **kurulmamıştır** (Bölüm 16.1); bu sentezde canlı kod veya veri tabanına karşı **yeniden doğrulanmamıştır**. *"Bugün kurulmamıştır"* değil, **"aktarılan son duruma göre kurulmamıştır"** okunmalıdır.
   - **Politika motoru** — kaynak katmanında bulunmadığı ölçülmüştür, ama **güncel sistemde var olup olmadığı ölçülmemiştir**. ⚠️ *"Kaynakta önerilmemiş"* → *"bugün kurulmamış"* **çıkarımı yapılamaz.**
   - **Yönetici koşu yüzeyi** — mevcut olup olmadığı **doğrulanmamıştır** ve Bölüm 17'de bir doğrulama kalemine bağlıdır.

   ⚠️ **Tek nüans 19.4'tedir:** oradaki kural yürürlükteki sentez görev sözleşmesinde yazılıdır ve sözleşme bugün geçerlidir — ama resmî hakem turu koşulmamıştır (Bölüm 16.1), dolayısıyla o senaryo da **gözlenmiş değildir**.
2. ⚠️ **Motorlu ↔ motorsuz ayrımı her senaryoda taşınır — yürürlükteki model motorlu modeldir** (✅ **K-22 KAPANDI — A**, Ek B). 19.1–19.5 **her iki modelde de** geçerlidir. **19.6 · 19.7 · 19.8 yalnız motorlu modelde geçerlidir** ve motor Faz 1'de olduğundan **Faz 1'de koşulur** (motorsuz modelde hiç oluşmazlardı).
3. ⚠️ **Bir senaryonun *Then* satırı açık kararı kapatmaz.** Beklenen sonucu henüz alınmamış bir karara bağlı olan her satırda **bağ cümlenin içinde taşınır** ve karar adlandırılır. Bu bölümde **hiçbir davranış, eşik veya enum uydurulmamıştır**; bir dalın davranışı hiçbir katmanda yazılı değilse **yazılmadığı yazılmıştır.**
4. ⚠️ **Senaryo bir kabul kriteri değildir.** Kabul kapıları Bölüm 2.3'te, doğrulama katmanları Bölüm 13'tedir. Buradaki *Then* satırları o kapıların **anlatısal karşılığıdır**; **Katman-2'ye ait gözlemler kalite sinyalidir ve otomatik red eşiği K-11 (b) kapanmadan tanımlanmaz.**

---

### 19.1 Normal akış — paketli markada üretim

**Given:**
- Kuyumculuk alt sektör satırı açılmış ve kök e-ticaret/perakende kovasının altına bağlanmıştır; markanın **kök kovası korunmuştur** (Bölüm 6.3).
- Markanın alt sektör alanı doludur ve bu alt sektörün **bir aktif paket sürümü** vardır.
- Kullanıcı bir ürün için post üretmek istemekte ve üretim ekranında **eşleşen bir özel gün** seçmiştir.

**When:** Kullanıcı üretimi başlatır.

**Then:**
- Marka ve ürün gerçekleri yüklenir; alt sektör alanı üzerinden **aktif paket** bulunur — sonuç en fazla tek satırdır (sektör başına tek aktif sürüm kısmi benzersiz indeksi, Bölüm 6.3).
- **Tier 2'de paket bloğu bulunur; kök `SECTOR_GUIDANCE` bulunmaz** — yan yana enjeksiyon yasaktır (Bölüm 4.1).
- Bloğun başında **dağarcık kullanım talimatı** yer alır — *birkaç öğe seç, listeyi tamamlama, sahip olunduğu bilinmeyen kanalı önerme* (**K-04**, kapalı karar). Talimatın metni Bölüm 4.6'dadır.
- Seçilen özel gün **kanonik anahtara** çevrilir ve pakette karşılığı bulunduğu için Tier 3'ün mevcut özel gün bağlamı bloğuna **dönemin kalıpları eklenir**; blok yapısı değişmez. ⚠️ **Anahtar biçimi K-01b'de açıktır** — o karar kapanmadan bu adımın anahtar sözleşmesi normatif değildir.
- Dönemin **tür etiketi** ikinci bir ton sürücüsü olur ve sistemin mevcut kategori-ton mekanizmasıyla üst üste biner. ✅ **Öncelik K-03'te KAPANDI: paketin tür etiketi üstündür**; kategori korunur ve günün kimliği ile doğrulanması için kullanılır (Bölüm 11.2). ⚠️ **Uygulanabilirliği sözleşme düzeltmesine bağlıdır** (Bölüm 14.4).
- Görsel üretiminde caption yönlendiricisinin çıktı talimatına **sektör görsel dili** eklenir; günün **görsel vurgusu** yalnız gün eşleştiğinde aynı yolla girer.
- **Video istenmişse** durağan kare istemi paketin **sahne kodlarını** alır — **iki modda da** (metinden görsele ve ürün referanslı düzenleme). ⚠️ **Hareket dili ayrı yüzeydir ve K-02'ye bağlıdır:** paket hareket havuzunun kullanılması, hareket komutunun modele ürettirilmesi ve hareket dilinin sonraki faza bırakılması **üç seçenektir** (Bölüm 10.2) — **bu satır seçmez.**
- Marka DNA'sında farklı bir ses tercihi varsa **sektör tonunun üzerinde** uygulanır. ⚠️ **Hiyerarşinin uçları kesindir:** en üstte güvenlik ve mevzuat · markaya özgü **yasak kelimeler kullanıcının somut isteğinin üstündedir** · Marka DNA'sı sektör paketinin üstündedir · en altta platform tonu ve kök rehber. ⚠️ **Açık olan yalnız orta basamaktır — K-118:** kullanıcının somut isteği ile markanın **yasak kelime dışındaki** ses/üslup profili çatıştığında hangisinin kazanacağı (Bölüm 4.6); **bu satır o sırayı kapatmaz.**
- Markanın sahip olduğu bilinmeyen bir kanala bağlı çağrı kalıbı kullanılmaz — talimat satırı korunur; ✅ **K-05 KAPANDI — B** (2026-08-21, Ek B): kanal envanteri **Faz 1'de bu işte kurulur**, deterministik filtrenin envantere bağlanma biçimi spec'te tanımlanır.
- Üretilen post kaydı **kullanılan paket sürümüne bağlanır**. ⚠️ **Bağın fiziksel temsili K-07'de açıktır** (ayrı kolonlar mı, mevcut bir JSONB alan mı).
- Üretim akışında kullanıcıya **alt sektörle ilgili soru sorulmaz** — sürtünme yasağı kesindir ve atama akışı üretim hattının dışındadır (Bölüm 9, 10.3).
- Görsel istem çıktısında sektör dağarcığının **bir alt kümesinin** kullanılması, dağarcığın tamamının listelenmemesi ve markanın mevzuat açısından yasaklı dilinin görülmemesi **beklenir**. ⚠️ **Üçü de Katman-2 gözlemidir, otomatik kapı değildir** (Bölüm 13.4); bloğun istemde **bulunup bulunmadığı** ise deterministiktir ve **Katman-1**'e aittir. ⚠️ Bunlar kalite sinyalidir; otomatik red eşiği **K-11 (b)** kapanmadan tanımlanmaz.

**İkinci dal — özel gün seçilmemişse:** Tier 3'ün özel gün bağlamı bloğu **bugünküyle aynı kalır**; yukarıdaki özel gün, tür etiketi ve görsel vurgu satırları **hiç oluşmaz.** Paket bloğu, dağarcık talimatı, görsel dil ve sürüm damgası satırları **değişmez.**

---

### 19.2 Fallback / hata akışı — paket yoluna girmeyen marka

**Given:** Markanın alt sektör alanı **boştur** — ya da doludur ama o alt sektörün **aktif paketi yoktur** (henüz üretilmemiş ya da arşivlenmiş).

**When:** Aynı içerik tipinde üretim yapılır.

**Then:**
- **Bütün yeni bloklar atlanır ve mevcut üretim yolu kullanılır** — Tier 2'de kök `SECTOR_GUIDANCE` **bugünkü metniyle ve bugünkü sırada** yer alır; paket bloğu yoktur.
- Tier 1/2/3 caption parçaları, görsel yönlendiricinin talimat bloğu, kısa video durağan kare isteminin **iki modu**, hareket havuzu ve fikir önerme ucunun istemi — **modele gönderilen mevcut prompt parçaları byte-exact değişmez.** Kanıt **Katman-1**'dir: **değişiklik öncesinde dondurulmuş prompt fixture'ıyla** karşılaştırma; **tek bayt fark = RED** (Bölüm 13.3). ⚠️ **Legacy kısa video yolunun fixture'daki beklenen değeri K-06'ya bağlıdır** — yol düzeltilirse düzeltilmiş davranış, kapsam dışı notlanırsa bugünkü davranış beklenir; **satırın kapsama girmesi koşulsuzdur.**
- Üretilen post kaydında **geçerli bir paket ilişkisi bulunmaz**; ⚠️ **fiziksel temsil K-07'de açıktır** (Bölüm 10.4).
- Kullanıcı yüzeyinde bir fark görülmesi **beklenmez.** ⚠️ **Dürüst sınır:** Katman-1'in güvence verdiği şey **modele gönderilen istem metnidir**, kullanıcı arayüzü davranışı değildir; *"kullanıcı hiçbir yeni hata mesajı almaz"* biçimindeki kesin ifade **ölçülmemiştir** ve bu belgede hüküm yapılmaz.

**İkinci dal — paket okunamıyor:** Paket içeriği bozuksa veya sorgu başarısız olursa **tüm yol mevcut yola düşer**, üretim bloklanmaz ve **kayda bir satır düşer**. ⚠️ Bu dal kaynak katmanında **doğrulanmamıştır** (Bölüm 10.1).

⚠️ **Üçüncü hâl için bu bölümde davranış yazılmamıştır — K-15 (a) açıktır.** *Yalnız bir alanın eksik olduğu* hâlde geri düşüşün tüm yolu mu kapsadığı yoksa yalnız o alanın enjeksiyonunun mu atlandığı, iki dal olarak tarif edilmiş ama **aralarındaki sınır tanımlanmamıştır** (Bölüm 10.1). Sınır tanımlanmadan *Then* satırı yazılamaz.

---

### 19.3 Sınır durumu — özel gün anahtarı eşleşmiyor

**Given:** Paketli markada kullanıcı, sistem takviminde **gün bazlı ayrı satırı** bulunan bir dönem seçmiştir (örneğin bir bayramın numaralı günü); pakette dönemin **üst anahtarı** vardır ama gün bazlı karşılığı yoktur (Bölüm 11.1).

**When:** Üretim başlar.

**Then — davranış K-01b'ye bağlıdır ve bu satır kararı kapatmaz.** ⚠️ **K-01b üç seçeneklidir:** *(A)* slugify öncesi normalize adımı (gün/arife eki kırpma) · *(B)* anahtarların sistem adlarıyla gün bazlı yazılması · *(C)* dar eşleme sözlüğü.
- **Seçeneklerden biri uygulanmışsa:** seçilen ad pakette karşılık bulur — (A)'da kanonik anahtara indirgenerek, (B)'de doğrudan, (C)'de sözlük üzerinden — ve Tier 3'e dönem kalıpları girer. **Üçü de eşleşme sağlayabilir; bu satır aralarında seçim yapmaz.**
- **Hiçbiri uygulanmamışsa:** eşleşme olmaz → **sessiz düşme + kayıt satırı**; Tier 3 bloğu bugünkü gibi davranır. Kayıt zorunluluğu kesindir.
- **Her iki dalda da üretim başarısız olmaz;** fark yalnız içerik zenginliğindedir.
- Eşleşmezlik kayıtlarının birikmesi, anahtar sözleşmesinin eksik uygulandığının **göstergesidir**. ⚠️ **Eşiğe bağlı uyarı üretilmesi bu belgede benimsenmemiştir:** alarm katmanının benimsenmesi (**K-56**) ve sorumlusu (**K-57**) açık karardır (Bölüm 13.6); bu satır onları ne kapatır ne ima eder.

---

### 19.4 Sınır durumu — dönem türü ile takvim kategorisi çelişiyor (sentez anı)

⚠️ **Bu senaryo çalışma zamanında değil, sentez adımında geçer** — 19.1'deki çalışma zamanı çakışmasından ayrıdır: orada iki ton sürücüsü üst üste biner, burada **pakete hangi türün yazılacağı** sorulur.

**Given:** Sentez, bir dönem için ticari fırsat türüne eğilimlidir; **sentez girdisi olarak verilen sistem özel gün listesinde** aynı dönem ulusal kategoriyle görünmektedir.

**When:** Sentez çıktı adımına gelir.

**Then — K-03 politikası uygulanır:**
- **Çatışma algılanır** ve **paketin tür etiketi üstün** kabul edilir (**K-03**, kapalı karar — Bölüm 11.2). Aday paketin dönem türü alanı **paketin araştırılmış değeriyle** doldurulur; şemaya birebir uygunluk korunur.
- **Takvim kategorisi korunur** ve düşürülmez — günün **kimliği** ve paket anahtarının **doğrulanması** için kullanılmaya devam eder (Bölüm 6.2).
- **Çatışma ve uygulanan politika karar günlüğüne yazılır**; kayıt, kararın politikayla verildiğini ayırt edilebilir kılar (Bölüm 6.5).
- **Bu vaka artık açık soru olarak sunulmaz.** ⚠️ **Kapsam dardır:** yalnız tür ↔ kategori çatışması çözülmüştür. Mevzuat çatışması, kapsam tercihi ve motorun karar veremediği öteki maddeler **etkilenmez**; genel bir *"koşuyu blokla"* kuralı kurulmaz ve **K-23 kapanmaz.**
- ⚠️ **Kapanmayan ayak — sözleşme metni.** Yürürlükteki sentez görev sözleşmesi bu çatışmada hâlâ *"kararı VERME — iki tarafı ve eğilimini yazarak açık soruya düşür"* der. Yukarıdaki davranış ancak sözleşme düzeltildiğinde geçerlidir; düzeltme **sürümlü bir supersession** olarak Bölüm 14.4'te kayıtlıdır — **sessiz değişiklik yapılmaz** ve **yeni kullanıcı kararı değildir.**
- ⚠️ **"Operatör kararı verilmeden aktivasyon yapılmaz" biçimindeki kesin ifade bu belgede normatif yapılmaz:** *açık soruların tamamının kapatılmış olmasının* aktivasyon ön koşulu olup olmadığı **açık karardır — K-71** (Bölüm 8.2). ⚠️ **K-03'ün kapanması bu soruyu KAPATMAZ**; yalnız bu vakanın açık soru üretmesini durdurur.
- ⚠️ **Motorlu modeldeki karşılığı da kapandı:** motorun kategori çakışması kontrolü artık *"politika konmuşsa uygulanır"* dalına düşer ve **politika konmuştur** (Bölüm 7.7); bu çatışma için **motor kararsız** sonucu üretilmez.

---

### 19.5 Sınır durumu — sürüm geri alma

**Given:** Bir alt sektörde yeni bir paket sürümü etkinleştirilmiştir; üretimlerde mevzuat hatası fark edilmiştir.

**When:** Yönetici geri alma ister.

**Then:**
- Kötü sürüm **arşivlenir**, ardından önceki iyi sürüm **etkinleştirilir**; **sıra zorunludur** ve ters sıra denenirse **kısmi benzersiz indeks ihlaliyle reddedilir** — veri bozulmaz, hata verir (Bölüm 8.3).
- **Paket sürümleri silinmez; ham kanıt katmanı geri almadan hiç etkilenmez** (salt-ekleme).
- Kötü sürümle üretilmiş postların bulunabilmesi **üretim sürüm damgasına** bağlıdır; damganın gerekliliği kesindir, **veri yeri K-07'de açıktır.**
- ⚠️ **Zaten üretilmiş postların geriye dönük değişmemesi bu belgede hüküm yapılmaz — K-39 açıktır**; hiçbir katmanda geriye dönük yeniden yazma mekanizması tarif edilmemiştir (Bölüm 8.2).
- ⚠️ **Geri almanın tek işlem içinde yürümesi de kesin hüküm değildir — K-102 açıktır** ve aktivasyonun atomikliğinden (**K-101**) **ayrı bir karardır** (Bölüm 8.3).
- **Düzeltme sonraki sürümde yapılır;** kötü sürümün karar günlüğü kanıt olarak durur (arşiv güvencesi Bölüm 8.4).

---

### 19.6 Motorlu turun normal akışı

⚠️ **Bu senaryo ve onu izleyen ikisi hedef modeldir ve yalnız motorlu modelde geçerlidir.** Motorun fazı karara bağlandı: ✅ **K-22 KAPANDI — A** (2026-08-21, Ek B) — motor **Faz 1'de** hattadır, dolayısıyla bu üç senaryo **Faz 1 kapsamındadır**. Motorsuz modelde (K-22 kapanışıyla yürürlük dışı) aşağıdaki akış **oluşmaz** — o modelde aday paketi sentez üretir ve akış doğrudan biçim doğrulayıcısına ve yönetici onayına geçer (Bölüm 7.7).

**Given:** Bir alt sektörün periyodik turunun zamanı gelmiştir. ⚠️ **Periyodun üç ay mı altı ay mı olacağı K-149'da, global mi sektör bazlı mı olacağı K-26'da açıktır.** Alt sektörün aktif bir paket sürümü vardır. Yönetici üç araştırma aracını **elle** koşmuş ve ham raporları üretmiştir (Bölüm 7.2).

**When:** Yönetici sektörü seçer, raporları teslim eder ve turu başlatır. ⚠️ **Turun başlatılacağı yüzey karara bağlandı — ✅ K-27 KAPANDI — A** (2026-08-21, Ek B): Claude Code komut ailesi; **bu satır ayrıca yüzey seçmez.** Koşu klasörü ve teslim sözleşmesi **K-17** kapsamında öneri statüsündedir.

**Then:**
- Mekanik kapı, iki bağımsız kör denetçi ve alan bazlı sentez koşar; **sentez raporu üretilir ve saklanır.** ⚠️ **Nerede saklanacağı açık karardır — K-95** (politika sonucu ve koşu kaydının yeri) **ve K-96** (özgün sentezin, motorun nihai adayının ve gerekçeli farkın ayrı saklanma biçimi; Bölüm 7.2). **Bu belge bir yerleşim seçmez.**
- **Politika motoru koşar:** her karar birimi için sonucu kontrol eder; **kanıtsız çıkarma kararlarını uygulamaz — kalıp korunur** (Bölüm 7.7); daha önce çıkarılmışla eşleşenleri **geri-ekleme çelişkisi** olarak işaretler; boyut tavanını uygular; karar veremediklerini ayırır.
  ⚠️ **Tam karar kapsamı iddiası kalıcı kalıp kimliğine bağlıdır ve o kimlik açık karardır — K-84** (biçimi **K-151**, üretim yöntemi **K-152**; Bölüm 6.3). **Bu satır taraf tutmaz.**
- Aday sürüm **taslak** olarak yazılır; **veri tabanına yalnız taslak yazılması kesin hükümdür.** Karar günlüğü motorun her kararını kanıt satırıyla taşır. ⚠️ **Kararın motor tarafından mı insan tarafından mı verildiğinin ayırt edilebilmesi K-25'te açıktır**; aynı ihtiyacın **koşu seviyesindeki** karşılığı (motorun sürüm ve yapılandırma damgası) **K-97**'dir ve **ikisi ayrı kararlardır** (Bölüm 7.7).
  ⚠️ **Bu satır koşulsuz değildir:** içerik aynıysa yeni sürüm açılmaması ve karşılaştırmanın canonical içerik hash'ine dayandırılması **kesinleşmemiştir**; alternatif modelde her koşu bir sonraki sürüm numarasıyla taslak üretir. **Kaydın yeri K-93'te, canonical üretim kuralı K-92'de açıktır** (Bölüm 6.4, 8.1).
- **Özet fark ve koşu raporu üretilir.** ⚠️ **Koşu raporunun ve politika sonucunun nerede tutulacağı açık karardır — K-95** (Bölüm 7.2). Özet farkta çıkarılanlar **sayı ve eşik üstü olanlar** hâlinde gösterilir; ⚠️ **eşiğin kendisi açık karardır — K-41** ve bu belgede uydurulmamıştır (Bölüm 7.8).
- **Katman-1** (paket yoluna girmeyen markada byte-exact istem karşılaştırması) ve **Katman-2** (kör çıktı örneklemi) koşar. ⚠️ **Katman-2'nin sonucu kapı değildir**; örneklem boyutu **K-11 (a)**'da, geçme eşiği **K-11 (b)**'de açıktır.
- Yönetici **özet farka bakar** ve kalıp kalıp listeyi açmak zorunda kalmaz; onay tek sorunun cevabıdır: *bu sürüm etkinleştirilsin mi?* ⚠️ **Bu yüzeyin motorsuz modeldeki karşılığı aynı değildir** — yürürlükteki sentez sözleşmesi çıkarılanların **tam listesini** onay ekranının ilk bölümü yapar (Bölüm 7.8). ⚠️ **Özet farkın sinyal odaklı tasarlanması bir risk kontrolü önerisidir ve benimsenmesi açık karardır — K-42**; etkisi ölçülmemiştir.
- Onay verilirse önceki sürüm arşivlenir, aday etkinleştirilir. ⚠️ **İki adımın tek işlem içinde yürümesi açık karardır — K-101**; ⚠️ **yetkinin teknik olarak nasıl zorlanacağı ayrıdır — K-103** (Bölüm 8.2); ⚠️ **koşuyu yürüten rol ile aktivasyon yetkisini taşıyan rolün ikiye bölünüp bölünmeyeceği de ayrıdır — K-54** (Bölüm 15).
- **Motor aktif sürüme dokunamaz** — ilke kesindir (**K-28**); açık olan, sınırın **sunucu tarafında nasıl zorlanacağıdır — K-103.**

**Gözlenebilir sonuç — ve sınırı.** Bu modelde yöneticinin tur boyunca verdiği karar sayısının **bir** olması hedeflenir; kalıp düzeyindeki kararlar motor tarafından uygulanmış ve karar günlüğünde izlenebilir olur. ⚠️ **Bu bir hedeftir, ölçüm değildir:** ne tur başına gerçek süre ne de motorun karar kalitesi ölçülmüştür (Bölüm 16.1). ⚠️ **Senaryo, kararsızların sıfır olduğu dalı anlatır;** kararsız çıkan maddelerin akıbeti **K-23**'te açıktır ve 19.7'nin konusudur.

---

### 19.7 Motorun kararsız kalması

**Given:** Sentez, bir çağrı kalıbı için çıkarma öneriyor ama **kanıt alanı boştur.** ⚠️ Tür ↔ kategori çelişkisi **bu senaryonun dalı değildir** — K-03 kapandığı için o çatışma politikayla çözülür (Bölüm 11.2). Senaryo yalnız **kanıtsız karar** üzerinden yürür; motorun kararsız kalabileceği öteki belirsizlik türleri (kanıt yetersizliği, karar kapsamı boşluğu) yerinde durur.

**When:** Politika motoru koşar.

**Then:**
- **Kanıtsız çıkarma uygulanmaz; kalıp korunur** ve koşu raporunda gerekçesiyle görünür. Kanıt kuralı kesindir.
- Kararsız kalan madde **motor kararsız** olarak ayrılır. ⚠️ **Akıbeti K-23'te açıktır ve seçenek üçtür:** *(A)* yöneticiye açık soru olarak düşer · *(B)* güvenli varsayılana düşer — mevcut kalıp korunur ve rapora yazılır · *(C)* **tur durur.** Her iki kaynak katmanının da yazdığı yön mevcut kalıbın korunmasıdır, ama **bu satır seçmez.** ⚠️ **(C) tek maddede turu durdurmaktır; kararsızlık ORANININ turu durdurması ayrı bir karardır (K-132) ve çözülemeyen çatışma kapısıyla (K-128) da karıştırılmaz.**
- ⚠️ **Otomatik çözülemeyen çatışmada koşuyu bloklama kapısı açık karardır — K-128** ve alternatifinde aynı çatışma **açık soruya** düşer (Bölüm 7.7). **İki mekanizma aynı değildir.** ⚠️ Bu, 19.4'ün tür ↔ kategori vakasından **ayrıdır**: orada K-03 kapandığı için çatışma politikayla çözülür ve açık soru üretmez.
- **Sessiz değişiklik oluşmaz** — bu, kanıt kuralının sonucudur. ⚠️ **Buna karşılık koşunun aday taslak üretip üretmeyeceği bu satırda kesinleştirilmez.** Bloklama kapısı benimsenir ve koşu bloklanırsa, bloklanan koşunun **paket satırı üretmeden durumlandırılması kesinleşmemiştir**; alternatif modelde her koşu bir sonraki sürüm numarasıyla taslak üretir. **`değişiklik yok` ve `bloklandı` koşularının nerede kayıtlandığı açık karardır — K-93** (Bölüm 6.4, 8.1) ve **bu bölüm onu kapatmaz.** Kapı benimsenmez ya da koşu bloklanmazsa taslak üretilir; **iki dal da yazılmıştır, biri seçilmemiştir.**
- ⚠️ **Kararsızlık oranı eşiği aşarsa turun durması koşulsuz bir hüküm değildir:** kararsızlık oranı bariyerinin **kurulup kurulmayacağı (K-132)** ve **eşiğin değeri (K-24)** iki ayrı açık karardır (Bölüm 7.7); ⚠️ **bariyer üç durdurma mekanizmasından yalnız biridir** (**K-130** · **K-131** · **K-132**) ve üçü farklı şeyleri ölçer. ⚠️ **Tur durdurulmasının koşu sonucu kümesinde nasıl kaydedileceği de açıktır — K-90** (Bölüm 4.5).
- **Motor hangi sonucu üretirse üretsin aktif sürüme dokunamaz** — ilke kesindir (**K-28**); açık olan, sınırın sunucu tarafında nasıl zorlanacağıdır (**K-103**). ⚠️ **K-28'in kapsamı bundan ibarettir:** *"motor her koşuda taslak üretir"* onun kapsamında **değildir** ve yukarıdaki açık karara (**K-93**) bağlıdır.

---

### 19.8 Motor kural hatasının ölçekte yayılması

**Given:** Motorun bir kuralı hatalıdır (örneğin bir kaynak-eskimişlik bayrağını gereğinden sert yorumlamaktadır) ve tur **birden çok alt sektör** için koşmaktadır.

**When:** Motor bütün paketlerde aynı kuralı uygular.

**Then:**
- Hata **bir pakette değil, kuralın uygulandığı bütün paketlerde** tekrarlanır — insan kararında oluşmayan bir yayılma biçimidir. ⚠️ **Yayılmanın büyüklüğü ölçülmemiştir:** Faz 1 aktif paket tavanı bir **öneridir** (**K-13**) ve tur başına süre ölçülmemiştir (Bölüm 16.1). ⚠️ **Bu öncüller senaryonun bugün kurulamayacağını KANITLAMAZ:** aktarılan son duruma göre aktif paket bulunmadığı için *çok sayıda pakete yayılma* hâli **o duruma göre oluşmaz** — güncel durum doğrulanmamıştır; ayrıca tavanın öneri olması ve sürenin ölçülmemiş olması **ölçek hakkında bir imkânsızlık değil, bir bilinmezlik** kurar.
- Tespit: özet farkta **beklenmedik toplu değişim**, çıkarma sayısı ölçütünde sıçrama, **Katman-2**'de kalite düşüşü. ⚠️ **Üçü de eşiksizdir:** değişim büyüklüğü bariyerinin benimsenmesi (**K-130**), eşik üstü çıkarılanlar eşiği (**K-41**) ve **K-11 (b)** ayrı ayrı açıktır — **bu satır hiçbirini eşiğe çevirmez.**
- Aksiyon: etkilenen paketler **önceki sürümlerine geri alınır** (sürümler durmaktadır, ham katman etkilenmemiştir), kural düzeltilir, tur yeniden koşulur.

  ⚠️ **Mekanizma sınırı — kayda geçirilir, yeni yükümlülük türetilmez.** Bölüm 8.3'ün geri alma prosedürü **tek paket sürümü** için yazılmıştır; **birden çok paketi tek işlemde geri alan ayrı bir mekanizma hiçbir katmanda tarif edilmemiştir.** Aksiyon, aynı prosedürün **etkilenen her pakete ayrı ayrı** uygulanmasıdır.

  ✅ **Müdahalenin KAPSAMI ayrı bir sorudur ve KAPANDI — K-145: vaka bazında geri alma, güvenli varsayılanla.** Üç kural birlikte işler: *(a)* **etkisi kanıtlanan paketler geri alınır** · *(b)* **etki alanı güvenilir biçimde ayrılamıyorsa, kuralın uygulandığı bütün paketler etkilenmiş kabul edilir ve geri alınır** · *(c)* **etkilenmediği kanıtlanan paketler gereksiz yere geri alınmaz.** ⚠️ **Belirsizlik güvenli tarafa düşer:** ayrım yapılamadığı anda davranış koşulsuz toplu geri almayla **aynıdır**; fark, ayrımın yapılabildiği durumlarda operasyon yükünün düşmesidir. ⚠️ **Kararın *"etkisi kanıtlanan"* ve *"güvenilir biçimde ayrılabilen"* ölçütleri hiçbir katmanda tanımlı değildir ve bu belgede uydurulmamıştır** — ölçüt tanımı **teknik bir kabul sözleşmesidir**, evi olay müdahalesi yordamıdır (Bölüm 14.5) ve **kullanıcı kararına çevrilmez.**
- ⚠️ **Kuru mod bu senaryonun gerekçesi olarak yazılmıştır** — motorun kararlarını uygulamadan önce raporlaması. **Yeni bir koşu kipidir ve zorunlu olup olmadığı K-22'den ayrı bir açık karardır — K-133** (Bölüm 7.7).

---

## 20. Spec hazırlık kontrol listesi

[ZORUNLU]

> **İşaret anlamı:** `[x]` karşılanıyor · `[~]` kısmen karşılanıyor, sınırı satırda yazılı · `[ ]` karşılanmıyor.
> **Sayıların kapsamı:** ölçümler **2026-08-19** taramasındandır; etiket sayımları **bu bölüm ile Bölüm 21'in kaynak tanımı satırı hariç** alınmıştır. Karar evreni değiştikçe yeniden ölçülmelidir.

### Amaç ve kapsam

- [x] **Problem ve hedef kullanıcı açık.** İki problem ayrı yazılıdır ve **statüleri farklıdır**: sektörel ayrışmama bir **mevcut sistem olgusudur**, bakım yükü ise **hedef işletim modelinin** riskidir (Bölüm 2.1). Sorun yaşayan roller adlandırılmıştır (Bölüm 2.1, 15).
- [~] **Kapsam içi ve dışı maddeler yazılı.** Bölüm 3.2'de **10 kapsam-dışı madde** vardır; **dokuzunda** yeniden ele alma koşulu veya adlandırılmış ev yazılıdır. ⚠️ **Bakım borçları maddesinin ikisi de yoktur:** madde bunu açıkça yazar — *"koşul uydurulmamıştır"* — ve kapsam kararını Bölüm 17'ye taşır; fakat **Bölüm 17'ye taşınmak zamanlanmış bir uygulama evi yaratmaz.**
- [~] **Başarı ölçütleri ve kabul eşikleri ölçülebilir.** **Prompt düzeyi kapı** (Katman-1, byte-exact) deterministiktir ve bugün ölçülebilir. **Çıktı kalitesi değerlendirmesi (Katman-2) bir kapı değildir** — sonucu kalite sinyalidir (Bölüm 13.4). Sayısal eşiğin konulup konulmayacağı **K-11 (b)**'de, örneklem boyutu **K-11 (a)**'da, gözlemlenebilirlik alarm eşikleri Bölüm 13.6'da açıktır. ⚠️ Bu **bilinçli bir boşluktur** — eşik uydurmak ölçülmemiş sayı iddiasıdır.
- [x] **Varsayımlar ile doğrulanmış gerçekler ayrılmış.** Ayrım claim düzeyindedir ve **129 statü etiketiyle** taşınır: aktarım 67 · varsayım 10 · ölçülmemiş 26 · bu sentezde doğrulanmamış 26. ⚠️ Hiçbir kod/DB hükmüne topluca doğrulanmış statüsü verilmemiştir; canlı kod ve veri tabanı **bu sentezde taranmamıştır**.

### Mimari ve veri

- [x] **Etkilenen bileşenler ve entegrasyonlar listeli.** Bölüm 5'te dört tabloda **36 kayıt**; ilişkili sistemler Bölüm 12'de yedi alt başlıkta.
- [~] **Veri sahipliği ve doğruluk kaynağı belli.** Bölüm 12'de **12 kayıtlık** sahiplik tablosu vardır ve çakışmalar sayılmıştır. ⚠️ **İki sahiplik ayağı açık karardır:** regresyon altyapısının paylaşımının bağlayıcı olup olmayacağı **K-20**'de, paket sürüm damgasının veri yeri **K-07**'de.
- [~] **Yaşam döngüsü, fallback ve rollback davranışı tanımlı.** Yaşam döngüsü Bölüm 8'de yazılıdır; geri alma davranışı on ayrı yerde ele alınır. **Paketin bulunmadığı** hâlde emniyetli geri düşüş kapanmış hükümdür. ⚠️ **Bozuk veya eksik paket içeriğinde çalışma zamanı davranışı K-15 (a)'da açıktır** ve tarif edilen iki dalın sınırı tanımsızdır.
- [~] **Geriye uyumluluk beklentisi açık.** Beklenti kesindir ve **kanıt yöntemi tanımlıdır**: paket yoluna girmeyen üretimde modele giden prompt parçaları **byte-exact** değişmez; ölçüldüğü yer **Katman-1** prompt kapısıdır (Bölüm 4, 13.3). ⚠️ **Legacy kısa video yolunun düzeltilmesi mi yoksa açıkça kapsam dışı notlanması mı gerektiği K-06'da açıktır** — yol sessiz bırakılamaz.

### İşletim ve kalite

- [~] **Roller, onaylar ve operasyon sahibi belli.** Bölüm 15'te iki tabloda **25 kayıt**; teknik onay ile ürün onayı ayrılmıştır. ⚠️ **İki ayak açıktır:** teknik sahip rolünün ikiye bölünüp bölünmeyeceği ve **kabul yetkisinin kimde olduğu** — ikincisi yalnız bir hakemde ele alınmıştır.
- [~] **Test/kalite kapıları ve gözlemlenebilirlik tanımlı.** Bölüm 13'te **dokuz başlık** (yedi numaralı alt bölüm + iki alt ayrım); iki doğrulama katmanı ve aralarındaki sınır yazılıdır. ⚠️ Katman-1 deterministiktir; **Katman-2 otomatik kapı değildir** ve sayısal eşikleri yukarıda sayılan kararlarda açıktır.
- [~] **Risklerin kontrolleri ve sahipleri var.** Bölüm 18'de **35 risk kaydı** vardır; her birinin kontrolü ve tetikleyicisi yazılıdır. ⚠️ **Sahip 27'sinde atanmıştır; 8'inde `[AÇIK]`'tır** (**R-25 · R-29 · R-30 · R-31 · R-32 · R-33 · R-34 · R-35**).
- [x] **Pilot veya rollout yaklaşımı gerekliyse tanımlı.** Bölüm 16'da pilot yaklaşımı yazılıdır; pilotun **kapsamadığı** varyasyonlar da açıkça sayılmıştır.

### Açık kararlar

- [~] **Spec'i bloklayan kararların sahibi ve son tarihi var.** **Sahip: var** — 162 kararın 158'inde sahip yazılıdır (kalan dördü kapanmış kararlardır). ⚠️ **Son tarih: büyük ölçüde yok** — belgenin **162 kararının 131'inin** son tarihi `[TANIMSIZ]`'dir.
- [~] **Çözülmemiş konular *"sonraya"* denilerek sahipsiz bırakılmadı.** **Sahipsiz bırakılan karar yoktur** ve kapsam-dışı maddelerin dokuzunda ev veya koşul yazılıdır. ⚠️ Ancak **tarihsizlik sahipsizlikle aynı şey değildir**: 131 kararın ne zaman kapatılacağı yazılı değildir — sahibi belli, **ödeme planı belli olmayan** bir borç yığınıdır.
- [x] **Teknik ayrıntılar kullanıcı onayına bırakılmak yerine spec/review/test ile doğrulanacak şekilde ayrıldı.** Bölüm 17 bunu **beş sınıflı bir sözleşmeyle** yapar: `Spec öncesi kullanıcı kararı` **47** · `Koşullu` **47** · `Spec içinde teknik olarak çözülür` **35** · `Bloklamaz` **32** · `Ölçülmedi` **1**. ⚠️ **Bu sınıflar kararı kimin çözeceğini söyler, hangi spec'in bloklandığını değil** — blok kapsamı ayrı bir eksendir ve aşağıda ele alınır.

**Spec'e geçiş kararı:** **Spec yazımı başlayabilir; Bölüm 17'deki ürün kararları ilgili sözleşme kesinleşmeden kapatılmalıdır.**

**Gerekçe:** Belgenin mimari gövdesi yazılmıştır: bileşenler, veri sahipliği, roller, riskler, doğrulama katmanları ve pilot yaklaşımı yerindedir. Spec, açık kararları çözmeden yazılabilir: ürün kararı gerektiren her nokta **Bölüm 17 K-ID atfıyla** işaretlenir ve karar uydurulmaz. Önceki hüküm (*"koşullu hazır — beş kullanıcı kararıyla"*) hangi kararın hangi kapsamı blokladığının sayımına dayanıyordu; sayımın kaynağı olan blok kapsam matrisi **tamamlanmamıştır** ve hüküm **kullanıcı kararıyla geri çekilmiştir** (2026-08-19 oturum kapanışı; Ek B).

⚠️ **Blok kapsamı sınıflandırması bu sentezin ölçüm katmanıdır**, Bölüm 17 tablosunda sütun olarak taşınmaz ve **tamamlanmamıştır**; kullanıcı kararıyla (2026-08-19) spec'e geçişin kritik yolundan çıkarılmıştır. **Blok sayısına dayanan bir hüküm yazılması gerekirse önce ölçülür.** Her kararın kendi metni ve `Spec'i bloklar mı?` sınıfı Bölüm 17'dedir.

⚠️ **Kalan yapısal boşluklar hükmü değiştirmez ama seansın gündemidir:** çıktı kalitesi değerlendirmesinin eşiği (**K-11 (b)**), bozuk veya eksik paket içeriğinde çalışma zamanı davranışı (**K-15 (a)**) ve legacy yolun akıbeti (**K-06**). Üçü ayrı türdendir — biri eşik, biri çalışma zamanı davranışı, biri kapsam kararıdır.

---

## 21. Kaynak belgeler ve referanslar

[ZORUNLU]

*"Kanonik"*, *"v1.1"*, *"olgusal iddialarının tamamı doğru"*, *"ESKİDİ"* — hepsi statü **iddiasıdır** ve iddianın kime ait olduğu cümlenin içinde taşınır.

#### Bu bölümün okunma kuralları — üç sınır

1. ⚠️ **Bu tablo bir kaynak kaydıdır, doğrulama kaydı değildir.** Bir dosyanın burada listelenmesi içeriğinin doğrulandığı anlamına gelmez. **Canlı kod ve veri tabanı bu sentezde taranmamıştır** (Bölüm 2.1); bütün kod/DB referansları 2026-07-11 taramasından aktarımdır ve spec seansında **taze koşum gerektirir**.
2. ⚠️ **Statünün sahibi cümlenin içinde taşınır.** Aşağıdaki güven/güncellik notlarının bir bölümü **bu sentezde kaynak dosyaların kendisine karşı denetlendi** ve o satırlarda ✅ ile işaretlidir; denetlenmemiş olanlar hakem beyanı olarak kaynak atfıyla durur.
3. ⚠️ **Girdi kümesi ile klasör aynı şey değildir.** Bu sentezin girdi kümesi **dokuz kaynak dosya + iki hakem belgesidir**. Klasörde bunların dışında da kaynak niteliğinde artefaktlar bulunmaktadır ve **hiçbir katman onları kaynak olarak kaydetmemiştir**; 21.4 bu boşluğu kayda geçirir.

---

### Kaynak tablosu

| Kaynak | Tür | Bu girdideki rolü | Güven/güncellik notu |
|---|---|---|---|
| `sektor-paket-mimari-karar-dokumani.md` | Karar dokümanı | **Ana omurga** — veri modeli, enjeksiyon hattı, süreç, **yedi kaynak karar maddesi**, riskler ve başarı kapıları *(iki hakem ortak)* | **Durum: ÖNERİ — kesinleşmiş uygulama kararı değildir.** ✅ **Bu sentezde dosyanın kendisine karşı doğrulandı** (başlık satırı 4). Tasarım 2026-07-07, kod/DB doğrulaması 2026-07-11. Bir hakem *"4 iddiası yanlış çıkıp düzeltilmiş"* der — **bu beyan bu sentezde denetlenmedi** `[BU SENTEZDE DOĞRULANMADI]` |
| `marka-dna-mimari-karar-dokumani.md` | Karar dokümanı | Kesişim katmanı — marka–sektör bilgi sınırı, hiyerarşi, kontrast, ortak regresyon altyapısı; **K-05'in evi**. ⚠️ 21.1'in **üç çıpası yalnız bu dosyadan** gelir | **Durum: ÖNERİ — kesinleşmiş uygulama kararı değildir.** ✅ **Bu sentezde doğrulandı** (başlık satırı 4). ⚠️ **İki hakem de bu statüyü taşımaz** — biri yalnız *"olgusal iddialarının tamamı doğru çıkmış"* der; o ifade de **dokümanın kendi başlık beyanıdır** (*"keşif iddialarının TAMAMI doğru çıktı"*), bağımsız doğrulama değildir |
| `_SABLON.md` | Görev şablonu | Araştırma girdi sözleşmesi — GÖREV A / GÖREV B; **biçim kuralları** ve mekanik tarama sözleşmesi (Bölüm 7.1, 7.3) | ⚠️ **"Kanonik" nitelemesi dosyanın kendi beyanı DEĞİLDİR** — ana karar dokümanının atamasıdır (*"kanonik olan `_SABLON.md`"*) ✅ bu sentezde doğrulandı; dosya kendini yalnız *"genel şablon"* diye tanıtır. ⚠️ **Tarih damgası GÜVENİLMEZDİR — 21.5'te ölçüldü:** dosya *"Son güncelleme: 2026-07-07"* der, ama **2026-07-11 değişikliğini içerdiği ölçülmüştür** |
| `hakem-denetci-gorevi.md` | Görev sözleşmesi | İki bağımsız denetçinin görev ve çıktı sözleşmesi (Bölüm 7.4) | **Sürüm 1.1 — 2026-07-11** ✅ **dosyanın kendi 8. satırında yazılı; bu sentezde doğrulandı.** ⚠️ Bir hakem sürümü olgu olarak verir, diğeri **revizyon ihtiyacı** tespit eder: yeni sürümde **çıktı sözleşmesi ve aktif paket eki** tanımlanmalıdır. İki ifade çelişmez — biri bugünkü sürümü, diğeri gereken sonraki sürümü söyler; **revizyon açık iştir** ve bu bölümde kapatılmaz |
| `hakem-sentez-gorevi.md` | Görev sözleşmesi | Alan bazlı evrimsel sentez ve `draft` üretim sözleşmesi (Bölüm 7.5, 7.6, 7.8) | **Sürüm 1.2 — 2026-07-11** ✅ **dosyanın kendi 9. satırında yazılı; bu sentezde doğrulandı.** ⚠️ Bu sözleşmenin *"kararı VERME"* hükmü **K-03 kararıyla dar kapsamda düzeltilecektir** — düzeltme sürümlü supersession ile yapılır ve **henüz uygulanmamıştır** (Bölüm 14.4) |
| `kuyumculuk.md` | Doldurulmuş brief | Pilot sektör bloğu; **"yalnız GÖREV B" modunun örneği** *(iki hakem ortak)* | **DONMUŞ; kanonik DEĞİL — kanonik olan `_SABLON.md`'dir** ✅ kaynağa karşı doğrulandı. Oluşturma **2026-07-07** ✅ dosyanın kendi başlığında. ⚠️ **"Eski sürümden türetilmiştir" iddiası artık BEYAN DEĞİL, ÖLÇÜMDÜR — 21.5.** ⚠️ **Kaynak, üç brief türevini birlikte hem dondurur hem K-18 kapsamında yeniden üretime bağlar** (`otomaix.md` · `marka-patent.md` · `kuyumculuk.md`); iki hakem yalnız üçüncüsünü kaynak sayar — bkz. **21.4** |
| `Kaynak-1.md` · `Kaynak-2.md` · `Kaynak-3.md` | Ham araştırma çıktısı | Hakem hattının **gerçek girdisi**; paket içeriğinin ham malzemesi. Kör adlandırılmıştır — hangi raporun hangi araca ait olduğu **yalnız operatörde** | **ESKİDİ** — ⚠️ **hakem beyanı türetilmiş bir yargıydı; bu sentezde ÖLÇÜLDÜ ve doğrulandı** (21.5). ⚠️ **Tarih damgası ölçümü ikiye ayrılır:** `Kaynak-1.md` ve `Kaynak-3.md` **hiçbir tarih taşımaz** (dört ayrı tarih deseni, **0 isabet**) — eskilikleri yalnız **biçimden** okunur; `Kaynak-2.md` kendi başlığında **"6 Temmuz 2026"** taşır ve bu **kanonik şablonun 2026-07-11 güncellemesinden öncedir.** Üçü de yalnız GÖREV A içerir; yeniden üretimleri **K-18**'e bağlıdır |
| Canlı kod + veri tabanı (**2026-07-11 taraması**) | Kod / veri | Bütün `[AKT·…]` etiketlerinin ve 21.1'deki çıpaların **tek kaynağı** | ⚠️ **Bu sentezde yeniden taranmadı** (Bölüm 2.1 md.2). İki hakem de taze taramamıştır; biri iddiaları etiketler, diğeri etiketsiz düz hüküm yazar. **Spec seansında taze koşum şarttır** — akıbet ⑤ |
| **2026-08-11 kullanıcı analizi** `[SEA-2026-08-11]` | Analiz oturumu | **Politika motoru · `pattern_id` · `no_change` · değişim bariyeri · yöneticinin yalnız koşu sonucuna verdiği son onay** — mimarinin en büyük eklentisi | ⚠️ **Dokuz kaynak dosyanın hiçbirinde yer almaz — bu sentezde ölçüldü ve doğrulandı** (aşağıda). ⚠️ **İki hakemdeki içerik AYNI DEĞİLDİR:** işaret sayısı **24 ↔ 22** (taze sayım) ve kapsamları ayrışır; tek bir sabit içerikli kaynak gibi kullanılamaz. ⚠️ **Birincil artefaktı kayıtsızdır — 21.4** |

### 21.1 Mevcut kod ve sistem referansları

> ⚠️ **Aşağıdaki konumların tamamı 2026-07-11 taramasından aktarımdır** `[AKT·KAYNAK · 2026-07-11]` **ve bu sentezde canlı koda karşı yeniden doğrulanmamıştır.** Doğrulanan tek şey **kaynak katmanında bulundukları**dır; satırların bugünkü kodda hâlâ aynı yerde olup olmadığı **bilinmemektedir.** Kod bu tarihten sonra değiştiyse çıpalar kayar — spec seansının ilk işi budur.

**Ana karar dokümanından gelen çıpalar** (`sektor-paket-mimari-karar-dokumani.md` — 27 kalemin 24'ü):

- `prompt_builder.build_brand_context` **232–235** — Tier 2 sektör rehberi çıpası; **paket bloğunun gireceği yer** (Bölüm 5.2'de enjektör olarak kayıtlı).
- `prompt_builder._SPECIAL_DAY_TONE_HINTS` — kategori→ton mekanizması; **K-03'ün diğer tarafı** (karar kapandı, Ek B).
- `caption_generator._build_output_format_instruction` **353–359** — `image_prompt` katı kurallar bloğu.
- `short_video.py` **128–129** — `Industry: {sector}` satırı; **187–204** ürün referanslı image-edit modu; **206–231** metinden görsele modu; **263–277** `_MOTION_PROMPTS` — **K-02'ye bağlıdır.**
- `ai.py` **26–89** — `POST /ai/analyze-website`, JSON sözleşmesi `{name, description, sector, colors, tonality}`; **275–277** — `/ai/suggest-ideas`, sektör rehberinin ikinci tüketicisi.
- `posts.py` **846–847** — legacy `/posts/generate-short-video`; rehberi slug yerine görünen adla arıyor → **bugün hep boş dönüyor** (sessiz hata). Akıbeti **K-06**'da açıktır.
- `sector_resolver.py` **59** — slug haritası **tüm** satırları alıyor, kök filtresi yok → **R-01**'in kaynağı.
- `sectors.py` **27–33** — `GET /sectors`, bugün filtresiz.
- `layer_a.py` **263** — trend Layer A, `WHERE parent_sector_id IS NULL` — alt sektörlere **zaten bağışık.**
- `main.py _validate_templates` — açılışta `status == "active"` zorluyor (legacy şablon borcunun parçası).
- Ön yüz tüketicileri: `onboarding/page.tsx:129` · `markalar/page.tsx:56` · `marka-ayarlari/page.tsx:434`.
- Tablolar: `social.sectors` (12 kök satır) · `social.public_holidays` (2026, 22 kayıt) · `social.sector_reports` · `social.sector_trend_cache` (⚠️ ad karışıklığı uyarısı) · `brands` (2 kayıt).

**Yalnız marka-DNA karar dokümanından gelen çıpalar** — ⚠️ **kaynak ayrımını bu sentez yaptı; iki hakem de yapmaz:**

- `prompt_builder` **185–254** — blok sırası: marka bilgisi → ton → renkler → hashtag'ler → sektör rehberi/paketi → şablon talimatı.
- `prompt_builder` **111–113** — `_SYSTEM_RULES`, *"marka tonu kazanır"* kuralı; **hiyerarşi genişletmesinin yeri.**
- `schemas.py` **37–46** (`BrandKitUpdate`) ve **54** (`BrandUpdate.brand_kit`) — marka DNA işinin bulgusu; **bu işte doğrudan kullanılmıyor**, kesişim kaydı olarak taşınır.

---

### 21.2 Ürün ve araştırma kaynakları

Aşağıdaki dosya-başı nitelemeler **tek hakemin değerlendirmesidir**; bu sentezde **dosyaların kendisine karşı ölçülenler** ✅ ile işaretlenmiştir.

**`Kaynak-2.md` — en Türkiye-yerel ve mevzuat açısından en güçlü dosya.** ✅ **Somut iddiaları bu sentezde dosyaya karşı doğrulandı:** Atasay **550.059 TL** Reklam Kurulu cezası (**3 isabet**), **12.11.2024** tarihi, **351** sayılı karar, Ahlatcı durdurma (**3**), **SPK 6362 md.109/2**, indirim öncesi fiyat penceresinin **30 → 10 gün**e inmesi (**33297** sayılı RG, **01.07.2026**; yürürlük **1 Ağustos 2026**). Kültürel derinlik de dosyada: **taklas** (4) · **gremse** (4) · **Trabzon hasırı** (2) · **kulplu** çeyrek (3) · **altın günü** (6). **K-05'in doğduğu satır burada:** *"[Ürün] gramaj/fiyatını WhatsApp'tan sor"* (`whatsapp` 5 · `gramaj` 5 isabet). ⚠️ **Doğrulanan şey iddiaların DOSYADA bulunmasıdır, dış dünyada doğru olmaları değildir** — mevzuat iddiaları **bu sentezde** birincil kaynağa karşı denetlenmemiştir `[BU SENTEZDE DOĞRULANMADI]`. ⚠️ **Ve "hiçbir katmanda denetlenmedi" denemez:** dosyanın kendi **Bölüm C güven notu** mevzuat alanını *"en güçlü ve en güncel alan … doğrulandı"* sayar. **Bu araştırma aracının kendi öz-değerlendirmesidir**, bağımsız denetim değildir — ve hakem hattının denetleyeceği iddianın ta kendisidir.

**`Kaynak-3.md` — farklı mevzuat açısı:** sentetik taş beyanı zorunluluğu (`sentetik` **4**), birim fiyat ve işçilik dahil görünürlüğü (`birim fiyat` **2** · `işçilik` **8**).

**`Kaynak-1.md` — en zayıf kaynak tabanı.** ✅ **Üç brief ihlali de bu sentezde ölçüldü:** *(a)* **gövdede dipnot** — cümle sonuna bitişik rakam işaretçisi, **14 isabet**; aynı desen Kaynak-2 ve Kaynak-3'te **0**; *(b)* `gorsel_kodlar` alanı **paragraf içinde virgülle** yazılmış ve içinde **fiziksel çekim parametresi** var (`4500K-5500K` — **1 isabet**, diğer iki dosyada 0); *(c)* **kendi yasaklar alanıyla çelişen aciliyet CTA'sı** (*"Sınırlı Stok + İndirim Fiyatı + Hızlı Sipariş … aciliyet hissiyle dönüşümü hızlandırır"*). ⚠️ **Bir alt-iddia daraltıldı:** hakem bunu *"aciliyet/kıtlık CTA'sı"* diye yazar; `kıtlık` dosyada **0 isabet**tir — ölçülen ihlal **aciliyet** eksenindedir, kıtlık ekseni **kanıtlanmamıştır.**

⚠️ **Üç ihlalin üçü de AYNI sözleşme maddesinden doğar — ölçüldü.** `_SABLON.md`'nin **BİÇİM KURALLARI** bölümü (satır 162 ve sonrası) hem *"her kalıp AYRI madde işareti olsun — paragraf içinde virgülle birleştirme (adet sayımı bozulur)"* der, hem de *"rapor gövdesinde dipnot/atıf işareti kullanma (üst simge rakam, `[1]`, `citeturn` vb.)"* der. **Kaynak-1'in (a) ve (b) ihlalleri ile Kaynak-3'ün `citeturn` kullanımı bu tek maddenin üç ayrı biçimidir.** ⚠️ **Ve ihlal olmalarının sebebi özensizlik değildir:** ana karar dokümanı *"[EK 2026-07-11] şablonun **yeni** BİÇİM KURALLARI bölümü de mekanik kontrole"* der — **kural, üç ham dosya üretildikten sonra yürürlüğe girmiştir.** İhlaller bu yüzden **eskiliğin kanıtıdır**, kalitenin değil.

⚠️ **Atıf biçimi ihlalinin dağılımı tek dosyaya özgüdür:** üç ham dosya içinde **yalnız Kaynak-3** `cite`+**U+E202**+`turn…` işaretçisini kullanır — **38 isabet**, diğer ikisinde **0**.

**Üçünün ortak zayıflığı — kendi güven notlarında yazılıdır.** ✅ Üç dosyanın üçünde de **`Bölüm C — Güven notu`** başlığı vardır (her birinde 1 isabet); hakem değerlendirmesi bu bölümlere dayanır: **CTA ve kanca kalıpları doğrudan kaynaklı değildir, soyutlamadır** → sentezde bu iki alanın kanıt ağırlığı **en düşüktür**. Görsel ve video kodları büyük ölçüde global rehberlerden gelir → hakem hattında **`[yerel-değil]` bayrağı beklenmelidir.** ⚠️ **Bu bir beklentidir, ölçülmüş bir sonuç değildir** `[ÖLÇÜLMEMİŞ VARSAYIM]` — resmî hakem turu koşulmamıştır (Bölüm 16.1) ve bayrak dağılımı hiçbir katmanda ölçülmemiştir. ⚠️ **Ve bir kalite sinyali otomatik red eşiğine çevrilmez:** bayrak yoğunluğu **Katman-2** gözlemidir; otomatik red eşiği **K-11 (b)** kapanmadan tanımlanmaz (Bölüm 13).

---

### 21.3 İlgili kararlar, ticket'lar ve önceki çalışmalar

| Kalem |
|---|
| **A′ kararı** — ayrı alt-sektör tablosu kurulmaz; hiyerarşi `sectors` içinde taşınır |
| **C kararı** — marka → alt-sektör ataması: **LLM önerir, kullanıcı teyit eder** |
| **A′ hakem mimarisi** — çift bağımsız denetçi + yapılandırılmış çıktı + **alan bazlı parçalı sentez** |
| **B süreci** — yarı otomatik araştırma/hakemlik hattı; tam otomatik **C süreci** Faz 2'ye bırakılmıştır |
| **marketingskills entegrasyonu** — beş psikoloji prensibi listeyi tamamlama refleksiyle **uydurma üretti**, üçe indirildi |
| **Gayriresmî ön hakem turu** — claude.ai oturumunda (Claude + ChatGPT) koşulmuş |
| **2026-07-11 kod/DB taraması** — aktarım etiketlerinin kaynağı |

⚠️ **Kaynağın yedi karar maddesi iki farklı kanıt tabanından doğar ve bu ayrım taşınır.** **İlk üçü** (sentezdeki karşılıkları **K-01a/K-01b** · **K-02** · **K-03**) **kod/DB gözleminden**; **son dördü** (**K-04** · **K-05** · **işlevsel kapı protokolü — Katman-1 / Katman-2** · **K-07**) aynı gün yapılan **tasarım analizinden** doğar. **İkisi aynı statüde değildir.**

---

### 21.4 Kayda geçirilmemiş kaynak artefaktları — bu bölümde görünür kılındı

⚠️ **Aşağıdaki kalemlerin hiçbiri, hiçbir katmanın KAYNAK TABLOSUNA girmemiştir** — iki hakem belgesi ve bu belgenin önceki 2834 satırı. *(Ayrı bir şey: ilk kalem ana karar dokümanında **anılır**; anılmak kaynak olarak kaydedilmek değildir.)* Kayda geçirilmeleri **yeni bir hüküm kurmaz**; girdi kümesi ile klasörün farkını görünür kılar.

**1. `otomaix.md` ve `marka-patent.md` — iki donmuş brief türevi.** İkisi de `_SABLON.md`'den türetilmiş, **2026-07-07** tarihli doldurulmuş brief örnekleridir ✅ (dosyaların kendi başlıklarında). Bir hakem ikisini yalnız bir **dosya ağacı** çiziminde anar (*"donmuş örnek türev"*), diğeri hiç anmaz; **ikisi de kaynak tablosuna almaz.** Eksik olan **kayıt**tır.

✅ **Akıbetleri ise kaynakta AÇIKÇA ÇÖZÜLMÜŞTÜR ve iki ayrı hükümle taşınır.** *(i)* Türetme kuralı: örnekler bilinçli olarak **dondurulmuştur**, **kanonik olan `_SABLON.md`'dir**, yeni türetmeler güncel şablondan yapılır. *(ii)* **K-18 kararının kendisi üçünü de ADIYLA sayar:** *"mevcut brief'ler (**otomaix / marka-patent / kuyumculuk**) ve Kaynak-1/2/3 çıktıları **ESKİDİ**; yeniden üretim bilinçli olarak spec + uygulama sonrasına, resmî hakem turundan hemen öncesine ertelendi … eski dosyalar **SİLİNMEZ**."*

**2. `claude-codex-sektör-bilgi-paketi-okuma.html` — `[SEA-2026-08-11]` katmanının kayıtsız birincil artefaktı.** Klasörde **3 684 076 baytlık** bir HTML dosyası bulunmaktadır; başlığı *"Claude / Codex — Sektör Bilgi Paketi Mimarisi"*tir ve terim profili `[SEA-2026-08-11]` katmanıyla örtüşür: `politika motoru` **83** · `2026-08-11` **80** · `otomaix` **50** · `pattern_id` **17** · `no_change` **16** isabet. ⚠️ **İçeriği bu sentezde OKUNMAMIŞ ve DOĞRULANMAMIŞTIR** `[BU SENTEZDE DOĞRULANMADI]`; yukarıdakiler yalnız terim sayımıdır ve dosyanın ne olduğunu **kanıtlamaz** — yalnız `[SEA-2026-08-11]` katmanıyla **uyumlu** olduğunu gösterir. ⚠️ **Hiçbir katman ona atıf yapmaz:** iki hakemde, iki karar dokümanında ve bu belgenin 2834 satırında `.html` deseni **0 isabet**.

⚠️ **Sonuç bir izlenebilirlik boşluğudur ve kapsam/risk seviyesindedir:** mimarinin **en büyük eklentisi** — politika motoru, `no_change`, değişim bariyeri ve yöneticinin yalnız koşu sonucuna verdiği son onay — dokuz kaynak dosyanın **hiçbirinde bulunmaz** (yukarıda ölçüldü) ve iki hakem belgesindeki kaydı **birbiriyle aynı değildir** (24 ↔ 22 işaret). **Bu katmanın dayandırılabileceği tek artefakt kayıtsızdır.** Karar **kullanıcı seviyesindedir**, çünkü tartılan şey teknik doğruluk değil, **maliyet ile izlenebilirlik riskidir:** artefakt kanonik kaynak olarak kayda alınıp içeriği denetlensin mi, yoksa `[SEA-2026-08-11]` katmanı **iki hakem belgesindeki hâliyle yeterli** sayılıp artefakt kayıtsız mı kalsın? ⚠️ **Bu bölümde kapatılmamıştır** ve **Bölüm 17'de ele alınacaktır; karar ID'si Bölüm 17 sweep'inde verilecektir** (Bölüm 2.9). Bu belge **hiçbir yönü varsaymaz** ve artefaktın içeriğinden **hiçbir hüküm türetmez**.

⚠️ **Bağımlılık:** bu kalemin ağırlığı **K-22**'ye bağlıydı ve karar ağır dalı seçti — motor **Faz 1'de** olduğundan (✅ **K-22 KAPANDI — A**, Ek B) mimarinin en büyük eklentisi **kayıtsız bir artefakta** dayanıyor olur; kalem **Faz 1 spec'i için kritiktir** (motor sonraya kalsaydı motor spec'ine kadar kritik olmazdı).

**3. Kaynak statülerinin yeniden doğrulanması — sahibi ve zamanı yazılı değildir.** Bu bölüm statülerin bir bölümünü **dosyaların kendisine karşı** denetledi (yukarıda ✅ ile işaretli olanlar). ⚠️ **Denetlenmeyenler kaldı:** *"4 iddiası yanlış çıkıp düzeltilmiş"* · *"olgusal iddiaların tamamı doğru çıkmış"* · **2026-07-11 kod/DB taramasının kendisi.** İlk ikisi belge beyanıdır ve birincil kanıtları bu klasörde bulunmamaktadır; üçüncüsü **akıbet ⑤**'tir ve spec seansına bağlıdır (Bölüm 2.1 md.2). **Teknik iş kalemidir**, yeni karar değildir; evi **Ek C "bilinen eksik kanıtlar"**dır.

---

### 21.5 Ölçülen tarih ve sürüm kayıtları — iki tutarsızlık, bir statü yükseltmesi

⚠️ **Bir belge-içi tutarsızlık kayda geçirilir ve ölçüm onu genişletti.** Bir hakem belgesi başlığında *"aşağıdaki **sekiz** dökümanın okunmasıyla"* der, hemen ardından **dokuz** dosya listeler; aynı belgenin karar günlüğü de *"**Sekiz** dökümanın damıtılması"* yazar — **iki geçiş** (taze ölçüm; envanter kaydı yalnız birincisini taşıyordu). Diğer hakem **dokuz** sayar. **Bu sentezde dokuz kullanılmıştır**; içerik etkisi yoktur ve **kaynak seçimini değiştirmemiştir**.

⚠️ **İkinci tutarsızlık KAYNAK katmanındadır ve pratik sonucu vardır.** `_SABLON.md` kendi başlığında *"Son güncelleme: **2026-07-07**"* der. Ana karar dokümanı ise iki ayrı yerde şablonun **2026-07-11'de güncellendiğini** yazar: *"örnekler şablonun **O GÜN GÜNCELLENMEDEN** önceki sürümünden türetilmiştir"* ve *"**[EK 2026-07-11]** şablonun **yeni** BİÇİM KURALLARI bölümü de mekanik kontrole"*. **Ölçüm karar dokümanını doğrular:** elimizdeki `_SABLON.md` o değişikliği **içermektedir** — `video_kodlar` alanı **6a hareket kodları / 6b sahne kodları** diye ikiye ayrılmıştır (`6a` 1 · `6b` 1 · `hareket kod` 1 · `sahne kod` 1 isabet). **Sonuç: kanonik şablonun kendi tarih damgası bayattır ve bir türevin güncelliğini ölçmek için kullanılamaz.**

✅ **Bunun getirisi bir statü yükseltmesidir — "DONMUŞ" ve "ESKİDİ" artık beyan değil, ölçümdür.** Aynı ayrımın altı türevin **hiçbirinde** bulunmadığı ölçüldü: `kuyumculuk.md` · `otomaix.md` · `marka-patent.md` · `Kaynak-1.md` · `Kaynak-2.md` · `Kaynak-3.md` — **altısında da `6a`/`6b`/`hareket kod`/`sahne kod` desenleri 0 isabet.** Yani üç brief türevi ve üç ham çıktı, şablonun **2026-07-11 öncesi** sürümüne dayanmaktadır ve bu, tarih damgası olmayan `Kaynak-1/2/3.md` için **tek somut eskilik kanıtıdır.** ⚠️ **Ayrım `video_kodlar` 6a/6b ayrımıdır ve K-02'nin konusudur** — kararın kendisi açık kalır, bu ölçüm yalnız türevlerin hangi sürüme dayandığını gösterir.

---

## Ek A — Terimler sözlüğü

[GEREKİRSE]

| Terim | Tanım |
|---|---|
| [terim] | [bu proje bağlamındaki kesin anlamı] |

## Ek B — Karar günlüğü

[GEREKİRSE]

> ⚠️ **Bu günlük yalnız BU SENTEZ SIRASINDA alınmış kararları taşır.** Kaynak dokümanların kendi karar geçmişi (çürütülmüş varsayımlar, superseded hükümler) **Ek B'nin kapsamı dışındadır** ve ilgili bölümlerde kayıtlıdır. Sentez öncesi karar geçmişi Bölüm 17 final sweep'inde toplanacaktır.

| Tarih | Karar | Gerekçe | Karar sahibi | Etkilenen bölümler |
|---|---|---|---|---|
| 2026-08-17 | **K-03 KAPANDI** — dönem türü ile takvim kategorisi çatıştığında **paketin tür etiketi üretim davranışında üstündür**; kategori **korunur** ve günün kimliği ile doğrulanması için kullanılır | Kullanıcı tercihi. ⚠️ Yön, üç katmanın da taşıdığı **öneriyle aynıdır** — ama dayanak o hemfikirlik değil, **kullanıcı kararıdır** (ortak-mod, 2.1 md.1). ⚠️ **Kapsam dardır:** yalnız tür ↔ kategori çatışması; **K-23 kapanmaz**, genel bloklama kuralı kurulmaz | Kullanıcı (ürün sahibi) | **4.5 · 6.2 · 7.5 · 7.7 · 11.1 · 11.2 · 13 · 13.7 · 14 · 14.4 · 16 · 18 · 19** |
| 2026-08-17 | ⚠️ **Superseded:** *"paketin türü kazanır"* hükmünün **öneri** statüsü | Üç katmanda da öneri olarak duruyordu ve **karar yükünü ortadan kaldırmıyordu**; yerine geçen hüküm (yukarıdaki kullanıcı kararı) **kesinleşti**, bu yüzden eski statü normatif metinde tekrar edilmez (2.1 md.9) | Kullanıcı (ürün sahibi) | **11.2 · 13 · 18 · 19.1 · 19.4** |
| 2026-08-17 | **Kural hatasında geri alma kapsamı KAPANDI** — **vaka bazında geri alma, güvenli varsayılanla**: etkisi kanıtlananlar geri alınır; etki alanı güvenilir ayrılamıyorsa kuralın uygulandığı **tümü** geri alınır; etkilenmediği kanıtlananlar geri alınmaz | Kullanıcı tercihi. Koşulsuz toplu geri almanın **operasyon yükünü** düşürür, belirsizlikte **güvenli tarafta** kalır. ⚠️ Ölçütler tanımsızdır ve **uydurulmamıştır** — tanım teknik kabul sözleşmesidir | Kullanıcı (ürün sahibi) | **8.3 · 14.5 · 18 · 19.8** |
| 2026-08-19 | ⚠️ **Superseded:** *"Spec'e geçiş kararı: **koşullu hazır — beş kullanıcı kararıyla** (K-27 · K-118 · K-119 · K-121 · K-123)"* hükmü | Hükmün dayanağı, kapsam başına bloklayan karar sayımıydı; sayımın kaynağı olan blok kapsam matrisi **tamamlanmamıştır** — sayılar ölçülmüş olgu değildi (İlke 9). Aynı oturumun kapanışında **kullanıcı kararıyla geri çekildi**; yerine geçen hüküm bu günlüğün son kaydındadır. ⚠️ Geri çekilme zinciri: aynı oturumda önce *"hazır değil"* hükmü alınmış, o da geri çekilmişti — ilk hüküm `Spec öncesi kullanıcı kararı` sınıfının 47 üyesinin tümünü spec bloklayıcısı sayıyor, **sınıf ile kapsamı karıştırıyordu**. Öneriyi sentezci yaptı, hükmü ürün sahibi verdi | Kullanıcı (ürün sahibi) | **20** |
| 2026-08-19 | ⚠️ **Superseded:** *"Spec'e geçiş kararı: **hazır** — iki blokla (**K-01b** ve **K-02**)"* hükmü | Hüküm bir hakem belgesinde, **Bölüm 17 sweep'inden önce** yazılmıştı. ⚠️ **Çürütülmemiştir, DAYANAKSIZDIR:** hangi kararların spec'i blokladığının tam sayımı bu sentezde ölçülmüş değildir; iki kararla sınırlı sayım da ölçülmemiş bir iddiadır. Aynı hakem *"Spec'i bloklayan kararların sahibi ve son tarihi var"* kutucuğunu `[x]` işaretlemişti; bugünkü belgede son tarih 162 kararın 131'inde `[TANIMSIZ]`'dir, o kutucuk `[~]`'dir | Kullanıcı (ürün sahibi) | **20** |
| 2026-08-19 | **Spec'e geçiş kararı KAPANDI — "Spec yazımı başlayabilir; Bölüm 17'deki ürün kararları ilgili sözleşme kesinleşmeden kapatılmalıdır."** Spec'te ürün kararı gerektiren noktada karar uydurulmaz; açık karar **K-ID atfıyla** işaretlenir ve spec'in geri kalanı yazılır | Karar-sayımına dayalı önceki kapı, **tamamlanmamış** blok kapsam matrisinden türetilmiş sayılara dayanıyordu — İlke 9: ölçülmemiş sayı kapıya çevrilemez. Blok matrisi spec'e geçişin **kritik yolundan çıkarıldı**; yeniden açılma koşulu: blok sayısına dayanan bir hüküm gerekirse önce ölçülür. Bölüm 20'deki kanıtlanmamış blok sayıları kaldırıldı | Kullanıcı (ürün sahibi) | **20** |
| 2026-08-21 | **K-22 KAPANDI — A: politika motoru Faz 1'e girer** (pilotla birlikte kurulur) | Kullanıcı kararı (spec kapsam turu). ⚠️ Yön, belgedeki önerinin (*B'ye eğilim — kalibrasyon verisi pilottan gelir*) **tersidir**; öneri sentez değerlendirmesiydi, karar ürün sahibinindir. Sonuçlar: spec motor alt sistemini **Faz 1 kapsamında** yazar; motor kararları (**K-23 · K-24 · K-25 · K-133**) Faz 1 spec gündemine girer; **K-21'in koşulu tetiklenir** — ölçek gerekçesi (22 · 12 · ≤5 rakamlarının referansı) netleştirilmelidir. Kalibrasyon ihtiyacı ortadan kalkmaz: motorun eşikleri uydurulmaz, ölçümle kalibre edilir (**K-24**) | Kullanıcı (ürün sahibi) | **1 · 3.1 · 5 · 7.7 · 8 · 13 · 14 · 15 · 16 · 18 · 19.6–19.8** |
| 2026-08-21 | **K-27 KAPANDI — A: yönetici turu Claude Code komut ailesinden koşulur**; yönetici paneli geliştirilmez | Kullanıcı kararı. ⚠️ Belge bu kararda öneri vermiyordu. Komut ailesinin bugün var olup olmadığı **doğrulanmamıştır** — spec seansına taze doğrulama görevi doğar; komut ailesi yoksa kurulum işi A'nın maliyetine eklenir (maliyet belirsizliği kabul edildi; karar bununla yeniden açılmaz) | Kullanıcı (ürün sahibi) | **3.1 · 3.3 · 5.1 · 7.1 · 7.4 · 14 · 15 · 16.1 · 19.6** |
| 2026-08-21 | **K-30 KAPANDI — A: gerçek kullanım sinyali beklenmez; aktivasyon Faz 1'de yapılır** (risk kabulü) | Kullanıcı kararı; risk kabulüdür. **K-29'dan bağımsızdır** — K-29 (pilot markası) açık kalır. *"Faz 1 boyunca sinyal elde edilemez"* iddiası ölçülmemiş bir tahmindi; karar o tahmine değil, risk kabulüne dayanır. ⚠️ Gövde atfı yalnız Bölüm 1 karar-durumu ölçümündedir (2026-08-21 sweep'inde eklendi; karar öncesinde gövdede K-30 atfı yoktu); Bölüm 17 satırı aynı sweep'te güncellenmiştir | Kullanıcı (ürün sahibi) | **8.2 · 16.2** |
| 2026-08-21 | **K-05 KAPANDI — B: Faz 1'de kanal envanteri de kurulur** | Kullanıcı kararı. ⚠️ Yön, belgedeki önerinin (*A'ya eğilim — envanterin doğal evi Marka DNA işidir*) **tersidir**. Sonuç: Marka DNA işinde alan adayı olarak tanımlı kanal envanteri **bu işin Faz 1 kapsamına çekilir**; Faz 1 kapsamı büyür ve **Marka DNA işiyle sınır yeniden çizilir — spec bu sınırı tanımlamalıdır.** Kullanım talimatı satırı (**K-04** bağlantısı) korunur | Kullanıcı (ürün sahibi) | **3.1 · 3.2 · 4.6 · 7.1 · 7.5 · 11.4 · 12 · 13.2 · 18 · 19.1** |

## Ek C — Spec yazarına devir notu

> ⚠️ **Bu not Bölüm 17'nin yerine geçmez.** Kararların tam metni, seçenekleri, önerileri, sahipleri ve blok sınıfı orada yaşar; burada yalnız spec seansının **gündemi** özetlenir.

**Spec'te özellikle çözülmesi gereken teknik konular**

> **Spec'e geçiş hükmü (Bölüm 20):** spec yazımı başlayabilir; Bölüm 17'deki ürün kararları **ilgili sözleşme kesinleşmeden** kapatılmalıdır. Ürün kararı gerektiren noktada karar uydurulmaz; açık karar **K-ID atfıyla** işaretlenir ve spec'in geri kalanı yazılır.
>
> ⚠️ **2026-08-21 kapsam turu:** **K-22 · K-27 · K-30 · K-05** kullanıcı kararıyla kapandı (**Ek B**). **Gövde sweep'i aynı gün tamamlandı** (bağımsız denetim bulgusu üzerine): dört kararın statü ve kapsam izleri Bölüm 17 satırları dahil gövdede güncellenmiştir; kalıntı *"açıktır"* ifadesi görülürse Ek B kayıtları esastır.

1. **K-01b — `ozel_gun` anahtar sözleşmesi.** Normalize fonksiyonu; yazım ile okumanın **aynı kod yolunu** paylaşması; canlı takvim verisine karşı doğrulama. Araştırma brief'inin çıktı sözleşmesini de etkiler.
2. **K-02 — video hareket yüzeyi.** Hareket havuzunun paketten seçilmesi ve paket yoluna girmeyen üretimde mevcut hareket listesinin **byte-exact** kalması; şablonun 6a/6b ayrımının nihai alan adlarına bağlanması.
3. **İşlevsel kapının Katman-1 harness'ı** — beş prompt yüzeyinin (caption · görsel · kısa video · fikir önerme · legacy yollar) yakalanması ve byte-exact karşılaştırma. ⚠️ Marka DNA işiyle **ortak kurulup kurulmayacağı açıktır** — regresyon altyapısı paylaşımının bağlayıcı olup olmayacağı **K-20**'dedir.
4. **Sektör çözücü kök filtresi** ve sektör listeleme ucunun üst-sektör filtresi + regresyon testleri (**R-01**, **R-02**).
5. **Enjeksiyon haritasının üç tüketiciyi de kapsaması**; legacy kısa video yolu için **K-06** — yol ya düzeltilir ya açıkça kapsam dışı notlanır, **sessiz bırakılmaz**.
6. **Migration konvansiyonuna uyarlama** (birincil anahtar tipi, adlandırma, salt-ekleme tetikleyicisi, sektör başına tek aktif sürüm kısmi indeksi) ve alt sektör kısıtının veri tabanında mı uygulama katmanında mı zorlanacağı — **K-08 (b)**; ham artefaktın sektöre bağının modeli — **K-08 (a)**.
7. **Sürüm damgasının veri yeri** (**K-07**) ve aktivasyonun atomikliği (**R-17**); paket satırının koşuya bağının zorunlu olup olmayacağı (**K-110**).
8. **Önbellek davranışı** — paket aktive edildiğinde tazelemenin nasıl olacağı (**K-109**). Bugünkü önbellek davranışı bu sentezde ölçülmemiştir.
9. **Kullanım talimatı satırının blok şablonuna yazılması** — dağarcık kullanım kuralı (**K-04**, kapalı karar) ve marka gerçeği filtresi (**K-05**, kapalı karar — B: kanal envanteri Faz 1'de bu işte kurulur; envanter tasarımı ve Marka DNA sınırı spec gündemidir).
10. **Politika motoru** — kural seti, kanıt/eşik/bayrak kontrolleri, *"kararsız"* davranışı (**K-23**), eşiklerin kalibrasyonu (**K-24**), karar günlüğünün aktör alanı (**K-25**), motorun `active` satırına dokunamaması (**K-28**, kapalı karar). ⚠️ **Kuru modun benimsenip benimsenmeyeceği K-133'te açıktır.** ✅ **Motorun fazı karara bağlandı — K-22 KAPANDI — A** (2026-08-21, Ek B): motor **Faz 1'de** kurulur; bu madde Faz 1 spec'inin gündemidir.
11. **Özet diff tasarımı** — sayı değil **sinyal** odaklı biçim (eşik üstü çıkarmaların, geri ekleme çelişkilerinin ve motorun kararsız kaldıklarının öne alınması; tam listenin derinlemesine görünümde açılması) **bir öneridir ve K-42'de açıktır**; eşik üstü çıkarmanın eşiği **K-41**'de açıktır. Onayın biçimsel bir imzaya dönüşmesi riski (**R-21**) bu iki kararın girdisidir.
12. **Yönetici koşu yüzeyi** — ✅ **K-27 KAPANDI — A** (2026-08-21, Ek B): Claude Code komut ailesi; ailenin **bugünkü varlığı spec seansında taze doğrulanır**. Kalan gündem: yönetici ile müşteri arasındaki yetki ayrımı (**R-24**).
13. **Karar izi ve eleme kuralları** — pakete hiç girmeyen adayın karar izinde nasıl temsil edileceği (**K-87**), global tavan aşıldığında eleme sırası (**K-121**), *"güçlü kaynak"* sınıfının ölçütleri (**K-123**).
14. **Öncelik çatışmaları** — kullanıcının somut isteği ile markanın ses/üslup profili çatıştığında hangisinin kazanacağı (**K-118**) ve anma günlerindeki satış dili yasağının kullanıcı isteğini geçersiz kılıp kılamayacağı (**K-119**). ⚠️ İkisi de **ürün kararıdır**, teknik çözüm değildir.

**Korunması gereken ürün kararları**

- Paket yoluna girmeyen üretimde **byte-exact değişmezlik** — pazarlığa açık değildir.
- **Yan yana enjeksiyon yasağı** — paket bloğu ile kök sektör rehberi aynı prompt'ta bulunmaz.
- Üretim akışına **soru eklenmemesi** (sürtünme yasağı).
- **Çıkarma pozitif kanıt ister**; *"yeni araştırmada görülmedi"* tek başına gerekçe değildir.
- Aday alt sektör listesinin **kapalı** olması — serbest metin kabul edilmez.
- Paket **ek bağlamdır**, geçersiz kılıcı değildir. ⚠️ `anma` kısıtının kullanıcının somut isteğini geçersiz kılıp kılamayacağı **K-119**'da açıktır — *"tek istisna"* kesinleşmiş değildir.
- Ham katmanın **salt-ekleme** olması.
- Veri tabanına yalnız `draft` yazılması; **aktivasyonun yöneticide kalması** ve motorun `active`'e dokunamaması.
- Denetçilerin **karar vermemesi** ve körlüğün korunması.
- Kapsam dışı maddelerin **evinin belli olması** — ölçülen durum (2026-08-21 sweep sonrası): Bölüm 3.2 listesindeki 10 maddeden biri (K-05) karar kapanışıyla **kapsam içine çekildi**; kalan **9 kapsam-dışı maddenin 8'inde** yeniden ele alma koşulu veya adlandırılmış ev yazılıdır, **bakım borçları maddesinde yoktur** (Bölüm 20). ✅ **K-05 KAPANDI — B** (Ek B): kanal envanteri Faz 1'de bu işte kurulur; Marka DNA sınırı spec'te çizilir.

**Doğrulanması gereken varsayımlar (spec seansında taze koşum)**

- **2026-07-11 taramasındaki bütün kod konumları ve veri tabanı olguları.** Bu belge onları **aktardı, yeniden ölçmedi**; canlı kod ve veri tabanı bu sentezde taranmamıştır.
- Önbellek davranışı ve paket değişiminde geçersiz kılmanın kendiliğinden olup olmadığı (**K-109**).
- Aktivasyonun iki adımının tek transaction'da yapılabilirliği (**R-17**).
- Canlı takvim verisinin bugünkü şekli ve zamanlanmış işin davranışı (**K-01b**).
- Carousel'in ayrı bir prompt yüzeyi olup olmadığı (**K-15 (b)**).
- Bozuk veya eksik paket içeriğinde çalışma zamanı davranışı — iki dal tarif edilmiştir, **aralarındaki sınır tanımsızdır** (**K-15 (a)**).

**Bilinen eksik kanıtlar — ölçülmemiştir, kapı yapılamaz**

- **Paket token maliyeti ve üretim başına maliyet bir tahmindir**; ölçülmemiştir.
- Bugünkü bağlam katmanının önbellek eşiğinin altında kalıp kalmadığı **ölçülmedi**; *"paket önbelleği açar"* iddiası **doğrulanmadı**.
- **Faz 1 aktif paket tavanı (≤5) ölçülmemiş bir öneridir** (**K-13**); tur süresi ölçülmeden eşiğe çevrilemez.
- **Katman-2 örneklem boyutu (K-11 (a)) ve geçme eşiği (K-11 (b)) belirlenmemiştir.**
- `anma` akışının bugünkü takvim verisiyle tetiklenemediği **2026-07-11 taramasının aktarımıdır** `[AKT·KAYNAK · 2026-07-11]`; bugünkü davranış bu sentezde doğrulanmamıştır — akışın test edilebilirliği spec seansında taze koşumla belirlenir (**K-01a**).
- **Prompt enjeksiyonu savunması hiç ele alınmamıştır** (**K-10**).
- Pilotun hizmet sektörünü temsil etmediği — görsel kod yaklaşımının orada çalışıp çalışmadığı **bilinmiyor**.
- **Ölçek gerekçesinin kendisi ölçülmemiştir.** Hedef sektör sayısı olarak anılan **22**, aynı kaynaklardaki **12 kök sektör** ve **Faz 1 için ≤5 aktif paket** rakamlarıyla birlikte durur; ⚠️ **bu üç rakamın neyi saydığı ve hangi zaman ufkuna ait olduğu tanımlı değildir — uyuşmazlık kanıtlanmış DEĞİLDİR** (**K-21**). *"İnsan eliyle aylar sürer"* iddiası da ölçülmemiştir; pilotta **yöneticinin tur başına gerçek süresi ölçülmelidir**. Motorun eşikleri ölçülmemiştir (**K-24**) — eşik uydurulmaz, **kalibre edilir**.
- **Yönetici koşu yüzeyi karara bağlandı** (✅ **K-27 KAPANDI — A**, Ek B: Claude Code komut ailesi); **ölçülmemiş kalan**, ailenin **bugünkü varlığıdır** — spec seansında taze doğrulanır, yoksa kurulum maliyeti A'ya eklenir.

**Önerilen spec dosyası:** `docs/specs/<spec yazım tarihi>-sektor-bilgi-paketi.md`
