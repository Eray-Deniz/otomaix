"""Webhook endpoints — currently fal.ai generation callbacks."""

import json
import logging

import sentry_sdk
from fastapi import APIRouter, Depends, Request

import asyncpg
from app.core.database import get_db
from app.models.schemas import OkResponse
from app.services.media_processor import apply_brand_processing
from app.services.storage import r2

logger = logging.getLogger(__name__)

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
        reason_short = (str(error_detail)[:200] if error_detail else "no images in payload")
        try:
            raw_payload_str = json.dumps(payload, ensure_ascii=False)[:8000]
        except (TypeError, ValueError):
            raw_payload_str = str(payload)[:8000]

        await db.execute(
            "UPDATE social.posts SET status = 'failed', updated_at = now() WHERE id = $1",
            post["id"],
        )
        logger.error(
            "fal.ai error for post %s (request_id=%s, status=%s): %s",
            post["id"], request_id, status_field, raw_payload_str,
        )
        sentry_sdk.set_context(
            "fal_webhook_error",
            {
                "post_id": str(post["id"]),
                "brand_id": str(post["brand_id"]),
                "request_id": request_id,
                "status": status_field,
                "reason_short": reason_short,
                "error_detail": error_detail,
                "raw_payload": raw_payload_str,
            },
        )
        sentry_sdk.capture_message(
            f"fal.ai generation failed: {reason_short}",
            level="error",
        )
        return OkResponse(data={"post_id": str(post["id"]), "status": "failed", "reason": reason_short})

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
            "SELECT brand_kit, logo_light_url, logo_dark_url, intro_video_url FROM social.brands WHERE id = $1",
            brand_id,
        )
        raw_kit = brand["brand_kit"] if brand else None
        if raw_kit and isinstance(raw_kit, str):
            import json as _json
            raw_kit = _json.loads(raw_kit)
        brand_kit = dict(raw_kit) if raw_kit else {}
        logo_light_url = brand["logo_light_url"] if brand else None
        logo_dark_url = brand["logo_dark_url"] if brand else None
        intro_video_url = brand["intro_video_url"] if brand else None

        # Phase 8 Sprint 1 — Per-post logo overlay override.
        # post.use_logo_overlay NULL ise brand_kit defaultu kullanılır;
        # true/false ise brand_kit.logo_overlay.enabled override edilir.
        # Kopya üzerinde çalışıyoruz — orijinal brand_kit dict mutate edilmez.
        post_use_logo = post["use_logo_overlay"]
        if post_use_logo is not None:
            existing_overlay = brand_kit.get("logo_overlay") or {}
            brand_kit["logo_overlay"] = {**existing_overlay, "enabled": bool(post_use_logo)}

        # Marka işlemlerini uygula (logo overlay / intro video)
        final_url = await apply_brand_processing(
            post_id=post_id,
            brand_id=brand_id,
            output_url=raw_url,
            content_type=content_type,
            brand_kit=brand_kit,
            logo_light_url=logo_light_url,
            logo_dark_url=logo_dark_url,
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
