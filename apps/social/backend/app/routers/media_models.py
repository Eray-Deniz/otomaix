"""Phase 7 Sprint 7 — GET /media-models/active endpoint'i.

Aktif fal.ai model registry bilgisi — 4 modalite (image / video /
image_to_video / short_video_background) için model_id + supported_ratios.
Frontend aspect selector'ı bu endpoint'ten dinamik populate edilir.

Public endpoint (JWT gerekmez) — registry bilgisi hassas değil. 1 saat
HTTP cache. Env değiştiğinde process restart gerekir (adapter'lar
modül import'unda resolve edilir).
"""
from fastapi import APIRouter, Response

from app.core.config import settings
from app.models.schemas import OkResponse
from app.services.media_adapters import (
    get_active_image_adapter,
    get_active_image_edit_adapter,
    get_active_image_to_video_adapter,
    get_active_short_video_background_adapter,
    get_active_video_adapter,
)

router = APIRouter(prefix="/media-models", tags=["media-models"])


@router.get("/active", response_model=OkResponse)
async def get_active_media_models(response: Response):
    """Aktif model registry — 4 modalite için model_id + supported_ratios.

    `image_to_video.supported_ratios` daima None — çıktı oranı input
    image'den türer, aspect_ratio parametresi yok.
    """
    response.headers["Cache-Control"] = "public, max-age=3600"

    image = get_active_image_adapter()
    video = get_active_video_adapter()
    i2v = get_active_image_to_video_adapter()
    short_bg = get_active_short_video_background_adapter()
    image_edit = get_active_image_edit_adapter()

    short_bg_payload = {
        "key": settings.SHORT_VIDEO_BACKGROUND_MODEL,
        "model_id": short_bg.model_id,
        "supported_ratios": sorted(short_bg.supported_ratios),
    }

    return OkResponse(
        data={
            "image": {
                "key": settings.IMAGE_MODEL,
                "model_id": image.model_id,
                "supported_ratios": sorted(image.supported_ratios),
            },
            "video": {
                "key": settings.VIDEO_MODEL,
                "model_id": video.model_id,
                "supported_ratios": sorted(video.supported_ratios),
            },
            "image_to_video": {
                "key": settings.IMAGE_TO_VIDEO_MODEL,
                "model_id": i2v.model_id,
                "supported_ratios": None,
            },
            "short_video_background": short_bg_payload,
            "image_edit": {
                "key": settings.IMAGE_EDIT_MODEL,
                "model_id": image_edit.model_id,
                "supported_ratios": None,
            },
        }
    )
