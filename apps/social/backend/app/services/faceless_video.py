"""Faceless Video pipeline: script → TTS → fal.ai background video.

Adımlar:
1. generate_script()  → Claude API ile Türkçe 30-60 saniyelik script
2. text_to_speech()   → Azure Cognitive Services TTS REST API → R2'ye mp3
3. generate_video()   → fal.ai ile arka plan videosu (async, webhook)

Azure TTS key yoksa TTS adımı atlanır; post kaydı yine de oluşturulur.
"""

import os
from uuid import UUID

import asyncpg
import httpx

from app.core.config import settings
from app.services.media_adapters import get_active_faceless_background_adapter

# Sabit Türkçe ses listesi
TURKISH_VOICES = [
    {"id": "tr-TR-EmelNeural",   "name": "Emel (Kadın)",     "gender": "female"},
    {"id": "tr-TR-AhmetNeural",  "name": "Ahmet (Erkek)",    "gender": "male"},
    {"id": "tr-TR-HazelNeural",  "name": "Hazel (Kadın)",    "gender": "female"},
]

DEFAULT_VOICE = "tr-TR-EmelNeural"

# Aktif faceless background adapter — modül import'unda bir kez çözülür.
_faceless_bg_adapter = get_active_faceless_background_adapter()

# Backward-compat module-level exports
FAL_VIDEO_MODEL: str = _faceless_bg_adapter.model_id
SUPPORTED_FACELESS_RATIOS: tuple[str, ...] = tuple(sorted(_faceless_bg_adapter.supported_ratios))
WEBHOOK_URL = "https://api.otomaix.com/webhooks/fal"


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

def _build_ssml(text: str, voice: str, brand_name: str = "") -> str:
    """Azure TTS için SSML yapısı oluştur.

    brand_name verilmişse script içindeki marka adını <lang xml:lang="en-US">
    ile sararak İngilizce telaffuz ettirir.
    """
    if brand_name:
        import re
        text = re.sub(
            re.escape(brand_name),
            f'<lang xml:lang="en-US">{brand_name}</lang>',
            text,
            flags=re.IGNORECASE,
        )

    return (
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="tr-TR">'
        f'<voice name="{voice}">{text}</voice>'
        '</speak>'
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

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(url, content=ssml.encode("utf-8"), headers=headers)
        if resp.status_code != 200:
            return None
        audio_bytes = resp.content

    r2_path = f"brands/{brand_id}/posts/audio/{post_id}.mp3"
    public_url = r2.upload(audio_bytes, r2_path, "audio/mpeg")
    return public_url


# ─── 3. fal.ai video üretimi ────────────────────────────────────────────────

async def generate_background_video(
    image_prompt: str,
    aspect_ratio: str,
    duration: int = 5,
) -> str:
    """fal.ai arka plan videosu üret — aktif FacelessBackgroundAdapter üzerinden.

    Returns fal job ID. Desteklenmeyen aspect_ratio için ValueError; endpoint
    katmanı submit öncesi validasyon yapmalı (SUPPORTED_FACELESS_RATIOS).
    """
    import fal_client

    os.environ["FAL_KEY"] = settings.FAL_KEY
    args = _faceless_bg_adapter.build_args(image_prompt, aspect_ratio, duration)

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
) -> dict:
    """Tam pipeline: post oluştur → script → TTS → fal.ai video.

    Returns post dict with post_id, script, audio_url.
    """
    # 1. Script üret
    script_result = await generate_script(prompt, brand_kit, brand_name, rag_context=rag_context)
    script = script_result["script"]
    duration = script_result["duration_estimate"]

    # 2. Post kaydı oluştur (script'i prompt'a kaydet)
    row = await db.fetchrow(
        """
        INSERT INTO social.posts
            (brand_id, content_type, prompt, user_text, aspect_ratio, status)
        VALUES ($1, 'video', $2, $3, $4, 'generating')
        RETURNING *
        """,
        brand_id,
        prompt,
        script,    # script'i user_text alanına kaydediyoruz
        aspect_ratio,
    )
    post = dict(row)
    post_id = post["id"]

    # 3. TTS → audio
    audio_url = await text_to_speech(script, voice, post_id, brand_id, brand_name=brand_name)

    # 4. fal.ai arka plan videosu
    sector = brand_kit.get("sector", "")
    colors = brand_kit.get("colors", [])
    if isinstance(colors, dict):
        color_str = ", ".join(f"{v}" for v in colors.values() if v)
    elif isinstance(colors, list):
        color_str = ", ".join(str(c) for c in colors if c)
    else:
        color_str = ""

    bg_parts = [
        "Faceless background video for social media, NO human figures or faces",
        f"Topic: {prompt}",
    ]
    if brand_description:
        bg_parts.append(f"Brand context: {brand_description}")
    if sector:
        bg_parts.append(f"Industry: {sector}")
    if color_str:
        bg_parts.append(f"Brand color palette: {color_str}")
    bg_parts.append("Abstract, ambient, slow motion, cinematic lighting, professional, loopable")
    image_prompt = ", ".join(bg_parts)
    try:
        fal_job_id = await generate_background_video(image_prompt, aspect_ratio, duration)
        await db.execute(
            "UPDATE social.posts SET fal_job_id = $2 WHERE id = $1",
            post_id, fal_job_id,
        )
        post["fal_job_id"] = fal_job_id
    except Exception:
        pass  # Video üretimi webhook üzerinden takip edilir

    post["script"] = script
    post["audio_url"] = audio_url
    post["duration_estimate"] = duration

    return post
