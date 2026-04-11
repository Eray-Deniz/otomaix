"""Webhook endpoints — currently fal.ai generation callbacks."""

import sentry_sdk
from fastapi import APIRouter, Depends, Request

import asyncpg
from app.core.database import get_db
from app.models.schemas import OkResponse
from app.services.media_processor import apply_brand_processing
from app.services.storage import r2

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/fal", response_model=OkResponse)
async def fal_webhook(request: Request, db: asyncpg.Connection = Depends(get_db)):
    """
    Receive fal.ai generation-complete callback.
    1. Downloads the generated file from fal's temp URL and copies it to R2.
    2. Applies brand processing: logo overlay (images) or intro video (videos).
    3. Updates the post record with the final URL.
    """
    body = await request.json()

    request_id: str = body.get("request_id", "")
    payload = body.get("payload", {})
    images = payload.get("images", [])

    if not images:
        return OkResponse(data={"skipped": True, "reason": "no images in payload"})

    image_url: str = images[0].get("url", "")
    if not image_url:
        return OkResponse(data={"skipped": True, "reason": "empty image url"})

    # Find the post by fal_job_id
    post = await db.fetchrow("SELECT * FROM social.posts WHERE fal_job_id = $1", request_id)
    if not post:
        return OkResponse(data={"skipped": True, "reason": "post not found for request_id"})

    post_id = post["id"]
    brand_id = post["brand_id"]
    content_type = post["content_type"] or "image"
    ext = "jpg"
    dest_path = f"brands/{brand_id}/posts/generated/{post_id}.{ext}"

    try:
        # R2'ye indir
        raw_url = await r2.download_and_upload(image_url, dest_path, "image/jpeg")

        # Marka bilgilerini çek (brand_kit, logo, intro_video)
        brand = await db.fetchrow(
            "SELECT brand_kit, logo_light_url, intro_video_url FROM social.brands WHERE id = $1",
            brand_id,
        )
        brand_kit = dict(brand["brand_kit"]) if brand and brand["brand_kit"] else {}
        logo_url = brand["logo_light_url"] if brand else None
        intro_video_url = brand["intro_video_url"] if brand else None

        # Marka işlemlerini uygula (logo overlay / intro video)
        final_url = await apply_brand_processing(
            post_id=post_id,
            brand_id=brand_id,
            output_url=raw_url,
            content_type=content_type,
            brand_kit=brand_kit,
            logo_url=logo_url,
            intro_video_url=intro_video_url,
        )
    except Exception as exc:
        sentry_sdk.set_context("fal_webhook", {"post_id": str(post_id), "brand_id": str(brand_id), "request_id": request_id})
        sentry_sdk.capture_exception(exc)
        await db.execute(
            "UPDATE social.posts SET status = 'failed', updated_at = now() WHERE id = $1",
            post_id,
        )
        return OkResponse(data={"post_id": str(post_id), "error": str(exc)})

    await db.execute(
        "UPDATE social.posts SET status = 'generated', output_url = $1, updated_at = now() WHERE id = $2",
        final_url,
        post_id,
    )

    return OkResponse(data={"post_id": str(post_id), "output_url": final_url})
