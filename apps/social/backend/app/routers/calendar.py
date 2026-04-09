"""Calendar endpoints — posts in date range + Turkish public holidays."""

from datetime import date, datetime
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import OkResponse

router = APIRouter(prefix="/calendar", tags=["calendar"])


# ─── GET /calendar/posts ─────────────────────────────────────────────────────

@router.get("/posts", response_model=OkResponse)
async def get_calendar_posts(
    brand_id: UUID,
    start: date,
    end: date,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Return posts in date range for calendar display."""
    rows = await db.fetch(
        """
        SELECT id, content_type, status, thumbnail_url, output_url,
               caption, platforms, scheduled_at, published_at, created_at
        FROM social.posts
        WHERE brand_id = $1
          AND (
            (scheduled_at BETWEEN $2 AND $3)
            OR (published_at BETWEEN $2 AND $3)
            OR (created_at::date BETWEEN $2 AND $3)
          )
        ORDER BY COALESCE(scheduled_at, published_at, created_at)
        """,
        brand_id,
        datetime.combine(start, datetime.min.time()),
        datetime.combine(end, datetime.max.time()),
    )
    items = []
    for r in rows:
        row = dict(r)
        event_date = row.get("scheduled_at") or row.get("published_at") or row.get("created_at")
        title = (row.get("caption") or "")[:30] or row["content_type"]
        items.append({
            "id": str(row["id"]),
            "title": title,
            "date": event_date.date().isoformat() if event_date else None,
            "status": row["status"],
            "thumbnail_url": row.get("thumbnail_url") or row.get("output_url"),
            "platforms": row.get("platforms") or [],
            "scheduled_at": row["scheduled_at"].isoformat() if row["scheduled_at"] else None,
            "published_at": row["published_at"].isoformat() if row["published_at"] else None,
        })
    return OkResponse(data=items)


# ─── PATCH /posts/{post_id}/schedule ──────────────────────────────────────────
# (Added here for calendar use; also usable standalone)

class ScheduleRequest(BaseModel):
    scheduled_at: datetime


@router.patch("/schedule/{post_id}", response_model=OkResponse)
async def schedule_post(
    post_id: UUID,
    payload: ScheduleRequest,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Set or update a post's scheduled_at datetime."""
    row = await db.fetchrow(
        "UPDATE social.posts SET scheduled_at = $2, status = 'scheduled', updated_at = now() WHERE id = $1 RETURNING id, status, scheduled_at",
        post_id,
        payload.scheduled_at,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")
    return OkResponse(data={
        "post_id": str(row["id"]),
        "status": row["status"],
        "scheduled_at": row["scheduled_at"].isoformat(),
    })


# ─── GET /calendar/holidays ───────────────────────────────────────────────────

@router.get("/holidays", response_model=OkResponse)
async def get_holidays(
    year: int,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Return Turkish public holidays for the given year."""
    try:
        rows = await db.fetch(
            "SELECT date, name_tr, name_en, category FROM social.public_holidays WHERE year = $1 ORDER BY date",
            year,
        )
        return OkResponse(data=[dict(r) for r in rows])
    except Exception:
        # Table may not exist yet — return empty list
        return OkResponse(data=[])
