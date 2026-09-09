"""Politika motoru — §9.2 zorunlu kontrol kümesi (Plan 2 Task 12).

**Motor SONUÇ üretmez, BULGU üretir.** `run_checks` saf bir ölçüm
fonksiyonudur: veritabanına dokunmaz, koşu sonucu (`activation_eligible` ·
`no_change` · `blocked`) döndürmez, sentez raporunu yerinde değiştirmez.
Bulguyu sonuca çeviren `decide`'dır ve o Task 13'te doğar (arayüz eki R7).

**Dört ölçüm kanalı, dördünün de tanımlı bir tüketicisi var:**

* `bulgular` → `engine_contract.BULGU_SINIFLARI` (KAPALI, altı); Task 13'ün
  dönüşüm tablosu hepsini tüketir.
* `uygulanmayan_kararlar` → `UYGULANMAMA_SEBEPLERI` (KAPALI, üç); kararı
  UYGULAMAYAN da Task 13'tür — burada yalnız KAYDEDİLİR.
* `notlar` → karar günlüğünün `tur="not"` satırları (`identity.NOT_SINIFLARI`).
* `olcumler` → K-24'ün ham dağılımı; `engine_diff`/`barrier_report`'un girdisi.

**Kapalı kümeye sığmayan ihlal BULGU İCAT ETMEZ.** Girdi kapıdan geçmiyorsa
(bozuk şema, durmuş mekanik tur) motor `EngineInputError` ile fail-closed
durur — `identity.decision_units` emsali. Yeni bir bulgu sınıfı ya da yeni bir
uygulanmama sebebi eklemek sözleşme revizyonudur (`engine_contract`, Task 8).

**Ölçülmemiş değer kapı yapılmaz (İlke 9).** Alan boyutu ÖLÇÜLÜR ve
`olcumler`'e yazılır; hiçbir eşiği yoktur ve hiçbir şeyi bloklamaz. Bariyerler
(K-130/131/132) bu modülün DEĞİL Task 13'ün kalemidir.

**Dürüst kapsam sınırları (İlke 3) — burada ÖLÇÜLEMEYEN üç kalem:**

1. **K-123 resmîlik ölçütü** metinsel bir yargıdır ve `EngineInputs`'a girmez
   (R5 alan kümesi KAPALI). K-126 istisnasının motorda ölçülebilen ayağı
   yalnız canlı URL doğrulamasıdır (`erisildi ∧ icerik_uyumlu`); resmîlik ayağı
   denetçi katmanında yaşar ve buraya UYDURULMAZ.
2. **Takvim KATEGORİSİ** girdide yoktur — `takvim_anahtarlari` yalnız
   anahtarları taşır. Bu yüzden K-03'ün motordaki ayağı paket içi tür etiketi
   çatışmasıdır (aktif tür ↔ aday tür); tür↔kategori çatışmasının üretim ayağı
   prompt yolundadır (spec §11.2) ve orada yaşar.
3. **Yedi bayrağın beşinin** pakete girmeme kuralını YAZIM KAPISI uygular
   (`sector_content_schema` ayraç yüzeyleri). Buradaki kontrol, yazım kapısının
   BAKMADIĞI yeri — karar satırının `kanit`/`gerekce` metnini — tarar; ikinci
   bir yazım kapısı yazılmaz.
"""

from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from app.services.sector_content_schema import (
    LIST_FIELDS,
    SPECIAL_DAY_SLOTS,
    TEXT_FIELDS,
    VIDEO_POOL_KEYS,
    structural_errors,
)
from app.services.sector_pipeline import identity
from app.services.sector_pipeline.auditors import KAYNAK_ETIKETI, ValidatedAuditPair
from app.services.sector_pipeline.brief_doctor import RoundGate, kimlik_bolumlemesi
from app.services.sector_pipeline.engine_contract import (
    BulguIzi,
    EngineResult,
    KararsizMadde,
    PolicyReport,
    UygulanmayanKarar,
)
from app.services.sector_pipeline.policy_config import PolicyConfig, config_sha
from app.services.sector_pipeline.synthesis import (
    MEVZUAT_ALANLARI,
    SynthesisResult,
    dogrulanmis_referanslar,
)


class EngineInputError(ValueError):
    """Motor girdisi kapıdan geçmedi — kontroller KOŞMAZ (fail-closed)."""


# ─── Kapalı yardımcı kümeler ────────────────────────────────────────────────

KAYNAK_TABANI_YENI_OGE = 2
"""`2-3` yapısal çoğunluk kuralının payı — spec §9.2'nin OYLAMA tasarımı.

Ölçülmüş bir eşik DEĞİLDİR (İlke 9): kaynak sözleşmesi motordan bağımsız
yürürlüktedir, motor onu UYGULAR, KOYMAZ.
"""

BAYRAKLAR: tuple[str, ...] = (
    "kaynak-bagimli",
    "genel-gecer",
    "yerel-degil",
    "kopya-suphesi",
    "marka-adi",
    "kanal-bagimli",
    "eski-kaynak",
    "metin-ogesi",
)
"""Kapalı bayrak kümesi — SEKİZ üye (denetçi sözleşmesi, sentez görevi 130-133).

Değerler pinlenmiş sözleşmeden ÖLÇÜLEREK yazıldı ve aksan-katlanmış biçimde
tutuluyor; `[kanal-bağımlı: X]` ile `[kanal-bagimli: X]` aynı bayraktır.
"""

SAG_CIKAN_BAYRAK = "kanal-bagimli"
"""Sentezden sağ çıkan TEK bayrak (sentez görevi 212-214); kalan yedi TÜKETİLİR."""

_BAYRAK_RE = re.compile(r"\[([^\]]*)\]")

MEVZUAT_ANAHTAR_KELIMELERI: tuple[str, ...] = (
    "mevzuat",
    "kanun",
    "yonetmelik",
    "teblig",
    "yasa",
    "madde",
    "vergi",
    "kdv",
    "ayar",
    "damga",
    "garanti",
    "tuketici",
    "iade",
    "standart",
)
"""K-129'un ikinci kolu: mevzuat iddiası taşıyan maddelerin MEKANİK işaretleri.

K-129 kapandı ve SABİTTİR: `yasaklar_ve_hassasiyetler` alanının tamamı + mevzuat/
tarih/sayı iddiası içeren tüm maddeler (spec §9.4). Tarih ve sayı ayağı rakam
varlığıyla, mevzuat ayağı bu aksan-katlanmış kelime listesiyle ölçülür. Liste
GENİŞ tutulur: yanlış-pozitif yönü bloklamaya (fail-closed), yanlış-negatif yönü
mevzuat uyuşmazlığını sessizce geçirmeye (fail-open) çıkar. Genişletmesi spec
revizyonudur.

**Eşleme ALT-DİZEDİR ve bu bilinçlidir.** Türkçe eklemeli bir dildir: "ayar"
kelimesi metinde "ayarı", "ayarında", "ayarlar" olarak geçer ve kelime-sınırı
ankoru bunları KAÇIRIR. Alt-dize eşlemesinin bedeli, kelimeyi içinde barındıran
ilgisiz bir sözcüğün de eşleşmesidir (yanlış-pozitif) — yön fail-closed olduğu
için bu bedel bilinçle kabul edilir. Kabul edilmiş kalan risk: rakam kolu
sıradan sayısal metni de mevzuat sayar (checkpoint 9, orta — accepted_risk).
"""

_CIKARMA_DESTEKLEYEN = frozenset({"contradicted"})
_GUNCELLEME_DESTEKLEYEN = frozenset({"contradicted", "needs_update"})
_DOGRULANAMADI_STATUSU = "risk_unverified"


# ─── Tipler (arayüz eki R5) ─────────────────────────────────────────────────


@dataclass(frozen=True)
class GateResults:
    """Otomatik kapı sonuçları — motorun ÖLÇMEDİĞİ, DEVRALDIĞI iki kapı."""

    katman1_passed: bool
    tek_aktif_ihlali: bool

    def __post_init__(self) -> None:
        # F4 (checkpoint 9, yüksek — ÖLÇÜLDÜ): anotasyon çalışma zamanı kapısı
        # DEĞİLDİR. Serileştirmeden gelen `"false"` DİZESİ doğruluk-değeriyle
        # DOĞRUdur; ölçümde `katman1_passed="false"` regresyon kapısını sessizce
        # GEÇTİ (bulgu üretilmedi). Bu, zorunlu kapının fail-open hâlidir.
        # Emsal: `sector_package_lifecycle._require_flag` aynı kuralı kurar.
        for _alan in ("katman1_passed", "tek_aktif_ihlali"):
            _deger = getattr(self, _alan)
            if type(_deger) is not bool:
                raise TypeError(
                    f"GateResults.{_alan} GERÇEKTEN bool olmalı "
                    f"({type(_deger).__name__} verildi) — doğru-görünen değer "
                    "kapı kanıtı DEĞİLDİR"
                )


@dataclass(frozen=True)
class EngineInputs:
    """Motor girdileri — ALAN KÜMESİ KAPALIDIR (K-52, spec §9.1).

    Marka DNA'sı için alan YOKTUR ve eklenmesi sözleşme revizyonu ister.
    `PolicyConfig` buraya GİRMEZ: `decide(inputs, config)` onu ayrı alır.
    """

    sentez: SynthesisResult
    aktif_paket: Mapping | None
    aktif_schema_version: int | None
    aktif_birimler: Mapping[str, Mapping]
    mevcut_birim_sayisi: int
    ilk_kosu: bool
    son_turlarin_cikarmalari: tuple[Mapping, ...]
    denetci_envanterleri: ValidatedAuditPair
    mekanik_eleme: RoundGate
    takvim_anahtarlari: frozenset[str]
    otomatik_kapilar: GateResults

    def __post_init__(self) -> None:
        # SIRA BAĞLAYICIDIR (R5/A3): ÖNCE dondur, SONRA kontrol et. Anotasyon
        # çalışma zamanı zorlaması DEĞİLDİR; çağıran değiştirilebilir bir `dict`
        # verirse takma ad paylaşılır ve `mevcut_birim_sayisi == len(...)`
        # invariantı yapımdan SONRA sessizce bozulurdu.
        for _alan in ("aktif_paket", "aktif_birimler", "son_turlarin_cikarmalari"):
            object.__setattr__(self, _alan, identity.donmus(getattr(self, _alan)))
        # `takvim_anahtarlari` ZATEN değişmezdir (`frozenset`), ama çağıran `set`
        # verebilir; `donmus` onu da çevirir — aynı TEK kural, ikinci kural YOK.
        object.__setattr__(
            self, "takvim_anahtarlari", identity.donmus(self.takvim_anahtarlari)
        )
        if type(self.denetci_envanterleri) is not ValidatedAuditPair:
            raise TypeError(
                "denetci_envanterleri ValidatedAuditPair olmalı "
                f"({type(self.denetci_envanterleri).__name__} verildi) — ham denetçi "
                "raporu motora GİRMEZ; doğrulayıcı ve tur-seviyesi mutabakat atlanamaz"
            )
        # F4 (checkpoint 9, yüksek): invariant TAŞIYAN iki tip de KİMLİKLE aranır.
        # `RoundGate`/`GateResults` değişmezlerini kendi `__post_init__`'lerinde
        # zorlar; benzeyen bir nesne (`dur=False` taşıyan serbest sınıf) o
        # değişmezleri ATLAYARAK motora girerdi.
        if type(self.mekanik_eleme) is not RoundGate:
            raise TypeError(
                "mekanik_eleme RoundGate olmalı "
                f"({type(self.mekanik_eleme).__name__} verildi) — benzeyen nesne "
                "kapı değişmezlerini taşımaz"
            )
        if type(self.otomatik_kapilar) is not GateResults:
            raise TypeError(
                "otomatik_kapilar GateResults olmalı "
                f"({type(self.otomatik_kapilar).__name__} verildi)"
            )
        if self.mevcut_birim_sayisi != len(self.aktif_birimler):
            raise ValueError("mevcut_birim_sayisi aktif_birimler ile tutarsız")
        # F1 (checkpoint 9, yüksek — ÖLÇÜLDÜ): `ValidatedAuditPair` iki raporun
        # BİR görüntü üzerinde uyuştuğunu kanıtlar; o görüntünün BU çağrıdaki
        # aktif birimler olduğunu KANITLAMAZ. Ölçümde farklı bir içerikten
        # türetilmiş birimler, eski çifte takılmadan kabul edildi: kimlikler
        # kalıcı olduğu için bayat statüler değişmiş içeriğe cevap veriyor ve
        # R6'nın görüntü sınırı sessizce düşüyordu. Bağ ARTIK YAPIMDA kurulur.
        _gorunti = identity.canonical_sha(self.aktif_birimler)
        if _gorunti != self.denetci_envanterleri.unit_snapshot_sha:
            raise ValueError(
                "denetci_envanterleri BU aktif görüntüye ait değil: çift "
                f"{self.denetci_envanterleri.unit_snapshot_sha}, aktif birimler "
                f"{_gorunti} — bayat envanter değişmiş içeriğe cevap veremez "
                "(K-79/K-100, arayüz eki R6)"
            )


@dataclass(frozen=True)
class CheckOutput:
    """Tek bir kontrolün ölçümü. Boş çıktı = o kontrol bir şey görmedi."""

    bulgular: tuple[BulguIzi, ...] = ()
    uygulanmayan_kararlar: tuple[UygulanmayanKarar, ...] = ()
    notlar: tuple[Mapping, ...] = ()
    olcumler: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class CheckOutcome:
    """`run_checks`'in TEK çıktısı — dört ölçüm kanalı, sonuç YOK."""

    bulgular: tuple[BulguIzi, ...]
    uygulanmayan_kararlar: tuple[UygulanmayanKarar, ...]
    notlar: tuple[Mapping, ...]
    olcumler: Mapping[str, Any]

    def __post_init__(self) -> None:
        # `donmus` donmuş dataclass'ı REDDEDER (kural 5); bulgu/karar demetleri
        # bu yüzden `tuple(...)` KOPYASIYLA kapanır — `PolicyReport` emsali.
        for _alan, _tip in (
            ("bulgular", BulguIzi),
            ("uygulanmayan_kararlar", UygulanmayanKarar),
        ):
            _deger = tuple(getattr(self, _alan))
            for _oge in _deger:
                if type(_oge) is not _tip:
                    raise TypeError(
                        f"CheckOutcome.{_alan} yalnız {_tip.__name__} taşır "
                        f"({type(_oge).__name__} verildi)"
                    )
            object.__setattr__(self, _alan, _deger)
        for _alan in ("notlar", "olcumler"):
            object.__setattr__(self, _alan, identity.donmus(getattr(self, _alan)))


@dataclass(frozen=True)
class EngineCheck:
    """§9.2 kümesinin tek üyesi. `ad` KAPALI kümenin parçasıdır (K-89 emsali)."""

    ad: str
    aciklama: str
    calistir: Callable[[EngineInputs], CheckOutput]


# ─── Ortak ölçüm yardımcıları ───────────────────────────────────────────────


def _katla(metin: str) -> str:
    """Aksanı katlanmış, küçük harfli biçim — `ş`/`s`, `ğ`/`g` aynı sayılır."""
    ayrisik = unicodedata.normalize("NFKD", metin)
    return "".join(ch for ch in ayrisik if not unicodedata.combining(ch)).casefold()


def _aday_icerik(inputs: EngineInputs) -> dict:
    """Aday paket içeriği — donmuş temsil ÇÖZÜLEREK (şema `list` ister)."""
    return identity.cozulmus(inputs.sentez.aday_json)


def _gunluk(inputs: EngineInputs) -> list[dict]:
    return [dict(satir) for satir in inputs.sentez.karar_gunlugu]


def _karar_satirlari(inputs: EngineInputs) -> list[dict]:
    return [satir for satir in _gunluk(inputs) if satir.get("tur") == "karar"]


def _metin(deger: Any) -> str:
    """Bir öğenin ölçülebilir metin temsili — sözlük öğeler de taranır."""
    if isinstance(deger, str):
        return deger
    return json.dumps(deger, ensure_ascii=False, sort_keys=True, default=str)


def _satir_metni(inputs: EngineInputs, satir: Mapping) -> str:
    """Satırın konu olduğu ÖĞENİN metni.

    Yaşayan satırda aday içerikteki değer, düşen satırda (`cikar`/`kirp`) aktif
    paketteki değer okunur — düşen öğe adayda zaten YOKTUR.
    """
    yol = satir.get("oge_yolu")
    birimler = identity.enumerate_content_units(_aday_icerik(inputs))
    if yol in birimler:
        return _metin(birimler[yol]["deger"])
    birim = inputs.aktif_birimler.get(satir.get("unit_id"))
    return _metin(birim["deger"]) if birim else ""


def _mevzuat_mi(alan: str, metin: str) -> bool:
    """K-129 — mekanik, yorumsuz: alan listesi + tarih/sayı + mevzuat kelimesi."""
    if alan in MEVZUAT_ALANLARI:
        return True
    katlanmis = _katla(metin)
    if any(ch.isdigit() for ch in katlanmis):
        return True
    return any(kelime in katlanmis for kelime in MEVZUAT_ANAHTAR_KELIMELERI)


def _referanslar(inputs: EngineInputs) -> set[str]:
    """İki denetçinin DOĞRULANMIŞ URL referans kümesi — kural TEK yerde yaşar."""
    cift = inputs.denetci_envanterleri
    return dogrulanmis_referanslar(cift.birinci) | dogrulanmis_referanslar(cift.ikinci)


def _denetci_satiri_kanitlari(inputs: EngineInputs, unit_id: str) -> set[str]:
    """O BİRİME ait denetçi envanter satırlarının taşıdığı kanıt referansları.

    F5 (checkpoint 9, yüksek — ÖLÇÜLDÜ): kanonik kural İKİ kollu — *"`guncelle`
    ve `cikar` kararları **denetçi satırı** veya doğrulanmış URL referansı
    taşımalı"* (spec girdisi satır 1189). İlk yazım yalnız URL kolunu tanıyordu;
    ölçümde doğrulanmış referans kümesi `{KAYNAK-1, https://...}` ile sınırlıydı,
    yani denetçinin kendi satırına dayanan meşru bir `guncelle` `kanit-yok`
    olarak kaydediliyordu — fail-closed bir işletim kırığı.

    Satır YOLA değil KİMLİĞE anahtarlanır: envanter K-100 gereği her aktif birimi
    tam bir kez taşır. `#<no>` biçimli satır numarası TİPLİ girdide YOKTUR ve
    buraya ayrıştırılmaz — sunum sırasından türetilen numara kayabilir; kimlik
    kaymaz.
    """
    cift = inputs.denetci_envanterleri
    kanitlar: set[str] = set()
    for rapor in (cift.birinci, cift.ikinci):
        for satir in rapor.yeniden_dogrulama:
            if satir.unit_id != unit_id:
                continue
            if isinstance(satir.kanit, str) and satir.kanit.strip():
                kanitlar.add(satir.kanit.strip())
    return kanitlar


def _kanit_parcalari(kanit: Any) -> list[str]:
    if not isinstance(kanit, str):
        return []
    return [parca.strip() for parca in kanit.split(",") if parca.strip()]


def _envanter_statuleri(inputs: EngineInputs, unit_id: str) -> list[set[str]]:
    """Rapor BAŞINA statü kümesi — mutabakat TUR seviyesinde okunur."""
    cift = inputs.denetci_envanterleri
    return [
        {satir.statu for satir in rapor.yeniden_dogrulama if satir.unit_id == unit_id}
        for rapor in (cift.birinci, cift.ikinci)
    ]


def _bayraklar(metin: str) -> set[str]:
    """Metindeki KAPALI kümeye ait bayraklar (aksan katlanmış adlarıyla)."""
    bulunan: set[str] = set()
    for ayrac in _BAYRAK_RE.findall(metin):
        ad = _katla(ayrac.split(":")[0]).strip().replace(" ", "")
        if ad in BAYRAKLAR:
            bulunan.add(ad)
    return bulunan


def _aktif_ozel_gunler(inputs: EngineInputs) -> dict:
    aktif = inputs.aktif_paket or {}
    icerik = aktif.get("content") or {}
    ozel_gun = icerik.get("ozel_gun") or {}
    return dict(ozel_gun)


# ─── Kontroller (§9.2 — sıra plan tarafından bağlıdır) ──────────────────────


def _sema_ve_boyut(inputs: EngineInputs) -> CheckOutput:
    icerik = _aday_icerik(inputs)
    try:
        identity.decision_units(icerik, _gunluk(inputs))
    except (ValueError, TypeError) as exc:
        raise EngineInputError(f"şema kapısı düştü: {exc}") from exc

    birimler = identity.enumerate_content_units(icerik)
    alan_karakterleri: dict[str, int] = {}
    for birim in birimler.values():
        alan_karakterleri[birim["alan"]] = alan_karakterleri.get(birim["alan"], 0) + len(
            _metin(birim["deger"])
        )
    boyut = {
        "toplam_karakter": len(
            json.dumps(icerik, ensure_ascii=False, sort_keys=True, default=str)
        ),
        "birim_sayisi": len(birimler),
        "alan_karakterleri": alan_karakterleri,
    }
    # İlke 9: ÖLÇÜLÜR, kapı DEĞİLDİR. Eşiği burada YOKTUR ve olmayacaktır.
    return CheckOutput(olcumler={"boyut": boyut})


def _karar_kapsami(inputs: EngineInputs) -> CheckOutput:
    aktif = set(inputs.aktif_birimler)
    satirlar = _karar_satirlari(inputs)
    gorulen = {satir["unit_id"] for satir in satirlar}
    bulgular: list[BulguIzi] = []

    for unit_id in sorted(aktif - gorulen):
        bulgular.append(
            BulguIzi(
                sinif="kapsam_ihlali",
                unit_id=unit_id,
                detay=(
                    "aktif birimin bu turda SONUCU yok — kısmi turda değişmeyen "
                    "birim de kendi `koru` satırını taşır (K-107); not satırı "
                    "kapsamı KARŞILAMAZ"
                ),
            )
        )
    for satir in satirlar:
        unit_id = satir["unit_id"]
        if unit_id in aktif or satir.get("karar") == "ekle":
            continue
        bulgular.append(
            BulguIzi(
                sinif="kapsam_ihlali",
                unit_id=unit_id,
                detay=(
                    f"karar {satir.get('karar')!r} tanınmayan bir kimliğe veriliyor — "
                    "aktif pakette karşılığı YOK"
                ),
            )
        )
    return CheckOutput(bulgular=tuple(bulgular))


def _kimlik_benzersizligi(inputs: EngineInputs) -> CheckOutput:
    aktif = set(inputs.aktif_birimler)
    bulgular: list[BulguIzi] = []
    for satir in _karar_satirlari(inputs):
        if satir.get("karar") != "ekle":
            continue
        unit_id = satir["unit_id"]
        if unit_id in aktif:
            bulgular.append(
                BulguIzi(
                    sinif="kapsam_ihlali",
                    unit_id=unit_id,
                    detay=(
                        "`ekle` satırı aktif bir kimliği yeniden kullanıyor — yeni "
                        "kalıp YENİ kimlik alır (K-86/K-152)"
                    ),
                )
            )
        hedef = satir.get("yerine_gecer")
        if hedef is not None and hedef not in aktif:
            bulgular.append(
                BulguIzi(
                    sinif="kapsam_ihlali",
                    unit_id=unit_id,
                    detay=(
                        f"`yerine_gecer` aktif olmayan kimliğe işaret ediyor: {hedef!r} "
                        "— çıkarma/ekleme çifti kopuk (K-154)"
                    ),
                )
            )
    return CheckOutput(bulgular=tuple(bulgular))


def _kanit(inputs: EngineInputs) -> CheckOutput:
    referanslar = _referanslar(inputs)
    kayitlar: list[UygulanmayanKarar] = []
    for satir in _karar_satirlari(inputs):
        karar = satir.get("karar")
        if karar not in ("guncelle", "cikar"):
            continue
        parcalar = _kanit_parcalari(satir.get("kanit"))
        kabul = referanslar | _denetci_satiri_kanitlari(inputs, satir["unit_id"])
        if any(parca in kabul for parca in parcalar):
            continue
        kayitlar.append(
            UygulanmayanKarar(unit_id=satir["unit_id"], karar=karar, sebep="kanit-yok")
        )
    return CheckOutput(uygulanmayan_kararlar=tuple(kayitlar))


def _mutabakat(inputs: EngineInputs) -> CheckOutput:
    bulgular: list[BulguIzi] = []
    kayitlar: list[UygulanmayanKarar] = []

    for satir in _karar_satirlari(inputs):
        karar = satir.get("karar")
        if karar not in ("guncelle", "cikar"):
            continue
        unit_id = satir["unit_id"]
        if unit_id not in inputs.aktif_birimler:
            continue  # kapsam kontrolünün konusu; burada ikinci kez bulgu ÜRETİLMEZ
        destekleyen = (
            _CIKARMA_DESTEKLEYEN if karar == "cikar" else _GUNCELLEME_DESTEKLEYEN
        )
        statuler = _envanter_statuleri(inputs, unit_id)
        if all(statu & destekleyen for statu in statuler):
            continue
        if _mevzuat_mi(satir.get("alan", ""), _satir_metni(inputs, satir)):
            bulgular.append(
                BulguIzi(
                    sinif="mevzuat_uyusmazligi",
                    unit_id=unit_id,
                    detay=(
                        f"K-125: mevzuat/güvenlik biriminde iki denetçi {karar!r} "
                        f"kararında uyuşmuyor (statüler: {[sorted(s) for s in statuler]})"
                    ),
                )
            )
            continue
        kayitlar.append(
            UygulanmayanKarar(unit_id=unit_id, karar=karar, sebep="mutabakat-yok")
        )

    # K-128 yolu — YALNIZ bulgu üretir; bloklamaya çeviren bayrak Task 13'tedir
    # ve varsayılanı KAPALIDIR. K-125 yolundan AYRIDIR (spec §9.4).
    for unit_id in sorted(inputs.aktif_birimler):
        birim = inputs.aktif_birimler[unit_id]
        if not _mevzuat_mi(birim.get("alan", ""), _metin(birim.get("deger"))):
            continue
        statuler = _envanter_statuleri(inputs, unit_id)
        if any(_DOGRULANAMADI_STATUSU in statu for statu in statuler):
            bulgular.append(
                BulguIzi(
                    sinif="mevzuat_dogrulanamadi",
                    unit_id=unit_id,
                    detay=(
                        "K-128: mevzuat/güvenlik birimi "
                        f"{_DOGRULANAMADI_STATUSU!r} statüsüyle raporlandı"
                    ),
                )
            )
    return CheckOutput(bulgular=tuple(bulgular), uygulanmayan_kararlar=tuple(kayitlar))


def _kabul_edilen_etiketler(inputs: EngineInputs) -> set[str]:
    r"""Bu koşuda GEÇERLİ sayılan KÖR KAYNAK ETİKETLERİ (`KAYNAK-<n>`).

    İki ayrı kırık aynı yerde birleşiyordu ve ikisi de ÖLÇÜLDÜ (checkpoint 9):

    **(F2) Serbest metinden yapı çıkarma.** İlk yazım `KAYNAK-\d+` desenini
    `kanit` metninin HERHANGİ bir yerinde arıyordu; uydurma kimlik (`KAYNAK-99`),
    elenmiş kaynak ve *"KAYNAK-1 desteklemiyor"* gibi OLUMSUZ cümle yapısal
    çoğunluğu geçiriyordu. Serbest düzyazıdan *"bu referans olumlu"* çıkarmak
    bypass ile yanlış-pozitif arasında salınan bir sınıftır; bu yüzden kural
    POZİTİF ve KAPALI bir kontrattır — `kanit` virgülle ayrılır ve bir parça
    ancak etiketin TA KENDİSİYSE sayılır. Bu, `synthesis.dogrulanmis_referanslar`
    doktrininin ("alt dizge değil TAM eşleşme") aynısıdır; ikinci bir ölçüt YOK.

    **(F8) Ad uzayı çakışması.** İkinci yazım `DoctorReport.kaynak_adi` (GERÇEK
    kaynak adı) ile denetçinin gördüğü KÖR etiketi karşılaştırıyordu. Bunlar ayrı
    ad uzaylarıdır: `build_packet` kimliği pakete YAZMAZ, kör etiketi KONUMDAN
    türetir (`EK-B — KAYNAK-1` …). Fixture'da adlar tesadüfen `KAYNAK-1`/`KAYNAK-2`
    olduğu için kırık görünmüyordu; gerçek adlarla (`kuyumculuk.md` gibi) hiçbir
    referans eşleşmez ve HER yeni öğe reddedilirdi. Eşleme artık konumdan türer —
    bu bir varsayım DEĞİL, sistemin kendi sözleşmesidir: `build_packet` her `i`
    için `doctor_reports[i].icerik_ozeti == canonical_sha(sources[i])` eşitliğini
    FAIL-CLOSED zorlar, yani sıra kayarsa paket hiç kurulmaz.

    **Kapanmayan ayak — dürüst etiket (İlke 3).** `EngineInputs` bir paket/koşu
    bağı TAŞIMAZ (R5 alan kümesi KAPALI): başka bir koşunun mekanik kapısı bu
    koşuya verilirse motor bunu göremez. F1'in görüntü bağına denk gelen bağ
    burada YOKTUR ve kurulması arayüz eki revizyonu ister. Açık borç olarak
    TASK.md'ye yazılır; bu katmanda kapatılamaz.
    """
    gecerli, _elenen, _tekrar, _ozetsiz = kimlik_bolumlemesi(
        inputs.mekanik_eleme.raporlar
    )
    gecerli_adlar = set(gecerli)
    return {
        KAYNAK_ETIKETI.format(sira + 1)
        for sira, rapor in enumerate(inputs.mekanik_eleme.raporlar)
        if rapor.kaynak_adi in gecerli_adlar
    }


_SATIR_ATIF_RE = re.compile(r"^D\d+#\d+$")
"""Denetçi satır atfının BİÇİMİ (`D1#7`) — sözleşmenin kendi yazımı."""


_URL_BILESENI_RE = re.compile(r"^https?://[^\s/?#]+(?:[/?#][^\s]*)?$")
"""URL bileşeninin TAM biçimi: şema + boş olmayan konak + boşluksuz kalan."""


def _bilesen_kabul_edilir(parca: str, kabul_edilen_etiketler: set[str]) -> bool:
    """Bileşen KAPALI dilbilgisinin üç biçiminden biri mi?

    Üç biçim SENTEZ SÖZLEŞMESİNİN KENDİ LİSTESİDİR (`hakem-sentez-gorevi.md`
    ADIM 4: *"kanit: <standart format: 'D1#<satır no>' / 'D2#<satır no>' /
    'KAYNAK-N' / URL>"*): (1) bu koşuda geçerli kör etiket, (2) URL, (3) denetçi
    satır atfı. Başka her şey — tek kelime dâhil — dilbilgisi DIŞIDIR.

    **URL kolu TAM doğrulanır (dördüncü kapanış turu, yüksek — ÖLÇÜLDÜ).** İlk
    yazım *"`://` içeriyor ve ASCII boşluk yok"* diyordu; bu kol düzyazıyı GERİ
    ALIYORDU: `https://ornek.example\nDESTEKLEMIYOR` bileşeni geçiyor ve komşu
    çıplak etiketler sayılıyordu (ölçüldü: iki kaynak). Sekme, satır sonu, geçersiz
    şema (`javascript://x`) ve konağı olmayan `://` de geçiyordu. Kural artık
    biçimin tamamını arar ve HER TÜR boşluk karakterini reddeder.

    **Ölçülmüş kapsam sınırı (dürüst etiket, İlke 3).** Baştaki boşluk kontrolü
    savunma derinliğidir: onu SÖKEN mutasyon hiçbir testi kırmızılaştırmadı,
    çünkü URL biçimi zaten boşluk taşıyamaz ve etiket/satır-atfı biçimleri de
    boşluksuzdur. Yani bugün TEK BAŞINA erişilebilir bir dal DEĞİLDİR ve "kendi
    testi var" diye okunmaz; kodda durmasının sebebi biçim kuralı ileride
    gevşetilirse kolun tek başına açılmamasıdır. Emsal:
    `auditors.check_snapshot_agreement`'in dördüncü koşulu aynı biçimde
    etiketlidir.
    """
    if any(ch.isspace() for ch in parca):
        return False
    if parca in kabul_edilen_etiketler:
        return True
    if _URL_BILESENI_RE.match(parca):
        return True
    return bool(_SATIR_ATIF_RE.match(parca))


def sayilan_kaynaklar(kanit: Any, kabul_edilen_etiketler: set[str]) -> set[str]:
    """`kanit` metninin SAYILAN kaynak etiketleri — TEK kanonik ayrıştırıcı.

    **Alan BÜTÜN olarak doğrulanır, bileşen bileşen SÜZÜLMEZ.** Üçüncü kapanış
    turu (checkpoint 9) bunun neden gerektiğini ölçtü: bileşen bazlı süzme, bir
    bileşendeki olumsuz düzyazının KOMŞU bileşenlerdeki çıplak etiketleri
    kurtarmasına izin veriyordu — *"Bu kaynaklar iddiayı desteklemiyor: KAYNAK-1,
    KAYNAK-2, KAYNAK-3"* iki kaynak sayılıyor ve yapısal çoğunluğu geçiriyordu.

    Aynı eksen üç turda üç varyant doğurdu (metnin herhangi bir yerinde desen →
    bileşen içinde sarmalanmış etiket → komşu bileşene taşan düzyazı). Varyant
    yamamak yerine EKSEN kapatıldı: `kanit` alanı **kapalı bir dilbilgisidir** —
    virgülle ayrılmış her bileşen ya geçerli bir kör etiket, ya bir URL, ya da bir
    denetçi satır atfıdır. Dilbilgisi dışında TEK bir bileşen bile varsa alan
    yapısal kanıt TAŞIMAZ ve hiçbir kaynak sayılmaz (fail-closed: karar
    uygulanmaz, kalıp korunur).

    **Neden olumsuzlama ARANMAZ.** *"Bu referans olumlu mu"* sorusunu serbest
    düzyazıdan yanıtlamak bypass ile yanlış-pozitif arasında salınan bir sınıftır;
    olumsuzlama listesi her turda yeni bir cümle biçimiyle aşılır. Kural bu yüzden
    yapısaldır: düzyazı ZATEN dilbilgisi dışıdır, ne dediğine bakılmaz.

    **Kabul edilen bedel, dürüst etiket:** meşru ama karışık yazılmış bir kanıt
    alanı (etiketlerin yanında serbest not) da reddedilir. Yön bilinçlidir —
    reddedilen karar uygulanmaz, kalıp korunur; sessizce kabul edilen desteksiz
    bir ekleme ise pakete girerdi. Kalıcı çözüm serbest metni tipli bir destek
    alanına çevirmektir ve o, arayüz eki revizyonudur (açık borç).
    """
    if not isinstance(kanit, str) or not kanit.strip():
        return set()
    # Bileşenler KAYIPSIZ ayrılır: boş bileşen (çift virgül, baştaki/sondaki
    # virgül) SESSİZCE DÜŞÜRÜLMEZ, alanı düşürür. Düşürülseydi biçimi bozuk bir
    # alan "temiz" görünürdü — dilbilgisinin kendisi de bir kapıdır.
    parcalar = [parca.strip() for parca in kanit.split(",")]
    if any(parca == "" for parca in parcalar):
        return set()
    if not all(_bilesen_kabul_edilir(p, kabul_edilen_etiketler) for p in parcalar):
        return set()
    return {parca for parca in parcalar if parca in kabul_edilen_etiketler}


def _yeni_oge_cogunlugu(inputs: EngineInputs) -> CheckOutput:
    kabul_edilen = _kabul_edilen_etiketler(inputs)
    kayitlar: list[UygulanmayanKarar] = []
    for satir in _karar_satirlari(inputs):
        if satir.get("karar") != "ekle":
            continue
        kanit = satir.get("kanit") or ""
        kaynaklar = sayilan_kaynaklar(kanit, kabul_edilen)
        if len(kaynaklar) >= KAYNAK_TABANI_YENI_OGE:
            continue
        # K-126 TEK-KAYNAK İSTİSNASI BU KATMANDA İŞLEMEZ — ve bu, fail-closed
        # bir karardır (F3, checkpoint 9, yüksek).
        #
        # Sözleşme istisnayı İKİ koşulun BİRLİKTE sağlanmasına bağlar: (1) kaynak
        # resmî/birincil (K-123 ölçütü) VE (2) en az bir denetçinin canlı URL
        # doğrulaması. (2) tipli girdide ölçülebilir; (1) ölçülemez — `EngineInputs`
        # alan kümesi KAPALIDIR (R5) ve resmîlik yargısı denetçi katmanında yaşar.
        # İlk yazım yalnız (2)'yi arayıp istisnayı AÇIYORDU: bir AND koşulunun tek
        # ayağını zorlamak, istisnayı canlı herhangi bir kaynağa açmak demektir.
        # Alan adı ("resmi.example") resmîlik KANITI değildir.
        #
        # Bu yüzden tekil iddia burada istisnadan yararlanmaz: kalıp pakete
        # girmez, gerekiyorsa açık soruya düşer (sentez görevi 142-147).
        # EV: istisnanın işleyebilmesi K-123'ün TİPLİ taşınmasını ister — bu,
        # arayüz eki revizyonu (R5 alan kümesi) + denetçi sözleşmesi işidir ve
        # Task 12'nin kapsamı DIŞINDADIR. Açık borç olarak TASK.md'ye yazılır.
        kayitlar.append(
            UygulanmayanKarar(
                unit_id=satir["unit_id"], karar="ekle", sebep="cogunluk-yok"
            )
        )
    return CheckOutput(uygulanmayan_kararlar=tuple(kayitlar))


def _bayrak_tuketimi(inputs: EngineInputs) -> CheckOutput:
    bulgular: list[BulguIzi] = []
    for satir in _karar_satirlari(inputs):
        metin = " ".join(
            str(satir.get(alan) or "") for alan in ("kanit", "gerekce")
        )
        tukenmeyen = sorted(_bayraklar(metin) - {SAG_CIKAN_BAYRAK})
        if not tukenmeyen:
            continue
        bulgular.append(
            BulguIzi(
                sinif="acik_soru",
                unit_id=satir["unit_id"],
                detay=(
                    f"sentezden sağ çıkmaması gereken bayrak motora ulaştı: "
                    f"{tukenmeyen} — kalan yedi bayrak sentezde TÜKETİLİR"
                ),
            )
        )
    return CheckOutput(bulgular=tuple(bulgular))


def _geri_ekleme_celiskisi(inputs: EngineInputs) -> CheckOutput:
    # Tespit kalıp METNİNE dayanır (sentez sözleşmesi) — metni değişmiş kalıbın
    # kaçabileceği KABUL EDİLMİŞ zayıflıktır; kapatıcısı K-84'tür.
    cikarilanlar = {
        _katla(_metin(kayit.get("deger"))).strip()
        for kayit in inputs.son_turlarin_cikarmalari
        if kayit.get("deger") is not None
    }
    bulgular: list[BulguIzi] = []
    for satir in _karar_satirlari(inputs):
        if satir.get("karar") != "ekle":
            continue
        if _katla(_satir_metni(inputs, satir)).strip() not in cikarilanlar:
            continue
        bulgular.append(
            BulguIzi(
                sinif="acik_soru",
                unit_id=satir["unit_id"],
                detay=(
                    "geri-ekleme önerisi: aday, son turların çıkarılanlar listesiyle "
                    "eşleşiyor — eski gerekçe ile yeni kanıt yan yana konur, çelişki "
                    "AÇIK SORUdur"
                ),
            )
        )
    return CheckOutput(bulgular=tuple(bulgular))


def _kategori_cakismasi(inputs: EngineInputs) -> CheckOutput:
    """K-03'ün ÖLÇÜLEBİLEN ayağı — ve ölçülemeyenin DÜRÜST adı.

    K-03 *"paket tür etiketi ile SİSTEM KATEGORİSİ çeliştiğinde paket türü
    üstündür"* der (spec §11.2, spec girdisi satır 1189 tablosu). Sistem
    kategorisi `EngineInputs`'ta YOKTUR: `takvim_anahtarlari` yalnız anahtar
    taşır, kategori taşımaz (R5 alan kümesi KAPALI).

    İlk yazım bu boşluğu aktif paketin ÖNCEKİ tür etiketiyle karşılaştırarak
    doldurmuş ve çıktıyı `kategori_cakismalari` diye adlandırmıştı — ölçtüğü şey
    ile adı ÖRTÜŞMÜYORDU (checkpoint 9, orta): sıradan bir tür revizyonu
    "kategori çatışması" gibi görünüyor, gerçek kategori çatışması ise hiç
    görünmüyordu. Ad artık ölçtüğü şeydir; K-03'ün kategori ayağı bu katmanda
    UYGULANMAMIŞTIR ve uygulanabilmesi arayüz eki revizyonu ister (anahtar →
    kategori eşlemesi). Açık borç olarak TASK.md'ye yazılır.
    """
    aday = _aday_icerik(inputs).get("ozel_gun") or {}
    onceki = _aktif_ozel_gunler(inputs)
    degisiklikler = []
    for anahtar in sorted(aday):
        yeni_tur = (aday.get(anahtar) or {}).get("tur")
        onceki_tur = (onceki.get(anahtar) or {}).get("tur")
        if onceki_tur is None or yeni_tur is None or onceki_tur == yeni_tur:
            continue
        degisiklikler.append(
            {"anahtar": anahtar, "paket_turu": yeni_tur, "onceki_tur": onceki_tur}
        )
    return CheckOutput(
        olcumler={"paket_turu_degisiklikleri": tuple(degisiklikler)}
    )


def _ozel_gun_anahtari(inputs: EngineInputs) -> CheckOutput:
    aday = _aday_icerik(inputs).get("ozel_gun") or {}
    notlar = []
    for anahtar in sorted(aday):
        if anahtar in inputs.takvim_anahtarlari:
            continue
        notlar.append(
            {
                "tur": "not",
                "sinif": "eslesmeyen-ozel-gun",
                "alan": "ozel_gun",
                "gerekce": (
                    f"özel gün anahtarı {anahtar!r} sistem takviminde YOK — karşılıksız "
                    "dönem pakete giremez; uydurma anahtar ÜRETİLMEZ"
                ),
            }
        )
    return CheckOutput(notlar=tuple(notlar))


def _diff_sayilari(inputs: EngineInputs) -> CheckOutput:
    # K-24: motor her koşuda HAM dağılımı yazar. Değer ÜRETMEZ — kalibrasyon
    # bu kayıtları okumaktır.
    sayim = {karar: 0 for karar in sorted(identity.KARAR_DEGERLERI)}
    sayim["not"] = 0
    for satir in _gunluk(inputs):
        if satir.get("tur") == "not":
            sayim["not"] += 1
            continue
        karar = satir.get("karar")
        if karar in sayim:
            sayim[karar] += 1
    return CheckOutput(olcumler={"diff": sayim})


def _regresyon_kapisi(inputs: EngineInputs) -> CheckOutput:
    if inputs.otomatik_kapilar.katman1_passed:
        return CheckOutput()
    return CheckOutput(
        bulgular=(
            BulguIzi(
                sinif="regresyon_kapisi",
                unit_id=None,
                detay=(
                    "Katman-1 prompt regresyonu GEÇMEDİ — spec §9.1: regresyon açık "
                    "karar değil ZORUNLU kapıdır"
                ),
            ),
        )
    )


def _tek_aktif_on_kontrolu(inputs: EngineInputs) -> CheckOutput:
    if not inputs.otomatik_kapilar.tek_aktif_ihlali:
        return CheckOutput()
    return CheckOutput(
        bulgular=(
            BulguIzi(
                sinif="ikinci_aktif",
                unit_id=None,
                detay="tek-aktif ön kontrolü ihlal edildi — sektörde ikinci aktif paket",
            ),
        )
    )


CHECKS: tuple[EngineCheck, ...] = (
    EngineCheck(
        ad="sema_ve_boyut",
        aciklama="Aday içerik yazım kapısını geçer; boyut ÖLÇÜLÜR, kapı değildir.",
        calistir=_sema_ve_boyut,
    ),
    EngineCheck(
        ad="karar_kapsami",
        aciklama="Aktif paketin HER birimi için tam bir sonuç (K-84/K-107).",
        calistir=_karar_kapsami,
    ),
    EngineCheck(
        ad="kimlik_benzersizligi",
        aciklama="`ekle` yeni kimlik alır; `yerine_gecer` aktif kimliğe bağlanır.",
        calistir=_kimlik_benzersizligi,
    ),
    EngineCheck(
        ad="kanit",
        aciklama="`guncelle`/`cikar` doğrulanmış referans taşır (spec girdisi 1189).",
        calistir=_kanit,
    ),
    EngineCheck(
        ad="mutabakat",
        aciklama="K-125 iki denetçi uyumu; mevzuat kolu bulgu üretir (K-128 pasif).",
        calistir=_mutabakat,
    ),
    EngineCheck(
        ad="yeni_oge_cogunlugu",
        aciklama="Yeni öğe `2-3` yapısal çoğunluğu; K-126 istisnası dar ve kapalı.",
        calistir=_yeni_oge_cogunlugu,
    ),
    EngineCheck(
        ad="bayrak_tuketimi",
        aciklama="Sağ çıkan tek bayrak `kanal-bagimli`; kalan yedi tüketilmiş olmalı.",
        calistir=_bayrak_tuketimi,
    ),
    EngineCheck(
        ad="geri_ekleme_celiskisi",
        aciklama="Çıkarılanlar listesiyle eşleşen aday AÇIK SORUdur (K-122).",
        calistir=_geri_ekleme_celiskisi,
    ),
    EngineCheck(
        ad="kategori_cakismasi",
        aciklama="K-03: paket tür etiketi değişimi kaydedilir; kategori ayağı girdide YOK.",
        calistir=_kategori_cakismasi,
    ),
    EngineCheck(
        ad="ozel_gun_anahtari",
        aciklama="Takvimde karşılığı olmayan anahtar NOT üretir, pakete girmez.",
        calistir=_ozel_gun_anahtari,
    ),
    EngineCheck(
        ad="diff_sayilari",
        aciklama="K-24 ham dağılımı; bariyer paydasının ve engine_diff'in girdisi.",
        calistir=_diff_sayilari,
    ),
    EngineCheck(
        ad="regresyon_kapisi",
        aciklama="Katman-1 geçmemişse bulgu; `decide` onu eligible YAPAMAZ.",
        calistir=_regresyon_kapisi,
    ),
    EngineCheck(
        ad="tek_aktif_on_kontrolu",
        aciklama="Sektörde ikinci aktif paket varsa bulgu üretilir.",
        calistir=_tek_aktif_on_kontrolu,
    ),
)
"""§9.2 kümesinin KODDA SABİTLENMİŞ hâli — sıra planın bağladığı sıradır.

Kontrol eklemek ya da çıkarmak sözleşme revizyonudur (K-89 emsali): kümenin
kendisi `test_checks_set_matches_the_binding_list` ile pinlidir.
"""


def run_checks(inputs: EngineInputs) -> CheckOutcome:
    """§9.2 kontrollerini SIRAYLA koşar ve dört ölçüm kanalını birleştirir.

    SAF fonksiyondur: veritabanına dokunmaz, girdisini değiştirmez, koşu sonucu
    ÜRETMEZ. Mutasyon testine açık kalması bilinçlidir — her kontrol tek tek
    devre dışı bırakılıp ilgili testin gerçekten kırıldığı ölçülür.
    """
    if inputs.mekanik_eleme.dur:
        raise EngineInputError(
            "mekanik eleme koşuyu DURDURDU (K-127 kaynak tabanı) — motor koşmaz: "
            f"{inputs.mekanik_eleme.bildirim}"
        )

    bulgular: list[BulguIzi] = []
    kayitlar: list[UygulanmayanKarar] = []
    notlar: list[Mapping] = []
    olcumler: dict[str, Any] = {}

    for kontrol in CHECKS:
        cikti = kontrol.calistir(inputs)
        bulgular.extend(cikti.bulgular)
        kayitlar.extend(cikti.uygulanmayan_kararlar)
        notlar.extend(cikti.notlar)
        for anahtar, deger in (cikti.olcumler or {}).items():
            if anahtar in olcumler:
                raise EngineInputError(
                    f"iki kontrol aynı ölçüm anahtarını yazıyor: {anahtar!r} — "
                    "ölçümün TEK sahibi olur"
                )
            olcumler[anahtar] = deger

    return CheckOutcome(
        bulgular=tuple(bulgular),
        uygulanmayan_kararlar=tuple(kayitlar),
        notlar=tuple(notlar),
        olcumler=olcumler,
    )


# ─── Sonuç katmanı (Plan 2 Task 13) ─────────────────────────────────────────
#
# **Bulguyu SONUCA çeviren tek yer burasıdır** (arayüz eki R7). `run_checks`
# ölçer; `decide` uygular. "Kanıt yoksa karar uygulanmaz, kalıp korunur" cümlesi
# bir UYGULAMA semantiğidir ve karşılığı bu katmandadır.

ENGINE_VERSION: str = "2.13.0"
"""Motor sözleşmesinin sürümü (K-97) — `decide` her üç sonuçta da damgalar.

Sözleşme değişince ARTAR: dönüşüm tablosu, bariyer mekanizması ya da uygulama
kuralı değiştiğinde eski koşuların sonucu yenisiyle karşılaştırılamaz.
"""

ETKI_BLOKLAR = "bloklar"
ETKI_BAYRAGA_BAGLI = "bayraga-bagli-bloklar"
ETKI_AKTIVASYONU_ENGELLER = "aktivasyonu-engeller"

SEBEP_BARIYER = "bariyer-asildi"
SEBEP_ILK_KOSU = "ilk-kosuda-degisiklik-yok-gecersiz"
SEBEP_UYGULANAMAZ = "uygulanan-aday-yazim-kapisini-gecmiyor"

KURAL_KIMLIKLERI: Mapping[str, str] = {
    "kanit-yok": "kanit-zorunlulugu",
    "mutabakat-yok": "K-125",
    "cogunluk-yok": "yeni-oge-cogunlugu",
}
"""K-145: uygulanmayan her kararın KURAL kimliği — `UYGULANMAMA_SEBEPLERI` ile
birebir. Sebep kapalı kümededir; eşlemenin eksik kalması `KeyError` ile
fail-closed durur, uydurma bir kimlik ÜRETİLMEZ."""


@dataclass(frozen=True)
class BulguEtkisi:
    """Bir bulgu sınıfının `decide`'daki TÜKETİCİSİ (arayüz eki R7)."""

    sinif: str
    etki: str
    sebep: str


BULGU_ETKILERI: tuple[BulguEtkisi, ...] = (
    BulguEtkisi("kapsam_ihlali", ETKI_BLOKLAR, "kapsam-ihlali"),
    BulguEtkisi("mevzuat_uyusmazligi", ETKI_BLOKLAR, "mevzuat-uyusmazligi"),
    BulguEtkisi(
        "mevzuat_dogrulanamadi", ETKI_BAYRAGA_BAGLI, "mevzuat-dogrulanamadi"
    ),
    BulguEtkisi(
        "regresyon_kapisi", ETKI_AKTIVASYONU_ENGELLER, "regresyon-kapisi-gecmedi"
    ),
    BulguEtkisi("ikinci_aktif", ETKI_BLOKLAR, "ikinci-aktif-paket"),
    BulguEtkisi("acik_soru", ETKI_BLOKLAR, "acik-soru-var"),
)
"""Bulgu → sonuç dönüşüm tablosu — `BULGU_SINIFLARI`'nın ALTISI da burada.

Yapısal kapı `test_finding_classes_all_have_a_consumer`'dır: kapalı kümeye bir
sınıf eklenip burada karşılanmazsa test düşer. Tüketicisi olmayan bulgu
sınıfı, sessizce yok sayılan bir ölçüm demektir (R7'nin kapattığı sınıf).
"""


# ─── Yol grameri (konumsal sıra numaraları BURADA çözülür) ──────────────────

_LISTE_YOLU = re.compile(r"^(?P<alan>[a-z_]+)\[(?P<sira>\d+)\]$")
_VIDEO_YOLU = re.compile(r"^video_kodlar/(?P<havuz>[a-z_]+)\[(?P<sira>\d+)\]$")
_OZEL_GUN_YOLU = re.compile(r"^ozel_gun/(?P<anahtar>[^/]+)/(?P<yuva>[a-z_]+)$")


def canonical_content_sha(content: Mapping) -> str:
    """Aday içeriğin kanonik kimliği (K-92).

    `identity.canonical_sha`'yı ÇAĞIRIR — ikinci bir hash kuralı YAZILMAZ.
    Anahtar sırası kimliği değiştirmez, LİSTE sırası değiştirir: sıra içeriğin
    parçasıdır (bir kalıp listesinin sırası okunma sırasıdır).
    """
    return identity.canonical_sha(content)


def _eslesmeyen_ozel_gunler(inputs: EngineInputs) -> tuple[str, ...]:
    """Sistem takviminde karşılığı OLMAYAN özel gün anahtarları.

    TEK kural, İKİ tüketici: `_ozel_gun_anahtari` bunu NOT'a çevirir,
    `decide` aynı kümeyi UYGULAR (anahtar pakete girmez). İkinci bir yerde
    yeniden ölçülseydi not ile uygulama sessizce ıraksardı; not satırının düz
    yazısından anahtar ÇIKARILMAZ.
    """
    aday = _aday_icerik(inputs).get("ozel_gun") or {}
    return tuple(
        anahtar for anahtar in sorted(aday) if anahtar not in inputs.takvim_anahtarlari
    )


def _yasayan_satirlar(inputs: EngineInputs) -> dict[str, dict]:
    """Aday günlüğün YAŞAYAN karar satırları: aday yolu → satır."""
    return {
        satir["oge_yolu"]: satir
        for satir in _karar_satirlari(inputs)
        if satir.get("karar") in identity.YASAYAN_KARARLAR
    }


def _eylem(
    satir: Mapping | None,
    reddedilen: Mapping[str, UygulanmayanKarar],
    aktif: Mapping[str, Mapping],
) -> tuple[str, Any]:
    """Bir aday öğesine ne olacak: `tut` · `sil` · `geri_al`.

    `geri_al` YALNIZ aktif pakette karşılığı olan birimde mümkündür; olmayan
    birimde karar `tut`'tur — çünkü geri alınacak bir kalıp YOKTUR. O durum
    zaten `kapsam_ihlali` bulgusudur ve koşuyu bloklar; burada sessizce
    uydurma bir değer üretilmez.
    """
    if satir is None:
        return ("tut", None)
    kayit = reddedilen.get(satir["unit_id"])
    if kayit is None:
        return ("tut", None)
    if kayit.karar == "ekle":
        return ("sil", None)
    birim = aktif.get(satir["unit_id"])
    if birim is None:
        return ("tut", None)
    return ("geri_al", birim["deger"])


def _geri_konanlar(
    reddedilen: Mapping[str, UygulanmayanKarar], aktif: Mapping[str, Mapping]
) -> dict[str, list[tuple[str, str, Any]]]:
    """Uygulanmayan `cikar` kararları: alan → (aktif yol, unit_id, değer).

    Öğe adayda YOKTUR (sentez onu çıkarmıştır); kalıbın korunması onu GERİ
    KOYMAK demektir.
    """
    yerlestirme: dict[str, list[tuple[str, str, Any]]] = {}
    for unit_id, kayit in reddedilen.items():
        if kayit.karar != "cikar":
            continue
        birim = aktif.get(unit_id)
        if birim is None:
            continue
        yerlestirme.setdefault(birim["alan"], []).append(
            (birim["oge_yolu"], unit_id, birim["deger"])
        )
    return yerlestirme


def _liste_kur(
    aday_liste: list,
    yol_kurucu: Callable[[int], str],
    satirlar: Mapping[str, Mapping],
    reddedilen: Mapping[str, UygulanmayanKarar],
    aktif: Mapping[str, Mapping],
    geri: list[tuple[str, str, Any]],
) -> tuple[list, dict[str, str], list[str]]:
    """Bir listeyi yeniden kurar ve KİMLİK → YENİ YOL eşlemesini üretir.

    Sıra numarası KONUMSALDIR: reddedilen bir ekleme listeyi kaydırır. Bu
    yüzden yollar üretimin KENDİSİNDE toplanır — sonradan değere bakarak
    eşlenseydi aynı listede iki kez geçen bir metin ayırt edilemezdi.
    """
    kurulan: list[tuple[str | None, Any]] = []
    silinen: list[str] = []
    for sira, deger in enumerate(aday_liste):
        satir = satirlar.get(yol_kurucu(sira))
        eylem, yeni_deger = _eylem(satir, reddedilen, aktif)
        if eylem == "sil":
            silinen.append(satir["unit_id"])  # type: ignore[index]
            continue
        kurulan.append(
            (
                satir["unit_id"] if satir is not None else None,
                yeni_deger if eylem == "geri_al" else deger,
            )
        )
    for aktif_yol, unit_id, deger in sorted(geri):
        eslesme = _LISTE_YOLU.match(aktif_yol) or _VIDEO_YOLU.match(aktif_yol)
        konum = int(eslesme.group("sira")) if eslesme else len(kurulan)
        kurulan.insert(min(konum, len(kurulan)), (unit_id, deger))
    yollar = {
        unit_id: yol_kurucu(sira)
        for sira, (unit_id, _) in enumerate(kurulan)
        if unit_id is not None
    }
    return [deger for _, deger in kurulan], yollar, silinen


def _nihai_icerik(
    inputs: EngineInputs,
    reddedilen: Mapping[str, UygulanmayanKarar],
    dusen_anahtarlar: tuple[str, ...],
) -> tuple[dict, dict[str, str], dict[str, tuple[str, ...]]]:
    """Motorun UYGULADIĞI içerik + kimlik→yol eşlemesi + DÜŞEN kimlikler.

    Düşen kimlikler İKİ AYRI kümedir ve karıştırılmaları sonucu bozar:
    `reddedilen_ekleme` hiç pakete girmemiş bir aday kalıptır (paket
    DEĞİŞMEMİŞTİR), `eslesmeyen_takvim` ise pakette olan bir dönemin
    düşmesidir (paket DEĞİŞMİŞTİR). K-91 ilkini değişiklik saysaydı, tek bir
    reddedilen ekleme ilk koşuyu "değişiklik oldu" gösterirdi.

    Aday içerik YERİNDE DEĞİŞTİRİLMEZ (K-96): sentezin raporu olduğu gibi
    kalır, motor kendi kopyasını kurar.
    """
    aday = _aday_icerik(inputs)
    aktif = inputs.aktif_birimler
    satirlar = _yasayan_satirlar(inputs)
    geri = _geri_konanlar(reddedilen, aktif)
    nihai = json.loads(json.dumps(aday, ensure_ascii=False))
    yollar: dict[str, str] = {}
    dusenler: list[str] = []
    takvim_dusenleri: list[str] = []

    for alan in TEXT_FIELDS:
        if alan not in nihai:
            continue
        satir = satirlar.get(alan)
        eylem, deger = _eylem(satir, reddedilen, aktif)
        if eylem == "sil":
            dusenler.append(satir["unit_id"])  # type: ignore[index]
            nihai.pop(alan)
            continue
        if eylem == "geri_al":
            nihai[alan] = deger
        if satir is not None:
            yollar[satir["unit_id"]] = alan
    for alan in TEXT_FIELDS:
        for aktif_yol, unit_id, deger in geri.get(alan, []):
            nihai[aktif_yol] = deger
            yollar[unit_id] = aktif_yol

    for alan in LIST_FIELDS:
        if not isinstance(nihai.get(alan), list):
            continue
        nihai[alan], alan_yollari, silinen = _liste_kur(
            aday[alan],
            lambda sira, _alan=alan: f"{_alan}[{sira}]",
            satirlar,
            reddedilen,
            aktif,
            geri.get(alan, []),
        )
        yollar.update(alan_yollari)
        dusenler.extend(silinen)

    video = nihai.get("video_kodlar")
    if isinstance(video, dict):
        havuz_geri: dict[str, list] = {}
        for aktif_yol, unit_id, deger in geri.get("video_kodlar", []):
            eslesme = _VIDEO_YOLU.match(aktif_yol)
            if eslesme is not None:
                havuz_geri.setdefault(eslesme.group("havuz"), []).append(
                    (aktif_yol, unit_id, deger)
                )
        for havuz in VIDEO_POOL_KEYS:
            if not isinstance(video.get(havuz), list):
                continue
            video[havuz], havuz_yollari, silinen = _liste_kur(
                aday["video_kodlar"][havuz],
                lambda sira, _h=havuz: f"video_kodlar/{_h}[{sira}]",
                satirlar,
                reddedilen,
                aktif,
                havuz_geri.get(havuz, []),
            )
            yollar.update(havuz_yollari)
            dusenler.extend(silinen)

    ozel_gun = nihai.get("ozel_gun")
    if isinstance(ozel_gun, dict):
        for anahtar in dusen_anahtarlar:
            ozel_gun.pop(anahtar, None)
        for anahtar in sorted(ozel_gun):
            for yuva in SPECIAL_DAY_SLOTS:
                if yuva not in ozel_gun[anahtar]:
                    continue
                yol = f"ozel_gun/{anahtar}/{yuva}"
                satir = satirlar.get(yol)
                eylem, deger = _eylem(satir, reddedilen, aktif)
                if eylem == "sil":
                    dusenler.append(satir["unit_id"])  # type: ignore[index]
                    ozel_gun[anahtar].pop(yuva)
                    continue
                if eylem == "geri_al":
                    ozel_gun[anahtar][yuva] = deger
                if satir is not None:
                    yollar[satir["unit_id"]] = yol
        for aktif_yol, unit_id, deger in geri.get("ozel_gun", []):
            eslesme = _OZEL_GUN_YOLU.match(aktif_yol)
            if eslesme is None or eslesme.group("anahtar") in dusen_anahtarlar:
                continue
            hedef = ozel_gun.setdefault(eslesme.group("anahtar"), {})
            hedef[eslesme.group("yuva")] = deger
            yollar[unit_id] = aktif_yol

    # Düşen anahtarın birimleri de nihai içerikte YOKTUR; günlükten çıkarlar.
    for unit_id, yol in list(yollar.items()):
        eslesme = _OZEL_GUN_YOLU.match(yol)
        if eslesme is not None and eslesme.group("anahtar") in dusen_anahtarlar:
            yollar.pop(unit_id)
            takvim_dusenleri.append(unit_id)
    for yol, satir in satirlar.items():
        eslesme = _OZEL_GUN_YOLU.match(yol)
        if (
            eslesme is not None
            and eslesme.group("anahtar") in dusen_anahtarlar
            and satir["unit_id"] not in takvim_dusenleri
        ):
            takvim_dusenleri.append(satir["unit_id"])

    return (
        nihai,
        yollar,
        {
            "reddedilen_ekleme": tuple(dusenler),
            "eslesmeyen_takvim": tuple(takvim_dusenleri),
        },
    )


def _motor_satiri(
    satir: Mapping, kayit: UygulanmayanKarar, yol: str, oge_sha: str
) -> dict:
    """Kalıbı KORUYAN motor kararı — K-145 kural damgasını TAŞIR.

    `aktor='motor'` satırı kural damgası taşımak ZORUNDADIR (`identity`
    şeması); sentez satırı ise taşıyAMAZ. F19'un ayrımı budur: nihai günlük
    motorun UYGULADIĞI kararların günlüğüdür, sentezin ham önerisininki değil.
    """
    return {
        "tur": "karar",
        "alan": satir["alan"],
        "oge_yolu": yol,
        "unit_id": satir["unit_id"],
        "oge_sha": oge_sha,
        "karar": "koru",
        "gerekce": (
            f"sentezin {kayit.karar!r} kararı UYGULANMADI ({kayit.sebep}); "
            "mevcut kalıp korundu (K-23=B)"
        ),
        "kanit": "",
        "aktor": "motor",
        "kural_kimligi": KURAL_KIMLIKLERI[kayit.sebep],
        "kural_surumu": ENGINE_VERSION,
    }


def _nihai_gunluk(
    inputs: EngineInputs,
    outcome: CheckOutcome,
    reddedilen: Mapping[str, UygulanmayanKarar],
    nihai: Mapping,
    yollar: Mapping[str, str],
) -> tuple[tuple[Mapping, ...], tuple[Mapping, ...]]:
    """(nihai günlük, uygulanan karar satırları).

    Yollar ve öğe hash'leri NİHAİ içerikten yeniden hesaplanır: konumsal sıra
    numarası reddedilen bir eklemeden sonra kayar ve eski yolunu taşıyan bir
    satır başka bir öğeyi işaret ederdi.
    """
    birimler = identity.enumerate_content_units(nihai)
    satirlar: list[Mapping] = []
    uygulanan: list[Mapping] = []

    for satir in _karar_satirlari(inputs):
        unit_id = satir["unit_id"]
        kayit = reddedilen.get(unit_id)
        yol = yollar.get(unit_id)
        if yol is None:
            continue  # öğe nihai içerikte YOK (reddedilen ekleme / düşen anahtar)
        oge_sha = birimler[yol]["oge_sha"]
        if kayit is None:
            yeni = dict(satir)
            yeni["oge_yolu"] = yol
            yeni["oge_sha"] = oge_sha
            satirlar.append(yeni)
            if satir.get("karar") != "koru":
                uygulanan.append(yeni)
            continue
        satirlar.append(_motor_satiri(satir, kayit, yol, oge_sha))

    # Uygulanmayan `cikar`: aday günlükte satırı YAŞAYAN değildir (öğe çıkmış
    # sayılıyordu) — kalıp geri konduğu için `koru` satırı BURADA doğar.
    for satir in _karar_satirlari(inputs):
        unit_id = satir["unit_id"]
        kayit = reddedilen.get(unit_id)
        if kayit is None or kayit.karar != "cikar":
            continue
        yol = yollar.get(unit_id)
        if yol is None:
            continue
        satirlar.append(_motor_satiri(satir, kayit, yol, birimler[yol]["oge_sha"]))

    notlar = [
        dict(satir) for satir in _gunluk(inputs) if satir.get("tur") == "not"
    ] + [dict(satir) for satir in outcome.notlar]
    return tuple(satirlar) + tuple(notlar), tuple(uygulanan)


def _bariyerler(
    inputs: EngineInputs,
    config: PolicyConfig,
    uygulanan: tuple[Mapping, ...],
    kararsiz_sayisi: int,
) -> dict:
    """K-130/131/132 — mekanizma KURULU, eşikler varsayılan olarak PASİF.

    Eşik `None` iken bariyer hiçbir şeyi bloklamaz, yalnız oranı yazar
    (İlke 9: ölçülmemiş sayı kapı yapılmaz). İlk paket koşusunda payda 0'dır;
    oran hesaplanmaz ve YALNIZ mutlak limit uygulanabilir.
    """
    sayilar = {
        "degisim": sum(
            1 for satir in uygulanan if satir["karar"] in ("guncelle", "cikar", "kirp")
        ),
        "ekleme": sum(1 for satir in uygulanan if satir["karar"] == "ekle"),
        "kararsizlik": kararsiz_sayisi,
    }
    esikler = {
        "degisim": config.max_change_ratio,
        "ekleme": config.max_add_ratio,
        "kararsizlik": config.max_undecided_ratio,
    }
    payda = inputs.mevcut_birim_sayisi
    mutlak = dict(config.abs_limits or {})
    oranlar: dict[str, float | None] = {}
    asilan: list[str] = []
    for ad, sayi in sayilar.items():
        if payda > 0:
            oran = sayi / payda
            oranlar[ad] = oran
            esik = esikler[ad]
            if esik is not None and oran > esik:
                asilan.append(ad)
            continue
        oranlar[ad] = None
        limit = mutlak.get(ad)
        if limit is not None and sayi > limit:
            asilan.append(ad)
    return {
        "payda": payda,
        "sayilar": sayilar,
        "oranlar": oranlar,
        "esikler": esikler,
        "abs_limits": mutlak,
        "asilan": tuple(sorted(asilan)),
    }


def _acik_soru_kimlikleri(inputs: EngineInputs, bulgular) -> tuple[str, ...]:
    """Açık sorunun İZİ: birime bağlanabilen bulgunun kimliği + sentezin soruları."""
    kimlikler = [
        bulgu.unit_id
        for bulgu in bulgular
        if bulgu.sinif == "acik_soru" and bulgu.unit_id is not None
    ]
    return tuple(kimlikler) + tuple(inputs.sentez.acik_sorular)


def decide(inputs: EngineInputs, config: PolicyConfig) -> EngineResult:
    """Bulguyu SONUCA çeviren tek yer (arayüz eki R7).

    **`run_checks`'in girdi kapısı `decide` tarafından YUTULMAZ.** Bozuk şema,
    durmuş mekanik tur ya da bayat denetçi çifti `EngineInputError` fırlatır ve
    bu istisna ÇAĞIRANA gider — `blocked`'a çevrilseydi bir koşu sonucu gibi
    kaydedilir ve "motor karar verdi" görünürdü; oysa motor hiç koşmadı.

    **Motor belirsizliği yeni içeriğin lehine YORUMLAMAZ** (spec §9.3): karar
    verilemeyen madde MEVCUT kalıbı korur, `kararsizlar`'a girer ve aktivasyonu
    BLOKLAMAZ (K-23=B). Sentezin AÇIK SORUsu ayrı bir yoldur ve K-71 gereği
    bloklar.
    """
    outcome = run_checks(inputs)
    reddedilen = {kayit.unit_id: kayit for kayit in outcome.uygulanmayan_kararlar}
    dusen_anahtarlar = _eslesmeyen_ozel_gunler(inputs)

    nihai, yollar, dusen_kimlikler = _nihai_icerik(inputs, reddedilen, dusen_anahtarlar)
    takvim_dusenleri = dusen_kimlikler["eslesmeyen_takvim"]
    yazim_hatalari = structural_errors(nihai)
    if yazim_hatalari:
        nihai_icerik: Mapping | None = None
        nihai_gunluk: tuple[Mapping, ...] | None = None
        uygulanan: tuple[Mapping, ...] = ()
        content_sha: str | None = None
        decision_log_sha: str | None = None
    else:
        nihai_icerik = nihai
        nihai_gunluk, uygulanan = _nihai_gunluk(
            inputs, outcome, reddedilen, nihai, yollar
        )
        content_sha = canonical_content_sha(nihai)
        decision_log_sha = identity.canonical_sha(nihai_gunluk)

    kararsizlar = tuple(
        KararsizMadde(
            unit_id=kayit.unit_id,
            sebep=(
                f"{kayit.karar!r} kararı {kayit.sebep} sebebiyle uygulanmadı; "
                "mevcut kalıp korundu"
            ),
        )
        for kayit in outcome.uygulanmayan_kararlar
    )
    acik_sorular = _acik_soru_kimlikleri(inputs, outcome.bulgular)
    policy_report = PolicyReport(
        kararsizlar=kararsizlar,
        bulgular=outcome.bulgular,
        uygulanmayan_kararlar=outcome.uygulanmayan_kararlar,
        acik_soru_kimlikleri=acik_sorular,
    )

    barrier_report = _bariyerler(inputs, config, uygulanan, len(kararsizlar))

    gorulen = {bulgu.sinif for bulgu in outcome.bulgular}
    sebepler: list[str] = []
    aktivasyon_engeli: str | None = None
    for etki in BULGU_ETKILERI:
        if etki.sinif not in gorulen:
            continue
        if etki.etki == ETKI_BLOKLAR:
            sebepler.append(etki.sebep)
        elif etki.etki == ETKI_BAYRAGA_BAGLI:
            if config.block_on_legislation:
                sebepler.append(etki.sebep)
        else:
            aktivasyon_engeli = etki.sebep
    if acik_sorular and "acik-soru-var" not in sebepler:
        sebepler.append("acik-soru-var")
    if barrier_report["asilan"]:
        sebepler.append(SEBEP_BARIYER)

    # Reddedilen bir ekleme DEĞİŞİKLİK DEĞİLDİR: o kalıp pakete hiç girmedi.
    degisiklik_var = bool(uygulanan) or bool(takvim_dusenleri)
    if not degisiklik_var and inputs.ilk_kosu:
        sebepler.append(SEBEP_ILK_KOSU)  # K-91
    if yazim_hatalari:
        sebepler.append(SEBEP_UYGULANAMAZ)
    if aktivasyon_engeli is not None and degisiklik_var:
        sebepler.append(aktivasyon_engeli)

    if sebepler:
        sonuc = "blocked"
    elif degisiklik_var:
        sonuc = "activation_eligible"
    else:
        sonuc = "no_change"

    engine_diff = {
        "uygulanmayan_kararlar": tuple(
            {
                "unit_id": kayit.unit_id,
                "karar": kayit.karar,
                "sebep": kayit.sebep,
                "kural_kimligi": KURAL_KIMLIKLERI[kayit.sebep],
                "kural_surumu": ENGINE_VERSION,
            }
            for kayit in outcome.uygulanmayan_kararlar
        ),
        "dusen_birimler": dusen_kimlikler,
        "dusen_birim_sayisi": sum(len(k) for k in dusen_kimlikler.values()),
        "eslesmeyen_ozel_gunler": dusen_anahtarlar,
        "paket_turu_degisiklikleri": outcome.olcumler.get(
            "paket_turu_degisiklikleri", ()
        ),
        "diff": outcome.olcumler.get("diff", {}),
        "uygulanan_karar_sayisi": len(uygulanan),
        "yazim_hatalari": tuple(yazim_hatalari),
    }

    return EngineResult(
        sonuc=sonuc,
        sebep="; ".join(sebepler) if sebepler else None,
        final_candidate=nihai_icerik,
        final_decision_log=nihai_gunluk,
        engine_diff=engine_diff,
        policy_report=policy_report,
        barrier_report=barrier_report,
        content_sha=content_sha,
        decision_log_sha=decision_log_sha,
        engine_version=ENGINE_VERSION,
        engine_config_sha=config_sha(config),
    )
