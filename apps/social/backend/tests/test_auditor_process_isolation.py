"""Denetçi alt süreçlerinin İŞLETİM SİSTEMİ kutusu — tripwire.

Bu dosya kod davranışını değil ORTAMI ölçer. Sebebi: `auditors.IZOLASYON_KULLANICISI`
altında koşan bir alt sürecin neyi okuyamadığı, argv'ye değil dosya izinlerine ve grup
üyeliklerine bağlıdır. Bir sistem güncellemesi, bir `usermod`, bir izin gevşemesi kutuyu
SESSİZCE açar; kod aynı kalır ve hiçbir birim testi bunu fark etmez.

**Neden tripwire, neden tek seferlik ölçüm değil.** Kutunun kapalılığı 2026-09-17'de elle
ölçüldü. Elle ölçüm bir defa doğrudur; regresyonu yakalamaz. Buradaki testler her koşumda
GERÇEK okuma denemesi yapar — izin bitlerine bakmaz, dosyayı açmayı DENER.

**Totoloji koruması — POZİTİF KONTROL.** Her yasak-erişim iddiasının yanında, aynı probun
root olarak KOŞTUĞU ve BAŞARDIĞI bir eş vardır. Pozitif kontrol olmasaydı bozuk bir prob
(yanlış yol, çalışmayan komut, sessiz istisna) her şeyi "erişilemez" raporlar ve test
yeşil kalırdı — yani hiçbir şey ölçmeyen bir kapı olurdu.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

from app.services.sector_pipeline import auditors, runs

KULLANICI = auditors.IZOLASYON_KULLANICISI

# Kök ev dizini ÖLÇÜLÜR, yazılmaz: testin kendi varsayımı sürüklenmesin.
ROOT_EVI = Path(os.path.expanduser("~root"))

# Backend'in kendi sır dosyası — yol bu dosyanın konumundan TÜRETİLİR.
BACKEND_KOKU = Path(__file__).resolve().parents[1]
BACKEND_ENV = BACKEND_KOKU / ".env"


def _atla_gerekcesi() -> str | None:
    """Ölçüm KURULAMIYORSA sebebini döndürür — sessiz yeşil YOK."""
    if os.geteuid() != 0:
        return "ölçüm root gerektirir (başka kullanıcı adına okuma denemesi)"
    if shutil.which("sudo") is None:
        return "sudo kurulu değil — kullanıcı değiştirilemiyor"
    if subprocess.run(["id", "-u", KULLANICI], capture_output=True).returncode != 0:
        return f"{KULLANICI} kullanıcısı yok — kutu kurulmamış"
    return None


def _okuma_denemesi(yol: Path, *, kullanici: str | None) -> bool:
    """`yol` GERÇEKTEN okunabildi mi? İzin bitine bakmaz, açmayı DENER.

    `kullanici` None ise çağıranın kendisi (root) dener — pozitif kontrol budur.
    Dizin için okuma = listeleyebilmek; dosya için = içeriği açabilmek.
    """
    komut = ["test", "-d", str(yol)]
    dizin_mi = subprocess.run(komut, capture_output=True).returncode == 0
    ic_komut = ["ls", str(yol)] if dizin_mi else ["cat", str(yol)]
    tam = ["sudo", "-n", "-u", kullanici, *ic_komut] if kullanici else ic_komut
    sonuc = subprocess.run(tam, capture_output=True, timeout=60)
    return sonuc.returncode == 0


def _kanonik_agac_hedefleri() -> list[Path]:
    """Kanonik denetçi ağacı — hedefler KAVRAMDAN türetilir, elle yazılmaz (T6).

    **Kavram:** *"boru hattının araştırma deposuna yazdığı ve denetçinin YALNIZ kendi
    sahnesi üzerinden görmesi gereken her şey."* Üç katman birlikte süpürülür:

    1. **Deponun KÖKÜ** (`runs.ARASTIRMA_DEPOSU_KOKU`) — kutunun dayandığı mekanizma
       `~root`'un `700` izni olduğu için, depo bir gün `/root` dışına taşınırsa kutu
       SESSİZCE açılır. Kök ölçülmezse bu kayma görünmez.
    2. **Kökün DOĞRUDAN çocukları** — elle üç ad yazmak yerine dizin listelenir, yani
       yarın eklenen bir aşama klasörü kendiliğinden kapsama girer.
    3. **Aşama ağaçlarının TAMAMI** — kökler `runs.ASAMALAR`'dan türetilir
       (`kök/<aşama>`), var olanların altındaki her düğüm süpürülür. Asıl korunan şey
       burada yaşar: GEÇMİŞ turların denetçi raporları. Kutulu kullanıcı onlardan birini
       okuyabilseydi K-79 körlüğü dosya sistemi üzerinden delinirdi — iki denetçi AYNI
       unix kullanıcısında koşar, dosya izinleriyle ayrılamazlar.

    **Maliyet dürüstçe:** süpürme tur sayısıyla büyür (bugün ölçüldü: aşama ağaçlarında
    18 düğüm). Tek bir yaprağı elle seçmek taramayı "zaten bildiğimi tekrar kontrol et"e
    indirgerdi; yavaşlama olursa bu GÖRÜNÜR bir sinyaldir.
    """
    kok = runs.ARASTIRMA_DEPOSU_KOKU
    if not kok.exists():
        return []
    hedefler = [kok, *sorted(kok.iterdir())]
    for asama in runs.ASAMALAR:
        agac = kok / asama
        if agac.is_dir():
            hedefler.extend(sorted(agac.rglob("*")))
    return hedefler


def _hedefler() -> list[Path]:
    """Yasak hedefler KAVRAMDAN türetilir, elle seçilmez.

    Kavram: *"root'un ev dizini ve altındaki her şey"* — kutunun dayandığı mekanizma
    tam olarak budur (`~root` izni `700`). Listeye elle üç dosya yazmak, taramayı
    "zaten bildiğimi tekrar kontrol et"e indirger; o yüzden kökün KENDİSİ ve altındaki
    VAR OLAN araç/sır yolları birlikte ölçülür.

    Kanonik denetçi ağacı da (T6) AYNI kümededir: yasak-erişim testi ve onun pozitif
    kontrolü ikisi de bu listeden okur, yani ağaç ayrı bir kapının değil aynı kapının
    kapsamındadır.
    """
    adaylar = [
        ROOT_EVI,
        BACKEND_ENV,
        *sorted(ROOT_EVI.glob(".c*")),
        *_kanonik_agac_hedefleri(),
    ]
    return [yol for yol in adaylar if yol.exists()]


@pytest.mark.skipif(_atla_gerekcesi() is not None, reason=str(_atla_gerekcesi()))
def test_izolasyon_kullanicisi_root_evini_okuyamaz() -> None:
    """Kutu KAPALI: yasak hedeflerin HİÇBİRİ o kullanıcı adına okunamaz."""
    hedefler = _hedefler()
    assert hedefler, "hedef kümesi BOŞ — prob ölçmüyor (yol türetimi bayatlamış)"

    sizanlar = [yol for yol in hedefler if _okuma_denemesi(yol, kullanici=KULLANICI)]
    assert not sizanlar, (
        f"{KULLANICI} kullanıcısı şunları OKUYABİLDİ: {sizanlar} — "
        "denetçi kutusu açık, alt süreç sırlara erişebilir"
    )


@pytest.mark.skipif(_atla_gerekcesi() is not None, reason=str(_atla_gerekcesi()))
def test_prob_erisimi_gercekten_olcuyor_pozitif_kontrol() -> None:
    """Totoloji koruması: aynı prob root olarak KOŞARSA hepsini okuyabilmeli.

    Bu test kırmızıya dönerse yukarıdaki yeşil ANLAMSIZDIR — prob bozuktur, kutu
    kapalı olduğu için değil ölçemediği için "erişilemez" diyordur.
    """
    hedefler = _hedefler()
    okunamayanlar = [yol for yol in hedefler if not _okuma_denemesi(yol, kullanici=None)]
    assert not okunamayanlar, (
        f"prob root olarak da okuyamadı: {okunamayanlar} — ölçüm bozuk, "
        "yasak-erişim testinin yeşili kanıt DEĞİL"
    )


@pytest.mark.skipif(_atla_gerekcesi() is not None, reason=str(_atla_gerekcesi()))
def test_izolasyon_kullanicisinin_sudo_yetkisi_yok() -> None:
    """Kutu `sudo` ile atlanamaz — üyelik kaldırıldı (2026-09-17, T1).

    Grup listesine bakmak YETMEZ: yetki `sudoers` dosyalarından da gelebilir.
    Ölçüm `sudo`'nun KENDİ kararını sorar.
    """
    sonuc = subprocess.run(
        ["sudo", "-l", "-U", KULLANICI], capture_output=True, text=True, timeout=60
    )
    cikti = (sonuc.stdout + sonuc.stderr).lower()
    assert cikti.strip(), "sudo -l çıktısı BOŞ — prob ölçmüyor"
    assert "not allowed to run sudo" in cikti, (
        f"{KULLANICI} sudo çalıştırabiliyor — kutu kâğıttan: "
        f"sudo kararı: {cikti.strip()[:200]}"
    )


@pytest.mark.skipif(_atla_gerekcesi() is not None, reason=str(_atla_gerekcesi()))
def test_kanonik_denetci_agaci_kutulu_kullaniciya_KAPALI() -> None:
    """Kutulu kullanıcı kanonik `denetim/` ağacına GİREMEZ (T6).

    Yukarıdaki genel tripwire bu ağacı zaten kapsıyor; bu test iddianın KENDİSİNİ
    adlandırır ve **sessiz yeşili** engeller: ağaç yoksa ya da yalnız boş klasörlerden
    ibaretse genel test yine yeşil kalırdı ve kimse "geçmiş raporlar okunamıyor"un hiç
    ölçülmediğini fark etmezdi.

    Ölçüm sahiplik/izin bitine DEĞİL, gerçek okuma denemesine dayanır — sahiplik ölçmek
    erişim ölçmek değildir (bu görevde bir kez tam bu hata yapıldı).
    """
    hedefler = _kanonik_agac_hedefleri()
    if not hedefler:
        pytest.skip(
            f"{runs.ARASTIRMA_DEPOSU_KOKU} YOK — kanonik ağaç bu makinede ölçülemiyor"
        )
    raporlar = [
        yol
        for yol in hedefler
        if yol.is_file() and (runs.ARASTIRMA_DEPOSU_KOKU / "denetim") in yol.parents
    ]
    assert raporlar, (
        "denetim ağacında tek bir DOSYA bile yok — 'geçmiş raporlar okunamıyor' "
        "iddiası ölçülmemiş olurdu (boş klasör hiçbir şey kanıtlamaz)"
    )

    sizanlar = [yol for yol in hedefler if _okuma_denemesi(yol, kullanici=KULLANICI)]
    assert not sizanlar, (
        f"{KULLANICI} kullanıcısı kanonik ağaçtan şunları OKUYABİLDİ: {sizanlar} — "
        "denetçi kendi sahnesi dışından, geçmiş turların raporlarına erişebilir"
    )
