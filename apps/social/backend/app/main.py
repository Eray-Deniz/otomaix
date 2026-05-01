from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from app.core.config import settings
from app.core.database import close_pool, get_pool
from app.core.redis import close_redis
from app.routers import ai, auth, autoposting, avatar, billing, brands, calendar, competitors, documents, internal, media_models, posts, product_documents, products, sectors, social, storage, templates as templates_router, trends, webhooks
from app.routers import settings as settings_router

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=0.1,
        environment=settings.ENVIRONMENT,
        integrations=[
            StarletteIntegration(),
            FastApiIntegration(),
        ],
        send_default_pii=False,
    )


def _validate_templates() -> None:
    """Phase 7 — startup validation for template catalog.

    Raises on misconfiguration: wrong count, ID mismatch, missing fields.
    """
    import logging

    from app.core.templates_data import SECTOR_GUIDANCE, TEMPLATES

    logger = logging.getLogger(__name__)
    assert len(TEMPLATES) > 0, f"No templates loaded (got {len(TEMPLATES)})"

    for template_id, template in TEMPLATES.items():
        assert template.id == template_id, f"ID mismatch: {template.id} vs {template_id}"
        assert template.status == "active", f"{template_id} not active"
        assert len(template.sectors) > 0, f"{template_id} has no sectors"
        assert len(template.formFields) > 0, f"{template_id} has no form fields"

    logger.info(
        "Phase 7 templates loaded: %d templates, %d sector guidance entries",
        len(TEMPLATES),
        len(SECTOR_GUIDANCE),
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    _validate_templates()
    await get_pool()
    yield
    await close_pool()
    await close_redis()


app = FastAPI(
    title="Otomaix Social API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.otomaix.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(ai.router)
app.include_router(billing.router)
app.include_router(billing.router_webhooks)
app.include_router(internal.router)
app.include_router(autoposting.router)
app.include_router(avatar.router)
app.include_router(brands.router)
app.include_router(competitors.router)
app.include_router(calendar.router)
app.include_router(documents.router)
app.include_router(media_models.router)
app.include_router(posts.router)
app.include_router(product_documents.router)
app.include_router(products.router)
app.include_router(sectors.router)
app.include_router(settings_router.router)
app.include_router(storage.router)
app.include_router(social.router)
app.include_router(templates_router.router)
app.include_router(trends.router)
app.include_router(webhooks.router)


@app.get("/health")
async def health():
    """Health check — DB ve Redis bağlantısını doğrular. Coolify monitoring için."""
    from datetime import datetime, timezone

    db_status = "ok"
    redis_status = "ok"

    try:
        pool = await get_pool()
        await pool.fetchval("SELECT 1")
    except Exception:
        db_status = "error"

    try:
        from app.core.redis import get_redis
        r = await get_redis()
        await r.ping()
    except Exception:
        redis_status = "error"

    overall = "ok" if db_status == "ok" and redis_status == "ok" else "degraded"
    return {
        "success": overall == "ok",
        "data": {
            "status": overall,
            "db": db_status,
            "redis": redis_status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    }
