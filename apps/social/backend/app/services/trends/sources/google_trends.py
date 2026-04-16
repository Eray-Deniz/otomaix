"""Google Trends — TR Daily Search Trends RSS feed.

pytrends `related_queries` endpoint'i Google tarafından çok sık 429/302
döndürüyor ve kararsız. Bu yüzden resmi Daily Search Trends RSS'ine geçtik:
auth gerektirmez, her sektör için aynı havuzu döner, Claude synthesis aşaması
sektör alakasını filtreler.
"""

import re
import xml.etree.ElementTree as ET

import httpx

NAME = "Google Trends"
_BASE_URL = "https://trends.google.com/trending/rss?geo=TR"
_TIMEOUT = 12
_NS = {"ht": "https://trends.google.com/trending/rss"}

# Google Trends RSS kategori kodları (geo=TR ile birlikte kullanılır)
# Ref: https://trends.google.com/trending/rss?geo=TR&cat=t
_SECTOR_CATEGORY: dict[str, str] = {
    "teknoloji": "t",               # Sci/Tech
    "finans": "b",                   # Business
    "e-ticaret-perakende": "b",      # Business
    "saglik": "m",                   # Health
    "egitim": "t",                   # Sci/Tech (en yakın)
    "otomotiv": "t",                 # Sci/Tech (en yakın)
}


def _parse_traffic(raw: str) -> float:
    if not raw:
        return 0.0
    digits = re.sub(r"[^\d]", "", raw)
    try:
        return float(digits) if digits else 0.0
    except ValueError:
        return 0.0


async def fetch(sector: dict) -> list[dict]:
    slug = sector.get("slug") or "genel"
    cat = _SECTOR_CATEGORY.get(slug)
    url = f"{_BASE_URL}&cat={cat}" if cat else _BASE_URL
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                return []
            xml_text = resp.text
    except Exception:
        return []

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    channel = root.find("channel")
    if channel is None:
        return []

    results: list[dict] = []
    for item in channel.findall("item")[:20]:
        title = (item.findtext("title") or "").strip()
        if not title:
            continue
        traffic = _parse_traffic(item.findtext("ht:approx_traffic", default="", namespaces=_NS))
        # İlk haber başlığını özet olarak kullan
        news = item.find("ht:news_item", _NS)
        summary = None
        if news is not None:
            summary = (news.findtext("ht:news_item_title", default="", namespaces=_NS) or "").strip() or None
        results.append({
            "title": title,
            "source": NAME,
            "url": f"https://trends.google.com/trends/explore?q={title}&geo=TR",
            "score": traffic,
            "summary": summary,
        })
    return results
