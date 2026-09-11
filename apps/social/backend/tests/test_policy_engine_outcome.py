"""Motorun SONUÇ katmanı — güvenli fallback · üç bariyer · sonuç tipleri
(Plan 2 Task 13, arayüz eki R2/R5/R6/R7).

Altı sözleşme burada pinlenir:

1. **BULGUYU SONUCA ÇEVİREN TEK YER `decide`'dır.** `run_checks` bulgu üretir
   (Task 12); uygulama/uygulanmama semantiği BU katmanındır (arayüz eki R7).
   Bu yüzden Task 12'nin "uygulanmaz/korunur" iddiaları buraya TAŞINDI.
2. **ALTI BULGU SINIFININ ALTISININ DA TÜKETİCİSİ VAR.** `BULGU_SINIFLARI`
   kapalıdır; `decide`'ın dönüşüm tablosu her değeri karşılar — yapısal kapı
   `test_finding_classes_all_have_a_consumer`'dır.
3. **K-23=B GÜVENLİ VARSAYILAN.** Motorun karar veremediği madde MEVCUT KALIBI
   KORUR, rapora girer ve aktivasyonu BLOKLAMAZ. Sentezin AÇIK SORUsu bundan
   AYRI bir yoldur ve K-71 gereği BLOKLAR.
4. **EŞİK `None` İKEN BARİYER HİÇBİR ŞEYİ BLOKLAMAZ (İlke 9).** Üç bariyerin
   mekanizması kurulur, eşikleri ölçülene kadar pasiftir. Mekanizmanın gerçekten
   çalıştığı POZİTİF kontrolle kanıtlanır: eşik dolduğunda bloklar.
5. **YOL SIRA NUMARALARI KONUMSALDIR.** Reddedilen bir ekleme listeyi kaydırır;
   `decide` nihai günlüğü KİMLİĞE göre yeniden numaralandırır — yola göre değil.
6. **BAĞIMSIZ ORACLE.** Sonuç adları, sebep dizeleri, alan listeleri ve dönüşüm
   tablosu bu dosyada ELLE yazılıdır; üretim sabitlerinden TÜRETİLMEZ.

**Fixture'lar Task 12'nin dosyasından İTHAL EDİLİR** (`_girdi` · `_tam_icerik` ·
denetçi kurucuları). İkinci bir kopya yazılsaydı iki fixture kümesi aynı içerik
sözleşmesini ayrı ayrı modeller ve sessizce ıraksardı; oracle'lar (beklenen
adlar/değerler) yine de BURADA elle yazılıdır — ithal edilen şey ölçüm ZEMİNİ,
beklenti DEĞİL.
"""

from __future__ import annotations

import re
from dataclasses import fields as dataclass_fields
from pathlib import Path

import pytest

from app.services.sector_content_schema import SPECIAL_DAY_SLOTS, structural_errors
from app.services.sector_pipeline import brief_doctor as bd, engine, identity
from app.services.sector_pipeline.engine_contract import (
    BULGU_SINIFLARI,
    EngineResult,
    PolicyReport,
    SONUCLAR,
    UYGULANMAMA_SEBEPLERI,
)
from app.services.sector_pipeline.policy_config import PolicyConfig, config_sha
from app.services.sector_pipeline import auditors
from tests.test_policy_engine_checks import (
    AKTIF_BIRIMLER,
    AKTIF_ICERIK,
    BEKLENEN_KONTROL_ADLARI,
    CIKAN_KIMLIK,
    CIKARILACAK_KANCA,
    DOGRULANMIS_KAYNAK,
    IKI_KAYNAKLI,
    TEK_KAYNAKLI,
    KIMLIKLER,
    KORUNAN_KANCA,
    MEVZUAT_ALANI,
    MEVZUAT_KIMLIGI,
    MEVZUAT_MADDESI,
    MUTABIK,
    MUTABIK_MEVZUAT,
    COZULEMEYEN_KANIT,
    TAKVIM_ANAHTARI,
    _cift,
    _denetim_satiri,
    _girdi,
    _gunluk,
    _guncelle_girdisi,
    _tam_icerik,
    _yol,
)


# ═══ Ölçüm anında ELLE yazılmış bağımsız beklentiler ═══════════════════════
#
# Kaynak: plan `### Task 13` gövdesi + arayüz eki R2 (`EngineResult` on bir
# alan) ve R7 (dönüşüm tablosu, altı satır).

BEKLENEN_SONUC_ALANLARI = (
    "sonuc",
    "sebep",
    "final_candidate",
    "final_decision_log",
    "engine_diff",
    "policy_report",
    "barrier_report",
    "content_sha",
    "decision_log_sha",
    "engine_version",
    "engine_config_sha",
)

BEKLENEN_RAPOR_ALANLARI = (
    "kararsizlar",
    "bulgular",
    "uygulanmayan_kararlar",
    "acik_soru_kimlikleri",
)

# R7 tablosu — sınıf → (etki, sebep). ELLE yazıldı.
BEKLENEN_DONUSUM = {
    "kapsam_ihlali": ("bloklar", "kapsam-ihlali"),
    "mevzuat_uyusmazligi": ("bloklar", "mevzuat-uyusmazligi"),
    "mevzuat_dogrulanamadi": ("bayraga-bagli-bloklar", "mevzuat-dogrulanamadi"),
    "regresyon_kapisi": ("aktivasyonu-engeller", "regresyon-kapisi-gecmedi"),
    "ikinci_aktif": ("bloklar", "ikinci-aktif-paket"),
    "acik_soru": ("bloklar", "acik-soru-var"),
}

SEBEP_BARIYER = "bariyer-asildi"
SEBEP_ILK_KOSU = "ilk-kosuda-degisiklik-yok-gecersiz"

GUNCELLENMIS_KANCA = "Guncellenmis kanca kalibi"


# ═══ Yerel kurucular ═══════════════════════════════════════════════════════


def _karar(girdi=None, config: PolicyConfig | None = None) -> EngineResult:
    return engine.decide(
        _girdi() if girdi is None else girdi, PolicyConfig() if config is None else config
    )


def _guncelle_parcalari(*, kanit: str) -> dict:
    """Tek kancayı `guncelle` ile değiştiren turun `_girdi` parçaları.

    Parça olarak döner ki çağıran aynı senaryoya `kapilar`/`acik_sorular` gibi
    ikinci bir ekseni EKLEYEBİLSİN — kurulmuş `EngineInputs`'ı alan alan yeniden
    kurmak, yapımdaki görüntü kapısını (R6) ikinci kez koşturmak demektir.
    """
    yol = _yol(AKTIF_ICERIK, "kanca_kaliplari", KORUNAN_KANCA)
    aday = _tam_icerik(kanca_kaliplari=[GUNCELLENMIS_KANCA, CIKARILACAK_KANCA])
    return {
        "icerik": aday,
        "gunluk": _gunluk(aday, degis={yol: {"karar": "guncelle", "kanit": kanit}}),
        "cift": _cift(statuler_1=MUTABIK, statuler_2=MUTABIK),
    }


def _uygulanan_guncelle(**ek):
    """Kanıtı ve mutabakatı TAM olan bir `guncelle` turu — karar UYGULANIR."""
    return _girdi(**_guncelle_parcalari(kanit=DOGRULANMIS_KAYNAK), **ek)


def _uygulanmayan_guncelle(**ek):
    """Kanıtı ÇÖZÜLMEYEN `guncelle` — K-23=B: kalıp korunur, bloklamaz."""
    return _girdi(**_guncelle_parcalari(kanit=COZULEMEYEN_KANIT), **ek)


def _tur_degisikligi_girdisi():
    """Özel günün TÜR etiketi değişir (K-03'ün ölçülebilen ayağı)."""
    aday = _tam_icerik()
    aday["ozel_gun"] = {
        TAKVIM_ANAHTARI: dict(AKTIF_ICERIK["ozel_gun"][TAKVIM_ANAHTARI], tur="anma")
    }
    yol = f"ozel_gun/{TAKVIM_ANAHTARI}/tur"
    kimlik = KIMLIKLER[yol]
    return _girdi(
        icerik=aday,
        gunluk=_gunluk(
            aday, degis={yol: {"karar": "guncelle", "kanit": DOGRULANMIS_KAYNAK}}
        ),
        cift=_cift(
            statuler_1={kimlik: "needs_update"}, statuler_2={kimlik: "needs_update"}
        ),
    )


def _cikar_girdisi(*, mutabik: bool):
    """`cikar` turu — `mutabik=False` iken iki denetçi UYUŞMAZ (mutabakat-yok)."""
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
    ikinci = "contradicted" if mutabik else "supported"
    return _girdi(
        icerik=aday,
        gunluk=_gunluk(aday, ek=(cikar_satiri,)),
        cift=_cift(
            statuler_1={CIKAN_KIMLIK: "contradicted"},
            statuler_2={CIKAN_KIMLIK: ikinci},
        ),
    )


def _kimlik_haritasi_degere_gore(aday: dict) -> dict[str, str]:
    """Aday yolları → kimlik: AYNI değer aktifte varsa AKTİF kimliği taşır.

    Konumsal eşleme burada KULLANILAMAZ — listenin başına eklenen bir öğe tüm
    sıra numaralarını kaydırır ve yola göre eşleyen bir harita yeni kalıba
    aktif bir kimlik verirdi (kimlik benzersizliği ihlali).
    """
    aktif = identity.enumerate_content_units(AKTIF_ICERIK)
    deger_kimligi = {
        (birim["alan"], birim["oge_sha"]): KIMLIKLER[yol] for yol, birim in aktif.items()
    }
    harita: dict[str, str] = {}
    sayac = 0
    for yol, birim in sorted(identity.enumerate_content_units(aday).items()):
        anahtar = (birim["alan"], birim["oge_sha"])
        if anahtar in deger_kimligi:
            harita[yol] = deger_kimligi[anahtar]
        else:
            sayac += 1
            harita[yol] = f"ku-{0xF00000000000 + sayac:012x}"
    return harita


def _basa_ekleme_girdisi(*, kanit: str):
    """Listenin BAŞINA eklenen yeni kalıp — kabul edilirse sıra numaraları kayar."""
    yeni = "Yeni kanca kalibi"
    aday = _tam_icerik(kanca_kaliplari=[yeni, KORUNAN_KANCA, CIKARILACAK_KANCA])
    harita = _kimlik_haritasi_degere_gore(aday)
    yeni_yol = _yol(aday, "kanca_kaliplari", yeni)
    return _girdi(
        icerik=aday,
        gunluk=_gunluk(
            aday, kimlikler=harita, degis={yeni_yol: {"karar": "ekle", "kanit": kanit}}
        ),
    )


def _ilk_kosu_girdisi(*, kanit: str):
    """İlk paket koşusu — her birim `ekle`; kanıt gücü çağırana bırakılır.

    Denetim tablosu ALAN BAŞINA bir satır taşır ve her karar KENDİ alanının
    satırına atıf yapar. Tek satıra toplu atıf, motorun alan bağını (hakem turu
    1, yüksek) ölçülmeden geçirir: fixture'ın kendi tutarsızlığı üretim
    hatasıymış gibi görünürdü.
    """
    yollar = identity.enumerate_content_units(AKTIF_ICERIK)
    alanlar = sorted({identity.enumerate_content_units(AKTIF_ICERIK)[yol]['alan'] for yol in yollar})
    tablo = tuple(
        _denetim_satiri(
            sira + 1,
            kaynaklar={1, 2} if kanit == IKI_KAYNAKLI else {1},
            sinif="2-2" if kanit == IKI_KAYNAKLI else auditors.SINIF_TEKIL,
            alan=alan,
        )
        for sira, alan in enumerate(alanlar)
    )
    atif = {alan: f"D1#{sira + 1}" for sira, alan in enumerate(alanlar)}
    gunluk = _gunluk(
        AKTIF_ICERIK,
        degis={
            yol: {"karar": "ekle", "kanit": atif[identity.enumerate_content_units(AKTIF_ICERIK)[yol]['alan']]}
            for yol in yollar
        },
        denetim=tablo,
    )
    return _girdi(gunluk=gunluk, aktif=False, denetim=tablo)


def _kancalar(sonuc: EngineResult) -> list[str]:
    return list(sonuc.final_candidate["kanca_kaliplari"])


# ═══ 1. Sözleşme yüzeyi (arayüz eki R2) ════════════════════════════════════


def test_engine_result_field_set_is_closed() -> None:
    """On bir alan — fazlası da eksiği de RED (`kararsizlar` alanı YOKTUR)."""
    adlar = tuple(alan.name for alan in dataclass_fields(EngineResult))
    assert adlar == BEKLENEN_SONUC_ALANLARI


def test_policy_report_field_set_is_closed() -> None:
    adlar = tuple(alan.name for alan in dataclass_fields(PolicyReport))
    assert adlar == BEKLENEN_RAPOR_ALANLARI


def test_bulgu_izi_class_values_are_closed() -> None:
    """Kapalı kümenin dışında bir sınıf üretilemez."""
    assert set(BULGU_SINIFLARI) == set(BEKLENEN_DONUSUM)


def test_uygulanmama_sebepleri_are_closed() -> None:
    assert set(UYGULANMAMA_SEBEPLERI) == {
        "kanit-yok",
        "mutabakat-yok",
        "referans-yok",
        "referans-uyusmuyor",
        "kaynak-iddia-yok",
        "iddia-arastirmada-yok",
        "iddia-denetcide-yok",
        "donem-kimligi-cozulemedi",
        "oneri-olumsuz",
        "celiski",
        "cogunluk-yok",
    }


def test_engine_version_is_pinned_to_the_RULE_SURFACE() -> None:
    """Damga KURAL YÜZEYİNE bağlıdır — tautolojik bir sürüm testi DEĞİL.

    `ENGINE_VERSION` kendi belgesinde *"uygulama kuralı değiştiğinde ARTAR"*
    der. Bu hüküm 2026-09-11'de İKİ commit boyunca İHLAL EDİLDİ: yetkilendirme
    iddia düzeyine taşındı · K-126 istisnası açıldı · K-03 kategori ayağı
    çalışmaya başladı · sebep kümesi yediden on bire çıktı — damga `2.13.0`
    kaldı. Aynı damgayı taşıyan iki koşu maddi olarak FARKLI kurallarla karar
    veriyordu ve denetim ikisini ayırt edemezdi.

    Bu test sürümü TEK BAŞINA pinlemez (o tautoloji olurdu); sürümü kural
    yüzeyinin ÖLÇÜLEBİLİR parmak iziyle BİRLİKTE pinler. Kural yüzeyi
    değişip damga değişmezse test DÜŞER ve kararı insana taşır.
    """
    kural_yuzeyi = (
        len(UYGULANMAMA_SEBEPLERI),
        tuple(sorted(engine.KURAL_KIMLIKLERI)),
        tuple(sorted(etki.sinif for etki in engine.BULGU_ETKILERI)),
        tuple(kontrol.ad for kontrol in engine.CHECKS),
        # 2.15.0: not sınıfı kümesi de kural yüzeyidir — motorun günlüğe
        # yazabildiği sınıflar değişince eski koşuların günlüğü yenisiyle
        # karşılaştırılamaz.
        tuple(sorted(engine.identity.NOT_SINIFLARI)),
    )
    assert (engine.ENGINE_VERSION, kural_yuzeyi) == (
        "2.15.0",
        (
            11,
            (
                "celiski",
                "cogunluk-yok",
                "donem-kimligi-cozulemedi",
                "iddia-arastirmada-yok",
                "iddia-denetcide-yok",
                "kanit-yok",
                "kaynak-iddia-yok",
                "mutabakat-yok",
                "oneri-olumsuz",
                "referans-uyusmuyor",
                "referans-yok",
            ),
            (
                "acik_soru",
                "ikinci_aktif",
                "kapsam_ihlali",
                "mevzuat_dogrulanamadi",
                "mevzuat_uyusmazligi",
                "regresyon_kapisi",
            ),
            BEKLENEN_KONTROL_ADLARI,
            ("eslesmeyen-ozel-gun", "reddedilen-aday", "tur-kategori-catismasi"),
        ),
    ), (
        "kural yüzeyi değişti ama ENGINE_VERSION değişmedi (ya da tersi) — "
        "damga kendi hükmünü ihlal ediyor; kararı insan verir"
    )


def test_engine_result_carries_version_and_config_sha() -> None:
    """K-97: her sonuç motor sürümünü ve ayar hash'ini damgalar."""
    sonuc = _karar()
    assert sonuc.engine_version == engine.ENGINE_VERSION
    assert sonuc.engine_config_sha == config_sha(PolicyConfig())


def test_config_sha_changes_when_config_changes() -> None:
    taban = config_sha(PolicyConfig())
    assert config_sha(PolicyConfig(max_change_ratio=0.5)) != taban
    assert config_sha(PolicyConfig(block_on_legislation=True)) != taban


def test_config_sha_uses_identity_canonical_rule(monkeypatch) -> None:
    """K-92: ikinci bir hash kuralı YOK — `identity.canonical_sha` ÇAĞRILIR."""
    cagrildi: list[object] = []
    gercek = identity.canonical_sha

    def izle(deger):
        cagrildi.append(deger)
        return gercek(deger)

    monkeypatch.setattr(identity, "canonical_sha", izle)
    config_sha(PolicyConfig())
    assert cagrildi, "config_sha kendi hash kuralını yazıyor — kanonik kural ÇAĞRILMALI"


def test_decide_returns_policy_report_for_every_outcome() -> None:
    """K-93: üç sonucun ÜÇÜNDE de dolu bir `PolicyReport` vardır."""
    gorulen = {}
    for girdi, config in (
        (_uygulanan_guncelle(), PolicyConfig()),
        (_girdi(), PolicyConfig()),
        (_girdi(kapilar=engine.GateResults(katman1_passed=True, tek_aktif_ihlali=True)),
         PolicyConfig()),
    ):
        sonuc = engine.decide(girdi, config)
        gorulen[sonuc.sonuc] = sonuc
        assert type(sonuc.policy_report) is PolicyReport
    assert set(gorulen) == set(SONUCLAR), f"üç sonuç da üretilemedi: {sorted(gorulen)}"


def test_policy_report_constructed_only_in_engine_module() -> None:
    """H2'nin ispatı: `PolicyReport(` çağrısı YALNIZ `engine.py`'de.

    Muafiyet açıkça yazılıdır: tanım dosyası (`engine_contract.py`) ve `tests/`.
    """
    kok = Path(__file__).resolve().parents[1]
    desen = re.compile(r"\bPolicyReport\(")
    muaf = {kok / "app/services/sector_pipeline/engine_contract.py"}
    kuranlar = set()
    for yol in kok.rglob("*.py"):
        if kok / "tests" in yol.parents or yol in muaf:
            continue
        if desen.search(yol.read_text(encoding="utf-8")):
            kuranlar.add(yol.relative_to(kok).as_posix())
    assert kuranlar == {"app/services/sector_pipeline/engine.py"}


# ═══ 2. Dönüşüm tablosu — altı sınıfın altısı (arayüz eki R7) ══════════════


def test_finding_classes_all_have_a_consumer() -> None:
    """Yapısal kapı: kapalı kümenin HER değeri dönüşüm tablosunda geçer."""
    tablo = {etki.sinif: (etki.etki, etki.sebep) for etki in engine.BULGU_ETKILERI}
    assert tablo == BEKLENEN_DONUSUM


def test_kapsam_ihlali_finding_becomes_blocked() -> None:
    """Aktif birimin sonucu yoksa kapsam ihlali BLOKLAR."""
    hedef = _yol(AKTIF_ICERIK, "kapsam", AKTIF_ICERIK["kapsam"])
    gunluk = _gunluk(AKTIF_ICERIK, degis={hedef: {"unit_id": "ku-aaaaaaaaaaaa"}})
    sonuc = _karar(_girdi(gunluk=gunluk))
    assert sonuc.sonuc == "blocked"
    assert BEKLENEN_DONUSUM["kapsam_ihlali"][1] in sonuc.sebep


def test_mevzuat_uyusmazligi_always_becomes_blocked() -> None:
    """K-125 benimsendi: mevzuat uyuşmazlığı bayrağa BAKMADAN bloklar."""
    girdi = _guncelle_girdisi(
        alan=MEVZUAT_ALANI,
        eski=MEVZUAT_MADDESI,
        yeni_metin="Ayar beyani yeni yonetmelige baglidir",
        kanit=DOGRULANMIS_KAYNAK,
        statuler_1=MUTABIK_MEVZUAT,
        statuler_2={MEVZUAT_KIMLIGI: "supported"},
    )
    for config in (PolicyConfig(), PolicyConfig(block_on_legislation=True)):
        sonuc = engine.decide(girdi, config)
        assert sonuc.sonuc == "blocked"
        assert BEKLENEN_DONUSUM["mevzuat_uyusmazligi"][1] in sonuc.sebep


def test_mevzuat_dogrulanamadi_does_not_block_by_default() -> None:
    """K-128 PASİF: doğrulanamayan mevzuat varsayılan ayarda bloklamaz."""
    sonuc = _karar(_girdi(cift=_cift(statuler_1={MEVZUAT_KIMLIGI: "risk_unverified"})))
    assert sonuc.sonuc != "blocked"
    assert any(
        bulgu.sinif == "mevzuat_dogrulanamadi" for bulgu in sonuc.policy_report.bulgular
    )


def test_mevzuat_dogrulanamadi_blocks_when_flag_enabled() -> None:
    """POZİTİF KONTROL: yetenek kuruludur — bayrak açılınca gerçekten bloklar."""
    girdi = _girdi(cift=_cift(statuler_1={MEVZUAT_KIMLIGI: "risk_unverified"}))
    sonuc = engine.decide(girdi, PolicyConfig(block_on_legislation=True))
    assert sonuc.sonuc == "blocked"
    assert BEKLENEN_DONUSUM["mevzuat_dogrulanamadi"][1] in sonuc.sebep


def test_regression_gate_finding_prevents_activation_eligible() -> None:
    """Katman-1 geçmediyse sonuç `activation_eligible` OLAMAZ."""
    kapali = _uygulanan_guncelle(
        kapilar=engine.GateResults(katman1_passed=False, tek_aktif_ihlali=False)
    )
    sonuc = engine.decide(kapali, PolicyConfig())
    assert sonuc.sonuc != "activation_eligible"
    assert BEKLENEN_DONUSUM["regresyon_kapisi"][1] in sonuc.sebep


def test_second_active_finding_becomes_blocked() -> None:
    girdi = _girdi(kapilar=engine.GateResults(katman1_passed=True, tek_aktif_ihlali=True))
    sonuc = _karar(girdi)
    assert sonuc.sonuc == "blocked"
    assert BEKLENEN_DONUSUM["ikinci_aktif"][1] in sonuc.sebep


def test_acik_soru_finding_becomes_blocked() -> None:
    """Tüketilmemiş bayrak `acik_soru` bulgusudur — K-71 gereği bloklar."""
    hedef = _yol(AKTIF_ICERIK, "kapsam", AKTIF_ICERIK["kapsam"])
    gunluk = _gunluk(
        AKTIF_ICERIK, degis={hedef: {"gerekce": "Kalip [genel-gecer: dar degil]."}}
    )
    sonuc = _karar(_girdi(gunluk=gunluk))
    assert sonuc.sonuc == "blocked"
    assert BEKLENEN_DONUSUM["acik_soru"][1] in sonuc.sebep


def test_surviving_flag_does_not_block() -> None:
    """POZİTİF KONTROL: sentezden sağ çıkan TEK bayrak bloklamaz."""
    hedef = _yol(AKTIF_ICERIK, "kapsam", AKTIF_ICERIK["kapsam"])
    gunluk = _gunluk(
        AKTIF_ICERIK, degis={hedef: {"gerekce": "Kalip [kanal-bagimli: reels]."}}
    )
    sonuc = _karar(_girdi(gunluk=gunluk))
    assert sonuc.sonuc != "blocked"


def test_synthesis_open_questions_become_blocked() -> None:
    """İkinci kaynak: sentezin AÇIK SORUsu da aynı sonuca çıkar."""
    sonuc = _karar(_girdi(acik_sorular=("Ayar beyani icin kaynak yok",)))
    assert sonuc.sonuc == "blocked"
    assert BEKLENEN_DONUSUM["acik_soru"][1] in sonuc.sebep
    assert sonuc.policy_report.acik_soru_kimlikleri


# ═══ 3. K-23=B güvenli varsayılan ══════════════════════════════════════════


def test_undecided_item_keeps_pattern_and_does_not_block() -> None:
    """Kanıtsız `guncelle`: kalıp KORUNUR, koşu BLOKLANMAZ."""
    sonuc = _karar(_uygulanmayan_guncelle())
    assert sonuc.sonuc != "blocked"
    assert KORUNAN_KANCA in _kancalar(sonuc)
    assert GUNCELLENMIS_KANCA not in _kancalar(sonuc)


def test_undecided_item_appears_in_report() -> None:
    sonuc = _karar(_uygulanmayan_guncelle())
    kimlikler = [madde.unit_id for madde in sonuc.policy_report.kararsizlar]
    assert kimlikler, "kararsız madde rapora GİRMELİ (K-23=B)"
    assert all(madde.sebep for madde in sonuc.policy_report.kararsizlar)


def test_open_question_from_synthesis_still_blocks() -> None:
    """İki yol AYRIDIR: aynı koşuda kararsız bloklamaz, açık soru bloklar."""
    acik = _uygulanmayan_guncelle(acik_sorular=("Cozulmemis celiski",))
    sonuc = engine.decide(acik, PolicyConfig())
    assert sonuc.sonuc == "blocked"
    assert sonuc.policy_report.kararsizlar, "kararsız kayıt açık soruyla SİLİNMEZ"


def test_guncelle_without_evidence_is_not_applied() -> None:
    """R7'den taşındı — 'uygulanmaz' iddiasının sahibi bu katmandır."""
    sonuc = _karar(_uygulanmayan_guncelle())
    assert GUNCELLENMIS_KANCA not in _kancalar(sonuc)


def test_guncelle_with_evidence_is_applied() -> None:
    """POZİTİF KONTROL: kanıt ve mutabakat tamsa karar UYGULANIR."""
    sonuc = _karar(_uygulanan_guncelle())
    assert GUNCELLENMIS_KANCA in _kancalar(sonuc)
    assert sonuc.policy_report.kararsizlar == ()


def test_cikar_without_two_auditor_agreement_keeps_pattern() -> None:
    """Mutabakatsız `cikar`: öğe pakette KALIR."""
    sonuc = _karar(_cikar_girdisi(mutabik=False))
    assert CIKARILACAK_KANCA in _kancalar(sonuc)
    assert sonuc.sonuc != "blocked"


def test_cikar_with_agreement_is_applied() -> None:
    """POZİTİF KONTROL: iki denetçi de çelişki bildirdiyse öğe ÇIKAR."""
    sonuc = _karar(_cikar_girdisi(mutabik=True))
    assert CIKARILACAK_KANCA not in _kancalar(sonuc)


def test_new_item_needs_two_of_three() -> None:
    """Tek kaynaklı yeni kalıp nihai adaya YAZILMAZ."""
    sonuc = _karar(_basa_ekleme_girdisi(kanit=TEK_KAYNAKLI))
    assert "Yeni kanca kalibi" not in _kancalar(sonuc)


def test_new_item_with_two_sources_is_written() -> None:
    """POZİTİF KONTROL: iki kaynak çoğunluğu karşılar, kalıp pakete girer."""
    sonuc = _karar(_basa_ekleme_girdisi(kanit=IKI_KAYNAKLI))
    assert "Yeni kanca kalibi" in _kancalar(sonuc)


def test_unmatched_holiday_key_not_written() -> None:
    """Takvimde karşılığı olmayan anahtar nihai adaya GİRMEZ."""
    sonuc = _karar(_girdi(takvim=frozenset()))
    assert sonuc.final_candidate["ozel_gun"] == {}


def test_matched_holiday_key_is_kept() -> None:
    """POZİTİF KONTROL: takvimde karşılığı olan anahtar KORUNUR."""
    sonuc = _karar()
    assert TAKVIM_ANAHTARI in sonuc.final_candidate["ozel_gun"]


def test_category_conflict_package_type_wins() -> None:
    """K-03'ün ölçülebilen ayağı: paket TÜR etiketi nihai adaya yazılır."""
    sonuc = engine.decide(_tur_degisikligi_girdisi(), PolicyConfig())
    assert sonuc.final_candidate["ozel_gun"][TAKVIM_ANAHTARI]["tur"] == "anma"
    assert sonuc.engine_diff["paket_turu_degisiklikleri"]


# ═══ 4. Üç bariyer — mekanizma kurulu, eşikler pasif (İlke 9) ══════════════


def test_barrier_with_none_threshold_never_blocks() -> None:
    """Eşik `None` iken bariyer YALNIZ oranı yazar."""
    sonuc = _karar(_uygulanan_guncelle())
    assert sonuc.sonuc != "blocked"
    assert sonuc.barrier_report["oranlar"]["degisim"] > 0
    assert sonuc.barrier_report["asilan"] == ()


def test_barrier_with_set_threshold_blocks() -> None:
    """POZİTİF KONTROL: mekanizma gerçekten çalışıyor."""
    sonuc = engine.decide(_uygulanan_guncelle(), PolicyConfig(max_change_ratio=0.0))
    assert sonuc.sonuc == "blocked"
    assert SEBEP_BARIYER in sonuc.sebep
    assert "degisim" in sonuc.barrier_report["asilan"]


def test_first_run_zero_denominator_uses_absolute_limits() -> None:
    """İlk koşuda payda 0: oran hesaplanmaz, mutlak limit uygulanır."""
    girdi = _ilk_kosu_girdisi(kanit=IKI_KAYNAKLI)
    gevsek = engine.decide(girdi, PolicyConfig())
    assert gevsek.barrier_report["oranlar"]["ekleme"] is None
    assert gevsek.sonuc == "activation_eligible"

    siki = engine.decide(girdi, PolicyConfig(abs_limits={"ekleme": 0}))
    assert siki.sonuc == "blocked"
    assert SEBEP_BARIYER in siki.sebep


# ═══ 5. Sonuç kuralları (K-90 / K-91) ══════════════════════════════════════


def test_first_run_no_change_is_invalid() -> None:
    """K-91: ilk koşuda hiçbir karar uygulanmadıysa `no_change` GEÇERSİZDİR."""
    sonuc = _karar(_ilk_kosu_girdisi(kanit=TEK_KAYNAKLI))
    assert sonuc.sonuc == "blocked"
    assert SEBEP_ILK_KOSU in sonuc.sebep


def test_no_change_run_is_reported_as_no_change() -> None:
    """POZİTİF KONTROL: aktif pakette değişiklik yoksa sonuç `no_change`."""
    sonuc = _karar()
    assert sonuc.sonuc == "no_change"
    assert sonuc.sebep is None


def test_blocked_carries_reason() -> None:
    """K-90: `blocked` sonucu SEBEP taşımak zorundadır."""
    sonuc = _karar(_girdi(kapilar=engine.GateResults(katman1_passed=True, tek_aktif_ihlali=True)))
    assert sonuc.sonuc == "blocked"
    assert isinstance(sonuc.sebep, str) and sonuc.sebep.strip()


def test_outcome_stays_inside_the_closed_set() -> None:
    for girdi in (_girdi(), _uygulanan_guncelle(), _uygulanmayan_guncelle()):
        assert engine.decide(girdi, PolicyConfig()).sonuc in SONUCLAR


# ═══ 6. Kimlik (K-92) ══════════════════════════════════════════════════════


def test_canonical_sha_stable_across_key_order() -> None:
    ilk = engine.canonical_content_sha({"a": 1, "b": [1, 2]})
    ikinci = engine.canonical_content_sha({"b": [1, 2], "a": 1})
    assert ilk == ikinci


def test_canonical_sha_changes_on_list_order() -> None:
    """Sıra içeriğin PARÇASIDIR — liste sırası hash'i değiştirir."""
    assert engine.canonical_content_sha({"a": [1, 2]}) != engine.canonical_content_sha(
        {"a": [2, 1]}
    )


def test_content_sha_matches_the_final_candidate() -> None:
    sonuc = _karar(_uygulanan_guncelle())
    assert sonuc.content_sha == identity.canonical_sha(sonuc.final_candidate)
    assert sonuc.decision_log_sha == identity.canonical_sha(sonuc.final_decision_log)


# ═══ 7. K-96 / K-145 — iz ve provenans ═════════════════════════════════════


def test_engine_diff_preserves_original_synthesis() -> None:
    """K-96: sentez raporu YERİNDE DEĞİŞTİRİLMEZ; reddedilen `engine_diff`'e yazılır."""
    girdi = _uygulanmayan_guncelle()
    sonuc = engine.decide(girdi, PolicyConfig())
    assert GUNCELLENMIS_KANCA in girdi.sentez.aday_json["kanca_kaliplari"]
    assert sonuc.engine_diff["uygulanmayan_kararlar"]


def test_engine_diff_records_rule_provenance() -> None:
    """K-145: REDDEDİLENLERİN izi kural damgası taşır."""
    sonuc = _karar(_uygulanmayan_guncelle())
    kayit = sonuc.engine_diff["uygulanmayan_kararlar"][0]
    assert kayit["kural_kimligi"]
    assert kayit["kural_surumu"] == engine.ENGINE_VERSION


def test_applied_motor_rows_carry_rule_stamp() -> None:
    """K-145: UYGULANAN motor satırının izi karar GÜNLÜĞÜNDE yaşar."""
    sonuc = _karar(_uygulanmayan_guncelle())
    motor_satirlari = [
        satir for satir in sonuc.final_decision_log if satir["aktor"] == "motor"
    ]
    assert motor_satirlari, "kalıbı koruyan karar motorun kendi satırıdır"
    for satir in motor_satirlari:
        assert satir["kural_kimligi"] and satir["kural_surumu"]
    assert identity.validate_decision_log([dict(s) for s in sonuc.final_decision_log]) == []


def test_synthesis_rows_keep_their_actor() -> None:
    """Uygulanan sentez kararı motorun satırına DÖNÜŞMEZ (F19 ayrımı)."""
    sonuc = _karar(_uygulanan_guncelle())
    aktorler = {satir["aktor"] for satir in sonuc.final_decision_log}
    assert aktorler == {"sentez"}


# ═══ 8. Nihai çiftin bütünlüğü + konumsal yol kapısı ═══════════════════════


def test_final_pair_passes_the_writing_gate() -> None:
    """Nihai içerik + günlük ÇİFTİ yazım kapısını ve bütünlük kapısını geçer."""
    sonuc = _karar(_uygulanmayan_guncelle())
    icerik = identity.cozulmus(sonuc.final_candidate)
    gunluk = [identity.cozulmus(satir) for satir in sonuc.final_decision_log]
    assert structural_errors(icerik) == []
    assert identity.check_unit_integrity(icerik, gunluk) == []


def test_paths_are_renumbered_after_a_rejected_addition() -> None:
    """Reddedilen ekleme listeyi kaydırır; günlük KİMLİĞE göre yeniden numaralanır."""
    sonuc = _karar(_basa_ekleme_girdisi(kanit=DOGRULANMIS_KAYNAK))
    icerik = identity.cozulmus(sonuc.final_candidate)
    gunluk = [identity.cozulmus(satir) for satir in sonuc.final_decision_log]
    assert identity.check_unit_integrity(icerik, gunluk) == []
    korunan_yol = _yol(icerik, "kanca_kaliplari", KORUNAN_KANCA)
    satir = next(s for s in gunluk if s["unit_id"] == KIMLIKLER[_yol(AKTIF_ICERIK, "kanca_kaliplari", KORUNAN_KANCA)])
    assert satir["oge_yolu"] == korunan_yol


def test_decide_does_not_swallow_input_errors() -> None:
    """Girdi kapısı düşerse `decide` onu `blocked`'a ÇEVİRMEZ — çağırana bırakır."""
    bozuk = _girdi(kapi=bd.gate_round([]))
    with pytest.raises(engine.EngineInputError):
        engine.decide(bozuk, PolicyConfig())


# ═══ 9. Checkpoint 10 hakem turunun kapattığı sınıflar ═════════════════════
#
# Altı bulgunun altısı da kontrolörün KENDİ probuyla doğrulandı (ezberden kabul
# edilmedi); aşağıdaki testler o probların kalıcı hâlidir.


def _koru_ihlali_girdisi(*, ek_guncelle: bool = False):
    """Aday yükü değişmiş ama satır `koru` diyor — "değişmedi" iddiası YALAN."""
    degismis = "Sessizce degistirilmis kanca kalibi"
    aday = _tam_icerik(kanca_kaliplari=[degismis, CIKARILACAK_KANCA])
    degis = {}
    if ek_guncelle:
        cikan_yol = _yol(aday, "kanca_kaliplari", CIKARILACAK_KANCA)
        aday = _tam_icerik(kanca_kaliplari=[degismis, GUNCELLENMIS_KANCA])
        degis = {
            _yol(aday, "kanca_kaliplari", GUNCELLENMIS_KANCA): {
                "karar": "guncelle",
                "kanit": DOGRULANMIS_KAYNAK,
            }
        }
        del cikan_yol
    return _girdi(
        icerik=aday,
        gunluk=_gunluk(aday, degis=degis),
        cift=_cift(
            statuler_1={CIKAN_KIMLIK: "needs_update"},
            statuler_2={CIKAN_KIMLIK: "needs_update"},
        ),
    )


def test_changed_value_labelled_koru_is_restored() -> None:
    """`koru` satırının iddiası uygulanır, aday yükünün iddiası DEĞİL.

    Ölçüldü (checkpoint 10, yüksek): sessizce değiştirilmiş bir kalıp `koru`
    etiketiyle geçiyor, koşu `no_change` diyordu — kanıt, mutabakat ve bariyer
    kontrollerinin ÜÇÜ birden atlanıyordu.
    """
    sonuc = _karar(_koru_ihlali_girdisi())
    assert KORUNAN_KANCA in _kancalar(sonuc)
    assert "Sessizce degistirilmis kanca kalibi" not in _kancalar(sonuc)
    assert sonuc.sonuc == "no_change"


def test_koru_violation_is_traced_in_engine_diff() -> None:
    """Geri alınan `koru` ihlali SESSİZ olmaz — izi `engine_diff`'e düşer."""
    sonuc = _karar(_koru_ihlali_girdisi())
    assert sonuc.engine_diff["koru_ihlalleri"]


def test_legitimate_change_survives_next_to_a_koru_violation() -> None:
    """POZİTİF KONTROL: ihlal geri alınırken meşru karar UYGULANMAYA devam eder."""
    sonuc = _karar(_koru_ihlali_girdisi(ek_guncelle=True))
    assert GUNCELLENMIS_KANCA in _kancalar(sonuc)
    assert KORUNAN_KANCA in _kancalar(sonuc)


def test_accepted_cikar_is_counted_logged_and_measured() -> None:
    """Kabul edilen çıkarma: sonuç · günlük satırı · bariyer payı — ÜÇÜ de.

    Ölçüldü: yol-varlığına bakan sınıflandırma kabul edilen `cikar`'ı hem
    günlükten hem `uygulanan` kümesinden düşürüyor, koşu `no_change` diyordu.
    """
    sonuc = _karar(_cikar_girdisi(mutabik=True))
    assert sonuc.sonuc == "activation_eligible"
    assert any(satir.get("karar") == "cikar" for satir in sonuc.final_decision_log)
    assert sonuc.barrier_report["sayilar"]["degisim"] == 1


def test_rejected_cikar_produces_exactly_one_motor_row() -> None:
    """Bir birim bir günlükte TEK sonuç alır — çift motor satırı şemayı düşürür."""
    sonuc = _karar(_cikar_girdisi(mutabik=False))
    satirlar = [
        satir for satir in sonuc.final_decision_log if satir.get("unit_id") == CIKAN_KIMLIK
    ]
    assert len(satirlar) == 1
    assert satirlar[0]["aktor"] == "motor"
    assert identity.validate_decision_log(
        [identity.cozulmus(satir) for satir in sonuc.final_decision_log]
    ) == []


def _cta_girdisi():
    """Yapılandırılmış (nesne) bir öğenin kanıtsız `guncelle`si."""
    cta_yol = _yol(AKTIF_ICERIK, "cta_kaliplari", AKTIF_ICERIK["cta_kaliplari"][0])
    kimlik = KIMLIKLER[cta_yol]
    aday = _tam_icerik(
        cta_kaliplari=[
            {"kalip": "Yeni cta kalibi", "tur": "ziyaret", "gerekce": "Yeni gerekce."}
        ]
    )
    return _girdi(
        icerik=aday,
        gunluk=_gunluk(aday, degis={cta_yol: {"karar": "guncelle", "kanit": COZULEMEYEN_KANIT}}),
        cift=_cift(statuler_1={kimlik: "needs_update"}, statuler_2={kimlik: "needs_update"}),
    )


def test_rejected_update_of_structured_item_does_not_block() -> None:
    """K-23=B temsil tipine takılmaz: donmuş aktif değer adaya ÇÖZÜLEREK girer.

    Ölçüldü: `mappingproxy` bir CTA öğesi yazım kapısını geçmiyor ve sıradan bir
    kanıtsız `guncelle` bütün koşuyu BLOKLUYORDU.
    """
    sonuc = _karar(_cta_girdisi())
    assert sonuc.sonuc != "blocked"
    assert sonuc.final_candidate is not None
    assert sonuc.final_candidate["cta_kaliplari"][0]["kalip"] == (
        AKTIF_ICERIK["cta_kaliplari"][0]["kalip"]
    )
    assert structural_errors(identity.cozulmus(sonuc.final_candidate)) == []


def test_one_unit_counts_once_even_with_two_reasons() -> None:
    """K-132 motorun ACZİNİ ölçer, kaç kontrolün aynı birime dokunduğunu değil."""
    yol = _yol(AKTIF_ICERIK, "kanca_kaliplari", KORUNAN_KANCA)
    kimlik = KIMLIKLER[yol]
    aday = _tam_icerik(kanca_kaliplari=[GUNCELLENMIS_KANCA, CIKARILACAK_KANCA])
    girdi = _girdi(
        icerik=aday,
        gunluk=_gunluk(aday, degis={yol: {"karar": "guncelle", "kanit": COZULEMEYEN_KANIT}}),
        cift=_cift(statuler_1={kimlik: "needs_update"}, statuler_2={kimlik: "supported"}),
    )
    sonuc = engine.decide(girdi, PolicyConfig())
    sebepler = {kayit.sebep for kayit in sonuc.policy_report.uygulanmayan_kararlar}
    assert len(sebepler) == 2, f"fixture iki sebep üretmeli: {sebepler}"
    assert len(sonuc.policy_report.kararsizlar) == 1
    assert sonuc.barrier_report["sayilar"]["kararsizlik"] == 1


def test_unmatched_key_note_and_application_share_one_predicate(monkeypatch) -> None:
    """Not üreticisi ile uygulayıcı AYNI yüklemi ÇAĞIRIR — sayı eşitliği değil.

    Sayıların eşitliği iki AYRI döngüyle de sağlanabilirdi; oradan "tek kural"
    sonucu çıkmaz. Yüklem susturulunca İKİ yolun da susması, paylaşımın kendisini
    ölçer.
    """
    girdi = _girdi(takvim=frozenset())
    normal_notlar = [
        satir
        for satir in engine.run_checks(girdi).notlar
        if satir["sinif"] == "eslesmeyen-ozel-gun"
    ]
    normal_sonuc = engine.decide(girdi, PolicyConfig())
    assert normal_notlar and normal_sonuc.engine_diff["eslesmeyen_ozel_gunler"] == (
        TAKVIM_ANAHTARI,
    )

    monkeypatch.setattr(engine, "_eslesmeyen_ozel_gunler", lambda icerik, takvim: ())
    susturulmus_notlar = [
        satir
        for satir in engine.run_checks(girdi).notlar
        if satir["sinif"] == "eslesmeyen-ozel-gun"
    ]
    susturulmus = engine.decide(girdi, PolicyConfig())
    assert susturulmus_notlar == []
    assert susturulmus.engine_diff["eslesmeyen_ozel_gunler"] == ()
    assert TAKVIM_ANAHTARI in susturulmus.final_candidate["ozel_gun"]


def test_invalid_final_pair_blocks_instead_of_shipping(monkeypatch) -> None:
    """POZİTİF KONTROL: çift bütünlük kapısını geçmiyorsa sonuç ÜRETİLMEZ."""
    gercek = engine._nihai_gunluk

    def bozuk(inputs, outcome, reddedilen, nihai, yollar):
        gunluk, uygulanan = gercek(inputs, outcome, reddedilen, nihai, yollar)
        return gunluk + (dict(gunluk[0]),), uygulanan  # aynı birim İKİ satır

    monkeypatch.setattr(engine, "_nihai_gunluk", bozuk)
    sonuc = _karar()
    assert sonuc.sonuc == "blocked"
    assert "uygulanan-cift-butunluk-kapisini-gecmiyor" in sonuc.sebep
    assert sonuc.final_candidate is None and sonuc.final_decision_log is None
    assert sonuc.content_sha is None and sonuc.decision_log_sha is None


# ── Üretilmiş matris: ekleme × çıkarma × yineleme ─────────────────────────
#
# Sınıf, ELLE seçilmiş bir örnekle değil ÜRETİLMİŞ matrisle kapatılır: konum ×
# kabul × çıkarma × yinelenen değer. Boş-küme kontrol kolu (ekleme yok, çıkarma
# yok) matrise DÂHİLDİR — hiçbir şey olmayan turda da çift geçerli kalmalı.

_MATRIS = [
    (konum, ekleme_kabul, cikarma, yinelenen)
    for konum in (None, 0, 1, 2)
    for ekleme_kabul in (True, False)
    for cikarma in (None, "kabul", "red")
    for yinelenen in (False, True)
    if not (konum is None and (ekleme_kabul is False or yinelenen))
]


def _matris_girdisi(konum, ekleme_kabul, cikarma, yinelenen):
    yeni = KORUNAN_KANCA if yinelenen else "Yeni kanca kalibi"
    liste = [KORUNAN_KANCA, CIKARILACAK_KANCA]
    if cikarma is not None:
        liste.remove(CIKARILACAK_KANCA)
    if konum is not None:
        liste.insert(min(konum, len(liste)), yeni)
    aday = _tam_icerik(kanca_kaliplari=liste)

    # Kimlik haritası KONUMU BİLEREK kurulur: yinelenen değerde değere göre
    # eşleme iki satıra aynı kimliği verirdi (fixture'ın kendi tuzağı).
    yeni_yol = None
    harita: dict[str, str] = {}
    for sira, deger in enumerate(liste):
        yol = f"kanca_kaliplari[{sira}]"
        if konum is not None and sira == min(konum, len(liste) - 1) and deger == yeni:
            harita[yol] = "ku-f00000000001"
            yeni_yol = yol
        else:
            harita[yol] = KIMLIKLER[_yol(AKTIF_ICERIK, "kanca_kaliplari", deger)]
    for yol in identity.enumerate_content_units(aday):
        # `setdefault(yol, KIMLIKLER[yol])` OLMAZ: varsayılan, anahtar VARKEN de
        # değerlendirilir ve adayda doğmuş yol için `KeyError` fırlatır.
        if yol not in harita:
            harita[yol] = KIMLIKLER[yol]

    degis = {}
    if yeni_yol is not None:
        kanit = IKI_KAYNAKLI if ekleme_kabul else TEK_KAYNAKLI
        degis[yeni_yol] = {"karar": "ekle", "kanit": kanit}

    ek: tuple = ()
    statuler = {}
    if cikarma is not None:
        cikan_yol = _yol(AKTIF_ICERIK, "kanca_kaliplari", CIKARILACAK_KANCA)
        birim = identity.enumerate_content_units(AKTIF_ICERIK)[cikan_yol]
        ek = (
            {
                "tur": "karar",
                "alan": birim["alan"],
                "oge_yolu": cikan_yol,
                "unit_id": CIKAN_KIMLIK,
                "oge_sha": birim["oge_sha"],
                "karar": "cikar",
                "gerekce": "Kaynaklar celisti.",
                "kanit": DOGRULANMIS_KAYNAK,
                "aktor": "sentez",
            },
        )
        statuler = {
            CIKAN_KIMLIK: "contradicted" if cikarma == "kabul" else "supported"
        }
    return _girdi(
        icerik=aday,
        gunluk=_gunluk(aday, kimlikler=harita, degis=degis, ek=ek),
        cift=_cift(
            statuler_1={CIKAN_KIMLIK: "contradicted"} if cikarma else None,
            statuler_2=statuler or None,
        ),
    )


@pytest.mark.parametrize("konum,ekleme_kabul,cikarma,yinelenen", _MATRIS)
def test_addition_removal_matrix_keeps_pair_valid_and_order_stable(
    konum, ekleme_kabul, cikarma, yinelenen
) -> None:
    """Her hücrede: çift geçerli · aktif komşuluk korunur · karar uygulanır."""
    sonuc = engine.decide(
        _matris_girdisi(konum, ekleme_kabul, cikarma, yinelenen), PolicyConfig()
    )
    assert sonuc.sonuc in SONUCLAR
    assert sonuc.final_candidate is not None, f"çift üretilemedi: {sonuc.sebep}"
    icerik = identity.cozulmus(sonuc.final_candidate)
    gunluk = [identity.cozulmus(satir) for satir in sonuc.final_decision_log]
    assert structural_errors(icerik) == []
    assert identity.validate_decision_log(gunluk) == []
    assert identity.check_unit_integrity(icerik, gunluk) == []

    liste = list(icerik["kanca_kaliplari"])
    # Çıkarma: kabul edilirse öğe YOK, reddedilirse KORUNUR (K-23=B).
    assert (CIKARILACAK_KANCA in liste) is (cikarma != "kabul")
    # Ekleme: çoğunluğu karşılamayan kalıp pakete GİRMEZ.
    beklenen_korunan = 1 + (1 if (yinelenen and ekleme_kabul) else 0)
    assert liste.count(KORUNAN_KANCA) == beklenen_korunan
    if konum is not None and not yinelenen:
        assert ("Yeni kanca kalibi" in liste) is ekleme_kabul
    # Aktif komşuluk: iki aktif kalıp da hayattaysa AKTİF sıraları korunur.
    if CIKARILACAK_KANCA in liste:
        assert liste.index(KORUNAN_KANCA) < liste.index(CIKARILACAK_KANCA)


def test_motor_row_provenance_follows_declared_precedence() -> None:
    """İki sebep varsa motor satırının provenansı ÖNCELİK sırasıyla seçilir.

    "Son yazan kazanır" bir kural değildir: kontrol çağrı sırası provenansı
    belirlerse aynı girdi, kontrol kümesinin sırası değiştiğinde başka bir kural
    kimliği damgalar.
    """
    yol = _yol(AKTIF_ICERIK, "kanca_kaliplari", KORUNAN_KANCA)
    kimlik = KIMLIKLER[yol]
    aday = _tam_icerik(kanca_kaliplari=[GUNCELLENMIS_KANCA, CIKARILACAK_KANCA])
    sonuc = engine.decide(
        _girdi(
            icerik=aday,
            gunluk=_gunluk(aday, degis={yol: {"karar": "guncelle", "kanit": COZULEMEYEN_KANIT}}),
            cift=_cift(statuler_1={kimlik: "needs_update"}, statuler_2={kimlik: "supported"}),
        ),
        PolicyConfig(),
    )
    motor = [
        satir
        for satir in sonuc.final_decision_log
        if satir.get("unit_id") == kimlik and satir.get("aktor") == "motor"
    ]
    assert len(motor) == 1
    assert motor[0]["kural_kimligi"] == engine.KURAL_KIMLIKLERI["kanit-yok"]


def _takvimden_dusen_donem_girdisi(*, takvim: frozenset, mutabik: bool):
    """Aday dönemi TAMAMEN çıkarır; çıkarma kararları çağırana göre kabul/red."""
    aday = _tam_icerik()
    aday["ozel_gun"] = {}
    aktif = identity.enumerate_content_units(AKTIF_ICERIK)
    ek, kimlikler = [], []
    for yuva in SPECIAL_DAY_SLOTS:
        yol = f"ozel_gun/{TAKVIM_ANAHTARI}/{yuva}"
        birim = aktif[yol]
        kimlik = KIMLIKLER[yol]
        kimlikler.append(kimlik)
        ek.append(
            {
                "tur": "karar",
                "alan": "ozel_gun",
                "oge_yolu": yol,
                "unit_id": kimlik,
                "oge_sha": birim["oge_sha"],
                "karar": "cikar",
                "gerekce": "Donem gecti.",
                "kanit": DOGRULANMIS_KAYNAK,
                "aktor": "sentez",
            }
        )
    return _girdi(
        icerik=aday,
        gunluk=_gunluk(aday, ek=tuple(ek)),
        takvim=takvim,
        cift=_cift(
            statuler_1={k: "contradicted" for k in kimlikler},
            statuler_2={k: "contradicted" if mutabik else "supported" for k in kimlikler},
        ),
    )


def test_restored_unmatched_calendar_key_stays_out() -> None:
    """Geri koyma takvim kapısını ATLAYAMAZ (F7, checkpoint 10 turu 2).

    Adayın TAMAMEN çıkardığı bir dönem, kural yalnız adaya sorulduğunda kümeye
    hiç girmiyordu; çıkarma reddedilince kalıp geri konuyor ve takvimde
    karşılığı olmayan dönem pakete SESSİZCE giriyordu — tüm kapılar "başarılı"
    diyordu.
    """
    sonuc = _karar(_takvimden_dusen_donem_girdisi(takvim=frozenset(), mutabik=False))
    assert sonuc.final_candidate["ozel_gun"] == {}
    assert TAKVIM_ANAHTARI in sonuc.engine_diff["eslesmeyen_ozel_gunler"]
    gunluk = [identity.cozulmus(satir) for satir in sonuc.final_decision_log]
    assert identity.check_unit_integrity(
        identity.cozulmus(sonuc.final_candidate), gunluk
    ) == []


def test_restored_matching_calendar_key_is_kept() -> None:
    """POZİTİF KONTROL: takvimde KARŞILIĞI OLAN dönem geri konar ve KALIR."""
    sonuc = _karar(
        _takvimden_dusen_donem_girdisi(takvim=frozenset({TAKVIM_ANAHTARI}), mutabik=False)
    )
    assert TAKVIM_ANAHTARI in sonuc.final_candidate["ozel_gun"]
    assert sonuc.engine_diff["eslesmeyen_ozel_gunler"] == ()


def test_accepted_calendar_removal_leaves_the_period_out() -> None:
    """POZİTİF KONTROL: kabul edilen çıkarma dönemi zaten dışarıda bırakır."""
    sonuc = _karar(
        _takvimden_dusen_donem_girdisi(takvim=frozenset({TAKVIM_ANAHTARI}), mutabik=True)
    )
    assert sonuc.final_candidate["ozel_gun"] == {}
    assert sonuc.sonuc == "activation_eligible"


def test_dropped_unit_bucket_carries_only_unit_ids() -> None:
    """Düşen BİRİM kovası yalnız kimlik taşır — takvim ANAHTARI oraya girmez.

    Sınıf yapısal kapanır: kovanın her üyesi kimlik biçimini taşımak zorundadır.
    Varyantı (takvim anahtarı) tek tek kovalamak yerine kovanın TÜRÜ sınanır —
    ikinci bir yabancı tür eklendiğinde de bu test kırılır.
    """
    for girdi in (
        _takvimden_dusen_donem_girdisi(takvim=frozenset(), mutabik=False),
        _girdi(takvim=frozenset()),
        _basa_ekleme_girdisi(kanit=DOGRULANMIS_KAYNAK),
        _girdi(),
    ):
        sonuc = engine.decide(girdi, PolicyConfig())
        kovalar = sonuc.engine_diff["dusen_birimler"]
        for ad, uyeler in kovalar.items():
            for uye in uyeler:
                assert identity.UNIT_ID_RE.match(uye), f"{ad} kimlik olmayan üye taşıyor: {uye!r}"
        assert sonuc.engine_diff["dusen_birim_sayisi"] == sum(
            len(uyeler) for uyeler in kovalar.values()
        )


def test_dropped_unit_count_excludes_calendar_keys() -> None:
    """Düşen dönemin BEŞ yuvası beş birimdir; anahtarın kendisi birim DEĞİLDİR."""
    sonuc = _karar(_takvimden_dusen_donem_girdisi(takvim=frozenset(), mutabik=False))
    assert sonuc.engine_diff["eslesmeyen_ozel_gunler"] == (TAKVIM_ANAHTARI,)
    assert sonuc.engine_diff["dusen_birim_sayisi"] == len(SPECIAL_DAY_SLOTS)


# ═══ Kalıcı yükün TİPLİ okuyucusu (hakem turu 2, yüksek) ═══════════════════


def test_policy_report_payload_roundtrips_through_the_typed_reader() -> None:
    """POZİTİF KONTROL: kanonik yük tam olarak geri okunur."""
    rapor = _karar(_girdi()).policy_report

    assert PolicyReport.from_payload(rapor.as_payload()) == rapor


@pytest.mark.parametrize(
    "yuk",
    [
        {
            "kararsizlar": 1,
            "bulgular": [{}],
            "uygulanmayan_kararlar": None,
            "acik_soru_kimlikleri": [],
        },
        {"kararsizlar": [], "bulgular": [], "uygulanmayan_kararlar": []},
        {
            "kararsizlar": [],
            "bulgular": [],
            "uygulanmayan_kararlar": [],
            "acik_soru_kimlikleri": [],
            "fazladan": 1,
        },
        {
            "kararsizlar": [],
            "bulgular": [
                {"sinif": "uydurma", "unit_id": None, "detay": "x", "kontrol": ""}
            ],
            "uygulanmayan_kararlar": [],
            "acik_soru_kimlikleri": [],
        },
        {
            "kararsizlar": [],
            "bulgular": [],
            "uygulanmayan_kararlar": [],
            "acik_soru_kimlikleri": [1],
        },
    ],
    ids=[
        "tipsiz-alanlar",
        "eksik-anahtar",
        "fazladan-anahtar",
        "kapali-kume-disi-sinif",
        "metin-olmayan-acik-soru",
    ],
)
def test_policy_report_from_payload_refuses_malformed(yuk) -> None:
    """Sözleşmeye uymayan yük SESSİZ boş rapora düşmez."""
    with pytest.raises((TypeError, ValueError)):
        PolicyReport.from_payload(yuk)


def _kanonik_yuk() -> dict:
    """Her alanı DOLU kanonik yük — mutasyon matrisinin tabanı."""
    return {
        "kararsizlar": [{"unit_id": "ku-000000000001", "sebep": "kanıt yok"}],
        "bulgular": [
            {
                "sinif": "acik_soru",
                "unit_id": "ku-000000000001",
                "detay": "açık soru var",
                "kontrol": "acik-soru",
            }
        ],
        "uygulanmayan_kararlar": [
            {
                "unit_id": "ku-000000000001",
                "karar": "koru",
                "sebep": next(iter(UYGULANMAMA_SEBEPLERI)),
            }
        ],
        "acik_soru_kimlikleri": ["as-1"],
    }


class _SahteMetin(str):
    """`str` ALT SINIFI — üyelik eşitliğini geçer, tip kapısından GEÇMEMELİ."""


class _EsitlikTaklidi:
    """Metin OLMAYAN ama eşitliği taklit eden nesne (alias vakası)."""

    def __init__(self, deger: str) -> None:
        self._deger = deger

    def __eq__(self, other: object) -> bool:
        return other == self._deger

    def __hash__(self) -> int:
        return hash(self._deger)


def _yaprak_matrisi() -> list:
    """Her öğe alanı × her yanlış tip — ÜRETİLMİŞ matris, elle seçim YOK.

    Kapalı-küme alanları (`sinif` · `karar` · `sebep`) için iki vaka AYRICA
    üretilir: `str` alt sınıfı ve eşitliği taklit eden nesne. Üyelik eşitliği
    ikisini de "üye" sayar; tip kapısı ikisini de reddetmelidir (hakem turu 4).
    """
    yanlis_degerler = (7, True, None, [], {}, 1.5)
    vakalar = []
    taban = _kanonik_yuk()
    for liste_adi in ("kararsizlar", "bulgular", "uygulanmayan_kararlar"):
        for alan in taban[liste_adi][0]:
            for deger in yanlis_degerler:
                if alan == "unit_id" and liste_adi == "bulgular" and deger is None:
                    continue  # `BulguIzi.unit_id` MEŞRU olarak None olabilir
                vakalar.append((liste_adi, alan, deger))
    kapali_kume_alanlari = (
        ("bulgular", "sinif", "acik_soru"),
        ("uygulanmayan_kararlar", "karar", "koru"),
        ("uygulanmayan_kararlar", "sebep", next(iter(UYGULANMAMA_SEBEPLERI))),
    )
    for liste_adi, alan, gecerli in kapali_kume_alanlari:
        vakalar.append((liste_adi, alan, _SahteMetin(gecerli)))
        vakalar.append((liste_adi, alan, _EsitlikTaklidi(gecerli)))
    return vakalar


@pytest.mark.parametrize(
    ("liste_adi", "alan", "deger"),
    _yaprak_matrisi(),
    ids=lambda d: str(d),
)
def test_policy_report_from_payload_refuses_every_malformed_leaf(
    liste_adi, alan, deger
) -> None:
    """YAPRAK alanların tipi de sözleşmenin parçasıdır (hakem turu 3, yüksek).

    Anotasyonlar çalışma zamanında tip ZORLAMAZ; kapı yalnız anahtar kümesine
    baksaydı `{"unit_id": 7, "sebep": []}` biçiminde bir öğe geçerdi ve hazırlık
    listesi onu "geçerli, temiz rapor" diye okurdu. Kapanış elle seçilmiş bir
    örnekle değil, ÜRETİLMİŞ matrisle kanıtlanır.
    """
    yuk = _kanonik_yuk()
    yuk[liste_adi][0][alan] = deger

    with pytest.raises((TypeError, ValueError)):
        PolicyReport.from_payload(yuk)

