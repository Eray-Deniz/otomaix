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
    # Kolonun GERÇEK nesne hâli. `object` doğrudan; `string` ise ÇİFT KODLANMIŞ
    # bir nesne olabilir (bu projede yaşanmış bir kaza — `parse_brand_kit` tam
    # bu yüzden JSON dizesi dönüşünü ayrıca ele alır). Çözülmüş biçim geçerli
    # bir nesneyse birleştirmeye O girer.
    #
    # Bu dal olmasaydı — ve ilk yazımda yoktu — çift kodlu bir satırda tek
    # alanlık güncelleme mevcut TÜM kit alanlarını sessizce silerdi (ölçüldü).
    # Yani eşzamanlılık sınıfı kapatılırken yeni bir veri kaybı sınıfı açılmıştı.
    #
    # Geriye kalan (sayı/dizi/çözülemeyen metin) hiçbir kod yolunun ürettiği bir
    # değer değildir; boş sayılır ve bu bilinçli bir sadeleştirmedir.
    kit = (
        "CASE WHEN jsonb_typeof(brand_kit) = 'object' THEN brand_kit "
        "WHEN jsonb_typeof(brand_kit) = 'string' "
        "AND (brand_kit #>> '{}') IS JSON OBJECT THEN (brand_kit #>> '{}')::jsonb "
        "ELSE '{}'::jsonb END"
    )
    base = f"({kit}) || ${kit_param}"
    if channels_param is None:
        return base
    previous_channels = (
        f"CASE WHEN jsonb_typeof(({kit}) -> 'channels') = 'object' "
        f"THEN ({kit}) -> 'channels' ELSE '{{}}'::jsonb END"
    )
    return (
        f"({base}) || jsonb_build_object('channels', "
        f"{previous_channels} || ${channels_param})"
    )
