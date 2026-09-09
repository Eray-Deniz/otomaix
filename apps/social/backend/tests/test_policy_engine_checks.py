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


def _rapor(rol: str, *, statuler=None, ornekle=None) -> auditors.AuditReport:
    return auditors.AuditReport(
        denetci=rol,
        ham_metin=f"{rol} ham raporu",
        bolumler={ad: f"{ad} govdesi" for ad in auditors.BOLUM_ANAHTARLARI},
        yeniden_dogrulama=_envanter(statuler),
        url_orneklem=_ornekle() if ornekle is None else ornekle,
        unit_snapshot_sha=AKTIF_GORUNTU_SHA,
    )


def _cift(*, statuler_1=None, statuler_2=None, ornekle_1=None, ornekle_2=None):
    """`ValidatedAuditPair` — TEK üreticisinden (mutabakat kapısı) geçerek."""
    mutabakat = auditors.check_snapshot_agreement(
        (
            auditors.ValidatedReport(
                _rapor(auditors.DENETCI_ROLLERI[0], statuler=statuler_1, ornekle=ornekle_1),
                (),
            ),
            auditors.ValidatedReport(
                _rapor(auditors.DENETCI_ROLLERI[1], statuler=statuler_2, ornekle=ornekle_2),
                (),
            ),
        ),
        expected_snapshot_sha=AKTIF_GORUNTU_SHA,
    )
    assert mutabakat.gecerli, mutabakat.errors
    return mutabakat.cift


def _ozet(ad: str) -> str:
    """Kanonik icerik ozeti — `DoctorReport` serbest metni kimlik kararina almaz."""
    return hashlib.sha256(ad.encode("utf-8")).hexdigest()


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
    return engine.EngineInputs(
        sentez=_sonuc(aday, log, acik_sorular=acik_sorular),
        aktif_paket=_aktif_paket() if aktif else None,
        aktif_schema_version=1 if aktif else None,
        aktif_birimler=birimler,
        mevcut_birim_sayisi=len(birimler),
        ilk_kosu=not aktif,
        son_turlarin_cikarmalari=cikarmalar,
        denetci_envanterleri=_cift() if cift is None else cift,
        mekanik_eleme=_gecen_kapi() if kapi is None else kapi,
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


def _ekle_girdisi(*, kanit: str, metin: str = "Yeni kanca kalibi", ornekle=None, cikarmalar=()):
    aday = _tam_icerik(kanca_kaliplari=[KORUNAN_KANCA, CIKARILACAK_KANCA, metin])
    harita = _kimlik_haritasi(AKTIF_ICERIK, aday)
    yeni_yol = _yol(aday, "kanca_kaliplari", metin)
    gunluk = _gunluk(
        aday, kimlikler=harita, degis={yeni_yol: {"karar": "ekle", "kanit": kanit}}
    )
    return _girdi(
        icerik=aday,
        gunluk=gunluk,
        cift=_cift(ornekle_1=ornekle, ornekle_2=ornekle),
        cikarmalar=cikarmalar,
    )


def test_new_item_needs_two_of_three() -> None:
    """Tek kaynaklı yeni öğe yapısal çoğunluğu geçemez."""
    sonuc = engine.run_checks(_ekle_girdisi(kanit=DOGRULANMIS_KAYNAK))
    assert "cogunluk-yok" in _sebepler(sonuc)


def test_new_item_with_two_sources_passes() -> None:
    """POZİTİF: iki bağımsız kaynak yapısal çoğunluğu KARŞILAR."""
    sonuc = engine.run_checks(
        _ekle_girdisi(kanit=f"{DOGRULANMIS_KAYNAK}, {IKINCI_KAYNAK}")
    )
    assert sonuc.uygulanmayan_kararlar == ()


def test_single_source_exception_requires_official_and_live_url() -> None:
    """K-126: tekil iddia YALNIZ resmî kaynak + canlı URL doğrulamasıyla girer."""
    gecen = engine.run_checks(
        _ekle_girdisi(kanit=f"{DOGRULANMIS_KAYNAK}, {DOGRULANMIS_URL}")
    )
    assert gecen.uygulanmayan_kararlar == ()

    dusen = engine.run_checks(
        _ekle_girdisi(
            kanit=f"{DOGRULANMIS_KAYNAK}, {DOGRULANMIS_URL}",
            ornekle=_ornekle(uyumlu=False),
        )
    )
    assert "cogunluk-yok" in _sebepler(dusen)


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


def test_category_conflict_is_recorded_and_package_type_wins() -> None:
    """K-03: tür etiketi çatışması KAYDEDİLİR; paket türü üstündür, blok YOK."""
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
    catismalar = sonuc.olcumler["kategori_cakismalari"]
    assert catismalar and catismalar[0]["anahtar"] == TAKVIM_ANAHTARI
    assert catismalar[0]["paket_turu"] == "anma"
    assert sonuc.bulgular == ()


def test_matching_type_label_records_no_conflict() -> None:
    """POZİTİF: tür etiketi değişmediyse çatışma kaydı YOKTUR."""
    sonuc = engine.run_checks(_girdi())
    assert sonuc.olcumler["kategori_cakismalari"] == ()


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


def test_engine_consumes_only_validated_inventory() -> None:
    """Motorun gördüğü envanter YALNIZ doğrulanmış çiftten gelir."""
    girdi = _girdi()
    assert girdi.denetci_envanterleri.unit_snapshot_sha == AKTIF_GORUNTU_SHA
    kimlikler = {
        satir.unit_id for satir in girdi.denetci_envanterleri.birinci.yeniden_dogrulama
    }
    assert kimlikler == set(AKTIF_BIRIMLER)


def test_yerel_degil_flag_closes_the_single_source_exception() -> None:
    """`[yerel-değil]` tekil istisnayı KAPATIR — canlı URL bile yetmez."""
    sonuc = engine.run_checks(
        _ekle_girdisi(kanit=f"{DOGRULANMIS_KAYNAK}, {DOGRULANMIS_URL} [yerel-değil]")
    )
    assert "cogunluk-yok" in _sebepler(sonuc)
