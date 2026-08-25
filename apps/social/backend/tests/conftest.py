"""Pytest altyapısı — atılabilir `otomaix_test` veritabanı üstünde koşar.

Bağlayıcı invariantlar (plan Task 1):

1. Migration uygulayıcı dosya listesini GLOB ile alır — hardcoded liste DEĞİL
   (`shared/local-deployment/migrations/run-migrations.sh` bayat-liste hatası
   burada tekrarlanmaz).
2. Bağlantı dizesi KODA GÖMÜLMEZ: uygulamanın kendi ayarından
   (`app.core.config.settings.DATABASE_URL` → `.env`) türetilir ve veritabanı
   adı `otomaix_test` ile değiştirilir.
3. Yıkıcı işlem (DROP/CREATE DATABASE, migration uygulaması) YALNIZ
   `127.0.0.1:5433` uç noktasındaki KAPALI KÜME veritabanlarına izinlidir:
   oturum veritabanı `otomaix_test` ve şema-yıkıcı testlerin taze kopyası
   `otomaix_test_scratch` (`DISPOSABLE_DB_NAMES`). Kapı FAIL-CLOSED'dır:
   host/port eşleşmiyorsa veya ad bu kümede değilse — takma ad (`localhost`,
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

# Şema-yıkıcı testlerin (migration geri alma, runner koşumu) kullandığı ikinci
# atılabilir veritabanı. `otomaix_test` oturum boyunca ayakta kalmalıdır; bu ad
# her testte sıfırdan yaratılıp düşürülür.
SCRATCH_DB_NAME = "otomaix_test_scratch"

# Yıkıcı işlemlere izinli veritabanı adları — kapalı küme, fail-closed.
DISPOSABLE_DB_NAMES = frozenset({TEST_DB_NAME, SCRATCH_DB_NAME})

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


def _require_endpoint(url: str, *, databases: frozenset[str]) -> str:
    """Fail-closed kapı: host/port eşleşmeli, veritabanı kapalı kümede olmalı.

    Parola hata mesajına ASLA girmez — yalnız host/port/veritabanı basılır.
    """
    seen_host, seen_port, seen_database = _endpoint(url)
    allowed = ", ".join(sorted(databases))

    problems: list[str] = []
    if seen_host != REQUIRED_HOST:
        problems.append(f"host={seen_host!r} (beklenen {REQUIRED_HOST!r})")
    if seen_port != REQUIRED_PORT:
        problems.append(f"port={seen_port!r} (beklenen {REQUIRED_PORT!r})")
    if seen_database not in databases:
        problems.append(f"veritabanı={seen_database!r} (beklenen {allowed})")

    if problems:
        raise RuntimeError(
            "Yıkıcı test altyapısı reddedildi — yalnız "
            f"{REQUIRED_HOST}:{REQUIRED_PORT}/[{allowed}] kabul edilir. "
            "Uyuşmayan: " + ", ".join(problems)
        )
    return url


def _require_test_database(url: str) -> str:
    """Guard: oturum veritabanı YALNIZ `127.0.0.1:5433/otomaix_test` olabilir."""
    return _require_endpoint(url, databases=frozenset({TEST_DB_NAME}))


def _require_disposable_database(url: str) -> str:
    """Guard: yıkıcı işlem YALNIZ atılabilir iki addan birine gidebilir."""
    return _require_endpoint(url, databases=DISPOSABLE_DB_NAMES)


def _require_admin_database(url: str) -> str:
    """Guard: yönetim bağlantısı YALNIZ aynı yerel uç noktanın bakım DB'sine gider."""
    return _require_endpoint(url, databases=frozenset({MAINTENANCE_DB_NAME}))


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


def psql_argv(url: str) -> tuple[list[str], dict[str, str]]:
    """Guard'dan geçmiş psql argv'si + parolayı taşıyan ortam.

    Kapı psql SÜRECİ BAŞLAMADAN koşar: yıkıcı komut asla uzak sunucuya gitmez.
    Bakım DB'si de aynı yerel uç noktaya kilitlidir (DROP/CREATE oradan koşar).
    Parola argv'ye DEĞİL PGPASSWORD ortam değişkenine gider.
    """
    parts = urlsplit(url)
    database = parts.path.lstrip("/")
    if database == MAINTENANCE_DB_NAME:
        _require_admin_database(url)
    else:
        _require_disposable_database(url)

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

    env = dict(os.environ)
    if parts.password:
        env["PGPASSWORD"] = parts.password
    return argv, env


# Dış transaction'a SARILMAYAN migration'lar — iki gerekçe, ikisi de dosyanın
# kendi içeriğinden gelir:
#   * `CREATE INDEX CONCURRENTLY` içerenler transaction bloğunda KOŞAMAZ (011).
#   * Kendi `BEGIN/COMMIT`ini taşıyanlar zaten atomiktir; sarmak garantiyi
#     ZAYIFLATIR — içteki COMMIT dıştakini erken kapatır (017, ölçüldü).
# Liste dağıtım runner'ındaki (`run-migrations.sh`) `SELF_MANAGED_TX` ile AYNI
# olmalıdır: tek gerçek, iki okuyucu. Uyum
# `test_migration_032_rollback.py::test_single_transaction_exemption_is_exact`
# ile iki yönlü ölçülür.
NON_TRANSACTIONAL_MIGRATIONS = frozenset(
    {"011_performance_indexes.sql", "017_trend_cache_unique.sql"}
)


def _run_psql(
    url: str,
    *,
    sql: str | None = None,
    file: Path | None = None,
    single_transaction: bool = False,
) -> None:
    """psql'i çalıştırır; sıfır-dışı çıkışta istisna fırlatır.

    `single_transaction`, dağıtım runner'ının migration uygularken kullandığı
    anlambilimin AYNISIDIR: dosya tek transaction'da koşar, doğrulama bloğu
    reddederse daha önce uyguladığı DDL de geri alınır. Testlerin üretimden
    FARKLI bir anlambilimle koşması, üretimde var olmayan bir garantiyi
    varmış gibi gösterirdi.
    """
    argv, env = psql_argv(url)
    if single_transaction:
        argv += ["--single-transaction"]
    argv += ["-c", sql] if sql is not None else ["-f", str(file)]

    result = subprocess.run(argv, env=env, capture_output=True, text=True)
    if result.returncode != 0:
        label = sql if sql is not None else str(file)
        raise RuntimeError(f"psql başarısız ({label}):\n{result.stderr.strip()}")


def _apply_migrations(url: str) -> None:
    """`social` şeması + pgvector + tüm numaralı migration'lar (sırayla)."""
    _run_psql(url, sql="CREATE SCHEMA IF NOT EXISTS social")
    _run_psql(url, sql="CREATE EXTENSION IF NOT EXISTS vector")
    for migration in _migration_files():
        _run_psql(
            url,
            file=migration,
            single_transaction=migration.name not in NON_TRANSACTIONAL_MIGRATIONS,
        )


def _recreate_database(url: str) -> None:
    """Hedef veritabanını DROP + CREATE eder (guard: yalnız atılabilir adlar)."""
    database = urlsplit(_require_disposable_database(url)).path.lstrip("/")
    admin_url = _require_admin_database(_with_database(url, MAINTENANCE_DB_NAME))
    _run_psql(admin_url, sql=f'DROP DATABASE IF EXISTS "{database}" WITH (FORCE)')
    _run_psql(admin_url, sql=f'CREATE DATABASE "{database}"')


def _drop_database(url: str) -> None:
    database = urlsplit(_require_disposable_database(url)).path.lstrip("/")
    admin_url = _require_admin_database(_with_database(url, MAINTENANCE_DB_NAME))
    _run_psql(admin_url, sql=f'DROP DATABASE IF EXISTS "{database}" WITH (FORCE)')


@pytest.fixture(scope="session")
def test_db_setup() -> str:
    """`otomaix_test`i sıfırdan yaratır ve tüm migration'ları uygular.

    Her oturumda veritabanı DROP + CREATE edilir; migration'ların idempotent
    olduğu varsayılmaz, durum deterministiktir. Canlı `otomaix` veritabanına
    dokunulmaz.
    """
    url = test_database_url()
    _recreate_database(url)
    _apply_migrations(url)
    return url


def _scratch_database_url() -> str:
    """Şema-yıkıcı testlerin atılabilir ikinci veritabanı (guard'dan geçmiş)."""
    return _require_disposable_database(
        _with_database(test_database_url(), SCRATCH_DB_NAME)
    )


def _scratch_database(*, with_migrations: bool):
    """`otomaix_test_scratch`i sıfırdan kurar, test bitince düşürür."""
    url = _scratch_database_url()
    _recreate_database(url)
    if with_migrations:
        _apply_migrations(url)
    try:
        yield url
    finally:
        _drop_database(url)


@pytest.fixture
def scratch_db_migrated():
    """Tüm migration'ları uygulanmış, şeması bozulabilir taze veritabanı."""
    yield from _scratch_database(with_migrations=True)


@pytest.fixture
def scratch_db_empty():
    """Boş veritabanı — migration'ları test edilen aracın KENDİSİ uygular."""
    yield from _scratch_database(with_migrations=False)


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
