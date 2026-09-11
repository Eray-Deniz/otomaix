"""Politika motorunun VERİ SÖZLEŞMESİ — yalnız kapalı kümeler ve tip tanımları.

**Neden ayrı bir modül (arayüz eki R2/H2 + R9).** `runs.record_result` (Task 8)
`EngineResult`'ı TÜKETİR, ama `decide` Task 13'te doğar ve R9 bir görevin SONRAKİ
görevde doğan yüzeyi tüketmesini YASAKLAR. Bu yüzden motor sözleşmesinin **veri
tipleri** (mantığı DEĞİL) burada, Task 8'de doğar.

Bu dosyada FONKSİYON YOKTUR, VERİTABANI YOKTUR ve import yönü tek yönlüdür:
`engine.py` buradan okur, burası `engine.py`'yi GÖRMEZ.

`ENGINE_VERSION` ve `config_sha` burada TANIMLANMAZ — ikisi de Task 13'ün
kalemidir (`engine.py` · `policy_config.py`). Burada tanımlansalardı motor
mantığının bir parçası veri sözleşmesine sızardı.
"""

from __future__ import annotations

from dataclasses import dataclass, fields as dataclass_fields
from typing import Any, Mapping, Sequence

from app.services.sector_pipeline import identity

# ─── Kapalı değer kümeleri ──────────────────────────────────────────────────

SONUCLAR: tuple[str, ...] = ("activation_eligible", "no_change", "blocked")
"""Koşu sonucu — KAPALI (K-90 birleştirmesi; dördüncü değer YOKTUR)."""

BULGU_SINIFLARI: tuple[str, ...] = (
    "kapsam_ihlali",
    "mevzuat_uyusmazligi",
    "mevzuat_dogrulanamadi",
    "regresyon_kapisi",
    "ikinci_aktif",
    "acik_soru",
)
"""`run_checks`'in üretebileceği bulgu sınıfları — KAPALI, ALTI değer (R7).

Task 12 bu kümeyi IMPORT eder ve DEĞERLERİNİ üretir; Task 13 `BulguIzi.sinif`
alanında ve dönüşüm tablosunda TÜKETİR. Tanımın burada olmasının sebebi R2/H2'de
yazılıdır: `PolicyReport` Task 8'in `record_result`'ında imza tipidir.
"""

UYGULANMAMA_SEBEPLERI: tuple[str, ...] = (
    "kanit-yok",  # spec girdisi satır 1189: kanıt yoksa karar uygulanmaz
    "mutabakat-yok",  # K-125: iki denetçi uyuşmuyor
    "referans-yok",  # sentez sözleşmesi 2.1: `ekle` en az bir D# referansı ister
    "referans-uyusmuyor",  # atıf BAŞKA bir alanın satırını gösteriyor
    "oneri-olumsuz",  # denetçi o satırda `alma`/`açık-soru` önermiş
    "celiski",  # denetçi satırı `çelişki` sınıfında — sayı yetse de girmez
    "cogunluk-yok",  # yeni öğe 2-3 yapısal çoğunluk kuralı
)
"""Aday kararın uygulanmama sebepleri — KAPALI, YEDİ değer. UYDURULMUŞ değer YOK.

**Sıra ÖNCELİKTİR** (`engine._reddedilenler`): bir birim birden çok sebeple
reddedilebilir ve rapora yazılan sebep bu sıradan seçilir. `referans-yok` ·
`referans-uyusmuyor` · `oneri-olumsuz` · `celiski`, `cogunluk-yok`'tan ÖNCE
gelir — hepsinde sayı ya hiç okunamamıştır ya da okunması anlamsızdır;
"çoğunluk yok" demek okunmuş bir sayı ima ederdi.
"""


# ─── Rapor öğeleri ──────────────────────────────────────────────────────────


def _metin_alani(deger: Any, etiket: str, *, bos_serbest: bool = False) -> None:
    """Metin alanının TİPİNİ zorlar — anotasyon bunu yapmaz.

    `bool` da dâhil doğru-görünen hiçbir değer kabul edilmez (`type(...) is not
    str`, alt sınıf da RED — A4 disiplini).
    """
    if type(deger) is not str:
        raise TypeError(
            f"{etiket} metin olmalı — {type(deger).__name__} verildi "
            "(doğru-görünen değer sözleşme kanıtı DEĞİLDİR)"
        )
    if not bos_serbest and not deger.strip():
        raise ValueError(f"{etiket} boş olamaz")


@dataclass(frozen=True)
class KararsizMadde:
    """K-23=B — motorun karar veremediği birim. Aktivasyonu BLOKLAMAZ."""

    unit_id: str
    sebep: str  # serbest metin; kapalı küme DEĞİL (dürüst etiket)

    def __post_init__(self) -> None:
        # Anotasyon çalışma zamanı kapısı DEĞİLDİR (hakem turu 3, yüksek):
        # `{"unit_id": 7, "sebep": []}` biçiminde bir öğe kalıcı yükten geri
        # okunduğunda "geçerli rapor" sayılıyordu. Kapı DEĞİŞMEZE kondu ki her
        # kurulum yolu — motor da, tipli okuyucu da — aynı gramerden geçsin.
        _metin_alani(self.unit_id, "KararsizMadde.unit_id")
        _metin_alani(self.sebep, "KararsizMadde.sebep")


@dataclass(frozen=True)
class BulguIzi:
    """`run_checks`'in ürettiği bulgunun kalıcı izi."""

    sinif: str  # BULGU_SINIFLARI içinden — KAPALI KÜME (R7, altı değer)
    unit_id: str | None  # birime bağlanamayan bulguda None
    detay: str  # bulguyu doğuran ölçümün tek cümlelik ifadesi
    kontrol: str = ""
    """Bulguyu ÜRETEN kontrolün adı (`EngineCheck.ad`) — TEK yazıcısı `run_checks`.

    `sinif` riskli sınıfları ayırt ETMEZ: `acik_soru` sınıfını BEŞ ayrı kontrol
    üretir. Onay yüzeyi (Task 14, K-42) sıralamayı sınıf ADIYLA kurar; bunu
    `detay` metnini eşleştirerek çözmek referans bütünlüğü olmayan bir bağ
    olurdu (İlke 1). Varsayılan boştur çünkü değeri kontrol gövdesi DEĞİL
    toplayıcı yazar; gövdenin yazdığı bir değer `run_checks` tarafından
    REDDEDİLİR (uydurma atıf = sessiz sınıf kayması).
    """

    def __post_init__(self) -> None:
        if self.unit_id is not None:
            _metin_alani(self.unit_id, "BulguIzi.unit_id")
        _metin_alani(self.detay, "BulguIzi.detay")
        _metin_alani(self.kontrol, "BulguIzi.kontrol", bos_serbest=True)
        if self.sinif not in BULGU_SINIFLARI:
            raise ValueError(
                f"BulguIzi.sinif kapalı kümenin dışında: {self.sinif!r} — "
                f"kabul edilenler: {list(BULGU_SINIFLARI)}"
            )


@dataclass(frozen=True)
class UygulanmayanKarar:
    """Aday karar KANITSIZ/MUTABAKATSIZ olduğu için uygulanmadı, kalıp KORUNDU."""

    unit_id: str
    karar: str  # identity.KARAR_DEGERLERI içinden — KAPALI (Task 3)
    sebep: str  # UYGULANMAMA_SEBEPLERI içinden — KAPALI

    def __post_init__(self) -> None:
        _metin_alani(self.unit_id, "UygulanmayanKarar.unit_id")
        if self.karar not in identity.KARAR_DEGERLERI:
            raise ValueError(
                f"UygulanmayanKarar.karar kapalı kümenin dışında: {self.karar!r}"
            )
        if self.sebep not in UYGULANMAMA_SEBEPLERI:
            raise ValueError(
                f"UygulanmayanKarar.sebep kapalı kümenin dışında: {self.sebep!r} — "
                f"kabul edilenler: {list(UYGULANMAMA_SEBEPLERI)}"
            )


@dataclass(frozen=True)
class PolicyReport:
    """K-95 politika raporu — koşu satırının `policy_report` kolonuna yazılan tip.

    **TEK ÜRETİCİSİ `engine.decide`'dır** (Task 13). Başka hiçbir modül bu sınıfı
    KURMAZ; serbest sözlükten üretilen bir politika raporu yolu YOKTUR.

    Dört alanın dördü de ZORUNLUDUR; boş rapor `PolicyReport((), (), (), ())`
    biçiminde **boş demetlerle** ifade edilir, `None` ile DEĞİL.
    """

    kararsizlar: tuple[KararsizMadde, ...]
    bulgular: tuple[BulguIzi, ...]
    uygulanmayan_kararlar: tuple[UygulanmayanKarar, ...]
    acik_soru_kimlikleri: tuple[str, ...]

    _OGE_TIPLERI = {  # KAPALI eşleme — dört alan, beşincisi YOK
        "kararsizlar": KararsizMadde,
        "bulgular": BulguIzi,
        "uygulanmayan_kararlar": UygulanmayanKarar,
        "acik_soru_kimlikleri": str,
    }

    def __post_init__(self) -> None:
        """A3 (arayüz eki R6(e)) — DEMET ANOTASYONU ZORLAMA DEĞİLDİR.

        `tuple[...]` bir ANOTASYONDUR; çağıran liste verirse alan LİSTE olur ve
        çağıranla takma ad PAYLAŞILIR. `identity.donmus` burada KULLANILAMAZ:
        `donmus`'un dönüşüm kümesi kapalıdır ve donmuş dataclass o kümenin
        DIŞINDADIR (kural 5 → `TypeError`). Bu yüzden kural `tuple(...)` KOPYASI
        + ÖĞE TİPİ kontrolüdür.
        """
        for _alan, _tip in PolicyReport._OGE_TIPLERI.items():
            _deger = tuple(getattr(self, _alan))  # KOPYA — takma ad kapanır
            for _oge in _deger:
                if type(_oge) is not _tip:
                    raise TypeError(
                        f"PolicyReport.{_alan} yalnız {_tip.__name__} taşır "
                        f"({type(_oge).__name__} verildi) — benzeyen nesne kabul edilmez"
                    )
            object.__setattr__(self, _alan, _deger)

    def as_payload(self) -> dict[str, Any]:
        """Koşu satırının `policy_report` kolonuna yazılan JSON temsili.

        Kolon `jsonb`'dir; dataclass demetleri kendiliğinden serileşmez. Temsil
        BURADA doğar ki `record_result` kendi çevirisini yazmasın (iki çeviri iki
        biçim demektir).
        """
        return {
            "kararsizlar": [
                {"unit_id": k.unit_id, "sebep": k.sebep} for k in self.kararsizlar
            ],
            "bulgular": [
                {
                    "sinif": b.sinif,
                    "unit_id": b.unit_id,
                    "detay": b.detay,
                    "kontrol": b.kontrol,
                }
                for b in self.bulgular
            ],
            "uygulanmayan_kararlar": [
                {"unit_id": u.unit_id, "karar": u.karar, "sebep": u.sebep}
                for u in self.uygulanmayan_kararlar
            ],
            "acik_soru_kimlikleri": list(self.acik_soru_kimlikleri),
        }

    @classmethod
    def from_payload(cls, payload: Any) -> "PolicyReport":
        """Kalıcı yükü TİPLİ olarak geri okur; sözleşmeye uymayan yük REDDEDİLİR.

        **Bu bir ÜRETİM yolu değildir, bir OKUYUCUdur** (H2 korunur): yalnız
        `as_payload`'ın ürettiği biçimi kabul eder ve her öğeyi kendi
        dataclass'ına kurarak sınıfların kapalı kümelerini yeniden uygular.

        **Neden var (hakem turu 2, yüksek).** Kalıcı raporu HAM sözlük olarak
        okuyan tüketiciler (hazırlık listesi, Task 17) alan VARLIĞINI şekil
        kanıtı sanıyordu: `{"kararsizlar": 1, "bulgular": [{}],
        "uygulanmayan_kararlar": None, "acik_soru_kimlikleri": []}` biçiminde
        bir yük "motor kontrolleri tamam + bulgu yok" diye okunabiliyordu.
        Tüketicinin kendi doğrulama listesini yazması ikinci bir sözleşme
        demekti; sözleşme zaten yapısaldır, eksik olan TİPLİ OKUYUCUYDU.

        Uymayan yükte `ValueError` / `TypeError` yükselir — sessiz boş rapora
        düşülmez.
        """
        if not isinstance(payload, Mapping):
            raise TypeError("politika raporu yükü eşleme olmalı")
        beklenen = {
            "kararsizlar",
            "bulgular",
            "uygulanmayan_kararlar",
            "acik_soru_kimlikleri",
        }
        if set(payload) != beklenen:
            raise ValueError(
                f"politika raporu yükünün anahtar kümesi sözleşmeye uymuyor: "
                f"{sorted(payload)} — beklenen {sorted(beklenen)}"
            )

        def _oge_listesi(ad: str) -> list[Mapping]:
            deger = payload[ad]
            if not isinstance(deger, Sequence) or isinstance(deger, (str, bytes)):
                raise TypeError(f"{ad} dizi olmalı")
            if any(not isinstance(oge, Mapping) for oge in deger):
                raise TypeError(f"{ad} öğeleri eşleme olmalı")
            return list(deger)

        def _kur(tip, oge: Mapping, alanlar: tuple[str, ...]):
            if set(oge) != set(alanlar):
                raise ValueError(
                    f"{tip.__name__} öğesinin alan kümesi sözleşmeye uymuyor: "
                    f"{sorted(oge)} — beklenen {sorted(alanlar)}"
                )
            return tip(**oge)

        acik = payload["acik_soru_kimlikleri"]
        if not isinstance(acik, Sequence) or isinstance(acik, (str, bytes)):
            raise TypeError("acik_soru_kimlikleri dizi olmalı")
        if any(type(kimlik) is not str for kimlik in acik):
            raise TypeError("acik_soru_kimlikleri öğeleri metin olmalı")

        return cls(
            kararsizlar=tuple(
                _kur(KararsizMadde, oge, ("unit_id", "sebep"))
                for oge in _oge_listesi("kararsizlar")
            ),
            bulgular=tuple(
                _kur(BulguIzi, oge, ("sinif", "unit_id", "detay", "kontrol"))
                for oge in _oge_listesi("bulgular")
            ),
            uygulanmayan_kararlar=tuple(
                _kur(UygulanmayanKarar, oge, ("unit_id", "karar", "sebep"))
                for oge in _oge_listesi("uygulanmayan_kararlar")
            ),
            acik_soru_kimlikleri=tuple(acik),
        )


@dataclass(frozen=True)
class EngineResult:
    """Motorun TEK çıktı nesnesi — `record_result`'ın TEK motor-türevi girdisi.

    Alan kümesi KAPALIDIR (on bir alan) ve koşu satırının on bir motor-türevi
    kolonuyla BİREBİR eşleşir. `kararsizlar` alanı YOKTUR: tek yeri
    `policy_report.kararsizlar`'dır (iki kaynak yasağı, R2).
    """

    sonuc: str  # SONUCLAR — KAPALI
    sebep: str | None
    final_candidate: Mapping | None
    final_decision_log: tuple[Mapping, ...] | None
    engine_diff: Mapping
    policy_report: PolicyReport
    barrier_report: Mapping
    content_sha: str | None
    decision_log_sha: str | None
    engine_version: str
    engine_config_sha: str

    def __post_init__(self) -> None:
        if self.sonuc not in SONUCLAR:
            raise ValueError(
                f"EngineResult.sonuc kapalı kümenin dışında: {self.sonuc!r} — "
                f"kabul edilenler: {list(SONUCLAR)}"
            )
        # A1: DÖRT yük alanı `identity.donmus`'tan geçirilir. `content_sha`
        # `final_candidate`'in, `decision_log_sha` `final_decision_log`'un
        # KİMLİĞİDİR; yapımdan sonra yükü değiştirmek, hash'i satıra yazılmış
        # ama içeriği başka olan bir sonuç nesnesi üretirdi.
        for _alan in (
            "final_candidate",
            "final_decision_log",
            "engine_diff",
            "barrier_report",
        ):
            object.__setattr__(self, _alan, identity.donmus(getattr(self, _alan)))
        # A3: `policy_report` bu döngüye GİRMEZ ve girmesi HATA olurdu —
        # `donmus` donmuş dataclass'ı reddeder (kural 5).
        if type(self.policy_report) is not PolicyReport:
            raise TypeError(
                "policy_report PolicyReport olmalı — serbest sözlük KABUL EDİLMEZ"
            )


ENGINE_RESULT_ALANLARI: tuple[str, ...] = tuple(
    alan.name for alan in dataclass_fields(EngineResult)
)
"""`EngineResult`'ın ÜRETİLMİŞ alan listesi — elle sayılmaz.

`record_result`'ın eşleme tablosu bu listeye karşı sınanır: motor sözleşmesine
bir alan eklenip koşu satırına yazılmazsa alan-kümesi testi düşer (R2'nin
sessiz-düşme kapısı).
"""
