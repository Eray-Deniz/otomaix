"""Pinterest Trends — moda, yemek, ev dekor, hediye için kritik."""

import re

import httpx

NAME = "Pinterest Trends"
_URL = "https://trends.pinterest.com/tr-tr/"
_TIMEOUT = 12

# Yalnızca bu sektörler için devrede — diğerlerinde alakasız
_ACTIVE_SECTORS = {
    "moda-tekstil", "yemek-gida", "insaat-gayrimenkul",
    "turizm", "e-ticaret-perakende", "saglik",
}


async def fetch(sector: dict) -> list[dict]:
    slug = sector.get("slug") or ""
    if slug not in _ACTIVE_SECTORS:
        return []
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

    # Pinterest trend kartları JSON-LD/next data içinde; basit regex ile anahtar kelimeleri yakala.
    # Yapı sık değişebilir — bulamadığımızda sessiz düş.
    candidates = re.findall(r'"keyword"\s*:\s*"([^"]{3,80})"', html)
    seen: set[str] = set()
    results: list[dict] = []
    for kw in candidates[:40]:
        k = kw.strip()
        low = k.lower()
        if low in seen:
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
