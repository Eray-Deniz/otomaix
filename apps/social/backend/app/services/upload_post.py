"""
Upload-Post.com integration.

Real API (https://docs.upload-post.com/openapi.json):
- Base URL: https://api.upload-post.com/api
- Auth: `Authorization: Apikey <key>`
- One Upload-Post user profile per Otomaix brand (profile_username: "brand_<uuid8>")
- Flow:
    1. POST /uploadposts/users                → create profile (idempotent, 409 = already exists)
    2. POST /uploadposts/users/generate-jwt   → returns access_url (48h, single use) for user to connect accounts
    3. GET  /uploadposts/users/{username}     → returns social_accounts dict
    4. POST /upload / /upload_photos          → publish content (user=profile_username, platform[]=...)
"""

from __future__ import annotations

from uuid import UUID

import asyncpg
import httpx
import sentry_sdk

from app.core.config import settings

BASE_URL = "https://api.upload-post.com/api"
FRONTEND_REDIRECT = "https://app.otomaix.com/marka-ayarlari?tab=sosyal&connected=1"
HTTP_TIMEOUT = 30


def _headers() -> dict:
    return {"Authorization": f"Apikey {settings.UPLOAD_POST_API_KEY}"}


def profile_username_for_brand(brand_id: UUID) -> str:
    """Stable Upload-Post profile identifier for an Otomaix brand."""
    return f"brand_{str(brand_id).replace('-', '')[:16]}"


# ─── Profile management ────────────────────────────────────────────────────

async def ensure_profile(brand_id: UUID, db: asyncpg.Connection) -> str:
    """
    Ensure an Upload-Post profile exists for this brand.
    Returns the profile_username. Idempotent.
    """
    # Check DB cache first
    row = await db.fetchrow(
        "SELECT upload_post_username FROM social.brands WHERE id = $1",
        brand_id,
    )
    if row and row["upload_post_username"]:
        return row["upload_post_username"]

    username = profile_username_for_brand(brand_id)

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.post(
            f"{BASE_URL}/uploadposts/users",
            headers={**_headers(), "Content-Type": "application/json"},
            json={"username": username},
        )

    # 201 = created, 409 = already exists (both fine)
    if resp.status_code not in (200, 201, 409):
        sentry_sdk.set_context(
            "upload_post_create_profile",
            {"brand_id": str(brand_id), "username": username, "status": resp.status_code, "body": resp.text[:500]},
        )
        sentry_sdk.capture_message(
            f"Upload-Post create profile failed: HTTP {resp.status_code}",
            level="error",
        )
        raise RuntimeError(f"Upload-Post profile creation failed ({resp.status_code})")

    await db.execute(
        "UPDATE social.brands SET upload_post_username = $1 WHERE id = $2",
        username,
        brand_id,
    )
    return username


async def generate_connect_url(brand_id: UUID, platform: str, db: asyncpg.Connection) -> str:
    """
    Generate a single-use URL (48h) the user visits to link their social account.
    Creates the profile on Upload-Post if it doesn't exist yet.
    """
    username = await ensure_profile(brand_id, db)

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.post(
            f"{BASE_URL}/uploadposts/users/generate-jwt",
            headers={**_headers(), "Content-Type": "application/json"},
            json={
                "username": username,
                "redirect_url": FRONTEND_REDIRECT,
                "platforms": [platform],
            },
        )

    if resp.status_code != 200:
        sentry_sdk.set_context(
            "upload_post_generate_jwt",
            {"brand_id": str(brand_id), "platform": platform, "status": resp.status_code, "body": resp.text[:500]},
        )
        sentry_sdk.capture_message(
            f"Upload-Post generate-jwt failed: HTTP {resp.status_code}",
            level="error",
        )
        raise RuntimeError(f"Upload-Post JWT generation failed ({resp.status_code})")

    body = resp.json()
    url = body.get("access_url")
    if not url:
        raise RuntimeError("Upload-Post response missing access_url")
    return url


async def fetch_social_accounts(brand_id: UUID, db: asyncpg.Connection) -> list[dict]:
    """
    Fetch currently connected social accounts from Upload-Post for this brand.
    Returns a normalized list: [{platform, account_name, handle, display_name}, ...]
    """
    row = await db.fetchrow(
        "SELECT upload_post_username FROM social.brands WHERE id = $1",
        brand_id,
    )
    username = row["upload_post_username"] if row else None
    if not username:
        return []

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        resp = await client.get(
            f"{BASE_URL}/uploadposts/users/{username}",
            headers=_headers(),
        )

    if resp.status_code == 404:
        return []
    if resp.status_code != 200:
        sentry_sdk.capture_message(
            f"Upload-Post get user failed: HTTP {resp.status_code}",
            level="warning",
        )
        return []

    body = resp.json()
    profile = body.get("profile") or body
    social_accounts = profile.get("social_accounts") or {}

    result = []
    for platform, info in social_accounts.items():
        if not info:
            continue
        if isinstance(info, dict):
            result.append({
                "platform": platform,
                "account_name": info.get("handle") or info.get("username") or info.get("display_name") or platform,
                "display_name": info.get("display_name"),
                "reauth_required": info.get("reauth_required", False),
            })
        else:
            result.append({
                "platform": platform,
                "account_name": str(info),
                "display_name": None,
                "reauth_required": False,
            })
    return result


async def sync_social_accounts(brand_id: UUID, db: asyncpg.Connection) -> list[dict]:
    """
    Sync connected accounts from Upload-Post into local brand_social_accounts cache.
    Returns the fresh list.
    """
    accounts = await fetch_social_accounts(brand_id, db)

    # Cache in DB: deactivate all, then upsert active ones
    await db.execute(
        "UPDATE social.brand_social_accounts SET is_active = false WHERE brand_id = $1",
        brand_id,
    )
    for acc in accounts:
        await db.execute(
            """
            INSERT INTO social.brand_social_accounts
                (brand_id, platform, account_name, is_active, connected_at)
            VALUES ($1, $2, $3, true, now())
            ON CONFLICT (brand_id, platform) DO UPDATE SET
                account_name = EXCLUDED.account_name,
                is_active = true,
                connected_at = now()
            """,
            brand_id,
            acc["platform"],
            acc["account_name"],
        )
    return accounts


# ─── Publishing ────────────────────────────────────────────────────────────

async def _download_media(url: str) -> tuple[bytes, str]:
    """Download media from R2 (or any URL) and return (bytes, content-type)."""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "application/octet-stream")
        return resp.content, content_type


def _filename_from_url(url: str, default: str) -> str:
    from urllib.parse import urlparse
    path = urlparse(url).path
    name = path.rsplit("/", 1)[-1]
    return name or default


async def _publish_single_platform(
    *,
    db: asyncpg.Connection,
    post_id: UUID,
    platform: str,
    username: str,
    is_video: bool,
    media_bytes: bytes,
    media_mime: str,
    filename: str,
    title_text: str,
) -> dict:
    """Upload-Post'a TEK platform için yayın çağrısı yapar ve
    `post_publications` satırını sonuca göre günceller. Her platform'un
    başarı/başarısızlık durumu bağımsız kayıt tutulur."""
    import datetime

    form_data = [
        ("user", (None, username)),
        ("title", (None, title_text[:2200])),
        ("platform[]", (None, platform)),
    ]
    if is_video:
        form_data.append(("video", (filename, media_bytes, media_mime)))
        endpoint = f"{BASE_URL}/upload"
    else:
        form_data.append(("photos[]", (filename, media_bytes, media_mime)))
        endpoint = f"{BASE_URL}/upload_photos"

    await db.execute(
        """
        INSERT INTO social.post_publications (post_id, platform, status)
        VALUES ($1, $2, 'publishing')
        ON CONFLICT (post_id, platform) DO UPDATE SET
            status = 'publishing',
            error_message = NULL,
            updated_at = now()
        """,
        post_id,
        platform,
    )

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(endpoint, headers=_headers(), files=form_data)
    except Exception as exc:  # noqa: BLE001
        err = str(exc)[:500]
        await db.execute(
            """
            UPDATE social.post_publications
            SET status = 'failed', error_message = $3, updated_at = now()
            WHERE post_id = $1 AND platform = $2
            """,
            post_id,
            platform,
            err,
        )
        return {"platform": platform, "status": "failed", "error": err}

    if resp.status_code == 200:
        body = resp.json() if resp.content else {}
        external_id = None
        platform_success = True  # Default varsayım: HTTP 200 + parse edilemeyen body → başarılı
        platform_error: str | None = None

        if isinstance(body, dict):
            results = body.get("results") or {}
            platform_data = results.get(platform) if isinstance(results, dict) else None
            if isinstance(platform_data, dict):
                # Upload-Post per-platform success field'ini açıkça döner
                ps = platform_data.get("success")
                if ps is False:
                    platform_success = False
                    platform_error = platform_data.get("error") or platform_data.get("status") or "Platform yayını başarısız"
                external_id = platform_data.get("id") or platform_data.get("post_id")

        if platform_success:
            await db.execute(
                """
                UPDATE social.post_publications
                SET status = 'published',
                    external_id = $3,
                    upload_post_response = $4,
                    published_at = $5,
                    error_message = NULL,
                    updated_at = now()
                WHERE post_id = $1 AND platform = $2
                """,
                post_id,
                platform,
                external_id,
                body if isinstance(body, dict) else {},
                datetime.datetime.utcnow(),
            )
            return {"platform": platform, "status": "published", "external_id": external_id}

        # HTTP 200 ama platform-level failure — failed olarak işaretle
        await db.execute(
            """
            UPDATE social.post_publications
            SET status = 'failed',
                error_message = $3,
                upload_post_response = $4,
                updated_at = now()
            WHERE post_id = $1 AND platform = $2
            """,
            post_id,
            platform,
            platform_error or "Platform yayını başarısız",
            body if isinstance(body, dict) else {},
        )
        return {"platform": platform, "status": "failed", "error": platform_error}

    err = f"HTTP {resp.status_code}: {resp.text[:300]}"
    # 4xx = kullanıcı hatası (platform bağlı değil, geçersiz medya vb.) — Sentry'ye gönderme
    # 5xx = Upload-Post tarafında sorun — Sentry'de görelim
    if resp.status_code >= 500:
        sentry_sdk.set_context(
            "upload_post_publish",
            {"post_id": str(post_id), "platform": platform, "status_code": resp.status_code, "body": resp.text[:500]},
        )
        sentry_sdk.capture_message(
            f"Upload-Post publish failed for {platform}: HTTP {resp.status_code}",
            level="error",
        )
    await db.execute(
        """
        UPDATE social.post_publications
        SET status = 'failed', error_message = $3, updated_at = now()
        WHERE post_id = $1 AND platform = $2
        """,
        post_id,
        platform,
        err,
    )
    return {"platform": platform, "status": "failed", "error": err}


async def publish_post(
    post_id: UUID,
    db: asyncpg.Connection,
    only_platforms: list[str] | None = None,
) -> dict:
    """
    Publish a post to its configured platforms via Upload-Post. Her platform
    için ayrı API çağrısı yapılır ve sonuç `post_publications` tablosunda
    platform-bazında saklanır.

    `only_platforms`: verilirse yalnızca bu platformlar için yayın (retry için).

    Idempotent: SELECT ... FOR UPDATE + `posts.status='publishing'` ile
    eşzamanlı çağrılar serileştirilir.

    Üst seviye `posts.status` sonuçları:
      - hepsi başarılı        → 'published'
      - en az biri başarılı   → 'partially_published'
      - hiçbiri başarılı değil → 'failed'
    """
    import datetime

    async with db.transaction():
        post = await db.fetchrow(
            "SELECT * FROM social.posts WHERE id = $1 FOR UPDATE",
            post_id,
        )
        if not post:
            raise ValueError(f"Post {post_id} not found")

        # Retry değilse idempotency kontrolü — tam published veya in-flight ise kısa devre
        if only_platforms is None:
            if post["status"] == "published":
                return {
                    "post_id": str(post_id),
                    "status": "published",
                    "note": "already_published",
                    "published_at": post["published_at"].isoformat() if post["published_at"] else None,
                }
            if post["status"] == "publishing":
                return {
                    "post_id": str(post_id),
                    "status": "publishing",
                    "note": "already_in_progress",
                }

        if not post["output_url"]:
            raise ValueError("Post has no output_url — generate content first")

        await db.execute(
            "UPDATE social.posts SET status = 'publishing' WHERE id = $1",
            post_id,
        )

    brand_id = post["brand_id"]
    all_platforms = post["platforms"] or []
    if not all_platforms:
        await db.execute(
            "UPDATE social.posts SET status = 'failed' WHERE id = $1",
            post_id,
        )
        return {"post_id": str(post_id), "status": "failed", "error": "No platforms configured"}

    # Retry: yalnızca istenen platformlar; yoksa hepsi
    platforms_to_publish = (
        [p for p in only_platforms if p in all_platforms]
        if only_platforms
        else list(all_platforms)
    )
    if not platforms_to_publish:
        return {"post_id": str(post_id), "status": "failed", "error": "No matching platforms"}

    username = await ensure_profile(brand_id, db)
    content_type = post["content_type"]
    is_video = content_type in ("video", "video_ugc")

    media_bytes, media_mime = await _download_media(post["output_url"])
    filename = _filename_from_url(post["output_url"], "media.mp4" if is_video else "media.jpg")

    caption = post["caption"] or ""
    hashtags = post["hashtags"] or []
    title_text = caption + (" " + " ".join(f"#{h.lstrip('#')}" for h in hashtags) if hashtags else "")

    results = []
    for platform in platforms_to_publish:
        res = await _publish_single_platform(
            db=db,
            post_id=post_id,
            platform=platform,
            username=username,
            is_video=is_video,
            media_bytes=media_bytes,
            media_mime=media_mime,
            filename=filename,
            title_text=title_text,
        )
        results.append(res)

    # Üst seviye durum: TÜM platformlara bak (retry edilmeyenler dahil)
    all_rows = await db.fetch(
        "SELECT platform, status FROM social.post_publications WHERE post_id = $1",
        post_id,
    )
    status_by_platform = {r["platform"]: r["status"] for r in all_rows}
    total = len(all_platforms)
    published_count = sum(1 for p in all_platforms if status_by_platform.get(p) == "published")

    if published_count == total:
        overall = "published"
    elif published_count == 0:
        overall = "failed"
    else:
        overall = "partially_published"

    published_at = datetime.datetime.utcnow() if published_count > 0 else None
    await db.execute(
        """
        UPDATE social.posts
        SET status = $2,
            published_at = COALESCE(published_at, $3)
        WHERE id = $1
        """,
        post_id,
        overall,
        published_at,
    )

    return {
        "post_id": str(post_id),
        "status": overall,
        "published_count": published_count,
        "total": total,
        "results": results,
    }
