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

**Ölçüm sınırları dürüstçe (İlke 9).** Mekanik kapı bir dil modeli değildir; aşağıdaki
kontroller sözleşmenin taranabilir yüzeyini ölçer, tamamını değil:

* Dil kuralı YALNIZ İngilizce yüzeylerde ölçülür (Türkçe'ye özgü harf işareti).
  "Diğer alanların Türkçe olması" mekanik olarak DOĞRULANMADI — sözlük gerektirir.
* Bölüm/başlık tanıma markdown başlık DÜZEYİNE dayanır: 1-2 düzey başlık bölüm
  sayılır, 3+ düzey bölüm içi kabul edilir. Sözleşme bir markdown düzeyi dayatmaz;
  bu bir mekanik vekildir.
* Boşluk ifadeleri (`_BOSLUK_IFADELERI`) belgelenmiş KÜÇÜK bir kümedir, tüketici
  değildir; kapsama oranı ölçülmemiştir.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Callable, Iterable, Sequence

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

    def __post_init__(self) -> None:
        object.__setattr__(self, "notlar", _bulgu_demeti(self.notlar, "notlar"))
        object.__setattr__(self, "elemeler", _bulgu_demeti(self.elemeler, "elemeler"))
        if not isinstance(self.kaynak_adi, str) or not self.kaynak_adi.strip():
            raise ValueError(
                "DoctorReport.kaynak_adi kimlik taşımak ZORUNDA (boş/boşluk "
                f"olamaz): {self.kaynak_adi!r} — K-127 kaynak SAYISI kapısı "
                "kimliğe göre sayar"
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


def _kimlik_bolumlemesi(
    raporlar: Sequence[DoctorReport],
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    """Raporları KİMLİĞE böler → (geçerli, elenen, tekrar eden) kimlikler.

    K-127 iki BAĞIMSIZ kaynak ister; mutabakat sinyali ilkece iki ayrı kaynağın
    işidir. Bu yüzden birim RAPOR değil KİMLİKTİR. Bir kimliğin raporlarından
    biri elendiyse kimlik elenmiş sayılır (fail-closed).
    """
    sirali: list[str] = []
    gorulen: dict[str, int] = {}
    elenen: set[str] = set()
    for rapor in raporlar:
        ad = rapor.kaynak_adi
        if ad not in gorulen:
            sirali.append(ad)
        gorulen[ad] = gorulen.get(ad, 0) + 1
        if rapor.sonuc == SONUC_ELENDI:
            elenen.add(ad)
    elenen_sirali = tuple(ad for ad in sirali if ad in elenen)
    gecerli = tuple(ad for ad in sirali if ad not in elenen)
    tekrar = tuple(ad for ad in sirali if gorulen[ad] > 1)
    return gecerli, elenen_sirali, tekrar


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
    gecerli, elenen, _ = _kimlik_bolumlemesi(raporlar)
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
) -> dict[str, _Yuva]:
    bloklar: dict[str, _Yuva] = {}
    aktif: _Yuva | None = None
    for satir in satirlar:
        eslesme = desen.match(satir)
        if eslesme:
            ad = eslesme.group(1)
            aktif = _Yuva(ad=ad, inline=(eslesme.group(2) or "").strip())
            bloklar[ad] = aktif
            continue
        if aktif is not None:
            aktif.satirlar.append(satir)
    return bloklar


def _ayristir(source_text: str) -> _Belge:
    """Rapor metnini bölümlere, alanlara ve dönemlere ayırır.

    Bölüm tanıma iki işarete dayanır: `Bölüm <harf>` kalıbı ve markdown başlık
    DÜZEYİ. 1-2 düzey başlık bölüm sayılır; 3+ düzey bölüm içi kabul edilir. Bu
    bir mekanik vekildir — sözleşme markdown düzeyi dayatmaz.
    """
    bolumler: dict[str, list[str]] = {}
    fazla: list[str] = []
    aktif: str | None = None

    for satir in source_text.splitlines():
        bolum = _BOLUM_RE.match(satir)
        if bolum:
            harf = bolum.group(1).strip().upper()
            if harf in BOLUM_HARFLERI:
                aktif = harf
                bolumler.setdefault(harf, [])
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

    a_satirlari = bolumler.get("A", [])
    alanlar = _bloklara_ayir(a_satirlari, _ALAN_DESENI)

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
    video_havuzlari = _bloklara_ayir(video.satirlar, _HAVUZ_DESENI) if video else {}

    b_satirlari = bolumler.get("B", [])
    tablo_satirlari: list[str] = []
    donemler: list[_Donem] = []
    aktif_donem: _Donem | None = None
    son_baslik: str | None = None

    for satir in b_satirlari:
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
        if aktif_donem is None:
            tablo_satirlari.append(satir)
        else:
            aktif_donem.satirlar.append(satir)

    for donem in donemler:
        donem.yuvalar = _bloklara_ayir(donem.satirlar, _YUVA_DESENI)

    tablo_veri_satirlari = _tablo_veri_satirlari(tablo_satirlari)

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
    )


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


def _kontrol_bolum_ve_alan(belge: _Belge) -> list[str]:
    mesajlar: list[str] = []
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


def _kontrol_adet_alt_sinirlari(belge: _Belge) -> list[str]:
    """ÖLÇÜLMEMİŞ sözleşme sayıları — seviyesi kalıcı olarak `not`tur (İlke 9)."""
    mesajlar: list[str] = []
    for ad, alt_sinir in ALAN_ALT_SINIRLARI.items():
        yuva = belge.alanlar.get(ad)
        adet = len(yuva.maddeler) if yuva else 0
        if adet < alt_sinir:
            mesajlar.append(
                f"`{ad}` {adet} madde taşıyor, sözleşme alt sınırı {alt_sinir} "
                "(ölçülmemiş sözleşme kuralı)"
            )
    toplam = 0
    for havuz in VIDEO_HAVUZLARI:
        yuva = belge.video_havuzlari.get(havuz)
        adet = len(yuva.maddeler) if yuva else 0
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
    if len(belge.donemler) < DONEM_ALT_SINIRI:
        mesajlar.append(
            f"Bölüm B {len(belge.donemler)} dönem işliyor, alt sınır "
            f"{DONEM_ALT_SINIRI}"
        )
    for donem in belge.donemler:
        if donem.bilincli_bos:
            # K-120: bu dönemde alt sınır denetimi UYGULANMAZ.
            continue
        for yuva_adi, alt_sinir in DONEM_YUVA_ALT_SINIRLARI.items():
            yuva = donem.yuvalar.get(yuva_adi)
            adet = len(yuva.maddeler) if yuva else 0
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


def _kontrol_url_bicimi(belge: _Belge) -> list[str]:
    mesajlar: list[str] = []
    for satir in belge.bolumler.get("C", []):
        if _TABLO_AYIRAC_RE.match(satir):
            continue
        if not (_MADDE_RE.match(satir) or _TABLO_RE.match(satir)):
            continue
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


def _kontrol_gerekce_tablosu(belge: _Belge) -> list[str]:
    if belge.tablo_var:
        return []
    return [
        "Bölüm B'de özel gün seçim/eleme/ekleme gerekçeleri tablosu yok "
        "(dönem + karar + tür etiketi + gerekçe)"
    ]


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
        aciklama="Beş bölüm + sekiz temel alan + dönem yuvalarının doluluğu (K-120 muaf)",
        kural=_kontrol_bolum_ve_alan,
    ),
    Check(
        kimlik="adet-alt-sinirlari",
        aile="adet-alt-sinirlari",
        seviye=SEVIYE_NOT,
        aciklama="Sözleşmenin ÖLÇÜLMEMİŞ adet alt sınırları — İlke 9 gereği kapı DEĞİL",
        kural=_kontrol_adet_alt_sinirlari,
    ),
    Check(
        kimlik="dil-kurali",
        aile="dil-kurali",
        seviye=SEVIYE_NOT,
        aciklama="İngilizce yüzeylerde Türkçe harf işareti (ters yön ölçülmez)",
        kural=_kontrol_dil_kurali,
    ),
    Check(
        kimlik="url-bicimi",
        aile="url-bicimi",
        seviye=SEVIYE_NOT,
        aciklama="Bölüm C kaynak satırları açılabilir tam `https://` bağlantı taşır",
        kural=_kontrol_url_bicimi,
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
        aciklama="Bölüm B'de seçim/eleme/ekleme gerekçeleri tablosunun varlığı",
        kural=_kontrol_gerekce_tablosu,
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
    gecerli, elenen, tekrar = _kimlik_bolumlemesi(raporlar)
    dur = len(gecerli) < KAYNAK_TABANI
    parcalar: list[str] = []
    if dur:
        parcalar.append(
            f"Koşu DURDU: geçerli kaynak sayısı {len(gecerli)}, K-127 tabanı "
            f"{KAYNAK_TABANI}. Elenen kaynak(lar): {list(elenen) or 'yok'}. "
            "Yöneticiye bildirilir."
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
