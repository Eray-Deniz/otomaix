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

# F20 uygunluk yüklemi — TEK yerde tanımlıdır. Kiralama ve süpürme AYNI "aday
# satır" tanımını kullanmak ZORUNDADIR: iki kopya ayrışırsa biri aktif kirayı
# süpürebilir (yolda olan teslimi `failed` yazmak), diğeri kirası dolmuş satırı
# görmezden gelebilirdi (kurtarma hiç koşmaz). İkisi de sessiz olurdu.
#
# Sorgu metnine gömülür; SABİT metindir, hiçbir kullanıcı girdisi buraya
# ulaşmaz — parametreler `$N` ile geçmeye devam eder.
_ELIGIBLE_ROW_SQL = (
    "(delivery_state = 'pending' "
    "OR (delivery_state = 'sending' AND lease_expires_at < now()))"
)

# Webhook payload sözleşmesinin sürümü. n8n workflow JSON'ı ile BİRLİKTE
# versiyonlanır; alan eklemek/çıkarmak bu sayıyı artırır.
ADMIN_EVENT_CONTRACT_VERSION = 1

# n8n workflow'unun webhook yolu — artefakt: shared/n8n-workflows/
# sector-package-admin-events.json
ADMIN_EVENT_WEBHOOK_PATH = "sector-package-admin-events"

# Kabul kontrolü başlığı. n8n tarafındaki `httpHeaderAuth` kimlik bilgisiyle
# BİREBİR aynı olmalıdır — workflow artefaktı ve bu sabit birlikte versiyonlanır.
ADMIN_EVENT_AUTH_HEADER = "X-Admin-Event-Key"

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
            f"""
            WITH candidate AS (
                SELECT id
                FROM social.admin_events
                WHERE attempt_count < $1
                  AND {_ELIGIBLE_ROW_SQL}
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
        f"""
        UPDATE social.admin_events
           SET delivery_state = 'failed',
               lease_expires_at = NULL
         WHERE attempt_count >= $1
           AND {_ELIGIBLE_ROW_SQL}
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

    **Kabul kontrolü fail-closed'dır (checkpoint 14, F1):** sır yapılandırılmamışsa
    çağrı HİÇ yapılmaz. Sırsız göndermek, kimlik doğrulamasız bir webhook'a
    erişebilen herkesin sahte yönetici uyarısı üretebilmesi demekti; sessizce
    kimliksiz göndermek de kapıyı boşa çıkarırdı. İstisna yolu satırı `pending`e
    döndürür — bildirim kaybolmaz, yapılandırma düzelince gider.
    """
    secret = settings.N8N_ADMIN_EVENT_SECRET
    if not secret:
        raise AdminEventContractError(
            "N8N_ADMIN_EVENT_SECRET boş — kimliksiz webhook çağrısı YAPILMAZ "
            "(fail-closed); sırrı yapılandırın, satır yeniden denenecek"
        )

    url = f"{settings.N8N_BASE_URL}/webhook/{ADMIN_EVENT_WEBHOOK_PATH}"
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            url, json=envelope, headers={ADMIN_EVENT_AUTH_HEADER: secret}
        )
        response.raise_for_status()


async def _deliver_claimed(rows: list[dict], send: Sender, finalize) -> tuple[int, int, int]:
    """Kiralanmış satırları gönderir ve kapatır; (sent, deferred, lost) döner.

    `finalize` bir geri-çağrıdır (`async (row, success) -> bool`) çünkü tek
    bağlantılı ve havuzlu iki dispatch biçiminin TEK farkı, kapatmanın hangi
    bağlantıda koştuğudur. Döngüyü iki kez yazmak, gelecekteki bir düzeltmenin
    yalnız bir kopyaya uygulanmasına davetiye olurdu.
    """
    sent = deferred = lost = 0
    for row in rows:
        try:
            await send(build_envelope(row))
        except Exception as exc:  # noqa: BLE001 — kanal hatası tur'u bitirmez
            logger.warning(
                "yönetici bildirimi gönderilemedi (event_id=%s deneme=%s): %s",
                row["id"],
                row["attempt_count"],
                exc,
            )
            await finalize(row, False)
            deferred += 1
            continue

        if await finalize(row, True):
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
    return sent, deferred, lost


async def dispatch_pending_admin_events(
    db,
    *,
    limit: int = DEFAULT_CLAIM_LIMIT,
    lease_seconds: int = DEFAULT_LEASE_SECONDS,
    send: Sender | None = None,
) -> DispatchReport:
    """Tek dispatch turu TEK bağlantı üstünde: süpür → kirala → gönder → kapat.

    Süpürme ÖNCE koşar: bütçesi bitmiş satır bu turda kiralanmaya çalışılmasın,
    doğrudan terminal duruma gitsin diye.

    **Bu biçim bağlantıyı gönderim boyunca ELİNDE TUTAR.** Çağıranın zaten bir
    bağlantısı olduğu ve onu bırakamayacağı durumlar (testler, tek seferlik
    script'ler) içindir. Uygulama yollarında `..._via_pool` kullanılır — orada
    ağ süresi boyunca havuzdan bağlantı işgal edilmez.
    """
    if send is None:
        send = _send_to_n8n

    failed = await sweep_exhausted_admin_events(db)
    claimed = await claim_admin_events(db, limit=limit, lease_seconds=lease_seconds)

    async def _finalize(row: dict, success: bool) -> bool:
        return await finalize_admin_event(
            db,
            event_id=row["id"],
            attempt_count=row["attempt_count"],
            lease_expires_at=row["lease_expires_at"],
            success=success,
        )

    sent, deferred, lost = await _deliver_claimed(claimed, send, _finalize)
    return DispatchReport(
        claimed=len(claimed), sent=sent, deferred=deferred, failed=failed, lost=lost
    )


async def dispatch_pending_admin_events_via_pool(
    pool,
    *,
    limit: int = DEFAULT_CLAIM_LIMIT,
    lease_seconds: int = DEFAULT_LEASE_SECONDS,
    send: Sender | None = None,
) -> DispatchReport:
    """Uygulama biçimi: DB bağlantısı ağ çağrısı boyunca TUTULMAZ.

    Bağlantı yalnız iki KISA pencerede alınır — (süpür + kirala) ve her satırın
    kapatılması. Aradaki gönderim havuzun dışındadır.

    Neden önemli (checkpoint 14, F3): eski biçim bağlantıyı turun tamamı
    boyunca tutuyordu. Yavaş bir n8n ile bu, dış bağımlılığın gecikmesini kendi
    veritabanı havuzuna bulaştırır ve ALAKASIZ üretim isteklerini bekletir.
    """
    if send is None:
        send = _send_to_n8n

    async with pool.acquire() as conn:
        failed = await sweep_exhausted_admin_events(conn)
        claimed = await claim_admin_events(conn, limit=limit, lease_seconds=lease_seconds)

    async def _finalize(row: dict, success: bool) -> bool:
        async with pool.acquire() as conn:
            return await finalize_admin_event(
                conn,
                event_id=row["id"],
                attempt_count=row["attempt_count"],
                lease_expires_at=row["lease_expires_at"],
                success=success,
            )

    sent, deferred, lost = await _deliver_claimed(claimed, send, _finalize)
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

# Aynı anda EN FAZLA bir hızlı-yol işçisi koşar. Olay başına bir görev doğurmak
# (ilk yazım) havuz tüketiminin kendisiydi (checkpoint 14, F3): her görev bir DB
# bağlantısı tutuyordu ve bir olay patlaması havuzu boşaltabiliyordu. Bir tur
# koşarken gelen olaylar KAYBOLMAZ — bir sonraki tetik ya da kurtarma turu
# onları toplar (satır kalıcıdır; tetik yalnız gecikmeyi kısar).
_fast_dispatch_task: asyncio.Task[Any] | None = None


def _maybe_trigger_fast_dispatch(db) -> None:
    """Satır COMMIT'lenmişse arka planda tek dispatch turu ateşler.

    Üç kapı, hepsi fail-closed yönde:

    1. Uygulama havuzu kurulu değilse (testler, script'ler) HİÇ ateşlenmez —
       aksi hâlde bir test uygulamanın CANLI veritabanına bağlanmasını
       tetikleyebilirdi.
    2. Açık transaction içindeysek ateşlenmez: satır henüz commit edilmemiş
       olabilir ve dispatcher ya boşuna dönerdi ya da — daha kötüsü — geri
       alınacak bir işin bildirimini yollardı.
    3. Zaten koşan bir işçi varsa yenisi doğmaz (birleştirme).

    **DÜRÜST SINIR:** bu genel bir "commit sonrası" kancası DEĞİLDİR. Açık
    transaction içinde yazan çağıranlar için hızlı yol hiç koşmaz; teslimi
    kurtarma yolu (n8n schedule → `/internal/admin-events/dispatch-pending`)
    üstlenir. Teslim garantisi hızlı yola DAYANMAZ — o yalnız gecikmeyi kısar.
    """
    global _fast_dispatch_task

    if get_pool_if_ready() is None:
        return
    try:
        if db.is_in_transaction():
            return
    except AttributeError:  # pragma: no cover — bağlantı benzeri sahte nesne
        return
    if _fast_dispatch_task is not None and not _fast_dispatch_task.done():
        return

    # Kontrol ile atama arasında `await` YOK: asyncio tek görev döngüsünde
    # çalıştığı için bu dizi bölünemez, yarış doğmaz.
    _fast_dispatch_task = asyncio.create_task(_dispatch_in_background())


async def _dispatch_in_background() -> None:
    """Havuzlu biçimi koşar; her hatayı yutar — üretim akışı etkilenmez."""
    pool = get_pool_if_ready()
    if pool is None:  # pragma: no cover — havuz arada kapandıysa
        return
    try:
        await dispatch_pending_admin_events_via_pool(pool)
    except Exception as exc:  # noqa: BLE001
        logger.warning("hızlı yol dispatch başarısız (kurtarma yolu kapsar): %s", exc)
