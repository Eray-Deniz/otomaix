from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import OkResponse, PostCreate, PostGenerate
from app.services.fal_ai import generate_image

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post("/generate", response_model=OkResponse, status_code=status.HTTP_201_CREATED)
async def generate_post(
    payload: PostGenerate,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Create a post record and trigger fal.ai image generation."""
    brand = await db.fetchrow("SELECT brand_kit FROM social.brands WHERE id = $1", payload.brand_id)
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand_kit = dict(brand["brand_kit"]) if brand["brand_kit"] else {}

    row = await db.fetchrow(
        """
        INSERT INTO social.posts
            (brand_id, content_type, content_category, prompt, user_text,
             aspect_ratio, platforms, status)
        VALUES ($1, $2, $3, $4, $5, $6, $7, 'generating')
        RETURNING *
        """,
        payload.brand_id,
        payload.content_type,
        payload.content_category,
        payload.prompt,
        payload.user_text,
        payload.aspect_ratio,
        payload.platforms,
    )
    post = dict(row)

    try:
        fal_job_id = await generate_image(payload.prompt or "", payload.aspect_ratio, brand_kit)
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
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Trigger a new fal.ai generation for an existing post."""
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
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """List posts for a brand, optionally filtered by status."""
    if status:
        rows = await db.fetch(
            "SELECT * FROM social.posts WHERE brand_id = $1 AND status = $2 ORDER BY created_at DESC",
            brand_id,
            status,
        )
    else:
        rows = await db.fetch(
            "SELECT * FROM social.posts WHERE brand_id = $1 ORDER BY created_at DESC",
            brand_id,
        )
    return OkResponse(data=[dict(r) for r in rows])


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
