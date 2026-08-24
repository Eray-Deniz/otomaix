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
            "hareket": [
                "Slow orbit around the display case.",
                "Gentle push-in on the ring tray.",
            ],
            "sahne": [
                "Boutique interior, warm ambient light.",
                "Velvet display surface, directional key light.",
            ],
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
    """`video_kodlar` İKİ havuz taşır: `hareket` ve `sahne` (K-02 = A ile bağlandı)."""
    result = validate_package_content(
        _valid_content(video_kodlar={"hareket": ["tek havuz"]}),
        banned_brand_names=[],
        holiday_keys=HOLIDAY_KEYS,
    )
    assert not result.ok
    assert any("video_kodlar" in e for e in result.errors)


def test_validator_rejects_unbound_video_substructure_names():
    """K-02 = A: adlar artık BAĞLI. Serbest ad kabul edilmez.

    K-02 açıkken kapı "herhangi iki ad" kabul ediyordu; karar kapandığı için
    (2026-08-24) sözleşme adlıdır. Serbest ad kabul edilseydi yazan taraf
    `motion`/`scene` yazar, okuyan taraf `hareket`/`sahne` arar ve havuz
    sessizce hiç bulunamazdı.
    """
    result = validate_package_content(
        _valid_content(video_kodlar={"motion": ["a"], "scene": ["b"]}),
        banned_brand_names=[],
        holiday_keys=HOLIDAY_KEYS,
    )
    assert not result.ok
    assert any("video_kodlar" in e for e in result.errors)


def test_validator_accepts_multi_entry_pools():
    """Havuzlar ÇOĞULDUR — alternatifsiz paket meşru ama tekil olmak zorunda değil."""
    result = validate_package_content(
        _valid_content(
            video_kodlar={"hareket": ["a", "b", "c"], "sahne": ["d", "e"]}
        ),
        banned_brand_names=[],
        holiday_keys=HOLIDAY_KEYS,
    )
    assert result.ok, result.errors


def test_validator_rejects_video_substructure_that_is_not_a_list():
    """Tek cümle artık geçmez — havuzun şekli listedir (spec §3.4 notu).

    Tekil cümle, sektöre özel olsa bile o sektörün her videosunu aynı tipte
    üretirdi; çoğulluk alanın işlevinin parçasıdır.
    """
    result = validate_package_content(
        _valid_content(video_kodlar={"hareket": "tek cümle", "sahne": ["b"]}),
        banned_brand_names=[],
        holiday_keys=HOLIDAY_KEYS,
    )
    assert not result.ok
    assert any("video_kodlar" in e for e in result.errors)


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
    # Mesaj da pinlenir: bu dal kapatılsa akış yine `None` döner (satır erişimi
    # istisna atar, genel emniyet ağı yakalar) — sonuç aynı, TEŞHİS kaybolurdu.
    # "Bayat atama" ile "sorgu patladı" işletimde farklı iki olaydır.
    assert any(
        "AKTİF paketi yok" in r.getMessage() and str(sub_id) in r.getMessage()
        for r in caplog.records
    ), "bayat/eksik atama kendi mesajıyla loglanmalı"


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


@pytest.mark.parametrize("bad_pool", [[], ["  "], ["a", ""]])
def test_validator_rejects_empty_video_substructure(bad_pool):
    """İki havuz VAR ama biri boş — sayı doğru, içerik değil.

    Boş havuz yazımda REDDEDİLİR. Çalışma zamanındaki boş-havuz dalı (K-113 = A,
    mevcut listeye düşüş) bundan AYRI bir şeydir: o, paket okunduktan sonra
    havuzun kullanılamaz çıkması hâlidir.
    """
    result = validate_package_content(
        _valid_content(video_kodlar={"hareket": bad_pool, "sahne": ["b"]}),
        banned_brand_names=[],
        holiday_keys=HOLIDAY_KEYS,
    )
    assert not result.ok
    assert any("video_kodlar" in e for e in result.errors)


def test_validator_rejects_special_day_missing_slot():
    """Özel gün girdisinin eksik alanı yakalanır."""
    content = _valid_content(
        ozel_gun={CUMHURIYET_KEY: {"tur": "kutlama", "mesaj_ekseni": "x"}}
    )
    result = validate_package_content(
        content, banned_brand_names=[], holiday_keys=HOLIDAY_KEYS
    )
    assert not result.ok
    # Anahtar kümesi TAM olmalı: eksik alan da fazlalık da aynı kapıdan döner.
    assert any("anahtar kümesi" in e for e in result.errors)


# ─── Checkpoint 8 bulguları ─────────────────────────────────────────────────
#
# Üç yüksek bulgu: (1) yazım kapısı yaprak düzeyinde denetlemiyordu, kap tipine
# bakıp geçiyordu; (2) çözümleyici her sözlüğü geçerli sayıyordu — boş sözlük
# dâhil; (3) marka adı taraması Türkçe büyük/küçük harfe ve sözcük sınırına
# duyarsızdı. Bir orta bulgu: mutasyon iddiası yardımcı-fonksiyon düzeyindeydi,
# dal düzeyinde değil — üç dalın bekçisi yoktu.


def _reject(**overrides) -> list[str]:
    result = validate_package_content(
        _valid_content(**overrides), banned_brand_names=[], holiday_keys=HOLIDAY_KEYS
    )
    assert not result.ok, "bozuk içerik KABUL edildi"
    return result.errors


# (1) Yaprak şeması


def test_validator_rejects_cta_item_with_extra_key():
    """`cta_kaliplari` öğesinin anahtar kümesi TAM — fazlası şema dışıdır."""
    _reject(cta_kaliplari=[{"kalip": "a", "tur": "b", "gerekce": "c", "fazla": 1}])


@pytest.mark.parametrize("bad", [None, 5, True, {"ic": "ice"}, ["dizi"]])
def test_validator_rejects_non_text_cta_value(bad):
    """CTA değerleri metin olmak zorunda — `None`/sayı/mantıksal geçmez."""
    _reject(cta_kaliplari=[{"kalip": bad, "tur": "b", "gerekce": "c"}])


@pytest.mark.parametrize("bad", ["   ", None, 0, False, {}, []])
def test_validator_rejects_bad_list_member(bad):
    """Dizi üyeleri dolu METİN olmalı — boşluk, `None`, sayı, boş yapı geçmez."""
    _reject(kanca_kaliplari=[bad])


def test_validator_rejects_empty_list_field():
    """Boş dizi alanı reddedilir (mutasyon taramasında bekçisi YOKTU)."""
    errors = _reject(kanca_kaliplari=[])
    assert any("kanca_kaliplari" in e for e in errors)


@pytest.mark.parametrize("bad", [False, 0, None, {"ic": "ice"}, "tek cümle"])
def test_validator_rejects_non_list_video_substructure(bad):
    """Havuz LİSTE olmalı — `False`/`0`/sözlük/tek cümle havuz değildir."""
    _reject(video_kodlar={"hareket": bad, "sahne": ["b"]})


@pytest.mark.parametrize("bad", [False, 0, None, {"ic": "ice"}, ["ic"]])
def test_validator_rejects_non_text_pool_entry(bad):
    """Havuzun ÖĞELERİ dolu metin olmalı — kap doğru olsa da yaprak denetlenir."""
    _reject(video_kodlar={"hareket": [bad], "sahne": ["b"]})


def test_validator_rejects_unknown_special_day_slot():
    """Özel gün girdisinin anahtar kümesi de TAM."""
    entry = {s: "x" for s in ("tur", "mesaj_ekseni", "kanca", "cta", "gorsel_vurgu")}
    entry["fazla"] = "şema dışı"
    _reject(ozel_gun={CUMHURIYET_KEY: entry})


@pytest.mark.parametrize("bad", ["   ", None, 5, False])
def test_validator_rejects_bad_special_day_slot_value(bad):
    """Boş/metin-olmayan özel gün alanı (mutasyon taramasında bekçisi YOKTU)."""
    entry = {s: "x" for s in ("tur", "mesaj_ekseni", "kanca", "cta", "gorsel_vurgu")}
    entry["kanca"] = bad
    _reject(ozel_gun={CUMHURIYET_KEY: entry})


# (3) Marka adı — Türkçe harf ve sözcük sınırı


@pytest.mark.parametrize(
    "banned,text",
    [
        ("Altınbaş", "ALTINBAŞ VİTRİNİ hazır"),   # büyük harf: casefold ı≠i tuzağı
        ("IŞIK", "ışık tonu yumuşak"),            # I → ı
        ("İNCİ", "inci dokusu"),                  # İ → i
        ("Altınbaş", "Altınbaşlar için özel"),    # Türkçe ek: sağ sınır serbest
        ("Altınbaş", "Altınbaş'tan seçmeler"),    # kesme işareti
    ],
)
def test_validator_catches_brand_name_across_turkish_casing(banned, text):
    """Marka adı Türkçe harf dönüşümleri ve eklerle GİZLENEMEZ."""
    result = validate_package_content(
        _valid_content(kanca_kaliplari=[text]),
        banned_brand_names=[banned],
        holiday_keys=HOLIDAY_KEYS,
    )
    assert not result.ok, f"{banned!r} adı {text!r} içinde kaçtı"


def test_validator_does_not_reject_ordinary_word_containing_brand_name():
    """Kısa marka adı sıradan sözcüğün İÇİNDE eşleşmez — sol sınır aranır.

    "Ada" adı "mağazada" içinde geçer ama sol sınırda değil. Sol sınırda geçseydi
    (ör. "adaya") bilinçli olarak YAKALANIRDI — bkz. `_check_banned_brand_names`
    belgesindeki asimetri.
    """
    result = validate_package_content(
        _valid_content(kanca_kaliplari=["Mağazada deneyin"]),
        banned_brand_names=["Ada"],
        holiday_keys=HOLIDAY_KEYS,
    )
    assert result.ok, result.errors


def test_validator_catches_brand_name_in_dict_key():
    """Yasak ad yalnız bir ANAHTARDA geçse de yakalanır (bekçisi YOKTU)."""
    entry = {s: "x" for s in ("tur", "mesaj_ekseni", "kanca", "cta", "gorsel_vurgu")}
    result = validate_package_content(
        _valid_content(ozel_gun={CUMHURIYET_KEY: entry}),
        banned_brand_names=[CUMHURIYET_KEY.split("-")[0]],
        holiday_keys=HOLIDAY_KEYS,
    )
    assert not result.ok


# (2) Çözümleyici — yapısal geçerlilik


@pytest.mark.parametrize("broken", [{}, {"kapsam": "yalnız bir alan"}])
async def test_resolver_falls_back_for_structurally_invalid_content(
    pkg_db, caplog, broken
):
    """Sözlük OLMASI yetmez — yapısal olarak bozuk paket de mevcut yola düşer.

    K-15(a) (alan-düzeyi atlama) bilinçli olarak YOK; sözleşme tüm yolun
    düşmesini istiyor. Boş sözlüğü geçirmek, hatayı Task 10'un render'ına
    taşırdı.
    """
    sub_id, _, _ = await _seed_package(pkg_db, status="active")
    await pkg_db.execute(
        "UPDATE social.sector_packages SET content = $2 WHERE sector_id = $1",
        sub_id,
        broken,
    )

    with caplog.at_level(logging.WARNING):
        result = await resolve_package_context(
            pkg_db, {"id": uuid.uuid4(), "sub_sector_id": sub_id}
        )

    assert result is None
    assert caplog.records


async def test_resolver_survives_malformed_row(caplog):
    """Satır çözümlemesi de emniyet sınırının İÇİNDE — istisna kaçmaz."""

    class _HostileRow:
        def __getitem__(self, _key):
            raise RuntimeError("satır çözümlenemedi")

    class _HostileConnection:
        async def fetchrow(self, *_args, **_kwargs):
            return _HostileRow()

    with caplog.at_level(logging.WARNING):
        result = await resolve_package_context(
            _HostileConnection(), {"id": uuid.uuid4(), "sub_sector_id": uuid.uuid4()}
        )

    assert result is None
    assert caplog.records


# ─── Checkpoint 8, tur 2 ────────────────────────────────────────────────────
#
# F3 kapanmamıştı: Türkçe→ASCII tablosu Unicode'u NORMALİZE etmiyordu, yani
# ayrışık (NFD) yazılmış bir ad hâlâ kaçıyordu. Aynı sınıf özel gün anahtarında
# da ölçüldü. F4: CTA sentinel dalının bekçisi yoktu. F5: bağlam kurulumu emniyet
# sınırının DIŞINDAYDI — önceki commit mesajı bunu yanlış anlatıyordu.

import unicodedata  # noqa: E402

from app.services.sector_packages import DELIBERATELY_EMPTY  # noqa: E402


@pytest.mark.parametrize("brand", ["Şeker", "İnci", "Çağrı", "Altınbaş"])
def test_validator_catches_brand_name_in_decomposed_unicode(brand):
    """Ayrışık (NFD) yazılmış ad da yakalanır — iki yazım aynı adı taşır."""
    decomposed = unicodedata.normalize("NFD", brand)
    assert decomposed != brand or unicodedata.normalize("NFC", decomposed) == brand
    result = validate_package_content(
        _valid_content(kanca_kaliplari=[f"{decomposed} dükkanı"]),
        banned_brand_names=[brand],
        holiday_keys=HOLIDAY_KEYS,
    )
    assert not result.ok, f"{brand!r} ayrışık biçimde kaçtı"


@pytest.mark.parametrize("brand", ["Şeker", "İnci"])
def test_validator_catches_decomposed_banned_name_against_composed_text(brand):
    """Ters yön: YASAK ad ayrışık, metin birleşik yazılmış."""
    result = validate_package_content(
        _valid_content(kanca_kaliplari=[f"{brand} dükkanı"]),
        banned_brand_names=[unicodedata.normalize("NFD", brand)],
        holiday_keys=HOLIDAY_KEYS,
    )
    assert not result.ok


@pytest.mark.parametrize("name", ["Şeker Bayramı", "Çanakkale Zaferi", "İşçi Bayramı"])
def test_normalize_key_is_unicode_form_independent(name):
    """Aynı gün adının iki Unicode yazımı AYNI anahtarı verir.

    Yazım tarafı birleşik, okuma tarafı ayrışık biçim görürse anahtar tutmaz ve
    özel gün bloğu sessizce hiç eşleşmez — K-01b'nin tek-modül kuralının
    önlemek için var olduğu şey tam olarak budur.
    """
    assert normalize_special_day_key(name) == normalize_special_day_key(
        unicodedata.normalize("NFD", name)
    )


def test_validator_accepts_sentinel_cta_item():
    """Tüm CTA listesi bilinçli boş olabilir (K-120) — dalın bekçisi budur."""
    result = validate_package_content(
        _valid_content(cta_kaliplari=[DELIBERATELY_EMPTY]),
        banned_brand_names=[],
        holiday_keys=HOLIDAY_KEYS,
    )
    assert result.ok, result.errors


async def test_resolver_survives_context_construction_error(pkg_db, caplog, monkeypatch):
    """Bağlam kurulumu da emniyet sınırının İÇİNDE.

    Bugünkü dataclass kurucusu önemsiz, ama sözleşme "çözümleyicinin hiçbir
    hatası üretimi bloklamaz" diyor — kurucuya bir doğrulama eklendiği gün bu
    kapı olmasaydı istisna üretim akışına kaçardı.
    """
    import app.services.sector_packages as module

    sub_id, _, _ = await _seed_package(pkg_db, status="active")

    def _boom(*_args, **_kwargs):
        raise RuntimeError("kurucu patladı")

    monkeypatch.setattr(module, "SectorPackageContext", _boom)

    with caplog.at_level(logging.WARNING):
        result = await resolve_package_context(
            pkg_db, {"id": uuid.uuid4(), "sub_sector_id": sub_id}
        )

    assert result is None
    assert caplog.records


# ─── Checkpoint 8, tur 3 — sınıfı kapatma ───────────────────────────────────
#
# F3 üç turdur açık: her tur aynı eksenin daha dar bir varyantını buldu (Türkçe
# büyük harf → ayrışık NFD → `İ`.lower()'ın ürettiği i+U+0307). Varyant yamalamak
# yakınsamıyor. Buradaki test tek tek biçimleri değil, bir adın ÜRETİLEBİLİR TÜM
# yazımlarını sınar: kanıt elle seçilmiş örnek değil, matristir.

TURKISH_BRAND_SAMPLES = ["İnci", "Şeker", "Çağrı", "Altınbaş", "Gümüş", "Işık"]


def _representations(name: str) -> list[str]:
    """Bir adın pratikte karşılaşılabilir tüm yazımları.

    Büyük/küçük harf işlemleri birleşen işaret ÜRETİR (`"İ".lower()` →
    `i`+U+0307), normalizasyon biçimleri de ayrı yazımlar doğurur. İkisinin
    çarpımı, metnin gerçekte gelebileceği biçim uzayıdır.
    """
    forms = {name, name.lower(), name.upper(), name.casefold(), name.title()}
    for form in list(forms):
        for norm in ("NFC", "NFD", "NFKC", "NFKD"):
            forms.add(unicodedata.normalize(norm, form))
    return sorted(forms)


@pytest.mark.parametrize("brand", TURKISH_BRAND_SAMPLES)
def test_brand_name_matching_is_representation_closed(brand):
    """Adın HER yazımı, yasak listesinin HER yazımına karşı yakalanır.

    Tek yönlü değil: yasak ad da içerik de farklı biçimde gelebilir, o yüzden
    biçim uzayının tam çarpımı sınanır.
    """
    forms = _representations(brand)
    escapes = []
    for banned in forms:
        for text in forms:
            result = validate_package_content(
                _valid_content(kanca_kaliplari=[f"{text} dükkanı"]),
                banned_brand_names=[banned],
                holiday_keys=HOLIDAY_KEYS,
            )
            if result.ok:
                escapes.append((banned, text))

    assert not escapes, (
        f"{brand!r} için {len(escapes)}/{len(forms) ** 2} yazım çifti KAÇTI: "
        f"{escapes[:5]}"
    )


@pytest.mark.parametrize("name", ["Şeker Bayramı", "İşçi Bayramı", "Çanakkale Zaferi"])
def test_special_day_key_is_representation_closed(name):
    """Gün adının her yazımı AYNI anahtarı verir — yazım/okuma ayrışamaz."""
    keys = {normalize_special_day_key(form) for form in _representations(name)}
    assert len(keys) == 1, f"{name!r} için {len(keys)} farklı anahtar üretildi: {keys}"
