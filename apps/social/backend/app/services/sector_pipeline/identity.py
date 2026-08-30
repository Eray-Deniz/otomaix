"""Kalıp kimliği + karar günlüğü şeması (Plan 2 Task 3, K-84 ailesi).

**İçerik şeması DEĞİŞMEZ; birim kümesi karar günlüğünden TÜRETİLİR.**

İlk yazım kimlikleri `content`'ten okumayı öngörüyordu. Ölçüldü ki bunun yeri
yok: `sector_packages.py::_check_cta_items` CTA öğesinin anahtar kümesini
`{kalip, tur, gerekce}` ile **eşitlik** olarak doğrular,
`_check_special_day_shapes` aynısını beş yuvayla yapar, `_check_field_shapes`
ise diğer liste öğelerini ve iki video havuzunu **düz metin** olmaya zorlar.
Yani içeriğe `unit_id` eklemek yazım kapısı tarafından REDDEDİLİR. Kimliği
yalnız karar günlüğüne yazmak da yetmezdi: kapsam kontrolü "aktif paketin HER
birimi" der, birim kümesi bir yerden TÜRETİLEBİLMELİDİR.

Bağlanan çözüm:

* Karar günlüğü satırı `unit_id` yanında **`oge_yolu`** (kimliğin ÇAPASI —
  kanonik yol, sıra ordinali dâhil) ve **`oge_sha`** (o öğenin kanonik hash'i)
  taşır. **Yalnız hash yetmez:** aynı listede iki özdeş metin AYNI hash'i
  taşır ve eşleme bire bir olmaz. Ayıran şey ordinaldir.
* **Yaşayan küme** = `koru` + `guncelle` + `ekle`. `kirp` ve `cikar` birimi
  kümeden DÜŞÜRÜR — kanonik kayıt: *"kırpma paketten çıkarır, kayıttan
  çıkarmaz"* (spec-input 1160). `kirp` yaşayan sayılsaydı her gerçek kırpma
  zorunlu olarak hayalet birim üretirdi.
* Bütünlük **iki yönlü** ölçülür: `enumerate_content_units(content)` yolları
  ile yaşayan satırların `oge_yolu` kümesi BİREBİR aynı olmalı (fazlası
  hayalet birim, eksiği sahipsiz öğe) **ve** her satırın `oge_sha`'sı o
  yoldaki öğenin taze hash'iyle eşleşmeli. Tek yönlü kontrol YETMEZ.
* `schema_version` ARTIRILMAZ, Plan 1 doğrulayıcısına DOKUNULMAZ.

**Bağımlılık yönü.** Bu modül Plan 1'in erişim katmanından (`sector_packages`)
yalnız OKUR: alan adları, yuva adları ve "anlamlı metin" ölçüsü orada TEK
yerde yaşar; buraya kopyalansaydı biri değişip diğeri kalırdı — Plan 1'in
K-01b'de kapattığı yazım/okuma ayrışmasının ta kendisi. Yaşam döngüsü modülü
(`sector_package_lifecycle`) buradan import eder; ters yön YOKTUR ve
yazılmayacaktır (döngü olurdu).
"""

from __future__ import annotations

import hashlib
import json
import re
import secrets
import unicodedata
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID

from app.services.sector_packages import (
    LIST_FIELDS,
    SPECIAL_DAY_SLOTS,
    TEXT_FIELDS,
    VIDEO_POOL_KEYS,
    _has_meaningful_text,
    structural_errors,
)

# ─── Kapalı değer kümeleri ──────────────────────────────────────────────────

# Kimlik biçimi bir KAPIDIR: kimlik metin özetinden türetilemez, dayatılır.
# Türetilseydi metnin her düzeltmesi kimliği değiştirir ve "aynı birim"
# ilişkisi sürümler arasında kopardı.
UNIT_ID_RE = re.compile(r"^ku-[0-9a-f]{12}$")

TUR_DEGERLERI = frozenset({"karar", "not"})

# BEŞ değer, kapalı. Altıncı değer EKLENMEZ (K-107): kısmi tür taşıması bir
# karar türü değil, `koru` satırının `kapsam` ek alanıdır.
KARAR_DEGERLERI = frozenset({"koru", "guncelle", "cikar", "ekle", "kirp"})

# Yeni paketin karar birimleri. `cikar` ve `kirp` kümeden DÜŞÜRÜR.
YASAYAN_KARARLAR = frozenset({"koru", "guncelle", "ekle"})

AKTOR_DEGERLERI = frozenset({"sentez", "motor", "insan"})

# İKİ değer, kapalı. `kismi-tur-tasima` bir not sınıfı DEĞİLDİR.
NOT_SINIFLARI = frozenset({"reddedilen-aday", "eslesmeyen-ozel-gun"})

# `koru` satırının ek alanı — K-107'nin doğru temsili.
KAPSAM_DEGERLERI = frozenset({"kismi-tur-tasima"})

# K-145 damgası: uygulanan karar satırının KENDİSİNDE yaşar. Yalnız
# `engine_diff`'e yazılsaydı üretici ile tüketici farklı artefaktlara bakardı
# ve sınıflandırma hiçbir zaman `kanitli` üretemezdi.
KURAL_DAMGA_ALANLARI = ("kural_kimligi", "kural_surumu")

_KARAR_ZORUNLU_ALANLAR = (
    "alan",
    "oge_yolu",
    "unit_id",
    "oge_sha",
    "karar",
    "gerekce",
    "kanit",
    "aktor",
)
_NOT_ZORUNLU_ALANLAR = ("sinif", "gerekce")

# Satır anahtar kümesi KAPALIDIR — tanınmayan alan sessizce taşınmaz. Şemayı
# genişletecek görev bu kümeyi bilerek büyütür; kaçak alan büyütmez.
_KARAR_ISTEGE_BAGLI = frozenset(KURAL_DAMGA_ALANLARI)
_NOT_ISTEGE_BAGLI = frozenset({"alan", "kanit"})

# `donmus`'un KAPALI skaler kümesi (R6(e), kural 4).
_DEGISMEZ_SKALERLER = (
    type(None),
    bool,
    int,
    float,
    str,
    bytes,
    Decimal,
    UUID,
    Path,
    datetime,
    date,
)


# ─── 1. Kimlik üretimi ──────────────────────────────────────────────────────


def new_unit_id() -> str:
    """`ku-` + 12 onaltılık, RASTGELE.

    İçerikten türetilmez: aynı metnin iki sektörde geçmesi kimlik çakışması
    üretirdi, metnin düzeltilmesi de kimliği koparırdı.
    """
    return "ku-" + secrets.token_hex(6)


# ─── 2. Kanonik hash (K-92) ─────────────────────────────────────────────────


def canonical_sha(value: Any) -> str:
    """K-92'nin kanonik hash kuralı: sıralı anahtar · boşluksuz · NFC.

    **Kural BURADA doğar.** Task 13'ün `engine.canonical_content_sha`'sı bunu
    ÇAĞIRIR, kendi kuralını yazmaz — iki kopya olsaydı biri anahtar sıralar
    diğeri sıralamaz, aynı içerik iki farklı hash alır ve sürüm karşılaştırması
    sessizce yalan söylerdi.

    NFC serileştirilmiş METNİN tamamına uygulanır. Bu, her dizeyi tek tek
    normalize etmekle EŞDEĞERDİR: JSON'da her dize ASCII tırnakla sınırlıdır
    ve birleşen bir işaret tırnakla birleşemez, yani sınır ötesi birleşme
    OLUŞAMAZ.

    JSON'a çevrilemeyen bir değer `TypeError` ile düşer (fail-closed) —
    "hash'i alınamadı, boş geç" dalı YOKTUR.
    """
    metin = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(
        unicodedata.normalize("NFC", metin).encode("utf-8")
    ).hexdigest()


# ─── 3. Kanonik yol grameri ─────────────────────────────────────────────────


def enumerate_content_units(content: dict) -> dict[str, dict]:
    """İçeriği kanonik YOLlarına ayırır: yol → birim kaydı.

    Gramer (Plan 1 doğrulayıcısının izin verdiği ŞEKİLLERDEN türetildi):

      * düz metin alanı        → ``kapsam``
      * liste öğesi            → ``kanca_kaliplari[0]``
      * video havuzu öğesi     → ``video_kodlar/hareket[0]``
      * özel gün yuvası        → ``ozel_gun/<anahtar>/kanca``

    **Sıra ordinali ZORUNLUDUR.** Aynı listede birebir aynı metin iki kez
    geçebilir; iki öğenin hash'i AYNIdır ve yalnız hash ile ayırt edilemezler
    (çokluk sorunu). Eşlemeyi bire bir yapan şey ordinaldir.

    Şekli bozuk alanlar (ör. liste yerine metin) hiç birim üretmez; onları
    yakalamak bu fonksiyonun değil Plan 1 yazım kapısının işidir ve
    `check_unit_integrity` o kapıyı ÖNCE koşturur.
    """
    if not isinstance(content, dict):
        raise TypeError(f"content nesne değil: {type(content).__name__}")

    units: dict[str, dict] = {}

    def kaydet(yol: str, alan: str, deger: Any) -> None:
        units[yol] = {
            "oge_yolu": yol,
            "alan": alan,
            "deger": deger,
            "oge_sha": canonical_sha(deger),
        }

    for name in TEXT_FIELDS:
        if name in content:
            kaydet(name, name, content[name])

    for name in LIST_FIELDS:
        deger = content.get(name)
        if isinstance(deger, list):
            for index, item in enumerate(deger):
                kaydet(f"{name}[{index}]", name, item)

    video = content.get("video_kodlar")
    if isinstance(video, dict):
        for havuz in VIDEO_POOL_KEYS:
            pool = video.get(havuz)
            if isinstance(pool, list):
                for index, item in enumerate(pool):
                    kaydet(f"video_kodlar/{havuz}[{index}]", "video_kodlar", item)

    ozel_gun = content.get("ozel_gun")
    if isinstance(ozel_gun, dict):
        # Anahtar sırası deterministik olsun: sözlük sırası girdi sırasına
        # bağlıdır, çıktı sırası ise iki koşumda aynı olmalı.
        for key in sorted(ozel_gun):
            entry = ozel_gun[key]
            if isinstance(entry, dict):
                for slot in SPECIAL_DAY_SLOTS:
                    if slot in entry:
                        kaydet(f"ozel_gun/{key}/{slot}", "ozel_gun", entry[slot])

    return units


# ─── 4. Karar günlüğü şeması ────────────────────────────────────────────────


def _require_meaningful(value: Any, label: str, errors: list[str]) -> None:
    """Alan ANLAMLI bir METİN mi — ölçü Plan 1 ile AYNI (`_has_meaningful_text`).

    Ayrı bir ölçü yazılsaydı yazım kapısından geçen bir değer burada hiçe
    inebilir ya da tersi olurdu; iki taraf aynı yüklemi çağırır.
    """
    if not isinstance(value, str):
        errors.append(f"{label} metin değil: {type(value).__name__}")
    elif not _has_meaningful_text(value):
        errors.append(f"{label} boş ya da yalnız noktalama")


def _validate_karar_row(
    row: dict, label: str, errors: list[str], gorulen: dict[str, int]
) -> None:
    karar = row.get("karar")

    izinli = set(_KARAR_ZORUNLU_ALANLAR) | _KARAR_ISTEGE_BAGLI | {"tur"}
    if karar == "ekle":
        # K-154: `cikar` + `ekle` çiftinin bağı YALNIZ `ekle` satırında yaşar.
        izinli.add("yerine_gecer")
    if karar == "koru":
        # K-107: kısmi tür taşımasının DOĞRU temsili.
        izinli.add("kapsam")
    bilinmeyen = sorted(set(row) - izinli)
    if bilinmeyen:
        errors.append(
            f"{label} şema dışı alan(lar): {bilinmeyen} — satır anahtar kümesi kapalıdır"
        )
    eksik = [name for name in _KARAR_ZORUNLU_ALANLAR if name not in row]
    if eksik:
        errors.append(f"{label} eksik alan(lar): {eksik}")

    if karar not in KARAR_DEGERLERI:
        errors.append(
            f"{label} karar değeri kapalı kümenin dışında: {karar!r} — "
            f"BEŞ değer: {sorted(KARAR_DEGERLERI)}"
        )

    aktor = row.get("aktor")
    if aktor not in AKTOR_DEGERLERI:
        errors.append(
            f"{label} aktor değeri kapalı kümenin dışında: {aktor!r} — "
            f"{sorted(AKTOR_DEGERLERI)}"
        )

    unit_id = row.get("unit_id")
    if not isinstance(unit_id, str) or not UNIT_ID_RE.match(unit_id):
        errors.append(
            f"{label} unit_id biçimi geçersiz: {unit_id!r} — 'ku-' + 12 onaltılık"
        )
    else:
        gorulen[unit_id] = gorulen.get(unit_id, 0) + 1
        if gorulen[unit_id] == 2:
            errors.append(
                f"aynı unit_id birden fazla karar satırı taşıyor: {unit_id!r} — "
                "bir birim bir günlükte TEK sonuç alır"
            )

    for name in ("alan", "oge_yolu", "oge_sha", "gerekce"):
        if name in row:
            _require_meaningful(row[name], f"{label}.{name}", errors)

    # `kanit` boş OLABİLİR (her karar dış kanıt istemez) ama METİN olmak
    # zorundadır; `cikar` ise POZİTİF kanıt olmadan GEÇERSİZDİR (spec §3.5).
    kanit = row.get("kanit")
    if "kanit" in row and not isinstance(kanit, str):
        errors.append(f"{label}.kanit metin değil: {type(kanit).__name__}")
    elif karar == "cikar" and not _has_meaningful_text(kanit):
        errors.append(
            f"{label} karar='cikar' satırı pozitif kanıt olmadan GEÇERSİZ (spec §3.5)"
        )

    if "kapsam" in row and row["kapsam"] not in KAPSAM_DEGERLERI:
        errors.append(
            f"{label} kapsam değeri kapalı kümenin dışında: {row['kapsam']!r} — "
            f"{sorted(KAPSAM_DEGERLERI)}"
        )

    if "yerine_gecer" in row:
        hedef = row["yerine_gecer"]
        if not isinstance(hedef, str) or not UNIT_ID_RE.match(hedef):
            errors.append(
                f"{label} yerine_gecer unit_id biçimi geçersiz: {hedef!r}"
            )

    damgalar = [
        name for name in KURAL_DAMGA_ALANLARI if _has_meaningful_text(row.get(name))
    ]
    if aktor == "motor":
        for name in KURAL_DAMGA_ALANLARI:
            if not _has_meaningful_text(row.get(name)):
                errors.append(
                    f"{label} aktor='motor' satırı {name} taşımak ZORUNDA (K-145) — "
                    "kural provenansı uygulanan kararın KENDİSİNDE yaşar"
                )
    elif damgalar:
        errors.append(
            f"{label} aktor={aktor!r} satırı kural damgası TAŞIYAMAZ: {damgalar} — "
            "damga yalnız motor kararının provenansıdır"
        )


def _validate_not_row(row: dict, label: str, errors: list[str]) -> None:
    izinli = set(_NOT_ZORUNLU_ALANLAR) | _NOT_ISTEGE_BAGLI | {"tur"}
    bilinmeyen = sorted(set(row) - izinli)
    if bilinmeyen:
        errors.append(
            f"{label} şema dışı alan(lar): {bilinmeyen} — satır anahtar kümesi kapalıdır"
        )
    eksik = [name for name in _NOT_ZORUNLU_ALANLAR if name not in row]
    if eksik:
        errors.append(f"{label} eksik alan(lar): {eksik}")

    sinif = row.get("sinif")
    if sinif == "kismi-tur-tasima":
        # Geçseydi doğrulayıcıdan ÇIKARdı ama motorun birim-başına kapsam
        # kontrolünü karşılamazdı — sessiz taşıma geri gelirdi.
        errors.append(
            f"{label} sinif='kismi-tur-tasima' bir not sınıfı DEĞİLDİR (K-107) — "
            "kısmi tür taşıması tur='karar', karar='koru' satırında "
            "kapsam='kismi-tur-tasima' ek alanıyla temsil edilir"
        )
    elif sinif not in NOT_SINIFLARI:
        errors.append(
            f"{label} sinif değeri kapalı kümenin dışında: {sinif!r} — "
            f"İKİ değer: {sorted(NOT_SINIFLARI)}"
        )

    if "gerekce" in row:
        _require_meaningful(row["gerekce"], f"{label}.gerekce", errors)


def validate_decision_log(rows: list[dict]) -> list[str]:
    """Karar günlüğü satırlarının ŞEMA kapısı — hata listesi döner (boş = geçti).

    Kapının kapattığı sınıflar tek tek: kapalı `tur`/`karar`/`aktor`/`sinif`
    kümeleri, kanıtsız `cikar`, aynı birimin iki kararı, biçimsiz `unit_id`,
    kural damgasının üretici-tüketici ayrışması (K-145) ve K-107'nin yanlış
    temsili.
    """
    if not isinstance(rows, list):
        return [f"karar günlüğü liste değil: {type(rows).__name__}"]

    errors: list[str] = []
    gorulen: dict[str, int] = {}
    for index, row in enumerate(rows):
        label = f"karar_gunlugu[{index}]"
        if not isinstance(row, dict):
            errors.append(f"{label} nesne değil: {type(row).__name__}")
            continue
        tur = row.get("tur")
        if tur not in TUR_DEGERLERI:
            errors.append(
                f"{label} tur değeri kapalı kümenin dışında: {tur!r} — "
                f"{sorted(TUR_DEGERLERI)}"
            )
            continue
        if tur == "karar":
            _validate_karar_row(row, label, errors, gorulen)
        else:
            _validate_not_row(row, label, errors)
    return errors


# ─── 5. Türetilmiş birim kümesi + bütünlük ──────────────────────────────────


def _yasayan_satirlar(decision_log: list[dict]):
    """`koru` + `guncelle` + `ekle` satırları — yaşayan küme."""
    for row in decision_log:
        if row.get("tur") == "karar" and row.get("karar") in YASAYAN_KARARLAR:
            yield row


def decision_units(content: dict, decision_log: list[dict]) -> dict[str, dict]:
    """Paketin karar birimleri: `unit_id` → birim kaydı.

    R6: bu fonksiyon **anlık görüntünün TEK üreticisidir** — Task 9'un
    `validate_report(unit_snapshot=...)` girdisi ve K-100 envanterinin
    dayanağı buradan gelir.

    Fail-closed: şemayı geçmeyen bir günlükten görüntü TÜRETİLMEZ (`ValueError`).
    Geçseydi bozuk bir günlükten üretilmiş "görüntü" sessizce denetçi zincirine
    akardı.

    Kapsam sınırı DÜRÜSTÇE: burası eşlemenin İÇERİKLE tutarlı olduğunu
    kanıtlamaz — o `check_unit_integrity`'nin işidir. İçerikte karşılığı
    olmayan bir yolun `deger`'i `None` gelir; çağıran ÖNCE bütünlük kapısını
    koşturur.
    """
    errors = validate_decision_log(decision_log)
    if errors:
        raise ValueError("karar günlüğü şemayı geçmedi: " + "; ".join(errors))

    units = enumerate_content_units(content)
    derived: dict[str, dict] = {}
    for row in _yasayan_satirlar(decision_log):
        yol = row["oge_yolu"]
        oge = units.get(yol)
        derived[row["unit_id"]] = {
            "unit_id": row["unit_id"],
            "alan": row["alan"],
            "oge_yolu": yol,
            "karar": row["karar"],
            "oge_sha": row["oge_sha"],
            "deger": oge["deger"] if oge is not None else None,
        }
    return derived


def check_unit_integrity(content: dict, decision_log: list[dict]) -> list[str]:
    """Eşleme GERÇEKTEN kapsayıcı mı — İKİ YÖNLÜ küme eşitliği + hash eşleşmesi.

    Üç kapı birden aranır ve hiçbiri diğerinin yerine geçmez:

      1. **günlük → içerik:** yaşayan her satırın yolu içerikte VAR (yoksa
         *hayalet birim*);
      2. **içerik → günlük:** içerikteki her yolu bir yaşayan satır sahiplenir
         (sahiplenmiyorsa *sahipsiz öğe* — kapsam kaçağı);
      3. her satırın `oge_sha`'sı o yoldaki öğenin TAZE hash'iyle eşleşir
         (eşleşmiyorsa *bayat oge_sha*).

    Tek yönlü bir kontrol (1) ya da (2)'den yalnız birini görür; ikisi de
    gerçek bir kaçak sınıfıdır. Eşleme ayrıca BİRE BİRDİR: iki yaşayan birim
    aynı yolu sahiplenemez — küme eşitliği bunu tek başına GÖREMEZ.

    Fail-closed: içerik yazım kapısını ya da günlük şema kapısını geçmiyorsa
    bütünlük ÖLÇÜLMEZ, o hatalar döner.
    """
    errors = list(structural_errors(content))
    errors.extend(validate_decision_log(decision_log))
    if errors:
        return errors

    units = enumerate_content_units(content)
    yasayan: dict[str, dict] = {}
    for row in _yasayan_satirlar(decision_log):
        yol = row["oge_yolu"]
        if yol in yasayan:
            errors.append(
                f"aynı yolu iki yaşayan birim sahipleniyor: {yol!r} — "
                f"{yasayan[yol]['unit_id']!r} ve {row['unit_id']!r}; eşleme BİRE BİRDİR"
            )
            continue
        yasayan[yol] = row

    for yol, row in yasayan.items():
        oge = units.get(yol)
        if oge is None:
            errors.append(
                f"hayalet birim: {row['unit_id']!r} — {yol!r} yolunun içerikte "
                "karşılığı YOK"
            )
        elif row["oge_sha"] != oge["oge_sha"]:
            errors.append(
                f"bayat oge_sha: {yol!r} — günlükte {row['oge_sha']}, "
                f"içerikte {oge['oge_sha']}"
            )

    for yol in sorted(units):
        if yol not in yasayan:
            errors.append(
                f"sahipsiz öğe: {yol!r} — hiçbir yaşayan karar satırı bu yolu "
                "sahiplenmiyor"
            )
    return errors


# ─── 6. Donmuş dataclass alanlarının TEK normalizasyon kuralı (R6(e)) ───────


def donmus(value: Any) -> Any:
    """Donmuş dataclass alanlarının TEK normalizasyon kuralı: derin, SALT-OKUNUR kopya.

    Kopya olduğu için çağıranın nesnesiyle takma ad PAYLAŞMAZ; salt-okunur
    olduğu için yapımdan sonra içi değiştirilemez. `frozen=True` yalnız alanın
    YENİDEN ATANMASINI engeller, tuttuğu listenin İÇİNİ değil — yasak hâl
    yapımdan SONRA geri kurulabiliyordu.

    Dönüşüm KÜMESİ KAPALIDIR — BEŞ kural, altıncısı YOKTUR:

      (1) `Mapping`           → `MappingProxyType`(anahtarları sıralı YENİ
                                `dict`; her değer özyinelemeli `donmus`)
      (2) `list` | `tuple`    → `tuple`(her öğe özyinelemeli `donmus`)
      (3) `set` | `frozenset` → `frozenset`(her öğe özyinelemeli `donmus`)
      (4) değişmez skaler     → OLDUĞU GİBİ döner (kapalı liste:
                                `None` · `bool` · `int` · `float` · `str` ·
                                `bytes` · `Decimal` · `UUID` · `Path` ·
                                `datetime` · `date`)
      (5) bu dördünün DIŞINDA her şey → `TypeError` (fail-closed; sessiz
                                geçiş YOK)

    `donmus(donmus(x))` ile `donmus(x)` AYNI değeri verir (idempotent).

    **Donmuş dataclass öğesi kuralın DIŞINDADIR** ve kural 5 ile düşer: öğeleri
    donmuş dataclass olan alanlar `tuple(...)` kopyası + `type(öge) is <Sınıf>`
    kontrolüyle korunur, `donmus`'a VERİLMEZ. İkinci bir normalizasyon kuralı
    YAZILMAZ.
    """
    if isinstance(value, _DEGISMEZ_SKALERLER):
        return value
    if isinstance(value, Mapping):
        return MappingProxyType({key: donmus(value[key]) for key in sorted(value)})
    if isinstance(value, (list, tuple)):
        return tuple(donmus(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(donmus(item) for item in value)
    raise TypeError(
        f"donmus kapalı kümenin dışında bir tip aldı: {type(value).__name__} — "
        "eşleme · dizi · küme · değişmez skaler dışına sessiz geçiş YOKTUR"
    )
