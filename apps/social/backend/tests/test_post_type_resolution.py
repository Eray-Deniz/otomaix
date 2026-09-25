"""Gönderi türü koddan çözülür (tasarım notu 2026-09-25 §3.1, §3.2, K-G; plan Task 5)."""

from __future__ import annotations

import itertools

import pytest

from app.services.sector_packages import (
    DAY_TYPE_TO_POST_TYPE,
    PostTypeResolution,
    resolve_post_type,
)

_DAY_TYPES = (None, "ticari-firsat", "karma", "kutlama", "anma")
_PRODUCTS = (None, "product", "service")

_EXPECTED_DAY = {
    "ticari-firsat": "satis",
    "karma": "satis",
    "kutlama": "kutlama",
    "anma": "anma",
}
_EXPECTED_PRODUCT = {"product": "satis", "service": "hizmet"}


def _day(tur: str) -> dict:
    return {
        "tur": tur,
        "mesaj_ekseni": "Eksen",
        "kanca": "Kanca",
        "cta": "içerik-önerilmez",
        "gorsel_vurgu": "Vurgu",
    }


@pytest.mark.parametrize(("day_type", "product_type"), list(itertools.product(_DAY_TYPES, _PRODUCTS)))
def test_resolution_matrix_generated(day_type, product_type):
    day_entry = _day(day_type) if day_type else None
    product = {"name": "Yüzük", "type": product_type} if product_type else None

    result = resolve_post_type(day_entry, product)

    if day_type is not None:
        assert result == PostTypeResolution(_EXPECTED_DAY[day_type], "gun_kaydi")
    elif product_type is not None:
        assert result == PostTypeResolution(_EXPECTED_PRODUCT[product_type], "urun_varsayilan")
    else:
        assert result == PostTypeResolution(None, "model")


def test_unknown_day_type_raises():
    with pytest.raises(ValueError, match="gün türü"):
        resolve_post_type(_day("bayram-indirimi"), None)


def test_product_without_type_raises():
    with pytest.raises(ValueError, match="type"):
        resolve_post_type(None, {"name": "Yüzük"})
    with pytest.raises(ValueError, match="type"):
        resolve_post_type(None, {"name": "Yüzük", "type": "bundle"})


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Ticari-Fırsat", "satis"),
        ("TİCARİ FIRSAT", "satis"),
        ("ticari_firsat", "satis"),
        ("KARMA", "satis"),
        ("Kutlama", "kutlama"),
        ("ANMA", "anma"),
    ],
)
def test_day_type_folding(raw, expected):
    assert resolve_post_type(_day(raw), None) == PostTypeResolution(expected, "gun_kaydi")
    assert set(DAY_TYPE_TO_POST_TYPE) == set(_EXPECTED_DAY)
