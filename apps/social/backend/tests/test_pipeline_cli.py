"""Operatör komut ailesinin sözleşme testleri (plan Task 16).

Dört iddia ailesi ölçülür:

1. **Sözleşme pini** — resmî koşu başlatan HER alt komut, sürüklenmiş pinde
   koşuya BAŞLAMAZ. Kapı tek tek elle seçilmiş örnekle değil, alt komut
   kümesinden ÜRETİLMİŞ matrisle kapatılır; boş-küme kontrol kolu vardır.
2. **`sector_sweep.py` deseni** — açık `--database-url` (ortamdan miras YOK) ·
   deterministik çıktı · anlamlı çıkış kodu.
3. **Servis yüzeyine bağlılık** — komut ailesi iş mantığı TAŞIMAZ; her alt
   komut adı konmuş servis fonksiyonunu çağırır (arayüz eki R10/R11).
4. **K-145 olay zinciri + AÇIK-1/AÇIK-2** — olay planı yazımı, üyelik
   değişikliği, onay damgası, paket paket yürütme ve `geri-al`'ın üç zorunlu
   argümanı.

Ayrıca K-26 vade bildirimi ve K-45 geri-dönüş bandının **müşteri yüzeyi**
burada ölçülür: `recovered` durumu maruziyet kanıtı olmadan ÜRETİLMEZ.
"""

from __future__ import annotations

import dataclasses
import json
import sys
import uuid
from pathlib import Path

import pytest
from fastapi import HTTPException

BACKEND_KOKU = Path(__file__).resolve().parents[1]
if str(BACKEND_KOKU / "scripts") not in sys.path:
    sys.path.insert(0, str(BACKEND_KOKU / "scripts"))

import sector_pipeline_cli as cli  # noqa: E402

from app.routers import brands as brands_router  # noqa: E402
from app.services import notifications  # noqa: E402
from app.services.sector_pipeline import runs  # noqa: E402

from .test_notifications import _seed_owner_and_brand, _seed_sub_sector  # noqa: E402
from .test_pipeline_runs import (  # noqa: E402
    ACTOR,
    CONFIG_SHA,
    KURAL,
    KURAL_V1,
    KURAL_V2,
    MOTOR_SURUM,
    _bos_evren,
    _geri_alinabilir,
    _kokenli_paket,
    _onayli_olay,
    _sub_sector,
    pkg_db,  # noqa: F401 — fixture yeniden dışa vurulur
)

SAHTE_URL = "postgresql://kullanici:parola@127.0.0.1:5432/otomaix_test"
"""Ayrıştırıcı testlerinde kullanılan uç — hiçbir teste GERÇEK bağlantı açtırmaz."""


def _args(*argv: str):
    """Alt komut argümanlarını ayrıştırır; bağlantı dizesi AÇIKÇA verilir."""
    return cli.build_parser().parse_args(["--database-url-env", "OTOMAIX_TEST_DSN", *argv])


def _dortlu() -> list[str]:
    """K-145 kural sürümünü adlandıran dörtlü — testlerde tek kaynak."""
    return [
        "--engine-version",
        MOTOR_SURUM,
        "--engine-config-sha",
        CONFIG_SHA,
        "--kural-kimligi",
        KURAL,
        "--kural-surumu",
        KURAL_V1,
    ]


def _asgari_argumanlar(komut: str) -> list[str]:
    """Bir alt komutun ZORUNLU argümanlarını ayrıştırıcıdan TÜRETİR.

    Elle yazılmış bir tablo, yeni bir zorunlu argüman eklendiği gün sessizce
    bayatlardı ve pin matrisi o komutu ayrıştırma hatasında kaybederdi —
    yani kapı YEŞİL kalırken hiçbir şey ölçmezdi.
    """
    alt = cli.build_parser()._subparsers._group_actions[0].choices[komut]
    argv: list[str] = []
    for eylem in alt._actions:
        if not eylem.option_strings or not eylem.required:
            continue
        bayrak = eylem.option_strings[-1]
        if eylem.choices:
            deger = sorted(eylem.choices)[0]
        elif eylem.type is cli._uuid:
            deger = str(uuid.uuid4())
        elif eylem.type in (int, float):
            deger = "1"
        elif bayrak == "--engine-config-sha":
            deger = CONFIG_SHA
        else:
            deger = "x"
        argv += [bayrak, deger]
    return argv


# ─── 1. Sözleşme pini — ÜRETİLMİŞ matris ────────────────────────────────────


@pytest.fixture
def surukklenmis_pin(tmp_path, monkeypatch):
    """Pini bozar: manifest gerçek dosyayı YANLIŞ hash ile adlandırır."""
    ham = json.loads(Path(cli.PIN_PATH).read_text(encoding="utf-8"))
    # Bozma SESSİZCE başarısız olamaz: anahtar adı değişirse fixture hiçbir şey
    # bozmaz ve matris "kapı çalışıyor" diye yeşil kalırdı.
    assert isinstance(ham.get("files"), dict) and ham["files"], (
        "pin manifestinde `files` yok — bozma adımı hiçbir şey değiştirmezdi"
    )
    ham["files"] = {ad: "0" * 64 for ad in ham["files"]}
    bozuk = tmp_path / "bozuk-pin.json"
    bozuk.write_text(json.dumps(ham), encoding="utf-8")
    monkeypatch.setattr(cli, "PIN_PATH", bozuk)
    return bozuk


def test_every_run_subcommand_requires_pin(surukklenmis_pin, monkeypatch):
    """Resmî koşu başlatan HER alt komut sürüklenmiş pinde rc≠0 döner.

    Küme `cli.RUN_SUBCOMMANDS`'tan ÜRETİLİR: yarın eklenen bir alt komut
    kapının kapsamına kendiliğinden girer, elle bir listeye eklenmesi
    beklenmez.

    Bağlantı SAHTE: kapı bağlantıdan ÖNCE koşmak zorunda olduğu için hiçbir
    alt komut veritabanına ulaşamamalıdır. `asyncpg.connect` bu testte
    çağrılırsa kapı sırası bozulmuş demektir ve test PATLAR.
    """
    assert cli.RUN_SUBCOMMANDS, "boş küme — matris hiçbir şey ölçmezdi"

    async def _asla(*a, **k):  # pragma: no cover — çağrılırsa test zaten düşer
        raise AssertionError("pin kapısından ÖNCE bağlantı açıldı")

    monkeypatch.setattr(cli.asyncpg, "connect", _asla)

    for komut in sorted(cli.RUN_SUBCOMMANDS):
        rc = cli.main(
            ["--database-url-env", "OTOMAIX_TEST_DSN", komut, *_asgari_argumanlar(komut)]
        )
        assert rc != 0, f"{komut}: sürüklenmiş pinde koşu başladı (rc={rc})"
        assert rc == cli.RC_USAGE, f"{komut}: beklenen çıkış kodu {cli.RC_USAGE}, {rc}"


def test_pin_clean_allows_run():
    """POZİTİF KONTROL — temiz pinde kapı geçirir.

    Bu test olmadan yukarıdaki matris boş bir iddia olurdu: her koşulda
    fırlatan bir kapı da matrisi yeşil gösterirdi.
    """
    cli.require_contract_pin()


def test_read_only_subcommands_are_outside_the_pin_gate():
    """Salt-okunur iki alt komut koşu BAŞLATMAZ — kapı kümesinin dışındadır."""
    tum = set(cli.build_parser()._subparsers._group_actions[0].choices)
    assert tum - cli.RUN_SUBCOMMANDS == {"durum", "etki-analizi"}


# ─── 2. sector_sweep deseni ─────────────────────────────────────────────────


def test_database_url_not_inherited_from_env(monkeypatch, capsys):
    """`DATABASE_URL` ortamda DOLU olsa bile komut onu OKUMAZ.

    `sector_sweep.py` deseninin sebebi ölçülmüş bir risktir: ortamdan miras
    alınan bir dize, operatörü farkında olmadan YANLIŞ veritabanına koşturur.

    **Ölçüm KATMANI değişti, iddia DEĞİŞMEDİ (2026-09-12, S-3):** zorunluluk
    artık `required=True` bayrağında değil, kanal çözümündedir — çünkü değerin
    kendisi argv'den çıkarıldı. Kanal seçilmemişse komut ortamdaki
    `DATABASE_URL`'e DÜŞMEZ, durur.
    """
    monkeypatch.setenv("DATABASE_URL", "postgresql://kacak@127.0.0.1:5432/yanlis")

    parser = cli.build_parser()
    args = parser.parse_args(["durum", "--run-id", "kosu-1"])
    with pytest.raises(SystemExit) as cikis:
        cli.dsn_coz(args, parser)

    assert cikis.value.code != 0
    hata = capsys.readouterr().err
    assert "kanalı verilmedi" in hata
    assert "kacak" not in hata, "ortamdaki değer hata metnine sızdı"


async def test_cli_output_is_deterministic(pkg_db):
    """Aynı girdi → BAYT-AYNI çıktı; zaman damgası/rastgele sıra yok."""
    await _bos_evren(pkg_db)
    await _geri_alinabilir(pkg_db)

    birinci, rc1 = await cli.dispatch(pkg_db, _args("etki-analizi", *_dortlu()))
    ikinci, rc2 = await cli.dispatch(pkg_db, _args("etki-analizi", *_dortlu()))

    assert rc1 == rc2 == cli.RC_OK
    assert birinci == ikinci, "çıktı deterministik değil"
    assert "\n".join(birinci).strip(), "boş rapor — determinizm iddiası boşalırdı"


# ─── 3. Servis yüzeyine bağlılık (arayüz eki R10 · R11) ─────────────────────


async def test_yazim_subcommand_calls_write_draft_from_run(pkg_db, monkeypatch):
    """`yazim` yazım kapısını ÇAĞIRIR — ikinci bir taslak yolu yoktur."""
    cagrilar: list[dict] = []
    paket_id = uuid.uuid4()

    async def _sahte(db, *, run_id, actor):
        cagrilar.append({"run_id": run_id, "actor": actor})
        return paket_id

    monkeypatch.setattr(cli.writeback, "write_draft_from_run", _sahte)

    satirlar, rc = await cli.dispatch(
        pkg_db, _args("yazim", "--run-id", "kosu-abc", "--actor", ACTOR)
    )

    assert rc == cli.RC_OK
    assert cagrilar == [{"run_id": "kosu-abc", "actor": ACTOR}]
    assert str(paket_id) in "\n".join(satirlar)


async def test_yazim_subcommand_refuses_correction_run(pkg_db, monkeypatch):
    """Düzeltme koşusu yazım kapısından GEÇMEZ; komut rc≠0 döner (K-106)."""

    async def _reddet(db, *, run_id, actor):
        raise runs.CorrectionRunRefused("düzeltme ikinci bir sürüm yakamaz")

    monkeypatch.setattr(cli.writeback, "write_draft_from_run", _reddet)

    satirlar, rc = await cli.dispatch(
        pkg_db, _args("yazim", "--run-id", "kosu-duz", "--actor", ACTOR)
    )

    assert rc == cli.RC_REFUSED
    assert any("düzeltme" in satir.lower() for satir in satirlar)


async def test_duzeltme_yaz_subcommand_calls_update_draft_from_run(pkg_db, monkeypatch):
    """`duzeltme-yaz` YERİNDE güncelleme yüzeyini çağırır (K-106)."""
    cagrilar: list[dict] = []

    async def _sahte(db, *, run_id, actor):
        cagrilar.append({"run_id": run_id, "actor": actor})

    monkeypatch.setattr(cli.writeback, "update_draft_from_run", _sahte)

    _satirlar, rc = await cli.dispatch(
        pkg_db, _args("duzeltme-yaz", "--run-id", "kosu-duz", "--actor", ACTOR)
    )

    assert rc == cli.RC_OK
    assert cagrilar == [{"run_id": "kosu-duz", "actor": ACTOR}]


async def test_deaktive_et_subcommand_calls_deactivate_package(pkg_db, monkeypatch):
    """`deaktive-et` yaşam döngüsü yüzeyini çağırır — `hedefsiz`in TEK çıkışı."""
    cagrilar: list[dict] = []
    paket_id = uuid.uuid4()

    async def _sahte(db, *, package_id, actor):
        cagrilar.append({"package_id": package_id, "actor": actor})

    monkeypatch.setattr(cli.lifecycle, "deactivate_package", _sahte)

    _satirlar, rc = await cli.dispatch(
        pkg_db,
        _args("deaktive-et", "--package-id", str(paket_id), "--actor", ACTOR),
    )

    assert rc == cli.RC_OK
    assert cagrilar == [{"package_id": paket_id, "actor": ACTOR}]


def test_deaktive_et_needs_no_incident_and_no_evidence():
    """K-38 acil kolu AÇIK-2'den ETKİLENMEZ: olay kimliği İSTEMEZ.

    Kanıt zinciri isteyen geri alma yolu artık YALNIZ olay yoludur; bu komut o
    yoldan ayrıdır ve tek başına koşar. "Acil durumda önce olay aç" yanlış
    hatırlamasına karşı yapısal kanıt.
    """
    alt = cli.build_parser()._subparsers._group_actions[0].choices["deaktive-et"]
    zorunlu = {
        eylem.option_strings[-1] for eylem in alt._actions if eylem.required
    }
    assert zorunlu == {"--package-id", "--actor"}
    assert "--incident-id" not in {
        bayrak for eylem in alt._actions for bayrak in eylem.option_strings
    }


# ─── 4. K-145 olay zinciri ──────────────────────────────────────────────────


async def test_etki_analizi_requires_full_quad():
    """Kural sürümünü adlandıran DÖRT alanın dördü de zorunludur."""
    for eksik in (
        "--engine-version",
        "--engine-config-sha",
        "--kural-kimligi",
        "--kural-surumu",
    ):
        argv = _dortlu()
        yer = argv.index(eksik)
        del argv[yer : yer + 2]
        with pytest.raises(SystemExit):
            _args("etki-analizi", *argv)


async def test_etki_analizi_reports_expanded_set_when_unseparable(pkg_db):
    """Ayrım yapılamıyorsa küme TÜM adaylara genişler ve rapor bunu SÖYLER."""
    await _bos_evren(pkg_db)
    # Kökeni okunamayan aktif paket → `ayrilamaz` → genişleme.
    sector_id = await _sub_sector(pkg_db)
    await pkg_db.execute(
        "INSERT INTO social.sector_packages "
        "(sector_id, version, status, schema_version, content) "
        "VALUES ($1, 1, 'active', 1, $2)",
        sector_id,
        {"kapsam": "kökensiz"},
    )

    satirlar, rc = await cli.dispatch(pkg_db, _args("etki-analizi", *_dortlu()))
    rapor = "\n".join(satirlar)

    assert rc == cli.RC_OK
    assert "genisletildi: evet" in rapor, rapor
    assert "ayrilamaz" in rapor


async def test_olay_plani_writes_plan_without_touching_package_state(pkg_db):
    """Plan satırı YAZILIR; paket durumu ve sürümü DEĞİŞMEZ."""
    await _bos_evren(pkg_db)
    _sector_id, aktif = await _geri_alinabilir(pkg_db)
    once = await pkg_db.fetchrow(
        "SELECT status, version FROM social.sector_packages WHERE id = $1", aktif
    )

    satirlar, rc = await cli.dispatch(
        pkg_db, _args("olay-plani", *_dortlu(), "--actor", ACTOR)
    )

    assert rc == cli.RC_OK
    assert await pkg_db.fetchval(
        "SELECT count(*) FROM social.package_rollback_plans"
    ) >= 1
    sonra = await pkg_db.fetchrow(
        "SELECT status, version FROM social.sector_packages WHERE id = $1", aktif
    )
    assert dict(sonra) == dict(once), "paket durumu plan yazımında değişti"
    assert any("incident" in satir for satir in satirlar)


async def test_olay_plani_does_not_emit_package_events(pkg_db):
    """Plan yazımı paket OLAY KAYDI üretmez — olay kaydı yürütmeye aittir."""
    await _bos_evren(pkg_db)
    await _geri_alinabilir(pkg_db)
    once = await pkg_db.fetchval("SELECT count(*) FROM social.package_events")

    _satirlar, rc = await cli.dispatch(
        pkg_db, _args("olay-plani", *_dortlu(), "--actor", ACTOR)
    )

    assert rc == cli.RC_OK
    assert await pkg_db.fetchval("SELECT count(*) FROM social.package_events") == once


async def test_olay_plani_with_incident_id_calls_amend_not_build(pkg_db, monkeypatch):
    """`--incident-id` VARSA üyelik değişir (amend), YOKSA olay açılır (build)."""
    await _bos_evren(pkg_db)
    await _geri_alinabilir(pkg_db)
    cagrilar: list[str] = []

    async def _build(db, *, affected, actor):
        cagrilar.append("build")
        return "olay-1"

    async def _amend(db, *, incident_id, affected, actor):
        cagrilar.append("amend")
        return (1, 0)

    monkeypatch.setattr(cli.runs, "build_rollback_plan", _build)
    monkeypatch.setattr(cli.runs, "amend_rollback_plan", _amend)

    await cli.dispatch(pkg_db, _args("olay-plani", *_dortlu(), "--actor", ACTOR))
    await cli.dispatch(
        pkg_db,
        _args("olay-plani", *_dortlu(), "--actor", ACTOR, "--incident-id", "olay-1"),
    )

    assert cagrilar == ["build", "amend"]


async def test_olay_plani_refuses_new_rows_after_execution_started(pkg_db, monkeypatch):
    """Yürütme başladıysa üyelik KİLİTLİDİR: rc≠0 ve HİÇBİR satır yazılmaz (A3)."""
    await _bos_evren(pkg_db)
    await _geri_alinabilir(pkg_db)

    async def _kilitli(db, *, incident_id, affected, actor):
        raise runs.IncidentMembershipLocked("yürütme başladı — üyelik kilitli")

    monkeypatch.setattr(cli.runs, "amend_rollback_plan", _kilitli)
    once = await pkg_db.fetchval("SELECT count(*) FROM social.package_rollback_plans")

    satirlar, rc = await cli.dispatch(
        pkg_db,
        _args("olay-plani", *_dortlu(), "--actor", ACTOR, "--incident-id", "olay-1"),
    )

    assert rc != cli.RC_OK
    assert rc == cli.RC_LOCKED
    assert any("kilitli" in satir.lower() for satir in satirlar)
    assert (
        await pkg_db.fetchval("SELECT count(*) FROM social.package_rollback_plans")
        == once
    )


async def test_olay_onayla_subcommand_stamps_incident(pkg_db):
    """`olay-onayla` bekleyen satırları damgalar ve sayıyı basar."""
    await _bos_evren(pkg_db)
    await _geri_alinabilir(pkg_db)
    kume = await runs.affected_packages(
        pkg_db,
        engine_version=MOTOR_SURUM,
        engine_config_sha=CONFIG_SHA,
        kural_kimligi=KURAL,
        kural_surumu=KURAL_V1,
    )
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)

    satirlar, rc = await cli.dispatch(
        pkg_db,
        _args("olay-onayla", "--incident-id", incident_id, "--actor", ACTOR),
    )

    assert rc == cli.RC_OK
    assert any("1" in satir for satir in satirlar)
    assert await pkg_db.fetchval(
        "SELECT count(*) FROM social.package_rollback_plans "
        "WHERE incident_id = $1 AND onay_actor IS NOT NULL",
        incident_id,
    ) == 1


async def test_olay_onayla_subcommand_refuses_blank_actor(pkg_db):
    """Boş aktör kanonik kapıdan geçmez — komut rc≠0 döner."""
    await _bos_evren(pkg_db)
    await _geri_alinabilir(pkg_db)
    kume = await runs.affected_packages(
        pkg_db,
        engine_version=MOTOR_SURUM,
        engine_config_sha=CONFIG_SHA,
        kural_kimligi=KURAL,
        kural_surumu=KURAL_V1,
    )
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)

    _satirlar, rc = await cli.dispatch(
        pkg_db, _args("olay-onayla", "--incident-id", incident_id, "--actor", "   ")
    )

    assert rc == cli.RC_REFUSED


async def test_olay_onayla_reseals_incident_after_membership_growth(pkg_db):
    """Üyelik büyüdükten sonra yeniden onay, kapsam mührünü TAZELER (A3)."""
    await _bos_evren(pkg_db)
    await _geri_alinabilir(pkg_db)
    kume = await runs.affected_packages(
        pkg_db,
        engine_version=MOTOR_SURUM,
        engine_config_sha=CONFIG_SHA,
        kural_kimligi=KURAL,
        kural_surumu=KURAL_V1,
    )
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)
    await cli.dispatch(
        pkg_db, _args("olay-onayla", "--incident-id", incident_id, "--actor", ACTOR)
    )
    ilk_muhur = await pkg_db.fetchval(
        "SELECT onay_kapsam_sha FROM social.package_rollback_plans "
        "WHERE incident_id = $1 LIMIT 1",
        incident_id,
    )

    # İkinci bir sektör kümeye girer → kapsam DEĞİŞİR.
    ikinci = await _sub_sector(pkg_db)
    await _kokenli_paket(
        pkg_db, ikinci, version=1, status="archived", kural_surumu=KURAL_V2
    )
    await _kokenli_paket(pkg_db, ikinci, version=2, status="active")
    buyumus = await runs.affected_packages(
        pkg_db,
        engine_version=MOTOR_SURUM,
        engine_config_sha=CONFIG_SHA,
        kural_kimligi=KURAL,
        kural_surumu=KURAL_V1,
    )
    await runs.amend_rollback_plan(
        pkg_db, incident_id=incident_id, affected=buyumus, actor=ACTOR
    )

    _satirlar, rc = await cli.dispatch(
        pkg_db, _args("olay-onayla", "--incident-id", incident_id, "--actor", ACTOR)
    )

    assert rc == cli.RC_OK
    yeni_muhur = await pkg_db.fetchval(
        "SELECT onay_kapsam_sha FROM social.package_rollback_plans "
        "WHERE incident_id = $1 LIMIT 1",
        incident_id,
    )
    assert yeni_muhur != ilk_muhur, "kapsam büyüdü ama mühür tazelenmedi"


# ─── 5. Olay yürütme — paket paket, `hedefsiz` AYRI ─────────────────────────


def test_olay_geri_al_requires_incident_id():
    """Olay kimliği olmadan yürütme YOKTUR."""
    with pytest.raises(SystemExit):
        _args("olay-geri-al", "--actor", ACTOR)


async def _iki_paketli_onayli_olay(pkg_db) -> tuple[str, list]:
    """İki sektör, ikisi de geri alınabilir; olay onaylanmış döner."""
    await _bos_evren(pkg_db)
    paketler = []
    for _ in range(2):
        sector_id = await _sub_sector(pkg_db)
        await _kokenli_paket(
            pkg_db, sector_id, version=1, status="archived", kural_surumu=KURAL_V2
        )
        aktif, _ = await _kokenli_paket(pkg_db, sector_id, version=2, status="active")
        paketler.append(aktif)
    kume = await runs.affected_packages(
        pkg_db,
        engine_version=MOTOR_SURUM,
        engine_config_sha=CONFIG_SHA,
        kural_kimligi=KURAL,
        kural_surumu=KURAL_V1,
    )
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)
    await runs.approve_incident_rollback(pkg_db, incident_id=incident_id, actor=ACTOR)
    return incident_id, paketler


async def test_olay_geri_al_rolls_back_each_package_separately(pkg_db):
    """Her paket KENDİ işleminde geri alınır — toplu-atomik yeni mekanizma YOK."""
    incident_id, paketler = await _iki_paketli_onayli_olay(pkg_db)

    satirlar, rc = await cli.dispatch(
        pkg_db, _args("olay-geri-al", "--incident-id", incident_id, "--actor", ACTOR)
    )

    assert rc == cli.RC_OK
    tamamlanan = await pkg_db.fetchval(
        "SELECT count(*) FROM social.package_rollback_plans "
        "WHERE incident_id = $1 AND durum = 'tamamlandi'",
        incident_id,
    )
    assert tamamlanan == len(paketler)
    assert any("tamamlandi" in satir for satir in satirlar)


async def test_olay_geri_al_logs_event_per_package(pkg_db):
    """Her paket KENDİ olay kaydını alır — tek toplu kayıt DEĞİL."""
    incident_id, paketler = await _iki_paketli_onayli_olay(pkg_db)
    once = await pkg_db.fetchval("SELECT count(*) FROM social.package_events")

    _satirlar, rc = await cli.dispatch(
        pkg_db, _args("olay-geri-al", "--incident-id", incident_id, "--actor", ACTOR)
    )

    assert rc == cli.RC_OK
    sonra = await pkg_db.fetchval("SELECT count(*) FROM social.package_events")
    assert sonra - once >= len(paketler), "paket başına olay kaydı yazılmadı"


async def test_olay_geri_al_resumes_without_double_rollback(pkg_db):
    """Yarıda kalan yürütme kaldığı yerden devam eder; ikinci kez geri ALMAZ."""
    incident_id, _paketler = await _iki_paketli_onayli_olay(pkg_db)

    await cli.dispatch(
        pkg_db, _args("olay-geri-al", "--incident-id", incident_id, "--actor", ACTOR)
    )
    surumler = await pkg_db.fetch(
        "SELECT id, version, status FROM social.sector_packages ORDER BY id"
    )

    satirlar, rc = await cli.dispatch(
        pkg_db, _args("olay-geri-al", "--incident-id", incident_id, "--actor", ACTOR)
    )

    assert rc == cli.RC_OK
    assert [dict(r) for r in surumler] == [
        dict(r)
        for r in await pkg_db.fetch(
            "SELECT id, version, status FROM social.sector_packages ORDER BY id"
        )
    ], "ikinci koşum paket durumunu yeniden değiştirdi"
    assert any("zaten_tamamlandi" in satir for satir in satirlar)


async def _hedefsiz_olay(pkg_db) -> tuple[str, object]:
    """Güvenli arşiv sürümü OLMAYAN aktif paket → plan satırı `hedefsiz`."""
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    aktif, _ = await _kokenli_paket(pkg_db, sector_id, version=1, status="active")
    kume = await runs.affected_packages(
        pkg_db,
        engine_version=MOTOR_SURUM,
        engine_config_sha=CONFIG_SHA,
        kural_kimligi=KURAL,
        kural_surumu=KURAL_V1,
    )
    incident_id = await runs.build_rollback_plan(pkg_db, affected=kume, actor=ACTOR)
    await runs.approve_incident_rollback(pkg_db, incident_id=incident_id, actor=ACTOR)
    return incident_id, aktif


async def test_olay_geri_al_reports_hedefsiz_separately(pkg_db):
    """`hedefsiz` satırlar AYRI BAŞLIK altında raporlanır — sessizce başarı DEĞİL."""
    incident_id, aktif = await _hedefsiz_olay(pkg_db)

    satirlar, rc = await cli.dispatch(
        pkg_db, _args("olay-geri-al", "--incident-id", incident_id, "--actor", ACTOR)
    )
    rapor = "\n".join(satirlar)

    assert rc != cli.RC_OK, "hedefsiz satır sessizce başarı sayıldı"
    assert "hedefsiz:" in rapor, rapor
    assert str(aktif) in rapor


async def test_olay_geri_al_does_not_auto_deactivate_hedefsiz(pkg_db):
    """`hedefsiz` paket KENDİLİĞİNDEN deaktive EDİLMEZ — ayrı operatör kararı (K-38)."""
    incident_id, aktif = await _hedefsiz_olay(pkg_db)

    await cli.dispatch(
        pkg_db, _args("olay-geri-al", "--incident-id", incident_id, "--actor", ACTOR)
    )

    assert (
        await pkg_db.fetchval(
            "SELECT status FROM social.sector_packages WHERE id = $1", aktif
        )
        == "active"
    ), "hedefsiz paket komut tarafından indirildi"


# ─── 6. AÇIK-2 — komut KALDIRILDI, tek yol olay yoludur ────────────────────


def test_geri_al_subcommand_no_longer_exists():
    """`geri-al` alt komutu YOKTUR (Eray kararı, 2026-09-11).

    Arayüz eki AÇIK-2 seçenek **A**'yı (komut kalsın, olay kimliği istesin)
    seçmişti; uygulamada o seçenek kapanmadı. Ölçüldü: komut üyeliği
    doğruladıktan sonra paket filtresi ALMAYAN olay-kapsamlı yürütücüyü
    çağırıyor ve aradaki pencerede adlandırılmayan paket geri alınabiliyor.
    Pencereyi kapatmak servis katmanında paket-hedefli bir yürütücü ister; o
    yüzey bu görevin dosya kümesinin dışındadır.

    **Bu test bir KARAR KİLİDİDİR:** komut sessizce geri eklenirse kapanmamış
    yarış da onunla birlikte geri gelir.
    """
    with pytest.raises(SystemExit):
        _args("geri-al", "--incident-id", "olay-1", "--actor", ACTOR)

    assert "geri-al" not in cli.GOVDELER
    assert "geri-al" not in cli.RUN_SUBCOMMANDS


async def test_single_package_rollback_still_possible_through_the_incident_path(pkg_db):
    """Yetenek KAYBOLMADI — tek paketlik geri alma tek satırlık olayla yapılır.

    Kaybolan şey kısayoldur, kanıt zinciri değil: `olay-plani` → `olay-onayla`
    → `olay-geri-al` aynen koşar ve tek paketi geri alır.
    """
    incident_id, aktif = await _onayli_olay(pkg_db)

    _satirlar, rc = await cli.dispatch(
        pkg_db, _args("olay-geri-al", "--incident-id", incident_id, "--actor", ACTOR)
    )

    assert rc == cli.RC_OK
    assert (
        await pkg_db.fetchval(
            "SELECT durum FROM social.package_rollback_plans "
            "WHERE incident_id = $1 AND package_id = $2",
            incident_id,
            aktif,
        )
        == "tamamlandi"
    )


# ─── 7. K-26 vade bildirimi ─────────────────────────────────────────────────


async def test_due_notice_creates_admin_event(pkg_db):
    """Periyodu (6 ay) dolan aktif paket için yöneticiye bildirim YAZILIR.

    Elle vade takibi kalmaz (K-26): komut, vadesi geçmiş her paketi bulur ve
    `record_admin_event` ile outbox satırı yazar.
    """
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    aktif, _ = await _kokenli_paket(pkg_db, sector_id, version=1, status="active")
    await pkg_db.execute(
        "UPDATE social.sector_packages SET activated_at = now() - interval '7 months' "
        "WHERE id = $1",
        aktif,
    )
    once = await pkg_db.fetchval("SELECT count(*) FROM social.admin_events")

    satirlar, rc = await cli.dispatch(pkg_db, _args("vade-bildirimi", "--actor", ACTOR))

    assert rc == cli.RC_OK
    assert await pkg_db.fetchval("SELECT count(*) FROM social.admin_events") == once + 1
    assert str(aktif) in "\n".join(satirlar)


async def test_due_notice_skips_packages_inside_the_period(pkg_db):
    """POZİTİF KONTROL'ün karşı kolu — vadesi DOLMAYAN paket bildirim üretmez."""
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    aktif, _ = await _kokenli_paket(pkg_db, sector_id, version=1, status="active")
    await pkg_db.execute(
        "UPDATE social.sector_packages SET activated_at = now() - interval '1 month' "
        "WHERE id = $1",
        aktif,
    )
    once = await pkg_db.fetchval("SELECT count(*) FROM social.admin_events")

    _satirlar, rc = await cli.dispatch(pkg_db, _args("vade-bildirimi", "--actor", ACTOR))

    assert rc == cli.RC_OK
    assert await pkg_db.fetchval("SELECT count(*) FROM social.admin_events") == once


# ─── 8. Yerel arıza — n8n errorWorkflow'un GÖREMEDİĞİ hat ───────────────────


async def test_brief_doctor_writes_the_mechanical_gate_artifact(pkg_db, tmp_path):
    """POZİTİF KONTROL: mekanik kapı raporu ham artefakt katmanına GERÇEKTEN iner.

    ÖLÇÜLEN KUSUR (Task 17 dispatch'i): şema `mechanical_gate` türünü
    tanımıyordu ve bu çağrı ilk gerçek koşumda `ValueError` ile düşüyordu —
    4134 yeşil testin hiçbiri değerleri GERÇEK veritabanına karşı koşmadığı
    için kusur görünmüyordu. Kapanış bu yüzden şemaya karşı koşan bir testle
    kurulur, tür sabitini okuyan bir testle değil.
    """
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk")

    kaynak = tmp_path / "KAYNAK-1.md"
    kaynak.write_text("# kaynak\n\nmekanik kapı girdisi\n", encoding="utf-8")

    satirlar, rc = await cli.dispatch(
        pkg_db,
        _args(
            "brief-doctor",
            "--run-id",
            run_id,
            "--kaynak-dosya",
            str(kaynak),
            "--kaynak-adi",
            "KAYNAK-1",
            "--sektor-slug",
            "kuyumculuk",
            "--damga",
            runs.build_stamp(
                model="brief-doctor",
                surum="1",
                tarih="2026-09-12",
                girdi_ozeti="test",
            ),
        ),
    )

    assert rc == cli.RC_OK, satirlar
    tur = await pkg_db.fetchval(
        "SELECT kind FROM social.sector_research_artifacts WHERE run_id = $1", run_id
    )
    assert tur == cli.MEKANIK_KAPI_ARTEFAKTI, (
        f"mekanik kapı raporu yazılmadı ya da başka türle yazıldı: {tur!r}"
    )


async def test_cli_terminal_failure_produces_admin_event(pkg_db, monkeypatch):
    """Hat adımı yerelde düşerse koşu YARIM işaretlenir ve yönetici bildirimi yazılır.

    n8n `errorWorkflow` yalnız workflow'un KENDİ arızasını yakalar; yerelde
    koşan bir adımın sıfırdan farklı çıkışı oraya HİÇ ulaşmaz. Kapı burada.
    """
    await _bos_evren(pkg_db)
    sector_id = await _sub_sector(pkg_db)
    run_id = runs.new_run_id()
    await runs.open_run(
        pkg_db, sector_id=sector_id, run_id=run_id, kosu_turu="ilk"
    )
    once = await pkg_db.fetchval("SELECT count(*) FROM social.admin_events")

    def _patla(source_text, *, source_name):
        raise RuntimeError("araç düştü")

    monkeypatch.setattr(cli.brief_doctor, "run", _patla)
    kaynak = BACKEND_KOKU / "tests" / "__init__.py"

    _satirlar, rc = await cli.dispatch(
        pkg_db,
        _args(
            "brief-doctor",
            "--run-id",
            run_id,
            "--kaynak-dosya",
            str(kaynak),
            "--kaynak-adi",
            "KAYNAK-1",
            "--sektor-slug",
            "kuyumculuk",
            "--damga",
            runs.build_stamp(
                model="brief-doctor",
                surum="1",
                tarih="2026-09-11",
                girdi_ozeti="test",
            ),
        ),
    )

    assert rc != cli.RC_OK
    assert (
        await pkg_db.fetchval(
            "SELECT durum FROM social.sector_package_runs WHERE run_id = $1", run_id
        )
        == "tamamlanmadi"
    )
    assert await pkg_db.fetchval("SELECT count(*) FROM social.admin_events") == once + 1


# ─── 9. K-45 geri-dönüş bandı — MÜŞTERİ YÜZEYİ ──────────────────────────────


async def test_recovered_state_exposed_on_package_status_endpoint(pkg_db):
    """Bakım penceresini yaşamış markaya `recovered` + SABİT metin döner."""
    sub_sector_id = await _seed_sub_sector(pkg_db)
    user, brand_id = await _seed_owner_and_brand(pkg_db, sub_sector_id=sub_sector_id)
    # Marka ÖNCE atanır (bakım penceresi), paket SONRA aktive edilir.
    #
    # Atama anı AÇIKÇA geriye alınır: `now()` PostgreSQL'de İŞLEM zaman damgası
    # olduğu için tek işlemde koşan testte tetikleyicinin yazdığı `assigned_at`
    # ile `activated_at` BİREBİR eşit çıkar ve gerçek bir bakım penceresi
    # kurulamazdı (ölçüldü: kesişim sorgusu boş döndü).
    await pkg_db.execute(
        "UPDATE social.brand_sub_sector_history "
        "SET assigned_at = now() - interval '3 days' WHERE brand_id = $1",
        brand_id,
    )
    await pkg_db.execute(
        "INSERT INTO social.sector_packages "
        "(sector_id, version, status, schema_version, content, activated_at) "
        "VALUES ($1, 1, 'active', 1, $2, now())",
        sub_sector_id,
        {"kapsam": "kuyumculuk"},
    )

    yanit = await brands_router.get_package_status(
        brand_id=brand_id, user=user, db=pkg_db
    )

    assert yanit.data["mode"] == "recovered"
    assert yanit.data["message"] == notifications.RECOVERED_BANNER_MESSAGE


async def test_recovered_only_for_brands_with_maintenance_overlap(pkg_db):
    """Paket aktifken atanan marka bakım YAŞAMADI — `packaged` döner."""
    sub_sector_id = await _seed_sub_sector(pkg_db)
    await pkg_db.execute(
        "INSERT INTO social.sector_packages "
        "(sector_id, version, status, schema_version, content, activated_at) "
        "VALUES ($1, 1, 'active', 1, $2, now() - interval '1 day')",
        sub_sector_id,
        {"kapsam": "kuyumculuk"},
    )
    # Atama aktivasyondan SONRA → kesişim YOK.
    user, brand_id = await _seed_owner_and_brand(pkg_db, sub_sector_id=sub_sector_id)

    yanit = await brands_router.get_package_status(
        brand_id=brand_id, user=user, db=pkg_db
    )

    assert yanit.data == {"mode": "packaged", "message": None}


async def test_recovered_skipped_when_history_unknown(pkg_db):
    """Geçmişi OLMAYAN marka retroaktif 'tamamlandı' bildirimi ALMAZ."""
    sub_sector_id = await _seed_sub_sector(pkg_db)
    user, brand_id = await _seed_owner_and_brand(pkg_db, sub_sector_id=sub_sector_id)
    await pkg_db.execute(
        "INSERT INTO social.sector_packages "
        "(sector_id, version, status, schema_version, content, activated_at) "
        "VALUES ($1, 1, 'active', 1, $2, now())",
        sub_sector_id,
        {"kapsam": "kuyumculuk"},
    )
    # Maruziyet kanıtı SİLİNİR — geçmiş bilinmiyor.
    await pkg_db.execute(
        "DELETE FROM social.brand_sub_sector_history WHERE brand_id = $1", brand_id
    )

    yanit = await brands_router.get_package_status(
        brand_id=brand_id, user=user, db=pkg_db
    )

    assert yanit.data == {"mode": "packaged", "message": None}


async def test_package_status_owner_scoped(pkg_db):
    """Geri-dönüş durumu da SAHİPLİK kapısının ardındadır — yabancıya 404."""
    sub_sector_id = await _seed_sub_sector(pkg_db)
    _user, brand_id = await _seed_owner_and_brand(pkg_db, sub_sector_id=sub_sector_id)
    await pkg_db.execute(
        "INSERT INTO social.sector_packages "
        "(sector_id, version, status, schema_version, content, activated_at) "
        "VALUES ($1, 1, 'active', 1, $2, now())",
        sub_sector_id,
        {"kapsam": "kuyumculuk"},
    )
    yabanci, _ = await _seed_owner_and_brand(pkg_db)

    with pytest.raises(HTTPException) as exc:
        await brands_router.get_package_status(
            brand_id=brand_id, user=yabanci, db=pkg_db
        )

    assert exc.value.status_code == 404


# ─── 10. Hakem turu 13 — kapanan üç yüksek bulgu ────────────────────────────


class _SahteKosum:
    """Alt süreç sonucunun asgari ikizi — `subprocess.run` dönüşü taklit edilir."""

    def __init__(self, stdout: str, returncode: int = 0) -> None:
        self.stdout = stdout
        self.stderr = ""
        self.returncode = returncode


def _prob(beklenen, cikti, *, rc=0):
    """Probu enjekte edilmiş getirici ve koşucuyla kurar."""
    return cli._web_probu(
        1.0,
        getirici=lambda _sn: beklenen,
        kosucu=lambda *a, **k: _SahteKosum(cikti, rc),
    )


def test_web_probe_accepts_only_the_exact_fresh_value():
    """POZİTİF KONTROL — aracın TAM değeri basması erişim kanıtıdır."""
    assert _prob("abc123", "abc123\n")(auditors_rolleri()[1]) is True


def test_web_probe_rejects_a_stale_or_invented_answer():
    """Ağa çıkmayan ama makul görünen cevap REDDEDİLİR.

    Ölçülen kusur: ilk yazım statik ve yaygın bilinen bir metni soruyordu;
    ağa hiç çıkmayan bir model onu ezberden üretebilirdi. Meydan okuma değeri
    artık TAZE olduğu için ezberden üretilemez.
    """
    prob = _prob("abc123", "UNREACHABLE\n")
    assert prob(auditors_rolleri()[1]) is False


def test_web_probe_rejects_a_value_buried_in_prose():
    """Karşılaştırma TAM EŞİTLİKTİR — değeri metne gömen cevap geçmez.

    Alt dize eşleşmesi kabul edilseydi, değeri doğru tahmin etmeden etrafına
    laf dolayan bir cevap da erişim sayılırdı.
    """
    prob = _prob("abc123", "The sha appears to be abc123, I think.\n")
    assert prob(auditors_rolleri()[1]) is False


def test_crashed_tool_is_a_measurement_failure_not_measured_absence():
    """Araç sıfırdan farklı çıkarsa bu ÖLÇÜM ARIZASIDIR — muafiyet doğurmaz.

    İki aşamalı bir ders. Önce kapı mutasyonda sahte-yeşil geldi: hiçbir test
    "araç çöktü ama doğru değeri bastı" hâlini ölçmüyordu. Eklenen ilk test
    `False` bekliyordu — ve o beklenti YANLIŞTI: `preflight` her `False`'u
    ÖLÇÜLMÜŞ ERİŞİMSİZLİK sayar ve o durum K-14'ün muafiyet yetkisini taşır.
    Yani eksik kimlik bilgisi ya da çöken bir CLI, "ölçtüm, ağ yok" diye
    kaydediliyordu (ölçüldü: `muafiyet_mesru=True`).

    Bu test artık kapıyı TÜKETİCİ üzerinden ölçer: probun dönüşüne değil,
    `preflight`in ürettiği duruma bakar — asıl iddia orada yaşıyor.
    """
    from app.services.sector_pipeline import auditors

    prob = _prob("abc123", "abc123\n", rc=1)

    with pytest.raises(cli.WebProbeUnavailable):
        prob(auditors_rolleri()[1])

    sonuc = auditors.preflight(auditors.DENETCI_ROLLERI[1], prob=prob)
    assert sonuc.durum == auditors.PreflightDurumu.OLCUM_ARIZASI
    assert not sonuc.tur_baslayabilir
    assert not sonuc.muafiyet_mesru, "ölçülmemiş arıza muafiyet üretti"


def test_clean_exit_with_wrong_value_is_measured_absence(auditors_roller=None):
    """`False` YALNIZ temiz çıkışlı yanlış cevaba ayrılmıştır.

    Bu, yukarıdaki testin karşı kolu: ikisi ayrışmazsa "ölçülmüş erişimsizlik"
    ile "ölçülemedi" aynı kovaya düşer ve muafiyet ayrımı anlamını yitirir.
    """
    from app.services.sector_pipeline import auditors

    prob = _prob("abc123", "UNREACHABLE\n", rc=0)

    assert prob(auditors_rolleri()[1]) is False
    sonuc = auditors.preflight(auditors.DENETCI_ROLLERI[1], prob=prob)
    assert sonuc.durum == auditors.PreflightDurumu.ERISIM_YOK
    assert sonuc.muafiyet_mesru


def test_web_probe_reports_measurement_failure_when_challenge_cannot_be_fetched():
    """Beklenen değer ALINAMAZSA bu bir ÖLÇÜM ARIZASIDIR — muafiyet doğmaz.

    `False` dönmek "ölçtüm, erişim yok" demektir ve K-14'ün muafiyet kolunu
    meşrulaştırır; ölçülemeyen bir şey muafiyet üretemez.
    """

    def _patla(_sn):
        raise OSError("ağ yok")

    prob = cli._web_probu(1.0, getirici=_patla, kosucu=lambda *a, **k: _SahteKosum(""))
    with pytest.raises(cli.WebProbeUnavailable):
        prob(auditors_rolleri()[1])


def test_web_probe_measurement_failure_grants_no_exemption():
    """Ölçüm arızası turu DURDURUR ve `ERISIM_YOK` muafiyeti ÜRETMEZ."""
    from app.services.sector_pipeline import auditors

    def _patla(_sn):
        raise OSError("ağ yok")

    sonuc = auditors.preflight(
        auditors.DENETCI_ROLLERI[1],
        prob=cli._web_probu(1.0, getirici=_patla, kosucu=lambda *a, **k: _SahteKosum("")),
    )

    assert sonuc.durum == auditors.PreflightDurumu.OLCUM_ARIZASI
    assert not sonuc.tur_baslayabilir
    assert not sonuc.muafiyet_mesru


def test_web_probe_success_opens_the_round():
    """POZİTİF KONTROL — doğrulanmış erişim turun başlamasına İZİN VERİR.

    Bu test olmasaydı prob "her koşulda reddet" hâline düşürülebilir ve kapanış
    turunun yakaladığı kusur (olumlu yolun tümden silinmesi) geri gelirdi.
    """
    from app.services.sector_pipeline import auditors

    sonuc = auditors.preflight(
        auditors.DENETCI_ROLLERI[1], prob=_prob("abc123", "abc123")
    )

    assert sonuc.durum == auditors.PreflightDurumu.ERISIM_VAR
    assert sonuc.tur_baslayabilir


def auditors_rolleri():
    from app.services.sector_pipeline import auditors

    return auditors.DENETCI_ROLLERI


async def test_olay_onayla_refuses_when_nothing_was_stamped(pkg_db):
    """Sıfır satır damgalandıysa komut BAŞARI DÖNMEZ (hakem, orta → düzeltildi)."""
    _satirlar, rc = await cli.dispatch(
        pkg_db,
        _args("olay-onayla", "--incident-id", f"olay-{uuid.uuid4().hex}", "--actor", ACTOR),
    )

    assert rc == cli.RC_REFUSED


# ═══ 5. Ham artefakt türü şemayla uyumlu mu ═════════════════════════════════
#
# 2026-09-11'de ÖLÇÜLDÜ: komut ailesi ham artefakt satırlarını şemanın kabul
# etmediği türlerle yazıyordu. Canlı kısıt (`sector_research_artifacts_kind_check`,
# migration 032) yalnız `research` · `review` · `synthesis` kabul ediyor; CLI ise
# üç çağrı yerinde Türkçe etiketler geçiyordu. Hiçbir test o değerleri gerçek
# veritabanına karşı koşmadığı için kusur 4134 yeşil testin altında görünmedi ve
# ilk gerçek koşumda (Task 19) her ham artefakt yazımı düşerdi.
#
# KAPSAM — dürüst etiket (hakem turu 2, orta). Bu tarama DOĞRUDAN çağrı
# yerlerini kapsar: `record_artifact(kind=...)` biçimini adıyla ve statik
# değerle görür. Takma adla çağırma, bir değişkene bağlama ya da `**kwargs` ile
# iletme biçimleri GÖRÜNMEZ. Bu yüzden kural DEĞİŞMEZE yükseltildi ve asıl kapı
# artık yazıcının kendisindedir (`runs.record_artifact`, şemanın kapalı kümesine
# karşı fail-closed). Buradaki tarama ön-uyarıdır: kusuru veritabanına gitmeden
# ÖNCE, testte gösterir.


async def _sema_izinli_artefakt_turleri(db) -> frozenset[str]:
    """İzinli tür kümesini UYGULANMIŞ şemadan okur — migration METNİNDEN değil.

    Önceki biçim yalnız 032'nin satır içi CHECK'ini regex'liyordu; kısıtı
    sonradan genişleten migration'lara (036) KÖRDÜ. Kapının ölçtüğü şey artık
    veritabanının gerçekten uyguladığı kuraldır.
    """
    import re

    tanim = await db.fetchval(
        "SELECT pg_get_constraintdef(c.oid) FROM pg_constraint c "
        " WHERE c.conrelid = 'social.sector_research_artifacts'::regclass "
        "   AND c.conname = 'sector_research_artifacts_kind_check'"
    )
    assert tanim, "sector_research_artifacts_kind_check YOK — kapı ölçemez"
    return frozenset(re.findall(r"'([a-z_]+)'::text", tanim))


def _uretim_dosyalari() -> list[Path]:
    """Taranacak ÜRETİM dosyaları — kavramdan türetilir, elle sayılmaz.

    Kapsam `app/` + `scripts/` altındaki her `.py`'dir. İlk yazım YALNIZ
    `sector_pipeline_cli.py`'yi tarıyordu ve "sınıf düzeyinde koruma" diye
    sunuluyordu; hakem turu 1 (orta) iddianın kapsamdan GENİŞ olduğunu ölçtü —
    başka bir serviste açılacak yeni bir çağrı yeri kapıya hiç uğramazdı.
    """
    kokler = (BACKEND_KOKU / "app", BACKEND_KOKU / "scripts")
    return sorted(
        yol
        for kok in kokler
        for yol in kok.rglob("*.py")
        if "__pycache__" not in yol.parts
    )


def _uretim_artefakt_turleri() -> dict[str, str]:
    """Üretimdeki her `record_artifact` çağrısının tür argümanı — yer: değer."""
    import ast

    bulunan: dict[str, str] = {}
    for yol in _uretim_dosyalari():
        kaynak = yol.read_text(encoding="utf-8")
        if "record_artifact" not in kaynak:
            continue
        agac = ast.parse(kaynak)
        sabitler = {
            hedef.id: dugum.value.value
            for dugum in ast.walk(agac)
            if isinstance(dugum, ast.Assign) and isinstance(dugum.value, ast.Constant)
            for hedef in dugum.targets
            if isinstance(hedef, ast.Name) and isinstance(dugum.value.value, str)
        }
        sabitler.update(
            {
                dugum.target.id: dugum.value.value
                for dugum in ast.walk(agac)
                if isinstance(dugum, ast.AnnAssign)
                and isinstance(dugum.target, ast.Name)
                and isinstance(dugum.value, ast.Constant)
                and isinstance(dugum.value.value, str)
            }
        )
        for dugum in ast.walk(agac):
            if not isinstance(dugum, ast.Call):
                continue
            ad = dugum.func
            adi = ad.attr if isinstance(ad, ast.Attribute) else getattr(ad, "id", "")
            if adi != "record_artifact":
                continue
            if isinstance(ad, ast.Name) and ad.id == "record_artifact":
                # tanımın kendisi degil, cagri; tanim `def` dugumudur
                pass
            for anahtar in dugum.keywords:
                if anahtar.arg != "kind":
                    continue
                yer = f"{yol.relative_to(BACKEND_KOKU)}:{dugum.lineno}"
                if isinstance(anahtar.value, ast.Constant):
                    bulunan[yer] = anahtar.value.value
                elif isinstance(anahtar.value, ast.Name):
                    bulunan[yer] = sabitler[anahtar.value.id]
                else:
                    raise AssertionError(
                        f"{yer}: `kind` argümanı statik olarak okunamıyor — "
                        "kapı bu biçimi ölçemez (fail-closed)"
                    )
    return bulunan


async def test_cli_records_artifacts_with_schema_accepted_kinds(pkg_db):
    """CLI'nin yazdığı her artefakt türü ŞEMANIN kabul ettiği kümededir.

    **MUAFİYET YOKTUR.** Eski biçimde bir borç listesi (`SEMA_DISI_ARTEFAKT_TURLERI`)
    kapının dışında kalmaya izin veriyordu; borç Task 18'de ödendi ve liste
    KALDIRILDI — kapı artık istisnasız fail-closed.
    """
    izinli = await _sema_izinli_artefakt_turleri(pkg_db)
    bulunan = _uretim_artefakt_turleri()

    assert bulunan, "üretimde hiç `record_artifact` çağrısı bulunamadı — kapı boşa koşuyor"
    ihlaller = {satir: tur for satir, tur in bulunan.items() if tur not in izinli}
    assert not ihlaller, (
        f"şemanın kabul etmediği artefakt türü: {ihlaller} — izinli küme {sorted(izinli)}"
    )


# ═══ 6. İşletime hazırlık onayı (plan Task 17, K-69/K-70) ═══════════════════


def test_hazirlik_onayla_requires_run_id(capsys):
    """Koşu kimliği OLMADAN çağrılamaz — tasdik koşusuz yazılamaz."""
    with pytest.raises(SystemExit) as cikis:
        _args("hazirlik-onayla", "--actor", ACTOR)

    assert cikis.value.code != 0
    assert "--run-id" in capsys.readouterr().err


async def test_hazirlik_onayla_writes_attestation(pkg_db):
    """`--onayla` ile TEK onay kalıcı tasdike döner (F18)."""
    from .test_readiness_checklist import _hazir_kosu

    run_id = await _hazir_kosu(pkg_db)

    satirlar, rc = await cli.dispatch(
        pkg_db,
        _args("hazirlik-onayla", "--run-id", run_id, "--actor", ACTOR, "--onayla"),
    )

    assert rc == cli.RC_OK, satirlar
    tasdik = await pkg_db.fetchval(
        "SELECT readiness_attestation FROM social.sector_package_runs WHERE run_id = $1",
        run_id,
    )
    assert tasdik is not None
    assert tasdik["onaylandi"] is True
    assert tasdik["actor"] == ACTOR


async def test_hazirlik_onayla_without_flag_only_reports(pkg_db):
    """Bayraksız çağrı RAPORDUR — K-70: ön-kontrol kendi kendini onaylamaz."""
    from .test_readiness_checklist import _hazir_kosu

    run_id = await _hazir_kosu(pkg_db)

    satirlar, rc = await cli.dispatch(
        pkg_db, _args("hazirlik-onayla", "--run-id", run_id, "--actor", ACTOR)
    )

    assert rc == cli.RC_OK
    assert satirlar, "rapor boş — operatör neyi onaylayacağını göremez"
    assert (
        await pkg_db.fetchval(
            "SELECT readiness_attestation FROM social.sector_package_runs "
            "WHERE run_id = $1",
            run_id,
        )
        is None
    )


async def test_hazirlik_onayla_refuses_when_a_gate_item_failed(pkg_db):
    """Otomatik ölçümü DÜŞEN kapı maddesi varken onay YAZILMAZ (fail-closed)."""
    from .test_pipeline_writeback import _kosu, _sub_sector

    sector_id = await _sub_sector(pkg_db)
    run_id = await _kosu(pkg_db, sector_id, sonuc="no_change", hazirlik=False)

    satirlar, rc = await cli.dispatch(
        pkg_db,
        _args("hazirlik-onayla", "--run-id", run_id, "--actor", ACTOR, "--onayla"),
    )

    assert rc == cli.RC_REFUSED
    assert any("md-11" in satir for satir in satirlar)
    assert (
        await pkg_db.fetchval(
            "SELECT readiness_attestation FROM social.sector_package_runs "
            "WHERE run_id = $1",
            run_id,
        )
        is None
    )


def test_hazirlik_onayla_evaluates_and_writes_under_one_locked_transaction():
    """Değerlendirme ile yazım AYNI işlemde ve koşu satırı KİLİTLİ olmalı.

    **Yapısal kapı, davranışsal değil — dürüst etiket.** Yarış penceresini
    davranışla ölçmek eşzamanlı iki koşum ister; burada kilidin ve işlemin
    KURULDUĞU doğrulanır. Hakem turu 1 (yüksek) ilk yazımda ikisinin ayrı
    autocommit ifadeleri olduğunu ölçtü: iki operatör aynı anda onaylayabiliyor
    ve değerlendirme ile yazım arasında koşu satırı değişebiliyordu.
    """
    import inspect

    kaynak = inspect.getsource(cli._kos_hazirlik_onayla)

    assert "conn.transaction()" in kaynak
    assert "FOR UPDATE" in kaynak
    assert kaynak.index("conn.transaction()") < kaynak.index("readiness.evaluate")


async def test_hazirlik_onayla_refuses_when_evidence_changed_after_evaluation(
    pkg_db, monkeypatch
):
    """Değerlendirmeden SONRA kanıt değiştiyse onay YAZILMAZ (hakem turu 2, F1).

    Kanıtın bir kısmı EKLEMELİ bir tabloda durur ve tasdik kaydının "ne
    gördüm" alanı yoktur. Pencere tamamen kapanmıyor — kapanışı sözleşme
    revizyonuna bağlı (son tarih Task 19) — ama yazımdan hemen önceki taze
    okuma, bayat değerlendirmeyi belgelemeyi ENGELLER.
    """
    from .test_readiness_checklist import _hazir_kosu
    from app.services.sector_pipeline import readiness

    run_id = await _hazir_kosu(pkg_db)
    gercek = readiness.evaluate

    async def _bayat(db, *, run_id):
        rapor = await gercek(db, run_id=run_id)
        return dataclasses.replace(rapor, kanit_parmakizi="bayat-parmakizi")

    monkeypatch.setattr(readiness, "evaluate", _bayat)

    satirlar, rc = await cli.dispatch(
        pkg_db,
        _args("hazirlik-onayla", "--run-id", run_id, "--actor", ACTOR, "--onayla"),
    )

    assert rc == cli.RC_REFUSED
    assert any("kanit" in satir.lower() for satir in satirlar)
    assert (
        await pkg_db.fetchval(
            "SELECT readiness_attestation FROM social.sector_package_runs "
            "WHERE run_id = $1",
            run_id,
        )
        is None
    )


async def test_aktive_et_kanit_degisince_operatore_NE_YAPACAGINI_soyler(pkg_db):
    """F1 kararının İKİNCİ yarısı: kapı yalnız DURMAZ, yeniden onaya ÇAĞIRIR.

    Ham `checklist_approved` reddi İKİ ayrı sebebi örter — tasdik hiç yok ya da
    onaydan sonra kanıt değişti. Operatör hangisi olduğunu görmezse karar
    ("dursun ve yeniden onay istesin") yarım kalır: komut "kapı kapalı" der ama
    ne yapacağını söylemez.
    """
    from .test_pipeline_writeback import _hazirlik_tasdiki
    from .test_readiness_checklist import _artefakt, _hazir_kosu

    run_id = await _hazir_kosu(pkg_db)
    await _hazirlik_tasdiki(pkg_db, run_id)
    # Onaydan SONRA kanıt kümesi büyür (tablo salt-eklemedir; erişilebilir
    # tek yön budur ve ölçüldü).
    await _artefakt(pkg_db, run_id, kind="research", model="arac-4", brief_ref="b")

    satirlar, rc = await cli.dispatch(
        pkg_db, _args("aktive-et", "--run-id", run_id, "--actor", ACTOR)
    )

    assert rc == cli.RC_REFUSED
    metin = " ".join(satirlar)
    assert "kanit kumesi degisti" in metin
    assert "hazirlik-onayla" in metin


async def test_aktive_et_BASKA_bir_kapi_dusunce_ham_hatayi_SAKLAMAZ(pkg_db):
    """Negatif kontrol: özel mesaj yalnız KANIT KAYMASINA aittir.

    Tasdik hiç yazılmamışsa sebep kayma DEĞİLDİR; o durumda komut kendi
    mesajını uydurmaz, alan hatasını olduğu gibi yüzeye bırakır. Aksi hâlde
    iki ayrı arıza tek mesajın altında birleşir.
    """
    from .test_readiness_checklist import _hazir_kosu

    run_id = await _hazir_kosu(pkg_db)  # hazırlık tasdiki YAZILMADI

    satirlar, rc = await cli.dispatch(
        pkg_db, _args("aktive-et", "--run-id", run_id, "--actor", ACTOR)
    )

    metin = " ".join(satirlar)
    assert rc == cli.RC_REFUSED          # alan hatası — dispatch zaten çevirir
    assert "GateNotSatisfied" in metin   # HAM hata yüzeyde
    assert "kanit kumesi degisti" not in metin
    assert "hazirlik-onayla" not in metin


# ─── 2b. Bağlantı dizesinin KANALI — argv değil (güvenlik review'ı S-3) ─────
#
# 2026-09-12 dual güvenlik review'ı: DSN zorunlu bir argv değeriydi. Argv gizli
# değildir — `/proc/<pid>/cmdline` bu makinede `hidepid` olmadan bağlı (ölçüldü),
# `ps` ve kabuk geçmişi de aynı değeri taşır. Kanal DEĞİŞTİ; korunan tasarım
# kararı "ortamdan sessiz miras YOK" aynen sürüyor (yukarıdaki test).


def test_raw_database_url_flag_is_rejected(capsys):
    """Eski bayrak SESSİZCE kaldırılmadı — kullanan operatöre sebebi söylenir.

    Tanımsız bırakmak "bilinmeyen argüman" derdi ve operatör bunu yazım hatası
    sanabilirdi; üstelik o koşumda değer ZATEN argv'ye yazılmış olurdu.
    """
    with pytest.raises(SystemExit) as cikis:
        cli.build_parser().parse_args(["--database-url", SAHTE_URL, "durum", "--run-id", "k-1"])

    assert cikis.value.code != 0
    hata = capsys.readouterr().err
    assert "--database-url-file" in hata and "--database-url-env" in hata
    assert "/proc" in hata, "sebep söylenmiyor — operatör neden değiştiğini bilmeli"


def test_dsn_file_must_not_be_readable_by_others(tmp_path, capsys):
    """Sırrı taşıyan dosya başkalarına açıksa kanal REDDEDER (fail-closed)."""
    dosya = tmp_path / "dsn.txt"
    dosya.write_text(SAHTE_URL, encoding="utf-8")
    dosya.chmod(0o644)

    parser = cli.build_parser()
    args = parser.parse_args(["--database-url-file", str(dosya), "durum", "--run-id", "k-1"])
    with pytest.raises(SystemExit):
        cli.dsn_coz(args, parser)

    assert "başkalarına açık" in capsys.readouterr().err


def test_dsn_file_channel_reads_the_value(tmp_path):
    """0600 dosya kabul edilir ve değer okunur — argv'de görünmez."""
    dosya = tmp_path / "dsn.txt"
    dosya.write_text(SAHTE_URL + "\n", encoding="utf-8")
    dosya.chmod(0o600)

    parser = cli.build_parser()
    args = parser.parse_args(["--database-url-file", str(dosya), "durum", "--run-id", "k-1"])

    assert cli.dsn_coz(args, parser) == SAHTE_URL


def test_dsn_env_channel_reads_the_named_variable(monkeypatch):
    """Değişkenin ADI verilir, değeri değil — `DATABASE_URL` sessizce okunmaz."""
    monkeypatch.setenv("OTOMAIX_TEST_DSN", SAHTE_URL)
    monkeypatch.setenv("DATABASE_URL", "postgresql://kacak@127.0.0.1:5432/yanlis")

    parser = cli.build_parser()
    args = parser.parse_args(
        ["--database-url-env", "OTOMAIX_TEST_DSN", "durum", "--run-id", "k-1"]
    )

    assert cli.dsn_coz(args, parser) == SAHTE_URL


def test_exactly_one_dsn_channel_is_required(tmp_path, capsys, monkeypatch):
    """Ne sıfır ne iki kanal — belirsizlik sessizce çözülmez."""
    parser = cli.build_parser()

    yok = parser.parse_args(["durum", "--run-id", "k-1"])
    with pytest.raises(SystemExit):
        cli.dsn_coz(yok, parser)
    assert "kanalı verilmedi" in capsys.readouterr().err

    dosya = tmp_path / "dsn.txt"
    dosya.write_text(SAHTE_URL, encoding="utf-8")
    dosya.chmod(0o600)
    monkeypatch.setenv("OTOMAIX_TEST_DSN", SAHTE_URL)
    ikisi = parser.parse_args(
        [
            "--database-url-file",
            str(dosya),
            "--database-url-env",
            "OTOMAIX_TEST_DSN",
            "durum",
            "--run-id",
            "k-1",
        ]
    )
    with pytest.raises(SystemExit):
        cli.dsn_coz(ikisi, parser)
    assert "tek kanal seçin" in capsys.readouterr().err
