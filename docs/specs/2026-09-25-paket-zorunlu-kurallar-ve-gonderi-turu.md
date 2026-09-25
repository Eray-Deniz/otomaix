---
title: Sektör paketi — zorunlu kurallar, türe göre seçim, gönderi türü
date: 2026-09-25
status: spec-approved
codex_review_status: approved
codex_review_iterations: 5
approved: 2026-09-25 (Codex Tur 5 approve; Eray çerçevesi + K-A/K-B/K-C/K-D/K-E/K-F/K-G kararları)
task: docs/active/sektor-bilgi-paketi-plan2 (Open Problems madde 0)
supersedes-in: docs/specs/2026-08-21-sektor-bilgi-paketi.md §4.5 (K-04 tek blok), §4.6 madde 1 (mutlak sınır — kullanıcı isteği karşısında kalkar, paket karşısında sürer), §4.6 K-119, §11.3 (anma satırları)
review-log: ~/.claude/logs/otomaix--ffc87809/2026-09-25-feat-sektor-bilgi-paketi-plan2.md (5 tur, 18:11–18:43 UTC; dispositions §7)
---

# 1. Sorun (ölçülmüş, 2026-09-25 sınavı)

Kaynak: `docs/active/sektor-bilgi-paketi-plan2/olcum/SONUC-sinav-2026-09-25.md`, `a-rapor.json`,
`b-sonuc.json`, istem dosyaları `sonuc-sinav/istemler/`.

1. **Paket kural koyamıyor.** Blok modele "Bu dağarcıktan içeriğe uyan 2-3 öğeyi seç" (K-04) talimatıyla
   TEK seçmeli havuz olarak gidiyor; yasaklar ve ton kuralları da havuzun içinde. Gramaj paketli metinlerin
   14'ünde 0 kez yazıldı; kritik hata ≥5 senaryo; hakem tercihi 17/20 (bilgi yerinde, uygulanmıyor).
2. **Genel kural paketi eziyor.** "Ölçü, sayı → caption'da rakamı yazma" (teknik-spec kuralı) ile paketin
   "ayar, gramaj açıkça söylenir" kuralı aynı istemde; 20 senaryonun 16'sında çelişki (A5).
3. **Kalıp seçiminin ölçütü yok.** 19 çıktıda dört kancadan biri açıkça 1 kez, dokuz CTA'dan biri açıkça
   4 kez kullanıldı (Claude okuması, hakem ölçümü değil). Gözlenen sıra: istek kanal söylüyorsa o > özel gün
   kaydı > konu kelimesi tutan kalıp > modelin genel cümlesi.
4. **Gönderi türü üç yerde örtük çıkarılıyor, hiçbir yere yazılmıyor:** psikoloji kuralı
   (`prompt_builder.py:154`), genel şablonun görsel-açı kuralı, paket bloğu. Sözlükler farklı.
5. **Anma günleri pakette yok.** 16 gün kaydının hiçbiri `anma`; S08/S09'da dönem bloğu 0. S10'da
   (`kutlama` kaydı + "kullanıcı isteğinin üstündedir" satırı) model istek satış istese de satış yazmadı;
   paketsiz "hemen sipariş verin" yazdı. Yani açık öncelik satırı varken uyuluyor.
6. **Üç CTA kaynağı sırasız:** genel şablon "link doldurulmadıysa yönlendirme satırı ekleme" der; paket
   CTA'ları mağazaya/WhatsApp'a davet eder; gün kaydının kendi CTA'sı var. Takvim akışı HER özel günü
   "kutlama/tebrik postudur — satış formülü uygulanmaz" diye basar (Black Friday, Sevgililer dâhil;
   `prompt_builder.py:366`), paketin gün kaydı aynı gün için `ticari-firsat` der. Sınav şablonsuz koştu;
   şablon-paket çatışması ÖLÇÜLMEDİ.
7. **Ürün/hizmet ayrımı tabloda var, modele gitmiyor.** `brand_products.type ∈ {product, service}`; ürün
   bloğu yalnız ad/açıklama/etiket basıyor (`prompt_builder.py:390-398`).

# 2. Eray kararları (2026-09-25, on altıncı oturum)

| # | Karar | Not |
|---|---|---|
| K-A | **Kullanıcı isteği her kuralın üstünde.** Yayın öncesi kullanıcı onayı zorunlu olacak; sorumluluk onay verende. | Spec §4.6 / K-118 ile aynı yön. **Tur-1 hakem F1 (critical) sonrası Eray, aynı gün: ŞİMDİLİK her kuralın üstünde kalır — mevzuat yasakları, kişisel veri ve uydurma yasağı dâhil.** Bağlayıcı koşul: kullanıcı her gönderiyi sosyal medyaya gitmeden önce onaylar ve **onay anında hangi kuralın çiğnendiği gösterilir** (§3.12). Eski spec §4.6 madde 1'in "mutlak" niteliği kullanıcı isteği karşısında bu kararla kalkar; paket karşısında sürer. "Şimdilik": Eray tetik/tarih vermedi. |
| K-B | **K-119 iptal.** Anma günlerinde de istek geçerli. | Anma varsayılanı (satış çağrısı yok) kullanıcı açıkça istemedikçe sürer. |
| K-C | **Anma günleri hem pakette hem takvimde;** pakette olup takvimde olmayan gün takvime de işlenir. | Ölçüm: pakette olup takvimde olmayan 0 (yazım kapısı reddeder); takvimde olup pakette olmayan 9. Anma önerisi: 18 Mart · 10 Kasım · 15 Temmuz (2. sürüm operatör turunda kesinleşir). |
| K-D | **Zorunlu / seçmeli ayrımı:** zorunlu = ton-ve-dil'in 3 kuralı + yasaklar 5 + kanal kuralı; seçmeli = kanca · CTA · takvim temaları · görsel dil. | Ölçüt: kural her gönderiye aynı anda uygulanır; kalıp alternatifler arasından seçimdir. |
| K-E | **Alt sınır YOK** ("her gönderide bir kanca ve bir CTA" reddedildi). Seçim türe göre. | |
| K-F | **Sektör şablonu YOK;** tür, şablonun değil gönderinin özelliği. | 22 sektör şablonu 2026-04-15'te terk edildi (vault); canlı 81 gönderide sektör şablonu 6 (terk öncesi). |
| K-G | **Gönderi türünü kim belirler:** özel gün → kod (gün kaydı) · ürün modu → kod varsayılanı (product→satış, service→hizmet) + modelin "bilgi" istisnası · genel mod → model. Her durumda çıktıya `gonderi_turu` yazılır. Kullanıcıya yeni alan sorulmaz. | Canlı dağılım: ürün modu 39 · genel 36 · özel gün 6 (81 gönderi). |

# 3. Tasarım

## 3.1 Tek tür sözlüğü

`gonderi_turu ∈ {satis, hizmet, bilgi, kutlama, anma}`. Eşlemeler:

- Gün kaydı `tur`: `ticari-firsat → satis` · `karma → satis` (gün bağlamı korunur) · `kutlama → kutlama` · `anma → anma`.
- Paket CTA etiketi `(tür: satis|bilgi|hizmet)` aynı değerler; kutlama/anma'da CTA havuzu boş.
- Kanca kalıpları 2. sürümde etiket alır (`tür:`); etiketsiz kanca `satis` sayılır (bugünkü dördü öyle).
- Model çıktısı aynı beş değer.

## 3.2 Gönderi türü çözümleme (kod, `resolve_post_type`)

Girdi: özel gün kaydı (varsa) · ürün kaydı (`type`) · mod. Çıktı: `(tur | None, kaynak)`.

1. Gün kaydı varsa → 3.1 eşlemesi, `kaynak=gun_kaydi`. Model değiştiremez (istek hariç, K-A).
2. Ürün modunda → `product→satis`, `service→hizmet`, `kaynak=urun_varsayilan`. İsteme "Varsayılan tür: X;
   istek açıkça anlatım/bilgi istiyorsa `bilgi`ye çevir ve çevirdiğini yaz" satırı gider.
3. Genel modda → `None`, `kaynak=model`; istem "Gönderi türünü belirle ve yaz" der.

Model çıktısına iki alan eklenir: `gonderi_turu` (zorunlu) ve `kural_uyumu` (zorunlu, **kural başına** bir
satır). **Bağlayıcı kural kümesi = kodun o çağrıda BASTIĞI her bağlayıcı kural:** zorunlu bloktakiler
(`Z1..Zn`) VE özel gün bloğunun bağlayıcı satırları (`G1..Gm`: gün kaydının `mesaj_ekseni` kuralı; kutlama/anma
"satış çağrısı kullanma" varsayılanı) — kimlikleri kod üretir ve bastığı kümeyi çağrı bağlamında tutar (Tur-3
F1: ayrı basılan gün kuralı kümenin dışında kalıyordu). Model her kimlik için tek karar verir: `uyuldu` ·
`istek-geregi-cignendi` (+ isteğin tetikleyen parçası + üretilen cümle) · `uygulanamadi` (+ neden).
**Kod kapısı (deterministik):** (i) basılan kimliklerin TAMAMI çıktıda var, (ii) bilinmeyen kimlik yok,
(iii) her karar kapalı kümeden, (iv) `uyuldu` dışındaki her kararın kanıt alanları dolu — biri düşerse üretim
geçersizdir (Tur-1/2 F1: serbest `uyarilar` listesi boş bırakılabiliyordu; kural-kural zorunlu beyanda "boş"
diye bir durum yoktur). Değerler gönderi satırına yazılır (§3.12; `generation_stamps` DEĞİL —
o tablo yalnız marka/paket/sürüm/zaman taşır, ölçüldü) ve onay yüzeyi oradan okur. **Kalan risk, dürüstçe:**
beyan yine modelindir; "uyuldu" dediği hâlde çiğnemiş olabilir. Bu, sınavda "sessiz ihlal" olarak sayılır ve
kapıdır (§4); sınavda sessiz ihlal > 0 çıkarsa onay öncesi bağımsız ihlal denetimi (ikinci model çağrısı,
gönderi başına maliyet — ölçülmedi) açılır (§5).

## 3.3 Paket bloğu iki parça (`render_package_block`)

**A. `--- SEKTÖR PAKETİ · ZORUNLU KURALLAR (kuyumculuk) ---`**
- `kapsam` + kapsam kuralı (`Z` kimlikli): "Kapsam dışı ürün için paketin kalıplarını uygulama; bu durumu
  `kural_uyumu`nda bu kuralın satırına `uygulanamadi` + neden ('ürün kapsam dışı: <ürün>') olarak yaz" (sınav S07:
  saat kuyumculuk kalıplarıyla tanıtıldı). Onay yüzeyi bu satırı §3.12 gereği gösterir.
- `ton_ve_dil` (kural olarak; 3.7'deki bölünme gelene kadar paragraf olduğu gibi, kural cümleleri işaretli) ·
  `sektor_gercekleri` (yeni alan, 3.9) · `yasaklar_ve_hassasiyetler`.
- K-04 talimatından buraya taşınan iki kural: "ürün veya marka bilgisiyle çelişen kalıbı kullanma" ·
  "markanın sahip olmadığı kanalı VEYA HİZMETİ önerme". Marka kanal listesi (`brand_kit.channels`) ve marka
  hizmet listesi (`brand_products.type='service'`, aktif kayıtlar) açık satır olarak basılır (madde 16).
- Öncelik satırı (eski spec §4.6 madde 2–3 KORUNUR — Tur-2 N1): "Bu kurallar şablon varsayılanlarının, genel
  yazım kurallarının ve ürün açıklaması/teknik spec kuralının ÜSTÜNDEDİR; ama KULLANICI İSTEĞİNİN, gerçek
  ÜRÜN BİLGİSİNİN ve MARKA DNA'sının (markaya özgü yasak kelimeler dâhil) ALTINDADIR. Ürün bilgisiyle çelişen
  paket kuralı uygulanmaz; marka yasak kelimesi paket kuralına ve genel kurallara karşı kazanır. Kullanıcı isteği
  bir kuralla çatışıyorsa isteğe uy ve her çiğnenen kuralı `kural_uyumu`nda 'istek gereği çiğnendi' diye
  işaretle (§3.12)."
- **Tek öncelik sırası (Tur-3 N3):** kullanıcının açık isteği > gerçek ürün bilgisi = marka DNA (yasak kelimeler
  dâhil) > paket zorunlu kuralları > genel yazım/teknik-spec kuralları > şablon varsayılanları. Kullanıcı açıkça
  kendi yasak kelimesini isterse istek kazanır (K-A, "her kuralın üstünde"); bu ihlalin onayda ifşası paket
  kimlik kümesinin DIŞINDADIR (marka DNA kuralı, paket kuralı değil) — evi Marka DNA işi
  (`otomaix-sosyal-medya-arastirmasi/marka-dna-mimari-karar-dokumani.md`, spec girdisi; tarih Eray'da).

**B. `--- SEKTÖR PAKETİ · DAĞARCIK (seçmeli) ---`**
- `kanca_kaliplari` (türe göre süzülmüş) · `cta_kaliplari` (tür + kanal süzgeci) · `takvim_temalari` (3.7'ye
  göre yalnız günsüz dönemler).
- Seçim talimatı (K-04'ün yerine): "Gönderi türü X. Kanca: bu türe uyan en fazla BİR kalıp; uyan yoksa hiç.
  CTA: yalnız `tür: X` etiketli ve markanın kanalına uyan en fazla BİR kalıp; uyan yoksa CTA yazma.
  Listeyi tamamlamaya çalışma; ürün veya marka bilgisiyle çelişen kalıbı kullanma." Kutlama/anma'da CTA
  havuzu basılmaz.
- Süzgeç iki katmanlı: tür çağrıdan ÖNCE biliniyorsa (özel gün · ürün modu varsayılanı) kanca/CTA havuzu
  KODDA türe göre süzülür; genel modda ve ürün modunun `bilgi` istisnasında tür çağrı içinde belirlendiği için
  havuz **tür etiketleriyle** basılır ve süzgeci model talimatla uygular ("yalnız `tür: X` etiketli"). Ürün
  modunda kod, varsayılan türün havuzu + `bilgi` havuzunu (etiketli) basar, `kutlama/anma` havuzlarını basmaz —
  model `bilgi`ye çevirirse kalıbı hazırdır (Tur-2 PN-1). Çıktıdaki `gonderi_turu` ile kullanılan kalıbın etiketi
  Katman-2'de karşılaştırılır. Blok, girdileri sabitken bayt-sabittir (Katman-1).

## 3.4 Özel gün satırları (`render_special_day_lines`)

- Gün kaydının beş yuvası ayrı yetkiyle basılır: `tur` → kod, gönderi türü (3.2; basılmaz, "Tür (paket)" satırı
  kalkar) · `mesaj_ekseni` → "Bu gün için geçerli kural:" başlığıyla, zorunlu bloğun yetkisiyle · `kanca` ve
  `cta` → seçmeli ("en fazla bir", kanal süzgeci aynı) · `gorsel_vurgu` → görsel yüzeyi, seçmeli (değişmez).
- K-119 satırları ("Bu yasak KULLANICI İSTEĞİNİN ÜSTÜNDEDİR…") KALDIRILIR (K-B).
- Kutlama/anma varsayılanı kalır: "CTA yerine kutlama-saygı kalıbı; satış çağrısı kullanma." + "Kullanıcı
  açıkça satış/kampanya isterse isteğe uy ve bu kuralı `kural_uyumu`nda `istek-geregi-cignendi` diye işaretle."
  Gün bloğunun bağlayıcı satırları `G` kimliği taşır ve §3.2'deki zorunlu beyan kümesine girer. Bugünkü
  render'ın bağlayıcı satırlarının TAMAMI (`render_special_day_lines`, ölçüldü) ve akıbeti:
  `G-mesaj` = "Mesaj ekseni: …" (her gün türünde) · `G-satis-yok` = "CTA yerine kutlama-saygı kalıbı; satış çağrısı
  kullanma" (kutlama ve anma) · `G-anma-cerceve` = "Anma ek kısıtı: yalnız saygı çerçevesinde içerik üret; uygun
  bir saygı çerçevesi kurulamıyorsa içerik önerme" (yalnız anma; KORUNUR, K-A gereği açık istekle ezilebilir ve
  ezilirse `istek-geregi-cignendi` ile ifşa edilir). Kaldırılan satırlar: "Tür (paket): …", K-03 çatışma satırı
  ("Çatışma hâlinde bu tür … üstündür") — tür artık koddan çözülür, satır kimlik almaz — ve K-119 satırı.
  Seçmeli yuvalar (kanca, cta, gorsel_vurgu) kimlik taşımaz. Kod, bastığı her bağlayıcı satıra kimlik verir;
  render'a yeni bir bağlayıcı satır eklenirse kimlik almadan basılamaz (yapısal test: bağlayıcı satır ↔ kimlik
  eşlemesi üretilmiş matrisle).
- Takvim akışının "her gün kutlama postudur" satırı (madde 6): paketli markada gün kaydının türü belirler;
  paketli yolda o satır türe göre basılır (`kutlama/anma` → kalır; `satis` → "gün bağlamı, satış serbest").
  **Paketsiz yol DEĞİŞMEZ.**

## 3.5 CTA kaynak sırası (tek sıra)

kullanıcı isteği (K-A) > gün kaydı CTA'sı (tür izin veriyorsa) > paket CTA'sı (tür + kanal) > şablonun
"link yoksa yönlendirme satırı ekleme" kuralı > hiç. Paketli markada markanın kanalını anan paket CTA'sı link
olmadan da yazılabilir; şablon kuralı yalnız link satırı için geçerli kalır.

## 3.6 Ürün bloğu

Ürün modunda bloğa `Tür: ürün | hizmet` satırı eklenir (`brand_products.type`). Paketsiz yolda da basılır
mı? **Hayır** — paketsiz Katman-1 bayt-bayt korunur; satır yalnız paketli yolda.

## 3.7 Paket 2. sürümü içeriği (operatör kararı yolu, `ekle ozel_gun` / `ekle kanca`)

- `anma` kayıtları: 18 Mart · 10 Kasım · 15 Temmuz (beş yuva: tur · mesaj_ekseni · kanca · cta=içerik-önerilmez · gorsel_vurgu).
- Sektör gerçeği: "22 ayar saf değildir; saf altın 24 ayardır" (madde 17) → zorunlu kurallara.
- Kanca havuzu tür başına: hizmet (onarım/ölçü/taklas/bakım), bilgi (kararma/ayar/taş bakımı), kutlama; bugünkü dördü `satis`.
- CTA etiketleri korunur; kanal etiketleri korunur.
- `ton_ve_dil` yeniden yazılır: üç kural ayrı satır (`degistir`), ton cümleleri ("güven eksenli danışman dili",
  "duygu ekseni anı, hediye, kuşaklar arası kalıcılık") ayrı ve K-118 gereği yumuşak yönlendirme olarak
  işaretli. Bloğu basan kod kural satırlarını zorunlu, ton cümlesini "ton (yumuşak)" etiketiyle basar.
- `takvim_temalari`: gün kaydı olan dört tema (Sevgililer · Anneler · Babalar · Yılbaşı) `cikar` ile düşer;
  alanda yalnız takvimde günü olmayan dönemler kalır (düğün ve nişan sezonu). Çift enjeksiyon biter.
- `sektor_gercekleri` doldurulur (3.9): "22 ayar saf değildir; saf altın 24 ayardır" + sentez/denetçi
  raporlarında kaynaklı olan diğer doğrular (kaynaksız doğru eklenmez — madde 11a).
- Anma günü takvimde zaten var (yıllık n8n işi 18 Mart ve 10 Kasım'ı üretiyor — ölçüldü); takvime gün EKLENMEZ.

## 3.8 Değişmeyenler

- Paketsiz yol bayt-bayt aynı (Katman-1 kapısı). Paketli fixture'lar yeniden üretilir (kasıtlı, diff incelenir).
- Motor/denetçi/sentez hattı, aktivasyon, kanal süzgeci fonksiyonu (`filter_channel_dependent`) aynı.
- Kullanıcıya tür seçtirilmez; şablon ızgarası açılmaz.
- İKİ şema değişikliği vardır ve ikisi de bu notta: 3.9 (paket içeriğine onuncu alan, şema sürümü 2) ve
  3.12 (gönderi satırına tür + uyarı kolonları). Mevcut dokuz alanın adı ve tipi değişmez.

## 3.9 Şema: `sektor_gercekleri` (onuncu alan)

Şema bugün dokuz alanla KAPALI (`CONTENT_FIELDS`); sektör doğrusu için yer yok. **Bağlayıcı uyumluluk
invariantı (Tur-1 F2):** alan kümesi paket satırındaki `schema_version`a bağlanır — sürüm 1 = bugünkü dokuz
alan, sürüm 2 = dokuz + `sektor_gercekleri`. Okuyucu (`resolve_package_context`) ve yazım kapısı
(`validate_package_content`) satırın kendi şema sürümüne göre denetler; **canlıdaki 1. sürüm paket yeni kodla
okunmaya devam eder** (ölçüldü: bugün `_check_closed_field_set` eksik alanı hata sayıyor ve okuyucu paketi
paketsiz yola düşürüyor; `schema_version` kolonu var, kod kullanmıyor). Dağıtım sırası: önce iki sürümü de
okuyan kod, sonra 2. sürümün yazımı/aktivasyonu. **Geri dönüş tabanı (Tur-2 N2):** 2. sürüm aktifken kod
geri dönüşü YALNIZ şema-2 okuyucusunu içeren ilk commit'e kadar yapılabilir (eski kod `sektor_gercekleri`ni
bilinmeyen alan sayar ve paketi paketsiz yola düşürür — ölçüldü). Tabanın altına inilirse düşüş SESSİZ DEĞİLDİR:
okuyucu `package_read_error` olayı yazar ve bu olay `ADMIN_NOTIFIED_EVENTS` kümesindedir → yönetici Telegram
bildirimi (ölçüldü, `package_events.py`); üretim paketsiz yolla sürer (paket öncesi davranış), çökmez. Bu yüzden
taban bir runbook kuralıdır, aktivasyon ön koşulu değildir; 1. sürümü yeniden aktive etme yoluna BAĞLI DEĞİLDİR
(Tur-3 N2: md-18 bağı döngüseldi, kaldırıldı — md-18 kendi evinde kalır). Aktivasyon öncesi kanıt (§4): şema-2
paket + şema-1 okuyucu → paketsiz yol + `package_read_error` olayı, test ortamında ölçülür. Geri dönüşte
1. sürüm okunabilir kalır. Alan `LIST_FIELDS`
(şema 2) içindedir; boş olmayan liste ister, `içerik-önerilmez` (K-120) kabul; sentez sözleşmesi ve şablon
(`_SABLON.md`) aynı adı alır (dış depo commit + pin). Yüzey: yalnız zorunlu blok (3.3-A). Operatör yolu
`ekle`/`degistir`/`cikar` bu alanı da tanır (şema-2 `LIST_FIELDS` üzerinden; test var).

## 3.10 `video_kodlar` (kayıt, davranış değişmez)

`sahne` (3) ve `hareket` (5) havuzları kısa video yüzeylerine gider (spec §4.3, Task 11); seçmeli havuzdur, bu
tasarım dokunmaz. Buraya yalnız ayrımın tam listesi eksik kalmasın diye yazıldı.

## 3.11 Ayrımın tam listesi (dokuz alan + iki talimat kuralı)

| Alan / kural | Sınıf | Yüzey | Kaynak bölüm |
|---|---|---|---|
| `kapsam` + kapsam kuralı | zorunlu | başlık, fikir | 3.3-A |
| `ton_ve_dil` — kural cümleleri | zorunlu | başlık, fikir | 3.3-A, 3.7 |
| `ton_ve_dil` — ton cümleleri | yumuşak yönlendirme (K-118) | başlık, fikir | 3.7 |
| `sektor_gercekleri` (yeni) | zorunlu | başlık, fikir | 3.9 |
| `yasaklar_ve_hassasiyetler` | zorunlu | başlık, fikir | 3.3-A |
| "çelişen kalıbı kullanma" · "bilmediğin kanalı/hizmeti önerme" | zorunlu | başlık, fikir | 3.3-A |
| `kanca_kaliplari` | seçmeli (türe göre ≤1) | başlık, fikir | 3.3-B |
| `cta_kaliplari` | seçmeli (tür + kanal, ≤1) | başlık, fikir | 3.3-B, 3.5 |
| `takvim_temalari` (yalnız günsüz dönemler) | seçmeli | başlık, fikir | 3.3-B, 3.7 |
| `gorsel_kodlar` | seçmeli | görsel talimatı | değişmez |
| `video_kodlar.sahne` · `.hareket` | seçmeli | kısa video | 3.10, değişmez |
| `ozel_gun[].tur` | kod (gönderi türü) | — | 3.2 |
| `ozel_gun[].mesaj_ekseni` | zorunlu (o gün) | başlık, fikir | 3.4 |
| `ozel_gun[].kanca` · `.cta` | seçmeli (≤1) | başlık, fikir | 3.4 |
| `ozel_gun[].gorsel_vurgu` | seçmeli | görsel talimatı | değişmez |

## 3.12 Onay anında ifşa (K-A'nın bağlayıcı koşulu — Tur-1 F1/F3)

- Gönderi satırı iki kolon alır (migration): `gonderi_turu TEXT NULL` · `kural_uyumu JSONB NOT NULL DEFAULT '[]'`.
  Üretim kaydı sırasında modelin iki alanı buraya yazılır (`posts.package_id/package_version` zaten var; damga
  tablosu değişmez). Paketsiz üretimde `kural_uyumu` boş listedir (paket kuralı yok).
- Kullanıcı onay verirken (arayüzdeki onay adımı ve Telegram onay akışı) `istek-geregi-cignendi` ve
  `uygulanamadi` satırları **kural adıyla gösterilir**; hepsi `uyuldu` ise kısa "paket kurallarına uyuldu" satırı.
  Paketli gönderide `kural_uyumu` eksikse (kod kapısı düşmüşse) gönderi onaya HİÇ gelmez. Gösterim biçimi
  uygulama planının kararıdır; gösterilmesi bu notun invariantıdır.
- Katman-2 ölçümü `kural_uyumu`nu okur: istekten gelen ihlal `istek-geregi-cignendi` ile işaretliyse "ifşa
  edildi"; hakem/okuyucu metinde ihlal bulur ama satır `uyuldu` diyorsa "sessiz ihlal" (§4).

# 4. Doğrulama

| Kapı | Ne |
|---|---|
| Katman-1 | paketsiz fixture bayt-aynı (PASS zorunlu); paketli fixture'lar yenilenir; iki blok + tür satırı varlığı deterministik |
| Birim | `resolve_post_type` matrisi (gün türü × ürün türü × mod); kanca/CTA süzgeci (tür × kanal, üretilmiş matris); K-119 satırlarının yokluğu; `kural_uyumu` kod kapısı (eksik/bilinmeyen kimlik → üretim geçersiz; paketsiz yolda boş liste); öncelik satırında ürün bilgisi + marka yasak kelimesi üstünlüğü (N1); geri dönüş tabanı testi (şema-2 paket + şema-1 okuyucu → paketsiz yola düşer + `package_read_error` olayı yazılır; runbook satırıyla eşleşir); `kural_uyumu` kümesinin gün bloğu kimliklerini (`G*`) de kapsadığı (özel günlü paketli üretimde eksik `G` kimliği → geçersiz); ürün `Tür:` satırı yalnız paketli yolda; kapsam kuralı + kanal/hizmet listesi satırları yalnız zorunlu blokta; gün bloğunda `mesaj_ekseni` kural başlığıyla, `Tür (paket)` satırı yok; `sektor_gercekleri` yazım kapısı (boş liste ret, `içerik-önerilmez` kabul) ve operatör `ekle/degistir/cikar` |
| Mutasyon | her yeni kapı için ≥1 mutasyon düşürür |
| Sınav tekrarı | aynı 20 senaryo, Codex kör hakem + Eray kör okuma. **İki ölçüt yan yana (Tur-1 F4):** (a) ESKİ ölçüt — `KALIBRASYON.md` (2026-09-25) DEĞİŞMEDEN, kritik hata sayımı yalnız karşılaştırma metriğidir (17/20 ve ≥5 ile aynı cetvel); (b) YENİ ölçüt — sınavdan ÖNCE ayrı dosyada sabitlenir (`KALIBRASYON-2.md`): istekten gelen ihlal `kural_uyumu`nda `istek-geregi-cignendi` ile işaretliyse hata değil, `uyuldu` deniyorsa **sessiz ihlal** (hata); modelin kendi ihlali her durumda hata. Ek ölçütler: `gonderi_turu` senaryo amacıyla uyuşma · kanca/CTA kalıbı türe göre · gramaj çelişkisi 0 · ürün bilgisi ve marka yasak kelimesiyle çatışan paket kuralı senaryosu (N1 matrisi) |
| Eşik | hakem ≥15/20 paketli VE yeni ölçütte (b) kritik hata 0 VE **sessiz ihlal 0**; eski ölçüt (a) sayımı raporda yan yana, kapı değil |
| Maliyet | ölçülmüş: 40 çağrı 1,5781 USD (2026-09-25) → tekrar **tahmin ≈ 1,6 USD**; her ücretli koşudan önce Eray onayı |

# 5. Kapsam dışı / açık kalemler (evli)

- **Kullanıcıya tür seçtirme (4 kutucuk):** yalnız sınav tekrarında `gonderi_turu` hatası çıkarsa. Ev: sınav sonucu değerlendirmesi.
- **`KALIBRASYON-2.md` (yeni ölçüt) sınavdan önce yazılır ve sabitlenir;** `KALIBRASYON.md` değişmez. Ev: ölçüm adımı.
- **Bağımsız ihlal denetimi (onay öncesi ikinci model çağrısı):** yalnız sınav tekrarında sessiz ihlal > 0
  çıkarsa açılır; gönderi başına maliyeti o gün ölçülür. Ev: sınav sonucu değerlendirmesi.
- **Kök perakende rehberi susuyor (madde 12):** ev Plan 2 kapanışı (mevcut).
- **21 pasif şablonun "önerilen CTA" listeleri:** pasif, dokunulmaz.
- **Takvime yeni gün (K-01a):** bugün gerek yok (eksik 0); tetik: 2. sürümde takvimde olmayan gün istenirse → n8n işi + migration birlikte.
- **Şablon-paket CTA çatışması canlıda:** sınav şablonsuz; tekrar sınavı `genel-gorsel-sablon` ile koşulur (3.5'i ölçer).

# 6. Riskler

- K-A yasal yasakları, kişisel veriyi ve uydurma yasağını da kullanıcı isteğine açar (S06 lab pırlanta, S16 gerçek ad bu kuralla üretilir). Kabul: Eray, 2026-09-25, "şimdilik"; azaltıcı: onay anında kural adıyla ifşa (§3.12). Kalan risk: kullanıcı ifşaya rağmen onaylar; metni platform üretmiş olur. İkinci kalan risk: kural-kural beyan
modelindir, "uyuldu" yanlış olabilir — sınavda sessiz ihlal kapısıyla ölçülür (§4), >0 ise §5 bağımsız denetim.
- Paketli Katman-1 fixture'ları yeniden temellenir; kapı o an "yeni davranışı" tanımlar. Azaltıcı: diff Codex hakemine gider.
- İstem büyür (iki blok + tür satırı); paketli blok bugün 2.681–3.330 karakter (ölçüldü); artış ölçülür, kapı değil.
- Model `gonderi_turu`yu yanlış çıkarabilir (genel mod): ölçülür, hata çıkarsa 5. bölümdeki kutucuk yolu açılır.

# 7. Hakem turu kayıtları

**Tur 1 (2026-09-25 18:11–18:15 UTC, Codex adversarial-review, worktree-review substratı):** verdict
needs-attention; 1 critical + 3 high (hepsi spec-level) + 1 plan notu. Ham çıktı: `review-log` (ön bilgi).

| F | Ağırlık | Başlık | Doğrulama | Disposition |
|---|---|---|---|---|
| F1 | critical | K-A yasal/uydurma sınırlarını isteğe açıyor; eski §4.6 madde 1 ile çelişki | doğru (notun kendi metni) | **Eray kararı:** şimdilik her kuralın üstünde, onay anında ifşa zorunlu → §2 K-A, §3.12, §6, ön bilgi `supersedes-in` |
| F2 | high | Yeni zorunlu alan 1. sürümü okunamaz kılar | doğru (`_check_closed_field_set` eksik alan = hata; okuyucu paketsiz yola düşürüyor; `schema_version` kullanılmıyor) | fixed → §3.9 uyumluluk invariantı + dağıtım sırası |
| F3 | high | `generation_stamps`te tür/uyarı kolonu yok; "tek şema değişikliği" çelişkisi | doğru (tablo: brand_id, package_id, package_version, created_at, consumed_at) | fixed → §3.2 + §3.12 (gönderi satırı kolonları) + §3.8 |
| F4 | high | Sınav kapısı yeniden adlandırmayla geçilebilir | doğru | fixed → §4 iki ölçüt, §5 |
| PN-1 | plan notu | Genel modda tür çağrı içinde belirleniyor; kod süzemez | doğru | fixed → §3.3-B iki katmanlı süzgeç |

**Tur 2 (2026-09-25 18:27–18:30 UTC, kapanış-doğrulama):** F2 · F3 · F4 KAPALI (hakem teyidi). F1 AÇIK kaldı +
iki yeni high + PN-1 ayağı.

| F | Ağırlık | Başlık | Doğrulama | Disposition |
|---|---|---|---|---|
| F1 | critical | İfşa yalnız modelin serbest beyanına dayanıyor; boş `uyarilar` ile ihlal onayda görünmez | doğru | fixed → §3.2 kural-kural zorunlu beyan (`kural_uyumu`, kod kapısı: eksik kimlik = geçersiz üretim), §3.12, §4 sessiz ihlal kapısı, §5 koşullu bağımsız denetim, §6 |
| N1 | high | Öncelik satırı marka DNA'sı ve gerçek ürün bilgisini paketin altına düşürüyor (eski §4.6 madde 2–3) | doğru (notun kendi metni) | fixed → §3.3-A öncelik satırı, §4 matris |
| N2 | high | 2. sürüm aktifken kod geri dönüşü paketi sessizce düşürür | doğru (`_check_closed_field_set` bilinmeyen alan = hata) | fixed → §3.9 geri dönüş tabanı + md-18 bağı, §4 test |
| PN-1b | plan notu | Ürün modunda `bilgi` istisnası çağrı içinde; kod varsayılana göre süzüyor | doğru | fixed → §3.3-B (varsayılan + bilgi havuzu birlikte) |

**Tur 3 (2026-09-25 18:33–18:35 UTC, kapanış-doğrulama):** N1 · PN-1b KAPALI. F1 ve N2 açık kaldı; N3 yeni high; PN-2 plan notu.

| F | Ağırlık | Başlık | Doğrulama | Disposition |
|---|---|---|---|---|
| F1 | critical | Ayrı basılan özel gün kuralı kimlik kümesinin dışında; §3.4 hâlâ `uyarilar` diyordu | doğru | fixed → §3.2 küme = basılan her bağlayıcı kural (Z* + G*), §3.4 |
| N2 | high | md-18 bağı döngüsel (md-18 2. sürümde koşuyor); taban aktivasyonda kanıtsız | doğru (TASK md-18 tanımı) | fixed → §3.9: taban runbook kuralı; tabanın altı sessiz değil (`package_read_error` ∈ `ADMIN_NOTIFIED_EVENTS`, ölçüldü); md-18 bağı kaldırıldı; §4 test |
| N3 | high | Yasak kelime için iki çelişen cümle | doğru (notun kendi metni) | fixed → §3.3-A tek öncelik sırası (K-A: açık istek kazanır; ifşa evi Marka DNA işi) |
| PN-2 | plan notu | Kapı yalnız kimlikleri denetliyordu | doğru | fixed → §3.2 kapı (iii)(iv): karar değeri + kanıt alanları |

**Tur 4 (2026-09-25 18:37–18:40 UTC, kapanış-doğrulama):** N2 · N3 · PN-2 KAPALI. F1 açık (dar) + 1 yeni high.

| F | Ağırlık | Başlık | Doğrulama | Disposition |
|---|---|---|---|---|
| F1 | critical | Anma "saygı çerçevesi" kısıtı G listesinde yoktu | doğru (render satırı var, §3.4 saymıyordu) | fixed → §3.4: render'ın bağlayıcı satırlarının tam listesi (`G-mesaj`, `G-satis-yok`, `G-anma-cerceve`), kaldırılanlar sayıldı, yapısal test |
| N4 | high | Kapsam kuralı kaldırılan `uyarilar` alanına yazdırıyordu | doğru | fixed → §3.3-A: `kural_uyumu` satırı `uygulanamadi` + neden; notta `uyarilar` atfı sınıf olarak süpürüldü |

**Tur 5 (2026-09-25 18:41–18:43 UTC, kapanış-doğrulama): `verdict: approve`.** F1 · F2 · F3 · F4 · N1 · N2 · N3 · N4 ·
PN-1/1b · PN-2 — on kapanışın onu hakemce teyit edildi; yeni spec-level bulgu yok; PLAN-NOTES yok.

**Zincir özeti:** 5 Codex turu (1 tam + 4 kapanış), toplam ~14 dk çağrı süresi (18:11→18:15 · 18:27→18:30 ·
18:33→18:35 · 18:37→18:40 · 18:41→18:43); kota kapısı her turdan sonra CONTINUE. Bulgu sayımı: 1 critical (F1,
dört turda dört komşu boşlukla kapandı) · 6 high (F2, F3, F4, N1, N2, N3 + N4 = 7) · 0 medium/low · 3 plan notu.
Review base: `--scope working-tree` (not untracked; substrat worktree-review, REQUIRED=`<SPEC_PATH>`).
Süreç dersi: F1'in dört turu, düzeltmeden sonra sınıfın (kaldırılan alan adı · render'ın bastığı her bağlayıcı
satır) notta süpürülmemesinden çıktı — kapanış turundan önce sınıf süpürmesi ([[feedback_close_the_class_not_the_variant]]).
