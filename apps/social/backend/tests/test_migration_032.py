"""Migration 032 şema sözleşmesi — deterministik DB garantileri (Task 2).

Bu dosya `shared/db/migrations/032_sector_packages.sql`'in bağlayıcı
invariantlarını kanıtlar (plan Task 2 · spec §14.1):

1. `sector_research_artifacts` UPDATE/DELETE istisna fırlatır (salt-ekleme).
2. INSERT başarılı + `run_id` ile sorgulanabilir.
3. Sektör başına ikinci `active` paket kısmi indeksten döner.
4. `(sector_id, version)` ihlali hata verir.
5. `brands.sub_sector_id`'ye kök sektör satırı yazımı reddedilir.
6. `sub_sector_id` NULL kalabilir (geri doldurma yok).

Ek olarak K-07 damga temsili (posts bileşik FK + MATCH FULL),
`social.generation_stamps` sözleşmesi ve reparenting yasağı doğrulanır.

Son bölüm (F7) migration'ın kendi fail-closed garanti doğrulamasını sınar: aynı
adda yanlış tanımlı bir nesne varken yeniden uygulama DURMALI, doğru şema
üstünde ise rc=0 kalmalı (idempotentlik). Tanımı DOĞRU bırakıp yalnız
uygulanma durumunu kapatan vakalar (geçersiz indeks, devre dışı FK iç
tetikleyicileri) de aynı bölümde sınanır.

Alt sektör satırları test İÇİNDE açılır — canlı seed dosyasına satır eklenmez.
"""

from __future__ import annotations

import subprocess
import uuid

import asyncpg
import pytest

from tests import conftest as infra

# jsonb kolonlarına test tarafından geçirilen sabit içerik. asyncpg'nin
# varsayılan jsonb kodlayıcısı metin kabul eder — `::jsonb` cast'e gerek yok.
CONTENT_JSON = '{"kapsam": "test alt sektoru"}'


# --- Kurulum yardımcıları --------------------------------------------------


def _slug(prefix: str) -> str:
    """Test içinde çakışmayan slug üretir (her test kendi transaction'ında)."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


async def _new_root_sector(db, prefix: str = "t032-kok") -> uuid.UUID:
    slug = _slug(prefix)
    return await db.fetchval(
        """
        INSERT INTO social.sectors (slug, display_name)
        VALUES ($1, $2)
        RETURNING id
        """,
        slug,
        slug,
    )


async def _new_sub_sector(db, parent_id, prefix: str = "t032-alt") -> uuid.UUID:
    slug = _slug(prefix)
    return await db.fetchval(
        """
        INSERT INTO social.sectors (slug, display_name, parent_sector_id)
        VALUES ($1, $2, $3)
        RETURNING id
        """,
        slug,
        slug,
        parent_id,
    )


async def _new_account(db) -> uuid.UUID:
    return await db.fetchval(
        "INSERT INTO social.accounts (email, name) VALUES ($1, $2) RETURNING id",
        f"t032-{uuid.uuid4().hex[:10]}@example.test",
        "T032 Hesap",
    )


async def _new_workspace(db, account_id) -> uuid.UUID:
    return await db.fetchval(
        "INSERT INTO social.workspaces (account_id, name) VALUES ($1, $2) RETURNING id",
        account_id,
        "T032 Workspace",
    )


async def _new_brand(db, workspace_id=None, sub_sector_id=None) -> uuid.UUID:
    return await db.fetchval(
        """
        INSERT INTO social.brands (workspace_id, name, sub_sector_id)
        VALUES ($1, $2, $3)
        RETURNING id
        """,
        workspace_id,
        "T032 Marka",
        sub_sector_id,
    )


async def _new_package(
    db, sector_id, *, version: int = 1, status: str = "draft"
) -> uuid.UUID:
    return await db.fetchval(
        """
        INSERT INTO social.sector_packages
            (sector_id, version, status, schema_version, content)
        VALUES ($1, $2, $3, 1, $4)
        RETURNING id
        """,
        sector_id,
        version,
        status,
        CONTENT_JSON,
    )


async def _new_artifact(db, *, run_id: str, sector_slug: str, kind: str = "research"):
    return await db.fetchval(
        """
        INSERT INTO social.sector_research_artifacts
            (run_id, sector_slug, kind, source, content_md)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
        """,
        run_id,
        sector_slug,
        kind,
        "claude-research",
        "# ham kanit",
    )


async def _rejected(db, sql: str, *args) -> asyncpg.PostgresError:
    """SQL'i savepoint içinde koşar; hata BEKLER ve istisnayı döndürür.

    Savepoint sayesinde dış (fixture) transaction'ı kullanılabilir kalır —
    aynı test hatadan sonra da sorgu koşabilir.
    """
    try:
        async with db.transaction():
            await db.execute(sql, *args)
    except asyncpg.PostgresError as exc:
        return exc
    raise AssertionError(f"Beklenen DB reddi gerçekleşmedi:\n{sql}")


# --- 1-2. Salt-ekleme tetikleyicisi ---------------------------------------


async def test_artifacts_append_only_update_raises(db):
    """Ham kanıt katmanı değiştirilemez: UPDATE istisna fırlatır."""
    artifact_id = await _new_artifact(db, run_id="run-1", sector_slug="kuafor")

    error = await _rejected(
        db,
        "UPDATE social.sector_research_artifacts SET content_md = $1 WHERE id = $2",
        "degistirilmis",
        artifact_id,
    )
    assert "salt-ekleme" in str(error).lower() or "append" in str(error).lower()

    # Satır ve içeriği bozulmadan duruyor.
    content = await db.fetchval(
        "SELECT content_md FROM social.sector_research_artifacts WHERE id = $1",
        artifact_id,
    )
    assert content == "# ham kanit"


async def test_artifacts_append_only_delete_raises(db):
    """Ham kanıt katmanı silinemez: DELETE istisna fırlatır."""
    artifact_id = await _new_artifact(db, run_id="run-2", sector_slug="kuafor")

    error = await _rejected(
        db,
        "DELETE FROM social.sector_research_artifacts WHERE id = $1",
        artifact_id,
    )
    assert "salt-ekleme" in str(error).lower() or "append" in str(error).lower()

    still_there = await db.fetchval(
        "SELECT count(*) FROM social.sector_research_artifacts WHERE id = $1",
        artifact_id,
    )
    assert still_there == 1


# --- 3. INSERT + run_id sorgusu -------------------------------------------


async def test_artifacts_insert_and_query_by_run_id(db):
    """INSERT serbest; `run_id` katmanlar arası bağdır; slug FK DEĞİLDİR (K-08a)."""
    run_id = f"run-{uuid.uuid4().hex[:8]}"
    # Sektör satırı AÇILMADAN araştırma koşabilmeli (K-08a gerekçesi).
    orphan_slug = _slug("kayitsiz-alt-sektor")

    for kind in ("research", "review", "synthesis"):
        await _new_artifact(db, run_id=run_id, sector_slug=orphan_slug, kind=kind)

    rows = await db.fetch(
        """
        SELECT kind, source, brief_ref, created_at
        FROM social.sector_research_artifacts
        WHERE run_id = $1 AND sector_slug = $2
        ORDER BY kind
        """,
        run_id,
        orphan_slug,
    )
    assert [row["kind"] for row in rows] == ["research", "review", "synthesis"]
    assert all(row["source"] == "claude-research" for row in rows)
    assert all(row["brief_ref"] is None for row in rows)
    assert all(row["created_at"] is not None for row in rows)

    # `kind` kapalı kümedir.
    error = await _rejected(
        db,
        """
        INSERT INTO social.sector_research_artifacts
            (run_id, sector_slug, kind, source, content_md)
        VALUES ($1, $2, 'gossip', 'x', 'y')
        """,
        run_id,
        orphan_slug,
    )
    assert isinstance(error, asyncpg.exceptions.CheckViolationError)

    # `(sector_slug, run_id)` indeksi sözleşmenin parçasıdır.
    index_columns = await db.fetchval(
        """
        SELECT count(*) FROM pg_indexes
        WHERE schemaname = 'social'
          AND tablename = 'sector_research_artifacts'
          AND indexdef LIKE '%(sector_slug, run_id)%'
        """
    )
    assert index_columns == 1, "(sector_slug, run_id) indeksi yok"


# --- 4-5. sector_packages benzersizlik garantileri ------------------------


async def test_packages_single_active_partial_index(db):
    """Sektör başına tek `active`; `draft`/`archived` sınırsız."""
    root_id = await _new_root_sector(db)
    sub_id = await _new_sub_sector(db, root_id)
    other_sub_id = await _new_sub_sector(db, root_id)

    await _new_package(db, sub_id, version=1, status="active")

    error = await _rejected(
        db,
        """
        INSERT INTO social.sector_packages
            (sector_id, version, status, schema_version, content)
        VALUES ($1, 2, 'active', 1, $2)
        """,
        sub_id,
        CONTENT_JSON,
    )
    assert isinstance(error, asyncpg.exceptions.UniqueViolationError)

    # Aynı sektörde ikinci `draft` ve `archived` serbesttir.
    await _new_package(db, sub_id, version=2, status="draft")
    await _new_package(db, sub_id, version=3, status="archived")
    await _new_package(db, sub_id, version=4, status="archived")

    # Kısıt sektör başınadır — başka alt sektör kendi `active`'ini alabilir.
    await _new_package(db, other_sub_id, version=1, status="active")

    # `status` kapalı kümedir.
    bad_status = await _rejected(
        db,
        """
        INSERT INTO social.sector_packages
            (sector_id, version, status, schema_version, content)
        VALUES ($1, 9, 'published', 1, $2)
        """,
        sub_id,
        CONTENT_JSON,
    )
    assert isinstance(bad_status, asyncpg.exceptions.CheckViolationError)


async def test_packages_version_unique(db):
    """`(sector_id, version)` benzersizdir; `run_id` NULL kalabilir (K-110 açık)."""
    root_id = await _new_root_sector(db)
    sub_id = await _new_sub_sector(db, root_id)

    package_id = await _new_package(db, sub_id, version=1, status="draft")

    error = await _rejected(
        db,
        """
        INSERT INTO social.sector_packages
            (sector_id, version, status, schema_version, content)
        VALUES ($1, 1, 'archived', 1, $2)
        """,
        sub_id,
        CONTENT_JSON,
    )
    assert isinstance(error, asyncpg.exceptions.UniqueViolationError)

    row = await db.fetchrow(
        """
        SELECT run_id, decision_log, activated_at, created_at
        FROM social.sector_packages WHERE id = $1
        """,
        package_id,
    )
    # K-110 AÇIK: `run_id` nullable KALIR — bu plan oraya karar yazmaz.
    assert row["run_id"] is None
    assert row["decision_log"] == "[]"
    assert row["activated_at"] is None
    assert row["created_at"] is not None

    # Bileşik damga FK'sının hedefi: UNIQUE (id, version).
    has_id_version_unique = await db.fetchval(
        """
        SELECT count(*) FROM pg_indexes
        WHERE schemaname = 'social'
          AND tablename = 'sector_packages'
          AND indexdef LIKE '%(id, version)%'
        """
    )
    assert has_id_version_unique == 1, "UNIQUE (id, version) yok — bileşik FK hedefsiz"


# --- 6-8. K-08b alt-sektör zorunluluğu ------------------------------------


async def test_sub_sector_id_rejects_root_sector(db):
    """`brands.sub_sector_id` yalnız `parent_sector_id IS NOT NULL` satırı kabul eder."""
    root_id = await _new_root_sector(db)
    brand_id = await _new_brand(db)

    insert_error = await _rejected(
        db,
        "INSERT INTO social.brands (name, sub_sector_id) VALUES ('Kok Marka', $1)",
        root_id,
    )
    assert "alt sektor" in str(insert_error).lower().replace("ö", "o").replace("ü", "u")

    update_error = await _rejected(
        db,
        "UPDATE social.brands SET sub_sector_id = $1 WHERE id = $2",
        root_id,
        brand_id,
    )
    assert "alt sektor" in str(update_error).lower().replace("ö", "o").replace("ü", "u")

    assert (
        await db.fetchval(
            "SELECT sub_sector_id FROM social.brands WHERE id = $1", brand_id
        )
        is None
    )


async def test_sub_sector_id_accepts_child_and_null(db):
    """Alt sektör satırı kabul edilir; NULL kalabilir — geri doldurma YOK."""
    root_id = await _new_root_sector(db)
    sub_id = await _new_sub_sector(db, root_id)

    assigned_brand = await _new_brand(db, sub_sector_id=sub_id)
    assert (
        await db.fetchval(
            "SELECT sub_sector_id FROM social.brands WHERE id = $1", assigned_brand
        )
        == sub_id
    )

    # NULL serbesttir ve atanmış satır NULL'a geri çekilebilir.
    unassigned_brand = await _new_brand(db)
    assert (
        await db.fetchval(
            "SELECT sub_sector_id FROM social.brands WHERE id = $1", unassigned_brand
        )
        is None
    )
    await db.execute(
        "UPDATE social.brands SET sub_sector_id = NULL WHERE id = $1", assigned_brand
    )

    # Kolon NULLABLE ve varsayılansız (geri doldurma yok).
    column = await db.fetchrow(
        """
        SELECT data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema = 'social' AND table_name = 'brands'
          AND column_name = 'sub_sector_id'
        """
    )
    assert column["data_type"] == "uuid"
    assert column["is_nullable"] == "YES"
    assert column["column_default"] is None

    # Mevcut markaların hiçbirine değer yazılmamıştır.
    backfilled = await db.fetchval(
        "SELECT count(*) FROM social.brands WHERE sub_sector_id IS NOT NULL AND id <> $1",
        assigned_brand,
    )
    assert backfilled == 0


async def test_package_sector_id_rejects_root(db):
    """`sector_packages.sector_id` de alt-sektör satırı zorunlu kılar (spec §3.3)."""
    root_id = await _new_root_sector(db)
    sub_id = await _new_sub_sector(db, root_id)

    error = await _rejected(
        db,
        """
        INSERT INTO social.sector_packages
            (sector_id, version, status, schema_version, content)
        VALUES ($1, 1, 'draft', 1, $2)
        """,
        root_id,
        CONTENT_JSON,
    )
    assert "alt sektor" in str(error).lower().replace("ö", "o").replace("ü", "u")

    package_id = await _new_package(db, sub_id, version=1, status="draft")
    move_error = await _rejected(
        db,
        "UPDATE social.sector_packages SET sector_id = $1 WHERE id = $2",
        root_id,
        package_id,
    )
    assert "alt sektor" in str(move_error).lower().replace("ö", "o").replace("ü", "u")


# --- 9-12. K-07 damga temsili (posts bileşik FK + MATCH FULL) -------------


async def test_stamp_both_null_accepted(db):
    """Paketsiz üretim: her iki damga kolonu da NULL kalabilir."""
    brand_id = await _new_brand(db)
    post_id = await db.fetchval(
        """
        INSERT INTO social.posts (brand_id, content_type, package_id, package_version)
        VALUES ($1, 'image', NULL, NULL)
        RETURNING id
        """,
        brand_id,
    )
    row = await db.fetchrow(
        "SELECT package_id, package_version FROM social.posts WHERE id = $1", post_id
    )
    assert row["package_id"] is None and row["package_version"] is None

    # Damga kolonları eklenirken mevcut satırlara değer yazılmaz.
    stamped_others = await db.fetchval(
        "SELECT count(*) FROM social.posts WHERE package_id IS NOT NULL"
    )
    assert stamped_others == 0


async def test_stamp_exact_pair_accepted(db):
    """Satırla eşleşen `(package_id, version)` çifti kabul edilir."""
    root_id = await _new_root_sector(db)
    sub_id = await _new_sub_sector(db, root_id)
    package_id = await _new_package(db, sub_id, version=7, status="active")
    brand_id = await _new_brand(db)

    post_id = await db.fetchval(
        """
        INSERT INTO social.posts (brand_id, content_type, package_id, package_version)
        VALUES ($1, 'image', $2, 7)
        RETURNING id
        """,
        brand_id,
        package_id,
    )
    row = await db.fetchrow(
        "SELECT package_id, package_version FROM social.posts WHERE id = $1", post_id
    )
    assert row["package_id"] == package_id
    assert row["package_version"] == 7


async def test_stamp_half_null_rejected(db):
    """MATCH FULL: yarım-NULL çift DB düzeyinde reddedilir (iki yönde de)."""
    root_id = await _new_root_sector(db)
    sub_id = await _new_sub_sector(db, root_id)
    package_id = await _new_package(db, sub_id, version=3, status="active")
    brand_id = await _new_brand(db)

    id_only = await _rejected(
        db,
        """
        INSERT INTO social.posts (brand_id, content_type, package_id, package_version)
        VALUES ($1, 'image', $2, NULL)
        """,
        brand_id,
        package_id,
    )
    assert isinstance(id_only, asyncpg.exceptions.ForeignKeyViolationError)

    version_only = await _rejected(
        db,
        """
        INSERT INTO social.posts (brand_id, content_type, package_id, package_version)
        VALUES ($1, 'image', NULL, 3)
        """,
        brand_id,
    )
    assert isinstance(version_only, asyncpg.exceptions.ForeignKeyViolationError)


async def test_stamp_mismatched_version_rejected(db):
    """Var olan pakete ait OLMAYAN sürüm numarası reddedilir."""
    root_id = await _new_root_sector(db)
    sub_id = await _new_sub_sector(db, root_id)
    package_id = await _new_package(db, sub_id, version=1, status="active")
    # Aynı sektörde ikinci sürüm — sürüm numarası ŞEMADA var ama BU satırda yok.
    await _new_package(db, sub_id, version=2, status="draft")
    brand_id = await _new_brand(db)

    error = await _rejected(
        db,
        """
        INSERT INTO social.posts (brand_id, content_type, package_id, package_version)
        VALUES ($1, 'image', $2, 2)
        """,
        brand_id,
        package_id,
    )
    assert isinstance(error, asyncpg.exceptions.ForeignKeyViolationError)

    unknown_package = await _rejected(
        db,
        """
        INSERT INTO social.posts (brand_id, content_type, package_id, package_version)
        VALUES ($1, 'image', $2, 1)
        """,
        brand_id,
        uuid.uuid4(),
    )
    assert isinstance(unknown_package, asyncpg.exceptions.ForeignKeyViolationError)


# --- 13. Reparenting yasağı (K-08b ayna ayağı) ----------------------------


async def test_parent_sector_id_update_rejected(db):
    """INSERT serbest; mevcut satırda `parent_sector_id` GÜNCELLEMESİ yasaktır."""
    root_a = await _new_root_sector(db)
    root_b = await _new_root_sector(db)
    sub_id = await _new_sub_sector(db, root_a)

    # (a) Alt satırı başka köke taşıma.
    reparent = await _rejected(
        db,
        "UPDATE social.sectors SET parent_sector_id = $1 WHERE id = $2",
        root_b,
        sub_id,
    )
    assert "parent_sector_id" in str(reparent)

    # (b) Alt satırı köke çevirme — invariantı sessizce çökerten yol.
    orphaning = await _rejected(
        db,
        "UPDATE social.sectors SET parent_sector_id = NULL WHERE id = $1",
        sub_id,
    )
    assert "parent_sector_id" in str(orphaning)

    # (c) Kök satıra sonradan ebeveyn verme.
    adopting = await _rejected(
        db,
        "UPDATE social.sectors SET parent_sector_id = $1 WHERE id = $2",
        root_a,
        root_b,
    )
    assert "parent_sector_id" in str(adopting)

    # Parent'a dokunmayan güncelleme SERBEST kalır (migration 021 gibi).
    await db.execute(
        "UPDATE social.sectors SET display_name = $1 WHERE id = $2", "Yeni Ad", sub_id
    )
    assert (
        await db.fetchval("SELECT parent_sector_id FROM social.sectors WHERE id = $1", sub_id)
        == root_a
    )


# --- 14-15. social.generation_stamps --------------------------------------


async def test_generation_stamps_schema_and_composite_fk(db):
    """Damga makbuzu tablosu: kolon sözleşmesi + bileşik FK + tek-kullanım işareti."""
    columns = {
        row["column_name"]: (row["data_type"], row["is_nullable"])
        for row in await db.fetch(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'social' AND table_name = 'generation_stamps'
            """
        )
    }
    assert columns == {
        "id": ("uuid", "NO"),
        "brand_id": ("uuid", "NO"),
        "package_id": ("uuid", "NO"),
        "package_version": ("integer", "NO"),
        "created_at": ("timestamp with time zone", "YES"),
        "consumed_at": ("timestamp with time zone", "YES"),
    }

    root_id = await _new_root_sector(db)
    sub_id = await _new_sub_sector(db, root_id)
    package_id = await _new_package(db, sub_id, version=5, status="active")
    brand_id = await _new_brand(db)

    stamp_id = await db.fetchval(
        """
        INSERT INTO social.generation_stamps (brand_id, package_id, package_version)
        VALUES ($1, $2, 5)
        RETURNING id
        """,
        brand_id,
        package_id,
    )
    row = await db.fetchrow(
        "SELECT created_at, consumed_at FROM social.generation_stamps WHERE id = $1",
        stamp_id,
    )
    assert row["created_at"] is not None
    assert row["consumed_at"] is None, "yeni makbuz tüketilmemiş olmalı"

    # Tek-kullanım işareti yazılabilir (tüketim davranışı Task 12).
    await db.execute(
        "UPDATE social.generation_stamps SET consumed_at = now() WHERE id = $1", stamp_id
    )
    assert (
        await db.fetchval(
            "SELECT consumed_at FROM social.generation_stamps WHERE id = $1", stamp_id
        )
        is not None
    )

    # Bileşik FK: satır-uyumsuz sürüm reddedilir.
    mismatched = await _rejected(
        db,
        """
        INSERT INTO social.generation_stamps (brand_id, package_id, package_version)
        VALUES ($1, $2, 6)
        """,
        brand_id,
        package_id,
    )
    assert isinstance(mismatched, asyncpg.exceptions.ForeignKeyViolationError)

    # İki kolon da NOT NULL — MATCH FULL'a gerek yok, yarım çift zaten imkânsız.
    half = await _rejected(
        db,
        """
        INSERT INTO social.generation_stamps (brand_id, package_id, package_version)
        VALUES ($1, $2, NULL)
        """,
        brand_id,
        package_id,
    )
    assert isinstance(half, asyncpg.exceptions.NotNullViolationError)


async def test_brand_delete_cascades_stamps_consumed_and_unconsumed(db):
    """F18: damgalı marka silinebilir kalır; workspace→brand zinciri de süpürür."""
    account_id = await _new_account(db)
    workspace_id = await _new_workspace(db, account_id)
    brand_id = await _new_brand(db, workspace_id=workspace_id)

    root_id = await _new_root_sector(db)
    sub_id = await _new_sub_sector(db, root_id)
    package_id = await _new_package(db, sub_id, version=1, status="active")

    unconsumed = await db.fetchval(
        """
        INSERT INTO social.generation_stamps (brand_id, package_id, package_version)
        VALUES ($1, $2, 1)
        RETURNING id
        """,
        brand_id,
        package_id,
    )
    consumed = await db.fetchval(
        """
        INSERT INTO social.generation_stamps
            (brand_id, package_id, package_version, consumed_at)
        VALUES ($1, $2, 1, now())
        RETURNING id
        """,
        brand_id,
        package_id,
    )

    # Doğrudan marka silme (mevcut `delete_brand` sözleşmesi) engellenmez.
    await db.execute("DELETE FROM social.brands WHERE id = $1", brand_id)
    remaining = await db.fetchval(
        "SELECT count(*) FROM social.generation_stamps WHERE id = ANY($1::uuid[])",
        [unconsumed, consumed],
    )
    assert remaining == 0, "tüketilmiş/tüketilmemiş makbuzlar markayla gitmedi"

    # Paket satırı ayakta kalır — makbuz ara-tablo verisidir, paket değil.
    assert (
        await db.fetchval(
            "SELECT count(*) FROM social.sector_packages WHERE id = $1", package_id
        )
        == 1
    )

    # workspace → brand → stamps zinciri de uçtan uca süpürür.
    second_brand = await _new_brand(db, workspace_id=workspace_id)
    chained = await db.fetchval(
        """
        INSERT INTO social.generation_stamps (brand_id, package_id, package_version)
        VALUES ($1, $2, 1)
        RETURNING id
        """,
        second_brand,
        package_id,
    )
    await db.execute("DELETE FROM social.workspaces WHERE id = $1", workspace_id)
    assert (
        await db.fetchval(
            "SELECT count(*) FROM social.generation_stamps WHERE id = $1", chained
        )
        == 0
    )


# --- Fail-closed garanti doğrulaması (F7) ----------------------------------
#
# `CREATE TABLE/INDEX IF NOT EXISTS` yalnız ADI arar, TANIMI doğrulamaz: aynı
# adda YANLIŞ tanımlı bir nesne önceden varsa DDL sessizce atlanır, migration
# NOTICE basıp başarıyla biter ve garanti kaybolur. Canlıya uygulama elle
# yapıldığı için bu senaryo gerçektir; migration sonundaki doğrulama bloğu
# bunu YAKALAMALI ve fail-closed durmalı.
#
# İzolasyon: her vaka `BEGIN … ROLLBACK` içinde koşar. psql tek oturumda önce
# bozmayı, sonra `\i 032`'yi uygular; sonuç ne olursa olsun transaction geri
# alınır (Postgres'te DDL transactional'dır). Diğer testlerin gördüğü şema
# değişmez — her vaka bunu ayrıca ölçer.

MIGRATION_032 = infra.MIGRATIONS_DIR / "032_sector_packages.sql"


def _psql_argv() -> tuple[list[str], dict[str, str]]:
    """Test DB'ye giden psql argv'si + parolayı taşıyan ortam.

    Kapı `conftest`in fail-closed guard'ıdır: yalnız 127.0.0.1:5433/otomaix_test.
    Bayrak kümesi (ON_ERROR_STOP dahil) tek yerde, `conftest.psql_argv`de yaşar.
    """
    return infra.psql_argv(infra._require_test_database(infra.test_database_url()))


def _reapply_032(setup_sql: str = "") -> subprocess.CompletedProcess:
    """`setup_sql` + migration 032'yi TEK transaction'da koşar, sonra ROLLBACK."""
    argv, env = _psql_argv()
    script = f"BEGIN;\n{setup_sql}\n\\i {MIGRATION_032}\nROLLBACK;\n"
    return subprocess.run(argv, input=script, env=env, capture_output=True, text=True)


def _scalar(sql: str) -> str:
    """Tek değerli sorgu — şemanın bozulmadan kaldığını ölçmek için."""
    argv, env = _psql_argv()
    result = subprocess.run(
        argv + ["--tuples-only", "--no-align", "-c", sql],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def _single_active_index_is_unique() -> str:
    return _scalar(
        """
        SELECT i.indisunique
        FROM pg_index i
        JOIN pg_class c ON c.oid = i.indexrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'social'
          AND c.relname = 'uq_sector_packages_single_active'
        """
    )


def test_reapply_on_correct_schema_succeeds(test_db_setup):
    """İdempotentlik: DOĞRU şema üstüne 032 yeniden uygulanınca rc=0 kalır."""
    result = _reapply_032()
    assert result.returncode == 0, (
        "doğru şema üstüne yeniden uygulama başarısız oldu "
        f"(rc={result.returncode}):\n{result.stderr}"
    )


def test_migration_raises_when_single_active_index_is_not_unique(test_db_setup):
    """Aynı ADDA benzersiz-OLMAYAN indeks varken migration durmalı.

    `CREATE UNIQUE INDEX IF NOT EXISTS` bu indeksi DEĞİŞTİRMEZ; doğrulama bloğu
    olmadan migration sessizce başarılı olur ve "sektör başına tek aktif paket"
    garantisi yok olur.
    """
    result = _reapply_032(
        """
        DROP INDEX social.uq_sector_packages_single_active;
        CREATE INDEX uq_sector_packages_single_active
            ON social.sector_packages (sector_id)
            WHERE status = 'active';
        """
    )

    assert result.returncode != 0, (
        "benzersiz-olmayan indeks sessizce kabul edildi — "
        f"stdout:\n{result.stdout}"
    )
    assert "uq_sector_packages_single_active" in result.stderr, result.stderr
    assert _single_active_index_is_unique() == "t", "ROLLBACK sonrası şema bozuk kaldı"


def test_migration_raises_when_sector_version_unique_is_missing(test_db_setup):
    """Önceden var olan `sector_packages` eksik UNIQUE ile kalırsa durmalı.

    `CREATE TABLE IF NOT EXISTS` gövdeyi doğrulamaz: kısıt geri gelmez.
    """
    result = _reapply_032(
        """
        ALTER TABLE social.sector_packages
            DROP CONSTRAINT sector_packages_sector_version_key;
        """
    )

    assert result.returncode != 0, (
        "eksik UNIQUE (sector_id, version) sessizce kabul edildi — "
        f"stdout:\n{result.stdout}"
    )
    assert "sector_packages_sector_version_key" in result.stderr, result.stderr
    assert (
        _scalar(
            """
            SELECT count(*) FROM pg_constraint
            WHERE conrelid = 'social.sector_packages'::regclass
              AND conname = 'sector_packages_sector_version_key'
            """
        )
        == "1"
    ), "ROLLBACK sonrası kısıt geri gelmedi"


def test_migration_raises_when_kind_check_is_missing(test_db_setup):
    """Önceden var olan `sector_research_artifacts` eksik CHECK ile kalırsa durmalı."""
    result = _reapply_032(
        """
        ALTER TABLE social.sector_research_artifacts
            DROP CONSTRAINT sector_research_artifacts_kind_check;
        """
    )

    assert result.returncode != 0, (
        f"eksik kind CHECK sessizce kabul edildi — stdout:\n{result.stdout}"
    )
    assert "kind" in result.stderr, result.stderr
    assert (
        _scalar(
            """
            SELECT count(*) FROM pg_constraint
            WHERE conrelid = 'social.sector_research_artifacts'::regclass
              AND contype = 'c'
            """
        )
        == "1"
    ), "ROLLBACK sonrası CHECK geri gelmedi"


# --- Uygulanma durumu: tanım DOĞRU ama garanti KAPALI (F7 tur 3) -----------
#
# Yukarıdaki vakalar nesnenin TANIMINI bozar. Bu iki vaka tanımı olduğu gibi
# bırakır, yalnız UYGULANMA durumunu kapatır: katalogda imza aynı görünür ama
# veritabanı artık hiçbir şeyi zorlamaz. Doğrulama bloğu bunu da yakalamalı.


def _single_active_index_is_valid() -> str:
    return _scalar(
        """
        SELECT i.indisvalid AND i.indisready AND i.indislive
        FROM pg_index i
        WHERE i.indexrelid = 'social.uq_sector_packages_single_active'::regclass
        """
    )


def _generation_stamps_fk_triggers_enabled() -> str:
    """`generation_stamps` üstündeki FK iç tetikleyicilerinden ETKİN olanlar."""
    return _scalar(
        """
        SELECT count(*)
        FROM pg_trigger t
        JOIN pg_constraint k ON k.oid = t.tgconstraint
        WHERE t.tgrelid = 'social.generation_stamps'::regclass
          AND k.contype = 'f'
          AND t.tgenabled = 'O'
        """
    )


def test_migration_raises_when_single_active_index_is_invalid(test_db_setup):
    """Geçersiz (yarım kalmış) indeks benzersizliği UYGULAMAZ — durmalı.

    `indisunique` true kalır, kolonlar ve predicate aynıdır; yalnız
    `indisvalid/indisready/indislive` düşer. Tanıma bakan bir doğrulama bunu
    göremez, ama "sektör başına tek aktif paket" garantisi fiilen yoktur.
    """
    result = _reapply_032(
        """
        UPDATE pg_index SET indisvalid = false
         WHERE indexrelid = 'social.uq_sector_packages_single_active'::regclass;
        """
    )

    assert result.returncode != 0, (
        "gecersiz (indisvalid=false) indeks sessizce kabul edildi — "
        f"stdout:\n{result.stdout}"
    )
    assert "uq_sector_packages_single_active" in result.stderr, result.stderr
    assert _single_active_index_is_valid() == "t", "ROLLBACK sonrası indeks bozuk kaldı"


def test_migration_raises_when_fk_triggers_disabled(test_db_setup):
    """`DISABLE TRIGGER ALL` FK'yı tanımı BOZMADAN kapatır — durmalı.

    `pg_get_constraintdef` aynı dizeyi döndürmeye devam eder; kısıtı fiilen
    uygulayan iç tetikleyiciler `tgenabled='D'` olur ve referans bütünlüğü
    sessizce ortadan kalkar.
    """
    result = _reapply_032(
        "ALTER TABLE social.generation_stamps DISABLE TRIGGER ALL;"
    )

    assert result.returncode != 0, (
        "devre disi FK tetikleyicileri sessizce kabul edildi — "
        f"stdout:\n{result.stdout}"
    )
    assert "generation_stamps_package_fkey" in result.stderr, result.stderr
    assert _generation_stamps_fk_triggers_enabled() == "4", (
        "ROLLBACK sonrası FK tetikleyicileri etkin durumuna dönmedi"
    )


# ─── Tablo/kolon imzası tuzakları (final review, 2026-08-25) ────────────────

FAILURE_MARKER_032 = "migration 032 garanti dogrulamasi BASARISIZ"


def _artifacts_decoy(
    *,
    content_type: str = "TEXT",
    id_extra: str = "PRIMARY KEY DEFAULT gen_random_uuid()",
    persistence: str = "",
    suffix: str = "",
) -> str:
    """Aynı ADDA, CHECK'i ve indeksi DOĞRU ama imzası bozuk sahte tablo.

    `sector_research_artifacts` seçildi çünkü ona gelen yabancı anahtar YOKTUR;
    tuzak kurulumu başka tabloları düşürmeden yapılabilir.
    """
    return f"""
        DROP TABLE IF EXISTS social.sector_research_artifacts CASCADE;
        CREATE {persistence} TABLE social.sector_research_artifacts (
            id UUID {id_extra},
            run_id TEXT NOT NULL,
            sector_slug TEXT NOT NULL,
            kind TEXT NOT NULL CHECK (kind IN ('research', 'review', 'synthesis')),
            source TEXT NOT NULL,
            brief_ref TEXT,
            content_md {content_type} NOT NULL,
            created_at TIMESTAMPTZ DEFAULT now()
        );
        CREATE INDEX idx_sector_research_artifacts_slug_run
            ON social.sector_research_artifacts (sector_slug, run_id);
        {suffix}
    """


def test_artifacts_wrong_content_type_is_caught():
    """`content_md` TEXT değilse migration DURur — kolon imzası kapısı.

    Ham kanıt katmanı Plan 2'nin YAZDIĞI yüzeydir; yanlış tipli bir kolon
    ya yazımı düşürür ya sessizce dönüştürür.
    """
    result = _reapply_032(_artifacts_decoy(content_type="JSONB"))
    assert result.returncode != 0, f"yanlış tipli content_md geçti:\n{result.stdout}"
    assert FAILURE_MARKER_032 in result.stderr, result.stderr
    assert "sector_research_artifacts kolon imzası" in result.stderr


def test_artifacts_missing_primary_key_is_caught():
    """`id` birincil anahtar değilse migration DURur."""
    result = _reapply_032(_artifacts_decoy(id_extra="DEFAULT gen_random_uuid()"))
    assert result.returncode != 0, f"PK'sız tablo geçti:\n{result.stdout}"
    assert FAILURE_MARKER_032 in result.stderr, result.stderr
    assert "sector_research_artifacts PRIMARY KEY" in result.stderr


@pytest.mark.parametrize(
    "persistence, suffix, label",
    [
        ("UNLOGGED", "", "UNLOGGED tablo"),
        (
            "",
            "ALTER TABLE social.sector_research_artifacts "
            "ENABLE ROW LEVEL SECURITY;",
            "satır güvenliği açık tablo",
        ),
    ],
)
def test_artifacts_table_property_corruption_is_caught(persistence, suffix, label):
    """Salt-ekleme kanıt katmanının dayanıklılığı da sözleşmenin parçası.

    `UNLOGGED` bir kanıt tablosu temiz olmayan kapanışta TRUNCATE edilir — yani
    "ham kanıt asla silinmez" vaadi (salt-ekleme tetikleyicisi) ayakta kalırken
    verinin kendisi yok olur. İkisi de kolon imzasını, CHECK'i ve indeksi
    BİREBİR aynı üretir; imza doğrulaması onları göremezdi.
    """
    result = _reapply_032(_artifacts_decoy(persistence=persistence, suffix=suffix))
    assert result.returncode != 0, f"{label} sessizce geçti:\n{result.stdout}"
    assert FAILURE_MARKER_032 in result.stderr, result.stderr
    assert "sector_research_artifacts tablo imzası" in result.stderr
