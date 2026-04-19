"""Media model adapters — fal.ai için model-agnostic soyutlama.

4 modalite için ayrı adapter hiyerarşisi:
- ImageModelAdapter        → görsel üretimi
- VideoModelAdapter        → text-to-video
- ImageToVideoModelAdapter → image-to-video
- FacelessBackgroundAdapter → faceless video arka plan üretimi

Aktif model seçimi env var ile yapılır (`settings.IMAGE_MODEL` vb.); default'lar
mevcut production model ID'leridir, davranış değişmeden adapter'lı yol kullanılır.

Yeni model eklemek için: adapter sınıfı yaz → ilgili registry'ye ekle →
env var'ı Coolify'da güncelle → redeploy. Kod değişikliği kalanı için yok.
"""

from __future__ import annotations

from typing import Any, Protocol

from app.core.config import settings


# ─── Image modality ─────────────────────────────────────────────────────────


class ImageModelAdapter(Protocol):
    """Görsel üretim modelleri için soyutlama."""

    model_id: str
    supported_ratios: frozenset[str]

    def build_args(self, prompt: str, aspect_ratio: str) -> dict[str, Any]: ...


class FluxProV2Adapter:
    """FLUX.2 [pro] adapter.

    image_size: preset literal (square_hd, portrait_4_3, ...) veya
    `{width, height}` dict. FLUX.2 Pro her ikisini de kabul eder.
    """

    model_id = "fal-ai/flux-2-pro"

    _SIZE_MAP: dict[str, Any] = {
        "1:1":  "square_hd",
        "9:16": "portrait_16_9",  # FLUX naming: 9:16 display oranı
        "4:5":  {"width": 1024, "height": 1280},
        "2:3":  {"width": 1024, "height": 1536},
        "16:9": "landscape_16_9",
        "4:3":  "landscape_4_3",
        "3:4":  "portrait_4_3",
    }

    supported_ratios = frozenset(_SIZE_MAP.keys())

    def build_args(self, prompt: str, aspect_ratio: str) -> dict[str, Any]:
        if aspect_ratio not in self._SIZE_MAP:
            raise ValueError(
                f"Unsupported aspect_ratio: {aspect_ratio!r}. "
                f"Supported: {', '.join(sorted(self.supported_ratios))}"
            )
        return {"prompt": prompt, "image_size": self._SIZE_MAP[aspect_ratio]}


IMAGE_ADAPTERS: dict[str, ImageModelAdapter] = {
    "flux-2-pro": FluxProV2Adapter(),
}


def get_active_image_adapter() -> ImageModelAdapter:
    key = (settings.IMAGE_MODEL or "flux-2-pro").strip()
    adapter = IMAGE_ADAPTERS.get(key)
    if not adapter:
        raise ValueError(
            f"Unknown IMAGE_MODEL: {key!r}. "
            f"Registered: {sorted(IMAGE_ADAPTERS.keys())}"
        )
    return adapter


# ─── Text-to-Video modality ─────────────────────────────────────────────────


class VideoModelAdapter(Protocol):
    """Text-to-video üretim modelleri için soyutlama."""

    model_id: str
    supported_ratios: frozenset[str]

    def build_args(self, prompt: str, aspect_ratio: str) -> dict[str, Any]: ...


class KlingV3ProAdapter:
    """Kling 3.0 Pro text-to-video adapter.

    aspect_ratio: "9:16" | "16:9" | "1:1" — Kling API'si literal string kabul eder.
    """

    model_id = "fal-ai/kling-video/v3/pro/text-to-video"

    supported_ratios = frozenset({"9:16", "16:9", "1:1"})

    def build_args(self, prompt: str, aspect_ratio: str) -> dict[str, Any]:
        if aspect_ratio not in self.supported_ratios:
            raise ValueError(
                f"Unsupported aspect_ratio for {self.model_id}: {aspect_ratio!r}. "
                f"Supported: {', '.join(sorted(self.supported_ratios))}"
            )
        return {"prompt": prompt, "aspect_ratio": aspect_ratio}


VIDEO_ADAPTERS: dict[str, VideoModelAdapter] = {
    "kling-v3-pro": KlingV3ProAdapter(),
}


def get_active_video_adapter() -> VideoModelAdapter:
    key = (settings.VIDEO_MODEL or "kling-v3-pro").strip()
    adapter = VIDEO_ADAPTERS.get(key)
    if not adapter:
        raise ValueError(
            f"Unknown VIDEO_MODEL: {key!r}. "
            f"Registered: {sorted(VIDEO_ADAPTERS.keys())}"
        )
    return adapter


# ─── Image-to-Video modality ────────────────────────────────────────────────


class ImageToVideoModelAdapter(Protocol):
    """Image-to-video üretim modelleri için soyutlama.

    Text-to-video'dan farklı olarak aspect_ratio yok — çıktı oranı input
    image'den türer. Arayüz: (prompt, image_url) → arguments dict.
    """

    model_id: str

    def build_args(self, prompt: str, image_url: str) -> dict[str, Any]: ...


class KlingV25TurboProAdapter:
    """Kling 2.5 Turbo Pro image-to-video adapter."""

    model_id = "fal-ai/kling-video/v2.5-turbo/pro/image-to-video"

    def build_args(self, prompt: str, image_url: str) -> dict[str, Any]:
        return {"prompt": prompt, "image_url": image_url}


IMAGE_TO_VIDEO_ADAPTERS: dict[str, ImageToVideoModelAdapter] = {
    "kling-v25-turbo-pro": KlingV25TurboProAdapter(),
}


def get_active_image_to_video_adapter() -> ImageToVideoModelAdapter:
    key = (settings.IMAGE_TO_VIDEO_MODEL or "kling-v25-turbo-pro").strip()
    adapter = IMAGE_TO_VIDEO_ADAPTERS.get(key)
    if not adapter:
        raise ValueError(
            f"Unknown IMAGE_TO_VIDEO_MODEL: {key!r}. "
            f"Registered: {sorted(IMAGE_TO_VIDEO_ADAPTERS.keys())}"
        )
    return adapter


# ─── Faceless Video Background modality ─────────────────────────────────────


class FacelessBackgroundAdapter(Protocol):
    """Faceless video arka plan üretim modelleri için soyutlama.

    Imza text-to-video'dan farklı: (prompt, aspect_ratio, duration) → arguments.
    Hunyuan gibi modeller resolution literal bekler (aspect_ratio → "720x1280"
    mapping adapter içinde).
    """

    model_id: str
    supported_ratios: frozenset[str]

    def build_args(self, prompt: str, aspect_ratio: str, duration: int = 5) -> dict[str, Any]: ...


class HunyuanVideoAdapter:
    """Hunyuan Video faceless background adapter.

    video_length şu an hardcoded "5s" (Hunyuan kısa format optimize);
    duration parametresi farklı modeller için esneklik bırakır.
    num_inference_steps=30 — kalite/hız dengesi, model-spesifik.
    """

    model_id = "fal-ai/hunyuan-video"

    _RESOLUTION_MAP: dict[str, str] = {
        "9:16": "720x1280",
        "1:1":  "720x720",
        "16:9": "1280x720",
        "4:5":  "720x900",
    }

    supported_ratios = frozenset(_RESOLUTION_MAP.keys())

    def build_args(self, prompt: str, aspect_ratio: str, duration: int = 5) -> dict[str, Any]:
        if aspect_ratio not in self._RESOLUTION_MAP:
            raise ValueError(
                f"Unsupported aspect_ratio for {self.model_id}: {aspect_ratio!r}. "
                f"Supported: {', '.join(sorted(self.supported_ratios))}"
            )
        return {
            "prompt": prompt,
            "resolution": self._RESOLUTION_MAP[aspect_ratio],
            "video_length": "5s",
            "num_inference_steps": 30,
        }


FACELESS_BACKGROUND_ADAPTERS: dict[str, FacelessBackgroundAdapter] = {
    "hunyuan-video": HunyuanVideoAdapter(),
}


def get_active_faceless_background_adapter() -> FacelessBackgroundAdapter:
    key = (settings.FACELESS_BACKGROUND_MODEL or "hunyuan-video").strip()
    adapter = FACELESS_BACKGROUND_ADAPTERS.get(key)
    if not adapter:
        raise ValueError(
            f"Unknown FACELESS_BACKGROUND_MODEL: {key!r}. "
            f"Registered: {sorted(FACELESS_BACKGROUND_ADAPTERS.keys())}"
        )
    return adapter
