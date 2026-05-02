"""Webhook endpoints — currently fal.ai generation callbacks."""

import json
import logging

import sentry_sdk
from fastapi import APIRouter, Depends, Request

import asyncpg
from app.core.database import get_db
from app.models.schemas import OkResponse
from app.core.templates_data import get_template_by_id
from app.services.media_processor import apply_brand_processing, detect_optimal_text_position
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

    # fal.ai error payload detection
    error_detail = None
    if isinstance(payload, dict):
        error_detail = payload.get("detail") or payload.get("error")

    # Image modelleri: payload.images[0].url
    # Video modelleri: payload.video.url
    images = payload.get("images", []) if isinstance(payload, dict) else []
    video_data = payload.get("video", {}) if isinstance(payload, dict) else {}

    image_url: str = ""
    video_url: str = ""
    if images and isinstance(images[0], dict):
        image_url = images[0].get("url", "")
    if isinstance(video_data, dict):
        video_url = video_data.get("url", "")

    media_url = image_url or video_url
    is_video_payload = bool(video_url) and not bool(image_url)

    if not media_url and not error_detail:
        error_detail = "no media url in payload"
    is_error = status_field == "ERROR" or bool(error_detail) or not media_url

    post = await db.fetchrow("SELECT * FROM social.posts WHERE fal_job_id = $1", request_id)

    is_carousel_slide = False
    if not post:
        post = await db.fetchrow(
            """
            SELECT * FROM social.posts
            WHERE content_type = 'carousel' AND status = 'generating'
              AND EXISTS (
                SELECT 1 FROM jsonb_array_elements(slides) AS s
                WHERE s->>'fal_job_id' = $1
              )
            """,
            request_id,
        )
        if post:
            is_carousel_slide = True

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

    if is_carousel_slide:
        return await _handle_carousel_slide(post, request_id, media_url, db)

    post_id = post["id"]
    brand_id = post["brand_id"]
    content_type = post["content_type"] or "image"

    if is_video_payload:
        ext = "mp4"
        mime = "video/mp4"
    else:
        ext = "jpg"
        mime = "image/jpeg"
    dest_path = f"brands/{brand_id}/posts/generated/{post_id}.{ext}"

    try:
        # R2'ye indir
        raw_url = await r2.download_and_upload(media_url, dest_path, mime)

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

        # Phase 8 Sprint 1 Part 3 — Template-spesifik görsel üzeri metin overlay.
        # Post'un template'ında imageTextOverlay tanımlıysa seçili field'ları görselin
        # üzerine yazı olarak render et. post.image_text_fields NULL ise template
        # default'u (template.imageTextOverlay.fields) kullanılır; boş liste ise hiç
        # overlay basılmaz; dolu liste ise yalnızca listedeki field'lar basılır.
        text_overlay_lines: list[str] | None = None
        text_overlay_position = "bottom-left"
        template_id = post.get("template_id") if isinstance(post, dict) else post["template_id"]
        if template_id:
            template = get_template_by_id(template_id)
            if template and template.imageTextOverlay:
                spec = template.imageTextOverlay
                override = post["image_text_fields"]
                effective_fields = override if override is not None else spec.fields
                if effective_fields:
                    raw_fields = post["template_fields"]
                    if raw_fields and isinstance(raw_fields, str):
                        try:
                            raw_fields = json.loads(raw_fields)
                        except (TypeError, ValueError):
                            raw_fields = {}
                    fields_map = dict(raw_fields) if raw_fields else {}

                    suffix_map = {ff.id: (ff.suffix or "") for ff in template.formFields}
                    lines: list[str] = []
                    for fid in effective_fields:
                        val = fields_map.get(fid)
                        if val in (None, ""):
                            continue
                        val_str = str(val).strip()
                        if not val_str:
                            continue
                        suffix = suffix_map.get(fid, "")
                        line = f"{val_str} {suffix}".strip() if suffix else val_str
                        lines.append(line)
                    if lines:
                        text_overlay_lines = lines
                        text_overlay_position = await detect_optimal_text_position(raw_url)

        # Faceless video: TTS audio'yu FFmpeg ile mux et (loop + ses değiştirme)
        audio_url: str | None = None
        subtitle_enabled = False
        if is_video_payload and content_type == "video":
            from app.core.config import settings as _settings
            audio_url = f"{_settings.R2_PUBLIC_URL}/brands/{brand_id}/posts/audio/{post_id}.mp3"

            # subtitle_enabled: template_fields JSONB'den oku
            t_fields = post["template_fields"]
            if t_fields and isinstance(t_fields, str):
                try:
                    t_fields = json.loads(t_fields)
                except (TypeError, ValueError):
                    t_fields = {}
            if isinstance(t_fields, dict):
                subtitle_enabled = bool(t_fields.get("subtitle_enabled", False))

        # Marka işlemlerini uygula (logo overlay / text overlay / audio mux / subtitle / intro video)
        final_url = await apply_brand_processing(
            post_id=post_id,
            brand_id=brand_id,
            output_url=raw_url,
            content_type=content_type,
            brand_kit=brand_kit,
            logo_light_url=logo_light_url,
            logo_dark_url=logo_dark_url,
            intro_video_url=intro_video_url,
            text_overlay_lines=text_overlay_lines,
            text_overlay_position=text_overlay_position,
            audio_url=audio_url,
            subtitle_enabled=subtitle_enabled,
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


async def _handle_carousel_slide(
    post: asyncpg.Record,
    request_id: str,
    image_url: str,
    db: asyncpg.Connection,
) -> OkResponse:
    """Process a single carousel slide fal.ai callback."""
    post_id = post["id"]
    brand_id = post["brand_id"]

    slides = post["slides"] or []
    if isinstance(slides, str):
        slides = json.loads(slides)

    slide_index = next(
        (i for i, s in enumerate(slides) if s.get("fal_job_id") == request_id),
        None,
    )
    if slide_index is None:
        return OkResponse(data={"skipped": True, "reason": "slide fal_job_id mismatch"})

    slide = slides[slide_index]
    slide_order = slide.get("order", slide_index + 1)
    total_slides = len(slides)
    is_first = slide_order == 1
    is_last = slide_order == total_slides

    dest_path = f"brands/{brand_id}/posts/generated/{post_id}_slide_{slide_order}.jpg"

    try:
        raw_url = await r2.download_and_upload(image_url, dest_path, "image/jpeg")

        brand = await db.fetchrow(
            "SELECT brand_kit, logo_light_url, logo_dark_url FROM social.brands WHERE id = $1",
            brand_id,
        )
        raw_kit = brand["brand_kit"] if brand else None
        if raw_kit and isinstance(raw_kit, str):
            raw_kit = json.loads(raw_kit)
        brand_kit = dict(raw_kit) if raw_kit else {}
        logo_light_url = brand["logo_light_url"] if brand else None
        logo_dark_url = brand["logo_dark_url"] if brand else None

        post_use_logo = post["use_logo_overlay"]
        if post_use_logo is not None:
            existing_overlay = brand_kit.get("logo_overlay") or {}
            brand_kit["logo_overlay"] = {**existing_overlay, "enabled": bool(post_use_logo)}

        text_overlay_lines: list[str] | None = None
        text_overlay_position = "bottom-left"
        if is_first or is_last:
            template_id = post.get("template_id") if isinstance(post, dict) else post["template_id"]
            if template_id:
                template = get_template_by_id(template_id)
                if template and template.imageTextOverlay:
                    spec = template.imageTextOverlay
                    override = post["image_text_fields"]
                    effective_fields = override if override is not None else spec.fields
                    if effective_fields:
                        # Carousel: ilk slide ilk field, son slide ikinci field
                        if len(effective_fields) >= 2:
                            if is_first and not is_last:
                                effective_fields = effective_fields[:1]
                            elif is_last and not is_first:
                                effective_fields = effective_fields[1:2]
                        raw_fields = post["template_fields"]
                        if raw_fields and isinstance(raw_fields, str):
                            try:
                                raw_fields = json.loads(raw_fields)
                            except (TypeError, ValueError):
                                raw_fields = {}
                        fields_map = dict(raw_fields) if raw_fields else {}
                        suffix_map = {ff.id: (ff.suffix or "") for ff in template.formFields}
                        lines: list[str] = []
                        for fid in effective_fields:
                            val = fields_map.get(fid)
                            if val in (None, ""):
                                continue
                            val_str = str(val).strip()
                            if not val_str:
                                continue
                            suffix = suffix_map.get(fid, "")
                            line = f"{val_str} {suffix}".strip() if suffix else val_str
                            lines.append(line)
                        if lines:
                            text_overlay_lines = lines
                            text_overlay_position = await detect_optimal_text_position(raw_url)

        final_url = await apply_brand_processing(
            post_id=post_id,
            brand_id=brand_id,
            output_url=raw_url,
            content_type="image",
            brand_kit=brand_kit,
            logo_light_url=logo_light_url,
            logo_dark_url=logo_dark_url,
            intro_video_url=None,
            text_overlay_lines=text_overlay_lines,
            text_overlay_position=text_overlay_position,
            slide_order=slide_order,
        )
    except Exception as exc:
        sentry_sdk.set_context("fal_webhook_carousel", {
            "post_id": str(post_id),
            "brand_id": str(brand_id),
            "slide_order": slide_order,
            "request_id": request_id,
        })
        sentry_sdk.capture_exception(exc)
        await db.execute(
            "UPDATE social.posts SET status = 'failed', updated_at = now() WHERE id = $1",
            post_id,
        )
        return OkResponse(data={"post_id": str(post_id), "slide_order": slide_order, "error": str(exc)})

    async with db.transaction():
        locked = await db.fetchrow(
            "SELECT slides FROM social.posts WHERE id = $1 FOR UPDATE",
            post_id,
        )
        current_slides = locked["slides"] or []
        if isinstance(current_slides, str):
            current_slides = json.loads(current_slides)

        current_slides[slide_index]["image_url"] = final_url

        all_done = all(s.get("image_url") for s in current_slides)

        if all_done:
            first_url = current_slides[0]["image_url"]
            await db.execute(
                "UPDATE social.posts SET slides = $2, status = 'ready', output_url = $3, updated_at = now() WHERE id = $1",
                post_id,
                current_slides,
                first_url,
            )
        else:
            await db.execute(
                "UPDATE social.posts SET slides = $2, updated_at = now() WHERE id = $1",
                post_id,
                current_slides,
            )

    completed = sum(1 for s in current_slides if s.get("image_url"))
    logger.info(
        "Carousel slide %d/%d processed for post %s (all_done=%s)",
        slide_order, total_slides, post_id, all_done,
    )

    return OkResponse(data={
        "post_id": str(post_id),
        "slide_order": slide_order,
        "completed": completed,
        "total": total_slides,
        "all_done": all_done,
    })
