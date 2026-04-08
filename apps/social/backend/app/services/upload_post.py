"""Upload-Post.com integration for social media publishing."""

from uuid import UUID

import asyncpg
import httpx

from app.core.config import settings

BASE_URL = "https://api.upload-post.com/v1"


def get_oauth_link(brand_id: UUID, platform: str) -> str:
    """
    Generate a JWT-authenticated OAuth link for connecting a social account.
    The client opens this URL to grant Upload-Post access to their platform account.
    """
    import time

    from jose import jwt

    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "brand_id": str(brand_id),
        "platform": platform,
    }
    token = jwt.encode(payload, settings.UPLOAD_POST_API_KEY, algorithm="HS256")
    return f"{BASE_URL}/oauth/{platform}?token={token}"


async def publish_post(post_id: UUID, db: asyncpg.Connection) -> dict:
    """
    Publish a post to all configured platforms.
    Fetches post + brand social accounts from DB, calls Upload-Post API, updates status.
    """
    post = await db.fetchrow("SELECT * FROM social.posts WHERE id = $1", post_id)
    if not post:
        raise ValueError(f"Post {post_id} not found")

    if not post["output_url"]:
        raise ValueError("Post has no output_url — generate content first")

    brand_id = post["brand_id"]
    platforms = post["platforms"] or []
    results = []

    async with httpx.AsyncClient(timeout=30) as client:
        for platform in platforms:
            account = await db.fetchrow(
                """
                SELECT * FROM social.brand_social_accounts
                WHERE brand_id = $1 AND platform = $2 AND is_active = true
                """,
                brand_id,
                platform,
            )
            if not account:
                results.append({"platform": platform, "success": False, "error": "No active account"})
                continue

            resp = await client.post(
                f"{BASE_URL}/publish",
                headers={"Authorization": f"Bearer {settings.UPLOAD_POST_API_KEY}"},
                json={
                    "platform": platform,
                    "token": account["upload_post_token"],
                    "media_url": post["output_url"],
                    "caption": post["caption"] or "",
                    "hashtags": post["hashtags"] or [],
                },
            )

            if resp.status_code == 200:
                results.append({"platform": platform, "success": True, "data": resp.json()})
            else:
                results.append({"platform": platform, "success": False, "error": resp.text})

    all_ok = all(r["success"] for r in results)
    new_status = "published" if all_ok else "failed"
    import datetime

    await db.execute(
        "UPDATE social.posts SET status = $1, published_at = $2 WHERE id = $3",
        new_status,
        datetime.datetime.utcnow() if all_ok else None,
        post_id,
    )

    return {"post_id": str(post_id), "status": new_status, "platforms": results}
