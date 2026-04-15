"""Layer C — Pro+ aylık sektör raporu (Apify aktörleri + Claude Haiku + PDF).

Akış:
  1. Sektöre göre koşulan Apify aktörlerini paralel çalıştır (per-actor try/except)
  2. Ham item'ları normalize et + dedupe
  3. Claude Haiku ile 12 trend sentezle (robust parse — Layer A/B ile aynı pattern)
  4. Jinja2 + weasyprint ile PDF render et
  5. PDF'i R2'ye yükle, sector_reports satırını status=ready olarak upsert et

Maliyet: `_ACTOR_COST_USD` sabit tablosu (her aktör için aylık ortalama)
+ Claude Haiku tokens.
"""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import asyncpg

from app.core.config import settings
from app.services import apify_client
from app.services.pdf_renderer import render_sector_report
from app.services.storage import r2

logger = logging.getLogger(__name__)

# Aktör ID'leri — yalnızca Apify marketplace'te doğrulanmış olanlar.
# epctex/* ve dtrungtin/* aktörleri 404 (silinmiş/taşınmış) → listeden çıkarıldı.
# Yeni aktör eklerken önce `GET /v2/acts/{id}` ile varlık kontrolü yap,
# ondan sonra SECTOR_ACTOR_MAP'e ekle. Aktör yoksa pipeline sessizce yutar
# ama raporda "kaynak yok" kartı görünür.
_ACTOR_IDS: dict[str, str] = {
    "tiktok":    "clockworks/free-tiktok-scraper",  # doğrulandı — 20 kayıt/çağrı
    "instagram": "apify/instagram-scraper",         # Apify resmi
    "trendyol":  "tyegen/trendyol-product-scraper", # pay-per-result $5/1k
}

# Aktör başına ortalama maliyet (Apify fiyatlandırma tablosu, USD)
# 20 item/run varsayımıyla tahmini ücret.
_ACTOR_COST_USD: dict[str, float] = {
    "tiktok":    0.05,
    "instagram": 0.10,
    "trendyol":  0.10,  # $5/1000 × 20 item
}

# Sektör slug → aktör anahtar listesi. Şu an sadece tiktok + instagram
# doğrulanmış durumda; sektör-spesifik e-ticaret aktörleri (trendyol,
# hepsiburada, dolap, ciceksepeti, sahibinden, yemeksepeti, booking, n11,
# twitter) eklendikçe bu harita genişleyecek.
SECTOR_ACTOR_MAP: dict[str, list[str]] = {
    "e-ticaret-perakende": ["tiktok", "instagram", "trendyol"],
    "moda-tekstil":        ["tiktok", "instagram", "trendyol"],
    "yemek-gida":          ["tiktok", "instagram"],
    "turizm":              ["tiktok", "instagram"],
    "insaat-gayrimenkul":  ["tiktok", "instagram"],
    "otomotiv":            ["tiktok", "instagram"],
    "teknoloji":           ["tiktok", "instagram", "trendyol"],
    "saglik":              ["tiktok", "instagram"],
    "egitim":              ["tiktok", "instagram"],
    "finans":              ["tiktok", "instagram"],
    "hizmet":              ["tiktok", "instagram"],
    "genel":               ["tiktok", "instagram"],
}


def _actor_input(actor_key: str, sector_slug: str, keywords: list[str]) -> dict:
    """Her aktör için temel input payload'ı üret. Aktörlerin input şeması
    büyük oranda `{"search": ...}` veya `{"startUrls": [...]}` şeklinde.
    Basit + güvenli varsayılanlar: Türkçe arama terimi + küçük result limit.
    """
    term = (keywords[0] if keywords else sector_slug).replace("-", " ")

    if actor_key == "tiktok":
        return {"hashtags": [term], "resultsPerPage": 20, "region": "TR"}
    if actor_key == "instagram":
        return {"search": term, "searchType": "hashtag", "resultsLimit": 20}
    if actor_key == "twitter":
        return {"country": "turkey", "maxItems": 20}
    if actor_key in {"trendyol", "hepsiburada", "n11", "ciceksepeti", "dolap"}:
        return {"search": [term], "maxItems": 20, "proxy": {"useApifyProxy": True}}
    if actor_key == "sahibinden":
        return {"search": [term], "maxItems": 20}
    if actor_key == "yemeksepeti":
        return {"search": [term], "maxItems": 20, "city": "istanbul"}
    if actor_key == "booking":
        return {"search": "istanbul", "maxItems": 20, "currency": "TRY", "language": "tr"}
    return {"search": term, "maxItems": 20}


def _normalize_items(actor_key: str, raw: list[dict]) -> list[dict]:
    """Aktör çıktısını ortak şemaya indir: title, url, source, snippet."""
    out: list[dict] = []
    for it in raw[:25]:
        if not isinstance(it, dict):
            continue
        title = (
            it.get("text")
            or it.get("title")
            or it.get("name")
            or it.get("displayName")
            or it.get("caption")
            or it.get("description")
            or ""
        )
        title = str(title).strip()[:180]
        if not title:
            continue
        url = it.get("url") or it.get("webVideoUrl") or it.get("link") or ""
        snippet = (
            it.get("description")
            or it.get("caption")
            or it.get("subtitle")
            or it.get("snippet")
            or ""
        )
        out.append({
            "title": title,
            "url": str(url)[:300] if url else "",
            "source": f"Apify/{actor_key}",
            "snippet": str(snippet)[:220],
        })
    return out


async def _run_one_actor(actor_key: str, sector_slug: str, keywords: list[str]) -> tuple[str, list[dict], float]:
    actor_id = _ACTOR_IDS.get(actor_key)
    if not actor_id:
        return actor_key, [], 0.0
    payload = _actor_input(actor_key, sector_slug, keywords)
    try:
        raw = await apify_client.run_actor(actor_id, payload, timeout=180)
    except Exception as e:
        logger.warning("layer_c actor run failed key=%s err=%s", actor_key, e)
        raw = []
    items = _normalize_items(actor_key, raw)
    cost = _ACTOR_COST_USD.get(actor_key, 0.05) if items else 0.0
    return actor_key, items, cost


async def _synthesize_with_claude(
    items: list[dict], sector_name: str, brand_name: str
) -> tuple[list[dict], int, int]:
    """Ham aktör item'larını 12 trende sentezle. Layer A/B ile aynı robust pattern."""
    if not items or not settings.ANTHROPIC_API_KEY:
        fallback = [
            {
                "title": f"{sector_name} içerik fırsatı {i + 1}",
                "source": it.get("source", "Apify"),
                "relevance_score": 70,
                "summary": (it.get("snippet") or "")[:160],
                "content_opportunity": "Bu trendi markanızın bakış açısıyla yorumlayın.",
                "suggested_prompt": f"{it['title']} hakkında {brand_name} için bir post",
            }
            for i, it in enumerate(items[:12])
        ]
        return fallback, 0, 0

    try:
        import anthropic
    except ImportError:
        return [], 0, 0

    lines: list[str] = []
    for it in items[:60]:
        line = f"[{it.get('source','')}] {it.get('title','')}"
        sn = it.get("snippet") or ""
        if sn:
            line += f" — {sn[:140]}"
        lines.append(line[:260])
    bulk = "\n".join(lines)

    system = (
        f"Sen {brand_name} markası için kıdemli sosyal medya stratejistisin. "
        f"Sektör: {sector_name}. Yanıtını SADECE geçerli JSON dizisi olarak döndür."
    )
    user_msg = (
        f"Bu ay toplanan {sector_name} sektörü ham sinyalleri (her satırın başındaki "
        f"köşeli parantez içi KAYNAK etiketidir):\n{bulk}\n\n"
        f"Görev: {brand_name} markasının bu ay konuşabileceği EN GÜÇLÜ 12 trendi seç. "
        "FARKLI kaynaklardan dengeli bir dağılım olmalı — tek bir kaynağa yığılma. "
        "Tekrarları birleştir, alakasızları ele. Her biri için içerik fırsatı ve prompt öner.\n\n"
        "KRİTİK KAYNAK KURALI:\n"
        "- Her trendin 'source' alanı, o trendin geldiği ham satırın başındaki "
        "[KAYNAK] etiketinden BİREBİR kopyalanmalı (örn. 'Apify/tiktok', "
        "'Apify/instagram', 'Apify/trendyol').\n"
        "- Birden fazla kaynaktan gelen tekrarı birleştirirsen source='Karma' yaz.\n"
        "- Tüm 12 trende aynı source'u yazma — çeşitlilik zorunlu.\n\n"
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
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY, timeout=90.0)
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=6000,
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
                it.setdefault("source", "Apify")
                it.setdefault("relevance_score", 70)
            logger.info(
                "layer_c synthesis ok sector=%s trends=%d attempt=%d",
                sector_name, len(parsed), attempt + 1,
            )
            return parsed[:12], pt, ct
        except Exception as e:
            last_err = e
            logger.warning(
                "layer_c synthesis failed (attempt %d) sector=%s err=%s raw_head=%s",
                attempt + 1, sector_name, e, (raw or "")[:200],
            )
            await asyncio.sleep(1.5)
    logger.error("layer_c synthesis gave up sector=%s last_err=%s", sector_name, last_err)
    return [], 0, 0


async def generate_monthly_report(
    db: asyncpg.Connection,
    account_id: str,
    brand_id: UUID,
) -> dict[str, Any]:
    """Bir marka için Layer C aylık raporu üret. Çağıran endpoint ownership +
    quota kontrolü yapar. sector_reports satırı burada yaratılır/güncellenir."""
    brand_row = await db.fetchrow(
        """
        SELECT b.id, b.name, b.sector, b.sector_id, s.slug AS sector_slug,
               s.display_name AS sector_name, s.keywords
        FROM social.brands b
        LEFT JOIN social.sectors s ON s.id = b.sector_id
        WHERE b.id = $1
        """,
        brand_id,
    )
    if not brand_row:
        raise ValueError("brand not found")
    brand = dict(brand_row)
    sector_slug = brand.get("sector_slug") or "genel"
    sector_name = brand.get("sector_name") or sector_slug
    brand_name = brand.get("name") or "Marka"
    keywords: list[str] = list(brand.get("keywords") or [])
    sector_id = brand.get("sector_id")

    # Pending satır oluştur (status=generating)
    report_id = uuid4()
    await db.execute(
        """
        INSERT INTO social.sector_reports
            (id, account_id, brand_id, sector_id, status, generated_at)
        VALUES ($1::uuid, $2::uuid, $3::uuid, $4::uuid, 'generating', now())
        """,
        report_id, account_id, brand_id, sector_id,
    )

    try:
        # 1. Aktörleri paralel çalıştır
        actor_keys = SECTOR_ACTOR_MAP.get(sector_slug, SECTOR_ACTOR_MAP["genel"])
        tasks = [_run_one_actor(k, sector_slug, keywords) for k in actor_keys]
        actor_results = await asyncio.gather(*tasks, return_exceptions=False)

        all_items: list[dict] = []
        apify_cost = 0.0
        actor_summary: list[dict] = []
        for key, items, cost in actor_results:
            all_items.extend(items)
            apify_cost += cost
            actor_summary.append({"name": key, "count": len(items)})

        # Dedupe
        seen: set[str] = set()
        deduped: list[dict] = []
        for it in all_items:
            k = (it.get("title") or "").lower().strip()[:80]
            if not k or k in seen:
                continue
            seen.add(k)
            deduped.append(it)

        # 2. Claude sentez
        trends, prompt_tokens, completion_tokens = await _synthesize_with_claude(
            deduped, sector_name, brand_name,
        )
        claude_cost = round(
            (prompt_tokens * 1.0 + completion_tokens * 5.0) / 1_000_000, 4,
        )

        # 3. PDF render
        generated_at = datetime.now(timezone.utc)
        pdf_data = {
            "sector_name": sector_name,
            "brand_name": brand_name,
            "report_id_short": str(report_id)[:8],
            "generated_at_tr": generated_at.strftime("%d.%m.%Y %H:%M UTC"),
            "trends": trends,
            "actor_summary": actor_summary,
            "raw_count": len(deduped),
            "apify_cost": apify_cost,
            "claude_cost": claude_cost,
        }
        pdf_bytes = render_sector_report(pdf_data)

        # 4. R2 upload
        r2_path = f"sector-reports/{account_id}/{report_id}.pdf"
        pdf_url = r2.upload(pdf_bytes, r2_path, "application/pdf")

        # 5. Satırı ready olarak güncelle
        await db.execute(
            """
            UPDATE social.sector_reports
            SET status = 'ready',
                pdf_url = $2,
                apify_cost_usd = $3,
                claude_cost_usd = $4
            WHERE id = $1::uuid
            """,
            report_id, pdf_url, apify_cost, claude_cost,
        )

        return {
            "report_id": str(report_id),
            "status": "ready",
            "pdf_url": pdf_url,
            "sector_slug": sector_slug,
            "trends_count": len(trends),
            "raw_count": len(deduped),
            "actor_summary": actor_summary,
            "apify_cost_usd": round(apify_cost, 4),
            "claude_cost_usd": claude_cost,
            "total_cost_usd": round(apify_cost + claude_cost, 4),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
        }
    except Exception as e:
        logger.exception("layer_c generate_monthly_report failed brand=%s", brand_id)
        await db.execute(
            """
            UPDATE social.sector_reports
            SET status = 'failed', error_message = $2
            WHERE id = $1::uuid
            """,
            report_id, str(e)[:500],
        )
        raise
