"""fal.ai integration — async image/video generation with webhook callback.

Image üretimi artık `media_adapters.ImageModelAdapter` üzerinden yapılır;
model seçimi `settings.IMAGE_MODEL` ile değiştirilebilir. Eski modül-seviyesi
export'lar (SUPPORTED_ASPECT_RATIOS, resolve_image_size, IMAGE_MODEL) mevcut
import site'ları kırmadan aktif adapter'dan türetilir.
"""

import fal_client

from app.core.config import settings
from app.services.media_adapters import (
    get_active_image_adapter,
    get_active_video_adapter,
)

WEBHOOK_URL = "https://api.otomaix.com/webhooks/fal"

# Aktif adapter'lar — modül import'unda bir kez çözülür (env değiştiğinde
# process restart gerekir; Coolify zaten redeploy'da bunu yapar).
_image_adapter = get_active_image_adapter()
_video_adapter = get_active_video_adapter()

# Backward-compat module-level exports (posts.py, trends.py, internal.py için)
IMAGE_MODEL: str = _image_adapter.model_id
SUPPORTED_ASPECT_RATIOS: tuple[str, ...] = tuple(sorted(_image_adapter.supported_ratios))
VIDEO_MODEL: str = _video_adapter.model_id

# Dead-code hazır model ID (henüz adapter'ı yok, Faz 2c'de eklenecek)
IMAGE_TO_VIDEO_MODEL = "fal-ai/kling-video/v2.5-turbo/pro/image-to-video"


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


def resolve_image_size(aspect_ratio: str) -> object:
    """BACKWARD COMPAT — mevcut dış çağrılar için korunur.

    Yeni kod doğrudan `get_active_image_adapter().build_args(...)` kullanmalı.
    """
    return _image_adapter.build_args("", aspect_ratio)["image_size"]


async def generate_image(prompt: str, aspect_ratio: str, brand_kit: dict) -> str:
    """Görsel üretimi — aktif ImageModelAdapter üzerinden. fal job ID'sini döndürür."""
    _setup_fal()
    full_prompt = _build_image_prompt(prompt, brand_kit)
    args = _image_adapter.build_args(full_prompt, aspect_ratio)

    handler = await fal_client.submit_async(
        _image_adapter.model_id,
        arguments=args,
        webhook_url=WEBHOOK_URL,
    )
    return handler.request_id


async def generate_video(prompt: str, aspect_ratio: str, brand_kit: dict) -> str:
    """Text-to-video üretimi — aktif VideoModelAdapter üzerinden. fal job ID'sini döndürür.

    NOT: Şu an hiçbir caller yok (dead code); adapter pattern gelecek caller'lar için hazır.
    """
    _setup_fal()
    full_prompt = _build_image_prompt(prompt, brand_kit)
    args = _video_adapter.build_args(full_prompt, aspect_ratio)

    handler = await fal_client.submit_async(
        _video_adapter.model_id,
        arguments=args,
        webhook_url=WEBHOOK_URL,
    )
    return handler.request_id


async def generate_video_from_image(prompt: str, image_url: str, brand_kit: dict) -> str:
    """Image-to-video üretimi — Kling 2.5 Turbo Pro. fal job ID'sini döndürür.

    NOT: Şu an hiçbir caller yok (dead code); Faz 2c'de ImageToVideoModelAdapter'a taşınacak.
    """
    _setup_fal()
    full_prompt = _build_image_prompt(prompt, brand_kit)

    handler = await fal_client.submit_async(
        IMAGE_TO_VIDEO_MODEL,
        arguments={"prompt": full_prompt, "image_url": image_url},
        webhook_url=WEBHOOK_URL,
    )
    return handler.request_id
