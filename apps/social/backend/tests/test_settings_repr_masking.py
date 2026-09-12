"""`Settings` temsilinin sır maskelemesi — 2026-09-12 güvenlik review'ı (S-8).

Bulgu ÖLÇÜMLE doğdu: güvenlik düzeltmeleri sırasında bir `monkeypatch.setattr`
hatası, pydantic'in varsayılan `repr`'i üzerinden AYAR NESNESİNİN TAMAMINI hata
metnine bastı — veritabanı parolası, Supabase servis anahtarı, fal.ai, R2,
Upload-Post, ElevenLabs, HeyGen, Apify, YouTube, Serper ve dâhilî API anahtarı
dâhil. Aynı yol her yığın izinde, her `print(settings)`'te ve hata izlemeye
(Sentry) giden her çerçeve yerelinde açıktır.

Kapı SINIF düzeyindedir: alan adından türetilir, elle seçilmiş liste değildir —
yarın eklenen `YENI_API_KEY` de kendiliğinden maskelenir.
"""

from __future__ import annotations

from app.core.config import Settings


def _sirli_ayarlar() -> Settings:
    return Settings(
        DATABASE_URL="postgresql://kullanici:SUPER-GIZLI-PAROLA@127.0.0.1:5432/db",
        FAL_KEY="fal-GIZLI-ANAHTAR",
        R2_SECRET_ACCESS_KEY="r2-GIZLI-ANAHTAR",
        INTERNAL_API_KEY="internal-GIZLI",
        N8N_CRM_EVENT_SECRET="crm-GIZLI",
        APP_URL="https://app.otomaix.com",
    )


def test_repr_masks_every_secret_bearing_field():
    """Sır taşıyan HİÇBİR alanın değeri temsile girmez — üretilmiş matris."""
    ayarlar = _sirli_ayarlar()
    metin = repr(ayarlar) + str(ayarlar)

    sizanlar = [
        deger
        for deger in (
            "SUPER-GIZLI-PAROLA",
            "fal-GIZLI-ANAHTAR",
            "r2-GIZLI-ANAHTAR",
            "internal-GIZLI",
            "crm-GIZLI",
        )
        if deger in metin
    ]
    assert not sizanlar, (
        f"ayar temsili sır DEĞERİ taşıyor ({len(sizanlar)} alan) — her yığın izi, "
        "her test hatası ve hata izleme kaydı bu değerleri kopyalar"
    )


def test_repr_still_shows_field_names_and_public_values():
    """Maskeleme teşhisi ÖLDÜRMEZ: alan adları ve sırsız değerler görünür kalır."""
    metin = repr(_sirli_ayarlar())

    assert "DATABASE_URL" in metin, "alan adı da kayboldu — teşhis imkânsızlaşır"
    assert "https://app.otomaix.com" in metin, "sırsız değer gereksiz yere maskelendi"


def test_masking_is_derived_from_the_field_name_not_a_hand_list():
    """Yeni eklenen sır alanı kendiliğinden maskelenir — liste bakımı gerekmez."""
    from app.core.config import _sir_alani_mi

    for ad in ("YENI_API_KEY", "X_SECRET", "SOME_TOKEN", "DB_PASSWORD", "DATABASE_URL"):
        assert _sir_alani_mi(ad), ad
    for ad in ("APP_URL", "ENVIRONMENT", "IMAGE_MODEL", "N8N_BASE_URL"):
        assert not _sir_alani_mi(ad), ad
