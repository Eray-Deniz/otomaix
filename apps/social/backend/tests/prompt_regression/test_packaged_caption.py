"""Tek-kapı enjeksiyon — caption + fikir önerme yüzeyleri (plan Task 10).

Burada pinlenen sözleşme, paketin ilk kez GERÇEK üretim akışına bağlanmasıdır.
Beş bağlayıcı invariant test edilir:

1. **Yerine-geçme (spec §4.1).** Aktif paket varken kök `SECTOR_GUIDANCE` bloğu
   hiçbir yüzeyde basılmaz — paket onun YERİNE geçer. Fikir önerme ucu da dâhil;
   aksi hâlde öneri kök rehberle, üretim paketle konuşurdu (iki ses ayrışması).
2. **Kullanım talimatı (spec §4.5, K-04).** Talimat bloğun BAŞINDA durur — ilk
   içerik alanından önce. Sonda duran bir talimat, listeyi tamamlama refleksi
   çoktan tetiklendikten sonra gelirdi.
3. **Tier 3 özel gün (spec §11.1).** Eşleşen günde dönem kalıpları mevcut bloğa
   EKLENİR (blok yapısı değişmez); eşleşmezse sessiz düşme + ZORUNLU log.
4. **Kanal filtresi (spec §12.2).** `[kanal-bağımlı: X]` etiketli CTA kalıbı
   yalnız markanın doğrulanmış kanalıyla basılır; etiket metni prompt'a SIZMAZ.
5. **K-119 (spec §11.3).** `anma` satış-dili yasağı kullanıcı isteğini geçersiz
   kılar — kullanıcı kampanya istese bile yasak satırı basılır ve üstünlüğü
   talimatta AÇIKÇA yazar.

Ayrıca K-07 taşıma sözleşmesinin üretici ucu: paketli üretim `generation_stamps`
satırı yazar ve yanıtta YALNIZ opak `generation_id` döner; ham paket çifti
istemciye gitmez. Paketsizde `None`.

Katman-1 kapısı bu dosyanın da ön koşuludur: paketsiz yolun byte-exact kalması
son testle (tam sweep alt kümesi) ayrıca kanıtlanır.
"""

from __future__ import annotations

import json
import logging
import uuid

import pytest

from app.core.caption_generator import generate_captions
from app.core.database import _init_connection
from app.core.templates_data import SECTOR_GUIDANCE, get_template_by_id
from app.routers import ai as ai_router
from app.routers import posts as posts_router
from app.services.sector_packages import (
    USAGE_INSTRUCTION,
    SectorPackageContext,
    normalize_special_day_key,
)

from .capture import assert_matches_fixture, capture_anthropic_calls
from .conftest import (
    FROZEN_SECTOR_SLUG,
    FROZEN_SINGLE_TEMPLATE_ID,
)
from .test_caption_surfaces import _run_caption

CUMHURIYET_KEY = normalize_special_day_key("Cumhuriyet Bayramı")
RAMAZAN_KEY = normalize_special_day_key("Ramazan Bayramı")

# CTA kalıbının kanal etiketi — paket İÇERİĞİNDE taşınır, prompt'a basılmaz
# (spec §3.4 "taşınır, silinmez" içeriğin kuralıdır; basım biçimi bu katmanın).
TAGGED_CTA = "WhatsApp hattımızdan fiyat sorun [kanal-bağımlı: whatsapp_hatti]"
PLAIN_CTA = "Vitrindeki modeli mağazada deneyin"


def _package_content(**overrides) -> dict:
    """Yapısal doğrulayıcıdan GEÇEN sabit paket içeriği."""
    content = {
        "kapsam": "Kuyumculuk: altın, gümüş ve pırlanta takı perakendesi.",
        "ton_ve_dil": "Güven veren, sade; fiyat vaadi yerine ayar ve sertifika dili.",
        "cta_kaliplari": [
            {"kalip": PLAIN_CTA, "tur": "ziyaret", "gerekce": "Takı kararı denemeye bağlı."},
            {"kalip": TAGGED_CTA, "tur": "mesaj", "gerekce": "Fiyat sorusu hatta düşer."},
        ],
        "kanca_kaliplari": ["Ayar farkını gözle ayırt edebilir misiniz?"],
        "gorsel_kodlar": "Warm directional light on polished metal, shallow depth of field.",
        "video_kodlar": {
            "hareket": [
                "Slow orbit around the display case.",
                "Gentle push-in on the ring tray.",
            ],
            "sahne": [
                "Boutique interior, warm ambient light.",
                "Velvet display surface, directional key light.",
            ],
        },
        "takvim_temalari": ["Söz-nişan yoğunluğu ilkbaharda artar."],
        "yasaklar_ve_hassasiyetler": [
            "Yatırım getirisi vaadi yasak (SPK mevzuatı, yürürlük 2013-06-30)."
        ],
        "ozel_gun": {
            CUMHURIYET_KEY: {
                "tur": "kutlama",
                "mesaj_ekseni": "Ortak sevinç ve emek",
                "kanca": "Bayram vitrinimiz hazır",
                "cta": "Bayramı ailenizle kutlayın",
                "gorsel_vurgu": "Red and white accents, no flag graphics",
            }
        },
    }
    content.update(overrides)
    return content


def _context(content: dict | None = None) -> SectorPackageContext:
    return SectorPackageContext(
        package_id=uuid.UUID("11111111-2222-3333-4444-555555555555"),
        version=3,
        content=content if content is not None else _package_content(),
        sub_sector_slug="kuyumculuk",
    )


async def _packaged_caption(
    frozen,
    monkeypatch,
    *,
    context: SectorPackageContext | None = None,
    special_day: bool = False,
    special_day_name: str | None = None,
    user_prompt: str | None = None,
    brand_kit: dict | None = None,
):
    """Paketli caption prompt'unu üretimin KENDİ yolundan yakalar."""
    calls = capture_anthropic_calls(monkeypatch)

    day = None
    if special_day or special_day_name:
        day = special_day_name or frozen["special_day"]["name"]

    await generate_captions(
        brand=frozen["brand"],
        brand_kit=brand_kit if brand_kit is not None else frozen["brand_kit"],
        template=get_template_by_id(FROZEN_SINGLE_TEMPLATE_ID),
        template_fields=frozen["template_fields"],
        user_prompt=user_prompt if user_prompt is not None else frozen["user_prompt"],
        rag_context=None,
        platforms=frozen["platforms"],
        product=frozen["product"],
        content_type="image",
        special_day_name=day,
        special_day_category=frozen["special_day"]["category"] if day else None,
        package_context=context if context is not None else _context(),
    )

    assert len(calls) == 1, f"tam olarak bir çağrı bekleniyordu, {len(calls)} oldu"
    return calls[0].rendered


# ─── 1. Yerine-geçme (spec §4.1) ────────────────────────────────────────────


async def test_packaged_caption_replaces_sector_guidance(
    frozen_brand_fixtures, monkeypatch
):
    """Paket bloğu basılır, kök `SECTOR_GUIDANCE` bloğu BASILMAZ."""
    # Ön koşul: bu markanın kök rehberi bugün GERÇEKTEN basılıyor — yoksa test
    # boşluğa karşı yeşil kalırdı.
    assert FROZEN_SECTOR_SLUG in SECTOR_GUIDANCE

    rendered = await _packaged_caption(frozen_brand_fixtures, monkeypatch)

    assert "SEKTÖR PAKETİ" in rendered, "paket bloğu hiç basılmadı"
    assert "SEKTÖR REHBERİ" not in rendered, "yan-yana basım yasağı ihlal edildi"
    assert SECTOR_GUIDANCE[FROZEN_SECTOR_SLUG] not in rendered
    # Paketin kendi içeriği gerçekten aktı:
    assert "Kuyumculuk: altın" in rendered


async def test_packaged_idea_prompt_replaces_guidance(db, monkeypatch):
    """Fikir önerme ucu da paket yoluna girer — iki ses ayrışması olmaz."""
    await _init_connection(db)
    calls = capture_anthropic_calls(monkeypatch, response_text="1. birinci\n2. ikinci")
    user, brand_id = await _seed_owned_brand(db, packaged=True)

    payload = ai_router.SuggestIdeasRequest(
        brand_id=brand_id,
        content_type="image",
        content_category="product",
        prompt="Yeni sürüm duyurusu",
        platforms=["instagram", "linkedin"],
        count=3,
        template_id=FROZEN_SINGLE_TEMPLATE_ID,
    )
    await ai_router.suggest_ideas(payload=payload, user=user, db=db)

    assert len(calls) == 1, "fikir yüzeyi sessizce fallback'e düştü"
    rendered = calls[0].rendered
    assert "SEKTÖR PAKETİ" in rendered
    assert "SEKTÖR REHBERİ" not in rendered
    assert SECTOR_GUIDANCE[FROZEN_SECTOR_SLUG] not in rendered


# ─── 2. Kullanım talimatı (spec §4.5 / K-04) ────────────────────────────────


async def test_usage_instruction_prefixes_package_block(
    frozen_brand_fixtures, monkeypatch
):
    """Talimat blok başında — ilk içerik alanından ÖNCE."""
    rendered = await _packaged_caption(frozen_brand_fixtures, monkeypatch)

    assert USAGE_INSTRUCTION in rendered, "K-04 kullanım talimatı basılmadı"
    header_at = rendered.index("SEKTÖR PAKETİ")
    instruction_at = rendered.index(USAGE_INSTRUCTION)
    first_content_at = rendered.index("Kuyumculuk: altın")
    assert header_at < instruction_at < first_content_at, (
        "talimat blok başında değil — listeyi tamamlama refleksi çoktan tetiklenirdi"
    )


# ─── 3. Tier 3 özel gün (spec §11.1) ────────────────────────────────────────


async def test_special_day_match_injects_period_block(
    frozen_brand_fixtures, monkeypatch
):
    """Eşleşen günde dönem kalıpları MEVCUT bloğa eklenir."""
    rendered = await _packaged_caption(
        frozen_brand_fixtures, monkeypatch, special_day=True
    )

    assert "Ortak sevinç ve emek" in rendered
    assert "Bayram vitrinimiz hazır" in rendered
    # Blok YAPISI değişmez: dönem kalıpları özel gün bloğunun İÇİNDE durur.
    block_start = rendered.index("=== ÖZEL GÜN BAĞLAMI")
    block_end = rendered.index("=== ÖZEL GÜN BAĞLAMI SONU ===")
    assert block_start < rendered.index("Ortak sevinç ve emek") < block_end
    # Görsel vurgu caption yüzeyine GİRMEZ (spec §4.3 — görsel yüzeyi Task 11).
    assert "Red and white accents" not in rendered


async def test_special_day_mismatch_silent_fallthrough_with_log(
    frozen_brand_fixtures, monkeypatch, caplog
):
    """Karşılığı olmayan günde sessiz düşme + ZORUNLU log."""
    assert RAMAZAN_KEY not in _package_content()["ozel_gun"]

    with caplog.at_level(logging.WARNING):
        rendered = await _packaged_caption(
            frozen_brand_fixtures,
            monkeypatch,
            special_day_name="Ramazan Bayramı",
        )

    # Sessiz düşme: mevcut özel gün bloğu basılır, dönem kalıpları basılmaz.
    assert "Ramazan Bayramı" in rendered
    assert "Ortak sevinç ve emek" not in rendered
    assert "SEKTÖR PAKETİ" in rendered, "paket bloğu düşmemeli — yalnız dönem eşleşmedi"
    # Zorunlu log: sessiz düşme SESSİZ olamaz.
    assert any(
        RAMAZAN_KEY in record.getMessage() for record in caplog.records
    ), "özel gün eşleşmemesi log üretmedi"


# ─── 4. Kanal filtresi (spec §12.2) ─────────────────────────────────────────


async def test_packaged_caption_cta_respects_channel_filter(
    frozen_brand_fixtures, monkeypatch
):
    """Etiketli CTA yalnız doğrulanmış kanalla basılır; etiket metni sızmaz."""
    kit = dict(frozen_brand_fixtures["brand_kit"])

    kit_without = {**kit, "channels": {"whatsapp_hatti": False}}
    rendered_without = await _packaged_caption(
        frozen_brand_fixtures, monkeypatch, brand_kit=kit_without
    )
    assert PLAIN_CTA in rendered_without
    assert "WhatsApp hattımızdan" not in rendered_without, (
        "doğrulanmamış kanalın CTA'sı prompt'a sızdı"
    )

    kit_with = {**kit, "channels": {"whatsapp_hatti": True}}
    rendered_with = await _packaged_caption(
        frozen_brand_fixtures, monkeypatch, brand_kit=kit_with
    )
    assert "WhatsApp hattımızdan" in rendered_with
    # Etiket, üretimin gördüğü metne SIZMAZ — o bir işaret, içerik değil.
    assert "kanal-bağımlı" not in rendered_with
    assert "whatsapp_hatti" not in rendered_with

    # Envantersiz marka muhafazakâr davranır (spec §12.2).
    rendered_missing = await _packaged_caption(
        frozen_brand_fixtures, monkeypatch, brand_kit=kit
    )
    assert "WhatsApp hattımızdan" not in rendered_missing


async def test_special_day_cta_respects_channel_filter(
    frozen_brand_fixtures, monkeypatch
):
    """Özel günün CTA'sı da bir CTA yüzeyidir — aynı filtreden geçer.

    Yazım kapısı kanal bayrağını `cta_kaliplari` VE `ozel_gun[*].cta`
    yüzeylerinde meşru sayar (`_channel_flag_scopes`). Basım yalnız ilkini
    elerse, doğrulanmamış kanalın CTA'sı özel gün dalından SIZAR — okuma
    tarafıyla hizasız bir kapsam, kapının kendisini deler.
    """
    content = _package_content(
        ozel_gun={
            CUMHURIYET_KEY: {
                "tur": "kutlama",
                "mesaj_ekseni": "Ortak sevinç ve emek",
                "kanca": "Bayram vitrinimiz hazır",
                "cta": "Bayram saatlerini WhatsApp'tan sorun "
                "[kanal-bağımlı: whatsapp_hatti]",
                "gorsel_vurgu": "Red and white accents",
            }
        }
    )
    kit = dict(frozen_brand_fixtures["brand_kit"])

    without = await _packaged_caption(
        frozen_brand_fixtures,
        monkeypatch,
        context=_context(content),
        special_day=True,
        brand_kit={**kit, "channels": {"whatsapp_hatti": False}},
    )
    assert "Bayram vitrinimiz hazır" in without, "dönem bloğu hiç basılmamış"
    assert "WhatsApp'tan sorun" not in without, (
        "doğrulanmamış kanalın özel gün CTA'sı sızdı"
    )

    with_channel = await _packaged_caption(
        frozen_brand_fixtures,
        monkeypatch,
        context=_context(content),
        special_day=True,
        brand_kit={**kit, "channels": {"whatsapp_hatti": True}},
    )
    assert "WhatsApp'tan sorun" in with_channel
    assert "kanal-bağımlı" not in with_channel
    assert "whatsapp_hatti" not in with_channel


# ─── 5. K-119 — `anma` yasağı kullanıcı isteğini geçersiz kılar ─────────────


async def test_anma_sales_ban_overrides_user_request(
    frozen_brand_fixtures, monkeypatch
):
    """Kullanıcı kampanya istese bile satış-dili yasağı basılır ve ÜSTTEDİR."""
    content = _package_content(
        ozel_gun={
            CUMHURIYET_KEY: {
                "tur": "anma",
                "mesaj_ekseni": "Saygı ve hatıra",
                "kanca": "Bugün susmayı biliyoruz",
                "cta": "Saygıyla anıyoruz",
                "gorsel_vurgu": "Muted tones, no product hero shot",
            }
        }
    )
    sales_request = "Kampanya duyurusu yap, %50 indirim ver, satışa yönlendir."

    rendered = await _packaged_caption(
        frozen_brand_fixtures,
        monkeypatch,
        context=_context(content),
        special_day=True,
        user_prompt=sales_request,
    )

    # Kullanıcı isteği hâlâ basılıyor — geçersiz kılma talimat düzeyindedir.
    assert sales_request in rendered
    # Yasak satırı VAR ve kullanıcı isteğinin üstünde olduğu AÇIKÇA yazıyor.
    #
    # Karşılaştırma KÜÇÜLTMEDEN yapılır: `"İ".lower()` birleşen nokta üretir
    # (`i` + U+0307) ve "kullanıcı isteği" araması sessizce ıskalardı — bu
    # kod tabanının başka yerlerinde de ölçülmüş bir tuzak.
    assert "satış çağrısı kullanma" in rendered
    ban_at = rendered.index("satış çağrısı kullanma")
    override_at = rendered.index("KULLANICI İSTEĞİNİN ÜSTÜNDEDİR")
    assert ban_at < override_at, "K-119 üstünlüğü yasak satırından önce geliyor"
    # Anma'nın ek içerik kısıtı da basılır (spec §11.3).
    assert "yalnız saygı çerçevesinde" in rendered


def test_non_ascii_bracket_tag_is_filtered_but_not_stripped():
    """Belgeli sınır — ölçülmüş, sessizce kaybolamaz.

    Tam genişlikli ayraçla yazılmış bir etiketi filtre TANIR (kanonikleştirme
    NFKC'den geçiyor), ama basım onu metinden ÇIKARAMAZ: çıkarma ham metinde
    ayraç parçası arar ve katlama 1:1 olmadığı için kanonik konum ham metne
    geri eşlenemez.

    Sonuç KOZMETİKtir, emniyet açığı değildir: etiket tanındığı için filtre
    kararını verir; artık kalan etiket yalnız DOĞRULANMIŞ bir kanalın
    kalıbında bulunabilir. Bu test iki yarıyı birlikte pinler — tanımanın
    daralması da, basımın sessizce genişlemesi de kırmızı üretir.
    """
    from app.services.sector_packages import _channel_tags, _strip_channel_tags

    tagged = "Fiyat için yazın ［kanal-bağımlı: whatsapp_hatti］"

    # Tanıma: filtre bu yazımı görür (emniyetli yarı).
    assert _channel_tags(tagged) == frozenset({"whatsapp_hatti"})
    # Basım: çıkaramaz (belgeli sınır).
    assert _strip_channel_tags(tagged) == tagged
    # ASCII ayraçlı kardeş yazım İKİ tarafta da kapalıdır — sınır ayraçtadır,
    # kanal anahtarında değil.
    ascii_tagged = "Fiyat için yazın [kanal-bağımlı: whatsapp_hatti]"
    assert _channel_tags(ascii_tagged) == frozenset({"whatsapp_hatti"})
    assert _strip_channel_tags(ascii_tagged) == "Fiyat için yazın"


# ─── 6. K-07 damga taşıma — üretici ucu ─────────────────────────────────────


async def _seed_owned_brand(db, *, packaged: bool):
    """Sahiplik zinciri + isteğe bağlı aktif paket ataması."""
    account_id = await db.fetchval(
        "INSERT INTO social.accounts (email, name, plan_id) "
        "VALUES ($1, $2, 'pro') RETURNING id",
        f"t10-{uuid.uuid4().hex[:10]}@example.test",
        "T10 Sahip",
    )
    workspace_id = await db.fetchval(
        "INSERT INTO social.workspaces (account_id, name) VALUES ($1, $2) RETURNING id",
        account_id,
        "T10 Workspace",
    )
    await db.execute(
        "INSERT INTO social.workspace_members (workspace_id, account_id) VALUES ($1, $2)",
        workspace_id,
        account_id,
    )

    root_id = await db.fetchval(
        "SELECT id FROM social.sectors WHERE slug = $1", FROZEN_SECTOR_SLUG
    )
    sub_id = None
    if packaged:
        sub_id = await db.fetchval(
            "INSERT INTO social.sectors (slug, display_name, parent_sector_id) "
            "VALUES ($1, $2, $3) RETURNING id",
            f"kuyumculuk-{uuid.uuid4().hex[:8]}",
            "Kuyumculuk",
            root_id,
        )
        await db.execute(
            "INSERT INTO social.sector_packages "
            "(sector_id, version, status, schema_version, content) "
            "VALUES ($1, 1, 'active', 1, $2)",
            sub_id,
            _package_content(),
        )

    brand_id = await db.fetchval(
        """
        INSERT INTO social.brands (workspace_id, name, sector_id, sub_sector_id, brand_kit)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
        """,
        workspace_id,
        "T10 Marka",
        root_id,
        sub_id,
        {"tonality": "professional", "channels": {"whatsapp_hatti": True}},
    )
    return {"sub": str(account_id)}, brand_id


async def _call_generate_caption(db, user, brand_id):
    payload = posts_router.GenerateCaptionRequest(
        brand_id=brand_id,
        platforms=["instagram"],
        content_type="image",
        user_prompt="Yeni koleksiyon duyurusu",
        template_id=FROZEN_SINGLE_TEMPLATE_ID,
    )
    response = await posts_router.generate_caption(payload=payload, user=user, db=db)
    return response.data


async def test_packaged_caption_response_carries_generation_id(db, monkeypatch):
    """Paketli üretim damga satırı yazar; yanıtta YALNIZ opak kimlik döner."""
    await _init_connection(db)
    capture_anthropic_calls(monkeypatch)
    user, brand_id = await _seed_owned_brand(db, packaged=True)

    data = await _call_generate_caption(db, user, brand_id)

    generation_id = data.get("generation_id")
    assert generation_id, "paketli üretim opak kimlik döndürmedi"
    # Ham paket çifti istemciye GİTMEZ.
    assert "package_id" not in data
    assert "package_version" not in data
    # Anahtar adı değil, DEĞER düzeyinde de kapalı: paketin kimliği yanıtın
    # hiçbir yerinde geçmez (anahtar-kara-listesi tek başına sınıfı kapatmaz).
    package_id = await db.fetchval(
        "SELECT package_id FROM social.generation_stamps WHERE id = $1",
        uuid.UUID(str(data["generation_id"])),
    )
    assert str(package_id) not in json.dumps(data, default=str)

    row = await db.fetchrow(
        "SELECT brand_id, package_id, package_version, consumed_at "
        "FROM social.generation_stamps WHERE id = $1",
        uuid.UUID(str(generation_id)),
    )
    assert row is not None, "damga makbuzu yazılmadı"
    assert row["brand_id"] == brand_id
    assert row["package_version"] == 1
    assert row["consumed_at"] is None, "üretici uç tüketim işareti koymamalı"


async def test_unpackaged_caption_response_generation_id_null(db, monkeypatch):
    """Paketsiz üretimde kimlik `None` ve HİÇ makbuz yazılmaz."""
    await _init_connection(db)
    capture_anthropic_calls(monkeypatch)
    user, brand_id = await _seed_owned_brand(db, packaged=False)

    before = await db.fetchval("SELECT count(*) FROM social.generation_stamps")
    data = await _call_generate_caption(db, user, brand_id)
    after = await db.fetchval("SELECT count(*) FROM social.generation_stamps")

    assert data.get("generation_id") is None
    assert after == before, "paketsiz üretim makbuz yazdı"


# ─── 7. Katman-1 — paketsiz yol bayt değişmez ───────────────────────────────


async def test_unpackaged_fixtures_still_byte_exact(frozen_brand_fixtures, monkeypatch):
    """Tek kapının `None` dalı caption yüzeyinde iz BIRAKMAZ (tam sweep alt kümesi)."""
    call = await _run_caption(
        frozen_brand_fixtures, monkeypatch, template_id=FROZEN_SINGLE_TEMPLATE_ID
    )
    assert "SEKTÖR PAKETİ" not in call.rendered
    assert_matches_fixture("caption__single__no_special_day", call.rendered)


# ─── 8. Checkpoint 10 bulgularının regresyon kapıları ───────────────────────


def test_generate_caption_route_targets_the_handler():
    """`/posts/generate-caption` GERÇEK işleyiciye bağlı olmalı (F1).

    Dekoratör ile işleyici arasına bir yardımcı fonksiyon sokulursa FastAPI
    yolu O yardımcıya bağlar: uç, kimlik doğrulamasız ve gövdesiz bir imzayla
    açılır, asıl caption akışı HTTP üzerinden ERİŞİLEMEZ olur. Fonksiyonu
    doğrudan çağıran testler bunu göremez — kapı yolun KENDİSİNE bakmalı.
    """
    from app.main import app

    matches = [r for r in app.routes if getattr(r, "path", "") == "/posts/generate-caption"]
    assert matches, "generate-caption yolu hiç kayıtlı değil"
    for route in matches:
        assert route.endpoint.__name__ == "generate_caption", (
            f"yol yanlış işleyiciye bağlı: {route.endpoint.__name__}"
        )


async def test_suggest_ideas_rejects_foreign_brand(db, frozen_brand_fixtures, monkeypatch):
    """Fikir ucu SAHİPLİK doğrular — kimlik doğrulama yetki değildir (F2).

    Uç paket-farkındalığı kazandığı an, başkasının markasının paket içeriği
    (spec §3.7'ye göre İÇSEL) yabancı bir kiracıya akmaya başlar. Sahiplik
    kapısı bu yüzden paket enjeksiyonundan ÖNCE koşmalıdır.
    """
    from fastapi import HTTPException

    await _init_connection(db)
    calls = capture_anthropic_calls(monkeypatch, response_text="1. bir")
    _, brand_id = await _seed_owned_brand(db, packaged=True)
    stranger = {"sub": str(uuid.uuid4())}

    payload = ai_router.SuggestIdeasRequest(
        brand_id=brand_id,
        content_type="image",
        content_category="product",
        prompt="deneme",
        platforms=["instagram"],
        count=3,
    )
    with pytest.raises(HTTPException) as excinfo:
        await ai_router.suggest_ideas(payload=payload, user=stranger, db=db)

    # Varlık sızmasın diye 404 (403 değil) — projenin yerleşik sözleşmesi.
    assert excinfo.value.status_code == 404
    assert not calls, "yetkisiz istek modele hiç ulaşmamalıydı"


async def test_fallback_generation_is_not_stamped(db, monkeypatch):
    """Paketsiz FALLBACK çıktısı paket damgası ALMAZ (F3).

    Çözümleyicinin paket bulmuş olması, dönen içeriğin o paketle üretildiğini
    KANITLAMAZ: anahtar yoksa ya da model çağrısı patlarsa `generate_captions`
    kullanıcı isteğini yankılayan bir yedeğe düşer. O yedeği damgalamak,
    üretilmemiş bir soyağacını doğrulanmış gibi göstermek olurdu.
    """
    await _init_connection(db)
    capture_anthropic_calls(monkeypatch)
    from app.core.config import settings

    # Anahtar YOK → üretim yedek dala düşer (paket bağlamı çözülmüş olsa bile).
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "", raising=False)
    user, brand_id = await _seed_owned_brand(db, packaged=True)

    before = await db.fetchval("SELECT count(*) FROM social.generation_stamps")
    data = await _call_generate_caption(db, user, brand_id)
    after = await db.fetchval("SELECT count(*) FROM social.generation_stamps")

    assert data.get("generation_id") is None, "yedek çıktı paket damgası aldı"
    assert after == before, "yedek çıktı için makbuz yazıldı"


@pytest.mark.parametrize("malformed", ["   ", "...", "!!"])
async def test_malformed_special_day_falls_through_silently(
    frozen_brand_fixtures, monkeypatch, caplog, malformed
):
    """Çözümlenemeyen gün adı SESSİZ DÜŞER — istisna KAÇMAZ (F4).

    `normalize_special_day_key` yazım tarafı için fail-closed'dır ve
    çözümlenemeyen adda `ValueError` fırlatır. Okuma tarafında bu, genel
    kullanıcı girdisiyle tetiklenen işlenmemiş bir sunucu hatasına dönüşür ve
    spec §11.1'in zorunlu sessiz-düşme sözleşmesini çiğner. Yazıcı katı kalır;
    okuma sınırında hata mismatch'e ÇEVRİLİR.
    """
    with caplog.at_level(logging.WARNING):
        rendered = await _packaged_caption(
            frozen_brand_fixtures, monkeypatch, special_day_name=malformed
        )

    assert "SEKTÖR PAKETİ" in rendered, "paket yolu malformed gün yüzünden düştü"
    assert "Ortak sevinç ve emek" not in rendered
    assert any(
        "özel gün" in record.getMessage() for record in caplog.records
    ), "çözümlenemeyen gün adı log üretmedi"
