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
    get_active_image_edit_adapter,
    get_active_image_to_video_adapter,
    get_active_video_adapter,
)

WEBHOOK_URL = "https://api.otomaix.com/webhooks/fal"

# Aktif adapter'lar — modül import'unda bir kez çözülür (env değiştiğinde
# process restart gerekir; Coolify zaten redeploy'da bunu yapar).
_image_adapter = get_active_image_adapter()
_video_adapter = get_active_video_adapter()
_image_to_video_adapter = get_active_image_to_video_adapter()
_image_edit_adapter = get_active_image_edit_adapter()

# Backward-compat module-level exports (posts.py, trends.py, internal.py için)
IMAGE_MODEL: str = _image_adapter.model_id
SUPPORTED_ASPECT_RATIOS: tuple[str, ...] = tuple(sorted(_image_adapter.supported_ratios))
VIDEO_MODEL: str = _video_adapter.model_id
IMAGE_TO_VIDEO_MODEL: str = _image_to_video_adapter.model_id
IMAGE_EDIT_MODEL: str = _image_edit_adapter.model_id


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

    NOT: UI caller sonraki faz'da eklenecek (text-to-video wizard entegrasyonu planlı).
    Adapter altyapısı önceden hazırlanıyor; silme — ileriki video özelliği için şart.
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
    """Image-to-video üretimi — aktif ImageToVideoModelAdapter üzerinden. fal job ID'sini döndürür.

    NOT: UI caller sonraki faz'da eklenecek (image-to-video wizard entegrasyonu planlı).
    Adapter altyapısı önceden hazırlanıyor; silme — ileriki video özelliği için şart.
    """
    _setup_fal()
    full_prompt = _build_image_prompt(prompt, brand_kit)
    args = _image_to_video_adapter.build_args(full_prompt, image_url)

    handler = await fal_client.submit_async(
        _image_to_video_adapter.model_id,
        arguments=args,
        webhook_url=WEBHOOK_URL,
    )
    return handler.request_id


async def generate_image_edit(prompt: str, image_urls: list[str], brand_kit: dict) -> str:
    """Image-edit üretimi — aktif ImageEditModelAdapter üzerinden. fal job ID'sini döndürür.

    NOT: UI caller Sprint 6 (urun-hizmet-sablon) + Sprint 9 (/icerik-olustur ürün mod)
    tarafından entegre edilecek. Adapter altyapısı Sprint 5'te hazırlanır.
    """
    _setup_fal()
    full_prompt = _build_image_prompt(prompt, brand_kit)
    args = _image_edit_adapter.build_args(full_prompt, image_urls)

    handler = await fal_client.submit_async(
        _image_edit_adapter.model_id,
        arguments=args,
        webhook_url=WEBHOOK_URL,
    )
    return handler.request_id
