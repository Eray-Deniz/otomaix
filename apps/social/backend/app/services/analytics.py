"""
PostHog server-side analytics.
All functions are no-ops if POSTHOG_API_KEY is not set.
"""
import logging
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

_client = None


def _get_client():
    global _client
    if not settings.POSTHOG_API_KEY:
        return None
    if _client is None:
        try:
            from posthog import Posthog  # type: ignore
            _client = Posthog(
                settings.POSTHOG_API_KEY,
                host=settings.POSTHOG_HOST or "https://eu.posthog.com",
            )
        except Exception as e:
            logger.warning(f"PostHog init failed: {e}")
    return _client


def capture(distinct_id: str, event: str, properties: Optional[dict] = None) -> None:
    """Fire a server-side PostHog event. Silent no-op on any failure."""
    client = _get_client()
    if client is None:
        return
    try:
        client.capture(distinct_id, event, properties or {})
    except Exception as e:
        logger.debug(f"PostHog capture error ({event}): {e}")


# ─── Typed helpers ────────────────────────────────────────────────────────────

def content_generation_failed(
    account_id: str, content_type: str, error: str
) -> None:
    capture(account_id, "content_generation_failed", {
        "content_type": content_type,
        "error": error,
    })


def fal_api_latency(
    account_id: str, model: str, duration_ms: int
) -> None:
    capture(account_id, "fal_api_latency", {
        "model": model,
        "duration_ms": duration_ms,
    })


def publishing_failed(
    account_id: str, platform: str, error: str
) -> None:
    capture(account_id, "publishing_failed", {
        "platform": platform,
        "error": error,
    })


def document_processed(
    account_id: str, file_type: str, chunks_created: int
) -> None:
    capture(account_id, "document_processed", {
        "file_type": file_type,
        "chunks_created": chunks_created,
    })


def competitor_analysis_completed(
    account_id: str, duration_seconds: float
) -> None:
    capture(account_id, "competitor_analysis_completed", {
        "duration_seconds": duration_seconds,
    })


def subscription_created(account_id: str, plan_id: str) -> None:
    capture(account_id, "subscription_created", {"plan_id": plan_id})


def subscription_cancelled(account_id: str, plan_id: str) -> None:
    capture(account_id, "subscription_cancelled", {"plan_id": plan_id})
