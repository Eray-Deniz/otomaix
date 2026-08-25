"""Yönetici bildirimi — transactional outbox + kira protokolü (plan Task 14).

Bu modül üç ayrı işi BİLİNÇLİ olarak birbirinden ayırır:

1. **Yazım** (`record_admin_event`) — satır, tetikleyen iş transaction'ıyla
   BİRLİKTE commit edilir. Doğrudan webhook gönderimi olsaydı, geri alınan bir
   işin bildirimi yola çıkmış olurdu; outbox tam olarak bu pencereyi kapatır.
2. **Kiralama** (`claim_admin_events`) — KISA bir transaction: adayları
   `FOR UPDATE SKIP LOCKED` ile alır, `sending` + kira yazar ve **deneme
   bütçesini burada tüketir** (F19). Bütçe finalize'da düşseydi, claim'den
   sonra çöken işçi bedelsiz bir deneme kazanır ve "sınırlı yeniden deneme"
   hükmü yalan olurdu.
3. **Kesinleştirme** (`finalize_admin_event`) — durum + kira korumalı
   güncelleme. Kira jetonu ayrı bir kolon değil, `(attempt_count,
   lease_expires_at)` çiftidir; her claim `attempt_count`'u atomik artırdığı
   için yeniden claim edilen satırın çifti kesin olarak değişir ve bayat işçi
   finalize edemez. Zaman damgası TEK BAŞINA jeton olamazdı (iki claim aynı
   mikrosaniyeye düşerse ayırt edilemez).

**Gönderim transaction DIŞINDADIR.** Ağ çağrısını transaction içinde tutmak,
n8n yavaşladığında satır kilidini ağ süresi kadar elde tutmak demekti.

**Teslim hedefi en-az-bir-kez.** Gönderim-sonrası-finalize-öncesi çökmede satır
yeniden gönderilir; alıcı tarafın dedupe anahtarı zarftaki `event_id`'dir ve o
kimlik turlar arasında DEĞİŞMEZ.

**Bildirim hiçbir koşulda üretimi bloklamaz** — çağıran yüzeyler
(`package_events.log_package_event`) bu modülün her hatasını yutar.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Awaitable, Callable
from uuid import UUID

import httpx

from app.core.config import settings
from app.core.database import get_pool_if_ready

logger = logging.getLogger(__name__)

# Sınırlı yeniden deneme (bağlanan teknik karar 6). Bu sayı bir ÜRÜN kararıdır,
# ölçüm değil: üçüncü denemeden sonra satır `failed`e çekilir ve polling'le
# görünür kalır.
MAX_DELIVERY_ATTEMPTS = 3

# Kira süresi. ÖLÇÜLMEMİŞ bir değerdir (tahmin) ve hiçbir kapının eşiği
# DEĞİLDİR — yalnız "çöken işçinin satırı ne kadar süre tuttuğu"nu sınırlar.
# Kısaltmak çift gönderim olasılığını artırır (en-az-bir-kez zaten kabul
# edilmiş), uzatmak kurtarmayı geciktirir.
DEFAULT_LEASE_SECONDS = 300

# Aynı anda kaç satır kiralanır. Kurtarma turunun bir seferde ne kadar iş
# aldığını sınırlar; kalanı bir sonraki tur alır.
DEFAULT_CLAIM_LIMIT = 20

# Webhook payload sözleşmesinin sürümü. n8n workflow JSON'ı ile BİRLİKTE
# versiyonlanır; alan eklemek/çıkarmak bu sayıyı artırır.
ADMIN_EVENT_CONTRACT_VERSION = 1

# n8n workflow'unun webhook yolu — artefakt: shared/n8n-workflows/
# sector-package-admin-events.json
ADMIN_EVENT_WEBHOOK_PATH = "sector-package-admin-events"

# K-45 SABİT devre-dışı metni. Marka sahibine gösterilen bant bu tek kaynaktan
# okunur; önyüz metni KOPYALAMAZ (kopya, iki yerde ıraksayan bir vaat üretir).
MAINTENANCE_BANNER_MESSAGE = (
    "Bakım çalışmaları nedeniyle gönderileriniz genel modda üretilmektedir. "
    "En kısa sürede sektöre özel gönderi moduna geçilecektir."
)

Sender = Callable[[dict], Awaitable[None]]


class AdminEventContractError(ValueError):
    """Outbox yazımı sözleşmesi ihlal edildi — çağıranın hatası."""


@dataclass(frozen=True)
class DispatchReport:
    """Tek dispatch turunun muhasebesi.

    `claimed` fiziksel gönderim denemesi sayısıdır; `sent` + `deferred` ona
    eşittir (kirası kaybedilmiş satır hariç — o `lost` altında görünür).
    """

    claimed: int = 0
    sent: int = 0
    deferred: int = 0
    failed: int = 0
    lost: int = 0


# ─── 1. Yazım ───────────────────────────────────────────────────────────────


async def record_admin_event(
    db, *, kind: str, payload: dict, idempotency_key: str
) -> UUID:
    """Outbox satırını çağıranın transaction'ı İÇİNDE yazar; kimliği döner.

    Aynı `idempotency_key` ile ikinci yazım YENİ satır üretmez — mevcut satırın
    kimliği döner ve payload EZİLMEZ. İlk yazımın kazanması bilinçlidir: outbox
    bir denetim kaydıdır, sonradan gelen bir çağrının gerçekliği yeniden
    yazmasına izin verilmez.
    """
    if not isinstance(kind, str) or not kind.strip():
        raise AdminEventContractError("kind boş olamaz")
    if not isinstance(payload, dict):
        raise AdminEventContractError(
            f"payload sözlük olmalı, {type(payload).__name__} verildi"
        )
    if not isinstance(idempotency_key, str) or not idempotency_key.strip():
        raise AdminEventContractError("idempotency_key boş olamaz")

    event_id = await db.fetchval(
        """
        INSERT INTO social.admin_events (kind, payload, idempotency_key)
        VALUES ($1, $2, $3)
        ON CONFLICT (idempotency_key) DO NOTHING
        RETURNING id
        """,
        kind,
        payload,
        idempotency_key,
    )
    if event_id is None:
        event_id = await db.fetchval(
            "SELECT id FROM social.admin_events WHERE idempotency_key = $1",
            idempotency_key,
        )
    if event_id is None:  # pragma: no cover — çakışma da satır da yoksa DUR
        raise AdminEventContractError(
            f"outbox satırı ne yazıldı ne bulundu: {idempotency_key!r}"
        )

    _maybe_trigger_fast_dispatch(db)
    return event_id


# ─── 2. Kira protokolü ──────────────────────────────────────────────────────


async def claim_admin_events(
    db,
    *,
    limit: int = DEFAULT_CLAIM_LIMIT,
    lease_seconds: int = DEFAULT_LEASE_SECONDS,
) -> list[dict]:
    """Aday satırları kiralar; **KISA transaction**, commit ile biter.

    Aday = `pending` VEYA kirası DOLMUŞ `sending`; her iki durumda da bütçesi
    kalmış olmalı. `FOR UPDATE SKIP LOCKED` sayesinde eşzamanlı iki dispatcher
    aynı satırı asla alamaz — biri satırı atlar, boş döner.

    Aktif kirası olan satır ADAY DEĞİLDİR: kirası süren bir satırı yeniden
    kiralamak, yolda olan bir teslimi ikizlemek olurdu.
    """
    async with db.transaction():
        rows = await db.fetch(
            """
            WITH candidate AS (
                SELECT id
                FROM social.admin_events
                WHERE attempt_count < $1
                  AND (
                        delivery_state = 'pending'
                        OR (delivery_state = 'sending' AND lease_expires_at < now())
                      )
                ORDER BY created_at
                LIMIT $2
                FOR UPDATE SKIP LOCKED
            )
            UPDATE social.admin_events e
               SET delivery_state = 'sending',
                   lease_expires_at = now() + make_interval(secs => $3),
                   attempt_count = e.attempt_count + 1
              FROM candidate c
             WHERE e.id = c.id
         RETURNING e.id, e.kind, e.payload, e.idempotency_key,
                   e.attempt_count, e.lease_expires_at
            """,
            MAX_DELIVERY_ATTEMPTS,
            limit,
            lease_seconds,
        )
    return [dict(row) for row in rows]


async def finalize_admin_event(
    db, *, event_id: UUID, attempt_count: int, lease_expires_at, success: bool
) -> bool:
    """Kirayı kapatır. Jeton eşleşmezse HİÇBİR ŞEY yazmaz ve `False` döner.

    Başarıda `sent`; başarısızlıkta `pending`e geri — bütçe zaten claim'de
    düştüğü için geri dönüş bedava bir deneme DEĞİLDİR.
    """
    target = "sent" if success else "pending"
    updated = await db.fetchval(
        """
        UPDATE social.admin_events
           SET delivery_state = $2,
               lease_expires_at = NULL
         WHERE id = $1
           AND delivery_state = 'sending'
           AND attempt_count = $3
           AND lease_expires_at = $4
        RETURNING id
        """,
        event_id,
        target,
        attempt_count,
        lease_expires_at,
    )
    return updated is not None


async def sweep_exhausted_admin_events(db) -> int:
    """Bütçesi bitmiş satırları kalıcı `failed`e çeker; sayısını döner.

    **F20 uygunluk kuralı:** aktif kira ASLA süpürülmez. `pending` + tükenmiş
    bütçe hemen düşer; `sending` + tükenmiş bütçe YALNIZ kirası dolmuşsa düşer.
    Üçüncü deneme canlıyken satırı terminalleştirmek, yolda olan başarılı bir
    teslimi `failed` diye kayda geçirmek olurdu — hem yanlış olur, hem de
    operatörü var olmayan bir arızayı kovalamaya iterdi.
    """
    rows = await db.fetch(
        """
        UPDATE social.admin_events
           SET delivery_state = 'failed',
               lease_expires_at = NULL
         WHERE attempt_count >= $1
           AND (
                 delivery_state = 'pending'
                 OR (delivery_state = 'sending' AND lease_expires_at < now())
               )
        RETURNING id
        """,
        MAX_DELIVERY_ATTEMPTS,
    )
    if rows:
        logger.warning(
            "yönetici bildirimi kalıcı olarak başarısız (deneme bütçesi bitti): %s",
            ", ".join(str(row["id"]) for row in rows),
        )
    return len(rows)


# ─── 3. Gönderim ────────────────────────────────────────────────────────────


def build_envelope(row: dict) -> dict:
    """Webhook payload sözleşmesi — n8n workflow JSON'ı ile BİRLİKTE versiyonlu.

    `event_id` alıcı tarafın dedupe anahtarıdır ve yeniden gönderimlerde AYNI
    kalır; en-az-bir-kez teslimin tekilleştirilmesi buna dayanır.
    """
    return {
        "event_id": str(row["id"]),
        "kind": row["kind"],
        "payload": row["payload"],
        "contract_version": ADMIN_EVENT_CONTRACT_VERSION,
    }


async def _send_to_n8n(envelope: dict) -> None:
    """Tek teslim kanalı. Başarısızlık İSTİSNA ile bildirilir (sessiz yutma YOK).

    HTTP 4xx/5xx da başarısızlıktır: `raise_for_status` olmadan n8n'in
    reddettiği bir çağrı `sent` diye kayda geçerdi.
    """
    url = f"{settings.N8N_BASE_URL}/webhook/{ADMIN_EVENT_WEBHOOK_PATH}"
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(url, json=envelope)
        response.raise_for_status()


async def dispatch_pending_admin_events(
    db,
    *,
    limit: int = DEFAULT_CLAIM_LIMIT,
    lease_seconds: int = DEFAULT_LEASE_SECONDS,
    send: Sender | None = None,
) -> DispatchReport:
    """Tek dispatch turu: süpür → kirala → (transaction DIŞINDA) gönder → kapat.

    Süpürme ÖNCE koşar: bütçesi bitmiş satır bu turda kiralanmaya çalışılmasın,
    doğrudan terminal duruma gitsin diye.
    """
    if send is None:
        send = _send_to_n8n

    failed = await sweep_exhausted_admin_events(db)
    claimed = await claim_admin_events(db, limit=limit, lease_seconds=lease_seconds)

    sent = deferred = lost = 0
    for row in claimed:
        try:
            await send(build_envelope(row))
        except Exception as exc:  # noqa: BLE001 — kanal hatası tur'u bitirmez
            logger.warning(
                "yönetici bildirimi gönderilemedi (event_id=%s deneme=%s): %s",
                row["id"],
                row["attempt_count"],
                exc,
            )
            await finalize_admin_event(
                db,
                event_id=row["id"],
                attempt_count=row["attempt_count"],
                lease_expires_at=row["lease_expires_at"],
                success=False,
            )
            deferred += 1
            continue

        accepted = await finalize_admin_event(
            db,
            event_id=row["id"],
            attempt_count=row["attempt_count"],
            lease_expires_at=row["lease_expires_at"],
            success=True,
        )
        if accepted:
            sent += 1
        else:
            # Kira kaybedildi (satır bu arada yeniden kiralanmış). Gönderim
            # gerçekten yapıldı ama sahiplik başkasında; `sent` YAZILMAZ.
            # En-az-bir-kez hedefinin görünür bedeli budur.
            lost += 1
            logger.warning(
                "yönetici bildirimi gönderildi ama kira kaybedilmişti "
                "(event_id=%s deneme=%s) — teslim tekrarlanabilir",
                row["id"],
                row["attempt_count"],
            )

    return DispatchReport(
        claimed=len(claimed), sent=sent, deferred=deferred, failed=failed, lost=lost
    )


# ─── 4. Hızlı yol (commit sonrası best-effort tetik) ────────────────────────
#
# İki tetikleyici vardır (bağlanan teknik karar 6): (a) olayı yazan istek,
# commit SONRASI dispatch'i best-effort çağırır — buradaki yol; (b) kurtarma
# yolu, n8n SCHEDULE'ı `POST /internal/admin-events/dispatch-pending`'i
# periyodik çağırır. (b) tek başına da yeterlidir; (a) yalnız gecikmeyi kısar.
#
# Kapı FAIL-CLOSED'dır: uygulama havuzu kurulu değilse (testler, script'ler)
# hızlı yol HİÇ ateşlenmez. Aksi hâlde bir test, uygulamanın CANLI veritabanına
# bağlanmasını tetikleyebilirdi.

_BACKGROUND_TASKS: set[asyncio.Task[Any]] = set()


def _maybe_trigger_fast_dispatch(db) -> None:
    """Satır COMMIT'lenmişse arka planda tek dispatch turu ateşler.

    Açık bir transaction içindeysek tetiklemeyiz: satır henüz commit edilmemiş
    olabilir ve dispatcher onu ya göremez (boşuna tur) ya da — daha kötüsü —
    geri alınacak bir işin bildirimini yollardı.
    """
    if get_pool_if_ready() is None:
        return
    try:
        if db.is_in_transaction():
            return
    except AttributeError:  # pragma: no cover — bağlantı benzeri sahte nesne
        return

    task = asyncio.create_task(_dispatch_in_background())
    _BACKGROUND_TASKS.add(task)
    task.add_done_callback(_BACKGROUND_TASKS.discard)


async def _dispatch_in_background() -> None:
    """Kendi bağlantısını alır; her hatayı yutar — üretim akışı etkilenmez."""
    pool = get_pool_if_ready()
    if pool is None:  # pragma: no cover — havuz arada kapandıysa
        return
    try:
        async with pool.acquire() as conn:
            await dispatch_pending_admin_events(conn)
    except Exception as exc:  # noqa: BLE001
        logger.warning("hızlı yol dispatch başarısız (kurtarma yolu kapsar): %s", exc)
