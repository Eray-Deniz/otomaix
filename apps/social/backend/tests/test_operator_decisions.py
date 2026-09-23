"""Operatör kararları — açık soruların kapanış yolu (migration 037, Eray 2026-09-23).

Girdi Task 12'nin fixture'ıdır: aktif paket var, motor değişiklik uygulamıyor ve
koşuyu durduran TEK sebep sentezin açık sorusudur (pozitif kontrol aşağıda).
"""

from __future__ import annotations

import itertools
import uuid

import pytest

from app.core.database import _init_connection
from app.services.sector_content_schema import SPECIAL_DAY_SLOTS
from app.services.sector_pipeline import approval, engine, identity, runs
from app.services.sector_pipeline import operator_decisions as od
from app.services.sector_pipeline.policy_config import PolicyConfig
from tests.test_policy_engine_checks import (
    AKTIF_ICERIK,
    KIMLIKLER,
    TAKVIM_ANAHTARI,
    _girdi,
)

SORU_1 = "**Ayar beyanı** — iki denetçi farklı okudu."
SORU_2 = "**Kasım indirimi** — dönem girsin mi?"
ACTOR = "eray"
YENI_ANAHTAR = "anneler-gunu"
TAKVIM = frozenset({TAKVIM_ANAHTARI, YENI_ANAHTAR})
CTA = {"kalip": "Randevu ile ücretsiz temizlik", "tur": "hizmet", "gerekce": "Operatör."}


def _motor(acik_sorular=(SORU_1, SORU_2)):
    girdi = _girdi(acik_sorular=acik_sorular)
    return engine.decide(girdi, PolicyConfig()), girdi


def _kimlik_uretici():
    sayac = itertools.count(1)
    return lambda: f"ku-{next(sayac):012x}".replace("ku-0", "ku-f", 1)


def _uygula(dosya, *, sonuc=None, sorular=(SORU_1, SORU_2), takvim=TAKVIM):
    if sonuc is None:
        sonuc, _ = _motor(sorular)
    return od.uygula(
        sonuc,
        dosya=dosya,
        sentez_sorulari=sorular,
        takvim_anahtarlari=takvim,
        actor=ACTOR,
        yeni_kimlik=_kimlik_uretici(),
    )


def _cevaplar(**islemler) -> dict:
    return {
        "kararlar": [
            {"soru": "S1", "cevap": "Ayar beyanı girmesin.", "islemler": islemler.get("S1", [])},
            {"soru": "S2", "cevap": "Kasım dönemi girmesin.", "islemler": islemler.get("S2", [])},
        ]
    }


def _yol(icerik: dict, unit_id: str, gunluk) -> str:
    for satir in gunluk:
        if satir.get("unit_id") == unit_id and satir.get("tur") == "karar":
            return satir["oge_yolu"]
    raise AssertionError(unit_id)


# ═══ Pozitif kontrol — fixture tam olarak ölçmek istediğimiz durumu kuruyor ═══


def test_fixture_is_blocked_only_by_open_questions() -> None:
    sonuc, _ = _motor()
    assert sonuc.sonuc == "blocked"
    assert sonuc.sebep == od.ACIK_SORU_SEBEBI
    assert sonuc.policy_report.acik_soru_kimlikleri == (SORU_1, SORU_2)


# ═══ Soru kapsamı ═══════════════════════════════════════════════════════════


def test_answering_every_question_without_change_gives_no_change() -> None:
    """Motor değişiklik uygulamadı, operatör de işlem yapmadı → `no_change`."""
    yeni, kayit = _uygula(_cevaplar())
    assert yeni.sonuc == "no_change"
    assert yeni.sebep is None
    assert yeni.policy_report.acik_soru_kimlikleri == ()
    assert [k["soru"] for k in kayit["kararlar"]] == ["S1", "S2"]
    assert kayit["kararlar"][0]["soru_metni"] == SORU_1


def test_policy_report_keeps_everything_but_answered_questions() -> None:
    sonuc, _ = _motor()
    yeni, _ = _uygula(_cevaplar(), sonuc=sonuc)
    assert yeni.policy_report.bulgular == sonuc.policy_report.bulgular
    assert yeni.policy_report.kararsizlar == sonuc.policy_report.kararsizlar
    assert yeni.engine_version == sonuc.engine_version


@pytest.mark.parametrize(
    "dosya,parca",
    [
        ({"kararlar": [{"soru": "S1", "cevap": "x"}]}, "cevaplanmayan açık soru: ['S2']"),
        (
            {"kararlar": [{"soru": "S1", "cevap": "x"}, {"soru": "S1", "cevap": "y"},
                          {"soru": "S2", "cevap": "z"}]},
            "birden fazla kez",
        ),
        ({"kararlar": [{"soru": "S9", "cevap": "x"}]}, "tanınmayan soru"),
        ({"kararlar": [{"soru": "S1", "cevap": " "}, {"soru": "S2", "cevap": "x"}]}, "cevap boş"),
        ({"cevaplar": []}, "biçiminde olmalı"),
        (
            {"kararlar": [{"soru": "S1", "soru_basi": "**Kasım", "cevap": "x"},
                          {"soru": "S2", "cevap": "y"}]},
            "soru_basi",
        ),
    ],
)
def test_malformed_or_incomplete_answers_are_refused(dosya, parca) -> None:
    with pytest.raises(od.OperatorKarariReddedildi, match=parca.replace("[", r"\[").replace("]", r"\]")):
        _uygula(dosya)


def test_soru_basi_that_matches_is_accepted() -> None:
    dosya = _cevaplar()
    dosya["kararlar"][0]["soru_basi"] = "**Ayar beyanı**"
    yeni, _ = _uygula(dosya)
    assert yeni.policy_report.acik_soru_kimlikleri == ()


def test_other_blocking_reason_is_not_bypassed() -> None:
    """Açık soru dışındaki engel (ör. bariyer) operatör kararıyla AŞILMAZ."""
    import dataclasses

    sonuc, _ = _motor()
    sonuc = dataclasses.replace(sonuc, sebep=f"{od.ACIK_SORU_SEBEBI}; bariyer-asildi")
    with pytest.raises(od.OperatorKarariReddedildi, match="DIŞINDA"):
        _uygula(_cevaplar(), sonuc=sonuc)


def test_non_blocked_result_is_refused() -> None:
    sonuc = engine.decide(_girdi(), PolicyConfig())
    assert sonuc.sonuc != "blocked"
    with pytest.raises(od.OperatorKarariReddedildi, match="yalnız açık sorularla"):
        _uygula(_cevaplar(), sonuc=sonuc)


# ═══ İşlemler ═══════════════════════════════════════════════════════════════


def _butunluk(yeni) -> None:
    icerik = identity.cozulmus(yeni.final_candidate)
    gunluk = [identity.cozulmus(s) for s in yeni.final_decision_log]
    assert identity.check_unit_integrity(icerik, gunluk) == []
    assert yeni.content_sha == engine.canonical_content_sha(icerik)
    assert yeni.decision_log_sha == identity.canonical_sha(gunluk)


def test_ekle_adds_a_labelled_unsourced_unit() -> None:
    yeni, kayit = _uygula(
        _cevaplar(S1=[{"islem": "ekle", "alan": "cta_kaliplari", "deger": CTA}])
    )
    assert yeni.sonuc == "activation_eligible"
    _butunluk(yeni)
    icerik = identity.cozulmus(yeni.final_candidate)
    assert icerik["cta_kaliplari"][-1] == CTA
    islem = kayit["kararlar"][0]["islemler"][0]
    satir = next(
        s for s in yeni.final_decision_log if s.get("unit_id") == islem["unit_id"]
    )
    assert satir["karar"] == "ekle" and satir["aktor"] == "insan"
    assert satir["kanit"] == od.KAYNAKSIZ_KANIT
    assert satir["gerekce"].startswith("operatör kararı (S1)")
    assert islem["yol"] == "cta_kaliplari[1]"
    assert islem["hukuki"] is False


@pytest.mark.parametrize(
    "metin,hukuki",
    [
        ("Birim gram fiyatı yönetmelik gereği görünür yazılır.", True),
        ("Kampanya 500 TL üzeri alışverişte geçerlidir.", True),
        ("22 ayar bilezik vitrinde.", False),
    ],
)
def test_ekle_marks_legal_items_with_the_k129_reading(metin, hukuki) -> None:
    _, kayit = _uygula(
        _cevaplar(S1=[{"islem": "ekle", "alan": "yasaklar_ve_hassasiyetler", "deger": metin}])
    )
    islem = kayit["kararlar"][0]["islemler"][0]
    # Yasak alanı her zaman risktir (K-129 alan kolu); içerik alanında da ölç.
    assert islem["hukuki"] is True
    _, kayit = _uygula(
        _cevaplar(S1=[{"islem": "ekle", "alan": "kanca_kaliplari", "deger": metin}])
    )
    assert kayit["kararlar"][0]["islemler"][0]["hukuki"] is hukuki


def test_degistir_turns_koru_into_guncelle_by_the_operator() -> None:
    hedef = KIMLIKLER["kanca_kaliplari[0]"]
    yeni, _ = _uygula(
        _cevaplar(S2=[{"islem": "degistir", "unit_id": hedef, "deger": "Yeni kanca"}])
    )
    _butunluk(yeni)
    satir = next(s for s in yeni.final_decision_log if s.get("unit_id") == hedef)
    assert satir["karar"] == "guncelle" and satir["aktor"] == "insan"
    assert identity.cozulmus(yeni.final_candidate)["kanca_kaliplari"][0] == "Yeni kanca"


def test_cikar_shifts_following_paths_and_keeps_integrity() -> None:
    ilk, ikinci = KIMLIKLER["kanca_kaliplari[0]"], KIMLIKLER["kanca_kaliplari[1]"]
    yeni, _ = _uygula(_cevaplar(S1=[{"islem": "cikar", "unit_id": ilk}]))
    _butunluk(yeni)
    icerik = identity.cozulmus(yeni.final_candidate)
    assert icerik["kanca_kaliplari"] == [AKTIF_ICERIK["kanca_kaliplari"][1]]
    gunluk = [identity.cozulmus(s) for s in yeni.final_decision_log]
    assert _yol(icerik, ikinci, gunluk) == "kanca_kaliplari[0]"
    cikan = next(s for s in gunluk if s.get("unit_id") == ilk)
    assert cikan["karar"] == "cikar" and cikan["aktor"] == "insan" and cikan["kanit"]


def test_cikar_of_an_item_added_this_round_becomes_rejected_candidate() -> None:
    """Aynı dosyada eklenip çıkarılan birim `cikar` değil, reddedilen adaydır."""
    yeni, kayit = _uygula(
        _cevaplar(S1=[
            {"islem": "ekle", "alan": "kanca_kaliplari", "deger": "Geçici kanca"},
            {"islem": "cikar", "unit_id": "ku-f00000000001"},
        ])
    )
    _butunluk(yeni)
    assert "Geçici kanca" not in identity.cozulmus(yeni.final_candidate)["kanca_kaliplari"]
    notlar = [s for s in yeni.final_decision_log if s.get("tur") == "not"
              and s.get("gerekce", "").startswith("operatör kararı")]
    assert len(notlar) == 1 and notlar[0]["sinif"] == "reddedilen-aday"
    assert kayit["kararlar"][0]["islemler"][0]["yol"] is None


def test_ozel_gun_is_added_whole_and_only_from_the_calendar() -> None:
    girdi = {y: f"{y} metni" for y in SPECIAL_DAY_SLOTS}
    yeni, kayit = _uygula(
        _cevaplar(S2=[{"islem": "ekle", "alan": "ozel_gun", "anahtar": YENI_ANAHTAR,
                       "deger": girdi}])
    )
    _butunluk(yeni)
    assert identity.cozulmus(yeni.final_candidate)["ozel_gun"][YENI_ANAHTAR] == girdi
    assert len(kayit["kararlar"][1]["islemler"]) == len(SPECIAL_DAY_SLOTS)
    with pytest.raises(od.OperatorKarariReddedildi, match="sistem takviminde yok"):
        _uygula(
            _cevaplar(S2=[{"islem": "ekle", "alan": "ozel_gun", "anahtar": "uydurma-gun",
                           "deger": girdi}])
        )


def test_ozel_gun_is_removed_whole() -> None:
    yeni, _ = _uygula(
        _cevaplar(S2=[{"islem": "cikar", "alan": "ozel_gun", "anahtar": TAKVIM_ANAHTARI}])
    )
    _butunluk(yeni)
    assert TAKVIM_ANAHTARI not in identity.cozulmus(yeni.final_candidate).get("ozel_gun", {})


@pytest.mark.parametrize(
    "islem,parca",
    [
        ({"islem": "ekle", "alan": "kanca_kaliplari", "deger": "Kanca [kopya-şüphesi]"},
         "tüketilmemiş bayrak"),
        ({"islem": "ekle", "alan": "cta_kaliplari", "deger": "düz metin"}, "CTA öğesi"),
        ({"islem": "ekle", "alan": "kapsam", "deger": "x"}, "eklenebilen alanlar"),
        ({"islem": "degistir", "unit_id": "ku-ffffffffffff", "deger": "x"}, "pakette yok"),
        ({"islem": "cikar", "unit_id": KIMLIKLER["kapsam"]}, "düz metin alanı"),
        ({"islem": "sil", "unit_id": KIMLIKLER["kapsam"]}, "işlem"),
        ({"islem": "ekle", "alan": "kanca_kaliplari", "deger": "x", "fazla": 1}, "alanlar"),
    ],
)
def test_invalid_operations_are_refused(islem, parca) -> None:
    with pytest.raises(od.OperatorKarariReddedildi, match=parca):
        _uygula(_cevaplar(S1=[islem]))


def test_emptying_a_list_is_refused_by_the_shape_gate() -> None:
    tek = [{"islem": "cikar", "unit_id": KIMLIKLER["yasaklar_ve_hassasiyetler[0]"]}]
    with pytest.raises(od.OperatorKarariReddedildi, match="boş"):
        _uygula(_cevaplar(S1=tek))


# ═══ Kalıcılık — tek sefer, ilk sonuç saklanır, onay yüzeyi görür ══════════


@pytest.fixture
async def pkg_db(db):
    await _init_connection(db)
    return db


async def _blocked_kosu(db) -> tuple[str, object]:
    root_id = await db.fetchval(
        "SELECT id FROM social.sectors WHERE parent_sector_id IS NULL LIMIT 1"
    )
    sector_id = await db.fetchval(
        "INSERT INTO social.sectors (slug, display_name, parent_sector_id) "
        "VALUES ($1, 'Alt', $2) RETURNING id",
        f"alt-{uuid.uuid4().hex[:8]}",
        root_id,
    )
    run_id = runs.new_run_id()
    await runs.open_run(db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")
    sonuc, _ = _motor()
    await runs.record_result(db, run_id=run_id, result=sonuc)
    return run_id, sonuc


async def test_resolution_is_written_once_and_keeps_the_first_result(pkg_db) -> None:
    run_id, sonuc = await _blocked_kosu(pkg_db)
    yeni, kayit = _uygula(
        _cevaplar(S1=[{"islem": "ekle", "alan": "cta_kaliplari", "deger": CTA}]),
        sonuc=sonuc,
    )
    await runs.record_operator_resolution(
        pkg_db, run_id=run_id, result=yeni, kararlar=kayit, actor=ACTOR
    )
    satir = await pkg_db.fetchrow(
        "SELECT sonuc, sebep, content_sha FROM social.sector_package_runs WHERE run_id = $1",
        run_id,
    )
    assert (satir["sonuc"], satir["sebep"]) == ("activation_eligible", None)
    assert satir["content_sha"] == yeni.content_sha
    karar = await pkg_db.fetchrow(
        "SELECT motor_ilk_sonucu, actor FROM social.sector_run_operator_decisions "
        "WHERE run_id = $1",
        run_id,
    )
    assert karar["actor"] == ACTOR
    assert karar["motor_ilk_sonucu"]["sonuc"] == "blocked"
    assert karar["motor_ilk_sonucu"]["sebep"] == od.ACIK_SORU_SEBEBI
    assert karar["motor_ilk_sonucu"]["policy_report"]["acik_soru_kimlikleri"] == [
        SORU_1, SORU_2,
    ]

    dogrulanmis = await runs.load_verified_run(pkg_db, run_id=run_id, for_update=False)
    assert dogrulanmis.operator_kararlari["kararlar"][0]["soru"] == "S1"

    with pytest.raises(ValueError, match="operatör kararı yazılamaz"):
        await runs.record_operator_resolution(
            pkg_db, run_id=run_id, result=yeni, kararlar=kayit, actor=ACTOR
        )


async def test_resolution_refuses_a_blocked_result_and_a_missing_run(pkg_db) -> None:
    run_id, sonuc = await _blocked_kosu(pkg_db)
    with pytest.raises(ValueError, match="`blocked` olmayan"):
        await runs.record_operator_resolution(
            pkg_db, run_id=run_id, result=sonuc, kararlar={}, actor=ACTOR
        )
    yeni, kayit = _uygula(_cevaplar(), sonuc=sonuc)
    with pytest.raises(ValueError, match="yazılamaz"):
        await runs.record_operator_resolution(
            pkg_db, run_id=runs.new_run_id(), result=yeni, kararlar=kayit, actor=ACTOR
        )


async def _onaya_hazir(pkg_db):
    from app.services.sector_pipeline import writeback

    run_id, sonuc = await _blocked_kosu(pkg_db)
    yeni, kayit = _uygula(
        _cevaplar(S1=[{"islem": "ekle", "alan": "yasaklar_ve_hassasiyetler",
                       "deger": "Gram fiyatı yönetmelik gereği yazılır."}]),
        sonuc=sonuc,
    )
    await runs.record_operator_resolution(
        pkg_db, run_id=run_id, result=yeni, kararlar=kayit, actor=ACTOR
    )
    await runs.attest_katman1(pkg_db, run_id=run_id, kosum_kimligi="k1", sonuc="PASS", actor=ACTOR)
    await writeback.write_draft_from_run(pkg_db, run_id=run_id, actor=ACTOR)
    await runs.attest_katman2(pkg_db, run_id=run_id, kosum_kimligi="k2", ozet="örnek", actor=ACTOR)
    return run_id


async def test_approval_summary_lists_operator_operations_and_legal_mark(pkg_db) -> None:
    run_id = await _onaya_hazir(pkg_db)
    goruntu = await approval.build_and_freeze_from_run(pkg_db, run_id=run_id, actor=ACTOR)
    assert goruntu["onaylanabilir"] is True
    assert goruntu["operator_kararlari"][0]["islemler"][0]["hukuki"] is True
    metin = approval.render_summary(goruntu)
    assert "Operatör kararları: 2 soru kapatıldı" in metin
    assert "HUKUKİ — operatör kararı" in metin


async def test_operator_record_drift_after_freeze_refuses_decision(pkg_db) -> None:
    """MUTASYON VAKASI (`operator_kararlari` çekirdek alanı): donduktan sonra
    kayıt değişirse görüntü ayrışır ve karar YAZILMAZ."""
    run_id = await _onaya_hazir(pkg_db)
    goruntu = await approval.build_and_freeze_from_run(pkg_db, run_id=run_id, actor=ACTOR)
    sha = identity.canonical_sha(goruntu)
    await pkg_db.execute(
        "UPDATE social.sector_run_operator_decisions "
        "SET kararlar = jsonb_set(kararlar, '{kararlar,0,cevap}', '\"değişti\"') "
        "WHERE run_id = $1",
        run_id,
    )
    with pytest.raises(approval.ApprovalRefused):
        await approval.record_decision(
            pkg_db, run_id=run_id, karar="onay", actor=ACTOR, seconds=1, snapshot_sha=sha
        )
