"""Spotify Web API — TR Top 50 playlist (sadece eğlence/yaşam tarzı sektörleri).

Not: Spotify Charts CSV 2023'te kapandı. Web API ile 'Top 50 - Türkiye'
resmi playlist'inden track'ler çekiliyor.
"""

import base64

import httpx

from app.core.config import settings

NAME = "Spotify"
_TIMEOUT = 12
_PLAYLIST_ID = "37i9dQZEVXbIVYVBNw9D5K"  # Top 50 — Türkiye

_ACTIVE_SECTORS = {"genel", "moda-tekstil", "turizm", "egitim"}


async def _get_token(client: httpx.AsyncClient) -> str | None:
    if not (settings.SPOTIFY_CLIENT_ID and settings.SPOTIFY_CLIENT_SECRET):
        return None
    auth = base64.b64encode(
        f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()
    ).decode()
    try:
        resp = await client.post(
            "https://accounts.spotify.com/api/token",
            headers={"Authorization": f"Basic {auth}"},
            data={"grant_type": "client_credentials"},
        )
        if resp.status_code != 200:
            return None
        return resp.json().get("access_token")
    except Exception:
        return None


async def fetch(sector: dict) -> list[dict]:
    slug = sector.get("slug") or ""
    if slug not in _ACTIVE_SECTORS:
        return []
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            token = await _get_token(client)
            if not token:
                return []
            resp = await client.get(
                f"https://api.spotify.com/v1/playlists/{_PLAYLIST_ID}/tracks?limit=20",
                headers={"Authorization": f"Bearer {token}"},
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
    except Exception:
        return []

    results: list[dict] = []
    for item in (data.get("items") or [])[:20]:
        track = item.get("track") or {}
        name = (track.get("name") or "").strip()
        if not name:
            continue
        artists = ", ".join(a.get("name", "") for a in (track.get("artists") or []))
        results.append({
            "title": f"{name} — {artists}" if artists else name,
            "source": NAME,
            "url": (track.get("external_urls") or {}).get("spotify"),
            "score": float(track.get("popularity") or 0),
            "summary": None,
        })
    return results
