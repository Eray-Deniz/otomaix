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
from pathlib import Path
from dataclasses import fields as dataclass_fields

import pytest

from app.services.sector_content_schema import structural_errors
from app.services.sector_pipeline import auditors, brief_doctor as bd, identity
from app.services.sector_pipeline import engine
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
    "otomatik_kapilar",
)

MEVZUAT_ALANI = "yasaklar_ve_hassasiyetler"

TAKVIM_ANAHTARI = "cumhuriyet-bayrami"


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
        satirlar.append(satir)
    satirlar.extend(ek)
    return satirlar


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
    alan: str = "cta_kaliplari",
) -> auditors.AuditRow:
    """Tek denetim satırı. `sinif` verilmezse kaynak sayısından TÜRETİLİR."""
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
        kaynaklar=frozenset(kaynaklar),
        sinif=sinif,
        bayraklar="—",
        oneri="al",
        gerekce="Tek cumle gerekce.",
    )


DENETIM_TABLOSU = (
    # Koşuya İKİ kaynak giriyor (`KAYNAK-1` · `KAYNAK-2`), oran ona uyarlıdır.
    _denetim_satiri(1, kaynaklar={1, 2}, sinif="2-2"),
    _denetim_satiri(2, kaynaklar={1}, sinif=auditors.SINIF_TEKIL),
    _denetim_satiri(3, kaynaklar={1, 2}, sinif=auditors.SINIF_CELISKI),
)

IKI_KAYNAKLI = "D1#1"
TEK_KAYNAKLI = "D1#2"
CELISKILI = "D1#3"


def _rapor(
    rol: str, *, statuler=None, ornekle=None, denetim=None
) -> auditors.AuditReport:
    return auditors.AuditReport(
        denetci=rol,
        ham_metin=f"{rol} ham raporu",
        bolumler={ad: f"{ad} govdesi" for ad in auditors.BOLUM_ANAHTARLARI},
        denetim_tablosu=DENETIM_TABLOSU if denetim is None else denetim,
        yeniden_dogrulama=_envanter(statuler),
        url_orneklem=_ornekle() if ornekle is None else ornekle,
        unit_snapshot_sha=AKTIF_GORUNTU_SHA,
    )


def _bos_gorunti_cifti(*, kaynak_sha=None):
    """İlk koşunun çifti: aktif birim YOK, görüntü BOŞ kümenin hash'idir."""
    sha = identity.canonical_sha({})
    raporlar = [
        auditors.AuditReport(
            denetci=rol,
            ham_metin=f"{rol} ham raporu",
            bolumler={ad: f"{ad} govdesi" for ad in auditors.BOLUM_ANAHTARLARI},
            denetim_tablosu=DENETIM_TABLOSU,
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
    denetim=None, kaynak_sha=None,
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
                ),
                (),
            ),
            auditors.ValidatedReport(
                _rapor(
                    auditors.DENETCI_ROLLERI[1],
                    statuler=statuler_2,
                    ornekle=ornekle_2,
                    denetim=denetim,
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


def _gecen_kapi() -> bd.RoundGate:
    return bd.gate_round(
        [
            bd.DoctorReport(
                sonuc=bd.SONUC_GECTI,
                notlar=(),
                elemeler=(),
                kaynak_adi=ad,
                icerik_ozeti=_ozet(ad),
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
    kapi: bd.RoundGate | None = None,
    takvim: frozenset[str] | None = None,
    kapilar: engine.GateResults | None = None,
    cikarmalar: tuple = (),
) -> engine.EngineInputs:
    aday = AKTIF_ICERIK if icerik is None else icerik
    log = _gunluk(aday) if gunluk is None else gunluk
    birimler = AKTIF_BIRIMLER if aktif else {}
    # Kapı DEĞİŞTİYSE çiftin taşıdığı kaynak kimliği de o kapıdan türer: koşu
    # bağı kapısı fixture'ın kendi tutarsızlığını değil, ÜRETİM tutarsızlığını
    # ölçmelidir (kapının kendisi ayrı bir testte ölçülür).
    mekanik = _gecen_kapi() if kapi is None else kapi
    varsayilan_cift = (
        _cift(kaynak_sha=_kaynak_seti_sha(mekanik))
        if aktif
        else _bos_gorunti_cifti(kaynak_sha=_kaynak_seti_sha(mekanik))
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
    metin: str = "Yeni kanca kalibi",
    ornekle=None,
    cikarmalar=(),
    denetim=None,
    kaynak_sha=None,
    kapi=None,
):
    aday = _tam_icerik(kanca_kaliplari=[KORUNAN_KANCA, CIKARILACAK_KANCA, metin])
    harita = _kimlik_haritasi(AKTIF_ICERIK, aday)
    yeni_yol = _yol(aday, "kanca_kaliplari", metin)
    gunluk = _gunluk(
        aday, kimlikler=harita, degis={yeni_yol: {"karar": "ekle", "kanit": kanit}}
    )
    return _girdi(
        icerik=aday,
        gunluk=gunluk,
        cift=_cift(
            ornekle_1=ornekle,
            ornekle_2=ornekle,
            denetim=denetim,
            kaynak_sha=_kaynak_seti_sha(kapi) if kapi is not None else kaynak_sha,
        ),
        kapi=kapi,
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


def test_single_source_exception_is_closed_until_officiality_is_typed() -> None:
    """K-126 İKİ koşulu BİRLİKTE ister; biri ölçülemiyorsa istisna İŞLEMEZ.

    Canlı ve içerikçe uyumlu bir URL (ikinci ayak) TEK BAŞINA yetmez: kaynağın
    resmî/birincil olduğu (K-123, birinci ayak) tipli girdide taşınmıyor. Bir
    AND koşulunun tek ayağını zorlamak istisnayı canlı HER kaynağa açardı.

    Tipli okumadan SONRA da kapalıdır: tek kaynaklı denetçi satırının yanına
    canlı bir URL konması sayıyı değiştirmez.
    """
    canli = engine.run_checks(
        _ekle_girdisi(kanit=f"{TEK_KAYNAKLI}, {DOGRULANMIS_URL}")
    )
    assert "cogunluk-yok" in _sebepler(canli)

    olu = engine.run_checks(
        _ekle_girdisi(
            kanit=f"{TEK_KAYNAKLI}, {DOGRULANMIS_URL}",
            ornekle=_ornekle(uyumlu=False),
        )
    )
    assert "cogunluk-yok" in _sebepler(olu)


# ═══ 11. Kontrol: bayrak tüketimi ═════════════════════════════════════════


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
}


@pytest.mark.parametrize("eksen", sorted(_KAYNAK_KIMLIGI_EKSENLERI))
def test_source_set_identity_is_sensitive_on_every_axis(eksen: str) -> None:
    """ÜRETİLMİŞ MATRİS: kimlik SIRA · AD · İÇERİK · ELEME eksenlerinde ayrışır.

    Dördü de bir sebeple girer: sıra kör etiketin hangi kaynağa düştüğünü
    belirler, ad kimliği, içerik metni, eleme ise motorun kabul ettiği etiket
    kümesini. Biri hash'e girmezse o eksende iki ayrı koşu AYNI kimliği taşır.
    """
    adlar, sapma = _KAYNAK_KIMLIGI_EKSENLERI[eksen]

    def _rapor_kur(ad: str, *, ozetler: dict, elenen: str | None) -> bd.DoctorReport:
        elendi = ad == elenen
        return bd.DoctorReport(
            sonuc=bd.SONUC_ELENDI if elendi else bd.SONUC_GECTI,
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
                if elendi
                else ()
            ),
            kaynak_adi=ad,
            icerik_ozeti=_ozet(ozetler.get(ad, ad)),
        )

    # TABAN sapmasızdır; sapma YALNIZ karşılaştırılan tarafa uygulanır.
    taban = bd.kaynak_seti_sha(
        [_rapor_kur(ad, ozetler={}, elenen=None) for ad in ("a", "b")]
    )
    sapan = bd.kaynak_seti_sha(
        [
            _rapor_kur(ad, ozetler=sapma.get("ozet", {}), elenen=sapma.get("elenen"))
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
        )
        for sira, ad in enumerate(adlar)
    ]
    kapi = bd.gate_round(raporlar)
    assert kapi.dur is False, "fixture kapıyı durdurmamalı — ölçülen şey SAYIM"

    # Denetçi satırı ELENEN konumu gösteriyor: iki numaradan biri düşer.
    elenen_tablo = (
        _denetim_satiri(1, kaynaklar={1, 2}, sinif="2-3"),
        _denetim_satiri(2, kaynaklar={1, 3}, sinif="2-3"),
    )
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
