"""Katman-1: legacy kısa video ucu — K-06 "bozuk-boş" kapısı (plan Task 7).

`/posts/generate-short-video` sektör rehberini marka satırının GÖRÜNEN ADINDAN
(`brands.sector`, ör. "Teknoloji") arıyor; `SECTOR_GUIDANCE` ise SLUG anahtarlı
(`teknoloji`). Sonuç: rehber bugün HER MARKADA boş. Bu bozukluk düzeltilmez —
AYNEN dondurulur. Sektör paketi enjeksiyonu (Task 10+) bu ucu değiştirdiğinde
fixture kırmızıya döner ve değişiklik BİLİNÇLİ olmak zorunda kalır.

Üretimin kendi kod yolu koşar: router → `run_short_video_pipeline` →
`generate_script`. Yalnız dış dünyaya çıkan iki uç (ElevenLabs TTS, fal.ai)
kesilir.
"""

from __future__ import annotations

import uuid

import pytest

from app.core.database import _init_connection
from app.core.templates_data import SECTOR_GUIDANCE
from app.models.schemas import ShortVideoGenerate
from app.routers import posts as posts_router
from app.services import short_video

from .capture import assert_matches_fixture, capture_anthropic_calls

# Görünen ad — slug DEĞİL. Bozukluğun kaynağı tam olarak budur.
BRAND_SECTOR_DISPLAY_NAME = "Teknoloji"

# Türkçe karakter taşıyan konu: `_looks_turkish` dalı açılır ve legacy uç
# durağan kare istemini de üretir (iki çağrı birden yakalanır).
LEGACY_PROMPT = "Yeni sürüm duyurusu için kısa video"


async def _seed_owner_and_brand(db) -> tuple[str, uuid.UUID]:
    """Sahiplik zinciri: account → workspace → membership → brand."""
    account_id = await db.fetchval(
        """
        INSERT INTO social.accounts (email, name, plan_id)
        VALUES ($1, $2, 'pro')
        RETURNING id
        """,
        f"donuk-{uuid.uuid4()}@example.test",
        "Donuk Sahip",
    )
    workspace_id = await db.fetchval(
        "INSERT INTO social.workspaces (account_id, name) VALUES ($1, $2) RETURNING id",
        account_id,
        "Donuk Çalışma Alanı",
    )
    await db.execute(
        "INSERT INTO social.workspace_members (workspace_id, account_id) VALUES ($1, $2)",
        workspace_id,
        account_id,
    )
    brand_id = await db.fetchval(
        """
        INSERT INTO social.brands
            (workspace_id, name, description, website_url, sector, brand_kit)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id
        """,
        workspace_id,
        "Donuk Teknoloji",
        "Küçük işletmeler için bulut yazılımı.",
        "https://donukteknoloji.example",
        BRAND_SECTOR_DISPLAY_NAME,
        {
            "tonality": "professional",
            "hashtags": ["#teknoloji", "#bulut", "#kobi"],
            "colors": {"primary": "#0A84FF", "secondary": "#1C1C1E"},
        },
    )
    return str(account_id), brand_id


@pytest.fixture
async def legacy_db(db):
    """Üretimin KENDİ bağlantı yapılandırması (jsonb codec) uygulanmış bağlantı."""
    await _init_connection(db)
    return db


async def test_legacy_short_video_guidance_is_empty_today(legacy_db, monkeypatch):
    """Legacy uç sektör rehberini BOŞ geçiyor — bugünkü gerçek (K-06)."""
    account_id, brand_id = await _seed_owner_and_brand(legacy_db)

    calls = capture_anthropic_calls(monkeypatch, response_text="Donuk bir senaryo.")

    # Dış dünya kesilir: TTS ve fal.ai çağrısı yapılmaz.
    async def _fake_tts(*_args, **_kwargs):
        return {"audio_url": "https://assets.example/donuk.mp3", "word_timestamps": []}

    async def _fake_background_video(*_args, **_kwargs):
        return "fal-job-donuk"

    monkeypatch.setattr(short_video, "text_to_speech", _fake_tts)
    monkeypatch.setattr(short_video, "generate_background_video", _fake_background_video)

    # Ön koşul ölçümü: aranan anahtar rehber tablosunda YOK — bozukluk buradan doğar.
    assert BRAND_SECTOR_DISPLAY_NAME not in SECTOR_GUIDANCE
    assert SECTOR_GUIDANCE.get(BRAND_SECTOR_DISPLAY_NAME, "") == ""

    payload = ShortVideoGenerate(brand_id=brand_id, prompt=LEGACY_PROMPT)
    await posts_router.generate_short_video(
        payload=payload, user={"sub": account_id}, db=legacy_db
    )

    # İki çağrı: script istemi + durağan kare istemi. Sayı tutmuyorsa yüzey
    # sessizce fallback'e düşmüştür ve karşılaştırma boşuna yeşil kalırdı.
    assert len(calls) == 2, f"iki çağrı bekleniyordu, {len(calls)} oldu"
    script_call, still_call = calls

    # Bozuk-boş davranışın kanıtı: rehber bloğu prompt'a HİÇ girmiyor.
    assert "SEKTÖR REHBERİ" not in script_call.rendered
    assert_matches_fixture("legacy_short_video__script", script_call.rendered)

    # Durağan kare istemi sektörü yalnız serbest metin olarak taşır.
    assert f"Industry: {BRAND_SECTOR_DISPLAY_NAME}" in still_call.rendered
    assert_matches_fixture("legacy_short_video__still", still_call.rendered)


async def test_legacy_guidance_would_be_non_empty_with_slug(legacy_db):
    """Pozitif kontrol: aynı sektörün SLUG'ı arandığında rehber DOLU.

    Bu test olmadan "boş" sonucu iki nedenden gelebilirdi — anahtar uyuşmazlığı
    ya da rehber tablosunun kendisinin boş olması. Ayrımı burası yapar.
    """
    assert SECTOR_GUIDANCE.get("teknoloji", "").strip() != ""
