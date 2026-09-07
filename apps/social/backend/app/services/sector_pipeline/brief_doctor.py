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
(madde · dönem · eşleme satırı) sözleşme bir sıra DAYATMADIĞI için yalnız TEKRAR ölçülür.

**Sayıya dayalı her eşik ESSİZ DOĞRULANMIŞ varlığı sayar.** Ham `len(...)` tekrarı ve
serbest boşluk ifadesini de sayar: "5 CTA kalıbı" aynı satırın beş kopyasıyla, ">=6 dönem"
aynı dönemin iki kez yazılmasıyla sağlanabiliyordu. Alt sınırlar bu yüzden
`_Yuva.essiz_maddeler` ve `_essiz_donem_sayisi` üstünden okur.

Dilbilgisi bilerek DAR TUTULMAMIŞTIR: tanınmayan bir başlık iz bırakmaz ve ihlal
sayılmaz — yanlış pozitif üretip gerçek araştırma çıktısını gürültüye boğmasın diye. Aynı
disiplinle, Bölüm B'de gerekçe tablosu artık dönemlerden ÖNCEKİ İLK BİTİŞİK tablodur
(`_gerekce_tablosu`): ayıraçtan sonraki her `|` satırını gerekçe malzemesi saymak, bir
dönem bloğunun içine konan meşru bir ölçüm tablosundan DÖRT uydurma not doğuruyordu.

**Ölçüm sınırları dürüstçe (İlke 9).** Mekanik kapı bir dil modeli değildir; kontroller
sözleşmenin taranabilir yüzeyini ölçer, tamamını değil. Bu sınırlar artık DOCSTRING'DE
SAKLI DEĞİLDİR: `Check.kapsam_siniri` alanında yaşarlar ve `run` onları
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
* Gerekçe tablosunda sütun SAYISI ölçülür, sütun başlıklarının ANLAMI değil; Bölüm C
  bağlantılarının gerçekten açıldığı doğrulanmaz (ağ çağrısı yapılmaz).
* Bölüm C'nin ÜÇLÜ yapısı (alan/dönem → iddia → kaynak) bir AYIRAÇ vekiliyle
  (`_C_AYIRAC_RE`) görülür; parçaların ANLAMI doğrulanmaz ve vekilin kapsama oranı
  ÖLÇÜLMEMİŞTİR.
* Gerekçe tablosu "dönemlerden ÖNCEKİ İLK BİTİŞİK tablo" vekiliyle bulunur; gerekçe
  tablosundan önce Bölüm B'ye konmuş alakasız bir tablonun ayırt edilmesi DOĞRULANMADI.
* Kaynak KİMLİĞİ yazım takma adlarını (`kanonik_kaynak_kimligi`) ve aynı metnin iki adla
  verilmesini (`icerik_ozeti`) denkler. Özetsiz kimlik artık kapıya UYGUN DEĞİLDİR, ama
  özetin `run` tarafından ÜRETİLDİĞİ doğrulanamaz: biçim zorlanır, KÖKEN zorlanmaz —
  metne sahip olmayan bir çağıran biçimi geçerli bir özet uydurabilir, o eksen
  DOĞRULANMADI.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Callable, Iterable, Sequence

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
# gerekçeleri tablosu (dönem + karar + tür etiketi + gerekçe), sonra dönem dönem
# dört başlık". SÜTUN SAYISI ve SIRA sözleşmenindir; test onu pinden okur.
GEREKCE_TABLOSU_SUTUNLARI = ("dönem", "karar", "tür etiketi", "gerekçe")

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
    kural: Callable[["_Belge"], list[str]]
    kapsam_siniri: str = ""
    """Kontrolün sözleşmenin NE KADARINI ölçtüğünün dürüst beyanı.

    Boş değilse `run` onu `DoctorReport.kapsam_sinirlari`'na taşır — İlke 9(4)
    ölçülmeyen davranış iddiasının "doğrulanmadı" etiketiyle SUNULMASINI ister
    ve docstring'de saklı kalmak sunum değildir. Bu bir BULGU değildir: rapor
    sonucunu değiştirmez, temiz kaynak `gecti` kalır.
    """

    def __post_init__(self) -> None:
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
    return tuple(check.kapsam_siniri for check in CHECKS if check.kapsam_siniri)


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


def _kimlik_bolumlemesi(
    raporlar: Sequence[DoctorReport],
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    """Raporları KİMLİĞE böler → (geçerli, elenen, tekrar eden, özetsiz).

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
    gecerli, elenen, _, _ = _kimlik_bolumlemesi(raporlar)
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

    @property
    def maddeler(self) -> list[str]:
        """Madde işaretli öğeler + varsa satır-içi değer."""
        ogeler = [self.inline] if self.inline else []
        ogeler += [
            _MADDE_RE.match(satir).group(1).strip()  # type: ignore[union-attr]
            for satir in self.satirlar
            if _MADDE_RE.match(satir)
        ]
        return [oge for oge in ogeler if oge]

    @property
    def essiz_maddeler(self) -> list[str]:
        """Sözleşmenin SAYDIĞI birim: BENZERSİZ ve ANLAMLI madde.

        Ham `maddeler` tekrarı ve serbest boşluk ifadesini de sayar. Adet alt
        sınırları ham sayıyı okursa "5 CTA kalıbı" aynı satırın beş kopyasıyla
        ya da beş `yok` ile sağlanır ve kapı SESSİZ kalır — ölçüldü. Bu yüzden
        sayıya dayalı her eşik BURADAN okur (`_kontrol_adet_alt_sinirlari`).
        """
        gorulen: set[str] = set()
        essiz: list[str] = []
        for madde in self.maddeler:
            anahtar = _sadelestir(madde)
            if not anahtar or anahtar in _BOSLUK_IFADELERI or anahtar in gorulen:
                continue
            gorulen.add(anahtar)
            essiz.append(madde)
        return essiz

    @property
    def dolu(self) -> bool:
        """Anlamlı içerik var mı — serbest boşluk ifadeleri BOŞ sayılır."""
        parcalar = [self.inline] if self.inline else []
        parcalar += [satir.strip() for satir in self.satirlar]
        anlamli = [
            parca
            for parca in parcalar
            if parca and _sadelestir(parca) not in _BOSLUK_IFADELERI
        ]
        return bool(anlamli)

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
    c_esleme_satiri_var: bool = False
    # Tur 1 yalnız BÖLÜM ve ALAN düzeyini kurtardı; aşağıdakiler iç içe KALAN
    # düzeylerin sıralı-tekrarlı izleridir. Düzey listesi belgenin KENDİ içerme
    # modelinden gelir (`_SABLON.md` §5 + GÖREV A/B adımları), bulunan
    # örneklerden değil: bölüm → alan → madde → video havuzu → havuz maddesi →
    # dönem → dönem yuvası → yuva maddesi → Bölüm C eşleme satırı.
    video_havuz_sirasi: tuple[str, ...] = ()
    donem_sirasi: tuple[str, ...] = ()
    c_esleme_satirlari: tuple[str, ...] = ()
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


def _baslik_metni(satir: str) -> str:
    return satir.strip().lstrip("#").strip().strip("*`").strip()


def _bloklara_ayir(
    satirlar: Iterable[str], desen: re.Pattern[str]
) -> tuple[dict[str, _Yuva], tuple[str, ...]]:
    """Blokları ada göre sözlükler VE başlıkların görülme sırasını döndürür.

    İkinci dönüş değeri TEKRARLIDIR ve SIRALIDIR: sözlük ikisini de kaybeder,
    sözleşmenin dilbilgisi ise ikisini de sorar.
    """
    bloklar: dict[str, _Yuva] = {}
    sira: list[str] = []
    aktif: _Yuva | None = None
    for satir in satirlar:
        eslesme = desen.match(satir)
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
    """
    bolumler: dict[str, list[str]] = {}
    bolum_sirasi: list[str] = []
    fazla: list[str] = []
    aktif: str | None = None

    for satir in source_text.splitlines():
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

    bos_bolumler = tuple(
        harf
        for harf in BOLUM_HARFLERI
        if harf in bolumler and not any(satir.strip() for satir in bolumler[harf])
    )

    a_satirlari = bolumler.get("A", [])
    alanlar, alan_sirasi = _bloklara_ayir(a_satirlari, _ALAN_DESENI)

    # "Tam alan adı" ihlali: başlık görünümlü bir satırın ilk sözcüğü bir alan
    # adı ama satırın kendisi o alan adı DEĞİL (ör. "kapsam ve tanım").
    yeniden_adlandirilmis: list[str] = []
    for satir in a_satirlari:
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
    tablo_izleri: list[tuple[int, str, bool]] = []

    for sira, satir in enumerate(b_satirlari):
        if _TABLO_RE.match(satir):
            tablo_izleri.append((sira, satir, bool(donemler)))
        yuva = _YUVA_DESENI.match(satir)
        if yuva and yuva.group(1) == "mesaj_ekseni":
            aktif_donem = _Donem(
                ad=son_baslik or f"dönem-{len(donemler) + 1}",
                yuvalar={},
                satirlar=[satir],
            )
            donemler.append(aktif_donem)
            continue
        if not yuva and _BASLIK_GORUNUMU_RE.match(satir):
            # Yuva olmayan bir başlık dönemi KAPATIR: sonraki dönemin adı budur.
            son_baslik = _baslik_metni(satir)
            aktif_donem = None
            continue
        if aktif_donem is not None:
            aktif_donem.satirlar.append(satir)

    tablo_satirlari, tablo_donem_sonrasi = _gerekce_tablosu(tablo_izleri)

    for donem in donemler:
        donem.yuvalar, donem.yuva_sirasi = _bloklara_ayir(
            donem.satirlar, _YUVA_DESENI
        )

    tablo_veri_satirlari = _tablo_veri_satirlari(tablo_satirlari)
    tablo_sutun_sayilari = tuple(
        len(_hucreler(satir))
        for satir in tablo_satirlari
        if not _TABLO_AYIRAC_RE.match(satir)
    )

    c_satirlari = bolumler.get("C", [])
    c_esleme_satirlari = tuple(
        satir
        for satir in c_satirlari
        if (_MADDE_RE.match(satir) or _TABLO_RE.match(satir))
        and not _TABLO_AYIRAC_RE.match(satir)
    )

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
        c_esleme_satiri_var=bool(c_esleme_satirlari),
        video_havuz_sirasi=video_havuz_sirasi,
        donem_sirasi=tuple(_sadelestir(donem.ad) for donem in donemler),
        c_esleme_satirlari=c_esleme_satirlari,
        c_esleme_izleri=tuple(_sadelestir(satir) for satir in c_esleme_satirlari),
    )


def _gerekce_tablosu(
    izler: Sequence[tuple[int, str, bool]]
) -> tuple[list[str], bool]:
    """Bölüm B'nin İLK BİTİŞİK tablo bloğu — gerekçe tablosu ODUR.

    **Ölçülmüş gerileme (tur 2, F5):** ayıraçtan sonraki HER `|` satırını
    gerekçe tablosu saymak, Bölüm B'deki bir dönem bloğunun içine konan meşru
    ve başlıklı iki sütunlu bir tablodan 4 UYDURMA not doğuruyordu (tür etiketi
    yok ×3 + sütun sayısı). Sözleşme "ÖNCE tablo, SONRA dönem dönem dört
    başlık" der; gerekçe tablosu bu yüzden TEK ve İLK bitişik bloktur.

    Dönen ikinci değer o bloğun SIRA ihlali taşıyıp taşımadığıdır (blok bir
    dönem açıldıktan sonra başlamışsa). Sonraki tablolar hiçbir gerekçe
    kontrolüne beslenmez.

    **Kapsam sınırı:** gerekçe tablosundan ÖNCE Bölüm B'ye konmuş alakasız bir
    tablo, gerekçe tablosu sanılır — o hâlde gerçek tablo zaten sözleşmenin
    istediği yerde değildir ve notlar boşa düşmez, ama ayrım DOĞRULANMADI.
    """
    if not izler:
        return [], False
    blok = [izler[0]]
    for iz in izler[1:]:
        if iz[0] != blok[-1][0] + 1:
            break
        blok.append(iz)
    return [satir for _, satir, _ in blok], blok[0][2]


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

    `sozlesme is None` → küme AÇIKTIR (sözleşme o düzeyde bir sıra DAYATMAZ):
    yalnız TEKRAR ölçülür, sıra ölçülmez. Sıra kuralı uydurulsaydı gerçek
    araştırma çıktısı gürültüye boğulurdu.
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
    return tuple(_sadelestir(madde) for madde in yuva.maddeler)


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
    """
    mesajlar: list[str] = []
    for gorulen, sozlesme, sablon, sira_etiketi in _ic_ice_izler(belge):
        mesajlar += _iz_ihlalleri(gorulen, sozlesme, sablon, sira_etiketi)
    for harf in belge.bos_bolumler:
        mesajlar.append(
            f"Bölüm {harf} boş — başlık var, içerik yok (beş bölümün hepsi "
            "doldurulur)"
        )
    return mesajlar


def _kontrol_bolum_ve_alan(belge: _Belge) -> list[str]:
    mesajlar: list[str] = _bolum_yapisi_ihlalleri(belge)
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
# Bölüm C eşlemesinin ÜÇLÜSÜNÜ (alan/dönem → iddia → kaynak) mekanik olarak
# görebilmek için kullanılan ayıraç kümesi. Sözleşme tek bir işaret DAYATMAZ;
# bu küme belgelenmiş KÜÇÜK bir vekildir (`_BOSLUK_IFADELERI` gibi) ve kapsama
# oranı ÖLÇÜLMEMİŞTİR. Küme geniş tutuldu: fazla ayıraç parça SAYISINI artırır,
# yani yanlış-pozitif değil yanlış-negatif yönünde hata yapar.
_C_AYIRAC_RE = re.compile(r"→|->|—|–|»|\||;|,|:")


def _c_esleme_parcalari(satir: str) -> list[str]:
    """Bir Bölüm C satırının bağlantı DIŞI anlam parçaları."""
    govde = satir.strip()
    madde = _MADDE_RE.match(govde)
    govde = madde.group(1) if madde else govde.strip("|")
    return [
        parca.strip()
        for parca in _C_AYIRAC_RE.split(_URL_RE.sub(" ", govde))
        if parca.strip()
    ]


def _kontrol_url_bicimi(belge: _Belge) -> list[str]:
    """Bölüm C ÜÇLÜ eşleme içermeli ve kaynak satırları tam `https://` taşımalı.

    Sözleşme (pinli `_SABLON.md`, Bölüm C): *"alan/dönem → iddia → kaynak
    eşlemesi"*. Tur 1 yalnız "bir madde satırı var mı" + `https://` yazımını
    ölçüyordu; ölçüldü ki Bölüm C'nin tamamı tek ÇIPLAK bağlantı satırına
    indirilse bile rapor `gecti / 0 not` veriyordu. Artık her eşleme satırının
    bağlantı DIŞINDA en az iki anlam parçası (alan/dönem ve iddia) taşıması
    aranır.

    **Kapsam sınırı:** bağlantının gerçekten açılıp açılmadığı ölçülmez (ağ
    çağrısı yapılmaz); ve üçlünün parçalara AYRILDIĞI bir ayıraç vekiliyle
    (`_C_AYIRAC_RE`) görülür — parçaların ANLAMI (gerçekten alan/dönem mi,
    gerçekten iddia mı) DOĞRULANMADI.
    """
    mesajlar: list[str] = []
    c_satirlari = belge.bolumler.get("C", [])
    if any(satir.strip() for satir in c_satirlari) and not belge.c_esleme_satiri_var:
        mesajlar.append(
            "Bölüm C tek bir kaynak eşleme satırı taşımıyor — sözleşme "
            "alan/dönem → iddia → kaynak eşlemesi ister (madde ya da tablo satırı)"
        )
    for satir in belge.c_esleme_satirlari:
        if len(_c_esleme_parcalari(satir)) < 2:
            mesajlar.append(
                "Bölüm C eşleme satırı ÜÇLÜ değil — sözleşme alan/dönem → "
                "iddia → kaynak ister, satır bağlantı dışında iki anlam "
                f"parçası taşımıyor: {satir.strip()[:80]!r}"
            )
        if "https://" not in satir:
            mesajlar.append(
                "Bölüm C kaynak satırı açılabilir tam bağlantı taşımıyor "
                f"(oturum-içi atıf kodu / dipnot / alan adı kısaltması kabul "
                f"edilmez): {satir.strip()[:80]!r}"
            )
        if "http://" in satir:
            mesajlar.append(
                f"Bölüm C satırı `http://` bağlantı taşıyor: {satir.strip()[:80]!r}"
            )
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


def _tablo_sekli_ihlalleri(belge: _Belge) -> list[str]:
    """Tablonun ŞEKLİ: dört sütun ve dönemlerden ÖNCE.

    Ayıraçtan sonraki HERHANGİ bir satırı kabul etmek yetmez — tek sütunlu bir
    sahte tablo da "tablo var" der. Sözleşme dört alan sayar
    (`GEREKCE_TABLOSU_SUTUNLARI`) ve tabloyu dönem başlıklarından ÖNCE ister.

    **Kapsam sınırı:** sütun SAYISI ölçülür, sütun BAŞLIKLARININ anlamı değil.
    Sözleşmenin saydığı dört alan dışında sütun eklenmişse burada NOT düşer —
    belirsizlikte kapalı düşen bir kural; seviyesi `not` olduğu için maliyeti
    gürültüdür, eleme değil.
    """
    mesajlar: list[str] = []
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
    if belge.tablo_donem_sonrasi:
        mesajlar.append(
            "Gerekçe tablosu dönem başlıklarından SONRA geliyor — sözleşme "
            "ÖNCE tablo, SONRA dönem dönem dört başlık der"
        )
    return mesajlar


def _kontrol_gerekce_tablosu(belge: _Belge) -> list[str]:
    mesajlar: list[str] = []
    if not belge.tablo_var:
        mesajlar.append(
            "Bölüm B'de özel gün seçim/eleme/ekleme gerekçeleri tablosu yok "
            f"({' + '.join(GEREKCE_TABLOSU_SUTUNLARI)})"
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
        for satir in yuva.satirlar:
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
        kapsam_siniri=(
            "bolum-ve-alan-tamligi: bölüm/başlık TANIMA markdown başlık düzeyine "
            "dayanan mekanik bir vekildir — sözleşme bir düzey dayatmaz, tanınmayan "
            "başlık iz bırakmaz. Boşluk ifadeleri kümesi belgelenmiş KÜÇÜK bir "
            "kümedir; kapsama oranı ÖLÇÜLMEDİ. Açık kümelerde (madde · dönem · "
            "Bölüm C eşleme satırı) yalnız TEKRAR ölçülür: sözleşme o düzeylerde "
            "bir SIRA dayatmaz, uydurulsaydı gerçek çıktı gürültüye boğulurdu."
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
        kapsam_siniri=(
            "dil-kurali: YALNIZ İngilizce olması gereken yüzeylerde Türkçe harf "
            "aranır. Sözleşmenin ters yönü — diğer alanların Türkçe olması — "
            "makineyle DOĞRULANMADI (sözlük gerektirir). Bu ailenin temiz çıkması "
            "Türkçe yüzeylerin doğrulandığı anlamına GELMEZ."
        ),
    ),
    Check(
        kimlik="url-bicimi",
        aile="url-bicimi",
        seviye=SEVIYE_NOT,
        aciklama=(
            "Bölüm C ÜÇLÜ bir eşleme İÇERİR (alan/dönem → iddia → kaynak) ve "
            "kaynak satırları açılabilir tam `https://` bağlantı taşır"
        ),
        kural=_kontrol_url_bicimi,
        kapsam_siniri=(
            "url-bicimi: bağlantının gerçekten AÇILDIĞI doğrulanmadı — ağ çağrısı "
            "yapılmaz, yalnız `https://` yazımı taranır. Eşlemenin ÜÇLÜ yapısı "
            "(alan/dönem → iddia → kaynak) bir ayıraç vekiliyle görülür; "
            "parçaların ANLAMI doğrulanmadı, vekilin kapsama oranı ÖLÇÜLMEDİ."
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
        kimlik="ozel-gun-gerekce-tablosu",
        aile="ozel-gun-gerekce-tablosu",
        seviye=SEVIYE_NOT,
        aciklama=(
            "Bölüm B'de seçim/eleme/ekleme gerekçeleri tablosunun VARLIĞI ve "
            "ŞEKLİ: dört sütun, dönem başlıklarından önce"
        ),
        kural=_kontrol_gerekce_tablosu,
        kapsam_siniri=(
            "ozel-gun-gerekce-tablosu: sütun SAYISI ölçülür, sütun başlıklarının "
            "ANLAMI doğrulanmadı. Tablo, Bölüm B'nin dönemlerden ÖNCEKİ İLK "
            "BİTİŞİK tablosu vekiliyle bulunur; gerekçe tablosundan ÖNCE konmuş "
            "alakasız bir tablonun ayırt edilmesi DOĞRULANMADI."
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
        for mesaj in check.kural(belge):
            bulgu = Bulgu(
                kontrol=check.kimlik,
                aile=check.aile,
                seviye=check.seviye,
                mesaj=mesaj,
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
        # `kapsam_sinirlari` BURADA verilmez: İlke 9(4)'ün beyanı çağıranın
        # yazdığı bir alan olamaz, `__post_init__` onu `CHECKS`'ten türetir.
    )


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
    gecerli, elenen, tekrar, ozetsiz = _kimlik_bolumlemesi(raporlar)
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
