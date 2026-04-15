"""Apify REST client — Layer C sektör raporları için paylaşılan yardımcı.

run-sync-get-dataset-items endpoint'i kısa süren aktörler için uygun
(≤ 300 sn). Dataset JSON doğrudan döner, ayrıca run metadata'sı çekilmez.

Not: `competitor_analyzer.py` kendi ad-hoc Apify çağrısını kullanmaya devam
ediyor; Layer C ile tek noktadan çağrı gerektiği için bu modül yeni yazıldı.
İleride refactor edilecek (backlog).
"""

import logging
from typing import Any

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_BASE = "https://api.apify.com/v2"


async def run_actor(
    actor_id: str,
    input_payload: dict,
    timeout: int = 240,
) -> list[dict[str, Any]]:
    """Apify aktörünü senkron çalıştır, dataset items listesini döndür.

    `actor_id`: `username/actor-name` veya `username~actor-name` formatı.
    `timeout`: saniye — httpx client timeout + query param olarak kullanılır.
    Hata durumunda sessiz boş liste döner; caller başarı oranını üst seviyede
    sayar. Exception fırlatmaz.
    """
    if not settings.APIFY_API_KEY:
        logger.warning("apify run skipped: APIFY_API_KEY missing actor=%s", actor_id)
        return []

    # Aktör ID'sinde slash varsa tilde'a çevir (Apify REST uyumu)
    safe_id = actor_id.replace("/", "~")
    url = (
        f"{_BASE}/acts/{safe_id}/run-sync-get-dataset-items"
        f"?token={settings.APIFY_API_KEY}&timeout={timeout}"
    )

    try:
        async with httpx.AsyncClient(timeout=timeout + 20) as client:
            resp = await client.post(url, json=input_payload)
            if resp.status_code >= 400:
                logger.warning(
                    "apify actor failed actor=%s status=%d body=%s",
                    actor_id, resp.status_code, resp.text[:200],
                )
                return []
            data = resp.json()
            if not isinstance(data, list):
                return []
            return data
    except Exception as e:
        logger.warning("apify actor exception actor=%s err=%s", actor_id, e)
        return []
