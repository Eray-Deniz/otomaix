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


# TANIM, KULLANIMDAN ÖNCE — ve bu bir DÜZELTMEDİR (fix turu 2, N1). Sınıf
# eskiden dosyanın ortasındaydı ama modül gövdesindeki bütünlük kapısı ondan
# ÖNCE koşuyordu (satır 122 < 150). Kapı fail-closed'dı — import yine düşüyordu
# — ama operatörün gördüğü şey ÖLÇÜLDÜ:
#     NameError: name 'PackageEventContractError' is not defined
# Yani NEYİN beyan edilmediğini söyleyen cümle import anında HİÇ görünmüyordu,
# fonksiyonun docstring'i fırlatılamayan bir tür vaat ediyordu ve import'u
# `except PackageEventContractError` ile sarmak işe yaramazdı. Sınıfın buraya
# taşınması tek hamlede üçünü birden kapatır.
class PackageEventContractError(ValueError):
    """Olay kaydı sözleşmesi ihlal edildi — çağıranın hatası."""


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

# ONAY kapsamı (K-99, migration 036). `LIFECYCLE_EVENTS`e KATILMADI ve bu
# bilinçlidir: yaşam döngüsü olayları paketin DURUM GEÇİŞLERİDİR ve sürüm
# alanları onlara ÖZGÜ doğrulanır (F22 — `_validate_version_shape`). Onay/ret
# bir koşunun kapı kararıdır, sürüm değiştirmez; `LIFECYCLE_EVENTS`e eklemek
# ya o kümenin "üçü de sürüm taşır" sözleşmesini bozardı ya da tür-özgü
# dalların hiçbirine uymayan iki sessiz üye bırakırdı.
#
# KAPSAM GEREKSİNİMİ AYNIDIR (sector_id + package_id + actor): aşağıdaki kapı
# marka-kapsamlı OLMAYAN her türe onu uygular. Kim onayladı ve HANGİ paketi
# onayladı sorularının cevabı olmayan bir onay kaydı, modülün başında
# reddedilen "yarım denetim izi"nin ta kendisidir.
APPROVAL_EVENTS = frozenset({"approval", "rejection"})

EVENT_TYPES = BRAND_SCOPED_EVENTS | LIFECYCLE_EVENTS | APPROVAL_EVENTS

# ─── Sürüm sözleşmesi TÜR BAŞINA BEYAN EDİLİR (fix turu 1, I2) ──────────────
#
# ÖLÇÜLEN KUSUR: `_validate_version_shape` kapalı bir
# `if activation / elif rollback / elif deactivation` zinciriydi ve `else`
# TAŞIMIYORDU. `EVENT_TYPES`e giren `approval`/`rejection` hiçbir dala uymuyor,
# doğrulamadan SESSİZCE geçiyordu:
#
#     log_package_event(..., event_type="approval", from_version=999, to_version=-5)
#
# UYDURMA sürüm numaraları taşıyan KALICI bir denetim satırı yazıyordu. Aynı
# çağrı `activation` ile gerçek aktif sürüme karşı TAM EŞLEŞME ile
# reddediliyordu — asimetri tam da denetim izindeydi. 033'te sürüm kolonlarına
# DB CHECK'i de YOKTUR, yani ikinci bir kapı da devrede değildi.
#
# DÜZELTİLEN ŞEY VARYANT DEĞİL SINIFTIR: sorun iki türün unutulması değil,
# `else`siz zincirin yarın eklenecek DÖRDÜNCÜ türü de aynı sessizlikle
# geçirecek olmasıydı. Bu yüzden dal eklenmedi, SÖZLEŞME BEYANI zorunlu kılındı.
#
# İki değer:
#   * `gecis`     — tür bir sürüm geçişidir; alanlar TÜRE ÖZGÜ doğrulanır (F22).
#   * `surumsuz`  — tür sürüm taşımaz; İKİ alan da NULL olmak ZORUNDA.
#
# Onay/ret `surumsuz`dur: onay bir koşunun kapı kararıdır, paketin sürümünü
# DEĞİŞTİRMEZ. "Boş bırakılabilir" değil "boş olmak zorunda": nullable bir alan
# uydurma bir değeri kabul eder ve denetim izi yalan söyler — modülün başındaki
# "yarım iz, izin hiç olmamasından daha kötüdür" hükmünün doğrudan karşılığı.
#
# DB CHECK'İ EKLENMEDİ, bilinçli. GEREKÇE DEĞİŞMEDİ; ARİTMETİĞİ fix turu 2'den
# sonra bayatlamıştı ve burada düzeltildi (fix turu 3, R2).
#
# Bugün on iki türün DOKUZU `surumsuz`dur ve onların sözleşmesi ("iki sürüm
# alanı da NULL") bir CHECK'te İFADE EDİLEBİLİR. Kalan ÜÇÜ (`gecis`)
# İLİŞKİSELDİR — `from_version`, olayın yazıldığı ANDA canlı olan aktif sürümle
# TAM EŞLEŞMEK zorundadır — ve bu bir CHECK'te İFADE EDİLEMEZ.
#
# İlk yazım "yalnız YARISI ifade edilebilir" diyordu; o oran İKİ tür
# `surumsuz`ken doğruydu, dokuz türken değil.
#
# Karar oranın büyüklüğünden DEĞİL, BÖLÜNMENİN KENDİSİNDEN gelir: ifade
# edilebilen dokuzu DB'ye, edilemeyen üçü Python'a koymak AYNI sözleşmeyi iki
# katmana böler ve iki ölçünün ıraksamasına izin verir (K-01b) — sözleşme
# değişince biri güncellenir, diğeri unutulur. Üstelik bütünlük kapısı
# eksik/ölü bir PYTHON beyanını yakalar; bayat bir DB CHECK'ini yakalayan
# HİÇBİR ŞEY olmazdı. Oranın 2/5'ten 9/12'ye çıkması bu riski AZALTMAZ,
# sözleşmenin daha BÜYÜK bir kısmını ikizlenmiş hâle getirir.
#
# Kalan risk dürüstçe: ham SQL bu kapıyı atlar — on iki türün HEPSİ için.
EVENT_VERSION_CONTRACT: dict[str, str] = {
    # Yaşam döngüsü — sürüm GEÇİŞİ; alanlar türe özgü doğrulanır (F22).
    "activation": "gecis",
    "rollback": "gecis",
    "deactivation": "gecis",
    # Onay kapısı — geçiş YOK.
    "approval": "surumsuz",
    "rejection": "surumsuz",
    # Marka-kapsamlı tanı olayları — geçiş YOK (fix turu 2, N2).
    "mismatch_fallthrough": "surumsuz",
    "package_read_error": "surumsuz",
    "stale_assignment_fallback": "surumsuz",
    "stamp_missing": "surumsuz",
    "stamp_invalid": "surumsuz",
    "stamp_stale_at_persist": "surumsuz",
}


def assert_version_contract_is_total(event_types, contract) -> None:
    """`EVENT_TYPES`in HER üyesi sürüm sözleşmesini BEYAN ETMİŞ olmalı.

    Kapanış sayarak değil YAPIYLA: eşleme kümenin TAMAMIYLA birebir aynı olmak
    zorundadır. Eksik beyan da (yeni tür doğrulamadan kaçar) ölü beyan da
    (kümeden çıkmış tür için kural durur) bulgudur. MODÜL YÜKLENİRKEN koşar:
    beyansız bir tür eklemek import'u düşürür, kusur çalışma zamanına kadar
    bekleyemez.

    `brand_scoped` PARAMETRESİ KALDIRILDI (fix turu 2, N2). Kıyas eskiden
    `event_types - brand_scoped` idi, yani sınıfın YARISI kapalıydı ve
    "kapanış yapıyla" iddiası yarı doğruydu. Muafiyeti bir parametre olarak
    taşımak, onu yanlışlıkla geri vermeyi de mümkün kılıyordu; bugün kapıya bir
    ALT KÜME geçirilemez.
    """
    beklenen = set(event_types)
    if set(contract) != beklenen:
        raise PackageEventContractError(
            "surum sozlesmesi BEYAN EDILMEMIS tur(ler) var — "
            f"eksik: {sorted(beklenen - set(contract))}, "
            f"olu beyan: {sorted(set(contract) - beklenen)}"
        )


assert_version_contract_is_total(EVENT_TYPES, EVENT_VERSION_CONTRACT)

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
    db,
    *,
    event_type: str,
    sector_id: UUID | None,
    package_id: UUID | None,
    from_version,
    to_version,
) -> None:
    """Sürüm alanları OLAY TÜRÜNE ÖZGÜdür (F22).

    Sınır geçişleri sentinel değerle temsil edilmez: "kaynak yok" NULL'dır,
    "hedef yok" NULL'dır. Uydurma bir `0` ya da `-1` denetim izini bozardı.

    TÜR BAŞINA SÖZLEŞME `EVENT_VERSION_CONTRACT`ten OKUNUR (fix turu 1, I2).
    Beyansız bir tür buraya kadar gelirse SQL'e VARMADAN reddedilir; önceki
    `else`siz zincir onu sessizce geçiriyordu.

    KAPSAM SINIFINDAN BAĞIMSIZ ÇAĞRILIR (fix turu 2, N2): marka-kapsamlı türler
    de buradan geçer. `sector_id`/`package_id` onlar için `None` olabilir ve bu
    güvenlidir — `surumsuz` kolu ikisine de DOKUNMADAN döner; imza o yüzden
    `None`u da kabul eder.
    """
    kontrat = EVENT_VERSION_CONTRACT.get(event_type)
    _require(
        kontrat is not None,
        f"{event_type}: sürüm sözleşmesi BEYAN EDİLMEMİŞ — paket-kapsamlı her "
        "tür `EVENT_VERSION_CONTRACT`te `gecis` ya da `surumsuz` olarak "
        "beyan edilmek ZORUNDA (doğrulanmamış tür denetim izine uydurma sürüm "
        "yazar)",
    )

    if kontrat == "surumsuz":
        _require(
            from_version is None,
            f"{event_type}: sürüm GEÇİŞİ taşımaz, from_version NULL olmalı "
            f"(verilen {from_version!r})",
        )
        _require(
            to_version is None,
            f"{event_type}: sürüm GEÇİŞİ taşımaz, to_version NULL olmalı "
            f"(verilen {to_version!r})",
        )
        return

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
    else:
        # DAĞITIM SEVİYESİ fix turu 1-2'de kapandı; bu `else` KOLUN KENDİ
        # zincirini kapatır (fix turu 3, R1). Bugünkü on iki tür için
        # ATEŞLENEMEZ — üç `gecis` türünün üçünün de dalı var — ama açık bırakılan
        # bir eksendi: ölçüldü ki dördüncü bir `gecis` türü beyan edilip
        # `from_version=999, to_version=-5` ile çağrıldığında Python kapısı KABUL
        # ediyor, yazım SQL'e ulaşıyor ve yalnız veritabanının kapalı tür CHECK'i
        # durduruyordu. O CHECK gerçek bir yeni türle BİRLİKTE genişletileceği
        # için dayanıklı bir ikinci hat DEĞİLDİR — yani tür eklendiği gün kapı
        # sessizce açılırdı. I2'nin gereği "yarın eklenen tür doğrulamadan
        # KAÇAMASIN"dı; bu satır onu bu seviyede de bitirir.
        raise PackageEventContractError(
            f"{event_type}: `gecis` BEYAN EDİLDİ ama SÜRÜM DALI YOK — geçiş "
            "türlerinin sürüm alanları TÜRE ÖZGÜ doğrulanır (F22) ve dalı "
            "olmayan bir tür, denetim izine doğrulanmadan yazılırdı. Türü "
            "`surumsuz` olarak beyan edin ya da bu zincire kendi dalını ekleyin."
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

    # SÜRÜM ŞEKLİ KAPSAM SINIFINDAN BAĞIMSIZDIR (fix turu 2, N2). Çağrı eskiden
    # yukarıdaki `else`in İÇİNDEYDİ, yani marka-kapsamlı altı tür hiç
    # doğrulanmıyordu; ölçüldü ki `stamp_missing` uydurma sürüm numaralarıyla
    # KALICI bir denetim satırı yazabiliyordu. Kapsam gereksinimleri (yukarıda)
    # sınıfa özgü KALIR; değişen tek şey, sürüm kapısının her tür için koşması.
    #
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
