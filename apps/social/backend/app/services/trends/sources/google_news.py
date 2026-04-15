"""Google News RSS — sektör keyword'leri ile TR feed."""

import asyncio
import re
from urllib.parse import quote_plus

import httpx

NAME = "Google News"
_TIMEOUT = 10


def _parse_rss(xml: str, limit: int = 15) -> list[dict]:
    items: list[dict] = []
    entries = re.findall(r"<item>(.*?)</item>", xml, flags=re.DOTALL)
    for entry in entries[:limit]:
        title_m = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", entry, flags=re.DOTALL)
        link_m = re.search(r"<link>(.*?)</link>", entry)
        if not title_m:
            continue
        title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip()
        if not title or len(title) < 8:
            continue
        items.append({
            "title": title,
            "source": NAME,
            "url": link_m.group(1).strip() if link_m else None,
            "score": None,
            "summary": None,
        })
    return items


async def _fetch_one(client: httpx.AsyncClient, query: str) -> list[dict]:
    url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=tr&gl=TR&ceid=TR:tr"
    try:
        resp = await client.get(url)
        if resp.status_code != 200:
            return []
        return _parse_rss(resp.text, limit=10)
    except Exception:
        return []


async def fetch(sector: dict) -> list[dict]:
    keywords: list[str] = list(sector.get("keywords") or [])[:4]
    if not keywords:
        return []
    async with httpx.AsyncClient(timeout=_TIMEOUT, headers={"User-Agent": "otomaix/1.0"}) as client:
        results = await asyncio.gather(*[_fetch_one(client, kw) for kw in keywords], return_exceptions=True)
    flat: list[dict] = []
    seen: set[str] = set()
    for r in results:
        if isinstance(r, list):
            for item in r:
                key = item["title"].lower()[:80]
                if key in seen:
                    continue
                seen.add(key)
                flat.append(item)
    return flat[:25]
