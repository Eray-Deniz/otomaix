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
    status_field: str = (body.get("status") or "").upper()
    payload = body.get("payload") or {}
    images = payload.get("images", []) if isinstance(payload, dict) else []

    # fal.ai error payload detection — validation errors, model failures,
    # rate-limits all arrive via webhook with status=ERROR or detail/error fields
    # in the payload. Without explicit handling the post would hang in 'generating'.
    error_detail = None
    if isinstance(payload, dict):
        error_detail = payload.get("detail") or payload.get("error")
    is_error = status_field == "ERROR" or bool(error_detail) or not images

    image_url: str = ""
    if images and isinstance(images[0], dict):
        image_url = images[0].get("url", "")
    if not is_error and not image_url:
        is_error = True
        error_detail = "empty image url"

    post = await db.fetchrow("SELECT * FROM social.posts WHERE fal_job_id = $1", request_id)
    if not post:
        sentry_sdk.set_context(
            "fal_webhook",
            {"request_id": request_id, "status": status_field, "is_error": is_error},
        )
        sentry_sdk.capture_message(
            f"fal.ai webhook for unknown post: {request_id}",
            level="warning",
        )
        return OkResponse(data={"skipped": True, "reason": "post not found for request_id"})

    if is_error:
        reason = str(error_detail)[:500] if error_detail else "no images in payload"
        await db.execute(
            "UPDATE social.posts SET status = 'failed', updated_at = now() WHERE id = $1",
            post["id"],
        )
        sentry_sdk.set_context(
            "fal_webhook_error",
            {
                "post_id": str(post["id"]),
                "brand_id": str(post["brand_id"]),
                "request_id": request_id,
                "status": status_field,
                "reason": reason[:200],
            },
        )
        sentry_sdk.capture_message(
            f"fal.ai generation failed: {reason[:200]}",
            level="error",
        )
        return OkResponse(data={"post_id": str(post["id"]), "status": "failed", "reason": reason[:200]})

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
        raw_kit = brand["brand_kit"] if brand else None
        if raw_kit and isinstance(raw_kit, str):
            import json as _json
            raw_kit = _json.loads(raw_kit)
        brand_kit = dict(raw_kit) if raw_kit else {}
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
        "UPDATE social.posts SET status = 'ready', output_url = $1, updated_at = now() WHERE id = $2",
        final_url,
        post_id,
    )

    return OkResponse(data={"post_id": str(post_id), "output_url": final_url})
