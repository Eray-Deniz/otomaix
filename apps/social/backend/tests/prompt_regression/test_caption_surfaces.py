"""Katman-1: caption ve fikir yüzeylerinin bayt-bayt dondurulmuş prompt'ları.

Bu testler bugünkü davranışı PİNLER. Sektör paketi enjeksiyonu geldiğinde
(Task 8+), paketsiz bir marka için bu dosyaların TEK BAYT değişmemesi gerekir —
spec §15'in K6 kriteri. Bir fixture kırmızıya dönerse bu bir alarmdır, güncelleme
daveti değil.
"""

from __future__ import annotations

import json
import uuid

import pytest

from app.core.caption_generator import generate_captions
from app.core.templates_data import get_template_by_id
from app.routers import ai as ai_router

from .capture import assert_matches_fixture, capture_anthropic_calls
from .conftest import FROZEN_CAROUSEL_TEMPLATE_ID, FROZEN_SINGLE_TEMPLATE_ID


async def _run_caption(frozen, monkeypatch, *, template_id, special_day=False):
    calls = capture_anthropic_calls(monkeypatch)

    await generate_captions(
        brand=frozen["brand"],
        brand_kit=frozen["brand_kit"],
        template=get_template_by_id(template_id),
        template_fields=frozen["template_fields"],
        user_prompt=frozen["user_prompt"],
        rag_context=None,
        platforms=frozen["platforms"],
        product=frozen["product"],
        content_type="image",
        special_day_name=frozen["special_day"]["name"] if special_day else None,
        special_day_category=frozen["special_day"]["category"] if special_day else None,
    )

    # Üretim yolu sessizce fallback'e düşmüş olabilir — o hâlde prompt hiç
    # üretilmez ve karşılaştırma boşuna yeşil kalırdı.
    assert len(calls) == 1, f"tam olarak bir çağrı bekleniyordu, {len(calls)} oldu"
    return calls[0]


async def test_capture_intercepts_and_renders_deterministically(
    frozen_brand_fixtures, monkeypatch
):
    """Aynı girdi iki koşumda AYNI baytları üretir — fixture'ın ön koşulu."""
    first = await _run_caption(
        frozen_brand_fixtures, monkeypatch, template_id=FROZEN_SINGLE_TEMPLATE_ID
    )
    second = await _run_caption(
        frozen_brand_fixtures, monkeypatch, template_id=FROZEN_SINGLE_TEMPLATE_ID
    )

    assert first.rendered.encode() == second.rendered.encode()
    # Yakalama gerçekten üretimin yolundan geçti: sistem bloğu ve marka bağlamı
    # dolu, çağrı üretimin kendi modelini taşıyor.
    assert "=== model: " in first.rendered
    assert frozen_brand_fixtures["brand"]["name"] in first.rendered


async def test_caption_single_no_special_day_matches_fixture(
    frozen_brand_fixtures, monkeypatch
):
    """Tekli caption, özel gün YOK."""
    call = await _run_caption(
        frozen_brand_fixtures, monkeypatch, template_id=FROZEN_SINGLE_TEMPLATE_ID
    )
    assert "ÖZEL GÜN" not in call.rendered.upper()
    assert_matches_fixture("caption__single__no_special_day", call.rendered)


async def test_caption_single_special_day_matches_fixture(
    frozen_brand_fixtures, monkeypatch
):
    """Tekli caption, özel gün VAR — Tier 3'e özel gün bloğu girer."""
    call = await _run_caption(
        frozen_brand_fixtures,
        monkeypatch,
        template_id=FROZEN_SINGLE_TEMPLATE_ID,
        special_day=True,
    )
    assert frozen_brand_fixtures["special_day"]["name"] in call.rendered
    assert_matches_fixture("caption__single__special_day", call.rendered)


async def test_caption_carousel_matches_fixture(frozen_brand_fixtures, monkeypatch):
    """Carousel dalı — K-15b: çıktı biçimi tekli daldan FARKLI olmalı."""
    carousel = await _run_caption(
        frozen_brand_fixtures, monkeypatch, template_id=FROZEN_CAROUSEL_TEMPLATE_ID
    )
    single = await _run_caption(
        frozen_brand_fixtures, monkeypatch, template_id=FROZEN_SINGLE_TEMPLATE_ID
    )

    assert carousel.rendered != single.rendered, "carousel dalı ayrışmadı"
    assert_matches_fixture("caption__carousel", carousel.rendered)


async def test_ideas_surface_matches_fixture(db, frozen_brand_fixtures, monkeypatch):
    """Fikir önerme yüzeyi — Tier 2 sektör rehberi bloğu dâhil.

    `suggest_ideas` HER istisnayı yutup sabit fikirlere düşer; o yüzden çağrının
    gerçekten yapıldığı ayrıca doğrulanır, yoksa test fallback üstünde yeşil
    kalırdı.
    """
    calls = capture_anthropic_calls(monkeypatch, response_text="1. birinci\n2. ikinci")

    sector_id = await db.fetchval(
        "SELECT id FROM social.sectors WHERE slug = $1",
        "teknoloji",
    )
    assert sector_id is not None, "sabit sektör slug'ı kök seed'de yok"

    brand_id = await db.fetchval(
        """
        INSERT INTO social.brands (name, sector, description, brand_kit, sector_id)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING id
        """,
        frozen_brand_fixtures["brand"]["name"],
        frozen_brand_fixtures["brand"]["sector"],
        frozen_brand_fixtures["brand"]["description"],
        json.dumps(frozen_brand_fixtures["brand_kit"], ensure_ascii=False),
        sector_id,
    )

    payload = ai_router.SuggestIdeasRequest(
        brand_id=brand_id,
        content_type="image",
        content_category="product",
        prompt=frozen_brand_fixtures["user_prompt"],
        platforms=frozen_brand_fixtures["platforms"],
        count=3,
        template_id=FROZEN_SINGLE_TEMPLATE_ID,
    )

    await ai_router.suggest_ideas(payload=payload, user={"id": str(uuid.uuid4())}, db=db)

    assert len(calls) == 1, "fikir yüzeyi sessizce fallback'e düştü"
    rendered = calls[0].rendered
    # Sektör rehberi bloğu bugün basılıyor — "yerine geçme" ancak bununla ölçülür.
    assert "SEKTÖR REHBERİ" in rendered
    # Marka kimliği fixture'a sızmasın diye uuid maskelenir.
    assert_matches_fixture("ideas__default", rendered.replace(str(brand_id), "<brand-id>"))
