"""Webhook endpoints — currently fal.ai generation callbacks."""

from fastapi import APIRouter, Depends, Request

import asyncpg
from app.core.database import get_db
from app.models.schemas import OkResponse
from app.services.storage import r2

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/fal", response_model=OkResponse)
async def fal_webhook(request: Request, db: asyncpg.Connection = Depends(get_db)):
    """
    Receive fal.ai generation-complete callback.
    Downloads the generated file from fal's temp URL and copies it to R2,
    then updates the post record.
    """
    body = await request.json()

    request_id: str = body.get("request_id", "")
    payload = body.get("payload", {})
    images = payload.get("images", [])

    if not images:
        return OkResponse(data={"skipped": True, "reason": "no images in payload"})

    image_url: str = images[0].get("url", "")
    if not image_url:
        return OkResponse(data={"skipped": True, "reason": "empty image url"})

    # Find the post by fal_job_id
    post = await db.fetchrow("SELECT * FROM social.posts WHERE fal_job_id = $1", request_id)
    if not post:
        return OkResponse(data={"skipped": True, "reason": "post not found for request_id"})

    post_id = post["id"]
    brand_id = post["brand_id"]
    ext = "jpg"
    dest_path = f"brands/{brand_id}/posts/generated/{post_id}.{ext}"

    public_url = await r2.download_and_upload(image_url, dest_path, "image/jpeg")

    await db.execute(
        "UPDATE social.posts SET status = 'generated', output_url = $1, updated_at = now() WHERE id = $2",
        public_url,
        post_id,
    )

    return OkResponse(data={"post_id": str(post_id), "output_url": public_url})
