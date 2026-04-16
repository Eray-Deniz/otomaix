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

# Sabit Türkçe ses listesi
TURKISH_VOICES = [
    {"id": "tr-TR-EmelNeural",   "name": "Emel (Kadın)",     "gender": "female"},
    {"id": "tr-TR-AhmetNeural",  "name": "Ahmet (Erkek)",    "gender": "male"},
    {"id": "tr-TR-HazelNeural",  "name": "Hazel (Kadın)",    "gender": "female"},
]

DEFAULT_VOICE = "tr-TR-EmelNeural"

# fal.ai video model
FAL_VIDEO_MODEL = "fal-ai/hunyuan-video"
WEBHOOK_URL = "https://api.otomaix.com/webhooks/fal"


# ─── 1. Script üretimi ──────────────────────────────────────────────────────

async def generate_script(prompt: str, brand_kit: dict, brand_name: str = "") -> dict:
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
        "Yaklaşık 30-60 saniye sürecek uzunlukta yaz (75-150 kelime)."
    )
    user_msg = (
        f"Marka: {brand_name}\n"
        f"Sektör: {sector}\n"
        f"Üslup: {tone_tr}\n\n"
        f"Konu: {prompt}\n\n"
        "Bu konuda bir sosyal medya videosu için Türkçe script yaz. "
        "Sadece script metnini yaz, başka açıklama ekleme."
    )

    try:
        import anthropic

        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=400,
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

def _build_ssml(text: str, voice: str) -> str:
    """Azure TTS için SSML yapısı oluştur."""
    import xml.etree.ElementTree as ET
    root = ET.Element("speak", version="1.0")
    root.set("xmlns", "http://www.w3.org/2001/10/synthesis")
    root.set("xml:lang", "tr-TR")
    v = ET.SubElement(root, "voice", name=voice)
    v.text = text
    return ET.tostring(root, encoding="unicode")


async def text_to_speech(
    script_text: str,
    voice: str,
    post_id: UUID,
    brand_id: UUID,
) -> str | None:
    """Azure TTS REST API → mp3 → R2. Returns public_url veya None."""
    if not settings.AZURE_TTS_KEY or not settings.AZURE_TTS_REGION:
        return None

    from app.services.storage import r2

    ssml = _build_ssml(script_text, voice)
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
    """fal.ai HunyuanVideo ile arka plan videosu üret. Returns fal job ID."""
    import fal_client

    os.environ["FAL_KEY"] = settings.FAL_KEY

    # Aspect ratio → resolution mapping
    res_map = {
        "9:16": "720x1280",
        "1:1": "720x720",
        "16:9": "1280x720",
        "4:5": "720x900",
    }
    resolution = res_map.get(aspect_ratio, "720x1280")

    handler = await fal_client.submit_async(
        FAL_VIDEO_MODEL,
        arguments={
            "prompt": image_prompt,
            "resolution": resolution,
            "video_length": "5s",
            "num_inference_steps": 30,
        },
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
) -> dict:
    """Tam pipeline: post oluştur → script → TTS → fal.ai video.

    Returns post dict with post_id, script, audio_url.
    """
    # 1. Script üret
    script_result = await generate_script(prompt, brand_kit, brand_name)
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
    audio_url = await text_to_speech(script, voice, post_id, brand_id)

    # 4. fal.ai arka plan videosu
    image_prompt = f"Abstract background video for social media, {prompt}, professional, cinematic"
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
