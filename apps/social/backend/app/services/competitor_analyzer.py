"""Rakip analizi servisi.

İki analiz kaynağı:
1. analyze_website(url)     — httpx ile site çek + Claude ile analiz et (her zaman çalışır)
2. analyze_instagram(handle) — APIFY_API_KEY varsa gerçek veri, yoksa yapısal placeholder döner

generate_competitor_report() — birden fazla rakibin analizini Claude ile sentezler.
"""

import re
from uuid import UUID

import asyncpg
import httpx

from app.core.config import settings


# ─── Website analizi ────────────────────────────────────────────────────────

async def analyze_website(url: str) -> dict:
    """Rakip web sitesini çek, Claude ile analiz et."""
    if not url:
        return {}

    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    html = ""
    try:
        async with httpx.AsyncClient(timeout=12, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            html = resp.text[:10000]
    except Exception:
        return {"error": "Web sitesine ulaşılamadı", "url": url}

    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()[:5000]

    system = (
        "Sen bir rekabet analisti olarak rakip firmaların web sitelerini analiz ediyorsun. "
        "Yanıtını SADECE JSON olarak ver."
    )
    user_msg = (
        f"Bu rakip web sitesi içeriğini analiz et:\n\n{text}\n\n"
        "Şu JSON formatında döndür:\n"
        '{"company_name": "...", "main_services": ["...", "..."], '
        '"target_audience": "...", "pricing_hints": "...", '
        '"content_themes": ["...", "..."], "positioning": "...", '
        '"strengths": ["...", "..."], "tone": "..."}'
    )

    result = {"url": url}
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=600,
            cache_control={"type": "ephemeral"},
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        import json

        raw = msg.content[0].text.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result.update(json.loads(raw))
    except Exception:
        result["error"] = "Analiz yapılamadı"

    return result


# ─── Instagram analizi ──────────────────────────────────────────────────────

def _normalize_instagram_handle(handle: str) -> str:
    """`@user`, `user`, `instagram.com/user/`, `https://www.instagram.com/user/?hl=tr`
    gibi varyantları saf `user` username'ine indirger."""
    h = handle.strip()
    m = re.search(r"instagram\.com/([^/?#]+)", h, re.IGNORECASE)
    if m:
        h = m.group(1)
    return h.lstrip("@").rstrip("/")


async def analyze_instagram(handle: str) -> dict:
    """Instagram hesabını analiz et.

    APIFY_API_KEY varsa gerçek veri çeker.
    Yoksa yapısal placeholder döner (gösterge amaçlı).
    """
    if not handle:
        return {}

    clean_handle = _normalize_instagram_handle(handle)

    if getattr(settings, "APIFY_API_KEY", ""):
        return await _analyze_instagram_apify(clean_handle)

    # Placeholder — API key olmadan çalışır, yapıyı gösterir
    return {
        "handle": clean_handle,
        "source": "placeholder",
        "note": "Gerçek veri için APIFY_API_KEY gerekli",
        "followers": None,
        "following": None,
        "post_count": None,
        "avg_likes": None,
        "avg_comments": None,
        "engagement_rate": None,
        "posting_frequency_per_week": None,
        "content_types": {"image": None, "video": None, "carousel": None},
        "top_hashtags": [],
        "best_posting_times": [],
        "top_posts": [],
    }


async def _analyze_instagram_apify(handle: str) -> dict:
    """Apify Instagram Profile Scraper ile profil bilgilerini çek.

    Bu actor sadece profil meta-verisini döndürür (takipçi, bio, verified, kategori).
    Post-level metrikler (avg_likes, engagement) için ayrı instagram-post-scraper
    gerekir — ek kredi maliyeti olduğu için şu an kapsam dışı.
    """
    run_url = (
        "https://api.apify.com/v2/acts/apify~instagram-profile-scraper/"
        f"run-sync-get-dataset-items?token={settings.APIFY_API_KEY}"
    )
    body = {"usernames": [handle]}
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            resp = await client.post(run_url, json=body)
            if resp.status_code >= 400:
                return {
                    "handle": handle,
                    "source": "apify_error",
                    "error": f"Apify HTTP {resp.status_code}: {resp.text[:200]}",
                }
            data = resp.json()
            if not data or not isinstance(data, list) or not data:
                return {
                    "handle": handle,
                    "source": "apify_error",
                    "error": "Apify veri döndürmedi (hesap bulunamadı veya kredi yok)",
                }

            profile = data[0]
            return {
                "handle": handle,
                "source": "apify",
                "full_name": profile.get("fullName"),
                "biography": profile.get("biography"),
                "followers": profile.get("followersCount"),
                "following": profile.get("followsCount"),
                "post_count": profile.get("postsCount"),
                "is_verified": profile.get("verified"),
                "is_business": profile.get("isBusinessAccount"),
                "business_category": profile.get("businessCategoryName"),
                "profile_pic_url": profile.get("profilePicUrlHD") or profile.get("profilePicUrl"),
                "external_url": profile.get("externalUrl"),
                # Post-level metrikler bu actor'dan gelmiyor:
                "avg_likes": None,
                "avg_comments": None,
                "engagement_rate": None,
                "content_types": None,
                "top_hashtags": [],
            }
    except Exception as e:
        return {"handle": handle, "source": "apify_error", "error": str(e)}


# ─── Rakip raporu sentezi ───────────────────────────────────────────────────

async def generate_competitor_report(
    brand_name: str,
    brand_sector: str,
    analyses: list[dict],
) -> dict:
    """Birden fazla rakip analizini Claude ile sentezle, fırsat ve öneri üret."""
    if not analyses:
        return {"summary": "Henüz analiz edilmiş rakip yok.", "opportunities": [], "recommendations": []}

    summaries = []
    for a in analyses:
        name = a.get("competitor_name", "Rakip")
        website_data = (a.get("analysis_data") or {}).get("website", {})
        instagram_data = (a.get("analysis_data") or {}).get("instagram", {})
        summaries.append(
            f"- {name}: "
            f"Konum='{website_data.get('positioning', 'Bilinmiyor')}', "
            f"Güçlü Yönler={website_data.get('strengths', [])}, "
            f"Instagram Etkileşim={instagram_data.get('engagement_rate', '?')}%"
        )

    context = "\n".join(summaries)

    system = (
        "Sen bir stratejik rekabet analisti olarak KOBİ'lere sosyal medya fırsatları buluyorsun. "
        "Yanıtını SADECE JSON olarak ver."
    )
    user_msg = (
        f"Marka: {brand_name} | Sektör: {brand_sector}\n\n"
        f"Rakip özeti:\n{context}\n\n"
        "Şu JSON formatında döndür:\n"
        '{"summary": "genel değerlendirme", '
        '"opportunities": ["fırsat 1", "fırsat 2", "fırsat 3"], '
        '"content_gaps": ["içerik boşluğu 1", "içerik boşluğu 2"], '
        '"recommendations": ["öneri 1", "öneri 2", "öneri 3"]}'
    )

    try:
        import json
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=700,
            cache_control={"type": "ephemeral"},
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = msg.content[0].text.strip()
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception:
        return {
            "summary": "Rapor üretilemedi.",
            "opportunities": [],
            "content_gaps": [],
            "recommendations": [],
        }


# ─── Tek rakip tam analizi ──────────────────────────────────────────────────

async def run_full_analysis(competitor: dict) -> dict:
    """Bir rakip kaydı için website + instagram analizini çalıştır."""
    website_result = {}
    instagram_result = {}

    if competitor.get("website_url"):
        website_result = await analyze_website(competitor["website_url"])

    if competitor.get("instagram_handle"):
        instagram_result = await analyze_instagram(competitor["instagram_handle"])

    return {
        "website": website_result,
        "instagram": instagram_result,
    }
