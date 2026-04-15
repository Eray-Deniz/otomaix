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


from app.core.utils import parse_brand_kit as _parse_brand_kit


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
    content_type: str = "image"        # image | carousel | video | special_day | quote
    content_category: str = "product"  # product | service | corporate
    prompt: str | None = None          # kullanıcının yazdığı açıklama (varsa)
    document_ids: list[UUID] | None = None
    platforms: list[str] | None = None
    count: int = 5


CATEGORY_TR = {
    "product": "ürün tanıtımı",
    "service": "hizmet tanıtımı",
    "corporate": "firma tanıtımı",
}

CATEGORY_GUIDANCE = {
    "product": (
        "Ürün tanıtımı: somut bir ürünün özelliklerine, faydasına, kullanım "
        "senaryosuna veya müşteri yorumuna odaklan. 'Şu ürün şu sorunu çözer' "
        "formatında fikirler öner. Soyut marka mesajlarından kaçın."
    ),
    "service": (
        "Hizmet tanıtımı: bir hizmetin süreci, sonucu, öncesi/sonrası "
        "karşılaştırması veya uzmanlık göstergesi üzerine kurgula. "
        "'Nasıl çalışıyoruz' ve 'ne kazandırıyoruz' sorularını yanıtla."
    ),
    "corporate": (
        "Firma tanıtımı: marka hikayesi, ekip, değerler, kilometre taşları, "
        "kültür veya kurumsal sosyal sorumluluk odaklı fikirler öner. "
        "Doğrudan satış dili kullanma."
    ),
}

CONTENT_TYPE_TR = {
    "image": "görsel (statik fotoğraf / illüstrasyon)",
    "carousel": "carousel (birden fazla kayan görsel)",
    "video": "kısa video / reel",
    "special_day": "özel gün / bayram kutlaması görseli",
    "quote": "alıntı kartı (metin ağırlıklı)",
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
    """Generate content idea suggestions using Claude based on full context."""
    from app.services.document_processor import get_document_context

    brand = await db.fetchrow(
        "SELECT name, sector, description, brand_kit FROM social.brands WHERE id = $1",
        payload.brand_id,
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand_kit = _parse_brand_kit(brand["brand_kit"])
    tonality = brand_kit.get("tonality", "professional")
    hashtags = brand_kit.get("hashtags", [])
    colors = brand_kit.get("colors") or {}
    category_tr = CATEGORY_TR.get(payload.content_category, payload.content_category)
    category_guidance = CATEGORY_GUIDANCE.get(payload.content_category, "")
    content_type_tr = CONTENT_TYPE_TR.get(payload.content_type, payload.content_type)
    platforms_str = ", ".join(payload.platforms) if payload.platforms else "belirtilmemiş"

    color_parts: list[str] = []
    for key in ("primary", "secondary", "accent"):
        val = colors.get(key)
        if val:
            color_parts.append(f"{key}: {val}")
    colors_str = ", ".join(color_parts) if color_parts else "belirtilmemiş"

    # Doküman bağlamı (varsa)
    doc_context = ""
    if payload.document_ids:
        base_query = payload.prompt or f"{brand['name']} sosyal medya içerik fikirleri"
        doc_context = await get_document_context(payload.document_ids, base_query, db) or ""

    system_prompt = (
        f"Sen Türk KOBİ'lerine sosyal medya içeriği üreten bir uzmansın. "
        f"Türkçe ve {tonality} bir üslupla, verilen tüm bağlamı dikkate alarak "
        f"içerik fikri önerileri üretiyorsun. "
        f"Her fikir tek cümle, net, uygulanabilir ve seçilen içerik tipine uygun olmalı.\n\n"
        "DİL KURALI (çok önemli): Yanıtın tamamen Türkçe olmalı. "
        "İngilizce veya yabancı kökenli terimler kullanma. "
        "Yaygın Türkçe karşılıkları kullan: 'content creator' yerine 'içerik üretici', "
        "'split-screen' yerine 'ikiye bölünmüş ekran', 'infografik' yerine 'bilgi görseli', "
        "'screenshot' yerine 'ekran görüntüsü', 'caption' yerine 'başlık', "
        "'engagement' yerine 'etkileşim', 'feed' yerine 'akış', 'story' yerine 'hikaye', "
        "'reel' yerine 'kısa video'. Marka adları ve platform isimleri (Instagram, TikTok vb.) "
        "orijinal kalabilir. Gerçekliği olmayan sayısal iddialar ('%300 artış', '30 saatten 2 saate' "
        "gibi) uydurma — sadece somut özellik ve faydalardan bahset."
    )

    user_prompt_parts = [
        f"Marka adı: {brand['name']}",
        f"Sektör: {brand['sector'] or 'Belirtilmemiş'}",
        f"Marka açıklaması: {brand['description'] or 'Belirtilmemiş'}",
        f"Marka renkleri: {colors_str}",
        f"İçerik tipi: {content_type_tr}",
        f"İçerik kategorisi: {category_tr}",
        f"Kategori talimatı: {category_guidance}" if category_guidance else "",
        f"Hedef platformlar: {platforms_str}",
        f"Marka tonu: {tonality}",
        f"Popüler hashtagler: {', '.join(hashtags[:5]) if hashtags else 'Yok'}",
    ]
    user_prompt_parts = [p for p in user_prompt_parts if p]

    if payload.prompt and payload.prompt.strip():
        user_prompt_parts.append(f"\nKullanıcının belirttiği konu/yön: {payload.prompt.strip()}")

    if doc_context:
        user_prompt_parts.append(
            f"\n=== REFERANS DOKÜMAN İÇERİĞİ (MUTLAKA KULLAN) ===\n{doc_context}\n=== DOKÜMAN SONU ==="
        )

    final_instruction = (
        f"\nYukarıdaki tüm bilgileri göz önüne alarak bu marka için "
        f"{payload.count} farklı sosyal medya içerik fikri öner. "
        f"Öneriler '{content_type_tr}' formatına uygun olmalı — "
        f"örneğin video tipiyse görsel tasarım değil video senaryosu/konu fikirleri öner. "
    )
    if doc_context:
        final_instruction += (
            "ÖNEMLİ: Referans dokümanda geçen spesifik ürün adları, hizmet başlıkları, "
            "rakamlar, özellikler ve örnekler fikirlerde açıkça yer almalı. "
            "Genel marka mesajları yerine dokümandaki somut içeriklere dayan. "
            "Her fikir, dokümandan aldığın bir veri/başlık/örneğe referans vermeli. "
        )
    final_instruction += "Sadece numaralı liste olarak yaz, başka açıklama ekleme."
    user_prompt_parts.append(final_instruction)

    user_prompt = "\n".join(user_prompt_parts)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = message.content[0].text.strip()
        ideas = []
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            import re
            line = re.sub(r"^\d+[\.\)]\s*", "", line)  # "1. " / "1) " gibi önekleri kaldır
            line = re.sub(r"^[-•]\s*", "", line)        # "- " / "• " öneklerini kaldır
            if line:
                ideas.append(line)
        ideas = ideas[: payload.count]
    except Exception:
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
