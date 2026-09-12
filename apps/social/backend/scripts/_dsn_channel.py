"""Bağlantı dizesinin operatör CLI'larına GİRİŞ KANALI — argv DEĞİL.

2026-09-12 güvenlik review'ı (S-3, high — iki hakem de bağımsız buldu): parola
taşıyan DSN zorunlu bir komut satırı argümanıydı. Argv gizli değildir —
`/proc/<pid>/cmdline` bu makinede `hidepid` olmadan bağlı (ölçüldü), yani her
kullanıcı okuyabiliyordu; ayrıca değer kabuk geçmişine ve her `ps` çıktısına
düşüyordu. Bulgu, denetçi alt süreciyle de zincirleniyordu: alt süreç
`/proc/<ppid>/cmdline` okuyarak `.env`'e hiç dokunmadan parolayı alabilirdi.

**Korunan tasarım kararı:** kaynak hâlâ AÇIKÇA seçilir — `DATABASE_URL` sessizce
okunmaz. Değişen tek şey, değerin argv yerine bir DOSYADAN ya da ADI VERİLEN bir
ortam değişkeninden gelmesidir:

    --database-url-file /run/secrets/otomaix.dsn     # 0600 dosya
    --database-url-env  OTOMAIX_PIPELINE_DSN         # adı açıkça verilen değişken

Ortam değişkeni argv'den daha korunaklı bir kanaldır: `/proc/<pid>/environ`
yalnız aynı kullanıcıya açıktır, `cmdline` herkese.
"""

from __future__ import annotations

import argparse
import os
import stat
from pathlib import Path

ARGV_SIR_MESAJI = (
    "--database-url ARTIK KABUL EDİLMİYOR: bağlantı dizesi argv'ye yazılırsa "
    "/proc/<pid>/cmdline, `ps` çıktısı ve kabuk geçmişi üzerinden okunur "
    "(2026-09-12 güvenlik review'ı, S-3). Bunun yerine "
    "--database-url-file <0600 dosya> ya da --database-url-env <DEĞİŞKEN ADI> kullanın."
)


class ArgvSirriReddedildi(argparse.Action):
    """Eski bayrak SESSİZCE kaldırılmaz — kullanan operatöre sebebi söylenir.

    Bayrağı tanımsız bırakmak "bilinmeyen argüman" hatası verirdi ve operatör
    onu bir yazım hatası sanabilirdi; üstelik değerin ARTIK argv'de olduğu
    gerçeği (o koşum için sızıntı gerçekleşti) hiç söylenmezdi.
    """

    def __init__(self, option_strings, dest, **kwargs):
        kwargs.setdefault("nargs", "?")
        kwargs.setdefault("help", argparse.SUPPRESS)
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        parser.error(ARGV_SIR_MESAJI)


def kanal_argumanlarini_ekle(parser: argparse.ArgumentParser) -> None:
    """İki kanal + reddedilen eski bayrak — tek yerde, iki CLI'da aynı."""
    parser.add_argument(
        "--database-url-file",
        help=(
            "Bağlantı dizesini taşıyan dosya (yalnız sahibine okunur olmalı, "
            "ör. 0600). Değer argv'ye YAZILMAZ."
        ),
    )
    parser.add_argument(
        "--database-url-env",
        help=(
            "Bağlantı dizesini taşıyan ortam değişkeninin ADI (değeri değil). "
            "Ortamdan sessiz miras YOK — değişken açıkça adlandırılır."
        ),
    )
    parser.add_argument("--database-url", action=ArgvSirriReddedildi)


def dsn_coz(args, parser: argparse.ArgumentParser) -> str:
    """Seçilen kanaldan DSN'i okur. Fail-closed: belirsizlik hata verir.

    * iki kanal birden verilirse → hata (hangisinin kazandığı sessiz kalmaz)
    * hiçbiri verilmezse → hata (ortamdan sessiz miras YOK)
    * dosya grup/dünya tarafından okunabiliyorsa → hata (sır paylaşımlı dosyada)
    """
    dosya = getattr(args, "database_url_file", None)
    degisken = getattr(args, "database_url_env", None)

    if dosya and degisken:
        parser.error(
            "--database-url-file ve --database-url-env birlikte verildi — "
            "tek kanal seçin (hangisinin kazandığı sessizce varsayılmaz)"
        )
    if not dosya and not degisken:
        parser.error(
            "bağlantı dizesi kanalı verilmedi: --database-url-file <0600 dosya> "
            "ya da --database-url-env <DEĞİŞKEN ADI> zorunludur"
        )

    if dosya:
        yol = Path(dosya)
        if not yol.is_file():
            parser.error(f"--database-url-file okunamıyor: {dosya}")
        kip = yol.stat().st_mode
        if kip & (stat.S_IRWXG | stat.S_IRWXO):
            parser.error(
                f"--database-url-file başkalarına açık ({stat.filemode(kip)}): {dosya} "
                "— sırrı taşıyan dosya yalnız sahibine okunabilir olmalı (chmod 600)"
            )
        deger = yol.read_text(encoding="utf-8").strip()
        if not deger:
            parser.error(f"--database-url-file boş: {dosya}")
        return deger

    if degisken not in os.environ:
        parser.error(f"--database-url-env ile verilen değişken ortamda YOK: {degisken}")
    deger = os.environ[degisken].strip()
    if not deger:
        parser.error(f"--database-url-env ile verilen değişken BOŞ: {degisken}")
    return deger
