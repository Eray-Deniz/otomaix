"""Phase 7 Sprint 4 — AI caption + image prompt generation.

Called from POST /posts/generate-caption.
Uses Claude Opus 4.7 with 3-tier prompt caching (via prompt_builder).

Returns structured response:
{
    "default_caption": "genel caption",
    "platform_captions": {
        "instagram": {"caption": "...", "first_comment": "..."},
        "linkedin": {"caption": "..."}
    },
    "image_prompt": "English image description for fal.ai",
    "hashtags": ["indirim", "kampanya"]
}
"""
import json
import logging
import re
from typing import Any

import anthropic
import json_repair

from app.core.config import settings
from app.core.prompt_builder import (
    _resolve_platform_rules,
    build_brand_context,
    build_dynamic_content,
    build_system_prompt,
)
from app.models.templates import Template

logger = logging.getLogger(__name__)

_HASHTAG_RE = re.compile(r"#[\wÇĞİÖŞÜçğıöşü]+", re.UNICODE)


def _split_caption_hashtags(caption: str) -> tuple[str, str]:
    """Caption'dan hashtag'leri ayır. Returns (clean_caption, hashtag_block)."""
    if not caption:
        return caption, ""
    tags = _HASHTAG_RE.findall(caption)
    if not tags:
        return caption, ""
    clean = _HASHTAG_RE.sub("", caption).rstrip()
    clean = re.sub(r"\s+\n", "\n", clean).rstrip()
    return clean, " ".join(tags)


def _ensure_first_comment(
    data: dict[str, Any],
    template: Template | None,
    platforms: list[str],
) -> None:
    """useFirstComment platformlar için first_comment alanını garanti et.

    Claude response'ta first_comment yoksa/boşsa, caption'daki hashtag'leri
    oraya taşır. Frontend textarea'sı görünmez kalmasın diye en azından "" set edilir.
    """
    overrides = (template.platformOverrides if template else None) or {}
    pcaptions = data.get("platform_captions") or {}
    for platform in platforms:
        rules = _resolve_platform_rules(platform, overrides.get(platform))
        if not rules.get("useFirstComment"):
            continue
        entry = pcaptions.get(platform)
        if not isinstance(entry, dict):
            entry = {"caption": "", "first_comment": ""}
            pcaptions[platform] = entry
        existing_fc = (entry.get("first_comment") or "").strip()
        caption_text = entry.get("caption") or ""
        if not existing_fc:
            clean, tags = _split_caption_hashtags(caption_text)
            if tags:
                entry["caption"] = clean
                entry["first_comment"] = tags
            else:
                entry["first_comment"] = ""
        else:
            entry["first_comment"] = existing_fc
    data["platform_captions"] = pcaptions


async def generate_captions(
    brand: dict,
    brand_kit: dict,
    template: Template | None,
    template_fields: dict | None,
    user_prompt: str | None,
    rag_context: str | None,
    platforms: list[str],
    product: dict | None = None,
    content_type: str | None = None,
    special_day_name: str | None = None,
    special_day_category: str | None = None,
) -> dict[str, Any]:
    """Generate caption + image prompt + hashtags via Claude. Video ise script de üretir.

    `special_day_name` + `special_day_category` doluysa caption tatil tonuna yönlendirilir
    (Tier 3 dynamic content'e ÖZEL GÜN BAĞLAMI bloğu eklenir).
    """

    system_prompt = build_system_prompt()
    brand_context = build_brand_context(brand, brand_kit, template)
    special_day = (
        {"name": special_day_name, "category": special_day_category}
        if special_day_name
        else None
    )
    dynamic_content = build_dynamic_content(
        template, template_fields, user_prompt, rag_context, platforms, product,
        special_day=special_day,
    )

    output_format = _build_output_format_instruction(
        template, platforms, template_fields, content_type=content_type,
        product=product,
    )

    user_content = [
        {
            "type": "text",
            "text": brand_context,
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": dynamic_content + "\n\n" + output_format,
        },
    ]

    if not settings.ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not configured — caption generation fallback")
        return _fallback_response(user_prompt, platforms)

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    try:
        message = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=2048,
            temperature=1.0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )

        if hasattr(message, "usage"):
            cache_read = getattr(message.usage, "cache_read_input_tokens", 0)
            cache_create = getattr(message.usage, "cache_creation_input_tokens", 0)
            logger.info(
                f"Caption gen cache: read={cache_read}, create={cache_create}, "
                f"template={template.id if template else None}"
            )

        raw = message.content[0].text.strip()

        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as decode_err:
            logger.warning(
                f"Caption JSON decode failed ({decode_err}); trying json-repair. "
                f"Raw length={len(raw)}, preview={raw[:200]!r}"
            )
            repaired = json_repair.loads(raw)
            if not isinstance(repaired, dict):
                raise ValueError(f"json-repair returned non-dict: {type(repaired)}")
            data = repaired

        data.setdefault("default_caption", "")
        data.setdefault("platform_captions", {})
        is_carousel = template is not None and "carousel" in (template.contentTypes or [])
        is_video = content_type == "video"
        if is_carousel:
            data.setdefault("image_prompts", [])
        else:
            data.setdefault("image_prompt", "")
        data.setdefault("hashtags", [])
        if is_video:
            data.setdefault("script", "")
            script_text = data.get("script") or ""
            word_count = len(script_text.split())
            data["duration_estimate"] = max(10, int(word_count * 60 / 130))

        _ensure_first_comment(data, template, platforms)

        if template and template.defaults.disclaimer:
            disclaimer = template.defaults.disclaimer
            if data["default_caption"] and not data["default_caption"].endswith(disclaimer):
                data["default_caption"] += f"\n\n{disclaimer}"
            for pcaption in data["platform_captions"].values():
                if isinstance(pcaption, dict) and "caption" in pcaption:
                    if pcaption["caption"] and not pcaption["caption"].endswith(disclaimer):
                        pcaption["caption"] += f"\n\n{disclaimer}"

        return data

    except Exception as e:
        logger.error(f"Caption generation failed: {e}", exc_info=True)
        fallback = _fallback_response(user_prompt, platforms, template)
        fallback["error"] = str(e)
        return fallback


def _fallback_response(
    user_prompt: str | None,
    platforms: list[str],
    template: Template | None = None,
) -> dict[str, Any]:
    overrides = (template.platformOverrides if template else None) or {}
    pcaptions: dict[str, dict[str, str]] = {}
    for p in platforms:
        entry: dict[str, str] = {"caption": user_prompt or ""}
        rules = _resolve_platform_rules(p, overrides.get(p))
        if rules.get("useFirstComment"):
            entry["first_comment"] = ""
        pcaptions[p] = entry
    is_carousel = template is not None and "carousel" in (template.contentTypes or [])
    result: dict[str, Any] = {
        "default_caption": user_prompt or "",
        "platform_captions": pcaptions,
        "hashtags": [],
    }
    if is_carousel:
        result["image_prompts"] = []
    else:
        result["image_prompt"] = user_prompt or "social media post image"
    return result


def _build_output_format_instruction(
    template: Template | None,
    platforms: list[str],
    template_fields: dict | None = None,
    content_type: str | None = None,
    product: dict | None = None,
) -> str:
    """Instruct Claude on exact JSON output format."""

    overrides = template.platformOverrides if template else None
    overrides = overrides or {}

    if platforms:
        schema_parts: list[str] = []
        for p in platforms:
            rules = _resolve_platform_rules(p, overrides.get(p))
            if rules.get("useFirstComment"):
                schema_parts.append(
                    f'"{p}": {{"caption": "...", "first_comment": "..."}}'
                )
            else:
                schema_parts.append(f'"{p}": {{"caption": "..."}}')
        platform_schema = ", ".join(schema_parts)
    else:
        platform_schema = '"default": {"caption": "..."}'

    is_carousel = template is not None and "carousel" in (template.contentTypes or [])
    is_video = content_type == "video"
    slide_count = int((template_fields or {}).get("slide_count", 5)) if is_carousel else 0

    if is_video:
        image_schema = '"image_prompt": "English scene description for still image (fal.ai Nano Banana 2) — this becomes the video background"'
        script_schema = ',\n  "script": "Türkçe voiceover script metni (15-30 saniye)"'

        product_rules = ""
        if product and product.get("name"):
            product_rules = (
                f"\n- Ürün/hizmet adı \"{product['name']}\" script içinde en az "
                "bir kez geçmeli.\n"
                "- Ürün açıklaması ve etiketlerinden script'e SOMUT bir özellik "
                "taşı: renk, malzeme, kullanım durumu, ölçü/rakam, sektörel terim. "
                "Soyut sıfatlar (\"şık\", \"premium\", \"kaliteli\", \"gösterişli\") "
                "tek başına özellik sayılmaz — yanına somut bir dayanak gerekir."
            )

        image_note = (
            "ÖNEMLİ: image_prompt İngilizce yazılmalı (still image → video arka planı olacak).\n"
            "script Türkçe yazılmalı — TTS ile seslendirilecek voiceover metni.\n"
            "Caption'lar ve hashtag'ler Türkçe olmalı.\n\n"
            "SCRIPT KURALLARI (yalnızca `script` alanına uygulanır, "
            "`platform_captions` alanına UYGULANMAZ):\n"
            "- 15-30 saniye arası (yaklaşık 32-65 kelime)\n"
            "- Hook cümlesiyle başla (ilk 3 saniye kritik)\n"
            "- Kısa, net cümleler — TTS'in doğal okuyacağı yapıda\n"
            "- Bilgide olmayan şey uydurma\n"
            "- URL/domain yazıyla: \"mygoodshoes.com\" → \"mygoodshoes nokta com\" "
            "(script içinde nokta karakteri kullanılmasın — TTS yanlış okuyor)\n"
            "- CTA varsa script'in sonunda da söyle"
            f"{product_rules}"
        )
        field_ref = "image_prompt'ta"
        rules_title = "⚠️ image_prompt İÇİN KATIİ KURALLAR"
    elif is_carousel:
        image_schema = (
            '"image_prompts": [\n'
            '    "Slide 1 (HOOK): English visual description for fal.ai FLUX.2 Pro",\n'
            '    "Slide 2 (VALUE): English visual description...",\n'
            f'    "... tam olarak {slide_count} adet İngilizce prompt"\n'
            '  ]'
        )
        script_schema = ""
        image_note = (
            f"ÖNEMLİ: image_prompts dizisinde TAM OLARAK {slide_count} adet İngilizce prompt olmalı.\n"
            "Her slide farklı bir görsel açı kategorisi kullanmalı — aynı açıyı iki slide'da tekrarlama.\n"
            "Caption'lar ve hashtag'ler Türkçe olmalı."
        )
        field_ref = "her image_prompts elemanında"
        rules_title = "⚠️ HER image_prompts ELEMANI İÇİN KATIİ KURALLAR"
    else:
        image_schema = '"image_prompt": "English visual description for image AI (fal.ai FLUX.2 Pro)"'
        script_schema = ""
        image_note = (
            "ÖNEMLİ: image_prompt İngilizce yazılmalı (AI model İngilizce prompt anlıyor).\n"
            "Caption'lar ve hashtag'ler Türkçe olmalı."
        )
        field_ref = "image_prompt'ta"
        rules_title = "⚠️ image_prompt İÇİN KATIİ KURALLAR"

    video_scene_rule = ""
    if is_video:
        video_scene_rule = (
            "\n7. VİDEO SAHNE: Kamera hareketi düşünerek sahne kur (dolly, pan, zoom uyumlu). "
            "Kullanıcının tarifine ve ürün/marka bağlamına göre sahnede hangi öğeler "
            "(insan, ürün, ortam, atmosfer) gerekiyorsa onları içer."
        )

    return f"""ÇIKTI FORMATI (SADECE JSON, BAŞKA HİÇBİR ŞEY YAZMA):

{{
  "platform_captions": {{
    {platform_schema}
  }},
  {image_schema},
  "hashtags": ["hashtag1", "hashtag2"]{script_schema}
}}

ÖNEMLİ: Her seçili platform için platform_captions altında ayrı caption üret — varsayılan/genel caption üretme, her platforma özel yaz.

{image_note}

{rules_title} (görsel kalitesi için kritik):
1. MARKA ADI YASAK: {field_ref} marka adını (örn. "MyGoodShoes") ASLA kullanma — text-to-image modeli bunu görsele metin olarak basıyor ("from MyGoodShoes" ❌).
2. ÜRÜN ADI YASAK: spesifik ürün modeli/adı (örn. "SporXL", "iPhone 15") {field_ref} geçmesin — görseldeki şort/kutu üzerine yazı olarak basılıyor. Genel kategori kullan: "running sneakers", "smartphone", "leather handbag".
3. TÜRKÇE METİN YASAK: {field_ref} hiçbir Türkçe kelime olmasın. "Rahat · Kaliteli · Şık" gibi özellik metinleri tarif etme — FLUX bunları aynen görsele yazıya döker. Özellikleri görsel olarak ima et (comfort → relaxed pose, quality → premium materials texture, style → modern composition).
4. LOGO/ROZET/METİN KATMANI YASAK: "brand logo badge in corner", "feature badge", "text overlay", "watermark", "caption text" ASLA tarif etme. Gerçek marka logosu webhook pipeline'ında post-process olarak ekleniyor — FLUX'un logo çizmesine gerek YOK, hatta hayali logo uyduruyor.
5. KOMPOZİSYON: Genel şablonlarda (genel-gorsel-sablon vb.) tam vücut, lifestyle, moda çekimi, sahne kompozisyonu gibi geniş kadrajlar tercih et — ürünü SADECE close-up'a sıkıştırma. Giyilebilir ürünler (ayakkabı, kıyafet, aksesuar) için tam vücut model + ürün dengeli görünmeli. E-ticaret ürün kartı şablonlarında ise ürün odaklı close-up/hero angle uygun.
6. FORMAT ÖNERİSİ: "Professional [photography style] of [generic product category], [full scene composition], [background description] in [brand color HEX], [lighting style], [material/texture detail]. No text, no logos, no overlays."{video_scene_rule}
"""
