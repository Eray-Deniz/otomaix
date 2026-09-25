"""Şema sürümüne duyarlı yaprak modül (tasarım notu 2026-09-25 §3.9; plan Task 1, D2, D12)."""

from __future__ import annotations

import itertools

import pytest

from app.services import sector_content_schema as sema
from app.services.sector_content_schema import (
    CURRENT_SCHEMA_VERSION,
    DELIBERATELY_EMPTY,
    POST_TYPES,
    SCHEMA_FIELDS,
    hook_type,
    split_tone_lines,
    structural_errors,
)

_V1_FIELDS = {
    "kapsam",
    "ton_ve_dil",
    "gorsel_kodlar",
    "cta_kaliplari",
    "kanca_kaliplari",
    "takvim_temalari",
    "yasaklar_ve_hassasiyetler",
    "video_kodlar",
    "ozel_gun",
}


def _v1_content() -> dict:
    return {
        "kapsam": "Altın ve pırlanta takı perakendesi.",
        "ton_ve_dil": "Güven eksenli danışman dili; ayar ve gramaj açıkça söylenir.",
        "gorsel_kodlar": "Makro detay, doğal ışık.",
        "cta_kaliplari": [
            {"kalip": "Mağazamıza bekleriz", "tur": "ziyaret", "gerekce": "Yerel alışveriş"},
        ],
        "kanca_kaliplari": ["[hediye kararsızlığı] + [takı tipi]"],
        "takvim_temalari": ["Düğün sezonu"],
        "yasaklar_ve_hassasiyetler": ["Getiri garantisi verilmez."],
        "video_kodlar": {"hareket": ["Yavaş dönüş"], "sahne": ["Vitrin önü"]},
        "ozel_gun": {},
    }


def _v2_content() -> dict:
    content = _v1_content()
    content["sektor_gercekleri"] = ["22 ayar saf değildir; saf altın 24 ayardır."]
    return content


def test_schema_fields_closed_sets_per_version():
    assert set(SCHEMA_FIELDS) == {1, 2}
    assert SCHEMA_FIELDS[1] == frozenset(_V1_FIELDS)
    assert SCHEMA_FIELDS[2] == frozenset(_V1_FIELDS | {"sektor_gercekleri"})
    assert CURRENT_SCHEMA_VERSION == 2
    assert POST_TYPES == ("satis", "hizmet", "bilgi", "kutlama", "anma")
    assert "sektor_gercekleri" in sema.LIST_FIELDS
    assert sema.TEXT_FIELDS == ("kapsam", "ton_ve_dil", "gorsel_kodlar")


def test_structural_errors_requires_explicit_schema_version():
    with pytest.raises(TypeError):
        structural_errors(_v1_content())  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        structural_errors(_v1_content(), 1)  # type: ignore[misc]


def test_v1_content_valid_v1_invalid_v2_and_reverse():
    assert structural_errors(_v1_content(), schema_version=1) == []
    v1_under_v2 = structural_errors(_v1_content(), schema_version=2)
    assert any("eksik alan" in e and "sektor_gercekleri" in e for e in v1_under_v2)

    assert structural_errors(_v2_content(), schema_version=2) == []
    v2_under_v1 = structural_errors(_v2_content(), schema_version=1)
    assert any("şema dışı alan" in e and "sektor_gercekleri" in e for e in v2_under_v1)


def test_unknown_schema_version_is_an_error_not_a_pass():
    for version in (0, 3, -1):
        errors = structural_errors(_v2_content(), schema_version=version)
        assert errors, version
        assert any("şema sürümü" in e for e in errors)


def test_sektor_gercekleri_empty_rejected_deliberately_empty_accepted():
    empty = _v2_content()
    empty["sektor_gercekleri"] = []
    assert any("sektor_gercekleri boş" in e for e in structural_errors(empty, schema_version=2))

    deliberate = _v2_content()
    deliberate["sektor_gercekleri"] = [DELIBERATELY_EMPTY]
    assert structural_errors(deliberate, schema_version=2) == []


_HOOK_TEXT = "[hediye kararsızlığı] + [takı tipi]"


@pytest.mark.parametrize(
    ("tagged", "value", "spacing"),
    list(
        itertools.product(
            (True, False),
            POST_TYPES + ("reklam",),
            ("(tür: {v})", "(tür:{v})", "( tür : {v} )", "(tür: {v})  "),
        )
    ),
)
def test_hook_type_grammar_generated_matrix(tagged, value, spacing):
    item = f"{_HOOK_TEXT} {spacing.format(v=value)}" if tagged else _HOOK_TEXT
    content = _v2_content()
    content["kanca_kaliplari"] = [item]
    errors = structural_errors(content, schema_version=2)

    if not tagged:
        assert hook_type(item) == (_HOOK_TEXT, "satis")
        assert errors == []
    elif value in POST_TYPES:
        assert hook_type(item) == (_HOOK_TEXT, value)
        assert errors == []
    else:
        with pytest.raises(ValueError):
            hook_type(item)
        assert any("kanca_kaliplari[0]" in e and "tür" in e for e in errors)


def test_hook_tag_is_not_checked_on_schema_1():
    """1. sürüm içerikte etiket yok; şema-1 kapısı kanca grameri denetlemez."""
    content = _v1_content()
    content["kanca_kaliplari"] = [f"{_HOOK_TEXT} (tür: reklam)"]
    assert structural_errors(content, schema_version=1) == []


def test_split_tone_lines_single_paragraph_is_one_rule():
    paragraph = (
        "Güven eksenli danışman dili: ayar açıkça söylenir. Baskıcı satış kullanılmaz."
    )
    assert split_tone_lines(paragraph) == ((paragraph,), ())


def test_split_tone_lines_soft_prefix():
    text = (
        "Ayar, gramaj ve işçilik açıkça söylenir.\n"
        "ton (yumuşak): güven eksenli danışman dili\n"
        "\n"
        "Baskıcı satış ve sahte aciliyet kullanılmaz.\n"
        "Ton (Yumuşak):   duygu ekseni anı ve hediye  \n"
    )
    rules, soft = split_tone_lines(text)
    assert rules == (
        "Ayar, gramaj ve işçilik açıkça söylenir.",
        "Baskıcı satış ve sahte aciliyet kullanılmaz.",
    )
    assert soft == ("güven eksenli danışman dili", "duygu ekseni anı ve hediye")



# Checkpoint 1 (Codex, high): tür anahtarı taşıyan ama TANINMAYAN her biçim kancayı
# sessizce `satis` yapıyordu. Kural pozitiftir: `tür` anahtarı YALNIZ kalıbın sonundaki
# TEK ve kurallı `(tür: <değer>)` etiketinde geçebilir; başka her biçim yapısal hatadır.
_TAG_FORMS = {
    "paren-colon": "(tür: {v})",
    "paren-space": "(tür {v})",
    "paren-equals": "(tür={v})",
    "bracket-colon": "[tür: {v}]",
    "bare-colon": "tür: {v}",
    "upper-paren-colon": "(TÜR: {v})",
}


@pytest.mark.parametrize(
    ("form", "position", "count"),
    list(itertools.product(_TAG_FORMS, ("terminal", "middle", "leading"), (1, 2))),
)
def test_hook_type_key_only_in_single_terminal_tag_generated(form, position, count):
    tag = " ".join(_TAG_FORMS[form].format(v=v) for v in ("hizmet", "bilgi")[:count])
    item = {
        "terminal": f"{_HOOK_TEXT} {tag}",
        "middle": f"{_HOOK_TEXT} {tag} (kanal: instagram)",
        "leading": f"{tag} {_HOOK_TEXT}",
    }[position]
    well_formed = form in ("paren-colon", "upper-paren-colon")

    if well_formed and position == "terminal" and count == 1:
        assert hook_type(item) == (_HOOK_TEXT, "hizmet")
        return
    with pytest.raises(ValueError):
        hook_type(item)
    content = _v2_content()
    content["kanca_kaliplari"] = [item]
    assert any("kanca_kaliplari[0]" in e for e in structural_errors(content, schema_version=2))


@pytest.mark.parametrize(
    "literal",
    ["(örnek: yüzük)", "(Türk işi)", "(türü fark etmez)", "(kanal: instagram)", "(tura çıkın)"],
)
def test_hook_literal_parentheses_without_the_key_stay_untagged(literal):
    item = f"{_HOOK_TEXT} {literal}"
    assert hook_type(item) == (item, "satis")


# Checkpoint 1 tur 2 (Codex, F1 yeniden açıldı): görünmez biçim karakteri (Unicode `Cf`)
# anahtarın ya da etiketin içine girince etiket yine sessizce kayboluyordu. Sınıf
# "okunuşu aynı, baytı farklı metin"dir; kanal bayraklarındaki ortak ölçüyle kapatılır.
_INVISIBLES = ("​", "‌", "‍", "⁠", "­", "﻿")
_TAG = "(tür: hizmet)"


@pytest.mark.parametrize(
    ("char", "position"), list(itertools.product(_INVISIBLES, range(len(_TAG) + 1)))
)
def test_invisible_characters_never_hide_the_tag_generated(char, position):
    tag = _TAG[:position] + char + _TAG[position:]
    item = f"{_HOOK_TEXT} {tag}"
    assert hook_type(item) == (_HOOK_TEXT, "hizmet")
    content = _v2_content()
    content["kanca_kaliplari"] = [item]
    assert structural_errors(content, schema_version=2) == []


@pytest.mark.parametrize("variant", ["（tür: hizmet）", "(ｔüｒ: hizmet)", "(tür： hizmet)"])
def test_width_variants_never_silently_default(variant):
    """Tam genişlikli biçimler ya doğru etiketlenir ya reddedilir — sessiz `satis` YOK."""
    item = f"{_HOOK_TEXT} {variant}"
    try:
        assert hook_type(item) == (_HOOK_TEXT, "hizmet")
    except ValueError:
        pass


@pytest.mark.parametrize("char", _INVISIBLES)
def test_soft_tone_prefix_read_on_visible_text(char):
    rules, soft = split_tone_lines(f"Ayar açıkça söylenir.\nton (yu{char}muşak): danışman dili")
    assert rules == ("Ayar açıkça söylenir.",)
    assert soft == ("danışman dili",)
