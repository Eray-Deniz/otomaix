"""Social account OAuth link generation and account listing."""

from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse

from app.core.database import get_db
from app.core.security import assert_brand_owned, get_current_user
from app.models.schemas import OkResponse
from app.services.upload_post import (
    fetch_social_accounts,
    generate_connect_url,
    sync_social_accounts,
)

router = APIRouter(prefix="/social", tags=["social"])

FRONTEND_SETTINGS_URL = "https://app.otomaix.com/marka-ayarlari?tab=sosyal"


@router.get("/oauth-link", response_model=OkResponse)
async def oauth_link(
    brand_id: UUID,
    platform: str,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """
    Return an Upload-Post access URL (48h, single use) that the user visits
    to link their social media account for this brand.
    """
    await assert_brand_owned(db, user, brand_id)
    try:
        url = await generate_connect_url(brand_id, platform, db)
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))
    return OkResponse(data={"url": url, "platform": platform})


@router.get("/accounts", response_model=OkResponse)
async def list_connected_accounts(
    brand_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """
    List active social media accounts connected to a brand.
    Syncs from Upload-Post on each call so the dashboard reflects the true state.
    """
    await assert_brand_owned(db, user, brand_id)
    accounts = await sync_social_accounts(brand_id, db)
    return OkResponse(data=accounts)


@router.get("/callback")
async def oauth_callback(
    state: str = Query(default=""),
    access_token: str = Query(default=""),
    account_name: str = Query(default=""),
):
    """
    Deprecated — kept as no-op redirect for backwards compatibility.

    Upload-Post.com now handles OAuth flow end-to-end and redirects directly to
    our `redirect_url` (configured in generate-jwt). This endpoint is no longer
    in the happy path but exists to prevent 404s from any stale links.
    """
    return RedirectResponse(url=f"{FRONTEND_SETTINGS_URL}", status_code=302)
