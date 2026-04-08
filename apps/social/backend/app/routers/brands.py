from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import BrandCreate, BrandOut, BrandUpdate, OkResponse

router = APIRouter(prefix="/brands", tags=["brands"])


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
