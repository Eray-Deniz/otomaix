"""Kalıp kimliği + karar günlüğü şeması (Plan 2 Task 3, K-84 ailesi).

**İçerik şeması DEĞİŞMEZ; birim kümesi karar günlüğünden TÜRETİLİR.**

İlk yazım kimlikleri `content`'ten okumayı öngörüyordu. Ölçüldü ki bunun yeri
yok: `sector_content_schema.py::_check_cta_items` CTA öğesinin anahtar kümesini
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

**Bağımlılık yönü.** Bu modül alan adlarını, yuva adlarını, "anlamlı metin"
ölçüsünü ve yapısal yazım kapısını ortak YAPRAK modülden (`sector_content_schema`)
okur. Ölçü TEK yerde yaşar; buraya kopyalansaydı biri değişip diğeri kalırdı —
Plan 1'in K-01b'de kapattığı yazım/okuma ayrışmasının ta kendisi.

Kural daha önce Plan 1'in erişim katmanında (`sector_packages`) yaşıyordu ve
buradan oraya bir import kenarı vardı. Plan 2 arayüz eki
(`docs/plans/2026-08-27-sektor-bilgi-paketi-plan2-arayuz-eki.md`, satır 1476-1477)
bunu yasaklar: *"`identity.py` hiçbir Plan 1 modülünü ve hiçbir DB yüzeyini
IMPORT ETMEZ"*. Kural yaprağa taşındı; iki taraf da yapraktan tüketir, kopya YOK.
Kapısı yapısal testtir
(`tests/test_plan2_interface_contract.py::test_identity_imports_no_plan1_module_and_no_db_surface`).

Yaşam döngüsü modülü (`sector_package_lifecycle`) buradan import eder; ters yön
YOKTUR ve yazılmayacaktır (döngü olurdu).
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import re
import secrets
import sys
import unicodedata
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping
from uuid import UUID

from app.services.sector_content_schema import (
    LIST_FIELDS,
    SPECIAL_DAY_SLOTS,
    TEXT_FIELDS,
    VIDEO_POOL_KEYS,
    has_meaningful_text,
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

# ── İKİ kapalı küme, İKİ AYRI soru — bilinçli olarak BİRLEŞTİRİLMEDİ ───────
#
# Aşağıdaki `_DEGISMEZ_SKALERLER` (R6(e), `donmus`) şunu sorar: *"bu değer olduğu
# gibi döndürülebilir mi, yani yapımından sonra İÇİ değiştirilebilir mi?"* Cevabı
# değişmezliktir; `bytes` orada VARDIR çünkü değişmezdir.
#
# `canonical_sha`'nın ön-serileştirme kuralı (aşağıda, bölüm 2) BAŞKA bir şey sorar:
# *"bu değerin DETERMİNİSTİK bir JSON metni var mı?"* İki küme çakışır ama eşit
# DEĞİLDİR ve eşitlenirlerse iki yönde de zarar verirler:
#   * `bytes` değişmezdir ama JSON'da bayt dizisi YOKTUR — bir kodlama seçmek ikinci
#     bir normalizasyon kuralı yazmak olurdu, o yüzden hash onu REDDEDER;
#   * `float` değişmezdir ama `nan`/`inf` DEĞERLERİ geçerli JSON değildir — hash
#     tipi değil o değerleri reddeder;
#   * donmuş bir veri sınıfı örneği `donmus`'un kümesinde YOKTUR (kural 5 düşürür)
#     ama kanonik JSON karşılığı vardır (alan adı → değer) ve hash onu KABUL EDER.
# Kümeler birleştirilseydi ya `donmus` deterministik olmayan bir değeri kabul eder,
# ya hash değişmez bir değeri gereksiz yere reddederdi.

# `canonical_sha`'nın METNE çevirdiği skalerler — her birinin TEK kanonik yazımı var.
_METNE_CEVRILEN_SKALERLER = (UUID, Path, Decimal)

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


def _kanonik_json_degeri(value: Any) -> Any:
    """`canonical_sha`'nın ÖN-SERİLEŞTİRME kuralı — KAPALI küme, fail-closed.

    `json.dumps` tek başına yetmiyordu: kural iki girdi sınıfına BAĞLIDIR ve ikisi
    de düz `json.dumps`'tan `TypeError` ile düşerdi — donmuş veri sınıfı örnekleri
    (arayüz eki satır 1901: `MADDE_KUMESI_SHA: str = identity.canonical_sha(MADDELER)`,
    `MADDELER` donmuş `ChecklistItem` demeti) ve `UUID` alanı taşıyan kanıt yükleri
    (aynı ek, satır 1450-1464). Bu fonksiyon o girdileri JSON'un anlayacağı kanonik
    karşılıklarına çevirir; kural TEK yerdedir, ikinci bir hash kuralı YAZILMAZ.

    Dönüşüm kümesi KAPALIDIR:

      (1) `None` · `bool` · `str` · `int`    → OLDUĞU GİBİ (tamsayı için
                                               büyüklük sınırı SÜREÇ ayarıdır,
                                               bkz. `canonical_sha`)
      (2) `float`                            → OLDUĞU GİBİ, ama SONLU olmak zorunda
      (3) `UUID` · `Path` · `Decimal`        → `str(...)`
      (4) `datetime` · `date`                → `isoformat()`
      (5) donmuş veri sınıfı örneği          → {alan adı: kural(değer)}
      (6) `Mapping`                          → {anahtar: kural(değer)}
      (7) `list` · `tuple`                   → [kural(öğe), ...]
      (8) bunların DIŞINDA her şey           → `TypeError` (fail-closed)

    Üç sınır bilerek dar tutuldu:

    * **Sonlu olmayan FLOAT REDDEDİLİR.** `json.dumps` `nan`/`inf` için varsayılan
      olarak `NaN`/`Infinity` yazar; bu geçerli JSON DEĞİLDİR ve hash sessizce
      taşınmaz hâle gelirdi. Ölçü YALNIZ `float`'a uygulanır: `math.isfinite`
      argümanını float'a çevirir, dolayısıyla tamsayıya uygulanması `10**309`'u
      `OverflowError` ile düşürürdü — hem eski özeti (`7fe8362b13128003…`)
      hesaplanamaz kılan hem de aşağıdaki `TypeError` vaadini kıran bir gerileme
      (fix turu 2, F1). Python tamsayısı sonsuz OLAMAZ; ölçülecek bir şey yoktur.
    * **Küme (`set`/`frozenset`) REDDEDİLİR.** Kümenin sırası yoktur; bir sıralama
      seçmek ikinci bir normalizasyon kuralı yazmak olurdu. Çağıran sıralı bir
      diziye kendisi çevirir ve o sıranın sorumluluğunu üstlenir.
    * **Donmamış veri sınıfı REDDEDİLİR.** Hash'lendikten sonra içi değişebilen bir
      nesnenin parmak izi, temsil ettiği şeye bağlı kalmaz.

    Veri sınıfının ADI kanonik diziye GİRMEZ: sınıf kimliğine ihtiyaç duyan çağıran
    onu kendi yüküne yazar (arayüz eki satır 1451-1453 `_evidence_fingerprint`'i tam
    olarak böyle tarif eder: "SINIF ADI + (alan adı, değer) çiftleri"). Burada
    yazılsaydı o yükte iki kez görünürdü.

    **Anahtarlara DOKUNULMAZ.** Eşleme anahtarları `json.dumps`'a olduğu gibi geçer;
    böylece bugün çalışan girdilerin ürettiği hash BİREBİR korunur ve anahtar tipi
    için ikinci bir kural doğmaz — JSON'un kabul etmediği bir anahtar yine
    `TypeError` ile düşer.
    """
    if value is None or isinstance(value, (bool, str)):
        return value
    if isinstance(value, int):
        # Tamsayı OLDUĞU GİBİ geçer — sonluluk ÖLÇÜLMEZ. `int` ve `float` ortak
        # bir dalda toplanıp `math.isfinite`'a verilseydi (fix turu 1'in yazımı)
        # argüman float'a çevrilirdi ve `10**309` `OverflowError` ile patlardı:
        # eski kural o değer için özet ÜRETİYORDU (`7fe8362b13128003…`) ve
        # `OverflowError` docstring'in vadettiği `TypeError` DEĞİLDİR. Python
        # tamsayısı zaten sonsuz olamaz; ölçülecek bir şey yoktu.
        #
        # Büyüklük yine de SINIRSIZ DEĞİLDİR ve sınır BURADA yaşamaz: Python'un
        # süreç düzeyindeki ondalık dönüşüm sınırını (`sys.get_int_max_str_digits()`)
        # aşan tamsayı `json.dumps` içinde metne çevrilemez. O yolun istisna
        # SINIFINI sözleşmeye uyduran yer `canonical_sha`'dır.
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise TypeError(
                f"canonical_sha sonlu olmayan sayı aldı: {value!r} — `NaN`/`Infinity` "
                "geçerli JSON değildir, hash sessizce taşınmaz olurdu"
            )
        return value
    if isinstance(value, _METNE_CEVRILEN_SKALERLER):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        if not value.__dataclass_params__.frozen:
            raise TypeError(
                f"canonical_sha donmamış veri sınıfı aldı: {type(value).__name__} — "
                "hash'lendikten sonra içi değişebilen nesnenin parmak izi bağlayıcı "
                "değildir"
            )
        return {
            alan.name: _kanonik_json_degeri(getattr(value, alan.name))
            for alan in dataclasses.fields(value)
        }
    if isinstance(value, Mapping):
        return {key: _kanonik_json_degeri(value[key]) for key in value}
    if isinstance(value, (list, tuple)):
        return [_kanonik_json_degeri(item) for item in value]
    raise TypeError(
        f"canonical_sha kapalı kümenin dışında bir tip aldı: {type(value).__name__} — "
        "deterministik JSON karşılığı olmayan değere sessiz geçiş YOKTUR"
    )


def canonical_sha(value: Any) -> str:
    """K-92'nin kanonik hash kuralı: sıralı anahtar · boşluksuz · NFC.

    **Kural BURADA doğar.** Task 13'ün `engine.canonical_content_sha`'sı bunu
    ÇAĞIRIR, kendi kuralını yazmaz — iki kopya olsaydı biri anahtar sıralar
    diğeri sıralamaz, aynı içerik iki farklı hash alır ve sürüm karşılaştırması
    sessizce yalan söylerdi.

    Değer önce `_kanonik_json_degeri`'nin KAPALI ön-serileştirme kuralından geçer
    (donmuş veri sınıfı · `UUID` · `Path` · `Decimal` · `date` · `datetime`), sonra
    `json.dumps`'a verilir. Ön-serileştirme düz sözlük · dize · sayı · iç içe liste
    girdilerini DEĞİŞTİRMEZ, dolayısıyla mevcut hash değerleri birebir korunur
    (`test_canonical_sha_keeps_existing_digests_byte_for_byte` bunu pinler).

    NFC serileştirilmiş METNİN tamamına uygulanır. Bu, her dizeyi tek tek
    normalize etmekle EŞDEĞERDİR: JSON'da her dize ASCII tırnakla sınırlıdır
    ve birleşen bir işaret tırnakla birleşemez, yani sınır ötesi birleşme
    OLUŞAMAZ.

    JSON'a çevrilemeyen bir değer `TypeError` ile düşer (fail-closed) —
    "hash'i alınamadı, boş geç" dalı YOKTUR. Ön-serileştirme bu vaadi GENİŞLETMEZ:
    kapalı kümenin dışı yine `TypeError`'dır, yalnız hata artık kuralın kendisinden
    gelir.

    **Tamsayı büyüklüğü sınırsız DEĞİLDİR** ve bu vaadin ikinci yarısı oradadır:
    Python'un süreç düzeyindeki ondalık dönüşüm sınırını
    (`sys.get_int_max_str_digits()`, ölçüldü: 3.12.3'te 4300 basamak) aşan bir
    tamsayı `json.dumps` içinde `ValueError` ile düşer. `ValueError` `TypeError`
    DEĞİLDİR; sözleşme tek istisna sınıfı söz verdiği için o hata burada
    `TypeError`'a ÇEVRİLİR. Sınırın kendisi CPU/bellek korumasıdır ve
    YÜKSELTİLMEZ — `sys.set_int_max_str_digits` çağrılsaydı vaat tutar ama yeni
    bir tehlike açılırdı.
    """
    try:
        metin = json.dumps(
            _kanonik_json_degeri(value),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
    except ValueError as exc:
        # Ön-serileştirmeden geçen ağaç yalnız düz JSON tiplerinden oluşur;
        # bu yolda ÖLÇÜLEN tek `ValueError` sebebi tamsayı ondalık dönüşüm
        # sınırıdır. Sebep yine de tahmin edilmez: özgün hata metni olduğu gibi
        # taşınır, değişen tek şey istisna SINIFIDIR.
        raise TypeError(
            f"canonical_sha kanonik JSON metni üretemedi: {exc} — bu yolda "
            "bilinen tek sebep tamsayının süreç düzeyindeki ondalık dönüşüm "
            f"sınırını (`sys.get_int_max_str_digits()` = "
            f"{sys.get_int_max_str_digits()} basamak) aşmasıdır; sınır "
            "CPU/bellek korumasıdır ve hash onu YÜKSELTMEZ"
        ) from exc
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
    """Alan ANLAMLI bir METİN mi — ölçü Plan 1 ile AYNI (`has_meaningful_text`).

    Ayrı bir ölçü yazılsaydı yazım kapısından geçen bir değer burada hiçe
    inebilir ya da tersi olurdu; iki taraf aynı yüklemi çağırır.
    """
    if not isinstance(value, str):
        errors.append(f"{label} metin değil: {type(value).__name__}")
    elif not has_meaningful_text(value):
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
    elif karar == "cikar" and not has_meaningful_text(kanit):
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
        name for name in KURAL_DAMGA_ALANLARI if has_meaningful_text(row.get(name))
    ]
    if aktor == "motor":
        for name in KURAL_DAMGA_ALANLARI:
            if not has_meaningful_text(row.get(name)):
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

    Fail-closed İÇERİK konusunda da (fix turu 1, F2): bütünlük kapısını
    geçmeyen bir çiftten görüntü TÜRETİLMEZ. Önceki yazım hayalet yolu
    `deger=None` ile sessizce geçiriyor ve yükümlülüğü docstring'de çağırana
    devrediyordu — yani kapı değil RİCA idi. Üretici ile tüketicinin farklı
    şeye bakması K-145'in saldırdığı sınıfın ta kendisidir.
    """
    # Üç kapı, ÜÇ AYRI mesaj: düşen kapının adı hata metninden okunabilmeli.
    # Hepsi tek başlık altında toplansaydı bozuk bir içerik "günlük tutarsız"
    # diye anılırdı ve okuyucu yanlış artefaktı incelerdi.
    errors = structural_errors(content)
    if errors:
        raise ValueError("içerik yazım kapısını geçmedi: " + "; ".join(errors))
    errors = validate_decision_log(decision_log)
    if errors:
        raise ValueError("karar günlüğü şemayı geçmedi: " + "; ".join(errors))
    errors = check_unit_integrity(content, decision_log)
    if errors:
        raise ValueError("içerik ile karar günlüğü tutarsız: " + "; ".join(errors))

    units = enumerate_content_units(content)
    derived: dict[str, dict] = {}
    for row in _yasayan_satirlar(decision_log):
        yol = row["oge_yolu"]
        # Bütünlük kapısı yukarıda geçtiği için yol MUTLAKA vardır ve
        # satırın `alan`'ı öğenin alanıyla uzlaşmıştır.
        oge = units[yol]
        derived[row["unit_id"]] = {
            "unit_id": row["unit_id"],
            "alan": row["alan"],
            "oge_yolu": yol,
            "karar": row["karar"],
            "oge_sha": row["oge_sha"],
            "deger": oge["deger"],
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
            continue
        # `alan` zorunlu, dışa verilen ve `decision_units`'in denetçi anlık
        # görüntüsüne KOPYALADIĞI bir alandır. Yolla uzlaştırılmazsa satır bir
        # alanı iddia edip başkasının yolunu sahiplenebilir; uyuşmazlık her
        # kapıdan geçip envantere olduğu gibi akardı (fix turu 1, F3).
        if row["alan"] != oge["alan"]:
            errors.append(
                f"alan uyuşmazlığı: {yol!r} yolu {oge['alan']!r} alanına ait, "
                f"satır {row['alan']!r} diyor ({row['unit_id']!r})"
            )
        if row["oge_sha"] != oge["oge_sha"]:
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
        try:
            anahtarlar = sorted(value)
        except TypeError as exc:
            # Mesaj KURALIN kendisinden gelsin: `sorted`'ın iç hatası
            # ("'<' not supported...") okuyucuya hangi kuralın düştüğünü
            # söylemiyordu.
            raise TypeError(
                "donmus eşleme anahtarları karşılaştırılamıyor: "
                f"{sorted(type(key).__name__ for key in value)} — sıralı "
                "kanonik kopya üretilemez"
            ) from exc
        return MappingProxyType({key: donmus(value[key]) for key in anahtarlar})
    if isinstance(value, (list, tuple)):
        return tuple(donmus(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(donmus(item) for item in value)
    raise TypeError(
        f"donmus kapalı kümenin dışında bir tip aldı: {type(value).__name__} — "
        "eşleme · dizi · küme · değişmez skaler dışına sessiz geçiş YOKTUR"
    )
