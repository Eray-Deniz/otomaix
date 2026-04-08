from fastapi import APIRouter, Depends

from app.core.security import get_current_user
from app.models.schemas import OkResponse, PresignedUrlRequest
from app.services.storage import r2

router = APIRouter(prefix="/storage", tags=["storage"])


@router.post("/presigned-url", response_model=OkResponse)
async def presigned_url(
    payload: PresignedUrlRequest,
    user: dict = Depends(get_current_user),
):
    """Return a presigned upload URL for direct-to-R2 uploads from the frontend."""
    url = r2.get_presigned_upload_url(payload.path, payload.content_type, payload.expires)
    return OkResponse(data={"url": url, "path": payload.path})
