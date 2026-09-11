"""`brief-doctor` — araştırma çıktısının MEKANİK girdi kapısı (Plan 2 Task 7).

Kapı, üç araştırma çıktısı geldikten sonra ve denetim adımından ÖNCE koşar; dil
modeline hiçbir iş verilmez (spec §8.3(a), spec-input §7.3). Çıktısı denetim
görevinin ekidir: elenen kaynak denetim dışı kalır, notla geçen kaynağın notlarını
denetçi dikkate alır.

**Bugün ELEME üreten kontrol kümesi BOŞTUR — ve bu bir kaza değil, ölçülmüş bir
hâldir.** Adet alt sınırları (cta ≥5 · kanca ≥3 · görsel kod ≥20 · video kodu ≥10 ·
dönem ≥6; dönem başına kanca ≥2 · cta ≥2 · gorsel_vurgu ≥5) **ölçülmemiş sözleşme
kurallarıdır**, ölçülmüş eşik değil (spec-input §7.3 tablosu, "Ölçülmüş eşik değil,
tasarım kararıdır"). İlke 9 uyum hükmü (spec §8.3, bu spec bağlar) bunları tek başına
eleme kapısı yapmayı YASAKLAR: K-88 (hangi kontrol eler, hangisi not düşer) kapanana
kadar varsayılan davranış `notlu-gecti`dir. Sözleşmenin bugün seviyesini AÇIKÇA yazdığı
tek kontrol "40+ kelime alıntı"dır ve o da **not**tur. `eleme` seviyesi bu yüzden TİPTE
vardır ama hiçbir kontrol tarafından ÜRETİLMEZ; K-88 kapandığında ilgili `Check`'in
`seviye` alanı değişir, ikinci bir mekanizma yazılmaz.

**`CHECKS` DONDURULMUŞ demettir (K-89).** Kontrol kümesinin sabitlenmesi açık bir
karardır; plan bunu demeti dondurarak çözer — kontrol eklemek/çıkarmak sözleşme
revizyonu ister, kaçak bir `append` değil. Küme spec-input §7.3'ün "Kontrol kümesi"
tablosunun DOKUZ satırından SEKİZİNDEN türer (`KONTROL_AILELERI`); dokuzuncusunun
neden dışarıda kaldığı `DISLANAN_KONTROL_GEREKCESI`'nde yazılıdır.

**K-127 = 2 (Eray, 2026-08-23).** `gate_round` bir KAYNAK-SAYISI kapısıdır, içerik
eşiği değil: geçerli kaynak sayısı 2'nin altına düşerse koşu durur ve yöneticiye
bildirilir (mutabakatın mümkün olduğu en küçük sayı — tek kaynakla denetim `tekil`
sınıfından başka bir şey üretemez). **Sayım birimi KİMLİKTİR, rapor değil:** aynı
kaynağın iki raporu iki bağımsız kaynak yerine geçmez. Bu yüzden `kaynak_adi`
zorunludur (varsayılansız, boş olamaz) — plan 950 yazımından bilinçli SAPMA, gerekçesi
`DoctorReport` docstring'inde ölçümüyle yazılıdır.

**Kimlik ÇAĞIRANIN YAZDIĞI METİN DEĞİL, kanonik bir kuraldan TÜRER.** Adı zorunlu
kılmak yetmedi: ölçüldü ki takma adlar (`" KAYNAK-1 "` · `"kaynak-1"` ·
`"a/../KAYNAK-1"` · NFD yazımı · `"KAYNAK-1.md"`) tek kaynağı beş eksende birden İKİ
bağımsız kaynak gibi gösteriyordu. Kapatma o eksenleri tek tek normalleştiren bir
liste DEĞİLDİR: `kanonik_kaynak_kimligi` kimliği TEK kuralla üretir ve hem
`DoctorReport.__post_init__` hem `_kimlik_bolumlemesi` onu çağırır. Yazımla
görülemeyen ikinci eksen — aynı metnin İKİ FARKLI adla verilmesi — `run`'ın ürettiği
kanonik içerik özetiyle (`identity.canonical_sha`) kapanır. İki ayak birlikte
raporlar üstünde geçişli bir DENKLİK bağıntısı kurar; birim yine kimliktir.
İçerik ayağı İSTEĞE BAĞLI DEĞİLDİR: ölçüldü ki `run`'ı atlayıp doğrudan kurulan
iki özetsiz rapor `dur=False, gecerli=2` veriyordu — kimliğin içerik ayağı
sessizce düşüyor ve tek kaynak K-127 tabanını geçiyordu. Kapatma fail-closed'dır
(`_kimlik_kapiya_uygun`): özeti olmayan kimlik SAYILMAZ ve bildirimde ADIYLA
söylenir. Meşru hâl uydurulmaz — `elendi` raporları zaten sayıma girmez.

**Bozuk hâl temsil edilemez.** `DoctorReport` ve `RoundGate` yapısal değişmezlerini
`__post_init__`'te zorlar (emsal `sector_pipeline/contracts.py::ContractPin`): rapor
kendi bulgularıyla çelişemez (`sonuc` onlardan TÜRER, bulgular doğru koleksiyonda ve
doğru seviyededir) ve `RoundGate`'in `gecerli`/`elenen`/`dur`/`taban` alanları
`raporlar`'ın fonksiyonudur. Kural gövdeye GÖMÜLMEZ, `_rapor_ihlalleri` ve
`_gate_ihlalleri` fonksiyonlarında yaşar — mutasyon kolu kapıyı sökebilsin diye.

**K-120.** `anma` dalında bilinçli boşluğun resmî temsili AYNEN `içerik-önerilmez`
değeridir: doluluk kontrolü onu eksik alan saymaz ve o dönem için alt sınır denetimi
uygulanmaz. Serbest cümleyle anlatılmış boşluk ("yok", "-") bu muafiyeti ALMAZ —
sözleşme onları boş alan sayar.

**Değişmezlik.** `DoctorReport` Task 9 paketleyicisine, `RoundGate` Task 12 motorunun
`EngineInputs`'ına gider. `EngineInputs.__post_init__` yalnız DÖRT alanı
`identity.donmus`'tan geçirir (`aktif_paket` · `aktif_birimler` ·
`son_turlarin_cikarmalari` · `takvim_anahtarlari`); `mekanik_eleme` o listede
DEĞİLDİR. Bu yüzden buradaki tipler KENDİLİĞİNDEN değişmezdir. `identity.donmus`
ÇAĞRILMAZ ve çağrılmamalıdır: koleksiyonların öğeleri donmuş veri sınıflarıdır ve
`donmus`'un beş kurallı kapalı kümesi onları kural 5 ile DÜŞÜRÜR
(`identity.donmus` docstring'i bu durumu adıyla tarif eder: *"öğeleri donmuş dataclass
olan alanlar `tuple(...)` kopyası + tip kontrolüyle korunur, `donmus`'a VERİLMEZ"*).
İkinci bir normalizasyon kuralı YAZILMAZ.

**Yüzey ayrımı.** Bu modülün taradığı şey ARAŞTIRMA RAPORU METNİDİR (`_SABLON.md`
çıktı biçimi), veri tabanına yazılan `content` nesnesi değil. İki yüzeyin alan
listeleri örtüşür ama AYNI DEĞİLDİR (ör. `gorsel_kodlar` raporda madde madde bir
listedir, damıtılmış `content`'te düz metindir; `ozel_gun` yuvalarında rapor `tur`
etiketini gerekçe tablosunda taşır). Bu yüzden sabitler `sector_content_schema`'dan
İTHAL EDİLMEZ — o modül ikinci yüzeyin kapısıdır ve buradan tüketilseydi iki sözleşme
tek sabit kümesine sıkışırdı.

**Sözleşmenin DİLBİLGİSİ ölçülür, yalnız varlığı değil — VE HER İÇ İÇE DÜZEYDE.**
Koleksiyonları sözlüğe koymak TEKRARI ve SIRAYI kaybettirir; "var mı" sorusu dört biçimi
birden göremez — tekrar (aynı bölüm/alan/dönem ikinci kez), sıra (sözleşmenin sırası
dışında), boşluk (başlık var içerik yok) ve tablo şekli (ayıraçtan sonraki HERHANGİ bir
satır tablo sayılıyordu). Kurtarma tur 1'de yalnız BÖLÜM ve ALAN düzeyinde yapılmıştı ve
ölçüldü ki dönem kimliği tekrarı, video havuzu bloğunun ikinci kez yazılması ve tekrar
eden Bölüm C eşleme satırı hâlâ `gecti / 0 not` veriyordu. Düzey listesi artık belgenin
KENDİ içerme modelinden türer ve TEK yerde yaşar (`_ic_ice_izler`): bölüm → Bölüm A alanı
→ alan maddesi · video havuzu → havuz maddesi · Bölüm B dönemi → dönem yuvası → yuva
maddesi · Bölüm C eşleme satırı. Sabit kümelerde SIRA da ölçülür; açık kümelerde
(madde · dönem · eşleme satırı) yalnız TEKRAR ölçülür. **Gerekçe tur 3'te DÜZELTİLDİ,
davranış DEĞİŞMEDİ:** sözleşme o düzeylerde sıra dayatMIYOR değil — `_SABLON.md` satır
73-75 her listede ÖNEM SIRASI dayatır (sektöre özgülük → kaynak sayısı ve gücü → Türkiye
yerelliği). Ama önem SEMANTİK bir yargıdır ve mekanik kapı doğrulayamaz; ölçüldü ki iki
çağrı kalıbı takas edildiğinde rapor `gecti / 0 not` verir. Uydurulmuş bir sıra kuralı
gerçek çıktıyı gürültüye boğardı, bu yüzden YAZILMAZ ve sınır artık kapsam beyanında
SUNULUR (docstring sunum değildir).

**Sayıya dayalı her eşik ESSİZ DOĞRULANMIŞ varlığı sayar.** Ham `len(...)` tekrarı ve
serbest boşluk ifadesini de sayar: "5 CTA kalıbı" aynı satırın beş kopyasıyla, ">=6 dönem"
aynı dönemin iki kez yazılmasıyla sağlanabiliyordu. Alt sınırlar bu yüzden
`_Yuva.essiz_maddeler` ve `_essiz_donem_sayisi` üstünden okur.

Dilbilgisi bilerek DAR TUTULMAMIŞTIR: tanınmayan bir başlık iz bırakmaz ve ihlal
sayılmaz — yanlış pozitif üretip gerçek araştırma çıktısını gürültüye boğmasın diye. Bölüm
B'deki gerekçe tablosunda ise bu disiplin ÜÇ TUR boyunca fail-open dal doğurdu: ayıraçtan
sonraki her `|` satırını gerekçe malzemesi saymak bir dönem bloğuna konan meşru ölçüm
tablosundan DÖRT uydurma not üretiyordu; onu kapatan "dönemlerden ÖNCEKİ İLK BİTİŞİK
tablo" kuralının önüne konan bir yem gerçek tabloyu gizledi; onu kapatan "KANONİK başlık
taşıyan adayı seç" kuralı da ÖLÇÜLDÜ ve kandırıldı — gerçek tablonun başlığı jenerik
olduğunda önüne konan kanonik başlıklı bir yem TEK aday oluyor ve gerçek tabloyu tamamen
susturuyordu (ölçüldü: `8 not → 0 not`). Ortak desen: her tur bir SEÇİM sezgiseli kurdu ve
her sezgisel kendi kalıbına uyan bir yemle kandırıldı. Dördüncü bir sezgisel KURULMADI —
seçim BIRAKILDI: dönem bloklarından ÖNCE gelen BÜTÜN tablolar denetlenir, hiçbiri sessizce
atılmaz, birden çoksa belirsizlik NOTU düşer. Kanonik başlık artık seçmez, yalnız NOT
besler. Bedeli bilinçle kabul edildi: dönemlerden önce konmuş meşru ve alakasız bir tablo
artık NOT üretir — bugün hiçbir kontrol elemediği için maliyet gürültüdür, kaynak kaybı
değil, ve not sessiz değildir. Korunan kazanım: dönem bölgesinde duran tablolar denetime
GİRMEZ. Bölgenin SINIRI tur 5'te DÜZELTİLDİ: dönem bloğu BAŞLIĞIYLA başlar, ilk yuvasıyla
değil (`_ilk_donem_baslangici`). Önceki sınır ilk yuvadaydı ve başlık ile ilk yuva ARASINA
konan meşru bir tablo hâlâ "dönem öncesi" sayılıyordu — ölçüldü (46579a1 vs 7075658, aynı
belge): `0 not → 4 not`.

**Tur 6 — altıncı KURAL yazılmadı, bir DEĞİŞMEZ kondu.** Beş turun beşi de bir SEÇİM ya da
SINIR kuralıydı ve her biri yeni bir BİLEŞİMLE kandırıldı; kural yazmak bu eksende işlemedi.
Kapanış artık bir özelliktir ve hangi sınır kuralı yürürlükte olursa olsun geçerlidir:
**bir belgeye tablo EKLEMEK, o belgenin zaten ürettiği notları KALDIRAMAZ**
(`kap_iddiasi_mi` başlığı). Yapısal ayağı `_gerekce_tablosu`'nun
MONOTONLUĞUDUR — karar blok BAŞINA verilir, bir bloğun denetime girip girmediği YALNIZ
kendi konumuna bakar. Kandıran şey v4'ün fail-open geri dönüşüydü ("dönem-öncesi blok
yoksa HEPSİNİ denetle"): dönem-öncesi TEK bir yem eklemek geri dönüşü devreden çıkarıyor
ve dönem-sonrası gerçek tablonun SEKİZ notunu birden düşürüyordu (ölçüldü: `9 not → 0
not`, 24 bileşimin 4'ünde). Geri dönüş KALDIRILDI. Değişmezin istisnası MUTLAK DEĞİL ama
İLKELİDİR: bir ekleme yalnız KENDİ VARLIĞININ yanlışladığı YOKLUK iddialarını düşürebilir
("kapta içerik yok" · "gerekli yerde tablo yok"); bir BLOĞA ait iddialar (satırı · sütunu ·
başlığı) dokunulmazdır. Ölçülmüş bedel: dönem bölgesinde kalan BOZUK bir tablo artık
satır/sütun denetimine hiç girmez, yerine iki küme düzeyi notu düşer.

**Tur 7 — değişmezin İKİ ayağı da kendi tanımına göre kapandı.** Tur 6'nın
değişmezi kendi ilan ettiği kapsam içinde İHLAL EDİLİYORDU: ilk dönemin
`mesaj_ekseni` yuvası boşaltılınca rapor `notlu-gecti / 1 not`, AYNI yuvaya
bağımsız iki sütunlu bir markdown tablosu eklenince `gecti / 0 not` veriyordu —
yani bir tablo EKLEMEK, muaf OLMAYAN bir notu kaldırıyordu. İki kök birden
düzeltildi. (a) **Sınıflandırma YAPISAL oldu:** muafiyet mesaj ÖNEKİ listesiyle
tanımlanıyordu ve bu bağ iki yönde de ölçüldü — metni değişen bir mesaj sınıf
değiştiriyor (15 notun 1 KAP iddiası olan hâli 0'a düşüyor), bir önekle
başlayacak biçimde yeniden yazılan BLOK notu ise sessizce muaf oluyordu. Artık
her `Bulgu` kendi `kategori`sini ÜRETİLDİĞİ yerden taşır (`_Mesaj` · `_kap`) ve
`kap_iddiasi_mi` yalnız o alanı okur; beyan edilmeyen yol fail-closed olarak
DOKUNULMAZDIR. Önek listesi bir üretim yolunu — Bölüm C eşleme kabının yokluk
iddiasını — KAÇIRIYORDU; yapısal tarama onu buldu. (b) **Doluluk kontrolü
SÖZLEŞME BİÇİMİNİ sayar:** `_sozlesme_bicimli` yalnız sözleşmenin tanıdığı üç
biçimi (düz yazı satırı · madde işaretli satır · resmî `içerik-önerilmez`)
içerik sayar; markdown tablosu ve yatay çizgi bir KABI DOLDURMAZ. Aşırı
sıkılaştırma bilinçle yapılmadı — hangi kabın hangi biçimi isteyeceği
DAYATILMAZ.

**Tur 8 — doluluk artık ÇİT-FARKINDADIR, ve envanterin kendisi bir TRIPWIRE.**
Tur 7'nin kuralı satırı TEK TEK değerlendiriyordu ve bir kod bloğu satır-tek-tek
GÖRÜLEMEZ: çıplak ` ``` ` ayıracı sözcüksüz olduğu için eleniyordu ama çitin
İÇİNDEKİ `print(42)` satırı "sözcük içeriyor" diye yuvayı DOLDURUYORDU (ölçüldü:
`notlu-gecti / 1 not` → `gecti / 0 not`; kapanmamış çit de aynı). Kapatma satır
dizisi üstünde yapılır (`_citsiz_satirlar`): DİLSİZ bir çitin açıcısı, gövdesi ve
eşleşen kapatıcısı doluluk sayımından ÇIKARILIR, kapanmamış çit FAIL-CLOSED
olarak (tur 11'den beri BELGE sonuna kadar) düşer. DİLLİ çit (` ```python `) ·
blockquote · HTML
bloğu ilan edilmiş AÇIK kalemlerdir ve DOKUNULMADI — gerçek çıktıda meşru
kullanımları olabilir, daraltmanın yanlış-pozitif maliyeti ÖLÇÜLMEDİ. Aynı turda
envanterin kendi bayatlaması kapatıldı: açık biçimler `ACIK_BLOK_BICIMLERI`'nde
TEK yerde yaşar, kapsam beyanı metnini oradan ÜRETİR ve test her kalemin
GERÇEKTEN bir boşluk notunu kaldırdığını ölçer — biri kapanırsa test kırılır. Bu
görevde beyan BEŞ kez bayatlamıştı.

**Tur 9 — kural TEK yerde, ama KARDEŞ SİTELER süpürüldü.** Tur 8 çit kuralını
kurdu ve yalnız DOLULUK yoluna bağladı; AYNI yuva içeriğini okuyan kardeş yollar
çit-farkında DEĞİLDİ. Ölçüldü: `cta_kaliplari` boşaltılınca rapor İKİ not
veriyordu (`alanı boş` + `0 madde taşıyor, sözleşme alt sınırı 5`), AYNI alana
DİLSİZ çit İÇİNDE beş madde konunca alt sınır notu SUSUYORDU. **Bu kaybın
görülmesi bir yöntem dersidir:** not SAYISI 2 → 3 ARTMIŞTI (çitin ürettiği
uydurma bir biçim notu yüzünden) ve sayı karşılaştırması kapanışı YANLIŞ
gösteriyordu; kayıp ancak mesaj KÜMELERİ farkıyla göründü. Süpürme kavramdan
türetildi (belgenin kendi içerme modeli × çitin boyutları) ve İKİ demette
sayıldı: `CIT_KURALI_KAPSAMI` (bugün SEKİZ yol — doluluk · adet sayımı · madde
tekrar izi · bölüm boşluğu · Bölüm C eşleme satırı · Bölüm B gerekçe tablosu
tanıma · ayrı madde işareti · tur 11'de eklenen BAŞLIK VE BÖLÜM TANIMA) ve
`CIT_KURALI_DISINDA` (bugün ALTI yol — hepsi HAM METİN tarar ya da fail-closed
tercihtir; ölçüt: kontrol SÖZLEŞME-BİÇİMLİ içerik mi arıyor, yoksa ham metin mi). Körlemesine eleme YAPILMADI: bir çitin içindeki İngilizce
metin gerçekten İngilizcedir, çite alınmış 40 kelimelik alıntı hâlâ alıntıdır ve
K-120 muafiyeti çite saklanmış içerikle ALINAMAZ (üçü de ölçüldü). Kural TEK
evde yaşar (`_cit_maskesi`); `_citsiz_satirlar` onun süzgeç yüzeyidir ve konum
koruması gereken yol maskeyi doğrudan okur (tur 11'de maske SATIRIN KENDİSİNE
taşındı — `_Satir.cit_icinde`).

**Tur 10 — çit tanıma BAĞLAMDAN BAĞIMSIZ.** Kural tek evdeydi ve süpürülmüş
yollar onu
çağırıyordu, ama evin kendi ekseni (dil × gövde × kapanış) GİRİNTİ/BAĞLAM
boyutunu TAŞIMIYORDU. Ölçüldü, aynı yuva, mesaj KÜMESİ farkıyla: `- ``` ` +
`  print(42)` + `  ``` ` bir notu KALDIRIYORDU. Sebep girinti DEĞİLDİ — ayıraç
deseninin baştaki boşluk yutan öneki girintiyi zaten alıyordu ve 2/4 boşluk girintili çit notu KORUYORDU; açık olan
MADDE BAĞLAMIYDI: `- ``` ` açıcı sayılmadığı için gövde MASKESİZ kalıp kabı
DOLDURUYOR, kapatıcı ise yeni bir açıcı sanılıyordu. Ayıraç deseni bağlamdan
BAĞIMSIZLAŞTIRILDI (`_KOD_CITI_RE`) — tek evde, ikinci ayrıştırıcı YAZILMADAN,
dolayısıyla hepsi aynı anda faydalandı. Kapatıcı eşleşmesi satırın SOLUNA
değil AYIRACIN KENDİSİNE bakar. AŞIRI SIKILAŞTIRMA YAPILMADI: ayıraç satırın TEK
ANLAMLI İÇERİĞİ olmak zorundadır — `- gerçek bir kalıp` çit değildir ve kabı
DOLDURMAYA devam eder (ölçüldü). Aynı turda eksen İKİ boyutla genişledi (bağlam
`CIT_BAGLAM_BICIMLERI` · ayıraç biçimi `CIT_AYIRAC_BICIMLERI`; envanter TEK
yerde yaşar, beyan ondan ÜRETİLİR ve tripwire her kalemi uçtan uca ÖLÇER) ve
HEDEFLİ mutasyon kolu eklendi: deseni tur 9 hâline döndürmek yalnız iki YENİ
bağlamı kırmızıya düşürür, girinti bağlamları YEŞİL kalır — boyutun gerçekten
ölçtüğünün kanıtı.

**Tur 11 — MASKE AYRIŞTIRMADAN ÖNCE, BİR KEZ, BELGENİN TAMAMI ÜSTÜNDE.** Tur
10'a kadar kural tek evdeydi ama maske HER KULLANIM YERİNDE, bir DİLİM üstünde
yeniden hesaplanıyordu ve ayrıştırma onu hiç görmüyordu. İki ölçülmüş açık:

  (a) **TAM YUVA SAHTECİLİĞİ.** `_bloklara_ayir` başlıkları HAM satırlardan
      tanıyordu. Belgeden TAMAMEN silinen `cta_kaliplari` alanı İKİ not
      veriyordu (`0 madde taşıyor, sözleşme alt sınırı 5` + `alan başlığı Bölüm
      A'da yok`); AYNI belgeye DİLSİZ bir çit içinde sahte `### cta_kaliplari`
      başlığı ve beş madde konunca rapor `gecti / 0 not` oluyordu. Yani VAR
      OLMAYAN bir sözleşme alanı, kod bloğunun içine yazılarak DOLU ve EKSİKSİZ
      gösterilebiliyordu. Bir önceki tur bu yolu "kapsam dışı, fail-closed,
      yalnız NOT EKLER" diye İLAN ETMİŞTİ; ölçüm ilanı YALANLADI ve beyan
      düzeltildi (bu görevde beyan ALTINCI kez bayatladı).
  (b) **KAP GEÇİŞİ.** Bir liste öğesi içinde açılan çit, o öğe bittikten çok
      sonra gelen KÖK düzeyi bir ayıracı kendi kapatıcısı sanıyordu:
      `- ```python` → girintili gövde → kabı bitiren kök paragraf → kökte DİLSİZ
      çit bileşimi, DİLSİZ çitin beş maddesini maskesiz bırakıp hem boş-yuva hem
      alt sınır notunu KALDIRIYORDU. Ayrıca liste işareti kümesi sözleşmenin
      madde kuralından (`-`) türetilmişti; `* ``` ` ve `+ ``` ` birer not
      kaldırıyordu.

Kapatma ÜÇ yama değil TEK yapısal değişikliktir: maske `_maskeli_satirlar`'da
BİR KEZ hesaplanır ve satıra YAPIŞIR (`_Satir`), böylece dilim alan hiçbir yol
onu yeniden hesaplayamaz; liste işaretleri MARKDOWN'ın kendi dilbilgisinden
türer (sözleşmenin madde kuralı ayrı yaşar ve `*` ile yazılmış maddeye NOT
düşmeye devam eder); durum makinesi KAP SONLANMASINI modeller
(`_kapsayici_kirildi`). HAM METİN tarayan yollar (dil kuralı · uzun alıntı ·
gövde dipnotu · tür etiketi · etiket yazımı) maskeyi GÖRMEZ — `_Satir` bir `str`
türevidir ve satır ham kalır; çite alınmış Türkçe harf hâlâ oradadır (ölçüldü).

**Ölçüm sınırları dürüstçe (İlke 9).** Mekanik kapı bir dil modeli değildir; kontroller
sözleşmenin taranabilir yüzeyini ölçer, tamamını değil. Bu sınırlar artık DOCSTRING'DE
SAKLI DEĞİLDİR: `Check.kapsam_sinirlari` demetinde yaşarlar ve `run` onları
`DoctorReport.kapsam_sinirlari`'na taşır — İlke 9'un dördüncü ayağı ölçülmemiş davranış
iddiasının "doğrulanmadı" etiketiyle SUNULMASINI ister, ve docstring sunum değildir.
Beyan bir BULGU değildir: rapor sonucunu bozmaz, temiz kaynak `gecti` kalır.

* Dil kuralı YALNIZ İngilizce yüzeylerde ölçülür (Türkçe'ye özgü harf işareti).
  "Diğer alanların Türkçe olması" mekanik olarak DOĞRULANMADI — sözlük gerektirir.
  Ailenin adı sözleşmedeki ÇİFT yönlü kuralı taşır, ölçüm tek yönlüdür; fark rapora
  yazılır.
* Bölüm/başlık tanıma markdown başlık DÜZEYİNE dayanır: 1-2 düzey başlık bölüm
  sayılır, 3+ düzey bölüm içi kabul edilir. Sözleşme bir markdown düzeyi dayatmaz;
  bu bir mekanik vekildir.
* Boşluk ifadeleri (`_BOSLUK_IFADELERI`) belgelenmiş KÜÇÜK bir kümedir, tüketici
  değildir; kapsama oranı ölçülmemiştir.
* Doluluk yalnız BİÇİM eler, İLGİ ölçmez: sözleşme biçiminde ama alakasız bir düz
  yazı satırı kabı doldurmuş sayılır — anlam yargısı gerektirir, DOĞRULANMADI.
  Elenen markdown yapıları TABLO · yatay çizgi · DİLSİZ kod çiti BLOĞU ile
  SINIRLIDIR; dilli kod çiti, blockquote ve HTML bloğu HÂLÂ kabı doldurur
  (`ACIK_BLOK_BICIMLERI` — envanter tek yerde yaşar ve testi onu sabitler).
  BÖLÜM düzeyindeki boşluk kontrolü TABLO kuralını UYGULAMAZ (sözleşme tabloyu
  Bölüm B gerekçesi ve Bölüm C eşlemesi olarak tanır); ölçüldü, ayrı bir sınıftır.
  ÇİT kuralı ise bölüm düzeyinde de UYGULANIR.
* Çit kuralının KAPSADIĞI ve bilinçle KAPSAMADIĞI yollar `CIT_KURALI_KAPSAMI` /
  `CIT_KURALI_DISINDA` demetlerinde sayılıdır; kapsam beyanı metnini onlardan
  ÜRETİR ve test her kalemi uçtan uca ölçer.
* Gerekçe tablosunda sütun SAYISI ölçülür, sütun başlıklarının ANLAMI değil.
* Bölüm C OLUMLU bir yapısal sözleşme olarak doğrulanır: birebir başlık satırı ·
  sözleşmenin SABİT sütun kümesi · hücre doluluğu · `no` biçimi ve DİZİSİ (kimlik:
  tekrarsız, boşluksuz) · `alan/dönem` kapalı kümesi · `iddia` kelime sınırı ·
  `URL` adres biçimi · `tarih` yazımı · `tek kaynak` kapalı kümesi; ayrıca BÜTÜNLÜK
  (her alan/dönem için en az bir satır). Önceki sürümün ayıraç vekili KALDIRILDI —
  serbest düzyazıdan "bu bir eşleme DEĞİL" sonucunu çıkarmak semantik-negatif bir
  sınıftı ve üç turda yakınsamadı; kök çözüm KODA değil SÖZLEŞMEYE yapıldı (dış depo
  `7964ed6`, sabit sütunlu tablo). Ölçülmeyen İKİ eksen kaldı ve ikisi de anlam
  yargısıdır: bağlantının gerçekten AÇILDIĞI (ağ çağrısı yapılmaz) ve `iddia`
  hücresinin kaynağı gerçekten ÖZETLEDİĞİ. İkisi de denetçi katmanının işidir.
* Gerekçe denetimine giren küme SEÇİLMEZ ve MONOTONdur: dönem bloklarından ÖNCEKİ bütün
  tablolar denetlenir, bir tablo EKLEMEK başka bir tabloyu kümeden ÇIKARAMAZ. Hangisinin
  GERÇEK gerekçe tablosu olduğu DOĞRULANMAZ ve doğrulanmaya ÇALIŞILMAZ. Bölgenin SINIRI
  ilk dönem BAŞLIĞIDIR: bir dönem başlığından SONRA gelen tablo, kanonik başlık taşısa
  bile denetime GİRMEZ — satır/sütun notu VERMEZ; yerine "dönem başlıklarından ÖNCE tablo
  yok" ve "tablo dönemlerden SONRA geliyor" küme notları düşer. **DÜZELTİLMİŞ BEYAN:** bir
  önceki tur bu dalda "tablo SUSTURULMAZ" diyordu ve ÖLÇÜM bunu YALANLADI — fail-open geri
  dönüş yüzünden dönem-öncesi tek bir yem tabloyu tamamen susturuyordu (`9 not → 0 not`).
  Ölçülmüş kalan sınırlar: (a) ilk döneme başlık yazılmamış ama tablonun üstüne alt yazı
  başlığı konmuşsa o alt yazı ilk dönemin başlığı sanılır ve tablo denetim dışında kalır;
  (b) düzey 1-2 bir ara başlık Bölüm B'yi KAPATIR ve o başlıktan sonrası Bölüm B sayılmaz
  (bölüm tanıma markdown düzeyine dayanır) — ikisi de AYRI sınıftır, bu turda kapatılmadı.
* Kaynak KİMLİĞİ yazım takma adlarını (`kanonik_kaynak_kimligi`) ve aynı metnin iki adla
  verilmesini (`icerik_ozeti`) denkler. Özetsiz kimlik artık kapıya UYGUN DEĞİLDİR, ama
  özetin `run` tarafından ÜRETİLDİĞİ doğrulanamaz: biçim zorlanır, KÖKEN zorlanmaz —
  metne sahip olmayan bir çağıran biçimi geçerli bir özet uydurabilir, o eksen
  DOĞRULANMADI.
"""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
import dataclasses
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Callable, Iterable, Sequence

from markdown_it import MarkdownIt

from . import identity

# ─── 1. Kapalı değer kümeleri ───────────────────────────────────────────────

SEVIYE_NOT = "not"
SEVIYE_ELEME = "eleme"
# İKİ seviye, kapalı (spec-input §7.3 "Hatalı girdinin davranışı — iki seviye").
SEVIYELER = (SEVIYE_NOT, SEVIYE_ELEME)

SONUC_GECTI = "gecti"
SONUC_NOTLU_GECTI = "notlu-gecti"
SONUC_ELENDI = "elendi"
# Yazım plan 950'de BAĞLAYICIDIR (ASCII, tireli).
SONUCLAR = (SONUC_GECTI, SONUC_NOTLU_GECTI, SONUC_ELENDI)

# `_SABLON.md` ═══ 5. ÇIKTI FORMATI ═══: beş bölüm, sabit.
BOLUM_HARFLERI = ("A", "B", "C", "D", "E")

# `_SABLON.md` BİÇİM KURALLARI, birinci madde — SIRA sözleşmenin sırasıdır.
TEMEL_ALANLAR = (
    "kapsam",
    "ton_ve_dil",
    "cta_kaliplari",
    "kanca_kaliplari",
    "gorsel_kodlar",
    "video_kodlar",
    "takvim_temalari",
    "yasaklar_ve_hassasiyetler",
)
# Düz metin yazılan iki alan; kalanı madde işaretli liste (BİÇİM KURALLARI md. 3).
METIN_ALANLARI = ("kapsam", "ton_ve_dil")
LISTE_ALANLARI = tuple(ad for ad in TEMEL_ALANLAR if ad not in METIN_ALANLARI)

# `_SABLON.md` ═══ 5. ÇIKTI FORMATI ═══ Bölüm B: "önce seçim/eleme/ekleme
# gerekçeleri tablosu (dönem + sistem anahtarı + karar + tür etiketi + gerekçe),
# sonra dönem dönem dört başlık". SÜTUN SAYISI ve SIRA sözleşmenindir; test onu
# pinden okur. `sistem anahtarı` sütunu 2026-09-11'in ikinci revizyonuyla geldi
# (dış depo `d9dc289`): dönem satırının SİSTEM ANAHTARINA köprüsü BU sütundur —
# Bölüm C dönem adını taşımaya devam eder, anahtar buradan okunur.
GEREKCE_TABLOSU_SUTUNLARI = (
    "dönem",
    "sistem anahtarı",
    "karar",
    "tür etiketi",
    "gerekçe",
)
GEREKCE_DONEM_INDEKSI = GEREKCE_TABLOSU_SUTUNLARI.index("dönem")
GEREKCE_ANAHTAR_INDEKSI = GEREKCE_TABLOSU_SUTUNLARI.index("sistem anahtarı")

# Sözleşme (Bölüm B): *"Aday listesinde olmayan, sektöre özgü eklediğin dönemde
# `—` yaz"*. Bu değer "anahtar YOK" demektir; boş hücre DEĞİLDİR (boş hücre
# ayrı bir ihlaldir — yazılmamış ile bilinçle yok arasındaki fark korunur).
SISTEM_ANAHTARI_YOK = "—"

# Sistem anahtarının BİÇİMİ — `sector_packages.normalize_special_day_key`'in
# ürettiği slug uzayı: küçük harf/rakam öbekleri, tek tire ile ayrılmış. Biçim
# burada yalnız TANINIR; anahtar burada ÜRETİLMEZ (uydurma anahtar yasağı,
# spec §4.4). Üretici tek modüldür ve bu kapı onu çağırmaz.
_SISTEM_ANAHTARI_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# `_SABLON.md` ═══ 4. GÖREV B ═══ ADIM 1 — ADAY TAKVİM tablosu: günlük dildeki
# dönem adı → o dönemin SİSTEM ANAHTARLARI (birden çok anahtar = bayram arifesi
# + günleri). Test bu eşlemeyi pinlenmiş şablonun TABLOSUNDAN okur; burada
# elle yazılı bir liste değil, sözleşmenin kopyasıdır — sözleşme değişip bu
# demet güncellenmezse alarm düşer. Kapı bu eşlemeyi ÜÇ yerde kullanır:
# hücre biçimi (`—` ya da bilinen anahtarlar), aday dönemde AYNEN kopya kuralı,
# ve `CIddia.anahtarlar`'ın kaynağı (dolaylı — kopya doğrulandıysa hücre).
ADAY_TAKVIM_ANAHTARLARI: dict[str, tuple[str, ...]] = {
    "Yılbaşı": ("yilbasi",),
    "Sevgililer Günü": ("sevgililer-gunu",),
    "8 Mart Dünya Kadınlar Günü": ("dunya-kadinlar-gunu",),
    "Ramazan Bayramı": (
        "ramazan-bayrami-arife",
        "ramazan-bayrami-1-gun",
        "ramazan-bayrami-2-gun",
        "ramazan-bayrami-3-gun",
    ),
    "Kurban Bayramı": (
        "kurban-bayrami-arife",
        "kurban-bayrami-1-gun",
        "kurban-bayrami-2-gun",
        "kurban-bayrami-3-gun",
        "kurban-bayrami-4-gun",
    ),
    "Anneler Günü": ("anneler-gunu",),
    "Babalar Günü": ("babalar-gunu",),
    "23 Nisan": ("ulusal-egemenlik-ve-cocuk-bayrami",),
    "19 Mayıs": ("ataturk-u-anma-genclik-ve-spor-bayrami",),
    "30 Ağustos": ("zafer-bayrami",),
    "29 Ekim": ("cumhuriyet-bayrami",),
    "10 Kasım": ("10-kasim-ataturk-u-anma-gunu",),
    "24 Kasım Öğretmenler Günü": ("24-kasim-ogretmenler-gunu",),
    "Kasım indirim dönemi": ("black-friday",),
    "okula dönüş (Eylül)": ("okula-donus",),
}

# Sistemde olup aday listesinde OLMAYAN günler — şablonun tablo altı satırı.
# Sektöre özgü ekleme olarak seçilirse anahtarı buradan gelir.
ADAY_DISI_SISTEM_ANAHTARLARI: tuple[str, ...] = (
    "canakkale-sehitlerini-anma-gunu",
    "demokrasi-ve-mill-birlik-gunu",
    "emek-ve-dayanisma-gunu",
)

SISTEM_ANAHTARLARI: frozenset[str] = frozenset(
    anahtar for anahtarlar in ADAY_TAKVIM_ANAHTARLARI.values() for anahtar in anahtarlar
) | frozenset(ADAY_DISI_SISTEM_ANAHTARLARI)
"""Şablonun tanıdığı BÜTÜN sistem anahtarları — hücre üyeliğinin kapalı kümesi."""

# Gerekçe tablosunun KANONİK BAŞLIK anahtarları — sütun adlarının çekirdek
# sözcükleri. İkinci bir liste YAZILMAZ: küme sözleşmeden okunan sabitin
# TÜREVİDİR ("tür etiketi" → "tür"), böylece sözleşme değişirse tanıma da değişir.
GEREKCE_BASLIK_ANAHTARLARI = tuple(
    sutun.split()[0] for sutun in GEREKCE_TABLOSU_SUTUNLARI
)
# Başlık satırı bu kadar anahtarı taşıyorsa blok gerekçe tablosu ADAYIDIR.
# Eşik TAM eşleşme değildir bilerek: gerçek çıktıda sütun adı kısaltılabilir
# ("tür etiketi" yerine "tür") ve tam eşleşme aramak yanlış-negatif üretirdi.
GEREKCE_BASLIK_ASGARI = 2

# `_SABLON.md` ═══ 5. ÇIKTI FORMATI ═══ Bölüm C: *"SABİT SÜTUNLU TABLO olarak
# yaz, aynen şu başlık satırıyla"*. Sütun ADLARI ve SIRA sözleşmenindir; test
# onu düzyazıdan değil, sözleşmenin BAŞLIK SATIRINDAN okur.
#
# **Neden burada TAM eşleşme aranır, gerekçe tablosunda aranmaz.** İki tablonun
# sözleşmedeki kipi AYNI DEĞİLDİR: Bölüm B'de başlık satırı bir bloğun gerekçe
# tablosu OLUP OLMADIĞINI SEÇMEYE yarar (yanlış-negatif pahalıdır, bu yüzden
# `GEREKCE_BASLIK_ASGARI` eşiği gevşektir); Bölüm C'de sözleşme "aynen" der ve
# başlık satırı kapının OLUMLU sözleşmesidir — hangi hücrenin ne olduğu ona
# dayanır, gevşetilirse sütun anlamı yeniden TAHMİNE düşer.
C_TABLOSU_SUTUNLARI = (
    "no",
    "alan/dönem",
    "iddia",
    "kaynak adı",
    "URL",
    "tarih",
    "tek kaynak",
)
# Hücre KONUMLARI addan TÜRER, elle sayılmaz. Sözleşme 2026-09-11'de başa bir
# sütun (`no`) ekledi ve elle yazılmış her indeks bir kaydırma hatası adayıydı;
# ad→konum türetmesi sözleşme yeniden sıra değiştirdiğinde kendiliğinden uyar.
C_NO_INDEKSI = C_TABLOSU_SUTUNLARI.index("no")
C_ALAN_INDEKSI = C_TABLOSU_SUTUNLARI.index("alan/dönem")
C_URL_INDEKSI = C_TABLOSU_SUTUNLARI.index("URL")
# `no` hücresi: 1'den başlayan ARTAN TAM SAYI, o raporda iddianın KALICI
# kimliği. Biçim burada, DİZİ kuralı `_c_no_dizisi_ihlalleri`'nde ölçülür.
_C_NO_RE = re.compile(r"^[1-9]\d*$")
# Sözleşme `iddia` hücresine ÜST SINIR koyar: "EN FAZLA 15 KELİME". Uydurma
# eşik DEĞİL — sözleşme metninden okunur, testi pinden doğrular.
C_IDDIA_KELIME_UST_SINIRI = 15
# `tek kaynak` hücresi kapalı kümedir (sözleşme: "`evet` ya da `hayır`").
C_TEK_KAYNAK_DEGERLERI = ("evet", "hayır")
# `tarih` hücresi: `YYYY-AA` · `YYYY-AA-GG` · ya da AYNEN `tarih-yok`.
C_TARIH_YOK = "tarih-yok"
_C_TARIH_RE = re.compile(r"^\d{4}-\d{2}(?:-\d{2})?$")

# ─── Ekleme değişmezi: EKLEMEK KALDIRAMAZ ───────────────────────────────────
#
# **Değişmez (kural değil, ÖZELLİK):** bir belgeye tablo EKLEMEK, o belgenin
# zaten ürettiği notları KALDIRAMAZ. Beş tur boyunca bu eksene beş SINIR/SEÇİM
# kuralı yazıldı ve her biri kendi kalıbına uyan yeni bir bileşimle kandırıldı
# (v1 tanıma yok · v2 ilk bitişik tablo · v3 kanonik başlıklı aday · v4 seçimi
# bırak · v5 sınırı ilk dönem başlığına çek). Altıncı kural YAZILMAZ: kapanış
# artık hangi sınır kuralı yürürlükte olursa olsun geçerli olan bir ÖZELLİKTİR
# ve yapısal ayağı `_gerekce_tablosu`'nun MONOTONLUĞUDUR — blok EKLEMEK denetim
# kümesinden blok ÇIKARAMAZ. Fail-open geri dönüş (dönem-öncesi blok yoksa
# HEPSİNİ denetle) tam olarak bu monotonluğu kırıyordu ve ölçüldü: dönem-öncesi
# TEK bir yem eklemek dönem-sonrası gerçek tablonun SEKİZ notunu birden
# düşürüyordu (`9 not → 0 not`).
#
# **İstisna İLKEDEN türer, örnekten DEĞİL.** "Hiçbir not kaybolamaz" YANLIŞ bir
# ifadedir: meşru bir gerekçe tablosu eklemek "gerekçe tablosu YOK" notunu
# HAKLI OLARAK kaldırır. İlke şudur: bir ekleme yalnız KENDİ VARLIĞININ
# YANLIŞLADIĞI iddiaları düşürebilir. Bunlar bir BLOĞA ait değil, KABIN
# bütünü hakkındaki YOKLUK iddialarıdır — "şu kapta içerik yok" ve "gerekli
# yerde tablo yok". Bir bloğun KENDİ içeriği hakkındaki iddialar (satırı ·
# sütunu · başlığı) istisnanın DIŞINDADIR: o blok hâlâ oradadır ve ikinci bir
# blok onu ilgisizleştiremez.
#
# **Tur 7 — istisnanın SINIRI artık YAPISALDIR, metin değil.** Muafiyet bir
# mesaj ÖNEKİ listesiyle tanımlanıyordu; her bulgu artık kendi KATEGORİSİNİ
# üretildiği yerden taşır (`_Mesaj` · `_kap` · `Bulgu.kategori`) ve
# `kap_iddiasi_mi` yalnız o alana bakar. Aynı turda değişmezin İKİNCİ ayağı
# da kapandı: bir markdown TABLOSU sözleşmenin tanıdığı bir içerik biçimi
# DEĞİLDİR (`_sozlesme_bicimli`), dolayısıyla bir kaba tablo eklemek o kabın
# BOŞLUK notunu artık düşüremez.
#
# **Tur 8 — aynı ayağın DİZİ boyutu.** Tablo eklemek düşüremiyordu ama bir
# DİLSİZ KOD ÇİTİ eklemek hâlâ düşürüyordu: çitin GÖVDESİ satır-tek-tek
# bakıldığında sözleşme biçimli görünür. Doluluk sayımı artık çit-farkındadır
# (`_citsiz_satirlar`) ve dilsiz çit bloğu sayımdan çıkarılır. Dilli çit ·
# blockquote · HTML bloğu ilan edilmiş AÇIK kalemdir (`ACIK_BLOK_BICIMLERI`).
#
# **Tur 9 — aynı ayağın KARDEŞ SİTELERİ.** Doluluk çit-farkındaydı ama AYNI
# içeriği okuyan adet sayımı, bölüm boşluğu, Bölüm C eşleme satırı ve Bölüm B
# tablo tanıma DEĞİLDİ: çite konan içerik o yollarda notu KALDIRIYORDU
# (ölçüldü, mesaj KÜMESİ farkıyla — not SAYISI artmıştı). Süpürüldüler;
# kapsam `CIT_KURALI_KAPSAMI` / `CIT_KURALI_DISINDA`'da sayılır.
#
# **Tur 10 — aynı ayağın BAĞLAM boyutu.** Yedi yol da çit-farkındaydı ama çitin
# KENDİSİ bağlam-farkında değildi: bir LİSTE İŞARETİNDEN sonra açılan çit
# (`- ``` `) ayıraç sayılmıyor, gövdesi kabı DOLDURUYORDU. Ayıraç deseni tek
# evde bağlamdan bağımsızlaştırıldı; girinti zaten çalışıyordu (ölçüldü).
#
# **Tur 11 — aynı ayağın YAPISAL boyutu: çit eklemek YUVA UYDURAMAZ.** Sekiz
# yolun hepsi çit-farkındaydı ama AYRIŞTIRMA değildi ve maske her yerde bir
# DİLİM üstünde yeniden hesaplanıyordu. Ölçüldü: DİLSİZ bir çit içine konan
# sahte `### cta_kaliplari` başlığı, belgeden TAMAMEN SİLİNMİŞ bir alanı DOLU
# gösteriyor ve İKİ notu birden KALDIRIYORDU (`notlu-gecti / 2 not` ->
# `gecti / 0 not`). Maske artık ayrıştırmadan ÖNCE, belgenin TAMAMI üstünde bir
# kez hesaplanır ve satıra YAPIŞIR (`_Satir`); ayrıca durum makinesi KAP
# SONLANMASINI modeller ve liste işaretleri markdown'ın kendi kümesinden türer.
#

BOLUM_BOS_MESAJI = (
    "Bölüm {harf} boş — başlık var, içerik yok (beş bölümün hepsi doldurulur)"
)
TABLO_YOK_MESAJI = (
    "Bölüm B'de dönem başlıklarından ÖNCE özel gün seçim/eleme/ekleme "
    f"gerekçeleri tablosu yok ({' + '.join(GEREKCE_TABLOSU_SUTUNLARI)})"
)
TABLO_DONEM_SONRASI_MESAJI = (
    "Gerekçe tablosu dönem başlıklarından SONRA geliyor — sözleşme "
    "ÖNCE tablo, SONRA dönem dönem dört başlık der"
)
# Bulgunun KATEGORİSİ — ekleme değişmezinin istisnası BURADAN okunur.
#
# İki değer, kapalı: bir bulgu ya tek bir BLOĞUN kendi içeriği hakkındadır
# (satırı · sütunu · başlığı — eklemeye karşı DOKUNULMAZ), ya da bir KABIN /
# kümenin BÜTÜNÜ hakkındadır ("var mı" · "kaç tane" · "gerekli yerde bir
# tanesi var mı"). İkincisi eklemeyle meşru olarak değişebilir: kap gerçekten
# değişmiştir. SAYIM taşıyan iddialar ayrıca AZALAMAZ (denetim kümesi monoton
# olduğu için); o ayak `gerekce_donem_oncesi_sayisi` /
# `gerekce_basliksiz_sayisi` üstünden AYRICA ölçülür — istisna "sayı düştü"yü
# örtmesin diye.
#
# **Kategori bulgunun ÜRETİLDİĞİ yerde verilir ve bulgu onu KENDİSİ TAŞIR;
# mesaj METNİNE BAKILMAZ.** Bir önceki tur istisnayı mesaj ÖNEKİ listesiyle
# tanımlıyordu ve o bağın kırılganlığı İKİ yönde de ÖLÇÜLDÜ:
#
#   (a) metin → sınıf: `BOLUM_BOS_MESAJI` metni yeniden yazıldığında aynı
#       bulgunun kategorisi sessizce kaydı (ölçüldü: aynı belgede 15 notun
#       1 KAP iddiası olan hâli, yalnız metin değişince 0 KAP iddiasına düştü);
#   (b) sınıf → metin: bir BLOK notu kazara bir önekle başlayacak biçimde
#       yeniden yazıldığında sessizce MUAF oldu (ölçüldü: "Bölüm B'de dönem
#       başlıklarından ÖNCE gelen tabloda 3 sütunlu satır var" → `True`).
#
# Bu oturumda mesaj metinleri iki kez yeniden yazıldı ve öneklerden biri
# güncellenmek ZORUNDA kaldı — bağ kurgusal değil ölçülmüş bir kırılganlıktı
# ve KALDIRILDI. İkinci bir metin-eşleştirme kuralı YAZILMAZ.
KATEGORI_BLOGA_AIT = "bloga-ait"
KATEGORI_KAP_IDDIASI = "kap-iddiasi"
KATEGORILER = (KATEGORI_BLOGA_AIT, KATEGORI_KAP_IDDIASI)


@dataclass(frozen=True)
class _Mesaj:
    """Bir kontrolün ürettiği tek bulgu: METİN + KATEGORİ.

    Varsayılan FAIL-CLOSED'dır (`bloga-ait`): kategorisini BEYAN ETMEYEN her
    üretim yolu dokunulmaz sayılır, yani ekleme değişmezi onu KORUR. Muafiyet
    ancak bilinçli bir `_kap(...)` çağrısıyla verilir — sızıntı yönü kapalıdır.
    Kontroller düz `str` de dönebilir; `run` onu bu varsayılanla sarar.
    """

    metin: str
    kategori: str = KATEGORI_BLOGA_AIT

    def __post_init__(self) -> None:
        if self.kategori not in KATEGORILER:
            raise ValueError(
                f"_Mesaj kategorisi kapalı kümenin dışında: {self.kategori!r} "
                f"— {list(KATEGORILER)}"
            )


def _kap(metin: str) -> _Mesaj:
    """KAP/KÜME iddiası olarak işaretler: yokluk · sayım · konum.

    Çağrı SÖZLEŞMEDİR: bir mesajı `_kap`'a sarmak, o iddianın tek bir BLOK
    hakkında DEĞİL kabın bütünü hakkında olduğunu BEYAN etmektir. Sarılmayan
    her mesaj eklemeye karşı DOKUNULMAZDIR.
    """
    return _Mesaj(metin, KATEGORI_KAP_IDDIASI)


def kap_iddiasi_mi(bulgu: "Bulgu") -> bool:
    """Bulgu bir KABIN bütünü hakkında mı (yokluk · sayım · konum)?

    Ekleme değişmezinin İLKELİ istisnası budur: bir ekleme yalnız KENDİ
    VARLIĞININ yanlışladığı KAP iddialarını değiştirebilir. Bir bloğun KENDİ
    içeriği hakkındaki iddialar (satırı · sütunu) `False` döner ve eklemeye
    karşı DOKUNULMAZDIR. Cevap bulgunun KENDİ alanından okunur — mesaj metni
    OKUNMAZ, bu yüzden metin yeniden yazımı sınıflandırmayı kaydıramaz.
    """
    return bulgu.kategori == KATEGORI_KAP_IDDIASI

VIDEO_HAVUZLARI = ("hareket", "sahne")

# GÖREV B ADIM 3 — dönem başına dört başlık.
OZEL_GUN_YUVALARI = ("mesaj_ekseni", "kanca", "cta", "gorsel_vurgu")
# Bunların üçü liste; `mesaj_ekseni` düz metindir.
OZEL_GUN_LISTE_YUVALARI = ("kanca", "cta", "gorsel_vurgu")

# Dörtle KAPALI, tek değerli, ASCII (ADIM 2 + BİÇİM KURALLARI md. 5).
TUR_ETIKETLERI = ("kutlama", "anma", "ticari-firsat", "karma")
# Dörtle KAPALI kanal anahtarı uzayı (`_SABLON.md` Bölüm 2 + BİÇİM KURALLARI md. 7).
KANAL_ANAHTARLARI = (
    "whatsapp_hatti",
    "fiziksel_magaza",
    "randevu_sistemi",
    "eticaret_sitesi",
)

# K-120'nin resmî değeri — AYNEN bu yazım.
BILINCLI_BOS = "içerik-önerilmez"

# K-127 (Eray, 2026-08-23): koşunun geçerlilik TABANI. Kaynak SAYISI kapısıdır.
KAYNAK_TABANI = 2

# Sözleşmenin seviyesini açıkça yazdığı tek kontrolün eşiği.
UZUN_ALINTI_KELIME_SINIRI = 40

# ── Ölçülmemiş sözleşme kuralları — hepsi NOT üretir (İlke 9) ───────────────
#
# Bu sayılar burada tek yerde durur ki "kapı mı, kural mı" sorusu tek yerden
# cevaplansın: kural. Değerleri değişse bile SEVİYE değişmez; seviye `CHECKS`
# üyesinin `seviye` alanındadır ve K-88 kapanmadan `eleme` olamaz.
ALAN_ALT_SINIRLARI = MappingProxyType(
    {"cta_kaliplari": 5, "kanca_kaliplari": 3, "gorsel_kodlar": 20}
)
VIDEO_TOPLAM_ALT_SINIRI = 10
VIDEO_HAVUZ_ALT_SINIRI = 5
DONEM_ALT_SINIRI = 6
DONEM_YUVA_ALT_SINIRLARI = MappingProxyType({"kanca": 2, "cta": 2, "gorsel_vurgu": 5})

# Serbest cümleyle anlatılmış boşluk — sözleşme bunları BOŞ alan sayar (ADIM 3
# muafiyet paragrafı). Küme küçüktür ve KAPSAMA ORANI ÖLÇÜLMEMİŞTİR; belgelenmiş
# bir vekildir, tüketici bir liste değil.
_BOSLUK_IFADELERI = frozenset(
    {
        "-",
        "—",
        "–",
        "yok",
        "yoktur",
        "n/a",
        "na",
        "içerik yok",
        "içerik önermiyorum",
        "içerik önerilmiyor",
        "boş",
    }
)

# Türkçe'ye özgü harfler — İngilizce yüzeylerin mekanik işareti.
_TURKCE_HARFLER = frozenset("çğıöşüÇĞİÖŞÜ")

# Kanonik kimliğin uzantı ayağı: nokta sonrası parça YALNIZ harflerden oluşuyor
# ve bu uzunluğu aşmıyorsa dosya uzantısı sayılır. Sınır rakam taşıyan sürüm
# eklerini (`KAYNAK-1.2`) uzantı sanmayı ENGELLER — o ekler kimliğin parçasıdır.
_UZANTI_AZAMI_UZUNLUK = 8

# Yol bileşenlerinde ATILAN parçalar (gezinme ve boş bileşen).
_YOL_GEZINME_PARCALARI = frozenset({"", ".", ".."})

# `run`'ın ürettiği kanonik içerik özetinin BİÇİMİ (`identity.canonical_sha`
# sha256 onaltılık dizesi döner). Serbest metin bu alandan geçemez.
_ICERIK_OZETI_RE = re.compile(r"^[0-9a-f]{64}$")


def kanonik_kaynak_kimligi(ad: str) -> str:
    """Ham kaynak adından KANONİK kimliği türetir — TEK kural, TEK yer.

    **Sınıf (tur 2, F1):** *"bir sayım/benzersizlik kararına giren kimlik,
    çağıranın serbest metnidir."* Tur 1 `kaynak_adi`'nı zorunlu yaptı ama
    normalleştirmedi; ölçüldü ki takma adlar (`" KAYNAK-1 "` · `"kaynak-1"` ·
    `"a/../KAYNAK-1"` · NFD yazımı · `"KAYNAK-1.md"`) tek kaynağı İKİ bağımsız
    kaynak gibi gösteriyordu — beşinde de `dur=False, gecerli=2`. Kapatma o beş
    ekseni tek tek yamalamak DEĞİL: kimlik burada TÜRER ve `gate_round` da,
    `DoctorReport.__post_init__` de aynı kuralı çağırır.

    Kural sırayla:

      (1) unicode NFC — aynı harfin ayrık ve bitişik yazımı tek biçime düşer;
      (2) `\\` → `/`, sonra yol bileşenlerine böl, gezinme parçalarını (`.`,
          `..`, boş) at ve SON bileşeni al — dizin öneki kimlik değildir;
      (3) iç/kenar boşluk tek boşluğa indirgenir;
      (4) tamamı HARF olan ve `_UZANTI_AZAMI_UZUNLUK`'u aşmayan son uzantı
          atılır — `KAYNAK-1.md` ile `KAYNAK-1` aynı kaynaktır;
      (5) `casefold` — harf durumu kimlik taşımaz.

    Boş dizeye düşen ad KİMLİK DEĞİLDİR ve çağıran (`__post_init__`) onu
    reddeder — kural burada sessizce bir yedek ad UYDURMAZ (fail-closed).

    **Kapsam sınırı (İlke 9(4)):** kural yalnız YAZIM takma adlarını denkler.
    Gerçekten farklı iki adın aynı kaynağı göstermesi (`"OpenAI-raporu"` ve
    `"gpt-cikitisi"`) yazımdan görülemez; o eksen İÇERİK özetiyle kapanır
    (`DoctorReport.icerik_ozeti`) ve özeti OLMAYAN kimlik `_kimlik_kapiya_uygun`
    gereği kapı sayımına hiç girmez (fail-closed).
    Son bileşeni almak `dizin-1/K` ile `dizin-2/K`'yi de denkler; bu yön
    fail-closed'dır (sayı DÜŞER, koşu durur).
    """
    if not isinstance(ad, str):
        raise TypeError(f"kaynak adı metin değil: {type(ad).__name__}")
    metin = unicodedata.normalize("NFC", ad).replace("\\", "/")
    parcalar = [
        parca
        for parca in metin.split("/")
        if parca.strip() not in _YOL_GEZINME_PARCALARI
    ]
    if not parcalar:
        return ""
    son = " ".join(parcalar[-1].split())
    kok, nokta, uzanti = son.rpartition(".")
    if (
        nokta
        and kok
        and uzanti.isalpha()
        and len(uzanti) <= _UZANTI_AZAMI_UZUNLUK
    ):
        son = kok
    return son.casefold()

DISLANAN_KONTROL_GEREKCESI = """
Spec-input §7.3 "Kontrol kümesi" tablosunun DOKUZUNCU satırı — "görsel/video/özel gün
görsel vurgu alanlarında metin unsuru" — bu kümeye BİLİNÇLE ALINMADI, unutulmadı.
Gerekçe sözleşmenin kendi cümlesidir: o satır bugün "mekanik kapının değil,
DENETÇİNİN kuralıdır" ve karşılığı `[metin-öğesi]` bayrağıdır (spec-input §7.4).
Aynı satır, anahtar sözcük taramasının "kapsama oranının ÖLÇÜLMEMİŞ" olduğunu da
söyler. Ölçülmemiş bir kapsamı mekanik kapıya koymak İlke 9'un yasakladığı şeydir;
kapıya konup konmayacağı kapsam kararına bağlıdır ve o karar açıktır.
""".strip()

# ─── 2. Tipler ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Bulgu:
    """Tek bir kontrolün tek bir bulgusu. Seviye kontrolden GELİR, üretilmez."""

    kontrol: str
    aile: str
    seviye: str
    mesaj: str
    kategori: str = KATEGORI_BLOGA_AIT
    """Ekleme değişmezi karşısındaki sınıf — bulgunun ÜRETİLDİĞİ yerden gelir.

    Kategori bir SINIFLANDIRICI tarafından mesaj metninden ÇIKARILMAZ; kontrol
    onu `_kap(...)` ile BEYAN eder, beyan edilmeyen yol fail-closed olarak
    `bloga-ait` (dokunulmaz) kalır. `kap_iddiasi_mi` yalnız bu alanı okur.
    """

    def __post_init__(self) -> None:
        if self.kategori not in KATEGORILER:
            raise ValueError(
                f"Bulgu kategorisi kapalı kümenin dışında: {self.kategori!r} "
                f"— {list(KATEGORILER)}"
            )


@dataclass(frozen=True)
class DoctorReport:
    """Bir kaynağın kapı raporu.

    Alan sırası plan 950'nin `DoctorReport(sonuc, notlar, elemeler)` yazımını
    KORUR; `kaynak_adi` sona eklenmiş dördüncü alandır — Task 9 paketleyicisi
    raporu kaynağıyla eşleştirebilsin diye (`build_packet` `sources` ve
    `doctor_reports` listelerini AYRI alır, eşleme sıraya bırakılırsa sessizce
    kayabilir).

    **SAPMA (bilinçli, plan 950'den):** `kaynak_adi` VARSAYILANSIZDIR. Plan
    yazımının ilk üç alanı adıyla ve sırasıyla korunur; dördüncü alan
    varsayılanını kaybeder. Gerekçe ÖLÇÜLDÜ: varsayılan `""` iken `gate_round`
    adsız iki raporu iki AYRI kaynak sayıyordu (`dur=False`, `gecerli=2`) —
    K-127'nin "iki BAĞIMSIZ kaynak" şartı fail-open'dı. Kimliği yalnız
    `gate_round`'da reddetmek daha ZAYIF kapatmadır: bozuk rapor yine kurulup
    Task 9 paketleyicisine akabilirdi.

    **Değişmez (H1(b)):** rapor kendi hakkında yalan söyleyemez. `sonuc`
    taşıdığı bulgulardan TÜRETİLEBİLİR (`sonuc_belirle`), ve bulgular doğru
    koleksiyonda + doğru seviyededir. Emsal
    `sector_pipeline/contracts.py::ContractPin.__post_init__`: yapısal
    değişmezler yapıcıda zorlanır ki `run` yolunu ATLAYAN çağrıcılar da
    kapsansın.
    """

    sonuc: str
    notlar: tuple[Bulgu, ...]
    elemeler: tuple[Bulgu, ...]
    kaynak_adi: str
    icerik_ozeti: str = ""
    iddialar: tuple[CIddia, ...] = ()
    """Bölüm C'nin TİPLİ satırları — motorun iddia bağının BİR ucu.

    `run` bunu belgeden ÜRETİR. Alan `icerik_ozeti`nin emsalini izler: BİÇİMİ
    fail-closed zorlanır (numara kimliktir: pozitif, tekrarsız; alan boş
    olamaz), KÖKENİ (gerçekten bu metnin Bölüm C'si mi) doğrulanmaz — `run`
    yolunu atlayan bir çağıran belgeye sahip olmayabilir ve burada uydurma bir
    değer ÜRETİLMEZ (dürüst etiket, İlke 9(4)).

    **DİZİ kuralı (1..N, boşluksuz) burada zorlanMAZ ve bu bilinçlidir:** o bir
    BULGU'dur (`_c_no_dizisi_ihlalleri`), yapıcı değişmezi değil. Aksi hâlde
    numarası bozuk bir araştırma çıktısı kapının RAPOR üretmesini engeller,
    yani kapı ölçmesi gereken belgede ÇÖKERDİ.
    """
    kapsam_sinirlari: tuple[str, ...] = field(init=False, default=())
    """Kapının NE KADARINI ölçtüğünün dürüst beyanı — `CHECKS`'ten TÜRER.

    **Ölçülmüş gerileme (tur 2, F3):** alan tur 1'de `()` varsayılanlı ve
    çağıran tarafından yazılabilirdi; `DoctorReport('gecti', (), (),
    kaynak_adi='K')` BEYANSIZ kuruluyor, `kapsam_sinirlari=('uydurma sınır',)`
    ise kabul ediliyordu. Ölçülmemiş ters dil kuralının TEK telafisi atlanabilir
    ya da uydurulabilir bir alan olamaz; bu yüzden alan artık `init=False`'tur
    ve `__post_init__` onu kanonik kontrol kümesinden üretir. Beyan yine BULGU
    değildir: rapor sonucunu bozmaz, temiz kaynak `gecti` kalır.
    """
    """Kaynak METNİNİN kanonik özeti — kimliğin İÇERİK ayağı.

    `run` bunu `identity.canonical_sha(source_text)`'ten ÜRETİR; çağıranın
    yazdığı bir etiket değildir ve biçimi (`sha256` onaltılık) fail-closed
    zorlanır — serbest metin buradan geçemez. `run` yolunu atlayan bir çağıran
    (Task 9/12 tüketicileri) metne sahip olmayabilir; o rapor özetsiz kalır ve
    burada uydurma bir değer ÜRETİLMEZ. Bunun bedeli `gate_round`'da ödenir:
    özetsiz bir kimlik K-127 sayımına GİRMEZ (`_kimlik_kapiya_uygun`) — ölçüldü
    ki aksi hâlde iki özetsiz rapor tabanı fail-open geçiyordu. Alanın BİÇİMİ
    zorlanır, KÖKENİ (gerçekten bu metnin özeti mi) DOĞRULANMADI.
    """

    @property
    def kanonik_kimlik(self) -> str:
        """Kimliğin AD ayağı — saklanmaz, kanonik kuraldan TÜRER."""
        return kanonik_kaynak_kimligi(self.kaynak_adi)

    def __post_init__(self) -> None:
        object.__setattr__(self, "notlar", _bulgu_demeti(self.notlar, "notlar"))
        object.__setattr__(self, "elemeler", _bulgu_demeti(self.elemeler, "elemeler"))
        object.__setattr__(
            self, "kapsam_sinirlari", _metin_demeti(_kapsam_beyani())
        )
        if not isinstance(self.kaynak_adi, str) or not self.kanonik_kimlik:
            raise ValueError(
                "DoctorReport.kaynak_adi kimlik taşımak ZORUNDA (kanonik "
                f"biçimde de boş olamaz): {self.kaynak_adi!r} — K-127 kaynak "
                "SAYISI kapısı KANONİK kimliğe göre sayar"
            )
        if not isinstance(self.icerik_ozeti, str):
            raise TypeError(
                f"DoctorReport.icerik_ozeti metin değil: "
                f"{type(self.icerik_ozeti).__name__}"
            )
        if self.icerik_ozeti and not _ICERIK_OZETI_RE.match(self.icerik_ozeti):
            raise ValueError(
                "DoctorReport.icerik_ozeti KANONİK bir özet olmak zorunda "
                f"(sha256 onaltılık ya da boş): {self.icerik_ozeti!r} — "
                "serbest metin kimlik kararına giremez"
            )
        object.__setattr__(self, "iddialar", tuple(self.iddialar))
        if not all(type(iddia) is CIddia for iddia in self.iddialar):
            raise TypeError(
                "DoctorReport.iddialar yalnız `CIddia` taşır: "
                f"{[type(i).__name__ for i in self.iddialar]} — benzeyen nesne "
                "kimlik değişmezlerini taşımaz"
            )
        numaralar = [iddia.no for iddia in self.iddialar]
        if any(not isinstance(no, int) or isinstance(no, bool) or no < 1 for no in numaralar):
            raise ValueError(
                f"DoctorReport.iddialar numarası 1'den küçük olamaz: {numaralar} "
                "— numara sözleşmede KİMLİKTİR (dış depo `12beec1`)"
            )
        if len(set(numaralar)) != len(numaralar):
            raise ValueError(
                f"DoctorReport.iddialar numarası TEKRAR EDEMEZ: {numaralar} — "
                "tekrar eden numara motorda iki ayrı iddiaya çözülür ve "
                "yetkilendirme yeniden alan düzeyine düşer"
            )
        if any(not iddia.alan.strip() for iddia in self.iddialar):
            raise ValueError(
                "DoctorReport.iddialar `alan` hücresi BOŞ olamaz — motor "
                "kararın alanıyla örtüşmeyi o hücrede ölçer"
            )
        if any(not isinstance(iddia.url, str) for iddia in self.iddialar):
            raise TypeError(
                "DoctorReport.iddialar `url` metin olmak zorunda — K-126 URL eşitliği "
                "metin karşılaştırmasıdır"
            )
        for iddia in self.iddialar:
            if not isinstance(iddia.anahtarlar, tuple) or any(
                not isinstance(a, str) or not _SISTEM_ANAHTARI_RE.match(a)
                for a in iddia.anahtarlar
            ):
                raise ValueError(
                    "DoctorReport.iddialar `anahtarlar` yalnız slug biçimli "
                    f"sistem anahtarı taşır: {iddia.anahtarlar!r} — motor Görev B "
                    "bağını bu kümeden kurar, serbest metin bağ kuramaz"
                )
        ihlaller = _rapor_ihlalleri(self.sonuc, self.notlar, self.elemeler)
        if ihlaller:
            raise ValueError(
                "DoctorReport kendi bulgularıyla çelişiyor: " + "; ".join(ihlaller)
            )


@dataclass(frozen=True)
class RoundGate:
    """K-127 kaynak tabanı kapısının sonucu — koşu düzeyinde tek nesne.

    **Değişmez (H1(c)):** `gecerli_kaynak_sayisi` · `elenen_kaynak_sayisi` ·
    `dur` · `taban` HAM VERİNİN (`raporlar`) fonksiyonudur; onlarla çelişen bir
    `RoundGate` kurulamaz. Sayım KİMLİĞE göredir: aynı kaynağın iki raporu tek
    kaynak sayılır ve bir kimliğin raporlarından biri elendiyse o kimlik
    ELENMİŞTİR (fail-closed).
    """

    dur: bool
    gecerli_kaynak_sayisi: int
    elenen_kaynak_sayisi: int
    taban: int
    bildirim: str
    raporlar: tuple[DoctorReport, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "raporlar", _rapor_demeti(self.raporlar))
        ihlaller = _gate_ihlalleri(
            dur=self.dur,
            gecerli_kaynak_sayisi=self.gecerli_kaynak_sayisi,
            elenen_kaynak_sayisi=self.elenen_kaynak_sayisi,
            taban=self.taban,
            bildirim=self.bildirim,
            raporlar=self.raporlar,
        )
        if ihlaller:
            raise ValueError(
                "RoundGate türetilmiş alanları ham veriyle çelişiyor: "
                + "; ".join(ihlaller)
            )


@dataclass(frozen=True)
class Check:
    """Tek bir mekanik kontrol.

    `seviye` kontrolün KENDİSİNDE yaşar: K-88 kapandığında değişecek yer burasıdır
    ve `run` seviyeye göre dallanır, kontrol adına göre DEĞİL — ikincisi eşlemeyi
    iki yere kopyalardı.
    """

    kimlik: str
    aile: str
    seviye: str
    aciklama: str
    kural: Callable[["_Belge"], list[str | _Mesaj]]
    kapsam_sinirlari: tuple[str, ...] = ()
    """Kontrolün sözleşmenin NE KADARINI ölçtüğünün dürüst beyanları.

    Boş değilse `run` onları `DoctorReport.kapsam_sinirlari`'na taşır — İlke
    9(4) ölçülmeyen davranış iddiasının "doğrulanmadı" etiketiyle SUNULMASINI
    ister ve docstring'de saklı kalmak sunum değildir. Bu bir BULGU değildir:
    rapor sonucunu değiştirmez, temiz kaynak `gecti` kalır.

    **Alan tur 3'te TEK metinden DEMETE çevrildi:** bir kontrolün birden çok
    BAĞIMSIZ ölçüm sınırı olabiliyor ve ikisini tek paragrafa sıkıştırmak
    denetçiden kalem SAYISINI gizliyordu. `bolum-ve-alan-tamligi` bunun ölçülmüş
    örneğidir: tanıma vekili ayrı bir sınır, sözleşmenin ÖNEM SIRASI kuralının
    doğrulanamaması ayrı bir sınırdır.
    """

    def __post_init__(self) -> None:
        if not isinstance(self.kapsam_sinirlari, tuple) or not all(
            isinstance(sinir, str) for sinir in self.kapsam_sinirlari
        ):
            raise TypeError(
                "Check.kapsam_sinirlari metin DEMETİ olmak zorunda: "
                f"{self.kapsam_sinirlari!r}"
            )
        if self.seviye not in SEVIYELER:
            raise ValueError(
                f"Check seviyesi kapalı kümenin dışında: {self.seviye!r} — "
                f"{list(SEVIYELER)}"
            )
        if self.aile not in KONTROL_AILELERI:
            raise ValueError(
                f"Check ailesi kanonik sabitin dışında: {self.aile!r} — "
                f"{list(KONTROL_AILELERI)}"
            )


def _bulgu_demeti(deger: object, etiket: str) -> tuple[Bulgu, ...]:
    """Koleksiyonu KOPYALAYARAK dondurur + öğe tipini zorlar (fail-closed).

    `identity.donmus` çağrılmaz: öğeleri donmuş veri sınıfı olan alanlar onun
    kapalı kümesinin DIŞINDADIR (kural 5) ve `donmus` docstring'i tam olarak bu
    yolu tarif eder — `tuple(...)` kopyası + tip kontrolü.
    """
    if isinstance(deger, (str, bytes)) or not isinstance(deger, Iterable):
        raise TypeError(f"DoctorReport.{etiket} dizi değil: {type(deger).__name__}")
    ogeler = tuple(deger)
    for oge in ogeler:
        if type(oge) is not Bulgu:
            raise TypeError(
                f"DoctorReport.{etiket} yalnız Bulgu taşır, {type(oge).__name__} "
                "aldı — yabancı tip rapora sessizce giremez"
            )
    return ogeler


def _kapsam_beyani() -> tuple[str, ...]:
    """Kapsam beyanı — kanonik kontrol kümesinin TÜREVİ, kopyası değil."""
    return tuple(
        sinir for check in CHECKS for sinir in check.kapsam_sinirlari
    )


def _metin_demeti(deger: object) -> tuple[str, ...]:
    """Kapsam sınırı beyanlarını kopyalayarak dondurur + tipi zorlar."""
    if isinstance(deger, (str, bytes)) or not isinstance(deger, Iterable):
        raise TypeError(
            f"DoctorReport.kapsam_sinirlari dizi değil: {type(deger).__name__}"
        )
    ogeler = tuple(deger)
    for oge in ogeler:
        if not isinstance(oge, str):
            raise TypeError(
                "DoctorReport.kapsam_sinirlari yalnız metin taşır, "
                f"{type(oge).__name__} aldı"
            )
    return ogeler


def _rapor_ihlalleri(
    sonuc: str, notlar: Sequence[Bulgu], elemeler: Sequence[Bulgu]
) -> list[str]:
    """Raporun kendi içindeki tutarsızlıkları listeler (boş liste = tutarlı).

    AYRI bir fonksiyondur ki testin mutasyon kolu kapıyı SÖKEBİLSİN: kural
    `__post_init__`'in gövdesine gömülseydi "kapı gerçekten burada mı" sorusu
    ölçülemezdi.
    """
    ihlaller: list[str] = []
    if sonuc not in SONUCLAR:
        ihlaller.append(
            f"sonuc kapalı kümenin dışında: {sonuc!r} — {list(SONUCLAR)}"
        )
    for bulgu in notlar:
        if bulgu.seviye != SEVIYE_NOT:
            ihlaller.append(
                f"`notlar` içinde {bulgu.seviye!r} seviyeli bulgu var "
                f"({bulgu.kontrol!r}) — koleksiyonlar seviyeye göre ayrışır"
            )
    for bulgu in elemeler:
        if bulgu.seviye != SEVIYE_ELEME:
            ihlaller.append(
                f"`elemeler` içinde {bulgu.seviye!r} seviyeli bulgu var "
                f"({bulgu.kontrol!r}) — koleksiyonlar seviyeye göre ayrışır"
            )
    if sonuc in SONUCLAR:
        beklenen = sonuc_belirle(notlar, elemeler)
        if sonuc != beklenen:
            ihlaller.append(
                f"sonuc {sonuc!r}, taşınan bulgulardan türeyen değer "
                f"{beklenen!r} ({len(notlar)} not, {len(elemeler)} eleme)"
            )
    return ihlaller


def _kimlik_anahtarlari(rapor: DoctorReport) -> tuple[tuple[str, str], ...]:
    """Bir raporun kimlik ANAHTARLARI — kanonik ad, ve varsa kanonik özet.

    İki ayaklı olmasının sebebi ölçüldü: ad ayağı YAZIM takma adlarını
    (`" KAYNAK-1 "`, `"kaynak-1.md"`, `"a/../KAYNAK-1"`) denkler; içerik ayağı
    aynı metnin İKİ FARKLI adla verilmesini denkler. İkisi ayrı şeyi çözer ve
    birlikte TEK bir denklik bağıntısı kurar (`_kimlik_bolumlemesi`).
    """
    anahtarlar: list[tuple[str, str]] = [("ad", rapor.kanonik_kimlik)]
    if rapor.icerik_ozeti:
        anahtarlar.append(("ozet", rapor.icerik_ozeti))
    return tuple(anahtarlar)


def _kimlik_kapiya_uygun(raporlar: Sequence[DoctorReport]) -> bool:
    """Bir kimlik grubu K-127 SAYIMINA girebilir mi — kimliğin İÇERİK ayağı.

    **Ölçülmüş fail-open (tur 3, F1):** `icerik_ozeti` boş olabildiği için
    kimliğin içerik ayağı SESSİZCE düşüyordu. `run`'ı ATLAYIP doğrudan kurulan
    iki özetsiz rapor (`DoctorReport(sonuc='gecti', notlar=(), elemeler=(),
    kaynak_adi='gemini-cikti' / 'claude-cikti')`) `dur=False, gecerli=2`
    veriyordu: kimliğin yalnız AD ayağı denklendiği için tek bir kaynağın iki
    adla verilmesi K-127 tabanını geçiyordu. Bir önceki turun takma-ad matrisi
    bunu göremezdi — o matris yalnız `run` üretimi raporları egzersiz eder ve
    `run` özeti HER ZAMAN üretir.

    Kapatma yönü FAIL-CLOSED'dır: özeti olmayan kimlik SAYILMAZ — ve sessizce
    düşmez, `gate_round` onu bildirimde ADIYLA söyler. Uydurma bir özet
    ÜRETİLMEZ; metne sahip olmayan çağıran için doğru cevap "bu kimlik kapıya
    uygun değildir"dir.

    **Meşru hâl açıkça temsil edilir:** sentetik/elenen raporun kaynak metni
    olmayabilir ve `elendi` raporları zaten sayıma GİRMEZ
    (`_kimlik_bolumlemesi` onları `elenen` kovasına koyar), dolayısıyla kural
    onları etkilemez. Aynı kimliğin raporlarından BİRİ özet taşıyorsa grup
    uygundur — özet KİMLİĞİN ayağıdır, tek bir raporun alanı değil.

    **Kapsam sınırı (İlke 9(4)):** özetin BİÇİMİ zorlanır (`_ICERIK_OZETI_RE`),
    KÖKENİ zorlanamaz — `run` yolunu atlayan çağıranın elinde metin yoktur ve
    biçimi geçerli bir özet uydurulabilir. O eksen DOĞRULANMADI; kapı yalnız
    "içerik ayağı BEYAN edilmiş mi" sorusunu sorar.
    """
    return any(rapor.icerik_ozeti for rapor in raporlar)


def kaynak_seti_sha(raporlar: Sequence[DoctorReport]) -> str:
    """Mekanik kapı rapor kümesinin KANONİK kimliği — TEK üretici.

    **Neyi kanıtlar.** İki taraf (denetçi paketini kuran `build_packet` ve
    motora verilen `RoundGate`) AYNI rapor kümesini AYNI SIRADA gördü mü. Kör
    kaynak etiketi (`KAYNAK-1/2/3`) KONUMDAN türer; sıra kayarsa aynı etiket
    başka bir kaynağı gösterir ve motorun saydığı çoğunluk sessizce başka bir
    koşunun kaynaklarına dayanır. Bu yüzden hash SIRAYA duyarlıdır.

    **Raporun TAMAMI girer — üç alanlık özet YETMEZ (hakem turu 1, orta).**
    İlk yazım yalnız `kaynak_adi` · `icerik_ozeti` · `sonuc` alıyordu ve
    beyan ettiği garanti mühürden GENİŞTİ: `notlar` ve `elemeler` denetçi
    paketinin EK-E bölümüne METİN olarak yazılır (`auditors._ek_e_metni`) —
    yani denetçinin GÖRDÜĞÜ şeyi değiştirirler.

    **`kapsam_sinirlari` BİLEREK DIŞARIDA.** O alan da EK-E'ye yazılır ama
    `field(init=False)`'tur ve `_kapsam_beyani()`'nden, yani modül düzeyindeki
    `CHECKS` kümesinden türer: TEK bir kod sürümü içinde her rapor için AYNIDIR.
    Karşılaştırmanın iki tarafı da aynı süreçte aynı değeri üretir, dolayısıyla
    hiçbir ayrım üretemez. Ölçülemeyen bir bileşeni mühre koymak, mührü
    olduğundan güçlü gösterirdi.
    Ölçüldü: aynı `sonuc`'u taşıyan iki rapor (`notlu-gecti`) yalnız not
    METNİYLE ayrılıyor ve eski kimlik ikisini AYIRT ETMİYORDU; mühür
    "aynı mekanik kapı" diyorken denetçiye başka bir EK-E gitmiş olabilirdi.
    `sonuc` alanı türetilmiştir ve kabalıktır (`gecti` · `notlu-gecti` ·
    `elendi`); ayrımı o taşıyamaz.

    Sıraya duyarlıdır: kör kaynak etiketi (`KAYNAK-1/2/3`) KONUMDAN türer, sıra
    kayarsa aynı etiket başka bir kaynağı gösterir.

    **Kapsam sınırı (dürüst etiket).** Bu kimlik koşunun `run_id`'sini ya da
    sektörünü TAŞIMAZ ve taşıyamaz: motorun girdi alan kümesi kapalıdır (R5) ve
    orada karşılaştırılacak ikinci bir `run_id` taşıyıcısı YOKTUR. Kanıtlanan
    tam olarak şudur: *"motora verilen mekanik kapı, denetçi paketini kuran
    kapının ta kendisidir."* Aynı raporlarla iki kez koşulmuş İKİ ayrı koşuyu
    birbirinden ayırmaz.
    """

    def _bulgu(bulgu: Bulgu) -> dict:
        return {
            "kontrol": bulgu.kontrol,
            "aile": bulgu.aile,
            "seviye": bulgu.seviye,
            "mesaj": bulgu.mesaj,
            "kategori": bulgu.kategori,
        }

    return identity.canonical_sha(
        [
            {
                "kaynak_adi": rapor.kaynak_adi,
                "icerik_ozeti": rapor.icerik_ozeti,
                "sonuc": rapor.sonuc,
                "notlar": [_bulgu(b) for b in rapor.notlar],
                "elemeler": [_bulgu(b) for b in rapor.elemeler],
                # `iddialar` MÜHRE GİRER (2026-09-11). Alan EK-E'ye YAZILMAZ,
                # yani denetçinin gördüğünü değiştirmez — ama motorun
                # YETKİLENDİRME kapısını besler: `ekle` kararının dayandığı
                # araştırma iddiası buradan çözülür.
                #
                # **Gerekçenin DÜRÜST sınırı (hakem turu 1, F9/düşük).** İlk
                # yazım "iddia kümesi değişmiş bir rapor mühürden SESSİZCE
                # geçerdi" diyordu; bu ABARTILIYDI. `run` yolunda `iddialar`
                # kaynak METNİNDEN saf olarak türer ve metnin kimliği
                # `icerik_ozeti` ile ZATEN aynı mührün içindedir — o yolda alan
                # bağımsız bir ayrım üretmez. Alanın gerçekten kapattığı şey
                # dardır: `DoctorReport`'u `run`'ı ATLAYARAK elle kuran bir
                # çağıranın iddia kümesi. O yolun kökeni zaten doğrulanmamıştır
                # (alanın kendi docstring'i böyle der); mühür onu da kapsar.
                # Attempt-3 F5 (düşük, gönüllü): alan kümesi ELLE sayılmaz, tipin
                # alanlarından türer — yeni bir yetkilendirme kolu (anahtarlar, url)
                # eklendiğinde mühür kendiliğinden kapsar.
                "iddialar": [
                    {
                        alan.name: (
                            list(getattr(iddia, alan.name))
                            if isinstance(getattr(iddia, alan.name), tuple)
                            else getattr(iddia, alan.name)
                        )
                        for alan in dataclasses.fields(CIddia)
                    }
                    for iddia in rapor.iddialar
                ],
            }
            for rapor in raporlar
        ]
    )


def kimlik_bolumlemesi(
    raporlar: Sequence[DoctorReport],
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    """Raporları KİMLİĞE böler → (geçerli, elenen, tekrar eden, özetsiz).

    **PUBLIC (Plan 2 Task 12, checkpoint 9 / F2).** Motorun `2-3` çoğunluk kapısı
    "hangi kaynak kimlikleri bu koşuda GEÇERLİ" sorusunu sorar ve cevabı BURADA
    yaşar. İkinci bir kopya yazmak iki sürümlü bir kimlik kuralı üretirdi —
    fail-closed eleme kuralı (bir raporu elenen kimlik ELENMİŞTİR) ve içerik
    ayağı yalnız burada doğru.

    K-127 iki BAĞIMSIZ kaynak ister; mutabakat sinyali ilkece iki ayrı kaynağın
    işidir. Bu yüzden birim RAPOR değil KİMLİKTİR. Bir kimliğin raporlarından
    biri elendiyse kimlik elenmiş sayılır (fail-closed) — takma adla `gecti`,
    öbür takma adla `elendi` gelen ÇELİŞKİLİ çift de elenmiştir.

    Denklik bağıntısı `_kimlik_anahtarlari`'nın ANAHTARLARI üstünde kurulur ve
    geçişlidir (birleştir/bul): A ile B adı üstünden, B ile C özet üstünden
    denkse üçü TEK kaynaktır. Dönen adlar grubun İLK görülen HAM adıdır —
    yönetici bildirimini kanonik biçimle değil yazdığı adla okur.

    Elenmemiş bir kimlik `_kimlik_kapiya_uygun` değilse GEÇERLİ sayılmaz;
    dördüncü demet (`özetsiz`) onu ADIYLA taşır ki sessizce düşmesin.
    """
    ebeveyn: dict[tuple[str, str], tuple[str, str]] = {}

    def bul(anahtar: tuple[str, str]) -> tuple[str, str]:
        while ebeveyn[anahtar] != anahtar:
            ebeveyn[anahtar] = ebeveyn[ebeveyn[anahtar]]
            anahtar = ebeveyn[anahtar]
        return anahtar

    def birlestir(sol: tuple[str, str], sag: tuple[str, str]) -> None:
        kok_sol, kok_sag = bul(sol), bul(sag)
        if kok_sol != kok_sag:
            ebeveyn[kok_sag] = kok_sol

    for rapor in raporlar:
        anahtarlar = _kimlik_anahtarlari(rapor)
        for anahtar in anahtarlar:
            ebeveyn.setdefault(anahtar, anahtar)
        for anahtar in anahtarlar[1:]:
            birlestir(anahtarlar[0], anahtar)

    sirali: list[tuple[str, str]] = []
    ad: dict[tuple[str, str], str] = {}
    grup: dict[tuple[str, str], list[DoctorReport]] = {}
    elenen: set[tuple[str, str]] = set()
    for rapor in raporlar:
        kok = bul(_kimlik_anahtarlari(rapor)[0])
        if kok not in ad:
            sirali.append(kok)
            ad[kok] = rapor.kaynak_adi
            grup[kok] = []
        grup[kok].append(rapor)
        if rapor.sonuc == SONUC_ELENDI:
            elenen.add(kok)
    kalan = [kok for kok in sirali if kok not in elenen]
    elenen_sirali = tuple(ad[kok] for kok in sirali if kok in elenen)
    gecerli = tuple(ad[kok] for kok in kalan if _kimlik_kapiya_uygun(grup[kok]))
    ozetsiz = tuple(
        ad[kok] for kok in kalan if not _kimlik_kapiya_uygun(grup[kok])
    )
    tekrar = tuple(ad[kok] for kok in sirali if len(grup[kok]) > 1)
    return gecerli, elenen_sirali, tekrar, ozetsiz


def _gate_ihlalleri(
    *,
    dur: bool,
    gecerli_kaynak_sayisi: int,
    elenen_kaynak_sayisi: int,
    taban: int,
    bildirim: str,
    raporlar: Sequence[DoctorReport],
) -> list[str]:
    """`RoundGate` türev alanlarının ham veriyle çelişkilerini listeler."""
    ihlaller: list[str] = []
    gecerli, elenen, _, _ = kimlik_bolumlemesi(raporlar)
    if taban != KAYNAK_TABANI:
        ihlaller.append(f"taban {taban}, kanonik K-127 tabanı {KAYNAK_TABANI}")
    if gecerli_kaynak_sayisi != len(gecerli):
        ihlaller.append(
            f"gecerli_kaynak_sayisi {gecerli_kaynak_sayisi}, benzersiz geçerli "
            f"kimlik sayısı {len(gecerli)} ({list(gecerli)})"
        )
    if elenen_kaynak_sayisi != len(elenen):
        ihlaller.append(
            f"elenen_kaynak_sayisi {elenen_kaynak_sayisi}, benzersiz elenen "
            f"kimlik sayısı {len(elenen)} ({list(elenen)})"
        )
    beklenen_dur = len(gecerli) < taban
    if bool(dur) is not beklenen_dur:
        ihlaller.append(
            f"dur {dur!r}, ham veriden türeyen değer {beklenen_dur!r} "
            f"({len(gecerli)} geçerli kimlik, taban {taban})"
        )
    if dur and not bildirim.strip():
        ihlaller.append("dur=True ama bildirim BOŞ — durdurma yöneticiye iletilir")
    return ihlaller


def _rapor_demeti(deger: object) -> tuple[DoctorReport, ...]:
    if isinstance(deger, (str, bytes)) or not isinstance(deger, Iterable):
        raise TypeError(f"RoundGate.raporlar dizi değil: {type(deger).__name__}")
    ogeler = tuple(deger)
    for oge in ogeler:
        if type(oge) is not DoctorReport:
            raise TypeError(
                f"RoundGate.raporlar yalnız DoctorReport taşır, "
                f"{type(oge).__name__} aldı"
            )
    return ogeler


# ─── 3. Belge ayrıştırma ────────────────────────────────────────────────────


@dataclass
class _Yuva:
    """Bir alan/yuva bloğu: başlıktaki satır-içi değer + altındaki satırlar."""

    ad: str
    inline: str = ""
    satirlar: list[str] = field(default_factory=list)

    def _ogeler(self, satirlar: Sequence[str]) -> list[str]:
        """Madde işaretli öğeler + varsa satır-içi değer — VERİLEN satırlardan."""
        ogeler = [self.inline] if self.inline else []
        ogeler += [
            _MADDE_RE.match(satir).group(1).strip()  # type: ignore[union-attr]
            for satir in satirlar
            if _MADDE_RE.match(satir)
        ]
        return [oge for oge in ogeler if oge]

    @property
    def maddeler(self) -> list[str]:
        """HAM madde listesi — DİLSİZ çit içindekiler DAHİL.

        Bu yüzeyi yalnız HAM METİN tarayan yollar okur (dil kuralı ·
        `tek_degeri` üstünden K-120): oradaki eleme yeni bir YANLIŞ-NEGATİF
        sınıfı açardı — bir çite alınmış Türkçe harf hâlâ oradadır ve
        `içerik-önerilmez` muafiyetini çite saklanmış içerikle almak
        FAIL-OPEN olurdu. SÖZLEŞME SAYAN yollar `citsiz_maddeler`'i okur.
        """
        return self._ogeler(self.satirlar)

    @property
    def citsiz_maddeler(self) -> list[str]:
        """Sözleşmenin SAYDIĞI yüzey: DİLSİZ çit bloğu ELENMİŞ madde listesi.

        Eleme kuralı doluluk sayımıyla AYNI TEK yerden gelir
        (`_maskeli_satirlar` hesaplar, `_citsiz_satirlar` süzer); ikinci bir
        çit ayrıştırıcısı YAZILMAZ.
        """
        return self._ogeler(_citsiz_satirlar(self.satirlar))

    @property
    def essiz_maddeler(self) -> list[str]:
        """Sözleşmenin SAYDIĞI birim: BENZERSİZ ve ANLAMLI madde.

        Ham `maddeler` tekrarı ve serbest boşluk ifadesini de sayar. Adet alt
        sınırları ham sayıyı okursa "5 CTA kalıbı" aynı satırın beş kopyasıyla
        ya da beş `yok` ile sağlanır ve kapı SESSİZ kalır — ölçüldü. Bu yüzden
        sayıya dayalı her eşik BURADAN okur (`_kontrol_adet_alt_sinirlari`).

        **Tur 9 — sayım da ÇİT-FARKINDADIR.** Doluluk yolu tur 8'de
        çit-farkında oldu ama AYNI içeriği okuyan ADET yolu süpürülmemişti:
        `cta_kaliplari` boşaltılınca rapor İKİ not veriyordu (`alanı boş` +
        `0 madde taşıyor, sözleşme alt sınırı 5`), AYNI alana DİLSİZ çit
        İÇİNDE beş madde konunca alt sınır notu SUSUYORDU. Ölçüm mesaj
        KÜMESİ farkıyla yapıldı: not SAYISI 2 → 3 ARTMIŞTI ve sayı
        karşılaştırması kapanışı YANLIŞ gösteriyordu.
        """
        gorulen: set[str] = set()
        essiz: list[str] = []
        for madde in self.citsiz_maddeler:
            anahtar = _sadelestir(madde)
            if not anahtar or anahtar in _BOSLUK_IFADELERI or anahtar in gorulen:
                continue
            gorulen.add(anahtar)
            essiz.append(madde)
        return essiz

    @property
    def dolu(self) -> bool:
        """Kapta SÖZLEŞME BİÇİMİNDE anlamlı içerik var mı?

        ÜÇ eleme birlikte çalışır ve ayrı şeyleri kapatır:

          * serbest BOŞLUK ifadeleri (`yok` · `-` · `n/a`) boş sayılır — K-120
            yalnız AYNEN `içerik-önerilmez` yazımını muaf tutar;
          * sözleşmenin tanımadığı markdown BLOK yapıları (tablo · yatay çizgi)
            kabı DOLDURMAZ (`_sozlesme_bicimli`) — ölçüldü ki bir dönem
            yuvasına konan bağımsız bir tablo yuvanın boşluk notunu
            kaldırıyordu (`notlu-gecti / 1 not` → `gecti / 0 not`);
          * DİLSİZ kod çiti BLOĞU — açıcısı, GÖVDESİ ve kapatıcısı — sayımdan
            ÇIKARILIR (`_citsiz_satirlar`). Bu eleme satır-tek-tek YAPILAMAZ:
            çıplak ` ``` ` ayıracı sözcüksüz olduğu için zaten eleniyordu ama
            çitin İÇİNDEKİ `print(42)` satırı kabı DOLDURUYORDU (ölçüldü:
            `notlu-gecti / 1 not` → `gecti / 0 not`; kapanmamış çit de aynı).
            DİLLİ çit (` ```python `) ilan edilmiş AÇIK kalemdir ve DOKUNULMAZ.
        """
        parcalar = [self.inline] if self.inline else []
        parcalar += _citsiz_satirlar(self.satirlar)
        return any(
            _sozlesme_bicimli(parca)
            and _sadelestir(parca) not in _BOSLUK_IFADELERI
            for parca in parcalar
        )

    @property
    def tek_degeri(self) -> str | None:
        """Yuva TEK bir değer taşıyorsa o değer, aksi hâlde `None`."""
        maddeler = self.maddeler
        return maddeler[0] if len(maddeler) == 1 else None


@dataclass
class _Donem:
    ad: str
    yuvalar: dict[str, _Yuva]
    satirlar: list[str]
    yuva_sirasi: tuple[str, ...] = ()

    @property
    def bilincli_bos(self) -> bool:
        """K-120: DÖRT yuvanın hepsi AYNEN `içerik-önerilmez` mi?"""
        if set(self.yuvalar) != set(OZEL_GUN_YUVALARI):
            return False
        return all(
            yuva.tek_degeri == BILINCLI_BOS for yuva in self.yuvalar.values()
        )


@dataclass
class _Belge:
    ham: str
    bolumler: dict[str, list[str]]
    fazla_bolumler: list[str]
    alanlar: dict[str, _Yuva]
    yeniden_adlandirilmis: list[str]
    video_havuzlari: dict[str, _Yuva]
    donemler: list[_Donem]
    tablo_satirlari: list[str]
    tablo_var: bool
    # ── Yapısal iz: sözlük TEKRARI ve SIRAYI kaybeder, bunlar kaybetmez ────
    #
    # `bolumler`/`alanlar` sözlüktür; ikinci bir `Bölüm A` ya da ikinci bir
    # `kapsam` başlığı sözlükte İZ BIRAKMAZ. Sözleşmenin dilbilgisi (beş bölüm
    # SABİT sırayla, sekiz alan SIRAYLA) ancak sıralı-tekrarlı iz üstünde
    # ölçülebilir; "var mı" sorusu bu dört biçimi göremez.
    bolum_sirasi: tuple[str, ...] = ()
    alan_sirasi: tuple[str, ...] = ()
    bos_bolumler: tuple[str, ...] = ()
    tablo_sutun_sayilari: tuple[int, ...] = ()
    tablo_donem_sonrasi: bool = False
    # Gerekçe denetimine GİREN blokların sayımı. Seçim yoktur: denetim kümesi
    # dönem BÖLGESİNDEN önceki bütün tablolardır (yoksa hepsi). Bölge ilk dönem
    # BAŞLIĞINDA başlar — sınır `_ilk_donem_baslangici`'nda yaşar.
    gerekce_donem_oncesi_sayisi: int = 0
    gerekce_basliksiz_sayisi: int = 0
    # Bölüm C artık OLUMLU bir yapısal sözleşmedir: sözleşmenin BİREBİR başlık
    # satırı var mı, ve ayıraçtan sonra kaç veri satırı geliyor. Eski alan
    # (`c_esleme_satiri_var`) bir madde/tablo satırının VARLIĞINI ölçüyordu ve
    # serbest düzyazıyı ayırt edemiyordu — o eksen sözleşme sabit sütunlu
    # tabloyu dayattığı için artık TAHMİN gerektirmiyor.
    c_baslik_satiri_var: bool = False
    c_veri_satirlari: tuple[str, ...] = ()
    # Tur 1 yalnız BÖLÜM ve ALAN düzeyini kurtardı; aşağıdakiler iç içe KALAN
    # düzeylerin sıralı-tekrarlı izleridir. Düzey listesi belgenin KENDİ içerme
    # modelinden gelir (`_SABLON.md` §5 + GÖREV A/B adımları), bulunan
    # örneklerden değil: bölüm → alan → madde → video havuzu → havuz maddesi →
    # dönem → dönem yuvası → yuva maddesi → Bölüm C eşleme satırı.
    video_havuz_sirasi: tuple[str, ...] = ()
    donem_sirasi: tuple[str, ...] = ()
    c_esleme_satirlari: tuple[str, ...] = ()
    # Bölüm B gerekçe tablosundan okunan DÖNEM → SİSTEM ANAHTARLARI köprüsü
    # (sadeleştirilmiş dönem adı → anahtar demeti; `—` → boş demet). Yalnız
    # sözleşmenin sütun sayısını taşıyan ve hücresi ÇÖZÜLEN satırlar girer;
    # çözülmeyen hücre ihlal olarak AYRICA bildirilir ve köprüye GİRMEZ
    # (fail-closed: uydurma ya da bozuk anahtar köprü kurmaz).
    donem_anahtarlari: dict[str, tuple[str, ...]] = field(default_factory=dict)
    c_esleme_izleri: tuple[str, ...] = ()


_BOLUM_RE = re.compile(r"^\s*(?:#{1,6}\s*)?Bölüm\s+([^\s—\-:]+)")
_UST_BASLIK_RE = re.compile(r"^\s*#{1,2}\s+(\S.*?)\s*$")
_MADDE_RE = re.compile(r"^\s*-\s+(\S.*)$")
_TABLO_RE = re.compile(r"^\s*\|")
_TABLO_AYIRAC_RE = re.compile(r"^\s*\|[\s:\-|]+\|?\s*$")
_BASLIK_GORUNUMU_RE = re.compile(
    r"^\s*(?:#{1,6}\s+|\d+[a-z]?\s*[.)]\s+|\*\*[^*]+\*\*\s*:?\s*$|[A-Za-zÇĞİÖŞÜ_"
    r"çğıöşü][\w_]*\s*:)"
)
_ILK_SOZCUK_RE = re.compile(r"^\s*(?:#{1,6}\s+|\d+[a-z]?\s*[.)]\s*)?\*{0,2}`?([a-z_]+)")
# Markdown YATAY ÇİZGİSİ — bir AYRAÇTIR, içerik değil.
_YATAY_CIZGI_RE = re.compile(r"^\s*(?:-{3,}|\*{3,}|_{3,})\s*$")
# Markdown KOD ÇİTİ açıcı/kapatıcı satırı. İkinci grup INFO dizesidir: BOŞsa çit
# DİLSİZDİR (` ``` `), doluysa DİLLİDİR (` ```python `).
#
# **BAĞLAMDAN BAĞIMSIZ (tur 10).** Bir çit ayıracı, önünde GİRİNTİ ya da LİSTE
# İŞARETİ olsa da çit ayıracıdır. `^\s*` girintiyi zaten yutuyordu — ölçüldü:
# 2 ve 4 boşluk girintili çit notu KORUYORDU. Açık olan LİSTE BAĞLAMIYDI:
# `- ``` ` açıcı sayılmıyordu, dolayısıyla üç satırlık bir madde-içi blokta
# gövde (`  print(42)`) MASKESİZ kalıp kabı DOLDURUYOR, kapatıcı (`  ``` `) ise
# yeni bir açıcı sanılıp fail-closed kapanmamış çit açıyordu. Ölçüldü, aynı yuva:
#
#     yalniz '- ```' satiri                 kayip=0  [KORUNDU]
#     '- ```' + '  print(42)' + '  ```'     kayip=1  [KAYBOLDU]  <-- ACIK
#     ic ice madde '  - ```' + govde        kayip=1  [KAYBOLDU]  <-- ACIK
#     2 ve 4 bosluk girintili cit           kayip=0  [KORUNDU]
#
# **Tur 11 — liste işareti kümesi MARKDOWN'IN, sözleşmenin DEĞİL.** Tur 10 yalnız
# `-`'yi tanıyordu ve gerekçesi "sözleşmenin KENDİ madde kavramı odur" idi. O
# gerekçe İKİ ayrı soruyu birbirine karıştırıyordu: markdown'ın hangi satırı KAP
# (liste öğesi) saydığı ile sözleşmenin hangi madde işaretini KABUL ettiği ayrı
# şeylerdir. Ölçüldü, aynı yuva, mesaj KÜMESİ farkıyla:
#
#     '- ```' + govde + kapanis   kayip=0  [kapali]
#     '* ```' + govde + kapanis   kayip=1  <-- ACIK
#     '+ ```' + govde + kapanis   kayip=1  <-- ACIK
#     '1. ```' + govde + kapanis  kayip=1  <-- ACIK
#
# Küme artık CommonMark'ın liste dilbilgisinden TÜRER (`-` · `*` · `+` ve
# sıralı liste). Bu, `*` ile yazılmış bir maddeyi sözleşmeye UYGUN yapmaz:
# `_MADDE_RE` değişmedi ve `bicim-kurallari/ayri-madde-isareti` o satıra NOT
# düşmeye DEVAM eder — ölçülür. Markdown TANIMASI ile sözleşme KURALI ayrı
# yaşar; çitin içindeki kodu sözleşme içeriğine çeviren şey liste işareti değil,
# ÇİTİN KENDİSİDİR.
#
# **AŞIRI SIKILAŞTIRMA YAPILMADI:** ayıraç satırın TEK ANLAMLI İÇERİĞİ olmak
# ZORUNDADIR — `- gerçek bir kalıp` çit DEĞİLDİR ve kabı DOLDURMAYA devam eder.
# Kapatıcı eşleşmesi ayıracın KENDİSİNE bakar, satırın SOLUNA değil — açıcı
# girintiliyse kapatıcı da öyledir ve eşleşme buna TAKILMAZ.
#
# BİRİNCİ grup açıcının ÖNEKİDİR (girinti + varsa liste işareti) ve uzunluğu
# çitin KAP SÜTUNUDUR — `_kapsayici_kirildi` onu okur.
_LISTE_ISARETI = r"(?:[-*+]|\d{1,9}[.)])[ \t]+"
_KOD_CITI_RE = re.compile(
    r"^([ \t]*(?:" + _LISTE_ISARETI + r")?)(`{3,}|~{3,})[ \t]*(\S*)[ \t]*$"
)
# En az bir SÖZCÜK karakteri: hem düz yazının hem madde gövdesinin asgari işareti.
_SOZCUK_RE = re.compile(r"\w")


def _yuva_deseni(isimler: Sequence[str]) -> re.Pattern[str]:
    """Başlık satırı deseni: `### ad`, `ad`, `**ad**`, `ad: satır-içi değer`.

    Madde işaretli satırlar BİLEREK dışarıdadır: `- cta ...` bir başlık değil,
    içeriktir; alınsaydı dönem içindeki bir madde yuva başlığı sanılırdı.
    """
    alternatif = "|".join(
        re.escape(ad) for ad in sorted(isimler, key=len, reverse=True)
    )
    return re.compile(
        r"^\s*(?:#{1,6}\s+)?(?:\d+[a-z]?\s*[.)]\s*)?\*{0,2}`?("
        + alternatif
        + r")`?\*{0,2}\s*(?::\s*(.*?))?\s*$"
    )


_ALAN_DESENI = _yuva_deseni(TEMEL_ALANLAR)
_HAVUZ_DESENI = _yuva_deseni(VIDEO_HAVUZLARI)
_YUVA_DESENI = _yuva_deseni(OZEL_GUN_YUVALARI)


def _sadelestir(metin: str) -> str:
    """Karşılaştırma için sadeleştirme: kırp, markdown vurgusunu ve tırnağı at."""
    return metin.strip().strip("*`_ ").strip().casefold()


def alan_karsilastirma_anahtari(hucre: str) -> str:
    """Bölüm C `alan/dönem` hücresinin KARŞILAŞTIRMA anahtarı — TEK kural.

    Kapı, hücrenin kapalı kümeye üyeliğini `_sadelestir` ile ölçer; motor da
    aynı hücreyi kararın alanıyla karşılaştırır. İkinci bir sadeleştirme kuralı
    YAZILMAZ: iki taraf farklı normalleştirirse meşru bir satır motorda sessizce
    eşleşmez (kapı "geçerli" der, motor "bulamadım" der).
    """
    return _sadelestir(hucre)


def _baslik_metni(satir: str) -> str:
    return satir.strip().lstrip("#").strip().strip("*`").strip()


# ─── Doluluk kontrolünün AÇIK BIRAKTIĞI markdown blok biçimleri ────────────
#
# Envanter BURADA yaşar ve İKİ yerden okunur: kapsam beyanı (`CHECKS`) metnini
# buradan üretir, testi de her kalemin GERÇEKTEN bir kabın boşluk notunu
# kaldırdığını buradan ölçer. Böylece beyan BAYATLAYAMAZ — bir biçim kapanırsa
# test kırılır ve envanter güncellenmek ZORUNDA kalır.
#
# Bu görevde beyan BEŞ kez bayatladı; sonuncusu ölçüldü: envanter DİLSİZ kod
# çitini "elenen" sayıyordu, oysa yalnız SÖZCÜKSÜZ (gövdesiz) hâli eleniyordu —
# gövdeli ve kapanmamış hâlleri kabı DOLDURUYORDU (`notlu-gecti / 1 not` ->
# `gecti / 0 not`). O eksen `_citsiz_satirlar` ile KAPANDI; aşağıdaki üç kalem
# ölçülmüş olarak AÇIK kalır — gerçek çıktıda meşru kullanımları olabilir ve
# daraltmanın yanlış-pozitif maliyeti ÖLÇÜLMEDİ.
ACIK_BLOK_BICIMLERI: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("dilli kod çiti (```python)", ("```python\n", "print(42)\n", "```\n")),
    ("blockquote (`>`)", ("> alintilanmis bir cumle\n",)),
    ("HTML bloğu (`<div>`)", ("<div>alakasiz</div>\n",)),
)


# ─── DİLSİZ ÇİT KURALININ KAPSAMI — envanterin İKİNCİ ayağı ────────────────
#
# Kalem SAYISI burada YAZILMAZ — demetlerin kendisi kanoniktir ve test onları
# birebir eşler. Tur 8 çit kuralını KURDU ama yalnız TEK yola bağladı (doluluk). Tur 9'da
# ölçüldü ki AYNI içeriği okuyan KARDEŞ yollar çit-farkında DEĞİLDİ ve çite
# konan içerik notları KALDIRIYORDU (kapanış kanıtı SAYI değil, mesaj KÜMESİ
# farkıyla alındı: `cta_kaliplari` probunda not SAYISI 2 → 3 ARTMIŞTI ve alt
# sınır notu yine de SUSMUŞTU).
#
# Beyan artık "doluluk çit-farkındadır" demez; çit kuralının HANGİ yolları
# kapsadığını ve hangilerini BİLİNÇLE kapsamadığını sayar. İki demet TEK
# yerde yaşar, kapsam beyanı metnini buradan ÜRETİR ve test her kalemi
# UÇTAN UCA ölçer — kapsanan yolda çit not KALDIRAMAZ, kapsanmayan yolda çit
# içeriği HÂLÂ GÖRÜLÜR. Biri kayarsa test kırılır ve envanter güncellenmek
# ZORUNDA kalır. Bu görevde beyan BEŞ kez bayatladı.
CIT_KURALI_KAPSAMI: tuple[tuple[str, str], ...] = (
    ("doluluk", "`_Yuva.dolu` — kapta sözleşme biçiminde içerik var mı"),
    (
        "adet-sayimi",
        "`_Yuva.essiz_maddeler` — alan · video havuzu · dönem yuvası alt "
        "sınırları",
    ),
    ("madde-tekrar-izi", "`_madde_izi` — adet ailesinin TEKRAR ayağı"),
    (
        "bolum-boslugu",
        "`_Belge.bos_bolumler` — bölüm başlığı var, içerik yok",
    ),
    (
        "c-esleme-satiri",
        "Bölüm C tablosunun BAŞLIK satırı, veri satırları, tekrarı ve satır "
        "denetimi",
    ),
    (
        "gerekce-tablosu-tanima",
        "Bölüm B'de gerekçe tablosu bloklarının TANINMASI (konum korunur)",
    ),
    (
        "baslik-ve-bolum-tanima",
        "AYRIŞTIRICI düzeyi — bölüm · Bölüm A alanı · video havuzu · dönem "
        "yuvası başlıklarının TANINMASI. Maske ayrıştırmadan ÖNCE, belgenin "
        "TAMAMI üstünde hesaplanır (`_maskeli_satirlar`), dolayısıyla çit "
        "içindeki bir başlık YAPI KURAMAZ",
    ),
    (
        "ayri-madde-isareti",
        "`bicim-kurallari/ayri-madde-isareti` — içerik satırı madde işareti "
        "taşıyor mu; bu yolda ölçülmüş bir NOT KAYBI YOKTU, süpürme TUTARLILIK "
        "içindir: çit gövdesi için UYDURMA biçim notu üretiliyordu (ölçüldü: "
        "`'```'` satırı için `madde işareti olmayan içerik satırı`) ve modül "
        "aynı satırları doluluk/adet yollarında içerik SAYMIYOR",
    ),
)
# Ölçüt: kontrol SÖZLEŞME-BİÇİMLİ içerik mi arıyor (ele), yoksa HAM METİN mi
# tarıyor (ELEME)? Hepsini körlemesine elemek yeni bir YANLIŞ-NEGATİF sınıfı
# açardı — bir kod bloğunun içindeki İngilizce metin gerçekten İngilizcedir ve
# çite alınmış bir alıntı hâlâ alıntıdır.
CIT_KURALI_DISINDA: tuple[tuple[str, str], ...] = (
    (
        "dil-kurali",
        "HAM METİN taraması — çite alınmış Türkçe harf hâlâ oradadır; elemek "
        "kuralı çitle atlatılabilir yapardı (ölçüldü: çit içindeki Türkçe "
        "görsel kod maddesi HÂLÂ not üretir)",
    ),
    (
        "uzun-alinti",
        "HAM METİN taraması — kopya şüphesi çite alınmakla ortadan kalkmaz "
        "(ölçüldü: çit içindeki 45 kelimelik blok HÂLÂ not üretir)",
    ),
    (
        "govde-dipnotu",
        "HAM METİN taraması — dipnot/atıf işareti gövdede geçiyorsa geçiyordur",
    ),
    (
        "tur-etiketi-ascii",
        "HAM METİN taraması — `ticari-fırsat` yazımı belgede geçiyorsa "
        "geçiyordur",
    ),
    (
        "etiket-yazimi",
        "HAM METİN taraması — kanal/bağımlılık etiketleri belgenin tamamında "
        "aranır",
    ),
    (
        "k120-bilincli-bos",
        "FAIL-CLOSED tercih — `tek_degeri` HAM maddeleri okur; elenseydi çite "
        "saklanan içerik K-120 muafiyetini ALIRDI ve notlar DÜŞERDİ (ölçüldü: "
        "çite konan madde bugün muafiyeti BOZAR, 0 not → 4 not)",
    ),
)


# Çit ayıracının SOLUNDA durabilecek BAĞLAMLAR (tur 10) — envanter TEK yerde
# yaşar, kapsam beyanı metnini buradan ÜRETİR ve testi her kalemin GERÇEKTEN
# maskelendiğini uçtan uca ölçer. Kalemler markdown'un LİSTE DİLBİLGİSİNDEN
# türer, bulunan örnekten değil: bir çit ya blok düzeyindedir, ya bir liste
# öğesinin DEVAMIDIR, ya kod-girintisi eşiğindedir, ya doğrudan bir MADDE
# İŞARETİNDEN sonra açılır, ya da İÇ İÇE bir maddenin içindedir. İkinci üye
# AÇICININ öneki, üçüncüsü ondan sonraki satırların DEVAM GİRİNTİSİDİR.
CIT_BAGLAM_BICIMLERI: tuple[tuple[str, str, str], ...] = (
    ("girintisiz", "", ""),
    ("iki boşluk (madde devamı)", "  ", "  "),
    # NOT (tur 13): "dört boşluk" bu envanterden ÇIKARILDI. CommonMark'ta 4
    # sütun girinti bir ÇİT AÇMAZ — boş satırdan sonra GİRİNTİLİ KOD BLOĞU,
    # paragraftan sonra ise paragrafın DEVAMIDIR. Onu bir çit bağlamı saymak
    # ölçtüğünü sandığın şeyi ölçmemektir; girintili kod bloğu maskeye AYRI
    # olarak dahildir (`code_block`) ve kendi testiyle ölçülür.
    ("madde işaretli (`- `)", "- ", "  "),
    ("iç içe madde (`  - `)", "  - ", "    "),
    # Tur 11 — liste işareti kümesi MARKDOWN'IN, sözleşmenin DEĞİL. Tur 10 yalnız
    # `-`'yi tanıyordu ve gerekçesi sözleşmenin madde kuralıydı; iki soru ayrı
    # şeydir (ölçüldü: `* ``` ` ve `+ ``` ` birer not KALDIRIYORDU).
    ("yıldız madde (`* `)", "* ", "  "),
    ("artı madde (`+ `)", "+ ", "  "),
    ("sıralı liste (`1. `)", "1. ", "   "),
    # Tur 12 — AÇILIŞ GİRİNTİSİ ile GÖVDE GİRİNTİSİ AYRI boyutlardır. Tur 11'e
    # dek her bağlam gövdeyi açıcının girintisiyle yazıyordu, dolayısıyla eksen
    # "kök düzeyinde açılmış ama gövdesi girintisiz çit" bileşimini HİÇ
    # üretmiyordu — 96 hücrelik yapısal matris bu yüzden yeşil kalıyordu.
    # CommonMark 0-3 boşluklu açıcıyı kök sayar ve gövdesinden girinti İSTEMEZ
    # (`_kapsayici_sutunu`).
    ("bir boşluk kök (gövde girintisiz)", " ", ""),
    ("üç boşluk kök (gövde girintisiz)", "   ", ""),
)
# AYIRAÇ BİÇİMLERİ — CommonMark İKİ ayıraç karakteri ve EN AZ üç uzunluk tanır;
# tur 9'a dek yalnız üçlü backtick egzersiz ediliyordu.
CIT_AYIRAC_BICIMLERI: tuple[tuple[str, str], ...] = (
    ("üçlü backtick", "```"),
    ("dört backtick", "````"),
    ("üçlü tilde", "~~~"),
)


def _cit_kapsam_beyani() -> str:
    """Çit kuralının kapsam beyanı — İKİ demetin TÜREVİ, kopyası değil."""
    return (
        "bolum-ve-alan-tamligi/cit-kapsami: DİLSİZ kod çiti eleme kuralı TEK "
        "yerde yaşar (`_cit_maskesi`) ve MASKE BELGENİN TAMAMI ÜSTÜNDE, BİR KEZ, "
        "AYRIŞTIRMADAN ÖNCE hesaplanır (`_maskeli_satirlar`); satıra YAPIŞIR "
        "(`_Satir.cit_icinde`) ve hiçbir yol onu yerel olarak yeniden hesaplamaz "
        "— ikinci bir çit ayrıştırıcısı yazılmaz. Bölüm · Bölüm A alanı · video "
        "havuzu · dönem yuvası TANIMANIN hepsi MASKELENMİŞ görünümü okur: çit "
        "içindeki bir başlık YAPI KURAMAZ. **DÜZELTİLMİŞ BEYAN (tur 11):** bir "
        "önceki tur `baslik-ve-bolum-tanima` için 'kapsam dışı, fail-closed, "
        "yalnız NOT EKLER' diyordu ve ÖLÇÜM bunu YALANLADI — belgeden TAMAMEN "
        "silinen `cta_kaliplari` alanı, DİLSİZ bir çit içine konan sahte "
        "`### cta_kaliplari` başlığı ve beş maddeyle DOLU ve EKSİKSİZ "
        "gösteriliyordu (ölçüldü, mesaj KÜMESİ farkıyla: `notlu-gecti / 2 not` "
        "-> `gecti / 0 not`; TAM YUVA SAHTECİLİĞİ). Yol artık KAPSANANLAR "
        "arasındadır. HAM METİN tarayan yollar maskeyi GÖRMEZ ve görmemelidir: "
        "satırlar `str` türevi olarak ham kalır. KAPSANAN yollar: "
        + " · ".join(f"{ad} ({gerekce})" for ad, gerekce in CIT_KURALI_KAPSAMI)
        + ". BİLİNÇLE KAPSAM DIŞI bırakılanlar — ölçüt: kontrol SÖZLEŞME-BİÇİMLİ "
        "içerik mi arıyor yoksa HAM METİN mi tarıyor: "
        + " · ".join(f"{ad} ({gerekce})" for ad, gerekce in CIT_KURALI_DISINDA)
        + ". Kapsam dışı yolların hiçbiri bu turda ölçülmüş bir NOT KAYBI "
        "üretmiyor; ürettikleri fazladan notlar fail-closed yöndedir. "
        "Kalan altı kalemin HEPSİ ham metin tarar ve maskesiz satırı okur; "
        "hiçbiri sözleşme-biçimli içerik ARAMAZ. "
        "DİLLİ çit · blockquote · HTML bloğu hâlâ AÇIK kalemdir "
        "(`ACIK_BLOK_BICIMLERI`) ve kapsanan yolların HİÇBİRİNDE elenmez. "
        "ÇİT TANIMA BAĞLAMDAN BAĞIMSIZDIR (tur 10): bir ayıraç, önünde GİRİNTİ "
        "ya da LİSTE İŞARETİ olsa da ayıraçtır ve açıcısı · gövdesi · eşleşen "
        "kapatıcısı sayımdan çıkar; kapatıcı eşleşmesi satırın SOLUNA değil "
        "AYIRACIN KENDİSİNE bakar. LİSTE İŞARETİ kümesi MARKDOWN'IN kendi "
        "dilbilgisinden türer (`-` · `*` · `+` · sıralı liste), sözleşmenin madde "
        "kuralından DEĞİL — ikisi AYRI sorudur: `*` ile yazılmış bir madde "
        "sözleşme ihlalidir ve `bicim-kurallari/ayri-madde-isareti` ona NOT "
        "düşmeye DEVAM eder, ama bu, içindeki kodu sözleşme içeriğine ÇEVİRMEZ. "
        "DURUM MAKİNESİ KAP SONLANMASINI MODELLER (`_kapsayici_kirildi`): bir KAP "
        "İÇİNDE açılan çitin kapsamı, o kaptan daha AZ girintili boş-olmayan bir "
        "satırla BİTER — uzaktaki bir kök ayıracı onun kapatıcısı DEĞİLDİR "
        "(ölçüldü: `- ```python` → girintili gövde → kabı bitiren kök paragraf → "
        "kökte DİLSİZ çit bileşimi, eski makinede İKİ notu birden KALDIRIYORDU). "
        "**DÜZELTİLMİŞ BEYAN (tur 12) — KAP ÜYELİĞİ GİRİNTİ DEĞİLDİR.** Tur 11 "
        "kap sütununu ham girintiye eşitliyor ve kapatıcıyı kap kontrolünden "
        "ÖNCE sınıyordu; ikisi de ÖLÇÜLMÜŞ fail-open'dı ve `2 not -> 0 not` "
        "verdi: (a) `  ``` ` ile KÖKTE açılıp gövdesi GİRİNTİSİZ olan çit ilk "
        "gövde satırında kapanmış sanılıyor, içindeki sahte başlık YAPI "
        "kuruyordu; (b) kap içinde açılan çidin hemen ardından gelen BİTİŞİK kök "
        "ayıracı kapatıcı sanılıyor, sonrası maskesiz kalıyordu (o hücrede toplam "
        "not 2'den 16'ya ÇIKARKEN gerçek iki not KAYBOLUYORDU — sayı bunu gizler). "
        "Kap üyeliği artık `_kapsayici_sutunu`'ndan türer (CommonMark: 0-3 "
        "boşluklu açıcı KÖKTÜR) ve KAP kontrolü kapatıcıdan ÖNCE koşar. "
        "KÖK düzeyinde açılan kapanmamış çit için hiçbir satır kabı bitiremez ve "
        "çit FAIL-CLOSED olarak BELGE SONUNA kadar düşer; bunun ÖLÇÜLMÜŞ bedeli "
        "şudur: belgenin geri kalanı görünmez olduğu için SAYIM taşıyan bir not "
        "daha SIKI bir sayıyla yeniden yazılabilir (ör. `toplam 5 madde` -> "
        "`toplam 0 madde`) — notun KENDİSİ susmaz, sayısı düşer. Ölçülen "
        "BAĞLAMLAR: "
        + " · ".join(ad for ad, _on, _devam in CIT_BAGLAM_BICIMLERI)
        + ". Ölçülen AYIRAÇ biçimleri: "
        + " · ".join(f"{ad} ({isaret})" for ad, isaret in CIT_AYIRAC_BICIMLERI)
        + ". AŞIRI SIKILAŞTIRMA YAPILMADI: ayıraç satırın TEK ANLAMLI İÇERİĞİ "
        "olmak zorundadır — `- gerçek bir kalıp` çit DEĞİLDİR ve kabı "
        "DOLDURMAYA devam eder, `- ``` içeren bir kalıp` da çit sayılmaz."
    )


class _Satir(str):
    """Belgenin BİR ham satırı + o satırın ÇİT MASKESİ — AYRILAMAZ biçimde.

    **Tur 11'in yapısal ayağı budur.** Maske tur 8-10 boyunca satır dizisinden
    HER KULLANIM YERİNDE yeniden hesaplanıyordu (`_citsiz_satirlar(...)` yuva
    satırları üstünde, bölüm satırları üstünde, Bölüm B satırları üstünde). Bu
    yerel yeniden hesap iki şeyi birden bozuyordu:

      (a) bir DİLİM, çitin AÇICISINI içermeyebilir — o zaman gövde MASKESİZ
          kalır ve kapatıcı yeni bir açıcı sanılır;
      (b) AYRIŞTIRMA hiç maske görmüyordu — çit içindeki `### cta_kaliplari`
          gerçek bir alan başlığı sayılıyor ve OLMAYAN bir alan DOLU
          görünüyordu (ölçüldü, mesaj KÜMESİ farkıyla: `2 not → 0 not`, sonuç
          `gecti`).

    Kapatma bir üçüncü kural DEĞİL: maske belgenin TAMAMI üstünde, BİR KEZ,
    ayrıştırmadan ÖNCE hesaplanır (`_maskeli_satirlar`) ve satıra YAPIŞIR. Satır
    nereye taşınırsa maskesi de oraya gider; dilim alan bir yol maskeyi yeniden
    hesaplayamaz çünkü hesaplayacak bir şey kalmamıştır.

    Tip `str` TÜREVİDİR ve bu bilinçlidir: HAM METİN tarayan yollar (dil kuralı ·
    uzun alıntı · gövde dipnotu · tür etiketi · etiket yazımı) satırı OLDUĞU GİBİ
    görmeye devam eder — çite alınmış Türkçe harf hâlâ oradadır.
    """

    cit_icinde: bool

    def __new__(cls, ham: str, cit_icinde: bool) -> "_Satir":
        nesne = super().__new__(cls, ham)
        nesne.cit_icinde = bool(cit_icinde)
        return nesne


def _cit_icinde(satir: str) -> bool:
    """Satır bir DİLSİZ çit bloğuna mı ait? (maskesiz satır için `False`)"""
    return bool(getattr(satir, "cit_icinde", False))


def _yapi_kurmaz(satir: str) -> bool:
    """Satır BAŞLIK olamaz mı — yani belgenin YAPISINI kuramaz mı?

    İki durum: (a) satır DİLSİZ bir çit bloğunun içindedir; (b) satırın kendisi
    bir çit AYIRACIDIR. İkincisi DİLLİ çit için de geçerlidir ve ayrı bir
    karardır: `ACIK_BLOK_BICIMLERI` dilli çitin bir kabı DOLDURMAYA devam
    ettiğini söyler — doluluk ayrı, YAPI ayrıdır. Bir çit ayıracı hiçbir
    markdown ayrıştırıcısında başlık değildir; ölçüldü ki aksi hâlde
    `1. ```python` satırı `_BASLIK_GORUNUMU_RE`'ye uyup bir DÖNEM bloğunu
    KAPATIYOR ve dilli çitin ilan edilmiş ŞEFFAFLIĞINI bozuyordu.
    """
    return _cit_icinde(satir) or bool(_KOD_CITI_RE.match(satir))


def _maskeli_satirlar(source_text: str) -> list[_Satir]:
    """Belgeyi satırlara böler ve ÇİT MASKESİNİ BİR KEZ, burada hesaplar.

    Ayrıştırmanın TEK girdisi budur: `_ayristir` ham `splitlines()` çağırmaz.
    Böylece bölüm · alan · video havuzu · dönem yuvası tanımanın hepsi
    MASKELENMİŞ görünüm üzerinden çalışır ve çit içindeki bir başlık yapı
    kuramaz.
    """
    ham = source_text.splitlines()
    return [
        _Satir(satir, cit_icinde)
        for satir, cit_icinde in zip(ham, _cit_maskesi(ham))
    ]


def _citsiz_satirlar(satirlar: Sequence[str]) -> list[str]:
    """DİLSİZ çit bloğuna ait satırları ELER — SÜZGEÇ, hesap DEĞİL.

    **Neden satır DİZİSİ (tur 8).** `_sozlesme_bicimli` satırı TEK TEK
    değerlendirir ve bir kod bloğu satır-tek-tek görülemez: çıplak ` ``` `
    ayıracı sözcük taşımadığı için zaten eleniyordu, ama çitin İÇİNDEKİ satır
    (`print(42)`) "sözcük içeriyor" diye kabı DOLDURUYORDU. Ölçüldü, aynı belge
    ve aynı yuva:

        yuva bos (taban)             notlu-gecti  not=1
        ciplak ``` (bos govde)       notlu-gecti  not=1
        ``` + print(42) + ```        gecti        not=0
        ``` + duz cumle + ```        gecti        not=0
        kapanmamis ``` + govde       gecti        not=0

    Satır-tek-tek bakan bir kural DİZİ gerektiren bir yapıyı ÖLÇEMEZ; bu yüzden
    eleme burada, doluluk sayımının GİRDİSİNDE yapılır.

    **Kapanmamış dilsiz çit FAIL-CLOSED düşer:** açık kalan bir çit "gerisi hep
    gövde" demektir, dolayısıyla açıcıdan blok sonuna kadar hiçbir satır kabı
    doldurmaz. Ölçüm bunu doğruladı — kapanmamış hâl de notu kaldırıyordu. (Tur
    11: maske belge geneli olduğu için sınır artık BELGE sonudur; KAP İÇİNDE
    açılan çit ise kabı bitiren ilk satırda biter — `_kapsayici_kirildi`.)

    **DİLLİ çite DOKUNULMAZ (ilan edilmiş açık kalem).** ` ```python ` bloğu
    açıcısıyla, gövdesiyle ve kapatıcısıyla OLDUĞU GİBİ kalır: gerçek çıktıda
    meşru kullanımı olabilir ve daraltmanın yanlış-pozitif maliyeti ÖLÇÜLMEDİ.
    Envanteri `ACIK_BLOK_BICIMLERI`'nde yaşar ve testi onu sabitler.

    Kapatıcı eşleşmesi CommonMark'ın kuralını izler: aynı işaret karakteri, en az
    açıcı kadar uzun ve INFO dizesi BOŞ. Eşleşme satırın SOLUNA BAKMAZ (tur 10):
    açıcı girintiliyse ya da bir LİSTE İŞARETİNDEN sonra geliyorsa kapatıcı da
    girintilidir, ve eşleşme buna TAKILMAZ.

    **Tur 11 — bu fonksiyon artık HESAP YAPMAZ, yalnız SÜZER.** Maske belgenin
    TAMAMI üstünde bir kez hesaplanır (`_maskeli_satirlar`) ve satıra YAPIŞIR
    (`_Satir.cit_icinde`); burada yerel bir yeniden hesap yapmak tam olarak
    kapatılan hatanın kendisiydi — açıcıyı içermeyen bir DİLİM üstünde maske
    yeniden hesaplanınca gövde maskesiz kalıyor, kapatıcı yeni bir açıcı
    sanılıyordu. Maskesiz (`str`) bir dizi verilirse hiçbir satır elenmez;
    ayrıştırmadan geçen bütün yollar `_Satir` taşır.
    """
    return [satir for satir in satirlar if not _cit_icinde(satir)]


# CommonMark referans-uyumlu blok ayrıştırıcı — TEK örnek, durumsuz ve
# yeniden girişli. "commonmark" ön ayarı bilerek seçildi: tablo/strikethrough
# gibi eklentiler kod bloğu sınırlarını değiştirmez ama gramerden UZAKLAŞTIRIR;
# burada istenen şey saf CommonMark'ın kendisidir.
# `maxNesting` BILEREK yukseltildi (varsayilan 20). Olculdu (2026-09-07,
# mesaj KUMESI farkiyla): 11 kat ic ice listenin altinda acilan kapanmamis
# dilsiz cit ayristiricinin ic ice gecme sinirina takiliyor, o bolge HIC
# tokenlanmiyor ve icindeki sahte `### cta_kaliplari` basligi MASKESIZ
# kaliyordu — gercek alan tamamen silinmisken rapor `gecti / 0 not` donuyordu.
# Sinir 10'da kapali, 11'de acikti. Deger 1000'e cekildi: derinlik 200'de acik
# KAPALI, temiz rapor DEGISMEDI, derinlik-400 belgesi 0.17 sn'de kosuyor
# (varsayilanla 0.10 sn) — patolojik girdi maliyeti olculdu, kabul edilebilir.
# Deger 1000 DENENDI ve GERI ALINDI: o esikte 1200 kat ic ice blockquote
# ayristiriciyi `RecursionError` ile dusuruyor (olculdu) — yani yuksek sinir
# fail-open'i kapatirken bir COKME yolu aciyor. 100 secildi: gercekci
# belgenin cok uzerinde, Python'un ozyineleme sinirinin cok altinda.
# Sinir hala SONLUDUR ve bu KAYITLIDIR: 100 kattan derin ic ice yapi tasiyan
# bir belgede ayni sinif yeniden acilir. O yol artik SESSIZ degil —
# `RecursionError` fail-closed yakalanir (asagida) ve belge TAMAMEN literal
# sayilir, yani rapor temiz GECMEZ.
_MD = MarkdownIt("commonmark", {"maxNesting": 100})


def _cit_maskesi(satirlar: Sequence[str]) -> list[bool]:
    """Satır başına: LİTERAL bir kod bloğuna mı ait (açıcı · gövde · kapatıcı)?

    ÇİT TANIMA KURALININ TEK EVİ. `_citsiz_satirlar` bunun süzgeç yüzeyidir;
    satır KONUMUNU korumak zorunda olan süpürme yolları (Bölüm B tablo izi)
    maskeyi doğrudan okur — maske satırın kendisine yapışır (`_Satir`).

    **Tur 13 — GRAMERİ YENİDEN YAZMIYORUZ, KOŞTURUYORUZ.** Tur 8-12 arasında bu
    fonksiyon elle yazılmış bir CommonMark YAKLAŞIMIYDI ve her turda gramerin
    kodlanmamış bir kuralı daha çıktı; her seferinde bir SINIR KURALI eklendi:

        tur 10  ayıracın önünde girinti/liste işareti olabilir
        tur 11  liste işareti kümesi markdown'ın, sözleşmenin değil
        tur 12  açılış girintisi kap üyeliği DEĞİLDİR (0-3 boşluk köktür)
        tur 12  kap kontrolü kapatıcı kontrolünden ÖNCE koşar
        tur 13  KAPATICI GİRİNTİSİ de kuralın parçası (en fazla 3 boşluk)
        tur 13  iç içe liste işaretleri (`- - ``` `) tek işaretle modellenemez

    Beşinci ve altıncı sınır kuralını yazmak yerine sınıf YAPIYLA kapatıldı:
    maske artık CommonMark referans-uyumlu bir blok ayrıştırıcıdan
    (`markdown-it-py`) türer. Kaçışlar "aklımıza gelen" bileşimlerle değil,
    gramerin KENDİSİYLE sınırlanır; matrisin kör noktası artık kendi hayal
    gücümüz kadar değildir. Bu, yürütme protokolünün M6 hükmünün de karşılığıdır
    (dış gramer modelleyen guardrail'de çalıştırılabilir ground-truth ZORUNLU).

    **Maskelenen küme — GEREKÇESİYLE:** ayrıştırıcının LİTERAL saydığı iki blok,
    yani DİLSİZ çit (`fence`, info boş) ve GİRİNTİLİ kod bloğu (`code_block`).
    İkisi de sözleşme içeriği OLAMAZ ve ikisinin içindeki bir başlık YAPI
    KURAMAZ. DİLLİ çit BİLEREK maskelenmez: `ACIK_BLOK_BICIMLERI` onun bir kabı
    DOLDURMAYA devam ettiğini söyler — doluluk ayrı, YAPI ayrıdır.

    Kapanmamış çit FAIL-CLOSED kalır: CommonMark böyle bir çiti KAPSAYAN BLOĞUN
    sonuna kadar sürdürür, dolayısıyla kök düzeyinde açılmışsa belge sonuna
    kadar düşer. Bu davranış artık bizim kuralımız değil, gramerin kuralıdır.

    Satır indisleri ÇAĞIRANIN dizisiyle hizalıdır: metin `"\n"` ile birleştirilip
    ayrıştırılır, dolayısıyla `splitlines()`'ın markdown-it'ten farklı böldüğü
    ayraçlar (`\x0b`, `\u2028` gibi) indis kaymasi yaratamaz.
    """
    maske = [False] * len(satirlar)
    try:
        jetonlar = _MD.parse("\n".join(satirlar))
    except RecursionError:
        # FAIL-CLOSED: ayristirici belgeyi COZEMEDI. Bos maske dondurmek
        # fail-OPEN olurdu (her sey yapi sayilir); belgenin TAMAMI literal
        # sayilir, dolayisiyla butun bolumler EKSIK gorunur ve rapor temiz
        # GECEMEZ. Sessiz basari YOK.
        return [True] * len(satirlar)
    for jeton in jetonlar:
        if jeton.map is None:
            continue
        if jeton.type == "code_block" or (
            jeton.type == "fence" and not (jeton.info or "").strip()
        ):
            bas, son = jeton.map
            for k in range(max(bas, 0), min(son, len(maske))):
                maske[k] = True
    return maske


def _sozlesme_bicimli(parca: str) -> bool:
    """Satır, sözleşmenin bir KABI DOLDURAN içerik biçimlerinden biri mi?

    Kabul kümesi SÖZLEŞME METNİNDEN türer, örnekten değil. `_SABLON.md` bir
    kabın içeriğini ÜÇ biçimde tanır:

      * DÜZ YAZI satırı — ADIM 3 `mesaj_ekseni` ("dönemin duygusal ekseni ve
        SEKTÖRE özgü açısı. Kısa ve yoğun.") ve BİÇİM KURALLARI md. 1'in düz
        metin alanları (`kapsam` · `ton_ve_dil`);
      * MADDE İŞARETLİ satır — ADIM 3 `kanca`/`cta`/`gorsel_vurgu` ve BİÇİM
        KURALLARI md. 3 ("Her kalıp / anahtar ifade AYRI madde işareti (-)
        olsun");
      * resmî `içerik-önerilmez` değeri — BİLİNÇLİ BOŞ muafiyeti (K-120).

    Markdown TABLOSU bunların HİÇBİRİ değildir: sözleşme tabloyu YALNIZ Bölüm
    B'nin gerekçe tablosu ve Bölüm C'nin eşlemesi için tanır, bir ALANIN ya da
    dönem YUVASININ içeriği olarak DEĞİL. Yatay çizgi de içerik değil ayraçtır.

    **Ölçülmüş fail-open (tur 7):** doluluk kontrolü "boş olmayan HERHANGİ bir
    satır" sayıyordu, dolayısıyla sözleşmeye UYMAYAN bir blok kabı doldurmuş
    sayılıyordu. Ölçüldü: ilk dönemin `mesaj_ekseni` yuvası boşaltılınca rapor
    `notlu-gecti / 1 not`; AYNI yuvaya bağımsız iki sütunlu bir markdown
    tablosu eklenince `gecti / 0 not`. Yani bir TABLO EKLEMEK bloğa ait bir
    notu kaldırıyordu — ekleme değişmezinin kendi ilan ettiği kapsam içinde
    ihlali.

    **Aşırı sıkılaştırma bilinçle YAPILMADI:** hangi kabın hangi biçimi
    isteyeceği (yuva bazında düz yazı mı madde mi) burada DAYATILMAZ — gerçek
    çıktılar `mesaj_ekseni`'ni madde olarak da yazar ve liste alanlarındaki
    paragraf zaten `bicim-kurallari/ayri-madde-isareti` ailesinde ölçülür.
    Burada yalnız sözleşmenin HİÇ tanımadığı iki markdown BLOK yapısı elenir.

    **Kapsam sınırı (tur 8):** bu fonksiyon SATIRA bakar ve bir DİZİ gerektiren
    yapıyı ölçemez. Kod çiti tam olarak öyle bir yapıdır — çıplak ` ``` `
    ayıracı burada sözcüksüz olduğu için zaten elenir, ama çitin GÖVDESİ
    tek başına bakıldığında sözleşme biçimli görünür. Dilsiz çit BLOĞUNUN
    elenmesi bu yüzden burada değil, doluluk sayımının girdisinde yapılır
    (`_citsiz_satirlar`).
    """
    govde = parca.strip()
    if not govde:
        return False
    if _TABLO_RE.match(govde) or _YATAY_CIZGI_RE.match(govde):
        return False
    madde = _MADDE_RE.match(govde)
    return bool(_SOZCUK_RE.search(madde.group(1) if madde else govde))


def _bloklara_ayir(
    satirlar: Iterable[str], desen: re.Pattern[str]
) -> tuple[dict[str, _Yuva], tuple[str, ...]]:
    """Blokları ada göre sözlükler VE başlıkların görülme sırasını döndürür.

    İkinci dönüş değeri TEKRARLIDIR ve SIRALIDIR: sözlük ikisini de kaybeder,
    sözleşmenin dilbilgisi ise ikisini de sorar.

    **Tanıma MASKELENMİŞ görünüm üzerinden yapılır (tur 11):** çit içindeki bir
    `### cta_kaliplari` satırı BAŞLIK DEĞİLDİR ve blok AÇMAZ — açsaydı olmayan
    bir sözleşme alanı dolu görünürdü (ölçüldü: `2 not → 0 not`). Satır yine de
    açık bloğun gövdesine EKLENİR: ham metin tarayan yollar onu görmeye devam
    eder.
    """
    bloklar: dict[str, _Yuva] = {}
    sira: list[str] = []
    aktif: _Yuva | None = None
    for satir in satirlar:
        eslesme = None if _yapi_kurmaz(satir) else desen.match(satir)
        if eslesme:
            ad = eslesme.group(1)
            aktif = _Yuva(ad=ad, inline=(eslesme.group(2) or "").strip())
            bloklar[ad] = aktif
            sira.append(ad)
            continue
        if aktif is not None:
            aktif.satirlar.append(satir)
    return bloklar, tuple(sira)


def _ayristir(source_text: str) -> _Belge:
    """Rapor metnini bölümlere, alanlara ve dönemlere ayırır.

    Bölüm tanıma iki işarete dayanır: `Bölüm <harf>` kalıbı ve markdown başlık
    DÜZEYİ. 1-2 düzey başlık bölüm sayılır; 3+ düzey bölüm içi kabul edilir. Bu
    bir mekanik vekildir — sözleşme markdown düzeyi dayatmaz.

    **Tur 11 — GİRDİ MASKELENMİŞTİR.** Ayrıştırma ham `splitlines()` çağırmaz;
    tek girdisi `_maskeli_satirlar`'dır ve maske belgenin TAMAMI üstünde BİR KEZ,
    burada başlamadan ÖNCE hesaplanmıştır. Bölüm · alan · video havuzu · dönem
    yuvası tanımanın hepsi maskelenmiş görünümü okur: çit içindeki bir başlık
    YAPI KURAMAZ. Satırların KENDİSİ ham kalır (`_Satir` bir `str` türevidir),
    dolayısıyla ham metin tarayan kontroller çit içeriğini görmeye DEVAM eder.
    """
    bolumler: dict[str, list[str]] = {}
    bolum_sirasi: list[str] = []
    fazla: list[str] = []
    aktif: str | None = None

    for satir in _maskeli_satirlar(source_text):
        if _yapi_kurmaz(satir):
            # Çit içindeki satır YAPI KURMAZ ama gövdede KALIR.
            if aktif is not None:
                bolumler[aktif].append(satir)
            continue
        bolum = _BOLUM_RE.match(satir)
        if bolum:
            harf = bolum.group(1).strip().upper()
            if harf in BOLUM_HARFLERI:
                aktif = harf
                bolumler.setdefault(harf, [])
                bolum_sirasi.append(harf)
            else:
                fazla.append(_baslik_metni(satir))
                aktif = None
            continue
        ust = _UST_BASLIK_RE.match(satir)
        if ust:
            fazla.append(ust.group(1).strip())
            aktif = None
            continue
        if aktif is not None:
            bolumler[aktif].append(satir)

    # BÖLÜM boşluğu da ÇİT-FARKINDADIR (tur 9): ölçüldü ki bir bölümün altına
    # konan DİLSİZ çit — GÖVDESİ BOŞ olanı bile — "Bölüm X boş" notunu
    # kaldırıyordu (50 hücrenin 50'si). Bu kural bölüm düzeyinde `_sozlesme_bicimli`
    # DEĞİLDİR ve öyle olmamalıdır (sözleşme tabloyu Bölüm B gerekçesi ve Bölüm C
    # eşlemesi olarak TANIR); çit ise sözleşmenin HİÇBİR yerde tanımadığı bir
    # yapıdır, dolayısıyla eleme bu düzeyde de geçerlidir.
    bos_bolumler = tuple(
        harf
        for harf in BOLUM_HARFLERI
        if harf in bolumler
        and not any(satir.strip() for satir in _citsiz_satirlar(bolumler[harf]))
    )

    a_satirlari = bolumler.get("A", [])
    alanlar, alan_sirasi = _bloklara_ayir(a_satirlari, _ALAN_DESENI)

    # "Tam alan adı" ihlali: başlık görünümlü bir satırın ilk sözcüğü bir alan
    # adı ama satırın kendisi o alan adı DEĞİL (ör. "kapsam ve tanım").
    yeniden_adlandirilmis: list[str] = []
    for satir in a_satirlari:
        if _yapi_kurmaz(satir):
            continue
        if _ALAN_DESENI.match(satir) or not _BASLIK_GORUNUMU_RE.match(satir):
            continue
        ilk = _ILK_SOZCUK_RE.match(satir)
        if ilk and ilk.group(1) in TEMEL_ALANLAR:
            yeniden_adlandirilmis.append(_baslik_metni(satir))

    video = alanlar.get("video_kodlar")
    if video:
        video_havuzlari, video_havuz_sirasi = _bloklara_ayir(
            video.satirlar, _HAVUZ_DESENI
        )
    else:
        video_havuzlari, video_havuz_sirasi = {}, ()

    b_satirlari = bolumler.get("B", [])
    donemler: list[_Donem] = []
    aktif_donem: _Donem | None = None
    son_baslik: str | None = None
    son_baslik_sirasi: int | None = None
    donem_bolgesi_basi: int | None = None
    ham_tablo_izleri: list[tuple[int, str]] = []

    # Tablo TANIMA da çit-farkındadır (tur 9): ölçüldü ki Bölüm B'de dönem
    # başlıklarından ÖNCE DİLSİZ bir çitin içine konan tablo "gerekçe tablosu
    # yok" notunu KALDIRIYORDU. Maske KONUMU korur — blok bitişikliği ve dönem
    # bölgesi sınırı satır sırasına bakar. Tur 11: maske artık satırın KENDİSİNDE
    # taşınır, burada YENİDEN HESAPLANMAZ (dilim üstünde yeniden hesap tam olarak
    # kapatılan hataydı) — ve DÖNEM BAŞLIĞI tanıma da aynı maskeyi okur.
    for sira, satir in enumerate(b_satirlari):
        if _yapi_kurmaz(satir):
            if aktif_donem is not None:
                aktif_donem.satirlar.append(satir)
            continue
        if _TABLO_RE.match(satir):
            ham_tablo_izleri.append((sira, satir))
        yuva = _YUVA_DESENI.match(satir)
        if yuva and yuva.group(1) == "mesaj_ekseni":
            aktif_donem = _Donem(
                ad=son_baslik or f"dönem-{len(donemler) + 1}",
                yuvalar={},
                satirlar=[satir],
            )
            donemler.append(aktif_donem)
            if donem_bolgesi_basi is None:
                donem_bolgesi_basi = _ilk_donem_baslangici(son_baslik_sirasi, sira)
            continue
        if not yuva and _BASLIK_GORUNUMU_RE.match(satir):
            # Yuva olmayan bir başlık dönemi KAPATIR: sonraki dönemin adı budur.
            son_baslik = _baslik_metni(satir)
            son_baslik_sirasi = sira
            aktif_donem = None
            continue
        if aktif_donem is not None:
            aktif_donem.satirlar.append(satir)

    # Konum bayrağı DÖNGÜDEN SONRA hesaplanır: dönem bloğu BAŞLIĞIYLA başlar ama
    # başlığın dönem başlığı OLDUĞU ancak ilk yuvası görülünce bilinir.
    tablo_izleri = [
        (sira, satir, donem_bolgesi_basi is not None and sira >= donem_bolgesi_basi)
        for sira, satir in ham_tablo_izleri
    ]

    tablo_bloklari = _tablo_bloklari(tablo_izleri)
    secilen_bloklar, gerekce_donem_oncesi_sayisi = _gerekce_tablosu(tablo_bloklari)
    # Konum notu KÜME düzeyinde bir YOKLUK iddiasıdır ("gerekli yerde tablo
    # yok, olan tablo dönemlerden sonra"), bir bloğun içeriği hakkında değil —
    # bu yüzden denetim kümesinden DEĞİL, bütün bloklardan türer.
    tablo_donem_sonrasi = not secilen_bloklar and any(
        blok and blok[0][2] for blok in tablo_bloklari
    )
    # Kanonik başlık artık SEÇMEZ, yalnız NOT besler: denetime giren kaç blok
    # gerekçe tablosunun kanonik başlığını taşımıyor?
    gerekce_basliksiz_sayisi = sum(
        1
        for blok in secilen_bloklar
        if blok and _gerekce_basligi_puani(blok[0][1]) < GEREKCE_BASLIK_ASGARI
    )

    for donem in donemler:
        donem.yuvalar, donem.yuva_sirasi = _bloklara_ayir(
            donem.satirlar, _YUVA_DESENI
        )

    # Sayımlar blok BAŞINA yürür: birden çok aday varken tek bir akışa
    # düzleştirmek ikinci bloğun BAŞLIK satırını veri sanırdı.
    tablo_veri_satirlari: list[str] = []
    sutun_sayilari: list[int] = []
    for blok in secilen_bloklar:
        blok_satirlari = [satir for _, satir, _ in blok]
        tablo_veri_satirlari += _tablo_veri_satirlari(blok_satirlari)
        sutun_sayilari += [
            len(_hucreler(satir))
            for satir in blok_satirlari
            if not _TABLO_AYIRAC_RE.match(satir)
        ]
    tablo_sutun_sayilari = tuple(sutun_sayilari)
    donem_anahtarlari = _donem_anahtarlari(tablo_veri_satirlari)

    c_satirlari = bolumler.get("C", [])
    # Eşleme satırı sayımı da çit-farkındadır (tur 9): ölçüldü ki Bölüm C'nin
    # eşlemesi silinip yerine DİLSİZ çit içinde madde ya da tablo satırı
    # konduğunda "Bölüm C tek bir kaynak eşleme satırı taşımıyor" notu
    # KAYBOLUYORDU.
    c_citsiz = _citsiz_satirlar(c_satirlari)
    c_esleme_satirlari = tuple(
        satir
        for satir in c_citsiz
        if (_MADDE_RE.match(satir) or _TABLO_RE.match(satir))
        and not _TABLO_AYIRAC_RE.match(satir)
    )
    # Sözleşmenin BİREBİR başlık satırı — kapının olumlu sözleşmesi. Hücre
    # bazında karşılaştırılır (boşluk/hizalama serbest), sütun ADLARI değil.
    c_baslik_satiri_var = any(
        _hucreler(satir) == list(C_TABLOSU_SUTUNLARI)
        for satir in c_citsiz
        if _TABLO_RE.match(satir)
    )
    # Veri satırları = ayıraçtan SONRAKİ tablo satırları; başlık satırı veri
    # DEĞİLDİR (aynı yardımcı Bölüm B gerekçe tablosunda da kullanılır).
    c_veri_satirlari = tuple(_tablo_veri_satirlari(c_citsiz))

    return _Belge(
        ham=source_text,
        bolumler=bolumler,
        fazla_bolumler=fazla,
        alanlar=alanlar,
        yeniden_adlandirilmis=yeniden_adlandirilmis,
        video_havuzlari=video_havuzlari,
        donemler=donemler,
        tablo_satirlari=tablo_veri_satirlari,
        tablo_var=bool(tablo_veri_satirlari),
        bolum_sirasi=tuple(bolum_sirasi),
        alan_sirasi=alan_sirasi,
        bos_bolumler=bos_bolumler,
        tablo_sutun_sayilari=tablo_sutun_sayilari,
        tablo_donem_sonrasi=tablo_donem_sonrasi,
        gerekce_donem_oncesi_sayisi=gerekce_donem_oncesi_sayisi,
        gerekce_basliksiz_sayisi=gerekce_basliksiz_sayisi,
        c_baslik_satiri_var=c_baslik_satiri_var,
        c_veri_satirlari=c_veri_satirlari,
        video_havuz_sirasi=video_havuz_sirasi,
        donem_sirasi=tuple(_sadelestir(donem.ad) for donem in donemler),
        c_esleme_satirlari=c_esleme_satirlari,
        c_esleme_izleri=tuple(_sadelestir(satir) for satir in c_esleme_satirlari),
        donem_anahtarlari=donem_anahtarlari,
    )


def _ilk_donem_baslangici(baslik_sirasi: int | None, yuva_sirasi: int) -> int:
    """Dönem bölgesinin BAŞLADIĞI satır — gerekçe denetim bölgesinin SINIRI.

    Bir dönem bloğu BAŞLIĞIYLA başlar, ilk yuvasıyla değil: `### Sevgililer
    Günü` satırından sonra gelen her tablo o DÖNEME aittir. Ayrıştırıcı dönemi
    ancak `mesaj_ekseni` yuvasını görünce KURABİLİR (başlığın dönem başlığı
    olduğu o an anlaşılır), bu yüzden sınır geriye dönük olarak BAŞLIĞA çekilir.

    **Ölçülmüş gerileme (tur 5):** bir önceki tur bölgeyi `bool(donemler)` ile
    kapatıyordu, yani ilk YUVADA. Dönem başlığı ile o dönemin ilk yuvası
    ARASINA konan bir tablo hâlâ "dönem öncesi" sayılıyor ve gerekçe denetimine
    giriyordu. Ölçüldü (46579a1 vs 7075658, aynı belge): `0 not → 4 not`.

    Bu bir SEÇİM sezgiseli DEĞİLDİR — v2/v3/v4'ün her turda bir yemle
    kandırılan aday-seçme kuralları gibi çalışmaz; hangi tablonun denetleneceği
    yine SEÇİLMEZ, yalnız bölgenin sınırı sözleşmenin sırasından okunan doğru
    yere konur ("önce tablo, sonra dönem dönem dört başlık").

    Başlıksız bir ilk dönemde (belge başlık yazmamışsa) bölge ilk YUVADA biter:
    ikinci dal fail-open değildir, tabloyu denetim İÇİNDE bırakır.

    **Kapsam sınırı (İlke 9(4)) — ÖLÇÜLMÜŞ.** "İlk dönemin başlığı" = ilk
    yuvadan ÖNCEKİ SON başlık görünümü. Belge ilk döneme başlık yazmamış AMA
    gerekçe tablosunun üstüne bir alt yazı başlığı koymuşsa o alt yazı ilk
    dönemin başlığı SANILIR, tablo dönem bölgesinde kalır ve denetim DIŞINDA
    olur; dönem ADI da yanlış türer. Ayrı bir kural YAZILMADI — bu dal beş
    gerçek çıktının hiçbirinde görülmedi (beşinde de Bölüm B tablosuzdur).

    **Bu dalın ZARARI artık SINIRLIDIR (tur 6).** Önceki tur burada "tablo
    SUSTURULMAZ" diye beyan ediyordu; ölçüm bunu YALANLADI: fail-open geri
    dönüş yüzünden dönem-öncesi TEK bir yem, bu dalda kalan gerçek tablonun
    SEKİZ notunu birden düşürüyordu (`9 not → 0 not`). Denetim kümesi artık
    MONOTONdur (`_gerekce_tablosu`), yani bir EKLEME hiçbir bloğu kümeden
    çıkaramaz; bu dalda kalan tablo denetlenmez ama denetlenmemesi bir
    EKLEMEYE de bağlı DEĞİLDİR — belgeye tablo eklemek notları eksiltemez.
    """
    return yuva_sirasi if baslik_sirasi is None else baslik_sirasi


def _tablo_bloklari(
    izler: Sequence[tuple[int, str, bool]]
) -> list[list[tuple[int, str, bool]]]:
    """Bölüm B'deki `|` satırlarını BİTİŞİK bloklara ayırır — tablo birimi budur."""
    bloklar: list[list[tuple[int, str, bool]]] = []
    for iz in izler:
        if bloklar and iz[0] == bloklar[-1][-1][0] + 1:
            bloklar[-1].append(iz)
        else:
            bloklar.append([iz])
    return bloklar


def _gerekce_basligi_puani(satir: str) -> int:
    """Bir tablo BAŞLIK satırının kanonik gerekçe anahtarı sayısı."""
    govde = " | ".join(_hucreler(satir)).casefold()
    return sum(
        1
        for anahtar in GEREKCE_BASLIK_ANAHTARLARI
        if anahtar.casefold() in govde
    )


def sistem_anahtarlarini_coz(hucre: str) -> tuple[str, ...] | None:
    """Bölüm B `sistem anahtarı` hücresi → anahtar demeti; bozuksa `None`.

    TEK ayrıştırıcıdır: kapı (hücre denetimi) ve köprü (`CIddia.anahtarlar`)
    aynı fonksiyonu çağırır, yoksa kapı "geçerli" derken köprü boş kalabilirdi.
    Sözleşme yazımı: `—` (anahtar YOK) ya da virgülle ayrılmış, tekrarsız,
    slug biçimli anahtarlar. Boş hücre, düzyazı, bilinmeyen anahtar → `None`.
    `—` → BOŞ demet (çözüldü, anahtar yok).
    """
    hucre = hucre.strip()
    if not hucre:
        return None
    if hucre == SISTEM_ANAHTARI_YOK:
        return ()
    parcalar = [parca.strip() for parca in hucre.split(",")]
    if any(not _SISTEM_ANAHTARI_RE.match(parca) for parca in parcalar):
        return None
    if any(parca not in SISTEM_ANAHTARLARI for parca in parcalar):
        return None
    if len(set(parcalar)) != len(parcalar):
        return None
    return tuple(parcalar)


_ADAY_TAKVIM_SADE: dict[str, tuple[str, ...]] = {
    _sadelestir(ad): demet for ad, demet in ADAY_TAKVIM_ANAHTARLARI.items()
}


def _aday_kopyasi_mi(donem: str, anahtarlar: tuple[str, ...]) -> bool:
    """Hücre sözleşmenin o dönem için İZİN VERDİĞİ değer mi? TEK yüklem, İKİ tüketici.

    * ADAY TAKVİM'deki dönem → şablondaki demetin AYNEN kopyası.
    * Aday listesinde OLMAYAN dönem → `—` (boş demet) YA DA yalnız aday-dışı sistem
      günü anahtarları (`ADAY_DISI_SISTEM_ANAHTARLARI` — şablon: *"sektöre özgü ekleme
      olarak bunlardan birini seçersen anahtarını buradan al"*). Bir ADAY dönemin
      anahtarı aday dışı bir ad altında TAŞINAMAZ.

    **Attempt-3 F1 (both-agree, yüksek — ÖLÇÜLDÜ):** ilk yazım aday dışı dönemde
    "kopya kuralı yok, geç" diyordu; geriye yalnız üyelik kalıyor ve `Sezon Açılışı
    → black-friday` notsuz geçip köprü kuruyordu — yani ilgisiz bir sezon araştırması
    Black Friday kararlarını yetkilendirebiliyordu. Sözleşme: *"tablodakinden farklıysa
    o dönemin HİÇBİR iddiası hiçbir paket kararını yetkilendiremez."*
    """
    beklenen = _ADAY_TAKVIM_SADE.get(donem)
    if beklenen is not None:
        return anahtarlar == beklenen
    # Şablon: *"bunlardan BİRİNİ seçersen"* — aday dışı dönem en fazla TEK aday-dışı
    # gün taşır (kapanış turu N1/2). Dönem ADI ile o günün bağı burada ölçülemez:
    # şablon üç günün anahtarını verir, günlük dildeki adını vermez — tam kapanış
    # dış sözleşme revizyonu ister (ad→anahtar satırı); dürüst sınır.
    return len(anahtarlar) <= 1 and all(
        anahtar in ADAY_DISI_SISTEM_ANAHTARLARI for anahtar in anahtarlar
    )


def _donem_anahtarlari(tablo_satirlari: Sequence[str]) -> dict[str, tuple[str, ...]]:
    """Gerekçe tablosundan DÖNEM → ANAHTARLAR köprüsü — yalnız çözülen satırlar.

    Aynı dönem iki satırda geçiyorsa ve anahtarları ÇELİŞİYORSA köprü o dönemi
    TAŞIMAZ (hangisinin doğru olduğu bilinemez; birini seçmek sessiz varsayım
    olurdu). Aynı anahtarla tekrar zararsızdır.

    KOPYA KURALI köprüde de yaşar (fail-closed): ADAY TAKVİM'deki bir dönem
    şablondakinden BAŞKA bir anahtar taşıyorsa satır not alır ve köprüye de
    GİRMEZ. Aksi hâlde "Sevgililer Günü" satırına yazılmış bir Ramazan anahtarı
    notlu geçer ama motor Ramazan kararlarını o satırla yetkilendirirdi — not,
    kapıyı kapatmaz; köprünün kendisi kapatır.
    """
    kopru: dict[str, tuple[str, ...]] = {}
    celisen: set[str] = set()
    for satir in tablo_satirlari:
        hucreler = _hucreler(satir)
        if len(hucreler) != len(GEREKCE_TABLOSU_SUTUNLARI):
            continue
        donem = _sadelestir(hucreler[GEREKCE_DONEM_INDEKSI])
        anahtarlar = sistem_anahtarlarini_coz(hucreler[GEREKCE_ANAHTAR_INDEKSI])
        if not donem or anahtarlar is None:
            continue
        if not _aday_kopyasi_mi(donem, anahtarlar):
            continue
        if donem in kopru and kopru[donem] != anahtarlar:
            celisen.add(donem)
            continue
        kopru[donem] = anahtarlar
    for donem in celisen:
        kopru.pop(donem, None)
    return kopru


def _gerekce_tablosu(
    bloklar: Sequence[Sequence[tuple[int, str, bool]]]
) -> tuple[list[Sequence[tuple[int, str, bool]]], int]:
    """Denetim kümesi = dönem bloklarından ÖNCEKİ BÜTÜN tablolar. SEÇİM YOK.

    **Bu fonksiyonun asıl sözleşmesi MONOTONLUKTUR** (`kap_iddiasi_mi`
    başlığındaki ekleme değişmezinin yapısal ayağı): bir blok EKLEMEK denetim
    kümesinden başka bir bloğu ÇIKARAMAZ. Karar blok BAŞINA verilir — bir bloğun
    denetime girip girmediği YALNIZ kendi konumuna bakar, başka blokların
    varlığına DEĞİL. Bu bir sezgisel değil bir özelliktir ve altıncı bir sınır
    kuralı yazmadan bütün yem bileşimlerini birden kapatır.

    Sınıfın tarihçesi — beş turun beşi de bir SEÇİM/SINIR kuralıydı ve her biri
    kendi kalıbına uyan bir bileşimle kandırıldı:

    * v1: tanıma yoktu → Bölüm B'deki her `|` satırı gerekçe malzemesiydi.
    * v2: "dönemlerden ÖNCEKİ İLK BİTİŞİK tablo" → önüne konan yem gizledi.
    * v3: "kanonik başlık taşıyan aday" → gerçek tablonun başlığı JENERİK
      olduğunda kanonik başlıklı bir yem TEK aday olur ve gerçek tabloyu
      susturur. Ölçüldü: `notlu-gecti / 8 not` → `gecti / 0 not`.
    * v4: "seçimi bırak, dönem öncesi HEPSİNİ denetle" → doğru yöndeydi ama
      geri dönüşü (`dönem-öncesi blok yoksa HEPSİNİ denetle`) monotonluğu
      kırıyordu.
    * v5: "sınırı ilk dönem BAŞLIĞINA çek" → sınır doğrulandı ama v4'ün geri
      dönüşü yerinde kaldı.

    **Tur 6 — ölçülmüş gerileme ve kapanış.** v4'ün fail-open geri dönüşü tam
    olarak "ekleme kaldırır" davranışıydı: ilk döneme başlık YAZILMAMIŞ ve
    tablonun üstüne bir alt yazı başlığı KONMUŞ bir belgede gerçek tablo
    dönem-SONRASI sayılıyor, geri dönüş sayesinde yine de denetleniyordu; önüne
    dönem-ÖNCESİ tek bir yem konduğunda geri dönüş DEVREDEN ÇIKIYOR ve gerçek
    tablonun bütün notları birden düşüyordu (ölçüldü: `9 not → 0 not`). Geri
    dönüş KALDIRILDI; kural artık blok başınadır ve monotondur.

    **Korunan kazanım (v2'nin yanlış-pozitif düzeltmesi):** dönem BÖLGESİNDE
    duran tablolar gerekçe denetimine GİRMEZ. Bu bir sezgisel değil,
    sözleşmenin kendi SIRASIDIR (`_SABLON.md` §5: "önce tablo, sonra dönem
    dönem dört başlık"). Bölgenin nerede BAŞLADIĞI ayrı bir sorudur ve
    `_ilk_donem_baslangici`'nda yaşar: dönem bloğu BAŞLIĞIYLA başlar.

    **Bilinçle kabul edilen bedel:** dönemlerden önce konmuş meşru ve alakasız
    bir tablo NOT üretir (kendi satırları da denetime girer). Bugün hiçbir
    kontrol ELEMEDİĞİ için maliyet gürültüdür, kaynak kaybı değil — ve not
    SESSİZ DEĞİLDİR, belirsizlik açıkça yazılır.

    **Geri dönüşün kaldırılmasının ölçülmüş bedeli:** dönem bölgesinden SONRA
    duran BOZUK bir tablo artık satır/sütun denetimine hiç GİRMEZ; onun yerine
    iki KÜME düzeyi notu düşer — "dönem başlıklarından ÖNCE tablo yok" ve
    "tablo dönemlerden SONRA geliyor". Sinyal kaybı değil, sinyal DEĞİŞİMİDİR:
    o konumdaki bir tablonun gerekçe tablosu olduğu ZATEN doğrulanamıyordu ve
    denetlenmesi v2'nin kapattığı yanlış-pozitif sınıfının ta kendisiydi.

    **Kapsam sınırı:** dönem-öncesi tabloların hangisinin GERÇEK gerekçe
    tablosu olduğu DOĞRULANMAZ ve doğrulanmaya ÇALIŞILMAZ; hepsi denetlenir.
    """
    donem_oncesi = [blok for blok in bloklar if blok and not blok[0][2]]
    return donem_oncesi, len(donem_oncesi)


def _tablo_veri_satirlari(satirlar: Sequence[str]) -> list[str]:
    """Ayıraç satırından SONRAKİ tablo satırları — başlık satırı veri değildir."""
    ayirac_gorundu = False
    veri: list[str] = []
    for satir in satirlar:
        if not _TABLO_RE.match(satir):
            continue
        if _TABLO_AYIRAC_RE.match(satir):
            ayirac_gorundu = True
            continue
        if ayirac_gorundu:
            veri.append(satir)
    return veri


def _hucreler(satir: str) -> list[str]:
    return [hucre.strip() for hucre in satir.strip().strip("|").split("|")]


def _bolum_satirlari(belge: _Belge, harfler: Sequence[str]) -> list[str]:
    toplam: list[str] = []
    for harf in harfler:
        toplam.extend(belge.bolumler.get(harf, []))
    return toplam


# ─── 4. Kontroller ──────────────────────────────────────────────────────────
#
# Her kontrol bir mesaj listesi döner (boş = temiz). SEVİYE burada DEĞİL,
# `CHECKS` üyesinin `seviye` alanındadır.


def _ilk_gorunum_sirasi(izler: Sequence[str]) -> tuple[str, ...]:
    """Tekrarları atarak İLK görünüm sırasını verir."""
    gorulen: list[str] = []
    for iz in izler:
        if iz not in gorulen:
            gorulen.append(iz)
    return tuple(gorulen)


def _sira_ihlali(
    gorulen: Sequence[str], sozlesme: Sequence[str], etiket: str
) -> list[str]:
    """Görülen sıra, sözleşme sırasının BİR ALT DİZİSİ mi?

    Eksik öğe burada ölçülmez (o `tamlık` kontrolünün işi) — yalnız var olanların
    SIRASI sözleşmeye vurulur. Böylece eksik bir bölüm/alan sıra ihlali gibi
    ikinci kez raporlanmaz.
    """
    beklenen = tuple(ad for ad in sozlesme if ad in set(gorulen))
    if tuple(gorulen) == beklenen:
        return []
    return [
        f"{etiket} sözleşmenin sırası değil: {list(gorulen)} — beklenen "
        f"{list(beklenen)}"
    ]


def _kisalt(metin: str, sinir: int = 60) -> str:
    return metin if len(metin) <= sinir else metin[:sinir] + "…"


def _iz_ihlalleri(
    gorulen: Sequence[str],
    sozlesme: Sequence[str] | None,
    tekrar_sablonu: str,
    sira_etiketi: str | None,
) -> list[str]:
    """Bir iç içe düzeyin SIRALI-TEKRARLI izini sözleşmeye vurur.

    `sozlesme is None` → küme AÇIKTIR: yalnız TEKRAR ölçülür, sıra ölçülmez.

    **Gerekçe tur 3'te DÜZELTİLDİ (davranış DEĞİŞMEDİ).** Önceki gerekçe
    "sözleşme o düzeyde bir sıra DAYATMAZ" diyordu ve YANLIŞTI: pinli sözleşme
    (`_SABLON.md` satır 73-75) her listede ÖNEM SIRASI dayatır — ölçüt sırasıyla
    sektöre özgülük, kaynak sayısı ve gücü, Türkiye yerelliği. Doğru gerekçe
    şudur: sözleşme sıra DAYATIR ama önem SEMANTİK bir yargıdır ve mekanik kapı
    onu DOĞRULAYAMAZ. Ölçüldü: iki çağrı kalıbı takas edildiğinde rapor
    `gecti / 0 not` verir. Uydurulmuş bir sıra kuralı gerçek araştırma çıktısını
    gürültüye boğar ve İlke 9'u ihlal ederdi; bu yüzden YAZILMAZ ve sınır
    `bolum-ve-alan-tamligi` kapsam beyanına BEŞİNCİ kalem olarak taşınır.
    """
    mesajlar: list[str] = []
    sayim: dict[str, int] = {}
    for ad in gorulen:
        sayim[ad] = sayim.get(ad, 0) + 1
    for ad in _ilk_gorunum_sirasi(gorulen):
        if sayim[ad] > 1:
            mesajlar.append(
                tekrar_sablonu.format(ad=_kisalt(ad), adet=sayim[ad])
            )
    if sozlesme is not None and sira_etiketi is not None:
        mesajlar += _sira_ihlali(
            _ilk_gorunum_sirasi(gorulen), sozlesme, sira_etiketi
        )
    return mesajlar


def _madde_izi(yuva: _Yuva) -> tuple[str, ...]:
    """Madde TEKRARI izi — sözleşmenin SAYDIĞI yüzeyden (`citsiz_maddeler`).

    İz mesajı adet ailesinin cümlesini taşır ("adet alt sınırı ESSİZ madde
    sayar"); sayım çit-farkındaysa iz de öyle olmak zorundadır, yoksa aynı
    içerik iki farklı yüzeyden okunur ve kapı kendi içinde çelişir.
    """
    return tuple(_sadelestir(madde) for madde in yuva.citsiz_maddeler)


def _ic_ice_izler(
    belge: _Belge,
) -> list[tuple[Sequence[str], Sequence[str] | None, str, str | None]]:
    """Belgenin İÇERME MODELİ — her iç içe düzeyin izi, tek yerde.

    Liste bulunan örneklerden değil, sözleşmenin kendi yapısından türer
    (`_SABLON.md` §5 ÇIKTI FORMATI + GÖREV A/B adımları):

        bölüm → Bölüm A alanı → alan maddesi
                              → video havuzu → havuz maddesi
              → Bölüm B dönemi → dönem yuvası → yuva maddesi
              → Bölüm C eşleme satırı

    Sabit kümelerde (bölüm · alan · havuz · yuva) SIRA da sözleşmenindir; açık
    kümelerde (madde · dönem · eşleme satırı) yalnız TEKRAR ölçülür.
    """
    izler: list[tuple[Sequence[str], Sequence[str] | None, str, str | None]] = [
        (
            belge.bolum_sirasi,
            BOLUM_HARFLERI,
            "Bölüm {ad} birden çok kez açılmış ({adet} kez) — beş bölüm "
            "SABİTTİR, aynı bölüm ikinci kez yazılmaz",
            "Bölüm sırası",
        ),
        (
            belge.alan_sirasi,
            TEMEL_ALANLAR,
            "`{ad}` alan başlığı birden çok kez yazılmış ({adet} kez) — "
            "Bölüm A sekiz alanı BİRER kez taşır",
            "Bölüm A alan sırası",
        ),
        (
            belge.video_havuz_sirasi,
            VIDEO_HAVUZLARI,
            "`video_kodlar.{ad}` alt listesi {adet} kez yazılmış — her havuz "
            "BİRER kez yazılır",
            "`video_kodlar` havuz sırası",
        ),
        (
            belge.donem_sirasi,
            None,
            "Bölüm B'de `{ad}` dönemi {adet} kez yazılmış — aynı dönem iki kez "
            "işlenmez; dönem alt sınırı ESSİZ dönem sayar",
            None,
        ),
        (
            belge.c_esleme_izleri,
            None,
            "Bölüm C eşleme satırı {adet} kez yazılmış: {ad}",
            None,
        ),
    ]
    for ad in LISTE_ALANLARI:
        yuva = belge.alanlar.get(ad)
        if yuva is not None and ad != "video_kodlar":
            izler.append(
                (
                    _madde_izi(yuva),
                    None,
                    f"`{ad}` içinde bir madde {{adet}} kez yazılmış — adet "
                    "alt sınırı ESSİZ madde sayar: {{ad}}",
                    None,
                )
            )
    for havuz, yuva in belge.video_havuzlari.items():
        izler.append(
            (
                _madde_izi(yuva),
                None,
                f"`video_kodlar.{havuz}` içinde bir madde {{adet}} kez "
                "yazılmış — adet alt sınırı ESSİZ madde sayar: {{ad}}",
                None,
            )
        )
    for donem in belge.donemler:
        izler.append(
            (
                donem.yuva_sirasi,
                OZEL_GUN_YUVALARI,
                "%s: `{ad}` başlığı birden çok kez yazılmış ({adet} kez) — "
                "dönem başına DÖRT başlık vardır" % donem.ad,
                f"{donem.ad}: dönem başlık sırası",
            )
        )
        if donem.bilincli_bos:
            continue
        for yuva_adi in OZEL_GUN_LISTE_YUVALARI:
            yuva = donem.yuvalar.get(yuva_adi)
            if yuva is not None:
                izler.append(
                    (
                        _madde_izi(yuva),
                        None,
                        f"{donem.ad}/`{yuva_adi}` içinde bir madde {{adet}} "
                        "kez yazılmış — adet alt sınırı ESSİZ madde sayar: {{ad}}",
                        None,
                    )
                )
    return izler


def _bolum_yapisi_ihlalleri(belge: _Belge) -> list[str]:
    """Sözleşmenin DİLBİLGİSİ: tekrar · sıra · boşluk — HER iç içe düzeyde.

    "Var mı" sorusu bu üç biçimi göremez; ayrıştırıcı koleksiyonları sözlüğe
    koyar ve sözlük tekrarı da sırayı da kaybeder. Tur 1 bunu yalnız BÖLÜM ve
    ALAN düzeyinde kurtarmıştı; ölçüldü ki dönem kimliği tekrarı, video havuzu
    bloğunun ikinci kez yazılması ve tekrar eden Bölüm C eşleme satırı hâlâ
    `gecti / 0 not` veriyordu. Düzey listesi artık `_ic_ice_izler`'de yaşar ve
    belgenin İÇERME MODELİNDEN türer.

    **Kapsam sınırı:** bölüm/alan TANIMA markdown başlık düzeyine ve ad
    eşleşmesine dayanan mekanik bir vekildir (`_ayristir` docstring'i); sözleşme
    markdown düzeyi dayatmaz. Dilbilgisi bilerek DAR TUTULMAMIŞTIR: tanınmayan
    bir başlık iz bırakmaz ve burada sessiz kalır — ihlal olarak sayılmaz.
    Açık kümelerde SIRANIN neden ölçülmediği `_iz_ihlalleri`'nde yazılıdır ve
    kapsam beyanının BEŞİNCİ kalemi olarak rapora taşınır.
    """
    mesajlar: list[str | _Mesaj] = []
    for gorulen, sozlesme, sablon, sira_etiketi in _ic_ice_izler(belge):
        mesajlar += _iz_ihlalleri(gorulen, sozlesme, sablon, sira_etiketi)
    # KAP iddiası: bölüm bir KAPTIR ve iddia onun BÜTÜNÜ hakkındadır.
    for harf in belge.bos_bolumler:
        mesajlar.append(_kap(BOLUM_BOS_MESAJI.format(harf=harf)))
    return mesajlar


def _kontrol_bolum_ve_alan(belge: _Belge) -> list[str]:
    mesajlar: list[str | _Mesaj] = _bolum_yapisi_ihlalleri(belge)
    for harf in BOLUM_HARFLERI:
        if harf not in belge.bolumler:
            mesajlar.append(
                f"Bölüm {harf} yok — beş bölümlü çıktı biçimi zorunludur"
            )
    for ad in TEMEL_ALANLAR:
        yuva = belge.alanlar.get(ad)
        if yuva is None:
            mesajlar.append(f"`{ad}` alan başlığı Bölüm A'da yok")
        elif not yuva.dolu:
            mesajlar.append(f"`{ad}` alanı boş")
    if "video_kodlar" in belge.alanlar:
        for havuz in VIDEO_HAVUZLARI:
            if havuz not in belge.video_havuzlari:
                mesajlar.append(f"`video_kodlar.{havuz}` alt listesi yok")
    for donem in belge.donemler:
        if donem.bilincli_bos:
            continue  # K-120: bilinçli boş dönem doluluk kontrolünü GEÇER.
        for yuva_adi in OZEL_GUN_YUVALARI:
            yuva = donem.yuvalar.get(yuva_adi)
            if yuva is None:
                mesajlar.append(f"{donem.ad}: `{yuva_adi}` başlığı yok")
            elif not yuva.dolu:
                mesajlar.append(
                    f"{donem.ad}: `{yuva_adi}` boş — bilinçli boşluğun resmî "
                    f"temsili AYNEN `{BILINCLI_BOS}` değeridir (K-120)"
                )
    return mesajlar


def _essiz_donem_sayisi(belge: _Belge) -> int:
    """Sözleşmenin saydığı birim ESSİZ dönem KİMLİĞİDİR, ham blok sayısı değil.

    Ölçüldü: aynı dönem adı iki kez yazıldığında `>=6 dönem` alt sınırı TEKRARLA
    sağlanıyor ve kapı sessiz kalıyordu (ayrıştırılan 6, essiz ad 5).
    """
    return len(_ilk_gorunum_sirasi(belge.donem_sirasi))


def _kontrol_adet_alt_sinirlari(belge: _Belge) -> list[str]:
    """ÖLÇÜLMEMİŞ sözleşme sayıları — seviyesi kalıcı olarak `not`tur (İlke 9).

    **Sayım birimi ESSİZ DOĞRULANMIŞ VARLIKTIR** (tur 2, F2): ham `len(...)`
    tekrarı ve serbest boşluk ifadesini de sayar, dolayısıyla her eşik aynı
    satırın kopyalarıyla ya da `yok` yazılarak sessizce sağlanabilirdi.
    """
    mesajlar: list[str] = []
    for ad, alt_sinir in ALAN_ALT_SINIRLARI.items():
        yuva = belge.alanlar.get(ad)
        adet = len(yuva.essiz_maddeler) if yuva else 0
        if adet < alt_sinir:
            mesajlar.append(
                f"`{ad}` {adet} madde taşıyor, sözleşme alt sınırı {alt_sinir} "
                "(ölçülmemiş sözleşme kuralı)"
            )
    toplam = 0
    for havuz in VIDEO_HAVUZLARI:
        yuva = belge.video_havuzlari.get(havuz)
        adet = len(yuva.essiz_maddeler) if yuva else 0
        toplam += adet
        if adet < VIDEO_HAVUZ_ALT_SINIRI:
            mesajlar.append(
                f"`video_kodlar.{havuz}` {adet} madde taşıyor, alt sınır "
                f"{VIDEO_HAVUZ_ALT_SINIRI}"
            )
    if toplam < VIDEO_TOPLAM_ALT_SINIRI:
        mesajlar.append(
            f"`video_kodlar` toplam {toplam} madde, alt sınır "
            f"{VIDEO_TOPLAM_ALT_SINIRI}"
        )
    essiz_donem = _essiz_donem_sayisi(belge)
    if essiz_donem < DONEM_ALT_SINIRI:
        mesajlar.append(
            f"Bölüm B {essiz_donem} ESSİZ dönem işliyor, alt sınır "
            f"{DONEM_ALT_SINIRI}"
        )
    for donem in belge.donemler:
        if donem.bilincli_bos:
            # K-120: bu dönemde alt sınır denetimi UYGULANMAZ.
            continue
        for yuva_adi, alt_sinir in DONEM_YUVA_ALT_SINIRLARI.items():
            yuva = donem.yuvalar.get(yuva_adi)
            adet = len(yuva.essiz_maddeler) if yuva else 0
            if adet < alt_sinir:
                mesajlar.append(
                    f"{donem.ad}: `{yuva_adi}` {adet} madde, alt sınır {alt_sinir}"
                )
    return mesajlar


def _ingilizce_yuzeyler(belge: _Belge) -> list[tuple[str, str]]:
    yuzeyler: list[tuple[str, str]] = []
    gorsel = belge.alanlar.get("gorsel_kodlar")
    if gorsel:
        yuzeyler += [("gorsel_kodlar", madde) for madde in gorsel.maddeler]
    for havuz, yuva in belge.video_havuzlari.items():
        yuzeyler += [(f"video_kodlar.{havuz}", madde) for madde in yuva.maddeler]
    for donem in belge.donemler:
        if donem.bilincli_bos:
            # `içerik-önerilmez` Türkçe'dir ve resmî değerdir — dil kuralı bu
            # dala UYGULANMAZ (K-120).
            continue
        yuva = donem.yuvalar.get("gorsel_vurgu")
        if yuva:
            yuzeyler += [
                (f"{donem.ad}/gorsel_vurgu", madde) for madde in yuva.maddeler
            ]
    return yuzeyler


def _kontrol_dil_kurali(belge: _Belge) -> list[str]:
    """YALNIZ İngilizce yüzeyler ölçülür — ters yön DOĞRULANMADI (İlke 9)."""
    mesajlar: list[str] = []
    for yuzey, madde in _ingilizce_yuzeyler(belge):
        harfler = sorted(_TURKCE_HARFLER.intersection(madde))
        if harfler:
            mesajlar.append(
                f"{yuzey} İNGİLİZCE olmalı, Türkçe harf taşıyor ({''.join(harfler)}): "
                f"{madde[:60]!r}"
            )
    return mesajlar


_URL_RE = re.compile(r"https?://\S+")


def _c_gecerli_anahtarlar(belge: _Belge) -> frozenset[str]:
    """`alan/dönem` hücresinin KAPALI kümesi — iki ayağı da türetilmiştir.

    Sözleşme (Bölüm C): *"`alan/dönem` hücresi ya Bölüm A alan adıdır ya da
    Bölüm B dönem adıdır — aynen o yazımla"*. Alan ayağı sözleşmenin kanonik
    sabitinden (`TEMEL_ALANLAR`), dönem ayağı BELGENİN KENDİ Bölüm B'sinden
    gelir; ikisi de elle yazılmış bir liste DEĞİLDİR.

    Dönem ayağının belgeden gelmesi bilinçlidir: dönem kümesi açıktır
    (araştırma kendi dönemlerini seçer), dolayısıyla tek doğrulanabilir bağ
    "Bölüm C'de gösterilen dönem, Bölüm B'de gerçekten İŞLENMİŞ mi"dir.
    """
    return frozenset(
        [_sadelestir(ad) for ad in TEMEL_ALANLAR] + list(belge.donem_sirasi)
    )


def _c_satir_ihlalleri(satir: str, belge: _Belge) -> list[str]:
    """Bölüm C'nin TEK bir veri satırının sözleşmeye uygunluğu.

    Ayrı bir fonksiyondur ki mutasyon kolu kuralı SÖKEBİLSİN — kapanış
    "kontrol var" değil "kontrol GERÇEKTEN eliyor" ile kanıtlanır.
    """
    kisa = satir.strip()[:80]
    hucreler = _hucreler(satir)
    if len(hucreler) != len(C_TABLOSU_SUTUNLARI):
        # Sütun sayısı tutmuyorsa hangi hücrenin ne olduğu BİLİNMEZ; hücre
        # denetimi yapılmaz, yoksa kaydırılmış sütunlar üstünde uydurma not
        # üretilirdi.
        return [
            f"Bölüm C satırı {len(hucreler)} sütunlu — sözleşme "
            f"{len(C_TABLOSU_SUTUNLARI)} SABİT sütun ister: {kisa!r}"
        ]
    mesajlar: list[str] = []
    for ad, hucre in zip(C_TABLOSU_SUTUNLARI, hucreler):
        if not hucre:
            mesajlar.append(f"Bölüm C satırında `{ad}` hücresi BOŞ: {kisa!r}")
    no, alan, iddia, _kaynak_adi, url, tarih, tek_kaynak = hucreler

    # `no` HÜCRESİNİN BİÇİMİ (dizi kuralı ayrı ölçülür). Sözleşme: *"1'den
    # başlayan ARTAN TAM SAYIDIR ve bu raporda o iddianın KALICI KİMLİĞİDİR"*.
    # Kimlik makine tarafından ÇÖZÜLEBİLİR olmak zorundadır: denetçinin
    # `kaynak-iddialari` sütunu ve sentezin `kaynak_iddia` alanı bu numarayı
    # gösterir; serbest yazım (`3a` · `#3` · `üç`) bağı sessizce koparırdı.
    if no and not _C_NO_RE.match(no):
        mesajlar.append(
            f"Bölüm C `no` hücresi 1'den başlayan artan TAM SAYI değil: {no!r}"
        )

    # Dönem ayağı belgeden geldiği için, Bölüm B HİÇ ayrıştırılamamışsa kapalı
    # küme yarım kalır ve her dönem satırı haksızca yanlışlanırdı. O hâl AYRI
    # bir ailenin konusudur (`bolum-ve-alan-tamligi`); aynı arıza iki kez
    # sayılmaz ve üyelik ayağı o durumda hiçbir şey İDDİA ETMEZ.
    if belge.donem_sirasi and alan:
        if _sadelestir(alan) not in _c_gecerli_anahtarlar(belge):
            mesajlar.append(
                f"Bölüm C `alan/dönem` hücresi ne bir Bölüm A alan adı ne de "
                f"Bölüm B'de işlenmiş bir dönem: {alan!r}"
            )
    if iddia:
        kelime = len(iddia.split())
        if kelime > C_IDDIA_KELIME_UST_SINIRI:
            mesajlar.append(
                f"Bölüm C `iddia` hücresi {kelime} kelime — sözleşme en fazla "
                f"{C_IDDIA_KELIME_UST_SINIRI} kelime ister (iddia ÖZETİDİR, "
                f"cümlesi değil): {kisa!r}"
            )
    if url:
        if "http://" in url:
            mesajlar.append(
                f"Bölüm C `URL` hücresi `http://` bağlantı taşıyor: {url!r}"
            )
        elif len(_URL_RE.findall(url)) != 1 or not url.startswith("https://"):
            mesajlar.append(
                "Bölüm C `URL` hücresi TEK bir açılabilir `https://` "
                "bağlantıdan ibaret olmalı (oturum-içi atıf kodu · dipnot "
                f"numarası · alan adı kısaltması kabul edilmez): {url!r}"
            )
    if tarih and tarih != C_TARIH_YOK and not _C_TARIH_RE.match(tarih):
        mesajlar.append(
            f"Bölüm C `tarih` hücresi `YYYY-AA` ya da `YYYY-AA-GG` değil; "
            f"kaynakta tarih görünmüyorsa AYNEN `{C_TARIH_YOK}` yazılır: "
            f"{tarih!r}"
        )
    if tek_kaynak and _sadelestir(tek_kaynak) not in {
        _sadelestir(deger) for deger in C_TEK_KAYNAK_DEGERLERI
    }:
        mesajlar.append(
            "Bölüm C `tek kaynak` hücresi kapalı kümenin dışında "
            f"({' / '.join(C_TEK_KAYNAK_DEGERLERI)} beklenir): {tek_kaynak!r}"
        )
    return mesajlar


def _c_no_dizisi_ihlalleri(belge: _Belge) -> list[str]:
    """`no` sütununun DİZİ kuralı — tekrar YOK, boşluk YOK, 1'den başlar.

    Ayrı bir fonksiyondur çünkü ayrı bir şey ölçer: `_c_satir_ihlalleri` TEK
    satıra bakar ve bir satırın kendi içinde "3" kusursuz bir numaradır; kimlik
    ise TABLONUN BÜTÜNÜNDE anlamlıdır. İki satırın aynı numarayı taşıması ya da
    `1, 2, 4` gibi bir boşluk, satır düzeyinde GÖRÜNMEZ.

    **Neden kimlik bu kadar sert.** Numara, denetçinin *"hangi iddiaya baktım"*
    ve sentezin *"yeni kalıbı hangi iddiadan türettim"* beyanlarını aynı üst
    kaynağa çivileyen TEK makine-okunur bağdır (dış depo `12beec1`). Tekrar
    eden bir numara o bağı ÇOĞA böler: motor `K1#3`'ün hangi satırı gösterdiğini
    bilemez ve yetkilendirme yeniden alan düzeyine düşerdi — kapatılan sınıfın
    ta kendisi. Bu yüzden küme TAM OLARAK `1..N`'dir.
    """
    hamlar = [
        _hucreler(satir)[C_NO_INDEKSI]
        for satir in belge.c_veri_satirlari
        if len(_hucreler(satir)) == len(C_TABLOSU_SUTUNLARI)
    ]
    # Biçimi bozuk hücre BURADA sayılmaz: onu `_c_satir_ihlalleri` zaten
    # bildirdi ve aynı arıza iki kez sayılmaz. Dizi kuralı yalnız ÇÖZÜLEBİLEN
    # numaralar üstünde iddiada bulunur.
    numaralar = [int(ham) for ham in hamlar if _C_NO_RE.match(ham)]
    if not numaralar:
        return []
    # F8 (hakem turu 1, düşük — ÖLÇÜLDÜ): "aynı arıza iki kez sayılmaz" beyanı
    # BOŞLUK kolunda TUTMUYORDU. Bozuk hücre `numaralar`dan düşünce N küçülüyor
    # ve boşluk kuralı SAHTE bir eksik üretiyordu: `1,2,3a,4` → "eksik numara:
    # [3]". 3 eksik DEĞİL, BOZUK — ve onu satır denetimi zaten bildirdi.
    bozuk_var = len(numaralar) != len(hamlar)
    mesajlar: list[str] = []
    tekrar = sorted({no for no in numaralar if numaralar.count(no) > 1})
    if tekrar:
        mesajlar.append(
            "Bölüm C `no` sütunu KİMLİKTİR, tekrar edemez — şu numaralar "
            f"birden çok satırda: {tekrar}"
        )
    beklenen = set(range(1, len(numaralar) + 1))
    eksik = sorted(beklenen - set(numaralar))
    if eksik and not tekrar and not bozuk_var:
        mesajlar.append(
            "Bölüm C `no` sütunu 1'den başlayıp boşluksuz artmalı — eksik "
            f"numara: {eksik}"
        )
    return mesajlar


@dataclass(frozen=True)
class CIddia:
    """Bölüm C'nin TEK satırının MAKİNE-OKUNUR özü: kimlik + alan.

    Kapı bu satırı zaten ayrıştırıyordu ve sonucu ATIYORDU; taşıyıcı eksikti.
    Motor, sentezin `kaynak_iddia` alanındaki `K<kaynak>#<iddia>` numarasının
    gerçekten VAR olduğunu ve alanının kararın alanıyla örtüştüğünü bu demet
    üstünde ölçer — beyandan değil, MEKANİK ayrıştırıcıdan (dış depo `12beec1`,
    sentez sözleşmesi 2.2: *"bunu mekanik ayrıştırıcı doğrular, senin beyanın
    değil"*).

    Hücrenin yalnız İKİ sütunu taşınır. `iddia` metni bilinçli olarak DIŞARIDA:
    motor onunla bir şey ölçmez, taşımak onu bir karar girdisi gibi gösterirdi.

    `anahtarlar` (dış depo `d9dc289`, F3): satır bir DÖNEM satırıysa o dönemin
    SİSTEM ANAHTARLARI — Bölüm B gerekçe tablosunun `sistem anahtarı`
    sütunundan köprüyle gelir (`_Belge.donem_anahtarlari`). Görev A satırında
    ve köprüsü kurulamayan dönem satırında BOŞTUR. Motor Görev B bağını bu
    kümeden kurar: kararın `oge_yolu` anahtarı kümede mi? Günlük dildeki dönem
    adından anahtar TÜRETİLMEZ — o tahmin, F3'ün kapattığı sınıftır.
    """

    no: int
    alan: str
    anahtarlar: tuple[str, ...] = ()
    url: str = ""
    """Bölüm C satırının `URL` hücresi, AYNEN (attempt-3 F2, both-agree, yüksek).

    K-126'nın ikinci ayağı bu iddianın URL'sinin canlı doğrulanmasıdır; denetçi
    sözleşmesi 2.3 örneklem satırının `URL` hücresini *"o Bölüm C satırının URL
    hücresidir — aynen kopyala"* diye bağlar. Motor eşitliği BURADAN ölçer: kimlik
    doğru ama URL başka bir adresse istisna AÇILMAZ. `run`'ı atlayan çağıranda boş
    kalır ve boş URL hiçbir örneklem satırıyla eşleşmez (fail-closed).
    """


def _c_iddialari(belge: _Belge) -> tuple[CIddia, ...]:
    """Bölüm C'nin ÇÖZÜLEBİLEN satırları — ayrıştırılamayan satır DÜŞER.

    Fail-closed: sütun sayısı tutmayan ya da numarası çözülemeyen satır iddia
    ÜRETMEZ. "Sanki 3'müş gibi" taşımak, kapatılan sınıfın — atfın alan
    düzeyinde yetkilendirilmesi — sessiz geri dönüşü olurdu. Düşen satır
    zaten `_c_satir_ihlalleri` tarafından NOT olarak bildirilmiştir; burada
    ikinci bir not üretilmez, yalnız taşıyıcıya girmez.
    """
    iddialar: list[CIddia] = []
    for satir in belge.c_veri_satirlari:
        hucreler = _hucreler(satir)
        if len(hucreler) != len(C_TABLOSU_SUTUNLARI):
            continue
        ham_no = hucreler[C_NO_INDEKSI]
        alan = hucreler[C_ALAN_INDEKSI]
        if not _C_NO_RE.match(ham_no) or not alan:
            continue
        iddialar.append(
            CIddia(
                no=int(ham_no),
                alan=alan,
                anahtarlar=belge.donem_anahtarlari.get(_sadelestir(alan), ()),
                url=hucreler[C_URL_INDEKSI].strip(),
            )
        )
    # Tekrar eden numara KİMLİK DEĞİLDİR: hangi satırı gösterdiği belirsiz olan
    # bir numara motorda iki ayrı iddiaya çözülürdü. İhlali `_c_no_dizisi_-
    # ihlalleri` NOT olarak bildirir; taşıyıcı o numaraların HİÇBİRİNİ almaz
    # (birini seçmek, seçimi sessiz bir varsayıma çevirirdi).
    sayim = Counter(iddia.no for iddia in iddialar)
    return tuple(iddia for iddia in iddialar if sayim[iddia.no] == 1)


def _kontrol_url_bicimi(belge: _Belge) -> list[str | _Mesaj]:
    """Bölüm C SABİT SÜTUNLU bir tablodur; sütunları ve hücreleri denetlenir.

    **Bu kontrol OLUMSUZ ÇIKARIMDAN OLUMLU SÖZLEŞMEYE çevrildi (4. ayak).**
    Önceki sürüm serbest düzyazıdan *"bu bir eşleme DEĞİL"* sonucunu çıkarmaya
    çalışıyordu: satırı bir ayıraç vekiliyle (`_C_AYIRAC_RE`) parçalayıp PARÇA
    SAYISINA bakıyordu. Vekil serbest noktalamayı da ayıraç saydığı için
    düzyazı kontrolü GEÇİYORDU (ölçüldü: `- Düz yazı, devamı
    https://example.com/kaynak` → `gecti`, 0 not) ve sertleştirmesi ÜÇ turda
    yakınsamadı — semantik-negatif bir sınıftır, regex'le kapanmaz.

    Kök çözüm koda değil SÖZLEŞMEYE yapıldı: `_SABLON.md` artık Bölüm C'yi
    sabit sütunlu bir tablo olarak İSTİYOR (dış depo `7964ed6`). Kapı bu
    yüzden hiçbir şey tahmin etmez; olumlu bir yapıyı doğrular — birebir
    başlık satırı · sütun sayısı · hücre doluluğu · `no` biçimi ve DİZİSİ ·
    `alan/dönem` kapalı kümesi · `iddia` kelime sınırı · `URL` adres biçimi ·
    `tarih` yazımı · `tek kaynak` kapalı kümesi.

    **Kapsam sınırı (kalan, gerçek):** bağlantının gerçekten AÇILDIĞI ölçülmez
    (ağ çağrısı yapılmaz) ve `iddia` hücresinin kaynağı gerçekten ÖZETLEDİĞİ
    ölçülmez — ikisi de anlam yargısıdır. Bunlar denetçi katmanının işidir;
    denetçi görev metni ADIM 1'de kaynak başına 3 iddia örnekleyip bağlantıyı
    GERÇEKTEN açar.
    """
    mesajlar: list[str | _Mesaj] = []
    c_satirlari = belge.bolumler.get("C", [])
    if not any(satir.strip() for satir in c_satirlari):
        # Boş bölüm AYRI bir ailenin konusudur (`bolum-ve-alan-tamligi`);
        # burada ikinci bir boşluk notu üretmek aynı arızayı iki kez sayardı.
        return mesajlar
    if not belge.c_baslik_satiri_var:
        mesajlar.append(
            _kap(
                "Bölüm C sözleşmenin başlık satırını taşımıyor — sabit sütunlu "
                "tablo beklenir, AYNEN: `| "
                + " | ".join(C_TABLOSU_SUTUNLARI)
                + " |`"
            )
        )
        return mesajlar
    if not belge.c_veri_satirlari:
        mesajlar.append(
            _kap(
                "Bölüm C tablosu BAŞLIK SATIRINDAN İBARET — tek bir "
                "iddia→kaynak satırı taşımıyor"
            )
        )
        return mesajlar
    for satir in belge.c_veri_satirlari:
        mesajlar.extend(_c_satir_ihlalleri(satir, belge))
    mesajlar.extend(_c_no_dizisi_ihlalleri(belge))
    mesajlar.extend(_c_kapsama_ihlalleri(belge))
    return mesajlar


def _c_kapsama_ihlalleri(belge: _Belge) -> list[str | _Mesaj]:
    """BÜTÜNLÜK: her alan ve her dönem için en az bir kaynak satırı var mı?

    Bu kontrol ancak sözleşme "İDDİA BAŞINA BİR SATIR" dediği için MÜMKÜN
    oldu — kaynak başına gruplanmış serbest bir kaynakça bu soruyu makineyle
    cevaplatmaz. Karar Eray'ındır (2026-09-07, dört sorunun dördüncüsü) ve
    gerekçesi AYNEN buydu: *"makine 'her alan için kaynak gösterilmiş mi'
    BÜTÜNLÜK sorusunu tam cevaplayabilsin"*.

    **Kapsanan küme belgeden türer, sabit bir listeden değil:** Bölüm A'nın
    sekiz alanı (sözleşme sabiti) + Bölüm B'de GERÇEKTEN işlenmiş dönemler.
    Bölüm B yoksa dönem ayağı boş kalır ve bu kontrol dönem hakkında bir şey
    İDDİA ETMEZ — eksik bölüm ayrı bir ailenin konusudur.

    Bir KAP iddiasıdır: kabın bütünü hakkında bir YOKLUK söyler ve eksik
    satırı EKLEMEK onu haklı olarak düşürür.
    """
    gorulen = {
        _sadelestir(_hucreler(satir)[C_ALAN_INDEKSI])
        for satir in belge.c_veri_satirlari
        if len(_hucreler(satir)) == len(C_TABLOSU_SUTUNLARI)
    }
    eksik = [ad for ad in TEMEL_ALANLAR if _sadelestir(ad) not in gorulen]
    eksik += [ad for ad in belge.donem_sirasi if ad not in gorulen]
    if not eksik:
        return []
    return [
        _kap(
            f"Bölüm C {len(eksik)} alan/dönem için tek bir kaynak satırı "
            f"taşımıyor: {', '.join(eksik)}"
        )
    ]


def _kontrol_sistem_anahtari(belge: _Belge) -> list[str]:
    """Bölüm B `sistem anahtarı` hücresi: çözülür, kopyadır, çelişmez.

    Üç kural, üçü de sözleşmenin kendi cümlesi (dış depo `d9dc289`):
    (1) hücre `—` ya da şablonun tanıdığı anahtarlardır — biçim ve üyelik
        `sistem_anahtarlarini_coz` ile ölçülür (uydurma anahtar köprü kurmaz);
    (2) ADAY TAKVİM'deki bir dönem için hücre tablodaki demetin AYNEN
        kopyasıdır ("AYNEN kopyalanır — hepsi, tablodaki sırayla");
    (3) aynı dönem iki satırda farklı anahtar taşıyamaz (köprü belirsizleşir).
    Tablonun VARLIĞI ve sütun SAYISI bu kontrolün konusu değildir (o
    `ozel-gun-gerekce-tablosu` ailesindedir); sütun sayısı tutmayan satırda
    hücrenin hangisi olduğu bilinmez, burada ölçülmez.
    """
    mesajlar: list[str] = []
    gorulen: dict[str, tuple[str, ...]] = {}
    aday = _ADAY_TAKVIM_SADE
    for satir in belge.tablo_satirlari:
        hucreler = _hucreler(satir)
        if len(hucreler) != len(GEREKCE_TABLOSU_SUTUNLARI):
            continue
        kisa = satir.strip()[:80]
        donem = _sadelestir(hucreler[GEREKCE_DONEM_INDEKSI])
        hucre = hucreler[GEREKCE_ANAHTAR_INDEKSI]
        anahtarlar = sistem_anahtarlarini_coz(hucre)
        if anahtarlar is None:
            mesajlar.append(
                f"Gerekçe tablosu `sistem anahtarı` hücresi çözülemedi: {hucre!r} — "
                f"`{SISTEM_ANAHTARI_YOK}` ya da ADAY TAKVİM'deki anahtarlar, "
                f"virgülle, tekrarsız: {kisa!r}"
            )
            continue
        if not _aday_kopyasi_mi(donem, anahtarlar):
            if donem in aday:
                mesajlar.append(
                    f"Gerekçe tablosu `sistem anahtarı` hücresi ADAY TAKVİM'in kopyası "
                    f"değil: dönem {hucreler[GEREKCE_DONEM_INDEKSI]!r} için şablon "
                    f"{', '.join(aday[donem])!r} der, hücre {hucre!r}: {kisa!r}"
                )
            else:
                mesajlar.append(
                    f"Gerekçe tablosu: aday listesinde OLMAYAN dönem "
                    f"{hucreler[GEREKCE_DONEM_INDEKSI]!r} yalnız `{SISTEM_ANAHTARI_YOK}` ya da "
                    f"aday-dışı sistem günü anahtarı taşır ({', '.join(ADAY_DISI_SISTEM_ANAHTARLARI)}); "
                    f"başka bir dönemin anahtarı sahiplenilemez, hücre {hucre!r}: {kisa!r}"
                )
            continue
        if donem in gorulen and gorulen[donem] != anahtarlar:
            mesajlar.append(
                f"Gerekçe tablosunda aynı dönem iki FARKLI anahtar kümesiyle "
                f"geçiyor ({hucreler[GEREKCE_DONEM_INDEKSI]!r}) — köprü kurulamaz: "
                f"{kisa!r}"
            )
            continue
        gorulen.setdefault(donem, anahtarlar)
    return mesajlar


_TICARI_FIRSAT_RE = re.compile(r"ticari[\s_\-]*f[ıi]rsat", re.IGNORECASE)


def _kontrol_tur_etiketi(belge: _Belge) -> list[str]:
    """Dörtle kapalı, TEK değerli, ASCII yazım.

    Tablonun VARLIĞI bu kontrolün konusu değildir (o `ozel-gun-gerekce-tablosu`
    ailesindedir) — tablo yoksa burada satır bazlı bir şey ölçülmez.
    """
    mesajlar: list[str] = []
    for satir in belge.tablo_satirlari:
        etiketler = [
            hucre for hucre in _hucreler(satir) if hucre in TUR_ETIKETLERI
        ]
        if not etiketler:
            mesajlar.append(
                "Gerekçe tablosu satırında kapalı kümeden tür etiketi yok "
                f"({list(TUR_ETIKETLERI)}): {satir.strip()[:80]!r}"
            )
        elif len(etiketler) > 1:
            mesajlar.append(
                f"Tür etiketi TEK değerli olmalı, {etiketler} bulundu: "
                f"{satir.strip()[:80]!r}"
            )
    for eslesme in _TICARI_FIRSAT_RE.finditer(belge.ham):
        if eslesme.group(0) != "ticari-firsat":
            mesajlar.append(
                f"Tür etiketi ASCII yazımda değil: {eslesme.group(0)!r} — "
                "sözleşme `ticari-firsat` yazımını AYNEN ister"
            )
    return mesajlar


def _tablo_sekli_ihlalleri(belge: _Belge) -> list[str | _Mesaj]:
    """Tablonun ŞEKLİ: dört sütun ve dönemlerden ÖNCE.

    Ayıraçtan sonraki HERHANGİ bir satırı kabul etmek yetmez — tek sütunlu bir
    sahte tablo da "tablo var" der. Sözleşme dört alan sayar
    (`GEREKCE_TABLOSU_SUTUNLARI`) ve tabloyu dönem başlıklarından ÖNCE ister.

    **Kapsam sınırı:** sütun SAYISI ölçülür, sütun BAŞLIKLARININ anlamı değil.
    Sözleşmenin saydığı dört alan dışında sütun eklenmişse burada NOT düşer —
    belirsizlikte kapalı düşen bir kural; seviyesi `not` olduğu için maliyeti
    gürültüdür, eleme değil.
    """
    mesajlar: list[str | _Mesaj] = []
    beklenen = len(GEREKCE_TABLOSU_SUTUNLARI)
    yanlis: dict[int, int] = {}
    for sayi in belge.tablo_sutun_sayilari:
        if sayi != beklenen:
            yanlis[sayi] = yanlis.get(sayi, 0) + 1
    for sayi in sorted(yanlis):
        mesajlar.append(
            f"Gerekçe tablosunda {sayi} sütunlu satır var ({yanlis[sayi]} satır); "
            f"sözleşme {beklenen} sütun sayar: "
            f"{' + '.join(GEREKCE_TABLOSU_SUTUNLARI)}"
        )
    # KAP iddiası: "gerekli yerde tablo yok, olan tablo dönemlerden SONRA" —
    # bir bloğun içeriği hakkında değil, kabın bütünü hakkında bir KONUM iddiası.
    if belge.tablo_donem_sonrasi:
        mesajlar.append(_kap(TABLO_DONEM_SONRASI_MESAJI))
    return mesajlar


def _kontrol_gerekce_tablosu(belge: _Belge) -> list[str | _Mesaj]:
    # Bu kontrolün ÜÇ mesajı da KAP iddiasıdır (yokluk · sayım · sayım): hiçbiri
    # tek bir bloğun kendi içeriği hakkında değildir. Şekil ihlalleri
    # (`_tablo_sekli_ihlalleri`) BLOĞA aittir ve sarılMAZ.
    mesajlar: list[str | _Mesaj] = []
    if not belge.tablo_var:
        mesajlar.append(_kap(TABLO_YOK_MESAJI))
    # Kanonik başlık bir SEÇİM kuralı değil, bir NOT konusudur: denetime giren
    # bir blok başlığı taşımıyorsa bu bir ihlaldir — ama blok yine denetlenir.
    # Bölüm B'de HİÇ tablo yokken bu dal susar; aksi hâlde tablosuz her gerçek
    # çıktı ikinci bir uydurma not alırdı (ölçüldü: beş gerçek çıktının beşinde
    # de Bölüm B tablosuzdur).
    if belge.gerekce_basliksiz_sayisi:
        mesajlar.append(
            _kap(
                f"Bölüm B'de gerekçe denetimine giren "
                f"{belge.gerekce_basliksiz_sayisi} tablo gerekçe tablosunun "
                f"KANONİK başlığını taşımıyor "
                f"({' + '.join(GEREKCE_TABLOSU_SUTUNLARI)}) — yine de denetlendi"
            )
        )
    # Belirsizlik ayrı bir ihlaldir: sessizce bir blok SEÇİLMEZ, hepsi denetlenir.
    if belge.gerekce_donem_oncesi_sayisi > 1:
        mesajlar.append(
            _kap(
                f"Bölüm B'de dönem başlıklarından ÖNCE "
                f"{belge.gerekce_donem_oncesi_sayisi} tablo var — sözleşme TEK "
                "gerekçe tablosu ister; hepsi denetlendi, hiçbiri atılmadı"
            )
        )
    # Şekil kontrolü VARLIKTAN bağımsız koşar: tablo sözleşmenin istediği yerde
    # bulunamadıysa bile yanlış yerde bulunmuş OLABİLİR ve bu ayrı bir ihlaldir.
    return mesajlar + _tablo_sekli_ihlalleri(belge)


_TIRNAK_RE = re.compile(r"\"([^\"]+)\"|“([^”]+)”")


def _kontrol_uzun_alinti(belge: _Belge) -> list[str]:
    """Sözleşmenin seviyesi AÇIKÇA yazılı tek kontrolü: 40+ kelime → NOT."""
    mesajlar: list[str] = []
    blok: list[str] = []

    def blogu_kapat() -> None:
        if not blok:
            return
        metin = " ".join(blok)
        adet = len(metin.split())
        if adet >= UZUN_ALINTI_KELIME_SINIRI:
            mesajlar.append(
                f"{adet} kelimelik kesintisiz alıntı bloğu (kopya şüphesi, "
                f"sınır {UZUN_ALINTI_KELIME_SINIRI}): {metin[:60]!r}"
            )
        blok.clear()

    for satir in belge.ham.splitlines():
        if satir.lstrip().startswith(">"):
            blok.append(satir.lstrip().lstrip(">").strip())
        else:
            blogu_kapat()
    blogu_kapat()

    for eslesme in _TIRNAK_RE.finditer(belge.ham):
        metin = eslesme.group(1) or eslesme.group(2) or ""
        adet = len(metin.split())
        if adet >= UZUN_ALINTI_KELIME_SINIRI:
            mesajlar.append(
                f"{adet} kelimelik tırnak içi alıntı (kopya şüphesi): {metin[:60]!r}"
            )
    return mesajlar


def _kontrol_bicim_tam_alan_adi(belge: _Belge) -> list[str]:
    return [
        f"Alan başlığı TAM alan adıyla yazılmamış: {baslik!r}"
        for baslik in belge.yeniden_adlandirilmis
    ]


def _kontrol_bicim_sozlesme_disi_bolum(belge: _Belge) -> list[str]:
    return [
        f"Sözleşme dışı bölüm: {baslik!r} — beş bölüm dışında bölüm EKLENMEZ"
        for baslik in belge.fazla_bolumler
    ]


def _kontrol_bicim_ayri_madde(belge: _Belge) -> list[str]:
    """Her kalıp / anahtar ifade AYRI madde işareti (-) olsun — adet sayımı bozulmasın."""
    mesajlar: list[str] = []

    def tara(etiket: str, yuva: _Yuva) -> None:
        # Çit-farkında (tur 9): kural SÖZLEŞME BİÇİMİ arar ("bu içerik satırı
        # madde işareti taşıyor mu"), ham metin taramaz. DİLSİZ çitin gövdesi
        # sözleşme içeriği DEĞİLDİR — modül bunu doluluk ve adet yollarında
        # zaten böyle sayar; burada saymamak kapıyı kendi içinde çelişkiye
        # düşürür ve ölçüldü ki gerçek olmayan satırlar için not üretiyordu
        # (`'```'` için "madde işareti olmayan içerik satırı").
        for satir in _citsiz_satirlar(yuva.satirlar):
            if not satir.strip():
                continue
            if _MADDE_RE.match(satir) or _TABLO_RE.match(satir):
                continue
            if _BASLIK_GORUNUMU_RE.match(satir):
                continue
            mesajlar.append(
                f"{etiket}: madde işareti olmayan içerik satırı — kalıplar "
                f"paragrafta birleştirilirse adet sayımı bozulur: "
                f"{satir.strip()[:60]!r}"
            )

    for ad in LISTE_ALANLARI:
        yuva = belge.alanlar.get(ad)
        if yuva and ad != "video_kodlar":
            tara(ad, yuva)
    for havuz, yuva in belge.video_havuzlari.items():
        tara(f"video_kodlar.{havuz}", yuva)
    for donem in belge.donemler:
        if donem.bilincli_bos:
            continue
        for yuva_adi in OZEL_GUN_LISTE_YUVALARI:
            yuva = donem.yuvalar.get(yuva_adi)
            if yuva:
                tara(f"{donem.ad}/{yuva_adi}", yuva)
    return mesajlar


_DIPNOT_RE = re.compile(r"\[\s*\d+\s*\]|citeturn\w*|[¹²³⁴⁵⁶⁷⁸⁹⁰]")


def _kontrol_bicim_govde_dipnotu(belge: _Belge) -> list[str]:
    """Gövdede dipnot/atıf işareti yok — eşleme YALNIZ Bölüm C'dedir."""
    mesajlar: list[str] = []
    for harf in ("A", "B", "D", "E"):
        for satir in belge.bolumler.get(harf, []):
            for eslesme in _DIPNOT_RE.finditer(satir):
                mesajlar.append(
                    f"Bölüm {harf} gövdesinde dipnot/atıf işareti "
                    f"{eslesme.group(0)!r}: {satir.strip()[:60]!r}"
                )
    return mesajlar


_KANAL_ETIKET_RE = re.compile(r"\[\s*kanal\s*-\s*ba[ğg][ıi]ml[ıi]\s*:\s*([^\]]*)\]")
_BAGIMLILIK_ETIKET_RE = re.compile(r"\[\s*(kaynak[^\]]*|eski[^\]]*)\]")


def _kontrol_bicim_etiket_yazimi(belge: _Belge) -> list[str]:
    """Bağımlılık ve güncellik etiketlerinin YAZIMI — anahtar uzayı kapalıdır."""
    mesajlar: list[str] = []
    for eslesme in _KANAL_ETIKET_RE.finditer(belge.ham):
        anahtar = eslesme.group(1).strip()
        if anahtar not in KANAL_ANAHTARLARI:
            mesajlar.append(
                f"Kanal etiketi anahtarı kapalı kümenin dışında: {anahtar!r} — "
                f"{list(KANAL_ANAHTARLARI)}"
            )
    for eslesme in _BAGIMLILIK_ETIKET_RE.finditer(belge.ham):
        icerik = eslesme.group(1).strip()
        if icerik not in ("kaynak-bağımlı", "eski-kaynak"):
            mesajlar.append(
                f"Bağımlılık/güncellik etiketi yazımı sözleşmede yok: "
                f"{eslesme.group(0)!r}"
            )
    return mesajlar


# ─── 5. Kontrol kümesi (K-89 — DONDURULMUŞ) ─────────────────────────────────
#
# Kaynak: spec-input §7.3 "Kontrol kümesi" tablosu. Dokuz satırın SEKİZİ; sıra
# tablonun sırasıdır. Dokuzuncunun dışlanma gerekçesi
# `DISLANAN_KONTROL_GEREKCESI`'ndedir.

KONTROL_AILELERI = (
    "bolum-ve-alan-tamligi",
    "adet-alt-sinirlari",
    "dil-kurali",
    "url-bicimi",
    "tur-etiketi",
    "ozel-gun-gerekce-tablosu",
    "uzun-alinti",
    "bicim-kurallari",
)

# Sekizinci aile birden çok alt kural paketler; granülerlik alt kural başına BİR
# `Check`'tir ve kimlikler bu KANONİK sabitten türer.
BICIM_ALT_KURALLARI = (
    "tam-alan-adi",
    "sozlesme-disi-bolum",
    "ayri-madde-isareti",
    "govde-dipnotu",
    "etiket-yazimi",
)

_BICIM_KURALLARI = {
    "tam-alan-adi": (
        "Alan başlıkları TAM alan adıyla yazılır",
        _kontrol_bicim_tam_alan_adi,
    ),
    "sozlesme-disi-bolum": (
        "Beş bölüm dışında bölüm eklenmez",
        _kontrol_bicim_sozlesme_disi_bolum,
    ),
    "ayri-madde-isareti": (
        "Her kalıp / anahtar ifade ayrı madde işareti taşır",
        _kontrol_bicim_ayri_madde,
    ),
    "govde-dipnotu": (
        "Rapor gövdesinde dipnot/atıf işareti kullanılmaz",
        _kontrol_bicim_govde_dipnotu,
    ),
    "etiket-yazimi": (
        "Bağımlılık ve güncellik etiketleri sözleşmedeki yazımla yazılır",
        _kontrol_bicim_etiket_yazimi,
    ),
}

CHECKS: tuple[Check, ...] = (
    Check(
        kimlik="bolum-ve-alan-tamligi",
        aile="bolum-ve-alan-tamligi",
        seviye=SEVIYE_NOT,
        aciklama=(
            "Beş bölüm + sekiz temel alan + dönem yuvalarının doluluğu (K-120 "
            "muaf); ayrıca sözleşme dilbilgisi HER iç içe düzeyde: tekrar · "
            "sıra · boş bölüm"
        ),
        kural=_kontrol_bolum_ve_alan,
        kapsam_sinirlari=(
            (
                "bolum-ve-alan-tamligi: bölüm/başlık TANIMA markdown başlık "
                "düzeyine dayanan mekanik bir vekildir — sözleşme bir düzey "
                "dayatmaz, tanınmayan başlık iz bırakmaz. Boşluk ifadeleri "
                "kümesi belgelenmiş KÜÇÜK bir kümedir; kapsama oranı ÖLÇÜLMEDİ."
            ),
            (
                "bolum-ve-alan-tamligi/sıra: sabit kümelerde (bölüm · alan · "
                "video havuzu · dönem yuvası) SIRA ölçülür. Açık kümelerde "
                "(madde · dönem · Bölüm C eşleme satırı) yalnız TEKRAR ölçülür — "
                "ve bunun sebebi sözleşmenin sıra dayatmaması DEĞİLDİR: "
                "sözleşme (`_SABLON.md` satır 73-75) her listede ÖNEM SIRASI "
                "dayatır (sektöre özgülük → kaynak sayısı ve gücü → Türkiye "
                "yerelliği). Önem SEMANTİK bir yargıdır ve mekanik kapı onu "
                "DOĞRULAYAMAZ; ölçüldü ki iki çağrı kalıbı takas edildiğinde "
                "rapor `gecti / 0 not` verir. Uydurma bir sıra kuralı gerçek "
                "çıktıyı gürültüye boğardı, bu yüzden YAZILMADI."
            ),
            (
                "bolum-ve-alan-tamligi/doluluk: bir KABIN dolu sayılması "
                "sözleşmenin TANIDIĞI içerik biçimlerine bağlıdır (düz yazı "
                "satırı · madde işaretli satır · resmî `içerik-önerilmez`); "
                "markdown TABLOSU ve yatay çizgi kabı DOLDURMAZ — ölçüldü ki "
                "aksi hâlde bir dönem yuvasına konan bağımsız bir tablo o "
                "yuvanın boşluk notunu kaldırıyordu (`notlu-gecti / 1 not` -> "
                "`gecti / 0 not`). ÖLÇÜLMÜŞ KALAN SINIRLAR: (a) kural yalnız "
                "BİÇİM eler, İLGİ ölçmez — sözleşme biçiminde ama ALAKASIZ bir "
                "düz yazı satırı kabı doldurmuş sayılır ve bu makineyle "
                "DOĞRULANAMAZ; ELENEN markdown yapıları TABLO · yatay çizgi · "
                "DİLSİZ kod çiti BLOĞU (açıcısı + GÖVDESİ + kapatıcısı; KÖK "
                "düzeyinde kapanmamış çit fail-closed olarak BELGE sonuna kadar, "
                "kap içinde açılan çit ise kabı bitiren ilk satıra kadar) ile "
                "SINIRLIDIR. Dilsiz çit bu turda KAPANDI ve beyan DÜZELTİLDİ: "
                "bir önceki tur yalnız SÖZCÜKSÜZ hâlini eliyordu, gövdeli ve "
                "kapanmamış hâlleri kabı DOLDURUYORDU (ölçüldü: `notlu-gecti / "
                "1 not` -> `gecti / 0 not`) — satır-tek-tek bakan bir kural "
                "DİZİ gerektiren bir yapıyı ölçemez. HÂLÂ kabı DOLDURAN ve bu "
                "turda KAPATILMADI: "
                + " · ".join(ad for ad, _ in ACIK_BLOK_BICIMLERI)
                + " (daraltmanın gerçek çıktıdaki yanlış-pozitif maliyeti "
                "ÖLÇÜLMEDİ); (b) BÖLÜM düzeyindeki "
                "boşluk kontrolü TABLO kuralını "
                "UYGULAMAZ, çünkü sözleşme tabloyu Bölüm B gerekçesi ve Bölüm C "
                "eşlemesi olarak TANIR — bir tablo o iki kabı gerçekten "
                "doldurur; ayrı bir sınıftır ve bu turda kapatılmadı. ÇİT "
                "kuralı ise bölüm düzeyinde de UYGULANIR (tur 9): sözleşme "
                "kod çitini HİÇBİR yerde içerik saymaz — ölçüldü ki bir bölümün "
                "altına konan DİLSİZ çit, GÖVDESİ BOŞ olanı bile, `Bölüm X boş` "
                "notunu KALDIRIYORDU (50 hücrenin 50'sinde)."
            ),
            _cit_kapsam_beyani(),
        ),
    ),
    Check(
        kimlik="adet-alt-sinirlari",
        aile="adet-alt-sinirlari",
        seviye=SEVIYE_NOT,
        aciklama=(
            "Sözleşmenin ÖLÇÜLMEMİŞ adet alt sınırları — İlke 9 gereği kapı "
            "DEĞİL; sayım birimi ESSİZ doğrulanmış varlıktır, ham satır değil"
        ),
        kural=_kontrol_adet_alt_sinirlari,
    ),
    Check(
        kimlik="dil-kurali",
        aile="dil-kurali",
        seviye=SEVIYE_NOT,
        aciklama=(
            "İngilizce yüzeylerde Türkçe harf işareti — sözleşmenin ÇİFT yönlü "
            "dil kuralının yalnız bir yönü; ters yön ölçülmez"
        ),
        kural=_kontrol_dil_kurali,
        kapsam_sinirlari=(
            "dil-kurali: YALNIZ İngilizce olması gereken yüzeylerde Türkçe harf "
            "aranır. Sözleşmenin ters yönü — diğer alanların Türkçe olması — "
            "makineyle DOĞRULANMADI (sözlük gerektirir). Bu ailenin temiz çıkması "
            "Türkçe yüzeylerin doğrulandığı anlamına GELMEZ.",
        ),
    ),
    Check(
        kimlik="url-bicimi",
        aile="url-bicimi",
        seviye=SEVIYE_NOT,
        aciklama=(
            "Bölüm C SABİT SÜTUNLU tablodur: birebir başlık satırı, "
            "sözleşmenin sütun kümesi, tekrarsız `no` kimliği, dolu "
            "hücreler, açılabilir `https://` adres"
        ),
        kural=_kontrol_url_bicimi,
        kapsam_sinirlari=(
            (
                "url-bicimi: Bölüm C artık OLUMLU bir yapısal sözleşme olarak "
                "doğrulanır — sözleşmenin BİREBİR başlık satırı, SABİT sütun "
                "kümesi, hücre doluluğu, `no` hücresinin biçimi ve tablo "
                "boyunca tekrarsız-boşluksuz DİZİSİ (kimlik ayağı: denetçi ve "
                "sentez bu numarayla aynı iddiayı gösterir), `alan/dönem` "
                "hücresinin kapalı kümesi "
                "(Bölüm A alan adları + Bölüm B'de İŞLENMİŞ dönemler), `iddia` "
                "hücresinin kelime sınırı, `URL` hücresinin tek açılabilir "
                "`https://` adresi, `tarih` yazımı ve `tek kaynak` kapalı "
                "kümesi. Kapı hiçbir şeyi TAHMİN ETMEZ: önceki sürümün ayıraç "
                "vekili (serbest düzyazının GEÇTİĞİ yol) KALDIRILDI, çünkü "
                "sözleşme biçimi dayatmaya başladı (dış depo `7964ed6`). "
                "BÜTÜNLÜK de ölçülür: her alan ve her dönem için en az bir "
                "kaynak satırı aranır. ÖLÇÜLMEYEN İKİ EKSEN: bağlantının "
                "gerçekten AÇILDIĞI doğrulanmaz (ağ çağrısı yapılmaz) ve "
                "`iddia` hücresinin kaynağı gerçekten ÖZETLEDİĞİ doğrulanmaz "
                "— ikisi de anlam yargısıdır ve denetçi katmanının işidir "
                "(denetçi ADIM 1'de kaynak başına 3 iddia örnekleyip "
                "bağlantıyı açar). Bu ailenin temiz çıkması Bölüm C'nin "
                "BİÇİMİNE uyduğu anlamına gelir, içeriğinin DOĞRU olduğu "
                "anlamına GELMEZ."
            ),
        ),
    ),
    Check(
        kimlik="tur-etiketi",
        aile="tur-etiketi",
        seviye=SEVIYE_NOT,
        aciklama="Tür etiketi dörtle kapalı, tek değerli, ASCII yazım",
        kural=_kontrol_tur_etiketi,
    ),
    Check(
        kimlik="sistem-anahtari",
        # Aile kümesi DONDURULMUŞTUR (K-89, spec-input §7.3 — sekiz aile). Bu
        # kontrol gerekçe TABLOSUNUN bir hücresini ölçer; ailesi o tablonun
        # ailesidir, dokuzuncu bir aile açılmaz (`bicim-kurallari` emsali:
        # bir aile birden çok `Check` paketleyebilir).
        aile="ozel-gun-gerekce-tablosu",
        seviye=SEVIYE_NOT,
        aciklama=(
            "Bölüm B `sistem anahtarı` hücresi: `—` ya da şablonun tanıdığı "
            "anahtarlar; aday dönemde ADAY TAKVİM'in aynen kopyası; çelişmez"
        ),
        kural=_kontrol_sistem_anahtari,
        kapsam_sinirlari=(
            (
                "sistem-anahtari: anahtarın SİSTEM TAKVİMİNDE gerçekten var "
                "olduğu burada ölçülmez (kapı veritabanı görmez); üyelik "
                "pinlenmiş şablonun tablosuna karşıdır. Takvim ile şablon "
                "ayrışırsa sentezin yazım kapısı (EK-J) yakalar, bu kapı değil."
            ),
        ),
    ),
    Check(
        kimlik="ozel-gun-gerekce-tablosu",
        aile="ozel-gun-gerekce-tablosu",
        seviye=SEVIYE_NOT,
        aciklama=(
            "Bölüm B'de seçim/eleme/ekleme gerekçeleri tablosunun VARLIĞI ve "
            "ŞEKLİ: dört sütun, dönem başlıklarından önce"
        ),
        kural=_kontrol_gerekce_tablosu,
        kapsam_sinirlari=(
            (
                "ozel-gun-gerekce-tablosu: sütun SAYISI ölçülür, sütun "
                "başlıklarının ANLAMI doğrulanmadı. Denetim kümesi SEÇİLMEZ "
                "ve MONOTONdur: bir tablo EKLEMEK denetim kümesinden başka "
                "bir tabloyu ÇIKARAMAZ, dolayısıyla bir bloğa AİT notlar "
                "ekleme ile kaybolamaz (ekleme değişmezi). Dönem "
                "bloklarından ÖNCEKİ bütün tablolar denetlenir, birden "
                "çoksa belirsizlik NOTU düşer; hangisinin GERÇEK gerekçe "
                "tablosu olduğu DOĞRULANMAZ. Değişmezin İLKELİ istisnası: "
                "eklemenin KENDİ VARLIĞININ yanlışladığı YOKLUK iddiaları "
                "('kapta içerik yok', 'gerekli yerde tablo yok') düşebilir. "
                "İstisnanın SINIRI YAPISALDIR, mesaj METNİ DEĞİL: her bulgu "
                "kendi KATEGORİSİNİ üretildiği yerden taşır (`_kap` ile BEYAN "
                "edilen ALTI yol) ve beyan edilmeyen her yol fail-closed olarak "
                "DOKUNULMAZ kalır (`kap_iddiasi_mi`). Önek listesi "
                "KALDIRILDI — bağın kırılganlığı iki yönde de ölçüldü ve liste "
                "bir üretim yolunu (Bölüm C eşleme kabının yokluk iddiası) "
                "KAÇIRIYORDU. Bölgenin "
                "SINIRI ilk dönem BAŞLIĞIDIR: bir dönem başlığından SONRA "
                "gelen tablo, kanonik başlık taşısa bile denetime GİRMEZ. "
                "DÜZELTİLMİŞ ÖNCEKİ BEYAN: bu beyan bir önceki turda dönem "
                "bölgesinde kalan tablonun 'SUSTURULMAZ' olduğunu söylüyordu "
                "— ölçüm bunu YALANLADI. Fail-open geri dönüş (dönem-öncesi "
                "küme boşsa hepsini denetle) yüzünden dönem-öncesi TEK bir "
                "yem, dönem-sonrası gerçek tablonun SEKİZ notunu birden "
                "düşürüyordu (ölçüldü: 9 not -> 0 not, 24 bileşimin 4'ünde). "
                "Geri dönüş KALDIRILDI. Bugünkü ÖLÇÜLMÜŞ hâl: dönem "
                "bölgesinde kalan tablo hiç DENETLENMEZ (satır/sütun notu "
                "vermez); yerine iki KÜME düzeyi notu düşer — 'dönem "
                "başlıklarından ÖNCE tablo yok' ve 'tablo dönemlerden SONRA "
                "geliyor'. İlk döneme başlık yazılmamış ama tablonun üstüne "
                "alt yazı başlığı konmuşsa o alt yazı ilk dönemin başlığı "
                "SANILIR ve tablo bu yolla denetim dışında kalır; dönem ADI "
                "da yanlış türer. Bir düzey 1-2 ara başlık Bölüm B'yi "
                "KAPATIR (bölüm tanıma markdown düzeyine dayanır) ve o "
                "başlıktan sonrası Bölüm B sayılmaz — ölçüldü, ayrı bir "
                "sınıftır ve bu turda KAPATILMADI."
            ),
        ),
    ),
    Check(
        kimlik="uzun-alinti",
        aile="uzun-alinti",
        seviye=SEVIYE_NOT,
        aciklama="40+ kelime kesintisiz alıntı — sözleşmenin TEK açık eşlemesi (not)",
        kural=_kontrol_uzun_alinti,
    ),
) + tuple(
    Check(
        kimlik=f"bicim-kurallari/{alt}",
        aile="bicim-kurallari",
        seviye=SEVIYE_NOT,
        aciklama=_BICIM_KURALLARI[alt][0],
        kural=_BICIM_KURALLARI[alt][1],
    )
    for alt in BICIM_ALT_KURALLARI
)


# ─── 6. Koşum ───────────────────────────────────────────────────────────────


def sonuc_belirle(
    notlar: Sequence[Bulgu], elemeler: Sequence[Bulgu]
) -> str:
    """Sonuç tipini bulgulardan türetir — TEK yer.

    `elendi` bugün ancak `eleme` seviyeli bir bulgu üretilirse ulaşılır ve
    `CHECKS`'in hiçbir üyesi o seviyede DEĞİLDİR (K-88 kapanmadı). Yani dal
    temsil edilebilir, bugün erişilemez; bu bir testle ÖLÇÜLÜR.
    """
    if elemeler:
        return SONUC_ELENDI
    if notlar:
        return SONUC_NOTLU_GECTI
    return SONUC_GECTI


def run(source_text: str, *, source_name: str) -> DoctorReport:
    """Tek bir araştırma çıktısını mekanik kapıdan geçirir.

    Kapı LLM'siz ve deterministiktir; aynı metin her koşuda aynı raporu üretir.
    Bulgular `CHECKS`'in SIRASINDA toplanır.
    """
    if not isinstance(source_text, str):
        raise TypeError(f"source_text metin değil: {type(source_text).__name__}")
    if not isinstance(source_name, str) or not source_name.strip():
        raise ValueError(
            f"source_name kimlik taşımak ZORUNDA (boş/boşluk olamaz): "
            f"{source_name!r} — kapı kaynakları KİMLİĞE göre sayar (K-127)"
        )
    belge = _ayristir(source_text)
    notlar: list[Bulgu] = []
    elemeler: list[Bulgu] = []
    for check in CHECKS:
        for ham in check.kural(belge):
            # Kategori ÜRETİM yerinden gelir; beyan etmeyen yol fail-closed
            # olarak `bloga-ait` (dokunulmaz) sayılır — mesaj metni OKUNMAZ.
            mesaj = ham if isinstance(ham, _Mesaj) else _Mesaj(ham)
            bulgu = Bulgu(
                kontrol=check.kimlik,
                aile=check.aile,
                seviye=check.seviye,
                mesaj=mesaj.metin,
                kategori=mesaj.kategori,
            )
            if check.seviye == SEVIYE_ELEME:
                elemeler.append(bulgu)
            else:
                notlar.append(bulgu)
    return DoctorReport(
        sonuc=sonuc_belirle(notlar, elemeler),
        notlar=tuple(notlar),
        elemeler=tuple(elemeler),
        kaynak_adi=source_name,
        # Kimliğin İÇERİK ayağı BURADA üretilir: aynı metin iki farklı adla
        # verilirse `gate_round` onu tek kaynak sayabilsin diye (K-127 iki
        # BAĞIMSIZ kaynak ister). Kural `identity.canonical_sha`'dır, ikinci
        # bir hash kuralı YAZILMAZ.
        icerik_ozeti=identity.canonical_sha(source_text),
        # Bölüm C'nin TİPLİ satırları: motorun iddia bağı bunu tüketir. Kapı
        # satırı zaten ayrıştırıyordu; burada yalnız SONUCU taşınır.
        iddialar=_c_iddialari(belge),
        # `kapsam_sinirlari` BURADA verilmez: İlke 9(4)'ün beyanı çağıranın
        # yazdığı bir alan olamaz, `__post_init__` onu `CHECKS`'ten türetir.
    )


_kimlik_bolumlemesi = kimlik_bolumlemesi
"""Geriye uyum: modül içi çağrı yerleri ve onları çivileyen testler."""


def gate_round(reports: Sequence[DoctorReport]) -> RoundGate:
    """K-127 kaynak tabanı kapısı — kaynak SAYISI kapısı, içerik eşiği DEĞİL.

    Geçerli kaynak = elenmemiş KİMLİK. Sayı `KAYNAK_TABANI`'nın (2) altına
    düşerse koşu DURUR ve yöneticiye bildirilir: tek kaynakla mutabakat sinyali
    ilkece üretilemez, denetim `tekil` sınıfından başka bir şey veremez.

    **Sayım birimi RAPOR DEĞİL KİMLİKTİR (H1(a)).** K-127'nin bütün varlık
    sebebi "koşu en az İKİ BAĞIMSIZ kaynakla devam edebilir" cümlesidir;
    aynı kaynağın iki raporu bağımsızlık üretmez. Tekrar eden kimlik BİR
    sayılır ve `bildirim`'de adıyla bildirilir. Kimliğin kendisi
    `DoctorReport.__post_init__`'te zorunludur (boş ad kurulamaz).
    """
    raporlar = _rapor_demeti(reports)
    gecerli, elenen, tekrar, ozetsiz = kimlik_bolumlemesi(raporlar)
    dur = len(gecerli) < KAYNAK_TABANI
    parcalar: list[str] = []
    if dur:
        parcalar.append(
            f"Koşu DURDU: geçerli kaynak sayısı {len(gecerli)}, K-127 tabanı "
            f"{KAYNAK_TABANI}. Elenen kaynak(lar): {list(elenen) or 'yok'}. "
            "Yöneticiye bildirilir."
        )
    if ozetsiz:
        parcalar.append(
            f"Kanonik içerik ÖZETİ olmayan kaynak(lar): {list(ozetsiz)} — "
            "özetsiz kimlik K-127 sayımına GİRMEZ (kimliğin içerik ayağı yok, "
            "iki BAĞIMSIZ kaynak şartı doğrulanamaz); uydurma özet ÜRETİLMEZ."
        )
    if tekrar:
        parcalar.append(
            f"Tekrar eden kaynak kimliği: {list(tekrar)} — aynı kimlik BİR "
            "bağımsız kaynak sayılır (K-127 iki BAĞIMSIZ kaynak ister)."
        )
    return RoundGate(
        dur=dur,
        gecerli_kaynak_sayisi=len(gecerli),
        elenen_kaynak_sayisi=len(elenen),
        taban=KAYNAK_TABANI,
        bildirim=" ".join(parcalar),
        raporlar=raporlar,
    )
