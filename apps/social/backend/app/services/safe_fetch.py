"""Kullanıcının verdiği URL'i sunucudan çekmenin TEK güvenli kapısı (SSRF).

Security review 2026-08-26 / S1. İki yüzey (marka sitesi analizi ve rakip sitesi
analizi) kullanıcıdan aldığı adresi doğrudan `httpx`'e veriyordu: yalnız şema ön
ekine bakılıyor, host/port kısıtı ve çözülen adres kontrolü yapılmıyor,
yönlendirmeler kör takip ediliyordu. Kimliği doğrulanmış herhangi bir kiracı
sunucuyu iç ağa, geri döngüye ya da bulut kimlik-bilgisi adresine gönderebiliyor,
dönen içerik de modele özetletilip kendisine geri veriliyordu — kör SSRF değil,
içerik sızdıran SSRF.

Kapının dört ayağı var:

1. **Şema ve port allowlist'i.** Yalnız `http`/`https`, yalnız 80/443. `file:`,
   `gopher:`, `redis:` gibi şemalar ve yüksek portlar hiç denenmez.
2. **Çözülen HER adres kontrol edilir.** Bir isim birden çok adrese çözülebilir;
   biri bile özel/geri-döngü/link-local/ayrılmış ise TÜMÜ reddedilir. "İlkine bak"
   demek, ikinci kaydı iç ağa koyan bir ismi kabul etmek olurdu. IPv4'ü sarmalayan
   IPv6 biçimleri (`::ffff:10.0.0.1`, 6to4, Teredo) açılıp yeniden kontrol edilir —
   aksi hâlde sarmalama kontrolü atlatırdı.
3. **Yönlendirme ELLE izlenir, her adımda yeniden doğrulanarak.** Kör takip, dış
   bir sitenin 302 ile iç ağa yönlendirmesine izin verirdi; ilk adresin herkese
   açık olması sonrakiler için hiçbir şey söylemez.
4. **Bağlantı doğrulanan IP'ye sabitlenir.** İsim doğrulama ile bağlanma arasında
   yeniden çözülseydi, saldırgan kendi DNS'iyle doğrulamada açık, bağlanmada özel
   bir adres verebilirdi (DNS rebinding). TLS'te doğru sertifika denetimi için SNI
   ve doğrulama adı GERÇEK host'tur; sabitlenen yalnız bağlanılan adrestir.

Yanıt gövdesi ayrıca bayt sınırıyla akıtılarak okunur: sınırsız gövde, hem bellek
hem de modele giden bağlam açısından ayrı bir maliyet yüzeyidir.

Kapsam sınırı (dürüst): bu kapı ÇIKIŞ ADRESİNİ kısıtlar, ağ katmanını değil.
Gerçek izolasyon çıkış-kısıtlı bir işçi/proxy'dir (iç ağa route yok); bu modül
onun yerine geçmez, o gelene kadarki kapıdır.
"""

from __future__ import annotations

import ipaddress
import re
import socket
from urllib.parse import urljoin, urlparse, urlunparse

import httpx

ALLOWED_SCHEMES = frozenset({"http", "https"})
ALLOWED_PORTS = frozenset({80, 443})
MAX_REDIRECTS = 3
MAX_RESPONSE_BYTES = 512 * 1024
USER_AGENT = "Mozilla/5.0 (compatible; OtomaixBot/1.0)"

# RFC 3986 şema biçimi. Şemasız girdiyi (`otomaix.com`, `otomaix.com:8080/x`)
# şemalı girdiden ayırmak için; `host:port` biçimi şemaya benzemesin diye
# ardından `//` ya da şema-dışı karakter gelmesi ayrıca sınanır.
_SCHEME_PREFIX_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:(?![0-9])")


class UnsafeUrlError(ValueError):
    """URL bu sunucudan çekilemez.

    Mesaj çağırana verilmek için DEĞİL teşhis içindir: uca dönerken jenerik
    "ulaşılamadı" metnine çevrilir, yoksa iç ağın haritası dışarı sızardı
    (hangi adresin var olduğu, hangisinin reddedildiği).
    """


def _is_public_address(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Adres herkese açık internet adresi mi — sarmalanmış biçimler dâhil."""
    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    ):
        return False

    # IPv6 içinde IPv4 taşıyan biçimler: sarmalanan adres AYRICA kontrol edilir.
    mapped = getattr(ip, "ipv4_mapped", None)
    if mapped is not None and not _is_public_address(mapped):
        return False
    sixtofour = getattr(ip, "sixtofour", None)
    if sixtofour is not None and not _is_public_address(sixtofour):
        return False
    teredo = getattr(ip, "teredo", None)
    if teredo is not None and not all(_is_public_address(part) for part in teredo):
        return False
    return True


def _validate_url(url: str) -> tuple[str, str, int]:
    """`(scheme, host, port)` döndürür; kapıdan geçmeyen URL'de istisna atar."""
    parsed = urlparse(url)
    scheme = (parsed.scheme or "").lower()
    if scheme not in ALLOWED_SCHEMES:
        raise UnsafeUrlError(f"izinsiz şema: {scheme!r}")

    host = parsed.hostname
    if not host:
        raise UnsafeUrlError("host yok")

    port = parsed.port or (443 if scheme == "https" else 80)
    if port not in ALLOWED_PORTS:
        raise UnsafeUrlError(f"izinsiz port: {port}")

    # Kimlik bilgisi taşıyan URL (`http://beklenen-host@gercek-host/`) reddedilir:
    # kullanıcıya gösterilen host ile bağlanılan host ayrışır.
    if parsed.username or parsed.password:
        raise UnsafeUrlError("URL kimlik bilgisi taşıyor")

    return scheme, host, port


def _resolve_public_ip(host: str, port: int) -> str:
    """Host'u çöz; adreslerden BİRİ bile açık değilse reddet, ilkini döndür."""
    # Host zaten bir IP ise getaddrinfo onu aynen döndürür — ayrı dal gerekmez.
    try:
        infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise UnsafeUrlError(f"isim çözülemedi: {host}") from exc

    if not infos:
        raise UnsafeUrlError(f"isim hiçbir adrese çözülmedi: {host}")

    addresses = [str(info[4][0]) for info in infos]
    for address in addresses:
        try:
            ip = ipaddress.ip_address(address)
        except ValueError as exc:  # pragma: no cover — getaddrinfo hep IP döner
            raise UnsafeUrlError(f"adres ayrıştırılamadı: {address!r}") from exc
        if not _is_public_address(ip):
            raise UnsafeUrlError(f"özel/dahili adrese çözülüyor: {host}")
    return addresses[0]


def _pinned_url(scheme: str, ip: str, port: int, path_and_rest: tuple[str, str, str]) -> str:
    """Bağlanılacak URL: host yerine doğrulanan IP. IPv6 köşeli ayraçla sarılır."""
    literal = f"[{ip}]" if ":" in ip else ip
    netloc = f"{literal}:{port}"
    path, query, fragment = path_and_rest
    return urlunparse((scheme, netloc, path or "/", "", query, fragment))


async def fetch_public_url(
    url: str,
    *,
    timeout: float = 10.0,
    max_bytes: int = MAX_RESPONSE_BYTES,
) -> str:
    """Herkese açık bir URL'i çek ve gövdesini metin olarak döndür.

    Şemasız gelen adres `https://` ile tamamlanır (bugünkü davranış korunur).
    Kapıdan geçmeyen her durumda `UnsafeUrlError` — sessiz düşüş YOK.
    """
    current = (url or "").strip()
    if not current:
        raise UnsafeUrlError("boş URL")
    # Şema tamamlama YALNIZ şemasız girdide yapılır. Koşulsuz ön ek koymak
    # `file:///etc/passwd`'i `https://file:///etc/passwd`'e çevirirdi: sonuç yine
    # reddedilirdi ama ŞEMA kapısına değil isim çözümlemesine takılarak, yani kapı
    # doğru çalıştığını yanlış yerden kanıtlamış olurdu (ölçüldü 2026-08-26).
    if "://" not in current and not _SCHEME_PREFIX_RE.match(current):
        current = f"https://{current}"

    async with httpx.AsyncClient(timeout=timeout, follow_redirects=False) as client:
        for _ in range(MAX_REDIRECTS + 1):
            scheme, host, port = _validate_url(current)
            ip = _resolve_public_ip(host, port)

            parsed = urlparse(current)
            target = _pinned_url(
                scheme, ip, port, (parsed.path, parsed.query, parsed.fragment)
            )
            headers = {"Host": host, "User-Agent": USER_AGENT}
            # SNI ve sertifika doğrulama adı GERÇEK host'tur; sabitlenen yalnız
            # bağlanılan adres. Aksi hâlde sertifika IP'ye karşı doğrulanır ve
            # her meşru HTTPS sitesi düşerdi.
            extensions = {"sni_hostname": host} if scheme == "https" else {}

            response = await client.get(target, headers=headers, extensions=extensions)

            if response.is_redirect:
                location = response.headers.get("location")
                if not location:
                    raise UnsafeUrlError("yönlendirme hedefi yok")
                # Göreli hedef, SABİTLENMİŞ URL'e değil gerçek URL'e göre çözülür.
                current = urljoin(current, location)
                continue

            body = response.content[:max_bytes]
            encoding = response.encoding or "utf-8"
            return body.decode(encoding, errors="replace")

    raise UnsafeUrlError("çok fazla yönlendirme")
