"""TCMB EVDS — USD/TL, Euro, faiz, enflasyon (sadece finans + e-ticaret + genel)."""

from datetime import datetime, timedelta

import httpx

from app.core.config import settings

NAME = "TCMB EVDS"
_TIMEOUT = 12
_URL = "https://evds2.tcmb.gov.tr/service/evds/series="

_ACTIVE_SECTORS = {"finans", "e-ticaret-perakende", "insaat-gayrimenkul", "genel"}

# Seri kodları
_SERIES = {
    "USD/TL": "TP.DK.USD.A.YTL",
    "EUR/TL": "TP.DK.EUR.A.YTL",
    "TÜFE Yıllık": "TP.FG.J0",
    "Politika Faizi": "TP.APIFON4",
}


async def fetch(sector: dict) -> list[dict]:
    if not settings.EVDS_API_KEY:
        return []
    slug = sector.get("slug") or ""
    if slug not in _ACTIVE_SECTORS:
        return []

    today = datetime.now()
    start = (today - timedelta(days=7)).strftime("%d-%m-%Y")
    end = today.strftime("%d-%m-%Y")
    series_codes = "-".join(_SERIES.values())
    url = f"{_URL}{series_codes}&startDate={start}&endDate={end}&type=json&aggregationTypes=last&formulas=0"
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
    last = items[-1]  # en güncel satır
    results: list[dict] = []
    for name, code in _SERIES.items():
        key = code.replace(".", "_")
        value = last.get(key)
        if value in (None, ""):
            continue
        results.append({
            "title": f"{name}: {value}",
            "source": NAME,
            "url": "https://evds2.tcmb.gov.tr/",
            "score": None,
            "summary": f"TCMB güncel değer ({last.get('Tarih')})",
        })
    return results
