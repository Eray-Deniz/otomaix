"""Migration 034 fail-closed garanti doğrulaması (Task 14, checkpoint 14 F4).

033 ile AYNI sınıf, ama bir adım daha ileri: 033'ün kapısı kısıtları ve
indeksleri doğruluyordu, TABLONUN KENDİSİNİ değil. Checkpoint 14 bunu ölçtü —
`payload` TEXT olan, `id`'si birincil anahtarsız ve varsayılansız, ama
CHECK'leri ve indeksi birebir doğru olan sahte bir tablo migration'dan `rc=0`
ile geçiyordu. Kısıtlar tablonun sözleşmesinin TAMAMI değildir.

Bu yüzden 034'ün kapısı kolon imzasını (ad · tip · null'lanabilirlik · kanonik
varsayılan, sırayla) ve birincil anahtarı da doğrular. Aşağıdaki vakalar o
kapının gerçekten durduğunu ölçer; kapı olmadan hepsi YEŞİL olurdu — yani
pozitif kontrol niteliğindedirler.

İzolasyon: her vaka `BEGIN … ROLLBACK` içinde koşar (Postgres'te DDL
transactional'dır). Diğer testlerin gördüğü şema değişmez — her vaka bunu
ayrıca ölçer.
"""

from __future__ import annotations

import subprocess

import pytest

from . import conftest as infra

MIGRATION_034 = infra.MIGRATIONS_DIR / "034_admin_events.sql"

FAILURE_MARKER = "migration 034 garanti dogrulamasi BASARISIZ"

# Doğru tanımlı sahte tablo gövdesi — vakalar bunun TEK bir alanını bozar.
# Böylece her vaka "yalnız bu alan yanlış" der ve kapının hangi alanı ölçtüğü
# ayrı ayrı görünür.
_DECOY_TEMPLATE = """
DROP TABLE social.admin_events CASCADE;
CREATE TABLE social.admin_events (
    id UUID {id_extra},
    kind TEXT NOT NULL,
    payload {payload_type} NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    delivery_state TEXT NOT NULL DEFAULT 'pending',
    lease_expires_at TIMESTAMPTZ,
    attempt_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT admin_events_delivery_state_check CHECK (delivery_state IN (
        'pending', 'sending', 'sent', 'failed'
    )),
    CONSTRAINT admin_events_lease_state_check CHECK (
        (delivery_state = 'sending') = (lease_expires_at IS NOT NULL)
    ),
    CONSTRAINT admin_events_attempt_count_check CHECK (attempt_count >= 0)
);
CREATE INDEX idx_admin_events_claimable
    ON social.admin_events (created_at)
    WHERE delivery_state IN ('pending', 'sending');
"""


def _decoy(*, payload_type: str = "JSONB", id_extra: str = "PRIMARY KEY DEFAULT gen_random_uuid()") -> str:
    return _DECOY_TEMPLATE.format(payload_type=payload_type, id_extra=id_extra)


def _psql_argv() -> tuple[list[str], dict[str, str]]:
    return infra.psql_argv(infra._require_test_database(infra.test_database_url()))


def _reapply_034(setup_sql: str = "") -> subprocess.CompletedProcess:
    """`setup_sql` + migration 034'ü TEK transaction'da koşar, sonra ROLLBACK."""
    argv, env = _psql_argv()
    script = f"BEGIN;\n{setup_sql}\n\\i {MIGRATION_034}\nROLLBACK;\n"
    return subprocess.run(argv, input=script, env=env, capture_output=True, text=True)


def _scalar(sql: str) -> str:
    argv, env = _psql_argv()
    result = subprocess.run(
        argv + ["--tuples-only", "--no-align", "-c", sql],
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def _payload_type() -> str:
    return _scalar(
        "SELECT format_type(a.atttypid, a.atttypmod) FROM pg_attribute a "
        "WHERE a.attrelid = 'social.admin_events'::regclass AND a.attname = 'payload'"
    )


def test_clean_reapply_succeeds():
    """Doğru şema üstünde yeniden uygulama SESSİZDİR — idempotentlik bozulmadı.

    Duyarlılık kontrolünün karşı ayağı: kapı her koşumda hata verseydi aşağıdaki
    bozulma testleri de yeşil olurdu ve hiçbir şey ölçülmemiş olurdu.
    """
    result = _reapply_034()
    assert result.returncode == 0, f"temiz yeniden uygulama DURDU:\n{result.stderr}"
    assert FAILURE_MARKER not in result.stderr


def test_decoy_with_correct_definition_passes():
    """Sahte tablo DOĞRU tanımlıysa geçer — kapı ada değil TANIMA bakıyor.

    Bu vaka olmadan aşağıdaki reddetmeler "her sahte tabloyu reddediyor"
    olabilirdi; o zaman kapı tanım değil, yalnız `DROP TABLE` izini ölçerdi.
    """
    result = _reapply_034(_decoy())
    assert result.returncode == 0, f"doğru tanımlı sahte tablo REDDEDİLDİ:\n{result.stderr}"


def test_wrong_payload_type_is_caught():
    """`payload` JSONB değilse migration DURur.

    Ölçülen gerçek vaka (checkpoint 14, F4): bu tablo CHECK'leri ve indeksi
    birebir doğru taşıdığı için eski kapı onu geçiriyordu. TEXT bir `payload`
    ile `record_admin_event` ya patlar ya kullanılamaz satır yazar, ve bildirim
    hataları zaten yutulduğu için arıza SESSİZ kalırdı.
    """
    before = _payload_type()

    result = _reapply_034(_decoy(payload_type="TEXT"))

    assert result.returncode != 0, (
        f"yanlış tipli payload sessizce geçti — stdout:\n{result.stdout}"
    )
    assert FAILURE_MARKER in result.stderr, result.stderr
    assert "kolon imzası" in result.stderr
    assert _payload_type() == before, "vaka şemayı kalıcı olarak değiştirdi"


def test_missing_primary_key_is_caught():
    """`id` birincil anahtar değilse migration DURur.

    PK'sız bir outbox tablosu yinelenen kimlik kabul eder; kira protokolünün
    tüm `WHERE id = $1` güncellemeleri o zaman birden çok satıra dokunabilirdi.
    """
    result = _reapply_034(_decoy(id_extra="DEFAULT gen_random_uuid()"))

    assert result.returncode != 0, (
        f"birincil anahtarsız tablo sessizce geçti — stdout:\n{result.stdout}"
    )
    assert FAILURE_MARKER in result.stderr, result.stderr
    assert "PRIMARY KEY" in result.stderr


def test_missing_id_default_is_caught():
    """`id` varsayılanı yoksa migration DURur.

    `record_admin_event` `id` YAZMAZ, varsayılana güvenir. Varsayılan düşerse
    her yazım NOT NULL ihlaliyle patlar — ve bildirim hataları yutulduğu için
    yine SESSİZ bir arıza olurdu.
    """
    result = _reapply_034(_decoy(id_extra="PRIMARY KEY"))

    assert result.returncode != 0, (
        f"varsayılansız id sessizce geçti — stdout:\n{result.stdout}"
    )
    assert FAILURE_MARKER in result.stderr, result.stderr
    assert "kolon imzası" in result.stderr


@pytest.mark.parametrize(
    "corruption, label",
    [
        (
            "ALTER TABLE social.admin_events "
            "DROP CONSTRAINT admin_events_delivery_state_check;",
            "delivery_state CHECK",
        ),
        (
            "ALTER TABLE social.admin_events "
            "DROP CONSTRAINT admin_events_lease_state_check;",
            "lease/state CHECK",
        ),
        (
            "ALTER TABLE social.admin_events "
            "DROP CONSTRAINT admin_events_idempotency_key_key;",
            "idempotency_key UNIQUE",
        ),
    ],
)
def test_dropped_guarantee_is_caught(corruption: str, label: str):
    """Kısıt/indeks düşürülmüşse migration DURur — `IF NOT EXISTS` geri getirmez.

    Üç kısıt üç ayrı sözü taşır: teslim durumu kapalı kümede kalır · kira yalnız
    `sending` satırında yaşar · aynı olay iki kez outbox'a girmez. Sessizce
    düşen her biri, kaybının FARK EDİLMEDİĞİ bir üretim davranışı üretirdi.
    """
    result = _reapply_034(corruption)

    assert result.returncode != 0, (
        f"{label} düşmüşken migration sessizce koştu — stdout:\n{result.stdout}"
    )
    assert FAILURE_MARKER in result.stderr, result.stderr
    assert label in result.stderr


def test_dropped_claim_index_is_repaired_not_rejected():
    """Eksik indeks ONARILIR, reddedilmez — kısıtlardan farkı budur.

    `CREATE TABLE IF NOT EXISTS` tablo varken KISITLARI geri getirmez (bütün
    ifade atlanır), ama indeksin kendi `CREATE INDEX IF NOT EXISTS` ifadesi
    vardır ve indeks yoksa GERÇEKTEN yaratılır. Bu ayrımı ölçmek gerekiyordu:
    ilk yazımda indeks de "yakalanır" varsayılmıştı ve test bu varsayımı
    ÇÜRÜTTÜ (checkpoint 14 fix turu). Kapının sözü artık dürüst: eksik indeks
    onarılır, YANLIŞ TANIMLI indeks reddedilir (bir sonraki test).
    """
    result = _reapply_034("DROP INDEX social.idx_admin_events_claimable;")

    assert result.returncode == 0, (
        f"eksik indeks onarılmadı, migration DURDU:\n{result.stderr}"
    )
    assert FAILURE_MARKER not in result.stderr


def test_widened_delivery_state_check_is_caught():
    """CHECK **var ama GENİŞLETİLMİŞ** olması da yakalanır.

    Varlık kontrolü yetmez: küme dışı bir durumu kabul eden bir CHECK, kira
    protokolünün sorgularını sessizce boşa çıkaran satırlara izin verirdi
    (claim yüklemi eşleşmez, satır görünmez olur).
    """
    result = _reapply_034(
        "ALTER TABLE social.admin_events "
        "DROP CONSTRAINT admin_events_delivery_state_check; "
        "ALTER TABLE social.admin_events ADD CONSTRAINT "
        "admin_events_delivery_state_check CHECK (delivery_state IN "
        "('pending', 'sending', 'sent', 'failed', 'yolda'));"
    )

    assert result.returncode != 0, (
        f"genişletilmiş CHECK sessizce geçti — stdout:\n{result.stdout}"
    )
    assert FAILURE_MARKER in result.stderr, result.stderr
    assert "delivery_state CHECK" in result.stderr


def test_non_partial_claim_index_is_caught():
    """İndeks **var ama predicate'siz** olması da yakalanır.

    Kısmi olmayan indeks terminal satırları da taşır; "claim maliyeti açık iş
    sayısıyla sınırlı" vaadi sessizce yanlışa döner.
    """
    result = _reapply_034(
        "DROP INDEX social.idx_admin_events_claimable; "
        "CREATE INDEX idx_admin_events_claimable "
        "ON social.admin_events (created_at);"
    )

    assert result.returncode != 0, (
        f"predicate'siz indeks sessizce geçti — stdout:\n{result.stdout}"
    )
    assert FAILURE_MARKER in result.stderr, result.stderr
    assert "idx_admin_events_claimable" in result.stderr
