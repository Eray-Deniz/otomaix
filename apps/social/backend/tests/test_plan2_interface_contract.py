"""Plan 2'ye teslim edilen arayüzlerin ÇAĞRILABİLİRLİK kanıtı (plan Task 16).

Bu dosya davranış testi DEĞİLDİR — davranışın kendisi Task 8-14'ün testlerinde
ölçülür. Burada ölçülen tek şey **teslim sözleşmesidir:** planın "Plan 2'ye
teslim edilen arayüzler" bölümündeki HER madde, orada BELGELENEN argümanlarla
import edilip çağrılabiliyor mu.

Neden ayrı bir dosya: teslim listesi bir prose bölümüdür ve prose sessizce
bayatlar. Bir imza değişir, liste eski hâlinde kalır ve Plan 2 yürütücüsü
çalışmayan bir sözleşmeye göre kod yazar. Bu dosya listeyi çalıştırılabilir
hâle getirir — imza değişirse burası KIRILIR.

Kapsam sınırı (dürüst etiket): bu testler arayüzlerin VAR ve ÇAĞRILABİLİR
olduğunu kanıtlar; Plan 2'nin onları DOĞRU kullanacağını kanıtlamaz.
"""

from __future__ import annotations

import uuid

import pytest

from app.core.database import _init_connection
from app.services.notifications import record_admin_event
from app.services.sector_package_lifecycle import (
    ActivationGateEvidence,
    GateNotSatisfied,
    RollbackGateEvidence,
    activate_package,
    deactivate_package,
    insert_draft,
    rollback_package,
)
from app.services.sector_packages import (
    SectorPackageContext,
    ValidationResult,
    motion_pool,
    normalize_special_day_key,
    scene_pool,
    validate_package_content,
)
from app.services.sector_pipeline import identity

from .prompt_regression.capture import (
    FIXTURES_DIR,
    assert_matches_fixture,
    capture_anthropic_calls,
)
from .test_sector_packages_service import CUMHURIYET_KEY, _valid_content

ACTOR = "plan2@otomaix"


# ─── Ortak kurulum ──────────────────────────────────────────────────────────


@pytest.fixture
async def pkg_db(db):
    """Üretimin KENDİ bağlantı yapılandırması + yazım kapısının takvim besini.

    `insert_draft` takvim anahtarlarını DB'den okur; `_valid_content()` bir
    `ozel_gun` anahtarı taşır. Takvim satırı olmadan kapı — doğru olarak —
    reddeder ve test arayüzü değil kurulumu ölçerdi.
    """
    await _init_connection(db)
    await db.execute(
        "INSERT INTO social.public_holidays (year, date, name_tr) "
        "VALUES (2099, '2099-10-29', $1)",
        "Cumhuriyet Bayramı",
    )
    return db


async def _sub_sector(db) -> uuid.UUID:
    root_id = await db.fetchval(
        "SELECT id FROM social.sectors WHERE parent_sector_id IS NULL LIMIT 1"
    )
    assert root_id is not None, "kök sektör seed'i eksik"
    return await db.fetchval(
        "INSERT INTO social.sectors (slug, display_name, parent_sector_id) "
        "VALUES ($1, $2, $3) RETURNING id",
        f"alt-{uuid.uuid4().hex[:8]}",
        "Alt Sektör",
        root_id,
    )


# ─── Madde 1: Migration 032 şeması ──────────────────────────────────────────


# ─── Madde 1: Migration 032 şeması — KAPALI MANİFEST ────────────────────────
#
# Neden seçilmiş özellik listesi DEĞİL: iki bağımsız review turu üst üste aynı ekseni
# buldu ("şu özelliği de denetlemiyorsun") — önce tablo/kolon, sonra birincil anahtar ·
# varsayılan · yabancı anahtar. Elle uzatılan liste her turda yeni bir varyant üretir ve
# kapanmaz. Bu yüzden liste değil MANİFEST: her ilişkinin tablo imzası · kolon ·
# kısıt · indeks · tetikleyici kümesi kataloğdan okunur ve beklenenle KAPALI KÜME olarak karşılaştırılır.
# Eksik olan da FAZLA olan da bulgudur; yeni bir özellik ekseni "denetlenmiyor" olamaz,
# çünkü eksen seçilmiyor.
#
# Manifest kataloğdan ÜRETİLDİ, sonra `shared/db/migrations/032_sector_packages.sql`'e
# karşı okunarak doğrulandı. Dürüst sınır: manifest, migration'ın o dosyada YAZDIĞINI
# değil, uygulandığında ORTAYA ÇIKANI pinler — migration'ın kendisi yanlışsa manifest o
# yanlışı dondurur. Koruduğu şey sonraki SESSİZ sapmadır.
#
# `NOT NULL <kolon>` kısıtları manifestten DIŞLANIR: PostgreSQL 17'den itibaren
# `pg_constraint`'te satır olarak görünürler, 16'da görünmezler. Null'lanabilirlik zaten
# kolon imzasında denetleniyor; bu satırları dışlamak kapsam kaybetmeden sürüm
# bağımlılığını kaldırır (bu depo PG16 ↔ PG18 farkını kabul edilmiş risk olarak taşıyor).

EXPECTED_032_MANIFEST = {
    "sector_research_artifacts": {
        # 034'ün tablo-imzası standardı (aynı beş alan).
        "relation": ("r", "p", False, False, False),
        "columns": {
            "id": ("uuid", "NO", "gen_random_uuid()"),
            "run_id": ("text", "NO", None),
            "sector_slug": ("text", "NO", None),
            "kind": ("text", "NO", None),
            "source": ("text", "NO", None),
            "brief_ref": ("text", "YES", None),
            "content_md": ("text", "NO", None),
            "created_at": ("timestamp with time zone", "YES", "now()"),
        },
        "constraints": {
            "sector_research_artifacts_pkey": "PRIMARY KEY (id)",
            "sector_research_artifacts_kind_check": (
                "CHECK ((kind = ANY (ARRAY['research'::text, 'review'::text, "
                "'synthesis'::text])))"
            ),
        },
        "indexes": {
            "sector_research_artifacts_pkey": (
                "CREATE UNIQUE INDEX sector_research_artifacts_pkey ON "
                "social.sector_research_artifacts USING btree (id)"
            ),
            "idx_sector_research_artifacts_slug_run": (
                "CREATE INDEX idx_sector_research_artifacts_slug_run ON "
                "social.sector_research_artifacts USING btree (sector_slug, run_id)"
            ),
        },
        "triggers": {
            "sector_research_artifacts_append_only": (
                "CREATE TRIGGER sector_research_artifacts_append_only BEFORE DELETE OR "
                "UPDATE ON social.sector_research_artifacts FOR EACH ROW EXECUTE "
                "FUNCTION social.reject_research_artifact_mutation()",
                "O",
            ),
            "sector_research_artifacts_no_truncate": (
                "CREATE TRIGGER sector_research_artifacts_no_truncate BEFORE TRUNCATE ON "
                "social.sector_research_artifacts FOR EACH STATEMENT EXECUTE FUNCTION "
                "social.reject_research_artifact_mutation()",
                "O",
            ),
        },
    },
    "sector_packages": {
        # 034'ün tablo-imzası standardı (aynı beş alan).
        "relation": ("r", "p", False, False, False),
        "columns": {
            "id": ("uuid", "NO", "gen_random_uuid()"),
            "sector_id": ("uuid", "NO", None),
            "version": ("integer", "NO", None),
            "status": ("text", "NO", None),
            "schema_version": ("integer", "NO", None),
            "content": ("jsonb", "NO", None),
            "decision_log": ("jsonb", "NO", "'[]'::jsonb"),
            "run_id": ("text", "YES", None),  # K-110 AÇIK — nullable KALIR
            "created_at": ("timestamp with time zone", "YES", "now()"),
            "activated_at": ("timestamp with time zone", "YES", None),
        },
        "constraints": {
            "sector_packages_pkey": "PRIMARY KEY (id)",
            "sector_packages_sector_version_key": "UNIQUE (sector_id, version)",
            "sector_packages_id_version_key": "UNIQUE (id, version)",
            "sector_packages_sector_id_fkey": (
                "FOREIGN KEY (sector_id) REFERENCES social.sectors(id)"
            ),
            "sector_packages_status_check": (
                "CHECK ((status = ANY (ARRAY['draft'::text, 'active'::text, "
                "'archived'::text])))"
            ),
        },
        "indexes": {
            "sector_packages_pkey": (
                "CREATE UNIQUE INDEX sector_packages_pkey ON social.sector_packages "
                "USING btree (id)"
            ),
            "sector_packages_sector_version_key": (
                "CREATE UNIQUE INDEX sector_packages_sector_version_key ON "
                "social.sector_packages USING btree (sector_id, version)"
            ),
            "sector_packages_id_version_key": (
                "CREATE UNIQUE INDEX sector_packages_id_version_key ON "
                "social.sector_packages USING btree (id, version)"
            ),
            "uq_sector_packages_single_active": (
                "CREATE UNIQUE INDEX uq_sector_packages_single_active ON "
                "social.sector_packages USING btree (sector_id) WHERE "
                "(status = 'active'::text)"
            ),
        },
        "triggers": {
            "sector_packages_sector_must_be_sub": (
                "CREATE TRIGGER sector_packages_sector_must_be_sub BEFORE INSERT OR "
                "UPDATE ON social.sector_packages FOR EACH ROW EXECUTE FUNCTION "
                "social.require_sub_sector_reference('sector_id')",
                "O",
            ),
        },
    },
    "generation_stamps": {
        # 034'ün tablo-imzası standardı (aynı beş alan).
        "relation": ("r", "p", False, False, False),
        "columns": {
            "id": ("uuid", "NO", "gen_random_uuid()"),
            "brand_id": ("uuid", "NO", None),
            "package_id": ("uuid", "NO", None),
            "package_version": ("integer", "NO", None),
            "created_at": ("timestamp with time zone", "YES", "now()"),
            "consumed_at": ("timestamp with time zone", "YES", None),
        },
        "constraints": {
            "generation_stamps_pkey": "PRIMARY KEY (id)",
            "generation_stamps_brand_id_fkey": (
                "FOREIGN KEY (brand_id) REFERENCES social.brands(id) ON DELETE CASCADE"
            ),
            # MATCH FULL YOK — iki kolon da NOT NULL, yarım çift zaten imkânsız.
            "generation_stamps_package_fkey": (
                "FOREIGN KEY (package_id, package_version) REFERENCES "
                "social.sector_packages(id, version)"
            ),
        },
        "indexes": {
            "generation_stamps_pkey": (
                "CREATE UNIQUE INDEX generation_stamps_pkey ON social.generation_stamps "
                "USING btree (id)"
            ),
        },
        "triggers": {},
    },
}

# Taşıyıcı tablolar (tablonun TAMAMI 032'nin değil) — 032'nin EKLEDİĞİ yüzey.
EXPECTED_032_CARRIER_COLUMNS = {
    ("brands", "sub_sector_id"): ("uuid", "YES", None),
    ("posts", "package_id"): ("uuid", "YES", None),
    ("posts", "package_version"): ("integer", "YES", None),
}

EXPECTED_032_CARRIER_CONSTRAINTS = {
    "brands_sub_sector_id_fkey": "FOREIGN KEY (sub_sector_id) REFERENCES social.sectors(id)",
    # K-07 damgası: MATCH FULL yarım-NULL çifti imkânsız kılar.
    "posts_package_stamp_fkey": (
        "FOREIGN KEY (package_id, package_version) REFERENCES "
        "social.sector_packages(id, version) MATCH FULL"
    ),
}

EXPECTED_032_CARRIER_TRIGGERS = {
    "brands_sub_sector_must_be_sub": (
        "CREATE TRIGGER brands_sub_sector_must_be_sub BEFORE INSERT OR UPDATE ON "
        "social.brands FOR EACH ROW EXECUTE FUNCTION "
        "social.require_sub_sector_reference('sub_sector_id')"
    ),
    "sectors_reject_reparenting": (
        "CREATE TRIGGER sectors_reject_reparenting BEFORE UPDATE ON social.sectors FOR "
        "EACH ROW EXECUTE FUNCTION social.reject_sector_reparenting()"
    ),
}


def _char(value):
    """asyncpg `"char"` kolonlarını bayt olarak döner — metne çevrilir."""
    return value.decode() if isinstance(value, (bytes, bytearray)) else value


async def _relation_manifest(db, table: str) -> dict:
    """Bir ilişkinin TAM katalog imzası — beklenenle kapalı küme karşılaştırması için."""
    relation = await db.fetchrow(
        "SELECT c.relkind, c.relpersistence, c.relispartition, c.relrowsecurity, "
        "       c.relforcerowsecurity "
        "  FROM pg_class AS c "
        "  JOIN pg_namespace AS n ON n.oid = c.relnamespace "
        " WHERE n.nspname = 'social' AND c.relname = $1",
        table,
    )
    columns = {
        row["column_name"]: (row["data_type"], row["is_nullable"], row["column_default"])
        for row in await db.fetch(
            "SELECT column_name, data_type, is_nullable, column_default "
            "  FROM information_schema.columns "
            " WHERE table_schema = 'social' AND table_name = $1",
            table,
        )
    }
    constraints = {
        row["conname"]: row["definition"]
        for row in await db.fetch(
            "SELECT c.conname, pg_get_constraintdef(c.oid) AS definition "
            "  FROM pg_constraint AS c "
            "  JOIN pg_class AS r ON r.oid = c.conrelid "
            "  JOIN pg_namespace AS n ON n.oid = r.relnamespace "
            " WHERE n.nspname = 'social' AND r.relname = $1",
            table,
        )
        # PG17+ `NOT NULL` kısıtlarını satır olarak gösterir, PG16 göstermez —
        # null'lanabilirlik zaten kolon imzasında denetleniyor.
        if not row["definition"].startswith("NOT NULL ")
    }
    indexes = {
        row["indexname"]: row["indexdef"]
        for row in await db.fetch(
            "SELECT indexname, indexdef FROM pg_indexes "
            " WHERE schemaname = 'social' AND tablename = $1",
            table,
        )
    }
    triggers = {
        row["tgname"]: (row["definition"], _char(row["tgenabled"]))
        for row in await db.fetch(
            "SELECT t.tgname, pg_get_triggerdef(t.oid) AS definition, t.tgenabled "
            "  FROM pg_trigger AS t "
            "  JOIN pg_class AS r ON r.oid = t.tgrelid "
            "  JOIN pg_namespace AS n ON n.oid = r.relnamespace "
            " WHERE n.nspname = 'social' AND r.relname = $1 AND NOT t.tgisinternal",
            table,
        )
    }
    return {
        # Tablonun KENDİ katalog özellikleri. Kısıt/indeks/tetikleyici tanımlarının
        # HİÇBİRİ bunu taşımaz: `CREATE TABLE` → `CREATE UNLOGGED TABLE` değişikliği
        # diğer dört yüzeyi bayt-aynı bırakır ama çökmede tabloyu boşaltır. Alan
        # listesi 034'ün tablo-imzası standardıyla AYNI (kendi icadım değil).
        "relation": (
            _char(relation["relkind"]),
            _char(relation["relpersistence"]),
            relation["relispartition"],
            relation["relrowsecurity"],
            relation["relforcerowsecurity"],
        )
        if relation is not None
        else None,
        "columns": columns,
        "constraints": constraints,
        "indexes": indexes,
        "triggers": triggers,
    }


@pytest.mark.parametrize("table", sorted(EXPECTED_032_MANIFEST))
async def test_migration_032_relation_manifest_is_closed(db, table):
    """İlişkinin kolon · kısıt · indeks · tetikleyici kümesi manifestle BİREBİR aynı.

    Kapalı karşılaştırma: bir birincil anahtarın, varsayılanın, yabancı anahtarın,
    tetikleyicinin ya da indeksin kaybolması da, habersiz eklenmesi de bu testi
    düşürür. Tek tek özellik saymak yerine kümeyi karşılaştırmanın sebebi budur.
    """
    observed = await _relation_manifest(db, table)
    expected = EXPECTED_032_MANIFEST[table]
    assert observed["columns"], f"social.{table} yok — 032 teslim edilmemiş"
    assert observed["relation"] == expected["relation"], (
        f"social.{table} tablo imzası saptı (relkind · kalıcılık · bölüm · satır "
        f"güvenliği): {observed['relation']} != {expected['relation']}"
    )
    for facet in ("columns", "constraints", "indexes", "triggers"):
        assert observed[facet] == expected[facet], (
            f"social.{table} '{facet}' manifestten SAPTI\n"
            f"yalnız gözlenende: {sorted(set(observed[facet]) - set(expected[facet]))}\n"
            f"yalnız beklenende: {sorted(set(expected[facet]) - set(observed[facet]))}\n"
            f"gözlenen: {sorted(observed[facet].items())}"
        )


async def test_migration_032_carrier_surface_delivered(db):
    """Taşıyıcı tablolara eklenen kolon · FK · tetikleyici — tanımlarıyla birlikte."""
    for (table, column), expected in EXPECTED_032_CARRIER_COLUMNS.items():
        manifest = await _relation_manifest(db, table)
        assert column in manifest["columns"], f"social.{table}.{column} yok"
        assert manifest["columns"][column] == expected, (
            f"social.{table}.{column} imzası saptı: "
            f"{manifest['columns'][column]} != {expected}"
        )
        if column == "sub_sector_id":
            assert (
                manifest["constraints"].get("brands_sub_sector_id_fkey")
                == EXPECTED_032_CARRIER_CONSTRAINTS["brands_sub_sector_id_fkey"]
            ), "brands.sub_sector_id yabancı anahtarı yok/sapmış"
        if column == "package_id":
            assert (
                manifest["constraints"].get("posts_package_stamp_fkey")
                == EXPECTED_032_CARRIER_CONSTRAINTS["posts_package_stamp_fkey"]
            ), "posts damga FK'sı yok/sapmış (MATCH FULL dahil)"

    for table in ("brands", "sectors"):
        manifest = await _relation_manifest(db, table)
        for name, definition in EXPECTED_032_CARRIER_TRIGGERS.items():
            if name in manifest["triggers"]:
                assert manifest["triggers"][name] == (definition, "O"), (
                    f"{name} tanımı/etkinliği saptı: {manifest['triggers'][name]}"
                )
    observed_triggers = set()
    for table in ("brands", "sectors"):
        observed_triggers |= set((await _relation_manifest(db, table))["triggers"])
    missing = [n for n in EXPECTED_032_CARRIER_TRIGGERS if n not in observed_triggers]
    assert not missing, f"eksik taşıyıcı tetikleyici(ler): {missing}"


async def test_plan2_write_surface_produces_draft_only(pkg_db):
    """K-135'in kod karşılığı: `insert_draft` YALNIZ `draft` üretir."""
    sector_id = await _sub_sector(pkg_db)
    package_id = await insert_draft(
        pkg_db,
        sector_id=sector_id,
        content=_valid_content(),
        schema_version=1,
        run_id=None,
        actor=ACTOR,
    )
    row = await pkg_db.fetchrow(
        "SELECT status, version FROM social.sector_packages WHERE id = $1", package_id
    )
    assert row["status"] == "draft"
    assert row["version"] == 1


# ─── Task 3: `insert_draft` karar günlüğünü kabul eder ──────────────────────


async def test_insert_draft_accepts_decision_log(pkg_db):
    """Genişletilmiş imza: verilen karar günlüğü DOĞRULANIR ve YAZILIR.

    K-135 gereği `sector_packages`'a yazan tek yüzey burasıdır; karar günlüğü
    için ikinci bir yazma yolu AÇILMAZ. Günlük içerikle AYNI işlemde yazıldığı
    için eşleme bayatlayamaz.
    """
    sector_id = await _sub_sector(pkg_db)
    content = _valid_content()
    decision_log = _kapsayici_log(content)

    package_id = await insert_draft(
        pkg_db,
        sector_id=sector_id,
        content=content,
        schema_version=1,
        actor=ACTOR,
        decision_log=decision_log,
    )
    row = await pkg_db.fetchrow(
        "SELECT content, decision_log FROM social.sector_packages WHERE id = $1",
        package_id,
    )
    assert row["decision_log"] == decision_log
    assert identity.check_unit_integrity(row["content"], row["decision_log"]) == []


async def test_insert_draft_rejects_a_decision_log_that_fails_the_schema(pkg_db):
    """Kapı GERÇEKTEN koşuyor: şemayı geçmeyen günlükle yazım YAPILMAZ."""
    sector_id = await _sub_sector(pkg_db)
    with pytest.raises(ValueError, match="karar günlüğü şemayı geçmedi"):
        await insert_draft(
            pkg_db,
            sector_id=sector_id,
            content=_valid_content(),
            schema_version=1,
            actor=ACTOR,
            decision_log=[{"tur": "karar", "karar": "birlestir"}],
        )
    assert (
        await pkg_db.fetchval(
            "SELECT count(*) FROM social.sector_packages WHERE sector_id = $1",
            sector_id,
        )
        == 0
    ), "reddedilen günlükte satır yazılmış"


async def test_insert_draft_without_decision_log_keeps_plan1_behavior(pkg_db):
    """GERİYE UYUM: parametre verilmezse Plan 1 davranışı AYNEN kalır."""
    sector_id = await _sub_sector(pkg_db)
    package_id = await insert_draft(
        pkg_db,
        sector_id=sector_id,
        content=_valid_content(),
        schema_version=1,
        actor=ACTOR,
    )
    row = await pkg_db.fetchrow(
        "SELECT status, decision_log FROM social.sector_packages WHERE id = $1",
        package_id,
    )
    assert row["status"] == "draft"
    assert row["decision_log"] == [{"event": "draft_created", "actor": ACTOR}]


def _kapsayici_log(content: dict, *, karar: str = "ekle") -> list[dict]:
    """İçeriğin HER kanonik yolunu sahiplenen karar günlüğü."""
    return [
        {
            "tur": "karar",
            "alan": unit["alan"],
            "oge_yolu": path,
            "unit_id": identity.new_unit_id(),
            "oge_sha": unit["oge_sha"],
            "karar": karar,
            "gerekce": "İlk paket: birim yeni doğdu.",
            "kanit": "",
            "aktor": "sentez",
        }
        for path, unit in identity.enumerate_content_units(content).items()
    ]


async def test_insert_draft_rejects_a_log_that_does_not_cover_the_content(pkg_db):
    """F2: TEK yazma yüzeyi tutarsız çifti KALICI HÂLE GETİRMEZ.

    Şema kapısı satırın kendi biçimini ölçer; kapsamayı ölçmez. Bu satır
    olmadan K-135 yüzeyi on altı birim iddia eden bir günlüğü on dokuz öğelik
    bir içerikle yan yana yazabilirdi ve tutarsızlık ancak denetçi turunda
    ortaya çıkardı.
    """
    sector_id = await _sub_sector(pkg_db)
    content = _valid_content()
    eksik = [r for r in _kapsayici_log(content) if r["oge_yolu"] != "kapsam"]
    with pytest.raises(ValueError, match="içerik ile karar günlüğü tutarsız"):
        await insert_draft(
            pkg_db,
            sector_id=sector_id,
            content=content,
            schema_version=1,
            actor=ACTOR,
            decision_log=eksik,
        )
    assert (
        await pkg_db.fetchval(
            "SELECT count(*) FROM social.sector_packages WHERE sector_id = $1",
            sector_id,
        )
        == 0
    ), "tutarsız çiftte satır yazılmış"


async def test_insert_draft_accepts_a_log_carrying_kirp_and_cikar_rows(pkg_db):
    """F2 aşırı-red kontrolü: yaşamayan satırlar MEŞRUDUR, kapı onları saymaz.

    `kirp` ve `cikar` satırlarının yolu tanım gereği içerikte YOKTUR (kırpma
    paketten çıkarır, kayıttan çıkarmaz). Kapı "her satırın yolu içerikte
    olsun" diye yazılsaydı gerçek bir kırpma taşıyan HER paket reddedilirdi.
    """
    sector_id = await _sub_sector(pkg_db)
    content = _valid_content()
    decision_log = _kapsayici_log(content)
    decision_log.append(
        {
            "tur": "karar",
            "alan": "kanca_kaliplari",
            "oge_yolu": "kanca_kaliplari[9]",
            "unit_id": identity.new_unit_id(),
            "oge_sha": "e" * 64,
            "karar": "kirp",
            "gerekce": "Uzunluk tavanı aşıldı, aday pakete alınmadı.",
            "kanit": "",
            "aktor": "motor",
            "kural_kimligi": "K-130",
            "kural_surumu": "2026-08-27",
        }
    )
    decision_log.append(
        {
            "tur": "karar",
            "alan": "yasaklar_ve_hassasiyetler",
            "oge_yolu": "yasaklar_ve_hassasiyetler[4]",
            "unit_id": identity.new_unit_id(),
            "oge_sha": "f" * 64,
            "karar": "cikar",
            "gerekce": "Mevzuat yürürlükten kalktı.",
            "kanit": "Resmî Gazete 2026-01-01, mülga.",
            "aktor": "insan",
        }
    )
    decision_log.append(
        {
            "tur": "not",
            "sinif": "reddedilen-aday",
            "gerekce": "Kaynak pinlenmemiş.",
        }
    )
    package_id = await insert_draft(
        pkg_db,
        sector_id=sector_id,
        content=content,
        schema_version=1,
        actor=ACTOR,
        decision_log=decision_log,
    )
    row = await pkg_db.fetchrow(
        "SELECT content, decision_log FROM social.sector_packages WHERE id = $1",
        package_id,
    )
    assert row["decision_log"] == decision_log
    assert identity.check_unit_integrity(row["content"], row["decision_log"]) == []


async def test_insert_draft_with_an_empty_decision_log_keeps_the_plan1_trace(pkg_db):
    """BOŞ günlük yazılmaz: Plan 1'in `draft_created` izi korunur.

    Boş liste yazılsaydı taslak hiç izi olmayan bir günlükle doğardı — "kim
    yazdı" sorusu cevapsız kalırdı.
    """
    sector_id = await _sub_sector(pkg_db)
    package_id = await insert_draft(
        pkg_db,
        sector_id=sector_id,
        content=_valid_content(),
        schema_version=1,
        actor=ACTOR,
        decision_log=[],
    )
    assert await pkg_db.fetchval(
        "SELECT decision_log FROM social.sector_packages WHERE id = $1", package_id
    ) == [{"event": "draft_created", "actor": ACTOR}]


# ─── Madde 2: normalize_special_day_key ─────────────────────────────────────


def test_normalize_special_day_key_documented_signature():
    """`(name: str) -> str` — yazım ve okuma AYNI anahtarı görür (K-01b)."""
    key = normalize_special_day_key("Cumhuriyet Bayramı")
    assert isinstance(key, str) and key
    assert key == CUMHURIYET_KEY
    # Tek modül olmanın gözlenebilir sonucu: aynı ad her çağrıda aynı anahtar.
    assert normalize_special_day_key("  Cumhuriyet Bayramı  ") == key


# ─── Madde 3: validate_package_content ──────────────────────────────────────


def test_validate_package_content_documented_signature():
    """`(content, *, banned_brand_names, holiday_keys) -> ValidationResult`."""
    result = validate_package_content(
        _valid_content(),
        banned_brand_names=["Altınbaş"],
        holiday_keys={CUMHURIYET_KEY},
    )
    assert isinstance(result, ValidationResult)
    assert result.ok, result.errors

    # `holiday_keys` gerçekten tüketiliyor: takvimde olmayan anahtar REDDEDİLİR.
    kapali = validate_package_content(
        _valid_content(), banned_brand_names=[], holiday_keys=set()
    )
    assert not kapali.ok


# ─── Madde 4-5: insert_draft → activate → rollback → deactivate ─────────────


async def test_insert_draft_and_activate_chain_end_to_end(pkg_db):
    """Geçerli yazım + KANITLI aktivasyon zinciri uçtan uca koşar."""
    sector_id = await _sub_sector(pkg_db)
    package_id = await insert_draft(
        pkg_db,
        sector_id=sector_id,
        content=_valid_content(),
        schema_version=1,
        actor=ACTOR,
    )
    assert isinstance(package_id, uuid.UUID)

    await activate_package(
        pkg_db,
        package_id=package_id,
        evidence=ActivationGateEvidence(
            activation_eligible=True,
            open_questions_count=0,
            katman1_passed=True,
            checklist_approved=True,
        ),
        actor=ACTOR,
    )
    status = await pkg_db.fetchval(
        "SELECT status FROM social.sector_packages WHERE id = $1", package_id
    )
    assert status == "active"


async def test_rollback_package_takes_its_own_evidence(pkg_db):
    """Rollback AYRI kanıt tipi ister; aktivasyon kanıtı KABUL EDİLMEZ."""
    sector_id = await _sub_sector(pkg_db)
    first = await insert_draft(
        pkg_db, sector_id=sector_id, content=_valid_content(), schema_version=1, actor=ACTOR
    )
    activation = ActivationGateEvidence(
        activation_eligible=True,
        open_questions_count=0,
        katman1_passed=True,
        checklist_approved=True,
    )
    await activate_package(pkg_db, package_id=first, evidence=activation, actor=ACTOR)

    second = await insert_draft(
        pkg_db, sector_id=sector_id, content=_valid_content(), schema_version=1, actor=ACTOR
    )
    await activate_package(pkg_db, package_id=second, evidence=activation, actor=ACTOR)

    # Kanıt tipleri PAYLAŞILMAZ — aktivasyon kanıtıyla rollback yapılamaz.
    with pytest.raises(GateNotSatisfied):
        await rollback_package(
            pkg_db, sector_id=sector_id, to_version=1, evidence=activation, actor=ACTOR
        )

    await rollback_package(
        pkg_db,
        sector_id=sector_id,
        to_version=1,
        evidence=RollbackGateEvidence(manager_approved=True, katman1_passed=True),
        actor=ACTOR,
    )
    assert (
        await pkg_db.fetchval(
            "SELECT status FROM social.sector_packages WHERE id = $1", first
        )
        == "active"
    )


async def test_deactivate_package_documented_signature(pkg_db):
    """`(db, *, package_id, actor)` — kanıt İSTEMEZ (K-38 acil kol)."""
    sector_id = await _sub_sector(pkg_db)
    package_id = await insert_draft(
        pkg_db, sector_id=sector_id, content=_valid_content(), schema_version=1, actor=ACTOR
    )
    await activate_package(
        pkg_db,
        package_id=package_id,
        evidence=ActivationGateEvidence(
            activation_eligible=True,
            open_questions_count=0,
            katman1_passed=True,
            checklist_approved=True,
        ),
        actor=ACTOR,
    )
    await deactivate_package(pkg_db, package_id=package_id, actor=ACTOR)
    assert (
        await pkg_db.fetchval(
            "SELECT status FROM social.sector_packages WHERE id = $1", package_id
        )
        != "active"
    )


# ─── Madde 6: record_admin_event ────────────────────────────────────────────


async def test_record_admin_event_documented_signature(db):
    """`(db, *, kind, payload, idempotency_key) -> uuid` — outbox teslimi."""
    await _init_connection(db)
    key = f"plan2-contract-{uuid.uuid4().hex}"
    event_id = await record_admin_event(
        db,
        kind="package_activated",
        payload={"sector_id": str(uuid.uuid4())},
        idempotency_key=key,
    )
    assert isinstance(event_id, uuid.UUID)
    # Aynı anahtar YENİ satır üretmez — Plan 2 tur takibi buna dayanır.
    again = await record_admin_event(
        db, kind="package_activated", payload={"farkli": True}, idempotency_key=key
    )
    assert again == event_id


# ─── Madde 7: Katman-1 harness ──────────────────────────────────────────────


def test_katman1_harness_is_delivered_and_live(monkeypatch):
    """Harness import edilebilir, fixture'lar donmuş, kapı gerçekten ölçüyor."""
    # Dondurma bayrağı asılı kalmışsa aşağıdaki çağrı fixture'ı EZERDİ.
    monkeypatch.delenv("PROMPT_REGRESSION_UPDATE", raising=False)

    frozen = sorted(p.name for p in FIXTURES_DIR.glob("*.txt"))
    assert frozen, "Katman-1 fixture kümesi boş — donmuş taban yok"

    assert callable(capture_anthropic_calls)
    # Pozitif kontrol: kapı bir sapmayı gerçekten YAKALIYOR (no-op değil).
    with pytest.raises(AssertionError):
        assert_matches_fixture(frozen[0][: -len(".txt")], "bozulmuş prompt")


# ─── Madde 8: video_kodlar İKİ HAVUZ ────────────────────────────────────────


def test_video_kodlar_delivers_two_pools():
    """`hareket` + `sahne`, ikisi de liste — tek havuz sözleşmeyi karşılamaz."""
    tek_havuz = _valid_content(video_kodlar={"hareket": ["Slow orbit."]})
    result = validate_package_content(
        tek_havuz, banned_brand_names=[], holiday_keys={CUMHURIYET_KEY}
    )
    assert not result.ok
    assert any("video_kodlar" in error for error in result.errors)

    tek_cumle = _valid_content(
        video_kodlar={"hareket": "Slow orbit.", "sahne": "Boutique interior."}
    )
    result = validate_package_content(
        tek_cumle, banned_brand_names=[], holiday_keys={CUMHURIYET_KEY}
    )
    assert not result.ok

    # Okuma tarafı da İKİ havuzu ayrı ayrı görüyor.
    context = SectorPackageContext(
        package_id=uuid.uuid4(),
        version=1,
        content=_valid_content(),
        sub_sector_slug="kuyumculuk",
    )
    assert len(motion_pool(context)) == 2
    assert len(scene_pool(context)) == 2


# ─── Madde 9: Plan 1 ↔ Plan 2 bağımlılık sınırı (yapısal kapı) ──────────────
#
# Ek (`docs/plans/2026-08-27-sektor-bilgi-paketi-plan2-arayuz-eki.md`, satır 1467-1480)
# sınırı harfiyen bağlar ve kapısının "yapısal test" olduğunu söyler. Kapı buradadır.
#
# Test ELLE SEÇİLMİŞ bir örneğe bakmaz: kaynağı `ast` ile ayrıştırır ve modülün TÜM
# import düğümlerinin ÜRETİLMİŞ listesini kapalı bir izin kümesiyle karşılaştırır.
# Tek bir yasak adı aramak, bir sonraki turda ikinci yasak adı davet ederdi.
#
# DÜRÜST ETİKET — kapanmayan ayak. Hüküm (a) "kullanılan TEK ad
# `identity.canonical_sha`" der. Bu test import BİÇİMİNİ (modül import edilir, ad
# değil) ve hüküm (c)'yi (başka `sector_pipeline` modülü YOK) kapatır; hüküm (a)'nın
# AD KÜMESİ ayağını KAPATMAZ: `sector_package_lifecycle` bugün gerçekten
# `identity.validate_decision_log` ve `identity.check_unit_integrity`'yi de çağırıyor
# (Task 3'ün şema kapısı orada koşar). Ad kümesinin daraltılması ekin hükmünün
# revizyonunu gerektirir — tasarım katmanının işidir, burada sessizce genişletilmez.

import ast
from pathlib import Path

from app.services import sector_package_lifecycle as _lifecycle_module

# Yaprak: bağımlılık-yönünden yansız şema modülü. Hem Plan 1'in erişim katmanı hem
# `identity` buradan tüketir; ikinci bir kopya YOKTUR.
_YAPRAK = "app.services.sector_content_schema"

# Üçüncü parti DB yüzeyleri — hüküm (b)'nin "hiçbir DB yüzeyi" ayağı.
_DB_YUZEYLERI = frozenset({"asyncpg", "psycopg", "psycopg2", "sqlalchemy", "databases"})


def _import_edilen_moduller(path: Path) -> list[str]:
    """Kaynaktaki HER import düğümünün hedef modülü — üretilmiş liste."""
    agac = ast.parse(path.read_text(encoding="utf-8"))
    moduller: list[str] = []
    for node in ast.walk(agac):
        if isinstance(node, ast.Import):
            moduller.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            moduller.append("." * node.level + (node.module or ""))
    return moduller


def _from_importlar(path: Path) -> list[tuple[str, list[str]]]:
    """`from X import a, b` düğümleri — (modül, alınan adlar)."""
    agac = ast.parse(path.read_text(encoding="utf-8"))
    return [
        ("." * node.level + (node.module or ""), sorted(a.name for a in node.names))
        for node in ast.walk(agac)
        if isinstance(node, ast.ImportFrom)
    ]


def test_identity_imports_no_plan1_module_and_no_db_surface():
    """Hüküm (b): `identity.py` YALNIZ yapraktan okur — Plan 1 modülü YOK, DB YOK."""
    moduller = _import_edilen_moduller(Path(identity.__file__))
    app_importlari = sorted({m for m in moduller if m.split(".")[0] == "app"})
    assert app_importlari == [_YAPRAK], app_importlari
    db = sorted({m for m in moduller if m.split(".")[0] in _DB_YUZEYLERI})
    assert db == [], db


def test_the_leaf_is_actually_a_leaf():
    """İzin kümesi kaçamak OLMASIN: yaprağın kendisi hiçbir `app` modülü import etmez."""
    from app.services import sector_content_schema

    moduller = _import_edilen_moduller(Path(sector_content_schema.__file__))
    assert [m for m in moduller if m.split(".")[0] == "app"] == []
    assert [m for m in moduller if m.split(".")[0] in _DB_YUZEYLERI] == []


def test_lifecycle_touches_plan2_through_the_identity_module_only():
    """Hüküm (a)'nın BİÇİM ayağı + hüküm (c): tek kenar, modül olarak import edilir."""
    path = Path(_lifecycle_module.__file__)
    pipeline = [m for m in _import_edilen_moduller(path) if "sector_pipeline" in m]
    assert pipeline == ["app.services.sector_pipeline"], pipeline
    from_pipeline = [
        (m, adlar) for m, adlar in _from_importlar(path) if "sector_pipeline" in m
    ]
    assert from_pipeline == [("app.services.sector_pipeline", ["identity"])], from_pipeline
