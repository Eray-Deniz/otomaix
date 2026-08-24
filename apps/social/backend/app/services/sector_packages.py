"""Sektör bilgi paketi erişim katmanı (plan Task 8).

Üç sorumluluk, üç ayrı sözleşme:

1. `normalize_special_day_key` — özel gün anahtarının TEK kaynağı (K-01b,
   spec §4.4). Yazım tarafı (aşağıdaki doğrulayıcı) ve okuma tarafı (çalışma
   zamanı gün eşleşmesi) bu fonksiyonu import eder. İkinci bir kopya yazılırsa
   yazım bir anahtarı doğrular, okuma başkasını arar ve özel gün bloğu sessizce
   hiç eşleşmez — bu yüzden kural tek yerde yaşar.
2. `validate_package_content` — DB yazımından ÖNCEKİ kapı (spec §3.4 / §8.3b).
   Reddederse yazım olmaz.
3. `resolve_package_context` — çalışma zamanı okuması (spec §4.2). Buradaki
   HİÇBİR hata üretimi bloklamaz: her başarısızlık `None` + gözlemlenebilir log
   demektir, yani marka paketsiz yola düşer.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from app.services.sector_resolver import _normalize_slug

logger = logging.getLogger(__name__)


# ─── 1. Özel gün anahtarı (K-01b) ───────────────────────────────────────────

# `_normalize_slug`'ın Türkçe harf tablosuyla AYNI küme. Burada yalnız "bu ad
# normalize edildikten sonra geriye harf/rakam kalıyor mu" sorusuna bakılır.
_TR_ASCII = str.maketrans(
    {
        "ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u",
        "Ç": "c", "Ğ": "g", "İ": "i", "Ö": "o", "Ş": "s", "Ü": "u",
    }
)


def normalize_special_day_key(name: str | None) -> str:
    """Sistem takvimi gün adını (`social.public_holidays.name_tr`) anahtara çevirir.

    Kural seti `sector_resolver._normalize_slug` ile BİRE BİR aynıdır ve testle
    eşitlenir — sektör slug'ı ile özel gün anahtarı aynı dünyayı adresler.

    TEK bilinçli ayrım: `_normalize_slug` çözümlenemeyen girdide `genel` döndürür
    (sektör düşüş kovası). Burada aynı davranış, bir sektör slug'ıyla ÇAKIŞAN
    sahte bir gün anahtarı üretirdi ve "sistemde karşılığı olmayan dönem pakete
    giremez" hükmünü (§4.4) sessizce delerdi. Bu yüzden çözümlenemeyen ad anahtar
    ÜRETMEZ, `ValueError` fırlatır.
    """
    if name is None or not str(name).strip():
        raise ValueError("özel gün adı boş — anahtar üretilemez (uydurma anahtar yasak)")
    if not _has_slug_content(str(name)):
        raise ValueError(
            f"özel gün adı çözümlenemedi: {name!r} — normalize sonrası harf/rakam kalmıyor"
        )
    return _normalize_slug(name)


def _has_slug_content(name: str) -> bool:
    """Ad, normalize edildikten sonra gerçekten harf/rakam taşıyor mu."""
    return bool(re.sub(r"[^a-z0-9]+", "", name.strip().lower().translate(_TR_ASCII)))


# ─── 2. Yazım kapısı — `content` doğrulayıcısı ──────────────────────────────

# Spec §3.4 kapalı kümesi: sekiz temel alan + `ozel_gun`. Şema değişimi
# `schema_version` ile taşınır, bu küme sessizce genişletilmez.
TEXT_FIELDS = ("kapsam", "ton_ve_dil", "gorsel_kodlar")
LIST_FIELDS = (
    "cta_kaliplari",
    "kanca_kaliplari",
    "takvim_temalari",
    "yasaklar_ve_hassasiyetler",
)
CONTENT_FIELDS = frozenset(TEXT_FIELDS + LIST_FIELDS + ("video_kodlar", "ozel_gun"))

# K-120: boş alanın RESMÎ temsili. Sıradan boş dizeden ayrıdır — "bilinçli boş"
# ile "doldurulmamış" aynı şey olsaydı eksik iş dolu görünürdü.
DELIBERATELY_EMPTY = "içerik-önerilmez"

# Tasarım hedefi, KAPI DEĞİL (spec §3.4 + İlke 9: ölçülmemiş sayı kapı olamaz).
SIZE_TARGET_CHARS = 6000

# K-02 AÇIK: hareket ve sahne kodlarının nihai alan ADLARI bağlanmamıştır.
# Bağlanan tek şey, iki AYRI alt yapının varlığıdır — ikisi iki ayrı yüzeye gider.
VIDEO_SUBSTRUCTURE_COUNT = 2

# `ozel_gun` girdisinin taşıdığı alanlar (spec §3.4 tablosu).
SPECIAL_DAY_SLOTS = ("tur", "mesaj_ekseni", "kanca", "cta", "gorsel_vurgu")


@dataclass
class ValidationResult:
    """Yazım kapısının sonucu. `ok=False` ise DB yazımı YAPILMAZ."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_package_content(
    content: dict,
    *,
    banned_brand_names: list[str],
    holiday_keys: set[str],
) -> ValidationResult:
    """Paket içeriğini DB yazımından ÖNCE denetler (spec §3.4).

    `holiday_keys` sistem takviminden türetilmiş NORMALİZE anahtar kümesidir —
    çağıran onu `normalize_special_day_key` ile üretir (K-01b yazım ayağı).
    """
    result = ValidationResult()

    if not isinstance(content, dict):
        result.errors.append(f"content nesne değil: {type(content).__name__}")
        return result

    _check_closed_field_set(content, result)
    _check_field_shapes(content, result)
    _check_special_days(content.get("ozel_gun"), holiday_keys, result)
    _check_banned_brand_names(content, banned_brand_names, result)
    _check_size_target(content, result)

    return result


def _check_closed_field_set(content: dict, result: ValidationResult) -> None:
    unknown = sorted(set(content) - CONTENT_FIELDS)
    if unknown:
        result.errors.append(
            f"şema dışı alan(lar): {unknown} — alan kümesi kapalıdır, "
            "genişletme `schema_version` ile taşınır"
        )
    missing = sorted(CONTENT_FIELDS - set(content))
    if missing:
        result.errors.append(f"eksik alan(lar): {missing}")


def _check_field_shapes(content: dict, result: ValidationResult) -> None:
    for name in TEXT_FIELDS:
        if name not in content:
            continue
        value = content[name]
        if not isinstance(value, str):
            result.errors.append(f"{name} metin değil: {type(value).__name__}")
        elif not _is_filled(value):
            result.errors.append(
                f"{name} boş — bilinçli boş bırakılacaksa {DELIBERATELY_EMPTY!r} yazılır"
            )

    for name in LIST_FIELDS:
        if name not in content:
            continue
        value = content[name]
        if not isinstance(value, list):
            result.errors.append(f"{name} dizi değil: {type(value).__name__}")
        elif not _is_filled(value):
            result.errors.append(
                f"{name} boş — bilinçli boş bırakılacaksa {DELIBERATELY_EMPTY!r} yazılır"
            )

    cta = content.get("cta_kaliplari")
    if isinstance(cta, list):
        for index, item in enumerate(cta):
            if item == DELIBERATELY_EMPTY:
                continue
            if not isinstance(item, dict) or not {"kalip", "tur", "gerekce"} <= set(item):
                result.errors.append(
                    f"cta_kaliplari[{index}] {{kalip, tur, gerekce}} taşımıyor"
                )

    if "video_kodlar" in content:
        video = content["video_kodlar"]
        if not isinstance(video, dict) or len(video) != VIDEO_SUBSTRUCTURE_COUNT:
            result.errors.append(
                f"video_kodlar {VIDEO_SUBSTRUCTURE_COUNT} alt yapı taşımalı "
                "(hareket ve sahne ayrı; alan adları K-02 ile bağlanacak)"
            )
        elif not all(_is_filled(v) for v in video.values()):
            result.errors.append("video_kodlar alt yapılarından biri boş")

    if "ozel_gun" in content and not isinstance(content["ozel_gun"], dict):
        result.errors.append(
            f"ozel_gun nesne değil: {type(content['ozel_gun']).__name__}"
        )


def _is_filled(value: Any) -> bool:
    """Değer dolu mu — `içerik-önerilmez` DOLU sayılır (K-120)."""
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return len(value) > 0
    return value is not None


def _check_special_days(
    ozel_gun: Any, holiday_keys: set[str], result: ValidationResult
) -> None:
    """Anahtarlar sistem takvimine karşı doğrulanır — uydurma anahtar yasak."""
    if not isinstance(ozel_gun, dict):
        return
    for key, entry in ozel_gun.items():
        if key not in holiday_keys:
            result.errors.append(
                f"özel gün anahtarı sistem takviminde YOK: {key!r} — "
                "karşılıksız dönem pakete giremez (spec §4.4)"
            )
        if not isinstance(entry, dict):
            result.errors.append(f"ozel_gun[{key!r}] nesne değil")
            continue
        for slot in SPECIAL_DAY_SLOTS:
            if slot not in entry:
                result.errors.append(f"ozel_gun[{key!r}] eksik alan: {slot}")
            elif not _is_filled(entry[slot]):
                result.errors.append(
                    f"ozel_gun[{key!r}].{slot} boş — bilinçli boş için "
                    f"{DELIBERATELY_EMPTY!r} yazılır"
                )


def _check_banned_brand_names(
    content: dict, banned_brand_names: list[str], result: ValidationResult
) -> None:
    """Gerçek marka/firma adı geçen metin pakete GİREMEZ (K-15 üçüncü bileşen).

    Tarama İÇ İÇE yapılar dâhil tüm metinlerde koşar: yasak ad `ozel_gun`
    içindeki bir kancada da geçse kural aynıdır.
    """
    names = [n.strip() for n in banned_brand_names if n and n.strip()]
    if not names:
        return
    haystack = "\n".join(_walk_strings(content)).casefold()
    for name in names:
        if name.casefold() in haystack:
            result.errors.append(
                f"pakette gerçek marka adı geçiyor: {name!r} — "
                "marka bilgisi DNA/RAG katmanının işidir (spec §12.3)"
            )


def _walk_strings(node: Any) -> list[str]:
    """İç içe yapıdaki TÜM metinleri toplar (anahtarlar dâhil)."""
    if isinstance(node, str):
        return [node]
    if isinstance(node, dict):
        found: list[str] = []
        for key, value in node.items():
            if isinstance(key, str):
                found.append(key)
            found.extend(_walk_strings(value))
        return found
    if isinstance(node, (list, tuple)):
        return [s for item in node for s in _walk_strings(item)]
    return []


def _check_size_target(content: dict, result: ValidationResult) -> None:
    """Boyut hedefi UYARI üretir, RED üretmez.

    ~6.000 karakter tasarım hedefidir, ölçülmüş bir eşik değildir (spec §3.4).
    Kapıya çevrilseydi ölçülmemiş bir sayı kabul kriteri olurdu (İlke 9).
    """
    total = sum(len(s) for s in _walk_strings(content))
    if total > SIZE_TARGET_CHARS:
        result.warnings.append(
            f"içerik {total} karakter — 6000 karakterlik tasarım hedefi aşıldı "
            "(uyarıdır, kapı değil)"
        )


# ─── 3. Çalışma zamanı okuması (spec §4.2) ──────────────────────────────────


@dataclass(frozen=True)
class SectorPackageContext:
    """Çalışma zamanına geçen paket bağlamı — dört alan (plan Task 8)."""

    package_id: UUID
    version: int
    content: dict
    sub_sector_slug: str


async def resolve_package_context(db, brand: dict) -> SectorPackageContext | None:
    """Markanın aktif paketini okur; yoksa/bozuksa `None`.

    Üç adım (spec §4.2): `sub_sector_id` boş → mevcut yol · dolu → `status='active'`
    tek satır · yok/bozuk → mevcut yol + log.

    `draft`/`archived` HİÇ okunmaz; sorgu onları zaten dışlar. Önbellek YOKTUR
    (bağlanan teknik karar 4) — aktivasyon anında bayat bağlam kalmasın diye.

    Bu fonksiyon üretim akışını ASLA kırmaz: her istisna yutulur ve `None`
    döner. Sessiz değildir — her başarısızlık log üretir.
    """
    sub_sector_id = brand.get("sub_sector_id")
    if not sub_sector_id:
        # Atamasız marka NORMAL yoldur — uyarı üretmez.
        return None

    try:
        row = await db.fetchrow(
            """
            SELECT p.id, p.version, p.content, s.slug AS sub_sector_slug
            FROM social.sector_packages p
            JOIN social.sectors s ON s.id = p.sector_id
            WHERE p.sector_id = $1 AND p.status = 'active'
            """,
            sub_sector_id,
        )
    except Exception as exc:
        logger.warning(
            "sektör paketi okunamadı, paketsiz yola düşülüyor "
            "(brand_id=%s sub_sector_id=%s): %s",
            brand.get("id"),
            sub_sector_id,
            exc,
        )
        return None

    if row is None:
        logger.warning(
            "alt sektöre atanmış markanın AKTİF paketi yok — bayat/eksik atama "
            "(brand_id=%s sub_sector_id=%s)",
            brand.get("id"),
            sub_sector_id,
        )
        return None

    content = row["content"]
    if not isinstance(content, dict):
        logger.warning(
            "sektör paketi içeriği bozuk (nesne değil: %s), paketsiz yola düşülüyor "
            "(brand_id=%s sub_sector_id=%s package_id=%s)",
            type(content).__name__,
            brand.get("id"),
            sub_sector_id,
            row["id"],
        )
        return None

    return SectorPackageContext(
        package_id=row["id"],
        version=row["version"],
        content=content,
        sub_sector_slug=row["sub_sector_slug"],
    )
