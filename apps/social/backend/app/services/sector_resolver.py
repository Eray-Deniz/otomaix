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
_CACHE_KEY = "otomaix:social:sector_slug_map_v2"


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


async def resolve_sector_id(db: asyncpg.Connection, sector_text: str | None) -> UUID | None:
    """Serbest metin sektör adından sector_id döndür."""
    resolved = await resolve_sector(db, sector_text)
    return resolved[0] if resolved else None


async def resolve_sector(
    db: asyncpg.Connection, sector_text: str | None
) -> tuple[UUID, str] | None:
    """Slug veya serbest metinden (sector_id, display_name) tuple'ı döndür.

    brands.py dual-write için: TEXT kolona human-readable display_name yazılır,
    sector_id UUID kanonik referans olur. AI/trend/competitors kodu hala
    `brand['sector']` TEXT okur — Türkçe ad korunur, prompt kalitesi bozulmaz.

    - Boşsa veya eşleşme yoksa 'genel' sektörüne düşer
    - 'teknoloji' (slug) veya 'Teknoloji' (display) → ('Teknoloji', UUID)
    - 'e-ticaret-perakende' → ('E-Ticaret & Perakende', UUID)
    """
    cached = await get_cached(_CACHE_KEY)
    if not cached:
        rows = await db.fetch("SELECT id::text, slug, display_name FROM social.sectors")
        cached = {r["slug"]: {"id": r["id"], "display_name": r["display_name"]} for r in rows}
        await set_cached(_CACHE_KEY, cached, _SECTOR_MAP_TTL)

    slug = _normalize_slug(sector_text)

    if slug in cached:
        entry = cached[slug]
        return UUID(entry["id"]), entry["display_name"]

    # Kısmi eşleşme
    for known_slug, entry in cached.items():
        if known_slug != "genel" and known_slug in slug:
            return UUID(entry["id"]), entry["display_name"]

    if "genel" in cached:
        entry = cached["genel"]
        return UUID(entry["id"]), entry["display_name"]
    return None
