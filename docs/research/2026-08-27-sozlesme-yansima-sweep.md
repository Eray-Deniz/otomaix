# Sözleşme yansıma sweep'i — 6 zorunlu düzeltme + 7 kapanış kalemi

**Tarih:** 2026-08-30 · **Görev:** Plan 2 / Task 2 · **Depo:** `/root/otomaix-sosyal-medya-arastirmasi/`
**Ölçüm tabanı (Adım 1):** commit `b356033`, çalışma ağacı temiz.
**Kanonik kaynak:** `docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md` (çelişkide spec'in üstündedir)
· ikincil: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` §8.7, §12.2.

Bu dosya **iki ölçüm** taşır: Adım 1 (düzeltmeden ÖNCE) ve Adım 3 (düzeltmeden SONRA).
Adım 1 tablosu düzeltme yapıldıktan sonra GERİYE DÖNÜK düzenlenmemiştir — kayıt olarak durur.

---

## Adım 1 — ÖNCE ölçümü (13 kalem)

Sözleşme dosyaları kısaltmaları: **S** = `hakem-sentez-gorevi.md` · **D** = `hakem-denetci-gorevi.md`
· **T** = `_SABLON.md`. Satır numaraları `b356033` içindeki hâle aittir.

| # | Kalem | Durum | Ölçüm (dosya:satır) |
|---|---|---|---|
| 1 | **K-03 yansıması** — tür etiketi üstün; "açık soruya düşür" metni kalkar | **EKSİK (ters drift)** | S:116-119 hâlâ *"kararı VERME — iki tarafı ve eğilimini yazarak AÇIK SORU'ya düşür (K3 operatör politikası)"* der. Kapanmış karar (K-03=A) bunun tersidir. |
| 2 | **Kök sektör rehberi** sentez girdi listesinde | **EKSİK** | S:23-33 GİRDİLER listesi altı kalem sayar (EK-A · EK-F/G · EK-H · EK-I · EK-J · ham kaynaklar). Onaylı **7. girdi** yok. Resmî tur bu yüzden BLOKLU. |
| 3 | **`[kopya-şüphesi]` tüketim satırı** | **EKSİK** | S:72-90 "Kurallar" bloğu altı bayrağın tüketimini yazar ( `[kaynak-bağımlı]` · `[genel-geçer]` · `[marka-adı]` · `[kanal-bağımlı]` · `[eski-kaynak]` · `[metin-öğesi]` ). `[kopya-şüphesi]` **hiç geçmiyor** (dosyada tek eşleşme yok). Bayrak D:71'de tanımlı ama sentezde tüketilmiyor. |
| 4 | **Rol hükmü** motorlu modele revize (K-22=A) | **EKSİK (ters drift)** | S:19 *"Karar merci sensin (aktivasyon hariç…)"*. Ayrıca S:135-137 sentezi doğrudan DB yazıcısı gibi konumlandırır (*"DB'ye yalnız status='draft' yazılır"*) — kanonik sıra `sentez → motor → draft` ile çelişir. |
| 5 | **URL örneklem "9 satır"** koşullu ölçüme | **EKSİK (ters drift)** | D:103 *"URL ÖRNEKLEM SONUCU — 9 satır"*. D:36 ve D:50-51 eleme hâlinde kaynak sayısının düşebileceğini zaten söylüyor → sözleşme içi tutarsızlık. |
| 6 | **Kanal anahtar uzayı dört değerle KAPALI** | **EKSİK — üç iniş yeri** | **T:49-51** (`[kanal-bağımlı: X]` etiketi koy) · **S:78** (`[kanal-bağımlı: X] kalıp pakete girerken…`) · **D:74-76** (`[kanal-bağımlı: X]: kalıp MARKADAN…`). Üçünde de X **serbest**. R12(c)'nin 2026-08-30 ölçümü doğrulandı, satır numaraları **kaymamıştır**. |
| 7 | **K-120** — resmî `içerik-önerilmez` değeri | **KISMİ** | T:131-132 `anma` dalında *"…veya "içerik önerilmez" de"* düz metin olarak geçer; **resmî değer değildir** (düz metin içinde tırnaklı serbest ifade; yazımı hiçbir yerde bağlanmamış) ve T:142 `cta` alt sınırı (≥2 kalıp) bu dala **muafiyet tanımaz**. Doluluk kontrolünün "bilinçli boş" davranışı hiçbir yerde yazılı değil. |
| 8 | **K-121** — mevzuat öncelikli ALTILI kırpma sırası | **EKSİK (ters drift)** | S:100 kırpma katmanında hâlâ terk edilmiş ÜÇLÜ sıra: *"(1) sektöre özgülük, (2) mutabakat gücü, (3) yerellik"*. |
| 9 | **K-122** — churn koruması | **EKSİK** | S:92-104 (ADIM 3) kırpma sonucuna konan böyle bir kısıt taşımıyor. S:62-63'teki *"'Yeni araştırmada geçmiyor' TEK BAŞINA çıkarma gerekçesi değildir"* satırı **başka bir şeydir** (`cikar` kanıt şartı), churn koruması değil. |
| 10 | **K-123** — "güçlü kaynak" ölçütü | **EKSİK** | Terim iki yerde KULLANILIYOR ama hiçbir yerde TANIMLI değil: D:57-58 (`tekil` → "tekil-kaynaklı" mı "muhtemel-uydurma" mı) ve S:68-70 (`ekle` tekil istisnası — ifade S:69/70 satır sonunda bölünmüştür: *"VE güçlü / kaynaklıysa"*). Ölçüt yokken ayrım yargısal kalır. |
| 11 | **K-124** — kanıt yeterliliği eşiği | **KISMİ** | S:65-67 pozitif kanıt satırını ZORUNLU kılar (bu doğru), ama **eşik** yok: normal bilgi için ≥1 doğrulanmış kaynaklı kanıt · mevzuat/güvenlikte ek olarak iki denetçi mutabakatı — yazılı değil. |
| 12 | **K-126** — tek-kaynak istisnası | **KISMİ** | S:68-70 istisnayı ("tekil … güçlü kaynaklıysa gerekçeli alınabilir") tarif eder ama **kesin sözleşmesi** yok: (1) kaynağın resmî olması (K-123 ölçütü) + (2) en az bir denetçinin **canlı URL doğrulaması** koşulları birlikte yazılı değil. |
| 13 | **K-02/K-113** — `video_kodlar` iki alt **LİSTE** (`hareket` · `sahne`) | **KISMİ** | T:96-102 iki alt listeyi zaten ister (6a hareket ≥5 · 6b sahne ≥5) — bu ayak **VAR**. Eksik olan: nihai alan adları hiçbir dosyada bağlanmamış (S:102-104 açıkça *"nihai alan adları spec'te, K2 kararıyla"* diye erteler), S:110 çıktı JSON şemasında `video_kodlar` **düz** görünür, ve iki alt yapının **LİSTE** olduğu (tek cümle değil) hiçbir yerde yazılı değil. K-113 (boş havuz → mevcut listeye düşüş) sözleşmede yok — ama o **kod tarafı** hükmüdür, sözleşme kalemi değildir. |

### Adım 1 sayımı

**VAR: 0 · KISMİ: 4 (7 · 11 · 12 · 13) · EKSİK: 9 (1 · 2 · 3 · 4 · 5 · 6 · 8 · 9 · 10).**

### Adım 1'de bilinçli olarak DOKUNULMAYACAK bulunan bir yer (dürüst kayıt)

`_SABLON.md:53-55` (fix turu 1 sonrası aynı metin **T:73-75**) brief katmanının önem
sırasını yazar: *"(1) sektöre özgülük, (2) kaynak sayısı
ve gücü, (3) Türkiye yerelliği"*. Bu **K-121'in kapsamı DEĞİLDİR** ve düzeltilmeyecektir. Kanonik
gerekçe — spec girdisi (K-121 bölümü): *"Önem sırasının iki katmanda farklı olması çelişki
değildir… Yukarıdaki açık karar **yalnız kırpma katmanının sırasını** ilgilendirir."* Tek bir
araştırma koşusu üç aracın mutabakatını göremez; bu yüzden brief katmanının ikinci ölçütü
"kaynak sayısı ve gücü", kırpma katmanınınki "mutabakat gücü"dür. Sweep bu satırı kalem
saymamıştır.

---

## Adım 3 — SONRA ölçümü (aynı 13 kalem, düzeltmeler yazıldıktan sonra)

Ölçüm 2026-08-30'da koşuldu; **fix turu 1'den sonra (F1-F4 sözleşme düzeltmeleri) tüm
satır aralıkları YENİDEN TÜRETİLDİ.** Aralıklar aşağıdaki dosyaların O ANKİ hâline aittir:
`_SABLON.md` **216** · `hakem-denetci-gorevi.md` **141** · `hakem-sentez-gorevi.md` **248**
satır. Kısaltmalar: **S** = sentez · **D** = denetçi · **T** = şablon.

| # | Kalem | Durum | İniş yeri (dosya:satır) |
|---|---|---|---|
| 1 | K-03 yansıması | **VAR** | S:215-227 — "POLİTİKA UYGULANIR — açık soruya DÜŞÜRME" + kapanışın istediği **beş adım** (a) algıla · (b) paket türü üstün, kategori korunur · (c) `tur` alanını paketin değeriyle doldur · (d) decision_log'a yaz · (e) açık soru olarak sunma. Kapsam darlığı (mevzuat/kapsam çatışmaları etkilenmez) S:225-227'de. |
| 2 | Kök sektör rehberi | **VAR** | S:53-58 — GİRDİLER listesine **EK-K = markanın kök sektörünün `SECTOR_GUIDANCE` metni** olarak eklendi; nüans kaybı kontrolü ve "yan yana basılmaz" sınırı da yazıldı. |
| 3 | `[kopya-şüphesi]` tüketim satırı | **VAR** | S:117-123 — bayrak artık ADIM 2 "Kurallar" bloğunda tüketiliyor: değişmeden giremez · soyutlanarak uyarlanabilir · soyutlanamıyorsa alınmaz. |
| 4 | Rol hükmü (K-22=A) | **VAR** | S:27-41 — "Karar mercii DEĞİLSİN — ADAY DEĞİŞİKLİK SETİ ÜRETİCİSİSİN"; kanonik sıra `sentez → motor → draft` ve DB'ye yazmama hükmü. **Kardeş siteler süpürüldü:** S:199 çıktı başlığı (`DRAFT PAKET` → `ADAY PAKET`) ve S:243-248 kapanış paragrafı — ikisi de sentezi doğrudan `draft` yazıcısı gösteriyordu. |
| 5 | URL örneklem satır sayısı | **VAR** | D:125-133 — "kaynak başına 3 satır… denetime giren kaynak sayısı × 3 (3→9, 2→6)"; bölüm başında sayının beyanı zorunlu; ortam kısıtı dalı korundu. **Fix turu 1:** "iki kaynak elendiyse → 3" dalı KALDIRILDI — K-127 (asgari kaynak tabanı 2) gereği o durumda koşu durur, örneklem hiç doldurulmaz (D:127-130). |
| 6 | Kanal anahtar uzayı KAPALI | **VAR — üç iniş yerinin üçü de** | **T:54-72** · **S:124-151** · **D:89-98**. Üçünde de dört anahtar aynen kod tarafındaki yazımla: `whatsapp_hatti` · `fiziksel_magaza` · `randevu_sistemi` · `eticaret_sitesi` (`sector_packages.CHANNEL_KEYS` ile birebir). T'ye ayrıca biçim kuralı (T:214-216), D'ye "dördüne oturmuyorsa etiketi kaldır" dalı (D:95-98). **Fix turu 1:** T:63-72'deki geri-düşüş yolu her yüzeyde uygulanabilir hâle getirildi (gerekçe yuvası olmayan alanlar için Bölüm D — EK BULGULAR); S:135-151'deki ayraç kuralı paket genelinden bayrağa + CTA yüzeylerine daraltıldı. |
| 7 | K-120 `içerik-önerilmez` | **VAR** | T:155-160 (`anma` dalı: içerik önermeme seçeneği; `içerik-önerilmez` bir tür etiketi DEĞİLDİR, tür kümesi dörtte kapalı kalır) · **T:175-183** (ADIM 3'ün altında BİLİNÇLİ BOŞ muafiyeti: dört başlığın hepsine aynı değer; alt sınırlar o dönem için uygulanmaz; serbest cümle kabul edilmez) · T:212-213 (yazım kuralı). Kod tarafıyla birebir: `sector_packages.DELIBERATELY_EMPTY == "içerik-önerilmez"`, `_require_text` onu geçerli sayar. |
| 8 | K-121 altılı kırpma sırası | **VAR** | S:179-188 — mevzuat/güvenlik 1., doğrulanmış sektöre özgü 2., 3-3 → 2-3 → tek güçlü kaynak → genel-geçer/zayıf. Terk edilen üçlü sıra kaldırıldı; katman ayrımı ("brief katmanının sırası ayrıdır") S:187-188'de. |
| 9 | K-122 churn koruması | **VAR** | S:158-165 — kırpmanın ve `cikar` kararının SONUCUNA konan kısıt olarak; sıralama ölçütü olmadığı açıkça belirtildi. |
| 10 | K-123 "güçlü kaynak" ölçütü | **VAR (çekirdek — kapsam sınırı 4. dürüstlük kaydında)** | D:64-73 — iki koşul BİRLİKTE: (1) kaynağın aslı olması (resmî/birincil; aktaran değil) + (2) tarihli güncellik. Sentez tarafı ölçüte atıfla bağlandı (S:101-102) — **tek tanım, tek yer**. |
| 11 | K-124 kanıt yeterliliği eşiği | **VAR** | S:92-98 — normal bilgide ≥1 doğrulanmış kaynaklı kanıt satırı; mevzuat/güvenlikte ek olarak iki denetçi mutabakatı, yoksa çıkarma yok → açık soru. |
| 12 | K-126 tek-kaynak istisnası | **VAR** | S:103-109 — (1) resmî/birincil kaynak (K-123 ölçütü) VE (2) en az bir denetçinin canlı URL doğrulaması (`DOĞRULANDI`). İki denetçi de açamadıysa istisna işlemez. |
| 13 | K-02/K-113 `video_kodlar` iki alt LİSTE | **VAR** | T:116-126 (nihai adlar `video_kodlar.hareket` / `video_kodlar.sahne`, "İKİSİ DE LİSTEDİR") · S:192-195 (aynı bağ, erteleme cümlesi kaldırıldı) · S:201 (çıktı JSON şeması `video_kodlar{hareket[], sahne[]}`). |

### Adım 3 sayımı — **13/13 VAR**

Kısmi kalan kalem YOKTUR. Aşağıdaki **dört** nokta dürüstlük kaydıdır; kalem eksikliği değildir:

1. **R12(c) satır ölçümü doğrulandı, kaymamıştır.** Kalem 6'nın üç iniş yeri düzeltme
   ÖNCESİNDE tam olarak ekin yazdığı yerlerdeydi: `_SABLON.md:49-51` (madde 49'da başlar,
   `[kanal-bağımlı: X]` sözcüğü 51'dedir) · `hakem-sentez-gorevi.md:78` ·
   `hakem-denetci-gorevi.md:74`. Rapor edilecek bir sapma çıkmadı.
2. **`EK-K` KANONİKTİR — bu turda uydurulmadı.** İlk aramam üç dosyayla sınırlıydı ve
   "eşleşme yok" sonucu verdi; kapsam genişletilince kalemin evi çıktı:
   `docs/specs/2026-07-11-sektor-bilgi-paketi.md:570-574` **EK-K = markanın kök sektörünün
   `SECTOR_GUIDANCE` metni** der ve *"hakem-sentez v1.2 girdi listesinde EK-K henüz yok →
   ilk resmî turdan önce görev dosyasına işlenir, **v1.2→v1.3**"* diye kalemi zaten
   adlandırır; `docs/plans/2026-07-12-sektor-bilgi-paketi.md:1002-1014` (Task 32) aynı
   değişikliği aynı sürüm damgasıyla ister. Sözleşme metni bu tanıma birebir hizalandı
   (`SECTOR_GUIDANCE` adı yazıldı) ve sürüm damgası bağımsız olarak aynı yere düştü:
   **1.2 → 1.3**.
3. **K-113'ün kod ayağı sözleşmeye YAZILMADI.** "Paketin hareket havuzu boşsa bugünkü
   `_MOTION_PROMPTS` listesine düşülür" hükmü çalışma zamanı davranışıdır; araştırmacıya
   ya da hakeme verilecek bir talimat değildir. Sözleşmeye giren ayak, alan adlarının
   bağlanması ve iki alt yapının LİSTE olmasıdır (kalem 13). Kod ayağının evi plan
   Task 11'dir.
4. **Kalem 10 ÇEKİRDEĞİ taşır, "tam metni" DEĞİL — ve bu bilinçlidir.** Spec girdisi
   K-123'ün karar kartında (satır 2598) ölçüt için **dört boyut** sayar: resmî/birincil
   kaynak önceliği · **bağımsız kaynak sayısı** · güncellik · **Türkiye yerelliği ağırlığı**.
   Kapanış (spec satır 811-814) bunlardan yalnız **ikisini** bağlar — *"çekirdek: kaynağın
   aslı (resmî/birincil — aktaran değil) + tarihli güncellik"* — ve kalanı *"tam metin
   sözleşme revizyonunda (teknik iş kalemi)"* diye bırakır. Sözleşmeye **yalnız kapanmış
   çekirdek** yazıldı; bağımsız kaynak sayısı ve yerellik ağırlığı **yazılmadı**, çünkü
   hiçbir kapanış onları bağlamıyor — yazmak yeni karar açmak olurdu. Kalemin "VAR"ı bu
   yüzden *kapanmış hükmün tamamı yansıdı* demektir, *ölçüt her boyutuyla tanımlandı*
   demek DEĞİLDİR. Kalan iki boyutun kapanışı ayrı bir karar kalemidir ve bu turda
   **açılmamıştır**; açılırsa evi K-123'ün kendi karar kartıdır.

### Adım 2'de dokunulan ek yer (kalem sayımına girmez, ama diff'te görünür)

Üç dosyanın da başlık yorumundaki **sürüm satırı** güncellendi. Bu, K-03 kapanışının
biçim şartıdır — spec girdisi: *"Yürürlükteki sözleşmede sessiz değişiklik yapılmaz —
düzeltme sürümlü bir supersession kaydıyla işlenir (mevcut sürüm arşivlenir, yeni sürüm
K-03 atfını taşır)."* Sürümler: S `1.2 → 1.3` · D `1.1 → 1.2` · T (numarasız) son
güncelleme `2026-07-07 → 2026-08-30`. Önceki sürümler dosya kopyasıyla değil, deponun
git tarihiyle arşivlenir; üç dosya da bunu commit `b356033` diye adıyla söyler.

### R1 — koşu klasörü commit yolunun kapatılması

`/root/otomaix-sosyal-medya-arastirmasi/.gitignore` mevcut tek satırının ALTINA `kosu/`
eklendi (dosya sıfırdan yazılmadı). Kanıt testi `test_external_repo_gitignores_run_folder`
(Sahip: Task 2) bu satırı gerçek dosyada ölçer.
