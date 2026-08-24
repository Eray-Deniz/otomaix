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
import unicodedata
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

    İki bilinçli ayrım var. **Birincisi:** girdi önce Unicode NFC'ye çekilir;
    `_normalize_slug` bunu yapmaz. Aynı adın iki yazımı aynı anahtarı vermek
    ZORUNDADIR, yoksa tek-modül kuralının koruduğu şey (yazım ve okuma aynı
    anahtarı görür) elden gider. Birleşik yazımda iki fonksiyon aynen eşittir —
    kural seti genişletilmedi, sağlamlaştırıldı.

    **İkincisi:** `_normalize_slug` çözümlenemeyen girdide `genel` döndürür
    (sektör düşüş kovası). Burada aynı davranış, bir sektör slug'ıyla ÇAKIŞAN
    sahte bir gün anahtarı üretirdi ve "sistemde karşılığı olmayan dönem pakete
    giremez" hükmünü (§4.4) sessizce delerdi. Bu yüzden çözümlenemeyen ad anahtar
    ÜRETMEZ, `ValueError` fırlatır.
    """
    if name is None or not str(name).strip():
        raise ValueError("özel gün adı boş — anahtar üretilemez (uydurma anahtar yasak)")
    # Unicode biçim bağımsızlığı: ayrışık (NFD) yazılmış bir ad, birleşik
    # yazımdan FARKLI bir anahtar üretiyordu (ölçüldü: "Şeker Bayramı" →
    # `seker-bayrami` ve `s-eker-bayrami`). Yazım tarafı biri, okuma tarafı
    # diğerini görürse özel gün bloğu sessizce hiç eşleşmez.
    name = unicodedata.normalize("NFC", str(name))
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

# `cta_kaliplari` öğesinin TAM anahtar kümesi (spec §3.4: {kalıp, tür, gerekçe}).
CTA_ITEM_KEYS = frozenset({"kalip", "tur", "gerekce"})

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

    structural = structural_errors(content)
    if structural:
        result.errors.extend(structural)
    if not isinstance(content, dict):
        # Yapısal hata listesi zaten sebebi söyledi; dış girdi gerektiren
        # kontroller (takvim, marka adları) bu noktadan sonra koşamaz.
        return result

    _check_special_day_keys(content.get("ozel_gun"), holiday_keys, result)
    _check_banned_brand_names(content, banned_brand_names, result)
    _check_size_target(content, result)

    return result


def structural_errors(content: Any) -> list[str]:
    """İçeriğin DIŞ GİRDİ GEREKTİRMEYEN yapısal hataları (spec §3.4).

    Yazım kapısı ile çalışma zamanı çözümleyicisi AYNI listeyi kullanır. Ayrı
    olsalardı yazımda geçen bir şekil çalışma zamanında farklı yorumlanabilirdi;
    aynı olduklarında "yazılabilen her paket okunabilir" tek cümleyle doğrudur.

    Yan etkisiz ve saf: çözümleyici bunu üretim yolunda çağırır.
    """
    errors: list[str] = []
    if not isinstance(content, dict):
        return [f"content nesne değil: {type(content).__name__}"]
    _check_closed_field_set(content, errors)
    _check_field_shapes(content, errors)
    _check_special_day_shapes(content.get("ozel_gun"), errors)
    return errors


def _check_closed_field_set(content: dict, errors: list[str]) -> None:
    unknown = sorted(set(content) - CONTENT_FIELDS)
    if unknown:
        errors.append(
            f"şema dışı alan(lar): {unknown} — alan kümesi kapalıdır, "
            "genişletme `schema_version` ile taşınır"
        )
    missing = sorted(CONTENT_FIELDS - set(content))
    if missing:
        errors.append(f"eksik alan(lar): {missing}")


def _check_field_shapes(content: dict, errors: list[str]) -> None:
    """Alanları YAPRAK düzeyinde denetler.

    Kap tipine bakıp geçmek yetmez (checkpoint 8, yüksek bulgu): `[None]`,
    `["   "]`, `{"a": False}` gibi yükler JSON'a yazılabilir ve Task 10'un
    render'ına deterministik olmayan veri taşırdı. Metin bekleyen her yaprak
    DOLU BİR METİN olmak zorundadır.
    """
    for name in TEXT_FIELDS:
        if name in content:
            _require_text(content[name], name, errors)

    for name in LIST_FIELDS:
        if name not in content:
            continue
        value = content[name]
        if not isinstance(value, list):
            errors.append(f"{name} dizi değil: {type(value).__name__}")
            continue
        if not value:
            errors.append(
                f"{name} boş — bilinçli boş bırakılacaksa {DELIBERATELY_EMPTY!r} yazılır"
            )
            continue
        if name == "cta_kaliplari":
            _check_cta_items(value, errors)
        else:
            for index, item in enumerate(value):
                _require_text(item, f"{name}[{index}]", errors)

    if "video_kodlar" in content:
        video = content["video_kodlar"]
        if not isinstance(video, dict) or len(video) != VIDEO_SUBSTRUCTURE_COUNT:
            errors.append(
                f"video_kodlar {VIDEO_SUBSTRUCTURE_COUNT} alt yapı taşımalı "
                "(hareket ve sahne ayrı; alan adları K-02 ile bağlanacak)"
            )
        else:
            for key, value in video.items():
                _require_text(value, f"video_kodlar[{key!r}]", errors)

    if "ozel_gun" in content and not isinstance(content["ozel_gun"], dict):
        errors.append(f"ozel_gun nesne değil: {type(content['ozel_gun']).__name__}")


def _check_cta_items(items: list, errors: list[str]) -> None:
    """CTA öğesi {kalip, tur, gerekce} — anahtar kümesi TAM, değerler metin."""
    for index, item in enumerate(items):
        label = f"cta_kaliplari[{index}]"
        if item == DELIBERATELY_EMPTY:
            continue
        if not isinstance(item, dict):
            errors.append(f"{label} nesne değil: {type(item).__name__}")
            continue
        if set(item) != CTA_ITEM_KEYS:
            errors.append(
                f"{label} anahtar kümesi {sorted(CTA_ITEM_KEYS)} olmalı, "
                f"{sorted(item)} geldi"
            )
        for slot in sorted(CTA_ITEM_KEYS & set(item)):
            _require_text(item[slot], f"{label}.{slot}", errors)


def _check_special_day_shapes(ozel_gun: Any, errors: list[str]) -> None:
    """Özel gün girdilerinin ŞEKLİ — anahtar doğrulaması ayrı (takvim gerekir)."""
    if not isinstance(ozel_gun, dict):
        return
    for key, entry in ozel_gun.items():
        label = f"ozel_gun[{key!r}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} nesne değil: {type(entry).__name__}")
            continue
        if set(entry) != set(SPECIAL_DAY_SLOTS):
            errors.append(
                f"{label} anahtar kümesi {sorted(SPECIAL_DAY_SLOTS)} olmalı, "
                f"{sorted(entry)} geldi"
            )
        for slot in SPECIAL_DAY_SLOTS:
            if slot in entry:
                _require_text(entry[slot], f"{label}.{slot}", errors)


def _require_text(value: Any, label: str, errors: list[str]) -> None:
    """Yaprak dolu bir METİN mi.

    `içerik-önerilmez` (K-120) geçerli sayılır — "bilinçli boş" ile
    "doldurulmamış" aynı değer olsaydı eksik iş dolu görünürdü. Mantıksal ve
    sayısal değerler metin DEĞİLDİR: `False`/`0` eskiden "dolu" sayılıyordu.
    """
    if not isinstance(value, str):
        errors.append(f"{label} metin değil: {type(value).__name__}")
    elif not value.strip():
        errors.append(
            f"{label} boş — bilinçli boş bırakılacaksa {DELIBERATELY_EMPTY!r} yazılır"
        )


def _check_special_day_keys(
    ozel_gun: Any, holiday_keys: set[str], result: ValidationResult
) -> None:
    """Anahtarlar sistem takvimine karşı doğrulanır — uydurma anahtar yasak."""
    if not isinstance(ozel_gun, dict):
        return
    for key in ozel_gun:
        if key not in holiday_keys:
            result.errors.append(
                f"özel gün anahtarı sistem takviminde YOK: {key!r} — "
                "karşılıksız dönem pakete giremez (spec §4.4)"
            )


def _check_banned_brand_names(
    content: dict, banned_brand_names: list[str], result: ValidationResult
) -> None:
    """Gerçek marka/firma adı geçen metin pakete GİREMEZ (K-15, spec §12.3).

    İki tuzak kapalı (checkpoint 8, yüksek bulgu):

    **Türkçe harf.** `casefold()` tek başına yetmez: `"ALTINBAŞ".casefold()`
    noktalı `i` üretir, `"Altınbaş".casefold()` noktasız `ı` bırakır — büyük
    harfle yazılmış marka adı kaçardı (ölçüldü). İki taraf da `_normalize_slug`
    ile AYNI Türkçe→ASCII tablosundan geçirilir, sonra katlanır.

    **Sözcük sınırı.** Çıplak alt dize araması kısa adları sıradan sözcüklerin
    içinde bulurdu ("Ada" ↔ "mağazada") ve meşru paketleri bloklardı. Eşleşme
    SOL sınırda aranır. Sağ taraf bilinçle SERBEST: Türkçe eklemeli bir dildir,
    "Altınbaş'tan" ve "Altınbaşlar" aynı adı taşır.

    Bilinçli asimetri: kısa bir marka adı aynı zamanda sıradan bir sözcükse
    (ör. "Ada") sol sınır onu yine de yakalar ve paket reddedilir. Yazım
    kapısında yanlış-pozitif, yanlış-negatiften iyidir — operatör mesajı görür,
    sızan marka bilgisi ise kalıcıdır.
    """
    names = [n.strip() for n in banned_brand_names if n and n.strip()]
    if not names:
        return
    haystack = _fold_turkish("\n".join(_walk_strings(content)))
    for name in names:
        folded = _fold_turkish(name)
        if not folded:
            continue
        # Sol sınır yalnız ad harf/rakamla BAŞLIYORSA aranır; noktalama ile
        # başlayan bir ad için sınır iddiası anlamsız olurdu.
        prefix = r"(?<![^\W_])" if folded[0].isalnum() else ""
        if re.search(prefix + re.escape(folded), haystack):
            result.errors.append(
                f"pakette gerçek marka adı geçiyor: {name!r} — "
                "marka bilgisi DNA/RAG katmanının işidir (spec §12.3)"
            )


def _fold_turkish(text: str) -> str:
    """Adı karşılaştırılabilir tek biçime indirger.

    Üç adım, sırası ÖNEMLİ: önce Unicode NFC (ayrışık `S`+birleşen-çengel ile
    birleşik `Ş` aynı şey demektir — ölçüldü: ayrışık yazım tabloya hiç
    uğramadan geçiyordu), sonra Türkçe→ASCII tablosu, sonra katlama. Sadece
    `casefold()` yetmez: `"ALTINBAŞ".casefold()` noktalı `i` üretir,
    `"Altınbaş".casefold()` noktasız `ı` bırakır.
    """
    return unicodedata.normalize("NFC", text).translate(_TR_ASCII).casefold()


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
    tek satır · yok/yapısal olarak geçersiz → mevcut yol + log.

    "Bozuk" ölçüsü yazım kapısıyla AYNIDIR (`structural_errors`): sözlük olması
    yetmez, alan şemasını tutturması gerekir. İki ölçü ayrı olsaydı yazımda geçen
    bir şekil çalışma zamanında başka türlü yorumlanabilirdi; aynı olduklarında
    "yazılabilen her paket okunabilir" tek cümleyle doğrudur. K-15(a) alan-düzeyi
    atlama dalı bilinçle YOKTUR — sözleşme tüm yolun düşmesini ister.

    `draft`/`archived` HİÇ okunmaz; sorgu onları zaten dışlar. Önbellek YOKTUR
    (bağlanan teknik karar 4) — aktivasyon anında bayat bağlam kalmasın diye.

    Bu fonksiyon üretim akışını ASLA kırmaz: sorgu, satır çözümlemesi ve yapısal
    doğrulama tek emniyet sınırının içindedir; her istisna yutulur ve `None`
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

        if row is None:
            logger.warning(
                "alt sektöre atanmış markanın AKTİF paketi yok — bayat/eksik atama "
                "(brand_id=%s sub_sector_id=%s)",
                brand.get("id"),
                sub_sector_id,
            )
            return None

        # Satır çözümlemesi de emniyet sınırının İÇİNDE (checkpoint 8, yüksek
        # bulgu): eskiden `try` yalnız sorguyu sarıyordu, satır erişiminde doğan
        # bir istisna üretim akışına KAÇARDI.
        package_id = row["id"]
        version = row["version"]
        content = row["content"]
        sub_sector_slug = row["sub_sector_slug"]

        # Sözlük OLMASI yetmez. Yazım kapısıyla AYNI yapısal doğrulayıcı koşar:
        # yazılabilen her paket okunabilir, okunamayan paket hiç açılmaz. Boş
        # sözlüğü geçirmek hatayı tüketiciye (Task 10 render'ı) taşırdı ve
        # K-15(a) alan-düzeyi atlama dalı bilinçle YOK.
        problems = structural_errors(content)
        if problems:
            logger.warning(
                "sektör paketi içeriği yapısal olarak geçersiz, paketsiz yola "
                "düşülüyor (brand_id=%s sub_sector_id=%s package_id=%s): %s",
                brand.get("id"),
                sub_sector_id,
                package_id,
                "; ".join(problems[:3]),
            )
            return None

        # Kurulum da `try` İÇİNDE: bugünkü dataclass kurucusu önemsiz, ama
        # sözleşme "çözümleyicinin hiçbir hatası üretimi bloklamaz" diyor ve
        # kurucuya bir gün doğrulama eklenirse istisna dışarı kaçmamalı.
        # (Checkpoint 8 tur 2: önceki commit bunun taşındığını YAZMIŞTI, oysa
        # taşınmamıştı — iddia yanlıştı.)
        return SectorPackageContext(
            package_id=package_id,
            version=version,
            content=content,
            sub_sector_slug=sub_sector_slug,
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
