"""Phase 9 Sprint 3 — Ürün/Hizmet Kütüphanesi CRUD.

Endpoints:
    POST   /products                 → create (JSON, quota-checked, 30/hour)
    POST   /products/{id}/image      → upload product image (multipart) — DEPRECATED (Sprint 1)
                                       Yeni: POST /products/{id}/images (çoklu görsel desteği).
                                       Eski endpoint mevcut FE/3rd party uyumluluğu için kalır;
                                       içerden product_images tablosuna yazar (mevcut tüm görselleri
                                       silip yenisini ana görsel olarak ekler — tek görsel davranışı).
    GET    /products?brand_id=       → list (filter: type, active) — response'da images dizisi
    GET    /products/{id}            → detail — response'da images dizisi
    PATCH  /products/{id}            → update (type immutable)
    DELETE /products/{id}            → hard delete + R2 cleanup
                                       (product_documents/chunks/product_images cascade in DB)

Ownership: JOIN via brands → workspace_members → accounts (same pattern as documents.py).
Quota: check_product_quota — marka başına plan-spesifik aktif ürün sayısı.
"""
from uuid import UUID, uuid4

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
EXT_MAP = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


async def _fetch_product_images(db: asyncpg.Connection, product_id: UUID) -> list[dict]:
    """Ürünün tüm görsellerini sıralı (ana görsel ilk) döndür."""
    rows = await db.fetch(
        """
        SELECT * FROM social.product_images
        WHERE product_id = $1
        ORDER BY is_primary DESC, position ASC, created_at ASC
        """,
        product_id,
    )
    return [dict(r) for r in rows]


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
            (brand_id, type, name, description, highlight, tags, is_active)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        RETURNING *
        """,
        payload.brand_id,
        payload.type,
        payload.name,
        payload.description,
        payload.highlight,
        payload.tags,
        payload.is_active,
    )
    product = dict(row)
    product["document_count"] = 0
    product["images"] = []
    return OkResponse(data=product)


@router.post("/{product_id}/image", response_model=OkResponse, deprecated=True)
async def upload_product_image(
    product_id: UUID,
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """DEPRECATED (Sprint 1): yeni endpoint POST /products/{id}/images kullanın.

    Bu endpoint geriye dönük uyumluluk için kalır; davranışı: ürünün TÜM mevcut
    görsellerini siler ve yeni görseli ana görsel olarak ekler (tek görsel mantığı).
    Çoklu görsel için yeni endpoint'i kullanın.
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

    # Mevcut tüm görsellerin R2 key'lerini topla (DELETE'ten önce)
    old_images = await db.fetch(
        "SELECT image_key FROM social.product_images WHERE product_id = $1",
        product_id,
    )
    old_keys = [r["image_key"] for r in old_images if r["image_key"]]
    # brand_products.image_key (denormalize) — backfill öncesi kayıtlar için ek koruma
    legacy_key = product.get("image_key")
    if legacy_key and legacy_key not in old_keys:
        old_keys.append(legacy_key)

    image_id = uuid4()
    ext = EXT_MAP[file.content_type]
    r2_path = f"brands/{product['brand_id']}/products/{product_id}/images/{image_id}.{ext}"
    public_url = r2.upload(content, r2_path, file.content_type)
    size_kb = max(1, len(content) // 1024)

    async with db.transaction():
        # Eski tüm görselleri DB'den sil
        await db.execute("DELETE FROM social.product_images WHERE product_id = $1", product_id)
        # Yeniyi ana görsel olarak ekle
        await db.execute(
            """
            INSERT INTO social.product_images
                (id, product_id, image_url, image_key, is_primary, position, mime_type, size_kb)
            VALUES ($1, $2, $3, $4, true, 0, $5, $6)
            """,
            image_id,
            product_id,
            public_url,
            r2_path,
            file.content_type,
            size_kb,
        )
        # brand_products denormalize senkron
        row = await db.fetchrow(
            """
            UPDATE social.brand_products
            SET image_url = $2, image_key = $3, updated_at = now()
            WHERE id = $1
            RETURNING *
            """,
            product_id,
            public_url,
            r2_path,
        )

    # R2 cleanup (best-effort, transaction dışı)
    for k in old_keys:
        try:
            r2.delete(k)
        except Exception:
            pass

    result = dict(row)
    result["document_count"] = await db.fetchval(
        "SELECT COUNT(*) FROM social.product_documents WHERE product_id = $1",
        product_id,
    )
    result["images"] = await _fetch_product_images(db, product_id)
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
    products = [dict(r) for r in rows]
    # Her ürün için images alanı (N+1 sorgu ama listelemede kabul edilebilir; ürün sayısı düşük).
    for p in products:
        p["images"] = await _fetch_product_images(db, p["id"])
    return OkResponse(data={"products": products, "count": len(products)})


@router.get("/{product_id}", response_model=OkResponse)
async def get_product(
    product_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Tek ürün detayı + doküman sayısı + görseller."""
    product = await assert_product_owned(db, user, product_id)
    product["document_count"] = await db.fetchval(
        "SELECT COUNT(*) FROM social.product_documents WHERE product_id = $1",
        product_id,
    )
    product["images"] = await _fetch_product_images(db, product_id)
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
            ("highlight", payload.highlight),
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
    result["images"] = await _fetch_product_images(db, product_id)
    return OkResponse(data=result)


@router.delete("/{product_id}", response_model=OkResponse)
async def delete_product(
    product_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Ürünü + bağlı dokümanları + tüm görselleri sil. R2 cleanup best-effort.

    Cascade: brand_products → product_documents → product_document_chunks (DB)
    Cascade: brand_products → product_images (DB)
    R2 cleanup: tüm görseller + tüm doküman dosyaları (manuel).
    """
    product = await assert_product_owned(db, user, product_id)

    # Bağlı doküman R2 key'lerini topla (DELETE'ten önce)
    doc_rows = await db.fetch(
        "SELECT file_key FROM social.product_documents WHERE product_id = $1",
        product_id,
    )
    doc_keys = [r["file_key"] for r in doc_rows if r["file_key"]]

    # Bağlı tüm görsel R2 key'lerini topla
    image_rows = await db.fetch(
        "SELECT image_key FROM social.product_images WHERE product_id = $1",
        product_id,
    )
    image_keys = [r["image_key"] for r in image_rows if r["image_key"]]
    # Backfill öncesi/legacy: brand_products.image_key denormalize değer (product_images'a düşmemiş olabilir)
    legacy_image_key = product.get("image_key")
    if legacy_image_key and legacy_image_key not in image_keys:
        image_keys.append(legacy_image_key)

    # DB delete (cascade ile chunks + documents + images otomatik silinir)
    await db.execute("DELETE FROM social.brand_products WHERE id = $1", product_id)

    # R2 cleanup (best effort — silmedeki hatalar kaydı geri getirmez)
    for key in doc_keys + image_keys:
        try:
            r2.delete(key)
        except Exception:
            pass

    return OkResponse(data={"deleted": True, "id": str(product_id)})
