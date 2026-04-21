"""Phase 9 Sprint 3 — Ürün/Hizmet Kütüphanesi CRUD.

Endpoints:
    POST   /products                 → create (JSON, quota-checked, 30/hour)
    POST   /products/{id}/image      → upload product image (multipart)
    GET    /products?brand_id=       → list (filter: type, active)
    PATCH  /products/{id}            → update (type immutable)
    DELETE /products/{id}            → hard delete + R2 cleanup
                                       (product_documents/chunks cascade in DB)

Ownership: JOIN via brands → workspace_members → accounts (same pattern as documents.py).
Quota: check_product_quota — marka başına plan-spesifik aktif ürün sayısı.
"""
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.security import assert_brand_owned, assert_product_owned, get_current_user
from app.models.schemas import OkResponse, ProductCreate, ProductUpdate
from app.routers.billing import check_product_quota
from app.services.storage import r2

router = APIRouter(prefix="/products", tags=["products"])

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_TYPES = {"product", "service"}


def _r2_path_from_url(url: str) -> str | None:
    """Public URL'den R2 object key çıkar (prefix strip)."""
    if not url:
        return None
    prefix = f"{r2.public_url}/"
    if url.startswith(prefix):
        return url[len(prefix):]
    return None


@router.post(
    "",
    response_model=OkResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(limiter(30, 3600))],
)
async def create_product(
    payload: ProductCreate,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Marka ürün/hizmet kütüphanesine yeni kayıt ekle.

    Plan kotası: marka başına aktif ürün sayısı (`check_product_quota`).
    Rate limit: 30/saat (hesap başına).
    """
    if payload.type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Geçersiz tip: '{payload.type}'. 'product' veya 'service' olmalı.",
        )

    await assert_brand_owned(db, user, payload.brand_id)
    await check_product_quota(user["sub"], str(payload.brand_id), db)

    row = await db.fetchrow(
        """
        INSERT INTO social.brand_products
            (brand_id, type, name, description, tags, is_active)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING *
        """,
        payload.brand_id,
        payload.type,
        payload.name,
        payload.description,
        payload.tags,
        payload.is_active,
    )
    product = dict(row)
    product["document_count"] = 0
    return OkResponse(data=product)


@router.post("/{product_id}/image", response_model=OkResponse)
async def upload_product_image(
    product_id: UUID,
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Ürün görseli yükle → R2. Mevcut görsel varsa onu siler."""
    product = await assert_product_owned(db, user, product_id)

    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Desteklenmeyen görsel tipi: {file.content_type}. JPEG/PNG/WebP yükleyin.",
        )

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="Görsel boyutu 10 MB'ı geçemez.")

    # Eski görsel varsa R2'den sil (best effort)
    old_key = product.get("image_key")
    if old_key:
        try:
            r2.delete(old_key)
        except Exception:
            pass

    ext_map = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}
    ext = ext_map[file.content_type]
    r2_path = f"brands/{product['brand_id']}/products/{product_id}.{ext}"
    public_url = r2.upload(content, r2_path, file.content_type)

    row = await db.fetchrow(
        """
        UPDATE social.brand_products
        SET image_url = $2, image_key = $3
        WHERE id = $1
        RETURNING *
        """,
        product_id,
        public_url,
        r2_path,
    )
    result = dict(row)
    result["document_count"] = await db.fetchval(
        "SELECT COUNT(*) FROM social.product_documents WHERE product_id = $1",
        product_id,
    )
    return OkResponse(data=result)


@router.get("", response_model=OkResponse)
async def list_products(
    brand_id: UUID,
    type: str | None = None,
    active: bool | None = None,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Markaya bağlı ürünleri listele. Filtreler opsiyonel."""
    await assert_brand_owned(db, user, brand_id)

    if type is not None and type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Geçersiz tip filtresi: '{type}'.",
        )

    conditions = ["p.brand_id = $1"]
    params: list = [brand_id]
    if type is not None:
        params.append(type)
        conditions.append(f"p.type = ${len(params)}")
    if active is not None:
        params.append(active)
        conditions.append(f"p.is_active = ${len(params)}")

    where_sql = " AND ".join(conditions)
    rows = await db.fetch(
        f"""
        SELECT p.*,
               (SELECT COUNT(*) FROM social.product_documents d WHERE d.product_id = p.id)
                 AS document_count
        FROM social.brand_products p
        WHERE {where_sql}
        ORDER BY p.created_at DESC
        """,
        *params,
    )
    return OkResponse(data=[dict(r) for r in rows])


@router.get("/{product_id}", response_model=OkResponse)
async def get_product(
    product_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Tek ürün detayı + doküman sayısı."""
    product = await assert_product_owned(db, user, product_id)
    product["document_count"] = await db.fetchval(
        "SELECT COUNT(*) FROM social.product_documents WHERE product_id = $1",
        product_id,
    )
    return OkResponse(data=product)


@router.patch("/{product_id}", response_model=OkResponse)
async def update_product(
    product_id: UUID,
    payload: ProductUpdate,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Ürün alanlarını güncelle. `type` immutable — değiştirmek için yeni kayıt oluşturun."""
    await assert_product_owned(db, user, product_id)

    updates: list[str] = []
    params: list = []
    for idx, (field, value) in enumerate(
        [
            ("name", payload.name),
            ("description", payload.description),
            ("tags", payload.tags),
            ("is_active", payload.is_active),
        ],
        start=1,
    ):
        if value is not None:
            params.append(value)
            updates.append(f"{field} = ${len(params)}")

    if not updates:
        raise HTTPException(status_code=400, detail="Güncellenecek alan yok.")

    params.append(product_id)
    row = await db.fetchrow(
        f"""
        UPDATE social.brand_products
        SET {', '.join(updates)}
        WHERE id = ${len(params)}
        RETURNING *
        """,
        *params,
    )
    result = dict(row)
    result["document_count"] = await db.fetchval(
        "SELECT COUNT(*) FROM social.product_documents WHERE product_id = $1",
        product_id,
    )
    return OkResponse(data=result)


@router.delete("/{product_id}", response_model=OkResponse)
async def delete_product(
    product_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Ürünü + bağlı dokümanları sil. R2 cleanup best-effort.

    Cascade: brand_products → product_documents → product_document_chunks (DB)
    R2 cleanup: product image + all document files (manuel).
    """
    product = await assert_product_owned(db, user, product_id)

    # Bağlı doküman R2 key'lerini topla (DELETE'ten önce)
    doc_rows = await db.fetch(
        "SELECT file_key FROM social.product_documents WHERE product_id = $1",
        product_id,
    )
    doc_keys = [r["file_key"] for r in doc_rows if r["file_key"]]

    # DB delete (cascade ile chunks + documents otomatik silinir)
    await db.execute("DELETE FROM social.brand_products WHERE id = $1", product_id)

    # R2 cleanup (best effort — silmedeki hatalar kaydı geri getirmez)
    for key in doc_keys:
        try:
            r2.delete(key)
        except Exception:
            pass

    image_key = product.get("image_key")
    if image_key:
        try:
            r2.delete(image_key)
        except Exception:
            pass

    return OkResponse(data={"deleted": True, "id": str(product_id)})
