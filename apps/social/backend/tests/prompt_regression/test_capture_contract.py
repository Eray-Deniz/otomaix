"""Yakalama harness'ının KENDİ sözleşmesi (plan Task 7, ilk adım).

Fixture'lar ancak `rendered` girdiyi KAYIPSIZ temsil ediyorsa kanıt değeri
taşır. Harness Marka DNA işinin de tüketeceği genel arayüz ilan edildi (K-20);
zengin blok kullanan ilk tüketici sessizce eksik bir fixture dondurabilirdi.

Buradaki kural: temsil edilemeyen girdi SESSİZCE GEÇMEZ, REDDEDİLİR. Alarm
üretmek, yanlış yeşilden iyidir.
"""

from __future__ import annotations

import pytest

from .capture import CapturedCall, UnrenderableBlock


def _call(**kwargs) -> CapturedCall:
    base = {"model": "m", "system": None, "messages": []}
    base.update(kwargs)
    return CapturedCall(**base)


def test_rendered_rejects_non_text_block():
    """Görsel/araç bloğu `<tip>` işaretine indirgenmez — REDDEDİLİR."""
    call = _call(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "data": "AAAA"}}
                ],
            }
        ]
    )
    with pytest.raises(UnrenderableBlock, match="image"):
        _ = call.rendered


def test_rendered_rejects_non_text_system_block():
    """Sistem tarafı da aynı kapıdan geçer."""
    call = _call(system=[{"type": "tool_result", "content": "x"}])
    with pytest.raises(UnrenderableBlock, match="tool_result"):
        _ = call.rendered


def test_rendered_rejects_unknown_cache_control_key():
    """`cache_control` yalnız `type` alanına indirgenmez.

    Bugün tek alan var; yarın bir alan eklenirse (ör. `ttl`) fixture bunu
    görmeden aynı kalırdı — önbellek sınırı mimari bir karardır, sessizce
    kaymamalı.
    """
    call = _call(
        system=[
            {
                "type": "text",
                "text": "abc",
                "cache_control": {"type": "ephemeral", "ttl": "1h"},
            }
        ]
    )
    with pytest.raises(UnrenderableBlock, match="cache_control"):
        _ = call.rendered


def test_rendered_accepts_plain_text_and_known_cache_control():
    """Bugünkü biçim aynen geçer — mevcut fixture'lar bayt-aynı kalır."""
    call = _call(
        system=[{"type": "text", "text": "abc", "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": "merhaba"}],
    )
    rendered = call.rendered
    assert "=== system[0] cache_control=ephemeral ===" in rendered
    assert "merhaba" in rendered
