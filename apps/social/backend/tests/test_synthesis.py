"""Sentez koşumu + çıktı doğrulayıcı (Plan 2 Task 11).

Ölçülen sözleşme beş başlıkta toplanır:

* **KANONİK SIRA.** `sentez → motor → draft`. Modül `sector_packages` tablosuna
  yazamaz; yapısal tarama `insert_draft` içe aktarımının YOKLUĞUNU kanıtlar.
* **KİMLİK SENTEZİN MALI DEĞİL.** Yol ve hash üretilen içerikten
  `identity.enumerate_content_units` + `identity.canonical_sha` ile TÜRETİLİR;
  modelin yazdığı değerler kabul edilmez. `guncelle` kimliği korur, `ekle` yeni
  kimlik alır ve `yerine_gecer` ile çıkarılana bağlanır.
* **ÇIKARMA POZİTİF KANIT İSTER (K-124), DOĞRULANMIŞ KALIP KORUNUR (K-122).**
  Reddedilen çıkarma SESSİZCE düşmez: birim içeriğe geri konur, `koru` satırı
  yazılır ve madde AÇIK SORUYA düşer.
* **TAŞMA KESMEZ (K-74/K-75).** Tavanı aşan madde DÜŞÜRÜLMEZ; yalnız `tasma`
  işaretlenir. Sayı kapı DEĞİLDİR.
* **DURUM SAHİPLİĞİ (K-82).** Zaman aşımı ve araç arızası `tamamlanmadi`
  işaretini SENTEZDEN attırır; testler GERÇEK veritabanı satırına bakar.

**Oracle bağımsızlığı.** Sentez çıktısının bölüm başlıkları ve iki taşma tavanı
bu dosyada pinlenmiş sözleşmelerden ELLE okunarak yazılmıştır; üretim
sabitlerinden TÜRETİLMEZ — türetilseydi yanlış bir değer de testi geçerdi
(totolojik oracle).

**Girdi kurucuları `identity`'yi KULLANIR.** Aktif paketin kendi bütünlük
kapısından geçmesi gerekir; elle yazılmış hash o kapıyı düşürürdü. Ölçülen şey
girdinin kendisi değil, sentezin ÜRETTİĞİdir.
"""

from __future__ import annotations

import ast
import json
import re
import uuid
from pathlib import Path

import pytest

from app.core.database import _init_connection
from app.services.sector_pipeline import auditors, identity, runs, synthesis

REPO_KOK = Path(__file__).resolve().parents[4]


# ═══ Ölçüm anında elle yazılmış BAĞIMSIZ sabitler ═══════════════════════════
#
# Kaynak: `/root/otomaix-sosyal-medya-arastirmasi/hakem-sentez-gorevi.md`
# ADIM 4 (satır 348 · 378 · 394 · 397) ve satır 395; denetçi sözleşmesi
# satır 217. Üretim sabitlerinden OKUNMAZ.

OLCULEN_BOLUM_ANAHTARLARI = ("ADAY PAKET", "DECISION_LOG", "AÇIK SORULAR", "ÖZET")
OLCULEN_ACIK_SORU_TAVANI = 10
OLCULEN_DENETCI_ONERI_TAVANI = 5


# ═══ İçerik ve kimlik kurucuları ═══════════════════════════════════════════


UNIT_KORU = "ku-111111111111"
UNIT_CIKAR = "ku-222222222222"
UNIT_MEVZUAT = "ku-333333333333"

KORUNAN_METIN = "Doğrulanmış kalıp metni"
CIKARILACAK_METIN = "Çıkarılacak kalıp metni"
MEVZUAT_METNI = "Ayar beyanı mevzuata bağlıdır"


def _tam_icerik(**degisiklik) -> dict:
    """Yazım kapısını GEÇEN eksiksiz içerik — alan kümesi kapalı ve TAM."""
    icerik = {
        "kapsam": "Kuyumculuk: altın ve gümüş takı perakendesi.",
        "ton_ve_dil": "Sıcak, güven veren, sade.",
        "gorsel_kodlar": "Yakın çekim, sıcak ışık, doku vurgusu.",
        "cta_kaliplari": [
            {
                "kalip": "Vitrini görmek için uğrayın",
                "tur": "ziyaret",
                "gerekce": "Mağaza trafiği hedefi.",
            }
        ],
        "kanca_kaliplari": [KORUNAN_METIN, CIKARILACAK_METIN],
        "takvim_temalari": ["Sevgililer Günü hediye seçimi"],
        "yasaklar_ve_hassasiyetler": [MEVZUAT_METNI],
        "video_kodlar": {"hareket": ["yavaş kaydırma"], "sahne": ["tezgâh üstü"]},
        "ozel_gun": {},
    }
    icerik.update(degisiklik)
    return icerik


AKTIF_ICERIK = _tam_icerik()

ADLI_KIMLIKLER = {
    "kanca_kaliplari[0]": UNIT_KORU,
    "kanca_kaliplari[1]": UNIT_CIKAR,
    "yasaklar_ve_hassasiyetler[0]": UNIT_MEVZUAT,
}


def _yol_kimlik(icerik: dict) -> dict[str, str]:
    """Yol → `unit_id`. Adlandırılmamış yollar deterministik kimlik alır."""
    eslemeler: dict[str, str] = {}
    for sira, yol in enumerate(sorted(identity.enumerate_content_units(icerik)), 1):
        eslemeler[yol] = ADLI_KIMLIKLER.get(yol, "ku-" + f"{sira:012x}")
    return eslemeler


def _aktif_paket() -> dict:
    icerik = AKTIF_ICERIK
    birimler = identity.enumerate_content_units(icerik)
    kimlikler = _yol_kimlik(icerik)
    return {
        "schema_version": 1,
        "content": icerik,
        "decision_log": [
            {
                "tur": "karar",
                "alan": birimler[yol]["alan"],
                "oge_yolu": yol,
                "unit_id": kimlikler[yol],
                "oge_sha": birimler[yol]["oge_sha"],
                "karar": "koru",
                "gerekce": "Önceki turdan taşındı.",
                "kanit": "",
                "aktor": "sentez",
            }
            for yol in sorted(birimler)
        ],
    }


BOZUK_SHA = "f" * 64
"""Modelin yazdığı hash — sentezin onu KABUL ETMEDİĞİ ancak böyle ölçülür."""


def _satir(karar: str, unit_id: str, yol: str, alan: str, **ek) -> dict:
    satir = {
        "tur": "karar",
        "alan": alan,
        "oge_yolu": yol,
        "unit_id": unit_id,
        "oge_sha": BOZUK_SHA,
        "karar": karar,
        "gerekce": "Sentez gerekçesi.",
        "kanit": "D1#1",
        "aktor": "sentez",
    }
    satir.update(ek)
    return satir


def _model_gunlugu(icerik: dict, *, atlanan: tuple[str, ...] = ()) -> list[dict]:
    """Modelin yazdığı "her şey kalsın" günlüğü — hash'ler BOZUK.

    `atlanan` kimlikleri günlükten düşer; çıkarma senaryoları o boşluğa kendi
    satırını koyar.
    """
    birimler = identity.enumerate_content_units(icerik)
    kimlikler = _yol_kimlik(AKTIF_ICERIK)
    satirlar = []
    for yol in sorted(birimler):
        unit_id = kimlikler.get(yol)
        if unit_id is None or unit_id in atlanan:
            continue
        satirlar.append(
            _satir("koru", unit_id, yol, birimler[yol]["alan"])
        )
    return satirlar


# ═══ Denetçi turu kurucuları ═══════════════════════════════════════════════


def _envanter(
    *satirlar: tuple[str, str], kanit: str | None = None
) -> tuple[auditors.InventoryRow, ...]:
    return tuple(
        auditors.InventoryRow(
            unit_id=uid,
            statu=statu,
            kanit=DOGRULANMIS_KAYNAK if kanit is None else kanit,
            gerekce="Tek cümle gerekçe.",
        )
        for uid, statu in satirlar
    )


DOGRULANMIS_KAYNAK = "KAYNAK-1"
DOGRULANMIS_URL = "https://ornek.example/mevzuat-2026"
COZULEMEYEN_KANIT = "D1#999"
"""Sözleşmede geçerli bir `kanit` biçimi, ama bu katmanda ÇÖZÜLEMEZ."""


def _dogrulanmis_ornekle() -> tuple[auditors.UrlCheck, ...]:
    """ADIM 1 örnekleminde DOĞRULANDI sonucu almış tek satır."""
    return (
        auditors.UrlCheck(
            url=DOGRULANMIS_URL,
            kaynak=DOGRULANMIS_KAYNAK,
            erisildi=True,
            icerik_uyumlu=True,
            not_metni="",
        ),
    )


def _aktif_gorunti_sha() -> str:
    """Aktif paketin görüntü kimliği — `PacketRef` ile AYNI ölçümden."""
    paket = _aktif_paket()
    return identity.canonical_sha(
        identity.decision_units(paket["content"], paket["decision_log"])
    )


def _rapor(
    rol: str,
    *,
    envanter: tuple[auditors.InventoryRow, ...] = (),
    oneri_sayisi: int = 1,
    ornekle: tuple[auditors.UrlCheck, ...] | None = None,
    snapshot_sha: str | None = None,
) -> auditors.AuditReport:
    oneriler = "\n".join(f"- Öneri {sira}" for sira in range(1, oneri_sayisi + 1))
    bolumler = {
        ad: (oneriler if ad == "AÇIK SORU ÖNERİLERİ" else f"{ad} gövdesi")
        for ad in auditors.BOLUM_ANAHTARLARI
    }
    return auditors.AuditReport(
        denetci=rol,
        ham_metin=f"{rol} ham raporu — Claude Code ile üretildi",
        bolumler=bolumler,
        denetim_tablosu=(
            auditors.AuditRow(
                no=1,
                alan="cta_kaliplari",
                iddia_ozeti="iddia 1",
                kaynak_iddialari=frozenset(
                    {
                        auditors.KaynakIddiasi(kaynak=1, iddia=1),
                        auditors.KaynakIddiasi(kaynak=2, iddia=1),
                    }
                ),
                kaynaklar=frozenset({1, 2}),
                sinif="2-3",
                bayraklar="—",
                oneri="al",
                gerekce="Tek cümle.",
            ),
        ),
        kaynak_profili=(
            auditors.KaynakProfili(kaynak=1, resmi=True, not_metni="Asıl kaynak."),
            auditors.KaynakProfili(kaynak=2, resmi=False, not_metni="Aktaran."),
        ),
        yeniden_dogrulama=envanter,
        url_orneklem=_dogrulanmis_ornekle() if ornekle is None else ornekle,
        unit_snapshot_sha=_aktif_gorunti_sha() if snapshot_sha is None else snapshot_sha,
    )


def _tur(
    *,
    envanter_1: tuple[auditors.InventoryRow, ...] = (),
    envanter_2: tuple[auditors.InventoryRow, ...] = (),
    oneri_sayisi: int = 1,
    ornekle_1: tuple[auditors.UrlCheck, ...] | None = None,
    snapshot_sha: str | None = None,
) -> auditors.AuditRound:
    return auditors.AuditRound(
        reports=(
            _rapor(
                auditors.DENETCI_ROLLERI[0],
                envanter=envanter_1,
                oneri_sayisi=oneri_sayisi,
                ornekle=ornekle_1,
                snapshot_sha=snapshot_sha,
            ),
            _rapor(
                auditors.DENETCI_ROLLERI[1],
                envanter=envanter_2,
                oneri_sayisi=oneri_sayisi,
                snapshot_sha=snapshot_sha,
            ),
        ),
        gecerli=True,
        sebep=None,
    )


# ═══ Sentez çıktısı kurucusu — sözleşmenin KENDİ biçiminden yazıldı ════════


def _sentez_metni(
    aday: dict,
    gunluk: list[dict],
    sorular: list[str],
    ozet: str = "Onay özeti gövdesi.",
) -> str:
    govde = (
        f"1) {OLCULEN_BOLUM_ANAHTARLARI[0]} — şemaya birebir JSON:\n"
        "```json\n"
        f"{json.dumps(aday, ensure_ascii=False)}\n"
        "```\n"
        f"2) {OLCULEN_BOLUM_ANAHTARLARI[1]} — karar günlüğü:\n"
        "```json\n"
        f"{json.dumps(gunluk, ensure_ascii=False)}\n"
        "```\n"
        f"3) {OLCULEN_BOLUM_ANAHTARLARI[2]} — insan kararı gerekenler:\n"
    )
    if sorular:
        govde += "\n".join(f"- {soru}" for soru in sorular) + "\n"
    govde += (
        f"4) {OLCULEN_BOLUM_ANAHTARLARI[3]} — operatör onay ekranı için:\n{ozet}\n"
    )
    return govde


class SahteRunner:
    """Sentez aracının yerine geçen dikiş — çağrıyı ve girdisini kaydeder."""

    def __init__(self, sonuc: auditors.RunnerOutcome) -> None:
        self.sonuc = sonuc
        self.cagrilar: list[tuple[str, Path, Path]] = []
        self.istem_metni: str | None = None

    def run(self, tool: str, cwd: Path, prompt_path: Path) -> auditors.RunnerOutcome:
        self.cagrilar.append((tool, cwd, prompt_path))
        self.istem_metni = prompt_path.read_text(encoding="utf-8")
        return self.sonuc


def _tamam(metin: str) -> auditors.RunnerOutcome:
    return auditors.RunnerOutcome(durum="tamam", stdout=metin, stderr="", exit_code=0)


# ═══ Koşu dikişi ═══════════════════════════════════════════════════════════


@pytest.fixture
async def kosu(db):
    """GERÇEK koşu satırı — `mark_incomplete` gerçekten YAZAR.

    Bağlantı üretimin kendi yapılandırmasından geçer (`_init_connection`):
    yönetici olayı `jsonb` kolona yazılır ve codec'siz bağlantıda düşer.
    """
    await _init_connection(db)
    root_id = await db.fetchval(
        "SELECT id FROM social.sectors WHERE parent_sector_id IS NULL LIMIT 1"
    )
    assert root_id is not None, "kök sektör seed'i eksik"
    sector_id = await db.fetchval(
        "INSERT INTO social.sectors (slug, display_name, parent_sector_id) "
        "VALUES ($1, $2, $3) RETURNING id",
        f"alt-{uuid.uuid4().hex[:8]}",
        "Alt Sektör",
        root_id,
    )
    run_id = runs.new_run_id()
    await runs.open_run(db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")
    return db, run_id


async def _durum(db, run_id: str) -> tuple[str, str | None]:
    kayit = await db.fetchrow(
        "SELECT durum, sebep FROM social.sector_package_runs WHERE run_id = $1",
        run_id,
    )
    return kayit["durum"], kayit["sebep"]


async def _sentez(
    kosu,
    tmp_path: Path,
    *,
    aday: dict,
    gunluk: list[dict],
    sorular: list[str] | None = None,
    tur: auditors.AuditRound | None = None,
    aktif: dict | None = None,
    sonuc: auditors.RunnerOutcome | None = None,
):
    db, run_id = kosu
    runner = SahteRunner(
        sonuc
        if sonuc is not None
        else _tamam(_sentez_metni(aday, gunluk, list(sorular or [])))
    )
    uretilen = await synthesis.run(
        db,
        _tur() if tur is None else tur,
        run_id=run_id,
        active_package=_aktif_paket() if aktif is None else aktif,
        removed_history=(),
        holiday_keys=set(),
        runner=runner,
        dest=tmp_path / "sentez-kokleri",
    )
    return uretilen, runner


def _satirlar(sonuc: synthesis.SynthesisResult) -> dict[str, dict]:
    """`unit_id` → satır. Yola DEĞİL KİMLİĞE anahtarlanır (yol KONUMSALDIR)."""
    return {
        satir["unit_id"]: dict(satir)
        for satir in sonuc.karar_gunlugu
        if satir.get("tur") == "karar"
    }


# ═══ 1. Ölçülmüş sözleşme ══════════════════════════════════════════════════


def test_section_keys_match_pinned_contract() -> None:
    """Başlıklar pinlenmiş sözleşmeden YENİDEN ölçülür — SIRA dâhil."""
    metin = (auditors.ARASTIRMA_DEPOSU_KOKU / synthesis.GOREV_DOSYASI).read_text(
        encoding="utf-8"
    )
    bulunan = tuple(
        m.group(1)
        for m in re.finditer(r"^\d\) ([A-ZÇĞİÖŞÜ_][A-ZÇĞİÖŞÜ_ ]*?) —", metin, re.M)
    )
    assert bulunan == OLCULEN_BOLUM_ANAHTARLARI
    assert synthesis.SENTEZ_BOLUM_ANAHTARLARI == OLCULEN_BOLUM_ANAHTARLARI


def test_suggestion_section_anchor_is_the_measured_heading() -> None:
    """K-75 sayımının okuduğu bölüm ADIYLA çapalanır — konumsal indis kayabilir.

    Üretim `BOLUM_ANAHTARLARI[3]` yazar; demet Task 9'da pinlenmiş denetçi
    sözleşmesine karşı ölçülüyor, ama İNDİS ölçülmüyor. Sözleşmeye bir bölüm
    eklenip sıra kayarsa taşma sayacı sessizce başka bir bölümü sayardı.
    Ölçülen literal: `hakem-denetci-gorevi.md` satır 216.
    """
    assert synthesis.ONERI_BOLUMU == "AÇIK SORU ÖNERİLERİ"


def test_overflow_caps_match_the_two_contracts() -> None:
    """K-74 ve K-75 AYRI sözleşmelerden gelir; tek karara bağlanmaz."""
    assert synthesis.K74_ACIK_SORU_TAVANI == OLCULEN_ACIK_SORU_TAVANI
    assert synthesis.K75_DENETCI_ONERI_TAVANI == OLCULEN_DENETCI_ONERI_TAVANI


# ═══ 2. Kanonik sıra — yapısal kapı ════════════════════════════════════════


DRAFT_YAZICISI = "insert_draft"
"""Paket tablosuna yazan TEK yüzeyin adı — kavramdan yazıldı, koddan değil."""

YASAM_DONGUSU_MODULU = "app.services.sector_package_lifecycle"
YASAM_DONGUSU_ADI = "sector_package_lifecycle"
"""Modülün SON parçası — `from app.services import <ad>` biçimi de ihlaldir."""


def _draft_yazici_referanslari(kaynak: str) -> list[str]:
    """Kaynakta draft yazıcısına yapılan KOD referansları.

    Ham dizge taraması KULLANILMAZ: bu dosyanın kendi adı da o dizgeyi taşır ve
    düz yazı içindeki bir anma ihlal DEĞİLDİR. Ölçülen şey söz dizimidir —
    içe aktarım, ad ve öznitelik düğümleri.
    """
    agac = ast.parse(kaynak)
    bulgular: list[str] = []
    for dugum in ast.walk(agac):
        if isinstance(dugum, ast.ImportFrom):
            if YASAM_DONGUSU_ADI in (dugum.module or ""):
                bulgular.append(f"from {dugum.module}")
            for ad in dugum.names:
                if ad.name in (DRAFT_YAZICISI, YASAM_DONGUSU_ADI):
                    bulgular.append(f"from ... import {ad.name}")
        elif isinstance(dugum, ast.Import):
            for ad in dugum.names:
                if YASAM_DONGUSU_ADI in ad.name:
                    bulgular.append(f"import {ad.name}")
        elif isinstance(dugum, ast.Name) and dugum.id == DRAFT_YAZICISI:
            bulgular.append(f"ad: {dugum.id}")
        elif isinstance(dugum, ast.Attribute) and dugum.attr == DRAFT_YAZICISI:
            bulgular.append(f"öznitelik: .{dugum.attr}")
    return bulgular


def test_synthesis_module_does_not_import_insert_draft() -> None:
    """`sentez → motor → draft` sırası KOD DÜZEYİNDE zorlanır.

    Desen kavramdan türetilir: aranan şey "paket tablosuna yazan yüzeyin adı",
    bulunan örneklerden değil.
    """
    kaynak = (
        REPO_KOK / "apps/social/backend/app/services/sector_pipeline/synthesis.py"
    ).read_text(encoding="utf-8")
    assert _draft_yazici_referanslari(kaynak) == []


@pytest.mark.parametrize(
    "ekilen",
    [
        "from app.services.sector_package_lifecycle import insert_draft\n",
        "from app.services import sector_package_lifecycle\n",
        "import app.services.sector_package_lifecycle\n",
        "def f(db):\n    return db.insert_draft()\n",
        "def f(insert_draft):\n    return insert_draft\n",
    ],
)
def test_draft_writer_scan_detects_a_planted_violation(ekilen: str) -> None:
    """Tarayıcının kendi mutasyon kanıtı: ekilen ihlal GÖRÜLÜR.

    Boş küme kontrol kolu ayrı testtedir (gerçek modül temiz döner); bu kol
    tarayıcının sessizce hiçbir şey görmediği hâli dışlar.
    """
    assert _draft_yazici_referanslari(ekilen) != []


# ═══ 3. Pozitif kontrol ve kimlik taşıması ═════════════════════════════════


async def test_valid_round_produces_four_outputs(kosu, tmp_path) -> None:
    """Geçerli turdan DÖRT çıktı doğar ve taşma işareti temizdir."""
    icerik = _tam_icerik()
    sonuc, runner = await _sentez(
        kosu,
        tmp_path,
        aday=icerik,
        gunluk=_model_gunlugu(icerik),
        sorular=["Kanca sayısı yeterli mi?"],
    )
    assert identity.cozulmus(sonuc.aday_json) == icerik
    assert len(sonuc.karar_gunlugu) == len(identity.enumerate_content_units(icerik))
    assert sonuc.acik_sorular == ("Kanca sayısı yeterli mi?",)
    assert sonuc.onay_ozeti.strip()
    assert sonuc.tasma is False
    assert [cagri[0] for cagri in runner.cagrilar] == [auditors.SENTEZ_ARACI]


async def test_prompt_carries_both_reports_with_tool_identity_masked(
    kosu, tmp_path
) -> None:
    """İki rapor da isteme girer; araç kimliği maskeden GEÇER (K-137 uzantısı).

    Vaat kümenin kendisi kadardır: `auditors.ARAC_KIMLIKLERI` kapalı bir
    kümedir ve dışındaki bir satıcı adı maskelenmez. Ölçülen, kümedeki bir
    adın maskelendiğidir.
    """
    icerik = _tam_icerik()
    _, runner = await _sentez(
        kosu, tmp_path, aday=icerik, gunluk=_model_gunlugu(icerik)
    )
    istem = runner.istem_metni
    assert istem is not None
    for rol in auditors.DENETCI_ROLLERI:
        assert rol in istem
    assert "Claude Code" not in istem
    assert auditors.ARAC_MASKESI in istem


async def test_every_decision_row_carries_path_and_sha(kosu, tmp_path) -> None:
    """Yol ve hash MODELDEN alınmaz, üretilen içerikten TÜRETİLİR."""
    icerik = _tam_icerik()
    sonuc, _ = await _sentez(
        kosu, tmp_path, aday=icerik, gunluk=_model_gunlugu(icerik)
    )
    birimler = identity.enumerate_content_units(identity.cozulmus(sonuc.aday_json))
    for satir in sonuc.karar_gunlugu:
        assert satir["aktor"] == "sentez"
        for alan in ("unit_id", "oge_yolu", "oge_sha"):
            assert satir[alan], f"{alan} boş"
        assert satir["oge_sha"] != BOZUK_SHA, "modelin yazdığı hash KABUL EDİLMİŞ"
        assert satir["oge_sha"] == birimler[satir["oge_yolu"]]["oge_sha"]
        assert satir["alan"] == birimler[satir["oge_yolu"]]["alan"]


async def test_produced_log_passes_check_unit_integrity(kosu, tmp_path) -> None:
    """Üretici ↔ doğrulayıcı uçtan uca: ürettiğimiz çift bütünlük kapısını GEÇER."""
    icerik = _tam_icerik()
    sonuc, _ = await _sentez(
        kosu, tmp_path, aday=icerik, gunluk=_model_gunlugu(icerik)
    )
    assert (
        identity.check_unit_integrity(
            identity.cozulmus(sonuc.aday_json), [dict(s) for s in sonuc.karar_gunlugu]
        )
        == []
    )
    assert synthesis.validate(sonuc) == []


async def test_guncelle_preserves_unit_id(kosu, tmp_path) -> None:
    """`guncelle` kimliği KORUR; hash yeni metinden TAZE üretilir."""
    yeni = KORUNAN_METIN + " — güncellendi"
    icerik = _tam_icerik(kanca_kaliplari=[yeni, CIKARILACAK_METIN])
    gunluk = _model_gunlugu(icerik)
    for satir in gunluk:
        if satir["unit_id"] == UNIT_KORU:
            satir["karar"] = "guncelle"
    sonuc, _ = await _sentez(kosu, tmp_path, aday=icerik, gunluk=gunluk)

    satir = _satirlar(sonuc)[UNIT_KORU]
    assert satir["karar"] == "guncelle"
    assert satir["unit_id"] == UNIT_KORU
    assert satir["oge_sha"] == identity.canonical_sha(yeni)


async def test_ekle_row_carries_the_source_claim_field(kosu, tmp_path) -> None:
    """Sentezin `kaynak_iddia` beyanı motora ULAŞIR — sessizce DÜŞMEZ.

    Alan 2026-09-11'de sözleşmeye eklendi (dış depo `12beec1`) ve `ekle`
    satırında ZORUNLUDUR; motor atfı onunla adaya bağlar. Satır kurucusu
    isteğe bağlı alanları AD AD taşır — listeye yazılmayan alan sessizce
    düşer ve modelin doğru yazdığı her `ekle` kararı üretimde
    `kaynak-iddia-yok` diye reddedilirdi. Kusur KAPIYA değil TAŞIMAYA aittir
    ve yalnız uçtan uca ölçülür.
    """
    yeni_metin = "Kaynak iddiali yeni kalip"
    icerik = _tam_icerik(kanca_kaliplari=[KORUNAN_METIN, yeni_metin])
    gunluk = _model_gunlugu(icerik, atlanan=(UNIT_CIKAR,))
    gunluk = [s for s in gunluk if s["oge_yolu"] != "kanca_kaliplari[1]"]
    gunluk.append(
        _satir("cikar", UNIT_CIKAR, "kanca_kaliplari[1]", "kanca_kaliplari")
    )
    gunluk.append(
        _satir(
            "ekle",
            "ku-999999999999",
            "kanca_kaliplari[1]",
            "kanca_kaliplari",
            yerine_gecer=UNIT_CIKAR,
            kaynak_iddia="K1#3, K2#7",
        )
    )
    tur = _tur(envanter_1=_envanter((UNIT_CIKAR, "contradicted")))
    sonuc, _ = await _sentez(kosu, tmp_path, aday=icerik, gunluk=gunluk, tur=tur)

    ekle = [s for s in _satirlar(sonuc).values() if s["karar"] == "ekle"]
    assert len(ekle) == 1
    assert ekle[0]["kaynak_iddia"] == "K1#3, K2#7"


async def test_cikar_ekle_pair_links_via_yerine_gecer(kosu, tmp_path) -> None:
    """K-86/K-154: `ekle` YENİ kimlik alır, `yerine_gecer` çıkarılana bağlar."""
    yeni_metin = "Yepyeni kalıp metni"
    icerik = _tam_icerik(kanca_kaliplari=[KORUNAN_METIN, yeni_metin])
    gunluk = _model_gunlugu(icerik, atlanan=(UNIT_CIKAR,))
    gunluk = [s for s in gunluk if s["oge_yolu"] != "kanca_kaliplari[1]"]
    gunluk.append(
        _satir("cikar", UNIT_CIKAR, "kanca_kaliplari[1]", "kanca_kaliplari")
    )
    gunluk.append(
        _satir(
            "ekle",
            "ku-999999999999",
            "kanca_kaliplari[1]",
            "kanca_kaliplari",
            yerine_gecer=UNIT_CIKAR,
        )
    )
    tur = _tur(envanter_1=_envanter((UNIT_CIKAR, "contradicted")))
    sonuc, _ = await _sentez(kosu, tmp_path, aday=icerik, gunluk=gunluk, tur=tur)

    satirlar = _satirlar(sonuc)
    assert satirlar[UNIT_CIKAR]["karar"] == "cikar"
    ekle = [s for s in satirlar.values() if s["karar"] == "ekle"]
    assert len(ekle) == 1
    assert ekle[0]["unit_id"] not in {
        UNIT_KORU,
        UNIT_CIKAR,
        UNIT_MEVZUAT,
        "ku-999999999999",
    }
    assert identity.UNIT_ID_RE.match(ekle[0]["unit_id"])
    assert ekle[0]["yerine_gecer"] == UNIT_CIKAR
    assert (
        identity.check_unit_integrity(
            identity.cozulmus(sonuc.aday_json), [dict(s) for s in sonuc.karar_gunlugu]
        )
        == []
    )


# ═══ 4. Çıkarma eşiği — K-124 ve K-122 ═════════════════════════════════════


def _cikarma_gunlugu(icerik: dict, hedef: str, yol: str, alan: str) -> list[dict]:
    """Modelin "bu birimi çıkar" günlüğü — kalan her öğe `koru`."""
    gunluk = _model_gunlugu(icerik, atlanan=(hedef,))
    gunluk.append(_satir("cikar", hedef, yol, alan))
    return gunluk


async def test_cikar_without_evidence_becomes_open_question(kosu, tmp_path) -> None:
    """K-124: pozitif kanıt yoksa çıkarma YAPILMAZ, madde açık soruya DÜŞER.

    Sessiz kayıp yolu kapalıdır: birim içeriğe geri konur ve onu sahiplenen
    `koru` satırı yazılır — yoksa bütünlük kapısı zaten düşerdi.
    """
    icerik = _tam_icerik(kanca_kaliplari=[KORUNAN_METIN])
    gunluk = _cikarma_gunlugu(
        icerik, UNIT_CIKAR, "kanca_kaliplari[1]", "kanca_kaliplari"
    )
    sonuc, _ = await _sentez(kosu, tmp_path, aday=icerik, gunluk=gunluk)

    assert CIKARILACAK_METIN in identity.cozulmus(sonuc.aday_json)["kanca_kaliplari"]
    assert _satirlar(sonuc)[UNIT_CIKAR]["karar"] == "koru"
    assert any(UNIT_CIKAR in soru for soru in sonuc.acik_sorular)
    assert (
        identity.check_unit_integrity(
            identity.cozulmus(sonuc.aday_json), [dict(s) for s in sonuc.karar_gunlugu]
        )
        == []
    )


async def test_cikar_with_positive_evidence_is_admitted(kosu, tmp_path) -> None:
    """Pozitif kontrol: tek denetçinin `contradicted` satırı normal bilgide YETER."""
    icerik = _tam_icerik(kanca_kaliplari=[KORUNAN_METIN])
    gunluk = _cikarma_gunlugu(
        icerik, UNIT_CIKAR, "kanca_kaliplari[1]", "kanca_kaliplari"
    )
    tur = _tur(envanter_1=_envanter((UNIT_CIKAR, "contradicted")))
    sonuc, _ = await _sentez(kosu, tmp_path, aday=icerik, gunluk=gunluk, tur=tur)

    assert CIKARILACAK_METIN not in identity.cozulmus(sonuc.aday_json)["kanca_kaliplari"]
    assert _satirlar(sonuc)[UNIT_CIKAR]["karar"] == "cikar"
    assert sonuc.acik_sorular == ()


async def test_cikar_of_legislation_requires_both_auditors(kosu, tmp_path) -> None:
    """K-124 mevzuat kolu: TEK denetçinin çelişki satırı YETMEZ."""
    icerik = _tam_icerik(yasaklar_ve_hassasiyetler=["Yeni mevzuat kalıbı"])
    gunluk = _model_gunlugu(icerik, atlanan=(UNIT_MEVZUAT,))
    gunluk = [s for s in gunluk if s["oge_yolu"] != "yasaklar_ve_hassasiyetler[0]"]
    gunluk.append(
        _satir(
            "cikar",
            UNIT_MEVZUAT,
            "yasaklar_ve_hassasiyetler[0]",
            "yasaklar_ve_hassasiyetler",
        )
    )
    gunluk.append(
        _satir(
            "ekle",
            "ku-888888888888",
            "yasaklar_ve_hassasiyetler[0]",
            "yasaklar_ve_hassasiyetler",
            yerine_gecer=UNIT_MEVZUAT,
        )
    )
    tek = _tur(envanter_1=_envanter((UNIT_MEVZUAT, "contradicted")))
    sonuc, _ = await _sentez(kosu, tmp_path, aday=icerik, gunluk=gunluk, tur=tek)

    assert MEVZUAT_METNI in identity.cozulmus(sonuc.aday_json)["yasaklar_ve_hassasiyetler"]
    assert _satirlar(sonuc)[UNIT_MEVZUAT]["karar"] == "koru"
    assert any(UNIT_MEVZUAT in soru for soru in sonuc.acik_sorular)


async def test_cikar_of_legislation_passes_with_both_auditors(kosu, tmp_path) -> None:
    """Pozitif kontrol: iki denetçi de çelişki gösterirse mevzuat birimi ÇIKAR."""
    icerik = _tam_icerik(yasaklar_ve_hassasiyetler=["Yeni mevzuat kalıbı"])
    gunluk = _model_gunlugu(icerik, atlanan=(UNIT_MEVZUAT,))
    gunluk = [s for s in gunluk if s["oge_yolu"] != "yasaklar_ve_hassasiyetler[0]"]
    gunluk.append(
        _satir(
            "cikar",
            UNIT_MEVZUAT,
            "yasaklar_ve_hassasiyetler[0]",
            "yasaklar_ve_hassasiyetler",
        )
    )
    gunluk.append(
        _satir(
            "ekle",
            "ku-888888888888",
            "yasaklar_ve_hassasiyetler[0]",
            "yasaklar_ve_hassasiyetler",
            yerine_gecer=UNIT_MEVZUAT,
        )
    )
    iki = _tur(
        envanter_1=_envanter((UNIT_MEVZUAT, "contradicted")),
        envanter_2=_envanter((UNIT_MEVZUAT, "contradicted")),
    )
    sonuc, _ = await _sentez(kosu, tmp_path, aday=icerik, gunluk=gunluk, tur=iki)

    assert MEVZUAT_METNI not in identity.cozulmus(sonuc.aday_json)["yasaklar_ve_hassasiyetler"]
    assert _satirlar(sonuc)[UNIT_MEVZUAT]["karar"] == "cikar"


async def test_churn_guard_blocks_weak_new_over_verified(kosu, tmp_path) -> None:
    """K-122: bir denetçi `supported` diyorsa doğrulanmış kalıp KALIR.

    Karşı taraftaki `contradicted` satırı tek başına yetmez — iki denetçinin
    ayrıştığı yer çıkarma değil AÇIK SORU yeridir.
    """
    icerik = _tam_icerik(kanca_kaliplari=[KORUNAN_METIN, "Yepyeni zayıf kalıp"])
    gunluk = _model_gunlugu(icerik, atlanan=(UNIT_CIKAR,))
    gunluk = [s for s in gunluk if s["oge_yolu"] != "kanca_kaliplari[1]"]
    gunluk.append(
        _satir("cikar", UNIT_CIKAR, "kanca_kaliplari[1]", "kanca_kaliplari")
    )
    gunluk.append(
        _satir(
            "ekle",
            "ku-777777777777",
            "kanca_kaliplari[1]",
            "kanca_kaliplari",
            yerine_gecer=UNIT_CIKAR,
        )
    )
    tur = _tur(
        envanter_1=_envanter((UNIT_CIKAR, "contradicted")),
        envanter_2=_envanter((UNIT_CIKAR, "supported")),
    )
    sonuc, _ = await _sentez(kosu, tmp_path, aday=icerik, gunluk=gunluk, tur=tur)

    assert CIKARILACAK_METIN in identity.cozulmus(sonuc.aday_json)["kanca_kaliplari"]
    assert _satirlar(sonuc)[UNIT_CIKAR]["karar"] == "koru"
    assert any(UNIT_CIKAR in soru for soru in sonuc.acik_sorular)


async def test_rejected_removal_unlinks_its_replacement(kosu, tmp_path) -> None:
    """Ret hâlinde `yerine_gecer` bağı ÇÖZÜLÜR — aday düşürülmez, bağ yalan söylemez."""
    icerik = _tam_icerik(kanca_kaliplari=[KORUNAN_METIN, "Yepyeni zayıf kalıp"])
    gunluk = [s for s in _model_gunlugu(icerik, atlanan=(UNIT_CIKAR,))
              if s["oge_yolu"] != "kanca_kaliplari[1]"]
    gunluk.append(
        _satir("cikar", UNIT_CIKAR, "kanca_kaliplari[1]", "kanca_kaliplari")
    )
    gunluk.append(
        _satir(
            "ekle",
            "ku-777777777777",
            "kanca_kaliplari[1]",
            "kanca_kaliplari",
            yerine_gecer=UNIT_CIKAR,
        )
    )
    sonuc, _ = await _sentez(kosu, tmp_path, aday=icerik, gunluk=gunluk)

    ekle = [s for s in _satirlar(sonuc).values() if s["karar"] == "ekle"]
    assert len(ekle) == 1
    assert "yerine_gecer" not in ekle[0]
    assert _satirlar(sonuc)[UNIT_CIKAR]["karar"] == "koru"


async def test_not_observed_alone_does_not_license_removal(kosu, tmp_path) -> None:
    """`not_observed` GEÇERSİZLİK KANITI DEĞİLDİR (denetçi sözleşmesi satır 179)."""
    icerik = _tam_icerik(kanca_kaliplari=[KORUNAN_METIN])
    gunluk = _cikarma_gunlugu(
        icerik, UNIT_CIKAR, "kanca_kaliplari[1]", "kanca_kaliplari"
    )
    tur = _tur(
        envanter_1=_envanter((UNIT_CIKAR, "not_observed")),
        envanter_2=_envanter((UNIT_CIKAR, "not_observed")),
    )
    sonuc, _ = await _sentez(kosu, tmp_path, aday=icerik, gunluk=gunluk, tur=tur)

    assert CIKARILACAK_METIN in identity.cozulmus(sonuc.aday_json)["kanca_kaliplari"]
    assert _satirlar(sonuc)[UNIT_CIKAR]["karar"] == "koru"


# ═══ 5. Taşma — K-74 / K-75 ════════════════════════════════════════════════


async def test_overflow_marks_flag_without_truncating(kosu, tmp_path) -> None:
    """Tavanı aşan açık soru DÜŞÜRÜLMEZ; yalnız `tasma` işaretlenir."""
    sorular = [f"Açık soru {sira}" for sira in range(OLCULEN_ACIK_SORU_TAVANI + 2)]
    icerik = _tam_icerik()
    sonuc, _ = await _sentez(
        kosu, tmp_path, aday=icerik, gunluk=_model_gunlugu(icerik), sorular=sorular
    )
    assert sonuc.tasma is True
    assert len(sonuc.acik_sorular) == len(sorular)
    assert sonuc.acik_sorular == tuple(sorular)


async def test_auditor_suggestion_overflow_also_marks_the_flag(kosu, tmp_path) -> None:
    """K-75 AYRI koldur: sentez hiç açık soru yazmasa da denetçi taşması işaretlenir."""
    icerik = _tam_icerik()
    tur = _tur(oneri_sayisi=OLCULEN_DENETCI_ONERI_TAVANI + 1)
    sonuc, _ = await _sentez(
        kosu, tmp_path, aday=icerik, gunluk=_model_gunlugu(icerik), tur=tur
    )
    assert sonuc.acik_sorular == ()
    assert sonuc.tasma is True


async def test_counts_at_the_cap_do_not_overflow(kosu, tmp_path) -> None:
    """Sınır dâhil: tam tavanda taşma YOKTUR (kapalı aralık kontrolü)."""
    sorular = [f"Açık soru {sira}" for sira in range(OLCULEN_ACIK_SORU_TAVANI)]
    icerik = _tam_icerik()
    tur = _tur(oneri_sayisi=OLCULEN_DENETCI_ONERI_TAVANI)
    sonuc, _ = await _sentez(
        kosu,
        tmp_path,
        aday=icerik,
        gunluk=_model_gunlugu(icerik),
        sorular=sorular,
        tur=tur,
    )
    assert sonuc.tasma is False


# ═══ 6. Çıktı doğrulayıcı — `validate` ═════════════════════════════════════


def _sonuc(aday: dict, gunluk: list[dict] | None = None) -> synthesis.SynthesisResult:
    return synthesis.SynthesisResult(
        aday_json=aday,
        karar_gunlugu=tuple(gunluk or []),
        acik_sorular=(),
        onay_ozeti="Özet.",
        tasma=False,
    )


@pytest.mark.parametrize(
    "video, etiket",
    [
        ({"hareket": "tek cümle", "sahne": ["tezgâh üstü"]}, "hareket dize"),
        ({"hareket": ["yavaş kaydırma"], "sahne": "tek cümle"}, "sahne dize"),
        ({"hareket": ["yavaş kaydırma"]}, "sahne havuzu yok"),
        ({"sahne": ["tezgâh üstü"]}, "hareket havuzu yok"),
    ],
)
def test_video_pools_are_two_lists(video, etiket) -> None:
    """K-02/K-113: İKİ havuz, ikisi de LİSTE.

    Kural KOPYALANMAZ — Plan 1 yazım kapısı yeniden kullanılır. Bu test
    `validate`'in o kapıyı gerçekten çağırdığını ölçer: çağrı düşerse KIRMIZI.
    """
    hatalar = synthesis.validate(_sonuc(_tam_icerik(video_kodlar=video)))
    assert any("video_kodlar" in hata for hata in hatalar), etiket


def test_validate_accepts_the_two_pool_shape() -> None:
    """Boş küme kontrol kolu: doğru şekil video_kodlar hatası ÜRETMEZ."""
    icerik = _tam_icerik()
    birimler = identity.enumerate_content_units(icerik)
    kimlikler = _yol_kimlik(icerik)
    gunluk = [
        {
            "tur": "karar",
            "alan": birimler[yol]["alan"],
            "oge_yolu": yol,
            "unit_id": kimlikler[yol],
            "oge_sha": birimler[yol]["oge_sha"],
            "karar": "koru",
            "gerekce": "Taşındı.",
            "kanit": "",
            "aktor": "sentez",
        }
        for yol in sorted(birimler)
    ]
    assert synthesis.validate(_sonuc(icerik, gunluk)) == []


def test_validate_rejects_a_row_written_by_another_actor() -> None:
    """Sentezin günlüğündeki her satırın aktörü `sentez`tir."""
    icerik = _tam_icerik()
    birimler = identity.enumerate_content_units(icerik)
    kimlikler = _yol_kimlik(icerik)
    gunluk = [
        {
            "tur": "karar",
            "alan": birimler[yol]["alan"],
            "oge_yolu": yol,
            "unit_id": kimlikler[yol],
            "oge_sha": birimler[yol]["oge_sha"],
            "karar": "koru",
            "gerekce": "Taşındı.",
            "kanit": "",
            "aktor": "sentez",
        }
        for yol in sorted(birimler)
    ]
    gunluk[0] = dict(gunluk[0], aktor="insan")
    hatalar = synthesis.validate(_sonuc(icerik, gunluk))
    assert any("aktor" in hata for hata in hatalar)


def test_result_collections_are_frozen() -> None:
    """R6(e): geçerlilik taşıyan koleksiyon yapımdan SONRA değiştirilemez."""
    icerik = _tam_icerik()
    sonuc = _sonuc(icerik)
    assert isinstance(sonuc.karar_gunlugu, tuple)
    assert isinstance(sonuc.acik_sorular, tuple)
    with pytest.raises(TypeError):
        sonuc.aday_json["kapsam"] = "değişti"  # type: ignore[index]


def test_result_does_not_alias_the_caller_content() -> None:
    """Çağıranın sözlüğü yapımdan sonra sonucun içini DEĞİŞTİREMEZ."""
    icerik = _tam_icerik()
    sonuc = _sonuc(icerik)
    icerik["kanca_kaliplari"].append("sonradan eklendi")
    assert "sonradan eklendi" not in identity.cozulmus(sonuc.aday_json)["kanca_kaliplari"]


# ═══ 7. Terminal arızalar — K-82 durum sahipliği ═══════════════════════════


@pytest.mark.parametrize(
    "sonuc, etiket",
    [
        (
            auditors.RunnerOutcome(
                durum="zaman-asimi", stdout="", stderr="", exit_code=None
            ),
            "zaman aşımı",
        ),
        (
            auditors.RunnerOutcome(
                durum="hata", stdout="", stderr="araç düştü", exit_code=1
            ),
            "araç arızası",
        ),
    ],
)
async def test_synthesis_timeout_marks_incomplete(
    kosu, tmp_path, sonuc, etiket
) -> None:
    """Sentezin de durum sahibi VARDIR — runner `tamamlanmadi` atamaz."""
    db, run_id = kosu
    icerik = _tam_icerik()
    with pytest.raises(synthesis.SynthesisFailed):
        await _sentez(
            kosu,
            tmp_path,
            aday=icerik,
            gunluk=_model_gunlugu(icerik),
            sonuc=sonuc,
        )
    durum, sebep = await _durum(db, run_id)
    assert durum == "tamamlanmadi", etiket
    assert sebep


async def test_unparseable_output_marks_incomplete(kosu, tmp_path) -> None:
    """Biçim kapısı: dört bölümü taşımayan çıktı SONUÇ DEĞİLDİR."""
    db, run_id = kosu
    with pytest.raises(synthesis.SynthesisFailed):
        await _sentez(
            kosu,
            tmp_path,
            aday=_tam_icerik(),
            gunluk=[],
            sonuc=_tamam("serbest metin rapor, bölüm yok"),
        )
    assert (await _durum(db, run_id))[0] == "tamamlanmadi"


async def test_candidate_failing_the_writing_gate_marks_incomplete(
    kosu, tmp_path
) -> None:
    """Şemayı geçmeyen aday motora ULAŞMAZ."""
    db, run_id = kosu
    bozuk = _tam_icerik()
    bozuk.pop("kapsam")
    with pytest.raises(synthesis.SynthesisFailed):
        await _sentez(kosu, tmp_path, aday=bozuk, gunluk=_model_gunlugu(bozuk))
    assert (await _durum(db, run_id))[0] == "tamamlanmadi"


async def test_invalid_round_blocks_synthesis(kosu, tmp_path) -> None:
    """K-150: geçersiz tur sentezi HİÇ başlatmaz — araç koşmaz, satır bozulmaz."""
    db, run_id = kosu
    runner = SahteRunner(_tamam("kullanılmayacak"))
    gecersiz = auditors.AuditRound(
        reports=(), gecerli=False, sebep="tek denetçi rapor üretti"
    )
    with pytest.raises(synthesis.SynthesisFailed):
        await synthesis.run(
            db,
            gecersiz,
            run_id=run_id,
            active_package=_aktif_paket(),
            removed_history=(),
            holiday_keys=set(),
            runner=runner,
            dest=tmp_path / "sentez-kokleri",
        )
    assert runner.cagrilar == []
    assert (await _durum(db, run_id)) == ("calisiyor", None)


async def test_existing_run_directory_refuses_the_round(kosu, tmp_path) -> None:
    """Aynı koşu kimliği için ikinci sentez kökü AÇILMAZ (salt-ekleme)."""
    db, run_id = kosu
    (tmp_path / "sentez-kokleri" / run_id).mkdir(parents=True)
    icerik = _tam_icerik()
    with pytest.raises(synthesis.SynthesisFailed):
        await _sentez(kosu, tmp_path, aday=icerik, gunluk=_model_gunlugu(icerik))
    assert (await _durum(db, run_id))[0] == "tamamlanmadi"


async def test_relative_dest_is_refused(kosu, tmp_path) -> None:
    """Göreli kök çalışma dizinine göre kayar — kapı dosya yaratmadan ÖNCE koşar."""
    db, run_id = kosu
    icerik = _tam_icerik()
    runner = SahteRunner(_tamam(_sentez_metni(icerik, _model_gunlugu(icerik), [])))
    with pytest.raises(synthesis.SynthesisFailed):
        await synthesis.run(
            db,
            _tur(),
            run_id=run_id,
            active_package=_aktif_paket(),
            removed_history=(),
            holiday_keys=set(),
            runner=runner,
            dest=Path("goreli/kok"),
        )
    assert runner.cagrilar == []


# ═══ 8. Checkpoint 8 düzeltmelerinin kapıları ══════════════════════════════


@pytest.mark.parametrize(
    "bozuk_id, etiket",
    [
        ("/tmp/kacak", "mutlak yol"),
        ("alt/dizin", "yol ayracı"),
        ("../ust", "üst dizin"),
        ("", "boş"),
        (".gizli", "nokta ile başlayan"),
    ],
)
async def test_run_id_grammar_gates_the_destination(
    kosu, tmp_path, bozuk_id, etiket
) -> None:
    """Koşu kimliği kardeş yüzeyin GRAMERİNDEN geçer — `dest` sessizce düşmez.

    Ölçüldü: `Path('/tmp/dest') / '/tmp/kacak'` -> `/tmp/kacak`. Gramer
    olmasaydı mutlak bir kimlik hedef kökü tamamen atlardı ve dosyalar
    çağıranın seçmediği bir yere düşerdi.
    """
    db, _ = kosu
    icerik = _tam_icerik()
    runner = SahteRunner(_tamam(_sentez_metni(icerik, _model_gunlugu(icerik), [])))
    with pytest.raises(synthesis.SynthesisFailed):
        await synthesis.run(
            db,
            _tur(),
            run_id=bozuk_id,
            active_package=_aktif_paket(),
            removed_history=(),
            holiday_keys=set(),
            runner=runner,
            dest=tmp_path / "sentez-kokleri",
        )
    assert runner.cagrilar == [], etiket
    assert not (tmp_path / "sentez-kokleri").exists()


async def test_valid_run_id_is_accepted(kosu, tmp_path) -> None:
    """Boş küme kontrol kolu: geçerli kimlik gramerde TAKILMAZ."""
    icerik = _tam_icerik()
    sonuc, runner = await _sentez(
        kosu, tmp_path, aday=icerik, gunluk=_model_gunlugu(icerik)
    )
    assert runner.cagrilar
    assert sonuc.onay_ozeti.strip()


async def test_round_from_another_snapshot_is_refused(kosu, tmp_path) -> None:
    """Tur ile aktif paket AYNI görüntüye bakmak ZORUNDA — kanıt sürüm bağlıdır."""
    db, run_id = kosu
    icerik = _tam_icerik()
    runner = SahteRunner(_tamam(_sentez_metni(icerik, _model_gunlugu(icerik), [])))
    with pytest.raises(synthesis.SynthesisFailed):
        await synthesis.run(
            db,
            _tur(snapshot_sha="b" * 64),
            run_id=run_id,
            active_package=_aktif_paket(),
            removed_history=(),
            holiday_keys=set(),
            runner=runner,
            dest=tmp_path / "sentez-kokleri",
        )
    assert runner.cagrilar == []
    assert (await _durum(db, run_id))[0] == "tamamlanmadi"


async def test_contradicted_without_resolvable_evidence_is_refused(
    kosu, tmp_path
) -> None:
    """K-124: `contradicted` DEMEK yetmez — `kanit` doğrulanmış referansa ÇÖZÜLMELİ.

    Sözleşme bu statüde *"doğrulanmış bir referans"* şart koşar (denetçi
    sözleşmesi satır 185-186). `D1#999` sözleşmede geçerli bir BİÇİMDİR ama bu
    katmanda çözülemez; kapı fail-closed davranır ve madde açık soruya düşer.
    """
    icerik = _tam_icerik(kanca_kaliplari=[KORUNAN_METIN])
    gunluk = _cikarma_gunlugu(
        icerik, UNIT_CIKAR, "kanca_kaliplari[1]", "kanca_kaliplari"
    )
    tur = _tur(
        envanter_1=_envanter((UNIT_CIKAR, "contradicted"), kanit=COZULEMEYEN_KANIT)
    )
    sonuc, _ = await _sentez(kosu, tmp_path, aday=icerik, gunluk=gunluk, tur=tur)

    assert CIKARILACAK_METIN in identity.cozulmus(sonuc.aday_json)["kanca_kaliplari"]
    assert _satirlar(sonuc)[UNIT_CIKAR]["karar"] == "koru"
    assert any("ÇÖZÜLMEDİ" in soru for soru in sonuc.acik_sorular)


async def test_unverified_url_sample_does_not_resolve_evidence(kosu, tmp_path) -> None:
    """Örneklem satırı DOĞRULANDI değilse referans kümesine GİRMEZ."""
    icerik = _tam_icerik(kanca_kaliplari=[KORUNAN_METIN])
    gunluk = _cikarma_gunlugu(
        icerik, UNIT_CIKAR, "kanca_kaliplari[1]", "kanca_kaliplari"
    )
    acilmayan = (
        auditors.UrlCheck(
            url=DOGRULANMIS_URL,
            kaynak=DOGRULANMIS_KAYNAK,
            erisildi=False,
            icerik_uyumlu=False,
            not_metni="URL AÇILMADI",
        ),
    )
    tur = _tur(envanter_1=_envanter((UNIT_CIKAR, "contradicted")), ornekle_1=acilmayan)
    sonuc, _ = await _sentez(kosu, tmp_path, aday=icerik, gunluk=gunluk, tur=tur)

    assert CIKARILACAK_METIN in identity.cozulmus(sonuc.aday_json)["kanca_kaliplari"]
    assert _satirlar(sonuc)[UNIT_CIKAR]["karar"] == "koru"


async def test_kirp_of_a_verified_unit_is_refused(kosu, tmp_path) -> None:
    """K-122 karar ETİKETİNE değil, birimin adaydan DÜŞMESİNE bağlıdır.

    Sözleşme churn korumasını *"kırpmanın ve `cikar` kararının SONUCUNA konan
    bir kısıt"* diye yazar. Etikete bağlanmış bir kapı `kirp` yazılarak
    aşılırdı ve ölü kararlar bütünlük kapısına görünmediği için kayıp sessiz
    olurdu.
    """
    icerik = _tam_icerik(kanca_kaliplari=[KORUNAN_METIN])
    gunluk = _model_gunlugu(icerik, atlanan=(UNIT_CIKAR,))
    gunluk.append(_satir("kirp", UNIT_CIKAR, "kanca_kaliplari[1]", "kanca_kaliplari"))
    tur = _tur(envanter_2=_envanter((UNIT_CIKAR, "supported")))
    sonuc, _ = await _sentez(kosu, tmp_path, aday=icerik, gunluk=gunluk, tur=tur)

    assert CIKARILACAK_METIN in identity.cozulmus(sonuc.aday_json)["kanca_kaliplari"]
    assert _satirlar(sonuc)[UNIT_CIKAR]["karar"] == "koru"
    assert any("K-122" in soru for soru in sonuc.acik_sorular)


async def test_kirp_without_positive_evidence_is_admitted(kosu, tmp_path) -> None:
    """`kirp` bir BOYUT kararıdır: K-124 kanıt eşiği ona UYGULANMAZ.

    Bu kolun ayrı olması bilinçlidir — kanıt eşiği kırpmaya da konsaydı
    sözleşmede olmayan bir kural yazılmış olurdu (spec §8.6 kırpma sırası).
    """
    icerik = _tam_icerik(kanca_kaliplari=[KORUNAN_METIN])
    gunluk = _model_gunlugu(icerik, atlanan=(UNIT_CIKAR,))
    gunluk.append(_satir("kirp", UNIT_CIKAR, "kanca_kaliplari[1]", "kanca_kaliplari"))
    sonuc, _ = await _sentez(kosu, tmp_path, aday=icerik, gunluk=gunluk)

    assert CIKARILACAK_METIN not in identity.cozulmus(sonuc.aday_json)["kanca_kaliplari"]
    assert _satirlar(sonuc)[UNIT_CIKAR]["karar"] == "kirp"


async def test_rejected_removal_of_a_still_present_unit_is_a_noop(
    kosu, tmp_path
) -> None:
    """Birim hâlâ yerindeyse geri koyma NO-OP'tur — liste ŞİŞMEZ.

    Model çıkarmayı günlükte önerip içerikten hiç düşürmemiş olabilir. Körü
    körüne ekleme yapılsaydı aynı metin iki kez listeye girer ve iki farklı yol
    tek kimliği paylaşırdı.
    """
    icerik = _tam_icerik()
    gunluk = _model_gunlugu(icerik, atlanan=(UNIT_CIKAR,))
    gunluk.append(_satir("cikar", UNIT_CIKAR, "kanca_kaliplari[1]", "kanca_kaliplari"))
    sonuc, _ = await _sentez(kosu, tmp_path, aday=icerik, gunluk=gunluk)

    kanca = identity.cozulmus(sonuc.aday_json)["kanca_kaliplari"]
    assert kanca == [KORUNAN_METIN, CIKARILACAK_METIN]
    assert _satirlar(sonuc)[UNIT_CIKAR]["karar"] == "koru"
    assert (
        identity.check_unit_integrity(
            identity.cozulmus(sonuc.aday_json),
            [dict(s) for s in sonuc.karar_gunlugu],
        )
        == []
    )


def test_result_content_is_deeply_frozen() -> None:
    """R6(e): iç içe koleksiyon da DONAR — doğrulanmış çift sonradan bozulamaz."""
    sonuc = _sonuc(_tam_icerik())
    assert isinstance(sonuc.aday_json["kanca_kaliplari"], tuple)
    assert isinstance(sonuc.aday_json["video_kodlar"]["hareket"], tuple)
    with pytest.raises(AttributeError):
        sonuc.aday_json["kanca_kaliplari"].append("sonradan")  # type: ignore[union-attr]
    with pytest.raises(TypeError):
        sonuc.aday_json["video_kodlar"]["hareket"] = ()  # type: ignore[index]


def test_thawed_content_passes_the_writing_gate() -> None:
    """Çözme, şema sınırında GERÇEKTEN çalışır — donmuş biçim şemayı geçemezdi."""
    from app.services.sector_content_schema import structural_errors

    sonuc = _sonuc(_tam_icerik())
    assert structural_errors(identity.cozulmus(sonuc.aday_json)) == []
    assert structural_errors(dict(sonuc.aday_json)) != []
