"""`brief-doctor` mekanik girdi kapısı (Plan 2 Task 7).

Ölçülen sözleşme tek cümleyle: **kapı bugün hiçbir kaynağı ELEMEZ.** Adet alt
sınırları (cta ≥5 · kanca ≥3 · görsel kod ≥20 · video kodu ≥10 · dönem ≥6;
dönem başına kanca ≥2 · cta ≥2 · gorsel_vurgu ≥5) ölçülmemiş sözleşme
kurallarıdır (spec §8.3, İlke 9 uyum hükmü) — hepsi `not` üretir. `eleme`
seviyesi TİPTE vardır (K-88 kapanınca kullanılacak) ama bugün hiçbir kontrol
onu üretmez; bu dosya o hâli **ölçer**, iddia etmez.

Bu dosyanın kanıtlamak zorunda olduğu zor noktalar:

* **Kapsama kimlik iddiası DEĞİLDİR.** `CHECKS`'i gezip kendisiyle
  karşılaştırmak bir şey kanıtlamaz. Beklenen aile kümesi burada KAVRAMDAN
  (spec-input §7.3 "Kontrol kümesi" tablosu) yazılır, modülün kanonik sabitiyle
  ve `CHECKS`'in gerçek kapsamıyla AYRI AYRI karşılaştırılır.
* **Seviye matrisi ÜRETİLİR**, elle seçilmiş assert'lerle yazılmaz — ve
  matrisin kendisi iki kontrol koluyla sınanır: bir kontrolün seviyesi `eleme`ye
  çevrilince matris KIRMIZI olmalı, boş kümede ise sessizce YEŞİL olmamalı.
* **Sözleşme sabitleri uydurulamaz.** Sekiz alan adı, dört tür etiketi, dört
  kanal anahtarı ve beş bölüm harfi PİNLENMİŞ `_SABLON.md`'den, hash
  doğrulanarak okunur. Depo yoksa test ATLANMAZ, DÜŞER (fail-closed) —
  `test_contract_pin.py` ile aynı disiplin.
"""

from __future__ import annotations

import ast
import dataclasses
import hashlib
import itertools
import json
import random
import re
import sys
import unicodedata
from pathlib import Path
from unittest import mock

import pytest

from app.services.sector_pipeline import brief_doctor as bd
from app.services.sector_pipeline import identity

MONOREPO_KOK = Path(__file__).resolve().parents[4]
PIN_PATH = MONOREPO_KOK / "shared/contracts/research-contracts.pin.json"
ARASTIRMA_DEPOSU = Path("/root/otomaix-sosyal-medya-arastirmasi")


# ─── Kavramdan yazılmış beklentiler ─────────────────────────────────────────
#
# Kaynak: spec-input §7.3 "Kontrol kümesi" tablosu (dokuz satır). SEKİZİ kapıya
# girer; DOKUZUNCU ("görsel/video/özel gün görsel vurgu alanlarında metin
# unsuru") bilinçle DIŞARIDADIR — spec-input onu bugün mekanik kapının değil
# DENETÇİNİN kuralı sayar (`[metin-öğesi]` bayrağı, §7.4) ve mekanik kapsama
# oranının ÖLÇÜLMEMİŞ olduğunu söyler.

BEKLENEN_AILELER = (
    "bolum-ve-alan-tamligi",
    "adet-alt-sinirlari",
    "dil-kurali",
    "url-bicimi",
    "tur-etiketi",
    "ozel-gun-gerekce-tablosu",
    "uzun-alinti",
    "bicim-kurallari",
)

# Sekizinci satır ("Biçim kuralları") birden çok alt kural paketler; granülerlik
# alt kural başına BİR `Check`'tir ve modülde kanonik sabitten türer.
BEKLENEN_BICIM_ALT_KURALLARI = (
    "tam-alan-adi",
    "sozlesme-disi-bolum",
    "ayri-madde-isareti",
    "govde-dipnotu",
    "etiket-yazimi",
)

DISLANAN_AILE_IZI = "metin-oge"


# ─── Kurgu üreteci ──────────────────────────────────────────────────────────
#
# Tek üreteç, her düğmesi BİR kontrol ailesini ateşler. Testler elle yazılmış
# metin parçaları değil, bu üreteçten TÜRETİLMİŞ matrisler kullanır.

_DONEM_ADLARI = (
    "Sevgililer Günü",
    "8 Mart Dünya Kadınlar Günü",
    "Anneler Günü",
    "Babalar Günü",
    "Kasım indirim dönemi",
    "Yılbaşı",
    "23 Nisan",
    "29 Ekim",
)
_DONEM_TURLERI = (
    "ticari-firsat",
    "kutlama",
    "ticari-firsat",
    "ticari-firsat",
    "ticari-firsat",
    "karma",
    "kutlama",
    "kutlama",
)


def kaynak(
    *,
    cta: int = 5,
    kanca: int = 3,
    gorsel: int = 20,
    hareket: int = 5,
    sahne: int = 5,
    donem: int = 6,
    donem_kanca: int = 2,
    donem_cta: int = 2,
    donem_gorsel: int = 5,
    anma_donemi: str | None = None,
    eksik_bolum: str | None = None,
    fazla_bolum: bool = False,
    uzun_alinti: bool = False,
    dipnot: bool = False,
    bozuk_url: bool = False,
    tablo: bool = True,
    bozuk_tur_etiketi: bool = False,
    turkce_gorsel_kod: bool = False,
    birlesik_madde: bool = False,
    yeniden_adlandirilmis_baslik: bool = False,
    bozuk_kanal_anahtari: bool = False,
) -> str:
    """`_SABLON.md` biçimine uyan bir araştırma çıktısı üretir.

    Varsayılan çağrı HİÇBİR not üretmeyen temiz kaynaktır; her adlandırılmış
    düğme tek bir kontrol ailesini bilerek bozar.

    `anma_donemi`: `None` (yok) · `"resmi"` (dört yuva da AYNEN
    `içerik-önerilmez`) · `"serbest"` (serbest cümleyle boşluk — sözleşme bunu
    boş alan sayar).
    """
    satirlar: list[str] = ["ARAŞTIRMA GÖREVİ: kuyumculuk sektörü çıktısı", ""]

    donem_adlari = list(_DONEM_ADLARI[:donem])
    donem_turleri = list(_DONEM_TURLERI[:donem])
    if anma_donemi is not None and donem_adlari:
        donem_adlari[-1] = "10 Kasım"
        donem_turleri[-1] = "anma"

    # ── Bölüm A ──────────────────────────────────────────────────────────
    if eksik_bolum != "A":
        satirlar += ["## Bölüm A — GÖREV A paketi", ""]
        satirlar += [
            "### kapsam ve tanim" if yeniden_adlandirilmis_baslik else "### kapsam",
            "Altin ve pirlanta taki perakendesi; saat haric tutulur.",
            "",
        ]
        ton = "Resmiyet olculu; duygu ekseni guven ve kalicilik uzerinedir."
        if dipnot:
            ton += " [1]"
        satirlar += ["### ton_ve_dil", ton, ""]

        satirlar += ["### cta_kaliplari"]
        satirlar += [
            f"- [urun-{i}] icin randevu daveti — satis — Sektore ozgu guven vurgusu."
            for i in range(1, cta + 1)
        ]
        if birlesik_madde:
            satirlar += [
                "Ayrica kaydet ve kesfet cagrilari ayni paragrafta birlestirilmistir."
            ]
        satirlar += [""]

        satirlar += ["### kanca_kaliplari"]
        satirlar += [
            f"- [duygusal an-{i}] + [urun bagi] + [davet]" for i in range(1, kanca + 1)
        ]
        satirlar += [""]

        satirlar += ["### gorsel_kodlar"]
        gorsel_maddeler = [
            f"- soft diffused light macro composition {i:02d}"
            for i in range(1, gorsel + 1)
        ]
        if turkce_gorsel_kod and gorsel_maddeler:
            gorsel_maddeler[0] = "- yumusak ışık altında makro çekim"
        satirlar += gorsel_maddeler
        satirlar += [""]

        satirlar += ["### video_kodlar", "#### hareket"]
        satirlar += [f"- slow orbital rotation {i:02d}" for i in range(1, hareket + 1)]
        satirlar += ["#### sahne"]
        satirlar += [f"- velvet tray reveal scene {i:02d}" for i in range(1, sahne + 1)]
        satirlar += [""]

        satirlar += ["### takvim_temalari"]
        satirlar += [f"- {ad} — donemin icerik acisi." for ad in donem_adlari]
        satirlar += [""]

        satirlar += ["### yasaklar_ve_hassasiyetler"]
        satirlar += [
            f"- Yasak {i} — mevzuat gerekcesiyle asla yapilmaz." for i in range(1, 5)
        ]
        satirlar += [""]

    if fazla_bolum:
        satirlar += ["## Yönetici Özeti", "", "- Sozlesme disi bir bolum.", ""]

    # ── Bölüm B ──────────────────────────────────────────────────────────
    if eksik_bolum != "B":
        satirlar += ["## Bölüm B — GÖREV B çıktısı", ""]
        if tablo:
            satirlar += ["| dönem | karar | tür | gerekçe |", "|---|---|---|---|"]
            for sira, (ad, tur) in enumerate(zip(donem_adlari, donem_turleri)):
                yazim = tur
                if bozuk_tur_etiketi and sira == 0:
                    yazim = "ticari-fırsat"
                satirlar += [f"| {ad} | secildi | {yazim} | Gerekce cumlesi. |"]
            satirlar += [""]

        for ad, tur in zip(donem_adlari, donem_turleri):
            satirlar += [f"### {ad}"]
            if tur == "anma" and anma_donemi is not None:
                deger = "içerik-önerilmez" if anma_donemi == "resmi" else "yok"
                satirlar += [
                    f"mesaj_ekseni: {deger}",
                    f"kanca: {deger}",
                    f"cta: {deger}",
                    f"gorsel_vurgu: {deger}",
                    "",
                ]
                continue
            satirlar += [f"mesaj_ekseni: {ad} icin duygusal eksen."]
            satirlar += ["kanca"]
            satirlar += [
                f"- [an-{i}] + [urun bagi] acilis kalibi"
                for i in range(1, donem_kanca + 1)
            ]
            satirlar += ["cta"]
            satirlar += [
                f"- randevu daveti {i} — satis — Gerekce cumlesi."
                for i in range(1, donem_cta + 1)
            ]
            satirlar += ["gorsel_vurgu"]
            satirlar += [
                f"- warm candlelit close up {i:02d}"
                for i in range(1, donem_gorsel + 1)
            ]
            satirlar += [""]

    # ── Bölüm C ──────────────────────────────────────────────────────────
    #
    # Sözleşme 2026-09-07'de bu bölümü SABİT SÜTUNLU tabloya çevirdi (dış depo
    # `7964ed6`); fixture serbest madde listesi olmaktan çıktı. Satır kümesi
    # ELLE yazılmaz: sekiz alan + belgede İŞLENEN dönemler üstünde üretilir,
    # çünkü kapı artık BÜTÜNLÜK de ölçüyor (her alan/dönem için ≥1 satır).
    if eksik_bolum != "C":
        satirlar += ["## Bölüm C — KAYNAKLAR", ""]
        satirlar += [
            "| " + " | ".join(bd.C_TABLOSU_SUTUNLARI) + " |",
            "|" + "---|" * len(bd.C_TABLOSU_SUTUNLARI),
        ]
        anahtarlar = list(bd.TEMEL_ALANLAR) + list(donem_adlari)
        for sira, anahtar in enumerate(anahtarlar, start=1):
            url = f"https://sektor-yayini.example/kaynak-{sira:02d}"
            if bozuk_url and sira == 1:
                url = "sektor-yayini.example/kaynak-01"
            satirlar += [
                f"| {anahtar} | Sektore ozgu bulgu {sira:02d} | "
                f"Sektor Yayini {sira:02d} | {url} | 2025-03 | hayır |"
            ]
        satirlar += [""]

    # ── Bölüm D ──────────────────────────────────────────────────────────
    if eksik_bolum != "D":
        satirlar += ["## Bölüm D — EK BULGULAR", ""]
        anahtar = "instagram_magaza" if bozuk_kanal_anahtari else "eticaret_sitesi"
        satirlar += [
            f"- kanca_kaliplari icindeki canli yayin kalibi [kanal-bağımlı: {anahtar}]"
        ]
        if uzun_alinti:
            satirlar += [
                "> " + " ".join(f"kelime{i}" for i in range(1, 46)),
            ]
        satirlar += [""]

    # ── Bölüm E ──────────────────────────────────────────────────────────
    if eksik_bolum != "E":
        satirlar += ["## Bölüm E — GÜVEN NOTU", ""]
        satirlar += ["- Video kodlarinin kaynak tabani zayiftir.", ""]

    return "\n".join(satirlar) + "\n"


def _rapor(*, _ad: str = "KAYNAK-1", **kwargs) -> "bd.DoctorReport":
    return bd.run(kaynak(**kwargs), source_name=_ad)


def _aileler(rapor) -> set[str]:
    return {bulgu.aile for bulgu in rapor.notlar + rapor.elemeler}


def _mesajlar(rapor) -> str:
    return " | ".join(b.mesaj for b in rapor.notlar + rapor.elemeler)


# ─── Pinlenmiş sözleşmeden okunan beklentiler ───────────────────────────────


def _pinli_sablon() -> str:
    """`_SABLON.md`'yi pin manifestindeki sha256'ya karşı doğrulayarak okur."""
    pin = json.loads(PIN_PATH.read_text(encoding="utf-8"))
    beklenen = pin["files"]["_SABLON.md"]
    ham = (ARASTIRMA_DEPOSU / "_SABLON.md").read_bytes()
    bulunan = hashlib.sha256(ham).hexdigest()
    assert bulunan == beklenen, (
        f"_SABLON.md pinden sapmış (pin {beklenen}, disk {bulunan}) — bu "
        "dosyadaki sözleşme sabitleri artık doğrulanamaz"
    )
    return ham.decode("utf-8")


def test_temel_alanlar_pinlenmis_sablondan_okunur() -> None:
    """Sekiz alan adı UYDURULMAZ: pinli sözleşmeden sıra dâhil çıkarılır."""
    metin = _pinli_sablon()
    blok = re.search(
        r"- Alan başlıklarını TAM alan adıyla yaz \((.*?)\)", metin, re.S
    )
    assert blok is not None, "sözleşmede alan adı kuralı bulunamadı"
    sozlesme_alanlari = tuple(re.findall(r"`([a-z_]+)`", blok.group(1)))
    assert sozlesme_alanlari == bd.TEMEL_ALANLAR
    assert tuple(sorted(bd.METIN_ALANLARI + bd.LISTE_ALANLARI)) == tuple(
        sorted(bd.TEMEL_ALANLAR)
    )


def test_tur_etiketleri_ve_kanal_anahtarlari_pinlenmis_sablondan_okunur() -> None:
    metin = _pinli_sablon()
    tur_blok = re.search(
        r"- GÖREV B tür etiketlerini aynen şu yazımla kullan: (.*?)\.\n", metin, re.S
    )
    assert tur_blok is not None
    assert tuple(re.findall(r"`([a-z\-]+)`", tur_blok.group(1))) == bd.TUR_ETIKETLERI

    kanal_blok = re.search(
        r"- Kanal etiketinin anahtarını aynen şu dört yazımdan biriyle yaz:(.*?)"
        r"\(Bölüm 2\)",
        metin,
        re.S,
    )
    assert kanal_blok is not None
    assert (
        tuple(re.findall(r"`([a-z_]+)`", kanal_blok.group(1))) == bd.KANAL_ANAHTARLARI
    )
    assert bd.BILINCLI_BOS in metin


def test_bolum_harfleri_pinlenmis_sablondan_okunur() -> None:
    metin = _pinli_sablon()
    assert tuple(re.findall(r"^Bölüm ([A-E]) —", metin, re.M)) == bd.BOLUM_HARFLERI


# ─── Planın saydığı sekiz test ──────────────────────────────────────────────


def test_clean_source_passes() -> None:
    """Pozitif kontrol: sözleşmeye uyan kaynak NOTSUZ geçer."""
    rapor = _rapor()
    assert rapor.notlar == (), _mesajlar(rapor)
    assert rapor.elemeler == ()
    assert rapor.sonuc == bd.SONUC_GECTI
    assert rapor.kaynak_adi == "KAYNAK-1"


ADET_DUGMELERI = (
    {"cta": 2},
    {"kanca": 1},
    {"gorsel": 10},
    {"hareket": 2},
    {"sahne": 2},
    {"donem": 3},
    {"donem_kanca": 1},
    {"donem_cta": 1},
    {"donem_gorsel": 2},
)


@pytest.mark.parametrize("dugme", ADET_DUGMELERI, ids=lambda d: next(iter(d)))
def test_count_shortfall_produces_note_not_elimination(dugme: dict) -> None:
    """İlke 9 kapısı: ölçülmemiş adet sınırı ELEME üretemez, yalnız NOT.

    Bu test, ölçülmemiş bir sayının ileride sessizce kapıya çevrilmesini
    engeller (spec §8.3 İlke 9 uyum hükmü).
    """
    rapor = _rapor(**dugme)
    assert "adet-alt-sinirlari" in _aileler(rapor), _mesajlar(rapor)
    assert rapor.elemeler == ()
    assert rapor.sonuc == bd.SONUC_NOTLU_GECTI
    assert all(bulgu.seviye == bd.SEVIYE_NOT for bulgu in rapor.notlar)


def test_icerik_onerilmez_passes_fill_check() -> None:
    """K-120: resmî `içerik-önerilmez` değeri doluluk kontrolünü geçirir."""
    rapor = _rapor(anma_donemi="resmi")
    assert rapor.notlar == (), _mesajlar(rapor)
    assert rapor.sonuc == bd.SONUC_GECTI

    # Kontrol kolu: serbest cümleyle boşluk sözleşmenin resmî temsili DEĞİLDİR.
    serbest = _rapor(anma_donemi="serbest")
    assert serbest.sonuc == bd.SONUC_NOTLU_GECTI
    assert "bolum-ve-alan-tamligi" in _aileler(serbest), _mesajlar(serbest)
    assert serbest.elemeler == ()


def test_long_quote_produces_note() -> None:
    """Sözleşmenin TEK açık eşlemesi: 40+ kelime alıntı → not (eleme değil)."""
    rapor = _rapor(uzun_alinti=True)
    assert "uzun-alinti" in _aileler(rapor), _mesajlar(rapor)
    assert rapor.elemeler == ()
    assert rapor.sonuc == bd.SONUC_NOTLU_GECTI


def test_extra_section_produces_note() -> None:
    """Beş bölüm dışında bölüm EKLEME → biçim ihlali, not seviyesinde."""
    rapor = _rapor(fazla_bolum=True)
    kimlikler = {b.kontrol for b in rapor.notlar}
    assert "bicim-kurallari/sozlesme-disi-bolum" in kimlikler, _mesajlar(rapor)
    assert rapor.elemeler == ()
    assert rapor.sonuc == bd.SONUC_NOTLU_GECTI


def _sahte_elenmis(ad: str) -> "bd.DoctorReport":
    """Elenmiş rapor — bugün hiçbir kontrol üretmediği için ELLE kurulur."""
    bulgu = bd.Bulgu(
        kontrol="sahte-kontrol",
        aile="bolum-ve-alan-tamligi",
        seviye=bd.SEVIYE_ELEME,
        mesaj="gelecekte K-88 kapanınca üretilecek eleme",
    )
    return bd.DoctorReport(
        sonuc=bd.SONUC_ELENDI, notlar=(), elemeler=(bulgu,), kaynak_adi=ad
    )


def test_round_gate_stops_below_two_sources() -> None:
    """K-127 = 2: geçerli kaynak sayısı 2'nin ALTINA düşerse koşu durur."""
    tek = bd.gate_round([_rapor(), _sahte_elenmis("KAYNAK-2")])
    assert tek.dur is True
    assert tek.gecerli_kaynak_sayisi == 1
    assert tek.elenen_kaynak_sayisi == 1
    assert tek.taban == 2
    assert tek.bildirim, "durduran kapı yöneticiye bildirim metni ÜRETMEK zorunda"

    bos = bd.gate_round([])
    assert bos.dur is True
    assert bos.gecerli_kaynak_sayisi == 0


def test_round_gate_allows_exactly_two_sources() -> None:
    """Pozitif kontrol: TAM İKİ geçerli kaynak koşuyu durdurmaz."""
    gate = bd.gate_round(
        [_rapor(), _rapor(_ad="KAYNAK-2", cta=2), _sahte_elenmis("KAYNAK-3")]
    )
    assert gate.dur is False
    assert gate.gecerli_kaynak_sayisi == 2
    assert gate.elenen_kaynak_sayisi == 1
    assert gate.bildirim == ""


def test_checks_tuple_is_frozen() -> None:
    """K-89: kontrol kümesi SABİTLENMİŞTİR — demet ve üyeleri değiştirilemez."""
    assert isinstance(bd.CHECKS, tuple)
    assert not hasattr(bd.CHECKS, "append")
    assert bd.Check.__dataclass_params__.frozen is True
    for check in bd.CHECKS:
        with pytest.raises(dataclasses.FrozenInstanceError):
            check.seviye = bd.SEVIYE_ELEME  # type: ignore[misc]
    # Kimlikler benzersiz olmalı: aynı kimlik iki kez geçseydi seviye matrisi
    # bir üyeyi sessizce gizlerdi.
    kimlikler = [check.kimlik for check in bd.CHECKS]
    assert len(kimlikler) == len(set(kimlikler))


# ─── Kapsama, seviye matrisi ve kontrol kolları ─────────────────────────────


def test_checks_cover_canonical_family_constant() -> None:
    """Kapsama: kavram → kanonik sabit → `CHECKS`. Üç katman da hizalı olmalı."""
    assert bd.KONTROL_AILELERI == BEKLENEN_AILELER
    assert {check.aile for check in bd.CHECKS} == set(BEKLENEN_AILELER)
    assert bd.BICIM_ALT_KURALLARI == BEKLENEN_BICIM_ALT_KURALLARI
    bicim_kimlikleri = tuple(
        check.kimlik for check in bd.CHECKS if check.aile == "bicim-kurallari"
    )
    assert bicim_kimlikleri == tuple(
        f"bicim-kurallari/{alt}" for alt in BEKLENEN_BICIM_ALT_KURALLARI
    )
    # Aile başına en az bir kontrol; tek aile bile boş kalırsa kapsama sahtedir.
    for aile in BEKLENEN_AILELER:
        assert [c for c in bd.CHECKS if c.aile == aile], f"{aile} kontrolsüz"


def test_metin_ogesi_control_is_deliberately_excluded() -> None:
    """Dokuzuncu tablo satırı kapıda DEĞİLDİR (spec-input §7.3/§7.4).

    Unutulmadı: bugün denetçinin kuralı ve mekanik kapsama oranı ölçülmemiş.
    """
    for check in bd.CHECKS:
        assert DISLANAN_AILE_IZI not in check.kimlik
        assert DISLANAN_AILE_IZI not in check.aile
    assert DISLANAN_AILE_IZI not in " ".join(bd.KONTROL_AILELERI)
    assert bd.DISLANAN_KONTROL_GEREKCESI.strip(), (
        "dışlama gerekçesi modülde YAZILI olmalı — sonraki okuyucu 'unutulmuş' "
        "sanmasın"
    )


def _matris_ihlalleri(checks) -> list[str]:
    """Seviye matrisi: ÜRETİLMİŞ ihlal listesi (boş liste = matris yeşil).

    Boş küme ihlal SAYILIR: aksi hâlde `CHECKS` boşaltıldığında matris sessizce
    yeşile döner ve kapı sökülmüş olmasına rağmen test geçerdi.
    """
    if not checks:
        return ["kontrol kümesi BOŞ — matris ölçecek bir şey bulamadı"]
    return [
        f"{check.kimlik} seviyesi {check.seviye!r} (beklenen {bd.SEVIYE_NOT!r})"
        for check in checks
        if check.seviye != bd.SEVIYE_NOT
    ]


def test_every_check_is_note_level() -> None:
    """Bugün ELEME üreten kontrol kümesi BOŞTUR — üretilmiş matrisle ölçülür."""
    assert _matris_ihlalleri(bd.CHECKS) == []
    assert {check.seviye for check in bd.CHECKS} == {bd.SEVIYE_NOT}


def test_level_matrix_has_mutation_and_empty_control_arms() -> None:
    """Kapıyı sök → matris KIRMIZI; kümeyi boşalt → matris yine KIRMIZI."""
    assert _matris_ihlalleri(()) == [
        "kontrol kümesi BOŞ — matris ölçecek bir şey bulamadı"
    ]
    for sira in range(len(bd.CHECKS)):
        mutant = list(bd.CHECKS)
        mutant[sira] = dataclasses.replace(mutant[sira], seviye=bd.SEVIYE_ELEME)
        ihlaller = _matris_ihlalleri(tuple(mutant))
        assert len(ihlaller) == 1
        assert bd.CHECKS[sira].kimlik in ihlaller[0]


AILE_DUGMELERI = {
    "bolum-ve-alan-tamligi": {"eksik_bolum": "D"},
    "adet-alt-sinirlari": {"cta": 2},
    "dil-kurali": {"turkce_gorsel_kod": True},
    "url-bicimi": {"bozuk_url": True},
    "tur-etiketi": {"bozuk_tur_etiketi": True},
    "ozel-gun-gerekce-tablosu": {"tablo": False},
    "uzun-alinti": {"uzun_alinti": True},
    "bicim-kurallari": {"fazla_bolum": True},
}


@pytest.mark.parametrize("aile", BEKLENEN_AILELER)
def test_her_aile_ihlalde_not_uretir(aile: str) -> None:
    """Her kontrol ailesi GERÇEKTEN ateşliyor mu — üretilmiş ihlal matrisi."""
    rapor = _rapor(**AILE_DUGMELERI[aile])
    assert aile in _aileler(rapor), _mesajlar(rapor)
    assert rapor.elemeler == ()
    assert rapor.sonuc == bd.SONUC_NOTLU_GECTI


BICIM_DUGMELERI = {
    "tam-alan-adi": {"yeniden_adlandirilmis_baslik": True},
    "sozlesme-disi-bolum": {"fazla_bolum": True},
    "ayri-madde-isareti": {"birlesik_madde": True},
    "govde-dipnotu": {"dipnot": True},
    "etiket-yazimi": {"bozuk_kanal_anahtari": True},
}


@pytest.mark.parametrize("alt_kural", BEKLENEN_BICIM_ALT_KURALLARI)
def test_her_bicim_alt_kurali_ateslenebilir(alt_kural: str) -> None:
    rapor = _rapor(**BICIM_DUGMELERI[alt_kural])
    kimlikler = {b.kontrol for b in rapor.notlar}
    assert f"bicim-kurallari/{alt_kural}" in kimlikler, _mesajlar(rapor)
    assert rapor.elemeler == ()


# ─── `elendi` temsil edilebilir ama bugün ULAŞILAMAZ ────────────────────────


def test_elendi_is_representable_in_the_type() -> None:
    """`eleme` seviyesi TİPTE vardır — K-88 kapanınca kullanılacak."""
    assert bd.SEVIYE_ELEME in bd.SEVIYELER
    assert bd.SONUC_ELENDI in bd.SONUCLAR
    bulgu = bd.Bulgu("x", "bolum-ve-alan-tamligi", bd.SEVIYE_ELEME, "m")
    assert bd.sonuc_belirle((), (bulgu,)) == bd.SONUC_ELENDI
    assert bd.sonuc_belirle((bulgu,), ()) == bd.SONUC_NOTLU_GECTI
    assert bd.sonuc_belirle((), ()) == bd.SONUC_GECTI


BOZUK_KAYNAKLAR = (
    {},
    {"cta": 0, "kanca": 0, "gorsel": 0, "hareket": 0, "sahne": 0, "donem": 0},
    {"eksik_bolum": "A"},
    {"eksik_bolum": "B"},
    {"eksik_bolum": "C"},
    {"eksik_bolum": "D"},
    {"eksik_bolum": "E"},
    {"fazla_bolum": True, "uzun_alinti": True, "dipnot": True},
    {"bozuk_url": True, "tablo": False, "bozuk_tur_etiketi": True},
    {"turkce_gorsel_kod": True, "birlesik_madde": True},
    {"yeniden_adlandirilmis_baslik": True, "bozuk_kanal_anahtari": True},
    {"anma_donemi": "serbest"},
)


@pytest.mark.parametrize("dugmeler", BOZUK_KAYNAKLAR)
def test_no_source_reaches_elendi_today(dugmeler: dict) -> None:
    """Ölçüm: bugün HİÇBİR girdi `elendi` üretemez (K-88 kapanmadı)."""
    rapor = _rapor(**dugmeler)
    assert rapor.elemeler == ()
    assert rapor.sonuc != bd.SONUC_ELENDI


def test_empty_source_is_noted_not_eliminated() -> None:
    rapor = bd.run("", source_name="BOŞ")
    assert rapor.elemeler == ()
    assert rapor.sonuc == bd.SONUC_NOTLU_GECTI
    assert "bolum-ve-alan-tamligi" in _aileler(rapor)


# ─── Değişmezlik (EngineInputs `donmus`'tan GEÇİRMEZ) ───────────────────────


def test_report_and_gate_are_self_freezing() -> None:
    """`RoundGate`/`DoctorReport` KENDİLİĞİNDEN değişmez olmalı.

    Arayüz eki: `EngineInputs.__post_init__` yalnız DÖRT alanı
    `identity.donmus`'tan geçirir (`aktif_paket` · `aktif_birimler` ·
    `son_turlarin_cikarmalari` · `takvim_anahtarlari`); `mekanik_eleme` o
    listede DEĞİLDİR.
    """
    bulgu = bd.Bulgu("x", "uzun-alinti", bd.SEVIYE_NOT, "m")
    rapor = bd.DoctorReport(
        sonuc=bd.SONUC_NOTLU_GECTI, notlar=[bulgu], elemeler=[], kaynak_adi="K"
    )
    assert isinstance(rapor.notlar, tuple)
    assert isinstance(rapor.elemeler, tuple)
    with pytest.raises(dataclasses.FrozenInstanceError):
        rapor.sonuc = bd.SONUC_GECTI  # type: ignore[misc]

    gate = bd.gate_round([rapor, dataclasses.replace(rapor, kaynak_adi="K2")])
    assert isinstance(gate.raporlar, tuple)
    with pytest.raises(dataclasses.FrozenInstanceError):
        gate.dur = True  # type: ignore[misc]
    assert bd.DoctorReport.__dataclass_params__.frozen is True
    assert bd.RoundGate.__dataclass_params__.frozen is True
    assert bd.Bulgu.__dataclass_params__.frozen is True


def test_report_rejects_foreign_finding_types() -> None:
    """Fail-closed: `Bulgu` olmayan öğe rapora sessizce giremez."""
    with pytest.raises(TypeError):
        bd.DoctorReport(
            sonuc=bd.SONUC_GECTI, notlar=("düz metin",), elemeler=(), kaynak_adi="K"
        )
    with pytest.raises(TypeError):
        bd.RoundGate(
            dur=False,
            gecerli_kaynak_sayisi=2,
            elenen_kaynak_sayisi=0,
            taban=bd.KAYNAK_TABANI,
            bildirim="",
            raporlar=("düz metin",),
        )


def test_sonuc_degerleri_plan_yazimiyla_ayni() -> None:
    """Plan 950: `sonuc` ∈ {`gecti`,`notlu-gecti`,`elendi`} — yazım BAĞLAYICI."""
    assert bd.SONUCLAR == ("gecti", "notlu-gecti", "elendi")
    assert bd.SEVIYELER == ("not", "eleme")
    assert bd.KAYNAK_TABANI == 2


# ─── H1: bozuk rapor / bozuk kapı TEMSİL EDİLEMEZ ───────────────────────────
#
# Emsal `sector_pipeline/contracts.py::ContractPin.__post_init__`: yapısal
# değişmezler yapıcıda zorlanır ki `run`/`gate_round` yolunu ATLAYIP doğrudan
# kuran çağrıcılar da kapsansın. Aşağıdaki üç matris o üç ayağı ölçer:
# (a) kaynak kimliği yetkilidir, (b) rapor kendi bulgularıyla tutarlıdır,
# (c) `RoundGate`'in türetilmiş alanları ham veriden hesaplanır.


def _not_bulgu() -> "bd.Bulgu":
    return bd.Bulgu("k", "uzun-alinti", bd.SEVIYE_NOT, "m")


def _eleme_bulgu() -> "bd.Bulgu":
    return bd.Bulgu("k", "uzun-alinti", bd.SEVIYE_ELEME, "m")


# Kombinasyonlar KAVRAMDAN üretilir: her koleksiyon ya boş, ya doğru seviyeli,
# ya YANLIŞ seviyeli bir bulgu taşır. Üçü üçle çarpılır, sonra üç `sonuc`la.
_KOLEKSIYON_SECENEKLERI = (("bos", ()), ("dogru-not", (_not_bulgu(),)),
                           ("yanlis-eleme", (_eleme_bulgu(),)))
_ELEME_SECENEKLERI = (("bos", ()), ("dogru-eleme", (_eleme_bulgu(),)),
                      ("yanlis-not", (_not_bulgu(),)))

RAPOR_MATRISI = tuple(
    (f"{n_ad}/{e_ad}/{sonuc}", notlar, elemeler, sonuc)
    for n_ad, notlar in _KOLEKSIYON_SECENEKLERI
    for e_ad, elemeler in _ELEME_SECENEKLERI
    for sonuc in bd.SONUCLAR
)


def _rapor_yasal(notlar, elemeler, sonuc) -> bool:
    """Sözleşme, testin KENDİ dilinde: koleksiyonlar seviyeye göre ayrışır ve
    `sonuc` onlardan TÜRER. Modülün kendi ihlal fonksiyonuna bakmaz — bakarsa
    kapıyı kendisiyle karşılaştırmış olurdu."""
    if any(b.seviye != bd.SEVIYE_NOT for b in notlar):
        return False
    if any(b.seviye != bd.SEVIYE_ELEME for b in elemeler):
        return False
    return sonuc == bd.sonuc_belirle(notlar, elemeler)


@pytest.mark.parametrize(
    "notlar,elemeler,sonuc",
    [m[1:] for m in RAPOR_MATRISI],
    ids=[m[0] for m in RAPOR_MATRISI],
)
def test_rapor_kendi_bulgulariyla_celisemez(notlar, elemeler, sonuc) -> None:
    """Rapor kendi hakkında YALAN söyleyemez — üretilmiş 27'lik matris."""
    if _rapor_yasal(notlar, elemeler, sonuc):
        rapor = bd.DoctorReport(
            sonuc=sonuc, notlar=notlar, elemeler=elemeler, kaynak_adi="K"
        )
        assert rapor.sonuc == sonuc
    else:
        with pytest.raises(ValueError):
            bd.DoctorReport(
                sonuc=sonuc, notlar=notlar, elemeler=elemeler, kaynak_adi="K"
            )


def test_rapor_matrisi_iki_kollu_ve_mutasyona_duyarli() -> None:
    """Boş-küme kolu + mutasyon kolu: matris gerçekten bir kapı ölçüyor mu?"""
    assert len(RAPOR_MATRISI) == 27, "matris kavramdan üretilmedi"
    yasal = [m for m in RAPOR_MATRISI if _rapor_yasal(*m[1:])]
    yasadisi = [m for m in RAPOR_MATRISI if not _rapor_yasal(*m[1:])]
    assert yasal, "matriste tek bir YASAL üçlü yok — kapı hep kırmızı ölçülür"
    assert yasadisi, "matriste tek bir YASADIŞI üçlü yok — matris sessizce yeşil"

    # Mutasyon kolu: kapıyı SÖK (ihlal fonksiyonunu boş dönene çevir) →
    # yasadışı üçlü kurulabilir hâle gelmeli. Gelmiyorsa kapı burada değildir
    # ve matris başka bir şeyi ölçüyordur.
    _, notlar, elemeler, sonuc = yasadisi[0]
    with mock.patch.object(bd, "_rapor_ihlalleri", lambda *a, **k: []):
        bd.DoctorReport(
            sonuc=sonuc, notlar=notlar, elemeler=elemeler, kaynak_adi="K"
        )


@pytest.mark.parametrize("ad", ("", "   ", "\t", "\n"))
def test_kimliksiz_rapor_kurulamaz(ad: str) -> None:
    """(a) ayağı: kimlik YETKİLİDİR — adsız rapor kurulamaz, üretilemez."""
    with pytest.raises(ValueError):
        bd.DoctorReport(
            sonuc=bd.SONUC_GECTI, notlar=(), elemeler=(), kaynak_adi=ad
        )
    with pytest.raises(ValueError):
        bd.run(kaynak(), source_name=ad)


def test_kaynak_adi_varsayilansizdir() -> None:
    """SAPMA (bilinçli): `kaynak_adi` VARSAYILANSIZDIR.

    Plan 950 `DoctorReport(sonuc, notlar, elemeler)` yazımını verir; ilk üç alanın
    adı ve SIRASI korunur, ama dördüncü alan varsayılanını KAYBEDER. Gerekçe
    ölçüldü: varsayılan `""` iken `gate_round` adsız iki raporu iki AYRI kaynak
    sayıyordu (fail-open). Alanı `gate_round`'da reddetmek daha zayıf kapatmadır
    — bozuk rapor yine kurulabilir ve Task 9 paketleyicisine akabilirdi.
    """
    with pytest.raises(TypeError):
        bd.DoctorReport(bd.SONUC_GECTI, (), ())  # type: ignore[call-arg]


KIMLIK_MATRISI = (
    ("ayni-kaynak-iki-kez", ("KAYNAK-1", "KAYNAK-1"), 1, True),
    ("iki-ayri-kaynak", ("KAYNAK-1", "KAYNAK-2"), 2, False),
    ("uc-rapor-iki-kimlik", ("A", "A", "B"), 2, False),
    ("uc-rapor-uc-kimlik", ("A", "B", "C"), 3, False),
    ("tek-kaynak", ("A",), 1, True),
    ("hic-kaynak", (), 0, True),
)


@pytest.mark.parametrize(
    "adlar,beklenen,dur",
    [m[1:] for m in KIMLIK_MATRISI],
    ids=[m[0] for m in KIMLIK_MATRISI],
)
def test_gate_round_kaynagi_kimlige_gore_sayar(
    adlar: tuple[str, ...], beklenen: int, dur: bool
) -> None:
    """K-127 iki BAĞIMSIZ kaynak ister: aynı kaynağın iki raporu bir sayılır.

    Raporların İÇERİĞİ bilerek FARKLIDIR (`cta` düğmesi): kimlik artık ada VE
    içerik özetine göre denkleşir, aynı metin iki adla verilseydi bu matris ad
    ekseni yerine içerik eksenini ölçerdi (bkz. TAKMA_AD_MATRISI).
    """
    gate = bd.gate_round(
        [_rapor(_ad=ad, cta=5 + i) for i, ad in enumerate(adlar)]
    )
    assert gate.gecerli_kaynak_sayisi == beklenen
    assert gate.dur is dur


def test_ayni_kimlikte_eleme_kimligi_gecersiz_kilar() -> None:
    """Fail-closed: bir kimliğin RAPORLARINDAN biri elendiyse kimlik elenmiştir."""
    gate = bd.gate_round(
        [_rapor(_ad="A", cta=5), _sahte_elenmis("A"), _rapor(_ad="B", cta=6)]
    )
    assert gate.gecerli_kaynak_sayisi == 1
    assert gate.elenen_kaynak_sayisi == 1
    assert gate.dur is True


def _gecerli_gate_argumanlari() -> dict:
    # İçerik AYRI: aynı metin iki adla verilseydi kimlik denkliği onları TEK
    # kaynağa indirir ve türev alanları ölçen matris yanlış tabanla koşardı.
    raporlar = (_rapor(_ad="A", cta=5), _rapor(_ad="B", cta=6), _sahte_elenmis("C"))
    return dict(
        dur=False,
        gecerli_kaynak_sayisi=2,
        elenen_kaynak_sayisi=1,
        taban=bd.KAYNAK_TABANI,
        bildirim="",
        raporlar=raporlar,
    )


TUREV_BOZMALARI = (
    ("gecerli_kaynak_sayisi", 99),
    ("gecerli_kaynak_sayisi", 0),
    ("elenen_kaynak_sayisi", 0),
    ("elenen_kaynak_sayisi", 7),
    ("dur", True),
    ("taban", 5),
)


@pytest.mark.parametrize(
    "alan,deger", TUREV_BOZMALARI, ids=[f"{a}={d}" for a, d in TUREV_BOZMALARI]
)
def test_roundgate_turev_alanlari_ham_veriyle_celisemez(alan: str, deger) -> None:
    """(c) ayağı: `gecerli`/`elenen`/`dur` `raporlar`'ın FONKSİYONUDUR."""
    argumanlar = _gecerli_gate_argumanlari()
    argumanlar[alan] = deger
    with pytest.raises(ValueError):
        bd.RoundGate(**argumanlar)


def test_roundgate_dogru_turevlerle_kurulur() -> None:
    """Pozitif kontrol: tutarlı türevler REDDEDİLMEZ (kapı fazla dar değil)."""
    gate = bd.RoundGate(**_gecerli_gate_argumanlari())
    assert gate.dur is False
    assert gate.gecerli_kaynak_sayisi == 2


def test_duran_kapi_bildirimsiz_kurulamaz() -> None:
    """`dur=True` bildirimsiz olamaz — durdurma yöneticiye İLETİLİR."""
    with pytest.raises(ValueError):
        bd.RoundGate(
            dur=True,
            gecerli_kaynak_sayisi=1,
            elenen_kaynak_sayisi=0,
            taban=bd.KAYNAK_TABANI,
            bildirim="",
            raporlar=(_rapor(_ad="A"),),
        )


def test_gate_ihlal_matrisi_iki_kollu_ve_mutasyona_duyarli() -> None:
    """Boş-küme + mutasyon kolu — `RoundGate` kapısı için."""
    assert TUREV_BOZMALARI, "türev bozma matrisi BOŞ — kapı ölçülmüyor"
    argumanlar = _gecerli_gate_argumanlari()
    assert bd._gate_ihlalleri(**argumanlar) == [], "pozitif kontrol kırmızı"
    argumanlar["gecerli_kaynak_sayisi"] = 99
    assert bd._gate_ihlalleri(**argumanlar), "bozuk türev yeşil geçti"

    with mock.patch.object(bd, "_gate_ihlalleri", lambda **k: []):
        bd.RoundGate(**argumanlar)  # kapı sökülünce kurulabilmeli


# ─── H2: biçimsel olarak geçersiz belge — tekrar · sıra · boşluk · tablo şekli ─
#
# Bu bölümün bozuk kurguları YUKARIDAKİ `kaynak()` üretecinden TÜRETİLMEZ.
# Üreteç uygulamanın kendi şekline göre yazılmıştır ve bu dört biçim tam da o
# yüzden görünmüyordu. Buradaki matrisler SÖZLEŞMENİN KENDİ listelerinden
# üretilir — `BOLUM_HARFLERI` (beş bölüm, sabit sıra), `TEMEL_ALANLAR` (8 alan,
# SIRAYLA) ve gerekçe tablosunun dört sütunu; üçü de pinlenmiş `_SABLON.md`'den
# doğrulanır. Temiz belge yalnız CERRAHİ TABAN'dır: matris ona sözleşmeden
# türetilmiş yapısal bozmalar uygular.

_BOLUM_BASLIK_RE = re.compile(r"^##\s+Bölüm\s+([A-E])\b")
_ALAN_BASLIK_RE = re.compile(r"^###\s+([a-z_]+)\s*$")


def _bolum_bloklari(metin: str) -> list[tuple[str | None, str]]:
    """Belgeyi `## Bölüm X` başlıklarına göre bloklara böler (önsöz = None)."""
    parcalar: list[tuple[str | None, str]] = []
    mevcut: list[str] = []
    harf: str | None = None
    for satir in metin.splitlines(keepends=True):
        eslesme = _BOLUM_BASLIK_RE.match(satir)
        if eslesme:
            parcalar.append((harf, "".join(mevcut)))
            mevcut, harf = [satir], eslesme.group(1)
        else:
            mevcut.append(satir)
    parcalar.append((harf, "".join(mevcut)))
    return parcalar


def _birlestir(parcalar) -> str:
    return "".join(blok for _, blok in parcalar)


def _bolum_degistir(metin: str, harf: str, donusum) -> str:
    return _birlestir(
        [(h, donusum(b) if h == harf else b) for h, b in _bolum_bloklari(metin)]
    )


def bolum_bosalt(metin: str, harf: str) -> str:
    return _bolum_degistir(metin, harf, lambda b: b.splitlines(True)[0] + "\n")


def bolum_cogalt(metin: str, harf: str) -> str:
    yeni: list[tuple[str | None, str]] = []
    for h, blok in _bolum_bloklari(metin):
        yeni.append((h, blok))
        if h == harf:
            yeni.append((h, blok))
    return _birlestir(yeni)


def bolum_sirasini_boz(metin: str, sol: str, sag: str) -> str:
    parcalar = _bolum_bloklari(metin)
    yerler = {h: i for i, (h, _) in enumerate(parcalar)}
    i, j = yerler[sol], yerler[sag]
    parcalar[i], parcalar[j] = parcalar[j], parcalar[i]
    return _birlestir(parcalar)


def _alan_bloklari(a_blogu: str) -> list[tuple[str | None, str]]:
    parcalar: list[tuple[str | None, str]] = []
    mevcut: list[str] = []
    ad: str | None = None
    for satir in a_blogu.splitlines(keepends=True):
        eslesme = _ALAN_BASLIK_RE.match(satir)
        if eslesme:
            parcalar.append((ad, "".join(mevcut)))
            mevcut, ad = [satir], eslesme.group(1)
        else:
            mevcut.append(satir)
    parcalar.append((ad, "".join(mevcut)))
    return parcalar


def alan_cogalt(metin: str, ad: str) -> str:
    def donusum(blok: str) -> str:
        yeni: list[tuple[str | None, str]] = []
        for a, parca in _alan_bloklari(blok):
            yeni.append((a, parca))
            if a == ad:
                yeni.append((a, parca))
        return _birlestir(yeni)

    return _bolum_degistir(metin, "A", donusum)


def alan_sirasini_boz(metin: str, sol: str, sag: str) -> str:
    def donusum(blok: str) -> str:
        parcalar = _alan_bloklari(blok)
        yerler = {a: i for i, (a, _) in enumerate(parcalar)}
        i, j = yerler[sol], yerler[sag]
        parcalar[i], parcalar[j] = parcalar[j], parcalar[i]
        return _birlestir(parcalar)

    return _bolum_degistir(metin, "A", donusum)


def tablo_sutunlarini_boz(metin: str, sutun: int) -> str:
    """Tablonun her satırını `sutun` hücreye indirger/genişletir.

    Tür etiketi sütunu KORUNUR — aksi hâlde `tur-etiketi` ailesi ateşler ve
    tablo ŞEKLİNİN görünüp görünmediğini ölçemeyiz (kontrolörün probu tam da
    bu yüzden `gecti / 0 not` vermişti).

    KAPSAM BÖLÜM B'DİR. 2026-09-07'ye kadar bütün belgeye uygulanıyordu ve
    sorun yoktu, çünkü tablo yalnız Bölüm B'de vardı; sözleşme Bölüm C'yi de
    sabit sütunlu tabloya çevirince aynı prob YANLIŞLIKLA Bölüm C'yi de
    bozuyor ve iki farklı ailenin notunu birbirine karıştırıyordu (ölçüldü:
    `_tablo_sekli_ihlalleri` sökülünce `sütun` izi Bölüm C'nin notundan
    geliyordu). Prob NEYİ ölçtüğünü bilmeli — bu, ölçüm kirlenmesidir.
    """

    def donusum(blok: str) -> str:
        cikti: list[str] = []
        for satir in blok.splitlines(keepends=True):
            if not satir.lstrip().startswith("|"):
                cikti.append(satir)
                continue
            hucreler = [h.strip() for h in satir.strip().strip("|").split("|")]
            tur = hucreler[2] if len(hucreler) > 2 else hucreler[0]
            yeni = ([tur] + [h for i, h in enumerate(hucreler) if i != 2])[:sutun]
            while len(yeni) < sutun:
                yeni.append(yeni[-1])
            cikti.append("| " + " | ".join(yeni) + " |\n")
        return "".join(cikti)

    return _bolum_degistir(metin, "B", donusum)


def tabloyu_donemlerden_sonraya_tasi(metin: str) -> str:
    def donusum(blok: str) -> str:
        satirlar = blok.splitlines(True)
        tablo = [s for s in satirlar if s.lstrip().startswith("|")]
        kalan = [s for s in satirlar if not s.lstrip().startswith("|")]
        return "".join(kalan + tablo)

    return _bolum_degistir(metin, "B", donusum)


def c_eslemesini_kaldir(metin: str) -> str:
    """Bölüm C dolu kalır ama tek bir eşleme satırı taşımaz (düz paragraf)."""

    def donusum(blok: str) -> str:
        satirlar = blok.splitlines(True)
        return satirlar[0] + "\nKaynaklar oturum icinde toplandi ve degerlendirildi.\n"

    return _bolum_degistir(metin, "C", donusum)


def _sozlesme_tablo_sutunlari() -> tuple[str, ...]:
    """Dört sütun UYDURULMAZ: pinlenmiş sözleşmenin BAŞLIK SATIRINDAN okunur.

    2026-09-07'ye kadar sütunlar sözleşmenin bir DÜZYAZI cümlesinden
    (`(dönem + karar + tür etiketi + gerekçe)`) ayrıştırılıyordu. Sözleşme o
    turda birebir başlık satırını DAYATTI; türetme de oraya taşındı —
    düzyazıyı ayrıştırmak yerine kapının beklediği satırın KENDİSİ okunuyor.
    """
    metin = _pinli_sablon()
    blok = re.search(
        r"tek tablo, aynen şu\s*\n\s*başlık satırıyla:\s*\n+\|(.+?)\|\s*\n\s*\|-",
        metin,
        re.S,
    )
    assert blok is not None, "sözleşmede gerekçe tablosu başlık satırı bulunamadı"
    return tuple(parca.strip() for parca in blok.group(1).split("|"))


def test_gerekce_tablosu_sutunlari_pinlenmis_sablondan_okunur() -> None:
    assert _sozlesme_tablo_sutunlari() == bd.GEREKCE_TABLOSU_SUTUNLARI
    assert len(bd.GEREKCE_TABLOSU_SUTUNLARI) == 4


# ─── Bölüm C sabitleri: DÖRDÜ de pinlenmiş sözleşmeden okunur ───────────────
#
# 4. ayak sözleşmeye DÖRT bağlayıcı değer yazdı (başlık satırı · `iddia` kelime
# sınırı · `tarih-yok` yazımı · `tek kaynak` kapalı kümesi). Hiçbiri modüle
# ELLE yazılmış bir sabit olarak kabul edilmez: sözleşme değişirse bu testler
# kırılır ve kapı sözleşmeyle birlikte güncellenmek ZORUNDA kalır.


def _sozlesme_c_sutunlari() -> tuple[str, ...]:
    metin = _pinli_sablon()
    blok = re.search(
        r"SABİT SÜTUNLU\s*\nTABLO olarak yaz, aynen şu başlık satırıyla:"
        r"\s*\n+\|(.+?)\|\s*\n\s*\|-",
        metin,
        re.S,
    )
    assert blok is not None, "sözleşmede Bölüm C başlık satırı bulunamadı"
    return tuple(parca.strip() for parca in blok.group(1).split("|"))


def test_bolum_c_sabitleri_pinlenmis_sablondan_okunur() -> None:
    metin = _pinli_sablon()
    assert _sozlesme_c_sutunlari() == bd.C_TABLOSU_SUTUNLARI
    assert len(bd.C_TABLOSU_SUTUNLARI) == 6

    sinir = re.search(r"`iddia` hücresi EN FAZLA (\d+) KELİME", metin)
    assert sinir is not None, "sözleşmede `iddia` kelime sınırı bulunamadı"
    assert int(sinir.group(1)) == bd.C_IDDIA_KELIME_UST_SINIRI

    tarih = re.search(r"aynen `([\w-]+)` yaz", metin)
    assert tarih is not None and tarih.group(1) == bd.C_TARIH_YOK

    tek = re.search(r"`tek kaynak` hücresi `(\w+)` ya da `([\wıİğĞşŞçÇöÖüÜ]+)`", metin)
    assert tek is not None and tek.groups() == bd.C_TEK_KAYNAK_DEGERLERI


TEMIZ = kaynak()


def _notlari(metin: str) -> str:
    rapor = bd.run(metin, source_name="P")
    assert rapor.elemeler == (), "İlke 9: bu tur ELEME üretmemeli"
    return " | ".join(b.mesaj for b in rapor.notlar)


# ── Matrisler: hepsi sözleşme listelerinden ÜRETİLİR ────────────────────────

BOLUM_TEKRAR_MATRISI = tuple(
    (harf, bolum_cogalt(TEMIZ, harf), f"Bölüm {harf} birden çok kez")
    for harf in bd.BOLUM_HARFLERI
)
BOLUM_BOSLUK_MATRISI = tuple(
    (harf, bolum_bosalt(TEMIZ, harf), f"Bölüm {harf} boş")
    for harf in bd.BOLUM_HARFLERI
)
BOLUM_SIRA_MATRISI = tuple(
    (
        f"{sol}<->{sag}",
        bolum_sirasini_boz(TEMIZ, sol, sag),
        "Bölüm sırası sözleşmenin sırası değil",
    )
    for sol, sag in zip(bd.BOLUM_HARFLERI, bd.BOLUM_HARFLERI[1:])
)
ALAN_TEKRAR_MATRISI = tuple(
    (ad, alan_cogalt(TEMIZ, ad), f"`{ad}` alan başlığı birden çok kez")
    for ad in bd.TEMEL_ALANLAR
)
ALAN_SIRA_MATRISI = tuple(
    (
        f"{sol}<->{sag}",
        alan_sirasini_boz(TEMIZ, sol, sag),
        "Bölüm A alan sırası sözleşmenin sırası değil",
    )
    for sol, sag in zip(bd.TEMEL_ALANLAR, bd.TEMEL_ALANLAR[1:])
)
TABLO_SEKIL_MATRISI = tuple(
    (f"{n}-sutun", tablo_sutunlarini_boz(TEMIZ, n), "sütun")
    for n in (1, 2, 3, 5, 6)
)
TEKIL_BOZMALAR = (
    (
        "tablo-donemlerden-sonra",
        tabloyu_donemlerden_sonraya_tasi(TEMIZ),
        "dönem başlıklarından SONRA",
    ),
    ("c-eslemesiz", c_eslemesini_kaldir(TEMIZ), "başlık satırını taşımıyor"),
)

BICIM_MATRISI = (
    BOLUM_TEKRAR_MATRISI
    + BOLUM_BOSLUK_MATRISI
    + BOLUM_SIRA_MATRISI
    + ALAN_TEKRAR_MATRISI
    + ALAN_SIRA_MATRISI
    + TABLO_SEKIL_MATRISI
    + TEKIL_BOZMALAR
)


@pytest.mark.parametrize(
    "metin,iz", [(m[1], m[2]) for m in BICIM_MATRISI], ids=[m[0] for m in BICIM_MATRISI]
)
def test_bicimsel_olarak_gecersiz_belge_gorunur(metin: str, iz: str) -> None:
    """Tekrar · sıra · boşluk · tablo şekli — dördü de kapıda GÖRÜNMELİ."""
    mesajlar = _notlari(metin)
    assert iz in mesajlar, f"{iz!r} bulunamadı; görülen: {mesajlar[:400]}"


def test_bicim_matrisi_bos_kume_ve_taban_kollari() -> None:
    """Boş-küme kolu: matris sözleşme listelerinden GERÇEKTEN üretilmiş mi?"""
    assert len(BOLUM_TEKRAR_MATRISI) == len(bd.BOLUM_HARFLERI) == 5
    assert len(BOLUM_BOSLUK_MATRISI) == 5
    assert len(BOLUM_SIRA_MATRISI) == 4
    assert len(ALAN_TEKRAR_MATRISI) == len(bd.TEMEL_ALANLAR) == 8
    assert len(ALAN_SIRA_MATRISI) == 7
    assert len(TABLO_SEKIL_MATRISI) == 5
    assert len(BICIM_MATRISI) == 36
    # Cerrahinin gerçekten metni DEĞİŞTİRDİĞİ ölçülür: değiştirmeseydi matris
    # temiz belgeyi 31 kez ölçer ve hiçbir şey kanıtlamazdı.
    for ad, metin, _ in BICIM_MATRISI:
        assert metin != TEMIZ, f"{ad}: cerrahi metni değiştirmedi"


def test_bicim_kapisi_mutasyona_duyarli() -> None:
    """Mutasyon kolu: yapı/tablo kapılarını sök → matris KIRMIZI düşmeli."""
    with mock.patch.object(bd, "_bolum_yapisi_ihlalleri", lambda belge: []):
        for _, metin, iz in (
            BOLUM_TEKRAR_MATRISI + BOLUM_BOSLUK_MATRISI + BOLUM_SIRA_MATRISI
            + ALAN_TEKRAR_MATRISI + ALAN_SIRA_MATRISI
        ):
            assert iz not in _notlari(metin), f"{iz!r} kapı sökülünce de görünüyor"
    with mock.patch.object(bd, "_tablo_sekli_ihlalleri", lambda belge: []):
        for _, metin, iz in TABLO_SEKIL_MATRISI:
            assert iz not in _notlari(metin)


def test_temiz_kaynak_yeni_kapilardan_sonra_da_notsuz() -> None:
    """Pozitif kontrol (yanlış-pozitif kapanı): temiz kaynak hâlâ `gecti`, 0 not."""
    rapor = bd.run(TEMIZ, source_name="P")
    assert rapor.notlar == (), " | ".join(b.mesaj for b in rapor.notlar)
    assert rapor.sonuc == bd.SONUC_GECTI
    # K-120 dalı da yanlış-pozitif üretmemeli.
    resmi = bd.run(kaynak(anma_donemi="resmi"), source_name="P")
    assert resmi.notlar == (), " | ".join(b.mesaj for b in resmi.notlar)
    assert resmi.sonuc == bd.SONUC_GECTI


# ─── M1: dil kuralının kapsam sınırı RAPORDA görünür ────────────────────────


def test_kapsam_sinirlari_checks_ten_turer_ve_belgeden_bagimsizdir() -> None:
    """İlke 9(4): ölçülmeyen yön 'doğrulanmadı' etiketiyle SUNULUR."""
    beklenen = tuple(s for c in bd.CHECKS for s in c.kapsam_sinirlari)
    assert beklenen, "hiçbir kontrol kapsam sınırı beyan etmiyor"
    assert bd.run(TEMIZ, source_name="P").kapsam_sinirlari == beklenen
    assert bd.run("", source_name="P").kapsam_sinirlari == beklenen


def test_dil_kurali_ters_yonu_dogrulanmadigini_raporda_soyler() -> None:
    """Docstring'de saklı kalmak SUNUM DEĞİLDİR — rapor okuyucusu görmeli."""
    rapor = bd.run(TEMIZ, source_name="P")
    birlesik = " ".join(rapor.kapsam_sinirlari)
    assert "dil-kurali" in birlesik
    assert "DOĞRULANMADI" in birlesik.upper()
    # ...ve bildirim bir BULGU değildir: temiz kaynağın sonucunu bozmaz.
    assert rapor.notlar == ()
    assert rapor.sonuc == bd.SONUC_GECTI
    # Kapsam sınırı ailenin `aciklama` alanına da yansır.
    dil = next(c for c in bd.CHECKS if c.aile == "dil-kurali")
    assert "DOĞRULANMADI" in " ".join(dil.kapsam_sinirlari).upper()
    assert "ters yön" in dil.aciklama or "ölçülmez" in dil.aciklama


def test_kapsam_sinirlari_donmus_ve_tip_zorlar() -> None:
    """Beyan demeti DONMUŞ ve METİN taşır — tip kapısı türev alanda da durur.

    Alan artık `init=False`'tur (F3): çağıran onu yazamaz. Tip kapısı yine de
    ölçülür, çünkü beyan `CHECKS`'ten TÜRER ve bozuk bir `Check` sessizce
    metin olmayan bir beyan sızdırmamalıdır.
    """
    rapor = bd.DoctorReport(
        sonuc=bd.SONUC_GECTI, notlar=(), elemeler=(), kaynak_adi="K"
    )
    assert isinstance(rapor.kapsam_sinirlari, tuple)
    assert all(isinstance(sinir, str) for sinir in rapor.kapsam_sinirlari)
    with mock.patch.object(bd, "_kapsam_beyani", lambda: (7,)):
        with pytest.raises(TypeError):
            bd.DoctorReport(
                sonuc=bd.SONUC_GECTI, notlar=(), elemeler=(), kaynak_adi="K"
            )


# ─── H3: KİMLİK kanonik bir kuraldan TÜRER (takma-ad denkliği) ─────────────
#
# Sınıf (tur 2, F1): *"bir sayım/benzersizlik kararına giren kimlik, çağıranın
# serbest metnidir."* Tur 1 kimliği ZORUNLU yaptı ama NORMALLEŞTİRMEDİ; takma
# adlar tek kaynağı iki bağımsız kaynak gibi gösteriyordu. Kapatma tek tek
# ekseni yamalamak DEĞİL, kimliği üreten TEK kanonik kuraldır: ad ekseninde
# `kanonik_kaynak_kimligi`, içerik ekseninde `run`'ın ürettiği kanonik özet.
# İkisi birlikte raporlar üstünde bir DENKLİK bağıntısı kurar.
#
# **Matris KAVRAMDAN türer, bulunan örneklerden değil.** Takma-ad denkliğinin
# eksenleri belgelenmiş bir addır ve her biri BAĞIMSIZ açılıp kapanır:
# kenar/iç boşluk · harf durumu · unicode normalizasyon biçimi · dosya uzantısı
# · yol bileşenleri. Bileşim uzayı 2**5 = 32'dir ve buna İÇERİK ekseni (aynı
# içerik / farklı içerik) ÇARPILIR → 64 hücre. Artı gerçekten FARKLI ad, iki
# içerik hâliyle → 66. Aşağıdaki liste elle seçilmemiştir, bu çarpımdan
# ÜRETİLİR.

AD_BOZMA_EKSENLERI = (
    ("harf-durumu", lambda ad: ad.swapcase()),
    ("unicode-nfd", lambda ad: unicodedata.normalize("NFD", ad)),
    ("dosya-uzantisi", lambda ad: f"{ad}.md"),
    ("yol-bileseni", lambda ad: f"arsiv/gecici/../{ad}"),
    ("kenar-bosluk", lambda ad: f"  {ad}\t"),
)
TABAN_AD = "KAYNAK-Şubat-1"
BASKA_AD = "KAYNAK-Mart-2"
ICERIK_EKSENI = (("ayni-icerik", True), ("farkli-icerik", False))


def _bozulmus_ad(taban: str, secim: tuple[bool, ...]) -> str:
    ad = taban
    for (_, donusum), acik in zip(AD_BOZMA_EKSENLERI, secim):
        if acik:
            ad = donusum(ad)
    return ad


_AD_BILESIMLERI = tuple(
    itertools.product((False, True), repeat=len(AD_BOZMA_EKSENLERI))
)

# Hücre: (kimlik, ad_a, ad_b, ayni_icerik, beklenen_gecerli, beklenen_dur)
TAKMA_AD_MATRISI = tuple(
    (
        (
            "+".join(
                eksen[0] for eksen, acik in zip(AD_BOZMA_EKSENLERI, secim) if acik
            )
            or "bozma-yok"
        )
        + f"/{icerik_adi}",
        TABAN_AD,
        _bozulmus_ad(TABAN_AD, secim),
        ayni,
        1,
        True,
    )
    for secim in _AD_BILESIMLERI
    for icerik_adi, ayni in ICERIK_EKSENI
) + tuple(
    (
        f"gercekten-farkli-ad/{icerik_adi}",
        TABAN_AD,
        BASKA_AD,
        ayni,
        1 if ayni else 2,
        ayni,
    )
    for icerik_adi, ayni in ICERIK_EKSENI
)

_FARKLI_ICERIK = kaynak(cta=6)


def _kimlik_gate(ad_a: str, ad_b: str, ayni_icerik: bool):
    a = bd.run(TEMIZ, source_name=ad_a)
    b = bd.run(TEMIZ if ayni_icerik else _FARKLI_ICERIK, source_name=ad_b)
    return bd.gate_round([a, b])


@pytest.mark.parametrize(
    "ad_a,ad_b,ayni,gecerli,dur",
    [h[1:] for h in TAKMA_AD_MATRISI],
    ids=[h[0] for h in TAKMA_AD_MATRISI],
)
def test_takma_ad_matrisi_kimligi_kanonik_sayar(
    ad_a: str, ad_b: str, ayni: bool, gecerli: int, dur: bool
) -> None:
    """Takma adlar TEK kaynaktır; gerçekten farklı iki kaynak İKİ kaynaktır."""
    gate = _kimlik_gate(ad_a, ad_b, ayni)
    assert gate.gecerli_kaynak_sayisi == gecerli
    assert gate.dur is dur


def test_takma_ad_matrisi_bos_kume_ve_taban_kollari() -> None:
    """Boş-küme kolu: matris gerçekten ÇARPIMDAN üretilmiş mi?"""
    eksen = len(AD_BOZMA_EKSENLERI)
    assert eksen == 5, "eksen kümesi daraldı — matris sessizce küçülür"
    assert len(_AD_BILESIMLERI) == 2**eksen == 32
    assert len(TAKMA_AD_MATRISI) == 2**eksen * len(ICERIK_EKSENI) + 2 == 66
    # Cerrahi gerçekten uygulanmış mı: boş bileşim DIŞINDA her ad farklı olmalı.
    bozulmus = {
        h[0]: h[2] for h in TAKMA_AD_MATRISI if not h[0].startswith("bozma-yok")
    }
    for kimlik, ad in bozulmus.items():
        if kimlik.startswith("gercekten-farkli-ad"):
            continue
        assert ad != TABAN_AD, f"{kimlik}: ad bozulmamış"
    # ...ve hepsi AYNI kanonik kimliğe düşmeli (kural TEK yerdedir).
    kanonik = {
        bd.kanonik_kaynak_kimligi(h[2])
        for h in TAKMA_AD_MATRISI
        if not h[0].startswith("gercekten-farkli-ad")
    }
    assert kanonik == {bd.kanonik_kaynak_kimligi(TABAN_AD)}


def test_takma_ad_kapisi_mutasyona_duyarli() -> None:
    """Mutasyon kolu: iki kanonik kuralı AYRI AYRI sök → matris KIRMIZI düşmeli."""
    # (a) Ad kuralını sök: farklı-içerikli takma ad hücreleri fail-open olmalı.
    ad_hucreleri = [
        h
        for h in TAKMA_AD_MATRISI
        if not h[0].startswith(("bozma-yok", "gercekten-farkli-ad"))
        and h[3] is False
    ]
    assert ad_hucreleri, "ad ekseni hücresi YOK — mutasyon kolu boş ölçüyor"
    with mock.patch.object(bd, "kanonik_kaynak_kimligi", lambda ad: ad):
        for kimlik, ad_a, ad_b, ayni, _, _ in ad_hucreleri:
            gate = _kimlik_gate(ad_a, ad_b, ayni)
            assert gate.gecerli_kaynak_sayisi == 2, f"{kimlik}: kapı sökülmedi"

    # (b) İçerik özeti kuralını sök: aynı içerik + farklı ad fail-open olmalı.
    with mock.patch.object(
        bd, "_kimlik_anahtarlari", lambda r: (("ad", r.kanonik_kimlik),)
    ):
        gate = _kimlik_gate(TABAN_AD, BASKA_AD, True)
        assert gate.gecerli_kaynak_sayisi == 2


def test_celiskili_takma_ad_cifti_fail_closed() -> None:
    """Bir takma adla `gecti`, öbürüyle `elendi` → KİMLİK elenmiştir."""
    gate = bd.gate_round(
        [bd.run(TEMIZ, source_name="KAYNAK-1"), _sahte_elenmis("  kaynak-1.md ")]
    )
    assert gate.gecerli_kaynak_sayisi == 0
    assert gate.elenen_kaynak_sayisi == 1
    assert gate.dur is True


@pytest.mark.parametrize("ad", ("/", "//", " / / ", "./", "../..", "  "))
def test_kanonik_kimligi_bos_dusen_ad_reddedilir(ad: str) -> None:
    """Kimlik KANONİK biçimde de boş olamaz — fail-closed."""
    assert bd.kanonik_kaynak_kimligi(ad) == ""
    with pytest.raises(ValueError):
        bd.DoctorReport(
            sonuc=bd.SONUC_GECTI, notlar=(), elemeler=(), kaynak_adi=ad
        )


def test_icerik_ozeti_run_tarafindan_uretilir_ve_bicimi_zorlanir() -> None:
    """Özet çağıranın serbest metni DEĞİLDİR: `run` üretir, biçim fail-closed."""
    rapor = bd.run(TEMIZ, source_name="K")
    assert rapor.icerik_ozeti == identity.canonical_sha(TEMIZ)
    assert re.fullmatch(r"[0-9a-f]{64}", rapor.icerik_ozeti)
    # Aynı metin → aynı özet; farklı metin → farklı özet (deterministik).
    assert bd.run(TEMIZ, source_name="B").icerik_ozeti == rapor.icerik_ozeti
    assert bd.run(_FARKLI_ICERIK, source_name="B").icerik_ozeti != rapor.icerik_ozeti
    # Doğrudan kurulan rapor özetsizdir (dürüst boşluk) ama SERBEST METİN olamaz.
    assert _sahte_elenmis("X").icerik_ozeti == ""
    for bozuk in ("elbette-ozet", "ABC", "0" * 63, "g" * 64):
        with pytest.raises(ValueError):
            bd.DoctorReport(
                sonuc=bd.SONUC_GECTI,
                notlar=(),
                elemeler=(),
                kaynak_adi="K",
                icerik_ozeti=bozuk,
            )


# ─── H4: İÇ İÇE her düzey tekrarı ve sırayı KORUR ──────────────────────────
#
# Sınıf (tur 2, F2): *"iç içe bir koleksiyon sözlüğe konuyor, tekrar ve sıra
# kayboluyor; ve sayıya dayalı her eşik ESSİZ doğrulanmış varlık yerine ham
# sayıyı okuyor."* Tur 1 yalnız BÖLÜM ve ALAN düzeyini kurtardı; ölçüldü ki
# dönem kimliği tekrarı (`ayrıştırılan dönem=6, ESSİZ ad=5`), video havuzu
# bloğunun ikinci kez yazılması ve Bölüm C'nin ÜÇLÜ yapısını kaybetmiş çıplak
# bağlantı satırı üçü de `gecti / 0 not` veriyordu.
#
# **Matris KAVRAMDAN türer:** eksen 1 = belgenin KENDİ içerme modeli
# (`_SABLON.md` §5 ÇIKTI FORMATI + GÖREV A/B adımları), eksen 2 = bozulma
# biçimi (tekrar · sıra · boş). Dokuz düzey × üç biçim = 27 hücre. SIRA hücresi,
# sözleşmenin bir sıra DAYATMADIĞI açık kümelerde bilinçle boştur ve gerekçesi
# hücrenin yanında yazılıdır — sessizce atlanmaz.

# **Tur 3 DÜZELTMESİ (davranış DEĞİŞMEZ, gerekçe değişir).** Eski gerekçe
# "sözleşme bu düzeyde SIRA dayatmaz" diyordu ve YANLIŞTI: pinli sözleşme
# (`_SABLON.md` satır 73-75) her listede ÖNEM SIRASI dayatır. Hücreler yine boş
# kalır — ama doğru gerekçeyle: önem SEMANTİK bir yargıdır, mekanik kapı
# doğrulayamaz. Ölçümü `test_sozlesme_onem_sirasi_dayatir_ama_kapi_olcemez`'te.
_ACIK_KUME_GEREKCESI = (
    "sözleşme bu düzeyde ÖNEM SIRASI dayatır (_SABLON.md satır 73-75) ama önem "
    "SEMANTİK bir yargıdır; mekanik kapı DOĞRULAYAMAZ — uydurulmuş bir sıra "
    "kuralı gerçek çıktıyı gürültüye boğardı (İlke 9)"
)

_YUVA_BASLIKLARI = ("kanca", "cta", "gorsel_vurgu")


def _md_duzeyi(satir: str) -> int:
    govde = satir.lstrip()
    sayi = len(govde) - len(govde.lstrip("#"))
    return sayi if sayi and govde[sayi : sayi + 1] == " " else 0


def _md_blok(satirlar: list[str], baslik: str) -> tuple[int, int]:
    """`baslik` satırının açtığı markdown bloğunun [i, j) aralığı."""
    for i, satir in enumerate(satirlar):
        if satir.strip() == baslik:
            duzey = _md_duzeyi(satir)
            j = i + 1
            while j < len(satirlar) and not 0 < _md_duzeyi(satirlar[j]) <= duzey:
                j += 1
            return i, j
    raise AssertionError(f"başlık bulunamadı: {baslik!r}")


def blok_cogalt(metin: str, baslik: str) -> str:
    satirlar = metin.splitlines(True)
    i, j = _md_blok(satirlar, baslik)
    return "".join(satirlar[:j] + satirlar[i:j] + satirlar[j:])


def blok_bosalt(metin: str, baslik: str) -> str:
    satirlar = metin.splitlines(True)
    i, j = _md_blok(satirlar, baslik)
    return "".join(satirlar[: i + 1] + ["\n"] + satirlar[j:])


def blok_takasla(metin: str, sol: str, sag: str) -> str:
    satirlar = metin.splitlines(True)
    i1, j1 = _md_blok(satirlar, sol)
    i2, j2 = _md_blok(satirlar, sag)
    assert j1 <= i2, "takas için bloklar ayrık ve sıralı olmalı"
    return "".join(
        satirlar[:i1]
        + satirlar[i2:j2]
        + satirlar[j1:i2]
        + satirlar[i1:j1]
        + satirlar[j2:]
    )


def _madde_indeksi(satirlar: list[str], i: int, j: int) -> int:
    for k in range(i + 1, j):
        if satirlar[k].lstrip().startswith("- "):
            return k
    raise AssertionError("blokta madde yok")


def blok_maddesini_cogalt(metin: str, baslik: str) -> str:
    satirlar = metin.splitlines(True)
    k = _madde_indeksi(satirlar, *_md_blok(satirlar, baslik))
    return "".join(satirlar[: k + 1] + [satirlar[k]] + satirlar[k + 1 :])


def blok_maddesini_bosalt(metin: str, baslik: str) -> str:
    """İlk maddeyi serbest BOŞLUK ifadesine çevirir — sözleşme onu boş sayar."""
    satirlar = metin.splitlines(True)
    k = _madde_indeksi(satirlar, *_md_blok(satirlar, baslik))
    return "".join(satirlar[:k] + ["- yok\n"] + satirlar[k + 1 :])


def _donem_yuva_araligi(
    satirlar: list[str], i: int, j: int, yuva_adi: str
) -> tuple[int, int]:
    for k in range(i, j):
        if satirlar[k].strip() == yuva_adi:
            m = k + 1
            while m < j and satirlar[m].strip() not in _YUVA_BASLIKLARI:
                m += 1
            return k, m
    raise AssertionError(f"dönem yuvası bulunamadı: {yuva_adi!r}")


def _ilk_donem_yuvasi(metin: str, yuva_adi: str) -> tuple[list[str], int, int]:
    satirlar = metin.splitlines(True)
    i, j = _md_blok(satirlar, f"### {_DONEM_ADLARI[0]}")
    return (satirlar, *_donem_yuva_araligi(satirlar, i, j, yuva_adi))


def donem_yuvasini_cogalt(metin: str, yuva_adi: str) -> str:
    satirlar, k, m = _ilk_donem_yuvasi(metin, yuva_adi)
    return "".join(satirlar[:m] + satirlar[k:m] + satirlar[m:])


def donem_yuvasini_bosalt(metin: str, yuva_adi: str) -> str:
    satirlar, k, m = _ilk_donem_yuvasi(metin, yuva_adi)
    return "".join(satirlar[: k + 1] + satirlar[m:])


def donem_yuva_sirasini_boz(metin: str, sol: str, sag: str) -> str:
    satirlar = metin.splitlines(True)
    i, j = _md_blok(satirlar, f"### {_DONEM_ADLARI[0]}")
    k1, m1 = _donem_yuva_araligi(satirlar, i, j, sol)
    k2, m2 = _donem_yuva_araligi(satirlar, i, j, sag)
    assert m1 <= k2
    return "".join(
        satirlar[:k1]
        + satirlar[k2:m2]
        + satirlar[m1:k2]
        + satirlar[k1:m1]
        + satirlar[m2:]
    )


def donem_yuva_maddesini_cogalt(metin: str, yuva_adi: str) -> str:
    satirlar, k, m = _ilk_donem_yuvasi(metin, yuva_adi)
    p = _madde_indeksi(satirlar, k, m)
    return "".join(satirlar[: p + 1] + [satirlar[p]] + satirlar[p + 1 :])


def donem_yuva_maddesini_bosalt(metin: str, yuva_adi: str) -> str:
    satirlar, k, m = _ilk_donem_yuvasi(metin, yuva_adi)
    p = _madde_indeksi(satirlar, k, m)
    return "".join(satirlar[:p] + ["- yok\n"] + satirlar[p + 1 :])


def _c_veri_satir_indeksi(satirlar: list[str]) -> int:
    """Bölüm C tablosunun İLK VERİ satırı — ayıraçtan SONRAKİ ilk tablo satırı.

    Sözleşme 2026-09-07'de Bölüm C'yi sabit sütunlu tabloya çevirdi; madde
    işareti arayan eski yardımcı (`_madde_indeksi`) artık orada hiçbir şey
    bulamaz.
    """
    i, j = _md_blok(satirlar, "## Bölüm C — KAYNAKLAR")
    ayirac_gorundu = False
    for k in range(i + 1, j):
        govde = satirlar[k].strip()
        if not govde.startswith("|"):
            continue
        if set(govde) <= set("|-: "):
            ayirac_gorundu = True
            continue
        if ayirac_gorundu:
            return k
    raise AssertionError("Bölüm C veri satırı yok")


def _c_hucreleri_degistir(metin: str, sutun: int, deger: str) -> str:
    satirlar = metin.splitlines(True)
    k = _c_veri_satir_indeksi(satirlar)
    hucreler = [h.strip() for h in satirlar[k].strip().strip("|").split("|")]
    hucreler[sutun] = deger
    yeni = "| " + " | ".join(hucreler) + " |\n"
    return "".join(satirlar[:k] + [yeni] + satirlar[k + 1 :])


def c_satirini_cogalt(metin: str) -> str:
    satirlar = metin.splitlines(True)
    k = _c_veri_satir_indeksi(satirlar)
    return "".join(satirlar[: k + 1] + [satirlar[k]] + satirlar[k + 1 :])


def c_iddiayi_bosalt(metin: str) -> str:
    """Eşleme satırı VAR ama `iddia` hücresi BOŞ — kap dolu, hücre boş."""
    return _c_hucreleri_degistir(metin, bd.C_TABLOSU_SUTUNLARI.index("iddia"), "")


def c_veri_satirlarini_kaldir(metin: str) -> str:
    """Bölüm C'de sözleşmenin BAŞLIK satırı durur, veri satırı KALMAZ."""
    satirlar = metin.splitlines(True)
    i, j = _md_blok(satirlar, "## Bölüm C — KAYNAKLAR")
    k = _c_veri_satir_indeksi(satirlar)
    kalan = [s for s in satirlar[k:j] if not s.strip().startswith("|")]
    return "".join(satirlar[:k] + kalan + satirlar[j:])


def c_ilk_satiri_kaldir(metin: str) -> str:
    """Bölüm C tablosu duruyor ama BİR alan/dönem kapsam DIŞINDA kalıyor."""
    satirlar = metin.splitlines(True)
    k = _c_veri_satir_indeksi(satirlar)
    return "".join(satirlar[:k] + satirlar[k + 1 :])


def c_sutun_sayisini_boz(metin: str, sutun: int) -> str:
    """Bölüm C'nin İLK veri satırını `sutun` hücreye indirger/genişletir."""
    satirlar = metin.splitlines(True)
    k = _c_veri_satir_indeksi(satirlar)
    hucreler = [h.strip() for h in satirlar[k].strip().strip("|").split("|")]
    yeni = (hucreler * sutun)[:sutun]
    return "".join(
        satirlar[:k] + ["| " + " | ".join(yeni) + " |\n"] + satirlar[k + 1 :]
    )


def bolum_b_alakasiz_tablo(metin: str, donem_sirasi: int) -> str:
    """Bölüm B'de bir dönem bloğunun İÇİNE meşru, başlıklı 2 sütunlu tablo koyar."""
    satirlar = metin.splitlines(True)
    i, j = _md_blok(satirlar, f"### {_DONEM_ADLARI[donem_sirasi]}")
    ek = [
        "\n",
        "| olcut | deger |\n",
        "|---|---|\n",
        "| talep | yuksek |\n",
        "| rekabet | orta |\n",
        "\n",
    ]
    return "".join(satirlar[: j] + ek + satirlar[j:])


def gerekce_tablosunu_boz(metin: str) -> str:
    """GERÇEK gerekçe tablosunun tür etiketi sütununu siler (kontrol kolu).

    KAPSAM BÖLÜM B'DİR — `tablo_sutunlarini_boz` ile aynı gerekçe: sözleşme
    2026-09-07'de Bölüm C'yi de tabloya çevirdi ve belge geneline uygulanan
    prob iki ailenin notunu birbirine karıştırıyordu.
    """

    def donusum(blok: str) -> str:
        cikti = []
        for satir in blok.splitlines(True):
            if not satir.lstrip().startswith("|") or satir.lstrip().startswith("|-"):
                cikti.append(satir)
                continue
            hucreler = [h.strip() for h in satir.strip().strip("|").split("|")]
            cikti.append(
                "| " + " | ".join(h for i, h in enumerate(hucreler) if i != 2) + " |\n"
            )
        return "".join(cikti)

    return _bolum_degistir(metin, "B", donusum)


# Eksen 1 — belgenin İÇERME MODELİ. Sıra sütunu `None` ise küme AÇIKTIR ve o
# hücre bilinçle boştur (gerekçe: `_ACIK_KUME_GEREKCESI`).
IC_ICE_DUZEYLER = (
    (
        "bolum",
        lambda: bolum_cogalt(TEMIZ, "C"),
        lambda: bolum_sirasini_boz(TEMIZ, "A", "B"),
        lambda: bolum_bosalt(TEMIZ, "C"),
        ("birden çok kez", "sözleşmenin sırası değil", "boş"),
    ),
    (
        "bolum-a-alani",
        lambda: alan_cogalt(TEMIZ, "cta_kaliplari"),
        lambda: alan_sirasini_boz(TEMIZ, "kapsam", "ton_ve_dil"),
        lambda: blok_bosalt(TEMIZ, "### cta_kaliplari"),
        ("birden çok kez", "sözleşmenin sırası değil", "boş"),
    ),
    (
        "alan-maddesi",
        lambda: blok_maddesini_cogalt(TEMIZ, "### cta_kaliplari"),
        None,
        lambda: blok_maddesini_bosalt(TEMIZ, "### cta_kaliplari"),
        ("kez yazılmış", None, "alt sınırı"),
    ),
    (
        "video-havuzu",
        lambda: blok_cogalt(TEMIZ, "#### hareket"),
        lambda: blok_takasla(TEMIZ, "#### hareket", "#### sahne"),
        lambda: blok_bosalt(TEMIZ, "#### hareket"),
        ("kez yazılmış", "sözleşmenin sırası değil", "alt sınır"),
    ),
    (
        "video-havuzu-maddesi",
        lambda: blok_maddesini_cogalt(TEMIZ, "#### hareket"),
        None,
        lambda: blok_maddesini_bosalt(TEMIZ, "#### hareket"),
        ("kez yazılmış", None, "alt sınır"),
    ),
    (
        "donem",
        lambda: blok_cogalt(TEMIZ, f"### {_DONEM_ADLARI[0]}"),
        None,
        lambda: blok_bosalt(TEMIZ, f"### {_DONEM_ADLARI[0]}"),
        ("kez yazılmış", None, "alt sınır"),
    ),
    (
        "donem-yuvasi",
        lambda: donem_yuvasini_cogalt(TEMIZ, "kanca"),
        lambda: donem_yuva_sirasini_boz(TEMIZ, "kanca", "cta"),
        lambda: donem_yuvasini_bosalt(TEMIZ, "kanca"),
        ("birden çok kez", "sözleşmenin sırası değil", "boş"),
    ),
    (
        "donem-yuvasi-maddesi",
        lambda: donem_yuva_maddesini_cogalt(TEMIZ, "kanca"),
        None,
        lambda: donem_yuva_maddesini_bosalt(TEMIZ, "kanca"),
        ("kez yazılmış", None, "alt sınır"),
    ),
    (
        "bolum-c-eslemesi",
        lambda: c_satirini_cogalt(TEMIZ),
        None,
        lambda: c_iddiayi_bosalt(TEMIZ),
        ("kez yazılmış", None, "iddia"),
    ),
)

IC_ICE_MATRISI = tuple(
    (f"{duzey}/{biçim}", uretec(), iz)
    for duzey, tekrar, sira, bos, izler in IC_ICE_DUZEYLER
    for biçim, uretec, iz in zip(("tekrar", "sira", "bos"), (tekrar, sira, bos), izler)
    if uretec is not None
)
BOS_BIRAKILAN_HUCRELER = tuple(
    (f"{duzey}/sira", _ACIK_KUME_GEREKCESI)
    for duzey, _, sira, _, _ in IC_ICE_DUZEYLER
    if sira is None
)


@pytest.mark.parametrize(
    "metin,iz",
    [(h[1], h[2]) for h in IC_ICE_MATRISI],
    ids=[h[0] for h in IC_ICE_MATRISI],
)
def test_ic_ice_duzeyler_tekrari_ve_sirayi_kaybetmez(metin: str, iz: str) -> None:
    mesajlar = _notlari(metin)
    assert iz in mesajlar, f"{iz!r} bulunamadı; görülen: {mesajlar[:500]}"


def test_ic_ice_matrisi_bos_kume_ve_taban_kollari() -> None:
    """Boş-küme kolu: matris içerme modelinden ÜRETİLMİŞ mi, hücreler dolu mu?"""
    assert len(IC_ICE_DUZEYLER) == 9, "içerme modeli düzey kaybetti"
    assert len(IC_ICE_MATRISI) + len(BOS_BIRAKILAN_HUCRELER) == 9 * 3 == 27
    assert len(BOS_BIRAKILAN_HUCRELER) == 5
    assert {ad for ad, _ in BOS_BIRAKILAN_HUCRELER} == {
        "alan-maddesi/sira",
        "video-havuzu-maddesi/sira",
        "donem/sira",
        "donem-yuvasi-maddesi/sira",
        "bolum-c-eslemesi/sira",
    }
    for _, gerekce in BOS_BIRAKILAN_HUCRELER:
        assert gerekce == _ACIK_KUME_GEREKCESI
    for ad, metin, _ in IC_ICE_MATRISI:
        assert metin != TEMIZ, f"{ad}: cerrahi metni değiştirmedi"


def test_ic_ice_kapisi_mutasyona_duyarli() -> None:
    """Mutasyon kolu: dilbilgisi kapısını sök → tekrar/sıra hücreleri sussun."""
    yapisal = [
        h for h in IC_ICE_MATRISI if h[0].endswith(("/tekrar", "/sira"))
    ]
    assert len(yapisal) == 13
    with mock.patch.object(bd, "_bolum_yapisi_ihlalleri", lambda belge: []):
        for ad, metin, iz in yapisal:
            if ad.startswith("bolum-c-eslemesi"):
                continue
            assert iz not in _notlari(metin), f"{ad}: kapı sökülünce de görünüyor"


def test_adet_esikleri_essiz_varlik_sayar() -> None:
    """Sayıya dayalı HER eşik ESSİZ doğrulanmış varlığı sayar, ham satırı değil."""
    yuva = bd._Yuva(ad="cta_kaliplari", satirlar=["- ayni", "- ayni", "- yok", "- baska"])
    assert len(yuva.maddeler) == 4
    assert [m for m in yuva.essiz_maddeler] == ["ayni", "baska"]
    belge = bd._ayristir(blok_cogalt(TEMIZ, f"### {_DONEM_ADLARI[0]}"))
    assert len(belge.donemler) == 7, "ham dönem sayısı"
    assert bd._essiz_donem_sayisi(belge) == 6, "ESSİZ dönem kimliği"


def test_bolum_c_hucreleri_denetlenir_ama_temizde_yanlis_pozitif_uretmez() -> None:
    """Bölüm C sözleşmesi SABİT SÜTUNLU tablodur; hücreler tek tek denetlenir."""
    assert "iddia" in _notlari(c_iddiayi_bosalt(TEMIZ))
    assert _notlari(TEMIZ) == "", "temiz Bölüm C sütun kontrolünden geçmeli"


# ─── 4. AYAK: Bölüm C hücre sözleşmesi — ÜRETİLMİŞ matris ──────────────────
#
# Kapanış ELLE SEÇİLMİŞ örnekle değil ÜRETİLMİŞ matrisle kanıtlanır. Doluluk
# ekseni sözleşmenin SÜTUN LİSTESİNDEN türer (bulunan örnekten değil), yani
# sözleşmeye altıncı bir sütun eklenirse hücre KENDİLİĞİNDEN doğar.
#
# Üç eksen ayrıdır ve ayrı şeyler ölçer:
#   (a) DOLULUK — her sütun için o hücre boşaltılır.
#   (b) DEĞER   — kapalı küme · biçim · sınır taşıyan sütunlarda bozuk değer.
#   (c) ŞEKİL   — başlık satırı · veri satırı · sütun sayısı · KAPSAMA.
C_DOLULUK_MATRISI = tuple(
    (
        f"bos-hucre/{ad}",
        _c_hucreleri_degistir(TEMIZ, i, ""),
        f"`{ad}` hücresi BOŞ",
    )
    for i, ad in enumerate(bd.C_TABLOSU_SUTUNLARI)
)

_UZUN_IDDIA = " ".join(
    f"kelime{i}" for i in range(1, bd.C_IDDIA_KELIME_UST_SINIRI + 2)
)
C_DEGER_MATRISI = (
    (
        "alan-disi",
        _c_hucreleri_degistir(TEMIZ, 0, "bilinmeyen_alan"),
        "ne bir Bölüm A alan adı",
    ),
    ("iddia-uzun", _c_hucreleri_degistir(TEMIZ, 1, _UZUN_IDDIA), "kelime — sözleşme"),
    ("url-ciplak", _c_hucreleri_degistir(TEMIZ, 3, "ornek.example/x"), "TEK bir açılabilir"),
    (
        "url-http",
        _c_hucreleri_degistir(TEMIZ, 3, "http://ornek.example/x"),
        "`http://` bağlantı taşıyor",
    ),
    (
        "url-iki-adres",
        _c_hucreleri_degistir(TEMIZ, 3, "https://a.example/x https://b.example/y"),
        "TEK bir açılabilir",
    ),
    ("tarih-serbest", _c_hucreleri_degistir(TEMIZ, 4, "2025 bahari"), "`tarih` hücresi"),
    (
        "tek-kaynak-disi",
        _c_hucreleri_degistir(TEMIZ, 5, "belki"),
        "`tek kaynak` hücresi",
    ),
)

C_SEKIL_MATRISI = (
    ("basliksiz", c_eslemesini_kaldir(TEMIZ), "başlık satırını taşımıyor"),
    ("veri-satirsiz", c_veri_satirlarini_kaldir(TEMIZ), "BAŞLIK SATIRINDAN İBARET"),
    ("kapsam-eksik", c_ilk_satiri_kaldir(TEMIZ), "kaynak satırı taşımıyor"),
) + tuple(
    (f"sutun-{n}", c_sutun_sayisini_boz(TEMIZ, n), f"{n} sütunlu")
    for n in (1, 2, 3, 5, 7)
)

C_HUCRE_MATRISI = C_DOLULUK_MATRISI + C_DEGER_MATRISI + C_SEKIL_MATRISI


@pytest.mark.parametrize(
    "metin,iz",
    [(m, iz) for _ad, m, iz in C_HUCRE_MATRISI],
    ids=[ad for ad, *_ in C_HUCRE_MATRISI],
)
def test_bolum_c_hucre_sozlesmesi(metin: str, iz: str) -> None:
    """Her bozma KENDİ izini üretiyor mu?"""
    assert iz in _notlari(metin)


def test_bolum_c_hucre_matrisi_bos_kume_ve_taban_kollari() -> None:
    """Matris gerçekten ÜRETİLDİ mi, taban BOŞA yeşil mi?"""
    assert len(C_DOLULUK_MATRISI) == len(bd.C_TABLOSU_SUTUNLARI) == 6
    assert len(C_HUCRE_MATRISI) == 6 + 7 + 8 == 21, len(C_HUCRE_MATRISI)
    adlar = [ad for ad, *_ in C_HUCRE_MATRISI]
    assert len(set(adlar)) == len(adlar), "hücreler ÇAKIŞIYOR"
    # Her hücre belgeyi GERÇEKTEN değiştiriyor.
    for ad, metin, _iz in C_HUCRE_MATRISI:
        assert metin != TEMIZ, ad
    # TABAN: temiz kaynak izlerin HİÇBİRİNİ üretmiyor (yanlış-pozitif yok).
    temiz = _notlari(TEMIZ)
    assert temiz == ""
    for ad, _metin, iz in C_HUCRE_MATRISI:
        assert iz not in temiz, ad


def test_bolum_c_hucre_matrisi_mutasyona_duyarli() -> None:
    """MUTASYON: kuralları sök → matris KIRMIZI düşmeli.

    Üç ayrı seam, çünkü üç ayrı kural: satır denetimi · kapsama kontrolü ·
    başlık satırının SÖZLEŞMEDEN okunması. Tek bir kaba mutasyon
    (`_kontrol_url_bicimi` → []) hepsini birden düşürür ve hangi kuralın
    gerçekten çalıştığını AYIRT ETMEZ.
    """
    satir_izleri = [
        iz for _ad, _m, iz in C_DOLULUK_MATRISI + C_DEGER_MATRISI
    ] + [f"{n} sütunlu" for n in (1, 2, 3, 5, 7)]
    with mock.patch.object(bd, "_c_satir_ihlalleri", lambda satir, belge: []):
        for (ad, metin, iz) in C_DOLULUK_MATRISI + C_DEGER_MATRISI:
            assert iz not in _notlari(metin), ad
        for n in (1, 2, 3, 5, 7):
            assert f"{n} sütunlu" not in _notlari(c_sutun_sayisini_boz(TEMIZ, n))
    assert satir_izleri, "izler üretilmedi"

    with mock.patch.object(bd, "_c_kapsama_ihlalleri", lambda belge: []):
        assert "kaynak satırı taşımıyor" not in _notlari(c_ilk_satiri_kaldir(TEMIZ))
        # ...ve KOMŞU kural ayakta kalıyor: mutasyon dar.
        assert "`iddia` hücresi BOŞ" in _notlari(c_iddiayi_bosalt(TEMIZ))

    # Başlık satırı SÖZLEŞMEDEN okunuyor: sabit değişirse TEMİZ belge DÜŞER.
    # Bu, "kapı gerçekten o satırı arıyor mu" sorusunun ölçümüdür.
    with mock.patch.object(bd, "C_TABLOSU_SUTUNLARI", ("a", "b", "c")):
        assert "başlık satırını taşımıyor" in _notlari(TEMIZ)


# ─── M2: kapsam beyanı ÇAĞIRAN tarafından uydurulamaz ──────────────────────


def test_kapsam_sinirlari_cagirandan_alinmaz() -> None:
    """F3: beyan `CHECKS`'ten TÜRER — isteğe bağlı da değildir, uydurulamaz da."""
    with pytest.raises(TypeError):
        bd.DoctorReport(
            sonuc=bd.SONUC_GECTI,
            notlar=(),
            elemeler=(),
            kaynak_adi="K",
            kapsam_sinirlari=("uydurma sınır",),  # type: ignore[call-arg]
        )
    dogrudan = bd.DoctorReport(
        sonuc=bd.SONUC_GECTI, notlar=(), elemeler=(), kaynak_adi="K"
    )
    beklenen = tuple(s for c in bd.CHECKS for s in c.kapsam_sinirlari)
    assert dogrudan.kapsam_sinirlari == beklenen
    assert dogrudan.kapsam_sinirlari == bd.run(TEMIZ, source_name="K").kapsam_sinirlari


def test_kapsam_beyani_checks_ten_turedigi_mutasyonla_olculur() -> None:
    """Mutasyon kolu: `CHECKS` değişince beyan da değişmeli (türev, kopya değil)."""
    sahte = bd.CHECKS[:1]
    with mock.patch.object(bd, "CHECKS", sahte):
        rapor = bd.DoctorReport(
            sonuc=bd.SONUC_GECTI, notlar=(), elemeler=(), kaynak_adi="K"
        )
        assert rapor.kapsam_sinirlari == tuple(
            sinir for c in sahte for sinir in c.kapsam_sinirlari
        )
    # Boş-küme kolu: hiç beyan yoksa demet BOŞ olmalı, eski değer sızmamalı.
    with mock.patch.object(bd, "CHECKS", ()):
        assert bd.DoctorReport(
            sonuc=bd.SONUC_GECTI, notlar=(), elemeler=(), kaynak_adi="K"
        ).kapsam_sinirlari == ()


# ─── M3: Bölüm B'deki ALAKASIZ tablo gerekçe kontrollerine beslenmez ───────

ALAKASIZ_TABLO_MATRISI = tuple(
    (f"donem-{i}-icine-tablo", bolum_b_alakasiz_tablo(TEMIZ, i)) for i in range(6)
)


@pytest.mark.parametrize(
    "metin", [m[1] for m in ALAKASIZ_TABLO_MATRISI],
    ids=[m[0] for m in ALAKASIZ_TABLO_MATRISI],
)
def test_alakasiz_tablo_uydurma_bulgu_uretmez(metin: str) -> None:
    """F5: gerekçe tablosu dönemlerden ÖNCEKİ İLK bitişik tablodur."""
    rapor = bd.run(metin, source_name="P")
    assert rapor.notlar == (), " | ".join(b.mesaj for b in rapor.notlar)
    assert rapor.sonuc == bd.SONUC_GECTI


def test_gercek_gerekce_tablosu_bozuksa_hala_gorunur() -> None:
    """Kontrol kolu: körelme YOK — bozuk GERÇEK tablo hâlâ not üretir."""
    mesajlar = _notlari(gerekce_tablosunu_boz(TEMIZ))
    assert "3 sütunlu satır" in mesajlar
    assert "tür etiketi yok" in mesajlar
    # ...alakasız tablo EKLENSE bile bozuk gerçek tablo görünmeye devam eder.
    ikili = _notlari(bolum_b_alakasiz_tablo(gerekce_tablosunu_boz(TEMIZ), 2))
    assert "3 sütunlu satır" in ikili


def test_tablo_donemlerden_sonra_hala_gorunur() -> None:
    """Kontrol kolu: ilk-bitişik-tablo kuralı SIRA ihlalini köreltmemeli."""
    assert "dönem başlıklarından SONRA" in _notlari(
        tabloyu_donemlerden_sonraya_tasi(TEMIZ)
    )


def test_yeni_kapilarin_hepsi_mutasyona_duyarli() -> None:
    """Mutasyon kolu: tur 2'de eklenen DÖRT kapıyı ayrı ayrı sök → susmalılar."""
    # (a) ESSİZ madde sayımı: sök → boşluk ifadesiyle doldurulan alan sussun.
    bos_madde = blok_maddesini_bosalt(TEMIZ, "### cta_kaliplari")
    assert "alt sınırı" in _notlari(bos_madde)
    with mock.patch.object(
        bd._Yuva, "essiz_maddeler", property(lambda self: self.maddeler)
    ):
        assert "alt sınırı" not in _notlari(bos_madde)

    # (b) ESSİZ dönem sayımı: sök → tekrarla sağlanan alt sınır sussun.
    tekrar_donem = blok_cogalt(TEMIZ, f"### {_DONEM_ADLARI[0]}")
    eksik = bolum_b_alakasiz_tablo(TEMIZ, 0)  # tabloyu bozmayan taban
    assert bd._essiz_donem_sayisi(bd._ayristir(tekrar_donem)) == 6
    with mock.patch.object(bd, "_essiz_donem_sayisi", lambda b: len(b.donemler)):
        assert bd._essiz_donem_sayisi(bd._ayristir(tekrar_donem)) == 7
    assert _notlari(eksik) == ""

    # (c) Bölüm C hücre denetimi: sök → boş `iddia` hücresi sussun.
    bos_hucre = c_iddiayi_bosalt(TEMIZ)
    assert "`iddia` hücresi BOŞ" in _notlari(bos_hucre)
    with mock.patch.object(bd, "_c_satir_ihlalleri", lambda satir, belge: []):
        assert "`iddia` hücresi BOŞ" not in _notlari(bos_hucre)

    # (d) Gerekçe tablosu TANIMA kuralı: sök → alakasız tablo uydurma not versin.
    # (Kural tur 3'te "ilk bitişik tablo"dan KANONİK BAŞLIK tanımasına geçti;
    #  mutasyon o yüzden yeni sözleşmeye göre yazılır — bkz. H6.)
    alakasiz = bolum_b_alakasiz_tablo(TEMIZ, 2)
    assert _notlari(alakasiz) == ""
    with mock.patch.object(
        bd, "_gerekce_tablosu", lambda bloklar: (list(bloklar), 1)
    ):
        bozuk = _notlari(alakasiz)
        assert "2 sütunlu satır" in bozuk and "tür etiketi yok" in bozuk


def test_alakasiz_tablo_matrisi_bos_kume_kolu() -> None:
    """Boş-küme kolu: alakasız tablo matrisi TÜM dönemlere uygulanmış mı?"""
    assert len(ALAKASIZ_TABLO_MATRISI) == 6
    for ad, metin in ALAKASIZ_TABLO_MATRISI:
        assert metin != TEMIZ, f"{ad}: cerrahi metni değiştirmedi"
        assert metin.count("| olcut | deger |") == 1


# ─── H5: kapıya UYGUN rapor kanonik ÖZET taşır (fail-closed) ───────────────
#
# Sınıf (tur 3, F1): *"kimliğin İÇERİK ayağı olmadan da K-127 tabanı
# geçilebiliyor."* Ölçüldü — `run`'ı ATLAYIP doğrudan kurulan iki özetsiz rapor
# (`DoctorReport(sonuc='gecti', notlar=(), elemeler=(), kaynak_adi='gemini-cikti'
# / 'claude-cikti')`) `dur=False, gecerli=2` veriyordu. Tipin AÇIKÇA desteklediği
# bir çağrı yolu (Task 9/12 tüketicileri `run`'ı atlayabilir) tek kaynakla tabanı
# geçiyordu. Bir önceki turun TAKMA_AD_MATRISI bunu göremezdi: o matris yalnız
# `run` üretimi raporları egzersiz eder ve `run` özeti HER ZAMAN üretir.
#
# **Matris KAVRAMDAN türer** (kontrolörün üç örneğinden değil): eksen 1 =
# raporun İÇERİK ayağının durumu, eksen 2 = AD ayağının denkliği, eksen 3 =
# raporun sonucu — kimliğin iki ayağı × kapı sayımına giriş koşulu. 3 × 2 × 3 =
# 18 hücre; bilinçle boş bırakılan hücre YOKTUR.

_OZET_A = bd.identity.canonical_sha("kanonik metin A")
_OZET_B = bd.identity.canonical_sha("kanonik metin B")

OZET_EKSENI = (
    # `run` yolunu atlayan çağıran metne sahip olmayabilir — özet BOŞ kalır.
    ("ozet-yok", ("", "")),
    # Biçimi geçerli ama `run` ÜRETMEDİ: köken doğrulanamaz (kapsam sınırı).
    ("ozet-uydurma-bicimli", ("a" * 64, "b" * 64)),
    # `identity.canonical_sha` üretimi — kimliğin gerçek İÇERİK ayağı.
    ("ozet-kanonik", (_OZET_A, _OZET_B)),
)
AD_EKSENI = (
    ("ad-ayni", ("KAYNAK-9", "KAYNAK-9")),
    ("ad-farkli", ("KAYNAK-9", "KAYNAK-8")),
)
SONUC_EKSENI = (
    ("gecti", bd.SONUC_GECTI),
    ("notlu-gecti", bd.SONUC_NOTLU_GECTI),
    ("elendi", bd.SONUC_ELENDI),
)


def _dogrudan_rapor(sonuc: str, ad: str, ozet: str) -> "bd.DoctorReport":
    """`run` yolunu ATLAYAN çağıranın kurduğu rapor — tipin açık yolu."""
    notlar = (_not_bulgu(),) if sonuc == bd.SONUC_NOTLU_GECTI else ()
    elemeler = (_eleme_bulgu(),) if sonuc == bd.SONUC_ELENDI else ()
    return bd.DoctorReport(
        sonuc=sonuc, notlar=notlar, elemeler=elemeler, kaynak_adi=ad,
        icerik_ozeti=ozet,
    )


def _ozet_matris_beklentisi(ozet_adi: str, ad_adi: str, sonuc: str) -> tuple[int, bool]:
    """Beklenti KURALDAN türer, hücre hücre elle yazılmaz."""
    kimlik_sayisi = 1 if ad_adi == "ad-ayni" else 2
    if sonuc == bd.SONUC_ELENDI:
        return 0, True  # elenen kimlik sayıma GİRMEZ (meşru özetsiz hâl)
    if ozet_adi == "ozet-yok":
        return 0, True  # fail-closed: özetsiz rapor kapıya uygun DEĞİLDİR
    return kimlik_sayisi, kimlik_sayisi < bd.KAYNAK_TABANI


OZET_MATRISI = tuple(
    (
        f"{ozet_adi}/{ad_adi}/{sonuc_adi}",
        _ozet_ciftler,
        _ad_ciftler,
        sonuc,
        _ozet_matris_beklentisi(ozet_adi, ad_adi, sonuc),
    )
    for ozet_adi, _ozet_ciftler in OZET_EKSENI
    for ad_adi, _ad_ciftler in AD_EKSENI
    for sonuc_adi, sonuc in SONUC_EKSENI
)


@pytest.mark.parametrize(
    "ozetler,adlar,sonuc,beklenen",
    [h[1:] for h in OZET_MATRISI],
    ids=[h[0] for h in OZET_MATRISI],
)
def test_ozetsiz_rapor_kapi_sayisina_giremez(
    ozetler: tuple[str, str], adlar: tuple[str, str], sonuc: str,
    beklenen: tuple[int, bool],
) -> None:
    """Özetsiz bir rapor SESSİZCE sayılamaz — sayılmaz (fail-closed)."""
    gate = bd.gate_round(
        [_dogrudan_rapor(sonuc, ad, ozet) for ad, ozet in zip(adlar, ozetler)]
    )
    assert (gate.gecerli_kaynak_sayisi, gate.dur) == beklenen


def test_ozet_matrisi_bos_kume_taban_ve_kontrol_kollari() -> None:
    """Boş-küme + kontrol kolları: matris üç eksenden GERÇEKTEN üretilmiş mi?"""
    assert len(OZET_EKSENI) == 3 and len(AD_EKSENI) == 2 and len(SONUC_EKSENI) == 3
    assert len(OZET_MATRISI) == 3 * 2 * 3 == 18
    assert {h[0] for h in OZET_MATRISI}.__len__() == 18, "hücre adları çakışıyor"
    # Matris hem geçen hem duran hücre taşımalı — tek renkli matris ölçmez.
    durumlar = {h[4][1] for h in OZET_MATRISI}
    assert durumlar == {True, False}, f"matris tek renkli: {durumlar}"

    # Kontrol kolu (a): `run` üretimi İKİ GERÇEK farklı kaynak hâlâ geçmeli.
    gate = bd.gate_round([_rapor(_ad="KAYNAK-1"), _rapor(_ad="KAYNAK-2", cta=6)])
    assert (gate.dur, gate.gecerli_kaynak_sayisi) == (False, 2)

    # Kontrol kolu (b): MEŞRU karma hâl — aynı kimliğin bir raporu özetli.
    # Grup özet taşıdığı için kimlik kapıya UYGUNDUR; uydurma özet ÜRETİLMEZ.
    karma = bd.gate_round(
        [
            _rapor(_ad="KAYNAK-1"),
            _dogrudan_rapor(bd.SONUC_GECTI, "KAYNAK-1", ""),
            _rapor(_ad="KAYNAK-2", cta=6),
        ]
    )
    assert (karma.dur, karma.gecerli_kaynak_sayisi) == (False, 2)

    # Boş-küme kolu.
    assert bd.gate_round([]).gecerli_kaynak_sayisi == 0


def test_ozetsiz_kaynak_yoneticiye_BILDIRILIR() -> None:
    """Sessizce düşmez: özetsiz kimlik bildirimde ADIYLA görünür."""
    gate = bd.gate_round(
        [
            _dogrudan_rapor(bd.SONUC_GECTI, "gemini-cikti", ""),
            _dogrudan_rapor(bd.SONUC_GECTI, "claude-cikti", ""),
        ]
    )
    assert gate.dur is True
    assert "gemini-cikti" in gate.bildirim and "claude-cikti" in gate.bildirim
    assert "özet" in gate.bildirim.casefold()


def test_ozet_kapisi_mutasyona_duyarli() -> None:
    """Mutasyon kolu: özet şartını SÖK → özetsiz çift yine 2 kaynak saysın."""
    ozetsiz = [
        _dogrudan_rapor(bd.SONUC_GECTI, "gemini-cikti", ""),
        _dogrudan_rapor(bd.SONUC_GECTI, "claude-cikti", ""),
    ]
    assert bd.gate_round(ozetsiz).gecerli_kaynak_sayisi == 0
    with mock.patch.object(bd, "_kimlik_kapiya_uygun", lambda raporlar: True):
        assert bd.gate_round(ozetsiz).gecerli_kaynak_sayisi == 2


# ─── H6: dönem-ÖNCESİ HER tablo denetlenir — SEÇİM YOK ─────────────────────
#
# Sınıf (tur 4, medium — aynı eksende ÜÇÜNCÜ kez ve üçüncü kez KENDİ
# düzeltmemizin ürünü):
#   v1  tanıma yoktu → Bölüm B'deki her `|` satırı gerekçe malzemesiydi
#       (dönem bloğuna konan meşru bir ölçüm tablosu DÖRT uydurma not verdi).
#   v2  "dönemlerden ÖNCEKİ İLK BİTİŞİK tablo" → önüne konan yem gizledi.
#   v3  "kanonik başlık taşıyan aday" → ölçüldü ve o da kandırıldı: GERÇEK
#       gerekçe tablosunun başlığı JENERİK olduğunda eşiğin ALTINDA kalır,
#       önüne konan KANONİK başlıklı bir yem TEK aday olur ve gerçek tabloyu
#       tamamen susturur. Ölçüldü: yem yokken `notlu-gecti / 8 not`, yem
#       eklenince `gecti / 0 not`.
#
# Ortak desen: her tur bir SEÇİM sezgiseli kurdu ve her sezgisel kendi kalıbına
# uyan bir yemle kandırıldı. Bu tur SEÇİMİ BIRAKIR: dönem bloklarından ÖNCE
# gelen BÜTÜN tablolar denetlenir, hiçbiri sessizce ATILMAZ; birden çoksa
# belirsizlik NOTU düşer. Kanonik başlık artık bir SEÇİM kuralı değil, bir NOT
# konusudur (`_gerekce_basligi_puani` yalnız notu besler).
#
# **Bilinçli bedel:** dönemlerden önce konmuş meşru ve alakasız bir tablo artık
# NOT üretir (kendi satırları da tür etiketi/sütun denetimine girer). Bugün
# hiçbir kontrol ELEMEDİĞİ için maliyet gürültüdür, kaynak kaybı değil — ve not
# SESSİZ DEĞİLDİR, belirsizlik açıkça yazılır. Sessiz gizlenmeye tercih edilir.
#
# **Korunan kazanım (v2'nin yanlış-pozitif düzeltmesi):** dönem bloklarının
# İÇİNDE ya da SONRASINDA duran tablolar gerekçe denetimine GİRMEZ ve 0 not
# vermeye devam eder. Bu bir sezgisel değil, sözleşmenin KENDİ sırasıdır
# ("önce tablo, sonra dönem dönem dört başlık").
#
# **Matris KAVRAMDAN türer** (bulunan örneklerden değil). Bir tablo bloğunun
# gerekçe denetimine girip girmemesi iki bağımsız eksene bağlıdır:
#   eksen 1 — KONUM: `_bolum_b_konumlari` ÜRETİR, bu yorum saymaz. Bölgeler
#             ayrıştırıcının Bölüm B işaretlerinden (dönemi AÇAN `mesaj_ekseni`
#             yuvası · dönemi KAPATAN başlık) türer ve BEŞ değerlidir.
#   eksen 2 — BAŞLIK: kanonik gerekçe başlığı taşıyor · taşımıyor
# ve denetlenecek belgede GERÇEK gerekçe tablosunun durumu üçüncü eksendir:
#   eksen 3 — sağlam · satırları bozuk · başlığı jenerik VE satırları bozuk
# 5 × 2 × 3 = 30 hücre. BOŞ HÜCRE YOKTUR.
#
# **Tur 5'in kapattığı boşluk.** Önceki eksen ÜÇ değerliydi (ÖNCE · İÇİNDE ·
# SONRA) ve "İÇİNDE" TEK bir alt-konumla — yuvadan SONRA — sınandı. Dönem
# BAŞLIĞI ile o dönemin İLK YUVASI arası hiç egzersiz edilmedi ve gerileme tam
# oradan geçti: `bool(donemler)` dönemi başlıkta değil ilk YUVAda başlatıyordu,
# başlığın hemen altındaki bir tablo "dönem öncesi" sayılıyor ve gerekçe
# denetimine giriyordu (ölçüldü, 46579a1 vs 7075658: `0 not → 4 not`). Düzeltme
# bir SEÇİM sezgiseli değil bir SINIR tanımıdır: bölge ilk dönem BAŞLIĞINDA
# biter (`_ilk_donem_baslangici`).
#
# Eksen 3'ün DÖRDÜNCÜ değeri ("gerçek gerekçe tablosu YOK") bilinçle dışarıda
# bırakıldı, sessizce atlanmadı: o dalda susturulacak bir blok bulunmadığı için
# bu sınıf (bir blok bir başkasını susturur mu) hiç KURULAMAZ; ayrıca kendi
# yanlış-pozitif kapanı vardır (`test_tablosuz_bolum_b_tanima_notu_uretmez`).

_EK_TABLOLAR = {
    # Alakasız ölçüm tablosu — kanonik gerekçe başlığını TAŞIMAZ.
    "jenerik": (
        "| ay | trafik | dönüşüm | serbest not |\n",
        "|---|---|---|---|\n",
        "| ocak | yuksek | orta | ilk ceyrek |\n",
        "| subat | orta | orta | ilk ceyrek |\n",
    ),
    # Aynı boydaki tablo ama kanonik gerekçe BAŞLIĞIYLA — v3'ü kandıran yem.
    "kanonik": (
        "| dönem | karar | tür | gerekçe |\n",
        "|---|---|---|---|\n",
        "| ocak | secildi | kutlama | Uydurma gerekce. |\n",
        "| subat | secildi | kutlama | Uydurma gerekce. |\n",
    ),
}
_ALAKASIZ_4_SUTUN = _EK_TABLOLAR["jenerik"]
_SAHTE_GEREKCE = _EK_TABLOLAR["kanonik"]


def _bolum_b_izdusumu(metin: str) -> tuple[list[str], int]:
    """Bölüm B satırları + o satırların TAM BELGEDEKİ ofseti.

    Bölümleme test tarafından YENİDEN YAPILMAZ: satırlar modülün KENDİ
    ayrıştırıcısından (`_ayristir`) okunur, ofset belgeye geri eşlenerek
    doğrulanır (eşleşme TEK olmak zorunda).
    """
    satirlar = metin.splitlines()
    b = bd._ayristir(metin).bolumler["B"]
    eslesmeler = [
        ofset
        for ofset in range(len(satirlar) - len(b) + 1)
        if satirlar[ofset : ofset + len(b)] == b
    ]
    assert len(eslesmeler) == 1, f"Bölüm B belgeye tek biçimde eşlenmedi: {eslesmeler}"
    return b, eslesmeler[0]


def _b_isaretleri(b_satirlari: list[str]) -> tuple[list[int], list[int]]:
    """Ayrıştırıcının Bölüm B'de tanıdığı İKİ işaret — modülün KENDİ desenleriyle.

    `_ayristir`'ın Bölüm B döngüsü yalnız şunlara bakar: dönemi AÇAN
    `mesaj_ekseni` yuvası ve dönemi KAPATAN (ve bir sonrakini ADLANDIRAN)
    başlık görünümü. Konum ekseni bu iki işaretin ayırdığı bölgelerden TÜRER —
    elle seçilmiş örneklerden değil.
    """
    yuvalar: list[int] = []
    basliklar: list[int] = []
    for i, satir in enumerate(b_satirlari):
        yuva = bd._YUVA_DESENI.match(satir)
        if yuva and yuva.group(1) == "mesaj_ekseni":
            yuvalar.append(i)
        elif not yuva and bd._BASLIK_GORUNUMU_RE.match(satir):
            basliklar.append(i)
    return yuvalar, basliklar


def _bolum_b_konumlari(metin: str) -> dict[str, tuple[int, tuple[str, ...]]]:
    """Bir tablo bloğunun Bölüm B'de durabileceği AYRIK konumlar.

    Değerler `(tam belge ekleme indeksi, önek satırları)`. Bölgeler
    `_b_isaretleri`'nin iki işaretinden türer:

      `donem-oncesi`            ilk dönem BAŞLIĞINDAN önce → denetime GİRER
      `baslik-yuva-arasi`       dönem başlığı ile o dönemin İLK YUVASI arasında
      `yuvalar-arasi`           bir dönemin yuvaları arasında
      `bolum-b-sonu`            son dönemin son satırından sonra
      `kapanis-basligi-sonrasi` son dönemi KAPATAN ama yeni dönem AÇMAYAN bir
                                başlıktan sonra (konum kendi öneğini getirir)

    Bir önceki turun ekseni ÜÇ değerliydi (ÖNCE · İÇİNDE · SONRA) ve "İÇİNDE"
    tek bir alt-konumla — yuvadan SONRA — sınanmıştı; `baslik-yuva-arasi` hiç
    egzersiz edilmedi ve gerileme tam oradan geçti (ölçüldü: `0 not → 4 not`).

    `yuvalar-arasi` ile `bolum-b-sonu` ayrıştırıcının AYNI durumundadır (dönem
    İÇİ, yuvadan sonra). İkisi ayrı hücre TUTULUR çünkü bir önceki turun
    gerileme kolu belge SONUNDA yaşıyordu; tek hücreye indirmek kapsamı
    DARALTIRDI. Bu bir durum ayrımı değil, bilinçli bir KAPSAMA fazlalığıdır.
    """
    b, ofset = _bolum_b_izdusumu(metin)
    yuvalar, basliklar = _b_isaretleri(b)
    assert len(yuvalar) > 1, "eksen çok dönemli belge ister"
    ilk_yuva = yuvalar[0]
    onceki = [i for i in basliklar if i < ilk_yuva]
    konumlar: dict[str, tuple[int, tuple[str, ...]]] = {"donem-oncesi": (ofset, ())}
    # İlk dönemin BAŞLIĞI yoksa bu konum o belgede VAR DEĞİLDİR; uydurulmaz.
    if onceki:
        konumlar["baslik-yuva-arasi"] = (ofset + onceki[-1] + 1, ())
    konumlar["yuvalar-arasi"] = (ofset + ilk_yuva + 1, ())
    konumlar["bolum-b-sonu"] = (ofset + len(b), ())
    konumlar["kapanis-basligi-sonrasi"] = (ofset + len(b), ("### Ek ölçüm bloğu", ""))
    return konumlar


def bolum_b_tablo_ekle(metin: str, konum: str, tablo: tuple[str, ...]) -> str:
    """Bölüm B'ye ek bir tabloyu `_bolum_b_konumlari`'nın bir konumuna koyar."""
    konumlar = _bolum_b_konumlari(metin)
    assert konum in konumlar, f"bilinmeyen konum: {konum!r} — {list(konumlar)}"
    k, onek = konumlar[konum]
    satirlar = metin.splitlines(True)
    ek = [f"{satir}\n" for satir in onek] + list(tablo)
    return "".join(satirlar[:k] + ["\n"] + ek + ["\n"] + satirlar[k:])


def gerekce_basligini_jeneriklestir(metin: str) -> str:
    """GERÇEK gerekçe tablosunun BAŞLIĞINI kanonik olmayan bir başlığa çevirir."""
    yeni = metin.replace("| dönem | karar | tür | gerekçe |", "| a | b | c | d |")
    assert yeni != metin, "cerrahi gerekçe tablosunun başlığını bulamadı"
    return yeni


# Eksen 3 — GERÇEK gerekçe tablosunun durumu. Üçüncü değer o durumun rapora
# BIRAKMASI gereken izleri taşır; izler kontrol MESAJLARINDAN türer.
_GERCEK_TABLO_DURUMLARI = (
    ("saglam", lambda m: m, ()),
    (
        "satirlari-bozuk",
        gerekce_tablosunu_boz,
        ("tür etiketi yok", "3 sütunlu satır"),
    ),
    (
        "jenerik-baslik-ve-bozuk",
        lambda m: gerekce_tablosunu_boz(gerekce_basligini_jeneriklestir(m)),
        ("tür etiketi yok", "3 sütunlu satır"),
    ),
)


def _tur_etiketi_notu_verir(tablo: tuple[str, ...]) -> bool:
    """Ek tablonun VERİ satırlarından biri kapalı kümeden etiket taşımıyor mu?

    Beklenti elle yazılmaz: denetime giren her satır `_kontrol_tur_etiketi`'ne
    de girer, o yüzden ek tablonun kendi hücrelerinden ÜRETİLİR.
    """
    return any(
        not any(
            hucre.strip() in bd.TUR_ETIKETLERI
            for hucre in satir.strip().strip("|").split("|")
        )
        for satir in tablo[2:]
    )


# Konum ekseni ELLE SAYILMAZ: belgenin kendi yapısından türer.
GEREKCE_KONUMLARI = tuple(_bolum_b_konumlari(TEMIZ))
# Denetime giren TEK konum — sınır ilk dönem BAŞLIĞINDA biter.
DENETLENEN_KONUM = "donem-oncesi"
# Konumun görünür izi: ek tablo dönem-öncesi kümeye KATILDIYSA belirsizlik
# notu düşer. Denetlenmeyen konumlarda bu iz OLMAMALIDIR (çift yönlü kapı).
_KONUM_IZI = "dönem başlıklarından ÖNCE"


def _beklenen_izler(konum: str, baslik: str, durum: str, durum_izleri) -> tuple:
    """Hücrenin beklentisini KURALDAN türetir, elle listelemez."""
    izler = list(durum_izleri)
    denetlenen = konum == DENETLENEN_KONUM
    if denetlenen and _tur_etiketi_notu_verir(_EK_TABLOLAR[baslik]):
        izler.append("tür etiketi yok")
    basliksiz = int(denetlenen and baslik == "jenerik") + int(
        durum == "jenerik-baslik-ve-bozuk"
    )
    if basliksiz:
        izler.append(f"denetimine giren {basliksiz} tablo")
    if denetlenen:
        izler.append(f"{_KONUM_IZI} 2 tablo var")
    return tuple(dict.fromkeys(izler))


def _yasak_izler(konum: str) -> tuple[str, ...]:
    """Hücrede BULUNMAMASI gereken izler — konumun negatif kapısı.

    Pozitif iz listesi tek başına yetmiyordu: gerçek tablosu BOZUK bir hücrede
    `olmali` listesi zaten doluydu ve ek tablonun denetime SIZDIĞI görünmüyordu.
    Gerilemenin altı hücresi tam bu boşluktan geçti.
    """
    return () if konum == DENETLENEN_KONUM else (_KONUM_IZI,)


GEREKCE_DENETIM_MATRISI = tuple(
    (
        f"ek-{konum}/baslik-{baslik}/gercek-{durum}",
        bolum_b_tablo_ekle(bozan(TEMIZ), konum, _EK_TABLOLAR[baslik]),
        _beklenen_izler(konum, baslik, durum, izler),
        _yasak_izler(konum),
        _EK_TABLOLAR[baslik][2],
    )
    for konum in GEREKCE_KONUMLARI
    for baslik in ("jenerik", "kanonik")
    for durum, bozan, izler in _GERCEK_TABLO_DURUMLARI
)


def _matris_ihlali(metin: str, olmali: tuple, olmamali: tuple) -> str:
    """Bir hücrenin ihlali (boş metin = hücre yeşil)."""
    mesajlar = _notlari(metin)
    if not olmali and mesajlar:
        return f"denetim dışı tablo not üretti: {mesajlar[:400]}"
    for iz in olmali:
        if iz not in mesajlar:
            return f"{iz!r} bulunamadı; görülen: {mesajlar[:600]}"
    for iz in olmamali:
        if iz in mesajlar:
            return f"{iz!r} SIZDI; görülen: {mesajlar[:600]}"
    return ""


@pytest.mark.parametrize(
    "metin,olmali,olmamali",
    [(h[1], h[2], h[3]) for h in GEREKCE_DENETIM_MATRISI],
    ids=[h[0] for h in GEREKCE_DENETIM_MATRISI],
)
def test_donem_oncesi_her_tablo_denetlenir(
    metin: str, olmali: tuple, olmamali: tuple
) -> None:
    """Aday olan bir blok, aday OLMAYAN bir bloğu SUSTURAMAZ — ve tersi."""
    assert _matris_ihlali(metin, olmali, olmamali) == ""


def test_gerekce_denetim_matrisi_bos_kume_ve_taban_kollari() -> None:
    """Boş-küme kolu: matris ÜÇ eksenden gerçekten üretilmiş mi, boşa yeşil mi?"""
    assert len(GEREKCE_KONUMLARI) == 5, GEREKCE_KONUMLARI
    assert DENETLENEN_KONUM in GEREKCE_KONUMLARI
    assert len(GEREKCE_DENETIM_MATRISI) == 5 * 2 * 3 == 30
    adlar = [h[0] for h in GEREKCE_DENETIM_MATRISI]
    assert len(set(adlar)) == 30, "matris hücreleri ÇAKIŞIYOR"
    for konum in GEREKCE_KONUMLARI:
        assert sum(1 for ad in adlar if ad.startswith(f"ek-{konum}/")) == 6, konum
    for baslik in ("jenerik", "kanonik"):
        assert sum(1 for ad in adlar if f"/baslik-{baslik}/" in ad) == 15, baslik
    for durum, _, _ in _GERCEK_TABLO_DURUMLARI:
        assert sum(1 for ad in adlar if ad.endswith(f"/gercek-{durum}")) == 10, durum
    for ad, metin, _, _, imza in GEREKCE_DENETIM_MATRISI:
        assert metin != TEMIZ, f"{ad}: cerrahi metni değiştirmedi"
        assert metin.count(imza) == 1, f"{ad}: ek tablo tam bir kez konmadı"
    # Beklentiler BOŞA yeşil değil: 30 hücrenin 22'si POZİTİF iz bekliyor
    # (boş kalan sekizi = denetim dışı DÖRT konum × iki başlık × sağlam gerçek
    # tablo; o hücrelerin kapısı "hiç not yok" + negatif iz listesidir).
    beklentili = [h[0] for h in GEREKCE_DENETIM_MATRISI if h[2]]
    assert len(beklentili) == 22, beklentili
    yasakli = [h[0] for h in GEREKCE_DENETIM_MATRISI if h[3]]
    assert len(yasakli) == 24, yasakli
    # Taban kolu: pozitif kontrol — ek tablo YOKKEN temiz kaynak notsuz geçer.
    rapor = bd.run(TEMIZ, source_name="P")
    assert rapor.notlar == () and rapor.sonuc == bd.SONUC_GECTI


def _sinir_ilk_yuvada(baslik_sirasi, yuva_sirasi):
    """Mutasyon: bölgeyi ilk YUVAda bitir — 46579a1'in (yanlış) sınırı."""
    return yuva_sirasi


def test_donem_bolgesi_siniri_mutasyona_duyarli() -> None:
    """Mutasyon kolu: sınırı ilk yuvaya geri al → matris KIRMIZI düşmeli."""
    kirmizi = []
    with mock.patch.object(bd, "_ilk_donem_baslangici", _sinir_ilk_yuvada):
        for ad, metin, olmali, olmamali, _ in GEREKCE_DENETIM_MATRISI:
            if _matris_ihlali(metin, olmali, olmamali):
                kirmizi.append(ad)
    assert kirmizi, "sınırı ilk yuvaya almak matrisi kırmızıya düşürmedi"
    # ...ve KAÇAN konumun ALTI hücresinin hepsi düşmeli: gerileme tam oradaydı.
    kacan = [ad for ad in kirmizi if ad.startswith("ek-baslik-yuva-arasi/")]
    assert len(kacan) == 6, kacan
    # Sınır mutasyonu YALNIZ o konumu bozmalı — matris başka yerden kırmızı
    # düşüyorsa mutasyon ölçtüğünü sandığımız şeyi ölçmüyordur.
    assert set(kirmizi) == set(kacan), sorted(set(kirmizi) - set(kacan))


def test_basliksiz_ilk_donem_sinirini_ilk_yuvaya_ceker() -> None:
    """Sınır fonksiyonunun İKİNCİ dalı: ilk dönemin başlığı YOKSA.

    Bölge o zaman ilk YUVAda biter — aksi hâlde başlıksız bir belgede bölge
    hiç kapanmaz ya da yanlış yerde kapanırdı (fail-open).
    """
    satirlar = TEMIZ.splitlines(True)
    i, _ = _md_blok(satirlar, f"### {_DONEM_ADLARI[0]}")
    basliksiz = "".join(satirlar[:i] + satirlar[i + 1 :])
    assert basliksiz != TEMIZ
    metin = bolum_b_tablo_ekle(basliksiz, DENETLENEN_KONUM, _ALAKASIZ_4_SUTUN)
    mesajlar = _notlari(metin)
    assert f"{_KONUM_IZI} 2 tablo var" in mesajlar, mesajlar[:400]


def _v3_secimi(bloklar):
    """Mutasyon: tur 3'ün SEÇİM sezgiseli (dönem-öncesi süpürme SÖKÜLÜ)."""
    adaylar = [
        blok
        for blok in bloklar
        if blok
        and bd._gerekce_basligi_puani(blok[0][1]) >= bd.GEREKCE_BASLIK_ASGARI
    ]
    if adaylar:
        return list(adaylar), len(adaylar)
    return list(bloklar), 0


def test_donem_oncesi_supurme_mutasyona_duyarli() -> None:
    """Mutasyon kolu: süpürmeyi sök (v3 seçimine dön) → matris KIRMIZI düşmeli."""
    kirmizi = []
    with mock.patch.object(bd, "_gerekce_tablosu", _v3_secimi):
        for ad, metin, olmali, olmamali, _ in GEREKCE_DENETIM_MATRISI:
            if _matris_ihlali(metin, olmali, olmamali):
                kirmizi.append(ad)
    assert kirmizi, "seçimi geri koymak matrisi kırmızıya düşürmedi"
    # ...ve GİZLENME hücresi adıyla adına düşmeli: v3 orada 0 not veriyordu.
    gizlenme = next(
        h
        for h in GEREKCE_DENETIM_MATRISI
        if h[0] == "ek-donem-oncesi/baslik-kanonik/gercek-jenerik-baslik-ve-bozuk"
    )
    assert gizlenme[0] in kirmizi
    with mock.patch.object(bd, "_gerekce_tablosu", _v3_secimi):
        assert _notlari(gizlenme[1]) == "", "v3 bu hücrede zaten gizlemiyordu"


def test_yem_tablo_gercek_tablonun_notlarini_gizleyemez() -> None:
    """Gizlenme kolu: yem EKLEMEK gerçek tablonun notlarını EKSİLTEMEZ."""
    yemsiz = gerekce_tablosunu_boz(gerekce_basligini_jeneriklestir(TEMIZ))
    yemli = bolum_b_tablo_ekle(yemsiz, DENETLENEN_KONUM, _SAHTE_GEREKCE)
    a = {b.mesaj for b in bd.run(yemsiz, source_name="P").notlar}
    b = {b.mesaj for b in bd.run(yemli, source_name="P").notlar}
    assert a, "taban kolu boş — prob gerçek tabloyu bozmuyor"
    assert a <= b, f"yem şu notları GİZLEDİ: {sorted(a - b)}"
    assert len(b) > len(a), "yem belirsizlik notu üretmedi"


def test_iki_donem_oncesi_tablo_belirsizlik_notu_duser() -> None:
    """Dönem-öncesi iki tablo → belirsizlik NOTU, ve İKİSİ DE denetlenir."""
    ikili = bolum_b_tablo_ekle(
        gerekce_tablosunu_boz(TEMIZ), DENETLENEN_KONUM, _SAHTE_GEREKCE
    )
    mesajlar = _notlari(ikili)
    assert "2 tablo var" in mesajlar, mesajlar[:400]
    # Fail-closed: belirsizlikte hepsi denetlenir, gerçek tablo GİZLENMEZ.
    assert "tür etiketi yok" in mesajlar and "3 sütunlu satır" in mesajlar


def test_kanonik_baslik_yoksa_tanima_notu_duser() -> None:
    """Denetime giren tablo kanonik başlık taşımıyorsa NOT düşer (seçim değil)."""
    basliksiz = gerekce_basligini_jeneriklestir(TEMIZ)
    mesajlar = _notlari(basliksiz)
    assert "KANONİK başlığını taşımıyor" in mesajlar, mesajlar[:400]


def test_tablosuz_bolum_b_tanima_notu_uretmez() -> None:
    """Yanlış-pozitif kapanı: Bölüm B'de HİÇ tablo yoksa tanıma notu ÇIKMAZ.

    Gerçek araştırma çıktılarının beşi de Bölüm B'de tablo taşımıyor; tanıma
    notu oraya sızarsa bu tur her dosyaya bir uydurma not ekler.
    """
    tablosuz = kaynak(tablo=False)
    mesajlar = _notlari(tablosuz)
    assert "KANONİK başlığını taşımıyor" not in mesajlar
    assert "tablo var" not in mesajlar
    assert "gerekçeleri tablosu yok" in mesajlar


def test_gerekce_denetim_kapisi_iki_ayri_yerden_mutasyona_duyarli() -> None:
    """Mutasyon kolu: denetim kümesini ve başlık notunu AYRI AYRI sök."""
    gizleyen = bolum_b_tablo_ekle(
        gerekce_tablosunu_boz(TEMIZ), DENETLENEN_KONUM, _ALAKASIZ_4_SUTUN
    )
    assert "3 sütunlu satır" in _notlari(gizleyen)
    # (a) Denetim kümesini sök: dönem-SONRASI tablolar da denetime girsin.
    with mock.patch.object(bd, "_gerekce_tablosu", lambda bloklar: (bloklar, 1)):
        bozuk = _notlari(bolum_b_alakasiz_tablo(TEMIZ, 2))
        assert "2 sütunlu satır" in bozuk, "dönem-içi tablo yine not vermeli"
    # (b) Başlık puanını sök: her tablo başlıksız sayılır → tanıma notu.
    with mock.patch.object(bd, "_gerekce_basligi_puani", lambda satir: 0):
        assert "KANONİK başlığını taşımıyor" in _notlari(TEMIZ)


# ─── M4: ÖNEM SIRASI dayatılır ama makineyle DOĞRULANAMAZ (dürüst beyan) ────
#
# Bir önceki turun iç içe matrisinde SIRA hücreleri "sözleşme bu düzeyde sıra
# DAYATMAZ" gerekçesiyle boş bırakılmıştı. Gerekçe YANLIŞTI: pinli sözleşme
# (`_SABLON.md` satır 73-75) her listede ÖNEM SIRASI dayatır. Ölçüldü ki iki
# çağrı kalıbı takas edildiğinde rapor `gecti / 0 not` veriyor. Davranış AYNEN
# KORUNUR — önem SEMANTİK bir yargıdır, uydurma bir sıra kuralı gerçek çıktıyı
# gürültüye boğardı — ama gerekçe düzelir ve kapsam beyanına GEÇER.


def _sozlesmenin_onem_sirasi_kurali() -> str:
    """Kural UYDURULMAZ: pinlenmiş sözleşmeden okunur."""
    metin = _pinli_sablon()
    for satir in metin.splitlines():
        if "ÖNEM SIRASINA" in satir:
            return satir.strip()
    raise AssertionError("sözleşmede önem sırası kuralı bulunamadı")


def test_sozlesme_onem_sirasi_dayatir_ama_kapi_olcemez() -> None:
    """Ölçülmüş hâl: sözleşme sıra DAYATIR, mekanik kapı görmez."""
    assert "ÖNEM SIRASINA göre sırala" in _sozlesmenin_onem_sirasi_kurali()

    satirlar = TEMIZ.splitlines(True)
    i, j = _md_blok(satirlar, "### cta_kaliplari")
    maddeler = [k for k in range(i + 1, j) if satirlar[k].lstrip().startswith("- ")]
    sol, sag = maddeler[0], maddeler[1]
    satirlar[sol], satirlar[sag] = satirlar[sag], satirlar[sol]
    takas = "".join(satirlar)
    assert takas != TEMIZ

    rapor = bd.run(takas, source_name="P")
    assert rapor.sonuc == bd.SONUC_GECTI
    assert rapor.notlar == (), "uydurma bir sıra kuralı yazılmış olmalı DEĞİL"

    # Dürüst beyan: ölçülemeyen kural RAPORDA "doğrulanmadı" etiketiyle yaşar.
    birlesik = " ".join(rapor.kapsam_sinirlari)
    assert "ÖNEM SIRASI" in birlesik and "DOĞRULAYAMAZ" in birlesik
    assert "73-75" in birlesik, "beyan sözleşme satırını göstermeli"


def test_kapsam_beyani_yedinci_kalemi_tasir() -> None:
    """Beyan sayısı ALTI değil YEDİ: çit kuralının KAPSAMI ayrı bir kalem oldu.

    Kalem sayısı `CHECKS`'ten TÜRER; beyan bir kontrolün alanında yaşar ve rapor
    onu kopyalar. Yeni bir ölçüm sınırı yazılırsa bu kapı düşer ve beyanın
    güncellendiğini görünür kılar. Tur 9'da düştü: beyan yalnız DOLULUĞUN
    çit-farkında olduğunu söylüyordu, oysa kural artık YEDİ yolu kapsıyor ve
    YEDİ yolu bilinçle kapsamıyor.
    """
    beyanlar = bd.run(TEMIZ, source_name="P").kapsam_sinirlari
    turetilen = sum(len(check.kapsam_sinirlari) for check in bd.CHECKS)
    assert len(beyanlar) == turetilen == 7, beyanlar
    assert len(set(beyanlar)) == 7, "beyanlar tekrar ediyor"
    doluluk = [b for b in beyanlar if b.startswith("bolum-ve-alan-tamligi/doluluk")]
    assert len(doluluk) == 1 and "markdown TABLOSU" in doluluk[0], beyanlar
    kapsam = [b for b in beyanlar if b.startswith("bolum-ve-alan-tamligi/cit-kapsami")]
    assert len(kapsam) == 1 and "KAPSAM DIŞI" in kapsam[0], beyanlar


def test_bolum_c_serbest_duzyazisi_ARTIK_YAKALANIYOR() -> None:
    """Kapanış kanıtı: bir önceki turun TRIPWIRE'ı ateşledi ve beyan güncellendi.

    Bu test 2026-09-07'ye kadar TERSİNİ ölçüyordu — Bölüm C'nin tamamı
    `- Düz yazı, devamı https://example.com/kaynak` satırına indirilse bile
    rapor `gecti / 0 not` dönüyordu ve beyan bunu AYNEN ilan ediyordu.
    Kök çözüm koda değil SÖZLEŞMEYE yapıldı (dış depo `7964ed6`: Bölüm C sabit
    sütunlu tablo) ve kapı olumsuz çıkarımdan OLUMLU sözleşmeye geçti.

    İki ayaklı kapanış: (a) kaçış artık NOT üretiyor, (b) beyan artık kaçışı
    ilan ETMİYOR — bayat beyan, beyan olmamaktan kötüdür.
    """
    satirlar = TEMIZ.splitlines(True)
    i, j = _md_blok(satirlar, "## Bölüm C — KAYNAKLAR")
    duzyazi = "".join(
        satirlar[: i + 1]
        + ["\n- Düz yazı, devamı https://example.com/kaynak\n\n"]
        + satirlar[j:]
    )
    rapor = bd.run(duzyazi, source_name="P")
    assert rapor.sonuc == bd.SONUC_NOTLU_GECTI
    mesajlar = [b.mesaj for b in rapor.notlar if b.aile == "url-bicimi"]
    assert len(mesajlar) == 1, mesajlar
    assert "başlık satırını taşımıyor" in mesajlar[0]

    beyan = next(b for b in rapor.kapsam_sinirlari if b.startswith("url-bicimi:"))
    assert "DOĞRULANMADI" not in beyan, "bayat beyan — kaçış kapandı"
    # Beyan kaçıştan yalnız GEÇMİŞ ZAMANDA söz edebilir: vekil KALDIRILDI.
    assert "KALDIRILDI" in beyan
    # Kalan İKİ eksen dürüstçe duruyor ve ikisi de anlam yargısıdır.
    assert "ağ çağrısı yapılmaz" in beyan
    assert "ÖZETLEDİĞİ" in beyan


# ─── H7: EKLEME DEĞİŞMEZİ — tablo eklemek not KALDIRAMAZ ───────────────────
#
# Bu sınıf ALTINCI turdur ve önceki beş turun beşi de bir KURAL yazdı:
#   v1 tanıma yok · v2 ilk bitişik tablo · v3 kanonik başlıklı aday ·
#   v4 seçimi bırak (dönem-öncesi hepsi) · v5 sınırı ilk dönem başlığına çek.
# Her kural, kendi kalıbına uyan yeni bir BİLEŞİMLE kandırıldı. Altıncı kural
# YAZILMAZ; onun yerine bir DEĞİŞMEZ konur:
#
#   **Bir belgeye tablo EKLEMEK, o belgenin zaten ürettiği notları KALDIRAMAZ.**
#
# Bu bir sezgisel değil bir ÖZELLİKTİR: hangi sınır kuralı yürürlükte olursa
# olsun geçerlidir ve yeni bileşimlerle kandırılamaz, çünkü test bileşimleri
# ÜRETİR ve özelliği doğrular.
#
# **İstisna MUTLAK DEĞİL, İLKELİDİR.** "Hiçbir not kaybolamaz" YANLIŞ bir
# ifadedir: meşru bir gerekçe tablosu eklemek "gerekçe tablosu YOK" notunu
# HAKLI OLARAK kaldırır. Kapsam İLKEDEN türer: bir ekleme yalnız KENDİ
# VARLIĞININ YANLIŞLADIĞI iddiaları düşürebilir — bunlar bir BLOĞA ait değil,
# KÜMENİN bütünü hakkındaki YOKLUK iddialarıdır ("kapta içerik yok" · "gerekli
# yerde tablo yok"). Bir bloğun KENDİ içeriği hakkındaki iddialar (satırı ·
# sütunu · başlığı) istisnanın DIŞINDADIR: o blok hâlâ oradadır. Kapalı liste
# modülün SÖZLEŞMESİDİR (`bd.kap_iddiasi_mi` — bulgunun ÜRETİLDİĞİ yerde
# verilen kategori), testin elle yazdığı bir liste DEĞİL; mesaj METNİ okunmaz.
#
# Değişmez İKİ katmanda ölçülür:
#   Katman 1 — YAPISAL, istisnasız: `_gerekce_tablosu` MONOTONdur (blok
#              eklemek denetim kümesinden blok ÇIKARAMAZ). Üretilmiş BLOK
#              dizileri üstünde ölçülür.
#   Katman 2 — DAVRANIŞSAL, ilkeli istisnalı: üretilmiş BELGE bileşimleri
#              üstünde `öncekiNotlar - sonrakiNotlar ⊆ istisna`.


# ── Katman 1: `_gerekce_tablosu` MONOTONdur ────────────────────────────────
#
# Blok modeli fonksiyonun KENDİ imzasından okunur: bir blok
# `(sıra, satır, dönem_sonrası)` üçlülerinden oluşur ve fonksiyon kararını
# YALNIZ `blok[0][2]`'ye (konum) bakarak verir. Blok TÜRLERİ bu iki bitten
# türer: konum (dönem öncesi · sonrası) × başlık (kanonik · jenerik).

_BLOK_TURLERI = tuple(
    itertools.product((False, True), (False, True))
)  # (dönem_sonrası, kanonik_başlık)


def _sentetik_blok(kimlik: int, donem_sonrasi: bool, kanonik: bool) -> list:
    """Ayrıştırıcının ürettiği blok biçiminde sentetik bir tablo bloğu."""
    baslik = (
        "| dönem | karar | tür | gerekçe |" if kanonik else "| a | b | c | d |"
    )
    govde = [baslik, "|---|---|---|---|", f"| kimlik-{kimlik} | x | y | z |"]
    return [(0, satir, donem_sonrasi) for satir in govde]


def _sira_ver(bloklar: list) -> list:
    """Blokları BİTİŞİK OLMAYACAK biçimde numaralandırır (blok birimi korunur)."""
    sirali, s = [], 0
    for blok in bloklar:
        sirali.append([(s + i, satir, bayrak) for i, (_, satir, bayrak) in enumerate(blok)])
        s += len(blok) + 1
    return sirali


def _blok_kimlikleri(bloklar) -> set:
    return {blok[-1][1] for blok in bloklar if blok}


def _monotonluk_bilesimleri():
    """Taban dizi × eklenen blok türü × ekleme KONUMU — hepsi üretilir."""
    for uzunluk in range(0, 4):
        for turler in itertools.product(_BLOK_TURLERI, repeat=uzunluk):
            taban = [
                _sentetik_blok(i, sonrasi, kanonik)
                for i, (sonrasi, kanonik) in enumerate(turler)
            ]
            for ek_sonrasi, ek_kanonik in _BLOK_TURLERI:
                ek = _sentetik_blok(99, ek_sonrasi, ek_kanonik)
                for yer in range(uzunluk + 1):
                    yield taban, ek, yer


MONOTONLUK_BILESIMLERI = tuple(_monotonluk_bilesimleri())


def _monotonluk_ihlali(taban, ek, yer, fonksiyon=None) -> str:
    fonksiyon = fonksiyon or bd._gerekce_tablosu
    once, _ = fonksiyon(_sira_ver(taban))
    sonra, _ = fonksiyon(_sira_ver(taban[:yer] + [ek] + taban[yer:]))
    kayip = _blok_kimlikleri(once) - _blok_kimlikleri(sonra)
    return f"ekleme kümeden blok ÇIKARDI: {sorted(kayip)}" if kayip else ""


def test_gerekce_tablosu_denetim_kumesi_monotondur() -> None:
    """Katman 1 — İSTİSNASIZ: blok eklemek denetim kümesinden blok çıkaramaz."""
    ihlaller = [
        f"uzunluk={len(taban)} yer={yer} ek={ek[0][1]!r}: {iz}"
        for taban, ek, yer in MONOTONLUK_BILESIMLERI
        if (iz := _monotonluk_ihlali(taban, ek, yer))
    ]
    assert ihlaller == [], ihlaller[:5]


def _v4_geri_donusu(bloklar):
    """Mutasyon: v4'ün fail-open geri dönüşü — dönem-öncesi boşsa HEPSİ."""
    donem_oncesi = [blok for blok in bloklar if blok and not blok[0][2]]
    if donem_oncesi:
        return donem_oncesi, len(donem_oncesi)
    return list(bloklar), 0


def test_monotonluk_kolu_mutasyona_duyarli_ve_bos_kume_degil() -> None:
    """Mutasyon + boş-küme kolu: geri dönüşü geri koy → monotonluk KIRILSIN."""
    # Boş-küme kolu: bileşim uzayı gerçekten ÜRETİLDİ mi?
    assert len(MONOTONLUK_BILESIMLERI) == sum(
        len(_BLOK_TURLERI) ** n * len(_BLOK_TURLERI) * (n + 1) for n in range(4)
    ) == 1252, len(MONOTONLUK_BILESIMLERI)
    # ...ve taban dizilerin bir kısmı GERÇEKTEN boş-olmayan bir küme üretiyor.
    dolu = sum(
        1
        for taban, _, _ in MONOTONLUK_BILESIMLERI
        if bd._gerekce_tablosu(_sira_ver(taban))[0]
    )
    assert dolu > 0, "hiçbir taban dizi denetim kümesi üretmiyor — kol BOŞA yeşil"
    # Mutasyon kolu.
    kirilan = [
        f"uzunluk={len(taban)} yer={yer}"
        for taban, ek, yer in MONOTONLUK_BILESIMLERI
        if _monotonluk_ihlali(taban, ek, yer, _v4_geri_donusu)
    ]
    assert kirilan, "v4 geri dönüşü monotonluğu KIRMADI — mutasyon ölçmüyor"


# ── Katman 2: BELGE bileşimleri ────────────────────────────────────────────
#
# Eksenler ayrıştırıcının KENDİ belge modelinden türer, bulunan örneklerden
# DEĞİL. Beş turun her biri tek bir ekseni tek başına oynattığı için delik
# BİLEŞİMDE kaldı; bu yüzden eksenler ÇAPRAZ çarpılır.

# Eksen 1 — ara başlığın markdown DÜZEYİ. Ayrıştırıcının iki rejimi vardır ve
# sınır `_UST_BASLIK_RE`'nin KENDİ deseninden okunur (elle sayılmaz): düzey
# 1..N bölüm KAPATIR, N+1 ve üstü bölüm İÇİ sayılır. Her rejimden iki değer.
_UST_SINIR = int(re.search(r"#\{1,(\d+)\}", bd._UST_BASLIK_RE.pattern).group(1))
ARA_BASLIK_DUZEYLERI = (1, _UST_SINIR, _UST_SINIR + 1, _UST_SINIR + 2)

# Eksen 2 — ara başlığın YERİ: gerçek tablonun iki yanı, ya da hiç yok.
ARA_BASLIK_YERLERI = ("yok", "tablo-oncesi", "tablo-sonrasi")

# Eksen 3 — `_ilk_donem_baslangici`'nın İKİ dalı.
ILK_DONEM_BASLIGI = ("var", "yok")

# Eksen 4 — eklenen tablonun YERİ: ayrıştırıcının Bölüm B işaretlerinden türer
# (bölüm başı · gerçek tablonun iki yanı · ilk dönem yuvasının içi).
YEM_YERLERI = ("bolum-b-basi", "tablo-oncesi", "tablo-sonrasi", "donem-icinde")

# Eksen 5 — eklenen tablonun BAŞLIĞI (`_EK_TABLOLAR`'dan; ikinci liste yok).
YEM_BASLIKLARI = tuple(_EK_TABLOLAR)

# Eksen 6 — GERÇEK gerekçe tablosunun durumu (`_GERCEK_TABLO_DURUMLARI`).


def _b_bolgesi(satirlar: list[str]) -> tuple[int, int]:
    """Bölüm B'nin FİZİKSEL satır aralığı (`## Bölüm B` → `## Bölüm C`).

    Ayrıştırıcının BÖLÜMLEMESİ kullanılamaz: bileşimlerin bir kısmı Bölüm B'yi
    bilerek kapatan (düzey 1-2) bir ara başlık taşır ve o hâlde ayrıştırıcı
    tabloyu Bölüm B'de GÖRMEZ — ekleme yine de fiziksel olarak oraya yapılır.
    """
    bas = next(i for i, s in enumerate(satirlar) if s.startswith("## Bölüm B"))
    son = next(i for i, s in enumerate(satirlar) if s.startswith("## Bölüm C"))
    return bas, son


def _gercek_tablo_araligi(satirlar: list[str]) -> tuple[int, int]:
    """Bölüm B'deki İLK bitişik `|` bloğu — gerçek gerekçe tablosu."""
    bas, son = _b_bolgesi(satirlar)
    izler = [i for i in range(bas, son) if satirlar[i].lstrip().startswith("|")]
    assert izler, "bileşim gerçek gerekçe tablosu olmadan kurulamaz"
    ilk = izler[0]
    bitis = ilk
    while bitis + 1 in izler:
        bitis += 1
    return ilk, bitis + 1


def _bilesim_metni(
    duzey: int, ara_yeri: str, ilk_baslik: str, yem_yeri: str, yem: str | None, bozan
) -> str:
    """Bir bileşimin belgesini KURAR (yem `None` ise yemsiz taban)."""
    satirlar = bozan(TEMIZ).splitlines(True)
    if ilk_baslik == "yok":
        i = next(
            k for k, s in enumerate(satirlar) if s.strip() == f"### {_DONEM_ADLARI[0]}"
        )
        satirlar = satirlar[:i] + satirlar[i + 1 :]
    if ara_yeri != "yok":
        bas, bitis = _gercek_tablo_araligi(satirlar)
        k = bas if ara_yeri == "tablo-oncesi" else bitis
        satirlar = satirlar[:k] + ["\n", "#" * duzey + " Ara ölçüm başlığı\n", "\n"] + satirlar[k:]
    if yem is None:
        return "".join(satirlar)
    b_bas, b_son = _b_bolgesi(satirlar)
    tablo_bas, tablo_bitis = _gercek_tablo_araligi(satirlar)
    if yem_yeri == "bolum-b-basi":
        k = b_bas + 1
    elif yem_yeri == "tablo-oncesi":
        k = tablo_bas
    elif yem_yeri == "tablo-sonrasi":
        k = tablo_bitis
    else:
        k = next(
            i for i in range(b_bas, b_son) if satirlar[i].startswith("mesaj_ekseni")
        ) + 1
    ek = ["\n"] + list(_EK_TABLOLAR[yem]) + ["\n"]
    return "".join(satirlar[:k] + ek + satirlar[k:])


def _bilesim_uzayi():
    """Altı eksenin ÇAPRAZ çarpımı; dejenere hücreler bilinçle ELENİR."""
    for ara_yeri in ARA_BASLIK_YERLERI:
        # Ara başlık YOKKEN düzey ekseninin karşılığı yoktur: aynı belgeyi dört
        # kez üretmek kapsamı BÜYÜTMEZ, yalnız sayıyı şişirir.
        duzeyler = ARA_BASLIK_DUZEYLERI if ara_yeri != "yok" else (ARA_BASLIK_DUZEYLERI[0],)
        for duzey in duzeyler:
            for ilk_baslik in ILK_DONEM_BASLIGI:
                for yem_yeri in YEM_YERLERI:
                    for yem in YEM_BASLIKLARI:
                        for durum, bozan, _ in _GERCEK_TABLO_DURUMLARI:
                            ad = (
                                f"ara-{ara_yeri}-d{duzey}/ilkbaslik-{ilk_baslik}/"
                                f"yem-{yem_yeri}-{yem}/gercek-{durum}"
                            )
                            yemsiz = _bilesim_metni(
                                duzey, ara_yeri, ilk_baslik, yem_yeri, None, bozan
                            )
                            yemli = _bilesim_metni(
                                duzey, ara_yeri, ilk_baslik, yem_yeri, yem, bozan
                            )
                            yield ad, yemsiz, yemli


EKLEME_BILESIMLERI = tuple(_bilesim_uzayi())


# ─── NOT KÜMESİ ÖNBELLEĞİ ─────────────────────────────────────────────────
#
# Aynı belge, çit süpürmeleri boyunca defalarca AYNI sonuç için baştan analiz
# ediliyordu. ÖLÇÜLDÜ (çit testleri, 2026-09-09): 18011 `bd.run` çağrısının
# 8154'ü tekrar (%45.3); süre 115.48s -> 70.64s. Önbellek hiçbir hücre SİLMEZ,
# hiçbir iddiayı zayıflatmaz — yalnız aynı girdinin ikinci analizini atlar.
#
# ANAHTAR MODÜL DURUMUNU TAŞIMAK ZORUNDA: bu dosya `bd`nin iç parçalarını
# mock'luyor ve mock ALTINDA alınan sonuç mock kalkınca GEÇERSİZDİR. Sessiz
# yanlış-yeşil buradan doğardı. Parmak izi iki mock biçimini de kapsar:
# (a) modül özniteliği (`mock.patch.object(bd, ...)`), (b) modülün TUTTUĞU
# nesnenin özniteliği (`mock.patch.object(bd._MD, "parse", ...)`).
# Kapsamın YETERLİ olduğu testle kapılanır: `test_onbellek_anahtari_bu_dosyanin
# _BUTUN_mock_bicimlerini_ayirt_eder` bu dosyanın KENDİ kaynağını ayrıştırıp
# her `mock.patch` hedefinin iki biçimden birine düştüğünü ölçer.
_NOT_ONBELLEGI: dict[str, frozenset] = {}
_ONBELLEK_PARMAK_IZI: tuple | None = None


def _mock_hedefleri_bu_dosyada() -> tuple[str, ...]:
    """`bd.<nesne>` üstünde mock'lanan nesneler — DOSYANIN KAYNAĞINDAN türer.

    Elle liste TUTULMAZ: yeni bir `mock.patch.object(bd.<X>, ...)` yazan gün
    parmak izi kendiliğinden genişler. Liste elle tutulsaydı bayatlar ve
    bayatlığı ancak sessiz bir yanlış-yeşille anlaşılırdı.
    """
    import ast

    adlar = set()
    for dugum in ast.walk(ast.parse(Path(__file__).read_text())):
        if not isinstance(dugum, ast.Call):
            continue
        if not ast.unparse(dugum.func).startswith(("mock.patch", "patch")):
            continue
        hedef = ast.unparse(dugum.args[0])
        if hedef.startswith("bd."):
            adlar.add(hedef[len("bd.") :])
    return tuple(sorted(adlar))


_MOCK_NESNELERI = _mock_hedefleri_bu_dosyada()


def _bd_parmak_izi() -> tuple:
    """`bd`nin mock'lanabilir durumunun kimliği — değişirse önbellek düşer."""
    return (
        tuple((ad, id(deger)) for ad, deger in vars(bd).items()),
        tuple(
            (
                ad,
                tuple(
                    (alan, id(deger))
                    for alan, deger in vars(getattr(bd, ad)).items()
                ),
            )
            for ad in _MOCK_NESNELERI
        ),
    )


def _not_kumesi(metin: str) -> set:
    """Bulguların KENDİSİ — kategori mesaj metninde değil bulgunun üstündedir."""
    global _ONBELLEK_PARMAK_IZI
    parmak = _bd_parmak_izi()
    if parmak != _ONBELLEK_PARMAK_IZI:
        _NOT_ONBELLEGI.clear()
        _ONBELLEK_PARMAK_IZI = parmak
    onbellekli = _NOT_ONBELLEGI.get(metin)
    if onbellekli is None:
        onbellekli = frozenset(bd.run(metin, source_name="P").notlar)
        _NOT_ONBELLEGI[metin] = onbellekli
    return set(onbellekli)


def test_onbellek_anahtari_bu_dosyanin_BUTUN_mock_bicimlerini_ayirt_eder() -> None:
    """ÖNBELLEK KAPISI — parmak izi bu dosyadaki HER mock biçimini görüyor mu?

    Desen KAVRAMDAN türer, bulunan örnekten değil: dosyanın KENDİ kaynağı
    ayrıştırılır ve her `mock.patch*` çağrısının hedefi çıkarılır. Hedef ya
    `bd` modülünün bir özniteliğidir (parmak izinin birinci ayağı) ya da
    `bd.<nesne>`nin bir özniteliğidir (ikinci ayak). Üçüncü bir biçim çıkarsa
    -- başka bir modül mock'lanırsa ya da `bd`den iki kat derine inilirse --
    bu test KIRILIR ve önbelleğin anahtarı o gün genişletilir.

    TRIPWIRE, beyan DEĞİL: kapsam iddiası bayatlarsa burada patlar.
    """
    import ast

    kaynak = Path(__file__).read_text()
    hedefler = []
    for dugum in ast.walk(ast.parse(kaynak)):
        if not isinstance(dugum, ast.Call):
            continue
        ad = ast.unparse(dugum.func)
        if not ad.startswith(("mock.patch", "patch")):
            continue
        assert ad.endswith(".object"), f"string hedefli mock: {ad}"
        hedefler.append(ast.unparse(dugum.args[0]))

    assert len(hedefler) >= 30, len(hedefler)
    modul_ustu = {h for h in hedefler if h == "bd"}
    nesne_ustu = {h for h in hedefler if h.startswith("bd.")}
    kapsanmayan = set(hedefler) - modul_ustu - nesne_ustu
    assert kapsanmayan == set(), sorted(kapsanmayan)
    # İkinci ayak GERÇEKTEN kullanılıyor -- kol boşa yeşil değil.
    assert nesne_ustu, "nesne üstü mock kalmadıysa ikinci ayak ölçmüyor"
    # ...ve parmak izi TAM O kümeyi taşıyor (iki taraf aynı kaynaktan türer,
    # ama burada BAĞIMSIZ olarak yeniden çıkarılır).
    assert set(_MOCK_NESNELERI) == {h[len("bd.") :] for h in nesne_ustu}
    # ...ve hepsi TEK kat derinde: `bd.a.b` parmak izinin dışında kalırdı.
    assert all(h.count(".") == 1 for h in nesne_ustu), sorted(nesne_ustu)


def test_onbellek_mock_altinda_BAYAT_sonuc_dondurmez() -> None:
    """DAVRANIŞSAL KOL: aynı metin, mock'lu ve mock'suz FARKLI cevap verir.

    Parmak izinin iki ayağı da AYRI AYRI ölçülür. Kol, önbelleği önce
    ISITARAK kurar: bayat sonuç ancak dolu önbellek üstünde görülebilir.
    """
    # PROB SEÇİMİ ÖLÇÜLDÜ: `TEMIZ` hiç not üretmez ve mock'lu hâli de üretmez;
    # o metinle kol BOŞA yeşil olurdu. Kap boşaltılmış belge not ÜRETİR.
    metin = KAP_AILELERI[0][2](TEMIZ)
    temiz_notlar = _not_kumesi(metin)  # önbellek ISINDI
    assert temiz_notlar, "prob not üretmiyor -- kol boşa yeşil olurdu"

    # (a) modül özniteliği mock'u -- rapor ihlalleri susturulunca sonuç DEĞİŞİR
    with mock.patch.object(bd, "CHECKS", ()):
        mocklu = _not_kumesi(metin)
    assert mocklu != temiz_notlar, "modül mock'u önbelleği düşürmedi"

    # (b) modülün TUTTUĞU nesnenin özniteliği -- ayrıştırıcı düşerse belge
    #     TAMAMEN literal sayılır ve bütün bölümler EKSİK görünür.
    with mock.patch.object(bd._MD, "parse", side_effect=RecursionError):
        nesne_mocklu = _not_kumesi(metin)
    assert nesne_mocklu != temiz_notlar, "nesne mock'u önbelleği düşürmedi"

    # ...ve mock kalkınca ESKİ cevap geri gelir (tek yönlü bozulma yok).
    assert _not_kumesi(metin) == temiz_notlar


def _mesajlari(bulgular) -> set:
    return {bulgu.mesaj for bulgu in bulgular}


def _mesru_gerekce_tablosu_ekle(metin: str) -> str:
    """Bölüm B'nin başına sözleşmeye UYAN gerçek bir gerekçe tablosu koyar."""
    satirlar = metin.splitlines(True)
    b_bas, _ = _b_bolgesi(satirlar)
    mesru = ["\n", "| dönem | karar | tür | gerekçe |\n", "|---|---|---|---|\n"] + [
        f"| {ad} | secildi | {tur} | Gerekce cumlesi. |\n"
        for ad, tur in zip(_DONEM_ADLARI[:6], _DONEM_TURLERI[:6])
    ] + ["\n"]
    return "".join(satirlar[: b_bas + 1] + mesru + satirlar[b_bas + 1 :])


def _ekleme_ihlali(yemsiz: str, yemli: str) -> str:
    """Değişmez ihlali (boş metin = bileşim yeşil)."""
    once, sonra = _not_kumesi(yemsiz), _not_kumesi(yemli)
    kayip = {bulgu for bulgu in once - sonra if not bd.kap_iddiasi_mi(bulgu)}
    return (
        f"ekleme şu notları KALDIRDI: {sorted(_mesajlari(kayip))}" if kayip else ""
    )


@pytest.mark.parametrize(
    "yemsiz,yemli",
    [(b[1], b[2]) for b in EKLEME_BILESIMLERI],
    ids=[b[0] for b in EKLEME_BILESIMLERI],
)
def test_tablo_eklemek_var_olan_notu_kaldiramaz(yemsiz: str, yemli: str) -> None:
    """Katman 2 — DEĞİŞMEZ: eklemeden önceki notlar sonrakinin ALT KÜMESİDİR."""
    assert _ekleme_ihlali(yemsiz, yemli) == ""


def test_ekleme_bilesim_uzayi_bos_kume_ve_taban_kollari() -> None:
    """Boş-küme kolu: uzay gerçekten ÜRETİLDİ mi, tabanlar BOŞA yeşil mi?"""
    beklenen = (
        (1 + 2 * len(ARA_BASLIK_DUZEYLERI))
        * len(ILK_DONEM_BASLIGI)
        * len(YEM_YERLERI)
        * len(YEM_BASLIKLARI)
        * len(_GERCEK_TABLO_DURUMLARI)
    )
    assert len(EKLEME_BILESIMLERI) == beklenen == 432, len(EKLEME_BILESIMLERI)
    adlar = [b[0] for b in EKLEME_BILESIMLERI]
    assert len(set(adlar)) == len(adlar), "bileşimler ÇAKIŞIYOR"
    # Her bileşim GERÇEKTEN bir tablo EKLİYOR ve ekleme belgeyi değiştiriyor.
    for ad, yemsiz, yemli in EKLEME_BILESIMLERI:
        assert yemli != yemsiz, f"{ad}: yem eklenmedi"
        assert len(yemli.splitlines()) > len(yemsiz.splitlines()), ad
    # Taban BOŞA yeşil DEĞİL. Ölçüldü: 432 bileşimin 392'sinde yemsiz belge
    # zaten not üretiyor; boş kalan 40'ın HEPSİ `gercek-saglam` — yani gerçek
    # tablosu bozulmamış, hiç not üretmeyen TEMİZ taban (bu hücrelerde değişmez
    # bedavaya sağlanır ve kapı onları saymaz).
    dolu = [ad for ad, yemsiz, _ in EKLEME_BILESIMLERI if _not_kumesi(yemsiz)]
    # 368 → 392 (4. ayak, ölçüldü). Yem/taban bileşimlerinin bir kısmı İLK DÖNEM
    # BAŞLIĞINI kaldırıyor; Bölüm C'nin `alan/dönem` hücresi artık Bölüm B'de
    # GERÇEKTEN işlenmiş dönemlere bağlı olduğu için o tabanlar da not üretmeye
    # başladı. Kapsam kaybı değil, ARTIŞ — ve boş kalanların hepsi hâlâ
    # `gercek-saglam`.
    assert len(dolu) == 392, len(dolu)
    bos = [ad for ad in adlar if ad not in set(dolu)]
    assert len(bos) == 40 and all(ad.endswith("/gercek-saglam") for ad in bos), bos[:5]
    # ...ve tabanların çoğunda not BLOĞA AİTTİR (istisna dışı) — yoksa değişmez
    # yalnız küme iddialarını ölçer ve asıl sınıfı hiç sınamazdı. Ölçüldü: 320 →
    # 392 (4. ayak). Artık not üreten HER tabanda bloğa ait bir not da var:
    # Bölüm C'nin `alan/dönem` üyelik notu SATIR düzeyindedir, kap iddiası
    # değildir, ve ilk dönem başlığını kaldıran tabanların hepsinde ateşliyor.
    bloga_ait = [
        ad
        for ad, yemsiz, _ in EKLEME_BILESIMLERI
        if any(not bd.kap_iddiasi_mi(bulgu) for bulgu in _not_kumesi(yemsiz))
    ]
    assert len(bloga_ait) == 392, len(bloga_ait)


def test_ekleme_degismezi_mutasyona_duyarli() -> None:
    """Mutasyon kolu: v4'ün fail-open geri dönüşünü geri koy → KIRMIZI düşsün."""
    with mock.patch.object(bd, "_gerekce_tablosu", _v4_geri_donusu):
        kirmizi = [
            ad
            for ad, yemsiz, yemli in EKLEME_BILESIMLERI
            if _ekleme_ihlali(yemsiz, yemli)
        ]
    assert kirmizi, "geri dönüşü geri koymak değişmezi KIRMADI"
    # Ölçüldü: SEKİZ hücre kırılır ve hepsi aynı imzayı taşır — ilk dönemin
    # başlığı YOK, gerçek tablonun üstünde bölüm-İÇİ (düzey 3+) bir ara başlık
    # var, yem Bölüm B'nin başında. O hâlde gerçek tablo dönem bölgesine düşer
    # ve v4'ün geri dönüşü onu ancak dönem-öncesi bir yem YOKKEN denetliyordu.
    assert len(kirmizi) == 8, kirmizi
    assert all("/ilkbaslik-yok/" in ad for ad in kirmizi), kirmizi
    assert all("/yem-bolum-b-basi-" in ad for ad in kirmizi), kirmizi


# ── İstisnanın KAPSAMI: YAPISAL kategori, metin eşleştirmesi DEĞİL ─────────
#
# Tur 6 muafiyeti mesaj ÖNEKİ listesiyle tanımlıyordu. Bağ iki yönde de
# ölçüldü ve kırılgandı; bu bölüm kapanışı SINAR, iddia etmez.

def _tur6_korpusu() -> tuple[str, ...]:
    """Tur 6'nın önek listesinin YAZILDIĞI belgeler — eşdeğerlik tabanı."""
    return (
        kaynak(tablo=False),  # hiç tablo yok → "gerekli yerde tablo yok"
        tabloyu_donemlerden_sonraya_tasi(TEMIZ),  # yalnız dönem-sonrası tablo
        gerekce_basligini_jeneriklestir(TEMIZ),  # denetime giren blok başlıksız
        bolum_b_tablo_ekle(TEMIZ, DENETLENEN_KONUM, _SAHTE_GEREKCE),  # iki tablo
    ) + tuple(bolum_bosalt(TEMIZ, harf) for harf in bd.BOLUM_HARFLERI)


def _kap_korpusu() -> tuple[str, ...]:
    """KAP iddiası üretebilen belgeler — HER beyan yolunu ateşlemek için.

    Tur 6 korpusuna Bölüm C'yi "dolu ama eşlemesiz" bırakan belge EKLENİR: o
    yolu önek listesi KAÇIRMIŞTI ve hiçbir bileşim onu üretmiyordu. 4. AYAK
    iki yol daha açtı — başlık satırı DURUP veri satırının kalmaması, ve
    tablonun bir alan/dönem'i hiç KAPSAMAMASI; ikisi de ayrı belge ister.
    """
    return _tur6_korpusu() + (
        c_eslemesini_kaldir(TEMIZ),
        c_veri_satirlarini_kaldir(TEMIZ),
        c_ilk_satiri_kaldir(TEMIZ),
    )


def _kap_beyan_eden_fonksiyonlar() -> tuple[str, ...]:
    """`_kap(...)` çağrısı TAŞIYAN fonksiyonlar — modülün KENDİ AST'inden.

    Küme testin elle yazdığı bir liste DEĞİL: modül kaynağı ayrıştırılır ve
    `_kap` çağrısını içeren her fonksiyon adı toplanır. Yeni bir beyan yolu
    eklenirse küme kendiliğinden büyür ve aşağıdaki "hepsi ATEŞLENEBİLİR"
    kapısı o yolu da ister.
    """
    agac = ast.parse(Path(bd.__file__).read_text(encoding="utf-8"))
    adlar: list[str] = []
    for dugum in ast.walk(agac):
        if not isinstance(dugum, ast.FunctionDef) or dugum.name == "_kap":
            continue
        if any(
            isinstance(alt, ast.Call)
            and isinstance(alt.func, ast.Name)
            and alt.func.id == "_kap"
            for alt in ast.walk(dugum)
        ):
            adlar.append(dugum.name)
    return tuple(sorted(set(adlar)))


def _kap_cagri_sayisi() -> int:
    agac = ast.parse(Path(bd.__file__).read_text(encoding="utf-8"))
    return sum(
        1
        for dugum in ast.walk(agac)
        if isinstance(dugum, ast.Call)
        and isinstance(dugum.func, ast.Name)
        and dugum.func.id == "_kap"
    )


def _kap_atesleyen_fonksiyonlar(metinler) -> set[str]:
    """Korpus koşarken `_kap`'ı GERÇEKTEN çağıran fonksiyon adları."""
    gorulen: set[str] = set()
    gercek = bd._kap

    def izleyici(metin: str):
        gorulen.add(sys._getframe(1).f_code.co_name)
        return gercek(metin)

    with mock.patch.object(bd, "_kap", izleyici):
        for metin in metinler:
            bd.run(metin, source_name="P")
    return gorulen


def test_kap_kategorisi_uretim_yerinde_BEYAN_edilir() -> None:
    """Muafiyetin KAPSAMI: her beyan yolu gerçekten ATEŞLENEBİLİR olmalı.

    Fazla geniş yazılmış bir istisna = değişmezin YOKLUĞU. Küme AST'ten türer;
    ölçülmemiş bir `_kap` çağrısı sızarsa bu kapı düşer ve gerekçe ister.
    """
    beyan_eden = _kap_beyan_eden_fonksiyonlar()
    assert beyan_eden == (
        "_bolum_yapisi_ihlalleri",
        "_c_kapsama_ihlalleri",
        "_kontrol_gerekce_tablosu",
        "_kontrol_url_bicimi",
        "_tablo_sekli_ihlalleri",
    ), beyan_eden
    # SEKİZ çağrı yeri: bölüm boş · tablo yok · başlıksız sayımı · dönem-öncesi
    # sayımı · tablo dönem sonrası · Bölüm C başlık satırı yok · Bölüm C
    # tablosu veri satırsız · Bölüm C alan/dönem kapsaması eksik.
    # 4. AYAK: Bölüm C'nin TEK kap iddiası (eşleme satırı yok) ÜÇE çıktı —
    # sözleşme sabit sütunlu tabloyu dayattığı için kabın YOKLUĞU artık üç
    # ayrı yapısal soruya ayrılabiliyor.
    assert _kap_cagri_sayisi() == 8, _kap_cagri_sayisi()
    assert _kap_atesleyen_fonksiyonlar(_kap_korpusu()) == set(beyan_eden)
    # ...ve kategori BULGUYA yazılıyor: korpusta gerçekten KAP bulgusu var.
    kap_bulgulari = {
        bulgu
        for metin in _kap_korpusu()
        for bulgu in _not_kumesi(metin)
        if bd.kap_iddiasi_mi(bulgu)
    }
    # Beş bölüm kabı + kalan YEDİ çağrı yerinin birer mesajı (tablo yok · dönem
    # sonrası · başlıksız sayımı · dönem-öncesi sayımı · Bölüm C başlık satırı ·
    # Bölüm C veri satırı · Bölüm C kapsaması) = sekiz çağrı yerinin hepsi
    # ürünüyle görünür.
    assert len(kap_bulgulari) == len(bd.BOLUM_HARFLERI) + (
        _kap_cagri_sayisi() - 1
    ) == 12, sorted(_mesajlari(kap_bulgulari))
    # ...ve BLOĞA AİT notlar muafiyete sızmıyor: satır/sütun notları DOKUNULMAZ.
    bloga_ait = _not_kumesi(gerekce_tablosunu_boz(TEMIZ))
    assert bloga_ait and all(not bd.kap_iddiasi_mi(b) for b in bloga_ait), sorted(
        _mesajlari(bloga_ait)
    )


def test_her_bulgu_kapali_kategori_kumesinden_bir_deger_tasir() -> None:
    """Kategorisi beyan edilmemiş yol FAIL-CLOSED: `bloga-ait` (dokunulmaz)."""
    bulgular = {
        bulgu
        for metin in _kap_korpusu() + tuple(b[1] for b in EKLEME_BILESIMLERI[:40])
        for bulgu in _not_kumesi(metin)
    }
    assert bulgular, "korpus not üretmiyor — kol BOŞA yeşil"
    assert all(b.kategori in bd.KATEGORILER for b in bulgular)
    assert bd.Bulgu("k", "uzun-alinti", bd.SEVIYE_NOT, "m").kategori == (
        bd.KATEGORI_BLOGA_AIT
    )
    with pytest.raises(ValueError):
        bd.Bulgu("k", "uzun-alinti", bd.SEVIYE_NOT, "m", "uydurma-kategori")
    with pytest.raises(ValueError):
        bd._Mesaj("m", "uydurma-kategori")


# Tur 6'nın metin-eşleştirmeli sınıflandırıcısı — POZİTİF KONTROL olarak durur.
_ESKI_ONEKLER = (
    "Bölüm B'de dönem başlıklarından ÖNCE ",
    "Bölüm B'de gerekçe denetimine giren ",
    "Gerekçe tablosu dönem başlıklarından SONRA",
) + tuple(f"Bölüm {harf} boş" for harf in bd.BOLUM_HARFLERI)


def _eski_sinif(bulgu) -> bool:
    return bulgu.mesaj.startswith(_ESKI_ONEKLER)


def _kap_sayilari(sinif, korpus=None) -> tuple[int, ...]:
    return tuple(
        sum(1 for bulgu in _not_kumesi(metin) if sinif(bulgu))
        for metin in (korpus if korpus is not None else _tur6_korpusu())
    )


def test_onek_listesi_bir_uretim_yolunu_KACIRMISTI() -> None:
    """Ayak 1'in ölçülmüş kazancı: metin listesi TAM değildi, yapı tamdır.

    Tur 6'nın önek listesi Bölüm C eşleme kabının YOKLUK iddiasını kapsamıyordu
    — hiçbir bileşim Bölüm C'yi "dolu ama eşlemesiz" bırakmadığı için ölçülmemiş
    kalmıştı. Yapısal kategori onu üretim yerinden alır.
    """
    belge = c_eslemesini_kaldir(TEMIZ)
    kacan = [
        bulgu
        for bulgu in _not_kumesi(belge)
        if bd.kap_iddiasi_mi(bulgu) and not _eski_sinif(bulgu)
    ]
    assert len(kacan) == 1, sorted(_mesajlari(kacan))
    assert kacan[0].mesaj.startswith("Bölüm C sözleşmenin başlık satırını")
    # Tur 6 korpusunda ise iki sınıflandırıcı BİREBİR aynıdır (kapsam sessizce
    # genişlemedi/daralmadı — fark YALNIZ bu kaçan yoldur).
    assert _kap_sayilari(bd.kap_iddiasi_mi) == _kap_sayilari(_eski_sinif)


# Metin mutasyonu: KAP mesajlarının METNİ yeniden yazılır (bu oturumda iki kez
# gerçekten yapıldı). Sabit adı + yeni metin; hiçbiri eski öneklerle başlamaz.
METIN_MUTASYONLARI = (
    ("BOLUM_BOS_MESAJI", "Kap {harf} DOLDURULMAMIŞ — başlık var, içerik yok"),
    ("TABLO_YOK_MESAJI", "Gerekçe tablosu gerekli yerde YOK (yeniden yazım)"),
    ("TABLO_DONEM_SONRASI_MESAJI", "Tablo YANLIŞ konumda (yeniden yazım)"),
)


@pytest.mark.parametrize("sabit,yeni_metin", METIN_MUTASYONLARI)
def test_kategori_mesaj_metninden_BAGIMSIZDIR(sabit: str, yeni_metin: str) -> None:
    """METİN MUTASYONU: mesaj yeniden yazılınca sınıflandırma KAYMAMALI.

    Pozitif kontrol aynı mutasyonla koşar: tur 6'nın önek sınıflandırıcısı
    AYNI mutasyonda KAYAR. Kolun boşa yeşil olmadığı böyle ölçülür.
    """
    taban_yapisal = _kap_sayilari(bd.kap_iddiasi_mi)
    taban_eski = _kap_sayilari(_eski_sinif)
    # Eşdeğerlik: yapısal kategori, mutasyonsuz hâlde eski öneklerle AYNI
    # kümeyi verir — istisnanın KAPSAMI sessizce genişlemedi/daralmadı.
    assert taban_yapisal == taban_eski, (taban_yapisal, taban_eski)
    assert sum(taban_yapisal) > 0, "korpus KAP iddiası üretmiyor — kol boşa yeşil"

    with mock.patch.object(bd, sabit, yeni_metin):
        mutasyon_yapisal = _kap_sayilari(bd.kap_iddiasi_mi)
        mutasyon_eski = _kap_sayilari(_eski_sinif)
    assert mutasyon_yapisal == taban_yapisal, (mutasyon_yapisal, taban_yapisal)
    assert mutasyon_eski != taban_eski, (
        f"{sabit}: metin mutasyonu ESKİ sınıflandırıcıyı da kaydırmadı — "
        "pozitif kontrol ölçmüyor"
    )


def test_kategori_yanlis_atanirsa_kapilar_KIRMIZI_duser() -> None:
    """MUTASYON: kategoriyi yanlış ata → iki ayrı kapı kırmızı düşsün."""
    # (a) KAP → BLOK: ilkeli istisna kolu KIRILIR (meşru tablo yokluk notunu
    #     kaldırıyor ama artık dokunulmaz sayılıyor).
    tablosuz = kaynak(tablo=False)
    tablolu = _mesru_gerekce_tablosu_ekle(tablosuz)
    with mock.patch.object(bd, "_kap", lambda metin: bd._Mesaj(metin)):
        kayip = {
            b
            for b in _not_kumesi(tablosuz) - _not_kumesi(tablolu)
            if not bd.kap_iddiasi_mi(b)
        }
    assert kayip, "KAP→BLOK mutasyonu ilkeli istisna kolunu KIRMADI"

    # (b) BLOK → KAP: bloğa ait şekil notları muafiyete sızarsa kapı düşer.
    gercek = bd._tablo_sekli_ihlalleri

    def sizdiran(belge):
        return [
            bd._kap(m.metin if isinstance(m, bd._Mesaj) else m)
            for m in gercek(belge)
        ]

    with mock.patch.object(bd, "_tablo_sekli_ihlalleri", sizdiran):
        bloga_ait = _not_kumesi(gerekce_tablosunu_boz(TEMIZ))
        sizan = [b for b in bloga_ait if bd.kap_iddiasi_mi(b)]
    assert sizan, "BLOK→KAP mutasyonu sızıntı üretmedi — kol ölçmüyor"


def test_sayim_iddialari_eklemeyle_AZALMAZ() -> None:
    """İstisna "sayı DÜŞTÜ"yü örtmesin: sayım taşıyan küme iddiaları monotondur.

    Sayım taşıyan mesajlar KAP iddiası olarak beyan edilir ve istisnaya girer. O boşluğu bu kapı kapatır: sayımların KENDİSİ ölçülür ve
    ekleme ile AZALAMAZ.
    """
    dusen = []
    for ad, yemsiz, yemli in EKLEME_BILESIMLERI:
        once, sonra = bd._ayristir(yemsiz), bd._ayristir(yemli)
        if (
            sonra.gerekce_donem_oncesi_sayisi < once.gerekce_donem_oncesi_sayisi
            or sonra.gerekce_basliksiz_sayisi < once.gerekce_basliksiz_sayisi
        ):
            dusen.append(ad)
    assert dusen == [], dusen[:5]
    # Boş-küme kolu: sayımlar gerçekten OYNUYOR mu, yoksa hep sıfır mı?
    artan = sum(
        1
        for _, yemsiz, yemli in EKLEME_BILESIMLERI
        if bd._ayristir(yemli).gerekce_donem_oncesi_sayisi
        > bd._ayristir(yemsiz).gerekce_donem_oncesi_sayisi
    )
    assert artan > 0, "hiçbir bileşimde sayım artmıyor — kol BOŞA yeşil"


def test_ilkeli_istisna_mesru_tablo_yokluk_notunu_kaldirir() -> None:
    """İLKELİ İSTİSNA KOLU: değişmez FAZLA GENİŞ yazılmamalı.

    Gerekçe tablosu HİÇ olmayan bir belgeye MEŞRU bir gerekçe tablosu
    eklenince "tablo yok" notunun kalkması BEKLENEN davranıştır — ekleme o
    iddiayı YANLIŞLAR. Bu kol sabitlenmezse değişmez "hiçbir not kaybolamaz"a
    kayar ve kapı meşru davranışı ihlal sayardı.
    """
    tablosuz = kaynak(tablo=False)
    once = _not_kumesi(tablosuz)
    assert bd.TABLO_YOK_MESAJI in _mesajlari(once)

    tablolu = _mesru_gerekce_tablosu_ekle(tablosuz)

    sonra = _not_kumesi(tablolu)
    assert bd.TABLO_YOK_MESAJI not in _mesajlari(
        sonra
    ), "meşru tablo yokluk notunu kaldırmalı"
    assert sonra == set(), f"meşru tablo başka not üretti: {sorted(_mesajlari(sonra))}"
    # Kaybolan HER not bir KAP iddiası: bloğa ait bir şey düşmüş OLMAMALI.
    assert all(bd.kap_iddiasi_mi(bulgu) for bulgu in once - sonra), sorted(
        _mesajlari(once - sonra)
    )


def test_korunan_gerilemeler_olculur() -> None:
    """KORUNACAK iki gerileme kolu — tur 5 ve tur 4'ün kazanımları."""
    # (a) v5: dönem BAŞLIĞININ hemen altına konan meşru tablo 0 NOT üretir.
    baslik_alti = bolum_b_tablo_ekle(TEMIZ, "baslik-yuva-arasi", _ALAKASIZ_4_SUTUN)
    assert _notlari(baslik_alti) == "", _notlari(baslik_alti)[:400]
    # (b) v4: jenerik başlıklı BOZUK gerçek tablo + kanonik YEM → not kaybı YOK.
    yemsiz = gerekce_tablosunu_boz(gerekce_basligini_jeneriklestir(TEMIZ))
    yemli = bolum_b_tablo_ekle(yemsiz, DENETLENEN_KONUM, _SAHTE_GEREKCE)
    once, sonra = _not_kumesi(yemsiz), _not_kumesi(yemli)
    assert once, "taban boş — prob gerçek tabloyu bozmuyor"
    assert once <= sonra, f"yem şu notları GİZLEDİ: {sorted(_mesajlari(once - sonra))}"
    # (c) POZİTİF KONTROL: temiz kaynak `gecti` ve SIFIR not.
    rapor = bd.run(TEMIZ, source_name="P")
    assert rapor.sonuc == bd.SONUC_GECTI and rapor.notlar == ()


# ─── H8: BOŞ OLABİLEN KAP ekseni — tablo eklemek BOŞLUK notunu kaldıramaz ───
#
# H7 (ekleme değişmezi) bileşim uzayı yalnız GEREKÇE TABLOSU durumlarını
# oynatıyordu: gerçek tablonun bozulması, yem konumu, ara başlık düzeyi. BOŞ
# KAP durumlarını HİÇ değiştirmiyordu ve delik tam orada kaldı — ölçüldü:
# ilk dönemin `mesaj_ekseni` yuvası boşaltılınca `notlu-gecti / 1 not`, AYNI
# yuvaya bağımsız iki sütunlu bir tablo eklenince `gecti / 0 not`.
#
# Bu eksen o boyutu ekler. Kap kümesi BULUNAN ÖRNEKTEN değil, modülün KENDİ
# yapısal sabitlerinden türer — doluluk/varlık kararı verilen her aile:
#
#   * Bölüm A alanı        → bd.TEMEL_ALANLAR        (`_Yuva.dolu`)
#   * dönem yuvası         → bd.OZEL_GUN_YUVALARI    (`_Yuva.dolu`)
#   * video havuzu         → bd.VIDEO_HAVUZLARI      (adet alt sınırı)
#   * bölüm                → bd.BOLUM_HARFLERI       (`_Belge.bos_bolumler`)
#   * Bölüm C eşleme kabı  → `_Belge.c_baslik_satiri_var`
#
# İki aile bilinçle İSTİSNADIR ve sözleşme gerekçesiyle işaretlidir: sözleşme
# tabloyu Bölüm B'nin gerekçesi ve Bölüm C'nin eşlemesi olarak TANIR, dolayısıyla
# bir tablo o iki kabı gerçekten DOLDURUR. Kalan üç ailede tablo sözleşmenin
# tanıdığı bir içerik biçimi DEĞİLDİR (`bd._sozlesme_bicimli`).


def _tablo_bicimleri() -> tuple[tuple[str, tuple[str, ...]], ...]:
    """Eklenen tablonun biçim uzayı — SÖZLEŞMEDEN türer, elle yazılmaz.

    Sütun sayısı ∈ {2, sözleşmenin gerekçe tablosu sütun sayısı} × başlık ∈
    {kanonik anahtarlar, jenerik}. Kanonik başlık taşıyan yem, tanıma notunu
    beslemeyen en "meşru görünen" hâldir; iki sütunlu jenerik yem kontrolörün
    probunun ta kendisidir.
    """
    bicimler: list[tuple[str, tuple[str, ...]]] = []
    for sutun in (2, len(bd.GEREKCE_TABLOSU_SUTUNLARI)):
        for tur in ("kanonik", "jenerik"):
            basliklar = (
                list(bd.GEREKCE_TABLOSU_SUTUNLARI)[:sutun]
                if tur == "kanonik"
                else [f"olcut{i}" for i in range(1, sutun + 1)]
            )
            govde = (
                ["\n", "| " + " | ".join(basliklar) + " |\n"]
                + ["|" + "---|" * sutun + "\n"]
                + [
                    "| " + " | ".join(f"deger{i}{j}" for j in range(sutun)) + " |\n"
                    for i in (1, 2)
                ]
                + ["\n"]
            )
            bicimler.append((f"{sutun}sutun-{tur}", tuple(govde)))
    return tuple(bicimler)


TABLO_BICIMLERI = _tablo_bicimleri()


def _baslik_altina_ekle(baslik: str):
    def ekle(metin: str, tablo: tuple[str, ...]) -> str:
        satirlar = metin.splitlines(True)
        i = next(k for k, s in enumerate(satirlar) if s.strip() == baslik)
        return "".join(satirlar[: i + 1] + list(tablo) + satirlar[i + 1 :])

    return ekle


def _ilk_donem_yuva_araligi(metin: str, yuva_adi: str):
    """Yuvanın [k, m) aralığı — hem `ad` hem `ad: değer` yazımını tanır."""
    satirlar = metin.splitlines(True)
    i, j = _md_blok(satirlar, f"### {_DONEM_ADLARI[0]}")

    def yuva_basi(satir: str) -> bool:
        govde = satir.strip()
        return any(
            govde == ad or govde.startswith(f"{ad}:") for ad in bd.OZEL_GUN_YUVALARI
        )

    for k in range(i, j):
        govde = satirlar[k].strip()
        if govde == yuva_adi or govde.startswith(f"{yuva_adi}:"):
            m = k + 1
            while m < j and not yuva_basi(satirlar[m]):
                m += 1
            return satirlar, k, m
    raise AssertionError(f"dönem yuvası bulunamadı: {yuva_adi!r}")


def _kap_aileleri():
    """(aile, kap adı, boşalt, ekle, tablo_kabı_doldurur_mu) — modülden türer."""
    for ad in bd.TEMEL_ALANLAR:
        baslik = f"### {ad}"
        yield (
            "bolum-a-alani",
            ad,
            (lambda b: lambda metin: blok_bosalt(metin, b))(baslik),
            _baslik_altina_ekle(baslik),
            False,
        )
    for yuva_adi in bd.OZEL_GUN_YUVALARI:

        def bosalt(metin: str, _ad: str = yuva_adi) -> str:
            satirlar, k, m = _ilk_donem_yuva_araligi(metin, _ad)
            return "".join(satirlar[:k] + [f"{_ad}:\n"] + satirlar[m:])

        def ekle(metin: str, tablo, _ad: str = yuva_adi) -> str:
            satirlar, k, _ = _ilk_donem_yuva_araligi(metin, _ad)
            return "".join(satirlar[: k + 1] + list(tablo) + satirlar[k + 1 :])

        yield ("donem-yuvasi", yuva_adi, bosalt, ekle, False)
    for havuz in bd.VIDEO_HAVUZLARI:
        baslik = f"#### {havuz}"
        yield (
            "video-havuzu",
            havuz,
            (lambda b: lambda metin: blok_bosalt(metin, b))(baslik),
            _baslik_altina_ekle(baslik),
            False,
        )
    for harf in bd.BOLUM_HARFLERI:

        def bolum_ekle(metin: str, tablo, _h: str = harf) -> str:
            satirlar = metin.splitlines(True)
            i = next(
                k
                for k, s in enumerate(satirlar)
                if (e := _BOLUM_BASLIK_RE.match(s)) and e.group(1) == _h
            )
            return "".join(satirlar[: i + 1] + list(tablo) + satirlar[i + 1 :])

        yield (
            "bolum",
            harf,
            (lambda h: lambda metin: bolum_bosalt(metin, h))(harf),
            bolum_ekle,
            True,  # sözleşme Bölüm B gerekçesini ve Bölüm C eşlemesini TABLO olarak tanır
        )

    def c_ekle(metin: str, tablo) -> str:
        satirlar = metin.splitlines(True)
        i = next(
            k
            for k, s in enumerate(satirlar)
            if (e := _BOLUM_BASLIK_RE.match(s)) and e.group(1) == "C"
        )
        return "".join(satirlar[: i + 1] + list(tablo) + satirlar[i + 1 :])

    # 4. AYAK — bayrak True'dan FALSE'a döndü. Sözleşme Bölüm C'yi sabit sütunlu
    # tabloya çevirdiğinden beri HERHANGİ bir tablo bu kabı doldurmuyor: kabın
    # yokluk iddiası birebir başlık satırını ister. Değişmez böylece SIKILAŞTI —
    # bu kapta artık HİÇBİR notun düşmemesi beklenir, "kap iddiası düşebilir"
    # muafiyeti de dâhil.
    yield ("c-esleme-kabi", "C", c_eslemesini_kaldir, c_ekle, False)


KAP_AILELERI = tuple(_kap_aileleri())
BOS_KAP_MATRISI = tuple(
    (f"{aile}/{ad}/{bicim_adi}", bosalt, ekle, doldurur, tablo)
    for aile, ad, bosalt, ekle, doldurur in KAP_AILELERI
    for bicim_adi, tablo in TABLO_BICIMLERI
)


def _bos_kap_olcumu(bosalt, ekle, tablo):
    bos = bosalt(TEMIZ)
    return _not_kumesi(bos), _not_kumesi(ekle(bos, tablo))


def _bos_kap_ihlali(bosalt, ekle, doldurur, tablo) -> str:
    once, sonra = _bos_kap_olcumu(bosalt, ekle, tablo)
    kayip = once - sonra
    if not doldurur:
        return (
            f"tablo eklemek şu notları KALDIRDI: {sorted(_mesajlari(kayip))}"
            if kayip
            else ""
        )
    disari = [b for b in kayip if not bd.kap_iddiasi_mi(b)]
    return (
        f"istisna ailesinde BLOĞA AİT not düştü: {sorted(_mesajlari(disari))}"
        if disari
        else ""
    )


@pytest.mark.parametrize(
    "bosalt,ekle,doldurur,tablo",
    [(b[1], b[2], b[3], b[4]) for b in BOS_KAP_MATRISI],
    ids=[b[0] for b in BOS_KAP_MATRISI],
)
def test_kaba_tablo_eklemek_bosluk_notunu_kaldiramaz(
    bosalt, ekle, doldurur, tablo
) -> None:
    """Boş bir kaba TABLO koymak, o kabın boşluk/adet notunu düşüremez."""
    assert _bos_kap_ihlali(bosalt, ekle, doldurur, tablo) == ""


def test_bos_kap_ekseni_bos_kume_ve_taban_kollari() -> None:
    """Eksen gerçekten ÜRETİLDİ mi, hücreler BOŞA yeşil mi?"""
    aileler = {ad.split("/")[0] for ad, *_ in BOS_KAP_MATRISI}
    assert aileler == {
        "bolum-a-alani",
        "donem-yuvasi",
        "video-havuzu",
        "bolum",
        "c-esleme-kabi",
    }
    beklenen = (
        len(bd.TEMEL_ALANLAR)
        + len(bd.OZEL_GUN_YUVALARI)
        + len(bd.VIDEO_HAVUZLARI)
        + len(bd.BOLUM_HARFLERI)
        + 1
    ) * len(TABLO_BICIMLERI)
    assert len(BOS_KAP_MATRISI) == beklenen == 80, len(BOS_KAP_MATRISI)
    adlar = [b[0] for b in BOS_KAP_MATRISI]
    assert len(set(adlar)) == len(adlar), "hücreler ÇAKIŞIYOR"
    # Her hücre GERÇEKTEN bir kap boşaltıyor ve boşaltma NOT üretiyor.
    bossuz = [
        ad for ad, bosalt, _, _, _ in BOS_KAP_MATRISI if not _not_kumesi(bosalt(TEMIZ))
    ]
    assert bossuz == [], bossuz
    # ...ve eklenen tablo belgeyi gerçekten BÜYÜTÜYOR.
    for ad, bosalt, ekle, _, tablo in BOS_KAP_MATRISI:
        bos = bosalt(TEMIZ)
        assert len(ekle(bos, tablo).splitlines()) > len(bos.splitlines()), ad
    # İstisna aileleri BOŞA istisna değil: orada gerçekten not DÜŞÜYOR.
    dusen = [
        ad
        for ad, bosalt, ekle, doldurur, tablo in BOS_KAP_MATRISI
        if doldurur and (_bos_kap_olcumu(bosalt, ekle, tablo)[0] - _bos_kap_olcumu(bosalt, ekle, tablo)[1])
    ]
    assert len(dusen) == len(
        [ad for ad, _, _, doldurur, _ in BOS_KAP_MATRISI if doldurur]
    ), dusen


def test_bos_kap_ekseni_mutasyona_duyarli() -> None:
    """MUTASYON (Ayak 2): doluluk kontrolünü ESKİ hâline al → eksen KIRILSIN."""

    def eski_dolu(parca: str) -> bool:
        """Tur 6 hâli: boş olmayan HERHANGİ bir satır kabı doldururdu."""
        return bool(parca.strip())

    with mock.patch.object(bd, "_sozlesme_bicimli", eski_dolu):
        kirmizi = [
            ad
            for ad, bosalt, ekle, doldurur, tablo in BOS_KAP_MATRISI
            if _bos_kap_ihlali(bosalt, ekle, doldurur, tablo)
        ]
    assert kirmizi, "eski doluluk kontrolü ekseni KIRMADI — kol ölçmüyor"
    # Ölçüldü: 48 hücre kırılır ve hepsi `_Yuva.dolu` okuyan İKİ aileden gelir
    # (8 alan + 4 yuva) × 4 tablo biçimi. Video havuzu ailesi bu sınıfa HİÇ açık
    # DEĞİLDİ — orada boşluk `essiz_maddeler` ile MADDE sayılarak ölçülür ve bir
    # tablo satırı madde değildir; bölüm ve Bölüm C aileleri ise ilan edilmiş
    # istisnadır. Dürüst kayıt: mutasyon kolunun kapsamı 80 hücrenin 48'idir.
    assert len(kirmizi) == 48, len(kirmizi)
    assert all(
        ad.startswith(("bolum-a-alani/", "donem-yuvasi/")) for ad in kirmizi
    ), kirmizi


def test_sozlesme_bicimli_kabul_kumesi_sozlesmeden_turer() -> None:
    """Kabul kümesi ADIM 3 + BİÇİM KURALLARI'ndan okunur; aşırı daraltma YOK."""
    # Sözleşmenin TANIDIĞI üç biçim kabul edilir.
    assert bd._sozlesme_bicimli("Sevgililer Günü icin duygusal eksen.")  # düz yazı
    assert bd._sozlesme_bicimli("- [an-1] + [urun bagi] acilis kalibi")  # madde
    assert bd._sozlesme_bicimli(bd.BILINCLI_BOS)  # resmî bilinçli boş
    assert bd._sozlesme_bicimli("  #### alt basligin altinda duz yazi")
    # Sözleşmenin TANIMADIĞI markdown blok yapıları kabı doldurmaz.
    assert not bd._sozlesme_bicimli("| olcut | deger |")
    assert not bd._sozlesme_bicimli("|---|---|")
    assert not bd._sozlesme_bicimli("---")
    assert not bd._sozlesme_bicimli("```")
    assert not bd._sozlesme_bicimli("   ")
    # TRIPWIRE (satır düzeyi) — ilan edilen açık biçimlerin AÇICI satırı hâlâ
    # sözleşme biçimli sayılır. Kalemler `bd.ACIK_BLOK_BICIMLERI`'nden TÜRER;
    # ikinci bir liste yazılmaz. Uçtan uca ayağı `test_acik_bicim_envanteri_*`.
    for _ad, _govde in bd.ACIK_BLOK_BICIMLERI:
        assert bd._sozlesme_bicimli(_govde[0]), _ad
    # ...ve DİLSİZ çitin GÖVDESİ satır düzeyinde hâlâ sözleşme biçimlidir:
    # kapatma satırda DEĞİL, dizide yapılır (`_citsiz_satirlar`).
    assert bd._sozlesme_bicimli("print(42)")
    # ...ve eleme DİZİ üstünde, MASKELİ girdiyle yapılır: `_citsiz_satirlar`
    # tur 11'den beri hesap yapmaz, yalnız SÜZER (`_maskeli_satirlar` hesaplar).
    assert bd._citsiz_satirlar(bd._maskeli_satirlar("```\nprint(42)\n```\n")) == []
    # ...ve K-120 muafiyeti ile adet sayımı SAĞLAM kalır (yanlış-pozitif yok).
    assert bd.run(kaynak(anma_donemi="resmi"), source_name="P").sonuc == (
        bd.SONUC_GECTI
    )
    assert bd.run(TEMIZ, source_name="P").notlar == ()


# ─── H9: DİLSİZ kod çiti BLOĞU sözleşme yüzeylerinde SAYILMAZ ──────────────
#
# H8 ekseni "boş olabilen kap"ı TABLO ile yokluyordu ve kapı tablo için
# kapanmıştı. Tur 8'de ölçüldü ki aynı kap bir KOD ÇİTİ ile hâlâ doluyordu —
# çünkü `_sozlesme_bicimli` satıra TEK TEK bakar ve bir kod bloğu DİZİ gerektirir.
# O tur DOLULUK yolunu kapattı.
#
# **Tur 9 — KARDEŞ SİTE SÜPÜRMESİ.** Kural kurulmuştu ama yalnız TEK yola
# bağlıydı; AYNI yuva içeriğini okuyan kardeş yollar çit-farkında DEĞİLDİ:
#
#     cta_kaliplari bosaltilmis                     notlu-gecti  not=2
#       * `cta_kaliplari` alanı boş
#       * `cta_kaliplari` 0 madde taşıyor, sözleşme alt sınırı 5
#     AYNI alana DİLSİZ çit içinde 5 madde konmuş    notlu-gecti  not=3
#       * `cta_kaliplari` alanı boş
#       * cta_kaliplari: madde işareti olmayan içerik satırı — ... (x2)
#       [KAYBOLDU] `cta_kaliplari` 0 madde taşıyor, sözleşme alt sınırı 5
#
# **YÖNTEM DERSİ, eksenin kendisi kadar önemli:** not SAYISI 2 → 3 ARTMIŞTI ve
# sayı karşılaştırması kapanışı YANLIŞ gösteriyordu. Kayıp ancak mesaj KÜMELERİ
# farkıyla göründü. Bu yüzden bu eksenin kapanış kanıtı SAYI DEĞİL, KÜME farkıdır
# (`_cit_kaybi` küme döner; hiçbir kol sayı karşılaştırmaz).
#
# Eksen SİLİNMEDİ, İKİ yönde GENİŞLETİLDİ:
#
#   (a) KAP ekseni: 12 doluluk kabı → `KAP_AILELERI`'nin TAMAMI (15 kap; video
#       havuzu · bölüm · Bölüm C eşleme kabı eklendi) — çünkü çit onları da
#       etkiliyordu ve tablo etkilemediği için dışarıda bırakılmışlardı.
#   (b) GÖVDE ekseni: `maddeli` ve `tablolu` gövdeler eklendi — sayım ve tanıma
#       yollarını YALNIZ onlar yoklar. Eski üç gövde (boş · sözcüklü · sözcüksüz)
#       hiç madde/tablo taşımıyordu, dolayısıyla adet ve tablo yollarındaki
#       kaybı GÖREMEZDİ. Bu, eksenin kör noktasıydı.
#
#     dil etiketi (yok · var) × gövde (boş · sözcüklü · sözcüksüz · maddeli ·
#                             tablolu) × kapanış (kapalı · kapanmamış)
#
# Beklenti boyuttan TÜRER: DİLSİZ çit hiçbir bileşimde, hiçbir kapta not
# düşüremez. DİLLİ çit ilan edilmiş AÇIK kalemdir ve ŞEFFAFTIR: aynı gövde ÇİTSİZ
# konsaydı hangi notları kaldırıyorsa onları kaldırmak ZORUNDADIR.
#
# **Tur 10 — GİRİNTİ/BAĞLAM ve AYIRAÇ BİÇİMİ.** Eksen üç boyutluyken bir kayıp
# daha maskeliydi: çit ayıracının SOLUNDA ne olduğu hiç sorulmuyordu. Ölçüldü,
# aynı yuva, mesaj KÜMESİ farkıyla:
#
#     yalniz '- ```' satiri                 kayip=0  [KORUNDU]
#     '- ```' + '  print(42)' + '  ```'     kayip=1  [KAYBOLDU]
#     ic ice madde '  - ```' + govde        kayip=1  [KAYBOLDU]
#     2 ve 4 bosluk girintili cit           kayip=0  [KORUNDU]
#
# Yani GİRİNTİ zaten çalışıyordu (`^\s*`), açık olan MADDE BAĞLAMIYDI. Ayrıca
# eksen bugüne dek yalnız ÜÇLÜ BACKTICK egzersiz ediyordu; CommonMark'ın tanıdığı
# tilde ve üçten uzun ayıraç hiç bir hücrede geçmiyordu. İki boyut EKLENDİ:
#
#     dil (yok · var) × gövde (boş · sözcüklü · sözcüksüz · maddeli · tablolu)
#       × kapanış (kapalı · kapanmamış)
#       × bağlam (girintisiz · 2 boşluk · 4 boşluk · madde işaretli · iç içe madde)
#       × ayıraç (backtick 3 · backtick 4 · tilde 3)
CIT_BOYUTLARI = {
    "dil": ("dilsiz", "dilli"),
    "govde": ("bos", "sozcuklu", "sozcuksuz", "maddeli", "tablolu", "c-tablolu"),
    "kapanis": ("kapali", "kapanmamis"),
    "baglam": (
        "girintisiz",
        "iki-bosluk",
        "madde-isaretli",
        "ic-ice-madde",
        "yildiz-madde",
        "arti-madde",
        "sirali-liste",
        "bir-bosluk-kok",
        "uc-bosluk-kok",
    ),
    "isaret": ("backtick3", "backtick4", "tilde3"),
}
# `maddeli` gövde en büyük alan alt sınırını (gorsel_kodlar >= 20) AŞACAK kadar
# ESSİZ madde taşır — sayım yolundaki kayıp ancak alt sınır SAĞLANDIĞINDA görülür.
_CIT_GOVDELERI = {
    "bos": (),
    "sozcuklu": ("print(42)\n",),
    "sozcuksuz": ("+++\n",),
    "maddeli": tuple(f"- cit maddesi {i:02d}\n" for i in range(1, 21)),
    "tablolu": (
        "| " + " | ".join(bd.GEREKCE_TABLOSU_SUTUNLARI) + " |\n",
        "|" + "---|" * len(bd.GEREKCE_TABLOSU_SUTUNLARI) + "\n",
        "| Sevgililer Günü | secildi | karma | Gerekce cumlesi. |\n",
    ),
    # 4. AYAK — ALTINCI gövde. Sözleşme Bölüm C'yi sabit sütunlu tabloya
    # çevirince (dış depo `7964ed6`) o kabı dolduran TEK içerik BU tablo oldu:
    # bir madde satırı ya da gerekçe-biçimli bir tablo artık kabı doldurmuyor.
    # Gövde EKLENMEZSE `c-esleme-kabi` temsilcisi eksende SESSİZCE VACUOUS'a
    # düşerdi (ölçüldü: dilli kayıp 1056 → 912, dilsiz kırmızı 720 → 576;
    # ikisinde de kayıp tam 144 = o kabın bütün payı). Kap çarpımı BÜYÜMEDİ,
    # AYIRT EDEN eksen büyüdü.
    "c-tablolu": (
        "| " + " | ".join(bd.C_TABLOSU_SUTUNLARI) + " |\n",
        "|" + "---|" * len(bd.C_TABLOSU_SUTUNLARI) + "\n",
    )
    + tuple(
        f"| {ad} | bulgu {i:02d} | Yayin {i:02d} | "
        f"https://ornek.example/{i:02d} | 2025-03 | hayır |\n"
        for i, ad in enumerate(bd.TEMEL_ALANLAR, start=1)
    ),
}
_CIT_DIL_ETIKETLERI = {"dilsiz": "", "dilli": "python"}
# Envanterin İNSAN adı beyanda geçer; hücre kimliği KISA olmalı (pytest id).
# Eşleme SIRAYA göre kurulur ve uzunluk eşitliği ALTTA sabitlenir — kalem
# eklenirse test kırılır, sessizce kaymaz.
_BAGLAM_KISA_ADLARI = (
    "girintisiz",
    "iki-bosluk",
    "madde-isaretli",
    "ic-ice-madde",
    "yildiz-madde",
    "arti-madde",
    "sirali-liste",
    "bir-bosluk-kok",
    "uc-bosluk-kok",
)
_ISARET_KISA_ADLARI = ("backtick3", "backtick4", "tilde3")


def _BAGLAM_ADLARI_ILE(envanter):
    assert len(envanter) == len(_BAGLAM_KISA_ADLARI), envanter
    return [
        (kisa, on, devam)
        for kisa, (_ad, on, devam) in zip(_BAGLAM_KISA_ADLARI, envanter)
    ]


def _ISARET_ADLARI_ILE(envanter):
    assert len(envanter) == len(_ISARET_KISA_ADLARI), envanter
    return [
        (kisa, isaret) for kisa, (_ad, isaret) in zip(_ISARET_KISA_ADLARI, envanter)
    ]
# BAĞLAM boyutu markdown'un LİSTE DİLBİLGİSİNDEN türer, bulunan örnekten değil:
# bir çit ya blok düzeyindedir (girintisiz), ya bir liste öğesinin DEVAMIDIR
# (iki boşluk), ya kod-girintisi eşiğindedir (dört boşluk), ya doğrudan bir
# MADDE İŞARETİNDEN sonra açılır (`- `), ya da İÇ İÇE bir maddenin içindedir
# (`  - `). Demetin ilk üyesi AÇICININ önekidir, ikincisi ondan SONRAKİ
# satırların (gövde + kapatıcı) DEVAM GİRİNTİSİ — gerçek markdown'da açıcı
# madde işareti taşısa bile kapatıcı yalnız girinti taşır.
# ...ve envanteri MODÜL sahiplenir (`bd.CIT_BAGLAM_BICIMLERI`): kapsam beyanı da
# testin boyutu da AYNI demetten türer, iki yerde iki liste tutulmaz.
CIT_BAGLAMLARI = {
    ad: (on, devam) for ad, on, devam in _BAGLAM_ADLARI_ILE(bd.CIT_BAGLAM_BICIMLERI)
}
# AYIRAÇ BİÇİMİ boyutu CommonMark'ın kod-çiti tanımından türer: İKİ ayıraç
# karakteri (backtick · tilde) ve EN AZ üç uzunluk.
CIT_ISARETLERI = {
    ad: isaret for ad, isaret in _ISARET_ADLARI_ILE(bd.CIT_AYIRAC_BICIMLERI)
}


def _cit_bicimleri() -> tuple[tuple[str, str, str, tuple[str, ...], tuple[str, ...]], ...]:
    """(ad, dil, gövde adı, gövde satırları, çit satırları) — BEŞ boyutun TAM
    çarpımı, elle yazılmaz.

    Dördüncü üye gövdenin BAĞLAMA GÖRE GİRİNTİLENMİŞ hâlidir: dilli çitin
    ŞEFFAFLIK tabanı (`_ham_kaybi`) aynı satırları ÇİTSİZ koyarak ölçülür,
    dolayısıyla taban da aynı girintiyi taşımalıdır — yoksa kıyas elma-armut
    olur.
    """
    bicimler: list[tuple[str, str, str, tuple[str, ...], tuple[str, ...]]] = []
    for dil in CIT_BOYUTLARI["dil"]:
        for govde in CIT_BOYUTLARI["govde"]:
            for kapanis in CIT_BOYUTLARI["kapanis"]:
                for baglam in CIT_BOYUTLARI["baglam"]:
                    for isaret in CIT_BOYUTLARI["isaret"]:
                        on, devam = CIT_BAGLAMLARI[baglam]
                        ayirac = CIT_ISARETLERI[isaret]
                        govde_satirlari = tuple(
                            devam + satir for satir in _CIT_GOVDELERI[govde]
                        )
                        satirlar = (
                            (f"{on}{ayirac}{_CIT_DIL_ETIKETLERI[dil]}\n",)
                            + govde_satirlari
                            + ((f"{devam}{ayirac}\n",) if kapanis == "kapali" else ())
                        )
                        bicimler.append(
                            (
                                f"{dil}-{govde}-{kapanis}-{baglam}-{isaret}",
                                dil,
                                govde,
                                govde_satirlari,
                                satirlar,
                            )
                        )
    return tuple(bicimler)


CIT_BICIMLERI = _cit_bicimleri()

# KAP kümesi artık `KAP_AILELERI`'nin TAMAMIDIR. Tur 8'de yalnız `_Yuva.dolu`
# okuyan iki aile alınmıştı ve gerekçe TABLO eksenine aitti (tablo öbür üç kabı
# doldurmaz). ÖLÇÜLDÜ ki ÇİT onları doldurur: video havuzu MADDE sayarak,
# bölüm HAM boşlukla, Bölüm C eşleme satırı MADDE/TABLO satırıyla.
# **Tur 11 — KAP ekseni AİLE TEMSİLCİSİNE indirildi (6000 → 2400 hücre).**
# Ölçüldü ki 20 kabın çarpımı ayırt edici güç EKLEMİYORDU: tur 10'un hedefli
# mutasyon kolunda kırmızının tamamı 776 hücrede toplanıyordu ve kalan çarpım
# aynı yanıtı tekrar ediyordu. Daha ağırı: o 6000 hücre tur 11'in İKİ bulgusunu
# da KAÇIRDI, çünkü eksende YAPISAL (çit içindeki başlık) ve AYRIŞTIRICI-BAĞLAMI
# (kap geçişi) boyutları YOKTU. Kazanılan yer o boyutlara harcandı
# (`CIT_YAPISAL_MATRISI` · `CIT_GECIS_MATRISI` · `CIT_BILESIM_MATRISI`).
#
# Temsilci SEÇİLMEZ, TÜRETİLİR: her ailenin modülün kanonik sabitindeki İLK
# üyesi. Sonradan "kırılan hücreyi" seçmek kolu kendi kanıtına göre ayarlamak
# olurdu; kural önce yazıldı, kırmızı SONRA ölçüldü.
CIT_KAP_TEMSILCILERI = tuple(
    dict.fromkeys(aile for aile, *_ in KAP_AILELERI)
)
CIT_KAPLARI = tuple(
    (aile, ad, bosalt, ekle)
    for aile, ad, bosalt, ekle, _d in KAP_AILELERI
    if ad == next(x for a, x, *_r in KAP_AILELERI if a == aile)
)
CIT_TAM_UZAY = tuple(
    (f"{aile}/{ad}/{bicim_adi}", dil, govde, govde_satirlari, bosalt, ekle, satirlar)
    for aile, ad, bosalt, ekle in CIT_KAPLARI
    for bicim_adi, dil, govde, govde_satirlari, satirlar in CIT_BICIMLERI
)

# ─── ÇARPIM DEĞİL, KAPSAMA (2026-09-09) ───────────────────────────────────
#
# Eksen ALTI boyutlu ve boyutların hepsi ayırt edici; ama boyutların TAM
# ÇARPIMI (3240 hücre) değil. Ölçüldü, tam çarpım üstünde:
#
#   * çit kuralı TAMAMEN sökülünce dilsiz yarının 924 hücresi YEŞİL kaldı —
#     en sert mutasyonu bile ayırt etmiyorlar;
#   * dilli yarının 1080 hücresinin beklentisi zaten BOŞTU (vacuous);
#   * `tur12` mutantını tam çarpımın HİÇBİR hücresi yakalamıyor (0 kırmızı) —
#     onu yakalayan şey CommonMark sınır PROBLARI, matris değil.
#
# Yani ayırt eden şey EKSEN eklemekti, var olan eksenleri birbiriyle çarpmak
# değil. Bu dosyanın kendi tarihi de bunu söylüyor: tur 11'de kap ekseni aile
# temsilcisine indirilmişti (6000 -> 2400) ve kazanılan yer YENİ eksenlere
# harcanmıştı; tur 11'in iki bulgusunu da o 6000 hücre KAÇIRMIŞTI.
#
# Matris bu yüzden ÜÇ-YOLLU KAPSAMA DİZİSİNE indirildi: altı boyutun her ÜÇLÜ
# değer bileşimi en az bir hücrede geçer. Tarihte bulunan çit hataları
# (tur 10 · 11 · 13) ikili ve üçlü etkileşimlerdi; üçlü kapsama onları
# yakalayabilecek en küçük kümedir.
#
# **DÜRÜST SINIR — kabul edilmiş risk:** dört ya da beş boyutun AYNI ANDA
# tuttuğu bir hata kaçabilir. "Gelecekteki her hata en fazla üç yolludur"
# ölçülemez; ölçülen tek şey bugüne kadar bulunanların hepsinin ≤3 yollu
# olduğudur. Yeniden açılma koşulu: dört-yollu bir çit hatası bulunursa
# `_KAPSAMA_DERECESI` 4'e çıkarılır (tek satır).
#
# **KÜME ELLE SEÇİLMEZ** — seçilseydi kol kendi kanıtına göre ayarlanmış
# olurdu. Belirlenimci açgözlü algoritma üretir; kapanış kanıtı aşağıdaki
# mutasyon kollarındadır, seçimin kendisinde değil.
_KAPSAMA_DERECESI = 3
_CIT_BOYUT_SIRASI = ("dil", "govde", "kapanis", "baglam", "isaret")


def _cit_kimlikleri() -> tuple[tuple[int, ...], ...]:
    """Her hücrenin BOYUT KİMLİĞİ — üretim sırasından çözülür, ADDAN DEĞİL.

    Ad ayrıştırmak yanlış: `c-tablolu` gövdesi tire taşıyor ve ad tireyle
    bölününce boyutlar kayıyor (ölçüldü — kapsama dizisi 280 yerine 500
    hücreye şişmişti). `CIT_BICIMLERI` iç içe döngüleri `_CIT_BOYUT_SIRASI`
    ile üretir, dolayısıyla sıra numarası karışık tabanlı bir sayıdır.
    """
    radix = [len(CIT_BOYUTLARI[ad]) for ad in _CIT_BOYUT_SIRASI]
    kimlikler = []
    for sira in range(len(CIT_TAM_UZAY)):
        kap, kalan = divmod(sira, len(CIT_BICIMLERI))
        basamaklar = []
        for taban in reversed(radix):
            kalan, basamak = divmod(kalan, taban)
            basamaklar.append(basamak)
        kimlikler.append((kap, *reversed(basamaklar)))
    return tuple(kimlikler)


CIT_KIMLIKLERI = _cit_kimlikleri()
# ÇÖZÜMÜN KONTROLÜ: saklanan alanlarla (dil, gövde) tutuyor mu? Karışık tabanlı
# çözüm sessizce kaysaydı kapsama dizisi yanlış boyutları kapsardı.
for _sira, (_ad, _dil, _govde, *_kalan) in enumerate(CIT_TAM_UZAY):
    _k = CIT_KIMLIKLERI[_sira]
    assert CIT_BOYUTLARI["dil"][_k[1]] == _dil, _ad
    assert CIT_BOYUTLARI["govde"][_k[2]] == _govde, _ad


def _kapsama_dizisi(derece: int, tohum: int = 0) -> tuple[int, ...]:
    """Her `derece`-li boyut bileşimini kapsayan en küçük hücre kümesi (açgözlü)."""
    eksen_kumeleri = list(itertools.combinations(range(6), derece))
    satir_bilesimleri = [
        frozenset((e, tuple(kimlik[i] for i in e)) for e in eksen_kumeleri)
        for kimlik in CIT_KIMLIKLERI
    ]
    kalan = set().union(*satir_bilesimleri)
    sira = list(range(len(CIT_TAM_UZAY)))
    random.Random(tohum).shuffle(sira)
    secili: list[int] = []
    while kalan:
        en_iyi, en_iyi_kazanc = None, -1
        for aday in sira:
            kazanc = len(satir_bilesimleri[aday] & kalan)
            if kazanc > en_iyi_kazanc:
                en_iyi, en_iyi_kazanc = aday, kazanc
        secili.append(en_iyi)
        kalan -= satir_bilesimleri[en_iyi]
    return tuple(sorted(secili))


CIT_SECILI_SIRALAR = _kapsama_dizisi(_KAPSAMA_DERECESI)
CIT_MATRISI = tuple(CIT_TAM_UZAY[sira] for sira in CIT_SECILI_SIRALAR)
_CIT_BOYUT_OLCULERI = (len(CIT_KAPLARI),) + tuple(
    len(CIT_BOYUTLARI[ad]) for ad in _CIT_BOYUT_SIRASI
)
CIT_HUCRE_KIMLIGI = {
    hucre[0]: CIT_KIMLIKLERI[sira]
    for hucre, sira in zip(CIT_MATRISI, CIT_SECILI_SIRALAR)
}


def _boyut_degeri(ad: str, boyut: str) -> str:
    """Hücrenin bir boyuttaki DEĞERİ — addan ayrıştırılmaz, kimlikten okunur."""
    kimlik = CIT_HUCRE_KIMLIGI[ad]
    return CIT_BOYUTLARI[boyut][kimlik[1 + _CIT_BOYUT_SIRASI.index(boyut)]]

# ÖLÇÜLMÜŞ PİNLER — sayılar taze koşumdan gelir, tahmin değildir.
_TUR9_KIRMIZI = 402
# KÖK düzeyinde KAPANMAMIŞ çit belgenin gerisini yutar ve SAYIM taşıyan bir notu
# daha SIKI bir sayıyla yeniden yazar. Ham (mesaj düzeyi) kaybın ÇIKTIĞI hücreler
# — istisna sessizce genişleyemesin diye ADIYLA sabitlenir. Hepsi AYNI hücre
# sınıfıdır: KÖK rejimindeki bağlam × `kapanmamis` × video havuzu temsilcisi;
# sebebi `test_kapanmamis_kok_citinin_bedeli_OLCULUR`'da ölçülür.
#
def _gramer_maskesi(satirlar) -> list[bool]:
    """ORACLE — maskeyi AYRIŞTIRICIDAN türetir, modülün fonksiyonundan DEĞİL.

    Bağımsızlık ŞARTTIR: beklenti `bd._cit_maskesi`'yi okusaydı, o fonksiyonu
    değiştiren her MUTASYON beklentiyi de birlikte kaydırırdı ve mutasyon
    kolları sessizce yeşile dönerdi (ölçüldü, tur 13). Oracle doğrudan
    `bd._MD`'yi okur; mutasyon onu DEĞİŞTİRMEZ.
    """
    maske = [False] * len(satirlar)
    for jeton in bd._MD.parse("\n".join(satirlar)):
        if jeton.map is None:
            continue
        if jeton.type == "code_block" or (
            jeton.type == "fence" and not (jeton.info or "").strip()
        ):
            bas, son = jeton.map
            for k in range(max(bas, 0), min(son, len(maske))):
                maske[k] = True
    return maske


# **Tur 13 — rejim GRAMERE SORULUR.** Tur 12'de ölçüt modülün kendi yardımcısıydı
# (`_kapsayici_sutunu`); tur 13'te o yardımcı SİLİNDİ çünkü kap üyeliğini artık
# CommonMark ayrıştırıcısı belirliyor. Test bir ad listesi TUTMAZ ve bir kural
# KOPYALAMAZ: kapanmamış bir çidin belge SONUNA kadar düşüp düşmediğini
# ayrıştırıcıya sorar. "Yutar" = kök rejim; "kap-biter" = bir kap içi.
def _cit_rejimi(on: str) -> str:
    """Bu önekle açılan KAPANMAMIŞ çit belge sonuna kadar yutar mı?"""
    maske = _gramer_maskesi([f"{on}```", "govde satiri", "kok duzeyi satir", "son satir"])
    return "yutar" if maske[-1] else "kap-biter"


_KOK_BAGLAMLARI = tuple(
    ad for ad in CIT_BOYUTLARI["baglam"] if _cit_rejimi(CIT_BAGLAMLARI[ad][0]) == "yutar"
)
HAM_KAYIPLI_HUCRELER = frozenset(
    f"video-havuzu/hareket/dilsiz-{govde}-kapanmamis-{baglam}-{isaret}"
    for govde in ("bos", "sozcuklu", "sozcuksuz", "maddeli", "tablolu", "c-tablolu")
    for baglam in _KOK_BAGLAMLARI
    for isaret in ("backtick3", "backtick4", "tilde3")
)

_BOS_KAP_ONBELLEGI: dict[int, frozenset] = {}


def _bos_kap_notlari(bosalt) -> frozenset:
    anahtar = id(bosalt)
    if anahtar not in _BOS_KAP_ONBELLEGI:
        _BOS_KAP_ONBELLEGI[anahtar] = frozenset(_not_kumesi(bosalt(TEMIZ)))
    return _BOS_KAP_ONBELLEGI[anahtar]


def _cit_kaybi(bosalt, ekle, satirlar) -> frozenset:
    """Eklemenin KALDIRDIĞI bulgu KÜMESİ — sayı DEĞİL, küme farkı.

    NÖTRDÜR: kaybın MEŞRU olup olmadığına karar VERMEZ. Bazı kollar kaybı
    BEKLER (dilli çit şeffaftır, gerçek madde kabı doldurur); "kayıp olamaz"
    iddiasını kuran kollar gramer kapısını KENDİ uygular (`_gizli_kayip`).
    """
    bos = bosalt(TEMIZ)
    return frozenset(_bos_kap_notlari(bosalt) - _not_kumesi(ekle(bos, satirlar)))


def _gizli_kayip(bosalt, ekle, satirlar) -> frozenset:
    """"Kayıp OLAMAZ" iddiasının kayıp kümesi — gramer kapısıyla.

    Enjekte edilen blok gramere göre GİZLİ değilse iddia kurulmaz: görünür
    içerik bir kabı gerçekten doldurur ve notu meşru düşürür.
    """
    if not _gizli_mi(bosalt, ekle, satirlar):
        return frozenset()
    return _cit_kaybi(bosalt, ekle, satirlar)


# Bir bulgunun KONUSU: ölçülen SAYI çıkarılmış mesaj. İki not aynı konudaysa
# kapı o konu hakkında SUSMAMIŞTIR — yalnız ölçtüğü sayı değişmiştir.
_SAYI_RE = re.compile(r"\d+")


def _sinif(mesajlar) -> frozenset:
    return frozenset(_SAYI_RE.sub("#", b.mesaj) for b in mesajlar)


def _cit_sinif_kaybi(bosalt, ekle, satirlar) -> frozenset:
    """SUSTURULAN KONU kümesi — sayısı değişen not kayıp SAYILMAZ.

    **Tur 11'de ölçülmüş ve İLKEDEN türetilmiş incelik.** KÖK düzeyinde açılan
    KAPANMAMIŞ bir çit, CommonMark gereği belgenin GERİSİNİ yutar (maske artık
    belge geneli olduğu için bu tur 10'daki "blok sonuna kadar"dan daha geniştir
    ve daha FAIL-CLOSED'dır). Yutulan bölge görünmez olunca SAYIM taşıyan bir not
    daha SIKI bir sayıyla yeniden yazılabilir — ölçüldü, `video_kodlar` havuzu:
    `toplam 5 madde, alt sınır 10` -> `toplam 0 madde, alt sınır 10`, yanında 19
    YENİ not. Kapı o konu hakkında SUSMADI; daha yüksek sesle konuştu.

    Değişmezin doğru düzeyi bu yüzden KONUDUR: bir çit eklemek hiçbir KONUYU
    susturamaz. Ham kayıp AYRICA ve ADIYLA sabitlenir
    (`test_kapanmamis_kok_citinin_bedeli_OLCULUR`) — istisna sessizce
    genişleyemesin diye.
    """
    bos = bosalt(TEMIZ)
    return _sinif(_bos_kap_notlari(bosalt)) - _sinif(_not_kumesi(ekle(bos, satirlar)))


def _ham_kaybi(bosalt, ekle, govde_satirlari) -> frozenset:
    """Aynı gövde ÇİTSİZ konsaydı hangi notlar düşerdi? (dilli beklentisinin tabanı)

    Gövde AYNI BAĞLAM GİRİNTİSİYLE konur — girinti tabanı değiştirseydi
    şeffaflık kıyası bağlam boyutunda anlamını kaybederdi.
    """
    return _cit_kaybi(bosalt, ekle, govde_satirlari)


# ─── BEKLENTİ GRAMERDEN TÜRER (tur 13) ─────────────────────────────────────
#
# Tur 12'ye kadar matris şunu varsayıyordu: verilen önekle yazılan bir ayıraç
# HER ZAMAN bir çit AÇAR ve gövdesini GİZLER. Gramer koşturulunca bu varsayımın
# yanlış olduğu ÖLÇÜLDÜ — enjeksiyon NOKTASI belirleyicidir:
#
#   * `   ``` ` bir liste öğesinin DEVAMI olarak gelirse çit o ÖĞENİN içinde
#     açılır ve öğe bitince kapanır; sonraki kök başlığı GERÇEKTEN görünür.
#   * `    ``` ` bir PARAGRAFTAN sonra gelirse girintili kod bloğu OLAMAZ
#     (paragrafı bölemez) — satırlar paragrafın devamı, yani GÖRÜNÜR metindir.
#
# Bu hücrelerde notun düşmesi SAHTECİLİK DEĞİLDİR: içerik belgede gerçekten
# vardır ve okuyan insan da görür. İddia bu yüzden gramere BAĞLANDI ve
# GÜÇLENDİ: bir not ancak enjekte edilen içerik GERÇEKTEN GÖRÜNÜRSE düşebilir;
# içerik LİTERAL bir blokta gizliyse HİÇBİR not düşemez.
def _gizli_mi(bosalt, ekle, satirlar) -> bool:
    """Enjekte edilen blok gramere göre LİTERAL mi (gizli mi)?

    Ölçüt: enjekte edilen satırların TAMAMI maskeli mi. Bir tanesi bile
    maskesizse içerik belgede görünür demektir ve "gizleme" iddiası düşer.
    """
    belge = ekle(bosalt(TEMIZ), satirlar)
    ham = belge.splitlines()
    maske = _gramer_maskesi(ham)
    aranan = [x.rstrip("\n") for x in satirlar]
    for k in range(len(ham) - len(aranan) + 1):
        if ham[k : k + len(aranan)] == aranan:
            return all(maske[k : k + len(aranan)])
    return False


def _cit_ihlali(dil: str, govde_satirlari, bosalt, ekle, satirlar) -> str:
    if dil == "dilsiz":
        if not _gizli_mi(bosalt, ekle, satirlar):
            return ""  # içerik GÖRÜNÜR — gizleme iddiası yok, kayıp meşru
        susan = _cit_sinif_kaybi(bosalt, ekle, satirlar)  # noqa: E501
        return (
            f"DİLSİZ çit eklemek şu KONULARI susturdu: {sorted(susan)}"
            if susan
            else ""
        )
    kayip = _cit_kaybi(bosalt, ekle, satirlar)
    # DİLLİ çit ilan edilmiş AÇIK kalemdir ve ŞEFFAFTIR: çitsiz hâlin kaldırdığı
    # her notu O DA kaldırmalı. Bu beklenti gövdeye göre boş olabilir (boş gövde
    # çitsiz hiçbir şey kaldırmaz) — boş hücreler `..._bos_kume_ve_taban_kollari`
    # kolunda ADIYLA sayılır, sessizce yeşile dönmezler.
    eksik = _ham_kaybi(bosalt, ekle, govde_satirlari) - kayip
    return (
        f"ilan edilen AÇIK biçim şeffaf DEĞİL — çitsiz hâlin kaldırdığı şu notlar "
        f"çitli hâlde KALMADI: {sorted(_mesajlari(eksik))}"
        if eksik
        else ""
    )


@pytest.mark.parametrize(
    "dil,govde_satirlari,bosalt,ekle,satirlar",
    [(h[1], h[3], h[4], h[5], h[6]) for h in CIT_MATRISI],
    ids=[h[0] for h in CIT_MATRISI],
)
def test_kod_citi_ekseni(dil, govde_satirlari, bosalt, ekle, satirlar) -> None:
    """DİLSİZ çit HİÇBİR notu kaldıramaz; DİLLİ çit ilan edildiği gibi ŞEFFAFTIR."""
    assert _cit_ihlali(dil, govde_satirlari, bosalt, ekle, satirlar) == ""


def test_kod_citi_ekseni_bos_kume_ve_taban_kollari() -> None:
    """Alt-eksen ÜRETİLDİ mi, hücreler BOŞA yeşil mi, boş hücreler HANGİLERİ?"""
    # Boyutların TAM çarpımı: 2 × 5 × 2 × 8 × 3 = 480 biçim.
    carpim = 1
    for degerler in CIT_BOYUTLARI.values():
        carpim *= len(degerler)
    assert carpim == len(CIT_BICIMLERI) == 648, len(CIT_BICIMLERI)
    # BAĞLAM ve AYIRAÇ boyutları GERÇEKTEN üretiliyor: her değer en az bir
    # biçimde geçiyor ve ürettiği açıcı satırı BİRBİRİNDEN farklı.
    acicilar = {ad: satirlar[0] for ad, _d, _g, _gs, satirlar in CIT_BICIMLERI}
    for baglam in CIT_BOYUTLARI["baglam"]:
        for isaret in CIT_BOYUTLARI["isaret"]:
            ad = f"dilsiz-bos-kapali-{baglam}-{isaret}"
            assert ad in acicilar, ad
    on, devam = CIT_BAGLAMLARI["madde-isaretli"]
    assert (on, devam) == ("- ", "  "), (on, devam)
    assert acicilar["dilsiz-bos-kapali-madde-isaretli-backtick3"] == "- ```\n"
    assert acicilar["dilsiz-bos-kapali-ic-ice-madde-tilde3"] == "  - ~~~\n"
    assert acicilar["dilsiz-bos-kapali-uc-bosluk-kok-backtick4"] == "   ````\n"
    assert acicilar["dilsiz-bos-kapali-yildiz-madde-backtick3"] == "* ```\n"
    assert acicilar["dilsiz-bos-kapali-arti-madde-backtick3"] == "+ ```\n"
    assert acicilar["dilsiz-bos-kapali-sirali-liste-backtick3"] == "1. ```\n"
    assert len(set(acicilar.values())) == 54, len(set(acicilar.values()))
    # KAP ekseni AİLE TEMSİLCİSİDİR (tur 11): her ailenin modül sabitindeki İLK
    # üyesi. Aile kümesi yine modülün KENDİ sabitlerinden türer.
    assert len(CIT_KAP_TEMSILCILERI) == len(CIT_KAPLARI) == 5
    assert {aile for aile, *_ in KAP_AILELERI} == set(CIT_KAP_TEMSILCILERI)
    assert [ad for _a, ad, *_ in CIT_KAPLARI] == [
        bd.TEMEL_ALANLAR[0],
        bd.OZEL_GUN_YUVALARI[0],
        bd.VIDEO_HAVUZLARI[0],
        bd.BOLUM_HARFLERI[0],
        "C",
    ], [ad for _a, ad, *_ in CIT_KAPLARI]
    # ...ve KÜÇÜLTÜLEN eksen KAYBOLMADI: aile başına bir temsilci ÖLÇÜLÜYOR.
    # ─── KAPSAMA KAPISI — küme ELLE SEÇİLMEDİ, İDDİA ÖLÇÜLÜYOR ───
    assert len(CIT_TAM_UZAY) == 648 * 5 == 3240, len(CIT_TAM_UZAY)
    assert len(CIT_MATRISI) == 280, len(CIT_MATRISI)  # taze koşum, 2026-09-09
    adlar = [h[0] for h in CIT_MATRISI]
    assert len(set(adlar)) == len(adlar), "hücreler ÇAKIŞIYOR"
    # Her ÜÇLÜ boyut bileşimi seçilmiş kümede GEÇİYOR — beklenti bileşim
    # uzayından ÜRETİLİR, seçilmiş hücrelerden değil.
    eksen_kumeleri = list(itertools.combinations(range(6), _KAPSAMA_DERECESI))
    beklenen = {
        (eksenler, degerler)
        for eksenler in eksen_kumeleri
        for degerler in itertools.product(
            *[range(_CIT_BOYUT_OLCULERI[i]) for i in eksenler]
        )
    }
    kapsanan = {
        (eksenler, tuple(CIT_KIMLIKLERI[sira][i] for i in eksenler))
        for sira in CIT_SECILI_SIRALAR
        for eksenler in eksen_kumeleri
    }
    assert kapsanan == beklenen, sorted(beklenen - kapsanan)[:5]
    # ...ve kapsama İKİLİ değil ÜÇLÜ: ikili yetseydi küme 55 hücreye inerdi
    # (ölçüldü), üçlü 280. Derece düşerse bu sayı düşer ve kol uyarır.
    assert _KAPSAMA_DERECESI == 3 and len(beklenen) == 1505, len(beklenen)
    # Her hücre GERÇEKTEN bir kap boşaltıyor ve boşaltma NOT üretiyor.
    bossuz = [
        ad for ad, _, _, _, bosalt, _, _ in CIT_MATRISI if not _bos_kap_notlari(bosalt)
    ]
    assert bossuz == [], bossuz
    # ...ve eklenen çit belgeyi gerçekten BÜYÜTÜYOR.
    for ad, _, _, _, bosalt, ekle, satirlar in CIT_MATRISI:
        bos = bosalt(TEMIZ)
        assert len(ekle(bos, satirlar).splitlines()) > len(bos.splitlines()), ad
    # DİLLİ yarı BOŞA yeşil değil: orada not gerçekten DÜŞÜYOR — ve HANGİ
    # hücrelerde düşmediği ADIYLA kayıtlıdır (boş hücre dürüstlüğü).
    dilli_dusen = {
        ad
        for ad, dil, _g, _gs, b, e, s in CIT_MATRISI
        if dil == "dilli" and _cit_kaybi(b, e, s)
    }
    assert len(dilli_dusen) == 102, len(dilli_dusen)  # taze koşum, 2026-09-09
    # DİLLİ beklentisinin VACUOUS olduğu hücreler: çitsiz gövde de bir şey
    # kaldırmıyorsa "şeffaflık" iddiası boşta kalır. Sayısı ölçülmüştür.
    vacuous = {
        (ad, govde)
        for ad, dil, govde, gs, b, e, _s in CIT_MATRISI
        if dil == "dilli" and not _ham_kaybi(b, e, gs)
    }
    assert len(vacuous) == 100, len(vacuous)  # taze koşum, 2026-09-09
    # ÖLÇÜLMÜŞ dürüst kayıt: `maddeli` gövdenin HİÇBİR hücresi vacuous DEĞİLDİR —
    # şeffaflık beklentisi dilli-maddeli hücrelerin hepsinde GERÇEKTEN ölçülür.
    assert {govde for _ad, govde in vacuous} == {
        "bos",
        "sozcuklu",
        "sozcuksuz",
        "tablolu",
        "maddeli",
        "c-tablolu",
    }
    # ESKİ KOL KALDIRILDI — DÜRÜST KAYIT. Burada "vacuous sayısı bağlam×ayıraç
    # çarpımına tam bölünür" diye bir kol vardı; o iddia TAM ÇARPIMIN bir yan
    # ürünüydü (her bileşim tam 30 kez geçtiği için), kapsama dizisinde
    # anlamını yitirir ve sağlamasa da bir kusur göstermez. Yerine iddianın
    # KENDİSİ ölçülüyor: vacuous'luk bağlam ve ayıraçtan BAĞIMSIZ.
    #
    # AYIRAÇ BAĞIMSIZLIĞI KOLU DÜŞÜRÜLDÜ — ÖLÇÜLDÜ, GİZLENMEDİ. Vacuous'luğun
    # hangi boyutlara bağlı olduğu ölçüldü: KAP + GÖVDE + KAPANIŞ + BAĞLAM
    # (`ic-ice-madde` gövdeyi iç içe maddenin girintisine sokuyor, çitsiz taban
    # da hiçbir not düşürmüyor). Geriye "ayıraç biçiminden bağımsız" iddiası
    # kalıyordu; kapsama dizisinde o iddiayı SINAYAN tek bir grup bile yok —
    # aynı (kap, gövde, kapanış, bağlam) iki farklı ayıraçla geçmiyor (ölçüldü:
    # sınayan grup sayısı 0). Boşa yeşil bir kol bırakmak beyanı bayatlatırdı.
    #
    # DÜRÜST ETİKET: çözülmedi + bilinçle düşürüldü. Yeniden açılma koşulu:
    # ayıraç biçimine bağlı gerçek bir çit hatası çıkarsa, iddia kapsama
    # dizisine bir ayıraç-çifti hücresi EKLENEREK sınanır.


def test_kod_citi_ekseni_mutasyona_duyarli() -> None:
    """MUTASYON: çit kuralının TEK EVİNİ sök (`_cit_maskesi`) → eksen KIRILSIN.

    Tek yeri sökmek BÜTÜN süpürülmüş yolları birden düşürür; bu, "kural tek
    yerde yaşıyor mu" sorusunun da ölçümüdür — ikinci bir çit ayrıştırıcısı
    yazılmış olsaydı mutasyon o yolu kapatamaz ve kol dar kalırdı.
    """
    _BOS_KAP_ONBELLEGI.clear()
    try:
        with mock.patch.object(bd, "_cit_maskesi", lambda satirlar: [False] * len(satirlar)):
            kirmizi = [
                ad
                for ad, dil, _g, gs, bosalt, ekle, satirlar in CIT_MATRISI
                if dil == "dilsiz" and _cit_ihlali(dil, gs, bosalt, ekle, satirlar)
            ]
    finally:
        _BOS_KAP_ONBELLEGI.clear()
    assert kirmizi, "çit kuralı sökülünce eksen KIRILMADI — kol ölçmüyor"
    # ÖLÇÜLDÜ: kırılan KAP AİLESİ BEŞTİR — tur 8'de kol yalnız İKİ aileyi
    # (doluluk kapları) kırıyordu. Süpürme kardeş kapları da kapsadığı için
    # mutasyon beş ailenin hepsini birden düşürür.
    assert len(kirmizi) == 59, len(kirmizi)  # taze koşum, 2026-09-09
    # ...ve ÇİT BOYUTLARININ HEPSİ kırmızıya katkı veriyor — kol tek bir
    # bileşime dayanmıyor. İDDİA GÜÇLENDİ: eskiden yalnız `-backtick3` ekli
    # adlar aranıyordu (tam çarpımın yan ürünü); şimdi her boyutun BÜTÜN
    # değerleri kırmızıda geçiyor mu diye KİMLİKTEN okunarak sorulur.
    assert len({ad.rsplit("/", 1)[1] for ad in kirmizi}) == 53, len(kirmizi)
    for boyut in ("baglam", "isaret", "govde"):
        gecen = {_boyut_degeri(ad, boyut) for ad in kirmizi}
        assert gecen == set(CIT_BOYUTLARI[boyut]), (
            boyut,
            sorted(set(CIT_BOYUTLARI[boyut]) - gecen),
        )
    aileler = {ad.split("/")[0] for ad in kirmizi}
    assert aileler == {
        "bolum-a-alani",
        "donem-yuvasi",
        "video-havuzu",
        "bolum",
        "c-esleme-kabi",
    }, aileler
    # DÜRÜST BOŞ HÜCRE KAYDI: mutasyon altında da yeşil kalan dilsiz hücreler —
    # hiçbiri `maddeli` DEĞİLDİR; o gövdenin hücrelerinin hepsi kırılır.
    yesil = {ad for ad, dil, *_ in CIT_MATRISI if dil == "dilsiz"} - set(kirmizi)
    assert len(yesil) == 74, len(yesil)  # taze koşum, 2026-09-09
    # DÜRÜST KAYIT — 4. ayaktan SONRA burası DEĞİŞTİ. `maddeli` gövdenin yeşil
    # hücreleri artık VAR ve hepsi TEK bir aileden geliyor: `c-esleme-kabi`.
    # Sebep yapısaldır, kapsam kaybı değil: sözleşme Bölüm C'yi sabit sütunlu
    # tabloya çevirdiğinden beri o kabı bir MADDE satırı DOLDURMUYOR, dolayısıyla
    # çitsiz hâl de bir not düşürmüyor ve "çit gizledi" iddiası kurulamıyor.
    # O kabın gerçek dolduran gövdesi `c-tablolu`dur ve onun 54 hücresinin
    # HEPSİ kırmızıdır (ölçüldü).
    assert {ad.split("/")[0] for ad in yesil if "-maddeli-" in ad} == {
        "c-esleme-kabi"
    }, sorted(ad for ad in yesil if "-maddeli-" in ad)[:5]
    assert not any("-c-tablolu-" in ad for ad in yesil if ad.startswith("c-esleme-kabi/"))


# ─── DONMUŞ MUTANTLAR (tur 13) — gönderdiğimiz HER elle yazılmış makine ────
#
# Tur 8-12 arasında maske elle yazılmıştı ve her turda gramerin bir kuralı daha
# eklendi. Tur 13'te maske `markdown-it-py`'ye devredildi. O makineler artık
# üretimde YAŞAMIYOR ama testte DONMUŞ MUTANT olarak duruyorlar: her biri, o
# turda BİLİNMEYEN bir bileşimde en az bir notu kaldırır. Kol, bağımlılığın
# yerini HAK ETTİĞİNİ ölçer — "grameri koşturmak daha iyi" bir iddia değil,
# ölçülen bir farktır.
#
# Mutantlar DEĞİŞTİRİLMEZ: tarihsel kayıttır, bugünkü koda göre güncellenmez.

_MUTANT_DESENLERI = {
    # tur 9: bağlama TAMAMEN kör (liste işareti yok)
    "tur9": re.compile(r"^([ \t]*)(`{3,}|~{3,})[ \t]*(\S*)[ \t]*$"),
    # tur 10: liste işareti kümesi SÖZLEŞMEDEN türetilmişti (`-` ve yalnız `-`)
    "tur10": re.compile(r"^([ \t]*(?:-[ \t]+)?)(`{3,}|~{3,})[ \t]*(\S*)[ \t]*$"),
    # tur 11-12: markdown'ın liste dilbilgisi, ama girinti/kapatıcı kuralları elle
    "tur12": re.compile(
        r"^([ \t]*(?:(?:[-*+]|\d{1,9}[.)])[ \t]+)?)(`{3,}|~{3,})[ \t]*(\S*)[ \t]*$"
    ),
}


def _mutant_maske(desen: re.Pattern[str], kok_tavani: int | None):
    """Elle yazılmış maskenin donmuş hâli.

    `kok_tavani=None` → tur 9/10/11 davranışı: ham girinti KAP sütunudur.
    `kok_tavani=3`    → tur 12 davranışı: 0-3 boşluklu açıcı köktür ve kap
                        kontrolü kapatıcıdan ÖNCE koşar.
    Hiçbirinde KAPATICI GİRİNTİSİ denetlenmez — tur 13'ün kapattığı açık budur.
    """

    def sutun(onek: str) -> int:
        ham = len(onek.expandtabs(4))
        if kok_tavani is not None and not onek.strip() and ham <= kok_tavani:
            return 0
        return ham

    def kapsayici_kirildi(satir: str, acik: int) -> bool:
        if acik <= 0 or not satir.strip():
            return False
        onek = satir[: len(satir) - len(satir.lstrip())]
        return len(onek.expandtabs(4)) < acik

    def maskele(satirlar):
        maske: list[bool] = []
        acik_isaret = None
        acik_sutun = 0
        acik_dilsiz = False
        for satir in satirlar:
            cit = desen.match(satir)
            kapatici = bool(
                cit
                and acik_isaret
                and cit.group(2)[0] == acik_isaret[0]
                and len(cit.group(2)) >= len(acik_isaret)
                and not cit.group(3)
            )
            if acik_isaret is not None:
                if kok_tavani is not None and kapsayici_kirildi(satir, acik_sutun):
                    acik_isaret, acik_dilsiz, acik_sutun = None, False, 0
                elif kapatici:
                    maske.append(acik_dilsiz)
                    acik_isaret, acik_dilsiz, acik_sutun = None, False, 0
                    continue
                elif kok_tavani is None and kapsayici_kirildi(satir, acik_sutun):
                    acik_isaret, acik_dilsiz, acik_sutun = None, False, 0
                else:
                    maske.append(acik_dilsiz)
                    continue
            if cit:
                acik_isaret = cit.group(2)
                acik_sutun = sutun(cit.group(1))
                acik_dilsiz = not cit.group(3)
                maske.append(acik_dilsiz)
                continue
            maske.append(False)
        return maske

    return maskele


MUTANTLAR = {
    "tur9": _mutant_maske(_MUTANT_DESENLERI["tur9"], None),
    "tur10": _mutant_maske(_MUTANT_DESENLERI["tur10"], None),
    "tur12": _mutant_maske(_MUTANT_DESENLERI["tur12"], 3),
}


def _kayipli_hucreler() -> set[str]:
    """Üretilmiş matris + CommonMark sınır probları — not KAYBEDEN hücreler."""
    kayipli = {
        ad
        for ad, dil, _g, gs, bosalt, ekle, satirlar in CIT_MATRISI
        if dil == "dilsiz" and _cit_ihlali(dil, gs, bosalt, ekle, satirlar)
    }
    for ad, (on, son) in COMMONMARK_SINIR_PROBLARI.items():
        taban, prob = _sinir_probu(on, son)
        if taban - prob:
            kayipli.add(f"sinir/{ad}")
    return kayipli


@pytest.mark.parametrize("mutant", sorted(MUTANTLAR))
def test_elle_yazilmis_her_maske_en_az_bir_kacis_birakir(mutant: str) -> None:
    """DİFERANSİYEL KOL: gönderdiğimiz her elle yazılmış makine kaçış bırakır."""
    _BOS_KAP_ONBELLEGI.clear()
    try:
        with mock.patch.object(bd, "_cit_maskesi", MUTANTLAR[mutant]):
            kayipli = _kayipli_hucreler()
    finally:
        _BOS_KAP_ONBELLEGI.clear()
    assert kayipli, (
        f"{mutant} mutantı HİÇBİR kaçış bırakmadı — kol ölçmüyor ya da mutant "
        f"bugünkü koda göre güncellenmiş"
    )


def test_gramer_maskesi_hicbir_kacis_birakmaz() -> None:
    """POZİTİF KONTROL: aynı kümede bugünkü maske HİÇ not kaybetmez."""
    _BOS_KAP_ONBELLEGI.clear()
    try:
        kayipli = _kayipli_hucreler()
    finally:
        _BOS_KAP_ONBELLEGI.clear()
    assert kayipli == set(), sorted(kayipli)
    # ...ve küme BOŞ DEĞİL: kol gerçekten hücre koşuyor. Eşik artık ÇARPIMIN
    # boyutuna değil KAPSAMA derecesine bağlanır — küme küçüldü, kapsadığı
    # bileşim uzayı küçülmedi.
    assert len(CIT_MATRISI) == len(CIT_SECILI_SIRALAR) >= 270
    assert len(COMMONMARK_SINIR_PROBLARI) == 2


def test_cit_ayiraci_satirin_tek_anlamli_icerigi_olmali() -> None:
    """AŞIRI SIKILAŞTIRMA KOLU: meşru bir madde çit sanılmamalı.

    Bağlam boyutu `- ``` `'i çit ayıracı yapar. Girintiyi/madde işaretini
    TAMAMEN görmezden gelen bir kural ise gerçek madde metnini de yutardı ve
    YENİ bir yanlış-pozitif sınıfı açardı. Ayıraç satırın TEK ANLAMLI İÇERİĞİ
    olmak zorundadır — bu kol onu ÖLÇER: meşru madde HÂLÂ kabı DOLDURUR (yani
    boşluk notunu KALDIRIR), çit ayıracı ise DOLDURMAZ.
    """
    bosalt, ekle = _kap_of("donem-yuvasi", bd.OZEL_GUN_YUVALARI[0])
    assert _bos_kap_notlari(bosalt), "taban BOŞ — kol boşa yeşil"
    # (a) MEŞRU madde: kabı doldurmaya DEVAM eder.
    assert _cit_kaybi(bosalt, ekle, ("- gerçek bir kalıp\n",)), (
        "meşru madde artık kabı DOLDURMUYOR — yeni yanlış-pozitif sınıfı açıldı"
    )
    # (b) Ayıraç satırının KENDİSİ hiçbir bağlamda kabı DOLDURMAZ. Ölçüm UÇTAN
    # UCADIR, satır düzeyinde DEĞİL: `1. ``` ` satırı tek başına bakıldığında
    # sözcük karakteri taşır (`_sozlesme_bicimli` `True` der) ama MASKELİ olduğu
    # için doluluk sayımına hiç GİRMEZ — kapının gerçek davranışı budur.
    for baglam in CIT_BAGLAMLARI:
        for ayirac in CIT_ISARETLERI.values():
            satirlar = _cit(baglam=baglam, isaret=ayirac)
            assert not _cit_kaybi(bosalt, ekle, tuple(satirlar)), (baglam, ayirac)
    # (c) İçinde ayıraç GEÇEN ama tek içeriği o OLMAYAN satır çit DEĞİLDİR.
    for satir in ("- gerçek bir kalıp\n", "- ``` içeren bir kalıp\n", "kod ``` arada\n"):
        assert not bd._KOD_CITI_RE.match(satir), satir
    # (d) LİSTE İŞARETİ kümesi MARKDOWN'ın kendi dilbilgisinden türer (tur 11):
    # `-` · `*` · `+` · sıralı liste. Tur 10 yalnız `-`'yi tanıyordu ve gerekçesi
    # sözleşmenin madde kuralıydı — ölçüldü ki bu İKİ ayrı soruyu karıştırıyor
    # ve `* ``` ` / `+ ``` ` birer notu KALDIRIYORDU.
    for satir in ("* ```\n", "+ ```\n", "1. ```\n", "1) ~~~\n", "  + ````\n"):
        assert bd._KOD_CITI_RE.match(satir), satir
    # ...ama SÖZLEŞME KURALI değişmedi: `*` ile yazılmış bir MADDE hâlâ ihlaldir
    # ve NOT alır. Markdown TANIMASI ile sözleşme KURALI ayrı yaşar.
    assert not bd._MADDE_RE.match("* gerçek bir kalıp\n")
    liste_bosalt, liste_ekle = _kap_of("bolum-a-alani", "cta_kaliplari")
    yildizli = liste_ekle(liste_bosalt(TEMIZ), ("* yildizla yazilmis bir kalip\n",))
    yeni = _mesajlari(_not_kumesi(yildizli) - _bos_kap_notlari(liste_bosalt))
    assert any("madde işareti olmayan içerik satırı" in m for m in yeni), sorted(yeni)


# ─── Çit kuralının KAPSAM ENVANTERİ — tripwire (tur 9) ─────────────────────
#
# Envanterin BİRİNCİ ayağı `ACIK_BLOK_BICIMLERI` (hangi BLOK BİÇİMLERİ hâlâ
# kabı doldurur). İKİNCİ ayağı burada: çit kuralı hangi YOLLARI kapsıyor ve
# hangilerini BİLİNÇLE kapsamıyor. Beyan bu görevde BEŞ kez bayatladı; artık
# her kalem UÇTAN UCA ölçülür — kapsanan yolda çit not KALDIRAMAZ, kapsanmayan
# yolda çit içeriği HÂLÂ GÖRÜLÜR. Ad kümeleri birebir eşleşmezse test kırılır.


def _sonra_ekle(metin: str, capa: str, govde: list[str]) -> str:
    satirlar = metin.splitlines(True)
    i = next(k for k, s in enumerate(satirlar) if s.strip() == capa)
    return "".join(satirlar[: i + 1] + govde + satirlar[i + 1 :])


def _cit(*govde: str, baglam: str = "girintisiz", isaret: str = "```") -> list[str]:
    """Çit satırları — BAĞLAM ve AYIRAÇ parametrik (tur 10 · 11).

    Öndeki girinti/liste işareti AÇICIYA, devam girintisi GÖVDEYE ve
    KAPATICIYA uygulanır; gerçek markdown'da kapatıcı liste işareti taşımaz.
    """
    on, devam = CIT_BAGLAMLARI[baglam]
    return [
        f"{on}{isaret}\n",
        *[devam + satir for satir in govde],
        f"{devam}{isaret}\n",
    ]


def _kapsanan_prob(bosalt, ekle, govde):
    """(kayıp kümesi) — kapsanan yolda BOŞ olmalı."""
    return lambda: _cit_kaybi(bosalt, ekle, govde)


def _kap_of(aile: str, ad: str):
    """Kap adresi TAM aile listesinden okunur — matris TEMSİLCİ kullanır, problar
    hangi kabı yoklayacaklarını KENDİ kavramlarından seçer."""
    return next((b, e) for a, x, b, e, _d in KAP_AILELERI if a == aile and x == ad)


def _kayip_cta_sayimi(baglam: str) -> frozenset:
    b, e = _kap_of("bolum-a-alani", "cta_kaliplari")
    return _gizli_kayip(
        b, e, tuple(_cit(*[f"- kalip {i}\n" for i in range(1, 6)], baglam=baglam))
    )


def _kayip_doluluk(baglam: str) -> frozenset:
    b, e = _kap_of("donem-yuvasi", "mesaj_ekseni")
    return _gizli_kayip(b, e, tuple(_cit("duz cumle govdesi\n", baglam=baglam)))


def _kayip_madde_tekrar_izi(baglam: str) -> frozenset:
    # Var olan bir maddenin çit içinde TEKRARI, tekrar notu ÜRETMEMELİ; ve
    # hiçbir notu da kaldırmamalı.
    b, e = _kap_of("bolum-a-alani", "gorsel_kodlar")
    return _gizli_kayip(
        b, e, tuple(_cit("- soft diffused light macro composition 01\n", baglam=baglam))
    )


def _kayip_bolum_boslugu(baglam: str) -> frozenset:
    b, e = _kap_of("bolum", "E")
    return _gizli_kayip(b, e, tuple(_cit("print(42)\n", baglam=baglam)))


def _kayip_c_esleme(baglam: str) -> frozenset:
    """Bölüm C kabını dolduran içerik SÖZLEŞMEDEN türer, elle yazılmaz.

    2026-09-07'ye kadar tek bir madde satırıydı; sözleşme sabit sütunlu tabloyu
    dayattığından beri kabı dolduran şey BAŞLIK SATIRI + AYIRAÇ + veri
    satırıdır — daha azı kabı zaten doldurmaz ve prob "çit gizledi" iddiasını
    kuramaz.
    """
    b, e = _kap_of("c-esleme-kabi", "C")
    return _gizli_kayip(
        b,
        e,
        tuple(
            _cit(
                "| " + " | ".join(bd.C_TABLOSU_SUTUNLARI) + " |\n",
                "|" + "---|" * len(bd.C_TABLOSU_SUTUNLARI) + "\n",
                *[
                    f"| {ad} | bulgu {i:02d} | Yayin {i:02d} | "
                    f"https://ornek.example/{i:02d} | 2025-03 | hayır |\n"
                    for i, ad in enumerate(bd.TEMEL_ALANLAR, start=1)
                ],
                baglam=baglam,
            )
        ),
    )


def _kayip_gerekce_tanima(baglam: str) -> frozenset:
    tablosuz = kaynak(tablo=False)
    citli = _sonra_ekle(
        tablosuz,
        "## Bölüm B — GÖREV B çıktısı",
        _cit(
            "| " + " | ".join(bd.GEREKCE_TABLOSU_SUTUNLARI) + " |\n",
            "|" + "---|" * len(bd.GEREKCE_TABLOSU_SUTUNLARI) + "\n",
            "| Sevgililer Günü | secildi | karma | G. |\n",
            baglam=baglam,
        ),
    )
    return frozenset(_not_kumesi(tablosuz) - _not_kumesi(citli))


def _kayip_ayri_madde(baglam: str) -> frozenset:
    b, e = _kap_of("bolum-a-alani", "kanca_kaliplari")
    return _gizli_kayip(b, e, tuple(_cit("madde isareti olmayan satir\n", baglam=baglam)))


def _gorunur(metin_citli: str, taban: str) -> set:
    return {b.mesaj for b in _not_kumesi(metin_citli) - _not_kumesi(taban)}


def _gorunur_dil_kurali(baglam: str) -> set:
    citli = _sonra_ekle(
        TEMIZ, "### gorsel_kodlar", _cit("- yumusak ışık altında çekim\n", baglam=baglam)
    )
    return _gorunur(citli, TEMIZ)


def _gorunur_uzun_alinti(baglam: str) -> set:
    govde = "> " + " ".join(f"kelime{i}" for i in range(1, 46)) + "\n"
    return _gorunur(
        _sonra_ekle(TEMIZ, "## Bölüm D — EK BULGULAR", _cit(govde, baglam=baglam)), TEMIZ
    )


def _gorunur_govde_dipnotu(baglam: str) -> set:
    return _gorunur(
        _sonra_ekle(
            TEMIZ, "## Bölüm D — EK BULGULAR", _cit("kod satiri [1]\n", baglam=baglam)
        ),
        TEMIZ,
    )


def _gorunur_tur_etiketi(baglam: str) -> set:
    return _gorunur(
        _sonra_ekle(
            TEMIZ, "## Bölüm B — GÖREV B çıktısı", _cit("ticari-fırsat\n", baglam=baglam)
        ),
        TEMIZ,
    )


def _gorunur_etiket_yazimi(baglam: str) -> set:
    return _gorunur(
        _sonra_ekle(
            TEMIZ,
            "## Bölüm D — EK BULGULAR",
            _cit("[kanal-bağımlı: instagram_magaza]\n", baglam=baglam),
        ),
        TEMIZ,
    )


def _gorunur_k120(baglam: str) -> set:
    taban = kaynak(anma_donemi="resmi")
    citli = _sonra_ekle(
        taban, "kanca: içerik-önerilmez", _cit("- gizli madde\n", baglam=baglam)
    )
    return _gorunur(citli, taban)


# ─── YAPISAL eksen (tur 11): çit içindeki BAŞLIK yuva UYDURAMAZ ────────────
#
# Tur 10'un 6000 hücresi bu bulguyu KAÇIRDI ve sebebi ölçülebilir: eksende
# YAPISAL bir boyut YOKTU — bütün gövdeler İÇERİK satırıydı, hiçbiri BAŞLIK
# değildi. Kontrolörün probu:
#
#     A) `cta_kaliplari` blogu belgeden TAMAMEN SILINDI       -> 2 not
#          * `cta_kaliplari` 0 madde tasiyor, alt sinir 5
#          * `cta_kaliplari` alan basligi Bolum A'da yok
#     B) AYNI belgeye, DILSIZ bir cit ICINE sahte baslik + 5 madde -> 0 not, gecti
#          KAYBOLAN: 2   <-- SESSIZ GIZLEME, TAM YUVA SAHTECILIGI
#
# Düzey listesi BULUNAN ÖRNEKTEN değil, belgenin KENDİ içerme modelinden türer
# (`bd._ic_ice_izler` ile aynı model): bölüm → Bölüm A alanı → video havuzu →
# dönem yuvası. Her düzeyde kap BELGEDEN SİLİNİR (yokluk notları ateşlenir) ve
# sahte başlığı bir çit İÇİNE konur; hiçbir not kaybolmamalıdır.


def _blok_sil(metin: str, baslik: str) -> tuple[str, int]:
    satirlar = metin.splitlines(True)
    i, j = _md_blok(satirlar, baslik)
    return "".join(satirlar[:i] + satirlar[j:]), i


def _donem_yuvasi_sil(metin: str, yuva_adi: str) -> tuple[str, int]:
    satirlar, k, m = _ilk_donem_yuvasi(metin, yuva_adi)
    return "".join(satirlar[:k] + satirlar[m:]), k


SAHTECILIK_DUZEYLERI = {
    "bolum": (
        lambda m: _blok_sil(m, "## Bölüm E — GÜVEN NOTU"),
        (
            "## Bölüm E — GÜVEN NOTU\n",
            "- Video kodlarinin kaynak tabani zayiftir.\n",
        ),
    ),
    "bolum-a-alani": (
        lambda m: _blok_sil(m, "### cta_kaliplari"),
        ("### cta_kaliplari\n",)
        + tuple(f"- sahte kalip {i}\n" for i in range(1, 6)),
    ),
    "video-havuzu": (
        lambda m: _blok_sil(m, "#### sahne"),
        ("#### sahne\n",)
        + tuple(f"- velvet tray reveal scene {i:02d}\n" for i in range(1, 6)),
    ),
    "donem-yuvasi": (
        lambda m: _donem_yuvasi_sil(m, "kanca"),
        ("kanca\n",)
        + tuple(f"- [an-{i}] + [urun bagi] acilis kalibi\n" for i in (1, 2)),
    ),
}


def _sahtecilik(duzey: str, baglam: str, isaret: str = "```") -> tuple[str, str]:
    """(taban, sahte) — kap BELGEDEN silinir, sahte başlığı ÇİT İÇİNE konur."""
    sil, sahte_govde = SAHTECILIK_DUZEYLERI[duzey]
    taban, yer = sil(TEMIZ)
    satirlar = taban.splitlines(True)
    sahte = "".join(
        satirlar[:yer]
        + _cit(*sahte_govde, baglam=baglam, isaret=isaret)
        + satirlar[yer:]
    )
    return taban, sahte


def _kayip_baslik_tanima(duzey: str, baglam: str, isaret: str = "```") -> frozenset:
    """Sahte başlık ÇİT İÇİNDE gizliyse HİÇBİR not düşemez.

    Tur 13: iddia gramere BAĞLI. Enjeksiyon noktası yüzünden blok gerçekte bir
    çit AÇMIYORSA (liste öğesi devamı · paragrafı bölemeyen girintili blok)
    sahte başlık GERÇEKTEN görünürdür — o hücrede notun düşmesi doğru
    davranıştır ve sahtecilik iddiası kurulamaz. Görünürlük ayrıştırıcıya
    SORULUR, elle listelenmez.
    """
    taban, sahte = _sahtecilik(duzey, baglam, isaret)
    sil, sahte_govde = SAHTECILIK_DUZEYLERI[duzey]
    on, devam = CIT_BAGLAMLARI[baglam]
    ham = sahte.splitlines()
    maske = _gramer_maskesi(ham)
    hedef = f"{devam}{sahte_govde[0]}".rstrip("\n")
    for k, satir in enumerate(ham):
        if satir == hedef and not maske[k]:
            return frozenset()  # başlık GÖRÜNÜR — gizleme iddiası yok
    return frozenset(_not_kumesi(taban) - _not_kumesi(sahte))


CIT_YAPISAL_MATRISI = tuple(
    (f"{duzey}/{baglam}/{isaret_adi}", duzey, baglam, isaret)
    for duzey in SAHTECILIK_DUZEYLERI
    for baglam in sorted(CIT_BAGLAMLARI)
    for isaret_adi, isaret in sorted(CIT_ISARETLERI.items())
)


@pytest.mark.parametrize(
    "duzey,baglam,isaret",
    [(h[1], h[2], h[3]) for h in CIT_YAPISAL_MATRISI],
    ids=[h[0] for h in CIT_YAPISAL_MATRISI],
)
def test_cit_icindeki_baslik_yuva_UYDURAMAZ(duzey, baglam, isaret) -> None:
    """SAHTECİLİK KOLU: eksik bir kap, çit içindeki sahte başlıkla DOLU görünemez."""
    kayip = _kayip_baslik_tanima(duzey, baglam, isaret)
    assert kayip == frozenset(), (
        f"{duzey}/{baglam}: çit içindeki sahte başlık şu notları KALDIRDI → "
        f"{sorted(_mesajlari(kayip))}"
    )


def test_yapisal_eksen_bos_kume_ve_taban_kollari() -> None:
    """Eksen ÜRETİLDİ mi, tabanı GERÇEKTEN not veriyor mu, hücreler boşa yeşil mi?"""
    assert len(CIT_YAPISAL_MATRISI) == (
        len(SAHTECILIK_DUZEYLERI) * len(CIT_BAGLAMLARI) * len(CIT_ISARETLERI)
    ) == 108, len(CIT_YAPISAL_MATRISI)
    assert len({h[0] for h in CIT_YAPISAL_MATRISI}) == len(CIT_YAPISAL_MATRISI)
    # Düzey listesi belgenin KENDİ içerme modelinden — dördü de gerçek kaptır.
    assert set(SAHTECILIK_DUZEYLERI) == {
        "bolum",
        "bolum-a-alani",
        "video-havuzu",
        "donem-yuvasi",
    }
    for duzey in SAHTECILIK_DUZEYLERI:
        taban, sahte = _sahtecilik(duzey, "girintisiz")
        yeni = _not_kumesi(taban) - _not_kumesi(TEMIZ)
        assert yeni, f"{duzey}: kap silinince NOT çıkmadı — hücre boşa yeşil"
        # ...ve sahte belge GERÇEKTEN büyüyor (prob belgeye dokunuyor).
        assert len(sahte.splitlines()) > len(taban.splitlines()), duzey


def test_yapisal_eksen_mutasyona_duyarli() -> None:
    """HEDEFLİ MUTASYON: maskeyi ayrıştırmadan SONRAYA al (tur 10 hâli).

    Genel mutasyon (`_cit_maskesi` tamamen sökülür) bütün eksenleri birden
    kırar ve YAPISAL boyutun bir şey ölçüp ölçmediğini gösteremez. Bu kol
    yalnız maskenin YERİNİ geri alır: satırlar maskesiz ayrıştırılır ve maske
    tur 10'daki gibi kullanım YERİNDE, bir DİLİM üstünde yeniden hesaplanır.
    """
    _BOS_KAP_ONBELLEGI.clear()
    try:
        with mock.patch.object(bd, "_maskeli_satirlar", _tur10_maskeli_satirlar), \
             mock.patch.object(bd, "_citsiz_satirlar", _tur10_citsiz_satirlar):
            kirmizi = {
                ad
                for ad, duzey, baglam, isaret in CIT_YAPISAL_MATRISI
                if _kayip_baslik_tanima(duzey, baglam, isaret)
            }
    finally:
        _BOS_KAP_ONBELLEGI.clear()
    assert kirmizi, "maske ayrıştırmadan SONRAYA alınınca eksen KIRILMADI"
    # Kırmızı DÖRT düzeyin hepsine ve HER bağlama yayılır: yapısal açık tek bir
    # düzeye ya da tek bir bağlama özgü değildi.
    assert {ad.split("/")[0] for ad in kirmizi} == set(SAHTECILIK_DUZEYLERI)
    assert {ad.split("/")[1] for ad in kirmizi} == set(CIT_BAGLAMLARI)
    # 96 hücrenin 96'sı da kırılır: yapısal açık HİÇBİR düzeyde ve HİÇBİR
    # bağlamda kapalı DEĞİLDİ.
    assert len(kirmizi) == 93, len(kirmizi)


def _tur10_maskeli_satirlar(metin: str):
    """Tur 10 hâli: ayrıştırma maskeyi HİÇ görmez."""
    return [bd._Satir(satir, False) for satir in metin.splitlines()]


def _tur10_citsiz_satirlar(satirlar):
    """Tur 10 hâli: maske kullanım YERİNDE, DİLİM üstünde yeniden hesaplanır."""
    return [
        satir
        for satir, cit_icinde in zip(satirlar, bd._cit_maskesi(satirlar))
        if not cit_icinde
    ]


# ─── KAP GEÇİŞİ ekseni (tur 11): çit bir kap sınırını AŞARSA ───────────────
#
# İkinci ölçülmüş açık, çitin KAP SINIRINI aşmasıydı. Taban her hücrede,
# AÇICININ bulunduğu kabın notlarıdır: yutulan bölgenin notları tabana
# KONMAZ (yutulan bölge zaten görünmez olur ve o, fail-closed yöndür).
GECIS_BICIMLERI = ("alan-siniri", "bolum-siniri", "kapanmamis-belge-sonu")


def _gecis_probu(gecis: str, baglam: str) -> tuple[str, str]:
    on, devam = CIT_BAGLAMLARI[baglam]
    if gecis == "alan-siniri":
        # Açıcı `cta_kaliplari` içinde, kapatıcı `kanca_kaliplari` içinde:
        # arada `### kanca_kaliplari` BAŞLIĞI var.
        bosalt, _ = _kap_of("bolum-a-alani", "cta_kaliplari")
        taban = bosalt(TEMIZ)
        satirlar = taban.splitlines(True)
        i = next(k for k, x in enumerate(satirlar) if x.strip() == "### cta_kaliplari")
        j = next(k for k, x in enumerate(satirlar) if x.strip() == "### kanca_kaliplari")
        gecisli = "".join(
            satirlar[: i + 1]
            + [f"{on}```\n", f"{devam}print(42)\n"]
            + satirlar[i + 1 : j + 1]
            + [f"{devam}```\n"]
            + satirlar[j + 1 :]
        )
        return taban, gecisli
    if gecis == "bolum-siniri":
        # Açıcı Bölüm D'de, kapatıcı Bölüm E'de: arada `## Bölüm E` BAŞLIĞI var.
        bosalt, _ = _kap_of("bolum", "D")
        taban = bosalt(TEMIZ)
        satirlar = taban.splitlines(True)
        i = next(
            k for k, x in enumerate(satirlar) if x.strip().startswith("## Bölüm D")
        )
        j = next(
            k for k, x in enumerate(satirlar) if x.strip().startswith("## Bölüm E")
        )
        gecisli = "".join(
            satirlar[: i + 1]
            + [f"{on}```\n", f"{devam}print(42)\n"]
            + satirlar[i + 1 : j + 1]
            + [f"{devam}```\n"]
            + satirlar[j + 1 :]
        )
        return taban, gecisli
    # KAPANMAMIŞ: açıcı `cta_kaliplari` içinde, kapatıcı YOK — kök düzeyinde
    # açılmışsa belge sonuna kadar fail-closed düşer, kap içinde açılmışsa kabı
    # bitiren ilk satırda biter.
    bosalt, ekle = _kap_of("bolum-a-alani", "cta_kaliplari")
    taban = bosalt(TEMIZ)
    return taban, ekle(taban, (f"{on}```\n", f"{devam}print(42)\n"))


CIT_GECIS_MATRISI = tuple(
    (f"{gecis}/{baglam}", gecis, baglam)
    for gecis in GECIS_BICIMLERI
    for baglam in sorted(CIT_BAGLAMLARI)
)


# Beklenti BAĞLAMDAN TÜRER, hücreden değil: KÖK düzeyinde (sütun 0) açılan bir
# çidi hiçbir satır bitiremez, dolayısıyla kapatıcıya kadar her şeyi YUTAR — ve
# yuttuğu KABIN eksikliği RAPORLANMAK zorundadır (fail-closed). Bir KAP İÇİNDE
# açılan çit ise kabı bitiren ilk satırda BİTER; hiçbir şey yutulmaz ve hiçbir
# not kaybolmaz. Tur 10'da bu ayrım YOKTU: kap içinde açılan çit de uzaktaki
# ayıraca kadar yutuyordu (mutasyon kolu bunu ölçer).
_YUTULAN_IZLER = {
    "alan-siniri": "`kanca_kaliplari` alan başlığı Bölüm A'da yok",
    "bolum-siniri": "Bölüm E yok — beş bölümlü çıktı biçimi zorunludur",
    "kapanmamis-belge-sonu": "Bölüm B yok — beş bölümlü çıktı biçimi zorunludur",
}


def _gecis_rejimi(baglam: str) -> str:
    """Rejim ÖNEKTEN değil, modülün KAP KURALINDAN türer.

    Tur 11'e dek ölçüt `önek == ""` idi, yani boşluktan ibaret HER önek kap
    sayılıyordu. Tur 13'ten beri ölçüt GRAMERİN KENDİSİDİR (`_cit_rejimi`):
    test bir kural kopyalamaz, ayrıştırıcıya sorar.
    """
    return _cit_rejimi(CIT_BAGLAMLARI[baglam][0])


def _gecis_ihlali(gecis: str, baglam: str) -> str:
    taban, gecisli = _gecis_probu(gecis, baglam)
    kayip = frozenset(_not_kumesi(taban) - _not_kumesi(gecisli))
    yeni = _mesajlari(_not_kumesi(gecisli) - _not_kumesi(taban))
    if _gecis_rejimi(baglam) == "kap-biter":
        return (
            f"kap içinde açılan çit KABI AŞTI, şu notlar KALDIRILDI: "
            f"{sorted(_mesajlari(kayip))}"
            if kayip
            else ""
        )
    iz = _YUTULAN_IZLER[gecis]
    return (
        ""
        if any(iz in mesaj for mesaj in yeni)
        else f"KÖK çiti yuttu ama eksikliği RAPORLAMADI ({iz!r}): {sorted(yeni)}"
    )


@pytest.mark.parametrize(
    "gecis,baglam",
    [(h[1], h[2]) for h in CIT_GECIS_MATRISI],
    ids=[h[0] for h in CIT_GECIS_MATRISI],
)
def test_cit_kap_sinirini_asarsa_fail_closed(gecis: str, baglam: str) -> None:
    """KAP GEÇİŞİ KOLU: kap içindeki çit kabı AŞMAZ; kök çiti yutar ama SUSMAZ."""
    assert _gecis_ihlali(gecis, baglam) == "", f"{gecis}/{baglam}"


def test_gecis_ekseni_bos_kume_ve_taban_kollari() -> None:
    assert len(CIT_GECIS_MATRISI) == len(GECIS_BICIMLERI) * len(CIT_BAGLAMLARI) == 27
    # İKİ rejim de GERÇEKTEN üretiliyor — kol tek yanlı değil.
    rejimler = {_gecis_rejimi(b) for b in CIT_BAGLAMLARI}
    assert rejimler == {"yutar", "kap-biter"}, rejimler
    for _ad, gecis, baglam in CIT_GECIS_MATRISI:
        taban, gecisli = _gecis_probu(gecis, baglam)
        assert _not_kumesi(taban), f"{gecis}: taban BOŞ — hücre boşa yeşil"
        assert len(gecisli.splitlines()) > len(taban.splitlines()), gecis
        if _gecis_rejimi(baglam) == "yutar":
            # Yutma GERÇEKTEN oluyor: fail-closed yönde YENİ notlar çıkıyor.
            assert _not_kumesi(gecisli) - _not_kumesi(taban), f"{gecis}/{baglam}"


def test_gecis_ekseni_mutasyona_duyarli() -> None:
    """MUTASYON: kap sonlanmasını sök → `kap-biter` rejimi KIRILSIN.

    Tur 10'un davranışı buydu: kap içinde açılan çit de uzaktaki ayıraca kadar
    yutuyordu. Kol, kap sonlanmasının GERÇEKTEN bir şey ölçtüğünü gösterir.
    """
    # Tur 13: kap sonlanmasi artik gramerin icindedir; sokulemez. Esdeger
    # mutasyon KAP FARKINDALIGI OLMAYAN donmus mutanttir (`tur9`).
    with mock.patch.object(bd, "_cit_maskesi", MUTANTLAR["tur9"]):
        kirmizi = {
            ad
            for ad, gecis, baglam in CIT_GECIS_MATRISI
            if _gecis_rejimi(baglam) == "kap-biter" and _gecis_ihlali(gecis, baglam)
        }
    assert kirmizi, "kap sonlanması sökülünce `kap-biter` rejimi KIRILMADI"
    # KÖK rejimindeki hiçbir bağlam girmez — onlar zaten `yutar` rejimindedir.
    # Ölçüt bağlam ADINDAN değil REJİMDEN türer (tur 12: kök kümesi artık
    # `girintisiz` tek üyeli DEĞİL — 0-3 boşluklu her açıcı köktür).
    assert not any(
        _gecis_rejimi(ad.split("/", 1)[1]) == "yutar" for ad in kirmizi
    ), sorted(kirmizi)
    # DÜRÜST BOŞ HÜCRE KAYDI: kırmızı İKİ geçiş biçimine yayılır, üçüncüsüne
    # DEĞİL. `kapanmamis-belge-sonu` mutasyon altında da YEŞİL kalır ve sebebi
    # ölçülmüştür, unutulmuş değildir: o hücrenin taban notları AÇICININ kendi
    # kabı hakkındadır (`cta_kaliplari` boş + 0 madde) ve yutulan bölge o kabın
    # DIŞINDADIR — yutmak not EKLER, kaldırmaz. Sınırı ölçen boyut budur:
    # kaybı ancak bir KABIN BAŞLIĞI yutulduğunda görürsün.
    # Tur 13: donmuş `tur9` mutantı kap farkındalığını TAMAMEN kaldırdığı için
    # kırmızı ÜÇ geçiş biçimine birden yayılır (tur 12'de mutasyon yalnız kap
    # sonlanmasını söküyordu ve `kapanmamis-belge-sonu` yeşil kalıyordu).
    # 15 = 5 gerçek KAP bağlamı × 3 geçiş biçimi.
    assert {ad.split("/")[0] for ad in kirmizi} == set(GECIS_BICIMLERI), sorted(kirmizi)
    assert len(kirmizi) == 15, len(kirmizi)
    assert len(kirmizi) == len(GECIS_BICIMLERI) * sum(
        1 for baglam in CIT_BAGLAMLARI if _gecis_rejimi(baglam) == "kap-biter"
    ), sorted(kirmizi)


# ─── İÇ İÇE ÇİT BİLEŞİMLERİ (tur 11) — hakemin ölçtüğü bileşim ─────────────
#
# `- ```python ` (dilli açıcı) → girintili gövde → kabı bitiren KÖK paragraf →
# kökte DİLSİZ çit. CommonMark bunu İKİ ayrı çit olarak ayrıştırır; tur 10'un
# makinesi dilli durumu kök açıcıya kadar sürdürüp DİLSİZ çitin beş maddesini
# maskesiz bırakıyordu. Kabı bitiren satır olarak markdown TABLOSU seçildi:
# tablo sözleşme biçimi DEĞİLDİR (`_sozlesme_bicimli`), dolayısıyla kabı
# doldurmaz ve prob YALNIZ çit davranışını ölçer.
_KAP_BITIREN = "| kap | bitti |\n"

# Tur 12 — ARA boyutu. Tur 11'in bileşimi kök ayıracından ÖNCE her zaman
# `_KAP_BITIREN` paragrafını koyuyordu, dolayısıyla kabın kırılması kök ayıracına
# GELMEDEN gerçekleşiyordu ve BİTİŞİK vaka hiç üretilmiyordu. Ölçüldü ki bitişik
# hâlde kapatıcı eşleşmesi kap kontrolünden ÖNCE koşuyor, kök ayıracı liste
# içindeki çitin KAPATICISI sanılıyor ve sonrası maskesiz kalıyordu. CommonMark
# ise kabı ÖNCE bitirir: kök ayıracı YENİ bir çit açar. Boyut kavramdan türer
# (araya kap-bitiren bir satır girer / girmez), bulunan örnekten değil.
BILESIM_ARALARI = {"paragrafli": (_KAP_BITIREN,), "bitisik": ()}

_BILESIM_ACICILARI = {
    # (açıcı dil etiketi, açıcı bağlamı)
    "dilli-acici-kap-kirilmasi": ("python", "madde-isaretli"),
    "dilsiz-acici-kap-kirilmasi": ("", "madde-isaretli"),
    "ic-ice-madde-kap-kirilmasi": ("python", "ic-ice-madde"),
    "yildiz-madde-kap-kirilmasi": ("python", "yildiz-madde"),
    "sirali-liste-kap-kirilmasi": ("python", "sirali-liste"),
}

BILESIM_BICIMLERI = {
    f"{acici}/{ara}": (dil, baglam, ara)
    for acici, (dil, baglam) in _BILESIM_ACICILARI.items()
    for ara in BILESIM_ARALARI
}


def _bilesim_govdesi(bilesim: str) -> tuple[str, ...]:
    dil, baglam, ara = BILESIM_BICIMLERI[bilesim]
    on, devam = CIT_BAGLAMLARI[baglam]
    return (
        (f"{on}```{dil}\n", f"{devam}| govde | satiri |\n")
        + BILESIM_ARALARI[ara]
        + ("```\n",)
        + tuple(f"- gizli kalip {i}\n" for i in range(1, 6))
        + ("```\n",)
    )


def _bilesim_ihlali(bilesim: str) -> str:
    """Uzak DİLSİZ çitin GİZLİ maddeleri sözleşme sayımına GİRMEMELİ.

    İddia dar ve ölçülebilir tutuldu: bileşimin İLK çiti bir kap içinde açılır
    ve gerçek markdown'da AÇIK kalem olabilir (dilli çit bir kabı DOLDURUR —
    ilan edilmiş karar), dolayısıyla "hiçbir not kaybolmaz" bu eksende YANLIŞ
    bir iddia olurdu ve ölçüldü: `- ```python ` satırının KENDİSİ sözleşme
    biçimli bir maddedir. Ölçülen şey UZAKTAKİ çitin gövdesidir: beş `gizli
    kalip` maddesi ESSİZ madde sayımına girerse `alt sınırı 5` notu SUSAR —
    tur 10'un davranışı tam olarak buydu.
    """
    bosalt, ekle = _kap_of("bolum-a-alani", "cta_kaliplari")
    rapor = bd.run(ekle(bosalt(TEMIZ), _bilesim_govdesi(bilesim)), source_name="P")
    mesajlar = [b.mesaj for b in rapor.notlar]
    if not any("alt sınırı 5" in m for m in mesajlar):
        return f"{bilesim}: uzak DİLSİZ çidin maddeleri SAYILDI — alt sınır notu SUSTU"
    if any("gizli kalip" in m for m in mesajlar):
        return f"{bilesim}: gizli maddeler sözleşme yüzeyine SIZDI"
    if rapor.sonuc == bd.SONUC_GECTI:
        return f"{bilesim}: rapor `gecti` — bileşim kapıyı sustur[du]"
    return ""


@pytest.mark.parametrize("bilesim", sorted(BILESIM_BICIMLERI))
def test_ic_ice_cit_bilesimi_uzak_citi_MASKELI_kalir(bilesim: str) -> None:
    """İÇ İÇE BİLEŞİM KOLU: uzaktaki kök ayıracı, kap içindeki çitin KAPATICISI DEĞİLDİR."""
    assert _bilesim_ihlali(bilesim) == ""


def test_bilesim_ekseni_mutasyona_ve_bos_kumeye_duyarli() -> None:
    """MUTASYON: donmuş `tur10` mutantı — uzak kök ayıracını kapatıcı sanar.

    Mutant SEÇİLMEDİ, ÖLÇÜLDÜ: üç donmuş mutant da koşuldu ve bu eksende
    yalnız `tur10` kırmızı veriyor (10 bileşimin 3'ü). `tur9` liste işaretli
    açıcıyı hiç TANIMIYOR, `tur12` kap sonlanmasını zaten modelliyor — ikisi de
    bu ekseni kıramaz ve bu, eksenin NEYİ ölçtüğünün kaydıdır.
    """
    bosalt, _ekle = _kap_of("bolum-a-alani", "cta_kaliplari")
    assert _bos_kap_notlari(bosalt), "taban BOŞ — kol boşa yeşil"
    _BOS_KAP_ONBELLEGI.clear()
    try:
        with mock.patch.object(bd, "_cit_maskesi", MUTANTLAR["tur10"]):
            kirmizi = {b for b in BILESIM_BICIMLERI if _bilesim_ihlali(b)}
    finally:
        _BOS_KAP_ONBELLEGI.clear()
    # ÖLÇÜLDÜ (tur 13): `tur10` mutantı 10 bileşimin 3'ünü kırar ve üçü de
    # `bitisik` ARA değerindedir. Bu, tur 12'de eklenen ARA boyutunun NE
    # ölçtüğünün kaydıdır: araya kabı bitiren bir paragraf girdiğinde eski
    # makine de doğru davranıyordu; açık YALNIZ bitişik ayıraçta vardı.
    assert kirmizi == {
        "dilli-acici-kap-kirilmasi/bitisik",
        "dilsiz-acici-kap-kirilmasi/bitisik",
        "ic-ice-madde-kap-kirilmasi/bitisik",
    }, sorted(kirmizi)
    # DÜRÜST BOŞ HÜCRE KAYDI: `yildiz-madde` ve `sirali-liste` bitişik
    # hücreleri mutant altında da YEŞİL kalır — `tur10` deseni o iki liste
    # işaretini zaten TANIMIYORDU (tur 11'in kazanımı), dolayısıyla o
    # hücrelerde açıcı hiç çit sayılmıyor ve kap geçişi sorusu doğmuyor.
    assert all(ad.endswith("/bitisik") for ad in kirmizi), sorted(kirmizi)
    # AŞIRI SIKILAŞTIRMA KOLU: kap KIRILDIKTAN sonra gelen GERÇEK içerik hâlâ
    # kabı DOLDURUR — kap sonlanması yalnız çitin kapsamını bitirir, sonrasını
    # görünmez YAPMAZ.
    _BOS_KAP_ONBELLEGI.clear()
    bos = bosalt(TEMIZ)
    _, ekle = _kap_of("bolum-a-alani", "cta_kaliplari")
    kirildi_ve_doldu = ekle(
        bos, ("- ```\n", "  print(42)\n", "gerçek bir kalıp satırı.\n")
    )
    assert "`cta_kaliplari` alanı boş" not in _mesajlari(
        _not_kumesi(kirildi_ve_doldu)
    ), "kap kırıldıktan SONRAKİ gerçek içerik kabı DOLDURMUYOR — aşırı sıkılaştırma"
    _BOS_KAP_ONBELLEGI.clear()


def test_kapanmamis_kok_citinin_bedeli_OLCULUR() -> None:
    """İSTİSNANIN SINIRI: ham kayıp ADIYLA sabitlenir, sessizce genişleyemez.

    Değişmez KONU düzeyindedir (`_cit_sinif_kaybi`): bir çit hiçbir konuyu
    susturamaz. Ham mesaj düzeyinde ise KÖK düzeyinde kapanmamış bir çit
    belgenin gerisini yutar ve SAYIM taşıyan bir notu daha SIKI bir sayıyla
    yeniden yazabilir. Bu kol o hücreleri TEK TEK sayar ve her birinde (a) aynı
    KONUNUN hâlâ konuştuğunu, (b) sayının ARTMADIĞINI ölçer.
    """
    ham_kayipli = {
        ad: _cit_kaybi(bosalt, ekle, satirlar)
        for ad, dil, _g, _gs, bosalt, ekle, satirlar in CIT_MATRISI
        if dil == "dilsiz" and _cit_kaybi(bosalt, ekle, satirlar)
    }
    # Beklenti KAVRAMDAN türer (kök rejimi × kapanmamış × video havuzu), sonra
    # kapsama dizisinin SEÇTİĞİ hücrelerle kesiştirilir — matris küçüldüğü için
    # beklenti listesi elle kısaltılmaz, kesişim ÜRETİLİR.
    secilenler = {hucre[0] for hucre in CIT_MATRISI}
    beklenen_ham = HAM_KAYIPLI_HUCRELER & secilenler
    assert beklenen_ham, "kapsama dizisi bu sınıftan hiç hücre seçmedi"
    assert set(ham_kayipli) == beklenen_ham, sorted(
        set(ham_kayipli) ^ beklenen_ham
    )
    for ad, kayip in ham_kayipli.items():
        bosalt, ekle, satirlar = next(
            (h[4], h[5], h[6]) for h in CIT_MATRISI if h[0] == ad
        )
        yeni = _not_kumesi(ekle(bosalt(TEMIZ), satirlar))
        for bulgu in kayip:
            konu = _SAYI_RE.sub("#", bulgu.mesaj)
            esler = [b.mesaj for b in yeni if _SAYI_RE.sub("#", b.mesaj) == konu]
            assert esler, f"{ad}: KONU SUSTU → {bulgu.mesaj!r}"
            eski_sayi = [int(x) for x in _SAYI_RE.findall(bulgu.mesaj)]
            for es in esler:
                assert [int(x) for x in _SAYI_RE.findall(es)] <= eski_sayi, (
                    f"{ad}: sayı ARTTI (daha gevşek yön) → {es!r}"
                )


CIT_KAPSANAN_PROBLARI = {
    "doluluk": _kayip_doluluk,
    "adet-sayimi": _kayip_cta_sayimi,
    "madde-tekrar-izi": _kayip_madde_tekrar_izi,
    "bolum-boslugu": _kayip_bolum_boslugu,
    "c-esleme-satiri": _kayip_c_esleme,
    "gerekce-tablosu-tanima": _kayip_gerekce_tanima,
    "ayri-madde-isareti": _kayip_ayri_madde,
    "baslik-ve-bolum-tanima": lambda baglam: _kayip_baslik_tanima(
        "bolum-a-alani", baglam
    ),
}
# Kapsam DIŞI yolda çit içeriği HÂLÂ GÖRÜLÜR: prob, çitli hâlin ÜRETTİĞİ yeni
# notlarda beklenen izin geçtiğini ölçer. "Unutuldu" sanılmasın diye BİLİNÇLİ
# yanlış-negatif/pozitif kararı böyle SABİTLENİR.
CIT_DISI_PROBLARI = {
    "dil-kurali": (_gorunur_dil_kurali, "İNGİLİZCE olmalı"),
    "uzun-alinti": (_gorunur_uzun_alinti, "kelimelik kesintisiz alıntı"),
    "govde-dipnotu": (_gorunur_govde_dipnotu, "dipnot/atıf işareti"),
    "tur-etiketi-ascii": (_gorunur_tur_etiketi, "ASCII yazımda değil"),
    "etiket-yazimi": (_gorunur_etiket_yazimi, "Kanal etiketi anahtarı"),
    "k120-bilincli-bos": (_gorunur_k120, "alt sınır"),
}


def test_cit_kapsam_envanteri_adlari_modulden_turer() -> None:
    """Ad kümeleri modülün İKİ demetiyle BİREBİR eşleşir — kalem eklenip
    prob yazılmadıysa (ya da tersi) test KIRILIR."""
    assert set(CIT_KAPSANAN_PROBLARI) == {ad for ad, _ in bd.CIT_KURALI_KAPSAMI}
    assert set(CIT_DISI_PROBLARI) == {ad for ad, _ in bd.CIT_KURALI_DISINDA}
    assert not (set(CIT_KAPSANAN_PROBLARI) & set(CIT_DISI_PROBLARI))
    assert len(bd.CIT_KURALI_KAPSAMI) == 8 and len(bd.CIT_KURALI_DISINDA) == 6
    # Beyan METNİ iki demetten ÜRETİLİR ve her kalem adıyla geçer.
    beyan = next(
        b
        for b in bd.run(TEMIZ, source_name="P").kapsam_sinirlari
        if b.startswith("bolum-ve-alan-tamligi/cit-kapsami")
    )
    for ad, gerekce in bd.CIT_KURALI_KAPSAMI + bd.CIT_KURALI_DISINDA:
        assert ad in beyan and gerekce in beyan, ad
    # ÜÇÜNCÜ ayak (tur 10): BAĞLAM ve AYIRAÇ envanterleri de beyanı ÜRETİR ve
    # her kalem UÇTAN UCA ölçülür — beyan "bağlamdan bağımsız" diyorsa o bağlam
    # GERÇEKTEN maskelenmelidir. Altıncı bayat beyan olamaz.
    assert "BAĞLAMDAN BAĞIMSIZDIR" in beyan
    assert bd.CIT_BAGLAM_BICIMLERI and bd.CIT_AYIRAC_BICIMLERI, "envanter BOŞ"
    bosalt, ekle = _kap_of("donem-yuvasi", bd.OZEL_GUN_YUVALARI[0])
    assert _bos_kap_notlari(bosalt), "taban BOŞ — kapı boşa yeşil"
    for baglam_adi, on, devam in bd.CIT_BAGLAM_BICIMLERI:
        assert baglam_adi in beyan, baglam_adi
        for isaret_adi, isaret in bd.CIT_AYIRAC_BICIMLERI:
            assert isaret_adi in beyan and isaret in beyan, isaret_adi
            kayip = _cit_kaybi(
                bosalt,
                ekle,
                (f"{on}{isaret}\n", f"{devam}print(42)\n", f"{devam}{isaret}\n"),
            )
            assert kayip == frozenset(), (
                f"{baglam_adi}/{isaret_adi}: BEYAN BAYAT — {sorted(_mesajlari(kayip))}"
            )
    # ...ve beyanın AŞIRI SIKILAŞTIRMA iddiası da ölçülür: meşru madde DOLDURUR.
    assert "AŞIRI SIKILAŞTIRMA YAPILMADI" in beyan
    assert _cit_kaybi(bosalt, ekle, ("- gerçek bir kalıp\n",))


@pytest.mark.parametrize("baglam", sorted(CIT_BAGLAMLARI))
@pytest.mark.parametrize("ad", sorted(CIT_KAPSANAN_PROBLARI))
def test_cit_kurali_kapsanan_yolda_not_kaldirmaz(ad: str, baglam: str) -> None:
    """KAPSANAN yol: çit içine içerik koymak HİÇBİR notu kaldırmaz (küme farkı).

    BAĞLAM ekseni tur 10'da eklendi ve iddia ÖLÇÜLÜR, varsayılmaz: kural TEK
    evde (`_cit_maskesi`) genişletildiğine göre YEDİ yolun HEPSİ yeni
    bağlamlardan otomatik faydalanmalıdır — 7 × 5 hücrenin hepsi burada koşar.
    """
    kayip = CIT_KAPSANAN_PROBLARI[ad](baglam)
    assert kayip == frozenset(), f"{ad}/{baglam}: KALDIRDI → {sorted(_mesajlari(kayip))}"


@pytest.mark.parametrize("baglam", sorted(CIT_BAGLAMLARI))
@pytest.mark.parametrize("ad", sorted(CIT_DISI_PROBLARI))
def test_cit_kurali_disindaki_yol_citi_HALA_gorur(ad: str, baglam: str) -> None:
    """KAPSAM DIŞI yol: BİLİNÇLİ karar — çit içeriği hâlâ görülür ve sabitlenir.

    Bu da HER bağlamda ölçülür: bağlam boyutu kapsam dışı yolları da
    kaydırmamalı — ne yeni bir kayıp açmalı ne de ilan edilmiş görünürlüğü
    kapatmalı.
    """
    prob, iz = CIT_DISI_PROBLARI[ad]
    yeni = prob(baglam)
    assert any(iz in mesaj for mesaj in yeni), f"{ad}/{baglam}: {iz!r} yok → {sorted(yeni)}"


def test_cit_govdesi_uydurma_bicim_notu_uretmez() -> None:
    """`ayri-madde-isareti` süpürmesinin AYRI ayağı: NOT KAYBI değil TUTARLILIK.

    Bu yol bir not KAYBI kapatmıyordu — çit eklemek not eklemekle sonuçlanıyordu.
    Süpürmenin gerekçesi tutarlılıktır: modül aynı satırları doluluk ve adet
    yollarında içerik SAYMAZ; "bu içerik satırı madde işareti taşıyor mu" diye
    sorup çitin AYIRACINA not düşmek kapının kendi içinde çelişmesidir. Ölçüm
    kontrolörün probundan gelir: DİLSİZ çit içine beş madde konduğunda eski hâl
    `'```'` satırı için uydurma bir biçim notu üretiyordu.
    """
    bosalt, ekle = _kap_of("bolum-a-alani", "cta_kaliplari")
    bos = bosalt(TEMIZ)
    citli = ekle(bos, tuple(_cit(*[f"- kalip {i}\n" for i in range(1, 6)])))
    yeni = _mesajlari(_not_kumesi(citli) - _not_kumesi(bos))
    assert yeni == set(), f"çit gövdesi UYDURMA not üretti: {sorted(yeni)}"
    # ...ve mesaj KÜMESİ ikisinde de AYNI: ne kayıp ne fazlalık.
    assert _not_kumesi(citli) == _not_kumesi(bos)


# ─── CommonMark SINIR EKSENİ (tur 13) — gramer bizim değil, ONUN ────────────
#
# Tur 8-12 boyunca çit maskesi ELLE yazılmış bir CommonMark yaklaşımıydı ve her
# turda gramerin kodlanmamış bir kuralı daha çıktı: liste işaretleri → açılış
# girintisi → kapatıcı sırası → KAPATICI GİRİNTİSİ → iç içe işaret derinliği.
# Beşinci sınır kuralını yazmak yerine gramer KOŞTURULUYOR (`markdown-it-py`,
# CommonMark referans uyumlu). Aşağıdaki üç prob tur 10'un bağımsız hakem
# turunda bildirilen ve kontrolörün KENDİ probuyla yeniden ürettiği kaçışlardır.
#
# Saldırının biçimi: erken KABUL EDİLEN bir kapatıcıdan SONRA sahte alan gelir.
# CommonMark kapatıcının en fazla ÜÇ boşluk girintili olmasını şart koşar
# (§4.5); daha girintili ayıraç kapatıcı DEĞİLDİR ve çit AÇIK kalır.
COMMONMARK_SINIR_PROBLARI = {
    "kok-cit-4-bosluk-kapatici": (["```", "print(1)", "    ```"], ["```"]),
    "kok-cit-tab-kapatici": (["```", "print(1)", "\t```"], ["```"]),
}

# ÖLÇÜLDÜ ve KAÇIŞ DEĞİL (tur 13): `- ``` ` + `      ``` ` bileşimini hem hakem
# hem kontrolör kaçış sandı. Gramere soruldu — markdown-it o ayıracı KAPATICI
# SAYMIYOR; çit liste ÖĞESİ bitince kapanıyor ve sonraki kök başlığı
# GERÇEKTEN görünür oluyor (render'da `<h3>` olarak çıkıyor). Notun düşmesi
# DOĞRU davranıştır. Hücre silinmiyor, KONTROL KOLUNA taşınıyor: yanlış
# pozitifin kendisi kayda geçer ki bir sonraki tur onu yeniden "kaçış" diye
# açmasın.
GORUNURLUK_KONTROL_PROBLARI = {
    "liste-citi-6-bosluk-kapatici": (["- ```", "  print(1)", "      ```"], ["```"]),
    "gecerli-3-bosluk-kapatici": (["```", "print(1)", "   ```"], []),
}


def _sinir_probu(on: list[str], son: list[str]) -> tuple[frozenset, frozenset]:
    """(taban notları, prob notları) — `cta_kaliplari` bloğu SİLİNMİŞ belgede."""
    bosalt, ekle = _kap_of("bolum-a-alani", "cta_kaliplari")
    bos = bosalt(TEMIZ)
    sahte = tuple(
        f"{satir}\n"
        for satir in on
        + ["### cta_kaliplari"]
        + [f"- [urun-{k}] icin randevu daveti — satis — vurgu." for k in range(1, 6)]
        + son
    )
    return frozenset(_bos_kap_notlari(bosalt)), frozenset(_not_kumesi(ekle(bos, sahte)))


# Tur 11 (bagimsiz hakem) — AYRISTIRICI SINIRI. Hakem `maxNesting`
# korumasinin fail-open urettigini bildirdi; kontrolor kendi probuyla
# dogruladi: sinir 10'da kapali, 11'de acikti. `_MD` yapilandirmasi
# yukseltildi; kol sinirin GERCEKTEN kalktigini derinlik derinlik olcer.
IC_ICE_DERINLIKLERI = (9, 11, 25, 60, 99)


def _ic_ice_probu(derinlik: int) -> tuple[frozenset, frozenset]:
    """İç içe geçme BLOCKQUOTE ile kurulur, madde listesiyle DEĞİL.

    Ölçüldü: iç içe `- x` maddeleri sözleşmenin GERÇEK maddeleridir ve kabı
    MEŞRU olarak doldururlar; o kuyrukla kurulan prob adet notunu her
    derinlikte düşürür ve ayrıştırıcı sınırını hiç ölçmez. Blockquote da
    `maxNesting` sayacını aynı şekilde tüketir ama sözleşme içeriği DEĞİLDİR.
    """
    on = "> " * derinlik
    bosalt, ekle = _kap_of("bolum-a-alani", "cta_kaliplari")
    bos = bosalt(TEMIZ)
    sahte = (
        (f"{on}```\n", f"{on}### cta_kaliplari\n")
        + tuple(f"{on}- [urun-{k}] x.\n" for k in range(1, 6))
    )
    return frozenset(_bos_kap_notlari(bosalt)), frozenset(_not_kumesi(ekle(bos, sahte)))


@pytest.mark.parametrize("derinlik", IC_ICE_DERINLIKLERI)
def test_ic_ice_liste_derinligi_sahte_yuva_KURDURMAZ(derinlik: int) -> None:
    """Ayrıştırıcının iç içe geçme sınırı bir fail-open ÜRETMEMELİ."""
    taban, prob = _ic_ice_probu(derinlik)
    kayip = taban - prob
    assert kayip == frozenset(), (
        f"derinlik {derinlik}: sahte yuva KURULDU → {sorted(_mesajlari(kayip))}"
    )


def test_ic_ice_ekseni_taban_ve_sinir_kollari() -> None:
    """Taban not veriyor mu; ve sınırın SONLU olduğu ilan edildi mi?"""
    taban, _prob = _ic_ice_probu(9)
    assert taban, "taban BOŞ — kol boşa yeşil"
    # Sınır SONLUDUR ve bu KAYITLIDIR: yapılandırılan değerin ÜSTÜNDE aynı
    # sınıf yeniden açılır. Beyan bayatlamasın diye TRIPWIRE olarak ölçülür.
    sinir = bd._MD.options["maxNesting"]
    assert sinir == 100, sinir
    # Sınırın ÜSTÜNDE sınıf yeniden açılır — beyan bayatlamasın diye ÖLÇÜLÜR.
    taban_a, prob_a = _ic_ice_probu(sinir + 50)
    assert taban_a - prob_a, (
        "ilan edilen sınır ÖLÇÜLMÜYOR — sınırın üstünde açık GÖRÜNMÜYOR, "
        "yani beyan bayat"
    )
    # ...ve ÇOK derin belge ÇÖKMEZ. Bu ölçüm bir GERİ ALMANIN kaydıdır:
    # sınır önce 1000 denendi ve o eşikte 1200 kat iç içe blockquote
    # ayrıştırıcıyı `RecursionError` ile düşürüyordu — yüksek sınır fail-open'ı
    # kapatırken bir ÇÖKME yolu açıyordu. 100'de ayrıştırıcı sınıra takılıp
    # duruyor, özyinelemeye inmiyor.
    for derin in (500, 2000, 5000):
        maske = bd._cit_maskesi(["> " * derin + "x", "metin"])
        assert len(maske) == 2, derin
    # `RecursionError` yolu yine de FAIL-CLOSED bağlanmıştır (savunma katmanı):
    # ayrıştırıcı bir gün düşerse maske boş DEĞİL, TAMAMEN literal döner.
    with mock.patch.object(bd._MD, "parse", side_effect=RecursionError):
        assert bd._cit_maskesi(["a", "b", "c"]) == [True, True, True]


@pytest.mark.parametrize("ad", sorted(COMMONMARK_SINIR_PROBLARI))
def test_commonmark_sinirinda_sahte_yuva_KURULAMAZ(ad: str) -> None:
    """Erken kabul edilen kapatıcıdan sonraki sahte başlık ALAN KURAMAZ."""
    on, son = COMMONMARK_SINIR_PROBLARI[ad]
    taban, prob = _sinir_probu(on, son)
    kayip = taban - prob
    assert kayip == frozenset(), (
        f"{ad}: sahte yuva KURULDU, şu notlar kalktı → {sorted(_mesajlari(kayip))}"
    )


@pytest.mark.parametrize("ad", sorted(GORUNURLUK_KONTROL_PROBLARI))
def test_gramer_gorunur_icerigi_MASKELEMEZ(ad: str) -> None:
    """AŞIRI SIKILAŞTIRMA KOLU: gramere göre GÖRÜNÜR içerik alanı GERÇEKTEN kurar."""
    on, son = GORUNURLUK_KONTROL_PROBLARI[ad]
    taban, prob = _sinir_probu(on, son)
    assert taban - prob, f"{ad}: görünür içerik alanı kurmadı — aşırı maskeleme"


def test_commonmark_sinir_ekseni_bos_kume_kollari() -> None:
    """Taban GERÇEKTEN not veriyor mu; iki envanter de dolu mu?"""
    bosalt, _ekle = _kap_of("bolum-a-alani", "cta_kaliplari")
    assert _bos_kap_notlari(bosalt), "taban BOŞ — eksen boşa yeşil"
    assert COMMONMARK_SINIR_PROBLARI and GORUNURLUK_KONTROL_PROBLARI
    assert not (set(COMMONMARK_SINIR_PROBLARI) & set(GORUNURLUK_KONTROL_PROBLARI))


def test_cit_kapsam_envanteri_mutasyona_duyarli() -> None:
    """MUTASYON + BOŞ KÜME: kuralı sök → kapsanan yolların HEPSİ kırılsın."""
    assert CIT_KAPSANAN_PROBLARI and CIT_DISI_PROBLARI, "envanter BOŞ — kapı boşa yeşil"
    _BOS_KAP_ONBELLEGI.clear()
    try:
        with mock.patch.object(bd, "_cit_maskesi", lambda satirlar: [False] * len(satirlar)):
            kirmizi = {
                (ad, baglam)
                for ad, prob in CIT_KAPSANAN_PROBLARI.items()
                for baglam in CIT_BAGLAMLARI
                if prob(baglam)
            }
    finally:
        _BOS_KAP_ONBELLEGI.clear()
    # HER yol, HER bağlamda kırılır: 7 × 5 hücrenin hepsi kural sökülünce düşer.
    beklenen = {(ad, baglam) for ad in CIT_KAPSANAN_PROBLARI for baglam in CIT_BAGLAMLARI}
    assert kirmizi == beklenen, sorted(beklenen - kirmizi)


def test_acik_bicim_envanteri_gercekten_not_kaldirir() -> None:
    """ENVANTER TRIPWIRE (birinci ayak): her AÇIK biçim gerçekten notu kaldırmalı.

    Bu görevde kapsam beyanı BEŞ kez bayatladı. Kapatma bir cümle düzeltmesi
    DEĞİL: envanter `bd.ACIK_BLOK_BICIMLERI`'nde TEK yerde yaşar, beyan metnini
    oradan ÜRETİR ve burası her kalemin UÇTAN UCA gerçekten bir boşluk notunu
    kaldırdığını ölçer. Bir biçim kapatılırsa bu test KIRILIR ve envanter
    güncellenmek ZORUNDA kalır — altıncı bayat beyan olamaz.
    """
    assert bd.ACIK_BLOK_BICIMLERI, "envanter BOŞ — kapı boşa yeşil"
    beyan = next(
        b
        for b in bd.run(TEMIZ, source_name="P").kapsam_sinirlari
        if b.startswith("bolum-ve-alan-tamligi/doluluk")
    )
    assert "KAPATILMADI" in beyan and "blockquote" in beyan
    bosalt, ekle = _kap_of("donem-yuvasi", bd.OZEL_GUN_YUVALARI[0])
    for ad, govde in bd.ACIK_BLOK_BICIMLERI:
        assert ad in beyan, f"envanter kalemi beyanda YOK: {ad!r}"
        assert _cit_kaybi(bosalt, ekle, govde), f"{ad}: notu KALDIRMIYOR — beyan BAYAT"
    # ...ve KAPANMIŞ kalem envanterde OLMAMALI: dilsiz çit artık not kaldırmaz.
    assert not any("DİLSİZ" in ad.upper() for ad, _ in bd.ACIK_BLOK_BICIMLERI), (
        bd.ACIK_BLOK_BICIMLERI
    )
    for _bad, _dil, _govde_adi, _govde_satirlari, satirlar in CIT_BICIMLERI:
        if _dil == "dilsiz":
            assert not _cit_kaybi(bosalt, ekle, satirlar), _bad
    assert "KAPANDI" in beyan
    # POZİTİF KONTROL: temiz kaynak yeni kapıdan sonra da notsuz GEÇER.
    temiz = bd.run(TEMIZ, source_name="P")
    assert temiz.sonuc == bd.SONUC_GECTI and temiz.notlar == ()
