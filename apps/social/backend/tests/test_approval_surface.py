"""Onay yüzeyi (Plan 2 Task 14).

Dört sözleşmeyi birden pinler:

1. **F18** — görüntü kilitli koşudan BASILIR; çağıranın kurduğu görüntüyü kabul
   eden yol YOKTUR ve karar görüntünün HASH'ine bağlanır.
2. **K-98** — görüntü değişmezdir; ikinci yazım veritabanı tetikleyicisiyle
   reddedilir, modül fikirsiz tekrarda olanı döner.
3. **K-42/K-41/K-71** — riskli sınıflar nötr sayıların önünde; çıkarılanlar
   sayısı eşiksizdir ve tam liste bir tık derinde; açık soru varsa onaylanabilir
   sonuç SUNULMAZ.
4. **R3** — onay/ret olayı paket kimliğini KİLİTLİ KOŞUDAN taşır; çağıran paket
   kimliği VERMEZ.

Beklentiler ölçüm anında elle yazılır: hash'ler `identity.canonical_sha` ile
(test edilen kodla DEĞİL), sıralama kavramdan (riskli sınıf adları) türetilir.
"""

from __future__ import annotations

import ast
import inspect
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

import asyncpg
import pytest

from app.core.database import _init_connection
from app.services.sector_pipeline import approval, identity, runs
from app.services.sector_pipeline.engine_contract import (
    BulguIzi,
    EngineResult,
    KararsizMadde,
    PolicyReport,
)

ACTOR = "admin@otomaix"
MOTOR_SURUM = "engine-1.0.0"
CONFIG_SHA = "c" * 64

APPROVAL_KAYNAK = Path(approval.__file__).read_text(encoding="utf-8")


# ═══ Ortak yardımcılar ══════════════════════════════════════════════════════


@pytest.fixture
async def pkg_db(db):
    """Üretimin KENDİ bağlantı yapılandırması (jsonb codec)."""
    await _init_connection(db)
    return db


async def _sub_sector(db) -> uuid.UUID:
    root_id = await db.fetchval(
        "SELECT id FROM social.sectors WHERE parent_sector_id IS NULL LIMIT 1"
    )
    assert root_id is not None, "kök sektör seed'i eksik"
    return await db.fetchval(
        "INSERT INTO social.sectors (slug, display_name, parent_sector_id) "
        "VALUES ($1, $2, $3) RETURNING id",
        f"alt-{uuid.uuid4().hex[:8]}",
        "Alt Sektör",
        root_id,
    )


def _aday() -> dict:
    return {
        "kapsam": "Kuyumculuk: altın ve gümüş takı perakendesi.",
        "kanca_kaliplari": [KANCA_METNI],
    }


KANCA_METNI = "Ayar farkını gözle ayırt edebilir misiniz?"
"""Kalıp METNİ — yönetici özetinde GÖRÜNMEMESİ gereken değer (spec §9.6)."""


def _karar_satiri(**overrides) -> dict:
    row = {
        "tur": "karar",
        "alan": "kanca_kaliplari",
        "oge_yolu": "kanca_kaliplari[0]",
        "unit_id": "ku-0123456789ab",
        "oge_sha": "a" * 64,
        "karar": "koru",
        "gerekce": "Kalıp sektörde hâlâ karşılık buluyor.",
        "kanit": "",
        "aktor": "sentez",
    }
    row.update(overrides)
    return row


def _policy_report(**overrides) -> PolicyReport:
    alanlar = {
        "kararsizlar": (),
        "bulgular": (),
        "uygulanmayan_kararlar": (),
        "acik_soru_kimlikleri": (),
    }
    alanlar.update(overrides)
    return PolicyReport(**alanlar)


def _engine_result(
    *,
    final_decision_log: list[dict] | None = None,
    policy_report: PolicyReport | None = None,
    sonuc: str = "activation_eligible",
    sebep: str | None = None,
) -> EngineResult:
    aday = _aday()
    gunluk = [_karar_satiri()] if final_decision_log is None else final_decision_log
    if sonuc == "activation_eligible":
        content_sha = identity.canonical_sha(aday)
        log_sha = identity.canonical_sha(gunluk)
    else:
        aday, gunluk, content_sha, log_sha = None, None, None, None
    return EngineResult(
        sonuc=sonuc,
        sebep=sebep,
        final_candidate=aday,
        final_decision_log=tuple(gunluk) if gunluk else None,
        engine_diff={"diff": {"cikar": 0, "ekle": 0, "koru": 1}},
        policy_report=policy_report or _policy_report(),
        barrier_report={"payda": 1, "oranlar": {"degisim": 0.0}, "asilan": []},
        content_sha=content_sha,
        decision_log_sha=log_sha,
        engine_version=MOTOR_SURUM,
        engine_config_sha=CONFIG_SHA,
    )


async def _taslak(db, sector_id: uuid.UUID, *, version: int = 1) -> uuid.UUID:
    return await db.fetchval(
        "INSERT INTO social.sector_packages "
        "(sector_id, version, status, schema_version, content) "
        "VALUES ($1, $2, 'draft', 1, $3) RETURNING id",
        sector_id,
        version,
        _aday(),
    )


async def _onaya_hazir_kosu(
    db,
    sector_id: uuid.UUID,
    *,
    final_decision_log: list[dict] | None = None,
    policy_report: PolicyReport | None = None,
    sonuc: str = "activation_eligible",
    sebep: str | None = None,
    taslak: bool = True,
    katman2: bool = True,
    created_at: datetime | None = None,
) -> str:
    """Yedi kapıdan geçmiş, taslağı yazılmış koşu — onay yüzeyinin girdisi."""
    run_id = runs.new_run_id()
    await runs.open_run(db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")
    await runs.record_result(
        db,
        run_id=run_id,
        result=_engine_result(
            final_decision_log=final_decision_log,
            policy_report=policy_report,
            sonuc=sonuc,
            sebep=sebep,
        ),
    )
    await runs.attest_katman1(
        db, run_id=run_id, kosum_kimligi="k1-1", sonuc="PASS", actor=ACTOR
    )
    if katman2:
        await runs.attest_katman2(
            db, run_id=run_id, kosum_kimligi="k2-1", ozet="sinyal özeti", actor=ACTOR
        )
    if created_at is not None:
        # `now()` TRANSACTION damgasıdır: aynı testte açılan koşular onu
        # paylaşır ve sıra ölçülemez hâle gelir. Üretimde her koşu kendi
        # transaction'ındadır; test o ayrımı damgayı AÇIKÇA vererek kurar.
        await db.execute(
            "UPDATE social.sector_package_runs SET created_at = $2 "
            "WHERE run_id = $1",
            run_id,
            created_at,
        )
    if taslak:
        package_id = await _taslak(db, sector_id)
        await db.execute(
            "UPDATE social.sector_package_runs SET package_id = $2 WHERE run_id = $1",
            run_id,
            package_id,
        )
    return run_id


# ═══ 1. Görüntü kilitli koşudan BASILIR (F18) ═══════════════════════════════


async def test_snapshot_fields_equal_persisted_run(pkg_db) -> None:
    """POZİTİF KONTROL: görüntünün her alanı kalıcı satırdan gelir."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _onaya_hazir_kosu(pkg_db, sector_id)

    goruntu = await approval.build_and_freeze_from_run(
        pkg_db, run_id=run_id, actor=ACTOR
    )

    satir = await pkg_db.fetchrow(
        "SELECT * FROM social.sector_package_runs WHERE run_id = $1", run_id
    )
    assert goruntu["sema"] == approval.SNAPSHOT_SEMA
    assert goruntu["run_id"] == run_id
    assert goruntu["sonuc"] == satir["sonuc"]
    assert goruntu["icerik_hashleri"] == {
        "content_sha": satir["content_sha"],
        "decision_log_sha": satir["decision_log_sha"],
    }
    assert goruntu["acik_sorular"] == []
    assert goruntu["kapi_sonuclari"]["katman1"] == "PASS"
    # Katman-2'nin SONUCU KAPI DEĞİLDİR (spec §10.2): görüntü yalnız koşulup
    # sunulduğunu taşır. "PASS/FAIL" yazmak, okunmayan bir sonucu kapıymış gibi
    # gösterirdi.
    assert goruntu["kapi_sonuclari"]["katman2"] == {"sunuldu": True}
    assert goruntu["motor_kosu_raporu"]["engine_version"] == MOTOR_SURUM
    assert goruntu["motor_kosu_raporu"]["engine_config_sha"] == CONFIG_SHA
    # Görüntü SATIRA yazıldı ve hash'i kaydedildi.
    assert satir["approval_snapshot"] == goruntu
    assert satir["snapshot_sha"] == identity.canonical_sha(goruntu)


async def test_snapshot_minted_from_locked_run_not_caller() -> None:
    """F18 YAPISAL KAPISI: imzada görüntü/sözlük parametresi YOKTUR.

    KENDİ KIRMIZISI YOKTUR (yapısal invariant testi): fonksiyon hiç yazılmadan
    da bu iddia kurulamazdı, yazıldıktan sonra ise ilk günden geçer. Rolü
    gerileme kapısıdır — yarın biri kolaylık için `snapshot=` parametresi
    eklerse burası düşer.
    """
    imza = inspect.signature(approval.build_and_freeze_from_run)
    assert list(imza.parameters) == ["db", "run_id", "actor"]
    for ad, param in imza.parameters.items():
        if ad == "db":
            continue
        assert param.annotation == "str", f"{ad} beklenmeyen tip taşıyor"


async def test_snapshot_freeze_is_idempotent_write_once(pkg_db) -> None:
    """K-98: ikinci çağrı OLANI döner, yeni görüntü BASMAZ."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _onaya_hazir_kosu(pkg_db, sector_id)

    birinci = await approval.build_and_freeze_from_run(
        pkg_db, run_id=run_id, actor=ACTOR
    )
    ilk_sha = await pkg_db.fetchval(
        "SELECT snapshot_sha FROM social.sector_package_runs WHERE run_id = $1", run_id
    )
    # İkinci çağrı BAŞKA bir aktörle gelir: içerik değişse bile satır DEĞİŞMEZ.
    ikinci = await approval.build_and_freeze_from_run(
        pkg_db, run_id=run_id, actor="baska@otomaix"
    )

    assert ikinci == birinci
    son_sha = await pkg_db.fetchval(
        "SELECT snapshot_sha FROM social.sector_package_runs WHERE run_id = $1", run_id
    )
    assert son_sha == ilk_sha


async def test_second_freeze_rejected_by_db(pkg_db) -> None:
    """K-98 tetikleyicisi: dolu görüntünün DEĞİŞTİRİLMESİ veritabanında reddedilir.

    KENDİ KIRMIZISI YOKTUR: garanti 036 migration'ında zaten indi; bu test onun
    onay yolunda GERÇEKTEN yürürlükte olduğunun pozitif kontrolüdür.
    """
    sector_id = await _sub_sector(pkg_db)
    run_id = await _onaya_hazir_kosu(pkg_db, sector_id)
    await approval.build_and_freeze_from_run(pkg_db, run_id=run_id, actor=ACTOR)

    with pytest.raises(
        asyncpg.exceptions.IntegrityConstraintViolationError, match="DEGISMEZDIR"
    ):
        await pkg_db.execute(
            "UPDATE social.sector_package_runs SET approval_snapshot = $2 "
            "WHERE run_id = $1",
            run_id,
            {"sema": 1, "run_id": "uydurma"},
        )


async def test_approval_refused_when_run_not_verified(pkg_db) -> None:
    """Yedi kapıdan biri düşükse onay yüzeyi ÇALIŞMAZ."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _onaya_hazir_kosu(
        pkg_db, sector_id, sonuc="blocked", sebep="acik-soru-var"
    )
    with pytest.raises(runs.RunNotVerified):
        await approval.build_and_freeze_from_run(pkg_db, run_id=run_id, actor=ACTOR)


async def test_no_change_result_is_not_approvable(pkg_db) -> None:
    """`no_change` koşusu onaylanabilir DEĞİLDİR (K-93 kaydı vardır, onayı yok)."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _onaya_hazir_kosu(pkg_db, sector_id, sonuc="no_change")
    with pytest.raises(runs.RunNotVerified):
        await approval.build_and_freeze_from_run(pkg_db, run_id=run_id, actor=ACTOR)


async def test_approval_refused_when_gate_attestation_missing(pkg_db) -> None:
    """FAIL-CLOSED: tasdiki OLMAYAN kapı için görüntü kapı sonucu UYDURMAZ.

    Yedi kapı tasdikleri KAPSAMAZ — bir koşu yedi kapıdan geçip Katman-2'yi hiç
    koşmamış olabilir. Görüntü o durumda "sunuldu" diyemez; onay REDDEDİLİR.
    """
    sector_id = await _sub_sector(pkg_db)
    run_id = await _onaya_hazir_kosu(pkg_db, sector_id, katman2=False)
    with pytest.raises(approval.ApprovalRefused, match="katman2"):
        await approval.build_and_freeze_from_run(pkg_db, run_id=run_id, actor=ACTOR)


# ═══ 2. Sayılar · çıkarmalar · sıralama (K-41/K-42/K-71) ════════════════════


def _cikarma_satiri(unit_id: str, *, alan: str = "kanca_kaliplari") -> dict:
    return _karar_satiri(
        unit_id=unit_id,
        alan=alan,
        oge_yolu=f"{alan}[0]",
        karar="cikar",
        gerekce="Kalıp artık karşılık bulmuyor.",
        aktor="motor",
    )


async def test_removal_count_without_threshold_and_detail_available(pkg_db) -> None:
    """K-41: özet SAYI verir (eşik YOK); tam liste bir tık derinde."""
    sector_id = await _sub_sector(pkg_db)
    gunluk = [
        _cikarma_satiri("ku-aaaaaaaaaaaa"),
        _cikarma_satiri("ku-bbbbbbbbbbbb"),
        _karar_satiri(),
    ]
    run_id = await _onaya_hazir_kosu(pkg_db, sector_id, final_decision_log=gunluk)

    goruntu = await approval.build_and_freeze_from_run(
        pkg_db, run_id=run_id, actor=ACTOR
    )

    assert goruntu["cikarmalar"]["sayi"] == 2
    assert "esik" not in goruntu["cikarmalar"], "K-41: eşik YOKTUR"
    ozet = approval.render_summary(goruntu)
    assert "Çıkarılanlar: 2" in ozet
    detay = approval.render_removals_detail(goruntu)
    assert "ku-aaaaaaaaaaaa" in detay and "ku-bbbbbbbbbbbb" in detay
    # Tam liste ÖZETTE değil, detayda.
    assert "ku-aaaaaaaaaaaa" not in ozet


async def test_last_four_rounds_removals_included(pkg_db) -> None:
    """Son DÖRT turun çıkarma özeti görüntüde bulunur — beşincisi girmez."""
    sector_id = await _sub_sector(pkg_db)
    eski_kosular = []
    for sira in range(5):
        eski = await _onaya_hazir_kosu(
            pkg_db,
            sector_id,
            final_decision_log=[_cikarma_satiri(f"ku-{sira:012d}"), _karar_satiri()],
            taslak=False,
            created_at=datetime(2026, 9, sira + 1, 10, tzinfo=timezone.utc),
        )
        eski_kosular.append(eski)
    run_id = await _onaya_hazir_kosu(
        pkg_db, sector_id, created_at=datetime(2026, 9, 9, 10, tzinfo=timezone.utc)
    )

    goruntu = await approval.build_and_freeze_from_run(
        pkg_db, run_id=run_id, actor=ACTOR
    )

    ozet = goruntu["son_dort_tur_cikarmalari"]
    assert [kayit["run_id"] for kayit in ozet] == eski_kosular[::-1][:4]
    assert all(kayit["sayi"] == 1 for kayit in ozet)
    assert run_id not in [kayit["run_id"] for kayit in ozet], "kendi turu sayılmaz"


async def test_open_questions_prevent_approvable_result(pkg_db) -> None:
    """K-71: açık soru varsa onaylanabilir sonuç SUNULMAZ.

    Motor böyle bir koşuyu zaten `blocked` yapar (`acik-soru-var`); bu, onay
    yüzeyinin İKİNCİ katmanıdır — satır elle kurulup yüzeyin kendi kapısı ölçülür.
    """
    sector_id = await _sub_sector(pkg_db)
    run_id = await _onaya_hazir_kosu(
        pkg_db,
        sector_id,
        policy_report=_policy_report(acik_soru_kimlikleri=("as-1", "as-2")),
    )

    goruntu = await approval.build_and_freeze_from_run(
        pkg_db, run_id=run_id, actor=ACTOR
    )

    assert goruntu["acik_sorular"] == ["as-1", "as-2"]
    assert goruntu["onaylanabilir"] is False
    ozet = approval.render_summary(goruntu)
    assert "ONAYLANAMAZ" in ozet
    assert "as-1" in ozet


async def test_summary_never_lists_patterns(pkg_db) -> None:
    """Spec §9.6: yönetici kalıp listesi GÖRMEZ."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _onaya_hazir_kosu(pkg_db, sector_id)

    goruntu = await approval.build_and_freeze_from_run(
        pkg_db, run_id=run_id, actor=ACTOR
    )

    assert KANCA_METNI not in approval.render_summary(goruntu)
    assert KANCA_METNI not in approval.render_removals_detail(goruntu)
    # Görüntünün KENDİSİ de kalıp metni taşımaz — özet onu gizlemekle yetinmez.
    assert KANCA_METNI not in str(goruntu)


async def test_risky_classes_precede_neutral_counts(pkg_db) -> None:
    """K-42: riskli sınıflar nötr sayıların ÖNÜNDE ve sıra SABİT.

    Sıra kavramdan türetilir (riskli sınıf adları), elle seçilmiş örnekten değil.
    """
    sector_id = await _sub_sector(pkg_db)
    gunluk = [
        _cikarma_satiri("ku-aaaaaaaaaaaa"),
        _karar_satiri(karar="ekle", unit_id="ku-cccccccccccc", aktor="motor"),
    ]
    rapor = _policy_report(
        kararsizlar=(KararsizMadde(unit_id="ku-cccccccccccc", sebep="kanıt dengede"),),
        bulgular=(
            BulguIzi(
                sinif="acik_soru",
                unit_id="ku-cccccccccccc",
                detay="geri-ekleme önerisi: aday çıkarılanlar listesiyle eşleşiyor",
                kontrol="geri_ekleme_celiskisi",
            ),
            BulguIzi(
                sinif="mevzuat_dogrulanamadi",
                unit_id="ku-aaaaaaaaaaaa",
                detay="mevzuat referansı doğrulanamadı",
                kontrol="kanit",
            ),
        ),
    )
    run_id = await _onaya_hazir_kosu(
        pkg_db, sector_id, final_decision_log=gunluk, policy_report=rapor
    )

    goruntu = await approval.build_and_freeze_from_run(
        pkg_db, run_id=run_id, actor=ACTOR
    )
    ozet = approval.render_summary(goruntu)

    riskli_basliklar = [
        "Geri-ekleme çelişkileri",
        "Motor kararsızları",
        "Çıkarılanlar",
    ]
    notr_basliklar = ["Alan bazlı sayılar", "Değişim oranları", "İçerik hash'leri"]
    yerler = [ozet.index(baslik) for baslik in riskli_basliklar]
    assert yerler == sorted(yerler), "riskli sınıfların SIRASI sabit değil"
    assert max(yerler) < min(
        ozet.index(baslik) for baslik in notr_basliklar
    ), "riskli sınıflar nötr sayıların ARKASINA düştü"
    # Geri-ekleme çelişkisi bulgusu ATIFTAN ayırt edilir, metin eşleştirmesinden DEĞİL.
    assert goruntu["geri_ekleme_celiskileri"] == [
        {
            "unit_id": "ku-cccccccccccc",
            "detay": "geri-ekleme önerisi: aday çıkarılanlar listesiyle eşleşiyor",
        }
    ]
    assert goruntu["uyarilar"] == [
        {
            "sinif": "mevzuat_dogrulanamadi",
            "unit_id": "ku-aaaaaaaaaaaa",
            "detay": "mevzuat referansı doğrulanamadı",
        }
    ]


async def test_field_and_total_counts_come_from_decision_log(pkg_db) -> None:
    """Alan-bazlı + toplam sayılar karar günlüğünden türetilir."""
    sector_id = await _sub_sector(pkg_db)
    gunluk = [
        _cikarma_satiri("ku-aaaaaaaaaaaa"),
        _cikarma_satiri("ku-bbbbbbbbbbbb", alan="cta_kaliplari"),
        _karar_satiri(),
    ]
    run_id = await _onaya_hazir_kosu(pkg_db, sector_id, final_decision_log=gunluk)

    goruntu = await approval.build_and_freeze_from_run(
        pkg_db, run_id=run_id, actor=ACTOR
    )

    assert goruntu["sayilar"]["alan_bazli"] == {"kanca_kaliplari": 2, "cta_kaliplari": 1}
    assert goruntu["sayilar"]["toplam"] == 3


# ═══ 3. Karar kaydı ve olay (K-42b/K-99/R3) ═════════════════════════════════


async def _olaylar(db, run_id: str) -> list:
    return await db.fetch(
        "SELECT event_type, sector_id, package_id, actor, detail "
        "FROM social.package_events WHERE detail->>'run_id' = $1 "
        "ORDER BY created_at",
        run_id,
    )


async def test_approval_seconds_recorded(pkg_db) -> None:
    """K-42(b): onaya kaç saniyede basıldığı KAYDEDİLİR — eşik YOK."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _onaya_hazir_kosu(pkg_db, sector_id)
    goruntu = await approval.build_and_freeze_from_run(
        pkg_db, run_id=run_id, actor=ACTOR
    )

    await approval.record_decision(
        pkg_db,
        run_id=run_id,
        karar="onay",
        actor=ACTOR,
        seconds=3,
        snapshot_sha=identity.canonical_sha(goruntu),
    )

    satir = await pkg_db.fetchrow(
        "SELECT approval_karar, approval_seconds, approved_at "
        "FROM social.sector_package_runs WHERE run_id = $1",
        run_id,
    )
    assert satir["approval_karar"] == "onay"
    assert satir["approval_seconds"] == 3
    assert satir["approved_at"] is not None


async def test_approval_event_logged_with_actor_and_time(pkg_db) -> None:
    """K-99 POZİTİF KONTROL: onay olayı kimlik ve zamanla kaydedilir."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _onaya_hazir_kosu(pkg_db, sector_id)
    goruntu = await approval.build_and_freeze_from_run(
        pkg_db, run_id=run_id, actor=ACTOR
    )

    await approval.record_decision(
        pkg_db,
        run_id=run_id,
        karar="onay",
        actor=ACTOR,
        seconds=7,
        snapshot_sha=identity.canonical_sha(goruntu),
    )

    olaylar = await _olaylar(pkg_db, run_id)
    assert [o["event_type"] for o in olaylar] == ["approval"]
    assert olaylar[0]["actor"] == ACTOR
    assert olaylar[0]["detail"]["seconds"] == 7


async def test_rejection_event_logged(pkg_db) -> None:
    """Ret de KAYDEDİLİR — sessizce düşmez."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _onaya_hazir_kosu(pkg_db, sector_id)
    goruntu = await approval.build_and_freeze_from_run(
        pkg_db, run_id=run_id, actor=ACTOR
    )

    await approval.record_decision(
        pkg_db,
        run_id=run_id,
        karar="ret",
        actor=ACTOR,
        seconds=11,
        snapshot_sha=identity.canonical_sha(goruntu),
    )

    olaylar = await _olaylar(pkg_db, run_id)
    assert [o["event_type"] for o in olaylar] == ["rejection"]
    satir = await pkg_db.fetchval(
        "SELECT approval_karar FROM social.sector_package_runs WHERE run_id = $1",
        run_id,
    )
    assert satir == "ret"


async def _kararin_olayini_olc(pkg_db, karar: str, beklenen_tur: str) -> None:
    """R3 ölçümünün gövdesi — iki testin ADI sözleşmede AYRI AYRI yazılıdır."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _onaya_hazir_kosu(pkg_db, sector_id)
    goruntu = await approval.build_and_freeze_from_run(
        pkg_db, run_id=run_id, actor=ACTOR
    )
    beklenen_paket = await pkg_db.fetchval(
        "SELECT package_id FROM social.sector_package_runs WHERE run_id = $1", run_id
    )

    await approval.record_decision(
        pkg_db,
        run_id=run_id,
        karar=karar,
        actor=ACTOR,
        seconds=2,
        snapshot_sha=identity.canonical_sha(goruntu),
    )

    olaylar = await _olaylar(pkg_db, run_id)
    assert [o["event_type"] for o in olaylar] == [beklenen_tur]
    assert olaylar[0]["package_id"] == beklenen_paket
    assert olaylar[0]["sector_id"] == sector_id


async def test_approval_event_carries_package_id_from_locked_run(pkg_db) -> None:
    """R3: ONAY olayı paket kimliğini kilitli koşudan alır."""
    await _kararin_olayini_olc(pkg_db, "onay", "approval")


async def test_rejection_event_carries_package_id_from_locked_run(pkg_db) -> None:
    """R3: RET olayı da paket kimliğini kilitli koşudan alır."""
    await _kararin_olayini_olc(pkg_db, "ret", "rejection")


async def test_record_decision_refuses_run_without_package_link(pkg_db) -> None:
    """R3: taslağı yazılmamış koşuda onay REDDEDİLİR (olay yazılamadan patlardı)."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _onaya_hazir_kosu(pkg_db, sector_id, taslak=False)
    goruntu = await approval.build_and_freeze_from_run(
        pkg_db, run_id=run_id, actor=ACTOR
    )

    with pytest.raises(approval.ApprovalRefused, match="paket"):
        await approval.record_decision(
            pkg_db,
            run_id=run_id,
            karar="onay",
            actor=ACTOR,
            seconds=1,
            snapshot_sha=identity.canonical_sha(goruntu),
        )

    assert await _olaylar(pkg_db, run_id) == []


async def test_record_decision_takes_no_caller_supplied_package_id() -> None:
    """R3 YAPISAL KAPISI: imzada `package_id`/`sector_id` parametresi YOK.

    KENDİ KIRMIZISI YOKTUR (yapısal invariant); rolü gerileme kapısıdır.
    """
    imza = inspect.signature(approval.record_decision)
    assert list(imza.parameters) == [
        "db",
        "run_id",
        "karar",
        "actor",
        "seconds",
        "snapshot_sha",
    ]


async def test_run_mutation_after_freeze_invalidates_approval(pkg_db) -> None:
    """F18: karar dondurulmuş görüntünün HASH'ine bağlanır."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _onaya_hazir_kosu(pkg_db, sector_id)
    await approval.build_and_freeze_from_run(pkg_db, run_id=run_id, actor=ACTOR)

    with pytest.raises(approval.ApprovalRefused, match="hash"):
        await approval.record_decision(
            pkg_db,
            run_id=run_id,
            karar="onay",
            actor=ACTOR,
            seconds=1,
            snapshot_sha="f" * 64,
        )

    satir = await pkg_db.fetchval(
        "SELECT approval_karar FROM social.sector_package_runs WHERE run_id = $1",
        run_id,
    )
    assert satir is None
    assert await _olaylar(pkg_db, run_id) == []


@pytest.mark.parametrize("karar", ["", "onayla", "ONAY", "approve", None])
async def test_record_decision_refuses_unknown_decision(pkg_db, karar) -> None:
    """`KARARLAR` KAPALI kümedir — benzeyen değer kabul edilmez."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _onaya_hazir_kosu(pkg_db, sector_id)
    goruntu = await approval.build_and_freeze_from_run(
        pkg_db, run_id=run_id, actor=ACTOR
    )

    with pytest.raises(approval.ApprovalRefused, match="karar"):
        await approval.record_decision(
            pkg_db,
            run_id=run_id,
            karar=karar,
            actor=ACTOR,
            seconds=1,
            snapshot_sha=identity.canonical_sha(goruntu),
        )

    assert await _olaylar(pkg_db, run_id) == []


# ═══ 4. Kanıt kurucusu YOKTUR (arayüz eki R8) ══════════════════════════════


def test_approval_module_exposes_no_evidence_constructor() -> None:
    """R8: modülde `to_activation_evidence` YOK ve kanıt sınıfı import EDİLMEZ."""
    assert not hasattr(approval, "to_activation_evidence")
    assert not hasattr(approval, "ActivationGateEvidence")
    # Ad KODDA geçmez. Docstring'te geçmesi MEŞRUDUR (hükmün kendisi orada
    # yazılı); bu yüzden metin taraması değil AST taraması yapılır — "yorumda
    # yazılı" ile "kodda kullanılıyor" karıştırılmaz.
    agac = ast.parse(APPROVAL_KAYNAK)
    adlar = {
        dugum.id for dugum in ast.walk(agac) if isinstance(dugum, ast.Name)
    } | {
        dugum.attr for dugum in ast.walk(agac) if isinstance(dugum, ast.Attribute)
    }
    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.ImportFrom):
            adlar |= {takma.name for takma in dugum.names}
        elif isinstance(dugum, ast.Import):
            adlar |= {takma.name for takma in dugum.names}
    assert "ActivationGateEvidence" not in adlar
    assert "to_activation_evidence" not in adlar
    assert "sector_package_lifecycle" not in " ".join(adlar)


async def test_second_decision_is_refused(pkg_db) -> None:
    """Karar BİR KEZ verilir; ikincisi reddedilir ve ikinci olay YAZILMAZ."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _onaya_hazir_kosu(pkg_db, sector_id)
    goruntu = await approval.build_and_freeze_from_run(
        pkg_db, run_id=run_id, actor=ACTOR
    )
    sha = identity.canonical_sha(goruntu)
    await approval.record_decision(
        pkg_db, run_id=run_id, karar="onay", actor=ACTOR, seconds=1, snapshot_sha=sha
    )

    with pytest.raises(approval.ApprovalRefused, match="ZATEN"):
        await approval.record_decision(
            pkg_db, run_id=run_id, karar="ret", actor=ACTOR, seconds=2, snapshot_sha=sha
        )

    olaylar = await _olaylar(pkg_db, run_id)
    assert [o["event_type"] for o in olaylar] == ["approval"], "ikinci olay yazıldı"
    assert await pkg_db.fetchval(
        "SELECT approval_karar FROM social.sector_package_runs WHERE run_id = $1",
        run_id,
    ) == "onay"


@pytest.mark.parametrize("sema", [None, 0, 2, "1"])
def test_renderers_refuse_unknown_snapshot_schema(sema) -> None:
    """Bilinmeyen şema OKUNMAZ — iki gösterici de fail-closed durur."""
    goruntu = {"sema": sema} if sema is not None else {}
    for gosterici in (approval.render_summary, approval.render_removals_detail):
        with pytest.raises(approval.ApprovalRefused, match="şema"):
            gosterici(goruntu)


async def test_finding_without_attribution_refuses_snapshot(pkg_db) -> None:
    """FAIL-CLOSED: atıf damgasından ÖNCEKİ şemayla yazılmış bulgu görüntü kurmaz.

    Atıf olmadan geri-ekleme çelişkisi nötr "uyarı" sınıfına düşerdi — riskli
    sınıfın SESSİZ kaybı. Böyle bir satır yeni motor tarafından üretilemez;
    testte doğrudan kurulur (bayat satır senaryosu).
    """
    sector_id = await _sub_sector(pkg_db)
    run_id = await _onaya_hazir_kosu(pkg_db, sector_id)
    bayat = {
        "kararsizlar": [],
        "bulgular": [{"sinif": "acik_soru", "unit_id": "ku-cccccccccccc", "detay": "x"}],
        "uygulanmayan_kararlar": [],
        "acik_soru_kimlikleri": [],
    }
    await pkg_db.execute(
        "UPDATE social.sector_package_runs SET policy_report = $2 WHERE run_id = $1",
        run_id,
        bayat,
    )

    with pytest.raises(approval.ApprovalRefused, match="atıf"):
        await approval.build_and_freeze_from_run(pkg_db, run_id=run_id, actor=ACTOR)

    assert await pkg_db.fetchval(
        "SELECT approval_snapshot FROM social.sector_package_runs WHERE run_id = $1",
        run_id,
    ) is None
