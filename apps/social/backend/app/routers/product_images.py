"""Sprint 1 (Çoklu Ürün Görseli) — Ürün/Hizmet görsel kütüphanesi CRUD.

Endpoints:
    GET    /products/{product_id}/images                       → list (position'a göre sıralı)
    POST   /products/{product_id}/images                       → upload (multipart, max 5)
    DELETE /products/{product_id}/images/{image_id}            → sil + R2 cleanup
                                                                 (ana görselse otomatik handoff)
    PATCH  /products/{product_id}/images/{image_id}/primary    → ana görseli değiştir (transaction)
    PATCH  /products/{product_id}/images/reorder               → drag-drop sıra batch update

Mimari notu: brand_products.image_url/image_key kolonları ANA görselin denormalize
kopyasıdır — mevcut posts.py / short_video.py SELECT image_url FROM brand_products
çağrılarını bozmamak için. Ana görsel değişiminde transaction'la senkron edilir.

Limit: ürün başına max 5 aktif kayıt — Nano Banana 2/edit sweet spot
(brand_reference_images max 20 paterniyle tutarlı, ürün limiti daha sıkı).

Ownership: brand_products → brands → workspace_members → accounts (assert_product_owned).
"""
from uuid import UUID, uuid4

import asyncpg
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import assert_product_owned, get_current_user
from app.models.schemas import OkResponse
from app.services.storage import r2

router = APIRouter(prefix="/products", tags=["product-images"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_IMAGES_PER_PRODUCT = 5  # Nano Banana 2/edit sweet spot
EXT_MAP = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


class ReorderPayload(BaseModel):
    image_ids: list[UUID]


@router.get("/{product_id}/images", response_model=OkResponse)
async def list_product_images(
    product_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Ürünün görsellerini sırayla listele (ana görsel her zaman position=0)."""
    await assert_product_owned(db, user, product_id)
    rows = await db.fetch(
        """
        SELECT * FROM social.product_images
        WHERE product_id = $1
        ORDER BY is_primary DESC, position ASC, created_at ASC
        """,
        product_id,
    )
    items = [dict(r) for r in rows]
    return OkResponse(
        data={
            "items": items,
            "count": len(items),
            "max": MAX_IMAGES_PER_PRODUCT,
        }
    )


@router.post(
    "/{product_id}/images",
    response_model=OkResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_product_image_v2(
    product_id: UUID,
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Ürüne yeni görsel ekle. İlk görsel otomatik ana görsel olur.

    Limit: ürün başına max 5 (Nano Banana 2/edit sweet spot).
    R2 path: brands/{brand_id}/products/{product_id}/images/{image_id}.{ext}
    """
    product = await assert_product_owned(db, user, product_id)

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Desteklenmeyen görsel tipi: {file.content_type}. JPEG/PNG/WebP yükleyin.",
        )

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="Görsel boyutu 10 MB'ı geçemez.")

    existing_count = await db.fetchval(
        "SELECT COUNT(*) FROM social.product_images WHERE product_id = $1",
        product_id,
    )
    if existing_count >= MAX_IMAGES_PER_PRODUCT:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Ürün başına en fazla {MAX_IMAGES_PER_PRODUCT} görsel ekleyebilirsiniz. "
                f"Önce eski görselleri silin."
            ),
        )

    image_id = uuid4()
    ext = EXT_MAP[file.content_type]
    r2_path = f"brands/{product['brand_id']}/products/{product_id}/images/{image_id}.{ext}"
    public_url = r2.upload(content, r2_path, file.content_type)
    size_kb = max(1, len(content) // 1024)

    is_primary = existing_count == 0  # ilk görsel otomatik ana görsel
    next_position = await db.fetchval(
        "SELECT COALESCE(MAX(position), -1) + 1 FROM social.product_images WHERE product_id = $1",
        product_id,
    )

    async with db.transaction():
        row = await db.fetchrow(
            """
            INSERT INTO social.product_images
                (id, product_id, image_url, image_key, is_primary, position, mime_type, size_kb)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING *
            """,
            image_id,
            product_id,
            public_url,
            r2_path,
            is_primary,
            next_position,
            file.content_type,
            size_kb,
        )
        if is_primary:
            # Denormalize: brand_products.image_url/image_key senkronla
            await db.execute(
                """
                UPDATE social.brand_products
                SET image_url = $2, image_key = $3, updated_at = now()
                WHERE id = $1
                """,
                product_id,
                public_url,
                r2_path,
            )

    return OkResponse(data=dict(row))


@router.delete("/{product_id}/images/{image_id}", response_model=OkResponse)
async def delete_product_image(
    product_id: UUID,
    image_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Görseli sil. Ana görselse: bir sonraki görsel ana olur, brand_products senkronlanır.
    Hiç görsel kalmazsa brand_products.image_url=NULL.
    """
    await assert_product_owned(db, user, product_id)

    img = await db.fetchrow(
        "SELECT id, image_key, is_primary FROM social.product_images WHERE id = $1 AND product_id = $2",
        image_id,
        product_id,
    )
    if not img:
        raise HTTPException(status_code=404, detail="Görsel bulunamadı")

    async with db.transaction():
        await db.execute("DELETE FROM social.product_images WHERE id = $1", image_id)

        if img["is_primary"]:
            # Bir sonraki görseli ana yap (position'a göre)
            next_img = await db.fetchrow(
                """
                SELECT id, image_url, image_key FROM social.product_images
                WHERE product_id = $1
                ORDER BY position ASC, created_at ASC
                LIMIT 1
                """,
                product_id,
            )
            if next_img:
                await db.execute(
                    "UPDATE social.product_images SET is_primary = true WHERE id = $1",
                    next_img["id"],
                )
                await db.execute(
                    """
                    UPDATE social.brand_products
                    SET image_url = $2, image_key = $3, updated_at = now()
                    WHERE id = $1
                    """,
                    product_id,
                    next_img["image_url"],
                    next_img["image_key"],
                )
            else:
                # Hiç görsel kalmadı
                await db.execute(
                    """
                    UPDATE social.brand_products
                    SET image_url = NULL, image_key = NULL, updated_at = now()
                    WHERE id = $1
                    """,
                    product_id,
                )

    # R2 cleanup (best-effort)
    if img["image_key"]:
        try:
            r2.delete(img["image_key"])
        except Exception:
            pass

    return OkResponse(data={"deleted": True, "id": str(image_id)})


@router.patch("/{product_id}/images/{image_id}/primary", response_model=OkResponse)
async def set_primary_image(
    product_id: UUID,
    image_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Ana görseli değiştir — eski is_primary=false, yeni is_primary=true,
    brand_products.image_url/image_key senkronla. Tek transaction.
    """
    await assert_product_owned(db, user, product_id)

    new_primary = await db.fetchrow(
        """
        SELECT id, image_url, image_key FROM social.product_images
        WHERE id = $1 AND product_id = $2
        """,
        image_id,
        product_id,
    )
    if not new_primary:
        raise HTTPException(status_code=404, detail="Görsel bulunamadı")

    async with db.transaction():
        # Mevcut primary'yi sıfırla (unique partial index nedeniyle önce eski sıfırlanmalı)
        await db.execute(
            "UPDATE social.product_images SET is_primary = false WHERE product_id = $1 AND is_primary = true",
            product_id,
        )
        await db.execute(
            "UPDATE social.product_images SET is_primary = true WHERE id = $1",
            image_id,
        )
        await db.execute(
            """
            UPDATE social.brand_products
            SET image_url = $2, image_key = $3, updated_at = now()
            WHERE id = $1
            """,
            product_id,
            new_primary["image_url"],
            new_primary["image_key"],
        )

    return OkResponse(data={"updated": True, "primary_id": str(image_id)})


@router.patch("/{product_id}/images/reorder", response_model=OkResponse)
async def reorder_product_images(
    product_id: UUID,
    payload: ReorderPayload,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Drag-drop sıra batch update. payload.image_ids = ürünün TÜM görsel ID'leri yeni sırada.

    Validation: image_ids ürünün gerçek görsel ID'leriyle birebir eşleşmeli (eksik/fazla kabul yok).
    Position 0'dan başlar. Ana görsel statüsü değişmez (sıra ile bağımsız).
    """
    await assert_product_owned(db, user, product_id)

    rows = await db.fetch(
        "SELECT id FROM social.product_images WHERE product_id = $1",
        product_id,
    )
    db_ids = {r["id"] for r in rows}
    payload_ids = set(payload.image_ids)
    if db_ids != payload_ids:
        raise HTTPException(
            status_code=400,
            detail="Sıra listesi ürünün görselleriyle birebir eşleşmiyor.",
        )

    async with db.transaction():
        for new_position, img_id in enumerate(payload.image_ids):
            await db.execute(
                "UPDATE social.product_images SET position = $2 WHERE id = $1",
                img_id,
                new_position,
            )

    return OkResponse(data={"reordered": True, "count": len(payload.image_ids)})
