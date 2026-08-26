"""Bildirim mekanizması — transactional outbox + kira protokolü (plan Task 14).

Bu dosyanın ölçtüğü dört sözleşme:

1. **Outbox iş transaction'ıyla BİRLİKTE commit edilir.** Olayı doğuran iş geri
   alınırsa bildirim de yoktur; "gerçekleşmemiş bir şey haber verildi" durumu
   doğamaz.
2. **Deneme bütçesi CLAIM anında tükenir (F19).** Kira, gönderim ve çökme
   pencereleri ne olursa olsun fiziksel gönderim sayısı sınırlıdır. Bütçeyi
   finalize'da düşürmek, claim'den sonra çöken işçiye bedava deneme verirdi ve
   "sınırlı yeniden deneme" hükmü yalan olurdu.
3. **Aktif kira ASLA süpürülmez (F20).** Üçüncü deneme canlıyken satırı
   `failed`e çekmek, yolda olan başarılı bir teslimi kaybetmek demektir.
4. **Bildirim başarısızlığı üretimi ASLA bloklamaz.** Outbox yazımı patlarsa
   olay kaydı ve üretim akışı ayakta kalır.

Kira jetonu ayrı bir kolon DEĞİL, `(attempt_count, lease_expires_at)` çiftidir:
her claim `attempt_count`'u atomik artırdığı için yeniden claim edilen satırın
çifti kesin olarak değişir ve bayat işçi finalize edemez.
"""

from __future__ import annotations

import asyncio
import uuid

import asyncpg as _asyncpg
import pytest
from fastapi import HTTPException

from app.core.database import _init_connection
from app.core.security import get_service_auth
from app.routers import brands as brands_router
from app.routers import internal as internal_router
from app.services import notifications
from app.services.notifications import (
    MAINTENANCE_BANNER_MESSAGE,
    MAX_DELIVERY_ATTEMPTS,
    claim_admin_events,
    dispatch_pending_admin_events,
    finalize_admin_event,
    record_admin_event,
    sweep_exhausted_admin_events,
)
from app.services.package_events import log_package_event

from .conftest import _require_test_database

KIND = "package_event.stale_assignment_fallback"


# ─── Ortak yardımcılar ──────────────────────────────────────────────────────


@pytest.fixture
async def notif_db(db):
    """Üretimin kendi bağlantı yapılandırması (jsonb codec)."""
    await _init_connection(db)
    return db


def _key() -> str:
    return f"test:{uuid.uuid4()}"


async def _seed_event(db, *, kind: str = KIND, payload: dict | None = None) -> uuid.UUID:
    return await record_admin_event(
        db,
        kind=kind,
        payload=payload if payload is not None else {"brand_id": str(uuid.uuid4())},
        idempotency_key=_key(),
    )


async def _row(db, event_id) -> dict:
    row = await db.fetchrow("SELECT * FROM social.admin_events WHERE id = $1", event_id)
    assert row is not None, "outbox satırı bulunamadı"
    return dict(row)


async def _expire_lease(db, event_id) -> None:
    await db.execute(
        "UPDATE social.admin_events SET lease_expires_at = now() - interval '1 second' "
        "WHERE id = $1",
        event_id,
    )


class _Sender:
    """Gönderimi kaydeden sahte kanal; `fail=True` ise her çağrıda düşer."""

    def __init__(self, *, fail: bool = False, delay: float = 0.0):
        self.fail = fail
        self.delay = delay
        self.calls: list[dict] = []

    async def __call__(self, envelope: dict) -> None:
        if self.delay:
            await asyncio.sleep(self.delay)
        self.calls.append(envelope)
        if self.fail:
            raise RuntimeError("n8n erişilemedi")


# ─── 1. Outbox yazımı ───────────────────────────────────────────────────────


async def test_admin_event_committed_with_business_transaction(test_db_setup):
    """İş transaction'ı geri alınırsa outbox satırı da YOKTUR.

    Outbox'ın tek varlık sebebi budur: bildirim, haber verdiği işle aynı
    kaderi paylaşır. Ayrı bir kanal (doğrudan webhook) olsaydı geri alınan bir
    işin bildirimi yola çıkmış olurdu.
    """
    url = _require_test_database(test_db_setup)
    conn = await _asyncpg.connect(url)
    await _init_connection(conn)
    committed_key = _key()
    rolled_key = _key()
    try:
        transaction = conn.transaction()
        await transaction.start()
        rolled_id = await record_admin_event(
            conn, kind=KIND, payload={"a": 1}, idempotency_key=rolled_key
        )
        await transaction.rollback()
        assert await conn.fetchval(
            "SELECT count(*) FROM social.admin_events WHERE id = $1", rolled_id
        ) == 0

        transaction = conn.transaction()
        await transaction.start()
        kept_id = await record_admin_event(
            conn, kind=KIND, payload={"a": 1}, idempotency_key=committed_key
        )
        await transaction.commit()
        assert await conn.fetchval(
            "SELECT delivery_state FROM social.admin_events WHERE id = $1", kept_id
        ) == "pending"
    finally:
        await conn.execute(
            "DELETE FROM social.admin_events WHERE idempotency_key = ANY($1::text[])",
            [committed_key, rolled_key],
        )
        await conn.close()


async def test_admin_event_every_occurrence_no_threshold(notif_db):
    """Eşik/oran YOK — aynı türden üç oluş, üç outbox satırı (K-56)."""
    ids = [await _seed_event(notif_db) for _ in range(3)]

    assert len(set(ids)) == 3
    assert await notif_db.fetchval(
        "SELECT count(*) FROM social.admin_events WHERE id = ANY($1::uuid[])", ids
    ) == 3


async def test_duplicate_dispatch_deduped_by_idempotency_key(notif_db):
    """Aynı anahtarla ikinci yazım YENİ satır üretmez, mevcut kimliği döner."""
    key = _key()
    first = await record_admin_event(
        notif_db, kind=KIND, payload={"n": 1}, idempotency_key=key
    )
    second = await record_admin_event(
        notif_db, kind=KIND, payload={"n": 2}, idempotency_key=key
    )

    assert first == second
    assert await notif_db.fetchval(
        "SELECT count(*) FROM social.admin_events WHERE idempotency_key = $1", key
    ) == 1
    # İlk yazım kazanır — ikinci çağrı payload'ı EZMEZ.
    assert (await _row(notif_db, first))["payload"] == {"n": 1}


async def test_package_read_error_triggers_admin_event(notif_db):
    """K-56 bağlaması: paket okuma hatası HER OLUŞTA outbox satırı üretir.

    Bağ tek kapıdadır (`log_package_event`), çağrı yerlerinde değil: yeni bir
    çağrı yeri eklendiğinde bildirimi ayrıca hatırlamak gerekmesin diye.
    """
    brand_id = await _seed_brand(notif_db)

    event_id = await log_package_event(
        notif_db,
        event_type="package_read_error",
        brand_id=brand_id,
        detail={"reason": "structural"},
    )

    row = await notif_db.fetchrow(
        "SELECT * FROM social.admin_events WHERE idempotency_key = $1",
        f"package_event:{event_id}",
    )
    assert row is not None, "paket okuma hatası outbox satırı üretmedi"
    assert row["kind"] == "package_event.package_read_error"
    assert dict(row["payload"])["event_id"] == str(event_id)
    assert dict(row["payload"])["brand_id"] == str(brand_id)


async def test_notification_failure_does_not_block(notif_db, monkeypatch):
    """Outbox yazımı patlasa bile olay kaydı ve akış ayakta kalır."""
    brand_id = await _seed_brand(notif_db)

    async def _boom(*args, **kwargs):
        raise RuntimeError("outbox erişilemedi")

    monkeypatch.setattr(notifications, "record_admin_event", _boom)

    event_id = await log_package_event(
        notif_db,
        event_type="mismatch_fallthrough",
        brand_id=brand_id,
        detail={"reason": "no_match"},
    )

    assert event_id is not None, "bildirim hatası olay kaydını düşürdü"
    assert await notif_db.fetchval(
        "SELECT count(*) FROM social.package_events WHERE id = $1", event_id
    ) == 1


# ─── 2. Şema ────────────────────────────────────────────────────────────────


async def test_schema_accepts_sending_state_and_lease(notif_db):
    """`sending` bir KİRA durumudur: durum kapalı kümede, kira kolonu var."""
    event_id = await _seed_event(notif_db)
    await notif_db.execute(
        "UPDATE social.admin_events SET delivery_state = 'sending', "
        "lease_expires_at = now() + interval '5 minutes' WHERE id = $1",
        event_id,
    )

    row = await _row(notif_db, event_id)
    assert row["delivery_state"] == "sending"
    assert row["lease_expires_at"] is not None

    with pytest.raises(asyncpg_errors()):
        await notif_db.execute(
            "UPDATE social.admin_events SET delivery_state = 'yolda' WHERE id = $1",
            event_id,
        )


def asyncpg_errors():
    from asyncpg.exceptions import CheckViolationError

    return CheckViolationError


# ─── 3. Kira protokolü — claim / send / finalize ────────────────────────────


async def test_attempt_budget_consumed_at_claim_bounded_sends(notif_db):
    """F19: claim = kalıcı deneme. Üç claim/çökme penceresi bütçeyi bitirir.

    Bütçe finalize'da düşseydi, claim'den sonra çöken işçi hiçbir bedel
    ödemeden satırı serbest bırakır ve gönderim sayısı sınırsız olurdu.
    """
    event_id = await _seed_event(notif_db)

    for expected_attempt in range(1, MAX_DELIVERY_ATTEMPTS + 1):
        claimed = await claim_admin_events(notif_db, lease_seconds=60)
        assert [c["id"] for c in claimed] == [event_id]
        assert claimed[0]["attempt_count"] == expected_attempt
        await _expire_lease(notif_db, event_id)  # çökme: finalize hiç koşmadı

    assert (await _row(notif_db, event_id))["attempt_count"] == MAX_DELIVERY_ATTEMPTS
    assert await claim_admin_events(notif_db, lease_seconds=60) == []


async def test_exhausted_row_not_claimable(notif_db):
    """Bütçesi bitmiş satır claim edilemez — kirası dolmuş olsa bile."""
    event_id = await _seed_event(notif_db)
    await notif_db.execute(
        "UPDATE social.admin_events SET attempt_count = $2, "
        "delivery_state = 'sending', lease_expires_at = now() - interval '1 minute' "
        "WHERE id = $1",
        event_id,
        MAX_DELIVERY_ATTEMPTS,
    )

    assert await claim_admin_events(notif_db, lease_seconds=60) == []


async def test_active_lease_not_reclaimed(notif_db):
    """Kirası SÜREN satır ikinci kez claim edilmez."""
    event_id = await _seed_event(notif_db)
    first = await claim_admin_events(notif_db, lease_seconds=600)
    assert [c["id"] for c in first] == [event_id]

    assert await claim_admin_events(notif_db, lease_seconds=600) == []


async def test_crash_after_claim_expired_lease_reclaimed(notif_db):
    """Claim sonrası çökme: kira dolunca satır yeniden claim edilir."""
    event_id = await _seed_event(notif_db)
    await claim_admin_events(notif_db, lease_seconds=600)
    await _expire_lease(notif_db, event_id)

    again = await claim_admin_events(notif_db, lease_seconds=600)
    assert [c["id"] for c in again] == [event_id]
    assert again[0]["attempt_count"] == 2


async def test_stale_worker_cannot_finalize(notif_db):
    """Bayat işçi (eski kira + eski deneme) finalize EDEMEZ.

    Kira jetonu `(attempt_count, lease_expires_at)` çiftidir; yeniden claim
    çifti değiştirir. Aksi hâlde geç uyanan bir işçi, başkasının süren
    denemesini `sent` yazıp gerçekleşmemiş bir teslimi kayda geçirirdi.
    """
    event_id = await _seed_event(notif_db)
    stale = (await claim_admin_events(notif_db, lease_seconds=600))[0]
    await _expire_lease(notif_db, event_id)
    fresh = (await claim_admin_events(notif_db, lease_seconds=600))[0]

    accepted = await finalize_admin_event(
        notif_db,
        event_id=event_id,
        attempt_count=stale["attempt_count"],
        lease_expires_at=stale["lease_expires_at"],
        success=True,
    )

    assert accepted is False
    row = await _row(notif_db, event_id)
    assert row["delivery_state"] == "sending"
    assert row["attempt_count"] == fresh["attempt_count"]


async def test_crash_after_send_before_finalize_redelivers_with_same_event_id(notif_db):
    """Gönderim sonrası çökme: yeniden teslim AYNI `event_id` ile gider.

    En-az-bir-kez teslim hedefinin bedeli budur; alıcı tarafın dedupe anahtarı
    payload'daki kimliktir, o yüzden kimliğin turlar arasında DEĞİŞMEMESİ
    sözleşmenin parçasıdır.
    """
    event_id = await _seed_event(notif_db)
    sender = _Sender()

    first = (await claim_admin_events(notif_db, lease_seconds=600))[0]
    await sender(notifications.build_envelope(first))  # gönderildi
    await _expire_lease(notif_db, event_id)  # finalize koşmadan çökme

    report = await dispatch_pending_admin_events(notif_db, send=sender, lease_seconds=600)

    assert report.sent == 1
    assert len(sender.calls) == 2
    assert {call["event_id"] for call in sender.calls} == {str(event_id)}
    assert (await _row(notif_db, event_id))["delivery_state"] == "sent"


async def test_dispatch_after_commit_with_bounded_retry(notif_db):
    """Sürekli düşen kanal: gönderim sayısı 3'te durur, satır `failed` olur."""
    event_id = await _seed_event(notif_db)
    sender = _Sender(fail=True)

    reports = [
        await dispatch_pending_admin_events(notif_db, send=sender, lease_seconds=600)
        for _ in range(MAX_DELIVERY_ATTEMPTS + 1)
    ]

    assert len(sender.calls) == MAX_DELIVERY_ATTEMPTS
    assert reports[-1].claimed == 0
    assert reports[-1].failed == 1
    assert (await _row(notif_db, event_id))["delivery_state"] == "failed"


async def test_sent_row_never_redispatched(notif_db):
    """`sent` satır bir daha claim edilmez."""
    event_id = await _seed_event(notif_db)
    sender = _Sender()

    first = await dispatch_pending_admin_events(notif_db, send=sender, lease_seconds=600)
    second = await dispatch_pending_admin_events(notif_db, send=sender, lease_seconds=600)

    assert first.sent == 1
    assert second.claimed == 0
    assert len(sender.calls) == 1
    assert (await _row(notif_db, event_id))["delivery_state"] == "sent"


# ─── 4. Süpürücü uygunluk kuralı (F20) ──────────────────────────────────────


async def test_sweeper_fails_exhausted_only_after_lease_expiry(notif_db):
    """Bütçesi bitmiş `sending` satır YALNIZ kirası dolduktan sonra `failed`."""
    event_id = await _seed_event(notif_db)
    await notif_db.execute(
        "UPDATE social.admin_events SET attempt_count = $2, delivery_state = 'sending', "
        "lease_expires_at = now() + interval '10 minutes' WHERE id = $1",
        event_id,
        MAX_DELIVERY_ATTEMPTS,
    )

    assert await sweep_exhausted_admin_events(notif_db) == 0
    assert (await _row(notif_db, event_id))["delivery_state"] == "sending"

    await _expire_lease(notif_db, event_id)
    assert await sweep_exhausted_admin_events(notif_db) == 1
    assert (await _row(notif_db, event_id))["delivery_state"] == "failed"


async def test_sweeper_spares_active_third_lease_and_finalize_wins(notif_db):
    """F20: üçüncü deneme canlıyken süpürme satıra DOKUNMAZ, finalize kazanır.

    Süpürücü aktif kirayı terminalleştirseydi yolda olan başarılı bir teslim
    `failed` diye kayda geçerdi — hem yanlış, hem de operatörü var olmayan bir
    arızayı kovalamaya iterdi.
    """
    event_id = await _seed_event(notif_db)
    await notif_db.execute(
        "UPDATE social.admin_events SET attempt_count = $2 WHERE id = $1",
        event_id,
        MAX_DELIVERY_ATTEMPTS - 1,
    )
    claimed = (await claim_admin_events(notif_db, lease_seconds=600))[0]
    assert claimed["attempt_count"] == MAX_DELIVERY_ATTEMPTS

    assert await sweep_exhausted_admin_events(notif_db) == 0
    assert (await _row(notif_db, event_id))["delivery_state"] == "sending"

    accepted = await finalize_admin_event(
        notif_db,
        event_id=event_id,
        attempt_count=claimed["attempt_count"],
        lease_expires_at=claimed["lease_expires_at"],
        success=True,
    )
    assert accepted is True
    assert (await _row(notif_db, event_id))["delivery_state"] == "sent"


# ─── 5. Eşzamanlılık ────────────────────────────────────────────────────────


async def test_concurrent_dispatchers_single_delivery(test_db_setup):
    """İki eşzamanlı dispatcher aynı satırı alamaz — tek gönderim."""
    url = _require_test_database(test_db_setup)
    setup = await _asyncpg.connect(url)
    await _init_connection(setup)
    workers: list = []
    key = _key()
    try:
        event_id = await record_admin_event(
            setup, kind=KIND, payload={"x": 1}, idempotency_key=key
        )
        for _ in range(2):
            worker = await _asyncpg.connect(url)
            await _init_connection(worker)
            workers.append(worker)

        sender = _Sender(delay=0.05)
        reports = await asyncio.gather(
            *[
                dispatch_pending_admin_events(worker, send=sender, lease_seconds=600)
                for worker in workers
            ]
        )

        assert sum(r.claimed for r in reports) == 1, f"tek claim bekleniyordu: {reports}"
        assert len(sender.calls) == 1
        assert await setup.fetchval(
            "SELECT delivery_state FROM social.admin_events WHERE id = $1", event_id
        ) == "sent"
    finally:
        for worker in workers:
            await worker.close()
        await setup.execute(
            "DELETE FROM social.admin_events WHERE idempotency_key = $1", key
        )
        await setup.close()


# ─── 5b. Bağlantı sahipliği ve hızlı yol tetiği (checkpoint 14, F3) ─────────


@pytest.fixture
async def notif_pool(test_db_setup):
    """TEK bağlantılık gerçek havuz — bağlantı sahipliğini ölçmenin tek yolu.

    `max_size=1` bilinçlidir: dispatcher bağlantıyı gönderim boyunca ELİNDE
    TUTUYORSA, gönderim sırasında havuzdan bağlantı isteyen herhangi bir iş
    kilitlenir. Kilitlenme bir zamanlama ölçüsü değil, ikili bir gözlemdir.
    """
    url = _require_test_database(test_db_setup)
    pool = await _asyncpg.create_pool(url, min_size=1, max_size=1, init=_init_connection)
    try:
        yield pool
    finally:
        await pool.close()


async def test_pool_dispatch_releases_connection_during_send(notif_pool):
    """Gönderim sırasında DB bağlantısı havuza GERİ VERİLİR.

    Eski biçim bağlantıyı süpürme + kiralama + TÜM gönderimler + kapatma
    boyunca tutuyordu. 20 bağlantılık havuzda, olay başına bir arka plan görevi
    ve yavaş bir n8n ile bu havuzu tüketip ALAKASIZ üretim isteklerini
    bekletirdi (checkpoint 14, F3). Ağ süresi boyunca bağlantı tutmak, dış
    bağımlılığın yavaşlığını kendi veritabanına bulaştırmaktır.
    """
    key = _key()
    async with notif_pool.acquire() as conn:
        await record_admin_event(conn, kind=KIND, payload={"x": 1}, idempotency_key=key)

    seen_during_send: list[int] = []

    async def _sender(envelope: dict) -> None:
        # Gönderim sırasında havuzdan bağlantı istiyoruz. Dispatcher tek
        # bağlantıyı bırakmadıysa burası asla dönmez.
        async with notif_pool.acquire() as conn:
            seen_during_send.append(await conn.fetchval("SELECT 1"))

    try:
        report = await asyncio.wait_for(
            notifications.dispatch_pending_admin_events_via_pool(
                notif_pool, send=_sender, lease_seconds=600
            ),
            timeout=10,
        )
        assert report.sent == 1
        assert seen_during_send == [1]
        async with notif_pool.acquire() as conn:
            assert await conn.fetchval(
                "SELECT delivery_state FROM social.admin_events WHERE idempotency_key = $1",
                key,
            ) == "sent"
    finally:
        async with notif_pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM social.admin_events WHERE idempotency_key = $1", key
            )


async def test_fast_dispatch_coalesces_into_single_worker(test_db_setup, monkeypatch):
    """Olay başına bir görev DEĞİL — aynı anda EN FAZLA bir dispatcher koşar.

    Görev başına bir bağlantı tutulduğu için "olay başına görev" havuz
    tüketiminin ta kendisiydi. Birleştirme bunu tek işçiye indirir; bir tur
    koşarken gelen olayları bir SONRAKİ tur toplar.
    """
    started = 0
    release = asyncio.Event()

    async def _slow_worker():
        nonlocal started
        started += 1
        await release.wait()

    monkeypatch.setattr(notifications, "get_pool_if_ready", lambda: object())
    monkeypatch.setattr(notifications, "_dispatch_in_background", _slow_worker)

    url = _require_test_database(test_db_setup)
    conn = await _asyncpg.connect(url)
    await _init_connection(conn)
    keys = [_key() for _ in range(3)]
    try:
        for key in keys:
            await record_admin_event(conn, kind=KIND, payload={"x": 1}, idempotency_key=key)
        await asyncio.sleep(0)  # görevlerin başlamasına izin ver
        assert started == 1, f"olay başına görev doğdu: {started}"
    finally:
        release.set()
        await asyncio.sleep(0)
        await conn.execute(
            "DELETE FROM social.admin_events WHERE idempotency_key = ANY($1::text[])", keys
        )
        await conn.close()


async def test_fast_dispatch_not_triggered_inside_transaction(test_db_setup, monkeypatch):
    """Açık transaction içinde tetik ATEŞLENMEZ — satır henüz commit değil.

    DÜRÜST SINIR: bu, genel bir "commit sonrası" kancası DEĞİLDİR. Açık
    transaction içinde yazan çağıranlar için hızlı yol hiç koşmaz ve teslimi
    kurtarma yolu (n8n schedule) üstlenir. Hızlı yol yalnız gecikmeyi kısar;
    teslim garantisi ona DAYANMAZ.
    """
    started = 0

    async def _worker():
        nonlocal started
        started += 1

    monkeypatch.setattr(notifications, "get_pool_if_ready", lambda: object())
    monkeypatch.setattr(notifications, "_dispatch_in_background", _worker)

    url = _require_test_database(test_db_setup)
    conn = await _asyncpg.connect(url)
    await _init_connection(conn)
    key = _key()
    try:
        transaction = conn.transaction()
        await transaction.start()
        await record_admin_event(conn, kind=KIND, payload={"x": 1}, idempotency_key=key)
        await asyncio.sleep(0)
        assert started == 0, "commit edilmemiş satır için tetik ateşlendi"
        await transaction.rollback()
    finally:
        await conn.close()


# ─── 6. İç uç nokta ─────────────────────────────────────────────────────────


def test_internal_endpoint_requires_internal_key(monkeypatch):
    """X-Internal-Key olmadan/yanlışken uç nokta 401 verir."""
    from app.core import security as security_module

    monkeypatch.setattr(security_module.settings, "INTERNAL_API_KEY", "dogru-anahtar")

    with pytest.raises(HTTPException) as missing:
        get_service_auth(x_internal_key=None)
    assert missing.value.status_code == 401

    with pytest.raises(HTTPException) as wrong:
        get_service_auth(x_internal_key="yanlis")
    assert wrong.value.status_code == 401

    assert get_service_auth(x_internal_key="dogru-anahtar") is None
    assert internal_router.dispatch_pending_admin_events_endpoint is not None


async def test_pending_events_reswept_via_internal_endpoint_after_crash(
    notif_pool, monkeypatch
):
    """Kurtarma yolu: çökmeden kalan `pending` satır iç uç noktayla süpürülür.

    Uç nokta artık istek bağlantısı ALMAZ (checkpoint 14, F3) — havuzu kendisi
    çözer. Test de bu yüzden gerçek bir havuz verir: sahte bir bağlantı
    geçirmek, düzeltilen davranışın ta kendisini ölçmeden bırakırdı.
    """
    from app.core import database

    sender = _Sender()
    monkeypatch.setattr(notifications, "_send_to_n8n", sender)

    async def _pool():
        return notif_pool

    monkeypatch.setattr(database, "get_pool", _pool)

    key = _key()
    try:
        async with notif_pool.acquire() as conn:
            await record_admin_event(
                conn, kind=KIND, payload={"x": 1}, idempotency_key=key
            )

        response = await internal_router.dispatch_pending_admin_events_endpoint(_=None)

        assert response.data["sent"] == 1
        assert len(sender.calls) == 1
        async with notif_pool.acquire() as conn:
            assert await conn.fetchval(
                "SELECT delivery_state FROM social.admin_events WHERE idempotency_key = $1",
                key,
            ) == "sent"
    finally:
        async with notif_pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM social.admin_events WHERE idempotency_key = $1", key
            )


# ─── 6b. Teslim kanalı: kabul kontrolü ve teslim semantiği (checkpoint 14) ──


class _FakeResponse:
    def __init__(self, status: int = 200):
        self.status_code = status

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class _FakeClient:
    """httpx.AsyncClient yerine geçen, isteği yakalayan sahte istemci."""

    captured: dict = {}

    def __init__(self, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def post(self, url, json=None, headers=None):
        _FakeClient.captured = {"url": url, "json": json, "headers": headers or {}}
        return _FakeResponse()


async def test_send_fails_closed_without_webhook_secret(notif_db, monkeypatch):
    """Sır yoksa gönderim YAPILMAZ — kimliksiz çağrı yola çıkmaz.

    Kabul kontrolü olmayan bir webhook'a yollamak, o webhook'a erişebilen
    herkesin sahte yönetici uyarısı üretebilmesi demekti (checkpoint 14, F1).
    Sır eksikken sessizce kimliksiz göndermek kapıyı boşa çıkarırdı; satır
    `pending`e döner ve yeniden denenir.
    """
    monkeypatch.setattr(notifications.settings, "N8N_ADMIN_EVENT_SECRET", "")
    monkeypatch.setattr(notifications.httpx, "AsyncClient", _FakeClient)
    _FakeClient.captured = {}

    event_id = await _seed_event(notif_db)
    report = await dispatch_pending_admin_events(notif_db, lease_seconds=600)

    assert report.sent == 0
    assert report.deferred == 1
    assert _FakeClient.captured == {}, "sırsızken çağrı YAPILDI"
    assert (await _row(notif_db, event_id))["delivery_state"] == "pending"


async def test_send_includes_admin_event_auth_header(notif_db, monkeypatch):
    """Sır varsa kabul başlığı isteğe EKLENİR ve zarf sözleşmeye uyar."""
    monkeypatch.setattr(notifications.settings, "N8N_ADMIN_EVENT_SECRET", "gizli-anahtar")
    monkeypatch.setattr(notifications.httpx, "AsyncClient", _FakeClient)
    _FakeClient.captured = {}

    event_id = await _seed_event(notif_db)
    report = await dispatch_pending_admin_events(notif_db, lease_seconds=600)

    assert report.sent == 1
    captured = _FakeClient.captured
    assert captured["headers"][notifications.ADMIN_EVENT_AUTH_HEADER] == "gizli-anahtar"
    assert captured["json"]["event_id"] == str(event_id)
    assert set(captured["json"]) == {"event_id", "kind", "payload", "contract_version"}


def _admin_workflow() -> dict:
    import json

    path = (
        infra_repo_root() / "shared" / "n8n-workflows" / "sector-package-admin-events.json"
    )
    return json.loads(path.read_text(encoding="utf-8"))


def infra_repo_root():
    from .conftest import REPO_ROOT

    return REPO_ROOT


def _node(workflow: dict, name: str) -> dict:
    for node in workflow["nodes"]:
        if node["name"] == name:
            return node
    raise AssertionError(f"düğüm yok: {name}")


def test_workflow_webhook_requires_authentication():
    """Webhook kimlik doğrulaması İSTER — açık uç kabul edilmez (F1).

    Bu artefaktın canlı importu manuel bir adım (Task 16); o yüzden sözleşme
    burada YAPISAL olarak pinlenir. Aksi hâlde "kimlik doğrulaması var" iddiası
    hiçbir yerde ölçülmemiş olurdu.
    """
    workflow = _admin_workflow()
    webhook = _node(workflow, "Yönetici Olayı Webhook")

    assert webhook["parameters"].get("authentication") == "headerAuth", (
        "webhook kimlik doğrulamasız — herkes sahte yönetici uyarısı üretebilir"
    )
    assert "httpHeaderAuth" in (webhook.get("credentials") or {})


def test_workflow_acknowledges_only_after_delivery():
    """Yanıt teslimden SONRA verilir ve Telegram hatası YUTULMAZ (F2).

    `onReceived` modunda n8n workflow BAŞLAR BAŞLAMAZ 200 döner; arka uç satırı
    `sent` yazar ve sonraki bir Telegram hatası SESSİZCE kaybolur. Üstelik
    tekrar-kaydı gönderimden önce yapılırsa yeniden teslim de bastırılır — yani
    bildirim hem kaybolur hem bir daha denenmez.
    """
    workflow = _admin_workflow()
    webhook = _node(workflow, "Yönetici Olayı Webhook")
    telegram = _node(workflow, "Telegram Bildir")
    sweeper = _node(workflow, "Bekleyenleri Süpür")

    assert webhook["parameters"].get("responseMode") != "onReceived"
    assert not telegram.get("continueOnFail"), (
        "Telegram hatası yutuluyor — arka uç yanlışlıkla `sent` yazar"
    )
    assert not sweeper.get("continueOnFail"), (
        "kurtarma turu hatası yutuluyor — n8n çalıştırma listesinde görünmez"
    )


def test_workflow_records_dedupe_only_after_successful_send():
    """Tekrar kaydı gönderimden SONRA yazılır — başarısız teslim bastırılmaz."""
    workflow = _admin_workflow()
    connections = workflow["connections"]

    targets = [
        target["node"]
        for branch in connections["Telegram Bildir"]["main"]
        for target in branch
    ]
    assert "Tekrarı Kaydet" in targets, (
        "tekrar kaydı Telegram'dan SONRA gelmiyor — başarısız teslim yeniden "
        "denendiğinde sessizce elenir"
    )
    # Gönderim ÖNCESİ düğüm yalnız KONTROL eder, kayıt YAPMAZ.
    checker = _node(workflow, "Tekrarı Kontrol Et")
    assert "seenEventIds.push" not in checker["parameters"]["jsCode"], (
        "kontrol düğümü gönderimden önce kayıt yazıyor"
    )


def test_workflow_reads_no_process_env():
    """Workflow node'ları `$env` OKUMAZ — canlı n8n bunu bloklar.

    ÖLÇÜLDÜ (2026-08-26, canlı kurulum): n8n servisi
    `N8N_BLOCK_ENV_ACCESS_IN_NODE=true` ile koşuyor, yani node içinden ortam
    değişkeni okumak KAPALI. Bu artefaktın ilk hâli Telegram token'ını ve chat
    id'sini `$env`'den okuyordu; import edilse canlıda HİÇ çalışamazdı ve hiçbir
    test bunu görmüyordu — sır/yapılandırma n8n'in kendi credential deposunda
    durmalı. Kapı `$env`'i yasaklar, alternatifi dikte ETMEZ.
    """
    import json

    blob = json.dumps(_admin_workflow(), ensure_ascii=False)

    assert "$env" not in blob, (
        "workflow `$env` okuyor — canlı n8n `N8N_BLOCK_ENV_ACCESS_IN_NODE=true` "
        "ile koşuyor, bu ifade orada çözülmez"
    )


def test_workflow_carries_a_stable_id():
    """Artefakt SABİT bir `id` taşır — n8n CLI importu onsuz REDDEDER.

    ÖLÇÜLDÜ (2026-08-26): `n8n import:workflow` id'siz dosyada
    `null value in column "id" of relation "workflow_entity"` ile düşüyor —
    yani artefakt canlıya HİÇ giremiyordu. Sabit id ayrıca tekrar import'u
    idempotent yapar: aynı workflow güncellenir, ikinci bir kopya doğmaz.
    """
    workflow = _admin_workflow()

    wid = workflow.get("id")
    assert wid, "workflow `id` taşımıyor — n8n CLI importu reddeder"
    assert isinstance(wid, str) and wid.isalnum(), (
        f"workflow id alfanümerik tek parça olmalı (bulunan: {wid!r})"
    )


def test_workflow_credentials_are_bound():
    """Her credential atıfı GERÇEK bir kimliğe bağlı — yer tutucu kalmaz.

    Yer tutucu bir id ile import edilen workflow n8n'de sessizce kimliksiz
    bir node üretir; kusur ancak ilk tetiklemede görülür.
    """
    workflow = _admin_workflow()

    seen = 0
    for node in workflow["nodes"]:
        for kind, ref in (node.get("credentials") or {}).items():
            seen += 1
            assert ref.get("id"), f"{node['name']}: {kind} credential id'si boş"
            assert "REPLACE" not in ref["id"].upper(), (
                f"{node['name']}: {kind} hâlâ yer tutucu id taşıyor ({ref['id']})"
            )
    assert seen >= 3, f"credential atıfı beklenenden az ({seen}) — dosya budanmış olabilir"


# ─── 7. Marka durumu ucu (K-45) ─────────────────────────────────────────────


async def _seed_brand(db, *, sub_sector_id=None) -> uuid.UUID:
    """Sahiplik zinciri kurmadan sadece marka (olay testleri için)."""
    _, brand_id = await _seed_owner_and_brand(db, sub_sector_id=sub_sector_id)
    return brand_id


async def _seed_owner_and_brand(db, *, sub_sector_id=None):
    account_id = await db.fetchval(
        "INSERT INTO social.accounts (email, name, plan_id) "
        "VALUES ($1, $2, 'pro') RETURNING id",
        f"bildirim-{uuid.uuid4()}@example.test",
        "Bildirim Sahibi",
    )
    workspace_id = await db.fetchval(
        "INSERT INTO social.workspaces (account_id, name) VALUES ($1, $2) RETURNING id",
        account_id,
        "Bildirim Çalışma Alanı",
    )
    await db.execute(
        "INSERT INTO social.workspace_members (workspace_id, account_id) VALUES ($1, $2)",
        workspace_id,
        account_id,
    )
    brand_id = await db.fetchval(
        "INSERT INTO social.brands (workspace_id, name, sub_sector_id) "
        "VALUES ($1, $2, $3) RETURNING id",
        workspace_id,
        "Bildirim Markası",
        sub_sector_id,
    )
    return {"sub": str(account_id)}, brand_id


async def _seed_sub_sector(db) -> uuid.UUID:
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


async def test_package_status_requires_ownership(notif_db):
    """Başkasının markası 404 — kaynağın VARLIĞI bile sızmaz."""
    _, brand_id = await _seed_owner_and_brand(notif_db)
    stranger, _ = await _seed_owner_and_brand(notif_db)

    with pytest.raises(HTTPException) as exc:
        await brands_router.get_package_status(
            brand_id=brand_id, user=stranger, db=notif_db
        )

    assert exc.value.status_code == 404


async def test_package_status_packaged_and_unpackaged(notif_db):
    """Atamasız marka `unpackaged`; aktif paketli marka `packaged`."""
    user, plain_brand = await _seed_owner_and_brand(notif_db)
    plain = await brands_router.get_package_status(
        brand_id=plain_brand, user=user, db=notif_db
    )
    assert plain.data == {"mode": "unpackaged", "message": None}

    sub_sector_id = await _seed_sub_sector(notif_db)
    owner, packaged_brand = await _seed_owner_and_brand(
        notif_db, sub_sector_id=sub_sector_id
    )
    await notif_db.execute(
        "INSERT INTO social.sector_packages "
        "(sector_id, version, status, schema_version, content) "
        "VALUES ($1, 1, 'active', 1, $2)",
        sub_sector_id,
        {"gorsel_kodlar": {}},
    )

    packaged = await brands_router.get_package_status(
        brand_id=packaged_brand, user=owner, db=notif_db
    )
    assert packaged.data == {"mode": "packaged", "message": None}


async def test_package_status_maintenance_message_exact(notif_db):
    """Bayat atama = `maintenance`; metin K-45 SABİT metnidir (birebir)."""
    sub_sector_id = await _seed_sub_sector(notif_db)
    user, brand_id = await _seed_owner_and_brand(notif_db, sub_sector_id=sub_sector_id)

    response = await brands_router.get_package_status(
        brand_id=brand_id, user=user, db=notif_db
    )

    assert response.data["mode"] == "maintenance"
    assert response.data["message"] == (
        "Bakım çalışmaları nedeniyle gönderileriniz genel modda üretilmektedir. "
        "En kısa sürede sektöre özel gönderi moduna geçilecektir."
    )
    # Metin backend'de TEK yerde yaşar — önyüz onu kopyalamaz, okur.
    assert response.data["message"] == MAINTENANCE_BANNER_MESSAGE
