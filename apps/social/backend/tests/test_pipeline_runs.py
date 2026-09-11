"""Koşu ve artefakt servisi (Plan 2 Task 8).

Bu dosya beş sözleşmeyi birden pinler:

1. **Ham katman salt-eklemedir** ve K-09/K-80 kapıları yazımdan ÖNCE koşar.
2. **TEK KAPI LİSTESİ** — `load_verified_run` yedi kapıyı uygular; ikinci bir
   liste yazmak mümkün değildir.
3. **Kanıt veritabanından okunur** — köken jetonu kilitli satırdan türetilir,
   çağırandan alınmaz (arayüz eki R8(c)/A2(d)).
4. **Olay üyeliği tek kilitle serileşir** ve onay mührü üyeliğe bağlıdır
   (AÇIK-1 · A1(a)/(b)/(c) · A3).
5. **Maskeleme süzgeci atlanamaz** (K-136) ve olay izini korur.

Matrisler ELLE SEÇİLMİŞ ÖRNEKTEN değil KAVRAMDAN türetilir: alan kümeleri
`dataclasses.fields`'tan, kapı listesi modülün kendi sabitinden, eşleme tablosu
`EngineResult`'ın alan listesinden okunur — yarın eklenen bir alan kendiliğinden
kapsanır.
"""

from __future__ import annotations

import ast
import asyncio
import inspect
import logging
import uuid
from dataclasses import dataclass, fields as dataclass_fields
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

import asyncpg
import pytest

from app.core.database import _init_connection
from app.services import sector_package_lifecycle as lifecycle
from app.services.sector_package_lifecycle import (
    ActivationGateEvidence,
    RollbackGateEvidence,
)
from app.services.sector_pipeline import identity, readiness_items, runs
from app.services.sector_pipeline.engine_contract import (
    ENGINE_RESULT_ALANLARI,
    BulguIzi,
    EngineResult,
    KararsizMadde,
    PolicyReport,
    UygulanmayanKarar,
)

from .conftest import _require_test_database

ACTOR = "admin@otomaix"
MOTOR_SURUM = "engine-1.0.0"
CONFIG_SHA = "c" * 64
KURAL = "kural-mevzuat"
KURAL_V1 = "v1"
KURAL_V2 = "v2"

RUNS_KAYNAK = Path(runs.__file__).read_text(encoding="utf-8")
LIFECYCLE_KAYNAK = Path(lifecycle.__file__).read_text(encoding="utf-8")


# ═══ Ortak yardımcılar ══════════════════════════════════════════════════════


@pytest.fixture
async def pkg_db(db):
    """Üretimin KENDİ bağlantı yapılandırması (jsonb codec)."""
    await _init_connection(db)
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


def _aday(**overrides) -> dict:
    aday = {
        "kapsam": "Kuyumculuk: altın ve gümüş takı perakendesi.",
        "kanca_kaliplari": ["Ayar farkını gözle ayırt edebilir misiniz?"],
    }
    aday.update(overrides)
    return aday


def _karar_satiri(**overrides) -> dict:
    row = {
        "tur": "karar",
        "alan": "kanca_kaliplari",
        "oge_yolu": "kanca_kaliplari[0]",
        "unit_id": "ku-0123456789ab",
        "oge_sha": "a" * 64,
        "karar": "koru",
        "gerekce": "Kalıp sektörde hâlâ karşılık buluyor.",
        "kanit": "",
        "aktor": "sentez",
    }
    row.update(overrides)
    return row


def _motor_satiri(
    *, karar: str = "koru", kural_kimligi: str = KURAL, kural_surumu: str = KURAL_V1,
    unit_id: str = "ku-0123456789ab",
) -> dict:
    return _karar_satiri(
        karar=karar,
        unit_id=unit_id,
        aktor="motor",
        kanit="Denetçi-1 satırı ve doğrulanmış URL referansı mevcut.",
        kural_kimligi=kural_kimligi,
        kural_surumu=kural_surumu,
    )


_VARSAYILAN = object()
"""Sentinel: `None` GEÇERLİ bir test girdisidir (K-24 eksik-değer kolu)."""


def _policy_report(**overrides) -> PolicyReport:
    alanlar = {
        "kararsizlar": (),
        "bulgular": (),
        "uygulanmayan_kararlar": (),
        "acik_soru_kimlikleri": (),
    }
    alanlar.update(overrides)
    return PolicyReport(**alanlar)


def _engine_result(
    *,
    sonuc: str = "activation_eligible",
    final_candidate: dict | None = None,
    final_decision_log: list[dict] | None = None,
    engine_version: str = MOTOR_SURUM,
    engine_config_sha: str = CONFIG_SHA,
    sebep: str | None = None,
    barrier_report: dict | None = _VARSAYILAN,
    policy_report: PolicyReport | None = None,
) -> EngineResult:
    """Motor sonucu — hash'ler `identity.canonical_sha` ile (test edilen kodla DEĞİL).

    `content_sha` ve `decision_log_sha` beklentisi Task 3'ün kanonik hash
    kuralından üretilir; Task 8'in kendi kodundan değil.
    """
    if sonuc == "activation_eligible":
        aday = _aday() if final_candidate is None else final_candidate
        gunluk = [_karar_satiri()] if final_decision_log is None else final_decision_log
        content_sha = identity.canonical_sha(aday)
        log_sha = identity.canonical_sha(gunluk)
        gunluk_demeti = tuple(gunluk)
    else:
        aday = final_candidate
        gunluk_demeti = tuple(final_decision_log) if final_decision_log else None
        content_sha = None
        log_sha = None
    return EngineResult(
        sonuc=sonuc,
        sebep=sebep,
        final_candidate=aday,
        final_decision_log=gunluk_demeti,
        engine_diff={"degisen": 1},
        policy_report=policy_report or _policy_report(),
        barrier_report=(
            {"oran": 0.1} if barrier_report is _VARSAYILAN else barrier_report
        ),
        content_sha=content_sha,
        decision_log_sha=log_sha,
        engine_version=engine_version,
        engine_config_sha=engine_config_sha,
    )


async def _tam_kosu(
    db,
    sector_id: uuid.UUID,
    *,
    run_id: str | None = None,
    final_decision_log: list[dict] | None = None,
    engine_version: str = MOTOR_SURUM,
    engine_config_sha: str = CONFIG_SHA,
    katman1: str | None = "PASS",
) -> str:
    """Açılmış + tamamlanmış (`activation_eligible`) bir koşu."""
    run_id = run_id or runs.new_run_id()
    await runs.open_run(db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")
    await runs.record_result(
        db,
        run_id=run_id,
        result=_engine_result(
            final_decision_log=final_decision_log,
            engine_version=engine_version,
            engine_config_sha=engine_config_sha,
        ),
    )
    if katman1 is not None:
        await runs.attest_katman1(
            db, run_id=run_id, kosum_kimligi="k1-1", sonuc=katman1, actor=ACTOR
        )
    return run_id


async def _anlik_goruntu_yaz(db, run_id: str, *, acik_sorular=()) -> None:
    """Koşu satırına onay anlık görüntüsü yazar (K-98: İLK yazım serbesttir).

    Üretim yazıcısı Task 14'ün kalemidir; bu görevde kanıt yükünün okuduğu satır
    alanı testlerde doğrudan kurulur.
    """
    await db.execute(
        "UPDATE social.sector_package_runs SET approval_snapshot = $2 "
        "WHERE run_id = $1",
        run_id,
        {"acik_sorular": list(acik_sorular)},
    )


async def _paket(
    db, sector_id: uuid.UUID, *, version: int, status: str, run_id: str | None = None
) -> uuid.UUID:
    return await db.fetchval(
        "INSERT INTO social.sector_packages "
        "(sector_id, version, status, schema_version, content, run_id) "
        "VALUES ($1, $2, $3, 1, $4, $5) RETURNING id",
        sector_id,
        version,
        status,
        _aday(),
        run_id,
    )


async def _kokenli_paket(
    db,
    sector_id: uuid.UUID,
    *,
    version: int,
    status: str,
    kural_surumu: str | None = KURAL_V1,
    engine_version: str = MOTOR_SURUM,
    engine_config_sha: str = CONFIG_SHA,
    karar: str = "koru",
    katman1: str | None = "PASS",
) -> tuple[uuid.UUID, str]:
    """Kökeni OKUNABİLİR bir paket: koşu satırı + tamamlanmış motor kararı.

    `kural_surumu=None` ise günlükte motor kararı YOKTUR (sentez kararı yazılır).
    """
    if kural_surumu is None:
        gunluk = [_karar_satiri()]
    else:
        gunluk = [_motor_satiri(karar=karar, kural_surumu=kural_surumu)]
    run_id = await _tam_kosu(
        db,
        sector_id,
        final_decision_log=gunluk,
        engine_version=engine_version,
        engine_config_sha=engine_config_sha,
        katman1=katman1,
    )
    package_id = await _paket(
        db, sector_id, version=version, status=status, run_id=run_id
    )
    await db.execute(
        "UPDATE social.sector_package_runs SET package_id = $2 WHERE run_id = $1",
        run_id,
        package_id,
    )
    return package_id, run_id


async def _affected(db, *, kural_surumu: str = KURAL_V1) -> runs.AffectedSet:
    return await runs.affected_packages(
        db,
        engine_version=MOTOR_SURUM,
        engine_config_sha=CONFIG_SHA,
        kural_kimligi=KURAL,
        kural_surumu=kural_surumu,
    )


def _kod_kimlikleri(kaynak: str) -> set[str]:
    """Kaynaktaki KOD kimlikleri — açıklama ve docstring metni HARİÇ.

    Ham metin taraması bu iddiaları ölçemez: bir yasak adı ANLATAN yorum satırı
    da eşleşir. Kimlik kümesi AST'ten türetilir.
    """
    agac = ast.parse(kaynak)
    adlar: set[str] = set()
    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.Name):
            adlar.add(dugum.id)
        elif isinstance(dugum, ast.Attribute):
            adlar.add(dugum.attr)
        elif isinstance(dugum, ast.arg):
            adlar.add(dugum.arg)
        elif isinstance(dugum, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            adlar.add(dugum.name)
        elif isinstance(dugum, ast.alias):
            adlar.add((dugum.asname or dugum.name).rsplit(".", 1)[-1])
    return adlar


async def _committed_sektor_sil(conn, sector_id) -> None:
    """Commit edilmiş test verisini FK ve tetikleyici sırasına UYARAK siler.

    Sıra ölçülmüştür: `sector_package_runs.package_id` → `sector_packages`
    yabancı anahtarı önce çözülür; `package_rollback_plans` satırları ise
    036'nın `BEFORE UPDATE OR DELETE` kapısı yüzünden önce `bekliyor`a
    çevrilir (kapı
    yürütülmüş satırın silinmesini reddeder — bu testin değil, kapının doğru
    davranışıdır).
    """
    await conn.execute(
        "UPDATE social.package_rollback_plans SET durum = 'bekliyor', "
        "kanit_jetonu_harcandi_at = NULL WHERE package_id IN "
        "(SELECT id FROM social.sector_packages WHERE sector_id = $1)",
        sector_id,
    )
    await conn.execute(
        "DELETE FROM social.package_rollback_plans WHERE package_id IN "
        "(SELECT id FROM social.sector_packages WHERE sector_id = $1)",
        sector_id,
    )
    await conn.execute(
        "DELETE FROM social.package_events WHERE sector_id = $1", sector_id
    )
    await conn.execute(
        "UPDATE social.sector_package_runs SET package_id = NULL WHERE sector_id = $1",
        sector_id,
    )
    await conn.execute(
        "DELETE FROM social.sector_package_runs WHERE sector_id = $1", sector_id
    )
    await conn.execute(
        "DELETE FROM social.sector_packages WHERE sector_id = $1", sector_id
    )
    await conn.execute("DELETE FROM social.sectors WHERE id = $1", sector_id)


def _fonksiyon_govdesi(kaynak: str, ad: str) -> str:
    """Kaynaktan TEK bir fonksiyonun gövde metnini çıkarır (yapısal testler için)."""
    agac = ast.parse(kaynak)
    for dugum in ast.walk(agac):
        if isinstance(dugum, (ast.FunctionDef, ast.AsyncFunctionDef)) and dugum.name == ad:
            return ast.get_source_segment(kaynak, dugum) or ""
    raise AssertionError(f"fonksiyon bulunamadı: {ad}")


# ═══ 1. Koşu satırı ve ham artefakt ═════════════════════════════════════════


async def test_open_run_and_record_artifact(pkg_db):
    """POZİTİF KONTROL: koşu açılır, artefakt yazılır, ikisi `run_id` ile bağlıdır."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()

    satir_id = await runs.open_run(
        pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk"
    )
    assert isinstance(satir_id, uuid.UUID)

    kayit = await pkg_db.fetchrow(
        "SELECT durum, sonuc, kosu_turu FROM social.sector_package_runs WHERE run_id = $1",
        run_id,
    )
    assert kayit["durum"] == "calisiyor"
    assert kayit["sonuc"] is None
    assert kayit["kosu_turu"] == "ilk"

    artefakt_id = await runs.record_artifact(
        pkg_db,
        run_id=run_id,
        sector_slug="kuyumculuk",
        kind="research",
        source=runs.build_stamp(
            model="arac-1", surum="2026-09", tarih="2026-09-08", girdi_ozeti="brief-sha"
        ),
        content_md="# Ham çıktı",
    )
    assert isinstance(artefakt_id, uuid.UUID)
    assert (
        await pkg_db.fetchval(
            "SELECT count(*) FROM social.sector_research_artifacts WHERE run_id = $1",
            run_id,
        )
        == 1
    )


async def test_duplicate_artifact_rejected(pkg_db):
    """K-09: aynı `(run_id, source, kind)` ikinci kez yazılamaz."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")
    damga = runs.build_stamp(
        model="arac-1", surum="2026-09", tarih="2026-09-08", girdi_ozeti="brief-sha"
    )
    await runs.record_artifact(
        pkg_db,
        run_id=run_id,
        sector_slug="kuyumculuk",
        kind="research",
        source=damga,
        content_md="ilk",
    )
    with pytest.raises(asyncpg.UniqueViolationError):
        await runs.record_artifact(
            pkg_db,
            run_id=run_id,
            sector_slug="kuyumculuk",
            kind="research",
            source=damga,
            content_md="ikinci",
        )


async def test_artifact_update_rejected_by_db(pkg_db):
    """Ham katman SALT-EKLEMEDİR — servis denemez, denese de DB reddeder."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")
    await runs.record_artifact(
        pkg_db,
        run_id=run_id,
        sector_slug="kuyumculuk",
        kind="research",
        source=runs.build_stamp(
            model="arac-1", surum="2026-09", tarih="2026-09-08", girdi_ozeti="brief-sha"
        ),
        content_md="ilk",
    )
    with pytest.raises(asyncpg.PostgresError):
        await pkg_db.execute(
            "UPDATE social.sector_research_artifacts SET content_md = 'degisti' "
            "WHERE run_id = $1",
            run_id,
        )
    # Servis katmanı da `UPDATE` yazmaz — yapısal kapı.
    assert "UPDATE social.sector_research_artifacts" not in RUNS_KAYNAK


@pytest.mark.parametrize(
    "source",
    [
        "arac-1",
        "model=arac-1",
        "model=arac-1; surum=2026-09",
        "model=arac-1; surum=2026-09; tarih=2026-09-08",
        "model=arac-1; surum=2026-09; tarih=dun; girdi_ozeti=brief",
        "model=; surum=2026-09; tarih=2026-09-08; girdi_ozeti=brief",
    ],
    ids=["damgasiz", "tek_alan", "iki_alan", "uc_alan", "bozuk_tarih", "bos_model"],
)
async def test_stamp_missing_rejects_write(pkg_db, source):
    """K-80: damga eksikse artefakt HİÇ yazılmaz (servis kapısı)."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")

    with pytest.raises(runs.ArtifactStampMissing):
        await runs.record_artifact(
            pkg_db,
            run_id=run_id,
            sector_slug="kuyumculuk",
            kind="research",
            source=source,
            content_md="ham",
        )
    assert (
        await pkg_db.fetchval(
            "SELECT count(*) FROM social.sector_research_artifacts WHERE run_id = $1",
            run_id,
        )
        == 0
    )


def test_run_folder_equals_run_id(tmp_path):
    """K-17: koşu klasörü adı DB `run_id`'sine EŞİTTİR; ikinci kimlik uzayı yok."""
    run_id = "kosu-abc123"
    yol = runs.run_folder(run_id)
    assert yol.name == run_id
    assert yol.parent.name == "kosu"
    with pytest.raises(ValueError):
        runs.run_folder("../kacis")
    with pytest.raises(ValueError):
        runs.run_folder("a/b")


# ═══ 2. Yarım koşu + yerel arıza bildirimi ══════════════════════════════════


async def test_mark_incomplete_preserves_row(pkg_db):
    """K-82: satır KALIR, `durum='tamamlanmadi'` olur; sebep yazılır."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")
    await runs.record_artifact(
        pkg_db,
        run_id=run_id,
        sector_slug="kuyumculuk",
        kind="research",
        source=runs.build_stamp(
            model="arac-1", surum="2026-09", tarih="2026-09-08", girdi_ozeti="brief"
        ),
        content_md="yarim",
    )

    await runs.mark_incomplete(
        pkg_db, run_id=run_id, asama="kaynak-tabani", sebep="K-127 duruşu"
    )

    kayit = await pkg_db.fetchrow(
        "SELECT durum, sebep, sonuc FROM social.sector_package_runs WHERE run_id = $1",
        run_id,
    )
    assert kayit["durum"] == "tamamlanmadi"
    assert kayit["sebep"] == "K-127 duruşu"
    assert kayit["sonuc"] is None
    # Artefakt EZİLMEZ.
    assert (
        await pkg_db.fetchval(
            "SELECT content_md FROM social.sector_research_artifacts WHERE run_id = $1",
            run_id,
        )
        == "yarim"
    )


async def test_mark_incomplete_writes_admin_event(pkg_db):
    """Yerel arıza n8n `errorWorkflow`'a ULAŞMAZ — outbox satırı bu yüzden var."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")

    await runs.mark_incomplete(
        pkg_db, run_id=run_id, asama="motor", sebep="yerel CLI zaman aşımı"
    )

    olay = await pkg_db.fetchrow(
        "SELECT kind, payload, idempotency_key FROM social.admin_events "
        "WHERE idempotency_key = $1",
        f"{run_id}:motor",
    )
    assert olay is not None
    assert olay["kind"] == runs.TUR_ARIZASI_OLAYI
    assert olay["payload"]["run_id"] == run_id
    assert olay["payload"]["asama"] == "motor"


async def test_admin_event_idempotent_per_run_and_stage(pkg_db):
    """`idempotency_key` = koşu + aşama; ikinci çağrı YENİ satır üretmez."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")

    await runs.mark_incomplete(pkg_db, run_id=run_id, asama="sentez", sebep="ilk")
    await runs.mark_incomplete(pkg_db, run_id=run_id, asama="sentez", sebep="ikinci")
    await runs.mark_incomplete(pkg_db, run_id=run_id, asama="denetim", sebep="baska")

    sayilar = await pkg_db.fetch(
        "SELECT idempotency_key, count(*) AS n FROM social.admin_events "
        "WHERE idempotency_key LIKE $1 GROUP BY idempotency_key",
        f"{run_id}:%",
    )
    assert {kayit["idempotency_key"]: kayit["n"] for kayit in sayilar} == {
        f"{run_id}:sentez": 1,
        f"{run_id}:denetim": 1,
    }


async def test_mark_incomplete_requires_stage(pkg_db):
    """`asama` ZORUNLUDUR — bildirim anahtarı onsuz üretilemez."""
    imza = inspect.signature(runs.mark_incomplete)
    assert imza.parameters["asama"].default is inspect.Parameter.empty


@pytest.mark.parametrize("asama", ["", "bilinmeyen", "Motor", "brief_doctor"])
async def test_stage_values_are_closed(pkg_db, asama):
    """Aşama kümesi KAPALIDIR; dışındaki değer satır da olay da yazmaz."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")

    with pytest.raises(ValueError):
        await runs.mark_incomplete(pkg_db, run_id=run_id, asama=asama, sebep="x")

    assert (
        await pkg_db.fetchval(
            "SELECT durum FROM social.sector_package_runs WHERE run_id = $1", run_id
        )
        == "calisiyor"
    )
    assert (
        await pkg_db.fetchval(
            "SELECT count(*) FROM social.admin_events WHERE idempotency_key LIKE $1",
            f"{run_id}:%",
        )
        == 0
    )


async def test_admin_event_payload_is_masked(pkg_db):
    """K-136: olay yükü maskeleme süzgecinden GEÇER."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")

    sir = "sk-live-ABCDEFGHIJKLMNOP1234"
    await runs.mark_incomplete(
        pkg_db,
        run_id=run_id,
        asama="motor",
        sebep=f"alt süreç düştü: api_key={sir}",
    )

    yuk = await pkg_db.fetchval(
        "SELECT payload FROM social.admin_events WHERE idempotency_key = $1",
        f"{run_id}:motor",
    )
    assert sir not in yuk["sebep"]
    assert runs.MASKE in yuk["sebep"]
    # Olay izi KORUNUR.
    assert yuk["run_id"] == run_id
    assert yuk["asama"] == "motor"


# ═══ 3. Yeniden koşum ve kimlik uzayı ═══════════════════════════════════════


async def test_retry_gets_new_run_id_linked_by_parent(pkg_db):
    """K-83: yeniden koşum YENİ `run_id` alır ve `parent_run_id` ile bağlanır."""
    sector_id = await _sub_sector(pkg_db)
    ilk = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=ilk, kosu_turu="periyodik")
    await runs.mark_incomplete(pkg_db, run_id=ilk, asama="denetim", sebep="yarım")

    yeni = await runs.new_retry_run_id(pkg_db, parent_run_id=ilk)

    assert yeni != ilk
    kayit = await pkg_db.fetchrow(
        "SELECT parent_run_id, kosu_turu, durum FROM social.sector_package_runs "
        "WHERE run_id = $1",
        yeni,
    )
    assert kayit["parent_run_id"] == ilk
    assert kayit["kosu_turu"] == "periyodik"
    assert kayit["durum"] == "calisiyor"


def test_no_attempt_parameter_anywhere():
    """İkinci kimlik uzayı YOK: `attempt` ne parametre ne fonksiyon adıdır."""
    agac = ast.parse(RUNS_KAYNAK)
    for dugum in ast.walk(agac):
        if isinstance(dugum, (ast.FunctionDef, ast.AsyncFunctionDef)):
            assert "attempt" not in dugum.name, dugum.name
            adlar = [
                arg.arg
                for arg in list(dugum.args.args)
                + list(dugum.args.kwonlyargs)
                + list(dugum.args.posonlyargs)
            ]
            assert not [ad for ad in adlar if "attempt" in ad], (dugum.name, adlar)
    kimlikler = _kod_kimlikleri(RUNS_KAYNAK)
    assert not [ad for ad in kimlikler if "attempt" in ad], sorted(kimlikler)


async def test_open_run_requires_kosu_turu(pkg_db):
    """R2: `NOT NULL` kolonun ADI KONMUŞ üreticisi olur — varsayılan YOK."""
    imza = inspect.signature(runs.open_run)
    assert imza.parameters["kosu_turu"].default is inspect.Parameter.empty
    assert imza.parameters["kosu_turu"].kind is inspect.Parameter.KEYWORD_ONLY


@pytest.mark.parametrize("deger", ["", "yeni", "ILK", "correction"])
async def test_kosu_turu_value_set_is_closed(pkg_db, deger):
    sector_id = await _sub_sector(pkg_db)
    with pytest.raises(ValueError):
        await runs.open_run(
            pkg_db, sector_id=sector_id, run_id=runs.new_run_id(), kosu_turu=deger
        )


async def test_open_run_rejects_duzeltme_type(pkg_db):
    """`duzeltme` `duzeltilen_run_id` gerektirir; onu yalnız düzeltme yolu yazar."""
    sector_id = await _sub_sector(pkg_db)
    with pytest.raises(ValueError):
        await runs.open_run(
            pkg_db, sector_id=sector_id, run_id=runs.new_run_id(), kosu_turu="duzeltme"
        )


async def test_retry_inherits_type_target_and_package(pkg_db):
    """Düzeltmenin yeniden koşumu ana koşudan ÜÇLÜYÜ devralır (R2 + R4)."""
    sector_id = await _sub_sector(pkg_db)
    ana = await _tam_kosu(pkg_db, sector_id)
    package_id = await _paket(pkg_db, sector_id, version=1, status="draft", run_id=ana)
    await pkg_db.execute(
        "UPDATE social.sector_package_runs SET package_id = $2, approval_karar = 'ret' "
        "WHERE run_id = $1",
        ana,
        package_id,
    )
    duzeltme = await runs.open_correction_run(pkg_db, parent_run_id=ana, actor=ACTOR)
    await runs.mark_incomplete(
        pkg_db, run_id=duzeltme, asama="sentez", sebep="çöktü"
    )

    tekrar = await runs.new_retry_run_id(pkg_db, parent_run_id=duzeltme)

    ana_satir = await pkg_db.fetchrow(
        "SELECT id, package_id, duzeltilen_run_id FROM social.sector_package_runs "
        "WHERE run_id = $1",
        duzeltme,
    )
    tekrar_satir = await pkg_db.fetchrow(
        "SELECT kosu_turu, package_id, duzeltilen_run_id, parent_run_id "
        "FROM social.sector_package_runs WHERE run_id = $1",
        tekrar,
    )
    assert tekrar_satir["kosu_turu"] == "duzeltme"
    assert tekrar_satir["package_id"] == ana_satir["package_id"] == package_id
    assert tekrar_satir["duzeltilen_run_id"] == ana_satir["duzeltilen_run_id"]
    assert tekrar_satir["parent_run_id"] == duzeltme


async def test_retry_refuses_conflicting_type(pkg_db):
    """Devralma UYDURULMAZ: farklı tür verilirse çağrı REDDEDİLİR."""
    sector_id = await _sub_sector(pkg_db)
    ilk = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=ilk, kosu_turu="ilk")
    with pytest.raises(ValueError):
        await runs.open_run(
            pkg_db,
            sector_id=sector_id,
            run_id=runs.new_run_id(),
            kosu_turu="periyodik",
            parent_run_id=ilk,
        )


# ═══ 4. Motor sonucu — K-24 · K-93 · F19 · R2 ═══════════════════════════════


def test_record_result_signature_has_no_var_keyword_arguments():
    """R2: `**report_fields` YOKTUR — isimsiz üretici deliği kapalı."""
    imza = inspect.signature(runs.record_result)
    turler = {p.kind for p in imza.parameters.values()}
    assert inspect.Parameter.VAR_KEYWORD not in turler
    assert inspect.Parameter.VAR_POSITIONAL not in turler


def test_record_result_takes_no_free_form_dict_parameter():
    """İmzada `db` · `run_id` · `result` DIŞINDA parametre YOKTUR."""
    imza = inspect.signature(runs.record_result)
    assert list(imza.parameters) == ["db", "run_id", "result"]


def test_engine_result_to_column_map_is_derived_and_total():
    """Eşleme BİREBİR: `EngineResult`'ın her alanı bir kolona gider, fazlası yok.

    BOŞ-KÜME KONTROL KOLU da burada: eşleme tablosu boşalırsa bu test düşer.
    """
    eslenen = {alan for alan, _kolon in runs._SONUC_KOLON_ESLEMESI}
    assert eslenen, "eşleme tablosu BOŞ — aşağıdaki alan testleri hiçbir şey ölçmezdi"
    assert eslenen == set(ENGINE_RESULT_ALANLARI)
    kolonlar = [kolon for _alan, kolon in runs._SONUC_KOLON_ESLEMESI]
    assert len(kolonlar) == len(set(kolonlar))


async def test_record_result_sets_durum_tamamlandi(pkg_db):
    """`load_verified_run`'ın 1. kapısını sağlanabilir kılan TEK üretici budur."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")
    await runs.record_result(pkg_db, run_id=run_id, result=_engine_result())
    assert (
        await pkg_db.fetchval(
            "SELECT durum FROM social.sector_package_runs WHERE run_id = $1", run_id
        )
        == "tamamlandi"
    )


async def test_record_result_persists_every_engine_result_field(pkg_db):
    """R2'nin sessiz-düşme kapısı: on bir alanın on biri de satırda OKUNUR."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")
    sonuc = _engine_result(
        sebep=None,
        policy_report=_policy_report(
            kararsizlar=(KararsizMadde("ku-0123456789ab", "iki denetçi ayrıştı"),),
            bulgular=(BulguIzi("acik_soru", "ku-0123456789ab", "mevzuat belirsiz"),),
            uygulanmayan_kararlar=(
                UygulanmayanKarar("ku-0123456789ab", "guncelle", "kanit-yok"),
            ),
            acik_soru_kimlikleri=("ku-0123456789ab",),
        ),
    )
    await runs.record_result(pkg_db, run_id=run_id, result=sonuc)

    satir = await pkg_db.fetchrow(
        "SELECT * FROM social.sector_package_runs WHERE run_id = $1", run_id
    )
    for alan, kolon in runs._SONUC_KOLON_ESLEMESI:
        beklenen = getattr(sonuc, alan)
        if alan == "policy_report":
            assert satir[kolon] == sonuc.policy_report.as_payload()
        elif beklenen is None or isinstance(beklenen, str):
            assert satir[kolon] == beklenen, alan
        else:
            # ORACLE Task 3'ün kanonik kuralıdır: JSON'da demet ile liste AYNI
            # değerdir, dolayısıyla eşitliği tip değil KANONİK HASH söyler.
            assert identity.canonical_sha(satir[kolon]) == identity.canonical_sha(
                beklenen
            ), alan


@pytest.mark.parametrize("sonuc", ["activation_eligible", "no_change", "blocked"])
async def test_barrier_report_persisted_for_all_three_outcomes(pkg_db, sonuc):
    """K-24: bariyer raporu ÜÇ sonuçta da koşu satırına yazılır."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")
    rapor = {"kalip_orani": 0.4, "alan_orani": 0.2, "kelime_orani": 0.1}
    await runs.record_result(
        pkg_db,
        run_id=run_id,
        result=_engine_result(
            sonuc=sonuc, barrier_report=rapor, sebep=None if sonuc == "activation_eligible" else "x"
        ),
    )
    assert (
        await pkg_db.fetchval(
            "SELECT barrier_report FROM social.sector_package_runs WHERE run_id = $1",
            run_id,
        )
        == rapor
    )


async def test_completed_run_without_barrier_report_is_rejected(pkg_db):
    """EKSİK DEĞER KAPISI: bariyer raporu yoksa tamamlanmış koşu yazılmaz."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")

    with pytest.raises(ValueError):
        await runs.record_result(
            pkg_db,
            run_id=run_id,
            result=_engine_result(sonuc="blocked", sebep="x", barrier_report=None),
        )
    assert (
        await pkg_db.fetchval(
            "SELECT durum FROM social.sector_package_runs WHERE run_id = $1", run_id
        )
        == "calisiyor"
    )


async def test_barrier_report_round_trip_matches_engine_output(pkg_db):
    """Motorun ürettiği rapor, satırdan okunduğunda BİREBİR aynı olmalı."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")
    rapor = {
        "kalip_orani": 0.37,
        "esikler": {"kalip": 0.5, "alan": 0.4},
        "asilan": [],
    }
    sonuc = _engine_result(barrier_report=rapor)
    await runs.record_result(pkg_db, run_id=run_id, result=sonuc)

    okunan = await pkg_db.fetchval(
        "SELECT barrier_report FROM social.sector_package_runs WHERE run_id = $1", run_id
    )
    assert okunan == rapor
    assert identity.canonical_sha(okunan) == identity.canonical_sha(
        dict(sonuc.barrier_report)
    )


async def test_no_change_run_recorded_without_package_row(pkg_db):
    """K-93: `no_change` koşusu da satır yazar, paket satırı ÜRETMEDEN."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="periyodik")
    await runs.record_result(
        pkg_db,
        run_id=run_id,
        result=_engine_result(sonuc="no_change", sebep="değişiklik yok"),
    )
    satir = await pkg_db.fetchrow(
        "SELECT durum, sonuc, sebep, package_id FROM social.sector_package_runs "
        "WHERE run_id = $1",
        run_id,
    )
    assert (satir["durum"], satir["sonuc"], satir["package_id"]) == (
        "tamamlandi",
        "no_change",
        None,
    )
    assert (
        await pkg_db.fetchval(
            "SELECT count(*) FROM social.sector_packages WHERE sector_id = $1", sector_id
        )
        == 0
    )


async def test_blocked_run_recorded_with_reason(pkg_db):
    """K-90: `blocked` koşusu SEBEBİYLE birlikte kaydedilir."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")
    await runs.record_result(
        pkg_db,
        run_id=run_id,
        result=_engine_result(sonuc="blocked", sebep="acik-soru-var"),
    )
    satir = await pkg_db.fetchrow(
        "SELECT sonuc, sebep FROM social.sector_package_runs WHERE run_id = $1", run_id
    )
    assert (satir["sonuc"], satir["sebep"]) == ("blocked", "acik-soru-var")


@pytest.mark.parametrize("eksik", list(runs.F19_ALANLARI))
async def test_record_result_rejects_eligible_result_missing_f19_fields(pkg_db, eksik):
    """F19: dört köken alanı AYNI işlemde yazılır; biri eksikse yazım REDDEDİLİR."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")

    tam = _engine_result()
    alanlar = {alan.name: getattr(tam, alan.name) for alan in dataclass_fields(EngineResult)}
    alanlar[eksik] = None
    with pytest.raises(ValueError):
        await runs.record_result(pkg_db, run_id=run_id, result=EngineResult(**alanlar))
    assert (
        await pkg_db.fetchval(
            "SELECT durum FROM social.sector_package_runs WHERE run_id = $1", run_id
        )
        == "calisiyor"
    )


async def test_record_result_refuses_a_second_write_for_the_same_run(pkg_db):
    """F3: sonuç yazımı KARŞILAŞTIR-VE-YAZ'dır — son-yazan-kazanır DEĞİL.

    Önceki yazım yalnız koşu kimliğine bakıyordu; iki eşzamanlı tamamlama
    son-yazan-kazanır oluyor ve SONRAKİ herhangi bir çağrı, tamamlanmış (hatta
    onaylanmış) bir koşunun BÜTÜN motor alanlarını değiştirebiliyordu.
    Migration yalnız onay anlık görüntüsünü koruyor, motor alanlarını DEĞİL.
    """
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")
    await runs.record_result(pkg_db, run_id=run_id, result=_engine_result())

    with pytest.raises(ValueError) as hata:
        await runs.record_result(
            pkg_db,
            run_id=run_id,
            result=_engine_result(sonuc="blocked", sebep="ikinci yazıcı"),
        )
    assert "koşu bulunamadı" not in str(hata.value)
    assert "calisiyor" in str(hata.value)

    satir = await pkg_db.fetchrow(
        "SELECT durum, sonuc, sebep, engine_version FROM social.sector_package_runs "
        "WHERE run_id = $1",
        run_id,
    )
    assert satir["durum"] == "tamamlandi"
    assert satir["sonuc"] == "activation_eligible"
    assert satir["sebep"] is None
    assert satir["engine_version"] == MOTOR_SURUM


async def test_record_result_refuses_to_overwrite_an_incomplete_run(pkg_db):
    """K-82 işareti de EZİLEMEZ: yarım koşu sonradan 'tamamlandi' yapılamaz."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")
    await runs.mark_incomplete(
        pkg_db, run_id=run_id, asama="sentez", sebep="yerel zaman aşımı"
    )

    with pytest.raises(ValueError):
        await runs.record_result(pkg_db, run_id=run_id, result=_engine_result())

    satir = await pkg_db.fetchrow(
        "SELECT durum, sonuc, sebep FROM social.sector_package_runs WHERE run_id = $1",
        run_id,
    )
    assert satir["durum"] == "tamamlanmadi"
    assert satir["sonuc"] is None
    assert satir["sebep"] == "yerel zaman aşımı"


async def test_record_result_still_names_a_missing_run_distinctly(pkg_db):
    """KONTROL KOLU: iki red birbirinden AYIRT EDİLİR — mesaj farkı ölçülür."""
    with pytest.raises(ValueError) as hata:
        await runs.record_result(
            pkg_db, run_id="kosu-hic-yok-0001", result=_engine_result()
        )
    assert "koşu bulunamadı" in str(hata.value)


# ═══ 5. TEK KAPI LİSTESİ ════════════════════════════════════════════════════


async def test_load_verified_run_passes_on_complete_run(pkg_db):
    """POZİTİF KONTROL: yedi kapıyı geçen koşu `VerifiedRun` üretir."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _tam_kosu(pkg_db, sector_id)

    kosu = await runs.load_verified_run(pkg_db, run_id=run_id)

    assert isinstance(kosu, runs.VerifiedRun)
    assert kosu.run_id == run_id
    assert kosu.durum == "tamamlandi"
    assert kosu.sonuc == "activation_eligible"
    assert kosu.content_sha == identity.canonical_sha(dict(kosu.final_candidate))


_KAPI_VAKALARI = [
    (
        "durum",
        "UPDATE social.sector_package_runs SET sonuc = NULL, durum = 'tamamlanmadi' "
        "WHERE run_id = $1",
        "durum",
    ),
    (
        "sonuc",
        "UPDATE social.sector_package_runs SET sonuc = 'no_change' WHERE run_id = $1",
        "sonuc",
    ),
    (
        "engine_version",
        "UPDATE social.sector_package_runs SET engine_version = NULL WHERE run_id = $1",
        "engine_version",
    ),
    (
        "engine_config_sha",
        "UPDATE social.sector_package_runs SET engine_config_sha = NULL WHERE run_id = $1",
        "engine_config_sha",
    ),
    (
        "content_sha",
        "UPDATE social.sector_package_runs SET content_sha = repeat('0', 64) "
        "WHERE run_id = $1",
        "content_sha",
    ),
    (
        "final_decision_log",
        "UPDATE social.sector_package_runs SET final_candidate = NULL, "
        "final_decision_log = NULL, decision_log_sha = NULL WHERE run_id = $1",
        "final_decision_log",
    ),
    (
        "decision_log_sha",
        "UPDATE social.sector_package_runs SET decision_log_sha = repeat('0', 64) "
        "WHERE run_id = $1",
        "decision_log_sha",
    ),
]


def test_seven_gate_matrix_covers_the_declared_gate_list():
    """MATRİS KAVRAMDAN TÜRETİLİR: kapı listesi ile vaka listesi BİREBİR."""
    assert [vaka[0] for vaka in _KAPI_VAKALARI] == list(runs.KAPILAR)
    assert len(runs.KAPILAR) == 7


@pytest.mark.parametrize(
    "kapi,mutasyon,imza", _KAPI_VAKALARI, ids=[v[0] for v in _KAPI_VAKALARI]
)
async def test_load_verified_run_rejects_each_of_seven_gates(pkg_db, kapi, mutasyon, imza):
    """Kapı başına BİR vaka — mutasyon uygulanınca doğrulama DÜŞER."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _tam_kosu(pkg_db, sector_id)
    await pkg_db.execute(mutasyon, run_id)

    with pytest.raises(runs.RunNotVerified) as hata:
        await runs.load_verified_run(pkg_db, run_id=run_id)
    assert imza in str(hata.value)


async def test_load_verified_run_rejects_missing_row(pkg_db):
    await _sub_sector(pkg_db)
    with pytest.raises(runs.RunNotVerified):
        await runs.load_verified_run(pkg_db, run_id="kosu-yok")


async def test_verified_run_payload_fields_are_read_only(pkg_db):
    """R6(e): dokuz jsonb yükünün dokuzu da SALT-OKUNUR; takma ad paylaşılmaz."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _tam_kosu(pkg_db, sector_id)
    await runs.attest_katman2(
        pkg_db, run_id=run_id, kosum_kimligi="k2-1", ozet="sunuldu", actor=ACTOR
    )
    await runs.attest_readiness(
        pkg_db,
        run_id=run_id,
        kapi_maddeleri=tuple(sorted(readiness_items.KAPI_MADDELERI)),
        sinyal_maddeleri=tuple(sorted(readiness_items.SINYAL_MADDELERI)),
        actor=ACTOR,
    )
    await pkg_db.execute(
        "UPDATE social.sector_package_runs SET approval_snapshot = $2 WHERE run_id = $1",
        run_id,
        {"acik_sorular": []},
    )

    kosu = await runs.load_verified_run(pkg_db, run_id=run_id)

    yuk_alanlari = (
        "final_candidate",
        "final_decision_log",
        "policy_report",
        "barrier_report",
        "engine_diff",
        "approval_snapshot",
        "katman1_attestation",
        "katman2_attestation",
        "readiness_attestation",
    )
    assert len(yuk_alanlari) == 9
    for alan in yuk_alanlari:
        deger = getattr(kosu, alan)
        assert deger is not None, alan
        if hasattr(deger, "keys"):
            with pytest.raises(TypeError):
                deger["yeni"] = 1
        else:
            assert isinstance(deger, tuple), alan


async def test_load_verified_run_takes_row_lock(test_db_setup):
    """Kilitli okuma GERÇEKTİR: ikinci bağlantı `FOR UPDATE NOWAIT` ile düşer.

    Deterministik: `NOWAIT` beklemez, kilit varsa ANINDA `lock_not_available`
    verir. `for_update=False` kolu pozitif kontroldür — kapı her koşulda
    kilitlemiyor.
    """
    url = _require_test_database(test_db_setup)
    kurulum = await asyncpg.connect(url)
    await _init_connection(kurulum)
    okuyucu = await asyncpg.connect(url)
    sector_id = None
    run_id = None
    try:
        sector_id = await _sub_sector(kurulum)
        run_id = await _tam_kosu(kurulum, sector_id)

        tx = kurulum.transaction()
        await tx.start()
        await runs.load_verified_run(kurulum, run_id=run_id, for_update=True)
        with pytest.raises(asyncpg.LockNotAvailableError):
            await okuyucu.fetchval(
                "SELECT id FROM social.sector_package_runs WHERE run_id = $1 "
                "FOR UPDATE NOWAIT",
                run_id,
            )
        await tx.rollback()

        # Pozitif kontrol: kilitsiz okuma satırı KİLİTLEMEZ.
        tx2 = kurulum.transaction()
        await tx2.start()
        await runs.load_verified_run(kurulum, run_id=run_id, for_update=False)
        assert (
            await okuyucu.fetchval(
                "SELECT id FROM social.sector_package_runs WHERE run_id = $1 "
                "FOR UPDATE NOWAIT",
                run_id,
            )
            is not None
        )
        await tx2.rollback()
    finally:
        if run_id is not None:
            await kurulum.execute(
                "DELETE FROM social.sector_package_runs WHERE run_id = $1", run_id
            )
        if sector_id is not None:
            await kurulum.execute("DELETE FROM social.sectors WHERE id = $1", sector_id)
        await okuyucu.close()
        await kurulum.close()


# ═══ 6. Kapı tasdikleri (F18) ═══════════════════════════════════════════════


async def test_attest_katman1_persists_run_and_result(pkg_db):
    """F18: Katman-1 tasdiki KANITTIR — koşum kimliği · sonuç · kim · ne zaman."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")

    await runs.attest_katman1(
        pkg_db, run_id=run_id, kosum_kimligi="katman1-2026-09-08", sonuc="PASS",
        actor=ACTOR,
    )

    tasdik = await pkg_db.fetchval(
        "SELECT katman1_attestation FROM social.sector_package_runs WHERE run_id = $1",
        run_id,
    )
    assert tasdik["kosum_kimligi"] == "katman1-2026-09-08"
    assert tasdik["sonuc"] == "PASS"
    assert tasdik["actor"] == ACTOR
    assert tasdik["at"]


async def test_attest_katman2_persists_run_and_presentation(pkg_db):
    """Katman-2: koşuldu + SUNULDU kaydı; sonucu kapı DEĞİLDİR."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")

    await runs.attest_katman2(
        pkg_db, run_id=run_id, kosum_kimligi="katman2-1", ozet="ayrışma zayıf",
        actor=ACTOR,
    )

    tasdik = await pkg_db.fetchval(
        "SELECT katman2_attestation FROM social.sector_package_runs WHERE run_id = $1",
        run_id,
    )
    assert tasdik["kosum_kimligi"] == "katman2-1"
    assert tasdik["sunuldu"] is True
    assert tasdik["ozet"] == "ayrışma zayıf"
    assert tasdik["at"]
    # Sonuç kapı değildir: tasdikte PASS/FAIL alanı YOKTUR.
    assert "sonuc" not in tasdik


@pytest.mark.parametrize("aktor", ["", "   ", None])
async def test_attest_refuses_blank_actor(pkg_db, aktor):
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")
    with pytest.raises(ValueError):
        await runs.attest_katman1(
            pkg_db, run_id=run_id, kosum_kimligi="k", sonuc="PASS", actor=aktor
        )


# ═══ 7. Hazırlık tasdiki (R9/H5) ════════════════════════════════════════════


def test_checklist_item_set_has_twenty_items():
    assert len(readiness_items.MADDELER) == 20


def test_item_ids_are_unique():
    kimlikler = [m.madde_id for m in readiness_items.MADDELER]
    assert len(set(kimlikler)) == len(kimlikler)


@pytest.mark.parametrize("sinif", ["", "kapı", "gate", "sinyal_", None])
def test_item_classes_are_closed(sinif):
    with pytest.raises((ValueError, TypeError)):
        readiness_items.ChecklistItem("md-99", sinif, True, "x")


def test_gate_and_signal_sets_partition_the_item_set():
    assert readiness_items.KAPI_MADDELERI & readiness_items.SINYAL_MADDELERI == frozenset()
    assert (
        readiness_items.KAPI_MADDELERI | readiness_items.SINYAL_MADDELERI
        == readiness_items.MADDE_KIMLIKLERI
    )


def test_katman2_signal_item_is_not_a_gate_item():
    """15. madde bir SONUÇ iddiasıdır — tamamlanma kapısına GİRMEZ."""
    onbesinci = readiness_items.MADDELER[14]
    assert onbesinci.madde_id == "md-15"
    assert onbesinci.sinif == "sinyal"
    assert onbesinci.madde_id not in readiness_items.KAPI_MADDELERI


def test_madde_kumesi_sha_uses_identity_canonical_rule():
    """İkinci hash kuralı YOK: parmak izi `identity.canonical_sha`'dan gelir."""
    beklenen = identity.canonical_sha(
        [
            {"madde_id": m.madde_id, "sinif": m.sinif, "otomatik": m.otomatik}
            for m in readiness_items.MADDELER
        ]
    )
    assert readiness_items.MADDE_KUMESI_SHA == beklenen


@pytest.mark.parametrize("mutasyon", ["ekle", "cikar", "sinif_degistir"])
def test_madde_kumesi_sha_changes_when_item_set_changes(mutasyon):
    """Madde eklenince/çıkınca ya da sınıfı değişince parmak izi DEĞİŞİR."""
    temel = [
        {"madde_id": m.madde_id, "sinif": m.sinif, "otomatik": m.otomatik}
        for m in readiness_items.MADDELER
    ]
    if mutasyon == "ekle":
        yeni = temel + [{"madde_id": "md-21", "sinif": "kapi", "otomatik": True}]
    elif mutasyon == "cikar":
        yeni = temel[:-1]
    else:
        yeni = [dict(m) for m in temel]
        yeni[14]["sinif"] = "kapi"
    assert identity.canonical_sha(yeni) != readiness_items.MADDE_KUMESI_SHA


def test_attest_readiness_takes_no_onaylandi_parameter():
    """H5'in ana ispatı: onay uydurulamaz, TÜRETİLİR."""
    assert "onaylandi" not in inspect.signature(runs.attest_readiness).parameters


async def test_attest_readiness_persists_actor_time_and_items(pkg_db):
    """POZİTİF KONTROL: tam kapı kümesiyle kayıt DOĞAR."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")

    await runs.attest_readiness(
        pkg_db,
        run_id=run_id,
        kapi_maddeleri=tuple(sorted(readiness_items.KAPI_MADDELERI)),
        sinyal_maddeleri=tuple(sorted(readiness_items.SINYAL_MADDELERI)),
        actor=ACTOR,
    )

    tasdik = await pkg_db.fetchval(
        "SELECT readiness_attestation FROM social.sector_package_runs WHERE run_id = $1",
        run_id,
    )
    assert tasdik["onaylandi"] is True
    assert tasdik["actor"] == ACTOR
    assert tasdik["at"]
    assert tasdik["madde_kumesi_sha"] == readiness_items.MADDE_KUMESI_SHA
    assert set(tasdik["kapi_maddeleri"]) == readiness_items.KAPI_MADDELERI


def _kapi_listesi() -> list[str]:
    return sorted(readiness_items.KAPI_MADDELERI)


def _sinyal_listesi() -> list[str]:
    return sorted(readiness_items.SINYAL_MADDELERI)


@pytest.mark.parametrize(
    "ad",
    [
        "bos",
        "eksik",
        "taninmayan",
        "sinyal_kapida",
        "kapi_sinyalde",
        "tekrar",
    ],
)
async def test_attest_readiness_refuses_invalid_item_sets(pkg_db, ad):
    """BEŞ ret koşulunun HEPSİ: kayıt hiç YAZILMAZ, sessiz `False` da üretilmez."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")

    kapi = _kapi_listesi()
    sinyal = _sinyal_listesi()
    if ad == "bos":
        kapi = []
    elif ad == "eksik":
        kapi = kapi[:-1]
    elif ad == "taninmayan":
        kapi = kapi + ["md-99"]
    elif ad == "sinyal_kapida":
        kapi = kapi + sinyal
    elif ad == "kapi_sinyalde":
        sinyal = sinyal + [kapi[0]]
    elif ad == "tekrar":
        kapi = kapi + [kapi[0]]

    with pytest.raises(runs.ReadinessAttestationRefused):
        await runs.attest_readiness(
            pkg_db,
            run_id=run_id,
            kapi_maddeleri=tuple(kapi),
            sinyal_maddeleri=tuple(sinyal),
            actor=ACTOR,
        )
    assert (
        await pkg_db.fetchval(
            "SELECT readiness_attestation FROM social.sector_package_runs "
            "WHERE run_id = $1",
            run_id,
        )
        is None
    )


# Ekin adıyla saydığı beş ayrı ret adı — yukarıdaki matrisin adlandırılmış
# kapıları. Matris kavramdan türer; bu adlar ekin sözleşmesini karşılar.
async def test_attest_readiness_refuses_empty_gate_set(pkg_db):
    await test_attest_readiness_refuses_invalid_item_sets(pkg_db, "bos")


async def test_attest_readiness_refuses_missing_gate_item(pkg_db):
    await test_attest_readiness_refuses_invalid_item_sets(pkg_db, "eksik")


async def test_attest_readiness_refuses_unknown_item(pkg_db):
    await test_attest_readiness_refuses_invalid_item_sets(pkg_db, "taninmayan")


async def test_attest_readiness_refuses_signal_item_in_gate_set(pkg_db):
    await test_attest_readiness_refuses_invalid_item_sets(pkg_db, "sinyal_kapida")


async def test_attest_readiness_refuses_gate_item_in_signal_set(pkg_db):
    await test_attest_readiness_refuses_invalid_item_sets(pkg_db, "kapi_sinyalde")


async def test_attest_readiness_refuses_duplicate_item(pkg_db):
    await test_attest_readiness_refuses_invalid_item_sets(pkg_db, "tekrar")


@pytest.mark.parametrize("aktor", ["", "   ", None])
async def test_attest_readiness_refuses_blank_actor(pkg_db, aktor):
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")
    with pytest.raises(ValueError):
        await runs.attest_readiness(
            pkg_db,
            run_id=run_id,
            kapi_maddeleri=tuple(_kapi_listesi()),
            sinyal_maddeleri=tuple(_sinyal_listesi()),
            actor=aktor,
        )


# ═══ 8. K-136 — maskeleme süzgeci ═══════════════════════════════════════════


@pytest.mark.parametrize(
    "metin,sizan",
    [
        ("api_key=sk-live-ABCDEFGHIJKLMNOP1234", "sk-live-ABCDEFGHIJKLMNOP1234"),
        ("PASSWORD: hunter2supersecret", "hunter2supersecret"),
        ("Authorization: Bearer abcdefghijklmnop", "abcdefghijklmnop"),
        ("token='0123456789abcdef0123456789abcdef0123456789'", "0123456789abcdef"),
        (
            "dsn=postgresql://kullanici:parolam@127.0.0.1:5433/otomaix",
            "parolam",
        ),
        (
            "jwt eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dBjftJeZ4CVPmB92K27u",
            "eyJhbGciOiJIUzI1NiJ9",
        ),
    ],
    ids=["api_key", "password", "bearer", "hex_token", "dsn", "jwt"],
)
def test_mask_filter_redacts_secret_shaped_values(metin, sizan):
    maskeli = runs.mask_secrets(metin)
    assert sizan not in maskeli
    assert runs.MASKE in maskeli


def test_mask_filter_preserves_event_trace():
    """AŞIRI MASKELEME YOK: iz anahtarları maskelenirse bildirim izlenemez olur."""
    metin = (
        "run_id=kosu-abc123 asama=motor incident_id=olay-42 durum=tamamlanmadi "
        "secret=cokgizlidegersaklanmali"
    )
    maskeli = runs.mask_secrets(metin)
    assert "run_id=kosu-abc123" in maskeli
    assert "asama=motor" in maskeli
    assert "incident_id=olay-42" in maskeli
    assert "durum=tamamlanmadi" in maskeli
    assert "cokgizlidegersaklanmali" not in maskeli


def test_mask_filter_applies_to_error_messages(caplog):
    """Hata mesajları da kapsamdadır — sızıntının en olası yerlerinden biri."""
    caplog.set_level(logging.ERROR, logger=runs.__name__)
    try:
        raise RuntimeError("baglanti kurulamadi: api_key=sk-live-GIZLIDEGER12345678")
    except RuntimeError:
        runs.logger.exception("run_id=kosu-1 motor cagrisi dustu")

    tum_metin = "\n".join(
        kayit.getMessage() + (kayit.exc_text or "") for kayit in caplog.records
    )
    assert "sk-live-GIZLIDEGER12345678" not in tum_metin
    assert "run_id=kosu-1" in tum_metin


def test_mask_filter_applies_to_subprocess_stderr(caplog):
    """Alt süreç stderr'i günlüğe giderken maskelenir."""
    caplog.set_level(logging.WARNING, logger=runs.__name__)
    stderr = (
        "Traceback (most recent call last):\n"
        "  File 'cli.py', line 3\n"
        "RuntimeError: ANTHROPIC_API_KEY=sk-ant-GIZLI0123456789abcdef gecersiz\n"
    )
    runs.log_run("kosu-2", f"alt surec stderr: {stderr}", level=logging.WARNING)

    kayit = caplog.records[-1].getMessage()
    assert "sk-ant-GIZLI0123456789abcdef" not in kayit
    assert "run_id=kosu-2" in kayit


def test_log_writer_cannot_bypass_mask_filter(caplog):
    """YAPISAL: süzgeç günlükçünün KENDİSİNE takılı — maskesiz ikinci yol YOK."""
    assert any(
        isinstance(suzgec, runs.SecretMaskingFilter) for suzgec in runs.logger.filters
    )
    assert RUNS_KAYNAK.count("logging.getLogger(") == 1

    caplog.set_level(logging.INFO, logger=runs.__name__)
    runs.logger.info("dogrudan cagri: api_key=sk-live-DOGRUDAN123456789")
    assert "sk-live-DOGRUDAN123456789" not in caplog.records[-1].getMessage()


def test_mask_payload_walks_nested_structures():
    yuk = {
        "run_id": "kosu-3",
        "detay": {"komut": ["psql", "--password=gizliparolam123"]},
    }
    maskeli = runs.mask_payload(yuk)
    assert maskeli["run_id"] == "kosu-3"
    assert "gizliparolam123" not in str(maskeli)


# ═══ 9. Düzeltme turu (K-106/K-72/NEW-2/NEW-3) ══════════════════════════════


async def _reddedilmis_kosu(db, sector_id) -> tuple[str, uuid.UUID]:
    run_id = await _tam_kosu(db, sector_id)
    package_id = await _paket(db, sector_id, version=1, status="draft", run_id=run_id)
    await db.execute(
        "UPDATE social.sector_package_runs SET package_id = $2, approval_karar = 'ret' "
        "WHERE run_id = $1",
        run_id,
        package_id,
    )
    return run_id, package_id


async def test_open_correction_run_copies_package_target(pkg_db):
    """K-106 POZİTİF KONTROL: hedef taslak KOPYALANIR, soyağacı kaydedilir."""
    sector_id = await _sub_sector(pkg_db)
    ana, package_id = await _reddedilmis_kosu(pkg_db, sector_id)

    duzeltme = await runs.open_correction_run(pkg_db, parent_run_id=ana, actor=ACTOR)

    ana_id = await pkg_db.fetchval(
        "SELECT id FROM social.sector_package_runs WHERE run_id = $1", ana
    )
    satir = await pkg_db.fetchrow(
        "SELECT kosu_turu, package_id, duzeltilen_run_id, durum, sector_id "
        "FROM social.sector_package_runs WHERE run_id = $1",
        duzeltme,
    )
    assert duzeltme != ana
    assert satir["kosu_turu"] == "duzeltme"
    assert satir["package_id"] == package_id
    assert satir["duzeltilen_run_id"] == ana_id
    assert satir["durum"] == "calisiyor"
    assert satir["sector_id"] == sector_id


@pytest.mark.parametrize("karar", ["onay", None])
async def test_open_correction_run_refuses_non_rejected_parent(pkg_db, karar):
    """Düzeltme turu YALNIZ 'ret' kararından açılır."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _tam_kosu(pkg_db, sector_id)
    package_id = await _paket(pkg_db, sector_id, version=1, status="draft", run_id=run_id)
    await pkg_db.execute(
        "UPDATE social.sector_package_runs SET package_id = $2, approval_karar = $3 "
        "WHERE run_id = $1",
        run_id,
        package_id,
        karar,
    )
    with pytest.raises(runs.CorrectionRunRefused):
        await runs.open_correction_run(pkg_db, parent_run_id=run_id, actor=ACTOR)


async def test_open_correction_run_refuses_parent_without_decision(pkg_db):
    """Kararı OLMAYAN koşudan düzeltme açılmaz (ayrı ad, ayrı mesaj)."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _tam_kosu(pkg_db, sector_id)
    package_id = await _paket(pkg_db, sector_id, version=1, status="draft", run_id=run_id)
    await pkg_db.execute(
        "UPDATE social.sector_package_runs SET package_id = $2 WHERE run_id = $1",
        run_id,
        package_id,
    )
    with pytest.raises(runs.CorrectionRunRefused) as hata:
        await runs.open_correction_run(pkg_db, parent_run_id=run_id, actor=ACTOR)
    assert "kararı YOK" in str(hata.value)


async def test_open_correction_run_refuses_second_open_correction(pkg_db):
    """NEW-3: aynı taslak için AÇIK ikinci düzeltme turu YOKTUR."""
    sector_id = await _sub_sector(pkg_db)
    ana, _package_id = await _reddedilmis_kosu(pkg_db, sector_id)
    await runs.open_correction_run(pkg_db, parent_run_id=ana, actor=ACTOR)

    with pytest.raises(runs.CorrectionRunRefused):
        await runs.open_correction_run(pkg_db, parent_run_id=ana, actor=ACTOR)


async def test_open_correction_run_allowed_after_correction_rejected(pkg_db):
    """Zincir SÜREBİLİR: reddedilen düzeltme yeni turu engellemez."""
    sector_id = await _sub_sector(pkg_db)
    ana, _pkg = await _reddedilmis_kosu(pkg_db, sector_id)
    ilk = await runs.open_correction_run(pkg_db, parent_run_id=ana, actor=ACTOR)
    await pkg_db.execute(
        "UPDATE social.sector_package_runs SET approval_karar = 'ret' WHERE run_id = $1",
        ilk,
    )

    ikinci = await runs.open_correction_run(pkg_db, parent_run_id=ana, actor=ACTOR)
    assert ikinci != ilk


async def test_open_correction_run_allowed_after_correction_incomplete(pkg_db):
    """`tamamlanmadi` düzeltme de sonuçlanmıştır — yeni tur açılabilir."""
    sector_id = await _sub_sector(pkg_db)
    ana, _pkg = await _reddedilmis_kosu(pkg_db, sector_id)
    ilk = await runs.open_correction_run(pkg_db, parent_run_id=ana, actor=ACTOR)
    await runs.mark_incomplete(pkg_db, run_id=ilk, asama="sentez", sebep="çöktü")

    ikinci = await runs.open_correction_run(pkg_db, parent_run_id=ana, actor=ACTOR)
    assert ikinci != ilk


async def test_crashed_correction_retry_updates_same_draft(pkg_db):
    """NEW-2: yarım kalan düzeltmenin yeniden koşumu AYNI taslağı hedefler.

    **DÜRÜST SINIR:** "aynı taslağı GÜNCELLER" iddiasının yazma ayağı
    `writeback.update_draft_from_run`'dadır ve o Task 15'te doğar (R9: bu görev
    sonraki görevin yüzeyini tüketemez). Burada ölçülen, o yazımın dayandığı
    KÖKEN bağıdır: yeniden koşum `package_id` · `duzeltilen_run_id` · `kosu_turu`
    üçlüsünü devralır, yani ikinci bir sürüm yakacak bir hedef belirsizliği
    kalmaz. Uçtan uca yazma iddiası Task 15'in testinde koşar.
    """
    sector_id = await _sub_sector(pkg_db)
    ana, package_id = await _reddedilmis_kosu(pkg_db, sector_id)
    duzeltme = await runs.open_correction_run(pkg_db, parent_run_id=ana, actor=ACTOR)
    await runs.mark_incomplete(pkg_db, run_id=duzeltme, asama="motor", sebep="çöktü")

    tekrar = await runs.new_retry_run_id(pkg_db, parent_run_id=duzeltme)

    satir = await pkg_db.fetchrow(
        "SELECT kosu_turu, package_id, duzeltilen_run_id FROM social.sector_package_runs "
        "WHERE run_id = $1",
        tekrar,
    )
    assert satir["kosu_turu"] == "duzeltme"
    assert satir["package_id"] == package_id
    assert satir["duzeltilen_run_id"] is not None


async def test_concurrent_open_correction_single_winner(test_db_setup):
    """İki eşzamanlı düzeltme açma denemesinden YALNIZ BİRİ kazanır.

    Tek bağlantıda araya girmek bu sınıfı ÖLÇMEZ: soru tam olarak "iki ayrı
    transaction aynı taslak için düzeltme açabilir mi".
    """
    url = _require_test_database(test_db_setup)
    kurulum = await asyncpg.connect(url)
    await _init_connection(kurulum)
    isciler: list = []
    sector_id = None
    try:
        sector_id = await _sub_sector(kurulum)
        ana, _pkg = await _reddedilmis_kosu(kurulum, sector_id)

        async def dene():
            baglanti = await asyncpg.connect(url)
            await _init_connection(baglanti)
            isciler.append(baglanti)
            try:
                return await runs.open_correction_run(
                    baglanti, parent_run_id=ana, actor=ACTOR
                )
            except runs.CorrectionRunRefused as hata:
                return hata

        sonuclar = await asyncio.gather(dene(), dene())
        kazanan = [s for s in sonuclar if isinstance(s, str)]
        kaybeden = [s for s in sonuclar if isinstance(s, runs.CorrectionRunRefused)]
        assert len(kazanan) == 1, sonuclar
        assert len(kaybeden) == 1, sonuclar
        assert (
            await kurulum.fetchval(
                "SELECT count(*) FROM social.sector_package_runs "
                "WHERE kosu_turu = 'duzeltme' AND sector_id = $1",
                sector_id,
            )
            == 1
        )
    finally:
        for baglanti in isciler:
            await baglanti.close()
        if sector_id is not None:
            await _committed_sektor_sil(kurulum, sector_id)
        await kurulum.close()


# ═══ 10. K-145 — evren ve sınıflandırma ═════════════════════════════════════


async def _bos_evren(db) -> None:
    """Ön koşul: bu testlerin başında AKTİF paket YOKTUR (boş-küme kontrolü)."""
    assert (
        await db.fetchval(
            "SELECT count(*) FROM social.sector_packages WHERE status = 'active'"
        )
        == 0
    ), "test öncesi aktif paket var — evren iddiaları ölçülemez"


async def test_universe_is_active_packages_only(pkg_db):
    """Evren AKTİF paketlerden kurulur — sektör başına TAM BİR satır."""
    await _bos_evren(pkg_db)
    s1 = await _sub_sector(pkg_db)
    s2 = await _sub_sector(pkg_db)
    a1, _ = await _kokenli_paket(pkg_db, s1, version=1, status="active")
    a2, _ = await _kokenli_paket(pkg_db, s2, version=1, status="active", kural_surumu=None)

    kume = await _affected(pkg_db)

    assert set(kume.aday_kume) == {a1, a2}
    assert kume.kanitli == (a1,)
    assert kume.kanitli_etkilenmemis == (a2,)
    assert kume.ayrilamaz == ()


async def test_archived_and_draft_versions_not_in_universe(pkg_db):
    """Arşivlenmiş ve taslak sürümler evrene GİRMEZ — hedef olabilir, konu olamaz."""
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    await _kokenli_paket(pkg_db, sector_id, version=1, status="archived")
    aktif, _ = await _kokenli_paket(pkg_db, sector_id, version=2, status="active")
    await _kokenli_paket(pkg_db, sector_id, version=3, status="draft")

    kume = await _affected(pkg_db)

    assert kume.aday_kume == (aktif,)


async def test_mixed_active_draft_archived_fixture_yields_one_row_per_sector(pkg_db):
    """Karışık fixture: her sektörden TEK satır (tarihî sürümler ayrı satır ÜRETMEZ)."""
    await _bos_evren(pkg_db)
    aktifler = []
    for _ in range(3):
        sector_id = await _sub_sector(pkg_db)
        await _kokenli_paket(pkg_db, sector_id, version=1, status="archived")
        aktif, _ = await _kokenli_paket(pkg_db, sector_id, version=2, status="active")
        await _kokenli_paket(pkg_db, sector_id, version=3, status="draft")
        aktifler.append(aktif)

    kume = await _affected(pkg_db)
    assert len(kume.aday_kume) == 3
    assert set(kume.aday_kume) == set(aktifler)


async def test_package_without_run_link_is_ayrilamaz(pkg_db):
    """`run_id` bağı YOK → köken okunamaz → `ayrilamaz` (ve evrene GİRER)."""
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    paket = await _paket(pkg_db, sector_id, version=1, status="active", run_id=None)

    kume = await _affected(pkg_db)

    assert kume.ayrilamaz == (paket,)
    assert paket in kume.aday_kume


async def test_package_with_missing_run_row_is_ayrilamaz(pkg_db):
    """`run_id` DOLU ama koşu satırı YOK → `ayrilamaz`."""
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    paket = await _paket(
        pkg_db, sector_id, version=1, status="active", run_id="kosu-hic-yazilmadi"
    )

    kume = await _affected(pkg_db)
    assert kume.ayrilamaz == (paket,)


async def test_incomplete_run_is_ayrilamaz(pkg_db):
    """`durum != 'tamamlandi'` → köken okunamaz → `ayrilamaz`."""
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")
    paket = await _paket(pkg_db, sector_id, version=1, status="active", run_id=run_id)

    kume = await _affected(pkg_db)
    assert kume.ayrilamaz == (paket,)


async def test_unseparable_expands_to_all_active_packages(pkg_db):
    """`ayrilamaz` boş DEĞİLSE küme ADAY KÜMENİN TAMAMINA genişler."""
    await _bos_evren(pkg_db)
    s1 = await _sub_sector(pkg_db)
    s2 = await _sub_sector(pkg_db)
    s3 = await _sub_sector(pkg_db)
    temiz, _ = await _kokenli_paket(pkg_db, s1, version=1, status="active", kural_surumu=None)
    etkilenen, _ = await _kokenli_paket(pkg_db, s2, version=1, status="active")
    kor = await _paket(pkg_db, s3, version=1, status="active", run_id=None)

    kume = await _affected(pkg_db)

    assert kume.genisletildi is True
    assert set(kume.geri_alinacaklar) == {temiz, etkilenen, kor}


async def test_affected_set_separates_proven_and_unprovable(pkg_db):
    """Üç sınıf ayrışır ve ÜÇÜ birlikte aday kümeyi tam kaplar."""
    await _bos_evren(pkg_db)
    s1 = await _sub_sector(pkg_db)
    s2 = await _sub_sector(pkg_db)
    s3 = await _sub_sector(pkg_db)
    kanitli, _ = await _kokenli_paket(pkg_db, s1, version=1, status="active")
    temiz, _ = await _kokenli_paket(pkg_db, s2, version=1, status="active", kural_surumu=None)
    kor = await _paket(pkg_db, s3, version=1, status="active", run_id=None)

    kume = await _affected(pkg_db)

    assert kume.kanitli == (kanitli,)
    assert kume.kanitli_etkilenmemis == (temiz,)
    assert kume.ayrilamaz == (kor,)
    assert set(kume.aday_kume) == {kanitli, temiz, kor}
    assert kume.sinif(kanitli) == "kanitli"
    assert kume.sinif(temiz) == "kanitli_etkilenmemis"
    assert kume.sinif(kor) == "ayrilamaz"


async def test_proven_unaffected_not_in_any_rollback_set(pkg_db):
    """Kanıtlı-etkilenmemiş paket, `ayrilamaz` YOKKEN geri alma kümesine GİRMEZ."""
    await _bos_evren(pkg_db)
    s1 = await _sub_sector(pkg_db)
    s2 = await _sub_sector(pkg_db)
    kanitli, _ = await _kokenli_paket(pkg_db, s1, version=1, status="active")
    temiz, _ = await _kokenli_paket(pkg_db, s2, version=1, status="active", kural_surumu=None)

    kume = await _affected(pkg_db)

    assert kume.genisletildi is False
    assert kume.geri_alinacaklar == (kanitli,)
    assert temiz not in kume.geri_alinacaklar


@pytest.mark.parametrize("karar", ["cikar", "kirp"])
async def test_non_living_decision_makes_package_kanitli(pkg_db, karar):
    """Karar TÜRÜ fark etmez: `cikar`/`kirp` yaşayan kümede YOK ama ETKİLENMİŞ."""
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    paket, _ = await _kokenli_paket(
        pkg_db, sector_id, version=1, status="active", karar=karar
    )

    kume = await _affected(pkg_db)
    assert kume.kanitli == (paket,)


async def test_cikar_decision_makes_package_kanitli(pkg_db):
    await test_non_living_decision_makes_package_kanitli(pkg_db, "cikar")


async def test_kirp_decision_makes_package_kanitli(pkg_db):
    await test_non_living_decision_makes_package_kanitli(pkg_db, "kirp")


async def test_same_rule_different_version_not_matched(pkg_db):
    """Dörtlünün SÜRÜM ayağı: aynı kuralın başka sürümü ETKİLENMİŞ sayılmaz."""
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    paket, _ = await _kokenli_paket(
        pkg_db, sector_id, version=1, status="active", kural_surumu=KURAL_V2
    )

    kume = await _affected(pkg_db, kural_surumu=KURAL_V1)

    assert kume.kanitli == ()
    assert kume.kanitli_etkilenmemis == (paket,)


@pytest.mark.parametrize(
    "eksik", ["engine_version", "engine_config_sha", "kural_kimligi", "kural_surumu"]
)
async def test_affected_requires_full_quad(pkg_db, eksik):
    """Olay girdisi kapalı DÖRTLÜDÜR — eksik ayak kabul edilmez."""
    argumanlar = {
        "engine_version": MOTOR_SURUM,
        "engine_config_sha": CONFIG_SHA,
        "kural_kimligi": KURAL,
        "kural_surumu": KURAL_V1,
    }
    argumanlar[eksik] = ""
    with pytest.raises(ValueError):
        await runs.affected_packages(pkg_db, **argumanlar)


# ═══ 11. Geri alma planı — hedef seçimi ve hedefsiz ═════════════════════════


async def _geri_alinabilir(pkg_db, *, guvenli_arsiv: bool = True):
    """Arşivlenmiş TEMİZ v1 + arızalı damgalı AKTİF v2 taşıyan sektör."""
    sector_id = await _sub_sector(pkg_db)
    await _kokenli_paket(
        pkg_db,
        sector_id,
        version=1,
        status="archived",
        kural_surumu=KURAL_V2 if guvenli_arsiv else KURAL_V1,
    )
    aktif, _ = await _kokenli_paket(pkg_db, sector_id, version=2, status="active")
    return sector_id, aktif


async def test_rollback_plan_freezes_target_version(pkg_db):
    """Hedef sürüm plan ANINDA sabitlenir; sonradan yeniden hesaplanmaz."""
    await _bos_evren(pkg_db)
    sector_id, aktif = await _geri_alinabilir(pkg_db)
    kume = await _affected(pkg_db)

    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)

    satir = await pkg_db.fetchrow(
        "SELECT * FROM social.package_rollback_plans WHERE incident_id = $1", incident_id
    )
    assert satir["package_id"] == aktif
    assert satir["target_version"] == 1
    assert satir["observed_active_version"] == 2
    assert satir["evidence_class"] == "kanitli"
    assert satir["durum"] == "bekliyor"

    # Yeni bir arşiv sürümü doğsa bile PLAN SATIRI değişmez.
    await _kokenli_paket(
        pkg_db, sector_id, version=3, status="archived", kural_surumu=KURAL_V2
    )
    assert (
        await pkg_db.fetchval(
            "SELECT target_version FROM social.package_rollback_plans "
            "WHERE incident_id = $1",
            incident_id,
        )
        == 1
    )


async def test_target_is_highest_archived_version_without_faulty_stamp(pkg_db):
    """İKİ koşul birden: arşivlenmiş VE arızalı sürümle damgasız EN YÜKSEK sürüm."""
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    await _kokenli_paket(pkg_db, sector_id, version=1, status="archived", kural_surumu=KURAL_V2)
    await _kokenli_paket(pkg_db, sector_id, version=2, status="archived", kural_surumu=KURAL_V2)
    await _kokenli_paket(pkg_db, sector_id, version=3, status="archived", kural_surumu=KURAL_V1)
    await _kokenli_paket(pkg_db, sector_id, version=4, status="active")

    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)

    assert (
        await pkg_db.fetchval(
            "SELECT target_version FROM social.package_rollback_plans "
            "WHERE incident_id = $1",
            incident_id,
        )
        == 2
    )


async def test_clean_draft_is_never_chosen_as_target(pkg_db):
    """Planlayıcı KOŞULAMAYAN satır yazmaz: taslak hedef OLAMAZ."""
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    await _kokenli_paket(pkg_db, sector_id, version=1, status="archived", kural_surumu=KURAL_V2)
    await _kokenli_paket(pkg_db, sector_id, version=2, status="active")
    await _kokenli_paket(pkg_db, sector_id, version=3, status="draft", kural_surumu=KURAL_V2)

    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)

    assert (
        await pkg_db.fetchval(
            "SELECT target_version FROM social.package_rollback_plans "
            "WHERE incident_id = $1",
            incident_id,
        )
        == 1
    )


async def test_no_safe_archived_version_yields_persisted_hedefsiz_row(pkg_db):
    """Güvenli sürüm YOKSA satır `hedefsiz` yazılır — geri alma UYDURULMAZ."""
    await _bos_evren(pkg_db)
    sector_id, aktif = await _geri_alinabilir(pkg_db, guvenli_arsiv=False)
    kume = await _affected(pkg_db)

    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)

    satir = await pkg_db.fetchrow(
        "SELECT * FROM social.package_rollback_plans WHERE incident_id = $1", incident_id
    )
    assert satir["durum"] == "hedefsiz"
    assert satir["target_version"] is None
    assert satir["evidence_class"] == "kanitli"
    assert satir["reason"]


async def test_executor_skips_hedefsiz_without_error(pkg_db):
    """`hedefsiz` satır HATA ÜRETMEDEN atlanır ve rapor onu AYRI sayar."""
    await _bos_evren(pkg_db)
    _sector_id, aktif = await _geri_alinabilir(pkg_db, guvenli_arsiv=False)
    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)
    await runs.approve_incident_rollback(pkg_db, incident_id=incident_id, actor=ACTOR)

    rapor = await runs.execute_rollback_plan(
        pkg_db, incident_id=incident_id, actor=ACTOR
    )

    assert rapor.hedefsiz == (aktif,)
    assert rapor.hata == ()
    assert rapor.tamamlandi == ()
    assert (
        await pkg_db.fetchval(
            "SELECT durum FROM social.package_rollback_plans WHERE incident_id = $1",
            incident_id,
        )
        == "hedefsiz"
    )


async def test_rerun_preserves_hedefsiz_outcome(pkg_db):
    """Tekrar koşumda hedef YENİDEN ARANMAZ — sonuç `hedefsiz` KALIR."""
    await _bos_evren(pkg_db)
    sector_id, aktif = await _geri_alinabilir(pkg_db, guvenli_arsiv=False)
    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)
    await runs.execute_rollback_plan(pkg_db, incident_id=incident_id, actor=ACTOR)

    # Aralarında güvenli bir arşiv sürümü doğsa BİLE satır hedefsiz kalır.
    await _kokenli_paket(
        pkg_db, sector_id, version=9, status="archived", kural_surumu=KURAL_V2
    )
    rapor = await runs.execute_rollback_plan(
        pkg_db, incident_id=incident_id, actor=ACTOR
    )

    assert rapor.hedefsiz == (aktif,)
    satir = await pkg_db.fetchrow(
        "SELECT durum, target_version FROM social.package_rollback_plans "
        "WHERE incident_id = $1",
        incident_id,
    )
    assert satir["durum"] == "hedefsiz"
    assert satir["target_version"] is None


# ═══ 12. Onay mührü ve kapsam (AÇIK-1 · A3) ═════════════════════════════════


async def _onayli_olay(pkg_db) -> tuple[str, uuid.UUID]:
    _sector_id, aktif = await _geri_alinabilir(pkg_db)
    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)
    await runs.approve_incident_rollback(pkg_db, incident_id=incident_id, actor=ACTOR)
    return incident_id, aktif


async def test_approve_incident_stamps_only_bekliyor_rows(pkg_db):
    await _bos_evren(pkg_db)
    s1 = await _sub_sector(pkg_db)
    s2 = await _sub_sector(pkg_db)
    await _kokenli_paket(pkg_db, s1, version=1, status="archived", kural_surumu=KURAL_V2)
    a1, _ = await _kokenli_paket(pkg_db, s1, version=2, status="active")
    a2, _ = await _kokenli_paket(pkg_db, s2, version=1, status="active")  # hedefsiz

    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)

    damgalanan = await runs.approve_incident_rollback(
        pkg_db, incident_id=incident_id, actor=ACTOR
    )

    assert damgalanan == 1
    satirlar = {
        satir["package_id"]: satir
        for satir in await pkg_db.fetch(
            "SELECT * FROM social.package_rollback_plans WHERE incident_id = $1",
            incident_id,
        )
    }
    assert satirlar[a1]["onay_actor"] == ACTOR
    assert satirlar[a2]["durum"] == "hedefsiz"
    assert satirlar[a2]["onay_actor"] is None


async def test_approve_incident_writes_same_scope_sha_to_every_stamped_row(pkg_db):
    await _bos_evren(pkg_db)
    aktifler = []
    for _ in range(2):
        sector_id = await _sub_sector(pkg_db)
        await _kokenli_paket(
            pkg_db, sector_id, version=1, status="archived", kural_surumu=KURAL_V2
        )
        aktif, _ = await _kokenli_paket(pkg_db, sector_id, version=2, status="active")
        aktifler.append(aktif)

    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)
    assert await runs.approve_incident_rollback(
        pkg_db, incident_id=incident_id, actor=ACTOR
    ) == 2

    shalar = await pkg_db.fetch(
        "SELECT onay_kapsam_sha FROM social.package_rollback_plans WHERE incident_id = $1",
        incident_id,
    )
    assert len({satir["onay_kapsam_sha"] for satir in shalar}) == 1


async def test_approve_incident_is_idempotent_and_keeps_first_approver_when_scope_unchanged(
    pkg_db,
):
    """Kapsam DEĞİŞMEDİĞİNDE ilk onay ve ilk onaylayan KORUNUR."""
    await _bos_evren(pkg_db)
    incident_id, _aktif = await _onayli_olay(pkg_db)
    ilk = await pkg_db.fetchrow(
        "SELECT onay_actor, onaylandi_at, onay_kapsam_sha "
        "FROM social.package_rollback_plans WHERE incident_id = $1",
        incident_id,
    )

    tekrar = await runs.approve_incident_rollback(
        pkg_db, incident_id=incident_id, actor="baska@otomaix"
    )

    assert tekrar == 0
    ikinci = await pkg_db.fetchrow(
        "SELECT onay_actor, onaylandi_at, onay_kapsam_sha "
        "FROM social.package_rollback_plans WHERE incident_id = $1",
        incident_id,
    )
    assert dict(ikinci) == dict(ilk)


async def test_approve_incident_returns_zero_when_nothing_pending(pkg_db):
    await _bos_evren(pkg_db)
    assert (
        await runs.approve_incident_rollback(
            pkg_db, incident_id="olay-hic-yok", actor=ACTOR
        )
        == 0
    )


@pytest.mark.parametrize("aktor", ["", "   ", None])
async def test_approve_incident_refuses_blank_actor(pkg_db, aktor):
    """FAIL-CLOSED: kısmi damgalama YOK — hiçbir satır damgalanmaz."""
    await _bos_evren(pkg_db)
    _sector_id, _aktif = await _geri_alinabilir(pkg_db)
    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)

    with pytest.raises(ValueError):
        await runs.approve_incident_rollback(
            pkg_db, incident_id=incident_id, actor=aktor
        )
    assert (
        await pkg_db.fetchval(
            "SELECT count(*) FROM social.package_rollback_plans "
            "WHERE incident_id = $1 AND onay_actor IS NOT NULL",
            incident_id,
        )
        == 0
    )


def test_approve_incident_uses_plan1_actor_guard():
    """YAPISAL: `runs.py` ikinci bir aktör kuralı YAZMAZ."""
    assert "from app.services.sector_package_lifecycle import" in RUNS_KAYNAK
    assert "_require_actor as require_actor" in RUNS_KAYNAK
    # `strip()` tabanlı ikinci bir aktör kontrolü yok: aktör adı geçen tek yer
    # `require_actor` çağrısıdır.
    agac = ast.parse(RUNS_KAYNAK)
    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.Call) and isinstance(dugum.func, ast.Attribute):
            if dugum.func.attr == "strip" and isinstance(dugum.func.value, ast.Attribute):
                assert "actor" not in dugum.func.value.attr, ast.dump(dugum)


def test_incident_scope_sha_uses_identity_canonical_rule():
    """İkinci hash kuralı YOK."""
    satirlar = [
        {
            "package_id": uuid.UUID(int=2),
            "observed_active_version": 3,
            "target_version": 1,
            "evidence_class": "kanitli",
        },
        {
            "package_id": uuid.UUID(int=1),
            "observed_active_version": 2,
            "target_version": None,
            "evidence_class": "ayrilamaz",
        },
    ]
    beklenen = identity.canonical_sha(
        [
            {
                "package_id": str(uuid.UUID(int=1)),
                "observed_active_version": 2,
                "target_version": None,
                "evidence_class": "ayrilamaz",
            },
            {
                "package_id": str(uuid.UUID(int=2)),
                "observed_active_version": 3,
                "target_version": 1,
                "evidence_class": "kanitli",
            },
        ]
    )
    assert runs.incident_scope_sha(satirlar) == beklenen


def test_incident_scope_sha_ignores_durum():
    """Kapsam tanımının ANA İSPATI: aynı üyelik, farklı `durum` → AYNI sha."""
    temel = {
        "package_id": uuid.UUID(int=7),
        "observed_active_version": 2,
        "target_version": 1,
        "evidence_class": "kanitli",
    }
    bekliyor = dict(temel, durum="bekliyor", reason="a")
    tamamlandi = dict(temel, durum="tamamlandi", reason="b")
    assert runs.incident_scope_sha([bekliyor]) == runs.incident_scope_sha([tamamlandi])


async def test_incident_scope_sha_covers_rows_outside_bekliyor(pkg_db):
    """`tamamlandi` · `hata` · `hedefsiz` satırlar da HASH'E GİRER."""
    await _bos_evren(pkg_db)
    _sector_id, _aktif = await _geri_alinabilir(pkg_db)
    s2 = await _sub_sector(pkg_db)
    await _kokenli_paket(pkg_db, s2, version=1, status="active")  # hedefsiz olur

    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)

    tum = await pkg_db.fetch(
        "SELECT * FROM social.package_rollback_plans WHERE incident_id = $1", incident_id
    )
    yalniz_bekliyor = [satir for satir in tum if satir["durum"] == "bekliyor"]
    assert len(tum) == 2 and len(yalniz_bekliyor) == 1
    assert runs.incident_scope_sha(tum) != runs.incident_scope_sha(yalniz_bekliyor)


# ═══ 13. Üyelik değişimi — amend (A1(a)) ════════════════════════════════════


def test_amend_rollback_plan_takes_incident_id_and_build_does_not():
    """A1(a)'nın ANA İSPATI: iki fonksiyon karıştırılamaz."""
    amend = inspect.signature(runs.amend_rollback_plan)
    build = inspect.signature(runs.build_rollback_plan)
    assert "incident_id" in amend.parameters
    assert "incident_id" not in build.parameters
    assert amend.return_annotation != build.return_annotation


async def test_amend_rollback_plan_adds_and_removes_rows(pkg_db):
    await _bos_evren(pkg_db)
    s1 = await _sub_sector(pkg_db)
    await _kokenli_paket(pkg_db, s1, version=1, status="archived", kural_surumu=KURAL_V2)
    a1, _ = await _kokenli_paket(pkg_db, s1, version=2, status="active")

    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)
    assert len(await pkg_db.fetch(
        "SELECT 1 FROM social.package_rollback_plans WHERE incident_id = $1", incident_id
    )) == 1

    # İkinci sektör doğar → üyelik BÜYÜR.
    s2 = await _sub_sector(pkg_db)
    await _kokenli_paket(pkg_db, s2, version=1, status="archived", kural_surumu=KURAL_V2)
    a2, _ = await _kokenli_paket(pkg_db, s2, version=2, status="active")

    genis = await _affected(pkg_db)
    assert await runs.amend_rollback_plan(
        pkg_db, incident_id=incident_id, affected=genis, actor=ACTOR
    ) == (1, 0)

    # Sonra ilk paket aktiflikten düşer → üyelik KÜÇÜLÜR.
    await pkg_db.execute(
        "UPDATE social.sector_packages SET status = 'archived' WHERE id = $1", a1
    )
    dar = await _affected(pkg_db)
    assert await runs.amend_rollback_plan(
        pkg_db, incident_id=incident_id, affected=dar, actor=ACTOR
    ) == (0, 1)

    kalan = await pkg_db.fetch(
        "SELECT package_id FROM social.package_rollback_plans WHERE incident_id = $1",
        incident_id,
    )
    assert [satir["package_id"] for satir in kalan] == [a2]


async def test_amend_rollback_plan_is_a_no_op_for_unchanged_membership(pkg_db):
    await _bos_evren(pkg_db)
    incident_id, _aktif = await _onayli_olay(pkg_db)
    kume = await _affected(pkg_db)
    assert await runs.amend_rollback_plan(
        pkg_db, incident_id=incident_id, affected=kume, actor=ACTOR
    ) == (0, 0)


async def test_amend_rollback_plan_leaves_approval_columns_untouched(pkg_db):
    """Madde 6: `amend` `onay_*` YAZMAZ — mühür kendiliğinden BAYATLAR."""
    await _bos_evren(pkg_db)
    incident_id, aktif = await _onayli_olay(pkg_db)
    once = await pkg_db.fetchrow(
        "SELECT onay_actor, onaylandi_at, onay_kapsam_sha "
        "FROM social.package_rollback_plans WHERE incident_id = $1 AND package_id = $2",
        incident_id,
        aktif,
    )

    s2 = await _sub_sector(pkg_db)
    await _kokenli_paket(pkg_db, s2, version=1, status="archived", kural_surumu=KURAL_V2)
    await _kokenli_paket(pkg_db, s2, version=2, status="active")
    genis = await _affected(pkg_db)
    await runs.amend_rollback_plan(
        pkg_db, incident_id=incident_id, affected=genis, actor=ACTOR
    )

    sonra = await pkg_db.fetchrow(
        "SELECT onay_actor, onaylandi_at, onay_kapsam_sha "
        "FROM social.package_rollback_plans WHERE incident_id = $1 AND package_id = $2",
        incident_id,
        aktif,
    )
    assert dict(sonra) == dict(once)
    # Ama mühür artık BAYAT: bugünkü kapsam farklıdır.
    bugun = runs.incident_scope_sha(
        await pkg_db.fetch(
            "SELECT * FROM social.package_rollback_plans WHERE incident_id = $1",
            incident_id,
        )
    )
    assert sonra["onay_kapsam_sha"] != bugun


@pytest.mark.parametrize("aktor", ["", "   ", None])
async def test_amend_rollback_plan_refuses_blank_actor(pkg_db, aktor):
    await _bos_evren(pkg_db)
    incident_id, _aktif = await _onayli_olay(pkg_db)
    kume = await _affected(pkg_db)
    with pytest.raises(ValueError):
        await runs.amend_rollback_plan(
            pkg_db, incident_id=incident_id, affected=kume, actor=aktor
        )


async def test_membership_growth_after_execution_started_is_rejected(pkg_db):
    """Pencere KAPALIYSA hiçbir satır yazılmaz (fail-closed)."""
    await _bos_evren(pkg_db)
    incident_id, _aktif = await _onayli_olay(pkg_db)
    await pkg_db.execute(
        "UPDATE social.package_rollback_plans SET durum = 'tamamlandi' "
        "WHERE incident_id = $1",
        incident_id,
    )
    once = await pkg_db.fetch(
        "SELECT * FROM social.package_rollback_plans WHERE incident_id = $1", incident_id
    )

    s2 = await _sub_sector(pkg_db)
    await _kokenli_paket(pkg_db, s2, version=1, status="archived", kural_surumu=KURAL_V2)
    await _kokenli_paket(pkg_db, s2, version=2, status="active")
    genis = await _affected(pkg_db)

    with pytest.raises(runs.IncidentMembershipLocked):
        await runs.amend_rollback_plan(
            pkg_db, incident_id=incident_id, affected=genis, actor=ACTOR
        )

    sonra = await pkg_db.fetch(
        "SELECT * FROM social.package_rollback_plans WHERE incident_id = $1", incident_id
    )
    assert [dict(satir) for satir in sonra] == [dict(satir) for satir in once]


@pytest.mark.parametrize(
    "durum,pencere_acik",
    [("hedefsiz", True), ("tamamlandi", False), ("hata", False)],
)
async def test_membership_lock_window_opens_only_on_tamamlandi_or_hata(
    pkg_db, durum, pencere_acik
):
    """SINIR VAKASI: `hedefsiz` yürütme DEĞİLDİR — pencereyi KAPATMAZ.

    `hedefsiz` satır KURULARAK üretilir, sonradan çevrilerek DEĞİL: 036'nın
    `hedefsiz_butun` CHECK'i `durum='hedefsiz'` ile `target_version IS NULL`
    ikisini birbirine bağlar ve onaylanmış satırda `target_version` zaten
    değişmezdir (036 tetikleyicisi). Yani "çevirerek" kurmak veri katmanında
    TEMSİL EDİLEMEZ.
    """
    await _bos_evren(pkg_db)
    if durum == "hedefsiz":
        _sector_id, _aktif = await _geri_alinabilir(pkg_db, guvenli_arsiv=False)
        kume0 = await _affected(pkg_db)
        incident_id = await runs.build_rollback_plan(
            pkg_db, affected=kume0, actor=ACTOR
        )
        await runs.approve_incident_rollback(
            pkg_db, incident_id=incident_id, actor=ACTOR
        )
        assert (
            await pkg_db.fetchval(
                "SELECT durum FROM social.package_rollback_plans WHERE incident_id = $1",
                incident_id,
            )
            == "hedefsiz"
        )
    else:
        incident_id, _aktif = await _onayli_olay(pkg_db)
        await pkg_db.execute(
            "UPDATE social.package_rollback_plans SET durum = $2 WHERE incident_id = $1",
            incident_id,
            durum,
        )
    kume = await _affected(pkg_db)

    if pencere_acik:
        assert await runs.amend_rollback_plan(
            pkg_db, incident_id=incident_id, affected=kume, actor=ACTOR
        ) == (0, 0)
    else:
        with pytest.raises(runs.IncidentMembershipLocked):
            await runs.amend_rollback_plan(
                pkg_db, incident_id=incident_id, affected=kume, actor=ACTOR
            )


async def test_amend_writes_admin_event_when_a_sealed_row_is_dropped(pkg_db):
    """R-B kararının (b) ayağı: mühürlü satırın düşmesi SESSİZ kalmaz."""
    await _bos_evren(pkg_db)
    s1 = await _sub_sector(pkg_db)
    await _kokenli_paket(pkg_db, s1, version=1, status="archived", kural_surumu=KURAL_V2)
    a1, _ = await _kokenli_paket(pkg_db, s1, version=2, status="active")
    s2 = await _sub_sector(pkg_db)
    await _kokenli_paket(pkg_db, s2, version=1, status="archived", kural_surumu=KURAL_V2)
    await _kokenli_paket(pkg_db, s2, version=2, status="active")

    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)
    await runs.approve_incident_rollback(pkg_db, incident_id=incident_id, actor=ACTOR)

    await pkg_db.execute(
        "UPDATE social.sector_packages SET status = 'archived' WHERE id = $1", a1
    )
    dar = await _affected(pkg_db)
    assert await runs.amend_rollback_plan(
        pkg_db, incident_id=incident_id, affected=dar, actor=ACTOR
    ) == (0, 1)

    olay = await pkg_db.fetchrow(
        "SELECT kind, payload FROM social.admin_events WHERE kind = $1",
        runs.UYELIK_DARALTMA_OLAYI,
    )
    assert olay is not None
    assert olay["payload"]["incident_id"] == incident_id
    assert str(a1) in olay["payload"]["muhru_dusen_paketler"]


async def test_executed_plan_row_cannot_be_hard_deleted(pkg_db):
    """R-B kararının (a) ayağı — 036'nın DELETE kolu: YÜRÜTÜLMÜŞ satır SİLİNEMEZ.

    Aşırı kilitleme yok: `bekliyor` satır silinebilir (pozitif kontrol).
    """
    await _bos_evren(pkg_db)
    incident_id, aktif = await _onayli_olay(pkg_db)

    # Pozitif kontrol: bekleyen satır silinebilir.
    await pkg_db.execute(
        "DELETE FROM social.package_rollback_plans WHERE incident_id = $1", incident_id
    )
    await pkg_db.execute(
        "INSERT INTO social.package_rollback_plans "
        "(incident_id, package_id, observed_active_version, target_version, "
        " evidence_class, reason, durum) "
        "VALUES ($1, $2, 2, 1, 'kanitli', 'test', 'tamamlandi')",
        incident_id,
        aktif,
    )
    with pytest.raises(asyncpg.PostgresError):
        await pkg_db.execute(
            "DELETE FROM social.package_rollback_plans WHERE incident_id = $1",
            incident_id,
        )


# ═══ 14. Geri alma kanıtı (R11 · A4) ════════════════════════════════════════


async def test_build_rollback_evidence_reads_manager_approval_from_db(pkg_db):
    """POZİTİF KONTROL: iki boolean da DB'den okunur, jeton BASILIR."""
    await _bos_evren(pkg_db)
    incident_id, aktif = await _onayli_olay(pkg_db)

    kanit = await runs.build_rollback_evidence(
        pkg_db, incident_id=incident_id, package_id=aktif
    )

    assert type(kanit) is RollbackGateEvidence
    assert kanit.manager_approved is True
    assert kanit.katman1_passed is True
    assert kanit.incident_id == incident_id
    assert kanit.package_id == aktif
    assert len(kanit.provenance_token) == 64


async def test_build_rollback_evidence_mints_a_single_use_token(pkg_db):
    """Dönen kanıtın jetonu plan satırındakiyle AYNI ve HENÜZ HARCANMAMIŞ."""
    await _bos_evren(pkg_db)
    incident_id, aktif = await _onayli_olay(pkg_db)

    kanit = await runs.build_rollback_evidence(
        pkg_db, incident_id=incident_id, package_id=aktif
    )

    satir = await pkg_db.fetchrow(
        "SELECT kanit_jetonu, kanit_jetonu_parmakizi, kanit_jetonu_basildi_at, "
        "       kanit_jetonu_harcandi_at FROM social.package_rollback_plans "
        "WHERE incident_id = $1 AND package_id = $2",
        incident_id,
        aktif,
    )
    assert satir["kanit_jetonu"] == kanit.provenance_token
    assert satir["kanit_jetonu_basildi_at"] is not None
    assert satir["kanit_jetonu_harcandi_at"] is None
    assert satir["kanit_jetonu_parmakizi"] == lifecycle._evidence_fingerprint(kanit)


async def test_build_rollback_evidence_reads_katman1_from_target_run_attestation(pkg_db):
    """F18: `katman1_passed` HEDEF sürümü üreten koşunun tasdikinden okunur."""
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    _hedef, hedef_run = await _kokenli_paket(
        pkg_db, sector_id, version=1, status="archived", kural_surumu=KURAL_V2,
        katman1="FAIL",
    )
    await _kokenli_paket(pkg_db, sector_id, version=2, status="active")
    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)
    await runs.approve_incident_rollback(pkg_db, incident_id=incident_id, actor=ACTOR)
    aktif = kume.geri_alinacaklar[0]

    with pytest.raises(runs.RollbackEvidenceUnavailable):
        await runs.build_rollback_evidence(
            pkg_db, incident_id=incident_id, package_id=aktif
        )

    # Tasdik PASS'e çevrilince aynı çağrı GEÇER (pozitif kontrol).
    await runs.attest_katman1(
        pkg_db, run_id=hedef_run, kosum_kimligi="k1-2", sonuc="PASS", actor=ACTOR
    )
    kanit = await runs.build_rollback_evidence(
        pkg_db, incident_id=incident_id, package_id=aktif
    )
    assert kanit.katman1_passed is True


async def test_build_rollback_evidence_refuses_when_target_run_unprovable(pkg_db):
    """Hedef paketin koşusu okunamıyorsa kanıt KURULMAZ."""
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    _hedef, hedef_run = await _kokenli_paket(
        pkg_db, sector_id, version=1, status="archived", kural_surumu=KURAL_V2
    )
    await _kokenli_paket(pkg_db, sector_id, version=2, status="active")
    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)
    await runs.approve_incident_rollback(pkg_db, incident_id=incident_id, actor=ACTOR)
    await pkg_db.execute(
        "UPDATE social.sector_packages SET run_id = NULL WHERE sector_id = $1 "
        "AND version = 1",
        sector_id,
    )

    with pytest.raises(runs.RollbackEvidenceUnavailable):
        await runs.build_rollback_evidence(
            pkg_db, incident_id=incident_id, package_id=kume.geri_alinacaklar[0]
        )


async def test_build_rollback_evidence_refuses_when_plan_row_unapproved(pkg_db):
    """NEGATİF KONTROL: onaylanmamış satır için kanıt kurulmaz."""
    await _bos_evren(pkg_db)
    _sector_id, aktif = await _geri_alinabilir(pkg_db)
    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)

    with pytest.raises(runs.RollbackEvidenceUnavailable):
        await runs.build_rollback_evidence(
            pkg_db, incident_id=incident_id, package_id=aktif
        )


@pytest.mark.parametrize("dolu", ["onay_actor", "onaylandi_at", "onay_kapsam_sha"])
async def test_build_rollback_evidence_true_only_when_all_three_approval_fields_set(
    pkg_db, dolu
):
    """ÜÇ koşul BİRDEN — ve KISMİ mühür VERİ KATMANINDA temsil EDİLEMEZ.

    İki iddia birlikte kapatır: (a) servis kapısı mühürsüz satırda kanıt
    kurmaz; (b) "üçlünün yalnız biri dolu" hâli 036'nın
    `num_nonnulls(...) IN (0,3)` CHECK'i yüzünden yazılamaz — yani servis
    kapısının kaçırabileceği bir ara hâl YOKTUR. Mührü SİLİP tek alan yazmak da
    yol değildir: tetikleyici dolu → BOŞ geçişini reddeder (R-C).
    """
    await _bos_evren(pkg_db)
    _sector_id, aktif = await _geri_alinabilir(pkg_db)
    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)

    # (a) mühürsüz satır → kanıt kurulmaz
    with pytest.raises(runs.RollbackEvidenceUnavailable):
        await runs.build_rollback_evidence(
            pkg_db, incident_id=incident_id, package_id=aktif
        )

    # (b) tek alan dolu bir mühür VERİ KATMANINDA yazılamaz
    degerler = {
        "onay_actor": "'x'",
        "onaylandi_at": "now()",
        "onay_kapsam_sha": "repeat('a', 64)",
    }
    with pytest.raises(asyncpg.PostgresError):
        await pkg_db.execute(
            f"UPDATE social.package_rollback_plans SET {dolu} = {degerler[dolu]} "
            "WHERE incident_id = $1",
            incident_id,
        )


async def test_build_rollback_evidence_accepts_unchanged_scope(pkg_db):
    """POZİTİF KONTROL: kapsam değişmediyse kanıt kurulur."""
    await _bos_evren(pkg_db)
    incident_id, aktif = await _onayli_olay(pkg_db)
    kanit = await runs.build_rollback_evidence(
        pkg_db, incident_id=incident_id, package_id=aktif
    )
    assert kanit.manager_approved is True


async def test_build_rollback_evidence_refuses_when_incident_scope_grew(pkg_db):
    """Onaydan SONRA olaya yeni satır eklendi → mühür BAYAT → RED."""
    await _bos_evren(pkg_db)
    incident_id, aktif = await _onayli_olay(pkg_db)

    s2 = await _sub_sector(pkg_db)
    await _kokenli_paket(pkg_db, s2, version=1, status="archived", kural_surumu=KURAL_V2)
    await _kokenli_paket(pkg_db, s2, version=2, status="active")
    genis = await _affected(pkg_db)
    await runs.amend_rollback_plan(
        pkg_db, incident_id=incident_id, affected=genis, actor=ACTOR
    )

    with pytest.raises(runs.RollbackEvidenceUnavailable):
        await runs.build_rollback_evidence(
            pkg_db, incident_id=incident_id, package_id=aktif
        )


async def test_build_rollback_evidence_refuses_when_incident_scope_shrank(pkg_db):
    """Onaylı bir satır ÜYELİKTEN ÇIKARILDI → mühür BAYAT → RED.

    Satırın `tamamlandi`'ya geçmesi küçülme SAYILMAZ (o ayrı testtedir).
    """
    await _bos_evren(pkg_db)
    s1 = await _sub_sector(pkg_db)
    await _kokenli_paket(pkg_db, s1, version=1, status="archived", kural_surumu=KURAL_V2)
    a1, _ = await _kokenli_paket(pkg_db, s1, version=2, status="active")
    s2 = await _sub_sector(pkg_db)
    await _kokenli_paket(pkg_db, s2, version=1, status="archived", kural_surumu=KURAL_V2)
    a2, _ = await _kokenli_paket(pkg_db, s2, version=2, status="active")

    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)
    await runs.approve_incident_rollback(pkg_db, incident_id=incident_id, actor=ACTOR)

    await pkg_db.execute(
        "UPDATE social.sector_packages SET status = 'archived' WHERE id = $1", a1
    )
    dar = await _affected(pkg_db)
    assert await runs.amend_rollback_plan(
        pkg_db, incident_id=incident_id, affected=dar, actor=ACTOR
    ) == (0, 1)

    with pytest.raises(runs.RollbackEvidenceUnavailable):
        await runs.build_rollback_evidence(
            pkg_db, incident_id=incident_id, package_id=a2
        )


async def test_build_rollback_evidence_refuses_whitespace_padded_scope_sha(pkg_db):
    """A4 #7: karşılaştırma NORMALİZASYONSUZ — boşluk-sarmalı mühür BAYATTIR."""
    await _bos_evren(pkg_db)
    incident_id, aktif = await _onayli_olay(pkg_db)
    mevcut = await pkg_db.fetchval(
        "SELECT onay_kapsam_sha FROM social.package_rollback_plans "
        "WHERE incident_id = $1 AND package_id = $2",
        incident_id,
        aktif,
    )
    await pkg_db.execute(
        "UPDATE social.package_rollback_plans SET onay_kapsam_sha = $3 "
        "WHERE incident_id = $1 AND package_id = $2",
        incident_id,
        aktif,
        f" {mevcut} ",
    )

    with pytest.raises(runs.RollbackEvidenceUnavailable):
        await runs.build_rollback_evidence(
            pkg_db, incident_id=incident_id, package_id=aktif
        )


async def test_approve_incident_treats_whitespace_padded_scope_sha_as_stale(pkg_db):
    """A4 #8: `strip()`'li karşılaştırma bayat mührü TAZE sanardı — sanmıyor."""
    await _bos_evren(pkg_db)
    incident_id, aktif = await _onayli_olay(pkg_db)
    mevcut = await pkg_db.fetchval(
        "SELECT onay_kapsam_sha FROM social.package_rollback_plans "
        "WHERE incident_id = $1 AND package_id = $2",
        incident_id,
        aktif,
    )
    await pkg_db.execute(
        "UPDATE social.package_rollback_plans SET onay_kapsam_sha = $3, "
        "onay_actor = 'eski@otomaix' WHERE incident_id = $1 AND package_id = $2",
        incident_id,
        aktif,
        f" {mevcut} ",
    )

    damgalanan = await runs.approve_incident_rollback(
        pkg_db, incident_id=incident_id, actor=ACTOR
    )

    assert damgalanan == 1
    yeni = await pkg_db.fetchrow(
        "SELECT onay_actor, onay_kapsam_sha FROM social.package_rollback_plans "
        "WHERE incident_id = $1 AND package_id = $2",
        incident_id,
        aktif,
    )
    assert yeni["onay_actor"] == ACTOR
    assert yeni["onay_kapsam_sha"] == mevcut


def test_executor_never_constructs_evidence_from_literals():
    """YAPISAL: `RollbackGateEvidence(` YALNIZ `build_rollback_evidence` gövdesinde."""
    govde = _fonksiyon_govdesi(RUNS_KAYNAK, "build_rollback_evidence")
    assert RUNS_KAYNAK.count("RollbackGateEvidence(") == 1
    assert "RollbackGateEvidence(" in govde


# ═══ 15. Yürütücü — tekrar güvenliği ve CAS ═════════════════════════════════


async def test_two_row_incident_completes_end_to_end(pkg_db):
    """A3: birinci satır tamamlandıktan SONRA ikincinin kanıtı da KURULUR."""
    await _bos_evren(pkg_db)
    aktifler = []
    for _ in range(2):
        sector_id = await _sub_sector(pkg_db)
        await _kokenli_paket(
            pkg_db, sector_id, version=1, status="archived", kural_surumu=KURAL_V2
        )
        aktif, _ = await _kokenli_paket(pkg_db, sector_id, version=2, status="active")
        aktifler.append(aktif)

    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)
    await runs.approve_incident_rollback(pkg_db, incident_id=incident_id, actor=ACTOR)
    ilk_kapsam = await pkg_db.fetchval(
        "SELECT onay_kapsam_sha FROM social.package_rollback_plans "
        "WHERE incident_id = $1 LIMIT 1",
        incident_id,
    )

    rapor = await runs.execute_rollback_plan(
        pkg_db, incident_id=incident_id, actor=ACTOR
    )

    assert set(rapor.tamamlandi) == set(aktifler), rapor
    assert rapor.hata == ()
    # Tamamlanma kapsamı DEĞİŞTİRMEZ: ikinci satırın mührü birincininkiyle AYNI.
    shalar = await pkg_db.fetch(
        "SELECT onay_kapsam_sha FROM social.package_rollback_plans WHERE incident_id = $1",
        incident_id,
    )
    assert {satir["onay_kapsam_sha"] for satir in shalar} == {ilk_kapsam}
    for paket in aktifler:
        assert (
            await pkg_db.fetchval(
                "SELECT status FROM social.sector_packages WHERE id = $1", paket
            )
            == "archived"
        )


async def test_execute_plan_skips_completed_entries_on_retry(pkg_db):
    """TEKRAR GÜVENLİ: tamamlanmış satır ATLANIR — ikinci geri alma YOK."""
    await _bos_evren(pkg_db)
    incident_id, aktif = await _onayli_olay(pkg_db)
    ilk = await runs.execute_rollback_plan(pkg_db, incident_id=incident_id, actor=ACTOR)
    assert ilk.tamamlandi == (aktif,)

    olay_sayisi = await pkg_db.fetchval(
        "SELECT count(*) FROM social.package_events WHERE event_type = 'rollback'"
    )

    ikinci = await runs.execute_rollback_plan(
        pkg_db, incident_id=incident_id, actor=ACTOR
    )

    assert ikinci.zaten_tamamlandi == (aktif,)
    assert ikinci.tamamlandi == ()
    assert (
        await pkg_db.fetchval(
            "SELECT count(*) FROM social.package_events WHERE event_type = 'rollback'"
        )
        == olay_sayisi
    )


async def test_partial_failure_then_retry_reuses_the_same_approval(pkg_db):
    """Birinci satır `hata`; tekrar koşumda KALAN satır AYNI onayla yürür.

    Yeni onay İSTENMEZ ve yürütücü onay yüzeyini HİÇ çağırmaz — bu yapısal
    olarak da ölçülür (`execute_rollback_plan` gövdesinde
    `approve_incident_rollback` adı geçmez).
    """
    await _bos_evren(pkg_db)
    aktifler = []
    for _ in range(2):
        sector_id = await _sub_sector(pkg_db)
        await _kokenli_paket(
            pkg_db, sector_id, version=1, status="archived", kural_surumu=KURAL_V2
        )
        aktif, _ = await _kokenli_paket(pkg_db, sector_id, version=2, status="active")
        aktifler.append(aktif)

    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)
    await runs.approve_incident_rollback(pkg_db, incident_id=incident_id, actor=ACTOR)
    kapsam_once = await pkg_db.fetchval(
        "SELECT onay_kapsam_sha FROM social.package_rollback_plans "
        "WHERE incident_id = $1 LIMIT 1",
        incident_id,
    )

    ilk_paket = sorted(aktifler, key=str)[0]
    await pkg_db.execute(
        "UPDATE social.package_rollback_plans SET durum = 'hata', reason = 'gecici' "
        "WHERE incident_id = $1 AND package_id = $2",
        incident_id,
        ilk_paket,
    )

    rapor = await runs.execute_rollback_plan(
        pkg_db, incident_id=incident_id, actor=ACTOR
    )

    kalan = [paket for paket in aktifler if paket != ilk_paket]
    assert rapor.tamamlandi == tuple(kalan)
    assert (
        await pkg_db.fetchval(
            "SELECT onay_kapsam_sha FROM social.package_rollback_plans "
            "WHERE incident_id = $1 AND package_id = $2",
            incident_id,
            kalan[0],
        )
        == kapsam_once
    )
    govde = _fonksiyon_govdesi(RUNS_KAYNAK, "execute_rollback_plan")
    assert "approve_incident_rollback" not in govde


async def test_execute_plan_cas_rejects_when_active_version_moved(pkg_db):
    """Karşılaştır-ve-uygula: aktif sürüm plandan beri kaydıysa satır `hata`."""
    await _bos_evren(pkg_db)
    sector_id, aktif = await _geri_alinabilir(pkg_db)
    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)
    await runs.approve_incident_rollback(pkg_db, incident_id=incident_id, actor=ACTOR)

    # GERÇEK aktif sürüm plandan sonra kaydı. Plan satırına DOKUNULMAZ —
    # onaylanmış satırın `observed_active_version`'ı zaten değişmezdir (036
    # tetikleyicisi), yani kayma yalnız paket tarafında temsil edilebilir.
    await pkg_db.execute(
        "UPDATE social.sector_packages SET version = 99 WHERE id = $1", aktif
    )

    rapor = await runs.execute_rollback_plan(
        pkg_db, incident_id=incident_id, actor=ACTOR
    )

    assert rapor.hata == (aktif,)
    assert rapor.tamamlandi == ()
    satir = await pkg_db.fetchrow(
        "SELECT durum, reason FROM social.package_rollback_plans WHERE incident_id = $1",
        incident_id,
    )
    assert satir["durum"] == "hata"
    assert "karşılaştır-ve-uygula" in satir["reason"]
    assert (
        await pkg_db.fetchval(
            "SELECT status FROM social.sector_packages WHERE id = $1", aktif
        )
        == "active"
    )


async def test_executor_marks_row_hata_when_evidence_unavailable(pkg_db):
    """Kanıt kurulamazsa satır `durum='hata'` + `reason` ile KAPANIR."""
    await _bos_evren(pkg_db)
    _sector_id, aktif = await _geri_alinabilir(pkg_db)
    kume = await _affected(pkg_db)
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)
    # Onay YOK — kanıt kurulamaz.

    rapor = await runs.execute_rollback_plan(
        pkg_db, incident_id=incident_id, actor=ACTOR
    )

    assert rapor.hata == (aktif,)
    satir = await pkg_db.fetchrow(
        "SELECT durum, reason FROM social.package_rollback_plans WHERE incident_id = $1",
        incident_id,
    )
    assert satir["durum"] == "hata"
    assert "yönetici onayı YOK" in satir["reason"]


async def test_membership_growth_before_execution_then_reapproval_completes(pkg_db):
    """A3'ün uçtan uca yolu: büyüme → bayat mühür → yeniden mühürleme → biter."""
    await _bos_evren(pkg_db)
    incident_id, a1 = await _onayli_olay(pkg_db)

    s2 = await _sub_sector(pkg_db)
    await _kokenli_paket(pkg_db, s2, version=1, status="archived", kural_surumu=KURAL_V2)
    a2, _ = await _kokenli_paket(pkg_db, s2, version=2, status="active")
    genis = await _affected(pkg_db)

    assert await runs.amend_rollback_plan(
        pkg_db, incident_id=incident_id, affected=genis, actor=ACTOR
    ) == (1, 0)

    with pytest.raises(runs.RollbackEvidenceUnavailable):
        await runs.build_rollback_evidence(
            pkg_db, incident_id=incident_id, package_id=a1
        )

    assert await runs.approve_incident_rollback(
        pkg_db, incident_id=incident_id, actor=ACTOR
    ) == 2

    rapor = await runs.execute_rollback_plan(
        pkg_db, incident_id=incident_id, actor=ACTOR
    )
    assert set(rapor.tamamlandi) == {a1, a2}


async def test_reapproval_restamps_stale_rows_and_leaves_fresh_rows_untouched(pkg_db):
    """Bayat satır YENİDEN mühürlenir; aynı koşumda İKİ KEZ mühürlenen satır YOK."""
    await _bos_evren(pkg_db)
    incident_id, a1 = await _onayli_olay(pkg_db)

    s2 = await _sub_sector(pkg_db)
    await _kokenli_paket(pkg_db, s2, version=1, status="archived", kural_surumu=KURAL_V2)
    a2, _ = await _kokenli_paket(pkg_db, s2, version=2, status="active")
    genis = await _affected(pkg_db)
    await runs.amend_rollback_plan(
        pkg_db, incident_id=incident_id, affected=genis, actor=ACTOR
    )

    # Yeni satır HİÇ mühürlenmemiş; eski satırın mührü BAYAT.
    yeni_satir = await pkg_db.fetchrow(
        "SELECT onay_actor FROM social.package_rollback_plans "
        "WHERE incident_id = $1 AND package_id = $2",
        incident_id,
        a2,
    )
    assert yeni_satir["onay_actor"] is None

    damgalanan = await runs.approve_incident_rollback(
        pkg_db, incident_id=incident_id, actor="ikinci@otomaix"
    )

    assert damgalanan == 2
    shalar = await pkg_db.fetch(
        "SELECT package_id, onay_actor, onay_kapsam_sha "
        "FROM social.package_rollback_plans WHERE incident_id = $1",
        incident_id,
    )
    assert {satir["onay_actor"] for satir in shalar} == {"ikinci@otomaix"}
    assert len({satir["onay_kapsam_sha"] for satir in shalar}) == 1


# ═══ 16. Olay kilidi (A1(b)) ════════════════════════════════════════════════


def test_incident_lock_name_is_the_single_prefix():
    """YAPISAL: `pg_advisory_xact_lock` YALNIZ `_lock_incident` gövdesinde geçer."""
    assert RUNS_KAYNAK.count("pg_advisory_xact_lock") == 1
    govde = _fonksiyon_govdesi(RUNS_KAYNAK, "_lock_incident")
    assert "pg_advisory_xact_lock" in govde
    assert RUNS_KAYNAK.count("_OLAY_KILIT_ONEKI") == 2  # tanım + tek kullanım


async def test_incident_lock_is_reentrant_within_one_transaction(pkg_db):
    """Dört yolun KOŞULSUZ almasının önkoşulu: aynı işlemde ikinci çağrı döner."""
    async with pkg_db.transaction():
        await runs._lock_incident(pkg_db, "olay-yeniden-giris")
        await runs._lock_incident(pkg_db, "olay-yeniden-giris")


def test_evidence_construction_and_spend_share_one_transaction():
    """YAPISAL: kanıt kurulumu ve geçiş AYNI işlem bloğunda ve KİLİDİN ALTINDA.

    Fix turu 1'de (F2) deneme bir KAYIT NOKTASINA (iç `db.transaction()`) alındı;
    olay kilidini alan blok artık onun DIŞINDADIR. Ölçü buna göre güncellendi ve
    ZAYIFLAMADI: iki çağrının aynı blokta olması KORUNUR, üstüne o bloğu SARAN
    zincirde kilidi İLK ifade yapan bir işlem bloğu ARANIR — yani kanıt ile
    harcamanın arasında kilidin düştüğü bir an yoktur.
    """
    govde = _fonksiyon_govdesi(RUNS_KAYNAK, "execute_rollback_plan")
    agac = ast.parse(govde)

    ebeveyn: dict[int, ast.AST] = {}
    for dugum in ast.walk(agac):
        for cocuk in ast.iter_child_nodes(dugum):
            ebeveyn[id(cocuk)] = dugum

    def _cagrilar(dugum: ast.AST) -> set[str]:
        return {
            alt.func.attr
            for alt in ast.walk(dugum)
            if isinstance(alt, ast.Call) and isinstance(alt.func, ast.Attribute)
        } | {
            alt.func.id
            for alt in ast.walk(dugum)
            if isinstance(alt, ast.Call) and isinstance(alt.func, ast.Name)
        }

    bulundu = False
    for dugum in ast.walk(agac):
        if not isinstance(dugum, ast.AsyncWith):
            continue
        if not {"build_rollback_evidence", "rollback_package"} <= _cagrilar(dugum):
            continue
        bulundu = True
        # Kilit, bu bloğun KENDİSİNİN ya da onu saran bir işlem bloğunun İLK
        # ifadesidir — arada kilitsiz bir katman YOKTUR.
        kilitli = False
        aday: ast.AST | None = dugum
        while aday is not None:
            if isinstance(aday, ast.AsyncWith) and "_lock_incident" in ast.dump(
                aday.body[0]
            ):
                kilitli = True
                break
            aday = ebeveyn.get(id(aday))
        assert kilitli, ast.dump(dugum)
    assert bulundu, "iki çağrı aynı transaction bloğunda bulunamadı"


async def test_evidence_and_spend_are_serialised_by_the_incident_lock(test_db_setup):
    """A1(b)'nin ANA İSPATI — DETERMİNİSTİK ARALIK TESTİ.

    Bağlantı A olay kilidini alır ve bir satırı `tamamlandi` yapar ama COMMIT
    ETMEZ. Bağlantı B `amend_rollback_plan` çağırır: kilitte BEKLER (bu, uyku
    ile değil `pg_locks` üzerinden ÖLÇÜLÜR — bekleyen kilit isteği katalogda
    görünür). A commit edince B koşar ve yürütme başladığı için
    `IncidentMembershipLocked` alır.

    KONTROL KOLU: A hiç kilit tutmazken aynı B çağrısı ANINDA döner — yani test
    kilidin VARLIĞINI ölçer, prose'unu değil.
    """
    url = _require_test_database(test_db_setup)
    kurulum = await asyncpg.connect(url)
    await _init_connection(kurulum)
    a_baglanti = await asyncpg.connect(url)
    await _init_connection(a_baglanti)
    b_baglanti = await asyncpg.connect(url)
    await _init_connection(b_baglanti)
    gozlemci = await asyncpg.connect(url)
    sektorler: list = []
    incident_id = None
    try:
        sector_id = await _sub_sector(kurulum)
        sektorler.append(sector_id)
        await _kokenli_paket(
            kurulum, sector_id, version=1, status="archived", kural_surumu=KURAL_V2
        )
        await _kokenli_paket(kurulum, sector_id, version=2, status="active")
        kume = await runs.affected_packages(
            kurulum,
            engine_version=MOTOR_SURUM,
            engine_config_sha=CONFIG_SHA,
            kural_kimligi=KURAL,
            kural_surumu=KURAL_V1,
        )
        incident_id = await runs.build_rollback_plan(
            kurulum, affected=kume, actor=ACTOR
        )
        await runs.approve_incident_rollback(
            kurulum, incident_id=incident_id, actor=ACTOR
        )

        # ── KONTROL KOLU: kilit tutulmuyorken B ANINDA döner.
        assert await asyncio.wait_for(
            runs.amend_rollback_plan(
                b_baglanti, incident_id=incident_id, affected=kume, actor=ACTOR
            ),
            timeout=10,
        ) == (0, 0)

        # ── ARALIK: A kilidi alır, yürütmeyi başlatır, COMMIT ETMEZ.
        a_tx = a_baglanti.transaction()
        await a_tx.start()
        await runs._lock_incident(a_baglanti, incident_id)
        await a_baglanti.execute(
            "UPDATE social.package_rollback_plans SET durum = 'tamamlandi' "
            "WHERE incident_id = $1",
            incident_id,
        )

        b_gorev = asyncio.create_task(
            runs.amend_rollback_plan(
                b_baglanti, incident_id=incident_id, affected=kume, actor=ACTOR
            )
        )

        # B'nin GERÇEKTEN kilitte beklediği katalogdan ölçülür (uyku değil).
        for _ in range(200):
            bekleyen = await gozlemci.fetchval(
                "SELECT count(*) FROM pg_locks WHERE locktype = 'advisory' "
                "AND NOT granted"
            )
            if bekleyen:
                break
            await asyncio.sleep(0.01)
        assert bekleyen, "B kilitte beklemedi — olay kilidi yük taşımıyor"
        assert not b_gorev.done()

        await a_tx.commit()

        with pytest.raises(runs.IncidentMembershipLocked):
            await asyncio.wait_for(b_gorev, timeout=10)
    finally:
        for baglanti in (a_baglanti, b_baglanti):
            await baglanti.close()
        await gozlemci.close()
        if incident_id is not None:
            await kurulum.execute(
                "UPDATE social.package_rollback_plans SET durum = 'bekliyor', "
                "kanit_jetonu_harcandi_at = NULL WHERE incident_id = $1",
                incident_id,
            )
            await kurulum.execute(
                "DELETE FROM social.package_rollback_plans WHERE incident_id = $1",
                incident_id,
            )
        for sector_id in sektorler:
            await _committed_sektor_sil(kurulum, sector_id)
        await kurulum.close()


@pytest.mark.parametrize(
    "yol", ["approve_incident_rollback", "build_rollback_evidence"]
)
async def test_remaining_lock_paths_wait_on_the_incident_lock(test_db_setup, yol):
    """B1 (fix turu B): KAPISIZ kalan İKİ yol için AYIRT EDEN çekişme ölçümü.

    `_lock_incident`'ın üretimde ALTI çağrı yeri var. `amend_rollback_plan`'in
    davranışsal ispatı (`test_evidence_and_spend_are_serialised_by_the_incident_lock`)
    ve `execute_rollback_plan`'in yapısal kapıları vardı; bu iki yolun HİÇBİR
    kapısı YOKTU — kilit satırı silinse tüm takım YEŞİL kalıyordu.

    ÖLÇÜM (uyku DEĞİL, katalog): bağlantı A YALNIZ olay kilidini alır — hiçbir
    satır kilidi TUTMAZ, hiçbir satırı DEĞİŞTİRMEZ. Bu bilinçlidir: kilit satırı
    silindiğinde B'yi bekletecek BAŞKA hiçbir şey kalmasın, yani beklemenin TEK
    açıklaması olay kilidi olsun. B'nin gerçekten beklediği `pg_locks`
    katalogundan (`locktype='advisory' AND NOT granted`) okunur.

    KONTROL KOLU çekişmeden SONRA koşar: kilit artık tutulmazken AYNI çağrı
    ANINDA döner — yani test kilidin VARLIĞINI ölçer, prose'unu değil.

    Olay ONAYLANMAZ. Gerekçe ölçülmüştür: onaylı bir olayda
    `build_rollback_evidence` `mint_evidence_token`'a iner ve O da `_lock_incident`
    çağırır — kendi kilit satırı silinse bile B orada beklerdi ve test AYIRT
    ETMEZDİ. Onaysız olayda çağrı, plan satırını okuduktan hemen sonra
    `RollbackEvidenceUnavailable` ile döner; yani kilit gerçekten İLK iş olmak
    ZORUNDADIR, yoksa hiç beklemez.
    """
    url = _require_test_database(test_db_setup)
    kurulum = await asyncpg.connect(url)
    await _init_connection(kurulum)
    a_baglanti = await asyncpg.connect(url)
    await _init_connection(a_baglanti)
    b_baglanti = await asyncpg.connect(url)
    await _init_connection(b_baglanti)
    gozlemci = await asyncpg.connect(url)
    sektorler: list = []
    incident_id = None
    try:
        sector_id = await _sub_sector(kurulum)
        sektorler.append(sector_id)
        await _kokenli_paket(
            kurulum, sector_id, version=1, status="archived", kural_surumu=KURAL_V2
        )
        aktif, _ = await _kokenli_paket(
            kurulum, sector_id, version=2, status="active"
        )
        kume = await runs.affected_packages(
            kurulum,
            engine_version=MOTOR_SURUM,
            engine_config_sha=CONFIG_SHA,
            kural_kimligi=KURAL,
            kural_surumu=KURAL_V1,
        )
        assert aktif in kume.geri_alinacaklar
        incident_id = await runs.build_rollback_plan(
            kurulum, affected=kume, actor=ACTOR
        )

        async def _b_cagrisi():
            if yol == "approve_incident_rollback":
                return await runs.approve_incident_rollback(
                    b_baglanti, incident_id=incident_id, actor=ACTOR
                )
            async with b_baglanti.transaction():
                return await runs.build_rollback_evidence(
                    b_baglanti, incident_id=incident_id, package_id=aktif
                )

        # ── ÇEKİŞME: A kilidi alır (BAŞKA HİÇBİR ŞEY yapmaz), COMMIT ETMEZ.
        a_tx = a_baglanti.transaction()
        await a_tx.start()
        await runs._lock_incident(a_baglanti, incident_id)

        b_gorev = asyncio.create_task(_b_cagrisi())
        for _ in range(200):
            bekleyen = await gozlemci.fetchval(
                "SELECT count(*) FROM pg_locks WHERE locktype = 'advisory' "
                "AND NOT granted"
            )
            if bekleyen:
                break
            await asyncio.sleep(0.01)
        assert bekleyen, f"{yol} olay kilidini BEKLEMEDİ — kilit yük taşımıyor"
        assert not b_gorev.done()

        await a_tx.commit()

        if yol == "approve_incident_rollback":
            assert await asyncio.wait_for(b_gorev, timeout=10) == 1
        else:
            with pytest.raises(runs.RollbackEvidenceUnavailable):
                await asyncio.wait_for(b_gorev, timeout=10)

        # ── KONTROL KOLU: kilit tutulmuyorken AYNI çağrı ANINDA döner.
        if yol == "approve_incident_rollback":
            assert await asyncio.wait_for(_b_cagrisi(), timeout=10) == 0
        else:
            with pytest.raises(runs.RollbackEvidenceUnavailable):
                await asyncio.wait_for(_b_cagrisi(), timeout=10)
    finally:
        for baglanti in (a_baglanti, b_baglanti):
            await baglanti.close()
        await gozlemci.close()
        if incident_id is not None:
            await kurulum.execute(
                "UPDATE social.package_rollback_plans SET durum = 'bekliyor', "
                "kanit_jetonu_harcandi_at = NULL WHERE incident_id = $1",
                incident_id,
            )
            await kurulum.execute(
                "DELETE FROM social.package_rollback_plans WHERE incident_id = $1",
                incident_id,
            )
        for sector_id in sektorler:
            await _committed_sektor_sil(kurulum, sector_id)
        await kurulum.close()



def _lock_incident_cagiranlari() -> set[str]:
    """`runs.py`'de `_lock_incident` ÇAĞIRAN her fonksiyonun adı — ÜRETİLİR.

    Küme ELLE YAZILMAZ: modülün kaynağı AST ile ayrıştırılır ve her çağrı, onu
    saran EN İÇTEKİ fonksiyon tanımının adına bağlanır. `_lock_incident`'ın
    kendi tanımı kümenin dışındadır.

    **Çözünürlük sınırı:** dönen şey fonksiyon ADLARIDIR, çağrı yerleri değil —
    aynı fonksiyondaki iki çağrı TEK girdiye çöker. Tüketicisinin ne yakalayıp
    ne yakalamadığı `test_every_incident_lock_call_site_is_gated_or_explicitly_excepted`
    docstring'inde yazılıdır.
    """
    agac = ast.parse(RUNS_KAYNAK)
    cagiranlar: set[str] = set()

    def _gez(dugum: ast.AST, kapsam: str | None) -> None:
        for cocuk in ast.iter_child_nodes(dugum):
            if isinstance(cocuk, (ast.FunctionDef, ast.AsyncFunctionDef)):
                _gez(cocuk, cocuk.name)
                continue
            if isinstance(cocuk, ast.Call):
                hedef = cocuk.func
                ad = (
                    hedef.id
                    if isinstance(hedef, ast.Name)
                    else hedef.attr
                    if isinstance(hedef, ast.Attribute)
                    else None
                )
                if ad == "_lock_incident" and kapsam is not None:
                    cagiranlar.add(kapsam)
            _gez(cocuk, kapsam)

    _gez(agac, None)
    return cagiranlar - {"_lock_incident"}


# Olay kilidini alan ve KAPISI OLAN yollar: ad → kapıyı koşan testin adı.
KILIT_KAPISI_OLAN_YOLLAR: Mapping[str, str] = MappingProxyType(
    {
        "amend_rollback_plan": (
            "test_evidence_and_spend_are_serialised_by_the_incident_lock — "
            "pg_locks'tan ölçülen davranışsal çekişme"
        ),
        "approve_incident_rollback": (
            "test_remaining_lock_paths_wait_on_the_incident_lock"
            "[approve_incident_rollback] — pg_locks'tan ölçülen çekişme"
        ),
        "build_rollback_evidence": (
            "test_remaining_lock_paths_wait_on_the_incident_lock"
            "[build_rollback_evidence] — pg_locks'tan ölçülen çekişme"
        ),
        "execute_rollback_plan": (
            "test_evidence_construction_and_spend_share_one_transaction — "
            "kilidin kanıt+harcama bloğunu sardığının yapısal kapısı"
        ),
    }
)

# Kapısı OLAN yollar: ad → o yolu koruyan testin ADI. Değerler DÜZ METİNDİR,
# çözülen referans DEĞİL: adı geçen test silinirse aşağıdaki kapı bunu GÖRMEZ.
# Kapısı OLMAYAN yollar: ad → NEDEN kapı kurulamadığının ÖLÇÜLMÜŞ gerekçesi.
# Gerekçe kodda YORUM değil VERİ olarak yaşar; bir gün bu koşullar değişirse
# (ör. `mint_evidence_token`'a ikinci bir doğrudan çağıran eklenirse) gerekçenin
# bayatladığı okunabilsin diye.
KILIT_KAPISI_OLMAYAN_YOLLAR: Mapping[str, str] = MappingProxyType(
    {
        "build_rollback_plan": (
            "kilidi, iki satır önce KENDİ ürettiği YEPYENİ uuid4 olay kimliği "
            "üzerine alır; kimliği o an başka kimse bilemez ve satırlar aynı "
            "işlemde yazılır → çekişme YAPISAL olarak imkânsız, kilit bugün "
            "yük taşımaz"
        ),
        "mint_evidence_token": (
            "geri alma dalına bugün TEK giriş, kilidi ZATEN almış olan "
            "`build_rollback_evidence`'tan; kilit yeniden girilebilir "
            "(test_incident_lock_is_reentrant_within_one_transaction) → koruma "
            "çağırandan gelir; ayrıca `FOR UPDATE` satır kilidi ve "
            "`_require_transaction` ayrıca durur"
        ),
    }
)


def test_every_incident_lock_call_site_is_gated_or_explicitly_excepted():
    """B5: kilit KAPSAMASI ELLE LİSTEDEN değil ÜRETİLMİŞ KÜMEDEN doğrulanır.

    Bir üstteki iki çekişme testi `_lock_incident`'ın İKİ çağrı yerini ELLE
    sayıyordu. Zayıflık testlerin kendisinde değil LİSTENİN ELLE OLMASINDAYDI:
    yarın `_lock_incident` alan yeni bir fonksiyon eklenirse hiçbir şey KIRMIZI
    olmazdı — kapsama sessizce düşerdi.

    Bu kapı çağıran FONKSİYON ADLARINI `runs.py`'nin AST'sinden ÜRETİR ve iki
    AÇIK sözlüğe karşı İKİ YÖNLÜ eşitler: kapısı olanlar ve gerekçesiyle
    istisna edilenler.

    **NE YAKALAR:** `_lock_incident` çağıran YENİ BİR FONKSİYON beyan edilmeden
    eklenirse KIRMIZI olur; beyan edilen bir fonksiyon artık kilit ALMIYORSA
    (bayatlamış girdi) yine KIRMIZI olur. İkisi de mutasyonla ölçüldü.

    **NE YAKALAMAZ — kapsam sınırı, kusur değil (kapanış-doğrulama turu 2026-09-08
    bunu bulgu olarak çıkardı, açıklama gerçeğe indirildi):**

      1. Kimlik FONKSİYON ADIDIR, çağrı yeri DEĞİL. `set[str]` olduğu için
         ZATEN BEYAN EDİLMİŞ bir fonksiyona eklenen İKİNCİ bir `_lock_incident`
         çağrısı kümeyi değiştirmez → kapı yeşil kalır. Özellikle
         `mint_evidence_token`'ın istisna gerekçesi YALNIZ geri alma dalı için
         ölçülmüştür; o fonksiyona başka koşulda ikinci bir kilit çağrısı
         eklenirse gerekçe kapsamaz ama bu kapı susar.
      2. `KILIT_KAPISI_OLAN_YOLLAR` değerleri test ADLARIDIR — DÜZ METİN, çözülen
         referans DEĞİL. Adı geçen koruma testlerinden biri silinir ya da yeniden
         adlandırılırsa bu kapı YEŞİL kalır.

    Yani bu kapı KAPSAMA MUHASEBESİ tutar; bir kilidin gerçekten yük taşıdığını
    ya da onu koruyan testin hâlâ var olduğunu KANITLAMAZ. O kanıt, adı geçen
    davranışsal testlerin kendisindedir.

    Saf AST — veritabanına DOKUNMAZ.
    """
    turetilen = _lock_incident_cagiranlari()
    assert turetilen, "boş-küme kontrol kolu: hiç çağrı yeri türetilemedi"

    ortak = set(KILIT_KAPISI_OLAN_YOLLAR) & set(KILIT_KAPISI_OLMAYAN_YOLLAR)
    assert not ortak, f"bir yol hem korunan hem istisna olamaz: {sorted(ortak)}"
    for ad, gerekce in KILIT_KAPISI_OLMAYAN_YOLLAR.items():
        assert gerekce.strip(), f"istisna gerekçesiz bırakılamaz: {ad}"

    beyan = set(KILIT_KAPISI_OLAN_YOLLAR) | set(KILIT_KAPISI_OLMAYAN_YOLLAR)
    kapsanmayan = turetilen - beyan
    assert not kapsanmayan, (
        "`_lock_incident` çağıran yeni yol(lar) beyan edilmedi — ya kapı "
        "kurulmalı ya da ÖLÇÜLMÜŞ gerekçeyle istisna edilmeli: "
        f"{sorted(kapsanmayan)}"
    )
    bayat = beyan - turetilen
    assert not bayat, (
        "beyan edilen yol(lar) artık `_lock_incident` ÇAĞIRMIYOR — girdi "
        f"bayat: {sorted(bayat)}"
    )

# ═══ 17. AÇIK-3 — yardımcıların YERİ ve import kenarı ═══════════════════════


def test_runs_module_defines_no_evidence_payload_or_fingerprint_helper():
    """AÇIK-3'ün ANA İSPATI: dört yardımcı `runs.py`'de TANIMLI DEĞİLDİR."""
    for ad in (
        "activation_evidence_payload",
        "rollback_evidence_payload",
        "_evidence_fingerprint",
        "_evidence_fingerprint_from_payload",
    ):
        assert f"def {ad}" not in RUNS_KAYNAK, ad
        assert f"def {ad}" in LIFECYCLE_KAYNAK, ad
    assert "from app.services.sector_package_lifecycle import" in RUNS_KAYNAK


def test_lifecycle_imports_no_pipeline_module_other_than_identity():
    """DÖNGÜSEL IMPORT YASAĞININ KAPISI — küme KAVRAMDAN türetilir.

    Yasak liste elle sayılmaz: `sector_pipeline` paketindeki HER modül taranır
    ve `identity` dışındakilerin hiçbirinin import edilmediği ölçülür.
    """
    paket_dizini = Path(identity.__file__).parent
    moduller = {
        yol.stem
        for yol in paket_dizini.glob("*.py")
        if yol.stem not in ("__init__", "identity")
    }
    assert moduller, "boş-küme kontrol kolu: taranacak modül bulunamadı"

    agac = ast.parse(LIFECYCLE_KAYNAK)
    alinan: set[str] = set()
    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.ImportFrom) and (dugum.module or "").startswith(
            "app.services.sector_pipeline"
        ):
            if dugum.module == "app.services.sector_pipeline":
                alinan.update(ad.name for ad in dugum.names)
            else:
                alinan.add(dugum.module.rsplit(".", 1)[-1])
        if isinstance(dugum, ast.Import):
            for ad in dugum.names:
                if ad.name.startswith("app.services.sector_pipeline"):
                    alinan.add(ad.name.rsplit(".", 1)[-1])

    assert alinan == {"identity"}, alinan
    assert not (alinan & moduller), alinan & moduller


def test_payload_helpers_do_not_import_verified_run():
    """Yardımcılar `runs.VerifiedRun`'a değil YEREL protokole yazılmıştır."""
    assert "VerifiedRun" not in _kod_kimlikleri(LIFECYCLE_KAYNAK)
    assert "KilitliKosuGorunumu" in _kod_kimlikleri(LIFECYCLE_KAYNAK)


def test_kosu_gorunumu_field_set_is_closed():
    """POZİTİF KONTROL: SEKİZ ad birebir; `VerifiedRun` protokolü KARŞILAR."""
    assert len(lifecycle._KOSU_GORUNUM_ALANLARI) == 8
    protokol_alanlari = tuple(
        lifecycle.KilitliKosuGorunumu.__annotations__
    )
    assert set(protokol_alanlari) == set(lifecycle._KOSU_GORUNUM_ALANLARI)

    verified_alanlari = {alan.name for alan in dataclass_fields(runs.VerifiedRun)}
    assert set(lifecycle._KOSU_GORUNUM_ALANLARI) <= verified_alanlari

    gorunum_alanlari = {alan.name for alan in dataclass_fields(runs.KosuSatiriGorunumu)}
    assert gorunum_alanlari == set(lifecycle._KOSU_GORUNUM_ALANLARI)


@pytest.mark.parametrize("eksik", list(lifecycle._KOSU_GORUNUM_ALANLARI))
def test_payload_helper_refuses_object_missing_a_view_field(eksik):
    """FAIL-CLOSED: bir alanı eksik sahte nesne `TypeError` ile düşer."""

    class Sahte:
        pass

    sahte = Sahte()
    for ad in lifecycle._KOSU_GORUNUM_ALANLARI:
        if ad != eksik:
            setattr(sahte, ad, None)

    # B4 (fix turu B): zorunlu anahtar-kelime parametresi VERİLİR. Verilmediğinde
    # `TypeError` argüman BAĞLAMADA doğuyordu — `_require_kosu_gorunumu` daha hiç
    # koşmuyordu, yani matrisin aktivasyon yarısı eksik-alan kapısı SİLİNSE BİLE
    # geçiyordu. Şimdi iki kol YALNIZ eksik görünüm alanında farklılaşır.
    with pytest.raises(TypeError):
        lifecycle.activation_evidence_payload(
            sahte, None, beklenen_madde_kumesi_sha=readiness_items.MADDE_KUMESI_SHA,
            beklenen_kanit_parmakizi=KANIT_IZI_ORNEGI,
        )
    with pytest.raises(TypeError):
        lifecycle.rollback_evidence_payload({}, sahte)


def test_evidence_payload_key_set_is_closed():
    """BUGÜNKÜ KAMU ŞEKLİ — sözleşme assert'i; TÜRETME KANITI DEĞİLDİR.

    Oracle burada ELLE yazılmıştır ve bilinçli öyledir: iki kamu kanıt sınıfının
    bugün hangi anahtarları taşıdığını ekin metnine karşı pinler. Ama bu test
    `_yuk_anahtarlari` yerine sabit bir tuple konsa da YEŞİL kalır — türetmenin
    kendisini ölçen kapı ayrıdır:
    `test_yuk_anahtarlari_discovers_a_field_it_was_never_told_about`.

    Geri alma yükü BEŞ anahtardır (A1(c)) ve ek metniyle BİREBİR eşleşir.
    Aktivasyon yükü ekte YEDİ anahtar diye bağlanmıştır; bugün ALTI'dır ve eksik
    olan TEK ad `expected_no_active`'dir — o alan Task 15'in kalemidir (arayüz
    eki R8(c) görev bölünmesi).

    **DÜRÜST ETİKET (fix turu B, B2):** bu test o gün KENDİLİĞİNDEN yedi ÖLÇMEZ.
    `assert aktivasyon == beklenen_bugun` Task 15 alanı eklediği gün KIRMIZI olur
    ve buradaki elle liste ELLE güncellenir — kapı budur, otomatik genişleme
    değil. Türetmenin taşıdığı güvence ayrı: yük, parmak izi ve `_yuk_kes`
    BİRLİKTE hareket eder; ayrışamazlar.
    """
    geri_alma = lifecycle._yuk_anahtarlari(RollbackGateEvidence)
    assert set(geri_alma) == {
        "manager_approved",
        "katman1_passed",
        "incident_id",
        "package_id",
        "onay_kapsam_sha",
    }
    assert len(geri_alma) == 5

    aktivasyon = set(lifecycle._yuk_anahtarlari(ActivationGateEvidence))
    beklenen_bugun = {
        "activation_eligible",
        "open_questions_count",
        "katman1_passed",
        "checklist_approved",
        "expected_active_version",
        # Plan 2 Task 15'te EKLENDİ. Bu satır ELLE yazıldı ve kapı tam olarak
        # buydu: alan eklendiği gün test KIRMIZI düştü ve liste elle
        # güncellendi. Otomatik genişleme olsaydı yeni bir alan sessizce
        # yüke girer, parmak izini değiştirir ve kimse fark etmezdi.
        "expected_no_active",
        "run_id",
    }
    assert aktivasyon == beklenen_bugun
    assert "provenance_token" not in aktivasyon


def test_yuk_anahtarlari_discovers_a_field_it_was_never_told_about():
    """B2'nin ANA İSPATI: küme SINIFTAN TÜRETİLİR — elle listeden DEĞİL.

    Oracle burada implementasyondan BAĞIMSIZDIR: sınıf testin İÇİNDE, üretim
    kodunda HİÇ GEÇMEYEN alan adlarıyla kurulur. `_yuk_anahtarlari` sabit bir
    tuple'a (ya da elle bakılan bir listeye) çevrilirse bu adları BULAMAZ ve
    burası KIRMIZI olur — oysa `test_evidence_payload_key_set_is_closed` aynı
    mutasyonda YEŞİL kalır. Ayırt eden kapı budur.

    Üç halka BİRLİKTE ölçülür: keşif (`_yuk_anahtarlari`) → taşıma (`_yuk_kes`)
    → parmak izi (`_evidence_fingerprint_from_payload`). Halkalardan biri
    kopsaydı, jetonu BASAN taraf ile kanıtı KURAN taraf sessizce ayrışırdı;
    A1(c)'nin kapattığı sınıf tam olarak budur.
    """

    @dataclass(frozen=True)
    class SentetikGelecekKaniti:
        zeta_gelecek_alani: int
        alfa_gelecek_alani: str
        provenance_token: str

    # (1) KEŞİF: jeton DIŞLANIR; kalan iki uydurma ad ARTAN sırada gelir.
    assert lifecycle._yuk_anahtarlari(SentetikGelecekKaniti) == (
        "alfa_gelecek_alani",
        "zeta_gelecek_alani",
    )

    # (2) TAŞIMA: `_yuk_kes` uydurma alanı yüke KOYAR, küme DIŞINI atar.
    assert dict(
        lifecycle._yuk_kes(
            SentetikGelecekKaniti,
            {
                "alfa_gelecek_alani": "a",
                "zeta_gelecek_alani": 7,
                "provenance_token": "jeton-yuke-GIRMEZ",
                "kume_disi": "atilir",
            },
        )
    ) == {"alfa_gelecek_alani": "a", "zeta_gelecek_alani": 7}

    # (3) FAIL-CLOSED: hesaplanmayan alan sessizce `None`'a DÜŞMEZ.
    with pytest.raises(KeyError):
        lifecycle._yuk_kes(SentetikGelecekKaniti, {"alfa_gelecek_alani": "a"})

    # (4) PARMAK İZİ o alanı ARAR: uydurma alansız yük REDDEDİLİR...
    with pytest.raises(ValueError):
        lifecycle._evidence_fingerprint_from_payload(
            SentetikGelecekKaniti, {"alfa_gelecek_alani": "a"}
        )
    # ...ve NESNELİ ikizle BİREBİR aynı diziyi üretir (jeton hash'e girmez).
    assert lifecycle._evidence_fingerprint_from_payload(
        SentetikGelecekKaniti,
        {"alfa_gelecek_alani": "a", "zeta_gelecek_alani": 7},
    ) == lifecycle._evidence_fingerprint(
        SentetikGelecekKaniti(
            zeta_gelecek_alani=7,
            alfa_gelecek_alani="a",
            provenance_token="jeton-HASHE-girmez",
        )
    )


def test_rollback_evidence_payload_has_five_keys(pkg_db):
    """A1(c): DÖRT anahtarlı eski küme RED — `onay_kapsam_sha` yüke GİRER."""
    assert len(lifecycle._yuk_anahtarlari(RollbackGateEvidence)) == 5
    assert "onay_kapsam_sha" in lifecycle._yuk_anahtarlari(RollbackGateEvidence)


async def test_evidence_payload_derived_from_locked_row_fields_only(pkg_db):
    """Yardımcılar ÇAĞIRANDAN hiçbir değer almaz — hepsi satırdan türer."""
    await _bos_evren(pkg_db)
    incident_id, aktif = await _onayli_olay(pkg_db)
    plan_satiri = await pkg_db.fetchrow(
        "SELECT * FROM social.package_rollback_plans WHERE incident_id = $1", incident_id
    )
    hedef_kosu = await runs._hedef_kosu_gorunumu(
        pkg_db, sector_id=await pkg_db.fetchval(
            "SELECT sector_id FROM social.sector_packages WHERE id = $1", aktif
        ),
        version=1,
    )

    yuk = lifecycle.rollback_evidence_payload(plan_satiri, hedef_kosu)

    assert yuk["incident_id"] == plan_satiri["incident_id"]
    assert yuk["package_id"] == plan_satiri["package_id"]
    assert yuk["onay_kapsam_sha"] == plan_satiri["onay_kapsam_sha"]
    assert yuk["manager_approved"] is True
    assert yuk["katman1_passed"] is True
    # İmza yalnız İKİ konumsal parametre alır: serbest bir sözlük parametresi YOK.
    assert list(inspect.signature(lifecycle.rollback_evidence_payload).parameters) == [
        "plan_satiri",
        "hedef_kosu",
    ]


def _ornek_geri_alma_yuku(**overrides) -> dict:
    yuk = {
        "manager_approved": True,
        "katman1_passed": True,
        "incident_id": "olay-1",
        "package_id": uuid.UUID(int=5),
        "onay_kapsam_sha": "a" * 64,
    }
    yuk.update(overrides)
    return yuk


def test_fingerprint_is_stable_across_equal_payloads():
    """Aynı yük → aynı parmak izi (anahtar sırası fark etmez)."""
    birinci = lifecycle._evidence_fingerprint_from_payload(
        RollbackGateEvidence, _ornek_geri_alma_yuku()
    )
    tersten = dict(reversed(list(_ornek_geri_alma_yuku().items())))
    ikinci = lifecycle._evidence_fingerprint_from_payload(RollbackGateEvidence, tersten)
    assert birinci == ikinci


@pytest.mark.parametrize(
    "alan,yeni",
    [
        ("manager_approved", False),
        ("katman1_passed", False),
        ("incident_id", "olay-2"),
        ("package_id", uuid.UUID(int=6)),
        ("onay_kapsam_sha", "b" * 64),
    ],
)
def test_fingerprint_differs_on_any_field_change(alan, yeni):
    """ÜRETİLMİŞ MATRİS: beş alanın BEŞİ de parmak izini değiştirir."""
    temel = lifecycle._evidence_fingerprint_from_payload(
        RollbackGateEvidence, _ornek_geri_alma_yuku()
    )
    degisik = lifecycle._evidence_fingerprint_from_payload(
        RollbackGateEvidence, _ornek_geri_alma_yuku(**{alan: yeni})
    )
    assert degisik != temel


def test_fingerprint_rejects_wrong_key_set():
    """FAIL-CLOSED: eksik ya da fazla anahtar `ValueError`."""
    eksik = _ornek_geri_alma_yuku()
    del eksik["onay_kapsam_sha"]
    with pytest.raises(ValueError):
        lifecycle._evidence_fingerprint_from_payload(RollbackGateEvidence, eksik)

    fazla = _ornek_geri_alma_yuku(fazladan=1)
    with pytest.raises(ValueError):
        lifecycle._evidence_fingerprint_from_payload(RollbackGateEvidence, fazla)


def test_object_fingerprint_matches_payload_fingerprint():
    """Tanım gereği İKİZ: nesne parmak izi ile yük parmak izi AYNI kuralı paylaşır."""
    kanit = RollbackGateEvidence(
        **_ornek_geri_alma_yuku(), provenance_token="f" * 64
    )
    assert lifecycle._evidence_fingerprint(kanit) == (
        lifecycle._evidence_fingerprint_from_payload(
            RollbackGateEvidence, _ornek_geri_alma_yuku()
        )
    )


def test_no_second_hash_rule_in_runs_module():
    """İkinci hash kuralı YOK: `runs.py` `hashlib`e inmez."""
    assert "hashlib" not in RUNS_KAYNAK


# ═══ 18. Jeton basımı (A2(d)) ═══════════════════════════════════════════════


def test_mint_evidence_token_takes_no_fingerprint_parameter():
    """A2(d)'nin ANA İSPATI: parmak izi ÇAĞIRANDAN alınmaz."""
    parametreler = inspect.signature(runs.mint_evidence_token).parameters
    assert "fingerprint" not in parametreler
    assert set(parametreler) == {"db", "table", "run_id", "incident_id", "package_id"}


async def test_minted_fingerprint_matches_evidence_built_by_the_factory(pkg_db):
    """POZİTİF KONTROL: basılan parmak izi, fabrikanın kanıtınınkiyle BİREBİR."""
    await _bos_evren(pkg_db)
    incident_id, aktif = await _onayli_olay(pkg_db)

    kanit = await runs.build_rollback_evidence(
        pkg_db, incident_id=incident_id, package_id=aktif
    )

    basilan = await pkg_db.fetchval(
        "SELECT kanit_jetonu_parmakizi FROM social.package_rollback_plans "
        "WHERE incident_id = $1 AND package_id = $2",
        incident_id,
        aktif,
    )
    assert basilan == lifecycle._evidence_fingerprint(kanit)


async def test_minted_fingerprint_tracks_the_locked_row_not_the_caller(pkg_db):
    """Satır alanı değişince parmak izi DEĞİŞİR; çağıranın elinde girdi YOK."""
    await _bos_evren(pkg_db)
    incident_id, aktif = await _onayli_olay(pkg_db)

    once = await runs.mint_evidence_token(
        pkg_db,
        table="package_rollback_plans",
        run_id=None,
        incident_id=incident_id,
        package_id=aktif,
    )
    ilk_parmakizi = await pkg_db.fetchval(
        "SELECT kanit_jetonu_parmakizi FROM social.package_rollback_plans "
        "WHERE incident_id = $1 AND package_id = $2",
        incident_id,
        aktif,
    )

    # Kilitli satırın onay mührü değişti → parmak izi de değişmeli.
    await pkg_db.execute(
        "UPDATE social.package_rollback_plans SET onay_kapsam_sha = $3 "
        "WHERE incident_id = $1 AND package_id = $2",
        incident_id,
        aktif,
        "d" * 64,
    )
    sonra = await runs.mint_evidence_token(
        pkg_db,
        table="package_rollback_plans",
        run_id=None,
        incident_id=incident_id,
        package_id=aktif,
    )
    ikinci_parmakizi = await pkg_db.fetchval(
        "SELECT kanit_jetonu_parmakizi FROM social.package_rollback_plans "
        "WHERE incident_id = $1 AND package_id = $2",
        incident_id,
        aktif,
    )
    assert once != sonra
    assert ilk_parmakizi != ikinci_parmakizi


async def test_mint_refuses_when_row_is_not_mintable(pkg_db):
    """`EvidenceMintRefused` — boş dönüş YOKTUR."""
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")

    with pytest.raises(lifecycle.EvidenceMintRefused):
        await runs.mint_evidence_token(
            pkg_db,
            table="sector_package_runs",
            run_id=run_id,
            incident_id=None,
            package_id=None,
        )
    with pytest.raises(lifecycle.EvidenceMintRefused):
        await runs.mint_evidence_token(
            pkg_db,
            table="package_rollback_plans",
            run_id=None,
            incident_id="olay-yok",
            package_id=uuid.UUID(int=3),
        )


@pytest.mark.parametrize("tablo", ["", "sector_packages", "admin_events"])
async def test_mint_table_set_is_closed(pkg_db, tablo):
    with pytest.raises(ValueError):
        await runs.mint_evidence_token(
            pkg_db, table=tablo, run_id="x", incident_id=None, package_id=None
        )


async def test_activation_token_minted_from_locked_run_row(pkg_db):
    """Aktivasyon yolu da kilitli satırdan türetir (yol AÇIK, ölçüldü)."""
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    run_id = await _tam_kosu(pkg_db, sector_id)
    # Onay anlık görüntüsü ZORUNLUDUR (fix turu 1, F1(b)): eksikse jeton
    # BASILMAZ — "açık soru yok" değeri uydurulamaz.
    await _anlik_goruntu_yaz(pkg_db, run_id)

    jeton = await runs.mint_evidence_token(
        pkg_db,
        table="sector_package_runs",
        run_id=run_id,
        incident_id=None,
        package_id=None,
    )

    satir = await pkg_db.fetchrow(
        "SELECT kanit_jetonu, kanit_jetonu_parmakizi, kanit_jetonu_harcandi_at "
        "FROM social.sector_package_runs WHERE run_id = $1",
        run_id,
    )
    assert satir["kanit_jetonu"] == jeton
    assert satir["kanit_jetonu_harcandi_at"] is None
    kosu = await runs._kosu_gorunumu(pkg_db, run_id)
    beklenen = lifecycle._evidence_fingerprint_from_payload(
        ActivationGateEvidence,
        lifecycle.activation_evidence_payload(
            kosu, None, beklenen_madde_kumesi_sha=readiness_items.MADDE_KUMESI_SHA,
            beklenen_kanit_parmakizi=KANIT_IZI_ORNEGI,
        ),
    )
    assert satir["kanit_jetonu_parmakizi"] == beklenen


# ═══ 19. Kanıt sınıflarının şekil kapıları (A4) ═════════════════════════════


class _AltSinifStr(str):
    pass


def test_evidence_run_id_rejects_str_subclass():
    """A4 #4: `type(...) is not str` — `str` alt sınıfı da RED."""
    with pytest.raises(ValueError):
        ActivationGateEvidence(
            activation_eligible=True,
            open_questions_count=0,
            katman1_passed=True,
            checklist_approved=True,
            run_id=_AltSinifStr("kosu-1"),
            provenance_token="a" * 64,
            expected_no_active=True,
        )


def test_evidence_incident_id_rejects_str_subclass():
    """A4 #5: aynı düzeltmenin ayna vakası."""
    with pytest.raises(ValueError):
        RollbackGateEvidence(
            manager_approved=True,
            katman1_passed=True,
            incident_id=_AltSinifStr("olay-1"),
            package_id=uuid.UUID(int=1),
            onay_kapsam_sha="a" * 64,
            provenance_token="b" * 64,
        )


@pytest.mark.parametrize(
    "sha", ["", "   ", "A" * 64, "a" * 63, "a" * 65, "z" * 64, None, 1]
)
def test_rollback_evidence_rejects_non_hex_scope_sha(sha):
    """A4 #6: kapsam mührü 64 karakterlik KÜÇÜK HARF hex olmak zorundadır."""
    with pytest.raises((TypeError, ValueError)):
        RollbackGateEvidence(
            manager_approved=True,
            katman1_passed=True,
            incident_id="olay-1",
            package_id=uuid.UUID(int=1),
            onay_kapsam_sha=sha,
            provenance_token="b" * 64,
        )


@pytest.mark.parametrize(
    "jeton", ["", "   ", "A" * 64, "a" * 63, "a" * 65, None, 1]
)
def test_provenance_token_shape_is_closed(jeton):
    with pytest.raises((TypeError, ValueError)):
        RollbackGateEvidence(
            manager_approved=True,
            katman1_passed=True,
            incident_id="olay-1",
            package_id=uuid.UUID(int=1),
            onay_kapsam_sha="a" * 64,
            provenance_token=jeton,
        )


def test_rollback_evidence_package_id_must_be_uuid():
    with pytest.raises(TypeError):
        RollbackGateEvidence(
            manager_approved=True,
            katman1_passed=True,
            incident_id="olay-1",
            package_id=str(uuid.UUID(int=1)),
            onay_kapsam_sha="a" * 64,
            provenance_token="b" * 64,
        )


# ═══ 20. A4 kapısının DÖRDÜNCÜ koşulu ve eksik onay anlık görüntüsü ════════
#
# Checkpoint fix turu 1, F1 (yüksek): `activation_evidence_payload` iki yerde
# birden FAIL-OPEN'dı.
#   (a) `_checklist_approved` A4'ün DÖRT koşulundan yalnız ÜÇÜNÜ uyguluyordu;
#       dördüncüsü — tasdikteki imzanın kanonik madde kümesi imzasına BİREBİR,
#       NORMALİZASYONSUZ eşitliği — hiç koşmuyordu. Boş olmayan HER dize
#       geçiyordu.
#   (b) Onay anlık görüntüsü `None` iken "açık soru sayısı" 0 yazılıyordu —
#       eksik kanıt, aktivasyon kapısını GEÇİREN değere genişliyordu.
#
# Erişilebilirlik ÖLÇÜLDÜ: `activate_package` `open_questions_count != 0` ve
# `checklist_approved` alanlarına OLDUĞU GİBİ güvenir; jeton tüketimi (Task 15)
# henüz YAZILMAMIŞTIR, dolayısıyla "sonraki görevin kapısı ayrıca reddeder"
# bugün DOĞRU DEĞİLDİR.
#
# İmport kenarı AÇILMAZ (AÇIK-3): beklenen kanonik imza ÇAĞIRANDAN, YALNIZ
# ANAHTAR bir parametreyle gelir; `runs.py` onu `readiness_items`ten okur.


KANIT_IZI_ORNEGI: str = "c" * 64
"""F1 — birim testlerinin kullandığı sahte kanıt parmak izi.

Değer KEYFİDİR ve öyle olması GEREKİR: bu testler kapının KARŞILAŞTIRMA
davranışını ölçer, gerçek türetmeyi değil. Türetmenin kendisi
`test_readiness_checklist.py`'de canlı veritabanına karşı ölçülür.
"""


def _kosu_gorunumu_ornegi(**overrides) -> runs.KosuSatiriGorunumu:
    """Kilitli koşu görünümünün TAM ve GEÇERLİ örneği — alanlar tek tek ezilir."""
    alanlar = {
        "run_id": "kosu-a4",
        "sector_id": uuid.UUID(int=7),
        "package_id": None,
        "durum": "tamamlandi",
        "sonuc": "activation_eligible",
        "approval_snapshot": {"acik_sorular": []},
        "katman1_attestation": {"sonuc": "PASS"},
        "readiness_attestation": {
            "onaylandi": True,
            "madde_kumesi_sha": readiness_items.MADDE_KUMESI_SHA,
            "kanit_parmakizi": KANIT_IZI_ORNEGI,
        },
    }
    alanlar.update(overrides)
    return runs.KosuSatiriGorunumu(**alanlar)


def test_activation_payload_takes_expected_sha_as_keyword_only_parameter():
    """İmport kenarı yerine ÇAĞIRAN taşır — ve YALNIZ ANAHTAR olarak."""
    parametreler = inspect.signature(lifecycle.activation_evidence_payload).parameters
    assert list(parametreler) == [
        "kosu",
        "aktif_paket_satiri",
        "beklenen_madde_kumesi_sha",
        "beklenen_kanit_parmakizi",
    ]
    assert (
        parametreler["beklenen_kanit_parmakizi"].kind
        is inspect.Parameter.KEYWORD_ONLY
    )
    assert (
        parametreler["beklenen_kanit_parmakizi"].default is inspect.Parameter.empty
    )
    assert (
        parametreler["beklenen_madde_kumesi_sha"].kind
        is inspect.Parameter.KEYWORD_ONLY
    )
    assert parametreler["beklenen_madde_kumesi_sha"].default is inspect.Parameter.empty


def test_activation_payload_checklist_true_for_canonical_sha():
    """POZİTİF KONTROL: kanonik imza BİREBİR eşleşince kapı AÇILIR."""
    yuk = lifecycle.activation_evidence_payload(
        _kosu_gorunumu_ornegi(),
        None,
        beklenen_madde_kumesi_sha=readiness_items.MADDE_KUMESI_SHA,
        beklenen_kanit_parmakizi=KANIT_IZI_ORNEGI,
    )
    assert yuk["checklist_approved"] is True
    assert yuk["open_questions_count"] == 0


@pytest.mark.parametrize(
    "sha",
    [
        "a" * 64,
        readiness_items.MADDE_KUMESI_SHA.upper(),
        " " + readiness_items.MADDE_KUMESI_SHA,
        readiness_items.MADDE_KUMESI_SHA + " ",
        readiness_items.MADDE_KUMESI_SHA[:-1] + ("0" if
            readiness_items.MADDE_KUMESI_SHA[-1] != "0" else "1"),
        "onaylandi",
    ],
)
def test_activation_payload_checklist_false_when_sha_is_not_canonical(sha):
    """A4'ün DÖRDÜNCÜ koşulu: boş olmayan HER dize GEÇMEZ — birebir eşitlik."""
    yuk = lifecycle.activation_evidence_payload(
        _kosu_gorunumu_ornegi(
            readiness_attestation={"onaylandi": True, "madde_kumesi_sha": sha}
        ),
        None,
        beklenen_madde_kumesi_sha=readiness_items.MADDE_KUMESI_SHA,
        beklenen_kanit_parmakizi=KANIT_IZI_ORNEGI,
    )
    assert yuk["checklist_approved"] is False


def test_activation_payload_rejects_malformed_expected_sha():
    """Beklenen imza da ŞEKİL kapısından geçer — uydurma değer taşınamaz."""
    for bozuk in ("", "   ", "a" * 63, "A" * 64, None, 1):
        with pytest.raises((TypeError, ValueError)):
            lifecycle.activation_evidence_payload(
                _kosu_gorunumu_ornegi(), None, beklenen_madde_kumesi_sha=bozuk, beklenen_kanit_parmakizi=KANIT_IZI_ORNEGI
            )


@pytest.mark.parametrize("anlik", [None, {}, {"baska": []}])
def test_activation_payload_refuses_missing_approval_snapshot(anlik):
    """Eksik kanıt SIFIRA normalize EDİLMEZ — jeton basımı REDDEDİLİR."""
    with pytest.raises(lifecycle.EvidenceMintRefused):
        lifecycle.activation_evidence_payload(
            _kosu_gorunumu_ornegi(approval_snapshot=anlik),
            None,
            beklenen_madde_kumesi_sha=readiness_items.MADDE_KUMESI_SHA,
            beklenen_kanit_parmakizi=KANIT_IZI_ORNEGI,
        )


# ─── 20b. Fix turu 2, F1 (yüksek): ŞEKİL kapısı ────────────────────────────
#
# Fix turu 1 EKSİK anlık görüntüyü ve EKSİK anahtarı kapattı, ama değerin
# ŞEKLİNİ doğrulamadan `len(...)` çağırmayı sürdürdü. Ölçüldü:
# `{"acik_sorular": ""}` · `{}` · `set()` · `()` hepsi `open_questions_count=0`
# üretiyordu — yani "açık soru YOK" diyen, K-71 kapısını GEÇİREN tek değer.
# Skaler şekiller (`int`/`bool`/`None`/`float`) ise alan-DIŞI bir `TypeError`
# fırlatıyordu; o da alan reddi değil, çağırana sızan beklenmedik hatadır.
#
# ERİŞİLEBİLİRLİK — dürüst sınır: `approval_snapshot` kolonu 036'da şekilsiz
# `JSONB`'dir (yalnız değişmezlik tetikleyicisi var, CHECK yok) ve BUGÜN üretim
# yazıcısı YOKTUR (yazıcı Task 14'ün kalemi). Sınıf bugün canlıda tetiklenemez;
# kapatılma sebebi, Task 14 yazıcısının bu şekli üretmesi hâlinde kanıtın
# SESSİZCE genişlemesidir. Tehdit modeli: girdi araştırma çıktısıdır —
# ÖZENSİZ/BAYAT olabilir, SALDIRGAN değildir.
#
# Sözleşme (ekin revizyonu R-F): `acik_sorular` YALNIZ `list` ve `tuple` kabul
# eder (boş olanlar dâhil — `[]`/`()` MEŞRUDUR, "açık soru yok" demektir);
# kalan HER şey `EvidenceMintRefused`. `tuple` de kabul edilir çünkü
# `VerifiedRun.__post_init__` yükü `identity.donmus`'tan geçirir ve `donmus`
# kuralı (2) `list|tuple → tuple` yazar: donmuş yolda değer `tuple`, ham yolda
# `list` gelir. Aynı şekil disiplini eşleme alanlarına da uygulanır — anlık
# görüntünün ve tasdiklerin KENDİLERİ de `Mapping` olmak ZORUNDADIR.
#
# Matris ELLE SEÇİLMEZ: `donmus`'un KAPALI skaler kümesinden
# (`identity._DEGISMEZ_SKALERLER`) ve kalan kapsayıcı sınıflarından ÜRETİLİR;
# red kolları sözleşme yüklemleriyle SÜZÜLÜR, implementasyondan kopyalanmaz.


class _SayilabilirYineleyici:
    """`Sized` + `Iterable` — GEVŞEK bir kontrol bunu GEÇİRİR, şekil kapısı GEÇİRMEZ.

    `len()`/`Sized`/`Iterable` tabanlı bir kapı yazılsaydı `str` ve `dict` de
    geçerdi; bu sınıf o gevşemenin NEGATİF kontrolüdür.
    """

    def __len__(self) -> int:  # pragma: no cover — çağrılırsa kapı gevşemiştir
        return 0

    def __iter__(self):  # pragma: no cover — çağrılırsa kapı gevşemiştir
        return iter(())


class _ListeAltSinifi(list):
    """Alt sınıf da RED — A4 disiplini (`type(...) is`, `isinstance` DEĞİL)."""


class _DemetAltSinifi(tuple):
    """Alt sınıf da RED — A4 disiplini."""


_SKALER_ORNEKLERI: dict[type, tuple] = {
    type(None): (None,),
    bool: (True, False),
    int: (0, 3),
    float: (0.0, 1.5),
    str: ("", "iki açık soru var"),
    bytes: (b"", b"xx"),
    Decimal: (Decimal("0"), Decimal("2")),
    uuid.UUID: (uuid.UUID(int=0),),
    Path: (Path("."),),
    datetime: (datetime(2026, 1, 1),),
    date: (date(2026, 1, 1),),
}


def _sekil_katalogu() -> list[tuple[str, object]]:
    """Şekil evreni — `donmus`'un kapalı kümesinden ÜRETİLİR, elle yazılmaz."""
    katalog: list[tuple[str, object]] = []
    for tip, ornekler in _SKALER_ORNEKLERI.items():
        for sira, ornek in enumerate(ornekler):
            katalog.append((f"skaler-{tip.__name__}-{sira}", ornek))
    katalog += [
        ("dizi-list-bos", []),
        ("dizi-list-dolu", ["s1", "s2"]),
        ("dizi-tuple-bos", ()),
        ("dizi-tuple-dolu", ("s1",)),
        ("esleme-dict-bos", {}),
        ("esleme-dict-dolu", {"acik_sorular": ["s1"]}),
        ("esleme-proxy-bos", MappingProxyType({})),
        ("esleme-proxy-dolu", MappingProxyType({"a": 1})),
        ("kume-set-bos", set()),
        ("kume-set-dolu", {"s1"}),
        ("kume-frozenset-bos", frozenset()),
        ("kume-frozenset-dolu", frozenset({"s1"})),
        ("sayilabilir-yineleyici", _SayilabilirYineleyici()),
        ("altsinif-list", _ListeAltSinifi(["s1"])),
        ("altsinif-tuple", _DemetAltSinifi(("s1",))),
    ]
    return katalog


def _param(sekiller):
    return [pytest.param(deger, id=etiket) for etiket, deger in sekiller]


# Red kolları SÖZLEŞME yüklemiyle süzülür (implementasyondan kopyalanmaz):
#   dizi sözleşmesi   → KABUL yalnız `type(x) in (list, tuple)`
#   eşleme sözleşmesi → KABUL yalnız `Mapping` (tasdiklerde ayrıca `None`)
_BOZUK_DIZI = [
    (etiket, deger)
    for etiket, deger in _sekil_katalogu()
    if type(deger) not in (list, tuple)
]
_ESLEME_OLMAYAN = [
    (etiket, deger)
    for etiket, deger in _sekil_katalogu()
    if not isinstance(deger, Mapping) and deger is not None
]


def test_open_question_shape_matrix_is_generated_from_the_closed_scalar_set():
    """Matrisin KAVRAMDAN türediğinin kapısı — yarın eklenen skaler kendiliğinden girer."""
    assert set(_SKALER_ORNEKLERI) == set(identity._DEGISMEZ_SKALERLER)
    etiketler = {etiket for etiket, _ in _sekil_katalogu()}
    assert len(etiketler) == len(_sekil_katalogu())  # etiketler TEKİL
    # Süzgeçler boş kalmasın ve kabul kolunu gerçekten DIŞARIDA bıraksın.
    assert {e for e, _ in _BOZUK_DIZI} & {"dizi-list-bos", "dizi-tuple-bos"} == set()
    assert len(_BOZUK_DIZI) == len(_sekil_katalogu()) - 4
    assert {e for e, _ in _ESLEME_OLMAYAN} & {"esleme-dict-bos", "esleme-proxy-bos"} == set()


@pytest.mark.parametrize(
    "acik_sorular,beklenen",
    [
        pytest.param([], 0, id="bos-list-MESRU"),
        pytest.param((), 0, id="bos-tuple-MESRU"),
        pytest.param(["s1"], 1, id="dolu-list"),
        pytest.param(("s1", "s2"), 2, id="dolu-tuple"),
        pytest.param(identity.donmus(["s1", "s2", "s3"]), 3, id="donmus-yol-tuple"),
    ],
)
def test_activation_payload_counts_open_questions_for_sequences(acik_sorular, beklenen):
    """POZİTİF KONTROL + BOŞ-KÜME kolu: `[]` ve `()` MEŞRUDUR, reddedilmez."""
    yuk = lifecycle.activation_evidence_payload(
        _kosu_gorunumu_ornegi(approval_snapshot={"acik_sorular": acik_sorular}),
        None,
        beklenen_madde_kumesi_sha=readiness_items.MADDE_KUMESI_SHA,
        beklenen_kanit_parmakizi=KANIT_IZI_ORNEGI,
    )
    assert yuk["open_questions_count"] == beklenen


@pytest.mark.parametrize("acik_sorular", _param(_BOZUK_DIZI))
def test_activation_payload_refuses_malformed_open_questions_shape(acik_sorular):
    """Şekli bozuk değer SIFIRA genişlemez, alan-DIŞI `TypeError` de fırlatmaz."""
    with pytest.raises(lifecycle.EvidenceMintRefused):
        lifecycle.activation_evidence_payload(
            _kosu_gorunumu_ornegi(approval_snapshot={"acik_sorular": acik_sorular}),
            None,
            beklenen_madde_kumesi_sha=readiness_items.MADDE_KUMESI_SHA,
            beklenen_kanit_parmakizi=KANIT_IZI_ORNEGI,
        )


@pytest.mark.parametrize("anlik", _param(_ESLEME_OLMAYAN))
def test_activation_payload_refuses_non_mapping_approval_snapshot(anlik):
    """Anlık görüntünün KENDİSİ de eşleme olmak zorundadır (`"x" in "xy"` tuzağı)."""
    with pytest.raises(lifecycle.EvidenceMintRefused):
        lifecycle.activation_evidence_payload(
            _kosu_gorunumu_ornegi(approval_snapshot=anlik),
            None,
            beklenen_madde_kumesi_sha=readiness_items.MADDE_KUMESI_SHA,
            beklenen_kanit_parmakizi=KANIT_IZI_ORNEGI,
        )


@pytest.mark.parametrize("tasdik", _param(_ESLEME_OLMAYAN))
def test_activation_payload_refuses_non_mapping_katman1_attestation(tasdik):
    """Aynı sınıf: tasdik de şekli doğrulanmadan booleana çevrilmez."""
    with pytest.raises(lifecycle.EvidenceMintRefused):
        lifecycle.activation_evidence_payload(
            _kosu_gorunumu_ornegi(katman1_attestation=tasdik),
            None,
            beklenen_madde_kumesi_sha=readiness_items.MADDE_KUMESI_SHA,
            beklenen_kanit_parmakizi=KANIT_IZI_ORNEGI,
        )


@pytest.mark.parametrize("tasdik", _param(_ESLEME_OLMAYAN))
def test_activation_payload_refuses_non_mapping_readiness_attestation(tasdik):
    """A4 kapısının girdisi de şekil kapısından geçer."""
    with pytest.raises(lifecycle.EvidenceMintRefused):
        lifecycle.activation_evidence_payload(
            _kosu_gorunumu_ornegi(readiness_attestation=tasdik),
            None,
            beklenen_madde_kumesi_sha=readiness_items.MADDE_KUMESI_SHA,
            beklenen_kanit_parmakizi=KANIT_IZI_ORNEGI,
        )


def test_activation_payload_keeps_none_attestations_as_closed_gates():
    """POZİTİF KONTROL: `None` tasdik MEŞRUDUR — reddedilmez, kapıyı KAPATIR."""
    yuk = lifecycle.activation_evidence_payload(
        _kosu_gorunumu_ornegi(katman1_attestation=None, readiness_attestation=None),
        None,
        beklenen_madde_kumesi_sha=readiness_items.MADDE_KUMESI_SHA,
        beklenen_kanit_parmakizi=KANIT_IZI_ORNEGI,
    )
    assert yuk["katman1_passed"] is False
    assert yuk["checklist_approved"] is False


def _ornek_plan_satiri() -> dict:
    return {
        "onay_actor": ACTOR,
        "onaylandi_at": datetime(2026, 1, 1),
        "onay_kapsam_sha": "d" * 64,
        "incident_id": "olay-sekil",
        "package_id": uuid.UUID(int=11),
    }


@pytest.mark.parametrize("tasdik", _param(_ESLEME_OLMAYAN))
def test_rollback_payload_refuses_non_mapping_target_attestation(tasdik):
    """SÜPÜRME: aynı okuma geri alma yükünde de var — orada da kapatılır."""
    with pytest.raises(lifecycle.EvidenceMintRefused):
        lifecycle.rollback_evidence_payload(
            _ornek_plan_satiri(),
            _kosu_gorunumu_ornegi(katman1_attestation=tasdik),
        )


def test_rollback_payload_keeps_none_target_attestation_as_closed_gate():
    """POZİTİF KONTROL: geri alma yolunda da `None` MEŞRUDUR, kapıyı KAPATIR."""
    yuk = lifecycle.rollback_evidence_payload(
        _ornek_plan_satiri(), _kosu_gorunumu_ornegi(katman1_attestation=None)
    )
    assert yuk["katman1_passed"] is False
    assert yuk["manager_approved"] is True


async def test_mint_refuses_activation_token_for_malformed_open_questions(pkg_db):
    """ERİŞİLEBİLİRLİK: şekilsiz `JSONB` kolonundan gelen bozuk şekil, jetonu DURDURUR."""
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    run_id = await _tam_kosu(pkg_db, sector_id)
    # Kolon 036'da şekilsizdir: CHECK yok, üretim yazıcısı da YOK (Task 14).
    await pkg_db.execute(
        "UPDATE social.sector_package_runs SET approval_snapshot = $2 "
        "WHERE run_id = $1",
        run_id,
        {"acik_sorular": ""},
    )

    with pytest.raises(lifecycle.EvidenceMintRefused):
        await runs.mint_evidence_token(
            pkg_db,
            table="sector_package_runs",
            run_id=run_id,
            incident_id=None,
            package_id=None,
        )

    assert (
        await pkg_db.fetchval(
            "SELECT kanit_jetonu FROM social.sector_package_runs WHERE run_id = $1",
            run_id,
        )
        is None
    )


def test_runs_passes_the_canonical_madde_kumesi_sha_to_the_payload_helper():
    """YAPISAL: beklenen imza `readiness_items.MADDE_KUMESI_SHA`'dan gelir.

    Değer çağırandan taşınıyor diye "dışarıdan gelebilir" olmamalı: `runs.py`'nin
    o çağrıda geçtiği ifade ELLE değil AST'ten okunur.
    """
    agac = ast.parse(RUNS_KAYNAK)
    gecilen: list[ast.expr] = []
    for dugum in ast.walk(agac):
        if (
            isinstance(dugum, ast.Call)
            and isinstance(dugum.func, ast.Name)
            and dugum.func.id == "activation_evidence_payload"
        ):
            anahtarlar = {kw.arg: kw.value for kw in dugum.keywords}
            assert "beklenen_madde_kumesi_sha" in anahtarlar, ast.dump(dugum)
            gecilen.append(anahtarlar["beklenen_madde_kumesi_sha"])
    assert gecilen, "runs.py yardımcıyı hiç çağırmıyor"
    for ifade in gecilen:
        assert isinstance(ifade, ast.Attribute), ast.dump(ifade)
        assert ifade.attr == "MADDE_KUMESI_SHA", ast.dump(ifade)
        assert isinstance(ifade.value, ast.Name), ast.dump(ifade)
        assert ifade.value.id == "readiness_items", ast.dump(ifade)


async def test_mint_refuses_activation_token_without_approval_snapshot(pkg_db):
    """ERİŞİLEBİLİRLİK: açık, `mint_evidence_token` üzerinden GERÇEKTEN kapanır."""
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    run_id = await _tam_kosu(pkg_db, sector_id)

    with pytest.raises(lifecycle.EvidenceMintRefused):
        await runs.mint_evidence_token(
            pkg_db,
            table="sector_package_runs",
            run_id=run_id,
            incident_id=None,
            package_id=None,
        )

    basildi = await pkg_db.fetchval(
        "SELECT kanit_jetonu FROM social.sector_package_runs WHERE run_id = $1",
        run_id,
    )
    assert basildi is None


async def test_mint_activation_token_records_checklist_gate_from_attestation(pkg_db):
    """POZİTİF KONTROL + FARK: tasdik kanonikse parmak izi DEĞİŞİR, kapı AÇIKTIR."""
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    run_id = await _tam_kosu(pkg_db, sector_id)
    await _anlik_goruntu_yaz(pkg_db, run_id)

    async with pkg_db.transaction():
        kosu = await runs._kosu_gorunumu(pkg_db, run_id)
        onaysiz = lifecycle.activation_evidence_payload(
            kosu, None, beklenen_madde_kumesi_sha=readiness_items.MADDE_KUMESI_SHA,
            beklenen_kanit_parmakizi=KANIT_IZI_ORNEGI,
        )
    assert onaysiz["checklist_approved"] is False

    await runs.attest_readiness(
        pkg_db,
        run_id=run_id,
        kapi_maddeleri=tuple(sorted(readiness_items.KAPI_MADDELERI)),
        sinyal_maddeleri=(),
        actor=ACTOR,
    )
    async with pkg_db.transaction():
        kosu = await runs._kosu_gorunumu(pkg_db, run_id)
        # F1: bu çağrı GERÇEK tasdike bakıyor, o yüzden beklenen iz de GERÇEK
        # türetmeden gelir — sahte sabit burada kapıyı haklı olarak düşürürdü.
        onayli = lifecycle.activation_evidence_payload(
            kosu, None, beklenen_madde_kumesi_sha=readiness_items.MADDE_KUMESI_SHA,
            beklenen_kanit_parmakizi=await runs.kanit_parmakizi(
                pkg_db, run_id=run_id
            ),
        )
    assert onayli["checklist_approved"] is True


# ═══ 21. Geri alma HATA kaydı — kilidin İÇİNDE ve satır sayısı KANITLI ═════
#
# Checkpoint fix turu 1, F2 (yüksek): paket başına işlem ve olay kilidi, tanınan
# bir istisna dışarı çıkınca SONA ERİYORDU; `durum='hata'` ancak ondan SONRA,
# KİLİTSİZ bir güncellemeyle yazılıyor ve kaç satır etkilendiği KONTROL
# EDİLMİYORDU. O pencerede üyelik daraltması kilidi alıp satırı `bekliyor` görüp
# SİLEBİLİR; hata güncellemesi sıfır satır etkiler, sessizce geçer ve rapor yine
# "bu paket düştü" der — yürütme denemesinin izi KAYBOLUR.
#
# Aralık DETERMİNİSTİKTİR, uykuyla değil katalogla ölçülür: B bağlantısı, A'nın
# işlem boyunca tuttuğu SATIR kilidine `FOR UPDATE` ile girmeye çalışır ve
# bekler (`pg_locks`, `NOT granted`). A'nın işlemi bittiği anda B sunucu
# tarafında UYANIR — yani "önce kim davranır" yarışı yoktur, B kazanır.
#
#   * DÜZELTMEDEN ÖNCE: A'nın işlemi istisnayla sona erer, satır hâlâ
#     `bekliyor`dur, B onu SİLER; A'nın kilitsiz güncellemesi 0 satır etkiler.
#   * DÜZELTMEDEN SONRA: A `durum='hata'`yı kilidi BIRAKMADAN yazar; B kilidi
#     ancak ondan sonra alır ve 036'nın DELETE kolu "yürütülmüş satır
#     SİLİNEMEZ" ile REDDEDER.


async def test_rollback_failure_status_is_written_before_the_lock_is_released(
    monkeypatch, test_db_setup
):
    """F2'nin ANA İSPATI: hata kaydı kilidin İÇİNDE yazılır ve izi silinemez."""
    url = _require_test_database(test_db_setup)
    kurulum = await asyncpg.connect(url)
    await _init_connection(kurulum)
    a_baglanti = await asyncpg.connect(url)
    await _init_connection(a_baglanti)
    b_baglanti = await asyncpg.connect(url)
    await _init_connection(b_baglanti)
    gozlemci = await asyncpg.connect(url)
    sektorler: list = []
    incident_id = None
    b_gorev = None
    try:
        await _bos_evren(kurulum)
        sector_id, aktif = await _geri_alinabilir(kurulum)
        sektorler.append(sector_id)
        kume = await _affected(kurulum)
        incident_id = await runs.build_rollback_plan(
            kurulum, affected=kume, actor=ACTOR
        )
        await runs.approve_incident_rollback(
            kurulum, incident_id=incident_id, actor=ACTOR
        )

        async def _b_uyeligi_siler():
            """Üyelik daraltmasının veri katmanı hamlesi: hard DELETE."""
            async with b_baglanti.transaction():
                await b_baglanti.fetchrow(
                    "SELECT package_id FROM social.package_rollback_plans "
                    "WHERE incident_id = $1 AND package_id = $2 FOR UPDATE",
                    incident_id,
                    aktif,
                )
                await b_baglanti.execute(
                    "DELETE FROM social.package_rollback_plans "
                    "WHERE incident_id = $1 AND package_id = $2",
                    incident_id,
                    aktif,
                )

        async def _dusen_kanit(db, *, incident_id, package_id):
            nonlocal b_gorev
            b_gorev = asyncio.create_task(_b_uyeligi_siler())
            bekleyen = 0
            for _ in range(300):
                bekleyen = await gozlemci.fetchval(
                    "SELECT count(*) FROM pg_locks WHERE NOT granted"
                )
                if bekleyen:
                    break
                await asyncio.sleep(0.01)
            assert bekleyen, "B satır kilidinde beklemedi — aralık kurulmadı"
            raise runs.RollbackEvidenceUnavailable("enjekte edilen arıza")

        monkeypatch.setattr(runs, "build_rollback_evidence", _dusen_kanit)

        rapor = await runs.execute_rollback_plan(
            a_baglanti, incident_id=incident_id, actor=ACTOR
        )

        assert rapor.hata == (aktif,)

        # B, A'nın işlemi bittiği anda kilidi alır. Satır `hata` olduğu için
        # 036'nın DELETE kolu onu REDDEDER — iz silinemez.
        with pytest.raises(asyncpg.PostgresError):
            await asyncio.wait_for(b_gorev, timeout=10)

        satir = await gozlemci.fetchrow(
            "SELECT durum, reason FROM social.package_rollback_plans "
            "WHERE incident_id = $1 AND package_id = $2",
            incident_id,
            aktif,
        )
        assert satir is not None, "hata satırı KAYBOLDU — yürütme izi silindi"
        assert satir["durum"] == "hata"
        assert "enjekte edilen arıza" in satir["reason"]
    finally:
        if b_gorev is not None and not b_gorev.done():
            b_gorev.cancel()
        for baglanti in (a_baglanti, b_baglanti):
            await baglanti.close()
        if incident_id is not None:
            await kurulum.execute(
                "UPDATE social.package_rollback_plans SET durum = 'bekliyor', "
                "kanit_jetonu_harcandi_at = NULL WHERE incident_id = $1",
                incident_id,
            )
            await kurulum.execute(
                "DELETE FROM social.package_rollback_plans WHERE incident_id = $1",
                incident_id,
            )
        for sector_id in sektorler:
            await _committed_sektor_sil(kurulum, sector_id)
        await gozlemci.close()
        await kurulum.close()


def test_rollback_failure_write_is_inside_the_locked_transaction():
    """YAPISAL: `except` kolu olay kilidini alan `async with` bloğunun İÇİNDEDİR.

    Davranış testi aralığı ölçer; bu kapı yapıyı pinler — hata yazımının
    kilidin dışına geri kayması sessizce olmasın.
    """
    agac = ast.parse(RUNS_KAYNAK)
    (govde,) = [
        dugum
        for dugum in ast.walk(agac)
        if isinstance(dugum, ast.AsyncFunctionDef)
        and dugum.name == "execute_rollback_plan"
    ]
    dis_bloklar = [
        dugum
        for dugum in ast.walk(govde)
        if isinstance(dugum, ast.AsyncWith)
        and "_lock_incident" in ast.dump(dugum.body[0])
    ]
    assert dis_bloklar, "olay kilidini ilk ifade yapan işlem bloğu bulunamadı"
    bulundu = False
    for blok in dis_bloklar:
        for dugum in ast.walk(blok):
            if isinstance(dugum, ast.Try):
                for kol in dugum.handlers:
                    metin = ast.dump(kol)
                    if "'hata'" in metin or "hata'" in metin:
                        bulundu = True
    assert bulundu, "hata yazımı kilitli işlem bloğunun İÇİNDE değil"


# ═══ 22. Kanıt üreticileri AÇIK bir işlem İSTER (F4) ═══════════════════════
#
# Checkpoint fix turu 1, F4 (yüksek): `build_rollback_evidence` işlem-ömürlü
# danışma kilidini ALIYOR ama kendi işlemini AÇMIYOR ve çağıranın açtığını da
# DOĞRULAMIYORDU. Otomatik-commit altında hem danışma kilidi hem satır kilitleri
# kendi ifadelerinin sonunda düşer; fonksiyon dışa açık olduğu için imzasına
# uyan bir çağıran kapsamı doğrulayıp, üyelik değişimiyle yarışıp, ESKİ kapsama
# bağlı bir jeton bastırıp kilitler bırakıldıktan SONRA kanıt döndürebilirdi.
# Aynı boşluk `mint_evidence_token` için de geçerliydi (kilitli satır iddiası).
#
# ÖLÇÜM NOTU (İlke 9): `db`/`pkg_db` fixture'ı HER testi bir işlemde koşturur —
# yani o bağlantıyla bu kapı hiç görülmez. Kapıyı ölçmek için işlem AÇMAYAN ham
# bir bağlantı gerekir; `islemsiz_db` tam olarak odur.


@pytest.fixture
async def islemsiz_db(test_db_setup: str):
    """İşlem AÇMAYAN ham bağlantı (üretimin havuzdan aldığı hâl).

    `db` fixture'ının aksine burada `transaction().start()` YOKTUR: otomatik
    commit altındaki gerçek çağıran davranışı ancak böyle ölçülebilir. Test
    verisi YAZMAZ — bu yolun kapısı veriye ULAŞMADAN önce koşar.
    """
    baglanti = await asyncpg.connect(_require_test_database(test_db_setup))
    await _init_connection(baglanti)
    try:
        yield baglanti
    finally:
        await baglanti.close()


async def test_build_rollback_evidence_refuses_outside_a_transaction(islemsiz_db):
    """FAIL-CLOSED: işlem yoksa kanıt KURULMAZ — kilitsiz kanıt YOKTUR.

    MESAJ FARKI: düzeltmeden önce bu çağrı olay kilidini alıp (ve HEMEN
    bırakıp) plan satırını arıyor ve `RollbackEvidenceUnavailable` veriyordu;
    yani kilitsiz koşum SESSİZCE kabul ediliyordu. Artık veriye ULAŞMADAN
    `TransactionRequired` ile düşer.
    """
    assert not islemsiz_db.is_in_transaction()
    with pytest.raises(runs.TransactionRequired):
        await runs.build_rollback_evidence(
            islemsiz_db, incident_id="olay-yok-0001", package_id=uuid.UUID(int=9)
        )


async def test_mint_evidence_token_refuses_outside_a_transaction(islemsiz_db):
    """Aynı kapı jeton basımında da vardır — hem de tablo kapısından ÖNCE."""
    assert not islemsiz_db.is_in_transaction()
    with pytest.raises(runs.TransactionRequired):
        await runs.mint_evidence_token(
            islemsiz_db,
            table="package_rollback_plans",
            run_id=None,
            incident_id="olay-yok-0001",
            package_id=uuid.UUID(int=9),
        )
    # Kapı İLK iştir: kapalı küme dışı bir tablo bile onu ATLAYAMAZ.
    with pytest.raises(runs.TransactionRequired):
        await runs.mint_evidence_token(
            islemsiz_db,
            table="admin_events",
            run_id=None,
            incident_id="olay-yok-0001",
            package_id=uuid.UUID(int=9),
        )


async def test_evidence_producers_run_when_the_caller_opened_a_transaction(
    islemsiz_db,
):
    """POZİTİF KONTROL: açık işlemde kapı GEÇİLİR — eski redler geri gelir.

    Kapının geniş kesmediği ancak böyle ölçülür: aynı çağrı, aynı (var olmayan)
    olayla, işlem içinde ESKİ istisnalarını verir.
    """
    async with islemsiz_db.transaction():
        with pytest.raises(runs.RollbackEvidenceUnavailable):
            await runs.build_rollback_evidence(
                islemsiz_db, incident_id="olay-yok-0001", package_id=uuid.UUID(int=9)
            )
        with pytest.raises(lifecycle.EvidenceMintRefused):
            await runs.mint_evidence_token(
                islemsiz_db,
                table="package_rollback_plans",
                run_id=None,
                incident_id="olay-yok-0001",
                package_id=uuid.UUID(int=9),
            )
        with pytest.raises(ValueError):
            await runs.mint_evidence_token(
                islemsiz_db,
                table="admin_events",
                run_id=None,
                incident_id="olay-yok-0001",
                package_id=uuid.UUID(int=9),
            )


@pytest.mark.parametrize(
    "sahte_db",
    [object(), type("Yok", (), {"is_in_transaction": None})()],
    ids=["yontem-yok", "yontem-cagrilabilir-degil"],
)
async def test_transaction_gate_is_fail_closed_for_unknown_connections(sahte_db):
    """Bağlantı soruyu CEVAPLAYAMIYORSA da düşer — "belki işlemdedir" YOK."""
    with pytest.raises(runs.TransactionRequired):
        await runs.mint_evidence_token(
            sahte_db,
            table="package_rollback_plans",
            run_id=None,
            incident_id="olay-1",
            package_id=uuid.UUID(int=1),
        )
    with pytest.raises(runs.TransactionRequired):
        await runs.build_rollback_evidence(
            sahte_db, incident_id="olay-1", package_id=uuid.UUID(int=1)
        )


def test_transaction_required_is_not_swallowed_by_the_rollback_executor():
    """SINIF TAKSONOMİSİ — ucuz ve doğru, ama TEK BAŞINA YETMEZ.

    `execute_rollback_plan` yalnız üç tipi yakalar; `TransactionRequired`
    onların hiçbirinin alt sınıfı DEĞİLDİR.

    **DÜRÜST SINIR (fix turu B, B3):** burası yürütücüyü ÇALIŞTIRMAZ. `except`
    kolu `except Exception` yapılsa bu iki assert YEŞİL kalırdı. Davranışsal
    yayılma ölçümü kardeş testtedir:
    `test_transaction_required_propagates_out_of_the_rollback_executor`.
    """
    assert not issubclass(
        runs.TransactionRequired,
        (
            runs.RollbackEvidenceUnavailable,
            lifecycle.EvidenceMintRefused,
            lifecycle.LifecycleError,
        ),
    )
    assert "TransactionRequired" in runs.__all__


async def test_transaction_required_propagates_out_of_the_rollback_executor(
    pkg_db, monkeypatch
):
    """B3'ün ANA İSPATI — YÜRÜTÜCÜ GERÇEKTEN KOŞAR.

    Geçerli, onaylanmış bir olay kurulur; `build_rollback_evidence` sözleşme
    ihlali (`TransactionRequired`) fırlatacak biçimde değiştirilir ve
    `execute_rollback_plan` ÇAĞRILIR. Ölçülen İKİ şey:
      1. İstisna ÇAĞIRANA çıkar — yürütücü rapor DÖNMEZ, dolayısıyla ihlal bir
         arıza satırı olarak RAPORLANAMAZ;
      2. plan satırı `durum='hata'` diye DAMGALANMAZ — `bekliyor` kalır ve olay
         yeniden koşulabilir.

    `except Exception` mutasyonunda ikisi de düşer: çağrı sessizce bir rapor
    döner ve satır `hata` olur.
    """
    await _bos_evren(pkg_db)
    incident_id, aktif = await _onayli_olay(pkg_db)

    async def _sozlesme_ihlali(db, *, incident_id, package_id):
        raise runs.TransactionRequired("SENTETİK sözleşme ihlali (fix turu B, B3)")

    monkeypatch.setattr(runs, "build_rollback_evidence", _sozlesme_ihlali)

    with pytest.raises(runs.TransactionRequired):
        await runs.execute_rollback_plan(
            pkg_db, incident_id=incident_id, actor=ACTOR
        )

    satir = await pkg_db.fetchrow(
        "SELECT durum, reason FROM social.package_rollback_plans "
        "WHERE incident_id = $1 AND package_id = $2",
        incident_id,
        aktif,
    )
    assert satir["durum"] == "bekliyor", satir["durum"]
    assert satir["reason"] is None or "SENTETİK" not in satir["reason"]


# ═══ Damga grameri ve artefakt türü — hakem turu 2 (yüksek) ════════════════


@pytest.mark.parametrize(
    "source",
    [
        "model=a; model=b; surum=1; tarih=2026-09-11; girdi_ozeti=x",
        "model=a; surum=1; tarih=2026-09-11; girdi_ozeti=x; bilinmeyen=z",
        "onek model=a; surum=1; tarih=2026-09-11; girdi_ozeti=x",
        "model=a; surum=1; tarih=2026-09-11; girdi_ozeti=x sonek=y",
    ],
    ids=["tekrar-eden-alan", "bilinmeyen-alan", "onek-artigi", "sonek-artigi"],
)
def test_parse_stamp_rejects_ambiguous_stamps(source):
    """Damga KİMLİK otoritesidir; belirsiz damga ayrıştırılamaz (fail-closed).

    Hakem turu 2 (yüksek): ayrıştırıcı çapasız `finditer` + sözlük kurgusuydu.
    Tekrar eden `model` alanında SON değer kazanıyordu, bilinmeyen alanlar ve
    artık metin sessizce yok sayılıyordu. Hazırlık listesi bu çıktıyı ÜRETİCİ
    KİMLİĞİ olarak tükettiği için belirsiz iki damga "iki ayrı hakem" diye
    okunabiliyordu.
    """
    with pytest.raises(runs.ArtifactStampMissing):
        runs.parse_stamp(source)


def test_parse_stamp_accepts_the_canonical_stamp():
    """POZİTİF KONTROL: kanonik damga geçer ve dört alanı da çözer."""
    damga = runs.build_stamp(
        model="arac-1", surum="2026-09", tarih="2026-09-11", girdi_ozeti="brief-sha"
    )

    assert runs.parse_stamp(damga) == {
        "model": "arac-1",
        "surum": "2026-09",
        "tarih": "2026-09-11",
        "girdi_ozeti": "brief-sha",
    }


def test_artifact_kinds_constant_mirrors_the_migration_check():
    """İzinli tür kümesi ŞEMADAN okunur — ikinci kanonik liste yazılmaz."""
    import re

    kok = Path(__file__).resolve().parents[4]
    metin = (kok / "shared/db/migrations/032_sector_packages.sql").read_text(
        encoding="utf-8"
    )
    esles = re.search(r"kind TEXT NOT NULL CHECK \(kind IN \(([^)]*)\)\)", metin)
    assert esles is not None
    assert set(runs.ARTEFAKT_TURLERI) == set(re.findall(r"'([^']+)'", esles.group(1)))


async def test_record_artifact_refuses_a_kind_the_schema_rejects(pkg_db):
    """DEĞİŞMEZ yazıcıda: şemanın kabul etmediği tür veritabanına GİTMEZ.

    Hakem turu 2 (orta): kapıyı yalnız bir test taraması tutuyordu ve dolaylı
    çağrı biçimlerini (takma ad, `**kwargs`) göremiyordu. Kural, yazıcının
    kendi değişmezine yükseltildi.
    """
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")

    with pytest.raises(ValueError, match="artefakt türü"):
        await runs.record_artifact(
            pkg_db,
            run_id=run_id,
            sector_slug="kuyumculuk",
            kind="denetci-raporu",
            source=runs.build_stamp(
                model="arac-1", surum="1", tarih="2026-09-11", girdi_ozeti="x"
            ),
            content_md="# ham",
        )

    assert (
        await pkg_db.fetchval(
            "SELECT count(*) FROM social.sector_research_artifacts WHERE run_id = $1",
            run_id,
        )
        == 0
    )
