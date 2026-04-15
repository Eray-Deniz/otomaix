"""Layer A orchestrator — sektör başına ücretsiz kaynakları paralel topla,
Claude Haiku ile sentezle ve `sector_trend_cache` tablosuna yaz.
"""

import asyncio
import json
import logging
from typing import Any

import asyncpg

from app.core.config import settings
from app.services.trends.sources import (
    google_news,
    google_trends,
    pinterest_trends,
    reddit,
    tcmb_evds,
    trends24,
    youtube,
)

logger = logging.getLogger(__name__)

_SOURCES = [
    google_news,
    google_trends,
    youtube,
    reddit,
    trends24,
    pinterest_trends,
    tcmb_evds,
]


async def _run_source(mod, sector: dict) -> tuple[str, list[dict]]:
    name = getattr(mod, "NAME", mod.__name__)
    try:
        items = await mod.fetch(sector)
        return name, items or []
    except Exception as e:
        logger.warning("trend source %s failed for %s: %s", name, sector.get("slug"), e)
        return name, []


async def fetch_sector_layer_a(sector: dict) -> dict:
    """Bir sektör için tüm ücretsiz kaynakları paralel topla, Claude ile sentezle."""
    tasks = [_run_source(mod, sector) for mod in _SOURCES]
    results = await asyncio.gather(*tasks, return_exceptions=False)

    all_items: list[dict] = []
    source_summary: dict[str, int] = {}
    for name, items in results:
        source_summary[name] = len(items)
        all_items.extend(items)

    # Dedupe by title prefix
    seen: set[str] = set()
    deduped: list[dict] = []
    for item in all_items:
        key = (item.get("title") or "").lower().strip()[:80]
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    trends = await _synthesize_with_claude(deduped, sector)
    return {"trends": trends, "source_summary": source_summary, "raw_count": len(deduped)}


def _fallback_trends(sector: dict) -> list[dict]:
    name = sector.get("display_name") or sector.get("slug") or "Genel"
    return [
        {
            "title": f"{name} Dijital Dönüşüm",
            "source": "Genel",
            "relevance_score": 80,
            "summary": f"{name} sektöründe dijitalleşme",
            "content_opportunity": "Dijital dönüşüm sürecinde markanızı konumlandırın.",
            "suggested_prompt": f"{name} sektöründe dijital dönüşüm trendleri hakkında bir post",
        }
    ]


async def _synthesize_with_claude(items: list[dict], sector: dict) -> list[dict]:
    if not items or not settings.ANTHROPIC_API_KEY:
        return _fallback_trends(sector)
    try:
        import anthropic
    except ImportError:
        return _fallback_trends(sector)

    sector_name = sector.get("display_name") or sector.get("slug", "Genel")

    # Her item'ı kısa satıra çevir
    lines: list[str] = []
    for i, it in enumerate(items[:60]):
        src = it.get("source", "")
        title = it.get("title", "")
        summary = it.get("summary") or ""
        line = f"[{src}] {title}"
        if summary:
            line += f" — {summary[:120]}"
        lines.append(line[:260])
    bulk = "\n".join(lines)

    system = (
        "Sen Türk KOBİ'lere sosyal medya trend analizi sunan kıdemli bir uzmansın. "
        "Yanıtını SADECE geçerli JSON dizisi olarak döndür, başka hiçbir şey yazma."
    )
    user_msg = (
        f"Sektör: {sector_name}\n\n"
        f"Bu hafta toplanan ham başlıklar/trendler:\n{bulk}\n\n"
        f"Görev: {sector_name} sektöründeki KOBİ'lerin sosyal medya için "
        "kullanabileceği EN GÜÇLÜ 8 trendi seç. Tekrarları birleştir, alakasızları "
        "ele. Her biri için içerik fırsatı ve prompt öner.\n\n"
        "JSON formatı (yalnızca dizi):\n"
        "[\n"
        "  {\n"
        '    "title": "trend başlığı (kısa, Türkçe)",\n'
        '    "source": "Google News / Twitter / Reddit vs.",\n'
        '    "relevance_score": 85,\n'
        '    "summary": "1 cümle bağlam",\n'
        '    "content_opportunity": "Bu trendi nasıl içeriğe dönüştürürsün (1 cümle)",\n'
        '    "suggested_prompt": "İçerik üretim prompt önerisi"\n'
        "  }\n"
        "]"
    )

    def _call_claude() -> str:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY, timeout=60.0)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4000,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        return msg.content[0].text.strip()

    raw = ""
    last_err: Exception | None = None
    loop = asyncio.get_event_loop()
    for attempt in range(2):
        try:
            raw = await loop.run_in_executor(None, _call_claude)
            # Kod bloğunu soy, ilk '[' ile son ']' arasını çek
            if "```" in raw:
                for part in raw.split("```"):
                    stripped = part.strip()
                    if stripped.startswith("json"):
                        stripped = stripped[4:].strip()
                    if stripped.startswith("["):
                        raw = stripped
                        break
            start = raw.find("[")
            end = raw.rfind("]")
            if start >= 0 and end > start:
                raw = raw[start : end + 1]
            parsed = json.loads(raw)
            if not isinstance(parsed, list) or not parsed:
                raise ValueError("parsed is not a non-empty list")
            for item in parsed:
                item.setdefault("source", "Karma")
                item.setdefault("relevance_score", 70)
            logger.info(
                "claude synthesis ok: sector=%s trends=%d attempt=%d",
                sector.get("slug"), len(parsed), attempt + 1,
            )
            return parsed[:8]
        except Exception as e:
            last_err = e
            logger.warning(
                "claude synthesis failed (attempt %d) sector=%s err=%s raw_head=%s",
                attempt + 1, sector.get("slug"), e, (raw or "")[:200],
            )
            await asyncio.sleep(1.5)
    logger.error("claude synthesis gave up sector=%s last_err=%s", sector.get("slug"), last_err)
    return _fallback_trends(sector)


async def run_nightly_sweep(db: asyncpg.Connection) -> dict[str, Any]:
    """Tüm ana sektörleri tara, sonuçları cache'e yaz."""
    sectors = await db.fetch(
        "SELECT id::text, slug, display_name, keywords "
        "FROM social.sectors WHERE parent_sector_id IS NULL ORDER BY slug"
    )

    processed = 0
    errors: list[str] = []

    for row in sectors:
        sector = dict(row)
        try:
            result = await fetch_sector_layer_a(sector)
            await db.execute(
                """
                INSERT INTO social.sector_trend_cache
                    (sector_id, layer, trends, source_summary, fetched_at)
                VALUES ($1::uuid, 'A', $2, $3, now())
                ON CONFLICT (sector_id, layer) DO UPDATE SET
                    trends = EXCLUDED.trends,
                    source_summary = EXCLUDED.source_summary,
                    fetched_at = now()
                """,
                sector["id"],
                result["trends"],
                result["source_summary"],
            )
            processed += 1
            logger.info(
                "layer_a: %s → %d trends (raw=%d)",
                sector["slug"], len(result["trends"]), result.get("raw_count", 0),
            )
        except Exception as e:
            msg = f"{sector.get('slug')}: {e}"
            errors.append(msg)
            logger.exception("layer_a nightly sweep failed for %s", sector.get("slug"))

    if errors:
        try:
            import sentry_sdk
            sentry_sdk.capture_message(
                f"Layer A nightly sweep errors ({len(errors)}/{len(sectors)}): "
                + "; ".join(errors[:10]),
                level="warning",
            )
        except Exception:
            pass

    return {
        "processed": processed,
        "total_sectors": len(sectors),
        "errors": errors,
    }
