"""Pytest altyapısı — atılabilir `otomaix_test` veritabanı üstünde koşar.

Bağlayıcı invariantlar (plan Task 1):

1. Migration uygulayıcı dosya listesini GLOB ile alır — hardcoded liste DEĞİL
   (`shared/local-deployment/migrations/run-migrations.sh` bayat-liste hatası
   burada tekrarlanmaz).
2. Bağlantı dizesi KODA GÖMÜLMEZ: uygulamanın kendi ayarından
   (`app.core.config.settings.DATABASE_URL` → `.env`) türetilir ve veritabanı
   adı `otomaix_test` ile değiştirilir. Canlı `otomaix` veritabanına bağlanmaya
   çalışan altyapı `_require_test_database` guard'ıyla REDDEDİLİR.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import asyncpg
import pytest

# Atılabilir test veritabanı. Canlı `otomaix` bu dosyada asla hedeflenmez.
TEST_DB_NAME = "otomaix_test"

# Yönetim (CREATE/DROP DATABASE) bağlantısının koştuğu bakım veritabanı.
MAINTENANCE_DB_NAME = "postgres"

# tests/ -> backend/ -> social/ -> apps/ -> <repo kökü>
REPO_ROOT = Path(__file__).resolve().parents[4]
MIGRATIONS_DIR = REPO_ROOT / "shared" / "db" / "migrations"

# Migration dosyaları numaralı önek taşır: `NNN_ad.sql`.
_MIGRATION_PREFIX = re.compile(r"^(\d+)_")


def _migration_files() -> list[Path]:
    """Migration dosyalarını GLOB ile toplar, numara sırasına dizer.

    Elle tutulan liste yok: dizine eklenen her `NNN_*.sql` otomatik koşar.
    """
    files: list[tuple[int, str, Path]] = []
    for path in MIGRATIONS_DIR.glob("*.sql"):
        match = _MIGRATION_PREFIX.match(path.name)
        if match is None:
            raise RuntimeError(
                f"Numarasız migration dosyası: {path.name} — sıralama garanti edilemez."
            )
        files.append((int(match.group(1)), path.name, path))

    if not files:
        raise RuntimeError(f"Migration bulunamadı: {MIGRATIONS_DIR}")

    files.sort(key=lambda item: (item[0], item[1]))
    return [item[2] for item in files]


def _require_test_database(url: str) -> str:
    """Guard: test altyapısı YALNIZ `otomaix_test`e bağlanabilir."""
    database = urlsplit(url).path.lstrip("/")
    if database != TEST_DB_NAME:
        raise RuntimeError(
            f"Test altyapısı {database!r} veritabanını hedefliyor; "
            f"yalnız {TEST_DB_NAME!r} kabul edilir."
        )
    return url


def _with_database(url: str, database: str) -> str:
    return urlunsplit(urlsplit(url)._replace(path=f"/{database}"))


def test_database_url() -> str:
    """Uygulamanın kendi ayarından test veritabanı bağlantı dizesini türetir."""
    from app.core.config import settings

    configured = settings.DATABASE_URL
    if not configured:
        raise RuntimeError(
            "DATABASE_URL boş — testler için apps/social/backend/.env gerekli."
        )
    return _require_test_database(_with_database(configured, TEST_DB_NAME))


def _run_psql(url: str, *, sql: str | None = None, file: Path | None = None) -> None:
    """psql'i çalıştırır. Parola argv'ye değil PGPASSWORD ortam değişkenine gider."""
    parts = urlsplit(url)
    argv = [
        "psql",
        "--no-psqlrc",
        "--quiet",
        "-v",
        "ON_ERROR_STOP=1",
        "-h",
        parts.hostname or "127.0.0.1",
        "-p",
        str(parts.port or 5432),
        "-U",
        parts.username or "",
        "-d",
        parts.path.lstrip("/"),
    ]
    argv += ["-c", sql] if sql is not None else ["-f", str(file)]

    env = dict(os.environ)
    if parts.password:
        env["PGPASSWORD"] = parts.password

    result = subprocess.run(argv, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        label = sql if sql is not None else str(file)
        raise RuntimeError(f"psql başarısız ({label}):\n{result.stderr.strip()}")


@pytest.fixture(scope="session")
def test_db_setup() -> str:
    """`otomaix_test`i sıfırdan yaratır ve tüm migration'ları uygular.

    Her oturumda veritabanı DROP + CREATE edilir; migration'ların idempotent
    olduğu varsayılmaz, durum deterministiktir. Canlı `otomaix` veritabanına
    dokunulmaz.
    """
    url = test_database_url()
    admin_url = _with_database(url, MAINTENANCE_DB_NAME)

    _run_psql(admin_url, sql=f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}" WITH (FORCE)')
    _run_psql(admin_url, sql=f'CREATE DATABASE "{TEST_DB_NAME}"')

    _run_psql(url, sql="CREATE SCHEMA IF NOT EXISTS social")
    _run_psql(url, sql="CREATE EXTENSION IF NOT EXISTS vector")

    for migration in _migration_files():
        _run_psql(url, file=migration)

    return url


@pytest.fixture
async def db(test_db_setup: str):
    """Function-scope asyncpg bağlantısı; her test kendi transaction'ında koşar.

    Transaction test sonunda GERİ ALINIR — testler birbirinin verisini görmez.
    """
    connection = await asyncpg.connect(_require_test_database(test_db_setup))
    transaction = connection.transaction()
    await transaction.start()
    try:
        yield connection
    finally:
        await transaction.rollback()
        await connection.close()
