"""Google Trends (pytrends) — sektör keyword'leri için rising queries."""

import asyncio

NAME = "Google Trends"


def _sync_fetch(keywords: list[str]) -> list[dict]:
    try:
        from pytrends.request import TrendReq  # type: ignore
    except ImportError:
        return []
    try:
        pt = TrendReq(hl="tr-TR", tz=180, timeout=(10, 25))
        pt.build_payload(keywords[:5], cat=0, timeframe="now 7-d", geo="TR")
        related = pt.related_queries()
    except Exception:
        return []

    items: list[dict] = []
    for kw, data in (related or {}).items():
        if not data:
            continue
        rising = data.get("rising")
        if rising is None:
            continue
        try:
            for _, row in rising.head(5).iterrows():
                title = str(row.get("query") or "").strip()
                if not title:
                    continue
                items.append({
                    "title": title,
                    "source": NAME,
                    "url": f"https://trends.google.com/trends/explore?q={title}&geo=TR",
                    "score": float(row.get("value") or 0),
                    "summary": f"'{kw}' sorgusu üzerinden yükselen arama",
                })
        except Exception:
            continue
    return items


async def fetch(sector: dict) -> list[dict]:
    keywords: list[str] = list(sector.get("keywords") or [])
    if not keywords:
        return []
    loop = asyncio.get_event_loop()
    try:
        return await asyncio.wait_for(
            loop.run_in_executor(None, _sync_fetch, keywords),
            timeout=35,
        )
    except Exception:
        return []
