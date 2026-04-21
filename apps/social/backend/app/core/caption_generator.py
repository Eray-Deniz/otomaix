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
) -> dict[str, Any]:
    """Generate caption + image prompt + hashtags via Claude."""

    system_prompt = build_system_prompt()
    brand_context = build_brand_context(brand, brand_kit, template)
    dynamic_content = build_dynamic_content(
        template, template_fields, user_prompt, rag_context, platforms, product
    )

    output_format = _build_output_format_instruction(template, platforms)

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
            model="claude-opus-4-7",
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
        data.setdefault("image_prompt", "")
        data.setdefault("hashtags", [])

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
    return {
        "default_caption": user_prompt or "",
        "platform_captions": pcaptions,
        "image_prompt": user_prompt or "social media post image",
        "hashtags": [],
    }


def _build_output_format_instruction(
    template: Template | None,
    platforms: list[str],
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

    return f"""ÇIKTI FORMATI (SADECE JSON, BAŞKA HİÇBİR ŞEY YAZMA):

{{
  "default_caption": "Genel caption — fallback olarak kullanılır",
  "platform_captions": {{
    {platform_schema}
  }},
  "image_prompt": "English visual description for image AI (fal.ai FLUX.2 Pro)",
  "hashtags": ["hashtag1", "hashtag2"]
}}

ÖNEMLİ: image_prompt İngilizce yazılmalı (AI model İngilizce prompt anlıyor).
Caption'lar ve hashtag'ler Türkçe olmalı.

⚠️ image_prompt İÇİN KATIİ KURALLAR (görsel kalitesi için kritik):
1. MARKA ADI YASAK: image_prompt'ta marka adını (örn. "MyGoodShoes") ASLA kullanma — text-to-image modeli bunu görsele metin olarak basıyor ("from MyGoodShoes" ❌).
2. ÜRÜN ADI YASAK: spesifik ürün modeli/adı (örn. "SporXL", "iPhone 15") image_prompt'ta geçmesin — görseldeki şort/kutu üzerine yazı olarak basılıyor. Genel kategori kullan: "running sneakers", "smartphone", "leather handbag".
3. TÜRKÇE METİN YASAK: image_prompt'ta hiçbir Türkçe kelime olmasın. "Rahat · Kaliteli · Şık" gibi özellik metinleri tarif etme — FLUX bunları aynen görsele yazıya döker. Özellikleri görsel olarak ima et (comfort → relaxed pose, quality → premium materials texture, style → modern composition).
4. LOGO/ROZET/METİN KATMANI YASAK: "brand logo badge in corner", "feature badge", "text overlay", "watermark", "caption text" ASLA tarif etme. Gerçek marka logosu webhook pipeline'ında post-process olarak ekleniyor — FLUX'un logo çizmesine gerek YOK, hatta hayali logo uyduruyor.
5. ÜRÜN ODAĞI: E-ticaret ürün kartlarında ana özne ürünün kendisi olmalı (shoe product shot, close-up, hero angle). İnsan modeli/lifestyle istenmiyorsa modeli tarif etme — sadece ürün. Şablon guidance'ı lifestyle istiyorsa bile ürün görselin en az %60'ını kaplamalı.
6. FORMAT ÖNERİSİ: "Professional product photography of [generic product category], [composition], clean studio background in [brand color HEX], [lighting style], [material/texture detail]. No text, no logos, no overlays."
"""
