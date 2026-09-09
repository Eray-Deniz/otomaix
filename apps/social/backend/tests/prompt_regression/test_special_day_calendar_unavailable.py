"""K-112 (a) — takvim ERİŞİLEMEZKEN üretim yolu (Plan 2 Task 12).

Ölçülen şey eşleşmeme DEĞİL, **erişilemezliktir**: takvim okunamadığında özel
gün bağlamı BOŞ döner, blok sessizce düşer ve **zorunlu maskeli log** yazılır.
Uydurma anahtar hiçbir koşulda üretilmez.

**Neden burada.** Bu yol Katman-1'in enjeksiyon yüzeyidir: bağlam boşaldığında
üretilen prompt, özel günsüz dondurulmuş fixture ile BAYT BAYT aynı olmalıdır.
Sessiz düşüşün "sessiz" ayağı ancak bu karşılaştırmayla kanıtlanır; "log" ayağı
ise ayrı ölçülür — ikisi birlikte kararın tamamıdır (spec §11, karar K-112).

Taban ölçümü: `docs/research/2026-08-27-k112-takvim-erisilemezlik-taban.md`.
"""

from __future__ import annotations

import logging

import pytest

from app.core.caption_generator import generate_captions
from app.core.templates_data import get_template_by_id
from app.routers import calendar as calendar_router

from .capture import assert_matches_fixture, capture_anthropic_calls
from .conftest import FROZEN_SINGLE_TEMPLATE_ID


SIR_TASIYAN_HATA = (
    "connection failed: postgresql://paket:supergizliparola@db.internal:5432/social"
)
SIZAN_PAROLA = "supergizliparola"


class _DusenBaglanti:
    """Takvim tablosuna erişemeyen bağlantı — hata ENJEKSİYONU."""

    async def fetch(self, *args, **kwargs):
        raise RuntimeError(SIR_TASIYAN_HATA)


@pytest.fixture
def cachesiz(monkeypatch):
    """Önbellek yolu devre dışı — ölçülen şey tablo erişimi."""

    async def _bos(_key):
        return None

    async def _yaz(*_args, **_kwargs):
        return None

    monkeypatch.setattr(calendar_router, "get_cached", _bos)
    monkeypatch.setattr(calendar_router, "set_cached", _yaz)


async def test_calendar_unavailable_yields_empty_special_day_context_and_logs(
    cachesiz, caplog
):
    """Takvim okunamazsa bağlam BOŞ döner ve ZORUNLU log yazılır."""
    with caplog.at_level(logging.WARNING, logger=calendar_router.__name__):
        cevap = await calendar_router.get_holidays(
            year=2099, user={"id": "u1"}, db=_DusenBaglanti()
        )

    assert cevap.data == [], "erişilemez takvim uydurma gün ÜRETEMEZ"
    assert caplog.records, "sessiz düşüş LOGSUZ olamaz (K-112 zorunlu log)"
    assert any(
        "takvim" in kayit.getMessage().lower() for kayit in caplog.records
    ), "log arızayı adıyla anmalı"


async def test_calendar_unavailable_log_is_masked(cachesiz, caplog):
    """K-136: log maskeleme süzgecinden geçer — sır hiçbir kopyaya girmez."""
    with caplog.at_level(logging.WARNING, logger=calendar_router.__name__):
        await calendar_router.get_holidays(
            year=2099, user={"id": "u1"}, db=_DusenBaglanti()
        )

    metin = " ".join(kayit.getMessage() for kayit in caplog.records)
    assert SIZAN_PAROLA not in metin, "ham parola günlüğe SIZDI"
    assert "***" in metin, "maskeleme süzgeci hiç çalışmamış"


async def test_empty_special_day_context_keeps_layer_one_byte_identical(
    frozen_brand_fixtures, monkeypatch
):
    """Bağlam boşaldığında üretilen prompt özel günsüz fixture ile AYNI bayttır."""
    calls = capture_anthropic_calls(monkeypatch)
    await generate_captions(
        brand=frozen_brand_fixtures["brand"],
        brand_kit=frozen_brand_fixtures["brand_kit"],
        template=get_template_by_id(FROZEN_SINGLE_TEMPLATE_ID),
        template_fields=frozen_brand_fixtures["template_fields"],
        user_prompt=frozen_brand_fixtures["user_prompt"],
        rag_context=None,
        platforms=frozen_brand_fixtures["platforms"],
        product=frozen_brand_fixtures["product"],
        content_type="image",
        special_day_name=None,
        special_day_category=None,
    )
    assert len(calls) == 1
    assert "ÖZEL GÜN" not in calls[0].rendered
    assert_matches_fixture("caption__single__no_special_day", calls[0].rendered)
