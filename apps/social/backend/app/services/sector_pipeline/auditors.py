"""Denetçi girdi paketleyicisi — körlük · biçim kapısı · veri kapısı · ön kontrol.

Plan 2 Task 9 (K-14 · K-79 · K-81 · K-100 · K-137). Arayüz eki R5 · R6 bağlar;
çelişkide EK GEÇERLİDİR.

Bu modülün dört yüzeyi vardır ve dördü de FAIL-CLOSED'dur:

* `build_packet` — iki denetçiye giden **bayt-özdeş** girdi kopyasını kurar
  (K-79). İlk işi `contracts.require_pinned_text`'tir: sözleşme v2 pinden
  sapmışsa paket KURULMAZ (arayüz eki M1 sıra kapısı) ve pakete YALNIZ o
  çağrının doğruladığı baytlar yazılır — sözleşme dosyası ikinci kez okunmaz.
  Kaynaklar `KAYNAK-1/2/3` olarak kör adlandırılır; brief-doctor raporunun
  `kaynak_adi`'sı pakete HİÇ yazılmaz.
* `anonymize` — K-137'nin kod düzeyindeki ayağı. Pakete yazılan HER bayt bundan
  geçer: görev metni, brief, ham kaynaklar, EK-E ve EK-H dâhil. **Vaadin ölçülen
  hâli:** `ARAC_KIMLIKLERI`'nin YAPILANDIRILMIŞ, pinlenmiş kümesinde adı geçen
  kimlikler maskelenir. "Her araç kimliği" DEĞİL — küme kapalıdır ve iki ad
  bilerek dışındadır (aşağıda `ARAC_KIMLIKLERI` beyanı). Serbest metinde geçen
  bir kimliğin YOKLUĞU bu katmanda kanıtlanamaz; kanıtlanan, kümenin
  maskelendiğidir.
* `validate_report` — K-81 **biçim** kapısı ile K-100 **veri** kapısı. İkisi
  ayrıdır: "beş bölüm var mı" bölüm-VARLIĞI kontrolüdür ve eksik bir envanteri
  görmez; eksik envanter motorun mutabakat kapısına "uyum" gibi görünürdü.
  Dönüş tipi arayüz eki R6(a) gereği `ValidatedReport`'tur — plan 1170'in
  `list[str]` yazımı GEÇERSİZDİR.
* `preflight` — K-14. Dönüş `PreflightDurumu`'nun KAPALI kümesindendir ve üç
  başarısızlık AYRIDIR (`OLCULMEDI` · `ERISIM_YOK` · `OLCUM_ARIZASI`): üçü de
  turu BAŞLATMAZ, ama ortam-kısıtı muafiyetini YALNIZ `ERISIM_YOK`
  meşrulaştırır. "Ölçmedim" ile "ölçtüm, erişim yok" aynı yetkiyi veremez.

**Kapsam sınırı (dürüst etiket, arayüz eki R6(c)).** Çapraz denetçi mutabakatı
(iki raporun AYNI anlık görüntüye karşı yazılmış olması) BURADA YAPILMAZ —
`validate_report` tek rapor görür ve tek rapor iki raporun mutabakatını
kanıtlayamaz. O kapı tur seviyesindedir (Task 10: `check_snapshot_agreement`,
`ValidatedAuditPair`, `SnapshotAgreement`).

**Bağımlılık yönü.** Anlık görüntünün TEK üreticisi `identity.decision_units`
(Task 3); kanonik hash kuralı `identity.canonical_sha`; donmuş alan
normalizasyonu `identity.donmus`. `run_id` şekil kapısı ve dış depo kökü Task
8'in `runs` modülünden ÇAĞRILIR, burada kopyalanmaz — iki kopya olsaydı biri
değişip diğeri kalırdı.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Mapping, Protocol, Sequence
from uuid import UUID

from app.services.sector_pipeline import contracts, identity, runs
from app.services.sector_pipeline.brief_doctor import (
    DoctorReport,
    kaynak_seti_sha,
    kimlik_bolumlemesi,
)
from app.services.sector_pipeline.runs import (
    ARASTIRMA_DEPOSU_KOKU as _DEPO_KOKU,
    _require_run_id as require_run_id,
)

# ─── Kapalı değer kümeleri ──────────────────────────────────────────────────

STATU_DEGERLERI: tuple[str, ...] = (
    "supported",
    "not_observed",
    "needs_update",
    "contradicted",
    "risk_unverified",
)
"""K-100 statü uzayı — KAPALI, beş değer.

Kaynak: pinlenmiş `hakem-denetci-gorevi.md`, "STATÜ UZAYI KAPALIDIR — beş
değer, aynen bu yazımla". Test o bloktan ölçer; burada UYDURULMAZ.
"""

DENETCI_ROLLERI: tuple[str, ...] = ("denetci-1", "denetci-2")
"""Denetçi ROL adları — KAPALI. Rol adıdır, ARAÇ adı DEĞİL (K-137).

Hangi rolün hangi araçla koşturulduğu operatörde kalır ve pakete GİRMEZ.
"""

ONERI_DEGERLERI: tuple[str, ...] = ("al", "uyarla", "alma", "açık-soru")

EKLEMEYE_IZIN_VEREN_ONERILER: tuple[str, ...] = ("al", "uyarla")
"""`ONERI_DEGERLERI`'nin yeni öğe EKLEMEYE izin veren ALT KÜMESİ.

`alma` ve `açık-soru` dışarıda kalır ve bu sözleşmenin kendi anlamıdır: denetçi
o satırda kalıbın alınmamasını ya da insana sorulmasını önermiştir. Küme burada
ADLANDIRILIR ki motor `oneri` değerlerini serbestçe yorumlamasın — tüketici
`engine._yeni_oge_cogunlugu`'dur.
"""
"""DENETİM TABLOSU `öneri` sütunu — KAPALI, dört değer.

Kaynak: pinlenmiş `hakem-denetci-gorevi.md`, ADIM 2'nin `ÖNERİ:` satırı.
Test o satırdan ölçer; burada UYDURULMAZ (İlke 9).
"""

SINIF_TEKIL = "tekil"
SINIF_CELISKI = "çelişki"
"""`sınıf` sütununun İKİ ADLI değeri — geri kalanı ORAN yazımıdır.

**Sözlük KAPALI DEĞİLDİR ve bu ölçüldü.** Sözleşme ADIM 2 elemeden sonra
oranı kalan kaynak sayısına uyarlatır (*"iki kaynakla: 2-2, 1-2"*), yani
geçerli oran kümesi koşuya göre değişir. Bu yüzden yapısal çoğunluk oran
ETİKETİNDEN sayılmaz — `kaynaklar` sütunundaki NUMARALARDAN sayılır; oran
yalnız o numaralara karşı çapraz kontrol edilir.
"""

_SINIF_ORAN_RE = re.compile(r"^([1-9]\d*)-([1-9]\d*)$")

BOLUM_ANAHTARLARI: tuple[str, ...] = (
    "DENETİM TABLOSU",
    "URL ÖRNEKLEM SONUCU",
    "KAYNAK PROFİLİ",
    "AÇIK SORU ÖNERİLERİ",
    "YENİDEN DOĞRULAMA ENVANTERİ",
)
"""K-81 biçim kapısının beş bölümü — SIRA sözleşmenin sırasıdır.

**Değerler ÖLÇÜLDÜ, uydurulmadı (İlke 9).** Pinlenmiş
`hakem-denetci-gorevi.md`'nin çıktı sözleşmesi başlıklarından çıkarıldı;
ölçüm komutu ve taze çıktısı Task 9'un commit mesajındadır. "Beş" sayısı da
tahmin değildir: sözleşmenin son satırı "yukarıdaki beş bölüm dışına çıkma"
der. `test_bolum_anahtarlari_match_pinned_contract_headings` bunu hash
doğrulayarak, SIRA DÂHİL yeniden ölçer — sözleşme değişip bu demet
güncellenmezse test DÜŞER.
"""

ARAC_KIMLIKLERI: tuple[str, ...] = (
    # satıcı / laboratuvar
    "OpenAI",
    "Anthropic",
    "Google DeepMind",
    "DeepMind",
    "xAI",
    "Meta AI",
    "Mistral AI",
    "Perplexity AI",
    "DeepSeek",
    # ürün / model ailesi
    "ChatGPT",
    "GPT",
    "Claude Code",
    "Claude",
    "Gemini",
    "Bard",
    "Codex",
    "Copilot",
    "Grok",
    "Llama",
    "Mistral",
    "Perplexity",
    "Qwen",
)
"""K-137 taraması — KAVRAMDAN yazılmış KAPALI küme, bulunan örneklerden türetilmiş DEĞİL.

Kavram: "araç kimliği" = bir yapay zekâ asistanının SATICI ya da ÜRÜN/model
ailesi adı. Depoda rastlanan adlardan türetilseydi tarama, zaten bulunmuş
olanın tekrar kontrolü olurdu.

**Vaat kümenin kendisi kadardır.** `anonymize` bu demette YAZILI kimlikleri
maskeler; "hiçbir araç kimliği kalmaz" YAPISAL bir garanti DEĞİLDİR ve bu
katmanda kanıtlanamaz — serbest metinde bir sonraki satıcı adı daima kümenin
dışında kalabilir (semantik olumsuzlama). Küme uzadıkça vaat değil kapsama
büyür; ikisi karıştırılmaz.

**Kapsam sınırı BEYAN EDİLİR, sessizce atlanmaz.** İki ad bilerek DIŞARIDADIR:
`Google` tek başına bir asistan kimliği değil şirket/arama motoru adıdır ve
araştırma çıktısında meşru olarak geçer (`Google DeepMind` ve `Gemini`
kapsamdadır); `Kimi` Türkçe'de yaygın bir sözcüktür ve maskelenmesi metni
bozardı. Bu ikisi için körlük garantisi DOĞRULANMADI.
"""

ARAC_MASKESI = "[araç-kimliği-kaldırıldı]"

KAYNAK_ETIKETI = "KAYNAK-{}"
"""Kör kaynak adı — dosya adı da rapor gövdesi de yalnız bunu görür."""

EK_HARFLERI: tuple[str, ...] = ("B", "C", "D")
"""Sözleşmenin EK-B/EK-C/EK-D yazımı: KAYNAK-1/2/3 sırasıyla."""

AZAMI_KAYNAK = len(EK_HARFLERI)

PIN_PATH = Path(__file__).resolve().parents[6] / (
    "shared/contracts/research-contracts.pin.json"
)
ARASTIRMA_DEPOSU_KOKU = _DEPO_KOKU
"""Dış sözleşme deposunun kökü — Task 8'in sabitinden ALINIR, kopyalanmaz."""

GOREV_DOSYASI = "hakem-denetci-gorevi.md"

GOREV_DOSYA_ADI = "00-GOREV.md"
"""Pakete yazılan görev dosyasının adı — istem yolu BURADAN türer.

İki yer okur: paketi kuran `_paket_dosyalari` ve turu koşturan
`run_audit_round`. İki ayrı dizge yazılsaydı biri değişip diğeri kalır,
denetçi var olmayan bir istem dosyasıyla koşardı.
"""

_ORTAM_KISITI = "URL doğrulaması yapılamadı (ortam kısıtı)"
"""Sözleşmenin web-erişimsiz kaçış cümlesi — satır beklentisini KALDIRIR."""

_URL_SONUCLARI: tuple[str, ...] = ("DOĞRULANDI", "KAYNAKTA YOK", "URL AÇILMADI")

KAYNAK_TABANI = 2
"""Sözleşmenin asgari kaynak tabanı: altına düşen koşuda örneklem hiç doldurulmaz."""

URL_SATIRI_PER_KAYNAK = 3
"""Sözleşmenin URL örneklem kuralı: KAYNAK BAŞINA üç satır.

Toplam satır sayısı (`kaynak × 3`) bu kuralın SONUCUdur, kendisi değil — ikisi
tek sabitten türer ki toplam kapısı ile dağılım kapısı ıraksayamasın."""

_BOLUM_BASLIGI_RE = re.compile(
    r"^(\d)\)[ \t]+([A-ZÇĞİÖŞÜ][A-ZÇĞİÖŞÜ ]*?)[ \t]*(?:—.*)?$", re.M
)
_KAYNAK_SAYISI_RE = re.compile(r"[Kk]aynak sayısı[ \t]*:[ \t]*(\d+)")
_BEKLENEN_SATIR_RE = re.compile(r"[Bb]eklenen satır(?:[ \t]*sayısı)?[ \t]*:[ \t]*(\d+)")
_AYIRAC_HUCRESI_RE = re.compile(r"^:?-{2,}:?$")

_ENVANTER_BASLIK_HUCRELERI = ("unit_id", "statu", "kanit", "gerekce")
# Denetçi sözleşmesi 2.3 (dış depo `d9dc289`): URL ÖRNEKLEM SONUCU birebir
# başlık satırlı tablo; ilk sütun İDDİA KİMLİĞİ (`K<kaynak>#<iddia>`), ayrı
# kaynak sütunu YOK (numara kimliğin içindedir). `_tablo_satirlari` başlığı
# küçük harfle karşılaştırır — `URL` burada `url` yazılır.
_URL_BASLIK_HUCRELERI = ("iddia", "url", "sonuç", "not")
_KAYNAK_PROFIL_BASLIK_HUCRELERI = ("kaynak", "resmi", "not")
RESMI_DEGERLERI = ("evet", "hayır")
"""`resmi` sütununun KAPALI kümesi — sözleşmenin kendi yazımı.

K-123'ün resmîlik yargısı denetçide YAPILIYORDU ama serbest düzyazıya gömülüydü
ve K-126'nın tek-kaynak istisnası onu hiç göremiyordu (motor bir AND koşulunun
tek ayağını ölçebiliyor, öbürünü ölçemiyordu). 2026-09-11'de sözleşme profili
TABLOYA çevirdi (dış depo `12beec1`); yargı artık TİPLİ taşınıyor.
"""

_DENETIM_BASLIK_HUCRELERI = (
    "no",
    "alan",
    "iddia-özeti",
    "kaynak-iddialari",
    "kaynaklar",
    "sınıf",
    "bayraklar",
    "öneri",
    "gerekçe",
)


def _arac_deseni() -> re.Pattern[str]:
    """Araç adı taramasının TEK deseni — uzun ad kısa adı GÖLGELER.

    `Claude Code` `Claude`'dan önce denenmezse maskeleme `Code` kelimesini
    metinde bırakırdı. Ek olarak sürüm eki (`GPT-5`) ve Türkçe iyelik/hâl eki
    (`Gemini'nin`) tüketilir: kimliğin kendisi kalmadığı hâlde ekin kalması
    okunabilirliği bozar, tersi ise kimliği sızdırırdı.
    """
    adlar = sorted(ARAC_KIMLIKLERI, key=len, reverse=True)
    return re.compile(
        r"(?<!\w)(?:"
        + "|".join(re.escape(ad) for ad in adlar)
        + r")(?:[-‑–]?\d[\w.]*)?(?:['’]\w*)?(?!\w)",
        re.IGNORECASE,
    )


_ARAC_DESENI = _arac_deseni()


# ─── Veri tipleri (arayüz eki R5 · R6) ──────────────────────────────────────


@dataclass(frozen=True)
class InventoryRow:
    """K-100 envanter satırı — DÖRT alan (spec-input satır 1031 kanoniktir)."""

    unit_id: str
    statu: str
    kanit: str
    gerekce: str


@dataclass(frozen=True)
class UrlCheck:
    """ADIM 1 URL örneklem satırı.

    Sözleşme 2.3 (dış depo `d9dc289`, F4): satır artık İDDİA KİMLİĞİ taşır —
    `iddia` sütunu `K<kaynak>#<iddia>`, `URL` o Bölüm C satırının adresi.
    `kaynak` (kör etiket, `KAYNAK-N`) kimliğin kaynak numarasından TÜRER; ayrı
    sütun yoktur. `erisildi` ve `icerik_uyumlu` sözleşmenin üç sonucundan
    türetilir. `iddia` alanı SONDADIR ve varsayılanı `None`'dır ki eski
    konumsal kurucular kırılmasın; `None` "kimliksiz satır" demektir ve K-126
    ikinci ayağını AÇMAZ (fail-closed) — eski biçim istisna kuramaz.
    """

    url: str
    kaynak: str
    erisildi: bool
    icerik_uyumlu: bool
    not_metni: str
    iddia: "KaynakIddiasi | None" = None


_KAYNAK_IDDIA_RE = re.compile(r"^K(\d+)#(\d+)$")


@dataclass(frozen=True, order=True)
class KaynakIddiasi:
    """Bir ARAŞTIRMA İDDİASININ kimliği: `K<kaynak>#<iddia>`.

    Numaranın sağ yarısı araştırma raporunun Bölüm C tablosundaki `no`
    sütunudur (`brief_doctor.CIddia`). Bu tip, denetçinin *"hangi iddiaya
    baktım"* beyanı ile sentezin *"yeni kalıbı hangi iddiadan türettim"*
    beyanını AYNI üst kaynağa çivileyen bağın taşıyıcısıdır.
    """

    kaynak: int
    iddia: int

    @property
    def etiket(self) -> str:
        return f"K{self.kaynak}#{self.iddia}"


def kaynak_iddialari_coz(ham: str) -> tuple[KaynakIddiasi, ...] | None:
    """`K1#3, K2#7` → tipli demet; biçim bozuksa `None` (fail-closed).

    TEK kuraldır ve İKİ yerde çağrılır: denetçinin `kaynak-iddialari` sütunu ve
    sentezin `kaynak_iddia` alanı. İki ayrı ayrıştırıcı yazılsaydı bağın iki
    ucu farklı biçimleri kabul edebilir, yani bağ sessizce gevşerdi.

    Sözleşme yazımı KAPALIDIR: virgülle ayrılmış, ARTAN, tekrarsız; düzyazı,
    ayraç, "hepsi"/"tümü" ya da boş hücre YOK. Artan-tekrarsız şartı biçimsel
    bir titizlik değil: aynı numaranın iki kez geçmesi ya da sıranın bozulması,
    kümenin `kaynaklar` sütunuyla karşılaştırılmasını sessizce kaydırırdı.

    **SIRA kuralı da BURADA yaşar, çağıranda değil.** İlk yazımda sıralama
    denetçi sütununda ayrıca ölçülüyordu; sentezin `kaynak_iddia` alanı AYNI
    ayrıştırıcıyı çağırdığı hâlde o kuralı MİRAS ALMIYORDU — bağın iki ucu
    farklı biçimleri kabul ediyordu, yani bağ sessizce gevşiyordu.
    """
    if not ham.strip():
        return None
    parcalar = [parca.strip() for parca in ham.split(",")]
    iddialar: list[KaynakIddiasi] = []
    for parca in parcalar:
        eslesme = _KAYNAK_IDDIA_RE.match(parca)
        if eslesme is None:
            return None
        kaynak, iddia = int(eslesme.group(1)), int(eslesme.group(2))
        if not 1 <= kaynak <= AZAMI_KAYNAK or iddia < 1:
            return None
        iddialar.append(KaynakIddiasi(kaynak=kaynak, iddia=iddia))
    if iddialar != sorted(set(iddialar)):
        return None
    return tuple(iddialar)


@dataclass(frozen=True)
class KaynakProfili:
    """KAYNAK PROFİLİ satırı — kaynak numarası, RESMÎLİK yargısı, not."""

    kaynak: int
    resmi: bool
    not_metni: str


def _kaynak_profili(govde: str) -> tuple[tuple[KaynakProfili, ...], list[str]]:
    """KAYNAK PROFİLİ'ni TİPLİ satırlara çevirir (çıktı sözleşmesi 3).

    **Kapsam sınırı, dürüst etiket (R6).** Sözleşme *"denetime giren HER
    kaynak için TEK satır"* der; bu imza koşunun YETKİLİ kaynak sayısını
    GÖRMEZ (tek rapor okunur), dolayısıyla burada yalnız satırların kendi iç
    tutarlılığı ölçülür — numara aralığı, tekrarsızlık, kapalı küme, dolu not.
    "Her kaynak kapsandı mı" sorusu bu katmanda CEVAPLANMAZ.
    """
    errors: list[str] = []
    ham = _tablo_satirlari(govde, _KAYNAK_PROFIL_BASLIK_HUCRELERI)
    if not ham:
        errors.append(
            "KAYNAK PROFİLİ boş ya da sözleşmenin başlık satırını taşımıyor "
            f"({' | '.join(_KAYNAK_PROFIL_BASLIK_HUCRELERI)}): profil 2026-09-11'de "
            "düz yazıdan TABLOYA çevrildi — `resmi` sütunu K-126 tek-kaynak "
            "istisnasının ayağıdır ve düz yazıdan okunamaz"
        )
        return (), errors
    satirlar: list[KaynakProfili] = []
    gorulen: set[int] = set()
    for sira, hucreler in enumerate(ham, start=1):
        if len(hucreler) != len(_KAYNAK_PROFIL_BASLIK_HUCRELERI):
            errors.append(
                f"kaynak profili satırı {sira} "
                f"{len(_KAYNAK_PROFIL_BASLIK_HUCRELERI)} sütunlu değil: {hucreler}"
            )
            continue
        kaynak_h, resmi_h, not_h = hucreler
        if not kaynak_h.isdigit() or not 1 <= int(kaynak_h) <= AZAMI_KAYNAK:
            errors.append(
                f"kaynak profili satırı {sira}: `kaynak` sütunu 1..{AZAMI_KAYNAK} "
                f"aralığında bir numara olmalı, {kaynak_h!r} yazılmış"
            )
            continue
        kaynak = int(kaynak_h)
        if kaynak in gorulen:
            errors.append(
                f"kaynak profili satırı {sira}: `kaynak` {kaynak} TEKRAR ediyor "
                "— numara kimliktir, aynı kaynağa iki resmîlik yargısı çözülemez"
            )
            continue
        if resmi_h not in RESMI_DEGERLERI:
            errors.append(
                f"kaynak profili satırı {sira}: `resmi` kapalı kümenin dışında: "
                f"{resmi_h!r} — {list(RESMI_DEGERLERI)} (emin değilsen "
                f"{RESMI_DEGERLERI[1]!r}; iyimser doldurma K-126 kapısını "
                "sessizce açar)"
            )
            continue
        if not not_h:
            errors.append(
                f"kaynak profili satırı {sira}: `not` hücresi BOŞ — sözleşme "
                "2-3 cümle ister (disiplin · yerellik · özgüllük · tutarlılık)"
            )
            continue
        gorulen.add(kaynak)
        satirlar.append(
            KaynakProfili(
                kaynak=kaynak, resmi=resmi_h == RESMI_DEGERLERI[0], not_metni=not_h
            )
        )
    return tuple(satirlar), errors


@dataclass(frozen=True)
class AuditRow:
    """DENETİM TABLOSU satırı — sözleşmenin SABİT sütun kümesi (çıktı 1)."""

    no: int
    alan: str
    iddia_ozeti: str
    kaynak_iddialari: frozenset[KaynakIddiasi]
    kaynaklar: frozenset[int]
    sinif: str
    bayraklar: str
    oneri: str
    gerekce: str


def _denetim_tablosu(govde: str) -> tuple[tuple[AuditRow, ...], list[str]]:
    """DENETİM TABLOSU'nu TİPLİ satırlara çevirir (çıktı sözleşmesi 1).

    **Neden bu tablo tipli okunur.** Motorun yapısal çoğunluk kapısı bu
    sayıyı bugüne kadar SENTEZİN serbest `kanit` metninden çıkarmaya
    çalışıyordu; denetçi onu ZATEN kendi sütununda söylüyordu. Aynı eksen
    Task 12'nin kontrol noktasında dört hakem turunda dört ayrı sızıntı
    verdi — sınıf düzyazıdan çıkarımla kapanmaz, tipli okumayla kapanır.

    **Çoğunluk `kaynaklar` sütunundan sayılır, `sınıf` etiketinden DEĞİL.**
    Sözleşme elemeden sonra oranı kalan kaynak sayısına uyarlatır, yani oran
    sözlüğü koşuya göre değişir; numara kümesi değişmez. `sınıf` burada
    yalnız numaralara karşı ÇAPRAZ KONTROLDÜR (bkz. `SINIF_TEKIL`).

    **Kapsam sınırı, dürüst etiket.** Oranın SAĞ tarafı ("denetime giren
    kaynak sayısı") burada yalnız `1..AZAMI_KAYNAK` aralığında ve sol
    tarafından küçük olmadığı için sınanır; koşunun YETKİLİ kaynak sayısına
    eşitliği bu imzada ölçülemez (tek rapor görülür, R6). O karşılaştırmanın
    evi TUR seviyesidir ve DOLUDUR: `_tur_sinif_kapisi`.
    """
    errors: list[str] = []
    satirlar: list[AuditRow] = []
    ham = _tablo_satirlari(govde, _DENETIM_BASLIK_HUCRELERI)
    if not ham:
        errors.append(
            "DENETİM TABLOSU boş: sözleşmenin dayattığı başlık satırıyla en az "
            "bir iddia satırı yazılır — boş tablo 'denetim yapılmadı' demektir "
            "ve motorun çoğunluk kapısı sessizce girdisiz kalırdı"
        )
        return (), errors

    onceki_no: int | None = None
    for sira, hucreler in enumerate(ham, start=1):
        if len(hucreler) != len(_DENETIM_BASLIK_HUCRELERI):
            errors.append(
                f"denetim tablosu satırı {sira} "
                f"{len(_DENETIM_BASLIK_HUCRELERI)} sütunlu değil "
                f"({' | '.join(_DENETIM_BASLIK_HUCRELERI)}): {hucreler}"
            )
            continue
        (
            no_h,
            alan,
            iddia,
            iddia_atiflari_h,
            kaynak_h,
            sinif,
            bayraklar,
            oneri,
            gerekce,
        ) = hucreler

        if not no_h.isdigit() or int(no_h) < 1:
            errors.append(
                f"denetim tablosu satırı {sira}: `no` pozitif tam sayı olmalı, "
                f"{no_h!r} yazılmış — bu sütun SATIR KİMLİĞİDİR"
            )
            continue
        no = int(no_h)
        if onceki_no is not None and no <= onceki_no:
            errors.append(
                f"denetim tablosu satırı {sira}: `no` artan olmak ZORUNDA "
                f"({onceki_no} → {no}) — sentezin `D1#<no>` referansı buna "
                "çözülür; tekrar eden numara referansı çözülemez kılar"
            )
            continue

        bos = [
            ad
            for ad, deger in (
                ("alan", alan),
                ("iddia-özeti", iddia),
                ("bayraklar", bayraklar),
                ("gerekçe", gerekce),
            )
            if not deger
        ]
        if bos:
            errors.append(
                f"denetim tablosu satırı {sira} boş hücre taşıyor: {bos} — "
                "boş bırakılmak istenen `bayraklar` hücresine `—` yazılır"
            )
            continue

        parcalar = [parca.strip() for parca in kaynak_h.split(",")]
        if not kaynak_h.strip() or any(not parca.isdigit() for parca in parcalar):
            errors.append(
                f"denetim tablosu satırı {sira}: `kaynaklar` sütunu YALNIZ "
                f"kaynak numarası taşır, {kaynak_h!r} yazılmış — düzyazı, "
                "kısaltma ya da boş hücre yapısal çoğunluğu SAYILAMAZ kılar"
            )
            continue
        numaralar = [int(parca) for parca in parcalar]
        disarda = sorted({n for n in numaralar if not 1 <= n <= AZAMI_KAYNAK})
        if disarda:
            errors.append(
                f"denetim tablosu satırı {sira}: kaynak numarası aralık dışında "
                f"{disarda} — geçerli aralık 1..{AZAMI_KAYNAK}"
            )
            continue
        if numaralar != sorted(set(numaralar)):
            errors.append(
                f"denetim tablosu satırı {sira}: `kaynaklar` artan sırada ve "
                f"tekrarsız yazılır, {kaynak_h!r} yazılmış"
            )
            continue

        # ATIF ADAYA BAĞLANIR (dış depo `12beec1`). Bu sütun raporu kısaltmak
        # için değil BAĞ kurmak için vardır: sentez yeni bir kalıbı pakete
        # sokarken hangi araştırma iddiasından türettiğini yazar, motor da
        # denetçinin AYNI iddiayı gösterdiğini burada doğrular.
        iddia_atiflari = kaynak_iddialari_coz(iddia_atiflari_h)
        if iddia_atiflari is None:
            errors.append(
                f"denetim tablosu satırı {sira}: `kaynak-iddialari` sütunu "
                f"YALNIZ `K<kaynak>#<iddia>` taşır — virgülle ayrılmış, ARTAN, "
                f"tekrarsız; {iddia_atiflari_h!r} yazılmış. Düzyazı, ayraç, "
                "'hepsi', bozuk sıra ya da boş hücre satırı hiçbir adaya "
                "bağlamaz ve ona dayanan `ekle` kararı UYGULANMAZ"
            )
            continue
        # İKİ SÜTUN TUTARLI OLMAK ZORUNDA (sözleşmenin kendi cümlesi) ve
        # eşitlik ÇİFT YÖNLÜ ölçülür. Tek yönlü bir kapı ("⊆") üç kaynakta
        # gördüğünü söyleyen bir satırın tek iddia göstermesine izin verirdi;
        # o satır motorda hâlâ ÜÇ kaynaklık çoğunluk sayardı.
        if {atif.kaynak for atif in iddia_atiflari} != set(numaralar):
            errors.append(
                f"denetim tablosu satırı {sira}: `kaynak-iddialari` ile "
                f"`kaynaklar` tutarlı değil ({iddia_atiflari_h!r} ↔ "
                f"{kaynak_h!r}) — geçen kaynak numaralarının kümesi EŞİT olmak "
                "zorundadır"
            )
            continue

        sinif_hatasi = _sinif_kaynakla_tutarli_mi(sira, sinif, numaralar)
        if sinif_hatasi is not None:
            errors.append(sinif_hatasi)
            continue

        if oneri not in ONERI_DEGERLERI:
            errors.append(
                f"denetim tablosu satırı {sira}: `öneri` kapalı kümenin "
                f"dışında: {oneri!r} — {list(ONERI_DEGERLERI)}"
            )
            continue

        onceki_no = no
        satirlar.append(
            AuditRow(
                no=no,
                alan=alan,
                iddia_ozeti=iddia,
                kaynak_iddialari=frozenset(iddia_atiflari),
                kaynaklar=frozenset(numaralar),
                sinif=sinif,
                bayraklar=bayraklar,
                oneri=oneri,
                gerekce=gerekce,
            )
        )
    return tuple(satirlar), errors


def _sinif_kaynakla_tutarli_mi(
    sira: int, sinif: str, numaralar: list[int]
) -> str | None:
    """`sınıf` etiketi ile numara SAYISI çelişiyorsa sebebi döner."""
    if sinif == SINIF_TEKIL:
        if len(numaralar) != 1:
            return (
                f"denetim tablosu satırı {sira}: `sınıf` {SINIF_TEKIL!r} TEK "
                f"kaynak demektir, `kaynaklar` {sorted(numaralar)} taşıyor"
            )
        return None
    if sinif == SINIF_CELISKI:
        if len(numaralar) < 2:
            return (
                f"denetim tablosu satırı {sira}: `sınıf` {SINIF_CELISKI!r} en az "
                f"iki kaynak ister, `kaynaklar` {sorted(numaralar)} taşıyor — "
                "tek kaynak kendisiyle çelişemez"
            )
        return None
    oran = _SINIF_ORAN_RE.match(sinif)
    if oran is None:
        return (
            f"denetim tablosu satırı {sira}: `sınıf` tanınmıyor: {sinif!r} — "
            f"oran yazımı (`n-m`), {SINIF_TEKIL!r} ya da {SINIF_CELISKI!r}"
        )
    sol, sag = int(oran.group(1)), int(oran.group(2))
    if sol != len(numaralar) or not sol <= sag <= AZAMI_KAYNAK:
        return (
            f"denetim tablosu satırı {sira}: `sınıf` {sinif!r} ile `kaynaklar` "
            f"{sorted(numaralar)} çelişiyor — orandaki SOL sayı numara sayısına "
            f"eşittir, SAĞ sayı denetime giren kaynak sayısıdır "
            f"(en çok {AZAMI_KAYNAK})"
        )
    return None


@dataclass(frozen=True)
class AuditReport:
    """Doğrulanmış tek denetçi raporu."""

    denetci: str
    ham_metin: str
    bolumler: Mapping[str, str]
    denetim_tablosu: tuple[AuditRow, ...]
    kaynak_profili: tuple[KaynakProfili, ...]
    yeniden_dogrulama: tuple[InventoryRow, ...]
    url_orneklem: tuple[UrlCheck, ...]
    unit_snapshot_sha: str

    def __post_init__(self) -> None:
        # `bolumler` `identity.donmus`'tan geçer: beş anahtarlı kapalı küme
        # `validate_report`'un KAPISIDIR; yapımdan sonra anahtar eklemek/silmek
        # o kapıyı geçmiş bir raporu kapıdan geçmemiş hâle çevirirdi.
        object.__setattr__(self, "bolumler", identity.donmus(self.bolumler))
        # DİZİ alanlarının HEPSİ kopyalanır ve ÖĞE TİPLERİ sınanır. Anotasyon çalışma
        # zamanında hiçbir şey yapmaz; çağıran liste verirse takma ad paylaşılır
        # ve kapıdan geçmiş envanter yapımdan SONRA değiştirilebilirdi.
        # `identity.donmus` burada KULLANILAMAZ: `InventoryRow`/`UrlCheck`
        # donmuş dataclass'tır ve `donmus`'un KAPALI kümesinin dışındadır
        # (kural 5 -> TypeError).
        for _alan, _tip in (
            ("denetim_tablosu", AuditRow),
            ("kaynak_profili", KaynakProfili),
            ("yeniden_dogrulama", InventoryRow),
            ("url_orneklem", UrlCheck),
        ):
            _deger = tuple(getattr(self, _alan))
            for _oge in _deger:
                if type(_oge) is not _tip:
                    raise TypeError(
                        f"AuditReport.{_alan} yalnız {_tip.__name__} taşır "
                        f"({type(_oge).__name__} verildi) — benzeyen nesne "
                        "kabul edilmez"
                    )
            object.__setattr__(self, _alan, _deger)


def kok_yolunu_kapila(kok: Path) -> Path:
    """Paket KÖKÜ mutlak ve KENDİ canonical'ine eşit olmak ZORUNDA.

    **Neden kökün KENDİSİ ölçülür.** Rol yolu kapısı `kok/<rol>` biçimini ve
    her rolün canonical eşitliğini sınar. O karşılaştırma kökü ÖNCE
    canonical'leştirseydi kökün kendi takma adlılığı hiç sınanmazdı: `..`
    içeren ya da symlink'li bir ata altında iki rol yolu da "kendi
    canonical'ine eşit" görünür, oysa paketin tamamı beklenenden BAŞKA bir
    yerde durur ve rol ayrımının dayandığı yol sözleşmesi anlamını yitirir.

    Kapı, dosya yaratan HER yüzeyde ilk yan etkiden ÖNCE koşar: `build_packet`
    `mkdir`'den önce, `PacketRef` yapımda. Geç reddetme diskte dosya bırakır.
    """
    yol = Path(kok)
    if not yol.is_absolute():
        raise ValueError(
            f"paket kökü MUTLAK olmak ZORUNDA: {yol} — göreli kök çalışma "
            "dizinine göre kayar ve paketin nerede durduğu ölçülemez"
        )
    canonical = yol.resolve()
    if canonical != yol:
        raise ValueError(
            f"paket kökü kendi canonical'ine EŞİT DEĞİL ({yol} → {canonical}) "
            "— takma ad ('..') ya da symlink'li ata, rol yolu sözleşmesini "
            "görünürde tutup paketin tamamını başka bir yere düşürür"
        )
    return yol


@dataclass(frozen=True)
class PacketRef:
    """Kurulmuş denetçi paketinin kaydı (K-79)."""

    run_id: str
    yetkili_kaynak_sayisi: int
    """DENETİME GİREN kaynak sayısı — ELENMEMİŞ kimlik sayısıdır, `len(sources)` DEĞİL.

    Hakem turu 1 (yüksek, ÖLÇÜLDÜ): eski yazım `len(sources)` diyordu ve elemeli
    her meşru tur reddediliyordu. Sözleşme ADIM 2 elemeden sonra hem URL örneklem
    satır sayısını hem sınıf oranını KALAN kaynak sayısına uyarlatır; denetçi
    doğru davranıp `Kaynak sayısı: 2` yazdığında iki tur kapısı da (`_tur_url_kapisi`
    ve `_tur_sinif_kapisi`) "yetkili sayı 3" diyerek raporu düşürüyordu.
    Kör etiket KONUMDAN türemeye devam eder (elenen kaynağın konumu KAYMAZ);
    değişen yalnız SAYIdır.
    """

    kaynak_seti_sha: str
    sector_id: UUID
    kok: Path
    kopyalar: Mapping[str, Path]
    kopya_shalari: Mapping[str, str]
    unit_snapshot: Mapping[str, Mapping]
    unit_snapshot_sha: str

    def __post_init__(self) -> None:
        # ÜÇ eşleme de salt-okunur kopyaya çevrilir: `kopya_shalari` K-79'un
        # eşitlik invariantını, `unit_snapshot` ise `unit_snapshot_sha`'nın
        # KİMLİĞİNİ taşır; ikisi de yapımdan sonra değiştirilebilir olamaz.
        for _alan in ("kopyalar", "kopya_shalari", "unit_snapshot"):
            object.__setattr__(self, _alan, identity.donmus(getattr(self, _alan)))
        beklenen_roller = set(DENETCI_ROLLERI)
        for _alan in ("kopyalar", "kopya_shalari"):
            if set(getattr(self, _alan)) != beklenen_roller:
                raise ValueError(
                    f"PacketRef.{_alan} anahtarları DENETCI_ROLLERI ile "
                    f"örtüşmüyor: {sorted(getattr(self, _alan))} — rol uzayı "
                    "KAPALIDIR"
                )
        self._rol_yollarini_kapila()
        if isinstance(self.yetkili_kaynak_sayisi, bool) or not isinstance(
            self.yetkili_kaynak_sayisi, int
        ):
            raise TypeError(
                "PacketRef.yetkili_kaynak_sayisi TAM SAYI olmak ZORUNDA: "
                f"{self.yetkili_kaynak_sayisi!r} — kaynak sayısı raporun "
                "beyanından değil paketi KURAN taraftan gelir"
            )
        if not 1 <= self.yetkili_kaynak_sayisi <= AZAMI_KAYNAK:
            raise ValueError(
                "PacketRef.yetkili_kaynak_sayisi sözleşmenin 1.."
                f"{AZAMI_KAYNAK} aralığının dışında: "
                f"{self.yetkili_kaynak_sayisi} — kaynaksız paket kurulmaz, "
                "üç kaynaktan fazlası da adlandırılmaz (EK-B/C/D)"
            )
        if len(set(self.kopya_shalari.values())) != 1:
            raise ValueError(
                "K-79 ihlali: iki denetçi kopyası bayt-özdeş DEĞİL "
                f"({dict(self.kopya_shalari)}) — farklı girdi gören iki rapor "
                "mutabakat kapısına giremez"
            )
        beklenen_sha = identity.canonical_sha(self.unit_snapshot)
        if self.unit_snapshot_sha != beklenen_sha:
            raise ValueError(
                "PacketRef.unit_snapshot_sha taşıdığı görüntünün kimliği DEĞİL "
                f"(beyan {self.unit_snapshot_sha}, ölçüm {beklenen_sha})"
            )


    def _rol_yollarini_kapila(self) -> None:
        """B3(2) — rol yolu TAKMA AD, SYMLINK ya da KÖK DIŞI olamaz.

        K-79 körlüğünün yol ayağı: iki rol AYRI dizinde koşar. `cwd` bir okuma
        sınırı olmadığı için ayrımın tek yapısal dayanağı YOLUN KENDİSİDİR —
        bir rol dizini kardeşinin (ya da paket dışının) takma adıysa ayrım
        görünüşte durur, gerçekte iki rol AYNI yeri görür.

        DÖRT koşul birden: KÖKÜN KENDİSİ mutlak ve canonical (`kok_yolunu_kapila`
        — kök canonical'leştirilerek karşılaştırılsaydı kendi takma adlılığı
        hiç sınanmazdı); yol `kok/<rol>` biçiminde MUTLAK ve kökün DOĞRUDAN
        çocuğu; symlink çözümü kökün HAM hâline karşı ölçülen canonical'ine
        EŞİT; iki rolün çözülmüş yolu birbirinden FARKLI.
        """
        kok = kok_yolunu_kapila(self.kok)
        object.__setattr__(self, "kok", kok)
        gorulen: dict[Path, str] = {}
        for rol in DENETCI_ROLLERI:
            yol = Path(self.kopyalar[rol])
            if not yol.is_absolute() or yol.parent != kok or yol.name != rol:
                raise ValueError(
                    f"PacketRef.kopyalar[{rol!r}] rol yolu sözleşmesini "
                    f"çiğniyor: {yol} — rol yolu MUTLAK, kökün DOĞRUDAN çocuğu "
                    f"ve `kok/{rol}` adında olmak ZORUNDA (kok={kok})"
                )
            canonical = yol.resolve()
            # Kök ARTIK canonical'dir (kapı yukarıda koştu): karşılaştırma
            # kökün HAM hâline karşıdır, ikinci bir canonical'leştirme YOK.
            if canonical != kok / rol:
                raise ValueError(
                    f"PacketRef.kopyalar[{rol!r}] rol yolu kendi canonical'ine "
                    f"EŞİT DEĞİL ({yol} → {canonical}) — takma ad/symlink bir "
                    "rolü kardeşinin ya da paketin dışının üstüne düşürebilir"
                )
            if canonical in gorulen:
                raise ValueError(
                    f"PacketRef.kopyalar rol yolu PAYLAŞILAMAZ: {rol!r} ile "
                    f"{gorulen[canonical]!r} AYNI dizini gösteriyor "
                    f"({canonical}) — iki rol ayrı dizinde koşar (K-79)"
                )
            gorulen[canonical] = rol


@dataclass(frozen=True)
class ValidatedReport:
    """Doğrulayıcının dönüşü — İKİ HÂL VARDIR, üçüncüsü YOKTUR.

    (rapor dolu, errors boş)  = geçerli
    (rapor None, errors dolu) = geçersiz
    """

    rapor: AuditReport | None
    errors: tuple[str, ...]

    def __post_init__(self) -> None:
        # `errors` tutarlılık kontrolünden ÖNCE normalize edilir: çağıran liste
        # verse de alan bir DEMET olur ve takma ad paylaşılmaz. Normalizasyon
        # önce koşmasaydı kontrol, kendisinin kopyalamadığı ve yapımdan SONRA
        # boşaltılabilen bir koleksiyona bakmış olurdu.
        object.__setattr__(self, "errors", tuple(self.errors))
        if (self.rapor is None) != bool(self.errors):
            raise ValueError(
                "ValidatedReport tutarsız: `rapor is None` ile `errors` "
                "doluluğu AYNI olmak ZORUNDA "
                f"(rapor={'None' if self.rapor is None else 'dolu'}, "
                f"errors={len(self.errors)}) — yarım doğrulama sonucu yazılmaz"
            )

    @property
    def gecerli(self) -> bool:
        """İKİ koşul BİRDEN — rapor VAR ve hata YOK."""
        return self.rapor is not None and not self.errors


class PreflightDurumu(str, Enum):
    """K-14 ön kontrolünün KAPALI sonuç kümesi.

    Tek bir `web_erisimi: bool` üç AYRI olguyu tek "başarısız"a ezerdi ve
    ikisi aynı yetkiyi üretirdi: "ölçmedim" ile "ölçtüm, erişim yok" birbirine
    karışır, ikisi de URL doğrulamasını atlatan muafiyete kapı olurdu. Ayrım
    TİPLİDİR çünkü iki AYRI kapı bu kümeyi farklı böler:

    * **Tur başlama kapısı** — YALNIZ `ERISIM_VAR` turu başlatır (fail-closed).
    * **Muafiyet kapısı** — ortam-kısıtı muafiyeti YALNIZ `ERISIM_YOK`'ta
      meşrudur; ölçülmemiş erişim muafiyet ÜRETMEZ.
    """

    ERISIM_VAR = "erisim-var"
    """Prob koştu ve erişimi DOĞRULADI — turu başlatan tek durum."""

    ERISIM_YOK = "erisim-yok"
    """Prob koştu ve erişimin YOKLUĞUNU ölçtü — muafiyeti meşrulaştıran tek durum."""

    OLCULMEDI = "olculmedi"
    """Prob VERİLMEDİ — erişim hiç ölçülmedi; ne tur başlar ne muafiyet doğar."""

    OLCUM_ARIZASI = "olcum-arizasi"
    """Prob patladı — istisna erişim kanıtı DEĞİLDİR; ölçüm yapılmamış sayılır."""


@dataclass(frozen=True)
class PreflightResult:
    """K-14 ön kontrolünün sonucu — ölçülen olgu `durum`dur.

    İki kapı da `durum`dan TÜRER (`tur_baslayabilir` · `muafiyet_mesru`) ve
    ikisi AYNI değer değildir. Erişimli olmayan bir sonuç sebepsiz kurulamaz:
    "neden başlamadı" sorusunun cevabı kayıtta olmak zorundadır; erişimli bir
    sonuç ise sebep TAŞIMAZ — iki hâl vardır, üçüncüsü yoktur.
    """

    arac: str
    durum: PreflightDurumu
    sebep: str

    def __post_init__(self) -> None:
        if not isinstance(self.arac, str) or not self.arac.strip():
            raise ValueError(
                f"PreflightResult.arac kimlik taşımak ZORUNDA: {self.arac!r}"
            )
        if not isinstance(self.durum, PreflightDurumu):
            raise TypeError(
                "PreflightResult.durum KAPALI kümeden gelmek ZORUNDA "
                f"({type(self.durum).__name__} verildi) — serbest bayrak üç "
                "olguyu tek 'başarısız'a ezer"
            )
        if self.durum is PreflightDurumu.ERISIM_VAR:
            if self.sebep.strip():
                raise ValueError(
                    "PreflightResult tutarsız: erişimi DOĞRULAYAN ölçüm sebep "
                    f"taşıyamaz: {self.sebep!r}"
                )
        elif not self.sebep.strip():
            raise ValueError(
                "PreflightResult sebepsiz başarısızlık taşıyamaz — turu "
                "durduran ölçüm kayda geçmek zorundadır"
            )

    @property
    def web_erisimi(self) -> bool:
        """ÖLÇÜLMÜŞ erişim — yalnız `ERISIM_VAR`."""
        return self.durum is PreflightDurumu.ERISIM_VAR

    @property
    def tur_baslayabilir(self) -> bool:
        """Tur başlama kapısı — ölçüm erişimi doğrulamıyorsa tur BAŞLAMAZ."""
        return self.durum is PreflightDurumu.ERISIM_VAR

    @property
    def muafiyet_mesru(self) -> bool:
        """Ortam-kısıtı muafiyeti kapısı — YALNIZ ÖLÇÜLMÜŞ erişimsizlikte."""
        return self.durum is PreflightDurumu.ERISIM_YOK


# ─── K-137 anonimleştirme ───────────────────────────────────────────────────


def anonymize(text: str) -> str:
    """`ARAC_KIMLIKLERI` kümesindeki araç kimliklerini maskeler (K-137).

    Anonimleştirme kod düzeyindedir, disiplin değil: pakete yazan HER yol bu
    fonksiyondan geçer, "bu dosyada zaten yoktur" varsayımı YAPILMAZ.

    **Ölçülen vaat KÜMEYE bağlıdır.** Dönen metinde `ARAC_KIMLIKLERI`'nin
    hiçbir üyesi kalmaz. "Metinde hiçbir araç kimliği kalmadı" bundan
    TÜREMEZ — küme kapalıdır ve `Google` ile `Kimi` bilerek dışındadır
    (gerekçeleri `ARAC_KIMLIKLERI` beyanında).
    """
    if not isinstance(text, str):
        raise TypeError(f"anonymize metin bekler: {type(text).__name__}")
    return _ARAC_DESENI.sub(ARAC_MASKESI, text)


# ─── Paketleyici (K-79 · K-137) ─────────────────────────────────────────────


def _pin_kapisi() -> str:
    """Task 9'un İLK işi: sözleşme v2 pini (arayüz eki M1 sıra kapısı).

    Kapı **doğrulanan görev metnini geri döndürür** ve pakete yalnız o metin
    yazılır. Ayrı bir `read_text` ikinci bir okuma olurdu; doğrulama ile
    paketleme arasındaki pencerede dosya değişirse pinlenmemiş talimat baytları
    pakete girer ve iki kopya da aynı olduğu için K-79 bayt-eşitliği bunu
    GÖSTERMEZDİ (iki kopya da yanlış baytı taşır).

    Modül sabitleri çağrı anında okunur — testler onları yerinden oynatarak
    kapının gerçekten koştuğunu ölçebilsin diye.
    """
    return contracts.require_pinned_text(
        PIN_PATH, ARASTIRMA_DEPOSU_KOKU, GOREV_DOSYASI
    )


def _ek_e_metni(doctor_reports: list[DoctorReport]) -> str:
    """EK-E: brief-doctor raporu — KÖR. `kaynak_adi` pakete YAZILMAZ."""
    satirlar = ["# EK-E — brief-doctor betik raporu", ""]
    for sira, rapor in enumerate(doctor_reports):
        satirlar.append(f"## {KAYNAK_ETIKETI.format(sira + 1)}")
        satirlar.append(f"- sonuç: {rapor.sonuc}")
        for sinif, bulgular in (("not", rapor.notlar), ("eleme", rapor.elemeler)):
            for bulgu in bulgular:
                satirlar.append(f"- {sinif}: [{bulgu.kontrol}] {bulgu.mesaj}")
        for sinir in rapor.kapsam_sinirlari:
            satirlar.append(f"- kapsam sınırı: {sinir}")
        satirlar.append("")
    return "\n".join(satirlar)


def _ek_h_metni(active_package: dict | None, unit_snapshot: dict[str, dict]) -> str:
    """EK-H: aktif paketin anlık görüntüsü + karar birimi listesi."""
    yuk = {
        "aktif_paket": active_package,
        "birim_sayisi": len(unit_snapshot),
        "birimler": unit_snapshot,
    }
    return json.dumps(yuk, sort_keys=True, ensure_ascii=False, indent=2) + "\n"


def _paket_dosyalari(
    *,
    gorev_metni: str,
    brief: str,
    sources: list[str],
    doctor_reports: list[DoctorReport],
    active_package: dict | None,
    unit_snapshot: dict[str, dict],
) -> dict[str, str]:
    """Paketin dosya adı → metin eşlemesi. HER değer anonimleştirmeden geçer.

    `gorev_metni` PARAMETREDİR ve burada diskten OKUNMAZ: pin kapısının
    doğruladığı baytların ta kendisi geçer. Fonksiyon dosyayı kendi okusaydı
    doğrulanan bayt ile paketlenen bayt iki ayrı okumadan gelirdi (TOCTOU).
    """
    dosyalar: dict[str, str] = {
        GOREV_DOSYA_ADI: gorev_metni,
        "EK-A-brief.md": brief,
        "EK-E-brief-doctor.md": _ek_e_metni(doctor_reports),
        "EK-H-aktif-paket.json": _ek_h_metni(active_package, unit_snapshot),
    }
    for sira, metin in enumerate(sources):
        etiket = KAYNAK_ETIKETI.format(sira + 1)
        dosyalar[f"EK-{EK_HARFLERI[sira]}-{etiket}.md"] = (
            f"# EK-{EK_HARFLERI[sira]} — {etiket}\n\n{metin}\n"
        )
    return {ad: anonymize(metin) for ad, metin in dosyalar.items()}


def build_packet(
    *,
    brief: str,
    sources: list[str],
    doctor_reports: list[DoctorReport],
    active_package: dict | None,
    unit_snapshot: dict[str, dict],
    run_id: str,
    sector_id: UUID,
    dest: Path,
) -> PacketRef:
    """İki denetçinin BAYT-ÖZDEŞ girdi kopyasını kurar (K-79 · K-137).

    **Eşleme sözleşmesi ÖLÇÜLÜR, çağırana bırakılmaz.** `sources[i]` ile
    `doctor_reports[i]` aynı kaynağı anlatmak ZORUNDADIR ve bunun kanıtı elde
    duran veridedir: `brief_doctor.run` her raporun `icerik_ozeti`'ni
    `identity.canonical_sha(source_text)`'ten üretir. Bu yüzden her `i` için
    `doctor_reports[i].icerik_ozeti == identity.canonical_sha(sources[i])`
    ZORLANIR (fail-closed) — sıra kayarsa özetler tutmaz ve paket kurulmaz.
    Özetsiz rapor da REDDEDİLİR: eşleme kanıtı taşımayan bir rapor kör
    etiketin arkasına saklanamaz. Kural TEKTİR (`identity.canonical_sha`);
    burada ikinci bir hash kuralı yazılmaz.

    Ayrıca ölçülen üç şey: sayıların eşitliği, `kaynak_adi` kimliklerinin
    TEKİLLİĞİ ve kaynak sayısının sözleşmenin üç-kaynak tavanını aşmaması.
    Kimliğin kendisi pakete GİRMEZ — kör etiket konumdan türer.

    **Kapsam sınırı (dürüst etiket).** Ölçülen, özetin METİNLE eşleştiğidir;
    özetin gerçekten `run` tarafından üretildiği (KÖKEN) burada da
    doğrulanmaz — metne sahip bir çağıran doğru özeti kendisi hesaplayabilir.
    O eksen `brief_doctor.DoctorReport.icerik_ozeti`'nin beyan ettiği sınırla
    aynıdır.
    """
    gorev_metni = _pin_kapisi()
    require_run_id(run_id)
    if not isinstance(sector_id, UUID):
        raise TypeError(f"sector_id UUID olmalı: {type(sector_id).__name__}")
    if not sources:
        raise ValueError("paket kaynaksız kurulamaz — denetlenecek çıktı yok")
    if len(sources) > AZAMI_KAYNAK:
        raise ValueError(
            f"sözleşme en çok {AZAMI_KAYNAK} kaynak adlandırır (EK-B/C/D); "
            f"{len(sources)} verildi"
        )
    gecerli_kimlikler = kimlik_bolumlemesi(doctor_reports)[0]
    if len(gecerli_kimlikler) < KAYNAK_TABANI:
        # KENDİ DÜZELTMEMİN YAN ETKİSİ (2026-09-10, kapanış turu — ÖLÇÜLDÜ).
        # `yetkili_kaynak_sayisi` `len(sources)` iken taban ihlali KAZARA
        # engelleniyordu: üç kaynakla kurulup ikisi elenen bir pakette rapor
        # "1 kaynak" der, kapı "yetkili 3" der ve tur düşerdi. Sayıyı
        # düzeltince o kaza kalktı ve TEK KAYNAKLI paket kurulabilir hâle
        # geldi — sözleşmenin K-127 tabanı (2) sessizce delinirdi: tek kaynakla
        # mutabakat sinyali İLKECE üretilemez.
        #
        # Kapı BURAYA konur, `gate_round`'a bırakılmaz: `gate_round` koşuyu
        # durdurur ama `build_packet`'in çağrılmadığını KANITLAMAZ; paketi
        # kuran yüzey kendi ön koşulunu kendisi ölçer (fail-closed).
        raise ValueError(
            f"denetime giren kaynak sayısı tabanın altında: "
            f"{len(gecerli_kimlikler)} < {KAYNAK_TABANI} — elemeden sonra tek "
            "kaynak kalan koşuda denetim YAPILMAZ, koşu durur ve yöneticiye "
            "bildirilir (K-127)"
        )
    if len(doctor_reports) != len(sources):
        raise ValueError(
            f"kaynak sayısı ({len(sources)}) ile brief-doctor raporu sayısı "
            f"({len(doctor_reports)}) eşit DEĞİL — eşleme konumsaldır ve "
            "sayılar ayrışırsa sessizce kayar"
        )
    kimlikler = [rapor.kanonik_kimlik for rapor in doctor_reports]
    if len(set(kimlikler)) != len(kimlikler):
        raise ValueError(
            f"brief-doctor kaynak kimlikleri TEKİL DEĞİL: {kimlikler} — aynı "
            "kaynağın iki raporu iki kaynak sayılamaz (K-127)"
        )
    for sira, (metin, rapor) in enumerate(zip(sources, doctor_reports)):
        if not rapor.icerik_ozeti:
            raise ValueError(
                f"brief-doctor raporu {sira} içerik özeti TAŞIMIYOR — konumsal "
                "eşlemenin kanıtı özettir; özetsiz rapor hangi kaynağı "
                "anlattığını gösteremez"
            )
        olculen = identity.canonical_sha(metin)
        if rapor.icerik_ozeti != olculen:
            raise ValueError(
                f"kaynak {sira} ile brief-doctor raporu {sira} EŞLEŞMİYOR "
                f"(rapor özeti {rapor.icerik_ozeti}, kaynak metnin özeti "
                f"{olculen}) — konumsal eşleme kaymış; kör etiket yanlış "
                "kaynağa yapıştırılamaz"
            )

    # Yol kapısı ilk yan etkiden ÖNCE: reddedilen girdi HİÇBİR dosya yaratmaz.
    kok = kok_yolunu_kapila(Path(dest) / run_id)
    if kok.exists():
        raise FileExistsError(
            f"koşu paketi ZATEN var: {kok} — ham katman salt-eklemedir, dosya "
            "EZİLMEZ (K-82); yeniden koşum yeni kimlik alır"
        )

    dosyalar = _paket_dosyalari(
        gorev_metni=gorev_metni,
        brief=brief,
        sources=sources,
        doctor_reports=doctor_reports,
        active_package=active_package,
        unit_snapshot=unit_snapshot,
    )
    kok.mkdir(parents=True)
    kopyalar: dict[str, Path] = {}
    kopya_shalari: dict[str, str] = {}
    for rol in DENETCI_ROLLERI:
        dizin = kok / rol
        dizin.mkdir()
        parmak: dict[str, str] = {}
        for ad, metin in sorted(dosyalar.items()):
            ham = metin.encode("utf-8")
            (dizin / ad).write_bytes(ham)
            parmak[ad] = hashlib.sha256(ham).hexdigest()
        kopyalar[rol] = dizin
        kopya_shalari[rol] = identity.canonical_sha(parmak)

    return PacketRef(
        run_id=run_id,
        # B4(1): YETKİLİ kaynak sayısı — paketi KURAN taraftan gelir. Raporun
        # kendi `Kaynak sayısı: <n>` beyanı bu sayıya karşı ölçülür (tur
        # seviyesi); rapor kendi beyanıyla tamlık kapısını geçemez.
        yetkili_kaynak_sayisi=len(gecerli_kimlikler),
        kaynak_seti_sha=kaynak_seti_sha(doctor_reports),
        sector_id=sector_id,
        kok=kok,
        kopyalar=kopyalar,
        kopya_shalari=kopya_shalari,
        unit_snapshot=unit_snapshot,
        unit_snapshot_sha=identity.canonical_sha(unit_snapshot),
    )


# ─── K-81 biçim kapısı + K-100 veri kapısı ──────────────────────────────────


def _bolumlere_ayir(text: str) -> tuple[dict[str, str], list[str]]:
    """Raporu beş bölüme ayırır; küme ya da SIRA sapmışsa hata döner."""
    eslesmeler = list(_BOLUM_BASLIGI_RE.finditer(text))
    bulunan = [(int(m.group(1)), m.group(2)) for m in eslesmeler]
    beklenen = list(enumerate(BOLUM_ANAHTARLARI, start=1))
    errors: list[str] = []
    if bulunan != beklenen:
        bulunan_kumesi = {ad for _, ad in bulunan}
        for sira, ad in beklenen:
            if ad not in bulunan_kumesi:
                errors.append(
                    f"biçim kapısı (K-81): {sira}) {ad} bölümü YOK — beş bölüm "
                    "eksiksiz olmak ZORUNDA"
                )
        for sira, ad in bulunan:
            if ad not in BOLUM_ANAHTARLARI:
                errors.append(
                    f"biçim kapısı (K-81): sözleşmede olmayan bölüm: {sira}) {ad}"
                )
        if not errors:
            errors.append(
                "biçim kapısı (K-81): bölüm SIRASI sözleşmeyle örtüşmüyor — "
                f"bulunan {bulunan}, beklenen {beklenen}"
            )
        return {}, errors

    bolumler: dict[str, str] = {}
    for sira, eslesme in enumerate(eslesmeler):
        bas = eslesme.end()
        son = (
            eslesmeler[sira + 1].start()
            if sira + 1 < len(eslesmeler)
            else len(text)
        )
        bolumler[eslesme.group(2)] = text[bas:son].strip("\n")
    return bolumler, errors


def _tablo_satirlari(govde: str, baslik_hucreleri: tuple[str, ...]) -> list[list[str]]:
    """Markdown tablo VERİ satırları — başlık ve ayıraç satırları düşer."""
    satirlar: list[list[str]] = []
    for ham in govde.splitlines():
        duz = ham.strip()
        if not duz.startswith("|"):
            continue
        hucreler = [h.strip() for h in duz.strip("|").split("|")]
        # AYIRAC kapısı (hakem turu 1, orta — ÖLÇÜLDÜ): boş hücreler ELENMEDEN
        # önce sayılır. Eski yazım `... for h in hucreler if h` diyordu; tamamen
        # boş bir satırda üreteç BOŞ kalıyor, `all(())` True dönüyor ve satır
        # AYIRAÇ sanılıp sessizce düşüyordu — sütun sayısı ve boş-hücre kapıları
        # o satırı HİÇ görmüyordu. Ayıraç artık her hücresi DOLU ve ayıraç
        # dilbilgisine uyan satırdır; kalan her şey VERİ satırıdır ve kendi
        # kapılarına girer (fail-closed).
        if hucreler and all(_AYIRAC_HUCRESI_RE.match(h) for h in hucreler):
            continue
        if tuple(h.lower() for h in hucreler) == baslik_hucreleri:
            continue
        satirlar.append(hucreler)
    return satirlar


def _url_orneklemi(govde: str) -> tuple[tuple[UrlCheck, ...], list[str]]:
    """URL örneklem bölümü — **BEYANIN KENDİ İÇİNDE TUTARLILIĞI** ölçülür.

    Ölçülen tam olarak şudur: raporun yazdığı `Kaynak sayısı: <n>` ile yazdığı
    `beklenen satır: <m>` kuralı sağlıyor mu (`n ≥ 2` ise `m = n × 3`, değilse
    `m = 0`) ve tabloya gerçekten `m` satır yazılmış mı.

    **BURADA ÖLÇÜLMEYEN — ama artık ÖLÇÜLEN (ev onurlandırıldı).** Beyan edilen
    kaynak sayısının YETKİLİ kaynak sayısıyla eşit olduğu ve `_ORTAM_KISITI`
    cümlesinin gerçekten ölçülmüş bir erişimsizliğe karşılık geldiği bu imzada
    KARŞILAŞTIRILAMAZ (ne yetkili sayı ne de ölçülmüş erişim durumu tek rapor
    gören bir kapıya girer). İkisinin evi **tur seviyesidir** ve o ev artık
    DOLUDUR: `_tur_url_kapisi` (`run_audit_round` içinden çağrılır)
    `PacketRef.yetkili_kaynak_sayisi` ile `preflight` sonucuna karşı ölçer.
    Bu fonksiyon TEK BAŞINA kullanılırsa iki karşılaştırma yapılmamış olur.
    """
    errors: list[str] = []
    kaynak_e = _KAYNAK_SAYISI_RE.search(govde)
    beklenen_e = _BEKLENEN_SATIR_RE.search(govde)
    if kaynak_e is None or beklenen_e is None:
        errors.append(
            "URL ÖRNEKLEM SONUCU bölümü zorunlu beyanı taşımıyor "
            "(`Kaynak sayısı: <n>` ve `beklenen satır: <m>`) — satır sayısı "
            "sabit olmadığı için beyan olmadan ölçülemez"
        )
        return (), errors

    kaynak_sayisi = int(kaynak_e.group(1))
    beyan = int(beklenen_e.group(1))
    kural = (
        kaynak_sayisi * URL_SATIRI_PER_KAYNAK
        if kaynak_sayisi >= KAYNAK_TABANI
        else 0
    )
    if beyan != kural:
        errors.append(
            f"URL örneklem beyanı kuralla çelişiyor: {kaynak_sayisi} kaynak "
            f"için beklenen satır {kural}, beyan {beyan} — tek kaynak kalırsa "
            "bölüm hiç doldurulmaz"
        )

    ham_satirlar = _tablo_satirlari(govde, _URL_BASLIK_HUCRELERI)
    kontroller: list[UrlCheck] = []
    for sira, hucreler in enumerate(ham_satirlar, start=1):
        if len(hucreler) != len(_URL_BASLIK_HUCRELERI):
            errors.append(
                f"URL örneklem satırı {sira} {len(_URL_BASLIK_HUCRELERI)} sütunlu "
                f"değil ({' | '.join(_URL_BASLIK_HUCRELERI)}): {hucreler}"
            )
            continue
        iddia_h, url, sonuc, not_metni = hucreler
        # İDDİA KİMLİĞİ — tek ayrıştırıcı (`kaynak_iddialari_coz`), TEK kimlik.
        # Boş, düzyazı, URL ya da birden çok kimlik → satır kimliksizdir ve
        # taşınmaz: K-126'nın ikinci ayağı iddiaya bağlıdır, "hangi iddia"
        # bilinmeyen bir doğrulama istisna açamaz (sözleşme 2.3: fail-closed).
        kimlikler = kaynak_iddialari_coz(iddia_h)
        if kimlikler is None or len(kimlikler) != 1:
            errors.append(
                f"URL örneklem satırı {sira}: `iddia` hücresi TEK iddia kimliği "
                f"olmalı (`K<kaynak>#<iddia>`), {iddia_h!r} yazılmış"
            )
            continue
        if not url.strip():
            errors.append(
                f"URL örneklem satırı {sira}: `URL` hücresi BOŞ — Bölüm C "
                "satırının adresi aynen kopyalanır"
            )
            continue
        if sonuc not in _URL_SONUCLARI:
            errors.append(
                f"URL örneklem satırı {sira} kapalı sonuç kümesinin dışında: "
                f"{sonuc!r} — {list(_URL_SONUCLARI)}"
            )
            continue
        (kimlik,) = kimlikler
        kontroller.append(
            UrlCheck(
                url=url,
                kaynak=KAYNAK_ETIKETI.format(kimlik.kaynak),
                erisildi=sonuc != "URL AÇILMADI",
                icerik_uyumlu=sonuc == "DOĞRULANDI",
                not_metni=not_metni,
                iddia=kimlik,
            )
        )

    if _ORTAM_KISITI in govde:
        if ham_satirlar:
            errors.append(
                f"ortam kısıtı beyan edilmiş ({_ORTAM_KISITI}) ama örneklem "
                f"{len(ham_satirlar)} satır taşıyor — doğrulama yapılmadan "
                "sonuç YAZILMAZ"
            )
    elif len(ham_satirlar) != kural:
        errors.append(
            f"URL örneklem satır sayısı koşullu kuralla çelişiyor: "
            f"{kaynak_sayisi} kaynak → {kural} satır beklenir, "
            f"{len(ham_satirlar)} yazılmış"
        )
    else:
        errors.extend(_url_dagilimi(kontroller, kaynak_sayisi))
    return tuple(kontroller), errors


def _url_dagilimi(
    kontroller: list[UrlCheck], kaynak_sayisi: int
) -> list[str]:
    """KAYNAK BAŞINA satır sayısı — toplam doğru olsa da dağılım bozuk olabilir.

    **ÖLÇÜLEN KUSUR (attempt-3 hakem turu F6).** Kapı yalnız `kaynak × 3`
    TOPLAMINI sayıyordu: dokuz satırın dokuzu da `K1#…` olsa geçerdi ve tek
    kaynağın örneklemi üç kaynağın örneklemi gibi görünürdü. Sözleşme "kaynak
    başına 3 satır" der; toplam o kuralın SONUCUdur, kendisi değil.

    Bu ölçüm ancak iddia kimliği kaynak numarasını TAŞIDIĞI için mümkün
    (sözleşme 2.3); eski biçimde satırın hangi kaynağa ait olduğu makine
    tarafından bilinemiyordu.
    """
    if kaynak_sayisi < KAYNAK_TABANI:
        return []
    sayim: dict[int, int] = {}
    for kontrol in kontroller:
        sayim[kontrol.iddia.kaynak] = sayim.get(kontrol.iddia.kaynak, 0) + 1

    sapan = {k: n for k, n in sayim.items() if n != URL_SATIRI_PER_KAYNAK}
    if len(sayim) != kaynak_sayisi or sapan:
        dokum = ", ".join(f"K{k}:{n}" for k, n in sorted(sayim.items())) or "<boş>"
        return [
            f"URL örneklem dağılımı kuralla çelişiyor: kaynak başına "
            f"{URL_SATIRI_PER_KAYNAK} satır beklenir ve {kaynak_sayisi} ayrı "
            f"kaynak yazılmalıdır; yazılan dağılım {dokum} — toplam doğru olsa "
            "da tek kaynağın örneklemi çok kaynak gibi görünür"
        ]
    return []


def _envanter(
    govde: str, unit_snapshot: Mapping[str, Any]
) -> tuple[tuple[InventoryRow, ...], list[str]]:
    """K-100 VERİ kapısı — biçim kapısından AYRI.

    Bölüm-varlığı kontrolü envanterin kendisini denetlemez: eksik envanter
    motorun mutabakat kapısına "uyum" gibi görünürdü (iki denetçi de atlanan
    birim hakkında sessiz kalır, kapı sessizliği uyum okur).
    """
    errors: list[str] = []
    satirlar: list[InventoryRow] = []
    gorulen: dict[str, int] = {}
    for sira, hucreler in enumerate(
        _tablo_satirlari(govde, _ENVANTER_BASLIK_HUCRELERI), start=1
    ):
        if len(hucreler) != 4:
            errors.append(
                f"envanter satırı {sira} dört alan taşımıyor "
                f"(unit_id · statu · kanit · gerekce): {hucreler}"
            )
            continue
        unit_id, statu, kanit, gerekce = hucreler
        if not kanit or not gerekce:
            errors.append(
                f"envanter satırı {sira} boş alan taşıyor — dört alanın DÖRDÜ "
                f"de doldurulur: {hucreler}"
            )
            continue
        if statu not in STATU_DEGERLERI:
            errors.append(
                f"envanter satırı {sira} kapalı statu kümesinin dışında: "
                f"{statu!r} — {list(STATU_DEGERLERI)}"
            )
            continue
        if unit_id not in unit_snapshot:
            errors.append(
                f"envanter satırı {sira} tanınmayan karar birimi taşıyor: "
                f"{unit_id} — anlık görüntüde YOK, kimlik ÜRETİLEMEZ"
            )
            continue
        gorulen[unit_id] = gorulen.get(unit_id, 0) + 1
        if gorulen[unit_id] > 1:
            errors.append(
                f"karar birimi {unit_id} tekrar raporlanmış "
                f"({gorulen[unit_id]} kez) — her birim TAM BİR KEZ"
            )
            continue
        satirlar.append(
            InventoryRow(
                unit_id=unit_id, statu=statu, kanit=kanit, gerekce=gerekce
            )
        )

    for unit_id in unit_snapshot:
        if unit_id not in gorulen:
            errors.append(
                f"karar birimi {unit_id} raporlanmamış — anlık görüntüdeki HER "
                "birim TAM BİR KEZ raporlanır; eksik envanter uyuşmazlığı gizler"
            )
    return tuple(satirlar), errors


def validate_report(
    text: str,
    *,
    unit_snapshot: dict[str, dict],
    denetci: str,
) -> ValidatedReport:
    """K-81 biçim kapısı + K-100 veri kapısı; AYRIŞTIRILMIŞ nesne döner.

    `unit_snapshot`'ın TEK üreticisi `identity.decision_units`'tir (Task 3).
    Çapraz denetçi mutabakatı BURADA YAPILMAZ — tek rapor görülür (R6(c)).

    **İki kapının GÜCÜ ayrıdır (dürüst etiket).** K-100 envanteri `unit_snapshot`
    ile karşılaştırılır: yetkili bir kaynağa karşı ölçülür ve rapor kendi
    beyanıyla bu kapıyı geçemez. URL örneklemi BURADA BÖYLE DEĞİLDİR — bu imza
    ne yetkili kaynak sayısını ne de ölçülmüş erişim durumunu görür, dolayısıyla
    yalnız raporun **kendi beyanının iç tutarlılığı** ölçülür. Eksik ayak TUR
    SEVİYESİNDE kapatıldı: `run_audit_round` → `_tur_url_kapisi` beyanı
    `PacketRef.yetkili_kaynak_sayisi` ile, ortam-kısıtı muafiyetini de `preflight`
    sonucuyla karşılaştırır. İmza arayüz eki R6(a) ile bağlıdır ve bu turda
    DEĞİŞTİRİLMEDİ — kapı EKLENMEDİ, tur seviyesine KONDU.
    """
    if not isinstance(text, str):
        raise TypeError(f"validate_report metin bekler: {type(text).__name__}")
    errors: list[str] = []
    if denetci not in DENETCI_ROLLERI:
        errors.append(
            f"denetci rol uzayının dışında: {denetci!r} — {list(DENETCI_ROLLERI)}"
        )

    bolumler, bicim_hatalari = _bolumlere_ayir(text)
    errors.extend(bicim_hatalari)
    if bicim_hatalari:
        # Bölüm kümesi sapmışsa gövdeler güvenilir biçimde ayrılamaz; veri
        # kapısı BOZUK bir ayrıştırmanın üstünde koşturulmaz (fail-closed).
        return ValidatedReport(None, tuple(errors))

    denetim, denetim_hatalari = _denetim_tablosu(bolumler[BOLUM_ANAHTARLARI[0]])
    errors.extend(denetim_hatalari)
    kontroller, url_hatalari = _url_orneklemi(bolumler[BOLUM_ANAHTARLARI[1]])
    errors.extend(url_hatalari)
    profil, profil_hatalari = _kaynak_profili(bolumler[BOLUM_ANAHTARLARI[2]])
    errors.extend(profil_hatalari)
    satirlar, envanter_hatalari = _envanter(
        bolumler[BOLUM_ANAHTARLARI[4]], unit_snapshot
    )
    errors.extend(envanter_hatalari)

    if errors:
        return ValidatedReport(None, tuple(errors))
    return ValidatedReport(
        AuditReport(
            denetci=denetci,
            ham_metin=text,
            bolumler=bolumler,
            denetim_tablosu=denetim,
            kaynak_profili=profil,
            yeniden_dogrulama=satirlar,
            url_orneklem=kontroller,
            unit_snapshot_sha=identity.canonical_sha(unit_snapshot),
        ),
        (),
    )


# ─── K-14 ön kontrol ────────────────────────────────────────────────────────


def preflight(
    tool: str, *, prob: Callable[[str], bool] | None = None
) -> PreflightResult:
    """Denetçi aracının web erişimini sınar — FAIL-CLOSED (K-14).

    `prob` çağıranın sağladığı ölçüm yoludur (CLI katmanı, Task 11). Dönüş
    `PreflightDurumu`'nun KAPALI kümesinden gelir ve üç başarısızlık AYRIDIR:
    prob yoksa `OLCULMEDI`, prob olumsuz dönerse `ERISIM_YOK`, prob patlarsa
    `OLCUM_ARIZASI`. Üçü de turu başlatmaz; muafiyeti YALNIZ `ERISIM_YOK`
    meşrulaştırır — ölçülmemiş erişim ne tur başlatır ne muafiyet üretir.

    **Kaçan istisna yutulmaz.** `Exception` `OLCUM_ARIZASI`'na çevrilir, ama
    `BaseException` (iptal dâhil) OLDUĞU GİBİ geçer: iptal bir ölçüm sonucu
    değildir ve çağıranın koruma bölgesine ait olmalıdır.

    **Dönüş TİP kapısından geçer (B5).** Kabul edilen tek değer kümesi
    `{True, False}`'tur ve kapı `type(...) is bool` ile ölçülür; başka her tip
    `OLCUM_ARIZASI`'dır. `bool(...)` süzgeci bu kapının YERİNE GEÇMEZ, tam
    tersine iki yönde de yalan söyler: `"false"` metni truthy'dir ve erişimi
    UYDURUR, `0` ise falsy'dir ve "ölçtüm, yok" gibi görünüp `ERISIM_YOK`'un
    meşrulaştırdığı MUAFİYETİ üretirdi. `bool` Python'da `int`'in alt
    sınıfıdır, ama `1`/`0` yine reddedilir: bir erişim BEYANI değil, bir
    sayıdır. Özensiz prob girdinin ta kendisidir — tehdit modeli budur.
    """
    if not isinstance(tool, str) or not tool.strip():
        raise ValueError(f"preflight araç kimliği bekler: {tool!r}")
    if prob is None:
        return PreflightResult(
            arac=tool,
            durum=PreflightDurumu.OLCULMEDI,
            sebep="web erişimi probu tanımlı DEĞİL — erişim ölçülmedi, tur "
            "başlamaz (ölçülmemiş erişim 'var' sayılmaz)",
        )
    try:
        deger = prob(tool)
    except Exception as exc:  # noqa: BLE001 — her arıza turu DURDURUR
        return PreflightResult(
            arac=tool,
            durum=PreflightDurumu.OLCUM_ARIZASI,
            sebep=f"web erişimi probu hata verdi: {type(exc).__name__}: {exc}",
        )
    if type(deger) is not bool:
        return PreflightResult(
            arac=tool,
            durum=PreflightDurumu.OLCUM_ARIZASI,
            sebep=(
                "web erişimi probu `bool` DEĞİL bir değer döndürdü "
                f"({type(deger).__name__}: {deger!r}) — `True`/`False` dışında "
                "hiçbir şey erişim BEYANI değildir; truthy bir dönüş erişimi "
                "uydurur, falsy bir dönüş muafiyet üretirdi (K-14 fail-closed)"
            ),
        )
    if deger:
        return PreflightResult(
            arac=tool, durum=PreflightDurumu.ERISIM_VAR, sebep=""
        )
    return PreflightResult(
        arac=tool,
        durum=PreflightDurumu.ERISIM_YOK,
        sebep="web erişimi probu olumsuz döndü — tur başlamaz",
    )


# ═══ Task 10 — iki kör denetçi orkestrasyonu (K-76 · K-78 · K-79 · K-82 · K-150) ═══

RAPOR_DOSYA_KALIBI = "RAPOR-{}.md"
DENETIM_ASAMASI = "denetim"
SENTEZ_ARACI = "sentez"
ARAC_ADLARI: tuple[str, ...] = DENETCI_ROLLERI + (SENTEZ_ARACI,)
RUNNER_DURUMLARI: tuple[str, ...] = ("tamam", "zaman-asimi", "hata")

_LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class ToolSpec:
    """Bir aracın DONDURULMUŞ komut satırı — argümanlar ÖLÇÜLDÜ, uydurulmadı.

    Ölçüm dosyası: `docs/research/2026-09-09-denetci-cli-olcumu.md` (kurulu
    CLI'ların ham `--help` çıktısı). İstem argv'ye GÖMÜLMEZ, alt sürece
    STDIN'den gider: tek argümanın bayt sınırı vardır, görev metni ekleriyle
    büyür.
    """

    argv: tuple[str, ...]

    def __post_init__(self) -> None:
        deger = tuple(self.argv)
        if not deger:
            raise ValueError("ToolSpec.argv BOŞ olamaz — komutsuz araç koşamaz")
        for parca in deger:
            if not isinstance(parca, str) or not parca:
                raise ValueError(
                    f"ToolSpec.argv yalnız boş olmayan dize taşır: {parca!r}"
                )
        object.__setattr__(self, "argv", deger)


_CLAUDE_YASAK_ARACLAR = "Bash,Write,Edit,NotebookEdit,WebFetch,WebSearch,Task"
"""`claude` alt süreçlerinin KULLANAMAYACAĞI araçlar (2026-09-12 güvenlik review'ı, S-2).

Girdi metni DIŞ kaynaklıdır: araştırma ekleri web'den derlenir ve denetçi paketine
AYNEN kopyalanır. Kısıtsız bir ajan bağlamında o metne gömülü bir talimat, şema
doğrulaması daha koşmadan dosya/ortam okuyabilir, komut çalıştırabilir ya da ağ
üzerinden sızdırabilirdi. `cwd` bir güvenlik sınırı DEĞİLDİR — sınırı argv kurar.
"""

_CLAUDE_ARAC_KUMESI = "Read,Glob,Grep"
"""Denetçinin KULLANABİLECEĞİ araçların TAMAMI — POZİTİF küme, yasak listesi değil.

**Neden pozitif (kapanış turu bulgusu, high — ÖLÇÜLDÜ):** ilk sertleştirme yalnız
bir yasak listesi taşıyordu ve `Read`/`Glob`/`Grep`/`Agent`/`Skill` açık kalıyordu;
yani enjekte edilmiş bir talimat paket DIŞINDAKİ dosyaları okuyup şema-geçerli bir
raporun içine koyabilirdi. Yasak listesi AÇIK UÇLUDUR — CLI'ya yarın eklenen her
araç kendiliğinden izinli olurdu. Pozitif küme tersini yapar: adı geçmeyen her şey
kapalıdır. Denetçinin işi paket dosyalarını OKUMAKTIR, o yüzden küme okuma
araçlarıdır.
"""

_CLAUDE_IZOLASYON = (
    "--permission-mode",
    "plan",
    "--safe-mode",
    "--restricted",
    "--tools",
    _CLAUDE_ARAC_KUMESI,
    "--strict-mcp-config",
    "--disallowedTools",
    _CLAUDE_YASAK_ARACLAR,
)
"""`codex`in `--sandbox read-only`'sinin `claude` karşılığı — simetri KASITLIDIR.

Katmanlar: `plan` kipi yazma/çalıştırma yollarını kapatır · `--safe-mode`
kullanıcının CLAUDE.md'si, skill'leri, hook'ları, eklentileri ve özel komutlarını
devre dışı bırakır (aksi hâlde denetçi, bu boru hattının hiç tanımadığı yerel
talimatları devralırdı — ayrıca o metinler de bir enjeksiyon yüzeyidir) ·
`--restricted` komut/kod çalıştıran yerleşik araçları kaldırır ve kullanıcı
özelleştirmelerini yok sayar · `--tools` izinli kümeyi POZİTİF olarak sayar ·
`--strict-mcp-config` MCP sunucularını devre dışı bırakır · yasak liste ise
derinlemesine savunmadır. Hepsi argv'dedir; hiçbiri prompt metnine dayanmaz.

**ÖLÇÜLEN SINIR (2026-09-12, kurulu CLI ile üç prob koşumu):** `--restricted`
dosya araçlarını ÇALIŞMA DİZİNİNE hapsediyor — aracın kendi hata metni:
*"<yol> is outside <cwd>; --restricted confines the file tools to the working
directory"*. Ölçüm iki zararsız hedefle yapıldı (göreli `../disarida.txt` ve
mutlak `/etc/hostname`); ikisi de ENGELLENDİ, paket içindeki dosya OKUNDU. Yani
`~/.claude/.credentials.json` · `.env` · `/proc/<ppid>/environ` gibi hedefler
paket dizininin dışında kaldıkları için bu kapının ARKASINDADIR.

**KALAN — dürüst etiket:** hapsi işleten CLI'nın kendisidir, işletim sistemi
DEĞİL. Alt süreç hâlâ aynı kullanıcı altında koşar; CLI'da bir gerileme ya da
bayrak adı değişikliği sınırı sessizce kaldırabilir (bu yüzden bayrakların
kurulu yardıma karşı ölçüldüğü tripwire testi vardır — ama o bayrağın VARLIĞINI
ölçer, DAVRANIŞINI değil). Kimlik dosyalarının kendisiyle doğrudan prob
YAPILAMADI: model o hedefleri okumayı reddediyor, yani ölçüm modelin kararına
karışıyor — sınır zararsız hedeflerle ölçüldü. Gerçek süreç izolasyonu
(kapsayıcı/ad-alanı ya da araçsız yapılandırılmış-çıktı API'si) bu turda
YAPILMADI (güvenlik review'ı S-2 kalıntısı).
"""


ARAC_KOMUTLARI: Mapping[str, ToolSpec] = MappingProxyType(
    {
        DENETCI_ROLLERI[0]: ToolSpec(
            ("claude", "-p", "--output-format", "text", *_CLAUDE_IZOLASYON)
        ),
        DENETCI_ROLLERI[1]: ToolSpec(
            (
                "codex",
                "exec",
                "--skip-git-repo-check",
                "--sandbox",
                "read-only",
                "--color",
                "never",
                "-",
            )
        ),
        SENTEZ_ARACI: ToolSpec(
            ("claude", "-p", "--output-format", "text", *_CLAUDE_IZOLASYON)
        ),
    }
)
"""Araç → komut satırı — KAPALI, ÜÇ giriş (iki denetçi + sentez).

Rol/araç eşlemesi planın 1267. satırında bağlıdır (`denetci-1` → Claude Code,
`denetci-2` → Codex). `sentez`'in Claude Code olması TERCİH DEĞİL ÖLÇÜMDÜR:
pinlenmiş `hakem-sentez-gorevi.md` 4. satırı "İki denetçi çıktısı hazır
olduktan sonra Claude Code'da koşulur" der.

**Testin beklentisi bu eşlemeden OKUNMAZ** — okusaydı yanlış bir eşlemeyi de
geçirirdi (totolojik test). `test_runner_argv_matches_independent_literals`
ölçüm anında elle yazılmış sabitlere bakar, ayrıca
`test_toolspec_flags_exist_in_the_installed_cli_help` her koşumda kurulu
CLI'nın yardımını yeniden okur.

**Ölçülmüş eksik (dürüst etiket):** `codex exec` 0.151.0'da `--search` YOKTUR
(yalnız üst düzey `codex`'te var), dolayısıyla bu argv canlı web aramasını
AÇMAZ. Kapı yine de fail-closed'dır: K-14 `preflight` erişimi ÖLÇER ve
erişimsiz tur BAŞLAMAZ. Evi Task 11'dir (probu sağlayan katman).
"""


@dataclass(frozen=True)
class RunnerOutcome:
    """Alt süreç koşumunun TİPLİ sonucu — ham metin DEĞİL.

    Üç hâl kapalıdır ve `tamam` hâli İKİ koşula birden bakar: çıkış kodu sıfır
    VE gövde dolu. "Sessiz başarı" (0 dönen ama hiçbir şey yazmayan araç) bu
    tiple KURULAMAZ; boş rapor, rapor değildir.
    """

    durum: str
    stdout: str
    stderr: str
    exit_code: int | None

    def __post_init__(self) -> None:
        if self.durum not in RUNNER_DURUMLARI:
            raise ValueError(
                f"RunnerOutcome.durum kapalı kümenin dışında: {self.durum!r} — "
                f"{list(RUNNER_DURUMLARI)}"
            )
        for alan in ("stdout", "stderr"):
            if not isinstance(getattr(self, alan), str):
                raise TypeError(
                    f"RunnerOutcome.{alan} dize olmak ZORUNDA: "
                    f"{type(getattr(self, alan)).__name__}"
                )
        if self.exit_code is not None and not isinstance(self.exit_code, int):
            raise TypeError(
                f"RunnerOutcome.exit_code int ya da None: {self.exit_code!r}"
            )
        if self.durum == "zaman-asimi" and self.exit_code is not None:
            raise ValueError(
                "zaman aşımına uğrayan süreç çıkış kodu TAŞIMAZ: "
                f"{self.exit_code!r}"
            )
        if self.durum == "tamam":
            if self.exit_code != 0:
                raise ValueError(
                    f"`tamam` sıfır çıkış kodu ister: {self.exit_code!r}"
                )
            if not self.stdout.strip():
                raise ValueError(
                    "`tamam` BOŞ gövdeyle kurulamaz — sessiz başarı YOKTUR; "
                    "çıktı yoksa sonuç `hata`dır"
                )


class Runner(Protocol):
    """Denetçi/sentez koşumunun test edilebilirlik DİKİŞİ.

    **İmzada koşu kimliği ya da veritabanı YOKTUR** — bu bilinçlidir: durum
    sahibi orkestratördür (`run_audit_round` · `synthesis.run`), runner
    `tamamlanmadi` işaretini ATAMAZ. Gerçek koşumda `SubprocessRunner`, testte
    sahte runner geçer.
    """

    def run(self, tool: str, cwd: Path, prompt_path: Path) -> RunnerOutcome: ...


class SubprocessRunner:
    """`Runner`'ın GERÇEK uygulaması — yerel CLI alt süreci (K-76).

    Dört şey burada olur, beşincisi OLMAZ:

    1. Araç adı KAPALI eşlemeden çözülür; tanınmayan ad fail-closed düşer.
    2. İstem dosyası STDIN'e verilir (argv'ye gömülmez).
    3. Dış zaman aşımı uygulanır — CLI'ların kendi zaman aşımı bayrağı YOKTUR
       (ölçüldü, `docs/research/2026-09-09-denetci-cli-olcumu.md` §3(d)).
       **Varsayılan YOKTUR:** süre zorunlu parametredir, ölçülmemiş bir saniye
       değeri sabit yazılmaz (İlke 9).
    4. stdout rapor gövdesidir; **stderr'e KARIŞMAZ** (ayrı yakalanır) ve
       günlüğe yazılmadan önce K-136 süzgecinden geçer.
    5. OLMAYAN: koşu durumu yazmak. Runner'ın `db`'si ve `run_id`'si yoktur.
    """

    def __init__(self, *, zaman_asimi_sn: float) -> None:
        if isinstance(zaman_asimi_sn, bool) or not isinstance(
            zaman_asimi_sn, (int, float)
        ):
            raise TypeError(
                f"zaman_asimi_sn sayı olmalı: {type(zaman_asimi_sn).__name__}"
            )
        if zaman_asimi_sn <= 0:
            raise ValueError(
                f"zaman_asimi_sn pozitif olmalı: {zaman_asimi_sn!r} — sıfır ya "
                "da negatif sınır koşumu hiç başlatmaz"
            )
        self.zaman_asimi_sn = float(zaman_asimi_sn)

    @staticmethod
    def _metin(ham: bytes | str | None) -> str:
        if ham is None:
            return ""
        if isinstance(ham, str):
            return ham
        return ham.decode("utf-8", errors="replace")

    def _gunlukle(self, tool: str, durum: str, stderr: str) -> None:
        """stderr GÜNLÜĞE maskelenerek gider (K-136) — ham hâli asla."""
        if not stderr.strip():
            return
        _LOG.warning(
            "denetçi alt süreci stderr yazdı: arac=%s durum=%s stderr=%s",
            tool,
            durum,
            runs.mask_secrets(stderr),
        )

    @staticmethod
    def _alt_surec_ortami() -> dict[str, str]:
        """Alt sürecin göreceği ortam — BEYAZ LİSTE (2026-09-12 güvenlik review'ı, S-2).

        Miras alınan ortam, enjekte edilmiş bir talimat için hazır bir sızdırma
        kanalıydı: çağıranın ortamına yüklenmiş her anahtar (veritabanı, fal.ai,
        R2, ElevenLabs, Anthropic) çocuğun `os.environ`'ında duruyordu. Liste
        ÇALIŞMAK için gerekenle sınırlıdır; araç kimlikleri `HOME` altındaki
        kendi yapılandırmalarından okunur, ortamdan DEĞİL.
        """
        izinli = ("PATH", "HOME", "LANG", "LC_ALL", "LC_CTYPE", "TERM", "TMPDIR")
        return {ad: os.environ[ad] for ad in izinli if ad in os.environ}

    def run(self, tool: str, cwd: Path, prompt_path: Path) -> RunnerOutcome:
        # Eşleme ÇAĞRI ANINDA okunur: testler onu yerinden oynatarak gerçek alt
        # süreç davranışını zararsız bir komutla ölçebilsin diye.
        spec = ARAC_KOMUTLARI.get(tool)
        if spec is None:
            raise ValueError(
                f"araç kapalı kümenin dışında: {tool!r} — "
                f"{sorted(ARAC_KOMUTLARI)}"
            )
        istem = Path(prompt_path).read_bytes()
        try:
            tamamlanan = subprocess.run(  # noqa: S603 — argv KAPALI eşlemeden
                list(spec.argv),
                cwd=str(cwd),
                env=self._alt_surec_ortami(),
                input=istem,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=self.zaman_asimi_sn,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = self._metin(exc.stdout)
            stderr = self._metin(exc.stderr)
            self._gunlukle(tool, "zaman-asimi", stderr)
            return RunnerOutcome(
                durum="zaman-asimi", stdout=stdout, stderr=stderr, exit_code=None
            )

        stdout = self._metin(tamamlanan.stdout)
        stderr = self._metin(tamamlanan.stderr)
        kod = tamamlanan.returncode
        if kod != 0:
            durum = "hata"
        elif not stdout.strip():
            # Sessiz başarı YOK: sıfır dönüp hiçbir şey yazmayan araç, boş bir
            # raporu geçerli sayan bir yol açardı.
            durum = "hata"
        else:
            durum = "tamam"
        self._gunlukle(tool, durum, stderr)
        return RunnerOutcome(
            durum=durum, stdout=stdout, stderr=stderr, exit_code=kod
        )


@dataclass(frozen=True)
class ValidatedAuditPair:
    """Motorun kabul ettiği TEK envanter tipi (K-150: tam iki denetçi).

    **TEK ÜRETİCİSİ `check_snapshot_agreement`'tır.** Sınıf başka hiçbir modülde
    KURULMAZ; kurulsaydı doğrulayıcıyı ve mutabakat kapısını atlayan ikinci bir
    yol doğardı — arayüz eki R6'nın kapattığı sınıfın ta kendisi. Yapısal tarama
    (`test_validated_pair_constructed_only_in_check_snapshot_agreement`) bunu
    kavramdan türetilmiş desenle ölçer.

    Tip TUTARSIZ KURULAMAZ: roller `DENETCI_ROLLERI` sırasına bağlıdır ve
    taşınan görüntü hash'i İKİ raporun hash'iyle de örtüşmek zorundadır.
    """

    birinci: AuditReport
    ikinci: AuditReport
    unit_snapshot_sha: str
    kaynak_seti_sha: str

    def __post_init__(self) -> None:
        for alan, beklenen_rol in (
            ("birinci", DENETCI_ROLLERI[0]),
            ("ikinci", DENETCI_ROLLERI[1]),
        ):
            rapor = getattr(self, alan)
            if type(rapor) is not AuditReport:
                raise TypeError(
                    f"ValidatedAuditPair.{alan} yalnız AuditReport taşır "
                    f"({type(rapor).__name__} verildi) — benzeyen nesne kabul "
                    "edilmez"
                )
            if rapor.denetci != beklenen_rol:
                raise ValueError(
                    f"ValidatedAuditPair.{alan} {beklenen_rol!r} raporunu "
                    f"taşımalı, {rapor.denetci!r} verildi — alan kimliğe "
                    "bağlıdır, konuma değil"
                )
        for _alan in ("unit_snapshot_sha", "kaynak_seti_sha"):
            _deger = getattr(self, _alan)
            if not isinstance(_deger, str) or not _deger:
                raise ValueError(
                    f"ValidatedAuditPair.{_alan} boş olamaz: {_deger!r}"
                )
        for alan in ("birinci", "ikinci"):
            rapor = getattr(self, alan)
            if rapor.unit_snapshot_sha != self.unit_snapshot_sha:
                raise ValueError(
                    f"ValidatedAuditPair tutarsız: {alan} raporunun görüntü "
                    f"hash'i {rapor.unit_snapshot_sha}, çiftin taşıdığı "
                    f"{self.unit_snapshot_sha} — ayrışan görüntüye yazılmış iki "
                    "rapor tek envanter olamaz (K-79/K-100)"
                )


@dataclass(frozen=True)
class SnapshotAgreement:
    """Mutabakat kapısının sonucu — İKİ HÂL VARDIR, üçüncüsü YOKTUR."""

    cift: ValidatedAuditPair | None
    errors: tuple[str, ...]

    def __post_init__(self) -> None:
        # `ValidatedReport` ile AYNI iki-hâl kuralı — üçüncü hâl yapım hatasıdır.
        # Normalizasyon kontrolden ÖNCE; takma ad da PAYLAŞILMAZ.
        object.__setattr__(self, "errors", tuple(self.errors))
        if (self.cift is None) != bool(self.errors):
            raise ValueError(
                "SnapshotAgreement tutarsız: cift ile errors birlikte karar "
                f"verir (cift={'None' if self.cift is None else 'dolu'}, "
                f"errors={len(self.errors)})"
            )

    @property
    def gecerli(self) -> bool:
        """İKİ koşul BİRDEN — çift VAR ve hata YOK."""
        return self.cift is not None and not self.errors


@dataclass(frozen=True)
class AuditRound:
    """Bir denetim turunun sonucu.

    Plan `reports: list[AuditReport]` yazar; arayüz eki R6(e) BAĞLAYICIDIR ve
    geçerlilik taşıyan koleksiyon DEĞİŞTİRİLEMEZ olur: alan kopyalanıp demete
    çevrilir, öğe tipleri sınanır (`AuditReport` donmuş dataclass'tır ve
    `identity.donmus`'un KAPALI kümesinin dışındadır — kural 5).

    Tur TUTARSIZ KURULAMAZ: geçerli bir tur TAM İKİ rol taşır ve sebepsizdir;
    geçersiz bir tur rapor taşımaz ve sebebi VARDIR. "Sebepsiz geçersiz tur"
    K-150'yi okunamaz kılardı — sentezin neden başlamadığı kayda geçmek zorunda.
    """

    reports: tuple[AuditReport, ...]
    gecerli: bool
    sebep: str | None

    def __post_init__(self) -> None:
        deger = tuple(self.reports)
        for oge in deger:
            if type(oge) is not AuditReport:
                raise TypeError(
                    f"AuditRound.reports yalnız AuditReport taşır "
                    f"({type(oge).__name__} verildi) — benzeyen nesne kabul "
                    "edilmez"
                )
        object.__setattr__(self, "reports", deger)
        if not isinstance(self.gecerli, bool):
            raise TypeError(
                f"AuditRound.gecerli bool olmalı: {type(self.gecerli).__name__}"
            )
        if self.gecerli:
            roller = tuple(rapor.denetci for rapor in deger)
            if roller != DENETCI_ROLLERI:
                raise ValueError(
                    "AuditRound tutarsız: geçerli tur DENETCI_ROLLERI'nin "
                    f"ikisini de sırayla taşır, {roller} verildi (K-150: tek "
                    "raporla ilerleme YOKTUR)"
                )
            if self.sebep is not None:
                raise ValueError(
                    f"AuditRound tutarsız: geçerli tur sebep TAŞIMAZ: "
                    f"{self.sebep!r}"
                )
        else:
            if deger:
                raise ValueError(
                    "AuditRound tutarsız: geçersiz tur rapor TAŞIMAZ "
                    f"({len(deger)} rapor verildi) — yarım envanter motora "
                    "ulaşamaz"
                )
            if not (isinstance(self.sebep, str) and self.sebep.strip()):
                raise ValueError(
                    "AuditRound tutarsız: geçersiz tur SEBEPSİZ kurulamaz — "
                    "sentezi durduran şey kayda geçer"
                )


def check_snapshot_agreement(
    validated: tuple[ValidatedReport, ValidatedReport],
    *,
    expected_snapshot_sha: str,
    expected_kaynak_sha: str,
) -> SnapshotAgreement:
    """Çapraz denetçi mutabakatı — TUR seviyesi kapı (arayüz eki R6(c)).

    Girdi HAM rapor DEĞİL, `validate_report`'un dönüşüdür. DÖRT koşul birden
    aranır:

    (1) iki `ValidatedReport`'un İKİSİ de `gecerli` — biri değilse `cift=None`
        ve hataları `errors`'a birleştirilir (K-150 fail-closed);
    (2) iki raporun `denetci` alanları `DENETCI_ROLLERI`nin ikisini de TAM BİR
        KEZ kapsar (aynı rolden iki rapor REDDEDİLİR);
    (3) her raporun `unit_snapshot_sha`'sı `expected_snapshot_sha`'ya EŞİT;
    (4) iki raporun `unit_snapshot_sha`'ları birbirine EŞİT (K-79/K-100).

    `expected_kaynak_sha` KAPI DEĞİLDİR, TAŞIMADIR: tek rapor gören bu imzada
    karşılaştırılacak ikinci bir kaynak-kümesi taşıyıcısı yoktur. Değer paketten
    gelir (`PacketRef.kaynak_seti_sha`, `build_packet`'in doğruladığı rapor
    kümesinden TÜRETİLMİŞTİR) ve çifte mühürlenir; karşılaştırma bir katman
    sonra, `EngineInputs` yapımında yapılır — motora verilen mekanik kapının bu
    paketi kuran kapı olduğu ORADA ölçülür.

    Dördü de geçerse `ValidatedAuditPair` üretilir — BAŞKA ÜRETİCİ YOKTUR. Bir
    koşul düşerse `cift` `None`'dır ve tur GEÇERSİZDİR.

    Çift kurulurken raporlar KİMLİĞE anahtarlanır (`denetci` alanı), girdi
    KONUMUNA değil: konumsal okuma, sırası kaymış bir çağrıda rolleri sessizce
    takas ederdi.

    **Ölçülmüş kapsam sınırı (dürüst etiket, İlke 3).** (4) numaralı koşul (3)
    numaralının MANTIKSAL SONUCUDUR: iki rapor birbirinden ayrışıyorsa en az
    biri `expected_snapshot_sha`'dan da ayrışır ve (3) zaten düşer. İkisi de
    ekin bağladığı biçimde kodda DURUR (savunma derinliği), ama (4) TEK BAŞINA
    erişilebilir bir dal DEĞİLDİR — yalnız onu kaldıran mutasyon (M8) hiçbir
    testi kırmızılaştırmadı. Bu, "(4)'ün kendi testi var" diye okunmaz;
    `test_snapshot_gate_matrix_over_hash_axes` ekseni bütün olarak kapatır.
    """
    sonuclar = tuple(validated)
    errors: list[str] = []
    if len(sonuclar) != 2:
        return SnapshotAgreement(
            None,
            (
                f"mutabakat kapısı TAM İKİ doğrulama sonucu ister, "
                f"{len(sonuclar)} verildi — K-150 tek raporla ilerlemez",
            ),
        )

    for sonuc in sonuclar:
        if not isinstance(sonuc, ValidatedReport):
            raise TypeError(
                "check_snapshot_agreement girdisi ValidatedReport olmalı: "
                f"{type(sonuc).__name__} — ham rapor kapıya ULAŞAMAZ"
            )
        if not sonuc.gecerli:
            errors.extend(sonuc.errors)
    if errors:
        return SnapshotAgreement(None, tuple(errors))

    raporlar = [sonuc.rapor for sonuc in sonuclar]
    roller = sorted(rapor.denetci for rapor in raporlar)
    if roller != sorted(DENETCI_ROLLERI):
        errors.append(
            f"mutabakat kapısı: iki rapor DENETCI_ROLLERI'ni tam bir kez "
            f"kapsamıyor (bulunan roller {roller}, beklenen "
            f"{sorted(DENETCI_ROLLERI)}) — aynı rolden iki rapor iki denetçi "
            "sayılamaz"
        )
    for rapor in raporlar:
        if rapor.unit_snapshot_sha != expected_snapshot_sha:
            errors.append(
                f"mutabakat kapısı: {rapor.denetci} raporu paketin anlık "
                f"görüntüsüne yazılmamış (rapor {rapor.unit_snapshot_sha}, "
                f"paket {expected_snapshot_sha})"
            )
    if raporlar[0].unit_snapshot_sha != raporlar[1].unit_snapshot_sha:
        errors.append(
            "mutabakat kapısı: iki rapor AYRI anlık görüntüye karşı yazılmış "
            f"({raporlar[0].unit_snapshot_sha} ≠ {raporlar[1].unit_snapshot_sha}) "
            "— farklı girdi gören iki rapor mutabakat kanıtlayamaz (K-79/K-100)"
        )
    if errors:
        return SnapshotAgreement(None, tuple(errors))

    esleme = {rapor.denetci: rapor for rapor in raporlar}
    return SnapshotAgreement(
        ValidatedAuditPair(
            birinci=esleme[DENETCI_ROLLERI[0]],
            ikinci=esleme[DENETCI_ROLLERI[1]],
            unit_snapshot_sha=expected_snapshot_sha,
            kaynak_seti_sha=expected_kaynak_sha,
        ),
        (),
    )


def _tur_dosyasi(dizin: Path, rol: str) -> Path:
    return dizin / RAPOR_DOSYA_KALIBI.format(rol)


def _kalicilastir(packet: PacketRef, ham: Mapping[str, str]) -> str | None:
    """Bellekte tutulan raporları diske indirir — var olan dosya EZİLMEZ.

    **Neden GEÇ yazılıyor (B3(1)).** Denetçi-1'in raporu diske indiği ANDAN
    itibaren denetçi-2'nin adresleyebileceği bir dosyadır (`cwd` okumayı
    sınırlamaz). Gözlenebilir sızıntı kanalı budur; yazımı iki rol de bitene
    kadar ertelemek onu kapatır. Denetçi-2 DÜŞSE bile denetçi-1'in raporu yine
    yazılır — kanıt kaybolmaz ve düşen rol zaten koşmadığı için sızıntı yoktur.

    Dönüş: hata yoksa `None`, bir ya da daha çok rol yazılamadıysa TOPLU SEBEP.

    **Koruma rol BAŞINADIR, döngü başına DEĞİL (B6).** Her rolün yazımı kendi
    `except OSError` kolundadır: denetçi-1'in izin/disk arızası döngüyü
    KESMEZ, sebep listesine eklenir ve denetçi-2'nin yazılabilir, TAMAMLANMIŞ
    raporu yine denenir. Döngü başına tek koruma, arızayı ilk gören rolün
    ötesindeki kanıtı hiç denemeden düşürürdü — üstelik `finally`'nin yeniden
    çağırması da işe yaramazdı: süpürme yine ilk roldeki aynı arızaya
    çarpardı. `FileExistsError` bu kümenin ADLANDIRILMIŞ alt hâlidir (K-82
    salt-eklemelik) ve kendi sebebini taşır.

    Yutulan şey ARIZANIN İSTİSNASIDIR, arızanın KENDİSİ değil: sebep dönüşe
    girer, çağıran turu `tamamlanmadi` işaretler (fail-closed korunur).
    """
    sebepler: list[str] = []
    for rol in DENETCI_ROLLERI:
        if rol not in ham:
            continue
        hedef = _tur_dosyasi(packet.kopyalar[rol], rol)
        try:
            # Salt-eklemeli açılış: var olan kısmi rapor EZİLMEZ (K-82).
            with open(hedef, "x", encoding="utf-8") as akis:
                akis.write(ham[rol])
        except FileExistsError:
            sebepler.append(
                f"denetim turu {rol} raporunu yazamadı: {hedef} ZATEN var — "
                "ham katman salt-eklemedir, dosya EZİLMEZ (K-82); yeniden "
                "koşum yeni kimlik alır"
            )
        except OSError as exc:
            _LOG.warning(
                "denetim turu %s raporunu yazamadı: %s", rol, hedef,
                exc_info=True,
            )
            sebepler.append(
                f"denetim turu {rol} raporunu yazamadı "
                f"({type(exc).__name__}): "
                + runs.mask_secrets(str(exc) or "<sebep boş>")
                + " — KALAN roller yine denendi"
            )
    return " · ".join(sebepler) if sebepler else None


def _hedef_rapor_kapisi(packet: PacketRef) -> str | None:
    """Hedef rapor dosyaları BOŞ olmak ZORUNDA — ilk runner'dan ÖNCE ölçülür.

    Çakışmayı `_kalicilastir` da görür, ama ORADA görmek GEÇTİR: önceki turdan
    kalmış bir `RAPOR-denetci-1.md`, denetçi-2 koşarken diskte DURUR ve K-79'un
    kapattığı gözlenebilir sızıntı kanalını yeniden açar. Geç yazım kanalı
    ancak hedef dizin başlangıçta boşsa kapatır; bu yüzden karar KABUL
    BÖLGESİNDEDİR ve tur hiç başlamaz.

    `_kalicilastir`'ın `open(..., "x")` açılışı YERİNE GEÇMEZ — o, yarış
    penceresini kapatan atomik ayaktır; bu kapı ise sızıntıyı kapatan sıra
    ayağıdır.
    """
    var_olanlar = [
        str(_tur_dosyasi(packet.kopyalar[rol], rol))
        for rol in DENETCI_ROLLERI
        if _tur_dosyasi(packet.kopyalar[rol], rol).exists()
    ]
    if not var_olanlar:
        return None
    return (
        "denetim turu BAŞLAMADI: hedef rapor dosyası ZATEN var "
        f"({' · '.join(var_olanlar)}) — ham katman salt-eklemedir (K-82) ve "
        "önceki turdan kalmış rapor denetçi-2 koşarken diskte durup kör "
        "bağımsızlığı düşürür; yeniden koşum yeni kimlik alır"
    )


def _kosum_ani_yol_kapisi(
    packet: PacketRef, *, onek: str = "denetim turu BAŞLAMADI"
) -> str | None:
    """Yol sözleşmesini KOŞUM ANINDA, ilk mutasyondan ÖNCE yeniden ölçer.

    `PacketRef` yol kapısı yalnız YAPIM anında koşar. Bir rol dizini — ya da
    paket KÖKÜNÜN kendisi — yapımdan sonra bayt-özdeş bir DIŞ ağaca symlink'le
    değiştirilirse parmak izi, saklı özet ve kardeş karşılaştırma üçü birden
    eşleşir; kapı geçer ve runner paket kökünün DIŞINDA koşar.

    Yeni kural YOKTUR: `PacketRef`'in kendi yol kapısı (`kok_yolunu_kapila` +
    rol yolu canonical eşitliği) OLDUĞU GİBİ yeniden çağrılır. KABUL
    BÖLGESİNDEKİ çağrısı kiralama dâhil HİÇBİR mutasyondan önce koşar —
    baştan geçersiz bir paket diskte iz bırakmaz. Rol döngüsündeki çağrısı ise
    her `runner.run`'dan hemen öncedir: orada tur zaten başlamıştır, kapatılan
    şey KALAN rolün alt sürecidir.

    `onek` YALNIZ sebebin ilk cümlesidir: kapı kabul bölgesinde turun HİÇ
    başlamadığı yerde de, rol döngüsünde turun DURDUĞU yerde de aynı kuralı
    ölçer; "BAŞLAMADI" ikinci yerde yanlış olurdu.
    """
    try:
        packet._rol_yollarini_kapila()
    except ValueError as hata:
        return f"{onek}: paket yol kapısı koşum anında düştü — {hata}"
    return None


KIRALAMA_DIZIN_ADI = ".kiralama"
"""Paket başına kiralamanın dizin adı — kökün ALTINDA, rol ağaçlarının DIŞINDA.

Rol ağaçlarının içine konsaydı koşum anı parmak izini kendisi bozardı.
"""

KIRALAMA_SAHIP_DOSYASI = "sahip"
"""Kiralamanın adli izi. DEVRALMA GİRDİSİ DEĞİLDİR — okunmaz, yalnız yazılır."""


def _kiralama_yolu(packet: PacketRef) -> Path:
    return packet.kok / KIRALAMA_DIZIN_ADI


def _kiralamayi_al(packet: PacketRef) -> str | None:
    """Paket başına ATOMİK kiralama alır (B7). Dönüş: alınamadıysa SEBEP.

    **Neden kiralama.** Hedef rapor çakışma kontrolü bir SIRA kapısıdır, kilit
    değildi: iki süreç aynı paket için kabul bölgesinden BİRLİKTE geçebilir ve
    biri raporlarını yazarken ötekinin denetçi-2'si koşuyor olabilirdi.
    `open(..., "x")` üzerine yazmayı engeller ama o denetçinin rakip raporu
    GÖRMESİNİ engellemez — yani eksik olan sıralama değil, K-79 körlüğüydü.

    **Atomiklik dosya sistemindedir.** `mkdir` tek ve bölünmez bir sistem
    çağrısıdır: iki süreçten yalnız biri kazanır, öteki `FileExistsError` alır.
    Yeni bir servis ya da bağımlılık EKLENMEZ.

    **ÖLÜ KİLİT DAVRANIŞI — açık seçim ve beyan.** Kiralama HİÇBİR KOŞULDA
    OTOMATİK DEVRALINMAZ: ne zaman aşımıyla, ne PID canlılığıyla, ne de sahip
    notundaki damgayla. Bu bir eksiklik değil, gerekçeli bir seçimdir —
    devralma eşiği, YAVAŞ ama CANLI bir sahibin kiralamasını çalar ve tam da
    kapatmak için var olduğumuz eşzamanlı-iki-tur durumunu geri açardı; üstelik
    duvar saati ve PID yeniden kullanımı ölçülemeyen sezgilerdir.

    Devralmanın GEREKMEMESİ yapısaldır: kiralama PAKET KÖKÜ başınadır, kök ise
    `<dest>/<run_id>` olduğu için koşu kimliği başınadır ve ham katman
    salt-eklemedir (K-82) — yeniden koşum YENİ kimlik, dolayısıyla YENİ kök ve
    YENİ kiralama alır. Sahibi düşen bir kiralama yalnız KENDİ koşusunun
    kökünü kapatır; zaten yeniden koşulamayacak olan kökü. İnsan kurtarması
    tek işlemdir: o dizini silmek.

    Serbest bırakma sahibin `finally` yolundadır ve sahiplenmeyen tur ASLA
    silmez (çağıran bunu bayrakla korur).
    """
    yol = _kiralama_yolu(packet)
    try:
        yol.mkdir()
    except FileExistsError:
        return (
            "denetim turu BAŞLAMADI: paket kiralaması BAŞKASINDA "
            f"({yol}) — aynı paket için eşzamanlı ikinci bir tur, denetçilerin "
            "rakip raporları görmesine yol açardı (K-79). Kiralama otomatik "
            "DEVRALINMAZ; sahibi düştüyse yeniden koşum YENİ kimlik alır"
        )
    try:
        (yol / KIRALAMA_SAHIP_DOSYASI).write_text(
            f"run_id={packet.run_id}\npid={os.getpid()}\n", encoding="utf-8"
        )
    except OSError:  # adli iz yazılamadı — kiralama YİNE geçerlidir
        _LOG.warning(
            "kiralama sahip notu yazılamadı: run_id=%s", packet.run_id,
            exc_info=True,
        )
    return None


def _kiralamayi_birak(packet: PacketRef) -> None:
    """Kiralamayı SAHİBİ bırakır — arıza asıl istisnayı MASKELEMEZ."""
    yol = _kiralama_yolu(packet)
    try:
        (yol / KIRALAMA_SAHIP_DOSYASI).unlink(missing_ok=True)
        yol.rmdir()
    except OSError:
        _LOG.warning(
            "kiralama bırakılamadı: run_id=%s yol=%s", packet.run_id, yol,
            exc_info=True,
        )


def _rol_agaci_parmagi(dizin: Path) -> tuple[dict[str, str], list[str]]:
    """Rol ağacının KOŞUM ANI parmak izi + reddedilen düğümler.

    Kural paket KURULUMUNDAKİ kuralın AYNISIDIR (`build_packet`): eşleme
    `{göreli yol: sha256(baytlar)}` ve özet `identity.canonical_sha`. İki ayrı
    kural yazılsaydı ölçüm ile beyan aynı ağaç için farklı özet üretir, kapı da
    her koşumda yalan söylerdi. Kurulum düz dosya yazdığı için özyinelemeli
    süpürme aynı eşlemeyi verir; alt dizin BELİRİRSE anahtar kümesi ayrışır ve
    kapı bunu görür.

    Süpürme symlink İZLEMEZ (`os.scandir` + `follow_symlinks=False`): izleyen
    bir süpürme, symlink çemberinde asılır ve reddetmesi gereken düğümü
    ölçmeye kalkardı. Symlink ve düzenli-olmayan düğümler parmak izine
    GİRMEZ, ayrı listede REDDEDİLİR — çünkü bayt-özdeş bir ikize kurulan
    symlink özeti DEĞİŞTİRMEZ ama rol ağacını paketin dışına açar.

    **Ölçülmemiş kapsam sınırı (dürüst etiket).** BOŞ bir alt dizinin
    sonradan eklenmesi parmak izini değiştirmez ve bu kapı onu GÖRMEZ; kural
    kurulumdakiyle özdeş tutulduğu için dosyasız düğüm özete girmez.
    """
    parmak: dict[str, str] = {}
    reddedilen: list[str] = []

    # Süpürme kökü `os.scandir` ile AÇILIR, yani kökün KENDİ düğüm tipi
    # çocuklarına uygulanan symlink kuralının DIŞINDA kalırdı: rol dizini
    # bayt-özdeş bir dış ikize symlink'lenirse scandir onu izler ve özet
    # eşleşir. Kök açıkça reddedilir.
    if Path(dizin).is_symlink():
        return {}, ["<ağaç kökü> (symlink)"]

    def _gez(kok: Path, onek: str) -> None:
        with os.scandir(kok) as girisler:
            sirali = sorted(girisler, key=lambda giris: giris.name)
        for giris in sirali:
            goreli = f"{onek}{giris.name}"
            if giris.is_symlink():
                reddedilen.append(f"{goreli} (symlink)")
                continue
            if giris.is_dir(follow_symlinks=False):
                _gez(Path(giris.path), f"{goreli}/")
                continue
            if not giris.is_file(follow_symlinks=False):
                reddedilen.append(f"{goreli} (düzenli dosya DEĞİL)")
                continue
            parmak[goreli] = hashlib.sha256(
                Path(giris.path).read_bytes()
            ).hexdigest()

    _gez(dizin, "")
    return parmak, reddedilen


def _paket_butunluk_kapisi(packet: PacketRef) -> str | None:
    """KOŞUM ANINDA ölçülen bayt-özdeşlik ve düğüm tipi (B7 · K-79).

    `PacketRef` yalnız YAPIM anında, üstelik iki BEYAN edilen özeti birbirine
    karşı ölçer; altındaki dosyalar yapımdan sonra değişebilir. Bayat ya da
    değiştirilmiş bir paket runner'lara ulaşırsa iki denetçi FARKLI girdi görür
    ve mutabakat kapısı ölçtüğünü sandığı şeyi ölçmez. Bu yüzden parmak izi
    ilk runner'dan ÖNCE, kiralama ALTINDA yeniden hesaplanır.

    İki karşılaştırma da yapılır: her ağaç kendi SAKLI özetine karşı, ardından
    iki ağaç BİRBİRİNE karşı. İkincisi bugün birinciden türer (`PacketRef`
    saklı özetlerin eşitliğini zorlar), yani tek başına hiçbir mutasyonu
    yakalamaz — kasıtlı bir yedek koldur ve dürüstçe böyle etiketlenir.

    Kapı `_hedef_rapor_kapisi`'nden SONRA koşar: turun KENDİ rapor dosyası o
    kapı geçtikten sonra provably yoktur, dolayısıyla ağaçtan dışlanacak ad
    yoktur ve `RAPOR-*` adlı bir kaçak dosya da burada yakalanır.
    """
    hatalar: list[str] = []
    olculen: dict[str, str] = {}
    for rol in DENETCI_ROLLERI:
        dizin = packet.kopyalar[rol]
        parmak, reddedilen = _rol_agaci_parmagi(dizin)
        if reddedilen:
            hatalar.append(
                f"{rol} ağacında symlink/düzensiz alt düğüm var "
                f"({' · '.join(reddedilen)}) — rol ağacı paketin DIŞINA "
                "açılamaz; baytlar aynı kalsa bile düğüm tipi kör ayrımı düşürür"
            )
            continue
        sha = identity.canonical_sha(parmak)
        olculen[rol] = sha
        if sha != packet.kopya_shalari[rol]:
            hatalar.append(
                f"{rol} ağacı paket YAPILDIKTAN SONRA değişti (beyan "
                f"{packet.kopya_shalari[rol]}, koşum anı ölçümü {sha})"
            )
    if not hatalar and len(set(olculen.values())) != 1:
        hatalar.append(
            "iki rol ağacı koşum anında bayt-özdeş DEĞİL "
            f"({olculen}) — farklı girdi gören iki rapor mutabakat "
            "kanıtlayamaz (K-79)"
        )
    if not hatalar:
        return None
    return (
        "denetim turu BAŞLAMADI: paket bütünlük kapısı düştü — "
        + " · ".join(hatalar)
    )


def _tur_url_kapisi(
    rapor: AuditReport,
    *,
    yetkili_kaynak_sayisi: int,
    on_kontrol: PreflightResult,
) -> list[str]:
    """B4 (F3) — URL tamlığı raporun KENDİ beyanıyla doğrulanamaz.

    `validate_report` tek rapor görür ve yalnız beyanın İÇ tutarlılığını ölçer
    (arayüz eki R6: "çapraz denetçi karşılaştırması BURADA YAPILMAZ"). Bu
    yüzden iki karşılaştırma TUR seviyesindedir ve imza DEĞİŞMEZ:

    (a) **Yetkili sayı.** Raporun `Kaynak sayısı: <n>` beyanı, paketi kuran
        tarafın `yetkili_kaynak_sayisi`'sına EŞİT olmak zorundadır. O değer
        `len(sources)` DEĞİL, **ELENMEMİŞ KİMLİK sayısıdır** (2026-09-10;
        eskisi elemeli her meşru turu düşürüyordu — sözleşme ADIM 2 hem
        oranı hem satır sayısını KALAN kaynağa uyarlatır). Örnek: üç kaynakla
        PAKETLENİP hiçbiri elenmemiş bir koşuda "Kaynak sayısı: 2" yazan rapor
        altı satırla iç tutarlıdır ama koşunun ÜÇÜNCÜ kaynağını hiç
        örneklememiştir. Elenen kaynağın KONUMU korunur (kör etiket konumdan
        türer); düşen yalnız SAYIdır.
    (b) **Ortam-kısıtı muafiyeti.** Kaçış cümlesi TÜM satır beklentisini
        kaldırır ve muafiyet YALNIZ `PreflightDurumu.ERISIM_YOK`'ta —
        yani ölçülmüş erişimSİZLİKTE — meşrudur. `ERISIM_VAR`'da muafiyet
        ölçülmüş erişimin üstüne yazılmış olur; `OLCULMEDI`/`OLCUM_ARIZASI`'nda
        ise ölçüm hiç yapılmamıştır ve "ölçülmedi" muafiyet ÜRETMEZ. Bu ayrım
        olmasaydı ölçmemek, ölçüp erişimsiz bulmakla aynı yetkiyi verirdi.

    **Ölçülmüş kapsam sınırı (dürüst etiket).** `run_audit_round`'un başlama
    kapısı YALNIZ `ERISIM_VAR`'ı geçirdiği için (b) o yoldan BUGÜN
    ERİŞİLEMEZDİR: turu başlatan her ön kontrol muafiyeti zaten yasaklar.
    Fonksiyon yine de kendi başına doğrudur ve doğrudan çağrıldığında dört
    durumun dördünü de ayırır; ölçüm o düzeydedir. "Erişim gerçekten yoktu"
    iddiası bu turda DOĞRULANMADI — probu sağlayan katman Task 11'dir.
    """
    govde = rapor.bolumler[BOLUM_ANAHTARLARI[1]]
    errors: list[str] = []
    eslesme = _KAYNAK_SAYISI_RE.search(govde)
    if eslesme is None:
        # Biçim kapısı bunu zaten düşürür; ikinci kez fail-closed durulur.
        errors.append(
            f"tur kapısı: {rapor.denetci} raporu kaynak sayısı beyanı "
            "TAŞIMIYOR — yetkili sayıyla karşılaştırılamaz"
        )
    elif int(eslesme.group(1)) != yetkili_kaynak_sayisi:
        errors.append(
            f"tur kapısı: {rapor.denetci} raporu {int(eslesme.group(1))} kaynak "
            f"beyan etti, koşunun YETKİLİ kaynak sayısı "
            f"{yetkili_kaynak_sayisi} — tamlık raporun kendi beyanıyla "
            "doğrulanamaz, paketi kuran taraf yetkilidir"
        )
    if _ORTAM_KISITI in govde and not on_kontrol.muafiyet_mesru:
        errors.append(
            f"tur kapısı: {rapor.denetci} raporu ortam kısıtı muafiyeti "
            f"kullandı ({_ORTAM_KISITI}) ama K-14 ön kontrolü "
            f"{on_kontrol.arac} için '{on_kontrol.durum.value}' ölçtü — "
            "muafiyet YALNIZ ÖLÇÜLMÜŞ erişimsizlikte meşrudur; ölçülmemiş "
            "erişimin üstüne yazılan muafiyet URL doğrulamasını atlatır"
        )
    return errors


def _tur_sinif_kapisi(
    rapor: AuditReport, *, yetkili_kaynak_sayisi: int
) -> list[str]:
    """Oran yazımının SAĞ tarafı koşunun YETKİLİ kaynak sayısına eşit mi.

    `_denetim_tablosu` tek rapor görür (R6) ve orada yalnız oranın İÇ
    tutarlılığı ölçülebilir: sol sayı `kaynaklar` hücresindeki numara sayısına
    eşit mi, sağ sayı ondan küçük değil mi. *"Sağ sayı koşuya giren kaynak
    sayısıdır"* hükmü o imzada ÖLÇÜLEMEZ — yetkili sayıyı paketi kuran taraf
    taşır. Emsal ve gerekçe `_tur_url_kapisi` ile aynıdır: rapor kendi
    beyanıyla tamlık kanıtlayamaz.

    Ölçülen tam olarak şudur: elemeden sonra iki kaynakla koşulan bir turda
    `2-3` yazan satır, koşunun ÜÇÜNCÜ kaynağı varmış gibi sınıflandırılmıştır
    — sözleşme ADIM 2 o durumda oranı `2-2`'ye uyarlatır. `tekil` ve `çelişki`
    etiketleri oran taşımaz ve bu kapıya GİRMEZ.
    """
    errors: list[str] = []
    for satir in rapor.denetim_tablosu:
        oran = _SINIF_ORAN_RE.match(satir.sinif)
        if oran is None:
            continue
        sag = int(oran.group(2))
        if sag != yetkili_kaynak_sayisi:
            errors.append(
                f"tur kapısı: {rapor.denetci} raporu denetim tablosu satırı "
                f"{satir.no} `sınıf` {satir.sinif!r} yazdı ama koşunun YETKİLİ "
                f"kaynak sayısı {yetkili_kaynak_sayisi} — eleme sonrası "
                "sınıflandırma kalan kaynak sayısına uyarlanır (ADIM 2); "
                "uyarlanmamış oran denetimin kapsamını yanlış gösterir"
            )
    return errors


async def run_audit_round(
    db,
    packet: PacketRef,
    *,
    runner: Runner,
    run_id: str,
    web_prob: Callable[[str], bool] | None = None,
) -> AuditRound:
    """İki kör denetçiyi SIRAYLA koşturur ve turu mutabakat kapısından geçirir.

    **UYGULAMA SINIRI TEKTİR.** Gövde iki bölgeye ayrılır ve kapılar tek yerde
    uygulanır — bu sınıfın kapanışı budur (ölçüm kararın uygulandığı yere
    konur, üretildiği yere değil):

    * **KABUL BÖLGESİ** — ilk yan etkiden (alt süreç · dosya yazımı · DB
      mutasyonu) ÖNCE biter ve TÜM giriş kapılarını uygular: kimlik bağı, K-14
      ön kontrol KARARI, paket KİRALAMASI, hedef rapor dosyalarının çakışma
      kontrolü ve paket BÜTÜNLÜĞÜ. Bir kapı reddederse hiçbir runner koşmaz ve
      hiçbir rapor dosyası yazılmaz.
    * **KOŞUM BÖLGESİ** — runner'lar, doğrulama ve mutabakat. Kabul bölgesinin
      ön-kontrol ayağı DÂHİL her şey `try` korumasının İÇİNDEDİR: prob
      `BaseException` (iptal) fırlatırsa da koşu satırı işaretsiz kalmaz.

    Bağlayıcı invariantlar bu gövdededir:

    * **KİMLİK BAĞI** — `run_id` ile `packet.run_id` TAM EŞİT olmak ZORUNDA.
      İkisi bağımsız doğrulanıp eşitlikleri ölçülmeseydi A koşusunun paketi
      denetlenip B koşusu `tamamlanmadi` işaretlenebilirdi: dosyalar paketin
      yollarından okunur, arıza ise argümanla adlandırılan SATIRA yazılır.
      Ayrışmada hiçbir alt süreç koşmaz ve hiçbir DB mutasyonu olmaz.
    * **K-78 SIRALI** — döngü `DENETCI_ROLLERI` üzerinde yürür ve bir rol
      bitmeden diğeri başlamaz; sıra deterministiktir.
    * **K-79 AYRI DİZİN** — her rol kendi `packet.kopyalar[rol]` dizininde
      koşar, istem dosyası da o dizinden okunur. KÖKÜN kendisinin ve rol
      yollarının takma ad/symlink/kök-dışı olmadığı `kok_yolunu_kapila`'da
      ölçülür ve kapı İKİ yüzeyde de dosya yaratmadan ÖNCE koşar
      (`build_packet` `mkdir`'den önce, `PacketRef` yapımda).
    * **K-79 GEÇ YAZIM** — denetçi-1'in raporu denetçi-2 çıkana kadar DİSKE
      YAZILMAZ; ikisi de bittikten sonra kalıcılaşır. Geç yazım kanalı ancak
      hedef dizin BAŞTA boşsa kapatır: `_hedef_rapor_kapisi` bunu kabul
      bölgesinde ölçer, `_kaniti_kalicilastir` da yazımı tek çıkışta toplar.
    * **K-79 PAKET KİRALAMASI (B7)** — kabul bölgesi çakışma kontrolünden ÖNCE
      paket kökü altında ATOMİK bir kiralama (`mkdir`) alır ve onu SON
      kalıcılaştırmaya kadar tutar. Çakışma kontrolü tek başına bir SIRA
      kapısıydı: iki süreç aynı paket için kabulden birlikte geçebilir, biri
      raporunu yazarken ötekinin denetçi-2'si koşuyor olabilirdi.
      **Kiralama HİÇBİR KOŞULDA otomatik DEVRALINMAZ** (zaman aşımı · PID
      canlılığı · damga YOK): devralma eşiği yavaş ama CANLI bir sahibin
      kilidini çalar ve kapatılan durumu geri açardı. Devralma gerekmez çünkü
      kiralama koşu kimliği başınadır ve ham katman salt-eklemedir (K-82) —
      yeniden koşum YENİ kimlik, yeni kök, yeni kiralama alır. Ayrıntı ve
      insan kurtarma yolu `_kiralamayi_al` gövdesindedir.
    * **K-79 KOŞUM ANI BÜTÜNLÜĞÜ (B7)** — kiralama altında, ilk runner'dan
      ÖNCE her rol ağacının parmak izi kurulumdaki KURALLA yeniden hesaplanır
      ve hem SAKLI özete hem kardeş ağaca karşı ölçülür; symlink ve düzensiz
      alt düğümler reddedilir. `PacketRef` yalnız YAPIM anında iki BEYANI
      karşılaştırır — bayat ya da değiştirilmiş bir paket runner'lara ulaşıp
      iki denetçiye FARKLI girdi gösterebilirdi.
    * **K-82 DURUM SAHİPLİĞİ** — terminal arızada `runs.mark_incomplete`
      BURADAN çağrılır (runner'ın `db`'si yoktur) ve yazılmış rapor dosyası
      EZİLMEZ: dosyalar salt-eklemeli (`"x"`) açılır.
    * **K-82 İSTİSNA YOLLARI** — turun tamamı bir dış koruma altındadır.
      Beklenen alt süreç/dosya sistemi `OSError`'ları tipli arızaya çevrilir;
      beklenmeyen istisnada ve İPTALDE işaret EN İYİ ÇABAYLA atılır ve istisna
      YENİDEN FIRLATILIR (yutulmaz). Koruma olmasaydı eksik CLI · izin · disk ·
      iptal yollarında satır `calisiyor` olarak ASILI kalırdı — K-82'nin
      kapatmak için var olduğu durum.
    * **K-14 GERÇEK KAPI (fail-closed)** — plan satır 200-201 BAĞLAYICIDIR:
      "HER turdan önce ZORUNLU ve mekanik ... başarısızsa tur BAŞLAMAZ".
      `preflight` yalnız ÖLÇMEZ, KARAR verir: rollerden birinin durumu
      `PreflightDurumu.ERISIM_VAR` değilse tur hiç başlamaz, koşu
      `tamamlanmadi` işaretlenir ve sebep ölçülen durumu adlandırır. Sonuç
      ayrıca tur seviyesindeki ortam-kısıtı kapısını besler — muafiyet YALNIZ
      `ERISIM_YOK`'ta meşrudur, "ölçülmedi" muafiyet ÜRETMEZ.

      **Bugünkü davranış (dürüst etiket).** `web_prob=None` bu modüldeki tek
      yol olduğu için kapı probsuz her çağrıyı BLOKE EDER; probu sağlayan
      katman Task 11'dir (CLI). Bu bilinçli bir davranış değişikliğidir:
      ölçülmemiş erişimle tur başlatmak, "ölçmedim" ile "ölçtüm, yok"u aynı
      yetkiye eşitliyordu.
    * **KANIT TEK ÇIKIŞTA KALICILAŞIR** — tamamlanmış raporlar DÖRT çıkış
      yolunun (normal başarı/arıza · `OSError` · iptal · beklenmeyen istisna)
      dördünde de yazılır; yazım TEK yardımcıdadır (`_kaniti_kalicilastir`) ve
      `finally`'den çağrılır. Dal başına kopyalanmış yazım, iki dalda
      unutulduğu için denetçi-1'in raporunu kaybediyordu. Kalıcılaştırma
      arızası asıl istisnayı MASKELEMEZ.
    * **K-136** — koşu sebebine giden stderr maskeleme süzgecinden geçer.
    * **K-150 FAIL-CLOSED** — iki GEÇERLİ rapor yoksa çift kurulmaz, tur
      geçersizdir ve sentez BAŞLAMAZ.
    * **LLM çıktısı VERİDİR** — gövde yalnız dosyaya yazılır ve
      `validate_report` biçim kapısına verilir; içindeki yönerge yürütülmez.

    **Doğrulama düşüşü TERMİNAL hata DEĞİLDİR (bilinçli, beyan edilir).** Rapor
    biçim/veri kapısını ya da tur kapısını geçemezse tur geçersiz döner ama koşu
    `tamamlanmadi` İŞARETLENMEZ: K-150 "eksik denetçi yeniden koşulur" der ve
    yarım işareti yeniden koşumun önünü keserdi. `tamamlanmadi` yalnız aracın
    KENDİSİ düştüğünde (zaman aşımı · sıfırdan farklı çıkış · boş çıktı · dosya
    çakışması · alt süreç istisnası · rapor YAZILAMADI) ya da tur ÇEVRESEL bir
    kapıdan hiç başlayamadığında (K-14 ön kontrol · paket kiralaması · hedef
    dosya çakışması · paket bütünlüğü) yazılır. İkinci
    küme de yeniden koşuma açıktır; işaretin amacı satırın `calisiyor` olarak
    ASILI kalmamasıdır.

    **KALAN RİSK — dürüst beyan (B3).** `cwd` bir güvenlik sınırı DEĞİLDİR:
    işletim sistemi düzeyinde kum havuzu YOKTUR ve kasıtlı düşmanca bir denetçi
    dosya sistemini gezip kardeş rolün dizinini okuyabilir. Bu turda kapatılan
    şey İZOLASYON değil, gözlenebilir SIZINTI KANALIDIR: denetçi-1'in raporu
    denetçi-2 koşarken diskte YOKTUR ve rol yolları takma ad kabul etmez.
    Tehdit modeli girdinin ÖZENSİZ olmasıdır, SALDIRGAN olması değil; gerçek
    izolasyon dağıtım katmanının işidir ve bu görevin kapsamı DIŞINDADIR.
    `test_cwd_is_not_a_security_boundary_and_the_declaration_is_measured` bu
    beyanı ölçer — izolasyon eklenirse test KIRMIZI olur ve beyan bayat kalamaz.
    Kiralama ve bütünlük kapısı bu sınırı DEĞİŞTİRMEZ: ikisi de dosya sistemi
    tabanlıdır, kum havuzu · konteyner · ayrı kullanıcı EKLEMEZ.

    **TOCTOU PENCERESİ — dürüst beyan.** Rol yolu artık HER `runner.run`'dan
    hemen önce yeniden doğrulanır, ama doğrulama ile kullanım arası ATOMİK
    DEĞİLDİR: kapı yolu ADIYLA çözer, alt süreç ise aynı adı bir sonraki anda
    KENDİ açar; ikisinin arasında ad başka bir düğüme bağlanabilir. Dosya
    TANIMLAYICI tabanlı işlemler (dizini bir kez açıp o fd'ye göre `openat` /
    `fchdir` ile koşmak) olmadan pencere TÜMÜYLE KAPANMAZ. Yapılan şey
    pencerenin DARALTILMASIDIR — bir turluk pencere rol başına indi —
    KAPATILMASI değildir. Tehdit modeli B3 ile aynıdır ve değişmez: girdi
    ÖZENSİZ olabilir, SALDIRGAN değildir; hat yerel ve tek kullanıcılıdır.
    `test_toctou_window_is_narrowed_not_closed_and_the_declaration_is_measured`
    bu beyanı ölçer — beyan gövdeden silinirse test KIRMIZI olur.
    """
    require_run_id(run_id)
    if not isinstance(packet, PacketRef):
        raise TypeError(
            f"run_audit_round PacketRef bekler: {type(packet).__name__}"
        )
    if run_id != packet.run_id:
        # FAIL-CLOSED ve HER ŞEYDEN ÖNCE: alt süreç de DB mutasyonu da yok.
        raise ValueError(
            f"koşu kimliği paketin kimliğiyle EŞİT DEĞİL (argüman {run_id!r}, "
            f"paket {packet.run_id!r}) — dosyalar paketin yollarından okunur, "
            "arıza ise argümanla adlandırılan satıra yazılırdı: bir koşunun "
            "denetimi başka bir koşuyu işaretleyemez"
        )

    async def _yarim(asama_sebebi: str) -> AuditRound:
        await runs.mark_incomplete(
            db, run_id=run_id, asama=DENETIM_ASAMASI, sebep=asama_sebebi
        )
        return AuditRound((), False, asama_sebebi)

    async def _en_iyi_cabayla_isaretle(sebep: str) -> None:
        """İstisna yolunda işaret — asıl istisnayı GÖLGELEMEZ."""
        try:
            await runs.mark_incomplete(
                db, run_id=run_id, asama=DENETIM_ASAMASI, sebep=sebep
            )
        except BaseException:  # noqa: BLE001 — asıl istisna korunur
            _LOG.warning(
                "denetim turu istisna yolunda işaretlenemedi: run_id=%s",
                run_id,
                exc_info=True,
            )

    ham: dict[str, str] = {}
    _yazim_sonucu: list[str | None] = []
    kiralama_alindi = False

    def _kaniti_kalicilastir(*, yut_hatalari: bool) -> str | None:
        """Tamamlanmış raporları EN ÇOK BİR KEZ diske indirir (TEK çıkış).

        Dört çıkış yolu da buradan geçer: normal dallar sebebi kullanmak için
        doğrudan çağırır, istisna yolları `finally`'den. Bellekleme sayesinde
        ikinci çağrı yeniden yazmaz ve `open(..., "x")` salt-eklemeliliği
        bozulmaz. `yut_hatalari` YALNIZ `finally` için doğrudur: orada bir
        `OSError` asıl istisnayı maskelerdi.
        """
        if _yazim_sonucu:
            return _yazim_sonucu[0]
        try:
            sebep = _kalicilastir(packet, ham)
        except OSError:
            if not yut_hatalari:
                raise  # normal yol: dış koruma tipli arızaya çevirir
            _LOG.warning(
                "denetim turu kısmi raporu istisna yolunda yazılamadı: "
                "run_id=%s",
                run_id,
                exc_info=True,
            )
            _yazim_sonucu.append(None)
            return None
        _yazim_sonucu.append(sebep)
        return sebep

    try:
        # ══ KABUL BÖLGESİ — ilk yan etkiden ÖNCE, TÜM giriş kapıları ══
        #
        # K-14 KARARI: ölçüm erişimi doğrulamıyorsa tur BAŞLAMAZ (plan 200-201).
        # Ön kontrol koruma bölgesinin İÇİNDEDİR: prob `BaseException`
        # fırlatırsa da koşu satırı işaretsiz kalmaz.
        on_kontroller = {
            rol: preflight(rol, prob=web_prob) for rol in DENETCI_ROLLERI
        }
        kapali = [
            sonuc
            for sonuc in on_kontroller.values()
            if not sonuc.tur_baslayabilir
        ]
        if kapali:
            return await _yarim(
                "denetim turu BAŞLAMADI — K-14 ön kontrolü erişimi "
                "DOĞRULAMADI: "
                + " · ".join(
                    f"{sonuc.arac} [{sonuc.durum.value}] {sonuc.sebep}"
                    for sonuc in kapali
                )
            )
        # Yol kapısı HER mutasyondan (kiralama `mkdir`'i dâhil) ÖNCE: yapımdan
        # sonra symlink'lenen bir kök ya da rol dizini parmak izi kapısını
        # bayt-özdeş bir ikizle geçebilir.
        yol_sebebi = _kosum_ani_yol_kapisi(packet)
        if yol_sebebi is not None:
            return await _yarim(yol_sebebi)
        # Kiralama ÇAKIŞMA KONTROLÜNDEN ÖNCE ve son kalıcılaştırmaya kadar
        # TUTULUR: çakışma kontrolü bir sıra kapısıdır, kilit değildir.
        kiralama_sebebi = _kiralamayi_al(packet)
        if kiralama_sebebi is not None:
            return await _yarim(kiralama_sebebi)
        kiralama_alindi = True
        # Hedef dosya çakışması İLK runner'dan ÖNCE: kalmış bir rapor,
        # denetçi-2 koşarken diskte durup sızıntı kanalını yeniden açardı.
        cakisma = _hedef_rapor_kapisi(packet)
        if cakisma is not None:
            return await _yarim(cakisma)
        # Bütünlük çakışmadan SONRA: turun kendi rapor dosyası artık provably
        # yoktur, dolayısıyla ağaçtan dışlanacak ad da yoktur.
        butunluk = _paket_butunluk_kapisi(packet)
        if butunluk is not None:
            return await _yarim(butunluk)

        # ══ KOŞUM BÖLGESİ — ilk yan etki buradan sonra ══
        for rol in DENETCI_ROLLERI:
            # Yol kapısı HER `runner.run`'dan hemen ÖNCE yeniden koşar. Kabul
            # bölgesindeki tek çağrı, denetçi-1 KOŞARKEN denetçi-2'nin rol
            # dizininin bayt-özdeş bir dış ikize symlink'lenmesini göremezdi.
            # Yeni kural YOKTUR: aynı yardımcı, aynı sözleşme.
            yol_sebebi = _kosum_ani_yol_kapisi(
                packet,
                onek=(
                    f"denetim turu {rol} rolünde DURDU, {rol} alt süreci "
                    "ÇAĞRILMADI"
                ),
            )
            if yol_sebebi is not None:
                return await _yarim(yol_sebebi)
            dizin = packet.kopyalar[rol]
            sonuc = runner.run(
                tool=rol, cwd=dizin, prompt_path=dizin / GOREV_DOSYA_ADI
            )
            if not isinstance(sonuc, RunnerOutcome):
                raise TypeError(
                    "Runner tipli sonuç döndürmek ZORUNDA: "
                    f"{type(sonuc).__name__} — ham metin kabul edilmez"
                )
            if sonuc.durum != "tamam":
                sebep = (
                    f"denetim turu {rol} aracında yarım kaldı "
                    f"(durum={sonuc.durum}, çıkış={sonuc.exit_code}): "
                    + runs.mask_secrets(sonuc.stderr.strip() or "<stderr boş>")
                )
                # Düşen rol koşmadı; ondan ÖNCEKİ rolün raporu kanıttır.
                yazma_sebebi = _kaniti_kalicilastir(yut_hatalari=False)
                if yazma_sebebi is not None:
                    sebep = f"{sebep} · {yazma_sebebi}"
                return await _yarim(sebep)
            ham[rol] = sonuc.stdout

        yazma_sebebi = _kaniti_kalicilastir(yut_hatalari=False)
        if yazma_sebebi is not None:
            return await _yarim(yazma_sebebi)

        dogrulanmis = tuple(
            validate_report(
                ham[rol], unit_snapshot=packet.unit_snapshot, denetci=rol
            )
            for rol in DENETCI_ROLLERI
        )
        anlasma = check_snapshot_agreement(
            dogrulanmis,
            expected_snapshot_sha=packet.unit_snapshot_sha,
            expected_kaynak_sha=packet.kaynak_seti_sha,
        )
        if anlasma.cift is None:
            return AuditRound((), False, " · ".join(anlasma.errors))

        tur_hatalari: list[str] = []
        for rol, rapor in zip(
            DENETCI_ROLLERI, (anlasma.cift.birinci, anlasma.cift.ikinci)
        ):
            tur_hatalari.extend(
                _tur_url_kapisi(
                    rapor,
                    yetkili_kaynak_sayisi=packet.yetkili_kaynak_sayisi,
                    on_kontrol=on_kontroller[rol],
                )
            )
            tur_hatalari.extend(
                _tur_sinif_kapisi(
                    rapor, yetkili_kaynak_sayisi=packet.yetkili_kaynak_sayisi
                )
            )
        if tur_hatalari:
            return AuditRound((), False, " · ".join(tur_hatalari))
        return AuditRound((anlasma.cift.birinci, anlasma.cift.ikinci), True, None)
    except OSError as exc:
        # Beklenen alt süreç/dosya sistemi arızası: eksik CLI · izin · disk.
        sebep = (
            f"denetim turu alt süreç arızasıyla düştü ({type(exc).__name__}): "
            + runs.mask_secrets(str(exc) or "<sebep boş>")
        )
        return await _yarim(sebep)
    except asyncio.CancelledError:
        await _en_iyi_cabayla_isaretle(
            "denetim turu İPTAL edildi (CancelledError) — koşu yarım kaldı"
        )
        raise
    except BaseException as exc:
        await _en_iyi_cabayla_isaretle(
            f"denetim turu beklenmeyen istisnayla düştü ({type(exc).__name__}): "
            + runs.mask_secrets(str(exc) or "<sebep boş>")
        )
        raise
    finally:
        # TEK ÇIKIŞ: dört yolun dördünde de tamamlanmış kanıt en iyi çabayla
        # yazılır. Normal dallar zaten çağırdıysa bellekleme bunu no-op yapar.
        _kaniti_kalicilastir(yut_hatalari=True)
        # Kiralama SON kalıcılaştırmadan sonra bırakılır. Sahiplenmeyen tur
        # ASLA silmez: bayrak yalnız `mkdir`'i KAZANAN turda doğrudur.
        if kiralama_alindi:
            _kiralamayi_birak(packet)
