"""Auto posting configuration endpoints."""

import json
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import OkResponse

router = APIRouter(prefix="/autoposting", tags=["autoposting"])


class AutopostingConfigRequest(BaseModel):
    brand_id: UUID
    frequency: str  # daily | 3x_weekly | weekly
    time_slots: list[dict]  # [{"day": "monday", "time": "10:00"}, ...]
    content_types: list[str]  # image | carousel | video
    content_categories: list[str]  # product | service | corporate
    topics: list[str]
    platforms: list[str]
    telegram_approval: bool = False
    telegram_bot_token: str = ""   # müşteriye özel bot token
    telegram_chat_id: str = ""     # müşterinin Telegram chat ID'si


@router.get("/config", response_model=OkResponse)
async def get_config(
    brand_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Get auto posting config for a brand."""
    row = await db.fetchrow(
        "SELECT * FROM social.autoposting_configs WHERE brand_id = $1",
        brand_id,
    )
    return OkResponse(data=dict(row) if row else None)


@router.post("/config", response_model=OkResponse)
async def upsert_config(
    payload: AutopostingConfigRequest,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Create or update auto posting config."""
    row = await db.fetchrow(
        """
        INSERT INTO social.autoposting_configs
            (brand_id, frequency, time_slots, content_types, content_categories,
             topics, platforms, telegram_approval, telegram_bot_token, telegram_chat_id)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ON CONFLICT (brand_id) DO UPDATE SET
            frequency           = EXCLUDED.frequency,
            time_slots          = EXCLUDED.time_slots,
            content_types       = EXCLUDED.content_types,
            content_categories  = EXCLUDED.content_categories,
            topics              = EXCLUDED.topics,
            platforms           = EXCLUDED.platforms,
            telegram_approval   = EXCLUDED.telegram_approval,
            telegram_bot_token  = EXCLUDED.telegram_bot_token,
            telegram_chat_id    = EXCLUDED.telegram_chat_id,
            updated_at          = now()
        RETURNING *
        """,
        payload.brand_id,
        payload.frequency,
        json.dumps(payload.time_slots),
        payload.content_types,
        payload.content_categories,
        payload.topics,
        payload.platforms,
        payload.telegram_approval,
        payload.telegram_bot_token or None,
        payload.telegram_chat_id or None,
    )
    return OkResponse(data=dict(row))


@router.post("/toggle", response_model=OkResponse)
async def toggle_config(
    brand_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Toggle is_enabled for a brand's auto posting config."""
    row = await db.fetchrow(
        """
        UPDATE social.autoposting_configs
        SET is_enabled = NOT is_enabled, updated_at = now()
        WHERE brand_id = $1
        RETURNING id, is_enabled
        """,
        brand_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Config not found")
    return OkResponse(data={"is_enabled": row["is_enabled"]})


@router.get("/upcoming", response_model=OkResponse)
async def get_upcoming(
    brand_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Return next 5 scheduled posts for a brand."""
    rows = await db.fetch(
        """
        SELECT id, content_type, status, thumbnail_url, caption, scheduled_at
        FROM social.posts
        WHERE brand_id = $1
          AND status = 'scheduled'
          AND scheduled_at > now()
        ORDER BY scheduled_at
        LIMIT 5
        """,
        brand_id,
    )
    return OkResponse(data=[dict(r) for r in rows])
