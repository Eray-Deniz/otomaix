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
from app.services import sector_package_lifecycle
from app.services.sector_package_lifecycle import (
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
    raw = sector_package_lifecycle._apply_status_transition
    aliases = [
        name
        for name in dir(sector_package_lifecycle)
        if not name.startswith("_") and getattr(sector_package_lifecycle, name, None) is raw
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

    monkeypatch.setattr(sector_package_lifecycle, "log_package_event", _broken)

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

    monkeypatch.setattr(sector_package_lifecycle, "_set_status", _broken)

    with pytest.raises(RuntimeError):
        await activate_package(
            pkg_db, package_id=package_id, evidence=_activation_evidence(), actor=ACTOR
        )

    assert await _status(pkg_db, package_id) == "draft"
    assert await _events(pkg_db, sector_id) == [], "geçişsiz olay kaldı"


# ═══ 7. Kanıt sınıflarının çalışma-zamanı zorlaması (checkpoint 13, F1) ═════
#
# Açıklama satırı bir kapı DEĞİLDİR. `activation_eligible: bool` yalnız bir
# not; Python onu zorlamaz. Doğruluk-değeriyle çalışan bir kapı, "false"
# metnini DOĞRU sayar — yani "aktive edilemez" diye işaretlenmiş bir aday
# aktive edilebilirdi. Sayısal alanda ayna vaka: `False == 0` ve `True == 1`.


@pytest.mark.parametrize(
    "override",
    [
        {"activation_eligible": "false"},
        {"katman1_passed": "false"},
        {"checklist_approved": "false"},
        {"activation_eligible": 1},
        {"open_questions_count": False},
        {"open_questions_count": "0"},
        {"open_questions_count": -1},
        {"expected_active_version": True},
        {"expected_active_version": "1"},
        {"expected_active_version": 0},
    ],
)
def test_activation_evidence_rejects_loose_values(override):
    """Doğru-görünen değer kanıt DEĞİLDİR — yapımda reddedilir."""
    fields = dict(
        activation_eligible=True,
        open_questions_count=0,
        katman1_passed=True,
        checklist_approved=True,
    )
    fields.update(override)
    with pytest.raises((TypeError, ValueError)):
        ActivationGateEvidence(**fields)


@pytest.mark.parametrize(
    "override",
    [{"manager_approved": "false"}, {"katman1_passed": 1}, {"manager_approved": None}],
)
def test_rollback_evidence_rejects_loose_values(override):
    fields = dict(manager_approved=True, katman1_passed=True)
    fields.update(override)
    with pytest.raises((TypeError, ValueError)):
        RollbackGateEvidence(**fields)


class _LookalikeEvidence:
    """Aynı alan adlarını taşıyan ama kanıt sınıfı OLMAYAN nesne."""

    activation_eligible = True
    open_questions_count = 0
    katman1_passed = True
    checklist_approved = True
    expected_active_version = None
    manager_approved = True


async def test_activate_rejects_lookalike_evidence(pkg_db):
    """Ördek tiplemesi kanıt yerine geçmez — sınıfın kendisi istenir."""
    sector_id = await _sub_sector(pkg_db)
    package_id = await _seed_package(pkg_db, sector_id, version=1, status="draft")

    with pytest.raises(GateNotSatisfied):
        await activate_package(
            pkg_db, package_id=package_id, evidence=_LookalikeEvidence(), actor=ACTOR
        )
    assert await _status(pkg_db, package_id) == "draft"


async def test_rollback_rejects_lookalike_evidence(pkg_db):
    sector_id = await _sub_sector(pkg_db)
    await _seed_package(pkg_db, sector_id, version=1, status="archived")
    current_id = await _seed_package(pkg_db, sector_id, version=2, status="active")

    with pytest.raises(GateNotSatisfied):
        await rollback_package(
            pkg_db,
            sector_id=sector_id,
            to_version=1,
            evidence=_LookalikeEvidence(),
            actor=ACTOR,
        )
    assert await _status(pkg_db, current_id) == "active"


async def test_rollback_rejects_activation_evidence(pkg_db):
    """Aktivasyon kanıtı rollback kapısını açmaz (sınıflar paylaşılmaz)."""
    sector_id = await _sub_sector(pkg_db)
    await _seed_package(pkg_db, sector_id, version=1, status="archived")
    await _seed_package(pkg_db, sector_id, version=2, status="active")

    with pytest.raises(GateNotSatisfied):
        await rollback_package(
            pkg_db,
            sector_id=sector_id,
            to_version=1,
            evidence=_activation_evidence(),
            actor=ACTOR,
        )


# ═══ 8. Eşzamanlılık — gerçek iki bağlantı (checkpoint 13, F2) ══════════════
#
# Tek bağlantıda araya girmek bu sınıfı ÖLÇMEZ: soru tam olarak "iki ayrı
# transaction aynı taslağı aynı anda aktive edebilir mi". Bu testler kendi
# bağlantılarını açar ve GERÇEKTEN commit eder, o yüzden temizlik ellerindedir.


async def _seed_committed_sector(conn) -> uuid.UUID:
    root_id = await conn.fetchval(
        "SELECT id FROM social.sectors WHERE parent_sector_id IS NULL LIMIT 1"
    )
    assert root_id is not None
    return await conn.fetchval(
        "INSERT INTO social.sectors (slug, display_name, parent_sector_id) "
        "VALUES ($1, $2, $3) RETURNING id",
        f"alt-{uuid.uuid4().hex[:8]}",
        "Alt Sektör",
        root_id,
    )


async def _drop_committed_sector(conn, sector_id) -> None:
    await conn.execute("DELETE FROM social.package_events WHERE sector_id = $1", sector_id)
    await conn.execute("DELETE FROM social.sector_packages WHERE sector_id = $1", sector_id)
    await conn.execute("DELETE FROM social.sectors WHERE id = $1", sector_id)


@pytest.mark.parametrize(
    "with_previous_active", [False, True], ids=["first_activation", "handover"]
)
async def test_concurrent_activation_of_same_draft_single_winner(
    test_db_setup, with_previous_active
):
    """Aynı taslağı iki transaction aynı anda aktive edemez.

    Kaybeden taraf sessizce başarılı olmamalı; ve denetim izinde TEK bir
    aktivasyon satırı kalmalı. İki olay satırı, olmamış bir devir teslimi
    olmuş gösterir.
    """
    import asyncio

    import asyncpg as _asyncpg

    from .conftest import _require_test_database

    url = _require_test_database(test_db_setup)
    setup = await _asyncpg.connect(url)
    await _init_connection(setup)
    workers: list = []
    sector_id = None
    try:
        sector_id = await _seed_committed_sector(setup)
        if with_previous_active:
            await setup.execute(
                "INSERT INTO social.sector_packages "
                "(sector_id, version, status, schema_version, content) "
                "VALUES ($1, 1, 'active', 1, $2)",
                sector_id,
                _valid_content(),
            )
        draft_id = await setup.fetchval(
            "INSERT INTO social.sector_packages "
            "(sector_id, version, status, schema_version, content) "
            "VALUES ($1, $2, 'draft', 1, $3) RETURNING id",
            sector_id,
            2 if with_previous_active else 1,
            _valid_content(),
        )

        for _ in range(2):
            worker = await _asyncpg.connect(url)
            await _init_connection(worker)
            workers.append(worker)

        async def _try(conn):
            try:
                await activate_package(
                    conn,
                    package_id=draft_id,
                    evidence=_activation_evidence(),
                    actor=ACTOR,
                )
                return "ok"
            except Exception as exc:  # kaybeden taraf AÇIKÇA düşmeli
                return type(exc).__name__

        results = await asyncio.gather(*[_try(worker) for worker in workers])

        assert results.count("ok") == 1, f"tek kazanan bekleniyordu: {results}"
        events = await setup.fetch(
            "SELECT event_type FROM social.package_events WHERE sector_id = $1", sector_id
        )
        assert [e["event_type"] for e in events] == ["activation"], (
            f"denetim izinde tek aktivasyon bekleniyordu: {[e['event_type'] for e in events]}"
        )
        assert await setup.fetchval(
            "SELECT count(*) FROM social.sector_packages "
            "WHERE sector_id = $1 AND status = 'active'",
            sector_id,
        ) == 1
    finally:
        for worker in workers:
            await worker.close()
        if sector_id is not None:
            await _drop_committed_sector(setup, sector_id)
        await setup.close()


# ═══ 9. Olay yazıcısının gerçeğe bağlanması (checkpoint 13, F3) ═════════════


async def test_activation_event_rejects_arbitrary_from_version(pkg_db):
    """Uydurma kaynak sürüm, eksik kaynak sürüm kadar zararlıdır.

    Eski kural asimetrikti: yalnız `from_version` YOKKEN itiraz ediyordu,
    dolayısıyla alakasız bir sürüm numarası denetimsiz geçip denetim izine
    olmamış bir devir teslim yazabiliyordu.
    """
    from app.services.package_events import PackageEventContractError, log_package_event

    sector_id = await _sub_sector(pkg_db)
    await _seed_package(pkg_db, sector_id, version=1, status="active")
    target_id = await _seed_package(pkg_db, sector_id, version=2, status="draft")

    with pytest.raises(PackageEventContractError, match="beklenen 1"):
        await log_package_event(
            pkg_db,
            event_type="activation",
            sector_id=sector_id,
            package_id=target_id,
            from_version=7,
            to_version=2,
            actor=ACTOR,
        )


async def test_activation_event_rejects_write_after_transition(pkg_db):
    """Sıra sözleşmesi artık MEKANİK — yorum değil.

    Olay geçişten SONRA yazılırsa devredilen paket çoktan arşivlenmiştir;
    gerçek aktif sürüm ölçüsü `None` döner ve kaynak sürüm taşıyan olay
    reddedilir. Eskiden bu yazım sessizce kabul ediliyordu.
    """
    from app.services.package_events import PackageEventContractError, log_package_event

    sector_id = await _sub_sector(pkg_db)
    old_id = await _seed_package(pkg_db, sector_id, version=1, status="active")
    new_id = await _seed_package(pkg_db, sector_id, version=2, status="draft")

    # Geçişi elle uygula, olayı SONRA yazmayı dene.
    await pkg_db.execute(
        "UPDATE social.sector_packages SET status = 'archived' WHERE id = $1", old_id
    )
    await pkg_db.execute(
        "UPDATE social.sector_packages SET status = 'active' WHERE id = $1", new_id
    )

    with pytest.raises(PackageEventContractError):
        await log_package_event(
            pkg_db,
            event_type="activation",
            sector_id=sector_id,
            package_id=new_id,
            from_version=1,
            to_version=2,
            actor=ACTOR,
        )


async def test_concurrent_activation_of_different_drafts_is_serializable(test_db_setup):
    """İki FARKLI taslağın eşzamanlı aktivasyonu, sırayla koşmuş gibi biter.

    Bu, sektör kilidinin ölçüsüdür. Kilit olmadan iki transaction hiçbir yerde
    karşılaşmaz (ilk aktivasyonda kilitlenecek aktif satır YOKTUR): ikisi de
    kendi taslağını aktif yapar ve çakışmayı ancak COMMIT anında tek-aktif
    kısmi indeksi yakalar — kaybeden taraf HAM bir kısıt ihlaliyle ölür.
    Sektör satırı her durumda var olduğu için serileştirme çapası odur.

    İddia dar tutuldu: kaybeden taraf düşebilir, ama ham `UniqueViolationError`
    ile DEĞİL; ve son durum her koşulda tutarlı olmalı.
    """
    import asyncio

    import asyncpg as _asyncpg

    from .conftest import _require_test_database

    url = _require_test_database(test_db_setup)
    setup = await _asyncpg.connect(url)
    await _init_connection(setup)
    workers: list = []
    sector_id = None
    try:
        sector_id = await _seed_committed_sector(setup)
        drafts = [
            await setup.fetchval(
                "INSERT INTO social.sector_packages "
                "(sector_id, version, status, schema_version, content) "
                "VALUES ($1, $2, 'draft', 1, $3) RETURNING id",
                sector_id,
                version,
                _valid_content(),
            )
            for version in (1, 2)
        ]

        for _ in range(2):
            worker = await _asyncpg.connect(url)
            await _init_connection(worker)
            workers.append(worker)

        async def _try(conn, draft_id):
            try:
                await activate_package(
                    conn, package_id=draft_id, evidence=_activation_evidence(), actor=ACTOR
                )
                return "ok"
            except LifecycleError:
                return "lifecycle-error"
            except Exception as exc:
                return f"RAW:{type(exc).__name__}"

        results = await asyncio.gather(
            *[_try(worker, draft) for worker, draft in zip(workers, drafts)]
        )

        raw = [r for r in results if r.startswith("RAW:")]
        assert raw == [], f"kaybeden taraf ham veritabanı hatasıyla düştü: {raw}"

        assert await setup.fetchval(
            "SELECT count(*) FROM social.sector_packages "
            "WHERE sector_id = $1 AND status = 'active'",
            sector_id,
        ) == 1, "tek-aktif değişmezi bozuldu"

        events = await setup.fetch(
            "SELECT event_type FROM social.package_events WHERE sector_id = $1", sector_id
        )
        assert len(events) == results.count("ok"), (
            f"olay sayısı başarılı geçiş sayısıyla eşleşmiyor: "
            f"{len(events)} olay, {results.count('ok')} geçiş"
        )
    finally:
        for worker in workers:
            await worker.close()
        if sector_id is not None:
            await _drop_committed_sector(setup, sector_id)
        await setup.close()


# ═══ 10. Kilit ile hedef arasındaki sektör penceresi (checkpoint 13, F4) ════


async def _race_sector_reassignment(test_db_setup, *, transition, seed_status, with_keeper):
    """Kilit alındıktan SONRA hedefin sektörünü değiştirir, sonra geçişi dener.

    Pencere gerçektir: sektör KİLİTSİZ okunuyor, o sektör kilitleniyor, sonra
    hedef yeniden okunurken sektörü YENİDEN OKUNMUYORDU. Araya giren bir
    yeniden-atama, A'nın aktif paketini arşivleyip B'ye ait hedefi aktive
    ettirebiliyor ve olayı A'ya yazdırabiliyordu. Karşılaştır-ve-yaz bunu
    görmez, çünkü sektöre bağlı değildir.

    Araya girme monkeypatch ile DETERMİNİSTİK kurulur — yarışın rastlantısına
    bırakmak bu sınıfı ölçmez.

    `seed_status` hedefin geçişe UYGUN durumu olmalıdır; aksi hâlde fonksiyon
    zaten başka bir gerekçeyle düşer ve test sektör penceresini hiç ölçmez
    (ilk yazımda deaktivasyon dalı tam bunu yaptı — sahte yeşil).
    """
    import asyncpg as _asyncpg

    from .conftest import _require_test_database

    url = _require_test_database(test_db_setup)
    setup = await _asyncpg.connect(url)
    await _init_connection(setup)
    worker = intruder = None
    sector_a = sector_b = None
    try:
        sector_a = await _seed_committed_sector(setup)
        sector_b = await _seed_committed_sector(setup)
        keeper_id = None
        if with_keeper:
            keeper_id = await setup.fetchval(
                "INSERT INTO social.sector_packages "
                "(sector_id, version, status, schema_version, content) "
                "VALUES ($1, 1, 'active', 1, $2) RETURNING id",
                sector_a,
                _valid_content(),
            )
        target_id = await setup.fetchval(
            "INSERT INTO social.sector_packages "
            "(sector_id, version, status, schema_version, content) "
            "VALUES ($1, 2, $2, 1, $3) RETURNING id",
            sector_a,
            seed_status,
            _valid_content(),
        )

        worker = await _asyncpg.connect(url)
        await _init_connection(worker)
        intruder = await _asyncpg.connect(url)
        await _init_connection(intruder)

        original = sector_package_lifecycle._lock_sector
        moved = {"done": False}

        async def _lock_then_move(db, sector_id):
            await original(db, sector_id)
            if not moved["done"]:
                moved["done"] = True
                await intruder.execute(
                    "UPDATE social.sector_packages SET sector_id = $2 WHERE id = $1",
                    target_id,
                    sector_b,
                )

        sector_package_lifecycle._lock_sector = _lock_then_move
        try:
            with pytest.raises(LifecycleError):
                await transition(worker, target_id)
        finally:
            sector_package_lifecycle._lock_sector = original

        assert moved["done"], "araya girme hiç koşmadı — test kendini ölçmüyor"
        assert (
            await setup.fetchval(
                "SELECT status FROM social.sector_packages WHERE id = $1", target_id
            )
            == seed_status
        ), "reddedilen geçiş yine de hedefin durumunu değiştirdi"
        if keeper_id is not None:
            assert (
                await setup.fetchval(
                    "SELECT status FROM social.sector_packages WHERE id = $1", keeper_id
                )
                == "active"
            ), "yanlış sektörün aktif paketi arşivlendi"
        for sector in (sector_a, sector_b):
            assert (
                await setup.fetchval(
                    "SELECT count(*) FROM social.package_events WHERE sector_id = $1", sector
                )
                == 0
            ), "reddedilen geçiş olay yazdı"
    finally:
        for conn in (worker, intruder):
            if conn is not None:
                await conn.close()
        for sector in (sector_a, sector_b):
            if sector is not None:
                await _drop_committed_sector(setup, sector)
        await setup.close()


async def test_activation_rejects_sector_reassignment_under_lock(test_db_setup):
    async def _transition(conn, target_id):
        await activate_package(
            conn, package_id=target_id, evidence=_activation_evidence(), actor=ACTOR
        )

    await _race_sector_reassignment(
        test_db_setup, transition=_transition, seed_status="draft", with_keeper=True
    )


async def test_deactivation_rejects_sector_reassignment_under_lock(test_db_setup):
    """Hedef GERÇEKTEN aktif olmalı — aksi hâlde fonksiyon başka gerekçeyle düşer."""

    async def _transition(conn, target_id):
        await deactivate_package(conn, package_id=target_id, actor=ACTOR)

    await _race_sector_reassignment(
        test_db_setup, transition=_transition, seed_status="active", with_keeper=False
    )
