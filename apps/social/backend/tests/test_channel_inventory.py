"""Task 9 — kanal envanteri: `brand_kit.channels` + deterministik CTA filtresi.

Üç bağlayıcı iddia sınanır:

1. **Filtre muhafazakârdır** (spec §12.2): `[kanal-bağımlı: X]` etiketli kalıp
   YALNIZ markanın envanterinde `X` doğrulanmışsa geçer. Envanter yok, boş,
   bozuk, `False`, `"true"` ya da `1` ise kalıp ATLANIR. Etiketsiz kalıp her
   zaman geçer.
2. **Anahtar uzayı KAPALIDIR** (`CHANNEL_KEYS`) ve kapalılık, çağıranın
   veri verebildiği HER yüzeyde geçerlidir — tek bir yüzeyi korumak yetmez,
   ikinci yüzey kapalılığı yalana çevirir (yapısal sweep testi bunu ölçer).
3. **Yazım uçtan uca çalışır**: Pydantic'in bilinmeyen alanı sessizce düşürme
   sınıfına karşı pozitif kontrol — API'den yazılan `channels` geri okunur.

Etiket tanıma ile kanal doğrulaması BİLİNÇLİ olarak asimetriktir: etiket
GENİŞ tanınır (her Unicode/büyük-küçük yazımı), kanal DAR doğrulanır (tam
`True`). İkisi de aynı yöne — atlama yönüne — çalışır.
"""

from __future__ import annotations

import ast
import inspect
import itertools
import uuid
from pathlib import Path

import pytest
from fastapi import HTTPException

from app.core.database import _init_connection
from app.core.utils import parse_brand_kit
from app.models.schemas import BrandKitUpdate, BrandUpdate
from app.routers import brands as brands_router
from app.services.sector_packages import CHANNEL_KEYS, filter_channel_dependent

BACKEND_ROOT = Path(__file__).resolve().parents[1]
BRANDS_ROUTER_PATH = BACKEND_ROOT / "app" / "routers" / "brands.py"

# Çağıranın brand_kit içeriği verebildiği şema tipleri. Bu tipleri parametre
# olarak alan HER handler kanal kapısından geçmek ZORUNDADIR.
CALLER_SUPPLIED_KIT_MODELS = frozenset({"BrandUpdate", "BrandKitUpdate"})

# Router'daki kapı fonksiyonunun adı — yapısal sweep bunu arar.
CHANNEL_GUARD_NAME = "_assert_valid_channels"


def cta(kalip: str) -> dict:
    """Doğrulayıcının kabul ettiği şekle sadık CTA öğesi (spec §3.4)."""
    return {"kalip": kalip, "tur": "yonlendirme", "gerekce": "test"}


# ─── 1. Deterministik filtre ────────────────────────────────────────────────


def test_filter_drops_tagged_without_channel():
    """Etiketli kalıp, kanal doğrulanmadıkça geçmez."""
    items = [cta("WhatsApp'tan yaz [kanal-bağımlı: whatsapp_hatti]")]

    assert filter_channel_dependent(items, {"whatsapp_hatti": False}) == []


def test_filter_passes_tagged_with_channel_true():
    """Kanal `True` ise etiketli kalıp AYNEN geçer — etiket silinmez."""
    item = cta("WhatsApp'tan yaz [kanal-bağımlı: whatsapp_hatti]")

    result = filter_channel_dependent([item], {"whatsapp_hatti": True})

    assert result == [item]
    assert "[kanal-bağımlı: whatsapp_hatti]" in result[0]["kalip"]


def test_filter_conservative_when_channels_missing():
    """Envanter hiç doldurulmamışsa etiketli kalıp ATLANIR (spec §12.2)."""
    items = [cta("Mağazaya bekleriz [kanal-bağımlı: fiziksel_magaza]")]

    assert filter_channel_dependent(items, None) == []
    assert filter_channel_dependent(items, {}) == []


def test_untagged_always_passes():
    """Etiketsiz kalıp envanterden bağımsız geçer."""
    items = [cta("Yorumlara yaz"), cta("Profildeki bağlantıya bak")]

    assert filter_channel_dependent(items, None) == items
    assert filter_channel_dependent(items, {"whatsapp_hatti": True}) == items


def test_filter_preserves_order_and_identity():
    """Filtre seçer; sıralamayı ve öğe kimliğini DEĞİŞTİRMEZ."""
    a = cta("etiketsiz bir")
    b = cta("randevu al [kanal-bağımlı: randevu_sistemi]")
    c = cta("etiketsiz iki")

    result = filter_channel_dependent([a, b, c], {"randevu_sistemi": True})

    assert result == [a, b, c]
    assert [id(x) for x in result] == [id(a), id(b), id(c)]


def test_filter_drops_unknown_channel_key_in_tag():
    """Kapalı uzay dışındaki `X` tanınmaz → kalıp atlanır (fail-closed).

    Kritik nokta: bilinmeyen anahtar "etiketsiz" sayılıp GEÇMEZ. Öyle olsaydı
    uzayın kapalılığı filtreyi delip geçmenin yolu olurdu.
    """
    items = [cta("Telegram'dan yaz [kanal-bağımlı: telegram]")]

    assert filter_channel_dependent(items, {"telegram": True}) == []


def test_filter_requires_every_tag_on_multi_tagged_item():
    """Bir kalıp iki kanal iddia ediyorsa İKİSİ de doğrulanmalı."""
    item = cta(
        "Mağazada dene [kanal-bağımlı: fiziksel_magaza], "
        "sonra siteden al [kanal-bağımlı: eticaret_sitesi]"
    )

    assert filter_channel_dependent([item], {"fiziksel_magaza": True}) == []
    assert filter_channel_dependent(
        [item], {"fiziksel_magaza": True, "eticaret_sitesi": True}
    ) == [item]


def test_filter_finds_tag_in_any_item_field():
    """Etiket `kalip` dışındaki alanda dursa da kalıp kanal-bağımlıdır."""
    item = {
        "kalip": "Randevunu ayırt",
        "tur": "yonlendirme",
        "gerekce": "randevu akışı gerektirir [kanal-bağımlı: randevu_sistemi]",
    }

    assert filter_channel_dependent([item], None) == []
    assert filter_channel_dependent([item], {"randevu_sistemi": True}) == [item]


def test_filter_returns_empty_for_non_list_input():
    """Liste olmayan girdi → boş sonuç (fail-closed; üretim akışı kırılmaz)."""
    for bad in (None, "içerik-önerilmez", {"kalip": "x"}, 7):
        assert filter_channel_dependent(bad, {"whatsapp_hatti": True}) == []


def test_filter_drops_tagged_when_channels_not_a_dict():
    """Bozuk envanter (liste/metin/sayı) = envanter YOK gibi davranır."""
    items = [cta("WhatsApp [kanal-bağımlı: whatsapp_hatti]")]

    for bad in ([], ["whatsapp_hatti"], "whatsapp_hatti", 1, True):
        assert filter_channel_dependent(items, bad) == []


def test_filter_keeps_non_dict_items_untagged():
    """`içerik-önerilmez` gibi metin öğesi etiketsizdir → geçer; şekli bozulmaz."""
    sentinel = "içerik-önerilmez"

    assert filter_channel_dependent([sentinel], None) == [sentinel]
    assert filter_channel_dependent(
        [f"{sentinel} [kanal-bağımlı: whatsapp_hatti]"], None
    ) == []


# ─── 1b. Kapanış matrisi (elle seçilmiş örnek DEĞİL — üretilmiş uzay) ───────

# Etiketin yazım uzayı: büyük/küçük harf · Türkçe harf · boşluk · anahtar yazımı.
# Her biri AYNI etiket sınıfıdır; hiçbiri "etiketsiz" sayılamaz.
TAG_SPELLINGS = (
    "[kanal-bağımlı: {key}]",
    "[KANAL-BAĞIMLI: {key}]",
    "[Kanal-Bağımlı: {key}]",
    "[kanal-bagimli: {key}]",
    "[KANAL-BAGIMLI: {key}]",
    "[kanal-bağımlı:{key}]",
    "[kanal-bağımlı:  {key}  ]",
    "[ kanal-bağımlı : {key} ]",
    "[kanal - bağımlı: {key}]",
)

# Anahtarın yazım uzayı — kanonik biçime indirgenmeli.
KEY_FORMS = (
    lambda k: k,
    lambda k: k.upper(),
    lambda k: k.capitalize(),
    lambda k: f" {k} ",
)

# Kanal değerinin uzayı: yalnız gerçek `True` geçirir.
CHANNEL_VALUES = (
    (True, True),
    (False, False),
    (None, False),
    ("true", False),
    ("evet", False),
    (1, False),
    (0, False),
    ([], False),
)


@pytest.mark.parametrize("key", sorted(CHANNEL_KEYS))
def test_tag_spelling_matrix_is_closed(key):
    """Yazım × değer çaprazının TAMAMI: tanıma geniş, geçirme dar.

    Elle seçilmiş üç örnek "sınıf kapandı" demek için yetmez (2026-08-24
    dersi) — biçim uzayını testin kendisi üretir. Kaçan tek bir yazım,
    kanal-bağımlı bir CTA'nın doğrulanmamış markaya sızması demektir.
    """
    escapes: list[tuple[str, object]] = []

    for tag_form, key_form, (value, should_pass) in itertools.product(
        TAG_SPELLINGS, KEY_FORMS, CHANNEL_VALUES
    ):
        written = tag_form.format(key=key_form(key))
        item = cta(f"Bir kalıp {written}")
        passed = filter_channel_dependent([item], {key: value}) == [item]
        if passed != should_pass:
            escapes.append((written, value))

    assert not escapes, f"kaçan yazım/değer çifti: {escapes[:5]}"


def test_matrix_has_no_false_positive_on_ordinary_text():
    """Yanlış-pozitif kontrolü: sıradan metin etiket sayılmaz."""
    innocuous = [
        cta("Kanal bağımlılığı yaratmayın"),
        cta("kanal-bağımlı bir kampanya kurgusu"),  # köşeli parantez YOK
        cta("[not: kanal-bağımlı değil]"),
        cta("[kanal-bagimsiz: whatsapp_hatti]"),
    ]

    assert filter_channel_dependent(innocuous, None) == innocuous


# ─── 2. Kapalı anahtar uzayı — yazım kapısı ────────────────────────────────


async def _seed_owner_and_brand(db, brand_kit: dict | None = None):
    """Sahiplik zinciri: account → workspace → membership → brand."""
    account_id = await db.fetchval(
        "INSERT INTO social.accounts (email, name, plan_id) "
        "VALUES ($1, $2, 'pro') RETURNING id",
        f"kanal-{uuid.uuid4()}@example.test",
        "Kanal Sahibi",
    )
    workspace_id = await db.fetchval(
        "INSERT INTO social.workspaces (account_id, name) VALUES ($1, $2) RETURNING id",
        account_id,
        "Kanal Çalışma Alanı",
    )
    await db.execute(
        "INSERT INTO social.workspace_members (workspace_id, account_id) VALUES ($1, $2)",
        workspace_id,
        account_id,
    )
    brand_id = await db.fetchval(
        "INSERT INTO social.brands (workspace_id, name, brand_kit) "
        "VALUES ($1, $2, $3) RETURNING id",
        workspace_id,
        "Kanal Markası",
        brand_kit if brand_kit is not None else {"tonality": "professional"},
    )
    return {"sub": str(account_id)}, brand_id


@pytest.fixture
async def kit_db(db, monkeypatch):
    """Üretimin kendi bağlantı yapılandırması + Redis'siz önbellek boşaltma."""
    await _init_connection(db)

    async def _noop(_pattern):
        return None

    monkeypatch.setattr(brands_router, "invalidate_pattern", _noop)
    return db


async def test_brand_kit_rejects_unknown_channel_key(kit_db):
    """Kapalı uzay dışındaki anahtar 400 ile reddedilir — DB'ye ULAŞMAZ."""
    user, brand_id = await _seed_owner_and_brand(kit_db)

    with pytest.raises(HTTPException) as exc:
        await brands_router.update_brand_kit(
            brand_id=brand_id,
            payload=BrandKitUpdate(channels={"telegram": True}),
            user=user,
            db=kit_db,
        )

    assert exc.value.status_code == 400
    assert "telegram" in str(exc.value.detail)

    stored = parse_brand_kit(
        await kit_db.fetchval("SELECT brand_kit FROM social.brands WHERE id = $1", brand_id)
    )
    assert "channels" not in stored


async def test_brand_kit_rejects_non_boolean_channel_value(kit_db):
    """Değer `True`/`False` değilse reddedilir.

    Filtre `is True` arar; `"true"` metni sessizce hiçbir zaman geçmezdi —
    operatör kanalı açtığını sanır, CTA'lar sessizce düşerdi. Kapı, sessiz
    yanlış-yapılandırmayı görünür hataya çevirir.
    """
    user, brand_id = await _seed_owner_and_brand(kit_db)

    with pytest.raises(HTTPException) as exc:
        await brands_router.update_brand_kit(
            brand_id=brand_id,
            payload=BrandKitUpdate(channels={"whatsapp_hatti": "true"}),
            user=user,
            db=kit_db,
        )

    assert exc.value.status_code == 400


async def test_brand_kit_rejects_non_dict_channels(kit_db):
    """`channels` nesne değilse reddedilir."""
    user, brand_id = await _seed_owner_and_brand(kit_db)

    with pytest.raises(HTTPException):
        await brands_router.update_brand(
            brand_id=brand_id,
            payload=BrandUpdate(brand_kit={"channels": ["whatsapp_hatti"]}),
            user=user,
            db=kit_db,
        )


async def test_brand_kit_channels_roundtrip_via_api(kit_db):
    """Yazılan `channels` geri okunur — Pydantic sessiz-düşürme pozitif kontrolü."""
    user, brand_id = await _seed_owner_and_brand(kit_db)
    payload_channels = {"whatsapp_hatti": True, "fiziksel_magaza": False}

    response = await brands_router.update_brand_kit(
        brand_id=brand_id,
        payload=BrandKitUpdate(channels=payload_channels),
        user=user,
        db=kit_db,
    )

    assert parse_brand_kit(response.data["brand_kit"])["channels"] == payload_channels

    stored = parse_brand_kit(
        await kit_db.fetchval("SELECT brand_kit FROM social.brands WHERE id = $1", brand_id)
    )
    assert stored["channels"] == payload_channels
    # Mevcut alanlar korunur — channels yazımı brand_kit'i sıfırlamaz.
    assert stored["tonality"] == "professional"


async def test_brand_kit_channels_partial_update_preserves_others(kit_db):
    """Kısmi güncelleme diğer kanalları SİLMEZ (deep-merge; spec §12.2).

    Sığ birleştirme olsaydı tek anahtarlık bir güncelleme markanın doğrulanmış
    öbür kanallarını sessizce düşürürdü — filtre muhafazakâr olduğu için sonuç
    "CTA'lar sessizce kayboldu" olurdu.
    """
    user, brand_id = await _seed_owner_and_brand(
        kit_db,
        {"tonality": "professional", "channels": {"fiziksel_magaza": True}},
    )

    await brands_router.update_brand_kit(
        brand_id=brand_id,
        payload=BrandKitUpdate(channels={"whatsapp_hatti": True}),
        user=user,
        db=kit_db,
    )

    stored = parse_brand_kit(
        await kit_db.fetchval("SELECT brand_kit FROM social.brands WHERE id = $1", brand_id)
    )
    assert stored["channels"] == {"fiziksel_magaza": True, "whatsapp_hatti": True}


async def test_brand_update_surface_also_validates_channels(kit_db):
    """İkinci yazım yüzeyi (`PATCH /brands/{id}`) de kapıdan geçer.

    `update_brand` brand_kit'i BÜTÜN olarak yazar. Yalnız `update_brand_kit`
    korunsaydı kapalı uzay bu yüzeyden delinirdi — kapalılık iddiası yalan
    olurdu (varyant değil sınıf kapatılır).
    """
    user, brand_id = await _seed_owner_and_brand(kit_db)

    with pytest.raises(HTTPException) as exc:
        await brands_router.update_brand(
            brand_id=brand_id,
            payload=BrandUpdate(brand_kit={"channels": {"telegram": True}}),
            user=user,
            db=kit_db,
        )

    assert exc.value.status_code == 400

    stored = parse_brand_kit(
        await kit_db.fetchval("SELECT brand_kit FROM social.brands WHERE id = $1", brand_id)
    )
    assert "channels" not in stored


async def test_brand_update_surface_accepts_valid_channels(kit_db):
    """Pozitif kontrol: kapı geçerli envanteri REDDETMİYOR."""
    user, brand_id = await _seed_owner_and_brand(kit_db)

    await brands_router.update_brand(
        brand_id=brand_id,
        payload=BrandUpdate(brand_kit={"channels": {"eticaret_sitesi": True}}),
        user=user,
        db=kit_db,
    )

    stored = parse_brand_kit(
        await kit_db.fetchval("SELECT brand_kit FROM social.brands WHERE id = $1", brand_id)
    )
    assert stored["channels"] == {"eticaret_sitesi": True}


# ─── 3. Kapanışın yapısal kanıtı ───────────────────────────────────────────


def test_every_caller_supplied_kit_surface_calls_the_guard():
    """Çağıranın kit içeriği verebildiği HER handler kanal kapısını çağırır.

    Elle sayılmış iki yüzey yerine kaynağın kendisi taranır: yarın üçüncü bir
    handler `BrandUpdate` alırsa bu test kırmızıya döner.
    """
    tree = ast.parse(BRANDS_ROUTER_PATH.read_text(encoding="utf-8"))
    unguarded = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            continue
        annotations = {
            arg.annotation.id
            for arg in node.args.args + node.args.kwonlyargs
            if isinstance(arg.annotation, ast.Name)
        }
        if not (annotations & CALLER_SUPPLIED_KIT_MODELS):
            continue
        calls = {
            inner.func.id
            for inner in ast.walk(node)
            if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name)
        }
        if CHANNEL_GUARD_NAME not in calls:
            unguarded.append(node.name)

    assert not unguarded, f"kanal kapısından geçmeyen handler: {unguarded}"


def test_guarded_surface_set_is_not_empty():
    """Yukarıdaki sweep'in pozitif kontrolü — boş kümede yeşil kalmasın."""
    tree = ast.parse(BRANDS_ROUTER_PATH.read_text(encoding="utf-8"))
    surfaces = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef))
        and {
            arg.annotation.id
            for arg in node.args.args + node.args.kwonlyargs
            if isinstance(arg.annotation, ast.Name)
        }
        & CALLER_SUPPLIED_KIT_MODELS
    ]

    assert sorted(surfaces) == ["update_brand", "update_brand_kit"]


def test_caller_supplied_kit_models_are_used_only_in_brands_router():
    """Kit şemaları başka bir router'da kullanılmıyor — sweep tam kapsıyor."""
    strays = []
    for path in (BACKEND_ROOT / "app").rglob("*.py"):
        if path == BRANDS_ROUTER_PATH:
            continue
        source = path.read_text(encoding="utf-8")
        for model in CALLER_SUPPLIED_KIT_MODELS:
            if model in source and "schemas.py" not in str(path):
                strays.append(f"{path.relative_to(BACKEND_ROOT)}:{model}")

    assert not strays, f"kit şeması router dışında da kullanılıyor: {strays}"


def test_channel_keys_are_the_documented_closed_set():
    """Kapalı küme spec §12.2 ile birebir."""
    assert CHANNEL_KEYS == frozenset(
        {"whatsapp_hatti", "fiziksel_magaza", "randevu_sistemi", "eticaret_sitesi"}
    )


def test_filter_signature_takes_channels_optional():
    """Sözleşme imzası: `(items, channels)` — `channels` opsiyonel değil, açık."""
    params = list(inspect.signature(filter_channel_dependent).parameters)
    assert params == ["items", "channels"]


# ─── 4. Checkpoint 9 bulguları — kapatılan iki sınıf ────────────────────────

# Etiketi "insan gözüyle aynı" ama baytça farklı yazan karakter sınıfları.
# Hepsi paket içeriğine GERÇEKÇİ yollarla girer: Word/LLM kopyası tire yerine
# uzun tire basar, biçimlendirme görünmez karakter bırakır. Sınıfın adı:
# "okunuşu etiket olan ama ASCII'ye eşit olmayan işaret".
MARKER_VARIANTS = {
    "u2010 hyphen": "‐",
    "u2011 non-breaking hyphen": "‑",
    "u2012 figure dash": "‒",
    "u2013 en dash": "–",
    "u2014 em dash": "—",
    "u2015 horizontal bar": "―",
    "u2212 minus sign": "−",
    "ufe58 small em dash": "﹘",
    "ufe63 small hyphen": "﹣",
    "uff0d fullwidth hyphen": "－",
}

INVISIBLE_VARIANTS = {
    "u00ad soft hyphen": "­",
    "u200b zero width space": "​",
    "u200c zero width non-joiner": "‌",
    "u200d zero width joiner": "‍",
    "ufeff bom": "﻿",
    "u2060 word joiner": "⁠",
}

SPACE_VARIANTS = {
    "u00a0 nbsp": " ",
    "u2009 thin space": " ",
    "u202f narrow nbsp": " ",
}


@pytest.mark.parametrize("channels", [None, {"whatsapp_hatti": True}])
def test_marker_variant_matrix_is_recognized_as_tag(channels):
    """Etiketin yazım SINIFI kapanır — tek tek varyant yamalanmaz.

    Checkpoint 9 bulgusu: kalıp yalnız ASCII `-` kabul ediyordu; U+2011/2013/
    2014/2212 ve görünmez karakterler etiketi GÖRÜNMEZ kılıyordu, yani kalıp
    "etiketsiz" sayılıp doğrulanmamış markaya SIZIYORDU (ölçüldü: 9 sondanın
    6'sı sızdı). Tanınmayan bir yazım = sızıntı, o yüzden tanıma tarafı sınıfın
    tamamını kapsamalıdır.
    """
    expected = [] if channels is None else "passthrough"
    escapes: list[str] = []

    for name, ch in MARKER_VARIANTS.items():
        item = cta(f"Yaz [kanal{ch}bağımlı: whatsapp_hatti]")
        result = filter_channel_dependent([item], channels)
        if result != ([] if expected == [] else [item]):
            escapes.append(f"tire/{name}")

    for name, ch in INVISIBLE_VARIANTS.items():
        item = cta(f"Yaz [kanal-bağ{ch}ımlı: whatsapp_hatti]")
        result = filter_channel_dependent([item], channels)
        if result != ([] if expected == [] else [item]):
            escapes.append(f"görünmez/{name}")

    for name, ch in SPACE_VARIANTS.items():
        item = cta(f"Yaz [kanal-bağımlı:{ch}whatsapp_hatti]")
        result = filter_channel_dependent([item], channels)
        if result != ([] if expected == [] else [item]):
            escapes.append(f"boşluk/{name}")

    assert not escapes, f"etiket olarak tanınmayan yazım: {escapes}"


def test_invisible_characters_inside_channel_key_are_canonicalized():
    """Anahtarın İÇİNDEKİ görünmez karakter de kanonikleşir."""
    item = cta("Yaz [kanal-bağımlı: whats​app_hatti]")

    assert filter_channel_dependent([item], None) == []
    assert filter_channel_dependent([item], {"whatsapp_hatti": True}) == [item]


def test_marker_canonicalization_does_not_invent_tags():
    """Kanonikleştirme yanlış-pozitif üretmez — yakın ama etiket olmayan metin."""
    innocuous = [
        cta("kanal—bağımsız bir kurgu"),
        cta("[kanal–bagimsiz: whatsapp_hatti]"),
        cta("kanal‑bağımlı: whatsapp_hatti"),  # köşeli parantez YOK
    ]

    assert filter_channel_dependent(innocuous, None) == innocuous


async def test_concurrent_channel_writes_do_not_lose_keys(test_db_setup, monkeypatch):
    """Eşzamanlı kit yazımı kanal kaybettirmez (checkpoint 9 high bulgusu).

    Ölçülmüş kusur: handler `SELECT brand_kit` → Python'da birleştir →
    `UPDATE brand_kit = <tam belge>` yapıyordu. Dört eşzamanlı PATCH aynı tabanı
    okuyup birbirini eziyordu; ölçüm: 4 anahtardan 3'ü KAYBOLDU. Kayıp sessizdi
    ve filtre muhafazakâr olduğu için sonucu "CTA'lar sebepsiz kayboldu" olurdu.

    Bu test kendi bağlantılarını açar (oturum fixture'ı tek bağlantıyı bir
    transaction'da tutar; eşzamanlılık ancak ayrı bağlantılarla ölçülür) ve
    ürettiği satırları `finally`de siler — `otomaix_test` kirlenmez.
    """
    import asyncio

    import asyncpg

    from .conftest import _require_test_database

    url = _require_test_database(test_db_setup)

    async def _noop(_pattern):
        return None

    monkeypatch.setattr(brands_router, "invalidate_pattern", _noop)

    setup = await asyncpg.connect(url)
    await _init_connection(setup)
    account_id = workspace_id = brand_id = None
    workers: list = []
    try:
        account_id = await setup.fetchval(
            "INSERT INTO social.accounts (email, name, plan_id) "
            "VALUES ($1, 'Yarış Sahibi', 'pro') RETURNING id",
            f"yaris-{uuid.uuid4()}@example.test",
        )
        workspace_id = await setup.fetchval(
            "INSERT INTO social.workspaces (account_id, name) VALUES ($1, 'Yarış') RETURNING id",
            account_id,
        )
        await setup.execute(
            "INSERT INTO social.workspace_members (workspace_id, account_id) VALUES ($1, $2)",
            workspace_id,
            account_id,
        )
        brand_id = await setup.fetchval(
            "INSERT INTO social.brands (workspace_id, name, brand_kit) "
            "VALUES ($1, 'Yarış Markası', $2) RETURNING id",
            workspace_id,
            {"tonality": "professional"},
        )

        keys = sorted(CHANNEL_KEYS)
        for _ in keys:
            worker = await asyncpg.connect(url)
            await _init_connection(worker)
            workers.append(worker)

        await asyncio.gather(
            *[
                brands_router.update_brand_kit(
                    brand_id=brand_id,
                    payload=BrandKitUpdate(channels={key: True}),
                    user={"sub": str(account_id)},
                    db=worker,
                )
                for key, worker in zip(keys, workers)
            ]
        )

        stored = parse_brand_kit(
            await setup.fetchval("SELECT brand_kit FROM social.brands WHERE id = $1", brand_id)
        )
        assert sorted(stored.get("channels", {})) == keys, "eşzamanlı yazımda kanal KAYBOLDU"
        assert stored["tonality"] == "professional"
    finally:
        for worker in workers:
            await worker.close()
        if brand_id:
            await setup.execute("DELETE FROM social.brands WHERE id = $1", brand_id)
        if workspace_id:
            await setup.execute(
                "DELETE FROM social.workspace_members WHERE workspace_id = $1", workspace_id
            )
            await setup.execute("DELETE FROM social.workspaces WHERE id = $1", workspace_id)
        if account_id:
            await setup.execute("DELETE FROM social.accounts WHERE id = $1", account_id)
        await setup.close()


def test_no_writer_reads_brand_kit_to_write_it_back():
    """Hiçbir yazıcı `brand_kit`i okuyup geri YAZMAZ (sınıf kapanışı).

    Varyant değil sınıf: `update_brand_kit`i atomik yapmak yetmez —
    `avatar.py` de aynı okundu-değiştir-geri-yaz desenini kullanıyor ve
    kanal envanterini SİLEBİLİR (checkpoint 9 bulgusunda adıyla anıldı).
    Tarama kaynağın kendisini gezer: yarın üçüncü bir yazıcı aynı deseni
    getirirse test kırmızıya döner.
    """
    offenders = []
    for path in (BACKEND_ROOT / "app").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
                continue
            # Docstring'ler (ve başıboş metin ifadeleri) HARİÇ: tarama KOŞAN
            # SQL'e bakar, anlatıya değil. Aksi hâlde "eskiden SELECT edip
            # UPDATE ediyordu" diye yazan bir docstring kendi düzeltmesini
            # ihlal gibi gösterirdi (ölçüldü — bu testin ilk hâli tam olarak
            # buna takıldı).
            prose = {
                id(stmt.value)
                for stmt in ast.walk(node)
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant)
            }
            sql = " ".join(
                inner.value
                for inner in ast.walk(node)
                if isinstance(inner, ast.Constant)
                and isinstance(inner.value, str)
                and id(inner) not in prose
            )
            writes_kit = "UPDATE social.brands" in sql and "brand_kit" in sql
            reads_kit = "SELECT brand_kit" in sql
            if writes_kit and reads_kit:
                offenders.append(f"{path.relative_to(BACKEND_ROOT)}::{node.name}")

    assert not offenders, f"okundu-değiştir-geri-yaz deseni: {offenders}"


# ─── 5. Checkpoint 9 turu 2 — aynı iki sınıfın kalan ayakları ───────────────


def test_malformed_marker_is_rejected_at_write_gate():
    """Bozuk etiket YAZIM kapısında reddedilir (F4 sınıf kapanışı).

    Tur 1'de etiketin KARAKTER temsili kapatıldı; tur 2 aynı eksenin ikinci
    ayağını açtı: ayıraç eksikse (`]` yok, `:` yok) katı kalıp eşleşmiyor,
    kalıp "etiketsiz" sayılıp geçiyordu. Bir regex varyantı daha eklemek
    üçüncü turda üçüncü varyantı davet ederdi.

    Kapanış iki taraflı bir SÖZLEŞMEYLE yapılır: yazım kapısı, etiket
    OKUNAN ama kurallı BİÇİMDE olmayan hiçbir metni içeri almaz; okuma tarafı
    katı kalır. Böylece bozuk etiket bir pakette VAR OLAMAZ.
    """
    from app.services.sector_packages import structural_errors

    def content_with(cta_text: str) -> dict:
        return {
            "kapsam": "kapsam",
            "ton_ve_dil": "ton",
            "gorsel_kodlar": "codes",
            "cta_kaliplari": [cta(cta_text)],
            "kanca_kaliplari": ["kanca"],
            "takvim_temalari": ["tema"],
            "yasaklar_ve_hassasiyetler": ["yasak"],
            "video_kodlar": {"hareket": "a", "sahne": "b"},
            "ozel_gun": {},
        }

    # Önce pozitif kontrol: kurallı etiket taşıyan içerik TEMİZ geçer.
    assert structural_errors(content_with("Yaz [kanal-bağımlı: whatsapp_hatti]")) == []

    malformed = {
        "kapanış ayracı yok": "Yaz [kanal-bağımlı: whatsapp_hatti",
        "iki nokta yok": "Yaz [kanal-bağımlı whatsapp_hatti]",
        "açılış ayracı yok": "Yaz kanal-bağımlı: whatsapp_hatti]",
        "bilinmeyen anahtar": "Yaz [kanal-bağımlı: telegram]",
        "boş anahtar": "Yaz [kanal-bağımlı: ]",
        "tipografik tire + bozuk ayraç": "Yaz [kanal—bağımlı whatsapp_hatti]",
        "alt çizgi ayırıcı": "Yaz [kanal_bağımlı: whatsapp_hatti]",
        "çoklu boşluk ayırıcı": "Yaz [kanal     bağımlı whatsapp_hatti]",
        "çoklu tire": "Yaz [kanal-----bağımlı: whatsapp_hatti]",
        "nokta + alt çizgi": "Yaz [kanal._bağımlı: whatsapp_hatti]",
        "iç içe ayraç": "Yaz [[kanal-bağımlı: whatsapp_hatti]]",
        "serbest metin ayracı": "Yaz [bkz. 3] ve [kanal-bağımlı: whatsapp_hatti]",
    }
    escapes = [name for name, text in malformed.items() if not structural_errors(content_with(text))]

    assert not escapes, f"yazım kapısından geçen bozuk etiket: {escapes}"


def _flag_content(cta_text: str) -> dict:
    return {
        "kapsam": "kapsam",
        "ton_ve_dil": "ton",
        "gorsel_kodlar": "codes",
        "cta_kaliplari": [cta(cta_text)],
        "kanca_kaliplari": ["kanca"],
        "takvim_temalari": ["tema"],
        "yasaklar_ve_hassasiyetler": ["yasak"],
        "video_kodlar": {"hareket": "a", "sahne": "b"},
        "ozel_gun": {},
    }


def test_only_the_channel_flag_may_appear_in_package_content():
    """Paket içeriğinde geçebilecek TEK bayrak kanal bayrağıdır (spec §8.5).

    Kapalı kayıt UYDURULMADI, spec'ten TÜRETİLDİ: §8.4 kümeyi "sekiz bayrak,
    kapalı" diye bağlar; §8.5 bunların YEDİSİNİN sentez sırasında TÜKETİLDİĞİNİ
    (karara etki edip kaybolduğunu) söyler ve yalnız kanal bayrağı için
    "etiketiyle taşınır" der; §3.4 aynı hükmü alan tablosunda tekrarlar
    ("taşınır, silinmez"). Dolayısıyla paket içeriğinin geçerli bayrak listesi
    tek kalemliktir ve bunu yazmak yeni bir karar DEĞİL, mevcut hükmün kod
    karşılığıdır.

    Bu, yanlış-yazım sınıfını da kapatır: sentezde tüketilmesi gereken bir
    bayrak pakette görünüyorsa ya sentez sözleşmesi ihlal edilmiştir ya da
    yazım hatalıdır — ikisi de reddedilmelidir.
    """
    from app.services.sector_packages import structural_errors

    consumed_upstream = ("[eski-kaynak]", "[kopya-şüphesi]", "[yerel-değil]", "[kaynak-bağımlı]")
    escapes = [f for f in consumed_upstream if not structural_errors(_flag_content(f"Yaz {f}"))]

    assert not escapes, f"sentezde tüketilmesi gereken bayrak pakete girdi: {escapes}"

    # Pozitif kontrol: kanal bayrağı geçer.
    assert structural_errors(_flag_content("Yaz [kanal-bağımlı: whatsapp_hatti]")) == []


def test_misspelled_channel_flag_is_rejected():
    """Kanal bayrağının yanlış yazımı REDDEDİLİR (tur 4 bulgusu).

    Kapalı kayıt tek kalemli olduğu için "yakın ama farklı" slug'ı ayırt etmeye
    gerek kalmaz: kanal bayrağı DEĞİLSE zaten pakette olamaz. Sınıf, tahminle
    değil kapsamayla kapanır.
    """
    from app.services.sector_packages import structural_errors

    misspelled = (
        "[kanal-bagimll: whatsapp_hatti]",
        "[kanal-bagimli-whatsapp-hatti]",
        "[whatsapp-gerekli: whatsapp_hatti]",
        "[kanal-baglantili]",
        "[kanal-bagimli]",  # değer YOK — kanal adı taşımayan kanal bayrağı
    )
    escapes = [f for f in misspelled if not structural_errors(_flag_content(f"WhatsApp {f}"))]

    assert not escapes, f"yanlış yazılmış bayrak pakete girdi: {escapes}"


def test_unbracketed_marker_is_a_documented_limit_not_a_closure():
    """Ayraçsız yazılmış işaret YAKALANMAZ — bu bilinen ve YAZILI sınırdır.

    Sözleşme ayraç üzerinedir: bayrak, tanımı gereği köşeli parantezlidir.
    Parantezsiz serbest metinden "bu aslında bir işaretti" sonucunu çıkarmak,
    üç tur boyunca yakınsamayan tam da o tahmin oyunudur (checkpoint 9). Kapanış
    iddiası bu yüzden DAR tutulur: *ayraçlı* her işaret kapalıdır.

    Test, sınırın sessizce kaybolmasını engeller: davranış değişirse burada
    görünür ve iddia yeniden yazılır.
    """
    from app.services.sector_packages import structural_errors

    assert structural_errors(
        _flag_content("Yaz kanal-bağımlı whatsapp_hatti")
    ) == [], "sınır kapandıysa iddia güncellenmeli"


def test_write_gate_rejection_makes_runtime_fallback_consistent():
    """Yazım kapısından geçemeyen içerik çalışma zamanında da okunmaz.

    `structural_errors` iki tarafın ORTAK ölçüsüdür (Task 8 sözleşmesi), yani
    bozuk etiketli bir paket K-15(a) gereği TÜM yoluyla paketsiz yola düşer —
    alan-düzeyi atlama yok. Bu test o bağın hâlâ tek ölçü olduğunu pinler.
    """
    from app.services import sector_packages as sp

    source = inspect.getsource(sp.resolve_package_context)
    assert "structural_errors(content)" in source


async def test_brand_update_surface_does_not_erase_concurrent_kit_state(kit_db):
    """`PATCH /brands/{id}` bayat bir belgeyle kanal envanterini SİLEMEZ (F3).

    Tur 1 sunucu-taraflı okundu-değiştir-geri-yaz desenini kapattı; tur 2
    sınıfın ikinci ayağını gösterdi: `BrandUpdate` tam bir `brand_kit` kabul
    ediyor ve doğrudan atıyordu. İstemci kiti okur, arada başka bir istek
    `channels` ekler, sonra bayat PATCH tüm belgeyi ezip yeni durumu silerdi.

    Sınıfın dürüst tanımı: "bayat bir okumadan hesaplanmış belgeyle
    `brand_kit`i DEĞİŞTİREBİLEN her yol". Üç üyesi vardı; üçü de birleştirmeye
    geçti.
    """
    user, brand_id = await _seed_owner_and_brand(kit_db)

    # Eşzamanlı/atomik yazım: kanal envanteri eklenir.
    await brands_router.update_brand_kit(
        brand_id=brand_id,
        payload=BrandKitUpdate(channels={"whatsapp_hatti": True}),
        user=user,
        db=kit_db,
    )

    # Bayat istemci belgesi: `channels` HİÇ yok (istemci onu görmeden okumuştu).
    await brands_router.update_brand(
        brand_id=brand_id,
        payload=BrandUpdate(brand_kit={"tonality": "friendly"}),
        user=user,
        db=kit_db,
    )

    stored = parse_brand_kit(
        await kit_db.fetchval("SELECT brand_kit FROM social.brands WHERE id = $1", brand_id)
    )
    assert stored["channels"] == {"whatsapp_hatti": True}, "bayat PATCH kanalları SİLDİ"
    assert stored["tonality"] == "friendly"


def test_no_writer_replaces_brand_kit_wholesale():
    """Hiçbir yazıcı `brand_kit`e ÇIPLAK parametre atamaz (sınıf kapanışı).

    Önceki yapısal tarama yalnız okundu-değiştir-geri-yaz desenini görüyordu;
    bayat-belge ataması (`brand_kit = $2`) onun ağından geçiyordu. Sınıfın
    kendisi şudur: **`brand_kit`e yapılan her yazım BİRLEŞTİRME olmalıdır**.
    Tarama bunu SQL metninden ölçer.

    **Kapsam sınırı (dürüstçe):** tarama yalnız METİN SABİTLERİNİ görür; SQL'i
    çalışma zamanında kuran `update_brand` bu ağdan geçer. Onun kanıtı
    davranışsaldır (`test_brand_update_surface_does_not_erase_concurrent_kit_state`)
    ve birleştirme ifadesinin tek evden geldiği ayrıca pinlenir
    (`test_kit_merge_sql_has_a_single_implementation`). Üçü birlikte sınıfı
    kapatır; tek başına bu tarama kapatmaz.
    """
    import re as _re

    assignment = _re.compile(r"brand_kit\s*=\s*\$\d+")
    offenders = []
    for path in (BACKEND_ROOT / "app").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
                continue
            prose = {
                id(stmt.value)
                for stmt in ast.walk(node)
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant)
            }
            for inner in ast.walk(node):
                if not (isinstance(inner, ast.Constant) and isinstance(inner.value, str)):
                    continue
                if id(inner) in prose:
                    continue
                if assignment.search(inner.value):
                    offenders.append(f"{path.relative_to(BACKEND_ROOT)}::{node.name}")

    assert not offenders, f"brand_kit'e çıplak atama (birleştirme değil): {sorted(set(offenders))}"


def test_kit_merge_sql_has_a_single_implementation():
    """Birleştirme SQL'i tek yerde yaşar — üç yazıcı da onu çağırır."""
    from app.core.utils import brand_kit_merge_sql

    assert callable(brand_kit_merge_sql)

    users = []
    for path in (BACKEND_ROOT / "app").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        if "brand_kit_merge_sql" in source and path.name != "utils.py":
            users.append(path.name)

    assert sorted(users) == ["avatar.py", "brands.py"]
