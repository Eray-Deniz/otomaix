-- Migration 032: Sektör bilgi paketi — tablolar, kolonlar, DB garantileri
--
-- Kapsam (spec §3.3 / §3.8, plan Task 2):
--   1. social.sector_research_artifacts  — ham kanıt katmanı (salt-ekleme)
--   2. social.sector_packages            — sürümlü paket katmanı (durum geçişleri meşru)
--   3. social.brands.sub_sector_id       — marka → alt sektör ataması (K-08b)
--   4. social.sectors reparenting yasağı — K-08b'nin ayna ayağı
--   5. social.posts.package_id/_version  — K-07 damga temsili (bileşik FK, MATCH FULL)
--   6. social.generation_stamps          — üretim-anı damga makbuzu (tek kullanımlık)
--
-- İki katman ayrımı (spec §3.1): ham kanıt DEĞİŞTİRİLEMEZ, paket katmanı sürümlenir.
-- Embedding kolonu bilinçli YOKTUR — paket erişimi deterministiktir.

-- ---------------------------------------------------------------------------
-- 1. Ham araştırma kanıtı — salt-ekleme
-- ---------------------------------------------------------------------------
--
-- `sector_slug` bilinçli olarak FK DEĞİLDİR (K-08a): araştırma, sektör satırı
-- açılmadan koşabilmeli. Katmanlar arası bağ `run_id`'dir.

CREATE TABLE IF NOT EXISTS social.sector_research_artifacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id TEXT NOT NULL,
    sector_slug TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('research', 'review', 'synthesis')),
    source TEXT NOT NULL,
    brief_ref TEXT,
    content_md TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sector_research_artifacts_slug_run
    ON social.sector_research_artifacts (sector_slug, run_id);

CREATE OR REPLACE FUNCTION social.reject_research_artifact_mutation()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION
        'social.sector_research_artifacts salt-ekleme tablosudur; % reddedildi', TG_OP
        USING ERRCODE = 'integrity_constraint_violation';
END;
$$;

DROP TRIGGER IF EXISTS sector_research_artifacts_append_only
    ON social.sector_research_artifacts;
CREATE TRIGGER sector_research_artifacts_append_only
    BEFORE UPDATE OR DELETE ON social.sector_research_artifacts
    FOR EACH ROW EXECUTE FUNCTION social.reject_research_artifact_mutation();

DROP TRIGGER IF EXISTS sector_research_artifacts_no_truncate
    ON social.sector_research_artifacts;
CREATE TRIGGER sector_research_artifacts_no_truncate
    BEFORE TRUNCATE ON social.sector_research_artifacts
    FOR EACH STATEMENT EXECUTE FUNCTION social.reject_research_artifact_mutation();

-- ---------------------------------------------------------------------------
-- 2. Sürümlü paket katmanı
-- ---------------------------------------------------------------------------
--
-- Salt-ekleme tetikleyicisi bu tabloya BİLİNÇLİ konmaz (spec §3.3): durum
-- geçişleri (draft → active → archived) meşru güncellemedir.
-- `run_id` NULLABLE kalır — K-110 AÇIK karardır, bu migration ona sonuç yazmaz.

CREATE TABLE IF NOT EXISTS social.sector_packages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sector_id UUID NOT NULL REFERENCES social.sectors(id),
    version INT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('draft', 'active', 'archived')),
    schema_version INT NOT NULL,
    content JSONB NOT NULL,
    decision_log JSONB NOT NULL DEFAULT '[]',
    run_id TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    activated_at TIMESTAMPTZ,
    -- Sektör içinde sürüm benzersizdir.
    CONSTRAINT sector_packages_sector_version_key UNIQUE (sector_id, version),
    -- Bileşik damga FK'sının hedefi (K-07): posts/generation_stamps buraya bağlanır.
    CONSTRAINT sector_packages_id_version_key UNIQUE (id, version)
);

-- Sektör başına tek `active` — kısmi benzersiz indeks.
CREATE UNIQUE INDEX IF NOT EXISTS uq_sector_packages_single_active
    ON social.sector_packages (sector_id)
    WHERE status = 'active';

-- ---------------------------------------------------------------------------
-- 3. K-08b — alt-sektör zorunluluğu (kısıt katmanı = DB)
-- ---------------------------------------------------------------------------
--
-- CHECK alt sorgu yapamaz; garanti BEFORE INSERT/UPDATE tetikleyicisindedir.
-- Tek fonksiyon iki tabloya hizmet eder; denetlenecek kolon adı TG_ARGV[0].

CREATE OR REPLACE FUNCTION social.require_sub_sector_reference()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    checked_column TEXT := TG_ARGV[0];
    referenced_id UUID;
    is_sub_sector BOOLEAN;
BEGIN
    referenced_id := (to_jsonb(NEW) ->> checked_column)::UUID;

    -- Atama YAPILMAMIŞ olabilir: NULL serbesttir, geri doldurma yoktur.
    IF referenced_id IS NULL THEN
        RETURN NEW;
    END IF;

    SELECT parent_sector_id IS NOT NULL
        INTO is_sub_sector
        FROM social.sectors
        WHERE id = referenced_id;

    -- Satır yoksa is_sub_sector NULL kalır — o da reddedilir (fail-closed).
    IF is_sub_sector IS NOT TRUE THEN
        RAISE EXCEPTION
            'social.%.% yalnizca alt sektor satirini kabul eder '
            '(parent_sector_id NOT NULL); reddedilen: %',
            TG_TABLE_NAME, checked_column, referenced_id
            USING ERRCODE = 'integrity_constraint_violation';
    END IF;

    RETURN NEW;
END;
$$;

ALTER TABLE social.brands
    ADD COLUMN IF NOT EXISTS sub_sector_id UUID REFERENCES social.sectors(id);

CREATE INDEX IF NOT EXISTS idx_brands_sub_sector_id
    ON social.brands (sub_sector_id);

DROP TRIGGER IF EXISTS brands_sub_sector_must_be_sub ON social.brands;
CREATE TRIGGER brands_sub_sector_must_be_sub
    BEFORE INSERT OR UPDATE ON social.brands
    FOR EACH ROW
    EXECUTE FUNCTION social.require_sub_sector_reference('sub_sector_id');

DROP TRIGGER IF EXISTS sector_packages_sector_must_be_sub ON social.sector_packages;
CREATE TRIGGER sector_packages_sector_must_be_sub
    BEFORE INSERT OR UPDATE ON social.sector_packages
    FOR EACH ROW
    EXECUTE FUNCTION social.require_sub_sector_reference('sector_id');

-- ---------------------------------------------------------------------------
-- 4. Reparenting yasağı — K-08b'nin ayna ayağı
-- ---------------------------------------------------------------------------
--
-- INSERT serbesttir; mevcut satırın `parent_sector_id`'si Faz 1'de HİÇ
-- degistirilemez. Aksi hâlde geçerli bir atamadan sonra alt satır köke
-- çevrilip alt-sektör invariantı sessizce çökerdi.

CREATE OR REPLACE FUNCTION social.reject_sector_reparenting()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF NEW.parent_sector_id IS DISTINCT FROM OLD.parent_sector_id THEN
        RAISE EXCEPTION
            'social.sectors.parent_sector_id Faz 1 de degistirilemez; % -> % reddedildi',
            OLD.parent_sector_id, NEW.parent_sector_id
            USING ERRCODE = 'integrity_constraint_violation';
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS sectors_reject_reparenting ON social.sectors;
CREATE TRIGGER sectors_reject_reparenting
    BEFORE UPDATE ON social.sectors
    FOR EACH ROW EXECUTE FUNCTION social.reject_sector_reparenting();

-- ---------------------------------------------------------------------------
-- 5. K-07 damga temsili — posts bileşik FK (MATCH FULL)
-- ---------------------------------------------------------------------------
--
-- MATCH FULL yarım-NULL çifti (yalnız id VEYA yalnız version) ve satırla
-- eşleşmeyen sürümü DB düzeyinde reddeder. Paketsiz üretimde ikisi de NULL.

ALTER TABLE social.posts ADD COLUMN IF NOT EXISTS package_id UUID;
ALTER TABLE social.posts ADD COLUMN IF NOT EXISTS package_version INT;

ALTER TABLE social.posts DROP CONSTRAINT IF EXISTS posts_package_stamp_fkey;
ALTER TABLE social.posts
    ADD CONSTRAINT posts_package_stamp_fkey
    FOREIGN KEY (package_id, package_version)
    REFERENCES social.sector_packages (id, version)
    MATCH FULL;

-- ---------------------------------------------------------------------------
-- 6. Üretim-anı damga makbuzu
-- ---------------------------------------------------------------------------
--
-- Üretici çağrı (caption / kısa video stage-1) buraya satır yazar, istemciye
-- yalnız opak kimlik döner. `consumed_at` tek-kullanım işaretidir; tüketim
-- davranışı Task 12'dedir.
--
-- F18: `brand_id` ON DELETE CASCADE — marka silme sözleşmesi korunur. Makbuz
-- ara-tablo verisidir, süresiz-saklama rejimine TABİ DEĞİLDİR; paket ve ham
-- kanıt satırları markadan bağımsız yaşamaya devam eder.
--
-- Bileşik FK burada MATCH FULL DEĞİLDİR: iki kolon da NOT NULL olduğundan
-- yarım çift zaten imkânsızdır.

CREATE TABLE IF NOT EXISTS social.generation_stamps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand_id UUID NOT NULL REFERENCES social.brands(id) ON DELETE CASCADE,
    package_id UUID NOT NULL,
    package_version INT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    consumed_at TIMESTAMPTZ,
    CONSTRAINT generation_stamps_package_fkey
        FOREIGN KEY (package_id, package_version)
        REFERENCES social.sector_packages (id, version)
);

-- ---------------------------------------------------------------------------
-- Belgeleme
-- ---------------------------------------------------------------------------

COMMENT ON TABLE social.sector_research_artifacts IS
    'Sektor bilgi paketi — ham kanit katmani. Salt-ekleme: UPDATE/DELETE/TRUNCATE tetikleyiciyle reddedilir. sector_slug FK degildir (K-08a).';
COMMENT ON TABLE social.sector_packages IS
    'Sektor bilgi paketi — surumlu paket katmani. Sektor basina tek active (kismi benzersiz indeks); salt-ekleme tetikleyicisi bilincli YOK.';
COMMENT ON COLUMN social.sector_packages.run_id IS
    'K-110 ACIK — nullable kalir; arastirma kosusuyla bag zorunlu degildir.';
COMMENT ON COLUMN social.brands.sub_sector_id IS
    'K-08b — yalnizca parent_sector_id NOT NULL olan sektor satirini kabul eder (tetikleyici garantisi). NULL = paketsiz marka.';
COMMENT ON COLUMN social.posts.package_id IS
    'K-07 damga — package_version ile birlikte MATCH FULL bilesik FK. Paketsiz uretimde her ikisi de NULL.';
COMMENT ON TABLE social.generation_stamps IS
    'K-07 uretim-ani damga makbuzu. consumed_at tek-kullanim isareti; marka silinince CASCADE ile gider (F18).';
