"""Workspace ayarları — Telegram entegrasyonu vb."""

import asyncpg
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import OkResponse

router = APIRouter(prefix="/settings", tags=["settings"])


class WorkspaceSettingsUpdate(BaseModel):
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""


@router.get("", response_model=OkResponse)
async def get_settings(
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Kullanıcının workspace ayarlarını döndür."""
    row = await db.fetchrow(
        "SELECT telegram_bot_token, telegram_chat_id FROM social.workspaces WHERE account_id = $1",
        user["sub"],
    )
    if not row:
        return OkResponse(data={"telegram_bot_token": "", "telegram_chat_id": ""})
    return OkResponse(data={
        "telegram_bot_token": row["telegram_bot_token"] or "",
        "telegram_chat_id": row["telegram_chat_id"] or "",
    })


@router.patch("", response_model=OkResponse)
async def update_settings(
    payload: WorkspaceSettingsUpdate,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Workspace Telegram ayarlarını güncelle."""
    await db.execute(
        """
        UPDATE social.workspaces
        SET telegram_bot_token = $2,
            telegram_chat_id   = $3
        WHERE account_id = $1
        """,
        user["sub"],
        payload.telegram_bot_token or None,
        payload.telegram_chat_id or None,
    )
    return OkResponse(data={
        "telegram_bot_token": payload.telegram_bot_token,
        "telegram_chat_id": payload.telegram_chat_id,
    })
