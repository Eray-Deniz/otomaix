"""DDL nesne kimliği — depo GENELİNDEKİ sınıf kapısı.

`CREATE OR REPLACE FUNCTION` ve `DROP TRIGGER IF EXISTS` katalog nesnesini
yalnız ADIYLA arar. Aynı adı taşıyan YABANCI bir nesne varsa:

* fonksiyon SESSİZCE EZİLİR — ve fonksiyon kimliği (oid) korunduğu için ona
  bağlı BAŞKA bir tetikleyici ANINDA bizim gövdemizi çalıştırmaya başlar;
* tetikleyici SESSİZCE DÜŞÜRÜLÜR — başkasının tablosu korumasız kalır.

Yazımdan SONRA koşan bir manifest bunu YAKALAYAMAZ: ezme işleminden sonraki
(kanonik görünen) durumu okur. Kapı kalıcı DDL'den ÖNCE koşmak zorundadır.

`036_package_runs.sql` bu disiplini checkpoint 4'te kazandı (KAPI 4) ve kendi
matrisi `test_migration_036.py`de koşuyor. Bu modül SINIFI kapatır: kapı artık
nesne yazan HER migration'ın sözleşmesidir ve matris dosya listesini de,
nesne listesini de KAVRAMDAN türetir — elle seçilmiş örnek yoktur, yarın
eklenen bir migration kendiliğinden kapsanır.

Kapsam sınırı (ölçülmüş, iddia edilmeyen):

* Kapı SIFIR argümanlı adı denetler (`to_regprocedure('<ad>()')`). Aynı adı
  taşıyan FARKLI imzalı bir aşırı yükleme bizim yazdığımızı EZMEZ — `CREATE OR
  REPLACE` onu görmez bile — dolayısıyla kapının konusu değildir.
* Geri alma script'leri (`rollback/*.sql`) yapısal kapıya TABİDİR; davranış
  matrisi yalnız ileri yöndeki migration'ları koşar, çünkü geri alma yolları
  kendi veri kapılarıyla daha erken durur.
"""

from __future__ import annotations

import re
import subprocess

import pytest

from . import conftest as infra

MIGRATIONS_DIR = infra.MIGRATIONS_DIR
ROLLBACK_DIR = MIGRATIONS_DIR / "rollback"

# Kapının RAISE metnindeki imza — 036'nın kullandığı metnin AYNISI, çünkü
# sınıfın tek bir dili olmalı.
IDENTITY_MARKER = "KANONIK OLMAYAN"

# Yabancı nesnenin parmak izi: ezilip ezilmediği BU metinle ölçülür.
FOREIGN_BODY_MARKER = "YABANCI GOVDE KIMLIK TESTI"


# ─── Kavramdan türetme ──────────────────────────────────────────────────────
#
# Desen bulunan örneklerden DEĞİL, mekanizmadan türetilir: "dosya bir katalog
# nesnesini adıyla yazıyor/düşürüyor mu?"

_WRITE_PATTERNS = (
    re.compile(r"CREATE\s+OR\s+REPLACE\s+FUNCTION", re.IGNORECASE),
    re.compile(r"CREATE\s+TRIGGER\b", re.IGNORECASE),
    re.compile(r"DROP\s+TRIGGER\s+IF\s+EXISTS", re.IGNORECASE),
    re.compile(r"DROP\s+FUNCTION\s+IF\s+EXISTS", re.IGNORECASE),
)

# Tek bir metin hem tetikleyici adını, hem tabloyu, hem fonksiyonu taşır —
# 036'nın kanonik sabitleri de, düz yazılmış DDL de aynı biçimde eşleşir.
# DEYİM SINIRI ZORUNLU (`[^;]`): sınırsız bir boşluk deseni bir `CREATE
# TRIGGER`dan sonraki deyime atlayıp YANLIŞ üçlü üretir — ölçüldü, `032`de
# argümanlı iki tetikleyici atlandığı için üçüncüsünün fonksiyonu birinciye
# yapıştı. Argüman da opsiyoneldir: tetikleyici fonksiyonu SIFIR argümanlıdır,
# parantez içindeki değer `TG_ARGV`dir.
_TRIGGER_TRIPLE_RE = re.compile(
    r"CREATE TRIGGER (\w+)\s+(?:BEFORE|AFTER|INSTEAD OF)[^;]*?"
    r"\bON (social\.\w+)[^;]*?EXECUTE (?:FUNCTION|PROCEDURE) (social\.\w+)\("
)
_FUNCTION_RE = re.compile(r"CREATE OR REPLACE FUNCTION\s+(social\.\w+)\(")
_DROPPED_FUNCTION_RE = re.compile(r"DROP FUNCTION IF EXISTS\s+(social\.\w+)\(")


def _sql_files() -> list:
    files = sorted(MIGRATIONS_DIR.glob("*.sql")) + sorted(ROLLBACK_DIR.glob("*.sql"))
    assert files, f"migration dizini boş görünüyor ({MIGRATIONS_DIR})"
    return files


def _carrier_files() -> list:
    """Katalog nesnesini ADIYLA yazan/düşüren HER dosya."""
    out = [p for p in _sql_files() if any(x.search(p.read_text("utf-8")) for x in _WRITE_PATTERNS)]
    assert out, "hiç taşıyıcı dosya türetilemedi — matris boş koşardı"
    return out


def _triples(path) -> tuple[tuple[str, str, str], ...]:
    text = path.read_text(encoding="utf-8")
    return tuple(dict.fromkeys(_TRIGGER_TRIPLE_RE.findall(text)))


def _functions(path) -> tuple[str, ...]:
    text = path.read_text(encoding="utf-8")
    adlar = set(_FUNCTION_RE.findall(text)) | set(_DROPPED_FUNCTION_RE.findall(text))
    adlar |= {fn for _t, _tab, fn in _triples(path)}
    return tuple(sorted(adlar))


CARRIERS = tuple(_carrier_files())
CARRIER_IDS = [p.name for p in CARRIERS]

# Davranış matrisi yalnız ileri yön: geri alma yolları kendi veri kapılarıyla
# daha erken durur, dolayısıyla kimlik kapısı orada ölçülemez (dürüst sınır).
FORWARD = tuple(p for p in CARRIERS if p.parent == MIGRATIONS_DIR)

FUNCTION_CASES = tuple((p, fn) for p in FORWARD for fn in _functions(p))
FUNCTION_IDS = [f"{p.name}:{fn}" for p, fn in FUNCTION_CASES]

TRIGGER_CASES = tuple((p, t) for p in FORWARD for t in _triples(p))
TRIGGER_IDS = [f"{p.name}:{t[0]}" for p, t in TRIGGER_CASES]


# ─── psql yardımcıları ──────────────────────────────────────────────────────


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


def _apply_file(url: str, path) -> subprocess.CompletedProcess:
    """Sarmalayıcı transaction OLMADAN uygular.

    "Yabancı gövde yerinde kaldı" iddiası ROLLBACK'in gizlediği bir sonuç
    değil, veritabanının KALICI durumundan okunur.
    """
    return _psql(url, "-f", str(path))


def _foreign_function_sql(fonksiyon: str) -> str:
    return (
        f"CREATE OR REPLACE FUNCTION {fonksiyon}() RETURNS trigger AS $yabanci$ "
        f"BEGIN RAISE EXCEPTION '{FOREIGN_BODY_MARKER}'; END $yabanci$ LANGUAGE plpgsql;"
    )


def _foreign_trigger_sql(tetikleyici: str, tablo: str) -> str:
    """Adı BİZİM, tanımı BAŞKA bir tetikleyici (farklı olay, farklı fonksiyon)."""
    return (
        "CREATE OR REPLACE FUNCTION social.yabanci_kimlik_test_fn() RETURNS trigger AS "
        "$yt$ BEGIN RETURN NEW; END $yt$ LANGUAGE plpgsql;"
        f"DROP TRIGGER IF EXISTS {tetikleyici} ON {tablo};"
        f"CREATE TRIGGER {tetikleyici} BEFORE DELETE ON {tablo} "
        "FOR EACH ROW EXECUTE FUNCTION social.yabanci_kimlik_test_fn();"
    )


def _function_body(url: str, fonksiyon: str) -> str:
    return _scalar(
        url,
        "SELECT coalesce((SELECT p.prosrc FROM pg_proc p "
        f"WHERE p.oid = to_regprocedure('{fonksiyon}()')), '<yok>')",
    )


def _trigger_def(url: str, tetikleyici: str, tablo: str) -> str:
    return _scalar(
        url,
        "SELECT coalesce((SELECT pg_get_triggerdef(t.oid) FROM pg_trigger t "
        f"WHERE t.tgrelid = '{tablo}'::regclass AND t.tgname = '{tetikleyici}' "
        "AND NOT t.tgisinternal), '<yok>')",
    )


# ─── 1. Boş-küme kontrol kolları ────────────────────────────────────────────


def test_carrier_set_is_derived_and_non_empty():
    """Taşıyıcı kümesi boşsa aşağıdaki matrislerin hiçbiri koşmazdı."""
    assert len(CARRIERS) >= 5, [p.name for p in CARRIERS]
    assert FORWARD, "ileri yönde hiç taşıyıcı yok"


def test_object_matrix_is_derived_and_non_empty():
    assert FUNCTION_CASES, "hiç fonksiyon adı türetilemedi"
    assert TRIGGER_CASES, "hiç (tetikleyici, tablo, fonksiyon) üçlüsü türetilemedi"
    for _path, fonksiyon in FUNCTION_CASES:
        assert fonksiyon.startswith("social."), fonksiyon
    for _path, (tetikleyici, tablo, fonksiyon) in TRIGGER_CASES:
        assert tablo.startswith("social."), tablo
        assert fonksiyon.startswith("social."), fonksiyon
        assert tetikleyici, "adsız tetikleyici"


# ─── 2. Yapısal kapı — SINIF tripwire'ı ─────────────────────────────────────


@pytest.mark.parametrize("path", CARRIERS, ids=CARRIER_IDS)
def test_every_carrier_declares_an_identity_gate(path):
    """Nesne yazan HER dosya kimlik kapısı taşır — gelecek dosyalar dâhil.

    Bu test bir davranış ölçmez, SÖZLEŞMEYİ zorlar: kapısız bir migration
    eklendiği anda kırmızı düşer. Davranışın kendisi aşağıdaki iki matriste
    ölçülür.
    """
    text = path.read_text(encoding="utf-8")
    assert IDENTITY_MARKER in text, (
        f"{path.name}: katalog nesnesini adıyla yazıyor ama kimlik kapısı YOK "
        f"('{IDENTITY_MARKER}' imzası bulunamadı) — aynı adı taşıyan yabancı bir "
        "nesne sessizce ezilir/düşürülür"
    )


# ─── 3. Davranış matrisi — kapı gerçekten reddediyor mu ─────────────────────


@pytest.mark.parametrize("case", FUNCTION_CASES, ids=FUNCTION_IDS)
def test_refuses_a_foreign_function_with_our_name(scratch_db_migrated, case):
    """Aynı adlı YABANCI fonksiyon EZİLMEZ: migration fail-closed durur.

    İki iddia birden: ret geldi mi, VE yabancı gövde yerinde mi. İkincisi
    olmadan test, "ezip sonra hata veren" bir migration'la da yeşil olurdu.
    """
    path, fonksiyon = case
    url = scratch_db_migrated
    _run_sql(url, _foreign_function_sql(fonksiyon))
    assert FOREIGN_BODY_MARKER in _function_body(url, fonksiyon), "kurulum tutmadı"

    result = _apply_file(url, path)

    assert result.returncode != 0, (
        f"{path.name}/{fonksiyon}: yabancı fonksiyon varken migration GEÇTİ:\n{result.stdout}"
    )
    assert IDENTITY_MARKER in result.stderr, result.stderr
    assert FOREIGN_BODY_MARKER in _function_body(url, fonksiyon), (
        f"{path.name}/{fonksiyon}: yabancı gövde EZİLDİ — kapı ret verdi ama yazımdan SONRA"
    )


@pytest.mark.parametrize("case", TRIGGER_CASES, ids=TRIGGER_IDS)
def test_refuses_a_foreign_trigger_with_our_name(scratch_db_migrated, case):
    """Aynı adlı YABANCI tetikleyici DÜŞÜRÜLMEZ: migration fail-closed durur."""
    path, (tetikleyici, tablo, _fonksiyon) = case
    url = scratch_db_migrated
    _run_sql(url, _foreign_trigger_sql(tetikleyici, tablo))
    yabanci_def = _trigger_def(url, tetikleyici, tablo)
    assert "BEFORE DELETE" in yabanci_def, f"kurulum tutmadı: {yabanci_def}"

    result = _apply_file(url, path)

    assert result.returncode != 0, (
        f"{path.name}/{tetikleyici}: yabancı tetikleyici varken migration GEÇTİ:\n"
        f"{result.stdout}"
    )
    assert IDENTITY_MARKER in result.stderr, result.stderr
    assert _trigger_def(url, tetikleyici, tablo) == yabanci_def, (
        f"{path.name}/{tetikleyici}: yabancı tetikleyici DEĞİŞTİ"
    )


# ─── 4. Pozitif kontrol — kapı her koşulda reddetmiyor ──────────────────────


@pytest.mark.parametrize("path", FORWARD, ids=[p.name for p in FORWARD])
def test_reapply_over_our_own_objects_passes(scratch_db_migrated, path):
    """İDEMPOTANS: kanonik nesneler kimlik kapısından GEÇER.

    Bu ayak olmadan yukarıdaki ret testleri "her koşulda reddeden" bir kapıyla
    da yeşil olurdu ve ikinci koşum imkânsız hâle gelirdi.
    """
    result = _apply_file(scratch_db_migrated, path)
    assert result.returncode == 0, f"{path.name} yeniden uygulama DURDU:\n{result.stderr}"
    assert IDENTITY_MARKER not in result.stderr, result.stderr
