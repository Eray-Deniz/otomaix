"""Rakip analizi endpoint'leri."""

from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.security import get_current_user
from app.models.schemas import OkResponse
from app.services.competitor_analyzer import (
    generate_competitor_report,
    run_full_analysis,
)

router = APIRouter(prefix="/competitors", tags=["competitors"])


# ─── Schemas ────────────────────────────────────────────────────────────────

class CompetitorCreate(BaseModel):
    brand_id: UUID
    competitor_name: str
    instagram_handle: str | None = None
    tiktok_handle: str | None = None
    website_url: str | None = None


# ─── Endpoints ──────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=OkResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(limiter(10, 3600))],  # 10/saat
)
async def add_competitor(
    payload: CompetitorCreate,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Yeni rakip ekle ve hemen analiz başlat."""
    row = await db.fetchrow(
        """
        INSERT INTO social.competitor_analyses
            (brand_id, competitor_name, instagram_handle, tiktok_handle, website_url)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *
        """,
        payload.brand_id,
        payload.competitor_name,
        payload.instagram_handle,
        payload.tiktok_handle,
        payload.website_url,
    )
    competitor = dict(row)

    # Analizi çalıştır ve sonucu kaydet
    analysis_data = await run_full_analysis(competitor)
    import json
    await db.execute(
        """
        UPDATE social.competitor_analyses
        SET analysis_data = $2::jsonb, last_analyzed_at = now()
        WHERE id = $1
        """,
        competitor["id"],
        json.dumps(analysis_data),
    )

    competitor["analysis_data"] = analysis_data
    competitor["last_analyzed_at"] = "just_now"
    return OkResponse(data=competitor)


@router.get("", response_model=OkResponse)
async def list_competitors(
    brand_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Bir markanın rakip listesini döndür."""
    rows = await db.fetch(
        """
        SELECT id, brand_id, competitor_name, instagram_handle, tiktok_handle,
               website_url, last_analyzed_at, created_at,
               analysis_data IS NOT NULL AS has_analysis
        FROM social.competitor_analyses
        WHERE brand_id = $1
        ORDER BY created_at DESC
        """,
        brand_id,
    )
    return OkResponse(data=[dict(r) for r in rows])


@router.get("/{competitor_id}/analysis", response_model=OkResponse)
async def get_analysis(
    competitor_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Rakibin detaylı analiz verisini döndür."""
    row = await db.fetchrow(
        "SELECT * FROM social.competitor_analyses WHERE id = $1",
        competitor_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Rakip bulunamadı")
    return OkResponse(data=dict(row))


@router.post("/{competitor_id}/refresh", response_model=OkResponse)
async def refresh_analysis(
    competitor_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Rakip analizini yeniden çalıştır."""
    row = await db.fetchrow(
        "SELECT * FROM social.competitor_analyses WHERE id = $1",
        competitor_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Rakip bulunamadı")

    competitor = dict(row)
    analysis_data = await run_full_analysis(competitor)

    import json
    await db.execute(
        """
        UPDATE social.competitor_analyses
        SET analysis_data = $2::jsonb, last_analyzed_at = now()
        WHERE id = $1
        """,
        competitor_id,
        json.dumps(analysis_data),
    )

    return OkResponse(data={"id": str(competitor_id), "analysis_data": analysis_data, "refreshed": True})


@router.delete("/{competitor_id}", response_model=OkResponse)
async def delete_competitor(
    competitor_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Rakibi sil."""
    result = await db.execute(
        "DELETE FROM social.competitor_analyses WHERE id = $1",
        competitor_id,
    )
    if result == "DELETE 0":
        raise HTTPException(status_code=404, detail="Rakip bulunamadı")
    return OkResponse(data={"deleted": True})


@router.get("/report/summary", response_model=OkResponse)
async def get_report(
    brand_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Tüm rakiplerin Claude sentez raporunu döndür."""
    brand = await db.fetchrow(
        "SELECT name, sector FROM social.brands WHERE id = $1", brand_id
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand bulunamadı")

    rows = await db.fetch(
        """
        SELECT competitor_name, analysis_data
        FROM social.competitor_analyses
        WHERE brand_id = $1 AND analysis_data IS NOT NULL
        ORDER BY last_analyzed_at DESC
        """,
        brand_id,
    )
    analyses = [dict(r) for r in rows]
    report = await generate_competitor_report(
        brand["name"],
        brand["sector"] or "",
        analyses,
    )
    return OkResponse(data=report)
