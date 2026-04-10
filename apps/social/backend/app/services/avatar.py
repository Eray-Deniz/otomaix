"""AI Avatar service — HeyGen API entegrasyonu.

İki mod:
  A) Kendi avatarı: kullanıcının fotoğrafından HeyGen photo_avatar oluşturulur
  B) Hazır avatar: HeyGen'in stok avatar kütüphanesinden seçilir

HEYGEN_API_KEY yoksa stok avatarlar için fallback liste döner,
oluşturma işlemleri 503 hatası verir.
"""

import asyncio
from uuid import UUID

import asyncpg
import httpx

from app.core.config import settings

HEYGEN_BASE = "https://api.heygen.com"


def _heygen_headers() -> dict:
    return {
        "X-Api-Key": settings.HEYGEN_API_KEY,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


# ─── Stok avatar listesi ────────────────────────────────────────────────────

# HeyGen API yokken gösterilecek fallback stok avatarlar
FALLBACK_STOCK_AVATARS = [
    {
        "avatar_id": "stock_001",
        "avatar_name": "Elif",
        "gender": "female",
        "preview_url": "",
        "preview_image_url": "",
        "is_stock": True,
    },
    {
        "avatar_id": "stock_002",
        "avatar_name": "Mehmet",
        "gender": "male",
        "preview_url": "",
        "preview_image_url": "",
        "is_stock": True,
    },
    {
        "avatar_id": "stock_003",
        "avatar_name": "Ayşe",
        "gender": "female",
        "preview_url": "",
        "preview_image_url": "",
        "is_stock": True,
    },
    {
        "avatar_id": "stock_004",
        "avatar_name": "Ali",
        "gender": "male",
        "preview_url": "",
        "preview_image_url": "",
        "is_stock": True,
    },
]


async def list_stock_avatars() -> list[dict]:
    """HeyGen stok avatarları çek. API yoksa fallback döner."""
    if not settings.HEYGEN_API_KEY:
        return FALLBACK_STOCK_AVATARS

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{HEYGEN_BASE}/v2/avatars",
                headers=_heygen_headers(),
            )
            if resp.status_code != 200:
                return FALLBACK_STOCK_AVATARS

            data = resp.json()
            avatars = data.get("data", {}).get("avatars", [])
            return [
                {
                    "avatar_id": a.get("avatar_id", ""),
                    "avatar_name": a.get("avatar_name", ""),
                    "gender": a.get("gender", ""),
                    "preview_url": a.get("preview_video_url", ""),
                    "preview_image_url": a.get("preview_image_url", ""),
                    "is_stock": True,
                }
                for a in avatars[:20]  # ilk 20 avatar
            ]
    except Exception:
        return FALLBACK_STOCK_AVATARS


# ─── Fotoğraftan avatar oluşturma ───────────────────────────────────────────

async def create_avatar_from_photo(
    photo_url: str,
    name: str,
    brand_id: UUID,
    db: asyncpg.Connection,
) -> dict:
    """Fotoğraf URL'den HeyGen photo_avatar oluştur, brand_kit'e kaydet.

    Returns: {"avatar_id": "...", "preview_url": "...", "status": "processing"|"ready"}
    """
    if not settings.HEYGEN_API_KEY:
        raise ValueError("HEYGEN_API_KEY yapılandırılmamış")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{HEYGEN_BASE}/v2/photo_avatar",
            headers=_heygen_headers(),
            json={"image_url": photo_url, "name": name},
        )
        if resp.status_code not in (200, 201):
            raise ValueError(f"HeyGen API hatası: {resp.status_code} — {resp.text[:200]}")

        data = resp.json().get("data", {})
        avatar_id = data.get("photo_avatar_id") or data.get("avatar_id", "")
        preview_url = data.get("image_url", photo_url)

    # brand_kit.avatar alanını güncelle
    row = await db.fetchrow("SELECT brand_kit FROM social.brands WHERE id = $1", brand_id)
    if row:
        import json
        existing_kit = dict(row["brand_kit"]) if row["brand_kit"] else {}
        existing_kit["avatar"] = {
            "type": "custom",
            "avatar_id": avatar_id,
            "preview_url": preview_url,
            "name": name,
        }
        await db.execute(
            "UPDATE social.brands SET brand_kit = $2, updated_at = now() WHERE id = $1",
            brand_id,
            json.dumps(existing_kit),
        )

    return {
        "avatar_id": avatar_id,
        "preview_url": preview_url,
        "name": name,
        "status": "processing",
    }


async def set_stock_avatar(
    avatar_id: str,
    avatar_name: str,
    preview_url: str,
    brand_id: UUID,
    db: asyncpg.Connection,
) -> dict:
    """Stok avatar seç ve brand_kit'e kaydet."""
    import json

    row = await db.fetchrow("SELECT brand_kit FROM social.brands WHERE id = $1", brand_id)
    existing_kit = dict(row["brand_kit"]) if row and row["brand_kit"] else {}
    existing_kit["avatar"] = {
        "type": "stock",
        "avatar_id": avatar_id,
        "preview_url": preview_url,
        "name": avatar_name,
    }
    await db.execute(
        "UPDATE social.brands SET brand_kit = $2, updated_at = now() WHERE id = $1",
        brand_id,
        json.dumps(existing_kit),
    )
    return existing_kit["avatar"]


# ─── UGC video üretimi ──────────────────────────────────────────────────────

async def generate_ugc_video(
    avatar_id: str,
    script: str,
    voice_id: str,
    aspect_ratio: str = "9:16",
) -> dict:
    """HeyGen v2 ile avatar + script → video üret.

    Returns: {"video_id": "...", "status": "processing"}
    HeyGen async çalışır; video_id ile durum sorgulanabilir.
    """
    if not settings.HEYGEN_API_KEY:
        raise ValueError("HEYGEN_API_KEY yapılandırılmamış")

    # En-boy oranı → HeyGen dimension
    dimension_map = {
        "9:16": {"width": 720, "height": 1280},
        "1:1": {"width": 720, "height": 720},
        "16:9": {"width": 1280, "height": 720},
        "4:5": {"width": 720, "height": 900},
    }
    dimension = dimension_map.get(aspect_ratio, {"width": 720, "height": 1280})

    payload = {
        "video_inputs": [
            {
                "character": {
                    "type": "avatar",
                    "avatar_id": avatar_id,
                    "avatar_style": "normal",
                },
                "voice": {
                    "type": "text",
                    "input_text": script,
                    "voice_id": voice_id,
                },
            }
        ],
        "dimension": dimension,
        "aspect_ratio": aspect_ratio,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{HEYGEN_BASE}/v2/video/generate",
            headers=_heygen_headers(),
            json=payload,
        )
        if resp.status_code not in (200, 201):
            raise ValueError(f"HeyGen video API hatası: {resp.status_code} — {resp.text[:200]}")

        data = resp.json().get("data", {})
        video_id = data.get("video_id", "")

    return {"video_id": video_id, "status": "processing"}


async def get_video_status(video_id: str) -> dict:
    """HeyGen video durumunu sorgula."""
    if not settings.HEYGEN_API_KEY:
        return {"status": "unknown"}

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(
            f"{HEYGEN_BASE}/v1/video_status.get?video_id={video_id}",
            headers=_heygen_headers(),
        )
        data = resp.json().get("data", {})
        return {
            "video_id": video_id,
            "status": data.get("status", "processing"),
            "video_url": data.get("video_url", ""),
            "thumbnail_url": data.get("thumbnail_url", ""),
        }
