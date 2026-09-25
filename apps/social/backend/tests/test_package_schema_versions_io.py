"""Saklı paket SATIRIN şema sürümüyle okunur ve yazılır (tasarım notu 2026-09-25 §3.9, §4; plan Task 2).

Canlıdaki 1. sürüm paket yeni kodla okunmaya devam eder; 2. sürüm satırı da okunur.
Geri dönüş tabanının kanıtı: şema-2 içerik şema-1 kuralıyla okunamaz ve bu SESSİZ
değildir (`package_read_error` → yönetici bildirimi).
"""

from __future__ import annotations

import itertools
import uuid

import pytest

from app.core.database import _init_connection
from app.services.package_events import ADMIN_NOTIFIED_EVENTS
from app.services.sector_package_lifecycle import insert_draft
from app.services.sector_packages import resolve_package_context

from .test_package_stamp_and_events import _seed_brand
from .test_sector_packages_service import _valid_content

ACTOR = "eray"


def _v2_content() -> dict:
    return _valid_content(sektor_gercekleri=["22 ayar saf değildir; saf altın 24 ayardır."])


@pytest.fixture
async def pkg_db(db):
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


async def _seed_active(db, *, schema_version: int, content: dict):
    """Aktif paket satırı — yazım kapısını ATLAR (okuma tarafı ölçülüyor)."""
    sub_id = await _sub_sector(db)
    package_id = await db.fetchval(
        "INSERT INTO social.sector_packages (sector_id, version, status, schema_version, content) "
        "VALUES ($1, 1, 'active', $2, $3) RETURNING id",
        sub_id,
        schema_version,
        content,
    )
    _, brand_id = await _seed_brand(db, sub_sector_id=sub_id)
    return sub_id, package_id, brand_id


async def _events(db, brand_id):
    return await db.fetch(
        "SELECT event_type, detail FROM social.package_events WHERE brand_id = $1",
        brand_id,
    )


async def test_live_v1_row_reads_under_new_code(pkg_db):
    sub_id, package_id, brand_id = await _seed_active(
        pkg_db, schema_version=1, content=_valid_content()
    )

    context = await resolve_package_context(pkg_db, {"id": brand_id, "sub_sector_id": sub_id})

    assert context is not None
    assert context.package_id == package_id
    assert "sektor_gercekleri" not in context.content
    assert await _events(pkg_db, brand_id) == []


async def test_v2_row_reads_under_new_code(pkg_db):
    sub_id, package_id, brand_id = await _seed_active(
        pkg_db, schema_version=2, content=_v2_content()
    )

    context = await resolve_package_context(pkg_db, {"id": brand_id, "sub_sector_id": sub_id})

    assert context is not None
    assert context.package_id == package_id
    assert context.content["sektor_gercekleri"] == ["22 ayar saf değildir; saf altın 24 ayardır."]
    assert await _events(pkg_db, brand_id) == []


async def test_v2_content_under_v1_rules_falls_back_with_read_error(pkg_db):
    """Geri dönüş tabanı (spec §4): şema-1 satırına sızan onuncu alan okunamaz — ve SESSİZ değil."""
    sub_id, _, brand_id = await _seed_active(pkg_db, schema_version=1, content=_v2_content())

    context = await resolve_package_context(pkg_db, {"id": brand_id, "sub_sector_id": sub_id})

    assert context is None
    rows = await _events(pkg_db, brand_id)
    assert [r["event_type"] for r in rows] == ["package_read_error"]
    assert rows[0]["detail"]["reason"] == "structural"
    assert "sektor_gercekleri" in rows[0]["detail"]["first_problem"]
    assert "package_read_error" in ADMIN_NOTIFIED_EVENTS


_CONTENTS = {1: _valid_content, 2: _v2_content}


@pytest.mark.parametrize(
    ("content_version", "row_version"), list(itertools.product((1, 2), (1, 2)))
)
async def test_insert_draft_rejects_content_schema_mismatch_generated(
    pkg_db, content_version, row_version
):
    sector_id = await _sub_sector(pkg_db)
    content = _CONTENTS[content_version]()

    if content_version != row_version:
        with pytest.raises(ValueError, match="yazım kapısını geçmedi"):
            await insert_draft(
                pkg_db,
                sector_id=sector_id,
                content=content,
                schema_version=row_version,
                actor=ACTOR,
            )
        count = await pkg_db.fetchval(
            "SELECT count(*) FROM social.sector_packages WHERE sector_id = $1", sector_id
        )
        assert count == 0, "uyuşmayan içerik/sürüm çifti taslağa yazıldı"
    else:
        package_id = await insert_draft(
            pkg_db,
            sector_id=sector_id,
            content=content,
            schema_version=row_version,
            actor=ACTOR,
        )
        stored = await pkg_db.fetchval(
            "SELECT schema_version FROM social.sector_packages WHERE id = $1", package_id
        )
        assert stored == row_version


async def test_update_draft_row_gates_by_version_and_writes_it(pkg_db):
    """İkinci taslak yazıcısı (K-106 yerinde güncelleme) da AYNI kapıdan geçer.

    Plan yalnız `insert_draft`'ı sayar; `_update_draft_row` aynı yazım kapısını
    paylaşır. Sürümsüz kalsaydı uyuşmayan içerik/sürüm çifti taslağa buradan
    girerdi. Sürüm içerikle AYNI güncellemede yazılır — satır çifti bölünmez.
    """
    from app.services.sector_package_lifecycle import _update_draft_row

    sector_id = await _sub_sector(pkg_db)
    package_id = await insert_draft(
        pkg_db, sector_id=sector_id, content=_valid_content(), schema_version=1, actor=ACTOR
    )
    # Plan 1 olay satırı karar günlüğü şemasını geçmez; boş günlük bütünlük
    # kapısını atlar ve bu testi yalnız içerik/sürüm kapısına odaklar.
    log: list[dict] = []

    with pytest.raises(ValueError, match="yazım kapısını geçmedi"):
        await _update_draft_row(
            pkg_db,
            package_id=package_id,
            sector_id=sector_id,
            content=_v2_content(),
            schema_version=1,
            decision_log=log,
        )

    await _update_draft_row(
        pkg_db,
        package_id=package_id,
        sector_id=sector_id,
        content=_v2_content(),
        schema_version=2,
        decision_log=log,
    )
    row = await pkg_db.fetchrow(
        "SELECT schema_version, content FROM social.sector_packages WHERE id = $1", package_id
    )
    assert row["schema_version"] == 2
    assert "sektor_gercekleri" in row["content"]
