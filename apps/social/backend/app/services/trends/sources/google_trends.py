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


def _parse_feed(xml_text: str, limit: int = 30) -> list[dict]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    channel = root.find("channel")
    if channel is None:
        return []

    results: list[dict] = []
    for item in channel.findall("item")[:limit]:
        title = (item.findtext("title") or "").strip()
        if not title:
            continue
        traffic = _parse_traffic(item.findtext("ht:approx_traffic", default="", namespaces=_NS))
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


async def fetch(sector: dict) -> list[dict]:
    slug = sector.get("slug") or "genel"
    cat = _SECTOR_CATEGORY.get(slug)

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        results: list[dict] = []

        # Kategori filtreli feed (sektöre özel)
        if cat:
            try:
                resp = await client.get(
                    f"{_BASE_URL}&cat={cat}",
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                if resp.status_code == 200:
                    results = _parse_feed(resp.text, limit=20)
            except Exception:
                pass

        # Az sonuç geldiyse genel feed'i de ekle (dedupe ile)
        if len(results) < 5:
            try:
                resp = await client.get(
                    _BASE_URL,
                    headers={"User-Agent": "Mozilla/5.0"},
                )
                if resp.status_code == 200:
                    general = _parse_feed(resp.text, limit=15)
                    seen = {r["title"].lower() for r in results}
                    for item in general:
                        if item["title"].lower() not in seen:
                            results.append(item)
                            seen.add(item["title"].lower())
            except Exception:
                pass

    return results[:30]
