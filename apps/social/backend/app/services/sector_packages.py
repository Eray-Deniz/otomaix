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
import random
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from app.services.package_events import log_package_event
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

# K-02 = A (Eray, 2026-08-24 — spec §11.5 karar bloğu): adlar BAĞLANDI ve şekil
# LİSTEDİR. Kapanıştan önce burada yalnız "iki alt yapı var mı" sorulabiliyordu;
# karar açık olduğu için adlar serbest, şekil de tek cümleydi.
#
# İki şey birden değişti ve ikisi de ürün gerekçesine dayanır:
#
# - **Adlar bağlı.** Serbest ad kabul edilseydi yazan taraf `motion`/`scene`
#   yazar, okuyan taraf `hareket`/`sahne` arardı ve havuz sessizce hiç
#   bulunamazdı — yazım/okuma ayrışmasının tam da K-01b'de kapatılan sınıfı.
# - **Şekil liste.** Tek cümle, sektöre özel olsa bile o sektörün HER videosunu
#   aynı tipte üretirdi. Çoğulluk biçimsel bir ayrıntı değil, alanın işlevinin
#   parçasıdır (spec §3.4'e eklenen not; input "havuz" / "alt liste" der).
VIDEO_POOL_KEYS = ("hareket", "sahne")

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
    _check_channel_markers(content, errors)
    return errors


# Paket içeriğinin KAPALI BAYRAK KAYDI — tek kalemli.
#
# Liste uydurulmadı, spec'ten TÜRETİLDİ: §8.4 bayrak kümesini "sekiz bayrak,
# kapalı" diye bağlar; §8.5 bunların YEDİSİNİN sentez sırasında TÜKETİLDİĞİNİ
# (karara etki edip kaybolduğunu) söyler ve yalnız kanal bayrağı için
# "etiketiyle taşınır" der; §3.4 aynı hükmü alan tablosunda tekrarlar
# ("taşınır, silinmez"). Dolayısıyla paket İÇERİĞİNDE geçebilecek bayrak
# kümesi tektir — bunu yazmak yeni bir karar değil, mevcut hükmün kod karşılığı.
_BRACKET_SEGMENT_RE = re.compile(r"\[[^\[\]]*\]")
_CHANNEL_FLAG_RE = re.compile(r"^\[\s*kanal\s*-\s*bagimli\s*:\s*([a-z0-9_]+)\s*\]$")


def _channel_flag_scopes(content: dict) -> list:
    """Bayrak kuralının uygulandığı YÜZEYLER — içeriğin tamamı DEĞİL.

    Kural önce tüm içeriğe uygulanmıştı ve aşırıydı: görsel yönergedeki
    `[close-up]` ya da kapsam metnindeki `[bkz. 3]` gibi zararsız bir notasyon
    yapısal hata sayılıyor, çalışma zamanı da paketin TAMAMINI devre dışı
    bırakıyordu. Spec bayrak sözlüğünü kapatır ama paket düz yazısındaki her
    ayracı bayrağa AYIRMAZ.

    Kapsam artık okuma tarafıyla hizalı: çalışma zamanı filtresi CTA öğesinin
    TÜM metinlerini tarar, o yüzden yazım kapısı da tam o birimi kapsar — ne
    eksik (aksi hâlde okumanın gördüğü bozuk bayrak yazımda denetlenmezdi) ne
    fazla. Özel gün girdisinin CTA'sı da bir CTA yüzeyidir, o da dâhildir.
    """
    scopes: list = [content.get("cta_kaliplari")]
    ozel_gun = content.get("ozel_gun")
    if isinstance(ozel_gun, dict):
        for entry in ozel_gun.values():
            if isinstance(entry, dict) and "cta" in entry:
                scopes.append(entry["cta"])
    return scopes


def _check_channel_markers(content: dict, errors: list[str]) -> None:
    """Pakette geçen HER köşeli ayraç, kanal bayrağının ta kendisi olmalıdır.

    **Neden bu biçim (checkpoint 9, dört tur).** İlk üç deneme "etiket gibi
    görünen metni yakala" mantığındaydı ve yakınsamadı: tur 1 tipografik tire
    ve görünmez karakteri kapattı, tur 2 eksik ayıracı, tur 3 ayırıcı sınıfını,
    tur 4 yanlış yazılmış bayrak adını açtı. Kök sebep her turda aynıydı:
    serbest metinden *"bu bir etiket DEĞİLDİR"* i kanıtlamaya çalışmak. Bu tür
    bir kapı ya bypass ya yanlış-pozitif üretir; beşinci regex beşinci turu
    davet ederdi.

    Kapanış negatif tahminden KAPSAMAYA taşındı. Bayrak tanımı gereği köşeli
    ayraçlıdır ve paket içeriğinde geçebilecek TEK bayrak vardır (yukarıdaki
    türetme). Öyleyse kural tektir: **ayraç içindeki her şey kanal bayrağının
    kurallı biçimine uymalı, yoksa içerik reddedilir.** Yanlış yazım, birleşik
    yazım, eksik ayıraç, iç içe ayraç, sentezde tüketilmesi gereken bir bayrağın
    pakete sızması — hepsi ayrı ayrı yakalanarak değil, TEK kuralla düşer.

    **Kapsam sınırı, dürüstçe:** ayraçsız yazılmış bir işaret (`kanal-bağımlı
    whatsapp_hatti`) YAKALANMAZ ve yakalanması hedeflenmez — ayraçsız metin
    bayrak konvansiyonunun dışındadır ve orada "işaret miydi" sorusunu sormak
    tam da yakınsamayan tahmin oyunudur. İddia bu yüzden dar: *ayraçlı* her
    işaret kapalıdır. Sınır kendi testiyle pinlidir, sessizce kaybolamaz.

    Yazım kapısı okuma tarafından KASITLI olarak daha katıdır (okuma
    `[kanal - bağımlı: x]` biçimini de etiket sayar). Asimetrinin yönü
    emniyetlidir: okuma daha çok etiket görür, yani daha çok kalıp atlar.

    Kapı `structural_errors` içinden koşar, yani çalışma zamanı da aynı ölçüyü
    uygular: bozuk bayraklı paket K-15(a) gereği TÜM yoluyla paketsiz yola düşer.
    """
    for text in _walk_strings(_channel_flag_scopes(content)):
        canonical = _canonical_marker_text(text)
        if "[" not in canonical and "]" not in canonical:
            continue

        segments = _BRACKET_SEGMENT_RE.findall(canonical)
        if canonical.count("[") != len(segments) or canonical.count("]") != len(segments):
            errors.append(
                f"dengesiz/iç içe köşeli ayraç: {text!r} — paket içeriğinde ayraç "
                "yalnız kanal bayrağı için kullanılır: `[kanal-bağımlı: <anahtar>]`"
            )
            continue

        for segment in segments:
            match = _CHANNEL_FLAG_RE.match(segment)
            if match is None:
                errors.append(
                    f"paket içeriğine giremeyecek bayrak: {segment!r} ({text!r}) — "
                    "burada geçebilecek TEK bayrak `[kanal-bağımlı: <anahtar>]`; "
                    "diğer bayraklar sentezde tüketilir (spec §8.5)"
                )
                continue
            key = match.group(1)
            if key not in CHANNEL_KEYS:
                errors.append(
                    f"kanal bayrağında geçersiz anahtar {key!r}: {text!r} — "
                    f"kapalı küme: {', '.join(sorted(CHANNEL_KEYS))}"
                )


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
        if not isinstance(video, dict) or set(video) != set(VIDEO_POOL_KEYS):
            errors.append(
                "video_kodlar anahtar kümesi "
                f"{sorted(VIDEO_POOL_KEYS)} olmalı (K-02 = A ile bağlandı); "
                + (
                    f"{sorted(video)} geldi"
                    if isinstance(video, dict)
                    else f"{type(video).__name__} geldi"
                )
            )
        else:
            for key in VIDEO_POOL_KEYS:
                pool = video[key]
                label = f"video_kodlar[{key!r}]"
                if not isinstance(pool, list):
                    errors.append(
                        f"{label} havuz (liste) olmalı, {type(pool).__name__} geldi — "
                        "tek cümle o sektörün her videosunu aynı tipte üretirdi"
                    )
                    continue
                if not pool:
                    errors.append(
                        f"{label} boş havuz — en az bir kalıp yazılmalı"
                    )
                    continue
                for index, item in enumerate(pool):
                    _require_text(item, f"{label}[{index}]", errors)

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


def has_meaningful_text(value: Any) -> bool:
    """Yaprak, noktalama ve boşluk dışında İÇERİK taşıyor mu.

    **Yazım ve okuma bu TEK yüklemi paylaşır** — K-01b'nin tek-normalize
    kuralıyla aynı disiplin. İkisi ayrı ölçü kullanırsa kabulden geçen bir değer
    tüketimde hiçe indirgenir ve sessiz bir delik açar.

    Ölçüldü (checkpoint 11, tur 3): sahne havuzundaki `"."` yazım kapısından
    geçiyordu (çünkü kapı yalnız `strip()` bakıyordu), tüketicide ise noktalama
    atılınca boş dizeye iniyordu. "Her metin boş dizeyi içerir" olduğu için
    sektörel zenginleştirme tamamen atlanıyor, üstelik ne hata ne log
    üretiliyordu. Sorun tek karakter değil ÖLÇÜ AYRIŞMASIydı; bu yüzden kural
    tek yerde yaşar ve iki taraf da onu çağırır.
    """
    return isinstance(value, str) and any(ch.isalnum() for ch in value)


def _require_text(value: Any, label: str, errors: list[str]) -> None:
    """Yaprak ANLAMLI bir METİN mi.

    `içerik-önerilmez` (K-120) geçerli sayılır — "bilinçli boş" ile
    "doldurulmamış" aynı değer olsaydı eksik iş dolu görünürdü. Mantıksal ve
    sayısal değerler metin DEĞİLDİR: `False`/`0` eskiden "dolu" sayılıyordu.
    Yalnız noktalamadan oluşan değerler de içerik DEĞİLDİR (bkz.
    `has_meaningful_text`).
    """
    if not isinstance(value, str):
        errors.append(f"{label} metin değil: {type(value).__name__}")
    elif not has_meaningful_text(value):
        errors.append(
            f"{label} boş ya da yalnız noktalama — bilinçli boş bırakılacaksa "
            f"{DELIBERATELY_EMPTY!r} yazılır"
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

    Dört adım, sırası ÖNEMLİ:

    1. **NFKC** — ayrışık `S`+birleşen-çengel ile birleşik `Ş` aynı şeydir.
    2. **Türkçe→ASCII tablosu** — `ı`/`İ` gibi ATOMİK harfler (ayrışması yok)
       burada düşer. Sadece `casefold()` yetmez: `"ALTINBAŞ".casefold()` noktalı
       `i` üretir, `"Altınbaş".casefold()` noktasız `ı` bırakır.
    3. **casefold** — kalan büyük/küçük harf farkı.
    4. **NFD + birleşen işaretleri at** — kapanış adımı. Büyük/küçük harf
       işlemlerinin KENDİSİ birleşen işaret üretir (`"İ".lower()` → `i`+U+0307)
       ve NFC bunu geri birleştirmez; ölçüldü. Tek tek biçim yamamak üç tur
       yakınsamadı, çünkü sorun bir varyant değil bir SINIF: "büyük/küçük harf
       işleminden sağ çıkan birleşen işaret". Bu adım sınıfın tamamını kapatır.

    Bilinçli yan etki: Türkçe dışı aksanlar da düşer (`é` → `e`). Yazım
    kapısında bu, eşleşmeyi genişletir — yani reddetme yönüne çalışır.
    """
    folded = unicodedata.normalize("NFKC", text).translate(_TR_ASCII).casefold()
    decomposed = unicodedata.normalize("NFD", folded)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


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


async def _record_event(db, **kwargs) -> None:
    """Olay yazımı BU yüzeyde asla üretimi düşürmez.

    `log_package_event` sözleşme ihlalinde bilerek istisna atar (yarım denetim
    izi üretmemek için). Ama çalışma zamanı yollarında o istisnanın kaçması,
    bir denetim satırı yüzünden kullanıcının içeriğini düşürmek olurdu —
    çözümleyicinin kendi sözleşmesi "üretim akışını ASLA kırmaz"dır. O yüzden
    çağrı burada sarılır ve başarısızlık log'a düşer.
    """
    try:
        await log_package_event(db, **kwargs)
    except Exception as exc:
        logger.error(
            "paket olayı kaydedilemedi (event_type=%s): %s", kwargs.get("event_type"), exc
        )


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
            await _record_event(
                db,
                event_type="stale_assignment_fallback",
                brand_id=brand.get("id"),
                sector_id=sub_sector_id,
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
            # Bu bir DOĞRULAMA hatasıdır, eşleşmezlik DEĞİL (spec §14.4 ikisini
            # ayrı sayar). Paket okundu ama şemayı tutturmadı; "bu gün pakette
            # yok" ile aynı kutuya konsaydı işletim ikisini ayırt edemezdi.
            await _record_event(
                db,
                event_type="package_read_error",
                brand_id=brand.get("id"),
                sector_id=sub_sector_id,
                package_id=package_id,
                detail={
                    "reason": "structural",
                    "problem_count": len(problems),
                    "first_problem": problems[0][:200],
                },
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
        # Belgeli sınır (plan Task 12): okuma hatası VERİTABANININ KENDİSİNDEN
        # geliyorsa olay satırı da yazılamaz — o durumda bağımsız best-effort
        # kanal yukarıdaki `logger.warning`'dir. Hata başka bir sebeptense
        # (satır çözümlemesi, kurucu) olay normal yazılır.
        await _record_event(
            db,
            event_type="package_read_error",
            brand_id=brand.get("id"),
            sector_id=sub_sector_id,
            detail={"reason": "read_failed", "error": type(exc).__name__},
        )
        return None


# ─── 4. Kanal envanteri (spec §12.2 — plan Task 9) ──────────────────────────

# Anahtar uzayı KAPALIDIR ve `[kanal-bağımlı: X]` etiketinin X uzayıyla birebir
# aynıdır. Serbest X değeri deterministik filtreyi imkânsız kılar (spec §12.2).
CHANNEL_KEYS = frozenset(
    {"whatsapp_hatti", "fiziksel_magaza", "randevu_sistemi", "eticaret_sitesi"}
)

# Etiket, kanonikleştirilmiş metinde aranır — bu yüzden kalıp katlanmış biçimi
# (`bagimli`) ve ASCII tireyi tarif eder. Boşluk ve tire çevresi serbesttir.
#
# Tanıma GENİŞ, geçirme DAR: her iki gevşeklik de aynı yöne — ATLAMA yönüne —
# çalışır. Bir yazımı tanımamak ise ters yöndedir (doğrulanmamış kanalın CTA'sı
# sızar), o yüzden tanıma tarafında cömert olmak fail-closed'dır.
_CHANNEL_TAG_RE = re.compile(r"\[\s*kanal\s*-\s*bagimli\s*:\s*([^\]]*)\]")

# Unicode kategorisi `Pd` (dash punctuation) DIŞINDA kalan, gözle tire okunan
# işaretler. `−` matematiksel eksi (Sm), `⁃` madde-işareti tire (Po), `˗`
# değiştirici eksi (Sk), `➖` ağır eksi (So).
_DASH_LOOKALIKES = frozenset({"−", "⁃", "˗", "➖"})


def _canonical_marker_text(text: str) -> str:
    """Etiket taraması için metni kanonikleştirir — YALNIZ tarama için.

    `_fold_turkish` büyük/küçük harf ve Türkçe harf sınıfını kapatır ama
    NOKTALAMAYA dokunmaz. Checkpoint 9'da ölçüldü: dokuz gerçekçi yazımdan
    ALTISI etiketi görünmez kılıyordu — `kanal‑bağımlı` (U+2011), `kanal–`,
    `kanal—`, `kanal−` ve `bağ<görünmez>ımlı` biçimleri "etiketsiz" sayılıp
    doğrulanmamış markaya SIZIYORDU.

    Kapatılan sınıf tek tek karakter değil: **"okunuşu etiket olan ama ASCII'ye
    eşit olmayan işaret"**. İki bileşeni var ve ikisi de kategori düzeyinde
    kapatılır (liste düzeyinde değil — yeni bir tire eklenirse yama gerekmesin):

    - `Cf` (format) karakterleri DÜŞÜRÜLÜR: yumuşak tire, sıfır-genişlikli
      boşluk/birleştirici, BOM, sözcük-birleştirici. Bunlar metne gözle
      görünmeden girer (kopyala-yapıştır, biçimlendirme) ve baytı değiştirir.
    - `Pd` (dash) karakterleri ve tire görünümlü diğer işaretler ASCII `-`
      olur.

    Bu dönüşüm `_fold_turkish`in İÇİNE konmadı: o fonksiyon marka adı yazım
    kapısının da tabanıdır ve davranışı dondurulmuş bir kapanış matrisiyle
    pinlenmiştir. Noktalama kanonikleştirmesi orada gereksiz bir davranış
    değişikliği olurdu; burada ise sözleşmenin ta kendisi.
    """
    canonical: list[str] = []
    for char in _fold_turkish(text):
        category = unicodedata.category(char)
        if category == "Cf":
            continue
        if category == "Pd" or char in _DASH_LOOKALIKES:
            canonical.append("-")
        else:
            canonical.append(char)
    return "".join(canonical)


def validate_channels(channels: Any) -> list[str]:
    """Marka kanal envanterinin yazım kapısı. Boş liste = geçerli.

    İki kural: anahtar kapalı kümede olmalı, değer MANTIKSAL olmalı.

    Değer kuralı neden sert: filtre `is True` arar. `"true"` metni ya da `1`
    sessizce hiçbir zaman geçmezdi — operatör kanalı açtığını sanır, CTA'lar
    sessizce düşerdi. Kapı bu sessiz yanlış-yapılandırmayı görünür hataya
    çevirir. (`isinstance(1, bool)` yanlıştır; `True` doğrudur.)
    """
    if not isinstance(channels, dict):
        return [
            f"channels nesne olmalı, {type(channels).__name__} geldi "
            "(kapalı anahtar kümesi: " + ", ".join(sorted(CHANNEL_KEYS)) + ")"
        ]

    errors: list[str] = []
    for key in sorted(channels, key=repr):
        if not isinstance(key, str) or key not in CHANNEL_KEYS:
            errors.append(
                f"bilinmeyen kanal anahtarı {key!r} — kapalı küme: "
                + ", ".join(sorted(CHANNEL_KEYS))
            )
            continue
        value = channels[key]
        if not isinstance(value, bool):
            errors.append(
                f"channels[{key!r}] mantıksal değer olmalı (true/false), "
                f"{type(value).__name__} geldi"
            )
    return errors


def _verified_channels(channels: Any) -> frozenset[str]:
    """Markanın DOĞRULANMIŞ kanalları — yalnız kapalı kümede ve tam `True`.

    `channels` yoksa, boşsa ya da nesne değilse sonuç boş kümedir: envanteri
    doldurulmamış marka, hiçbir kanal-bağımlı kalıbı almaz (spec §12.2
    "muhafazakâr davranır").
    """
    if not isinstance(channels, dict):
        return frozenset()
    return frozenset(key for key in CHANNEL_KEYS if channels.get(key) is True)


def _channel_tags(item: Any) -> frozenset[str]:
    """Öğenin taşıdığı kanal etiketlerini (kanonik anahtar biçiminde) toplar.

    Etiket YALNIZ `kalip` alanında aranmaz — öğenin her metni taranır. Etiketin
    hangi alanda durduğu brief/denetçi sözleşmesinin işidir; filtre onu
    varsayarsa yanlış alana yazılmış bir etiket sessizce görünmez olurdu.

    Anahtar da kanonikleşmiş gelir, yani `WHATSAPP_HATTI` ile `whatsapp_hatti`
    aynı anahtardır. Kapalı kümeye ait olup olmadığına ÇAĞIRAN bakar — burada
    "yazılan ne" toplanır, "geçerli mi" değil.
    """
    tags: set[str] = set()
    for text in _walk_strings(item):
        for match in _CHANNEL_TAG_RE.finditer(_canonical_marker_text(text)):
            tags.add(match.group(1).strip())
    return frozenset(tags)


def filter_channel_dependent(items: Any, channels: Any) -> list[dict]:
    """`[kanal-bağımlı: X]` etiketli kalıpları marka gerçeğine göre eler.

    Sözleşme (spec §12.2 · plan Task 9):

    - etiketsiz kalıp HER ZAMAN geçer;
    - etiketli kalıp yalnız `channels[X] is True` ise geçer;
    - `channels` yok/boş/bozuk → etiketli kalıp ATLANIR;
    - etiketteki `X` kapalı kümede değilse kalıp ATLANIR — bilinmeyen anahtar
      "etiketsiz" sayılMAZ, yoksa uzayın kapalılığı filtreyi delmenin yolu
      olurdu;
    - bir kalıp birden çok etiket taşıyorsa HEPSİ doğrulanmalıdır.

    Filtre SEÇER, değiştirmez: dönen öğeler girdideki nesnelerin ta kendisidir
    ve sıraları korunur. Etiket metni de silinmez (spec §3.4: "taşınır,
    silinmez") — basım biçimi enjeksiyon katmanının (Task 10) işidir.

    Girdi savunması her dalda açıktır (liste değil → boş; sözlük değil →
    envantersiz sayılır), bu yüzden gövdede toptan bir `except` YOKTUR: burada
    G/Ç yok, ve pakete giren içerik yazım kapısından + çözümleyicinin yapısal
    doğrulamasından geçmiş JSON'dur. Test edilemeyen bir emniyet dalı, kapalı
    olduğunu sandığın bir dal demektir.
    """
    if not isinstance(items, list):
        return []

    verified = _verified_channels(channels)
    return [item for item in items if _channel_tags(item) <= verified]


# ─── 5. Enjeksiyon basımı (spec §4.3/§4.5 — plan Task 10) ───────────────────

# K-04, spec §4.5 — NORMATİF metin, birebir. "2-3" talimat metninin parçasıdır,
# eşik/kapı DEĞİLDİR (İlke 9).
USAGE_INSTRUCTION = (
    "Bu dağarcıktan içeriğe uyan 2-3 öğeyi seç; listeyi tamamlamaya çalışma; "
    "ürün veya marka bilgisiyle çelişen kalıbı kullanma; markanın sahip olduğunu "
    "bilmediğin kanalı veya hizmeti önerme."
)

BLOCK_HEADER = "SEKTÖR PAKETİ"

# Yüzey → basılacak alanlar, SIRASIYLA. Sıra sabittir: aynı paket iki koşumda
# aynı baytları üretmezse Katman-1 kapısı anlamını yitirir.
#
# Görsel/video dağarcığı (`gorsel_kodlar`, `video_kodlar`) bu yüzeylerde YOK —
# spec §4.3 onları görsel director ve durağan kare yüzeylerine gönderir (Task
# 11). Fazla basmak "doğru yüzey" kontrolünü (spec §5.4) delerdi.
_SURFACE_FIELDS: dict[str, tuple[str, ...]] = {
    "caption": (
        "kapsam",
        "ton_ve_dil",
        "kanca_kaliplari",
        "cta_kaliplari",
        "takvim_temalari",
        "yasaklar_ve_hassasiyetler",
    ),
    "idea": (
        "kapsam",
        "ton_ve_dil",
        "kanca_kaliplari",
        "cta_kaliplari",
        "takvim_temalari",
        "yasaklar_ve_hassasiyetler",
    ),
}

_FIELD_LABELS = {
    "kapsam": "Kapsam",
    "ton_ve_dil": "Ton ve dil",
    "kanca_kaliplari": "Kanca kalıpları",
    "cta_kaliplari": "CTA kalıpları",
    "takvim_temalari": "Takvim temaları",
    "yasaklar_ve_hassasiyetler": "Yasaklar ve hassasiyetler",
}

# `anma` ve `kutlama` türlerinde CTA yerine kutlama-saygı kalıbı geçer
# (spec §11.3). Karşılaştırma katlanmış biçimde yapılır — paket metni büyük
# harfle ya da Türkçe harflerle yazılmış olabilir.
_RESPECT_TYPES = frozenset({"anma", "kutlama"})
_MEMORIAL_TYPE = "anma"


def _strip_channel_tags(text: str) -> str:
    """`[kanal-bağımlı: X]` işaretini BASILAN metinden çıkarır.

    Etiket paket İÇERİĞİNDE taşınır ve silinmez (spec §3.4) — orası filtrenin
    girdisidir. Modele giden metinde ise işaretin işi bitmiştir: filtre zaten
    kararı vermiştir, kalan metin kalıbın kendisidir.

    Tanıma ölçüsü filtreninkiyle AYNI yerden gelir: ayraç parçası tek tek
    kanonikleştirilip `_CHANNEL_FLAG_RE`'ye sorulur. İkinci bir gramer
    yazılmadı — yazılsaydı filtre bir yazımı tanıyıp basım tanımayabilirdi.

    **Belgeli sınır:** ayracın kendisi ASCII `[` `]` olmak zorundadır. Tam
    genişlikli ayraçla yazılmış bir etiketi filtre (kanonikleştirmeden sonra)
    TANIR ama bu fonksiyon metinden çıkaramaz — çıkarma ham metinde ayraç
    parçası aramak zorunda, kanonik metindeki konumu ham metne geri
    eşlenemiyor (katlama 1:1 değil). Sonuç kozmetiktir, emniyet açığı değildir:
    artık kalan etiket YALNIZ filtreden GEÇMİŞ, yani markada DOĞRULANMIŞ bir
    kanalın kalıbında bulunabilir. Sınır testle pinlidir.
    """

    def _drop(match: re.Match) -> str:
        segment = match.group(0)
        canonical = _canonical_marker_text(segment).strip()
        return "" if _CHANNEL_FLAG_RE.fullmatch(canonical) else segment

    stripped = _BRACKET_SEGMENT_RE.sub(_drop, text)
    # Etiketin bıraktığı boşluk artığı temizlenir; sonuç deterministiktir.
    return re.sub(r"[ \t]{2,}", " ", stripped).strip()


def _render_cta_items(items: Any, channels: Any) -> list[str]:
    """CTA kalıplarını marka gerçeğine göre eleyip basar.

    Eleme Task 9'un filtresidir — burada ikinci bir koşul YAZILMAZ.
    `gerekce` basılmaz: o, kalıbın yazarına ait bir gerekçedir, üretim
    talimatı değil.
    """
    lines: list[str] = []
    for item in filter_channel_dependent(items, channels):
        if isinstance(item, dict):
            kalip = _strip_channel_tags(str(item.get("kalip", "")))
            tur = str(item.get("tur", "")).strip()
            lines.append(f"- {kalip} (tür: {tur})" if tur else f"- {kalip}")
        else:
            lines.append(f"- {_strip_channel_tags(str(item))}")
    return lines


def render_package_block(
    context: SectorPackageContext, *, surface: str, channels: Any = None
) -> str:
    """Paket bloğunu deterministik metne çevirir (spec §4.3).

    Blok kök `SECTOR_GUIDANCE`'ın YERİNE geçer — yan yana basılmaz (spec §4.1).
    Başında K-04 kullanım talimatı durur: sonda duran bir talimat, listeyi
    tamamlama refleksi çoktan tetiklendikten sonra gelirdi (spec §4.5).

    `surface` geliştirici sabitidir, veri DEĞİL — tanınmayan yüzey sessizce
    "hepsini bas"a düşmez, istisna fırlatır. Sessiz düşüş, yanlış yüzeye yanlış
    dağarcık basmak demek olurdu (spec §5.4 "doğru yüzey" kontrolü).
    """
    fields = _SURFACE_FIELDS.get(surface)
    if fields is None:
        raise ValueError(
            f"bilinmeyen enjeksiyon yüzeyi: {surface!r} — tanımlı yüzeyler: "
            + ", ".join(sorted(_SURFACE_FIELDS))
        )

    content = context.content
    parts = [
        f"\n--- {BLOCK_HEADER} ({context.sub_sector_slug}) ---",
        USAGE_INSTRUCTION,
        "",
    ]

    for name in fields:
        if name not in content:
            continue
        label = _FIELD_LABELS[name]
        value = content[name]
        if name == "cta_kaliplari":
            lines = _render_cta_items(value, channels)
            if lines:
                parts.append(f"{label}:")
                parts.extend(lines)
        elif isinstance(value, list):
            parts.append(f"{label}:")
            parts.extend(f"- {item}" for item in value)
        else:
            parts.append(f"{label}: {value}")

    parts.append(f"--- {BLOCK_HEADER} SONU ---")
    return "\n".join(parts)


def match_special_day(context, day_name: str) -> tuple[str | None, str | None]:
    """İstenen özel günün pakette karşılığı var mı — `(anahtar, sebep)`.

    Saf ve eşzamanlıdır: hem basım yolu (`render_special_day_lines`) hem olay
    kaydını yazan async sahip AYNI yüklemi çağırır. İki ayrı ölçü olsaydı basım
    "eşleşti" derken denetim izi "eşleşmedi" diyebilirdi (K-01b disiplini).

    `sebep is None` = eşleşti. Anahtar, çözümlenebildiği her durumda döner —
    log ve olay `detail`i onu taşır, çünkü işletimde "hangi anahtara bakıldı"
    sorusu eşleşmemenin kendisinden daha çok iş görür.
    """
    if not day_name:
        return (None, None)
    ozel_gun = context.content.get("ozel_gun")
    try:
        key = normalize_special_day_key(day_name)
    except ValueError:
        return (None, "day_name_not_normalizable")
    if not isinstance(ozel_gun, dict):
        return (key, "package_has_no_special_days")
    if not isinstance(ozel_gun.get(key), dict):
        return (key, "no_entry_for_day")
    return (key, None)


def render_special_day_lines(
    context: SectorPackageContext, day_name: str | None, channels: Any = None
) -> list[str]:
    """Seçili özel günün paket karşılığını basar; yoksa BOŞ döner + log.

    Sessiz düşme sözleşmesi (spec §11.1) "iz bırakmadan düş" demek DEĞİLDİR:
    üretim akışı kesilmez ama eşleşmeme GÖZLENEBİLİR olur. Eşleşmeme normal bir
    durumdur (paket her günü taşımak zorunda değil), o yüzden seviye `info`
    değil `warning` olmalı mı sorusu şuradan karara bağlandı: pakete atanmış bir
    markada operatör bir günü eklemeyi unutmuş olabilir ve bu görülmelidir.

    Görsel vurgu burada BASILMAZ — o, görsel yüzeyinin dağarcığıdır (spec §4.3,
    Task 11). Anahtar eşleşmesi tek normalize modülünden geçer (K-01b).

    Günün CTA'sı da bir CTA yüzeyidir ve AYNI kanal filtresinden geçer. Yazım
    kapısı bayrağı bu yüzeyde de meşru sayar (`_channel_flag_scopes`); basım
    yalnız `cta_kaliplari`'nı elerse doğrulanmamış kanal buradan sızardı —
    kapsam okuma tarafıyla hizalı olmalı, ne eksik ne fazla.
    """
    if not day_name:
        return []
    # Eşleşme yüklemi TEK yerde yaşar (`match_special_day`); burası onun
    # sonucunu kullanır. Olay kaydını async sahip yazar — basım yolu
    # eşzamanlıdır ve donmuş prompt kapısının içinden geçer, oraya bir
    # veritabanı yazımı sokmak o kapıyı da kirletirdi.
    key, reason = match_special_day(context, day_name)
    if reason is not None:
        logger.warning(
            "özel gün paket karşılığı YOK, dönem kalıpları basılmıyor "
            "(package_id=%s sub_sector=%s gün=%r anahtar=%r sebep=%s)",
            context.package_id,
            context.sub_sector_slug,
            day_name,
            key,
            reason,
        )
        return []
    entry = context.content["ozel_gun"][key]

    tur = str(entry.get("tur", "")).strip()
    lines = [f"--- {BLOCK_HEADER} DÖNEM KALIPLARI ---"]
    if tur:
        lines.append(f"Tür (paket): {tur}")
        # K-03 (spec §11.2, kapalı): çatışmada paket türü üretim davranışında
        # üstündür; takvim kategorisi günün kimliği için korunur ve basılmaya
        # devam eder.
        lines.append(
            "Çatışma hâlinde bu tür üretim davranışında üstündür; yukarıdaki "
            "takvim kategorisi günün kimliği için korunur."
        )
    for slot, label in (("mesaj_ekseni", "Mesaj ekseni"), ("kanca", "Kanca")):
        value = entry.get(slot)
        if isinstance(value, str) and value.strip():
            lines.append(f"{label}: {value}")

    cta = entry.get("cta")
    if isinstance(cta, str) and cta.strip():
        # Tek öğelik de olsa filtre AYNI fonksiyondur; burada ikinci bir kanal
        # koşulu yazılmaz. Doğrulanmamış kanalın CTA'sı satırıyla birlikte
        # DÜŞER (muhafazakâr yön, spec §12.2).
        if filter_channel_dependent([cta], channels):
            lines.append(f"CTA: {_strip_channel_tags(cta)}")

    folded_tur = _fold_turkish(tur).strip()
    if folded_tur in _RESPECT_TYPES:
        lines.append(
            "Bu dönemde CTA yerine kutlama-saygı kalıbı kullan; satış çağrısı "
            "kullanma (indirim, kampanya, fiyat vurgusu yasak)."
        )
        # K-119 (Eray, 2026-08-23): yasak KULLANICI İSTEĞİNİ geçersiz kılar.
        # Bu, öncelik hiyerarşisinin (spec §4.6) tek istisnasıdır ve talimatta
        # AÇIKÇA yazması gerekir — yoksa model kullanıcı isteğini üstün sayar.
        lines.append(
            "Bu yasak KULLANICI İSTEĞİNİN ÜSTÜNDEDİR: kullanıcı kampanya, "
            "indirim veya satış yönlendirmesi istese bile uygulanmaz."
        )
    if folded_tur == _MEMORIAL_TYPE:
        lines.append(
            "Anma ek kısıtı: yalnız saygı çerçevesinde içerik üret; uygun bir "
            "saygı çerçevesi kurulamıyorsa içerik önerme."
        )
    return lines


# ─── 6. Hareket havuzu (K-02 = A · K-113 = A — plan Task 11) ────────────────

MOTION_POOL_KEY = "hareket"
SCENE_POOL_KEY = "sahne"


def _pool(context: SectorPackageContext | None, key: str) -> list[str]:
    """Paketin adlı havuzunu dolu metinlere indirger; yoksa BOŞ liste.

    Yazım kapısı bu şekli zaten zorluyor (`VIDEO_POOL_KEYS`), ama okuma tarafı
    kapıya GÜVENMEZ: paket eski bir şemayla yazılmış olabilir ya da içerik elle
    değiştirilebilir. Boş sonuç, çağıranın "havuz yok" dalına düşmesi demektir —
    bu, uydurmanın değil geri düşüşün yönüdür.
    """
    if context is None:
        return []
    video = context.content.get("video_kodlar")
    if not isinstance(video, dict):
        return []
    pool = video.get(key)
    if not isinstance(pool, list):
        return []
    # Okuma tarafı da AYNI yüklemi uygular: kapı bugün anlamsız yaprağı
    # reddediyor ama eski bir paket ya da elle değiştirilmiş içerik hâlâ
    # taşıyabilir. Süzme burada da yapılır ki tüketiciler hep anlamlı öğe görsün.
    return [item for item in pool if has_meaningful_text(item)]


def scene_pool(context: SectorPackageContext | None) -> list[str]:
    """Durağan kare yüzeyine giden sahne havuzu (spec §4.3, iki modda da)."""
    return _pool(context, SCENE_POOL_KEY)


def motion_pool(context: SectorPackageContext | None) -> list[str]:
    """Hareket yüzeyine giden havuz — modele SEÇTİRİLİR (K-02 = A)."""
    return _pool(context, MOTION_POOL_KEY)


def resolve_motion_prompt(
    context: SectorPackageContext | None, requested: Any
) -> str | None:
    """İstemciden dönen hareket seçimini havuza karşı doğrular.

    Sözleşme (spec §11.5 karar bloğu):

    - paketsiz marka ya da boş/bozuk havuz → `None`; çağıran BUGÜNKÜ sabit
      listeye düşer (K-113 = A). Bu katman orada hiçbir şey söylemez;
    - `requested` havuzun TAM üyesiyse aynen kullanılır — modelin içeriğe uygun
      seçimi budur;
    - üye DEĞİLSE kullanılmaz ve uydurmaya düşülmez: sunucu AYNI havuzdan seçer.

    **Neden tam eşleşme.** Seçim caption aşamasında yapılır, kullanım stage-1'de;
    arada istemci vardır. Serbest metin kabul edilseydi video üreticisine keyfi
    bir istem enjekte edilebilirdi. Bu, K-07 damgasının taşıma ilkesiyle aynıdır:
    istemci taşır, sunucu doğrular.

    **Neden geri düşüş rastgele.** Sabit bir öğeye (`pool[0]`) düşmek belirleyici
    olurdu ama model alanı sistematik olarak döndürmediğinde o sektörün HER
    videosu aynı kalıba düşerdi — yani K-02'yi kapatma sebebimizin ta kendisi
    geri gelirdi. Seçici bu yüzden bugünkü `_pick_motion_prompt` ile aynı
    biçimde çalışır; değişen yalnız KAYNAKTIR (input satır 485).
    """
    pool = motion_pool(context)
    if not pool:
        return None
    if isinstance(requested, str) and requested in pool:
        return requested
    logger.warning(
        "hareket seçimi havuzun üyesi değil, sunucu havuzdan seçiyor "
        "(package_id=%s sub_sector=%s istenen=%r)",
        context.package_id if context else None,
        context.sub_sector_slug if context else None,
        requested,
    )
    return random.choice(pool)


def special_day_visual_accent(
    context: SectorPackageContext | None, day_name: str | None
) -> str | None:
    """Eşleşen günün görsel vurgusu — GÖRSEL yüzeyine aittir (spec §4.3).

    Caption metnine giden dönem kalıplarından AYRI tutulur: `gorsel_vurgu`
    görsel director talimatına girer, `mesaj_ekseni`/`kanca`/`cta` metne. İkisi
    aynı yerden basılsaydı "görsel dağarcığı doğru yüzeyde" kontrolü (spec §5.4)
    anlamını yitirirdi.

    Eşleşme yoksa `None`. Burada log ÜRETİLMEZ: aynı gün için eşleşme uyarısını
    `render_special_day_lines` zaten basıyor ve iki yüzeyden iki kez uyarmak
    aynı olayı çift sayardı.
    """
    if context is None or not day_name:
        return None
    ozel_gun = context.content.get("ozel_gun")
    if not isinstance(ozel_gun, dict):
        return None
    try:
        key = normalize_special_day_key(day_name)
    except ValueError:
        return None
    entry = ozel_gun.get(key)
    if not isinstance(entry, dict):
        return None
    vurgu = entry.get("gorsel_vurgu")
    return vurgu if isinstance(vurgu, str) and vurgu.strip() else None


# ─── 6. K-07 damga tüketimi — kalıcı-kayıt ucu (plan Task 12) ───────────────


async def resolve_persist_stamp(
    db, brand: dict, generation_id, *, receipt_expected: bool = True
) -> tuple:
    """Kalıcı-kayıt anında yazılacak `(package_id, package_version)` çiftini verir.

    Sözleşme (K-07, bağlanan teknik karar 1):

    * Makbuz ATOMİK ve TEK-KULLANIMLIK tüketilir — koşullu güncelleme
      (`consumed_at IS NULL` + doğrulanmış marka). Eşzamanlı iki kayıt aynı
      makbuzla gelirse kazanan tektir; kaybeden satırı tüketilmiş bulur.
    * Kayıtlı çift AYNEN yazılır. Kayıt anında YENİDEN ÇÖZÜMLEME YOKTUR: içeriği
      üreten paket neyse damga odur.
    * Geçersiz / yabancı / başka markaya ait / zaten tüketilmiş makbuz → damga
      YAZILMAZ + `stamp_invalid`. Üretim bloklanmaz.
    * Makbuzsuz istek + marka paket yolunda + makbuz BEKLENİYORDUYSA →
      `stamp_missing`. `receipt_expected`, üretimin bir caption çağrısının
      ucunda olup olmadığını söyler; caption üretmeyen yollar (alıntı) için
      makbuz hiç doğmaz, yokluğu anomali DEĞİLDİR. Değer İSTEMCİNİN DÜŞÜREBİLECEĞİ
      bir alandan türetilemez: opsiyonel bir alanın yokluğu denetim izini
      susturmak için yeterli olurdu (fail-open). Çağıran onu içerik türü gibi
      akışı BELİRLEYEN, düşürülmesi akışı da bozan bir girdiden hesaplar ve
      bilinmeyen durumda BEKLENİR tarafına düşer.
    * Damganın paketi kayıt anında artık aktif değilse damga YİNE yazılır +
      `stamp_stale_at_persist`. Provenans dürüsttür: damgayı düşürmek üretimin
      gerçek kökenini silerdi, yeniden çözümlemek ise post'a onu üretmeyen bir
      paketi iliştirirdi.

    Bu fonksiyon kalıcı-kayıt transaction'ının İÇİNDEN çağrılmalıdır — tüketim
    ile post yazımı ayrı transaction'larda olursa makbuz tüketilip post
    yazılmayabilir (kayıp atıf) ya da tersi (çift atıf).
    """
    brand_id = brand.get("id")

    if generation_id is None:
        # Paketsiz marka için makbuzsuz istek NORMALDİR — olay üretmez.
        #
        # "Paket yolunda mı" sorusu `resolve_package_context` ile DEĞİL, doğrudan
        # sorguyla cevaplanır. Çözümleyici kendi olaylarını yazar; burada
        # çağrılsaydı paketi hiç KULLANMAYAN bir kayıt isteği (ör. görsel
        # üretimi) bayat-atama olayı üretirdi. O olayın anlamı "bir üretim yolu
        # paketi istedi ve alamadı"dır; kayıt ucu paketi istemez, yalnız
        # makbuzun beklenip beklenmediğini sorar.
        on_package_path = bool(
            brand.get("sub_sector_id")
            and await db.fetchval(
                "SELECT EXISTS (SELECT 1 FROM social.sector_packages "
                "WHERE sector_id = $1 AND status = 'active')",
                brand.get("sub_sector_id"),
            )
        )
        if on_package_path and receipt_expected:
            await _record_event(db, event_type="stamp_missing", brand_id=brand_id)
        return (None, None)

    row = await db.fetchrow(
        """
        UPDATE social.generation_stamps
        SET consumed_at = now()
        WHERE id = $1 AND brand_id = $2 AND consumed_at IS NULL
        RETURNING package_id, package_version
        """,
        generation_id,
        brand_id,
    )
    if row is None:
        await _record_event(db, event_type="stamp_invalid", brand_id=brand_id)
        return (None, None)

    package_id = row["package_id"]
    package_version = row["package_version"]

    # Bayatlık ölçümü DOĞRUDAN sorguyla yapılır, çözümleyiciyle DEĞİL:
    # `resolve_package_context` kendi olaylarını yazar ve burada çağrılsaydı tek
    # bir kayıt isteği iki olay üretirdi (bayat atama + bayat damga). Soru zaten
    # dar: bu makbuzun işaret ettiği sürüm hâlâ aktif mi.
    still_active = await db.fetchval(
        "SELECT status = 'active' FROM social.sector_packages WHERE id = $1 AND version = $2",
        package_id,
        package_version,
    )
    if not still_active:
        await _record_event(
            db,
            event_type="stamp_stale_at_persist",
            brand_id=brand_id,
            package_id=package_id,
            detail={"stamped_version": package_version},
        )

    return (package_id, package_version)
