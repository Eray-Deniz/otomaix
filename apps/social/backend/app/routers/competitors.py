"""Rakip analizi endpoint'leri."""

import json
import logging
from uuid import UUID

import asyncpg
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.database import get_db, get_pool
from app.core.rate_limit import limiter
from app.core.security import assert_brand_owned, get_current_user
from app.models.schemas import OkResponse
from app.services.competitor_analyzer import (
    generate_competitor_report,
    run_full_analysis,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/competitors", tags=["competitors"])


# ─── Schemas ────────────────────────────────────────────────────────────────

class CompetitorCreate(BaseModel):
    brand_id: UUID
    competitor_name: str
    instagram_handle: str | None = None
    tiktok_handle: str | None = None
    website_url: str | None = None


# ─── Background task helper ─────────────────────────────────────────────────

async def _run_analysis_task(competitor_id: UUID) -> None:
    """Background task: fetch competitor row, run analysis, persist result.

    Request-scoped DB connection closes after the response is sent, so this
    task acquires its own connection from the global pool. Errors are
    captured into the `status='failed'` + `error_message` state.
    """
    pool = await get_pool()
    async with pool.acquire() as db:
        row = await db.fetchrow(
            "SELECT * FROM social.competitor_analyses WHERE id = $1",
            competitor_id,
        )
        if not row:
            return
        competitor = dict(row)

    try:
        analysis_data = await run_full_analysis(competitor)
        async with pool.acquire() as db:
            await db.execute(
                """
                UPDATE social.competitor_analyses
                SET analysis_data = $2::jsonb,
                    status = 'ready',
                    error_message = NULL,
                    last_analyzed_at = now()
                WHERE id = $1
                """,
                competitor_id,
                json.dumps(analysis_data),
            )
    except Exception as exc:  # noqa: BLE001
        logger.exception("competitor analysis failed for %s", competitor_id)
        async with pool.acquire() as db:
            await db.execute(
                """
                UPDATE social.competitor_analyses
                SET status = 'failed',
                    error_message = $2
                WHERE id = $1
                """,
                competitor_id,
                str(exc)[:500],
            )


# ─── Endpoints ──────────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=OkResponse,
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(limiter(10, 3600))],  # 10/saat
)
async def add_competitor(
    payload: CompetitorCreate,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Yeni rakip ekle; analiz arka planda çalışır, 202 Accepted döner.

    Önceden bu endpoint run_full_analysis()'i senkron çağırıyordu ve 30+ saniye
    bloklu kalıyordu (Cloudflare 504 / uvicorn worker tükenmesi riski).
    Artık kaydı `status='analyzing'` ile INSERT eder, BackgroundTasks ile
    analizi planlar ve hemen döner. Frontend `GET /competitors/{id}/analysis`
    ile polling yaparak sonucu alır.
    """
    await assert_brand_owned(db, user, payload.brand_id)
    row = await db.fetchrow(
        """
        INSERT INTO social.competitor_analyses
            (brand_id, competitor_name, instagram_handle, tiktok_handle,
             website_url, status)
        VALUES ($1, $2, $3, $4, $5, 'analyzing')
        RETURNING *
        """,
        payload.brand_id,
        payload.competitor_name,
        payload.instagram_handle,
        payload.tiktok_handle,
        payload.website_url,
    )
    competitor = dict(row)
    background_tasks.add_task(_run_analysis_task, competitor["id"])
    return OkResponse(data=competitor)


@router.get("", response_model=OkResponse)
async def list_competitors(
    brand_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Bir markanın rakip listesini döndür."""
    await assert_brand_owned(db, user, brand_id)
    rows = await db.fetch(
        """
        SELECT id, brand_id, competitor_name, instagram_handle, tiktok_handle,
               website_url, last_analyzed_at, created_at, status, error_message,
               analysis_data IS NOT NULL AS has_analysis
        FROM social.competitor_analyses
        WHERE brand_id = $1
        ORDER BY created_at DESC
        """,
        brand_id,
    )
    return OkResponse(data=[dict(r) for r in rows])


def _row_to_competitor(row: asyncpg.Record) -> dict:
    """Row → dict, `analysis_data` jsonb alanını güvenli şekilde parse et.

    asyncpg jsonb codec register edilmiş olsa bile (bkz. database.py), bu
    helper belt-and-suspenders olarak str/dict ikisini de handle eder —
    böylece codec başarısız olsa bile frontend her zaman dict alır.
    """
    data = dict(row)
    raw = data.get("analysis_data")
    if isinstance(raw, str):
        try:
            data["analysis_data"] = json.loads(raw)
        except (ValueError, TypeError):
            data["analysis_data"] = None
    return data


@router.get("/{competitor_id}/analysis", response_model=OkResponse)
async def get_analysis(
    competitor_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Rakibin detaylı analiz verisini döndür (polling için kullanılır)."""
    account_id = user.get("sub")
    row = await db.fetchrow(
        """
        SELECT c.*
        FROM social.competitor_analyses c
        JOIN social.brands b ON b.id = c.brand_id
        JOIN social.workspace_members m ON m.workspace_id = b.workspace_id
        WHERE c.id = $1 AND m.account_id = $2
        """,
        competitor_id,
        account_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Rakip bulunamadı")
    return OkResponse(data=_row_to_competitor(row))


@router.post(
    "/{competitor_id}/refresh",
    response_model=OkResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def refresh_analysis(
    competitor_id: UUID,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Rakip analizini yeniden çalıştır (background task, 202 Accepted)."""
    account_id = user.get("sub")
    row = await db.fetchrow(
        """
        SELECT c.*
        FROM social.competitor_analyses c
        JOIN social.brands b ON b.id = c.brand_id
        JOIN social.workspace_members m ON m.workspace_id = b.workspace_id
        WHERE c.id = $1 AND m.account_id = $2
        """,
        competitor_id,
        account_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Rakip bulunamadı")

    if row["status"] == "analyzing":
        raise HTTPException(status_code=409, detail="Analiz zaten devam ediyor")

    await db.execute(
        """
        UPDATE social.competitor_analyses
        SET status = 'analyzing', error_message = NULL
        WHERE id = $1
        """,
        competitor_id,
    )
    background_tasks.add_task(_run_analysis_task, competitor_id)
    return OkResponse(data={"id": str(competitor_id), "status": "analyzing"})


@router.delete("/{competitor_id}", response_model=OkResponse)
async def delete_competitor(
    competitor_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Rakibi sil."""
    account_id = user.get("sub")
    result = await db.execute(
        """
        DELETE FROM social.competitor_analyses c
        USING social.brands b, social.workspace_members m
        WHERE c.id = $1
          AND b.id = c.brand_id
          AND m.workspace_id = b.workspace_id
          AND m.account_id = $2
        """,
        competitor_id,
        account_id,
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
    await assert_brand_owned(db, user, brand_id)
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
