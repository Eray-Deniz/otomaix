"""Plan 2 Task 15 — doğrulanmış koşudan pakete yazım, güncelleme, aktivasyon.

**Ölçülen doktrin:** *kanıt veritabanından OKUNUR, çağırandan alınmaz* (arayüz
eki R8). Bu dosyanın en önemli testi pozitif kontrol değil, ATLATMA yoludur:
elle kurulmuş bir sonuç nesnesi ya da elle kurulmuş bir kanıt sınıfı hiçbir
kapıdan geçemez.

**Köken jetonu (R8(c)).** Python'da `frozen=True` bir dataclass'ın literalden
kurulmasını engellemek MÜMKÜN DEĞİLDİR; o yüzden kapı sınıfın kurulumunda değil,
geçiş fonksiyonunun içindedir: kanıt yalnız veritabanı destekli bir fabrikanın
BASTIĞI tek kullanımlık bir jeton taşırsa kabul edilir, ve jeton geçişte HARCANIR.
"""

from __future__ import annotations

import asyncio
import contextlib
import inspect
import re
import uuid
from pathlib import Path

import asyncpg
import pytest

from app.core.database import _init_connection
from app.services import sector_package_lifecycle as lifecycle
from app.services.sector_package_lifecycle import (
    ActivationGateEvidence,
    EvidenceProvenanceInvalid,
    GateNotSatisfied,
    RollbackGateEvidence,
)
from app.services.sector_pipeline import approval, identity, readiness_items, runs
from app.services.sector_pipeline import writeback
from app.services.sector_pipeline.engine_contract import EngineResult, PolicyReport

from .test_sector_packages_service import _valid_content  # noqa: E402

# `pytest.ini` `asyncio_mode = auto` taşır — dosya düzeyinde `pytestmark`
# YAZILMAZ: senkron testleri de asyncio ile işaretler ve her koşumda uyarı
# üretirdi (depodaki diğer test dosyalarının hiçbiri de yazmıyor).

ACTOR = "admin@otomaix"
MOTOR_SURUM = "motor-1.0.0"
CONFIG_SHA = "c" * 64

WRITEBACK_KAYNAK = Path(writeback.__file__).read_text(encoding="utf-8")


# ═══ Ortak yardımcılar ══════════════════════════════════════════════════════


@pytest.fixture
async def pkg_db(db):
    """Üretimin KENDİ bağlantı yapılandırması + takvim kapısının besini.

    `_valid_content()` bir `ozel_gun` anahtarı taşır ve `insert_draft`'ın yazım
    kapısı o anahtarı SİSTEM TAKVİMİNE karşı doğrular; satır olmadan her yazım
    testi kapıya takılırdı.
    """
    await _init_connection(db)
    await db.execute(
        "INSERT INTO social.public_holidays (year, date, name_tr) "
        "VALUES (2099, '2099-10-29', $1)",
        "Cumhuriyet Bayramı",
    )
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


def _icerik(**overrides) -> dict:
    """Yazım kapısını GEÇEN içerik — Plan 1'in kendi geçerli örneği."""
    content = _valid_content()
    content.update(overrides)
    return content


def _gunluk(content: dict) -> list[dict]:
    """İçeriğin HER birimini bire bir sahiplenen karar günlüğü.

    Elle yazılmış sabit bir günlük kullanılmıyor: `insert_draft`'ın bütünlük
    kapısı iki yönlü küme eşitliği arar, yani günlük İÇERİKTEN türetilmezse
    her içerik değişiminde testler kapıya takılır ve ölçtükleri şey kayardı.
    """
    birimler = identity.enumerate_content_units(content)
    return [
        {
            "tur": "karar",
            "alan": oge["alan"],
            "oge_yolu": yol,
            "unit_id": f"ku-{sira:012x}",
            "oge_sha": oge["oge_sha"],
            "karar": "koru",
            "gerekce": "Kalıp sektörde hâlâ karşılık buluyor.",
            "kanit": "Denetçi-1 satırı ve doğrulanmış URL referansı mevcut.",
            "aktor": "motor",
            "kural_kimligi": "kural-koru",
            "kural_surumu": "v1",
        }
        for sira, (yol, oge) in enumerate(sorted(birimler.items()))
    ]


def _sonuc(
    *,
    content: dict | None = None,
    gunluk: list[dict] | None = None,
    sonuc: str = "activation_eligible",
    engine_version: str = MOTOR_SURUM,
    engine_config_sha: str = CONFIG_SHA,
    acik_sorular: tuple[str, ...] = (),
) -> EngineResult:
    aday = _icerik() if content is None else content
    kayit = _gunluk(aday) if gunluk is None else gunluk
    eligible = sonuc == "activation_eligible"
    return EngineResult(
        sonuc=sonuc,
        sebep=None if eligible else "motor kararı",
        final_candidate=aday if eligible else None,
        final_decision_log=tuple(kayit) if eligible else None,
        engine_diff={"degisen": 1},
        policy_report=PolicyReport(
            kararsizlar=(),
            bulgular=(),
            uygulanmayan_kararlar=(),
            acik_soru_kimlikleri=acik_sorular,
        ),
        barrier_report={"oran": 0.1},
        content_sha=identity.canonical_sha(aday) if eligible else None,
        decision_log_sha=identity.canonical_sha(kayit) if eligible else None,
        engine_version=engine_version,
        engine_config_sha=engine_config_sha,
    )


async def _kosu(
    db,
    sector_id: uuid.UUID,
    *,
    run_id: str | None = None,
    kosu_turu: str = "ilk",
    content: dict | None = None,
    gunluk: list[dict] | None = None,
    sonuc: str = "activation_eligible",
    engine_version: str = MOTOR_SURUM,
    engine_config_sha: str = CONFIG_SHA,
    katman1: str | None = "PASS",
    katman2: bool = True,
    hazirlik: bool = True,
    acik_sorular: tuple[str, ...] = (),
) -> str:
    """Tamamlanmış koşu + istenen tasdikler. Tasdikler AYRI AYRI kapatılabilir."""
    run_id = run_id or runs.new_run_id()
    await runs.open_run(db, sector_id=sector_id, run_id=run_id, kosu_turu=kosu_turu)
    await runs.record_result(
        db,
        run_id=run_id,
        result=_sonuc(
            content=content,
            gunluk=gunluk,
            sonuc=sonuc,
            engine_version=engine_version,
            engine_config_sha=engine_config_sha,
            acik_sorular=acik_sorular,
        ),
    )
    if katman1 is not None:
        await runs.attest_katman1(
            db, run_id=run_id, kosum_kimligi="k1-1", sonuc=katman1, actor=ACTOR
        )
    if katman2:
        await runs.attest_katman2(
            db, run_id=run_id, kosum_kimligi="k2-1", ozet="kör tur özeti", actor=ACTOR
        )
    if hazirlik:
        await _hazirlik_tasdiki(db, run_id)
    return run_id


async def _hazirlik_tasdiki(db, run_id: str) -> None:
    await runs.attest_readiness(
        db,
        run_id=run_id,
        kapi_maddeleri=tuple(sorted(readiness_items.KAPI_MADDELERI)),
        sinyal_maddeleri=tuple(sorted(readiness_items.SINYAL_MADDELERI)),
        actor=ACTOR,
    )


async def _onayli(db, run_id: str, *, karar: str = "onay") -> None:
    """Görüntüyü dondurur ve kararı yazar — Task 14'ün ÜRETİM yolu."""
    goruntu = await approval.build_and_freeze_from_run(db, run_id=run_id, actor=ACTOR)
    await approval.record_decision(
        db,
        run_id=run_id,
        karar=karar,
        actor=ACTOR,
        seconds=42,
        snapshot_sha=identity.canonical_sha(identity.cozulmus(goruntu)),
    )


async def _yazilmis_ve_onayli(
    db, sector_id: uuid.UUID, **kosu_kwargs
) -> tuple[str, uuid.UUID]:
    """Aktivasyona HAZIR zincir: koşu → taslak → dondurulmuş görüntü → onay."""
    run_id = await _kosu(db, sector_id, **kosu_kwargs)
    package_id = await writeback.write_draft_from_run(db, run_id=run_id, actor=ACTOR)
    await _onayli(db, run_id)
    return run_id, package_id


async def _paket_satiri(db, package_id: uuid.UUID):
    return await db.fetchrow(
        "SELECT id, version, status, content, decision_log, run_id "
        "FROM social.sector_packages WHERE id = $1",
        package_id,
    )


async def _koan(db, sector_id: uuid.UUID) -> list[tuple[int, str]]:
    rows = await db.fetch(
        "SELECT version, status FROM social.sector_packages WHERE sector_id = $1 "
        "ORDER BY version",
        sector_id,
    )
    return [(r["version"], r["status"]) for r in rows]


@contextlib.asynccontextmanager
async def _committed_ortam(test_db_setup):
    """COMMIT EDİLMİŞ sektör + takvim satırı — eşzamanlılık testleri için.

    `db` fixture'ı her testi geri alınan bir transaction'da koşturur; iki AYRI
    bağlantının aynı satırları görmesi gereken yarış testleri o yüzden kendi
    committed evrenini kurar ve sonunda ELLE temizler.
    """
    from .conftest import _require_test_database

    url = _require_test_database(test_db_setup)
    setup = await asyncpg.connect(url)
    await _init_connection(setup)
    sector_id = None
    try:
        sector_id = await _sub_sector(setup)
        await setup.execute(
            "INSERT INTO social.public_holidays (year, date, name_tr) "
            "VALUES (2099, '2099-10-29', $1) ON CONFLICT DO NOTHING",
            "Cumhuriyet Bayramı",
        )
        yield url, setup, sector_id
    finally:
        if sector_id is not None:
            await setup.execute(
                "DELETE FROM social.package_events WHERE sector_id = $1", sector_id
            )
            await setup.execute(
                "DELETE FROM social.sector_package_runs WHERE sector_id = $1", sector_id
            )
            await setup.execute(
                "DELETE FROM social.sector_packages WHERE sector_id = $1", sector_id
            )
            await setup.execute("DELETE FROM social.sectors WHERE id = $1", sector_id)
        await setup.execute(
            "DELETE FROM social.public_holidays WHERE year = 2099 AND name_tr = $1",
            "Cumhuriyet Bayramı",
        )
        await setup.close()


@contextlib.asynccontextmanager
async def _isciler(url, sayi: int = 2):
    baglantilar = []
    try:
        for _ in range(sayi):
            conn = await asyncpg.connect(url)
            await _init_connection(conn)
            baglantilar.append(conn)
        yield baglantilar
    finally:
        for conn in baglantilar:
            await conn.close()


# ═══ 1. Yazım yolu — YEDİ kapı kilitli koşudan okunur ═══════════════════════


async def test_persisted_eligible_run_writes_draft(pkg_db):
    """POZİTİF KONTROL: kalıcı ve uygun koşu taslağa dönüşür."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _kosu(pkg_db, sector_id)

    package_id = await writeback.write_draft_from_run(
        pkg_db, run_id=run_id, actor=ACTOR
    )

    satir = await _paket_satiri(pkg_db, package_id)
    assert satir["status"] == "draft"
    assert satir["version"] == 1
    assert satir["run_id"] == run_id
    bagli = await pkg_db.fetchval(
        "SELECT package_id FROM social.sector_package_runs WHERE run_id = $1", run_id
    )
    assert bagli == package_id, "koşu satırı yazılan taslağa BAĞLANMALI"


async def test_unpersisted_result_object_rejected(pkg_db):
    """ASIL ATLATMA YOLU: motor hiç koşmadan yazım YAPILAMAZ.

    İki ayak birden ölçülür ve biri diğerinin yerine GEÇMEZ:
    (a) imzada bir sonuç/kanıt nesnesi taşıyacak parametre YOKTUR — yani elle
        kurulmuş bir `EngineResult` fonksiyona verilemez bile;
    (b) satırı olmayan bir `run_id` REDDEDİLİR — kalıcılık kapısı çalışır.
    """
    imza = inspect.signature(writeback.write_draft_from_run)
    assert set(imza.parameters) == {"db", "run_id", "actor"}
    for ad, parametre in imza.parameters.items():
        if ad == "db":
            continue
        assert parametre.kind is inspect.Parameter.KEYWORD_ONLY

    with pytest.raises(runs.RunNotVerified):
        await writeback.write_draft_from_run(
            pkg_db, run_id="kosu-hic-yazilmadi", actor=ACTOR
        )


async def test_synthesis_only_candidate_rejected(pkg_db):
    """Sentez adayı motor kararından GEÇMEDEN yazılamaz (`sonuc` kapısı)."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _kosu(pkg_db, sector_id, sonuc="no_change")

    with pytest.raises(runs.RunNotVerified, match="sonuc"):
        await writeback.write_draft_from_run(pkg_db, run_id=run_id, actor=ACTOR)


async def test_hash_mismatch_rejected(pkg_db):
    """`content_sha` adayla eşleşmiyorsa yazım yok."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _kosu(pkg_db, sector_id)
    await pkg_db.execute(
        "UPDATE social.sector_package_runs SET content_sha = $2 WHERE run_id = $1",
        run_id,
        "d" * 64,
    )

    with pytest.raises(runs.RunNotVerified, match="content_sha"):
        await writeback.write_draft_from_run(pkg_db, run_id=run_id, actor=ACTOR)


async def test_missing_engine_stamp_rejected(pkg_db):
    """Motor damgası boşsa koşu doğrulanmamıştır."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _kosu(pkg_db, sector_id)
    await pkg_db.execute(
        "UPDATE social.sector_package_runs SET engine_config_sha = '' WHERE run_id = $1",
        run_id,
    )

    with pytest.raises(runs.RunNotVerified, match="engine_config_sha"):
        await writeback.write_draft_from_run(pkg_db, run_id=run_id, actor=ACTOR)


async def test_missing_final_decision_log_rejected(pkg_db):
    """F19: karar günlüğü BOŞ olan koşu taslak yazamaz."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _kosu(pkg_db, sector_id)
    await pkg_db.execute(
        "UPDATE social.sector_package_runs SET final_decision_log = $2 "
        "WHERE run_id = $1",
        run_id,
        [],
    )

    with pytest.raises(runs.RunNotVerified, match="final_decision_log"):
        await writeback.write_draft_from_run(pkg_db, run_id=run_id, actor=ACTOR)


async def test_decision_log_sha_mismatch_rejected(pkg_db):
    """F19: günlük hash'i günlükle ayrıştıysa yazım yok."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _kosu(pkg_db, sector_id)
    await pkg_db.execute(
        "UPDATE social.sector_package_runs SET decision_log_sha = $2 WHERE run_id = $1",
        run_id,
        "e" * 64,
    )

    with pytest.raises(runs.RunNotVerified, match="decision_log_sha"):
        await writeback.write_draft_from_run(pkg_db, run_id=run_id, actor=ACTOR)


async def test_written_draft_carries_engine_decision_log_not_placeholder(pkg_db):
    """F19 POZİTİF KONTROL: yazılan günlük MOTORUNKİDİR, yer tutucu değil.

    Plan 1'in `insert_draft`'ı günlük verilmezse tek satırlık bir
    `draft_created` izi yazar. O iz buraya sızarsa karar günlüğünü okuyan her
    kapı boş bir tarihçe görür ve K-84 kimlik zinciri kopar.
    """
    sector_id = await _sub_sector(pkg_db)
    content = _icerik()
    gunluk = _gunluk(content)
    run_id = await _kosu(pkg_db, sector_id, content=content, gunluk=gunluk)

    package_id = await writeback.write_draft_from_run(
        pkg_db, run_id=run_id, actor=ACTOR
    )

    satir = await _paket_satiri(pkg_db, package_id)
    yazilan = list(satir["decision_log"])
    assert yazilan == gunluk
    assert all(row.get("event") != "draft_created" for row in yazilan)
    assert identity.canonical_sha(yazilan) == identity.canonical_sha(gunluk)


async def test_incomplete_run_rejected(pkg_db):
    """`durum != 'tamamlandi'` — yarım koşu taslak yazamaz."""
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")
    await runs.mark_incomplete(
        pkg_db, run_id=run_id, asama="motor", sebep="denetçi düştü"
    )

    with pytest.raises(runs.RunNotVerified, match="durum"):
        await writeback.write_draft_from_run(pkg_db, run_id=run_id, actor=ACTOR)


@pytest.mark.parametrize("sonuc", ["no_change", "blocked"])
async def test_no_change_and_blocked_write_no_draft(pkg_db, sonuc):
    """Motorun iki olumsuz sonucu da taslak ÜRETMEZ ve satır bırakmaz."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _kosu(pkg_db, sector_id, sonuc=sonuc)

    with pytest.raises(runs.RunNotVerified):
        await writeback.write_draft_from_run(pkg_db, run_id=run_id, actor=ACTOR)

    assert await _koan(pkg_db, sector_id) == []


async def test_writeback_cannot_read_run_row_outside_loader():
    """YAPISAL: koşu satırının TEK okuma kapısı `load_verified_run`'dır.

    İkinci bir `SELECT ... FROM social.sector_package_runs` yazıldığı an ikinci
    bir kapı listesi doğar; yedi kapı orada koşmaz ve doğrulanmamış bir satır
    yazım yoluna sızabilir. Tarama YAZIMLARI kapsamaz: koşu satırına taslak
    bağını yazmak bu modülün işidir.
    """
    okumalar = re.findall(
        r"SELECT\b[^;\"']*?\bFROM\s+social\.sector_package_runs",
        WRITEBACK_KAYNAK,
        flags=re.IGNORECASE | re.DOTALL,
    )
    assert okumalar == [], f"ikinci kapı listesi: {okumalar}"
    assert "load_verified_run" in WRITEBACK_KAYNAK


# ═══ 2. Tekrar oynatma ve yarış — tek taslak ════════════════════════════════


async def test_replay_returns_existing_draft_without_new_version(pkg_db):
    """Aynı koşu ikinci kez yazıldığında YENİ sürüm yakılmaz (idempotency)."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _kosu(pkg_db, sector_id)

    birinci = await writeback.write_draft_from_run(pkg_db, run_id=run_id, actor=ACTOR)
    ikinci = await writeback.write_draft_from_run(pkg_db, run_id=run_id, actor=ACTOR)

    assert birinci == ikinci
    assert await _koan(pkg_db, sector_id) == [(1, "draft")]


async def test_concurrent_writes_yield_single_draft(test_db_setup):
    """İki eşzamanlı yazım TEK taslak bırakır — kaybeden AÇIKÇA düşer."""
    async with _committed_ortam(test_db_setup) as (url, setup, sector_id):
        run_id = await _kosu(setup, sector_id)

        async def _yaz(conn):
            try:
                return await writeback.write_draft_from_run(
                    conn, run_id=run_id, actor=ACTOR
                )
            except Exception as exc:  # kaybeden taraf AÇIKÇA düşmeli
                return type(exc).__name__

        async with _isciler(url) as isciler:
            sonuclar = await asyncio.gather(*[_yaz(conn) for conn in isciler])

        yazilanlar = [s for s in sonuclar if isinstance(s, uuid.UUID)]
        assert yazilanlar, f"iki taraf da düştü: {sonuclar}"
        assert len(set(yazilanlar)) == 1, f"iki farklı taslak yazıldı: {sonuclar}"
        assert await _koan(setup, sector_id) == [(1, "draft")]


# ═══ 3. K-72 / K-106 — düzeltme ikinci sürüm YAKMAZ ═════════════════════════


async def _duzeltme_kosusu(
    db, sector_id: uuid.UUID, *, content: dict | None = None, **kwargs
) -> tuple[str, str, uuid.UUID]:
    """Reddedilmiş ana koşu + ondan açılmış TAMAMLANMIŞ düzeltme koşusu.

    Dönen: `(ana_run_id, duzeltme_run_id, package_id)`.
    """
    ana_run_id = await _kosu(db, sector_id)
    package_id = await writeback.write_draft_from_run(
        db, run_id=ana_run_id, actor=ACTOR
    )
    await _onayli(db, ana_run_id, karar="ret")

    duzeltme_run_id = await runs.open_correction_run(
        db, parent_run_id=ana_run_id, actor=ACTOR
    )
    yeni_icerik = _icerik() if content is None else content
    await runs.record_result(
        db,
        run_id=duzeltme_run_id,
        result=_sonuc(content=yeni_icerik, **kwargs),
    )
    await runs.attest_katman1(
        db, run_id=duzeltme_run_id, kosum_kimligi="k1-2", sonuc="PASS", actor=ACTOR
    )
    await runs.attest_katman2(
        db, run_id=duzeltme_run_id, kosum_kimligi="k2-2", ozet="ikinci tur", actor=ACTOR
    )
    await _hazirlik_tasdiki(db, duzeltme_run_id)
    return ana_run_id, duzeltme_run_id, package_id


def _degistirilmis_icerik() -> dict:
    """Ana koşununkinden FARKLI ama yazım kapısını geçen içerik."""
    return _icerik(ton_ve_dil="Sade ve güven veren; sertifika dili öne çıkar.")


async def test_write_path_refuses_correction_run(pkg_db):
    """K-106: düzeltme koşusu İKİNCİ bir sürüm yakamaz — yazım yolu REDDEDER."""
    sector_id = await _sub_sector(pkg_db)
    _, duzeltme_run_id, _ = await _duzeltme_kosusu(pkg_db, sector_id)

    with pytest.raises(runs.CorrectionRunRefused):
        await writeback.write_draft_from_run(
            pkg_db, run_id=duzeltme_run_id, actor=ACTOR
        )

    assert await _koan(pkg_db, sector_id) == [(1, "draft")]


async def test_update_path_requires_correction_lineage(pkg_db):
    """Güncelleme yolu soyağacı ŞART KOŞAR: `duzeltilen_run_id` boşsa çalışmaz."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _kosu(pkg_db, sector_id)
    await writeback.write_draft_from_run(pkg_db, run_id=run_id, actor=ACTOR)

    with pytest.raises(writeback.WritebackRefused, match="soyağac|duzeltilen"):
        await writeback.update_draft_from_run(pkg_db, run_id=run_id, actor=ACTOR)


async def test_correction_updates_parent_target_draft(pkg_db):
    """K-106 POZİTİF KONTROL: düzeltme AYNI satırı yerinde günceller."""
    sector_id = await _sub_sector(pkg_db)
    yeni_icerik = _degistirilmis_icerik()
    _, duzeltme_run_id, package_id = await _duzeltme_kosusu(
        pkg_db, sector_id, content=yeni_icerik
    )

    await writeback.update_draft_from_run(
        pkg_db, run_id=duzeltme_run_id, actor=ACTOR
    )

    satir = await _paket_satiri(pkg_db, package_id)
    assert satir["content"] == yeni_icerik
    assert list(satir["decision_log"]) == _gunluk(yeni_icerik)
    assert await _koan(pkg_db, sector_id) == [(1, "draft")], "ikinci sürüm YAKILDI"


async def test_update_from_run_keeps_version_number(pkg_db):
    """K-106: sürüm numarası DEĞİŞMEZ."""
    sector_id = await _sub_sector(pkg_db)
    _, duzeltme_run_id, package_id = await _duzeltme_kosusu(
        pkg_db, sector_id, content=_degistirilmis_icerik()
    )
    onceki = await _paket_satiri(pkg_db, package_id)

    await writeback.update_draft_from_run(
        pkg_db, run_id=duzeltme_run_id, actor=ACTOR
    )

    sonraki = await _paket_satiri(pkg_db, package_id)
    assert sonraki["version"] == onceki["version"] == 1
    assert sonraki["id"] == onceki["id"]


async def test_update_path_uses_same_seven_gates(pkg_db):
    """Güncelleme AYRI bir kapı listesi TAŞIMAZ — aynı doğrulayıcıdan geçer.

    İki ayak: (a) kapılardan biri düşen bir düzeltme koşusu güncelleme yapamaz;
    (b) yapısal olarak gövde `load_verified_run`'ı çağırır.
    """
    sector_id = await _sub_sector(pkg_db)
    _, duzeltme_run_id, _ = await _duzeltme_kosusu(
        pkg_db, sector_id, content=_degistirilmis_icerik()
    )
    await pkg_db.execute(
        "UPDATE social.sector_package_runs SET engine_version = '' WHERE run_id = $1",
        duzeltme_run_id,
    )

    with pytest.raises(runs.RunNotVerified, match="engine_version"):
        await writeback.update_draft_from_run(
            pkg_db, run_id=duzeltme_run_id, actor=ACTOR
        )

    govde = inspect.getsource(writeback.update_draft_from_run)
    assert "load_verified_run" in govde


async def test_update_rejected_on_missing_decision_log(pkg_db):
    """F19 güncelleme yolu: günlüğü boş koşu yerinde güncelleme YAPAMAZ."""
    sector_id = await _sub_sector(pkg_db)
    _, duzeltme_run_id, _ = await _duzeltme_kosusu(
        pkg_db, sector_id, content=_degistirilmis_icerik()
    )
    await pkg_db.execute(
        "UPDATE social.sector_package_runs SET final_decision_log = $2 "
        "WHERE run_id = $1",
        duzeltme_run_id,
        [],
    )

    with pytest.raises(runs.RunNotVerified, match="final_decision_log"):
        await writeback.update_draft_from_run(
            pkg_db, run_id=duzeltme_run_id, actor=ACTOR
        )


async def test_update_rejected_on_decision_log_hash_mismatch(pkg_db):
    """F19 güncelleme yolu: günlük hash'i ayrıştıysa güncelleme yok."""
    sector_id = await _sub_sector(pkg_db)
    _, duzeltme_run_id, _ = await _duzeltme_kosusu(
        pkg_db, sector_id, content=_degistirilmis_icerik()
    )
    await pkg_db.execute(
        "UPDATE social.sector_package_runs SET decision_log_sha = $2 WHERE run_id = $1",
        duzeltme_run_id,
        "f" * 64,
    )

    with pytest.raises(runs.RunNotVerified, match="decision_log_sha"):
        await writeback.update_draft_from_run(
            pkg_db, run_id=duzeltme_run_id, actor=ACTOR
        )


async def test_update_from_run_requires_eligible_persisted_run(pkg_db):
    """Kalıcı olmayan / uygun olmayan koşu güncelleme yapamaz."""
    sector_id = await _sub_sector(pkg_db)
    _, duzeltme_run_id, _ = await _duzeltme_kosusu(
        pkg_db, sector_id, content=_degistirilmis_icerik()
    )
    await pkg_db.execute(
        "UPDATE social.sector_package_runs SET sonuc = 'blocked' WHERE run_id = $1",
        duzeltme_run_id,
    )

    with pytest.raises(runs.RunNotVerified, match="sonuc"):
        await writeback.update_draft_from_run(
            pkg_db, run_id=duzeltme_run_id, actor=ACTOR
        )

    with pytest.raises(runs.RunNotVerified):
        await writeback.update_draft_from_run(
            pkg_db, run_id="kosu-hic-yazilmadi", actor=ACTOR
        )


async def test_update_from_run_rejected_on_active_row(pkg_db):
    """Yerinde güncelleme YALNIZ taslak satırında olur — aktif sürüm dokunulmaz."""
    sector_id = await _sub_sector(pkg_db)
    _, duzeltme_run_id, package_id = await _duzeltme_kosusu(
        pkg_db, sector_id, content=_degistirilmis_icerik()
    )
    await pkg_db.execute(
        "UPDATE social.sector_packages SET status = 'active' WHERE id = $1", package_id
    )

    # Kapı yaşam döngüsü katmanındadır ve güncellemenin KENDİ `WHERE`'inde
    # durur (yarış-güvenli). Writeback'te ikinci bir durum ön-kontrolü YAZILMADI:
    # iki kapı iki davranış demektir ve mesaj kalitesi için kapı çoğaltılmaz.
    with pytest.raises(lifecycle.LifecycleError, match="draft"):
        await writeback.update_draft_from_run(
            pkg_db, run_id=duzeltme_run_id, actor=ACTOR
        )


async def test_parent_snapshot_unchanged_after_correction(pkg_db):
    """K-98: ana koşunun dondurulmuş görüntüsüne DOKUNULMAZ."""
    sector_id = await _sub_sector(pkg_db)
    ana_run_id, duzeltme_run_id, _ = await _duzeltme_kosusu(
        pkg_db, sector_id, content=_degistirilmis_icerik()
    )
    onceki = await pkg_db.fetchrow(
        "SELECT approval_snapshot, snapshot_sha FROM social.sector_package_runs "
        "WHERE run_id = $1",
        ana_run_id,
    )

    await writeback.update_draft_from_run(
        pkg_db, run_id=duzeltme_run_id, actor=ACTOR
    )

    sonraki = await pkg_db.fetchrow(
        "SELECT approval_snapshot, snapshot_sha FROM social.sector_package_runs "
        "WHERE run_id = $1",
        ana_run_id,
    )
    assert sonraki["snapshot_sha"] == onceki["snapshot_sha"]
    assert sonraki["approval_snapshot"] == onceki["approval_snapshot"]


async def test_correction_mints_its_own_snapshot_and_approval(pkg_db):
    """Düzeltme koşusu KENDİ taze görüntüsünü basar ve KENDİ onayını alır."""
    sector_id = await _sub_sector(pkg_db)
    ana_run_id, duzeltme_run_id, _ = await _duzeltme_kosusu(
        pkg_db, sector_id, content=_degistirilmis_icerik()
    )
    await writeback.update_draft_from_run(
        pkg_db, run_id=duzeltme_run_id, actor=ACTOR
    )

    await _onayli(pkg_db, duzeltme_run_id)

    satirlar = {
        r["run_id"]: r
        for r in await pkg_db.fetch(
            "SELECT run_id, snapshot_sha, approval_karar "
            "FROM social.sector_package_runs WHERE run_id = ANY($1::text[])",
            [ana_run_id, duzeltme_run_id],
        )
    }
    assert satirlar[ana_run_id]["approval_karar"] == "ret"
    assert satirlar[duzeltme_run_id]["approval_karar"] == "onay"
    assert (
        satirlar[duzeltme_run_id]["snapshot_sha"]
        != satirlar[ana_run_id]["snapshot_sha"]
    ), "düzeltme ana koşunun görüntüsünü DEVRALAMAZ"


async def test_periodic_run_after_rollback_or_deactivation_writes_new_version(pkg_db):
    """Düzeltme soyağacı SIRADAN turu engellemez — periyodik koşu yeni sürüm yazar."""
    sector_id = await _sub_sector(pkg_db)
    _, duzeltme_run_id, package_id = await _duzeltme_kosusu(
        pkg_db, sector_id, content=_degistirilmis_icerik()
    )
    await writeback.update_draft_from_run(
        pkg_db, run_id=duzeltme_run_id, actor=ACTOR
    )
    await pkg_db.execute(
        "UPDATE social.sector_packages SET status = 'archived' WHERE id = $1",
        package_id,
    )

    periyodik = await _kosu(pkg_db, sector_id, kosu_turu="periyodik")
    yeni_paket = await writeback.write_draft_from_run(
        pkg_db, run_id=periyodik, actor=ACTOR
    )

    assert yeni_paket != package_id
    assert await _koan(pkg_db, sector_id) == [(1, "archived"), (2, "draft")]


# ═══ 4. F18 — aktivasyon kanıt zinciri KİLİTLİ SATIRDAN doğrulanır ══════════


async def _tasdiki_yaz(db, run_id: str, kolon: str, payload) -> None:
    """Tasdik kolonunu DOĞRUDAN yazar/siler — kapının kendi ölçümü için.

    Onay yüzeyi eksik tasdikle görüntü DONDURMAZ; yani "tasdik yok" hâlini
    onaydan ÖNCE kuramayız. Zincir normal yoldan kurulur, sonra satır bozulur —
    ölçülen şey AKTİVASYONUN kendi kapısıdır, onay yüzeyininki değil.
    """
    await db.execute(
        f"UPDATE social.sector_package_runs SET {kolon} = $2 WHERE run_id = $1",
        run_id,
        payload,
    )


async def test_activation_succeeds_with_full_attestation_chain(pkg_db):
    """F18 POZİTİF KONTROL: zincirin tamamı sağlamsa aktivasyon iner."""
    sector_id = await _sub_sector(pkg_db)
    run_id, package_id = await _yazilmis_ve_onayli(pkg_db, sector_id)

    await writeback.activate_from_snapshot(pkg_db, run_id=run_id, actor=ACTOR)

    assert await _koan(pkg_db, sector_id) == [(1, "active")]
    olaylar = await pkg_db.fetch(
        "SELECT event_type, package_id FROM social.package_events WHERE sector_id = $1",
        sector_id,
    )
    assert [o["event_type"] for o in olaylar] == ["approval", "activation"]
    assert olaylar[-1]["package_id"] == package_id


async def test_activation_requires_recorded_approval(pkg_db):
    """Karar HİÇ yoksa aktivasyon yok — dondurulmuş görüntü tek başına yetmez."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _kosu(pkg_db, sector_id)
    await writeback.write_draft_from_run(pkg_db, run_id=run_id, actor=ACTOR)
    await approval.build_and_freeze_from_run(pkg_db, run_id=run_id, actor=ACTOR)

    with pytest.raises(writeback.ActivationRefused, match="(?i)karar"):
        await writeback.activate_from_snapshot(pkg_db, run_id=run_id, actor=ACTOR)

    assert await _koan(pkg_db, sector_id) == [(1, "draft")]


async def test_activation_refused_after_rejection(pkg_db):
    """Reddedilmiş koşu aktive EDİLEMEZ."""
    sector_id = await _sub_sector(pkg_db)
    run_id = await _kosu(pkg_db, sector_id)
    await writeback.write_draft_from_run(pkg_db, run_id=run_id, actor=ACTOR)
    await _onayli(pkg_db, run_id, karar="ret")

    with pytest.raises(writeback.ActivationRefused, match="ret"):
        await writeback.activate_from_snapshot(pkg_db, run_id=run_id, actor=ACTOR)

    assert await _koan(pkg_db, sector_id) == [(1, "draft")]


@pytest.mark.parametrize(
    "tasdik",
    [None, {"kosum_kimligi": "k1-1", "sonuc": "FAIL", "actor": ACTOR}],
    ids=["missing", "failed"],
)
async def test_activation_refused_when_katman1_attestation_missing_or_failed(
    pkg_db, tasdik
):
    """Katman-1 tasdiki YOK ya da PASS değil → aktivasyon RED."""
    sector_id = await _sub_sector(pkg_db)
    run_id, _ = await _yazilmis_ve_onayli(pkg_db, sector_id)
    await _tasdiki_yaz(pkg_db, run_id, "katman1_attestation", tasdik)

    with pytest.raises((writeback.ActivationRefused, GateNotSatisfied)):
        await writeback.activate_from_snapshot(pkg_db, run_id=run_id, actor=ACTOR)

    assert await _koan(pkg_db, sector_id) == [(1, "draft")]


async def test_activation_refused_when_readiness_not_approved(pkg_db):
    """Hazırlık listesi ONAYLANMAMIŞSA aktivasyon yok (K-69)."""
    sector_id = await _sub_sector(pkg_db)
    run_id, _ = await _yazilmis_ve_onayli(pkg_db, sector_id)
    await _tasdiki_yaz(pkg_db, run_id, "readiness_attestation", None)

    with pytest.raises((writeback.ActivationRefused, GateNotSatisfied)):
        await writeback.activate_from_snapshot(pkg_db, run_id=run_id, actor=ACTOR)

    assert await _koan(pkg_db, sector_id) == [(1, "draft")]


@pytest.mark.parametrize(
    "sha_alani",
    [{}, {"madde_kumesi_sha": ""}, {"madde_kumesi_sha": "   "}],
    ids=["missing", "empty", "whitespace"],
)
async def test_activation_refused_when_madde_kumesi_sha_missing_or_blank(
    pkg_db, sha_alani
):
    """A4: imza yok / boş / yalnız-boşluk → RED. Geriye uyum yedeği YOKTUR."""
    sector_id = await _sub_sector(pkg_db)
    run_id, _ = await _yazilmis_ve_onayli(pkg_db, sector_id)
    await _tasdiki_yaz(
        pkg_db,
        run_id,
        "readiness_attestation",
        {"onaylandi": True, "actor": ACTOR, **sha_alani},
    )

    with pytest.raises((writeback.ActivationRefused, GateNotSatisfied)):
        await writeback.activate_from_snapshot(pkg_db, run_id=run_id, actor=ACTOR)

    assert await _koan(pkg_db, sector_id) == [(1, "draft")]


@pytest.mark.parametrize(
    "sha",
    ["a" * 64, f" {readiness_items.MADDE_KUMESI_SHA} "],
    ids=["eski_surum", "bosluk_sarmali"],
)
async def test_activation_refused_when_madde_kumesi_sha_differs_from_current(
    pkg_db, sha
):
    """A4: karşılaştırma NORMALİZASYONSUZDUR — boşluk-sarmalı değer de GEÇMEZ."""
    sector_id = await _sub_sector(pkg_db)
    run_id, _ = await _yazilmis_ve_onayli(pkg_db, sector_id)
    await _tasdiki_yaz(
        pkg_db,
        run_id,
        "readiness_attestation",
        {"onaylandi": True, "actor": ACTOR, "madde_kumesi_sha": sha},
    )

    with pytest.raises((writeback.ActivationRefused, GateNotSatisfied)):
        await writeback.activate_from_snapshot(pkg_db, run_id=run_id, actor=ACTOR)

    assert await _koan(pkg_db, sector_id) == [(1, "draft")]


async def test_activation_succeeds_when_madde_kumesi_sha_matches_current(pkg_db):
    """A4 POZİTİF KONTROL: imza BİREBİR eşitse kapı açılır."""
    sector_id = await _sub_sector(pkg_db)
    run_id, _ = await _yazilmis_ve_onayli(pkg_db, sector_id)
    tasdik = await pkg_db.fetchval(
        "SELECT readiness_attestation FROM social.sector_package_runs WHERE run_id = $1",
        run_id,
    )
    assert tasdik["madde_kumesi_sha"] == readiness_items.MADDE_KUMESI_SHA

    await writeback.activate_from_snapshot(pkg_db, run_id=run_id, actor=ACTOR)

    assert await _koan(pkg_db, sector_id) == [(1, "active")]


async def test_activation_refused_when_katman2_attestation_missing(pkg_db):
    """Katman-2 KOŞULMUŞ ve SUNULMUŞ olmalı — varlığı ön koşuldur."""
    sector_id = await _sub_sector(pkg_db)
    run_id, _ = await _yazilmis_ve_onayli(pkg_db, sector_id)
    await _tasdiki_yaz(pkg_db, run_id, "katman2_attestation", None)

    with pytest.raises(writeback.ActivationRefused, match="[Kk]atman-?2"):
        await writeback.activate_from_snapshot(pkg_db, run_id=run_id, actor=ACTOR)

    assert await _koan(pkg_db, sector_id) == [(1, "draft")]


async def test_activation_succeeds_with_negative_katman2_result(pkg_db):
    """POZİTİF KONTROL: Katman-2'nin SONUCU kapı DEĞİLDİR (spec §10.2).

    Olumsuz bir özet taşıyan tasdik aktivasyonu DURDURMAZ; durduran tek şey
    tasdikin hiç olmamasıdır. Kapı olsaydı spec'in okumadığı bir sonucu okuyor
    olurduk.
    """
    sector_id = await _sub_sector(pkg_db)
    run_id, _ = await _yazilmis_ve_onayli(pkg_db, sector_id)
    await _tasdiki_yaz(
        pkg_db,
        run_id,
        "katman2_attestation",
        {
            "kosum_kimligi": "k2-1",
            "ozet": "kör tur sektörel ayrışma GÖSTERMEDİ",
            "actor": ACTOR,
            "sunuldu": True,
        },
    )

    await writeback.activate_from_snapshot(pkg_db, run_id=run_id, actor=ACTOR)

    assert await _koan(pkg_db, sector_id) == [(1, "active")]


# ═══ 5. NEW-3 — GÖRÜLMEYEN BAYT aktive edilemez ═════════════════════════════


async def test_activation_succeeds_when_draft_unchanged_since_approval(pkg_db):
    """POZİTİF KONTROL: taslak onaydan beri değişmediyse içerik bağı tutar."""
    sector_id = await _sub_sector(pkg_db)
    run_id, package_id = await _yazilmis_ve_onayli(pkg_db, sector_id)

    await writeback.activate_from_snapshot(pkg_db, run_id=run_id, actor=ACTOR)

    satir = await _paket_satiri(pkg_db, package_id)
    assert satir["status"] == "active"
    assert identity.canonical_sha(satir["content"]) == await pkg_db.fetchval(
        "SELECT content_sha FROM social.sector_package_runs WHERE run_id = $1", run_id
    )


async def test_activation_refused_when_draft_content_hash_differs(pkg_db):
    """Onaydan SONRA değiştirilen içerik aktive EDİLEMEZ."""
    sector_id = await _sub_sector(pkg_db)
    run_id, package_id = await _yazilmis_ve_onayli(pkg_db, sector_id)
    await pkg_db.execute(
        "UPDATE social.sector_packages SET content = $2 WHERE id = $1",
        package_id,
        _degistirilmis_icerik(),
    )

    with pytest.raises(writeback.ActivationRefused, match="içeri|content"):
        await writeback.activate_from_snapshot(pkg_db, run_id=run_id, actor=ACTOR)

    assert await _koan(pkg_db, sector_id) == [(1, "draft")]


async def test_activation_refused_when_draft_decision_log_hash_differs(pkg_db):
    """Onaydan SONRA değiştirilen karar günlüğü de aktive EDİLEMEZ."""
    sector_id = await _sub_sector(pkg_db)
    run_id, package_id = await _yazilmis_ve_onayli(pkg_db, sector_id)
    bozuk = _gunluk(_icerik())
    bozuk[0] = {**bozuk[0], "gerekce": "Sonradan değiştirilmiş gerekçe."}
    await pkg_db.execute(
        "UPDATE social.sector_packages SET decision_log = $2 WHERE id = $1",
        package_id,
        bozuk,
    )

    with pytest.raises(writeback.ActivationRefused, match="günlü|decision_log"):
        await writeback.activate_from_snapshot(pkg_db, run_id=run_id, actor=ACTOR)

    assert await _koan(pkg_db, sector_id) == [(1, "draft")]


# ═══ 6. K-94 — TABAN DURUMU açıkça beyan edilir ═════════════════════════════


def _kanit_alanlari(**overrides) -> dict:
    alanlar = dict(
        activation_eligible=True,
        open_questions_count=0,
        katman1_passed=True,
        checklist_approved=True,
        expected_no_active=True,
        run_id="kosu-literal",
        provenance_token="0" * 64,
    )
    alanlar.update(overrides)
    return alanlar


@pytest.mark.parametrize(
    "taban",
    [
        {"expected_no_active": True, "expected_active_version": 3},
        {"expected_no_active": False, "expected_active_version": None},
    ],
    ids=["ikisi_birden", "hicbiri"],
)
def test_evidence_base_state_requires_exactly_one(taban):
    """K-94 TABAN DURUMU — DOĞRUDAN ölçüm, aktivasyon yoluyla İKAME EDİLMEZ.

    "İkisi birden ya da hiçbiri" bir YAPIM hatasıdır ve kapısı sınıfın kendi
    `__post_init__`'indedir. Bu iddiayı aktivasyon-yolu testlerine yıkmak
    yanlış olurdu: o testler yalnız fabrikanın ÜRETTİĞİ kombinasyonları görür,
    yani elle kurulan geçersiz kombinasyon hiç ölçülmemiş olurdu.
    """
    with pytest.raises(ValueError, match="taban|expected"):
        ActivationGateEvidence(**_kanit_alanlari(**taban))


def test_evidence_base_state_accepts_exactly_one():
    """POZİTİF KONTROL: iki meşru taban durumunun ikisi de kurulur."""
    ilk = ActivationGateEvidence(**_kanit_alanlari())
    devir = ActivationGateEvidence(
        **_kanit_alanlari(expected_no_active=False, expected_active_version=3)
    )
    assert ilk.expected_no_active is True and ilk.expected_active_version is None
    assert devir.expected_no_active is False and devir.expected_active_version == 3


async def test_first_activation_uses_expected_no_active(pkg_db):
    """K-94 ilk aktivasyon: aktif satır yokken kanıt `expected_no_active` taşır."""
    sector_id = await _sub_sector(pkg_db)
    run_id, _ = await _yazilmis_ve_onayli(pkg_db, sector_id)

    async with pkg_db.transaction():
        kanit = await writeback.build_activation_evidence(pkg_db, run_id=run_id)

    assert kanit.expected_no_active is True
    assert kanit.expected_active_version is None


async def test_expected_no_active_rejected_when_active_row_exists(pkg_db):
    """Kanıt basıldıktan SONRA aktif satır doğduysa geçiş REDDEDİLİR."""
    sector_id = await _sub_sector(pkg_db)
    run_id, _ = await _yazilmis_ve_onayli(pkg_db, sector_id)

    async with pkg_db.transaction():
        kanit = await writeback.build_activation_evidence(pkg_db, run_id=run_id)
    assert kanit.expected_no_active is True

    await pkg_db.execute(
        "INSERT INTO social.sector_packages "
        "(sector_id, version, status, schema_version, content) "
        "VALUES ($1, 9, 'active', 1, $2)",
        sector_id,
        _icerik(),
    )
    hedef = await pkg_db.fetchval(
        "SELECT id FROM social.sector_packages WHERE run_id = $1", run_id
    )

    with pytest.raises(GateNotSatisfied, match="expected_no_active"):
        await lifecycle.activate_package(
            pkg_db, package_id=hedef, evidence=kanit, actor=ACTOR
        )


async def test_version_mismatch_rejects_activation(pkg_db):
    """K-94 uçtan uca: aktif sürüm onaydan beri değiştiyse geçiş REDDEDİLİR."""
    sector_id = await _sub_sector(pkg_db)
    await pkg_db.execute(
        "INSERT INTO social.sector_packages "
        "(sector_id, version, status, schema_version, content) "
        "VALUES ($1, 1, 'active', 1, $2)",
        sector_id,
        _icerik(),
    )
    run_id, hedef = await _yazilmis_ve_onayli(pkg_db, sector_id)

    async with pkg_db.transaction():
        kanit = await writeback.build_activation_evidence(pkg_db, run_id=run_id)
    assert kanit.expected_active_version == 1 and kanit.expected_no_active is False

    await pkg_db.execute(
        "UPDATE social.sector_packages SET version = 7 "
        "WHERE sector_id = $1 AND status = 'active'",
        sector_id,
    )

    with pytest.raises(GateNotSatisfied, match="expected_active_version"):
        await lifecycle.activate_package(
            pkg_db, package_id=hedef, evidence=kanit, actor=ACTOR
        )


# ═══ 7. R8(c) — KÖKEN JETONU: kapı kabul fonksiyonunun içinde ══════════════


def test_token_table_mapping_matches_the_minting_side():
    """Tüketim tarafının tablo eşlemesi, BASIM tarafının kapalı kümesiyle aynı.

    İki taraf ayrışırsa jeton bir tabloya basılıp başka bir tabloda aranır ve
    kapı sessizce hiçbir şeyi doğrulamaz hâle gelirdi.
    """
    assert set(lifecycle._JETON_TABLOSU) == {
        ActivationGateEvidence,
        RollbackGateEvidence,
    }
    assert set(lifecycle._JETON_TABLOSU.values()) == set(runs.JETON_TABLOLARI)


def test_evidence_is_constructed_only_inside_the_writeback_factory():
    """YAPISAL: `ActivationGateEvidence(` writeback'te YALNIZ fabrikada geçer."""
    assert WRITEBACK_KAYNAK.count("ActivationGateEvidence(") == 1
    govde = inspect.getsource(writeback.build_activation_evidence)
    assert "ActivationGateEvidence(" in govde

    imza = inspect.signature(writeback.activate_from_snapshot)
    assert set(imza.parameters) == {"db", "run_id", "actor"}


async def test_literal_evidence_refused_by_activation(pkg_db):
    """ASIL KAPI: elle kurulan kanıt geçiş YAPAMAZ (arayüz eki R8(c)).

    Sınıfın kurulumu engellenemez — `frozen=True` bir dataclass herkese açıktır.
    Engellenen şey KABULDÜR: jeton veritabanı destekli bir fabrikadan gelmediği
    için kilitli satırda karşılığı yoktur.
    """
    sector_id = await _sub_sector(pkg_db)
    run_id, hedef = await _yazilmis_ve_onayli(pkg_db, sector_id)
    sahte = ActivationGateEvidence(**_kanit_alanlari(run_id=run_id))

    with pytest.raises(EvidenceProvenanceInvalid):
        await lifecycle.activate_package(
            pkg_db, package_id=hedef, evidence=sahte, actor=ACTOR
        )

    assert await _koan(pkg_db, sector_id) == [(1, "draft")]


async def test_rollback_refuses_literal_evidence(pkg_db):
    """Aynı kapı geri alma yolunda da durur — tek taraflı sertleştirme YOK."""
    sahte = RollbackGateEvidence(
        manager_approved=True,
        katman1_passed=True,
        incident_id="olay-literal",
        package_id=uuid.UUID(int=7),
        onay_kapsam_sha="b" * 64,
        provenance_token="0" * 64,
    )

    with pytest.raises(EvidenceProvenanceInvalid):
        await lifecycle.rollback_package(
            pkg_db,
            sector_id=uuid.UUID(int=8),
            to_version=1,
            evidence=sahte,
            actor=ACTOR,
        )


async def test_tampered_evidence_field_is_refused(pkg_db):
    """Gerçek jeton + DEĞİŞTİRİLMİŞ alan = RED: parmak izi alanları mühürler."""
    import dataclasses

    sector_id = await _sub_sector(pkg_db)
    run_id, hedef = await _yazilmis_ve_onayli(pkg_db, sector_id)
    async with pkg_db.transaction():
        gercek = await writeback.build_activation_evidence(pkg_db, run_id=run_id)

    bozuk = dataclasses.replace(
        gercek, expected_no_active=False, expected_active_version=5
    )
    assert bozuk.provenance_token == gercek.provenance_token

    with pytest.raises(EvidenceProvenanceInvalid):
        await lifecycle.activate_package(
            pkg_db, package_id=hedef, evidence=bozuk, actor=ACTOR
        )


async def test_provenance_token_is_single_use(pkg_db):
    """Jeton TEK KULLANIMLIKTIR — harcanmış kanıt ikinci geçişi açamaz."""
    sector_id = await _sub_sector(pkg_db)
    run_id, hedef = await _yazilmis_ve_onayli(pkg_db, sector_id)
    async with pkg_db.transaction():
        kanit = await writeback.build_activation_evidence(pkg_db, run_id=run_id)

    await lifecycle.activate_package(
        pkg_db, package_id=hedef, evidence=kanit, actor=ACTOR
    )
    # Satırı taslağa geri çekmek jetonu GERİ GETİRMEZ: harcanma kaydı koşu
    # satırındadır, paket satırında değil.
    await pkg_db.execute(
        "UPDATE social.sector_packages SET status = 'draft' WHERE id = $1", hedef
    )

    with pytest.raises(EvidenceProvenanceInvalid):
        await lifecycle.activate_package(
            pkg_db, package_id=hedef, evidence=kanit, actor=ACTOR
        )


async def test_update_invalidates_previous_snapshot(pkg_db):
    """Yerinde güncelleme BEKLEYEN kanıtı geçersizler — bayat kanıtla aktivasyon yok.

    İki bağımsız kapı bu senaryoyu kapatır ve biri diğerinin yerine GEÇMEZ:
    burada ölçülen JETON ayağıdır (güncelleme bekleyen jetonu yakar); içerik
    hash'i ayağı `test_activation_refused_when_draft_content_hash_differs`te
    ayrıca ölçülür.
    """
    sector_id = await _sub_sector(pkg_db)
    ana_run_id = await _kosu(pkg_db, sector_id)
    package_id = await writeback.write_draft_from_run(
        pkg_db, run_id=ana_run_id, actor=ACTOR
    )
    await _onayli(pkg_db, ana_run_id, karar="ret")

    ilk_duzeltme = await runs.open_correction_run(
        pkg_db, parent_run_id=ana_run_id, actor=ACTOR
    )
    await runs.record_result(
        pkg_db, run_id=ilk_duzeltme, result=_sonuc(content=_degistirilmis_icerik())
    )
    await runs.attest_katman1(
        pkg_db, run_id=ilk_duzeltme, kosum_kimligi="k1-2", sonuc="PASS", actor=ACTOR
    )
    await runs.attest_katman2(
        pkg_db, run_id=ilk_duzeltme, kosum_kimligi="k2-2", ozet="tur", actor=ACTOR
    )
    await _hazirlik_tasdiki(pkg_db, ilk_duzeltme)
    await writeback.update_draft_from_run(pkg_db, run_id=ilk_duzeltme, actor=ACTOR)
    await _onayli(pkg_db, ilk_duzeltme)

    async with pkg_db.transaction():
        bekleyen = await writeback.build_activation_evidence(
            pkg_db, run_id=ilk_duzeltme
        )

    ikinci_duzeltme = await runs.open_correction_run(
        pkg_db, parent_run_id=ana_run_id, actor=ACTOR
    )
    ikinci_icerik = _icerik(kapsam="Kuyumculuk: yalnız gümüş takı perakendesi.")
    await runs.record_result(
        pkg_db, run_id=ikinci_duzeltme, result=_sonuc(content=ikinci_icerik)
    )
    await runs.attest_katman1(
        pkg_db, run_id=ikinci_duzeltme, kosum_kimligi="k1-3", sonuc="PASS", actor=ACTOR
    )
    await runs.attest_katman2(
        pkg_db, run_id=ikinci_duzeltme, kosum_kimligi="k2-3", ozet="tur", actor=ACTOR
    )
    await _hazirlik_tasdiki(pkg_db, ikinci_duzeltme)

    await writeback.update_draft_from_run(pkg_db, run_id=ikinci_duzeltme, actor=ACTOR)

    with pytest.raises(EvidenceProvenanceInvalid):
        await lifecycle.activate_package(
            pkg_db, package_id=package_id, evidence=bekleyen, actor=ACTOR
        )
    assert await _koan(pkg_db, sector_id) == [(1, "draft")]


# ═══ 8. Yarışlar — güncelleme ile aktivasyon TEK kazanan bırakır ════════════


async def _duzeltme_zinciri_committed(setup, sector_id):
    """Committed evrende: ret'lenmiş ana + onaylı düzeltme + ikinci açık düzeltme.

    Dönen: `(package_id, onayli_duzeltme, ikinci_duzeltme)`.
    """
    ana = await _kosu(setup, sector_id)
    package_id = await writeback.write_draft_from_run(setup, run_id=ana, actor=ACTOR)
    await _onayli(setup, ana, karar="ret")

    onayli = await runs.open_correction_run(setup, parent_run_id=ana, actor=ACTOR)
    await runs.record_result(
        setup, run_id=onayli, result=_sonuc(content=_degistirilmis_icerik())
    )
    await runs.attest_katman1(
        setup, run_id=onayli, kosum_kimligi="k1-2", sonuc="PASS", actor=ACTOR
    )
    await runs.attest_katman2(
        setup, run_id=onayli, kosum_kimligi="k2-2", ozet="tur", actor=ACTOR
    )
    await _hazirlik_tasdiki(setup, onayli)
    await writeback.update_draft_from_run(setup, run_id=onayli, actor=ACTOR)
    await _onayli(setup, onayli)

    ikinci = await runs.open_correction_run(setup, parent_run_id=ana, actor=ACTOR)
    ikinci_icerik = _icerik(kapsam="Kuyumculuk: yalnız gümüş takı perakendesi.")
    await runs.record_result(
        setup, run_id=ikinci, result=_sonuc(content=ikinci_icerik)
    )
    await runs.attest_katman1(
        setup, run_id=ikinci, kosum_kimligi="k1-3", sonuc="PASS", actor=ACTOR
    )
    await runs.attest_katman2(
        setup, run_id=ikinci, kosum_kimligi="k2-3", ozet="tur", actor=ACTOR
    )
    await _hazirlik_tasdiki(setup, ikinci)
    return package_id, onayli, ikinci


def _sonuclari_oku(sonuclar) -> list[str]:
    return ["ok" if s is None else s for s in sonuclar]


async def test_concurrent_update_and_activation_single_winner(test_db_setup):
    """Yerinde güncelleme ile aktivasyon aynı anda koşamaz — TEK kazanan."""
    async with _committed_ortam(test_db_setup) as (url, setup, sector_id):
        package_id, onayli, ikinci = await _duzeltme_zinciri_committed(
            setup, sector_id
        )

        async def _guncelle(conn):
            try:
                await writeback.update_draft_from_run(
                    conn, run_id=ikinci, actor=ACTOR
                )
                return None
            except Exception as exc:
                return type(exc).__name__

        async def _aktive(conn):
            try:
                await writeback.activate_from_snapshot(
                    conn, run_id=onayli, actor=ACTOR
                )
                return None
            except Exception as exc:
                return type(exc).__name__

        async with _isciler(url) as (bir, iki):
            sonuclar = _sonuclari_oku(
                await asyncio.gather(_guncelle(bir), _aktive(iki))
            )

        assert sonuclar.count("ok") >= 1, f"iki taraf da düştü: {sonuclar}"
        durum = await setup.fetchval(
            "SELECT status FROM social.sector_packages WHERE id = $1", package_id
        )
        if sonuclar[1] == "ok":
            assert durum == "active"
        else:
            assert durum == "draft", "aktivasyon düştüyse satır taslak KALMALI"


async def test_correction_vs_stale_activation_single_winner(test_db_setup):
    """BAYAT kanıtla aktivasyon, düzeltmeyle yarışırsa kazanamaz.

    Bir önceki testten farkı kanıtın YAŞIDIR: burada jeton güncellemeden ÖNCE
    basılır ve ham yaşam döngüsü sınırına verilir — yani `activate_from_snapshot`
    içindeki taze kapılar devrede DEĞİLDİR. Kalan tek savunma köken jetonudur.
    """
    async with _committed_ortam(test_db_setup) as (url, setup, sector_id):
        package_id, onayli, ikinci = await _duzeltme_zinciri_committed(
            setup, sector_id
        )
        async with setup.transaction():
            bayat = await writeback.build_activation_evidence(setup, run_id=onayli)

        async def _guncelle(conn):
            try:
                await writeback.update_draft_from_run(
                    conn, run_id=ikinci, actor=ACTOR
                )
                return None
            except Exception as exc:
                return type(exc).__name__

        async def _aktive(conn):
            try:
                await lifecycle.activate_package(
                    conn, package_id=package_id, evidence=bayat, actor=ACTOR
                )
                return None
            except Exception as exc:
                return type(exc).__name__

        async with _isciler(url) as (bir, iki):
            sonuclar = _sonuclari_oku(
                await asyncio.gather(_guncelle(bir), _aktive(iki))
            )

        assert sonuclar.count("ok") >= 1, f"iki taraf da düştü: {sonuclar}"
        olaylar = await setup.fetch(
            "SELECT event_type FROM social.package_events "
            "WHERE sector_id = $1 AND event_type = 'activation'",
            sector_id,
        )
        assert len(olaylar) <= 1, "iki aktivasyon olayı yazılamaz"
        if sonuclar[0] == "ok":
            assert sonuclar[1] != "ok", "güncelleme kazandıysa bayat kanıt geçmemeli"


async def test_update_path_applies_the_same_content_gate(pkg_db):
    """Yerinde güncelleme, ilk yazımın REDDEDECEĞİ içeriği kalıcı KILAMAZ.

    K-135 "tek yazma yüzeyi" ancak kapı da tekse anlamlıdır: yedi kapı
    (`load_verified_run`) içerik↔günlük çifti bütünlüğünü ÖLÇMEZ — hash'lerin
    kendi değerleriyle tutarlı olmasına bakar. Yani yalnız yedi kapıya
    yaslanan bir güncelleme yolu, hayalet birim taşıyan bir çifti taslağa
    yazabilirdi.
    """
    sector_id = await _sub_sector(pkg_db)
    ana_run_id = await _kosu(pkg_db, sector_id)
    package_id = await writeback.write_draft_from_run(
        pkg_db, run_id=ana_run_id, actor=ACTOR
    )
    onceki = await _paket_satiri(pkg_db, package_id)
    await _onayli(pkg_db, ana_run_id, karar="ret")

    duzeltme = await runs.open_correction_run(
        pkg_db, parent_run_id=ana_run_id, actor=ACTOR
    )
    yeni_icerik = _degistirilmis_icerik()
    hayaletli = _gunluk(yeni_icerik) + [
        {
            "tur": "karar",
            "alan": "kanca_kaliplari",
            "oge_yolu": "kanca_kaliplari[7]",
            "unit_id": "ku-ffffffffffff",
            "oge_sha": "a" * 64,
            "karar": "koru",
            "gerekce": "İçerikte karşılığı OLMAYAN hayalet birim.",
            "kanit": "",
            "aktor": "motor",
            "kural_kimligi": "kural-koru",
            "kural_surumu": "v1",
        }
    ]
    await runs.record_result(
        pkg_db,
        run_id=duzeltme,
        result=_sonuc(content=yeni_icerik, gunluk=hayaletli),
    )
    await runs.attest_katman1(
        pkg_db, run_id=duzeltme, kosum_kimligi="k1-2", sonuc="PASS", actor=ACTOR
    )

    with pytest.raises(ValueError, match="içerik ile karar günlüğü tutarsız"):
        await writeback.update_draft_from_run(pkg_db, run_id=duzeltme, actor=ACTOR)

    sonraki = await _paket_satiri(pkg_db, package_id)
    assert sonraki["content"] == onceki["content"], "reddedilen çift YAZILDI"


async def test_activation_refused_when_snapshot_was_never_frozen(pkg_db):
    """Görüntü hiç DONDURULMAMIŞSA operatöre söylenen şey "ekran yok"tur.

    Bu test kapının VARLIĞINI değil SIRASINI ölçer ve bu bilinçlidir: görüntü de
    karar da yokken iki kapı da düşer, ama operatöre önce hangisinin söylendiği
    onu doğru yere gönderir. Görüntü kapısı kaldırılırsa mesaj "karar"a döner ve
    operatör var olmayan bir kararı aramaya başlar.
    """
    sector_id = await _sub_sector(pkg_db)
    run_id = await _kosu(pkg_db, sector_id)
    await writeback.write_draft_from_run(pkg_db, run_id=run_id, actor=ACTOR)

    with pytest.raises(writeback.ActivationRefused, match="GÖRÜNTÜ YOK"):
        await writeback.activate_from_snapshot(pkg_db, run_id=run_id, actor=ACTOR)

    assert await _koan(pkg_db, sector_id) == [(1, "draft")]


async def test_in_place_update_rewrites_content_and_log_together(pkg_db):
    """Yol sıra numaraları KONUMSALDIR — güncelleme ikisini BİRLİKTE yazar.

    `oge_yolu` değerleri (`kanca_kaliplari[0]` gibi) konumsaldır: bir öğe
    çıkarılınca sonraki öğelerin yolları KAYAR. Yerinde güncelleme tam olarak
    bu kaymayı üreten işlemdir, o yüzden tehlike buradadır: içerik yazılıp
    günlük eski yollarıyla bırakılsaydı, karar günlüğü var olmayan konumlara
    işaret ederdi ve kimlik zinciri sessizce kopardı.

    Ölçülen POZİTİF sözleşme: güncellemeden sonra içerik ile günlük BİRLİKTE
    tutarlıdır — her yaşayan satırın yolu içerikte VARDIR ve `unit_id` eşlemesi
    korunur. Depoda yolları SÜRÜMLER ARASI karşılaştıran bir tüketici yoktur;
    sektörün turlar arası tek çapraz tüketicisi (`approval._son_dort_tur`)
    çıkarma SAYAR, yol EŞLEŞTİRMEZ.
    """
    sector_id = await _sub_sector(pkg_db)
    iki_kancali = _icerik()
    iki_kancali["kanca_kaliplari"] = [
        "Sertifikayı okumayı biliyor musunuz?",
        *iki_kancali["kanca_kaliplari"],
    ]
    ana_run_id = await _kosu(pkg_db, sector_id, content=iki_kancali)
    package_id = await writeback.write_draft_from_run(
        pkg_db, run_id=ana_run_id, actor=ACTOR
    )
    onceki = await _paket_satiri(pkg_db, package_id)
    onceki_yollar = [s["oge_yolu"] for s in onceki["decision_log"]]
    await _onayli(pkg_db, ana_run_id, karar="ret")

    # İLK kanca kalıbı ÇIKARILIR → sonraki kalıbın yolu [1]'den [0]'a KAYAR.
    kisaltilmis = dict(iki_kancali)
    kisaltilmis["kanca_kaliplari"] = iki_kancali["kanca_kaliplari"][1:]

    duzeltme = await runs.open_correction_run(
        pkg_db, parent_run_id=ana_run_id, actor=ACTOR
    )
    await runs.record_result(
        pkg_db, run_id=duzeltme, result=_sonuc(content=kisaltilmis)
    )
    await runs.attest_katman1(
        pkg_db, run_id=duzeltme, kosum_kimligi="k1-2", sonuc="PASS", actor=ACTOR
    )

    await writeback.update_draft_from_run(pkg_db, run_id=duzeltme, actor=ACTOR)

    sonraki = await _paket_satiri(pkg_db, package_id)
    sonraki_yollar = [s["oge_yolu"] for s in sonraki["decision_log"]]
    assert sonraki_yollar != onceki_yollar, "kayma hiç olmadı — test bir şey ölçmüyor"
    # ASIL SÖZLEŞME: yazılan çift KENDİ İÇİNDE tutarlı; bayat yol KALMADI.
    assert identity.check_unit_integrity(
        sonraki["content"], [dict(s) for s in sonraki["decision_log"]]
    ) == []
