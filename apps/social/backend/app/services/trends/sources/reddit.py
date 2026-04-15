"""Reddit — TR subreddit'leri ve sektörel subreddit'ler.

Not: Reddit Haziran 2024'ten sonra unauthenticated `.json` endpoint'lerini
büyük ölçüde 403'ledi. RSS (`.rss`) feed'i hâlâ public — onu kullanıyoruz.
"""

import asyncio
import re

import httpx

from app.core.config import settings

NAME = "Reddit"
_TIMEOUT = 10

# Sektör slug → subreddit listesi
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
    "genel": ["turkey"],
}


def _parse_atom(xml: str, sub: str, limit: int = 10) -> list[dict]:
    items: list[dict] = []
    entries = re.findall(r"<entry>(.*?)</entry>", xml, flags=re.DOTALL)
    for entry in entries[:limit]:
        title_m = re.search(r"<title>(.*?)</title>", entry, flags=re.DOTALL)
        link_m = re.search(r'<link[^>]*href="([^"]+)"', entry)
        if not title_m:
            continue
        title = re.sub(r"\s+", " ", title_m.group(1)).strip()
        if not title or len(title) < 8:
            continue
        items.append({
            "title": title,
            "source": f"{NAME}/r/{sub}",
            "url": link_m.group(1) if link_m else None,
            "score": None,
            "summary": None,
        })
    return items


async def _fetch_sub(client: httpx.AsyncClient, sub: str) -> list[dict]:
    url = f"https://www.reddit.com/r/{sub}/top.rss?t=day"
    try:
        resp = await client.get(url)
        if resp.status_code != 200:
            return []
        return _parse_atom(resp.text, sub, limit=10)
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
    return flat[:20]
