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

from app.services.sector_content_schema import SPECIAL_DAY_SLOTS
from app.services.sector_pipeline import identity
from app.services.sector_pipeline.auditors import ValidatedAuditPair
from app.services.sector_pipeline.brief_doctor import RoundGate
from app.services.sector_pipeline.engine_contract import BulguIzi, UygulanmayanKarar
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

_KAYNAK_ETIKETI_RE = re.compile(r"KAYNAK-\d+")

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

ISTISNAYI_KAPATAN_BAYRAKLAR = frozenset({"yerel-degil", "eski-kaynak"})
"""Tek-kaynak istisnasını kapatan bayraklar (sentez görevi 125-126 · 193-195)."""

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
        if self.mevcut_birim_sayisi != len(self.aktif_birimler):
            raise ValueError("mevcut_birim_sayisi aktif_birimler ile tutarsız")


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
    """İki denetçinin DOĞRULANMIŞ referans kümesi — kural TEK yerde yaşar."""
    cift = inputs.denetci_envanterleri
    return dogrulanmis_referanslar(cift.birinci) | dogrulanmis_referanslar(cift.ikinci)


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
        if any(parca in referanslar for parca in parcalar):
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


def _yeni_oge_cogunlugu(inputs: EngineInputs) -> CheckOutput:
    referanslar = _referanslar(inputs)
    kayitlar: list[UygulanmayanKarar] = []
    for satir in _karar_satirlari(inputs):
        if satir.get("karar") != "ekle":
            continue
        kanit = satir.get("kanit") or ""
        kaynaklar = set(_KAYNAK_ETIKETI_RE.findall(kanit))
        if len(kaynaklar) >= KAYNAK_TABANI_YENI_OGE:
            continue
        # K-126 tek-kaynak istisnası — ölçülebilen ayak: canlı URL doğrulaması.
        # İstisnayı kapatan bayrak varsa (sentez görevi 125-126 · 193-195) hiç
        # bakılmaz: bayrak ZATEN "bu iddia tekil işlenir" demektir.
        bayraklar = _bayraklar(kanit) | _bayraklar(str(satir.get("gerekce") or ""))
        istisna = (
            not (bayraklar & ISTISNAYI_KAPATAN_BAYRAKLAR)
            and kaynaklar
            and any(parca in referanslar for parca in _kanit_parcalari(kanit) if "://" in parca)
        )
        if istisna:
            continue
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
    aday = _aday_icerik(inputs).get("ozel_gun") or {}
    onceki = _aktif_ozel_gunler(inputs)
    catismalar = []
    for anahtar in sorted(aday):
        yeni = (aday.get(anahtar) or {}).get("tur")
        eski = (onceki.get(anahtar) or {}).get("tur")
        if eski is None or yeni is None or eski == yeni:
            continue
        # K-03: paket türü ÜSTÜNDÜR — çatışma kararsız dalına DÜŞMEZ, kaydedilir.
        catismalar.append(
            {"anahtar": anahtar, "paket_turu": yeni, "onceki_tur": eski}
        )
    return CheckOutput(olcumler={"kategori_cakismalari": tuple(catismalar)})


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
        aciklama="K-03: tür etiketi çatışması kaydedilir; paket türü üstündür.",
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
