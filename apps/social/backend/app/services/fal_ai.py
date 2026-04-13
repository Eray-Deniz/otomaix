"""fal.ai integration — async image/video generation with webhook callback."""

import fal_client

from app.core.config import settings

WEBHOOK_URL = "https://api.otomaix.com/webhooks/fal"

# Model seçimleri
IMAGE_MODEL = "fal-ai/flux-2-pro"                              # FLUX.2 [pro] — görsel üretimi
VIDEO_MODEL = "fal-ai/kling-video/v3/pro/text-to-video"        # Kling 3.0 Pro — text-to-video
IMAGE_TO_VIDEO_MODEL = "fal-ai/kling-video/v2.5-turbo/pro/image-to-video"  # Kling 2.5 Turbo — image-to-video


def _build_image_prompt(prompt: str, brand_kit: dict) -> str:
    colors = brand_kit.get("colors", [])
    style = brand_kit.get("style", "")
    parts = [prompt]
    if colors:
        parts.append(f"Brand colors: {', '.join(colors)}.")
    if style:
        parts.append(f"Visual style: {style}.")
    return " ".join(parts)


def _setup_fal():
    import os
    os.environ["FAL_KEY"] = settings.FAL_KEY


# Aspect ratio → fal.ai image_size mapping
_SIZE_MAP = {
    "1:1": "square",
    "9:16": "portrait_9_16",
    "4:5": "portrait_4_5",
    "2:3": "portrait_2_3",
    "16:9": "landscape_16_9",
}


async def generate_image(prompt: str, aspect_ratio: str, brand_kit: dict) -> str:
    """Görsel üretimi — FLUX.2 [pro]. fal job ID'sini döndürür."""
    _setup_fal()
    full_prompt = _build_image_prompt(prompt, brand_kit)
    image_size = _SIZE_MAP.get(aspect_ratio, "square")

    handler = await fal_client.submit_async(
        IMAGE_MODEL,
        arguments={"prompt": full_prompt, "image_size": image_size},
        webhook_url=WEBHOOK_URL,
    )
    return handler.request_id


async def generate_video(prompt: str, aspect_ratio: str, brand_kit: dict) -> str:
    """Text-to-video üretimi — Kling 3.0 Pro. fal job ID'sini döndürür."""
    _setup_fal()
    full_prompt = _build_image_prompt(prompt, brand_kit)

    # Kling aspect ratio mapping
    aspect = "9:16" if aspect_ratio == "9:16" else "16:9" if aspect_ratio == "16:9" else "1:1"

    handler = await fal_client.submit_async(
        VIDEO_MODEL,
        arguments={"prompt": full_prompt, "aspect_ratio": aspect},
        webhook_url=WEBHOOK_URL,
    )
    return handler.request_id


async def generate_video_from_image(prompt: str, image_url: str, brand_kit: dict) -> str:
    """Image-to-video üretimi — Kling 2.5 Turbo Pro. fal job ID'sini döndürür."""
    _setup_fal()
    full_prompt = _build_image_prompt(prompt, brand_kit)

    handler = await fal_client.submit_async(
        IMAGE_TO_VIDEO_MODEL,
        arguments={"prompt": full_prompt, "image_url": image_url},
        webhook_url=WEBHOOK_URL,
    )
    return handler.request_id
