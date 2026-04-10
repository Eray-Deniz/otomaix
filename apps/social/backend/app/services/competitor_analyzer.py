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
            model="claude-haiku-4-5-20251001",
            max_tokens=600,
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

async def analyze_instagram(handle: str) -> dict:
    """Instagram hesabını analiz et.

    APIFY_API_KEY varsa gerçek veri çeker.
    Yoksa yapısal placeholder döner (gösterge amaçlı).
    """
    if not handle:
        return {}

    clean_handle = handle.lstrip("@")

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
    """Apify Instagram Scraper ile gerçek hesap verisi çek."""
    run_url = "https://api.apify.com/v2/acts/apify~instagram-profile-scraper/run-sync-get-dataset-items"
    params = {
        "token": settings.APIFY_API_KEY,
        "usernames": handle,
        "resultsLimit": 20,
    }
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(run_url, json=params)
            data = resp.json()
            if not data or not isinstance(data, list):
                return {"handle": handle, "error": "Apify veri döndürmedi"}

            profile = data[0] if data else {}
            posts = profile.get("latestPosts", [])

            total_likes = sum(p.get("likesCount", 0) for p in posts)
            total_comments = sum(p.get("commentsCount", 0) for p in posts)
            post_count = len(posts) or 1
            followers = profile.get("followersCount", 0) or 1

            content_types: dict = {"image": 0, "video": 0, "carousel": 0}
            for p in posts:
                t = p.get("type", "image").lower()
                if t in content_types:
                    content_types[t] += 1

            hashtag_freq: dict = {}
            for p in posts:
                for tag in (p.get("hashtags") or []):
                    tag = tag.lower().lstrip("#")
                    hashtag_freq[tag] = hashtag_freq.get(tag, 0) + 1
            top_hashtags = sorted(hashtag_freq, key=lambda k: -hashtag_freq[k])[:10]

            return {
                "handle": handle,
                "source": "apify",
                "followers": profile.get("followersCount"),
                "following": profile.get("followingCount"),
                "post_count": profile.get("postsCount"),
                "avg_likes": round(total_likes / post_count),
                "avg_comments": round(total_comments / post_count),
                "engagement_rate": round((total_likes + total_comments) / followers * 100, 2),
                "posting_frequency_per_week": None,
                "content_types": content_types,
                "top_hashtags": top_hashtags,
                "best_posting_times": [],
                "top_posts": [
                    {"url": p.get("url"), "likes": p.get("likesCount"), "type": p.get("type")}
                    for p in sorted(posts, key=lambda x: x.get("likesCount", 0), reverse=True)[:3]
                ],
            }
    except Exception as e:
        return {"handle": handle, "error": str(e)}


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
            model="claude-haiku-4-5-20251001",
            max_tokens=700,
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
