"""YouTube Data API v3 — TR most popular, sektör kategori mapping'i ile."""

import httpx

from app.core.config import settings

NAME = "YouTube"
_TIMEOUT = 12

# Sektör slug → YouTube videoCategoryId (TR için)
# Ref: https://developers.google.com/youtube/v3/docs/videoCategories/list
_CATEGORY_MAP: dict[str, str] = {
    "teknoloji": "28",          # Science & Technology
    "moda-tekstil": "26",       # Howto & Style
    "yemek-gida": "26",
    "otomotiv": "2",            # Autos & Vehicles
    "egitim": "27",             # Education
    "saglik": "26",
    "turizm": "19",             # Travel & Events
    "finans": "25",             # News & Politics
    "e-ticaret-perakende": "26",
    "insaat-gayrimenkul": "26",
    "hizmet": "22",             # People & Blogs
    "genel": "24",              # Entertainment
}


async def fetch(sector: dict) -> list[dict]:
    if not settings.YOUTUBE_API_KEY:
        return []
    slug = sector.get("slug") or "genel"
    category_id = _CATEGORY_MAP.get(slug, "0")

    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": "TR",
        "maxResults": "15",
        "key": settings.YOUTUBE_API_KEY,
    }
    if category_id != "0":
        params["videoCategoryId"] = category_id

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get("https://www.googleapis.com/youtube/v3/videos", params=params)
            if resp.status_code != 200:
                return []
            data = resp.json()
    except Exception:
        return []

    results: list[dict] = []
    for item in data.get("items", [])[:15]:
        snippet = item.get("snippet") or {}
        stats = item.get("statistics") or {}
        title = (snippet.get("title") or "").strip()
        if not title:
            continue
        results.append({
            "title": title,
            "source": NAME,
            "url": f"https://www.youtube.com/watch?v={item.get('id')}",
            "score": float(stats.get("viewCount") or 0),
            "summary": (snippet.get("description") or "")[:240] or None,
        })
    return results
