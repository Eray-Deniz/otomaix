"""Migration 036 — koşu kaydı · politika raporu · onay anlık görüntüsü · atama geçmişi.

Bu dosya Plan 2'nin ŞEMA katmanını pinler (plan Task 6 + bağlayıcı arayüz eki).
Ölçülen sözleşmeler:

1. **`social.sector_package_runs`** — bir denemenin KANONİK kaydı. `run_id`
   benzersizdir; yeniden koşum yeni `run_id` + `parent_run_id` alır. `durum`
   (yürütmenin hâli) ile `sonuc` (motorun çıktısı) AYRI kolonlardır ve ikisi de
   kapalı kümedir.
2. **`social.package_rollback_plans`** (K-145) — olay başına geri alma planı.
   Kimliği bileşiktir (`incident_id`, `package_id`); `id` kolonu YOKTUR.
   `hedefsiz` durumunun AÇIK veri karşılığı iki yönlü bir CHECK'tir.
3. **`social.brand_sub_sector_history`** (K-45) — maruziyet kanıtı. Tabloyu bir
   TETİKLEYİCİ yazar: atama yolu hangi koddan geçerse geçsin aralık açılır ve
   kapanır. Geri doldurma YOKTUR.
4. **Donmuş sözleşmelere sürüm-farkında dokunuş** — 032'nin indeks/kısıt
   kümesi ve 033'ün olay CHECK'i 036 SONRASI genişlemiş hâli de kabul eder;
   adı geçmeyen fazladan nesne ve tanınmayan olay türü hâlâ REDDEDİLİR.
5. **F20 — geri alma VERİ VARKEN fail-closed durur.** `036_down.sql` Plan 2
   verisi varsa `rc≠0` ile durur ve HİÇBİR şeye dokunmaz (bayt-bayt ölçülür).

**Kapanış SAYARAK değil YAPIYLA kurulur.** CHECK kapıları elle seçilmiş
örneklerle değil, değer kümelerinin ÇAPRAZ ÇARPIMINDAN üretilen matrislerle
ölçülür; her hücrenin beklentisi kuralın KENDİSİNDEN türetilir, elle
listelenmez. Böylece "şu kombinasyon denenmemiş" hücresi doğamaz.
"""

from __future__ import annotations

import importlib.util
import itertools
import json
import pathlib
import re
import subprocess
import uuid
from datetime import datetime, timedelta, timezone

import asyncpg
import pytest

from app.services import package_events as package_events_module
from app.services.package_events import (
    APPROVAL_EVENTS,
    BRAND_SCOPED_EVENTS,
    EVENT_TYPES,
    EVENT_VERSION_CONTRACT,
    LIFECYCLE_EVENTS,
    VERSION_CONTRACT_VALUES,
    PackageEventContractError,
    assert_version_contract_is_wellformed,
    log_package_event,
)

from . import conftest as infra

MIGRATIONS_DIR = infra.MIGRATIONS_DIR
ROLLBACK_DIR = MIGRATIONS_DIR / "rollback"

MIGRATION_032 = MIGRATIONS_DIR / "032_sector_packages.sql"
MIGRATION_033 = MIGRATIONS_DIR / "033_package_events.sql"
MIGRATION_036 = MIGRATIONS_DIR / "036_package_runs.sql"

DOWN_033 = ROLLBACK_DIR / "033_down.sql"
DOWN_034 = ROLLBACK_DIR / "034_down.sql"
DOWN_036 = ROLLBACK_DIR / "036_down.sql"

# Bu görevde DOĞAN üç geri alma script'i. `032_down.sql` / `035_down.sql`
# BİLEREK dışarıdadır: onlar `ON_ERROR_STOP`u çağıranın oturumuna SIZDIRIR ve o
# tutarsızlık kayıt altına alınmıştır, süpürülmemiştir (kontrolör kararı).
NEW_DOWN_SCRIPTS = (DOWN_033, DOWN_034, DOWN_036)

REFUSAL_MARKER_036 = "migration 036 geri alma REDDEDILDI"
REFUSAL_MARKER_033 = "migration 033 geri alma REDDEDILDI"
REFUSAL_MARKER_034 = "migration 034 geri alma REDDEDILDI"

FAILURE_MARKER_032 = "migration 032 garanti dogrulamasi BASARISIZ"
FAILURE_MARKER_033 = "migration 033 garanti dogrulamasi BASARISIZ"

# K-09 kısıtının ADI SÖZLEŞMEYLE SABİTTİR — katalogdan tahmin edilmez.
K09_CONSTRAINT = "sector_research_artifacts_run_source_kind_key"

# K-45 üreticisinin YAPISAL kapısının imzası. Üretici, dayandığı kolonu
# bulamazsa SESSİZ KALMAZ — bu metinle DURur.
HISTORY_PRODUCER_MARKER = "K-45 uretici KIRIK"

# Kapalı değer kümeleri — matrislerin ÜRETİCİSİ. Testler bu demetlerden
# çarpım alır; hücre listesi elle yazılmaz.
DURUM_VALUES = ("calisiyor", "tamamlandi", "tamamlanmadi")
SONUC_VALUES = (None, "activation_eligible", "no_change", "blocked")
KOSU_TURU_VALUES = ("ilk", "periyodik", "duzeltme")
PLAN_DURUM_VALUES = ("bekliyor", "tamamlandi", "hata", "hedefsiz")
APPROVAL_KARAR_VALUES = (None, "onay", "ret")


# ─── psql yardımcıları (şema-yıkıcı yol: `otomaix_test_scratch`) ────────────


def _psql(url: str, *args: str) -> subprocess.CompletedProcess:
    argv, env = infra.psql_argv(url)
    return subprocess.run(argv + list(args), env=env, capture_output=True, text=True)


def _run_sql(url: str, sql: str) -> None:
    result = _psql(url, "-c", sql)
    assert result.returncode == 0, result.stderr


def _scalar(url: str, sql: str) -> str:
    result = _psql(url, "--tuples-only", "--no-align", "-c", sql)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def _argv_without_error_stop(url: str) -> tuple[list[str], dict[str, str]]:
    """`-v ON_ERROR_STOP=1` çiftini ADINA göre düşürür, KONUMUNA göre değil.

    Aynı gerekçe `test_migration_035.py`de ölçüldü: konuma göre düşürmek,
    conftest argv'ye daha erken bir `-v` eklediğinde SESSİZCE yanlış çifti
    düşürür ve test ölçtüğünü sandığı şeyi ölçmez.
    """
    argv, env = infra.psql_argv(url)
    assert "ON_ERROR_STOP=1" in argv, f"conftest sözleşmesi değişmiş: {argv}"
    value = argv.index("ON_ERROR_STOP=1")
    assert argv[value - 1] == "-v", f"`ON_ERROR_STOP` bayrağı `-v` taşımıyor: {argv}"
    return argv[: value - 1] + argv[value + 1 :], env


def _apply_file(url: str, path, *, single_transaction: bool = True) -> subprocess.CompletedProcess:
    """Bir migration dosyasını dağıtım runner'ının anlambilimiyle uygular."""
    argv, env = infra.psql_argv(url)
    if single_transaction:
        argv = argv + ["--single-transaction"]
    return subprocess.run(argv + ["-f", str(path)], env=env, capture_output=True, text=True)


def _apply_down(url: str, path) -> subprocess.CompletedProcess:
    """Geri alma script'ini SARMALAYICI TRANSACTION OLMADAN uygular.

    Sarmalamıyoruz: "hiçbir değişiklik yapmadan reddetti" iddiası ROLLBACK'in
    gizlediği bir sonuç değil, veritabanının KALICI durumundan okunur.
    """
    return _psql(url, "-f", str(path))


def _reapply_in_session(url: str, migration, setup_sql: str = "") -> subprocess.CompletedProcess:
    """`setup_sql` + migration'ı TEK transaction'da koşar, sonra ROLLBACK.

    Diğer testlerin gördüğü şema değişmez (Postgres'te DDL transactional'dır).
    """
    argv, env = infra.psql_argv(url)
    script = f"BEGIN;\n{setup_sql}\n\\i {migration}\nROLLBACK;\n"
    return subprocess.run(argv, input=script, env=env, capture_output=True, text=True)


def _apply_range(url: str, *, upto: int) -> None:
    """001..`upto` arası migration'ları sırayla uygular — GLOB ile, elle liste YOK."""
    _run_sql(url, "CREATE SCHEMA IF NOT EXISTS social")
    _run_sql(url, "CREATE EXTENSION IF NOT EXISTS vector")
    for path in infra._migration_files():
        number = int(path.name.split("_", 1)[0])
        if number > upto:
            continue
        result = _apply_file(
            url,
            path,
            single_transaction=path.name not in infra.NON_TRANSACTIONAL_MIGRATIONS,
        )
        assert result.returncode == 0, f"{path.name} DURDU:\n{result.stderr}"


# ─── Şema + veri parmak izi (bayt-bayt karşılaştırma için) ──────────────────
#
# `pg_dump` KULLANILMAZ: bu makinede istemci 16.15, sunucu 18.3 — pg_dump daha
# yeni bir sunucudan dökmeyi REDDEDER (ölçüldü). Parmak izi katalogtan okunur.

_SCHEMA_FINGERPRINT_SQL = """
SELECT coalesce(string_agg(line, E'\n' ORDER BY line), '<bos>') FROM (
    SELECT 'rel|' || c.relname || '|' || c.relkind::text || '|' || c.relpersistence::text AS line
      FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
     WHERE n.nspname = 'social'
    UNION ALL
    SELECT 'col|' || c.relname || '|' || a.attname || '|'
           || format_type(a.atttypid, a.atttypmod) || '|' || a.attnotnull::text || '|'
           || coalesce(pg_get_expr(d.adbin, d.adrelid), '-')
      FROM pg_attribute a
      JOIN pg_class c ON c.oid = a.attrelid
      JOIN pg_namespace n ON n.oid = c.relnamespace
      LEFT JOIN pg_attrdef d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
     WHERE n.nspname = 'social' AND a.attnum > 0 AND NOT a.attisdropped
    UNION ALL
    SELECT 'con|' || c.relname || '|' || k.conname || '|' || pg_get_constraintdef(k.oid)
      FROM pg_constraint k
      JOIN pg_class c ON c.oid = k.conrelid
      JOIN pg_namespace n ON n.oid = c.relnamespace
     WHERE n.nspname = 'social'
    UNION ALL
    SELECT 'idx|' || i.indexname || '|' || i.indexdef
      FROM pg_indexes i WHERE i.schemaname = 'social'
    UNION ALL
    SELECT 'trg|' || t.tgname || '|' || pg_get_triggerdef(t.oid) || '|' || t.tgenabled::text
      FROM pg_trigger t
      JOIN pg_class c ON c.oid = t.tgrelid
      JOIN pg_namespace n ON n.oid = c.relnamespace
     WHERE n.nspname = 'social' AND NOT t.tgisinternal
    UNION ALL
    SELECT 'fun|' || p.proname || '|' || pg_get_functiondef(p.oid)
      FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
     WHERE n.nspname = 'social' AND p.prokind = 'f'
) AS s
"""

# Geri almanın DOKUNABİLECEĞİ her tablo — içerik de bayt-bayt karşılaştırılır.
_DATA_FINGERPRINT_TABLES = (
    "sector_package_runs",
    "package_rollback_plans",
    "brand_sub_sector_history",
    "package_events",
    "sector_research_artifacts",
    "sector_packages",
    "brands",
    "sectors",
    "admin_events",
)


def _schema_fingerprint(url: str) -> str:
    return _scalar(url, _SCHEMA_FINGERPRINT_SQL)


def _data_fingerprint(url: str) -> str:
    parts = []
    for table in _DATA_FINGERPRINT_TABLES:
        exists = _scalar(url, f"SELECT to_regclass('social.{table}') IS NOT NULL")
        if exists != "t":
            parts.append(f"{table}=<tablo yok>")
            continue
        rows = _scalar(
            url,
            f"SELECT coalesce(string_agg(t::text, E'\\n' ORDER BY t::text), '<bos>') "
            f"FROM social.{table} AS t",
        )
        parts.append(f"{table}=\n{rows}")
    return "\n".join(parts)


# ─── asyncpg yardımcıları (`db` fixture — her test kendi transaction'ında) ──

JSONB_RUN_COLUMNS = frozenset({
    "policy_report",
    "barrier_report",
    "final_candidate",
    "final_decision_log",
    "engine_diff",
    "approval_snapshot",
    "katman1_attestation",
    "readiness_attestation",
    "katman2_attestation",
})


async def _sub_sector(db) -> uuid.UUID:
    slug = f"t6-{uuid.uuid4().hex[:8]}"
    root_id = await db.fetchval(
        "INSERT INTO social.sectors (slug, display_name) VALUES ($1, $1) RETURNING id",
        f"{slug}-kok",
    )
    return await db.fetchval(
        "INSERT INTO social.sectors (slug, display_name, parent_sector_id) "
        "VALUES ($1, $1, $2) RETURNING id",
        f"{slug}-alt",
        root_id,
    )


async def _package(db, sector_id, *, version: int = 1, status: str = "draft") -> uuid.UUID:
    return await db.fetchval(
        "INSERT INTO social.sector_packages "
        "    (sector_id, version, status, schema_version, content) "
        "VALUES ($1, $2, $3, 1, $4) RETURNING id",
        sector_id,
        version,
        status,
        '{"kapsam": "t6"}',
    )


async def _brand(db, *, sub_sector_id=None) -> uuid.UUID:
    return await db.fetchval(
        "INSERT INTO social.brands (name, sub_sector_id) VALUES ($1, $2) RETURNING id",
        f"t6-marka-{uuid.uuid4().hex[:8]}",
        sub_sector_id,
    )


def _run_insert_sql(fields: dict) -> str:
    names = list(fields)
    values = ", ".join(
        f"${i + 1}::jsonb" if name in JSONB_RUN_COLUMNS else f"${i + 1}"
        for i, name in enumerate(names)
    )
    return (
        f"INSERT INTO social.sector_package_runs ({', '.join(names)}) "
        f"VALUES ({values}) RETURNING id"
    )


async def _insert_run(db, *, sector_id, **over):
    """Geçerli bir koşu satırı yazar; `over` alanları EZER."""
    fields: dict = {
        "run_id": f"run-{uuid.uuid4().hex[:12]}",
        "sector_id": sector_id,
        "durum": "calisiyor",
        "kosu_turu": "ilk",
    }
    fields.update(over)
    return await db.fetchval(_run_insert_sql(fields), *fields.values())


async def _attempt(db, coro_factory):
    """İşlemi SAVEPOINT içinde dener; hatayı döner, şemayı/veriyi kirletmez."""
    nested = db.transaction()
    await nested.start()
    try:
        await coro_factory()
        return None
    except asyncpg.PostgresError as exc:
        return exc
    finally:
        await nested.rollback()


async def _insert_plan(db, **over):
    fields: dict = {
        "incident_id": f"olay-{uuid.uuid4().hex[:10]}",
        "package_id": over.pop("package_id", None) or uuid.uuid4(),
        "observed_active_version": 3,
        "target_version": 2,
        "evidence_class": "kanit-a",
        "reason": "gerekce",
        "durum": "bekliyor",
    }
    fields.update(over)
    names = list(fields)
    values = ", ".join(f"${i + 1}" for i in range(len(names)))
    return await db.execute(
        f"INSERT INTO social.package_rollback_plans ({', '.join(names)}) "
        f"VALUES ({values})",
        *fields.values(),
    )


# ═══════════════════════════════════════════════════════════════════════════
# 1. KAPALI İLİŞKİ MANİFESTLERİ — üç yeni ilişkinin TAM katalog imzası
# ═══════════════════════════════════════════════════════════════════════════
#
# Seçilmiş özellik listesi DEĞİL: kolon · kısıt · indeks · tetikleyici kümeleri
# KAPALI karşılaştırılır. Eksik olan da FAZLA olan da bulgudur; "şu ekseni
# denetlemiyorsun" varyantı doğamaz.

EXPECTED_036_MANIFEST = {
    "sector_package_runs": {
        "relation": ("r", "p", False, False, False),
        "columns": {
            "id": ("uuid", "NO", "gen_random_uuid()"),
            "run_id": ("text", "NO", None),
            "parent_run_id": ("text", "YES", None),
            "sector_id": ("uuid", "NO", None),
            "durum": ("text", "NO", None),
            "sonuc": ("text", "YES", None),
            "sebep": ("text", "YES", None),
            "engine_version": ("text", "YES", None),
            "engine_config_sha": ("text", "YES", None),
            "policy_report": ("jsonb", "YES", None),
            "barrier_report": ("jsonb", "YES", None),
            "final_candidate": ("jsonb", "YES", None),
            "final_decision_log": ("jsonb", "YES", None),
            "decision_log_sha": ("text", "YES", None),
            "engine_diff": ("jsonb", "YES", None),
            "content_sha": ("text", "YES", None),
            "approval_snapshot": ("jsonb", "YES", None),
            "approval_karar": ("text", "YES", None),
            "approved_at": ("timestamp with time zone", "YES", None),
            "approval_seconds": ("integer", "YES", None),
            "katman1_attestation": ("jsonb", "YES", None),
            "readiness_attestation": ("jsonb", "YES", None),
            "katman2_attestation": ("jsonb", "YES", None),
            "snapshot_sha": ("text", "YES", None),
            "package_id": ("uuid", "YES", None),
            "duzeltilen_run_id": ("uuid", "YES", None),
            "kosu_turu": ("text", "NO", None),
            "kanit_jetonu": ("text", "YES", None),
            "kanit_jetonu_parmakizi": ("text", "YES", None),
            "kanit_jetonu_basildi_at": ("timestamp with time zone", "YES", None),
            "kanit_jetonu_harcandi_at": ("timestamp with time zone", "YES", None),
            "created_at": ("timestamp with time zone", "NO", "now()"),
        },
        "constraints": {
            "sector_package_runs_pkey": "PRIMARY KEY (id)",
            "sector_package_runs_run_id_key": "UNIQUE (run_id)",
            "sector_package_runs_sector_id_fkey": (
                "FOREIGN KEY (sector_id) REFERENCES social.sectors(id)"
            ),
            "sector_package_runs_package_id_fkey": (
                "FOREIGN KEY (package_id) REFERENCES social.sector_packages(id)"
            ),
            "sector_package_runs_durum_check": (
                "CHECK ((durum = ANY (ARRAY['calisiyor'::text, 'tamamlandi'::text, "
                "'tamamlanmadi'::text])))"
            ),
            "sector_package_runs_sonuc_check": (
                "CHECK (((sonuc IS NULL) OR (sonuc = ANY (ARRAY["
                "'activation_eligible'::text, 'no_change'::text, 'blocked'::text]))))"
            ),
            "sector_package_runs_sonuc_yalniz_tamamlandi": (
                "CHECK (((sonuc IS NULL) OR (durum = 'tamamlandi'::text)))"
            ),
            "sector_package_runs_barrier_report_zorunlu": (
                "CHECK (((durum <> 'tamamlandi'::text) OR (barrier_report IS NOT NULL)))"
            ),
            "sector_package_runs_approval_karar_check": (
                "CHECK (((approval_karar IS NULL) OR (approval_karar = ANY (ARRAY["
                "'onay'::text, 'ret'::text]))))"
            ),
            "sector_package_runs_kosu_turu_check": (
                "CHECK ((kosu_turu = ANY (ARRAY['ilk'::text, 'periyodik'::text, "
                "'duzeltme'::text])))"
            ),
            "sector_package_runs_duzeltme_soyagaci": (
                "CHECK (((kosu_turu = 'duzeltme'::text) = (duzeltilen_run_id IS NOT NULL)))"
            ),
            "sector_package_runs_karar_gunlugu_cifti": (
                "CHECK (((final_decision_log IS NULL) = (decision_log_sha IS NULL)))"
            ),
            "sector_package_runs_icerik_gunluksuz_yazilmaz": (
                "CHECK (((final_candidate IS NULL) OR (final_decision_log IS NOT NULL)))"
            ),
            "sector_package_runs_kanit_jetonu_butun": (
                "CHECK (((kanit_jetonu IS NULL) OR ((kanit_jetonu_parmakizi IS NOT NULL) "
                "AND (kanit_jetonu_basildi_at IS NOT NULL))))"
            ),
        },
        "indexes": {
            "sector_package_runs_pkey": (
                "CREATE UNIQUE INDEX sector_package_runs_pkey ON "
                "social.sector_package_runs USING btree (id)"
            ),
            "sector_package_runs_run_id_key": (
                "CREATE UNIQUE INDEX sector_package_runs_run_id_key ON "
                "social.sector_package_runs USING btree (run_id)"
            ),
            "idx_sector_package_runs_sector_created": (
                "CREATE INDEX idx_sector_package_runs_sector_created ON "
                "social.sector_package_runs USING btree (sector_id, created_at DESC)"
            ),
        },
        "triggers": {
            "sector_package_runs_approval_snapshot_immutable": (
                "CREATE TRIGGER sector_package_runs_approval_snapshot_immutable BEFORE "
                "UPDATE ON social.sector_package_runs FOR EACH ROW EXECUTE FUNCTION "
                "social.reject_approval_snapshot_mutation()",
                "O",
            ),
        },
    },
    "package_rollback_plans": {
        "relation": ("r", "p", False, False, False),
        "columns": {
            "incident_id": ("text", "NO", None),
            "package_id": ("uuid", "NO", None),
            "observed_active_version": ("integer", "NO", None),
            "target_version": ("integer", "YES", None),
            "evidence_class": ("text", "NO", None),
            "reason": ("text", "NO", None),
            "durum": ("text", "NO", None),
            "onay_actor": ("text", "YES", None),
            "onaylandi_at": ("timestamp with time zone", "YES", None),
            "onay_kapsam_sha": ("text", "YES", None),
            "kanit_jetonu": ("text", "YES", None),
            "kanit_jetonu_parmakizi": ("text", "YES", None),
            "kanit_jetonu_basildi_at": ("timestamp with time zone", "YES", None),
            "kanit_jetonu_harcandi_at": ("timestamp with time zone", "YES", None),
            "created_at": ("timestamp with time zone", "NO", "now()"),
        },
        "constraints": {
            "package_rollback_plans_incident_id_package_id_key": (
                "UNIQUE (incident_id, package_id)"
            ),
            "package_rollback_plans_durum_check": (
                "CHECK ((durum = ANY (ARRAY['bekliyor'::text, 'tamamlandi'::text, "
                "'hata'::text, 'hedefsiz'::text])))"
            ),
            "package_rollback_plans_hedefsiz_butun": (
                "CHECK (((durum = 'hedefsiz'::text) = (target_version IS NULL)))"
            ),
            "package_rollback_plans_onay_butun": (
                "CHECK ((num_nonnulls(onay_actor, onaylandi_at, onay_kapsam_sha) = ANY "
                "(ARRAY[0, 3])))"
            ),
            "package_rollback_plans_onay_actor_dolu": (
                "CHECK (((onay_actor IS NULL) OR (btrim(onay_actor) <> ''::text)))"
            ),
            "package_rollback_plans_kanit_jetonu_butun": (
                "CHECK (((kanit_jetonu IS NULL) OR ((kanit_jetonu_parmakizi IS NOT NULL) "
                "AND (kanit_jetonu_basildi_at IS NOT NULL))))"
            ),
        },
        "indexes": {
            "package_rollback_plans_incident_id_package_id_key": (
                "CREATE UNIQUE INDEX package_rollback_plans_incident_id_package_id_key "
                "ON social.package_rollback_plans USING btree (incident_id, package_id)"
            ),
        },
        "triggers": {
            "package_rollback_plans_approved_immutable": (
                "CREATE TRIGGER package_rollback_plans_approved_immutable BEFORE UPDATE "
                "ON social.package_rollback_plans FOR EACH ROW EXECUTE FUNCTION "
                "social.reject_approved_rollback_plan_mutation()",
                "O",
            ),
        },
    },
    "brand_sub_sector_history": {
        "relation": ("r", "p", False, False, False),
        "columns": {
            "id": ("uuid", "NO", "gen_random_uuid()"),
            "brand_id": ("uuid", "NO", None),
            "sub_sector_id": ("uuid", "NO", None),
            "assigned_at": ("timestamp with time zone", "NO", "now()"),
            "unassigned_at": ("timestamp with time zone", "YES", None),
        },
        "constraints": {
            "brand_sub_sector_history_pkey": "PRIMARY KEY (id)",
            "brand_sub_sector_history_brand_id_fkey": (
                "FOREIGN KEY (brand_id) REFERENCES social.brands(id) ON DELETE CASCADE"
            ),
            "brand_sub_sector_history_aralik_check": (
                "CHECK (((unassigned_at IS NULL) OR (unassigned_at >= assigned_at)))"
            ),
        },
        "indexes": {
            "brand_sub_sector_history_pkey": (
                "CREATE UNIQUE INDEX brand_sub_sector_history_pkey ON "
                "social.brand_sub_sector_history USING btree (id)"
            ),
            "uq_brand_sub_sector_history_acik": (
                "CREATE UNIQUE INDEX uq_brand_sub_sector_history_acik ON "
                "social.brand_sub_sector_history USING btree (brand_id) WHERE "
                "(unassigned_at IS NULL)"
            ),
            "idx_brand_sub_sector_history_brand": (
                "CREATE INDEX idx_brand_sub_sector_history_brand ON "
                "social.brand_sub_sector_history USING btree (brand_id, assigned_at DESC)"
            ),
        },
        "triggers": {},
    },
}


def _char(value):
    return value.decode() if isinstance(value, (bytes, bytearray)) else value


async def _relation_manifest(db, table: str) -> dict:
    """Bir ilişkinin TAM katalog imzası (032 manifest yardımcısıyla AYNI biçim)."""
    relation = await db.fetchrow(
        "SELECT c.relkind, c.relpersistence, c.relispartition, c.relrowsecurity, "
        "       c.relforcerowsecurity "
        "  FROM pg_class AS c JOIN pg_namespace AS n ON n.oid = c.relnamespace "
        " WHERE n.nspname = 'social' AND c.relname = $1",
        table,
    )
    columns = {
        row["column_name"]: (row["data_type"], row["is_nullable"], row["column_default"])
        for row in await db.fetch(
            "SELECT column_name, data_type, is_nullable, column_default "
            "  FROM information_schema.columns "
            " WHERE table_schema = 'social' AND table_name = $1",
            table,
        )
    }
    constraints = {
        row["conname"]: row["definition"]
        for row in await db.fetch(
            "SELECT c.conname, pg_get_constraintdef(c.oid) AS definition "
            "  FROM pg_constraint AS c JOIN pg_class AS r ON r.oid = c.conrelid "
            "  JOIN pg_namespace AS n ON n.oid = r.relnamespace "
            " WHERE n.nspname = 'social' AND r.relname = $1",
            table,
        )
        # PG17+ `NOT NULL` kısıtlarını satır olarak gösterir, PG16 göstermez —
        # null'lanabilirlik zaten kolon imzasında denetleniyor.
        if not row["definition"].startswith("NOT NULL ")
    }
    indexes = {
        row["indexname"]: row["indexdef"]
        for row in await db.fetch(
            "SELECT indexname, indexdef FROM pg_indexes "
            " WHERE schemaname = 'social' AND tablename = $1",
            table,
        )
    }
    triggers = {
        row["tgname"]: (row["definition"], _char(row["tgenabled"]))
        for row in await db.fetch(
            "SELECT t.tgname, pg_get_triggerdef(t.oid) AS definition, t.tgenabled "
            "  FROM pg_trigger AS t JOIN pg_class AS r ON r.oid = t.tgrelid "
            "  JOIN pg_namespace AS n ON n.oid = r.relnamespace "
            " WHERE n.nspname = 'social' AND r.relname = $1 AND NOT t.tgisinternal",
            table,
        )
    }
    return {
        "relation": (
            _char(relation["relkind"]),
            _char(relation["relpersistence"]),
            relation["relispartition"],
            relation["relrowsecurity"],
            relation["relforcerowsecurity"],
        )
        if relation is not None
        else None,
        "columns": columns,
        "constraints": constraints,
        "indexes": indexes,
        "triggers": triggers,
    }


@pytest.mark.parametrize("table", sorted(EXPECTED_036_MANIFEST))
async def test_runs_table_shape_and_closed_result_enum(db, table):
    """036'nın açtığı her ilişkinin TAM imzası manifestle BİREBİR aynı.

    `sonuc` ve `durum` kapalılığı da buradan okunur: CHECK tanımları manifestin
    içindedir, yani bir değerin sessizce eklenmesi ya da kısıtın düşmesi
    kümeler karşılaştırmasında yakalanır.
    """
    observed = await _relation_manifest(db, table)
    expected = EXPECTED_036_MANIFEST[table]
    assert observed["columns"], f"social.{table} yok — 036 uygulanmamış"
    assert observed["relation"] == expected["relation"], (
        f"social.{table} tablo imzası saptı: {observed['relation']} != "
        f"{expected['relation']}"
    )
    for facet in ("columns", "constraints", "indexes", "triggers"):
        assert observed[facet] == expected[facet], (
            f"social.{table} '{facet}' manifestten SAPTI\n"
            f"yalnız gözlenende: {sorted(set(observed[facet]) - set(expected[facet]))}\n"
            f"yalnız beklenende: {sorted(set(expected[facet]) - set(observed[facet]))}\n"
            f"gözlenen: {sorted(observed[facet].items())}"
        )


async def test_package_rollback_plans_has_no_id_column(db):
    """Kimlik BİLEŞİKTİR — `id` kolonu YOKTUR (arayüz eki, AÇIK-1 dipnotu)."""
    manifest = await _relation_manifest(db, "package_rollback_plans")
    assert "id" not in manifest["columns"], (
        "package_rollback_plans `id` taşıyor — kimliği (incident_id, package_id)"
    )


async def test_barrier_report_column_present(db):
    """K-24: motorun ham değişim sayı/oranları için kolon VAR ve jsonb."""
    manifest = await _relation_manifest(db, "sector_package_runs")
    assert manifest["columns"].get("barrier_report") == ("jsonb", "YES", None)


async def test_snapshot_sha_column_present(db):
    """F18: onayın bağlandığı dondurulmuş görüntünün hash'i kolon olarak VAR."""
    manifest = await _relation_manifest(db, "sector_package_runs")
    assert manifest["columns"].get("snapshot_sha") == ("text", "YES", None)


@pytest.mark.parametrize(
    "column",
    ["katman1_attestation", "readiness_attestation", "katman2_attestation"],
)
async def test_attestation_columns_present_and_nullable(db, column):
    """F18: kapı tasdikleri KANITTIR, boolean değil — jsonb ve NULL'lanabilir.

    NULL'lanabilirlik zorunludur: tasdik koşu BAŞLARKEN yoktur, kapı geçildikçe
    doldurulur. NOT NULL olsaydı koşu satırı hiç açılamazdı.
    """
    manifest = await _relation_manifest(db, "sector_package_runs")
    assert manifest["columns"].get(column) == ("jsonb", "YES", None)


@pytest.mark.parametrize(
    "table", ["sector_package_runs", "package_rollback_plans"]
)
async def test_evidence_token_columns_present_and_nullable(db, table):
    """R8(c): jeton DÖRTLÜSÜ İKİ tabloda da VAR ve dördü de NULL'lanabilir.

    Jetonun TÜRÜ kolonda taşınmaz — türünü taşıdığı TABLO belirler; ikinci bir
    enum AÇILMAZ.
    """
    manifest = await _relation_manifest(db, table)
    assert manifest["columns"].get("kanit_jetonu") == ("text", "YES", None)
    assert manifest["columns"].get("kanit_jetonu_parmakizi") == ("text", "YES", None)
    assert manifest["columns"].get("kanit_jetonu_basildi_at") == (
        "timestamp with time zone",
        "YES",
        None,
    )
    assert manifest["columns"].get("kanit_jetonu_harcandi_at") == (
        "timestamp with time zone",
        "YES",
        None,
    )
    assert f"{table}_kanit_jetonu_butun" in manifest["constraints"]
    assert "jeton_turu" not in manifest["columns"], (
        "jeton TÜRÜ kolonu açılmış — türünü TABLO belirler (R8c)"
    )


# ═══════════════════════════════════════════════════════════════════════════
# 2. ÜRETİLMİŞ CHECK MATRİSLERİ — kapanış sayarak değil YAPIYLA
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.parametrize(
    "durum, sonuc, barrier",
    list(itertools.product(DURUM_VALUES, SONUC_VALUES, (None, '{"degisen": 3}'))),
)
async def test_sonuc_null_unless_completed(db, durum, sonuc, barrier):
    """`durum` × `sonuc` × `barrier_report` ÇAPRAZ ÇARPIMI — 24 hücre.

    Beklenti hücre hücre ELLE yazılmaz, iki bağlayıcı kuraldan TÜRETİLİR:
      * `durum != 'tamamlandi'` iken `sonuc` NULL olmak ZORUNDA.
      * `durum = 'tamamlandi'` iken `barrier_report` NULL OLAMAZ (K-24) —
        sonucun üçünde de.
    Kural değişirse bu matris kendiliğinden yeniden hesaplanır; unutulan
    kombinasyon hücresi doğamaz.
    """
    sector_id = await _sub_sector(db)
    kabul_edilmeli = (sonuc is None or durum == "tamamlandi") and (
        durum != "tamamlandi" or barrier is not None
    )

    error = await _attempt(
        db,
        lambda: _insert_run(
            db, sector_id=sector_id, durum=durum, sonuc=sonuc, barrier_report=barrier
        ),
    )

    if kabul_edilmeli:
        assert error is None, f"meşru hücre reddedildi ({durum}/{sonuc}/{barrier}): {error}"
    else:
        assert isinstance(error, asyncpg.exceptions.CheckViolationError), (
            f"kural dışı hücre KABUL edildi ({durum}/{sonuc}/{barrier}): {error!r}"
        )


@pytest.mark.parametrize(
    "kosu_turu, hedef_var, parent_var",
    list(itertools.product(KOSU_TURU_VALUES, (False, True), (False, True))),
)
async def test_kosu_turu_and_duzeltilen_run_id_check_consistent(
    db, kosu_turu, hedef_var, parent_var
):
    """Düzeltme soyağacı matrisi — 12 hücre, TEK kuraldan türetilmiş.

    Kural: `kosu_turu='duzeltme'` ⇔ `duzeltilen_run_id` dolu.
    `parent_run_id` DİK bir eksendir (yeniden koşum bağı) ve kuralı ETKİLEMEZ —
    karşılıklı dışlama tur 5'te KALDIRILDI. Matris bunu ayrı bir test değil,
    üçüncü bir eksen olarak kanıtlar.
    """
    sector_id = await _sub_sector(db)
    hedef = await _insert_run(db, sector_id=sector_id) if hedef_var else None
    kabul_edilmeli = (kosu_turu == "duzeltme") == hedef_var

    error = await _attempt(
        db,
        lambda: _insert_run(
            db,
            sector_id=sector_id,
            kosu_turu=kosu_turu,
            duzeltilen_run_id=hedef,
            parent_run_id="ana-kosu" if parent_var else None,
        ),
    )

    if kabul_edilmeli:
        assert error is None, (
            f"meşru soyağacı reddedildi ({kosu_turu}/hedef={hedef_var}/"
            f"parent={parent_var}): {error}"
        )
    else:
        assert isinstance(error, asyncpg.exceptions.CheckViolationError), (
            f"tutarsız soyağacı KABUL edildi ({kosu_turu}/hedef={hedef_var}): {error!r}"
        )


async def test_retry_of_correction_may_carry_both_links(db):
    """NEW-2: yarıda kalmış bir DÜZELTMENİN yeniden koşumu İKİ bağı da taşır.

    `parent_run_id` (yeniden koşum) ile `duzeltilen_run_id` (düzeltme hedefi)
    DİK ilişkilerdir. Karşılıklı dışlama, K-82 ile `tamamlanmadi` işaretlenmiş
    bir düzeltmenin kurtarılmasını İMKÂNSIZ kılardı.
    """
    sector_id = await _sub_sector(db)
    hedef = await _insert_run(db, sector_id=sector_id)
    ana = await db.fetchrow(
        "SELECT run_id FROM social.sector_package_runs WHERE id = $1", hedef
    )
    yeniden = await _insert_run(
        db,
        sector_id=sector_id,
        kosu_turu="duzeltme",
        duzeltilen_run_id=hedef,
        parent_run_id=ana["run_id"],
    )
    row = await db.fetchrow(
        "SELECT parent_run_id, duzeltilen_run_id, kosu_turu "
        "  FROM social.sector_package_runs WHERE id = $1",
        yeniden,
    )
    assert row["parent_run_id"] == ana["run_id"]
    assert row["duzeltilen_run_id"] == hedef
    assert row["kosu_turu"] == "duzeltme"


@pytest.mark.parametrize(
    "candidate, log, sha",
    list(itertools.product((None, '{"a": 1}'), (None, '[{"tur": "karar"}]'), (None, "abc"))),
)
async def test_final_decision_log_and_sha_written_atomically(db, candidate, log, sha):
    """F19 matrisi — içerik · karar günlüğü · günlük hash'i, 8 hücre.

    İki kuraldan türetilir:
      * günlük ve hash'i BİRLİKTE dolar, BİRLİKTE boşalır (ikisi ayrı yazılamaz);
      * içerik günlüksüz YAZILAMAZ.
    """
    sector_id = await _sub_sector(db)
    kabul_edilmeli = ((log is None) == (sha is None)) and (
        candidate is None or log is not None
    )

    error = await _attempt(
        db,
        lambda: _insert_run(
            db,
            sector_id=sector_id,
            final_candidate=candidate,
            final_decision_log=log,
            decision_log_sha=sha,
        ),
    )

    if kabul_edilmeli:
        assert error is None, f"meşru hücre reddedildi ({candidate}/{log}/{sha}): {error}"
    else:
        assert isinstance(error, asyncpg.exceptions.CheckViolationError), (
            f"kopuk günlük KABUL edildi ({candidate}/{log}/{sha}): {error!r}"
        )


async def test_final_candidate_written_without_decision_log_rejected(db):
    """Row-D D5: içerik kolonu `final_candidate`tir — günlüksüz yazılamaz.

    (Plan gövdesindeki `test_content_written_without_decision_log_rejected` adı
    şemada BULUNMAYAN bir `content` kolonuna iddia ediyordu; arayüz eki adı ve
    iddiayı düzeltti, sahip DEĞİŞMEDİ.)
    """
    sector_id = await _sub_sector(db)
    error = await _attempt(
        db,
        lambda: _insert_run(
            db, sector_id=sector_id, final_candidate='{"kapsam": "t6"}'
        ),
    )
    assert isinstance(error, asyncpg.exceptions.CheckViolationError), error


@pytest.mark.parametrize(
    "table, jeton, parmak, basildi",
    [
        (table, jeton, parmak, basildi)
        for table in ("sector_package_runs", "package_rollback_plans")
        for jeton, parmak, basildi in itertools.product(
            (None, "a" * 64), (None, "parmak"), (None, "2026-01-01T00:00:00+00")
        )
    ],
)
async def test_evidence_token_check_requires_fingerprint_and_mint_time(
    db, table, jeton, parmak, basildi
):
    """R8(c) jeton bütünlüğü — İKİ tablo × 8 kombinasyon = 16 hücre.

    Kural: jeton doluysa parmak izi VE basım zamanı da dolu olmalıdır.
    Harcanma zamanı kuralın DIŞINDADIR (jeton harcanınca NULL'lanır; o anda
    parmak izi ve basım zamanı satırda KALIR).
    """
    kabul_edilmeli = jeton is None or (parmak is not None and basildi is not None)
    ts = None if basildi is None else datetime.fromisoformat(basildi)

    if table == "sector_package_runs":
        sector_id = await _sub_sector(db)

        async def _write():
            await _insert_run(
                db,
                sector_id=sector_id,
                kanit_jetonu=jeton,
                kanit_jetonu_parmakizi=parmak,
                kanit_jetonu_basildi_at=ts,
            )
    else:

        async def _write():
            await _insert_plan(
                db,
                kanit_jetonu=jeton,
                kanit_jetonu_parmakizi=parmak,
                kanit_jetonu_basildi_at=ts,
            )

    error = await _attempt(db, _write)

    if kabul_edilmeli:
        assert error is None, f"meşru jeton hücresi reddedildi ({table}): {error}"
    else:
        assert isinstance(error, asyncpg.exceptions.CheckViolationError), (
            f"yarım jeton KABUL edildi ({table}/{jeton}/{parmak}/{basildi}): {error!r}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 3. `run_id` kimliği + kardinalite
# ═══════════════════════════════════════════════════════════════════════════


async def test_run_id_unique_across_attempts(db):
    """`run_id` deneme başına KANONİK ve BENZERSİZDİR — ikinci `attempt` uzayı YOK."""
    sector_id = await _sub_sector(db)
    await _insert_run(db, sector_id=sector_id, run_id="kanonik-run")
    error = await _attempt(
        db, lambda: _insert_run(db, sector_id=sector_id, run_id="kanonik-run")
    )
    assert isinstance(error, asyncpg.exceptions.UniqueViolationError), error


async def test_parent_run_id_links_retry(db):
    """Yeniden koşum YENİ `run_id` alır ve `parent_run_id` ile ana koşuya bağlanır."""
    sector_id = await _sub_sector(db)
    await _insert_run(db, sector_id=sector_id, run_id="ana-run")
    yeniden = await _insert_run(
        db, sector_id=sector_id, run_id="yeniden-run", parent_run_id="ana-run"
    )
    row = await db.fetchrow(
        "SELECT run_id, parent_run_id FROM social.sector_package_runs WHERE id = $1",
        yeniden,
    )
    assert row["run_id"] == "yeniden-run"
    assert row["parent_run_id"] == "ana-run"


async def test_package_id_is_not_unique(db):
    """KARDİNALİTE KAPISI (tur 4 düzeltmesi): `package_id` BENZERSİZ DEĞİLDİR.

    `UNIQUE` olsaydı "bir koşu → bir taslak" değil "bir taslak → bir koşu"
    demek olurdu ve K-106'yı İMKÂNSIZ kılardı: düzeltme turu yeni bir koşudur,
    yeni bir `run_id` alır, ama AYNI taslağı güncellemek zorundadır.
    """
    manifest = await _relation_manifest(db, "sector_package_runs")
    for name, definition in manifest["constraints"].items():
        assert not (
            definition.startswith("UNIQUE") and "package_id" in definition
        ), f"`package_id` benzersiz kılınmış: {name} -> {definition}"
    for name, definition in manifest["indexes"].items():
        assert not (
            "UNIQUE" in definition and "(package_id" in definition
        ), f"`package_id` üstünde benzersiz indeks: {name} -> {definition}"

    sector_id = await _sub_sector(db)
    package_id = await _package(db, sector_id)
    await _insert_run(db, sector_id=sector_id, package_id=package_id)
    await _insert_run(db, sector_id=sector_id, package_id=package_id)
    assert (
        await db.fetchval(
            "SELECT count(*) FROM social.sector_package_runs WHERE package_id = $1",
            package_id,
        )
        == 2
    )


async def test_correction_run_may_share_package_id_with_parent(db):
    """K-106: düzeltme koşusu ana koşunun taslağını PAYLAŞABİLİR.

    Ana koşu `package_id`yi tutar; düzeltme turu K-72 gereği YENİ bir koşudur,
    K-83 gereği yeni bir `run_id` alır ve AYNI taslağı hedefler.
    """
    sector_id = await _sub_sector(db)
    package_id = await _package(db, sector_id)
    ana = await _insert_run(db, sector_id=sector_id, package_id=package_id)
    duzeltme = await _insert_run(
        db,
        sector_id=sector_id,
        package_id=package_id,
        kosu_turu="duzeltme",
        duzeltilen_run_id=ana,
    )
    row = await db.fetchrow(
        "SELECT package_id, duzeltilen_run_id FROM social.sector_package_runs "
        "WHERE id = $1",
        duzeltme,
    )
    assert row["package_id"] == package_id
    assert row["duzeltilen_run_id"] == ana


# ═══════════════════════════════════════════════════════════════════════════
# 4. K-98 — `approval_snapshot` DEĞİŞMEZDİR
# ═══════════════════════════════════════════════════════════════════════════


async def test_approval_snapshot_first_write_allowed(db):
    """POZİTİF KONTROL: boşken ilk yazım SERBESTTİR (aşırı kilitleme yok)."""
    sector_id = await _sub_sector(db)
    run = await _insert_run(db, sector_id=sector_id)
    await db.execute(
        "UPDATE social.sector_package_runs SET approval_snapshot = $2::jsonb "
        "WHERE id = $1",
        run,
        '{"donmus": true}',
    )
    stored = await db.fetchval(
        "SELECT approval_snapshot FROM social.sector_package_runs WHERE id = $1", run
    )
    assert json.loads(stored) == {"donmus": True}


@pytest.mark.parametrize(
    "yeni_deger", ['{"donmus": false}', None], ids=["degistir", "sil"]
)
async def test_approval_snapshot_update_rejected_when_set(db, yeni_deger):
    """KAPI: dolu bir anlık görüntü DEĞİŞTİRİLEMEZ ve SİLİNEMEZ.

    İki hücre ayrı ayrı ölçülür: yalnız "başka bir değere çevirme"yi engelleyen
    bir tetikleyici, NULL'a çekerek kanıtı yok etmeye izin verirdi.
    """
    sector_id = await _sub_sector(db)
    run = await _insert_run(db, sector_id=sector_id, approval_snapshot='{"donmus": true}')

    error = await _attempt(
        db,
        lambda: db.execute(
            "UPDATE social.sector_package_runs SET approval_snapshot = $2::jsonb "
            "WHERE id = $1",
            run,
            yeni_deger,
        ),
    )
    assert error is not None, "dolu anlık görüntü değiştirildi"
    assert "approval_snapshot" in str(error), str(error)

    stored = await db.fetchval(
        "SELECT approval_snapshot FROM social.sector_package_runs WHERE id = $1", run
    )
    assert json.loads(stored) == {"donmus": True}


@pytest.mark.parametrize("karar", ["onay", "ret"])
async def test_approval_decision_columns_still_updatable(db, karar):
    """AŞIRI KİLİTLEME YOK: karar · zaman · süre kolonları güncellenebilir.

    Değişmezlik YALNIZ `approval_snapshot` kolonundadır; onay kararının
    kendisi anlık görüntü dondurulduktan SONRA yazılır.
    """
    sector_id = await _sub_sector(db)
    run = await _insert_run(db, sector_id=sector_id, approval_snapshot='{"donmus": true}')
    onay_zamani = datetime.now(timezone.utc)
    await db.execute(
        "UPDATE social.sector_package_runs "
        "   SET approval_karar = $2, approved_at = $3, approval_seconds = $4 "
        " WHERE id = $1",
        run,
        karar,
        onay_zamani,
        42,
    )
    row = await db.fetchrow(
        "SELECT approval_karar, approved_at, approval_seconds "
        "  FROM social.sector_package_runs WHERE id = $1",
        run,
    )
    assert row["approval_karar"] == karar
    assert row["approved_at"] == onay_zamani
    assert row["approval_seconds"] == 42


@pytest.mark.parametrize("karar", [None, "onay", "ret", "belki"])
async def test_approval_karar_is_a_closed_set(db, karar):
    """`approval_karar` kapalıdır: `onay`/`ret` (ya da boş) — üçüncü değer YOK."""
    sector_id = await _sub_sector(db)
    error = await _attempt(
        db, lambda: _insert_run(db, sector_id=sector_id, approval_karar=karar)
    )
    if karar in APPROVAL_KARAR_VALUES:
        assert error is None, f"meşru karar reddedildi ({karar}): {error}"
    else:
        assert isinstance(error, asyncpg.exceptions.CheckViolationError), error


# ═══════════════════════════════════════════════════════════════════════════
# 5. K-145 — geri alma planları
# ═══════════════════════════════════════════════════════════════════════════


async def test_rollback_plan_unique_incident_package(db):
    """Tekrar güvenliğinin VERİ karşılığı: (incident_id, package_id) BENZERSİZ."""
    package_id = uuid.uuid4()
    await _insert_plan(db, incident_id="olay-1", package_id=package_id)
    error = await _attempt(
        db, lambda: _insert_plan(db, incident_id="olay-1", package_id=package_id)
    )
    assert isinstance(error, asyncpg.exceptions.UniqueViolationError), error

    # Aynı olay BAŞKA paket için, ve aynı paket BAŞKA olay için serbesttir.
    await _insert_plan(db, incident_id="olay-1", package_id=uuid.uuid4())
    await _insert_plan(db, incident_id="olay-2", package_id=package_id)


@pytest.mark.parametrize(
    "durum, hedef_var", list(itertools.product(PLAN_DURUM_VALUES, (False, True)))
)
async def test_hedefsiz_requires_null_target_version(db, durum, hedef_var):
    """`hedefsiz` ⇔ `target_version IS NULL` — İKİ YÖNLÜ, 8 hücre.

    Hedefsizlik KALICI bir kayıttır, çalışma zamanı sezgisi DEĞİL: tekrar
    koşumda korunur ve yeniden hedef aranmaz.
    """
    kabul_edilmeli = (durum == "hedefsiz") == (not hedef_var)
    error = await _attempt(
        db,
        lambda: _insert_plan(
            db, durum=durum, target_version=7 if hedef_var else None
        ),
    )
    if kabul_edilmeli:
        assert error is None, f"meşru hücre reddedildi ({durum}/hedef={hedef_var}): {error}"
    else:
        assert isinstance(error, asyncpg.exceptions.CheckViolationError), (
            f"kural dışı hücre KABUL edildi ({durum}/hedef={hedef_var}): {error!r}"
        )


async def test_non_hedefsiz_requires_target_version(db):
    """İkinci yön ayrıca pinlenir: `hedefsiz` OLMAYAN durum hedefsiz KALAMAZ."""
    for durum in ("bekliyor", "tamamlandi", "hata"):
        error = await _attempt(
            db, lambda d=durum: _insert_plan(db, durum=d, target_version=None)
        )
        assert isinstance(error, asyncpg.exceptions.CheckViolationError), (
            f"{durum} hedefsiz yazıldı: {error!r}"
        )


@pytest.mark.parametrize(
    "actor, zaman_var, sha_var",
    list(
        itertools.product(
            (None, "", "   ", "yonetici@otomaix"), (False, True), (False, True)
        )
    ),
)
async def test_rollback_plan_approval_triple_matrix(db, actor, zaman_var, sha_var):
    """AÇIK-1 onay üçlüsü matrisi — 16 hücre, İKİ CHECK'ten türetilmiş.

    * Üçü BİRLİKTE dolar, BİRLİKTE boşalır (`num_nonnulls ∈ {0, 3}`).
    * Boş/yalnız-boşluk kimlik onay SAYILMAZ.
    Tek CHECK yetmezdi: `onay_actor = ''` ölçüldü ki `(actor IS NULL) =
    (onaylandi_at IS NULL)` kuralını GEÇER ve boş kimlikli bir onay üretirdi.
    """
    zaman = datetime.now(timezone.utc) if zaman_var else None
    sha = "kapsam-sha" if sha_var else None
    dolu = sum(x is not None for x in (actor, zaman, sha))
    kabul_edilmeli = dolu in (0, 3) and (actor is None or actor.strip() != "")

    error = await _attempt(
        db,
        lambda: _insert_plan(
            db, onay_actor=actor, onaylandi_at=zaman, onay_kapsam_sha=sha
        ),
    )
    if kabul_edilmeli:
        assert error is None, f"meşru onay hücresi reddedildi ({actor!r}): {error}"
    else:
        assert isinstance(error, asyncpg.exceptions.CheckViolationError), (
            f"kural dışı onay KABUL edildi ({actor!r}/{zaman_var}/{sha_var}): {error!r}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 5b. AYAK (d) — ONAYLANMIŞ geri alma planının kimlik/hedef alanları DEĞİŞMEZ
# ═══════════════════════════════════════════════════════════════════════════
#
# KİLİTLİ ALAN KÜMESİ ELLE YAZILMAZ. Bağlayıcı arayüz ekindeki tetikleyici
# gövdesinden (`NEW.x IS DISTINCT FROM OLD.x` çiftleri) ÜRETİLİR ve
# migration'ın gövdesinden türetilen kümeyle karşılaştırılır. İki kaynak
# ıraksarsa tek tek hücreler değil, KÜMENİN KENDİSİ kırmızı düşer; "şu alan
# unutulmuş" hücresi doğamaz.
#
# AŞIRI KİLİTLEME DE BİR KUSURDUR (ekin bağlayıcı sınırı): yürütücü onaydan
# SONRA `durum` · `reason` · `onay_*` · `kanit_jetonu_*` yazar; yeniden
# mühürleme (reseal) onay üçlüsünü YENİDEN yazar ve bu MEŞRUDUR. Bu yüzden
# izinli kolon kümesi de türetilir: manifestin kolonları EKSİ kilitli alanlar.

ANNEX_PATH = (
    infra.REPO_ROOT
    / "docs"
    / "plans"
    / "2026-08-27-sektor-bilgi-paketi-plan2-arayuz-eki.md"
)

IMMUTABLE_FUNCTION = "social.reject_approved_rollback_plan_mutation"
IMMUTABLE_TRIGGER = "package_rollback_plans_approved_immutable"
IMMUTABLE_MARKER = "kimlik/hedef alanları değiştirilemez"

_NEW_OLD_PAIR = re.compile(r"NEW\.(\w+)\s+IS DISTINCT FROM\s+OLD\.\1\b")

# Kapı, KENDİ KOŞULUYLA bulunur: "onaylı satırda değişmesi yasak alanlar"
# yüklemi `OLD.onay_actor IS NOT NULL AND (...)` ile başlar. Fonksiyonun ADIYLA
# ya da dosyadaki YERİYLE aranmaz — F7 turunda gövdeler `DECLARE`'e taşındı ve
# ada dayalı dilim kapıyı ıskaladı (boş-küme kontrol kolu yakaladı). Kavramdan
# türeyen bu desen taşınmadan etkilenmez ve ekte de aynen çalışır.
_GUARD_CONDITION = re.compile(
    r"OLD\.onay_actor IS NOT NULL AND \((.*?)\)\s*THEN", re.DOTALL
)


def _guard_body(text: str) -> str:
    """Değişmezlik yükleminin KOŞULU — dosyadaki BAŞKA yüklemler hariç.

    Koşul HİÇ YOKSA boş metin döner: eksiklik toplama (collection) hatası değil,
    kümenin BOŞ çıkması olarak raporlanır — kapı o zaman kendi boş-küme kolunda
    düşer ve dosyanın kalan testleri koşmaya devam eder.
    """
    eslesme = _GUARD_CONDITION.search(text)
    return eslesme.group(1) if eslesme else ""


def _locked_fields(text: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(_NEW_OLD_PAIR.findall(_guard_body(text))))


ANNEX_LOCKED_FIELDS = _locked_fields(ANNEX_PATH.read_text(encoding="utf-8"))
MIGRATION_LOCKED_FIELDS = _locked_fields(MIGRATION_036.read_text(encoding="utf-8"))

PLAN_COLUMNS = EXPECTED_036_MANIFEST["package_rollback_plans"]["columns"]

# İzinli kolonlar TÜRETİLİR: tablonun tamamı EKSİ kilitli alanlar.
PERMITTED_COLUMNS = frozenset(PLAN_COLUMNS) - set(ANNEX_LOCKED_FIELDS)

_NOW = datetime.now(timezone.utc)

# Çok kolonlu CHECK'ler bazı kolonları ATOMİK yazmaya zorlar (onay üçlüsü
# `num_nonnulls ∈ {0,3}`, jeton üçlüsü `kanit_jetonu_butun`). Gruplar izinli
# kolon kümesini BÖLER; kapsama kapısı `test_permitted_groups_cover_...`.
PERMITTED_UPDATE_GROUPS = {
    "durum": {"durum": "tamamlandi"},
    "reason": {"reason": "guncellenmis gerekce"},
    "onay_ucluc_yeniden_muhurleme": {
        "onay_actor": "ikinci@otomaix",
        "onaylandi_at": _NOW + timedelta(minutes=5),
        "onay_kapsam_sha": "yeni-kapsam-sha",
    },
    "kanit_jetonu_basimi": {
        "kanit_jetonu": "j" * 64,
        "kanit_jetonu_parmakizi": "p" * 64,
        "kanit_jetonu_basildi_at": _NOW,
    },
    "kanit_jetonu_harcandi_at": {"kanit_jetonu_harcandi_at": _NOW},
    "created_at": {"created_at": _NOW - timedelta(days=1)},
}


def _farkli_deger(kolon: str, mevcut):
    """Kolonun KATALOG TİPİNDEN türetilmiş, mevcuttan FARKLI bir değer.

    Tip kapsanmıyorsa test DÜŞER — "yeni tipte bir kilitli alan sessizce
    denenmedi" hücresi doğamaz.
    """
    tip = PLAN_COLUMNS[kolon][0]
    if tip == "text":
        return f"{mevcut}-degisti"
    if tip == "uuid":
        return uuid.uuid4()
    if tip == "integer":
        return (mevcut or 0) + 1
    raise AssertionError(
        f"kilitli kolon {kolon} tipi {tip!r} için değer üreticisi YOK — "
        "matris o alanı sessizce atlardı"
    )


def _sql_farkli_ifade(kolon: str) -> str:
    """Aynı üretici, SQL tarafı (psql ile koşan mutasyon kolu için)."""
    tip = PLAN_COLUMNS[kolon][0]
    if tip == "text":
        return f"{kolon} = {kolon} || '-degisti'"
    if tip == "uuid":
        return f"{kolon} = gen_random_uuid()"
    if tip == "integer":
        return f"{kolon} = coalesce({kolon}, 0) + 1"
    raise AssertionError(f"{kolon}: {tip!r} tipi için SQL üreticisi YOK")


async def _onayli_plan(db, *, onayli: bool = True):
    """Bir plan satırı yazar ve (incident_id, package_id) anahtarını döner."""
    incident_id = f"olay-{uuid.uuid4().hex[:10]}"
    package_id = uuid.uuid4()
    onay = (
        {
            "onay_actor": "yonetici@otomaix",
            "onaylandi_at": _NOW,
            "onay_kapsam_sha": "kapsam-sha-1",
        }
        if onayli
        else {}
    )
    await _insert_plan(db, incident_id=incident_id, package_id=package_id, **onay)
    return incident_id, package_id


def test_locked_field_set_is_derived_and_non_empty():
    """BOŞ-KÜME KONTROL KOLU + iki kaynak arasında ıraksama kapısı.

    Küme boşsa aşağıdaki matrisler HİÇ hücre koşmadan yeşil görünürdü; bu test
    o sessiz yeşili imkânsız kılar.
    """
    assert ANNEX_LOCKED_FIELDS, (
        "bağlayıcı ekten HİÇ kilitli alan türetilemedi — mutasyon matrisi boş koşardı"
    )
    assert MIGRATION_LOCKED_FIELDS == ANNEX_LOCKED_FIELDS, (
        "migration 036 ile bağlayıcı ek IRAKSADI: "
        f"ek={ANNEX_LOCKED_FIELDS} migration={MIGRATION_LOCKED_FIELDS}"
    )
    bilinmeyen = set(ANNEX_LOCKED_FIELDS) - set(PLAN_COLUMNS)
    assert not bilinmeyen, f"kilitli alan tabloda YOK: {sorted(bilinmeyen)}"


def test_permitted_groups_cover_every_non_locked_column():
    """İZİNLİ kolon kümesi de KAPALI: gruplar tam olarak onu böler.

    Tabloya yarın bir kolon eklenirse (ve kilitlenmezse) bu kapı kırmızı düşer
    — "aşırı kilitleme yok" iddiası o kolon için ölçülmemiş kalamaz.
    """
    kapsanan: set[str] = set()
    for kolonlar in PERMITTED_UPDATE_GROUPS.values():
        cakisma = kapsanan & set(kolonlar)
        assert not cakisma, f"kolon iki grupta birden: {sorted(cakisma)}"
        kapsanan |= set(kolonlar)
    assert kapsanan == PERMITTED_COLUMNS, (
        f"izinli kolon kapsaması eksik/fazla: eksik={sorted(PERMITTED_COLUMNS - kapsanan)} "
        f"fazla={sorted(kapsanan - PERMITTED_COLUMNS)}"
    )


@pytest.mark.parametrize("alan", ANNEX_LOCKED_FIELDS)
async def test_approved_rollback_plan_identity_fields_are_immutable(db, alan):
    """Onaylı satırda kimlik/hedef alanı DEĞİŞTİRİLEMEZ — hücreler ekten üretilir.

    Onay, onayladığı satır kümesine mühürlenir (`onay_kapsam_sha`); mühür
    basıldıktan sonra hedefin değişmesi, "yönetici bunu onayladı" iddiasını
    sessizce başka bir işe taşırdı.
    """
    incident_id, package_id = await _onayli_plan(db)
    mevcut = await db.fetchrow(
        f"SELECT {alan} FROM social.package_rollback_plans "
        "WHERE incident_id = $1 AND package_id = $2",
        incident_id,
        package_id,
    )
    yeni = _farkli_deger(alan, mevcut[alan])

    error = await _attempt(
        db,
        lambda: db.execute(
            f"UPDATE social.package_rollback_plans SET {alan} = $1 "
            "WHERE incident_id = $2 AND package_id = $3",
            yeni,
            incident_id,
            package_id,
        ),
    )
    assert error is not None, f"onaylı satırda {alan} DEĞİŞTİRİLDİ"
    assert IMMUTABLE_MARKER in str(error), f"{alan}: beklenmeyen hata: {error!r}"


@pytest.mark.parametrize("grup", sorted(PERMITTED_UPDATE_GROUPS))
async def test_approved_rollback_plan_stays_updatable_on_operational_columns(db, grup):
    """AŞIRI KİLİTLEME YOK: yürütücünün yazdığı kolonlar onaydan SONRA da açık.

    `onay_*` grubu YENİDEN MÜHÜRLEMEdir (üyelik değişince zorunlu) ve tetikleyici
    onu engellemez — engelleseydi kapsamı değişen bir olay bir daha asla
    onaylanamazdı.
    """
    incident_id, package_id = await _onayli_plan(db)
    kolonlar = PERMITTED_UPDATE_GROUPS[grup]
    atama = ", ".join(f"{ad} = ${i + 1}" for i, ad in enumerate(kolonlar))
    degerler = list(kolonlar.values())

    error = await _attempt(
        db,
        lambda: db.execute(
            f"UPDATE social.package_rollback_plans SET {atama} "
            f"WHERE incident_id = ${len(degerler) + 1} "
            f"AND package_id = ${len(degerler) + 2}",
            *degerler,
            incident_id,
            package_id,
        ),
    )
    assert error is None, f"{grup}: meşru güncelleme REDDEDİLDİ: {error!r}"


@pytest.mark.parametrize("alan", ANNEX_LOCKED_FIELDS)
async def test_unapproved_rollback_plan_identity_fields_are_free(db, alan):
    """`onay_actor IS NULL` satır SERBEST — kilit onayla başlar, satırla değil."""
    incident_id, package_id = await _onayli_plan(db, onayli=False)
    mevcut = await db.fetchrow(
        f"SELECT {alan} FROM social.package_rollback_plans "
        "WHERE incident_id = $1 AND package_id = $2",
        incident_id,
        package_id,
    )
    yeni = _farkli_deger(alan, mevcut[alan])

    error = await _attempt(
        db,
        lambda: db.execute(
            f"UPDATE social.package_rollback_plans SET {alan} = $1 "
            "WHERE incident_id = $2 AND package_id = $3",
            yeni,
            incident_id,
            package_id,
        ),
    )
    assert error is None, f"onaysız satırda {alan} güncellenemedi: {error!r}"


def _doctored_guard_sql(fields) -> str:
    """Kilitli alan kümesi VERİLEN küme olan bir mutant fonksiyon gövdesi."""
    assert fields, "mutant gövde boş koşul üretemez"
    kosullar = "\n        OR ".join(
        f"NEW.{alan} IS DISTINCT FROM OLD.{alan}" for alan in fields
    )
    return (
        f"CREATE OR REPLACE FUNCTION {IMMUTABLE_FUNCTION}() RETURNS trigger AS $mut$ "
        f"BEGIN IF OLD.onay_actor IS NOT NULL AND ({kosullar}) THEN "
        f"RAISE EXCEPTION 'mutant kol: {IMMUTABLE_MARKER}'; END IF; RETURN NEW; END "
        "$mut$ LANGUAGE plpgsql;"
    )


def test_every_locked_field_clause_is_load_bearing(scratch_db_migrated):
    """MUTASYON KOLU: her alanın kolu tek tek SİLİNİR ve kapı ölür mü ölçülür.

    Kanonik fonksiyonla UPDATE `rc≠0` (ret), o alanın kolu silinmiş mutantla
    `rc=0` (kabul). Bir alanın kolu ölçülmemiş olsaydı mutant da reddederdi ve
    bu test kırmızı düşerdi — matrisin kendisi böyle sınanır.
    """
    url = scratch_db_migrated
    assert ANNEX_LOCKED_FIELDS, "kilitli alan kümesi BOŞ — mutasyon hiç koşmazdı"

    kanonik_def = _scalar(
        url, f"SELECT pg_get_functiondef('{IMMUTABLE_FUNCTION}()'::regprocedure)"
    )
    assert IMMUTABLE_FUNCTION in kanonik_def, kanonik_def

    for alan in ANNEX_LOCKED_FIELDS:
        incident_id = f"mutasyon-{alan}"
        _run_sql(
            url,
            "INSERT INTO social.package_rollback_plans "
            "(incident_id, package_id, observed_active_version, target_version, "
            " evidence_class, reason, durum, onay_actor, onaylandi_at, onay_kapsam_sha) "
            f"VALUES ('{incident_id}', gen_random_uuid(), 3, 2, 'kanit-a', 'gerekce', "
            "'bekliyor', 'yonetici@otomaix', now(), 'kapsam-sha-1')",
        )
        guncelle = (
            f"UPDATE social.package_rollback_plans SET {_sql_farkli_ifade(alan)} "
            f"WHERE incident_id = '{incident_id}'"
        )

        kanonik = _psql(url, "-c", guncelle)
        assert kanonik.returncode != 0, (
            f"{alan}: KANONİK tetikleyici onaylı satırın alanını DEĞİŞTİRTTİ"
        )

        _run_sql(
            url,
            _doctored_guard_sql([a for a in ANNEX_LOCKED_FIELDS if a != alan]),
        )
        mutant = _psql(url, "-c", guncelle)
        _run_sql(url, kanonik_def)

        assert mutant.returncode == 0, (
            f"{alan}: kolu SİLİNMİŞ mutant hâlâ reddediyor — bu alanın hücresi "
            f"gerçekte başka bir kolu ölçüyor:\n{mutant.stderr}"
        )


# ═══════════════════════════════════════════════════════════════════════════
# 6. K-09 — `sector_research_artifacts` benzersizliği
# ═══════════════════════════════════════════════════════════════════════════


async def test_artifacts_unique_run_source_kind_rejects_duplicate_upload(db):
    """(run_id, source, kind) üçlüsü BENZERSİZ — tekrar yükleme reddedilir."""

    async def _write(kind: str = "research", source: str = "claude"):
        await db.execute(
            "INSERT INTO social.sector_research_artifacts "
            "    (run_id, sector_slug, kind, source, content_md) "
            "VALUES ($1, $2, $3, $4, $5)",
            "run-k09",
            "alt-sektor",
            kind,
            source,
            "# icerik",
        )

    await _write()
    error = await _attempt(db, _write)
    assert isinstance(error, asyncpg.exceptions.UniqueViolationError), error
    assert K09_CONSTRAINT in str(error), str(error)

    # Üçlünün her bileşeni AYRIŞTIRICIDIR: kind ya da source değişince serbest.
    await _write(kind="review")
    await _write(source="codex")


# ═══════════════════════════════════════════════════════════════════════════
# 7. K-99 — olay kümesi `approval` ve `rejection` ile genişler
# ═══════════════════════════════════════════════════════════════════════════


@pytest.mark.parametrize("event_type", ["approval", "rejection"])
async def test_package_events_accepts_approval_and_rejection(db, event_type):
    """POZİTİF KONTROL: DB CHECK'i iki yeni türü KABUL eder."""
    row_id = await db.fetchval(
        "INSERT INTO social.package_events (event_type, actor) VALUES ($1, $2) "
        "RETURNING id",
        event_type,
        "yonetici@otomaix",
    )
    assert row_id is not None


async def test_package_events_still_rejects_unknown_type(db):
    """KAPALILIK KORUNDU: küme dışı bir tür hâlâ DB'ye giremez."""
    error = await _attempt(
        db,
        lambda: db.execute(
            "INSERT INTO social.package_events (event_type) VALUES ($1)",
            "uydurma_olay",
        ),
    )
    assert isinstance(error, asyncpg.exceptions.CheckViolationError), error


@pytest.mark.parametrize("event_type", ["approval", "rejection"])
async def test_log_package_event_accepts_approval_and_rejection(db, event_type):
    """K-99 ÜRETİCİSİ: yalnız DB CHECK'ini genişletmek YETMEZ.

    ÖLÇÜLDÜ: `log_package_event` bilinmeyen türü SQL'e VARMADAN reddeder
    (`EVENT_TYPES` kapısı). Python üreticisi genişlemezse onay/ret olayı
    yazılamaz — CHECK genişlemiş olsa bile.
    """
    from app.core.database import _init_connection

    await _init_connection(db)
    sector_id = await _sub_sector(db)
    package_id = await _package(db, sector_id)

    event_id = await log_package_event(
        db,
        event_type=event_type,
        sector_id=sector_id,
        package_id=package_id,
        actor="yonetici@otomaix",
        detail={"karar": "onay" if event_type == "approval" else "ret"},
    )
    assert event_id is not None, "onay/ret olayı yazılamadı"
    stored = await db.fetchval(
        "SELECT event_type FROM social.package_events WHERE id = $1", event_id
    )
    assert stored == event_type


async def test_log_package_event_still_rejects_unknown_type(db):
    """Python kapısı KAPALI kalır — genişleme iki değerle sınırlıdır."""
    from app.core.database import _init_connection

    await _init_connection(db)
    sector_id = await _sub_sector(db)
    package_id = await _package(db, sector_id)
    with pytest.raises(PackageEventContractError):
        await log_package_event(
            db,
            event_type="approval_maybe",
            sector_id=sector_id,
            package_id=package_id,
            actor="yonetici@otomaix",
        )


# ─── AKTÖR KAPISI: truthiness DEĞİL, KANONİK doğrulayıcı ────────────────────
#
# ÖLÇÜLEN KUSUR (Codex checkpoint, F2): kapı `bool(actor)` idi ve `"   "`
# (yalnız boşluk) truthy olduğu için GEÇİYORDU; değer KALICI denetim satırına
# olduğu gibi yazılıyordu. `social.package_events.actor` kolonu `TEXT` —
# NOT NULL yok, CHECK yok (033_package_events.sql). Yani tek kapı buydu ve
# kimliğin en çok önemli olduğu yüzeyde (onay/ret) sahipsiz bir denetim satırı
# üretilebiliyordu. `123` gibi `str` OLMAYAN bir kimlik de truthy'dir: eski kapı
# onu geçiriyor, yazım SQL'de düşüyor ve ALTYAPI hatası sayılıp YUTULUYORdu
# (`None` döner) — yani olay sessizce kayboluyordu.
#
# HÜCRELER KAVRAMDAN ÜRETİLİR: "`strip()` sonrası boşalan her kimlik" +
# "`str` olmayan her kimlik". Bulunan örnekten (`"   "`) desen türetilseydi bu
# bir tarama değil, zaten bilinenin tekrar kontrolü olurdu.

_BOSLUK_KARAKTERLERI = (" ", "\t", "\n", "\r", "\v", "\f", "\u00a0", "\u2009")
BLANK_ACTORS = tuple(
    dict.fromkeys(
        ("",) + tuple(k * n for k in _BOSLUK_KARAKTERLERI for n in (1, 3))
    )
)
INVALID_ACTORS = (None,) + BLANK_ACTORS + (123, 0, ("yonetici",))

# Aktör kapısı KAPSAM SINIFINA bağlıdır, tek tek türlere değil: paket-kapsamlı
# her tür (yaşam döngüsü + onay/ret) buradan geçer. Küme modülden TÜRETİLİR.
PACKAGE_SCOPED_EVENTS = tuple(sorted(EVENT_TYPES - BRAND_SCOPED_EVENTS))


def test_actor_gate_is_a_single_canonical_object():
    """İKİ KAPI = İKİ DAVRANIŞ. Kimlik doğrulayıcısı TEK nesnedir.

    Kural kopyalanırsa biri kırpar biri kırpmaz, biri `str` sorar biri sormaz —
    ekin (`AÇIK-1` ayak (b)) kapattığı sınıf tam olarak budur.
    """
    from app.services import sector_package_lifecycle

    assert sector_package_lifecycle._require_actor is package_events_module.require_actor
    assert PACKAGE_SCOPED_EVENTS, "paket-kapsamlı tür kümesi BOŞ — matris hiç koşmazdı"
    assert BLANK_ACTORS, "boş-kimlik hücreleri üretilemedi"


@pytest.mark.parametrize("actor", INVALID_ACTORS, ids=repr)
@pytest.mark.parametrize("event_type", PACKAGE_SCOPED_EVENTS)
async def test_package_scoped_event_rejects_ownerless_actor(db, event_type, actor):
    """Sahipsiz kimlikle KALICI denetim satırı YAZILMAZ — ve HİÇBİR satır yazılmaz.

    İki iddia birden ölçülür: sözleşme hatası çağırana ULAŞIR ve `package_events`
    o paket için BOŞ kalır (yarım iz, izin hiç olmamasından daha kötüdür).
    """
    from app.core.database import _init_connection

    await _init_connection(db)
    sector_id = await _sub_sector(db)
    package_id = await _package(db, sector_id)

    with pytest.raises(PackageEventContractError):
        await log_package_event(
            db,
            event_type=event_type,
            sector_id=sector_id,
            package_id=package_id,
            actor=actor,
        )

    yazilan = await db.fetchval(
        "SELECT count(*) FROM social.package_events WHERE package_id = $1", package_id
    )
    assert yazilan == 0, f"{event_type}/{actor!r}: sahipsiz olay YAZILDI ({yazilan} satır)"


# Marka-kapsamlı dalda kimlik OPSİYONELDİR (olay otomatiktir, insan işlemi
# değil) — ama VERİLDİĞİNDE aynı kapıdan geçer. KISMİ FİX YOK: "kapı yalnız
# yaşam döngüsü dalında" demek, aynı kolonun aynı çöpü kabul ettiği ikinci bir
# yolu açık bırakmak olurdu. `None` hücresi bu matriste YOKTUR: orada `None`
# MEŞRUDUR ve ayrı bir pozitif kontrol testiyle ölçülür.
BRAND_SCOPED_INVALID_ACTORS = tuple(a for a in INVALID_ACTORS if a is not None)


@pytest.mark.parametrize("actor", BRAND_SCOPED_INVALID_ACTORS, ids=repr)
@pytest.mark.parametrize("event_type", sorted(BRAND_SCOPED_EVENTS))
async def test_brand_scoped_event_rejects_a_given_but_blank_actor(db, event_type, actor):
    """Kimlik kapısı KAPSAM SINIFINDAN BAĞIMSIZDIR — ve satır yazılmaz."""
    from app.core.database import _init_connection

    await _init_connection(db)
    brand_id = await _brand(db)

    with pytest.raises(PackageEventContractError):
        await log_package_event(
            db, event_type=event_type, brand_id=brand_id, actor=actor
        )

    yazilan = await db.fetchval(
        "SELECT count(*) FROM social.package_events WHERE brand_id = $1", brand_id
    )
    assert yazilan == 0, f"{event_type}/{actor!r}: sahipsiz olay YAZILDI"


@pytest.mark.parametrize("event_type", sorted(BRAND_SCOPED_EVENTS))
async def test_brand_scoped_event_still_accepts_a_missing_actor(db, event_type):
    """POZİTİF KONTROL: marka-kapsamlı olay OTOMATİKTİR, kimliği olmayabilir.

    Bu ayak olmadan yukarıdaki matris, `actor`ı zorunlu kılan bir kapıyla da
    yeşil olurdu — ve depodaki gerçek çağrı yerleri (`posts.py`,
    `sector_packages.py`) kimlik GEÇİRMEZ; kapı onları kırardı.
    """
    from app.core.database import _init_connection

    await _init_connection(db)
    brand_id = await _brand(db)

    event_id = await log_package_event(db, event_type=event_type, brand_id=brand_id)
    assert event_id is not None
    stored = await db.fetchval(
        "SELECT actor FROM social.package_events WHERE id = $1", event_id
    )
    assert stored is None


@pytest.mark.parametrize("event_type", sorted(APPROVAL_EVENTS))
async def test_package_scoped_event_stores_the_normalized_actor(db, event_type):
    """POZİTİF KONTROL: kimlik KIRPILMIŞ hâliyle yazılır.

    Kapı yalnız reddetseydi `" yonetici@otomaix "` kabul edilir ve denetim izine
    iki farklı görünen AYNI kimlik yazılırdı; kanonik doğrulayıcı kırpılmış
    değeri DÖNER ve yazılan odur.
    """
    from app.core.database import _init_connection

    await _init_connection(db)
    sector_id = await _sub_sector(db)
    package_id = await _package(db, sector_id)

    event_id = await log_package_event(
        db,
        event_type=event_type,
        sector_id=sector_id,
        package_id=package_id,
        actor="  yonetici@otomaix \n",
    )
    assert event_id is not None
    stored = await db.fetchval(
        "SELECT actor FROM social.package_events WHERE id = $1", event_id
    )
    assert stored == "yonetici@otomaix", f"kimlik normalize edilmeden yazıldı: {stored!r}"


@pytest.mark.parametrize(
    "event_type, from_version, to_version",
    [
        (t, f, v)
        for t in sorted(APPROVAL_EVENTS)
        for f in (None, 999)
        for v in (None, -5)
    ],
)
async def test_approval_events_reject_invented_versions(
    db, event_type, from_version, to_version
):
    """Onay/ret SÜRÜM GEÇİŞİ TAŞIMAZ — iki alan da NULL olmak ZORUNDA.

    ÖLÇÜLEN KUSUR (fix turu 1, I2): `_validate_version_shape` kapalı bir
    `if activation / elif rollback / elif deactivation` zinciriydi ve `else`
    TAŞIMIYORDU. `EVENT_TYPES`e giren iki yeni tür hiçbir dala uymuyor, sessizce
    geçiyordu; `from_version=999, to_version=-5` taşıyan KALICI bir denetim
    satırı yazılabiliyordu. Aynı çağrı `activation` ile gerçek aktif sürüme
    karşı TAM EŞLEŞME ile reddediliyordu — yani asimetri denetim izindeydi.

    Matris 2 tür × 2 `from_version` × 2 `to_version` = 8 hücre; beklenti tek
    kuraldan türetilir.
    """
    from app.core.database import _init_connection

    await _init_connection(db)
    sector_id = await _sub_sector(db)
    package_id = await _package(db, sector_id)
    kabul_edilmeli = from_version is None and to_version is None

    async def _yaz():
        return await log_package_event(
            db,
            event_type=event_type,
            sector_id=sector_id,
            package_id=package_id,
            actor="yonetici@otomaix",
            from_version=from_version,
            to_version=to_version,
        )

    if kabul_edilmeli:
        assert await _yaz() is not None
        return

    with pytest.raises(PackageEventContractError, match="sürüm"):
        await _yaz()
    assert (
        await db.fetchval(
            "SELECT count(*) FROM social.package_events WHERE package_id = $1",
            package_id,
        )
        == 0
    ), "reddedilen olay satır bıraktı"


@pytest.mark.parametrize(
    "event_type, from_version, to_version",
    [
        (t, f, v)
        for t in sorted(BRAND_SCOPED_EVENTS)
        for f in (None, 999)
        for v in (None, -5)
    ],
)
async def test_brand_scoped_events_reject_invented_versions(
    db, event_type, from_version, to_version
):
    """SINIFIN İKİNCİ YARISI (fix turu 2, N2) — 6 tür × 2 × 2 = 24 hücre.

    ÖLÇÜLEN KUSUR: `log_package_event`in marka-kapsamlı dalı
    `_validate_version_shape`i HİÇ çağırmıyordu, dolayısıyla I2'de kapatılan
    tehlike altı tür üzerinden AYNEN erişilebilir kalmıştı. Canlı ölçüm:

        stamp_missing, from_version=999, to_version=-5  → KABUL
        yazılan satır: {'event_type': 'stamp_missing',
                        'from_version': 999, 'to_version': -5}

    Marka-kapsamlı türler sürüm GEÇİŞİ taşımaz — sürüm bilgisi `detail`e yazılır
    (`stamp_stale_at_persist` → `detail={"stamped_version": ...}`). Bu ölçüldü:
    depodaki HİÇBİR çağrı yeri marka-kapsamlı bir türle sürüm kolonu geçirmiyor,
    yani kapı hiçbir çağıranı kırmıyor.
    """
    from app.core.database import _init_connection

    await _init_connection(db)
    brand_id = await _brand(db)
    kabul_edilmeli = from_version is None and to_version is None

    async def _yaz():
        return await log_package_event(
            db,
            event_type=event_type,
            brand_id=brand_id,
            from_version=from_version,
            to_version=to_version,
        )

    if kabul_edilmeli:
        assert await _yaz() is not None
        return

    with pytest.raises(PackageEventContractError, match="sürüm"):
        await _yaz()
    assert (
        await db.fetchval(
            "SELECT count(*) FROM social.package_events WHERE brand_id = $1", brand_id
        )
        == 0
    ), "reddedilen olay satır bıraktı"


def test_every_event_type_declares_a_version_contract():
    """SINIF KAPANIŞI: `EVENT_TYPES`in HER üyesi sürüm sözleşmesini BEYAN EDER.

    Fix turu 2 (N2) düzeltmesi: önceki hâl eşlemeyi `EVENT_TYPES` EKSİ
    `BRAND_SCOPED_EVENTS` ile karşılaştırıyordu, yani sınıfın YARISI kapalıydı
    ve "kapanış sayarak değil YAPIYLA" iddiası yarı doğruydu. Yarım sınıf,
    kapalı sınıf DEĞİLDİR. Muafiyet KALDIRILDI; kıyas artık kümenin TAMAMIdır.
    """
    assert set(EVENT_VERSION_CONTRACT) == set(EVENT_TYPES), (
        f"beyan edilmemiş: {sorted(set(EVENT_TYPES) - set(EVENT_VERSION_CONTRACT))}\n"
        f"ölü beyan: {sorted(set(EVENT_VERSION_CONTRACT) - set(EVENT_TYPES))}"
    )
    assert set(EVENT_VERSION_CONTRACT.values()) <= {"gecis", "surumsuz"}
    # Marka-kapsamlı altı tür sürüm TAŞIMAZ: sürüm bilgisi `detail`e yazılır
    # (`stamp_stale_at_persist` → `detail={"stamped_version": ...}`), sürüm
    # kolonlarına DEĞİL. Kolonlar yaşam döngüsü geçişlerinin dilidir.
    for event_type in BRAND_SCOPED_EVENTS:
        assert EVENT_VERSION_CONTRACT[event_type] == "surumsuz", event_type


def test_version_contract_totality_gate_rejects_an_undeclared_type():
    """Bütünlük kapısının KENDİSİ ölçülür — pozitif kontrol + iki negatif kol.

    İmza İKİ argümanlıdır (fix turu 2): `brand_scoped` parametresi KALDIRILDI.
    Muafiyeti parametre olarak taşımak, onu yanlışlıkla geri vermeyi mümkün
    kılardı; bugün kapıya bir ALT KÜME geçirilemez.
    """
    assert_version_contract_is_wellformed(EVENT_TYPES, EVENT_VERSION_CONTRACT)

    with pytest.raises(PackageEventContractError, match="beyan"):
        assert_version_contract_is_wellformed(
            EVENT_TYPES | {"uydurma_gecis"}, EVENT_VERSION_CONTRACT
        )
    with pytest.raises(PackageEventContractError, match="beyan"):
        assert_version_contract_is_wellformed(
            EVENT_TYPES - {"activation"}, EVENT_VERSION_CONTRACT
        )


# ─── Import kapısının TÜRÜ ve MESAJI (fix turu 2, N1) ──────────────────────
#
# ÖLÇÜLEN KUSUR: `assert_version_contract_is_wellformed(...)` modül gövdesinde
# `class PackageEventContractError` TANIMINDAN ÖNCE koşuyordu (122 < 150). Yük
# taşıyan yarısı sağlamdı — import yine düşüyordu, yani kapı fail-closed'dı —
# ama operatörün gördüğü şey `NameError: name 'PackageEventContractError' is
# not defined` oluyordu. Yani NEYİN beyan edilmediğini söyleyen cümle
# (`eksik: [...] / olu beyan: [...]`) import anında HİÇ görünmüyordu ve
# `except PackageEventContractError` ile sarmak da işe yaramazdı.
#
# Bu yüzden test "import düştü mü" diye SORMAZ: fırlatılan TÜRÜ ve MESAJI ölçer.


# ─── `gecis` kolunun KENDİ zinciri de kapanır (fix turu 3, R1) ─────────────
#
# Dağıtım seviyesi fix turu 1-2'de kapandı: her tür `gecis` ya da `surumsuz`
# beyan eder, bütünlük import anında zorlanır. Ama `gecis` KOLUNUN İÇİ hâlâ
# `if activation / elif rollback / elif deactivation` idi ve sonunda `else`
# YOKTU. Bugün var olan on bir tür için ATEŞLENEMEZ (üç `gecis` türünün üçü de
# dala sahip; sayım: `test_contract_values_are_a_closed_pair` ile aynı kaynaktan)
# — yani canlı bir tehlike değil, AÇIK BIRAKILMIŞ BİR EKSENDİ.
#
# Neden yine de kapatılıyor: I2'nin gereği "yarın eklenecek bir tür doğrulamadan
# KAÇAMASIN"dı. Bu seviyede kaçabiliyordu. Ölçüldü: dördüncü bir `gecis` türü
# beyan edilip `from_version=999, to_version=-5` ile çağrıldığında Python kapısı
# KABUL ediyor, yazım SQL'e ulaşıyor ve yalnız veritabanının kendi kapalı tür
# CHECK'i durduruyordu — o CHECK ise gerçek bir yeni türle BİRLİKTE
# genişletileceği için dayanıklı bir ikinci hat DEĞİLDİR.


def test_import_time_gate_rejects_a_mistyped_contract_value(tmp_path):
    """Sözleşme DEĞERİ de kapalı bir kümedir — yazım hatası import'ta DURur.

    ÖLÇÜLEN KUSUR (fix turu 4, Minor): bütünlük kapısı yalnız ANAHTARLARI
    denetliyordu. `"approval": "surumsuzz"` gibi bir yazım hatası import'tan
    GEÇİYOR, sonra `_validate_version_shape`in `else` koluna düşüyor ve o kolun
    mesajı türün `gecis` BEYAN EDİLDİĞİNİ söylüyordu — beyan edilmemişti.
    Etkisi fail-closed ve gürültülüydü, ama mesaj kodun durumu hakkında YANLIŞ
    bir şey söylüyordu; bu görevin dört kez ürettiği sınıfın ta kendisi.

    Kapı ANAHTAR + DEĞER kümesini birlikte denetler; adı da bunu söylesin diye
    `..._is_total` → `..._is_wellformed` oldu.
    """
    with pytest.raises(Exception) as excinfo:
        _load_doctored_package_events(
            tmp_path, ('    "approval": "surumsuz",\n', '    "approval": "surumsuzz",\n')
        )
    hata = excinfo.value
    assert type(hata).__name__ == "PackageEventContractError", (
        f"yazım hatası import'tan GEÇTİ ya da yanlış tür fırlattı: "
        f"{type(hata).__name__}: {hata}"
    )
    assert "surumsuzz" in str(hata), str(hata)
    assert "approval" in str(hata), str(hata)


# ─── SAYI İDDİALARI KAPI HÂLİNE GETİRİLİR (fix turu 5) ─────────────────────
#
# Bu görev beş turda YEDİ kez aynı kusuru üretti: gönderilen bir artefakta,
# koşulmamış bir sayı yazmak. Dördü de disiplinle düzeltildi, ama disiplin
# tekrarlanabilir bir kapı DEĞİLDİR. Aşağıdaki iki test, sayıları ELLE
# denetlenen prose'dan ÇALIŞTIRILAN sözleşmeye çevirir:
#
#   * docstring'lerde yazan `N hücre` iddiası ↔ GERÇEKTEN toplanan parametre
#     sayısı (11 iddia, tek kapı);
#   * gerekçe bloğundaki ÖLÇÜM-SATIRI ↔ CANLI modülün sözleşme sayıları.
#
# Bundan sonra bir sayı bayatlarsa test düşer; kimsenin fark etmesi gerekmez.


def _parametrize_hucre_sayisi(func) -> int:
    """Bir testin ÜRETTİĞİ hücre sayısı — yığılmış `parametrize`lerin ÇARPIMI."""
    toplam = 1
    for mark in getattr(func, "pytestmark", []):
        if mark.name == "parametrize":
            toplam *= len(mark.args[1])
    return toplam


def test_docstring_cell_counts_match_the_collected_matrix():
    """Docstring'de yazan `N hücre`, GERÇEKTEN üretilen hücre sayısına eşit.

    Sayı artık iddia değil ÖLÇÜM: kaynağı `parametrize` argüman listelerinin
    kendisidir. Bir eksen eklenip docstring güncellenmezse — ya da tersi — bu
    test düşer.

    Kapsam otomatiktir: bu modüldeki `N hücre` yazan HER test. Liste elle
    tutulmaz, yoksa kapının kendisi bayatlardı.
    """
    import re as _re
    import sys as _sys

    modul = _sys.modules[__name__]
    denetlenen = {}
    for ad in dir(modul):
        if not ad.startswith("test_"):
            continue
        func = getattr(modul, ad)
        doc = getattr(func, "__doc__", None) or ""
        eslesme = _re.findall(r"(\d+)\s*hücre", doc)
        if not eslesme:
            continue
        denetlenen[ad] = (int(eslesme[-1]), _parametrize_hucre_sayisi(func))

    assert denetlenen, "hiç `N hücre` iddiası bulunamadı — kapı boşa koşuyor"
    sapan = {a: v for a, v in denetlenen.items() if v[0] != v[1]}
    assert not sapan, (
        "docstring hücre sayısı GERÇEK matrisle uyuşmuyor "
        "(iddia, gerçek): " + repr(sapan)
    )


def test_rationale_measurement_line_matches_the_live_module():
    """`package_events.py`nin ÖLÇÜM-SATIRI canlı modülle birebir aynı.

    Gerekçe bloğu üç sayıya dayanıyor (toplam · `gecis` · `surumsuz`) ve o
    sayılar iki kez sessizce bayatladı. Satır artık makine-okunur ve burada
    CANLI modüle karşı ölçülüyor; prose de o satırdan okuyor.
    """
    import re as _re
    from collections import Counter as _Counter

    kaynak = pathlib.Path(package_events_module.__file__).read_text()
    satir = _re.search(
        r"ÖLÇÜM-SATIRI: toplam=(\d+) gecis=(\d+) surumsuz=(\d+)", kaynak
    )
    assert satir, "ÖLÇÜM-SATIRI bulunamadı — gerekçe bloğunun dayanağı yok"
    yazilan = tuple(int(g) for g in satir.groups())

    dagilim = _Counter(EVENT_VERSION_CONTRACT.values())
    olculen = (
        len(EVENT_VERSION_CONTRACT),
        dagilim.get("gecis", 0),
        dagilim.get("surumsuz", 0),
    )
    assert yazilan == olculen, (
        f"ÖLÇÜM-SATIRI bayat: yazılan {yazilan}, ölçülen {olculen}"
    )
    # Çapraz kontrol: üç kapsam sınıfının toplamı da aynı sayıyı vermeli.
    assert olculen[0] == len(BRAND_SCOPED_EVENTS) + len(LIFECYCLE_EVENTS) + len(
        APPROVAL_EVENTS
    ), "kapsam sınıflarının toplamı sözleşme sayısıyla uyuşmuyor"


def test_contract_values_are_a_closed_pair():
    """İki değer TEK yerde tanımlıdır ve eşlemenin tamamı o kümededir."""
    assert VERSION_CONTRACT_VALUES == {"gecis", "surumsuz"}
    assert set(EVENT_VERSION_CONTRACT.values()) <= VERSION_CONTRACT_VALUES


async def test_unknown_contract_value_message_does_not_claim_gecis(db, monkeypatch):
    """`else` kolunun mesajı BEYAN EDİLMEMİŞ bir şeyi İDDİA ETMEZ.

    Import kapısı yazım hatasının VAR OLMASINI engeller; bu test kapının
    atlandığı yolu (çalışma zamanında eşlemenin değiştirilmesi) ölçer ve
    mesajın GERÇEKTEN OKUDUĞU değeri bildirdiğini doğrular. İki kapı iki ayrı
    yarıyı kapatır: biri kusurun doğmasını, diğeri mesajın yalan söylemesini.
    """
    from app.core.database import _init_connection

    await _init_connection(db)
    sector_id = await _sub_sector(db)
    package_id = await _package(db, sector_id)
    monkeypatch.setattr(
        package_events_module,
        "EVENT_VERSION_CONTRACT",
        {**EVENT_VERSION_CONTRACT, "approval": "surumsuzz"},
    )

    with pytest.raises(PackageEventContractError) as excinfo:
        await log_package_event(
            db,
            event_type="approval",
            sector_id=sector_id,
            package_id=package_id,
            actor="yonetici@otomaix",
        )

    mesaj = str(excinfo.value)
    assert "'surumsuzz'" in mesaj, f"mesaj OKUDUĞU değeri bildirmiyor: {mesaj}"
    assert "'gecis'" not in mesaj, (
        f"mesaj yapılmamış bir `gecis` beyanını İDDİA EDİYOR: {mesaj}"
    )


async def test_a_fourth_gecis_type_is_rejected_by_the_python_gate(db, tmp_path):
    """Dördüncü bir `gecis` türü SQL'e VARMADAN reddedilir.

    Bozuk kopya iki dokunuş taşır — tür `LIFECYCLE_EVENTS`e eklenir VE
    sözleşmede `gecis` olarak beyan edilir — çünkü yalnız biri yapılsaydı test
    YANLIŞ SEBEPLE yeşil olurdu: eksik beyan import kapısına, beyansız küme ise
    `EVENT_TYPES` kapısına takılırdı. İkisi de kapatılınca geriye TEK ölçülen
    şey kalır: `gecis` kolunun sonundaki `else`.

    HANGİ KAPININ durdurduğu da ölçülür: Python kapısı reddederse sözleşme
    hatası ÇAĞIRANA ULAŞIR; SQL reddederse `log_package_event` altyapı hatasını
    yutar ve `None` döner. `pytest.raises` ikisini birbirinden tam olarak ayırır.
    """
    from app.core.database import _init_connection

    bozuk = _load_doctored_package_events(
        tmp_path,
        (
            'LIFECYCLE_EVENTS = frozenset({"activation", "rollback", "deactivation"})',
            'LIFECYCLE_EVENTS = frozenset({"activation", "rollback", "deactivation", '
            '"gecis_dorduncu"})',
        ),
        ('    "deactivation": "gecis",\n', '    "deactivation": "gecis",\n    "gecis_dorduncu": "gecis",\n'),
    )
    assert bozuk.EVENT_VERSION_CONTRACT["gecis_dorduncu"] == "gecis"

    await _init_connection(db)
    sector_id = await _sub_sector(db)
    package_id = await _package(db, sector_id)

    with pytest.raises(Exception) as excinfo:
        await bozuk.log_package_event(
            db,
            event_type="gecis_dorduncu",
            sector_id=sector_id,
            package_id=package_id,
            actor="yonetici@otomaix",
            from_version=999,
            to_version=-5,
        )

    hata = excinfo.value
    assert type(hata).__name__ == "PackageEventContractError", (
        f"beyansız dal SQL'e ULAŞTI — durduran Python kapısı değil: "
        f"{type(hata).__name__}: {hata}"
    )
    assert "gecis_dorduncu" in str(hata), str(hata)
    assert (
        await db.fetchval(
            "SELECT count(*) FROM social.package_events WHERE package_id = $1",
            package_id,
        )
        == 0
    ), "reddedilen olay satır bıraktı"


def _load_doctored_package_events(tmp_path, *replacements: tuple[str, str]):
    """`package_events.py`nin bozulmuş bir KOPYASINI import eder ve döner.

    Birden çok düzenleme alır: bir türü kümeye eklemek ve onu sözleşmede beyan
    etmek AYRI iki dokunuştur; ikisini birden yapamayan bir yardımcı, "yeni tür"
    senaryosunu hiç kuramazdı.

    Kopya kendi `PackageEventContractError` sınıfını tanımlar (ayrı modül, ayrı
    sınıf nesnesi), o yüzden tür kimliği `isinstance` ile DEĞİL ADIYLA ölçülür —
    ve ayrıca `ValueError` mirasının korunduğu doğrulanır.
    """
    src = pathlib.Path(package_events_module.__file__).read_text()
    for old, new in replacements:
        assert src.count(old) == 1, f"bozma deseni {src.count(old)} kez bulundu"
        src = src.replace(old, new, 1)
    target = tmp_path / "package_events_bozuk.py"
    target.write_text(src)
    spec = importlib.util.spec_from_file_location("package_events_bozuk", target)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # import kapısı varsa BURADA patlar
    return module


@pytest.mark.parametrize(
    "bozulma, old, new",
    [
        (
            "eksik_beyan",
            '    "rejection": "surumsuz",\n',
            "",
        ),
        (
            "yeni_tur_beyansiz",
            'APPROVAL_EVENTS = frozenset({"approval", "rejection"})',
            'APPROVAL_EVENTS = frozenset({"approval", "rejection", "uydurma_onay"})',
        ),
        (
            "olu_beyan",
            'APPROVAL_EVENTS = frozenset({"approval", "rejection"})',
            'APPROVAL_EVENTS = frozenset({"approval"})',
        ),
    ],
)
def test_import_time_totality_gate_raises_the_declared_error(
    tmp_path, bozulma, old, new
):
    """Import kapısı SÖZLEŞME HATASI fırlatır — `NameError` DEĞİL.

    3 hücre, kümelerin ıraksayabileceği üç yol: beyan silindi · küme büyüdü,
    beyan büyümedi · küme küçüldü, beyan küçülmedi. Üçünde de operatörün
    gördüğü metin NEYİN eksik/ölü olduğunu ADIYLA söylemek zorunda.
    """
    with pytest.raises(Exception) as excinfo:
        _load_doctored_package_events(tmp_path, (old, new))

    hata = excinfo.value
    assert type(hata).__name__ == "PackageEventContractError", (
        f"{bozulma}: import kapısı YANLIŞ TÜR fırlattı — "
        f"{type(hata).__name__}: {hata}"
    )
    assert isinstance(hata, ValueError), "sözleşme hatası ValueError olmalı"
    assert "beyan" in str(hata), str(hata)
    assert ("rejection" in str(hata)) or ("uydurma_onay" in str(hata)), (
        f"{bozulma}: mesaj NEYİN beyan edilmediğini söylemiyor: {hata}"
    )


async def test_undeclared_package_scoped_event_is_rejected_at_runtime(db, monkeypatch):
    """Çalışma zamanı arka durağı: beyansız tür SQL'e VARMADAN reddedilir.

    Import kapısı yapısal kapanıştır; bu test onun ÇALIŞMA ZAMANI eşini ölçer
    (kümeler süreç içinde değiştirilirse kapı yine kapalı kalır). İkisi olmadan
    `else`siz zincirin açtığı sınıf tam kapanmazdı.
    """
    from app.core.database import _init_connection

    await _init_connection(db)
    sector_id = await _sub_sector(db)
    package_id = await _package(db, sector_id)
    monkeypatch.setattr(
        package_events_module, "EVENT_TYPES", EVENT_TYPES | {"uydurma_gecis"}
    )
    with pytest.raises(PackageEventContractError, match="beyan"):
        await log_package_event(
            db,
            event_type="uydurma_gecis",
            sector_id=sector_id,
            package_id=package_id,
            actor="yonetici@otomaix",
        )


def test_event_sets_stay_disjoint_and_closed():
    """Üç kapsam sınıfı ÖRTÜŞMEZ ve birleşimleri `EVENT_TYPES`e EŞİTTİR."""
    assert APPROVAL_EVENTS == {"approval", "rejection"}
    assert EVENT_TYPES == BRAND_SCOPED_EVENTS | LIFECYCLE_EVENTS | APPROVAL_EVENTS
    assert not (BRAND_SCOPED_EVENTS & APPROVAL_EVENTS)
    assert not (LIFECYCLE_EVENTS & APPROVAL_EVENTS)


async def test_db_check_and_python_gate_agree(db):
    """İKİ KAPI TEK KÜMEDİR: DB CHECK'i ile `EVENT_TYPES` birebir aynı.

    Kümeler ayrı ayrı bakımlanırsa ıraksarlar: ya Python'un yazabildiği bir tür
    DB'de reddedilir (akış düşer), ya DB'nin kabul ettiği bir tür Python'dan
    hiç geçemez (ölü değer). Karşılaştırma katalogtan ÜRETİLİR.
    """
    definition = await db.fetchval(
        "SELECT pg_get_constraintdef(c.oid) FROM pg_constraint c "
        " WHERE c.conrelid = 'social.package_events'::regclass "
        "   AND c.conname = 'package_events_type_check'"
    )
    assert definition, "package_events_type_check YOK"
    db_values = set(__import__("re").findall(r"'([a-z_]+)'::text", definition))
    assert db_values == set(EVENT_TYPES), (
        f"DB CHECK'i ile EVENT_TYPES ıraksadı\n"
        f"yalnız DB'de: {sorted(db_values - set(EVENT_TYPES))}\n"
        f"yalnız Python'da: {sorted(set(EVENT_TYPES) - db_values)}"
    )


# ═══════════════════════════════════════════════════════════════════════════
# 8. K-45 — atama geçmişi TETİKLEYİCİSİ (üretici ZORUNLU)
# ═══════════════════════════════════════════════════════════════════════════


async def _intervals(db, brand_id):
    return await db.fetch(
        "SELECT sub_sector_id, assigned_at, unassigned_at "
        "  FROM social.brand_sub_sector_history WHERE brand_id = $1 "
        " ORDER BY assigned_at, sub_sector_id",
        brand_id,
    )


async def test_history_trigger_opens_and_closes_interval_on_assignment_change(db):
    """Atama değişimi AYNI İŞLEMDE açık aralığı kapatır ve yenisini açar."""
    ilk = await _sub_sector(db)
    ikinci = await _sub_sector(db)
    brand_id = await _brand(db, sub_sector_id=ilk)

    rows = await _intervals(db, brand_id)
    assert len(rows) == 1, rows
    assert rows[0]["sub_sector_id"] == ilk
    assert rows[0]["unassigned_at"] is None, "ilk aralık AÇIK olmalı"

    await db.execute(
        "UPDATE social.brands SET sub_sector_id = $2 WHERE id = $1", brand_id, ikinci
    )
    rows = await _intervals(db, brand_id)
    assert len(rows) == 2, rows
    kapali = [r for r in rows if r["unassigned_at"] is not None]
    acik = [r for r in rows if r["unassigned_at"] is None]
    assert len(kapali) == 1 and kapali[0]["sub_sector_id"] == ilk
    assert len(acik) == 1 and acik[0]["sub_sector_id"] == ikinci

    # Atama kaldırılınca aralık KAPANIR, yenisi AÇILMAZ.
    await db.execute(
        "UPDATE social.brands SET sub_sector_id = NULL WHERE id = $1", brand_id
    )
    rows = await _intervals(db, brand_id)
    assert len(rows) == 2, rows
    assert all(r["unassigned_at"] is not None for r in rows), rows


@pytest.mark.parametrize(
    "path_label",
    [
        "tek_satir_update",
        "coklu_satir_update",
        "insert_atamali",
        "insert_atamasiz_sonra_update",
        "diger_kolonla_birlikte_update",
        "ayni_degere_update",
        "servis_katmani",
    ],
)
async def test_history_trigger_fires_regardless_of_writing_code_path(db, path_label):
    """Atama yolu hangi koddan geçerse geçsin geçmiş YAZILIR.

    Yollar ÇEŞİTLENDİRİLİR çünkü tetikleyicinin varlık sebebi budur: K-45
    kanıtı tek bir servis fonksiyonuna bağlanamaz (Task 16 onu maruziyet
    kanıtı olarak tüketecek). Son hücre üretimin KENDİ yazma yolunu koşar.
    `ayni_degere_update` NEGATİF kontroldür: değişmeyen atama yeni aralık
    ÜRETMEZ, yoksa "maruziyet" gürültüye boğulurdu.
    """
    hedef = await _sub_sector(db)
    diger = await _sub_sector(db)

    if path_label == "tek_satir_update":
        brand_id = await _brand(db)
        await db.execute(
            "UPDATE social.brands SET sub_sector_id = $2 WHERE id = $1", brand_id, hedef
        )
        beklenen_acik = hedef
        beklenen_sayi = 1
    elif path_label == "coklu_satir_update":
        brand_id = await _brand(db)
        komsu = await _brand(db)
        await db.execute(
            "UPDATE social.brands SET sub_sector_id = $1 WHERE id = ANY($2::uuid[])",
            hedef,
            [brand_id, komsu],
        )
        assert len(await _intervals(db, komsu)) == 1, "toplu yazımda komşu satır atlandı"
        beklenen_acik = hedef
        beklenen_sayi = 1
    elif path_label == "insert_atamali":
        brand_id = await _brand(db, sub_sector_id=hedef)
        beklenen_acik = hedef
        beklenen_sayi = 1
    elif path_label == "insert_atamasiz_sonra_update":
        brand_id = await _brand(db)
        assert await _intervals(db, brand_id) == [], "atamasız INSERT aralık açtı"
        await db.execute(
            "UPDATE social.brands SET sub_sector_id = $2 WHERE id = $1", brand_id, hedef
        )
        beklenen_acik = hedef
        beklenen_sayi = 1
    elif path_label == "diger_kolonla_birlikte_update":
        brand_id = await _brand(db, sub_sector_id=diger)
        await db.execute(
            "UPDATE social.brands SET name = $2, sub_sector_id = $3 WHERE id = $1",
            brand_id,
            "yeni-ad",
            hedef,
        )
        beklenen_acik = hedef
        beklenen_sayi = 2
    elif path_label == "ayni_degere_update":
        brand_id = await _brand(db, sub_sector_id=hedef)
        await db.execute(
            "UPDATE social.brands SET sub_sector_id = $2, name = $3 WHERE id = $1",
            brand_id,
            hedef,
            "ad-degisti",
        )
        beklenen_acik = hedef
        beklenen_sayi = 1
    else:  # servis_katmani
        from app.core.database import _init_connection

        await _init_connection(db)
        brand_id = await _brand(db)
        await db.execute(
            "UPDATE social.brands SET sub_sector_id = $2, updated_at = now() "
            " WHERE id = $1",
            brand_id,
            hedef,
        )
        beklenen_acik = hedef
        beklenen_sayi = 1

    rows = await _intervals(db, brand_id)
    assert len(rows) == beklenen_sayi, f"{path_label}: {rows}"
    acik = [r for r in rows if r["unassigned_at"] is None]
    assert len(acik) == 1, f"{path_label}: tam olarak BİR açık aralık olmalı — {rows}"
    assert acik[0]["sub_sector_id"] == beklenen_acik, f"{path_label}: {rows}"


# ─── K-45 üreticisi SESSİZCE DURAMAZ (fix turu 1, I1) ──────────────────────
#
# ÖLÇÜLEN KUSUR: üretici kolonu `to_jsonb(NEW) ->> 'sub_sector_id'` ile
# okuyordu ve bu okuma kolon YOKSA ya da YENİDEN ADLANDIRILMIŞSA `NULL` döner.
# `yeni IS NOT DISTINCT FROM eski` o durumda DOĞRU olur, tetikleyici `RETURN
# NULL` ile çıkar ve K-45 üreticisi SESSİZCE yazmayı bırakır — marka yazımları
# `rc=0` ile geçmeye devam ederken maruziyet kanıtı birikmez. Ölçüm (taze
# scratch, tüm migration'lar):
#   * kolon `sub_sector_id_v2`ye yeniden adlandırıldı → marka INSERT `rc=0`,
#     geçmiş satırı 1'de KALDI (yeni satır YOK).
#   * kolon düşürüldü → marka INSERT `rc=0`, geçmiş satırı yine 1.
# Sessizlik, tam da K-45'in var olma sebebinin karşıtıdır.


def _brands_write_probe(kolon: str | None) -> str:
    """Alt sektör kur, sonra markayı YAZ — kolon adı hücreye göre değişir."""
    atama = "" if kolon is None else f", {kolon}"
    deger = "" if kolon is None else ", (SELECT id FROM social.sectors WHERE slug = 't6fix-alt')"
    return f"""
        INSERT INTO social.brands (name{atama}) VALUES ('t6fix-marka'{deger});
    """


_HISTORY_SETUP = """
    INSERT INTO social.sectors (slug, display_name) VALUES ('t6fix-kok', 't6fix-kok');
    INSERT INTO social.sectors (slug, display_name, parent_sector_id)
         SELECT 't6fix-alt', 't6fix-alt', id
           FROM social.sectors WHERE slug = 't6fix-kok';
"""


@pytest.mark.parametrize(
    "bozulma, bozan_sql, yazma_kolonu",
    [
        ("saglikli", "", "sub_sector_id"),
        (
            "yeniden_adlandirildi",
            "ALTER TABLE social.brands RENAME COLUMN sub_sector_id TO sub_sector_id_v2;",
            "sub_sector_id_v2",
        ),
        (
            "dusuruldu",
            "ALTER TABLE social.brands DROP COLUMN sub_sector_id;",
            None,
        ),
    ],
)
def test_history_producer_fails_loudly_when_its_column_is_missing(
    scratch_db_migrated, bozulma, bozan_sql, yazma_kolonu
):
    """Dayandığı kolon yoksa üretici SESSİZ KALMAZ, DURur.

    Matris 3 hücre: sağlıklı (pozitif kontrol — yazım geçer VE satır doğar),
    kolon yeniden adlandırıldı, kolon düşürüldü. Beklenti hücre hücre elle
    yazılmaz, TEK kuraldan türetilir: kolon yerinde mi?

    Sağlıklı hücre olmadan bu matris "her koşulda düşen" bir tetikleyiciyle de
    yeşil olurdu ve hiçbir şey ölçülmemiş olurdu.
    """
    url = scratch_db_migrated
    _run_sql(url, _HISTORY_SETUP)
    if bozan_sql:
        _run_sql(url, bozan_sql)

    result = _psql(url, "-c", _brands_write_probe(yazma_kolonu))
    gecmis = _scalar(url, "SELECT count(*) FROM social.brand_sub_sector_history")

    if bozulma == "saglikli":
        assert result.returncode == 0, f"sağlıklı yol DURDU:\n{result.stderr}"
        assert gecmis == "1", f"sağlıklı yolda aralık AÇILMADI (gecmis={gecmis})"
        return

    assert result.returncode != 0, (
        f"{bozulma}: kolon yokken marka yazımı SESSİZCE geçti — üretici durdu "
        f"ama kimse duymadı:\n{result.stdout}"
    )
    assert HISTORY_PRODUCER_MARKER in result.stderr, result.stderr
    assert gecmis == "0", f"{bozulma}: reddedilen yazım satır bıraktı ({gecmis})"


def test_column_dependency_is_created_only_by_a_trigger_column_list(scratch_db_migrated):
    """DÜZELTİLEN İDDİA — artık AKIL YÜRÜTME değil, ÖLÇÜM.

    Önceki yazım "`NEW.sub_sector_id` gövdede kolona KATALOG BAĞIMLILIĞI kurar"
    diyordu ve bunu `ÖLÇÜLDÜ` diye etiketliyordu. YANLIŞTI: plpgsql gövdesi geç
    bağlanır, katalog bağımlılığı YARATMAZ. İddianın yalnız İKİNCİ yarısı
    doğrudur — bağımlılığı TETİKLEYİCİNİN KOLON LİSTESİ (`UPDATE OF <kolon>`)
    kurar.

    Bu test o bilgiyi çalıştırılabilir hâle getirir: aynı veritabanında iki kol,
    ikisi de ölçülür.
    """
    url = scratch_db_migrated

    # (a) Kolon listeli bir tetikleyici VARKEN kolon düşürülemez.
    _run_sql(
        url,
        "CREATE TRIGGER t6fix_kolon_listeli AFTER UPDATE OF sub_sector_id "
        "ON social.brands FOR EACH ROW "
        "EXECUTE FUNCTION social.track_brand_sub_sector_history();",
    )
    engelli = _psql(url, "-c", "ALTER TABLE social.brands DROP COLUMN sub_sector_id")
    assert engelli.returncode != 0, "kolon listeli tetikleyici düşürmeyi ENGELLEMEDİ"
    assert "depends on column" in engelli.stderr, engelli.stderr

    # (b) 036'nın KENDİ tetikleyicisi (kolon listesi YOK) düşürmeyi engellemez.
    _run_sql(url, "DROP TRIGGER t6fix_kolon_listeli ON social.brands;")
    serbest = _psql(url, "-c", "ALTER TABLE social.brands DROP COLUMN sub_sector_id")
    assert serbest.returncode == 0, (
        "036'nın tetikleyicisi kolona katalog bağımlılığı kuruyor:\n"
        f"{serbest.stderr}"
    )


async def test_history_has_no_backfill(db):
    """Geri doldurma YOKTUR: 036 ÖNCESİ atamalar retroaktif aralık üretmez.

    Bilinmeyen geçmiş "bakım tamamlandı" ÜRETMEZ — geçmişsiz marka bildirim
    almaz. Ölçüm: tetikleyiciyi atlatan bir yazım (tetikleyici oturum için
    devre dışı) sonrası geçmiş BOŞ kalır.
    """
    hedef = await _sub_sector(db)
    brand_id = await _brand(db)
    await db.execute("SET LOCAL session_replication_role = 'replica'")
    await db.execute(
        "UPDATE social.brands SET sub_sector_id = $2 WHERE id = $1", brand_id, hedef
    )
    await db.execute("SET LOCAL session_replication_role = 'origin'")
    assert await _intervals(db, brand_id) == [], "geri doldurma yapılmış"


async def test_open_interval_is_unique_per_brand(db):
    """Marka başına EN FAZLA BİR açık aralık — kısmi benzersiz indeks."""
    hedef = await _sub_sector(db)
    diger = await _sub_sector(db)
    brand_id = await _brand(db, sub_sector_id=hedef)
    error = await _attempt(
        db,
        lambda: db.execute(
            "INSERT INTO social.brand_sub_sector_history (brand_id, sub_sector_id) "
            "VALUES ($1, $2)",
            brand_id,
            diger,
        ),
    )
    assert isinstance(error, asyncpg.exceptions.UniqueViolationError), error


async def test_history_follows_brand_delete(db):
    """F18 marka silme sözleşmesi: markaya ait iz markayla BİRLİKTE gider."""
    hedef = await _sub_sector(db)
    brand_id = await _brand(db, sub_sector_id=hedef)
    assert len(await _intervals(db, brand_id)) == 1
    await db.execute("DELETE FROM social.brands WHERE id = $1", brand_id)
    assert (
        await db.fetchval(
            "SELECT count(*) FROM social.brand_sub_sector_history WHERE brand_id = $1",
            brand_id,
        )
        == 0
    )


# ═══════════════════════════════════════════════════════════════════════════
# 9. F20 — geri alma VERİ VARKEN fail-closed durur
# ═══════════════════════════════════════════════════════════════════════════
#
# Hücreler ÜRETİLİR: Plan 2 verisinin her sınıfı × "reddetti mi" + "hiçbir şeye
# dokunmadı mı" (bayt-bayt). Tek tek örnek seçilmez.

PLAN2_DATA_CASES = {
    "kosu_satiri": """
        INSERT INTO social.sectors (slug, display_name)
             VALUES ('t6-kok', 't6-kok');
        INSERT INTO social.sectors (slug, display_name, parent_sector_id)
             SELECT 't6-alt', 't6-alt', id FROM social.sectors WHERE slug = 't6-kok';
        INSERT INTO social.sector_package_runs (run_id, sector_id, durum, kosu_turu)
             SELECT 'pilot-run', id, 'calisiyor', 'ilk'
               FROM social.sectors WHERE slug = 't6-alt';
    """,
    "onay_olayi": """
        INSERT INTO social.package_events (event_type, actor)
             VALUES ('approval', 'yonetici@otomaix');
    """,
    "ret_olayi": """
        INSERT INTO social.package_events (event_type, actor)
             VALUES ('rejection', 'yonetici@otomaix');
    """,
    "gecmis_araligi": """
        INSERT INTO social.sectors (slug, display_name)
             VALUES ('t6h-kok', 't6h-kok');
        INSERT INTO social.sectors (slug, display_name, parent_sector_id)
             SELECT 't6h-alt', 't6h-alt', id FROM social.sectors WHERE slug = 't6h-kok';
        INSERT INTO social.brands (name, sub_sector_id)
             SELECT 't6-marka', id FROM social.sectors WHERE slug = 't6h-alt';
    """,
    "geri_alma_plani": """
        INSERT INTO social.package_rollback_plans
             (incident_id, package_id, observed_active_version, target_version,
              evidence_class, reason, durum)
             VALUES ('olay-1', gen_random_uuid(), 3, 2, 'kanit-a', 'gerekce',
                     'bekliyor');
    """,
}


@pytest.mark.parametrize("case", sorted(PLAN2_DATA_CASES))
def test_036_down_refuses_when_plan2_data_exists(scratch_db_migrated, case):
    """Plan 2 verisi VARSA geri alma `rc≠0` ile DURur ve HİÇBİR şeye dokunmaz.

    Matris ÜRETİLMİŞTİR: veri sınıfı başına bir hücre. Her hücrede iki iddia
    birden ölçülür — ret geldi mi, VE kalıcı durum bayt-bayt önceki hâline eşit
    mi. `test_036_down_refuses_when_run_rows_exist` /
    `..._approval_events_exist` / `..._history_intervals_exist` /
    `..._leaves_everything_untouched_on_refusal` bu matrisin hücreleridir.
    """
    url = scratch_db_migrated
    _run_sql(url, PLAN2_DATA_CASES[case])

    schema_before = _schema_fingerprint(url)
    data_before = _data_fingerprint(url)

    result = _apply_down(url, DOWN_036)

    assert result.returncode != 0, f"{case}: veri varken geri alma GEÇTİ:\n{result.stdout}"
    assert REFUSAL_MARKER_036 in result.stderr, result.stderr
    assert _schema_fingerprint(url) == schema_before, f"{case}: ŞEMA değişti"
    assert _data_fingerprint(url) == data_before, f"{case}: VERİ değişti"


def test_036_down_refuses_when_run_rows_exist(scratch_db_migrated):
    """F20 — koşu satırı varken ret (matris hücresinin ADIYLA pinlenmesi)."""
    url = scratch_db_migrated
    _run_sql(url, PLAN2_DATA_CASES["kosu_satiri"])
    result = _apply_down(url, DOWN_036)
    assert result.returncode != 0, result.stdout
    assert "sector_package_runs" in result.stderr, result.stderr


def test_036_down_refuses_when_approval_events_exist(scratch_db_migrated):
    """F20 — onay/ret olayı varken ret; satırları SİLMEK denetim izini yok ederdi."""
    url = scratch_db_migrated
    _run_sql(url, PLAN2_DATA_CASES["onay_olayi"])
    result = _apply_down(url, DOWN_036)
    assert result.returncode != 0, result.stdout
    assert "package_events" in result.stderr, result.stderr


def test_036_down_refuses_when_history_intervals_exist(scratch_db_migrated):
    """F20 — atama geçmişi aralığı varken ret (maruziyet kanıtı korunur)."""
    url = scratch_db_migrated
    _run_sql(url, PLAN2_DATA_CASES["gecmis_araligi"])
    result = _apply_down(url, DOWN_036)
    assert result.returncode != 0, result.stdout
    assert "brand_sub_sector_history" in result.stderr, result.stderr


def test_036_down_leaves_everything_untouched_on_refusal(scratch_db_migrated):
    """Ret BAYT-BAYT izsizdir — şema da veri de değişmez."""
    url = scratch_db_migrated
    _run_sql(url, PLAN2_DATA_CASES["kosu_satiri"])
    schema_before = _schema_fingerprint(url)
    data_before = _data_fingerprint(url)

    result = _apply_down(url, DOWN_036)

    assert result.returncode != 0
    assert _schema_fingerprint(url) == schema_before
    assert _data_fingerprint(url) == data_before


def test_036_down_succeeds_on_empty_plan2_data(scratch_db_migrated):
    """POZİTİF KONTROL: Plan 2 verisi yokken geri alma 036'nın açtığını KALDIRIR.

    Bu ayak olmadan yukarıdaki ret testleri "her koşulda reddeden" bir script'le
    de yeşil olurdu — hiçbir şey ölçülmemiş olurdu.
    """
    url = scratch_db_migrated
    result = _apply_down(url, DOWN_036)
    assert result.returncode == 0, f"boş veride geri alma DURDU:\n{result.stderr}"

    for table in ("sector_package_runs", "package_rollback_plans",
                  "brand_sub_sector_history"):
        assert _scalar(url, f"SELECT to_regclass('social.{table}') IS NULL") == "t", (
            f"{table} hâlâ duruyor"
        )
    assert (
        _scalar(
            url,
            "SELECT count(*) FROM pg_constraint WHERE conrelid = "
            f"'social.sector_research_artifacts'::regclass AND conname = '{K09_CONSTRAINT}'",
        )
        == "0"
    ), "K-09 kısıtı hâlâ duruyor"
    assert (
        _scalar(
            url,
            "SELECT pg_get_constraintdef(oid) FROM pg_constraint "
            "WHERE conrelid = 'social.package_events'::regclass "
            "AND conname = 'package_events_type_check'",
        ).count("approval")
        == 0
    ), "olay CHECK'i daraltılmadı"
    assert (
        _scalar(
            url,
            "SELECT count(*) FROM pg_trigger WHERE NOT tgisinternal "
            "AND tgname = 'brands_sub_sector_history'",
        )
        == "0"
    ), "geçmiş tetikleyicisi hâlâ duruyor"


# ═══════════════════════════════════════════════════════════════════════════
# 9b. KİLİT SIRASI ÜRETİCİ BAĞIMLILIK YÖNÜNÜ İZLER
# ═══════════════════════════════════════════════════════════════════════════
#
# ÖLÇÜLEN KUSUR (Codex checkpoint, F3): `036_down.sql` preflight'ı kilitleri AD
# SIRASINA göre alıyordu — `brand_sub_sector_history` ÖNCE, `brands` SONRA.
# Normal yazım yolu TERS yöndedir: `brands` güncellenir, tetikleyici geçmiş
# tablosuna yazar. Ters sıra bir deadlock penceresidir; PostgreSQL birini abort
# eder (tutarlılık için güvenli) ama ACİL geri almanın koşabilirliği belirsizleşir.
#
# KAPANIŞ CANLI ÇOK-OTURUMLU DEADLOCK TESTİYLE DEĞİL, YAPISAL REGRESYONLA
# kurulur: kilit sırası ile 036'nın tetikleyici bağımlılık yönü ÇELİŞİRSE bu
# test düşer. İki taraf da DOSYADAN TÜRETİLİR — ne sıra ne kenar elle yazılır.

_LOCK_RE = re.compile(r"LOCK TABLE (social\.\w+) IN ACCESS EXCLUSIVE MODE")
_TRIGGER_RE = re.compile(
    r"CREATE TRIGGER\s+(\w+)\s+(?:BEFORE|AFTER|INSTEAD OF)\b[^;$]*?"
    r"\bON\s+(social\.\w+)\b[^;$]*?EXECUTE FUNCTION\s+(social\.\w+)\(\)",
    re.DOTALL,
)
# Gövdeler F7 turunda kanonik SABİTLERE taşındı (tek kaynak: kapı da yazım da
# aynı metni okur). Bağ, kimlik kapısının kendi VALUES listesinden türetilir:
#   ('social.<fonksiyon>', <sabit_adi>)
# ve sabit `<ad> CONSTANT TEXT := $tag$...$tag$;` olarak çözülür. Ada göre
# `CREATE FUNCTION` metni aramak artık HİÇBİR gövde bulmaz — dosya o metni
# `format()` şablonunda tutuyor.
_CONST_RE = re.compile(r"(\w+) CONSTANT TEXT := \$(\w+)\$(.*?)\$\2\$;", re.DOTALL)
_FN_BINDING_RE = re.compile(r"\('(social\.\w+)',\s*(\w+)\)")
_WRITE_RE = re.compile(r"(?:INSERT INTO|UPDATE|DELETE FROM)\s+(social\.\w+)")


def _function_bodies(text: str) -> dict:
    sabitler = {ad: govde for ad, _tag, govde in _CONST_RE.findall(text)}
    return {
        fonksiyon: sabitler[degisken]
        for fonksiyon, degisken in _FN_BINDING_RE.findall(text)
        if degisken in sabitler
    }


def _lock_order(text: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys(_LOCK_RE.findall(text)))


def _trigger_write_edges(text: str) -> tuple[tuple[str, str], ...]:
    """(ÜRETİCİ tablo, tetikleyicinin YAZDIĞI tablo) kenarları — katalog yönü."""
    bodies = _function_bodies(text)
    edges: list[tuple[str, str]] = []
    for _, uretici, fonksiyon in _TRIGGER_RE.findall(text):
        for yazilan in _WRITE_RE.findall(bodies.get(fonksiyon, "")):
            if yazilan != uretici:
                edges.append((uretici, yazilan))
    return tuple(dict.fromkeys(edges))


DOWN_036_LOCK_ORDER = _lock_order(DOWN_036.read_text(encoding="utf-8"))
TRIGGER_WRITE_EDGES = _trigger_write_edges(MIGRATION_036.read_text(encoding="utf-8"))


def _lock_order_violations(lock_order, edges):
    """Üreticisi, yazdığı tablodan SONRA kilitlenen kenarlar."""
    sira = {ad: i for i, ad in enumerate(lock_order)}
    return sorted(
        (uretici, yazilan)
        for uretici, yazilan in edges
        if uretici in sira and yazilan in sira and sira[uretici] > sira[yazilan]
    )


def test_down_lock_order_follows_the_producer_direction():
    """Kilit sırası ⟂ tetikleyici yönü — ikisi de DOSYADAN türetilir.

    BOŞ-KÜME KONTROL KOLU: kenar üretilemezse kapı hiçbir şey ölçmeden yeşil
    olurdu; ilk iki iddia o sessiz yeşili imkânsız kılar. MUTASYON KOLU: sıra
    ters çevrildiğinde kapı KIRMIZI düşmek ZORUNDA — düşmüyorsa denetimin
    kendisi ölüdür.
    """
    assert TRIGGER_WRITE_EDGES, (
        "036'dan HİÇ tetikleyici-yazım kenarı türetilemedi — kapı boş kümede "
        "yeşil düşerdi"
    )
    assert DOWN_036_LOCK_ORDER, "036_down.sql'den kilit sırası okunamadı"

    assert _lock_order_violations(DOWN_036_LOCK_ORDER, TRIGGER_WRITE_EDGES) == [], (
        "kilit sırası ÜRETİCİ yönüne ters: normal yazım yolu üreticiyi ÖNCE, "
        "yazdığı tabloyu SONRA kilitler; geri alma bunu tersine çevirirse "
        f"deadlock penceresi açılır (sıra={DOWN_036_LOCK_ORDER})"
    )
    assert _lock_order_violations(tuple(reversed(DOWN_036_LOCK_ORDER)), TRIGGER_WRITE_EDGES), (
        "TERS sıra da ihlal ÜRETMİYOR — denetim ölü"
    )
    assert _lock_order_violations(tuple(reversed(DOWN_036_LOCK_ORDER)), ()) == [], (
        "kenar kümesi boşken ihlal uydurulmuş"
    )


def test_every_locked_table_of_the_down_script_is_locked_exactly_once():
    """Sıra SABİT ve TEKİL: aynı tabloyu iki kez kilitlemek sırayı belirsizleştirir."""
    ham = _LOCK_RE.findall(DOWN_036.read_text(encoding="utf-8"))
    assert ham, "kilit ifadesi bulunamadı"
    assert len(ham) == len(set(ham)), f"tablo birden çok kez kilitleniyor: {ham}"


# ═══════════════════════════════════════════════════════════════════════════
# 9c. AD ≠ SAHİPLİK — aynı adı taşıyan YABANCI fonksiyon/tetikleyici EZİLMEZ
# ═══════════════════════════════════════════════════════════════════════════
#
# ÖLÇÜLEN KUSUR (Codex kapanış-doğrulama turu, F7): 036 kalıcı DDL'inde üç
# fonksiyon/tetikleyici çifti KOŞULSUZ yazılıyordu (`CREATE OR REPLACE
# FUNCTION` + `DROP TRIGGER IF EXISTS` + `CREATE TRIGGER`), yani nesnenin ADI
# var diye SAHİPLİK varsayılıyordu. Kayan bir şemada aynı adlı YABANCI bir
# fonksiyon sessizce EZİLİR; ona bağlı başka bir tetikleyici, fonksiyon
# kimliği (oid) korunduğu için ANINDA bizim gövdemizi çalıştırmaya başlar.
# Kapalı manifest bunu YAKALAYAMAZ: manifest ezme İŞLEMİNDEN SONRAKİ
# (kanonik görünen) durumu okur.
#
# Bu, dosyanın KENDİ standardının açık kalmış varyantıydı — kısıtlar için
# KAPI 2 / KAPI 3 tam bu disiplini uyguluyor (`pg_get_constraintdef` +
# `contype` + `convalidated`). Sınıf kapatıldı, varyant değil: ÜÇ çiftin ÜÇÜ.
#
# ÇİFTLER ELLE YAZILMAZ: kanonik tetikleyici tanımlarından TÜRETİLİR — tek bir
# metin hem tetikleyici adını, hem tabloyu, hem fonksiyonu taşır.

_TRIGGER_TRIPLE_RE = re.compile(
    r"CREATE TRIGGER (\w+)\s+(?:BEFORE|AFTER|INSTEAD OF)[\s\S]*?"
    r"\bON (social\.\w+)[\s\S]*?EXECUTE FUNCTION (social\.\w+)\(\)"
)

IDENTITY_TRIPLES = tuple(
    dict.fromkeys(_TRIGGER_TRIPLE_RE.findall(MIGRATION_036.read_text(encoding="utf-8")))
)
IDENTITY_IDS = [trg for trg, _, _ in IDENTITY_TRIPLES]

IDENTITY_MARKER = "KANONIK OLMAYAN"

# Mutasyon kolunun kestiği sınırlar — dosyadaki bölüm başlıkları.
IDENTITY_GATE_BEGIN = "-- ── KAPI 4 — FONKSİYON VE TETİKLEYİCİ KİMLİĞİ"
IDENTITY_GATE_END = "-- ═══ BURADAN SONRASI KALICI"

# Yabancı gövdenin parmak izi: ezilip ezilmediği BU metinle ölçülür.
FOREIGN_BODY_MARKER = "YABANCI GOVDE 036 TESTI"


def _foreign_function_sql(fonksiyon: str) -> str:
    return (
        f"CREATE OR REPLACE FUNCTION {fonksiyon}() RETURNS trigger AS $yabanci$ "
        f"BEGIN RAISE EXCEPTION '{FOREIGN_BODY_MARKER}'; END $yabanci$ LANGUAGE plpgsql;"
    )


def _foreign_trigger_sql(tetikleyici: str, tablo: str) -> str:
    """Adı BİZİM, tanımı BAŞKA bir tetikleyici (farklı olay, farklı fonksiyon)."""
    return (
        "CREATE OR REPLACE FUNCTION social.yabanci_036_test_fn() RETURNS trigger AS "
        "$yt$ BEGIN RETURN NEW; END $yt$ LANGUAGE plpgsql;"
        f"DROP TRIGGER IF EXISTS {tetikleyici} ON {tablo};"
        f"CREATE TRIGGER {tetikleyici} BEFORE DELETE ON {tablo} "
        "FOR EACH ROW EXECUTE FUNCTION social.yabanci_036_test_fn();"
    )


def _function_body(url: str, fonksiyon: str) -> str:
    return _scalar(
        url,
        "SELECT coalesce((SELECT p.prosrc FROM pg_proc p "
        f"WHERE p.oid = to_regprocedure('{fonksiyon}()')), '<yok>')",
    )


def _trigger_def(url: str, tetikleyici: str, tablo: str) -> str:
    return _scalar(
        url,
        "SELECT coalesce((SELECT pg_get_triggerdef(t.oid) FROM pg_trigger t "
        f"WHERE t.tgrelid = '{tablo}'::regclass AND t.tgname = '{tetikleyici}' "
        "AND NOT t.tgisinternal), '<yok>')",
    )


def test_identity_triples_are_derived_and_non_empty():
    """BOŞ-KÜME KONTROL KOLU: çift kümesi boşsa aşağıdaki matris hiç koşmazdı."""
    assert IDENTITY_TRIPLES, (
        "036'dan HİÇ (tetikleyici, tablo, fonksiyon) üçlüsü türetilemedi — "
        "kimlik matrisi boş koşardı"
    )
    for tetikleyici, tablo, fonksiyon in IDENTITY_TRIPLES:
        assert tablo.startswith("social."), tablo
        assert fonksiyon.startswith("social."), fonksiyon
    assert len(set(IDENTITY_IDS)) == len(IDENTITY_IDS), IDENTITY_IDS


@pytest.mark.parametrize("triple", IDENTITY_TRIPLES, ids=IDENTITY_IDS)
def test_036_refuses_a_foreign_function_with_our_name(scratch_db_migrated, triple):
    """Aynı adlı YABANCI fonksiyon EZİLMEZ: migration fail-closed durur.

    İki iddia birden: ret geldi mi, VE yabancı gövde yerinde mi (bizimki
    yazılmadı). İkincisi olmadan test, "ezip sonra hata veren" bir migration'la
    da yeşil olurdu.
    """
    _tetikleyici, _tablo, fonksiyon = triple
    url = scratch_db_migrated
    _run_sql(url, _foreign_function_sql(fonksiyon))
    assert FOREIGN_BODY_MARKER in _function_body(url, fonksiyon), "kurulum tutmadı"

    result = _apply_file(url, MIGRATION_036, single_transaction=False)

    assert result.returncode != 0, (
        f"{fonksiyon}: yabancı fonksiyon varken migration GEÇTİ:\n{result.stdout}"
    )
    assert IDENTITY_MARKER in result.stderr, result.stderr
    assert fonksiyon in result.stderr, result.stderr
    assert FOREIGN_BODY_MARKER in _function_body(url, fonksiyon), (
        f"{fonksiyon}: yabancı gövde EZİLDİ — kapı ret verdi ama yazımdan SONRA"
    )


@pytest.mark.parametrize("triple", IDENTITY_TRIPLES, ids=IDENTITY_IDS)
def test_036_refuses_a_foreign_trigger_with_our_name(scratch_db_migrated, triple):
    """Aynı adlı YABANCI tetikleyici DÜŞÜRÜLMEZ: migration fail-closed durur."""
    tetikleyici, tablo, _fonksiyon = triple
    url = scratch_db_migrated
    _run_sql(url, _foreign_trigger_sql(tetikleyici, tablo))
    yabanci_def = _trigger_def(url, tetikleyici, tablo)
    assert "BEFORE DELETE" in yabanci_def, f"kurulum tutmadı: {yabanci_def}"

    result = _apply_file(url, MIGRATION_036, single_transaction=False)

    assert result.returncode != 0, (
        f"{tetikleyici}: yabancı tetikleyici varken migration GEÇTİ:\n{result.stdout}"
    )
    assert IDENTITY_MARKER in result.stderr, result.stderr
    assert tetikleyici in result.stderr, result.stderr
    assert _trigger_def(url, tetikleyici, tablo) == yabanci_def, (
        f"{tetikleyici}: yabancı tetikleyici DEĞİŞTİ"
    )


def test_036_reapply_after_036_passes(scratch_db_migrated):
    """POZİTİF KONTROL — İDEMPOTANS: kanonik nesneler kimlik kapısından GEÇER.

    Bu ayak olmadan yukarıdaki ret testleri "her koşulda reddeden" bir kapıyla
    da yeşil olurdu ve ikinci koşum imkânsız hâle gelirdi.
    """
    result = _apply_file(scratch_db_migrated, MIGRATION_036)
    assert result.returncode == 0, f"036 yeniden uygulama DURDU:\n{result.stderr}"
    assert IDENTITY_MARKER not in result.stderr, result.stderr


def test_identity_gate_is_load_bearing(scratch_db_migrated, tmp_path):
    """MUTASYON KOLU: kapı SİLİNİRSE yabancı gövde gerçekten EZİLİR.

    Kapının varlığı değil, ETKİSİ ölçülür: doktorlanmış dosyada aynı kurulum
    `rc=0` ile geçer ve yabancı gövde bizimkiyle DEĞİŞTİRİLİR. Kapı ölü olsaydı
    bu kol da ret alır ve test kırmızı düşerdi.
    """
    url = scratch_db_migrated
    ham = MIGRATION_036.read_text(encoding="utf-8")
    bas = ham.index(IDENTITY_GATE_BEGIN)
    son = ham.index(IDENTITY_GATE_END)
    assert bas < son, "kapı sınırları dosyada beklenen sırada değil"
    doktorlu = ham[:bas] + ham[son:]
    assert len(doktorlu) < len(ham), "mutasyon hiçbir şey silmedi"

    hedef = tmp_path / "036_kapisiz.sql"
    hedef.write_text(doktorlu, encoding="utf-8")

    _tetikleyici, _tablo, fonksiyon = IDENTITY_TRIPLES[0]
    _run_sql(url, _foreign_function_sql(fonksiyon))
    result = _apply_file(url, hedef, single_transaction=False)

    assert result.returncode == 0, (
        f"kapısız mutant BAŞKA bir sebeple durdu — mutasyon ölçtüğünü ölçmüyor:\n"
        f"{result.stderr}"
    )
    assert FOREIGN_BODY_MARKER not in _function_body(url, fonksiyon), (
        "kapısız mutant yabancı gövdeyi EZMEDİ — kapı zaten gereksizmiş demektir"
    )


@pytest.mark.parametrize("triple", IDENTITY_TRIPLES, ids=IDENTITY_IDS)
def test_036_down_refuses_a_foreign_function_with_our_name(scratch_db_migrated, triple):
    """Geri alma da ADIN gördüğünü düşürmez: yabancı gövde varsa fail-closed."""
    _tetikleyici, _tablo, fonksiyon = triple
    url = scratch_db_migrated
    _run_sql(url, _foreign_function_sql(fonksiyon))

    result = _apply_down(url, DOWN_036)

    assert result.returncode != 0, (
        f"{fonksiyon}: yabancı gövde varken geri alma GEÇTİ:\n{result.stdout}"
    )
    assert REFUSAL_MARKER_036 in result.stderr, result.stderr
    assert FOREIGN_BODY_MARKER in _function_body(url, fonksiyon), (
        f"{fonksiyon}: yabancı fonksiyon DÜŞÜRÜLDÜ"
    )


@pytest.mark.parametrize("triple", IDENTITY_TRIPLES, ids=IDENTITY_IDS)
def test_036_down_refuses_a_foreign_trigger_with_our_name(scratch_db_migrated, triple):
    """Aynı asimetri geri almada da kapalı: yabancı tetikleyici düşürülmez."""
    tetikleyici, tablo, _fonksiyon = triple
    url = scratch_db_migrated
    _run_sql(url, _foreign_trigger_sql(tetikleyici, tablo))
    yabanci_def = _trigger_def(url, tetikleyici, tablo)

    result = _apply_down(url, DOWN_036)

    assert result.returncode != 0, (
        f"{tetikleyici}: yabancı tetikleyici varken geri alma GEÇTİ:\n{result.stdout}"
    )
    assert REFUSAL_MARKER_036 in result.stderr, result.stderr
    assert _trigger_def(url, tetikleyici, tablo) == yabanci_def, (
        f"{tetikleyici}: yabancı tetikleyici DEĞİŞTİ"
    )


def test_down_function_pins_match_the_live_catalog(scratch_db_migrated):
    """İKİ DOSYA ARASINDA IRAKSAMA KAPISI — ölçüm katalogtan, liste dosyadan.

    `036_down.sql` fonksiyon kimliğini gövdenin ÖZETİYLE (`md5(prosrc)`) pinler:
    ileri dosyanın gövde sabitlerinin ikinci bir KOPYASINI taşımaz. Özet, ileri
    dosya değiştiği gün bayatlar — bu test o bayatlığı yakalar ve pinin
    ÖLÇÜLMÜŞ kalmasını zorunlu kılar.
    """
    url = scratch_db_migrated
    down_metni = DOWN_036.read_text(encoding="utf-8")
    olculen = {}
    for _tetikleyici, _tablo, fonksiyon in IDENTITY_TRIPLES:
        olculen[fonksiyon] = _scalar(
            url, f"SELECT md5(p.prosrc) FROM pg_proc p WHERE p.oid = to_regprocedure('{fonksiyon}()')"
        )

    assert olculen, "hiç fonksiyon ölçülemedi — kapı boş kümede yeşil düşerdi"
    eksik = {
        ad: ozet for ad, ozet in olculen.items() if ozet not in down_metni
    }
    assert not eksik, (
        "036_down.sql'in gövde özeti CANLI katalogla uyuşmuyor (ileri dosya "
        f"değişti, pin güncellenmedi): {eksik}"
    )


# ═══════════════════════════════════════════════════════════════════════════
# 10. `ON_ERROR_STOP` çağıranın oturumunda BOZULMAZ
# ═══════════════════════════════════════════════════════════════════════════
#
# `032_down.sql` ve `035_down.sql` `\set ON_ERROR_STOP on`u DOSYA KAPSAMINDA
# bırakır ve değer çağıranın psql oturumuna SIZAR. Bu görevde doğan ÜÇ script
# bunu yapmaz: önceki değeri saklar, sonunda GERİ YÜKLER.
#
# DÜRÜST SINIR: geri yükleme dosyanın SONUNDA koşar. Ret yolunda psql girdi
# işlemeyi ON_ERROR_STOP yüzünden keser ve o satıra ulaşılmaz — ölçülmüş,
# dosya başlıklarında yazılı. Sızan değer `on`dur, yani çağıran DAHA KATI olur;
# davranış sürprizi, güvenlik açığı değil.


def _source_in_session(url: str, script, prior: str | None) -> subprocess.CompletedProcess:
    """Script'i bir psql OTURUMUNDA `\\i` ile kaynaklar; SONRAKİ değeri basar.

    ÖLÇÜLDÜ (psql 16.15): `ON_ERROR_STOP` YERLEŞİK bir değişkendir ve her zaman
    TANIMLIdır — bayrak verilmemiş taze bir oturumda bile `:{?ON_ERROR_STOP}`
    DOĞRU döner ve değeri `off`tur. Yani "tanımsız" diye bir başlangıç durumu
    yoktur; `prior=None` hücresi "çağıran hiç dokunmadı" (varsayılan `off`)
    anlamına gelir.
    """
    argv, env = _argv_without_error_stop(url)
    lines = []
    if prior is not None:
        lines.append(f"\\set ON_ERROR_STOP {prior}")
    lines.append(r"\echo ONCE=:ON_ERROR_STOP")
    lines.append(f"\\i {script}")
    lines.append(r"\echo SONRA=:ON_ERROR_STOP")
    return subprocess.run(
        argv, input="\n".join(lines) + "\n", env=env, capture_output=True, text=True
    )


_DOWN_SCRIPT_IDS = {DOWN_033: "033", DOWN_034: "034", DOWN_036: "036"}


@pytest.mark.parametrize(
    "script, prior",
    [
        (script, prior)
        for script in NEW_DOWN_SCRIPTS
        for prior in (None, "on", "1")
    ],
    ids=[
        f"{_DOWN_SCRIPT_IDS[script]}-{prior or 'dokunulmamis'}"
        for script in NEW_DOWN_SCRIPTS
        for prior in (None, "on", "1")
    ],
)
def test_down_scripts_restore_caller_on_error_stop(scratch_db_migrated, script, prior):
    """3 script × 3 önceki durum = 9 hücre; oturum ayarı DEĞİŞMEDEN döner.

    Üçüncü hücre (`1`) bilinçlidir: `on` ile `1` psql için aynı ANLAMI taşır ama
    aynı METİN değildir. Script değeri "doğruysa `on` yaz" diye normalize etseydi
    bu hücre kırmızı düşerdi — çağıranın yazdığı metin korunur.
    """
    url = scratch_db_migrated
    if script is DOWN_033:
        # 033 geri alması 036'nın genişlettiği CHECK'i taşıyan tabloyu düşürür;
        # sıra runbook'ta 036 → 033'tür, o yüzden önce 036 geri alınır.
        assert _apply_down(url, DOWN_036).returncode == 0

    result = _source_in_session(url, script, prior)

    assert result.returncode == 0, f"kaynaklama DURDU:\n{result.stderr}"
    # `prior=None` = çağıran hiç dokunmadı → psql varsayılanı `off`.
    beklenen = "SONRA=off" if prior is None else f"SONRA={prior}"
    assert beklenen in result.stdout, (
        f"çağıranın ON_ERROR_STOP'u BOZULDU (beklenen {beklenen!r}):\n{result.stdout}"
    )


# ═══════════════════════════════════════════════════════════════════════════
# 11. MİGRATION MATRİSİ — donmuş sözleşme uyumu (Step 2)
# ═══════════════════════════════════════════════════════════════════════════


def test_clean_001_to_032_expectations_unchanged(scratch_db_empty):
    """032 TEK BAŞINA uygulandığında beklentisi DEĞİŞMEDİ.

    Sürüm-farkındalık eski beklentiyi gevşetmez: 036 uygulanmamış bir şemada
    032'nin doğrulayıcısı hâlâ İKİ indeks ve İKİ kısıt bekler ve geçer.
    """
    url = scratch_db_empty
    _apply_range(url, upto=32)
    assert (
        _scalar(
            url,
            "SELECT count(*) FROM pg_constraint WHERE conrelid = "
            "'social.sector_research_artifacts'::regclass AND contype <> 'n'",
        )
        == "2"
    )
    result = _apply_file(url, MIGRATION_032)
    assert result.returncode == 0, f"032 tek başına DURDU:\n{result.stderr}"


def test_full_001_to_036(scratch_db_empty):
    """001..036 sırayla uygulanır — zincirin tamamı yeşil."""
    url = scratch_db_empty
    _apply_range(url, upto=36)
    assert _scalar(url, "SELECT to_regclass('social.sector_package_runs') IS NOT NULL") == "t"


def test_032_reapply_after_036_passes(scratch_db_migrated):
    """036 UYGULANMIŞKEN 032 yeniden uygulanabilir (sürüm-farkında beklenti)."""
    result = _apply_file(scratch_db_migrated, MIGRATION_032)
    assert result.returncode == 0, f"032 yeniden uygulama DURDU:\n{result.stderr}"
    assert FAILURE_MARKER_032 not in result.stderr


def test_033_reapply_after_036_passes(scratch_db_migrated):
    """036 UYGULANMIŞKEN 033 yeniden uygulanabilir (genişlemiş CHECK kabul)."""
    result = _apply_file(scratch_db_migrated, MIGRATION_033)
    assert result.returncode == 0, f"033 yeniden uygulama DURDU:\n{result.stderr}"
    assert FAILURE_MARKER_033 not in result.stderr


def test_036_down_then_032_and_033_reapply(scratch_db_migrated):
    """Geri almadan SONRA da 032/033 yeniden uygulanabilir — eski beklenti geçerli."""
    url = scratch_db_migrated
    assert _apply_down(url, DOWN_036).returncode == 0
    for migration in (MIGRATION_032, MIGRATION_033):
        result = _apply_file(url, migration)
        assert result.returncode == 0, f"{migration.name} DURDU:\n{result.stderr}"


@pytest.mark.parametrize(
    "extra, marker, label",
    [
        (
            "CREATE UNIQUE INDEX artifacts_sinsi_unique ON "
            "social.sector_research_artifacts (run_id, source);",
            FAILURE_MARKER_032,
            "adı geçmeyen fazladan indeks",
        ),
        (
            "ALTER TABLE social.sector_research_artifacts "
            f"DROP CONSTRAINT {K09_CONSTRAINT}; "
            "ALTER TABLE social.sector_research_artifacts "
            f"ADD CONSTRAINT {K09_CONSTRAINT} UNIQUE (run_id, kind);",
            FAILURE_MARKER_032,
            "adı DOĞRU ama tanımı YANLIŞ K-09 kısıtı",
        ),
    ],
)
def test_unnamed_extra_index_still_rejected(scratch_db_migrated, extra, marker, label):
    """KAPALILIK VAADİ ZAYIFLAMADI — muafiyet TEK ADA ve TEK TANIMA yazılıdır.

    "036 sonrası her şey serbest" DEĞİL: adı geçmeyen fazladan bir indeks de,
    adı doğru ama tanımı başka olan bir kısıt da hâlâ REDDEDİLİR.
    """
    url = scratch_db_migrated
    _run_sql(url, extra)
    result = _apply_file(url, MIGRATION_032)
    assert result.returncode != 0, f"{label} sessizce geçti:\n{result.stdout}"
    assert marker in result.stderr, result.stderr


def test_032_down_is_fail_closed_while_036_is_applied(scratch_db_migrated):
    """DÜZELTMENİN KENDİ YAN ETKİSİ — ölçüldü ve PİNLENDİ.

    036, `sector_package_runs.package_id`i `sector_packages(id)`e yabancı
    anahtarla bağlar (plan Task 6 hükmü, harfiyen). Bunun ÖLÇÜLEN yan etkisi:
    032'nin geri alması artık SIRA-BAĞIMLIdır — 036 ayaktayken
    `DROP TABLE social.sector_packages` PostgreSQL tarafından reddedilir.

    Yan etki SESSİZ DEĞİLDİR ve zararsızdır: script kendi transaction'ını
    sahiplendiği için ret KALICI İZ BIRAKMAZ. Burada iki şey birden ölçülür —
    sıfır-dışı çıkış VE bayt-bayt değişmemiş şema. Doğru sıra (Task 18
    runbook'u) 036 → 034 → 033 → 032'dir.
    """
    url = scratch_db_migrated
    down_032 = ROLLBACK_DIR / "032_down.sql"

    schema_before = _schema_fingerprint(url)
    result = _apply_down(url, down_032)

    assert result.returncode != 0, f"sıra dışı 032 geri alması KOŞTU:\n{result.stdout}"
    assert "sector_package_runs" in result.stderr, result.stderr
    assert _schema_fingerprint(url) == schema_before, "sıra dışı çağrı iz bıraktı"

    # POZİTİF KONTROL: doğru sırada aynı script GEÇER.
    assert _apply_down(url, DOWN_036).returncode == 0
    assert _apply_down(url, down_032).returncode == 0, "doğru sırada da düştü"


def test_unrecognized_event_type_still_rejected(scratch_db_migrated):
    """033 tarafında da kapalılık korundu: TANINMAYAN olay türü REDDEDİLİR."""
    url = scratch_db_migrated
    _run_sql(
        url,
        "ALTER TABLE social.package_events DROP CONSTRAINT package_events_type_check; "
        "ALTER TABLE social.package_events ADD CONSTRAINT package_events_type_check "
        "CHECK (event_type IN ('mismatch_fallthrough', 'package_read_error', "
        "'stale_assignment_fallback', 'stamp_missing', 'stamp_invalid', "
        "'stamp_stale_at_persist', 'activation', 'rollback', 'deactivation', "
        "'approval', 'rejection', 'uydurma_olay'));",
    )
    result = _apply_file(url, MIGRATION_033)
    assert result.returncode != 0, f"12. değer sessizce kabul edildi:\n{result.stdout}"
    assert FAILURE_MARKER_033 in result.stderr, result.stderr


def test_rollback_036_restores_prior_shape(scratch_db_empty):
    """036 → 036_down şemayı BAYT-BAYT önceki hâline döndürür."""
    url = scratch_db_empty
    _apply_range(url, upto=35)
    before = _schema_fingerprint(url)

    assert _apply_file(url, MIGRATION_036).returncode == 0
    assert _schema_fingerprint(url) != before, "036 hiçbir şey değiştirmedi (?)"

    result = _apply_down(url, DOWN_036)
    assert result.returncode == 0, f"geri alma DURDU:\n{result.stderr}"
    assert _schema_fingerprint(url) == before, "şema önceki hâline DÖNMEDİ"


def test_rollback_033_and_034_restore_prior_shape(scratch_db_empty):
    """033/034 → geri alma şemayı BAYT-BAYT önceki hâline döndürür.

    Bu iki script Plan 1'den DEVRALINAN gerçek boşluktu (ölçüldü: `rollback/`
    yalnız `032_down.sql` ve `035_down.sql` taşıyordu); Plan 2'nin geri alma
    anlatısı onlara dayanıyor.
    """
    url = scratch_db_empty
    _apply_range(url, upto=32)
    before = _schema_fingerprint(url)

    assert _apply_file(url, MIGRATION_033).returncode == 0
    assert _apply_file(url, MIGRATIONS_DIR / "034_admin_events.sql").returncode == 0
    assert _schema_fingerprint(url) != before

    assert _apply_down(url, DOWN_034).returncode == 0
    assert _apply_down(url, DOWN_033).returncode == 0
    assert _schema_fingerprint(url) == before, "şema önceki hâline DÖNMEDİ"


@pytest.mark.parametrize(
    "script, setup, marker",
    [
        (
            DOWN_033,
            "INSERT INTO social.package_events (event_type, actor) "
            "VALUES ('activation', 'a');",
            REFUSAL_MARKER_033,
        ),
        (
            DOWN_034,
            "INSERT INTO social.admin_events (kind, payload, idempotency_key) "
            "VALUES ('t6', '{}'::jsonb, 't6-1');",
            REFUSAL_MARKER_034,
        ),
    ],
    ids=["033", "034"],
)
def test_033_and_034_down_refuse_when_data_exists(scratch_db_migrated, script, setup, marker):
    """Devralınan iki script de VERİ VARKEN fail-closed durur (032'nin disiplini)."""
    url = scratch_db_migrated
    assert _apply_down(url, DOWN_036).returncode == 0
    _run_sql(url, setup)
    schema_before = _schema_fingerprint(url)
    data_before = _data_fingerprint(url)

    result = _apply_down(url, script)

    assert result.returncode != 0, f"veri varken geri alma GEÇTİ:\n{result.stdout}"
    assert marker in result.stderr, result.stderr
    assert _schema_fingerprint(url) == schema_before
    assert _data_fingerprint(url) == data_before
