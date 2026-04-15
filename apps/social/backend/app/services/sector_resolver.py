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
_CACHE_KEY = "otomaix:social:sector_slug_map"


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


async def _load_slug_to_id_map(db: asyncpg.Connection) -> dict[str, str]:
    """Tüm sektör slug→id eşleşmesini Redis cache üzerinden getir."""
    cached = await get_cached(_CACHE_KEY)
    if cached:
        return cached

    rows = await db.fetch("SELECT id::text, slug FROM social.sectors")
    mapping = {r["slug"]: r["id"] for r in rows}
    await set_cached(_CACHE_KEY, mapping, _SECTOR_MAP_TTL)
    return mapping


async def resolve_sector_id(db: asyncpg.Connection, sector_text: str | None) -> UUID | None:
    """Serbest metin sektör adından sector_id döndür.

    - Boşsa veya eşleşme yoksa 'genel' sektörüne düşer
    - 'Teknoloji' → 'teknoloji' slug → UUID
    - 'E-Ticaret' → 'e-ticaret' slug → UUID
    """
    mapping = await _load_slug_to_id_map(db)
    slug = _normalize_slug(sector_text)

    # Doğrudan eşleşme
    if slug in mapping:
        return UUID(mapping[slug])

    # Kısmi eşleşme (kullanıcı "teknoloji ve yazılım" yazdıysa "teknoloji"yi bul)
    for known_slug, sector_id in mapping.items():
        if known_slug != "genel" and known_slug in slug:
            return UUID(sector_id)

    # Son çare: genel
    return UUID(mapping["genel"]) if "genel" in mapping else None
