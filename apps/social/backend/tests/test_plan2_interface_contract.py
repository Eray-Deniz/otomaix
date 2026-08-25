"""Plan 2'ye teslim edilen arayüzlerin ÇAĞRILABİLİRLİK kanıtı (plan Task 16).

Bu dosya davranış testi DEĞİLDİR — davranışın kendisi Task 8-14'ün testlerinde
ölçülür. Burada ölçülen tek şey **teslim sözleşmesidir:** planın "Plan 2'ye
teslim edilen arayüzler" bölümündeki HER madde, orada BELGELENEN argümanlarla
import edilip çağrılabiliyor mu.

Neden ayrı bir dosya: teslim listesi bir prose bölümüdür ve prose sessizce
bayatlar. Bir imza değişir, liste eski hâlinde kalır ve Plan 2 yürütücüsü
çalışmayan bir sözleşmeye göre kod yazar. Bu dosya listeyi çalıştırılabilir
hâle getirir — imza değişirse burası KIRILIR.

Kapsam sınırı (dürüst etiket): bu testler arayüzlerin VAR ve ÇAĞRILABİLİR
olduğunu kanıtlar; Plan 2'nin onları DOĞRU kullanacağını kanıtlamaz.
"""

from __future__ import annotations

import uuid

import pytest

from app.core.database import _init_connection
from app.services.notifications import record_admin_event
from app.services.sector_packages import (
    ActivationGateEvidence,
    GateNotSatisfied,
    RollbackGateEvidence,
    SectorPackageContext,
    ValidationResult,
    activate_package,
    deactivate_package,
    insert_draft,
    motion_pool,
    normalize_special_day_key,
    rollback_package,
    scene_pool,
    validate_package_content,
)

from .prompt_regression.capture import (
    FIXTURES_DIR,
    assert_matches_fixture,
    capture_anthropic_calls,
)
from .test_sector_packages_service import CUMHURIYET_KEY, _valid_content

ACTOR = "plan2@otomaix"


# ─── Ortak kurulum ──────────────────────────────────────────────────────────


@pytest.fixture
async def pkg_db(db):
    """Üretimin KENDİ bağlantı yapılandırması + yazım kapısının takvim besini.

    `insert_draft` takvim anahtarlarını DB'den okur; `_valid_content()` bir
    `ozel_gun` anahtarı taşır. Takvim satırı olmadan kapı — doğru olarak —
    reddeder ve test arayüzü değil kurulumu ölçerdi.
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


# ─── Madde 1: Migration 032 şeması ──────────────────────────────────────────


async def test_migration_032_tables_and_columns_delivered(db):
    """İki tablo + Plan 2'nin yazdığı kolonlar + tek-aktif garantisi ayakta."""
    for table in ("sector_research_artifacts", "sector_packages"):
        exists = await db.fetchval(
            "SELECT to_regclass($1) IS NOT NULL", f"social.{table}"
        )
        assert exists, f"social.{table} yok — 032 teslim edilmemiş"

    columns = {
        row["column_name"]
        for row in await db.fetch(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema = 'social' AND table_name = 'sector_packages'"
        )
    }
    # `insert_draft`'ın yazdığı küme — Plan 2 bu kolonlara BAĞLIDIR.
    assert {
        "id",
        "sector_id",
        "version",
        "status",
        "schema_version",
        "content",
        "decision_log",
        "run_id",
    } <= columns

    single_active = await db.fetchval(
        "SELECT count(*) FROM pg_indexes WHERE schemaname = 'social' "
        "AND indexname = 'uq_sector_packages_single_active'"
    )
    assert single_active == 1, "tek-aktif garantisi (kısmi indeks) yok"


async def test_plan2_write_surface_produces_draft_only(pkg_db):
    """K-135'in kod karşılığı: `insert_draft` YALNIZ `draft` üretir."""
    sector_id = await _sub_sector(pkg_db)
    package_id = await insert_draft(
        pkg_db,
        sector_id=sector_id,
        content=_valid_content(),
        schema_version=1,
        run_id=None,
        actor=ACTOR,
    )
    row = await pkg_db.fetchrow(
        "SELECT status, version FROM social.sector_packages WHERE id = $1", package_id
    )
    assert row["status"] == "draft"
    assert row["version"] == 1


# ─── Madde 2: normalize_special_day_key ─────────────────────────────────────


def test_normalize_special_day_key_documented_signature():
    """`(name: str) -> str` — yazım ve okuma AYNI anahtarı görür (K-01b)."""
    key = normalize_special_day_key("Cumhuriyet Bayramı")
    assert isinstance(key, str) and key
    assert key == CUMHURIYET_KEY
    # Tek modül olmanın gözlenebilir sonucu: aynı ad her çağrıda aynı anahtar.
    assert normalize_special_day_key("  Cumhuriyet Bayramı  ") == key


# ─── Madde 3: validate_package_content ──────────────────────────────────────


def test_validate_package_content_documented_signature():
    """`(content, *, banned_brand_names, holiday_keys) -> ValidationResult`."""
    result = validate_package_content(
        _valid_content(),
        banned_brand_names=["Altınbaş"],
        holiday_keys={CUMHURIYET_KEY},
    )
    assert isinstance(result, ValidationResult)
    assert result.ok, result.errors

    # `holiday_keys` gerçekten tüketiliyor: takvimde olmayan anahtar REDDEDİLİR.
    kapali = validate_package_content(
        _valid_content(), banned_brand_names=[], holiday_keys=set()
    )
    assert not kapali.ok


# ─── Madde 4-5: insert_draft → activate → rollback → deactivate ─────────────


async def test_insert_draft_and_activate_chain_end_to_end(pkg_db):
    """Geçerli yazım + KANITLI aktivasyon zinciri uçtan uca koşar."""
    sector_id = await _sub_sector(pkg_db)
    package_id = await insert_draft(
        pkg_db,
        sector_id=sector_id,
        content=_valid_content(),
        schema_version=1,
        actor=ACTOR,
    )
    assert isinstance(package_id, uuid.UUID)

    await activate_package(
        pkg_db,
        package_id=package_id,
        evidence=ActivationGateEvidence(
            activation_eligible=True,
            open_questions_count=0,
            katman1_passed=True,
            checklist_approved=True,
        ),
        actor=ACTOR,
    )
    status = await pkg_db.fetchval(
        "SELECT status FROM social.sector_packages WHERE id = $1", package_id
    )
    assert status == "active"


async def test_rollback_package_takes_its_own_evidence(pkg_db):
    """Rollback AYRI kanıt tipi ister; aktivasyon kanıtı KABUL EDİLMEZ."""
    sector_id = await _sub_sector(pkg_db)
    first = await insert_draft(
        pkg_db, sector_id=sector_id, content=_valid_content(), schema_version=1, actor=ACTOR
    )
    activation = ActivationGateEvidence(
        activation_eligible=True,
        open_questions_count=0,
        katman1_passed=True,
        checklist_approved=True,
    )
    await activate_package(pkg_db, package_id=first, evidence=activation, actor=ACTOR)

    second = await insert_draft(
        pkg_db, sector_id=sector_id, content=_valid_content(), schema_version=1, actor=ACTOR
    )
    await activate_package(pkg_db, package_id=second, evidence=activation, actor=ACTOR)

    # Kanıt tipleri PAYLAŞILMAZ — aktivasyon kanıtıyla rollback yapılamaz.
    with pytest.raises(GateNotSatisfied):
        await rollback_package(
            pkg_db, sector_id=sector_id, to_version=1, evidence=activation, actor=ACTOR
        )

    await rollback_package(
        pkg_db,
        sector_id=sector_id,
        to_version=1,
        evidence=RollbackGateEvidence(manager_approved=True, katman1_passed=True),
        actor=ACTOR,
    )
    assert (
        await pkg_db.fetchval(
            "SELECT status FROM social.sector_packages WHERE id = $1", first
        )
        == "active"
    )


async def test_deactivate_package_documented_signature(pkg_db):
    """`(db, *, package_id, actor)` — kanıt İSTEMEZ (K-38 acil kol)."""
    sector_id = await _sub_sector(pkg_db)
    package_id = await insert_draft(
        pkg_db, sector_id=sector_id, content=_valid_content(), schema_version=1, actor=ACTOR
    )
    await activate_package(
        pkg_db,
        package_id=package_id,
        evidence=ActivationGateEvidence(
            activation_eligible=True,
            open_questions_count=0,
            katman1_passed=True,
            checklist_approved=True,
        ),
        actor=ACTOR,
    )
    await deactivate_package(pkg_db, package_id=package_id, actor=ACTOR)
    assert (
        await pkg_db.fetchval(
            "SELECT status FROM social.sector_packages WHERE id = $1", package_id
        )
        != "active"
    )


# ─── Madde 6: record_admin_event ────────────────────────────────────────────


async def test_record_admin_event_documented_signature(db):
    """`(db, *, kind, payload, idempotency_key) -> uuid` — outbox teslimi."""
    await _init_connection(db)
    key = f"plan2-contract-{uuid.uuid4().hex}"
    event_id = await record_admin_event(
        db,
        kind="package_activated",
        payload={"sector_id": str(uuid.uuid4())},
        idempotency_key=key,
    )
    assert isinstance(event_id, uuid.UUID)
    # Aynı anahtar YENİ satır üretmez — Plan 2 tur takibi buna dayanır.
    again = await record_admin_event(
        db, kind="package_activated", payload={"farkli": True}, idempotency_key=key
    )
    assert again == event_id


# ─── Madde 7: Katman-1 harness ──────────────────────────────────────────────


def test_katman1_harness_is_delivered_and_live(monkeypatch):
    """Harness import edilebilir, fixture'lar donmuş, kapı gerçekten ölçüyor."""
    # Dondurma bayrağı asılı kalmışsa aşağıdaki çağrı fixture'ı EZERDİ.
    monkeypatch.delenv("PROMPT_REGRESSION_UPDATE", raising=False)

    frozen = sorted(p.name for p in FIXTURES_DIR.glob("*.txt"))
    assert frozen, "Katman-1 fixture kümesi boş — donmuş taban yok"

    assert callable(capture_anthropic_calls)
    # Pozitif kontrol: kapı bir sapmayı gerçekten YAKALIYOR (no-op değil).
    with pytest.raises(AssertionError):
        assert_matches_fixture(frozen[0][: -len(".txt")], "bozulmuş prompt")


# ─── Madde 8: video_kodlar İKİ HAVUZ ────────────────────────────────────────


def test_video_kodlar_delivers_two_pools():
    """`hareket` + `sahne`, ikisi de liste — tek havuz sözleşmeyi karşılamaz."""
    tek_havuz = _valid_content(video_kodlar={"hareket": ["Slow orbit."]})
    result = validate_package_content(
        tek_havuz, banned_brand_names=[], holiday_keys={CUMHURIYET_KEY}
    )
    assert not result.ok
    assert any("video_kodlar" in error for error in result.errors)

    tek_cumle = _valid_content(
        video_kodlar={"hareket": "Slow orbit.", "sahne": "Boutique interior."}
    )
    result = validate_package_content(
        tek_cumle, banned_brand_names=[], holiday_keys={CUMHURIYET_KEY}
    )
    assert not result.ok

    # Okuma tarafı da İKİ havuzu ayrı ayrı görüyor.
    context = SectorPackageContext(
        package_id=uuid.uuid4(),
        version=1,
        content=_valid_content(),
        sub_sector_slug="kuyumculuk",
    )
    assert len(motion_pool(context)) == 2
    assert len(scene_pool(context)) == 2
