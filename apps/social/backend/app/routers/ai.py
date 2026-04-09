"""AI helper endpoints — content idea suggestions via Claude."""

from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException

from app.core.config import settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas import OkResponse

router = APIRouter(prefix="/ai", tags=["ai"])


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


@router.post("/suggest-ideas", response_model=OkResponse)
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

    brand_kit = dict(brand["brand_kit"]) if brand["brand_kit"] else {}
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
