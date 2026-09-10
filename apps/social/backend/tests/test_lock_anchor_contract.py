"""SEKTÖR ÇAPASI SÖZLEŞMESİ — paket satırına dokunan her yol önce çapayı alır.

**Bu test bir VARYANTI değil bir SINIFI tutar.** Üç bağımsız hakem turunda üç
ayrı kilitlenme döngüsü çıktı. İlk ikisi tek tek SIRA kuralıyla kapatıldı ve
üçüncü tur sınıfın kapanmadığını gösterdi: sıra kuralı satır SINIFLARI arasında
düzen kurar (koşu → sektör → paket) ama sınıf İÇİNDE kurmaz. Jeton yakma tek bir
toplu güncellemeyle birden çok koşu satırını sırasız kilitler; jetonu henüz boş
olan bir koşu ise o güncellemeye hiç girmez. İkisi de sıralamayla kapanmaz.

Çözüm tek noktadır: paket satırlarına dokunan her yol, HERHANGİ bir satır
kilidinden ÖNCE sektöre ait işlem-ömürlü bir danışma kilidi alır. Aynı sektörde
iki mutasyon artık iç içe geçemez; sıralanacak bir şey kalmayınca sıralama
hatası da kalmaz.

**Tarama deseni KAVRAMDAN türetilir, bulunan örneklerden değil:** dört modülün
TÜM `async def`'leri taranır ve paket satırına dokunan HER biri sözleşmeye tabi
tutulur. Yarın eklenecek bir fonksiyon da aynı taramaya girer. Muafiyetler
sessiz değildir — adı ve GEREKÇESİ aşağıdaki tabloda görünür.
"""

from __future__ import annotations

import ast
import inspect
import re
from pathlib import Path

import pytest

from app.services import sector_package_lifecycle as lifecycle
from app.services.sector_pipeline import approval, runs, writeback

MODULLER = (lifecycle, writeback, approval, runs)

# Paket satırını KİLİTLEYEN ya da DEĞİŞTİREN işaretler.
_PAKET_DOKUNUSU = (
    r"FROM\s+social\.sector_packages.{0,240}?FOR\s+UPDATE",
    r"UPDATE\s+social\.sector_packages",
    r"INSERT\s+INTO\s+social\.sector_packages",
    r"DELETE\s+FROM\s+social\.sector_packages",
    r"\b_lock_and_load\b",
    r"\b_active_row\b",
    r"\b_set_status\b",
    r"\b_apply_status_transition\b",
    r"\b_update_draft_row\b",
    # Paket satırını DOLAYLI kilitleyen yardımcılar. Mutasyon ölçümü bunların
    # eksikliğini SAHTE-YEŞİL olarak gösterdi: çağıranın çapası kaldırıldığında
    # tarama hiçbir dokunuş görmüyor ve sessizce geçiyordu.
    r"\b_paket_kapisi\b",
    r"\bmint_evidence_token\b",
    r"\bactivate_package\b",
    r"\brollback_package\b",
    r"\bdeactivate_package\b",
    r"\binsert_draft\b",
)

_CAPA = (r"\banchor_sector\b", r"\banchor_for_package\b", r"\banchor_run\b")

MUAFLAR: dict[str, str] = {
    # ── ÖZEL yardımcılar: çağıranları çapalar, kendileri giriş noktası DEĞİL ──
    "_lock_and_load": "özel yardımcı; üç public geçişin İÇİNDEN çağrılır",
    "_active_row": "özel yardımcı; sektör kilidi ALINDIKTAN sonra çağrılır",
    "_set_status": "özel yardımcı; yalnız `_apply_status_transition` içinden",
    "_apply_status_transition": "özel yardımcı; kapı kanıtı doğrulandıktan SONRA",
    "_update_draft_row": "özel ilkel; tek çağıranı çapalanmış güncelleme yoludur",
    "_paket_kapisi": "özel kapı; iki onay yolu da çağrıdan ÖNCE çapalar",
    # ── Public ama mevcut satır KİLİTLEMEYEN yazıcı ──────────────────────
    "insert_draft": (
        "YENİ satır yazar, mevcut satır kilitlemez; sürüm yarışını "
        "`UNIQUE (sector_id, version)` fail-closed kapatır. Üretimdeki tek "
        "çağıranı (`write_draft_from_run`) çapayı ZATEN alır."
    ),
}


def _fonksiyonlar(modul):
    """Her fonksiyonun KOD metni — docstring ve YORUMLAR hariç.

    Ham metin taraması bu iddiayı ÖLÇEMEZ: bir kilit çağrısını ANLATAN yorum
    satırı da eşleşir ve fonksiyon kilit alıyormuş gibi görünür (ölçüldü —
    ilk yazım tam bu yüzden yanlış ihlal üretti). Metin AST'ten yeniden
    üretilir: yorumlar düşer, dize sabitleri (SQL) KALIR.
    """
    kaynak = Path(modul.__file__).read_text(encoding="utf-8")
    agac = ast.parse(kaynak)
    for dugum in ast.walk(agac):
        if not isinstance(dugum, (ast.AsyncFunctionDef, ast.FunctionDef)):
            continue
        govde = list(dugum.body)
        if (
            govde
            and isinstance(govde[0], ast.Expr)
            and isinstance(govde[0].value, ast.Constant)
            and isinstance(govde[0].value.value, str)
        ):
            govde = govde[1:]
        yield dugum.name, "\n".join(ast.unparse(ifade) for ifade in govde)


def _kendi_adini_dusur(desenler, ad: str):
    """Fonksiyonun KENDİ adını işaret saymaz.

    Ölçüldü: `_require_transaction(db, 'mint_evidence_token')` gibi bir kendine
    atıf, fonksiyonu kendi işaretiyle eşleştiriyor ve çapadan ÖNCE bir dokunuş
    varmış gibi gösteriyordu. Bir fonksiyonun adını kendi gövdesinde anması bir
    kilit alması DEĞİLDİR.
    """
    return tuple(d for d in desenler if d != rf"\b{ad}\b")


def _ilk_konum(govde: str, desenler) -> int | None:
    konumlar = [
        m.start()
        for desen in desenler
        for m in re.finditer(desen, govde, re.DOTALL | re.IGNORECASE)
    ]
    return min(konumlar) if konumlar else None


@pytest.mark.parametrize("modul", MODULLER, ids=lambda m: m.__name__.rsplit(".", 1)[-1])
def test_every_package_touching_path_anchors_first(modul):
    """Paket satırına dokunan her fonksiyon, dokunuştan ÖNCE çapayı alır."""
    ihlaller = []
    kapsanan = 0
    for ad, govde in _fonksiyonlar(modul):
        dokunus = _ilk_konum(govde, _kendi_adini_dusur(_PAKET_DOKUNUSU, ad))
        if dokunus is None:
            continue
        kapsanan += 1
        if ad in MUAFLAR:
            continue
        capa = _ilk_konum(govde, _CAPA)
        if capa is None or capa > dokunus:
            ihlaller.append(ad)

    assert kapsanan, f"{modul.__name__}: paket dokunuşu bulunamadı — tarama boş küme ölçüyor"
    assert ihlaller == [], (
        f"{modul.__name__}: çapasız paket dokunuşu — kilitlenme sınıfı yeniden açılır: {ihlaller}"
    )


def test_the_exemption_table_has_no_stale_entries():
    """Muaf listesi BAYATLAMAZ: her muafın hâlâ bir paket dokunuşu olmalı.

    Bayat muaf, sessiz muaftır: fonksiyon değişip dokunuşu kalkınca satır
    listede kalır ve bir gün BAŞKA bir fonksiyona yanlışlıkla kalkan olur.
    """
    dokunanlar = {
        ad
        for modul in MODULLER
        for ad, govde in _fonksiyonlar(modul)
        if _ilk_konum(govde, _kendi_adini_dusur(_PAKET_DOKUNUSU, ad)) is not None
    }
    bayat = sorted(set(MUAFLAR) - dokunanlar)
    assert bayat == [], f"muaf listesinde bayat satır: {bayat}"


def test_the_sweep_would_catch_an_unanchored_path():
    """POZİTİF KONTROL: boş-küme kolu — desen gerçekten yakalıyor mu?

    Tarama hiçbir ihlal bulmadığında iki açıklama vardır: ihlal YOK, ya da desen
    HİÇBİR ŞEYİ eşleştiremiyor. İkisi ayrılmadan yeşil bir sonuç kanıt değildir.
    """
    capasiz = (
        '    row = await db.fetchrow(\n'
        '        "SELECT id FROM social.sector_packages WHERE id = $1 FOR UPDATE", pid\n'
        "    )\n"
    )
    assert _ilk_konum(capasiz, _PAKET_DOKUNUSU) is not None
    assert _ilk_konum(capasiz, _CAPA) is None

    capali = "    await anchor_sector(db, sector_id)\n" + capasiz
    capa_konumu = _ilk_konum(capali, _CAPA)
    dokunus_konumu = _ilk_konum(capali, _PAKET_DOKUNUSU)
    assert capa_konumu is not None and dokunus_konumu is not None
    assert capa_konumu < dokunus_konumu


def test_the_anchor_is_transaction_scoped_and_single_sourced():
    """Çapa TEK yerde tanımlıdır, işlem-ömürlüdür ve KENDİ ad alanındadır.

    İkinci bir tanım iki kural iki davranış demektir; elle bırakılabilen bir
    kilit ise unutulabilir. `pg_advisory_xact_lock` commit ya da rollback ile
    KENDİLİĞİNDEN bırakılır ve bırakma yolu YOKTUR.

    **Depoda İKİ ayrı danışma kilidi vardır ve bu doğrudur:** olay kapsamlı
    kilit (Task 8) ve sektör çapası (bu tur). Ölçülen şey "tek danışma kilidi"
    değil, HER BİRİNİN tek kaynaklı olması ve ad alanlarının ÇAKIŞMAMASIDIR —
    aynı anahtarı üretselerdi iki farklı kavram tek kilide düşer ve olay
    yürütmesi ilgisiz bir sektörü bloke ederdi.
    """
    govde = inspect.getsource(lifecycle.anchor_sector)
    assert "pg_advisory_xact_lock" in govde
    assert "pg_advisory_unlock" not in govde

    sektor_tanimi = [
        f"{modul.__name__}.{ad}"
        for modul in MODULLER
        for ad, kod in _fonksiyonlar(modul)
        if "pg_advisory_xact_lock" in kod and "ANCHOR_ONEKI" in kod
    ]
    assert len(sektor_tanimi) == 1, f"sektör çapası {sektor_tanimi} yerlerinde yazılmış"

    assert lifecycle.ANCHOR_ONEKI != runs._OLAY_KILIT_ONEKI
    assert not lifecycle.ANCHOR_ONEKI.startswith(runs._OLAY_KILIT_ONEKI)
    assert not runs._OLAY_KILIT_ONEKI.startswith(lifecycle.ANCHOR_ONEKI)
