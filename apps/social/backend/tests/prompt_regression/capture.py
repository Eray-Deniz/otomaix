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

# `cache_control` içinde basılan alanlar. Küme fail-closed'dır: dışında bir alan
# görülürse yakalama REDDEDİLİR (bkz. `_cache_suffix`).
_KNOWN_CACHE_CONTROL_KEYS = frozenset({"type"})

# Metin bloğunda basılan alanlar. Küme fail-closed'dır: dışında bir alan
# görülürse yakalama REDDEDİLİR (bkz. `_require_closed_text_block`).
_KNOWN_TEXT_BLOCK_KEYS = frozenset({"type", "text", "cache_control"})


class UnrenderableBlock(AssertionError):
    """Kayıpsız temsil edilemeyen bir girdi bloğu yakalandı.

    `AssertionError` türevi: pytest bunu test hatası olarak gösterir ve sessiz
    bir geçiş yerine ALARM üretir.
    """

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
    """Düz metni de blok listesini de tek biçime indirger.

    KAYIPLI temsil YOKTUR. Üç kapı da fail-closed'dır (checkpoint 7):

    1. **Kap:** yalnız düz metin veya liste/demet kabul edilir. Sözlük REDDEDİLİR
       — `for block in content` bir sözlüğü ANAHTARLARI üzerinden gezer ve
       `{"type": "image", ...}` sessizce "type" + "source" metin bloklarına
       inerdi (ölçüldü).
    2. **Blok:** metin olmayan blok (görsel, araç sonucu) `<tip>` işaretine
       indirgenmez. İki farklı görsel aynı işarete inseydi fixture değişmeden
       prompt değişebilirdi.
    3. **Şema:** metin bloğunun alan kümesi KAPALIDIR. Tanınmayan bir üst alan
       (ör. `citations`) sessizce düşmez — basılmayan alan, görünmeyen davranış
       demektir.
    """
    if content is None:
        return []
    if isinstance(content, str):
        return [{"type": "text", "text": content}]
    if not isinstance(content, (list, tuple)):
        raise UnrenderableBlock(
            f"blok kabı liste değil: {type(content).__name__} "
            "(sözlük verilirse anahtarları metin sanılırdı). "
            "İçerik ya düz metin ya da blok LİSTESİ olmalıdır."
        )
    blocks = []
    for block in content:
        if isinstance(block, str):
            blocks.append({"type": "text", "text": block})
        elif isinstance(block, dict) and block.get("type") == "text":
            _require_closed_text_block(block)
            blocks.append(block)
        else:
            kind = block.get("type") if isinstance(block, dict) else type(block).__name__
            raise UnrenderableBlock(
                f"metin olmayan blok kayıpsız temsil edilemiyor: type={kind!r}. "
                "Bu yüzeyi dondurmadan ÖNCE harness'a o blok türü için "
                "deterministik ve kayıpsız bir temsil eklenmelidir."
            )
    return blocks


def _require_closed_text_block(block: dict) -> None:
    """Metin bloğunun basılan alan kümesini doğrular — fazlası REDDEDİLİR."""
    unknown = set(block) - _KNOWN_TEXT_BLOCK_KEYS
    if unknown:
        raise UnrenderableBlock(
            f"metin bloğu tanınmayan alan taşıyor: {sorted(unknown)}. "
            "Harness bu alanları basmıyor; temsil eklenmeden fixture dondurulamaz."
        )
    if not isinstance(block.get("text"), str):
        raise UnrenderableBlock(
            "metin bloğunda `text` alanı yok veya metin değil — bozuk blok "
            "sessizce boş basılmaz."
        )


def _cache_suffix(block: dict) -> str:
    """Önbellek sınırını basar; tanınmayan alan varsa REDDEDER.

    Bugün `cache_control` tek alan taşıyor (`type`). Yarın bir alan eklenirse
    (ör. `ttl`) yalnız `type` basmak onu görünmez kılardı — önbellek sınırı
    mimari bir karardır (3 katmanlı prompt cache), sessizce kaymamalı.
    """
    if "cache_control" not in block:
        return ""
    cache_control = block["cache_control"]
    if not isinstance(cache_control, dict) or not cache_control:
        # Boş/bozuk `cache_control`, "önbellek yok" ile AYNI şey DEĞİLDİR:
        # ikisi aynı bayta inseydi sınırın kaybolması görünmezdi.
        raise UnrenderableBlock(
            f"cache_control bozuk veya boş: {cache_control!r} — "
            "önbellek sınırı sessizce yok sayılmaz."
        )
    unknown = set(cache_control) - _KNOWN_CACHE_CONTROL_KEYS
    if unknown:
        raise UnrenderableBlock(
            f"cache_control tanınmayan alan taşıyor: {sorted(unknown)}. "
            "Harness bu alanı basmıyor; temsil eklenmeden fixture dondurulamaz."
        )
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

    İş sırası İKİ adımdır (checkpoint 7): bayrakla dondur — bu koşum
    `test_update_flag_must_be_unset_for_verification` yüzünden KIRMIZI raporlar,
    çünkü bir dondurma koşumu doğrulama koşumu DEĞİLDİR — sonra bayrağı kaldırıp
    doğrula. Böylece ortamda asılı kalmış bir bayrak asla yeşil bir doğrulama
    üretemez.
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
