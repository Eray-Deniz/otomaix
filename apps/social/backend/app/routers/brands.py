import json
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import BrandCreate, BrandKitUpdate, BrandOut, BrandUpdate, OkResponse
from app.services.storage import r2

router = APIRouter(prefix="/brands", tags=["brands"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/svg+xml"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm"}


@router.post("", response_model=OkResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(
    payload: BrandCreate,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Create a new brand inside a workspace."""
    row = await db.fetchrow(
        """
        INSERT INTO social.brands (workspace_id, name, description, website_url, sector)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *
        """,
        payload.workspace_id,
        payload.name,
        payload.description,
        payload.website_url,
        payload.sector,
    )
    return OkResponse(data=dict(row))


@router.get("", response_model=OkResponse)
async def list_brands(
    workspace_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """List all brands in a workspace."""
    rows = await db.fetch(
        "SELECT * FROM social.brands WHERE workspace_id = $1 ORDER BY created_at",
        workspace_id,
    )
    return OkResponse(data=[dict(r) for r in rows])


@router.get("/{brand_id}", response_model=OkResponse)
async def get_brand(
    brand_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Get a single brand by id."""
    row = await db.fetchrow("SELECT * FROM social.brands WHERE id = $1", brand_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    return OkResponse(data=dict(row))


@router.patch("/{brand_id}", response_model=OkResponse)
async def update_brand(
    brand_id: UUID,
    payload: BrandUpdate,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Partially update a brand."""
    updates = payload.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    fields = ", ".join(f"{k} = ${i + 2}" for i, k in enumerate(updates))
    values = list(updates.values())
    row = await db.fetchrow(
        f"UPDATE social.brands SET {fields} WHERE id = $1 RETURNING *",
        brand_id,
        *values,
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    return OkResponse(data=dict(row))


@router.delete("/{brand_id}", response_model=OkResponse)
async def delete_brand(
    brand_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Delete a brand."""
    result = await db.execute("DELETE FROM social.brands WHERE id = $1", brand_id)
    if result == "DELETE 0":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")
    return OkResponse(data={"deleted": True})


@router.patch("/{brand_id}/kit", response_model=OkResponse)
async def update_brand_kit(
    brand_id: UUID,
    payload: BrandKitUpdate,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Update the brand_kit JSONB field for a brand."""
    row = await db.fetchrow("SELECT brand_kit FROM social.brands WHERE id = $1", brand_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Brand not found")

    # Merge incoming fields into existing brand_kit
    existing = dict(row["brand_kit"]) if row["brand_kit"] else {}
    updates = payload.model_dump(exclude_none=True)
    merged = {**existing, **updates}

    updated = await db.fetchrow(
        "UPDATE social.brands SET brand_kit = $2, updated_at = now() WHERE id = $1 RETURNING *",
        brand_id,
        json.dumps(merged),
    )
    return OkResponse(data=dict(updated))


@router.post("/{brand_id}/logo", response_model=OkResponse)
async def upload_logo(
    brand_id: UUID,
    variant: str = Form(...),  # "light" or "dark"
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Upload a brand logo (light or dark variant) to R2."""
    if variant not in ("light", "dark"):
        raise HTTPException(status_code=400, detail="variant must be 'light' or 'dark'")
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "png"
    path = f"brands/{brand_id}/kit/logo_{variant}.{ext}"
    content = await file.read()
    public_url = r2.upload(content, path, file.content_type)

    col = "logo_light_url" if variant == "light" else "logo_dark_url"
    row = await db.fetchrow(
        f"UPDATE social.brands SET {col} = $2, updated_at = now() WHERE id = $1 RETURNING *",
        brand_id,
        public_url,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Brand not found")
    return OkResponse(data={"url": public_url})


@router.post("/{brand_id}/intro-video", response_model=OkResponse)
async def upload_intro_video(
    brand_id: UUID,
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Upload a brand intro video to R2."""
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported video type")

    ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "mp4"
    path = f"brands/{brand_id}/kit/intro.{ext}"
    content = await file.read()
    public_url = r2.upload(content, path, file.content_type)

    row = await db.fetchrow(
        "UPDATE social.brands SET intro_video_url = $2, updated_at = now() WHERE id = $1 RETURNING *",
        brand_id,
        public_url,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Brand not found")
    return OkResponse(data={"url": public_url})
