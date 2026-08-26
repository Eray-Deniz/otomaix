"""Kalıcı paket olay kaydı (spec §14.4, plan Task 12).

Task 8-11'de geçici `logger.*` çağrılarıyla işaretlenen olaylar buraya bağlanır.
Fark, log ile denetim izi arasındaki farktır: log dönerek kaybolur, olay kaydı
"bu markanın üretimi şu tarihte paketsiz yola düştü" sorusunu aylar sonra da
cevaplar.

**İki hata sınıfı ayrı ele alınır ve bu bilinçlidir:**

* **Sözleşme ihlali** (çağıranın hatası: bilinmeyen tür, eksik kapsam alanı,
  çelişkili sürüm şekli) → `PackageEventContractError` ATILIR. Bunlar kodun
  yanlış olduğunu söyler; sessizce yutmak yarım bir denetim izi üretir ve
  yarım iz, izin hiç olmamasından daha kötüdür — var gibi görünür.
* **Altyapı hatası** (tablo erişilemiyor, bağlantı düştü) → YUTULUR, log'a
  düşer, `None` döner. Kullanıcının içeriğini bir denetim satırı yazılamadı
  diye düşürmek orantısızdır.
"""

from __future__ import annotations

import contextlib
import logging
from typing import Any
from uuid import UUID

from app.services import notifications

logger = logging.getLogger(__name__)

# ─── Kapalı olay kümesi ve iki kapsam sınıfı (F21) ──────────────────────────

# MARKA-kapsamlı: hangi markanın üretimi etkilendiğini söylerler. Markasız bir
# `stamp_invalid` kaydı hiçbir soruyu cevaplamaz.
BRAND_SCOPED_EVENTS = frozenset({
    "mismatch_fallthrough",
    "package_read_error",
    "stale_assignment_fallback",
    "stamp_missing",
    "stamp_invalid",
    "stamp_stale_at_persist",
})

# PAKET-kapsamlı yaşam döngüsü: sıfır, bir ya da çok markayı etkileyebilir.
# Fan-out YAPILMAZ — tek paket-kapsamlı satır yazılır. İlk aktivasyon marka
# atamasından ÖNCE meşru olduğu için `brand_id` burada opsiyoneldir.
LIFECYCLE_EVENTS = frozenset({"activation", "rollback", "deactivation"})

EVENT_TYPES = BRAND_SCOPED_EVENTS | LIFECYCLE_EVENTS

# K-56: bu üç olay HER OLUŞTA bir yönetici bildirimi (outbox satırı) üretir —
# eşik/oran YOKTUR (olay-bazlı, spec §14.4). Damga olayları (`stamp_*`) bu
# kümede DEĞİLDİR: onlar atıf muhasebesidir, "paketli üretim beklendiği gibi
# çalışmadı" sınıfına girmezler.
#
# Bağ TEK KAPIDADIR, çağrı yerlerinde değil. Fan-out'u `_record_event` gibi
# sarmalayıcılara ya da tek tek uçlara koymak, yarın eklenecek bir çağrı
# yerinin bildirimi sessizce atlamasına izin verirdi — sınıf kapatılır,
# varyant değil.
ADMIN_NOTIFIED_EVENTS = frozenset({
    "mismatch_fallthrough",
    "package_read_error",
    "stale_assignment_fallback",
})

# `detail` şekil kapısı. Sınır POZİTİF bir sözleşmedir, negatif bir yüklem
# DEĞİL: "bu metin paket içeriği değildir"i serbest metinden kanıtlamaya
# çalışan bir kapı yakınsamaz (bu yürütmede beş tur boyunca ölçüldü). Paket
# içeriği iç içe ve uzundur; skaler-değerli ve kısa bir sözlük şartı onu
# ANLAMINA hiç bakmadan dışarıda tutar.
DETAIL_VALUE_TYPES = (str, int, float, bool, type(None))
DETAIL_MAX_TEXT = 200


class PackageEventContractError(ValueError):
    """Olay kaydı sözleşmesi ihlal edildi — çağıranın hatası."""


def _savepoint_if_in_tx(db):
    """İç transaction YALNIZ çağıranın transaction'ı VARSA açılır.

    Savepoint'in tek işi DIŞTAKİ transaction'ı korumaktır; dışarıda transaction
    yoksa korunacak bir şey de yoktur. Koşulsuz açmak zararsız GÖRÜNÜYORDU ama
    değildi ve kapanış turu ölçtü: `db.transaction()` transaction DIŞINDA
    savepoint değil GERÇEK transaction açar, o sırada `is_in_transaction()`
    `True` döner, ve `notifications._maybe_trigger_fast_dispatch` tam da o
    kapıyı taşır ("açık transaction içindeysek ateşleme"). Sonuç: yönetici
    bildiriminin hızlı gönderim yolu bu yüzeyin TAMAMINDA sessizce ölmüştü —
    teslim garantisi değil (onu kurtarma yolu üstlenir) ama tasarlanmış gecikme
    kısaltması. Kendi düzeltmemin yan etkisiydi.

    `getattr` geri düşüşü bilinçli: bağlantı benzeri sahte nesneler (testlerdeki
    yazım-düşer sahtesi) `is_in_transaction` taşımaz ve transaction'ları da
    yoktur — onlar için doğru cevap "savepoint açma"dır.
    """
    in_tx = getattr(db, "is_in_transaction", lambda: False)()
    return db.transaction() if in_tx else contextlib.nullcontext()


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise PackageEventContractError(message)


def _validate_detail(detail: Any) -> None:
    if detail is None:
        return
    _require(isinstance(detail, dict), f"detail sözlük olmalı, {type(detail).__name__} verildi")
    for key, value in detail.items():
        _require(isinstance(key, str), f"detail anahtarı metin olmalı: {key!r}")
        _require(
            isinstance(value, DETAIL_VALUE_TYPES),
            f"detail[{key!r}] skaler olmalı ({type(value).__name__} verildi) — "
            "paket içeriği olay kaydına basılmaz",
        )
        if isinstance(value, str):
            _require(
                len(value) <= DETAIL_MAX_TEXT,
                f"detail[{key!r}] {DETAIL_MAX_TEXT} karakteri aşıyor — "
                "olay kaydı bir kopya deposu değildir",
            )


async def _active_version_excluding(db, *, sector_id: UUID, package_id: UUID) -> int | None:
    """Sektörde ŞU AN aktif olan BAŞKA paketin sürümü; yoksa `None`.

    Soru ÇAĞIRANA sorulmaz, paket tablosundan okunur. Ayrı bir "bu bir
    yerine-geçmedir" bayrağı ile `from_version` iki ayrı beyandır ve
    çelişebilirler; ikisini tek ölçüye bağlamak o sınıfı kapatır (K-01b
    disiplini).

    **Sıra bağımlılığı — sözleşmenin parçası:** ölçü yalnız durum geçişi
    UYGULANMADAN ÖNCE doğrudur. Tek yazıcı `_apply_status_transition`'dır ve
    olayı geçişten önce yazar.

    İlk yazımda ölçü "arşivlenmiş satır var mı" idi ve o vekil ölçü yanlıştı:
    acil geri çekme (K-38) sonrası sektörde arşivlenmiş satır KALIR ama aktif
    satır kalmaz, dolayısıyla sonraki aktivasyon yerine geçtiği bir şey olmadan
    "devir teslim" sayılıp reddediliyordu — meşru bir yol kapalıydı (Task 13
    ölçtü). "Yerine geçilen sürüm" tanım gereği geçiş anında AKTİF olandır.
    """
    return await db.fetchval(
        """
        SELECT version FROM social.sector_packages
        WHERE sector_id = $1 AND id <> $2 AND status = 'active'
        """,
        sector_id,
        package_id,
    )


async def _validate_version_shape(
    db, *, event_type: str, sector_id: UUID, package_id: UUID, from_version, to_version
) -> None:
    """Sürüm alanları OLAY TÜRÜNE ÖZGÜdür (F22).

    Sınır geçişleri sentinel değerle temsil edilmez: "kaynak yok" NULL'dır,
    "hedef yok" NULL'dır. Uydurma bir `0` ya da `-1` denetim izini bozardı.
    """
    if event_type == "activation":
        _require(to_version is not None, "activation: to_version zorunlu")
        # TAM EŞLEŞME. Yalnız "from_version yoksa itiraz et" demek asimetrikti
        # (checkpoint 13, F3): boş olmayan HERHANGİ bir değer — alakasız bir
        # sürüm dahil — hiç denetlenmeden geçiyordu. Denetim izinde uydurma bir
        # kaynak sürüm, eksik kaynak sürüm kadar zararlıdır.
        actual = await _active_version_excluding(
            db, sector_id=sector_id, package_id=package_id
        )
        _require(
            from_version == actual,
            f"activation: from_version gerçek aktif sürümle eşleşmeli "
            f"(beklenen {actual!r}, verilen {from_version!r}) — "
            "olay geçişten ÖNCE yazılır; bu uyuşmazlık ya yanlış kaynak sürüm "
            "ya da bozulmuş yazım sırası demektir",
        )
    elif event_type == "rollback":
        _require(to_version is not None, "rollback: to_version (geri getirilen hedef) zorunlu")
        actual = await _active_version_excluding(
            db, sector_id=sector_id, package_id=package_id
        )
        _require(
            from_version is not None and from_version == actual,
            f"rollback: from_version arşivlenen aktif sürüm olmalı "
            f"(beklenen {actual!r}, verilen {from_version!r})",
        )
    elif event_type == "deactivation":
        _require(to_version is None, "deactivation: hedef sürüm YOKTUR, to_version NULL olmalı")
        own = await db.fetchval(
            "SELECT version FROM social.sector_packages WHERE id = $1 AND status = 'active'",
            package_id,
        )
        _require(
            from_version is not None and from_version == own,
            f"deactivation: from_version geri çekilen aktif sürüm olmalı "
            f"(beklenen {own!r}, verilen {from_version!r})",
        )


async def log_package_event(
    db,
    *,
    event_type: str,
    sector_id: UUID | None = None,
    brand_id: UUID | None = None,
    package_id: UUID | None = None,
    from_version: int | None = None,
    to_version: int | None = None,
    actor: str | None = None,
    detail: dict | None = None,
) -> UUID | None:
    """Olayı kalıcı kaydeder; yazılan satırın kimliğini döner.

    Sözleşme ihlalinde `PackageEventContractError` atar. Altyapı hatasında
    `None` döner ve log'a düşer — çağıran akışı DÜŞÜRMEZ.
    """
    _require(event_type in EVENT_TYPES, f"bilinmeyen olay türü: {event_type!r}")
    _validate_detail(detail)

    if event_type in BRAND_SCOPED_EVENTS:
        _require(brand_id is not None, f"{event_type}: marka-kapsamlı olay brand_id ister (F21)")
    else:
        _require(sector_id is not None, f"{event_type}: yaşam döngüsü olayı sector_id ister")
        _require(package_id is not None, f"{event_type}: yaşam döngüsü olayı package_id ister")
        _require(bool(actor), f"{event_type}: yaşam döngüsü olayı actor ister")
        assert sector_id is not None and package_id is not None  # yukarıdaki kapılar
        # SAVEPOINT (review 2026-08-26, H2). Bu okumalar çağıranın transaction'ı
        # İÇİNDE koşabilir. Başarısız bir ifade PostgreSQL'de transaction'ı abort
        # durumuna sokar ve sonraki HER komut `current transaction is aborted` ile
        # düşer — asyncpg kendiliğinden savepoint AÇMAZ (ölçüldü 18.3'te). İç
        # transaction bir SAVEPOINT'tir: hata yalnız buraya kadar geri sarılır,
        # dıştaki post yazımı ayakta kalır. İstisna akışı DEĞİŞMEZ — ne yakalanır
        # ne yutulur, yalnız dıştaki transaction zehirlenmez.
        async with _savepoint_if_in_tx(db):
            await _validate_version_shape(
                db,
                event_type=event_type,
                sector_id=sector_id,
                package_id=package_id,
                from_version=from_version,
                to_version=to_version,
            )

    try:
        # SAVEPOINT (aynı gerekçe): aşağıdaki `except` altyapı hatasını yutup
        # `None` döner ve sözleşmesi "çağıran akışı DÜŞÜRMEZ"dir. Savepoint
        # olmadan bu söz YALNIZ transaction dışında doğruydu: içeride yutulan
        # hata dıştaki INSERT'ü de düşürüyordu, yani koruma tersine çalışıyordu.
        async with _savepoint_if_in_tx(db):
            event_id = await db.fetchval(
                """
                INSERT INTO social.package_events
                    (event_type, sector_id, brand_id, package_id,
                     from_version, to_version, actor, detail)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                RETURNING id
                """,
                event_type,
                sector_id,
                brand_id,
                package_id,
                from_version,
                to_version,
                actor,
                detail,
            )
    except Exception as exc:
        logger.error(
            "paket olayı yazılamadı (event_type=%s brand_id=%s package_id=%s): %s",
            event_type,
            brand_id,
            package_id,
            exc,
        )
        return None

    if event_id is not None and event_type in ADMIN_NOTIFIED_EVENTS:
        await _notify_admin(
            db,
            event_id=event_id,
            event_type=event_type,
            sector_id=sector_id,
            brand_id=brand_id,
            package_id=package_id,
            detail=detail,
        )
    return event_id


async def _notify_admin(
    db,
    *,
    event_id: UUID,
    event_type: str,
    sector_id: UUID | None,
    brand_id: UUID | None,
    package_id: UUID | None,
    detail: dict | None,
) -> None:
    """Olayı yönetici bildirim outbox'ına yazar — ASLA akışı düşürmez.

    Aynı transaction'dadır: olay kaydı geri alınırsa bildirim de yoktur.
    `idempotency_key` olay kimliğidir; olay satırı zaten tekil olduğu için
    ikinci bir tekillik ölçüsü uydurmaya gerek yok ve iki ölçü ıraksayamaz.

    Payload paket İÇERİĞİ taşımaz: `detail` zaten skaler-değerli kısa bir
    sözlüktür (şekil kapısı yukarıda), buraya olduğu gibi geçer.
    """
    try:
        # SAVEPOINT (review 2026-08-26, H2): "ASLA akışı düşürmez" sözü, çağıranın
        # transaction'ı içinde savepoint OLMADAN tutmuyordu — yutulan hata dıştaki
        # yazımı da düşürüyordu. Aynı transaction'da kalma sözleşmesi korunur:
        # savepoint dıştakinin İÇİNDEDİR, olay geri alınırsa bildirim de yoktur.
        async with _savepoint_if_in_tx(db):
            await notifications.record_admin_event(
                db,
                kind=f"package_event.{event_type}",
                payload={
                    "event_id": str(event_id),
                    "event_type": event_type,
                    "sector_id": str(sector_id) if sector_id else None,
                    "brand_id": str(brand_id) if brand_id else None,
                    "package_id": str(package_id) if package_id else None,
                    "detail": detail,
                },
                idempotency_key=f"package_event:{event_id}",
            )
    except Exception as exc:  # noqa: BLE001
        logger.error(
            "yönetici bildirimi yazılamadı (event_type=%s event_id=%s): %s",
            event_type,
            event_id,
            exc,
        )
