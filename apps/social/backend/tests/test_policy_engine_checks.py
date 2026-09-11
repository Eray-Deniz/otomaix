"""Politika motorunun zorunlu kontrol kümesi (Plan 2 Task 12, spec §9.2).

Beş sözleşme burada pinlenir:

1. **MOTOR SONUÇ ÜRETMEZ, BULGU ÜRETİR.** `run_checks` saf bir ölçüm
   fonksiyonudur: koşu sonucu (`activation_eligible`/`no_change`/`blocked`)
   üretmez, veritabanına dokunmaz. Bulguyu sonuca çeviren `decide`'dır ve o
   Task 13'te doğar (arayüz eki R7).
2. **GİRDİ KÜMESİ KAPALIDIR (K-52).** `EngineInputs` alan alan pinlidir; marka
   DNA'sı için alan YOKTUR ve eklenmesi sözleşme revizyonu ister. Ham denetçi
   raporu motora GİRMEZ — yalnız tur seviyesindeki mutabakat kapısından çıkan
   `ValidatedAuditPair` kabul edilir (arayüz eki R5/R6).
3. **KONTROL KÜMESİ DONMUŞTUR.** `CHECKS` planın bağladığı on üç kontrolü
   sırasıyla taşır; kontrol eklemek/çıkarmak sözleşme revizyonudur (K-89
   emsali). Kontrol başına en az bir POZİTİF ve bir NEGATİF ölçüm vardır.
4. **KAPALI KÜMELER UYDURULMAZ.** Bulgu sınıfları (altı) ve uygulanmama
   sebepleri (üç) `engine_contract`'ta tanımlıdır; bu dosya onlara karşı ölçer.
   Kapalı kümeye sığmayan bir ihlal BULGU İCAT ETMEZ — girdi kapısında
   fail-closed durur (`EngineInputError`).
5. **BAĞIMSIZ ORACLE.** Kontrol adları ve K-129 alan listesi bu dosyada ELLE
   yazılıdır; üretim sabitlerinden TÜRETİLMEZ — türetilseydi yanlış bir ad da
   testi geçerdi (totolojik oracle).
"""

from __future__ import annotations

import hashlib
from unittest import mock
from pathlib import Path
from dataclasses import fields as dataclass_fields

import pytest

from app.services.sector_content_schema import structural_errors
from app.services.sector_pipeline import auditors, brief_doctor as bd, identity
from app.services.sector_pipeline import engine
from app.services.sector_pipeline.policy_config import PolicyConfig
from app.services.sector_pipeline.engine_contract import (
    BULGU_SINIFLARI,
    SONUCLAR,
    UYGULANMAMA_SEBEPLERI,
)
from app.services.sector_pipeline.synthesis import SynthesisResult


# ═══ Ölçüm anında ELLE yazılmış bağımsız beklentiler ═══════════════════════
#
# Kaynak: plan `### Task 12` "Bağlayıcı kontrol kümesi" satırı (spec §9.2'nin
# planda sabitlenmiş hâli) ve K-129'un spec §9.4'teki kapanış metni.

BEKLENEN_KONTROL_ADLARI = (
    "sema_ve_boyut",
    "karar_kapsami",
    "kimlik_benzersizligi",
    "kanit",
    "mutabakat",
    "yeni_oge_cogunlugu",
    "bayrak_tuketimi",
    "geri_ekleme_celiskisi",
    "kategori_cakismasi",
    "ozel_gun_anahtari",
    "diff_sayilari",
    "regresyon_kapisi",
    "tek_aktif_on_kontrolu",
)

BEKLENEN_GIRDI_ALANLARI = (
    "sentez",
    "aktif_paket",
    "aktif_schema_version",
    "aktif_birimler",
    "mevcut_birim_sayisi",
    "ilk_kosu",
    "son_turlarin_cikarmalari",
    "denetci_envanterleri",
    "mekanik_eleme",
    "takvim_anahtarlari",
    "takvim_kategorileri",
    "otomatik_kapilar",
)

MEVZUAT_ALANI = "yasaklar_ve_hassasiyetler"

TAKVIM_ANAHTARI = "cumhuriyet-bayrami"
SISTEM_KATEGORISI = "national"
"""Sistem takviminin bu gün için yazdığı kategori — ÖLÇÜLMÜŞ değer kümesinden.

`social.public_holidays.category` bugün üç değer taşıyor: `religious` ·
`national` · `commercial` (2026-09-11, yerel veritabanında sayıldı).
"""
MEVCUT_DONEM_ADI = "Cumhuriyet Bayramı"
YENI_DONEM_ADI = "Sevgililer Günü"
YENI_DONEM_ANAHTARI = "sevgililer-gunu"
"""Araştırmanın Bölüm C'de yazdığı DÖNEM ADI — sistem anahtarının slug'ı DEĞİL.

Sözleşme (`_SABLON.md` Bölüm C): *"`alan/dönem` hücresi ya Bölüm A alan adıdır
ya da Bölüm B dönem adıdır (`Sevgililer Günü` gibi) — aynen o yazımla"*. Karar
satırı ise `ozel_gun` taşır ve dönemi `oge_yolu`nun slug'ında saklar; ikisinin
bağı bu yüzden NORMALİZASYONLA kurulur. Değerler ÖLÇÜLDÜ:
`normalize_special_day_key('Cumhuriyet Bayramı')` → `cumhuriyet-bayrami` ve
`normalize_special_day_key('Sevgililer Günü')` → `sevgililer-gunu`.
"""


# ═══ İçerik kurucuları ═════════════════════════════════════════════════════


KORUNAN_KANCA = "Dogrulanmis kanca kalibi"
CIKARILACAK_KANCA = "Cikarilacak kanca kalibi"
MEVZUAT_MADDESI = "Ayar beyani mevzuata baglidir"


def _tam_icerik(**degisiklik) -> dict:
    """Yazım kapısını GEÇEN eksiksiz içerik — alan kümesi kapalı ve TAM."""
    icerik = {
        "kapsam": "Kuyumculuk: altin ve gumus taki perakendesi.",
        "ton_ve_dil": "Sicak, guven veren, sade.",
        "gorsel_kodlar": "Yakin cekim, sicak isik, doku vurgusu.",
        "cta_kaliplari": [
            {
                "kalip": "Vitrini gormek icin ugrayin",
                "tur": "ziyaret",
                "gerekce": "Magaza trafigi hedefi.",
            }
        ],
        "kanca_kaliplari": [KORUNAN_KANCA, CIKARILACAK_KANCA],
        "takvim_temalari": ["Sevgililer Gunu hediye secimi"],
        "yasaklar_ve_hassasiyetler": [MEVZUAT_MADDESI],
        "video_kodlar": {"hareket": ["yavas kaydirma"], "sahne": ["tezgah ustu"]},
        "ozel_gun": {
            TAKVIM_ANAHTARI: {
                "tur": "kutlama",
                "mesaj_ekseni": "Saygi cercevesi",
                "kanca": "Bayrama ozel vitrin",
                "cta": "Magazamiza bekleriz",
                "gorsel_vurgu": "Bayrak ve altin dokusu",
            }
        },
    }
    icerik.update(degisiklik)
    return icerik


AKTIF_ICERIK = _tam_icerik()


def _kimlik_haritasi(*icerikler: dict) -> dict[str, str]:
    """Yol → `unit_id`, deterministik. İlk gören içerik kimliği ÇİVİLER."""
    harita: dict[str, str] = {}
    for icerik in icerikler:
        for yol in sorted(identity.enumerate_content_units(icerik)):
            harita.setdefault(yol, "ku-" + f"{len(harita) + 1:012x}")
    return harita


KIMLIKLER = _kimlik_haritasi(AKTIF_ICERIK)


def _yol(icerik: dict, alan: str, deger) -> str:
    """Bir öğenin YOLUNU değerinden bulur — sıra numarası elle yazılmaz."""
    for yol, birim in identity.enumerate_content_units(icerik).items():
        if birim["alan"] == alan and birim["deger"] == deger:
            return yol
    raise AssertionError(f"fixture bozuk: {alan} altında {deger!r} yok")


def _gunluk(
    icerik: dict,
    *,
    kimlikler: dict[str, str] | None = None,
    degis: dict[str, dict] | None = None,
    ek: tuple[dict, ...] = (),
    dus: tuple[str, ...] = (),
    denetim=None,
) -> list[dict]:
    """Yaşayan her yola bir satır (varsayılan `koru`) + istenen ek satırlar."""
    harita = KIMLIKLER if kimlikler is None else kimlikler
    birimler = identity.enumerate_content_units(icerik)
    satirlar: list[dict] = []
    for yol in sorted(birimler):
        if yol in dus:
            continue
        satir = {
            "tur": "karar",
            "alan": birimler[yol]["alan"],
            "oge_yolu": yol,
            "unit_id": harita[yol],
            "oge_sha": birimler[yol]["oge_sha"],
            "karar": "koru",
            "gerekce": "Onceki turdan tasindi.",
            "kanit": "",
            "aktor": "sentez",
        }
        satir.update((degis or {}).get(yol, {}))
        _kaynak_iddiasini_tamamla(satir, denetim)
        satirlar.append(satir)
    satirlar.extend(ek)
    return satirlar


def _kaynak_iddiasini_tamamla(satir: dict, denetim=None) -> None:
    """`ekle` satırına `kaynak_iddia`'yı TÜRETİR — testi yazan elle yazmasın.

    Sentez sözleşmesi 2.2 bu alanı `ekle` satırında ZORUNLU kılar. Fixture'lar
    onu elle taşısaydı, alanı ölçmeyen onlarca test bu turda tek tek
    düzenlenirdi ve her biri bir yazım hatası adayı olurdu. Türetme, bağın
    KURULU hâlini üretir: `kanit`teki D# referansının gösterdiği denetçi
    satırının `kaynak-iddialari` sütunu. Bağı BOZAN vakalar alanı AÇIKÇA verir.
    """
    if satir.get("karar") != "ekle" or "kaynak_iddia" in satir:
        return
    etiketler: set[str] = set()
    for parca in str(satir.get("kanit") or "").split(","):
        parca = parca.strip()
        for denetci_satiri in DENETIM_TABLOSU if denetim is None else denetim:
            if parca in (f"D1#{denetci_satiri.no}", f"D2#{denetci_satiri.no}"):
                etiketler |= {
                    atif.etiket for atif in denetci_satiri.kaynak_iddialari
                }
    satir["kaynak_iddia"] = ", ".join(sorted(etiketler))


AKTIF_GUNLUK = _gunluk(AKTIF_ICERIK)
AKTIF_BIRIMLER = identity.decision_units(AKTIF_ICERIK, AKTIF_GUNLUK)
AKTIF_GORUNTU_SHA = identity.canonical_sha(AKTIF_BIRIMLER)


def _aktif_paket() -> dict:
    return {"schema_version": 1, "content": AKTIF_ICERIK, "decision_log": AKTIF_GUNLUK}


# ═══ Denetçi kurucuları ════════════════════════════════════════════════════


DOGRULANMIS_KAYNAK = "KAYNAK-1"
IKINCI_KAYNAK = "KAYNAK-2"
DOGRULANMIS_URL = "https://resmi.example/mevzuat-2026"
COZULEMEYEN_KANIT = "D1#42"


def _ornekle(*, erisildi: bool = True, uyumlu: bool = True) -> tuple[auditors.UrlCheck, ...]:
    return (
        auditors.UrlCheck(
            url=DOGRULANMIS_URL,
            kaynak=DOGRULANMIS_KAYNAK,
            erisildi=erisildi,
            icerik_uyumlu=uyumlu,
            not_metni="",
        ),
    )


def _envanter(statuler: dict[str, str] | None = None) -> tuple[auditors.InventoryRow, ...]:
    """K-100 tamlık sözleşmesi: aktif her birim TAM BİR KEZ görünür."""
    secim = statuler or {}
    return tuple(
        auditors.InventoryRow(
            unit_id=unit_id,
            statu=secim.get(unit_id, "supported"),
            kanit=DOGRULANMIS_KAYNAK,
            gerekce="Tek cumle gerekce.",
        )
        for unit_id in sorted(AKTIF_BIRIMLER)
    )


def _denetim_satiri(
    no: int,
    *,
    kaynaklar: set[int],
    sinif: str | None = None,
    alan: str = "kanca_kaliplari",
    oneri: str = "al",
    bayraklar: str = "—",
    kaynak_iddialari: set[auditors.KaynakIddiasi] | None = None,
) -> auditors.AuditRow:
    """Tek denetim satırı. `sinif` verilmezse kaynak sayısından TÜRETİLİR.

    `kaynak-iddialari` da verilmezse TÜRETİLİR: satır kimliği `no` ile aynı
    numaralı iddiaya, her kaynaktan bir tane. Fixture'ın sözleşmenin tutarlılık
    kuralına (geçen kaynak kümesi = `kaynaklar`) kendiliğinden uyması için.
    """
    if kaynak_iddialari is None:
        kaynak_iddialari = {
            auditors.KaynakIddiasi(kaynak=k, iddia=no) for k in kaynaklar
        }
    if sinif is None:
        sinif = (
            auditors.SINIF_TEKIL
            if len(kaynaklar) == 1
            else f"{len(kaynaklar)}-{auditors.AZAMI_KAYNAK}"
        )
    return auditors.AuditRow(
        no=no,
        alan=alan,
        iddia_ozeti=f"iddia {no}",
        kaynak_iddialari=frozenset(kaynak_iddialari),
        kaynaklar=frozenset(kaynaklar),
        sinif=sinif,
        bayraklar=bayraklar,
        oneri=oneri,
        gerekce="Tek cumle gerekce.",
    )


DENETIM_TABLOSU = (
    # Koşuya İKİ kaynak giriyor (`KAYNAK-1` · `KAYNAK-2`), oran ona uyarlıdır.
    _denetim_satiri(1, kaynaklar={1, 2}, sinif="2-2"),
    _denetim_satiri(2, kaynaklar={1}, sinif=auditors.SINIF_TEKIL),
    _denetim_satiri(3, kaynaklar={1, 2}, sinif=auditors.SINIF_CELISKI),
    # BAŞKA alanın satırı — `kanca_kaliplari` eklemesi buna dayanamaz.
    _denetim_satiri(4, kaynaklar={1, 2}, sinif="2-2", alan="cta_kaliplari"),
    # Denetçi eklemeye izin VERMEYEN öneri yazmış.
    _denetim_satiri(5, kaynaklar={1, 2}, sinif="2-2", oneri="alma"),
    # Denetçi TÜKETİLMESİ gereken bir bayrak yazmış; sentez onu düz yazıya
    # kopyalamamış olabilir — motor artık tipli sütundan okur.
    #
    # YAZIM NOTU (ölçüldü, MEVCUT sınırlama — bu turun ürünü DEĞİL): bayrak adı
    # ASCII yazımla verilir. `_katla` `ç`/`ğ`/`ş`'yi katlar ama NOKTASIZ `ı`'yı
    # KATLAMAZ; sözleşmenin kendi yazımı olan `[marka-adı]`, `[kanal-bağımlı]`
    # ve `[kaynak-bağımlı]` bu yüzden `BAYRAKLAR` kümesiyle EŞLEŞMEZ — ne bu
    # kapıda ne de eskiden beri var olan `_bayrak_tuketimi` kontrolünde.
    # Fixture kodun BUGÜN tanıdığı yazımı kullanır; sınır açıkça raporlandı.
    _denetim_satiri(6, kaynaklar={1, 2}, sinif="2-2", bayraklar="[marka-adi]"),
)

IKI_KAYNAKLI = "D1#1"
TEK_KAYNAKLI = "D1#2"
CELISKILI = "D1#3"
BASKA_ALAN = "D1#4"
OLUMSUZ_ONERI = "D1#5"
BAYRAKLI = "D1#6"


def _rapor(
    rol: str, *, statuler=None, ornekle=None, denetim=None, profil=None
) -> auditors.AuditReport:
    return auditors.AuditReport(
        denetci=rol,
        ham_metin=f"{rol} ham raporu",
        bolumler={ad: f"{ad} govdesi" for ad in auditors.BOLUM_ANAHTARLARI},
        denetim_tablosu=DENETIM_TABLOSU if denetim is None else denetim,
        kaynak_profili=KAYNAK_PROFILI if profil is None else profil,
        yeniden_dogrulama=_envanter(statuler),
        url_orneklem=_ornekle() if ornekle is None else ornekle,
        unit_snapshot_sha=AKTIF_GORUNTU_SHA,
    )


def _bos_gorunti_cifti(*, kaynak_sha=None, denetim=None):
    """İlk koşunun çifti: aktif birim YOK, görüntü BOŞ kümenin hash'idir."""
    sha = identity.canonical_sha({})
    raporlar = [
        auditors.AuditReport(
            denetci=rol,
            ham_metin=f"{rol} ham raporu",
            bolumler={ad: f"{ad} govdesi" for ad in auditors.BOLUM_ANAHTARLARI},
            denetim_tablosu=DENETIM_TABLOSU if denetim is None else denetim,
            kaynak_profili=KAYNAK_PROFILI,
            yeniden_dogrulama=(),
            url_orneklem=_ornekle(),
            unit_snapshot_sha=sha,
        )
        for rol in auditors.DENETCI_ROLLERI
    ]
    mutabakat = auditors.check_snapshot_agreement(
        (auditors.ValidatedReport(raporlar[0], ()), auditors.ValidatedReport(raporlar[1], ())),
        expected_snapshot_sha=sha,
        expected_kaynak_sha=KAYNAK_SETI_SHA if kaynak_sha is None else kaynak_sha,
    )
    assert mutabakat.gecerli, mutabakat.errors
    return mutabakat.cift


def _cift(
    *, statuler_1=None, statuler_2=None, ornekle_1=None, ornekle_2=None,
    denetim=None, kaynak_sha=None, profil_1=None, profil_2=None,
):
    """`ValidatedAuditPair` — TEK üreticisinden (mutabakat kapısı) geçerek."""
    mutabakat = auditors.check_snapshot_agreement(
        (
            auditors.ValidatedReport(
                _rapor(
                    auditors.DENETCI_ROLLERI[0],
                    statuler=statuler_1,
                    ornekle=ornekle_1,
                    denetim=denetim,
                    profil=profil_1,
                ),
                (),
            ),
            auditors.ValidatedReport(
                _rapor(
                    auditors.DENETCI_ROLLERI[1],
                    statuler=statuler_2,
                    ornekle=ornekle_2,
                    denetim=denetim,
                    profil=profil_2,
                ),
                (),
            ),
        ),
        expected_snapshot_sha=AKTIF_GORUNTU_SHA,
        expected_kaynak_sha=KAYNAK_SETI_SHA if kaynak_sha is None else kaynak_sha,
    )
    assert mutabakat.gecerli, mutabakat.errors
    return mutabakat.cift


def _ozet(ad: str) -> str:
    """Kanonik icerik ozeti — `DoctorReport` serbest metni kimlik kararina almaz."""
    return hashlib.sha256(ad.encode("utf-8")).hexdigest()


def _kaynak_seti_sha(kapi: bd.RoundGate) -> str:
    """Kapının kaynak kümesi kimliği — motorun karşılaştırdığı değerin ta kendisi."""
    return bd.kaynak_seti_sha(kapi.raporlar)


def _profil(*resmi: bool) -> tuple[auditors.KaynakProfili, ...]:
    """Denetçinin RESMÎLİK yargısı — K-126 istisnasının motordaki birinci ayağı."""
    return tuple(
        auditors.KaynakProfili(
            kaynak=no, resmi=deger, not_metni="Kaynak profili notu."
        )
        for no, deger in enumerate(resmi, start=1)
    )


KAYNAK_PROFILI = _profil(False, False)
"""VARSAYILAN profil: hiçbir kaynak resmî DEĞİL.

Bilinçli olarak KAPALI taraftan kurulur. K-126 istisnası açıkken varsayılanı
"resmî" yapmak, çoğunluk kapısını ölçen onlarca testi sessizce istisna koluna
kaydırırdı — sayımı ölçtüğünü sanan bir test aslında istisnayı ölçerdi.
İstisnayı ölçen testler profili AÇIKÇA verir.
"""


# Araştırma iddiaları: `K<kaynak>#<iddia>` evreni mekanik kapının
# raporlarından TÜRER (kaynak numarası KONUMDAN gelir — motorun kendi kuralı).
# Numaralar DENETİM_TABLOSU'nun satır numaralarıyla hizalı tutulur ki fixture
# okunur kalsın: `D1#4` başka alanın satırıysa `K1#4` da başka alanın iddiasıdır.
YENI_DONEM_IDDIA_NO = 101
MEVCUT_DONEM_IDDIA_NO = 102
"""Dönem iddialarının numaraları — denetim tablosu satır numaralarıyla ÇAKIŞMAZ."""


def _arastirma_iddialari(denetim=None) -> tuple[bd.CIddia, ...]:
    """Araştırma raporunun Bölüm C iddiaları — DENETİM TABLOSUNDAN türetilir.

    Hizalama fixture'ı okunur kılar ve GERÇEĞE de uyar: denetçi satırı hangi
    alanı anlatıyorsa, dayandığı araştırma iddiası da o alanı anlatır. Elle
    yazılmış bir evren, tabloya satır ekleyen her testte sessizce eksik kalırdı.

    İki DÖNEM iddiası ayrıca eklenir: Görev B bağı (`ozel_gun` kararı ↔ dönem
    adı) tablo satırlarından türetilemez, çünkü denetçi alanı `ozel_gun/...`
    yazımındadır, araştırma ise dönem ADINI yazar.
    """
    tablo = DENETIM_TABLOSU if denetim is None else denetim
    iddialar = {satir.no: satir.alan for satir in tablo}
    iddialar[YENI_DONEM_IDDIA_NO] = YENI_DONEM_ADI
    iddialar[MEVCUT_DONEM_IDDIA_NO] = MEVCUT_DONEM_ADI
    return tuple(
        bd.CIddia(no=no, alan=alan) for no, alan in sorted(iddialar.items())
    )


def _gecen_kapi(denetim=None) -> bd.RoundGate:
    return bd.gate_round(
        [
            bd.DoctorReport(
                sonuc=bd.SONUC_GECTI,
                notlar=(),
                elemeler=(),
                kaynak_adi=ad,
                icerik_ozeti=_ozet(ad),
                iddialar=_arastirma_iddialari(denetim),
            )
            for ad in (DOGRULANMIS_KAYNAK, IKINCI_KAYNAK)
        ]
    )


KAYNAK_SETI_SHA = _kaynak_seti_sha(_gecen_kapi())


# ═══ Girdi kurucusu ════════════════════════════════════════════════════════


def _sonuc(icerik: dict, gunluk: list[dict], *, acik_sorular=()) -> SynthesisResult:
    return SynthesisResult(
        aday_json=icerik,
        karar_gunlugu=tuple(dict(satir) for satir in gunluk),
        acik_sorular=tuple(acik_sorular),
        onay_ozeti="Ozet.",
        tasma=False,
    )


def _girdi(
    *,
    icerik: dict | None = None,
    gunluk: list[dict] | None = None,
    acik_sorular=(),
    aktif: bool = True,
    cift=None,
    denetim=None,
    kapi: bd.RoundGate | None = None,
    takvim: frozenset[str] | None = None,
    kategoriler: dict[str, str] | None = None,
    kapilar: engine.GateResults | None = None,
    cikarmalar: tuple = (),
) -> engine.EngineInputs:
    aday = AKTIF_ICERIK if icerik is None else icerik
    log = _gunluk(aday) if gunluk is None else gunluk
    birimler = AKTIF_BIRIMLER if aktif else {}
    # Kapı DEĞİŞTİYSE çiftin taşıdığı kaynak kimliği de o kapıdan türer: koşu
    # bağı kapısı fixture'ın kendi tutarsızlığını değil, ÜRETİM tutarsızlığını
    # ölçmelidir (kapının kendisi ayrı bir testte ölçülür).
    mekanik = _gecen_kapi(denetim) if kapi is None else kapi
    varsayilan_cift = (
        _cift(kaynak_sha=_kaynak_seti_sha(mekanik), denetim=denetim)
        if aktif
        else _bos_gorunti_cifti(
            kaynak_sha=_kaynak_seti_sha(mekanik), denetim=denetim
        )
    )
    return engine.EngineInputs(
        sentez=_sonuc(aday, log, acik_sorular=acik_sorular),
        aktif_paket=_aktif_paket() if aktif else None,
        aktif_schema_version=1 if aktif else None,
        aktif_birimler=birimler,
        mevcut_birim_sayisi=len(birimler),
        ilk_kosu=not aktif,
        son_turlarin_cikarmalari=cikarmalar,
        denetci_envanterleri=varsayilan_cift if cift is None else cift,
        mekanik_eleme=mekanik,
        takvim_anahtarlari=frozenset({TAKVIM_ANAHTARI}) if takvim is None else takvim,
        takvim_kategorileri=(
            {TAKVIM_ANAHTARI: SISTEM_KATEGORISI} if kategoriler is None else kategoriler
        ),
        otomatik_kapilar=(
            engine.GateResults(katman1_passed=True, tek_aktif_ihlali=False)
            if kapilar is None
            else kapilar
        ),
    )


def _siniflar(sonuc: engine.CheckOutcome) -> list[str]:
    return [bulgu.sinif for bulgu in sonuc.bulgular]


def _sebepler(sonuc: engine.CheckOutcome) -> list[str]:
    return [karar.sebep for karar in sonuc.uygulanmayan_kararlar]


# ═══ 1. Fixture'ın kendi sağlığı (pozitif kontrol) ═════════════════════════


def test_fixture_content_passes_the_writing_gate() -> None:
    """Ölçüm ancak girdi gerçekten geçerliyse anlamlıdır."""
    assert structural_errors(AKTIF_ICERIK) == []
    assert identity.check_unit_integrity(AKTIF_ICERIK, AKTIF_GUNLUK) == []


# ═══ 2. Girdi sözleşmesi (arayüz eki R5) ═══════════════════════════════════


def test_engine_inputs_field_set_is_closed() -> None:
    """K-52'nin denetlenebilir karşılığı: alan kümesi BİREBİR pinlidir."""
    alanlar = tuple(alan.name for alan in dataclass_fields(engine.EngineInputs))
    assert alanlar == BEKLENEN_GIRDI_ALANLARI


def test_engine_inputs_has_no_brand_dna_field() -> None:
    """K-52 negatif kontrolü — DNA okuma yolu AÇILMAZ."""
    adlar = {alan.name for alan in dataclass_fields(engine.EngineInputs)}
    assert not [ad for ad in adlar if "dna" in ad.lower() or "marka" in ad.lower()]


def test_engine_inputs_accepts_only_validated_pair() -> None:
    """Pozitif kontrol: mutabakat kapısından çıkan çift KABUL edilir."""
    girdi = _girdi()
    assert type(girdi.denetci_envanterleri) is auditors.ValidatedAuditPair


def test_engine_inputs_refuses_bare_audit_report_tuple() -> None:
    """İki ham rapordan oluşan demet REDDEDİLİR (R6/H3)."""
    ham = (_rapor(auditors.DENETCI_ROLLERI[0]), _rapor(auditors.DENETCI_ROLLERI[1]))
    with pytest.raises(TypeError, match="ValidatedAuditPair"):
        _girdi(cift=ham)


def test_engine_inputs_refuses_lookalike_pair() -> None:
    """Aynı alan adlarını taşıyan SAHTE nesne de reddedilir — ördek tipleme YOK."""

    class SahteCift:
        def __init__(self) -> None:
            self.birinci = _rapor(auditors.DENETCI_ROLLERI[0])
            self.ikinci = _rapor(auditors.DENETCI_ROLLERI[1])
            self.unit_snapshot_sha = AKTIF_GORUNTU_SHA

    with pytest.raises(TypeError, match="ValidatedAuditPair"):
        _girdi(cift=SahteCift())


def test_engine_inputs_rejects_inconsistent_unit_count() -> None:
    """`mevcut_birim_sayisi` bariyer paydasıdır; uydurulamaz."""
    with pytest.raises(ValueError, match="mevcut_birim_sayisi"):
        engine.EngineInputs(
            sentez=_sonuc(AKTIF_ICERIK, AKTIF_GUNLUK),
            aktif_paket=_aktif_paket(),
            aktif_schema_version=1,
            aktif_birimler=AKTIF_BIRIMLER,
            mevcut_birim_sayisi=len(AKTIF_BIRIMLER) + 1,
            ilk_kosu=False,
            son_turlarin_cikarmalari=(),
            denetci_envanterleri=_cift(),
            mekanik_eleme=_gecen_kapi(),
            takvim_anahtarlari=frozenset({TAKVIM_ANAHTARI}),
            takvim_kategorileri={TAKVIM_ANAHTARI: SISTEM_KATEGORISI},
            otomatik_kapilar=engine.GateResults(True, False),
        )


def test_engine_inputs_freezes_collections_before_the_count_check() -> None:
    """A3: koleksiyonlar ÖNCE donar — yapımdan sonra payda bozulamaz."""
    birimler = dict(AKTIF_BIRIMLER)
    girdi = _girdi()
    assert girdi.mevcut_birim_sayisi == len(birimler)
    with pytest.raises(TypeError):
        girdi.aktif_birimler["ku-yeni"] = {}  # type: ignore[index]
    assert isinstance(girdi.takvim_anahtarlari, frozenset)


# ═══ 3. Kontrol kümesi ve çıktı sözleşmesi ═════════════════════════════════


def test_checks_set_matches_the_binding_list() -> None:
    """`CHECKS` planın bağladığı on üç kontrolü SIRAYLA taşır."""
    assert tuple(kontrol.ad for kontrol in engine.CHECKS) == BEKLENEN_KONTROL_ADLARI


def test_every_check_has_a_description() -> None:
    """Her kontrol hangi hükmü uyguladığını KENDİ taşır."""
    assert all(kontrol.aciklama.strip() for kontrol in engine.CHECKS)


def test_run_checks_runs_every_check_in_the_frozen_set(monkeypatch) -> None:
    """Ekilen bir kontrol GERÇEKTEN koşar — küme dekoratif değildir."""
    kosulanlar: list[str] = []

    def izle(inputs):
        kosulanlar.append("ekilen")
        return engine.CheckOutput()

    ekli = engine.CHECKS + (
        engine.EngineCheck(ad="ekilen", aciklama="tarama izi", calistir=izle),
    )
    monkeypatch.setattr(engine, "CHECKS", ekli)
    engine.run_checks(_girdi())
    assert kosulanlar == ["ekilen"]


def test_run_checks_never_returns_a_run_outcome() -> None:
    """Sözleşme kapısı: motor SONUÇ üretmez — çıktı yalnız ölçüm taşır."""
    sonuc = engine.run_checks(_girdi())
    alanlar = tuple(alan.name for alan in dataclass_fields(engine.CheckOutcome))
    assert alanlar == ("bulgular", "uygulanmayan_kararlar", "notlar", "olcumler")
    metin = repr(sonuc)
    assert not [deger for deger in SONUCLAR if deger in metin]


def test_findings_and_reasons_stay_inside_the_closed_sets() -> None:
    """Bulgu sınıfı ve uygulanmama sebebi UYDURULAMAZ."""
    sonuc = engine.run_checks(_girdi())
    assert set(_siniflar(sonuc)) <= set(BULGU_SINIFLARI)
    assert set(_sebepler(sonuc)) <= set(UYGULANMAMA_SEBEPLERI)


def test_full_coverage_passes() -> None:
    """POZİTİF KONTROL: temiz bir tur hiç bulgu ÜRETMEZ."""
    sonuc = engine.run_checks(_girdi())
    assert sonuc.bulgular == ()
    assert sonuc.uygulanmayan_kararlar == ()
    assert sonuc.notlar == ()


def test_notes_pass_the_decision_log_schema() -> None:
    """Üretilen not satırları karar günlüğü şemasını GEÇER."""
    icerik = _tam_icerik(
        ozel_gun={
            "olmayan-gun": AKTIF_ICERIK["ozel_gun"][TAKVIM_ANAHTARI],
        }
    )
    sonuc = engine.run_checks(_girdi(icerik=icerik, gunluk=_gunluk(icerik, kimlikler=_kimlik_haritasi(AKTIF_ICERIK, icerik))))
    assert sonuc.notlar, "eşleşmeyen anahtar not ÜRETMELİ"
    assert identity.validate_decision_log([dict(n) for n in sonuc.notlar]) == []


# ═══ 4. Kontrol: şema + boyut ══════════════════════════════════════════════


def test_malformed_candidate_fails_closed() -> None:
    """Yazım kapısını geçmeyen aday için BULGU İCAT EDİLMEZ — kapı kapanır."""
    bozuk = _tam_icerik(kanca_kaliplari="liste degil")
    with pytest.raises(engine.EngineInputError, match="şema"):
        engine.run_checks(_girdi(icerik=bozuk, gunluk=AKTIF_GUNLUK))


def test_size_is_measured_but_never_blocks() -> None:
    """İlke 9: boyut ÖLÇÜLÜR, kapı DEĞİLDİR."""
    buyuk = _tam_icerik(kapsam="k" * 20000)
    gunluk = _gunluk(buyuk, kimlikler=_kimlik_haritasi(AKTIF_ICERIK, buyuk))
    sonuc = engine.run_checks(_girdi(icerik=buyuk, gunluk=gunluk))
    assert sonuc.bulgular == ()
    assert sonuc.olcumler["boyut"]["toplam_karakter"] > 20000


# ═══ 5. Kontrol: karar kapsamı (K-84 / K-107) ══════════════════════════════


def test_missing_unit_result_emits_kapsam_ihlali_finding() -> None:
    """Aktif birimin sonucu YOKSA kapsam ihlali doğar.

    Öğe adaydan düşürülür ama `cikar` satırı YAZILMAZ — sessiz taşıma tam da
    K-84'ün kapattığı sınıftır.
    """
    aday = _tam_icerik(kanca_kaliplari=[KORUNAN_KANCA])
    sonuc = engine.run_checks(_girdi(icerik=aday, gunluk=_gunluk(aday)))
    bulgular = [b for b in sonuc.bulgular if b.unit_id == CIKAN_KIMLIK]
    assert [b.sinif for b in bulgular] == ["kapsam_ihlali"]


def test_unknown_unit_id_emits_kapsam_ihlali_finding() -> None:
    """Aktif pakette karşılığı olmayan `unit_id` de kapsam ihlalidir."""
    hedef = _yol(AKTIF_ICERIK, "kapsam", AKTIF_ICERIK["kapsam"])
    gunluk = _gunluk(AKTIF_ICERIK, degis={hedef: {"unit_id": "ku-aaaaaaaaaaaa"}})
    sonuc = engine.run_checks(_girdi(gunluk=gunluk))
    assert "kapsam_ihlali" in _siniflar(sonuc)


def test_partial_run_with_koru_rows_has_full_coverage() -> None:
    """K-107: kısmi turda değişmeyen birim `koru` satırı taşır — kapsam TAMDIR."""
    hedef = _yol(AKTIF_ICERIK, "kapsam", AKTIF_ICERIK["kapsam"])
    gunluk = _gunluk(AKTIF_ICERIK, degis={hedef: {"kapsam": "kismi-tur-tasima"}})
    sonuc = engine.run_checks(_girdi(gunluk=gunluk))
    assert "kapsam_ihlali" not in _siniflar(sonuc)


def test_first_run_has_full_coverage_without_active_units() -> None:
    """İlk koşuda aktif birim yoktur; kapsam kontrolü kendi kendini bloklamaz."""
    gunluk = _gunluk(
        AKTIF_ICERIK,
        degis={
            yol: {"karar": "ekle", "kanit": f"{DOGRULANMIS_KAYNAK}, {IKINCI_KAYNAK}"}
            for yol in identity.enumerate_content_units(AKTIF_ICERIK)
        },
    )
    sonuc = engine.run_checks(_girdi(gunluk=gunluk, aktif=False))
    assert "kapsam_ihlali" not in _siniflar(sonuc)


# ═══ 6. Kontrol: yeni kimlik benzersizliği ═════════════════════════════════


def test_duplicate_new_identity_emits_kapsam_ihlali_finding() -> None:
    """`ekle` satırı aktif bir kimliği YENİDEN kullanamaz (K-86/K-152)."""
    aday = _tam_icerik(kanca_kaliplari=[KORUNAN_KANCA, "Yeni kanca kalibi"])
    yeni_yol = _yol(aday, "kanca_kaliplari", "Yeni kanca kalibi")
    gunluk = _gunluk(
        aday,
        degis={
            yeni_yol: {
                "karar": "ekle",
                "kanit": f"{DOGRULANMIS_KAYNAK}, {IKINCI_KAYNAK}",
            }
        },
    )
    # Yol AYNI olduğu için satır aktif kimliği (CIKAN_KIMLIK) taşır: yeni kalıp
    # eski kimliğin üstüne yazılmaya çalışılıyor.
    sonuc = engine.run_checks(_girdi(icerik=aday, gunluk=gunluk))
    detaylar = [b.detay for b in sonuc.bulgular if b.sinif == "kapsam_ihlali"]
    assert any("yeniden kullan" in detay for detay in detaylar), detaylar


def test_yerine_gecer_must_point_to_an_active_unit() -> None:
    """`yerine_gecer` aktif olmayan kimliğe işaret edemez — çift KOPUK olur."""
    aday = _tam_icerik(
        kanca_kaliplari=[KORUNAN_KANCA, CIKARILACAK_KANCA, "Yeni kanca kalibi"]
    )
    harita = _kimlik_haritasi(AKTIF_ICERIK, aday)
    yeni_yol = _yol(aday, "kanca_kaliplari", "Yeni kanca kalibi")
    gunluk = _gunluk(
        aday,
        kimlikler=harita,
        degis={
            yeni_yol: {
                "karar": "ekle",
                "kanit": f"{DOGRULANMIS_KAYNAK}, {IKINCI_KAYNAK}",
                "yerine_gecer": "ku-ffffffffffff",
            }
        },
    )
    sonuc = engine.run_checks(_girdi(icerik=aday, gunluk=gunluk))
    detaylar = [b.detay for b in sonuc.bulgular if b.sinif == "kapsam_ihlali"]
    assert any("yerine_gecer" in detay for detay in detaylar), detaylar


def test_new_identity_that_is_unique_emits_no_finding() -> None:
    """POZİTİF: gerçekten yeni kimlik bulgu üretmez."""
    yeni = _tam_icerik(kanca_kaliplari=[KORUNAN_KANCA, CIKARILACAK_KANCA, "Yeni kanca"])
    harita = _kimlik_haritasi(AKTIF_ICERIK, yeni)
    yeni_yol = _yol(yeni, "kanca_kaliplari", "Yeni kanca")
    gunluk = _gunluk(
        yeni,
        kimlikler=harita,
        degis={yeni_yol: {"karar": "ekle", "kanit": f"{DOGRULANMIS_KAYNAK}, {IKINCI_KAYNAK}"}},
    )
    sonuc = engine.run_checks(_girdi(icerik=yeni, gunluk=gunluk))
    assert sonuc.bulgular == ()


# ═══ 7. Kontrol: kanıt (spec girdisi satır 1189) ═══════════════════════════


def _guncelle_girdisi(
    *, alan: str, eski, yeni_metin: str, kanit: str, statuler_1=None, statuler_2=None,
    cikarmalar: tuple = (),
):
    """Tek bir öğeyi `guncelle` ile değiştiren tur — tek eksende ölçüm."""
    yol = _yol(AKTIF_ICERIK, alan, eski)
    aday = _tam_icerik()
    if alan == "kanca_kaliplari":
        aday["kanca_kaliplari"] = [
            yeni_metin if metin == eski else metin for metin in aday["kanca_kaliplari"]
        ]
    elif alan == "takvim_temalari":
        aday["takvim_temalari"] = [yeni_metin]
    elif alan == MEVZUAT_ALANI:
        aday[MEVZUAT_ALANI] = [yeni_metin]
    else:  # pragma: no cover - fixture koruması
        raise AssertionError(f"kurucu {alan!r} alanını taşımıyor")
    gunluk = _gunluk(aday, degis={yol: {"karar": "guncelle", "kanit": kanit}})
    return _girdi(
        icerik=aday,
        gunluk=gunluk,
        cift=_cift(statuler_1=statuler_1, statuler_2=statuler_2),
        cikarmalar=cikarmalar,
    )


def _mevcut_kimlik(alan: str, deger) -> str:
    return KIMLIKLER[_yol(AKTIF_ICERIK, alan, deger)]


KANCA_KIMLIGI = _mevcut_kimlik("kanca_kaliplari", KORUNAN_KANCA)
CIKAN_KIMLIK = _mevcut_kimlik("kanca_kaliplari", CIKARILACAK_KANCA)
MEVZUAT_KIMLIGI = _mevcut_kimlik(MEVZUAT_ALANI, MEVZUAT_MADDESI)
TEMA_KIMLIGI = _mevcut_kimlik("takvim_temalari", "Sevgililer Gunu hediye secimi")

MUTABIK = {KANCA_KIMLIGI: "needs_update"}
MUTABIK_MEVZUAT = {MEVZUAT_KIMLIGI: "needs_update"}
MUTABIK_TEMA = {TEMA_KIMLIGI: "needs_update"}


def test_guncelle_without_evidence_is_recorded_as_unapplied() -> None:
    """Kanıt çözülmezse karar UYGULANMAZ olarak KAYDEDİLİR (uygulama Task 13'te)."""
    sonuc = engine.run_checks(
        _guncelle_girdisi(
            alan="kanca_kaliplari",
            eski=KORUNAN_KANCA,
            yeni_metin="Guncellenmis kanca kalibi",
            kanit=COZULEMEYEN_KANIT,
            statuler_1=MUTABIK,
            statuler_2=MUTABIK,
        )
    )
    assert "kanit-yok" in _sebepler(sonuc)


def test_guncelle_with_validated_reference_is_not_recorded() -> None:
    """POZİTİF: doğrulanmış referans taşıyan karar kayda GİRMEZ."""
    sonuc = engine.run_checks(
        _guncelle_girdisi(
            alan="kanca_kaliplari",
            eski=KORUNAN_KANCA,
            yeni_metin="Guncellenmis kanca kalibi",
            kanit=DOGRULANMIS_KAYNAK,
            statuler_1=MUTABIK,
            statuler_2=MUTABIK,
        )
    )
    assert sonuc.uygulanmayan_kararlar == ()


def test_unreachable_url_does_not_count_as_evidence() -> None:
    """Örneklem satırı açılamadıysa referans DOĞRULANMIŞ sayılmaz."""
    yol = _yol(AKTIF_ICERIK, "kanca_kaliplari", KORUNAN_KANCA)
    aday = _tam_icerik(kanca_kaliplari=["Guncellenmis kanca kalibi", CIKARILACAK_KANCA])
    gunluk = _gunluk(aday, degis={yol: {"karar": "guncelle", "kanit": DOGRULANMIS_URL}})
    sonuc = engine.run_checks(
        _girdi(
            icerik=aday,
            gunluk=gunluk,
            cift=_cift(
                statuler_1=MUTABIK,
                statuler_2=MUTABIK,
                ornekle_1=_ornekle(erisildi=False),
                ornekle_2=_ornekle(erisildi=False),
            ),
        )
    )
    assert "kanit-yok" in _sebepler(sonuc)


# ═══ 8. Kontrol: mutabakat (K-125) ═════════════════════════════════════════


def test_guncelle_without_two_auditor_agreement_keeps_pattern() -> None:
    """Uyuşmazlıkta karar UYGULANMAZ; kalıp korunur (normal içerik)."""
    sonuc = engine.run_checks(
        _guncelle_girdisi(
            alan="kanca_kaliplari",
            eski=KORUNAN_KANCA,
            yeni_metin="Guncellenmis kanca kalibi",
            kanit=DOGRULANMIS_KAYNAK,
            statuler_1=MUTABIK,
            statuler_2={KANCA_KIMLIGI: "supported"},
        )
    )
    assert "mutabakat-yok" in _sebepler(sonuc)
    assert "mevzuat_uyusmazligi" not in _siniflar(sonuc)


def test_agreeing_auditors_produce_no_record() -> None:
    """POZİTİF: iki denetçi uyuşuyorsa kayıt YOK."""
    sonuc = engine.run_checks(
        _guncelle_girdisi(
            alan="kanca_kaliplari",
            eski=KORUNAN_KANCA,
            yeni_metin="Guncellenmis kanca kalibi",
            kanit=DOGRULANMIS_KAYNAK,
            statuler_1=MUTABIK,
            statuler_2=MUTABIK,
        )
    )
    assert sonuc.uygulanmayan_kararlar == ()
    assert sonuc.bulgular == ()


def test_cikar_without_two_auditor_agreement_keeps_pattern() -> None:
    """`cikar` da mutabakat ister — tek denetçinin çelişkisi yetmez."""
    aday = _tam_icerik(kanca_kaliplari=[KORUNAN_KANCA])
    cikan_yol = _yol(AKTIF_ICERIK, "kanca_kaliplari", CIKARILACAK_KANCA)
    birim = identity.enumerate_content_units(AKTIF_ICERIK)[cikan_yol]
    cikar_satiri = {
        "tur": "karar",
        "alan": birim["alan"],
        "oge_yolu": cikan_yol,
        "unit_id": CIKAN_KIMLIK,
        "oge_sha": birim["oge_sha"],
        "karar": "cikar",
        "gerekce": "Kaynaklar celisti.",
        "kanit": DOGRULANMIS_KAYNAK,
        "aktor": "sentez",
    }
    gunluk = _gunluk(aday, ek=(cikar_satiri,))
    sonuc = engine.run_checks(
        _girdi(
            icerik=aday,
            gunluk=gunluk,
            cift=_cift(
                statuler_1={CIKAN_KIMLIK: "contradicted"},
                statuler_2={CIKAN_KIMLIK: "supported"},
            ),
        )
    )
    assert "mutabakat-yok" in _sebepler(sonuc)


# ═══ 9. Kontrol: mevzuat kolları (K-129 / K-125 / K-128) ══════════════════


def test_legislation_disagreement_emits_mevzuat_uyusmazligi_finding() -> None:
    """K-129 alanında uyuşmazlık BULGU üretir — kayıt değil."""
    sonuc = engine.run_checks(
        _guncelle_girdisi(
            alan=MEVZUAT_ALANI,
            eski=MEVZUAT_MADDESI,
            yeni_metin="Ayar beyani guncellendi",
            kanit=DOGRULANMIS_KAYNAK,
            statuler_1=MUTABIK_MEVZUAT,
            statuler_2={MEVZUAT_KIMLIGI: "supported"},
        )
    )
    assert "mevzuat_uyusmazligi" in _siniflar(sonuc)


def test_number_claim_outside_the_field_list_is_legislation() -> None:
    """K-129'un ikinci kolu: sayı/tarih iddiası taşıyan madde de mevzuattır."""
    sonuc = engine.run_checks(
        _guncelle_girdisi(
            alan="takvim_temalari",
            eski="Sevgililer Gunu hediye secimi",
            yeni_metin="Sevgililer Gunu 2026 kampanya takvimi",
            kanit=DOGRULANMIS_KAYNAK,
            statuler_1=MUTABIK_TEMA,
            statuler_2={TEMA_KIMLIGI: "supported"},
        )
    )
    assert "mevzuat_uyusmazligi" in _siniflar(sonuc)


def test_plain_item_disagreement_is_not_legislation() -> None:
    """NEGATİF KONTROL: sayısız/normal madde mevzuat koluna DÜŞMEZ."""
    sonuc = engine.run_checks(
        _guncelle_girdisi(
            alan="kanca_kaliplari",
            eski=KORUNAN_KANCA,
            yeni_metin="Guncellenmis kanca kalibi",
            kanit=DOGRULANMIS_KAYNAK,
            statuler_1=MUTABIK,
            statuler_2={KANCA_KIMLIGI: "supported"},
        )
    )
    assert "mevzuat_uyusmazligi" not in _siniflar(sonuc)


def test_unverified_legislation_emits_mevzuat_dogrulanamadi_finding() -> None:
    """K-128 yolu: `risk_unverified` mevzuat birimi BULGU üretir (pasif kapı)."""
    sonuc = engine.run_checks(
        _girdi(cift=_cift(statuler_1={MEVZUAT_KIMLIGI: "risk_unverified"}))
    )
    assert "mevzuat_dogrulanamadi" in _siniflar(sonuc)


def test_unverified_plain_item_emits_no_legislation_finding() -> None:
    """POZİTİF/NEGATİF ayrımı: mevzuat DIŞI birimin `risk_unverified`'ı bulgu değil."""
    sonuc = engine.run_checks(
        _girdi(cift=_cift(statuler_1={KANCA_KIMLIGI: "risk_unverified"}))
    )
    assert "mevzuat_dogrulanamadi" not in _siniflar(sonuc)


# ═══ 10. Kontrol: yeni öğe 2-3 çoğunluğu + K-126 istisnası ════════════════


def _ekle_girdisi(
    *,
    kanit: str,
    kaynak_iddia: str | None = None,
    metin: str = "Yeni kanca kalibi",
    ornekle=None,
    cikarmalar=(),
    denetim=None,
    kaynak_sha=None,
    kapi=None,
    profil_1=None,
    profil_2=None,
):
    aday = _tam_icerik(kanca_kaliplari=[KORUNAN_KANCA, CIKARILACAK_KANCA, metin])
    harita = _kimlik_haritasi(AKTIF_ICERIK, aday)
    yeni_yol = _yol(aday, "kanca_kaliplari", metin)
    gunluk = _gunluk(
        aday,
        kimlikler=harita,
        degis={
            yeni_yol: (
                {"karar": "ekle", "kanit": kanit}
                if kaynak_iddia is None
                else {
                    "karar": "ekle",
                    "kanit": kanit,
                    "kaynak_iddia": kaynak_iddia,
                }
            )
        },
        denetim=DENETIM_TABLOSU if denetim is None else denetim,
    )
    # Mekanik kapı ile çiftin taşıdığı kaynak kimliği AYNI kapıdan türer:
    # denetim tablosu değişince iddia evreni de değişir ve evren mühre girer
    # (`kaynak_seti_sha`), yani sabit bir hash koşu bağı kapısını düşürürdü.
    mekanik = _gecen_kapi(denetim) if kapi is None else kapi
    return _girdi(
        icerik=aday,
        gunluk=gunluk,
        cift=_cift(
            ornekle_1=ornekle,
            ornekle_2=ornekle,
            denetim=denetim,
            profil_1=profil_1,
            profil_2=profil_2,
            kaynak_sha=(
                _kaynak_seti_sha(mekanik) if kaynak_sha is None else kaynak_sha
            ),
        ),
        kapi=mekanik,
        cikarmalar=cikarmalar,
    )


def test_new_item_needs_two_of_three() -> None:
    """Tek kaynaklı yeni öğe yapısal çoğunluğu geçemez.

    Sayı artık DENETÇİNİN sütunundan okunur: `D1#2` satırı tek kaynak taşıyor.
    """
    sonuc = engine.run_checks(_ekle_girdisi(kanit=TEK_KAYNAKLI))
    assert "cogunluk-yok" in _sebepler(sonuc)


def test_new_item_with_two_sources_passes() -> None:
    """POZİTİF: denetçi satırı iki kaynak gösteriyorsa çoğunluk KARŞILANIR."""
    sonuc = engine.run_checks(_ekle_girdisi(kanit=IKI_KAYNAKLI))
    assert sonuc.uygulanmayan_kararlar == ()


def test_new_item_without_an_auditor_reference_is_not_applied() -> None:
    """Çıplak kaynak etiketi ARTIK yetmez — sayı denetçi sütunundan gelir.

    Alan dilbilgisi bakımından KUSURSUZDUR (iki geçerli kör etiket); düşen tek
    şey, motorun okuyacağı denetçi satırına referans olmamasıdır. Sebep
    `kanit-yok` DEĞİL `referans-yok` diye adlandırılır: hangi kapının düştüğü
    rapordan okunabilmelidir.
    """
    sonuc = engine.run_checks(
        _ekle_girdisi(kanit=f"{DOGRULANMIS_KAYNAK}, {IKINCI_KAYNAK}")
    )
    assert "referans-yok" in _sebepler(sonuc)
    assert "cogunluk-yok" not in _sebepler(sonuc)


def test_extra_bare_labels_do_not_add_to_the_count() -> None:
    """Referansın YANINDAKİ çıplak etiketler sayıya KATILMAZ (sözleşme 2.1).

    Tek kaynaklı bir satıra iki çıplak etiket eklenirse eski motor üçe sayardı;
    yeni motor yalnız satırın kendi sütununu okur ve çoğunluk düşer.
    """
    sonuc = engine.run_checks(
        _ekle_girdisi(
            kanit=f"{TEK_KAYNAKLI}, {DOGRULANMIS_KAYNAK}, {IKINCI_KAYNAK}"
        )
    )
    assert "cogunluk-yok" in _sebepler(sonuc)


def test_an_unresolvable_reference_is_not_applied() -> None:
    """Var olmayan satıra yapılan atıf çözülmez — karar uygulanmaz."""
    sonuc = engine.run_checks(_ekle_girdisi(kanit="D1#99"))
    assert "referans-yok" in _sebepler(sonuc)


def test_a_reference_to_another_field_is_not_applied() -> None:
    """Atıf BAŞKA bir alanın satırını gösteriyorsa karar UYGULANMAZ.

    Hakem turu 1 (yüksek): motor yalnız `kaynaklar` ve `sinif` okuyordu, yani
    `kanca_kaliplari` eklemesi `cta_kaliplari` hakkındaki bir satıra dayanıp
    çoğunluk kapısını geçebiliyordu. Bu olağan sentez sapmasıdır; test
    fixture'ının kendisi de tam bu eşleşmeyi taşıyor ve hatayı MASKELİYORDU.
    """
    sonuc = engine.run_checks(_ekle_girdisi(kanit=BASKA_ALAN))
    assert "referans-uyusmuyor" in _sebepler(sonuc)
    assert "cogunluk-yok" not in _sebepler(sonuc)


# ── Atıf ADAYA bağlanır: iki uçlu iddia bağı (dış depo `12beec1`) ─────────
#
# Yetkilendirme bağı 2026-09-11'e kadar ALAN düzeyindeydi: `kanca_kaliplari`
# hakkındaki HERHANGİ bir denetçi satırı, o listeye giren HERHANGİ bir kalıbı
# yetkilendirebiliyordu. Aynı eksen üç hakem turunda üç varyant üretti; varyant
# yamamak bırakıldı ve sınıf, üç beyanı da AYNI üst kaynağa — araştırma
# iddiasının numarasına — çivileyerek kapatıldı.


def test_an_addition_without_a_claim_reference_is_not_applied() -> None:
    """Sentez sözleşmesi 2.2: `kaynak_iddia` `ekle` satırında ZORUNLU."""
    sonuc = engine.run_checks(_ekle_girdisi(kanit=IKI_KAYNAKLI, kaynak_iddia=""))
    assert "kaynak-iddia-yok" in _sebepler(sonuc)


@pytest.mark.parametrize(
    "deger", ["hepsi", "K1", "1#1", "K1#1 K2#1", "K2#1, K1#1", "K1#1, K1#1"],
    ids=["duzyazi", "iddiasiz", "kaynaksiz", "ayracsiz", "azalan", "tekrar"],
)
def test_a_malformed_claim_reference_is_not_applied(deger: str) -> None:
    """Biçim KAPALI — ayrıştırıcı denetçi sütunuyla AYNI, ikinci kural yok."""
    sonuc = engine.run_checks(
        _ekle_girdisi(kanit=IKI_KAYNAKLI, kaynak_iddia=deger)
    )
    assert "kaynak-iddia-yok" in _sebepler(sonuc)


def test_a_claim_that_is_not_in_the_research_is_not_applied() -> None:
    """(a) ayağı: numaranın gösterdiği satır araştırmada GERÇEKTEN olmalı."""
    sonuc = engine.run_checks(
        _ekle_girdisi(kanit=IKI_KAYNAKLI, kaynak_iddia="K1#404")
    )
    assert "iddia-arastirmada-yok" in _sebepler(sonuc)


def test_a_claim_about_another_field_is_not_applied() -> None:
    """(a) ayağının İKİNCİ yarısı: iddianın ALANI kararla örtüşmek zorunda.

    `K1#4` araştırmada VARDIR ama `cta_kaliplari` hakkındadır; `kanca_kaliplari`
    eklemesi ona dayanamaz. Varlık kontrolü tek başına bırakılsaydı kapatılan
    sınıf bir basamak aşağıda aynen sürerdi.
    """
    sonuc = engine.run_checks(
        _ekle_girdisi(kanit=IKI_KAYNAKLI, kaynak_iddia="K1#4")
    )
    assert "iddia-arastirmada-yok" in _sebepler(sonuc)


def test_a_claim_the_cited_auditor_row_does_not_carry_is_not_applied() -> None:
    """(b) ayağı: `kanit`teki denetçi satırı AYNI numarayı taşımalı.

    `K1#2` araştırmada vardır ve alanı da örtüşür — ama atıf yapılan satır
    (`D1#1`) kendi `kaynak-iddialari` sütununda `K1#1` yazmıştır. Tek uçlu bir
    bağ burada geçerdi: iki beyanı da AYNI model yazar, üçüncü taraf (denetçinin
    tipli sütunu) olmadan zincir kapanmaz.
    """
    sonuc = engine.run_checks(
        _ekle_girdisi(kanit=IKI_KAYNAKLI, kaynak_iddia="K1#2")
    )
    assert "iddia-denetcide-yok" in _sebepler(sonuc)


def test_the_two_ended_claim_link_passes_when_both_ends_hold() -> None:
    """POZİTİF KONTROL: bağın iki ucu da duruyorsa karar UYGULANIR.

    Bu kol olmadan yukarıdaki beş test "kapı her şeyi reddediyor" hâliyle de
    yeşil kalırdı.
    """
    sonuc = engine.run_checks(
        _ekle_girdisi(kanit=IKI_KAYNAKLI, kaynak_iddia="K1#1, K2#1")
    )
    assert sonuc.uygulanmayan_kararlar == ()


def test_an_unrelated_row_cannot_supply_the_majority() -> None:
    """F2 (hakem turu 1, yüksek — ÖLÇÜLDÜ): SAYIM da iddiaya bağlıdır.

    Kapatıldığı iddia edilen sınıf yetkilendirme ayağında kapanmış, SAYIM
    ayağında yaşamaya devam ediyordu: tek kaynaklı bir iddiadan türetildiği
    BEYAN EDİLEN kalıp, atfa aynı alandan alakasız bir satır eklenerek
    iki-kaynaklık çoğunluk devralıyor ve bu turda açılan K-126 istisnasını
    (resmîlik + canlı URL) tamamen ATLIYORDU.
    """
    # TABAN: tek kaynaklı iddia yalnız başına çoğunluğu geçemez.
    tek = engine.run_checks(_ekle_girdisi(kanit=TEK_KAYNAKLI, kaynak_iddia="K1#2"))
    assert "cogunluk-yok" in _sebepler(tek)
    # Alakasız KOMŞU satır eklenince de geçemez — sayım iddiaya bağlı.
    komsulu = engine.run_checks(
        _ekle_girdisi(kanit=f"{TEK_KAYNAKLI}, {IKI_KAYNAKLI}", kaynak_iddia="K1#2")
    )
    assert "cogunluk-yok" not in _sebepler(komsulu), (
        "komşu satır artık sayıma girmemeli; onun yerine ATIF kapısı düşmeli"
    )
    assert "iddia-denetcide-yok" in _sebepler(komsulu)


def test_a_cited_row_carrying_no_declared_claim_is_rejected() -> None:
    """Bağın İKİNCİ yönü: her atıf yapılan satır en az bir iddiayı taşımalı.

    Tek yönlü bir bağ ("her iddia bir satırda geçsin") atfa istenen sayıda
    alakasız satır eklenmesine izin verir; o satırlar sayıma girmese bile
    provenans yalan söyler — karar, dayanmadığı satırlara atıf yapmış olur.
    """
    sonuc = engine.run_checks(
        _ekle_girdisi(kanit=f"{IKI_KAYNAKLI}, {TEK_KAYNAKLI}", kaynak_iddia="K1#1, K2#1")
    )
    assert "iddia-denetcide-yok" in _sebepler(sonuc)


def test_the_majority_narrowing_holds_even_if_the_citation_gate_falls() -> None:
    """F2'nin İKİNCİ katmanı BAĞIMSIZ ölçülür (savunma derinliği gerçek mi?).

    Çift yönlü atıf kapısı ayaktayken sayım daraltması ERİŞİLEMEZ — mutasyon
    ölçümü bunu yakaladı: daraltmayı söktüğümde hiçbir test düşmedi, yani
    "ikinci katman" ölçülmemiş koddu. Ölçmenin tek yolu BİRİNCİ katmanı
    devre dışı bırakıp ikincisini tek başına sınamaktır; aksi hâlde
    "savunma derinliği" iddiası doğrulanmamış kalırdı.
    """
    girdi = _ekle_girdisi(
        kanit=f"{TEK_KAYNAKLI}, {IKI_KAYNAKLI}", kaynak_iddia="K1#2"
    )
    # Kontrol kolu: birinci katman ayakta → atıf kapısı düşürüyor.
    assert "iddia-denetcide-yok" in _sebepler(engine.run_checks(girdi))

    # BİRİNCİ katman sökülür ("her atıf bir iddia taşıyor" gibi davranır);
    # ikinci katman tek başına ayakta mı?
    with mock.patch.object(engine, "_iddiasiz_atiflar", lambda atiflar, tasiyan: []):
        sonuc = engine.run_checks(girdi)
    assert "cogunluk-yok" in _sebepler(sonuc), (
        "atıf kapısı düşünce sayım daraltması TEK BAŞINA tutmalı"
    )


def test_the_claim_bound_majority_still_admits_a_genuine_two_source_claim() -> None:
    """POZİTİF KONTROL: daraltma MEŞRU çoğunluğu kapatmıyor.

    Bu kol olmadan F2 düzeltmesi "her şeyi reddet" hâliyle de yeşil kalırdı.
    """
    sonuc = engine.run_checks(
        _ekle_girdisi(kanit=IKI_KAYNAKLI, kaynak_iddia="K1#1, K2#1")
    )
    assert sonuc.uygulanmayan_kararlar == ()


def test_the_claim_link_gates_are_separately_measurable() -> None:
    """MUTASYON: her ayak AYRI sökülür; komşusu ayakta kalır.

    Tek kaba mutasyon üç kapıyı birden düşürür ve hangisinin gerçekten
    çalıştığını AYIRT ETMEZ.
    """
    bozuk = _ekle_girdisi(kanit=IKI_KAYNAKLI, kaynak_iddia="K1#404")
    assert "iddia-arastirmada-yok" in _sebepler(engine.run_checks(bozuk))
    with mock.patch.object(engine, "_arastirma_iddialari", lambda inputs: {}):
        # Evren boşalırsa (a) ayağı HER atfı düşürür — kapı gerçekten o
        # evrenden okuyor.
        temiz = _ekle_girdisi(kanit=IKI_KAYNAKLI, kaynak_iddia="K1#1, K2#1")
        assert "iddia-arastirmada-yok" in _sebepler(engine.run_checks(temiz))
    with mock.patch.object(
        engine,
        "_iddia_alani_bagli_mi",
        lambda karar, yol, iddia, takvim=frozenset(): engine.IDDIA_BAGI_VAR,
    ):
        # Alan bağı sökülünce BAŞKA alanın iddiası geçer; (b) ayağı hâlâ ayakta
        # olduğu için sebep `iddia-denetcide-yok`a kayar, karar YİNE uygulanmaz.
        baska = _ekle_girdisi(kanit=IKI_KAYNAKLI, kaynak_iddia="K1#4")
        assert "iddia-denetcide-yok" in _sebepler(engine.run_checks(baska))


# ── Görev B: bağ ALANA değil O DÖNEME kurulur ─────────────────────────────


def _ozel_gun_ekle_girdisi(*, kaynak_iddia: str, donem_adi: str | None = None):
    """`ozel_gun` alanına yeni bir kanca ekleyen karar.

    Denetçi satırı Görev B yazımındadır (`ozel_gun/{dönem}/{başlık}`), araştırma
    iddiası ise DÖNEM ADINI taşır (`Cumhuriyet Bayramı`) — sözleşmenin kendi
    iki ayrı yazımı. Bağ bu yüzden normalizasyonla kurulur.
    """
    aday = _tam_icerik()
    aday["ozel_gun"] = {
        **aday["ozel_gun"],
        YENI_DONEM_ANAHTARI: {
            "tur": "kutlama",
            "mesaj_ekseni": "Hediye secimi ekseni",
            "kanca": "Sevgiliye ozel vitrin",
            "cta": "Hediyenizi secmek icin ugrayin",
            "gorsel_vurgu": "Kirmizi kadife ve altin",
        },
    }
    harita = _kimlik_haritasi(AKTIF_ICERIK, aday)
    yeni_yollar = sorted(
        yol
        for yol in identity.enumerate_content_units(aday)
        if yol.startswith(f"ozel_gun/{YENI_DONEM_ANAHTARI}/")
    )
    assert yeni_yollar, "fixture yeni dönem birimi ÜRETMEDİ"
    tablo = DENETIM_TABLOSU + (
        _denetim_satiri(
            7,
            kaynaklar={1, 2},
            sinif="2-2",
            alan=f"ozel_gun/{YENI_DONEM_ANAHTARI}/kanca",
            kaynak_iddialari={
                auditors.KaynakIddiasi(kaynak=1, iddia=YENI_DONEM_IDDIA_NO),
                auditors.KaynakIddiasi(kaynak=2, iddia=YENI_DONEM_IDDIA_NO),
            },
        ),
    )
    gunluk = _gunluk(
        aday,
        kimlikler=harita,
        degis={
            yol: {
                "karar": "ekle",
                "kanit": "D1#7",
                "kaynak_iddia": kaynak_iddia,
            }
            for yol in yeni_yollar
        },
        denetim=tablo,
    )
    if donem_adi is None:
        mekanik = _gecen_kapi(tablo)
    else:
        # Araştırmanın YAZDIĞI ad değiştirilir; sistem anahtarı aynı kalır.
        iddialar = tuple(
            bd.CIddia(no=iddia.no, alan=donem_adi)
            if iddia.no == YENI_DONEM_IDDIA_NO
            else iddia
            for iddia in _arastirma_iddialari(tablo)
        )
        mekanik = bd.gate_round(
            [
                bd.DoctorReport(
                    sonuc=bd.SONUC_GECTI,
                    notlar=(),
                    elemeler=(),
                    kaynak_adi=ad,
                    icerik_ozeti=_ozet(ad),
                    iddialar=iddialar,
                )
                for ad in (DOGRULANMIS_KAYNAK, IKINCI_KAYNAK)
            ]
        )
    return _girdi(
        icerik=aday,
        gunluk=gunluk,
        cift=_cift(denetim=tablo, kaynak_sha=_kaynak_seti_sha(mekanik)),
        kapi=mekanik,
        takvim=frozenset({TAKVIM_ANAHTARI, YENI_DONEM_ANAHTARI}),
    )


def test_a_special_day_claim_binds_to_that_period() -> None:
    """POZİTİF: dönem adı kararın `oge_yolu` slug'ıyla NORMALİZE eşleşiyor."""
    sonuc = engine.run_checks(
        _ozel_gun_ekle_girdisi(kaynak_iddia=f"K1#{YENI_DONEM_IDDIA_NO}")
    )
    assert sonuc.uygulanmayan_kararlar == ()


def test_a_daily_language_period_name_reports_the_HONEST_reason() -> None:
    """F3 (hakem turu 1, yüksek — ÖLÇÜLDÜ): teşhis doğru yeri göstermeli.

    Araştırma şablonunun ADAY TAKVİMİ dönem adını GÜNLÜK DİLDE yazar
    (`29 Ekim`); sistem takvimi RESMÎ adı taşır (`Cumhuriyet Bayramı` →
    `cumhuriyet-bayrami`). ÖLÇÜLDÜ: `normalize_special_day_key('29 Ekim')` →
    `'29-ekim'` ve şablonun 15 aday adından yalnız 4'ü sistem slug'ına düşüyor.

    Kapı FAIL-CLOSED kalır — uydurma eşleştirme YAPILMAZ, kalıp girmez. Düzelen
    şey TEŞHİSTİR: eskiden `iddia-arastirmada-yok` deniyordu ve bu YANLIŞTI
    (iddia araştırmada VAR; çözülemeyen DÖNEM KİMLİĞİ). Kalıcı kapanış dış
    sözleşme revizyonu ister: Bölüm C dönem satırı kanonik sistem anahtarını
    TAŞIMALIDIR.
    """
    sonuc = engine.run_checks(
        _ozel_gun_ekle_girdisi(
            kaynak_iddia=f"K1#{YENI_DONEM_IDDIA_NO}",
            donem_adi="14 Şubat",
        )
    )
    assert "donem-kimligi-cozulemedi" in _sebepler(sonuc)
    assert "iddia-arastirmada-yok" not in _sebepler(sonuc)


def test_a_known_field_name_is_NOT_diagnosed_as_a_period_problem() -> None:
    """Yeni sebep AŞIRI GENİŞ olmamalı (kapanış turu, orta — iki hakem de buldu).

    `anahtar not in takvim_anahtarlari` yüklemi *"dönem adı mı"* sorusunu DEĞİL
    *"takvimde var mı"* sorusunu cevaplıyor. ÖLÇÜLDÜ: `cta_kaliplari` gibi
    bilinen bir ALAN adı da `donem-kimligi-cozulemedi` etiketi alıyordu — oysa o,
    iki uçlu bağın yakalamak için kurulduğu sentez sapmasının ta kendisi.
    Operatör onu bilinen sözleşme borcu sanıp araştırmayı bırakırdı.
    """
    for alan in ("cta_kaliplari", "kanca_kaliplari", "yasaklar_ve_hassasiyetler"):
        sonuc = engine.run_checks(
            _ozel_gun_ekle_girdisi(
                kaynak_iddia=f"K1#{YENI_DONEM_IDDIA_NO}", donem_adi=alan
            )
        )
        assert "iddia-arastirmada-yok" in _sebepler(sonuc), alan
        assert "donem-kimligi-cozulemedi" not in _sebepler(sonuc), alan
    # POZİTİF KONTROL: gerçek bir dönem adı HÂLÂ dönem teşhisi alır.
    gercek = engine.run_checks(
        _ozel_gun_ekle_girdisi(
            kaynak_iddia=f"K1#{YENI_DONEM_IDDIA_NO}", donem_adi="14 Şubat"
        )
    )
    assert "donem-kimligi-cozulemedi" in _sebepler(gercek)


def test_a_claim_about_another_period_does_not_authorise() -> None:
    """BAŞKA dönemin iddiası bu dönemi yetkilendirmez.

    Bu, kapatılan sınıfın bir basamak aşağısıdır: `ozel_gun` alanına bakan bir
    bağ, `Sevgililer Günü` iddiasını `Cumhuriyet Bayramı` kancasına
    yetkilendirirdi.
    """
    sonuc = engine.run_checks(
        _ozel_gun_ekle_girdisi(kaynak_iddia=f"K1#{MEVCUT_DONEM_IDDIA_NO}")
    )
    assert "iddia-arastirmada-yok" in _sebepler(sonuc)


def test_a_negative_recommendation_blocks_the_addition() -> None:
    """Denetçi `alma` demişse sayı yetse bile kalıp GİRMEZ, açık soru olur."""
    sonuc = engine.run_checks(_ekle_girdisi(kanit=OLUMSUZ_ONERI))
    assert "oneri-olumsuz" in _sebepler(sonuc)
    assert "acik_soru" in _siniflar(sonuc)


def test_a_partially_dangling_reference_list_is_not_applied() -> None:
    """Atıflardan BİRİ bile çözülmüyorsa alan yapısal kanıt TAŞIMAZ.

    Hakem turu 1 (orta): geçerli satır tek başına yetkilendiriyordu ve hatalı
    satır numarası provenanstan sessizce kayboluyordu.
    """
    sonuc = engine.run_checks(_ekle_girdisi(kanit=f"{IKI_KAYNAKLI}, D2#999"))
    assert "referans-yok" in _sebepler(sonuc)


def test_special_day_field_prefix_binds_to_the_decision() -> None:
    """Görev B yazımı (`ozel_gun/{dönem}/{başlık}`) `ozel_gun` kararına BAĞLIDIR.

    Bağ ÖNEK eşleşmesidir ama serbest alt dizge DEĞİLDİR: komşu bir ad
    (`ozel_gunler`) kapsanmaz.
    """
    assert engine._alan_bagi_var("ozel_gun", "ozel_gun/ramazan/kanca") is True
    assert engine._alan_bagi_var("ozel_gun", "ozel_gun") is True
    assert engine._alan_bagi_var("ozel_gun", "ozel_gunler") is False
    assert engine._alan_bagi_var("ozel_gun", "cta_kaliplari") is False
    assert engine._alan_bagi_var("", "ozel_gun") is False


def _pinli_sozlesme(ad: str) -> str:
    """Pinlenmiş sözleşme dosyasını sha256 doğrulayarak okur (fail-closed)."""
    import json

    kok = Path(__file__).resolve().parents[4]
    pin = json.loads(
        (kok / "shared/contracts/research-contracts.pin.json").read_text(
            encoding="utf-8"
        )
    )
    ham = (Path("/root/otomaix-sosyal-medya-arastirmasi") / ad).read_bytes()
    assert hashlib.sha256(ham).hexdigest() == pin["files"][ad], (
        f"{ad} pinden sapmış — sözleşmeden ölçülen bayrak adları doğrulanamaz"
    )
    return ham.decode("utf-8")


def test_every_contract_flag_spelling_is_recognised() -> None:
    """ÜRETİLMİŞ KÜME: sözleşmenin YAZDIĞI her bayrak adı tanınır.

    Sınıf, elle seçilmiş bir örnekle değil sözleşmeden ÜRETİLEN kümeyle
    kapanır. Ölçülen hata şuydu: `_katla` noktasız `ı`'yı katlamıyordu ve
    sözleşmenin kendi yazımı olan `[marka-adı]` · `[kanal-bağımlı]` ·
    `[kaynak-bağımlı]` HİÇBİR bayrak kontrolünde tanınmıyordu — `[marka-adı]`
    gerçek marka adının pakete girmesini engelleyen bayraktır.

    Sözleşmeye yeni bir bayrak eklenip `BAYRAKLAR` güncellenmezse bu test DÜŞER.
    """
    import re

    metin = _pinli_sozlesme("hakem-denetci-gorevi.md")
    blok = re.search(
        r"^BAYRAKLAR \(geçerli olan tümü\):\n(.*?)\n\nÖNERİ:",
        metin,
        re.S | re.M,
    )
    assert blok is not None, "BAYRAKLAR bloğu sözleşmede bulunamadı"
    yazimlar = re.findall(r"^- \[([^\]:]+)", blok.group(1), re.M)
    assert len(yazimlar) == len(engine.BAYRAKLAR), (
        f"sözleşme {len(yazimlar)} bayrak yazıyor, modül {len(engine.BAYRAKLAR)}"
    )
    taninmayan = [
        yazim for yazim in yazimlar if not engine._bayraklar(f"[{yazim}]")
    ]
    assert not taninmayan, f"sözleşmenin yazdığı bayraklar TANINMIYOR: {taninmayan}"


def test_flag_folding_matrix_has_a_negative_arm() -> None:
    """BOŞ-KÜME kontrol kolu: kümede olmayan bir ad TANINMAZ (tarama körü kabul etmiyor)."""
    assert engine._bayraklar("[uydurma-bayrak]") == set()
    assert engine._bayraklar("[]") == set()


def test_an_unconsumed_flag_on_the_typed_row_becomes_an_open_question() -> None:
    """Bayrak SENTEZİN metninde değil, denetçinin TİPLİ sütununda da aranır.

    Kapanış turu (yüksek): `_bayrak_tuketimi` bayrakları `kanit`/`gerekce`
    METNİNDE arıyor; sentez bir bayrağı yazmayı ATLARSA kısıt sessizce
    kayboluyordu — oysa tipli satırda duruyor.
    """
    sonuc = engine.run_checks(_ekle_girdisi(kanit=BAYRAKLI))
    assert "acik_soru" in _siniflar(sonuc)
    detaylar = " ".join(b.detay for b in sonuc.bulgular)
    assert "tüketilmemiş bayrak" in detaylar


def test_the_surviving_flag_does_not_raise_an_open_question() -> None:
    """BOŞ-KÜME kontrol kolu: sağ çıkan TEK bayrak (`kanal-bagimli`) sessizdir."""
    tablo = DENETIM_TABLOSU + (
        _denetim_satiri(
            7,
            kaynaklar={1, 2},
            sinif="2-2",
            bayraklar="[kanal-bagimli: whatsapp_hatti]",
        ),
    )
    sonuc = engine.run_checks(_ekle_girdisi(kanit="D1#7", denetim=tablo))
    assert "acik_soru" not in _siniflar(sonuc)
    assert sonuc.uygulanmayan_kararlar == ()


def test_a_contradiction_row_becomes_an_open_question() -> None:
    """Denetçi `çelişki` dediyse kalıp OTOMATİK GİRMEZ, operatöre çıkar.

    Satır İKİ kaynak taşıyor — yani sayı tabanı KARŞILIYOR. Düşen tek şey
    denetçinin sınıflandırmasıdır; bu sinyal bugüne kadar motora hiç
    ulaşmıyordu.
    """
    sonuc = engine.run_checks(_ekle_girdisi(kanit=CELISKILI))
    assert "celiski" in _sebepler(sonuc)
    assert "acik_soru" in _siniflar(sonuc)


def test_reference_prefixes_match_the_pinned_synthesis_contract() -> None:
    """`D1`/`D2` ön ekleri UYDURULMAZ — pinli sentez sözleşmesinden ölçülür.

    Ön ek rol ADINDAN türetilir (`denetci-1` → `D1`). Sözleşme başka bir yazım
    kullansaydı motorun çözüm tablosu HİÇBİR referansı çözemez ve her `ekle`
    sessizce `referans-yok`'a düşerdi — ölçülmeyen bir tam-ret.
    """
    import json
    import re

    pin = json.loads(
        (
            Path(__file__).resolve().parents[4]
            / "shared/contracts/research-contracts.pin.json"
        ).read_text(encoding="utf-8")
    )
    ad = "hakem-sentez-gorevi.md"
    ham = (Path("/root/otomaix-sosyal-medya-arastirmasi") / ad).read_bytes()
    assert hashlib.sha256(ham).hexdigest() == pin["files"][ad], (
        f"{ad} pinden sapmış — sözleşmeden ölçülen ön ek doğrulanamaz"
    )
    olculen = sorted(set(re.findall(r'"(D\d+)#', ham.decode("utf-8"))))
    turetilen = sorted(
        engine._denetci_onegi(rol) for rol in auditors.DENETCI_ROLLERI
    )
    assert olculen == turetilen, (
        f"sözleşmenin referans ön ekleri {olculen}, motorun türettiği {turetilen}"
    )


def test_both_auditors_references_resolve() -> None:
    """İKİ denetçinin de satırları çözülür — evren tek rapordan üretilmiyor.

    D1 kolu tek başına ölçülseydi, evreni yalnız `cift.birinci`'den kuran bir
    yazım da yeşil kalırdı ve ikinci denetçiye yapılan her atıf sessizce
    `referans-yok`'a düşerdi.
    """
    evren = engine._denetci_satirlari(_ekle_girdisi(kanit=IKI_KAYNAKLI))
    assert {"D1#1", "D2#1"} <= set(evren)

    sonuc = engine.run_checks(_ekle_girdisi(kanit="D2#1"))
    assert sonuc.uygulanmayan_kararlar == ()

    tek = engine.run_checks(_ekle_girdisi(kanit="D2#2"))
    assert "cogunluk-yok" in _sebepler(tek)


def test_a_non_contradiction_row_with_two_sources_emits_no_open_question() -> None:
    """BOŞ-KÜME kontrol kolu: çelişki kapısı her satırı bulguya çevirmiyor."""
    sonuc = engine.run_checks(_ekle_girdisi(kanit=IKI_KAYNAKLI))
    assert "acik_soru" not in _siniflar(sonuc)


# ── K-126 tek-kaynak istisnası: İKİ ayak BİRLİKTE (spec §9.4) ─────────────
#
# İstisna 2026-09-11'e kadar KAPALIYDI ve bu bilinçliydi: resmîlik yargısı
# denetçinin serbest düzyazısına gömülüydü, motor onu göremiyordu ve bir AND
# koşulunun tek ayağını zorlamak istisnayı canlı HER kaynağa açardı. Denetçi
# sözleşmesi 2.2 KAYNAK PROFİLİ'ni tabloya çevirip `resmi` sütununu ekledi;
# yargı artık TİPLİ taşınıyor ve kapı ÇALIŞIYOR.


def _tek_kaynak_girdisi(*, profil_1=None, profil_2=None, ornekle=None):
    """Tek kaynaklı `ekle` (D1#2, yalnız `KAYNAK-1`) — çoğunluk tabanın ALTINDA."""
    return _ekle_girdisi(
        kanit=TEK_KAYNAKLI,
        profil_1=profil_1,
        profil_2=profil_2,
        ornekle=ornekle,
    )


def test_single_source_exception_opens_when_both_legs_hold() -> None:
    """POZİTİF: kaynak RESMÎ + canlı URL doğrulaması → kalıp GİRER."""
    sonuc = engine.run_checks(
        _tek_kaynak_girdisi(profil_1=_profil(True, False), profil_2=_profil(True, False))
    )
    assert sonuc.uygulanmayan_kararlar == ()


def test_single_source_exception_stays_closed_without_officiality() -> None:
    """İkinci ayak TEK BAŞINA yetmez: canlı URL resmîlik KANITI değildir."""
    sonuc = engine.run_checks(_tek_kaynak_girdisi())
    assert "cogunluk-yok" in _sebepler(sonuc)


def test_single_source_exception_stays_closed_without_a_live_url() -> None:
    """Birinci ayak TEK BAŞINA da yetmez — AND koşulunun öteki yarısı ölçülür."""
    olu = engine.run_checks(
        _tek_kaynak_girdisi(
            profil_1=_profil(True, False),
            profil_2=_profil(True, False),
            ornekle=_ornekle(uyumlu=False),
        )
    )
    assert "cogunluk-yok" in _sebepler(olu)
    erisilemeyen = engine.run_checks(
        _tek_kaynak_girdisi(
            profil_1=_profil(True, False),
            profil_2=_profil(True, False),
            ornekle=_ornekle(erisildi=False),
        )
    )
    assert "cogunluk-yok" in _sebepler(erisilemeyen)


def test_a_contested_officiality_judgement_does_not_open_the_exception() -> None:
    """ÇEKİŞMELİ yargı istisnayı AÇMAZ — fail-closed.

    Bir denetçi `evet`, öteki `hayır` diyorsa yargı çekişmelidir. Sözleşme
    *"emin değilsen `hayır` yaz — iyimser doldurma kapıyı sessizce açar"* der;
    şüpheyi iyimserlikle susturmak o hükmü tersine çevirirdi. Nicelik ayrımı
    UYDURMA değil: spec ikinci ayak için AÇIKÇA "en az bir denetçi" der,
    birinci ayak için demez.
    """
    sonuc = engine.run_checks(
        _tek_kaynak_girdisi(
            profil_1=_profil(True, False), profil_2=_profil(False, False)
        )
    )
    assert "cogunluk-yok" in _sebepler(sonuc)


def test_a_missing_profile_row_from_one_auditor_closes_the_exception() -> None:
    """F5 (hakem turu 1, yüksek — ÖLÇÜLDÜ): satırı YAZMAMAK şüpheyi susturamaz.

    İlk yazım yargıları iki raporun satırlarından TOPLUYOR ve "yazan herkes
    evet demiş olmalı" diyordu. Ölçüldü: bir denetçi o kaynak için satırı hiç
    yazmazsa liste `[evet]` kalıyor, `all()` geçiyor ve istisna AÇILIYORDU —
    docstring'in kapattığını söylediği şeyin ta kendisi. Hiçbir katman profilin
    HER kaynağı kapsadığını ölçmüyor (`_kaynak_profili` bunu R6 kapsam sınırı
    olarak açıkça beyan eder), o yüzden kapı MOTORDA kuruldu.
    """
    # D2 kaynak-1 için satır HİÇ YOK (yalnız kaynak-2 profillenmiş).
    eksik = engine.run_checks(
        _tek_kaynak_girdisi(
            profil_1=_profil(True, False),
            profil_2=(
                auditors.KaynakProfili(kaynak=2, resmi=False, not_metni="Not."),
            ),
        )
    )
    assert "cogunluk-yok" in _sebepler(eksik)
    # POZİTİF KONTROL: iki rapor da o kaynağı profillerse istisna AÇILIR.
    tam = engine.run_checks(
        _tek_kaynak_girdisi(
            profil_1=_profil(True, False), profil_2=_profil(True, False)
        )
    )
    assert tam.uygulanmayan_kararlar == ()


def test_a_duplicated_profile_row_does_not_open_the_exception() -> None:
    """Aynı kaynağa İKİ yargı da kapıyı açmaz — kimlik tek olmalı.

    Rapor düzeyinde tekrar zaten reddedilir; motor kapısı o katmana GÜVENMEZ
    (tek yerde tutulan değişmez, o yer değişince sessizce kaybolur).
    """
    sonuc = engine.run_checks(
        _tek_kaynak_girdisi(
            profil_1=(
                auditors.KaynakProfili(kaynak=1, resmi=True, not_metni="A."),
                auditors.KaynakProfili(kaynak=1, resmi=True, not_metni="B."),
            ),
            profil_2=_profil(True, False),
        )
    )
    assert "cogunluk-yok" in _sebepler(sonuc)


def test_an_absent_officiality_judgement_does_not_open_the_exception() -> None:
    """Yargı HİÇ yazılmamışsa istisna AÇILMAZ — sessizlik `evet` değildir."""
    sonuc = engine.run_checks(
        _tek_kaynak_girdisi(profil_1=(), profil_2=())
    )
    assert "cogunluk-yok" in _sebepler(sonuc)


def test_the_exception_does_not_apply_to_a_two_source_addition() -> None:
    """BOŞ-KÜME kontrol kolu: istisna yalnız TEK kaynaklı kolda çağrılır.

    İki kaynaklı ekleme zaten tabanı karşılar; istisna oraya hiç uğramaz —
    yoksa kapı "her şeyi geçiriyor" hâliyle de yeşil görünürdü.
    """
    assert engine._tek_kaynak_istisnasi(
        _tek_kaynak_girdisi(
            profil_1=_profil(True, False), profil_2=_profil(True, False)
        ),
        {"KAYNAK-1", "KAYNAK-2"},
    ) is False


# ═══ 11. Kontrol: bayrak tüketimi ═════════════════════════════════════════


# ── K-03: paket tür etiketi ↔ SİSTEM KATEGORİSİ (spec §11.2) ──────────────


def _kategorili_girdi(*, paket_turu: str, kategori: str):
    """Özel günün tür etiketi ve sistem kategorisi AYRI AYRI kurulur."""
    aday = _tam_icerik()
    gun = dict(aday["ozel_gun"][TAKVIM_ANAHTARI])
    gun["tur"] = paket_turu
    aday["ozel_gun"] = {TAKVIM_ANAHTARI: gun}
    return _girdi(
        icerik=aday,
        gunluk=_gunluk(aday, kimlikler=_kimlik_haritasi(AKTIF_ICERIK, aday)),
        kategoriler={TAKVIM_ANAHTARI: kategori},
    )


def _catismalar(sonuc) -> tuple:
    return sonuc.olcumler["kategori_cakismalari"]


# ÜRETİLMİŞ MATRİS: iki sözlüğün ORTAK ekseni (ticari mi değil mi) üstünde TAM
# çarpım. Elle seçilmiş örnek, kuralın çift yönlü olduğunu KANITLAMAZ.
_KATEGORI_MATRISI = tuple(
    (kategori, tur, (kategori == "commercial") != (tur == "ticari-firsat"))
    for kategori in ("commercial", "national", "religious")
    for tur in ("ticari-firsat", "kutlama", "anma")
)


@pytest.mark.parametrize(
    "kategori,tur,catisir",
    _KATEGORI_MATRISI,
    ids=[f"{k}-{t}" for k, t, _ in _KATEGORI_MATRISI],
)
def test_tur_kategori_catismasi_iki_yonlu_olculur(
    kategori: str, tur: str, catisir: bool
) -> None:
    """Çelişki ÇİFT YÖNLÜDÜR — kural 'ikisi çeliştiğinde' der, yön seçmez."""
    sonuc = engine.run_checks(_kategorili_girdi(paket_turu=tur, kategori=kategori))
    assert bool(_catismalar(sonuc)) is catisir, _catismalar(sonuc)


def test_tur_kategori_matrisi_iki_kolu_da_tasiyor() -> None:
    """TABAN: matris hem çelişen hem çelişmeyen vaka üretiyor mu?"""
    assert len(_KATEGORI_MATRISI) == 9
    assert sum(1 for *_, c in _KATEGORI_MATRISI if c) == 4
    assert sum(1 for *_, c in _KATEGORI_MATRISI if not c) == 5


@pytest.mark.parametrize("kategori", ["commercial", "national", "religious"])
def test_karma_tur_hicbir_kategoriyle_catismaz(kategori: str) -> None:
    """`karma` iki ekseni birden taşır — hiçbir kategoriyle çelişemez."""
    sonuc = engine.run_checks(_kategorili_girdi(paket_turu="karma", kategori=kategori))
    assert _catismalar(sonuc) == ()


def test_kategorisiz_gun_hakkinda_hicbir_sey_iddia_edilmez() -> None:
    """Etiketsiz gün davranışı K-15(a) kapsamında AÇIK — burada uydurulmaz."""
    sonuc = engine.run_checks(_kategorili_girdi(paket_turu="ticari-firsat", kategori=""))
    assert _catismalar(sonuc) == ()


def test_tur_kategori_catismasi_KOSUYU_BLOKLAMAZ() -> None:
    """K-03 çatışması UÇTAN UCA bloklamamalı — hakem turu 1, F1 (critical).

    **Bu test `decide()` yolunu koşar, `run_checks()` değil** — ve sebebi
    ölçülmüştür: ilk yazım çatışmayı bir NOT satırıyla kaydediyordu, o sınıf
    DIŞ SÖZLEŞMEDE kapalı kümenin dışındaydı, `decide()` kendi ürettiği günlüğü
    doğruladığı için sonuç `blocked` oluyordu. Yani her çatışma paketi
    DÜŞÜRÜYORDU — K-03'ün hükmünün TAM TERSİ. `run_checks` bunu GÖREMEZ:
    notu üretmek onu geçerli kılmaz, son montaj kapısı reddeder.

    Emsal bu dosyada zaten duruyordu (`test_notes_pass_the_decision_log_schema`)
    ve yeni sınıfa uygulanmamıştı; sınıf artık uçtan uca kapanıyor.
    """
    girdi = _kategorili_girdi(paket_turu="ticari-firsat", kategori="national")
    sonuc = engine.decide(girdi, PolicyConfig())
    assert sonuc.sonuc != "blocked", sonuc.sebep
    assert sonuc.final_decision_log is not None
    assert sonuc.final_candidate is not None
    # Çatışma KAYBOLMUYOR: ölçüm olarak koşunun diff'ine geçer.
    assert sonuc.engine_diff["kategori_cakismalari"], sonuc.engine_diff


def test_tur_kategori_catismasi_olcum_olarak_tasinir() -> None:
    """Çatışmanın İÇERİĞİ ölçümde tam — anahtar, paket türü, sistem kategorisi."""
    sonuc = engine.run_checks(
        _kategorili_girdi(paket_turu="ticari-firsat", kategori="national")
    )
    catisma = _catismalar(sonuc)
    assert len(catisma) == 1, catisma
    assert catisma[0] == {
        "anahtar": TAKVIM_ANAHTARI,
        "paket_turu": "ticari-firsat",
        "sistem_kategorisi": "national",
    }
    # Paket türü ÜSTÜNDÜR: hiçbir karar bu yüzden uygulanmaz hâle gelmez.
    assert sonuc.uygulanmayan_kararlar == ()


def test_motorun_urettigi_her_NOT_sinifi_KAPALI_kumeden_gelir() -> None:
    """SINIF KAPANIŞI: kapı elle seçilmiş örnekle değil, ÜRETİLMİŞ kümeyle.

    F1 tek bir not sınıfının kaçak olmasıydı; kapanış "o sınıfı kaldırdım"
    değil, "motorun ürettiği HER sınıf sözleşmenin kümesindedir" olmalıdır —
    yoksa yarın eklenen dördüncü sınıf aynı deliği yeniden açar.
    """
    girdiler = [
        _kategorili_girdi(paket_turu="ticari-firsat", kategori="national"),
        _kategorili_girdi(paket_turu="kutlama", kategori="commercial"),
        _girdi(takvim=frozenset()),
        _ekle_girdisi(kanit=IKI_KAYNAKLI, kaynak_iddia="K1#1, K2#1"),
        _ekle_girdisi(kanit=TEK_KAYNAKLI, kaynak_iddia="K1#2"),
    ]
    gorulen: set[str] = set()
    for girdi in girdiler:
        for not_satiri in engine.run_checks(girdi).notlar:
            gorulen.add(not_satiri["sinif"])
    assert gorulen, "hiç not üretilmedi — tarama hiçbir şey kanıtlamıyor"
    assert gorulen <= identity.NOT_SINIFLARI, (
        f"motor sözleşmenin kapalı kümesi dışında not sınıfı üretti: "
        f"{sorted(gorulen - identity.NOT_SINIFLARI)}"
    )


def test_tur_revizyonu_kategori_catismasindan_AYRI_olculur() -> None:
    """İki ölçüm ayrı adlandırılır çünkü ayrı şeylerdir (checkpoint 9, orta)."""
    sonuc = engine.run_checks(
        _kategorili_girdi(paket_turu="ticari-firsat", kategori="national")
    )
    assert sonuc.olcumler["paket_turu_degisiklikleri"], "tür revizyonu ölçülmedi"
    assert _catismalar(sonuc), "kategori çatışması ölçülmedi"
    assert (
        sonuc.olcumler["paket_turu_degisiklikleri"] != _catismalar(sonuc)
    )


def test_unconsumed_flag_becomes_an_open_question() -> None:
    """Sentezden sağ çıkmaması gereken bayrak motora ulaşırsa AÇIK SORUDUR."""
    sonuc = engine.run_checks(
        _ekle_girdisi(
            kanit=f"{DOGRULANMIS_KAYNAK}, {IKINCI_KAYNAK} [kopya-şüphesi]"
        )
    )
    assert "acik_soru" in _siniflar(sonuc)


def test_channel_flag_survives_without_a_finding() -> None:
    """POZİTİF: `[kanal-bagimli: X]` sentezden sağ çıkan TEK bayraktır."""
    aday = _tam_icerik(
        cta_kaliplari=[
            {
                "kalip": "Magazamiza bekleriz [kanal-bagimli: fiziksel_magaza]",
                "tur": "ziyaret",
                "gerekce": "Kanal etiketi tasinir.",
            }
        ]
    )
    harita = _kimlik_haritasi(AKTIF_ICERIK, aday)
    sonuc = engine.run_checks(
        _girdi(icerik=aday, gunluk=_gunluk(aday, kimlikler=harita))
    )
    assert "acik_soru" not in _siniflar(sonuc)


# ═══ 12. Kontrol: geri-ekleme çelişkisi (K-122) ═══════════════════════════


def test_readd_conflict_emits_acik_soru_finding() -> None:
    """Çıkarılanlar listesiyle eşleşen aday açık soru DOĞURUR."""
    sonuc = engine.run_checks(
        _ekle_girdisi(
            kanit=f"{DOGRULANMIS_KAYNAK}, {IKINCI_KAYNAK}",
            metin="Geri gelen kanca",
            cikarmalar=(
                {
                    "unit_id": "ku-ffffffffffff",
                    "alan": "kanca_kaliplari",
                    "deger": "Geri gelen kanca",
                    "gerekce": "Onceki turda cikarildi.",
                },
            ),
        )
    )
    assert "acik_soru" in _siniflar(sonuc)


def test_new_item_unrelated_to_removals_emits_no_finding() -> None:
    """POZİTİF: çıkarılanlar listesiyle eşleşmeyen aday açık soru üretmez."""
    sonuc = engine.run_checks(
        _ekle_girdisi(
            kanit=f"{DOGRULANMIS_KAYNAK}, {IKINCI_KAYNAK}",
            cikarmalar=(
                {
                    "unit_id": "ku-ffffffffffff",
                    "alan": "kanca_kaliplari",
                    "deger": "Baska bir kalip",
                    "gerekce": "Onceki turda cikarildi.",
                },
            ),
        )
    )
    assert "acik_soru" not in _siniflar(sonuc)


# ═══ 12b. Bulgunun ÜRETİCİSİ — atıf (Task 14 önkoşulu) ════════════════════
#
# Task 14'ün bağlayıcı sıralama invariantı (K-42) riskli sınıfları ADIYLA
# ayırır: geri-ekleme çelişkileri · motor kararsızları · çıkarmalar. `sinif`
# bunu ayırt ETMEZ — `acik_soru` sınıfını BEŞ ayrı kontrol üretiyor (ölçüldü).
# Onay yüzeyinin bunu `detay` metnini eşleştirerek çözmesi referans bütünlüğü
# olmayan bir bağ olurdu (İlke 1). Bu yüzden atıf, bulguyu TOPLAYAN yerde
# damgalanır: tek yazıcı `run_checks`, değer `EngineCheck.ad`.


def test_finding_carries_the_check_that_produced_it() -> None:
    """Geri-ekleme çelişkisi bulgusu, onu üreten kontrolün adını TAŞIR."""
    sonuc = engine.run_checks(
        _ekle_girdisi(
            kanit=f"{DOGRULANMIS_KAYNAK}, {IKINCI_KAYNAK}",
            metin="Geri gelen kanca",
            cikarmalar=(
                {
                    "unit_id": "ku-ffffffffffff",
                    "alan": "kanca_kaliplari",
                    "deger": "Geri gelen kanca",
                    "gerekce": "Onceki turda cikarildi.",
                },
            ),
        )
    )
    atifli = [b for b in sonuc.bulgular if b.kontrol == "geri_ekleme_celiskisi"]
    assert [b.sinif for b in atifli] == ["acik_soru"]


def test_every_finding_is_attributed_to_a_real_check() -> None:
    """Her bulgunun atfı GERÇEK bir kontrol adıdır — boş atıf yok."""
    sonuc = engine.run_checks(
        _ekle_girdisi(
            kanit=DOGRULANMIS_KAYNAK,
            metin="Geri gelen kanca",
            cikarmalar=(
                {
                    "unit_id": "ku-ffffffffffff",
                    "alan": "kanca_kaliplari",
                    "deger": "Geri gelen kanca",
                    "gerekce": "Onceki turda cikarildi.",
                },
            ),
        )
    )
    assert sonuc.bulgular, "senaryo bulgu üretmedi — test konusunu ölçemez"
    assert {b.kontrol for b in sonuc.bulgular} <= set(BEKLENEN_KONTROL_ADLARI)
    assert all(b.kontrol for b in sonuc.bulgular)


def test_collector_stamps_attribution_for_any_check(monkeypatch) -> None:
    """SINIF KAPANIŞI: atıf tek tek kontrollere değil TOPLAYICIYA yazılıdır.

    Üretilmiş kol — kontrol kümesine sonradan eklenen HERHANGİ bir kontrol de
    atfını alır; kendi gövdesinde `kontrol=` yazması GEREKMEZ. Aksi tasarımda
    her yeni kontrol atfı unutabilirdi ve onay yüzeyi sessizce sınıf kaybederdi.
    """
    uydurma = engine.EngineCheck(
        ad="sema_ve_boyut",
        aciklama="test kolu",
        calistir=lambda _girdi: engine.CheckOutput(
            bulgular=(
                engine.BulguIzi(sinif="acik_soru", unit_id=None, detay="test bulgusu"),
            )
        ),
    )
    monkeypatch.setattr(engine, "CHECKS", (uydurma,))
    sonuc = engine.run_checks(_girdi())
    assert [b.kontrol for b in sonuc.bulgular] == ["sema_ve_boyut"]


def test_unrelated_finding_is_not_attributed_to_readd_check() -> None:
    """NEGATİF KONTROL: başka kontrolün bulgusu geri-ekleme atfı ALMAZ."""
    hedef = _yol(AKTIF_ICERIK, "kapsam", AKTIF_ICERIK["kapsam"])
    gunluk = _gunluk(AKTIF_ICERIK, degis={hedef: {"unit_id": "ku-aaaaaaaaaaaa"}})
    sonuc = engine.run_checks(_girdi(gunluk=gunluk))
    assert sonuc.bulgular, "senaryo bulgu üretmedi — negatif kontrol anlamsız olur"
    assert "kapsam_ihlali" in _siniflar(sonuc)
    assert all(b.kontrol != "geri_ekleme_celiskisi" for b in sonuc.bulgular)


def test_check_body_may_not_forge_its_own_attribution(monkeypatch) -> None:
    """FAIL-CLOSED: kontrol gövdesi kendi atfını UYDURAMAZ.

    Atfı gövdenin yazabilmesi, bir bulgunun onay yüzeyinde BAŞKA bir riskli
    sınıf gibi görünmesine izin verirdi (sessiz sınıf kayması). Toplayıcı
    çelişkiyi sessizce EZMEZ, DURUR.
    """
    uydurma = engine.EngineCheck(
        ad="sema_ve_boyut",
        aciklama="test kolu",
        calistir=lambda _girdi: engine.CheckOutput(
            bulgular=(
                engine.BulguIzi(
                    sinif="acik_soru",
                    unit_id=None,
                    detay="test bulgusu",
                    kontrol="geri_ekleme_celiskisi",
                ),
            )
        ),
    )
    monkeypatch.setattr(engine, "CHECKS", (uydurma,))
    with pytest.raises(engine.EngineInputError, match="atıf"):
        engine.run_checks(_girdi())


def test_no_findings_yields_no_attributions() -> None:
    """BOŞ-KÜME KOLU: bulgu yoksa damgalama da bir şey uydurmaz."""
    sonuc = engine.run_checks(_girdi())
    assert [b for b in sonuc.bulgular if b.sinif == "acik_soru"] == []


# ═══ 13. Kontrol: kategori çakışması (K-03) ═══════════════════════════════


def test_package_type_change_is_recorded_and_never_blocks() -> None:
    """K-03'ün ölçülebilen ayağı: tür etiketi DEĞİŞİMİ kaydedilir, blok YOK.

    Kategori ayağı girdide olmadığı için ölçüm adı da onu iddia ETMEZ (checkpoint 9).
    """
    aday = _tam_icerik(
        ozel_gun={
            TAKVIM_ANAHTARI: {
                **AKTIF_ICERIK["ozel_gun"][TAKVIM_ANAHTARI],
                "tur": "anma",
            }
        }
    )
    harita = _kimlik_haritasi(AKTIF_ICERIK, aday)
    tur_yolu = f"ozel_gun/{TAKVIM_ANAHTARI}/tur"
    gunluk = _gunluk(
        aday,
        kimlikler=harita,
        degis={tur_yolu: {"karar": "guncelle", "kanit": DOGRULANMIS_KAYNAK}},
    )
    sonuc = engine.run_checks(
        _girdi(
            icerik=aday,
            gunluk=gunluk,
            cift=_cift(
                statuler_1={harita[tur_yolu]: "needs_update"},
                statuler_2={harita[tur_yolu]: "needs_update"},
            ),
        )
    )
    degisiklikler = sonuc.olcumler["paket_turu_degisiklikleri"]
    assert degisiklikler and degisiklikler[0]["anahtar"] == TAKVIM_ANAHTARI
    assert degisiklikler[0]["paket_turu"] == "anma"
    assert sonuc.bulgular == ()


def test_matching_type_label_records_no_change() -> None:
    """POZİTİF: tür etiketi değişmediyse kayıt YOKTUR."""
    sonuc = engine.run_checks(_girdi())
    assert sonuc.olcumler["paket_turu_degisiklikleri"] == ()


# ═══ 14. Kontrol: özel gün anahtarı ═══════════════════════════════════════


def test_unmatched_holiday_key_emits_note() -> None:
    """Takvimde karşılığı olmayan anahtar NOT üretir; uydurma anahtar yazılmaz."""
    sonuc = engine.run_checks(_girdi(takvim=frozenset()))
    siniflar = [not_satiri["sinif"] for not_satiri in sonuc.notlar]
    assert "eslesmeyen-ozel-gun" in siniflar


def test_matched_holiday_key_emits_no_note() -> None:
    """POZİTİF: takvimde karşılığı olan anahtar not üretmez."""
    sonuc = engine.run_checks(_girdi())
    assert sonuc.notlar == ()


# ═══ 15. Kontrol: diff sayıları (K-24) ════════════════════════════════════


def test_diff_counts_are_measured() -> None:
    """Ham dağılım her koşuda ÖLÇÜLÜR — değer üretilmez, sayılır."""
    sonuc = engine.run_checks(_girdi())
    assert sonuc.olcumler["diff"]["koru"] == len(AKTIF_BIRIMLER)
    assert sonuc.olcumler["diff"]["guncelle"] == 0


def test_diff_counts_follow_the_log() -> None:
    """NEGATİF KONTROL: günlük değişince sayım da değişir (sabit değer değil)."""
    sonuc = engine.run_checks(
        _guncelle_girdisi(
            alan="kanca_kaliplari",
            eski=KORUNAN_KANCA,
            yeni_metin="Guncellenmis kanca kalibi",
            kanit=DOGRULANMIS_KAYNAK,
            statuler_1=MUTABIK,
            statuler_2=MUTABIK,
        )
    )
    assert sonuc.olcumler["diff"]["guncelle"] == 1
    assert sonuc.olcumler["diff"]["koru"] == len(AKTIF_BIRIMLER) - 1


# ═══ 16. Kontrol: regresyon kapısı ve tek-aktif ön kontrolü ═══════════════


def test_regression_gate_failure_emits_finding() -> None:
    """Katman-1 geçmemişse bulgu doğar (spec §9.1: zorunlu kapı)."""
    sonuc = engine.run_checks(
        _girdi(kapilar=engine.GateResults(katman1_passed=False, tek_aktif_ihlali=False))
    )
    assert "regresyon_kapisi" in _siniflar(sonuc)


def test_regression_gate_pass_emits_no_finding() -> None:
    """POZİTİF: kapı geçtiyse bulgu YOK."""
    sonuc = engine.run_checks(_girdi())
    assert "regresyon_kapisi" not in _siniflar(sonuc)


def test_second_active_precheck_emits_finding() -> None:
    """Tek-aktif ön kontrolü ihlal edilmişse bulgu doğar."""
    sonuc = engine.run_checks(
        _girdi(kapilar=engine.GateResults(katman1_passed=True, tek_aktif_ihlali=True))
    )
    assert "ikinci_aktif" in _siniflar(sonuc)


def test_clean_precheck_emits_no_finding() -> None:
    """POZİTİF: ihlal yoksa bulgu YOK."""
    sonuc = engine.run_checks(_girdi())
    assert "ikinci_aktif" not in _siniflar(sonuc)


# ═══ 17. Girdi kapıları: durmuş tur ve doğrulanmamış envanter ═════════════


def test_stopped_mechanical_round_fails_closed() -> None:
    """K-127 ile DURMUŞ turda motor koşmaz — sessiz devam YOK."""
    duran = bd.gate_round(
        [
            bd.DoctorReport(
                sonuc=bd.SONUC_GECTI,
                notlar=(),
                elemeler=(),
                kaynak_adi=DOGRULANMIS_KAYNAK,
                icerik_ozeti=_ozet(DOGRULANMIS_KAYNAK),
            )
        ]
    )
    assert duran.dur is True
    with pytest.raises(engine.EngineInputError, match="mekanik eleme"):
        engine.run_checks(_girdi(kapi=duran))


def _kapi_kaynaklarla(adlar: tuple[str, ...]) -> bd.RoundGate:
    """Verilen kaynak adlarıyla GEÇEN bir mekanik kapı kurar."""
    return bd.gate_round(
        [
            bd.DoctorReport(
                sonuc=bd.SONUC_GECTI,
                notlar=(),
                elemeler=(),
                kaynak_adi=ad,
                icerik_ozeti=_ozet(ad),
            )
            for ad in adlar
        ]
    )


def test_engine_rejects_a_mechanical_gate_from_another_run() -> None:
    """Başka bir koşunun mekanik kapısı motora GİREMEZ.

    Kör kaynak etiketi (`KAYNAK-1/2/3`) kapının rapor SIRASINDAN türer; başka
    bir koşunun kapısı verilirse aynı etiket başka bir kaynağı gösterir ve
    yapısal çoğunluk sessizce yanlış kaynaklara dayanır. Bağ, motorun girdi
    alan kümesi AÇILMADAN kurulur: kimlik paketten doğar ve denetçi çifti taşır.
    """
    baska = _kapi_kaynaklarla(("baska-kaynak-bir", "baska-kaynak-iki"))
    with pytest.raises(ValueError, match="BU denetçi paketine ait değil"):
        engine.EngineInputs(
            sentez=_sonuc(AKTIF_ICERIK, _gunluk(AKTIF_ICERIK)),
            aktif_paket=_aktif_paket(),
            aktif_schema_version=1,
            aktif_birimler=AKTIF_BIRIMLER,
            mevcut_birim_sayisi=len(AKTIF_BIRIMLER),
            ilk_kosu=False,
            son_turlarin_cikarmalari=(),
            denetci_envanterleri=_cift(),          # varsayılan kapının kimliği
            mekanik_eleme=baska,                   # BAŞKA koşunun kapısı
            takvim_anahtarlari=frozenset({TAKVIM_ANAHTARI}),
            takvim_kategorileri={TAKVIM_ANAHTARI: SISTEM_KATEGORISI},
            otomatik_kapilar=engine.GateResults(
                katman1_passed=True, tek_aktif_ihlali=False
            ),
        )


def test_engine_accepts_the_gate_that_built_the_packet() -> None:
    """BOŞ-KÜME kontrol kolu: doğru kapı GEÇER — kapı her şeyi reddetmiyor."""
    girdi = _girdi()
    assert girdi.mekanik_eleme is not None
    assert (
        girdi.denetci_envanterleri.kaynak_seti_sha
        == _kaynak_seti_sha(girdi.mekanik_eleme)
    )


_KAYNAK_KIMLIGI_EKSENLERI = {
    "sira": (("b", "a"), {}),
    "ad": (("a", "c"), {}),
    "icerik": (("a", "b"), {"ozet": {"b": "farkli-icerik"}}),
    "eleme": (("a", "b"), {"elenen": "b"}),
    # Asagidaki iki eksen `sonuc`u DEGISTIRMEZ: ayrim yalniz BULGU METNINDEDIR.
    # Ilk yazim yalniz ad/ozet/sonuc hash'liyordu ve bu ikisini AYIRT ETMIYORDU;
    # oysa iki alan da EK-E'ye yazilir, yani denetcinin GORDUGU sey degisir.
    "not-metni": (("a", "b"), {"not_mesaji": {"b": "bambaska not"}}),
    "eleme-metni": (("a", "b"), {"elenen": "b", "eleme_mesaji": "bambaska eleme"}),
}


@pytest.mark.parametrize("eksen", sorted(_KAYNAK_KIMLIGI_EKSENLERI))
def test_source_set_identity_is_sensitive_on_every_axis(eksen: str) -> None:
    """ÜRETİLMİŞ MATRİS: kimlik SIRA · AD · İÇERİK · ELEME eksenlerinde ayrışır.

    Dördü de bir sebeple girer: sıra kör etiketin hangi kaynağa düştüğünü
    belirler, ad kimliği, içerik metni, eleme ise motorun kabul ettiği etiket
    kümesini. Biri hash'e girmezse o eksende iki ayrı koşu AYNI kimliği taşır.
    """
    adlar, sapma = _KAYNAK_KIMLIGI_EKSENLERI[eksen]

    def _rapor_kur(
        ad: str,
        *,
        ozetler: dict,
        elenen: str | None,
        not_mesajlari: dict | None = None,
        eleme_mesaji: str = "elenmis kaynak",
    ) -> bd.DoctorReport:
        elendi = ad == elenen
        notlar = ()
        not_mesaji = (not_mesajlari or {}).get(ad)
        if not_mesaji is not None:
            notlar = (
                bd.Bulgu(
                    kontrol="sahte-kontrol",
                    aile="bolum-ve-alan-tamligi",
                    seviye=bd.SEVIYE_NOT,
                    mesaj=not_mesaji,
                ),
            )
        elemeler = (
            (
                bd.Bulgu(
                    kontrol="sahte-kontrol",
                    aile="bolum-ve-alan-tamligi",
                    seviye=bd.SEVIYE_ELEME,
                    mesaj=eleme_mesaji,
                ),
            )
            if elendi
            else ()
        )
        return bd.DoctorReport(
            sonuc=bd.sonuc_belirle(notlar, elemeler),
            notlar=notlar,
            elemeler=elemeler,
            kaynak_adi=ad,
            icerik_ozeti=_ozet(ozetler.get(ad, ad)),
        )

    # TABAN sapmasızdır; sapma YALNIZ karşılaştırılan tarafa uygulanır.
    # Metin eksenlerinde taban da aynı YAPIDAdır (not/eleme VAR) — ayrım
    # yalnız METİNDEDİR, yoksa `sonuc` farkı ölçümü kirletirdi.
    # Taban, eksenin DEĞİŞTİRDİĞİ şey dışında sapan tarafla AYNI YAPIDA olmalı.
    # `eleme` ekseninde değişen şey elemenin KENDİSİdir → taban elemesizdir.
    # `eleme-metni` ekseninde değişen şey yalnız MESAJdır → taban da elenmiştir,
    # yoksa ayrım `sonuc` farkından gelir ve mesaj ekseni ÖLÇÜLMEMİŞ olur.
    taban_sapmasi: dict = {
        "elenen": sapma.get("elenen") if "eleme_mesaji" in sapma else None
    }
    if "not_mesaji" in sapma:
        taban_sapmasi["not_mesajlari"] = {ad: "taban not" for ad in sapma["not_mesaji"]}
    taban = bd.kaynak_seti_sha(
        [
            _rapor_kur(ad, ozetler={}, **taban_sapmasi)
            for ad in ("a", "b")
        ]
    )
    sapan = bd.kaynak_seti_sha(
        [
            _rapor_kur(
                ad,
                ozetler=sapma.get("ozet", {}),
                elenen=sapma.get("elenen"),
                not_mesajlari=sapma.get("not_mesaji"),
                **(
                    {"eleme_mesaji": sapma["eleme_mesaji"]}
                    if "eleme_mesaji" in sapma
                    else {}
                ),
            )
            for ad in adlar
        ]
    )
    assert taban != sapan, f"{eksen} ekseninde kimlik AYRIŞMIYOR"


def test_source_set_identity_matrix_has_an_identical_arm() -> None:
    """BOŞ-KÜME kontrol kolu: aynı küme AYNI kimliği verir (hash rastgele değil)."""
    kapi = _kapi_kaynaklarla(("a", "b"))
    assert _kaynak_seti_sha(kapi) == _kaynak_seti_sha(_kapi_kaynaklarla(("a", "b")))


def test_engine_consumes_only_validated_inventory() -> None:
    """Motorun gördüğü envanter YALNIZ doğrulanmış çiftten gelir."""
    girdi = _girdi()
    assert girdi.denetci_envanterleri.unit_snapshot_sha == AKTIF_GORUNTU_SHA
    kimlikler = {
        satir.unit_id for satir in girdi.denetci_envanterleri.birinci.yeniden_dogrulama
    }
    assert kimlikler == set(AKTIF_BIRIMLER)



# ═══ 18. Checkpoint 9 fix'lerinin kendi kapıları ══════════════════════════
#
# Bu bölüm hakem turunda ÖLÇÜLEN beş fail-open/fail-closed kırığını çiviler.
# Her biri düzeltmeden ÖNCE kırmızıydı; mutasyon kaydı
# `docs/research/2026-08-27-motor-mutasyon-olcumu.md`'dedir.


def test_stale_audit_pair_is_rejected() -> None:
    """F1: çift BU aktif görüntüye ait değilse motora GİREMEZ (R6 sınırı).

    Kimlikler kalıcı olduğu için bayat statüler değişmiş içeriğe cevap verir;
    `ValidatedAuditPair` yalnız iki raporun BİR görüntüde uyuştuğunu kanıtlar,
    o görüntünün BU çağrının görüntüsü olduğunu kanıtlamaz.
    """
    degisik = _tam_icerik(kapsam="Degismis kapsam metni.")
    gunluk = _gunluk(degisik, kimlikler=_kimlik_haritasi(AKTIF_ICERIK, degisik))
    birimler = identity.decision_units(degisik, gunluk)
    with pytest.raises(ValueError, match="aktif görüntüye ait değil"):
        engine.EngineInputs(
            sentez=_sonuc(degisik, gunluk),
            aktif_paket={"schema_version": 1, "content": degisik, "decision_log": gunluk},
            aktif_schema_version=1,
            aktif_birimler=birimler,
            mevcut_birim_sayisi=len(birimler),
            ilk_kosu=False,
            son_turlarin_cikarmalari=(),
            denetci_envanterleri=_cift(),  # AKTIF_ICERIK'in görüntüsü — bayat
            mekanik_eleme=_gecen_kapi(),
            takvim_anahtarlari=frozenset({TAKVIM_ANAHTARI}),
            takvim_kategorileri={TAKVIM_ANAHTARI: SISTEM_KATEGORISI},
            otomatik_kapilar=engine.GateResults(True, False),
        )


def test_current_audit_pair_is_accepted() -> None:
    """POZİTİF KONTROL: görüntü eşleşiyorsa çift kabul edilir."""
    girdi = _girdi()
    assert identity.canonical_sha(girdi.aktif_birimler) == (
        girdi.denetci_envanterleri.unit_snapshot_sha
    )


def test_invented_source_label_does_not_count() -> None:
    """F2: mekanik kapının tanımadığı kimlik dilbilgisinin DIŞINDADIR.

    `KAYNAK-99` bu koşuda geçerli bir kör etiket değildir; alan bir bütün
    olarak düşer ve referans hiç okunmaz — bu yüzden sebep `kanit-yok`.
    """
    sonuc = engine.run_checks(_ekle_girdisi(kanit=f"{IKI_KAYNAKLI}, KAYNAK-99"))
    assert "kanit-yok" in _sebepler(sonuc)


def test_eliminated_source_does_not_count() -> None:
    """F2/F8: elenen kaynağın KONUMUNA düşen kör etiket sayılmaz.

    Kaynak adları bilerek kör etiketten FARKLI: denetçi `KAYNAK-<n>` görür,
    mekanik kapı gerçek adı bilir. Eşleme konumdan türer (`build_packet` bu
    hizayı fail-closed zorlar); ad uzaylarını karşılaştırmak F8'in kırığıydı.
    """
    adlar = ("kuyumculuk-rehberi.md", "sektor-notlari.md", "vitrin-analizi.md")
    # Denetçi satırı ELENEN konumu gösteriyor: iki numaradan biri düşer.
    elenen_tablo = (
        _denetim_satiri(1, kaynaklar={1, 2}, sinif="2-3"),
        _denetim_satiri(2, kaynaklar={1, 3}, sinif="2-3"),
    )
    raporlar = [
        bd.DoctorReport(
            sonuc=bd.SONUC_ELENDI if sira == 1 else bd.SONUC_GECTI,
            notlar=(),
            elemeler=(
                (
                    bd.Bulgu(
                        kontrol="sahte-kontrol",
                        aile="bolum-ve-alan-tamligi",
                        seviye=bd.SEVIYE_ELEME,
                        mesaj="elenmis kaynak",
                    ),
                )
                if sira == 1
                else ()
            ),
            kaynak_adi=ad,
            icerik_ozeti=_ozet(ad),
            iddialar=_arastirma_iddialari(elenen_tablo),
        )
        for sira, ad in enumerate(adlar)
    ]
    kapi = bd.gate_round(raporlar)
    assert kapi.dur is False, "fixture kapıyı durdurmamalı — ölçülen şey SAYIM"

    girdi = _kapili_girdi(kapi, kanit="D1#1", denetim=elenen_tablo)
    assert "cogunluk-yok" in _sebepler(engine.run_checks(girdi))

    # POZİTİF KONTROL: elenmeyen İKİ konum sayılır (KAYNAK-1 ve KAYNAK-3).
    temiz = _kapili_girdi(kapi, kanit="D1#2", denetim=elenen_tablo)
    assert engine.run_checks(temiz).uygulanmayan_kararlar == ()


def _kapili_girdi(
    kapi: bd.RoundGate, *, kanit: str, denetim=None
) -> engine.EngineInputs:
    """`_ekle_girdisi`nin mekanik kapısı değiştirilmiş hâli.

    Kapı değişince ÇİFTİN taşıdığı kaynak kimliği de o kapıdan türetilir —
    aksi hâlde koşu bağı kapısı düşer ve test ölçmek istediği şeye (SAYIM) hiç
    ulaşamaz. Kapının kendisi ayrı bir testte ölçülür.
    """
    return _ekle_girdisi(kanit=kanit, denetim=denetim, kapi=kapi)


# ── Sınıf kapanışı: ÜRETİLMİŞ matris (elle seçilmiş örnek DEĞİL) ───────────
#
# Çoğunluk kapısı iki hakem turunda aynı eksenin üç ayrı varyantını doğurdu
# (serbest metin · uydurma kimlik · ad uzayı). Kapanış tek kanonik ayrıştırıcıyla
# yapıldı; kanıtı da elle seçilmiş örnek değil, sarmalayıcı ekseni üzerinde
# ÜRETİLMİŞ bir matristir: bir etiket ancak parçanın TAMAMIYSA sayılır.

def _sayilan_etiketler(kanit, etiketler) -> set[str]:
    """Dilbilgisinden geçen ÇIPLAK etiketler — eski `sayilan_kaynaklar` ölçümü.

    Üretim tarafı artık çoğunluğu etiketlerden SAYMIYOR (denetçinin `kaynaklar`
    sütunundan okuyor), ama `kanit` alanının KAPALI DİLBİLGİSİ aynen duruyor ve
    dört hakem turunda kapanan sınıf odur. Bu projeksiyon o kapsamı korur:
    ölçülen şey `engine.kanit_bilesenleri`'nin ta kendisidir.
    """
    parcalar = engine.kanit_bilesenleri(kanit, etiketler)
    return set() if parcalar is None else {p for p in parcalar if p in etiketler}


_SARMALAYICILAR = {
    "tam": ("{etiket}", True),
    "onunde-duzyazi": ("kaynak {etiket}", False),
    "arkasinda-duzyazi": ("{etiket} desteklemiyor", False),
    "olumsuz-cumle": ("{etiket} bu iddiayi DESTEKLEMIYOR", False),
    "ayrac-icinde": ("[{etiket}]", False),
    "kucuk-harf": ("{etiket_kucuk}", False),
    "bosluklu": ("  {etiket}  ", True),
}


@pytest.mark.parametrize("sarmalayici", sorted(_SARMALAYICILAR))
def test_source_parser_counts_only_whole_part_matches(sarmalayici) -> None:
    """ÜRETİLMİŞ MATRİS: sarmalanan etiket sayılmaz, çıplak etiket sayılır."""
    kalip, sayilmali = _SARMALAYICILAR[sarmalayici]
    etiket = DOGRULANMIS_KAYNAK
    parca = kalip.format(etiket=etiket, etiket_kucuk=etiket.lower())
    sayilan = _sayilan_etiketler(parca, {DOGRULANMIS_KAYNAK, IKINCI_KAYNAK})
    assert (sayilan == {etiket}) is sayilmali, f"{sarmalayici}: {sayilan}"


def test_source_parser_empty_arm_is_measured() -> None:
    """BOŞ-KÜME kontrol kolu: matris gerçekten bir şey ölçüyor mu?"""
    assert _sayilan_etiketler("", {DOGRULANMIS_KAYNAK}) == set()
    assert _sayilan_etiketler(DOGRULANMIS_KAYNAK, set()) == set()
    assert _sayilan_etiketler(None, {DOGRULANMIS_KAYNAK}) == set()
    # Tekrar eden etiket TEK kaynaktır (küme semantiği).
    assert _sayilan_etiketler(
        f"{DOGRULANMIS_KAYNAK}, {DOGRULANMIS_KAYNAK}", {DOGRULANMIS_KAYNAK}
    ) == {DOGRULANMIS_KAYNAK}


def test_negated_prose_does_not_pass_the_majority_gate() -> None:
    """Hakem turunun somut bypass örneği: düzyazı alanın TAMAMINI düşürür."""
    sonuc = engine.run_checks(
        _ekle_girdisi(
            kanit=f"{IKI_KAYNAKLI} desteklemiyor, {DOGRULANMIS_KAYNAK} yalniz baglam"
        )
    )
    assert "kanit-yok" in _sebepler(sonuc)


@pytest.mark.parametrize("deger", ["false", "true", 1, 0, None])
def test_gate_results_reject_non_bool_values(deger) -> None:
    """F4: doğru-görünen değer kapı kanıtı DEĞİLDİR (`"false"` DOĞRUdur)."""
    with pytest.raises(TypeError, match="bool"):
        engine.GateResults(katman1_passed=deger, tek_aktif_ihlali=False)
    with pytest.raises(TypeError, match="bool"):
        engine.GateResults(katman1_passed=True, tek_aktif_ihlali=deger)


def test_engine_inputs_rejects_lookalike_round_gate() -> None:
    """F4: `dur=False` taşıyan benzeyen nesne kapı değişmezlerini ATLAR."""

    class SahteKapi:
        dur = False
        bildirim = ""
        raporlar = ()

    with pytest.raises(TypeError, match="RoundGate"):
        _girdi(kapi=SahteKapi())


def test_auditor_row_reference_counts_as_evidence() -> None:
    """F5: kanonik kural İKİ kolludur — denetçi SATIRI da kanıttır.

    Satır kanıtı YOLA değil KİMLİĞE bağlıdır: aynı referans BAŞKA bir birimin
    satırında duruyorsa bu karara kanıt olmaz.
    """
    satir_kaniti = "D1#7"
    girdi = _guncelle_girdisi(
        alan="kanca_kaliplari",
        eski=KORUNAN_KANCA,
        yeni_metin="Guncellenmis kanca kalibi",
        kanit=satir_kaniti,
        statuler_1=MUTABIK,
        statuler_2=MUTABIK,
    )
    # Kanıt hiçbir denetçi satırında YOKKEN: uygulanmaz.
    assert "kanit-yok" in _sebepler(engine.run_checks(girdi))

    # Aynı kanıt DOĞRU birimin satırında dururken: çözülür.
    def _envanter_kanitli(hedef: str) -> tuple[auditors.InventoryRow, ...]:
        return tuple(
            auditors.InventoryRow(
                unit_id=unit_id,
                statu="needs_update" if unit_id == KANCA_KIMLIGI else "supported",
                kanit=satir_kaniti if unit_id == hedef else DOGRULANMIS_KAYNAK,
                gerekce="Tek cumle gerekce.",
            )
            for unit_id in sorted(AKTIF_BIRIMLER)
        )

    def _cift_kanitli(hedef: str):
        raporlar = [
            auditors.AuditReport(
                denetci=rol,
                ham_metin=f"{rol} ham raporu",
                bolumler={ad: f"{ad} govdesi" for ad in auditors.BOLUM_ANAHTARLARI},
                denetim_tablosu=DENETIM_TABLOSU,
                kaynak_profili=KAYNAK_PROFILI,
                yeniden_dogrulama=_envanter_kanitli(hedef),
                url_orneklem=_ornekle(),
                unit_snapshot_sha=AKTIF_GORUNTU_SHA,
            )
            for rol in auditors.DENETCI_ROLLERI
        ]
        mutabakat = auditors.check_snapshot_agreement(
            (
                auditors.ValidatedReport(raporlar[0], ()),
                auditors.ValidatedReport(raporlar[1], ()),
            ),
            expected_snapshot_sha=AKTIF_GORUNTU_SHA,
            expected_kaynak_sha=KAYNAK_SETI_SHA,
        )
        assert mutabakat.gecerli, mutabakat.errors
        return mutabakat.cift

    dogru = engine.EngineInputs(
        sentez=girdi.sentez,
        aktif_paket=girdi.aktif_paket,
        aktif_schema_version=girdi.aktif_schema_version,
        aktif_birimler=girdi.aktif_birimler,
        mevcut_birim_sayisi=girdi.mevcut_birim_sayisi,
        ilk_kosu=girdi.ilk_kosu,
        son_turlarin_cikarmalari=girdi.son_turlarin_cikarmalari,
        denetci_envanterleri=_cift_kanitli(KANCA_KIMLIGI),
        mekanik_eleme=girdi.mekanik_eleme,
        takvim_anahtarlari=girdi.takvim_anahtarlari,
        takvim_kategorileri=girdi.takvim_kategorileri,
        otomatik_kapilar=girdi.otomatik_kapilar,
    )
    assert engine.run_checks(dogru).uygulanmayan_kararlar == ()

    yanlis = engine.EngineInputs(
        sentez=girdi.sentez,
        aktif_paket=girdi.aktif_paket,
        aktif_schema_version=girdi.aktif_schema_version,
        aktif_birimler=girdi.aktif_birimler,
        mevcut_birim_sayisi=girdi.mevcut_birim_sayisi,
        ilk_kosu=girdi.ilk_kosu,
        son_turlarin_cikarmalari=girdi.son_turlarin_cikarmalari,
        denetci_envanterleri=_cift_kanitli(MEVZUAT_KIMLIGI),
        mekanik_eleme=girdi.mekanik_eleme,
        takvim_anahtarlari=girdi.takvim_anahtarlari,
        takvim_kategorileri=girdi.takvim_kategorileri,
        otomatik_kapilar=girdi.otomatik_kapilar,
    )
    assert "kanit-yok" in _sebepler(engine.run_checks(yanlis))


# ── Eksen kapanışı: ALAN BÜTÜN olarak doğrulanır (üretilmiş matris) ────────
#
# Üçüncü kapanış turu bileşen-bazlı süzmenin komşu bileşene taşan düzyazıyla
# aşıldığını ÖLÇTÜ. Matris artık düzyazının KONUMUNU (baş/orta/son) ve etiket
# sayısını (iki/üç) çarpım olarak üretir; tek tek örnek yazılmaz.

_ETIKET_KUMESI = {DOGRULANMIS_KAYNAK, IKINCI_KAYNAK, "KAYNAK-3"}
_DUZYAZILAR = (
    "Bu kaynaklar iddiayi desteklemiyor",
    "ancak ikisi de iddiayi desteklemiyor",
    "yalniz baglam",
)


def _matris_vakalari():
    """(kimlik, kanit, beklenen_sayim) üçlülerini ÜRETİR."""
    etiket_kumeleri = [
        [DOGRULANMIS_KAYNAK, IKINCI_KAYNAK],
        [DOGRULANMIS_KAYNAK, IKINCI_KAYNAK, "KAYNAK-3"],
    ]
    for etiketler in etiket_kumeleri:
        n = len(etiketler)
        # Pozitif kol: yalnız çıplak etiketler → hepsi sayılır.
        yield (f"saf-{n}", ", ".join(etiketler), n)
        # Pozitif kol: etiket + dilbilgisi içi bileşenler (URL, satır atfı).
        yield (f"saf-{n}-url", ", ".join([*etiketler, DOGRULANMIS_URL]), n)
        yield (f"saf-{n}-satir", ", ".join([*etiketler, "D1#7"]), n)
        # Negatif kol: düzyazı BAŞTA / ORTADA / SONDA — alanın tamamı düşer.
        for sira, duzyazi in enumerate(_DUZYAZILAR):
            for konum, ad in ((0, "bas"), (len(etiketler) // 2, "orta"), (len(etiketler), "son")):
                parcalar = list(etiketler)
                parcalar.insert(konum, duzyazi)
                yield (f"duzyazi-{ad}-{n}-{sira}", ", ".join(parcalar), 0)
        # Negatif kol: düzyazı ETİKETE YAPIŞIK (ilk turun varyantı).
        yield (
            f"yapisik-{n}",
            ", ".join([f"{_DUZYAZILAR[0]}: {etiketler[0]}", *etiketler[1:]]),
            0,
        )


_MATRIS = list(_matris_vakalari())


def test_matrix_is_actually_generated_and_two_sided() -> None:
    """BOŞ-KÜME kontrol kolu: matris gerçekten iki yanlı ve doluysa anlamlıdır."""
    assert len(_MATRIS) >= 20, len(_MATRIS)
    beklenenler = {beklenen for _ad, _kanit, beklenen in _MATRIS}
    assert beklenenler == {0, 2, 3}, beklenenler


@pytest.mark.parametrize("ad,kanit,beklenen", _MATRIS, ids=[v[0] for v in _MATRIS])
def test_evidence_field_is_validated_as_a_whole(ad, kanit, beklenen) -> None:
    """Dilbilgisi dışı TEK bileşen bile alanın tamamını düşürür."""
    sayilan = _sayilan_etiketler(kanit, _ETIKET_KUMESI)
    assert len(sayilan) == beklenen, f"{ad}: {sorted(sayilan)}"


def test_cross_part_prose_does_not_pass_the_majority_gate() -> None:
    """Entegrasyon: üçüncü turun somut bypass'ı `run_checks` düzeyinde kapalı."""
    sonuc = engine.run_checks(
        _ekle_girdisi(
            kanit=f"Bu kaynaklar iddiayi desteklemiyor: {IKI_KAYNAKLI}, {DOGRULANMIS_KAYNAK}"
        )
    )
    assert "kanit-yok" in _sebepler(sonuc)


# ── URL kolunun kendi matrisi (dördüncü kapanış turu) ─────────────────────
#
# Gevşek URL kolu düzyazıyı geri alıyordu: "://" içeren ve ASCII boşluk taşımayan
# her bileşen URL sayılıyordu. Matris bozuk biçimleri ÜRETİR; kollar tek tek
# yazılmaz.

_BOZUK_URL_BILESENLERI = {
    "satir-sonu": "https://ornek.example\nDESTEKLEMIYOR",
    "sekme": "https://ornek.example\tDESTEKLEMIYOR",
    "dikey-bosluk": "https://ornek.example\x0bDESTEKLEMIYOR",
    "gecersiz-sema": "javascript://ornek",
    "sema-yok": "://ornek.example",
    "konak-yok": "https://",
    "cikplak-metin": "ornek.example",
}

_GECERLI_URL_BILESENLERI = {
    "sade": "https://ornek.example",
    "yollu": "https://ornek.example/a/b",
    "sorgulu": "https://ornek.example/a?b=1#c",
    "http": "http://ornek.example",
}


@pytest.mark.parametrize("ad", sorted(_BOZUK_URL_BILESENLERI))
def test_malformed_url_component_drops_the_whole_field(ad) -> None:
    """Bozuk URL bileşeni alanın TAMAMINI düşürür — komşu etiketler kurtulmaz."""
    kanit = f"{DOGRULANMIS_KAYNAK}, {IKINCI_KAYNAK}, {_BOZUK_URL_BILESENLERI[ad]}"
    assert _sayilan_etiketler(kanit, _ETIKET_KUMESI) == set()


@pytest.mark.parametrize("ad", sorted(_GECERLI_URL_BILESENLERI))
def test_wellformed_url_component_keeps_the_labels(ad) -> None:
    """POZİTİF KONTROL: düzgün URL bileşeni etiketleri düşürmez."""
    kanit = f"{DOGRULANMIS_KAYNAK}, {IKINCI_KAYNAK}, {_GECERLI_URL_BILESENLERI[ad]}"
    assert _sayilan_etiketler(kanit, _ETIKET_KUMESI) == {
        DOGRULANMIS_KAYNAK,
        IKINCI_KAYNAK,
    }


@pytest.mark.parametrize(
    "kanit",
    [
        f"{DOGRULANMIS_KAYNAK}, , {IKINCI_KAYNAK}",
        f"{DOGRULANMIS_KAYNAK}, {IKINCI_KAYNAK},",
        f",{DOGRULANMIS_KAYNAK}, {IKINCI_KAYNAK}",
        f"{DOGRULANMIS_KAYNAK},,{IKINCI_KAYNAK}",
    ],
    ids=["orta-bos", "sondaki-virgul", "bastaki-virgul", "cift-virgul"],
)
def test_empty_component_drops_the_whole_field(kanit) -> None:
    """Boş bileşen sessizce DÜŞÜRÜLMEZ; biçim bozuksa alan kanıt taşımaz."""
    assert _sayilan_etiketler(kanit, _ETIKET_KUMESI) == set()


def test_malformed_url_does_not_pass_the_majority_gate() -> None:
    """Entegrasyon: dördüncü turun somut probu `run_checks` düzeyinde kapalı."""
    sonuc = engine.run_checks(
        _ekle_girdisi(
            kanit=f"{IKI_KAYNAKLI}, {DOGRULANMIS_KAYNAK}, https://ornek.example\nDESTEKLEMIYOR"
        )
    )
    assert "kanit-yok" in _sebepler(sonuc)
