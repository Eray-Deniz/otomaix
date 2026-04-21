"""Phase 9 Sprint 4 — Ürün/Hizmet dokümanları (product_documents CRUD).

Endpoints:
    POST   /product-documents               → upload (multipart, RAG pipeline)
    GET    /product-documents?product_id=   → list
    GET    /product-documents/{doc_id}      → detail
    DELETE /product-documents/{doc_id}      → delete + R2 cleanup (chunks cascade)

Ownership zinciri: product_documents → brand_products → brands → workspace_members → accounts.
Cascade: brand_products → product_documents → product_document_chunks (DB).
R2 cleanup: DELETE üzerinde best-effort.
"""
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import OkResponse
from app.services.document_processor import ALLOWED_MIME_TYPES, process_document
from app.services.storage import r2

router = APIRouter(prefix="/product-documents", tags=["product-documents"])

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB — brand_documents ile aynı


async def _assert_product_owned(
    db: asyncpg.Connection,
    user: dict,
    product_id: UUID,
) -> dict:
    """Ürün sahiplik kontrolü (inline JOIN, 404 on miss)."""
    account_id = user.get("sub")
    if not account_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz oturum")
    row = await db.fetchrow(
        """
        SELECT p.id, p.brand_id
        FROM social.brand_products p
        JOIN social.brands b ON b.id = p.brand_id
        JOIN social.workspace_members m ON m.workspace_id = b.workspace_id
        WHERE p.id = $1 AND m.account_id = $2
        LIMIT 1
        """,
        product_id,
        account_id,
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ürün bulunamadı")
    return dict(row)


async def _assert_doc_owned(
    db: asyncpg.Connection,
    user: dict,
    doc_id: UUID,
) -> dict:
    """Doküman sahiplik kontrolü (product_documents → brand_products → brands → members)."""
    account_id = user.get("sub")
    if not account_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz oturum")
    row = await db.fetchrow(
        """
        SELECT d.*, p.brand_id
        FROM social.product_documents d
        JOIN social.brand_products p ON p.id = d.product_id
        JOIN social.brands b ON b.id = p.brand_id
        JOIN social.workspace_members m ON m.workspace_id = b.workspace_id
        WHERE d.id = $1 AND m.account_id = $2
        LIMIT 1
        """,
        doc_id,
        account_id,
    )
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Doküman bulunamadı")
    return dict(row)


@router.post("", response_model=OkResponse, status_code=status.HTTP_201_CREATED)
async def upload_product_document(
    product_id: UUID = Form(...),
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Ürüne doküman ekle → R2'ye yükle + metin çıkar + chunk/embed pipeline."""
    product = await _assert_product_owned(db, user, product_id)
    brand_id = product["brand_id"]

    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Desteklenmeyen dosya tipi: {file.content_type}. PDF, Word, Excel veya metin dosyası yükleyin.",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Dosya boyutu 50 MB'ı geçemez.")

    filename = file.filename or "document"
    file_size = len(content)

    row = await db.fetchrow(
        """
        INSERT INTO social.product_documents
            (product_id, filename, file_url, file_key, file_type, file_size)
        VALUES ($1, $2, '', '', $3, $4)
        RETURNING *
        """,
        product_id,
        filename,
        file.content_type,
        file_size,
    )
    doc_id = row["id"]

    r2_path = f"brands/{brand_id}/products/{product_id}/documents/{doc_id}_{filename}"
    public_url = r2.upload(content, r2_path, file.content_type)

    await db.execute(
        "UPDATE social.product_documents SET file_url = $2, file_key = $3 WHERE id = $1",
        doc_id,
        public_url,
        r2_path,
    )

    processing_result = await process_document(
        doc_id, None, content, file.content_type, db, kind="product"
    )

    doc = dict(row)
    doc["file_url"] = public_url
    doc["file_key"] = r2_path
    doc["processing"] = processing_result

    return OkResponse(data=doc)


@router.get("", response_model=OkResponse)
async def list_product_documents(
    product_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Ürüne bağlı dokümanları listele + chunk_count."""
    await _assert_product_owned(db, user, product_id)
    rows = await db.fetch(
        """
        SELECT d.id, d.product_id, d.filename, d.file_url, d.file_key,
               d.file_type, d.file_size, d.created_at,
               (d.raw_text IS NOT NULL) AS has_raw_text,
               (SELECT COUNT(*) FROM social.product_document_chunks c WHERE c.document_id = d.id)
                 AS chunk_count
        FROM social.product_documents d
        WHERE d.product_id = $1
        ORDER BY d.created_at DESC
        """,
        product_id,
    )
    documents = [dict(r) for r in rows]
    return OkResponse(data={"documents": documents, "count": len(documents)})


@router.get("/{doc_id}", response_model=OkResponse)
async def get_product_document(
    doc_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Tek doküman detayı + chunk sayısı."""
    doc = await _assert_doc_owned(db, user, doc_id)
    doc["has_raw_text"] = doc.get("raw_text") is not None
    doc["chunk_count"] = await db.fetchval(
        "SELECT COUNT(*) FROM social.product_document_chunks WHERE document_id = $1",
        doc_id,
    )
    doc.pop("brand_id", None)
    doc.pop("raw_text", None)
    return OkResponse(data=doc)


@router.delete("/{doc_id}", response_model=OkResponse)
async def delete_product_document(
    doc_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Dokümanı sil. Chunks cascade ile otomatik silinir. R2 cleanup best-effort."""
    doc = await _assert_doc_owned(db, user, doc_id)
    file_key = doc.get("file_key")

    await db.execute("DELETE FROM social.product_documents WHERE id = $1", doc_id)

    if file_key:
        try:
            r2.delete(file_key)
        except Exception:
            pass

    return OkResponse(data={"deleted": True, "id": str(doc_id)})
