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


# ─── Checkpoint 7 bulguları (iki orta) ──────────────────────────────────────


def test_update_flag_must_be_unset_for_verification():
    """Dondurma bayrağı ortamda ASILI kalırsa koşum yeşil raporlayamaz.

    Bulgu (checkpoint 7): `PROMPT_REGRESSION_UPDATE=1` süreç ortamından
    devralınıyordu. Bir kez dondurmak için export eden operatör, ardından
    "bayraksız" sandığı doğrulamayı koşarsa TÜM sapmış fixture'lar sessizce
    yeniden yazılır ve sweep yeşil döner — bu kapının önlemek için var olduğu
    yanlış-yeşilin tam kendisi.

    Kapı testin KENDİSİDİR: dondurma koşumu artık kırmızı raporlar, yani hiçbir
    dondurma koşumu doğrulama koşumu yerine geçemez. Sıra: önce bayrakla dondur
    (bu test kırmızı), sonra bayraksız doğrula (hepsi yeşil).
    """
    import os

    from .capture import UPDATE_ENV

    assert os.environ.get(UPDATE_ENV) != "1", (
        f"{UPDATE_ENV}=1 AÇIK — bu bir DONDURMA koşumudur, doğrulama değil. "
        "Fixture'lar yeniden yazıldı; doğrulama için bayrağı kaldırıp tekrar koş."
    )


def test_rendered_rejects_mapping_content():
    """Blok listesi yerine tek bir sözlük gelirse anahtarları metin sanılmaz."""
    call = _call(
        messages=[{"role": "user", "content": {"type": "image", "source": {"d": 1}}}]
    )
    with pytest.raises(UnrenderableBlock, match="dict"):
        _ = call.rendered


def test_rendered_rejects_unknown_text_block_field():
    """Metin bloğunun tanınmayan üst alanı sessizce DÜŞMEZ.

    `cache_control` için kapatılan boşluğun aynısı bloğun kendisinde de açıktı:
    ör. `citations` taşıyan bir blok, alan görünmeden aynı baytlara iniyordu.
    """
    call = _call(system=[{"type": "text", "text": "abc", "citations": [{"x": 1}]}])
    with pytest.raises(UnrenderableBlock, match="citations"):
        _ = call.rendered


def test_rendered_rejects_text_block_without_text():
    """`type=text` ama `text` alanı yok — bozuk blok reddedilir."""
    call = _call(system=[{"type": "text"}])
    with pytest.raises(UnrenderableBlock, match="text"):
        _ = call.rendered


def test_rendered_rejects_empty_cache_control():
    """Boş `cache_control`, "önbellek yok" ile AYNI şey sayılmaz."""
    call = _call(system=[{"type": "text", "text": "abc", "cache_control": {}}])
    with pytest.raises(UnrenderableBlock, match="cache_control"):
        _ = call.rendered
