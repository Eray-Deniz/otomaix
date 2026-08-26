"""K-07 damga tüketimi + kalıcı paket olay kaydı (plan Task 12).

İki ayrı sözleşme, tek dosyada çünkü ikisi de aynı olay tablosuna yaslanıyor:

1. **Olay kaydı (`log_package_event`).** Kapalı olay kümesi, iki kapsam sınıfı
   (F21) ve olay-türüne özgü sürüm şekli (F22). Fonksiyon kendi sözleşmesini
   DOĞRULAR — çağıran tarafın dikkatine bırakılmaz, çünkü olay kaydı bir
   denetim izidir ve yarım kayıt sessiz bir yalan üretir.
2. **Damga tüketimi (K-07).** Üretim anında yazılan makbuz, kalıcı-kayıt
   isteğinde ATOMİK ve TEK-KULLANIMLIK tüketilir; kayıtlı çift AYNEN yazılır,
   kayıt anında yeniden çözümleme YAPILMAZ.

**Test yaprağa değil YOLA bakar** (checkpoint 11'in dersi): damga testleri
yardımcı fonksiyonu değil, gerçek kalıcı-kayıt ucunu (`/posts/generate` ve kısa
video stage-1) koşar. Yardımcıyı test edip yönlendiricide ayrılan yolu kaçırmak
bu yürütmede iki kez ölçüldü.
"""

from __future__ import annotations

import asyncio
import logging
import uuid

import asyncpg
import pytest

from app.core.database import _init_connection
from app.services.sector_packages import resolve_package_context
from app.services.package_events import (
    BRAND_SCOPED_EVENTS,
    EVENT_TYPES,
    LIFECYCLE_EVENTS,
    PackageEventContractError,
    log_package_event,
)

# ─── Ortak seed ─────────────────────────────────────────────────────────────


# Yapısal olarak GEÇERLİ içerik tek yerde yaşar: yazım kapısıyla okuma kapısı
# aynı doğrulayıcıyı paylaşıyor (Task 8), o yüzden fixture'ı kopyalamak iki
# ölçü yaratma riskidir — kopya bayatlarsa bu dosya sessizce "geçersiz paket"
# senaryosunu test etmeye başlardı (ölçüldü: ilk yazımda tam bunu yaptı).
from .test_sector_packages_service import _valid_content  # noqa: E402


async def _seed_sector_and_package(db, *, status: str = "active", version: int = 1):
    """Kök sektör + alt sektör + paket. `(sub_id, package_id)` döner."""
    root_id = await db.fetchval(
        "SELECT id FROM social.sectors WHERE parent_sector_id IS NULL LIMIT 1"
    )
    assert root_id is not None, "kök sektör seed'i eksik"
    sub_id = await db.fetchval(
        "INSERT INTO social.sectors (slug, display_name, parent_sector_id) "
        "VALUES ($1, $2, $3) RETURNING id",
        f"alt-{uuid.uuid4().hex[:8]}",
        "Alt Sektör",
        root_id,
    )
    package_id = await db.fetchval(
        "INSERT INTO social.sector_packages (sector_id, version, status, schema_version, content) "
        "VALUES ($1, $2, $3, 1, $4) RETURNING id",
        sub_id,
        version,
        status,
        _valid_content(),
    )
    return sub_id, package_id


async def _seed_brand(db, *, sub_sector_id=None):
    """Hesap + workspace + üyelik + marka. `(account_id, brand_id)` döner."""
    account_id = await db.fetchval(
        "INSERT INTO social.accounts (email, name, plan_id) "
        "VALUES ($1, 'Damga Sahibi', 'pro') RETURNING id",
        f"damga-{uuid.uuid4()}@example.test",
    )
    workspace_id = await db.fetchval(
        "INSERT INTO social.workspaces (account_id, name) VALUES ($1, 'Damga') RETURNING id",
        account_id,
    )
    await db.execute(
        "INSERT INTO social.workspace_members (workspace_id, account_id) VALUES ($1, $2)",
        workspace_id,
        account_id,
    )
    brand_id = await db.fetchval(
        "INSERT INTO social.brands (workspace_id, name, sector, brand_kit, sub_sector_id) "
        "VALUES ($1, 'Damga Markası', 'Kuyumculuk', $2, $3) RETURNING id",
        workspace_id,
        {"tonality": "professional"},
        sub_sector_id,
    )
    return account_id, brand_id


async def _write_stamp(db, *, brand_id, package_id, version) -> uuid.UUID:
    return await db.fetchval(
        "INSERT INTO social.generation_stamps (brand_id, package_id, package_version) "
        "VALUES ($1, $2, $3) RETURNING id",
        brand_id,
        package_id,
        version,
    )


@pytest.fixture
async def pkg_db(db):
    """Üretimin KENDİ bağlantı yapılandırması (jsonb codec) uygulanmış bağlantı."""
    await _init_connection(db)
    return db


# ═══ 1. Olay kaydı sözleşmesi ═══════════════════════════════════════════════


async def test_event_types_are_a_closed_set():
    """Olay kümesi kapalı ve iki kapsam sınıfı ÖRTÜŞMEZ."""
    assert EVENT_TYPES == BRAND_SCOPED_EVENTS | LIFECYCLE_EVENTS
    assert not (BRAND_SCOPED_EVENTS & LIFECYCLE_EVENTS)
    assert LIFECYCLE_EVENTS == {"activation", "rollback", "deactivation"}


async def test_unknown_event_type_rejected(pkg_db):
    """Küme dışı tür yazılamaz — kapalı küme kapı olarak işler."""
    _, brand_id = await _seed_brand(pkg_db)
    with pytest.raises(PackageEventContractError):
        await log_package_event(pkg_db, event_type="uydurma_olay", brand_id=brand_id)


@pytest.mark.parametrize("event_type", sorted(BRAND_SCOPED_EVENTS))
async def test_brand_scoped_event_requires_brand_id(pkg_db, event_type):
    """Marka-kapsamlı olay markasız yazılamaz (F21).

    Markasız bir `stamp_invalid` kaydı hangi markanın etkilendiğini söylemez;
    denetim izi olarak değersiz, üstelik "olay kaydedildi" görüntüsü verir.
    """
    with pytest.raises(PackageEventContractError):
        await log_package_event(pkg_db, event_type=event_type)


async def test_brand_scoped_event_persists(pkg_db):
    """Geçerli marka-kapsamlı olay satır olarak yazılır."""
    _, brand_id = await _seed_brand(pkg_db)
    event_id = await log_package_event(
        pkg_db, event_type="stamp_invalid", brand_id=brand_id, detail={"reason": "consumed"}
    )
    row = await pkg_db.fetchrow(
        "SELECT event_type, brand_id, detail FROM social.package_events WHERE id = $1", event_id
    )
    assert row["event_type"] == "stamp_invalid"
    assert row["brand_id"] == brand_id
    assert row["detail"] == {"reason": "consumed"}


async def test_lifecycle_event_valid_without_brand(pkg_db):
    """İlk aktivasyon marka atamasından ÖNCE meşrudur (F21) — fan-out YOK."""
    sub_id, package_id = await _seed_sector_and_package(pkg_db)
    event_id = await log_package_event(
        pkg_db,
        event_type="activation",
        sector_id=sub_id,
        package_id=package_id,
        to_version=1,
        actor="admin",
    )
    row = await pkg_db.fetchrow(
        "SELECT brand_id, sector_id, to_version FROM social.package_events WHERE id = $1", event_id
    )
    assert row["brand_id"] is None
    assert row["sector_id"] == sub_id
    assert row["to_version"] == 1


@pytest.mark.parametrize("missing", ["sector_id", "package_id", "actor"])
async def test_lifecycle_event_requires_sector_package_actor(pkg_db, missing):
    """Yaşam döngüsü olayı üç alanı ZORUNLU ister (F21)."""
    sub_id, package_id = await _seed_sector_and_package(pkg_db)
    kwargs = dict(
        event_type="activation",
        sector_id=sub_id,
        package_id=package_id,
        to_version=1,
        actor="admin",
    )
    kwargs[missing] = None
    with pytest.raises(PackageEventContractError):
        await log_package_event(pkg_db, **kwargs)


async def test_activation_event_first_allows_null_from_version(pkg_db):
    """İLK aktivasyonda `from_version` NULL meşrudur (F22)."""
    sub_id, package_id = await _seed_sector_and_package(pkg_db)
    event_id = await log_package_event(
        pkg_db,
        event_type="activation",
        sector_id=sub_id,
        package_id=package_id,
        to_version=1,
        actor="admin",
    )
    assert event_id is not None


async def test_activation_event_replacement_requires_from_version(pkg_db):
    """Yerine-geçme aktivasyonunda `from_version` ZORUNLU (F22).

    "Yerine geçilen bir şey var mı" sorusu ÇAĞIRANA sorulmaz, aynı tablodan
    okunur: sektörde ŞU AN aktif olan başka bir paket varsa bu bir devir
    teslimdir. İki ayrı alan (bir "bu replacement" bayrağı + `from_version`)
    birbiriyle çelişebilirdi; tek ölçüye bağlamak o sınıfı kapatır.

    Olay geçişten ÖNCE yazılır (`_apply_status_transition` sözleşmesi), o
    yüzden bu kurulum devredilen sürümü hâlâ `active` tutar.
    """
    sub_id, first_id = await _seed_sector_and_package(pkg_db, status="active", version=1)
    second_id = await pkg_db.fetchval(
        "INSERT INTO social.sector_packages (sector_id, version, status, schema_version, content) "
        "VALUES ($1, 2, 'draft', 1, $2) RETURNING id",
        sub_id,
        _valid_content(),
    )
    assert first_id != second_id

    with pytest.raises(PackageEventContractError):
        await log_package_event(
            pkg_db,
            event_type="activation",
            sector_id=sub_id,
            package_id=second_id,
            to_version=2,
            actor="admin",
        )

    event_id = await log_package_event(
        pkg_db,
        event_type="activation",
        sector_id=sub_id,
        package_id=second_id,
        from_version=1,
        to_version=2,
        actor="admin",
    )
    assert event_id is not None


async def test_activation_event_requires_to_version(pkg_db):
    """Aktivasyonun hedef sürümü uydurma değerle temsil edilemez (F22)."""
    sub_id, package_id = await _seed_sector_and_package(pkg_db)
    with pytest.raises(PackageEventContractError):
        await log_package_event(
            pkg_db,
            event_type="activation",
            sector_id=sub_id,
            package_id=package_id,
            actor="admin",
        )


@pytest.mark.parametrize("drop", ["from_version", "to_version"])
async def test_rollback_event_requires_source_and_target_versions(pkg_db, drop):
    """Rollback İKİ sürümü de ister: arşivlenen kaynak + geri getirilen hedef."""
    sub_id, package_id = await _seed_sector_and_package(pkg_db)
    kwargs = dict(
        event_type="rollback",
        sector_id=sub_id,
        package_id=package_id,
        from_version=2,
        to_version=1,
        actor="admin",
    )
    kwargs[drop] = None
    with pytest.raises(PackageEventContractError):
        await log_package_event(pkg_db, **kwargs)


async def test_deactivation_event_requires_from_null_to(pkg_db):
    """Deaktivasyonun hedefi YOKTUR — `to_version` NULL kalmalı (F22).

    `from_version` ayrıca GERÇEĞE karşı doğrulanır: geri çekilen paketin
    kendi sürümü olmalı. Eskiden boş olmayan herhangi bir değer denetimsiz
    geçiyordu (checkpoint 13, F3) — uydurma bir kaynak sürüm, eksik kaynak
    sürüm kadar zararlıdır.
    """
    sub_id, package_id = await _seed_sector_and_package(pkg_db, version=1)

    # (a) kaynak sürüm hiç yok
    with pytest.raises(PackageEventContractError):
        await log_package_event(
            pkg_db,
            event_type="deactivation",
            sector_id=sub_id,
            package_id=package_id,
            actor="admin",
        )

    # (b) kaynak sürüm var ama GERÇEK değil
    with pytest.raises(PackageEventContractError):
        await log_package_event(
            pkg_db,
            event_type="deactivation",
            sector_id=sub_id,
            package_id=package_id,
            from_version=3,
            actor="admin",
        )

    event_id = await log_package_event(
        pkg_db,
        event_type="deactivation",
        sector_id=sub_id,
        package_id=package_id,
        from_version=1,
        actor="admin",
    )
    assert event_id is not None


async def test_lifecycle_event_rejects_contradictory_shape(pkg_db):
    """Çelişkili kombinasyon reddedilir (F22): deaktivasyon + hedef sürüm."""
    sub_id, package_id = await _seed_sector_and_package(pkg_db)
    with pytest.raises(PackageEventContractError):
        await log_package_event(
            pkg_db,
            event_type="deactivation",
            sector_id=sub_id,
            package_id=package_id,
            from_version=3,
            to_version=4,
            actor="admin",
        )


@pytest.mark.parametrize(
    "bad_detail",
    [
        pytest.param({"content": _valid_content()}, id="paket-içeriği"),
        pytest.param({"pool": ["a", "b"]}, id="liste"),
        pytest.param({"long": "x" * 500}, id="uzun-metin"),
        pytest.param("düz metin", id="sözlük-değil"),
    ],
)
async def test_event_detail_excludes_package_content(pkg_db, bad_detail):
    """`detail` KAPALI bir şekle uyar; paket içeriği yapısal olarak giremez.

    "Bu metin paket içeriği DEĞİL mi" sorusunu serbest metinden cevaplamaya
    çalışan bir yüklem yakınsamaz (bu yürütmede beş tur boyunca ölçüldü). O
    yüzden kural NEGATİF değil POZİTİF: `detail` yalnız skaler değerli, kısa
    bir sözlüktür. Paket içeriği iç içe ve uzundur — şekle takılır, anlamına
    bakılmasına gerek kalmaz.
    """
    _, brand_id = await _seed_brand(pkg_db)
    with pytest.raises(PackageEventContractError):
        await log_package_event(
            pkg_db, event_type="stamp_invalid", brand_id=brand_id, detail=bad_detail
        )


async def test_event_write_failure_does_not_block_caller(caplog):
    """Olay tablosu yazılamazsa üretim DÜŞMEZ — hata log'a düşer.

    Sözleşme ihlali (çağıranın hatası) İSTİSNA atar; altyapı hatası atmaz. İkisi
    ayrı sınıftır: birincisi kodun yanlış olduğunu söyler ve testte yakalanmalı,
    ikincisi kullanıcının içeriğini düşürmek için yeterli sebep değildir.
    """

    class _WriteFails:
        async def fetchval(self, *_args, **_kwargs):
            raise RuntimeError("tablo yok")

    with caplog.at_level(logging.ERROR):
        result = await log_package_event(
            _WriteFails(), event_type="stamp_invalid", brand_id=uuid.uuid4()
        )

    assert result is None
    assert any("paket olayı yazılamadı" in r.getMessage() for r in caplog.records)


async def test_event_write_failure_inside_transaction_does_not_poison_it(pkg_db, caplog):
    """Yutulan olay hatası çağıranın transaction'ını ÖLDÜRMEZ (review 2026-08-26, H2).

    Yukarıdaki test sahte bir bağlantı nesnesiyle koşar ve transaction YOKTUR —
    o yüzden "üretim düşmez" sözünü gerçek yolda hiç sınamıyordu. Üretimde
    `resolve_persist_stamp` post yazımıyla AYNI transaction'ın içindedir
    (`routers/posts.py`, K-07). PostgreSQL'de başarısız bir ifade transaction'ı
    abort durumuna sokar ve sonraki HER komut — `SELECT 1` dahil — reddedilir;
    asyncpg kendiliğinden savepoint AÇMAZ. Savepoint olmadan bu sözleşme
    transaction dışında doğru, içinde YANLIŞTI: yutulan hata post yazımını da
    düşürüyor ve kullanıcı 500 alıyordu.

    Mutasyon kontrolü: `log_package_event`'teki `async with db.transaction()`
    kaldırılırsa bu test `InFailedSQLTransactionError` ile DÜŞER (ölçüldü).
    """
    sub_id, _package_id = await _seed_sector_and_package(pkg_db)
    _account_id, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)

    async with pkg_db.transaction():
        # Olay tablosunu bu transaction içinde erişilemez kıl — altyapı hatasının
        # gerçek karşılığı (033 uygulanmamış, izin çekilmiş, tablo taşınmış).
        await pkg_db.execute(
            "ALTER TABLE social.package_events RENAME TO package_events__unavailable"
        )

        with caplog.at_level(logging.ERROR):
            result = await log_package_event(
                pkg_db, event_type="stamp_invalid", brand_id=brand_id
            )

        assert result is None
        assert any("paket olayı yazılamadı" in r.getMessage() for r in caplog.records)

        # ASIL İDDİA: transaction hâlâ canlı — dıştaki iş devam edebilir.
        assert await pkg_db.fetchval("SELECT 1") == 1
        wrote = await pkg_db.fetchval(
            "UPDATE social.brands SET name = 'txn hayatta' WHERE id = $1 RETURNING name",
            brand_id,
        )
        assert wrote == "txn hayatta"


async def test_savepoint_only_opens_inside_a_caller_transaction(pkg_db):
    """Transaction DIŞINDA iç transaction AÇILMAZ (kapanış turu 2026-08-26, N1).

    `db.transaction()` transaction dışında savepoint değil GERÇEK transaction
    açar. `notifications._maybe_trigger_fast_dispatch` "açık transaction
    içindeysem ateşleme" kapısını taşıdığı için, koşulsuz sarmak yönetici
    bildiriminin hızlı gönderim yolunu bu yüzeyin TAMAMINDA sessizce öldürüyordu.
    Teslim garantisi değil (onu kurtarma yolu üstlenir), tasarlanmış gecikme
    kısaltması kaybolmuştu.

    Mutasyon kontrolü: `_savepoint_if_in_tx` koşulsuz `db.transaction()` dönerse
    ilk iddia DÜŞER.
    """
    from app.services.package_events import _savepoint_if_in_tx

    class _Conn:
        """`transaction()` çağrılıp çağrılmadığını kaydeden sahte bağlantı.

        Gerçek bağlantı KULLANILMAZ: bu dosyanın `db` fixture'ı testi zaten bir
        transaction'ın içinde koşturur (geri sarma fixture'ı), dolayısıyla
        "transaction dışında" dalı gerçek bağlantıyla hiç gözlemlenemezdi.
        """

        def __init__(self, in_tx: bool):
            self._in_tx = in_tx
            self.opened = False

        def is_in_transaction(self) -> bool:
            return self._in_tx

        def transaction(self):
            conn = self

            class _T:
                async def __aenter__(self):
                    conn.opened = True
                    return self

                async def __aexit__(self, *_exc):
                    return False

            return _T()

    outside = _Conn(in_tx=False)
    async with _savepoint_if_in_tx(outside):
        pass
    assert outside.opened is False, (
        "transaction DIŞINDA iç transaction açıldı — `db.transaction()` orada "
        "savepoint değil GERÇEK transaction açar ve hızlı gönderim kapısını tetikler"
    )

    inside = _Conn(in_tx=True)
    async with _savepoint_if_in_tx(inside):
        pass
    assert inside.opened is True, "transaction İÇİNDE savepoint açılmadı — koruma yok"

    # `is_in_transaction` taşımayan bağlantı benzeri nesne patlatmamalı.
    class _Bare:
        pass

    async with _savepoint_if_in_tx(_Bare()):
        pass

    # Gerçek bağlantı, gerçekten transaction içindeyken: savepoint açılır ve
    # dıştaki transaction ayakta kalır.
    assert pkg_db.is_in_transaction()
    async with _savepoint_if_in_tx(pkg_db):
        assert await pkg_db.fetchval("SELECT 1") == 1


async def test_admin_notify_failure_inside_transaction_does_not_poison_it(pkg_db, caplog):
    """Yönetici bildirimi düşerse çağıranın transaction'ı YAŞAR (N3 kapısı).

    `_notify_admin`in belgesi "ASLA akışı düşürmez" der, ama savepoint olmadan
    bu söz yalnız transaction dışında doğruydu. Kapanış turu bu savepoint'in
    hiçbir test tarafından bağlanmadığını mutasyonla ölçtü — bu test o boşluğu
    kapatır.

    Mutasyon kontrolü: `_notify_admin`deki savepoint kaldırılırsa bu test
    `InFailedSQLTransactionError` ile DÜŞER.
    """
    sub_id, _package_id = await _seed_sector_and_package(pkg_db)
    _account_id, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)

    async with pkg_db.transaction():
        # `mismatch_fallthrough` ADMIN_NOTIFIED_EVENTS içindedir → outbox yazımı
        # denenir. Outbox tablosunu bu transaction içinde erişilemez kılıyoruz.
        await pkg_db.execute(
            "ALTER TABLE social.admin_events RENAME TO admin_events__unavailable"
        )

        with caplog.at_level(logging.ERROR):
            event_id = await log_package_event(
                pkg_db, event_type="mismatch_fallthrough", brand_id=brand_id
            )

        # Olay satırı YAZILDI (asıl denetim izi), yalnız bildirim düştü.
        assert event_id is not None
        assert any("yönetici bildirimi yazılamadı" in r.getMessage() for r in caplog.records)

        # ASIL İDDİA: transaction hâlâ canlı.
        assert await pkg_db.fetchval("SELECT 1") == 1
        assert await pkg_db.fetchval(
            "SELECT count(*) FROM social.package_events WHERE id = $1", event_id
        ) == 1


# ═══ 2. Damga tüketimi — GERÇEK kalıcı-kayıt ucundan ════════════════════════


async def _generate_post(db, *, account_id, brand_id, generation_id=None):
    """`/posts/generate` ucunu üretim yolundan koşar (yaprak yardımcı DEĞİL)."""
    from app.models.schemas import PostGenerate
    from app.routers import posts as posts_router

    return await posts_router.generate_post(
        payload=PostGenerate(
            brand_id=brand_id,
            content_type="image",
            image_prompt="A gold ring on velvet",
            platforms=["instagram"],
            # Caption-öncüllü akışın sunucuda görünen izi — makbuz beklentisi
            # buna bağlıdır (alıntı akışı bunu göndermez).
            platform_captions={"instagram": {"caption": "x", "hashtags": ["#x"]}},
            generation_id=generation_id,
        ),
        user={"sub": str(account_id)},
        db=db,
    )


@pytest.fixture
def no_image_calls(monkeypatch):
    """fal.ai submit'i keser — bu dosyanın konusu damga, görsel değil."""
    from app.routers import posts as posts_router

    async def _fake_generate_image(*_args, **_kwargs):
        return "fake-job-id"

    monkeypatch.setattr(posts_router, "generate_image", _fake_generate_image)
    monkeypatch.setattr(posts_router, "generate_image_edit", _fake_generate_image)


async def test_persist_writes_recorded_stamp_verbatim(pkg_db, no_image_calls):
    """Kayıtlı çift AYNEN yazılır — kayıt anında yeniden çözümleme YOK."""
    sub_id, package_id = await _seed_sector_and_package(pkg_db, version=7)
    account_id, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)
    stamp_id = await _write_stamp(pkg_db, brand_id=brand_id, package_id=package_id, version=7)

    response = await _generate_post(
        pkg_db, account_id=account_id, brand_id=brand_id, generation_id=stamp_id
    )

    row = await pkg_db.fetchrow(
        "SELECT package_id, package_version FROM social.posts WHERE id = $1",
        uuid.UUID(response.data["post_id"]),
    )
    assert row["package_id"] == package_id
    assert row["package_version"] == 7
    consumed = await pkg_db.fetchval(
        "SELECT consumed_at FROM social.generation_stamps WHERE id = $1", stamp_id
    )
    assert consumed is not None, "makbuz tüketilmedi — tek kullanım işareti yazılmalı"


async def test_unpackaged_post_stamp_null(pkg_db, no_image_calls):
    """Paketsiz markada damga NULL ve olay üretilmez — normal yol sessizdir."""
    account_id, brand_id = await _seed_brand(pkg_db)

    response = await _generate_post(pkg_db, account_id=account_id, brand_id=brand_id)

    row = await pkg_db.fetchrow(
        "SELECT package_id, package_version FROM social.posts WHERE id = $1",
        uuid.UUID(response.data["post_id"]),
    )
    assert row["package_id"] is None and row["package_version"] is None
    events = await pkg_db.fetch(
        "SELECT event_type FROM social.package_events WHERE brand_id = $1", brand_id
    )
    assert events == [], "paketsiz üretim olay üretmez"


async def test_missing_generation_id_on_packaged_brand_logs_event(pkg_db, no_image_calls):
    """Paket yolundaki marka makbuzsuz kayıt yaparsa `stamp_missing` yazılır."""
    sub_id, _ = await _seed_sector_and_package(pkg_db)
    account_id, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)

    response = await _generate_post(pkg_db, account_id=account_id, brand_id=brand_id)

    row = await pkg_db.fetchrow(
        "SELECT package_id FROM social.posts WHERE id = $1",
        uuid.UUID(response.data["post_id"]),
    )
    assert row["package_id"] is None
    kinds = [
        r["event_type"]
        for r in await pkg_db.fetch(
            "SELECT event_type FROM social.package_events WHERE brand_id = $1", brand_id
        )
    ]
    assert kinds == ["stamp_missing"]


async def test_forged_generation_id_writes_null_and_alerts(pkg_db, no_image_calls):
    """Uydurulmuş makbuz kimliği damga YAZDIRMAZ; üretim de bloklanmaz."""
    sub_id, _ = await _seed_sector_and_package(pkg_db)
    account_id, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)

    response = await _generate_post(
        pkg_db, account_id=account_id, brand_id=brand_id, generation_id=uuid.uuid4()
    )

    row = await pkg_db.fetchrow(
        "SELECT package_id FROM social.posts WHERE id = $1",
        uuid.UUID(response.data["post_id"]),
    )
    assert row["package_id"] is None
    kinds = [
        r["event_type"]
        for r in await pkg_db.fetch(
            "SELECT event_type FROM social.package_events WHERE brand_id = $1", brand_id
        )
    ]
    assert kinds == ["stamp_invalid"]


async def test_cross_brand_generation_id_rejected(pkg_db, no_image_calls):
    """Başka markanın makbuzu bu markanın postuna TAKILAMAZ."""
    sub_id, package_id = await _seed_sector_and_package(pkg_db)
    _, other_brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)
    account_id, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)
    stolen = await _write_stamp(
        pkg_db, brand_id=other_brand_id, package_id=package_id, version=1
    )

    response = await _generate_post(
        pkg_db, account_id=account_id, brand_id=brand_id, generation_id=stolen
    )

    row = await pkg_db.fetchrow(
        "SELECT package_id FROM social.posts WHERE id = $1",
        uuid.UUID(response.data["post_id"]),
    )
    assert row["package_id"] is None
    still_unconsumed = await pkg_db.fetchval(
        "SELECT consumed_at FROM social.generation_stamps WHERE id = $1", stolen
    )
    assert still_unconsumed is None, "yabancı makbuz tüketilmemeli — sahibi hâlâ kullanabilmeli"


async def test_same_brand_replay_of_consumed_id_rejected(pkg_db, no_image_calls):
    """Aynı markanın TÜKETİLMİŞ makbuzu ikinci kez yazılamaz (replay)."""
    sub_id, package_id = await _seed_sector_and_package(pkg_db)
    account_id, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)
    stamp_id = await _write_stamp(pkg_db, brand_id=brand_id, package_id=package_id, version=1)

    first = await _generate_post(
        pkg_db, account_id=account_id, brand_id=brand_id, generation_id=stamp_id
    )
    second = await _generate_post(
        pkg_db, account_id=account_id, brand_id=brand_id, generation_id=stamp_id
    )

    first_row = await pkg_db.fetchrow(
        "SELECT package_id FROM social.posts WHERE id = $1",
        uuid.UUID(first.data["post_id"]),
    )
    second_row = await pkg_db.fetchrow(
        "SELECT package_id FROM social.posts WHERE id = $1",
        uuid.UUID(second.data["post_id"]),
    )
    assert first_row["package_id"] == package_id
    assert second_row["package_id"] is None, "yeniden kullanılan makbuz damga yazdırmamalı"
    kinds = [
        r["event_type"]
        for r in await pkg_db.fetch(
            "SELECT event_type FROM social.package_events WHERE brand_id = $1", brand_id
        )
    ]
    assert kinds == ["stamp_invalid"]


async def test_old_version_stamp_replay_to_new_post_rejected(pkg_db, no_image_calls):
    """Tüketilmiş ESKİ sürüm makbuzu yeni posta taşınamaz."""
    sub_id, package_id = await _seed_sector_and_package(pkg_db, version=1)
    account_id, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)
    stamp_id = await _write_stamp(pkg_db, brand_id=brand_id, package_id=package_id, version=1)
    await pkg_db.execute(
        "UPDATE social.generation_stamps SET consumed_at = now() WHERE id = $1", stamp_id
    )

    response = await _generate_post(
        pkg_db, account_id=account_id, brand_id=brand_id, generation_id=stamp_id
    )

    row = await pkg_db.fetchrow(
        "SELECT package_id FROM social.posts WHERE id = $1",
        uuid.UUID(response.data["post_id"]),
    )
    assert row["package_id"] is None


async def test_deactivation_between_stages_keeps_producing_stamp_and_logs_stale(
    pkg_db, no_image_calls
):
    """Aşamalar arası deaktivasyon: ÖZGÜN çift yazılır + `stamp_stale_at_persist`.

    Provenans dürüsttür: içeriği o paket üretti. Damgayı düşürmek üretimin
    gerçek kökenini silerdi; yeniden çözümlemek ise post'a onu üretmeyen bir
    paketi iliştirirdi. İkisi de yanlış; doğru olan özgün çifti yazıp durumu
    olay olarak kaydetmektir.
    """
    sub_id, package_id = await _seed_sector_and_package(pkg_db, version=4)
    account_id, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)
    stamp_id = await _write_stamp(pkg_db, brand_id=brand_id, package_id=package_id, version=4)
    await pkg_db.execute(
        "UPDATE social.sector_packages SET status = 'archived' WHERE id = $1", package_id
    )

    response = await _generate_post(
        pkg_db, account_id=account_id, brand_id=brand_id, generation_id=stamp_id
    )

    row = await pkg_db.fetchrow(
        "SELECT package_id, package_version FROM social.posts WHERE id = $1",
        uuid.UUID(response.data["post_id"]),
    )
    assert row["package_id"] == package_id and row["package_version"] == 4
    kinds = [
        r["event_type"]
        for r in await pkg_db.fetch(
            "SELECT event_type FROM social.package_events WHERE brand_id = $1", brand_id
        )
    ]
    assert kinds == ["stamp_stale_at_persist"]


async def test_concurrent_persists_with_same_id_single_winner(test_db_setup, monkeypatch):
    """İki eşzamanlı kayıt aynı makbuzla gelirse damgayı TEK kazanan alır.

    Tüketim koşullu güncellemedir ve kalıcı-kayıt transaction'ı içindedir;
    ikinci istek satırı tüketilmiş bulur, damga yazmaz ve olay üretir.
    """
    from .conftest import _require_test_database

    url = _require_test_database(test_db_setup)
    setup = await asyncpg.connect(url)
    await _init_connection(setup)

    workers: list = []
    account_id = brand_id = sub_id = None
    try:
        sub_id, package_id = await _seed_sector_and_package(setup)
        account_id, brand_id = await _seed_brand(setup, sub_sector_id=sub_id)
        stamp_id = await _write_stamp(
            setup, brand_id=brand_id, package_id=package_id, version=1
        )

        for _ in range(2):
            worker = await asyncpg.connect(url)
            await _init_connection(worker)
            workers.append(worker)

        from app.routers import posts as posts_router

        async def _fake_generate_image(*_args, **_kwargs):
            return "fake-job-id"

        monkeypatch.setattr(posts_router, "generate_image", _fake_generate_image)
        monkeypatch.setattr(posts_router, "generate_image_edit", _fake_generate_image)

        results = await asyncio.gather(
            *[
                _generate_post(
                    worker, account_id=account_id, brand_id=brand_id, generation_id=stamp_id
                )
                for worker in workers
            ]
        )

        stamped = await setup.fetch(
            "SELECT package_id FROM social.posts WHERE id = ANY($1::uuid[])",
            [uuid.UUID(r.data["post_id"]) for r in results],
        )
        winners = [r for r in stamped if r["package_id"] is not None]
        assert len(winners) == 1, f"tek kazanan olmalı, {len(winners)} damga yazıldı"
        kinds = [
            r["event_type"]
            for r in await setup.fetch(
                "SELECT event_type FROM social.package_events WHERE brand_id = $1", brand_id
            )
        ]
        assert kinds == ["stamp_invalid"], "kaybeden istek olay üretmeli"
    finally:
        for worker in workers:
            await worker.close()
        if brand_id:
            await setup.execute("DELETE FROM social.posts WHERE brand_id = $1", brand_id)
            await setup.execute("DELETE FROM social.brands WHERE id = $1", brand_id)
        if account_id:
            await setup.execute(
                "DELETE FROM social.workspace_members WHERE account_id = $1", account_id
            )
            await setup.execute(
                "DELETE FROM social.workspaces WHERE account_id = $1", account_id
            )
            await setup.execute("DELETE FROM social.accounts WHERE id = $1", account_id)
        if sub_id:
            await setup.execute(
                "DELETE FROM social.sector_packages WHERE sector_id = $1", sub_id
            )
            await setup.execute("DELETE FROM social.sectors WHERE id = $1", sub_id)
        await setup.close()


# ═══ 3. Task 8-11'in geçici logları kalıcı olay kaydına bağlandı ═══════════


async def test_stale_assignment_event_recorded(pkg_db):
    """Bayat atama (`draft`/`archived`) kalıcı olay üretir — yalnız log değil."""
    sub_id, _ = await _seed_sector_and_package(pkg_db, status="archived")
    _, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)

    result = await resolve_package_context(
        pkg_db, {"id": brand_id, "sub_sector_id": sub_id}
    )

    assert result is None
    kinds = [
        r["event_type"]
        for r in await pkg_db.fetch(
            "SELECT event_type FROM social.package_events WHERE brand_id = $1", brand_id
        )
    ]
    assert kinds == ["stale_assignment_fallback"]


async def test_package_read_error_recorded_when_only_the_read_fails(pkg_db):
    """Okuma hatası kalıcı olarak kaydedilir — hata bağlantıdan gelmiyorsa."""
    sub_id, _ = await _seed_sector_and_package(pkg_db)
    _, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)

    class _ReadFails:
        """Yalnız paket sorgusunu düşürür; bağlantı sağlam kalır."""

        def __init__(self, real):
            self._real = real

        def __getattr__(self, name):
            return getattr(self._real, name)

        async def fetchrow(self, *_args, **_kwargs):
            raise RuntimeError("okuma düştü")

    result = await resolve_package_context(
        _ReadFails(pkg_db), {"id": brand_id, "sub_sector_id": sub_id}
    )

    assert result is None
    rows = await pkg_db.fetch(
        "SELECT event_type, detail FROM social.package_events WHERE brand_id = $1", brand_id
    )
    assert [r["event_type"] for r in rows] == ["package_read_error"]
    assert rows[0]["detail"] == {"reason": "read_failed", "error": "RuntimeError"}


async def test_package_read_error_degrades_to_log_when_db_is_down(caplog):
    """BELGELİ SINIR: veritabanının kendisi erişilemezse olay da yazılamaz.

    Plan Task 12 bu sınırı açıkça tanır — o durumda bağımsız best-effort kanal
    `logger`'dır. Test bunu bir eksiklik olarak değil, ÖLÇÜLMÜŞ ve belgelenmiş
    davranış olarak pinler: sessizce kaybolmadığını (log üretildiğini) ve
    çağıranın DÜŞMEDİĞİNİ (None döndüğünü) kanıtlar.
    """

    class _DeadConnection:
        async def fetchrow(self, *_args, **_kwargs):
            raise RuntimeError("bağlantı yok")

        async def fetchval(self, *_args, **_kwargs):
            raise RuntimeError("bağlantı yok")

    with caplog.at_level(logging.ERROR):
        result = await resolve_package_context(
            _DeadConnection(), {"id": uuid.uuid4(), "sub_sector_id": uuid.uuid4()}
        )

    assert result is None
    assert any(
        "paket olayı yazılamadı" in r.getMessage() for r in caplog.records
    ), "olay yazımı başarısızlığı sessiz kalmamalı"


async def test_quote_flow_without_caption_call_logs_no_event(pkg_db, no_image_calls):
    """Caption çağrısı YAPMAYAN akışta makbuz yokluğu anomali DEĞİLDİR.

    Alıntı akışı `/generate-caption`'a hiç uğramaz; makbuz doğmaz. `stamp_missing`
    "beklenen makbuz gelmedi" demektir — hiç beklenmediği yerde yazılırsa denetim
    izi yanlış konuşur ve gerçek eksiklikler gürültüde kaybolur.
    """
    from app.models.schemas import PostGenerate
    from app.routers import posts as posts_router

    sub_id, _ = await _seed_sector_and_package(pkg_db)
    account_id, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)

    await posts_router.generate_post(
        payload=PostGenerate(
            brand_id=brand_id,
            content_type="quote",
            quote_text="Kısa bir alıntı.",
            platforms=["instagram"],
        ),
        user={"sub": str(account_id)},
        db=pkg_db,
    )

    events = await pkg_db.fetch(
        "SELECT event_type FROM social.package_events WHERE brand_id = $1", brand_id
    )
    assert events == [], "caption üretmeyen akış makbuz olayı üretmemeli"


# ═══ 4. İstemci taşıması — yapısal kapı ════════════════════════════════════

FRONTEND_DIR = (
    __import__("pathlib").Path(__file__).resolve().parents[2] / "frontend"
)


def _persist_payloads() -> list[tuple[str, str]]:
    """Üretim sayfasındaki kalıcı-kayıt isteklerinin gövdelerini çıkarır."""
    import re

    page = (FRONTEND_DIR / "app/(dashboard)/icerik-olustur/page.tsx").read_text("utf-8")
    bodies = []
    for match in re.finditer(r"api\.post<[^>]*>\('(/posts/[^']+)',\s*\{", page):
        depth = 1
        i = match.end()
        while i < len(page) and depth:
            depth += {"{": 1, "}": -1}.get(page[i], 0)
            i += 1
        bodies.append((match.group(1), page[match.end() : i]))
    return bodies


def test_every_caption_first_persist_request_carries_the_receipt():
    """Caption çağrısının ucundaki HER kalıcı-kayıt isteği makbuzu taşır (K-07).

    Beklenen küme sabit listeyle değil, isteğin KENDİSİNDEN türetilir:
    `platform_captions` gönderen istek caption çağrısının ucundadır, dolayısıyla
    makbuzu da taşımalıdır. Yeni bir caption-öncüllü akış eklenirse bu kapı onu
    liste güncellemeden yakalar.

    **Dürüst etiket: bu YAPISAL bir kapıdır, davranışsal değil.** İsteğin gerçek
    gövdesinde alanın gittiğini kanıtlamaz; kanıtı gerçek arayüz koşumudur
    (kuyumculuk pilotu). Checkpoint 11'de tam bu halka koptuğu ve hiçbir birim
    testi görmediği için kapı yine de kuruluyor.
    """
    payloads = _persist_payloads()
    assert payloads, "kalıcı-kayıt isteği bulunamadı — yapısal sweep boşa koştu"

    caption_first = [
        (endpoint, body) for endpoint, body in payloads if "platform_captions" in body
    ]
    assert caption_first, "caption-öncüllü istek bulunamadı — sweep duyarsız"
    for endpoint, body in caption_first:
        assert "generation_id" in body, (
            f"{endpoint}: caption-öncüllü istek makbuzu taşımıyor — "
            "paketli üretim damgasız kaydedilir"
        )


def test_caption_response_handler_preserves_the_receipt():
    """Caption yanıtındaki makbuz istemci durumunda KORUNUR.

    Zincirin ilk halkası: yanıt alanı `captionData`'ya yazılmazsa sonraki
    isteklere hiç ulaşmaz. Checkpoint 11 F1 tam olarak buydu (hareket seçimi
    yeniden kurulan nesnede düşüyordu).
    """
    page = (FRONTEND_DIR / "app/(dashboard)/icerik-olustur/page.tsx").read_text("utf-8")
    assert "res.data.generation_id" in page, (
        "caption yanıtındaki makbuz istemci durumuna hiç yazılmıyor"
    )
    editor = (FRONTEND_DIR / "components/templates/CaptionEditor.tsx").read_text("utf-8")
    assert "generation_id" in editor, "CaptionData tipi makbuzu taşımıyor"


# ═══ 5. İkinci kalıcı-kayıt ucu — kısa video stage-1 ═══════════════════════


async def _run_stage1(db, *, brand_id, sub_sector_id, generation_id, monkeypatch):
    """Stage-1'i ÜRETİM yolundan koşar; yalnız dış dünya kesilir."""
    from app.services import short_video as sv

    async def _fake_tts(*_a, **_k):
        return {"audio_url": "https://example.test/a.mp3"}

    async def _fake_still_text(*_a, **_k):
        return "https://example.test/still.jpg"

    async def _fake_still_prompt(*_a, **_k):
        return "A gold ring on velvet"

    monkeypatch.setattr(sv, "text_to_speech", _fake_tts)
    monkeypatch.setattr(sv, "_generate_still_via_text", _fake_still_text)
    monkeypatch.setattr(sv, "_generate_still_via_edit", _fake_still_text)
    monkeypatch.setattr(sv, "_resolve_still_prompt", _fake_still_prompt)

    return await sv.run_short_video_stage1(
        brand_id=brand_id,
        prompt="A gold ring on velvet",
        script="Kısa bir senaryo metni.",
        voice="qSeXEcewz7tA0Q0qk9fH",
        aspect_ratio="9:16",
        brand_kit={"sector": "Kuyumculuk"},
        brand_name="Damga Markası",
        db=db,
        platform_captions={"instagram": {"caption": "x"}},
        sub_sector_id=sub_sector_id,
        generation_id=generation_id,
    )


async def test_stage1_persist_writes_recorded_stamp(pkg_db, monkeypatch):
    """Kısa videonun kalıcı kaydı da makbuzu tüketip damgayı yazar.

    İKİNCİ kalıcı-kayıt ucudur ve ayrı sınanır. Bu yürütmede iki kez ölçüldü:
    bir yolu test edip diğerini varsaymak, yönlendiricide ayrılan gerçek ürün
    yolunu gözden kaçırıyor.
    """
    sub_id, package_id = await _seed_sector_and_package(pkg_db, version=5)
    _, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)
    stamp_id = await _write_stamp(pkg_db, brand_id=brand_id, package_id=package_id, version=5)

    result = await _run_stage1(
        pkg_db,
        brand_id=brand_id,
        sub_sector_id=sub_id,
        generation_id=stamp_id,
        monkeypatch=monkeypatch,
    )

    row = await pkg_db.fetchrow(
        "SELECT package_id, package_version FROM social.posts WHERE id = $1",
        result["post_id"],
    )
    assert row["package_id"] == package_id
    assert row["package_version"] == 5
    assert await pkg_db.fetchval(
        "SELECT consumed_at FROM social.generation_stamps WHERE id = $1", stamp_id
    ) is not None


async def test_stage1_forged_receipt_writes_null_and_alerts(pkg_db, monkeypatch):
    """Stage-1'de de uydurulmuş makbuz damga YAZDIRMAZ; video yine üretilir."""
    sub_id, _ = await _seed_sector_and_package(pkg_db)
    _, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)

    result = await _run_stage1(
        pkg_db,
        brand_id=brand_id,
        sub_sector_id=sub_id,
        generation_id=uuid.uuid4(),
        monkeypatch=monkeypatch,
    )

    row = await pkg_db.fetchrow(
        "SELECT package_id FROM social.posts WHERE id = $1", result["post_id"]
    )
    assert row["package_id"] is None
    kinds = [
        r["event_type"]
        for r in await pkg_db.fetch(
            "SELECT event_type FROM social.package_events WHERE brand_id = $1", brand_id
        )
    ]
    assert kinds == ["stamp_invalid"]


# ═══ 6. Checkpoint 12 bulgularının regresyon kapıları ══════════════════════


async def test_special_day_mismatch_records_the_event(pkg_db):
    """Özel gün EŞLEŞMEZLİĞİ kalıcı olay üretir (spec §14.4 "eşleşmezlik log'u").

    Spec iki ayrı kalem sayıyor: *eşleşmezlik* ve *okuma/doğrulama hatası*.
    Eşleşmezlik, istenen özel günün pakette karşılığı olmamasıdır — paketin
    kendisi sağlamdır, yalnız o gün yoktur. İlk yazımda bu olay yanlışlıkla
    yapısal geçersizlik dalına bağlanmıştı; o dal bir DOĞRULAMA hatasıdır ve
    kendi olayına aittir. Yanlış etiket, işletimde "paket bozuk" ile "bu gün
    pakette yok"u aynı kutuya koyardı.
    """
    from app.routers import posts as posts_router
    from app.routers.posts import GenerateCaptionRequest

    sub_id, package_id = await _seed_sector_and_package(pkg_db)
    account_id, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)

    async def _fake_captions(**_kwargs):
        return {
            "default_caption": "x",
            "platform_captions": {},
            "image_prompt": "x",
            "hashtags": [],
        }

    import app.routers.posts as _posts
    original = _posts.generate_captions
    _posts.generate_captions = _fake_captions
    try:
        await posts_router.generate_caption(
            payload=GenerateCaptionRequest(
                brand_id=brand_id,
                platforms=["instagram"],
                special_day_name="Bilinmeyen Uydurma Günü",
                special_day_category="commercial",
            ),
            user={"sub": str(account_id)},
            db=pkg_db,
        )
    finally:
        _posts.generate_captions = original

    rows = await pkg_db.fetch(
        "SELECT event_type, package_id FROM social.package_events WHERE brand_id = $1",
        brand_id,
    )
    assert [r["event_type"] for r in rows] == ["mismatch_fallthrough"]
    assert rows[0]["package_id"] == package_id


async def test_structurally_invalid_package_is_a_validation_error(pkg_db):
    """Yapısal geçersizlik DOĞRULAMA hatasıdır, eşleşmezlik DEĞİL."""
    sub_id, package_id = await _seed_sector_and_package(pkg_db)
    await pkg_db.execute(
        "UPDATE social.sector_packages SET content = $2 WHERE id = $1",
        package_id,
        {"kapsam": "yalnız kapsam var, gerisi eksik"},
    )
    _, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)

    result = await resolve_package_context(pkg_db, {"id": brand_id, "sub_sector_id": sub_id})

    assert result is None
    rows = await pkg_db.fetch(
        "SELECT event_type, detail FROM social.package_events WHERE brand_id = $1", brand_id
    )
    assert [r["event_type"] for r in rows] == ["package_read_error"]
    assert rows[0]["detail"]["reason"] == "structural"


@pytest.mark.parametrize(
    "captions",
    [pytest.param(None, id="alan-yok"), pytest.param({}, id="boş-sözlük")],
)
async def test_receipt_expectation_is_not_client_suppressible(
    pkg_db, no_image_calls, captions
):
    """İstemci OPSİYONEL bir alanı düşürerek denetim izini SUSTURAMAZ.

    Makbuz beklentisi, istemcinin gönderip göndermemekte serbest olduğu bir
    alandan türetilemez: `platform_captions` boş ya da yok gönderilirse paketli
    bir marka damgasız kayıt yapar ve olay hiç yazılmazdı — fail-open. Beklenti
    artık içerik türünden okunuyor; bilinmeyen tür de BEKLENİR sayılır
    (fail-closed yön).
    """
    from app.models.schemas import PostGenerate
    from app.routers import posts as posts_router

    sub_id, _ = await _seed_sector_and_package(pkg_db)
    account_id, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)

    await posts_router.generate_post(
        payload=PostGenerate(
            brand_id=brand_id,
            content_type="image",
            image_prompt="A gold ring on velvet",
            platforms=["instagram"],
            platform_captions=captions,
        ),
        user={"sub": str(account_id)},
        db=pkg_db,
    )

    kinds = [
        r["event_type"]
        for r in await pkg_db.fetch(
            "SELECT event_type FROM social.package_events WHERE brand_id = $1", brand_id
        )
    ]
    assert kinds == ["stamp_missing"]


async def test_stage1_failure_leaves_the_receipt_reusable(pkg_db, monkeypatch):
    """Stage-1 dış dünyada patlarsa makbuz YANMAZ — yeniden deneme damgalanır.

    Ölçüldü (düzeltmeden önce): makbuz post yazımıyla birlikte, TTS ve still
    üretiminden ÖNCE tüketiliyordu. TTS patlayınca post `failed` oluyor, arayüz
    kullanıcıyı adım 2'ye geri atıyor ve AYNI `generation_id` ile tekrar
    deneniyor — ikinci istek makbuzu tüketilmiş buluyor, başarılı video
    DAMGASIZ kalıyor ve damga başarısız postun üstünde kalıyordu.

    Kural: makbuz, üretimin KALICI BAŞARI noktasında tüketilir.
    """
    from app.services import short_video as sv

    sub_id, package_id = await _seed_sector_and_package(pkg_db, version=2)
    _, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)
    stamp_id = await _write_stamp(pkg_db, brand_id=brand_id, package_id=package_id, version=2)

    async def _tts_fails(*_a, **_k):
        return {"audio_url": ""}

    monkeypatch.setattr(sv, "text_to_speech", _tts_fails)
    monkeypatch.setattr(sv, "_resolve_still_prompt", lambda *_a, **_k: _noop_prompt())

    with pytest.raises(RuntimeError):
        await sv.run_short_video_stage1(
            brand_id=brand_id,
            prompt="A gold ring on velvet",
            script="Kısa bir senaryo metni.",
            voice="qSeXEcewz7tA0Q0qk9fH",
            aspect_ratio="9:16",
            brand_kit={"sector": "Kuyumculuk"},
            brand_name="Damga Markası",
            db=pkg_db,
            platform_captions={"instagram": {"caption": "x"}},
            sub_sector_id=sub_id,
            generation_id=stamp_id,
        )

    assert await pkg_db.fetchval(
        "SELECT consumed_at FROM social.generation_stamps WHERE id = $1", stamp_id
    ) is None, "başarısız koşum makbuzu YAKTI — yeniden deneme damgalanamaz"
    assert await pkg_db.fetchval(
        "SELECT count(*) FROM social.posts WHERE brand_id = $1 AND package_id IS NOT NULL",
        brand_id,
    ) == 0, "başarısız post damga taşıyor"

    # Yeniden deneme: bu kez dış dünya çalışıyor → damga BU posta yazılır.
    result = await _run_stage1(
        pkg_db,
        brand_id=brand_id,
        sub_sector_id=sub_id,
        generation_id=stamp_id,
        monkeypatch=monkeypatch,
    )
    row = await pkg_db.fetchrow(
        "SELECT package_id, package_version FROM social.posts WHERE id = $1",
        result["post_id"],
    )
    assert row["package_id"] == package_id and row["package_version"] == 2
    kinds = [
        r["event_type"]
        for r in await pkg_db.fetch(
            "SELECT event_type FROM social.package_events WHERE brand_id = $1", brand_id
        )
    ]
    assert kinds == [], "başarılı yeniden deneme sahte bir olay üretmemeli"


async def _noop_prompt():
    return "A gold ring on velvet"


async def test_stage1_publishes_and_stamps_atomically(pkg_db, monkeypatch):
    """Onaya AÇILMA ile damga yazımı TEK transaction'dadır (tur 2, F4).

    Post artık `generating` olarak yazılıyor ve `awaiting_approval`a YALNIZ damga
    transaction'ında geçiyor. Aksi hâlde ikisi arasında bir çöküş, stage-2'ye
    uygun ama damgasız bir post bırakır ve makbuz hâlâ kullanılabilir olurdu —
    aynı makbuz sonra BAŞKA bir postu damgalayabilirdi (sahte soyağacı).
    """
    from app.services import short_video as sv
    from app.services import sector_packages as sp

    sub_id, package_id = await _seed_sector_and_package(pkg_db, version=3)
    _, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)
    stamp_id = await _write_stamp(pkg_db, brand_id=brand_id, package_id=package_id, version=3)

    # (a) Sonlandırma patlarsa: post onaya AÇILMAZ, makbuz YANMAZ.
    async def _boom(*_a, **_k):
        raise RuntimeError("sonlandırma düştü")

    monkeypatch.setattr(sv, "resolve_persist_stamp", _boom)
    with pytest.raises(RuntimeError):
        await _run_stage1(
            pkg_db,
            brand_id=brand_id,
            sub_sector_id=sub_id,
            generation_id=stamp_id,
            monkeypatch=monkeypatch,
        )

    rows = await pkg_db.fetch(
        "SELECT status, package_id FROM social.posts WHERE brand_id = $1", brand_id
    )
    assert [r["status"] for r in rows] == ["generating"], (
        "sonlandırma patladı ama post stage-2'ye uygun kaldı"
    )
    assert rows[0]["package_id"] is None
    assert await pkg_db.fetchval(
        "SELECT consumed_at FROM social.generation_stamps WHERE id = $1", stamp_id
    ) is None, "sonlandırma patladı ama makbuz yandı"

    # (b) Başarılı koşum: onaya açılma ve damga BİRLİKTE gelir.
    monkeypatch.setattr(sv, "resolve_persist_stamp", sp.resolve_persist_stamp)
    result = await _run_stage1(
        pkg_db,
        brand_id=brand_id,
        sub_sector_id=sub_id,
        generation_id=stamp_id,
        monkeypatch=monkeypatch,
    )
    row = await pkg_db.fetchrow(
        "SELECT status, package_id, package_version FROM social.posts WHERE id = $1",
        result["post_id"],
    )
    assert row["status"] == "awaiting_approval"
    assert row["package_id"] == package_id and row["package_version"] == 3


async def test_finalization_refuses_to_resurrect_a_swept_post(pkg_db, monkeypatch):
    """Sonlandırma, süpürücünün TERMİNAL kararını geri alamaz (tur 3, M1).

    Yeni `generating` başlangıcı postu bayat-iş süpürücüsünün 10 dakikalık
    penceresine sokuyor. Sonlandırma koşulsuz `UPDATE ... WHERE id` yapsaydı,
    süpürücü postu `failed` yaptıktan sonra stage-1 onu diriltip onaya açardı —
    üstelik silinmiş bir postta güncelleme sessizce hiçbir satıra dokunmaz ve
    makbuz KARŞILIĞI OLMAYAN bir kayıt için tüketilirdi (öksüz makbuz).

    Kural: sonlandırma karşılaştır-ve-yaz'dır; satır `generating` değilse
    transaction geri alınır ve makbuz yanmaz.
    """
    from app.services import short_video as sv

    sub_id, package_id = await _seed_sector_and_package(pkg_db)
    _, brand_id = await _seed_brand(pkg_db, sub_sector_id=sub_id)
    stamp_id = await _write_stamp(pkg_db, brand_id=brand_id, package_id=package_id, version=1)

    async def _still_then_sweep(*_a, **_k):
        # Süpürücünün araya girmesini temsil eder: still üretimi sürerken
        # post terminal duruma çekilir.
        await pkg_db.execute(
            "UPDATE social.posts SET status = 'failed' WHERE brand_id = $1", brand_id
        )
        return "https://example.test/still.jpg"

    async def _fake_tts(*_a, **_k):
        return {"audio_url": "https://example.test/a.mp3"}

    async def _fake_still_prompt(*_a, **_k):
        return "A gold ring on velvet"

    # `_run_stage1` yardımcısı KULLANILMIYOR: o, still üreticisini kendi sahtesiyle
    # eziyor ve bu testin tam olarak oraya yerleştirdiği araya-girmeyi silerdi.
    monkeypatch.setattr(sv, "text_to_speech", _fake_tts)
    monkeypatch.setattr(sv, "_resolve_still_prompt", _fake_still_prompt)
    monkeypatch.setattr(sv, "_generate_still_via_text", _still_then_sweep)

    with pytest.raises(RuntimeError):
        await sv.run_short_video_stage1(
            brand_id=brand_id,
            prompt="A gold ring on velvet",
            script="Kısa bir senaryo metni.",
            voice="qSeXEcewz7tA0Q0qk9fH",
            aspect_ratio="9:16",
            brand_kit={"sector": "Kuyumculuk"},
            brand_name="Damga Markası",
            db=pkg_db,
            platform_captions={"instagram": {"caption": "x"}},
            sub_sector_id=sub_id,
            generation_id=stamp_id,
        )

    statuses = [
        r["status"]
        for r in await pkg_db.fetch(
            "SELECT status FROM social.posts WHERE brand_id = $1", brand_id
        )
    ]
    assert statuses == ["failed"], "süpürülmüş post diriltildi"
    assert await pkg_db.fetchval(
        "SELECT consumed_at FROM social.generation_stamps WHERE id = $1", stamp_id
    ) is None, "karşılığı olmayan kayıt için makbuz tüketildi (öksüz makbuz)"


def test_library_polling_reconciles_backend_changeable_states():
    """Yoklama kümesi, arka ucun HÂLÂ değiştirebileceği satırları kapsar (tur 4).

    İki ayrı gerileme burada birden pinleniyor ve ikisi de benim açtığım:

    1. Değişim ölçüsü yalnız `output_url` idi. Kısa video stage-1 çıktı URL'si
       ÜRETMEDEN bitiyor; o satır sonsuza kadar `generating` görünüp her 3
       saniyede bir istek atıyordu (tur 3, M2).
    2. Düzeltirken `failed` satırlarını yoklama kümesinden ÇIKARDIM. Ama arka
       uçta `failed` terminal DEĞİL: bayat-iş süpürücüsü 10 dakikayı aşan bir
       üretimi `failed` yapıyor, fal.ai webhook'u geç gelen başarıyı sonradan
       `ready` + `output_url` yazabiliyor. Kullanıcı başarısız görünen ama
       aslında hazır olan bir içerikle kalırdı (tur 4).

    **Dürüst etiket: YAPISAL kapı.** Gerçek yoklama davranışı bu suite'ten
    ölçülemez (JS koşucusu yok). Kapının pinlediği şey, yoklama kümesinin
    `failed`i kapsaması ve değişim ölçüsünün `status`u içermesidir.

    **Altta çözülmemiş bir tutarsızlık var ve etiketi dürüst:** süpürücü
    "başarısız" derken webhook aynı satırı "hazır" yapabiliyor. Bu bir ÜRÜN
    kararıdır (geç gelen başarı kabul edilsin mi) ve Task 12'nin kapsamı
    DIŞINDADIR — burada yalnız arayüzün arka uçla tutarlı kalması sağlandı.
    """
    import re

    page = (FRONTEND_DIR / "app/(dashboard)/icerik-kutuphanesi/page.tsx").read_text("utf-8")
    match = re.search(r"const generatingIds = posts.*?\}, 3000\)", page, re.S)
    assert match, "yoklama efekti bulunamadı — yapısal sweep boşa koştu"
    block = match.group(0)
    assert "status" in block, (
        "yoklama yalnız output_url'e bakıyor — çıktı üretmeden biten üretim "
        "sonsuza kadar 'generating' görünür"
    )
    assert "'failed'" in block, (
        "yoklama `failed` satırlarını uzlaştırmıyor — geç gelen webhook başarısı "
        "arayüze hiç yansımaz"
    )
