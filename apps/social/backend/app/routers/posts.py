import asyncio
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from app.core.caption_generator import generate_captions
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.security import (
    assert_brand_owned,
    assert_post_owned,
    get_current_user,
    get_current_user_optional,
    get_service_auth,
)
from app.core.templates_data import SECTOR_GUIDANCE, get_template_by_id
from app.models.schemas import (
    FacelessVideoGenerate,
    OkResponse,
    PostCreate,
    PostGenerate,
    PostUpdate,
)
from app.routers.billing import check_plan_limit
from app.services.document_processor import get_document_context, get_product_document_context
from app.services.fal_ai import SUPPORTED_ASPECT_RATIOS, generate_image, generate_image_edit
from app.services.faceless_video import (
    DEFAULT_MAX_DURATION,
    PLATFORM_MAX_DURATION,
    SUPPORTED_FACELESS_RATIOS,
    TURKISH_VOICES,
    run_faceless_stage1,
    run_faceless_stage2,
    run_faceless_video_pipeline,
)

router = APIRouter(prefix="/posts", tags=["posts"])


from app.core.utils import parse_brand_kit as _parse_brand_kit
from app.routers.ai import CATEGORY_TR


async def _build_image_prompt(
    payload: PostGenerate,
    brand: object,
    brand_kit: dict,
    db,
) -> str:
    """Build fal.ai image prompt.

    Template varsa: payload.image_prompt (Sprint 4 caption endpoint'inden gelen)
    kullanılır; yoksa form_fields'ten basit image prompt inşa edilir.
    Template yoksa: legacy path (special_day/quote hariç tüm mevcut akışlar).
    """
    if payload.template_id:
        template = get_template_by_id(payload.template_id)
        if not template:
            return payload.prompt or ""

        # Akış C'de caption endpoint image_prompt üretir, payload'a gelir
        if payload.image_prompt:
            return payload.image_prompt

        # Fallback: form_fields'tan basit image prompt inşa et
        parts = [f"{template.name} — sosyal medya görseli"]
        if payload.template_fields:
            for field in template.formFields:
                value = payload.template_fields.get(field.id)
                if value is not None and value != "":
                    parts.append(f"{field.label}: {value}")
        return " ".join(parts)

    # Legacy path (no template)
    return await _build_prompt_with_rag_legacy(payload, brand, brand_kit, db)


async def _build_prompt_with_rag_legacy(
    payload: PostGenerate,
    brand: object,
    brand_kit: dict,
    db,
) -> str:
    """Legacy prompt builder (Sprint 3 öncesi `_build_prompt_with_rag`'ın birebir kopyası).

    Template olmayan akışlar için çalışmaya devam eder:
    - Serbest içerik (template_id=None, prompt var)
    - special_day, quote (zaten kendi fonksiyonlarını kullanıyor, buraya düşmez)
    - /internal/autoposting/trigger n8n akışı
    """
    base_prompt = payload.prompt or ""
    category_tr = CATEGORY_TR.get(payload.content_category or "", "")

    # Doküman seçilmemişse bile kategoriyi prompt'a ekle
    if not payload.document_ids:
        if category_tr and base_prompt:
            return f"{category_tr} odaklı görsel: {base_prompt}"
        elif category_tr:
            return f"{category_tr} odaklı sosyal medya görseli"
        return base_prompt

    doc_context = await get_document_context(payload.document_ids, base_prompt, db)
    if not doc_context:
        if category_tr and base_prompt:
            return f"{category_tr} odaklı görsel: {base_prompt}"
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
- İçerik Kategorisi: {category_tr}
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


class GenerateCaptionRequest(BaseModel):
    """Phase 7 Sprint 4 — POST /posts/generate-caption body."""

    brand_id: UUID
    template_id: str | None = None
    template_fields: dict | None = None
    user_prompt: str | None = None
    document_ids: list[UUID] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)
    product_id: UUID | None = None
    content_type: str | None = None
    voice: str | None = None


@router.post(
    "/generate-caption",
    response_model=OkResponse,
    dependencies=[Depends(limiter(30, 3600))],  # 30/saat
)
async def generate_caption(
    payload: GenerateCaptionRequest,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Claude ile caption + image_prompt + hashtag üret (Akış C parçası)."""
    await assert_brand_owned(db, user, payload.brand_id)

    brand = await db.fetchrow(
        """
        SELECT b.*, s.slug AS sector_slug
        FROM social.brands b
        LEFT JOIN social.sectors s ON b.sector_id = s.id
        WHERE b.id = $1
        """,
        payload.brand_id,
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand_kit = _parse_brand_kit(brand["brand_kit"])

    template = None
    if payload.template_id:
        template = get_template_by_id(payload.template_id)
        if not template:
            raise HTTPException(
                status_code=400,
                detail=f"Template {payload.template_id} not found",
            )

    product = None
    if payload.product_id:
        product_row = await db.fetchrow(
            """
            SELECT id, name, description, tags, image_url
            FROM social.brand_products
            WHERE id = $1 AND brand_id = $2
            """,
            payload.product_id,
            payload.brand_id,
        )
        if not product_row:
            raise HTTPException(status_code=404, detail="Ürün bulunamadı")
        product = dict(product_row)

    base_query = payload.user_prompt or (
        template.name if template else "social media caption"
    )

    rag_parts: list[str] = []
    if payload.document_ids:
        doc_context = await get_document_context(payload.document_ids, base_query, db)
        if doc_context:
            rag_parts.append(doc_context)
    if payload.product_id:
        product_doc_context = await get_product_document_context(
            [payload.product_id], base_query, db
        )
        if product_doc_context:
            rag_parts.append(product_doc_context)
    rag_context = "\n\n---\n\n".join(rag_parts) if rag_parts else None

    result = await generate_captions(
        brand=dict(brand),
        brand_kit=brand_kit,
        template=template,
        template_fields=payload.template_fields,
        user_prompt=payload.user_prompt,
        rag_context=rag_context,
        platforms=payload.platforms,
        product=product,
        content_type=payload.content_type,
    )

    return OkResponse(data=result)


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
    await assert_brand_owned(db, user, payload.brand_id)
    await check_plan_limit(user["sub"], "post", db)
    if payload.aspect_ratio not in SUPPORTED_ASPECT_RATIOS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Desteklenmeyen en-boy oranı: {payload.aspect_ratio!r}. "
                f"Geçerli değerler: {', '.join(SUPPORTED_ASPECT_RATIOS)}"
            ),
        )
    brand = await db.fetchrow(
        "SELECT brand_kit, name, sector FROM social.brands WHERE id = $1", payload.brand_id
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand_kit = _parse_brand_kit(brand["brand_kit"])

    # Phase 9 Sprint 6 — Ürün/Hizmet image-edit routing
    # product_id set ise ürünü markaya ait mi kontrol et; image_url varsa image-edit,
    # yoksa FLUX text-to-image fallback (S4 kararı).
    product_row = None
    if payload.product_id:
        product_row = await db.fetchrow(
            "SELECT id, image_url FROM social.brand_products WHERE id = $1 AND brand_id = $2",
            payload.product_id,
            payload.brand_id,
        )
        if not product_row:
            raise HTTPException(status_code=404, detail="Ürün bulunamadı")

    # Build prompt based on content type
    if payload.content_type == "special_day":
        enriched_prompt = _build_special_day_prompt(payload, brand, brand_kit)
    elif payload.content_type == "quote":
        enriched_prompt = _build_quote_prompt(payload, dict(brand), brand_kit)
    elif payload.image_prompt:
        # Phase 7 Sprint 4/5 — Akış C (unified): caption endpoint'ten image_prompt geldiyse
        # template_id olsun olmasın bypass et (free mode da caption-first akışı kullanır)
        enriched_prompt = payload.image_prompt
    else:
        enriched_prompt = await _build_image_prompt(payload, brand, brand_kit, db)

    # Carousel — çoklu slide prompt dizisi
    slides_data: list[dict] | None = None
    if payload.content_type == "carousel" and payload.image_prompts:
        slides_data = [
            {"order": i + 1, "image_prompt": p, "fal_job_id": None, "image_url": None}
            for i, p in enumerate(payload.image_prompts)
        ]

    # Default caption for quote posts (the quote text itself)
    default_caption: str | None = None
    if payload.content_type == "quote" and payload.quote_text:
        author_part = f"\n\n— {payload.quote_author}" if payload.quote_author else ""
        default_caption = f'"{payload.quote_text}"{author_part}'

    # Phase 7 Sprint 4 — platform_captions'dan caption/hashtags backward-fill
    # Beklenen şekil: {"default": "...", "platforms": {"instagram": {"caption":"...", "hashtags":[...]}}}
    caption_value: str | None = default_caption
    hashtags_value: list[str] | None = None
    if payload.platform_captions:
        pc = payload.platform_captions
        caption_value = pc.get("default") or default_caption
        platforms_map = pc.get("platforms") or {}
        if not caption_value and platforms_map:
            first_platform = next(iter(platforms_map.values()), None)
            if isinstance(first_platform, dict):
                caption_value = first_platform.get("caption")

        hashtag_set: set[str] = set()
        for platform_data in platforms_map.values():
            if isinstance(platform_data, dict):
                for h in platform_data.get("hashtags", []) or []:
                    hashtag_set.add(h)
        if hashtag_set:
            hashtags_value = list(hashtag_set)

    # Phase 7 — template_id varsa content_category'yi boşalt (yeni akış legacy ile karışmasın)
    effective_category = None if payload.template_id else payload.content_category

    row = await db.fetchrow(
        """
        INSERT INTO social.posts
            (brand_id, content_type, content_category, prompt, user_text,
             document_ids, aspect_ratio, platforms, status,
             template_id, template_fields, platform_captions,
             caption, hashtags, use_logo_overlay, image_text_fields,
             product_id, slides)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'generating',
                $9, $10, $11, $12, $13, $14, $15, $16, $17)
        RETURNING *
        """,
        payload.brand_id,
        payload.content_type,
        effective_category,
        payload.prompt or payload.special_day_name or payload.quote_text,
        payload.user_text,
        [str(d) for d in payload.document_ids] if payload.document_ids else None,
        payload.aspect_ratio,
        payload.platforms,
        payload.template_id,
        payload.template_fields,
        payload.platform_captions,
        caption_value,
        hashtags_value,
        payload.use_logo_overlay,
        payload.image_text_fields,
        payload.product_id,
        slides_data,
    )
    post = dict(row)

    import logging
    _logger = logging.getLogger(__name__)

    if slides_data:
        # Phase 12 — Carousel: parallel fal.ai submissions for each slide
        try:
            tasks = []
            for slide in slides_data:
                sp = slide["image_prompt"]
                if product_row and product_row["image_url"]:
                    tasks.append(generate_image_edit(sp, [product_row["image_url"]], brand_kit))
                else:
                    tasks.append(generate_image(sp, payload.aspect_ratio, brand_kit))
            job_ids = await asyncio.gather(*tasks, return_exceptions=True)
            has_failure = any(isinstance(jid, Exception) for jid in job_ids)
            if has_failure:
                for i, jid in enumerate(job_ids):
                    if isinstance(jid, Exception):
                        _logger.error(f"Carousel slide {i+1} fal.ai submit failed: {jid}", exc_info=jid)
                await db.execute(
                    "UPDATE social.posts SET status = 'failed', updated_at = now() WHERE id = $1",
                    post["id"],
                )
            else:
                for i, jid in enumerate(job_ids):
                    slides_data[i]["fal_job_id"] = str(jid)
                await db.execute(
                    "UPDATE social.posts SET slides = $2 WHERE id = $1",
                    post["id"],
                    slides_data,
                )
        except Exception as e:
            _logger.error(f"Carousel fal.ai submission failed for post {post['id']}: {e}", exc_info=True)
    else:
        # Single image flow
        try:
            if product_row and product_row["image_url"]:
                fal_job_id = await generate_image_edit(
                    enriched_prompt, [product_row["image_url"]], brand_kit
                )
            else:
                fal_job_id = await generate_image(enriched_prompt, payload.aspect_ratio, brand_kit)
            await db.execute(
                "UPDATE social.posts SET fal_job_id = $2 WHERE id = $1",
                post["id"],
                fal_job_id,
            )
            post["fal_job_id"] = fal_job_id
        except Exception as e:
            _logger.error(f"fal.ai generate_image failed for post {post['id']}: {e}", exc_info=True)

    return OkResponse(data={
        "post_id": str(post["id"]),
        "status": "generating",
        "caption": caption_value,
        "slide_count": len(slides_data) if slides_data else None,
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
    if user:
        await assert_post_owned(db, user, post_id)
    post = await db.fetchrow(
        "SELECT p.*, b.brand_kit FROM social.posts p JOIN social.brands b ON b.id = p.brand_id WHERE p.id = $1",
        post_id,
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    brand_kit = _parse_brand_kit(post["brand_kit"])
    aspect_ratio = post["aspect_ratio"] or "1:1"
    if aspect_ratio not in SUPPORTED_ASPECT_RATIOS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Desteklenmeyen en-boy oranı: {aspect_ratio!r}. "
                f"Geçerli değerler: {', '.join(SUPPORTED_ASPECT_RATIOS)}"
            ),
        )
    await db.execute(
        "UPDATE social.posts SET status = 'generating', output_url = NULL, thumbnail_url = NULL WHERE id = $1",
        post_id,
    )

    try:
        fal_job_id = await generate_image(post["prompt"] or "", aspect_ratio, brand_kit)
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
    await assert_brand_owned(db, user, payload.brand_id)
    await check_plan_limit(user["sub"], "post", db)
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
    await assert_brand_owned(db, user, brand_id)
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


@router.get("/stats/summary", response_model=OkResponse)
async def posts_stats_summary(
    brand_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Lightweight counts for dashboard stat cards."""
    await assert_brand_owned(db, user, brand_id)
    row = await db.fetchrow(
        """
        SELECT
          COUNT(*) FILTER (WHERE created_at >= date_trunc('month', now())) AS generated_this_month,
          COUNT(*) FILTER (WHERE status = 'published') AS published_total
        FROM social.posts
        WHERE brand_id = $1
        """,
        brand_id,
    )
    return OkResponse(data={
        "generated_this_month": int(row["generated_this_month"] or 0),
        "published_total": int(row["published_total"] or 0),
    })


@router.get("/{post_id}", response_model=OkResponse)
async def get_post(
    post_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Get a single post by id with per-platform publication rows."""
    row = await assert_post_owned(db, user, post_id)
    pub_rows = await db.fetch(
        """
        SELECT platform, status, external_id, error_message, published_at, updated_at
        FROM social.post_publications
        WHERE post_id = $1
        ORDER BY platform
        """,
        post_id,
    )
    data = dict(row) if not isinstance(row, dict) else row
    data["publications"] = [dict(r) for r in pub_rows]
    return OkResponse(data=data)


@router.patch("/{post_id}", response_model=OkResponse)
async def update_post(
    post_id: UUID,
    payload: PostUpdate,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Update editable post fields (caption, hashtags)."""
    await assert_post_owned(db, user, post_id)
    updates = payload.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    fields = ", ".join(f"{k} = ${i + 2}" for i, k in enumerate(updates))
    values = list(updates.values())
    row = await db.fetchrow(
        f"UPDATE social.posts SET {fields}, updated_at = now() WHERE id = $1 RETURNING *",
        post_id,
        *values,
    )
    return OkResponse(data=dict(row))


@router.post("/{post_id}/publish", response_model=OkResponse)
async def publish_post(
    post_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Trigger publishing a post to its configured platforms."""
    post = await assert_post_owned(db, user, post_id)
    if not post.get("output_url"):
        raise HTTPException(status_code=409, detail="Post içeriği henüz üretilmemiş")
    if post.get("status") in ("draft", "generating"):
        raise HTTPException(status_code=409, detail="Post henüz hazır değil")
    from app.services.upload_post import publish_post as svc_publish

    result = await svc_publish(post_id, db)
    return OkResponse(data=result)


@router.post("/{post_id}/retry", response_model=OkResponse)
async def retry_publish(
    post_id: UUID,
    platform: str,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Başarısız olan tek bir platform yayınını yeniden dene."""
    await assert_post_owned(db, user, post_id)
    from app.services.upload_post import publish_post as svc_publish

    result = await svc_publish(post_id, db, only_platforms=[platform])
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

    # Telegram bilgilerini workspace ayarlarından al
    workspace = await db.fetchrow(
        """
        SELECT w.telegram_bot_token, w.telegram_chat_id
        FROM social.workspaces w
        WHERE w.account_id = $1
        """,
        user["sub"],
    )
    if not workspace or not workspace["telegram_chat_id"] or not workspace["telegram_bot_token"]:
        raise HTTPException(
            status_code=400,
            detail="Telegram konfigürasyonu bulunamadı. Ayarlar sayfasından Bot Token ve Chat ID girin.",
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
                "telegram_bot_token": workspace["telegram_bot_token"],
                "telegram_chat_id": workspace["telegram_chat_id"],
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
    """Faceless video pipeline: script → TTS → fal.ai arka plan videosu."""
    await assert_brand_owned(db, user, payload.brand_id)
    if payload.aspect_ratio not in SUPPORTED_FACELESS_RATIOS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Desteklenmeyen en-boy oranı: '{payload.aspect_ratio}'. "
                f"Geçerli değerler: {', '.join(SUPPORTED_FACELESS_RATIOS)}"
            ),
        )
    await check_plan_limit(user["sub"], "video", db)
    await check_plan_limit(user["sub"], "post", db)
    brand = await db.fetchrow(
        "SELECT brand_kit, name, sector, description, website_url FROM social.brands WHERE id = $1", payload.brand_id
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand_kit = _parse_brand_kit(brand["brand_kit"])
    brand_kit["sector"] = brand["sector"] or ""

    rag_context: str | None = None
    if payload.document_ids:
        rag_context = await get_document_context(payload.document_ids, payload.prompt, db)

    # Seçili platformların en kısıtlayıcı süre limitini al
    max_duration = DEFAULT_MAX_DURATION
    if payload.platforms:
        durations = [PLATFORM_MAX_DURATION.get(p, DEFAULT_MAX_DURATION) for p in payload.platforms]
        max_duration = min(durations)

    sector_slug = brand["sector"] or ""
    sector_guidance_text = SECTOR_GUIDANCE.get(sector_slug, "")

    post = await run_faceless_video_pipeline(
        brand_id=payload.brand_id,
        prompt=payload.prompt,
        script=payload.script or "",
        voice=payload.voice,
        aspect_ratio=payload.aspect_ratio,
        brand_kit=brand_kit,
        brand_name=brand["name"],
        brand_description=brand["description"] or "",
        website_url=brand["website_url"] or "",
        sector_guidance=sector_guidance_text,
        rag_context=rag_context,
        platform_captions=payload.platform_captions,
        template_id=payload.template_id,
        template_fields=payload.template_fields,
        intro_position=payload.intro_position,
        product_id=payload.product_id,
        max_duration=max_duration,
        db=db,
    )
    return OkResponse(data={
        "post_id": str(post["id"]),
        "script": post["script"],
        "audio_url": post["audio_url"],
        "duration_estimate": post["duration_estimate"],
        "status": "generating",
    })


@router.post(
    "/generate-faceless-stage1",
    response_model=OkResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(limiter(60, 3600))],
)
async def generate_faceless_stage1(
    payload: FacelessVideoGenerate,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Stage 1: post oluştur (status='awaiting_approval') + TTS + Nano Banana 2 still.

    Kota burada düşer (video + post). Onay/Reject endpoint'leri sonra çağrılır.
    """
    await assert_brand_owned(db, user, payload.brand_id)
    if payload.aspect_ratio not in SUPPORTED_FACELESS_RATIOS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Desteklenmeyen en-boy oranı: '{payload.aspect_ratio}'. "
                f"Geçerli değerler: {', '.join(SUPPORTED_FACELESS_RATIOS)}"
            ),
        )
    if not (payload.script or "").strip():
        raise HTTPException(
            status_code=400,
            detail="Script boş — önce /posts/generate-caption ile script üretin.",
        )

    # Kullanıcı kararı: kota Stage 1'de düşer, reject'te geri verilmez
    await check_plan_limit(user["sub"], "video", db)
    await check_plan_limit(user["sub"], "post", db)

    brand = await db.fetchrow(
        "SELECT brand_kit, name, sector, description FROM social.brands WHERE id = $1",
        payload.brand_id,
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand_kit = _parse_brand_kit(brand["brand_kit"])
    brand_kit["sector"] = brand["sector"] or ""

    max_duration = DEFAULT_MAX_DURATION
    if payload.platforms:
        durations = [PLATFORM_MAX_DURATION.get(p, DEFAULT_MAX_DURATION) for p in payload.platforms]
        max_duration = min(durations)

    # Ürün bilgisi + ürün dokümanları → görsel prompt'una bağlam olarak gider.
    # Brief ya da script, RAG sorgusu için kullanılır.
    product_info = ""
    product_doc_context = ""
    if payload.product_id:
        product_row = await db.fetchrow(
            """
            SELECT name, description, tags
            FROM social.brand_products
            WHERE id = $1 AND brand_id = $2
            """,
            payload.product_id, payload.brand_id,
        )
        if product_row:
            parts: list[str] = []
            if product_row["name"]:
                parts.append(f"Name: {product_row['name']}")
            if product_row["description"]:
                parts.append(f"Description: {product_row['description']}")
            tags = product_row["tags"] or []
            if isinstance(tags, list) and tags:
                parts.append(f"Tags: {', '.join(str(t) for t in tags)}")
            product_info = "\n".join(parts)

        rag_query = (payload.visual_brief or payload.script or payload.prompt or "").strip()
        if rag_query:
            ctx = await get_product_document_context(
                [payload.product_id], rag_query, db,
            )
            if ctx:
                product_doc_context = ctx

    try:
        stage1 = await run_faceless_stage1(
            brand_id=payload.brand_id,
            prompt=payload.prompt,
            script=payload.script,
            voice=payload.voice,
            aspect_ratio=payload.aspect_ratio,
            brand_kit=brand_kit,
            brand_name=brand["name"],
            brand_description=brand["description"] or "",
            platform_captions=payload.platform_captions,
            template_id=payload.template_id,
            template_fields=payload.template_fields,
            intro_position=payload.intro_position,
            product_id=payload.product_id,
            max_duration=max_duration,
            user_brief=payload.visual_brief or "",
            product_info=product_info,
            product_doc_context=product_doc_context,
            db=db,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return OkResponse(data={
        "post_id": str(stage1["post_id"]),
        "script": stage1["script"],
        "audio_url": stage1["audio_url"],
        "still_image_url": stage1["still_image_url"],
        "duration_estimate": stage1["duration_estimate"],
        "aspect_ratio": stage1["aspect_ratio"],
        "status": "awaiting_approval",
    })


@router.post(
    "/{post_id}/approve-faceless",
    response_model=OkResponse,
    dependencies=[Depends(limiter(30, 3600))],
)
async def approve_faceless_video(
    post_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Stage 2 tetikle: 'awaiting_approval' post'unu Wan I2V'ye gönder.

    Kota Stage 1'de düşmüştü — burada düşmez.
    """
    row = await assert_post_owned(db, user, post_id)
    if row["status"] != "awaiting_approval":
        raise HTTPException(
            status_code=400,
            detail=f"Post status='{row['status']}' — onay beklenmiyor.",
        )

    try:
        result = await run_faceless_stage2(post_id=post_id, db=db)
    except (LookupError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Stage 2 başlatılamadı: {exc}") from exc

    return OkResponse(data={
        "post_id": str(result["post_id"]),
        "fal_job_id": result["fal_job_id"],
        "status": result["status"],
    })


@router.post(
    "/{post_id}/reject-faceless",
    response_model=OkResponse,
    dependencies=[Depends(limiter(60, 3600))],
)
async def reject_faceless_video(
    post_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """'awaiting_approval' post'unu DELETE et + R2'deki audio'yu temizle.

    Kullanıcı kararı: post tamamen silinir, kota geri verilmez.
    """
    row = await assert_post_owned(db, user, post_id)
    if row["status"] != "awaiting_approval":
        raise HTTPException(
            status_code=400,
            detail=f"Post status='{row['status']}' — reddedilemez.",
        )

    # R2 audio temizliği (best-effort)
    try:
        from app.services.storage import r2
        audio_path = f"brands/{row['brand_id']}/posts/audio/{post_id}.mp3"
        timestamps_path = f"brands/{row['brand_id']}/posts/audio/{post_id}_timestamps.json"
        r2.delete(audio_path)
        r2.delete(timestamps_path)
    except Exception:  # noqa: BLE001
        pass

    await db.execute("DELETE FROM social.posts WHERE id = $1", post_id)
    return OkResponse(data={"ok": True, "post_id": str(post_id)})


@router.get("/voices/turkish", response_model=OkResponse)
async def list_turkish_voices():
    """Mevcut Türkçe TTS ses seçeneklerini döndür. (public endpoint — statik liste)"""
    return OkResponse(data=TURKISH_VOICES)
