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

from app.services.sector_pipeline import (
    auditors,
    engine,
    identity,
    readiness_items,
    runs,
)
from app.services.sector_pipeline.engine_contract import PolicyReport

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
    kanit_parmakizi: str = ""
    """Değerlendirmenin OKUDUĞU ham artefakt kümesinin parmak izi.

    Tasdik kaydının "ne gördüm" alanı YOKTUR (Task 8 sözleşmesi) ve artefakt
    tablosu EKLEMELİDİR: onaydan sonra satır düşebilir. Bu alan, yazımdan hemen
    önce TAZE bir okumayla karşılaştırılır; bayat bir değerlendirme belgelenemez.
    **Pencereyi DARALTIR, kapatmaz** — gerçek kapanış (tasdiğin gördüğünü
    kaydetmesi ya da aktivasyonun yeniden ölçmesi) sözleşme revizyonundadır,
    son tarih Task 19 (hakem turu 2, F1; Eray kararı 2026-09-11).
    """

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

    def ureticiler(self, kind: str) -> set[str]:
        """O türdeki artefaktları ÜRETEN kimlikler (damgadaki `model`).

        **Damga kimlik DEĞİLDİR, damga BİLEŞİKTİR** (hakem turu 1, yüksek):
        `model; surum; tarih; girdi_ozeti`. İlk yazım ham `source` dizelerini
        sayıyordu, yani TEK aracın üç ayrı tarihli çıktısı "üç araç" diye
        okunuyordu. Kimlik yalnız `model` alanıdır.

        Damgası ayrıştırılamayan satır SESSİZCE atlanmaz — `ArtifactStampMissing`
        fırlatılır; `evaluate` onu YALNIZ o maddenin düşüşüne çevirir (komşu
        maddeler etkilenmez, rapor üretilmeye devam eder).
        """
        return {
            runs.parse_stamp(satir["source"])["model"]
            for satir in self.artefaktlar
            if satir["kind"] == kind
        }


# ─── Problar — her biri TEK artefaktı okur ve ADINI söyler ──────────────────
#
# Prob yazılmayan madde otomatik SAYILMAZ: bayrağı `readiness_items`'ta `False`
# olur ve raporda `elle` görünür. "Ölçülebilir sanılan ama ölçülmeyen" üçüncü
# bir hâl YOKTUR — İlke 9'un bu modüldeki karşılığı budur.

BLOKLAYAN_BULGU_SINIFLARI: frozenset[str] = frozenset(
    etki.sinif
    for etki in engine.BULGU_ETKILERI
    if etki.etki in (engine.ETKI_BLOKLAR, engine.ETKI_AKTIVASYONU_ENGELLER)
)
"""16. maddenin saydığı bulgu sınıfları — MOTORUN etki tablosundan TÜRETİLİR.

**Elle yazılmış küme, motorun politikasını sessizce EZİYORDU** (hakem turu 1,
orta; kendi gerilemem). İlk yazım `mevzuat_dogrulanamadi`'yı koşulsuz bloklayıcı
sayıyordu; oysa o sınıf `ETKI_BAYRAGA_BAGLI`dır (K-128) ve varsayılan
`block_on_legislation=False` altında motor onu BLOKLAMAZ — hazırlık kapısı,
motorun izin verdiği koşuyu reddediyordu. Bloklayıcılık tek yerde tanımlıdır ve
burası onu OKUR, yeniden yazmaz.

`POLITIKA_RAPORU_ALANLARI` ile birlikte bu modülün motor sözleşmesine tek
bağımlılığıdır (R9 yönü: motor Task 12/13, hazırlık Task 17 — geriye bağımlılık).
"""

def _politika_raporu(kanit: _Kanit) -> PolicyReport | None:
    """Koşu satırındaki politika raporunu TİPLİ okur; uymayan yükte `None`.

    **Şekil listesi BURADA yazılmaz** (hakem turu 2, yüksek). İlk yazım dört
    anahtarın VARLIĞINA ve iki dizinin tipine bakıyordu; `{"kararsizlar": 1,
    "bulgular": [{}], "uygulanmayan_kararlar": None, "acik_soru_kimlikleri": []}`
    o kapıdan geçiyor ve `md-16` boş bulguyu sessizce atlayıp "temiz" diyordu.
    Tüketicinin kendi doğrulama listesini yazması ikinci bir sözleşme demekti;
    sözleşme zaten yapısaldır — eksik olan tipli okuyucuydu ve o okuyucu artık
    sözleşmenin kendi evinde: `PolicyReport.from_payload`.
    """
    try:
        return PolicyReport.from_payload(kanit.kosu["policy_report"])
    except (TypeError, ValueError):
        return None


def _uc_arac_ayni_brief(kanit: _Kanit) -> tuple[bool, str]:
    """ÜÇ AYRI ÜRETİCİ + TEK brief referansı.

    Araçların HANGİLERİ olduğu doğrulanamaz: üç araçlı araştırma dış depoda elle
    koşulur ve kanonik bir araç kimliği listesi YOKTUR. Ölçülen şey "üç ayrı
    üretici kimliği"dir; `detay` bunu olduğu gibi söyler (İlke 9).
    """
    ureticiler = kanit.ureticiler("research")
    briefler = {
        satir["brief_ref"]
        for satir in kanit.artefaktlar
        if satir["kind"] == "research"
    }
    yeterli = len(ureticiler) >= 3 and len(briefler) == 1 and None not in briefler
    return (
        yeterli,
        f"ham artefakt katmanı: {len(ureticiler)} AYRI üretici kimliği "
        f"({', '.join(sorted(ureticiler)) or 'yok'}), {len(briefler)} ayrı brief "
        "referansı — araç kimlikleri doğrulanamaz, yalnız ayrıklık ölçülür",
    )


def _iki_kor_hakem(kanit: _Kanit) -> tuple[bool, str]:
    """Hakem ROL UZAYI kapalıdır — iki rapor iki hakem demek değildir."""
    ureticiler = kanit.ureticiler("review")
    beklenen = set(auditors.DENETCI_ROLLERI)
    return (
        ureticiler == beklenen,
        f"ham artefakt katmanı: hakem kimlikleri {sorted(ureticiler) or 'yok'}; "
        f"beklenen rol uzayı {sorted(beklenen)}",
    )


def _sentez_ve_karar_gunlugu(kanit: _Kanit) -> tuple[bool, str]:
    sentezler = kanit.ureticiler("synthesis")
    gunluk = kanit.kosu["final_decision_log"]
    return (
        bool(sentezler) and bool(gunluk),
        f"ham artefakt katmanı: {len(sentezler)} sentez çıktısı; koşu satırı: "
        f"karar günlüğü {'dolu' if gunluk else 'BOŞ'}",
    )


def _motor_kontrolleri(kanit: _Kanit) -> tuple[bool, str]:
    rapor = _politika_raporu(kanit)
    return (
        rapor is not None,
        "koşu satırı: politika raporu "
        + ("dört alanıyla yazılı" if rapor is not None else "YOK ya da ŞEKLİ BOZUK"),
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
    rapor = _politika_raporu(kanit)
    if rapor is None:
        return (
            False,
            "koşu satırı: politika raporu YOK ya da ŞEKLİ BOZUK — bulgu sayılamaz",
        )
    bulgular = [
        bulgu for bulgu in rapor.bulgular if bulgu.sinif in BLOKLAYAN_BULGU_SINIFLARI
    ]
    acik_sorular = rapor.acik_soru_kimlikleri
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


async def _artefakt_satirlari(db, run_id: str) -> list:
    return await db.fetch(
        "SELECT kind, source, brief_ref FROM social.sector_research_artifacts "
        "WHERE run_id = $1 ORDER BY kind, source",
        run_id,
    )


def _parmakizi(artefaktlar) -> str:
    """Okunan kanıt kümesinin KANONİK parmak izi — tek türetme kuralı."""
    return identity.canonical_sha(
        [
            {
                "kind": satir["kind"],
                "source": satir["source"],
                "brief_ref": satir["brief_ref"],
            }
            for satir in artefaktlar
        ]
    )


async def kanit_parmakizi(db, *, run_id: str) -> str:
    """Koşunun O ANKİ kanıt kümesinin parmak izi (yazım öncesi tazelik kapısı)."""
    return _parmakizi(await _artefakt_satirlari(db, run_id))


async def evaluate(db, *, run_id: str) -> ReadinessReport:
    """Koşunun hazırlık listesini değerlendirir — HİÇBİR ŞEY YAZMAZ (K-70)."""
    if type(run_id) is not str or not run_id.strip():
        raise ValueError("run_id zorunlu")
    kosu = await db.fetchrow(
        "SELECT * FROM social.sector_package_runs WHERE run_id = $1", run_id
    )
    if kosu is None:
        raise runs.RunNotVerified(f"koşu satırı yok: {run_id!r}")
    artefaktlar = await _artefakt_satirlari(db, run_id)
    kanit = _Kanit(kosu=kosu, artefaktlar=artefaktlar)

    satirlar: list[MaddeSonucu] = []
    for madde in CHECKLIST:
        if madde.otomatik:
            try:
                gecti, detay = PROBLAR[madde.madde_id](kanit)
            except runs.ArtifactStampMissing as hata:
                # Bozuk damga ölçülemezliktir, temizlik DEĞİLDİR: madde düşer,
                # rapor ayakta kalır ve sebebi operatöre görünür.
                gecti, detay = False, f"ölçülemedi — bozuk K-80 damgası: {hata}"
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
    return ReadinessReport(
        run_id=run_id,
        satirlar=tuple(satirlar),
        kanit_parmakizi=_parmakizi(artefaktlar),
    )
