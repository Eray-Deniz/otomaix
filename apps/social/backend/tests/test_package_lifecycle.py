"""Paket yaşam döngüsü servis fonksiyonları (plan Task 13).

Dört sözleşme burada pinlenir:

1. **Kanıtsız geçiş YOLU YOKTUR.** Ham iki-adım geçişi özeldir
   (`_apply_status_transition`); public yüzeyden geçmenin tek yolu kendi kapı
   kanıtını taşımaktır. Aktivasyon `ActivationGateEvidence`, rollback AYRI bir
   `RollbackGateEvidence` ister — ikisi PAYLAŞILMAZ, çünkü acil rollback adayın
   aktivasyon kapılarından bağımsızdır.
2. **Geçiş + olay ATOMİKTİR (F24).** Olay yazımı ile durum geçişi aynı
   transaction'dadır: olaysız geçiş de geçişsiz olay da mümkün değildir.
   Altyapı hatası bu yüzeyde YUTULMAZ — çalışma zamanı yollarının aksine
   (`_record_event`), yaşam döngüsünde yarım bir denetim izi geçişin kendisini
   geçersiz kılar.
3. **Sıra sözleşmesi: olay ÖNCE, geçiş SONRA.** `log_package_event`'in
   "bu bir devir teslim mi" ölçüsü tablodan okunur ve o ölçü YALNIZ geçiş
   uygulanmadan önce doğrudur (aşağıdaki deaktivasyon-sonrası aktivasyon
   testi bu sırayı bağlar).
4. **Yazım kapısı `insert_draft`'ın arkasındadır.** Doğrulayıcı girdilerini
   (sistem takvimi, mevcut marka adları) çağırandan değil DB'den alır; kapı
   geçmeden satır yazılmaz.
"""

from __future__ import annotations

import logging
import uuid

import pytest

from app.core.database import _init_connection
from app.services import sector_package_lifecycle
from app.services.sector_package_lifecycle import (
    ActivationGateEvidence,
    GateNotSatisfied,
    LifecycleError,
    RollbackGateEvidence,
    activate_package,
    deactivate_package,
    insert_draft,
    rollback_package,
)

from .test_sector_packages_service import _valid_content  # noqa: E402
from .test_unit_identity import _karar_row  # noqa: E402

ACTOR = "admin@otomaix"


# ─── Ortak seed ─────────────────────────────────────────────────────────────


@pytest.fixture
async def pkg_db(db):
    """Üretimin KENDİ bağlantı yapılandırması + takvim kapısının besini.

    `_valid_content()` bir `ozel_gun` anahtarı taşır ve yazım kapısı o anahtarı
    SİSTEM TAKVİMİNE karşı doğrular. Anahtarı sabitlemek yerine takvime bir
    satır eklemek, kapının gerçekten tablodan beslendiğini de gösterir.
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


async def _seed_package(db, sector_id, *, version: int, status: str) -> uuid.UUID:
    """Kurulum satırı — yazım kapısını ATLAR (kapı kendi testinde ölçülür)."""
    return await db.fetchval(
        "INSERT INTO social.sector_packages "
        "(sector_id, version, status, schema_version, content) "
        "VALUES ($1, $2, $3, 1, $4) RETURNING id",
        sector_id,
        version,
        status,
        _valid_content(),
    )


async def _status(db, package_id) -> str:
    return await db.fetchval(
        "SELECT status FROM social.sector_packages WHERE id = $1", package_id
    )


async def _events(db, sector_id) -> list:
    return await db.fetch(
        "SELECT event_type, from_version, to_version, actor "
        "FROM social.package_events WHERE sector_id = $1 ORDER BY created_at, event_type",
        sector_id,
    )


class _EventTail:
    """Her adımdan sonra YENİ eklenen olayları döner.

    Neden `created_at` sıralaması değil: `now()` transaction başlangıcını
    verir ve testin tamamı tek dış transaction'da koştuğu için bütün satırlar
    AYNI damgayı taşır — sıralama iddiası orada hiçbir şey ölçmez (ölçüldü).
    Kimliğe göre delta almak sıralamadan bağımsız ve kesindir.
    """

    def __init__(self):
        self.seen: set = set()

    async def new(self, db, sector_id) -> list[tuple]:
        rows = await db.fetch(
            "SELECT id, event_type, from_version, to_version, actor "
            "FROM social.package_events WHERE sector_id = $1",
            sector_id,
        )
        fresh = [row for row in rows if row["id"] not in self.seen]
        self.seen.update(row["id"] for row in rows)
        return [
            (r["event_type"], r["from_version"], r["to_version"], r["actor"]) for r in fresh
        ]


# ── KÖKEN ALANLARI (Plan 2 Task 8, arayüz eki R8(c)) ────────────────────────
#
# İki kanıt sınıfı da artık ZORUNLU köken alanları taşır. Bu dosyadaki kurulum
# hâlâ LİTERALDİR ve bu bilinçlidir: jetonun TÜKETİMİ (`_consume_provenance`)
# Task 15'in kalemidir, bugün hiçbir geçiş jetonu doğrulamaz. Task 15 bu iki
# yardımcıyı veritabanı destekli FABRİKAYA çevirir (planın Task 15 kaleminde
# adıyla yazılı) ve o gün literal kurulan kanıt her iki geçişte de REDDEDİLİR.
# Bugün eklenen tek şey ŞEKİL kapısıdır — 64 hex jeton, boş olmayan kimlik.
_JETON = "0" * 64
_KAPSAM_SHA = "a" * 64

_ACTIVATION_DEFAULTS = dict(
    activation_eligible=True,
    open_questions_count=0,
    katman1_passed=True,
    checklist_approved=True,
    run_id="kosu-plan1-testi",
    provenance_token=_JETON,
)

_ROLLBACK_DEFAULTS = dict(
    manager_approved=True,
    katman1_passed=True,
    incident_id="olay-plan1-testi",
    package_id=uuid.UUID(int=1),
    onay_kapsam_sha=_KAPSAM_SHA,
    provenance_token=_JETON,
)


def _activation_evidence(**overrides) -> ActivationGateEvidence:
    """Kanıt NESNESİ — henüz MÜHÜRLENMEMİŞ (kökeni yok).

    K-94 taban durumu (Plan 2 Task 15) iki alandan tam olarak birini ister.
    Çağıran `expected_active_version` verdiyse taban "devir teslim"dir; hiç
    vermediyse "ilk aktivasyon". Kural burada TÜRETİLİR ki her çağrı yerine
    ikinci bir alan eklemek gerekmesin — ama TÜRETME de açıkça yazılıdır:
    sessiz varsayılan, K-94'ün kapatmak için var olduğu belirsizliğin ta
    kendisiydi.
    """
    fields = dict(_ACTIVATION_DEFAULTS)
    fields.update(overrides)
    if "expected_no_active" not in overrides:
        fields["expected_no_active"] = fields.get("expected_active_version") is None
    return ActivationGateEvidence(**fields)


def _rollback_evidence(**overrides) -> RollbackGateEvidence:
    fields = dict(_ROLLBACK_DEFAULTS)
    fields.update(overrides)
    return RollbackGateEvidence(**fields)


# ── KÖKEN MÜHRÜ (Plan 2 Task 15, arayüz eki R8(c)) ──────────────────────────
#
# Kanıt sınıfları artık TEK KULLANIMLIK bir köken jetonu taşır ve geçiş
# fonksiyonları o jetonu KİLİTLİ satıra karşı doğrulayıp HARCAR. Literal kanıt
# artık hiçbir geçişten geçmez — yani bu dosyanın başarı yollarının kanıtı
# satırda karşılığı OLAN bir jeton taşımak zorundadır.
#
# **Bu yardımcı Plan 2'nin fabrikasını TAKLİT eder, onu ÇAĞIRMAZ ve bu bilinçli
# bir sınırdır (İlke 3).** Fabrikanın kendisi (`writeback.build_activation_evidence`
# → `runs.mint_evidence_token`) tam bir doğrulanmış koşu zinciri ister; bu
# dosyanın konusu ise GEÇİŞİN kendisidir, fabrikanın değil. Fabrika ↔ tüketim
# gidiş-dönüşü `tests/test_pipeline_writeback.py`'de GERÇEK jetonla ölçülür
# (`test_tampered_evidence_field_is_refused` · `test_provenance_token_is_single_use`
# · `test_literal_evidence_refused_by_activation`). Burada ölçülen şey "mühürlü
# kanıt geçer, mühürsüz geçmez"dir.


async def _muhurle_aktivasyon(conn, evidence, *, sector_id) -> None:
    await conn.execute(
        "INSERT INTO social.sector_package_runs "
        "(run_id, sector_id, durum, kosu_turu, kanit_jetonu, "
        " kanit_jetonu_parmakizi, kanit_jetonu_basildi_at) "
        "VALUES ($1, $2, 'calisiyor', 'ilk', $3, $4, now()) "
        "ON CONFLICT (run_id) DO UPDATE SET "
        "  kanit_jetonu = EXCLUDED.kanit_jetonu, "
        "  kanit_jetonu_parmakizi = EXCLUDED.kanit_jetonu_parmakizi, "
        "  kanit_jetonu_basildi_at = now(), "
        "  kanit_jetonu_harcandi_at = NULL",
        evidence.run_id,
        sector_id,
        evidence.provenance_token,
        sector_package_lifecycle._evidence_fingerprint(evidence),
    )


async def _muhurle_rollback(conn, evidence, *, observed_version: int = 1) -> None:
    await conn.execute(
        "INSERT INTO social.package_rollback_plans "
        "(incident_id, package_id, observed_active_version, target_version, "
        " evidence_class, reason, durum, kanit_jetonu, kanit_jetonu_parmakizi, "
        " kanit_jetonu_basildi_at) "
        "VALUES ($1, $2, $3, 1, 'kanitli', 'test', 'bekliyor', $4, $5, now()) "
        "ON CONFLICT (incident_id, package_id) DO UPDATE SET "
        "  kanit_jetonu = EXCLUDED.kanit_jetonu, "
        "  kanit_jetonu_parmakizi = EXCLUDED.kanit_jetonu_parmakizi, "
        "  kanit_jetonu_basildi_at = now(), "
        "  kanit_jetonu_harcandi_at = NULL",
        evidence.incident_id,
        evidence.package_id,
        observed_version,
        evidence.provenance_token,
        sector_package_lifecycle._evidence_fingerprint(evidence),
    )


async def _kanit(conn, sector_id, **overrides) -> ActivationGateEvidence:
    """MÜHÜRLÜ aktivasyon kanıtı — geçişten geçebilen tek biçim."""
    evidence = _activation_evidence(**overrides)
    await _muhurle_aktivasyon(conn, evidence, sector_id=sector_id)
    return evidence


async def _geri_alma_kaniti(conn, **overrides) -> RollbackGateEvidence:
    """MÜHÜRLÜ geri alma kanıtı."""
    evidence = _rollback_evidence(**overrides)
    await _muhurle_rollback(conn, evidence)
    return evidence


# ═══ 1. Draft yazımı ════════════════════════════════════════════════════════


async def test_insert_draft_requires_valid_content(pkg_db):
    """Doğrulayıcı GEÇMEDEN satır yazılmaz (spec §3.6)."""
    sector_id = await _sub_sector(pkg_db)
    broken = _valid_content()
    del broken["kapsam"]

    with pytest.raises(ValueError):
        await insert_draft(
            pkg_db, sector_id=sector_id, content=broken, schema_version=1, actor=ACTOR
        )

    assert (
        await pkg_db.fetchval(
            "SELECT count(*) FROM social.sector_packages WHERE sector_id = $1", sector_id
        )
        == 0
    ), "kapı düşerken satır yazıldı"


async def test_insert_draft_sources_validator_inputs_from_db(pkg_db):
    """Doğrulayıcı girdileri ÇAĞIRANDAN değil DB'den gelir.

    Marka adı yasağı (K-15) yalnız çağıran doğru listeyi verirse çalışıyorsa
    kapı değil, nezaket kuralıdır. Kayıtlı bir marka adının pakete sızması bu
    yüzden çağırandan bağımsız reddedilmeli.
    """
    sector_id = await _sub_sector(pkg_db)
    workspace_id = await pkg_db.fetchval(
        "INSERT INTO social.workspaces (name) VALUES ('Test WS') RETURNING id"
    )
    await pkg_db.execute(
        "INSERT INTO social.brands (workspace_id, name) VALUES ($1, $2)",
        workspace_id,
        "Zarelfa",
    )

    content = _valid_content(kapsam="Zarelfa mağazalarında altın perakendesi.")
    with pytest.raises(ValueError, match="Zarelfa"):
        await insert_draft(
            pkg_db, sector_id=sector_id, content=content, schema_version=1, actor=ACTOR
        )


async def test_insert_draft_versions_sequentially(pkg_db):
    """`version` = son + 1; ilk satır 1'den başlar."""
    sector_id = await _sub_sector(pkg_db)
    first = await insert_draft(
        pkg_db, sector_id=sector_id, content=_valid_content(), schema_version=1, actor=ACTOR
    )
    second = await insert_draft(
        pkg_db, sector_id=sector_id, content=_valid_content(), schema_version=1, actor=ACTOR
    )

    rows = await pkg_db.fetch(
        "SELECT id, version, status FROM social.sector_packages "
        "WHERE sector_id = $1 ORDER BY version",
        sector_id,
    )
    assert [(r["id"], r["version"], r["status"]) for r in rows] == [
        (first, 1, "draft"),
        (second, 2, "draft"),
    ]


async def test_insert_draft_records_actor(pkg_db):
    """`actor` sessizce DÜŞÜRÜLMEZ — satırın kendi izinde durur."""
    sector_id = await _sub_sector(pkg_db)
    package_id = await insert_draft(
        pkg_db,
        sector_id=sector_id,
        content=_valid_content(),
        schema_version=1,
        run_id="run-42",
        actor=ACTOR,
    )
    row = await pkg_db.fetchrow(
        "SELECT run_id, decision_log FROM social.sector_packages WHERE id = $1", package_id
    )
    assert row["run_id"] == "run-42"
    assert any(
        entry.get("actor") == ACTOR for entry in row["decision_log"]
    ), f"actor izi yok: {row['decision_log']!r}"


async def test_insert_draft_rejects_missing_actor(pkg_db):
    """Kanıtsız yazım gibi, sahipsiz yazım da reddedilir."""
    sector_id = await _sub_sector(pkg_db)
    with pytest.raises(ValueError):
        await insert_draft(
            pkg_db, sector_id=sector_id, content=_valid_content(), schema_version=1, actor=" "
        )


async def test_insert_draft_logs_content_warnings_before_pair_gate(pkg_db, caplog):
    """Reddedilen bir çiftte içeriğin KENDİ uyarıları yine de günlüklenir.

    Sıra sözleşmesi: yazım kapısının uyarıları ÖNCE basılır, içerik↔günlük
    bütünlük kapısı SONRA koşar. Fix turu 1'de bütünlük kapısı uyarı
    döngüsünün ÖNÜNE girmişti ve reddedilen bir çift içeriğin uyarılarını
    sessizce yutuyordu; fix turu 2 sırayı geri aldı ama onu tutan bir test
    YAZILMAMIŞTI — bu test o boşluğu kapatır (fix turu 3, B2).

    Ayırt edici olması için iki koşul AYNI anda kurulur: içerik yazım
    kapısını GEÇER ama boyut hedefi uyarısı üretir, çift ise tutarsızdır ve
    bütünlük kapısı `ValueError` fırlatır. Sıra tersine dönerse uyarı hiç
    basılmaz ve bu test düşer.
    """
    sector_id = await _sub_sector(pkg_db)
    # Boyut hedefi (6000 karakter) UYARI üretir, RED üretmez — yazım kapısı
    # `ok` döner ve akış bütünlük kapısına kadar gelir.
    content = _valid_content(
        kapsam=_valid_content()["kapsam"]
        + " "
        + ("Kuyumcu vitrin dili ayrıntılı anlatım. " * 160)
    )
    # Şemayı GEÇEN ama içerikte karşılığı OLMAYAN tek satır: hayalet birim.
    decision_log = [
        _karar_row(oge_yolu="kanca_kaliplari[7]", unit_id="ku-ffffffffffff")
    ]

    with caplog.at_level(logging.WARNING):
        with pytest.raises(ValueError, match="içerik ile karar günlüğü tutarsız"):
            await insert_draft(
                pkg_db,
                sector_id=sector_id,
                content=content,
                schema_version=1,
                decision_log=decision_log,
                actor=ACTOR,
            )

    assert any(
        "tasarım hedefi aşıldı" in record.getMessage() for record in caplog.records
    ), (
        "reddedilen çiftte içerik uyarısı YUTULDU — bütünlük kapısı uyarı "
        f"döngüsünün önüne geçmiş: {[r.getMessage() for r in caplog.records]!r}"
    )

    assert (
        await pkg_db.fetchval(
            "SELECT count(*) FROM social.sector_packages WHERE sector_id = $1", sector_id
        )
        == 0
    ), "bütünlük kapısı düşerken satır yazıldı"


# ═══ 2. Ham geçişin kapatılması ═════════════════════════════════════════════


async def test_raw_transition_not_publicly_exported():
    """Ham geçiş modül DIŞINA verilmez — public takma ad da yok.

    `__all__` listesine güvenmek yetmez (liste bayatlar). Ölçü doğrudan:
    modülde ham fonksiyonu işaret eden ALTÇİZGİSİZ bir ad var mı?
    """
    raw = sector_package_lifecycle._apply_status_transition
    aliases = [
        name
        for name in dir(sector_package_lifecycle)
        if not name.startswith("_") and getattr(sector_package_lifecycle, name, None) is raw
    ]
    assert aliases == [], f"ham geçiş public adla sızıyor: {aliases}"


# ═══ 3. Aktivasyon kapıları ═════════════════════════════════════════════════


async def test_first_activation_single_step(pkg_db):
    """Sektörün İLK paketi tek adımda aktive olur; arşivlenecek şey yoktur."""
    sector_id = await _sub_sector(pkg_db)
    package_id = await _seed_package(pkg_db, sector_id, version=1, status="draft")

    await activate_package(
        pkg_db, package_id=package_id, evidence=await _kanit(pkg_db, sector_id), actor=ACTOR
    )

    assert await _status(pkg_db, package_id) == "active"
    events = await _events(pkg_db, sector_id)
    assert [(e["event_type"], e["from_version"], e["to_version"]) for e in events] == [
        ("activation", None, 1)
    ]


async def test_activate_archives_previous_then_activates(pkg_db):
    """Devir teslim: önceki arşivlenir, yeni aktive olur — tek geçişte."""
    sector_id = await _sub_sector(pkg_db)
    old_id = await _seed_package(pkg_db, sector_id, version=1, status="active")
    new_id = await _seed_package(pkg_db, sector_id, version=2, status="draft")

    # Devir teslimde taban durumu AÇIKÇA beyan edilir (K-94, Plan 2 Task 15):
    # "ilk aktivasyon" diyen bir kanıt burada geçmez.
    await activate_package(
        pkg_db,
        package_id=new_id,
        evidence=await _kanit(pkg_db, sector_id, expected_active_version=1),
        actor=ACTOR,
    )

    assert await _status(pkg_db, old_id) == "archived"
    assert await _status(pkg_db, new_id) == "active"
    events = await _events(pkg_db, sector_id)
    assert [(e["event_type"], e["from_version"], e["to_version"]) for e in events] == [
        ("activation", 1, 2)
    ]


@pytest.mark.parametrize(
    "override",
    [
        {"activation_eligible": False},
        {"open_questions_count": 1},
        {"katman1_passed": False},
        {"checklist_approved": False},
    ],
    ids=["not_eligible", "open_questions", "failed_katman1", "missing_checklist"],
)
async def test_activate_rejects_unsatisfied_gate(pkg_db, override):
    """Kanıt alanlarından HERHANGİ biri sağlanmazsa geçiş REDDEDİLİR.

    K-71 (açık soru sayısı 0 olmalı) ve K-28'in Plan-1 ayağı bu kapıdadır.
    """
    sector_id = await _sub_sector(pkg_db)
    package_id = await _seed_package(pkg_db, sector_id, version=1, status="draft")

    with pytest.raises(GateNotSatisfied):
        await activate_package(
            pkg_db,
            package_id=package_id,
            evidence=await _kanit(pkg_db, sector_id, **override),
            actor=ACTOR,
        )

    assert await _status(pkg_db, package_id) == "draft"
    assert await _events(pkg_db, sector_id) == []


async def test_activate_rejects_stale_base_version_when_provided(pkg_db):
    """K-94 yeteneği: dolu `expected_active_version` gerçekle eşleşmeli."""
    sector_id = await _sub_sector(pkg_db)
    await _seed_package(pkg_db, sector_id, version=1, status="active")
    new_id = await _seed_package(pkg_db, sector_id, version=2, status="draft")

    with pytest.raises(GateNotSatisfied, match="expected_active_version"):
        await activate_package(
            pkg_db,
            package_id=new_id,
            evidence=await _kanit(pkg_db, sector_id, expected_active_version=99),
            actor=ACTOR,
        )

    assert await _status(pkg_db, new_id) == "draft"


async def test_activate_accepts_matching_base_version(pkg_db):
    """Doğru base-sürüm kanıtı geçişi ENGELLEMEZ (yetenek gerçekten çalışıyor)."""
    sector_id = await _sub_sector(pkg_db)
    await _seed_package(pkg_db, sector_id, version=1, status="active")
    new_id = await _seed_package(pkg_db, sector_id, version=2, status="draft")

    await activate_package(
        pkg_db,
        package_id=new_id,
        evidence=await _kanit(pkg_db, sector_id, expected_active_version=1),
        actor=ACTOR,
    )
    assert await _status(pkg_db, new_id) == "active"


async def test_missing_base_version_is_no_longer_a_bypass(pkg_db):
    """K-94 KAPANDI (Plan 2 Task 15): `None` artık "kontrol yapma" demiyor.

    Bu test bir DAVRANIŞ TERSİNMESİDİR ve bilinçlidir. Önceki hâli
    `test_activate_allows_missing_base_version_while_k94_open` adını taşıyor ve
    `expected_active_version=None`'ın geçişi ENGELLEMEDİĞİNİ ölçüyordu — o
    boşluk K-94'ün açık kalmasının kod karşılığıydı: `None` hem "aktif sürüm
    YOK" hem "kontrol yapma" anlamına geliyordu ve ikincisi kapıyı sessizce
    kapatıyordu. Taban durumu artık AÇIKÇA beyan edilir; "ilk aktivasyon"
    diyen bir kanıt, sektörde aktif sürüm varken geçemez.

    Kanıt MÜHÜRLENİR ki düşen kapının K-94 olduğu kesin olsun — mühürsüz kanıt
    daha erken, köken kapısında düşerdi ve test yanlış şeyi ölçerdi.
    """
    sector_id = await _sub_sector(pkg_db)
    await _seed_package(pkg_db, sector_id, version=1, status="active")
    new_id = await _seed_package(pkg_db, sector_id, version=2, status="draft")
    kanit = await _kanit(pkg_db, sector_id, expected_active_version=None)
    assert kanit.expected_no_active is True

    with pytest.raises(GateNotSatisfied, match="expected_no_active"):
        await activate_package(
            pkg_db, package_id=new_id, evidence=kanit, actor=ACTOR
        )
    assert await _status(pkg_db, new_id) == "draft"


async def test_activate_rejects_non_draft_package(pkg_db):
    """Arşivlenmiş satırı `activate_package` diriltmez — o iş rollback'indir."""
    sector_id = await _sub_sector(pkg_db)
    archived_id = await _seed_package(pkg_db, sector_id, version=1, status="archived")

    with pytest.raises(LifecycleError):
        await activate_package(
            pkg_db, package_id=archived_id, evidence=await _kanit(pkg_db, sector_id), actor=ACTOR
        )
    assert await _status(pkg_db, archived_id) == "archived"


async def test_activate_after_deactivation_has_no_from_version(pkg_db):
    """Deaktivasyon SONRASI aktivasyon bir devir teslim DEĞİLDİR.

    Bu senaryo (acil geri çekme → bakım → yeniden açma) K-38'in doğal
    devamıdır. O anda sektörde arşivlenmiş satır VARDIR ama AKTİF satır
    yoktur; yerine geçilen bir şey olmadığı için `from_version` NULL'dır ve
    olay kaydı bunu reddetmemelidir. Denetim izi burada uydurma bir kaynak
    sürüm taşıyamaz.
    """
    sector_id = await _sub_sector(pkg_db)
    first_id = await _seed_package(pkg_db, sector_id, version=1, status="active")
    second_id = await _seed_package(pkg_db, sector_id, version=2, status="draft")
    tail = _EventTail()

    await deactivate_package(pkg_db, package_id=first_id, actor=ACTOR)
    assert await _status(pkg_db, first_id) == "archived"
    assert await tail.new(pkg_db, sector_id) == [("deactivation", 1, None, ACTOR)]

    await activate_package(
        pkg_db, package_id=second_id, evidence=await _kanit(pkg_db, sector_id), actor=ACTOR
    )

    assert await _status(pkg_db, second_id) == "active"
    assert await tail.new(pkg_db, sector_id) == [("activation", None, 2, ACTOR)]


# ═══ 4. Rollback ════════════════════════════════════════════════════════════


async def test_rollback_restores_previous_version(pkg_db):
    """Rollback: aktif olan arşivlenir, hedef sürüm geri gelir."""
    sector_id = await _sub_sector(pkg_db)
    old_id = await _seed_package(pkg_db, sector_id, version=1, status="archived")
    current_id = await _seed_package(pkg_db, sector_id, version=2, status="active")

    await rollback_package(
        pkg_db,
        sector_id=sector_id,
        to_version=1,
        evidence=await _geri_alma_kaniti(pkg_db),
        actor=ACTOR,
    )

    assert await _status(pkg_db, old_id) == "active"
    assert await _status(pkg_db, current_id) == "archived"
    events = await _events(pkg_db, sector_id)
    assert [(e["event_type"], e["from_version"], e["to_version"]) for e in events] == [
        ("rollback", 2, 1)
    ]


async def test_rollback_rejects_without_manager_approval(pkg_db):
    """Yönetici onayı ZORUNLU (spec §2.3)."""
    sector_id = await _sub_sector(pkg_db)
    await _seed_package(pkg_db, sector_id, version=1, status="archived")
    current_id = await _seed_package(pkg_db, sector_id, version=2, status="active")

    with pytest.raises(GateNotSatisfied, match="manager_approved"):
        await rollback_package(
            pkg_db,
            sector_id=sector_id,
            to_version=1,
            evidence=await _geri_alma_kaniti(pkg_db, manager_approved=False),
            actor=ACTOR,
        )

    assert await _status(pkg_db, current_id) == "active"
    assert await _events(pkg_db, sector_id) == []


async def test_rollback_evidence_is_not_the_activation_evidence():
    """İki kanıt sınıfı PAYLAŞILMAZ; rollback aktivasyon alanlarını İSTEMEZ."""
    rollback_fields = set(RollbackGateEvidence.__dataclass_fields__)
    activation_only = {
        "activation_eligible",
        "open_questions_count",
        "checklist_approved",
        "expected_active_version",
    }
    assert rollback_fields & activation_only == set()
    assert "manager_approved" in rollback_fields
    assert "manager_approved" not in set(ActivationGateEvidence.__dataclass_fields__)


async def test_rollback_allowed_while_candidate_activation_gates_fail(pkg_db):
    """Acil rollback, adayın aktivasyon kapılarından BAĞIMSIZDIR.

    Aktif sürüm ancak "aday yeterli değil" diye kilitlenirse acil kol işe
    yaramaz; rollback yalnız kendi kanıtına bakar.
    """
    sector_id = await _sub_sector(pkg_db)
    old_id = await _seed_package(pkg_db, sector_id, version=1, status="archived")
    current_id = await _seed_package(pkg_db, sector_id, version=2, status="active")
    candidate_id = await _seed_package(pkg_db, sector_id, version=3, status="draft")

    # Aday aktive EDİLEMEZ durumda.
    with pytest.raises(GateNotSatisfied):
        await activate_package(
            pkg_db,
            package_id=candidate_id,
            evidence=await _kanit(pkg_db, sector_id, activation_eligible=False),
            actor=ACTOR,
        )

    # Buna rağmen rollback koşar.
    await rollback_package(
        pkg_db,
        sector_id=sector_id,
        to_version=1,
        evidence=await _geri_alma_kaniti(pkg_db),
        actor=ACTOR,
    )
    assert await _status(pkg_db, old_id) == "active"
    assert await _status(pkg_db, current_id) == "archived"
    assert await _status(pkg_db, candidate_id) == "draft"


@pytest.mark.parametrize("to_version", [3, 2], ids=["draft_target", "already_active_target"])
async def test_rollback_rejects_non_archived_target(pkg_db, to_version):
    """Hedef sürüm ARŞİVLENMİŞ olmalı.

    İki reddedilen şekil: henüz aktive edilmemiş bir taslağa "geri dönmek"
    (v3) ve zaten aktif olan sürüme geri dönmek (v2 — kendi üstüne geçiş).
    İkinci sektörde ikinci bir `active` satır kurulamaz (kısmi benzersiz
    indeks), o yüzden vaka mevcut aktif satır üzerinden koşulur.
    """
    sector_id = await _sub_sector(pkg_db)
    await _seed_package(pkg_db, sector_id, version=1, status="archived")
    current_id = await _seed_package(pkg_db, sector_id, version=2, status="active")
    await _seed_package(pkg_db, sector_id, version=3, status="draft")

    with pytest.raises(LifecycleError):
        await rollback_package(
            pkg_db,
            sector_id=sector_id,
            to_version=to_version,
            evidence=await _geri_alma_kaniti(pkg_db),
            actor=ACTOR,
        )

    assert await _status(pkg_db, current_id) == "active"
    assert await _events(pkg_db, sector_id) == []


async def test_rollback_rejects_nonexistent_target(pkg_db):
    """Var olmayan sürüme rollback edilmez."""
    sector_id = await _sub_sector(pkg_db)
    await _seed_package(pkg_db, sector_id, version=1, status="archived")
    await _seed_package(pkg_db, sector_id, version=2, status="active")

    with pytest.raises(LifecycleError):
        await rollback_package(
            pkg_db,
            sector_id=sector_id,
            to_version=7,
            evidence=await _geri_alma_kaniti(pkg_db),
            actor=ACTOR,
        )


async def test_first_package_rollback_error_points_to_deactivation(pkg_db):
    """Önceki sürüm HİÇ yoksa istenen şey rollback değil deaktivasyondur."""
    sector_id = await _sub_sector(pkg_db)
    only_id = await _seed_package(pkg_db, sector_id, version=1, status="active")

    with pytest.raises(LifecycleError, match="deactivate_package"):
        await rollback_package(
            pkg_db,
            sector_id=sector_id,
            to_version=1,
            evidence=await _geri_alma_kaniti(pkg_db),
            actor=ACTOR,
        )

    assert await _status(pkg_db, only_id) == "active"


# ═══ 5. Deaktivasyon ════════════════════════════════════════════════════════


async def test_deactivate_without_new_version_no_evidence_needed(pkg_db):
    """K-38 acil kol: kanıt İSTEMEZ, olay kaydı ZORUNLUDUR."""
    sector_id = await _sub_sector(pkg_db)
    package_id = await _seed_package(pkg_db, sector_id, version=1, status="active")

    await deactivate_package(pkg_db, package_id=package_id, actor=ACTOR)

    assert await _status(pkg_db, package_id) == "archived"
    events = await _events(pkg_db, sector_id)
    assert [(e["event_type"], e["from_version"], e["to_version"], e["actor"]) for e in events] == [
        ("deactivation", 1, None, ACTOR)
    ]


async def test_deactivate_rejects_non_active_package(pkg_db):
    """Aktif olmayan satır geri çekilemez — çekilecek bir şey yok."""
    sector_id = await _sub_sector(pkg_db)
    draft_id = await _seed_package(pkg_db, sector_id, version=1, status="draft")

    with pytest.raises(LifecycleError):
        await deactivate_package(pkg_db, package_id=draft_id, actor=ACTOR)
    assert await _status(pkg_db, draft_id) == "draft"


# ═══ 6. Geçiş + olay atomikliği (F24) ═══════════════════════════════════════


async def test_lifecycle_events_recorded(pkg_db):
    """Uçtan uca zincir tam bir denetim izi bırakır."""
    sector_id = await _sub_sector(pkg_db)
    tail = _EventTail()

    v1 = await insert_draft(
        pkg_db, sector_id=sector_id, content=_valid_content(), schema_version=1, actor=ACTOR
    )
    await activate_package(pkg_db, package_id=v1, evidence=await _kanit(pkg_db, sector_id), actor=ACTOR)
    assert await tail.new(pkg_db, sector_id) == [("activation", None, 1, ACTOR)]

    v2 = await insert_draft(
        pkg_db, sector_id=sector_id, content=_valid_content(), schema_version=1, actor=ACTOR
    )
    await activate_package(
        pkg_db,
        package_id=v2,
        evidence=await _kanit(pkg_db, sector_id, expected_active_version=1),
        actor=ACTOR,
    )
    assert await tail.new(pkg_db, sector_id) == [("activation", 1, 2, ACTOR)]

    await rollback_package(
        pkg_db, sector_id=sector_id, to_version=1, evidence=await _geri_alma_kaniti(pkg_db), actor=ACTOR
    )
    assert await tail.new(pkg_db, sector_id) == [("rollback", 2, 1, ACTOR)]

    await deactivate_package(pkg_db, package_id=v1, actor=ACTOR)
    assert await tail.new(pkg_db, sector_id) == [("deactivation", 1, None, ACTOR)]

    assert (
        await pkg_db.fetchval(
            "SELECT count(*) FROM social.package_events WHERE sector_id = $1", sector_id
        )
        == 4
    ), "yaşam döngüsü fazladan olay yazdı"


@pytest.mark.parametrize("failure", ["raises", "returns_none"], ids=["exception", "silent_none"])
async def test_event_insert_failure_rolls_back_transition(pkg_db, monkeypatch, failure):
    """Olay yazılamazsa geçiş DE olmaz (F24).

    `returns_none` dalı asıl tehlikeli olandır: `log_package_event` altyapı
    hatasında bilinçle `None` döner ve çalışma zamanı yollarında bu doğrudur.
    Yaşam döngüsünde aynı sessizlik "geçiş oldu ama izi yok" demektir — bu
    yüzden dönüş değeri burada KONTROL EDİLİR.
    """
    sector_id = await _sub_sector(pkg_db)
    package_id = await _seed_package(pkg_db, sector_id, version=1, status="draft")

    async def _broken(*args, **kwargs):
        if failure == "raises":
            raise RuntimeError("olay tablosu erişilemiyor")
        return None

    monkeypatch.setattr(sector_package_lifecycle, "log_package_event", _broken)

    with pytest.raises(Exception):
        await activate_package(
            pkg_db, package_id=package_id, evidence=await _kanit(pkg_db, sector_id), actor=ACTOR
        )

    assert await _status(pkg_db, package_id) == "draft", "olaysız geçiş kaldı"


async def test_transition_failure_leaves_no_event(pkg_db, monkeypatch):
    """Geçiş patlarsa ÖNCE yazılmış olay da geri alınır (F24).

    Olay geçişten ÖNCE yazıldığı için bu test transaction'ın kendisini ölçer:
    sarmalayıcı olmasaydı sahte bir `activation` satırı kalırdı.
    """
    sector_id = await _sub_sector(pkg_db)
    package_id = await _seed_package(pkg_db, sector_id, version=1, status="draft")

    async def _broken(*args, **kwargs):
        raise RuntimeError("durum güncellemesi düştü")

    monkeypatch.setattr(sector_package_lifecycle, "_set_status", _broken)

    with pytest.raises(RuntimeError):
        await activate_package(
            pkg_db, package_id=package_id, evidence=await _kanit(pkg_db, sector_id), actor=ACTOR
        )

    assert await _status(pkg_db, package_id) == "draft"
    assert await _events(pkg_db, sector_id) == [], "geçişsiz olay kaldı"


# ═══ 7. Kanıt sınıflarının çalışma-zamanı zorlaması (checkpoint 13, F1) ═════
#
# Açıklama satırı bir kapı DEĞİLDİR. `activation_eligible: bool` yalnız bir
# not; Python onu zorlamaz. Doğruluk-değeriyle çalışan bir kapı, "false"
# metnini DOĞRU sayar — yani "aktive edilemez" diye işaretlenmiş bir aday
# aktive edilebilirdi. Sayısal alanda ayna vaka: `False == 0` ve `True == 1`.


@pytest.mark.parametrize(
    "override",
    [
        {"activation_eligible": "false"},
        {"katman1_passed": "false"},
        {"checklist_approved": "false"},
        {"activation_eligible": 1},
        {"open_questions_count": False},
        {"open_questions_count": "0"},
        {"open_questions_count": -1},
        {"expected_active_version": True},
        {"expected_active_version": "1"},
        {"expected_active_version": 0},
        # Plan 2 Task 8 — köken alanlarının şekil kapıları.
        {"run_id": ""},
        {"run_id": "   "},
        {"run_id": None},
        {"provenance_token": ""},
        {"provenance_token": "a" * 63},
        {"provenance_token": "A" * 64},
        {"provenance_token": None},
    ],
)
def test_activation_evidence_rejects_loose_values(override):
    """Doğru-görünen değer kanıt DEĞİLDİR — yapımda reddedilir."""
    fields = dict(_ACTIVATION_DEFAULTS)
    fields.update(override)
    with pytest.raises((TypeError, ValueError)):
        ActivationGateEvidence(**fields)


@pytest.mark.parametrize(
    "override",
    [
        {"manager_approved": "false"},
        {"katman1_passed": 1},
        {"manager_approved": None},
        # Plan 2 Task 8 — köken alanlarının şekil kapıları.
        {"incident_id": ""},
        {"incident_id": None},
        {"package_id": str(uuid.UUID(int=1))},
        {"onay_kapsam_sha": "a" * 63},
        {"onay_kapsam_sha": "A" * 64},
        {"provenance_token": ""},
        {"provenance_token": "a" * 63},
        {"provenance_token": None},
    ],
)
def test_rollback_evidence_rejects_loose_values(override):
    fields = dict(_ROLLBACK_DEFAULTS)
    fields.update(override)
    with pytest.raises((TypeError, ValueError)):
        RollbackGateEvidence(**fields)


class _LookalikeEvidence:
    """Aynı alan adlarını taşıyan ama kanıt sınıfı OLMAYAN nesne."""

    activation_eligible = True
    open_questions_count = 0
    katman1_passed = True
    checklist_approved = True
    expected_active_version = None
    manager_approved = True


async def test_activate_rejects_lookalike_evidence(pkg_db):
    """Ördek tiplemesi kanıt yerine geçmez — sınıfın kendisi istenir."""
    sector_id = await _sub_sector(pkg_db)
    package_id = await _seed_package(pkg_db, sector_id, version=1, status="draft")

    with pytest.raises(GateNotSatisfied):
        await activate_package(
            pkg_db, package_id=package_id, evidence=_LookalikeEvidence(), actor=ACTOR
        )
    assert await _status(pkg_db, package_id) == "draft"


async def test_rollback_rejects_lookalike_evidence(pkg_db):
    sector_id = await _sub_sector(pkg_db)
    await _seed_package(pkg_db, sector_id, version=1, status="archived")
    current_id = await _seed_package(pkg_db, sector_id, version=2, status="active")

    with pytest.raises(GateNotSatisfied):
        await rollback_package(
            pkg_db,
            sector_id=sector_id,
            to_version=1,
            evidence=_LookalikeEvidence(),
            actor=ACTOR,
        )
    assert await _status(pkg_db, current_id) == "active"


async def test_rollback_rejects_activation_evidence(pkg_db):
    """Aktivasyon kanıtı rollback kapısını açmaz (sınıflar paylaşılmaz)."""
    sector_id = await _sub_sector(pkg_db)
    await _seed_package(pkg_db, sector_id, version=1, status="archived")
    await _seed_package(pkg_db, sector_id, version=2, status="active")

    with pytest.raises(GateNotSatisfied):
        await rollback_package(
            pkg_db,
            sector_id=sector_id,
            to_version=1,
            evidence=await _kanit(pkg_db, sector_id),
            actor=ACTOR,
        )


# ═══ 8. Eşzamanlılık — gerçek iki bağlantı (checkpoint 13, F2) ══════════════
#
# Tek bağlantıda araya girmek bu sınıfı ÖLÇMEZ: soru tam olarak "iki ayrı
# transaction aynı taslağı aynı anda aktive edebilir mi". Bu testler kendi
# bağlantılarını açar ve GERÇEKTEN commit eder, o yüzden temizlik ellerindedir.


async def _seed_committed_sector(conn) -> uuid.UUID:
    root_id = await conn.fetchval(
        "SELECT id FROM social.sectors WHERE parent_sector_id IS NULL LIMIT 1"
    )
    assert root_id is not None
    return await conn.fetchval(
        "INSERT INTO social.sectors (slug, display_name, parent_sector_id) "
        "VALUES ($1, $2, $3) RETURNING id",
        f"alt-{uuid.uuid4().hex[:8]}",
        "Alt Sektör",
        root_id,
    )


async def _drop_committed_sector(conn, sector_id) -> None:
    await conn.execute("DELETE FROM social.package_events WHERE sector_id = $1", sector_id)
    # Köken mührü satırları da committed'dır (Plan 2 Task 15) — bırakılırsa
    # sonraki koşumda aynı `run_id` HARCANMIŞ jetonla karşılaşır ve testler
    # birbirinin kalıntısına bağlı hâle gelirdi.
    await conn.execute(
        "DELETE FROM social.package_rollback_plans WHERE package_id IN "
        "(SELECT id FROM social.sector_packages WHERE sector_id = $1)",
        sector_id,
    )
    await conn.execute(
        "DELETE FROM social.sector_package_runs WHERE sector_id = $1", sector_id
    )
    await conn.execute("DELETE FROM social.sector_packages WHERE sector_id = $1", sector_id)
    await conn.execute("DELETE FROM social.sectors WHERE id = $1", sector_id)


@pytest.mark.parametrize(
    "with_previous_active", [False, True], ids=["first_activation", "handover"]
)
async def test_concurrent_activation_of_same_draft_single_winner(
    test_db_setup, with_previous_active
):
    """Aynı taslağı iki transaction aynı anda aktive edemez.

    Kaybeden taraf sessizce başarılı olmamalı; ve denetim izinde TEK bir
    aktivasyon satırı kalmalı. İki olay satırı, olmamış bir devir teslimi
    olmuş gösterir.
    """
    import asyncio

    import asyncpg as _asyncpg

    from .conftest import _require_test_database

    url = _require_test_database(test_db_setup)
    setup = await _asyncpg.connect(url)
    await _init_connection(setup)
    workers: list = []
    sector_id = None
    try:
        sector_id = await _seed_committed_sector(setup)
        if with_previous_active:
            await setup.execute(
                "INSERT INTO social.sector_packages "
                "(sector_id, version, status, schema_version, content) "
                "VALUES ($1, 1, 'active', 1, $2)",
                sector_id,
                _valid_content(),
            )
        draft_id = await setup.fetchval(
            "INSERT INTO social.sector_packages "
            "(sector_id, version, status, schema_version, content) "
            "VALUES ($1, $2, 'draft', 1, $3) RETURNING id",
            sector_id,
            2 if with_previous_active else 1,
            _valid_content(),
        )

        for _ in range(2):
            worker = await _asyncpg.connect(url)
            await _init_connection(worker)
            workers.append(worker)

        # TEK mühürlü kanıt: jeton tek kullanımlıktır, yani köken kapısı da
        # kazananı tekleştirir. Sektör kilidi ile jeton kapısı BURADA aynı
        # sonuca varır ve bu bilinçlidir — iddia "tek kazanan"dır, hangi kapının
        # tekleştirdiği değil.
        kanit = await _kanit(
            setup,
            sector_id,
            **({"expected_active_version": 1} if with_previous_active else {}),
        )

        async def _try(conn):
            try:
                await activate_package(
                    conn,
                    package_id=draft_id,
                    evidence=kanit,
                    actor=ACTOR,
                )
                return "ok"
            except Exception as exc:  # kaybeden taraf AÇIKÇA düşmeli
                return type(exc).__name__

        results = await asyncio.gather(*[_try(worker) for worker in workers])

        assert results.count("ok") == 1, f"tek kazanan bekleniyordu: {results}"
        events = await setup.fetch(
            "SELECT event_type FROM social.package_events WHERE sector_id = $1", sector_id
        )
        assert [e["event_type"] for e in events] == ["activation"], (
            f"denetim izinde tek aktivasyon bekleniyordu: {[e['event_type'] for e in events]}"
        )
        assert await setup.fetchval(
            "SELECT count(*) FROM social.sector_packages "
            "WHERE sector_id = $1 AND status = 'active'",
            sector_id,
        ) == 1
    finally:
        for worker in workers:
            await worker.close()
        if sector_id is not None:
            await _drop_committed_sector(setup, sector_id)
        await setup.close()


# ═══ 9. Olay yazıcısının gerçeğe bağlanması (checkpoint 13, F3) ═════════════


async def test_activation_event_rejects_arbitrary_from_version(pkg_db):
    """Uydurma kaynak sürüm, eksik kaynak sürüm kadar zararlıdır.

    Eski kural asimetrikti: yalnız `from_version` YOKKEN itiraz ediyordu,
    dolayısıyla alakasız bir sürüm numarası denetimsiz geçip denetim izine
    olmamış bir devir teslim yazabiliyordu.
    """
    from app.services.package_events import PackageEventContractError, log_package_event

    sector_id = await _sub_sector(pkg_db)
    await _seed_package(pkg_db, sector_id, version=1, status="active")
    target_id = await _seed_package(pkg_db, sector_id, version=2, status="draft")

    with pytest.raises(PackageEventContractError, match="beklenen 1"):
        await log_package_event(
            pkg_db,
            event_type="activation",
            sector_id=sector_id,
            package_id=target_id,
            from_version=7,
            to_version=2,
            actor=ACTOR,
        )


async def test_activation_event_rejects_write_after_transition(pkg_db):
    """Sıra sözleşmesi artık MEKANİK — yorum değil.

    Olay geçişten SONRA yazılırsa devredilen paket çoktan arşivlenmiştir;
    gerçek aktif sürüm ölçüsü `None` döner ve kaynak sürüm taşıyan olay
    reddedilir. Eskiden bu yazım sessizce kabul ediliyordu.
    """
    from app.services.package_events import PackageEventContractError, log_package_event

    sector_id = await _sub_sector(pkg_db)
    old_id = await _seed_package(pkg_db, sector_id, version=1, status="active")
    new_id = await _seed_package(pkg_db, sector_id, version=2, status="draft")

    # Geçişi elle uygula, olayı SONRA yazmayı dene.
    await pkg_db.execute(
        "UPDATE social.sector_packages SET status = 'archived' WHERE id = $1", old_id
    )
    await pkg_db.execute(
        "UPDATE social.sector_packages SET status = 'active' WHERE id = $1", new_id
    )

    with pytest.raises(PackageEventContractError):
        await log_package_event(
            pkg_db,
            event_type="activation",
            sector_id=sector_id,
            package_id=new_id,
            from_version=1,
            to_version=2,
            actor=ACTOR,
        )


async def test_concurrent_activation_of_different_drafts_is_serializable(test_db_setup):
    """İki FARKLI taslağın eşzamanlı aktivasyonu, sırayla koşmuş gibi biter.

    Bu, sektör kilidinin ölçüsüdür. Kilit olmadan iki transaction hiçbir yerde
    karşılaşmaz (ilk aktivasyonda kilitlenecek aktif satır YOKTUR): ikisi de
    kendi taslağını aktif yapar ve çakışmayı ancak COMMIT anında tek-aktif
    kısmi indeksi yakalar — kaybeden taraf HAM bir kısıt ihlaliyle ölür.
    Sektör satırı her durumda var olduğu için serileştirme çapası odur.

    İddia dar tutuldu: kaybeden taraf düşebilir, ama ham `UniqueViolationError`
    ile DEĞİL; ve son durum her koşulda tutarlı olmalı.
    """
    import asyncio

    import asyncpg as _asyncpg

    from .conftest import _require_test_database

    url = _require_test_database(test_db_setup)
    setup = await _asyncpg.connect(url)
    await _init_connection(setup)
    workers: list = []
    sector_id = None
    try:
        sector_id = await _seed_committed_sector(setup)
        drafts = [
            await setup.fetchval(
                "INSERT INTO social.sector_packages "
                "(sector_id, version, status, schema_version, content) "
                "VALUES ($1, $2, 'draft', 1, $3) RETURNING id",
                sector_id,
                version,
                _valid_content(),
            )
            for version in (1, 2)
        ]

        for _ in range(2):
            worker = await _asyncpg.connect(url)
            await _init_connection(worker)
            workers.append(worker)

        # AYRI kanıt, AYRI jeton: bu testin konusu sektör kilidinin
        # serileştirmesidir. Tek jeton paylaşılsaydı kazananı köken kapısı
        # belirler ve kilit HİÇ ÖLÇÜLMEMİŞ olurdu. Mühürleme yarıştan ÖNCE ve
        # TEK bağlantıda yapılır — asyncpg bağlantısı eşzamanlı kullanılamaz.
        kanitlar = {
            draft: await _kanit(setup, sector_id, run_id=f"kosu-{draft}")
            for draft in drafts
        }

        async def _try(conn, draft_id):
            try:
                await activate_package(
                    conn, package_id=draft_id, evidence=kanitlar[draft_id], actor=ACTOR
                )
                return "ok"
            except LifecycleError:
                return "lifecycle-error"
            except GateNotSatisfied:
                # K-94 taban durumu (Plan 2 Task 15): kaybeden taraf artık
                # burada da düşebilir — kazanan aktif satırı yarattığı için
                # "ilk aktivasyon" diyen kanıt geçersizleşir. Bu AÇIK bir
                # reddir, testin yasakladığı HAM veritabanı hatası değildir.
                return "gate-not-satisfied"
            except Exception as exc:
                return f"RAW:{type(exc).__name__}"

        results = await asyncio.gather(
            *[_try(worker, draft) for worker, draft in zip(workers, drafts)]
        )

        raw = [r for r in results if r.startswith("RAW:")]
        assert raw == [], f"kaybeden taraf ham veritabanı hatasıyla düştü: {raw}"

        assert await setup.fetchval(
            "SELECT count(*) FROM social.sector_packages "
            "WHERE sector_id = $1 AND status = 'active'",
            sector_id,
        ) == 1, "tek-aktif değişmezi bozuldu"

        events = await setup.fetch(
            "SELECT event_type FROM social.package_events WHERE sector_id = $1", sector_id
        )
        assert len(events) == results.count("ok"), (
            f"olay sayısı başarılı geçiş sayısıyla eşleşmiyor: "
            f"{len(events)} olay, {results.count('ok')} geçiş"
        )
    finally:
        for worker in workers:
            await worker.close()
        if sector_id is not None:
            await _drop_committed_sector(setup, sector_id)
        await setup.close()


# ═══ 10. Kilit ile hedef arasındaki sektör penceresi (checkpoint 13, F4) ════


async def _race_sector_reassignment(test_db_setup, *, transition, seed_status, with_keeper):
    """Kilit alındıktan SONRA hedefin sektörünü değiştirir, sonra geçişi dener.

    Pencere gerçektir: sektör KİLİTSİZ okunuyor, o sektör kilitleniyor, sonra
    hedef yeniden okunurken sektörü YENİDEN OKUNMUYORDU. Araya giren bir
    yeniden-atama, A'nın aktif paketini arşivleyip B'ye ait hedefi aktive
    ettirebiliyor ve olayı A'ya yazdırabiliyordu. Karşılaştır-ve-yaz bunu
    görmez, çünkü sektöre bağlı değildir.

    Araya girme monkeypatch ile DETERMİNİSTİK kurulur — yarışın rastlantısına
    bırakmak bu sınıfı ölçmez.

    `seed_status` hedefin geçişe UYGUN durumu olmalıdır; aksi hâlde fonksiyon
    zaten başka bir gerekçeyle düşer ve test sektör penceresini hiç ölçmez
    (ilk yazımda deaktivasyon dalı tam bunu yaptı — sahte yeşil).
    """
    import asyncpg as _asyncpg

    from .conftest import _require_test_database

    url = _require_test_database(test_db_setup)
    setup = await _asyncpg.connect(url)
    await _init_connection(setup)
    worker = intruder = None
    sector_a = sector_b = None
    try:
        sector_a = await _seed_committed_sector(setup)
        sector_b = await _seed_committed_sector(setup)
        keeper_id = None
        if with_keeper:
            keeper_id = await setup.fetchval(
                "INSERT INTO social.sector_packages "
                "(sector_id, version, status, schema_version, content) "
                "VALUES ($1, 1, 'active', 1, $2) RETURNING id",
                sector_a,
                _valid_content(),
            )
        target_id = await setup.fetchval(
            "INSERT INTO social.sector_packages "
            "(sector_id, version, status, schema_version, content) "
            "VALUES ($1, 2, $2, 1, $3) RETURNING id",
            sector_a,
            seed_status,
            _valid_content(),
        )

        worker = await _asyncpg.connect(url)
        await _init_connection(worker)
        intruder = await _asyncpg.connect(url)
        await _init_connection(intruder)

        original = sector_package_lifecycle._lock_sector
        moved = {"done": False}

        async def _lock_then_move(db, sector_id):
            await original(db, sector_id)
            if not moved["done"]:
                moved["done"] = True
                await intruder.execute(
                    "UPDATE social.sector_packages SET sector_id = $2 WHERE id = $1",
                    target_id,
                    sector_b,
                )

        sector_package_lifecycle._lock_sector = _lock_then_move
        try:
            with pytest.raises(LifecycleError):
                await transition(worker, target_id)
        finally:
            sector_package_lifecycle._lock_sector = original

        assert moved["done"], "araya girme hiç koşmadı — test kendini ölçmüyor"
        assert (
            await setup.fetchval(
                "SELECT status FROM social.sector_packages WHERE id = $1", target_id
            )
            == seed_status
        ), "reddedilen geçiş yine de hedefin durumunu değiştirdi"
        if keeper_id is not None:
            assert (
                await setup.fetchval(
                    "SELECT status FROM social.sector_packages WHERE id = $1", keeper_id
                )
                == "active"
            ), "yanlış sektörün aktif paketi arşivlendi"
        for sector in (sector_a, sector_b):
            assert (
                await setup.fetchval(
                    "SELECT count(*) FROM social.package_events WHERE sector_id = $1", sector
                )
                == 0
            ), "reddedilen geçiş olay yazdı"
    finally:
        for conn in (worker, intruder):
            if conn is not None:
                await conn.close()
        for sector in (sector_a, sector_b):
            if sector is not None:
                await _drop_committed_sector(setup, sector)
        await setup.close()


async def test_activation_rejects_sector_reassignment_under_lock(test_db_setup):
    async def _transition(conn, target_id):
        sector_id = await conn.fetchval(
            "SELECT sector_id FROM social.sector_packages WHERE id = $1", target_id
        )
        kanit = await _kanit(conn, sector_id, run_id=f"kosu-{target_id}")
        await activate_package(
            conn, package_id=target_id, evidence=kanit, actor=ACTOR
        )

    await _race_sector_reassignment(
        test_db_setup, transition=_transition, seed_status="draft", with_keeper=True
    )


async def test_deactivation_rejects_sector_reassignment_under_lock(test_db_setup):
    """Hedef GERÇEKTEN aktif olmalı — aksi hâlde fonksiyon başka gerekçeyle düşer."""

    async def _transition(conn, target_id):
        await deactivate_package(conn, package_id=target_id, actor=ACTOR)

    await _race_sector_reassignment(
        test_db_setup, transition=_transition, seed_status="active", with_keeper=False
    )


# ─── K-112 (b): takvim erişilemezken YAZIM KAPISI (Plan 2 Task 12) ──────────
#
# Ölçülen şey eşleşmeme DEĞİL, ERİŞİLEMEZLİKTİR. Bu yolda sessiz düşüş YANLIŞ
# olurdu: anahtar doğrulaması yapılamadan yazım, uydurma bir özel gün anahtarını
# pakete alırdı. Doğru davranış açık ve TİPLİ bir hatayla fail-closed durmaktır.
# Bugünkü davranış (ham `asyncpg` istisnası) doğruydu ama KAZARAydı; taban ölçümü
# `docs/research/2026-08-27-k112-takvim-erisilemezlik-taban.md`'dedir.


class _TakvimiDusenBaglanti:
    """Yalnız takvim sorgusunda düşen sarmalayıcı — hata ENJEKSİYONU."""

    def __init__(self, inner):
        self._inner = inner
        self.calendar_reads = 0

    async def fetch(self, query, *args, **kwargs):
        if "public_holidays" in query:
            self.calendar_reads += 1
            raise RuntimeError("takvim tablosuna erisilemedi (enjekte edilmis ariza)")
        return await self._inner.fetch(query, *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._inner, name)


async def test_calendar_unavailable_fails_draft_write_closed(pkg_db):
    """Takvim okunamazsa yazım TİPLİ bir hatayla durur; satır YAZILMAZ."""
    sector_id = await _sub_sector(pkg_db)
    kirik = _TakvimiDusenBaglanti(pkg_db)

    with pytest.raises(sector_package_lifecycle.CalendarUnavailable):
        await insert_draft(
            kirik,
            sector_id=sector_id,
            content=_valid_content(),
            schema_version=1,
            actor=ACTOR,
        )

    assert kirik.calendar_reads == 1, "kapı takvimi GERÇEKTEN okumaya çalışmalı"
    yazilan = await pkg_db.fetchval(
        "SELECT count(*) FROM social.sector_packages WHERE sector_id = $1", sector_id
    )
    assert yazilan == 0, "kapı geçilmeden satır yazılamaz"


async def test_calendar_unavailable_error_keeps_the_original_cause(pkg_db):
    """Tipli hata ham sebebi YUTMAZ — teşhis kaybolmaz."""
    sector_id = await _sub_sector(pkg_db)
    kirik = _TakvimiDusenBaglanti(pkg_db)

    with pytest.raises(sector_package_lifecycle.CalendarUnavailable) as hata:
        await insert_draft(
            kirik,
            sector_id=sector_id,
            content=_valid_content(),
            schema_version=1,
            actor=ACTOR,
        )

    assert isinstance(hata.value.__cause__, RuntimeError)
    assert hata.value.__cause__ is not hata.value


async def test_calendar_available_still_writes_the_draft(pkg_db):
    """POZİTİF KONTROL: kapı yalnız ERİŞİLEMEZLİKTE kapanır."""
    sector_id = await _sub_sector(pkg_db)
    package_id = await insert_draft(
        pkg_db,
        sector_id=sector_id,
        content=_valid_content(),
        schema_version=1,
        actor=ACTOR,
    )
    assert package_id is not None
