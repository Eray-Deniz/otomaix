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


# Plan 2'nin BAĞLI olduğu 032 yüzeyi — kolon imzası (ad · tip · null'lanabilirlik).
# Kaynak: shared/db/migrations/032_sector_packages.sql. Migration'ın KENDİ garanti bloğu
# yalnız kısıtları ve indeksleri denetler; kolon imzasını denetleMEZ (bilinen boşluk,
# `CURRENT.md` → migration-guarantee-block-signature-gap). Bu yüzden imza kapısı BURADA.
MIGRATION_032_COLUMNS = {
    "sector_research_artifacts": {
        "id": ("uuid", "NO"),
        "run_id": ("text", "NO"),
        "sector_slug": ("text", "NO"),
        "kind": ("text", "NO"),
        "source": ("text", "NO"),
        "brief_ref": ("text", "YES"),
        "content_md": ("text", "NO"),
        "created_at": ("timestamp with time zone", "YES"),
    },
    "sector_packages": {
        "id": ("uuid", "NO"),
        "sector_id": ("uuid", "NO"),
        "version": ("integer", "NO"),
        "status": ("text", "NO"),
        "schema_version": ("integer", "NO"),
        "content": ("jsonb", "NO"),
        "decision_log": ("jsonb", "NO"),
        "run_id": ("text", "YES"),  # K-110 AÇIK — nullable KALIR
        "created_at": ("timestamp with time zone", "YES"),
        "activated_at": ("timestamp with time zone", "YES"),
    },
    "generation_stamps": {
        "id": ("uuid", "NO"),
        "brand_id": ("uuid", "NO"),
        "package_id": ("uuid", "NO"),
        "package_version": ("integer", "NO"),
        "created_at": ("timestamp with time zone", "YES"),
        "consumed_at": ("timestamp with time zone", "YES"),
    },
}

# Taşıyıcı tablolara EKLENEN kolonlar (tablonun tamamı 032'nin değil).
MIGRATION_032_ADDED_COLUMNS = {
    ("brands", "sub_sector_id"): ("uuid", "YES"),
    ("posts", "package_id"): ("uuid", "YES"),
    ("posts", "package_version"): ("integer", "YES"),
}

# Garantiler: kısıt adı -> (tip, ek yüklem). 'f' = MATCH FULL (confmatchtype).
MIGRATION_032_CONSTRAINTS = {
    "sector_packages_sector_version_key": "u",
    "sector_packages_id_version_key": "u",
    "posts_package_stamp_fkey": "f",
    "generation_stamps_package_fkey": "f",
}

MIGRATION_032_TRIGGERS = (
    "sector_research_artifacts_append_only",
    "sector_research_artifacts_no_truncate",
    "brands_sub_sector_must_be_sub",
    "sector_packages_sector_must_be_sub",
    "sectors_reject_reparenting",
)


async def _column_signature(db, table: str) -> dict:
    rows = await db.fetch(
        "SELECT column_name, data_type, is_nullable FROM information_schema.columns "
        "WHERE table_schema = 'social' AND table_name = $1",
        table,
    )
    return {r["column_name"]: (r["data_type"], r["is_nullable"]) for r in rows}


async def test_migration_032_column_signatures_delivered(db):
    """Üç tablonun kolon imzası (ad · tip · null'lanabilirlik) TAM eşleşir.

    Kapalı küme karşılaştırması: eksik kolon da FAZLA kolon da bulgudur — Plan 2
    yazma yüzeyi şemanın tamamına bakar, seçilmiş bir alt kümesine değil.
    """
    for table, expected in MIGRATION_032_COLUMNS.items():
        observed = await _column_signature(db, table)
        assert observed, f"social.{table} yok — 032 teslim edilmemiş"
        assert observed == expected, (
            f"social.{table} kolon imzası sözleşmeden SAPTI\n"
            f"beklenen: {sorted(expected.items())}\n"
            f"gözlenen: {sorted(observed.items())}"
        )


async def test_migration_032_added_columns_on_carrier_tables(db):
    """`brands.sub_sector_id` + `posts` damga çifti — 032'nin eklediği kolonlar."""
    for (table, column), expected in MIGRATION_032_ADDED_COLUMNS.items():
        observed = await _column_signature(db, table)
        assert column in observed, f"social.{table}.{column} yok"
        assert observed[column] == expected, (
            f"social.{table}.{column} imzası saptı: {observed[column]} != {expected}"
        )


async def test_migration_032_constraints_delivered(db):
    """İki benzersizlik kısıtı + iki bileşik FK; damga FK'sı MATCH FULL."""
    rows = await db.fetch(
        "SELECT c.conname, c.contype, c.confmatchtype FROM pg_constraint AS c "
        "JOIN pg_namespace AS n ON n.oid = c.connamespace WHERE n.nspname = 'social'"
    )
    # asyncpg `"char"` kolonlarını bayt olarak döner — metne çevrilir.
    def _char(value):
        return value.decode() if isinstance(value, (bytes, bytearray)) else value

    observed = {
        r["conname"]: (_char(r["contype"]), _char(r["confmatchtype"])) for r in rows
    }
    for name, expected in MIGRATION_032_CONSTRAINTS.items():
        assert name in observed, f"kısıt yok: {name}"
        contype, matchtype = observed[name]
        if expected == "f":
            assert contype == "f", f"{name} yabancı anahtar değil ({contype})"
        else:
            assert contype == expected, f"{name} tipi {contype}, beklenen {expected}"
    # K-07 damgası: yarım çift (yalnız id VEYA yalnız version) İMKÂNSIZ olmalı.
    assert observed["posts_package_stamp_fkey"][1] == "f", (
        "posts damga FK'sı MATCH FULL değil — yarım-NULL çift sızabilir"
    )


async def test_migration_032_single_active_index_is_unique_and_partial(db):
    """Tek-aktif garantisi: UNIQUE + KISMİ + `sector_id` anahtarlı + geçerli.

    Adın var olması yetmez; aynı adla benzersiz OLMAYAN ya da yanlış kolonla
    kurulmuş bir indeks garantiyi sessizce boşaltırdı.
    """
    row = await db.fetchrow(
        "SELECT i.indisunique, i.indisvalid, i.indpred IS NOT NULL AS is_partial, "
        "       pg_get_indexdef(i.indexrelid) AS definition "
        "  FROM pg_index AS i "
        "  JOIN pg_class AS c ON c.oid = i.indexrelid "
        "  JOIN pg_namespace AS n ON n.oid = c.relnamespace "
        " WHERE n.nspname = 'social' AND c.relname = 'uq_sector_packages_single_active'"
    )
    assert row is not None, "uq_sector_packages_single_active yok"
    assert row["indisunique"], "indeks UNIQUE değil — tek-aktif garantisi yok"
    assert row["indisvalid"], "indeks GEÇERSİZ (invalid) — zorlamıyor"
    assert row["is_partial"], "indeks kısmi değil — arşivlenmiş sürümleri de kilitler"
    assert "(sector_id)" in row["definition"], row["definition"]
    assert "status = 'active'" in row["definition"], row["definition"]


async def test_migration_032_triggers_delivered(db):
    """Salt-ekleme · alt sektör zorlaması · yeniden-ebeveynleme reddi ayakta."""
    rows = await db.fetch(
        "SELECT t.tgname FROM pg_trigger AS t "
        "  JOIN pg_class AS c ON c.oid = t.tgrelid "
        "  JOIN pg_namespace AS n ON n.oid = c.relnamespace "
        " WHERE n.nspname = 'social' AND NOT t.tgisinternal"
    )
    observed = {r["tgname"] for r in rows}
    missing = [name for name in MIGRATION_032_TRIGGERS if name not in observed]
    assert not missing, f"eksik tetikleyici(ler): {missing}"


async def test_migration_032_value_checks_delivered(db):
    """`kind` ve `status` kapalı kümeleri DB düzeyinde zorlanıyor."""
    definitions = {
        r["conname"]: r["definition"]
        for r in await db.fetch(
            "SELECT c.conname, pg_get_constraintdef(c.oid) AS definition "
            "  FROM pg_constraint AS c "
            "  JOIN pg_namespace AS n ON n.oid = c.connamespace "
            " WHERE n.nspname = 'social' AND c.contype = 'c'"
        )
    }
    joined = " ".join(definitions.values())
    for value in ("research", "review", "synthesis"):
        assert f"'{value}'" in joined, f"kind kapalı kümesinde {value} yok"
    for value in ("draft", "active", "archived"):
        assert f"'{value}'" in joined, f"status kapalı kümesinde {value} yok"


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
