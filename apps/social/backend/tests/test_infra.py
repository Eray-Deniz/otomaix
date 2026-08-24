"""Test altyapısı bootstrap doğrulaması (Task 1).

Kanıtladığı: `db` fixture'ı `otomaix_test` veritabanına bağlanıyor ve
migration zinciri test DB'de uçtan uca koşmuş (social.sectors mevcut).
"""


async def test_db_fixture_connects_and_sees_social_schema(db):
    assert await db.fetchval("SELECT 1") == 1

    sectors_exists = await db.fetchval(
        """
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables
            WHERE table_schema = 'social' AND table_name = 'sectors'
        )
        """
    )
    assert sectors_exists is True, "social.sectors yok — migration zinciri koşmamış"


async def test_db_fixture_targets_the_disposable_test_database(db):
    """Canlı `otomaix` veritabanına bağlanan altyapı reddedilir (invariant 2)."""
    assert await db.fetchval("SELECT current_database()") == "otomaix_test"
