from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import close_pool, get_pool
from app.core.redis import close_redis
from app.routers import ai, auth, autoposting, avatar, brands, calendar, documents, internal, posts, social, storage, webhooks


@asynccontextmanager
async def lifespan(app: FastAPI):
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
app.include_router(internal.router)
app.include_router(autoposting.router)
app.include_router(avatar.router)
app.include_router(brands.router)
app.include_router(calendar.router)
app.include_router(documents.router)
app.include_router(posts.router)
app.include_router(storage.router)
app.include_router(social.router)
app.include_router(webhooks.router)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"success": True, "data": {"status": "ok"}}
