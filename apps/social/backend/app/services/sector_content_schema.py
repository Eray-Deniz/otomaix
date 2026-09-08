"""Paket içeriğinin ŞEMASI ve dış girdi GEREKTİRMEYEN yazım kapısı — YAPRAK modül.

**Neden ayrı bir modül (bağımlılık yönü).** Alan adları, yuva adları, kapalı kanal
anahtar uzayı, "anlamlı metin" ölçüsü ve yapısal kapının kendisi TEK yerde yaşamak
zorundadır: Plan 1'in erişim katmanı (`sector_packages`) yazarken, Plan 2'nin kimlik
katmanı (`sector_pipeline.identity`) okurken AYNI ölçüyü uygular. Kopyalansaydı biri
değişip diğeri kalırdı — K-01b'de kapatılan yazım/okuma ayrışmasının ta kendisi.

Kural daha önce `sector_packages` içinde yaşıyordu ve `identity` oradan import ediyordu;
bu, `identity`'nin bir Plan 1 modülüne bağlanması demekti. Plan 2 arayüz eki
(`docs/plans/2026-08-27-sektor-bilgi-paketi-plan2-arayuz-eki.md`, satır 1509-1510 — 2026-09-08 revizyonundan sonra)
bunu açıkça yasaklar: *"`identity.py` hiçbir Plan 1 modülünü ve hiçbir DB yüzeyini
IMPORT ETMEZ"*. Çözüm kopya DEĞİL, ortak yapraktır: kural buraya taşındı, iki taraf da
buradan tüketir.

**Bu modül YAPRAKTIR ve öyle kalır:** hiçbir `app.*` modülünü ve hiçbir DB yüzeyini
import etmez — yalnız standart kitaplık. Kapısı yapısal testtir
(`tests/test_plan2_interface_contract.py::test_the_leaf_is_actually_a_leaf`).
"""

from __future__ import annotations

import re
import unicodedata
from typing import Any


# ─── Kapalı değer kümeleri ──────────────────────────────────────────────────

# `_normalize_slug`'ın Türkçe harf tablosuyla AYNI küme. Burada yalnız "bu ad
# normalize edildikten sonra geriye harf/rakam kalıyor mu" sorusuna bakılır.
_TR_ASCII = str.maketrans(
    {
        "ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u",
        "Ç": "c", "Ğ": "g", "İ": "i", "Ö": "o", "Ş": "s", "Ü": "u",
    }
)

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
#
# Anahtarlar TEK yerde adlandırılır: yazım kapısı (`VIDEO_POOL_KEYS`) ile okuma
# tarafı (`MOTION_POOL_KEY` / `SCENE_POOL_KEY`) aynı dizeleri iki ayrı yerde
# taşısaydı, birinin değişip diğerinin kalması tam da yukarıda kapatılan
# yazım/okuma ayrışmasını geri açardı.
MOTION_POOL_KEY = "hareket"
SCENE_POOL_KEY = "sahne"
VIDEO_POOL_KEYS = (MOTION_POOL_KEY, SCENE_POOL_KEY)

# `cta_kaliplari` öğesinin TAM anahtar kümesi (spec §3.4: {kalıp, tür, gerekçe}).
CTA_ITEM_KEYS = frozenset({"kalip", "tur", "gerekce"})

# `ozel_gun` girdisinin taşıdığı alanlar (spec §3.4 tablosu).
SPECIAL_DAY_SLOTS = ("tur", "mesaj_ekseni", "kanca", "cta", "gorsel_vurgu")


# Anahtar uzayı KAPALIDIR ve `[kanal-bağımlı: X]` etiketinin X uzayıyla birebir
# aynıdır. Serbest X değeri deterministik filtreyi imkânsız kılar (spec §12.2).
CHANNEL_KEYS = frozenset(
    {"whatsapp_hatti", "fiziksel_magaza", "randevu_sistemi", "eticaret_sitesi"}
)

# Unicode kategorisi `Pd` (dash punctuation) DIŞINDA kalan, gözle tire okunan
# işaretler. `−` matematiksel eksi (Sm), `⁃` madde-işareti tire (Po), `˗`
# değiştirici eksi (Sk), `➖` ağır eksi (So).
_DASH_LOOKALIKES = frozenset({"−", "⁃", "˗", "➖"})


# ─── Yapısal yazım kapısı ───────────────────────────────────────────────────


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

    **PUBLIC (Plan 2 fix turu 1).** Bu yüklem artık modül dışından da
    çağrılıyor (`sector_pipeline.identity` karar günlüğü alanlarını AYNI
    ölçüyle sınar); alt çizgili ad "modül içi" diye yalan söylüyordu. Özel
    takma ad aşağıda korunuyor, çağrı yerleri kırılmıyor.

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


# Geriye uyum: modül içi çağrı yerleri (ve onları çiviyen testler) bu adı
# kullanmaya devam eder.
_has_meaningful_text = has_meaningful_text


def _require_text(value: Any, label: str, errors: list[str]) -> None:
    """Yaprak ANLAMLI bir METİN mi.

    `içerik-önerilmez` (K-120) geçerli sayılır — "bilinçli boş" ile
    "doldurulmamış" aynı değer olsaydı eksik iş dolu görünürdü. Mantıksal ve
    sayısal değerler metin DEĞİLDİR: `False`/`0` eskiden "dolu" sayılıyordu.
    Yalnız noktalamadan oluşan değerler de içerik DEĞİLDİR (bkz.
    `_has_meaningful_text`).
    """
    if not isinstance(value, str):
        errors.append(f"{label} metin değil: {type(value).__name__}")
    elif not _has_meaningful_text(value):
        errors.append(
            f"{label} boş ya da yalnız noktalama — bilinçli boş bırakılacaksa "
            f"{DELIBERATELY_EMPTY!r} yazılır"
        )


# ─── Metin kanonikleştirme (yazım kapısının ve okuma tarafının ORTAK ölçüsü) ─


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
