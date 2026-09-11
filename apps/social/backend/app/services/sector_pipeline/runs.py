"""Koşu ve artefakt servisi (Plan 2 Task 8 — K-09/K-17/K-82/K-83/K-93/K-136/K-145).

Bu modül bir denemenin KANONİK kaydını yazar ve okur: koşu satırı · ham artefakt ·
kapı tasdikleri · motor sonucu · geri alma olayları. Migration 036 kurduğu
tabloların TEK servis yüzeyidir.

**Bağlayıcı invariantlar:**

* Ham katman SALT-EKLEMEDİR (032 tetikleyicisi); bu modül `UPDATE` denemez.
* K-09: aynı `(run_id, source, kind)` ikinci kez yazılamaz.
* K-80: her artefakt satırı `source` alanında model/sürüm/tarih/girdi-özeti
  damgası taşır; eksikse yazım REDDEDİLİR (servis kapısı — DB'de karşılığı yok).
* K-82: yarım koşu `mark_incomplete` ile işaretlenir, dosya EZİLMEZ; aynı işlemde
  yönetici bildirimi yazılır.
* K-17: koşu klasörü adı DB `run_id`'sine EŞİTTİR.
* K-93: `no_change`/`blocked` dâhil HER koşu satır yazar.
* TEK KAPI LİSTESİ: yazım · güncelleme · onay · aktivasyon dördü de
  `load_verified_run`'dan geçer; ikinci bir kapı listesi YOKTUR.

**Bağımlılık yönü.** Bu modül Plan 1'in `sector_package_lifecycle`'ından okur
(aktör kapısı · kanıt sınıfları · kanıt yükü/parmak izi yardımcıları); ters
yönde import YOKTUR. Yardımcılar bu dosyada NE TANIMLI NE KOPYALIDIR — arayüz
eki AÇIK-3 kararı gereği tanımları Plan 1 modülündedir, burası yalnız ÇAĞIRIR.
"""

from __future__ import annotations

import logging
import re
import secrets
import uuid
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence
from uuid import UUID

from app.services.notifications import record_admin_event
from app.services.sector_package_lifecycle import (
    ActivationGateEvidence,
    anchor_for_package,
    anchor_sector,
    EvidenceMintRefused,
    LifecycleError,
    RollbackGateEvidence,
    _evidence_fingerprint_from_payload,
    _require_actor as require_actor,
    activation_evidence_payload,
    rollback_evidence_payload,
    rollback_package,
)
from app.services.sector_pipeline import identity, readiness_items
from app.services.sector_pipeline.engine_contract import EngineResult

# ─── Kapalı değer kümeleri ──────────────────────────────────────────────────

KOSU_TURLERI: tuple[str, ...] = ("ilk", "periyodik", "duzeltme")
DURUMLAR: tuple[str, ...] = ("calisiyor", "tamamlandi", "tamamlanmadi")

ASAMALAR: tuple[str, ...] = (
    "brief-doctor",
    "kaynak-tabani",
    "denetim",
    "sentez",
    "motor",
)
"""`mark_incomplete`'in aşama kümesi — KAPALI. Bildirim anahtarı koşu + aşamadır."""

PLAN_DURUMLARI: tuple[str, ...] = ("bekliyor", "tamamlandi", "hata", "hedefsiz")
KANIT_SINIFLARI: tuple[str, ...] = ("kanitli", "kanitli_etkilenmemis", "ayrilamaz")

TUR_ARIZASI_OLAYI = "sektor_paketi.tur_arizasi"
UYELIK_DARALTMA_OLAYI = "sektor_paketi.olay_uyeligi_daraltildi"

JETON_TABLOLARI: tuple[str, ...] = ("sector_package_runs", "package_rollback_plans")

_OLAY_KILIT_ONEKI: str = "sektor_paketi.olay:"
"""Olay danışma kilidinin TEK öneki — ikincisi YOKTUR."""

ARASTIRMA_DEPOSU_KOKU = Path("/root/otomaix-sosyal-medya-arastirmasi")
"""Dış araştırma deposunun kökü (K-17). Koşu klasörü onun `kosu/` alt dizinindedir.

Klasör dış deponun `.gitignore`'undadır (arayüz eki R1): izlenmeyen koşu klasörü
pin kapısını DÜŞÜRMEZ, onu COMMIT etmek düşürürdü.
"""

_RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
"""`run_id` hem veritabanı anahtarı hem DOSYA SİSTEMİ adıdır (K-17).

Bu yüzden şekil kapısı yol ayracını, `..`yı ve boş adı reddeder — koşu klasörü
adı DB değerinden türetildiği için şekilsiz bir kimlik dizin kaçışına dönüşürdü.
"""


# ─── İstisnalar ─────────────────────────────────────────────────────────────


class RunNotVerified(RuntimeError):
    """Koşu YEDİ kapının en az birinden geçemedi — doğrulanmış koşu üretilmez."""


class CorrectionRunRefused(RuntimeError):
    """Düzeltme turu AÇILAMAZ (K-106/K-72) — ana koşu uygun değil ya da açık tur var."""


class ArtifactStampMissing(ValueError):
    """K-80: artefakt tekrar-üretilebilirlik damgası eksik — yazım REDDEDİLİR."""


class RollbackEvidenceUnavailable(RuntimeError):
    """Kanıt DB'den KURULAMADI — geri alma satırı `hata` olarak kapanır.

    Uydurulmuş boolean ile geçiş YOLU YOKTUR.
    """


class IncidentMembershipLocked(RuntimeError):
    """Olayın ÜYELİĞİ artık değiştirilemez — yürütme BAŞLAMIŞ durumda."""


class ReadinessAttestationRefused(ValueError):
    """Onay TÜRETİLEMEDİ — verilen kapı kümesi kanonik kümeyle örtüşmüyor."""


class TransactionRequired(RuntimeError):
    """Kanıt üreticisi AÇIK bir işlem DIŞINDA çağrıldı — kilitler taşımıyordu.

    Kanıt sınıflarından ve `LifecycleError`'dan AYRI tutulur: bu bir paket
    arızası değil, çağıranın sözleşme ihlalidir ve `execute_rollback_plan`'ın
    `durum='hata'` koluna DÜŞMEZ.
    """


# ─── K-136 — maskeleme süzgeci ve günlük yazıcısı ───────────────────────────
#
# Karar evrensel bir kısıttı ama onu UYGULAYAN dosya/arayüz/test yoktu. Süzgeç
# hata mesajlarını ve alt süreç stderr'ini de kapsar (sızıntının en olası yeri
# orasıdır) ve günlüğe yazan HER yol ondan geçer.

MASKE = "***"

_SIR_ANAHTAR_KELIMELERI = (
    "token",
    "secret",
    "password",
    "passwd",
    "apikey",
    "api_key",
    "api-key",
    "authorization",
    "auth",
    "credential",
    "private_key",
    "access_key",
    "session_key",
    "signature",
    "cookie",
    "jeton",
    "parola",
    "sifre",
    "sır",
    "sir",
    "anahtar",
)

_ANAHTAR_DEGER_RE = re.compile(
    r"(?P<anahtar>[A-Za-z_][A-Za-z0-9_.\-]*)"
    r"(?P<ayirac>\s*[:=]\s*|\s*=>\s*)"
    r"(?P<tirnak>[\"']?)(?P<deger>[^\s\"',;)}\]]+)(?P=tirnak)"
)

_BEARER_RE = re.compile(r"(?i)\b(bearer|basic|token)\s+([A-Za-z0-9._\-+/=]{8,})")

# Şekil-tabanlı sırlar: sağlayıcı önekleri ve uzun rastgele bloklar.
_SEKIL_DESENLERI = (
    re.compile(r"\b(?:sk|pk|rk|ghp|gho|xox[baprs])[-_][A-Za-z0-9_\-]{12,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\b"),
    re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]{40,}(?![0-9a-fA-F])"),
    re.compile(r"postgres(?:ql)?://[^\s]*:[^\s@]+@[^\s]+"),
)

# Olay izi KORUNUR — aşırı maskeleme yok. Bu anahtarlar sır değil kimliktir ve
# maskelenirse arıza bildirimi izlenemez hâle gelir.
_IZ_ANAHTARLARI = frozenset(
    {
        "run_id",
        "parent_run_id",
        "incident_id",
        "package_id",
        "sector_id",
        "asama",
        "kind",
        "durum",
        "sonuc",
        "kosu_turu",
        "event",
        "version",
    }
)


def _sir_anahtari_mi(anahtar: str) -> bool:
    kucuk = anahtar.lower()
    if kucuk in _IZ_ANAHTARLARI:
        return False
    return any(kelime in kucuk for kelime in _SIR_ANAHTAR_KELIMELERI)


def mask_secrets(text: str) -> str:
    """Sır-şekilli değerleri maskeler; olay izini KORUR (K-136).

    İki bağımsız kol: (a) `anahtar=deger` biçiminde sır-adlı anahtarların
    DEĞERİ, (b) sağlayıcı öneki · JWT · uzun hex · kimlikli bağlantı dizesi gibi
    ŞEKİL desenleri. İkisi de gerekir: şekilsiz bir parola yalnız (a) ile,
    anahtarsız bir jeton yalnız (b) ile yakalanır.

    `run_id` · `incident_id` · `asama` gibi iz anahtarları AÇIKÇA muaftır — aşırı
    maskeleme, bildirimin var olma sebebini yok ederdi.
    """
    if not isinstance(text, str):
        text = str(text)

    def _anahtar_deger(eslesme: re.Match[str]) -> str:
        if not _sir_anahtari_mi(eslesme.group("anahtar")):
            return eslesme.group(0)
        tirnak = eslesme.group("tirnak")
        return (
            f"{eslesme.group('anahtar')}{eslesme.group('ayirac')}"
            f"{tirnak}{MASKE}{tirnak}"
        )

    # SIRA BAĞLAYICIDIR (ölçüldü): anahtar=değer kolu önce koşarsa
    # `Authorization: Bearer <jeton>` metninde `Authorization`ın DEĞERİ
    # `Bearer` sanılır, maskelenir ve JETONUN KENDİSİ metinde KALIR.
    sonuc = _BEARER_RE.sub(lambda m: f"{m.group(1)} {MASKE}", text)
    sonuc = _ANAHTAR_DEGER_RE.sub(_anahtar_deger, sonuc)
    for desen in _SEKIL_DESENLERI:
        sonuc = desen.sub(MASKE, sonuc)
    return sonuc


def mask_payload(value: Any) -> Any:
    """Yükün TÜM metin yapraklarını maskeler — sözlük/dizi içinde de."""
    if isinstance(value, Mapping):
        return {anahtar: mask_payload(deger) for anahtar, deger in value.items()}
    if isinstance(value, (list, tuple)):
        return [mask_payload(oge) for oge in value]
    if isinstance(value, str):
        return mask_secrets(value)
    return value


class SecretMaskingFilter(logging.Filter):
    """Kayıt SEVİYESİNDE maskeleme — atlanabilecek bir yol bırakmaz.

    Süzgeç günlükçünün KENDİSİNE takılıdır; `logger.info(...)` doğrudan
    çağrılsa bile kayıt buradan geçer. "Maskesiz yazıcı" diye ikinci bir yol
    açmak, süzgeci nezaket kuralına çevirirdi.

    Alt süreç stderr'i ve hata mesajları da kapsamdadır: `exc_info` burada
    biçimlendirilip maskelenir ve ham hâliyle akışa BIRAKILMAZ.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            metin = record.getMessage()
        except Exception:  # pragma: no cover — biçimlendirilemeyen kayıt
            metin = str(record.msg)
        record.msg = mask_secrets(metin)
        record.args = ()
        if record.exc_info:
            record.exc_text = mask_secrets(
                logging.Formatter().formatException(record.exc_info)
            )
            record.exc_info = None
        elif record.exc_text:
            record.exc_text = mask_secrets(record.exc_text)
        return True


logger = logging.getLogger(__name__)
logger.addFilter(SecretMaskingFilter())


def log_run(run_id: str, message: str, *, level: int = logging.INFO) -> None:
    """Koşu günlüğüne yazan TEK yüzey — maskeleme süzgecinden geçer.

    İz açıkça taşınır (`run_id=<...>`), çünkü maskeleme onu muaf tutar.
    """
    logger.log(level, "run_id=%s %s", run_id, message)


# ─── Dış tipler ────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class VerifiedRun:
    """`load_verified_run`'ın YEDİ kapıdan geçmiş koşu görünümü.

    Dokuz jsonb yükünün dokuzu da `identity.donmus`'tan geçirilir: aktivasyon
    kapısı bu yüklerin İÇİNDEN okur ve `content_sha`/`decision_log_sha` onların
    KİMLİĞİDİR — yapımdan sonra çevrilebilir bir sözlük taşımak, kilitli satırdan
    okunmuş kanıtı sonradan değiştirmeye izin verirdi.
    """

    id: UUID
    run_id: str
    parent_run_id: str | None
    sector_id: UUID
    package_id: UUID | None
    kosu_turu: str
    duzeltilen_run_id: UUID | None
    durum: str
    sonuc: str
    sebep: str | None
    engine_version: str
    engine_config_sha: str
    content_sha: str
    decision_log_sha: str
    final_candidate: Mapping
    final_decision_log: tuple[Mapping, ...]
    policy_report: Mapping
    barrier_report: Mapping
    engine_diff: Mapping
    approval_snapshot: Mapping | None
    approval_karar: str | None
    snapshot_sha: str | None
    katman1_attestation: Mapping | None
    katman2_attestation: Mapping | None
    readiness_attestation: Mapping | None

    def __post_init__(self) -> None:
        for _alan in (
            "final_candidate",
            "final_decision_log",
            "policy_report",
            "barrier_report",
            "engine_diff",
            "approval_snapshot",
            "katman1_attestation",
            "katman2_attestation",
            "readiness_attestation",
        ):
            object.__setattr__(self, _alan, identity.donmus(getattr(self, _alan)))


@dataclass(frozen=True)
class KosuSatiriGorunumu:
    """`KilitliKosuGorunumu` protokolünü karşılayan HAFİF görünüm.

    `VerifiedRun` YEDİ kapıdan geçmiş bir koşuyu temsil eder; kanıt yükü
    türetmesinin bazı yolları (geri almanın HEDEF koşusu — R11) o kapıları
    İSTEMEZ, yalnız `durum='tamamlandi'` ve tasdik arar. İkinci bir kapı listesi
    yazmamak için ayrı bir TİP kullanılır, gevşetilmiş bir `load_verified_run`
    DEĞİL.
    """

    run_id: str
    sector_id: UUID
    package_id: UUID | None
    durum: str
    sonuc: str
    approval_snapshot: Mapping | None
    katman1_attestation: Mapping | None
    readiness_attestation: Mapping | None


@dataclass(frozen=True)
class AffectedSet:
    """K-145 — bir kural SÜRÜMÜNÜN etkilediği aktif paketlerin sınıflandırması.

    Evren AKTİF paketlerden kurulur: aktif paketi olan HER sektörün o aktif
    paketi, sektör başına TAM BİR satır. Arşivlenmiş ve taslak sürümler evrene
    GİRMEZ — onlar hedef olabilir, konu olamaz.
    """

    engine_version: str
    engine_config_sha: str
    kural_kimligi: str
    kural_surumu: str
    kanitli: tuple[UUID, ...]
    kanitli_etkilenmemis: tuple[UUID, ...]
    ayrilamaz: tuple[UUID, ...]

    def __post_init__(self) -> None:
        for _alan in ("kanitli", "kanitli_etkilenmemis", "ayrilamaz"):
            object.__setattr__(self, _alan, tuple(getattr(self, _alan)))

    @property
    def aday_kume(self) -> tuple[UUID, ...]:
        """Evrenin tamamı — aktif paketi olan her sektörün aktif paketi."""
        return tuple(
            sorted(
                self.kanitli + self.kanitli_etkilenmemis + self.ayrilamaz,
                key=str,
            )
        )

    @property
    def genisletildi(self) -> bool:
        """`ayrilamaz` boş DEĞİLSE küme ADAY KÜMENİN TAMAMINA genişler.

        Kanonik kayıt bunu böyle bağlıyor: ayrım yapılamadığı anda davranış
        koşulsuz toplu geri almayla AYNIdır.
        """
        return bool(self.ayrilamaz)

    @property
    def geri_alinacaklar(self) -> tuple[UUID, ...]:
        return self.aday_kume if self.genisletildi else tuple(sorted(self.kanitli, key=str))

    def sinif(self, package_id: UUID) -> str:
        if package_id in self.kanitli:
            return "kanitli"
        if package_id in self.ayrilamaz:
            return "ayrilamaz"
        if package_id in self.kanitli_etkilenmemis:
            return "kanitli_etkilenmemis"
        raise KeyError(f"paket bu kümede yok: {package_id}")


@dataclass(frozen=True)
class RollbackReport:
    """`execute_rollback_plan`'ın koşum raporu — `hedefsiz` AYRI sayılır."""

    incident_id: str
    tamamlandi: tuple[UUID, ...] = ()
    zaten_tamamlandi: tuple[UUID, ...] = ()
    hedefsiz: tuple[UUID, ...] = ()
    hata: tuple[UUID, ...] = ()
    sebepler: Mapping[str, str] = field(default_factory=dict)


# ─── 1. Koşu satırı ─────────────────────────────────────────────────────────


def _require_run_id(run_id: Any, label: str = "run_id") -> str:
    if type(run_id) is not str or not _RUN_ID_RE.match(run_id):
        raise ValueError(
            f"{label} şekil kapısından geçmedi: {run_id!r} — koşu klasörü adı bu "
            "değerden türetilir (K-17), yol ayracı ve boş ad kabul edilmez"
        )
    return run_id


def new_run_id(prefix: str = "kosu") -> str:
    """Yeni bir koşu kimliği üretir. İkinci bir kimlik uzayı (`attempt`) YOKTUR."""
    return f"{prefix}-{uuid.uuid4().hex}"


def run_folder(run_id: str) -> Path:
    """Koşu klasörü — `<araştırma deposu>/kosu/<run_id>/` (K-17).

    Klasör adı DB `run_id`'sine EŞİTTİR; iki kimlik uzayı yoktur.
    """
    return ARASTIRMA_DEPOSU_KOKU / "kosu" / _require_run_id(run_id)


async def anchor_run(db, *, run_id: str) -> UUID:
    """Koşunun sektörünü KİLİTSİZ okur ve SEKTÖR ÇAPASINI alır; sektörü döner.

    Çapanın tanımı `sector_package_lifecycle.anchor_sector`'dadır ve TEK
    yerdedir; burası yalnız koşu-anahtarlı GİRİŞİDİR. İkinci bir tanım
    yazılsaydı iki kural iki davranış olurdu.

    Bu giriş `approval` için de zorunludur: o modül yapısal olarak yaşam
    döngüsünü import EDEMEZ (Task 14 hükmü) ama paket satırını kilitler, yani
    aynı çapayı almak zorundadır. Kural burada kırılmaz, yalnız taşınır.

    **Kilitsiz arama bilinçlidir:** çapayı seçebilmek için sektörü önce bilmek
    gerekir. Yanlış çapa seçilirse satır çapadan SONRA yeniden okunur ve kimlik
    doğrulanmadan hiçbir geçiş olmaz.
    """
    _require_run_id(run_id)
    sector_id = await db.fetchval(
        "SELECT sector_id FROM social.sector_package_runs WHERE run_id = $1", run_id
    )
    if sector_id is None:
        raise RunNotVerified(f"koşu satırı yok: {run_id!r}")
    await anchor_sector(db, sector_id)
    return sector_id


async def open_run(
    db,
    *,
    sector_id: UUID,
    run_id: str,
    kosu_turu: str,
    parent_run_id: str | None = None,
) -> UUID:
    """Koşu satırını `durum='calisiyor'`, `sonuc=NULL` ile açar.

    `kosu_turu` ZORUNLUDUR ve KAPALI kümedendir (arayüz eki R2: `NOT NULL` her
    kolonun adı konmuş bir üreticisi olur). `duzeltme` değerini bu fonksiyon
    KENDİ reddeder: o değer `duzeltilen_run_id` gerektirir (036 CHECK) ve onu
    yalnız `open_correction_run` yazar.

    `parent_run_id` DOLU ise (yeniden koşum, K-83) satır ana koşudan `kosu_turu` ·
    `duzeltilen_run_id` · `package_id` üçlüsünü DEVRALIR; açıkça verilen
    `kosu_turu` ana koşununkinden farklıysa çağrı REDDEDİLİR.
    """
    _require_run_id(run_id)
    if kosu_turu not in KOSU_TURLERI:
        raise ValueError(
            f"kosu_turu kapalı kümenin dışında: {kosu_turu!r} — "
            f"kabul edilenler: {list(KOSU_TURLERI)}"
        )

    devralinan_turu = kosu_turu
    duzeltilen_run_id: UUID | None = None
    package_id: UUID | None = None

    async with db.transaction():
        if parent_run_id is not None:
            _require_run_id(parent_run_id, "parent_run_id")
            ana = await db.fetchrow(
                "SELECT kosu_turu, duzeltilen_run_id, package_id, sector_id "
                "FROM social.sector_package_runs WHERE run_id = $1 FOR UPDATE",
                parent_run_id,
            )
            if ana is None:
                raise ValueError(f"ana koşu bulunamadı: {parent_run_id!r}")
            if ana["kosu_turu"] != kosu_turu:
                raise ValueError(
                    "yeniden koşum ana koşunun türünü DEVRALIR: ana "
                    f"{ana['kosu_turu']!r}, verilen {kosu_turu!r} — hedef "
                    "tutarlılığı servis katmanında zorlanır"
                )
            devralinan_turu = ana["kosu_turu"]
            duzeltilen_run_id = ana["duzeltilen_run_id"]
            package_id = ana["package_id"]
        elif kosu_turu == "duzeltme":
            raise ValueError(
                "open_run 'duzeltme' türünü açamaz — o tür `duzeltilen_run_id` "
                "gerektirir ve onu yalnız open_correction_run yazar (K-106)"
            )

        return await db.fetchval(
            "INSERT INTO social.sector_package_runs "
            "(run_id, parent_run_id, sector_id, durum, kosu_turu, "
            " duzeltilen_run_id, package_id) "
            "VALUES ($1, $2, $3, 'calisiyor', $4, $5, $6) RETURNING id",
            run_id,
            parent_run_id,
            sector_id,
            devralinan_turu,
            duzeltilen_run_id,
            package_id,
        )


async def new_retry_run_id(db, *, parent_run_id: str) -> str:
    """K-83 — YENİ bir `run_id` üretir ve `parent_run_id` ile ilkine bağlar.

    Sonek üreten `next_attempt` KALDIRILDI: ikinci bir kimlik uzayı açıyordu
    (teknik karar 23).
    """
    _require_run_id(parent_run_id, "parent_run_id")
    ana = await db.fetchrow(
        "SELECT sector_id, kosu_turu FROM social.sector_package_runs WHERE run_id = $1",
        parent_run_id,
    )
    if ana is None:
        raise ValueError(f"ana koşu bulunamadı: {parent_run_id!r}")

    yeni = new_run_id()
    await open_run(
        db,
        sector_id=ana["sector_id"],
        run_id=yeni,
        kosu_turu=ana["kosu_turu"],
        parent_run_id=parent_run_id,
    )
    return yeni


# ─── 2. Ham artefakt (salt-ekleme) ──────────────────────────────────────────

_DAMGA_ALANLARI: tuple[str, ...] = ("model", "surum", "tarih", "girdi_ozeti")
_DAMGA_RE = re.compile(
    r"model=(?P<model>[^;=]+);\s*surum=(?P<surum>[^;=]+);\s*"
    r"tarih=(?P<tarih>[^;=]+);\s*girdi_ozeti=(?P<girdi_ozeti>[^;=]+)"
)
"""Damganın TAM grameri — `fullmatch` ile uygulanır.

**Çapasız ayrıştırıcı KİMLİK otoritesi olamaz (hakem turu 2, yüksek).** Önceki
biçim `finditer` + sözlük kurgusuydu: tekrar eden `model` alanında SON değer
kazanıyor, bilinmeyen alanlar ve önek/sonek artıkları sessizce yok sayılıyordu.
Hazırlık listesi (Task 17) bu çıktıyı ÜRETİCİ KİMLİĞİ olarak tükettiği andan
itibaren belirsiz iki damga "iki ayrı hakem" diye okunabilir hâle geldi.

Değerlerde `=` KABUL EDİLMEZ: `girdi_ozeti` serbest bir özet olsa da eşittir
işareti alan sınırını belirsizleştirir ve sonek artığını değere gizlerdi.
"""

ARTEFAKT_TURLERI: tuple[str, ...] = ("research", "review", "synthesis")
"""`sector_research_artifacts.kind`in KAPALI kümesi — migration 032'nin CHECK'i.

Değerler ŞEMANIN aynasıdır; `tests/test_pipeline_runs.py` ikisinin eşitliğini
migration dosyasından okuyarak doğrular (ikinci kanonik liste yazılmaz).
"""


def parse_stamp(source: str) -> dict[str, str]:
    """K-80 damgasını ayrıştırır: `model=… ; surum=… ; tarih=… ; girdi_ozeti=…`.

    Damga `source` alanında taşınır çünkü 036'nın `UNIQUE (run_id, source, kind)`
    kısıtı zaten oradadır: damga kimliğin PARÇASIDIR, yanına iliştirilmiş bir
    açıklama değil.
    """
    if type(source) is not str:
        raise ArtifactStampMissing("source metin olmalı")
    eslesme = _DAMGA_RE.fullmatch(source.strip())
    if eslesme is None:
        raise ArtifactStampMissing(
            "K-80 tekrar-üretilebilirlik damgası kanonik biçimde DEĞİL — beklenen "
            "'model=<...>; surum=<...>; tarih=YYYY-MM-DD; girdi_ozeti=<...>'; "
            "tekrar eden alan, bilinmeyen alan ve artık metin REDDEDİLİR"
        )
    bulunan = {ad: eslesme.group(ad).strip() for ad in _DAMGA_ALANLARI}
    eksik = [ad for ad in _DAMGA_ALANLARI if not bulunan.get(ad)]
    if eksik:
        raise ArtifactStampMissing(
            f"K-80 tekrar-üretilebilirlik damgası eksik: {eksik}"
        )
    try:
        date.fromisoformat(bulunan["tarih"])
    except ValueError as hata:
        raise ArtifactStampMissing(
            f"K-80 damgasının tarihi ISO biçiminde değil: {bulunan['tarih']!r}"
        ) from hata
    return {ad: bulunan[ad] for ad in _DAMGA_ALANLARI}


def build_stamp(*, model: str, surum: str, tarih: str, girdi_ozeti: str) -> str:
    """Kanonik damga metnini üretir — ikinci bir biçim yazılmaz."""
    return (
        f"model={model}; surum={surum}; tarih={tarih}; girdi_ozeti={girdi_ozeti}"
    )


async def record_artifact(
    db,
    *,
    run_id: str,
    sector_slug: str,
    kind: str,
    source: str,
    content_md: str,
    brief_ref: str | None = None,
) -> UUID:
    """Ham artefaktı SALT-EKLEME katmanına yazar; kimliğini döner.

    K-80 damgası ZORUNLUDUR — eksikse satır hiç yazılmaz. K-09 (aynı
    `(run_id, source, kind)` ikinci kez yazılamaz) veritabanı kısıtıdır ve bu
    fonksiyon onu YUTMAZ: benzersizlik ihlali çağırana ulaşır.
    """
    _require_run_id(run_id)
    parse_stamp(source)
    if kind not in ARTEFAKT_TURLERI:
        # DEĞİŞMEZ, kural DEĞİL (hakem turu 2): kapıyı bir test taramasına
        # bırakmak dolaylı çağrı biçimlerini (takma ad, `**kwargs`) görmüyordu.
        raise ValueError(
            f"şemanın kabul etmediği artefakt türü: {kind!r} — "
            f"kabul edilenler: {list(ARTEFAKT_TURLERI)}"
        )
    return await db.fetchval(
        "INSERT INTO social.sector_research_artifacts "
        "(run_id, sector_slug, kind, source, brief_ref, content_md) "
        "VALUES ($1, $2, $3, $4, $5, $6) RETURNING id",
        run_id,
        sector_slug,
        kind,
        source,
        brief_ref,
        content_md,
    )


# ─── 3. Yarım koşu (K-82) + yerel arıza bildirimi ──────────────────────────


async def mark_incomplete(db, *, run_id: str, asama: str, sebep: str) -> None:
    """K-82 — yarım koşuyu işaretler ve AYNI işlemde yönetici bildirimi yazar.

    `asama` ZORUNLU ve KAPALIDIR: bildirim anahtarı "koşu + aşama"dır, aşama
    olmadan anahtar üretilemez.

    **Yönetici bildirimi neden burada:** n8n `errorWorkflow` yalnız workflow'un
    KENDİ arızasını yakalar — yerel CLI zaman aşımı, sıfırdan farklı çıkış ya da
    K-127 kaynak-tabanı duruşu ORAYA HİÇ ULAŞMAZ. Bu yol olmadan yarım tur
    yalnız veritabanında ve günlükte kalırdı.

    Olay yükü maskeleme süzgecinden geçer (K-136); dosya EZİLMEZ.
    """
    _require_run_id(run_id)
    if asama not in ASAMALAR:
        raise ValueError(
            f"asama kapalı kümenin dışında: {asama!r} — kabul edilenler: {list(ASAMALAR)}"
        )

    async with db.transaction():
        guncellendi = await db.fetchval(
            "UPDATE social.sector_package_runs "
            "SET durum = 'tamamlanmadi', sebep = $2 "
            "WHERE run_id = $1 RETURNING id",
            run_id,
            sebep,
        )
        if guncellendi is None:
            raise ValueError(f"koşu bulunamadı: {run_id!r}")

        await record_admin_event(
            db,
            kind=TUR_ARIZASI_OLAYI,
            payload=mask_payload(
                {"run_id": run_id, "asama": asama, "sebep": sebep}
            ),
            idempotency_key=f"{run_id}:{asama}",
        )
    log_run(run_id, f"asama={asama} yarım kaldı: {sebep}", level=logging.WARNING)


# ─── 4. Motor sonucu (K-24 · K-93 · F19) ────────────────────────────────────

_SONUC_KOLON_ESLEMESI: tuple[tuple[str, str], ...] = (
    ("sonuc", "sonuc"),
    ("sebep", "sebep"),
    ("engine_version", "engine_version"),
    ("engine_config_sha", "engine_config_sha"),
    ("policy_report", "policy_report"),
    ("barrier_report", "barrier_report"),
    ("engine_diff", "engine_diff"),
    ("final_candidate", "final_candidate"),
    ("final_decision_log", "final_decision_log"),
    ("content_sha", "content_sha"),
    ("decision_log_sha", "decision_log_sha"),
)
"""`EngineResult` alanı → koşu satırı kolonu — BİREBİR, on bir çift.

`EngineResult`'ta bulunup satıra yazılmayan alan YOKTUR; satırda bulunup
`EngineResult`'tan gelmeyen motor-türevi kolon da YOKTUR. Eşleme burada
adlandırıldığı için bir alanın sessizce düşmesi imza sorunu değil ALAN-KÜMESİ
sorunudur ve testi vardır.
"""

def _coz(value: Any) -> Any:
    """Donmuş yükü JSON'a yazılabilir düz yapıya ÇÖZER.

    `EngineResult` alanları `identity.donmus`'tan geçtiği için `MappingProxyType`
    ve `tuple` taşırlar; asyncpg'nin jsonb kodlayıcısı `json.dumps`'tır ve
    `mappingproxy`yi serileştiremez (ölçüldü: `TypeError`).

    **Kural artık BURADA DEĞİL** (2026-09-09): çözme, dondurmanın tersidir ve
    ikisi bir çifttir; `identity.cozulmus` tek evdir. Bu ad yalnız çağıranların
    okunabilirliği için duruyor ve kendi dönüşümünü YAZMAZ — ikinci bir kopya
    iki kuralın sürüm sürüm ayrışması demekti.
    """
    return identity.cozulmus(value)


F19_ALANLARI: tuple[str, ...] = (
    "final_candidate",
    "final_decision_log",
    "content_sha",
    "decision_log_sha",
)


async def record_result(db, *, run_id: str, result: EngineResult) -> None:
    """Motor sonucunu koşu satırına yazar ve AYNI ifadede `durum='tamamlandi'` yapar.

    İmzada `**report_fields` ya da serbest sözlük parametresi YOKTUR: koşu
    satırına yazılan HER motor-türevi kolon `EngineResult`'ın adı konmuş ve
    kapalı bir alanından okunur (arayüz eki R2).

    `no_change`/`blocked` dâhil HER koşu satır yazar (K-93), paket satırı
    üretmeden. `barrier_report` üç sonuçta da ZORUNLUDUR (K-24). F19:
    `activation_eligible` iken dört köken alanı BİRLİKTE yazılır; biri eksikse
    yazım REDDEDİLİR — yarım köken kaydı yoktur.

    **Yazım KARŞILAŞTIR-VE-YAZ'dır (fix turu 1, F3):** yalnız
    `durum='calisiyor'` ve `sonuc IS NULL` iken koşar. Kaybeden ya da tekrar
    eden yazıcı REDDEDİLİR; yarım koşu işareti (K-82) de EZİLEMEZ.
    """
    _require_run_id(run_id)
    if type(result) is not EngineResult:
        raise TypeError(
            f"result EngineResult olmalı ({type(result).__name__} verildi) — "
            "benzer alan taşıyan nesne motor sonucu yerine geçmez"
        )
    if result.barrier_report is None:
        raise ValueError(
            "barrier_report ZORUNLUDUR (K-24) — üç sonucun üçünde de; "
            "metriksiz tamamlanmış koşu yazılmaz"
        )
    if not result.engine_version or not result.engine_config_sha:
        raise ValueError(
            "engine_version ve engine_config_sha üç sonuçta da ZORUNLUDUR (K-97)"
        )
    if result.sonuc == "activation_eligible":
        eksik = [
            ad for ad in F19_ALANLARI if getattr(result, ad) in (None, (), {})
        ]
        if eksik:
            raise ValueError(
                f"F19: activation_eligible sonuçta {eksik} alanları AYNI işlemde "
                "yazılmak ZORUNDA — yarım köken kaydı yoktur"
            )

    degerler = {
        kolon: _coz(getattr(result, alan)) for alan, kolon in _SONUC_KOLON_ESLEMESI
    }
    degerler["policy_report"] = result.policy_report.as_payload()

    kolonlar = [kolon for _alan, kolon in _SONUC_KOLON_ESLEMESI]
    atamalar = ", ".join(f"{kolon} = ${i + 2}" for i, kolon in enumerate(kolonlar))
    # KARŞILAŞTIR-VE-YAZ (fix turu 1, F3). Koşul YALNIZ `run_id` olsaydı yazım
    # SON-YAZAN-KAZANIR olurdu: iki eşzamanlı tamamlama birbirini ezer ve
    # SONRAKİ herhangi bir çağrı, tamamlanmış — hatta onaylanmış — bir koşunun
    # bütün motor alanlarını değiştirebilirdi. Migration yalnız onay anlık
    # görüntüsünü koruyor (K-98), motor sonuç alanlarını DEĞİL.
    guncellendi = await db.fetchval(
        "UPDATE social.sector_package_runs "
        f"SET durum = 'tamamlandi', {atamalar} "
        "WHERE run_id = $1 AND durum = 'calisiyor' AND sonuc IS NULL "
        "RETURNING id",
        run_id,
        *[degerler[kolon] for kolon in kolonlar],
    )
    if guncellendi is None:
        # Kaybeden/tekrarlayan yazıcı ile OLMAYAN koşu AYRI iki hatadır; tek
        # mesaj ikisini birbirine karıştırırdı.
        mevcut = await db.fetchrow(
            "SELECT durum, sonuc FROM social.sector_package_runs WHERE run_id = $1",
            run_id,
        )
        if mevcut is None:
            raise ValueError(f"koşu bulunamadı: {run_id!r}")
        raise ValueError(
            f"koşu sonucu ZATEN yazılmış: {run_id!r} "
            f"durum={mevcut['durum']!r}, sonuc={mevcut['sonuc']!r} — yazım "
            "yalnız 'calisiyor' ve sonucu boş satıra yapılır"
        )


# ─── 5. TEK KAPI LİSTESİ — load_verified_run ───────────────────────────────

KAPILAR: tuple[str, ...] = (
    "durum",
    "sonuc",
    "engine_version",
    "engine_config_sha",
    "content_sha",
    "final_decision_log",
    "decision_log_sha",
)
"""YEDİ kapı — ikinci bir liste yazmak mümkün değildir."""


def _kapi_ihlalleri(row: Mapping[str, Any]) -> list[str]:
    """YEDİ kapının HANGİLERİNİN düştüğünü döner — kapı listesi TEK yerdedir."""
    ihlaller: list[str] = []
    if row["durum"] != "tamamlandi":
        ihlaller.append(f"durum={row['durum']!r} (beklenen 'tamamlandi')")
    if row["sonuc"] != "activation_eligible":
        ihlaller.append(f"sonuc={row['sonuc']!r} (beklenen 'activation_eligible')")
    if not row["engine_version"]:
        ihlaller.append("engine_version boş")
    if not row["engine_config_sha"]:
        ihlaller.append("engine_config_sha boş")

    aday = row["final_candidate"]
    if aday is None:
        ihlaller.append("final_candidate boş")
    elif row["content_sha"] != identity.canonical_sha(aday):
        ihlaller.append("content_sha final_candidate ile eşleşmiyor")

    gunluk = row["final_decision_log"]
    if not gunluk:
        ihlaller.append("final_decision_log boş")
    elif row["decision_log_sha"] != identity.canonical_sha(gunluk):
        ihlaller.append("decision_log_sha karar günlüğü ile eşleşmiyor")
    return ihlaller


async def load_verified_run(db, *, run_id: str, for_update: bool = True) -> VerifiedRun:
    """Koşu satırını KİLİTLİ okur ve YEDİ kapının tamamını uygular.

    Yazım · güncelleme · onay · aktivasyon DÖRDÜ DE bunu çağırır; hiçbiri kendi
    kapı listesini taşımaz. Kapılardan biri düşerse `RunNotVerified`.
    """
    _require_run_id(run_id)
    row = await db.fetchrow(
        "SELECT * FROM social.sector_package_runs WHERE run_id = $1"
        + (" FOR UPDATE" if for_update else ""),
        run_id,
    )
    if row is None:
        raise RunNotVerified(f"koşu satırı yok: {run_id!r}")

    ihlaller = _kapi_ihlalleri(row)
    if ihlaller:
        raise RunNotVerified(
            f"koşu {run_id!r} doğrulanmadı — düşen kapılar: " + " · ".join(ihlaller)
        )

    return VerifiedRun(
        id=row["id"],
        run_id=row["run_id"],
        parent_run_id=row["parent_run_id"],
        sector_id=row["sector_id"],
        package_id=row["package_id"],
        kosu_turu=row["kosu_turu"],
        duzeltilen_run_id=row["duzeltilen_run_id"],
        durum=row["durum"],
        sonuc=row["sonuc"],
        sebep=row["sebep"],
        engine_version=row["engine_version"],
        engine_config_sha=row["engine_config_sha"],
        content_sha=row["content_sha"],
        decision_log_sha=row["decision_log_sha"],
        final_candidate=row["final_candidate"],
        final_decision_log=tuple(row["final_decision_log"]),
        policy_report=row["policy_report"] or {},
        barrier_report=row["barrier_report"],
        engine_diff=row["engine_diff"] or {},
        approval_snapshot=row["approval_snapshot"],
        approval_karar=row["approval_karar"],
        snapshot_sha=row["snapshot_sha"],
        katman1_attestation=row["katman1_attestation"],
        katman2_attestation=row["katman2_attestation"],
        readiness_attestation=row["readiness_attestation"],
    )


# ─── 6. Kapı tasdikleri (F18) ───────────────────────────────────────────────


async def _write_attestation(db, *, run_id: str, kolon: str, payload: dict) -> None:
    guncellendi = await db.fetchval(
        f"UPDATE social.sector_package_runs SET {kolon} = "
        "$2 || jsonb_build_object('at', now()) "
        "WHERE run_id = $1 RETURNING id",
        run_id,
        payload,
    )
    if guncellendi is None:
        raise ValueError(f"koşu bulunamadı: {run_id!r}")


async def attest_katman1(
    db, *, run_id: str, kosum_kimligi: str, sonuc: str, actor: str
) -> None:
    """F18 — Katman-1 tasdikinin ADLANDIRILMIŞ üreticisi.

    Tasdik KANITTIR, boolean değil: hangi koşum · hangi sonuç · kim · ne zaman.
    Aktivasyon bu satırdan okur; adaptörün boolean uydurabileceği yol kapanır.
    """
    _require_run_id(run_id)
    owner = require_actor(actor)
    if type(sonuc) is not str or not sonuc.strip():
        raise ValueError("katman1 sonucu zorunlu")
    await _write_attestation(
        db,
        run_id=run_id,
        kolon="katman1_attestation",
        payload={"kosum_kimligi": kosum_kimligi, "sonuc": sonuc, "actor": owner},
    )


async def attest_katman2(
    db, *, run_id: str, kosum_kimligi: str, ozet: str, actor: str
) -> None:
    """Katman-2'nin KOŞULDUĞU ve SUNULDUĞU kanıtı — sonucu KAPI DEĞİLDİR.

    Spec §10.2 ikisini ayırır: koşulması ve sunulması ön koşuldur, sonucu
    başarısızlık koşulu üretmez. Aktivasyon bu satırın VARLIĞINA bakar,
    `ozet`in içeriğine BAKMAZ.
    """
    _require_run_id(run_id)
    owner = require_actor(actor)
    await _write_attestation(
        db,
        run_id=run_id,
        kolon="katman2_attestation",
        payload={
            "kosum_kimligi": kosum_kimligi,
            "ozet": ozet,
            "actor": owner,
            "sunuldu": True,
        },
    )


async def attest_readiness(
    db,
    *,
    run_id: str,
    kapi_maddeleri: tuple[str, ...],
    sinyal_maddeleri: tuple[str, ...],
    actor: str,
) -> None:
    """F18 — operatörün TEK onayını koşu satırına kalıcı yazar (arayüz eki R9/H5).

    **`onaylandi` PARAMETRE DEĞİLDİR — burada TÜRETİLİR:**
    `set(kapi_maddeleri) == readiness_items.KAPI_MADDELERI`. Parametre olsaydı
    herhangi bir iç çağıran `onaylandi=True, kapi_maddeleri=()` yazıp K-69
    kapısını atlayabilirdi.

    BEŞ koşuldan biri düşerse kayıt hiç YAZILMAZ (`ReadinessAttestationRefused`);
    sessiz `onaylandi=False` kaydı da ÜRETİLMEZ:
      (1) `kapi_maddeleri` BOŞ; (2) eksik kapı maddesi; (3) tanınmayan kimlik;
      (4) yanlış sınıf (iki yönde de); (5) tekrar eden kimlik.
    """
    _require_run_id(run_id)
    owner = require_actor(actor)

    kapi = tuple(kapi_maddeleri)
    sinyal = tuple(sinyal_maddeleri)

    if len(set(kapi)) != len(kapi) or len(set(sinyal)) != len(sinyal):
        raise ReadinessAttestationRefused("hazırlık maddesi TEKRAR EDİYOR")
    if not kapi:
        raise ReadinessAttestationRefused("kapı maddesi kümesi BOŞ — onay türetilemez")

    taninmayan = sorted((set(kapi) | set(sinyal)) - readiness_items.MADDE_KIMLIKLERI)
    if taninmayan:
        raise ReadinessAttestationRefused(f"tanınmayan hazırlık maddesi: {taninmayan}")

    yanlis_sinif = sorted(
        [m for m in kapi if readiness_items.sinif(m) != "kapi"]
        + [m for m in sinyal if readiness_items.sinif(m) != "sinyal"]
    )
    if yanlis_sinif:
        raise ReadinessAttestationRefused(
            f"madde yanlış sınıfta verildi: {yanlis_sinif}"
        )

    eksik = sorted(readiness_items.KAPI_MADDELERI - set(kapi))
    if eksik:
        raise ReadinessAttestationRefused(f"eksik kapı maddesi: {eksik}")

    await _write_attestation(
        db,
        run_id=run_id,
        kolon="readiness_attestation",
        payload={
            "onaylandi": True,
            "actor": owner,
            "kapi_maddeleri": sorted(kapi),
            "sinyal_maddeleri": sorted(sinyal),
            "madde_kumesi_sha": readiness_items.MADDE_KUMESI_SHA,
        },
    )


# ─── 7. Düzeltme turu (K-106/K-72) ──────────────────────────────────────────


async def open_correction_run(db, *, parent_run_id: str, actor: str) -> str:
    """Reddedilmiş ana koşudan düzeltme turu açar; YENİ `run_id` döner.

    Ana koşuyu KİLİTLER (`approval_karar='ret'` değilse REDDEDER),
    `package_id`'sini KOPYALAR, `kosu_turu='duzeltme'` + `duzeltilen_run_id`
    yazar.

    **Aynı anda TEK açık düzeltme (NEW-3).** Hedef taslak için sonuçlanmamış bir
    düzeltme koşusu varsa yenisi AÇILMAZ; aksi hâlde iki düzeltme aynı taslağı
    yazabilir ve biri diğerinin onayladığı baytları ezerdi. "Sonuçlanmış" =
    kararı var (`onay`/`ret`) ya da `durum='tamamlanmadi'`.
    """
    _require_run_id(parent_run_id, "parent_run_id")
    owner = require_actor(actor)

    async with db.transaction():
        # ÇAPA BURADA YOK — ve gerekçesi hakem turu 4'te DÜZELTİLDİ.
        #
        # ÖNCEKİ GEREKÇE YANLIŞTI: "bu fonksiyon hiçbir paket satırı kilitlemez"
        # diyordu. Ölçüldü ki YANLIŞ — satır `package_id` yabancı anahtarını
        # taşıyor, dolayısıyla PostgreSQL ekleme sırasında EBEVEYN paket satırına
        # örtük bir `KEY SHARE` kilidi alır. Kaynakta görünmeyen bir kilit
        # kenarıdır ve çapa sözleşmesinin tarayıcısı onu MODELLEMEZ.
        #
        # ÇAPANIN OLMAMASININ GERÇEK GEREKÇESİ (hakem turu 4'te izlendi): bugün
        # bu kenarın TERSİ YOKTUR — çapalı yollar paket satırını `FOR UPDATE` ile
        # alır ve bu fonksiyonun tuttuğu örtük kilidi bekler; bu fonksiyon ise
        # çapalı yolların tuttuğu hiçbir şeyi beklemez. Grafik döngüsüzdür.
        # Buraya savunma amaçlı bir çapa eklemek onu SAHTE-YEŞİL bir kapı yapardı
        # (mutasyon ölçtü: hiçbir test varlığını görmüyordu).
        #
        # KALAN RİSK DÜRÜSTÇE: gelecekte ters bir kenar eklenirse tarayıcı bunu
        # GÖREMEZ. Sınır `tests/test_lock_anchor_contract.py` başında yazılıdır.
        ana = await db.fetchrow(
            "SELECT id, sector_id, package_id, approval_karar "
            "FROM social.sector_package_runs WHERE run_id = $1 FOR UPDATE",
            parent_run_id,
        )
        if ana is None:
            raise CorrectionRunRefused(f"ana koşu bulunamadı: {parent_run_id!r}")
        if ana["approval_karar"] is None:
            raise CorrectionRunRefused(
                f"ana koşunun kararı YOK ({parent_run_id!r}) — düzeltme turu yalnız "
                "REDDEDİLMİŞ koşudan açılır"
            )
        if ana["approval_karar"] != "ret":
            raise CorrectionRunRefused(
                f"ana koşunun kararı {ana['approval_karar']!r} — düzeltme turu yalnız "
                "'ret' kararından açılır (K-72)"
            )
        if ana["package_id"] is None:
            raise CorrectionRunRefused(
                "ana koşunun taslak bağı YOK — düzeltilecek hedef belirsiz (K-106)"
            )

        acik = await db.fetchval(
            "SELECT run_id FROM social.sector_package_runs "
            "WHERE package_id = $1 AND kosu_turu = 'duzeltme' "
            "  AND approval_karar IS NULL AND durum <> 'tamamlanmadi' "
            "LIMIT 1",
            ana["package_id"],
        )
        if acik is not None:
            raise CorrectionRunRefused(
                f"bu taslak için sonuçlanmamış bir düzeltme turu VAR ({acik!r}) — "
                "iki düzeltme aynı taslağı yazamaz"
            )

        yeni = new_run_id("duzeltme")
        await db.execute(
            "INSERT INTO social.sector_package_runs "
            "(run_id, sector_id, durum, kosu_turu, duzeltilen_run_id, package_id) "
            "VALUES ($1, $2, 'calisiyor', 'duzeltme', $3, $4)",
            yeni,
            ana["sector_id"],
            ana["id"],
            ana["package_id"],
        )

    log_run(yeni, f"duzeltme turu acildi (ana={parent_run_id}, actor={owner})")
    return yeni


# ─── 8. K-145 — etkilenen paketler ──────────────────────────────────────────


def _damgali_motor_karari(
    decision_log: Any, *, kural_kimligi: str, kural_surumu: str
) -> bool:
    """Uygulanmış motor kararlarından en az biri o kural SÜRÜMÜYLE damgalı mı?

    Karar TÜRÜ fark etmez: `cikar` ve `kirp` yaşayan kümede olmasa da etkilenmiş
    sayılır — kalıbı listeden çıkaran bir karar da arızalı kuralın ürünüdür.
    """
    if not isinstance(decision_log, (list, tuple)):
        return False
    for satir in decision_log:
        if not isinstance(satir, Mapping):
            continue
        if satir.get("tur") != "karar" or satir.get("aktor") != "motor":
            continue
        if (
            satir.get("kural_kimligi") == kural_kimligi
            and satir.get("kural_surumu") == kural_surumu
        ):
            return True
    return False


def _koken_okunabilir(run_row: Mapping[str, Any] | None) -> bool:
    """Köken okunabilir mi: koşu satırı var · `tamamlandi` · günlük okunabilir."""
    if run_row is None:
        return False
    if run_row["durum"] != "tamamlandi":
        return False
    gunluk = run_row["final_decision_log"]
    if not isinstance(gunluk, (list, tuple)) or not gunluk:
        return False
    return not identity.validate_decision_log(list(gunluk))


async def _paket_kokeni(db, package_row: Mapping[str, Any]):
    """Paketin `run_id` bağından koşu satırını okur (yoksa `None`)."""
    if not package_row["run_id"]:
        return None
    return await db.fetchrow(
        "SELECT * FROM social.sector_package_runs WHERE run_id = $1",
        package_row["run_id"],
    )


async def affected_packages(
    db,
    *,
    engine_version: str,
    engine_config_sha: str,
    kural_kimligi: str,
    kural_surumu: str,
) -> AffectedSet:
    """K-145 — bir kural SÜRÜMÜNÜN etkilediği AKTİF paketleri sınıflandırır.

    **Olay girdisi kapalı DÖRTLÜDÜR** — dördü de zorunludur; sürüm olmadan aynı
    kuralın iki sürümü ayrışmaz ve doğru sürümle üretilmiş paketler de geri
    alınırdı.

    **Evren AKTİF paketlerden kurulur.** Kökene dayalı bir evren, tam da
    `ayrilamaz` sınıfının saydığı vakaları (koşu satırı yok · `package_id` boş)
    dışarıda bırakırdı ve güvenli genişleme HİÇ ateşlenmezdi.

    Motorda DEĞİL burada: motor saf kalır, bu fonksiyon koşu kayıtlarını okur.
    """
    for ad, deger in (
        ("engine_version", engine_version),
        ("engine_config_sha", engine_config_sha),
        ("kural_kimligi", kural_kimligi),
        ("kural_surumu", kural_surumu),
    ):
        if type(deger) is not str or not deger.strip():
            raise ValueError(
                f"{ad} zorunlu — olay girdisi kapalı DÖRTLÜDÜR, eksik ayak kabul edilmez"
            )

    adaylar = await db.fetch(
        "SELECT id, sector_id, version, run_id FROM social.sector_packages "
        "WHERE status = 'active' ORDER BY sector_id"
    )

    kanitli: list[UUID] = []
    etkilenmemis: list[UUID] = []
    ayrilamaz: list[UUID] = []

    for paket in adaylar:
        kosu = await _paket_kokeni(db, paket)
        if not _koken_okunabilir(kosu):
            ayrilamaz.append(paket["id"])
            continue
        damgali_motor = (
            kosu["engine_version"] == engine_version
            and kosu["engine_config_sha"] == engine_config_sha
        )
        if damgali_motor and _damgali_motor_karari(
            kosu["final_decision_log"],
            kural_kimligi=kural_kimligi,
            kural_surumu=kural_surumu,
        ):
            kanitli.append(paket["id"])
        else:
            etkilenmemis.append(paket["id"])

    return AffectedSet(
        engine_version=engine_version,
        engine_config_sha=engine_config_sha,
        kural_kimligi=kural_kimligi,
        kural_surumu=kural_surumu,
        kanitli=tuple(kanitli),
        kanitli_etkilenmemis=tuple(etkilenmemis),
        ayrilamaz=tuple(ayrilamaz),
    )


# ─── 9. Olay kilidi ve kapsam mührü ─────────────────────────────────────────


def _require_transaction(db, label: str) -> None:
    """Çağıran AÇIK bir işlemin İÇİNDE olmak ZORUNDADIR (fix turu 1, F4).

    Bu modülün kanıt üreticileri işlem-ömürlü kilitlere dayanır: olayın danışma
    kilidi (`_lock_incident`) ve satırların `FOR UPDATE`'i. Otomatik-commit altında
    ikisi de KENDİ İFADELERİNİN sonunda düşer — yani fonksiyon kapsamı
    doğrulayıp, üyelik değişimiyle yarışıp, ESKİ kapsama bağlı bir jeton
    bastırıp kilitler bırakıldıktan sonra kanıt döndürebilirdi. Fonksiyonlar
    dışa açıktır; imzalarına uyan herhangi bir çağıran bu yolu açardı.

    Kapı fail-closed'dur: bağlantı nesnesi bu soruyu CEVAPLAYAMIYORSA da düşer —
    "belki işlemdedir" varsayımı kanıt sayılmaz.

    Fırlatılan tip `execute_rollback_plan`'ın yakaladığı kümede DEĞİLDİR:
    programlama hatası, `durum='hata'` diye rapor edilecek bir paket arızası
    olarak maskelenmez.
    """
    kontrol = getattr(db, "is_in_transaction", None)
    if not callable(kontrol) or not kontrol():
        raise TransactionRequired(
            f"{label} AÇIK bir işlem içinde çağrılmalıdır — otomatik-commit "
            "altında danışma kilidi ve satır kilitleri kendi ifadelerinin "
            "sonunda düşer, kanıt kilitsiz kalırdı"
        )


async def _lock_incident(db, incident_id: str) -> None:
    """Olay kapsamlı, İŞLEM ÖMÜRLÜ danışma kilidi — TEK kilit adı budur.

    Satır düzeyi `FOR UPDATE` kilitleri kalır, ama üyelik/kapsam kararlarının
    serileştirilmesi YALNIZ bunun işidir: yeni bir satırın EKLENMESİ hiçbir satır
    kilidinde görünmez, o pencereyi yalnız olay kilidi kapatır.

    Yeniden giriş serbesttir; dört yol da kilidi KOŞULSUZ alır — "acaba çağıran
    almış mıydı" sorusu sessiz atlamanın kapısıdır.
    """
    await db.execute(
        "SELECT pg_advisory_xact_lock(hashtextextended($1, 0))",
        _OLAY_KILIT_ONEKI + incident_id,
    )


def incident_scope_sha(rows: Sequence[Mapping[str, Any]]) -> str:
    """Olayın DEĞİŞMEZ ÜYELİĞİNİN parmak izi — yürütme durumunun DEĞİL.

    Girdi o olaya ait TÜM plan satırlarıdır, `durum`'dan BAĞIMSIZ. Her satırdan
    yalnız kimlik ve hedef alanları alınır; `durum` ve `reason` hash'e GİRMEZ —
    onlar yürütme durumudur, üyelik değil. Bir satırın tamamlanması kapsamı
    DEĞİŞTİRMEZ, yoksa N satırlı bir olay ilk başarılı geri almadan sonra
    tamamlanamazdı.
    """
    kanonik = [
        {
            "package_id": str(satir["package_id"]),
            "observed_active_version": satir["observed_active_version"],
            "target_version": satir["target_version"],
            "evidence_class": satir["evidence_class"],
        }
        for satir in sorted(rows, key=lambda satir: str(satir["package_id"]))
    ]
    return identity.canonical_sha(kanonik)


async def _incident_rows(db, incident_id: str, *, for_update: bool = False):
    return await db.fetch(
        "SELECT * FROM social.package_rollback_plans WHERE incident_id = $1 "
        "ORDER BY package_id" + (" FOR UPDATE" if for_update else ""),
        incident_id,
    )


# ─── 10. Geri alma planı ────────────────────────────────────────────────────


async def _guvenli_hedef(
    db, *, sector_id: UUID, kural_kimligi: str, kural_surumu: str,
    engine_version: str, engine_config_sha: str,
) -> int | None:
    """İKİ koşul birden: `status='archived'` VE arızalı kural sürümüyle damgasız.

    Planlayıcı hedefi kısıtlamazsa yürütme anında ölecek bir plan satırı yazar —
    Plan 1'in geri alma yordamı hedefin durumunu okur ve `archived` değilse hata
    verir. Koşulamayan plan üreten planlayıcı kabul edilmez.

    Kökeni OKUNAMAYAN arşiv sürümü de hedef olamaz: "damgalanmamış" olduğu
    KANITLANAMADIĞI için güvenli tarafa düşer (fail-closed).
    """
    arsivler = await db.fetch(
        "SELECT id, version, run_id FROM social.sector_packages "
        "WHERE sector_id = $1 AND status = 'archived' ORDER BY version DESC",
        sector_id,
    )
    for aday in arsivler:
        kosu = await _paket_kokeni(db, aday)
        if not _koken_okunabilir(kosu):
            continue
        if (
            kosu["engine_version"] == engine_version
            and kosu["engine_config_sha"] == engine_config_sha
            and _damgali_motor_karari(
                kosu["final_decision_log"],
                kural_kimligi=kural_kimligi,
                kural_surumu=kural_surumu,
            )
        ):
            continue
        return aday["version"]
    return None


async def _plan_satiri_kur(db, affected: AffectedSet, package_id: UUID) -> dict:
    paket = await db.fetchrow(
        "SELECT id, sector_id, version, status FROM social.sector_packages WHERE id = $1",
        package_id,
    )
    if paket is None:
        raise LifecycleError(f"paket bulunamadı: {package_id}")

    hedef = await _guvenli_hedef(
        db,
        sector_id=paket["sector_id"],
        kural_kimligi=affected.kural_kimligi,
        kural_surumu=affected.kural_surumu,
        engine_version=affected.engine_version,
        engine_config_sha=affected.engine_config_sha,
    )
    sinif = affected.sinif(package_id)
    if hedef is None:
        return {
            "package_id": package_id,
            "observed_active_version": paket["version"],
            "target_version": None,
            "evidence_class": sinif,
            "reason": (
                f"{sinif}: güvenli arşiv sürümü YOK — geri alma uydurulmaz, "
                "tek çıkış deaktivasyondur (K-38)"
            ),
            "durum": "hedefsiz",
        }
    return {
        "package_id": package_id,
        "observed_active_version": paket["version"],
        "target_version": hedef,
        "evidence_class": sinif,
        "reason": (
            f"{sinif}: {affected.kural_kimligi}@{affected.kural_surumu} "
            f"(motor {affected.engine_version})"
        ),
        "durum": "bekliyor",
    }


async def _plan_satirini_yaz(db, incident_id: str, satir: Mapping[str, Any]) -> None:
    await db.execute(
        "INSERT INTO social.package_rollback_plans "
        "(incident_id, package_id, observed_active_version, target_version, "
        " evidence_class, reason, durum) "
        "VALUES ($1, $2, $3, $4, $5, $6, $7)",
        incident_id,
        satir["package_id"],
        satir["observed_active_version"],
        satir["target_version"],
        satir["evidence_class"],
        satir["reason"],
        satir["durum"],
    )


async def build_rollback_plan(db, *, affected: AffectedSet, actor: str) -> str:
    """DEĞİŞMEZ bir geri alma planı yazar ve OLAY KİMLİĞİNİ döner.

    **Bu fonksiyon YALNIZ olay AÇAR; mevcut bir olayın üyeliğini DEĞİŞTİRMEZ**
    (imzasında `incident_id` yoktur). Üyelik değişikliğinin yüzeyi ayrıdır:
    `amend_rollback_plan`.

    Sektör başına TEK giriş — aday küme aktif paketlerden kurulduğu için tarihî
    sürümler ayrı satır üretmez. **Hedef sürüm plan anında SABİTLENİR**; tekrar
    denemede yeniden hesaplanırsa ikinci kez geri alma riski doğar.
    """
    owner = require_actor(actor)
    incident_id = f"olay-{uuid.uuid4().hex}"

    async with db.transaction():
        await _lock_incident(db, incident_id)
        for package_id in affected.geri_alinacaklar:
            satir = await _plan_satiri_kur(db, affected, package_id)
            await _plan_satirini_yaz(db, incident_id, satir)

    log_run(
        incident_id,
        f"geri alma plani yazildi (paket={len(affected.geri_alinacaklar)}, actor={owner})",
    )
    return incident_id


async def amend_rollback_plan(
    db, *, incident_id: str, affected: AffectedSet, actor: str
) -> tuple[int, int]:
    """MEVCUT bir olayın üyeliğini YENİDEN YAZAR; olay AÇMAZ. `(eklenen, silinen)`.

    Adımların SIRASI bağlayıcıdır ve hepsi TEK işlemdedir:
      1. `require_actor` — boş kimlikte `ValueError`, hiçbir satır yazılmaz.
      2. `_lock_incident` — HERHANGİ bir `durum`/kapsam OKUMASINDAN ÖNCE.
      3. Olayın TÜM satırları `FOR UPDATE`.
      4. Pencere kapısı: en az bir satır `durum ∈ ('tamamlandi','hata')` ise
         `IncidentMembershipLocked` — hiçbir satır yazılmaz (fail-closed).
      5. Kümede olup satırı olmayanlar EKLENİR; satırı olup kümede olmayanlar
         SİLİNİR (hedef seçimi `build_rollback_plan`'ın kuralının AYNISI).
      6. **Mühürlere DOKUNULMAZ** — `onay_*` YAZILMAZ; üyelik değişince kalan
         damgalar kendiliğinden BAYATLAR ve olay yürütülemez hâle gelir. Yeniden
         mühürleme operatörün ayrı ve GÖRÜNÜR adımıdır (`olay-onayla`).
      7. 0/0 değişiklik başarıyla döner; çağıran bunu hata SAYMAZ.

    **Satır SİLME hard DELETE'tir (R-B'nin açık ayağının Task 8 kararı).** Durum
    değişikliği seçilemezdi: `durum` kapsam parmak izine GİRMEZ, dolayısıyla
    "çıkarıldı" diye işaretlenen bir satır mührü bayatlatmaz ve üyelik küçülmesi
    hiçbir kapıda görünmezdi. Kanıt kaybı SESSİZ kalmasın diye iki koruma
    birlikte konur: (a) veri katmanında 036'nın değişmezlik tetikleyicisi
    `BEFORE UPDATE OR DELETE`e genişletildi ve `TG_OP` ayrımlı DELETE kolu
    YÜRÜTÜLMÜŞ satırın (durum `tamamlandi`/`hata` ya da jetonu HARCANMIŞ)
    silinmesini reddeder; (b) onaylanmış ama henüz yürütülmemiş bir satır
    üyelikten çıkarıldığında burada bir yönetici olayı yazılır.
    """
    owner = require_actor(actor)

    async with db.transaction():
        await _lock_incident(db, incident_id)
        mevcut = await _incident_rows(db, incident_id, for_update=True)
        if not mevcut:
            raise LifecycleError(f"olay bulunamadı: {incident_id!r}")

        yurutulmus = [s for s in mevcut if s["durum"] in ("tamamlandi", "hata")]
        if yurutulmus:
            raise IncidentMembershipLocked(
                f"olay {incident_id!r} yürütmeye başlamış "
                f"({len(yurutulmus)} satır tamamlandi/hata) — üyelik DEĞİŞTİRİLEMEZ"
            )

        mevcut_kimlikler = {satir["package_id"] for satir in mevcut}
        hedef_kimlikler = set(affected.geri_alinacaklar)

        eklenecek = sorted(hedef_kimlikler - mevcut_kimlikler, key=str)
        silinecek = sorted(mevcut_kimlikler - hedef_kimlikler, key=str)

        for package_id in eklenecek:
            satir = await _plan_satiri_kur(db, affected, package_id)
            await _plan_satirini_yaz(db, incident_id, satir)

        muhurlu_silinen = [
            satir["package_id"]
            for satir in mevcut
            if satir["package_id"] in set(silinecek) and satir["onay_actor"] is not None
        ]
        for package_id in silinecek:
            await db.execute(
                "DELETE FROM social.package_rollback_plans "
                "WHERE incident_id = $1 AND package_id = $2",
                incident_id,
                package_id,
            )

        if muhurlu_silinen:
            await record_admin_event(
                db,
                kind=UYELIK_DARALTMA_OLAYI,
                payload=mask_payload(
                    {
                        "incident_id": incident_id,
                        "actor": owner,
                        "muhru_dusen_paketler": [str(p) for p in muhurlu_silinen],
                    }
                ),
                idempotency_key=(
                    f"{incident_id}:uyelik:"
                    + identity.canonical_sha(sorted(str(p) for p in muhurlu_silinen))
                ),
            )

    return len(eklenecek), len(silinecek)


async def approve_incident_rollback(db, *, incident_id: str, actor: str) -> int:
    """Olayın BEKLEYEN satırlarını tek işlemde damgalar; damgalanan sayıyı döner.

    `onay_kapsam_sha` damgalanacak satırların değil, olayın **TAM üyeliğinin**
    parmak izidir; damgalanan HER satıra AYNI değer yazılır.

    **Damgalı satır iki hâlde iki davranış görür:** satırdaki `onay_kapsam_sha`
    bu koşumda hesaplanan değere EŞİTSE dokunulmaz (idempotans — ilk onay ve ilk
    onaylayan korunur); FARKLIYSA satır YENİDEN MÜHÜRLENİR. Karşılaştırma
    NORMALİZASYONSUZDUR: `strip()`'li bir karşılaştırma boşluk-sarmalı bayat bir
    mührü TAZE sanardı.
    """
    owner = require_actor(actor)

    async with db.transaction():
        await _lock_incident(db, incident_id)
        tum_satirlar = await _incident_rows(db, incident_id, for_update=True)
        if not tum_satirlar:
            return 0

        kapsam = incident_scope_sha(tum_satirlar)
        damgalanan = 0
        for satir in tum_satirlar:
            if satir["durum"] != "bekliyor":
                continue
            mevcut_sha = satir["onay_kapsam_sha"]
            taze = (
                type(mevcut_sha) is str
                and mevcut_sha.strip() != ""
                and mevcut_sha == kapsam
            )
            if taze:
                continue
            await db.execute(
                "UPDATE social.package_rollback_plans "
                "SET onay_actor = $3, onaylandi_at = now(), onay_kapsam_sha = $4 "
                "WHERE incident_id = $1 AND package_id = $2",
                incident_id,
                satir["package_id"],
                owner,
                kapsam,
            )
            damgalanan += 1
        return damgalanan


# ─── 11. Köken jetonu basımı (R8(c) / A2(d)) ────────────────────────────────


async def _kosu_gorunumu(db, run_id: str) -> KosuSatiriGorunumu | None:
    row = await db.fetchrow(
        "SELECT run_id, sector_id, package_id, durum, sonuc, approval_snapshot, "
        "       katman1_attestation, readiness_attestation "
        "FROM social.sector_package_runs WHERE run_id = $1 FOR UPDATE",
        run_id,
    )
    if row is None:
        return None
    return KosuSatiriGorunumu(
        run_id=row["run_id"],
        sector_id=row["sector_id"],
        package_id=row["package_id"],
        durum=row["durum"],
        sonuc=row["sonuc"] or "",
        approval_snapshot=row["approval_snapshot"],
        katman1_attestation=row["katman1_attestation"],
        readiness_attestation=row["readiness_attestation"],
    )


async def _hedef_kosu_gorunumu(db, *, sector_id: UUID, version: int):
    """Plan satırının hedef sürümünü ÜRETEN koşunun kilitli görünümü.

    Hedefin `run_id` bağı yoksa, koşu satırı yoksa ya da `durum != 'tamamlandi'`
    ise `None` döner — çağıran onu `RollbackEvidenceUnavailable`'a çevirir
    (F18: tasdik kanıttır, boolean değil).
    """
    paket = await db.fetchrow(
        "SELECT run_id FROM social.sector_packages "
        "WHERE sector_id = $1 AND version = $2",
        sector_id,
        version,
    )
    if paket is None or not paket["run_id"]:
        return None
    gorunum = await _kosu_gorunumu(db, paket["run_id"])
    if gorunum is None or gorunum.durum != "tamamlandi":
        return None
    return gorunum


async def mint_evidence_token(
    db,
    *,
    table: str,
    run_id: str | None,
    incident_id: str | None,
    package_id: UUID | None,
) -> str:
    """Kilitli satıra 64 hex'lik YENİ bir jeton + parmak izi basar; jetonu döner.

    **`fingerprint` PARAMETRE DEĞİLDİR (A2(d)).** Parmak izi BURADA, KİLİTLİ
    SATIRDAN türetilir; çağıranın elinde onu etkileyecek hiçbir girdi yoktur.
    Türetme yardımcıları `sector_package_lifecycle`'dan gelir (AÇIK-3); bu modül
    kendi türetmesini ya da kendi parmak izi hesabını YAZMAZ.

    Satır çağıran tarafından ZATEN kilitlenmiş olmalıdır; fonksiyon kendi SATIR
    kilidini almaz — kilit · basım · tüketim aynı işlemde kalsın diye. Geri alma
    yolunda olay kilidi yeniden alınır (yeniden-girişli). Basılamazsa
    `EvidenceMintRefused`; **boş dönüş YOKTUR.**

    **Çağıran AÇIK bir işlemde olmak ZORUNDADIR (fix turu 1, F4).** Aksi hâlde
    "kilitli satırdan türetilmiş parmak izi" iddiası boşa düşer: otomatik-commit
    altında `FOR UPDATE` kilidi kendi ifadesinin sonunda bırakılır. İlk iş bu
    kapıdır; sağlanmazsa `TransactionRequired`.
    """
    _require_transaction(db, "mint_evidence_token")
    if table not in JETON_TABLOLARI:
        raise ValueError(
            f"jeton tablosu kapalı kümenin dışında: {table!r} — "
            f"kabul edilenler: {list(JETON_TABLOLARI)}"
        )

    if table == "sector_package_runs":
        if run_id is None:
            raise ValueError("aktivasyon yolunda run_id zorunludur")
        # ÇAPA: bu fonksiyon aktif paket satırını kilitler, yani tek başına
        # çağrıldığında da mutasyon yollarıyla yarışır. Çapa yeniden girişlidir;
        # çağıran zaten almışsa bedeli yoktur.
        await anchor_run(db, run_id=run_id)
        kosu = await _kosu_gorunumu(db, run_id)
        if kosu is None or kosu.durum != "tamamlandi":
            raise EvidenceMintRefused(
                f"jeton basılamaz: koşu {run_id!r} yok ya da 'tamamlandi' değil"
            )
        aktif = await db.fetchrow(
            "SELECT id, version FROM social.sector_packages "
            "WHERE sector_id = $1 AND status = 'active' FOR UPDATE",
            kosu.sector_id,
        )
        # A4'ün DÖRDÜNCÜ koşulu (fix turu 1, F1): kanonik madde kümesi imzası
        # Plan 1 modülünün import kenarından GEÇEMEZ (AÇIK-3), o yüzden değeri
        # ÇAĞIRAN taşır. Kaynak kapalıdır ve buradadır — dış dünyadan gelen
        # hiçbir girdi bu parametreye ulaşamaz.
        payload = activation_evidence_payload(
            kosu,
            aktif,
            beklenen_madde_kumesi_sha=readiness_items.MADDE_KUMESI_SHA,
        )
        parmakizi = _evidence_fingerprint_from_payload(ActivationGateEvidence, payload)
        anahtarlar: tuple[Any, ...] = (run_id,)
        kosul = "run_id = $2"
    else:
        if incident_id is None or package_id is None:
            raise ValueError("geri alma yolunda incident_id ve package_id zorunludur")
        # SIRA: olay kilidi EN DIŞTA kalır (A1(b)), sektör çapası onun İÇİNDE.
        # Tek sıra = döngü yok; geri alma dışı yollar olay kilidini hiç istemez.
        await _lock_incident(db, incident_id)
        await anchor_for_package(db, package_id)
        plan_satiri = await db.fetchrow(
            "SELECT * FROM social.package_rollback_plans "
            "WHERE incident_id = $1 AND package_id = $2 FOR UPDATE",
            incident_id,
            package_id,
        )
        if plan_satiri is None or plan_satiri["durum"] != "bekliyor":
            raise EvidenceMintRefused(
                f"jeton basılamaz: plan satırı ({incident_id!r}, {package_id}) yok ya "
                "da 'bekliyor' değil"
            )
        paket = await db.fetchrow(
            "SELECT sector_id FROM social.sector_packages WHERE id = $1", package_id
        )
        hedef_kosu = (
            None
            if paket is None
            else await _hedef_kosu_gorunumu(
                db, sector_id=paket["sector_id"], version=plan_satiri["target_version"]
            )
        )
        if hedef_kosu is None:
            raise EvidenceMintRefused(
                "jeton basılamaz: hedef sürümü üreten koşu okunamıyor"
            )
        payload = rollback_evidence_payload(plan_satiri, hedef_kosu)
        parmakizi = _evidence_fingerprint_from_payload(RollbackGateEvidence, payload)
        anahtarlar = (incident_id, package_id)
        kosul = "incident_id = $2 AND package_id = $3"

    jeton = secrets.token_hex(32)
    basildi = await db.fetchval(
        f"UPDATE social.{table} SET kanit_jetonu = $1, kanit_jetonu_parmakizi = "
        f"${len(anahtarlar) + 2}, kanit_jetonu_basildi_at = now(), "
        f"kanit_jetonu_harcandi_at = NULL WHERE {kosul} "
        "RETURNING kanit_jetonu_basildi_at",
        jeton,
        *anahtarlar,
        parmakizi,
    )
    if basildi is None:  # pragma: no cover — satır yukarıda kilitlendi
        raise EvidenceMintRefused("jeton basılamadı: satır kayboldu")
    return jeton


# ─── 12. Geri alma kanıtı (R11) ─────────────────────────────────────────────


async def build_rollback_evidence(
    db, *, incident_id: str, package_id: UUID
) -> RollbackGateEvidence:
    """İki boolean'ı da OKUR, hiçbirini kabul etmez; jetonu da BURADA basar.

    İLK İŞ olay kilididir (A1(b), yol #3) — plan satırı `FOR UPDATE` ile
    okunmadan, `onay_*` alanları ve bugünkü kapsam hesaplanmadan ÖNCE.

    `manager_approved` — AÇIK-1'in ÜÇ koşulu: `onay_actor` · `onaylandi_at` ·
    `onay_kapsam_sha` dolu VE kapsam parmak izi bugünkü satır kümesiyle EŞLEŞİYOR.
    Karşılaştırma NORMALİZASYONSUZDUR (`strip`/`lower` YOK).

    `katman1_passed` — HEDEF sürümü üreten koşunun
    `katman1_attestation["sonuc"] == "PASS"` kaydı.

    Herhangi biri düşerse `RollbackEvidenceUnavailable` — uydurma YOK.

    **Çağıran AÇIK bir işlemde olmak ZORUNDADIR (fix turu 1, F4).** Olay kilidi
    işlem-ömürlüdür; otomatik-commit altında hem o hem satır kilitleri kendi
    ifadelerinin sonunda düşerdi ve fonksiyon kapsamı doğrulayıp, üyelik
    değişimiyle yarışıp, ESKİ kapsama bağlı bir jeton bastırıp kilitler
    bırakıldıktan sonra kanıt döndürebilirdi. Kapı `_lock_incident`'tan da
    ÖNCEDİR; sağlanmazsa `TransactionRequired`.
    """
    _require_transaction(db, "build_rollback_evidence")
    await _lock_incident(db, incident_id)
    # Olay kilidi EN DIŞTA, sektör çapası onun İÇİNDE (hakem turu 3).
    await anchor_for_package(db, package_id)

    plan_satiri = await db.fetchrow(
        "SELECT * FROM social.package_rollback_plans "
        "WHERE incident_id = $1 AND package_id = $2 FOR UPDATE",
        incident_id,
        package_id,
    )
    if plan_satiri is None:
        raise RollbackEvidenceUnavailable(
            f"plan satırı yok: ({incident_id!r}, {package_id})"
        )

    onay_actor = plan_satiri["onay_actor"]
    kapsam_sha = plan_satiri["onay_kapsam_sha"]
    if (
        type(onay_actor) is not str
        or onay_actor.strip() == ""
        or plan_satiri["onaylandi_at"] is None
        or type(kapsam_sha) is not str
        or kapsam_sha.strip() == ""
    ):
        raise RollbackEvidenceUnavailable(
            "yönetici onayı YOK: üç onay alanının üçü de dolu olmak ZORUNDA"
        )

    bugunku_kapsam = incident_scope_sha(await _incident_rows(db, incident_id))
    if kapsam_sha != bugunku_kapsam:
        raise RollbackEvidenceUnavailable(
            "onay mührü BAYAT: olayın üyeliği onaydan sonra değişti — yeniden "
            "mühürleme (olay-onayla) gerekir"
        )

    if plan_satiri["target_version"] is None:
        raise RollbackEvidenceUnavailable(
            "hedefsiz satır için geri alma kanıtı kurulamaz (K-38: deaktivasyon)"
        )

    paket = await db.fetchrow(
        "SELECT sector_id FROM social.sector_packages WHERE id = $1", package_id
    )
    if paket is None:
        raise RollbackEvidenceUnavailable(f"paket bulunamadı: {package_id}")

    hedef_kosu = await _hedef_kosu_gorunumu(
        db, sector_id=paket["sector_id"], version=plan_satiri["target_version"]
    )
    if hedef_kosu is None or hedef_kosu.katman1_attestation is None:
        raise RollbackEvidenceUnavailable(
            "hedef sürümü üreten koşunun Katman-1 tasdiki YOK — F18: tasdik "
            "kanıttır, boolean değil"
        )

    payload = rollback_evidence_payload(plan_satiri, hedef_kosu)
    if payload["katman1_passed"] is not True:
        raise RollbackEvidenceUnavailable(
            "hedef koşunun Katman-1 tasdiki PASS değil"
        )

    jeton = await mint_evidence_token(
        db,
        table="package_rollback_plans",
        run_id=None,
        incident_id=incident_id,
        package_id=package_id,
    )
    return RollbackGateEvidence(**payload, provenance_token=jeton)


# ─── 13. Geri alma yürütücüsü ───────────────────────────────────────────────


async def _plan_durumu_yaz(
    db, *, incident_id: str, package_id: UUID, durum: str, reason: str | None = None
) -> None:
    """Plan satırının durumunu yazar ve BİR satır etkilediğini KANITLAR.

    `execute` sıfır satır etkilese de sessizce başarılı olur; yürütme sonucunu
    yazan bir güncelleme için bu, izin sessizce kaybolması demektir (fix turu 1,
    F2). `RETURNING` ile dönen değer kontrol edilir — satır kaybolmuşsa
    `LifecycleError` fırlatılır ve rapor "düştü" diye YALAN SÖYLEMEZ.

    Hata kolundaki çağrı `except` bloğunun İÇİNDEN yapılır; oradan fırlayan bir
    `LifecycleError` yeniden yakalanmaz, yukarı çıkar (fail-closed). Tamamlanma
    kolundaki çağrı ise kayıt noktasının içindedir: orada düşerse deneme geri
    alınır ve satır `hata` olarak kaydedilir.
    """
    yazilan = await db.fetchval(
        "UPDATE social.package_rollback_plans SET durum = $3, "
        "reason = COALESCE($4, reason) "
        "WHERE incident_id = $1 AND package_id = $2 RETURNING package_id",
        incident_id,
        package_id,
        durum,
        reason,
    )
    if yazilan is None:
        raise LifecycleError(
            f"geri alma planı satırı yazılamadı: ({incident_id!r}, {package_id}) "
            f"durum={durum!r} güncellemesi SIFIR satır etkiledi — yürütme izi "
            "kaybolurdu"
        )


async def execute_rollback_plan(db, *, incident_id: str, actor: str) -> RollbackReport:
    """Planı PAKET PAKET yürütür — toplu-atomik mekanizma YOKTUR.

    Her paket kendi işlemindedir ve o işlemin İLK ifadesi olay kilididir
    (A1(b), yol #4); kilit `build_rollback_evidence` ve `rollback_package`
    çağrılarının İKİSİNİ de kapsayacak biçimde işlem sonuna kadar TUTULUR —
    aksi hâlde "doğrula → harca" aralığı açık kalırdı.

    **Tekrar güvenli:** tamamlanmış satır ATLANIR, hedef YENİDEN HESAPLANMAZ.
    **`hedefsiz` satır HATA ÜRETMEDEN atlanır** ve `durum='hedefsiz'` kalır;
    tekrar koşumda aynı sonucu korur. Rapor onu AYRI sayar.

    **Deneme bir KAYIT NOKTASINDA koşar (fix turu 1, F2).** Tanınan bir istisna
    dış işlemi SONLANDIRMAZ: yalnız kayıt noktası geri alınır, olay kilidi ile
    satır kilidi AYAKTA kalır ve `durum='hata'` kilit bırakılmadan yazılır.
    Önceki yazımda istisna dış işlemi de düşürüyor, hata kaydı KİLİTSİZ
    koşuyordu — o pencerede `amend_rollback_plan` kilidi alıp satırı `bekliyor`
    görüp SİLEBİLİYORDU; hata güncellemesi sıfır satır etkileyip sessizce
    geçiyor, rapor yine "bu paket düştü" diyordu ve denemenin izi kayboluyordu.
    İki durum yazımı da etkilenen satır sayısını `RETURNING` ile KANITLAR
    (`_plan_durumu_yaz`).
    """
    owner = require_actor(actor)

    satirlar = await _incident_rows(db, incident_id)
    if not satirlar:
        raise LifecycleError(f"olay bulunamadı: {incident_id!r}")

    tamamlandi: list[UUID] = []
    zaten: list[UUID] = []
    hedefsiz: list[UUID] = []
    hatali: list[UUID] = []
    sebepler: dict[str, str] = {}

    for kayit in satirlar:
        package_id = kayit["package_id"]
        async with db.transaction():
            await _lock_incident(db, incident_id)
            await anchor_for_package(db, package_id)
            satir = await db.fetchrow(
                "SELECT * FROM social.package_rollback_plans "
                "WHERE incident_id = $1 AND package_id = $2 FOR UPDATE",
                incident_id,
                package_id,
            )
            if satir is None:  # pragma: no cover — üyelik kilidi bunu kapatır
                continue
            if satir["durum"] == "tamamlandi":
                zaten.append(package_id)
                continue
            if satir["durum"] == "hedefsiz":
                hedefsiz.append(package_id)
                continue

            # DENEME bir KAYIT NOKTASINDA (savepoint) koşar. Dış işlem — ve
            # onunla birlikte olay kilidi ile satır kilidi — istisnada da AYAKTA
            # KALIR; yalnız denemenin yazdıkları geri alınır (fix turu 1, F2).
            try:
                async with db.transaction():
                    paket = await db.fetchrow(
                        "SELECT sector_id, version, status "
                        "FROM social.sector_packages WHERE id = $1",
                        package_id,
                    )
                    if paket is None:
                        raise RollbackEvidenceUnavailable(
                            f"paket bulunamadı: {package_id}"
                        )
                    if (
                        paket["status"] != "active"
                        or paket["version"] != satir["observed_active_version"]
                    ):
                        raise RollbackEvidenceUnavailable(
                            "karşılaştır-ve-uygula düştü: aktif sürüm plandan beri "
                            f"kaydı (plan {satir['observed_active_version']}, "
                            f"gerçek {paket['version']}/{paket['status']})"
                        )

                    evidence = await build_rollback_evidence(
                        db, incident_id=incident_id, package_id=package_id
                    )
                    await rollback_package(
                        db,
                        sector_id=paket["sector_id"],
                        to_version=satir["target_version"],
                        evidence=evidence,
                        actor=owner,
                    )
                    await _plan_durumu_yaz(
                        db,
                        incident_id=incident_id,
                        package_id=package_id,
                        durum="tamamlandi",
                    )
            except (
                RollbackEvidenceUnavailable,
                EvidenceMintRefused,
                LifecycleError,
            ) as hata:
                # Yeni durum değeri ÜRETİLMEZ: `hedefsiz` bu vaka için
                # KULLANILMAZ (o yalnız güvenli sürüm yokluğu demektir).
                #
                # Yazım DIŞ işlemin İÇİNDEDİR: kilit bırakılmadan önce satır
                # `hata` olur. Önceki yazımda kilit istisnayla birlikte düşüyor,
                # güncelleme kilitsiz koşuyordu — o pencerede üyelik daraltması
                # satırı `bekliyor` görüp SİLEBİLİYOR, güncelleme sıfır satır
                # etkileyip SESSİZCE geçiyor ve rapor yine "düştü" diyordu.
                sebep = mask_secrets(str(hata))
                await _plan_durumu_yaz(
                    db,
                    incident_id=incident_id,
                    package_id=package_id,
                    durum="hata",
                    reason=sebep,
                )
                hatali.append(package_id)
                sebepler[str(package_id)] = sebep
            else:
                tamamlandi.append(package_id)

    return RollbackReport(
        incident_id=incident_id,
        tamamlandi=tuple(tamamlandi),
        zaten_tamamlandi=tuple(zaten),
        hedefsiz=tuple(hedefsiz),
        hata=tuple(hatali),
        sebepler=sebepler,
    )


__all__ = [
    "ASAMALAR",
    "AffectedSet",
    "ArtifactStampMissing",
    "CorrectionRunRefused",
    "DURUMLAR",
    "IncidentMembershipLocked",
    "KOSU_TURLERI",
    "KosuSatiriGorunumu",
    "ReadinessAttestationRefused",
    "RollbackEvidenceUnavailable",
    "RollbackReport",
    "RunNotVerified",
    "SecretMaskingFilter",
    "TransactionRequired",
    "VerifiedRun",
    "affected_packages",
    "amend_rollback_plan",
    "approve_incident_rollback",
    "attest_katman1",
    "attest_katman2",
    "attest_readiness",
    "build_rollback_evidence",
    "build_rollback_plan",
    "build_stamp",
    "execute_rollback_plan",
    "incident_scope_sha",
    "load_verified_run",
    "log_run",
    "mark_incomplete",
    "mask_payload",
    "mask_secrets",
    "mint_evidence_token",
    "new_retry_run_id",
    "new_run_id",
    "open_correction_run",
    "open_run",
    "parse_stamp",
    "record_artifact",
    "record_result",
    "run_folder",
]
