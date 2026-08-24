"""Paket erişim katmanı — normalize · doğrulayıcı · çözümleyici (plan Task 8).

Üç sözleşme burada pinlenir:

1. **Tek normalize modülü (K-01b).** Yazım tarafı (doğrulayıcı) ve okuma tarafı
   (çözümleyici) AYNI fonksiyonu kullanır; ikinci kopya yazılamaz. Kural seti
   `sector_resolver._normalize_slug` ile eşittir — eşitlik testle bağlanır.
2. **Yazım kapısı (spec §3.4).** Kapalı alan kümesi, özel gün anahtarlarının
   sistem takvimine karşı doğrulanması, marka adı yasağı (K-15 üçüncü bileşen),
   bilinçli boşun özel temsili (K-120), boyut tavanının UYARI olması (İlke 9).
3. **Güvenli geri düşüş (spec §4.2).** Çözümleyicinin hiçbir hatası üretimi
   bloklamaz: her başarısızlık `None` + gözlemlenebilir log demektir.
"""

from __future__ import annotations

import logging
import uuid

import pytest

from app.services.sector_packages import (
    SectorPackageContext,
    normalize_special_day_key,
    resolve_package_context,
    validate_package_content,
)
from app.services.sector_resolver import _normalize_slug


# ─── Sabit geçerli paket içeriği ────────────────────────────────────────────

CUMHURIYET_KEY = normalize_special_day_key("Cumhuriyet Bayramı")


def _valid_content(**overrides) -> dict:
    content = {
        "kapsam": "Kuyumculuk: altın, gümüş ve pırlanta takı perakendesi.",
        "ton_ve_dil": "Güven veren, sade; fiyat vaadi yerine ayar ve sertifika dili.",
        "cta_kaliplari": [
            {
                "kalip": "Vitrindeki modeli mağazada deneyin",
                "tur": "ziyaret",
                "gerekce": "Takı kararı fiziksel denemeye bağlı.",
            }
        ],
        "kanca_kaliplari": ["Ayar farkını gözle ayırt edebilir misiniz?"],
        "gorsel_kodlar": "Warm directional light on polished metal, shallow depth of field.",
        "video_kodlar": {
            "hareket": "Slow orbit around the display case.",
            "sahne": "Boutique interior, warm ambient light.",
        },
        "takvim_temalari": ["Söz-nişan yoğunluğu ilkbaharda artar."],
        "yasaklar_ve_hassasiyetler": [
            "Yatırım getirisi vaadi yasak (SPK mevzuatı, yürürlük 2013-06-30)."
        ],
        "ozel_gun": {
            CUMHURIYET_KEY: {
                "tur": "kutlama",
                "mesaj_ekseni": "Ortak sevinç",
                "kanca": "Bayram vitrinimiz hazır",
                "cta": "Mağazada görün",
                "gorsel_vurgu": "Red and white accents, no flag graphics",
            }
        },
    }
    content.update(overrides)
    return content


HOLIDAY_KEYS = {CUMHURIYET_KEY, normalize_special_day_key("Ramazan Bayramı")}


# ─── 1. Normalize sözleşmesi ────────────────────────────────────────────────


@pytest.mark.parametrize(
    "raw",
    [
        "Cumhuriyet Bayramı",
        "  Ramazan   Bayramı  ",
        "Şeker Bayramı",
        "Öğretmenler Günü",
        "İşçi Bayramı",
        "Çanakkale Zaferi",
        "Ulusal Egemenlik ve Çocuk Bayramı",
    ],
)
def test_normalize_key_matches_writer_and_reader(raw):
    """Anahtar kuralı `_normalize_slug` ile BİRE BİR aynı.

    İki kopya olsaydı yazım tarafı bir anahtarı doğrular, okuma tarafı başkasını
    arardı ve özel gün bloğu sessizce hiç eşleşmezdi.
    """
    assert normalize_special_day_key(raw) == _normalize_slug(raw)


@pytest.mark.parametrize("raw", ["", "   ", None, "!!!", "---"])
def test_normalize_key_rejects_empty_input(raw):
    """Boş/çözümlenemez ad anahtar ÜRETMEZ — uydurma anahtar yasak (§4.4).

    `_normalize_slug` bu girdilerde `genel` döndürür (sektör düşüş kovası). Özel
    gün tarafında aynı davranış bir sektör slug'ıyla ÇAKIŞAN sahte bir gün
    anahtarı üretirdi; burada bilinçli olarak AYRIŞIR ve reddedilir.
    """
    with pytest.raises(ValueError):
        normalize_special_day_key(raw)


# ─── 2. Yazım kapısı — `content` doğrulayıcısı ──────────────────────────────


def test_validator_accepts_reference_content():
    """Sabit geçerli içerik temiz geçer — diğer testlerin ön koşulu."""
    result = validate_package_content(
        _valid_content(), banned_brand_names=["Altınbaş"], holiday_keys=HOLIDAY_KEYS
    )
    assert result.ok, result.errors
    assert result.errors == []


def test_validator_rejects_unknown_field():
    """Kapalı küme: şemada olmayan alan REDDEDİLİR."""
    result = validate_package_content(
        _valid_content(bonus_alan="şemada yok"),
        banned_brand_names=[],
        holiday_keys=HOLIDAY_KEYS,
    )
    assert not result.ok
    assert any("bonus_alan" in e for e in result.errors)


def test_validator_rejects_missing_field():
    """Eksik alan da kapalı kümenin ihlalidir."""
    content = _valid_content()
    del content["gorsel_kodlar"]
    result = validate_package_content(
        content, banned_brand_names=[], holiday_keys=HOLIDAY_KEYS
    )
    assert not result.ok
    assert any("gorsel_kodlar" in e for e in result.errors)


def test_validator_rejects_unknown_special_day_key():
    """Takvimde karşılığı olmayan anahtar pakete GİREMEZ (K-01b yazım ayağı)."""
    content = _valid_content(
        ozel_gun={
            "uydurma-gun": {
                "tur": "kutlama",
                "mesaj_ekseni": "x",
                "kanca": "y",
                "cta": "z",
                "gorsel_vurgu": "w",
            }
        }
    )
    result = validate_package_content(
        content, banned_brand_names=[], holiday_keys=HOLIDAY_KEYS
    )
    assert not result.ok
    assert any("uydurma-gun" in e for e in result.errors)


def test_validator_accepts_icerik_onerilmez():
    """Bilinçli boşun özel temsili geçerlidir (K-120) — boş dizeden AYRI."""
    content = _valid_content(
        ozel_gun={
            CUMHURIYET_KEY: {
                "tur": "anma",
                "mesaj_ekseni": "içerik-önerilmez",
                "kanca": "içerik-önerilmez",
                "cta": "içerik-önerilmez",
                "gorsel_vurgu": "içerik-önerilmez",
            }
        }
    )
    result = validate_package_content(
        content, banned_brand_names=[], holiday_keys=HOLIDAY_KEYS
    )
    assert result.ok, result.errors


def test_validator_rejects_plain_empty_value():
    """Sıradan boş değer geçerli DEĞİL — özel temsil olmadan boş bırakılamaz."""
    result = validate_package_content(
        _valid_content(kapsam="  "), banned_brand_names=[], holiday_keys=HOLIDAY_KEYS
    )
    assert not result.ok
    assert any("kapsam" in e for e in result.errors)


def test_validator_rejects_brand_name_text():
    """Gerçek marka adı geçen metin pakete GİREMEZ (K-15 üçüncü bileşen)."""
    content = _valid_content(
        kanca_kaliplari=["Altınbaş vitrininde gördüğünüz modeli sorun"]
    )
    result = validate_package_content(
        content, banned_brand_names=["Altınbaş"], holiday_keys=HOLIDAY_KEYS
    )
    assert not result.ok
    assert any("Altınbaş" in e for e in result.errors)


def test_validator_finds_brand_name_in_nested_text():
    """Yasak ad iç içe yapıda da bulunur — yüzeysel tarama yetmez."""
    content = _valid_content(
        ozel_gun={
            CUMHURIYET_KEY: {
                "tur": "kutlama",
                "mesaj_ekseni": "Ortak sevinç",
                "kanca": "Altınbaş tarzı bir vitrin",
                "cta": "Mağazada görün",
                "gorsel_vurgu": "Red accents",
            }
        }
    )
    result = validate_package_content(
        content, banned_brand_names=["altınbaş"], holiday_keys=HOLIDAY_KEYS
    )
    assert not result.ok


def test_validator_size_warning_not_rejection():
    """~6.000 karakter tavanı UYARI üretir, RED üretmez (tasarım hedefi, kapı değil)."""
    result = validate_package_content(
        _valid_content(kapsam="uzun metin. " * 700),
        banned_brand_names=[],
        holiday_keys=HOLIDAY_KEYS,
    )
    assert result.ok, result.errors
    assert result.warnings
    assert any("6000" in w or "6.000" in w for w in result.warnings)


def test_validator_rejects_video_kodlar_without_two_substructures():
    """`video_kodlar` iki alt yapı taşır (K-02 kapısı) — adlar bağlanmaz, sayı bağlanır."""
    result = validate_package_content(
        _valid_content(video_kodlar={"hareket": "tek yapı"}),
        banned_brand_names=[],
        holiday_keys=HOLIDAY_KEYS,
    )
    assert not result.ok
    assert any("video_kodlar" in e for e in result.errors)


def test_validator_accepts_any_two_video_substructure_names():
    """K-02 AÇIK: nihai alan adları bağlanmaz, yalnız iki-alt-yapı aranır."""
    result = validate_package_content(
        _valid_content(video_kodlar={"motion": "a", "scene": "b"}),
        banned_brand_names=[],
        holiday_keys=HOLIDAY_KEYS,
    )
    assert result.ok, result.errors


# ─── 3. Çözümleyici — güvenli geri düşüş ────────────────────────────────────


async def _seed_package(db, *, status: str, version: int = 1) -> tuple[uuid.UUID, uuid.UUID, str]:
    """Kök sektör + alt sektör + paket + marka kurar."""
    root_id = await db.fetchval(
        "SELECT id FROM social.sectors WHERE slug = 'teknoloji' AND parent_sector_id IS NULL"
    )
    assert root_id is not None, "kök seed eksik"
    sub_slug = f"alt-{uuid.uuid4().hex[:8]}"
    sub_id = await db.fetchval(
        """
        INSERT INTO social.sectors (slug, display_name, parent_sector_id)
        VALUES ($1, $2, $3) RETURNING id
        """,
        sub_slug,
        "Alt Sektör",
        root_id,
    )
    package_id = await db.fetchval(
        """
        INSERT INTO social.sector_packages
            (sector_id, version, status, schema_version, content)
        VALUES ($1, $2, $3, 1, $4)
        RETURNING id
        """,
        sub_id,
        version,
        status,
        # asyncpg jsonb codec AÇIK: dict doğrudan geçilir. `json.dumps` + `::jsonb`
        # burada ÇİFT KODLAMA yapar (değer JSON *dizesi* olarak yazılır) — proje
        # konvansiyonu bunu açıkça yasaklıyor.
        _valid_content(),
    )
    return sub_id, package_id, sub_slug


@pytest.fixture
async def pkg_db(db):
    """Üretimin KENDİ bağlantı yapılandırması (jsonb codec) uygulanmış bağlantı."""
    from app.core.database import _init_connection

    await _init_connection(db)
    return db


async def test_resolver_returns_none_without_assignment(pkg_db, caplog):
    """Atama yoksa paket yolu HİÇ açılmaz — sorgu da log da yok."""
    with caplog.at_level(logging.WARNING):
        result = await resolve_package_context(pkg_db, {"id": uuid.uuid4(), "sub_sector_id": None})
    assert result is None
    assert caplog.records == [], "atamasız marka normal yoldur, uyarı üretmez"


async def test_resolver_returns_context_for_active(pkg_db):
    """Aktif paket okunur; bağlam dört alanını taşır."""
    sub_id, package_id, sub_slug = await _seed_package(pkg_db, status="active", version=3)

    result = await resolve_package_context(pkg_db, {"id": uuid.uuid4(), "sub_sector_id": sub_id})

    assert isinstance(result, SectorPackageContext)
    assert result.package_id == package_id
    assert result.version == 3
    assert result.sub_sector_slug == sub_slug
    assert result.content["kapsam"].startswith("Kuyumculuk")


@pytest.mark.parametrize("status", ["draft", "archived"])
async def test_resolver_none_for_non_active_with_stale_log(pkg_db, caplog, status):
    """`draft`/`archived` çalışma zamanında HİÇ okunmaz — bayat atama loglanır."""
    sub_id, _, _ = await _seed_package(pkg_db, status=status)

    with caplog.at_level(logging.WARNING):
        result = await resolve_package_context(pkg_db, {"id": uuid.uuid4(), "sub_sector_id": sub_id})

    assert result is None
    assert any(str(sub_id) in r.getMessage() for r in caplog.records), (
        "bayat/eksik atama gözlemlenebilir log ÜRETMELİ"
    )


async def test_resolver_swallows_db_error_returns_none(pkg_db, caplog):
    """Sorgu hatası üretimi BLOKLAMAZ — None + log."""

    class _BoomConnection:
        async def fetchrow(self, *_args, **_kwargs):
            raise RuntimeError("bağlantı düştü")

    with caplog.at_level(logging.WARNING):
        result = await resolve_package_context(
            _BoomConnection(), {"id": uuid.uuid4(), "sub_sector_id": uuid.uuid4()}
        )

    assert result is None
    assert caplog.records, "yutulan istisna sessiz kalmaz"


async def test_resolver_none_for_broken_content(pkg_db, caplog):
    """Bozuk `content` (nesne değil) güvenli geri düşüş üretir."""
    sub_id, _, _ = await _seed_package(pkg_db, status="active")
    await pkg_db.execute(
        "UPDATE social.sector_packages SET content = $2 WHERE sector_id = $1",
        sub_id,
        ["liste", "nesne değil"],
    )

    with caplog.at_level(logging.WARNING):
        result = await resolve_package_context(pkg_db, {"id": uuid.uuid4(), "sub_sector_id": sub_id})

    assert result is None
    # Sebep de pinlenir: bu test bir kez ÇİFT KODLAMA yüzünden (`content` bir JSON
    # dizesiydi) yanlış sebeple yeşil kalmıştı. Log tipin `list` olduğunu söylemeli.
    assert any("list" in r.getMessage() for r in caplog.records), (
        "bozukluk sebebi beklenen değil — test yanlış sebeple yeşil olabilir"
    )


# ─── Şema dallarının kalan kapıları ─────────────────────────────────────────
#
# Aşağıdakiler mutasyon taramasında koruması OLMAYAN dallardı: kapıyı silmek
# hiçbir testi kırmıyordu. Test edilmeyen kapı, olmayan kapıdır.


def test_validator_rejects_cta_item_missing_fields():
    """`cta_kaliplari` öğesi {kalip, tur, gerekce} taşımalı (spec §3.4)."""
    result = validate_package_content(
        _valid_content(cta_kaliplari=[{"kalip": "Mağazada görün"}]),
        banned_brand_names=[],
        holiday_keys=HOLIDAY_KEYS,
    )
    assert not result.ok
    assert any("cta_kaliplari[0]" in e for e in result.errors)


def test_validator_rejects_wrong_field_types():
    """Metin alanına dizi, dizi alanına metin geçirilemez."""
    result = validate_package_content(
        _valid_content(kapsam=["metin değil"], kanca_kaliplari="dizi değil"),
        banned_brand_names=[],
        holiday_keys=HOLIDAY_KEYS,
    )
    assert not result.ok
    assert any("kapsam metin değil" in e for e in result.errors)
    assert any("kanca_kaliplari dizi değil" in e for e in result.errors)


def test_validator_rejects_non_dict_ozel_gun():
    """`ozel_gun` nesne değilse anahtar doğrulaması hiç koşamaz — reddedilir."""
    result = validate_package_content(
        _valid_content(ozel_gun=["liste"]),
        banned_brand_names=[],
        holiday_keys=HOLIDAY_KEYS,
    )
    assert not result.ok
    assert any("ozel_gun nesne değil" in e for e in result.errors)


def test_validator_rejects_non_dict_content():
    """`content` hiç nesne değilse tek hatayla durulur."""
    result = validate_package_content(
        ["nesne değil"], banned_brand_names=[], holiday_keys=HOLIDAY_KEYS
    )
    assert not result.ok
    assert result.errors == ["content nesne değil: list"]


def test_validator_rejects_empty_video_substructure():
    """İki alt yapı VAR ama biri boş — sayı doğru, içerik değil."""
    result = validate_package_content(
        _valid_content(video_kodlar={"hareket": "a", "sahne": "  "}),
        banned_brand_names=[],
        holiday_keys=HOLIDAY_KEYS,
    )
    assert not result.ok
    assert any("video_kodlar alt yapılarından biri boş" in e for e in result.errors)


def test_validator_rejects_special_day_missing_slot():
    """Özel gün girdisinin eksik alanı yakalanır."""
    content = _valid_content(
        ozel_gun={CUMHURIYET_KEY: {"tur": "kutlama", "mesaj_ekseni": "x"}}
    )
    result = validate_package_content(
        content, banned_brand_names=[], holiday_keys=HOLIDAY_KEYS
    )
    assert not result.ok
    assert any("eksik alan: kanca" in e for e in result.errors)
