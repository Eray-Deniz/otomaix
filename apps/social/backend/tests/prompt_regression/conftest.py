"""Katman-1 fixture determinizminin dayandığı SABİT girdiler.

Fixture'lar ancak girdiler sabitse anlamlıdır. Bu dosya o girdi setini
versiyonlar: değişirse fixture'lar bilinçli olarak yeniden dondurulur ve
değişiklik commit'te görünür.
"""

from __future__ import annotations

import pytest

# Sektör rehberi OLAN bir slug — "yerine geçme" ancak bugün basılan blokla
# kanıtlanabilir (plan Task 6).
FROZEN_SECTOR_SLUG = "teknoloji"

# Carousel dalı için şablon (K-15b: `is_carousel` çıktı-biçim varyasyonu).
FROZEN_CAROUSEL_TEMPLATE_ID = "carousel-genel-sablon"
FROZEN_SINGLE_TEMPLATE_ID = "eticaret-urun-karti"


@pytest.fixture
def frozen_brand_fixtures() -> dict:
    """Sabit marka/brand_kit/ürün/platform girdileri."""
    return {
        "brand": {
            "name": "Donuk Teknoloji",
            "sector": "Teknoloji",
            "sector_slug": FROZEN_SECTOR_SLUG,
            "description": "Küçük işletmeler için bulut yazılımı.",
        },
        "brand_kit": {
            "tonality": "professional",
            "hashtags": ["#teknoloji", "#bulut", "#kobi"],
            "colors": {"primary": "#0A84FF", "secondary": "#1C1C1E"},
        },
        "product": {
            "name": "Bulut Panel",
            "description": "Tek ekrandan stok ve sipariş yönetimi.",
            "price": "499",
        },
        "platforms": ["instagram", "linkedin"],
        "template_fields": {},
        "user_prompt": "Yeni sürüm duyurusu",
        "special_day": {"name": "Cumhuriyet Bayramı", "category": "national"},
    }


# Kısa video yüzeylerinin sabit girdileri (plan Task 7). Ürün bilgisi üretimin
# kendi biçiminde kurulur (`posts.py` stage-1: "Name: / Description: / Tags:").
FROZEN_PRODUCT_INFO = (
    "Name: Bulut Panel\n"
    "Description: Tek ekrandan stok ve sipariş yönetimi.\n"
    "Tags: bulut, panel, kobi"
)


@pytest.fixture
def frozen_short_video_fixtures() -> dict:
    """Kısa video durağan kare + script yüzeylerinin sabit girdileri."""
    return {
        "topic": "Yeni sürüm duyurusu",
        "brand_name": "Donuk Teknoloji",
        "brand_description": "Küçük işletmeler için bulut yazılımı.",
        "sector": "Teknoloji",
        "color_str": "#0A84FF, #1C1C1E",
        "user_brief": "Ofiste ekibin panele bakarak gülümsediği bir sahne",
        "product_info": FROZEN_PRODUCT_INFO,
        "product_doc_context": "Panel, stok uyarılarını gün sonunda toplu gönderir.",
        "script_prompt": "Yeni sürümü duyuran kısa video",
        "brand_kit": {
            "tonality": "professional",
            "sector": "Teknoloji",
            "hashtags": ["#teknoloji", "#bulut", "#kobi"],
            "colors": {"primary": "#0A84FF", "secondary": "#1C1C1E"},
        },
        "website_url": "https://donukteknoloji.example",
        "max_duration": 30,
    }
