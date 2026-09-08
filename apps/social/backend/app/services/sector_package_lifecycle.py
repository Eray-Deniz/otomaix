"""Sektör bilgi paketi yaşam döngüsü (plan Task 13).

`sector_packages`'tan AYRI bir modüldür ve bağımlılık TEK YÖNLÜDÜR: buradan
oraya bakılır, tersi YOKTUR. Ayrımın gerekçesi sözleşme farkıdır — erişim
katmanı çalışma zamanında ASLA üretimi bloklamaz (her hata `None` + log),
buradaki geçişler ise tam tersine **fail-closed**'dur: kanıt eksikse,
statü uyuşmuyorsa ya da sektör kilidi kaymışsa geçiş YAPILMAZ ve istisna atar.

İki sözleşme aynı dosyada yaşarsa "hata durumunda ne olmalı" sorusunun cevabı
okuyucuya göre değişir; ayrı dosyada her modülün tek bir cevabı vardır.

**Plan 2'ye TEK bağımlılık kenarı.** Sınırı Plan 2 arayüz eki bağlar
(`docs/plans/2026-08-27-sektor-bilgi-paketi-plan2-arayuz-eki.md`, satır 1494-1513 — 2026-09-08 revizyonundan sonra):
kenar TEKTİR ve yaprak bir modüle gider. İzin verilen biçim MODÜL importudur —
`from app.services.sector_pipeline import identity` — ve `sector_pipeline` altından
BAŞKA hiçbir modül import edilmez. Kenar tek yönlüdür: `identity` bu modülü import
ETMEZ ve etmeyecektir (döngü olurdu); `identity` ortak yaprak `sector_content_schema`
dışında hiçbir `app` modülünü import etmez. İkisinin de kapısı yapısal testtir
(`tests/test_plan2_interface_contract.py`, "Madde 9").

**AYAK (a) KAPANDI — ek REVİZE EDİLDİ (2026-09-08, revizyon R-A).** Eski hüküm
"kullanılan TEK ad `identity.canonical_sha`" diyordu ve bu modül gerçekte
`identity.validate_decision_log` ile `identity.check_unit_integrity` adlarını
kullanıyordu (Task 3'ün şema kapısı `insert_draft` içinde koşar; kuralın İKİNCİ BİR
KOPYASI yazılamaz). Ölçüldü: bu modül `canonical_sha`'yı HİÇ çağırmıyor — yani hüküm
dayandığı varsayım yüzünden de kodla uyumsuzdu. Revizyondan sonra bağlayan invaryant AD
SAYISI değil KENARIN kendisidir: tek import, MODÜL biçiminde, hedefi YAPRAK, başka
`sector_pipeline` modülü YOK. Kullanılabilir ad kümesi `identity`nin ÜRETİLMİŞ public
yüzeyidir; elle sayılmaz.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, fields as dataclass_fields
from typing import Any, Mapping, Protocol
from uuid import UUID

from app.services.package_events import log_package_event, require_actor as _require_actor
from app.services.sector_packages import (
    normalize_special_day_key,
    validate_package_content,
)
from app.services.sector_pipeline import identity

logger = logging.getLogger(__name__)


# ─── Sözleşme ───────────────────────────────────────────────────────────────
#
# Üç public geçiş + tek draft yazıcısı. Ortak omurga `_apply_status_transition`
# ÖZELDİR: public yüzeyden kanıtsız geçiş YOLU YOKTUR (K-28'in Plan-1 ayağı).
# Çağıranın KİMLİĞİNİN doğrulanması (K-103) bu katmanın konusu değildir —
# burada taşınan şey kanıttır, yetki değil; sınır dürüstçe budur.
#
# **Sıra sözleşmesi: olay ÖNCE, geçiş SONRA.** İkisi aynı transaction'dadır
# (F24), ama sıra keyfî DEĞİL: `log_package_event`'in "bu bir devir teslim mi"
# ölçüsü sektörde AKTİF bir satır olup olmadığına bakar ve o ölçü yalnız geçiş
# uygulanmadan önce doğrudur. Sıra tersine çevrilirse deaktivasyon sonrası
# aktivasyon yanlışlıkla devir teslim sayılır.


class LifecycleError(RuntimeError):
    """Yaşam döngüsü DURUMU istenen geçişe uygun değil (hedef yok, yanlış statü)."""


class GateNotSatisfied(RuntimeError):
    """Geçiş kapısının kanıtı sağlanmadı — geçiş YAPILMAZ."""


def _require_flag(value: Any, label: str) -> None:
    """Alan GERÇEKTEN `bool` olmalı — doğru-görünen değer kanıt değildir.

    Açıklama satırı (`activation_eligible: bool`) bir kapı DEĞİLDİR; Python
    onu zorlamaz. Doğruluk-değeriyle çalışan bir kapı `"false"` metnini DOĞRU
    sayar (boş olmayan her metin doğrudur) — yani "aktive edilemez" diye
    işaretlenmiş bir aday aktive edilebilirdi (checkpoint 13, F1: ölçüldü).
    `isinstance` YETMEZ: `bool` bir `int` alt sınıfıdır, o yüzden tam tip
    eşitliği aranır.
    """
    if type(value) is not bool:
        raise TypeError(
            f"{label} bool olmalı ({type(value).__name__} verildi) — "
            "doğru-görünen değer kanıt sayılmaz"
        )


def _require_count(value: Any, label: str) -> None:
    """Sayaç GERÇEKTEN `int` olmalı ve negatif olamaz.

    Ayna vaka: `False == 0` ve `True == 1`. Bir bool sayaç alanına düşerse
    "açık soru yok" kapısı sessizce açılırdı.
    """
    if type(value) is not int:
        raise TypeError(
            f"{label} int olmalı ({type(value).__name__} verildi) — "
            "bool bir sayaç değildir"
        )
    if value < 0:
        raise ValueError(f"{label} negatif olamaz: {value}")


# ─── Köken jetonu — ŞEKİL kapıları (Plan 2 Task 8 MODIFY) ──────────────────
#
# Arayüz eki R8(c): iki kanıt sınıfı da yalnız veritabanı destekli bir fabrikanın
# üretebileceği TEK KULLANIMLIK bir köken jetonu taşır. Bu görevde YALNIZ alanlar
# ve onların ŞEKİL kapıları doğar; jetonun TÜKETİMİ (`_consume_provenance`,
# `EvidenceProvenanceInvalid`) ve geçiş fonksiyonlarının doğrulaması Task 15'in
# kalemidir. Bölünme R9 gereğidir: jetonu BASAN (`runs.mint_evidence_token`) ve
# kanıtı KURAN (`runs.build_rollback_evidence`) iki fonksiyon da Task 8'dedir.


class EvidenceMintRefused(RuntimeError):
    """Jeton BASILAMADI — satır yok ya da jeton basmaya uygun durumda değil.

    R9: `runs.mint_evidence_token` (Task 8) bunu fırlatır, bu yüzden TANIM YERİ
    bu modül olsa da YAZAN GÖREV Task 8'dir.
    """


_HEX_KARAKTERLERI = frozenset("0123456789abcdef")


def _require_token(value: Any, label: str) -> None:
    """Jeton 64 karakterlik KÜÇÜK HARF hex `str` olmalı — boş/whitespace/`None` RED.

    `type(...) is not str`: `str` alt sınıfı da reddedilir (A4 süpürmesi #3).
    Hiçbir yerde `strip()`/`lower()` UYGULANMAZ — normalizasyon, uydurulmuş bir
    değeri geçerli görünür kılardı.
    """
    if (
        type(value) is not str
        or len(value) != 64
        or any(karakter not in _HEX_KARAKTERLERI for karakter in value)
    ):
        raise TypeError(
            f"{label} 64 karakterlik hex jeton olmalı — köken kanıtı uydurulamaz"
        )


def _require_kapsam_sha(value: Any, label: str) -> None:
    """Sha alanları 64 karakterlik küçük harf hex `str` (A4 süpürmesi #6).

    `_require_token` ile AYNI şekil kuralıdır, ayrı bir mesajla — ikinci bir
    NORMALİZASYON kuralı DEĞİLDİR. İki çağıranı vardır: kapsam mührü
    (`onay_kapsam_sha`) ve A4'ün beklenen kanonik madde kümesi imzası.
    """
    if (
        type(value) is not str
        or len(value) != 64
        or any(karakter not in _HEX_KARAKTERLERI for karakter in value)
    ):
        raise TypeError(
            f"{label} 64 karakterlik hex sha olmalı — mühür uydurulamaz"
        )


@dataclass(frozen=True)
class ActivationGateEvidence:
    """Aktivasyon kapısının mekanik kanıtı (spec §2.3, K-71).

    `expected_active_version` OPSİYONELDİR ve bu K-94'ün açık kalmasının kod
    karşılığıdır: dolu gelirse geçiş anındaki gerçek aktif sürümle eşleşmeli
    (yetenek kurulu), `None` gelirse kontrol yapılmaz. Alanın onay akışında
    ZORUNLU olup olmayacağı kararın kendisidir ve burada yazılmaz.

    Alan tipleri YAPIMDA zorlanır: geçersiz kanıt hiç var olamaz, dolayısıyla
    "kapıya geçersiz kanıtla gelme" diye bir durum da doğmaz.
    """

    activation_eligible: bool
    open_questions_count: int
    katman1_passed: bool
    checklist_approved: bool
    expected_active_version: int | None = None
    # ── Plan 2 Task 8 (arayüz eki R8(c)) — KÖKEN alanları.
    # `field(kw_only=True)` seçilmesinin sebebi ölçülmüştür: yeni alanlar
    # VARSAYILANSIZ olmalı, ama `expected_active_version` zaten varsayılanlı
    # olduğu için konumsal sırada öncelerine konamazlar. Depoda kanıt sınıflarını
    # kuran her çağrı anahtar argüman kullanıyor, yani kırılma yoktur.
    run_id: str = field(kw_only=True)  # jetonun basıldığı koşu
    provenance_token: str = field(kw_only=True)  # 64 hex, TEK KULLANIMLIK

    def __post_init__(self) -> None:
        _require_flag(self.activation_eligible, "activation_eligible")
        _require_flag(self.katman1_passed, "katman1_passed")
        _require_flag(self.checklist_approved, "checklist_approved")
        _require_count(self.open_questions_count, "open_questions_count")
        if self.expected_active_version is not None:
            _require_count(self.expected_active_version, "expected_active_version")
            if self.expected_active_version < 1:
                raise ValueError(
                    "expected_active_version 1'den küçük olamaz: "
                    f"{self.expected_active_version} (sürümler 1'den başlar)"
                )
        # A4 süpürmesi #4: `isinstance` DEĞİL `type(...) is not str` — `str` alt
        # sınıfı da RED. Boşluk kapısı AYRI kalır; karşılaştırma değildir.
        if type(self.run_id) is not str or self.run_id.strip() == "":
            raise ValueError("run_id zorunlu — kökensiz kanıt kurulamaz")
        _require_token(self.provenance_token, "provenance_token")


@dataclass(frozen=True)
class RollbackGateEvidence:
    """Rollback kapısının kanıtı — aktivasyon kanıtıyla PAYLAŞILMAZ.

    Acil rollback, ADAYIN aktivasyon kapılarından bağımsızdır: "aday yeterli
    değil" diye aktif sürümü geri alamamak, acil kolu işlevsiz bırakırdı. O
    yüzden buradaki tek insan kapısı yönetici onayıdır.
    """

    manager_approved: bool
    katman1_passed: bool
    # ── Plan 2 Task 8 (arayüz eki R8(c) + A1(c)) — KÖKEN alanları.
    incident_id: str = field(kw_only=True)  # jetonun basıldığı olay
    package_id: UUID = field(kw_only=True)  # geri alınan paket
    onay_kapsam_sha: str = field(kw_only=True)  # onaylanan ÜYELİĞİN parmak izi
    provenance_token: str = field(kw_only=True)  # 64 hex, TEK KULLANIMLIK

    def __post_init__(self) -> None:
        _require_flag(self.manager_approved, "manager_approved")
        _require_flag(self.katman1_passed, "katman1_passed")
        # A4 süpürmesi #5: `type(...) is not str` — alt sınıf da RED.
        if type(self.incident_id) is not str or self.incident_id.strip() == "":
            raise ValueError("incident_id zorunlu")
        if type(self.package_id) is not UUID:
            raise TypeError("package_id UUID olmalı")
        _require_kapsam_sha(self.onay_kapsam_sha, "onay_kapsam_sha")
        _require_token(self.provenance_token, "provenance_token")


def _require_evidence(evidence: Any, expected: type) -> None:
    """Kanıt SINIFIN KENDİSİ olmalı — ördek tiplemesi kabul edilmez.

    Aynı alan adlarını taşıyan gelişigüzel bir nesne, yapımdaki tip kapısını
    hiç görmeden kapıya ulaşırdı. İki kanıt sınıfının ayrı olması da ancak
    burada gerçek olur: aktivasyon kanıtı rollback kapısını açamaz.
    """
    if type(evidence) is not expected:
        raise GateNotSatisfied(
            f"kanıt {expected.__name__} olmalı ({type(evidence).__name__} verildi) — "
            "benzer alan taşıyan nesne kanıt yerine geçmez"
        )


# ─── Kanıt YÜKÜ ve PARMAK İZİ (Plan 2 Task 8 MODIFY — AÇIK-3 kararı) ───────
#
# Arayüz eki AÇIK-3 (B seçeneği): dört yardımcı `sector_pipeline/` altında DEĞİL,
# BU dosyada doğar. Gerekçe bağımlılık YÖNÜdür — bugüne kadar Plan 2'nin her
# modülü Plan 1'den okur, tersi yoktur; yardımcıları Plan 2'ye koymak o yönü
# tersine çevirirdi. `runs.py` (Plan 2) bu modülden ZATEN `_require_actor`'ı
# alıyor; yön değişmez, yalnız alınan ad sayısı artar.
#
# DÖNGÜSEL IMPORT — kararın ölçülmüş teknik kusuru ve çözümü: yardımcılar
# `runs.VerifiedRun`'ı IMPORT ETMEZ (o import `runs` → burası → `runs` döngüsü
# üretirdi), aşağıdaki YEREL protokole yazılır. `VerifiedRun` protokolü YAPISAL
# olarak karşılar; nominal bağ KURULMAZ.


class KilitliKosuGorunumu(Protocol):
    """`runs.VerifiedRun`'ın bu modülün GÖRDÜĞÜ yüzeyi — YEREL tip, KAPALI küme.

    Alan kümesi KAPALIDIR: SEKİZ alan, dokuzuncusu YOKTUR. Hepsi `VerifiedRun`'da
    aynı adla ve aynı tiple vardır.
    """

    run_id: str
    sector_id: UUID
    package_id: UUID | None
    durum: str
    sonuc: str
    approval_snapshot: Mapping[str, Any] | None
    katman1_attestation: Mapping[str, Any] | None
    readiness_attestation: Mapping[str, Any] | None


_KOSU_GORUNUM_ALANLARI: tuple[str, ...] = (
    "run_id",
    "sector_id",
    "package_id",
    "durum",
    "sonuc",
    "approval_snapshot",
    "katman1_attestation",
    "readiness_attestation",
)  # KAPALI — SEKİZ ad; `KilitliKosuGorunumu` ile BİREBİR


def _require_kosu_gorunumu(value: Any, label: str) -> None:
    """Ördek tiplemesi kabul edilmez ama nominal bağ da kurulamaz (döngüsel import).

    Aradaki tek dürüst kapı: SEKİZ alanın SEKİZİ de VAR mı? Biri eksikse
    `TypeError` (fail-closed) — sessizce `None` üretilmez.
    """
    eksik = [ad for ad in _KOSU_GORUNUM_ALANLARI if not hasattr(value, ad)]
    if eksik:
        raise TypeError(
            f"{label} kilitli koşu görünümü değil — eksik alanlar: {sorted(eksik)}"
        )


# ─── Kanıt alanlarının ŞEKİL kapıları (fix turu 2, F1 — yüksek) ────────────
#
# Fix turu 1 EKSİK anlık görüntüyü kapattı; bu tur değerin ŞEKLİNİ kapatır.
# Ölçülen açık: `{"acik_sorular": ""}` · `{}` · `set()` hepsi `len(...) == 0`
# veriyordu — yani "açık soru YOK" diyen ve K-71 kapısını GEÇİREN tek değer.
# Skaler şekiller (`int`/`bool`/`None`/`float`) ise alan-DIŞI bir `TypeError`
# fırlatıyordu; o da bir alan reddi değil, çağırana sızan beklenmedik hatadır.
#
# `Sized`/`Iterable`/`hasattr(..., "__len__")` tabanlı GEVŞEK bir kapı YAZILMAZ:
# `str` de `dict` de o kapıyı geçer ve açık aynen kalırdı. Kabul kümesi KAPALI
# ve NOMİNALDİR.
#
# ERİŞİLEBİLİRLİK — dürüst sınır: `approval_snapshot` kolonu 036'da şekilsiz
# `JSONB`'dir (yalnız değişmezlik tetikleyicisi var, CHECK yok) ve BUGÜN üretim
# yazıcısı YOKTUR — yazıcı Task 14'ün kalemidir. Sınıf bugün canlıda
# tetiklenemez; kapatılma sebebi, Task 14 yazıcısının bu şekli üretmesi hâlinde
# kanıtın SESSİZCE genişlemesidir. Tehdit modeli: girdi araştırma çıktısıdır —
# ÖZENSİZ/BAYAT olabilir, SALDIRGAN değildir.

_DIZI_ALAN_TIPLERI: tuple[type, ...] = (list, tuple)
"""`acik_sorular` gibi SAYILAN alanların KAPALI kabul kümesi — ikisi de gerekli.

`VerifiedRun.__post_init__` dokuz jsonb yükünü `identity.donmus`'tan geçirir ve
`donmus` kuralı (2) `list | tuple → tuple` yazar: DONMUŞ yolda değer `tuple`,
HAM yolda (sürücünün çözdüğü jsonb dizisi) `list`'tir. Biri kabul edilmezse
üretim yolu kırılır. Alt sınıflar RED — A4 disiplini `type(...) is` arar.
"""


def _dizi_alan(value: Any, label: str) -> tuple[Any, ...]:
    """Sayılacak alanın şekli: YALNIZ `list` ya da `tuple`; kalan her şey RED.

    **Boş olan MEŞRUDUR.** `[]` ve `()` "açık soru YOK" demektir ve pozitif
    kontrolü vardır; reddedilen şey boşluk değil, YANLIŞ ŞEKİLDİR.
    """
    if type(value) not in _DIZI_ALAN_TIPLERI:
        raise EvidenceMintRefused(
            f"{label} dizi DEĞİL: {type(value).__name__} — şekli doğrulanmamış "
            "bir değer sayıya çevrilmez; bozuk kanıt SIFIRA genişletilemez"
        )
    return tuple(value)


def _esleme_alan(value: Any, label: str) -> Mapping[str, Any] | None:
    """Jsonb eşleme alanının şekli: `Mapping` ya da `None`; kalan her şey RED.

    `None` MEŞRUDUR — "tasdik yok" demektir ve kapıyı KAPATIR. Reddedilen,
    eşleme olmayan bir değerin anahtarla okunmaya çalışılmasıdır: `"x" in "xy"`
    alt dize kontrolüdür, `"x" in {"x"}` küme üyeliğidir — ikisi de `in`
    kapısını geçer, ardından gelen `[...]` alan-DIŞI `TypeError` fırlatır.
    """
    if value is None or isinstance(value, Mapping):
        return value
    raise EvidenceMintRefused(
        f"{label} eşleme DEĞİL: {type(value).__name__} — şekli doğrulanmamış "
        "bir değer anahtarla okunup booleana çevrilmez"
    )


def _yuk_anahtarlari(cls: type) -> tuple[str, ...]:
    """Sınıfın jeton-DIŞI alan kümesi, alan adına göre ARTAN sırada.

    **Küme ELLE SAYILMAZ, sınıfın kendisinden ÜRETİLİR.** Arayüz eki aktivasyon
    yükünü YEDİ, geri alma yükünü BEŞ anahtar diye bağlar; geri alma bugün tam
    olarak BEŞ'tir. Aktivasyon bugün ALTI'dır ve eksik olan tek ad
    `expected_no_active`'dir — o alan Task 15'in kalemidir (arayüz eki R8(c)
    görev bölünmesi). Küme türetilmiş olduğu için Task 15 alanı eklediği anda
    yük, parmak izi ve kapı BİRLİKTE yediye çıkar; ikinci bir elle-liste
    bakımı gerekmez ve iki tarafın ayrışabileceği bir pencere açılmaz.
    """
    return tuple(
        sorted(
            alan.name
            for alan in dataclass_fields(cls)
            if alan.name != "provenance_token"
        )
    )


def activation_evidence_payload(
    kosu: KilitliKosuGorunumu,
    aktif_paket_satiri: Mapping[str, Any] | None,
    *,
    beklenen_madde_kumesi_sha: str,
) -> Mapping[str, Any]:
    """`ActivationGateEvidence`'ın jeton DIŞI alanlarını KİLİTLİ satırlardan TÜRETİR.

    İki konumsal girdinin İKİSİ de aynı işlemde `FOR UPDATE` ile kilitlenmiş
    satırlardır: `kosu` doğrulanmış koşu satırı, `aktif_paket_satiri` o sektörün
    o an AKTİF paket satırı (aktif paket yoksa `None` — K-94 ilk aktivasyon
    hâli). Çağıranın serbestçe ürettiği hiçbir değer GİRMEZ.

    **`beklenen_madde_kumesi_sha` — kanonik SABİT, çağıran girdisi DEĞİL
    (fix turu 1, F1).** A4 kapısının dördüncü koşulu kanonik madde kümesinin
    imzasını gerektirir; o sabit `sector_pipeline/readiness_items.py`'de yaşar ve
    bu modülün import kenarı (AÇIK-3) `identity` DIŞINDA hiçbir `sector_pipeline`
    modülüne açılamaz — yapısal testi de vardır. Daraltılan taraf artık kapı
    DEĞİL, taşıma biçimidir: değeri ÇAĞIRAN taşır ve tek çağıran
    (`runs.mint_evidence_token`) onu `readiness_items.MADDE_KUMESI_SHA`'dan
    okur. İstekten/dış dünyadan gelen bir değer OLAMAZ; kapısı
    `tests/test_pipeline_runs.py::
    test_runs_passes_the_canonical_madde_kumesi_sha_to_the_payload_helper`
    (AST: geçilen ifade birebir o nitelik erişimidir).

    **TEK türetici:** hem `runs.mint_evidence_token` hem
    `writeback.build_activation_evidence` (Task 15) BUNU çağırır. İki yerde iki
    türetme yazılsaydı, basılan parmak izi ile kurulan kanıtın parmak izi
    sessizce ayrışabilirdi.

    Onay anlık görüntüsü EKSİKSE `EvidenceMintRefused` — eksik kanıt sıfıra
    normalize EDİLMEZ (aşağıda gerekçesi).
    """
    _require_kosu_gorunumu(kosu, "kosu")
    _require_kapsam_sha(beklenen_madde_kumesi_sha, "beklenen_madde_kumesi_sha")

    # F1(b), fix turu 1: ÖNCEKİ yazım `approval_snapshot is None` iken
    # `open_questions_count = 0` yazıyordu. Sıfır, K-71 kapısını GEÇİREN tek
    # değerdir (`activate_package`: `open_questions_count != 0` → red) — yani
    # "kanıt yok" hâli sessizce "kanıt temiz" hâline genişliyordu. Eksik anlık
    # görüntü artık jeton BASTIRMAZ; kanıt hiç doğmaz.
    anlik = _esleme_alan(kosu.approval_snapshot, "approval_snapshot")
    if anlik is None or "acik_sorular" not in anlik:
        raise EvidenceMintRefused(
            "onay anlık görüntüsü YOK ya da 'acik_sorular' taşımıyor — eksik "
            "kanıt SIFIRA normalize edilmez; açık soru sayısı uydurulamaz"
        )
    # F1, fix turu 2: `len(...)` ÇAĞRILMADAN ÖNCE şekil kapısı. Önceki yazım
    # `""` · `{}` · `set()` · `()` için 0, skalerler için alan-DIŞI `TypeError`
    # üretiyordu; ilki K-71'i AÇAR, ikincisi alan reddi DEĞİLDİR.
    acik_sorular = _dizi_alan(anlik["acik_sorular"], "acik_sorular")
    katman1 = _esleme_alan(kosu.katman1_attestation, "katman1_attestation")

    okunan = {
        "activation_eligible": kosu.sonuc == "activation_eligible",
        "open_questions_count": len(acik_sorular),
        "katman1_passed": katman1 is not None and katman1["sonuc"] == "PASS",
        "checklist_approved": _checklist_approved(
            _esleme_alan(kosu.readiness_attestation, "readiness_attestation"),
            beklenen_madde_kumesi_sha,
        ),
        "expected_active_version": (
            aktif_paket_satiri["version"] if aktif_paket_satiri is not None else None
        ),
        "expected_no_active": aktif_paket_satiri is None,
        "run_id": kosu.run_id,
    }
    return _yuk_kes(ActivationGateEvidence, okunan)


def _checklist_approved(
    readiness_attestation: Mapping[str, Any] | None,
    beklenen_madde_kumesi_sha: str,
) -> bool:
    """A4 kapısının DÖRT koşulunun DÖRDÜ — hiçbiri başka göreve devredilmez.

    Koşullar: (1) tasdik VAR ve `onaylandi is True`; (2) `madde_kumesi_sha`
    anahtarı VAR ve değeri `type(...) is str`; (3) `strip()` sonrası BOŞ DEĞİL;
    (4) değer `beklenen_madde_kumesi_sha`'ya **BİREBİR** eşit. `strip()` yalnız
    boş-olmama kapısında kullanılır, KARŞILAŞTIRILAN değerin üzerinde DEĞİL —
    yani `" <kanonik> "` GEÇMEZ. Geriye uyum yedeği YOKTUR (fail-closed).

    **DÖRDÜNCÜ koşul fix turu 1'de BURAYA GELDİ (F1(a), yüksek).** Önceki yazım
    onu Task 15'e devrediyor ve gerekçesini "import kenarı açılamaz"a
    dayandırıyordu; ölçüldü ki devir bugün BOŞTU — devralacak kapı
    (`writeback.activate_from_snapshot`) henüz YAZILMAMIŞTIR, oysa
    `activate_package` `checklist_approved` alanına BUGÜN olduğu gibi güveniyor.
    Yani "yeri değişti" değil, kapı hiç koşmuyordu: boş olmayan HER dize
    geçiyordu. İmport kenarı (AÇIK-3) yine AÇILMADI — beklenen kanonik değer
    ÇAĞIRANDAN, yalnız-anahtar bir parametreyle taşınır. Task 15 kendi
    kapısını kurduğunda bu koşul ORTADAN KALKMAZ; iki kapı da aynı sabite bakar.

    **Girdi ÇAĞRI YERİNDE şekil kapısından geçmiştir (fix turu 2):** buraya
    yalnız `None` ya da `Mapping` gelir. İkinci bir şekil kontrolü YAZILMAZ —
    `"onaylandi" not in "…onaylandi…"` alt dize kontrolüdür ve bir `str`
    tasdiki bu kapıyı geçip aşağıdaki `[...]` okumasında alan-DIŞI `TypeError`
    fırlatırdı; o yüzden kapı burada değil, TEK yerde (`_esleme_alan`) durur.
    """
    if readiness_attestation is None:
        return False
    if "onaylandi" not in readiness_attestation:
        return False
    if readiness_attestation["onaylandi"] is not True:
        return False
    if "madde_kumesi_sha" not in readiness_attestation:
        return False
    sha = readiness_attestation["madde_kumesi_sha"]
    return (
        type(sha) is str
        and sha.strip() != ""
        and sha == beklenen_madde_kumesi_sha
    )


def rollback_evidence_payload(
    plan_satiri: Mapping[str, Any],
    hedef_kosu: KilitliKosuGorunumu,
) -> Mapping[str, Any]:
    """`RollbackGateEvidence`'ın jeton DIŞI alanlarını KİLİTLİ satırlardan TÜRETİR.

    Anahtar kümesi KAPALI ve TAM — BEŞ anahtar (A1(c)): `manager_approved` ·
    `katman1_passed` · `incident_id` · `package_id` · `onay_kapsam_sha`.
    Türetme kuralının GEREKÇESİ `runs.build_rollback_evidence`'ın gövdesindedir;
    burada YALNIZ kilitli satır alanları okunur.
    """
    _require_kosu_gorunumu(hedef_kosu, "hedef_kosu")
    hedef_katman1 = _esleme_alan(
        hedef_kosu.katman1_attestation, "katman1_attestation"
    )

    onay_actor = plan_satiri["onay_actor"]
    okunan = {
        "manager_approved": (
            type(onay_actor) is str
            and onay_actor.strip() != ""
            and plan_satiri["onaylandi_at"] is not None
            and type(plan_satiri["onay_kapsam_sha"]) is str
        ),
        # Süpürme (fix turu 2): AYNI şekilsiz okuma burada da vardı.
        "katman1_passed": (
            hedef_katman1 is not None and hedef_katman1["sonuc"] == "PASS"
        ),
        "incident_id": plan_satiri["incident_id"],
        # Sürücü `uuid.UUID`in bir ALT SINIFINI döndürür; kanıt sınıfının şekil
        # kapısı `type(...) is UUID` arar (alt sınıf kabul etmez, A4 disiplini).
        # Normalize BURADA yapılır — kapı gevşetilmez.
        "package_id": UUID(str(plan_satiri["package_id"])),
        "onay_kapsam_sha": plan_satiri["onay_kapsam_sha"],
    }
    return _yuk_kes(RollbackGateEvidence, okunan)


def _yuk_kes(cls: type, okunan: dict[str, Any]) -> Mapping[str, Any]:
    """Türetilmiş anahtar kümesini uygular — fail-closed.

    Sınıfın jeton-dışı her alanının BURADA hesaplanmış bir karşılığı olmak
    ZORUNDADIR; olmayan bir alan sessizce `None`'a düşmez, `KeyError` fırlatır.
    """
    anahtarlar = _yuk_anahtarlari(cls)
    eksik = [ad for ad in anahtarlar if ad not in okunan]
    if eksik:
        raise KeyError(
            f"{cls.__name__} yük türetmesi eksik: {sorted(eksik)} — sessizce "
            "atlanan alan, parmak izini basan ve kanıtı kuran iki tarafı ayırırdı"
        )
    return {ad: okunan[ad] for ad in anahtarlar}


def _evidence_fingerprint(evidence: Any) -> str:
    """Kanıtın kanonik parmak izi — `provenance_token` HARİÇ.

    SINIF ADI + (alan adı, değer) çiftleri, alan adına göre ARTAN sırada;
    `identity.canonical_sha` (K-92) kuralıyla hash'lenir. İkinci bir hash kuralı
    YAZILMAZ.
    """
    cls = type(evidence)
    payload = {ad: getattr(evidence, ad) for ad in _yuk_anahtarlari(cls)}
    return _evidence_fingerprint_from_payload(cls, payload)


def _evidence_fingerprint_from_payload(cls: type, payload: Mapping[str, Any]) -> str:
    """`_evidence_fingerprint`'in NESNESİZ ikizi — AYNI kanonik diziyi üretir.

    Tanım gereği `_evidence_fingerprint(e)` ≡
    `_evidence_fingerprint_from_payload(type(e), <e'nin jeton dışı alanları>)`.
    `payload` anahtar kümesi sınıfın jeton-dışı alan kümesiyle **birebir**
    olmalıdır; eksik ya da fazla anahtar `ValueError`'dır (fail-closed).
    """
    anahtarlar = _yuk_anahtarlari(cls)
    if set(payload) != set(anahtarlar):
        raise ValueError(
            f"{cls.__name__} parmak izi yükü uyuşmuyor: beklenen {list(anahtarlar)}, "
            f"verilen {sorted(payload)} — eksik ya da fazla anahtar kabul edilmez"
        )
    return identity.canonical_sha(
        [cls.__name__] + [[ad, payload[ad]] for ad in anahtarlar]
    )


# `_require_actor` TANIMI BURADA DEĞİL, `package_events.require_actor`tadır —
# davranışı DEĞİŞMEDİ (aynı `ValueError`, aynı mesaj, aynı kırpılmış dönüş) ve
# bu modüldeki adı da değişmedi. Taşımanın tek sebebi ÖLÇÜLMÜŞ bir döngüdür:
# olay kaydı dalı da aynı kapıyı kullanmak zorundaydı (Codex checkpoint, F2),
# ama bu modül `package_events`i ZATEN import ediyor — ters yönde ikinci bir
# import `ImportError` ile düşerdi. Kuralın İKİNCİ BİR KOPYASI yazılmadı:
# iki kapı iki davranış demektir (bağlayıcı ek, AÇIK-1 ayak (b)).


async def _set_status(db, package_id: UUID, status: str, *, expected: str) -> None:
    """Durumu KARŞILAŞTIR-VE-YAZ ile günceller.

    Koşulsuz `UPDATE ... WHERE id = $1` yetmiyordu (checkpoint 13, F2): iki
    transaction aynı taslağı okuyup ikisi de yazınca ikinci güncelleme
    `active → active` olarak geçiyor ve sessizce başarılı oluyordu. Beklenen
    önceki durumu koşula koymak, kaybeden tarafı AÇIKÇA düşürür.

    Ayrı bir fonksiyon olmasının ikinci sebebi: geçişin her adımı AYNI kapıdan
    geçsin ve atomiklik testi geçiş adımını gerçekten düşürebilsin.
    """
    updated = await db.fetchval(
        "UPDATE social.sector_packages SET status = $2, "
        "activated_at = CASE WHEN $2 = 'active' THEN now() ELSE activated_at END "
        "WHERE id = $1 AND status = $3 RETURNING id",
        package_id,
        status,
        expected,
    )
    if updated is None:
        raise LifecycleError(
            f"durum geçişi reddedildi: {package_id} artık {expected!r} değil — "
            "eşzamanlı bir geçiş önce davrandı"
        )


def _require_same_sector(observed: UUID, locked: UUID, package_id: UUID) -> None:
    """Kilitlenen sektör ile paketin GERÇEK sektörü aynı olmalı.

    Sektör kilitsiz okunup kilitleniyor; hedef ancak ondan SONRA kilitlenebilir.
    O pencerede paketin sektörü değişirse yanlış sektör serileştirilmiş olur:
    A'nın aktif paketi arşivlenip B'ye ait hedef aktive edilebilir ve olay A'ya
    yazılabilirdi (checkpoint 13, F4). Durum karşılaştır-ve-yaz'ı bunu GÖRMEZ,
    çünkü yalnız duruma bakar, sektöre değil.

    Bu kapı pencereyi kapatmaz — kapatılamaz, çünkü paket kilitlenmeden önce
    okunmak zorunda. Yaptığı şey pencereyi FAIL-CLOSED yapmaktır: uyuşmazlık
    görülürse geçiş reddedilir. Kalıcı çözüm `sector_packages.sector_id`'yi
    yazımdan sonra DEĞİŞMEZ kılmaktır; o bir migration işidir ve bu görevin
    kapsamında değildir (bugün hiçbir üretim yolu bu kolonu güncellemiyor —
    ölçüldü: depo genelinde yazıcı yok).
    """
    if observed != locked:
        raise LifecycleError(
            f"paketin sektörü kilit alındıktan sonra değişti: {package_id} "
            f"artık {observed} sektöründe, kilitlenen {locked} — geçiş reddedildi"
        )


async def _lock_sector(db, sector_id: UUID) -> None:
    """Sektör satırını kilitler — yaşam döngüsünün TEK serileştirme noktası.

    Paket satırlarını kilitlemek yetmiyordu: ilk aktivasyonda kilitlenecek
    aktif satır YOKTUR, dolayısıyla iki eşzamanlı ilk aktivasyon hiçbir yerde
    karşılaşmıyor ve ikisi de olay yazıyordu (checkpoint 13, F2). Sektör satırı
    her durumda vardır ve sabittir, o yüzden çapa odur.

    **Kilit sırası (üç yaşam döngüsü fonksiyonunda da AYNI):** önce
    `social.sectors` satırı, sonra paket satırları. Tek sıra = kilitlenme yok.
    """
    locked = await db.fetchval(
        "SELECT id FROM social.sectors WHERE id = $1 FOR UPDATE", sector_id
    )
    if locked is None:
        raise LifecycleError(f"sektör bulunamadı: {sector_id}")


async def _lock_and_load(db, package_id: UUID):
    """Sektör kilidini alıp paketi kilit ALTINDA okur — `(sector_id, satır)`.

    İki okuma bilerek ayrıdır: kilitsiz ilk okuma YALNIZ hangi sektörü
    kilitleyeceğimizi bulmak içindir; durum kararı kilitten SONRAKİ okumaya
    dayanır. Aradaki pencere F2'nin kaynağıydı ve F4'ün fail-closed kapısı da
    burada durur — protokol TEK kopya olduğu için iki yaşam döngüsü ucunun o
    pencereyi farklı kapatması mümkün değildir.

    **Durum kontrolü ÇAĞIRANDA kalır:** her uç kendi beklediği durumu ve o
    durum tutmadığında kullanıcıya ne söyleneceğini bilir; buraya taşımak
    farkı bir parametreye çevirip okunurluğu düşürürdü.
    """
    sector_id = await db.fetchval(
        "SELECT sector_id FROM social.sector_packages WHERE id = $1", package_id
    )
    if sector_id is None:
        raise LifecycleError(f"paket bulunamadı: {package_id}")
    await _lock_sector(db, sector_id)

    row = await db.fetchrow(
        "SELECT sector_id, version, status FROM social.sector_packages "
        "WHERE id = $1 FOR UPDATE",
        package_id,
    )
    if row is None:
        raise LifecycleError(f"paket bulunamadı: {package_id}")
    _require_same_sector(row["sector_id"], sector_id, package_id)
    return sector_id, row


async def _active_row(db, sector_id: UUID):
    """Sektörün aktif satırı. Sektör kilidi ALINDIKTAN SONRA çağrılır."""
    return await db.fetchrow(
        "SELECT id, version FROM social.sector_packages "
        "WHERE sector_id = $1 AND status = 'active' FOR UPDATE",
        sector_id,
    )


async def _apply_status_transition(
    db,
    *,
    sector_id: UUID,
    event_type: str,
    actor: str,
    activate: tuple[UUID, str] | None,
    archive: tuple[UUID, str] | None,
    from_version: int | None,
    to_version: int | None,
) -> None:
    """Ham iki-adım geçişi + olay kaydı — TEK transaction (F24, K-101/K-102).

    `activate` ve `archive` aynı şekli taşır: `(paket_id, beklenen_durum)`.
    Sürüm numarası bu demetlerde DURMAZ — olayın sürümleri zaten `from_version`
    / `to_version` ile taşınıyor ve iki yerde taşımak, ikisinin ayrışabildiği
    bir pencere açardı.

    ÖZELDİR ve modül dışına verilmez. Public yüzey (aktivasyon / rollback /
    deaktivasyon) kendi kapı kanıtını doğruladıktan SONRA buraya gelir.

    Olay yazımı burada `_record_event` ile SARILMAZ: çalışma zamanı yollarında
    bir denetim satırı yüzünden kullanıcının içeriğini düşürmek orantısızdır,
    ama yaşam döngüsünde izsiz bir geçiş sessiz bir yalandır. `log_package_event`
    altyapı hatasında `None` döner — o dönüş burada HATA sayılır.
    """
    async with db.transaction():
        event_id = await log_package_event(
            db,
            event_type=event_type,
            sector_id=sector_id,
            package_id=activate[0] if activate else archive[0],
            from_version=from_version,
            to_version=to_version,
            actor=actor,
        )
        if event_id is None:
            raise LifecycleError(
                f"{event_type} olayı yazılamadı — izsiz geçiş yapılmaz (F24)"
            )

        if archive is not None:
            await _set_status(db, archive[0], "archived", expected=archive[1])
        if activate is not None:
            await _set_status(db, activate[0], "active", expected=activate[1])


async def insert_draft(
    db,
    *,
    sector_id: UUID,
    content: dict,
    schema_version: int,
    run_id: str | None = None,
    actor: str,
    decision_log: list[dict] | None = None,
) -> UUID:
    """Doğrulayıcı-arkalı TEK draft yazıcısı (spec §3.6; K-135 yazma yüzeyi).

    Doğrulayıcının iki dış girdisi (sistem takvimi, kayıtlı marka adları)
    ÇAĞIRANDAN alınmaz, DB'den okunur. Aksi hâlde kapı yalnız çağıran doğru
    listeyi verdiğinde çalışırdı — yani kapı değil nezaket kuralı olurdu.

    `version` sektör içinde son + 1'dir. Eşzamanlı iki yazımda ikisi de aynı
    numarayı görebilir; `UNIQUE (sector_id, version)` birini reddeder
    (fail-closed).

    **`decision_log` (Plan 2 Task 3).** Verilmezse Plan 1 davranışı AYNEN
    korunur: günlüğe tek bir `draft_created` izi yazılır. Verilirse İKİ
    kapıdan geçer — `identity.validate_decision_log` (satır şeması) ve
    `identity.check_unit_integrity` (içerikle iki yönlü örtüşme) — ve boş
    değilse yazılan günlük ODUR. Plan 1'in olay satırı ÖNÜNE eklenmez: o
    satır şemayı geçmez ve karar günlüğünü okuyan her kapı onu geçersiz
    sayardı.

    Bütünlük kapısının BURADA olması zorunludur: K-135 tek yazma yüzeyidir,
    yani tutarsız bir çiftin kalıcı hâle gelebileceği tek kapı da burasıdır.
    Sonraki bir göreve bırakılsaydı, bu görevin ürettiği "iki yönlü örtüşme"
    garantisini hiçbir şey denetlemiyor olurdu.

    Kimlik günlükte, içerik şemasında DEĞİL: içeriğe `unit_id` eklemek yazım
    kapısından geçmez (`_check_cta_items` anahtar kümesini eşitlikle ölçer).
    İkisi AYNI işlemde yazıldığı için eşleme bayatlayamaz.

    **ÇÖZÜLMEDİ + PARK EDİLDİ — taslağın yaratıcısı bu yolda KAYBOLUYOR
    (fix turu 1, F1; evi YOK).** Ölçüldü: `insert_draft` hiç olay yazmaz
    (`log_package_event`'in bu modüldeki tek çağrısı `_apply_status_transition`
    içindedir), `package_events.EVENT_TYPES` kapalıdır ve `draft_created`
    diye bir tür TAŞIMAZ, `sector_packages` tablosunda da `actor`/`created_by`
    kolonu YOKTUR (migration 032). Yani `actor` şu ana kadar YALNIZ Plan 1'in
    `draft_created` satırında yaşıyordu; günlük verildiğinde o satır yazılmaz
    ve yaratıcı hiçbir yerde durmaz. Bu bir kabul edilmiş risk DEĞİL, açık bir
    kayıptır ve burada çözülemez.

    **Yolların ÖLÇÜLMÜŞ bedeli (fix turu 2'de DÜZELTİLDİ).** Önceki yazım
    "K-56 bildirim bağı" diyordu; bu YANLIŞTI ve ölçümle çürüdü: K-56 yorumu
    `ADMIN_NOTIFIED_EVENTS`'in üstündedir ve "bu üç olay" derken kendi kümesini
    kastediyor (`mismatch_fallthrough` · `package_read_error` ·
    `stale_assignment_fallback`); bildirim kapısı tek koşuldur
    (`event_type in ADMIN_NOTIFIED_EVENTS`, `package_events.py:275`) ve
    `LIFECYCLE_EVENTS`'in HİÇBİR üyesi o kümede DEĞİLDİR. Yani yeni bir olay
    türü eklemek bildirim davranışına DOKUNMAZ. Gerçek bedel şudur:

    * **Olay türü yolu:** `033_package_events.sql:40-50` `event_type` CHECK'ini
      TAM DOKUZ değerle pinler → yeni tür için migration + rollback şart.
      Üstelik 033 kendi doğrulama bloğunda CHECK tanımının birebir metnini
      **İKİ AYRI YERDE** bekler ve genişletme İKİSİNİ BİRDEN düşürür:
      `033:114-119` (`package_events.event_type CHECK` etiketi) ve
      `033:183-184` (`package_events kısıt kümesi (kapalı)` etiketi — kapalı
      manifest, CHECK metnini ayrıca taşır). ÖLÇÜLDÜ: dokuz değere onuncu bir
      değer (`draft_created`) eklenmiş CHECK'le 033 yeniden uygulanınca
      `rc=3` ve hata mesajı İKİ etiketi birden basıyor. (Bu ikinci kalem fix
      turu 2'de sayılmamıştı.) `tests/test_migration_033.py::
      test_widened_event_type_check_is_caught` genişletilmiş CHECK'i
      yakalamak için VARDIR. Ayrıca `package_events.EVENT_TYPES` (bu görevin
      Files listesi DIŞINDA) ve `tests/test_package_stamp_and_events.py:118-122`
      pinli enum testi. Not: `package_events` tablosunda `actor` kolonu ZATEN
      var ve yaşam döngüsü olayları onu ZORUNLU kılıyor
      (`package_events.py:223`) — yani taşıyıcı hazır, kapalı olan yalnız
      türün kendisi.
    * **Kolon yolu:** `sector_packages`'a `created_by` — yine migration +
      rollback, ve bu yol da PİNLİ BEKLENTİ güncellemesi taşır (ilk yazım
      yalnız "migration + rollback" diyordu, eksikti). `032_sector_packages.sql:377`
      `sector_packages kolon imzası`nı KAPALI küme olarak pinler. ÖLÇÜLDÜ:
      `sector_packages`'a `created_by TEXT` eklenip 032 yeniden uygulanınca
      `rc=3`, düşen tek etiket `sector_packages kolon imzası`. Ek olarak
      `tests/test_plan2_interface_contract.py:366-367` kolon kümesini sözlük
      EŞİTLİĞİYLE karşılaştırır; ÖLÇÜLDÜ: aynı kolon eklendiğinde `columns`
      yüzeyi eşit ÇIKMIYOR (`yalnız gözlenende: ['created_by']`), diğer üç
      yüzey (kısıt · indeks · tetikleyici) eşit kalıyor. (Ölçüm yöntemi:
      testin KENDİ `_relation_manifest` + `EXPECTED_032_MANIFEST` çifti
      bozulmuş bir şemaya karşı koşuldu; pytest oturumu şemayı her koşumda
      yeniden kurduğu için testin kendisi bu yolda koşturulamıyor.)
    * **Üçüncü `tur` yolu:** karar günlüğü şemasını (ek ile pinli K-84)
      değiştirmek.

    Üçü de bu görevin kapsamı DIŞINDADIR. Sahibi kontrolör tarafından
    atanacaktır; burada uydurma bir ev VERİLMEZ.
    """
    owner = _require_actor(actor)

    if decision_log is not None:
        log_errors = identity.validate_decision_log(decision_log)
        if log_errors:
            raise ValueError(
                "karar günlüğü şemayı geçmedi: " + "; ".join(log_errors)
            )

    holiday_rows = await db.fetch(
        "SELECT name_tr FROM social.public_holidays WHERE name_tr IS NOT NULL"
    )
    holiday_keys = {
        key
        for key in (normalize_special_day_key(row["name_tr"]) for row in holiday_rows)
        if key
    }
    brand_rows = await db.fetch("SELECT name FROM social.brands WHERE name IS NOT NULL")

    result = validate_package_content(
        content,
        banned_brand_names=[row["name"] for row in brand_rows],
        holiday_keys=holiday_keys,
    )
    if not result.ok:
        raise ValueError("paket içeriği yazım kapısını geçmedi: " + "; ".join(result.errors))

    # SIRA: içerik uyarıları ÖNCE (fix turu 2, Minor). Bütünlük kapısı fix
    # turu 1'de bu döngünün ÖNÜNE girmişti; reddedilen bir çift, içeriğin
    # kendi uyarılarını da sessizce yutuyordu. Yazım her iki hâlde de olmuyor
    # ama gözlemlenebilirlik farkı gerçekti ve sessizce değişmişti.
    # Sırayı YORUM değil TEST tutar (fix turu 3, B2):
    # `tests/test_package_lifecycle.py::
    #  test_insert_draft_logs_content_warnings_before_pair_gate` — kapı bu
    # döngünün önüne geçerse KIRMIZI düşer (411c767'ye karşı ölçüldü).
    for warning in result.warnings:
        logger.warning("paket taslağı uyarısı (sector_id=%s): %s", sector_id, warning)

    if decision_log:
        # Yaşamayan satırlar (`kirp` · `cikar` · notlar) bu kapıda SAYILMAZ:
        # kırpılan öğe aday pakete girmez, yani yolu içerikte olmayacaktır.
        # Kapı "her satırın yolu içerikte olsun" diye yazılsaydı gerçek bir
        # kırpma taşıyan her paket reddedilirdi.
        pair_errors = identity.check_unit_integrity(content, decision_log)
        if pair_errors:
            raise ValueError(
                "içerik ile karar günlüğü tutarsız: " + "; ".join(pair_errors)
            )

    return await db.fetchval(
        """
        INSERT INTO social.sector_packages
            (sector_id, version, status, schema_version, content, decision_log, run_id)
        SELECT $1,
               COALESCE(MAX(version), 0) + 1,
               'draft',
               $2,
               $3,
               $4,
               $5
          FROM social.sector_packages
         WHERE sector_id = $1
        RETURNING id
        """,
        sector_id,
        schema_version,
        content,
        decision_log if decision_log else [{"event": "draft_created", "actor": owner}],
        run_id,
    )


async def activate_package(
    db,
    *,
    package_id: UUID,
    evidence: ActivationGateEvidence,
    actor: str,
) -> None:
    """Taslağı aktif yapar; varsa öncekini AYNI transaction'da arşivler.

    Kanıt alanlarından herhangi biri sağlanmazsa `GateNotSatisfied` ile
    REDDEDER — mekanik kontrol, yorum değil.
    """
    _require_evidence(evidence, ActivationGateEvidence)
    owner = _require_actor(actor)

    unmet = []
    if not evidence.activation_eligible:
        unmet.append("activation_eligible")
    if evidence.open_questions_count != 0:
        unmet.append(f"open_questions_count={evidence.open_questions_count} (K-71: 0 olmalı)")
    if not evidence.katman1_passed:
        unmet.append("katman1_passed")
    if not evidence.checklist_approved:
        unmet.append("checklist_approved")
    if unmet:
        raise GateNotSatisfied("aktivasyon kapısı sağlanmadı: " + ", ".join(unmet))

    async with db.transaction():
        sector_id, target = await _lock_and_load(db, package_id)
        if target["status"] != "draft":
            raise LifecycleError(
                f"yalnız 'draft' aktive edilebilir (görülen: {target['status']!r}); "
                "arşivlenmiş sürümü geri getirmek rollback_package'ın işidir"
            )

        current = await _active_row(db, sector_id)
        current_version = current["version"] if current else None

        if evidence.expected_active_version is not None and (
            current_version != evidence.expected_active_version
        ):
            raise GateNotSatisfied(
                "expected_active_version uyuşmuyor: kanıt "
                f"{evidence.expected_active_version}, gerçek {current_version} — "
                "onay verildiğinden beri aktif sürüm değişmiş (K-94 yeteneği)"
            )

        await _apply_status_transition(
            db,
            sector_id=sector_id,
            event_type="activation",
            actor=owner,
            activate=(package_id, "draft"),
            archive=(current["id"], "active") if current else None,
            from_version=current_version,
            to_version=target["version"],
        )


async def rollback_package(
    db,
    *,
    sector_id: UUID,
    to_version: int,
    evidence: RollbackGateEvidence,
    actor: str,
) -> None:
    """Arşivlenmiş bir sürümü geri getirir; aktif olanı arşivler.

    Hedef-sürüm kanıtı ÇAĞIRANDAN alınmaz, burada doğrulanır: hedef o sektörde
    var olmalı ve `archived` durumda olmalı.
    """
    _require_evidence(evidence, RollbackGateEvidence)
    owner = _require_actor(actor)

    unmet = []
    if not evidence.manager_approved:
        unmet.append("manager_approved")
    if not evidence.katman1_passed:
        unmet.append("katman1_passed")
    if unmet:
        raise GateNotSatisfied("rollback kapısı sağlanmadı: " + ", ".join(unmet))

    async with db.transaction():
        await _lock_sector(db, sector_id)
        has_archived = await db.fetchval(
            "SELECT EXISTS (SELECT 1 FROM social.sector_packages "
            "WHERE sector_id = $1 AND status = 'archived')",
            sector_id,
        )
        if not has_archived:
            raise LifecycleError(
                "bu sektörde arşivlenmiş sürüm YOK — geri dönülecek bir nokta "
                "yoksa istenen şey rollback değil geri çekmedir: deactivate_package"
            )

        target = await db.fetchrow(
            "SELECT id, status FROM social.sector_packages "
            "WHERE sector_id = $1 AND version = $2 FOR UPDATE",
            sector_id,
            to_version,
        )
        if target is None:
            raise LifecycleError(f"hedef sürüm bu sektörde yok: v{to_version}")
        if target["status"] != "archived":
            raise LifecycleError(
                f"hedef sürüm arşivlenmiş değil (görülen: {target['status']!r}) — "
                "rollback yalnız bir zamanlar aktif olmuş sürüme döner"
            )

        current = await _active_row(db, sector_id)
        if current is None:
            raise LifecycleError(
                "bu sektörde aktif sürüm YOK — geri alınacak bir geçiş yok; "
                "yeni sürüm açmak activate_package'ın işidir"
            )

        await _apply_status_transition(
            db,
            sector_id=sector_id,
            event_type="rollback",
            actor=owner,
            activate=(target["id"], "archived"),
            archive=(current["id"], "active"),
            from_version=current["version"],
            to_version=to_version,
        )


async def deactivate_package(db, *, package_id: UUID, actor: str) -> None:
    """K-38 acil geri çekme — kanıt İSTEMEZ, olay kaydı ZORUNLUDUR.

    Kanıt istememesi bilinçlidir: acil kol, onay toplamayı bekleyemez. Bedeli
    denetim iziyle ödenir — kim, ne zaman, hangi sürümü çekti.
    """
    owner = _require_actor(actor)

    async with db.transaction():
        sector_id, row = await _lock_and_load(db, package_id)
        if row["status"] != "active":
            raise LifecycleError(
                f"yalnız aktif paket geri çekilebilir (görülen: {row['status']!r})"
            )

        await _apply_status_transition(
            db,
            sector_id=sector_id,
            event_type="deactivation",
            actor=owner,
            activate=None,
            archive=(package_id, "active"),
            from_version=row["version"],
            to_version=None,
        )
