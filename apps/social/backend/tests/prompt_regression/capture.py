"""Katman-1 prompt yakalama altyapısı (plan Task 6).

Amaç: üretimin KENDİ kod yolundan geçen prompt'ları bayt-bayt dondurmak. Sektör
paketi enjeksiyonu geldiğinde (Task 8+), paketsiz bir markanın prompt'unun TEK
BİT değişmediği bu fixture'larla kanıtlanır — spec §15'in K6 kriteri.

Bağlayıcı kural: fixture üretimi ve doğrulaması AYNI yoldan geçer. Tek fark,
dondurmanın `PROMPT_REGRESSION_UPDATE=1` ile AÇIKÇA istenmesidir. Test-özel bir
prompt kurulumu YASAKTIR: burada kesilen tek şey ağ çağrısıdır, prompt'u üreten
kod üretimin kendisidir.

Harness genel arayüzdür (K-20): Marka DNA işi de aynı `capture_anthropic_calls`
ucunu tüketir.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import anthropic

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"

# Dondurmayı AÇIK talep eden bayrak. Yokluğunda fixture'lar salt-okunur kabul
# edilir: karşılaştırma başarısızlığı sessizce "güncelleme" olmaz.
UPDATE_ENV = "PROMPT_REGRESSION_UPDATE"

# Yakalanan çağrıya verilen sabit yanıt. Üretim yolu bunu ayrıştırıp akmaya
# devam eder; yanıtın İÇERİĞİ testin konusu DEĞİLDİR, prompt'tur.
_CANNED_JSON = json.dumps(
    {
        "default_caption": "sabit yanıt",
        "platform_captions": {},
        "image_prompt": "sabit görsel istemi",
        "image_prompts": ["sabit görsel istemi"],
        "hashtags": ["#sabit"],
        "script": "sabit senaryo",
    },
    ensure_ascii=False,
    sort_keys=True,
)


@dataclass
class CapturedCall:
    """Tek bir `messages.create` çağrısının TAM girdisi."""

    model: str
    system: Any
    messages: list[dict]
    extra: dict = field(default_factory=dict)

    @property
    def rendered(self) -> str:
        """Sistem + mesaj bloklarını deterministik ayraçlarla birleştirir.

        Ayraçlar blok KİMLİĞİNİ de taşır (rol, sıra, `cache_control`). Önbellek
        sınırı mimari bir karardır (3 katmanlı prompt cache); sınırın kayması
        prompt metni değişmese bile fixture'ı kırmalıdır.
        """
        lines = [f"=== model: {self.model} ==="]

        for index, block in enumerate(_as_blocks(self.system)):
            lines.append(f"=== system[{index}]{_cache_suffix(block)} ===")
            lines.append(block["text"])

        for m_index, message in enumerate(self.messages):
            role = message.get("role", "?")
            for b_index, block in enumerate(_as_blocks(message.get("content"))):
                lines.append(
                    f"=== message[{m_index}].{role}[{b_index}]"
                    f"{_cache_suffix(block)} ==="
                )
                lines.append(block["text"])

        return "\n".join(lines) + "\n"


def _as_blocks(content: Any) -> list[dict]:
    """Düz metni de blok listesini de tek biçime indirger."""
    if content is None:
        return []
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    blocks = []
    for block in content:
        if isinstance(block, str):
            blocks.append({"type": "text", "text": block})
        elif block.get("type") == "text":
            blocks.append(block)
        else:
            # Metin olmayan blok (görsel vb.) sessizce DÜŞÜRÜLMEZ: türü basılır.
            blocks.append({"type": block.get("type"), "text": f"<{block.get('type')}>"})
    return blocks


def _cache_suffix(block: dict) -> str:
    cache_control = block.get("cache_control")
    if not cache_control:
        return ""
    return f" cache_control={cache_control.get('type')}"


class _FakeUsage:
    cache_read_input_tokens = 0
    cache_creation_input_tokens = 0


class _FakeTextBlock:
    def __init__(self, text: str) -> None:
        self.text = text


class _FakeMessage:
    def __init__(self, text: str) -> None:
        self.content = [_FakeTextBlock(text)]
        self.usage = _FakeUsage()


def capture_anthropic_calls(
    monkeypatch, response_text: str = _CANNED_JSON
) -> list[CapturedCall]:
    """`anthropic.Anthropic(...).messages.create` çağrılarını yakalar.

    Dönen liste ÇAĞRI SIRASINDA dolar. Ağ çağrısı YAPILMAZ; API anahtarı da
    gerekmez (çağıranlar anahtar yoksa fallback'e düşer — o yüzden sahte bir
    anahtar kurulur, aksi hâlde prompt hiç üretilmezdi).
    """
    calls: list[CapturedCall] = []

    class _Messages:
        @staticmethod
        def create(**kwargs):
            calls.append(
                CapturedCall(
                    model=kwargs.get("model", "?"),
                    system=kwargs.get("system"),
                    messages=kwargs.get("messages", []),
                )
            )
            return _FakeMessage(response_text)

    class _FakeClient:
        def __init__(self, *_args, **_kwargs) -> None:
            self.messages = _Messages()

    monkeypatch.setattr(anthropic, "Anthropic", _FakeClient)

    from app.core.config import settings

    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "test-key-not-used", raising=False)
    return calls


def assert_matches_fixture(name: str, rendered: str) -> None:
    """Bayt-bayt karşılaştırır; `PROMPT_REGRESSION_UPDATE=1` ile dondurur.

    Dondurma AÇIK talep olmadan ASLA yapılmaz: yoksa her kırmızı test kendini
    yeşile boyardı ve fixture'ın koruma değeri sıfıra inerdi.
    """
    path = FIXTURES_DIR / f"{name}.txt"
    payload = rendered.encode("utf-8")

    if os.environ.get(UPDATE_ENV) == "1":
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        return

    if not path.exists():
        raise AssertionError(
            f"fixture yok: {path}\n"
            f"Dondurmak için: {UPDATE_ENV}=1 .venv/bin/python -m pytest "
            "tests/prompt_regression/ -q"
        )

    frozen = path.read_bytes()
    if frozen != payload:
        raise AssertionError(
            f"prompt fixture'dan SAPTI: {path.name}\n"
            f"dondurulmuş {len(frozen)} bayt, üretilen {len(payload)} bayt.\n"
            "Bu bir ALARM'dır: paketsiz markanın prompt'u değişmemeliydi."
        )
