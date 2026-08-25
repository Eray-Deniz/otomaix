"""Task 15b — marka ayarları kaydetme bütünlüğü (arka uç ayağı).

Sayfa müşterinin kendi doldurduğu yüzeydir; oradaki sessiz kayıp kabul edilen
risk değildir. Arka ucun buradaki payı TEK bir şeydir: **eski bir sürümün
üstüne yazılmasını reddetmek.**

Sıra bozulması iki ayrı yerden gelir:

* aynı sekmede iki isteğin ters sırada varması — bunun çözümü istemcide (tek
  uçuş kuralı), sunucuda değil;
* iki sekme / iki cihaz — bunu yalnız sunucu görebilir, çünkü sekmeler
  birbirini görmez.

Bu dosya ikincisini ölçer. Kapı İSTEĞE BAĞLIdır: sürüm göndermeyen çağıran
bugünkü davranışı aynen görür (başka yüzeyler bozulmaz).

**Bilinen sınır (doğrulanmadı, tasarımdan biliniyor):** sürüm damgası satırın
güncellenme anıdır ve bu an transaction'ın BAŞLANGIÇ zamanıdır. Aynı
mikrosaniyede başlayan iki transaction teorik olarak aynı damgayı görebilir;
tamsayı bir sayaç bu açığı da kapatırdı, zaman damgası kapatmaz. Ölçülen şey
mekanizmanın çalıştığıdır, mikrosaniye çakışmasının imkânsızlığı DEĞİL.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi import HTTPException

import asyncpg

from app.core.database import _init_connection
from app.models.schemas import BrandUpdate
from app.routers import brands as brands_router

from .conftest import _require_test_database


# Bu dosyanın açtığı satırların işareti — teardown onunla temizler.
_SEED_PREFIX = "kayit-15b-"


@pytest.fixture
async def save_db(test_db_setup):
    """COMMIT EDEN bağlantı — sarmalayıcı transaction YOK.

    Standart `db` fixture'ı her testi tek bir transaction'da koşturur. Sürüm
    damgası `now()`'dan gelir ve `now()` transaction'ın BAŞLANGIÇ anını
    döndürür; yani o düzenekte damga iki yazım arasında HİÇ ilerlemez ve kapı
    ölçülemez hâle gelir — sahte yeşil üretirdi.

    Üretimde her istek kendi transaction'ındadır (ölçüldü: ayrı
    transaction'larda damga her yazımda ilerliyor). Burada o gerçek
    yeniden kurulur; karşılığında temizlik ELLE yapılır.
    """
    connection = await asyncpg.connect(_require_test_database(test_db_setup))
    await _init_connection(connection)
    try:
        yield connection
    finally:
        # Geri sarma YOK, o yüzden temizlik elle. Bu dosyanın açtığı hesaplar
        # sabit bir önekle işaretlenir; hesabı düşürmek çalışma alanını ve
        # markaları da düşürür.
        await connection.execute(
            "DELETE FROM social.accounts WHERE email LIKE $1", f"{_SEED_PREFIX}%"
        )
        await connection.close()


async def _seed_owner_and_brand(db):
    account_id = await db.fetchval(
        "INSERT INTO social.accounts (email, name, plan_id) "
        "VALUES ($1, $2, 'pro') RETURNING id",
        f"{_SEED_PREFIX}{uuid.uuid4()}@example.test",
        "Kayıt Sahibi",
    )
    workspace_id = await db.fetchval(
        "INSERT INTO social.workspaces (account_id, name) VALUES ($1, $2) RETURNING id",
        account_id,
        "Kayıt Çalışma Alanı",
    )
    await db.execute(
        "INSERT INTO social.workspace_members (workspace_id, account_id) VALUES ($1, $2)",
        workspace_id,
        account_id,
    )
    brand_id = await db.fetchval(
        "INSERT INTO social.brands (workspace_id, name) VALUES ($1, $2) RETURNING id",
        workspace_id,
        "Kayıt Markası",
    )
    return {"sub": str(account_id)}, brand_id


async def _version(db, brand_id):
    return await db.fetchval("SELECT updated_at FROM social.brands WHERE id = $1", brand_id)


async def test_stale_write_is_rejected_and_changes_nothing(save_db):
    """İki sekme senaryosu: eski sürümü gören yazım REDDEDİLİR.

    Kritik ayak yalnız hata kodu değil, satırın DEĞİŞMEMİŞ olmasıdır — kısmen
    uygulanmış bir yazım, reddedilmiş bir yazımdan daha kötüdür.
    """
    user, brand_id = await _seed_owner_and_brand(save_db)
    stale = await _version(save_db, brand_id)

    # Başka bir sekme araya girer.
    await brands_router.update_brand(
        brand_id=brand_id,
        payload=BrandUpdate(name="İkinci sekmenin yazdığı"),
        user=user,
        db=save_db,
    )
    fresh = await _version(save_db, brand_id)
    assert fresh != stale, "sürüm damgası ilerlemedi — kapı ölçemez"

    with pytest.raises(HTTPException) as exc:
        await brands_router.update_brand(
            brand_id=brand_id,
            payload=BrandUpdate(name="Bayat sekmenin yazdığı", expected_version=stale),
            user=user,
            db=save_db,
        )

    assert exc.value.status_code == 409
    row = await save_db.fetchrow(
        "SELECT name, updated_at FROM social.brands WHERE id = $1", brand_id
    )
    assert row["name"] == "İkinci sekmenin yazdığı", "bayat yazım kısmen uygulandı"
    assert row["updated_at"] == fresh, "reddedilen yazım satıra dokundu"


async def test_current_version_is_accepted(save_db):
    """Güncel sürümü gören yazım normal geçer — kapı her şeyi reddetmiyor."""
    user, brand_id = await _seed_owner_and_brand(save_db)
    current = await _version(save_db, brand_id)

    result = (
        await brands_router.update_brand(
            brand_id=brand_id,
            payload=BrandUpdate(name="Güncel yazım", expected_version=current),
            user=user,
            db=save_db,
        )
    ).data

    assert result["name"] == "Güncel yazım"


async def test_version_free_callers_are_unaffected(save_db):
    """Sürüm göndermeyen çağıran bugünkü davranışı görür (geriye uyum)."""
    user, brand_id = await _seed_owner_and_brand(save_db)
    await brands_router.update_brand(
        brand_id=brand_id, payload=BrandUpdate(name="Sürümsüz"), user=user, db=save_db
    )
    await brands_router.update_brand(
        brand_id=brand_id, payload=BrandUpdate(name="Sürümsüz iki"), user=user, db=save_db
    )
    assert await save_db.fetchval(
        "SELECT name FROM social.brands WHERE id = $1", brand_id
    ) == "Sürümsüz iki"


async def test_conflict_is_distinguished_from_missing_brand(save_db):
    """Çakışma ile "marka yok" AYNI cevaba düşmez.

    İkisi de "satır güncellenmedi" olarak görünür; ayırmazsak silinmiş bir
    markaya yazan istemci sonsuza dek tazeleyip tekrar dener.
    """
    user, brand_id = await _seed_owner_and_brand(save_db)
    version = await _version(save_db, brand_id)
    await save_db.execute("DELETE FROM social.brands WHERE id = $1", brand_id)

    with pytest.raises(HTTPException) as exc:
        await brands_router.update_brand(
            brand_id=brand_id,
            payload=BrandUpdate(name="Yok olana yazım", expected_version=version),
            user=user,
            db=save_db,
        )
    # Sahiplik kapısı silinmiş markayı zaten 404 ile karşılar — çakışma DEĞİL.
    assert exc.value.status_code == 404


async def test_response_carries_the_new_version(save_db):
    """Yanıt YENİ sürümü taşır — istemci art arda yazabilsin diye.

    Taşımasaydı istemci her yazımdan sonra ayrıca okumak zorunda kalır, o da
    yeni bir yarış penceresi açardı.
    """
    user, brand_id = await _seed_owner_and_brand(save_db)
    first = (
        await brands_router.update_brand(
            brand_id=brand_id, payload=BrandUpdate(name="Bir"), user=user, db=save_db
        )
    ).data

    second = (
        await brands_router.update_brand(
            brand_id=brand_id,
            payload=BrandUpdate(name="İki", expected_version=first["updated_at"]),
            user=user,
            db=save_db,
        )
    ).data

    assert second["name"] == "İki"
    assert second["updated_at"] != first["updated_at"]
