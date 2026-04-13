from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.security import get_current_user, get_current_user_optional, get_service_auth
from app.models.schemas import FacelessVideoGenerate, OkResponse, PostCreate, PostGenerate
from app.services.document_processor import get_document_context
from app.services.fal_ai import generate_image
from app.services.faceless_video import TURKISH_VOICES, run_faceless_video_pipeline

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


def _build_special_day_prompt(payload: PostGenerate, brand: object, brand_kit: dict) -> str:
    """Build an fal.ai image prompt for special day / holiday content."""
    holiday = payload.special_day_name or "Özel Gün"
    brand_name = brand["name"] or ""
    sector = brand["sector"] or ""
    colors = ", ".join(brand_kit.get("colors", []))
    style = brand_kit.get("style", "modern, professional")
    extra = f" Additional context: {payload.prompt}" if payload.prompt else ""

    category_hints = {
        "religious": "warm, festive, respectful, traditional Turkish aesthetic",
        "national": "patriotic, proud, celebratory, Turkish colors red and white",
        "commercial": "vibrant, promotional, eye-catching, commercial photography style",
    }
    mood = category_hints.get(payload.special_day_category or "", "festive, celebratory, warm")

    return (
        f"Social media post image for {holiday}. "
        f"Brand: {brand_name}, sector: {sector}. "
        f"Visual mood: {mood}. "
        f"Brand colors: {colors}. Style: {style}. "
        f"Professional, high quality, suitable for {', '.join(payload.platforms) or 'social media'}."
        f"{extra}"
    )


def _build_quote_prompt(payload: PostGenerate, brand: dict, brand_kit: dict) -> str:
    """Build an fal.ai image prompt for quote card content."""
    quote = payload.quote_text or ""
    author = payload.quote_author or ""
    brand_name = brand["name"] or ""
    colors = ", ".join(brand_kit.get("colors", []))
    style = brand_kit.get("style", "minimalist, modern")

    return (
        f"Elegant quote card for social media. "
        f"Quote text prominently displayed: \"{quote}\""
        + (f" — {author}" if author else "") +
        f". Brand: {brand_name}. Brand colors: {colors}. "
        f"Style: {style}, clean typography, strong visual hierarchy. "
        f"The quote is the hero element. Minimal background, professional design."
    )


@router.post(
    "/generate",
    response_model=OkResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(limiter(20, 3600))],  # 20/saat
)
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

    # Build prompt based on content type
    if payload.content_type == "special_day":
        enriched_prompt = _build_special_day_prompt(payload, brand, brand_kit)
    elif payload.content_type == "quote":
        enriched_prompt = _build_quote_prompt(payload, dict(brand), brand_kit)
    else:
        enriched_prompt = await _build_prompt_with_rag(payload, brand, brand_kit, db)

    # Default caption for quote posts (the quote text itself)
    default_caption: str | None = None
    if payload.content_type == "quote" and payload.quote_text:
        author_part = f"\n\n— {payload.quote_author}" if payload.quote_author else ""
        default_caption = f'"{payload.quote_text}"{author_part}'

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
        payload.prompt or payload.special_day_name or payload.quote_text,
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

    return OkResponse(data={
        "post_id": str(post["id"]),
        "status": "generating",
        "caption": default_caption,
    })


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


@router.post("/{post_id}/request-approval", response_model=OkResponse)
async def request_approval(
    post_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Telegram onay akışını başlatır — n8n telegram-content-approval webhook'unu tetikler."""
    import httpx
    from app.core.config import settings

    # Post'u al ve kullanıcıya ait olduğunu doğrula
    post = await db.fetchrow(
        """
        SELECT p.id, p.brand_id, p.status
        FROM social.posts p
        JOIN social.brands b ON b.id = p.brand_id
        JOIN social.workspaces w ON w.id = b.workspace_id
        WHERE p.id = $1 AND w.account_id = $2
        """,
        post_id, user["sub"],
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post bulunamadı")

    if post["status"] not in ("ready", "failed", "rejected"):
        raise HTTPException(
            status_code=400,
            detail="Sadece 'Hazır', 'Başarısız' veya 'Reddedildi' durumundaki içerikler onaya gönderilebilir",
        )

    # Telegram bilgilerini autoposting_configs'ten al
    config = await db.fetchrow(
        "SELECT telegram_chat_id FROM social.autoposting_configs WHERE brand_id = $1",
        post["brand_id"],
    )
    if not config or not config["telegram_chat_id"]:
        raise HTTPException(
            status_code=400,
            detail="Bu marka için Telegram konfigürasyonu bulunamadı. Otomatik Yayın ayarlarından Telegram bilgilerini girin.",
        )

    # Post durumunu 'reviewing' yap
    await db.execute(
        "UPDATE social.posts SET status = 'reviewing' WHERE id = $1",
        post_id,
    )

    # n8n webhook'unu tetikle (fire-and-forget)
    n8n_url = f"{settings.N8N_BASE_URL}/webhook/telegram-content-approval"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(n8n_url, json={
                "post_id": str(post_id),
                "brand_id": str(post["brand_id"]),
                "telegram_chat_id": config["telegram_chat_id"],
            })
    except Exception:
        pass  # fire-and-forget — n8n ulaşılamasa bile devam et

    return OkResponse(data={"status": "reviewing"})


@router.post(
    "/generate-faceless-video",
    response_model=OkResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(limiter(20, 3600))],  # 20/saat (image + video birlikte sayılır)
)
async def generate_faceless_video(
    payload: FacelessVideoGenerate,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Faceless video pipeline: script üret → TTS → fal.ai arka plan videosu."""
    brand = await db.fetchrow(
        "SELECT brand_kit, name, sector FROM social.brands WHERE id = $1", payload.brand_id
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand_kit = dict(brand["brand_kit"]) if brand["brand_kit"] else {}
    brand_kit["sector"] = brand["sector"] or ""

    post = await run_faceless_video_pipeline(
        brand_id=payload.brand_id,
        prompt=payload.prompt,
        voice=payload.voice,
        aspect_ratio=payload.aspect_ratio,
        brand_kit=brand_kit,
        brand_name=brand["name"],
        db=db,
    )
    return OkResponse(data={
        "post_id": str(post["id"]),
        "script": post["script"],
        "audio_url": post["audio_url"],
        "duration_estimate": post["duration_estimate"],
        "status": "generating",
    })


@router.get("/voices/turkish", response_model=OkResponse)
async def list_turkish_voices():
    """Mevcut Türkçe TTS ses seçeneklerini döndür. (public endpoint — statik liste)"""
    return OkResponse(data=TURKISH_VOICES)
