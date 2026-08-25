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

import ast
import time
import uuid
from pathlib import Path

import asyncpg
import pytest
from fastapi import HTTPException
from pydantic import ValidationError

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


def _fake_anthropic(monkeypatch, raw: str, captured: dict | None = None):
    """Anthropic çağrısını sabit metinle değiştirir; istenirse argümanları yakalar."""

    class _Messages:
        def create(self, **kwargs):
            if captured is not None:
                captured["kwargs"] = kwargs
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


def _files_referencing(needle: str) -> set[str]:
    """`app/` altında verilen adı GEÇEN dosyaların depo-göreli yolları."""
    hits: set[str] = set()
    for path in sorted(APP_DIR.rglob("*.py")):
        if needle in path.read_text(encoding="utf-8"):
            hits.add(str(path.relative_to(BACKEND_ROOT)))
    return hits


def _modules_importing(symbol: str, module: str) -> set[str]:
    """`app/` altında `module`'dan `symbol`'ü İÇE AKTARAN dosyalar — AST ile.

    Metin araması değil ayrıştırılmış içe aktarma: yorumdaki ya da dizedeki
    geçişler sayılmaz, `from x import y as z` yeniden adlandırması sayılır.
    """
    hits: set[str] = set()
    for path in sorted(APP_DIR.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:  # pragma: no cover — ayrıştırılamayan dosya sweep'i durdurmasın
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == module:
                if any(alias.name == symbol for alias in node.names):
                    hits.add(str(path.relative_to(BACKEND_ROOT)))
            elif isinstance(node, ast.Import):
                if any(alias.name == module for alias in node.names):
                    hits.add(str(path.relative_to(BACKEND_ROOT)))
    return hits


async def test_generation_path_never_queries_candidates():
    """Aday kümesinin okuyucu kümesi KAPALIdır (spec §7.1 sürtünme yasağı).

    Kapı POZİTİF bir sözleşmedir: "şu iki modül içe aktarabilir", "hiçbir
    üretim yolu benzeri sorgu yazmasın" değil. İkincisi semantik bir
    olumsuzlamadır ve metin araması onu KANITLAYAMAZ.

    **Kapsam sınırı — dürüstçe:** bu kapı (a) yardımcının içe aktarılmasını
    ve (b) adının geçmesini görür. Bir üretim yolu AYNI SORGUYU elle yazsa
    (yüklem sırası değişik, `IN ('active')`, görünüm arkasına saklı) bu kapı
    onu GÖRMEZ. O sınıfın savunması review'dır, bu test değil. Kapının
    yakaladığı şey, gerçekte olan şeydir: yardımcıyı yanlış yerden çağırmak.
    """
    readers = _files_referencing("fetch_sub_sector_candidates")
    importers = _modules_importing("fetch_sub_sector_candidates", "app.routers.sectors")

    assert readers, "sweep hiçbir şey bulamadı — detektör bozuk"
    assert readers <= CANDIDATE_READER_PATHS, (
        "aday kümesi kapalı yüzey kümesi dışından okunuyor: "
        + ", ".join(sorted(readers - CANDIDATE_READER_PATHS))
    )
    assert importers <= CANDIDATE_READER_PATHS, (
        "aday yardımcısı kapalı küme dışından içe aktarılıyor: "
        + ", ".join(sorted(importers - CANDIDATE_READER_PATHS))
    )
    # Tanımın evi TEK: yardımcı yalnız bir modülde tanımlıdır.
    definitions = {
        path
        for path in _files_referencing("def fetch_sub_sector_candidates")
    }
    assert definitions == {"app/routers/sectors.py"}, (
        "aday yardımcısı birden fazla evde: " + ", ".join(sorted(definitions))
    )

    # Pozitif kontroller — detektörlerin gerçekten ölçtüğünü gösterir.
    assert "app/routers/ai.py" in importers, "AST detektörü bilinen içe aktarmayı görmüyor"
    assert "app/routers/brands.py" not in readers
    assert _files_referencing("assert_brand_owned"), "metin detektörü bilinen bir adı bulamadı"


# ─── 5. Checkpoint 15 bulguları — kapanış testleri ──────────────────────────


async def test_db_error_gate_only_claims_its_own_constraints(flow_db):
    """Hata çevirisi YALNIZ kendi kapılarını sahiplenir (F6).

    Üç GERÇEK veritabanı hatası provoke edilir ve sınıflandırıcıya sorulur —
    uydurma istisna nesnesi değil, canlı katalogdan gelen gerçeği.

    **Ölçüldü:** eksik `sub_sector_id` yabancı anahtara HİÇ ulaşmaz; BEFORE
    tetikleyicisi önce patlar (23000, kısıt adı YOK). Yabancı anahtar dalı yine
    de tanınır — tetikleyici düşerse tek savunma o kalır.

    Kritik ayak: `workspace_id` ve `sector_id` yarışları da 23503 üretir. Onları
    "geçersiz alt sektör" diye etiketlemek gerçek bir tutarlılık arızasını
    istemci girdisi hatası gibi gösterirdi.
    """
    root_id = await _root_id(flow_db)
    cases: list[tuple[str, asyncpg.PostgresError]] = []

    async def _capture(label, sql, *args):
        tx = flow_db.transaction()
        await tx.start()
        try:
            await flow_db.execute(sql, *args)
            raise AssertionError(f"{label}: beklenen hata oluşmadı")
        except asyncpg.PostgresError as exc:
            cases.append((label, exc))
        finally:
            await tx.rollback()

    await _capture(
        "trigger",
        "INSERT INTO social.brands (name, sub_sector_id) VALUES ('x', $1)",
        root_id,
    )
    await _capture(
        "sector_id_race",
        "INSERT INTO social.brands (name, sector_id) VALUES ('x', $1)",
        uuid.uuid4(),
    )
    await _capture(
        "workspace_race",
        "INSERT INTO social.brands (name, workspace_id) VALUES ('x', $1)",
        uuid.uuid4(),
    )

    verdicts = {label: brands_router._is_sub_sector_write_error(exc) for label, exc in cases}

    assert verdicts["trigger"] is True, "kendi tetikleyicisini tanımıyor"
    assert verdicts["sector_id_race"] is False, "kök sektör yarışını alt sektör hatası sandı"
    assert verdicts["workspace_race"] is False, "çalışma alanı yarışını alt sektör hatası sandı"

    # Yabancı anahtar dalı doğru adlandırılmış olmalı — migration kısıtı
    # yeniden adlandırırsa bu iddia kırmızıya döner (sessiz sapma yok).
    fkeys = {
        r["conname"]
        for r in await flow_db.fetch(
            "SELECT conname FROM pg_constraint "
            "WHERE conrelid = 'social.brands'::regclass AND contype = 'f'"
        )
    }
    assert brands_router._SUB_SECTOR_FK_CONSTRAINT in fkeys
    assert {"brands_workspace_id_fkey", "brands_sector_id_fkey"} <= fkeys


async def test_analyze_website_prompt_embeds_closed_candidate_list(flow_db, monkeypatch):
    """Aday listesi prompt'a GERÇEKTEN gömülüyor mu (F4 kanıt boşluğu).

    Doğrulama kapısının yeşil olması, listenin modele gösterildiğini KANITLAMAZ:
    listede-yoksa-boş kuralı liste hiç gönderilmese de aynı sonucu verirdi.
    Bu test modele giden argümanları yakalar.
    """
    sub_id = await _new_sub_sector(flow_db, slug="aday-prompt", display="Aday Prompt")
    await _activate_package(flow_db, sub_id)

    captured: dict = {}
    _fake_website(monkeypatch)
    _fake_anthropic(
        monkeypatch,
        '{"name": "X", "description": "", "sector": "", "colors": [], '
        '"tonality": "professional", "sub_sector": "aday-prompt"}',
        captured=captured,
    )

    await ai_router.analyze_website(
        payload=ai_router.AnalyzeWebsiteRequest(url="example.test"),
        user={"sub": "x"},
        db=flow_db,
    )

    sent = str(captured["kwargs"])
    assert "aday-prompt" in sent, "aday slug'ı modele hiç gösterilmemiş"
    assert "Aday Prompt" in sent, "aday görünen adı modele hiç gösterilmemiş"

    # Aday kümesi boşken liste bölümü HİÇ gönderilmez (modeli uydurmaya davet
    # etmemek için) — karşı kontrol.
    await flow_db.execute("DELETE FROM social.sector_packages")
    captured.clear()
    await ai_router.analyze_website(
        payload=ai_router.AnalyzeWebsiteRequest(url="example.test"),
        user={"sub": "x"},
        db=flow_db,
    )
    assert "aday-prompt" not in str(captured["kwargs"])


@pytest.mark.parametrize(
    "model_field, expected",
    [
        ('"aday-sitesiz"', True),
        ('"listede-olmayan"', False),
        ('"serbest metin"', False),
        ("null", False),
    ],
)
async def test_website_less_suggestion_uses_same_closed_list(
    flow_db, monkeypatch, model_field, expected
):
    """Web sitesiz geri düşüş AYNI kısıtla öneri üretir (spec §7.1, F3).

    Site analizi olmayan kullanıcı da modelden öneri alır; kapalı liste kuralı
    birebir aynıdır — ayrı bir gevşek yol açılmaz.
    """
    sub_id = await _new_sub_sector(flow_db, slug="aday-sitesiz", display="Aday Sitesiz")
    await _activate_package(flow_db, sub_id)

    captured: dict = {}
    _fake_anthropic(monkeypatch, '{"sub_sector": ' + model_field + "}", captured=captured)

    data = (
        await ai_router.suggest_sub_sector(
            payload=ai_router.SuggestSubSectorRequest(
                name="Sitesiz Marka", description="Kuaför salonu", sector="Hizmet"
            ),
            user={"sub": "x"},
            db=flow_db,
        )
    ).data

    if expected:
        assert data["sub_sector_id"] == str(sub_id)
        assert data["sub_sector_slug"] == "aday-sitesiz"
    else:
        assert data["sub_sector_id"] is None
        assert data["sub_sector_slug"] is None

    # Kapalı liste burada da modele gösterilir — yoksa "listeden seç" kuralı
    # yalnız sunucu tarafında var olurdu.
    assert "aday-sitesiz" in str(captured["kwargs"])


async def test_website_less_suggestion_empty_when_no_candidates(flow_db, monkeypatch):
    """Aday yokken sitesiz yol boş döner VE modeli hiç çağırmaz.

    İkinci yarı ayrıca ölçülür: doğrulayıcı zaten boş döndüreceği için çıktı
    tek başına kısa devrenin koştuğunu kanıtlamaz. Kısa devrenin amacı çıktı
    değil, sorulacak şey yokken ücretli bir çağrı YAKMAMAKtır.
    """
    await flow_db.execute("DELETE FROM social.sector_packages")
    captured: dict = {}
    _fake_anthropic(monkeypatch, '{"sub_sector": "her-ne-olursa"}', captured=captured)

    data = (
        await ai_router.suggest_sub_sector(
            payload=ai_router.SuggestSubSectorRequest(
                name="Marka", description=None, sector=None
            ),
            user={"sub": "x"},
            db=flow_db,
        )
    ).data

    assert data["sub_sector_id"] is None
    assert "kwargs" not in captured, "aday yokken model yine de çağrıldı (boşuna ücret)"


# ─── 6. Checkpoint 15 tur 2 bulguları ───────────────────────────────────────


async def test_suggest_sub_sector_bounds_its_input():
    """Girdi SINIRLI (F7). Ücretli bir uca sınırsız metin gönderilemez."""
    with pytest.raises(ValidationError):
        ai_router.SuggestSubSectorRequest(name="x" * 500)
    with pytest.raises(ValidationError):
        ai_router.SuggestSubSectorRequest(name="Marka", description="d" * 5000)
    with pytest.raises(ValidationError):
        ai_router.SuggestSubSectorRequest(name="   ")  # boş ad anlamsız çağrı

    # Makul girdi geçer — kapı her şeyi reddetmiyor.
    assert ai_router.SuggestSubSectorRequest(name="Marka", description="Kuaför").name == "Marka"


async def test_suggest_sub_sector_declares_rate_limit():
    """Uç, ev kuralındaki kota kapısını TAŞIR (F7).

    Yapısal iddia: kotayı davranışsal ölçmek Redis ister ve ev kuralı Redis
    yokken zaten fail-open'dır (`app/core/rate_limit.py` belgeli kararı) —
    yani davranışsal test burada boş bir yeşil üretirdi. Ölçülen şey, ucun
    kardeşleriyle AYNI kapıyı bildirmesidir.
    """
    from app.main import app

    routes = {
        r.path: r for r in app.routes if getattr(r, "path", None) and hasattr(r, "methods")
    }
    guarded = routes["/ai/suggest-sub-sector"]
    sibling = routes["/ai/suggest-ideas"]

    def _limiter_deps(route):
        return [
            d for d in route.dependant.dependencies
            if "_check" in getattr(d.call, "__name__", "")
        ]

    assert _limiter_deps(guarded), "yeni ücretli uçta kota kapısı YOK"
    assert _limiter_deps(sibling), "karşılaştırma dayanağı kayboldu (kardeş uç kotasız)"


async def test_suggest_sub_sector_surfaces_provider_failure(flow_db, monkeypatch):
    """Sağlayıcı arızası BAŞARI gibi dönmez (F9).

    Geçerli "eşleşme yok" ile "model çağrılamadı" aynı yanıta düşerse bozuk bir
    API anahtarı ya da sağlayıcı kesintisi kullanıcıya "uygun öneri çıkmadı"
    diye görünür ve hiçbir yerde iz bırakmaz.
    """
    sub_id = await _new_sub_sector(flow_db, slug="aday-ariza", display="Aday Arıza")
    await _activate_package(flow_db, sub_id)

    class _Boom:
        def __init__(self, **_kwargs):
            raise RuntimeError("sağlayıcı erişilemez")

    import anthropic

    monkeypatch.setattr(anthropic, "Anthropic", _Boom)

    with pytest.raises(HTTPException) as exc:
        await ai_router.suggest_sub_sector(
            payload=ai_router.SuggestSubSectorRequest(name="Marka"),
            user={"sub": "x"},
            db=flow_db,
        )
    assert exc.value.status_code == 503

    # Karşı kontrol: GEÇERLİ eşleşme-yok hâlâ 200 + boş döner, hata DEĞİL.
    _fake_anthropic(monkeypatch, '{"sub_sector": ""}')
    data = (
        await ai_router.suggest_sub_sector(
            payload=ai_router.SuggestSubSectorRequest(name="Marka"),
            user={"sub": "x"},
            db=flow_db,
        )
    ).data
    assert data["sub_sector_id"] is None


async def test_suggest_sub_sector_does_not_block_forever(flow_db, monkeypatch):
    """Asılı sağlayıcı çağrısı işçiyi süresiz TUTMAZ (F7).

    Çağrı olay döngüsünün dışında ve süre sınırlı koşar; sınır aşılırsa uç
    503 verir — yanıtsız beklemez.
    """
    sub_id = await _new_sub_sector(flow_db, slug="aday-asili", display="Aday Asılı")
    await _activate_package(flow_db, sub_id)

    monkeypatch.setattr(ai_router, "_SUGGEST_TIMEOUT_SECONDS", 0.2)

    class _Messages:
        def create(self, **_kwargs):
            time.sleep(5)  # olay döngüsünü bloklayacak kadar uzun
            raise AssertionError("zaman aşımı tetiklenmedi")

    class _Hanging:
        def __init__(self, **_kwargs):
            self.messages = _Messages()

    import anthropic

    monkeypatch.setattr(anthropic, "Anthropic", _Hanging)

    started = time.monotonic()
    with pytest.raises(HTTPException) as exc:
        await ai_router.suggest_sub_sector(
            payload=ai_router.SuggestSubSectorRequest(name="Marka"),
            user={"sub": "x"},
            db=flow_db,
        )
    elapsed = time.monotonic() - started

    assert exc.value.status_code == 503
    assert elapsed < 3, f"çağrı süre sınırına uymadı ({elapsed:.1f}s)"
