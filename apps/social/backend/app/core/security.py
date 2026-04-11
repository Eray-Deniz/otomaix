import hashlib
import json
import time

import httpx
import jwt as pyjwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

_bearer = HTTPBearer(auto_error=False)
_jwks_cache: dict | None = None
_jwks_fetched_at: float = 0.0
_JWKS_TTL = 3600.0  # re-fetch JWKS every hour


async def _get_jwks() -> dict:
    global _jwks_cache, _jwks_fetched_at
    now = time.monotonic()
    if _jwks_cache is None or (now - _jwks_fetched_at) > _JWKS_TTL:
        url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            _jwks_cache = resp.json()
            _jwks_fetched_at = now
    return _jwks_cache


def _find_key(jwks: dict, kid: str) -> dict | None:
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    return None


def _jwk_to_public_key(jwk: dict):
    """Convert a JWK dict to a PyJWT-compatible public key object."""
    kty = jwk.get("kty")
    jwk_json = json.dumps(jwk)
    if kty == "EC":
        return pyjwt.algorithms.ECAlgorithm.from_jwk(jwk_json)
    if kty == "RSA":
        return pyjwt.algorithms.RSAAlgorithm.from_jwk(jwk_json)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unsupported key type")


async def _decode_token(token: str) -> dict:
    jwks = await _get_jwks()
    headers = pyjwt.get_unverified_header(token)
    jwk = _find_key(jwks, headers.get("kid", ""))
    if not jwk:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token key")
    try:
        public_key = _jwk_to_public_key(jwk)
        payload = pyjwt.decode(
            token,
            public_key,
            algorithms=["RS256", "ES256"],
            audience="authenticated",
            options={"verify_exp": True},
        )
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except pyjwt.PyJWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return payload


async def _decode_token_cached(token: str) -> dict:
    """Decode JWT with a 300s Redis cache to avoid repeated JWKS lookups."""
    from app.core.redis import get_redis

    token_hash = hashlib.sha256(token.encode()).hexdigest()[:32]
    cache_key = f"otomaix:social:user:{token_hash}"

    try:
        redis = await get_redis()
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception:
        pass  # Redis unavailable — fall through to normal decode

    payload = await _decode_token(token)

    try:
        redis = await get_redis()
        await redis.setex(cache_key, 300, json.dumps(payload))
    except Exception:
        pass

    return payload


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict:
    """Require a valid Supabase JWT. Returns decoded payload with 'sub' and 'email'."""
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return await _decode_token_cached(credentials.credentials)


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict | None:
    """Optional JWT — returns None for unauthenticated requests."""
    if not credentials:
        return None
    try:
        return await _decode_token_cached(credentials.credentials)
    except HTTPException:
        return None


def get_service_auth(x_internal_key: str | None = Header(default=None)) -> None:
    """Validate X-Internal-Key header for n8n → backend service calls."""
    if not settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=503, detail="Internal API key not configured")
    if x_internal_key != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid internal API key")
