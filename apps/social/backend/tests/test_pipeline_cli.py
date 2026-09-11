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
    return cli.build_parser().parse_args(["--database-url", SAHTE_URL, *argv])


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
        rc = cli.main(["--database-url", SAHTE_URL, komut, *_asgari_argumanlar(komut)])
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
    """
    monkeypatch.setenv("DATABASE_URL", "postgresql://kacak@127.0.0.1:5432/yanlis")

    with pytest.raises(SystemExit) as cikis:
        cli.build_parser().parse_args(["durum", "--run-id", "kosu-1"])

    assert cikis.value.code != 0
    assert "--database-url" in capsys.readouterr().err


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
