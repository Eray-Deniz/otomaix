"""Shared helpers used by multiple routers/services."""

from __future__ import annotations

import json


def parse_brand_kit(raw) -> dict:
    """asyncpg bazen JSONB kolonunu string olarak döndürür — her ikisini de handle et."""
    if not raw:
        return {}
    if isinstance(raw, str):
        return json.loads(raw)
    return dict(raw)


def brand_kit_merge_sql(kit_param: int, channels_param: int | None = None) -> str:
    """`brand_kit` yazımının TEK birleştirme ifadesi — üç yazıcı da bunu kullanır.

    Kapatılan sınıf (checkpoint 9, iki tur): **"bayat bir okumadan hesaplanmış
    belgeyle `brand_kit`i değiştirebilen her yol"**. Üç üyesi vardı —
    `update_brand_kit` ve `avatar.py`nin iki yazıcısı sunucuda okuyup geri
    yazıyordu; `update_brand` ise istemcinin gönderdiği tam belgeyi doğrudan
    atıyordu. Üçü de tek bir sunucu-taraflı birleştirmeye indirgendi, çünkü
    ölçüldü: dört eşzamanlı yazımda dört anahtardan ÜÇÜ sessizce kayboluyordu.

    Kaybın neden sessiz olmadığı önemli: kanal envanteri düşerse CTA filtresi
    muhafazakâr davranıp kalıpları atlar — kullanıcıya "CTA'lar sebepsiz
    kayboldu" olarak görünür.

    `channels` ANAHTAR BAZINDA birleşir (spec §12.2 "deep-merge"), kitin geri
    kalanı üst düzeyde. `jsonb_typeof` kapıları kolon NULL ya da nesne-olmayan
    bir JSON taşırken `||` operatörünün patlamasını önler.

    Bedeli dürüstçe: bu yolla bir kit anahtarı SİLİNEMEZ, yalnız üzerine
    yazılabilir. PATCH semantiği zaten kısmi güncellemedir; silme gerekirse
    ayrı ve açık bir uç ister.
    """
    base = (
        "CASE WHEN jsonb_typeof(brand_kit) = 'object' "
        f"THEN brand_kit ELSE '{{}}'::jsonb END || ${kit_param}"
    )
    if channels_param is None:
        return base
    return (
        f"({base}) || jsonb_build_object('channels', "
        "CASE WHEN jsonb_typeof(brand_kit -> 'channels') = 'object' "
        f"THEN brand_kit -> 'channels' ELSE '{{}}'::jsonb END || ${channels_param})"
    )
