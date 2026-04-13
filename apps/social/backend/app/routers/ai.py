"""AI helper endpoints — content idea suggestions + website analysis via Claude."""

from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.security import get_current_user
from app.models.schemas import OkResponse

router = APIRouter(prefix="/ai", tags=["ai"])


def _parse_brand_kit(raw) -> dict:
    """asyncpg bazen JSONB kolonunu string olarak döndürür — her ikisini de handle et."""
    if not raw:
        return {}
    if isinstance(raw, str):
        import json
        return json.loads(raw)
    return dict(raw)


class AnalyzeWebsiteRequest(BaseModel):
    url: str


@router.post("/analyze-website", response_model=OkResponse)
async def analyze_website(
    payload: AnalyzeWebsiteRequest,
    user: dict = Depends(get_current_user),
):
    """Fetch a website and extract brand info using Claude."""
    import re

    import httpx

    url = payload.url.strip()
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    html = ""
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            html = resp.text[:8000]  # cap at 8k chars
    except Exception:
        raise HTTPException(status_code=422, detail="Web sitesine ulaşılamadı")

    # Strip tags to plain text for Claude
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()[:4000]

    system_prompt = (
        "Sen bir marka analisti olarak web sitesi içeriğinden marka bilgilerini çıkarıyorsun. "
        "Yanıtını SADECE JSON olarak ver, başka hiçbir şey yazma."
    )
    user_prompt = (
        f"Bu web sitesi içeriğinden marka bilgilerini çıkar:\n\n{text}\n\n"
        "Şu JSON formatında döndür:\n"
        '{"name": "marka adı", "description": "1-2 cümle açıklama", '
        '"sector": "sektör (örn: Teknoloji, Gıda, Tekstil, vb)", '
        '"colors": ["#hex1", "#hex2", "#hex3"], '
        '"tonality": "professional|friendly|fun|informative"}\n\n'
        "Eğer bilgi bulamazsan ilgili alanı boş string bırak. Renkler için sitenin görsel renklerini tahmin et."
    )

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        import json

        raw = message.content[0].text.strip()
        # Extract JSON block if wrapped in ```
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
    except Exception:
        data = {"name": "", "description": "", "sector": "", "colors": [], "tonality": "professional"}

    return OkResponse(data=data)


class IdeaRequest:
    def __init__(self, brand_id: UUID, content_category: str = "product", count: int = 3):
        self.brand_id = brand_id
        self.content_category = content_category
        self.count = count


from pydantic import BaseModel


class SuggestIdeasRequest(BaseModel):
    brand_id: UUID
    content_category: str = "product"  # product | service | corporate
    count: int = 3


CATEGORY_TR = {
    "product": "ürün tanıtımı",
    "service": "hizmet tanıtımı",
    "corporate": "firma tanıtımı",
}


@router.post(
    "/suggest-ideas",
    response_model=OkResponse,
    dependencies=[Depends(limiter(30, 3600))],  # 30/saat
)
async def suggest_ideas(
    payload: SuggestIdeasRequest,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Generate content idea suggestions using Claude based on brand kit."""
    brand = await db.fetchrow(
        "SELECT name, sector, brand_kit FROM social.brands WHERE id = $1", payload.brand_id
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand_kit = _parse_brand_kit(brand["brand_kit"])
    tonality = brand_kit.get("tonality", "professional")
    hashtags = brand_kit.get("hashtags", [])
    category_tr = CATEGORY_TR.get(payload.content_category, payload.content_category)

    system_prompt = (
        f"Sen bir sosyal medya içerik uzmanısın. Türkçe ve {tonality} bir üslupla "
        f"fikir önerileri üretiyorsun. Her fikir tek cümle, net ve uygulanabilir olmalı."
    )
    user_prompt = (
        f"Marka adı: {brand['name']}\n"
        f"Sektör: {brand['sector'] or 'Belirtilmemiş'}\n"
        f"İçerik kategorisi: {category_tr}\n"
        f"Popüler hashtagler: {', '.join(hashtags[:5]) if hashtags else 'Yok'}\n\n"
        f"Bu marka için {payload.count} farklı sosyal medya içerik fikri öner. "
        f"Sadece numaralı liste olarak yaz, başka açıklama ekleme."
    )

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = message.content[0].text.strip()
        ideas = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            # Strip leading "1. " / "1) " / "- "
            for prefix in ("1. ", "2. ", "3. ", "4. ", "5. ", "1) ", "2) ", "3) ", "- "):
                if line.startswith(prefix):
                    line = line[len(prefix):]
                    break
            if line:
                ideas.append(line)
        ideas = ideas[: payload.count]
    except Exception:
        # Fallback ideas if API unavailable
        ideas = [
            f"{brand['name']} ile fark yaratın — yeni ürünlerimizi keşfedin!",
            f"Müşterilerimizin deneyimlerini sizinle paylaşıyoruz.",
            f"Bugün için özel bir içerik: {category_tr} odaklı paylaşım.",
        ][: payload.count]

    return OkResponse(data={"ideas": ideas})


class GenerateScriptRequest(BaseModel):
    brand_id: UUID
    prompt: str


@router.post("/generate-script", response_model=OkResponse)
async def generate_script_endpoint(
    payload: GenerateScriptRequest,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Claude ile Türkçe video scripti üret."""
    from app.services.faceless_video import generate_script

    brand = await db.fetchrow(
        "SELECT name, sector, brand_kit FROM social.brands WHERE id = $1", payload.brand_id
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand_kit = _parse_brand_kit(brand["brand_kit"])
    brand_kit["sector"] = brand["sector"] or ""

    result = await generate_script(payload.prompt, brand_kit, brand["name"])
    return OkResponse(data=result)
