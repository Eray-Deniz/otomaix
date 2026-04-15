"""Layer B orchestrator — kullanıcı tetiklemeli kişisel trend araması.

Akış:
  1. Marka + RAG + geçmiş postlardan arama sorguları üret (Claude Haiku)
  2. Serper.dev ile paralel Google TR araması
  3. Sonuçları birleştir + dedupe
  4. Claude Haiku ile sentez → 8 trend
  5. brand_trend_cache'e yaz, trend_usage sayacını artır
"""

import asyncio
import json
import logging
from typing import Any
from uuid import UUID

import asyncpg

from app.core.config import settings
from app.services.trends import serper_client

logger = logging.getLogger(__name__)

_MAX_QUERIES = 4
_FALLBACK_QUERIES_LIMIT = 3


async def _build_search_queries(brand: dict, recent_posts: list[dict]) -> list[str]:
    """Claude Haiku ile 3-4 canlı arama sorgusu öner."""
    name = brand.get("name") or "marka"
    sector = brand.get("sector") or "genel"
    kit = brand.get("brand_kit") or {}
    if isinstance(kit, str):
        try:
            kit = json.loads(kit)
        except Exception:
            kit = {}

    tone = kit.get("tone") or kit.get("voice") or ""
    audience = kit.get("target_audience") or kit.get("audience") or ""

    recent_titles = [p.get("prompt") or p.get("caption") or "" for p in recent_posts[:8]]
    recent_block = "\n".join(f"- {t[:120]}" for t in recent_titles if t)

    if not settings.ANTHROPIC_API_KEY:
        return [
            f"{sector} son gelişmeler Türkiye",
            f"{name} {sector} trend 2026",
            f"{sector} sosyal medya haftanın konusu",
        ][:_FALLBACK_QUERIES_LIMIT]

    try:
        import anthropic
    except ImportError:
        return [f"{sector} güncel haberler Türkiye"]

    system = (
        "Sen sosyal medya trend araştırmacısısın. Verilen markanın bu hafta "
        "konuşabileceği canlı konuları bulmak için Google'da arayacağın 3-4 "
        "somut arama sorgusu üret. Yanıtı SADECE JSON dizisi olarak ver."
    )
    user_msg = (
        f"Marka: {name}\nSektör: {sector}\nTonalite: {tone}\nHedef kitle: {audience}\n\n"
        f"Son içerikler:\n{recent_block or '(yok)'}\n\n"
        "Görev: Bu markayı ilgilendirecek güncel/canlı konular için Google'da "
        "arayacağın 3-4 arama sorgusu öner. Türkçe, Türkiye odaklı, güncellik öne "
        "çıksın. Sadece JSON dizisi:\n"
        '["sorgu 1", "sorgu 2", "sorgu 3"]'
    )

    def _call() -> str:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        return msg.content[0].text.strip()

    try:
        loop = asyncio.get_event_loop()
        raw = await loop.run_in_executor(None, _call)
        if "```" in raw:
            for part in raw.split("```"):
                s = part.strip()
                if s.startswith("json"):
                    s = s[4:].strip()
                if s.startswith("["):
                    raw = s
                    break
        queries = json.loads(raw)
        if isinstance(queries, list):
            return [str(q).strip() for q in queries if q][:_MAX_QUERIES]
    except Exception as e:
        logger.warning("layer_b query generation failed: %s", e)

    return [f"{sector} güncel gelişmeler", f"{name} {sector} trend"]


def _flatten_and_dedupe(raw_results: list[Any]) -> list[dict]:
    flat: list[dict] = []
    seen: set[str] = set()
    for r in raw_results:
        if isinstance(r, Exception) or not isinstance(r, dict):
            continue
        for it in serper_client.extract_items(r):
            key = (it.get("title") or "").lower().strip()[:80]
            if not key or key in seen:
                continue
            seen.add(key)
            flat.append(it)
    return flat


async def _synthesize_with_claude(items: list[dict], brand: dict) -> list[dict]:
    name = brand.get("name") or "marka"
    sector = brand.get("sector") or "genel"

    if not items:
        return [{
            "title": f"{name} için canlı sonuç bulunamadı",
            "source": "Serper",
            "relevance_score": 50,
            "summary": "Arama sonuçları boş döndü.",
            "content_opportunity": "Farklı bir anahtar kelime ile tekrar deneyin.",
            "suggested_prompt": f"{name} markası için genel bir post",
        }]

    if not settings.ANTHROPIC_API_KEY:
        return [
            {
                "title": it["title"][:100],
                "source": it.get("source") or "Google",
                "relevance_score": 70,
                "summary": (it.get("snippet") or "")[:200],
                "content_opportunity": "Bu gelişmeyi markanızın bakış açısıyla yorumlayın.",
                "suggested_prompt": f"{it['title']} hakkında {name} için bir post",
            }
            for it in items[:8]
        ]

    try:
        import anthropic
    except ImportError:
        return []

    lines: list[str] = []
    for i, it in enumerate(items[:40]):
        src = it.get("source", "")
        title = it.get("title", "")
        snippet = (it.get("snippet") or "")[:180]
        lines.append(f"[{src}] {title} — {snippet}"[:300])
    bulk = "\n".join(lines)

    system = (
        f"Sen {name} markası için kıdemli sosyal medya stratejistisin. "
        "Yanıtını SADECE geçerli JSON dizisi olarak döndür."
    )
    user_msg = (
        f"Marka: {name}\nSektör: {sector}\n\n"
        f"Canlı Google aramalarından dönen sonuçlar (her satırın başındaki "
        f"köşeli parantez içi KAYNAK domain'idir):\n{bulk}\n\n"
        f"Görev: {name} markasının bu hafta konuşabileceği EN GÜÇLÜ 8 trendi seç. "
        "FARKLI kaynaklardan dengeli bir dağılım olmalı — tek bir domain'e yığılma. "
        "Her biri için markanın bakış açısıyla içerik fırsatı ve prompt öner.\n\n"
        "KRİTİK KAYNAK KURALI:\n"
        "- Her trendin 'source' alanı, o trendin geldiği ham satırın başındaki "
        "[KAYNAK] etiketinden (domain adı) BİREBİR kopyalanmalı.\n"
        "- Birden fazla kaynaktan gelen tekrarı birleştirirsen source='Karma' yaz.\n"
        "- Tüm 8 trende aynı source'u yazma — çeşitlilik zorunlu.\n\n"
        "JSON formatı (yalnızca dizi):\n"
        "[\n"
        '  {\n'
        '    "title": "trend başlığı (kısa, Türkçe)",\n'
        '    "source": "ham satırdaki [KAYNAK] etiketinden kopyala",\n'
        '    "relevance_score": 85,\n'
        '    "summary": "1 cümle bağlam",\n'
        '    "content_opportunity": "Bu trendi nasıl içeriğe dönüştürürsün (1 cümle)",\n'
        '    "suggested_prompt": "İçerik üretim prompt önerisi"\n'
        '  }\n'
        "]"
    )

    def _call() -> tuple[str, int, int]:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY, timeout=60.0)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4000,
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = msg.content[0].text.strip()
        pt = getattr(msg.usage, "input_tokens", 0) if msg.usage else 0
        ct = getattr(msg.usage, "output_tokens", 0) if msg.usage else 0
        return text, pt, ct

    raw = ""
    last_err: Exception | None = None
    loop = asyncio.get_event_loop()
    for attempt in range(2):
        try:
            raw, pt, ct = await loop.run_in_executor(None, _call)
            if "```" in raw:
                for part in raw.split("```"):
                    s = part.strip()
                    if s.startswith("json"):
                        s = s[4:].strip()
                    if s.startswith("["):
                        raw = s
                        break
            start = raw.find("[")
            end = raw.rfind("]")
            if start >= 0 and end > start:
                raw = raw[start : end + 1]
            parsed = json.loads(raw)
            if not isinstance(parsed, list) or not parsed:
                raise ValueError("parsed is not a non-empty list")
            for it in parsed:
                it.setdefault("source", "Karma")
                it.setdefault("relevance_score", 70)
            parsed[0]["_prompt_tokens"] = pt
            parsed[0]["_completion_tokens"] = ct
            logger.info(
                "layer_b claude synthesis ok: brand=%s trends=%d attempt=%d",
                brand.get("name"), len(parsed), attempt + 1,
            )
            return parsed[:8]
        except Exception as e:
            last_err = e
            logger.warning(
                "layer_b synthesis failed (attempt %d) brand=%s err=%s raw_head=%s",
                attempt + 1, brand.get("name"), e, (raw or "")[:200],
            )
            await asyncio.sleep(1.5)
    logger.error("layer_b synthesis gave up brand=%s last_err=%s", brand.get("name"), last_err)
    return []


async def fetch_personal_trends(
    db: asyncpg.Connection,
    brand_id: UUID,
) -> dict:
    """Kişisel Layer B trend pipeline. Brand ownership ve quota kontrolü
    endpoint katmanında yapılır."""
    brand_row = await db.fetchrow(
        "SELECT id, name, sector, brand_kit FROM social.brands WHERE id = $1",
        brand_id,
    )
    if not brand_row:
        raise ValueError("brand not found")
    brand = dict(brand_row)

    recent = await db.fetch(
        "SELECT prompt, caption FROM social.posts "
        "WHERE brand_id = $1 AND status IN ('ready','published','partially_published') "
        "ORDER BY created_at DESC LIMIT 8",
        brand_id,
    )
    recent_posts = [dict(r) for r in recent]

    queries = await _build_search_queries(brand, recent_posts)
    if not queries:
        queries = [f"{brand.get('sector') or 'genel'} güncel"]

    search_tasks = [serper_client.search(q) for q in queries]
    raw_results = await asyncio.gather(*search_tasks, return_exceptions=True)
    flat = _flatten_and_dedupe(raw_results)

    trends = await _synthesize_with_claude(flat, brand)

    prompt_tokens = 0
    completion_tokens = 0
    if trends:
        prompt_tokens = trends[0].pop("_prompt_tokens", 0)
        completion_tokens = trends[0].pop("_completion_tokens", 0)

    serper_calls = sum(
        1 for r in raw_results if not isinstance(r, Exception)
    )

    await db.execute(
        """
        INSERT INTO social.brand_trend_cache
            (brand_id, trends, fetched_at, serper_queries, prompt_tokens, completion_tokens)
        VALUES ($1::uuid, $2, now(), $3, $4, $5)
        ON CONFLICT (brand_id) DO UPDATE SET
            trends = EXCLUDED.trends,
            fetched_at = now(),
            serper_queries = EXCLUDED.serper_queries,
            prompt_tokens = EXCLUDED.prompt_tokens,
            completion_tokens = EXCLUDED.completion_tokens
        """,
        brand_id,
        trends,
        serper_calls,
        prompt_tokens,
        completion_tokens,
    )

    return {
        "trends": trends,
        "queries": queries,
        "serper_calls": serper_calls,
        "raw_count": len(flat),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
    }
