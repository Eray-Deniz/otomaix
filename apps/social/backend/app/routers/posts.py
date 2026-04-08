from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import OkResponse, PostCreate

router = APIRouter(prefix="/posts", tags=["posts"])


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
