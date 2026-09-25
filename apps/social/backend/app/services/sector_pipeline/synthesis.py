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
import logging
import re
import shutil
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence

from app.services.sector_content_schema import (
    CURRENT_SCHEMA_VERSION,
    LIST_FIELDS,
    VIDEO_POOL_KEYS,
    structural_errors,
)
from app.services import sector_content_schema as sema
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
    RunnerOutcome,
    anonymize,
    iddia_evreni,
    kaynak_iddialari_coz,
    kok_yolunu_kapila,
)
from app.services.sector_pipeline.brief_doctor import (
    TEMEL_ALAN_ANAHTARLARI,
    CIddia,
    DoctorReport,
    alan_karsilastirma_anahtari,
    iddiasiz_kaynaklar,
)

_LOG = logging.getLogger(__name__)

SENTEZ_ASAMASI = "sentez"
"""`runs.ASAMALAR` içindeki aşama adı — bildirim anahtarı koşu + aşamadır."""

GOREV_DOSYASI = "hakem-sentez-gorevi.md"
"""Pinlenmiş sentez sözleşmesinin dış depodaki adı."""

GOREV_DOSYA_ADI = "00-SENTEZ-GOREVI.md"
CIKTI_DOSYA_ADI = "01-SENTEZ-CIKTISI.md"

SENTEZ_DUZELTME_HAKKI = 1
"""İlk üretimden SONRA kaç düzeltme çağrısı yapılabilir.

**Neden var (2026-09-22 ölçümü).** Sekiz kayıtlı sentez denemesi birbirinden
FARKLI sebeplerle düştü — plan kipi · karar günlüğü biçimi · CTA şekli ·
kesilme. Her düşüş koşuyu K-82 gereği terminal yaptığı için 24-25 dakikalık
denetçi turunu da beraberinde götürdü; bir günde iki kez ödendi.

**Neden 1.** Düzeltme çağrısı ÜCRETLİDİR (ölçüldü: tek sentez çağrısı 11,6
dakika · 2,45 USD). Bir hak, denetçi turunu kurtarmaya yeter; ikinci hakkın
kazandıracağını gösteren ÖLÇÜM yok. Sayı ölçümle artar, tahminle değil.
"""


def _cikti_dosya_adi(deneme: int) -> str:
    """Deneme başına AYRI çıktı dosyası — önceki EZİLMEZ.

    İlk denemenin adı `CIKTI_DOSYA_ADI` ile birebir aynıdır: düzeltme hakkı
    eklenmesi, tek denemede biten turların dosya adını DEĞİŞTİRMEZ.
    """
    return CIKTI_DOSYA_ADI if deneme == 1 else f"{deneme:02d}-SENTEZ-CIKTISI.md"

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
    r"^(?:#{1,6}[ \t]+)?(\d)\)[ \t]+([A-ZÇĞİÖŞÜ_][A-ZÇĞİÖŞÜ_ ]*?)[ \t]*(?:[—(:].*)?$",
    re.M,
)
"""Sentez bölüm başlığı — denetçi kapısıyla AYNI tolerans, aynı gerekçe.

Desen `auditors._BOLUM_BASLIGI_RE`'nin ikizidir. Kusur denetçi turunda ölçüldü
(iki araç da `## 1) …` yazdı); aynı refleksi sentez aracının göstermesi için
bir sebep yoktu — tek hata izole değildir, onu doğuran desen buraya
KOPYALANMIŞTI ve bir sonraki adımda aynı şekilde düşerdi. İkinci tolerans
(addan sonraki `—`/`(`/`:` süsü) de aynı gün, bu dosyada ÖLÇÜLDÜ: araç
`# 4) ÖZET (operatör onay ekranı)` yazdı.
"""
_JSON_FENCE_RE = re.compile(r"```[A-Za-z0-9_-]*[ \t]*\n(.*?)\n[ \t]*```", re.S)
"""Çitli blok deseni — etiket SERBEST, çünkü etiketi model seçiyor.

**Neden `json` sabiti KALDIRILDI (2026-09-22).** Desen `json` ve çıplak etiketi
tanıyor, `jsonl`i TANIMIYORDU. O çıktılarda hiç çit bulunmuyor, okuyucu
gövdenin TAMAMINI satır satır tarayan yedek yola düşüyor ve tesadüfen doğru
sonucu veriyordu — yani doğruluk, modelin seçtiği etikete bağlıydı. Etiket
serbest bırakılınca davranış her iki yazımda da AYNI yoldan geçer.
"""
_LISTE_OGESI_RE = re.compile(
    r"^(?P<girinti>[ \t]*)(?:[-*•]|\d+[.)])[ \t]+(?P<metin>\S.*?)[ \t]*$"
)
_OGE_AYRACI = " — "

_LISTE_YOLU_RE = re.compile(r"^(?P<alan>[a-z_]+)\[(?P<sira>\d+)\]$")
_VIDEO_YOLU_RE = re.compile(r"^video_kodlar/(?P<havuz>[a-z]+)\[(?P<sira>\d+)\]$")


class SynthesisFailed(RuntimeError):
    """Sentez terminal arızası — yarım sonuç motora ULAŞMAZ."""


class SynthesisOutputError(SynthesisFailed):
    """Model ÇIKTISININ biçimi hatalı — aynı girdiyle düzeltme istenebilir.

    `SynthesisFailed` terminal anlam taşır ve öyle KALIR; bu alt sınıf o
    kümenin içinden YALNIZ "modelin yazdığı belge yanlış biçimde" hâlini
    ayırır. Ayrım dar tutulur, çünkü her genişletme bir model çağrısı daha
    ödetir:

    **Kapsamda:** eksik/sırasız bölüm · okunamayan JSON gövdesi · bölümün
    beklenen tipte olmaması · boş özet.

    **Kapsam DIŞI (hemen terminal):** sözleşme pin sapması · eksik denetçi ·
    geçersiz tur · aracın hiç koşmaması ya da zaman aşımı · ölçüm taşımayan
    zarf · veritabanı hatası · içerik yazım kapısı. Bunların hiçbiri "modele
    tekrar sor" ile düzelmez; tekrar sormak arızayı gizler.
    """


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
    hatalar = list(structural_errors(icerik, schema_version=CURRENT_SCHEMA_VERSION))
    if not hatalar:
        # Şekil geçtiyse birimler numaralandırılabilir; araştırma etiketi
        # taşıyan birim sonucu DÜŞÜRÜR (Codex Ek 2.3 — kanıt kaydı pakete sızmaz).
        hatalar.extend(
            f"{yol}: paket metni araştırma etiketi taşıyor (`[C: …]` · "
            "`[uyarlama]` · `destek=` · `yer=`) — kanıt kaydı karar girdisidir, "
            "paket içeriği değil"
            for yol in arastirma_etiketi_sizintilari(icerik)
        )
    gunluk = [dict(satir) for satir in result.karar_gunlugu]
    hatalar.extend(identity.validate_decision_log(gunluk))
    if not hatalar:
        # Bütünlük ancak iki kapı da geçilmişse ÖLÇÜLEBİLİR; `check_unit_integrity`
        # kendi içinde de bunu sorar, ama hatayı iki kez raporlamayalım.
        hatalar.extend(
            identity.check_unit_integrity(
                icerik, gunluk, schema_version=CURRENT_SCHEMA_VERSION
            )
        )
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


def _cikti_butcesini_dogrula(sonuc: RunnerOutcome) -> None:
    """Koşum kendi ÖLÇÜMÜNÜ taşımalı; taşımıyorsa zarf okunamamıştır.

    Ölçümün YOKLUĞU başarı sayılmaz: sentez `json` kipinde koşar, yani ölçüm
    taşımayan bir sonuç zarfın okunamadığı anlamına gelir ve o hâlde gövdenin
    tam olup olmadığı BİLİNMEZ (İlke 9(4): doğrulanmamış, "sorunsuz" değil).

    **BURADA JETON TAVANI YOKTUR — denendi ve ZARAR VERDİ (2026-09-22).**
    Kısa ömürlü bir kapı, bildirilen kümülatif çıktı jetonu 48.000'i aşınca
    turu düşürüyordu. Ölçüm yanlış şeyi sayıyordu: zarfın `output_tokens`
    alanı TÜM turların toplamıdır ve model düşünmesini AYRI bir mesaja
    koyabilir. `kosu-8a2081d4…` koşumunda düşünme turu 56.554 jeton yedi,
    cevap turu 22.468 jetonla 39.082 karakteri TEK mesajda ve `end_turn` ile
    tamamladı; dosya dört bölümün dördünü de taşıyordu (biçim kapısı 0 hata).
    Kapı o sağlam turu öldürdü ve bir denetçi turunu (24 dk + para) çöpe attı.
    Kesilmenin doğru işareti bir mesajın `max_tokens` ile bitmesidir ve `json`
    zarfı yalnız SON mesajın `stop_reason`'ını verir — yani bu zarfla
    ölçülemez. Vekil bir sayıyla kapı kurulmaz.
    """
    olcum = sonuc.olcum
    if olcum is None:
        raise SynthesisFailed(
            "sentez koşumu ÖLÇÜM taşımıyor — `json` kipinde zarf okunamamış "
            "demektir; gövdenin kesilip kesilmediği doğrulanamaz"
        )


def _cikti_bicimini_coz(ham: str) -> tuple[dict, list, list[str], str]:
    """Modelin yazdığı belgeyi dört parçaya çözer.

    Bu fonksiyonun attığı HER hata `SynthesisOutputError`'dur, yani düzeltme
    hakkı kapsamındadır. Kapsamı genişletmek isteyen, hatayı BURAYA taşır —
    böylece "ne düzeltilebilir" sorusunun tek bir yeri olur.
    """
    bolumler, hatalar = _bolumlere_ayir(ham)
    if hatalar:
        raise SynthesisOutputError("; ".join(hatalar))

    aday = _json_govdesi(
        bolumler[SENTEZ_BOLUM_ANAHTARLARI[0]], SENTEZ_BOLUM_ANAHTARLARI[0]
    )
    if not isinstance(aday, dict):
        raise SynthesisOutputError(
            f"{SENTEZ_BOLUM_ANAHTARLARI[0]} nesne DEĞİL: {type(aday).__name__}"
        )
    ham_gunluk = _json_govdesi(
        bolumler[SENTEZ_BOLUM_ANAHTARLARI[1]], SENTEZ_BOLUM_ANAHTARLARI[1]
    )
    if not isinstance(ham_gunluk, list):
        raise SynthesisOutputError(
            f"{SENTEZ_BOLUM_ANAHTARLARI[1]} liste DEĞİL: {type(ham_gunluk).__name__}"
        )
    sorular = _liste_ogeleri(bolumler[SENTEZ_BOLUM_ANAHTARLARI[2]])
    ozet = bolumler[SENTEZ_BOLUM_ANAHTARLARI[3]].strip()
    if not ozet:
        raise SynthesisOutputError(
            f"{SENTEZ_BOLUM_ANAHTARLARI[3]} BOŞ — onay ekranının girdisi boş olamaz"
        )
    return aday, ham_gunluk, sorular, ozet


def _duzeltme_istemi(istem: str, hata: SynthesisOutputError, deneme: int) -> str:
    """Özgün istem + doğrulayıcının SOMUT hatası.

    **"Devam et" YETMEZ — ölçüldü (2026-09-22).** `kosu-3f22d638…` koşumunda
    araç kendiliğinden devam etti (*"Output token limit hit. Resume directly"*)
    ve devam mesajında da dört bölümün ikisini yazmadan bitirdi. Modele NEYİN
    yanlış olduğu söylenmezse aynı belgeyi aynı kusurla üretir.

    Belge BAŞTAN istenir, parça istenmez: kesilmiş bir gövdeyle yeni parçayı
    birleştirmek, modelin bölümü yeniden yazmış ya da JSON ortasında kesilmiş
    olma ihtimali yüzünden UYDURMA üretir.
    """
    return (
        f"{istem}\n\n"
        "---\n\n"
        f"## ÖNCEKİ DENEME REDDEDİLDİ (deneme {deneme})\n\n"
        "Yukarıdaki görevi bir kez ürettin; çıktı mekanik doğrulamadan GEÇMEDİ. "
        "Doğrulayıcının bulduğu somut hata:\n\n"
        f"> {hata}\n\n"
        "Şimdi belgenin TAMAMINI baştan yaz. Parça, ek ya da yama gönderme: "
        "dört bölüm de (`ADAY PAKET` · `DECISION_LOG` · `AÇIK SORULAR` · "
        "`ÖZET`) eksiksiz, numaralı ve sözleşmedeki SIRAYLA olmalı. "
        "Açıklama, özür ya da ne yaptığının özeti YAZMA — yalnız belgeyi ver.\n"
    )


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


def _satir_satir_json(ham: str) -> list | None:
    """JSONL gövdesi → liste; gövde JSONL DEĞİLSE `None`.

    **Neden tolerans (ÖLÇÜLDÜ 2026-09-18, 906 sn'lik tur):** araç karar
    günlüğünü köşeli ayraçsız, satır başına bir nesne olarak yazdı; bir önceki
    turda AYNI araç düzgün dizi yazmıştı. İki biçim de TEK ANLAMLIDIR — fark
    yazımdadır, anlamda değil — ve her sapma bir tam turu (~15 dk + jeton)
    yakıyor.

    **Tolerans KÖRLÜK DEĞİLDİR:** her boş olmayan satır tek başına geçerli bir
    JSON NESNESİ olmak ZORUNDA. Tek bozuk satır `None` döndürür ve çağıran
    özgün ayrıştırma hatasını fırlatır (negatif kontrolü testte).
    """
    ogeler: list = []
    for satir in ham.splitlines():
        parca = satir.strip().rstrip(",")
        if not parca:
            continue
        try:
            oge = json.loads(parca)
        except (json.JSONDecodeError, ValueError):
            return None
        if not isinstance(oge, dict):
            return None
        ogeler.append(oge)
    return ogeler or None


def _json_govdesi(govde: str, etiket: str) -> Any:
    """Bölümün JSON gövdesi — çitli blokların TAMAMI, yoksa bölümün kendisi.

    İki okuma yolu YOKTUR: çit varsa gövde çitlerin içidir; model çiti unutursa
    bölümün tamamı denenir. Ayrıştırılamayan gövde SESSİZ boş sonuç üretmez.

    **BİRDEN ÇOK BLOK KAYIP ÜRETMEZ (2026-09-22 ölçümü).** Önceki yazım
    `.search()` ile yalnız İLK bloğu alıyordu ve kalanı sessizce düşürüyordu.
    Kayıtlı sekiz çıktının ayrıştırılabilen altısında bu iki kez gerçekleşti:
    `kosu-7705437…` 79 kaydın 60'ını, `DUSMUS-2026-09-18-jsonl-…` 90 kaydın
    61'ini döndürüyordu. Birincisi VERİTABANINA da 60 kayıtla indi — reddedilen
    adayların denetim izi hiç yazılmadı.

    Bugünkü kural: her blok AYRI ayrıştırılır ve sonuçlar BİRLEŞTİRİLİR, ama
    yalnız birleştirilebilir olanlar. Bloklardan biri liste değilse (ör. aday
    paket gibi TEK nesne) çokluk ANLAMSIZDIR ve reddedilir — hangi nesnenin
    geçerli olduğunu seçmek UYDURMA olurdu. Bozuk blok da yutulmaz: kayıpsızlık,
    hatayı görmezden gelmek değildir.
    """
    bloklar = [parca for parca in _JSON_FENCE_RE.findall(govde)]
    if not bloklar:
        return _tek_govde(govde, etiket)
    if len(bloklar) == 1:
        return _tek_govde(bloklar[0], etiket)

    okunan = [_tek_govde(parca, f"{etiket} (blok {sira})")
              for sira, parca in enumerate(bloklar, start=1)]
    if all(isinstance(parca, dict) for parca in okunan):
        # Hepsi NESNE: bölüm ya tek nesneliktir (aday paket) ya da her blok tek
        # kayıtlık bir günlüktür — ikisi bu gövdeden AYIRT EDİLEMEZ. Birini
        # seçmek uydurma olurdu, o yüzden reddedilir.
        raise SynthesisOutputError(
            f"{etiket} bölümü birden çok çitli blok taşıyor ve hepsi tek NESNE "
            f"({len(okunan)} blok) — hangisinin geçerli olduğu ya da bunların "
            "tek bir günlük mü olduğu gövdeden anlaşılmıyor; bölüm TEK blokta "
            "yazılmalı"
        )
    # En az biri liste: bölüm KAYIT DİZİSİDİR. Tek kayıtlık blok (`{...}`) o
    # dizinin bir öğesidir; atılmaz, tek öğelik liste gibi eklenir.
    birlesik: list[Any] = []
    for parca in okunan:
        if isinstance(parca, list):
            birlesik.extend(parca)
        else:
            birlesik.append(parca)
    return birlesik


def _tek_govde(ham: str, etiket: str) -> Any:
    """Tek bir gövdeyi okur: önce JSON, sonra satır-satır JSON (JSONL)."""
    try:
        return json.loads(ham)
    except (json.JSONDecodeError, ValueError) as hata:
        satirlar = _satir_satir_json(ham)
        if satirlar is not None:
            return satirlar
        raise SynthesisOutputError(
            f"{etiket} bölümü JSON olarak okunamadı: {hata}"
        ) from hata


def _liste_ogeleri(govde: str) -> list[str]:
    """ÜST DÜZEY madde imli satırları öğe olarak okur; daha derin girintili
    satırlar bir önceki öğeye katılır.

    **KAPSAM SINIRI, sessizce atlanmaz.** Kural YAPISALDIR: madde imi (`-`,
    `*`, `•`, `1.`, `1)`) taşıyan satırlardan girintisi bölümdeki EN SIĞ olanlar
    öğe başlatır — sütun 0 değil, çünkü bütün liste girintili yazılabilir. Daha
    derin girintili boş olmayan satır (alt madde ya da devam satırı) bir önceki
    öğeye `_OGE_AYRACI` ile katılır: içerik kaybolmaz, sayı artmaz. İmsiz serbest
    düz yazı SIFIR öğe verir; üst düzeyde ya da daha sığda duran imsiz satır hiçbir
    öğeye katılmaz. Üst maddeyle AYNI girintide yazılmış alt madde yapısal olarak
    ayırt edilemez ve ayrı öğe sayılır.

    **Neden (2026-09-23, ölçüldü):** eski kural HER madde imli satırı sayıyordu.
    `kosu-2851dc22…` sentezi her açık soruyu bir üst madde + iki girintili alt
    madde ("İki taraf", "Eğilimim") olarak yazdı — sözleşme her soru için bu üçünü
    ister, biçim dayatmaz. 10 soru 30 sayıldı, denetçi-1'in 5 önerisi 9 sayıldı;
    `tasma` iki koldan da yanlış yandı ve 30 parça motorun açık soru kimliklerine,
    oradan onay ekranına taşındı.

    Buradaki sayı bir KAPI değil, yalnız `tasma` işaretinin girdisidir — yanlış
    saymak hiçbir koşuyu durdurmaz, yalnız işareti eksik/fazla koyar. Serbest
    metinden madde SAYISI çıkarmaya çalışan bir yaklaşım (semantik olumsuzlama)
    bilinçle terk edilmiştir.
    """
    satirlar = [satir.expandtabs(4) for satir in govde.splitlines()]
    eslesmeler = [_LISTE_OGESI_RE.match(satir) for satir in satirlar]
    girintiler = [len(m.group("girinti")) for m in eslesmeler if m]
    if not girintiler:
        return []
    ust_duzey = min(girintiler)
    ogeler: list[list[str]] = []
    for satir, eslesme in zip(satirlar, eslesmeler):
        girinti = len(satir) - len(satir.lstrip(" "))
        if eslesme and girinti == ust_duzey:
            ogeler.append([eslesme.group("metin")])
        elif ogeler and girinti > ust_duzey and satir.strip():
            ogeler[-1].append(eslesme.group("metin") if eslesme else satir.strip())
    return [_OGE_AYRACI.join(parcalar) for parcalar in ogeler]


# ─── 3. İstem kurulumu ──────────────────────────────────────────────────────


def _sema_sekli() -> str:
    """EK-L gövdesi — alan ŞEKİLLERİ yazım kapısının sabitlerinden ÜRETİLİR.

    **Neden makineden (2026-09-18):** aynı gün ÜÇ sözleşme sapması ölçüldü
    (bölüm başlığı biçimi · `oge_sha` hükmü · `cta_kaliplari` öğe şekli) ve
    üçü de aynı sınıftan: elle bakımlı düz yazı, makine kapısının okuduğu
    şemadan sessizce ayrışıyor. Her sapma bir tam turu (~18 dk + jeton)
    yakıyor. Bu ek sapmayı TEKİL olarak yamamak yerine kaynağı tek yere
    bağlar: şema değişirse ek kendiliğinden değişir.
    """
    satirlar = [
        "Alan şekilleri AŞAĞIDAKİ gibidir; düz yazı ile çelişirse BU EK geçerlidir.",
        "",
        f"- Metin alanları: {', '.join(sema.TEXT_FIELDS)}",
        f"- Liste alanları: {', '.join(sema.LIST_FIELDS)}",
        (
            "- `cta_kaliplari` öğesi NESNEDİR, anahtar kümesi TAM ve kapalı: "
            f"{{{', '.join(sorted(sema.CTA_ITEM_KEYS))}}} — üçü de metin"
        ),
        (
            "- `video_kodlar` iki havuz taşır: "
            f"{', '.join(sema.VIDEO_POOL_KEYS)} — ikisi de metin LİSTESİ"
        ),
        (
            "- `ozel_gun[<anahtar>]` yuvaları (hepsi METİN, dizi DEĞİL): "
            f"{', '.join(sema.SPECIAL_DAY_SLOTS)}"
        ),
        (
            "- `[kanal-bağımlı: X]` etiketinde X kapalı kümedir: "
            f"{', '.join(sorted(sema.CHANNEL_KEYS))}"
        ),
        f"- Bilinçli boş alanın RESMÎ değeri: {sema.DELIBERATELY_EMPTY!r}",
    ]
    return "\n".join(satirlar)


def _etiket_sirasi(etiket: str) -> tuple[int, int]:
    """`K2#13` → `(2, 13)`. Ayrıştırıcı TEK yerdedir, burada yeniden yazılmaz."""
    iddialar = kaynak_iddialari_coz(etiket)
    if not iddialar:
        # Ulaşılmaz olmalı — etiketi üreten `KaynakIddiasi.etiket`'in kendisi.
        # "Olmalı" bir kapı değildir: çözülemeyen etiket sona alınır, ATILMAZ.
        return (10**6, 10**6)
    return (iddialar[0].kaynak, iddialar[0].iddia)


def _iddia_gorunumu(etiket: str, iddia: CIddia) -> str:
    """EK-M satır parçası: `K1#3 {destek=öneri; yer=Bölüm 2}` (+ `[uyarlama]`)."""
    destek = iddia.destek or "?"
    if iddia.uyarlama:
        destek = f"{destek} [uyarlama]"
    yer = iddia.yer or "?"
    return f"{etiket} {{destek={destek}; yer={yer}}}"


# ARAŞTIRMA BİLGİSİ ≠ PAKET İÇERİĞİ (Codex Ek 2.3, dış depo `0824c0f`): geri
# bağlantı, uyarlama etiketi, destek ve yer KANIT kayıtlarıdır; sentez bunları
# KARAR verirken kullanır, nihai paket metnine YAZMAZ. Bu desen aday paketin
# HER metin biriminde aranır ve bulunursa sonuç REDDEDİLİR (fail-closed) —
# "EK-L değişmez" hükmü bu koşulla geçerlidir. Köşeli ayraçlı DEĞİŞKEN
# (`[duygusal an]`) ve kanal bayrağı (`[kanal-bağımlı: …]`) desene GİRMEZ.
_ARASTIRMA_ETIKETI_RE = re.compile(
    r"\[\s*C\s*:|\[\s*uyarlama\s*\]|\bdestek\s*=|\byer\s*=", re.IGNORECASE
)


def arastirma_etiketi_sizintilari(icerik: Mapping) -> list[str]:
    """Aday paket metninde araştırma etiketi taşıyan birimler — yol listesi.

    TEK kural, TEK yer: `validate` (sentez çıktısı kapısı) burayı çağırır;
    regresyon testi de aynı fonksiyonu çağırır. Birim kümesi
    `identity.enumerate_content_units`'ten gelir — paket şemasının okuduğu
    yollar; ikinci bir gezinti yazılmaz. Sözlük öğeler (CTA nesnesi) JSON
    olarak taranır ki `gerekce` alanı da kapsansın.
    """
    sizanlar: list[str] = []
    for yol, birim in identity.enumerate_content_units(dict(icerik)).items():
        deger = birim["deger"]
        metin = (
            deger
            if isinstance(deger, str)
            else json.dumps(deger, ensure_ascii=False, sort_keys=True, default=str)
        )
        # MARKDOWN KAÇIŞI SAYDAM (Codex bulgu 5, orta — ÖLÇÜLDÜ 2026-09-21):
        # `\[uyarlama\]` ve `\[C\: 3\]` kapıdan geçiyordu. Desen ters eğik
        # çizgisi düşürülmüş metinde aranır — brief-doctor'un `_yapi_gorunumu`
        # ilkesiyle aynı yön: süs anlamı değiştirmez, kapıyı da geçirmez.
        if _ARASTIRMA_ETIKETI_RE.search(metin.replace("\\", "")):
            sizanlar.append(yol)
    return sizanlar


def _iddia_dizini(raporlar: Sequence[DoctorReport]) -> str:
    """EK-M gövdesi — `K<kaynak>#<iddia>` → ALAN dizini, MOTORUN tablosundan.

    **Neden makineden (2026-09-19, canlı koşu `kosu-222706dc…`):** sentez ham
    araştırma raporlarını göremiyor ve Bölüm C'nin `alan/dönem` hücresini
    bilemiyor. Sözleşme `kaynak_iddia`'yı ZORUNLU tutuyor, motor da onu alan
    eşleşmesiyle mekanik doğruluyor; arada kalan sentez numaraları
    denetçilerin kullanımından TAHMİN etti ve bunu çıktısının ilk cümlesinde
    beyan etti. Ölçülen bedel: 52 `ekle` kararının 8'i, kalan atıfları doğru
    olduğu hâlde TEK bir komşu-alan atıfı yüzünden tümüyle düştü
    (`any(bağsız) → reddet`), ve üç yazım hatasının ikisi buradan doğdu.

    **Eksik olan KURAL DEĞİL VERİYDİ.** Sözleşme bağı zaten doğru tarif
    ediyor (*"o satırın `alan/dönem` hücresi kararın `alan`ıyla örtüşür —
    bunu mekanik ayrıştırıcı doğrular, senin beyanın değil"*). Bu yüzden
    burada yeni bir kural yazılmaz, VAR OLAN kuralın okuduğu tablo modele
    GÖSTERİLİR.

    **Anahtar, motorun KARŞILAŞTIRDIĞI yazımdır.** Bölüm C hücresi markdown
    kaçışlı gelebiliyor (`ton\\_ve\\_dil` — canlı koşuda KAYNAK-1'in üç satırı
    böyleydi) ve motor onu `alan_karsilastirma_anahtari` ile sadeleştirip
    karşılaştırıyor. Ham hücreyi basmak, sentezin motorun hiç görmediği bir
    yazıma bakmasına yol açar — aynı kör noktaya ikinci bir kapıdan girmek.

    Dönem satırında bağ ADDAN değil SİSTEM ANAHTARINDAN kurulur (F3'ün
    kapattığı sınıf): motor `oge_yolu`nun anahtarını `CIddia.anahtarlar`
    kümesinde arar. Bu yüzden dönem satırı anahtarlarıyla listelenir ve
    anahtarı ÇÖZÜLEMEYEN satır dürüstçe "bağ kurulamaz" altına yazılır —
    o numarayı `kaynak_iddia`'ya yazan karar zaten düşecektir.
    """
    evren = iddia_evreni(raporlar)
    alanlar: dict[str, list[str]] = {}
    donemler: dict[str, list[str]] = {}
    bagsizlar: list[str] = []
    # Sıra KAYNAK sonra NUMARA — `K1#3, K1#4, K2#3`. Etiketin kendisi metin
    # olarak sıralanırsa `K1#10` `K1#3`'ten önce gelir ve dizin, modelin
    # tarayacağı tek tabloda okunmaz hâle gelir.
    for etiket, iddia in sorted(
        evren.items(), key=lambda ikili: _etiket_sirasi(ikili[0])
    ):
        anahtar = alan_karsilastirma_anahtari(iddia.alan)
        # TAŞIMA YOLU (Grup 3, dış depo `0824c0f`): destek beyanı · `[uyarlama]`
        # etiketi · kaynak içi yer, iddianın kimliğiyle BİRLİKTE basılır —
        # sentez kaynaksız birimi GÖREREK karar yazar (aday yapmaz, günlüğe
        # "kaynaksız" notuyla geçirir), motor aynı alanları kabul eşlemesinde
        # kullanır. Ham hücre değil, brief-doctor'un kanonik değeri basılır.
        gorunum = _iddia_gorunumu(etiket, iddia)
        if anahtar in TEMEL_ALAN_ANAHTARLARI:
            alanlar.setdefault(anahtar, []).append(gorunum)
        elif iddia.anahtarlar:
            for gun in iddia.anahtarlar:
                donemler.setdefault(gun, []).append(gorunum)
        else:
            bagsizlar.append(etiket)

    satirlar = [
        "`kaynak_iddia`'ya YALNIZ buradan numara yaz. Motor bağı BU tablodan",
        "ölçer; düz yazı ile çelişirse BU EK geçerlidir.",
        "",
        "Her numaranın yanında araştırmacının KANIT KAYDI durur:",
        "`{destek=<tür>; yer=<kaynak içi konum>}` — `destek` kapalı küme",
        "(`uygulama` · `öneri` · `veri` · `mevzuat` · `yok`), `[uyarlama]` kalıbın",
        "kaynaktan TÜRETİLDİĞİNİ söyler. `destek=yok` satırı kalıbın araştırmada",
        "VAR olduğunu gösterir ama dış kanıt taşımaz: mutabakata (kaç araştırmada",
        "var) sayılır, kanıt kapısına SAYILMAZ. Bağladığın satırların HEPSİ",
        "`destek=yok` ise ALAN SINIFINA bak: İÇERİK kalıbını (CTA · kanca ·",
        "görsel · video · takvim · dönem yuvası) ADAY YAPMA — `tur: \"not\"`,",
        "`sinif: \"reddedilen-aday\"` satırıyla, gerekçesi `kaynaksız:` ile",
        "başlayarak günlüğe yaz; RİSK maddesini (`yasaklar_ve_hassasiyetler` ya da",
        "hukuki dil, madde/sayılı atıf veya nicel iddia — yüzde, para, büyük",
        "istatistik — içeren madde; tek başına tarih/ölçü/adet risk DEĞİLDİR)",
        "yine `ekle` olarak yaz — motor onu AÇIK SORUYA düşürür, insan karar",
        "verir; not satırı o yolu kapatır.",
        "Bu kayıtlar KANIT bilgisidir: paket metnine (`kalip` ·",
        "`gerekce` · görsel/video kodu · dönem yuvası) `[C: …]`, `[uyarlama]`,",
        "`destek=` ya da `yer=` YAZMA — yazım kapısı reddeder.",
        "",
        "### Bölüm A alanları — kararın `alan` değeri ile EŞLEŞMELİ",
    ]
    satirlar.extend(
        f"- `{anahtar}`: {', '.join(alanlar[anahtar])}" for anahtar in sorted(alanlar)
    )
    if not alanlar:
        satirlar.append("- (yok)")
    satirlar.extend(
        [
            "",
            "### Bölüm B dönemleri — kararın `oge_yolu` ANAHTARI ile eşleşmeli",
        ]
    )
    satirlar.extend(
        f"- `{gun}`: {', '.join(donemler[gun])}" for gun in sorted(donemler)
    )
    if not donemler:
        satirlar.append("- (yok)")
    if bagsizlar:
        satirlar.extend(
            [
                "",
                "### Bağ KURULAMAYAN iddialar — `kaynak_iddia`'ya YAZMA",
                "Bu satırların `alan/dönem` hücresi ne Bölüm A alanı ne de sistem",
                "anahtarı çözülebilen bir dönem: " + ", ".join(bagsizlar),
            ]
        )
    return "\n".join(satirlar)


def _istem_metni(
    gorev_metni: str,
    tur: AuditRound,
    active_package: Mapping | None,
    removed_history: Sequence[Mapping],
    holiday_keys: set[str],
    *,
    brief: str,
    kok_rehberi: str,
    doktor_raporlari: Sequence[DoctorReport],
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
        # EK-A ve EK-K 2026-09-18'de EKLENDİ. Sözleşme ikisini de "komut
        # otomatik ekler" diye sayıyordu; istem ikisini de taşımıyordu ve araç
        # kök rehber nüans kontrolünü YAPAMADAN turu düşürdü.
        "## EK-A — ARAŞTIRMA BRIEF'İ",
        brief,
        "",
        "## EK-K — KÖK SEKTÖR REHBERİ",
        kok_rehberi,
        "",
        "## EK-L — ŞEMA ŞEKLİ (makineden üretilir)",
        _sema_sekli(),
        "",
        "## EK-M — İDDİA DİZİNİ (makineden üretilir)",
        _iddia_dizini(doktor_raporlari),
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
        # Saklı paket → SATIRIN sürümü (tasarım notu 2026-09-25 §3.9).
        surum = active_package["schema_version"]
    except (KeyError, TypeError) as hata:
        raise SynthesisFailed(
            "aktif paket `content` + `decision_log` + `schema_version` taşımak "
            "ZORUNDA — kimlik "
            f"taşıması bu çiftten türer: {hata}"
        ) from hata
    try:
        return identity.decision_units(dict(icerik), list(gunluk), schema_version=surum)
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


def _denemeyi_kos(runner: Runner, kok: Path, istem_yolu: Path) -> RunnerOutcome:
    """Denemeyi YALNIZ kendi istemini içeren temiz bir sahne kaynağıyla koşar.

    Kalıcı kök (`kok`) her denemenin istemini, çıktısını ve ham akışını
    biriktirir. Onu sahne kaynağı yapmak, düzeltme denemesine önceki denemenin
    reddedilen gövdesini ve akışını okunabilir kılıyordu — "belgeyi BAŞTAN
    yaz" talimatıyla çelişen, girdiyi denemeden denemeye BEYANSIZ değiştiren
    bir kanal (review 2026-09-22 M2). Her deneme artık ilk denemenin gördüğünü
    görür: tek dosya, kendi istemi. Dizin adı kökünkiyle aynıdır; ilk
    denemenin görünümü değişmez.

    İstem runner'a yine KANONİK yolundan verilir (runner onu STDIN'e okur);
    buradaki kopya yalnız modelin araçlarla görebileceği kümedir.
    """
    with tempfile.TemporaryDirectory(prefix="sentez-sahne-") as gecici:
        kaynak = Path(gecici).resolve() / kok.name
        kaynak.mkdir()
        shutil.copyfile(istem_yolu, kaynak / istem_yolu.name)
        return runner.run(SENTEZ_ARACI, kaynak, istem_yolu)


def _denemeyi_uret(
    runner: Runner,
    kok: Path,
    istem_yolu: Path,
    deneme: int,
    *,
    aktif_birimler: Mapping[str, Mapping],
    tur: AuditRound,
) -> tuple[dict, list[dict], list[str], str]:
    """Tek deneme: aracı koşar, kanıt dosyalarını yazar, çıktıyı çözer ve kimliğe bağlar.

    Model ya da araç kaynaklı her düşüş `SynthesisFailed` olarak yükselir (biçim
    düşüşü onun alt sınıfı `SynthesisOutputError`); hangisinin düzeltme hakkı
    kullandıracağına ÇAĞIRAN karar verir. Kimlik bağı (`_kimlik_bagla`) deneme
    İÇİNDEDİR, çünkü motorun bağ kapıları bağlanmış günlüğü okur (2026-09-23).
    """
    sonuc = _denemeyi_kos(runner, kok, istem_yolu)
    if sonuc.ham_akis is not None:
        # Ham olay akışı: gövdenin nasıl kurulduğunun KANITI. Durum
        # kontrolünden ÖNCE yazılır — yarıda kalan ya da başarı beyan
        # etmeyen akış tam da teşhis edilecek olandır (review 2026-09-22
        # M3). Yoksa dosya UYDURULMAZ — boş bir `.jsonl`, akışın olduğunu
        # ima ederdi.
        akis_adi = _cikti_dosya_adi(deneme).replace(
            "-SENTEZ-CIKTISI.md", "-SENTEZ-AKISI.jsonl"
        )
        with (kok / akis_adi).open("x", encoding="utf-8") as dosya:
            dosya.write(sonuc.ham_akis)
    if sonuc.durum != "tamam":
        # Araç arızası MODEL ÇIKTI HATASI DEĞİLDİR: tekrar sormak arızayı
        # gizler ve ikinci kez ödetir.
        raise SynthesisFailed(
            f"sentez aracı sonuç ÜRETMEDİ: durum={sonuc.durum!r}, "
            f"cikis={sonuc.exit_code!r}"
        )
    with (kok / _cikti_dosya_adi(deneme)).open("x", encoding="utf-8") as akis:
        akis.write(sonuc.stdout)

    # Çıktı dosyası ÖNCE yazılır: kesilmiş gövde de teşhis için diskte kalsın.
    _cikti_butcesini_dogrula(sonuc)
    aday, ham_gunluk, sorular, ozet = _cikti_bicimini_coz(sonuc.stdout)
    gunluk, sorular = _kimlik_bagla(aday, ham_gunluk, aktif_birimler, tur, sorular)
    return aday, gunluk, sorular, ozet


_BAG_SEBEBI_ACIKLAMASI: dict[str, str] = {
    "kanit-yok": "`kanit` alanı sözleşmenin kapalı biçimine uymuyor",
    "referans-yok": "`kanit`te çözülemeyen ya da hiç olmayan bir denetçi satırı atfı var",
    "referans-uyusmuyor": "`kanit`te gösterilen denetçi satırı BAŞKA bir alanı ya da dönemi anlatıyor",
    "kaynak-iddia-yok": "`kaynak_iddia` boş",
    "iddia-arastirmada-yok": "`kaynak_iddia` numarası EK-M dizininde yok",
    "iddia-alani-uyusmuyor": (
        "`kaynak_iddia` numarasının araştırma satırı BAŞKA bir alanı anlatıyor "
        "(EK-M'deki alan hücresine bak)"
    ),
    "donem-kimligi-cozulemedi": "`kaynak_iddia` numarasının dönemi sistem anahtarına çözülmüyor",
    "iddia-denetcide-yok": (
        "`kaynak_iddia` numarası `kanit`teki denetçi satırlarının iddia sütununda "
        "geçmiyor ya da atıf yapılan satırlardan biri hiçbir iddiayı taşımıyor"
    ),
}


def _bag_hatalari(gunluk: Sequence[Mapping], tur: AuditRound, doktor_raporlari) -> list:
    """Motorun `ekle` bağ kapıları — sentez turunda, düzeltme hakkı kullanılabilirken.

    Kural motorda TEK yerde yaşar (`engine.ekle_bagini_coz`). Motor bu modülü
    modül düzeyinde içe aktarır (`MEVZUAT_ALANLARI` · `SynthesisResult` ·
    `dogrulanmis_referanslar`); ters yön döngü kurardı, içe aktarma bu yüzden
    çağrı anındadır.
    """
    from app.services.sector_pipeline import engine

    return engine.ekle_bag_hatalari(
        gunluk, denetci_raporlari=tur.reports, doktor_raporlari=doktor_raporlari
    )


def _bag_hatasi_metni(hatalar: Sequence) -> str:
    """Düzeltme isteminin SOMUT hatası — kararı alanı, yolu ve atıflarıyla gösterir."""
    satirlar = [
        f"bağ kapısı (motorla AYNI kural): {len(hatalar)} `ekle` kararının atfı "
        "tutarsız; bu kararlar motorda UYGULANMAZ ve pakete girmez."
    ]
    for hata in hatalar:
        s = hata.satir
        satirlar.append(
            f"- alan `{s.get('alan')}`, öğe `{s.get('oge_yolu')}`, kanit "
            f"`{s.get('kanit')}`, kaynak_iddia `{s.get('kaynak_iddia')}`: "
            f"{_BAG_SEBEBI_ACIKLAMASI.get(hata.sebep, hata.sebep)}"
        )
    satirlar.append(
        "Her kararı EK-M dizinindeki DOĞRU numaraya ve o numarayı taşıyan, AYNI "
        "alanı anlatan denetçi satırına bağla. Doğru bağ kurulamıyorsa kalıbı aday "
        "paketten çıkar ve `reddedilen-aday` not satırı yaz."
    )
    return "\n".join(satirlar)


async def _kos(
    db,
    tur: AuditRound,
    *,
    run_id: str,
    brief: str,
    kok_rehberi: str,
    doktor_raporlari: Sequence[DoctorReport],
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
    # EK-M BOŞ OLAMAZ — fail-closed, ve arıza aracı DOĞURMADAN alınır.
    # Boş bir dizinle koşmak, kapatılan kusurun ta kendisine geri dönmektir:
    # sentez `kaynak_iddia` numarasını yine tahmin eder, tur yine ~940 sn ve
    # jeton harcar, motor yine `any(bağsız) → reddet` ile düşürür. Emsal EK-K:
    # rehber metni olmayan sektör turu BAŞLATMAZ, turdan sonra düşürmez.
    # Review 2026-09-22 H2: TOPLU dizin dolu olsa da iddia çözmeyen tek bir rapor
    # (eski sözleşme sürümü) tura girip denetçi/motor yolunda oy verebiliyordu.
    # Rapor BAŞINA ölçülür; karışık küme reddedilir, kaynak süzülmez.
    iddiasiz = iddiasiz_kaynaklar(doktor_raporlari)
    if iddiasiz:
        raise SynthesisFailed(
            f"iddia dizini EKSİK — Bölüm C iddiası çözmeyen kaynak(lar): "
            f"{list(iddiasiz)}; eski sözleşme sürümü ya da okunamayan tablo, "
            "karışık küme tura GİRMEZ (K-18: araştırma yeni şablonla yeniden "
            "üretilir). Tur BAŞLATILMAZ."
        )
    if not iddia_evreni(doktor_raporlari):
        raise SynthesisFailed(
            "iddia dizini BOŞ — mekanik eleme raporlarının hiçbiri Bölüm C "
            "iddiası taşımıyor; `kaynak_iddia` zorunlu bir alandır ve dizin "
            "olmadan yazılması TAHMİNDİR (ölçüldü: 52 `ekle` kararının 8'i "
            "tahmin yüzünden düştü). Tur BAŞLATILMAZ."
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
    istem = _istem_metni(
        gorev_metni,
        tur,
        active_package,
        removed_history,
        holiday_keys,
        brief=brief,
        kok_rehberi=kok_rehberi,
        doktor_raporlari=doktor_raporlari,
    )
    kok.mkdir(parents=True)

    # ── ÜRETİM + SINIRLI DÜZELTME ───────────────────────────────────────────
    # Koşu satırı bu döngü boyunca `calisiyor` KALIR: girdiler, denetçi
    # raporları, sözleşme ve görüntü sabittir; değişen tek şey modelin yazdığı
    # belgedir. Deneme sırası YENİ BİR KOŞU KİMLİĞİ DEĞİLDİR (K-83 ile
    # karıştırılmaz) — aynı sentez işleminin içindeki tekrar denemedir.
    suanki_istem = istem
    deneme = 0
    # Bağ düzeltmesi için açılan tur sonucu KÖTÜLEŞTİREMEZ (2026-09-23): bağ
    # hatası koşuyu öldürmez, motor o kararı uygulamaz. Düzeltme turu araç,
    # bütçe, biçim ya da kimlik kapısında düşerse ya da DAHA ÇOK bağ hatası
    # getirirse biçimi geçerli önceki deneme kullanılır.
    yedek: tuple | None = None
    while True:
        deneme += 1
        istem_adi = (
            GOREV_DOSYA_ADI if deneme == 1 else f"{deneme:02d}-SENTEZ-DUZELTME.md"
        )
        istem_yolu = kok / istem_adi
        with istem_yolu.open("x", encoding="utf-8") as akis:
            akis.write(suanki_istem)

        try:
            aday, gunluk, sorular, ozet = _denemeyi_uret(
                runner, kok, istem_yolu, deneme, aktif_birimler=aktif_birimler, tur=tur
            )
        except SynthesisFailed as hata:
            if yedek is not None:
                _LOG.warning(
                    "sentez: bağ düzeltmesi denemesi düştü (%s) — önceki deneme kullanılıyor",
                    hata,
                )
                aday, gunluk, sorular, ozet, bag_hatalari = yedek
                break
            if not isinstance(hata, SynthesisOutputError) or deneme > SENTEZ_DUZELTME_HAKKI:
                raise
            suanki_istem = _duzeltme_istemi(istem, hata, deneme)
            continue

        bag_hatalari = _bag_hatalari(gunluk, tur, doktor_raporlari)
        if yedek is not None and len(yedek[4]) < len(bag_hatalari):
            aday, gunluk, sorular, ozet, bag_hatalari = yedek
        if not bag_hatalari or deneme > SENTEZ_DUZELTME_HAKKI:
            break
        yedek = (aday, gunluk, sorular, ozet, bag_hatalari)
        suanki_istem = _duzeltme_istemi(
            istem, SynthesisOutputError(_bag_hatasi_metni(bag_hatalari)), deneme
        )
    if bag_hatalari:
        _LOG.warning(
            "sentez: %d `ekle` kararı bağ kapısını geçemedi — motor uygulamayacak",
            len(bag_hatalari),
        )

    # Plan 1 yazım kapısı YENİDEN KULLANILIR. İki dış girdisinden marka adları
    # çağırandan değil VERİTABANINDAN okunur (R8 doktrini): çağıran boş liste
    # verirse K-15 sessizce kapanırdı.
    marka_satirlari = await db.fetch(
        "SELECT name FROM social.brands WHERE name IS NOT NULL"
    )
    dogrulama = validate_package_content(
        aday,
        schema_version=CURRENT_SCHEMA_VERSION,
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
    brief: str,
    kok_rehberi: str,
    doktor_raporlari: Sequence[DoctorReport],
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
            brief=brief,
            kok_rehberi=kok_rehberi,
            doktor_raporlari=doktor_raporlari,
            active_package=active_package,
            removed_history=removed_history,
            holiday_keys=holiday_keys,
            runner=runner,
            dest=dest,
        )
    except SynthesisFailed as ariza:
        try:
            await runs.mark_incomplete(
                db, run_id=run_id, asama=SENTEZ_ASAMASI, sebep=str(ariza)
            )
        except runs.RunAlreadyTerminal:
            # Review 2026-09-22 M1: terminal satır EZİLMEZ; işaret düşerse ÖZGÜN
            # arıza yine çağırana ulaşır (`raise` bu kolda hiç atlanmaz).
            _LOG.warning(
                "sentez arızası terminal koşuya işlenemedi, satır korunur: "
                "run_id=%s",
                run_id,
                exc_info=True,
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
