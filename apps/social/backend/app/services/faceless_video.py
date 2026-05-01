"""Faceless Video pipeline: script → TTS → fal.ai background video.

Adımlar:
1. generate_script()  → Claude API ile Türkçe 30-60 saniyelik script
2. text_to_speech()   → Azure Cognitive Services TTS REST API → R2'ye mp3
3. generate_video()   → fal.ai ile arka plan videosu (async, webhook)

Azure TTS key yoksa TTS adımı atlanır; post kaydı yine de oluşturulur.
"""

import os
import re
from uuid import UUID

import asyncpg
import httpx
import sentry_sdk

from app.core.config import settings
from app.services.media_adapters import get_active_faceless_background_adapter, get_active_image_adapter

# Sabit Türkçe ses listesi
TURKISH_VOICES = [
    {"id": "tr-TR-EmelNeural",   "name": "Emel (Kadın)",     "gender": "female"},
    {"id": "tr-TR-AhmetNeural",  "name": "Ahmet (Erkek)",    "gender": "male"},
]

DEFAULT_VOICE = "tr-TR-EmelNeural"

# Aktif faceless background adapter — modül import'unda bir kez çözülür.
_faceless_bg_adapter = get_active_faceless_background_adapter()

# Backward-compat module-level exports
FAL_VIDEO_MODEL: str = _faceless_bg_adapter.model_id
SUPPORTED_FACELESS_RATIOS: tuple[str, ...] = tuple(sorted(_faceless_bg_adapter.supported_ratios))
WEBHOOK_URL = "https://api.otomaix.com/webhooks/fal"


# ─── 0. Still image prompt üretimi ──────────────────────────────────────────

async def _build_still_prompt(
    topic: str,
    brand_name: str,
    brand_description: str,
    sector: str,
    color_str: str,
) -> str:
    """Marka bilgisinden FLUX.2 için sahne prompt'u üret.

    Claude Opus 4.7 ile görsel-odaklı İngilizce prompt oluşturur.
    API hatası durumunda fallback template kullanılır.
    """
    context_parts = []
    if brand_name:
        context_parts.append(f"Brand: {brand_name}")
    if brand_description:
        context_parts.append(f"What they do: {brand_description}")
    if sector:
        context_parts.append(f"Industry: {sector}")
    if topic:
        context_parts.append(f"Video topic: {topic}")
    if color_str:
        context_parts.append(f"Brand colors: {color_str}")

    context = "\n".join(context_parts)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=150,
            cache_control={"type": "ephemeral"},
            system=(
                "You are an expert cinematographer and visual director specializing in brand storytelling. "
                "Given brand info, output ONE English image generation prompt "
                "describing a scene. Rules:\n"
                "- Describe what the camera SEES: products, environments, surfaces, lighting, atmosphere\n"
                "- Include brand colors naturally (lighting, surfaces, props)\n"
                "- NEVER include people, faces, hands, text, logos, or brand names\n"
                "- Style: cinematic, professional, 4K quality\n"
                "- Output ONLY the prompt, nothing else."
            ),
            messages=[{"role": "user", "content": context}],
        )
        return msg.content[0].text.strip()
    except Exception:
        parts = []
        if brand_description:
            parts.append(brand_description)
        elif topic:
            parts.append(topic)
        if sector:
            parts.append(f"{sector} industry")
        if color_str:
            parts.append(f"color palette: {color_str}")
        parts.append(
            "product showcase, no people, no text, "
            "cinematic composition, professional lighting, 4K"
        )
        return ", ".join(parts)


# ─── 1. Script üretimi ──────────────────────────────────────────────────────

async def generate_script(prompt: str, brand_kit: dict, brand_name: str = "", rag_context: str | None = None) -> dict:
    """Claude API ile Türkçe sosyal medya video scripti üret.

    Returns: {"script": "...", "duration_estimate": 45}
    """
    tonality = brand_kit.get("tonality", "professional")
    sector = brand_kit.get("sector", "")

    tone_map = {
        "professional": "profesyonel ve güvenilir",
        "friendly": "samimi ve sıcak",
        "fun": "eğlenceli ve enerjik",
        "informative": "bilgilendirici ve net",
    }
    tone_tr = tone_map.get(tonality, "profesyonel")

    system = (
        "Sen Türkçe sosyal medya video scriptleri yazan bir içerik uzmanısın. "
        "Scriptler doğal konuşma dilinde, akıcı ve ilgi çekici olmalı. "
        "Yaklaşık 30-60 saniye sürecek uzunlukta yaz (75-150 kelime). "
        "Kullanıcı hazır bir script verdiyse onu TEMELden yeniden yaz — aynı mesajı "
        "farklı kelimelerle, farklı bir açıdan anlat. Birebir kopyalama."
    )
    user_parts = [
        f"Marka: {brand_name}",
        f"Sektör: {sector}",
        f"Üslup: {tone_tr}",
        "",
        f"Konu / Kullanıcı girdisi: {prompt}",
    ]
    if rag_context:
        user_parts.append(f"\n=== MARKA DÖKÜMAN BAĞLAMI ===\n{rag_context}\n=== BAĞLAM SONU ===")
        user_parts.append("Yukarıdaki doküman bağlamını içeriğe doğal şekilde yansıt.")
    user_parts.append(
        "\nBu konuda bir sosyal medya videosu için Türkçe script yaz. "
        "Her seferinde farklı bir anlatım açısı ve yaratıcı bir giriş kullan. "
        "Sadece script metnini yaz, başka açıklama ekleme."
    )
    user_msg = "\n".join(user_parts)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=400,
            temperature=1.0,
            cache_control={"type": "ephemeral"},
            system=system,
            messages=[{"role": "user", "content": user_msg}],
        )
        script = msg.content[0].text.strip()
    except Exception:
        script = f"{brand_name} ile tanışın. {prompt}"

    # Kelime sayısına göre süre tahmini (~130 kelime/dakika Türkçe)
    word_count = len(script.split())
    duration_estimate = max(15, min(60, round(word_count / 130 * 60)))

    return {"script": script, "duration_estimate": duration_estimate}


# ─── 2. TTS (Azure REST API) ────────────────────────────────────────────────

_VOICE_EN = "en-US-JennyNeural"

try:
    import enchant
    _en_dict = enchant.Dict("en_US")
    _tr_dict = enchant.Dict("tr_TR")
    _HAS_ENCHANT = True
except Exception:
    _HAS_ENCHANT = False


def _is_english_word(word: str) -> bool:
    """Kelimenin İngilizce olup olmadığını kontrol et."""
    clean = re.sub(r"[.,!?;:\"'()\-]", "", word).lower()
    if not clean or len(clean) <= 1:
        return False
    if re.search(r"[çğıöşüÇĞİÖŞÜ]", word):
        return False
    if re.search(r"\d", clean):
        return False
    # URL pattern
    if re.search(r"\.(?:com|org|net|io|co)$", clean):
        return True
    # PascalCase / camelCase / ALL CAPS
    if re.match(r"[A-Z][a-z]+[A-Z]", word) or re.match(r"[A-Z]{2,}$", clean):
        return True
    if _HAS_ENCHANT and re.match(r"^[a-zA-Z]+$", clean):
        return _en_dict.check(clean) and not _tr_dict.check(clean)
    return False


def _detect_language_segments(text: str) -> list[tuple[str, str]]:
    """Metni TR/EN bölümlerine ayır."""
    tokens = re.findall(r"\S+|\s+", text)
    segments: list[tuple[str, str]] = []
    for token in tokens:
        if token.isspace():
            if segments:
                segments[-1] = (segments[-1][0], segments[-1][1] + token)
            continue
        lang = "en" if _is_english_word(token) else "tr"
        if segments and segments[-1][0] == lang:
            segments[-1] = (lang, segments[-1][1] + token)
        else:
            segments.append((lang, token))
    return segments


def _build_ssml(text: str, voice: str, brand_name: str = "") -> str:
    """Azure TTS için SSML yapısı oluştur.

    İngilizce kelimeler enchant sözlük ile tespit edilip
    İngilizce voice ile okunur.
    """
    from xml.sax.saxutils import escape

    segments = _detect_language_segments(text)

    inner = ""
    for lang, txt in segments:
        v = _VOICE_EN if lang == "en" else voice
        inner += f'<voice name="{v}">{escape(txt)}</voice>\n'

    return (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="tr-TR">\n'
        f"{inner}</speak>"
    )


async def text_to_speech(
    script_text: str,
    voice: str,
    post_id: UUID,
    brand_id: UUID,
    brand_name: str = "",
) -> str | None:
    """Azure TTS REST API → mp3 → R2. Returns public_url veya None."""
    if not settings.AZURE_TTS_KEY or not settings.AZURE_TTS_REGION:
        sentry_sdk.capture_message(
            f"TTS skipped: AZURE_TTS_KEY={'set' if settings.AZURE_TTS_KEY else 'EMPTY'}, "
            f"AZURE_TTS_REGION={settings.AZURE_TTS_REGION or 'EMPTY'}",
            level="warning",
        )
        return None

    from app.services.storage import r2

    ssml = _build_ssml(script_text, voice, brand_name=brand_name)
    url = f"https://{settings.AZURE_TTS_REGION}.tts.speech.microsoft.com/cognitiveservices/v1"
    headers = {
        "Ocp-Apim-Subscription-Key": settings.AZURE_TTS_KEY,
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "audio-48khz-96kbitrate-mono-mp3",
        "User-Agent": "otomaix-social",
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, content=ssml.encode("utf-8"), headers=headers)
            if resp.status_code != 200:
                sentry_sdk.set_context("tts_error", {
                    "post_id": str(post_id),
                    "status_code": resp.status_code,
                    "response_body": resp.text[:500],
                })
                sentry_sdk.capture_message(f"Azure TTS failed (HTTP {resp.status_code})", level="error")
                return None
            audio_bytes = resp.content

        r2_path = f"brands/{brand_id}/posts/audio/{post_id}.mp3"
        public_url = r2.upload(audio_bytes, r2_path, "audio/mpeg")
        return public_url
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        return None


# ─── 3. fal.ai video üretimi ────────────────────────────────────────────────

async def _generate_still_image(prompt: str, aspect_ratio: str) -> str:
    """FLUX.2 ile still görsel üret (senkron bekleme). Returns fal temp URL."""
    import fal_client

    image_adapter = get_active_image_adapter()
    args = image_adapter.build_args(prompt, aspect_ratio)

    result = await fal_client.subscribe_async(
        image_adapter.model_id,
        arguments=args,
    )
    return result["images"][0]["url"]


async def generate_background_video(
    still_prompt: str,
    motion_prompt: str,
    aspect_ratio: str,
    duration: int = 5,
    audio_url: str = "",
    product_image_url: str = "",
) -> str:
    """fal.ai arka plan videosu üret — aktif FacelessBackgroundAdapter üzerinden.

    2 aşamalı adapters (Wan i2v): FLUX.2 still (still_prompt) üretir,
    sonra Wan'a motion_prompt + image + audio gönderir.
    product_image_url varsa FLUX.2 adımı atlanır, ürün görseli doğrudan Wan'a gider.
    Legacy adapters (Hunyuan): her iki prompt'u birleştirip text-to-video yapar.

    Returns fal job ID.
    """
    import fal_client

    os.environ["FAL_KEY"] = settings.FAL_KEY

    still_url = ""
    if product_image_url:
        still_url = product_image_url
        prompt_for_model = motion_prompt
    elif _faceless_bg_adapter.requires_still_image:
        still_url = await _generate_still_image(still_prompt, aspect_ratio)
        prompt_for_model = motion_prompt
    else:
        prompt_for_model = f"{still_prompt}, {motion_prompt}"

    args = _faceless_bg_adapter.build_args(
        prompt_for_model, aspect_ratio, duration,
        image_url=still_url, audio_url=audio_url,
    )

    handler = await fal_client.submit_async(
        _faceless_bg_adapter.model_id,
        arguments=args,
        webhook_url=WEBHOOK_URL,
    )
    return handler.request_id


# ─── Ana pipeline ────────────────────────────────────────────────────────────

async def run_faceless_video_pipeline(
    brand_id: UUID,
    prompt: str,
    voice: str,
    aspect_ratio: str,
    brand_kit: dict,
    brand_name: str,
    db: asyncpg.Connection,
    brand_description: str = "",
    rag_context: str | None = None,
    script: str = "",
    platform_captions: dict | None = None,
    template_id: str | None = None,
    template_fields: dict | None = None,
    intro_position: str = "none",
    product_id: UUID | None = None,
) -> dict:
    """Tam pipeline: post oluştur → script → TTS → fal.ai video.

    Returns post dict with post_id, script, audio_url.
    """
    # intro_position'ı template_fields'e kaydet (post tablosunda ayrı kolon yok)
    if template_fields is None:
        template_fields = {}
    template_fields["intro_position"] = intro_position

    # 1. Script — frontend'den geldiyse aynen kullan, yoksa üret
    if script.strip():
        word_count = len(script.split())
        duration = max(15, min(60, round(word_count / 130 * 60)))
    else:
        script_result = await generate_script(prompt, brand_kit, brand_name, rag_context=rag_context)
        script = script_result["script"]
        duration = script_result["duration_estimate"]

    # 2. Post kaydı oluştur
    row = await db.fetchrow(
        """
        INSERT INTO social.posts
            (brand_id, content_type, prompt, user_text, aspect_ratio, status,
             template_id, template_fields, platform_captions, product_id)
        VALUES ($1, 'video', $2, $3, $4, 'generating',
                $5, $6, $7, $8)
        RETURNING *
        """,
        brand_id,
        prompt,
        script,
        aspect_ratio,
        template_id,
        template_fields,
        platform_captions,
        product_id,
    )
    post = dict(row)
    post_id = post["id"]

    # 3. TTS → audio
    audio_url = await text_to_speech(script, voice, post_id, brand_id, brand_name=brand_name)

    # 4. fal.ai arka plan videosu
    # Ürün görseli varsa FLUX.2 still adımını atla, doğrudan Wan'a gönder
    product_image_url = ""
    if product_id:
        product_row = await db.fetchrow(
            "SELECT image_url FROM social.brand_products WHERE id = $1",
            product_id,
        )
        if product_row and product_row["image_url"]:
            product_image_url = product_row["image_url"]

    # prompt = image_prompt (caption generator tarafından üretilen İngilizce sahne açıklaması)
    # Eğer prompt boşsa veya Türkçe ise fallback olarak _build_still_prompt kullan
    still_prompt = prompt.strip()
    if not product_image_url and (not still_prompt or _looks_turkish(still_prompt)):
        sector = brand_kit.get("sector", "")
        colors = brand_kit.get("colors", [])
        if isinstance(colors, dict):
            color_str = ", ".join(f"{v}" for v in colors.values() if v)
        elif isinstance(colors, list):
            color_str = ", ".join(str(c) for c in colors if c)
        else:
            color_str = ""
        still_prompt = await _build_still_prompt(
            topic=prompt or script[:100],
            brand_name=brand_name,
            brand_description=brand_description,
            sector=sector,
            color_str=color_str,
        )

    motion_prompt = (
        "Slow cinematic camera push-in, soft ambient lighting, "
        "gentle particle motion, seamless loop, return to starting position, "
        "no people, no human figures, no faces"
    )

    try:
        fal_job_id = await generate_background_video(
            still_prompt, motion_prompt, aspect_ratio, duration,
            audio_url=audio_url or "",
            product_image_url=product_image_url,
        )
        await db.execute(
            "UPDATE social.posts SET fal_job_id = $2 WHERE id = $1",
            post_id, fal_job_id,
        )
        post["fal_job_id"] = fal_job_id
    except Exception as exc:
        sentry_sdk.capture_exception(exc)

    post["script"] = script
    post["audio_url"] = audio_url
    post["duration_estimate"] = duration

    return post


def _looks_turkish(text: str) -> bool:
    """Basit Türkçe karakter kontrolü."""
    return bool(re.search(r"[çğıöşüÇĞİÖŞÜ]", text))
