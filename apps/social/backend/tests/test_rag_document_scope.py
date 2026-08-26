"""Security review 2026-08-26 / S2 — RAG doküman erişimi marka kapsamına bağlıdır.

Bulgu: `get_document_context` sorguyu yalnız doküman kimliğiyle kuruyordu. Çağıranlar
`payload.brand_id`'nin SAHİPLİĞİNİ doğruluyordu ama `payload.document_ids`'i doğrulamadan
geçiriyordu; başka kiracının doküman kimliğini bilen kimliği doğrulanmış bir kullanıcı, o
dokümanın `raw_text`'ini kendi üretim bağlamına enjekte ettirip modelden geri okutabiliyordu.
Ürün yolunda ikinci bir kapı daha açıktı: kısa video 2. aşaması ürün satırını sahiplik
filtresiyle çekiyor ama sonucu kullanmıyordu, dolayısıyla yabancı ürünün dokümanları yine
enjekte ediliyordu.

Bu dosya iddiayı POZİTİF ve NEGATİF yönde birden sınar — yalnız "reddediliyor" demek yetmez,
"meşru kullanım hâlâ çalışıyor" da kanıtlanmalı, aksi hâlde her şeyi reddeden bir fix de
testi geçerdi.

Kapsam sınırı (dürüst): buradaki kapı VERİTABANI sorgusudur, model çağrısı değil. Testler
model çağırmaz; kanıtladıkları şey yabancı metnin BAĞLAMA HİÇ GİRMEDİĞİdir.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi import HTTPException

from app.services.document_processor import (
    get_document_context,
    get_product_document_context,
)

SENTINEL = "GIZLI-ISARET-METNI-baska-kiracinin-dokumani"


async def _seed_brand(db, label: str):
    account_id = await db.fetchval(
        "INSERT INTO social.accounts (email, name) VALUES ($1, $2) RETURNING id",
        f"rag-scope-{uuid.uuid4()}@example.test",
        f"{label} Sahibi",
    )
    workspace_id = await db.fetchval(
        "INSERT INTO social.workspaces (account_id, name) VALUES ($1, $2) RETURNING id",
        account_id,
        f"{label} Çalışma Alanı",
    )
    await db.execute(
        "INSERT INTO social.workspace_members (workspace_id, account_id) VALUES ($1, $2)",
        workspace_id,
        account_id,
    )
    return await db.fetchval(
        "INSERT INTO social.brands (workspace_id, name) VALUES ($1, $2) RETURNING id",
        workspace_id,
        f"{label} Markası",
    )


async def _seed_brand_document(db, brand_id, text: str):
    return await db.fetchval(
        """
        INSERT INTO social.brand_documents (brand_id, name, file_url, raw_text)
        VALUES ($1, $2, $3, $4)
        RETURNING id
        """,
        brand_id,
        "gizli.pdf",
        "https://example.test/gizli.pdf",
        text,
    )


async def _seed_product_document(db, brand_id, text: str):
    product_id = await db.fetchval(
        """
        INSERT INTO social.brand_products (brand_id, type, name)
        VALUES ($1, 'product', $2)
        RETURNING id
        """,
        brand_id,
        "Gizli Ürün",
    )
    await db.execute(
        """
        INSERT INTO social.product_documents (product_id, filename, file_url, file_key, raw_text)
        VALUES ($1, $2, $3, $4, $5)
        """,
        product_id,
        "urun-gizli.pdf",
        "https://example.test/urun-gizli.pdf",
        f"products/{product_id}/urun-gizli.pdf",
        text,
    )
    return product_id


# ── Marka dokümanları ───────────────────────────────────────────────────────


async def test_foreign_brand_document_is_rejected(db):
    """Yabancı dokümanın kimliğini bilmek yetmez: istek 404 ile TAMAMEN reddedilir."""
    victim = await _seed_brand(db, "Kurban")
    attacker = await _seed_brand(db, "Saldırgan")
    foreign_doc = await _seed_brand_document(db, victim, SENTINEL)

    with pytest.raises(HTTPException) as exc:
        await get_document_context([foreign_doc], "her neyse", db, brand_id=attacker)

    assert exc.value.status_code == 404


async def test_own_brand_document_still_works(db):
    """Pozitif kontrol: meşru okuma bozulmadı (her şeyi reddeden fix bu testi geçemez)."""
    brand = await _seed_brand(db, "Sahip")
    own_doc = await _seed_brand_document(db, brand, "kendi dokümanımın metni")

    context = await get_document_context([own_doc], "her neyse", db, brand_id=brand)

    assert "kendi dokümanımın metni" in context


async def test_mixed_own_and_foreign_leaks_nothing(db):
    """En kritik hâl: kendi dokümanıyla yabancıyı karıştırmak KISMİ sonuç döndürmez.

    Kısmi sonuç dönmek iki şeyi birden yapardı — yabancı metni sızdırmasa bile hangi
    kimliğin var olduğunu söylerdi, ve saldırgana ayıklama imkânı verirdi.
    """
    victim = await _seed_brand(db, "Kurban")
    attacker = await _seed_brand(db, "Saldırgan")
    foreign_doc = await _seed_brand_document(db, victim, SENTINEL)
    own_doc = await _seed_brand_document(db, attacker, "kendi metnim")

    with pytest.raises(HTTPException) as exc:
        await get_document_context(
            [own_doc, foreign_doc], "her neyse", db, brand_id=attacker
        )

    assert exc.value.status_code == 404


async def test_scope_is_not_optional(db):
    """Kapsam parametresi ZORUNLU: yeni bir çağıran unutursa sızdırmaz, hata verir."""
    brand = await _seed_brand(db, "Sahip")
    doc = await _seed_brand_document(db, brand, "metin")

    with pytest.raises(TypeError):
        await get_document_context([doc], "her neyse", db)  # type: ignore[call-arg]


# ── Ürün dokümanları ────────────────────────────────────────────────────────


async def test_foreign_product_documents_are_rejected(db):
    """Yabancı ürünün dokümanları bağlama giremez (kısa video yolundaki ikinci kapı)."""
    victim = await _seed_brand(db, "Kurban")
    attacker = await _seed_brand(db, "Saldırgan")
    foreign_product = await _seed_product_document(db, victim, SENTINEL)

    with pytest.raises(HTTPException) as exc:
        await get_product_document_context(
            [foreign_product], "her neyse", db, brand_id=attacker
        )

    assert exc.value.status_code == 404


async def test_own_product_documents_still_work(db):
    """Pozitif kontrol: kendi ürününün dokümanı hâlâ bağlama giriyor."""
    brand = await _seed_brand(db, "Sahip")
    product = await _seed_product_document(db, brand, "kendi ürün metnim")

    context = await get_product_document_context(
        [product], "her neyse", db, brand_id=brand
    )

    assert "kendi ürün metnim" in context


async def test_foreign_product_without_documents_is_still_rejected(db):
    """Ürün kapısını ayrıca ölçen hâl: dokümansız YABANCI ürün de 404 alır.

    Doküman sorgusundaki JOIN zaten yabancı metni engelliyor (savunma derinliği), ama
    ürünün hiç dokümanı yoksa o sorguya HİÇ gidilmez — kapı olmasa sessizce boş bağlam
    dönerdi ve "bu ürün senin değil" bilgisi kaybolurdu. Bu test o kapıyı ölçer:
    kapı kaldırılırsa DÜŞER, sınıfı kapatan diğer kapı bu vakayı görmez.
    """
    victim = await _seed_brand(db, "Kurban")
    attacker = await _seed_brand(db, "Saldırgan")
    empty_foreign_product = await db.fetchval(
        """
        INSERT INTO social.brand_products (brand_id, type, name)
        VALUES ($1, 'product', 'Dokümansız Ürün')
        RETURNING id
        """,
        victim,
    )

    with pytest.raises(HTTPException) as exc:
        await get_product_document_context(
            [empty_foreign_product], "her neyse", db, brand_id=attacker
        )

    assert exc.value.status_code == 404


async def test_own_product_without_documents_returns_empty(db):
    """Pozitif kontrol: kendi dokümansız ürünün hata değil BOŞ bağlam döndürür."""
    brand = await _seed_brand(db, "Sahip")
    product = await db.fetchval(
        """
        INSERT INTO social.brand_products (brand_id, type, name)
        VALUES ($1, 'product', 'Dokümansız Ürün')
        RETURNING id
        """,
        brand,
    )

    assert await get_product_document_context(
        [product], "her neyse", db, brand_id=brand
    ) == ""


# ── Kısa video ürün görseli (kapanış turu bulgusu) ──────────────────────────


async def _seed_product_with_image(db, brand_id, image_url: str):
    return await db.fetchval(
        """
        INSERT INTO social.brand_products (brand_id, type, name, image_url)
        VALUES ($1, 'product', $2, $3)
        RETURNING id
        """,
        brand_id,
        "Görselli Ürün",
        image_url,
    )


async def test_foreign_product_image_is_not_used(db):
    """Yabancı ürünün GÖRSELİ video hattına giremez.

    Doküman yolu kapatılmıştı ama aynı sınıfın görsel ayağı açıktı: iki kısa
    video yolu da ürünü `WHERE id = $1` ile okuyordu. Kimliği bilen kiracı,
    başkasının ürün görselinden türetilmiş video ürettirebiliyordu.
    """
    from app.services.short_video import _owned_product_image

    victim = await _seed_brand(db, "Kurban")
    attacker = await _seed_brand(db, "Saldırgan")
    foreign = await _seed_product_with_image(db, victim, "https://cdn.test/gizli.jpg")

    assert await _owned_product_image(db, foreign, attacker) == ""


async def test_own_product_image_is_used(db):
    """Pozitif kontrol: kendi ürününün görseli hâlâ kullanılıyor."""
    from app.services.short_video import _owned_product_image

    brand = await _seed_brand(db, "Sahip")
    product = await _seed_product_with_image(db, brand, "https://cdn.test/benim.jpg")

    assert await _owned_product_image(db, product, brand) == "https://cdn.test/benim.jpg"
