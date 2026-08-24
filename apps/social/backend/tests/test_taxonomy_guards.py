"""Task 4 — kök kova korumaları (R-01 / R-02) + trend bağışıklığı.

Alt sektör satırları (`parent_sector_id IS NOT NULL`) yalnız paket katmanının
adresidir; markanın kök sektörü, `GET /sectors` listesi ve trend süpürmesi
onları GÖRMEZ. Üç yüzey de kendi sorgusunu koştuğu için üçü ayrı ayrı sınanır:

1. `sector_resolver.resolve_sector` — hem tam slug hem kısmi eşleşme dalı.
2. `routers/sectors.list_sectors` — frontend'in üç tüketicisi aynı listeyi görür.
3. `trends/layer_a.run_nightly_sweep` — sorgu zaten kök filtreli; test onu PİNLER.

Önbellek bu testlerde devre dışıdır: Redis'te kalmış bir değer sorgunun
sonucunu gizleyebilir. Canlı LLM çağrısı YOKTUR — süpürmenin Claude ucu
monkeypatch ile kesilir (plan "Global Constraints").
"""

from __future__ import annotations

import uuid

import pytest

from app.routers import sectors as sectors_router
from app.services import sector_resolver
from app.services.trends import layer_a

SUB_SLUG = "kuafor-salonu"


@pytest.fixture(autouse=True)
def no_cache(monkeypatch):
    """Sektör önbelleğini kapat — testler DB sorgusunu ölçer, Redis'i değil."""

    async def _miss(_key):
        return None

    async def _noop(_key, _value, _ttl):
        return None

    for module in (sector_resolver, sectors_router):
        monkeypatch.setattr(module, "get_cached", _miss)
        monkeypatch.setattr(module, "set_cached", _noop)


async def _root_id(db, slug: str = "hizmet") -> uuid.UUID:
    return await db.fetchval("SELECT id FROM social.sectors WHERE slug = $1", slug)


async def _new_sub_sector(db, slug: str = SUB_SLUG) -> uuid.UUID:
    """Kök seed'in altına bir alt sektör açar (test transaction'ında)."""
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


async def test_resolver_ignores_sub_sector_rows(db):
    """R-01: çözücü hiçbir girdiyi alt sektöre çözmez — tam VE kısmi eşleşme."""
    sub_id = await _new_sub_sector(db)

    # Tam slug: alt satırın kendi adı verilse bile kök kovaya düşer.
    exact = await sector_resolver.resolve_sector(db, SUB_SLUG)
    assert exact is not None
    assert exact[0] != sub_id, "çözücü alt sektöre çözdü (tam slug)"

    # Kısmi eşleşme dalı: alt slug'ı İÇEREN serbest metin de alt satıra gitmez.
    partial = await sector_resolver.resolve_sector(db, "Kuaför Salonu Ankara")
    assert partial is not None
    assert partial[0] != sub_id, "çözücü alt sektöre çözdü (kısmi eşleşme)"

    # Her iki yol da kök kovada kalır.
    root_ids = {
        row["id"]
        for row in await db.fetch(
            "SELECT id FROM social.sectors WHERE parent_sector_id IS NULL"
        )
    }
    assert exact[0] in root_ids
    assert partial[0] in root_ids

    # `resolve_sector_id` aynı garantiyi taşır (brands.py bu ucu çağırır).
    resolved_id = await sector_resolver.resolve_sector_id(db, SUB_SLUG)
    assert resolved_id != sub_id
    assert resolved_id in root_ids


async def test_sectors_endpoint_excludes_sub_sectors(db):
    """R-02: `GET /sectors` alt satırı listelemez; kök liste aynen görünür."""
    sub_id = await _new_sub_sector(db)

    response = await sectors_router.list_sectors(db=db)
    data = response.data

    listed_ids = {row["id"] for row in data}
    assert str(sub_id) not in listed_ids, "alt sektör listeye sızdı"
    assert all(row["parent_sector_id"] is None for row in data)

    # Kök satırların tamamı listede — filtre fazla kırpmıyor.
    root_slugs = {
        row["slug"]
        for row in await db.fetch(
            "SELECT slug FROM social.sectors WHERE parent_sector_id IS NULL"
        )
    }
    assert {row["slug"] for row in data} == root_slugs


async def test_trend_sweep_query_root_only(db, monkeypatch):
    """Trend süpürmesi alt satırı hiç görmez (sorgu zaten kök filtreli — pin)."""
    sub_id = await _new_sub_sector(db)

    seen: list[str] = []

    async def _fake_layer_a(sector):
        seen.append(sector["id"])
        # İki kolon da jsonb — düz metin geçersizdir.
        return {
            "trends": "[]",
            "source_summary": '{"kaynak": "test"}',
            "raw_count": 0,
        }

    # Canlı Claude çağrısı YASAK — uç kesilir.
    monkeypatch.setattr(layer_a, "fetch_sector_layer_a", _fake_layer_a)

    result = await layer_a.run_nightly_sweep(db)

    assert str(sub_id) not in seen, "trend süpürmesi alt sektörü taradı"
    assert result["total_sectors"] == len(seen)
    assert result["total_sectors"] == await db.fetchval(
        "SELECT count(*) FROM social.sectors WHERE parent_sector_id IS NULL"
    )
