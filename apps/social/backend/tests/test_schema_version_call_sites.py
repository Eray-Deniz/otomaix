"""Hiçbir çağrı yeri şema sürümünü sessizce varsaymaz (tasarım notu 2026-09-25 §3.9; plan Task 3, D2).

Sınıflandırma (plan Task 3):
- Saklı paket (DB satırı) → satırın sürümü: CLI `_aktif_paket`, `resolve_package_context`,
  `insert_draft` / `_update_draft_row`, sentezin aktif paket birimleri.
- Yeni aday → `CURRENT_SCHEMA_VERSION`: motor şema kapısı + nihai kapı, operatör yolu,
  sentez aday doğrulaması, taslak yazıcısının sürümü.
"""

from __future__ import annotations

import ast
import sys
import uuid
from pathlib import Path

from app.core.database import _init_connection

from .test_sector_packages_service import _valid_content
from .test_unit_identity import _log_for

BACKEND_KOKU = Path(__file__).resolve().parents[1]
if str(BACKEND_KOKU / "scripts") not in sys.path:
    sys.path.insert(0, str(BACKEND_KOKU / "scripts"))

import sector_pipeline_cli as cli  # noqa: E402

# Kavram: şema kapısını ya da ondan türeyen birim görüntüsünü çağıran HER ad.
SCHEMA_GATE_NAMES = frozenset(
    {"structural_errors", "decision_units", "check_unit_integrity", "validate_package_content"}
)


def _called_name(node: ast.Call) -> str | None:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return None


def _schema_gate_calls() -> list[tuple[str, int, ast.Call]]:
    found = []
    for root in (BACKEND_KOKU / "app", BACKEND_KOKU / "scripts"):
        for path in sorted(root.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and _called_name(node) in SCHEMA_GATE_NAMES:
                    found.append((str(path.relative_to(BACKEND_KOKU)), node.lineno, node))
    return found


def test_every_schema_gate_call_passes_explicit_version():
    calls = _schema_gate_calls()
    # Pozitif kontrol: tarama gerçekten çağrı buluyor (boş küme "hepsi temiz" demez).
    assert len(calls) >= 10, calls
    missing = [
        f"{path}:{line}"
        for path, line, node in calls
        if not any(kw.arg == "schema_version" for kw in node.keywords)
    ]
    assert missing == [], f"şema sürümü açıkça seçilmemiş çağrı yerleri: {missing}"


async def test_active_v1_package_units_under_v2_code(db):
    """CLI aktif paketi SATIRIN sürümüyle birimlere ayırır — v1 satır v2 kodla okunur."""
    await _init_connection(db)
    root_id = await db.fetchval(
        "SELECT id FROM social.sectors WHERE parent_sector_id IS NULL LIMIT 1"
    )
    sector_id = await db.fetchval(
        "INSERT INTO social.sectors (slug, display_name, parent_sector_id) "
        "VALUES ($1, 'Alt', $2) RETURNING id",
        f"alt-{uuid.uuid4().hex[:8]}",
        root_id,
    )
    content = _valid_content()
    await db.execute(
        "INSERT INTO social.sector_packages "
        "(sector_id, version, status, schema_version, content, decision_log) "
        "VALUES ($1, 1, 'active', 1, $2, $3)",
        sector_id,
        content,
        _log_for(content),
    )

    _aktif, birimler, surum = await cli._aktif_paket(db, sector_id)

    assert surum == 1
    assert birimler
    assert {b["alan"] for b in birimler.values()} >= {"kapsam", "kanca_kaliplari"}




def test_synthesis_active_units_use_the_rows_version():
    """Sentezin aktif paket birimleri SATIRIN sürümüyle türer — v1 aktif, v2 kodla."""
    import pytest

    from app.services.sector_pipeline import synthesis

    content = _valid_content()
    paket = {"schema_version": 1, "content": content, "decision_log": _log_for(content)}

    birimler = synthesis._aktif_birimler(paket)
    assert len(birimler) == len(paket["decision_log"])

    eksik = {k: v for k, v in paket.items() if k != "schema_version"}
    with pytest.raises(synthesis.SynthesisFailed, match="schema_version"):
        synthesis._aktif_birimler(eksik)


async def test_cli_active_package_is_the_wrapper_its_consumers_read(db):
    """CLI aktif paketi sentez ve motorun okuduğu SARMAL biçimde verir.

    Kusur (2026-09-25, Task 3 sırasında bulundu): `_aktif_paket` yalnız içerik
    sözlüğünü döndürüyordu; `synthesis._aktif_birimler` `content` +
    `decision_log` + `schema_version` okur (aksi hâlde `SynthesisFailed`),
    motor `_aktif_ozel_gunler` `content` altından okur (aksi hâlde özel günler
    boş görünür), sentez istemi EK-H'de `unit_id`'leri göstermek zorundadır.
    Testler bu yolu yalnız "aktif paket yok" hâliyle koşuyordu.
    """
    from app.services.sector_pipeline import engine, synthesis

    await _init_connection(db)
    root_id = await db.fetchval(
        "SELECT id FROM social.sectors WHERE parent_sector_id IS NULL LIMIT 1"
    )
    sector_id = await db.fetchval(
        "INSERT INTO social.sectors (slug, display_name, parent_sector_id) "
        "VALUES ($1, 'Alt', $2) RETURNING id",
        f"alt-{uuid.uuid4().hex[:8]}",
        root_id,
    )
    content = _valid_content()
    log = _log_for(content)
    await db.execute(
        "INSERT INTO social.sector_packages "
        "(sector_id, version, status, schema_version, content, decision_log) "
        "VALUES ($1, 1, 'active', 1, $2, $3)",
        sector_id,
        content,
        log,
    )

    aktif, birimler, surum = await cli._aktif_paket(db, sector_id)

    assert aktif == {"schema_version": 1, "content": content, "decision_log": log}
    assert surum == 1
    assert synthesis._aktif_birimler(aktif) == birimler

    class _Girdi:
        aktif_paket = aktif

    assert engine._aktif_ozel_gunler(_Girdi()) == content["ozel_gun"]
