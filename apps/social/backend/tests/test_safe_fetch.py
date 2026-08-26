"""Security review 2026-08-26 / S1 — kullanıcı URL'ini çeken kapının regresyonu.

Bu testler AĞA ÇIKMAZ: isim çözümlemesi ve HTTP istemcisi yerine deterministik
sahteler konur. Gerekçe, kapının doğruluğunun internetin o anki hâline bağlı
olmamasıdır — ağa çıkan bir test, DNS değiştiğinde sebepsiz kırmızıya döner ve
zamanla "zaten ara sıra düşer" diye görmezden gelinir.

Kapının gerçek dünyada çalıştığı AYRI ve BİR KEZ ölçüldü (2026-08-26, canlı
koşum): `example.com` ve `otomaix.com` TLS ile çekildi, `http://github.com`
yönlendirme zinciriyle izlendi, bulut kimlik-bilgisi adresi · geri döngü ·
`localhost` · özel ağ · IPv6 geri döngü · IPv4-mapped IPv6 · izinsiz port ·
`file:` şeması · kimlik bilgili URL reddedildi. O koşum bu dosyanın yerine
GEÇMEZ; bu dosya onun tekrar koşabilir hâlidir.
"""

from __future__ import annotations

import socket

import httpx
import pytest

from app.services import safe_fetch
from app.services.safe_fetch import UnsafeUrlError, fetch_public_url

PUBLIC_IP = "93.184.216.34"
PRIVATE_IP = "10.0.1.8"
LOOPBACK_IP = "127.0.0.1"
METADATA_IP = "169.254.169.254"


def _addrinfo(*addresses: str):
    """`getaddrinfo` biçiminde sahte sonuç — IPv4/IPv6 ayrımı adresten türer."""
    out = []
    for address in addresses:
        family = socket.AF_INET6 if ":" in address else socket.AF_INET
        sockaddr = (address, 443, 0, 0) if family == socket.AF_INET6 else (address, 443)
        out.append((family, socket.SOCK_STREAM, 6, "", sockaddr))
    return out


@pytest.fixture
def dns(monkeypatch):
    """Ad → adres eşlemesini testin belirlediği sahte çözümleyici."""
    table: dict[str, list[str]] = {}

    def fake_getaddrinfo(host, port, *args, **kwargs):
        if host not in table:
            raise socket.gaierror(socket.EAI_NONAME, "sahte çözümleyicide yok")
        return _addrinfo(*table[host])

    monkeypatch.setattr(safe_fetch.socket, "getaddrinfo", fake_getaddrinfo)
    return table


class _ScriptedResponse:
    """Akıtarak okunan sahte yanıt.

    `produced` ÜRETİLEN parça sayısını tutar — gövdenin gerçekten erken kesilip
    kesilmediğini ölçmenin tek yolu budur. Hazır bir gövdeyi dilimleyen bir sahte,
    "indirme sınırlandı" iddiasını kanıtlayamaz (kapanış turunun haklı olduğu nokta).
    """

    def __init__(self, status, body=b"ok", location=None, chunk_size=64):
        self.status_code = status
        self.headers = httpx.Headers({"location": location} if location else {})
        self.encoding = "utf-8"
        self._body = body
        self._chunk_size = chunk_size
        self.produced = 0
        self.closed = False

    @property
    def is_redirect(self):
        return self.status_code in (301, 302, 303, 307, 308) and "location" in self.headers

    async def aiter_bytes(self):
        for start in range(0, len(self._body), self._chunk_size):
            chunk = self._body[start : start + self._chunk_size]
            self.produced += len(chunk)
            yield chunk


@pytest.fixture
def http(monkeypatch):
    """Scriptli HTTP istemcisi. `requests` listesi gerçekten nereye gidildiğini tutar."""
    script: list[_ScriptedResponse] = []
    requests: list[dict] = []
    served: list[_ScriptedResponse] = []

    class _StreamCtx:
        def __init__(self, response):
            self._response = response

        async def __aenter__(self):
            return self._response

        async def __aexit__(self, *exc):
            self._response.closed = True
            return False

    class FakeClient:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        def stream(self, method, url, headers=None, extensions=None):
            requests.append(
                {"url": url, "headers": headers or {}, "extensions": extensions or {}}
            )
            if not script:
                raise AssertionError("beklenenden fazla istek yapıldı")
            response = script.pop(0)
            served.append(response)
            return _StreamCtx(response)

    monkeypatch.setattr(safe_fetch.httpx, "AsyncClient", FakeClient)
    return {"script": script, "requests": requests, "served": served}


def _response(status: int, *, body: bytes = b"ok", location: str | None = None, chunk_size: int = 64):
    return _ScriptedResponse(status, body=body, location=location, chunk_size=chunk_size)


# ── URL doğrulama: ağa hiç çıkmadan reddedilenler ───────────────────────────


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "gopher://evil.test/",
        "redis://evil.test:6379/",
    ],
)
async def test_disallowed_scheme_is_rejected(url, dns, http):
    with pytest.raises(UnsafeUrlError, match="şema"):
        await fetch_public_url(url)
    assert http["requests"] == [], "reddedilen URL için yine de istek yapıldı"


async def test_disallowed_port_is_rejected(dns, http):
    dns["example.test"] = [PUBLIC_IP]
    with pytest.raises(UnsafeUrlError, match="port"):
        await fetch_public_url("http://example.test:5432/")
    assert http["requests"] == []


async def test_url_with_credentials_is_rejected(dns, http):
    """`http://beklenen@gercek/` — gösterilen host ile bağlanılan host ayrışır."""
    dns["evil.test"] = [PUBLIC_IP]
    with pytest.raises(UnsafeUrlError, match="kimlik"):
        await fetch_public_url("http://example.test@evil.test/")
    assert http["requests"] == []


async def test_empty_url_is_rejected(dns, http):
    with pytest.raises(UnsafeUrlError):
        await fetch_public_url("   ")


# ── Adres kontrolü ──────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "address",
    [
        LOOPBACK_IP,
        PRIVATE_IP,
        METADATA_IP,
        "::1",
        "::ffff:127.0.0.1",
        "0.0.0.0",
        "192.168.1.1",
        "172.16.0.5",
        # Kapanış turunda ÖLÇÜLEN kaçak: taşıyıcı-NAT alanı (CGNAT, Tailscale)
        # hiçbir "yasak" bayrağına takılmıyor ve sayarak kurulmuş kapıdan
        # geçiyordu. Pozitif `is_global` koşulu bu sınıfı kapatır.
        "100.64.0.1",
        "100.100.100.100",
        # `is_global` TEK BAŞINA da yetmiyor: multicast için True döner.
        "224.0.0.1",
        "ff02::1",
        # 6to4 sarmalayıcısı içinde özel adres.
        "2002:0a00:0108::",
        "fd00::1",
        "fe80::1",
    ],
)
async def test_private_address_is_rejected(address, dns, http):
    dns["internal.test"] = [address]
    with pytest.raises(UnsafeUrlError, match="özel/dahili"):
        await fetch_public_url("http://internal.test/")
    assert http["requests"] == [], "özel adrese istek yapıldı"


async def test_any_private_address_rejects_the_whole_name(dns, http):
    """İki kayıttan biri iç ağa bakıyorsa isim TÜMDEN reddedilir.

    "İlkine bak" demek, ikinci kaydı iç ağa koyan bir ismi kabul etmek olurdu;
    hangi kaydın kullanılacağı bizim kontrolümüzde değil.
    """
    dns["mixed.test"] = [PUBLIC_IP, PRIVATE_IP]
    with pytest.raises(UnsafeUrlError, match="özel/dahili"):
        await fetch_public_url("http://mixed.test/")
    assert http["requests"] == []


async def test_unresolvable_name_is_rejected(dns, http):
    with pytest.raises(UnsafeUrlError, match="çözülemedi"):
        await fetch_public_url("http://yok.test/")


# ── Yönlendirme ─────────────────────────────────────────────────────────────


async def test_redirect_into_private_network_is_rejected(dns, http):
    """Kapının asıl sınavı: ilk adres açık, yönlendirme iç ağa.

    Kör takip (`follow_redirects=True`) tam olarak bunu kaçırıyordu — ilk
    adresin herkese açık olması sonrakiler için hiçbir şey söylemez.
    """
    dns["public.test"] = [PUBLIC_IP]
    dns["internal.test"] = [METADATA_IP]
    http["script"].append(_response(302, location="http://internal.test/secret"))

    with pytest.raises(UnsafeUrlError, match="özel/dahili"):
        await fetch_public_url("http://public.test/")

    assert len(http["requests"]) == 1, "yönlendirme hedefine istek yapıldı"


async def test_redirect_to_public_target_is_followed(dns, http):
    """Pozitif kontrol: meşru yönlendirme hâlâ izleniyor (her şeyi reddeden fix geçmesin)."""
    dns["public.test"] = [PUBLIC_IP]
    dns["other.test"] = [PUBLIC_IP]
    http["script"].append(_response(301, location="https://other.test/final"))
    http["script"].append(_response(200, body="hedef gövde".encode()))

    body = await fetch_public_url("http://public.test/")

    assert body == "hedef gövde"
    assert len(http["requests"]) == 2


async def test_redirect_loop_stops(dns, http):
    dns["loop.test"] = [PUBLIC_IP]
    for _ in range(safe_fetch.MAX_REDIRECTS + 1):
        http["script"].append(_response(302, location="http://loop.test/again"))

    with pytest.raises(UnsafeUrlError, match="yönlendirme"):
        await fetch_public_url("http://loop.test/")

    assert len(http["requests"]) == safe_fetch.MAX_REDIRECTS + 1


async def test_relative_redirect_resolves_against_the_real_host(dns, http):
    """Göreli hedef, SABİTLENMİŞ IP'li URL'e değil gerçek URL'e göre çözülür.

    Sabitlenmiş URL'e göre çözülseydi bir sonraki turun host'u IP olurdu ve
    `Host` başlığı ile SNI sessizce yanlış isme kayardı.
    """
    dns["public.test"] = [PUBLIC_IP]
    http["script"].append(_response(302, location="/ikinci"))
    http["script"].append(_response(200, body=b"tamam"))

    await fetch_public_url("https://public.test/birinci")

    assert http["requests"][1]["headers"]["Host"] == "public.test"
    assert http["requests"][1]["url"].endswith("/ikinci")


# ── Bağlantı sabitleme ve gövde sınırı ──────────────────────────────────────


async def test_connection_is_pinned_to_the_validated_address(dns, http):
    """Bağlanılan adres doğrulanan IP; `Host` ve SNI gerçek isim.

    Yeniden çözülseydi, saldırgan doğrulamada açık bağlanmada özel bir adres
    verebilirdi (DNS rebinding). SNI gerçek isim olmasaydı sertifika doğrulaması
    IP'ye karşı yapılır ve her meşru HTTPS sitesi düşerdi.
    """
    dns["public.test"] = [PUBLIC_IP]
    http["script"].append(_response(200, body=b"tamam"))

    await fetch_public_url("https://public.test/yol?q=1")

    request = http["requests"][0]
    assert PUBLIC_IP in request["url"]
    assert "public.test" not in request["url"]
    assert request["headers"]["Host"] == "public.test"
    assert request["extensions"]["sni_hostname"] == "public.test"


async def test_plain_http_does_not_set_sni(dns, http):
    dns["public.test"] = [PUBLIC_IP]
    http["script"].append(_response(200, body=b"tamam"))

    await fetch_public_url("http://public.test/")

    assert http["requests"][0]["extensions"] == {}


async def test_body_is_capped(dns, http):
    dns["public.test"] = [PUBLIC_IP]
    http["script"].append(_response(200, body=b"a" * 5000))

    body = await fetch_public_url("http://public.test/", max_bytes=100)

    assert len(body) == 100


async def test_download_stops_at_the_cap_instead_of_buffering(dns, http):
    """Sınır İNDİRMEYİ kesmeli, sonucu değil.

    İlk sürüm gövdenin tamamını belleğe alıp sonra dilimliyordu; sınır o hâliyle
    bir bellek koruması değildi ve saldırganın sunucusu işçiyi doldurabilirdi.
    Burada ÜRETİLEN bayt sayısı ölçülür — hazır gövdeyi dilimleyen bir sahte bu
    farkı gösteremezdi (kapanış turu, 2026-08-26).
    """
    dns["public.test"] = [PUBLIC_IP]
    http["script"].append(_response(200, body=b"a" * 100_000, chunk_size=64))

    await fetch_public_url("http://public.test/", max_bytes=128)

    response = http["served"][0]
    assert response.produced < 1000, (
        f"gövdenin tamamı okundu: {response.produced} bayt üretildi"
    )
    assert response.closed, "akış kapatılmadı"


async def test_redirect_body_is_never_read(dns, http):
    """Yönlendirme yanıtının gövdesi HİÇ okunmaz — o da bir tüketim yüzeyidir."""
    dns["public.test"] = [PUBLIC_IP]
    dns["other.test"] = [PUBLIC_IP]
    http["script"].append(
        _response(302, body=b"x" * 100_000, location="https://other.test/final")
    )
    http["script"].append(_response(200, body=b"tamam"))

    await fetch_public_url("http://public.test/")

    assert http["served"][0].produced == 0, "yönlendirme gövdesi okundu"


async def test_schemeless_input_still_works(dns, http):
    """Bugünkü davranış korunur: şemasız adres `https://` ile tamamlanır."""
    dns["public.test"] = [PUBLIC_IP]
    http["script"].append(_response(200, body=b"tamam"))

    await fetch_public_url("public.test/yol")

    assert http["requests"][0]["extensions"]["sni_hostname"] == "public.test"


async def test_public_address_is_still_accepted(dns, http):
    """Pozitif kontrol: kapıyı sertleştirmek meşru adresleri kapatmadı.

    `is_global` koşulu eklenirken asıl risk, her şeyi reddeden bir kapı kurup
    testlerin yine yeşil kalmasıydı.
    """
    dns["public.test"] = [PUBLIC_IP]
    http["script"].append(_response(200, body=b"tamam"))

    assert await fetch_public_url("http://public.test/") == "tamam"


async def test_public_ipv6_is_accepted(dns, http):
    dns["v6.test"] = ["2001:4860:4860::8888"]
    http["script"].append(_response(200, body=b"tamam"))

    await fetch_public_url("http://v6.test/")

    assert "[2001:4860:4860::8888]" in http["requests"][0]["url"]
