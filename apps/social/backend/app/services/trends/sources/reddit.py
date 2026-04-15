"""Reddit — TR subreddit'leri ve sektörel subreddit'ler."""

import asyncio

import httpx

from app.core.config import settings

NAME = "Reddit"
_TIMEOUT = 10

# Sektör slug → ek subreddit listesi
_SECTOR_SUBS: dict[str, list[str]] = {
    "teknoloji": ["turkey", "tech", "programming", "artificial"],
    "finans": ["turkey", "borsaistanbul", "personalfinance"],
    "e-ticaret-perakende": ["turkey", "ecommerce"],
    "yemek-gida": ["turkey", "food", "Cooking"],
    "moda-tekstil": ["turkey", "femalefashionadvice", "malefashionadvice"],
    "saglik": ["turkey", "health", "Fitness"],
    "egitim": ["turkey", "OdtuLife", "universite"],
    "turizm": ["turkey", "travel", "solotravel"],
    "otomotiv": ["turkey", "cars", "ElectricVehicles"],
    "insaat-gayrimenkul": ["turkey", "RealEstate"],
    "hizmet": ["turkey", "smallbusiness"],
    "genel": ["turkey", "Turkey_ekonomi"],
}


async def _fetch_sub(client: httpx.AsyncClient, sub: str) -> list[dict]:
    url = f"https://www.reddit.com/r/{sub}/top.json?t=day&limit=10"
    try:
        resp = await client.get(url)
        if resp.status_code != 200:
            return []
        data = resp.json()
        items: list[dict] = []
        for child in (data.get("data") or {}).get("children", [])[:10]:
            d = child.get("data") or {}
            title = (d.get("title") or "").strip()
            if not title or len(title) < 8:
                continue
            items.append({
                "title": title,
                "source": f"{NAME}/r/{sub}",
                "url": f"https://reddit.com{d.get('permalink', '')}",
                "score": float(d.get("score") or 0),
                "summary": (d.get("selftext") or "")[:240] or None,
            })
        return items
    except Exception:
        return []


async def fetch(sector: dict) -> list[dict]:
    slug = sector.get("slug") or "genel"
    subs = _SECTOR_SUBS.get(slug) or _SECTOR_SUBS["genel"]
    headers = {"User-Agent": settings.REDDIT_USER_AGENT}
    async with httpx.AsyncClient(timeout=_TIMEOUT, headers=headers, follow_redirects=True) as client:
        results = await asyncio.gather(*[_fetch_sub(client, s) for s in subs], return_exceptions=True)
    flat: list[dict] = []
    for r in results:
        if isinstance(r, list):
            flat.extend(r)
    flat.sort(key=lambda x: x.get("score") or 0, reverse=True)
    return flat[:20]
