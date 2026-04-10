"""Social account OAuth link generation and callback handling."""

from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import OkResponse
from app.services.upload_post import get_oauth_link

router = APIRouter(prefix="/social", tags=["social"])

FRONTEND_SETTINGS_URL = "https://app.otomaix.com/marka-ayarlari"
# tab=sosyal matches the TabsTrigger value in the frontend settings page


@router.get("/oauth-link", response_model=OkResponse)
async def oauth_link(
    brand_id: UUID,
    platform: str,
    user: dict = Depends(get_current_user),
):
    """Return a JWT-authenticated OAuth link for connecting a social platform account."""
    url = get_oauth_link(brand_id, platform)
    return OkResponse(data={"url": url, "platform": platform})


@router.get("/callback")
async def oauth_callback(
    state: str = Query(..., description="HS256 JWT encoding brand_id + platform"),
    access_token: str = Query(..., description="OAuth access token from Upload-Post"),
    account_name: str = Query(default="", description="Connected account username (optional)"),
    db: asyncpg.Connection = Depends(get_db),
):
    """
    OAuth callback — called by Upload-Post.com after user grants access.

    Upload-Post redirects here with:
      ?state=<JWT>&access_token=<token>&account_name=<handle>

    Steps:
    1. Decode + verify the state JWT (CSRF protection)
    2. Upsert into brand_social_accounts with the new token
    3. Redirect browser to frontend settings page (Tab: Sosyal Hesaplar)
    """
    from jose import JWTError, jwt

    # 1. Decode state to recover brand_id + platform
    try:
        payload = jwt.decode(state, settings.UPLOAD_POST_API_KEY, algorithms=["HS256"])
    except JWTError:
        return RedirectResponse(
            url=f"{FRONTEND_SETTINGS_URL}?tab=sosyal&error=invalid_state",
            status_code=302,
        )

    brand_id: str = payload.get("brand_id", "")
    platform: str = payload.get("platform", "")

    if not brand_id or not platform:
        return RedirectResponse(
            url=f"{FRONTEND_SETTINGS_URL}?tab=sosyal&error=missing_params",
            status_code=302,
        )

    # 2. Upsert into brand_social_accounts
    await db.execute(
        """
        INSERT INTO social.brand_social_accounts
            (brand_id, platform, account_name, upload_post_token, is_active, connected_at)
        VALUES ($1, $2, $3, $4, true, now())
        ON CONFLICT (brand_id, platform) DO UPDATE SET
            upload_post_token = EXCLUDED.upload_post_token,
            account_name      = EXCLUDED.account_name,
            is_active         = true,
            connected_at      = now()
        """,
        brand_id,
        platform,
        account_name or platform,
        access_token,
    )

    # 3. Redirect back to frontend settings (sosyal hesaplar tab)
    return RedirectResponse(
        url=f"{FRONTEND_SETTINGS_URL}?tab=sosyal&connected={platform}",
        status_code=302,
    )
