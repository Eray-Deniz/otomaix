"""Paket yaşam döngüsü servis fonksiyonları (plan Task 13).

Dört sözleşme burada pinlenir:

1. **Kanıtsız geçiş YOLU YOKTUR.** Ham iki-adım geçişi özeldir
   (`_apply_status_transition`); public yüzeyden geçmenin tek yolu kendi kapı
   kanıtını taşımaktır. Aktivasyon `ActivationGateEvidence`, rollback AYRI bir
   `RollbackGateEvidence` ister — ikisi PAYLAŞILMAZ, çünkü acil rollback adayın
   aktivasyon kapılarından bağımsızdır.
2. **Geçiş + olay ATOMİKTİR (F24).** Olay yazımı ile durum geçişi aynı
   transaction'dadır: olaysız geçiş de geçişsiz olay da mümkün değildir.
   Altyapı hatası bu yüzeyde YUTULMAZ — çalışma zamanı yollarının aksine
   (`_record_event`), yaşam döngüsünde yarım bir denetim izi geçişin kendisini
   geçersiz kılar.
3. **Sıra sözleşmesi: olay ÖNCE, geçiş SONRA.** `log_package_event`'in
   "bu bir devir teslim mi" ölçüsü tablodan okunur ve o ölçü YALNIZ geçiş
   uygulanmadan önce doğrudur (aşağıdaki deaktivasyon-sonrası aktivasyon
   testi bu sırayı bağlar).
4. **Yazım kapısı `insert_draft`'ın arkasındadır.** Doğrulayıcı girdilerini
   (sistem takvimi, mevcut marka adları) çağırandan değil DB'den alır; kapı
   geçmeden satır yazılmaz.
"""

from __future__ import annotations

import uuid

import pytest

from app.core.database import _init_connection
from app.services import sector_packages
from app.services.sector_packages import (
    ActivationGateEvidence,
    GateNotSatisfied,
    LifecycleError,
    RollbackGateEvidence,
    activate_package,
    deactivate_package,
    insert_draft,
    rollback_package,
)

from .test_sector_packages_service import _valid_content  # noqa: E402

ACTOR = "admin@otomaix"


# ─── Ortak seed ─────────────────────────────────────────────────────────────


@pytest.fixture
async def pkg_db(db):
    """Üretimin KENDİ bağlantı yapılandırması + takvim kapısının besini.

    `_valid_content()` bir `ozel_gun` anahtarı taşır ve yazım kapısı o anahtarı
    SİSTEM TAKVİMİNE karşı doğrular. Anahtarı sabitlemek yerine takvime bir
    satır eklemek, kapının gerçekten tablodan beslendiğini de gösterir.
    """
    await _init_connection(db)
    await db.execute(
        "INSERT INTO social.public_holidays (year, date, name_tr) "
        "VALUES (2099, '2099-10-29', $1)",
        "Cumhuriyet Bayramı",
    )
    return db


async def _sub_sector(db) -> uuid.UUID:
    root_id = await db.fetchval(
        "SELECT id FROM social.sectors WHERE parent_sector_id IS NULL LIMIT 1"
    )
    assert root_id is not None, "kök sektör seed'i eksik"
    return await db.fetchval(
        "INSERT INTO social.sectors (slug, display_name, parent_sector_id) "
        "VALUES ($1, $2, $3) RETURNING id",
        f"alt-{uuid.uuid4().hex[:8]}",
        "Alt Sektör",
        root_id,
    )


async def _seed_package(db, sector_id, *, version: int, status: str) -> uuid.UUID:
    """Kurulum satırı — yazım kapısını ATLAR (kapı kendi testinde ölçülür)."""
    return await db.fetchval(
        "INSERT INTO social.sector_packages "
        "(sector_id, version, status, schema_version, content) "
        "VALUES ($1, $2, $3, 1, $4) RETURNING id",
        sector_id,
        version,
        status,
        _valid_content(),
    )


async def _status(db, package_id) -> str:
    return await db.fetchval(
        "SELECT status FROM social.sector_packages WHERE id = $1", package_id
    )


async def _events(db, sector_id) -> list:
    return await db.fetch(
        "SELECT event_type, from_version, to_version, actor "
        "FROM social.package_events WHERE sector_id = $1 ORDER BY created_at, event_type",
        sector_id,
    )


class _EventTail:
    """Her adımdan sonra YENİ eklenen olayları döner.

    Neden `created_at` sıralaması değil: `now()` transaction başlangıcını
    verir ve testin tamamı tek dış transaction'da koştuğu için bütün satırlar
    AYNI damgayı taşır — sıralama iddiası orada hiçbir şey ölçmez (ölçüldü).
    Kimliğe göre delta almak sıralamadan bağımsız ve kesindir.
    """

    def __init__(self):
        self.seen: set = set()

    async def new(self, db, sector_id) -> list[tuple]:
        rows = await db.fetch(
            "SELECT id, event_type, from_version, to_version, actor "
            "FROM social.package_events WHERE sector_id = $1",
            sector_id,
        )
        fresh = [row for row in rows if row["id"] not in self.seen]
        self.seen.update(row["id"] for row in rows)
        return [
            (r["event_type"], r["from_version"], r["to_version"], r["actor"]) for r in fresh
        ]


def _activation_evidence(**overrides) -> ActivationGateEvidence:
    fields = dict(
        activation_eligible=True,
        open_questions_count=0,
        katman1_passed=True,
        checklist_approved=True,
    )
    fields.update(overrides)
    return ActivationGateEvidence(**fields)


def _rollback_evidence(**overrides) -> RollbackGateEvidence:
    fields = dict(manager_approved=True, katman1_passed=True)
    fields.update(overrides)
    return RollbackGateEvidence(**fields)


# ═══ 1. Draft yazımı ════════════════════════════════════════════════════════


async def test_insert_draft_requires_valid_content(pkg_db):
    """Doğrulayıcı GEÇMEDEN satır yazılmaz (spec §3.6)."""
    sector_id = await _sub_sector(pkg_db)
    broken = _valid_content()
    del broken["kapsam"]

    with pytest.raises(ValueError):
        await insert_draft(
            pkg_db, sector_id=sector_id, content=broken, schema_version=1, actor=ACTOR
        )

    assert (
        await pkg_db.fetchval(
            "SELECT count(*) FROM social.sector_packages WHERE sector_id = $1", sector_id
        )
        == 0
    ), "kapı düşerken satır yazıldı"


async def test_insert_draft_sources_validator_inputs_from_db(pkg_db):
    """Doğrulayıcı girdileri ÇAĞIRANDAN değil DB'den gelir.

    Marka adı yasağı (K-15) yalnız çağıran doğru listeyi verirse çalışıyorsa
    kapı değil, nezaket kuralıdır. Kayıtlı bir marka adının pakete sızması bu
    yüzden çağırandan bağımsız reddedilmeli.
    """
    sector_id = await _sub_sector(pkg_db)
    workspace_id = await pkg_db.fetchval(
        "INSERT INTO social.workspaces (name) VALUES ('Test WS') RETURNING id"
    )
    await pkg_db.execute(
        "INSERT INTO social.brands (workspace_id, name) VALUES ($1, $2)",
        workspace_id,
        "Zarelfa",
    )

    content = _valid_content(kapsam="Zarelfa mağazalarında altın perakendesi.")
    with pytest.raises(ValueError, match="Zarelfa"):
        await insert_draft(
            pkg_db, sector_id=sector_id, content=content, schema_version=1, actor=ACTOR
        )


async def test_insert_draft_versions_sequentially(pkg_db):
    """`version` = son + 1; ilk satır 1'den başlar."""
    sector_id = await _sub_sector(pkg_db)
    first = await insert_draft(
        pkg_db, sector_id=sector_id, content=_valid_content(), schema_version=1, actor=ACTOR
    )
    second = await insert_draft(
        pkg_db, sector_id=sector_id, content=_valid_content(), schema_version=1, actor=ACTOR
    )

    rows = await pkg_db.fetch(
        "SELECT id, version, status FROM social.sector_packages "
        "WHERE sector_id = $1 ORDER BY version",
        sector_id,
    )
    assert [(r["id"], r["version"], r["status"]) for r in rows] == [
        (first, 1, "draft"),
        (second, 2, "draft"),
    ]


async def test_insert_draft_records_actor(pkg_db):
    """`actor` sessizce DÜŞÜRÜLMEZ — satırın kendi izinde durur."""
    sector_id = await _sub_sector(pkg_db)
    package_id = await insert_draft(
        pkg_db,
        sector_id=sector_id,
        content=_valid_content(),
        schema_version=1,
        run_id="run-42",
        actor=ACTOR,
    )
    row = await pkg_db.fetchrow(
        "SELECT run_id, decision_log FROM social.sector_packages WHERE id = $1", package_id
    )
    assert row["run_id"] == "run-42"
    assert any(
        entry.get("actor") == ACTOR for entry in row["decision_log"]
    ), f"actor izi yok: {row['decision_log']!r}"


async def test_insert_draft_rejects_missing_actor(pkg_db):
    """Kanıtsız yazım gibi, sahipsiz yazım da reddedilir."""
    sector_id = await _sub_sector(pkg_db)
    with pytest.raises(ValueError):
        await insert_draft(
            pkg_db, sector_id=sector_id, content=_valid_content(), schema_version=1, actor=" "
        )


# ═══ 2. Ham geçişin kapatılması ═════════════════════════════════════════════


async def test_raw_transition_not_publicly_exported():
    """Ham geçiş modül DIŞINA verilmez — public takma ad da yok.

    `__all__` listesine güvenmek yetmez (liste bayatlar). Ölçü doğrudan:
    modülde ham fonksiyonu işaret eden ALTÇİZGİSİZ bir ad var mı?
    """
    raw = sector_packages._apply_status_transition
    aliases = [
        name
        for name in dir(sector_packages)
        if not name.startswith("_") and getattr(sector_packages, name, None) is raw
    ]
    assert aliases == [], f"ham geçiş public adla sızıyor: {aliases}"


# ═══ 3. Aktivasyon kapıları ═════════════════════════════════════════════════


async def test_first_activation_single_step(pkg_db):
    """Sektörün İLK paketi tek adımda aktive olur; arşivlenecek şey yoktur."""
    sector_id = await _sub_sector(pkg_db)
    package_id = await _seed_package(pkg_db, sector_id, version=1, status="draft")

    await activate_package(
        pkg_db, package_id=package_id, evidence=_activation_evidence(), actor=ACTOR
    )

    assert await _status(pkg_db, package_id) == "active"
    events = await _events(pkg_db, sector_id)
    assert [(e["event_type"], e["from_version"], e["to_version"]) for e in events] == [
        ("activation", None, 1)
    ]


async def test_activate_archives_previous_then_activates(pkg_db):
    """Devir teslim: önceki arşivlenir, yeni aktive olur — tek geçişte."""
    sector_id = await _sub_sector(pkg_db)
    old_id = await _seed_package(pkg_db, sector_id, version=1, status="active")
    new_id = await _seed_package(pkg_db, sector_id, version=2, status="draft")

    await activate_package(
        pkg_db, package_id=new_id, evidence=_activation_evidence(), actor=ACTOR
    )

    assert await _status(pkg_db, old_id) == "archived"
    assert await _status(pkg_db, new_id) == "active"
    events = await _events(pkg_db, sector_id)
    assert [(e["event_type"], e["from_version"], e["to_version"]) for e in events] == [
        ("activation", 1, 2)
    ]


@pytest.mark.parametrize(
    "override",
    [
        {"activation_eligible": False},
        {"open_questions_count": 1},
        {"katman1_passed": False},
        {"checklist_approved": False},
    ],
    ids=["not_eligible", "open_questions", "failed_katman1", "missing_checklist"],
)
async def test_activate_rejects_unsatisfied_gate(pkg_db, override):
    """Kanıt alanlarından HERHANGİ biri sağlanmazsa geçiş REDDEDİLİR.

    K-71 (açık soru sayısı 0 olmalı) ve K-28'in Plan-1 ayağı bu kapıdadır.
    """
    sector_id = await _sub_sector(pkg_db)
    package_id = await _seed_package(pkg_db, sector_id, version=1, status="draft")

    with pytest.raises(GateNotSatisfied):
        await activate_package(
            pkg_db,
            package_id=package_id,
            evidence=_activation_evidence(**override),
            actor=ACTOR,
        )

    assert await _status(pkg_db, package_id) == "draft"
    assert await _events(pkg_db, sector_id) == []


async def test_activate_rejects_stale_base_version_when_provided(pkg_db):
    """K-94 yeteneği: dolu `expected_active_version` gerçekle eşleşmeli."""
    sector_id = await _sub_sector(pkg_db)
    await _seed_package(pkg_db, sector_id, version=1, status="active")
    new_id = await _seed_package(pkg_db, sector_id, version=2, status="draft")

    with pytest.raises(GateNotSatisfied, match="expected_active_version"):
        await activate_package(
            pkg_db,
            package_id=new_id,
            evidence=_activation_evidence(expected_active_version=99),
            actor=ACTOR,
        )

    assert await _status(pkg_db, new_id) == "draft"


async def test_activate_accepts_matching_base_version(pkg_db):
    """Doğru base-sürüm kanıtı geçişi ENGELLEMEZ (yetenek gerçekten çalışıyor)."""
    sector_id = await _sub_sector(pkg_db)
    await _seed_package(pkg_db, sector_id, version=1, status="active")
    new_id = await _seed_package(pkg_db, sector_id, version=2, status="draft")

    await activate_package(
        pkg_db,
        package_id=new_id,
        evidence=_activation_evidence(expected_active_version=1),
        actor=ACTOR,
    )
    assert await _status(pkg_db, new_id) == "active"


async def test_activate_allows_missing_base_version_while_k94_open(pkg_db):
    """K-94 AÇIK: alan opsiyoneldir, `None` geçişi engellemez."""
    sector_id = await _sub_sector(pkg_db)
    await _seed_package(pkg_db, sector_id, version=1, status="active")
    new_id = await _seed_package(pkg_db, sector_id, version=2, status="draft")

    await activate_package(
        pkg_db,
        package_id=new_id,
        evidence=_activation_evidence(expected_active_version=None),
        actor=ACTOR,
    )
    assert await _status(pkg_db, new_id) == "active"


async def test_activate_rejects_non_draft_package(pkg_db):
    """Arşivlenmiş satırı `activate_package` diriltmez — o iş rollback'indir."""
    sector_id = await _sub_sector(pkg_db)
    archived_id = await _seed_package(pkg_db, sector_id, version=1, status="archived")

    with pytest.raises(LifecycleError):
        await activate_package(
            pkg_db, package_id=archived_id, evidence=_activation_evidence(), actor=ACTOR
        )
    assert await _status(pkg_db, archived_id) == "archived"


async def test_activate_after_deactivation_has_no_from_version(pkg_db):
    """Deaktivasyon SONRASI aktivasyon bir devir teslim DEĞİLDİR.

    Bu senaryo (acil geri çekme → bakım → yeniden açma) K-38'in doğal
    devamıdır. O anda sektörde arşivlenmiş satır VARDIR ama AKTİF satır
    yoktur; yerine geçilen bir şey olmadığı için `from_version` NULL'dır ve
    olay kaydı bunu reddetmemelidir. Denetim izi burada uydurma bir kaynak
    sürüm taşıyamaz.
    """
    sector_id = await _sub_sector(pkg_db)
    first_id = await _seed_package(pkg_db, sector_id, version=1, status="active")
    second_id = await _seed_package(pkg_db, sector_id, version=2, status="draft")
    tail = _EventTail()

    await deactivate_package(pkg_db, package_id=first_id, actor=ACTOR)
    assert await _status(pkg_db, first_id) == "archived"
    assert await tail.new(pkg_db, sector_id) == [("deactivation", 1, None, ACTOR)]

    await activate_package(
        pkg_db, package_id=second_id, evidence=_activation_evidence(), actor=ACTOR
    )

    assert await _status(pkg_db, second_id) == "active"
    assert await tail.new(pkg_db, sector_id) == [("activation", None, 2, ACTOR)]


# ═══ 4. Rollback ════════════════════════════════════════════════════════════


async def test_rollback_restores_previous_version(pkg_db):
    """Rollback: aktif olan arşivlenir, hedef sürüm geri gelir."""
    sector_id = await _sub_sector(pkg_db)
    old_id = await _seed_package(pkg_db, sector_id, version=1, status="archived")
    current_id = await _seed_package(pkg_db, sector_id, version=2, status="active")

    await rollback_package(
        pkg_db,
        sector_id=sector_id,
        to_version=1,
        evidence=_rollback_evidence(),
        actor=ACTOR,
    )

    assert await _status(pkg_db, old_id) == "active"
    assert await _status(pkg_db, current_id) == "archived"
    events = await _events(pkg_db, sector_id)
    assert [(e["event_type"], e["from_version"], e["to_version"]) for e in events] == [
        ("rollback", 2, 1)
    ]


async def test_rollback_rejects_without_manager_approval(pkg_db):
    """Yönetici onayı ZORUNLU (spec §2.3)."""
    sector_id = await _sub_sector(pkg_db)
    await _seed_package(pkg_db, sector_id, version=1, status="archived")
    current_id = await _seed_package(pkg_db, sector_id, version=2, status="active")

    with pytest.raises(GateNotSatisfied, match="manager_approved"):
        await rollback_package(
            pkg_db,
            sector_id=sector_id,
            to_version=1,
            evidence=_rollback_evidence(manager_approved=False),
            actor=ACTOR,
        )

    assert await _status(pkg_db, current_id) == "active"
    assert await _events(pkg_db, sector_id) == []


async def test_rollback_evidence_is_not_the_activation_evidence():
    """İki kanıt sınıfı PAYLAŞILMAZ; rollback aktivasyon alanlarını İSTEMEZ."""
    rollback_fields = set(RollbackGateEvidence.__dataclass_fields__)
    activation_only = {
        "activation_eligible",
        "open_questions_count",
        "checklist_approved",
        "expected_active_version",
    }
    assert rollback_fields & activation_only == set()
    assert "manager_approved" in rollback_fields
    assert "manager_approved" not in set(ActivationGateEvidence.__dataclass_fields__)


async def test_rollback_allowed_while_candidate_activation_gates_fail(pkg_db):
    """Acil rollback, adayın aktivasyon kapılarından BAĞIMSIZDIR.

    Aktif sürüm ancak "aday yeterli değil" diye kilitlenirse acil kol işe
    yaramaz; rollback yalnız kendi kanıtına bakar.
    """
    sector_id = await _sub_sector(pkg_db)
    old_id = await _seed_package(pkg_db, sector_id, version=1, status="archived")
    current_id = await _seed_package(pkg_db, sector_id, version=2, status="active")
    candidate_id = await _seed_package(pkg_db, sector_id, version=3, status="draft")

    # Aday aktive EDİLEMEZ durumda.
    with pytest.raises(GateNotSatisfied):
        await activate_package(
            pkg_db,
            package_id=candidate_id,
            evidence=_activation_evidence(activation_eligible=False),
            actor=ACTOR,
        )

    # Buna rağmen rollback koşar.
    await rollback_package(
        pkg_db,
        sector_id=sector_id,
        to_version=1,
        evidence=_rollback_evidence(),
        actor=ACTOR,
    )
    assert await _status(pkg_db, old_id) == "active"
    assert await _status(pkg_db, current_id) == "archived"
    assert await _status(pkg_db, candidate_id) == "draft"


@pytest.mark.parametrize("to_version", [3, 2], ids=["draft_target", "already_active_target"])
async def test_rollback_rejects_non_archived_target(pkg_db, to_version):
    """Hedef sürüm ARŞİVLENMİŞ olmalı.

    İki reddedilen şekil: henüz aktive edilmemiş bir taslağa "geri dönmek"
    (v3) ve zaten aktif olan sürüme geri dönmek (v2 — kendi üstüne geçiş).
    İkinci sektörde ikinci bir `active` satır kurulamaz (kısmi benzersiz
    indeks), o yüzden vaka mevcut aktif satır üzerinden koşulur.
    """
    sector_id = await _sub_sector(pkg_db)
    await _seed_package(pkg_db, sector_id, version=1, status="archived")
    current_id = await _seed_package(pkg_db, sector_id, version=2, status="active")
    await _seed_package(pkg_db, sector_id, version=3, status="draft")

    with pytest.raises(LifecycleError):
        await rollback_package(
            pkg_db,
            sector_id=sector_id,
            to_version=to_version,
            evidence=_rollback_evidence(),
            actor=ACTOR,
        )

    assert await _status(pkg_db, current_id) == "active"
    assert await _events(pkg_db, sector_id) == []


async def test_rollback_rejects_nonexistent_target(pkg_db):
    """Var olmayan sürüme rollback edilmez."""
    sector_id = await _sub_sector(pkg_db)
    await _seed_package(pkg_db, sector_id, version=1, status="archived")
    await _seed_package(pkg_db, sector_id, version=2, status="active")

    with pytest.raises(LifecycleError):
        await rollback_package(
            pkg_db,
            sector_id=sector_id,
            to_version=7,
            evidence=_rollback_evidence(),
            actor=ACTOR,
        )


async def test_first_package_rollback_error_points_to_deactivation(pkg_db):
    """Önceki sürüm HİÇ yoksa istenen şey rollback değil deaktivasyondur."""
    sector_id = await _sub_sector(pkg_db)
    only_id = await _seed_package(pkg_db, sector_id, version=1, status="active")

    with pytest.raises(LifecycleError, match="deactivate_package"):
        await rollback_package(
            pkg_db,
            sector_id=sector_id,
            to_version=1,
            evidence=_rollback_evidence(),
            actor=ACTOR,
        )

    assert await _status(pkg_db, only_id) == "active"


# ═══ 5. Deaktivasyon ════════════════════════════════════════════════════════


async def test_deactivate_without_new_version_no_evidence_needed(pkg_db):
    """K-38 acil kol: kanıt İSTEMEZ, olay kaydı ZORUNLUDUR."""
    sector_id = await _sub_sector(pkg_db)
    package_id = await _seed_package(pkg_db, sector_id, version=1, status="active")

    await deactivate_package(pkg_db, package_id=package_id, actor=ACTOR)

    assert await _status(pkg_db, package_id) == "archived"
    events = await _events(pkg_db, sector_id)
    assert [(e["event_type"], e["from_version"], e["to_version"], e["actor"]) for e in events] == [
        ("deactivation", 1, None, ACTOR)
    ]


async def test_deactivate_rejects_non_active_package(pkg_db):
    """Aktif olmayan satır geri çekilemez — çekilecek bir şey yok."""
    sector_id = await _sub_sector(pkg_db)
    draft_id = await _seed_package(pkg_db, sector_id, version=1, status="draft")

    with pytest.raises(LifecycleError):
        await deactivate_package(pkg_db, package_id=draft_id, actor=ACTOR)
    assert await _status(pkg_db, draft_id) == "draft"


# ═══ 6. Geçiş + olay atomikliği (F24) ═══════════════════════════════════════


async def test_lifecycle_events_recorded(pkg_db):
    """Uçtan uca zincir tam bir denetim izi bırakır."""
    sector_id = await _sub_sector(pkg_db)
    tail = _EventTail()

    v1 = await insert_draft(
        pkg_db, sector_id=sector_id, content=_valid_content(), schema_version=1, actor=ACTOR
    )
    await activate_package(pkg_db, package_id=v1, evidence=_activation_evidence(), actor=ACTOR)
    assert await tail.new(pkg_db, sector_id) == [("activation", None, 1, ACTOR)]

    v2 = await insert_draft(
        pkg_db, sector_id=sector_id, content=_valid_content(), schema_version=1, actor=ACTOR
    )
    await activate_package(pkg_db, package_id=v2, evidence=_activation_evidence(), actor=ACTOR)
    assert await tail.new(pkg_db, sector_id) == [("activation", 1, 2, ACTOR)]

    await rollback_package(
        pkg_db, sector_id=sector_id, to_version=1, evidence=_rollback_evidence(), actor=ACTOR
    )
    assert await tail.new(pkg_db, sector_id) == [("rollback", 2, 1, ACTOR)]

    await deactivate_package(pkg_db, package_id=v1, actor=ACTOR)
    assert await tail.new(pkg_db, sector_id) == [("deactivation", 1, None, ACTOR)]

    assert (
        await pkg_db.fetchval(
            "SELECT count(*) FROM social.package_events WHERE sector_id = $1", sector_id
        )
        == 4
    ), "yaşam döngüsü fazladan olay yazdı"


@pytest.mark.parametrize("failure", ["raises", "returns_none"], ids=["exception", "silent_none"])
async def test_event_insert_failure_rolls_back_transition(pkg_db, monkeypatch, failure):
    """Olay yazılamazsa geçiş DE olmaz (F24).

    `returns_none` dalı asıl tehlikeli olandır: `log_package_event` altyapı
    hatasında bilinçle `None` döner ve çalışma zamanı yollarında bu doğrudur.
    Yaşam döngüsünde aynı sessizlik "geçiş oldu ama izi yok" demektir — bu
    yüzden dönüş değeri burada KONTROL EDİLİR.
    """
    sector_id = await _sub_sector(pkg_db)
    package_id = await _seed_package(pkg_db, sector_id, version=1, status="draft")

    async def _broken(*args, **kwargs):
        if failure == "raises":
            raise RuntimeError("olay tablosu erişilemiyor")
        return None

    monkeypatch.setattr(sector_packages, "log_package_event", _broken)

    with pytest.raises(Exception):
        await activate_package(
            pkg_db, package_id=package_id, evidence=_activation_evidence(), actor=ACTOR
        )

    assert await _status(pkg_db, package_id) == "draft", "olaysız geçiş kaldı"


async def test_transition_failure_leaves_no_event(pkg_db, monkeypatch):
    """Geçiş patlarsa ÖNCE yazılmış olay da geri alınır (F24).

    Olay geçişten ÖNCE yazıldığı için bu test transaction'ın kendisini ölçer:
    sarmalayıcı olmasaydı sahte bir `activation` satırı kalırdı.
    """
    sector_id = await _sub_sector(pkg_db)
    package_id = await _seed_package(pkg_db, sector_id, version=1, status="draft")

    async def _broken(*args, **kwargs):
        raise RuntimeError("durum güncellemesi düştü")

    monkeypatch.setattr(sector_packages, "_set_status", _broken)

    with pytest.raises(RuntimeError):
        await activate_package(
            pkg_db, package_id=package_id, evidence=_activation_evidence(), actor=ACTOR
        )

    assert await _status(pkg_db, package_id) == "draft"
    assert await _events(pkg_db, sector_id) == [], "geçişsiz olay kaldı"
