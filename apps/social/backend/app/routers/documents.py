from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import OkResponse
from app.services.document_processor import ALLOWED_MIME_TYPES, process_document
from app.services.storage import r2

router = APIRouter(prefix="/documents", tags=["documents"])

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.post("", response_model=OkResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    brand_id: UUID = Form(...),
    name: str = Form(...),
    category: str = Form(default=""),
    description: str = Form(default=""),
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Upload a document and trigger text extraction + RAG processing."""
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Desteklenmeyen dosya tipi: {file.content_type}. PDF, Word, Excel veya metin dosyası yükleyin.",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Dosya boyutu 50 MB'ı geçemez.")

    ext = file.filename.rsplit(".", 1)[-1] if "." in (file.filename or "") else "bin"
    file_size_kb = len(content) // 1024

    # Insert DB record first to get the ID
    row = await db.fetchrow(
        """
        INSERT INTO social.brand_documents
            (brand_id, name, file_url, file_type, category, description, file_size_kb)
        VALUES ($1, $2, '', $3, $4, $5, $6)
        RETURNING *
        """,
        brand_id,
        name,
        file.content_type,
        category or None,
        description or None,
        file_size_kb,
    )
    doc_id = row["id"]

    # Upload file to R2
    r2_path = f"brands/{brand_id}/documents/{doc_id}_{file.filename}"
    public_url = r2.upload(content, r2_path, file.content_type)

    await db.execute(
        "UPDATE social.brand_documents SET file_url = $2 WHERE id = $1",
        doc_id,
        public_url,
    )

    # Process document (extract text + chunk/embed)
    processing_result = await process_document(doc_id, brand_id, content, file.content_type, db)

    doc = dict(row)
    doc["file_url"] = public_url
    doc["processing"] = processing_result

    return OkResponse(data=doc)


@router.get("", response_model=OkResponse)
async def list_documents(
    brand_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """List all documents for a brand."""
    rows = await db.fetch(
        """
        SELECT id, brand_id, name, file_url, file_type, category, description,
               file_size_kb, created_at,
               (raw_text IS NOT NULL) AS has_raw_text,
               (SELECT COUNT(*) FROM social.brand_document_chunks c WHERE c.document_id = d.id) AS chunk_count
        FROM social.brand_documents d
        WHERE brand_id = $1
        ORDER BY created_at DESC
        """,
        brand_id,
    )
    return OkResponse(data=[dict(r) for r in rows])


@router.delete("/{doc_id}", response_model=OkResponse)
async def delete_document(
    doc_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Delete a document, its R2 file, and all associated chunks."""
    row = await db.fetchrow(
        "SELECT file_url FROM social.brand_documents WHERE id = $1",
        doc_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Doküman bulunamadı")

    # Try to delete from R2 (best effort)
    file_url = row["file_url"]
    if file_url:
        try:
            r2_path = file_url.replace(f"{r2.public_url}/", "")
            r2.delete(r2_path)
        except Exception:
            pass

    # Cascade deletes brand_document_chunks automatically
    await db.execute("DELETE FROM social.brand_documents WHERE id = $1", doc_id)

    return OkResponse(data={"deleted": True, "id": str(doc_id)})
