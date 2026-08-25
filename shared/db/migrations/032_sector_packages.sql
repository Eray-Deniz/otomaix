-- Migration 032: Sektör bilgi paketi — tablolar, kolonlar, DB garantileri
--
-- Kapsam (spec §3.3 / §3.8, plan Task 2):
--   1. social.sector_research_artifacts  — ham kanıt katmanı (salt-ekleme)
--   2. social.sector_packages            — sürümlü paket katmanı (durum geçişleri meşru)
--   3. social.brands.sub_sector_id       — marka → alt sektör ataması (K-08b)
--   4. social.sectors reparenting yasağı — K-08b'nin ayna ayağı
--   5. social.posts.package_id/_version  — K-07 damga temsili (bileşik FK, MATCH FULL)
--   6. social.generation_stamps          — üretim-anı damga makbuzu (tek kullanımlık)
--   7. Garanti doğrulaması              — fail-closed katalog kontrolü (F7)
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

-- ---------------------------------------------------------------------------
-- 7. Garanti doğrulaması — fail-closed (F7)
-- ---------------------------------------------------------------------------
--
-- `CREATE TABLE / INDEX IF NOT EXISTS` yalnız o ADDA bir nesne var mı diye
-- bakar, TANIMINI doğrulamaz. Aynı adda ama yanlış tanımlı bir nesne önceden
-- duruyorsa DDL sessizce atlanır, migration NOTICE basıp BAŞARIYLA biter ve
-- yukarıda adı geçen garanti fark edilmeden yok olur. Canlıya uygulama elle
-- yapıldığından (plan Task 3/16) bu makul bir deploy senaryosudur.
--
-- Aşağıdaki blok DDL'den SONRA koşar: katalogtan (pg_index / pg_constraint /
-- pg_trigger) GERÇEK tanımı okur ve planın Task 2 "Interfaces" bölümünde
-- garanti sayılan her maddeyi beklenen imzasıyla karşılaştırır. Tutmayan varsa
-- hepsi tek mesajda (ad + beklenen + görülen) raporlanır ve migration
-- EXCEPTION ile durur.
--
-- İdempotentlik BOZULMAZ: `IF NOT EXISTS` desenleri yerinde kalır; doğru şema
-- üstünde bu blok sessizdir.
--
-- Otomatik adlandırılan kısıtlar (CHECK'ler, `brand_id` FK'sı) ADLA değil
-- KOLONLA aranır — ad üretimi Postgres'e aittir, garanti kolona bağlıdır.
--
-- TANIM ≠ UYGULANMA (F7 tur 3): doğru imzalı bir nesne yine de hiçbir şeyi
-- zorlamıyor olabilir. Bu yüzden imzanın yanında uygulanma durumu da okunur:
--   * indeksler — `indisvalid/indisready/indislive`. Yarım kalmış (invalid)
--     bir indekste `indisunique` true kalır ama benzersizlik UYGULANMAZ.
--     Hem kısmi indeks hem iki UNIQUE kısıtının arkasındaki indeks denetlenir.
--   * yabancı anahtarlar — `conenforced` / `convalidated` ve kısıtı fiilen
--     yürüten iç tetikleyiciler (`pg_trigger.tgconstraint`, dördü de
--     `tgenabled='O'`). `ALTER TABLE ... DISABLE TRIGGER ALL` kısıt tanımını
--     DEĞİŞTİRMEDEN FK'yı kapatır; tanıma bakan bir kontrol bunu göremez.
-- `conenforced` PostgreSQL 18 kolonudur; bu sunucuda (18.3) varlığı
-- `pg_attribute` üstünden ÖLÇÜLDÜ. Daha eski bir sunucuda blok "column does
-- not exist" ile durur — fail-closed, sessiz geçiş yoktur.
--
-- ELLE UYGULARKEN: psql'i `-v ON_ERROR_STOP=1` ile çağırın. Ölçüldü — bayrak
-- yokken hata mesajı yine basılır ama psql çıkış kodu 0 döner; sıfır-dışı çıkış
-- yalnız bu bayrakla gelir (testler ve `conftest` onu zaten kullanır).

DO $verify$
DECLARE
    failures TEXT;
BEGIN
    WITH expected(label, want) AS (
        VALUES
            -- Sektör başına tek `active`: gerçekten UNIQUE mi, (sector_id)
            -- üstünde mi, predicate tam olarak `status = 'active'` mi, ve
            -- indeks GERÇEKTEN uygulanıyor mu (valid/ready/live).
            ('uq_sector_packages_single_active',
             'unique=true cols=sector_id pred=(status = ''active''::text)'
             ' valid=true ready=true live=true'),

            -- Sürüm benzersizliği + bileşik damga FK'sının hedefi.
            ('sector_packages_sector_version_key',
             'u|UNIQUE (sector_id, version)|idx valid=true ready=true live=true'),
            ('sector_packages_id_version_key',
             'u|UNIQUE (id, version)|idx valid=true ready=true live=true'),

            -- K-07 damga temsili: bileşik FK ve MATCH FULL (matchtype 'f').
            ('posts_package_stamp_fkey',
             'f|matchtype=f|FOREIGN KEY (package_id, package_version)'
             ' REFERENCES social.sector_packages(id, version) MATCH FULL'
             '|enforced=true validated=true trig=4 enabled=4'),

            -- Makbuz: bileşik FK + marka silmede CASCADE (deltype 'c').
            ('generation_stamps_package_fkey',
             'f|matchtype=s|FOREIGN KEY (package_id, package_version)'
             ' REFERENCES social.sector_packages(id, version)'
             '|enforced=true validated=true trig=4 enabled=4'),
            ('generation_stamps.brand_id FK',
             'f|ondelete=c|FOREIGN KEY (brand_id)'
             ' REFERENCES social.brands(id) ON DELETE CASCADE'
             '|enforced=true validated=true trig=4 enabled=4'),

            -- Değer kümesi kısıtları.
            ('sector_research_artifacts.kind CHECK',
             'c|CHECK ((kind = ANY (ARRAY[''research''::text, ''review''::text,'
             ' ''synthesis''::text])))'),
            ('sector_packages.status CHECK',
             'c|CHECK ((status = ANY (ARRAY[''draft''::text, ''active''::text,'
             ' ''archived''::text])))'),

            -- Salt-ekleme: UPDATE/DELETE **ve** TRUNCATE ayağı.
            ('sector_research_artifacts_append_only',
             'CREATE TRIGGER sector_research_artifacts_append_only BEFORE DELETE'
             ' OR UPDATE ON social.sector_research_artifacts FOR EACH ROW EXECUTE'
             ' FUNCTION social.reject_research_artifact_mutation()|enabled=O'),
            ('sector_research_artifacts_no_truncate',
             'CREATE TRIGGER sector_research_artifacts_no_truncate BEFORE TRUNCATE'
             ' ON social.sector_research_artifacts FOR EACH STATEMENT EXECUTE'
             ' FUNCTION social.reject_research_artifact_mutation()|enabled=O'),

            -- K-08b alt-sektör zorunluluğu (iki tablo; TG_ARGV[0] = kolon adı).
            ('brands_sub_sector_must_be_sub',
             'CREATE TRIGGER brands_sub_sector_must_be_sub BEFORE INSERT OR UPDATE'
             ' ON social.brands FOR EACH ROW EXECUTE FUNCTION'
             ' social.require_sub_sector_reference(''sub_sector_id'')|enabled=O'),
            ('sector_packages_sector_must_be_sub',
             'CREATE TRIGGER sector_packages_sector_must_be_sub BEFORE INSERT OR'
             ' UPDATE ON social.sector_packages FOR EACH ROW EXECUTE FUNCTION'
             ' social.require_sub_sector_reference(''sector_id'')|enabled=O'),

            -- Reparenting yasağı — K-08b'nin ayna ayağı.
            ('sectors_reject_reparenting',
             'CREATE TRIGGER sectors_reject_reparenting BEFORE UPDATE ON'
             ' social.sectors FOR EACH ROW EXECUTE FUNCTION'
             ' social.reject_sector_reparenting()|enabled=O'),

            -- ---------------------------------------------------------------
            -- TABLO + KOLON İMZASI + BİRİNCİL ANAHTAR (final review, 2026-08-25)
            --
            -- Aşağıdaki kısıt/indeks/tetikleyici kontrolleri tablonun sözleşmesinin
            -- TAMAMI DEĞİLDİR. 034'te ÖLÇÜLDÜ: kolonu yanlış tipte, birincil
            -- anahtarsız ve varsayılansız ama CHECK'leri ve indeksleri birebir
            -- doğru olan sahte bir tablo migration'dan rc=0 ile geçiyordu; ayrıca
            -- `UNLOGGED` bir tablo diğer bütün imzaları AYNEN üretir ve temiz
            -- olmayan bir kapanışta TRUNCATE edilir (commit edilmiş satırlar yok
            -- olur). Aynı boşluk 032'de de vardı — 034 sertleştirilirken burası
            -- bilinçli olarak açık bırakılmıştı, final review yeniden buldu.
            --
            -- İmza attnum sırasındadır ve TAM eşleşmedir: eksik kolon da FAZLA
            -- kolon da yakalanır.
            -- ---------------------------------------------------------------
            ('sector_research_artifacts tablo imzası',
             'relkind=r relpersistence=p partition=f rls=f force_rls=f'),

            ('sector_research_artifacts kolon imzası',
             'id:uuid:nn:gen_random_uuid() && run_id:text:nn:- && sector_slug:text:nn:- && kind:text:nn:- && source:text:nn:- && brief_ref:text:null:- && content_md:text:nn:- && created_at:timestamp with time zone:null:now()'),

            ('sector_research_artifacts PRIMARY KEY',
             'p|PRIMARY KEY (id)|enforced=true validated=true'),
            ('sector_packages tablo imzası',
             'relkind=r relpersistence=p partition=f rls=f force_rls=f'),

            ('sector_packages kolon imzası',
             'id:uuid:nn:gen_random_uuid() && sector_id:uuid:nn:- && version:integer:nn:- && status:text:nn:- && schema_version:integer:nn:- && content:jsonb:nn:- && decision_log:jsonb:nn:''[]''::jsonb && run_id:text:null:- && created_at:timestamp with time zone:null:now() && activated_at:timestamp with time zone:null:-'),

            ('sector_packages PRIMARY KEY',
             'p|PRIMARY KEY (id)|enforced=true validated=true'),
            ('generation_stamps tablo imzası',
             'relkind=r relpersistence=p partition=f rls=f force_rls=f'),

            ('generation_stamps kolon imzası',
             'id:uuid:nn:gen_random_uuid() && brand_id:uuid:nn:- && package_id:uuid:nn:- && package_version:integer:nn:- && created_at:timestamp with time zone:null:now() && consumed_at:timestamp with time zone:null:-'),

            ('generation_stamps PRIMARY KEY',
             'p|PRIMARY KEY (id)|enforced=true validated=true')
    ),
    observed(label, got) AS (
        VALUES
            ('sector_research_artifacts tablo imzası',
             (SELECT format('relkind=%s relpersistence=%s partition=%s'
                            ' rls=%s force_rls=%s',
                            c.relkind, c.relpersistence,
                            CASE WHEN c.relispartition THEN 't' ELSE 'f' END,
                            CASE WHEN c.relrowsecurity THEN 't' ELSE 'f' END,
                            CASE WHEN c.relforcerowsecurity THEN 't' ELSE 'f' END)
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
               WHERE n.nspname = 'social' AND c.relname = 'sector_research_artifacts')),

            ('sector_research_artifacts kolon imzası',
             (SELECT string_agg(format('%s:%s:%s:%s',
                                       a.attname,
                                       format_type(a.atttypid, a.atttypmod),
                                       CASE WHEN a.attnotnull
                                            THEN 'nn' ELSE 'null' END,
                                       coalesce(pg_get_expr(d.adbin, d.adrelid),
                                                '-')),
                                ' && ' ORDER BY a.attnum)
                FROM pg_attribute a
                LEFT JOIN pg_attrdef d
                       ON d.adrelid = a.attrelid AND d.adnum = a.attnum
               WHERE a.attrelid = 'social.sector_research_artifacts'::regclass
                 AND a.attnum > 0
                 AND NOT a.attisdropped)),

            ('sector_research_artifacts PRIMARY KEY',
             (SELECT string_agg(format('%s|%s|enforced=%s validated=%s',
                                       k.contype, pg_get_constraintdef(k.oid),
                                       CASE WHEN k.conenforced
                                            THEN 'true' ELSE 'false' END,
                                       CASE WHEN k.convalidated
                                            THEN 'true' ELSE 'false' END),
                                ' && ')
                FROM pg_constraint k
               WHERE k.conrelid = 'social.sector_research_artifacts'::regclass
                 AND k.contype = 'p')),

            ('sector_packages tablo imzası',
             (SELECT format('relkind=%s relpersistence=%s partition=%s'
                            ' rls=%s force_rls=%s',
                            c.relkind, c.relpersistence,
                            CASE WHEN c.relispartition THEN 't' ELSE 'f' END,
                            CASE WHEN c.relrowsecurity THEN 't' ELSE 'f' END,
                            CASE WHEN c.relforcerowsecurity THEN 't' ELSE 'f' END)
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
               WHERE n.nspname = 'social' AND c.relname = 'sector_packages')),

            ('sector_packages kolon imzası',
             (SELECT string_agg(format('%s:%s:%s:%s',
                                       a.attname,
                                       format_type(a.atttypid, a.atttypmod),
                                       CASE WHEN a.attnotnull
                                            THEN 'nn' ELSE 'null' END,
                                       coalesce(pg_get_expr(d.adbin, d.adrelid),
                                                '-')),
                                ' && ' ORDER BY a.attnum)
                FROM pg_attribute a
                LEFT JOIN pg_attrdef d
                       ON d.adrelid = a.attrelid AND d.adnum = a.attnum
               WHERE a.attrelid = 'social.sector_packages'::regclass
                 AND a.attnum > 0
                 AND NOT a.attisdropped)),

            ('sector_packages PRIMARY KEY',
             (SELECT string_agg(format('%s|%s|enforced=%s validated=%s',
                                       k.contype, pg_get_constraintdef(k.oid),
                                       CASE WHEN k.conenforced
                                            THEN 'true' ELSE 'false' END,
                                       CASE WHEN k.convalidated
                                            THEN 'true' ELSE 'false' END),
                                ' && ')
                FROM pg_constraint k
               WHERE k.conrelid = 'social.sector_packages'::regclass
                 AND k.contype = 'p')),

            ('generation_stamps tablo imzası',
             (SELECT format('relkind=%s relpersistence=%s partition=%s'
                            ' rls=%s force_rls=%s',
                            c.relkind, c.relpersistence,
                            CASE WHEN c.relispartition THEN 't' ELSE 'f' END,
                            CASE WHEN c.relrowsecurity THEN 't' ELSE 'f' END,
                            CASE WHEN c.relforcerowsecurity THEN 't' ELSE 'f' END)
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
               WHERE n.nspname = 'social' AND c.relname = 'generation_stamps')),

            ('generation_stamps kolon imzası',
             (SELECT string_agg(format('%s:%s:%s:%s',
                                       a.attname,
                                       format_type(a.atttypid, a.atttypmod),
                                       CASE WHEN a.attnotnull
                                            THEN 'nn' ELSE 'null' END,
                                       coalesce(pg_get_expr(d.adbin, d.adrelid),
                                                '-')),
                                ' && ' ORDER BY a.attnum)
                FROM pg_attribute a
                LEFT JOIN pg_attrdef d
                       ON d.adrelid = a.attrelid AND d.adnum = a.attnum
               WHERE a.attrelid = 'social.generation_stamps'::regclass
                 AND a.attnum > 0
                 AND NOT a.attisdropped)),

            ('generation_stamps PRIMARY KEY',
             (SELECT string_agg(format('%s|%s|enforced=%s validated=%s',
                                       k.contype, pg_get_constraintdef(k.oid),
                                       CASE WHEN k.conenforced
                                            THEN 'true' ELSE 'false' END,
                                       CASE WHEN k.convalidated
                                            THEN 'true' ELSE 'false' END),
                                ' && ')
                FROM pg_constraint k
               WHERE k.conrelid = 'social.generation_stamps'::regclass
                 AND k.contype = 'p')),
            ('uq_sector_packages_single_active',
             (SELECT format(
                         'unique=%s cols=%s pred=%s valid=%s ready=%s live=%s',
                         CASE WHEN i.indisunique THEN 'true' ELSE 'false' END,
                         (SELECT string_agg(a.attname, ',' ORDER BY k.ord)
                            FROM unnest(i.indkey) WITH ORDINALITY AS k(attnum, ord)
                            JOIN pg_attribute a
                              ON a.attrelid = i.indrelid AND a.attnum = k.attnum),
                         coalesce(pg_get_expr(i.indpred, i.indrelid),
                                  '<kismi degil>'),
                         CASE WHEN i.indisvalid THEN 'true' ELSE 'false' END,
                         CASE WHEN i.indisready THEN 'true' ELSE 'false' END,
                         CASE WHEN i.indislive THEN 'true' ELSE 'false' END)
                FROM pg_index i
                JOIN pg_class c ON c.oid = i.indexrelid
                JOIN pg_namespace n ON n.oid = c.relnamespace
               WHERE n.nspname = 'social'
                 AND c.relname = 'uq_sector_packages_single_active'
                 AND i.indrelid = 'social.sector_packages'::regclass)),

            -- UNIQUE kısıtı ARKASINDAKİ indeks de uygulanıyor olmalı: `conindid`
            -- üstünden JOIN edilir, indeks yoksa satır düşer → '<nesne yok>'.
            ('sector_packages_sector_version_key',
             (SELECT format('%s|%s|idx valid=%s ready=%s live=%s',
                            k.contype, pg_get_constraintdef(k.oid),
                            CASE WHEN i.indisvalid THEN 'true' ELSE 'false' END,
                            CASE WHEN i.indisready THEN 'true' ELSE 'false' END,
                            CASE WHEN i.indislive THEN 'true' ELSE 'false' END)
                FROM pg_constraint k
                JOIN pg_index i ON i.indexrelid = k.conindid
               WHERE k.conrelid = 'social.sector_packages'::regclass
                 AND k.conname = 'sector_packages_sector_version_key')),
            ('sector_packages_id_version_key',
             (SELECT format('%s|%s|idx valid=%s ready=%s live=%s',
                            k.contype, pg_get_constraintdef(k.oid),
                            CASE WHEN i.indisvalid THEN 'true' ELSE 'false' END,
                            CASE WHEN i.indisready THEN 'true' ELSE 'false' END,
                            CASE WHEN i.indislive THEN 'true' ELSE 'false' END)
                FROM pg_constraint k
                JOIN pg_index i ON i.indexrelid = k.conindid
               WHERE k.conrelid = 'social.sector_packages'::regclass
                 AND k.conname = 'sector_packages_id_version_key')),
            ('posts_package_stamp_fkey',
             (SELECT format('%s|matchtype=%s|%s|enforced=%s validated=%s'
                            ' trig=%s enabled=%s',
                            k.contype, k.confmatchtype,
                            pg_get_constraintdef(k.oid),
                            CASE WHEN k.conenforced THEN 'true' ELSE 'false' END,
                            CASE WHEN k.convalidated THEN 'true' ELSE 'false' END,
                            (SELECT count(*) FROM pg_trigger t
                              WHERE t.tgconstraint = k.oid),
                            (SELECT count(*) FROM pg_trigger t
                              WHERE t.tgconstraint = k.oid
                                AND t.tgenabled = 'O'))
                FROM pg_constraint k
               WHERE k.conrelid = 'social.posts'::regclass
                 AND k.conname = 'posts_package_stamp_fkey')),
            ('generation_stamps_package_fkey',
             (SELECT format('%s|matchtype=%s|%s|enforced=%s validated=%s'
                            ' trig=%s enabled=%s',
                            k.contype, k.confmatchtype,
                            pg_get_constraintdef(k.oid),
                            CASE WHEN k.conenforced THEN 'true' ELSE 'false' END,
                            CASE WHEN k.convalidated THEN 'true' ELSE 'false' END,
                            (SELECT count(*) FROM pg_trigger t
                              WHERE t.tgconstraint = k.oid),
                            (SELECT count(*) FROM pg_trigger t
                              WHERE t.tgconstraint = k.oid
                                AND t.tgenabled = 'O'))
                FROM pg_constraint k
               WHERE k.conrelid = 'social.generation_stamps'::regclass
                 AND k.conname = 'generation_stamps_package_fkey')),

            -- Kolon bazlı arama: birden çok eşleşme tek imzada birleşir, böylece
            -- beklenenden sapma (eksik VEYA fazla kısıt) fail-closed yakalanır.
            ('generation_stamps.brand_id FK',
             (SELECT string_agg(format('%s|ondelete=%s|%s|enforced=%s'
                                       ' validated=%s trig=%s enabled=%s',
                                       k.contype,
                                       k.confdeltype,
                                       pg_get_constraintdef(k.oid),
                                       CASE WHEN k.conenforced
                                            THEN 'true' ELSE 'false' END,
                                       CASE WHEN k.convalidated
                                            THEN 'true' ELSE 'false' END,
                                       (SELECT count(*) FROM pg_trigger t
                                         WHERE t.tgconstraint = k.oid),
                                       (SELECT count(*) FROM pg_trigger t
                                         WHERE t.tgconstraint = k.oid
                                           AND t.tgenabled = 'O')),
                                ' && ' ORDER BY k.conname)
                FROM pg_constraint k
               WHERE k.conrelid = 'social.generation_stamps'::regclass
                 AND k.contype = 'f'
                 AND k.conkey = ARRAY[
                         (SELECT a.attnum FROM pg_attribute a
                           WHERE a.attrelid = 'social.generation_stamps'::regclass
                             AND a.attname = 'brand_id')]::int2[])),
            ('sector_research_artifacts.kind CHECK',
             (SELECT string_agg(format('%s|%s', k.contype,
                                       pg_get_constraintdef(k.oid)),
                                ' && ' ORDER BY k.conname)
                FROM pg_constraint k
               WHERE k.conrelid = 'social.sector_research_artifacts'::regclass
                 AND k.contype = 'c'
                 AND k.conkey = ARRAY[
                         (SELECT a.attnum FROM pg_attribute a
                           WHERE a.attrelid
                                 = 'social.sector_research_artifacts'::regclass
                             AND a.attname = 'kind')]::int2[])),
            ('sector_packages.status CHECK',
             (SELECT string_agg(format('%s|%s', k.contype,
                                       pg_get_constraintdef(k.oid)),
                                ' && ' ORDER BY k.conname)
                FROM pg_constraint k
               WHERE k.conrelid = 'social.sector_packages'::regclass
                 AND k.contype = 'c'
                 AND k.conkey = ARRAY[
                         (SELECT a.attnum FROM pg_attribute a
                           WHERE a.attrelid = 'social.sector_packages'::regclass
                             AND a.attname = 'status')]::int2[])),

            -- `pg_get_triggerdef` zamanlama + olay kümesi + satır/deyim düzeyi +
            -- fonksiyon + TG_ARGV'yi tek dizede taşır; `tgenabled` ayrıca
            -- kontrol edilir (devre dışı tetikleyici de fail-open'dır).
            ('sector_research_artifacts_append_only',
             (SELECT format('%s|enabled=%s', pg_get_triggerdef(t.oid), t.tgenabled)
                FROM pg_trigger t
               WHERE NOT t.tgisinternal
                 AND t.tgrelid = 'social.sector_research_artifacts'::regclass
                 AND t.tgname = 'sector_research_artifacts_append_only')),
            ('sector_research_artifacts_no_truncate',
             (SELECT format('%s|enabled=%s', pg_get_triggerdef(t.oid), t.tgenabled)
                FROM pg_trigger t
               WHERE NOT t.tgisinternal
                 AND t.tgrelid = 'social.sector_research_artifacts'::regclass
                 AND t.tgname = 'sector_research_artifacts_no_truncate')),
            ('brands_sub_sector_must_be_sub',
             (SELECT format('%s|enabled=%s', pg_get_triggerdef(t.oid), t.tgenabled)
                FROM pg_trigger t
               WHERE NOT t.tgisinternal
                 AND t.tgrelid = 'social.brands'::regclass
                 AND t.tgname = 'brands_sub_sector_must_be_sub')),
            ('sector_packages_sector_must_be_sub',
             (SELECT format('%s|enabled=%s', pg_get_triggerdef(t.oid), t.tgenabled)
                FROM pg_trigger t
               WHERE NOT t.tgisinternal
                 AND t.tgrelid = 'social.sector_packages'::regclass
                 AND t.tgname = 'sector_packages_sector_must_be_sub')),
            ('sectors_reject_reparenting',
             (SELECT format('%s|enabled=%s', pg_get_triggerdef(t.oid), t.tgenabled)
                FROM pg_trigger t
               WHERE NOT t.tgisinternal
                 AND t.tgrelid = 'social.sectors'::regclass
                 AND t.tgname = 'sectors_reject_reparenting'))
    )
    SELECT string_agg(
               format('%s -> beklenen [%s] · gorulen [%s]',
                      e.label, e.want, coalesce(o.got, '<nesne yok>')),
               E'\n  - ' ORDER BY e.label)
      INTO failures
      FROM expected e
      LEFT JOIN observed o ON o.label = e.label
     WHERE o.got IS DISTINCT FROM e.want;

    IF failures IS NOT NULL THEN
        RAISE EXCEPTION 'migration 032 garanti dogrulamasi BASARISIZ:%',
            E'\n  - ' || failures
            USING ERRCODE = 'integrity_constraint_violation',
                  HINT = 'Ayni adda YANLIS TANIMLI bir nesne var; IF NOT EXISTS '
                         'onu DEGISTIRMEZ. Nesneyi elle dusurup migration i '
                         'yeniden uygulayin.';
    END IF;
END
$verify$;
