"""Migration 033 fail-closed garanti doğrulaması (Task 12, checkpoint 12 F3).

`CREATE TABLE/INDEX IF NOT EXISTS` yalnız ADI arar, TANIMI doğrulamaz: aynı adda
YANLIŞ tanımlı bir nesne önceden varsa DDL sessizce atlanır, migration NOTICE
basıp başarıyla biter ve garanti kaybolur. Canlıya uygulama elle yapıldığı için
bu senaryo gerçektir — 032 bu sınıfı zaten kapatmıştı (F7); 033 aynı sınıftadır
ve ilk yazımda kapıyı ALMAMIŞTI.

**Temiz veritabanına uygulamak bu davranışı ÖLÇMEZ** — yalnız mutlu yolu koşar.
Bu dosya bozulmayı üretip kapının gerçekten durduğunu ölçer; kapı olmadan bu
testler yeşil olurdu, o yüzden pozitif kontrol niteliğindedir.

İzolasyon: her vaka `BEGIN … ROLLBACK` içinde koşar. psql tek oturumda önce
bozmayı, sonra `\\i 033`'ü uygular; sonuç ne olursa olsun transaction geri alınır
(Postgres'te DDL transactional'dır). Diğer testlerin gördüğü şema değişmez —
her vaka bunu ayrıca ölçer.
"""

from __future__ import annotations

import subprocess

import pytest

from . import conftest as infra

MIGRATION_033 = infra.MIGRATIONS_DIR / "033_package_events.sql"

FAILURE_MARKER = "migration 033 garanti dogrulamasi BASARISIZ"


def _psql_argv() -> tuple[list[str], dict[str, str]]:
    return infra.psql_argv(infra._require_test_database(infra.test_database_url()))


def _reapply_033(setup_sql: str = "") -> subprocess.CompletedProcess:
    """`setup_sql` + migration 033'ü TEK transaction'da koşar, sonra ROLLBACK."""
    argv, env = _psql_argv()
    script = f"BEGIN;\n{setup_sql}\n\\i {MIGRATION_033}\nROLLBACK;\n"
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


def _event_type_check_count() -> str:
    return _scalar(
        """
        SELECT count(*) FROM pg_constraint
        WHERE conrelid = 'social.package_events'::regclass AND contype = 'c'
        """
    )


def test_clean_reapply_succeeds():
    """Doğru şema üstünde yeniden uygulama SESSİZDİR — idempotentlik bozulmadı.

    Duyarlılık kontrolünün karşı ayağı: kapı her koşumda hata verseydi aşağıdaki
    bozulma testleri de yeşil olurdu ve hiçbir şey ölçülmemiş olurdu.
    """
    result = _reapply_033()
    assert result.returncode == 0, f"temiz yeniden uygulama DURDU:\n{result.stderr}"
    assert FAILURE_MARKER not in result.stderr


def test_missing_event_type_check_is_caught():
    """Kapalı olay kümesi CHECK'i düşürülmüşse migration DURur.

    Bu, sessiz kaybın en pahalı hâli: CHECK yoksa küme dışı bir olay türü
    yazılabilir ve "kapalı başlangıç kümesi" hükmü uygulamada yok olur, ama
    `CREATE TABLE IF NOT EXISTS` bunu geri getirmez.
    """
    before = _event_type_check_count()

    result = _reapply_033(
        "ALTER TABLE social.package_events DROP CONSTRAINT package_events_type_check;"
    )

    assert result.returncode != 0, (
        f"CHECK düşmüşken migration sessizce koştu — stdout:\n{result.stdout}"
    )
    assert FAILURE_MARKER in result.stderr, result.stderr
    assert "event_type CHECK" in result.stderr
    assert _event_type_check_count() == before, "vaka şemayı kalıcı olarak değiştirdi"


def test_widened_event_type_check_is_caught():
    """CHECK **var ama GENİŞLETİLMİŞ** olması da yakalanır.

    Varlık kontrolü yetmez: aynı adda, aynı kolonda, ama küme dışı bir türü
    kabul eden bir CHECK "kapalı küme" iddiasını sessizce boşa çıkarırdı.
    """
    result = _reapply_033(
        """
        ALTER TABLE social.package_events DROP CONSTRAINT package_events_type_check;
        ALTER TABLE social.package_events ADD CONSTRAINT package_events_type_check
            CHECK (event_type IN ('mismatch_fallthrough', 'uydurma_olay'));
        """
    )

    assert result.returncode != 0, (
        f"genişletilmiş CHECK sessizce kabul edildi — stdout:\n{result.stdout}"
    )
    assert FAILURE_MARKER in result.stderr, result.stderr


def test_brand_fk_without_cascade_is_caught():
    """Marka FK'sı CASCADE'ini kaybetmişse yakalanır (F18 sözleşmesi)."""
    result = _reapply_033(
        """
        ALTER TABLE social.package_events
            DROP CONSTRAINT package_events_brand_id_fkey;
        ALTER TABLE social.package_events
            ADD CONSTRAINT package_events_brand_id_fkey
            FOREIGN KEY (brand_id) REFERENCES social.brands(id);
        """
    )

    assert result.returncode != 0, (
        f"CASCADE kaybı sessizce geçti — stdout:\n{result.stdout}"
    )
    assert FAILURE_MARKER in result.stderr, result.stderr
    assert "brand_id FK" in result.stderr


def test_disabled_brand_fk_is_caught():
    """TANIM doğru ama FK KAPALIYSA yakalanır (tanım ≠ uygulanma).

    `DISABLE TRIGGER ALL` kısıt tanımını değiştirmeden FK'yı fiilen kapatır;
    yalnız `pg_get_constraintdef`e bakan bir kontrol bunu göremezdi.
    """
    result = _reapply_033("ALTER TABLE social.package_events DISABLE TRIGGER ALL;")

    assert result.returncode != 0, (
        f"kapalı FK sessizce geçti — stdout:\n{result.stdout}"
    )
    assert FAILURE_MARKER in result.stderr, result.stderr


@pytest.mark.parametrize(
    "index_name",
    ["idx_package_events_brand_created", "idx_package_events_sector_created"],
)
def test_wrong_index_definition_is_caught(index_name):
    """Aynı adda YANLIŞ tanımlı indeks yakalanır — ad varlığı garanti değildir."""
    result = _reapply_033(
        f"""
        DROP INDEX social.{index_name};
        CREATE INDEX {index_name} ON social.package_events (created_at);
        """
    )

    assert result.returncode != 0, (
        f"{index_name} yanlış tanımıyla sessizce kabul edildi — stdout:\n{result.stdout}"
    )
    assert FAILURE_MARKER in result.stderr, result.stderr
    assert index_name in result.stderr


# --- İmza TAMLIĞI (checkpoint 12 tur 2, F3) --------------------------------
#
# İlk yazımda indeks imzası elle kurulmuş alanlardan oluşuyordu (kolonlar +
# predicate + uygulanma bayrakları) ve `indisunique`, erişim yöntemi ile sıralama
# DIŞARIDA kalmıştı. Aynı adda UNIQUE bir indeks beklenen dizeyi ÜRETİYOR, yani
# `CREATE INDEX IF NOT EXISTS` onu atlıyor ve migration başarıyla bitiyordu —
# oysa o şema aynı markanın aynı zaman damgalı iki olayını REDDEDERDİ.
#
# Çözüm alan EKLEMEK değil, imzayı TAM tanıma bağlamak oldu: `pg_get_indexdef`
# indeksin kanonik tanımının tamamını taşır, dolayısıyla unutulabilecek bir alan
# KALMAZ. Aşağıdaki vakalar bunu ölçer.


def test_unique_index_with_matching_columns_is_caught():
    """Aynı ad + aynı kolon + aynı predicate, ama UNIQUE → yakalanmalı.

    Bu, kısmi imzanın gerçek atlatma vakasıdır: eski kapı bu şemayı ONAYLIYORDU.
    """
    result = _reapply_033(
        """
        DROP INDEX social.idx_package_events_brand_created;
        CREATE UNIQUE INDEX idx_package_events_brand_created
            ON social.package_events (brand_id, created_at DESC)
            WHERE brand_id IS NOT NULL;
        """
    )

    assert result.returncode != 0, (
        f"UNIQUE indeks sessizce kabul edildi — stdout:\n{result.stdout}"
    )
    assert FAILURE_MARKER in result.stderr, result.stderr
    assert "idx_package_events_brand_created" in result.stderr


def test_reversed_index_ordering_is_caught():
    """Sıralama yönü (DESC → ASC) değişmişse yakalanmalı."""
    result = _reapply_033(
        """
        DROP INDEX social.idx_package_events_sector_created;
        CREATE INDEX idx_package_events_sector_created
            ON social.package_events (sector_id, created_at ASC)
            WHERE sector_id IS NOT NULL;
        """
    )

    assert result.returncode != 0, (
        f"ters sıralama sessizce kabul edildi — stdout:\n{result.stdout}"
    )
    assert FAILURE_MARKER in result.stderr, result.stderr


def test_non_partial_index_is_caught():
    """Kısmi olmayan (predicate'siz) indeks yakalanmalı."""
    result = _reapply_033(
        """
        DROP INDEX social.idx_package_events_brand_created;
        CREATE INDEX idx_package_events_brand_created
            ON social.package_events (brand_id, created_at DESC);
        """
    )

    assert result.returncode != 0, (
        f"predicate kaybı sessizce kabul edildi — stdout:\n{result.stdout}"
    )
    assert FAILURE_MARKER in result.stderr, result.stderr


# ─── Tablo/kolon imzası tuzakları (final review, 2026-08-25) ────────────────


def _events_decoy(
    *,
    detail_type: str = "JSONB",
    id_extra: str = "PRIMARY KEY DEFAULT gen_random_uuid()",
    persistence: str = "",
    suffix: str = "",
) -> str:
    """Aynı ADDA, kısıtları ve indeksleri DOĞRU ama imzası bozuk sahte tablo.

    `CREATE TABLE IF NOT EXISTS` bu tabloyu DEĞİŞTİRMEZ; garanti bloğu onu
    yakalamazsa migration rc=0 ile geçer ve yanlış tanımlı tablo canlıda kalır.
    """
    return f"""
        DROP TABLE IF EXISTS social.package_events CASCADE;
        CREATE {persistence} TABLE social.package_events (
            id UUID {id_extra},
            event_type TEXT NOT NULL,
            sector_id UUID,
            brand_id UUID,
            package_id UUID,
            from_version INT,
            to_version INT,
            actor TEXT,
            detail {detail_type},
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        {suffix}
    """


def test_events_wrong_detail_type_is_caught():
    """`detail` JSONB değilse migration DURur — kolon imzası kapısı."""
    result = _reapply_033(_events_decoy(detail_type="TEXT"))
    assert result.returncode != 0, f"yanlış tipli detail geçti:\n{result.stdout}"
    assert FAILURE_MARKER in result.stderr, result.stderr
    assert "package_events kolon imzası" in result.stderr


def test_events_missing_primary_key_is_caught():
    """`id` birincil anahtar değilse migration DURur."""
    result = _reapply_033(_events_decoy(id_extra="DEFAULT gen_random_uuid()"))
    assert result.returncode != 0, f"PK'sız tablo geçti:\n{result.stdout}"
    assert FAILURE_MARKER in result.stderr, result.stderr
    assert "package_events PRIMARY KEY" in result.stderr


@pytest.mark.parametrize(
    "persistence, suffix, label",
    [
        ("UNLOGGED", "", "UNLOGGED tablo"),
        (
            "",
            "ALTER TABLE social.package_events ENABLE ROW LEVEL SECURITY;",
            "satır güvenliği açık tablo",
        ),
    ],
)
def test_events_table_property_corruption_is_caught(persistence, suffix, label):
    """Tablonun KENDİ özellikleri de sözleşmenin parçası.

    İkisi de kolon imzasını, kısıtları ve indeksleri BİREBİR aynı üretir.
    `UNLOGGED` bir olay tablosu temiz olmayan kapanışta TRUNCATE edilir — yaşam
    döngüsü geçmişi (kim, ne zaman, hangi sürüm) yok olur; RLS ise satırları
    yazdırır ama okutmaz, yani denetim izi sessizce görünmez olur.
    """
    result = _reapply_033(_events_decoy(persistence=persistence, suffix=suffix))
    assert result.returncode != 0, f"{label} sessizce geçti:\n{result.stdout}"
    assert FAILURE_MARKER in result.stderr, result.stderr
    assert "package_events tablo imzası" in result.stderr


@pytest.mark.parametrize(
    "extra, label",
    [
        (
            "ALTER TABLE social.package_events "
            "ADD CONSTRAINT package_events_never_check CHECK (false);",
            "fazladan CHECK (false)",
        ),
        (
            "ALTER TABLE social.package_events "
            "ADD CONSTRAINT package_events_extra_unique UNIQUE (event_type);",
            "fazladan UNIQUE",
        ),
        (
            "CREATE FUNCTION social.probe_reject() RETURNS trigger AS $fn$ "
            "BEGIN RAISE EXCEPTION 'red'; END $fn$ LANGUAGE plpgsql; "
            "CREATE TRIGGER package_events_probe_reject BEFORE INSERT "
            "ON social.package_events FOR EACH ROW "
            "EXECUTE FUNCTION social.probe_reject();",
            "yazımı reddeden fazladan tetikleyici",
        ),
    ],
)
def test_events_extra_objects_are_caught(extra, label):
    """FAZLADAN nesne de bulgudur — pozitif izin listesi yetmez.

    Üçü de beklenen kolonları, kısıtları ve indeksleri BİREBİR taşır; yani
    madde madde kontrollerin hepsinden geçerler. Ama üçü de tabloyu fiilen
    yazılamaz ya da beklenenden dar hâle getirir: migration "başarılı" der,
    uygulama yazamaz. Kapalı küme karşılaştırması bunun tek kapısıdır.
    """
    result = _reapply_033(_events_decoy() + "\n" + extra)
    assert result.returncode != 0, f"{label} sessizce geçti:\n{result.stdout}"
    assert FAILURE_MARKER in result.stderr, result.stderr
    assert "kümesi (kapalı)" in result.stderr, result.stderr
