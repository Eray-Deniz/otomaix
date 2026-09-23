"""Operatör kararları — açık soruların kapanış yolu (Eray, 2026-09-23).

**Neden var (ölçüldü).** Motor sentezin her açık sorusunda koşuyu `blocked` yapar
(K-71) ama cevabı geri alan bir yol yoktu: `blocked` koşu taslak yazmaz, düzeltme
turu ise yalnız reddedilmiş taslaktan açılır. `kosu-23e19d03` koşusunu durduran
TEK sebep 11 açık soruydu (yazmadan oynatma, 2026-09-23).

**Ne yapar.** Operatörün karar dosyası her açık soruyu TAM BİR KEZ cevaplar ve
isteğe bağlı olarak pakete işlem uygular (`ekle` · `degistir` · `cikar`). Bu
modül motorun sonucunu ALIR, işlemleri nihai içeriğe ve karar günlüğüne
uygular, sonra paketin bütün yapısal kapılarını YENİDEN koşar: şema · karar
günlüğü şeması · birim bütünlüğü · tüketilmemiş bayrak · takvim anahtarı. Bir
kapı düşerse hiçbir şey üretilmez (`OperatorKarariReddedildi`).

**Karar (Eray, 2026-09-23): kaynaksız ekleme SERBESTTİR, etiketlidir.** Operatör
işlemi karar günlüğüne `aktor="insan"` satırıyla yazılır ve gerekçesi
`operatör kararı (<soru>)` ile başlar. Metni K-129 okumasıyla risk sınıfına
düşen işlem `hukuki: true` taşır; onay özeti onu ayrıca işaretler.

**Sınır — bilinçli.** Motorun açık soru DIŞINDA bir engeli varsa (bariyer,
yazım hatası, değişiklik yok …) operatör kararı YAZILMAZ: bu yol yalnız soruları
kapatır, motorun başka bir kapısını aşmaz.

**PolicyReport istisnası.** `PolicyReport`'un tek üreticisi `engine.decide`'dır;
bu modül raporu KURMAZ, yalnız cevaplanan soru kimliklerini `dataclasses.replace`
ile düşürür. Bulgular, kararsızlar ve uygulanmayan kararlar olduğu gibi kalır.
"""

from __future__ import annotations

import dataclasses
from typing import Any, Callable, Mapping, Sequence

from app.services.sector_content_schema import (
    CTA_ITEM_KEYS,
    LIST_FIELDS,
    SPECIAL_DAY_SLOTS,
    TEXT_FIELDS,
    VIDEO_POOL_KEYS,
    structural_errors,
)
from app.services.sector_pipeline import engine, identity
from app.services.sector_pipeline.engine_contract import EngineResult

ACIK_SORU_SEBEBI = "acik-soru-var"
ISLEMLER = frozenset({"ekle", "degistir", "cikar"})
SENTEZ_SORU_ONEKI = "S"
GEREKCE_ONEKI = "operatör kararı"
KAYNAKSIZ_KANIT = "operatör eklemesi — araştırma kaynağı yok"


class OperatorKarariReddedildi(ValueError):
    """Karar dosyası ya da uygulanmış sonuç kapılardan geçmedi."""


# ─── Soru kimlikleri ─────────────────────────────────────────────────────────


def soru_kimlikleri(
    acik_soru_kimlikleri: Sequence[str], sentez_sorulari: Sequence[str]
) -> dict[str, str]:
    """Açık soru → operatörün kullanacağı kısa kimlik.

    Motor biriminin sorusu kendi `unit_id`'siyle, sentezin sorusu `S<sıra>`
    ile (1'den başlar, sentez çıktısındaki sıra) adlandırılır. Sentez sorusu
    serbest metindir; kısa kimlik onu dosyada tekrar yazmayı gerektirmez.
    """
    sentez_sira = {soru: f"{SENTEZ_SORU_ONEKI}{i}" for i, soru in enumerate(sentez_sorulari, 1)}
    kimlikler: dict[str, str] = {}
    for soru in acik_soru_kimlikleri:
        kimlikler[soru] = sentez_sira.get(soru, soru)
    return kimlikler


# ─── İçerik modeli ───────────────────────────────────────────────────────────


@dataclasses.dataclass
class _Oge:
    unit_id: str
    deger: Any


class _Model:
    """Nihai içeriğin birim kimlikli, düzenlenebilir görünümü.

    Liste öğesi silinince ardındakilerin sıra ordinali kayar; yolları bu model
    içerikten YENİDEN türetir, elle kaydırma yapılmaz.
    """

    def __init__(self, icerik: Mapping, yol_kimlik: Mapping[str, str]) -> None:
        self.sira = list(icerik)
        self.metin: dict[str, _Oge] = {}
        self.liste: dict[str, list[_Oge]] = {}
        self.video: dict[str, list[_Oge]] = {}
        self.ozel: dict[str, dict[str, _Oge]] = {}
        for ad in TEXT_FIELDS:
            if ad in icerik:
                self.metin[ad] = _Oge(yol_kimlik[ad], icerik[ad])
        for ad in LIST_FIELDS:
            if ad in icerik:
                self.liste[ad] = [
                    _Oge(yol_kimlik[f"{ad}[{i}]"], oge) for i, oge in enumerate(icerik[ad])
                ]
        if "video_kodlar" in icerik:
            for havuz in VIDEO_POOL_KEYS:
                self.video[havuz] = [
                    _Oge(yol_kimlik[f"video_kodlar/{havuz}[{i}]"], oge)
                    for i, oge in enumerate(icerik["video_kodlar"][havuz])
                ]
        if "ozel_gun" in icerik:
            for anahtar, girdi in icerik["ozel_gun"].items():
                self.ozel[anahtar] = {
                    yuva: _Oge(yol_kimlik[f"ozel_gun/{anahtar}/{yuva}"], girdi[yuva])
                    for yuva in SPECIAL_DAY_SLOTS
                }

    def icerik(self) -> dict:
        cikti: dict[str, Any] = {}
        for ad in self.sira + [a for a in ("ozel_gun",) if a not in self.sira and self.ozel]:
            if ad in self.metin:
                cikti[ad] = self.metin[ad].deger
            elif ad in self.liste:
                cikti[ad] = [o.deger for o in self.liste[ad]]
            elif ad == "video_kodlar":
                cikti[ad] = {h: [o.deger for o in self.video[h]] for h in VIDEO_POOL_KEYS}
            elif ad == "ozel_gun":
                cikti[ad] = {
                    k: {y: girdi[y].deger for y in SPECIAL_DAY_SLOTS}
                    for k, girdi in self.ozel.items()
                }
        return cikti

    def bul(self, unit_id: str) -> tuple[str, Any]:
        """Birimin (alan, konum) bilgisi; yoksa `KeyError`."""
        for ad, oge in self.metin.items():
            if oge.unit_id == unit_id:
                return ad, ("metin", ad)
        for ad, ogeler in self.liste.items():
            for oge in ogeler:
                if oge.unit_id == unit_id:
                    return ad, ("liste", ad)
        for havuz, ogeler in self.video.items():
            for oge in ogeler:
                if oge.unit_id == unit_id:
                    return "video_kodlar", ("video", havuz)
        for anahtar, girdi in self.ozel.items():
            for yuva, oge in girdi.items():
                if oge.unit_id == unit_id:
                    return "ozel_gun", ("ozel", anahtar, yuva)
        raise KeyError(unit_id)

    def oge(self, unit_id: str) -> _Oge:
        _alan, konum = self.bul(unit_id)
        if konum[0] == "metin":
            return self.metin[konum[1]]
        if konum[0] == "liste":
            return next(o for o in self.liste[konum[1]] if o.unit_id == unit_id)
        if konum[0] == "video":
            return next(o for o in self.video[konum[1]] if o.unit_id == unit_id)
        return self.ozel[konum[1]][konum[2]]


# ─── Karar dosyası doğrulaması ───────────────────────────────────────────────


def _dosya_kararlari(dosya: Any) -> list[Mapping]:
    if not isinstance(dosya, Mapping) or set(dosya) != {"kararlar"}:
        raise OperatorKarariReddedildi(
            "karar dosyası tam olarak {'kararlar': [...]} biçiminde olmalı"
        )
    kararlar = dosya["kararlar"]
    if not isinstance(kararlar, list) or not kararlar:
        raise OperatorKarariReddedildi("'kararlar' boş olmayan bir dizi olmalı")
    for i, karar in enumerate(kararlar):
        if not isinstance(karar, Mapping):
            raise OperatorKarariReddedildi(f"kararlar[{i}] nesne değil")
        fazla = set(karar) - {"soru", "soru_basi", "cevap", "islemler"}
        if fazla or not {"soru", "cevap"} <= set(karar):
            raise OperatorKarariReddedildi(
                f"kararlar[{i}] alanları {{soru, soru_basi?, cevap, islemler?}} olmalı"
            )
        if not isinstance(karar["cevap"], str) or not karar["cevap"].strip():
            raise OperatorKarariReddedildi(f"kararlar[{i}].cevap boş")
        if not isinstance(karar.get("islemler", []), list):
            raise OperatorKarariReddedildi(f"kararlar[{i}].islemler dizi değil")
    return list(kararlar)


def _kapsam_kapisi(kararlar: list[Mapping], kimlikler: Mapping[str, str]) -> None:
    """Her açık soru TAM BİR KEZ cevaplanır; tanınmayan soru kabul edilmez."""
    kisa_to_soru = {kisa: soru for soru, kisa in kimlikler.items()}
    gorulen: dict[str, int] = {}
    for karar in kararlar:
        kisa = karar["soru"]
        if kisa not in kisa_to_soru:
            raise OperatorKarariReddedildi(
                f"tanınmayan soru: {kisa!r} — açık sorular: {sorted(kisa_to_soru)}"
            )
        gorulen[kisa] = gorulen.get(kisa, 0) + 1
        basi = karar.get("soru_basi")
        if basi is not None and not kisa_to_soru[kisa].startswith(basi):
            raise OperatorKarariReddedildi(
                f"{kisa}: soru_basi sorunun metniyle eşleşmiyor — yanlış soruya "
                f"cevap yazılmış olabilir ({basi!r})"
            )
    cift = sorted(k for k, n in gorulen.items() if n > 1)
    if cift:
        raise OperatorKarariReddedildi(f"birden fazla kez cevaplanan soru: {cift}")
    eksik = sorted(set(kisa_to_soru) - set(gorulen))
    if eksik:
        raise OperatorKarariReddedildi(
            f"cevaplanmayan açık soru: {eksik} — her açık soru cevaplanmadan koşu "
            "ilerleyemez (K-71)"
        )


# ─── İşlemler ────────────────────────────────────────────────────────────────


def _gerekce(soru: str, cevap: str) -> str:
    return f"{GEREKCE_ONEKI} ({soru}): {cevap.strip()}"


def _deger_kapisi(alan: str, deger: Any, etiket: str) -> None:
    if alan == "cta_kaliplari":
        if not isinstance(deger, Mapping) or set(deger) != CTA_ITEM_KEYS:
            raise OperatorKarariReddedildi(
                f"{etiket}: CTA öğesi tam olarak {sorted(CTA_ITEM_KEYS)} anahtarlarını taşır"
            )
    elif not isinstance(deger, str):
        raise OperatorKarariReddedildi(f"{etiket}: {alan} öğesi metin olmalı")


def _uygula_islem(
    model: _Model,
    satirlar: dict[str, dict],
    yeni_satirlar: list[dict],
    islem: Mapping,
    *,
    soru: str,
    cevap: str,
    takvim: frozenset[str],
    yeni_kimlik: Callable[[], str],
) -> list[dict]:
    """Tek işlemi uygular; işlem kaydını (etkilenen birimler) döner."""
    etiket = f"{soru}/{islem.get('islem')}"
    tur = islem.get("islem")
    if tur not in ISLEMLER:
        raise OperatorKarariReddedildi(f"{etiket}: işlem {sorted(ISLEMLER)} dışında")
    gerekce = _gerekce(soru, cevap)

    def _yeni_satir(alan: str) -> tuple[str, dict]:
        kimlik = yeni_kimlik()
        satir = {
            "tur": "karar",
            "karar": "ekle",
            "alan": alan,
            "oge_yolu": "",  # yeniden türetilir
            "unit_id": kimlik,
            "oge_sha": "",  # yeniden türetilir
            "gerekce": gerekce,
            "kanit": KAYNAKSIZ_KANIT,
            "aktor": "insan",
        }
        yeni_satirlar.append(satir)
        satirlar[kimlik] = satir
        return kimlik, satir

    if tur == "ekle":
        alan = islem.get("alan")
        if alan in LIST_FIELDS:
            _alanlar_kapisi(islem, {"islem", "alan", "deger"}, etiket)
            _deger_kapisi(alan, islem["deger"], etiket)
            if alan not in model.liste:
                raise OperatorKarariReddedildi(f"{etiket}: içerikte {alan} yok")
            kimlik, _ = _yeni_satir(alan)
            model.liste[alan].append(_Oge(kimlik, islem["deger"]))
            return [{"islem": "ekle", "alan": alan, "unit_id": kimlik, "deger": islem["deger"]}]
        if alan == "video_kodlar":
            _alanlar_kapisi(islem, {"islem", "alan", "havuz", "deger"}, etiket)
            if islem["havuz"] not in model.video:
                raise OperatorKarariReddedildi(
                    f"{etiket}: havuz {list(VIDEO_POOL_KEYS)} dışında"
                )
            _deger_kapisi(alan, islem["deger"], etiket)
            kimlik, _ = _yeni_satir(alan)
            model.video[islem["havuz"]].append(_Oge(kimlik, islem["deger"]))
            return [{"islem": "ekle", "alan": alan, "unit_id": kimlik, "deger": islem["deger"]}]
        if alan == "ozel_gun":
            _alanlar_kapisi(islem, {"islem", "alan", "anahtar", "deger"}, etiket)
            anahtar, girdi = islem["anahtar"], islem["deger"]
            if anahtar not in takvim:
                raise OperatorKarariReddedildi(
                    f"{etiket}: {anahtar!r} sistem takviminde yok — takvimde olmayan "
                    "dönem pakete giremez"
                )
            if anahtar in model.ozel:
                raise OperatorKarariReddedildi(
                    f"{etiket}: {anahtar!r} pakette zaten var — yuvaları `degistir` ile değiştir"
                )
            if not isinstance(girdi, Mapping) or set(girdi) != set(SPECIAL_DAY_SLOTS):
                raise OperatorKarariReddedildi(
                    f"{etiket}: özel gün girdisi tam olarak {list(SPECIAL_DAY_SLOTS)} yuvalarını taşır"
                )
            kayit = []
            model.ozel[anahtar] = {}
            for yuva in SPECIAL_DAY_SLOTS:
                _deger_kapisi("ozel_gun", girdi[yuva], f"{etiket}.{yuva}")
                kimlik, _ = _yeni_satir("ozel_gun")
                model.ozel[anahtar][yuva] = _Oge(kimlik, girdi[yuva])
                kayit.append(
                    {"islem": "ekle", "alan": "ozel_gun", "unit_id": kimlik, "deger": girdi[yuva]}
                )
            return kayit
        raise OperatorKarariReddedildi(
            f"{etiket}: eklenebilen alanlar {list(LIST_FIELDS)} · video_kodlar · ozel_gun"
            " (düz metin alanı `degistir` ile değişir)"
        )

    if tur == "degistir":
        _alanlar_kapisi(islem, {"islem", "unit_id", "deger"}, etiket)
        kimlik = islem["unit_id"]
        try:
            alan, _konum = model.bul(kimlik)
        except KeyError:
            raise OperatorKarariReddedildi(f"{etiket}: {kimlik!r} pakette yok") from None
        _deger_kapisi(alan, islem["deger"], etiket)
        model.oge(kimlik).deger = islem["deger"]
        eski = satirlar[kimlik]
        yeni = {k: v for k, v in eski.items() if k not in identity.KURAL_DAMGA_ALANLARI}
        if yeni["karar"] == "koru":
            yeni["karar"] = "guncelle"
            yeni.pop("kapsam", None)
        yeni.update(aktor="insan", gerekce=gerekce)
        satirlar[kimlik] = yeni
        return [{"islem": "degistir", "alan": alan, "unit_id": kimlik, "deger": islem["deger"]}]

    # cikar
    if islem.get("alan") == "ozel_gun":
        _alanlar_kapisi(islem, {"islem", "alan", "anahtar"}, etiket)
        anahtar = islem["anahtar"]
        if anahtar not in model.ozel:
            raise OperatorKarariReddedildi(f"{etiket}: {anahtar!r} pakette yok")
        kimlikler = [oge.unit_id for oge in model.ozel.pop(anahtar).values()]
    else:
        _alanlar_kapisi(islem, {"islem", "unit_id"}, etiket)
        kimlik = islem["unit_id"]
        try:
            _alan, konum = model.bul(kimlik)
        except KeyError:
            raise OperatorKarariReddedildi(f"{etiket}: {kimlik!r} pakette yok") from None
        if konum[0] == "metin":
            raise OperatorKarariReddedildi(
                f"{etiket}: düz metin alanı çıkarılamaz — `degistir` kullan"
            )
        if konum[0] == "ozel":
            raise OperatorKarariReddedildi(
                f"{etiket}: özel gün yuvası tek başına çıkarılamaz — dönemi "
                "{'islem': 'cikar', 'alan': 'ozel_gun', 'anahtar': ...} ile çıkar"
            )
        havuz = model.liste[konum[1]] if konum[0] == "liste" else model.video[konum[1]]
        havuz[:] = [o for o in havuz if o.unit_id != kimlik]
        kimlikler = [kimlik]
    kayit = []
    for kimlik in kimlikler:
        eski = satirlar[kimlik]
        if eski["karar"] == "ekle":
            # Bu turda eklenen aday aktif pakette hiç yoktu: düşmesi bir
            # `cikar` değil, reddedilen adaydır (sentezin aynı sınıfı).
            satirlar[kimlik] = {
                "tur": "not",
                "sinif": "reddedilen-aday",
                "alan": eski["alan"],
                "gerekce": gerekce,
            }
        else:
            satirlar[kimlik] = {
                **{k: v for k, v in eski.items() if k not in identity.KURAL_DAMGA_ALANLARI},
                "karar": "cikar",
                "aktor": "insan",
                "gerekce": gerekce,
                "kanit": gerekce,
            }
            satirlar[kimlik].pop("kapsam", None)
        kayit.append({"islem": "cikar", "alan": eski["alan"], "unit_id": kimlik})
    return kayit


def _alanlar_kapisi(islem: Mapping, beklenen: set[str], etiket: str) -> None:
    if set(islem) != beklenen:
        raise OperatorKarariReddedildi(
            f"{etiket}: alanlar tam olarak {sorted(beklenen)} olmalı, {sorted(islem)} geldi"
        )


# ─── Ana giriş ───────────────────────────────────────────────────────────────


def uygula(
    sonuc: EngineResult,
    *,
    dosya: Any,
    sentez_sorulari: Sequence[str],
    takvim_anahtarlari: frozenset[str],
    actor: str,
    yeni_kimlik: Callable[[], str] = identity.new_unit_id,
) -> tuple[EngineResult, dict]:
    """Operatör kararlarını motor sonucuna uygular → (yeni sonuç, kayıt).

    Kayıt, koşu satırının `operator_kararlari` kolonuna yazılan yüktür.
    """
    if sonuc.sonuc != "blocked":
        raise OperatorKarariReddedildi(
            f"motor sonucu {sonuc.sonuc!r} — operatör kararı yalnız açık sorularla "
            "durmuş (`blocked`) koşuya yazılır"
        )
    sebepler = [s for s in (sonuc.sebep or "").split("; ") if s]
    diger = [s for s in sebepler if s != ACIK_SORU_SEBEBI]
    if diger:
        raise OperatorKarariReddedildi(
            f"koşuyu açık sorular DIŞINDA da durduran sebep var: {diger} — operatör "
            "kararı yalnız soruları kapatır, motorun başka kapısını aşmaz"
        )
    if sonuc.final_candidate is None or not sonuc.final_decision_log:
        raise OperatorKarariReddedildi(
            "motor nihai içerik üretmedi — üzerine karar uygulanacak paket yok"
        )

    acik = list(sonuc.policy_report.acik_soru_kimlikleri)
    kimlikler = soru_kimlikleri(acik, sentez_sorulari)
    kararlar = _dosya_kararlari(dosya)
    _kapsam_kapisi(kararlar, kimlikler)

    icerik = identity.cozulmus(sonuc.final_candidate)
    gunluk = [identity.cozulmus(s) for s in sonuc.final_decision_log]
    yasayan = [
        s for s in gunluk
        if s.get("tur") == "karar" and s.get("karar") in identity.YASAYAN_KARARLAR
    ]
    model = _Model(icerik, {s["oge_yolu"]: s["unit_id"] for s in yasayan})
    satirlar = {s["unit_id"]: s for s in yasayan}
    yeni_satirlar: list[dict] = []

    kayit_kararlar = []
    for karar in kararlar:
        islem_kayitlari: list[dict] = []
        for islem in karar.get("islemler", []):
            if not isinstance(islem, Mapping):
                raise OperatorKarariReddedildi(f"{karar['soru']}: işlem nesne değil")
            islem_kayitlari += _uygula_islem(
                model,
                satirlar,
                yeni_satirlar,
                islem,
                soru=karar["soru"],
                cevap=karar["cevap"],
                takvim=takvim_anahtarlari,
                yeni_kimlik=yeni_kimlik,
            )
        kayit_kararlar.append(
            {
                "soru": karar["soru"],
                "soru_metni": next(s for s, k in kimlikler.items() if k == karar["soru"]),
                "cevap": karar["cevap"].strip(),
                "islemler": islem_kayitlari,
            }
        )

    yeni_icerik = model.icerik()
    birimler = identity.enumerate_content_units(yeni_icerik)
    yol_kimlik = {yol: _yol_sahibi(model, yol) for yol in birimler}
    kimlik_yol = {k: y for y, k in yol_kimlik.items()}

    def _yolu_tazele(satir: dict) -> dict:
        if satir.get("tur") == "karar" and satir["karar"] in identity.YASAYAN_KARARLAR:
            yol = kimlik_yol[satir["unit_id"]]
            return {**satir, "oge_yolu": yol, "oge_sha": birimler[yol]["oge_sha"]}
        return satir

    # Sıra korunur: motorun satırları yerinde (işlem gördüyse güncel hâliyle),
    # operatörün yeni birimleri sonda.
    yeni_gunluk = [
        _yolu_tazele(satirlar[s["unit_id"]]) if s in yasayan else s for s in gunluk
    ] + [_yolu_tazele(satirlar[s["unit_id"]]) for s in yeni_satirlar]

    hatalar = list(structural_errors(yeni_icerik))
    hatalar += identity.validate_decision_log(yeni_gunluk)
    hatalar += identity.check_unit_integrity(yeni_icerik, yeni_gunluk)
    bilinmeyen = sorted(set(yeni_icerik.get("ozel_gun", {})) - set(takvim_anahtarlari))
    if bilinmeyen:
        hatalar.append(f"sistem takviminde olmayan özel gün: {bilinmeyen}")
    for _, yol, bayraklar in engine.bayrak_ihlalleri(yeni_icerik, yol_kimlik):
        hatalar.append(f"{yol}: {engine.bayrak_detayi(bayraklar, nihai=True)}")
    if hatalar:
        raise OperatorKarariReddedildi(
            "operatör kararları uygulanınca paket kapılardan geçmedi: "
            + " · ".join(dict.fromkeys(hatalar))
        )

    for karar in kayit_kararlar:
        for islem in karar["islemler"]:
            if islem["islem"] == "cikar":
                islem["hukuki"] = False
                continue
            # Aynı dosyada eklenip sonra çıkarılan birimin pakette yolu YOKTUR.
            islem["yol"] = kimlik_yol.get(islem["unit_id"])
            islem["hukuki"] = engine._mevzuat_mi(islem["alan"], engine._metin(islem["deger"]))

    # Motorun kuralı (`decide`): değişiklik = uygulanan karar ya da düşen takvim
    # birimi. Operatörün işlemi de değişikliktir; hiçbiri yoksa sonuç `no_change`.
    diff = sonuc.engine_diff
    degisiklik_var = (
        bool(diff.get("uygulanan_karar_sayisi"))
        or bool((diff.get("dusen_birimler") or {}).get("eslesmeyen_takvim"))
        or any(k["islemler"] for k in kayit_kararlar)
    )
    yeni_sonuc = dataclasses.replace(
        sonuc,
        sonuc="activation_eligible" if degisiklik_var else "no_change",
        sebep=None,
        final_candidate=yeni_icerik,
        final_decision_log=tuple(yeni_gunluk),
        policy_report=dataclasses.replace(sonuc.policy_report, acik_soru_kimlikleri=()),
        content_sha=engine.canonical_content_sha(yeni_icerik),
        decision_log_sha=identity.canonical_sha(yeni_gunluk),
    )
    kayit = {"actor": actor, "motor_surumu": sonuc.engine_version, "kararlar": kayit_kararlar}
    return yeni_sonuc, kayit


def _yol_sahibi(model: _Model, yol: str) -> str:
    """Yeniden kurulmuş içerikte bir yolun birim kimliği."""
    if yol in model.metin:
        return model.metin[yol].unit_id
    if yol.startswith("video_kodlar/"):
        havuz, sira = yol[len("video_kodlar/"):].rstrip("]").split("[")
        return model.video[havuz][int(sira)].unit_id
    if yol.startswith("ozel_gun/"):
        _, anahtar, yuva = yol.split("/")
        return model.ozel[anahtar][yuva].unit_id
    ad, sira = yol.rstrip("]").split("[")
    return model.liste[ad][int(sira)].unit_id
