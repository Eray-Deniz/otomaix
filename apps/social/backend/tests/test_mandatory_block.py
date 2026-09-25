"""Paketin kuralları tek zorunlu blokta, `Z*` kimlikleriyle (tasarım notu 2026-09-25 §3.3-A, §3.11; plan Task 6)."""

from __future__ import annotations

import itertools
import re
import uuid

import pytest

from app.services.sector_content_schema import DELIBERATELY_EMPTY, split_tone_lines
from app.services.sector_packages import (
    MANDATORY_PRIORITY_LINE,
    MANDATORY_PRIORITY_ORDER_LINE,
    RenderedRules,
    SectorPackageContext,
    render_mandatory_block,
)

from .test_sector_packages_service import _valid_content

_Z_LINE = re.compile(r"^Z(\d+): (.+)$")

_TONE_PARAGRAPH = "Güven eksenli, bilgilendirici danışman dili; ayar ve gramaj açıkça söylenir."
_TONE_LINES = (
    "Ayar, gramaj ve işçilik açıkça söylenir.\n"
    "ton (yumuşak): güven eksenli danışman dili\n"
    "Baskıcı satış ve sahte aciliyet kullanılmaz.\n"
    "ton (yumuşak): duygu ekseni anı ve hediye"
)
_FACTS = {
    "absent": None,
    "empty": [DELIBERATELY_EMPTY],
    "two": ["22 ayar saf değildir; saf altın 24 ayardır.", "Gram fiyatı günlük değişir."],
}
_BANS = {
    "empty": [DELIBERATELY_EMPTY],
    "five": [
        "Yatırım getirisi vaadi verilmez.",
        "Sahte aciliyet kullanılmaz.",
        "Rakip karşılaştırması yapılmaz.",
        "Yetki belgesi numarasız ilan verilmez.",
        "Değer garantisi verilmez.",
    ],
}
_SERVICES = {"none": [], "two": ["Takı onarımı", "Yüzük ölçü ayarı"]}
_CHANNELS = {
    "none": None,
    "empty": {},
    "full": {
        "whatsapp_hatti": True,
        "fiziksel_magaza": True,
        "randevu_sistemi": True,
        "eticaret_sitesi": True,
    },
}


def _context(*, tone=_TONE_PARAGRAPH, facts="two", bans="five") -> SectorPackageContext:
    content = _valid_content(ton_ve_dil=tone, yasaklar_ve_hassasiyetler=list(_BANS[bans]))
    if _FACTS[facts] is not None:
        content["sektor_gercekleri"] = list(_FACTS[facts])
    return SectorPackageContext(
        package_id=uuid.uuid4(), version=2, content=content, sub_sector_slug="kuyumculuk"
    )


def _z_lines(text: str) -> list[tuple[str, str]]:
    return [(f"Z{m.group(1)}", m.group(2)) for m in map(_Z_LINE.match, text.splitlines()) if m]


@pytest.mark.parametrize(
    ("tone", "facts", "bans", "services", "channels"),
    list(
        itertools.product(
            (_TONE_PARAGRAPH, _TONE_LINES), _FACTS, _BANS, _SERVICES, _CHANNELS
        )
    ),
)
def test_every_binding_line_has_exactly_one_id_generated(tone, facts, bans, services, channels):
    context = _context(tone=tone, facts=facts, bans=bans)
    result = render_mandatory_block(
        context, surface="caption", channels=_CHANNELS[channels], services=_SERVICES[services]
    )

    assert isinstance(result, RenderedRules)
    printed = _z_lines(result.text)
    # Metindeki kimlikli satırlar == haritanın kendisi, basım sırasıyla, Z1'den ardışık.
    assert printed == list(result.rules)
    assert [k for k, _ in printed] == [f"Z{i}" for i in range(1, len(printed) + 1)]

    rule_texts = [t for _, t in result.rules]
    tone_rules, tone_soft = split_tone_lines(tone)
    expected_binding = list(tone_rules)
    expected_binding += [f for f in (_FACTS[facts] or []) if f != DELIBERATELY_EMPTY]
    expected_binding += [b for b in _BANS[bans] if b != DELIBERATELY_EMPTY]
    for text in expected_binding:
        assert text in rule_texts, f"bağlayıcı satır kimliksiz basıldı: {text!r}"
    # Kimliksiz basılmış bağlayıcı satır yok: her bağlayıcı metin YALNIZ Z satırında geçer.
    for line in result.text.splitlines():
        if _Z_LINE.match(line):
            continue
        for text in expected_binding:
            assert text not in line, f"bağlayıcı metin kimliksiz satırda: {line!r}"
    # Yumuşak ton satırları kural DEĞİLDİR.
    for soft in tone_soft:
        assert soft not in rule_texts
        assert f"Ton (yumuşak yönlendirme): {soft}" in result.text


def test_priority_line_verbatim_and_order():
    result = render_mandatory_block(
        _context(), surface="caption", channels=_CHANNELS["full"], services=_SERVICES["two"]
    )
    lines = result.text.splitlines()

    assert MANDATORY_PRIORITY_LINE == (
        "Bu kurallar şablon varsayılanlarının, genel yazım kurallarının ve ürün açıklaması/teknik "
        "spec kuralının ÜSTÜNDEDİR; ama KULLANICI İSTEĞİNİN, gerçek ÜRÜN BİLGİSİNİN ve MARKA "
        "DNA'sının (markaya özgü yasak kelimeler dâhil) ALTINDADIR. Ürün bilgisiyle çelişen paket "
        "kuralı uygulanmaz; marka yasak kelimesi paket kuralına ve genel kurallara karşı kazanır. "
        "Kullanıcı isteği bir kuralla çatışıyorsa isteğe uy ve her çiğnenen kuralı `kural_uyumu`nda "
        "'istek gereği çiğnendi' diye işaretle."
    )
    assert MANDATORY_PRIORITY_LINE in lines
    assert MANDATORY_PRIORITY_ORDER_LINE in lines
    # Ürün bilgisi + marka DNA'sı paketin ÜSTÜNDE (N1); kullanıcı isteği en üstte.
    order = MANDATORY_PRIORITY_ORDER_LINE
    assert order.index("kullanıcının açık isteği") < order.index("gerçek ürün bilgisi")
    assert order.index("marka DNA") < order.index("paket zorunlu kuralları")
    assert order.index("paket zorunlu kuralları") < order.index("genel yazım")
    assert order.index("genel yazım") < order.index("şablon varsayılanları")
    # Öncelik satırları son kuraldan SONRA gelir.
    last_rule = max(i for i, line in enumerate(lines) if _Z_LINE.match(line))
    assert lines.index(MANDATORY_PRIORITY_LINE) > last_rule
    assert lines.index(MANDATORY_PRIORITY_ORDER_LINE) > lines.index(MANDATORY_PRIORITY_LINE)
    assert lines[1] == "--- SEKTÖR PAKETİ · ZORUNLU KURALLAR (kuyumculuk) ---"


def test_idea_surface_omits_declaration_sentence():
    caption = render_mandatory_block(
        _context(), surface="caption", channels=_CHANNELS["full"], services=_SERVICES["two"]
    )
    idea = render_mandatory_block(
        _context(), surface="idea", channels=_CHANNELS["full"], services=_SERVICES["two"]
    )
    assert "kural_uyumu" in caption.text
    assert "kural_uyumu" not in idea.text
    assert "çiğnendi" not in idea.text
    # Kurallar aynı sayıda basılır; yalnız beyan kısmı yüzeye göre değişir.
    assert [k for k, _ in idea.rules] == [k for k, _ in caption.rules]


def test_deliberately_empty_items_are_not_rules():
    result = render_mandatory_block(
        _context(facts="empty", bans="empty"),
        surface="caption",
        channels=None,
        services=[],
    )
    assert all(DELIBERATELY_EMPTY not in text for _, text in result.rules)
    assert DELIBERATELY_EMPTY not in result.text


def test_mandatory_block_byte_stable():
    context = _context(tone=_TONE_LINES)
    first = render_mandatory_block(
        context, surface="caption", channels=_CHANNELS["full"], services=_SERVICES["two"]
    )
    reordered = dict(reversed(list(_CHANNELS["full"].items())))
    second = render_mandatory_block(
        context, surface="caption", channels=reordered, services=_SERVICES["two"]
    )
    assert first == second


def test_scope_rule_and_channel_service_lines_only_in_mandatory_block():
    result = render_mandatory_block(
        _context(), surface="caption", channels=_CHANNELS["full"], services=_SERVICES["two"]
    )
    lines = result.text.splitlines()
    scope_rules = [t for _, t in result.rules if t.startswith("Kapsam dışı ürün için")]
    assert len(scope_rules) == 1
    assert "ürün kapsam dışı: <ürün>" in scope_rules[0]
    assert sum(line.startswith("Markanın kanalları:") for line in lines) == 1
    assert sum(line.startswith("Markanın hizmetleri:") for line in lines) == 1
    assert "Markanın hizmetleri: Takı onarımı, Yüzük ölçü ayarı" in lines
    assert any("Markanın sahip olmadığı kanalı VEYA HİZMETİ önerme" in t for _, t in result.rules)


def test_unknown_surface_raises():
    with pytest.raises(ValueError, match="yüzey"):
        render_mandatory_block(_context(), surface="video", channels=None, services=[])
