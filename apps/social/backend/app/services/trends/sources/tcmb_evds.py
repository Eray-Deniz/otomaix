"""TCMB EVDS — USD/TL, Euro, faiz, enflasyon (sadece finans + e-ticaret + genel)."""

from datetime import datetime, timedelta

import httpx

from app.core.config import settings

NAME = "TCMB EVDS"
_TIMEOUT = 12
_URL = "https://evds3.tcmb.gov.tr/igmevdsms-dis/series="

_ACTIVE_SECTORS = {"finans", "e-ticaret-perakende", "insaat-gayrimenkul", "genel"}

# Seri kodları — günlük frekansta yayınlananlar seçildi
_SERIES = {
    "USD/TL (Satış)": "TP.DK.USD.S.YTL",
    "EUR/TL (Satış)": "TP.DK.EUR.S.YTL",
}


async def fetch(sector: dict) -> list[dict]:
    if not settings.EVDS_API_KEY:
        return []
    slug = sector.get("slug") or ""
    if slug not in _ACTIVE_SECTORS:
        return []

    today = datetime.now()
    start = (today - timedelta(days=14)).strftime("%d-%m-%Y")
    end = today.strftime("%d-%m-%Y")
    series_codes = "-".join(_SERIES.values())
    url = f"{_URL}{series_codes}&startDate={start}&endDate={end}&type=json"
    headers = {"key": settings.EVDS_API_KEY}

    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return []
            data = resp.json()
    except Exception:
        return []

    items = data.get("items") or []
    if not items:
        return []

    results: list[dict] = []
    for name, code in _SERIES.items():
        col = code.replace(".", "_")
        latest_value = None
        latest_date = None
        for row in reversed(items):
            v = row.get(col)
            if v not in (None, "", "null"):
                latest_value = v
                latest_date = row.get("Tarih")
                break
        if latest_value is None:
            continue
        try:
            formatted = f"{float(latest_value):.4f}"
        except (TypeError, ValueError):
            formatted = str(latest_value)
        results.append({
            "title": f"{name}: {formatted} ({latest_date})",
            "source": NAME,
            "url": "https://evds3.tcmb.gov.tr/",
            "score": None,
            "summary": f"TCMB güncel değer: {formatted}",
        })
    return results
