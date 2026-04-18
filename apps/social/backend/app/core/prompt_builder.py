"""Phase 7 — Template-aware prompt builder.

Handles:
- Template guidance injection
- SECTOR_GUIDANCE injection
- Structured form field data
- Platform-specific caption instructions
- RAG document priority
- 3-tier prompt caching (Tier 1 system, Tier 2 brand context, Tier 3 dynamic)

Consumers:
- posts.py:_build_image_prompt (Sprint 3) — kısa image prompt inşası
- caption endpoint (Sprint 4) — Tier 1/2/3 bloklarını Claude'a yollar
- ai.py:suggest_ideas (Sprint 3) — template_id varsa Tier 2'ye şablon guidance ekler
"""
from app.core.templates_data import SECTOR_GUIDANCE
from app.models.templates import Template


# Tier 1 — Static system prompt (cached, same for all calls)
_SYSTEM_RULES = """Sen Türk KOBİ'lerine sosyal medya içeriği üreten bir uzmansın.

DİL KURALI (çok önemli): Yanıtın tamamen Türkçe olmalı.
İngilizce veya yabancı kökenli terimler kullanma. Yaygın Türkçe karşılıkları
kullan: 'content creator' yerine 'içerik üretici', 'caption' yerine 'başlık',
'engagement' yerine 'etkileşim', 'story' yerine 'hikaye', 'reel' yerine
'kısa video'. Marka adları ve platform isimleri orijinal kalabilir.

YASAK: Gerçekliği olmayan sayısal iddialar ('%300 artış', '30 saatten 2 saate')
uydurma — sadece somut özellik ve faydalardan bahset.

ÇIKTI FORMATI: Her zaman JSON döndür. Başka açıklama, preamble veya markdown
kullanma.
"""


def build_system_prompt() -> list[dict]:
    """Tier 1 — cached system prompt."""
    return [
        {
            "type": "text",
            "text": _SYSTEM_RULES,
            "cache_control": {"type": "ephemeral"},
        }
    ]


def build_brand_context(
    brand: dict,
    brand_kit: dict,
    template: Template | None,
) -> str:
    """Tier 2 — cached brand + sector + template context.

    This block is reused across calls for the same brand+template combo.
    Cache hit reduces latency and cost significantly.
    """
    parts: list[str] = []

    # Brand info
    brand_name = brand.get("name") or ""
    parts.append(f"Marka: {brand_name}")
    if brand.get("description"):
        parts.append(f"Marka açıklaması: {brand['description']}")

    tonality = brand_kit.get("tonality") or "professional"
    parts.append(f"Marka tonu: {tonality}")

    colors = brand_kit.get("colors") or []
    if isinstance(colors, dict):
        colors_str = ", ".join(f"{k}: {v}" for k, v in colors.items() if v)
    elif isinstance(colors, list):
        colors_str = ", ".join(str(c) for c in colors if c)
    else:
        colors_str = str(colors)
    if colors_str:
        parts.append(f"Marka renkleri: {colors_str}")

    hashtags = brand_kit.get("hashtags") or []
    if hashtags:
        parts.append(f"Marka hashtagleri: {', '.join(hashtags[:5])}")

    # Sector guidance (if brand has sector)
    sector_slug = brand.get("sector_slug")
    if sector_slug and sector_slug in SECTOR_GUIDANCE:
        parts.append(f"\n--- SEKTÖR REHBERİ ({sector_slug}) ---")
        parts.append(SECTOR_GUIDANCE[sector_slug])

    # Template guidance
    if template:
        parts.append(f"\n--- ŞABLON TALİMATI ({template.name}) ---")
        parts.append(template.prompt.guidance)

        if template.defaults.suggestedCTAs:
            parts.append(f"Önerilen CTA'lar: {', '.join(template.defaults.suggestedCTAs)}")
        if template.defaults.suggestedHashtags:
            parts.append(f"Önerilen hashtagler: {', '.join(template.defaults.suggestedHashtags)}")

        # Disclaimer (MANDATORY if present)
        if template.defaults.disclaimer:
            parts.append(
                f"\n⚠️ ZORUNLU DISCLAIMER: Caption sonuna bu metni AYNEN ekle:\n"
                f'"{template.defaults.disclaimer}"'
            )

    return "\n".join(parts)


def build_dynamic_content(
    template: Template | None,
    template_fields: dict | None,
    user_prompt: str | None,
    rag_context: str | None,
    platforms: list[str] | None,
) -> str:
    """Tier 3 — dynamic content (not cached)."""
    parts: list[str] = []

    # Form fields (highest priority per template.prompt.priority)
    if template and template_fields:
        parts.append("=== YAPISAL VERİLER (EN YÜKSEK ÖNCELİK) ===")
        for field in template.formFields:
            value = template_fields.get(field.id)
            if value is not None and value != "":
                suffix = f" {field.suffix}" if field.suffix else ""
                parts.append(f"{field.label}: {value}{suffix}")
        parts.append("=== VERİ SONU ===\n")

    if user_prompt:
        parts.append(f"KULLANICI EK TALİMATI:\n{user_prompt}\n")

    if rag_context:
        parts.append(f"=== REFERANS DOKÜMAN ===\n{rag_context}\n=== DOKÜMAN SONU ===\n")

    if template:
        priority = template.prompt.priority
        parts.append(f"ÖNCELİK SIRASI (çatışma durumunda): {' > '.join(priority)}\n")

    if template and template.platformOverrides and platforms:
        parts.append(build_platform_instructions(template.platformOverrides, platforms))

    return "\n".join(parts)


def build_platform_instructions(
    overrides: dict,
    platforms: list[str],
) -> str:
    """Build per-platform caption rules for Claude."""
    style_map = {
        "long": "200-500 kelime, profesyonel, detaylı",
        "medium": "50-150 kelime, emoji kullanılabilir",
        "short": "40-100 karakter, vurucu, hook'lu",
    }

    parts = ["=== PLATFORM-SPESİFİK CAPTION'LAR ==="]
    parts.append(
        "Aşağıdaki her platform için AYRI caption üret. "
        "Response'da JSON formatında `platform_captions` objesi dön, "
        "her platform için ayrı key ile."
    )

    for platform in platforms:
        override = overrides.get(platform)
        if not override:
            continue

        rules = [f"\n{platform}:"]
        if override.captionStyle:
            rules.append(f"  Uzunluk: {style_map.get(override.captionStyle, 'medium')}")
        if override.maxHashtags:
            rules.append(f"  Max hashtag: {override.maxHashtags}")
        if override.useFirstComment:
            rules.append(
                f"  Hashtag'leri CAPTION'DAN AYIR, response'da "
                f"`{platform}.first_comment` key'inde dön"
            )
        if override.toneAdjustment:
            rules.append(f"  Ton ayarlama: {override.toneAdjustment}")
        if override.additionalGuidance:
            rules.append(f"  Ek talimat: {override.additionalGuidance}")

        parts.append("\n".join(rules))

    parts.append("\n=== PLATFORM BİTİŞ ===")
    return "\n".join(parts)
