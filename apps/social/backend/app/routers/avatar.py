"""Avatar endpoints — HeyGen entegrasyonu."""

import json
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.core.cache import get_cached, set_cached
from app.core.database import get_db
from app.core.security import assert_brand_owned, get_current_user
from app.models.schemas import OkResponse
from app.routers.billing import check_plan_limit
from app.services.avatar import (
    create_avatar_from_photo,
    generate_ugc_video,
    get_video_status,
    list_stock_avatars,
    set_stock_avatar,
)
from app.services.storage import r2

router = APIRouter(prefix="/avatar", tags=["avatar"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


# ─── Stok avatarlar ────────────────────────────────────────────────────────

@router.get("/stock", response_model=OkResponse)
async def get_stock_avatars(
    user: dict = Depends(get_current_user),
):
    """HeyGen stok avatar listesini döndür."""
    cache_key = "otomaix:social:avatar:stock"
    cached = await get_cached(cache_key)
    if cached is not None:
        return OkResponse(data=cached)

    avatars = await list_stock_avatars()
    await set_cached(cache_key, avatars, 3600)  # 1 saat
    return OkResponse(data=avatars)


# ─── Fotoğraftan avatar oluşturma ──────────────────────────────────────────

@router.post("/create", response_model=OkResponse, status_code=status.HTTP_201_CREATED)
async def create_avatar(
    brand_id: UUID = Form(...),
    name: str = Form(...),
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Kullanıcı fotoğrafından HeyGen avatar oluştur."""
    await assert_brand_owned(db, user, brand_id)
    await check_plan_limit(user["sub"], "avatar", db)
    from app.core.config import settings as _settings
    if not _settings.HEYGEN_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI Avatar özelliği henüz yapılandırılmamış. HEYGEN_API_KEY gerekli.",
        )

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Sadece JPEG, PNG veya WebP kabul edilir.")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:  # 10 MB
        raise HTTPException(status_code=400, detail="Dosya boyutu 10 MB'ı geçemez.")

    # Fotoğrafı R2'ye yükle → HeyGen'e URL ver
    ext = file.filename.rsplit(".", 1)[-1] if "." in (file.filename or "") else "jpg"
    r2_path = f"brands/{brand_id}/avatar/photo.{ext}"
    photo_url = r2.upload(content, r2_path, file.content_type)

    result = await create_avatar_from_photo(photo_url, name, brand_id, db)
    return OkResponse(data=result)


# ─── Stok avatar seçme ─────────────────────────────────────────────────────

class SelectStockAvatarRequest(BaseModel):
    brand_id: UUID
    avatar_id: str
    avatar_name: str
    preview_url: str


@router.post("/select-stock", response_model=OkResponse)
async def select_stock_avatar(
    payload: SelectStockAvatarRequest,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Seçilen stok avatarı brand_kit'e kaydet."""
    await assert_brand_owned(db, user, payload.brand_id)
    result = await set_stock_avatar(
        payload.avatar_id,
        payload.avatar_name,
        payload.preview_url,
        payload.brand_id,
        db,
    )
    return OkResponse(data=result)


# ─── UGC video üretimi ─────────────────────────────────────────────────────

class GenerateUGCRequest(BaseModel):
    brand_id: UUID
    script: str
    voice_id: str = "tr-TR-EmelNeural"
    aspect_ratio: str = "9:16"


@router.post("/generate-ugc", response_model=OkResponse, status_code=status.HTTP_201_CREATED)
async def generate_ugc(
    payload: GenerateUGCRequest,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Markanın aktif avatarı ile UGC video üret."""
    await assert_brand_owned(db, user, payload.brand_id)
    await check_plan_limit(user["sub"], "avatar", db)
    await check_plan_limit(user["sub"], "post", db)
    from app.core.config import settings as _settings
    if not _settings.HEYGEN_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI Avatar özelliği henüz yapılandırılmamış. HEYGEN_API_KEY gerekli.",
        )

    # Brand'den aktif avatar bilgisini al
    row = await db.fetchrow(
        "SELECT brand_kit FROM social.brands WHERE id = $1", payload.brand_id
    )
    if not row:
        raise HTTPException(status_code=404, detail="Brand bulunamadı")

    brand_kit = dict(row["brand_kit"]) if row["brand_kit"] else {}
    avatar_info = brand_kit.get("avatar")
    if not avatar_info or not avatar_info.get("avatar_id"):
        raise HTTPException(
            status_code=400,
            detail="Bu marka için henüz bir avatar seçilmemiş.",
        )

    result = await generate_ugc_video(
        avatar_id=avatar_info["avatar_id"],
        script=payload.script,
        voice_id=payload.voice_id,
        aspect_ratio=payload.aspect_ratio,
    )

    # Post kaydı oluştur
    post_row = await db.fetchrow(
        """
        INSERT INTO social.posts
            (brand_id, content_type, prompt, user_text, aspect_ratio, status)
        VALUES ($1, 'ugc_video', $2, $3, $4, 'generating')
        RETURNING id
        """,
        payload.brand_id,
        "UGC video — avatar ile",
        payload.script,
        payload.aspect_ratio,
    )

    return OkResponse(data={
        "post_id": str(post_row["id"]),
        "video_id": result["video_id"],
        "status": "processing",
        "message": "Video üretimi başlatıldı. Birkaç dakika içinde hazır olacak.",
    })


@router.get("/video-status/{video_id}", response_model=OkResponse)
async def check_video_status(
    video_id: str,
    user: dict = Depends(get_current_user),
):
    """HeyGen video üretim durumunu sorgula."""
    result = await get_video_status(video_id)
    return OkResponse(data=result)
