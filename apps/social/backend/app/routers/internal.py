"""Internal endpoints — called exclusively by n8n with X-Internal-Key header.

These bypass Supabase JWT auth and use a shared service key instead.
Never expose these routes to the public API without the service auth dependency.
"""

from datetime import datetime, timezone

import asyncpg
from fastapi import APIRouter, Depends

from app.core.database import get_db
from app.core.security import get_service_auth
from app.models.schemas import OkResponse

router = APIRouter(prefix="/internal", tags=["internal"])


@router.get("/autoposting/due", response_model=OkResponse)
async def get_due_configs(
    _: None = Depends(get_service_auth),
    db: asyncpg.Connection = Depends(get_db),
):
    """
    Return autoposting configs whose time slot matches the current time (±15 min window).
    Called by n8n Auto Posting Scheduler every 30 minutes.

    Logic:
    1. Fetch all enabled configs with brand timezone from brand_kit
    2. For each config, convert now() to brand timezone
    3. Check if current day+time falls within ±15 min of any time_slot
    4. Skip if a post was already generated/scheduled for this slot today
    """
    import json

    DAY_MAP = {
        0: "monday", 1: "tuesday", 2: "wednesday",
        3: "thursday", 4: "friday", 5: "saturday", 6: "sunday",
    }

    rows = await db.fetch(
        """
        SELECT ac.*, b.brand_kit, b.name AS brand_name,
               w.telegram_bot_token, w.telegram_chat_id
        FROM social.autoposting_configs ac
        JOIN social.brands b ON b.id = ac.brand_id
        JOIN social.workspaces w ON w.id = b.workspace_id
        WHERE ac.is_enabled = true
        """
    )

    now_utc = datetime.now(timezone.utc)
    due = []

    for row in rows:
        config = dict(row)
        brand_kit = dict(config.get("brand_kit") or {})
        tz_name = brand_kit.get("timezone", "Europe/Istanbul")

        try:
            from zoneinfo import ZoneInfo
            now_local = now_utc.astimezone(ZoneInfo(tz_name))
        except Exception:
            now_local = now_utc

        current_day = DAY_MAP[now_local.weekday()]
        current_minutes = now_local.hour * 60 + now_local.minute

        time_slots = config.get("time_slots") or []
        if isinstance(time_slots, str):
            time_slots = json.loads(time_slots)

        matched_slot = None
        for slot in time_slots:
            if slot.get("day") != current_day:
                continue
            try:
                h, m = map(int, slot["time"].split(":"))
            except (KeyError, ValueError):
                continue
            slot_minutes = h * 60 + m
            if abs(current_minutes - slot_minutes) <= 15:
                matched_slot = slot
                break

        if not matched_slot:
            continue

        # Duplicate guard: was a post already generated for this brand today?
        today_start = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        existing = await db.fetchval(
            """
            SELECT COUNT(*) FROM social.posts
            WHERE brand_id = $1
              AND status IN ('generating', 'ready', 'scheduled', 'publishing', 'published')
              AND created_at >= $2
            """,
            config["brand_id"],
            today_start.astimezone(timezone.utc).replace(tzinfo=None),
        )

        if existing and existing > 0:
            continue

        telegram_chat_id = config.get("telegram_chat_id") or ""
        due.append({
            "brand_id": str(config["brand_id"]),
            "brand_name": config["brand_name"],
            "frequency": config["frequency"],
            "matched_slot": matched_slot,
            "content_types": config["content_types"] or ["image"],
            "content_categories": config["content_categories"] or ["product"],
            "topics": config["topics"] or [],
            "platforms": config["platforms"] or [],
            "telegram_approval": bool(telegram_chat_id),
            "telegram_bot_token": config.get("telegram_bot_token") or "",
            "telegram_chat_id": telegram_chat_id,
        })

    return OkResponse(data=due)


from pydantic import BaseModel


class TriggerRequest(BaseModel):
    brand_id: str
    topic: str = ""
    content_type: str = "image"
    content_category: str = "product"
    platforms: list[str] = []
    telegram_approval: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""


@router.post("/autoposting/trigger", response_model=OkResponse)
async def trigger_autopost(
    payload: TriggerRequest,
    _: None = Depends(get_service_auth),
    db: asyncpg.Connection = Depends(get_db),
):
    """
    Generate a post for an autoposting config.
    Called by n8n for each due config returned by /internal/autoposting/due.
    Returns post_id so n8n can route to Telegram approval if needed.
    """
    from uuid import UUID as UUIDType
    from app.services.fal_ai import generate_image

    brand_id = UUIDType(payload.brand_id)
    brand = await db.fetchrow("SELECT brand_kit FROM social.brands WHERE id = $1", brand_id)
    if not brand:
        return OkResponse(data={"error": f"Brand {brand_id} not found"})

    raw_kit = brand["brand_kit"]
    if raw_kit and isinstance(raw_kit, str):
        import json as _json
        raw_kit = _json.loads(raw_kit)
    brand_kit = dict(raw_kit) if raw_kit else {}

    row = await db.fetchrow(
        """
        INSERT INTO social.posts
            (brand_id, content_type, content_category, prompt, aspect_ratio, platforms, status)
        VALUES ($1, $2, $3, $4, '1:1', $5, 'generating')
        RETURNING id
        """,
        brand_id,
        payload.content_type,
        payload.content_category,
        payload.topic or f"Otomatik {payload.content_category} içeriği",
        payload.platforms,
    )
    post_id = row["id"]

    try:
        fal_job_id = await generate_image(payload.topic or "", "1:1", brand_kit)
        await db.execute(
            "UPDATE social.posts SET fal_job_id = $2 WHERE id = $1",
            post_id, fal_job_id,
        )
    except Exception:
        pass

    return OkResponse(data={
        "post_id": str(post_id),
        "status": "generating",
        "telegram_approval": payload.telegram_approval,
        "telegram_bot_token": payload.telegram_bot_token,
        "telegram_chat_id": payload.telegram_chat_id,
    })


class StatusUpdate(BaseModel):
    status: str


@router.get("/posts/scheduled-due", response_model=OkResponse)
async def get_scheduled_due_posts(
    _: None = Depends(get_service_auth),
    db: asyncpg.Connection = Depends(get_db),
):
    """
    Return posts whose scheduled_at has passed and are still in 'scheduled' status.
    Called by n8n Scheduled Post Publisher every 5 minutes.

    NOTE: Must be declared BEFORE `/posts/{post_id}` — FastAPI matches routes in
    declaration order and would otherwise treat "scheduled-due" as a post_id.
    """
    rows = await db.fetch(
        """
        SELECT p.id, p.brand_id, p.platforms, p.scheduled_at,
               b.name AS brand_name
        FROM social.posts p
        JOIN social.brands b ON b.id = p.brand_id
        WHERE p.status = 'scheduled'
          AND p.scheduled_at IS NOT NULL
          AND p.scheduled_at <= NOW()
        ORDER BY p.scheduled_at ASC
        LIMIT 50
        """
    )
    due = [
        {
            "post_id": str(row["id"]),
            "brand_id": str(row["brand_id"]),
            "brand_name": row["brand_name"],
            "platforms": row["platforms"] or [],
            "scheduled_at": row["scheduled_at"].isoformat(),
        }
        for row in rows
    ]
    return OkResponse(data=due)


@router.get("/posts/{post_id}", response_model=OkResponse)
async def get_post_internal(
    post_id: str,
    _: None = Depends(get_service_auth),
    db: asyncpg.Connection = Depends(get_db),
):
    """Get post details — called by n8n without user JWT."""
    from uuid import UUID as UUIDType
    row = await db.fetchrow("SELECT * FROM social.posts WHERE id = $1", UUIDType(post_id))
    if not row:
        return OkResponse(data=None)
    return OkResponse(data=dict(row))


@router.patch("/posts/{post_id}/status", response_model=OkResponse)
async def update_post_status(
    post_id: str,
    payload: StatusUpdate,
    _: None = Depends(get_service_auth),
    db: asyncpg.Connection = Depends(get_db),
):
    """Update post status — called by n8n (e.g. set to 'rejected')."""
    from uuid import UUID as UUIDType
    await db.execute(
        "UPDATE social.posts SET status = $2, updated_at = now() WHERE id = $1",
        UUIDType(post_id),
        payload.status,
    )
    return OkResponse(data={"post_id": post_id, "status": payload.status})


@router.post("/trends/nightly-sweep", response_model=OkResponse)
async def trends_nightly_sweep(
    _: None = Depends(get_service_auth),
    db: asyncpg.Connection = Depends(get_db),
):
    """Phase 6 Layer A — tüm sektörler için ücretsiz kaynak tarama.

    Called by n8n `trends-nightly-sweep` workflow (daily cron).
    Her sektör için 9 kaynak paralel toplanır, Claude ile sentezlenir ve
    `sector_trend_cache` tablosuna (layer='A') yazılır.
    """
    from app.services.trends.layer_a import run_nightly_sweep

    result = await run_nightly_sweep(db)
    return OkResponse(data=result)
