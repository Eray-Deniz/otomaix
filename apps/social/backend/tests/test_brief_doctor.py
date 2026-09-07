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

import dataclasses
import hashlib
import itertools
import json
import re
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
    if eksik_bolum != "C":
        satirlar += ["## Bölüm C — KAYNAKLAR", ""]
        kaynak_satirlari = [
            "- cta_kaliplari → randevu daveti kalibi → https://ornek-ajans.example/rehber",
            "- gorsel_kodlar → vitrin isigi → https://sektor-yayini.example/analiz",
            "- Sevgililer Günü → hediye talebi → https://pazarlama-blogu.example/veri",
        ]
        if bozuk_url:
            kaynak_satirlari[0] = (
                "- cta_kaliplari → randevu daveti kalibi → ornek-ajans.example/rehber"
            )
        satirlar += kaynak_satirlari + [""]

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
    """
    cikti: list[str] = []
    for satir in metin.splitlines(keepends=True):
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
    """Dört sütun UYDURULMAZ: pinlenmiş sözleşme cümlesinden okunur."""
    metin = _pinli_sablon()
    blok = re.search(
        r"gerekçeleri tablosu\s*\n?\((.*?)\), sonra", metin, re.S
    )
    assert blok is not None, "sözleşmede gerekçe tablosu sütun cümlesi bulunamadı"
    return tuple(parca.strip() for parca in blok.group(1).split("+"))


def test_gerekce_tablosu_sutunlari_pinlenmis_sablondan_okunur() -> None:
    assert _sozlesme_tablo_sutunlari() == bd.GEREKCE_TABLOSU_SUTUNLARI
    assert len(bd.GEREKCE_TABLOSU_SUTUNLARI) == 4


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
    ("c-eslemesiz", c_eslemesini_kaldir(TEMIZ), "eşleme satırı"),
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


def c_satirini_cogalt(metin: str) -> str:
    satirlar = metin.splitlines(True)
    k = _madde_indeksi(satirlar, *_md_blok(satirlar, "## Bölüm C — KAYNAKLAR"))
    return "".join(satirlar[: k + 1] + [satirlar[k]] + satirlar[k + 1 :])


def c_ucluyu_boz(metin: str) -> str:
    """Eşleme satırı VAR ama alan/dönem → iddia → kaynak ÜÇLÜSÜ yok."""
    satirlar = metin.splitlines(True)
    k = _madde_indeksi(satirlar, *_md_blok(satirlar, "## Bölüm C — KAYNAKLAR"))
    return "".join(satirlar[:k] + ["- https://ornek-ajans.example/rehber\n"] + satirlar[k + 1 :])


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
    """GERÇEK gerekçe tablosunun tür etiketi sütununu siler (kontrol kolu)."""
    cikti = []
    for satir in metin.splitlines(True):
        if not satir.lstrip().startswith("|") or satir.lstrip().startswith("|-"):
            cikti.append(satir)
            continue
        hucreler = [h.strip() for h in satir.strip().strip("|").split("|")]
        cikti.append("| " + " | ".join(h for i, h in enumerate(hucreler) if i != 2) + " |\n")
    return "".join(cikti)


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
        lambda: c_ucluyu_boz(TEMIZ),
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


def test_bolum_c_ucluyu_ister_ama_temizde_yanlis_pozitif_uretmez() -> None:
    """Bölüm C sözleşmesi ÜÇLÜdür: alan/dönem → iddia → kaynak."""
    assert "iddia" in _notlari(c_ucluyu_boz(TEMIZ))
    assert _notlari(TEMIZ) == "", "temiz Bölüm C üçlü kontrolünden geçmeli"


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

    # (c) Bölüm C üçlüsü: sök → çıplak bağlantı satırı sussun.
    ciplak = c_ucluyu_boz(TEMIZ)
    assert "ÜÇLÜ değil" in _notlari(ciplak)
    with mock.patch.object(bd, "_c_esleme_parcalari", lambda satir: ["a", "b"]):
        assert "ÜÇLÜ değil" not in _notlari(ciplak)

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


def test_kapsam_beyani_besinci_kalemi_tasir() -> None:
    """Beyan sayısı DÖRT değil BEŞ: sıra sınırı ayrı bir kalem olarak eklendi."""
    beyanlar = bd.run(TEMIZ, source_name="P").kapsam_sinirlari
    assert len(beyanlar) == 5, beyanlar
    assert len(set(beyanlar)) == 5, "beyanlar tekrar ediyor"


def test_bolum_c_uclusu_serbest_duzyaziyla_gecer_ve_beyan_bunu_soyler() -> None:
    """Dürüst ilan (Kalem 4): kaçış ÖLÇÜLÜR, beyan onu AYNEN söyler.

    Kök çözüm sözleşme revizyonudur (Bölüm C'nin sabit sütunlu tablo olması) ve
    AYRI bir tasarım işine kaydedilmiştir; bu tur ayıraç vekilini
    SERTLEŞTİRMEZ — sertleştirme üç turdur yakınsamadı ve yanlış-pozitif üretir.
    Test bir TRIPWIRE'dır: kaçış kapanırsa burası kırılır ve beyan güncellenir.
    """
    satirlar = TEMIZ.splitlines(True)
    i, j = _md_blok(satirlar, "## Bölüm C — KAYNAKLAR")
    maddeler = [k for k in range(i + 1, j) if satirlar[k].lstrip().startswith("- ")]
    duzyazi = "".join(
        satirlar[: maddeler[0]]
        + ["- Düz yazı, devamı https://example.com/kaynak\n"]
        + satirlar[maddeler[-1] + 1 :]
    )
    rapor = bd.run(duzyazi, source_name="P")
    assert rapor.sonuc == bd.SONUC_GECTI
    assert [b.mesaj for b in rapor.notlar if b.aile == "url-bicimi"] == []

    beyan = next(
        b for b in rapor.kapsam_sinirlari if b.startswith("url-bicimi:")
    )
    assert "serbest düzyazı" in beyan
    assert "DOĞRULANMADI" in beyan
    assert "ÜÇLÜSÜ" in beyan or "ÜÇLÜ" in beyan
