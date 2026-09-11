"""Sentez koşumu + çıktı doğrulayıcı (Plan 2 Task 11).

Sentez, iki kör denetçinin doğrulanmış turundan **aday değişiklik seti**
üretir. Karar mercii DEĞİLDİR: ürettiği aday motora girer, motor kendi
kontrolleriyle sınar, `draft` yazımı ondan SONRA ayrı bir adımda olur.

**PAKET TABLOSUNA YAZMAZ.** Kesin sınır: bu modül yalnız koşu DURUMUNU
(`runs.mark_incomplete`) ve ham artefaktı yazabilir; `social.sector_packages`
tablosuna hiçbir şey yazamaz ve yaşam döngüsü modülünü içe AKTARMAZ. Kanonik
sıra `sentez → motor → draft` böylece kod düzeyinde zorlanır
(`test_synthesis_module_does_not_import_insert_draft`).

**Kimlik sentezin malı değildir.** Modelin yazdığı `oge_yolu`/`oge_sha`
değerleri KABUL EDİLMEZ: yol üretilen içerikten
`identity.enumerate_content_units` ile, hash `identity.canonical_sha` ile
yeniden üretilir. `guncelle` aktif paketin kimliğini korur, `ekle` YENİ kimlik
alır ve `yerine_gecer` ile çıkarılana bağlanır (K-86/K-154). Kimlik yola değil,
yol kimliğe göre çözülür — yol sıra numaraları KONUMSALDIR.

**Çıkarma eşiği (K-122 + K-124).** Bir birimin çıkarılması POZİTİF kanıt ister
ve reddedilen çıkarma SESSİZCE DÜŞMEZ: birim içeriğe geri konur, onu
sahiplenen `koru` satırı yazılır ve madde AÇIK SORUYA düşer. Üç ret sebebi
ayrıdır ve hata metninde adlandırılır:

  1. **K-122** — denetçilerden biri `supported` diyorsa kalıp DOĞRULANMIŞTIR;
     yeni bir adayın salt varlığı onu çıkaramaz. Karşı taraftaki `contradicted`
     satırı tek başına yetmez: iki denetçinin ayrıştığı yer çıkarma değil açık
     soru yeridir.
  2. **K-124 mevzuat kolu** — `MEVZUAT_ALANLARI` içindeki bir birim için İKİ
     denetçinin de `contradicted` satırı gerekir.
  3. **K-124 normal kol** — en az BİR `contradicted` satırı gerekir.

`not_observed` bu kapıların hiçbirini açmaz. Sebep ölçüldü, uydurulmadı:
pinlenmiş denetçi sözleşmesi (satır 179-182) *"`not_observed` GEÇERSİZLİK
KANITI DEĞİLDİR"* der ve onu `contradicted`'ın yumuşak hâli gibi kullanmayı
açıkça yasaklar. **KAPSAM SINIRI, dürüst etiket:** `risk_unverified` de
çıkarma açmaz. Bu muhafazakâr okuma bilinçlidir (spec §3.5 "çıkarma yalnız
pozitif kanıtla") ve sonucu kayıp değil AÇIK SORUDUR — doğrulanamayan bir
mevzuat birimi insana gider, sessizce silinmez.

**Taşma KESMEZ (K-74/K-75).** İki tavan İKİ AYRI sözleşmeden gelir ve tek
karara bağlanmaz: sentezin açık soru tavanı (10) `hakem-sentez-gorevi.md`
satır 395'ten, denetçinin öneri tavanı (5) `hakem-denetci-gorevi.md` satır
217'den ÖLÇÜLDÜ. Aşan madde DÜŞÜRÜLMEZ, kesilmez; yalnız `tasma`
işaretlenir — sayı bir kapı DEĞİLDİR (İlke 9).

**Durum sahipliği (K-82).** `Runner`'ın veritabanı yoktur; terminal arızada
`runs.mark_incomplete` BURADAN çağrılır. Tur geçerli değilse (K-150) sentez
hiç başlamaz ve koşu satırına DOKUNULMAZ: o satırı denetim turu zaten
işaretlemiştir, ikinci bir işaret sebebi EZERDİ.

**Plan imzasından SAPMA — beyan edilir.** Plan `synthesis.run`'ı `dest`
argümanı olmadan yazar. `Runner` protokolü bir çalışma dizini ve bir istem
DOSYASI ister (`run(tool, cwd, prompt_path)`), yani sentezin de bir kökü
olmak zorundadır. Kök gizli bir sabitten türetilseydi testler gerçek
araştırma deposuna yazardı; bu yüzden `dest` AÇIK bir parametredir ve
`build_packet`'in `dest` deseniyle simetriktir. Kök kapısı da aynı kuralı
kullanır — ikinci bir yol kuralı YAZILMAZ.
"""

from __future__ import annotations

import copy
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence

from app.services.sector_content_schema import (
    LIST_FIELDS,
    VIDEO_POOL_KEYS,
    structural_errors,
)
from app.services.sector_packages import validate_package_content
from app.services.sector_pipeline import contracts, identity, runs
from app.services.sector_pipeline.runs import _require_run_id as require_run_id
from app.services.sector_pipeline.auditors import (
    ARASTIRMA_DEPOSU_KOKU,
    BOLUM_ANAHTARLARI,
    DENETCI_ROLLERI,
    PIN_PATH,
    SENTEZ_ARACI,
    AuditRound,
    Runner,
    anonymize,
    kok_yolunu_kapila,
)

SENTEZ_ASAMASI = "sentez"
"""`runs.ASAMALAR` içindeki aşama adı — bildirim anahtarı koşu + aşamadır."""

GOREV_DOSYASI = "hakem-sentez-gorevi.md"
"""Pinlenmiş sentez sözleşmesinin dış depodaki adı."""

GOREV_DOSYA_ADI = "00-SENTEZ-GOREVI.md"
CIKTI_DOSYA_ADI = "01-SENTEZ-CIKTISI.md"

SENTEZ_BOLUM_ANAHTARLARI: tuple[str, ...] = (
    "ADAY PAKET",
    "DECISION_LOG",
    "AÇIK SORULAR",
    "ÖZET",
)
"""Sentez çıktısının DÖRT bölümü — SIRA sözleşmenin sırasıdır.

**Değerler ÖLÇÜLDÜ, uydurulmadı (İlke 9).** Pinlenmiş `hakem-sentez-gorevi.md`
ADIM 4'ün numaralı başlıklarından (satır 348 · 378 · 394 · 397) çıkarıldı.
`test_section_keys_match_pinned_contract` bunu her koşumda YENİDEN ölçer —
sözleşme değişip bu demet güncellenmezse test DÜŞER.
"""

ONERI_BOLUMU = BOLUM_ANAHTARLARI[3]
"""Denetçi raporunun açık soru öneri bölümü — Task 9'un ölçülmüş demetinden.

Adı burada ikinci kez YAZILMAZ (R14): demet zaten pinlenmiş denetçi
sözleşmesine karşı ölçülüyor, ikinci bir dizge iki doğruluk kaynağı üretirdi.
"""

K74_ACIK_SORU_TAVANI = 10
"""Sentezin açık soru tavanı — `hakem-sentez-gorevi.md` satır 395."""

K75_DENETCI_ONERI_TAVANI = 5
"""Denetçinin öneri tavanı — `hakem-denetci-gorevi.md` satır 217. AYRI karar."""

CIKARMAYI_DESTEKLEYEN_STATU = "contradicted"
"""TEK pozitif-kanıt statüsü (denetçi sözleşmesi satır 185-186)."""

CIKARMAYI_ENGELLEYEN_STATU = "supported"
"""Doğrulanmış kalıbın statüsü — K-122'nin dayanağı."""

MEVZUAT_ALANLARI: tuple[str, ...] = ("yasaklar_ve_hassasiyetler",)
"""Mevzuat/güvenlik bilgisini taşıyan alan(lar) — K-124'ün iki-denetçi kolu."""

_BOLUM_BASLIGI_RE = re.compile(
    r"^(\d)\)[ \t]+([A-ZÇĞİÖŞÜ_][A-ZÇĞİÖŞÜ_ ]*?)[ \t]*(?:—.*)?$", re.M
)
_JSON_FENCE_RE = re.compile(r"```(?:json)?[ \t]*\n(.*?)\n[ \t]*```", re.S)
_LISTE_OGESI_RE = re.compile(r"^[ \t]*(?:[-*•]|\d+[.)])[ \t]+(\S.*?)[ \t]*$", re.M)

_LISTE_YOLU_RE = re.compile(r"^(?P<alan>[a-z_]+)\[(?P<sira>\d+)\]$")
_VIDEO_YOLU_RE = re.compile(r"^video_kodlar/(?P<havuz>[a-z]+)\[(?P<sira>\d+)\]$")


class SynthesisFailed(RuntimeError):
    """Sentez terminal arızası — yarım sonuç motora ULAŞMAZ."""


@dataclass(frozen=True)
class SynthesisResult:
    """Sentezin dört çıktısı + taşma işareti.

    **Üç koleksiyon da R6(e) kuralıyla DERİNLEMESİNE donar.** İlk yazım
    `aday_json`'u yalnız üst düzeyde salt-okunur yapıyor ve gerekçe olarak
    *"şema `list` ister"* diyordu; bu gerekçe ÇÜRÜTÜLDÜ (checkpoint 8, yüksek):
    çalışma zamanı şeklinin `list` olması, KALICI temsilin de değiştirilebilir
    olmasını gerektirmez — çözme, şema sınırında yapılır. Doğrulanmış bir
    sonucun iç içe listesine sonradan öğe eklemek, içerik/günlük çiftini
    doğrulamadan SONRA tutarsız hâle getirirdi.

    Şemaya ya da JSON'a verilecekken `identity.cozulmus` ile çözülür; `donmus`
    ile birlikte TEK bir çifttir ve ikinci bir kopyası yoktur.
    """

    aday_json: Mapping
    karar_gunlugu: tuple[Mapping, ...]
    acik_sorular: tuple[str, ...]
    onay_ozeti: str
    tasma: bool

    def __post_init__(self) -> None:
        if not isinstance(self.aday_json, Mapping):
            raise TypeError(
                f"SynthesisResult.aday_json eşleme olmak ZORUNDA: "
                f"{type(self.aday_json).__name__}"
            )
        object.__setattr__(self, "aday_json", identity.donmus(dict(self.aday_json)))
        satirlar = tuple(self.karar_gunlugu)
        for satir in satirlar:
            if not isinstance(satir, Mapping):
                raise TypeError(
                    f"SynthesisResult.karar_gunlugu yalnız eşleme taşır: "
                    f"{type(satir).__name__}"
                )
        object.__setattr__(self, "karar_gunlugu", identity.donmus(satirlar))
        sorular = tuple(self.acik_sorular)
        for soru in sorular:
            if not isinstance(soru, str):
                raise TypeError(
                    f"SynthesisResult.acik_sorular yalnız dize taşır: "
                    f"{type(soru).__name__}"
                )
        object.__setattr__(self, "acik_sorular", sorular)
        if not isinstance(self.onay_ozeti, str):
            raise TypeError(
                f"SynthesisResult.onay_ozeti dize olmak ZORUNDA: "
                f"{type(self.onay_ozeti).__name__}"
            )
        if not isinstance(self.tasma, bool):
            raise TypeError(
                f"SynthesisResult.tasma bool olmak ZORUNDA: "
                f"{type(self.tasma).__name__}"
            )


# ─── 1. Çıktı doğrulayıcı (seam) ────────────────────────────────────────────


def validate(result: SynthesisResult) -> list[str]:
    """Sentez çıktısının BAĞLAMSIZ değişmezleri — hata listesi (boş = geçti).

    Bağlam gerektiren kapılar (K-122 · K-124 · geri-ekleme) burada DEĞİLDİR:
    onlar aktif paketi ve denetçi turunu ister, `SynthesisResult` ise onları
    taşımaz. Bu ayrım bilinçlidir — burada sorulan tek soru *"bu sonuç kendi
    içinde tutarlı mı"*dır.

    Plan 1 doğrulayıcıları YENİDEN KULLANILIR, kopyalanmaz: `structural_errors`
    (K-02/K-113 dâhil içerik şekli), `identity.validate_decision_log` (satır
    şeması) ve `identity.check_unit_integrity` (iki yönlü örtüşme). Buraya
    kural kopyalansaydı yazım kapısıyla sentez kapısı sürüm sürüm ayrışırdı.
    """
    icerik = identity.cozulmus(result.aday_json)
    hatalar = list(structural_errors(icerik))
    gunluk = [dict(satir) for satir in result.karar_gunlugu]
    hatalar.extend(identity.validate_decision_log(gunluk))
    if not hatalar:
        # Bütünlük ancak iki kapı da geçilmişse ÖLÇÜLEBİLİR; `check_unit_integrity`
        # kendi içinde de bunu sorar, ama hatayı iki kez raporlamayalım.
        hatalar.extend(identity.check_unit_integrity(icerik, gunluk))
    for sira, satir in enumerate(gunluk):
        if satir.get("tur") != "karar":
            continue
        if satir.get("aktor") != "sentez":
            hatalar.append(
                f"karar_gunlugu[{sira}] aktor {satir.get('aktor')!r} — sentezin "
                "günlüğündeki her karar satırı 'sentez' aktörünü taşır"
            )
    return hatalar


# ─── 2. Çıktı ayrıştırma ────────────────────────────────────────────────────


def _bolumlere_ayir(text: str) -> tuple[dict[str, str], list[str]]:
    """Çıktıyı dört bölüme ayırır; küme ya da SIRA sapmışsa hata döner."""
    eslesmeler = list(_BOLUM_BASLIGI_RE.finditer(text))
    bulunan = [(int(m.group(1)), m.group(2)) for m in eslesmeler]
    beklenen = list(enumerate(SENTEZ_BOLUM_ANAHTARLARI, start=1))
    if bulunan != beklenen:
        return {}, [
            "sentez biçim kapısı: dört bölüm eksiksiz ve SIRAYLA olmak ZORUNDA "
            f"— bulunan {bulunan}, beklenen {beklenen}"
        ]

    bolumler: dict[str, str] = {}
    for sira, eslesme in enumerate(eslesmeler):
        bas = eslesme.end()
        son = (
            eslesmeler[sira + 1].start()
            if sira + 1 < len(eslesmeler)
            else len(text)
        )
        bolumler[eslesme.group(2)] = text[bas:son].strip("\n")
    return bolumler, []


def _json_govdesi(govde: str, etiket: str) -> Any:
    """Bölümün JSON gövdesi — çitli blok varsa O, yoksa bölümün kendisi.

    İki okuma yolu YOKTUR: çit varsa gövde çitin içidir; model çiti unutursa
    bölümün tamamı denenir. Ayrıştırılamayan gövde SESSİZ boş sonuç üretmez.
    """
    eslesme = _JSON_FENCE_RE.search(govde)
    ham = eslesme.group(1) if eslesme else govde
    try:
        return json.loads(ham)
    except (json.JSONDecodeError, ValueError) as hata:
        raise SynthesisFailed(
            f"{etiket} bölümü JSON olarak okunamadı: {hata}"
        ) from hata


def _liste_ogeleri(govde: str) -> list[str]:
    """Madde imli satırları öğe olarak okur.

    **KAPSAM SINIRI, sessizce atlanmaz.** Kural YAPISALDIR: madde imi (`-`,
    `*`, `•`, `1.`, `1)`) taşıyan satırlar sayılır. İmsiz serbest düz yazı SIFIR
    öğe verir. Bu, serbest metinden madde SAYISI çıkarmaya çalışan bir yaklaşımın
    (semantik olumsuzlama) bilinçle terk edilmiş hâlidir; buradaki sayı bir KAPI
    değil, yalnız `tasma` işaretinin girdisidir — yanlış saymak hiçbir koşuyu
    durdurmaz, yalnız işareti eksik/fazla koyar.
    """
    return [m.group(1) for m in _LISTE_OGESI_RE.finditer(govde)]


# ─── 3. İstem kurulumu ──────────────────────────────────────────────────────


def _istem_metni(
    gorev_metni: str,
    tur: AuditRound,
    active_package: Mapping | None,
    removed_history: Sequence[Mapping],
    holiday_keys: set[str],
) -> str:
    """Sentez aracına verilen tek istem dosyası.

    İstemin TAMAMI `anonymize`'dan GEÇER — `_paket_dosyalari` ile aynı desen. K-137 bugüne dek yalnız pakete
    GİDEN baytı kapsıyordu; rapor gövdesindeki araç kimliği geri dönüş yolunda
    maskesizdi ve sentez istemine olduğu gibi akıyordu. Aynı kural burada da
    uygulanır — ikinci bir maskeleme kuralı yazılmaz. **Vaat kümenin kendisi
    kadardır:** `ARAC_KIMLIKLERI` kapalıdır, dışındaki bir satıcı adı
    maskelenmez; bu kapsama, yapısal bir garanti değildir.
    """
    parcalar = [
        gorev_metni,
        "",
        f"KOŞU TARİHİ: {date.today().isoformat()}",
        "",
        "## EK-H — AKTİF PAKET",
        json.dumps(active_package, ensure_ascii=False, indent=2, default=str)
        if active_package is not None
        else "İLK KOŞU — aktif paket YOK.",
        "",
        "## EK-I — SON TURLARIN ÇIKARILANLARI",
        json.dumps(list(removed_history), ensure_ascii=False, indent=2, default=str),
        "",
        "## EK-J — SİSTEM ÖZEL GÜN ANAHTARLARI",
        json.dumps(sorted(holiday_keys), ensure_ascii=False, indent=2),
    ]
    for rapor in tur.reports:
        parcalar.extend(
            ["", f"## DENETÇİ RAPORU — {rapor.denetci}", anonymize(rapor.ham_metin)]
        )
    return anonymize("\n".join(parcalar) + "\n")


# ─── 4. Kimlik bağlama ve çıkarma eşiği ─────────────────────────────────────


def _aktif_birimler(active_package: Mapping | None) -> dict[str, dict]:
    """Aktif paketin `unit_id` → birim eşlemesi. İlk koşuda BOŞ.

    Üretici `identity.decision_units`'tir ve ikinci bir üretici YOKTUR: aktif
    paketin içerik/günlük çifti onun kapılarından geçmeden sentezin girdisi
    olamaz.
    """
    if active_package is None:
        return {}
    try:
        icerik = active_package["content"]
        gunluk = active_package["decision_log"]
    except (KeyError, TypeError) as hata:
        raise SynthesisFailed(
            "aktif paket `content` + `decision_log` taşımak ZORUNDA — kimlik "
            f"taşıması bu çiftten türer: {hata}"
        ) from hata
    try:
        return identity.decision_units(dict(icerik), list(gunluk))
    except (ValueError, TypeError) as hata:
        raise SynthesisFailed(f"aktif paket kimlik kapısını geçmedi: {hata}") from hata


def dogrulanmis_referanslar(rapor) -> set[str]:
    """Raporun DOĞRULANMIŞ kaynak referansları — TAM EŞLEŞME kümesi.

    **PUBLIC (Plan 2 Task 12).** Motorun kanıt kontrolü AYNI kuralı sorar;
    alt çizgili ad "modül içi" diye yalan söylüyordu. İkinci bir kopya yazmak
    iki sürümlü bir kanıt ölçütü üretirdi — `auditors.kok_yolunu_kapila`
    emsali: kural TEK yerde yaşar, iki tüketici onu ÇAĞIRIR.

    Doğrulanmış = ADIM 1 örnekleminde hem erişilmiş hem içerikçe uyumlu
    (sözleşmenin `DOĞRULANDI` sonucu). Küme, o satırın hem URL'sini hem kör
    kaynak etiketini taşır; `kanit` alanı ikisinden birine TAM eşit olmalıdır.

    **Neden alt dizge değil tam eşleşme.** Serbest metinden *"bu referans
    doğrulanmıştır"* çıkarmaya çalışmak bypass ile yanlış-pozitif arasında
    salınan bir sınıftır. Burada pozitif ve KAPALI bir kontrat kullanılır:
    referans ya kümededir ya değildir.
    """
    referanslar: set[str] = set()
    for kontrol in rapor.url_orneklem:
        if not (kontrol.erisildi and kontrol.icerik_uyumlu):
            continue
        for deger in (kontrol.url, kontrol.kaynak):
            if isinstance(deger, str) and deger.strip():
                referanslar.add(deger.strip())
    return referanslar


def _cikarma_kapisi(
    unit_id: str, alan: str, tur: AuditRound, *, karar: str
) -> str | None:
    """Birimin içerikten DÜŞMESİ admissible mı — değilse RET SEBEBİ döner.

    Kapı `cikar` ve `kirp`'in İKİSİNE de uygulanır. Sözleşme churn korumasını
    *"kırpmanın ve `cikar` kararının SONUCUNA konan bir kısıt"* diye yazar
    (satır 202-203): karar etiketi değil, aktif bir birimin adaydan DÜŞMESİ
    tetikler. Etikete bağlansaydı `supported` bir birim `kirp` yazılarak
    kapıdan geçerdi — ölü kararlar bütünlük kapısına da görünmez.

    İki kol AYRIDIR ve bu bilinçlidir:

      * **K-122 (her iki karar için)** — bir denetçi `supported` diyorsa kalıp
        doğrulanmıştır ve düşmez.
      * **K-124 (yalnız `cikar`)** — çıkarma POZİTİF kanıt ister. `kirp` bir
        BOYUT kararıdır (spec §8.6 kırpma sırası), kanıt kararı değil; ona
        kanıt eşiği koymak sözleşmede olmayan bir kural olurdu.

    Üç ret sebebi ayrı adlandırılır: hangi kapının düştüğü açık sorunun
    metninden okunabilmelidir.
    """
    dogrulayan: list[str] = []
    destekleyen: list[str] = []
    kanitsiz: list[str] = []
    for rapor in tur.reports:
        satirlar = [
            satir for satir in rapor.yeniden_dogrulama if satir.unit_id == unit_id
        ]
        if any(satir.statu == CIKARMAYI_ENGELLEYEN_STATU for satir in satirlar):
            dogrulayan.append(rapor.denetci)
        celiskiler = [
            satir for satir in satirlar if satir.statu == CIKARMAYI_DESTEKLEYEN_STATU
        ]
        if not celiskiler:
            continue
        referanslar = dogrulanmis_referanslar(rapor)
        if any(str(satir.kanit).strip() in referanslar for satir in celiskiler):
            destekleyen.append(rapor.denetci)
        else:
            kanitsiz.append(rapor.denetci)

    if dogrulayan:
        return (
            f"K-122 churn koruması: {sorted(dogrulayan)} birimi "
            f"{CIKARMAYI_ENGELLEYEN_STATU!r} raporladı; doğrulanmış kalıp yeni bir "
            "adayın varlığıyla düşürülemez"
        )
    if karar != "cikar":
        return None
    if alan in MEVZUAT_ALANLARI:
        if len(destekleyen) < len(DENETCI_ROLLERI):
            return (
                "K-124 mevzuat kolu: mevzuat/güvenlik birimi için İKİ denetçinin de "
                f"doğrulanmış referanslı {CIKARMAYI_DESTEKLEYEN_STATU!r} satırı "
                f"gerekir; çözülen {sorted(destekleyen)}, çözülemeyen "
                f"{sorted(kanitsiz)}"
            )
        return None
    if not destekleyen:
        if kanitsiz:
            return (
                f"K-124: {sorted(kanitsiz)} {CIKARMAYI_DESTEKLEYEN_STATU!r} dedi ama "
                "`kanit` doğrulanmış bir referansa ÇÖZÜLMEDİ — sözleşme bu statüde "
                "doğrulanmış referans ZORUNLU kılar (denetçi sözleşmesi satır 185-186)"
            )
        return (
            f"K-124: çıkarma en az bir doğrulanmış referanslı "
            f"{CIKARMAYI_DESTEKLEYEN_STATU!r} satırı ister; hiçbir denetçi pozitif "
            "çelişki kanıtı raporlamadı"
        )
    return None


def _geri_koy(aday: dict, birim: Mapping) -> str:
    """Reddedilen çıkarmanın birimini içeriğe GERİ KOYAR; yeni yolunu döner.

    Yalnız EKLEME yapılır (liste sonuna), böylece daha önce bağlanmış yolların
    sıra numaraları KAYMAZ.

    **KAPSAM SINIRI, dürüst etiket:** düz metin alanı ve `ozel_gun` yuvası geri
    konulamaz. Düz metin alanı zaten kapalı alan kümesinin parçasıdır ve
    "çıkarılmış" hâli yazım kapısını geçemez; `ozel_gun` yuvası ise tek başına
    değil beş yuvalı bir girdinin parçasıdır ve tek yuvayı geri koymak eksik
    girdi üretirdi. İkisi de fail-closed düşer — sessizce atlanmaz.
    """
    yol = str(birim["oge_yolu"])
    deger = copy.deepcopy(birim["deger"])

    # Birim ZATEN yerinde ve DEĞİŞMEMİŞ olabilir: model çıkarmayı günlükte
    # önerip içerikten hiç düşürmemiş olabilir (düz metin alanı zaten kapalı
    # alan kümesinin parçasıdır ve düşürülemez). O hâlde geri koyma NO-OP'tur,
    # yalnız sahiplenme yazılır. Eşitlik YOLA değil HASH'e bakar: aynı yol
    # başka bir değeri taşıyor olabilir (sıra numaraları KONUMSALDIR) ve o
    # birimi eski kimlikle sahiplenmek yanlış eşleme üretirdi.
    mevcut = identity.enumerate_content_units(aday)
    yerinde = mevcut.get(yol)
    if yerinde is not None and yerinde["oge_sha"] == birim["oge_sha"]:
        return yol

    eslesme = _VIDEO_YOLU_RE.match(yol)
    if eslesme:
        havuz = eslesme.group("havuz")
        if havuz not in VIDEO_POOL_KEYS:
            raise SynthesisFailed(f"tanınmayan video havuzu: {yol}")
        video = aday.setdefault("video_kodlar", {})
        if not isinstance(video, dict):
            raise SynthesisFailed(f"video_kodlar nesne DEĞİL: {type(video).__name__}")
        liste = video.setdefault(havuz, [])
        if not isinstance(liste, list):
            raise SynthesisFailed(f"{yol} havuzu liste DEĞİL")
        liste.append(deger)
        return f"video_kodlar/{havuz}[{len(liste) - 1}]"

    eslesme = _LISTE_YOLU_RE.match(yol)
    if eslesme and eslesme.group("alan") in LIST_FIELDS:
        alan = eslesme.group("alan")
        liste = aday.setdefault(alan, [])
        if not isinstance(liste, list):
            raise SynthesisFailed(f"{alan} liste DEĞİL: {type(liste).__name__}")
        liste.append(deger)
        return f"{alan}[{len(liste) - 1}]"

    raise SynthesisFailed(
        f"reddedilen çıkarma geri KONULAMADI: {yol!r} — liste biçiminde olmayan "
        "birim (düz metin alanı ya da özel gün yuvası) bu katmanda geri "
        "konulamaz; koşu yarım işaretlenir, madde sessizce DÜŞMEZ"
    )


def _satir_kur(ham: Mapping, **zorunlu) -> dict:
    """Modelin satırından ŞEMA alanlarını taşır; kimlik alanlarını EZER."""
    satir = {
        "tur": "karar",
        "karar": ham.get("karar"),
        "gerekce": ham.get("gerekce"),
        "kanit": ham.get("kanit", ""),
        "aktor": "sentez",
    }
    # İsteğe bağlı alanlar AD AD taşınır; listeye yazılmayan alan SESSİZCE DÜŞER.
    # `kaynak_iddia` 2026-09-11'de eklendi (sentez sözleşmesi 2.2): motor atfı
    # onunla adaya bağlar. Listeye alınmasaydı modelin DOĞRU yazdığı her `ekle`
    # kararı üretimde `kaynak-iddia-yok` diye reddedilirdi — kapı çalışır, taşıma
    # kırıktır; bu ancak uçtan uca bir testle görünür.
    for istege_bagli in ("yerine_gecer", "kapsam", "kaynak_iddia"):
        if istege_bagli in ham:
            satir[istege_bagli] = ham[istege_bagli]
    satir.update(zorunlu)
    return satir


def _kimlik_bagla(
    aday: dict,
    ham_gunluk: list,
    aktif_birimler: Mapping[str, Mapping],
    tur: AuditRound,
    sorular: list[str],
) -> tuple[list[dict], list[str]]:
    """Modelin günlüğünü KİMLİĞE ve ÜRETİLEN İÇERİĞE bağlar.

    Sıra bağlayıcıdır: önce satırlar sınıflanır ve çıkarma eşiği uygulanır,
    SONRA reddedilenler içeriğe geri konur, EN SON yol/alan/hash üretilen
    içerikten yeniden hesaplanır. Ters sırada bir geri koyma, kendisinden önce
    bağlanmış hash'leri bayatlatırdı.

    Kimlik yola göre DEĞİL, yol kimliğe göre çözülür: sıra numaraları
    konumsaldır ve iki tur arasında kayar.
    """
    yasayan: list[tuple[dict, str]] = []
    olu: list[tuple[dict, str]] = []
    notlar: list[dict] = []
    reddedilen: list[tuple[str, str, Mapping]] = []
    kullanilan: set[str] = set()
    acik_sorular = list(sorular)

    for sira, ham in enumerate(ham_gunluk):
        etiket = f"karar_gunlugu[{sira}]"
        if not isinstance(ham, Mapping):
            raise SynthesisFailed(f"{etiket} nesne DEĞİL: {type(ham).__name__}")
        if ham.get("tur") == "not":
            notlar.append(dict(ham))
            continue
        if ham.get("tur") != "karar":
            raise SynthesisFailed(
                f"{etiket} tur değeri kapalı kümenin dışında: {ham.get('tur')!r}"
            )
        karar = ham.get("karar")
        if karar not in identity.KARAR_DEGERLERI:
            raise SynthesisFailed(
                f"{etiket} karar değeri kapalı kümenin dışında: {karar!r}"
            )

        if karar == "ekle":
            # YENİ birimin kimliği sistemindir, modelin değil: model uydurduğu
            # bir kimliği ikinci kez kullanabilir ve iki birim tek kimliğe
            # düşerdi.
            unit_id = identity.new_unit_id()
        else:
            unit_id = ham.get("unit_id")
            if not isinstance(unit_id, str) or unit_id not in aktif_birimler:
                raise SynthesisFailed(
                    f"{etiket} {karar!r} satırı aktif pakette BULUNMAYAN kimliğe "
                    f"işaret ediyor: {unit_id!r} — kimlik taşıması aktif paketten "
                    "türer, uydurulamaz"
                )
        if unit_id in kullanilan:
            raise SynthesisFailed(
                f"{etiket} aynı kimlik ikinci karar satırını taşıyor: {unit_id!r} — "
                "bir birim bir günlükte TEK sonuç alır"
            )
        kullanilan.add(unit_id)

        if karar in ("cikar", "kirp"):
            sebep = _cikarma_kapisi(
                unit_id, str(aktif_birimler[unit_id]["alan"]), tur, karar=karar
            )
            if sebep is not None:
                reddedilen.append((unit_id, sebep, ham))
                continue

        satir = _satir_kur(ham, unit_id=unit_id)
        if karar in identity.YASAYAN_KARARLAR:
            yol = ham.get("oge_yolu")
            if not isinstance(yol, str) or not yol:
                raise SynthesisFailed(f"{etiket} oge_yolu TAŞIMIYOR: {yol!r}")
            yasayan.append((satir, yol))
        else:
            olu.append((satir, unit_id))

    # Reddedilen çıkarmanın EŞİ olan `ekle` satırı artık bir şeyin yerine
    # geçmiyor: hedef birim yaşıyor. Bağ bırakılsaydı günlük, olmamış bir
    # değiştirmeyi olmuş gibi gösterirdi (K-154'ün çift bağı tek yönlü yalana
    # dönerdi). Aday DÜŞÜRÜLMEZ — yalnız bağ çözülür ve açık soru bunu söyler.
    reddedilen_kimlikler = {unit_id for unit_id, _, _ in reddedilen}
    for satir, _ in yasayan:
        if satir.get("yerine_gecer") in reddedilen_kimlikler:
            satir.pop("yerine_gecer")

    for unit_id, sebep, ham in reddedilen:
        birim = aktif_birimler[unit_id]
        yeni_yol = _geri_koy(aday, birim)
        yasayan.append(
            (
                {
                    "tur": "karar",
                    "karar": "koru",
                    "gerekce": f"Çıkarma reddedildi ve birim korundu: {sebep}",
                    "kanit": ham.get("kanit", "") if isinstance(ham, Mapping) else "",
                    "aktor": "sentez",
                    "unit_id": unit_id,
                },
                yeni_yol,
            )
        )
        acik_sorular.append(f"{unit_id}: çıkarma reddedildi — {sebep}")

    birimler = identity.enumerate_content_units(aday)
    gunluk: list[dict] = []
    for satir, yol in yasayan:
        oge = birimler.get(yol)
        if oge is None:
            raise SynthesisFailed(
                f"karar satırının yolu üretilen içerikte YOK: {yol!r} "
                f"(kimlik {satir['unit_id']!r}) — yaşayan karar sahipsiz kalamaz"
            )
        satir["oge_yolu"] = yol
        satir["alan"] = oge["alan"]
        satir["oge_sha"] = oge["oge_sha"]
        gunluk.append(satir)
    for satir, unit_id in olu:
        birim = aktif_birimler[unit_id]
        satir["oge_yolu"] = birim["oge_yolu"]
        satir["alan"] = birim["alan"]
        satir["oge_sha"] = birim["oge_sha"]
        gunluk.append(satir)
    gunluk.extend(notlar)
    return gunluk, acik_sorular


# ─── 5. Koşum ───────────────────────────────────────────────────────────────


async def _kos(
    db,
    tur: AuditRound,
    *,
    run_id: str,
    active_package: Mapping | None,
    removed_history: Sequence[Mapping],
    holiday_keys: set[str],
    runner: Runner,
    dest: Path,
) -> SynthesisResult:
    """Kabul bölgesi + koşum bölgesi. Arıza işaretini ÇAĞIRAN `run` atar."""
    # ── KABUL BÖLGESİ — ilk yan etkiden ÖNCE biter ──────────────────────────
    # Koşu kimliği ÖNCE gramerden geçer. `Path(dest) / run_id` tek başına bir
    # sınır DEĞİLDİR: mutlak bir `run_id` `dest`'i sessizce DÜŞÜRÜR (ölçüldü:
    # Path('/tmp/dest') / '/tmp/kacak' -> '/tmp/kacak'). Kural kardeş yüzeyin
    # (`build_packet`) kullandığının ta kendisidir — ikinci bir gramer yazılmaz;
    # `_RUN_ID_RE` yol ayracını, `..`'yı ve boş adı zaten reddeder, `dest`'in
    # kendi takma adlılığını da `kok_yolunu_kapila` ölçer.
    try:
        kok = kok_yolunu_kapila(Path(dest) / require_run_id(run_id))
    except (ValueError, TypeError) as hata:
        raise SynthesisFailed(f"sentez kökü yol kapısını geçmedi: {hata}") from hata
    if kok.exists():
        raise SynthesisFailed(
            f"sentez kökü ZATEN var: {kok} — ham katman salt-eklemedir, dosya "
            "EZİLMEZ (K-82); yeniden koşum yeni kimlik alır"
        )
    aktif_birimler = _aktif_birimler(active_package)
    # Tur ile aktif paket AYNI görüntüye bakmak ZORUNDA. İkisi bağımsız
    # parametre olduğu için bir çağıran, A sürümüne yazılmış denetçi raporlarını
    # B sürümünün paketiyle eşleştirebilir; o raporlardaki `contradicted`
    # satırları başka bir sürümün birimlerini çıkarma yetkisine dönüşürdü.
    # Ölçüm noktası `PacketRef` ile AYNI: `canonical_sha(decision_units(...))`.
    beklenen_sha = identity.canonical_sha(aktif_birimler)
    for rapor in tur.reports:
        if rapor.unit_snapshot_sha != beklenen_sha:
            raise SynthesisFailed(
                f"denetçi raporu {rapor.denetci!r} BAŞKA bir görüntüye yazılmış "
                f"(rapor {rapor.unit_snapshot_sha}, aktif paket {beklenen_sha}) — "
                "ayrışan görüntünün kanıtı bu paketten birim çıkaramaz"
            )
    try:
        gorev_metni = contracts.require_pinned_text(
            PIN_PATH, ARASTIRMA_DEPOSU_KOKU, GOREV_DOSYASI
        )
    except contracts.ContractDriftError as hata:
        raise SynthesisFailed(f"sözleşme pin kapısı düştü: {hata}") from hata

    # ── KOŞUM BÖLGESİ ───────────────────────────────────────────────────────
    istem = _istem_metni(gorev_metni, tur, active_package, removed_history, holiday_keys)
    kok.mkdir(parents=True)
    istem_yolu = kok / GOREV_DOSYA_ADI
    with istem_yolu.open("x", encoding="utf-8") as akis:
        akis.write(istem)

    sonuc = runner.run(SENTEZ_ARACI, kok, istem_yolu)
    if sonuc.durum != "tamam":
        raise SynthesisFailed(
            f"sentez aracı sonuç ÜRETMEDİ: durum={sonuc.durum!r}, "
            f"cikis={sonuc.exit_code!r}"
        )
    with (kok / CIKTI_DOSYA_ADI).open("x", encoding="utf-8") as akis:
        akis.write(sonuc.stdout)

    bolumler, hatalar = _bolumlere_ayir(sonuc.stdout)
    if hatalar:
        raise SynthesisFailed("; ".join(hatalar))

    aday = _json_govdesi(
        bolumler[SENTEZ_BOLUM_ANAHTARLARI[0]], SENTEZ_BOLUM_ANAHTARLARI[0]
    )
    if not isinstance(aday, dict):
        raise SynthesisFailed(
            f"{SENTEZ_BOLUM_ANAHTARLARI[0]} nesne DEĞİL: {type(aday).__name__}"
        )
    ham_gunluk = _json_govdesi(
        bolumler[SENTEZ_BOLUM_ANAHTARLARI[1]], SENTEZ_BOLUM_ANAHTARLARI[1]
    )
    if not isinstance(ham_gunluk, list):
        raise SynthesisFailed(
            f"{SENTEZ_BOLUM_ANAHTARLARI[1]} liste DEĞİL: {type(ham_gunluk).__name__}"
        )
    sorular = _liste_ogeleri(bolumler[SENTEZ_BOLUM_ANAHTARLARI[2]])
    ozet = bolumler[SENTEZ_BOLUM_ANAHTARLARI[3]].strip()
    if not ozet:
        raise SynthesisFailed(
            f"{SENTEZ_BOLUM_ANAHTARLARI[3]} BOŞ — onay ekranının girdisi boş olamaz"
        )

    gunluk, sorular = _kimlik_bagla(aday, ham_gunluk, aktif_birimler, tur, sorular)

    # Plan 1 yazım kapısı YENİDEN KULLANILIR. İki dış girdisinden marka adları
    # çağırandan değil VERİTABANINDAN okunur (R8 doktrini): çağıran boş liste
    # verirse K-15 sessizce kapanırdı.
    marka_satirlari = await db.fetch(
        "SELECT name FROM social.brands WHERE name IS NOT NULL"
    )
    dogrulama = validate_package_content(
        aday,
        banned_brand_names=[satir["name"] for satir in marka_satirlari],
        holiday_keys=set(holiday_keys),
    )
    if not dogrulama.ok:
        raise SynthesisFailed(
            "aday paket yazım kapısını geçmedi: " + "; ".join(dogrulama.errors)
        )

    denetci_onerisi = max(
        (len(_liste_ogeleri(rapor.bolumler.get(ONERI_BOLUMU, ""))) for rapor in tur.reports),
        default=0,
    )
    tasma = (
        len(sorular) > K74_ACIK_SORU_TAVANI
        or denetci_onerisi > K75_DENETCI_ONERI_TAVANI
    )

    sonuc_nesnesi = SynthesisResult(
        aday_json=aday,
        karar_gunlugu=tuple(gunluk),
        acik_sorular=tuple(sorular),
        onay_ozeti=ozet,
        tasma=tasma,
    )
    kapi_hatalari = validate(sonuc_nesnesi)
    if kapi_hatalari:
        raise SynthesisFailed(
            "sentez çıktısı kendi kapısını geçmedi: " + "; ".join(kapi_hatalari)
        )
    return sonuc_nesnesi


async def run(
    db,
    round: AuditRound,
    *,
    run_id: str,
    active_package: Mapping | None,
    removed_history: Sequence[Mapping],
    holiday_keys: set[str],
    runner: Runner,
    dest: Path,
) -> SynthesisResult:
    """Sentez turunu koşturur ve doğrulanmış aday kümesini döner.

    `round` adı planın imzasından gelir ve yerleşik `round`'u bu gövdede
    gölgeler; gövde yuvarlama yapmaz, çakışma zararsızdır.

    **K-150 kapısı DB'ye dokunmaz.** Geçersiz tur zaten `run_audit_round`
    tarafından işaretlenmiştir; buradan ikinci bir `mark_incomplete` o satırın
    GERÇEK sebebini ezerdi.

    **`removed_history` bu katmanda KAPI DEĞİLDİR — beyan edilir.** Geri-ekleme
    tespiti sözleşmenin ADIM 2'sinde modelin işidir (çıkarılanlar listesiyle
    eşleşen aday "geri-ekleme önerisi" olarak işaretlenir ve çelişki açık soru
    olur). Bu modül listeyi isteme TAŞIR ama eşleşmeyi kendi ölçmez; ölçseydi
    metne dayalı ikinci bir eşleştirme kuralı doğar ve sözleşmeyle ayrışırdı.

    Sonrasındaki her yol dış korumanın içindedir: beklenen arıza da beklenmeyen
    istisna da iptal de koşu satırını `calisiyor` ASILI bırakmaz (K-82).
    """
    if not round.gecerli:
        raise SynthesisFailed(
            f"tur GEÇERSİZ, sentez başlamaz (K-150): {round.sebep!r}"
        )
    # Kimlik grameri dış korumanın DIŞINDA, ondan ÖNCE koşar. İçeride koşsaydı
    # arıza yolu `mark_incomplete`'i geçersiz bir kimlikle çağırır, o da kendi
    # gramerinden düşer ve özgün sebebi EZERDİ — koşu satırı işaretsiz kalır,
    # çağıran da yanlış istisnayı görürdü.
    try:
        require_run_id(run_id)
    except (ValueError, TypeError) as hata:
        raise SynthesisFailed(f"koşu kimliği gramerden geçmedi: {hata}") from hata
    try:
        return await _kos(
            db,
            round,
            run_id=run_id,
            active_package=active_package,
            removed_history=removed_history,
            holiday_keys=holiday_keys,
            runner=runner,
            dest=dest,
        )
    except SynthesisFailed as ariza:
        await runs.mark_incomplete(
            db, run_id=run_id, asama=SENTEZ_ASAMASI, sebep=str(ariza)
        )
        raise
    except BaseException as beklenmeyen:
        # EN İYİ ÇABA: işaretin kendisi düşerse özgün istisna YUTULMAZ.
        try:
            await runs.mark_incomplete(
                db,
                run_id=run_id,
                asama=SENTEZ_ASAMASI,
                sebep=f"beklenmeyen arıza: {beklenmeyen!r}",
            )
        except BaseException:
            pass
        raise
