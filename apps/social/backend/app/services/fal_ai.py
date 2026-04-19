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


# Aspect ratio → FLUX.2 Pro image_size mapping.
# FLUX.2 Pro preset literal'leri: square_hd, square, portrait_4_3, portrait_16_9,
# landscape_4_3, landscape_16_9. Preset'te olmayan oranlar için `{width, height}`
# dict formatı kullanılır (FLUX.2 Pro image_size Union[ImageSize, Literal] kabul eder).
_SIZE_MAP: dict[str, object] = {
    "1:1":  "square_hd",
    "9:16": "portrait_16_9",               # FLUX naming: 9:16 display oranı
    "4:5":  {"width": 1024, "height": 1280},
    "2:3":  {"width": 1024, "height": 1536},
    "16:9": "landscape_16_9",
    "4:3":  "landscape_4_3",
    "3:4":  "portrait_4_3",
}

SUPPORTED_ASPECT_RATIOS: tuple[str, ...] = tuple(_SIZE_MAP.keys())


def resolve_image_size(aspect_ratio: str) -> object:
    """Return fal.ai image_size value for aspect ratio, or raise ValueError."""
    if aspect_ratio not in _SIZE_MAP:
        raise ValueError(
            f"Unsupported aspect_ratio: {aspect_ratio!r}. "
            f"Supported: {', '.join(SUPPORTED_ASPECT_RATIOS)}"
        )
    return _SIZE_MAP[aspect_ratio]


async def generate_image(prompt: str, aspect_ratio: str, brand_kit: dict) -> str:
    """Görsel üretimi — FLUX.2 [pro]. fal job ID'sini döndürür."""
    _setup_fal()
    full_prompt = _build_image_prompt(prompt, brand_kit)
    image_size = resolve_image_size(aspect_ratio)

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
