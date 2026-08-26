"""Katman-1: kısa video durağan kare + script prompt'ları (plan Task 7).

Task 6'daki caption/fikir yüzeylerinin devamı. Aynı kural: prompt'u üreten kod
ÜRETİMİN kendisidir, burada kesilen tek şey ağ çağrısıdır. Bir fixture kırmızıya
dönerse bu bir ALARM'dır.

Her iki yüzey de HER istisnayı yutup metin fallback'ine düşüyor
(`_build_still_prompt` try/except, `generate_script` try/except) — o yüzden her
testte "çağrı gerçekten yapıldı mı" AYRICA doğrulanır; yoksa test fallback
üstünde sessizce yeşil kalırdı.
"""

from __future__ import annotations

from app.core.templates_data import SECTOR_GUIDANCE
from app.services.short_video import _build_still_prompt, generate_script

from .capture import assert_matches_fixture, capture_anthropic_calls


async def _run_still(frozen, monkeypatch, **overrides):
    calls = capture_anthropic_calls(monkeypatch, response_text="a frozen scene")

    kwargs = {
        "topic": frozen["topic"],
        "brand_name": frozen["brand_name"],
        "brand_description": frozen["brand_description"],
        "sector": frozen["sector"],
        "color_str": frozen["color_str"],
        "user_brief": frozen["user_brief"],
        "product_info": "",
        "product_doc_context": "",
        "image_edit_mode": False,
    }
    kwargs.update(overrides)

    result = await _build_still_prompt(**kwargs)

    assert len(calls) == 1, (
        f"tam olarak bir çağrı bekleniyordu, {len(calls)} oldu — "
        "yüzey sessizce metin fallback'ine düşmüş olabilir"
    )
    assert result == "a frozen scene", "üretim yolu yakalanan yanıtı kullanmadı"
    return calls[0]


async def test_still_prompt_text_to_image_mode_matches_fixture(
    frozen_short_video_fixtures, monkeypatch
):
    """Metinden-görsele, ürünsüz — ürün odak bloğu BASILMAZ."""
    call = await _run_still(frozen_short_video_fixtures, monkeypatch)
    assert "PRODUCT FOCUS" not in call.rendered
    assert_matches_fixture("short_video__still__t2i__no_product", call.rendered)


async def test_still_prompt_text_to_image_with_product_matches_fixture(
    frozen_short_video_fixtures, monkeypatch
):
    """Metinden-görsele, ürünlü — ürün odak bloğu BASILIR (dal ayrışması)."""
    call = await _run_still(
        frozen_short_video_fixtures,
        monkeypatch,
        product_info=frozen_short_video_fixtures["product_info"],
        product_doc_context=frozen_short_video_fixtures["product_doc_context"],
    )
    assert "PRODUCT FOCUS" in call.rendered
    assert_matches_fixture("short_video__still__t2i__with_product", call.rendered)


async def test_still_prompt_product_edit_mode_matches_fixture(
    frozen_short_video_fixtures, monkeypatch
):
    """Ürün referanslı edit modu — ürün TARİF EDİLMEZ, sahne yazılır."""
    call = await _run_still(
        frozen_short_video_fixtures,
        monkeypatch,
        image_edit_mode=True,
        product_info=frozen_short_video_fixtures["product_info"],
        product_doc_context=frozen_short_video_fixtures["product_doc_context"],
    )
    assert "do NOT describe the product itself" in call.rendered
    assert_matches_fixture("short_video__still__edit__with_product", call.rendered)


async def test_still_prompt_edit_mode_without_product_matches_fixture(
    frozen_short_video_fixtures, monkeypatch
):
    """Edit modu ama ürün bilgisi YOK — `is_product_video` yine de doğru.

    Matris hücresi bilinçli pinlenir: edit modunda ürün odak bloğu ürün
    bilgisinden BAĞIMSIZ basılır.
    """
    call = await _run_still(
        frozen_short_video_fixtures, monkeypatch, image_edit_mode=True
    )
    assert "PRODUCT FOCUS" in call.rendered
    assert "Product context" not in call.rendered
    assert_matches_fixture("short_video__still__edit__no_product", call.rendered)


async def test_still_prompt_modes_diverge(frozen_short_video_fixtures, monkeypatch):
    """İki mod aynı prompt'u üretmiyor — fixture'ların ayrı olması anlamlı."""
    t2i = await _run_still(frozen_short_video_fixtures, monkeypatch)
    edit = await _run_still(
        frozen_short_video_fixtures, monkeypatch, image_edit_mode=True
    )
    assert t2i.rendered != edit.rendered


async def test_script_request_matches_fixture(
    frozen_short_video_fixtures, monkeypatch
):
    """Script istemi — sektör rehberi bloğu DOLU varyantı.

    Bugün hiçbir üretim çağrısı bu parametreyi dolu geçmiyor (ölçüldü:
    `/ai/generate-script` hiç geçmiyor, legacy uç display-name ile boş
    üretiyor — bkz. `test_legacy_short_video.py`). Blok yine de dondurulur:
    sektör paketi enjeksiyonu (Task 10+) tam BU bloğun yerine geçecek.
    """
    frozen = frozen_short_video_fixtures
    guidance = SECTOR_GUIDANCE["teknoloji"]
    assert guidance, "sabit slug'ın rehberi boş — fixture anlamsız olurdu"

    calls = capture_anthropic_calls(monkeypatch, response_text="Donuk bir senaryo.")
    result = await generate_script(
        frozen["script_prompt"],
        frozen["brand_kit"],
        frozen["brand_name"],
        brand_description=frozen["brand_description"],
        website_url=frozen["website_url"],
        sector_guidance=guidance,
        rag_context=None,
        max_duration=frozen["max_duration"],
    )

    assert len(calls) == 1, "script yüzeyi sessizce fallback'e düştü"
    assert result["script"] == "Donuk bir senaryo."
    assert "SEKTÖR REHBERİ" in calls[0].rendered
    assert_matches_fixture("short_video__script__with_guidance", calls[0].rendered)


async def test_script_request_without_guidance_matches_fixture(
    frozen_short_video_fixtures, monkeypatch
):
    """Script istemi — rehbersiz varyant: BUGÜNKÜ üretim davranışı budur."""
    frozen = frozen_short_video_fixtures
    calls = capture_anthropic_calls(monkeypatch, response_text="Donuk bir senaryo.")
    await generate_script(
        frozen["script_prompt"],
        frozen["brand_kit"],
        frozen["brand_name"],
        brand_description=frozen["brand_description"],
        website_url=frozen["website_url"],
        rag_context=None,
        max_duration=frozen["max_duration"],
    )

    assert len(calls) == 1, "script yüzeyi sessizce fallback'e düştü"
    assert "SEKTÖR REHBERİ" not in calls[0].rendered
    assert_matches_fixture("short_video__script__no_guidance", calls[0].rendered)
