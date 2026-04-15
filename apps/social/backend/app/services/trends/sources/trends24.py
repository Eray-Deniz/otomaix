"""trends24.in HTML scrape — Twitter/X Türkiye günlük trendler."""

import re

import httpx

NAME = "Twitter Trends"
_URL = "https://trends24.in/turkey/"
_TIMEOUT = 10


async def fetch(sector: dict) -> list[dict]:
    try:
        async with httpx.AsyncClient(
            timeout=_TIMEOUT,
            headers={"User-Agent": "Mozilla/5.0 (compatible; otomaix/1.0)"},
            follow_redirects=True,
        ) as client:
            resp = await client.get(_URL)
            if resp.status_code != 200:
                return []
            html = resp.text
    except Exception:
        return []

    # İlk <ol class="trend-card__list"> bloğundan <a> metinlerini topla.
    block_match = re.search(r'<ol class="trend-card__list">(.*?)</ol>', html, flags=re.DOTALL)
    if not block_match:
        return []
    items_html = block_match.group(1)
    titles = re.findall(r"<a[^>]*>([^<]+)</a>", items_html)

    results: list[dict] = []
    seen: set[str] = set()
    for t in titles[:30]:
        title = t.strip()
        if not title or title in seen or len(title) < 3:
            continue
        seen.add(title)
        results.append({
            "title": title,
            "source": NAME,
            "url": None,
            "score": None,
            "summary": None,
        })
    return results[:20]
