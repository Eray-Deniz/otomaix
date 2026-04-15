"""Serper.dev Google Search API wrapper — Layer B canlı arama."""

import httpx

from app.core.config import settings

_URL = "https://google.serper.dev/search"
_TIMEOUT = 15


async def search(query: str, gl: str = "tr", hl: str = "tr", num: int = 10) -> dict:
    """Tek HTTP call — organic + news sonuçları döndürür.

    Raises ValueError if SERPER_API_KEY is missing.
    """
    if not settings.SERPER_API_KEY:
        raise ValueError("SERPER_API_KEY is not configured")

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            _URL,
            headers={
                "X-API-KEY": settings.SERPER_API_KEY,
                "Content-Type": "application/json",
            },
            json={"q": query, "gl": gl, "hl": hl, "num": num},
        )
        resp.raise_for_status()
        return resp.json()


def extract_items(result: dict) -> list[dict]:
    """Serper JSON → normalize edilmiş item listesi."""
    items: list[dict] = []
    for r in result.get("organic", [])[:10]:
        items.append({
            "title": r.get("title", ""),
            "url": r.get("link"),
            "snippet": r.get("snippet", ""),
            "source": r.get("source") or "Google",
        })
    for r in result.get("news", [])[:5]:
        items.append({
            "title": r.get("title", ""),
            "url": r.get("link"),
            "snippet": r.get("snippet", ""),
            "source": r.get("source") or "Google News",
            "date": r.get("date"),
        })
    return items
