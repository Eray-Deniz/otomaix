"""Trend analizi endpoint'leri.

GET /trends?brand_id=uuid  → markanın sektörüne ait güncel trendler
POST /trends/{trend_id}/create-post → trend prompt'u ile içerik oluştur
POST /trends/refresh?brand_id=uuid  → önbelleği atlayarak taze veri çek
"""

from uuid import UUID

import asyncpg
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.database import get_db, get_pool
from app.core.security import assert_brand_owned, get_current_user
from app.models.schemas import OkResponse
from app.routers.billing import check_plan_limit, check_trend_quota, increment_trend_usage
from app.services.fal_ai import generate_image
from app.services.trends.layer_a import fetch_sector_layer_a
from app.services.trends.layer_b import fetch_personal_trends
from app.services.trends.layer_c import generate_monthly_report

router = APIRouter(prefix="/trends", tags=["trends"])


# ─── Schemas ────────────────────────────────────────────────────────────────

class TrendCreatePost(BaseModel):
    brand_id: UUID
    suggested_prompt: str
    content_type: str = "image"
    aspect_ratio: str = "1:1"
    platforms: list[str] = []


# ─── Endpoints ──────────────────────────────────────────────────────────────

async def _resolve_brand_sector(db: asyncpg.Connection, brand_id: UUID) -> dict:
    """Brand + sector (yeni sectors tablosu) metadata döndür."""
    row = await db.fetchrow(
        """
        SELECT b.id, b.name, b.sector AS sector_text, b.sector_id,
               s.slug AS sector_slug, s.display_name AS sector_name, s.keywords
        FROM social.brands b
        LEFT JOIN social.sectors s ON s.id = b.sector_id
        WHERE b.id = $1
        """,
        brand_id,
    )
    if not row:
        raise HTTPException(status_code=404, detail="Brand bulunamadı")
    return dict(row)


@router.get("", response_model=OkResponse)
async def get_trends(
    brand_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Markanın sektörüne ait Layer A trendleri (nightly sweep cache)."""
    await assert_brand_owned(db, user, brand_id)
    brand = await _resolve_brand_sector(db, brand_id)

    sector_id = brand.get("sector_id")
    sector_slug = brand.get("sector_slug") or "genel"
    sector_name = brand.get("sector_name") or sector_slug

    trends: list = []
    fetched_at: str | None = None
    if sector_id:
        row = await db.fetchrow(
            """
            SELECT trends, fetched_at
            FROM social.sector_trend_cache
            WHERE sector_id = $1::uuid AND layer = 'A'
            """,
            sector_id,
        )
        if row and row["trends"]:
            raw = row["trends"]
            trends = raw if isinstance(raw, list) else []
        if row and row["fetched_at"]:
            fetched_at = row["fetched_at"].isoformat()

    return OkResponse(
        data={
            "sector": sector_name,
            "sector_slug": sector_slug,
            "trends": trends,
            "count": len(trends),
            "fetched_at": fetched_at,
        }
    )


@router.post("/refresh", response_model=OkResponse)
async def refresh_trends(
    brand_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Layer A pipeline'ı sadece bu markanın sektörü için çalıştır ve cache'i güncelle."""
    await assert_brand_owned(db, user, brand_id)
    brand = await _resolve_brand_sector(db, brand_id)

    sector_id = brand.get("sector_id")
    sector_slug = brand.get("sector_slug") or "genel"
    sector_name = brand.get("sector_name") or sector_slug
    if not sector_id:
        raise HTTPException(
            status_code=400,
            detail="Markanın sektörü atanmamış, önce Marka Ayarları'ndan seçin.",
        )

    sector_dict = {
        "id": str(sector_id),
        "slug": sector_slug,
        "display_name": sector_name,
        "keywords": list(brand.get("keywords") or []),
    }

    result = await fetch_sector_layer_a(sector_dict)
    await db.execute(
        """
        INSERT INTO social.sector_trend_cache
            (sector_id, layer, trends, source_summary, fetched_at)
        VALUES ($1::uuid, 'A', $2, $3, now())
        ON CONFLICT (sector_id, layer) DO UPDATE SET
            trends = EXCLUDED.trends,
            source_summary = EXCLUDED.source_summary,
            fetched_at = now()
        """,
        sector_id,
        result["trends"],
        result["source_summary"],
    )

    return OkResponse(
        data={
            "sector": sector_name,
            "sector_slug": sector_slug,
            "trends": result["trends"],
            "refreshed": True,
            "raw_count": result.get("raw_count", 0),
        }
    )


@router.get("/personal", response_model=OkResponse)
async def get_personal_trends(
    brand_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Layer B — son kişisel trend arama sonuçlarını cache'den oku."""
    await assert_brand_owned(db, user, brand_id)
    row = await db.fetchrow(
        """
        SELECT trends, fetched_at
        FROM social.brand_trend_cache
        WHERE brand_id = $1::uuid
        """,
        brand_id,
    )
    trends: list = []
    fetched_at: str | None = None
    if row and row["trends"]:
        raw = row["trends"]
        trends = raw if isinstance(raw, list) else []
        if row["fetched_at"]:
            fetched_at = row["fetched_at"].isoformat()

    return OkResponse(
        data={
            "trends": trends,
            "count": len(trends),
            "fetched_at": fetched_at,
        }
    )


@router.post("/personal", response_model=OkResponse)
async def personal_trends(
    brand_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Layer B — Serper.dev + Claude Haiku ile kişisel trend araması.

    Aylık kota kontrolüne tabi. ADR-4: Starter 5, Pro 10, Business 20, Agency 50.
    Tetik başı maliyet ~$0.005. Sonuç `brand_trend_cache`'e yazılır.
    """
    await assert_brand_owned(db, user, brand_id)
    quota = await check_trend_quota(user["sub"], "layer_b", db)

    try:
        result = await fetch_personal_trends(db, brand_id)
    except ValueError as e:
        if "SERPER_API_KEY" in str(e):
            raise HTTPException(
                status_code=503,
                detail={"error": "serper_not_configured", "message": "Canlı arama servisi yapılandırılmamış."},
            )
        raise HTTPException(status_code=404, detail=str(e))

    # Maliyet: Serper ~$0.001/arama + Haiku (~$1/M input, $5/M output)
    serper_cost = 0.001 * result["serper_calls"]
    haiku_cost = (result["prompt_tokens"] * 1.0 + result["completion_tokens"] * 5.0) / 1_000_000
    total_cost = round(serper_cost + haiku_cost, 4)

    await increment_trend_usage(user["sub"], "layer_b", total_cost, db)

    return OkResponse(
        data={
            "trends": result["trends"],
            "queries": result["queries"],
            "raw_count": result["raw_count"],
            "quota": {
                "used": quota["used"] + 1,
                "limit": quota["limit"],
                "remaining": quota["remaining"] - 1,
                "plan_id": quota["plan_id"],
            },
            "cost_usd": total_cost,
        }
    )


# ─── Layer C — Aylık Sektör Raporu (Pro+) ──────────────────────────────────

async def _run_report_task(account_id: str, brand_id: UUID) -> None:
    """BackgroundTasks helper — kendi pool bağlantısını alır."""
    pool = await get_pool()
    try:
        async with pool.acquire() as db:
            try:
                result = await generate_monthly_report(db, account_id, brand_id)
                apify_cost = result.get("apify_cost_usd", 0.0)
                claude_cost = result.get("claude_cost_usd", 0.0)
                total = round(apify_cost + claude_cost, 4)
                await increment_trend_usage(account_id, "layer_c", total, db)
            except Exception:
                try:
                    import sentry_sdk
                    sentry_sdk.capture_exception()
                except Exception:
                    pass
    except Exception:
        pass


@router.post("/monthly-report", response_model=OkResponse, status_code=status.HTTP_202_ACCEPTED)
async def monthly_report(
    brand_id: UUID,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Layer C — Pro+ için aylık Apify + Claude sektör raporu üret.

    ADR-5: Starter'a kilitli. ADR-4 kota: Pro 1, Business 3, Agency 10 / ay.
    Uzun sürdüğü için BackgroundTasks ile arka planda çalışır, 202 döner.
    """
    await assert_brand_owned(db, user, brand_id)
    quota = await check_trend_quota(user["sub"], "layer_c", db)
    background_tasks.add_task(_run_report_task, user["sub"], brand_id)
    return OkResponse(
        data={
            "status": "generating",
            "message": "Rapor arka planda üretiliyor. Bittiğinde listede görünecek.",
            "quota": {
                "used": quota["used"] + 1,
                "limit": quota["limit"],
                "remaining": quota["remaining"] - 1,
                "plan_id": quota["plan_id"],
            },
        }
    )


@router.get("/reports", response_model=OkResponse)
async def list_reports(
    brand_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Markaya ait son 20 Layer C raporu."""
    await assert_brand_owned(db, user, brand_id)
    rows = await db.fetch(
        """
        SELECT id::text, status, pdf_url, generated_at, error_message,
               apify_cost_usd, claude_cost_usd
        FROM social.sector_reports
        WHERE brand_id = $1
        ORDER BY generated_at DESC
        LIMIT 20
        """,
        brand_id,
    )
    return OkResponse(data={"reports": [dict(r) for r in rows]})


@router.get("/reports/{report_id}", response_model=OkResponse)
async def get_report(
    report_id: UUID,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Tek rapor detayı — sahiplik JOIN ile kontrol edilir."""
    row = await db.fetchrow(
        """
        SELECT sr.id::text, sr.status, sr.pdf_url, sr.generated_at,
               sr.error_message, sr.apify_cost_usd, sr.claude_cost_usd,
               sr.brand_id::text, sr.sector_id::text
        FROM social.sector_reports sr
        JOIN social.brands b ON b.id = sr.brand_id
        JOIN social.workspace_members wm ON wm.workspace_id = b.workspace_id
        WHERE sr.id = $1 AND wm.account_id = $2::uuid
        """,
        report_id, user["sub"],
    )
    if not row:
        raise HTTPException(status_code=404, detail="Rapor bulunamadı")
    return OkResponse(data=dict(row))


@router.post("/{trend_index}/create-post", response_model=OkResponse, status_code=status.HTTP_201_CREATED)
async def create_post_from_trend(
    trend_index: int,
    payload: TrendCreatePost,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Trend prompt'u kullanarak içerik oluştur ve fal.ai tetikle."""
    await assert_brand_owned(db, user, payload.brand_id)
    await check_plan_limit(user["sub"], "post", db)
    brand = await db.fetchrow(
        "SELECT brand_kit, name, sector FROM social.brands WHERE id = $1",
        payload.brand_id,
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand bulunamadı")

    raw_kit = brand["brand_kit"]
    if raw_kit and isinstance(raw_kit, str):
        import json as _json
        raw_kit = _json.loads(raw_kit)
    brand_kit = dict(raw_kit) if raw_kit else {}

    row = await db.fetchrow(
        """
        INSERT INTO social.posts
            (brand_id, content_type, prompt, aspect_ratio, platforms, status)
        VALUES ($1, $2, $3, $4, $5, 'generating')
        RETURNING *
        """,
        payload.brand_id,
        payload.content_type,
        payload.suggested_prompt,
        payload.aspect_ratio,
        payload.platforms,
    )
    post = dict(row)

    try:
        fal_job_id = await generate_image(
            payload.suggested_prompt,
            payload.aspect_ratio,
            brand_kit,
        )
        await db.execute(
            "UPDATE social.posts SET fal_job_id = $2 WHERE id = $1",
            post["id"],
            fal_job_id,
        )
        post["fal_job_id"] = fal_job_id
    except Exception:
        pass  # Webhook üretim başarısızlığını yönetir

    return OkResponse(data={"post_id": str(post["id"]), "status": "generating"})
