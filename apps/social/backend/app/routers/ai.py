"""AI helper endpoints — content idea suggestions + website analysis via Claude."""

import asyncio
import logging
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator

from app.core.config import settings
from app.core.database import get_db
from app.core.rate_limit import limiter
from app.core.security import assert_brand_owned, get_current_user
from app.core.templates_data import SECTOR_GUIDANCE, get_template_by_id
from app.routers.sectors import fetch_sub_sector_candidates
from app.services.sector_packages import render_package_block, resolve_package_context
from app.models.schemas import OkResponse

router = APIRouter(prefix="/ai", tags=["ai"])

logger = logging.getLogger(__name__)

# Sağlayıcı çağrısının üst sınırı. Çağrı senkron istemciyle yapılır, o yüzden
# olay döngüsünün DIŞINDA koşturulur — aksi hâlde asılı bir sağlayıcı tek bir
# istekle işçiyi süresiz tutardı.
_SUGGEST_TIMEOUT_SECONDS = 20.0

# Öneri ucunun kullanıcıya dönen TEK arıza mesajı. İki ayrı arıza dalı (çağrı
# düştü / yanıt sözleşmeye uymadı) aynı cümleyi gösterir — çünkü kullanıcı için
# ikisi de aynı şeydir. Metin tek yerde durur: iki kopya ayrışırsa aynı durum
# iki farklı cümleyle anlatılırdı.
_SUGGEST_UNAVAILABLE_DETAIL = (
    "Alt sektör önerisi şu an alınamıyor; listeden seçebilirsiniz."
)


from app.core.utils import parse_brand_kit as _parse_brand_kit


class AnalyzeWebsiteRequest(BaseModel):
    url: str


class SuggestSubSectorRequest(BaseModel):
    """Web sitesiz geri düşüşün girdisi (spec §7.1): ad + açıklama + kök sektör.

    Alanlar SINIRLI: bu uç ücretli bir model çağrısı doğurur, dolayısıyla
    girdi boyu bir maliyet yüzeyidir. Sınırlar marka formunun kendi
    gerçekleriyle uyumlu; darlaştırmak değil, sınırsızlığı kapatmak amaç.
    """

    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    sector: str | None = Field(default=None, max_length=200)

    @field_validator("name")
    @classmethod
    def _name_not_blank(cls, value: str) -> str:
        # Yalnız boşluktan oluşan ad, modele sorulacak hiçbir şey taşımaz —
        # çağrı yapılmadan reddedilir.
        if not value.strip():
            raise ValueError("name boş olamaz")
        return value


def _candidate_prompt_block(candidates: list[dict]) -> str:
    """Kapalı listenin prompt karşılığı — İKİ yol da bunu kullanır.

    Aday yoksa BOŞ string döner ve çağıran alt sektörü hiç sormaz: boş listeden
    seçim istemek modeli uydurmaya davet ederdi.
    """
    if not candidates:
        return ""
    lines = "\n".join(f"- {row['slug']}: {row['display_name']}" for row in candidates)
    return (
        "\n\nAlt sektör için YALNIZ şu listeden seç ve slug'ı AYNEN yaz:\n"
        f"{lines}\n"
        "Hiçbiri uymuyorsa `sub_sector` alanını boş string bırak. "
        "Listede olmayan bir değer YAZMA."
    )


def _suggestion_fields(suggestion: dict | None) -> dict:
    """Öneri alanlarının SABİT şekli — üç alan hep vardır, ya dolu ya `null`."""
    return {
        "sub_sector_id": suggestion["id"] if suggestion else None,
        "sub_sector_slug": suggestion["slug"] if suggestion else None,
        "sub_sector_display_name": suggestion["display_name"] if suggestion else None,
    }


def _resolve_sub_sector_suggestion(raw, candidates: list[dict]) -> dict | None:
    """Model önerisinin KAPALI doğrulaması (spec §7.1).

    İki dönüş biçimi vardır: aday kümedeki bir satır ya da BOŞ. Üçüncü biçim
    yoktur — serbest metin, uydurma slug, tip dışı değer ve aday listesi
    boşken gelen her öneri aynı yere, boşa düşer.

    Kapı listenin KENDİSİNE karşı çalışır, ayrı bir kopyaya değil: prompt'a
    gömülen küme ile burada eşleştirilen küme aynı canlı sorgunun çıktısıdır,
    yani ikisi arasında bayatlama penceresi yoktur.
    """
    if not isinstance(raw, str):
        return None
    slug = raw.strip()
    if not slug:
        return None
    for row in candidates:
        if row["slug"] == slug:
            return row
    return None


@router.post("/analyze-website", response_model=OkResponse)
async def analyze_website(
    payload: AnalyzeWebsiteRequest,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Fetch a website and extract brand info using Claude."""
    import re

    from app.services.safe_fetch import fetch_public_url

    # Çekim TEK güvenli kapıdan geçer (SSRF — security review 2026-08-26, S1).
    # Reddin SEBEBİ çağırana verilmez: "özel adrese çözülüyor" ile "isim yok"
    # arasındaki fark, iç ağın haritasını dışarı sızdıran bir yan kanaldır.
    try:
        html = (await fetch_public_url(payload.url, timeout=10))[:8000]
    except Exception:
        raise HTTPException(status_code=422, detail="Web sitesine ulaşılamadı")

    # Strip tags to plain text for Claude
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()[:4000]

    # Aday küme CANLI sorgudan gelir ve prompt'a KAPALI liste olarak gömülür
    # (plan "bağladığı teknik kararlar" 7). Aday yoksa alt sektör hiç sorulmaz:
    # boş listeden seçim istemek modeli uydurmaya davet ederdi.
    candidates = await fetch_sub_sector_candidates(db)
    sub_sector_rule = _candidate_prompt_block(candidates)
    sub_sector_field = (
        '"sub_sector": "aşağıdaki listeden TAM slug veya boş string"'
        if candidates
        else '"sub_sector": ""'
    )

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
        '"tonality": "professional|friendly|fun|informative", '
        f'{sub_sector_field}}}\n\n'
        "Eğer bilgi bulamazsan ilgili alanı boş string bırak. "
        "Renkler için sitenin görsel renklerini tahmin et."
        f"{sub_sector_rule}"
    )

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=512,
            cache_control={"type": "ephemeral"},
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
        if not isinstance(data, dict):
            # Model geçerli JSON ama nesne-olmayan bir gövde döndürebilir
            # (liste, sayı). Aşağıdaki alan yazımı o gövdede patlardı; bilinen
            # boş şablona düşmek fail-closed davranıştır.
            raise ValueError("analyze-website yanıtı JSON nesnesi değil")
    except Exception:
        data = {"name": "", "description": "", "sector": "", "colors": [], "tonality": "professional"}

    # Öneri alanı HER YOLDA aynı kapıdan geçer (model hatası, geçersiz JSON,
    # aday-dışı öneri) ve yanıt şekli sabittir: üç alan hep vardır, ya doludur
    # ya `null`. Ham `sub_sector` değeri istemciye SIZMAZ.
    suggestion = _resolve_sub_sector_suggestion(data.pop("sub_sector", None), candidates)
    data.update(_suggestion_fields(suggestion))

    return OkResponse(data=data)


@router.post(
    "/suggest-sub-sector",
    response_model=OkResponse,
    dependencies=[Depends(limiter(20, 3600))],  # 20/saat — kardeş uçlarla aynı ev kuralı
)
async def suggest_sub_sector(
    payload: SuggestSubSectorRequest,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Web sitesiz geri düşüşün öneri ucu (spec §7.1).

    Site analizi yapılamayan kullanıcı da modelden öneri alır; kısıt site
    yolununkiyle AYNIdır — kapalı liste prompt'a gömülür ve dönüş aynı
    doğrulayıcıdan geçer. Ayrı ve gevşek bir ikinci yol AÇILMAZ; bu yüzden
    liste üretimi ve doğrulama iki uçta da tek kaynaktan gelir.

    Aday kümesi boşsa model HİÇ çağrılmaz: sorulacak bir şey yoktur ve
    boşuna bir model çağrısı ücret yakar.
    """
    candidates = await fetch_sub_sector_candidates(db)
    if not candidates:
        return OkResponse(data=_suggestion_fields(None))

    system_prompt = (
        "Sen bir marka analisti olarak marka bilgilerinden alt sektör seçiyorsun. "
        "Yanıtını SADECE JSON olarak ver, başka hiçbir şey yazma."
    )
    user_prompt = (
        "Bu marka bilgilerinden alt sektörü seç:\n"
        f"Ad: {payload.name}\n"
        f"Açıklama: {payload.description or '-'}\n"
        f"Sektör: {payload.sector or '-'}\n\n"
        'Şu JSON formatında döndür:\n{"sub_sector": "TAM slug veya boş string"}'
        f"{_candidate_prompt_block(candidates)}"
    )

    def _call_model() -> str:
        import anthropic

        # `max_retries=0` BİLİNÇLİ: dış `wait_for` yalnız BEKLEMEYİ keser, senkron
        # çağrıyı durduramaz — iş parçacığı çağrı bitene kadar tutulur. SDK
        # varsayılanı iki yeniden denemedir, yani işgal sessizce üç katına
        # çıkardı. Süre sınırının tek sahibi dışarıdaki kapıdır.
        client = anthropic.Anthropic(
            api_key=settings.ANTHROPIC_API_KEY,
            timeout=_SUGGEST_TIMEOUT_SECONDS,
            max_retries=0,
        )
        message = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=128,
            cache_control={"type": "ephemeral"},
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text.strip()

    try:
        # Senkron istemci ayrı bir iş parçacığında; süre sınırı DIŞARIDAN
        # uygulanır ki istemcinin kendi zaman aşımı çalışmasa bile uç yanıtsız
        # kalmasın.
        raw = await asyncio.wait_for(
            asyncio.to_thread(_call_model), timeout=_SUGGEST_TIMEOUT_SECONDS
        )
    except Exception as exc:
        # Sağlayıcı arızası GEÇERLİ "eşleşme yok" ile aynı yanıta düşemez:
        # düşseydi bozuk bir API anahtarı kullanıcıya "uygun öneri çıkmadı"
        # diye görünür ve hiçbir yerde iz bırakmazdı. Prompt log'lanmaz.
        logger.error("suggest_sub_sector: sağlayıcı çağrısı başarısız: %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_SUGGEST_UNAVAILABLE_DETAIL,
        ) from exc

    raw_field = None
    try:
        import json

        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw)
        # Sözleşme TEK bir geçerli boş biçim tanımlar: BOŞ STRING. Anahtarı hiç
        # taşımayan, `null` ya da yanlış tipte taşıyan yanıt sağlayıcı tarafının
        # ihlalidir — "aday yok" DEĞİLDİR. İkisini aynı yere düşürmek bozuk bir
        # entegrasyonu normal kullanıcı sonucu gibi gösterirdi.
        if not isinstance(parsed, dict) or not isinstance(parsed.get("sub_sector"), str):
            raise ValueError("yanıt `sub_sector` metnini taşımıyor")
        raw_field = parsed["sub_sector"]
    except Exception as exc:
        # Ayrıştırma hatası da sağlayıcı tarafının arızasıdır (sözleşmeye
        # uymayan yanıt), geçerli bir "eşleşme yok" DEĞİLDİR.
        logger.error("suggest_sub_sector: model yanıtı ayrıştırılamadı: %s", type(exc).__name__)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_SUGGEST_UNAVAILABLE_DETAIL,
        ) from exc

    return OkResponse(
        data=_suggestion_fields(_resolve_sub_sector_suggestion(raw_field, candidates))
    )


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
    # Phase 7 — template-aware fikir önerileri
    template_id: str | None = None
    template_fields: dict | None = None


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

    # Sahiplik kapısı paket enjeksiyonundan ÖNCE koşar. Kimlik doğrulama yetki
    # DEĞİLDİR: bu uç paket-farkındalığı kazandığı an, başkasının markasının
    # paket içeriği (spec §3.7'ye göre içsel) yabancı bir kiracıya akardı.
    # 404 (403 değil) — başkasının kaynağının varlığı sızmasın (yerleşik kural).
    await assert_brand_owned(db, user, payload.brand_id)

    brand = await db.fetchrow(
        """
        SELECT b.id, b.name, b.sector, b.description, b.brand_kit,
               b.sub_sector_id, s.slug AS sector_slug
        FROM social.brands b
        LEFT JOIN social.sectors s ON s.id = b.sector_id
        WHERE b.id = $1
        """,
        payload.brand_id,
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand_kit = _parse_brand_kit(brand["brand_kit"])
    package_context = await resolve_package_context(db, dict(brand))
    tonality = brand_kit.get("tonality", "professional")
    hashtags = brand_kit.get("hashtags", [])
    colors = brand_kit.get("colors") or {}
    content_type_tr = CONTENT_TYPE_TR.get(payload.content_type, payload.content_type)
    platforms_str = ", ".join(payload.platforms) if payload.platforms else "belirtilmemiş"

    # Phase 7 — template varsa yükle; kategori guidance yalnızca template yoksa kullanılır
    template = get_template_by_id(payload.template_id) if payload.template_id else None
    if template:
        category_tr = template.name
        category_guidance = ""  # template guidance Tier 2'de enjekte edilecek
    else:
        category_tr = CATEGORY_TR.get(payload.content_category, payload.content_category)
        category_guidance = CATEGORY_GUIDANCE.get(payload.content_category, "")

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
        doc_context = (
            await get_document_context(
                payload.document_ids, base_query, db, brand_id=payload.brand_id
            )
            or ""
        )

    # System prompt: sabit talimatlar (prompt caching için ayrı blok)
    _STATIC_RULES = (
        "Sen Türk KOBİ'lerine sosyal medya içeriği üreten bir uzmansın. "
        "Her fikir tek cümle, net, uygulanabilir ve seçilen içerik tipine uygun olmalı.\n\n"
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
    system_prompt = [
        {"type": "text", "text": _STATIC_RULES, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": f"Türkçe ve {tonality} bir üslupla, verilen tüm bağlamı dikkate alarak içerik fikri önerileri üretiyorsun."},
    ]

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
        "Her seferinde farklı açılardan, yaratıcı ve çeşitli fikirler üret — "
        "genel kalıpları tekrarlama, özgün ve sürpriz öneriler sun. "
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

    # User mesajını marka bağlamı (cache) + dinamik kısım olarak ayır
    brand_context_parts = [
        f"Marka adı: {brand['name']}",
        f"Sektör: {brand['sector'] or 'Belirtilmemiş'}",
        f"Marka açıklaması: {brand['description'] or 'Belirtilmemiş'}",
        f"Marka renkleri: {colors_str}",
        f"Marka tonu: {tonality}",
        f"Popüler hashtagler: {', '.join(hashtags[:5]) if hashtags else 'Yok'}",
    ]

    # Phase 7 — sektör rehberi + şablon guidance Tier 2'de (cache hit için)
    #
    # Yan-yana basım yasağının FİKİR ucu (spec §4.1): aktif paket varken kök
    # rehber basılmaz, paket onun yerine geçer. Aksi hâlde öneri kök rehberle,
    # üretim paketle konuşurdu — iki ses ayrışması. Tek kapı burada da
    # çözümleyicinin sonucudur; ikinci bir koşul yazılmaz.
    if package_context is not None:
        brand_context_parts.append(
            render_package_block(
                package_context, surface="idea", channels=brand_kit.get("channels")
            )
        )
    else:
        sector_slug = brand["sector_slug"]
        if sector_slug and sector_slug in SECTOR_GUIDANCE:
            brand_context_parts.append(f"\n--- SEKTÖR REHBERİ ({sector_slug}) ---")
            brand_context_parts.append(SECTOR_GUIDANCE[sector_slug])

    if template:
        brand_context_parts.append(f"\n--- ŞABLON TALİMATI ({template.name}) ---")
        brand_context_parts.append(template.prompt.guidance)
        if template.defaults.suggestedCTAs:
            brand_context_parts.append(
                f"Önerilen CTA'lar: {', '.join(template.defaults.suggestedCTAs)}"
            )
        if template.defaults.suggestedHashtags:
            brand_context_parts.append(
                f"Önerilen hashtagler: {', '.join(template.defaults.suggestedHashtags)}"
            )

    brand_context = "\n".join(brand_context_parts)

    # Phase 7 — template_fields Tier 3 dinamik bloğa eklenir
    dynamic_prefix_parts: list[str] = []
    if template and payload.template_fields:
        dynamic_prefix_parts.append("=== YAPISAL VERİLER (EN YÜKSEK ÖNCELİK) ===")
        for field in template.formFields:
            value = payload.template_fields.get(field.id)
            if value is not None and value != "":
                suffix = f" {field.suffix}" if field.suffix else ""
                dynamic_prefix_parts.append(f"{field.label}: {value}{suffix}")
        dynamic_prefix_parts.append("=== VERİ SONU ===\n")

    dynamic_text = "\n".join(dynamic_prefix_parts) + user_prompt if dynamic_prefix_parts else user_prompt

    user_content = [
        {"type": "text", "text": brand_context, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": dynamic_text},
    ]

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=1024,
            temperature=1.0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
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
    from app.services.short_video import generate_script

    brand = await db.fetchrow(
        "SELECT name, sector, brand_kit FROM social.brands WHERE id = $1", payload.brand_id
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand_kit = _parse_brand_kit(brand["brand_kit"])
    brand_kit["sector"] = brand["sector"] or ""

    result = await generate_script(payload.prompt, brand_kit, brand["name"])
    return OkResponse(data=result)
