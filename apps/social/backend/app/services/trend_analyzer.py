"""DEPRECATED — Phase 6 öncesi trend analizi servisi (Phase 3-5).

Phase 6'dan itibaren üç katmanlı yeni sistem kullanılmaktadır:
  - app/services/trends/layer_a.py  → Nightly ücretsiz kaynak taraması (7 kaynak)
  - app/services/trends/layer_b.py  → Serper.dev + Claude Haiku kişisel trend
  - app/services/trends/layer_c.py  → Apify + PDF aylık sektör raporu

Bu dosya geriye uyumluluk için korunmaktadır. Yeni geliştirmelerde kullanmayın.

Eski veri kaynakları:
1. Google Trends (pytrends) — sektöre göre TR trendleri (pytrends kuruluysa)
2. Türk haber RSS feed'leri — hurriyet, milliyet, sabah
3. Claude API — sektör relevance sıralaması ve özet üretimi
"""

import asyncio
import json
import re
from datetime import datetime, timezone

import httpx

from app.core.config import settings


# ─── RSS kaynakları ─────────────────────────────────────────────────────────

RSS_SOURCES = [
    {
        "name": "Hürriyet",
        "url": "https://www.hurriyet.com.tr/rss/anasayfa",
    },
    {
        "name": "Milliyet",
        "url": "https://www.milliyet.com.tr/rss/rssNew/gundemRss.xml",
    },
    {
        "name": "Sabah",
        "url": "https://www.sabah.com.tr/rss/anasayfa.xml",
    },
]


async def _fetch_rss(url: str, source_name: str) -> list[dict]:
    """Bir RSS feed'ini çek, başlık + açıklamaları listele."""
    items: list[dict] = []
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(
                url,
                headers={"User-Agent": "Mozilla/5.0 (compatible; Otomaix/1.0)"},
            )
            xml = resp.text

        # Başlıkları regex ile çıkar (feedparser bağımlılığından kaçın)
        titles = re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>", xml)
        if not titles:
            titles = re.findall(r"<title>(.*?)</title>", xml)

        # İlk eleman genellikle feed başlığıdır, atla
        for title in titles[1:16]:
            clean = re.sub(r"<[^>]+>", "", title).strip()
            if clean and len(clean) > 10:
                items.append({"title": clean, "source": source_name})
    except Exception:
        pass
    return items


async def _fetch_all_rss() -> list[dict]:
    """Tüm RSS kaynaklarını eşzamanlı çek."""
    results = await asyncio.gather(
        *[_fetch_rss(src["url"], src["name"]) for src in RSS_SOURCES],
        return_exceptions=True,
    )
    all_items: list[dict] = []
    for r in results:
        if isinstance(r, list):
            all_items.extend(r)
    return all_items


async def _fetch_google_trends(sector_keywords: list[str]) -> list[dict]:
    """pytrends ile Google Trends verisi çek (opsiyonel)."""
    try:
        from pytrends.request import TrendReq  # type: ignore

        pt = TrendReq(hl="tr-TR", tz=180, timeout=(10, 25))
        # Anahtar kelime sayısını 5 ile sınırla (pytrends limiti)
        kw_list = sector_keywords[:5]
        pt.build_payload(kw_list, cat=0, timeframe="now 7-d", geo="TR")
        related = pt.related_queries()

        trends: list[dict] = []
        for kw, data in related.items():
            if data and isinstance(data.get("rising"), object):
                rising_df = data["rising"]
                if rising_df is not None and not rising_df.empty:
                    for _, row in rising_df.head(5).iterrows():
                        trends.append(
                            {
                                "title": str(row.get("query", "")),
                                "source": "Google Trends",
                                "value": int(row.get("value", 0)),
                            }
                        )
        return trends
    except ImportError:
        return []
    except Exception:
        return []


def _extract_sector_keywords(sector: str) -> list[str]:
    """Sektör adından arama anahtar kelimeleri üret."""
    mapping: dict[str, list[str]] = {
        "teknoloji": ["teknoloji", "yazılım", "yapay zeka", "dijital", "siber"],
        "e-ticaret": ["e-ticaret", "online alışveriş", "kargo", "mağaza", "satış"],
        "yemek": ["restoran", "yemek", "mutfak", "tarif", "gastronomi"],
        "sağlık": ["sağlık", "hastane", "ilaç", "wellness", "fitness"],
        "eğitim": ["eğitim", "üniversite", "kurs", "öğrenci", "diploma"],
        "moda": ["moda", "giyim", "trend", "stil", "koleksiyon"],
        "turizm": ["turizm", "tatil", "otel", "seyahat", "destinasyon"],
        "finans": ["finans", "borsa", "yatırım", "döviz", "ekonomi"],
        "gayrimenkul": ["gayrimenkul", "konut", "inşaat", "kira", "tapu"],
        "otomotiv": ["otomotiv", "araç", "elektrikli araç", "trafik", "galeri"],
    }

    lower = sector.lower()
    for key, kws in mapping.items():
        if key in lower:
            return kws
    # Eşleşme yoksa sektörün kendisini kullan
    return [sector, f"{sector} Türkiye", f"{sector} haberleri"]


async def _rank_trends_with_claude(
    news_items: list[dict],
    google_trends: list[dict],
    sector: str,
    brand_name: str,
) -> list[dict]:
    """Claude ile trendleri sektöre uygunluk açısından sırala ve özet üret."""
    all_titles = []
    for item in news_items[:30]:
        all_titles.append(f"[Haber/{item['source']}] {item['title']}")
    for item in google_trends[:15]:
        all_titles.append(f"[Google Trends] {item['title']}")

    if not all_titles:
        return _fallback_trends(sector)

    titles_text = "\n".join(all_titles)

    system = (
        "Sen Türk KOBİ'lere sosyal medya içeriği stratejisi sunan bir uzmansın. "
        "Yanıtını SADECE geçerli JSON dizisi olarak ver, başka hiçbir şey yazma."
    )
    user_msg = (
        f"Marka: {brand_name}\n"
        f"Sektör: {sector}\n\n"
        f"Bu hafta Türkiye'deki güncel başlıklar:\n{titles_text}\n\n"
        f"Görev: Bu başlıklardan {sector} sektörüyle en alakalı 6 tanesini seç. "
        "Her biri için sosyal medya içerik fırsatını açıkla.\n\n"
        "JSON formatı (sadece dizi, fazladan metin yok):\n"
        '[\n'
        '  {\n'
        '    "title": "trend başlığı (kısa, Türkçe)",\n'
        '    "source": "Haber veya Google Trends",\n'
        '    "relevance_score": 85,\n'
        '    "content_opportunity": "Bu trendi nasıl içeriğe dönüştürebilirsin (1 cümle)",\n'
        '    "suggested_prompt": "İçerik üretim prompt önerisi"\n'
        '  }\n'
        ']'
    )

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1000,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        raw = msg.content[0].text.strip()
        # Markdown kod bloğunu temizle
        if "```" in raw:
            parts = raw.split("```")
            for part in parts:
                stripped = part.strip()
                if stripped.startswith("json"):
                    stripped = stripped[4:].strip()
                if stripped.startswith("["):
                    raw = stripped
                    break

        ranked: list[dict] = json.loads(raw)
        # Her öğeye kaynak bilgisi ekle
        for item in ranked:
            item.setdefault("source", "Haber")
            item.setdefault("relevance_score", 70)
        return ranked[:6]
    except Exception:
        return _fallback_trends(sector)


def _fallback_trends(sector: str) -> list[dict]:
    """Claude ya da kaynak erişimi başarısız olduğunda örnek trendler döndür."""
    return [
        {
            "title": f"{sector} Dijital Dönüşüm",
            "source": "Genel",
            "relevance_score": 90,
            "content_opportunity": "Dijital dönüşüm sürecinde markanızı konumlandırın.",
            "suggested_prompt": f"{sector} sektöründe dijital dönüşümün faydalarını anlatan bir post",
        },
        {
            "title": "Yapay Zeka Uygulamaları",
            "source": "Google Trends",
            "relevance_score": 85,
            "content_opportunity": "AI araçlarını işinizde nasıl kullandığınızı paylaşın.",
            "suggested_prompt": f"{sector} işletmelerinde yapay zeka kullanımı hakkında bilgilendirici içerik",
        },
        {
            "title": "Sürdürülebilirlik",
            "source": "Haber",
            "relevance_score": 75,
            "content_opportunity": "Markanızın çevre dostu yaklaşımını öne çıkarın.",
            "suggested_prompt": f"{sector} sektöründe sürdürülebilir uygulamalar hakkında içerik",
        },
    ]


# ─── Ana fonksiyon ───────────────────────────────────────────────────────────

async def get_trends_for_sector(sector: str, brand_name: str) -> list[dict]:
    """Bir sektör için güncel trendleri getir ve Claude ile sırala."""
    sector_keywords = _extract_sector_keywords(sector)

    # Paralel veri çekme
    news_items, google_trends = await asyncio.gather(
        _fetch_all_rss(),
        _fetch_google_trends(sector_keywords),
        return_exceptions=False,
    )

    ranked = await _rank_trends_with_claude(
        news_items if isinstance(news_items, list) else [],
        google_trends if isinstance(google_trends, list) else [],
        sector,
        brand_name,
    )
    return ranked


async def get_cached_or_fresh_trends(
    sector: str,
    brand_name: str,
    db,
    max_age_hours: int = 6,
) -> list[dict]:
    """Önbellekte güncel veri varsa döndür, yoksa yenile."""
    row = await db.fetchrow(
        """
        SELECT trends, fetched_at
        FROM social.trend_cache
        WHERE sector = $1
          AND fetched_at > now() - ($2 || ' hours')::interval
        ORDER BY fetched_at DESC
        LIMIT 1
        """,
        sector,
        str(max_age_hours),
    )

    if row and row["trends"]:
        cached = row["trends"]
        if isinstance(cached, str):
            cached = json.loads(cached)
        return cached

    # Taze veri çek
    trends = await get_trends_for_sector(sector, brand_name)

    # Önbelleğe kaydet
    await db.execute(
        """
        INSERT INTO social.trend_cache (sector, trends, fetched_at)
        VALUES ($1, $2::jsonb, now())
        ON CONFLICT (sector) DO UPDATE SET
            trends = EXCLUDED.trends,
            fetched_at = now()
        """,
        sector,
        json.dumps(trends),
    )

    return trends
