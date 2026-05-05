"""Faceless Video pipeline: script → TTS → fal.ai background video.

Adımlar:
1. generate_script()  → Claude API ile Türkçe 15-30 saniyelik script
2. text_to_speech()   → ElevenLabs TTS API → R2'ye mp3
3. generate_video()   → fal.ai ile arka plan videosu (async, webhook)

ELEVENLABS_KEY yoksa TTS adımı atlanır; post kaydı yine de oluşturulur.
"""

import os
import re
from uuid import UUID

import asyncpg
import sentry_sdk

from app.core.config import settings
from app.services.media_adapters import (
    IMAGE_ADAPTERS,
    IMAGE_EDIT_ADAPTERS,
    get_active_faceless_background_adapter,
    get_active_image_adapter,
)

TURKISH_VOICES = [
    {"id": "qSeXEcewz7tA0Q0qk9fH", "name": "Buse (Kadın)",   "gender": "female"},
    {"id": "EST9Ui6982FZPSi7gCHi", "name": "Zeynep (Kadın)", "gender": "female"},
    {"id": "kPzsL2i3teMYv0FxEYQ6", "name": "Eylül (Kadın)",  "gender": "female"},
    {"id": "IuRRIAcbQK5AQk1XevPj", "name": "Emre (Erkek)",   "gender": "male"},
    {"id": "ctoYieZ4J7WwcdhujpMq", "name": "Kaan (Erkek)",   "gender": "male"},
    {"id": "UgBBYS2sOqTuMpoF3BR0", "name": "Ahmet (Erkek)",  "gender": "male"},
]

DEFAULT_VOICE = "qSeXEcewz7tA0Q0qk9fH"

ELEVENLABS_MODEL = "eleven_flash_v2_5"

# Tüm sesler için kalite-odaklı uniform ayarlar (kelime atlama/yutma sorununu önler).
# Voice'ların UI'daki kendi default'ları override edilir — production deterministic kalır.
VOICE_SETTINGS = {
    "stability": 1.0,
    "similarity_boost": 1.0,
    "style": 1.0,
    "use_speaker_boost": True,
    "speed": 1.08,
}

# Tüm platformlar için tek tip max konuşma süresi (saniye).
# Wan i2v 15s clip cap'i nedeniyle 30s'lik ses → max 1 ekstra loop = 2x clip.
# Daha uzun süreler aynı clip'in monoton tekrarına yol açıyor.
PLATFORM_MAX_DURATION: dict[str, int] = {
    "tiktok": 30,
    "instagram": 30,
    "youtube": 30,
    "threads": 30,
    "facebook": 30,
    "linkedin": 30,
    "twitter": 30,
    "pinterest": 30,
    "bluesky": 30,
}
DEFAULT_MAX_DURATION = 30

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
    user_brief: str = "",
    product_info: str = "",
    product_doc_context: str = "",
    image_edit_mode: bool = False,
) -> str:
    """Sahne prompt'u üret (Claude Opus).

    image_edit_mode=False (default): Text-to-image için tam sahne tarifi
    (öğeler, ışık, ürün dahil). Çıktı max 80 kelime.

    image_edit_mode=True: Nano Banana edit için scene-only prompt.
    Ürün tarif edilmez (model resmi zaten görüyor), sadece sahne yazılır.
    Çıktı max 60 kelime — image-edit kısa prompt sever.
    """
    context_parts = []
    if user_brief:
        context_parts.append(
            "USER'S SCENE REQUEST (highest priority — build the scene around this):\n"
            f"{user_brief}"
        )
    if brand_name:
        context_parts.append(f"Brand: {brand_name}")
    if brand_description:
        context_parts.append(f"What they do: {brand_description}")
    if sector:
        context_parts.append(f"Industry: {sector}")
    if product_info:
        if image_edit_mode:
            context_parts.append(
                "Product context (the product image will be passed to the model — "
                "do NOT describe the product itself):\n"
                f"{product_info}"
            )
        else:
            context_parts.append(f"Product/service in scene:\n{product_info}")
    if product_doc_context:
        context_parts.append(
            f"Product reference docs (use for accurate detail):\n{product_doc_context}"
        )
    if topic:
        context_parts.append(f"Video topic: {topic}")
    if color_str:
        context_parts.append(f"Brand colors: {color_str}")

    context = "\n\n".join(context_parts)

    if image_edit_mode:
        system_prompt = (
            "You are an expert cinematographer writing prompts for an image-edit AI model "
            "(Nano Banana / Gemini 2.5 Flash Image). The user's product photograph WILL BE "
            "passed to the model as a reference image. Your job: describe ONLY the scene "
            "around the product.\n\n"
            "STRICT RULES:\n"
            "- DO NOT describe the product's color, shape, material, or details — the model "
            "  sees the actual product photo.\n"
            "- Refer to the product as 'this exact product' or 'the item shown'.\n"
            "- Describe ONLY: who is in the scene (if anyone), where it takes place, "
            "  lighting, camera angle, mood, atmosphere.\n"
            "- Honor USER'S SCENE REQUEST exactly — every element they named must appear.\n"
            "- Style: cinematic, photorealistic, vertical 9:16 composition.\n"
            "- NO text, logos, or brand names in the scene (added post-process).\n"
            "- Output max 60 words. End the sentence cleanly.\n"
            "- Output ONLY the prompt, nothing else.\n\n"
            "Example: 'Place this exact product on a stylish woman walking through a "
            "bustling modern shopping mall, polished marble floors, warm golden hour "
            "lighting, soft bokeh of glowing storefronts behind, eye-level cinematic shot.'"
        )
        max_tokens = 300
    else:
        system_prompt = (
            "You are an expert cinematographer and visual director specializing in brand storytelling. "
            "Given brand info, output ONE English image generation prompt describing a scene.\n\n"
            "PRIORITY: If a USER'S SCENE REQUEST is provided, build the scene EXACTLY around it — "
            "honor every element the user mentioned (people, objects, environment, action). "
            "Use brand info as supporting context, not as override.\n\n"
            "VISUAL ANGLE — pick ONE that fits the video topic:\n"
            "1. PAIN POINT: Show the problem — before scene, frustration, obstacle\n"
            "2. OUTCOME: Show the transformation — after scene, success moment\n"
            "3. SOCIAL PROOF: Show community — group usage, collective context\n"
            "4. CURIOSITY: Show partial/hidden detail — extreme close-up, macro, mystery\n"
            "5. URGENCY: Show scarcity/time — limited display, countdown context\n"
            "6. IDENTITY: Show the target audience's environment — their world\n"
            "7. CONTRARIAN: Show the unexpected — product in surprising context\n\n"
            "Do NOT always pick the same angle. Vary based on topic.\n\n"
            "Rules:\n"
            "- Describe what the camera SEES: subjects, environments, surfaces, lighting, atmosphere\n"
            "- Include brand colors naturally (lighting, surfaces, props, accent tones)\n"
            "- NEVER include text, logos, or brand names (these are added in post-processing)\n"
            "- Style: cinematic, professional, 4K quality\n"
            "- Output max 80 words. Plan the sentence so it ends cleanly.\n"
            "- Output ONLY the prompt, nothing else."
        )
        max_tokens = 400

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=max_tokens,
            cache_control={"type": "ephemeral"},
            system=system_prompt,
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
            "product showcase, no text, no logos, "
            "cinematic composition, professional lighting, 4K"
        )
        return ", ".join(parts)


# ─── 0b. Motion prompt çeşitliliği ────────────────────────────────────────────

_MOTION_PROMPTS = [
    "Slow cinematic camera push-in, soft ambient lighting, gentle particle motion, seamless loop",
    "Smooth lateral dolly shot, warm natural light, subtle depth-of-field shift",
    "Gentle orbit around subject, golden hour lighting, cinematic bokeh",
    "Slow vertical tilt revealing the scene, soft diffused lighting, atmospheric haze",
    "Parallax effect with foreground blur, cool-tone ambient light, elegant composition",
    "Slow zoom-out revealing context, dramatic rim lighting, film grain texture",
    "Steady tracking shot with subtle camera sway, natural daylight, shallow focus",
]


def _pick_motion_prompt() -> str:
    """Her video için farklı kamera hareketi seç."""
    import random
    return random.choice(_MOTION_PROMPTS)


# ─── 1. Script üretimi ──────────────────────────────────────────────────────

async def generate_script(
    prompt: str,
    brand_kit: dict,
    brand_name: str = "",
    brand_description: str = "",
    website_url: str = "",
    sector_guidance: str = "",
    rag_context: str | None = None,
    max_duration: int = DEFAULT_MAX_DURATION,
) -> dict:
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

    colors = brand_kit.get("colors", [])
    if isinstance(colors, dict):
        color_str = ", ".join(f"{k}: {v}" for k, v in colors.items() if v)
    elif isinstance(colors, list):
        color_str = ", ".join(str(c) for c in colors if c)
    else:
        color_str = ""

    hashtags = brand_kit.get("hashtags", [])
    hashtag_str = ", ".join(hashtags[:5]) if hashtags else ""

    # Süre → kelime hedefi (~130 kelime/dakika Türkçe konuşma hızı)
    max_words = round(max_duration / 60 * 130)
    min_words = max(40, round(max_words * 0.5))

    system = (
        "Sen Türkçe sosyal medya video scriptleri yazan bir içerik uzmanısın.\n\n"
        f"SÜRE: {min_words}-{max_words} kelime (max {max_duration} saniye). "
        "Bu limiti ASLA aşma.\n\n"
        "YAZI KURALLARI:\n"
        "1. FAYDA > ÖZELLİK: Ürün/hizmetin özelliğini değil, müşteriye ne "
        "kazandırdığını anlat. AMA sadece verilen bilgideki özelliklerden fayda çıkar.\n"
        "2. SOMUTLUK > SOYUTLUK: 'Kalite', 'premium', 'modern', 'inovatif', 'en iyi' "
        "gibi belirsiz sözler KULLANMA. Spesifik detay veya durum anlat.\n"
        "3. AKTİF SES: Edilgen cümle kurma. 'Yapılır/oluşturulur' değil, doğrudan hitap.\n"
        "4. MÜŞTERİ DİLİ: Jargon kullanma, müşterinin günlük dilinde konuş.\n\n"
        "PSİKOLOJİ (uygun olanı seç, hepsini sokma):\n"
        "- SOMUTLUK: Her vaadin arkasında spesifik durum/rakam/zaman olmalı. "
        "Gerçek değilse KULLANMA.\n"
        "- LOSS AVERSION: 'Kaçırma' tarafını göster — ama SAHTE scarcity yaratma. "
        "Gerçek stok/süre bilgisi yoksa kullanma.\n"
        "- SOCIAL PROOF: Gerçek sayı/topluluk/referans varsa doğal şekilde yerleştir.\n"
        "Emin değilsen hiçbir prensip sokma — doğal akışa bırak.\n\n"
        "YASAK — İCAT ETME:\n"
        "- Sayısal iddia uydurma ('%300 artış', '30 saatten 2 saate').\n"
        "- Teknik özellik icat etme (malzeme, bileşen, sertifika).\n"
        "- Dolaylı fayda/performans iddiası icat etme.\n"
        "- Hayali müşteri hikayesi/yorumu uydurma.\n"
        "Bilgide olmayan hiçbir şeyi yazma. İçerik kısa kalsa bile dürüst kalsın.\n\n"
        "KULLANICI İSTEĞİ her zaman önceliklidir — konu/istek belirtildiyse "
        "marka varsayılanlarını geçersiz kılar.\n\n"
        "FORMAT: Sadece script metnini yaz. Başka açıklama, başlık, emoji ekleme. "
        "Script doğal konuşma dilinde, sesli okunacak şekilde yaz. "
        "Kullanıcı hazır script verdiyse TEMELden yeniden yaz — farklı açıdan anlat."
    )

    # User message — marka bağlamı + konu
    user_parts = [
        "=== MARKA BİLGİSİ ===",
        f"Marka: {brand_name}",
    ]
    if brand_description:
        user_parts.append(f"Ne yapar: {brand_description}")
    if sector:
        user_parts.append(f"Sektör: {sector}")
    user_parts.append(f"Üslup: {tone_tr}")
    if color_str:
        user_parts.append(f"Marka renkleri: {color_str}")
    if website_url:
        user_parts.append(f"Web sitesi: {website_url}")
    if hashtag_str:
        user_parts.append(f"Marka hashtag'leri: {hashtag_str}")
    user_parts.append("=== MARKA BİLGİSİ SONU ===")

    if sector_guidance:
        user_parts.append(f"\n=== SEKTÖR REHBERİ ===\n{sector_guidance}\n=== SEKTÖR REHBERİ SONU ===")

    if rag_context:
        user_parts.append(f"\n=== MARKA DÖKÜMAN BAĞLAMI ===\n{rag_context}\n=== BAĞLAM SONU ===")

    user_parts.append(f"\n=== KONU ===\n{prompt}\n=== KONU SONU ===")
    user_parts.append(
        "\nBu konuda bir sosyal medya videosu için Türkçe script yaz. "
        "Her seferinde farklı bir anlatım açısı ve yaratıcı bir giriş kullan."
    )
    user_msg = "\n".join(user_parts)

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=500,
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
    duration_estimate = max(15, min(max_duration, round(word_count / 130 * 60)))

    return {"script": script, "duration_estimate": duration_estimate}


# ─── 2. TTS (ElevenLabs API) ────────────────────────────────────────────────


async def text_to_speech(
    script_text: str,
    voice: str,
    post_id: UUID,
    brand_id: UUID,
    brand_name: str = "",
) -> dict:
    """ElevenLabs TTS → mp3 → R2. Returns {"audio_url": ..., "word_timestamps": [...]}.

    word_timestamps: [{"word": "Merhaba", "start": 0.0, "end": 0.45}, ...]
    """
    if not settings.ELEVENLABS_KEY:
        sentry_sdk.capture_message("TTS skipped: ELEVENLABS_KEY is empty", level="warning")
        return {"audio_url": None, "word_timestamps": []}

    from elevenlabs.client import ElevenLabs
    from elevenlabs.types import VoiceSettings
    from app.services.storage import r2

    try:
        client = ElevenLabs(api_key=settings.ELEVENLABS_KEY)

        # with_timestamps → tek AudioWithTimestampsResponse objesi
        # (audio_base_64 + alignment alanları, streaming DEĞİL)
        response = client.text_to_speech.convert_with_timestamps(
            text=script_text,
            voice_id=voice,
            model_id=ELEVENLABS_MODEL,
            output_format="mp3_44100_128",
            voice_settings=VoiceSettings(**VOICE_SETTINGS),
        )

        import base64
        # SDK alanı snake_case `audio_base_64`, eski sürümlerde `audio_base64` olabilir
        audio_b64 = (
            getattr(response, "audio_base_64", None)
            or getattr(response, "audio_base64", None)
        )
        if not audio_b64:
            return {"audio_url": None, "word_timestamps": []}
        audio_bytes = base64.b64decode(audio_b64)

        word_timestamps: list[dict] = []
        alignment = getattr(response, "alignment", None)
        if alignment is not None:
            chars = getattr(alignment, "characters", None) or []
            char_starts = getattr(alignment, "character_start_times_seconds", None) or []
            char_ends = getattr(alignment, "character_end_times_seconds", None) or []

            # Character-level → word-level aggregation
            current_word = ""
            word_start: float | None = None
            for i, char in enumerate(chars):
                if char == " ":
                    if current_word and word_start is not None:
                        word_timestamps.append({
                            "word": current_word,
                            "start": word_start,
                            "end": char_starts[i] if i < len(char_starts) else char_ends[i - 1],
                        })
                    current_word = ""
                    word_start = None
                else:
                    if word_start is None and i < len(char_starts):
                        word_start = char_starts[i]
                    current_word += char
            # Son kelime
            if current_word and word_start is not None:
                word_timestamps.append({
                    "word": current_word,
                    "start": word_start,
                    "end": char_ends[-1] if char_ends else word_start + 0.3,
                })

        r2_path = f"brands/{brand_id}/posts/audio/{post_id}.mp3"
        public_url = r2.upload(audio_bytes, r2_path, "audio/mpeg")

        # Timestamp'leri de R2'ye kaydet (webhook'ta subtitle burn-in için lazım)
        if word_timestamps:
            import json as _json
            ts_path = f"brands/{brand_id}/posts/audio/{post_id}_timestamps.json"
            r2.upload(_json.dumps(word_timestamps).encode(), ts_path, "application/json")

        return {"audio_url": public_url, "word_timestamps": word_timestamps}
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        return {"audio_url": None, "word_timestamps": []}


# ─── 3. fal.ai video üretimi ────────────────────────────────────────────────

async def _generate_still_image(prompt: str, aspect_ratio: str) -> str:
    """Legacy FLUX.2 still üretimi (image content type tarafından kullanılır).

    Video pipeline artık doğrudan _generate_still_via_text veya
    _generate_still_via_edit helper'larını kullanıyor (Nano Banana ailesi).
    """
    import fal_client

    image_adapter = get_active_image_adapter()
    args = image_adapter.build_args(prompt, aspect_ratio)

    result = await fal_client.subscribe_async(
        image_adapter.model_id,
        arguments=args,
    )
    return result["images"][0]["url"]


async def _generate_still_via_text(prompt: str, aspect_ratio: str) -> str:
    """Nano Banana 2 text-to-image ile still üret (senkron). Video Stage 1 için.

    Ürün referans görseli yokken (genel video) veya kullanıcı tarifsizken
    çağrılır. Çıktı 9:16 doğrudan model tarafından üretilir, FFmpeg pad gerek yok.
    """
    import fal_client

    adapter = IMAGE_ADAPTERS["nano-banana-2"]
    args = adapter.build_args(prompt, aspect_ratio)

    result = await fal_client.subscribe_async(
        adapter.model_id,
        arguments=args,
    )
    return result["images"][0]["url"]


async def _generate_still_via_edit(
    prompt: str, image_urls: list[str], aspect_ratio: str,
) -> str:
    """Nano Banana 2 edit ile still üret (senkron). Ürün + brief senaryosu için.

    image_urls genelde tek elemanlı: [product.image_url]. Prompt SAHNE-ONLY
    olmalı — ürünü tarif etme, model resmi zaten görüyor.
    """
    import fal_client

    adapter = IMAGE_EDIT_ADAPTERS["nano-banana-2-edit"]
    args = adapter.build_args(prompt, image_urls, aspect_ratio=aspect_ratio)

    result = await fal_client.subscribe_async(
        adapter.model_id,
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
    website_url: str = "",
    sector_guidance: str = "",
    rag_context: str | None = None,
    script: str = "",
    platform_captions: dict | None = None,
    template_id: str | None = None,
    template_fields: dict | None = None,
    intro_position: str = "none",
    product_id: UUID | None = None,
    max_duration: int = DEFAULT_MAX_DURATION,
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
        duration = max(15, min(max_duration, round(word_count / 130 * 60)))
    else:
        script_result = await generate_script(
            prompt, brand_kit, brand_name,
            brand_description=brand_description,
            website_url=website_url,
            sector_guidance=sector_guidance,
            rag_context=rag_context,
            max_duration=max_duration,
        )
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

    async def _update_stage(stage: str) -> None:
        await db.execute(
            """UPDATE social.posts
               SET template_fields = COALESCE(template_fields, '{}'::jsonb) || $2::jsonb
               WHERE id = $1""",
            post_id, {"generation_stage": stage},
        )

    await _update_stage("script_done")

    # 3. TTS → audio + word timestamps
    tts_result = await text_to_speech(script, voice, post_id, brand_id, brand_name=brand_name)
    audio_url = tts_result["audio_url"]
    await _update_stage("tts_done")

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

    motion_prompt = _pick_motion_prompt()
    await _update_stage("generating_video")

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


# ─── Stage 1 / Stage 2 split (onay gate'li pipeline) ────────────────────────

async def _resolve_still_prompt(
    prompt: str,
    script: str,
    brand_kit: dict,
    brand_name: str,
    brand_description: str,
    user_brief: str = "",
    product_info: str = "",
    product_doc_context: str = "",
    image_edit_mode: bool = False,
) -> str:
    """image_prompt'u still_prompt'a dönüştür.

    image_edit_mode=True (Nano Banana edit yolu): Her zaman _build_still_prompt
    çağrılır, sahne-only prompt üretilir (ürün tarif edilmez).

    image_edit_mode=False (text-to-image yolu):
    - user_brief doluysa caption gen'in image_prompt'unu yok say, yeni sahne üret
    - user_brief boşsa caption gen'in image_prompt'u (İngilizce) varsa onu kullan
    - O da yoksa brand bağlamından fallback üret
    """
    sector = brand_kit.get("sector", "")
    colors = brand_kit.get("colors", [])
    if isinstance(colors, dict):
        color_str = ", ".join(f"{v}" for v in colors.values() if v)
    elif isinstance(colors, list):
        color_str = ", ".join(str(c) for c in colors if c)
    else:
        color_str = ""

    if image_edit_mode:
        return await _build_still_prompt(
            topic="",
            brand_name=brand_name,
            brand_description=brand_description,
            sector=sector,
            color_str=color_str,
            user_brief=user_brief.strip(),
            product_info=product_info,
            product_doc_context=product_doc_context,
            image_edit_mode=True,
        )

    if user_brief.strip():
        return await _build_still_prompt(
            topic="",
            brand_name=brand_name,
            brand_description=brand_description,
            sector=sector,
            color_str=color_str,
            user_brief=user_brief.strip(),
            product_info=product_info,
            product_doc_context=product_doc_context,
        )

    still_prompt = (prompt or "").strip()
    if still_prompt and not _looks_turkish(still_prompt):
        return still_prompt
    return await _build_still_prompt(
        topic=prompt or script[:100],
        brand_name=brand_name,
        brand_description=brand_description,
        sector=sector,
        color_str=color_str,
        product_info=product_info,
        product_doc_context=product_doc_context,
    )


async def _submit_wan_video(
    still_url: str,
    prompt_for_model: str,
    aspect_ratio: str,
    duration: int,
    audio_url: str = "",
) -> str:
    """Wan I2V'ye (veya aktif arka plan adapter'ına) submit et — Stage 2'nin Wan kısmı."""
    import fal_client

    os.environ["FAL_KEY"] = settings.FAL_KEY

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


async def run_faceless_stage1(
    brand_id: UUID,
    prompt: str,
    script: str,
    voice: str,
    aspect_ratio: str,
    brand_kit: dict,
    brand_name: str,
    db: asyncpg.Connection,
    brand_description: str = "",
    platform_captions: dict | None = None,
    template_id: str | None = None,
    template_fields: dict | None = None,
    intro_position: str = "none",
    product_id: UUID | None = None,
    max_duration: int = DEFAULT_MAX_DURATION,
    user_brief: str = "",
    product_info: str = "",
    product_doc_context: str = "",
) -> dict:
    """Stage 1: post oluştur (status='awaiting_approval') + TTS + Nano Banana 2 still.

    Wan I2V tetiklenmez — kullanıcı 4.3'te onaylayınca Stage 2 çalışır.
    Returns: {post_id, script, audio_url, still_image_url, duration_estimate, ...}
    """
    if not script.strip():
        raise ValueError("Stage 1 için script boş olamaz (caption-step'ten gelmeli)")

    if template_fields is None:
        template_fields = {}
    template_fields["intro_position"] = intro_position
    template_fields["generation_stage"] = "stage1_started"

    # Duration tahmini (130 wpm Türkçe)
    word_count = len(script.split())
    duration = max(15, min(max_duration, round(word_count / 130 * 60)))
    template_fields["duration_estimate"] = duration

    # Ürün görseli kontrolü
    product_image_url = ""
    if product_id:
        product_row = await db.fetchrow(
            "SELECT image_url FROM social.brand_products WHERE id = $1",
            product_id,
        )
        if product_row and product_row["image_url"]:
            product_image_url = product_row["image_url"]

    has_brief = bool(user_brief.strip())
    has_product_image = bool(product_image_url)

    # Still üretim stratejisi (4 senaryo):
    #   product + brief        → Nano Banana edit (ürün resmi referans, scene-only prompt)
    #   product + brief yok    → ürün resmi as-is (mevcut davranış)
    #   brief + ürün yok       → Nano Banana text-to-image (full sahne prompt)
    #   hiçbiri yok            → Nano Banana text-to-image (markaya göre default)
    use_product_as_still = has_product_image and not has_brief
    use_image_edit = has_product_image and has_brief
    template_fields["still_strategy"] = (
        "product_as_still" if use_product_as_still
        else "image_edit" if use_image_edit
        else "text_to_image"
    )

    # Still prompt — Stage 2'de tekrar çözmemek için DB'ye kaydet
    still_prompt = await _resolve_still_prompt(
        prompt, script, brand_kit, brand_name, brand_description,
        user_brief=user_brief,
        product_info=product_info,
        product_doc_context=product_doc_context,
        image_edit_mode=use_image_edit,
    )
    template_fields["still_prompt"] = still_prompt

    # Post INSERT — TTS R2 path'i post_id'ye bağlı
    row = await db.fetchrow(
        """
        INSERT INTO social.posts
            (brand_id, content_type, prompt, user_text, aspect_ratio, status,
             template_id, template_fields, platform_captions, product_id)
        VALUES ($1, 'video', $2, $3, $4, 'awaiting_approval',
                $5, $6, $7, $8)
        RETURNING *
        """,
        brand_id, prompt, script, aspect_ratio,
        template_id, template_fields, platform_captions, product_id,
    )
    post = dict(row)
    post_id = post["id"]

    async def _patch(patch: dict) -> None:
        await db.execute(
            """UPDATE social.posts
               SET template_fields = COALESCE(template_fields, '{}'::jsonb) || $2::jsonb
               WHERE id = $1""",
            post_id, patch,
        )

    # TTS — fail olursa Stage 1 başarısız sayılır
    tts_result = await text_to_speech(script, voice, post_id, brand_id, brand_name=brand_name)
    audio_url = tts_result["audio_url"]
    if not audio_url:
        await db.execute(
            "UPDATE social.posts SET status = 'failed' WHERE id = $1",
            post_id,
        )
        raise RuntimeError("TTS üretimi başarısız oldu")
    await _patch({"audio_url": audio_url, "generation_stage": "tts_done"})

    # Still görseli üret — strategy'e göre
    try:
        if use_product_as_still:
            still_image_url = product_image_url
        elif use_image_edit:
            still_image_url = await _generate_still_via_edit(
                still_prompt, [product_image_url], aspect_ratio,
            )
        else:
            still_image_url = await _generate_still_via_text(still_prompt, aspect_ratio)
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        await db.execute(
            "UPDATE social.posts SET status = 'failed' WHERE id = $1",
            post_id,
        )
        raise RuntimeError(f"Still görsel üretimi başarısız: {exc}") from exc

    await _patch({
        "still_image_url": still_image_url,
        "product_image_url": product_image_url,
        "generation_stage": "awaiting_approval",
    })

    return {
        "post_id": post_id,
        "script": script,
        "audio_url": audio_url,
        "still_image_url": still_image_url,
        "duration_estimate": duration,
        "aspect_ratio": aspect_ratio,
    }


async def run_faceless_stage2(
    post_id: UUID,
    db: asyncpg.Connection,
) -> dict:
    """Stage 2: post'u 'awaiting_approval' durumundan al → Wan I2V submit.

    Stage 1'in ürettiği audio_url + still_image_url + still_prompt template_fields'tan okunur.
    Returns: {post_id, fal_job_id, status: 'generating'}
    """
    row = await db.fetchrow(
        "SELECT * FROM social.posts WHERE id = $1",
        post_id,
    )
    if not row:
        raise LookupError(f"Post {post_id} bulunamadı")
    if row["status"] != "awaiting_approval":
        raise ValueError(f"Post status='{row['status']}' — onay beklenmiyor")

    tf = row["template_fields"] or {}
    audio_url = tf.get("audio_url", "")
    still_image_url = tf.get("still_image_url", "")
    product_image_url = tf.get("product_image_url", "")
    still_prompt = tf.get("still_prompt", row["prompt"] or "")
    duration = int(tf.get("duration_estimate", 30))
    aspect_ratio = row["aspect_ratio"] or "9:16"

    if not still_image_url:
        raise ValueError("Stage 1 still görseli kaydedilmemiş — Stage 2 çalıştırılamaz")

    # Wan submission: ürün görseliyse motion-only, Nano Banana 2 ürettiyse motion-only,
    # legacy text-to-video adapter ise birleşik prompt
    motion_prompt = _pick_motion_prompt()
    if product_image_url or _faceless_bg_adapter.requires_still_image:
        prompt_for_model = motion_prompt
    else:
        prompt_for_model = f"{still_prompt}, {motion_prompt}"

    # Status flip + stage işaretle
    await db.execute(
        """UPDATE social.posts
           SET status = 'generating',
               template_fields = COALESCE(template_fields, '{}'::jsonb) || $2::jsonb
           WHERE id = $1""",
        post_id, {"generation_stage": "generating_video", "motion_prompt": motion_prompt},
    )

    try:
        fal_job_id = await _submit_wan_video(
            still_url=still_image_url,
            prompt_for_model=prompt_for_model,
            aspect_ratio=aspect_ratio,
            duration=duration,
            audio_url=audio_url,
        )
    except Exception as exc:
        sentry_sdk.capture_exception(exc)
        await db.execute(
            "UPDATE social.posts SET status = 'failed' WHERE id = $1",
            post_id,
        )
        raise

    await db.execute(
        "UPDATE social.posts SET fal_job_id = $2 WHERE id = $1",
        post_id, fal_job_id,
    )

    return {
        "post_id": post_id,
        "fal_job_id": fal_job_id,
        "status": "generating",
    }
