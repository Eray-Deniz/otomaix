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
* `preflight` — K-14. Ölçülmemiş erişim "var" sayılmaz: probu olmayan ya da
  patlayan ön kontrol turu BAŞLATMAZ.

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

import hashlib
import json
import logging
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Mapping, Protocol, Sequence
from uuid import UUID

from app.services.sector_pipeline import contracts, identity, runs
from app.services.sector_pipeline.brief_doctor import DoctorReport
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

_ORTAM_KISITI = "URL doğrulaması yapılamadı (ortam kısıtı)"
"""Sözleşmenin web-erişimsiz kaçış cümlesi — satır beklentisini KALDIRIR."""

_URL_SONUCLARI: tuple[str, ...] = ("DOĞRULANDI", "KAYNAKTA YOK", "URL AÇILMADI")

KAYNAK_TABANI = 2
"""Sözleşmenin asgari kaynak tabanı: altına düşen koşuda örneklem hiç doldurulmaz."""

_BOLUM_BASLIGI_RE = re.compile(
    r"^(\d)\)[ \t]+([A-ZÇĞİÖŞÜ][A-ZÇĞİÖŞÜ ]*?)[ \t]*(?:—.*)?$", re.M
)
_KAYNAK_SAYISI_RE = re.compile(r"[Kk]aynak sayısı[ \t]*:[ \t]*(\d+)")
_BEKLENEN_SATIR_RE = re.compile(r"[Bb]eklenen satır(?:[ \t]*sayısı)?[ \t]*:[ \t]*(\d+)")
_AYIRAC_HUCRESI_RE = re.compile(r"^:?-{2,}:?$")

_ENVANTER_BASLIK_HUCRELERI = ("unit_id", "statu", "kanit", "gerekce")
_URL_BASLIK_HUCRELERI = ("iddia", "kaynak", "sonuç", "not")


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

    **Ad ile sütun arasındaki fark BEYAN EDİLİR:** sözleşmenin çıktı bölümü ilk
    sütuna `iddia` der ve o hücre iddianın URL referansını taşır; alan adı
    arayüz eki R5'te `url` olarak BAĞLIDIR ve hücre AYNEN taşınır. `erisildi` ve
    `icerik_uyumlu` sözleşmenin üç sonucundan TÜRETİLİR, ayrıca yazılmaz.
    """

    url: str
    kaynak: str
    erisildi: bool
    icerik_uyumlu: bool
    not_metni: str


@dataclass(frozen=True)
class AuditReport:
    """Doğrulanmış tek denetçi raporu."""

    denetci: str
    ham_metin: str
    bolumler: Mapping[str, str]
    yeniden_dogrulama: tuple[InventoryRow, ...]
    url_orneklem: tuple[UrlCheck, ...]
    unit_snapshot_sha: str

    def __post_init__(self) -> None:
        # `bolumler` `identity.donmus`'tan geçer: beş anahtarlı kapalı küme
        # `validate_report`'un KAPISIDIR; yapımdan sonra anahtar eklemek/silmek
        # o kapıyı geçmiş bir raporu kapıdan geçmemiş hâle çevirirdi.
        object.__setattr__(self, "bolumler", identity.donmus(self.bolumler))
        # İki dizi alanı DA kopyalanır ve ÖĞE TİPLERİ sınanır. Anotasyon çalışma
        # zamanında hiçbir şey yapmaz; çağıran liste verirse takma ad paylaşılır
        # ve kapıdan geçmiş envanter yapımdan SONRA değiştirilebilirdi.
        # `identity.donmus` burada KULLANILAMAZ: `InventoryRow`/`UrlCheck`
        # donmuş dataclass'tır ve `donmus`'un KAPALI kümesinin dışındadır
        # (kural 5 -> TypeError).
        for _alan, _tip in (
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


@dataclass(frozen=True)
class PacketRef:
    """Kurulmuş denetçi paketinin kaydı (K-79)."""

    run_id: str
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


@dataclass(frozen=True)
class PreflightResult:
    """K-14 ön kontrolünün sonucu.

    `web_erisimi` ÖLÇÜLEN olgudur; `tur_baslayabilir` ondan TÜRER. Erişimsiz bir
    sonuç sebepsiz kurulamaz — "neden başlamadı" sorusunun cevabı kayıtta olmak
    zorundadır.
    """

    arac: str
    web_erisimi: bool
    sebep: str

    def __post_init__(self) -> None:
        if not isinstance(self.arac, str) or not self.arac.strip():
            raise ValueError(
                f"PreflightResult.arac kimlik taşımak ZORUNDA: {self.arac!r}"
            )
        if not self.web_erisimi and not self.sebep.strip():
            raise ValueError(
                "PreflightResult sebepsiz başarısızlık taşıyamaz — turu "
                "durduran ölçüm kayda geçmek zorundadır"
            )

    @property
    def tur_baslayabilir(self) -> bool:
        return self.web_erisimi


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
        "00-GOREV.md": gorev_metni,
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

    kok = Path(dest) / run_id
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
        if all(_AYIRAC_HUCRESI_RE.match(h) for h in hucreler if h):
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

    **ÖLÇÜLMEYEN (dürüst etiket, çözülmedi + evi var).** Beyan edilen kaynak
    sayısının YETKİLİ kaynak sayısıyla eşit olduğu BURADA KARŞILAŞTIRILMAZ:
    üç kaynakla koşan bir rapor "Kaynak sayısı: 2" yazıp altı satırla bu
    kapıdan geçer. Aynı şekilde `_ORTAM_KISITI` cümlesinin gerçekten ölçülmüş
    bir erişimsizliğe karşılık geldiği de ölçülmez — cümle satır beklentisini
    KALDIRIR ve doğruluğu bu kapının görüş alanı dışındadır. İki karşılaştırma
    da tek rapor gören bir kapıya sığmaz (yetkili sayı ile ölçülmüş erişim
    durumu bu imzada YOKTUR); evleri **Task 10 tur seviyesidir** — orada koşu
    kaydı yetkili kaynak sayısını ve `preflight` sonucunu taşır.
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
    kural = kaynak_sayisi * 3 if kaynak_sayisi >= KAYNAK_TABANI else 0
    if beyan != kural:
        errors.append(
            f"URL örneklem beyanı kuralla çelişiyor: {kaynak_sayisi} kaynak "
            f"için beklenen satır {kural}, beyan {beyan} — tek kaynak kalırsa "
            "bölüm hiç doldurulmaz"
        )

    ham_satirlar = _tablo_satirlari(govde, _URL_BASLIK_HUCRELERI)
    kontroller: list[UrlCheck] = []
    for sira, hucreler in enumerate(ham_satirlar, start=1):
        if len(hucreler) != 4:
            errors.append(
                f"URL örneklem satırı {sira} dört sütunlu değil "
                f"(iddia | kaynak | sonuç | not): {hucreler}"
            )
            continue
        url, kaynak, sonuc, not_metni = hucreler
        if sonuc not in _URL_SONUCLARI:
            errors.append(
                f"URL örneklem satırı {sira} kapalı sonuç kümesinin dışında: "
                f"{sonuc!r} — {list(_URL_SONUCLARI)}"
            )
            continue
        kontroller.append(
            UrlCheck(
                url=url,
                kaynak=kaynak,
                erisildi=sonuc != "URL AÇILMADI",
                icerik_uyumlu=sonuc == "DOĞRULANDI",
                not_metni=not_metni,
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
    return tuple(kontroller), errors


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
    beyanıyla bu kapıyı geçemez. URL örneklemi ise BÖYLE DEĞİLDİR — orada
    yalnız raporun **kendi beyanının iç tutarlılığı** ölçülür; beyan edilen
    kaynak sayısı yetkili kaynak sayısıyla KARŞILAŞTIRILMAZ, çünkü bu imza ne
    yetkili sayıyı ne de ölçülmüş erişim durumunu görür. O karşılaştırmanın evi
    **Task 10 tur seviyesidir** (çözülmedi + evi var). İmza arayüz eki R6(a)
    ile bağlıdır ve bu turda DEĞİŞTİRİLMEZ.
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

    kontroller, url_hatalari = _url_orneklemi(bolumler[BOLUM_ANAHTARLARI[1]])
    errors.extend(url_hatalari)
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

    `prob` çağıranın sağladığı ölçüm yoludur (CLI katmanı, Task 11). **Prob
    YOKSA sonuç başarısızdır:** ölçülmemiş erişim "var" sayılmaz. Prob patlarsa
    istisna da erişim kanıtı DEĞİLDİR; sebep olduğu gibi taşınır.
    """
    if not isinstance(tool, str) or not tool.strip():
        raise ValueError(f"preflight araç kimliği bekler: {tool!r}")
    if prob is None:
        return PreflightResult(
            arac=tool,
            web_erisimi=False,
            sebep="web erişimi probu tanımlı DEĞİL — erişim ölçülmedi, tur "
            "başlamaz (ölçülmemiş erişim 'var' sayılmaz)",
        )
    try:
        erisim = bool(prob(tool))
    except Exception as exc:  # noqa: BLE001 — her arıza turu DURDURUR
        return PreflightResult(
            arac=tool,
            web_erisimi=False,
            sebep=f"web erişimi probu hata verdi: {type(exc).__name__}: {exc}",
        )
    return PreflightResult(
        arac=tool,
        web_erisimi=erisim,
        sebep="" if erisim else "web erişimi probu olumsuz döndü — tur başlamaz",
    )


# ═══ Task 10 — iki kör denetçi orkestrasyonu (K-76 · K-78 · K-79 · K-82 · K-150) ═══

GOREV_DOSYA_ADI = "00-GOREV.md"
RAPOR_DOSYA_KALIBI = "RAPOR-{}.md"
DENETIM_ASAMASI = "denetim"
SENTEZ_ARACI = "sentez"
ARAC_ADLARI: tuple[str, ...] = DENETCI_ROLLERI + (SENTEZ_ARACI,)
RUNNER_DURUMLARI: tuple[str, ...] = ("tamam", "zaman-asimi", "hata")

_LOG = logging.getLogger(__name__)


@dataclass(frozen=True)
class ToolSpec:
    argv: tuple[str, ...]

    def __post_init__(self) -> None:
        raise NotImplementedError


ARAC_KOMUTLARI: Mapping[str, ToolSpec] = MappingProxyType({})


@dataclass(frozen=True)
class RunnerOutcome:
    durum: str
    stdout: str
    stderr: str
    exit_code: int | None

    def __post_init__(self) -> None:
        raise NotImplementedError


class Runner(Protocol):
    def run(self, tool: str, cwd: Path, prompt_path: Path) -> RunnerOutcome: ...


class SubprocessRunner:
    def __init__(self, *, zaman_asimi_sn: float) -> None:
        raise NotImplementedError

    def run(self, tool: str, cwd: Path, prompt_path: Path) -> RunnerOutcome:
        raise NotImplementedError


@dataclass(frozen=True)
class ValidatedAuditPair:
    birinci: AuditReport
    ikinci: AuditReport
    unit_snapshot_sha: str

    def __post_init__(self) -> None:
        raise NotImplementedError


@dataclass(frozen=True)
class SnapshotAgreement:
    cift: ValidatedAuditPair | None
    errors: tuple[str, ...]

    def __post_init__(self) -> None:
        raise NotImplementedError

    @property
    def gecerli(self) -> bool:
        raise NotImplementedError


@dataclass(frozen=True)
class AuditRound:
    reports: tuple[AuditReport, ...]
    gecerli: bool
    sebep: str | None

    def __post_init__(self) -> None:
        raise NotImplementedError


def check_snapshot_agreement(
    validated: tuple[ValidatedReport, ValidatedReport],
    *,
    expected_snapshot_sha: str,
) -> SnapshotAgreement:
    raise NotImplementedError


async def run_audit_round(
    db,
    packet: PacketRef,
    *,
    runner: Runner,
    run_id: str,
) -> AuditRound:
    raise NotImplementedError
