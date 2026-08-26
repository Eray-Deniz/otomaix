"""Test altyapısı bootstrap doğrulaması (Task 1).

Kanıtladığı: `db` fixture'ı `otomaix_test` veritabanına bağlanıyor ve
migration zinciri test DB'de uçtan uca koşmuş (social.sectors mevcut).
"""

import pytest

from tests import conftest as infra


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


# --- Yıkıcı test-DB kabul kapısı (F1) -------------------------------------
#
# Sözleşme: DROP/CREATE DATABASE ve migration uygulaması YALNIZ
# 127.0.0.1:5433/otomaix_test üstünde koşabilir. Host/port/veritabanı üçlüsü
# birebir eşleşmezse fail-closed reddedilir — takma ad, eksik port veya
# varsayılana düşme kabul edilmez.

_PASSWORD = "s3cr3t-parola"

REJECTED_URLS = [
    # Uzak host, doğru veritabanı adı — F1'in ta kendisi.
    pytest.param("10.0.1.8:5432", "otomaix_test", id="uzak-host"),
    # Uzak host, doğru port.
    pytest.param("10.0.1.8:5433", "otomaix_test", id="uzak-host-dogru-port"),
    # `localhost` takma adı — birebir 127.0.0.1 isteniyor.
    pytest.param("localhost:5433", "otomaix_test", id="localhost-takma-adi"),
    # IPv6 loopback takma adı.
    pytest.param("[::1]:5433", "otomaix_test", id="ipv6-loopback"),
    # Wildcard adres.
    pytest.param("0.0.0.0:5433", "otomaix_test", id="wildcard-adres"),
    # Doğru host, yanlış port.
    pytest.param("127.0.0.1:5432", "otomaix_test", id="yanlis-port"),
    # Port hiç yok — varsayılana düşmek YASAK.
    pytest.param("127.0.0.1", "otomaix_test", id="port-yok"),
    # Host hiç yok (boş authority).
    pytest.param("", "otomaix_test", id="host-yok"),
    # Canlı veritabanı adı — mevcut koruma korunmalı.
    pytest.param("127.0.0.1:5433", "otomaix", id="canli-veritabani"),
    # Veritabanı adı hiç yok.
    pytest.param("127.0.0.1:5433", "", id="veritabani-yok"),
    # Ön ek eşleşmesiyle kaçış denemesi.
    pytest.param("127.0.0.1:5433", "otomaix_test_x", id="on-ek-kacisi"),
]


def _url(authority: str, database: str) -> str:
    credentials = f"u:{_PASSWORD}@" if authority else ""
    return f"postgresql://{credentials}{authority}/{database}"


ACCEPTED_URL = _url("127.0.0.1:5433", "otomaix_test")


@pytest.mark.parametrize(("authority", "database"), REJECTED_URLS)
def test_destructive_gate_rejects_non_local_endpoints(authority, database):
    with pytest.raises(RuntimeError) as excinfo:
        infra._require_test_database(_url(authority, database))
    assert _PASSWORD not in str(excinfo.value), "hata mesajı parolayı basıyor"


def test_destructive_gate_accepts_the_exact_local_triple():
    assert infra._require_test_database(ACCEPTED_URL) == ACCEPTED_URL


def test_destructive_gate_error_names_expected_and_seen():
    with pytest.raises(RuntimeError) as excinfo:
        infra._require_test_database(_url("10.0.1.8:5432", "otomaix_test"))
    message = str(excinfo.value)
    assert "127.0.0.1" in message and "5433" in message, "beklenen uç nokta yazılmamış"
    assert "10.0.1.8" in message, "görülen host yazılmamış"


def test_admin_gate_rejects_remote_maintenance_endpoint():
    with pytest.raises(RuntimeError):
        infra._require_admin_database(_url("10.0.1.8:5432", "postgres"))


def test_admin_gate_accepts_local_maintenance_endpoint():
    url = _url("127.0.0.1:5433", "postgres")
    assert infra._require_admin_database(url) == url


def test_run_psql_refuses_remote_endpoint_before_spawning_psql(monkeypatch):
    """Doğrulama yıkıcı işlemden ÖNCE koşar: subprocess hiç çağrılmaz."""

    def _explode(*args, **kwargs):  # pragma: no cover - çağrılmamalı
        raise AssertionError("psql reddedilmesi gereken uç nokta için çalıştırıldı")

    monkeypatch.setattr(infra.subprocess, "run", _explode)

    with pytest.raises(RuntimeError):
        infra._run_psql(_url("10.0.1.8:5432", "otomaix_test"), sql="SELECT 1")
