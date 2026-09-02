"""Migration 035 — takvim dönem desteği + üç takvim kalemi (plan Task 5).

Beş sözleşme burada pinlenir:

1. **Dönem temsili.** `social.public_holidays.end_date DATE NULL` — dolu ise kayıt
   bir DÖNEMdir (`date`..`end_date`), boş ise tek gündür. `UNIQUE(year, date)`
   KORUNUR: dönemin başlangıcı hâlâ benzersiz anahtardır.
2. **Ters dönem YOK.** `end_date IS NULL OR end_date >= date` bir CHECK kısıtıdır;
   yorumla değil veritabanıyla tutulur.
3. **Üç satırın değerleri OPERATÖR KARARIDIR** (2026-09-02, `331fe7a`) ve migration
   onları SABİT yazar. Bu dosya o değerleri harfiyen pinler — uygulama tarafı
   onları tek taraflı değiştiremez.
4. **Geri alma anlamı bozmaz.** `035_down.sql` YALNIZ migration'ın KENDİ yazdığı üç
   satırı siler; önceden var olan satırlara dokunmaz. Kolon düşerken sahibi 035
   OLMAYAN bir dönem satırı varsa geri alma REDDEDER — aksi hâlde o satır sessizce
   "tek günlük" bir kayda dönüşürdü (planın geri-alma hükmünün doğrudan karşılığı).
5. **Yıllık iş kanonik kaynaktır ve düzeltme hakkı ONUNDUR.** Mevcut
   `ON CONFLICT (year, date) DO UPDATE SET name_tr, name_en, category` davranışı
   AYNEN korunur; değişen tek şey güncellemenin dönem alanını SIFIRLAMAMASIDIR.

**Yıllık iş testleri workflow'un KENDİ JavaScript'ini koşar** (`node`, ağ kapalı).
Sözleşmeyi Python'da yeniden yazmak, ölçtüğünü sandığın şeyin taklidini ölçmek
olurdu: canlıya giden metin n8n düğümünün ürettiği metindir. `node` yoksa test
ATLANMAZ, DÜŞER — atlanan sözleşme ölçülmemiş sözleşmedir.
"""

from __future__ import annotations

import json
import subprocess
import uuid
from datetime import date

import asyncpg
import pytest

from app.routers import calendar as calendar_router
from app.services.sector_packages import normalize_special_day_key

from . import conftest as infra

MIGRATION_035 = infra.MIGRATIONS_DIR / "035_holiday_periods.sql"
ROLLBACK_035 = infra.MIGRATIONS_DIR / "rollback" / "035_down.sql"
CALENDAR_WORKFLOW = (
    infra.REPO_ROOT / "shared" / "n8n-workflows" / "turkey-calendar-update.json"
)

# ─── Operatör kararı (2026-09-02, `331fe7a`) — UYDURULMAZ ───────────────────
#
# (year, date, name_tr, name_en, category, end_date)
SEED_ROWS: tuple[tuple, ...] = (
    (
        2026,
        date(2026, 11, 10),
        "10 Kasım Atatürk'ü Anma Günü",
        "Atatürk Memorial Day",
        "national",
        None,
    ),
    (
        2026,
        date(2026, 11, 24),
        "24 Kasım Öğretmenler Günü",
        "Teachers' Day",
        "commercial",
        None,
    ),
    (
        2026,
        date(2026, 8, 15),
        "Okula Dönüş",
        "Back to School",
        "commercial",
        date(2026, 9, 15),
    ),
)

EXPECTED_KEYS = {
    "10-kasim-ataturk-u-anma-gunu",
    "24-kasim-ogretmenler-gunu",
    "okula-donus",
}

# Geri alma reddinin metinsel imzası — testler ret SEBEBİNİ de ölçer, yalnız
# sıfır-dışı çıkışı değil.
REFUSAL_MARKER = "migration 035 geri alma REDDEDILDI"

# Seed anahtarı DOLU olduğu için operatör kararının yazılamadığını duyuran NOTICE.
# Hata değildir: migration `rc=0` döner, `ON CONFLICT DO NOTHING` sözleşmesi durur.
SKIPPED_SEED_MARKER = "migration 035: takvim anahtari ZATEN DOLU"

# Seed manifestinin KENDİ paydasını doğrulayan kapının imzası (fix turu 2, N3).
MANIFEST_DENOMINATOR_MARKER = "seed manifesti"


# ─── psql yardımcıları (şema-yıkıcı yol: `otomaix_test_scratch`) ────────────


def _psql(url: str, *args: str) -> subprocess.CompletedProcess:
    argv, env = infra.psql_argv(url)
    return subprocess.run(argv + list(args), env=env, capture_output=True, text=True)


def _run_sql(url: str, sql: str) -> None:
    result = _psql(url, "-c", sql)
    assert result.returncode == 0, result.stderr


def _scalar(url: str, sql: str) -> str:
    result = _psql(url, "--tuples-only", "--no-align", "-c", sql)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def _apply_down(url: str) -> subprocess.CompletedProcess:
    """`035_down.sql`i sarmalayıcı transaction OLMADAN uygular.

    Sarmalamıyoruz: "hiçbir değişiklik yapmadan reddetti" iddiası ROLLBACK'in
    gizlediği bir sonuç değil, veritabanının kalıcı durumundan okunur.
    """
    return _psql(url, "-f", str(ROLLBACK_035))


def _apply_up(
    url: str, *, env_extra: dict[str, str] | None = None, sql_file=None
) -> subprocess.CompletedProcess:
    """035'i dağıtım runner'ının anlambilimiyle (tek transaction) uygular."""
    argv, env = infra.psql_argv(url)
    if env_extra:
        env = {**env, **env_extra}
    return subprocess.run(
        argv + ["--single-transaction", "-f", str(sql_file or MIGRATION_035)],
        env=env,
        capture_output=True,
        text=True,
    )


def _apply_up_unwrapped(url: str, *, error_stop: bool) -> subprocess.CompletedProcess:
    """035'i SARMALAYICI TRANSACTION OLMADAN uygular — operatörün elle koştuğu biçim.

    Deponun kendi elle-uygulama alışkanlığı çıplak `psql -f`tir
    (`docs/_archive/01-social-phase1.md:195` · `07-social-template-system.md:752` ·
    `docs/archive/CLAUDE_crm_pre_cleanup.md:212`). Atılabilir-veritabanı kapısı
    korunur, yalnız `ON_ERROR_STOP` bayrağı isteğe göre düşürülür.
    """
    argv, env = infra.psql_argv(url)
    if not error_stop:
        flag = argv.index("-v")
        argv = argv[:flag] + argv[flag + 2 :]
    return subprocess.run(
        argv + ["-f", str(MIGRATION_035)], env=env, capture_output=True, text=True
    )


def _names(url: str) -> set[str]:
    raw = _scalar(url, "SELECT name_tr FROM social.public_holidays ORDER BY date, name_tr")
    return {line for line in raw.splitlines() if line}


def _has_end_date_column(url: str) -> bool:
    return _scalar(
        url,
        "SELECT count(*) FROM information_schema.columns WHERE table_schema = 'social' "
        "AND table_name = 'public_holidays' AND column_name = 'end_date'",
    ) == "1"


# ─── n8n düğümünü GERÇEKTEN koşan yardımcı ─────────────────────────────────


_NODE_HARNESS = r"""
const fs = require('fs');
const [wfPath, nodeName, itemsJson, nowYear] = process.argv.slice(1);
const wf = JSON.parse(fs.readFileSync(wfPath, 'utf8'));
const node = wf.nodes.find((n) => n.name === nodeName);
if (!node) { throw new Error('dugum yok: ' + nodeName); }
const items = JSON.parse(itemsJson).map((j) => ({ json: j }));
const $input = { all: () => items };
// Düğümün kendi günlüğü ÖLÇÜMÜ kirletmesin (stdout tek çıktı kanalı).
console.log = () => {};
// Ağ KAPALI: dış servise bağımlı bir test ölçüm değil, kumar olurdu. Düğümün
// kendi try/catch'i bu hatayı zaten yutuyor — statik kalemler yine üretilir.
globalThis.fetch = async () => { throw new Error('ag kapali (olcum)'); };
// SAHTE SAAT: yıllık iş "içinde bulunduğu yılı" `new Date().getFullYear()` ile
// okur. Bir sonraki yılın satırlarını ÜRETİCİNİN KENDİSİNE ürettirmenin tek
// yolu saati kaydırmaktır — yıl numarasını elle metne gömmek, üreticinin
// yazdığı satırı değil onun taklidini ölçerdi. YALNIZ argümansız `new Date()`
// kaydırılır; `new Date(yr, ay, gun)` biçimleri aynen gerçek Date'e gider.
if (nowYear) {
  const RealDate = Date;
  const fixed = RealDate.UTC(Number(nowYear), 5, 15, 12, 0, 0);
  class FakeDate extends RealDate {
    constructor(...args) {
      if (args.length === 0) { super(fixed); } else { super(...args); }
    }
    static now() { return fixed; }
  }
  globalThis.Date = FakeDate;
}
const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const fn = new AsyncFunction('$input', node.parameters.jsCode);
fn($input).then((out) => {
  process.stdout.write(JSON.stringify(out.map((o) => o.json)));
});
"""


def _run_workflow_node(
    node_name: str, items: list[dict] | None = None, now_year: int | None = None
) -> list[dict]:
    """Takvim workflow'unun bir Code düğümünü node ile koşar, çıktısını döner."""
    result = subprocess.run(
        [
            "node",
            "-e",
            _NODE_HARNESS,
            str(CALENDAR_WORKFLOW),
            node_name,
            json.dumps(items or [], ensure_ascii=False),
            "" if now_year is None else str(now_year),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"düğüm koşumu DURDU ({node_name}):\n{result.stderr}"
    )
    return json.loads(result.stdout)


def _annual_job_sql(items: list[dict]) -> str:
    """Yıllık işin veritabanına GÖNDERDİĞİ metnin ta kendisi."""
    out = _run_workflow_node("SQL Oluştur", items)
    assert len(out) == 1, out
    return out[0]["sql"]


# ─── 1. Kolon + kısıt ───────────────────────────────────────────────────────


async def test_end_date_column_exists_and_nullable(db):
    """`end_date` DATE ve NULL'lanabilir — boş olmak "tek gün" demektir.

    NOT NULL olsaydı her tek günlük satır kendi bitişini taşımak zorunda kalırdı
    ve "dönem mi tek gün mü" ayrımı veriden okunamazdı.
    """
    row = await db.fetchrow(
        "SELECT data_type, is_nullable, column_default FROM information_schema.columns "
        "WHERE table_schema = 'social' AND table_name = 'public_holidays' "
        "AND column_name = 'end_date'"
    )
    assert row is not None, "`end_date` kolonu YOK"
    assert row["data_type"] == "date", row["data_type"]
    assert row["is_nullable"] == "YES", row["is_nullable"]
    assert row["column_default"] is None, (
        f"`end_date` varsayılan taşıyor ({row['column_default']}) — tek günlük "
        "satırlar sessizce dönem olurdu"
    )


async def test_check_rejects_end_before_start(db):
    """`end_date >= date` KISIT'tır — ters dönem veritabanına giremez.

    Üç ayaklı ölçüm: geriye dönük REDDEDİLİR · aynı gün KABUL (tek günlük dönem
    meşrudur) · ileri tarih KABUL. Tek ayak ölçülseydi "her şeyi reddeden" bir
    kısıt da yeşil görünürdü.
    """
    async def _insert(day: date, end: date | None):
        nested = db.transaction()
        await nested.start()
        try:
            await db.execute(
                "INSERT INTO social.public_holidays (year, date, name_tr, end_date) "
                "VALUES (2099, $1, $2, $3)",
                day,
                f"probe-{uuid.uuid4().hex[:8]}",
                end,
            )
        finally:
            await nested.rollback()

    with pytest.raises(asyncpg.exceptions.CheckViolationError) as excinfo:
        await _insert(date(2099, 5, 10), date(2099, 5, 9))
    assert "end_date" in str(excinfo.value), str(excinfo.value)

    await _insert(date(2099, 5, 11), date(2099, 5, 11))  # aynı gün — tek günlük dönem
    await _insert(date(2099, 5, 12), date(2099, 6, 12))  # ileri bitiş
    await _insert(date(2099, 5, 13), None)  # tek gün


async def test_period_row_roundtrip(db, monkeypatch):
    """Dönem satırı yazılır ve TAKVİM UCUNDAN dönem alanıyla birlikte okunur.

    Roundtrip yalnız kolonu değil TÜKETİCİYİ de ölçer: `get_holidays` SELECT
    listesine `end_date` girmezse kolon var ama önyüze hiç ulaşmaz — şema
    değişmiş, davranış değişmemiş olurdu.

    Önbellek BİLEREK devre dışı: `get_cached` süreçler arası yaşayan bir Redis
    anahtarıdır ve testin gördüğü şey önceki koşumun kalıntısı olabilirdi
    (rollback edilen transaction Redis'i geri almaz).
    """
    monkeypatch.setattr(calendar_router, "get_cached", lambda key: _none())
    monkeypatch.setattr(calendar_router, "set_cached", lambda key, value, ttl: _noop())

    await db.execute(
        "INSERT INTO social.public_holidays (year, date, name_tr, name_en, category, end_date) "
        "VALUES (4242, '4242-08-15'::date, 'Deneme Dönemi', 'Probe Period', 'commercial', "
        "'4242-09-15'::date)"
    )
    await db.execute(
        "INSERT INTO social.public_holidays (year, date, name_tr, name_en, category) "
        "VALUES (4242, '4242-10-29'::date, 'Deneme Günü', 'Probe Day', 'national')"
    )

    response = await calendar_router.get_holidays(year=4242, user={"id": "t"}, db=db)
    data = {row["name_tr"]: row for row in response.data}

    assert set(data) == {"Deneme Dönemi", "Deneme Günü"}
    assert data["Deneme Dönemi"]["end_date"] == date(4242, 9, 15), (
        "takvim ucu dönem alanını DÖNMÜYOR — kolon önyüze ulaşmıyor"
    )
    assert data["Deneme Günü"]["end_date"] is None, (
        "tek günlük satır dönem alanı taşıyor"
    )


async def _none():
    return None


async def _noop():
    return None


# ─── 2. Üç yeni satır ───────────────────────────────────────────────────────


async def test_three_new_rows_present_and_normalize(db):
    """Üç satır operatörün verdiği değerlerle DURUYOR ve anahtarları benzersiz.

    İki ayrı iddia tek testte, çünkü ikincisi birincisiz anlamsız: anahtar
    benzersizliği ancak adlar SABİTSE bir şey söyler.

    `normalize_special_day_key` bu testte YALNIZ ÇAĞRILIR — davranışı bu görevde
    DEĞİŞMEZ; eşleşme ada dayanır, tarihe değil, yani dönem desteği paket
    eşleşmesini etkilemez.
    """
    for year, day, name_tr, name_en, category, end_date in SEED_ROWS:
        row = await db.fetchrow(
            "SELECT year, date, name_tr, name_en, category, end_date "
            "FROM social.public_holidays WHERE year = $1 AND date = $2",
            year,
            day,
        )
        assert row is not None, f"seed satırı YOK: {name_tr}"
        assert tuple(row) == (year, day, name_tr, name_en, category, end_date), (
            f"seed satırı operatör kararından SAPTI: {tuple(row)!r}"
        )

    assert {normalize_special_day_key(r[2]) for r in SEED_ROWS} == EXPECTED_KEYS

    all_names = [
        r["name_tr"]
        for r in await db.fetch(
            "SELECT name_tr FROM social.public_holidays WHERE name_tr IS NOT NULL"
        )
    ]
    keys = [normalize_special_day_key(name) for name in all_names]
    assert len(keys) == len(set(keys)), (
        "takvimde ÇAKIŞAN özel gün anahtarı var — paket eşleşmesi belirsizleşir: "
        + repr(sorted(k for k in keys if keys.count(k) > 1))
    )
    assert EXPECTED_KEYS <= set(keys)


# ─── 3. Geri alma sahipliği ────────────────────────────────────────────────


def test_rollback_removes_migration_owned_seed_rows(scratch_db_migrated):
    """Geri alma 035'in KENDİ yazdığı üç satırı kaldırır ve kolonu düşürür."""
    url = scratch_db_migrated
    before = _names(url)
    assert {r[2] for r in SEED_ROWS} <= before

    result = _apply_down(url)
    assert result.returncode == 0, f"geri alma DURDU:\n{result.stderr}"

    after = _names(url)
    assert not ({r[2] for r in SEED_ROWS} & after), (
        f"035'in satırları duruyor: {sorted({r[2] for r in SEED_ROWS} & after)}"
    )
    assert not _has_end_date_column(url), "`end_date` kolonu geri alınmadı"


def test_rollback_preserves_pre_existing_rows(scratch_db_migrated):
    """035 ÖNCESİNDE var olan satırlar geri almadan sağ çıkar.

    İki sınıf ayrı ayrı ölçülür: (a) migration seed'inin dokunmadığı satırlar,
    (b) 035'in üç anahtarından BİRİNDE oturan, migration'dan ÖNCE yazılmış satır.

    (b) satırı GERÇEKTEN önce yaratılır — 035 geri alınır, satır yazılır, 035
    yeniden uygulanır. İlk yazımda bu satır 035'in yazdığı satırı `UPDATE`
    ederek üretiliyordu; o senaryo "içeriği kaymış satır" senaryosuydu ve
    docstring'in söylediği şeyi ölçmüyordu (bağımsız hakem yakaladı). O ayrı
    iddia artık kendi testinde: `test_rollback_spares_a_content_drifted_seed_row`.
    """
    url = scratch_db_migrated
    _run_sql(
        url,
        "INSERT INTO social.public_holidays (year, date, name_tr, name_en, category) "
        "VALUES (2030, '2030-06-01', 'Onceden Var Olan', 'Pre Existing', 'commercial')",
    )

    # (b) — 035'i geri al, anahtarı BAŞKASI doldursun, 035'i yeniden uygula.
    # `ON CONFLICT DO NOTHING` o satırı gerçekten atlar; sahibi 035 değildir.
    assert _apply_down(url).returncode == 0
    _run_sql(
        url,
        "INSERT INTO social.public_holidays (year, date, name_tr, name_en, category) "
        "VALUES (2026, '2026-11-24', 'Baskasinin Yazdigi', 'Someone Elses Row', 'national')",
    )
    reapply = _apply_up(url)
    assert reapply.returncode == 0, f"yeniden uygulama DURDU:\n{reapply.stderr}"

    result = _apply_down(url)
    assert result.returncode == 0, f"geri alma DURDU:\n{result.stderr}"

    after = _names(url)
    assert "Onceden Var Olan" in after, "önceden var olan satır SİLİNDİ"
    assert "Baskasinin Yazdigi" in after, (
        "035'in YAZMADIĞI bir satır, yalnız anahtarı çakıştığı için silindi — "
        "sahiplik sınırı ihlali"
    )
    assert "Yılbaşı" in after, "002 seed'i silindi"


def test_rollback_spares_a_content_drifted_seed_row(scratch_db_migrated):
    """035'in yazdığı satırın içeriği SONRADAN kaydıysa artık 035'in değildir.

    Takvim beslemesinin ad/kategori düzeltme hakkı vardır (`DO UPDATE`); o
    düzeltmeden sonra satır operatör kararının birebir kopyası olmaktan çıkar.
    Geri alma beş alan eşitliğine baktığı için satırı BIRAKIR — bu bilinçlidir
    ve `035_down.sql`in sahiplik bölümünde yazılıdır.

    Bu, üstteki testten FARKLI bir iddiadır (o: hiç yazılmamış satır; bu:
    yazılmış ama kaymış satır) ve o yüzden ayrı isim taşır.
    """
    url = scratch_db_migrated
    _run_sql(
        url,
        "UPDATE social.public_holidays SET name_tr = 'Yerel Duzeltme' "
        "WHERE year = 2026 AND date = '2026-11-24'",
    )

    result = _apply_down(url)
    assert result.returncode == 0, f"geri alma DURDU:\n{result.stderr}"

    after = _names(url)
    assert "Yerel Duzeltme" in after, (
        "içeriği kaymış satır silindi — geri alma anahtara göre siliyor demektir"
    )


def test_rollback_refuses_when_a_foreign_period_row_exists(scratch_db_migrated):
    """Sahibi 035 OLMAYAN bir dönem satırı varsa geri alma HİÇBİR ŞEY yapmadan durur.

    Gerekçe planın kendi geri-alma hükmüdür: kolon düşünce dönem satırı "035
    öncesinde var olmayan" bir hâle, tek günlük bir kayda dönüşürdü. 035'in
    kendi üç satırı için bu bedel bilinçlidir (onları zaten siliyoruz); BAŞKA
    birinin dönem satırı için değildir — o sessiz bir anlam kaybı olurdu.
    """
    url = scratch_db_migrated
    _run_sql(
        url,
        "INSERT INTO social.public_holidays (year, date, name_tr, name_en, category, end_date) "
        "VALUES (2030, '2030-07-01', 'Yabanci Donem', 'Foreign Period', 'commercial', "
        "'2030-07-20')",
    )

    result = _apply_down(url)

    assert result.returncode != 0, (
        f"yabancı dönem satırı sessizce tek güne dönüştü — stdout:\n{result.stdout}"
    )
    assert REFUSAL_MARKER in result.stderr, result.stderr
    assert _has_end_date_column(url), "reddeden koşum kolonu yine de düşürdü"
    assert {r[2] for r in SEED_ROWS} <= _names(url), (
        "reddeden koşum seed satırlarını yine de sildi — 'hiçbir şey yapmadan durur' YALAN"
    )


def test_rollback_runs_after_the_annual_job_wrote_a_later_year_period(scratch_db_migrated):
    """Geri alma, KENDİ üreticisinin yazdığı sonraki yıl dönemine TAKILMAZ.

    Ölçülen arıza (bağımsız hakem, Q1): yabancı-dönem kapısının muafiyeti
    2026'ya çivilenmişti. Oysa aynı commit'in gönderdiği yıllık iş `Okula
    Dönüş`ü KOŞTUĞU YILA göre yazar (`${year}-08-15`..`${year}-09-15`). 1 Ocak
    2027'de iş 2027 dönem satırını yazar; o satır tanım gereği "yabancı dönem"
    olur ve geri alma o günden sonra bir operatör elle `end_date` boşaltana
    kadar REDDEDER. Kapı, korumaya çalıştığı migration'ın kendi üreticisi
    tarafından bir takvim yılı içinde tetikleniyordu.

    Sonraki yılın satırı ÜRETİCİYE ürettirilir (sahte saat), elle yazılmaz —
    yoksa üreticinin yazdığı satırı değil onun taklidini ölçerdik.

    Muafiyetin BEDELİ dürüstçe ölçülür: üreticinin satırı SİLİNMEZ (035 onun
    sahibi değil), ama kolon düştüğü için dönem bilgisi gider. Bu geri
    alınabilir bir kayıptır — üretici bir sonraki turunda dönemi yeniden yazar
    ve geri alma zaten workflow'un önceki sürümüne dönmeyi de kapsar.
    """
    from datetime import datetime

    url = scratch_db_migrated
    next_year = datetime.now().year + 1

    items = _run_workflow_node("Tatilleri Topla", now_year=next_year)
    period = [item for item in items if item["name_tr"] == "Okula Dönüş"]
    assert period, "üretici dönem kalemini hiç üretmedi (prob bozuk)"
    assert period[0]["date"] == f"{next_year}-08-15", period[0]
    assert period[0]["end_date"] == f"{next_year}-09-15", period[0]

    _run_sql(url, _annual_job_sql(items))
    assert (
        _scalar(
            url,
            "SELECT end_date FROM social.public_holidays "
            f"WHERE year = {next_year} AND date = '{next_year}-08-15'",
        )
        == f"{next_year}-09-15"
    ), "üreticinin dönem satırı veritabanına hiç girmedi (prob bozuk)"

    result = _apply_down(url)

    assert result.returncode == 0, (
        "geri alma KENDİ üreticisinin yazdığı satıra takıldı:\n" + result.stderr
    )
    assert not _has_end_date_column(url)
    assert (
        _scalar(
            url,
            "SELECT count(*) FROM social.public_holidays "
            f"WHERE year = {next_year} AND date = '{next_year}-08-15'",
        )
        == "1"
    ), "geri alma üreticinin satırını SİLDİ — sahiplik sınırı ihlali"
    assert (
        _scalar(
            url,
            "SELECT count(*) FROM social.public_holidays "
            "WHERE year = 2026 AND date = '2026-08-15'",
        )
        == "0"
    ), "035 kendi seed satırını kaldırmadı"


def test_up_down_up_on_mixed_row_set(scratch_db_migrated):
    """KARIŞIK küme üstünde up → down → up döngüsü anlamı korur.

    Karışık = 002 seed'i + 035'in üç satırı + sonradan eklenmiş bir satır.
    Döngü sonunda üçünün de aynı anda ayakta olması gerekir; ara adımda
    yalnız 035'in sahip olduğu kısım kaybolur.
    """
    url = scratch_db_migrated
    _run_sql(
        url,
        "INSERT INTO social.public_holidays (year, date, name_tr, name_en, category) "
        "VALUES (2031, '2031-06-01', 'Karisik Kume Satiri', 'Mixed Row', 'commercial')",
    )
    owned = {r[2] for r in SEED_ROWS}
    foreign = {"Yılbaşı", "Karisik Kume Satiri"}
    assert (owned | foreign) <= _names(url)

    down = _apply_down(url)
    assert down.returncode == 0, f"geri alma DURDU:\n{down.stderr}"
    mid = _names(url)
    assert not (owned & mid)
    assert foreign <= mid
    assert not _has_end_date_column(url)

    up = _apply_up(url)
    assert up.returncode == 0, f"yeniden uygulama DURDU:\n{up.stderr}"
    end = _names(url)
    assert owned <= end, "yeniden uygulama seed satırlarını geri getirmedi"
    assert foreign <= end, "yeniden uygulama yabancı satırları kaybetti"
    assert _has_end_date_column(url)
    assert (
        _scalar(
            url,
            "SELECT end_date FROM social.public_holidays "
            "WHERE year = 2026 AND date = '2026-08-15'",
        )
        == "2026-09-15"
    ), "okula dönüş satırı dönem bilgisi OLMADAN geri geldi"


def test_seed_reports_when_a_key_is_already_occupied(scratch_db_migrated):
    """Anahtar DOLUYSA migration bunu SÖYLER — sessizce atlamaz.

    Ölçülen boşluk (bağımsız hakem, Q2): seed `ON CONFLICT DO NOTHING` ile
    yazılıyor ve fail-closed doğrulama yalnız üç anahtarın VAR OLDUĞUNU
    ölçüyordu. Hedef veritabanı o anahtarlardan birini zaten tutuyorsa migration
    BAŞARILI rapor ediyor, operatör kararındaki değerler hiç yazılmıyor ve kimse
    haberdar olmuyordu — ekin en sert hükmü ("migration BU DEĞERLERİ SABİT
    yazar") tam da önemli olduğu vakada ölçüsüz kalıyordu.

    Sözleşme DEĞİŞMEZ (`DO NOTHING` durur, ad/kategori düzeltme hakkı takvim
    beslemesinindir); değişen şey atlamanın GÖRÜNÜR olmasıdır: NOTICE, hata
    değil. Migration yine `rc=0` döner.
    """
    url = scratch_db_migrated

    assert _apply_down(url).returncode == 0
    _run_sql(
        url,
        "INSERT INTO social.public_holidays (year, date, name_tr, name_en, category) "
        "VALUES (2026, '2026-11-10', 'Baskasinin Satiri', 'Someone Elses Row', 'commercial')",
    )

    result = _apply_up(url)

    assert result.returncode == 0, f"migration DURDU:\n{result.stderr}"
    assert SKIPPED_SEED_MARKER in result.stderr, (
        "dolu anahtar SESSİZCE atlandı — operatör kararı yazılmadı ve kimse "
        f"haberdar olmadı. stderr:\n{result.stderr}"
    )
    assert "2026-11-10" in result.stderr, result.stderr

    # Mevcut satır EZİLMEDİ (DO NOTHING sözleşmesi korunuyor).
    assert (
        _scalar(
            url,
            "SELECT name_tr FROM social.public_holidays "
            "WHERE year = 2026 AND date = '2026-11-10'",
        )
        == "Baskasinin Satiri"
    )
    # Boş olan iki anahtara operatör kararı YAZILDI.
    assert {"24 Kasım Öğretmenler Günü", "Okula Dönüş"} <= _names(url)


@pytest.mark.parametrize(
    "error_stop, label",
    [
        (False, "çıplak `psql -f` (bayraksız)"),
        (True, "`-v ON_ERROR_STOP=1`, sarmalayıcı YOK"),
    ],
    ids=["ciplak", "on_error_stop"],
)
def test_bare_psql_apply_is_complete(scratch_db_migrated, error_stop: bool, label: str):
    """SARMALANMAMIŞ `psql -f` de migration'ı TAM uygular — yarım bırakmaz.

    Ölçülen gerileme (fix turu 2, N1 — **bu yürütmenin kendi ürünü**, devralınan
    borç değil): M1 düzeltmesi seed manifestini `CREATE TEMP TABLE …
    ON COMMIT DROP` ile kurdu. Bu dosya KENDİ transaction'ını taşımaz; autocommit
    altında her deyim kendi transaction'ıdır, yani manifest KENDİ `CREATE`inin
    commit'inde düşer ve sonraki her deyim onu bulamaz.

    Ölçüldü (düzeltmeden önce, taze scratch veritabanı):
      * çıplak: `rc=0`, stderr'de `relation "m035_seed" does not exist`,
        kolon + CHECK commit edilmiş, **0 seed satırı** — ve hata fail-closed
        garanti bloğunun İÇİNDE de tekrarlandığı için tam da bunu yakalaması
        gereken kapı hiç değerlendirilemedi. Fail-OPEN: yarım şema, sıfır seed,
        çıkış 0.
      * `ON_ERROR_STOP=1` ama sarmalayıcısız: `rc=3`, yine 0 seed satırı,
        kolon commit edilmiş.

    Bugünkü onaylı yolların hepsi dosyayı sarmalıyor (`run-migrations.sh` ·
    `conftest._apply_migrations` · plan Task 18 Adım 1-2), ama deponun elle
    uygulama alışkanlığı çıplak biçimdir ve yeni arıza SESSİZDİR. İki
    sarmalanmamış biçim de burada ölçülür — sınıf kapatılır, tek varyant değil.
    """
    url = scratch_db_migrated
    assert _apply_down(url).returncode == 0, "ön koşul: 035 geri alınamadı"

    result = _apply_up_unwrapped(url, error_stop=error_stop)

    assert "ERROR" not in result.stderr, (
        f"{label}: migration hata bastı — yarım uygulama:\n{result.stderr}"
    )
    assert result.returncode == 0, f"{label}: rc={result.returncode}\n{result.stderr}"
    assert _has_end_date_column(url), f"{label}: kolon uygulanmadı"
    assert {row[2] for row in SEED_ROWS} <= _names(url), (
        f"{label}: seed satırları YAZILMADI — şema ilerledi, veri ilerlemedi"
    )


def test_seed_report_survives_a_hostile_client_min_messages(scratch_db_migrated):
    """Atlama uyarısı `client_min_messages` kısılmışken de GÖRÜNÜR.

    Ölçülen boşluk (fix turu 2, N2): Q2'nin tüm görünürlüğü bir NOTICE'e
    dayanıyor ve NOTICE'in yayınlanıp yayınlanmayacağını bu depoda YAŞAMAYAN bir
    ayar belirliyor. Ölçüldü: sunucu varsayılanı `notice` ve mesaj çıkıyor; ama
    `PGOPTIONS='-c client_min_messages=warning'` altında AYNI `RAISE NOTICE`
    boş stderr + `rc=0` üretiyor. Rol ya da veritabanı düzeyinde
    `ALTER … SET client_min_messages='warning'` sıradan bir üretim
    sıkılaştırmasıdır — yani kapattığımız Q2 koşulu, kontrol etmediğimiz bir
    ortam tarafından sessizce geri açılabilirdi.

    Bu test o ortamı taklit eder ve uyarının yine de çıkmasını ister.
    """
    url = scratch_db_migrated

    assert _apply_down(url).returncode == 0
    _run_sql(
        url,
        "INSERT INTO social.public_holidays (year, date, name_tr, name_en, category) "
        "VALUES (2026, '2026-11-10', 'Baskasinin Satiri', 'Someone Elses Row', 'commercial')",
    )

    result = _apply_up(
        url, env_extra={"PGOPTIONS": "-c client_min_messages=warning"}
    )

    assert result.returncode == 0, f"migration DURDU:\n{result.stderr}"
    assert SKIPPED_SEED_MARKER in result.stderr, (
        "düşman `client_min_messages` altında atlama uyarısı KAYBOLDU — Q2'nin "
        f"düzeltmesi bir ortam değişkeniyle kapatılabiliyor. stderr:\n{result.stderr!r}"
    )


def test_guarantee_block_asserts_its_own_denominator(scratch_db_migrated, tmp_path):
    """Garanti bloğu KENDİ paydasını doğrular — boş manifestle sessizce geçmez.

    Ölçülen zayıflık (fix turu 2, N3): M1'den önce anahtar doğrulaması boş
    olamayacak bir literal `VALUES` listesi üzerinde dönüyordu; sonra
    `FROM m035_seed` oldu. Manifest boşsa blok hiçbir sorun bulamaz ve migration
    HİÇBİR ŞEY seed etmemiş olarak "başarılı" raporlar. Sarmalayıcı transaction
    altında boş manifeste giden bir yol ÖLÇÜLMEDİ (hakem dürüstçe "erişilebilirliği
    ölçülmedi" etiketi koydu) — ama veriye dayalı bir payda kendini doğrulamalıdır,
    yoksa garanti boş kümede vakuum olarak sağlanır.

    Pozitif kontrol: manifest INSERT'i çıkarılmış bir KOPYA koşulur. Kapı yoksa
    o kopya `rc=0` ile geçer; kapı varsa DURur.
    """
    url = scratch_db_migrated
    source = MIGRATION_035.read_text(encoding="utf-8")
    start = source.index("INSERT INTO m035_seed")
    end = source.index(";", start) + 1
    decoy = tmp_path / "035_bos_manifest.sql"
    decoy.write_text(source[:start] + source[end:], encoding="utf-8")

    assert _apply_down(url).returncode == 0
    result = _apply_up(url, sql_file=decoy)

    assert result.returncode != 0, (
        "boş manifestli migration sessizce GEÇTİ — payda kendini doğrulamıyor. "
        f"stdout:\n{result.stdout}"
    )
    assert MANIFEST_DENOMINATOR_MARKER in result.stderr, result.stderr
    assert not _has_end_date_column(url), (
        "reddeden koşum şemayı yine de ilerletti (tek transaction bekleniyordu)"
    )


def test_reseeding_is_conflict_free():
    """035 ikinci kez uygulanınca çakışmaz ve satırları ikizlemez.

    Dağıtım gerçeği: runner tüm migration'ları her koşumda uygular. Seed bloğu
    `ON CONFLICT` taşımasaydı ikinci koşum `UNIQUE(year, date)` ile DURur ve
    ondan sonraki hiçbir migration uygulanmazdı.

    İzolasyon: `BEGIN … ROLLBACK` (Postgres'te DDL transactional'dır) — oturum
    veritabanının şeması değişmez.
    """
    argv, env = infra.psql_argv(infra._require_test_database(infra.test_database_url()))
    script = (
        "BEGIN;\n"
        f"\\i {MIGRATION_035}\n"
        "SELECT count(*) AS seed_rows FROM social.public_holidays "
        "WHERE (year, date) IN ((2026, '2026-11-10'), (2026, '2026-11-24'), "
        "(2026, '2026-08-15'));\n"
        "ROLLBACK;\n"
    )
    result = subprocess.run(argv, input=script, env=env, capture_output=True, text=True)

    assert result.returncode == 0, f"yeniden uygulama DURDU:\n{result.stderr}"
    assert "3" in result.stdout.split("seed_rows")[-1], (
        f"seed satırları ikizlendi ya da kayboldu — çıktı:\n{result.stdout}"
    )
    # Atlama uyarısının KARŞI ayağı: üç satır da yerinde ve içerikleri operatör
    # kararıyla aynıysa uyarı ÇIKMAZ. Bu ayak olmadan uyarı "her koşumda bağıran"
    # bir gürültü olabilirdi ve hiçbir şey ölçmezdi.
    assert SKIPPED_SEED_MARKER not in result.stderr, (
        f"temiz yeniden uygulama atlama uyarısı bastı:\n{result.stderr}"
    )


# ─── 4. Yıllık n8n işi ──────────────────────────────────────────────────────


def test_annual_job_emits_the_three_new_items():
    """Yıllık iş üç kalemi KENDİSİ üretir — 2027 satırları migration'dan gelmez.

    Migration yalnız 2026'yı yazar (`new Date().getFullYear()` ölçüldü: iş
    yalnız içinde bulunduğu yılı yazar). Üç kalem yıllık işe İŞLENMEZSE takvim
    2027'de sessizce eksilirdi.
    """
    from datetime import datetime

    year = datetime.now().year
    emitted = {item["name_tr"]: item for item in _run_workflow_node("Tatilleri Topla")}

    for _, _, name_tr, name_en, category, end_date in SEED_ROWS:
        assert name_tr in emitted, f"yıllık iş '{name_tr}' kalemini üretmiyor"
        item = emitted[name_tr]
        assert item["name_en"] == name_en, item
        assert item["category"] == category, item
        assert item["year"] == year, item

    assert emitted["10 Kasım Atatürk'ü Anma Günü"]["date"] == f"{year}-11-10"
    assert emitted["24 Kasım Öğretmenler Günü"]["date"] == f"{year}-11-24"
    assert emitted["Okula Dönüş"]["date"] == f"{year}-08-15"
    assert emitted["Okula Dönüş"].get("end_date") == f"{year}-09-15", (
        "okula dönüş kalemi dönem bitişi TAŞIMIYOR — yıllık işten tek günlük doğar"
    )
    assert emitted["10 Kasım Atatürk'ü Anma Günü"].get("end_date") is None
    assert emitted["24 Kasım Öğretmenler Günü"].get("end_date") is None


async def test_annual_job_still_corrects_name_and_category(db):
    """Ezme davranışı AYNEN korunur — takvim beslemesi kanonik kaynaktır.

    İlk yazım "mevcut satırı ezme" diyordu; ÖLÇÜM canlı işin ad/kategori
    düzeltmelerini bilinçli olarak uyguladığını gösterdi. Bu kapı o hakkı
    korur: dönem desteği düzeltme yolunu KAPATMAMALIDIR.
    """
    await db.execute(
        "INSERT INTO social.public_holidays (year, date, name_tr, name_en, category) "
        "VALUES (2099, '2099-05-05'::date, 'Yanlis Ad', 'Wrong Name', 'national')"
    )

    sql = _annual_job_sql([
        {
            "year": 2099,
            "date": "2099-05-05",
            "name_tr": "Doğru Ad",
            "name_en": "Right Name",
            "category": "commercial",
        }
    ])
    await db.execute(sql)

    row = await db.fetchrow(
        "SELECT name_tr, name_en, category FROM social.public_holidays "
        "WHERE year = 2099 AND date = '2099-05-05'::date"
    )
    assert tuple(row) == ("Doğru Ad", "Right Name", "commercial"), tuple(row)


async def test_annual_job_update_preserves_period_field(db):
    """Yıllık işin güncellemesi dönem alanını SIFIRLAMAZ.

    Kural "ezme" değil, "ezerken dönemi düşürme"dir. İki yön de ölçülür:
    dönem taşımayan bir kalem mevcut dönemi KORUR, dönem taşıyan bir kalem onu
    DÜZELTİR — aksi hâlde iş kendi dönem kalemini hiç güncelleyemezdi.
    """
    await db.execute(
        "INSERT INTO social.public_holidays "
        "(year, date, name_tr, name_en, category, end_date) "
        "VALUES (2099, '2099-08-15'::date, 'Okula Dönüş', 'Back to School', "
        "'commercial', '2099-09-15'::date)"
    )

    # (a) dönem taşımayan kalem — mevcut dönem KORUNUR
    await db.execute(
        _annual_job_sql([
            {
                "year": 2099,
                "date": "2099-08-15",
                "name_tr": "Okula Dönüş",
                "name_en": "Back to School",
                "category": "commercial",
            }
        ])
    )
    assert await db.fetchval(
        "SELECT end_date FROM social.public_holidays "
        "WHERE year = 2099 AND date = '2099-08-15'::date"
    ) == date(2099, 9, 15), "yıllık iş güncellemesi dönem alanını SIFIRLADI"

    # (b) dönem taşıyan kalem — dönem DÜZELTİLİR
    await db.execute(
        _annual_job_sql([
            {
                "year": 2099,
                "date": "2099-08-15",
                "name_tr": "Okula Dönüş",
                "name_en": "Back to School",
                "category": "commercial",
                "end_date": "2099-09-20",
            }
        ])
    )
    assert await db.fetchval(
        "SELECT end_date FROM social.public_holidays "
        "WHERE year = 2099 AND date = '2099-08-15'::date"
    ) == date(2099, 9, 20), "yıllık iş kendi dönem kalemini düzeltemiyor"
