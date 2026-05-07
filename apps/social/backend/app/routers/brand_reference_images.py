"""Sprint 3 (Özel Gün) — Marka referans görsel kütüphanesi CRUD.

Endpoints:
    POST   /brand-reference-images           → upload (multipart, save_to_library opsiyonel)
    GET    /brand-reference-images?brand_id= → list
    DELETE /brand-reference-images/{id}      → hard delete + R2 cleanup

Kullanım: kullanıcı kendi referans görsellerini (Atatürk fotoğrafı, kurucu portre vb.)
yükler; içerik üretirken Nano Banana 2 edit'e ref olarak verilir.

save_to_library=true (default): R2 + DB kayıtlı, kütüphaneden tekrar seçilebilir.
save_to_library=false: yalnız R2'ye geçici yazılır, DB'ye kayıt yok (tek seferlik).

Limit: marka başına max 20 aktif kayıt — application layer (brand_products pattern).
"""
from uuid import UUID, uuid4

import asyncpg
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.database import get_db
from app.core.security import assert_brand_owned, get_current_user
from app.models.schemas import OkResponse
from app.services.storage import r2

router = APIRouter(prefix="/brand-reference-images", tags=["brand-reference-images"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_REFERENCES_PER_BRAND = 20


@router.post("", response_model=OkResponse, status_code=status.HTTP_201_CREATED)
async def upload_reference_image(
    brand_id: UUID = Form(...),
    file: UploadFile = File(...),
    label: str | None = Form(None),
    save_to_library: bool = Form(True),
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Yeni referans görsel yükle.

    save_to_library=true (default): R2 + DB kalıcı kayıt; max 20 limit kontrolü.
    save_to_library=false: yalnız R2'ye geçici upload, DB kayıt yok — tek seferlik
    kullanım için (frontend çıktıyı `image_url` olarak alır, scene_reference_image_url
    payload alanına koyar).
    """
    await assert_brand_owned(db, user, brand_id)

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Desteklenmeyen görsel tipi: {file.content_type}. JPEG/PNG/WebP yükleyin.",
        )

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="Görsel boyutu 10 MB'ı geçemez.")

    if save_to_library:
        existing = await db.fetchval(
            "SELECT COUNT(*) FROM social.brand_reference_images WHERE brand_id = $1",
            brand_id,
        )
        if existing >= MAX_REFERENCES_PER_BRAND:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Marka başına en fazla {MAX_REFERENCES_PER_BRAND} referans görsel "
                    f"saklayabilirsiniz. Önce eski görselleri silin."
                ),
            )

    ext_map = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
    ext = ext_map[file.content_type]

    if save_to_library:
        ref_id = uuid4()
        r2_path = f"brands/{brand_id}/references/{ref_id}.{ext}"
    else:
        # Geçici upload — tek seferlik, kütüphane dışı
        r2_path = f"brands/{brand_id}/references/temp/{uuid4()}.{ext}"

    public_url = r2.upload(content, r2_path, file.content_type)
    size_kb = max(1, len(content) // 1024)

    if not save_to_library:
        return OkResponse(
            data={
                "image_url": public_url,
                "image_key": r2_path,
                "saved": False,
            }
        )

    row = await db.fetchrow(
        """
        INSERT INTO social.brand_reference_images
            (id, brand_id, image_url, image_key, label, mime_type, size_kb)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING *
        """,
        ref_id,
        brand_id,
        public_url,
        r2_path,
        label,
        file.content_type,
        size_kb,
    )
    return OkResponse(data=dict(row))


@router.get("", response_model=OkResponse)
async def list_reference_images(
    brand_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Markaya bağlı referans görselleri listele (yeni eklenen önce)."""
    await assert_brand_owned(db, user, brand_id)
    rows = await db.fetch(
        """
        SELECT * FROM social.brand_reference_images
        WHERE brand_id = $1
        ORDER BY created_at DESC
        """,
        brand_id,
    )
    items = [dict(r) for r in rows]
    return OkResponse(data={"items": items, "count": len(items), "max": MAX_REFERENCES_PER_BRAND})


@router.delete("/{ref_id}", response_model=OkResponse)
async def delete_reference_image(
    ref_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Referans görseli sil — DB + R2 (best-effort)."""
    row = await db.fetchrow(
        """
        SELECT r.id, r.brand_id, r.image_key
        FROM social.brand_reference_images r
        JOIN social.brands b ON b.id = r.brand_id
        JOIN social.workspace_members wm ON wm.workspace_id = b.workspace_id
        WHERE r.id = $1 AND wm.account_id = $2
        """,
        ref_id,
        user["sub"],
    )
    if not row:
        raise HTTPException(status_code=404, detail="Referans görsel bulunamadı")

    image_key = row["image_key"]
    if image_key:
        try:
            r2.delete(image_key)
        except Exception:
            pass

    await db.execute("DELETE FROM social.brand_reference_images WHERE id = $1", ref_id)
    return OkResponse(data={"deleted": True})
