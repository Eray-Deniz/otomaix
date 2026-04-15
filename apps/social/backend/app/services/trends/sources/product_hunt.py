"""Product Hunt GraphQL — teknoloji/hizmet sektörleri için son 24 saat trending."""

from datetime import datetime, timedelta, timezone

import httpx

from app.core.config import settings

NAME = "Product Hunt"
_TIMEOUT = 12
_URL = "https://api.producthunt.com/v2/api/graphql"

_ACTIVE_SECTORS = {"teknoloji", "hizmet", "finans", "e-ticaret-perakende"}

_QUERY = """
query TopPosts($postedAfter: DateTime!) {
  posts(order: VOTES, postedAfter: $postedAfter, first: 15) {
    edges {
      node {
        name
        tagline
        url
        votesCount
      }
    }
  }
}
"""


async def fetch(sector: dict) -> list[dict]:
    if not settings.PRODUCT_HUNT_TOKEN:
        return []
    slug = sector.get("slug") or ""
    if slug not in _ACTIVE_SECTORS:
        return []

    posted_after = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    headers = {
        "Authorization": f"Bearer {settings.PRODUCT_HUNT_TOKEN}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.post(
                _URL,
                headers=headers,
                json={"query": _QUERY, "variables": {"postedAfter": posted_after}},
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
    except Exception:
        return []

    edges = (((data.get("data") or {}).get("posts") or {}).get("edges")) or []
    results: list[dict] = []
    for edge in edges:
        node = edge.get("node") or {}
        name = (node.get("name") or "").strip()
        if not name:
            continue
        results.append({
            "title": name,
            "source": NAME,
            "url": node.get("url"),
            "score": float(node.get("votesCount") or 0),
            "summary": node.get("tagline"),
        })
    return results
