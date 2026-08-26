"""Sektör bilgi paketi yaşam döngüsü (plan Task 13).

`sector_packages`'tan AYRI bir modüldür ve bağımlılık TEK YÖNLÜDÜR: buradan
oraya bakılır, tersi YOKTUR. Ayrımın gerekçesi sözleşme farkıdır — erişim
katmanı çalışma zamanında ASLA üretimi bloklamaz (her hata `None` + log),
buradaki geçişler ise tam tersine **fail-closed**'dur: kanıt eksikse,
statü uyuşmuyorsa ya da sektör kilidi kaymışsa geçiş YAPILMAZ ve istisna atar.

İki sözleşme aynı dosyada yaşarsa "hata durumunda ne olmalı" sorusunun cevabı
okuyucuya göre değişir; ayrı dosyada her modülün tek bir cevabı vardır.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.services.package_events import log_package_event
from app.services.sector_packages import (
    normalize_special_day_key,
    validate_package_content,
)

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


@dataclass(frozen=True)
class RollbackGateEvidence:
    """Rollback kapısının kanıtı — aktivasyon kanıtıyla PAYLAŞILMAZ.

    Acil rollback, ADAYIN aktivasyon kapılarından bağımsızdır: "aday yeterli
    değil" diye aktif sürümü geri alamamak, acil kolu işlevsiz bırakırdı. O
    yüzden buradaki tek insan kapısı yönetici onayıdır.
    """

    manager_approved: bool
    katman1_passed: bool

    def __post_init__(self) -> None:
        _require_flag(self.manager_approved, "manager_approved")
        _require_flag(self.katman1_passed, "katman1_passed")


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


def _require_actor(actor: Any) -> str:
    if not isinstance(actor, str) or not actor.strip():
        raise ValueError("actor zorunlu — sahipsiz yaşam döngüsü işlemi yazılmaz")
    return actor.strip()


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
) -> UUID:
    """Doğrulayıcı-arkalı TEK draft yazıcısı (spec §3.6; K-135 yazma yüzeyi).

    Doğrulayıcının iki dış girdisi (sistem takvimi, kayıtlı marka adları)
    ÇAĞIRANDAN alınmaz, DB'den okunur. Aksi hâlde kapı yalnız çağıran doğru
    listeyi verdiğinde çalışırdı — yani kapı değil nezaket kuralı olurdu.

    `version` sektör içinde son + 1'dir. Eşzamanlı iki yazımda ikisi de aynı
    numarayı görebilir; `UNIQUE (sector_id, version)` birini reddeder
    (fail-closed).
    """
    owner = _require_actor(actor)

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
    for warning in result.warnings:
        logger.warning("paket taslağı uyarısı (sector_id=%s): %s", sector_id, warning)

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
        [{"event": "draft_created", "actor": owner}],
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
