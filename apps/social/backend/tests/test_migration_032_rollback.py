"""Task 3 — dağıtım gerçeği, geri alma sözleşmesi ve aktivasyon atomikliği.

Üç bağımsız iddia sınanır (plan Task 3):

1. **Runner sözleşmesi** — `shared/local-deployment/migrations/run-migrations.sh`
   dosya listesini KANONİK dizinden (`shared/db/migrations`) glob'lar, numara
   sırasında uygular, `docker compose`u açık `-f` ile çağırır ve her psql
   çağrısına `-v ON_ERROR_STOP=1` geçirir — SQL hatası sıfır-dışı çıkış üretir
   ve zincir orada DURur (sonraki migration'lar uygulanmaz).
2. **Geri alma sözleşmesi (F4 tahkimi)** — `rollback/032_down.sql` veri varken
   HİÇBİR değişiklik yapmadan reddeder; boş-veri yolunda 032'nin açtığı her
   nesneyi kaldırır ve kök sektör seed'ine dokunmaz.
3. **R-17 ampirik ölçümü (spec §10.3)** — iki-adım aktivasyon TEK transaction'da
   geçer; ters sıra kısmi benzersiz indeksçe reddedilir.

Runner testleri gerçek `docker`a muhtaç değildir: PATH'e konan bir `docker`
kabuğu (shim) çağrıyı olduğu gibi kaydeder ve `psql` bölümünü yerel atılabilir
veritabanına yönlendirir. Böylece komutun GERÇEK argümanları (compose dosyası,
ON_ERROR_STOP bayrağı) ölçülür, taklit edilmez.

Şema-yıkıcı testler `otomaix_test`e DEĞİL, her testte sıfırdan kurulan
`otomaix_test_scratch`e koşar (conftest guard'ı ikisini de atılabilir sayar).
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import time
import uuid
from pathlib import Path

import asyncpg
import pytest

from tests import conftest as infra

ROLLBACK_SQL = infra.MIGRATIONS_DIR / "rollback" / "032_down.sql"
RUNNER = infra.REPO_ROOT / "shared" / "local-deployment" / "migrations" / "run-migrations.sh"
COMPOSE_FILE = infra.REPO_ROOT / "shared" / "local-deployment" / "docker-compose.yml"


# --- psql yardımcıları -----------------------------------------------------


def _psql(url: str, *args: str) -> subprocess.CompletedProcess:
    argv, env = infra.psql_argv(url)
    return subprocess.run(
        argv + list(args), env=env, capture_output=True, text=True
    )


def _run_sql(url: str, sql: str) -> None:
    result = _psql(url, "-c", sql)
    assert result.returncode == 0, result.stderr


def _scalar(url: str, sql: str) -> str:
    result = _psql(url, "--tuples-only", "--no-align", "-c", sql)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def _apply_rollback(url: str) -> subprocess.CompletedProcess:
    """`032_down.sql`i transaction sarmalayıcısı OLMADAN uygular.

    Sarmalayıcı yok: "hiçbir değişiklik yapmadan durdu" iddiası, ROLLBACK'in
    gizlediği bir sonuç değil, veritabanının kalıcı durumundan okunur.
    """
    return _psql(url, "-f", str(ROLLBACK_SQL))


# --- 1. R-17: iki-adım aktivasyon atomikliği ------------------------------


async def _sector_pair(db) -> uuid.UUID:
    slug = f"t3-{uuid.uuid4().hex[:8]}"
    root_id = await db.fetchval(
        "INSERT INTO social.sectors (slug, display_name) VALUES ($1, $1) RETURNING id",
        f"{slug}-kok",
    )
    return await db.fetchval(
        """
        INSERT INTO social.sectors (slug, display_name, parent_sector_id)
        VALUES ($1, $1, $2) RETURNING id
        """,
        f"{slug}-alt",
        root_id,
    )


async def _package(db, sector_id, *, version: int, status: str) -> uuid.UUID:
    return await db.fetchval(
        """
        INSERT INTO social.sector_packages
            (sector_id, version, status, schema_version, content)
        VALUES ($1, $2, $3, 1, $4) RETURNING id
        """,
        sector_id,
        version,
        status,
        '{"kapsam": "t3"}',
    )


async def test_two_step_activation_in_single_transaction_succeeds(db):
    """R-17: `archived←active` + `active←draft` TEK transaction'da geçer.

    Kısmi benzersiz indeks deyim-sonunda değerlendirilir; doğru sırada (önce
    eski sürüm arşive, sonra yeni sürüm aktife) ara durumda ikinci `active`
    hiç doğmaz. Aktivasyonun tek transaction'da koşabildiği ampirik dayanaktır
    (plan "bağladığı teknik kararlar" #8).
    """
    sub_id = await _sector_pair(db)
    current = await _package(db, sub_id, version=1, status="active")
    incoming = await _package(db, sub_id, version=2, status="draft")

    async with db.transaction():
        await db.execute(
            "UPDATE social.sector_packages SET status = 'archived' WHERE id = $1",
            current,
        )
        await db.execute(
            """
            UPDATE social.sector_packages
               SET status = 'active', activated_at = now()
             WHERE id = $1
            """,
            incoming,
        )

    rows = {
        row["id"]: row["status"]
        for row in await db.fetch(
            "SELECT id, status FROM social.sector_packages WHERE sector_id = $1",
            sub_id,
        )
    }
    assert rows == {current: "archived", incoming: "active"}


async def test_wrong_order_activation_rejected_by_partial_index(db):
    """Ters sıra (önce yeni aktif) kısmi indeksle DB düzeyinde reddedilir."""
    sub_id = await _sector_pair(db)
    current = await _package(db, sub_id, version=1, status="active")
    incoming = await _package(db, sub_id, version=2, status="draft")

    with pytest.raises(asyncpg.exceptions.UniqueViolationError):
        async with db.transaction():
            await db.execute(
                "UPDATE social.sector_packages SET status = 'active' WHERE id = $1",
                incoming,
            )
            await db.execute(
                "UPDATE social.sector_packages SET status = 'archived' WHERE id = $1",
                current,
            )

    # Reddedilen geçiş hiçbir iz bırakmaz: eski sürüm hâlâ tek aktiftir.
    rows = {
        row["id"]: row["status"]
        for row in await db.fetch(
            "SELECT id, status FROM social.sector_packages WHERE sector_id = $1",
            sub_id,
        )
    }
    assert rows == {current: "active", incoming: "draft"}


# --- 2. Geri alma sözleşmesi ----------------------------------------------

# 032'nin açtığı nesneler — geri alma bunların tamamını kaldırmalı.
_TABLES = ("sector_packages", "sector_research_artifacts", "generation_stamps")
_COLUMNS = (("brands", "sub_sector_id"), ("posts", "package_id"), ("posts", "package_version"))
_TRIGGERS = (
    ("sectors", "sectors_reject_reparenting"),
    ("brands", "brands_sub_sector_must_be_sub"),
)
_FUNCTIONS = (
    "reject_research_artifact_mutation",
    "require_sub_sector_reference",
    "reject_sector_reparenting",
)

_SEED_SQL = """
INSERT INTO social.sectors (slug, display_name) VALUES ('t3-kok', 'T3 Kok');
INSERT INTO social.sectors (slug, display_name, parent_sector_id)
VALUES ('t3-alt', 'T3 Alt', (SELECT id FROM social.sectors WHERE slug = 't3-kok'));
INSERT INTO social.brands (name, sub_sector_id)
VALUES ('T3 Marka', (SELECT id FROM social.sectors WHERE slug = 't3-alt'));
"""

_PACKAGE_DATA_SQL = """
INSERT INTO social.sector_packages (sector_id, version, status, schema_version, content)
VALUES ((SELECT id FROM social.sectors WHERE slug = 't3-alt'), 1, 'active', 1, '{"k": 1}');
INSERT INTO social.sector_research_artifacts (run_id, sector_slug, kind, source, content_md)
VALUES ('t3-run', 't3-alt', 'research', 'claude-research', '# ham kanit');
INSERT INTO social.generation_stamps (brand_id, package_id, package_version)
SELECT b.id, p.id, p.version FROM social.brands b, social.sector_packages p
 WHERE b.name = 'T3 Marka' AND p.version = 1;
INSERT INTO social.posts (brand_id, package_id, package_version)
SELECT b.id, p.id, p.version FROM social.brands b, social.sector_packages p
 WHERE b.name = 'T3 Marka' AND p.version = 1;
"""


def _table_exists(url: str, name: str) -> bool:
    return _scalar(url, f"SELECT to_regclass('social.{name}') IS NOT NULL") == "t"


def _column_exists(url: str, table: str, column: str) -> bool:
    return (
        _scalar(
            url,
            "SELECT count(*) FROM information_schema.columns "
            f"WHERE table_schema = 'social' AND table_name = '{table}' "
            f"AND column_name = '{column}'",
        )
        == "1"
    )


def _trigger_exists(url: str, table: str, trigger: str) -> bool:
    return (
        _scalar(
            url,
            "SELECT count(*) FROM pg_trigger t "
            f"WHERE t.tgrelid = 'social.{table}'::regclass "
            f"AND NOT t.tgisinternal AND t.tgname = '{trigger}'",
        )
        == "1"
    )


def _function_exists(url: str, name: str) -> bool:
    return (
        _scalar(
            url,
            "SELECT count(*) FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace "
            f"WHERE n.nspname = 'social' AND p.proname = '{name}'",
        )
        == "1"
    )


def test_rollback_refuses_when_package_data_exists(scratch_db_migrated):
    """Veri varken geri alma DURur ve HİÇBİR nesneyi düşürmez.

    Süresiz-saklama rejimindeki (K-140/141) paket ve ham kanıt satırları bir
    script'le imha edilemez; canlıda yol forward-fix migration'dır.
    """
    url = scratch_db_migrated
    _run_sql(url, _SEED_SQL)
    _run_sql(url, _PACKAGE_DATA_SQL)

    result = _apply_rollback(url)

    assert result.returncode != 0, (
        f"veri varken geri alma sessizce koştu — stdout:\n{result.stdout}"
    )
    assert "REDDEDILDI" in result.stderr, result.stderr

    # Kalıcı durum: hiçbir nesne düşmemiş, hiçbir satır silinmemiş.
    for table in _TABLES:
        assert _table_exists(url, table), f"{table} düşürülmüş"
    for table, column in _COLUMNS:
        assert _column_exists(url, table, column), f"{table}.{column} düşürülmüş"
    for table, trigger in _TRIGGERS:
        assert _trigger_exists(url, table, trigger), f"{trigger} düşürülmüş"
    for function in _FUNCTIONS:
        assert _function_exists(url, function), f"{function} düşürülmüş"

    assert _scalar(url, "SELECT count(*) FROM social.sector_packages") == "1"
    assert _scalar(url, "SELECT count(*) FROM social.sector_research_artifacts") == "1"
    assert _scalar(url, "SELECT count(*) FROM social.generation_stamps") == "1"
    assert (
        _scalar(url, "SELECT count(*) FROM social.posts WHERE package_id IS NOT NULL")
        == "1"
    )
    assert (
        _scalar(url, "SELECT count(*) FROM social.sectors WHERE slug = 't3-alt'") == "1"
    )


def _wait_for_writer_lock(url: str, table: str, timeout: float = 15.0) -> None:
    """Eşzamanlı yazarın satır kilidini alana kadar bekler (yoklama)."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        held = _scalar(
            url,
            "SELECT count(*) FROM pg_locks l JOIN pg_class c ON c.oid = l.relation "
            f"WHERE c.relname = '{table}' AND l.mode = 'RowExclusiveLock' AND l.granted",
        )
        if held != "0":
            return
        time.sleep(0.1)
    raise AssertionError(f"eşzamanlı yazar {table} üstünde kilit almadı")


@pytest.mark.parametrize("isolation", ["read committed", "repeatable read"])
def test_rollback_refuses_data_committed_while_it_waits(scratch_db_migrated, isolation):
    """Sayım ile silme arasına giren yazar veriyi KAYBETTİREMEZ.

    Kilitsiz sürümde pencere gerçekti: preflight açık transaction'daki satırı
    GÖREMEZ (0 sayar), sonra `DROP TABLE` yazarın commit'ini bekler ve satırı
    onunla birlikte yok ederdi. Kilit sayımdan ÖNCE alındığı için script artık
    yazarı bekler, satırı görür ve REDDEDER.

    Oturumun varsayılan yalıtımı REPEATABLE READ ise kilit tek başına YETMEZ:
    o seviyede snapshot, transaction'ın ilk deyiminde donar ve kilit beklenirken
    commit edilen satır sayıma GÖRÜNMEZ — script kendi yalıtımını READ COMMITTED'a
    çekmek zorundadır (Codex checkpoint 3, tur 2).
    """
    url = scratch_db_migrated
    _run_sql(url, _SEED_SQL)

    argv, env = infra.psql_argv(url)
    writer = subprocess.Popen(
        argv + ["-f", "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        text=True,
    )
    writer.stdin.write(
        "BEGIN;\n"
        "INSERT INTO social.sector_packages "
        "(sector_id, version, status, schema_version, content) VALUES "
        "((SELECT id FROM social.sectors WHERE slug = 't3-alt'), 1, 'draft', 1, "
        "'{\"k\": 1}');\n"
        "SELECT pg_sleep(5);\n"
        "COMMIT;\n"
    )
    writer.stdin.close()

    try:
        _wait_for_writer_lock(url, "sector_packages")

        # Sonsuz bekleme testi asmasın: kilit 60 sn'de gelmezse psql hata verir
        # (o hâlde mesaj REDDEDILDI olmaz ve test doğru sebeple düşer).
        blocked_env = dict(env)
        # PGOPTIONS'ta boşluk TIRNAKLA değil ters bölü ile kaçırılır.
        escaped = isolation.replace(" ", "\\ ")
        blocked_env["PGOPTIONS"] = (
            f"-c lock_timeout=60s -c default_transaction_isolation={escaped}"
        )
        started = time.monotonic()
        result = subprocess.run(
            argv + ["-f", str(ROLLBACK_SQL)],
            env=blocked_env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        waited = time.monotonic() - started
    finally:
        writer.wait(timeout=60)

    assert result.returncode != 0, (
        f"araya giren yazara ragmen geri alma kostu — stdout:\n{result.stdout}"
    )
    assert "REDDEDILDI" in result.stderr, result.stderr
    assert waited >= 1.0, (
        "geri alma yazarı hiç beklemedi — kilit sayımdan önce alınmıyor olabilir "
        f"(bekleme: {waited:.2f} sn)"
    )

    # Yazarın satırı ve tablolar yerinde.
    assert _table_exists(url, "sector_packages")
    assert _scalar(url, "SELECT count(*) FROM social.sector_packages") == "1"


def test_rollback_clean_path_full_teardown(scratch_db_migrated):
    """Veri boşken geri alma 032'nin TÜM nesnelerini kaldırır; kök seed durur."""
    url = scratch_db_migrated
    _run_sql(url, _SEED_SQL)

    root_count_before = _scalar(
        url, "SELECT count(*) FROM social.sectors WHERE parent_sector_id IS NULL"
    )
    assert int(root_count_before) > 0, "kök sektör seed'i yok — test anlamsız"

    result = _apply_rollback(url)
    assert result.returncode == 0, f"temiz yolda geri alma başarısız:\n{result.stderr}"

    for table in _TABLES:
        assert not _table_exists(url, table), f"{table} hâlâ duruyor"
    for table, column in _COLUMNS:
        assert not _column_exists(url, table, column), f"{table}.{column} hâlâ duruyor"
    for table, trigger in _TRIGGERS:
        assert not _trigger_exists(url, table, trigger), f"{trigger} hâlâ duruyor"
    for function in _FUNCTIONS:
        assert not _function_exists(url, function), f"{function} hâlâ duruyor"
    assert (
        _scalar(
            url,
            "SELECT count(*) FROM pg_indexes WHERE schemaname = 'social' "
            "AND indexname = 'idx_brands_sub_sector_id'",
        )
        == "0"
    ), "idx_brands_sub_sector_id hâlâ duruyor"

    # Alt sektör satırları gider; kök seed ve marka satırı KALIR.
    assert (
        _scalar(
            url, "SELECT count(*) FROM social.sectors WHERE parent_sector_id IS NOT NULL"
        )
        == "0"
    )
    assert (
        _scalar(
            url, "SELECT count(*) FROM social.sectors WHERE parent_sector_id IS NULL"
        )
        == root_count_before
    )
    assert _scalar(url, "SELECT count(*) FROM social.brands WHERE name = 'T3 Marka'") == "1"


def test_rollback_refuses_when_protected_tables_are_absent(scratch_db_migrated):
    """Korunan tablolar yokken geri alma BAŞTA durur — ikinci koşum reddedilir.

    Olmayan tablo kilitlenemez. Sessizce devam eden bir koşumda, preflight ile
    `DROP TABLE IF EXISTS` arasında başka biri 032'yi ileri uygulayıp kanıt
    yazarsa, DROP o yeni tabloyu görür ve kalıcı olarak yok ederdi (Codex
    checkpoint 3, tur 3 — kritik). Giriş kapısı bu yolu tamamen kapatır.
    """
    url = scratch_db_migrated

    first = _apply_rollback(url)
    assert first.returncode == 0, f"ilk geri alma başarısız:\n{first.stderr}"
    assert not _table_exists(url, "sector_packages")

    second = _apply_rollback(url)
    assert second.returncode != 0, (
        f"korunan tablolar yokken geri alma yine koştu — stdout:\n{second.stdout}"
    )
    assert "REDDEDILDI" in second.stderr, second.stderr
    assert "korunan tablolar eksik" in second.stderr, second.stderr


def test_rollback_refuses_to_run_inside_an_enclosing_transaction(scratch_db_migrated):
    """`psql -1` gibi sarmalayıcı çağrı REDDEDİLİR — sahiplik çakışması.

    Dosya kendi transaction'ını sahiplenir. Dışarıdan bir transaction açılmışsa
    içerideki `BEGIN` savepoint YARATMAZ ve dosyanın `COMMIT`i ÇAĞIRANIN
    transaction'ını erken kapatır: çağıranın atomik sandığı toplu iş, yıkım
    kalıcı olduktan sonra yarıda kalabilir. Bu durum SQL'den saptanabilir —
    transaction bloğu içinde `DO ... COMMIT` "invalid transaction termination"
    verir — ve script hiçbir şeye dokunmadan durur.
    """
    url = scratch_db_migrated
    _run_sql(url, _SEED_SQL)

    argv, env = infra.psql_argv(url)
    result = subprocess.run(
        argv + ["-1", "-f", str(ROLLBACK_SQL)],
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode != 0, (
        f"sarmalanmış çağrı sessizce koştu — stdout:\n{result.stdout}"
    )
    for table in _TABLES:
        assert _table_exists(url, table), f"{table} sarmalanmış çağrıda düşürüldü"
    for table, column in _COLUMNS:
        assert _column_exists(url, table, column), f"{table}.{column} düşürüldü"


# --- 3. Runner sözleşmesi -------------------------------------------------

_DOCKER_SHIM = """#!/bin/bash
# Test kabuğu: `docker compose ... exec -T postgres psql ...` çağrısını olduğu
# gibi kaydeder, psql bölümünü yerel atılabilir veritabanına yönlendirir.
set -uo pipefail
printf '%s\\n' "docker $*" >> "$SHIM_LOG"

args=("$@")
index=-1
for i in "${!args[@]}"; do
    if [ "${args[$i]}" = "psql" ]; then index=$i; break; fi
done
if [ "$index" -lt 0 ]; then
    echo "shim: cagri psql degil: $*" >&2
    exit 90
fi

# Sondaki bağlantı argümanları öncekileri ezer — bayraklar (ON_ERROR_STOP dahil)
# runner'dan geldiği GİBİ geçer.
exec psql --no-psqlrc "${args[@]:$((index + 1))}" \\
    -h "$SHIM_HOST" -p "$SHIM_PORT" -U "$SHIM_USER" -d "$SHIM_DB"
"""


def _shim_env(tmp_path: Path, url: str) -> tuple[dict[str, str], Path]:
    """PATH'e sahte `docker` koyar; psql'i scratch veritabanına yönlendirir."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(parents=True, exist_ok=True)
    shim = bin_dir / "docker"
    shim.write_text(_DOCKER_SHIM)
    shim.chmod(0o755)

    log = tmp_path / "docker-calls.log"
    log.write_text("")

    argv, psql_env = infra.psql_argv(url)
    env = dict(psql_env)
    env["PATH"] = f"{bin_dir}{os.pathsep}{os.environ['PATH']}"
    env["SHIM_LOG"] = str(log)
    env["SHIM_HOST"] = infra.REQUIRED_HOST
    env["SHIM_PORT"] = str(infra.REQUIRED_PORT)
    env["SHIM_USER"] = argv[argv.index("-U") + 1]
    env["SHIM_DB"] = infra.SCRATCH_DB_NAME
    return env, log


def _applied_files(stdout: str) -> list[str]:
    return [
        line.split("→", 1)[1].strip() for line in stdout.splitlines() if "→" in line
    ]


@pytest.mark.parametrize("cwd_kind", ["repo-root", "local-deployment"])
def test_runner_glob_covers_canonical_dir_in_order(tmp_path, scratch_db_empty, cwd_kind):
    """Runner kanonik dizini glob'lar, numara sırasında uygular, cwd'den bağımsız.

    Bayat elle-yazılmış liste (001–011) yerine `shared/db/migrations` esastır;
    sıra `conftest`in kendi keşfiyle BİREBİR aynı olmalıdır — iki keşif tek
    gerçeği okur.
    """
    env, log = _shim_env(tmp_path, scratch_db_empty)
    cwd = (
        infra.REPO_ROOT
        if cwd_kind == "repo-root"
        else infra.REPO_ROOT / "shared" / "local-deployment"
    )

    result = subprocess.run(
        ["bash", str(RUNNER)], cwd=str(cwd), env=env, capture_output=True, text=True
    )
    assert result.returncode == 0, f"runner başarısız:\n{result.stdout}\n{result.stderr}"

    expected = [path.name for path in infra._migration_files()]
    assert _applied_files(result.stdout) == expected
    assert "032_sector_packages.sql" in expected, "kanonik dizin 032'yi içermiyor"

    calls = [line for line in log.read_text().splitlines() if line.strip()]
    assert calls, "docker hiç çağrılmadı"
    for call in calls:
        assert "-v ON_ERROR_STOP=1" in call, f"ON_ERROR_STOP taşımayan çağrı: {call}"
        assert f"compose -f {COMPOSE_FILE} exec -T postgres psql" in call, call

    # Zincir gerçekten uygulandı: 032'nin tabloları scratch veritabanında.
    assert _table_exists(scratch_db_empty, "sector_packages")
    assert _table_exists(scratch_db_empty, "generation_stamps")


def test_runner_stops_on_sql_error(tmp_path, scratch_db_empty):
    """Geçersiz SQL sıfır-dışı çıkış üretir; zincir DURur, 032 hiç uygulanmaz.

    `ON_ERROR_STOP=1` olmadan psql hatayı basar ama 0 döner; `set -e` de zinciri
    kesmez ve kısmi şema "başarılı" raporlanır.
    """
    tree = tmp_path / "repo"
    canonical = tree / "shared" / "db" / "migrations"
    deploy = tree / "shared" / "local-deployment"
    canonical.mkdir(parents=True)
    (deploy / "migrations").mkdir(parents=True)

    for path in infra._migration_files():
        shutil.copy2(path, canonical / path.name)
    shutil.copy2(RUNNER, deploy / "migrations" / RUNNER.name)
    shutil.copy2(COMPOSE_FILE, deploy / "docker-compose.yml")

    # 031 ile 032 ARASINA giren bozuk dosya: sıra numarası 031, adı sonda.
    (canonical / "031_zz_injected_bad.sql").write_text(
        "CREATE TABLE social.t3_injected_marker (id INT);\n"
        "BU GECERLI SQL DEGILDIR;\n"
    )

    env, _ = _shim_env(tmp_path, scratch_db_empty)
    result = subprocess.run(
        ["bash", str(deploy / "migrations" / RUNNER.name)],
        cwd=str(tree),
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0, (
        f"gecersiz SQL sessizce kabul edildi — stdout:\n{result.stdout}"
    )
    applied = _applied_files(result.stdout)
    assert "031_zz_injected_bad.sql" in applied
    assert "032_sector_packages.sql" not in applied, "zincir hatadan sonra devam etti"
    assert not _table_exists(scratch_db_empty, "sector_packages"), "kısmi 032 nesnesi var"

# ─── Dağıtım atomikliği (final review F-H2) ─────────────────────────────────


def test_single_transaction_exemption_is_exact():
    """Muafiyet listesi ile GERÇEK iki yönlü uyumlu: liste ne eksik ne fazla.

    Muafiyetin İKİ meşru gerekçesi var ve ikisi de dosyanın kendi içeriğinden
    okunur:
      * `CREATE INDEX CONCURRENTLY` — transaction bloğunda KOŞAMAZ (011).
      * Kendi `BEGIN/COMMIT`i — dosya zaten atomiktir (017). ÖLÇÜLDÜ: böyle bir
        dosyayı `--single-transaction` ile sarmak garantiyi ZAYIFLATIR, çünkü
        içteki COMMIT dıştaki transaction'ı erken kapatır ve sonrasındaki DDL
        hata durumunda bile kalır.

    Kontrat POZİTİF ve İKİ YÖNLÜDÜR: muaf olan dosyanın gerekçelerden BİRİ
    olmalı, muaf OLMAYAN hiçbirinde İKİSİ DE olmamalı. Tek yön yeterli olmazdı —
    yalnız birincisi listeye keyfî dosya eklenmesine, yalnız ikincisi
    CONCURRENTLY ekleyen yeni bir migration'ın listeye yazılmadan kalmasına
    izin verirdi. İkincisi üretimde "cannot run inside a transaction block" ile
    PATLARDI.
    """
    concurrently, self_tx = set(), set()
    for path in infra._migration_files():
        body = path.read_text(encoding="utf-8")
        if re.search(r"\bCONCURRENTLY\b", body):
            concurrently.add(path.name)
        if re.search(r"(?mi)^\s*(BEGIN|COMMIT)\s*;", body):
            self_tx.add(path.name)

    exempt = set(infra.NON_TRANSACTIONAL_MIGRATIONS)
    assert concurrently | self_tx == exempt, (
        "muafiyet listesi gerçekle uyuşmuyor\n"
        f"CONCURRENTLY içeren: {sorted(concurrently)}\n"
        f"kendi transaction'ı olan: {sorted(self_tx)}\n"
        f"muaf listelenen: {sorted(exempt)}"
    )
    for name in exempt:
        assert name in concurrently or name in self_tx, (
            f"{name} gerekçesiz muaf — listede ama iki sebepten hiçbirini taşımıyor"
        )

    # Dağıtım runner'ı ile test altyapısı AYNI listeyi taşımalı (tek gerçek).
    runner = (
        infra.REPO_ROOT / "shared" / "local-deployment" / "migrations"
        / "run-migrations.sh"
    ).read_text(encoding="utf-8")
    for name in exempt:
        assert f'"{name}"' in runner, (
            f"{name} test altyapısında muaf ama runner'da değil — iki okuyucu ıraksadı"
        )


def test_self_transactional_file_is_not_double_wrapped(scratch_db_empty):
    """Kendi COMMIT'ini taşıyan dosyayı sarmak garantiyi ZAYIFLATIR — ölçülür.

    Bu, muafiyetin ikinci gerekçesinin gerçekliğidir: `--single-transaction`
    altında içteki COMMIT dıştaki transaction'ı ERKEN kapatır, ve o noktadan
    sonrası hata durumunda bile geri alınmaz. Yani sarmak, korumadığı gibi
    koruduğu izlenimi verir.
    """
    argv, env = infra.psql_argv(scratch_db_empty)
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False) as handle:
        handle.write(
            "CREATE SCHEMA IF NOT EXISTS probe;\n"
            "BEGIN;\nCREATE TABLE probe.inner_tx (id INT);\nCOMMIT;\n"
            "CREATE TABLE probe.after_commit (id INT);\n"
            "DO $v$ BEGIN RAISE EXCEPTION 'red (kurgu)'; END $v$;\n"
        )
        script_path = handle.name

    def _exists(name: str) -> str:
        result = subprocess.run(
            argv + ["--tuples-only", "--no-align", "-c",
                    f"SELECT to_regclass('probe.{name}') IS NOT NULL"],
            env=env, capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        return result.stdout.strip()

    try:
        result = subprocess.run(
            argv + ["--single-transaction", "-f", script_path],
            env=env, capture_output=True, text=True,
        )
        assert result.returncode != 0
        assert _exists("inner_tx") == "t" and _exists("after_commit") == "t", (
            "içteki COMMIT dıştaki transaction'ı kapatmadı — muafiyetin ikinci "
            "gerekçesi bu sürümde geçerli DEĞİL, liste gözden geçirilmeli"
        )
    finally:
        os.unlink(script_path)


def test_failed_migration_leaves_no_partial_ddl(scratch_db_empty):
    """Doğrulama bloğu reddettiğinde ÖNCEKİ DDL de geri alınır.

    Bu testin ölçtüğü şey ÜRETİM anlambilimidir: dosya `--single-transaction`
    ile koşar. Ölçüldü (2026-08-25) — bayraksız koşumda `ON_ERROR_STOP=1` yalnız
    AKIŞI durduruyor, doğrulama hatasından ÖNCE yaratılmış tablo commit edilmiş
    kalıyordu; yani başarısız bir dağıtım yarım değişmiş bir şema bırakırdı.

    Neden sahte bir dosya: gerçek 032'yi düşürmek için önce 001-031'i uygulamak
    gerekir ve ölçülen şey migration'ın İÇERİĞİ değil, ÇALIŞTIRMA anlambilimidir.
    Sahte dosya gerçek desenle aynı sırayı taşır: önce DDL, sonra reddeden
    doğrulama bloğu.
    """
    argv, env = infra.psql_argv(scratch_db_empty)

    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False) as handle:
        handle.write(
            "CREATE SCHEMA IF NOT EXISTS probe;\n"
            "CREATE TABLE probe.before_verify (id INT);\n"
            "DO $v$ BEGIN RAISE EXCEPTION 'dogrulama reddetti (kurgu)'; END $v$;\n"
        )
        script_path = handle.name

    def _exists() -> str:
        result = subprocess.run(
            argv + ["--tuples-only", "--no-align", "-c",
                    "SELECT to_regclass('probe.before_verify') IS NOT NULL"],
            env=env, capture_output=True, text=True,
        )
        assert result.returncode == 0, result.stderr
        return result.stdout.strip()

    try:
        applied = subprocess.run(
            argv + ["--single-transaction", "-f", script_path],
            env=env, capture_output=True, text=True,
        )
        assert applied.returncode != 0, "reddeden migration sıfır çıkış verdi"
        assert _exists() == "f", (
            "doğrulama öncesi DDL commit edilmiş kaldı — dağıtım ATOMİK DEĞİL"
        )

        # Pozitif kontrol: bayrak OLMADAN aynı dosya kalıntı bırakır. Bu satır,
        # yukarıdaki iddianın bayraktan geldiğini kanıtlar (yoksa test, hiçbir
        # şey ölçmeden yeşil kalabilirdi).
        bare = subprocess.run(
            argv + ["-f", script_path], env=env, capture_output=True, text=True
        )
        assert bare.returncode != 0
        assert _exists() == "t", (
            "bayraksız koşum da temiz çıktı — bu test bayrağın etkisini ÖLÇMÜYOR"
        )
    finally:
        os.unlink(script_path)


@pytest.mark.parametrize("kind", ["symlink", "dangling-symlink"])
def test_runner_rejects_symlinked_migrations(tmp_path, scratch_db_empty, kind):
    """Symlink migration VERİTABANINA DOKUNMADAN reddedilir.

    Dosya adı, uygulanacak baytların kimliği yerine geçemez: `-f` symlink'i
    İZLER, yani kanonik dizindeki numaralı bir symlink baytları bu ağacın
    DIŞINDA duran (ve orada değişebilen) bir dosyadan alıp canlıya uygulatırdı.
    Kapı ilk `psql` çağrısından ÖNCE koşmalı — yoksa red, şema zaten değişmişken
    gelir.

    Tekrarlı NUMARA burada bilerek test EDİLMEZ: eşit numarada dosya adına
    düşmek bu deponun BELGELİ davranışıdır (runner ve test keşfi aynı `(int, ad)`
    sırasını paylaşır) ve `test_runner_stops_on_sql_error` ona dayanır.
    """
    tree = tmp_path / "repo"
    canonical = tree / "shared" / "db" / "migrations"
    deploy = tree / "shared" / "local-deployment"
    (deploy / "migrations").mkdir(parents=True)
    canonical.mkdir(parents=True)
    for path in infra._migration_files():
        shutil.copy2(path, canonical / path.name)
    shutil.copy2(RUNNER, deploy / "migrations" / RUNNER.name)
    shutil.copy2(COMPOSE_FILE, deploy / "docker-compose.yml")

    if kind == "symlink":
        outside = tmp_path / "outside.sql"
        outside.write_text("SELECT 1;\n", encoding="utf-8")
        (canonical / "900_outside.sql").symlink_to(outside)
    else:
        (canonical / "901_dangling.sql").symlink_to(tmp_path / "yok.sql")

    env, log = _shim_env(tmp_path, scratch_db_empty)
    result = subprocess.run(
        ["bash", str(deploy / "migrations" / RUNNER.name)],
        cwd=str(tree),
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0, (
        f"{kind} sessizce kabul edildi:\n{result.stdout}\n{result.stderr}"
    )
    calls = [line for line in log.read_text().splitlines() if line.strip()]
    assert not calls, (
        f"{kind} reddedilmeden ÖNCE veritabanına dokunuldu: {calls[:3]}"
    )
