"""Trend analizi endpoint'leri.

GET /trends?brand_id=uuid  → markanın sektörüne ait güncel trendler
POST /trends/{trend_id}/create-post → trend prompt'u ile içerik oluştur
POST /trends/refresh?brand_id=uuid  → önbelleği atlayarak taze veri çek
"""

from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import OkResponse
from app.services.fal_ai import generate_image
from app.services.trend_analyzer import get_cached_or_fresh_trends, get_trends_for_sector

router = APIRouter(prefix="/trends", tags=["trends"])


# ─── Schemas ────────────────────────────────────────────────────────────────

class TrendCreatePost(BaseModel):
    brand_id: UUID
    suggested_prompt: str
    content_type: str = "image"
    aspect_ratio: str = "1:1"
    platforms: list[str] = []


# ─── Endpoints ──────────────────────────────────────────────────────────────

@router.get("", response_model=OkResponse)
async def get_trends(
    brand_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Markanın sektörüne göre güncel trendleri döndür (6 saatlik önbellekle)."""
    brand = await db.fetchrow(
        "SELECT name, sector FROM social.brands WHERE id = $1",
        brand_id,
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand bulunamadı")

    sector = brand["sector"] or "genel"
    brand_name = brand["name"] or ""

    trends = await get_cached_or_fresh_trends(sector, brand_name, db, max_age_hours=6)

    return OkResponse(
        data={
            "sector": sector,
            "trends": trends,
            "count": len(trends),
        }
    )


@router.post("/refresh", response_model=OkResponse)
async def refresh_trends(
    brand_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Önbelleği atlayarak taze trend verisi çek ve kaydet."""
    brand = await db.fetchrow(
        "SELECT name, sector FROM social.brands WHERE id = $1",
        brand_id,
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand bulunamadı")

    sector = brand["sector"] or "genel"
    brand_name = brand["name"] or ""

    # Taze veri çek (önbelleği atla)
    trends = await get_trends_for_sector(sector, brand_name)

    import json
    await db.execute(
        """
        INSERT INTO social.trend_cache (sector, trends)
        VALUES ($1, $2::jsonb)
        """,
        sector,
        json.dumps(trends),
    )

    return OkResponse(
        data={
            "sector": sector,
            "trends": trends,
            "refreshed": True,
        }
    )


@router.post("/{trend_index}/create-post", response_model=OkResponse, status_code=status.HTTP_201_CREATED)
async def create_post_from_trend(
    trend_index: int,
    payload: TrendCreatePost,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Trend prompt'u kullanarak içerik oluştur ve fal.ai tetikle."""
    brand = await db.fetchrow(
        "SELECT brand_kit, name, sector FROM social.brands WHERE id = $1",
        payload.brand_id,
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand bulunamadı")

    raw_kit = brand["brand_kit"]
    if raw_kit and isinstance(raw_kit, str):
        import json as _json
        raw_kit = _json.loads(raw_kit)
    brand_kit = dict(raw_kit) if raw_kit else {}

    row = await db.fetchrow(
        """
        INSERT INTO social.posts
            (brand_id, content_type, prompt, aspect_ratio, platforms, status)
        VALUES ($1, $2, $3, $4, $5, 'generating')
        RETURNING *
        """,
        payload.brand_id,
        payload.content_type,
        payload.suggested_prompt,
        payload.aspect_ratio,
        payload.platforms,
    )
    post = dict(row)

    try:
        fal_job_id = await generate_image(
            payload.suggested_prompt,
            payload.aspect_ratio,
            brand_kit,
        )
        await db.execute(
            "UPDATE social.posts SET fal_job_id = $2 WHERE id = $1",
            post["id"],
            fal_job_id,
        )
        post["fal_job_id"] = fal_job_id
    except Exception:
        pass  # Webhook üretim başarısızlığını yönetir

    return OkResponse(data={"post_id": str(post["id"]), "status": "generating"})
