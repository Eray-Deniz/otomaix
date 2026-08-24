"""Pytest altyapısı — atılabilir `otomaix_test` veritabanı üstünde koşar.

Bağlayıcı invariantlar (plan Task 1):

1. Migration uygulayıcı dosya listesini GLOB ile alır — hardcoded liste DEĞİL
   (`shared/local-deployment/migrations/run-migrations.sh` bayat-liste hatası
   burada tekrarlanmaz).
2. Bağlantı dizesi KODA GÖMÜLMEZ: uygulamanın kendi ayarından
   (`app.core.config.settings.DATABASE_URL` → `.env`) türetilir ve veritabanı
   adı `otomaix_test` ile değiştirilir.
3. Yıkıcı işlem (DROP/CREATE DATABASE, migration uygulaması) YALNIZ
   `127.0.0.1:5433/otomaix_test` üçlüsüne izinlidir. Kapı FAIL-CLOSED'dır:
   host/port/veritabanı üçlüsü birebir eşleşmiyorsa — takma ad (`localhost`,
   `::1`, `0.0.0.0`), eksik port, eksik host veya canlı `otomaix` adı — işlem
   BAŞLAMADAN reddedilir. Varsayılana düşme YOKTUR.
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

# Yıkıcı işlemlere izinli TEK uç nokta (plan "Global Constraints" bölümü).
# Takma ad kabul edilmez: `localhost` / `::1` / `0.0.0.0` de REDDEDİLİR.
REQUIRED_HOST = "127.0.0.1"
REQUIRED_PORT = 5433

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


def _endpoint(url: str) -> tuple[str | None, int | None, str]:
    """URL'i (host, port, veritabanı) üçlüsüne ayırır — varsayılan UYDURMAZ."""
    parts = urlsplit(url)
    try:
        port = parts.port
    except ValueError:
        # Bozuk port ("abc", "-1", aralık dışı): belirsiz → fail-closed.
        port = None
    return parts.hostname, port, parts.path.lstrip("/")


def _require_endpoint(url: str, *, database: str) -> str:
    """Fail-closed kapı: host/port/veritabanı üçlüsü birebir eşleşmeli.

    Parola hata mesajına ASLA girmez — yalnız host/port/veritabanı basılır.
    """
    seen_host, seen_port, seen_database = _endpoint(url)

    problems: list[str] = []
    if seen_host != REQUIRED_HOST:
        problems.append(f"host={seen_host!r} (beklenen {REQUIRED_HOST!r})")
    if seen_port != REQUIRED_PORT:
        problems.append(f"port={seen_port!r} (beklenen {REQUIRED_PORT!r})")
    if seen_database != database:
        problems.append(f"veritabanı={seen_database!r} (beklenen {database!r})")

    if problems:
        raise RuntimeError(
            "Yıkıcı test altyapısı reddedildi — yalnız "
            f"{REQUIRED_HOST}:{REQUIRED_PORT}/{database} kabul edilir. "
            "Uyuşmayan: " + ", ".join(problems)
        )
    return url


def _require_test_database(url: str) -> str:
    """Guard: test altyapısı YALNIZ `127.0.0.1:5433/otomaix_test`e bağlanabilir."""
    return _require_endpoint(url, database=TEST_DB_NAME)


def _require_admin_database(url: str) -> str:
    """Guard: yönetim bağlantısı YALNIZ aynı yerel uç noktanın bakım DB'sine gider."""
    return _require_endpoint(url, database=MAINTENANCE_DB_NAME)


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
    # Kapı psql SÜRECİ BAŞLAMADAN koşar: yıkıcı komut asla uzak sunucuya gitmez.
    # Bakım DB'si de aynı yerel uç noktaya kilitlidir (DROP/CREATE oradan koşar).
    database = urlsplit(url).path.lstrip("/")
    if database == MAINTENANCE_DB_NAME:
        _require_admin_database(url)
    else:
        _require_test_database(url)

    parts = urlsplit(url)
    argv = [
        "psql",
        "--no-psqlrc",
        "--quiet",
        "-v",
        "ON_ERROR_STOP=1",
        "-h",
        REQUIRED_HOST,
        "-p",
        str(REQUIRED_PORT),
        "-U",
        parts.username or "",
        "-d",
        database,
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
    admin_url = _require_admin_database(_with_database(url, MAINTENANCE_DB_NAME))

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
