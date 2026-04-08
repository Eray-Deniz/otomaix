"""fal.ai integration — async image generation with webhook callback."""

import fal_client

from app.core.config import settings

WEBHOOK_URL = "https://api.otomaix.com/webhooks/fal"
DEFAULT_MODEL = "fal-ai/flux/schnell"


def _build_prompt(prompt: str, brand_kit: dict) -> str:
    colors = brand_kit.get("colors", [])
    style = brand_kit.get("style", "")
    parts = [prompt]
    if colors:
        parts.append(f"Brand colors: {', '.join(colors)}.")
    if style:
        parts.append(f"Visual style: {style}.")
    return " ".join(parts)


async def generate_image(prompt: str, aspect_ratio: str, brand_kit: dict) -> str:
    """Submit an image generation job to fal.ai. Returns the fal job ID immediately."""
    import os

    os.environ["FAL_KEY"] = settings.FAL_KEY

    full_prompt = _build_prompt(prompt, brand_kit)

    # Map aspect_ratio to width/height
    size_map = {
        "1:1": "square",
        "9:16": "portrait_9_16",
        "4:5": "portrait_4_5",
        "2:3": "portrait_2_3",
        "16:9": "landscape_16_9",
    }
    image_size = size_map.get(aspect_ratio, "square")

    handler = await fal_client.submit_async(
        DEFAULT_MODEL,
        arguments={"prompt": full_prompt, "image_size": image_size},
        webhook_url=WEBHOOK_URL,
    )
    return handler.request_id
