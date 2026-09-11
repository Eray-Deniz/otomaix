"""İşletime hazırlık kontrol listesinin DEĞERLENDİRİCİSİ (plan Task 17, K-69/K-70).

Ölçülen dört iddia:

1. **Çift kayıt YOK** — `readiness.CHECKLIST` kimlik kümesini `readiness_items`'tan
   kurar; ikinci bir madde listesi yazılmaz (arayüz eki H5).
2. **K-70 — ön-kontrol ONAYLAMAZ** — `evaluate` yazmaz, `actor` almaz, raporunda
   onay alanı yoktur.
3. **K-69 — kapı yalnız `kapi` sınıfını sayar** — `sinyal` maddesi (bugün md-15)
   tamamlanmayı bloklamaz; `kapi` maddesi bloklar (pozitif kontrol).
4. **İlke 9 — ölçülmemiş madde "ölçüldü" gibi sunulmaz** — otomatik ölçülebilen
   her maddenin adlandırılmış bir probu vardır, kalanlar `elle` + `beklemede`.
"""

from __future__ import annotations

import inspect
import uuid

import pytest

from app.services.sector_pipeline import readiness, readiness_items, runs

from .test_pipeline_writeback import (  # noqa: F401 — fixture yeniden dışa vurulur
    _kosu,
    _sub_sector,
    _yazilmis_ve_onayli,
    pkg_db,
)

# `pytest.ini` `asyncio_mode = auto` taşır — dosya düzeyinde `pytestmark` YAZILMAZ.


async def _artefakt(
    db,
    run_id: str,
    *,
    kind: str,
    model: str,
    brief_ref: str | None = None,
) -> None:
    await runs.record_artifact(
        db,
        run_id=run_id,
        sector_slug="kuyumculuk",
        kind=kind,
        source=runs.build_stamp(
            model=model, surum="2026-09", tarih="2026-09-11", girdi_ozeti="brief-sha"
        ),
        brief_ref=brief_ref,
        content_md=f"# {model} çıktısı",
    )


async def _hazir_kosu(db) -> str:
    """Otomatik ön-kontrolün TAMAMINI geçen koşu — pozitif kontrolün zemini.

    Zincir TAM kurulur (koşu → taslak → dondurulmuş görüntü → onay), çünkü
    otomatik maddelerin ikisi taslak bağını ve yönetici kararını okur.
    """
    sector_id = await _sub_sector(db)
    run_id, _ = await _yazilmis_ve_onayli(db, sector_id, hazirlik=False)
    for model in ("arac-1", "arac-2", "arac-3"):
        await _artefakt(db, run_id, kind="research", model=model, brief_ref="brief-v1")
    for model in ("denetci-1", "denetci-2"):
        await _artefakt(db, run_id, kind="review", model=model)
    await _artefakt(db, run_id, kind="synthesis", model="sentez")
    return run_id


def _satir(rapor: readiness.ReadinessReport, madde_id: str) -> readiness.MaddeSonucu:
    for satir in rapor.satirlar:
        if satir.madde_id == madde_id:
            return satir
    raise AssertionError(f"raporda yok: {madde_id}")


# ═══ 1. Çift kayıt yasağı ═══════════════════════════════════════════════════


def test_checklist_is_built_from_readiness_items():
    """`CHECKLIST` kanonik kümenin KENDİSİDİR — ikinci kayıt değil."""
    assert readiness.CHECKLIST is readiness_items.MADDELER
    assert [madde.madde_id for madde in readiness.CHECKLIST] == [
        madde.madde_id for madde in readiness_items.MADDELER
    ]


def test_checklist_has_twenty_items():
    """Spec §13.4'ün YİRMİ maddesi."""
    assert len(readiness.CHECKLIST) == 20


def test_every_auto_item_has_a_probe_and_manual_items_have_none():
    """Prob tablosu madde kümesine BAĞLIDIR — iki yönlü, fail-closed.

    Probu olmayan bir `otomatik` madde sessizce ölçülmemiş kalırdı; probu olan
    bir `elle` madde ise beyanı ölçüm gibi gösterirdi.
    """
    otomatikler = {
        madde.madde_id for madde in readiness.CHECKLIST if madde.otomatik
    }
    assert set(readiness.PROBLAR) == otomatikler


# ═══ 2. K-70 — ön-kontrol onaylamaz ═════════════════════════════════════════


def test_evaluate_takes_no_actor_and_report_carries_no_approval():
    """Yapısal kapı: onay bu yüzeyde DOĞAMAZ."""
    imza = inspect.signature(readiness.evaluate)
    assert "actor" not in imza.parameters

    alanlar = set(readiness.ReadinessReport.__dataclass_fields__)
    assert not {
        ad for ad in alanlar if "onay" in ad.lower() or "approved" in ad.lower()
    }


async def test_auto_precheck_does_not_self_approve(pkg_db):  # noqa: F811
    """K-70: ön-kontrol KOŞAR ama tasdik yazmaz — satır boş KALIR."""
    run_id = await _hazir_kosu(pkg_db)

    rapor = await readiness.evaluate(pkg_db, run_id=run_id)

    assert rapor.run_id == run_id
    assert (
        await pkg_db.fetchval(
            "SELECT readiness_attestation FROM social.sector_package_runs "
            "WHERE run_id = $1",
            run_id,
        )
        is None
    )


# ═══ 3. K-69 — kapı yalnız `kapi` sınıfını sayar ════════════════════════════


def test_signal_items_do_not_block_completion():
    """DÜŞMÜŞ bir `sinyal` maddesi kapıyı kapatmaz; `kapi` maddesi kapatır.

    **Bu test neden koşu üstünden DEĞİL (mutasyonla ölçüldü, 2026-09-11).**
    İlk yazımı `evaluate` çıktısına bakıyordu ve SAHTE YEŞİLDİ: bugünkü tek
    sinyal maddesi `elle` olduğu için durumu hep `beklemede`, yani hiçbir
    koşulda `gecmedi` olamıyor. Sınıf filtresi koddan tamamen SİLİNDİĞİNDE bile
    test geçiyordu. Özellik, onu SINAYABİLEN yerde — raporun kendi kapısında —
    ölçülür: sınıfı düşmüş iki satır kurulur, biri `kapi` biri `sinyal`.
    """
    rapor = readiness.ReadinessReport(
        run_id="kosu-sentetik",
        satirlar=(
            readiness.MaddeSonucu(
                madde_id="md-x-kapi",
                sinif="kapi",
                baslik="ölçümü düşmüş kapı maddesi",
                olcum="otomatik",
                durum="gecmedi",
                detay="sentetik",
            ),
            readiness.MaddeSonucu(
                madde_id="md-x-sinyal",
                sinif="sinyal",
                baslik="ölçümü düşmüş sinyal maddesi",
                olcum="otomatik",
                durum="gecmedi",
                detay="sentetik",
            ),
        ),
    )

    assert rapor.bloklayan_kapi_maddeleri == ("md-x-kapi",)


async def test_signal_items_are_shown_to_the_operator(pkg_db):  # noqa: F811
    """Sinyal maddesi GİZLENMEZ: operatöre beyan bekleyen olarak görünür."""
    run_id = await _hazir_kosu(pkg_db)

    rapor = await readiness.evaluate(pkg_db, run_id=run_id)

    sinyaller = readiness_items.SINYAL_MADDELERI
    assert sinyaller, "sinyal sınıfı boşsa bu kapı hiçbir şey ölçmez"
    assert set(sinyaller) <= set(rapor.elle_bekleyen_maddeler)


async def test_gate_items_still_block_completion(pkg_db):  # noqa: F811
    """POZİTİF KONTROL: ölçümü DÜŞEN `kapi` maddesi bloklar."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _kosu(pkg_db, sector_id, sonuc="no_change", hazirlik=False)

    rapor = await readiness.evaluate(pkg_db, run_id=run_id)

    assert "md-11" in rapor.bloklayan_kapi_maddeleri
    assert _satir(rapor, "md-11").durum == "gecmedi"


async def test_auto_gate_items_pass_on_a_fully_prepared_run(pkg_db):  # noqa: F811
    """POZİTİF KONTROL: kapı her şeyi reddetmiyor — hazır koşuda blokaj YOK."""
    run_id = await _hazir_kosu(pkg_db)

    rapor = await readiness.evaluate(pkg_db, run_id=run_id)

    assert rapor.bloklayan_kapi_maddeleri == ()
    otomatik_kapilar = [
        satir
        for satir in rapor.satirlar
        if satir.olcum == "otomatik" and satir.sinif == "kapi"
    ]
    assert otomatik_kapilar, "otomatik kapı maddesi yoksa pozitif kontrol boş koşar"
    assert all(satir.durum == "gecti" for satir in otomatik_kapilar)


# ═══ 4. İlke 9 — ölçülmemiş madde "ölçüldü" gibi sunulmaz ═══════════════════


async def test_manual_items_labelled_as_manual(pkg_db):  # noqa: F811
    """Otomatik ölçülemeyen madde `elle` + `beklemede`; ASLA `gecti` değil."""
    run_id = await _hazir_kosu(pkg_db)

    rapor = await readiness.evaluate(pkg_db, run_id=run_id)

    elle_olmasi_gerekenler = {
        madde.madde_id for madde in readiness.CHECKLIST if not madde.otomatik
    }
    assert elle_olmasi_gerekenler, "elle madde yoksa bu kapı boş koşar"
    for madde_id in elle_olmasi_gerekenler:
        satir = _satir(rapor, madde_id)
        assert satir.olcum == "elle"
        assert satir.durum == "beklemede"


async def test_every_automatic_row_names_the_artifact_it_read(pkg_db):  # noqa: F811
    """Otomatik satır, ölçümünü ÜRETEN kanıtı `detay`da ADLANDIRIR (İlke 9)."""
    run_id = await _hazir_kosu(pkg_db)

    rapor = await readiness.evaluate(pkg_db, run_id=run_id)

    otomatikler = [satir for satir in rapor.satirlar if satir.olcum == "otomatik"]
    assert otomatikler
    assert all(satir.detay.strip() for satir in otomatikler)


async def test_report_covers_every_checklist_item(pkg_db):  # noqa: F811
    """Rapor kümeyi TAM taşır — sessizce düşen madde olamaz."""
    run_id = await _hazir_kosu(pkg_db)

    rapor = await readiness.evaluate(pkg_db, run_id=run_id)

    assert [satir.madde_id for satir in rapor.satirlar] == [
        madde.madde_id for madde in readiness.CHECKLIST
    ]


async def test_evaluate_refuses_an_unknown_run(pkg_db):  # noqa: F811
    """Tanınmayan koşu SESSİZ boş rapor üretmez (fail-closed)."""
    with pytest.raises(runs.RunNotVerified):
        await readiness.evaluate(pkg_db, run_id=f"kosu-{uuid.uuid4().hex[:8]}")


def test_blocking_finding_classes_are_a_subset_of_the_engine_contract():
    """16. maddenin saydığı bulgu sınıfları MOTOR sözleşmesinden gelir.

    Elle yazılmış bir sınıf adı sessizce hiçbir bulguyla eşleşmez ve madde
    daima "geçti" derdi — referans bütünlüğü kapısı (İlke 1).
    """
    from app.services.sector_pipeline.engine_contract import BULGU_SINIFLARI

    assert readiness.BLOKLAYAN_BULGU_SINIFLARI <= set(BULGU_SINIFLARI)
    assert readiness.BLOKLAYAN_BULGU_SINIFLARI, "boş küme hiçbir bulguyu saymaz"


# ═══ 5. Hakem turu 1 bulguları — üretici kimliği ve şekil kapısı ════════════


async def test_md03_refuses_three_stamps_from_one_producer(pkg_db):  # noqa: F811
    """Üç DAMGA üç ARAÇ değildir (hakem turu 1, yüksek).

    Damga `model; surum; tarih; girdi_ozeti` bileşiğidir. İlk yazım farklı
    damgaları farklı kaynak sayıyordu: TEK aracın üç ayrı tarihle ürettiği üç
    çıktı "üç araçta koşuldu" maddesini geçiriyordu.
    """
    sector_id = await _sub_sector(pkg_db)
    run_id, _ = await _yazilmis_ve_onayli(pkg_db, sector_id, hazirlik=False)
    for tarih in ("2026-09-09", "2026-09-10", "2026-09-11"):
        await runs.record_artifact(
            pkg_db,
            run_id=run_id,
            sector_slug="kuyumculuk",
            kind="research",
            source=runs.build_stamp(
                model="arac-1", surum="2026-09", tarih=tarih, girdi_ozeti="brief-sha"
            ),
            brief_ref="brief-v1",
            content_md="# tek araç",
        )

    rapor = await readiness.evaluate(pkg_db, run_id=run_id)

    assert _satir(rapor, "md-03").durum == "gecmedi"


async def test_md05_requires_both_blind_auditor_roles(pkg_db):  # noqa: F811
    """İki rapor, İKİ HAKEM demek değildir — rol uzayı sözleşmede kapalı."""
    sector_id = await _sub_sector(pkg_db)
    run_id, _ = await _yazilmis_ve_onayli(pkg_db, sector_id, hazirlik=False)
    for tarih in ("2026-09-10", "2026-09-11"):
        await runs.record_artifact(
            pkg_db,
            run_id=run_id,
            sector_slug="kuyumculuk",
            kind="review",
            source=runs.build_stamp(
                model="denetci-1", surum="2026-09", tarih=tarih, girdi_ozeti="paket-sha"
            ),
            content_md="# tek hakem",
        )

    rapor = await readiness.evaluate(pkg_db, run_id=run_id)

    assert _satir(rapor, "md-05").durum == "gecmedi"


async def test_malformed_policy_report_blocks_instead_of_reading_clean(pkg_db):  # noqa: F811
    """Eksik alan BOŞ-TEMİZ kanıta genişlemez (hakem turu 1, yüksek).

    İlk yazım md-09 için `is not None`, md-16 için `.get(..., ())` kullanıyordu:
    `{}` biçiminde bir rapor "motor kontrolleri tamam + bulgu yok" diye okunurdu.
    """
    run_id = await _hazir_kosu(pkg_db)
    await pkg_db.execute(
        "UPDATE social.sector_package_runs SET policy_report = $2 WHERE run_id = $1",
        run_id,
        {},
    )

    rapor = await readiness.evaluate(pkg_db, run_id=run_id)

    assert _satir(rapor, "md-09").durum == "gecmedi"
    assert _satir(rapor, "md-16").durum == "gecmedi"


def test_blocking_finding_classes_come_from_the_engine_effect_table():
    """Bloklayan sınıflar MOTORUN etki tablosundan TÜRETİLİR — elle yazılmaz.

    `mevzuat_dogrulanamadi` bayrağa bağlıdır (K-128, varsayılan KAPALI); elle
    yazılmış kümede bloklayıcı sayılıyordu ve hazırlık kapısı motorun İZİN
    VERDİĞİ koşuyu reddediyordu (hakem turu 1, orta — kendi gerilemem).
    """
    from app.services.sector_pipeline import engine

    assert "mevzuat_dogrulanamadi" not in readiness.BLOKLAYAN_BULGU_SINIFLARI
    assert "kapsam_ihlali" in readiness.BLOKLAYAN_BULGU_SINIFLARI
    bayraga_bagli = {
        etki.sinif
        for etki in engine.BULGU_ETKILERI
        if etki.etki == engine.ETKI_BAYRAGA_BAGLI
    }
    assert not (readiness.BLOKLAYAN_BULGU_SINIFLARI & bayraga_bagli)


async def test_malformed_artifact_stamp_fails_only_its_own_probe(pkg_db):  # noqa: F811
    """Bozuk damga RAPORU ÖLDÜRMEZ, kendi maddesini düşürür (fail-closed).

    `record_artifact` damgayı yazarken doğrular; bu satır oraya BAKMAYAN bir
    yoldan (elle bakım, ileriki bir yazıcı) gelmiş olabilir.
    """
    run_id = await _hazir_kosu(pkg_db)
    await pkg_db.execute(
        "INSERT INTO social.sector_research_artifacts "
        "(run_id, sector_slug, kind, source, content_md) VALUES ($1, $2, $3, $4, $5)",
        run_id,
        "kuyumculuk",
        "research",
        "damgasiz-kaynak",
        "# bozuk",
    )

    rapor = await readiness.evaluate(pkg_db, run_id=run_id)

    assert _satir(rapor, "md-03").durum == "gecmedi"
    assert "damga" in _satir(rapor, "md-03").detay.lower()
    assert _satir(rapor, "md-11").durum == "gecti", "komşu prob etkilenmemeli"
