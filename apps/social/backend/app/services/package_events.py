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

import logging
from typing import Any
from uuid import UUID

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

# `detail` şekil kapısı. Sınır POZİTİF bir sözleşmedir, negatif bir yüklem
# DEĞİL: "bu metin paket içeriği değildir"i serbest metinden kanıtlamaya
# çalışan bir kapı yakınsamaz (bu yürütmede beş tur boyunca ölçüldü). Paket
# içeriği iç içe ve uzundur; skaler-değerli ve kısa bir sözlük şartı onu
# ANLAMINA hiç bakmadan dışarıda tutar.
DETAIL_VALUE_TYPES = (str, int, float, bool, type(None))
DETAIL_MAX_TEXT = 200


class PackageEventContractError(ValueError):
    """Olay kaydı sözleşmesi ihlal edildi — çağıranın hatası."""


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


async def _is_replacement_activation(db, *, sector_id: UUID, package_id: UUID) -> bool:
    """Bu aktivasyon bir devir teslim mi, yoksa yerine geçtiği bir şey yok mu.

    Soru ÇAĞIRANA sorulmaz, paket tablosundan okunur. Ayrı bir "bu bir
    yerine-geçmedir" bayrağı ile `from_version` iki ayrı beyandır ve
    çelişebilirler; ikisini tek ölçüye bağlamak o sınıfı kapatır (K-01b
    disiplini).

    **Ölçü: sektörde ŞU AN aktif olan başka bir paket var mı.** İlk yazımda
    ölçü "arşivlenmiş satır var mı" idi ve o vekil ölçü yanlıştı: acil geri
    çekme (K-38) sonrası sektörde arşivlenmiş satır KALIR ama aktif satır
    kalmaz, dolayısıyla sonraki aktivasyon yerine geçtiği bir şey olmadan
    "devir teslim" sayılıp reddediliyordu — meşru bir yol kapalıydı (Task 13
    ölçtü). "Yerine geçilen sürüm" tanım gereği geçiş anında AKTİF olandır.

    **Sıra bağımlılığı — sözleşmenin parçası:** ölçü yalnız durum geçişi
    UYGULANMADAN ÖNCE doğrudur. Tek yazıcı `_apply_status_transition`'dır ve
    olayı geçişten önce yazar; sıra tersine çevrilirse bu ölçü çöker.
    """
    return bool(
        await db.fetchval(
            """
            SELECT EXISTS (
                SELECT 1 FROM social.sector_packages
                WHERE sector_id = $1 AND id <> $2 AND status = 'active'
            )
            """,
            sector_id,
            package_id,
        )
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
        if from_version is None:
            _require(
                not await _is_replacement_activation(
                    db, sector_id=sector_id, package_id=package_id
                ),
                "activation: yerine-geçme aktivasyonunda from_version zorunlu "
                "(sektörde arşivlenmiş paket var)",
            )
    elif event_type == "rollback":
        _require(from_version is not None, "rollback: from_version (arşivlenen kaynak) zorunlu")
        _require(to_version is not None, "rollback: to_version (geri getirilen hedef) zorunlu")
    elif event_type == "deactivation":
        _require(from_version is not None, "deactivation: from_version zorunlu")
        _require(to_version is None, "deactivation: hedef sürüm YOKTUR, to_version NULL olmalı")


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
        await _validate_version_shape(
            db,
            event_type=event_type,
            sector_id=sector_id,
            package_id=package_id,
            from_version=from_version,
            to_version=to_version,
        )

    try:
        return await db.fetchval(
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
