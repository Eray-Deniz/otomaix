"""Phase 6 — Sektör çözümleyici.

Markanın serbest metin `sector` alanını `social.sectors` tablosundaki `sector_id`'ye
(UUID) çevirir. Eşleşme yoksa 'genel' sektörüne düşer.

Dual-write stratejisi: `brands.py` create/update sırasında hem eski `sector` TEXT
hem de yeni `sector_id` UUID güncellenir. Mevcut kod (`ai.py`, `posts.py`, `trends.py`,
`competitors.py`) değişmeden `sector` TEXT alanını okumaya devam eder.
"""

import re
from uuid import UUID

import asyncpg

from app.core.cache import get_cached, set_cached

_SECTOR_MAP_TTL = 3600  # 1 saat — sektörler neredeyse hiç değişmez
# v3: harita YALNIZ kök sektörleri taşır (R-01). Sürüm artışı, filtresiz
# v2 değerini önbellekte bırakmış kurulumları da devre dışı bırakır.
_CACHE_KEY = "otomaix:social:sector_slug_map_v3"


class TaxonomyUnavailableError(RuntimeError):
    """Kök sektör taksonomisi kullanılamaz durumda — çözümleme YAPILMAZ.

    Kök harita boşsa ya da düşüş kovası (`genel`) yoksa çözümleyici bir sonuç
    UYDURAMAZ. Eskiden bu durumda `None` dönerdi ve çağıranlar onu "eşleşme yok"
    sanıyordu: `create_brand` markayı ham kullanıcı metniyle ve NULL `sector_id`
    ile yazıyor, `update_brand` metni değiştirip ESKİ `sector_id`'yi bırakıyordu
    — yani bozuk taksonomi sessizce tutarsız veri üretiyordu. Artık yazımdan
    ÖNCE durulur (Codex checkpoint 4, yüksek bulgu).
    """


def _normalize_slug(text: str | None) -> str:
    """Serbest metin sektör adını slug formatına indirger."""
    if not text:
        return "genel"
    lower = text.strip().lower()
    # Türkçe karakter → ASCII
    trans = str.maketrans({
        "ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u",
        "Ç": "c", "Ğ": "g", "İ": "i", "Ö": "o", "Ş": "s", "Ü": "u",
    })
    normalized = lower.translate(trans)
    # Boşluk/özel karakterleri tire yap
    slug = re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")
    return slug or "genel"


async def resolve_sector_id(db: asyncpg.Connection, sector_text: str | None) -> UUID:
    """Serbest metin sektör adından sector_id döndür.

    Taksonomi bozuksa `TaxonomyUnavailableError` fırlatır — `None` DÖNMEZ.
    """
    return (await resolve_sector(db, sector_text))[0]


async def resolve_sector(
    db: asyncpg.Connection, sector_text: str | None
) -> tuple[UUID, str]:
    """Slug veya serbest metinden (sector_id, display_name) tuple'ı döndür.

    brands.py dual-write için: TEXT kolona human-readable display_name yazılır,
    sector_id UUID kanonik referans olur. AI/trend/competitors kodu hala
    `brand['sector']` TEXT okur — Türkçe ad korunur, prompt kalitesi bozulmaz.

    - Boşsa veya eşleşme yoksa 'genel' sektörüne düşer
    - Kök harita boşsa, ya da eşleşme yokken düşüş kovası ('genel') da yoksa
      `TaxonomyUnavailableError` fırlatır (sessiz `None` YOK — çağıranlar onu
      "eşleşme yok" sanıp tutarsız yazıyordu)
    - 'teknoloji' (slug) veya 'Teknoloji' (display) → ('Teknoloji', UUID)
    - 'e-ticaret-perakende' → ('E-Ticaret & Perakende', UUID)
    """
    cached = await get_cached(_CACHE_KEY)
    if not cached:
        # R-01: alt sektör satırları (`parent_sector_id IS NOT NULL`) yalnız paket
        # katmanının adresidir — marka çözümlemesi onları HİÇ görmez. Filtre
        # burada durur: kısmi eşleşme dalı da aynı haritada gezer.
        rows = await db.fetch(
            "SELECT id::text, slug, display_name FROM social.sectors "
            "WHERE parent_sector_id IS NULL"
        )
        cached = {r["slug"]: {"id": r["id"], "display_name": r["display_name"]} for r in rows}
        await set_cached(_CACHE_KEY, cached, _SECTOR_MAP_TTL)

    # Fail-closed: boş haritada hiçbir girdi çözülemez.
    if not cached:
        raise TaxonomyUnavailableError(
            "Kök sektör haritası BOŞ — migration/seed uygulanmamış olabilir."
        )

    slug = _normalize_slug(sector_text)

    if slug in cached:
        entry = cached[slug]
        return UUID(entry["id"]), entry["display_name"]

    # Kısmi eşleşme
    for known_slug, entry in cached.items():
        if known_slug != "genel" and known_slug in slug:
            return UUID(entry["id"]), entry["display_name"]

    # Buraya gelen girdi hiçbir kök satırla eşleşmedi: düşüş kovası ŞART.
    # Kapı dar tutulur — taksonomi onarımı sırasında tam eşleşen bir kök satır
    # hâlâ çözülebilir kalsın diye kontrol sona bırakılır.
    if "genel" not in cached:
        raise TaxonomyUnavailableError(
            f"'{slug}' hiçbir kök sektörle eşleşmedi ve düşüş kovası ('genel') "
            f"haritada YOK (kayıt sayısı={len(cached)})."
        )

    entry = cached["genel"]
    return UUID(entry["id"]), entry["display_name"]
