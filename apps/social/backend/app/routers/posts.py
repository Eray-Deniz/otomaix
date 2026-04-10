from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_db
from fastapi import Header
from app.core.security import get_current_user, get_current_user_optional, get_service_auth
from app.models.schemas import OkResponse, PostCreate, PostGenerate
from app.services.document_processor import get_document_context
from app.services.fal_ai import generate_image

router = APIRouter(prefix="/posts", tags=["posts"])


async def _build_prompt_with_rag(
    payload: PostGenerate,
    brand: object,
    brand_kit: dict,
    db,
) -> str:
    """Build an enriched image/content prompt by injecting document context."""
    base_prompt = payload.prompt or ""

    if not payload.document_ids:
        return base_prompt

    doc_context = await get_document_context(payload.document_ids, base_prompt, db)
    if not doc_context:
        return base_prompt

    brand_name = brand["name"] if brand["name"] else ""
    sector = brand["sector"] if brand["sector"] else ""
    tonality = brand_kit.get("tonality", "")
    colors = ", ".join(brand_kit.get("colors", []))
    hashtags = ", ".join(brand_kit.get("hashtags", []))

    enriched = f"""Sen Türk KOBİ'lerine sosyal medya içeriği üreten bir uzmansın.

Marka Bilgileri:
- İsim: {brand_name}
- Sektör: {sector}
- Ton: {tonality}
- Renkler: {colors}
- Hashtag'ler: {hashtags}

Referans Doküman İçeriği:
{doc_context}

{f"Mutlaka kullanılacak metin: {payload.user_text}" if payload.user_text else ""}

Görev: {base_prompt}

Platform: {", ".join(payload.platforms)}
Boyut: {payload.aspect_ratio}

Lütfen üret:
1. Görsel için kısa tasarım açıklaması (İngilizce, fal.ai için)
2. Caption (Türkçe, {tonality} tonda)
3. Hashtag önerileri

Yanıt olarak sadece JSON döndür: {{"image_prompt": "...", "caption": "...", "hashtags": [...]}}"""

    return enriched


@router.post("/generate", response_model=OkResponse, status_code=status.HTTP_201_CREATED)
async def generate_post(
    payload: PostGenerate,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Create a post record and trigger fal.ai image generation."""
    brand = await db.fetchrow(
        "SELECT brand_kit, name, sector FROM social.brands WHERE id = $1", payload.brand_id
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand_kit = dict(brand["brand_kit"]) if brand["brand_kit"] else {}

    # Build enriched prompt with document context (RAG)
    enriched_prompt = await _build_prompt_with_rag(payload, brand, brand_kit, db)

    row = await db.fetchrow(
        """
        INSERT INTO social.posts
            (brand_id, content_type, content_category, prompt, user_text,
             document_ids, aspect_ratio, platforms, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'generating')
        RETURNING *
        """,
        payload.brand_id,
        payload.content_type,
        payload.content_category,
        payload.prompt,
        payload.user_text,
        [str(d) for d in payload.document_ids] if payload.document_ids else None,
        payload.aspect_ratio,
        payload.platforms,
    )
    post = dict(row)

    try:
        fal_job_id = await generate_image(enriched_prompt, payload.aspect_ratio, brand_kit)
        await db.execute(
            "UPDATE social.posts SET fal_job_id = $2 WHERE id = $1",
            post["id"],
            fal_job_id,
        )
        post["fal_job_id"] = fal_job_id
    except Exception:
        pass  # Generation failure handled via webhook; status stays 'generating'

    return OkResponse(data={"post_id": str(post["id"]), "status": "generating"})


@router.post("/{post_id}/regenerate", response_model=OkResponse)
async def regenerate_post(
    post_id: UUID,
    x_internal_key: str | None = Header(default=None),
    user: dict | None = Depends(get_current_user_optional),
    db: asyncpg.Connection = Depends(get_db),
):
    """Trigger a new fal.ai generation for an existing post. Accepts JWT or X-Internal-Key."""
    from app.core.config import settings as _settings
    if not user and x_internal_key != _settings.INTERNAL_API_KEY:
        from fastapi import HTTPException as _HTTPException
        raise _HTTPException(status_code=401, detail="Not authenticated")
    post = await db.fetchrow(
        "SELECT p.*, b.brand_kit FROM social.posts p JOIN social.brands b ON b.id = p.brand_id WHERE p.id = $1",
        post_id,
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    brand_kit = dict(post["brand_kit"]) if post["brand_kit"] else {}
    await db.execute(
        "UPDATE social.posts SET status = 'generating', output_url = NULL, thumbnail_url = NULL WHERE id = $1",
        post_id,
    )

    try:
        fal_job_id = await generate_image(post["prompt"] or "", post["aspect_ratio"] or "1:1", brand_kit)
        await db.execute("UPDATE social.posts SET fal_job_id = $2 WHERE id = $1", post_id, fal_job_id)
    except Exception:
        pass

    return OkResponse(data={"post_id": str(post_id), "status": "generating"})


@router.post("/create", response_model=OkResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    payload: PostCreate,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Create a new post (status=draft). Trigger generation separately."""
    row = await db.fetchrow(
        """
        INSERT INTO social.posts
            (brand_id, content_type, content_category, prompt, user_text,
             aspect_ratio, platforms, scheduled_at)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING *
        """,
        payload.brand_id,
        payload.content_type,
        payload.content_category,
        payload.prompt,
        payload.user_text,
        payload.aspect_ratio,
        payload.platforms,
        payload.scheduled_at,
    )
    return OkResponse(data=dict(row))


@router.get("", response_model=OkResponse)
async def list_posts(
    brand_id: UUID,
    status: str | None = None,
    content_type: str | None = None,
    platform: str | None = None,
    page: int = 1,
    limit: int = 20,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """List posts for a brand with optional filters and pagination."""
    conditions = ["brand_id = $1"]
    params: list = [brand_id]
    idx = 2

    if status:
        conditions.append(f"status = ${idx}")
        params.append(status)
        idx += 1

    if content_type:
        conditions.append(f"content_type = ${idx}")
        params.append(content_type)
        idx += 1

    if platform:
        conditions.append(f"${idx} = ANY(platforms)")
        params.append(platform)
        idx += 1

    where = " AND ".join(conditions)
    offset = (page - 1) * limit

    rows = await db.fetch(
        f"SELECT * FROM social.posts WHERE {where} ORDER BY created_at DESC LIMIT {limit} OFFSET {offset}",
        *params,
    )
    total = await db.fetchval(f"SELECT COUNT(*) FROM social.posts WHERE {where}", *params)
    return OkResponse(data={
        "items": [dict(r) for r in rows],
        "total": total,
        "page": page,
        "pages": max(1, -(-total // limit)),  # ceil division
    })


@router.get("/{post_id}", response_model=OkResponse)
async def get_post(
    post_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Get a single post by id."""
    row = await db.fetchrow("SELECT * FROM social.posts WHERE id = $1", post_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return OkResponse(data=dict(row))


@router.post("/{post_id}/publish", response_model=OkResponse)
async def publish_post(
    post_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Trigger publishing a post to its configured platforms."""
    from app.services.upload_post import publish_post as svc_publish

    result = await svc_publish(post_id, db)
    return OkResponse(data=result)


@router.post("/{post_id}/publish-now", response_model=OkResponse)
async def publish_post_now(
    post_id: UUID,
    _: None = Depends(get_service_auth),
    db: asyncpg.Connection = Depends(get_db),
):
    """Publish a post immediately — called by n8n with X-Internal-Key header."""
    from app.services.upload_post import publish_post as svc_publish

    result = await svc_publish(post_id, db)
    return OkResponse(data=result)
