"""Social account OAuth link generation."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.schemas import OkResponse
from app.services.upload_post import get_oauth_link

router = APIRouter(prefix="/social", tags=["social"])


@router.get("/oauth-link", response_model=OkResponse)
async def oauth_link(
    brand_id: UUID,
    platform: str,
    user: dict = Depends(get_current_user),
):
    """Return a JWT-authenticated OAuth link for connecting a social platform account."""
    url = get_oauth_link(brand_id, platform)
    return OkResponse(data={"url": url, "platform": platform})
