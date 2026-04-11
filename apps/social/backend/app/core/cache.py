"""Redis cache helpers — get / set / invalidate.

Cache key convention:
  otomaix:social:{endpoint}:{identifier}

All operations silently swallow Redis errors so a Redis outage
never takes down the API — it just bypasses the cache.
"""

import json
from typing import Any

from app.core.redis import get_redis


async def get_cached(key: str) -> Any | None:
    try:
        redis = await get_redis()
        data = await redis.get(key)
        return json.loads(data) if data else None
    except Exception:
        return None


async def set_cached(key: str, value: Any, ttl: int) -> None:
    try:
        redis = await get_redis()
        await redis.setex(key, ttl, json.dumps(value, default=str))
    except Exception:
        pass


async def invalidate(key: str) -> None:
    try:
        redis = await get_redis()
        await redis.delete(key)
    except Exception:
        pass


async def invalidate_pattern(pattern: str) -> None:
    """Delete all keys matching a glob pattern (uses KEYS — OK for low cardinality)."""
    try:
        redis = await get_redis()
        keys = await redis.keys(pattern)
        if keys:
            await redis.delete(*keys)
    except Exception:
        pass
