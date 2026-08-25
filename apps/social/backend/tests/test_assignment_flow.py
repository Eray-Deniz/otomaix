"""Task 15 — atama akışı: aday küme, model önerisi, teyit yazımı.

Spec §7.1-7.3'ün bağladığı üç iddia burada ölçülür:

1. **Aday kümesi = aktif paketi olan alt sektörler** (spec §7.2 kanonik tanım).
   Küme CANLI sorgudan gelir; kopya/görünüm tutulmaz — paket deaktive olduğu an
   satır listeden düşer.
2. **Model önerisi kapalıdır:** `analyze-website` dönüşündeki alt sektör alanı ya
   aday kümededir ya BOŞtur. Üçüncü dönüş biçimi (serbest metin, uydurma slug,
   liste dışı kimlik) YOKTUR — spec §7.1.
3. **Yazım yüzeyi marka oluşturma + marka ayarlarıdır** ve kök satır kabul
   etmez (K-08b tetikleyicisi 4xx'e çevrilir). Üretim akışı aday kümesini HİÇ
   okumaz (sürtünme yasağı — spec §7.1).
"""

from __future__ import annotations

import re
import uuid
from pathlib import Path

import pytest
from fastapi import HTTPException

from app.core.database import _init_connection
from app.models.schemas import BrandCreate, BrandUpdate
from app.routers import ai as ai_router
from app.routers import brands as brands_router
from app.routers import sectors as sectors_router

BACKEND_ROOT = Path(__file__).resolve().parents[1]
APP_DIR = BACKEND_ROOT / "app"

# Aday kümesini okumaya izinli KAPALI dosya kümesi (spec §7.1 sürtünme yasağı).
# `sectors.py` tanımın evi, `ai.py` öneri çağrısının tek tüketicisi.
CANDIDATE_READER_PATHS = frozenset({
    "app/routers/sectors.py",
    "app/routers/ai.py",
})


# ─── Ortak seed yardımcıları ────────────────────────────────────────────────


@pytest.fixture
async def flow_db(db):
    """Üretimin kendi bağlantı yapılandırması (jsonb codec) — router'lar onu bekler."""
    await _init_connection(db)
    return db


async def _root_id(db) -> uuid.UUID:
    root_id = await db.fetchval(
        "SELECT id FROM social.sectors WHERE parent_sector_id IS NULL ORDER BY slug LIMIT 1"
    )
    assert root_id is not None, "kök sektör seed'i eksik"
    return root_id


async def _new_sub_sector(db, *, slug: str | None = None, display: str = "Alt Sektör") -> uuid.UUID:
    return await db.fetchval(
        "INSERT INTO social.sectors (slug, display_name, parent_sector_id) "
        "VALUES ($1, $2, $3) RETURNING id",
        slug or f"alt-{uuid.uuid4().hex[:8]}",
        display,
        await _root_id(db),
    )


async def _activate_package(db, sector_id: uuid.UUID, *, version: int = 1) -> uuid.UUID:
    return await db.fetchval(
        "INSERT INTO social.sector_packages "
        "(sector_id, version, status, schema_version, content) "
        "VALUES ($1, $2, 'active', 1, $3) RETURNING id",
        sector_id,
        version,
        {"gorsel_kodlar": {}},
    )


async def _seed_owner_and_workspace(db):
    account_id = await db.fetchval(
        "INSERT INTO social.accounts (email, name, plan_id) "
        "VALUES ($1, $2, 'pro') RETURNING id",
        f"atama-{uuid.uuid4()}@example.test",
        "Atama Sahibi",
    )
    workspace_id = await db.fetchval(
        "INSERT INTO social.workspaces (account_id, name) VALUES ($1, $2) RETURNING id",
        account_id,
        "Atama Çalışma Alanı",
    )
    await db.execute(
        "INSERT INTO social.workspace_members (workspace_id, account_id) VALUES ($1, $2)",
        workspace_id,
        account_id,
    )
    return {"sub": str(account_id)}, workspace_id


def _slugs(payload) -> set[str]:
    return {row["slug"] for row in payload}


# ─── 1. Aday kümesi — kanonik tanım ─────────────────────────────────────────


async def test_candidates_only_active_packaged_sub_sectors(flow_db):
    """Aday = alt sektör VE aktif paketi olan satır; üç negatif ayrı ayrı elenir."""
    packaged = await _new_sub_sector(flow_db, slug="aday-paketli", display="Aday Paketli")
    await _activate_package(flow_db, packaged)

    # (a) paketsiz alt sektör
    await _new_sub_sector(flow_db, slug="aday-paketsiz", display="Aday Paketsiz")
    # (b) yalnız draft/archived paketi olan alt sektör
    only_draft = await _new_sub_sector(flow_db, slug="aday-taslak", display="Aday Taslak")
    await flow_db.execute(
        "INSERT INTO social.sector_packages "
        "(sector_id, version, status, schema_version, content) "
        "VALUES ($1, 1, 'draft', 1, $2), ($1, 2, 'archived', 1, $2)",
        only_draft,
        {"gorsel_kodlar": {}},
    )

    data = (await sectors_router.list_sub_sector_candidates(db=flow_db, user={"sub": "x"})).data
    slugs = _slugs(data)

    assert "aday-paketli" in slugs
    assert "aday-paketsiz" not in slugs, "paketsiz alt sektör adaya girdi"
    assert "aday-taslak" not in slugs, "aktif olmayan paket adaylık üretti"

    # (c) kök satırlar — paketi olsa bile aday DEĞİL (bölüm 6 filtresiyle ters küme)
    root_slugs = {
        row["slug"]
        for row in await flow_db.fetch(
            "SELECT slug FROM social.sectors WHERE parent_sector_id IS NULL"
        )
    }
    assert not (slugs & root_slugs), "kök sektör aday kümesine sızdı"

    # Şekil sözleşmesi: açılır liste id + görünen ad ister.
    row = next(r for r in data if r["slug"] == "aday-paketli")
    assert row["id"] == str(packaged)
    assert row["display_name"] == "Aday Paketli"


async def test_candidates_live_query_reflects_deactivation(flow_db):
    """Küme CANLI sorgudur — kopya/önbellek tutulmaz (spec §7.2)."""
    sub_id = await _new_sub_sector(flow_db, slug="aday-canli", display="Aday Canlı")
    package_id = await _activate_package(flow_db, sub_id)

    before = _slugs((await sectors_router.list_sub_sector_candidates(db=flow_db, user={"sub": "x"})).data)
    assert "aday-canli" in before

    await flow_db.execute(
        "UPDATE social.sector_packages SET status = 'archived' WHERE id = $1", package_id
    )

    after = _slugs((await sectors_router.list_sub_sector_candidates(db=flow_db, user={"sub": "x"})).data)
    assert "aday-canli" not in after, "deaktivasyondan sonra satır listede kaldı (bayat kopya)"

    # Duyarlılık: aynı sorgu yeniden aktive edilen satırı GERİ getirir.
    await flow_db.execute(
        "UPDATE social.sector_packages SET status = 'active' WHERE id = $1", package_id
    )
    again = _slugs((await sectors_router.list_sub_sector_candidates(db=flow_db, user={"sub": "x"})).data)
    assert "aday-canli" in again


async def test_empty_candidate_set_returns_empty_list(flow_db):
    """Aday yoksa yanıt BOŞ LİSTEdir — hata değil, uydurma da değil."""
    await flow_db.execute("DELETE FROM social.sector_packages")
    await _new_sub_sector(flow_db, slug="aday-yok", display="Aday Yok")

    response = await sectors_router.list_sub_sector_candidates(db=flow_db, user={"sub": "x"})

    assert response.data == []


# ─── 2. Model önerisi — kapalı doğrulama ────────────────────────────────────


class _FakeResponse:
    def __init__(self, text: str):
        self.content = [type("Block", (), {"text": text})()]


def _fake_anthropic(monkeypatch, raw: str):
    """`analyze_website` içindeki Anthropic çağrısını sabit metinle değiştirir."""

    class _Messages:
        def create(self, **_kwargs):
            return _FakeResponse(raw)

    class _Client:
        def __init__(self, **_kwargs):
            self.messages = _Messages()

    import anthropic

    monkeypatch.setattr(anthropic, "Anthropic", _Client)


def _fake_website(monkeypatch, html: str = "<html><body>Kuaför salonu</body></html>"):
    """Site indirmeyi ağa çıkmadan sabitler."""

    class _Resp:
        text = html

    class _Client:
        def __init__(self, **_kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return False

        async def get(self, *_args, **_kwargs):
            return _Resp()

    import httpx

    monkeypatch.setattr(httpx, "AsyncClient", _Client)


@pytest.mark.parametrize(
    "model_field",
    [
        '"aday-disi-slug"',        # aday kümede olmayan slug
        '"Kuaför Salonu Falan"',   # serbest metin
        '""',                      # boş
        "null",                    # tip dışı
        "123",                     # tip dışı
        '["aday-oneri"]',          # tip dışı (doğru slug'ı liste içinde göndermek de geçmez)
    ],
)
async def test_analyze_website_suggestion_must_be_in_candidates(
    flow_db, monkeypatch, model_field
):
    """Öneri ya aday kümededir ya BOŞtur — üçüncü dönüş biçimi yok (spec §7.1)."""
    sub_id = await _new_sub_sector(flow_db, slug="aday-oneri", display="Aday Öneri")
    await _activate_package(flow_db, sub_id)

    _fake_website(monkeypatch)

    # (a) Geçerli öneri: aday kümedeki slug KABUL edilir — negatiflerin
    #     boş çıkması, alanın hiç dolmamasından değil, filtreden gelmeli.
    _fake_anthropic(
        monkeypatch,
        '{"name": "X", "description": "", "sector": "Hizmet", "colors": [], '
        '"tonality": "professional", "sub_sector": "aday-oneri"}',
    )
    accepted = (
        await ai_router.analyze_website(
            payload=ai_router.AnalyzeWebsiteRequest(url="example.test"),
            user={"sub": "x"},
            db=flow_db,
        )
    ).data
    assert accepted["sub_sector_id"] == str(sub_id)
    assert accepted["sub_sector_slug"] == "aday-oneri"
    assert accepted["sub_sector_display_name"] == "Aday Öneri"

    # (b) Aday dışı / serbest metin / tip dışı → alan BOŞ.
    _fake_anthropic(
        monkeypatch,
        '{"name": "X", "description": "", "sector": "Hizmet", "colors": [], '
        '"tonality": "professional", "sub_sector": ' + model_field + "}",
    )
    rejected = (
        await ai_router.analyze_website(
            payload=ai_router.AnalyzeWebsiteRequest(url="example.test"),
            user={"sub": "x"},
            db=flow_db,
        )
    ).data
    assert rejected["sub_sector_id"] is None, f"aday dışı öneri geçti: {model_field}"
    assert rejected["sub_sector_slug"] is None
    # Öneri reddedilse bile çağrının geri kalanı bozulmaz.
    assert rejected["name"] == "X"


async def test_analyze_website_suggestion_empty_when_no_candidates(flow_db, monkeypatch):
    """Aday kümesi boşken öneri HER ZAMAN boştur — model ne derse desin."""
    await flow_db.execute("DELETE FROM social.sector_packages")

    _fake_website(monkeypatch)
    _fake_anthropic(
        monkeypatch,
        '{"name": "X", "description": "", "sector": "Hizmet", "colors": [], '
        '"tonality": "professional", "sub_sector": "her-ne-olursa"}',
    )

    data = (
        await ai_router.analyze_website(
            payload=ai_router.AnalyzeWebsiteRequest(url="example.test"),
            user={"sub": "x"},
            db=flow_db,
        )
    ).data

    assert data["sub_sector_id"] is None
    assert data["sub_sector_slug"] is None


# ─── 3. Yazım yüzeyi ────────────────────────────────────────────────────────


async def test_brand_create_and_update_sub_sector_roundtrip_via_api(flow_db):
    """Alan uçtan uca taşınır: yaz (create) → oku → değiştir → BOŞALT.

    Boşaltma ayrı bir ayaktır: `BrandUpdate` `exclude_none` ile serileşiyor,
    yani açıkça gönderilen `null` sessizce DÜŞERSE kullanıcı yanlış atamasını
    hiçbir zaman geri alamaz (spec §7.5 düzeltme yolu).
    """
    user, workspace_id = await _seed_owner_and_workspace(flow_db)
    first = await _new_sub_sector(flow_db, slug="atama-bir", display="Atama Bir")
    second = await _new_sub_sector(flow_db, slug="atama-iki", display="Atama İki")
    await _activate_package(flow_db, first)
    await _activate_package(flow_db, second)

    created = (
        await brands_router.create_brand(
            payload=BrandCreate(
                workspace_id=workspace_id,
                name="Atama Markası",
                sub_sector_id=first,
            ),
            user=user,
            db=flow_db,
        )
    ).data
    brand_id = created["id"]
    assert created["sub_sector_id"] == first

    read_back = (await brands_router.get_brand(brand_id=brand_id, user=user, db=flow_db)).data
    assert read_back["sub_sector_id"] == first

    changed = (
        await brands_router.update_brand(
            brand_id=brand_id,
            payload=BrandUpdate(sub_sector_id=second),
            user=user,
            db=flow_db,
        )
    ).data
    assert changed["sub_sector_id"] == second

    cleared = (
        await brands_router.update_brand(
            brand_id=brand_id,
            payload=BrandUpdate(sub_sector_id=None),
            user=user,
            db=flow_db,
        )
    ).data
    assert cleared["sub_sector_id"] is None, "açık null boşaltmayı yapmadı"

    # Boşaltma yalnız ALANI etkiler: başka alan gönderilmediğinde ad korunur.
    assert cleared["name"] == "Atama Markası"

    # Karşı kontrol: alanı HİÇ göndermeyen güncelleme atamayı SİLMEZ.
    await brands_router.update_brand(
        brand_id=brand_id,
        payload=BrandUpdate(sub_sector_id=second),
        user=user,
        db=flow_db,
    )
    untouched = (
        await brands_router.update_brand(
            brand_id=brand_id, payload=BrandUpdate(name="Yeni Ad"), user=user, db=flow_db
        )
    ).data
    assert untouched["sub_sector_id"] == second, "ilgisiz güncelleme atamayı düşürdü"


async def test_brand_update_rejects_root_as_sub_sector(flow_db):
    """Kök satır ataması 4xx'e çevrilir — 500 değil (K-08b tetikleyicisi)."""
    user, workspace_id = await _seed_owner_and_workspace(flow_db)
    root_id = await _root_id(flow_db)

    created = (
        await brands_router.create_brand(
            payload=BrandCreate(workspace_id=workspace_id, name="Kök Deneme"),
            user=user,
            db=flow_db,
        )
    ).data

    with pytest.raises(HTTPException) as exc:
        await brands_router.update_brand(
            brand_id=created["id"],
            payload=BrandUpdate(sub_sector_id=root_id),
            user=user,
            db=flow_db,
        )
    assert 400 <= exc.value.status_code < 500

    # Yaratma yüzeyi de aynı kapıdan geçer — tek yüzeyi korumak yetmez.
    with pytest.raises(HTTPException) as exc_create:
        await brands_router.create_brand(
            payload=BrandCreate(
                workspace_id=workspace_id, name="Kök Yaratma", sub_sector_id=root_id
            ),
            user=user,
            db=flow_db,
        )
    assert 400 <= exc_create.value.status_code < 500

    # Var olmayan sektör kimliği de aynı sınıftır (FK ihlali → 4xx).
    with pytest.raises(HTTPException) as exc_missing:
        await brands_router.update_brand(
            brand_id=created["id"],
            payload=BrandUpdate(sub_sector_id=uuid.uuid4()),
            user=user,
            db=flow_db,
        )
    assert 400 <= exc_missing.value.status_code < 500

    # Reddedilen yazımdan sonra satır DEĞİŞMEMİŞ olmalı.
    assert await flow_db.fetchval(
        "SELECT sub_sector_id FROM social.brands WHERE id = $1", created["id"]
    ) is None


# ─── 4. Üretim akışı aday kümesini okumaz ───────────────────────────────────


# Aday sorgusunun İMZASI: alt-sektörlük sorusu ile AKTİF PAKET şartının aynı
# ifadede birleşmesi. Yalnız `parent_sector_id` aramak yetmez — `brands.py`'deki
# atanabilirlik kapısı da o soruyu sorar ve orada olması DOĞRUdur (K-08b'nin
# uygulama ayağı); aday kümesi olan şey, ikinci yarısıdır.
_CANDIDATE_QUERY_RE = re.compile(
    r"parent_sector_id\s+IS\s+NOT\s+NULL.{0,400}?status\s*=\s*\'active\'",
    re.DOTALL,
)


def _has_candidate_query(rel_path: str) -> bool:
    return bool(
        _CANDIDATE_QUERY_RE.search((BACKEND_ROOT / rel_path).read_text(encoding="utf-8"))
    )


def _files_referencing(needle: str) -> set[str]:
    """`app/` altında verilen adı GEÇEN dosyaların depo-göreli yolları."""
    hits: set[str] = set()
    for path in sorted(APP_DIR.rglob("*.py")):
        if needle in path.read_text(encoding="utf-8"):
            hits.add(str(path.relative_to(BACKEND_ROOT)))
    return hits


async def test_generation_path_never_queries_candidates():
    """Aday kümesi TEK yerde tanımlanır ve yalnız iki yüzeyden okunur.

    Yapısal sweep — örneklem değil: `app/` altındaki HER python dosyası taranır.
    Üretim yolu (caption / görsel / kısa video / post yazımı) aday kümesine
    dokunursa üretim akışına soru eklenmiş olur (spec §7.1 sürtünme yasağı).
    """
    readers = _files_referencing("fetch_sub_sector_candidates")

    assert readers, "sweep hiçbir şey bulamadı — detektör bozuk"
    assert readers <= CANDIDATE_READER_PATHS, (
        "aday kümesi kapalı yüzey kümesi dışından okunuyor: "
        + ", ".join(sorted(readers - CANDIDATE_READER_PATHS))
    )
    # Tanım gerçekten TEK evde: sorgunun kendisi kopyalanmamış.
    definitions = {
        path for path in _files_referencing("parent_sector_id") if _has_candidate_query(path)
    }
    assert definitions == {"app/routers/sectors.py"}, (
        "aday sorgusu birden fazla evde: " + ", ".join(sorted(definitions))
    )

    # Pozitif kontroller — detektörün gerçekten ayrım yaptığını kanıtlar.
    assert "app/routers/brands.py" not in readers
    assert _files_referencing("assert_brand_owned"), "detektör bilinen bir adı bulamadı"
    # (a) Aday sorgusunun KOPYASI yakalanır.
    assert _CANDIDATE_QUERY_RE.search(
        "WHERE s.parent_sector_id IS NOT NULL AND EXISTS ("
        "SELECT 1 FROM social.sector_packages p WHERE p.status = \'active\')"
    ), "detektör aday sorgusunun kopyasını görmüyor"
    # (b) Alt-sektörlük sorusu TEK BAŞINA aday sorgusu SAYILMAZ — `brands.py`
    #     atanabilirlik kapısı meşru olarak bunu sorar (K-08b uygulama ayağı).
    assert not _CANDIDATE_QUERY_RE.search(
        "SELECT parent_sector_id IS NOT NULL FROM social.sectors WHERE id = $1"
    ), "detektör atanabilirlik kapısını aday sorgusu sanıyor"
