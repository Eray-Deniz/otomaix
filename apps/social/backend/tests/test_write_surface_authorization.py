"""K-103 (a) — paket tablosuna YAZMA yüzeyi yapısal olarak DAR tutulur.

İki tarama birbirinin yerine geçmez ve ikisi de gerekir:

1. **Import taraması** — hiçbir HTTP router'ı yaşam döngüsü yazıcılarını import
   etmez. Tek başına yeterli olsaydı, ham SQL yazan bir router görünmez kalırdı.
2. **Ham SQL taraması** — üretim kodunda `social.sector_packages` tablosuna
   doğrudan yazan (INSERT/UPDATE/DELETE) tek yer yaşam döngüsü modülüdür.

**Kapsamın DÜRÜST sınırı (İlke 3).** Tarama ÜRETİM kodunu (`app/`) kapsar;
`tests/` ve `shared/db/migrations/` kapsam DIŞIDIR ve bu bir eksiklik değil,
tanımın kendisidir: K-103 çalışma zamanındaki yazma yüzeyini daraltır, test
kurulum satırları ve şema göçü bir çalışma zamanı yüzeyi değildir. Bu iki dizin
"muaf tutuldu" diye sessizce atlanmıyor — kapsam dışı oldukları burada YAZILI.

**Bu tarama tek kapı DEĞİLDİR.** Asıl kapı köken jetonudur (arayüz eki R8(c),
`sector_package_lifecycle._consume_provenance`); burası yardımcı bir hijyen
kontrolüdür. Yapısal tarama takma adı (`L = lifecycle`) ve dinamik erişimi
göremez; jeton kapısı çalışma zamanında durur.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

APP_KOKU = Path(__file__).resolve().parents[1] / "app"
ROUTER_KOKU = APP_KOKU / "routers"

YASAM_DONGUSU_MODULU = APP_KOKU / "services" / "sector_package_lifecycle.py"

YAZICI_MODULLER: frozenset[str] = frozenset(
    {
        "app.services.sector_package_lifecycle",
        "app.services.sector_pipeline.writeback",
    }
)
"""Paket satırını DEĞİŞTİREN modüller — router'ların hiçbiri bunları çağıramaz."""

PAKET_TABLOSU_YAZIMI = re.compile(
    r"(INSERT\s+INTO\s+social\.sector_packages"
    r"|UPDATE\s+social\.sector_packages"
    r"|DELETE\s+FROM\s+social\.sector_packages)",
    re.IGNORECASE,
)


def _uretim_modulleri() -> list[Path]:
    """Taranacak dosya kümesi KAVRAMDAN türetilir: `app/` altındaki tüm Python.

    Bulunmuş örneklerden liste çıkarmak tarama değil, zaten bilinenin tekrar
    kontrolü olurdu — yeni bir modül eklendiği gün sessizce kapsam dışı kalırdı.
    """
    return sorted(
        yol
        for yol in APP_KOKU.rglob("*.py")
        if "__pycache__" not in yol.parts
    )


def _import_edilen_moduller(kaynak: str) -> set[str]:
    """AST'ten import edilen tam modül adları — yorum ve metin SAYILMAZ."""
    adlar: set[str] = set()
    agac = ast.parse(kaynak)
    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.Import):
            adlar.update(ad.name for ad in dugum.names)
        elif isinstance(dugum, ast.ImportFrom) and dugum.module and not dugum.level:
            adlar.add(dugum.module)
            adlar.update(f"{dugum.module}.{ad.name}" for ad in dugum.names)
    return adlar


def test_no_router_imports_lifecycle_writers():
    """Hiçbir HTTP router'ı yaşam döngüsü yazıcılarını import ETMEZ."""
    assert ROUTER_KOKU.is_dir(), f"router kökü yok: {ROUTER_KOKU}"
    router_dosyalari = sorted(
        yol for yol in ROUTER_KOKU.rglob("*.py") if "__pycache__" not in yol.parts
    )
    assert router_dosyalari, "router dosyası bulunamadı — tarama boş küme ölçüyor"

    ihlaller = []
    for yol in router_dosyalari:
        adlar = _import_edilen_moduller(yol.read_text(encoding="utf-8"))
        for ad in sorted(adlar):
            if any(ad == yazici or ad.startswith(yazici + ".") for yazici in YAZICI_MODULLER):
                ihlaller.append(f"{yol.name}: {ad}")

    assert ihlaller == [], f"router yaşam döngüsü yazıcısını import ediyor: {ihlaller}"


def test_no_direct_sql_writer_outside_lifecycle():
    """`social.sector_packages`'a doğrudan yazan TEK üretim modülü yaşam döngüsüdür."""
    moduller = _uretim_modulleri()
    assert moduller, "üretim modülü bulunamadı — tarama boş küme ölçüyor"

    yazanlar = sorted(
        yol.relative_to(APP_KOKU).as_posix()
        for yol in moduller
        if PAKET_TABLOSU_YAZIMI.search(yol.read_text(encoding="utf-8"))
    )
    beklenen = [YASAM_DONGUSU_MODULU.relative_to(APP_KOKU).as_posix()]
    assert yazanlar == beklenen, (
        "paket tablosuna yaşam döngüsü dışından yazan üretim modülü var: "
        f"{sorted(set(yazanlar) - set(beklenen))}"
    )


def test_the_scan_would_catch_a_new_writer(tmp_path):
    """POZİTİF KONTROL: desen gerçekten yakalıyor mu — boş-küme kontrol kolu.

    Tarama hiçbir şey bulmadığında iki açıklama vardır: yazıcı YOK, ya da desen
    HİÇBİR ŞEYİ eşleştiremiyor. İkisini ayırmadan yeşil bir sonuç kanıt değildir.
    """
    ornek = tmp_path / "sahte_router.py"
    ornek.write_text(
        'SQL = "UPDATE social.sector_packages SET status = $2 WHERE id = $1"\n',
        encoding="utf-8",
    )
    assert PAKET_TABLOSU_YAZIMI.search(ornek.read_text(encoding="utf-8"))

    temiz = tmp_path / "temiz_router.py"
    temiz.write_text(
        'SQL = "SELECT id FROM social.sector_packages WHERE id = $1"\n',
        encoding="utf-8",
    )
    assert PAKET_TABLOSU_YAZIMI.search(temiz.read_text(encoding="utf-8")) is None
