"""Task 5 — veri/API regresyon kümesi + marka kök-sektör tam sweep.

Spec §5.3'ün bağlayıcı iddiası: alt sektör satırlarının varlığı BUGÜNKÜ veri ve
API yüzeylerini değiştirmez. Ölçüt alan-bazlı eşitliktir (byte değil): aynı
alanlar, aynı değerler, aynı sıra.

Dört yüzey ayrı ayrı sınanır:

1. `GET /sectors` — alt satır eklendikten sonra kök liste ALAN-BAZLI aynı.
2. Marka → kök sektör eşlemesi — TAM sweep (spot yasak: veritabanındaki HER
   marka karşılaştırılır, örneklem değil).
3. Paketsiz üretim kaydı — hiçbir üretim yolu damga kolonlarına yazmaz
   (yapısal sweep: `INSERT INTO social.posts` çağıran her yer taranır).
4. `scripts/sector_sweep.py` — canlıda da koşulabilen salt-okunur, deterministik
   operasyonel sweep. Salt-okunurluk SALT-OKUNUR ROL ile kanıtlanır; rolün
   gerçekten yazamadığı ayrıca pozitif kontrol edilir (aksi hâlde kanıt boştur).
"""

from __future__ import annotations

import re
import subprocess
import sys
import uuid
from pathlib import Path

import asyncpg
import pytest

from app.routers import sectors as sectors_router

from .conftest import (
    REQUIRED_HOST,
    REQUIRED_PORT,
    _require_disposable_database,
    psql_argv,
)

BACKEND_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = BACKEND_ROOT / "app"
SWEEP_SCRIPT = BACKEND_ROOT / "scripts" / "sector_sweep.py"

# Salt-okunurluk kanıtı için açılan rol. Rol küme-genelidir; fixture sonunda
# düşürülür.
READONLY_ROLE = "otomaix_test_readonly"
READONLY_PASSWORD = "sweep-readonly-fixture"

SUB_SLUG = "kuafor-salonu"


@pytest.fixture(autouse=True)
def no_cache(monkeypatch):
    """Sektör önbelleğini kapat — testler DB sorgusunu ölçer, Redis'i değil."""

    async def _miss(_key):
        return None

    async def _noop(_key, _value, _ttl):
        return None

    monkeypatch.setattr(sectors_router, "get_cached", _miss)
    monkeypatch.setattr(sectors_router, "set_cached", _noop)


async def _root_id(db, slug: str = "hizmet") -> uuid.UUID:
    return await db.fetchval("SELECT id FROM social.sectors WHERE slug = $1", slug)


async def _new_sub_sector(db, slug: str = SUB_SLUG) -> uuid.UUID:
    return await db.fetchval(
        """
        INSERT INTO social.sectors (slug, display_name, parent_sector_id)
        VALUES ($1, $2, $3)
        RETURNING id
        """,
        slug,
        "Kuaför Salonu",
        await _root_id(db),
    )


async def _brand_sector_map(db) -> list[tuple[str, str | None]]:
    """TAM sweep: veritabanındaki HER markanın (id, sector_id) eşlemesi."""
    rows = await db.fetch(
        """
        SELECT id::text AS brand_id, sector_id::text AS sector_id
        FROM social.brands
        ORDER BY id
        """
    )
    return [(row["brand_id"], row["sector_id"]) for row in rows]


async def _seed_brands(db, count: int = 3) -> list[uuid.UUID]:
    """Kök sektörlere bağlı markalar açar (test transaction'ında)."""
    roots = await db.fetch(
        """
        SELECT id FROM social.sectors
        WHERE parent_sector_id IS NULL
        ORDER BY slug
        LIMIT $1
        """,
        count,
    )
    assert len(roots) == count, "kök seed beklenenden az sektör içeriyor"

    brand_ids = []
    for index, root in enumerate(roots):
        brand_ids.append(
            await db.fetchval(
                """
                INSERT INTO social.brands (name, sector_id)
                VALUES ($1, $2)
                RETURNING id
                """,
                f"Regresyon Markası {index}",
                root["id"],
            )
        )
    return brand_ids


async def test_sectors_list_unchanged_after_sub_sector_insert(db):
    """Alt satır eklemek `GET /sectors` çıktısını ALAN-BAZLI değiştirmez."""
    before = (await sectors_router.list_sectors(db=db)).data

    sub_id = await _new_sub_sector(db)

    after = (await sectors_router.list_sectors(db=db)).data

    assert before == after, "alt sektör eklemek kök listeyi değiştirdi"
    assert str(sub_id) not in {row["id"] for row in after}
    # Liste boş olsaydı eşitlik boşuna sağlanırdı — karşılaştırma gerçek veri üstünde.
    assert len(after) > 1

    # Duyarlılık kontrolü: karşılaştırma KÖK satır değişikliğini görüyor mu?
    # Görmüyorsa yukarıdaki eşitlik iddiası boştur.
    await db.execute(
        """
        INSERT INTO social.sectors (slug, display_name, parent_sector_id)
        VALUES ('regresyon-kok', 'Regresyon Kök', NULL)
        """
    )
    sensitive = (await sectors_router.list_sectors(db=db)).data
    assert sensitive != before, "karşılaştırma kök değişikliğine duyarsız"


async def test_brand_sector_mappings_full_sweep_unchanged(db):
    """TAM sweep: alt satır eklemek HİÇBİR markanın kök sektörünü oynatmaz."""
    await _seed_brands(db)

    before = await _brand_sector_map(db)
    assert before, "sweep boş küme üstünde koştu — karşılaştırma anlamsız"

    await _new_sub_sector(db)

    after = await _brand_sector_map(db)

    assert before == after, "alt sektör eklemek marka eşlemelerini değiştirdi"
    # Örneklem değil, tam küme karşılaştırıldı.
    assert len(after) == await db.fetchval("SELECT count(*) FROM social.brands")

    # Duyarlılık kontrolü: sweep tek bir markanın kayışını yakalıyor mu?
    # Yakalamıyorsa "değişmedi" iddiası boştur.
    await db.execute(
        """
        UPDATE social.brands SET sector_id = (
            SELECT id FROM social.sectors
            WHERE parent_sector_id IS NULL AND id <> sector_id
            ORDER BY slug LIMIT 1
        )
        WHERE id = $1
        """,
        uuid.UUID(before[0][0]),
    )
    assert await _brand_sector_map(db) != before, "sweep marka kayışına duyarsız"


def _post_insert_statements() -> list[tuple[Path, str]]:
    """`app/` içindeki her `INSERT INTO social.posts` ifadesini toplar."""
    statements: list[tuple[Path, str]] = []
    for path in sorted(APP_DIR.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"INSERT\s+INTO\s+social\.posts", text):
            end = text.find('"""', match.end())
            statements.append((path, text[match.start() : end if end != -1 else None]))
    return statements


async def test_unpackaged_post_has_no_package_stamp(db):
    """Paketsiz üretim kaydında damga kolonları NULL kalır.

    İki ayak: (a) yapısal — bugün hiçbir üretim yolu damga kolonlarına YAZMIYOR
    (Task 12 damgayı eklediğinde bu test bilinçli olarak güncellenecek);
    (b) davranışsal — üretim yolunun kolon kümesiyle yazılan kayıt damgasız
    kalır ve damgasız olarak sorgulanabilir.
    """
    statements = _post_insert_statements()
    assert statements, "üretim yolu bulunamadı — yapısal sweep boşa koştu"

    for path, statement in statements:
        assert "package_id" not in statement, f"{path} damga yazıyor (package_id)"
        assert "package_version" not in statement, (
            f"{path} damga yazıyor (package_version)"
        )

    brand_id = (await _seed_brands(db, count=1))[0]
    row = await db.fetchrow(
        """
        INSERT INTO social.posts
            (brand_id, content_type, content_category, prompt, status)
        VALUES ($1, 'image', 'genel', 'test', 'generating')
        RETURNING id, package_id, package_version
        """,
        brand_id,
    )

    assert row["package_id"] is None
    assert row["package_version"] is None
    assert await db.fetchval(
        """
        SELECT count(*) FROM social.posts
        WHERE id = $1 AND package_id IS NULL AND package_version IS NULL
        """,
        row["id"],
    ) == 1


def _psql(url: str, sql: str) -> None:
    argv, env = psql_argv(url)
    result = subprocess.run(
        argv + ["-c", sql], env=env, capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"psql başarısız: {result.stderr.strip()}")


def _readonly_dsn(url: str, database: str) -> str:
    return (
        f"postgresql://{READONLY_ROLE}:{READONLY_PASSWORD}"
        f"@{REQUIRED_HOST}:{REQUIRED_PORT}/{database}"
    )


@pytest.fixture
def readonly_role(scratch_db_migrated: str):
    """Yalnız SELECT yetkisi olan, süper-kullanıcı OLMAYAN rol açar.

    Süper-kullanıcı yetki denetimini atlar; salt-okunurluk ancak ayrı bir rolle
    kanıtlanabilir. Rol küme-geneli olduğu için fixture sonunda düşürülür.
    """
    url = _require_disposable_database(scratch_db_migrated)
    database = url.rsplit("/", 1)[-1]

    _psql(url, f"DROP ROLE IF EXISTS {READONLY_ROLE}")
    _psql(
        url,
        f"CREATE ROLE {READONLY_ROLE} LOGIN NOSUPERUSER "
        f"PASSWORD '{READONLY_PASSWORD}'",
    )
    _psql(url, f"ALTER ROLE {READONLY_ROLE} SET default_transaction_read_only = on")
    _psql(url, f'GRANT CONNECT ON DATABASE "{database}" TO {READONLY_ROLE}')
    _psql(url, f"GRANT USAGE ON SCHEMA social TO {READONLY_ROLE}")
    _psql(url, f"GRANT SELECT ON ALL TABLES IN SCHEMA social TO {READONLY_ROLE}")
    try:
        yield url, _readonly_dsn(url, database)
    finally:
        _psql(url, f"REVOKE ALL ON ALL TABLES IN SCHEMA social FROM {READONLY_ROLE}")
        _psql(url, f"REVOKE ALL ON SCHEMA social FROM {READONLY_ROLE}")
        _psql(url, f'REVOKE ALL ON DATABASE "{database}" FROM {READONLY_ROLE}')
        _psql(url, f"DROP ROLE IF EXISTS {READONLY_ROLE}")


def _run_sweep(dsn: str) -> subprocess.CompletedProcess:
    """Script'i ÇIPLAK ortamda koşar — bağlantı dizesi ortamdan miras ALINMAZ."""
    return subprocess.run(
        [sys.executable, str(SWEEP_SCRIPT), "--database-url", dsn, "--dry-run"],
        cwd=str(BACKEND_ROOT),
        env={"PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
    )


async def test_sector_sweep_readonly_and_deterministic(readonly_role):
    """Sweep salt-okunur rolle koşar, aynı durumda BAYT-AYNI rapor üretir."""
    admin_url, readonly_dsn = readonly_role

    # Pozitif kontrol: rol gerçekten yazamıyor. Yazabilseydi salt-okunurluk
    # kanıtı boş olurdu.
    writer = await asyncpg.connect(readonly_dsn)
    try:
        with pytest.raises(asyncpg.PostgresError):
            await writer.execute(
                "INSERT INTO social.brands (name) VALUES ('yazma denemesi')"
            )
    finally:
        await writer.close()

    # Kök sektöre bağlı iki marka (COMMIT edilmiş — script ayrı bağlantıdan okur).
    seeder = await asyncpg.connect(admin_url)
    try:
        root_id = await seeder.fetchval(
            "SELECT id FROM social.sectors WHERE parent_sector_id IS NULL ORDER BY slug LIMIT 1"
        )
        for index in range(2):
            await seeder.execute(
                "INSERT INTO social.brands (name, sector_id) VALUES ($1, $2)",
                f"Sweep Markası {index}",
                root_id,
            )
    finally:
        await seeder.close()

    first = _run_sweep(readonly_dsn)
    second = _run_sweep(readonly_dsn)

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    assert first.stdout == second.stdout, "rapor deterministik değil"
    assert "brands_total: 2" in first.stdout
    assert "differences: 0" in first.stdout

    # Alt sektöre kayan bir marka farkı GÖRÜNÜR kılar — fark=0 iddiası boş değil.
    drifter = await asyncpg.connect(admin_url)
    try:
        sub_id = await drifter.fetchval(
            """
            INSERT INTO social.sectors (slug, display_name, parent_sector_id)
            VALUES ($1, $2, (SELECT id FROM social.sectors
                             WHERE parent_sector_id IS NULL ORDER BY slug LIMIT 1))
            RETURNING id
            """,
            SUB_SLUG,
            "Kuaför Salonu",
        )
        await drifter.execute(
            "UPDATE social.brands SET sector_id = $1 WHERE name = $2",
            sub_id,
            "Sweep Markası 0",
        )
    finally:
        await drifter.close()

    drifted = _run_sweep(readonly_dsn)

    assert drifted.returncode != 0, "kök-dışı marka fark olarak raporlanmadı"
    assert "differences: 1" in drifted.stdout
    assert "sub_sector" in drifted.stdout
