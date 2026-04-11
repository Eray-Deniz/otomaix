"""Per-user, per-endpoint rate limiting via Redis INCR + EXPIRE.

Usage:
    from app.core.rate_limit import limiter

    @router.post("/generate", dependencies=[Depends(limiter(20, 3600))])
    async def generate_post(...):
        ...

Redis key pattern:
    otomaix:rl:{endpoint_slug}:{user_id}

If Redis is unavailable, the check is silently skipped (fail-open)
so a Redis outage never blocks legitimate requests.
"""

from fastapi import Depends, HTTPException, Request, status

from app.core.redis import get_redis
from app.core.security import get_current_user


def limiter(max_requests: int, window_seconds: int):
    """
    Return a FastAPI dependency that enforces a per-user rate limit.

    Args:
        max_requests:   Maximum allowed requests in the window.
        window_seconds: Rolling window duration in seconds.
    """
    async def _check(
        request: Request,
        user: dict = Depends(get_current_user),
    ) -> None:
        try:
            redis = await get_redis()
            user_id = user.get("sub", "anon")
            # Build a stable slug from the URL path
            endpoint = request.url.path.strip("/").replace("/", "_")
            key = f"otomaix:rl:{endpoint}:{user_id}"

            count = await redis.incr(key)
            if count == 1:
                # Set TTL only on first increment so we don't accidentally extend it
                await redis.expire(key, window_seconds)

            if count > max_requests:
                ttl = await redis.ttl(key)
                retry_after = max(int(ttl), 1)
                hours = window_seconds // 3600
                window_label = f"{hours} saatte" if hours >= 1 else f"{window_seconds} saniyede"
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "rate_limit",
                        "message": f"Limit aşıldı: {window_label} en fazla {max_requests} istek yapılabilir.",
                        "retry_after": retry_after,
                    },
                    headers={"Retry-After": str(retry_after)},
                )
        except HTTPException:
            raise
        except Exception:
            # Redis unavailable → fail-open, don't block the request
            pass

    return _check
