"""Phase 6 — Sektör listesi endpoint'i.

Frontend (onboarding, marka oluşturma, marka ayarları) artık sektör listesini
hardcoded const yerine bu endpoint'ten çeker. Tek doğruluk kaynağı: social.sectors.
"""

import asyncpg
from fastapi import APIRouter, Depends

from app.core.cache import get_cached, set_cached
from app.core.database import get_db
from app.models.schemas import OkResponse

router = APIRouter(prefix="/sectors", tags=["sectors"])

_CACHE_KEY = "otomaix:social:sectors:list"
_TTL = 3600  # 1 saat — sektörler neredeyse hiç değişmez


@router.get("", response_model=OkResponse)
async def list_sectors(db: asyncpg.Connection = Depends(get_db)):
    """Tüm aktif sektörleri döndürür (auth gerekmez — onboarding'de de kullanılır)."""
    cached = await get_cached(_CACHE_KEY)
    if cached is not None:
        return OkResponse(data=cached)

    rows = await db.fetch(
        """
        SELECT id::text, slug, display_name, parent_sector_id::text, keywords
        FROM social.sectors
        ORDER BY display_name
        """
    )
    data = [dict(r) for r in rows]
    await set_cached(_CACHE_KEY, data, _TTL)
    return OkResponse(data=data)
