"""Pinterest Trends — TR ideas feed'inden trend anahtar kelimeleri.

Eski `trends.pinterest.com/tr-tr/` sayfası artık 404. Bunun yerine
`tr.pinterest.com/ideas/` TR lokalinde Türkçe trend idea'ları render ediyor
(SSR HTML + inline JSON). Regex ile `"name":"..."` alanları yakalanır,
middleware gürültüsü büyük harfle başlayan girdiler filtresiyle elenir.
"""

import re

import httpx

NAME = "Pinterest Trends"
_URL = "https://tr.pinterest.com/ideas/"
_TIMEOUT = 12

# Yalnızca bu sektörler için devrede — diğerlerinde alakasız
_ACTIVE_SECTORS = {
    "moda-tekstil", "yemek-gida", "insaat-gayrimenkul",
    "turizm", "e-ticaret-perakende", "saglik",
}

_NAME_RE = re.compile(r'"name":"([A-ZÇĞİÖŞÜ][^"]{3,60})"')
_BLOCKLIST = {"pending", "loader", "middleware"}


async def fetch(sector: dict) -> list[dict]:
    slug = sector.get("slug") or ""
    if slug not in _ACTIVE_SECTORS:
        return []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "tr-TR,tr;q=0.9",
    }
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT, headers=headers, follow_redirects=True) as client:
            resp = await client.get(_URL)
            if resp.status_code != 200:
                return []
            html = resp.text
    except Exception:
        return []

    seen: set[str] = set()
    results: list[dict] = []
    for kw in _NAME_RE.findall(html):
        k = kw.strip()
        low = k.lower()
        if low in seen or low in _BLOCKLIST:
            continue
        # Tek kelimelik kategori adlarını (Beauty, Animals) ele — gerçek trend'ler
        # genelde 2+ kelime
        if " " not in k:
            continue
        seen.add(low)
        results.append({
            "title": k,
            "source": NAME,
            "url": f"https://tr.pinterest.com/search/pins/?q={k}",
            "score": None,
            "summary": None,
        })
        if len(results) >= 20:
            break
    return results
