"""Phase 7 Sprint 7 — GET /media-models/active endpoint'i.

Aktif fal.ai model registry bilgisi — 4 modalite (image / video /
image_to_video / faceless_background) için model_id + supported_ratios.
Frontend aspect selector'ı bu endpoint'ten dinamik populate edilir.

Public endpoint (JWT gerekmez) — registry bilgisi hassas değil. 1 saat
HTTP cache. Env değiştiğinde process restart gerekir (adapter'lar
modül import'unda resolve edilir).
"""
from fastapi import APIRouter, Response

from app.core.config import settings
from app.models.schemas import OkResponse
from app.services.media_adapters import (
    get_active_faceless_background_adapter,
    get_active_image_adapter,
    get_active_image_to_video_adapter,
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
    faceless = get_active_faceless_background_adapter()

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
            "faceless_background": {
                "key": settings.FACELESS_BACKGROUND_MODEL,
                "model_id": faceless.model_id,
                "supported_ratios": sorted(faceless.supported_ratios),
            },
        }
    )
