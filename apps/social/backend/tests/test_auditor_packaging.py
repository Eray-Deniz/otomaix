"""Denetçi girdi paketleyicisi — körlük · biçim kapısı · veri kapısı (Plan 2 Task 9).

Ölçülen sözleşme dört başlıkta toplanır:

* **K-137 körlük.** Pakete yazılan HİÇBİR baytta araç kimliği bulunmaz. Beklenen
  araç adı kümesi burada bulunan örneklerden DEĞİL, kavramdan yazılır (bir yapay
  zekâ asistanının satıcı/ürün adı) ve ayrıca **pinlenmiş sözleşmelerden ölçülen**
  adlarla bağımsız olarak sınanır — iki kaynak birbirinin yerine geçmez.
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


def test_arac_kimlikleri_cover_the_pinned_contract_tool_names() -> None:
    """Kavramsal küme ile modül sabiti aynı; ölçülen adlar İKİSİ tarafından da kapsanır.

    Ölçülen adlar iki pinli sözleşmeden gelir: `_SABLON.md` üç araştırma aracını,
    `hakem-denetci-gorevi.md` iki denetçi aracını ADIYLA anar.
    """
    assert tuple(sorted(auditors.ARAC_KIMLIKLERI)) == tuple(
        sorted(KAVRAMSAL_ARAC_ADLARI)
    )

    sablon = _pinli("_SABLON.md")
    arastirma_blok = re.search(r"Üç araştırma aracına da \((.*?)\)", sablon)
    assert arastirma_blok is not None, "_SABLON.md üç aracı adıyla anmıyor"
    olculen = [ad.strip() for ad in arastirma_blok.group(1).split("/")]

    gorev = _pinli("hakem-denetci-gorevi.md")
    denetci_blok = re.search(r"Bu görev iki denetçiye \((.*?)\)", gorev)
    assert denetci_blok is not None, "sözleşme iki denetçi aracını adıyla anmıyor"
    olculen += [ad.strip() for ad in denetci_blok.group(1).split(" ve ")]

    assert olculen, "ölçüm boş küme döndü — tarama hiçbir şey kanıtlamaz"
    for ad in olculen:
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


def _rapor_metni(
    *,
    envanter: str | None = None,
    url: str | None = None,
    atlanan_bolum: int | None = None,
) -> str:
    govdeler = {
        1: "| no | alan | iddia | kaynaklar | sınıf | bayraklar | öneri | gerekçe |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
        "| 1 | cta_kaliplari | örnek iddia | 1,2 | 2-3 | — | koru | Tek cümle. |",
        2: _url_bolumu() if url is None else url,
        3: "KAYNAK-1 kaynak gösterme disiplini yeterli; KAYNAK-2 yerel değil.",
        4: "- Mevzuat tarihi operatöre sorulmalı mı?",
        5: _envanter_bolumu(None) if envanter is None else envanter,
    }
    parcalar = []
    for sira, baslik in enumerate(auditors.BOLUM_ANAHTARLARI, start=1):
        if sira == atlanan_bolum:
            continue
        parcalar.append(f"{sira}) {baslik}\n{govdeler[sira]}")
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


def _paket(
    tmp_path: Path,
    *,
    kaynak_sayisi: int = 3,
    kimlikler: tuple[str, ...] = ARAC_ADLI_KIMLIKLER,
):
    kaynaklar = [
        "KAYNAK metni: ChatGPT bu bölümü üretti.",
        "Gemini çıktısı — takvim temaları.",
        "Claude Code notu: cta kalıpları.",
    ][:kaynak_sayisi]
    raporlar = [
        bd.DoctorReport(
            sonuc=bd.SONUC_GECTI,
            notlar=(),
            elemeler=(),
            kaynak_adi=ad,
        )
        for ad in kimlikler[:kaynak_sayisi]
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


def test_packet_contains_no_tool_identity(tmp_path: Path) -> None:
    """Yapısal garanti: pakete yazılan hiçbir baytta araç kimliği YOK."""
    ref = _paket(tmp_path)
    dosyalar = sorted(p for p in ref.kok.rglob("*") if p.is_file())
    assert dosyalar, "paket boş — tarama hiçbir şey kanıtlamaz"

    for dosya in dosyalar:
        metin = dosya.read_text(encoding="utf-8")
        for ad in KAVRAMSAL_ARAC_ADLARI:
            assert not re.search(rf"(?<!\w){re.escape(ad)}(?!\w)", metin, re.I), (
                f"{dosya.relative_to(ref.kok)} araç kimliği taşıyor: {ad!r}"
            )
        # Kaynak KİMLİKLERİ (brief-doctor `kaynak_adi`) pakete hiç yazılmaz.
        for kimlik in ARAC_ADLI_KIMLIKLER:
            assert kimlik not in metin
        # Dosya adları da kör: yalnız KAYNAK-n.
        assert not re.search(r"(?<!\w)(gemini|chatgpt|claude)", dosya.name, re.I)

    ekler = {p.name for p in dosyalar}
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
        sector_id=ref.sector_id,
        kok=ref.kok,
        kopyalar=dict(ref.kopyalar),
        kopya_shalari=dict(ref.kopya_shalari),
        unit_snapshot=cagiran,
        unit_snapshot_sha=identity.canonical_sha(cagiran),
    )
    cagiran[UNIT_C] = {"unit_id": UNIT_C}
    assert set(ikinci.unit_snapshot) == {UNIT_A, UNIT_B}


def test_build_packet_stops_when_the_contract_pin_drifts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """M1 sıra kapısı: pin v2 doğrulanmadan paket KURULMAZ (fail-closed)."""
    sahte_depo = tmp_path / "sahte-depo"
    sahte_depo.mkdir()
    monkeypatch.setattr(auditors, "ARASTIRMA_DEPOSU_KOKU", sahte_depo)
    with pytest.raises(ContractDriftError):
        _paket(tmp_path / "paket")


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


def test_audit_report_sequences_are_tuples_and_unaliased() -> None:
    rapor = _gecerli_rapor()
    satirlar = list(rapor.yeniden_dogrulama)
    kontroller = list(rapor.url_orneklem)
    ikinci = auditors.AuditReport(
        denetci=rapor.denetci,
        ham_metin=rapor.ham_metin,
        bolumler=dict(rapor.bolumler),
        yeniden_dogrulama=satirlar,
        url_orneklem=kontroller,
        unit_snapshot_sha=rapor.unit_snapshot_sha,
    )
    satirlar.clear()
    kontroller.clear()
    assert isinstance(ikinci.yeniden_dogrulama, tuple)
    assert isinstance(ikinci.url_orneklem, tuple)
    assert len(ikinci.yeniden_dogrulama) == 2 and len(ikinci.url_orneklem) == 6


def test_audit_report_rejects_foreign_row_type() -> None:
    """Benzeyen nesne KABUL EDİLMEZ — öğe tipi alan başına zorlanır."""
    rapor = _gecerli_rapor()
    yabanci = auditors.UrlCheck("u", "KAYNAK-1", True, True, "not")
    with pytest.raises(TypeError, match="InventoryRow"):
        auditors.AuditReport(
            denetci=rapor.denetci,
            ham_metin=rapor.ham_metin,
            bolumler=dict(rapor.bolumler),
            yeniden_dogrulama=(yabanci,),
            url_orneklem=rapor.url_orneklem,
            unit_snapshot_sha=rapor.unit_snapshot_sha,
        )


# ─── K-14 ön kontrol ────────────────────────────────────────────────────────


def test_preflight_failure_blocks_round() -> None:
    sonuc = auditors.preflight("denetci-2-araci", prob=lambda _: False)
    assert sonuc.web_erisimi is False
    assert sonuc.tur_baslayabilir is False
    assert sonuc.sebep

    # Prob patlarsa da fail-closed: istisna "erişim var" diye okunmaz.
    def _patla(_: str) -> bool:
        raise RuntimeError("bağlantı yok")

    patlayan = auditors.preflight("denetci-2-araci", prob=_patla)
    assert patlayan.tur_baslayabilir is False
    assert "bağlantı yok" in patlayan.sebep


def test_preflight_without_a_probe_is_fail_closed() -> None:
    """Ölçülmemiş erişim "var" sayılmaz — prob yoksa tur BAŞLAMAZ."""
    assert auditors.preflight("denetci-2-araci").tur_baslayabilir is False


def test_preflight_success_allows_round() -> None:
    sonuc = auditors.preflight("denetci-2-araci", prob=lambda _: True)
    assert sonuc.web_erisimi is True
    assert sonuc.tur_baslayabilir is True
    assert sonuc.arac == "denetci-2-araci"
