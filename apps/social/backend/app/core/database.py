import json

import asyncpg
from app.core.config import settings

_pool: asyncpg.Pool | None = None


async def _init_connection(conn: asyncpg.Connection) -> None:
    """Register jsonb/json codecs so asyncpg returns dicts instead of strings.

    asyncpg default jsonb dönüşünü str olarak yapar — bu yüzden `dict(row)`
    sonrası `row['analysis_data']` bir JSON string oluyordu ve frontend
    `data?.website` gibi property access'lerde hep undefined alıyordu. Codec
    register edildiğinde asyncpg otomatik json.loads uygular.

    Mevcut INSERT/UPDATE kodları `$N::jsonb` cast ile text parametre geçirdiği
    için codec encoder tetiklenmez — geriye uyumlu.
    """
    await conn.set_type_codec(
        "jsonb",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
    )
    await conn.set_type_codec(
        "json",
        encoder=json.dumps,
        decoder=json.loads,
        schema="pg_catalog",
    )


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(
            settings.DATABASE_URL,
            min_size=5,
            max_size=20,
            init=_init_connection,
        )
    return _pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def get_db():
    """FastAPI dependency — yields a connection from the pool."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn
