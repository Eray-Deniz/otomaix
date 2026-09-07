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
import json
import re
from pathlib import Path
from unittest import mock

import pytest

from app.services.sector_pipeline import brief_doctor as bd

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
    """K-127 iki BAĞIMSIZ kaynak ister: aynı kaynağın iki raporu bir sayılır."""
    gate = bd.gate_round([_rapor(_ad=ad) for ad in adlar])
    assert gate.gecerli_kaynak_sayisi == beklenen
    assert gate.dur is dur


def test_ayni_kimlikte_eleme_kimligi_gecersiz_kilar() -> None:
    """Fail-closed: bir kimliğin RAPORLARINDAN biri elendiyse kimlik elenmiştir."""
    gate = bd.gate_round(
        [_rapor(_ad="A"), _sahte_elenmis("A"), _rapor(_ad="B")]
    )
    assert gate.gecerli_kaynak_sayisi == 1
    assert gate.elenen_kaynak_sayisi == 1
    assert gate.dur is True


def _gecerli_gate_argumanlari() -> dict:
    raporlar = (_rapor(_ad="A"), _rapor(_ad="B"), _sahte_elenmis("C"))
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
    beklenen = tuple(c.kapsam_siniri for c in bd.CHECKS if c.kapsam_siniri)
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
    assert "DOĞRULANMADI" in dil.kapsam_siniri.upper()
    assert "ters yön" in dil.aciklama or "ölçülmez" in dil.aciklama


def test_kapsam_sinirlari_donmus_ve_tip_zorlar() -> None:
    rapor = bd.DoctorReport(
        sonuc=bd.SONUC_GECTI,
        notlar=(),
        elemeler=(),
        kaynak_adi="K",
        kapsam_sinirlari=["tek sınır"],
    )
    assert rapor.kapsam_sinirlari == ("tek sınır",)
    with pytest.raises(TypeError):
        bd.DoctorReport(
            sonuc=bd.SONUC_GECTI,
            notlar=(),
            elemeler=(),
            kaynak_adi="K",
            kapsam_sinirlari=(7,),  # type: ignore[arg-type]
        )
