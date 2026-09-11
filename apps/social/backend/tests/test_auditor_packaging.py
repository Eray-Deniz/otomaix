"""Denetçi girdi paketleyicisi — körlük · biçim kapısı · veri kapısı (Plan 2 Task 9).

Ölçülen sözleşme dört başlıkta toplanır:

* **K-137 körlük — ÖLÇÜLEN vaat.** Pakete yazılan hiçbir bayt, PİNLENMİŞ
  sözleşmelerde ya da YAPILANDIRILMIŞ `ARAC_KIMLIKLERI` kümesinde adı geçen bir
  araç kimliği taşımaz; tarama kümesi elle yazılmaz, bu iki kaynaktan TÜRETİLİR.
  "Hiçbir araç kimliği yok" bundan TÜREMEZ — o semantik olumsuzlamadır ve
  serbest metinden kanıtlanamaz. Kimliğin pakete hiç yazılmadığı YAPISAL ayak
  ayrıca, maskelemeye bağışık opak sentinellerle sınanır.
* **K-79 bayt-özdeşlik.** İki denetçinin kopyası bayt bayt aynıdır; `PacketRef`
  eşitsiz iki özet TAŞIYAMAZ.
* **K-81 biçim kapısı.** Beş bölüm, sözleşmedeki SIRAYLA. Anahtarların kendisi
  pinlenmiş `hakem-denetci-gorevi.md`'den hash doğrulanarak okunur — modülün
  sabitiyle karşılaştırılır, ondan TÜRETİLMEZ.
* **K-100 veri kapısı.** Envanterin kendisi denetlenir: dört alan · kapalı statü
  kümesi · anlık görüntüdeki her birim TAM BİR KEZ.

**Kapsam sınırı (dürüst etiket):** çapraz denetçi mutabakatı (iki raporun aynı
anlık görüntüye karşı yazıldığı) BU dosyada ÖLÇÜLMEZ — arayüz eki R6(c) onu tur
seviyesine (Task 10) taşıdı; tek rapor gören bir doğrulayıcı onu kanıtlayamaz.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import re
import subprocess
import uuid
from pathlib import Path

import pytest

from app.services.sector_pipeline import auditors, identity
from app.services.sector_pipeline import brief_doctor as bd
from app.services.sector_pipeline.contracts import ContractDriftError

MONOREPO_KOK = Path(__file__).resolve().parents[4]
PIN_PATH = MONOREPO_KOK / "shared/contracts/research-contracts.pin.json"
ARASTIRMA_DEPOSU = Path("/root/otomaix-sosyal-medya-arastirmasi")


# ─── Kavramdan yazılmış beklentiler ─────────────────────────────────────────
#
# KAVRAM: "araç kimliği" = bir yapay zekâ asistanının SATICI ya da ÜRÜN/model
# ailesi adı. Küme bu tanımdan yazılır; depoda rastlanan örneklerden TÜRETİLMEZ
# (öyle olsaydı tarama, zaten bulunmuş olanın tekrar kontrolü olurdu).
#
# Bu demet yalnız `auditors.ARAC_KIMLIKLERI`'nin AYNASIdır (modül sabiti sessizce
# değişirse `test_arac_kimlikleri_cover_the_pinned_contract_tool_names` düşer).
# Paket TARAMASININ kümesi bu değildir — o `TURETILEN_KIMLIKLER`'dir ve pin
# manifestinden + modül sabitinden TÜRETİLİR (elle uzatılmaz).
#
# Bilinçli DIŞARIDA (ölçülmüş gerekçeyle): "Google" tek başına bir asistan
# kimliği değil, bir şirket/arama motoru adıdır ve araştırma çıktısında meşru
# olarak geçebilir; "Kimi" Türkçe'de yaygın bir sözcüktür ve maskelenmesi
# metni bozar. İkisi de kapsam sınırı olarak BEYAN edilir, sessizce atlanmaz.

KAVRAMSAL_ARAC_ADLARI = (
    # satıcı / laboratuvar
    "OpenAI",
    "Anthropic",
    "Google DeepMind",
    "DeepMind",
    "xAI",
    "Meta AI",
    "Mistral AI",
    "Perplexity AI",
    "DeepSeek",
    # ürün / model ailesi
    "ChatGPT",
    "GPT",
    "Claude Code",
    "Claude",
    "Gemini",
    "Bard",
    "Codex",
    "Copilot",
    "Grok",
    "Llama",
    "Mistral",
    "Perplexity",
    "Qwen",
)

UNIT_A = "ku-0123456789ab"
UNIT_B = "ku-abcdef012345"
UNIT_C = "ku-fedcba987654"


# ─── Pinlenmiş sözleşmeden okunan beklentiler ───────────────────────────────


def _pinli(ad: str) -> str:
    """Pinlenmiş sözleşme dosyasını sha256 doğrulayarak okur (fail-closed)."""
    pin = json.loads(PIN_PATH.read_text(encoding="utf-8"))
    beklenen = pin["files"][ad]
    ham = (ARASTIRMA_DEPOSU / ad).read_bytes()
    bulunan = hashlib.sha256(ham).hexdigest()
    assert bulunan == beklenen, (
        f"{ad} pinden sapmış (pin {beklenen}, disk {bulunan}) — bu dosyadaki "
        "sözleşme sabitleri artık doğrulanamaz"
    )
    return ham.decode("utf-8")


def test_bolum_anahtarlari_match_pinned_contract_headings() -> None:
    """M1: beş anahtar UYDURULMAZ — pinli sözleşmeden SIRA DÂHİL ölçülür."""
    metin = _pinli("hakem-denetci-gorevi.md")
    olculen = tuple(re.findall(r"^\d\) ([A-ZÇĞİÖŞÜ ]+?) —", metin, re.M))
    assert olculen == auditors.BOLUM_ANAHTARLARI, (
        "sözleşmenin çıktı bölümü başlıkları ile BOLUM_ANAHTARLARI ayrıştı — "
        f"sözleşme {olculen}, modül {auditors.BOLUM_ANAHTARLARI}"
    )


def test_bolum_anahtarlari_has_five_entries() -> None:
    """Beş sayısı sözleşmenin KENDİ hükmüdür, tahmin değildir."""
    metin = _pinli("hakem-denetci-gorevi.md")
    assert "yukarıdaki beş bölüm dışına çıkma" in metin
    assert len(auditors.BOLUM_ANAHTARLARI) == 5


def _pinde_adi_gecen_araclar() -> tuple[str, ...]:
    """Pin manifestinin adlandırdığı sözleşmelerden ÖLÇÜLEN araç kimlikleri.

    `_SABLON.md` üç araştırma aracını, `hakem-denetci-gorevi.md` iki denetçi
    aracını ADIYLA anar. Küme burada elle yazılmaz; sözleşme yeni bir aracı
    adıyla anarsa tarama onu KENDİLİĞİNDEN kapsar.
    """
    sablon = _pinli("_SABLON.md")
    arastirma_blok = re.search(r"Üç araştırma aracına da \((.*?)\)", sablon)
    assert arastirma_blok is not None, "_SABLON.md üç aracı adıyla anmıyor"
    olculen = [ad.strip() for ad in arastirma_blok.group(1).split("/")]

    gorev = _pinli("hakem-denetci-gorevi.md")
    denetci_blok = re.search(r"Bu görev iki denetçiye \((.*?)\)", gorev)
    assert denetci_blok is not None, "sözleşme iki denetçi aracını adıyla anmıyor"
    olculen += [ad.strip() for ad in denetci_blok.group(1).split(" ve ")]

    assert olculen, "ölçüm boş küme döndü — tarama hiçbir şey kanıtlamaz"
    return tuple(olculen)


# Tarama kümesi TÜRETİLİR (elle yazılmaz): pin manifestinde adı geçen
# sözleşmelerden ölçülen adlar + `auditors.ARAC_KIMLIKLERI` yapılandırılmış
# kaynak kümesi. Parametrize edilebilmesi için toplama anında hesaplanır.
TURETILEN_KIMLIKLER = tuple(
    sorted(set(_pinde_adi_gecen_araclar()) | set(auditors.ARAC_KIMLIKLERI))
)


def test_arac_kimlikleri_cover_the_pinned_contract_tool_names() -> None:
    """Kavramsal küme ile modül sabiti aynı; ölçülen adlar İKİSİ tarafından da kapsanır."""
    assert tuple(sorted(auditors.ARAC_KIMLIKLERI)) == tuple(
        sorted(KAVRAMSAL_ARAC_ADLARI)
    )
    for ad in _pinde_adi_gecen_araclar():
        assert auditors.ARAC_MASKESI in auditors.anonymize(
            f"kaynak: {ad} tarafından üretildi"
        ), f"pinli sözleşmede ölçülen araç adı maskelenmiyor: {ad!r}"


# ─── Rapor metni kurucuları ─────────────────────────────────────────────────


def _snapshot(*unit_ids: str) -> dict[str, dict]:
    return {
        uid: {
            "unit_id": uid,
            "alan": "cta_kaliplari",
            "oge_yolu": f"cta_kaliplari[{sira}]",
            "karar": "koru",
            "oge_sha": "0" * 64,
            "deger": f"kalıp {sira}",
        }
        for sira, uid in enumerate(unit_ids)
    }


def _url_bolumu(
    *,
    kaynak_sayisi: int = 2,
    satir_sayisi: int | None = None,
    ortam_kisiti: bool = False,
) -> str:
    beklenen = 0 if kaynak_sayisi < 2 else kaynak_sayisi * 3
    yazilan = beklenen if satir_sayisi is None else satir_sayisi
    satirlar = [
        "| iddia | kaynak | sonuç | not |",
        "| --- | --- | --- | --- |",
    ]
    for sira in range(yazilan):
        satirlar.append(
            f"| https://ornek.example/{sira} | KAYNAK-{sira % 3 + 1} | "
            "DOĞRULANDI | tek cümle not |"
        )
    if yazilan == 0:
        satirlar = []
    gövde = [f"Kaynak sayısı: {kaynak_sayisi} — beklenen satır: {beklenen}"]
    if ortam_kisiti:
        gövde.append("URL doğrulaması yapılamadı (ortam kısıtı)")
    return "\n".join(gövde + satirlar)


def _envanter_bolumu(satirlar: list[str] | None) -> str:
    if satirlar is None:
        satirlar = [
            f"| {UNIT_A} | supported | #1 | Yeni kanıt kalıbı destekliyor. |",
            f"| {UNIT_B} | needs_update | #2 | Tarihli mevzuat değişti. |",
        ]
    baslik = [
        "EK-H birim sayısı: 2 — yazılan satır: 2",
        "| unit_id | statu | kanit | gerekce |",
        "| --- | --- | --- | --- |",
    ]
    return "\n".join(baslik + satirlar)


DENETIM_BASLIGI = (
    "| no | alan | iddia-özeti | kaynak-iddialari | kaynaklar | sınıf "
    "| bayraklar | öneri | gerekçe |\n"
    "|---|---|---|---|---|---|---|---|---|"
)


def _denetim_bolumu(satirlar: list[str] | None = None) -> str:
    """DENETİM TABLOSU gövdesi — başlık sözleşmenin BİREBİR yazımıdır."""
    if satirlar is None:
        satirlar = [
            "| 1 | cta_kaliplari | ilk iddia | K1#1, K2#4 | 1,2 | 2-3 | — | al "
            "| Tek cümle. |",
            "| 2 | kanca_kaliplari | ikinci iddia | K3#2 | 3 | tekil | — "
            "| uyarla | Tek cümle. |",
        ]
    return "\n".join([DENETIM_BASLIGI] + satirlar)


KAYNAK_PROFIL_BASLIGI = "| kaynak | resmi | not |\n|---|---|---|"


def _kaynak_profili_bolumu(satirlar: list[str] | None = None) -> str:
    """KAYNAK PROFİLİ gövdesi — 2026-09-11'de düz yazıdan TABLOYA döndü."""
    if satirlar is None:
        satirlar = [
            "| 1 | evet | Mevzuat metninin kendisi; yerel ve tutarlı. |",
            "| 2 | hayır | Haberleştiren kaynak; yerel değil. |",
            "| 3 | hayır | Derleme; özgüllük zayıf. |",
        ]
    return "\n".join([KAYNAK_PROFIL_BASLIGI] + satirlar)


def _rapor_metni(
    *,
    denetim: str | None = None,
    envanter: str | None = None,
    url: str | None = None,
    profil: str | None = None,
    atlanan_bolum: int | None = None,
    takas: tuple[int, int] | None = None,
) -> str:
    """Rapor metni kurucusu.

    `takas` İKİ TAM bölüm bloğunu yer değiştirir: başlıklar, numaralandırma,
    gövdeler ve envanter geçerliliği KORUNUR — sapan tek şey bölüm SIRASIDIR.
    """
    govdeler = {
        1: _denetim_bolumu(None) if denetim is None else denetim,
        2: _url_bolumu() if url is None else url,
        3: _kaynak_profili_bolumu() if profil is None else profil,
        4: "- Mevzuat tarihi operatöre sorulmalı mı?",
        5: _envanter_bolumu(None) if envanter is None else envanter,
    }
    parcalar = []
    for sira, baslik in enumerate(auditors.BOLUM_ANAHTARLARI, start=1):
        if sira == atlanan_bolum:
            continue
        parcalar.append(f"{sira}) {baslik}\n{govdeler[sira]}")
    if takas is not None:
        i, j = (n - 1 for n in takas)
        parcalar[i], parcalar[j] = parcalar[j], parcalar[i]
    return "\n\n".join(parcalar) + "\n"


def _dogrula(metin: str, snapshot: dict[str, dict] | None = None):
    return auditors.validate_report(
        metin,
        unit_snapshot=_snapshot(UNIT_A, UNIT_B) if snapshot is None else snapshot,
        denetci=auditors.DENETCI_ROLLERI[0],
    )


# ─── Kapalı değer kümeleri ──────────────────────────────────────────────────


def test_status_and_role_sets_are_closed() -> None:
    """Statü uzayı BEŞ, rol uzayı İKİ — ikisi de pinli sözleşmeden ölçülür."""
    gorev = _pinli("hakem-denetci-gorevi.md")
    blok = re.search(
        r"STATÜ UZAYI KAPALIDIR — beş değer, aynen bu yazımla:(.*?)\n\nBu adımda",
        gorev,
        re.S,
    )
    assert blok is not None, "sözleşmede kapalı statü bloğu bulunamadı"
    assert tuple(re.findall(r"^- `([a-z_]+)`:", blok.group(1), re.M)) == (
        auditors.STATU_DEGERLERI
    )
    assert auditors.DENETCI_ROLLERI == ("denetci-1", "denetci-2")


# ─── K-137 körlük ───────────────────────────────────────────────────────────


def test_anonymize_strips_tool_names() -> None:
    ham = (
        "Bu çıktı ChatGPT ile üretildi, Gemini'nin sürümü kontrol edildi; "
        "Claude Code ve Codex denetledi. GPT-5 notu OpenAI tarafından yazıldı."
    )
    temiz = auditors.anonymize(ham)
    for ad in ("ChatGPT", "Gemini", "Claude", "Codex", "GPT", "OpenAI"):
        assert not re.search(rf"(?<!\w){re.escape(ad)}", temiz, re.IGNORECASE), (
            f"anonimleştirme {ad!r} kimliğini bırakmış: {temiz!r}"
        )
    assert auditors.ARAC_MASKESI in temiz
    # Maskeleme metni yutmaz: araç dışı içerik korunur.
    assert "sürümü kontrol edildi" in temiz


ARAC_ADLI_KIMLIKLER = ("gemini-2026-08", "chatgpt-2026-08", "claude-2026-08")
# Maskeye BAĞIŞIK kimlikler: hiçbiri kavramsal araç adı taşımaz, dolayısıyla
# `anonymize` onları görmez. K-137'nin YAPISAL ayağını (kimlik pakete hiç
# YAZILMAZ) maskeleme ayağından ayırt eden tek girdi budur — araç adlı
# kimlikler maskeyle de temizlenir ve iki ayak birbirini gizler.
MASKE_BAGISIK_KIMLIKLER = (
    "arastirma-kaynagi-alfa",
    "arastirma-kaynagi-beta",
    "arastirma-kaynagi-gama",
)


KAYNAK_METINLERI = (
    "KAYNAK metni: ChatGPT bu bölümü üretti.",
    "Gemini çıktısı — takvim temaları.",
    "Claude Code notu: cta kalıpları.",
)


def _rapor(kaynak_adi: str, kaynak_metni: str, **sapma) -> bd.DoctorReport:
    """`brief_doctor.run`'ın ürettiği raporun aynısı — özet DAHİL.

    `icerik_ozeti` burada da `identity.canonical_sha` ile üretilir; ikinci bir
    hash kuralı yazılmaz. `sapma` ile alan bilerek bozulabilir (negatif vaka).
    """
    alanlar = {
        "sonuc": bd.SONUC_GECTI,
        "notlar": (),
        "elemeler": (),
        "kaynak_adi": kaynak_adi,
        "icerik_ozeti": identity.canonical_sha(kaynak_metni),
    }
    alanlar.update(sapma)
    return bd.DoctorReport(**alanlar)


def _paket(
    tmp_path: Path,
    *,
    kaynak_sayisi: int = 3,
    kimlikler: tuple[str, ...] = ARAC_ADLI_KIMLIKLER,
    raporlar: list[bd.DoctorReport] | None = None,
):
    kaynaklar = list(KAYNAK_METINLERI[:kaynak_sayisi])
    if raporlar is None:
        raporlar = [
            _rapor(ad, metin)
            for ad, metin in zip(kimlikler[:kaynak_sayisi], kaynaklar)
        ]
    return auditors.build_packet(
        brief="Marka için sektör araştırması — ChatGPT'ye verilen metinle aynı.",
        sources=kaynaklar,
        doctor_reports=raporlar,
        active_package={"schema_version": 1, "content": {"kapsam": "metin"}},
        unit_snapshot=_snapshot(UNIT_A, UNIT_B),
        run_id="kosu-2026-09-08-t9",
        sector_id=uuid.UUID("11111111-2222-3333-4444-555555555555"),
        dest=tmp_path,
    )


@pytest.fixture(scope="module")
def taranan_paket(tmp_path_factory: pytest.TempPathFactory):
    """Kimlik taramasının tek paketi — parametrize edilen her ad aynı paketi görür."""
    return _paket(tmp_path_factory.mktemp("kimlik-taramasi"))


@pytest.mark.parametrize("kimlik", TURETILEN_KIMLIKLER)
def test_packet_excludes_every_identity_named_by_pin_or_config(
    taranan_paket, kimlik: str
) -> None:
    """Ölçülen vaat: PİNLENMİŞ sözleşmelerde ve YAPILANDIRILMIŞ kaynak kümesinde
    adı geçen kimlikler paket içeriğine de dosya adlarına da GİRMEZ.

    "Hiçbir araç kimliği geçmez" DEĞİL — o bir semantik olumsuzlamadır ve
    serbest metinden kanıtlanamaz: elle yazılan liste ne kadar uzasa bir
    sonraki satıcı adı (Amazon Q · Cursor · Manus …) hep dışarıda kalır. Bu
    yüzden küme uzatılmaz, TÜRETİLİR — sözleşme yeni bir aracı adıyla anarsa
    tarama onu kendiliğinden kapsar; kapsam sınırı da `ARAC_KIMLIKLERI`'nin
    beyan ettiği kadardır.

    Yapısal ayak (kaynak `kaynak_adi`'sı pakete HİÇ yazılmaz) bu testte DEĞİL,
    maskelemeye bağışık opak sentinellerle
    `test_packet_never_writes_the_source_identity`'de ölçülür.
    """
    dosyalar = sorted(p for p in taranan_paket.kok.rglob("*") if p.is_file())
    assert dosyalar, "paket boş — tarama hiçbir şey kanıtlamaz"
    desen = re.compile(rf"(?<!\w){re.escape(kimlik)}(?!\w)", re.I)
    for dosya in dosyalar:
        goreli = dosya.relative_to(taranan_paket.kok)
        assert not desen.search(dosya.read_text(encoding="utf-8")), (
            f"{goreli} araç kimliği taşıyor: {kimlik!r}"
        )
        assert not desen.search(dosya.name), (
            f"{goreli} dosya ADI araç kimliği taşıyor: {kimlik!r}"
        )


def test_packet_file_names_are_blind_positional_labels(tmp_path: Path) -> None:
    """Pozitif kontrol: kör etiketler GERÇEKTEN yazılmış (boş kümeyi temiz okuma)."""
    ref = _paket(tmp_path)
    ekler = {p.name for p in ref.kok.rglob("*") if p.is_file()}
    assert {"EK-B-KAYNAK-1.md", "EK-C-KAYNAK-2.md", "EK-D-KAYNAK-3.md"} <= ekler


def test_packet_never_writes_the_source_identity(tmp_path: Path) -> None:
    """K-137'nin YAPISAL ayağı: `kaynak_adi` pakete HİÇ yazılmaz.

    Maskeye bağışık kimlikler kullanılır; araç adlı bir kimlik `anonymize`
    tarafından da temizlenirdi ve yapısal körlüğün kendisi ölçülmemiş kalırdı.
    """
    ref = _paket(tmp_path, kimlikler=MASKE_BAGISIK_KIMLIKLER)
    dosyalar = sorted(p for p in ref.kok.rglob("*") if p.is_file())
    assert dosyalar
    for dosya in dosyalar:
        metin = dosya.read_text(encoding="utf-8")
        for kimlik in MASKE_BAGISIK_KIMLIKLER:
            assert kimlik not in metin, (
                f"{dosya.relative_to(ref.kok)} kaynak kimliğini sızdırıyor: "
                f"{kimlik!r} — kör etiket KONUMDAN türer, kimlikten değil"
            )
    # Pozitif kontrol: kör etiket gerçekten YAZILMIŞ (tarama boş kümeyi
    # "temiz" diye okumasın).
    ek_e = (ref.kopyalar["denetci-1"] / "EK-E-brief-doctor.md").read_text("utf-8")
    assert "KAYNAK-1" in ek_e and "KAYNAK-3" in ek_e


def test_packet_bytes_identical_for_both_auditors(tmp_path: Path) -> None:
    """K-79: iki kopya bayt bayt aynı; özetleri EŞİT."""
    ref = _paket(tmp_path)
    birinci, ikinci = (ref.kopyalar[rol] for rol in auditors.DENETCI_ROLLERI)
    adlar_1 = sorted(p.name for p in birinci.iterdir())
    adlar_2 = sorted(p.name for p in ikinci.iterdir())
    assert adlar_1 == adlar_2 and adlar_1
    for ad in adlar_1:
        assert (birinci / ad).read_bytes() == (ikinci / ad).read_bytes()
    assert len(set(ref.kopya_shalari.values())) == 1


def test_packet_ref_carries_unit_snapshot_and_equal_copy_hashes(
    tmp_path: Path,
) -> None:
    """R5: anlık görüntü pakete TAŞINIR ve `unit_snapshot_sha` onun kimliğidir."""
    ref = _paket(tmp_path)
    assert set(ref.unit_snapshot) == {UNIT_A, UNIT_B}
    assert ref.unit_snapshot_sha == identity.canonical_sha(
        _snapshot(UNIT_A, UNIT_B)
    )
    assert set(ref.kopyalar) == set(auditors.DENETCI_ROLLERI)
    assert set(ref.kopya_shalari) == set(auditors.DENETCI_ROLLERI)

    with pytest.raises(ValueError, match="bayt-özdeş"):
        auditors.PacketRef(
            run_id=ref.run_id,
            yetkili_kaynak_sayisi=ref.yetkili_kaynak_sayisi,
            kaynak_seti_sha=ref.kaynak_seti_sha,
            sector_id=ref.sector_id,
            kok=ref.kok,
            kopyalar=dict(ref.kopyalar),
            kopya_shalari={"denetci-1": "a" * 64, "denetci-2": "b" * 64},
            unit_snapshot=dict(ref.unit_snapshot),
            unit_snapshot_sha=ref.unit_snapshot_sha,
        )


def test_packet_ref_mappings_are_read_only_and_unaliased(tmp_path: Path) -> None:
    """R6(e): üç eşleme de salt-okunur ve çağıranın nesnesiyle takma ad paylaşmaz."""
    ref = _paket(tmp_path)
    for alan in ("kopyalar", "kopya_shalari", "unit_snapshot"):
        with pytest.raises(TypeError):
            getattr(ref, alan)["yeni"] = "x"

    cagiran = _snapshot(UNIT_A, UNIT_B)
    ikinci = auditors.PacketRef(
        run_id=ref.run_id,
        yetkili_kaynak_sayisi=ref.yetkili_kaynak_sayisi,
            kaynak_seti_sha=ref.kaynak_seti_sha,
        sector_id=ref.sector_id,
        kok=ref.kok,
        kopyalar=dict(ref.kopyalar),
        kopya_shalari=dict(ref.kopya_shalari),
        unit_snapshot=cagiran,
        unit_snapshot_sha=identity.canonical_sha(cagiran),
    )
    cagiran[UNIT_C] = {"unit_id": UNIT_C}
    assert set(ikinci.unit_snapshot) == {UNIT_A, UNIT_B}


@pytest.mark.parametrize(
    "alan", ["kopyalar", "kopya_shalari", "unit_snapshot"]
)
def test_packet_ref_does_not_alias_the_caller_mapping(
    tmp_path: Path, alan: str
) -> None:
    """ÜÇ eşlemenin HER BİRİ çağıranın sözlüğüyle takma ad paylaşmaz.

    Alan başına AYRI mutasyon: tek alanı sınamak diğerlerini kapsamaz.
    `kopya_shalari` için tehlike en somut hâlde — çağıran, bayt-özdeşlik kapısı
    GEÇTİKTEN sonra bir özeti değiştirebilseydi `PacketRef` doğrulanmamış bir
    eşitlik iddiası taşırdı.
    """
    ref = _paket(tmp_path)
    cagiran = {
        "kopyalar": dict(ref.kopyalar),
        "kopya_shalari": dict(ref.kopya_shalari),
        "unit_snapshot": _snapshot(UNIT_A, UNIT_B),
    }
    ikinci = auditors.PacketRef(
        run_id=ref.run_id,
        yetkili_kaynak_sayisi=ref.yetkili_kaynak_sayisi,
            kaynak_seti_sha=ref.kaynak_seti_sha,
        sector_id=ref.sector_id,
        kok=ref.kok,
        kopyalar=cagiran["kopyalar"],
        kopya_shalari=cagiran["kopya_shalari"],
        unit_snapshot=cagiran["unit_snapshot"],
        unit_snapshot_sha=identity.canonical_sha(cagiran["unit_snapshot"]),
    )
    once = dict(getattr(ikinci, alan))

    hedef = cagiran[alan]
    anahtar = sorted(hedef)[0]
    hedef[anahtar] = "SONRADAN DEĞİŞTİ"
    hedef["SONRADAN EKLENDİ"] = "x"
    del hedef[sorted(hedef)[-1]]

    assert dict(getattr(ikinci, alan)) == once, (
        f"PacketRef.{alan} çağıranın sözlüğüyle takma ad paylaşıyor — kapıdan "
        "geçmiş değer yapımdan SONRA değiştirilebiliyor"
    )
    # `kopya_shalari` için invariant da ayakta kalır: özetler HÂLÂ eşit.
    assert len(set(ikinci.kopya_shalari.values())) == 1


def test_build_packet_stops_when_the_contract_pin_drifts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """M1 sıra kapısı: pin v2 doğrulanmadan paket KURULMAZ (fail-closed)."""
    sahte_depo = tmp_path / "sahte-depo"
    sahte_depo.mkdir()
    monkeypatch.setattr(auditors, "ARASTIRMA_DEPOSU_KOKU", sahte_depo)
    with pytest.raises(ContractDriftError):
        _paket(tmp_path / "paket")


# ─── F1: konumsal eşleme ÖLÇÜLÜR (kaynak ↔ brief-doctor raporu) ────────────


def test_build_packet_rejects_a_shifted_source_report_pairing(tmp_path: Path) -> None:
    """Sıra kayarsa paket KURULMAZ — eşleme "ölçülemez" değil, ölçülür.

    Kayma dışındaki HER kapı geçerli kalır: sayılar eşit (3 = 3) ve üç kimlik
    tekil. Ölçülen tek sapma, hangi raporun hangi METNİ anlattığıdır; kanıt
    `DoctorReport.icerik_ozeti`'dir (`brief_doctor.run` onu
    `identity.canonical_sha(source_text)`'ten üretir).
    """
    raporlar = [
        _rapor(ad, metin)
        for ad, metin in zip(ARAC_ADLI_KIMLIKLER, KAYNAK_METINLERI)
    ]
    ters = [raporlar[1], raporlar[0], raporlar[2]]
    # Kayan sıra dışındaki kapılar HÂLÂ geçerli — tek ölçülen sapma eşlemedir.
    assert len(ters) == len(KAYNAK_METINLERI)
    assert len({rapor.kanonik_kimlik for rapor in ters}) == 3

    with pytest.raises(ValueError, match="EŞLEŞMİYOR"):
        _paket(tmp_path / "kayan", raporlar=ters)


def test_build_packet_rejects_a_doctor_report_without_a_content_digest(
    tmp_path: Path,
) -> None:
    """Özetsiz rapor eşleme KANITI taşımaz — kör etiketin arkasına saklanamaz."""
    raporlar = [
        _rapor(ad, metin)
        for ad, metin in zip(ARAC_ADLI_KIMLIKLER, KAYNAK_METINLERI)
    ]
    raporlar[1] = _rapor(
        ARAC_ADLI_KIMLIKLER[1], KAYNAK_METINLERI[1], icerik_ozeti=""
    )
    with pytest.raises(ValueError, match="içerik özeti TAŞIMIYOR"):
        _paket(tmp_path / "ozetsiz", raporlar=raporlar)


def test_build_packet_accepts_a_correctly_paired_packet(tmp_path: Path) -> None:
    """Pozitif kontrol: kapı hep-RED değil — doğru eşleşen paket KURULUR."""
    ref = _paket(tmp_path)
    assert ref.kok.is_dir()
    assert set(ref.kopyalar) == set(auditors.DENETCI_ROLLERI)


# ─── F2: pin kapısının doğruladığı baytlar paketlenir (TOCTOU) ──────────────


PINLENEN_SOZLESMELER = (
    "_SABLON.md",
    "hakem-denetci-gorevi.md",
    "hakem-sentez-gorevi.md",
)


def _git(repo: Path, *args: str) -> str:
    """Sahte depoda git çalıştırır. Kurulum aracıdır — üretim kodu değil."""
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _sahte_pinli_depo(tmp_path: Path) -> tuple[Path, Path]:
    """Pin kapısını GERÇEKTEN geçen sahte dış depo + eşleşen manifest.

    Gerçek depo kullanılamaz: TOCTOU penceresini ölçmek için sözleşme dosyasını
    doğrulama SONRASINDA değiştirmek gerekir ve pinli artefaktlara YAZILMAZ.
    """
    repo = tmp_path / "arastirma-deposu"
    repo.mkdir(parents=True)
    _git(repo, "init", "-q", "-b", "master")
    _git(repo, "config", "user.email", "test@otomaix")
    _git(repo, "config", "user.name", "Test")
    for ad in PINLENEN_SOZLESMELER:
        (repo / ad).write_text(
            f"# {ad}\n\nPİNLENMİŞ SÖZLEŞME GÖVDESİ\n", encoding="utf-8"
        )
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "sözleşme v2")

    pin_path = tmp_path / "research-contracts.pin.json"
    pin_path.write_text(
        json.dumps(
            {
                "commit": _git(repo, "rev-parse", "HEAD"),
                "files": {
                    ad: hashlib.sha256((repo / ad).read_bytes()).hexdigest()
                    for ad in PINLENEN_SOZLESMELER
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return repo, pin_path


def test_packet_carries_the_bytes_the_pin_gate_verified(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Sözleşme BİR KEZ okunur: doğrulanan bayt ile paketlenen bayt AYNIDIR.

    Kurgu TOCTOU penceresini bilerek açar: pin kapısı döndükten HEMEN sonra
    sözleşme dosyası diskte değişir. İkinci bir okuma yapan bir uygulama
    pinlenmemiş talimatı pakete yazardı — ve iki kopya da AYNI yanlış baytı
    taşıdığı için K-79 bayt-eşitliği bunu göstermezdi.
    """
    repo, pin_path = _sahte_pinli_depo(tmp_path / "dis")
    monkeypatch.setattr(auditors, "ARASTIRMA_DEPOSU_KOKU", repo)
    monkeypatch.setattr(auditors, "PIN_PATH", pin_path)

    gorev = repo / auditors.GOREV_DOSYASI
    dogrulanan = gorev.read_text(encoding="utf-8")
    sizan = "# SIZAN TALİMAT\n\npinlenmemiş bayt\n"

    gercek = auditors.contracts.require_pinned_text

    def _yaris(*args, **kwargs):
        metin = gercek(*args, **kwargs)
        # Doğrulama BİTTİ; pencere burada açık.
        gorev.write_text(sizan, encoding="utf-8")
        return metin

    monkeypatch.setattr(auditors.contracts, "require_pinned_text", _yaris)

    ref = _paket(tmp_path / "paket")
    for rol in auditors.DENETCI_ROLLERI:
        paketlenen = (ref.kopyalar[rol] / "00-GOREV.md").read_text("utf-8")
        assert "SIZAN" not in paketlenen, (
            f"{rol} kopyası doğrulama SONRASI yazılan baytı taşıyor — sözleşme "
            "ikinci kez okunmuş"
        )
        assert paketlenen == auditors.anonymize(dogrulanan)
    # Yarış gerçekten koştu: disk hâlâ sızan içeriği taşıyor (kurgu boş değil).
    assert gorev.read_text(encoding="utf-8") == sizan


def test_pin_gate_stops_when_the_contract_file_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Tek okumaya geçiş kapıyı ZAYIFLATMAZ: eksik sözleşme yine fail-closed."""
    repo, pin_path = _sahte_pinli_depo(tmp_path / "dis")
    monkeypatch.setattr(auditors, "ARASTIRMA_DEPOSU_KOKU", repo)
    monkeypatch.setattr(auditors, "PIN_PATH", pin_path)
    (repo / auditors.GOREV_DOSYASI).unlink()
    with pytest.raises(ContractDriftError, match="sözleşme dosyası yok"):
        _paket(tmp_path / "paket")


def test_pin_gate_stops_when_the_contract_bytes_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Doğrulamadan ÖNCE değişen bayt: paket hiç kurulmaz (hash kapısı)."""
    repo, pin_path = _sahte_pinli_depo(tmp_path / "dis")
    monkeypatch.setattr(auditors, "ARASTIRMA_DEPOSU_KOKU", repo)
    monkeypatch.setattr(auditors, "PIN_PATH", pin_path)
    (repo / auditors.GOREV_DOSYASI).write_text("başka gövde\n", encoding="utf-8")
    with pytest.raises(ContractDriftError, match="hash uyuşmuyor"):
        _paket(tmp_path / "paket")
    assert not (tmp_path / "paket").exists()


def test_build_packet_refuses_to_overwrite_an_existing_packet(
    tmp_path: Path,
) -> None:
    """K-82: paket klasörü EZİLMEZ — ikinci yazım reddedilir."""
    ref = _paket(tmp_path)
    onceki = {
        p.relative_to(ref.kok): p.read_bytes()
        for p in ref.kok.rglob("*")
        if p.is_file()
    }
    with pytest.raises(FileExistsError, match="EZİLMEZ"):
        _paket(tmp_path, kimlikler=MASKE_BAGISIK_KIMLIKLER)
    sonraki = {
        p.relative_to(ref.kok): p.read_bytes()
        for p in ref.kok.rglob("*")
        if p.is_file()
    }
    assert sonraki == onceki


# ─── K-81 biçim kapısı ──────────────────────────────────────────────────────


def test_validate_report_requires_five_sections() -> None:
    sonuc = _dogrula(_rapor_metni(atlanan_bolum=5))
    assert not sonuc.gecerli
    assert sonuc.rapor is None
    assert any("YENİDEN DOĞRULAMA ENVANTERİ" in hata for hata in sonuc.errors)


def test_validate_report_rejects_swapped_section_order() -> None:
    """Bölüm SIRASI kapıdır — küme doğru olsa bile sıra sapması RED.

    Takas iki TAM bloğu yer değiştirir: başlıklar, numaralandırma, gövdeler ve
    envanterin kendi geçerliliği BOZULMAZ. Set karşılaştırmasına dönen bir
    uygulama bu raporu geçerli sayardı; sıralı karşılaştırma saymaz.
    """
    sonuc = _dogrula(_rapor_metni(takas=(3, 4)))
    assert not sonuc.gecerli and sonuc.rapor is None
    assert any("SIRASI" in hata for hata in sonuc.errors), sonuc.errors
    # Sapan şey SIRA: hiçbir bölüm eksik ya da yabancı değil.
    assert not any(
        "bölümü YOK" in hata or "sözleşmede olmayan" in hata
        for hata in sonuc.errors
    ), sonuc.errors
    # Pozitif kontrol: aynı gövdeler DOĞRU sırayla geçerli rapor üretir.
    assert _dogrula(_rapor_metni()).gecerli


def test_validate_report_accepts_valid_report() -> None:
    sonuc = _dogrula(_rapor_metni())
    assert sonuc.errors == ()
    assert sonuc.gecerli
    # Anahtar KÜMESİ kapıdır; `identity.donmus` kanonik sıralama uygular,
    # bölümlerin metindeki SIRASI ise biçim kapısında ayrıca ölçülür.
    assert set(sonuc.rapor.bolumler) == set(auditors.BOLUM_ANAHTARLARI)
    assert sonuc.rapor.bolumler[auditors.BOLUM_ANAHTARLARI[3]].startswith("-")
    assert sonuc.rapor.denetci == auditors.DENETCI_ROLLERI[0]
    assert sonuc.rapor.ham_metin == _rapor_metni()


def test_validate_report_rejects_an_unknown_auditor_role() -> None:
    sonuc = auditors.validate_report(
        _rapor_metni(),
        unit_snapshot=_snapshot(UNIT_A, UNIT_B),
        denetci="codex",
    )
    assert not sonuc.gecerli
    assert any("denetci" in hata for hata in sonuc.errors)


def test_validate_report_url_sample_count_is_conditional() -> None:
    """Satır sayısı SABİT DEĞİL: kalan kaynak × 3 (tek kaynak → hiç doldurulmaz)."""
    beklenen = {
        (3, 9): True,
        (3, 6): False,
        (2, 6): True,
        (2, 9): False,
        (1, 0): True,
        (1, 3): False,
    }
    olculen = {
        (kaynak, satir): _dogrula(
            _rapor_metni(
                url=_url_bolumu(kaynak_sayisi=kaynak, satir_sayisi=satir)
            )
        ).gecerli
        for kaynak, satir in beklenen
    }
    assert olculen == beklenen

    # Ortam kısıtı beyanı satır beklentisini KALDIRIR ama beyanı kaldırmaz.
    kisitli = _dogrula(
        _rapor_metni(
            url=_url_bolumu(kaynak_sayisi=3, satir_sayisi=0, ortam_kisiti=True)
        )
    )
    assert kisitli.gecerli


def test_url_sample_rows_are_parsed_into_checks() -> None:
    sonuc = _dogrula(_rapor_metni(url=_url_bolumu(kaynak_sayisi=2)))
    assert len(sonuc.rapor.url_orneklem) == 6
    ilk = sonuc.rapor.url_orneklem[0]
    assert isinstance(ilk, auditors.UrlCheck)
    assert ilk.erisildi and ilk.icerik_uyumlu


# ─── K-100 veri kapısı ──────────────────────────────────────────────────────


def test_inventory_requires_four_fields() -> None:
    sonuc = _dogrula(
        _rapor_metni(
            envanter=_envanter_bolumu(
                [
                    f"| {UNIT_A} | supported | #1 |",
                    f"| {UNIT_B} | needs_update | #2 | Tarihli mevzuat değişti. |",
                ]
            )
        )
    )
    assert not sonuc.gecerli
    assert any("dört alan" in hata for hata in sonuc.errors)


def test_inventory_rejects_missing_unit() -> None:
    sonuc = _dogrula(
        _rapor_metni(
            envanter=_envanter_bolumu(
                [f"| {UNIT_A} | supported | #1 | Tek cümle. |"]
            )
        )
    )
    assert not sonuc.gecerli
    assert any(UNIT_B in hata and "raporlanmamış" in hata for hata in sonuc.errors)


def test_inventory_rejects_duplicate_unit() -> None:
    sonuc = _dogrula(
        _rapor_metni(
            envanter=_envanter_bolumu(
                [
                    f"| {UNIT_A} | supported | #1 | Tek cümle. |",
                    f"| {UNIT_A} | supported | #1 | Tek cümle. |",
                    f"| {UNIT_B} | supported | #2 | Tek cümle. |",
                ]
            )
        )
    )
    assert not sonuc.gecerli
    assert any("tekrar" in hata for hata in sonuc.errors)


def test_inventory_rejects_unknown_unit() -> None:
    sonuc = _dogrula(
        _rapor_metni(
            envanter=_envanter_bolumu(
                [
                    f"| {UNIT_A} | supported | #1 | Tek cümle. |",
                    f"| {UNIT_B} | supported | #2 | Tek cümle. |",
                    f"| {UNIT_C} | supported | #3 | Tek cümle. |",
                ]
            )
        )
    )
    assert not sonuc.gecerli
    assert any(UNIT_C in hata and "tanınmayan" in hata for hata in sonuc.errors)


def test_inventory_rejects_invalid_status() -> None:
    sonuc = _dogrula(
        _rapor_metni(
            envanter=_envanter_bolumu(
                [
                    f"| {UNIT_A} | dogrulandi | #1 | Tek cümle. |",
                    f"| {UNIT_B} | supported | #2 | Tek cümle. |",
                ]
            )
        )
    )
    assert not sonuc.gecerli
    assert any("statu" in hata for hata in sonuc.errors)


def test_complete_inventory_accepted() -> None:
    """Pozitif kontrol: eksiksiz, tekrarsız, kapalı statülü envanter GEÇER."""
    snapshot = _snapshot(UNIT_A, UNIT_B, UNIT_C)
    sonuc = auditors.validate_report(
        _rapor_metni(
            envanter=_envanter_bolumu(
                [
                    f"| {UNIT_A} | supported | #1 | Tek cümle. |",
                    f"| {UNIT_B} | not_observed | — | Tek cümle. |",
                    f"| {UNIT_C} | risk_unverified | #3 | Tek cümle. |",
                ]
            )
        ),
        unit_snapshot=snapshot,
        denetci=auditors.DENETCI_ROLLERI[1],
    )
    assert sonuc.errors == ()
    assert {satir.unit_id for satir in sonuc.rapor.yeniden_dogrulama} == set(snapshot)


def test_empty_snapshot_expects_an_empty_inventory() -> None:
    """İlk koşu: EK-H boşsa envanter BOŞ üretilir; satır uydurulursa RED."""
    bos = auditors.validate_report(
        _rapor_metni(envanter=_envanter_bolumu([])),
        unit_snapshot={},
        denetci=auditors.DENETCI_ROLLERI[0],
    )
    assert bos.gecerli and bos.rapor.yeniden_dogrulama == ()

    uydurma = auditors.validate_report(
        _rapor_metni(),
        unit_snapshot={},
        denetci=auditors.DENETCI_ROLLERI[0],
    )
    assert not uydurma.gecerli


def test_validate_report_returns_parsed_inventory_on_success() -> None:
    """R6(a): doğrulayıcı hata listesi DEĞİL, AYRIŞTIRILMIŞ nesne döner."""
    sonuc = _dogrula(_rapor_metni())
    satirlar = sonuc.rapor.yeniden_dogrulama
    assert isinstance(satirlar, tuple) and len(satirlar) == 2
    ilk = satirlar[0]
    assert (ilk.unit_id, ilk.statu, ilk.kanit) == (UNIT_A, "supported", "#1")
    assert ilk.gerekce == "Yeni kanıt kalıbı destekliyor."
    assert sonuc.rapor.unit_snapshot_sha == identity.canonical_sha(
        _snapshot(UNIT_A, UNIT_B)
    )


def test_audit_report_inventory_rows_have_four_fields() -> None:
    alanlar = tuple(
        alan.name for alan in dataclasses.fields(auditors.InventoryRow)
    )
    assert alanlar == ("unit_id", "statu", "kanit", "gerekce")


def test_invalid_report_yields_none_object_with_errors() -> None:
    sonuc = _dogrula(_rapor_metni(atlanan_bolum=3))
    assert sonuc.rapor is None
    assert sonuc.errors and isinstance(sonuc.errors, tuple)
    assert not sonuc.gecerli


# ─── R6 / R6(e): tutarsız kurulum ve kurucu-SONRASI mutasyon ────────────────


def _gecerli_rapor() -> auditors.AuditReport:
    sonuc = _dogrula(_rapor_metni())
    assert sonuc.rapor is not None
    return sonuc.rapor


def test_validated_report_rejects_none_report_with_empty_errors() -> None:
    with pytest.raises(ValueError, match="tutarsız"):
        auditors.ValidatedReport(None, [])


def test_validated_report_rejects_report_carrying_errors() -> None:
    with pytest.raises(ValueError, match="tutarsız"):
        auditors.ValidatedReport(_gecerli_rapor(), ["x"])


def test_valid_report_object_reports_gecerli_true() -> None:
    assert auditors.ValidatedReport(_gecerli_rapor(), ()).gecerli


def test_validated_report_errors_are_a_tuple_and_cannot_be_cleared() -> None:
    nesne = auditors.ValidatedReport(None, ["x"])
    assert isinstance(nesne.errors, tuple)
    with pytest.raises(AttributeError):
        nesne.errors.clear()


def test_validated_report_does_not_alias_caller_error_list() -> None:
    cagiran = ["x"]
    nesne = auditors.ValidatedReport(None, cagiran)
    cagiran.clear()
    assert nesne.errors == ("x",) and not nesne.gecerli


def test_validated_report_gecerli_is_false_without_a_report() -> None:
    """`gecerli` İKİ koşula bakar — hatalar boşaltılsa bile raporsuz nesne geçersiz."""
    nesne = auditors.ValidatedReport(None, ("x",))
    object.__setattr__(nesne, "errors", ())
    assert nesne.gecerli is False


def test_audit_report_sections_are_read_only() -> None:
    rapor = _gecerli_rapor()
    with pytest.raises(TypeError):
        rapor.bolumler["yeni"] = "x"


def _dizi_alanlari() -> set[str]:
    """`AuditReport`'un dizi alanları — dataclass'tan ÜRETİLİR, elle yazılmaz."""
    return {
        alan.name
        for alan in dataclasses.fields(auditors.AuditReport)
        if str(alan.type).startswith("tuple[")
    }


def test_audit_report_sequences_are_tuples_and_unaliased() -> None:
    """HER dizi alanı kopyalanır — küme dataclass'tan üretilir, seçilmez.

    Elle sayılan iki alan yazılsaydı üçüncü alan eklendiğinde bu test sessizce
    onu atlardı; ölçüm o gün "geçti" derdi ve takma ad açık kalırdı.
    """
    rapor = _gecerli_rapor()
    alanlar = {
        alan: getattr(rapor, alan) for alan in rapor.__dataclass_fields__
    }
    diziler = _dizi_alanlari()
    assert diziler, "dizi alanı ölçülemedi — tarama hiçbir şey kanıtlamaz"
    canli = {ad: list(getattr(rapor, ad)) for ad in diziler}
    beklenen = {ad: len(deger) for ad, deger in canli.items()}
    assert all(beklenen.values()), f"boş dizi alanı takma adı ölçemez: {beklenen}"

    alanlar.update(canli)
    alanlar["bolumler"] = dict(rapor.bolumler)
    ikinci = auditors.AuditReport(**alanlar)
    for liste in canli.values():
        liste.clear()

    for ad, uzunluk in beklenen.items():
        assert isinstance(getattr(ikinci, ad), tuple), ad
        assert len(getattr(ikinci, ad)) == uzunluk, ad


def test_audit_report_rejects_foreign_row_type() -> None:
    """Benzeyen nesne KABUL EDİLMEZ — öğe tipi alan başına zorlanır."""
    rapor = _gecerli_rapor()
    yabanci = auditors.UrlCheck("u", "KAYNAK-1", True, True, "not")
    with pytest.raises(TypeError, match="InventoryRow"):
        auditors.AuditReport(
            denetci=rapor.denetci,
            ham_metin=rapor.ham_metin,
            bolumler=dict(rapor.bolumler),
            denetim_tablosu=rapor.denetim_tablosu,
            kaynak_profili=rapor.kaynak_profili,
            yeniden_dogrulama=(yabanci,),
            url_orneklem=rapor.url_orneklem,
            unit_snapshot_sha=rapor.unit_snapshot_sha,
        )


YABANCI_SATIR_VAKALARI = (
    (
        "denetim_tablosu",
        "AuditRow",
        auditors.InventoryRow(UNIT_A, "supported", "#1", "Tek cümle."),
    ),
    (
        "yeniden_dogrulama",
        "InventoryRow",
        auditors.UrlCheck("u", "KAYNAK-1", True, True, "not"),
    ),
    (
        "url_orneklem",
        "UrlCheck",
        auditors.InventoryRow(UNIT_A, "supported", "#1", "Tek cümle."),
    ),
    (
        "kaynak_profili",
        "KaynakProfili",
        auditors.InventoryRow(UNIT_A, "supported", "#1", "Tek cümle."),
    ),
)


@pytest.mark.parametrize(
    "alan, beklenen_tip, yabanci",
    YABANCI_SATIR_VAKALARI,
    ids=[vaka[0] for vaka in YABANCI_SATIR_VAKALARI],
)
def test_audit_report_rejects_a_foreign_row_in_each_sequence_field(
    alan: str, beklenen_tip: str, yabanci: object
) -> None:
    """Tip kapısı ALAN BAŞINA ölçülür — tek alanı sınamak diğerini kapsamaz."""
    rapor = _gecerli_rapor()
    alanlar = {
        "denetci": rapor.denetci,
        "ham_metin": rapor.ham_metin,
        "bolumler": dict(rapor.bolumler),
        "denetim_tablosu": rapor.denetim_tablosu,
        "kaynak_profili": rapor.kaynak_profili,
        "yeniden_dogrulama": rapor.yeniden_dogrulama,
        "url_orneklem": rapor.url_orneklem,
        "unit_snapshot_sha": rapor.unit_snapshot_sha,
    }
    alanlar[alan] = (yabanci,)
    with pytest.raises(TypeError, match=beklenen_tip):
        auditors.AuditReport(**alanlar)


def test_the_foreign_row_matrix_covers_every_sequence_field() -> None:
    """Matris KAPALI: ileride eklenen her dizi alanı buraya girmek ZORUNDA.

    `from __future__ import annotations` yüzünden alan tipleri METİNDİR; dizi
    alanı `tuple[...]` yazımından tanınır. Yeni bir dizi alanı eklenip matrise
    yazılmazsa bu test DÜŞER — kapanış elle seçilmiş örnekle değil, üretilmiş
    kümeyle kanıtlanır.
    """
    dizi_alanlari = _dizi_alanlari()
    assert dizi_alanlari, "dizi alanı ölçülemedi — tarama hiçbir şey kanıtlamaz"
    assert dizi_alanlari == {vaka[0] for vaka in YABANCI_SATIR_VAKALARI}


def test_audit_report_does_not_alias_the_caller_sections() -> None:
    """`bolumler` çağıranın sözlüğüyle takma ad PAYLAŞMAZ (kurucu-sonrası mutasyon).

    Salt-okunur olması yetmez: `MappingProxyType` çağıranın sözlüğünün CANLI
    görüntüsüdür. Kapıdan geçmiş beş anahtarlı küme yapımdan SONRA
    değiştirilebilirdi.
    """
    rapor = _gecerli_rapor()
    cagiran = dict(rapor.bolumler)
    ikinci = auditors.AuditReport(
        denetci=rapor.denetci,
        ham_metin=rapor.ham_metin,
        bolumler=cagiran,
        denetim_tablosu=rapor.denetim_tablosu,
        kaynak_profili=rapor.kaynak_profili,
        yeniden_dogrulama=rapor.yeniden_dogrulama,
        url_orneklem=rapor.url_orneklem,
        unit_snapshot_sha=rapor.unit_snapshot_sha,
    )
    once = dict(ikinci.bolumler)
    cagiran[auditors.BOLUM_ANAHTARLARI[0]] = "SONRADAN DEĞİŞTİ"
    cagiran["UYDURMA BÖLÜM"] = "sonradan eklendi"
    del cagiran[auditors.BOLUM_ANAHTARLARI[4]]
    assert dict(ikinci.bolumler) == once
    assert set(ikinci.bolumler) == set(auditors.BOLUM_ANAHTARLARI)


# ─── K-14 ön kontrol ────────────────────────────────────────────────────────


ARAC = "denetci-2-araci"


class _KayitliProb:
    """Argümanını KAYDEDEN prob — hangi aracın yoklandığı ölçülebilsin diye.

    Argümanı yok sayan bir prob (`lambda _: False`) yanlış aracı yoklayan bir
    uygulamayı yeşil bırakırdı: ölçülmeyen erişim "ölçüldü" sayılır ve K-14'ün
    bütün varlık sebebi düşerdi.
    """

    def __init__(self, sonuc: bool | Exception) -> None:
        self.cagrilar: list[str] = []
        self._sonuc = sonuc

    def __call__(self, arac: str) -> bool:
        self.cagrilar.append(arac)
        if isinstance(self._sonuc, Exception):
            raise self._sonuc
        return self._sonuc


def test_preflight_failure_blocks_round() -> None:
    prob = _KayitliProb(False)
    sonuc = auditors.preflight(ARAC, prob=prob)
    assert sonuc.web_erisimi is False
    assert sonuc.tur_baslayabilir is False
    assert sonuc.sebep
    assert prob.cagrilar == [ARAC], (
        f"ön kontrol yanlış aracı yokladı: {prob.cagrilar} — ölçüm hangi araç "
        "için yapıldıysa sonuç O aracın sonucudur"
    )

    # Prob patlarsa da fail-closed: istisna "erişim var" diye okunmaz.
    patlayan_prob = _KayitliProb(RuntimeError("bağlantı yok"))
    patlayan = auditors.preflight(ARAC, prob=patlayan_prob)
    assert patlayan.tur_baslayabilir is False
    assert "bağlantı yok" in patlayan.sebep
    assert patlayan_prob.cagrilar == [ARAC]


def test_preflight_without_a_probe_is_fail_closed() -> None:
    """Ölçülmemiş erişim "var" sayılmaz — prob yoksa tur BAŞLAMAZ."""
    assert auditors.preflight(ARAC).tur_baslayabilir is False


def test_preflight_success_allows_round() -> None:
    prob = _KayitliProb(True)
    sonuc = auditors.preflight(ARAC, prob=prob)
    assert sonuc.web_erisimi is True
    assert sonuc.tur_baslayabilir is True
    assert sonuc.arac == ARAC
    assert prob.cagrilar == [ARAC], (
        f"ön kontrol yanlış aracı yokladı: {prob.cagrilar} — başka bir aracın "
        "erişimi bu turu başlatamaz"
    )


def test_build_packet_rejects_a_round_below_the_source_floor(tmp_path: Path) -> None:
    """Elemeden sonra TEK kaynak kalan koşuda paket KURULMAZ (K-127).

    Kapanış turunda ölçüldü: `yetkili_kaynak_sayisi`'nı `len(sources)`'tan
    elenmemiş kimlik sayısına çevirmek, taban ihlalini KAZARA engelleyen
    davranışı da kaldırdı — üç kaynakla kurulup ikisi elenen bir pakette
    yetkili sayı 1'e iniyor ve iki tur kapısı da "1 kaynak" diyen bir raporu
    KABUL ediyordu. Tek kaynakla mutabakat sinyali ilkece üretilemez.
    """
    kaynaklar = ["a metni", "b metni", "c metni"]
    raporlar = [
        (
            bd.DoctorReport(
                sonuc=bd.SONUC_ELENDI,
                notlar=(),
                elemeler=(
                    bd.Bulgu(
                        kontrol="sahte-kontrol",
                        aile="bolum-ve-alan-tamligi",
                        seviye=bd.SEVIYE_ELEME,
                        mesaj="elenmis kaynak",
                    ),
                ),
                kaynak_adi=f"kaynak-{sira}",
                icerik_ozeti=identity.canonical_sha(metin),
            )
            if sira > 0
            else bd.DoctorReport(
                sonuc=bd.SONUC_GECTI,
                notlar=(),
                elemeler=(),
                kaynak_adi=f"kaynak-{sira}",
                icerik_ozeti=identity.canonical_sha(metin),
            )
        )
        for sira, metin in enumerate(kaynaklar)
    ]
    assert bd.gate_round(raporlar).dur is True, "fixture tabanın ALTINDA olmalı"

    with pytest.raises(ValueError, match="tabanın altında"):
        auditors.build_packet(
            brief="Kuyumculuk brief metni.",
            sources=kaynaklar,
            doctor_reports=raporlar,
            active_package=None,
            unit_snapshot={},
            run_id="kosu-2026-09-08-t9",
            sector_id=uuid.uuid4(),
            dest=tmp_path / "taban-alti",
        )


def test_build_packet_accepts_the_floor_exactly(tmp_path: Path) -> None:
    """BOŞ-KÜME kontrol kolu: TAM tabanda (iki geçerli kaynak) paket KURULUR."""
    kaynaklar = ["a metni", "b metni", "c metni"]
    raporlar = [
        (
            bd.DoctorReport(
                sonuc=bd.SONUC_ELENDI,
                notlar=(),
                elemeler=(
                    bd.Bulgu(
                        kontrol="sahte-kontrol",
                        aile="bolum-ve-alan-tamligi",
                        seviye=bd.SEVIYE_ELEME,
                        mesaj="elenmis kaynak",
                    ),
                ),
                kaynak_adi=f"kaynak-{sira}",
                icerik_ozeti=identity.canonical_sha(metin),
            )
            if sira == 2
            else bd.DoctorReport(
                sonuc=bd.SONUC_GECTI,
                notlar=(),
                elemeler=(),
                kaynak_adi=f"kaynak-{sira}",
                icerik_ozeti=identity.canonical_sha(metin),
            )
        )
        for sira, metin in enumerate(kaynaklar)
    ]
    ref = auditors.build_packet(
        brief="Kuyumculuk brief metni.",
        sources=kaynaklar,
        doctor_reports=raporlar,
        active_package=None,
        unit_snapshot={},
        run_id="kosu-2026-09-08-t9",
        sector_id=uuid.uuid4(),
        dest=tmp_path / "tam-taban",
    )
    assert ref.yetkili_kaynak_sayisi == 2


# ═══ Düzeltme turu — B3(2): rol yolları takma ad/symlink/kök-dışı KABUL ETMEZ ═


def _rol_yollu_ref(ref, *, kok: Path, kopyalar: dict[str, Path]):
    return auditors.PacketRef(
        run_id=ref.run_id,
        yetkili_kaynak_sayisi=ref.yetkili_kaynak_sayisi,
            kaynak_seti_sha=ref.kaynak_seti_sha,
        sector_id=ref.sector_id,
        kok=kok,
        kopyalar=kopyalar,
        kopya_shalari=dict(ref.kopya_shalari),
        unit_snapshot=dict(ref.unit_snapshot),
        unit_snapshot_sha=ref.unit_snapshot_sha,
    )


def test_packet_ref_rejects_a_symlinked_role_path(tmp_path: Path) -> None:
    """Rol adı doğru olsa da symlink KABUL EDİLMEZ — yol kendi canonical'i olmalı.

    Sızıntı ekseni: bir rol dizini kardeşinin (ya da paket dışının) takma adı
    olursa `cwd` ayrımı görünüşte durur, gerçekte iki rol AYNI yeri görür.
    """
    ref = _paket(tmp_path)
    sahte_kok = tmp_path / "sahte-kok"
    sahte_kok.mkdir()
    disarisi = tmp_path / "disarisi"
    disarisi.mkdir()
    (sahte_kok / "denetci-1").symlink_to(disarisi, target_is_directory=True)
    (sahte_kok / "denetci-2").mkdir()

    with pytest.raises(ValueError, match="rol yolu"):
        _rol_yollu_ref(
            ref,
            kok=sahte_kok,
            kopyalar={
                "denetci-1": sahte_kok / "denetci-1",
                "denetci-2": sahte_kok / "denetci-2",
            },
        )


def test_packet_ref_rejects_a_role_path_outside_the_root(tmp_path: Path) -> None:
    """Kök dışındaki rol yolu REDDEDİLİR — paket sınırı yol düzeyinde ölçülür."""
    ref = _paket(tmp_path)
    disarisi = tmp_path / "kok-disi"
    disarisi.mkdir()
    (disarisi / "denetci-2").mkdir()

    with pytest.raises(ValueError, match="rol yolu"):
        _rol_yollu_ref(
            ref,
            kok=ref.kok,
            kopyalar={
                "denetci-1": ref.kopyalar["denetci-1"],
                "denetci-2": disarisi / "denetci-2",
            },
        )


def test_packet_ref_rejects_two_roles_sharing_one_directory(
    tmp_path: Path,
) -> None:
    """İki rol AYNI dizini gösteremez — kör bağımsızlığın yol ayağı."""
    ref = _paket(tmp_path)
    with pytest.raises(ValueError, match="rol yolu"):
        _rol_yollu_ref(
            ref,
            kok=ref.kok,
            kopyalar={
                "denetci-1": ref.kopyalar["denetci-1"],
                "denetci-2": ref.kopyalar["denetci-1"],
            },
        )


def test_packet_ref_accepts_the_paths_build_packet_produced(
    tmp_path: Path,
) -> None:
    """POZİTİF KONTROL: kapı gerçek paketi REDDETMEZ."""
    ref = _paket(tmp_path)
    ikinci = _rol_yollu_ref(ref, kok=ref.kok, kopyalar=dict(ref.kopyalar))
    assert dict(ikinci.kopyalar) == dict(ref.kopyalar)


# ═══ Düzeltme turu — B4(1): YETKİLİ kaynak sayısı pakette taşınır ═══════════


def test_build_packet_carries_the_authoritative_source_count(
    tmp_path: Path,
) -> None:
    """Yetkili sayı paketi KURAN taraftan gelir — rapordan DEĞİL.

    Değer artık ELENMEMİŞ kimlik sayısıdır; elemesiz fixture'da bu `sources`
    uzunluğuna eşittir. TEK kaynak artık paket bile kurdurmaz (K-127 tabanı),
    o kol ayrı testte ölçülür.
    """
    for sayi in (2, 3):
        ref = _paket(tmp_path / f"kaynak-{sayi}", kaynak_sayisi=sayi)
        assert ref.yetkili_kaynak_sayisi == sayi

    with pytest.raises(ValueError, match="tabanın altında"):
        _paket(tmp_path / "kaynak-1", kaynak_sayisi=1)


@pytest.mark.parametrize("deger", [0, 4, -1, True, "2", 2.0, None])
def test_packet_ref_rejects_an_out_of_contract_source_count(
    tmp_path: Path, deger
) -> None:
    """Sayı sözleşmenin 1..3 aralığında bir TAM SAYI olmak ZORUNDA."""
    ref = _paket(tmp_path)
    with pytest.raises((ValueError, TypeError), match="yetkili_kaynak_sayisi"):
        auditors.PacketRef(
            run_id=ref.run_id,
            yetkili_kaynak_sayisi=deger,
            kaynak_seti_sha=ref.kaynak_seti_sha,
            sector_id=ref.sector_id,
            kok=ref.kok,
            kopyalar=dict(ref.kopyalar),
            kopya_shalari=dict(ref.kopya_shalari),
            unit_snapshot=dict(ref.unit_snapshot),
            unit_snapshot_sha=ref.unit_snapshot_sha,
        )


# ─── DENETİM TABLOSU — tipli okuma (çoğunluk sınıfı düz yazıdan çıkarılmaz) ──


def _pinli_baslik_hucreleri(metin: str, isaret: str) -> tuple[str, ...]:
    """İşaretten SONRAKİ ilk markdown tablosunun başlık hücreleri.

    Sözleşme başlık satırını *"aynen şu başlık satırıyla"* diye dayatır; bu
    yardımcı o satırı OKUR. Modüldeki demet burada UYDURULMAZ (İlke 9) —
    sözleşme başlığı değişip demet güncellenmezse test DÜŞER.
    """
    bas = metin.index(isaret)
    eslesme = re.search(r"\n\|(.+?)\|\n\|[-| :]+\|\n", metin[bas:])
    assert eslesme is not None, f"{isaret!r} sonrası başlık satırı YOK"
    return tuple(h.strip() for h in eslesme.group(1).split("|"))


def test_denetim_basligi_matches_pinned_contract_header() -> None:
    """Sütunların ADI ve SIRASI pinli sözleşmeden ölçülür (sayı da oradan)."""
    olculen = _pinli_baslik_hucreleri(
        _pinli("hakem-denetci-gorevi.md"), "1) DENETİM TABLOSU"
    )
    assert olculen == auditors._DENETIM_BASLIK_HUCRELERI, (
        "sözleşmenin dayattığı başlık satırı ile modülün beklediği hücreler "
        f"ayrıştı — sözleşme {olculen}, modül {auditors._DENETIM_BASLIK_HUCRELERI}"
    )


def test_envanter_basligi_matches_pinned_contract_header() -> None:
    """Envanter başlığı da ARTIK sözleşmede yazılı — tahmin edilmiyor."""
    olculen = _pinli_baslik_hucreleri(
        _pinli("hakem-denetci-gorevi.md"), "5) YENİDEN DOĞRULAMA ENVANTERİ"
    )
    assert olculen == auditors._ENVANTER_BASLIK_HUCRELERI


def test_oneri_degerleri_measured_from_pinned_contract() -> None:
    """Öneri uzayı KAPALI — dört değer, sözleşmenin ADIM 2 satırından ölçülür."""
    metin = _pinli("hakem-denetci-gorevi.md")
    eslesme = re.search(r"^ÖNERİ: (.+?) \(\+tek cümle gerekçe\)\.", metin, re.M)
    assert eslesme is not None, "ÖNERİ satırı sözleşmede bulunamadı"
    olculen = tuple(d.strip() for d in eslesme.group(1).split("/"))
    assert olculen == auditors.ONERI_DEGERLERI


def test_validate_report_returns_parsed_audit_table() -> None:
    """Tablo TİPLİ satırlara çevrilir; `kaynaklar` numara kümesidir."""
    sonuc = _dogrula(_rapor_metni())
    assert sonuc.rapor is not None, sonuc.errors
    satirlar = sonuc.rapor.denetim_tablosu
    assert [s.no for s in satirlar] == [1, 2]
    assert satirlar[0].kaynaklar == frozenset({1, 2})
    assert satirlar[1].kaynaklar == frozenset({3})
    assert satirlar[0].kaynak_iddialari == frozenset(
        {auditors.KaynakIddiasi(1, 1), auditors.KaynakIddiasi(2, 4)}
    )
    assert satirlar[1].kaynak_iddialari == frozenset({auditors.KaynakIddiasi(3, 2)})
    assert satirlar[0].alan == "cta_kaliplari"
    assert satirlar[0].sinif == "2-3"
    assert satirlar[0].oneri == "al"
    assert satirlar[1].sinif == auditors.SINIF_TEKIL


def _denetim_hatasi(satir: str) -> str:
    """Tek satırlık bozuk tabloyu doğrular ve hata metnini döndürür."""
    sonuc = _dogrula(_rapor_metni(denetim=_denetim_bolumu([satir])))
    assert sonuc.rapor is None, "bozuk tablo rapor ÜRETMEMELİ"
    return " · ".join(sonuc.errors)


# TEMİZ satır ve KONUMLAR sözleşmenin sütun listesinden TÜRER. Sözleşme
# 2026-09-11'de araya bir sütun (`kaynak-iddialari`) ekledi; elle yazılmış her
# hücre dizisi o gün kaydı ve "şu sütunu bozdum" diyen bir test aslında
# KOMŞUSUNU bozuyor olurdu — sessiz yeşil.
_TEMIZ_DENETIM_HUCRELERI = {
    "no": "1",
    "alan": "cta_kaliplari",
    "iddia-özeti": "iddia",
    "kaynak-iddialari": "K1#1, K2#4",
    "kaynaklar": "1,2",
    "sınıf": "2-3",
    "bayraklar": "—",
    "öneri": "al",
    "gerekçe": "Tek cümle.",
}


def _denetim_satiri(**sapma: str) -> str:
    """Sözleşme sırasında TEMİZ bir satır; `sapma` adlandırılmış hücreyi bozar."""
    hucreler = dict(_TEMIZ_DENETIM_HUCRELERI)
    bilinmeyen = set(sapma) - set(hucreler)
    assert not bilinmeyen, f"sözleşmede olmayan sütun: {bilinmeyen}"
    hucreler.update(sapma)
    return (
        "| "
        + " | ".join(hucreler[ad] for ad in auditors._DENETIM_BASLIK_HUCRELERI)
        + " |"
    )


def test_temiz_denetim_satiri_sozlesmenin_sutunlariyla_ortusur() -> None:
    """TABAN: kurucunun anahtarları sözleşmenin sütunlarıdır — eksiksiz."""
    assert tuple(_TEMIZ_DENETIM_HUCRELERI) == auditors._DENETIM_BASLIK_HUCRELERI
    assert _dogrula(_rapor_metni(denetim=_denetim_bolumu([_denetim_satiri()]))).rapor


def test_audit_table_rejects_prose_in_source_column() -> None:
    hatalar = _denetim_hatasi(
        _denetim_satiri(**{"kaynaklar": "hepsi", "sınıf": "3-3"})
    )
    assert "kaynaklar" in hatalar


def test_audit_table_rejects_empty_source_column() -> None:
    hatalar = _denetim_hatasi(
        _denetim_satiri(**{"kaynaklar": "", "sınıf": "tekil"})
    )
    assert "kaynaklar" in hatalar


_BOS_HUCRE_SUTUNLARI = ("alan", "iddia-özeti", "bayraklar", "gerekçe")
"""Boş bırakılamayan METİN sütunları.

`kaynaklar` · `kaynak-iddialari` · `sınıf` · `öneri` burada YOKTUR: onların
boşluğunu kendi kapalı değer kapıları yakalar ve o kapılar ayrıca ölçülür.
`no` da yoktur (tip kapısı).
"""


@pytest.mark.parametrize("sutun", _BOS_HUCRE_SUTUNLARI)
def test_audit_table_rejects_an_empty_text_cell(sutun: str) -> None:
    """ÜRETİLMİŞ MATRİS: boş bırakılan HER metin hücresi satırı düşürür.

    Elle tek sütun seçilseydi kapının öteki üç sütunu ölçülmemiş kalırdı;
    mutasyon ölçümü tam olarak bu boşluğu yakaladı (kapı testsiz eklenmişti).
    """
    hatalar = _denetim_hatasi(_denetim_satiri(**{sutun: ""}))
    assert "boş hücre" in hatalar and sutun in hatalar


# ─── `kaynak-iddialari`: atıf ADAYA bağlanır (dış depo `12beec1`) ───────────


def test_kaynak_iddialari_sutunu_pinli_sozlesmede_yazili() -> None:
    """Sütunun VARLIĞI da biçimi de sözleşmeden ölçülür, uydurulmaz."""
    metin = _pinli("hakem-denetci-gorevi.md")
    assert "kaynak-iddialari" in auditors._DENETIM_BASLIK_HUCRELERI
    assert re.search(r"Biçim `K<kaynak-no>#<iddia-no>`", metin)
    # TUTARLILIK kuralı da sözleşmenin kendi cümlesidir.
    assert "İKİ SÜTUN TUTARLI OLMAK ZORUNDADIR" in metin


_BICIM_IZI = "`K<kaynak>#<iddia>` taşır"
"""BİÇİM kapısının KENDİ izi.

Yalnız sütun adını aramak yetmez: tutarlılık kapısının mesajı da o adı taşır,
yani biçim kapısı sökülse bile test yeşil kalırdı. Mutasyon ölçümü tam olarak
bunu yakaladı (boş hücre kolu sağ kaldı).
"""


@pytest.mark.parametrize(
    "deger",
    ["", "hepsi", "K1", "1#1", "K1#1 K2#4", "K2#4, K1#1", "K1#1, K1#1", "K1#0"],
    ids=[
        "bos", "duzyazi", "iddiasiz", "kaynaksiz", "ayracsiz",
        "azalan", "tekrar", "sifir-iddia",
    ],
)
def test_kaynak_iddialari_bicimi_kapalidir(deger: str) -> None:
    """Biçim kapalı: serbest yazım bağı sessizce koparırdı (fail-closed)."""
    hatalar = _denetim_hatasi(_denetim_satiri(**{"kaynak-iddialari": deger}))
    assert _BICIM_IZI in hatalar, hatalar


def test_kaynak_iddialari_kaynaklar_sutunuyla_tutarli_olmak_zorunda() -> None:
    """Sözleşme: geçen kaynak numaralarının kümesi `kaynaklar`a EŞİTTİR.

    Eşitlik ÇİFT YÖNLÜ ölçülür: eksik taraf da fazla taraf da düşer. Tek yönlü
    bir kapı (`⊆`) "üç kaynakta gördüm" diyen bir satırın tek iddia göstermesine
    izin verirdi ve o satır motorda hâlâ ÜÇ kaynaklık çoğunluk sayardı.
    """
    eksik = _denetim_hatasi(
        _denetim_satiri(**{"kaynak-iddialari": "K1#1", "kaynaklar": "1,2"})
    )
    assert "tutarlı" in eksik
    fazla = _denetim_hatasi(
        _denetim_satiri(
            **{"kaynak-iddialari": "K1#1, K2#4", "kaynaklar": "1", "sınıf": "tekil"}
        )
    )
    assert "tutarlı" in fazla


# ─── KAYNAK PROFİLİ: düz yazıdan TABLOYA, `resmi` TİPLİ (K-126'nın ayağı) ───


def test_kaynak_profili_basligi_matches_pinned_contract_header() -> None:
    olculen = _pinli_baslik_hucreleri(
        _pinli("hakem-denetci-gorevi.md"), "3) KAYNAK PROFİLİ"
    )
    assert olculen == auditors._KAYNAK_PROFIL_BASLIK_HUCRELERI


def test_kaynak_profili_resmi_degerleri_pinli_sozlesmeden_olculur() -> None:
    """`resmi` kapalı kümesi sözleşmenin kendi cümlesinden okunur."""
    metin = _pinli("hakem-denetci-gorevi.md")
    eslesme = re.search(
        r"`resmi` sütunu `(\w+)` ya da `([\wıİğĞşŞçÇöÖüÜ]+)`", metin
    )
    assert eslesme is not None, "sözleşmede `resmi` kapalı kümesi bulunamadı"
    assert eslesme.groups() == auditors.RESMI_DEGERLERI


def test_validate_report_returns_parsed_source_profile() -> None:
    """Profil TİPLİ okunur: resmîlik yargısı artık motorun görebileceği yerde."""
    sonuc = _dogrula(_rapor_metni())
    assert sonuc.rapor is not None, sonuc.errors
    profil = sonuc.rapor.kaynak_profili
    assert [p.kaynak for p in profil] == [1, 2, 3]
    assert [p.resmi for p in profil] == [True, False, False]
    assert profil[0].not_metni.startswith("Mevzuat")


def _profil_hatasi(satirlar: list[str]) -> str:
    sonuc = _dogrula(_rapor_metni(profil=_kaynak_profili_bolumu(satirlar)))
    assert sonuc.rapor is None, "bozuk profil tablosu rapor ÜRETMEMELİ"
    return " · ".join(sonuc.errors)


@pytest.mark.parametrize(
    "satir,iz",
    [
        ("| 1 | belki | Not. |", "resmi"),
        ("| 1 | EVET | Not. |", "resmi"),
        ("| 1 |  | Not. |", "resmi"),
        ("| bir | evet | Not. |", "kaynak"),
        ("| 0 | evet | Not. |", "kaynak"),
        ("| 1 | evet |  |", "not"),
    ],
    ids=["kapali-kume", "buyuk-harf", "bos", "sayi-degil", "sifir", "notsuz"],
)
def test_kaynak_profili_hucre_sozlesmesi(satir: str, iz: str) -> None:
    assert iz in _profil_hatasi([satir])


def test_kaynak_profili_kaynak_numarasi_tekrar_edemez() -> None:
    """Numara KİMLİKTİR: aynı kaynağa iki resmîlik yargısı çözülemez.

    Motor K-126 istisnasını kaynak numarasından çözer; tekrar eden numara
    "hangi yargı geçerli" sorusunu sessiz bir seçime çevirirdi.
    """
    hatalar = _profil_hatasi(
        ["| 1 | evet | Not. |", "| 1 | hayır | Başka not. |"]
    )
    assert "TEKRAR" in hatalar


def test_kaynak_profili_tablosuz_rapor_reddedilir() -> None:
    """Düz yazı profil ARTIK geçmez — sözleşme tabloyu dayatıyor."""
    sonuc = _dogrula(
        _rapor_metni(profil="KAYNAK-1 disiplini yeterli; KAYNAK-2 yerel değil.")
    )
    assert sonuc.rapor is None
    assert any("KAYNAK PROFİLİ" in hata for hata in sonuc.errors), sonuc.errors


def test_empty_cell_matrix_covers_the_gates_own_column_list() -> None:
    """Matris KAPALI: kapının listesine sütun eklenip matrise yazılmazsa DÜŞER."""
    import inspect

    kaynak = inspect.getsource(auditors._denetim_tablosu)
    olculen = set(re.findall(r'\(\s*"([a-zçğıöşü\-]+)",\s*\w+\),?\s*\n', kaynak))
    assert olculen == set(_BOS_HUCRE_SUTUNLARI), (
        f"kapının sütun listesi {sorted(olculen)}, matris "
        f"{sorted(_BOS_HUCRE_SUTUNLARI)}"
    )


def test_audit_table_rejects_unordered_sources() -> None:
    hatalar = _denetim_hatasi(
        _denetim_satiri(**{"kaynaklar": "2,1"})
    )
    assert "artan" in hatalar


def test_audit_table_rejects_repeated_sources() -> None:
    hatalar = _denetim_hatasi(
        _denetim_satiri(**{"kaynaklar": "1,1"})
    )
    assert "artan" in hatalar


def test_audit_table_rejects_source_number_out_of_range() -> None:
    hatalar = _denetim_hatasi(
        _denetim_satiri(**{"kaynaklar": "1,4"})
    )
    assert "kaynak numarası" in hatalar


def test_audit_table_rejects_ratio_contradicting_source_count() -> None:
    """`2-3` diyorsa kaynak hücresinde İKİ numara olmak zorunda."""
    hatalar = _denetim_hatasi(
        _denetim_satiri(**{"kaynak-iddialari": "K1#1", "kaynaklar": "1"})
    )
    assert "sınıf" in hatalar


def test_audit_table_rejects_tekil_with_two_sources() -> None:
    hatalar = _denetim_hatasi(
        _denetim_satiri(**{"sınıf": "tekil"})
    )
    assert "tekil" in hatalar


def test_audit_table_rejects_celiski_with_single_source() -> None:
    """Tek kaynak KENDİSİYLE çelişemez — sözleşmenin kendi hükmü."""
    hatalar = _denetim_hatasi(
        _denetim_satiri(
            **{
                "kaynak-iddialari": "K2#4",
                "kaynaklar": "2",
                "sınıf": "çelişki",
                "öneri": "açık-soru",
            }
        )
    )
    assert "çelişki" in hatalar


def test_audit_table_accepts_celiski_with_two_sources() -> None:
    """Kontrol kolu: çelişki İKİ numarayla MEŞRUDUR — kapı fazla kapamıyor."""
    sonuc = _dogrula(
        _rapor_metni(
            denetim=_denetim_bolumu(
                [
                    _denetim_satiri(
                        **{"sınıf": "çelişki", "öneri": "açık-soru"}
                    )
                ]
            )
        )
    )
    assert sonuc.rapor is not None, sonuc.errors
    assert sonuc.rapor.denetim_tablosu[0].sinif == auditors.SINIF_CELISKI


def test_audit_table_rejects_recommendation_outside_closed_set() -> None:
    hatalar = _denetim_hatasi(
        _denetim_satiri(**{"öneri": "belki"})
    )
    assert "öneri" in hatalar


def test_audit_table_rejects_non_increasing_row_numbers() -> None:
    """`no` SATIR KİMLİĞİDİR — tekrar eden numara referansı çözülemez kılar."""
    sonuc = _dogrula(
        _rapor_metni(
            denetim=_denetim_bolumu(
                [
                    _denetim_satiri(**{"no": "2"}),
                    _denetim_satiri(**{"no": "1", "alan": "kanca_kaliplari"}),
                ]
            )
        )
    )
    assert sonuc.rapor is None
    assert "artan" in " · ".join(sonuc.errors)


def test_audit_table_rejects_a_row_with_too_few_columns() -> None:
    """Sütun SAYISI sözleşmeden okunur — mesaj da o sayıyı söyler."""
    hatalar = _denetim_hatasi("| 1 | cta_kaliplari | iddia | 1,2 | 2-3 | al |")
    assert f"{len(auditors._DENETIM_BASLIK_HUCRELERI)} sütunlu değil" in hatalar


def test_audit_table_rejects_a_wholly_empty_row() -> None:
    """Tamamen boş satır AYIRAÇ değildir — veri satırı olarak kapıya girer.

    Hakem turu 1 (orta, ÖLÇÜLDÜ): ayıraç yüklemi boş hücreleri saymadan ÖNCE
    eliyordu (`for h in hucreler if h`); tamamen boş bir satırda üreteç boş
    kalıyor, `all(())` True dönüyor ve satır sessizce düşüyordu — sütun sayısı
    ve boş-hücre kapıları o satırı HİÇ görmüyordu. Boş-hücre matrisi bunu
    kaçırdı: matris her seferinde TEK hücreyi boşaltıyor.
    """
    sonuc = _dogrula(
        _rapor_metni(
            denetim=_denetim_bolumu(
                [
                    _denetim_satiri(),
                    "|" + "  |" * len(auditors._DENETIM_BASLIK_HUCRELERI),
                ]
            )
        )
    )
    assert sonuc.rapor is None, "boş satır sessizce DÜŞMEMELİ"
    # Satır artık VERİ satırıdır ve ilk kapıya takılır: `no` hücresi boştur.
    # Ölçülen şey "hangi mesaj" değil, satırın kapılara GİRMESİ ve raporu
    # düşürmesidir — eskiden hiçbir kapıya girmiyordu.
    hatalar = " · ".join(sonuc.errors)
    assert "satırı 2" in hatalar and "`no`" in hatalar, hatalar


def test_separator_row_is_still_recognised() -> None:
    """BOŞ-KÜME kontrol kolu: gerçek ayıraç hâlâ ayıraçtır (kapı fazla kapamıyor)."""
    sonuc = _dogrula(_rapor_metni())
    assert sonuc.rapor is not None, sonuc.errors
    assert len(sonuc.rapor.denetim_tablosu) == 2


def test_audit_table_rejects_a_different_header_row() -> None:
    """Başlık farklı yazılmışsa VERİ satırı sanılır ve kapı düşer."""
    sonuc = _dogrula(
        _rapor_metni(
            denetim=(
                DENETIM_BASLIGI.replace("iddia-özeti", "iddia")
                + "\n"
                + _denetim_satiri()
            )
        )
    )
    assert sonuc.rapor is None
    assert sonuc.errors


def test_audit_table_rejects_an_empty_table() -> None:
    """Boş tablo = denetim yapılmamış; sessizce geçmez."""
    sonuc = _dogrula(_rapor_metni(denetim=DENETIM_BASLIGI))
    assert sonuc.rapor is None
    assert "DENETİM TABLOSU" in " · ".join(sonuc.errors)
