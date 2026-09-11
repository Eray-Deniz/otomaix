"""İşletime hazırlık kontrol listesinin DEĞERLENDİRİCİSİ (plan Task 17).

**Kimlik kümesi burada DOĞMAZ.** `readiness_items` (Task 8) kanonik yirmi
maddeyi, sınıflarını ve kümenin parmak izini taşır; bu modül ONUN üstüne yalnız
DEĞERLENDİRME ekler (otomatik ön-kontrolün sonucu · `elle` etiketi). İkinci bir
madde kaydı YASAKTIR (arayüz eki H5) — `CHECKLIST` bir TAKMA ADDIR, kopya değil.

**K-70 — ön-kontrol ONAYLAMAZ.** `evaluate` hiçbir şey yazmaz, `actor` almaz ve
döndürdüğü raporda "onaylandı" diye bir alan YOKTUR. Onay tek bir yerde doğar:
operatör `hazirlik-onayla` komutunu koşar ve `runs.attest_readiness` onayı KAPI
maddelerinden TÜRETİR. Ön-kontrol yalnız işaretler.

**K-69 — kapı yalnız `kapi` sınıfını sayar.** Sonuç iddia eden maddeler
(bugün tek: 15. madde) `sinyal` sınıfındadır; operatöre GÖSTERİLİR, kararını
etkiler, ama tamamlanma kapısına GİRMEZ (spec §10.2 + K-11 (b) açık).

**İlke 9 — ölçülmemiş madde "ölçüldü" gibi sunulmaz.** Otomatik ölçülebilen her
maddenin adlandırılmış bir PROBU vardır ve probun okuduğu artefakt `detay`
alanında yazılıdır. Probu olmayan madde `elle` etiketiyle ve `beklemede`
durumuyla görünür; hiçbir koşulda `gecti` OLMAZ.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from app.services.sector_pipeline import readiness_items, runs

OLCUM_BICIMLERI: tuple[str, ...] = ("otomatik", "elle")
"""Maddenin nasıl işaretlendiği — KAPALI küme."""

MADDE_DURUMLARI: tuple[str, ...] = ("gecti", "gecmedi", "beklemede")
"""Değerlendirme sonucu — KAPALI küme. `beklemede` = operatör beyanı bekleniyor."""

CHECKLIST: tuple[readiness_items.ChecklistItem, ...] = readiness_items.MADDELER
"""Kanonik madde kümesinin TAKMA ADI — ikinci kayıt DEĞİL (arayüz eki H5)."""


@dataclass(frozen=True)
class MaddeSonucu:
    """Tek maddenin değerlendirme satırı."""

    madde_id: str
    sinif: str
    baslik: str
    olcum: str
    durum: str
    detay: str

    def __post_init__(self) -> None:
        if self.olcum not in OLCUM_BICIMLERI:
            raise ValueError(
                f"MaddeSonucu.olcum kapalı kümenin dışında: {self.olcum!r}"
            )
        if self.durum not in MADDE_DURUMLARI:
            raise ValueError(
                f"MaddeSonucu.durum kapalı kümenin dışında: {self.durum!r}"
            )
        if self.olcum == "elle" and self.durum != "beklemede":
            raise ValueError(
                "elle işaretlenen madde ÖLÇÜLMÜŞ gibi sunulamaz — durumu "
                f"'beklemede' olmalı, {self.durum!r} verildi (İlke 9)"
            )


@dataclass(frozen=True)
class ReadinessReport:
    """Bir koşunun hazırlık görünümü — ONAY TAŞIMAZ (K-70)."""

    run_id: str
    satirlar: tuple[MaddeSonucu, ...]

    @property
    def bloklayan_kapi_maddeleri(self) -> tuple[str, ...]:
        """Otomatik ölçümü DÜŞMÜŞ `kapi` maddeleri — onay bunlarla verilemez.

        `sinyal` maddeleri buraya GİRMEZ (K-69): sonuç iddia eden madde
        operatöre gösterilir, kararını etkiler, ama bloklamaz.
        """
        return tuple(
            satir.madde_id
            for satir in self.satirlar
            if satir.sinif == "kapi" and satir.durum == "gecmedi"
        )

    @property
    def elle_bekleyen_maddeler(self) -> tuple[str, ...]:
        """Operatör beyanı bekleyen maddeler (sınıf farkı GÖZETİLMEZ)."""
        return tuple(
            satir.madde_id for satir in self.satirlar if satir.durum == "beklemede"
        )


_Prob = Callable[["_Kanit"], tuple[bool, str]]


@dataclass(frozen=True)
class _Kanit:
    """Probların okuduğu KANIT yüzeyi — koşu satırı + ham artefakt satırları.

    **Koşu satırı HAM okunur, `load_verified_run` ile DEĞİL.** Doğrulanmış
    görünüm yedi kapıyı uygular ve düşen koşuda `RunNotVerified` fırlatır; oysa
    hazırlık raporunun asıl işi tam da yarım koşuyu ANLATMAKTIR. Doğrulanmış
    görünümle okunsaydı rapor, ölçmesi gereken durumda hiç üretilemezdi.
    """

    kosu: Mapping
    artefaktlar: Sequence[Mapping]

    def _kaynaklar(self, kind: str) -> set[str]:
        return {
            satir["source"] for satir in self.artefaktlar if satir["kind"] == kind
        }


# ─── Problar — her biri TEK artefaktı okur ve ADINI söyler ──────────────────
#
# Prob yazılmayan madde otomatik SAYILMAZ: bayrağı `readiness_items`'ta `False`
# olur ve raporda `elle` görünür. "Ölçülebilir sanılan ama ölçülmeyen" üçüncü
# bir hâl YOKTUR — İlke 9'un bu modüldeki karşılığı budur.

BLOKLAYAN_BULGU_SINIFLARI: frozenset[str] = frozenset(
    {"mevzuat_uyusmazligi", "mevzuat_dogrulanamadi", "kapsam_ihlali", "ikinci_aktif"}
)
"""16. maddenin saydığı bulgu sınıfları — `engine_contract.BULGU_SINIFLARI` alt kümesi.

`acik_soru` ve `regresyon_kapisi` DIŞARIDADIR: birincisi maddenin "eksik karar"
ayağında ayrıca sayılır, ikincisi 13./14. maddelerin (Katman-1) konusudur.
"""


def _uc_arac_ayni_brief(kanit: _Kanit) -> tuple[bool, str]:
    kaynaklar = kanit._kaynaklar("research")
    briefler = {
        satir["brief_ref"]
        for satir in kanit.artefaktlar
        if satir["kind"] == "research"
    }
    yeterli = len(kaynaklar) >= 3 and len(briefler) == 1 and None not in briefler
    return (
        yeterli,
        f"ham artefakt katmanı: {len(kaynaklar)} araştırma kaynağı, "
        f"{len(briefler)} ayrı brief referansı",
    )


def _iki_kor_hakem(kanit: _Kanit) -> tuple[bool, str]:
    kaynaklar = kanit._kaynaklar("review")
    return (
        len(kaynaklar) >= 2,
        f"ham artefakt katmanı: {len(kaynaklar)} hakem raporu",
    )


def _sentez_ve_karar_gunlugu(kanit: _Kanit) -> tuple[bool, str]:
    sentezler = kanit._kaynaklar("synthesis")
    gunluk = kanit.kosu["final_decision_log"]
    return (
        bool(sentezler) and bool(gunluk),
        f"ham artefakt katmanı: {len(sentezler)} sentez çıktısı; koşu satırı: "
        f"karar günlüğü {'dolu' if gunluk else 'BOŞ'}",
    )


def _motor_kontrolleri(kanit: _Kanit) -> tuple[bool, str]:
    rapor = kanit.kosu["policy_report"]
    return (
        rapor is not None,
        "koşu satırı: politika raporu "
        + ("yazılı" if rapor is not None else "YOK"),
    )


def _diff_ve_bariyer(kanit: _Kanit) -> tuple[bool, str]:
    diff = kanit.kosu["engine_diff"]
    bariyer = kanit.kosu["barrier_report"]
    return (
        bool(diff) and bool(bariyer),
        "koşu satırı: canonical diff "
        + ("dolu" if diff else "BOŞ")
        + ", bariyer raporu "
        + ("dolu" if bariyer else "BOŞ"),
    )


def _aktivasyona_uygun(kanit: _Kanit) -> tuple[bool, str]:
    sonuc = kanit.kosu["sonuc"]
    return sonuc == "activation_eligible", f"koşu satırı: sonuc={sonuc!r}"


def _aday_yazim_kapisindan_gecti(kanit: _Kanit) -> tuple[bool, str]:
    paket = kanit.kosu["package_id"]
    return (
        paket is not None,
        "koşu satırı: taslak bağı "
        + (f"var ({paket})" if paket is not None else "YOK — yazım kapısı koşmadı"),
    )


def _katman1_pass(kanit: _Kanit) -> tuple[bool, str]:
    """13. ve 14. maddenin ORTAK probu — kayıt bu granülaritede tutulur.

    Katman-1 tasdiki TEK sonuç taşır (`PASS`/`FAIL`); paketsiz regresyon ile
    paketli yapısal kontrolleri AYRI AYRI kaydeden bir alan YOKTUR. İki maddeyi
    de aynı tasdikten okumak, olmayan bir ayrımı varmış gibi göstermekten
    dürüsttür; `detay` okunan kaydı adıyla söyler.
    """
    tasdik = kanit.kosu["katman1_attestation"]
    sonuc = tasdik.get("sonuc") if tasdik else None
    return (
        sonuc == "PASS",
        f"Katman-1 tasdiki: sonuc={sonuc!r} (iki madde de AYNI tasdikten okunur)",
    )


def _bloklayan_uyusmazlik_yok(kanit: _Kanit) -> tuple[bool, str]:
    rapor = kanit.kosu["policy_report"]
    if rapor is None:
        return (False, "koşu satırı: politika raporu YOK — bulgu sayılamaz")
    bulgular = [
        bulgu
        for bulgu in rapor.get("bulgular", ())
        if bulgu.get("sinif") in BLOKLAYAN_BULGU_SINIFLARI
    ]
    acik_sorular = rapor.get("acik_soru_kimlikleri", ())
    return (
        not bulgular and not acik_sorular,
        f"politika raporu: {len(bulgular)} bloklayıcı bulgu, "
        f"{len(acik_sorular)} açık soru",
    )


def _yonetici_gorerek_onayladi(kanit: _Kanit) -> tuple[bool, str]:
    goruntu = kanit.kosu["approval_snapshot"]
    karar = kanit.kosu["approval_karar"]
    return (
        goruntu is not None and karar == "onay",
        "koşu satırı: dondurulmuş görüntü "
        + ("var" if goruntu is not None else "YOK")
        + f", karar={karar!r}",
    )


PROBLAR: dict[str, _Prob] = {
    "md-03": _uc_arac_ayni_brief,
    "md-05": _iki_kor_hakem,
    "md-07": _sentez_ve_karar_gunlugu,
    "md-09": _motor_kontrolleri,
    "md-10": _diff_ve_bariyer,
    "md-11": _aktivasyona_uygun,
    "md-12": _aday_yazim_kapisindan_gecti,
    "md-13": _katman1_pass,
    "md-14": _katman1_pass,
    "md-16": _bloklayan_uyusmazlik_yok,
    "md-19": _yonetici_gorerek_onayladi,
}
"""`madde_id` → probu. Yalnız `otomatik=True` maddelerin probu OLUR."""

ELLE_GEREKCELERI: dict[str, str] = {
    "md-01": "kapsam onayı bir YÖNETİM kararıdır; artefakt bırakmaz.",
    "md-02": "bloklayıcı kararların kapanışı karar deposunda yaşar, koşu satırında değil.",
    "md-04": (
        "mekanik kapı raporunun artefakt türü şemada YOK — yazım bugün düşüyor; "
        "ev: Task 18 şema ayağı."
    ),
    "md-06": "örneklem kısıtının DÜRÜSTÇE raporlanması metnin yargısıdır, sayılamaz.",
    "md-08": (
        "kapsam tamlığı kalıcı kalıp kimliğine bağlıdır; koşu satırı kapsam "
        "sayacı TUTMUYOR."
    ),
    "md-15": (
        "sonuç iddia eden SİNYAL maddesi — kapıya çevrilmez (spec §10.2, K-11 (b))."
    ),
    "md-17": "post sürüm damgasının VERİ YERİ K-07'de açık; okunacak alan yok.",
    "md-18": "prosedür testi elle koşulur; koşu satırına iz bırakmaz.",
    "md-20": (
        "taban sürüm eşitliğini aktivasyon kapısı kendi kanıtından ölçer; burada "
        "yeniden türetmek ikinci bir türetim olurdu."
    ),
}
"""`madde_id` → neden otomatik ölçülemediği. Beyan, ölçüm gibi sunulmaz."""


async def evaluate(db, *, run_id: str) -> ReadinessReport:
    """Koşunun hazırlık listesini değerlendirir — HİÇBİR ŞEY YAZMAZ (K-70)."""
    if type(run_id) is not str or not run_id.strip():
        raise ValueError("run_id zorunlu")
    kosu = await db.fetchrow(
        "SELECT * FROM social.sector_package_runs WHERE run_id = $1", run_id
    )
    if kosu is None:
        raise runs.RunNotVerified(f"koşu satırı yok: {run_id!r}")
    artefaktlar = await db.fetch(
        "SELECT kind, source, brief_ref FROM social.sector_research_artifacts "
        "WHERE run_id = $1",
        run_id,
    )
    kanit = _Kanit(kosu=kosu, artefaktlar=artefaktlar)

    satirlar: list[MaddeSonucu] = []
    for madde in CHECKLIST:
        if madde.otomatik:
            gecti, detay = PROBLAR[madde.madde_id](kanit)
            durum = "gecti" if gecti else "gecmedi"
            olcum = "otomatik"
        else:
            durum, olcum = "beklemede", "elle"
            detay = ELLE_GEREKCELERI[madde.madde_id]
        satirlar.append(
            MaddeSonucu(
                madde_id=madde.madde_id,
                sinif=madde.sinif,
                baslik=madde.baslik,
                olcum=olcum,
                durum=durum,
                detay=detay,
            )
        )
    return ReadinessReport(run_id=run_id, satirlar=tuple(satirlar))
