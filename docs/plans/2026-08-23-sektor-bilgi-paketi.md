---
title: Sektör Bilgi Paketi — Plan 1/2 Runtime Çekirdeği
status: plan-approved
date: 2026-08-23
source_spec: docs/specs/2026-08-21-sektor-bilgi-paketi.md
source_spec_unapproved_override: false
noisy_review_override: false
unresolved_high_severity_override: false
codex_plan_review_status: approved
codex_plan_review_iterations: 0
codex_plan_review_log: docs/reviews/codex/2026-08-23-sektor-bilgi-paketi-plan.md
---

# Sektör Bilgi Paketi — Plan 1/2: Runtime Çekirdeği Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **Workflow override:** Otomaix `/root/otomaix/CLAUDE.md` "Skill Chain Override Notları" gereği `executing-plans`'in auto-chain'leri (`finishing-a-development-branch`, `using-git-worktrees`) bilinçli çağrılmaz.

**Goal:** Sektör bilgi paketi sisteminin runtime çekirdeğini kurmak: migration 032 + taksonomi korumaları + Katman-1 byte-exact prompt kapısı + tek-kapı enjeksiyon + atama akışı + kanal envanteri + bildirim mekanizması.

**Architecture:** Spec §13.2 kurulum sırasına sadık tek-hat ilerleme. Tüm prompt yüzeyleri tek bir `SectorPackageContext | None` çözümleyicisini tüketir; `None` dalı mevcut kod yolunu bayt değiştirmeden çalıştırır (Katman-1 kapısı bunu her artımda kanıtlar). Paketi ÜRETEN/AKTİVE EDEN işletim hattı (araştırma→hakemlik→sentez→motor→komut ailesi→pilot) **Plan 2'nin kapsamıdır** — bu plan yalnız DB sözleşmesini, runtime tüketimini ve Plan 2'ye teslim edilen servis arayüzlerini kurar.

**Tech Stack:** FastAPI + asyncpg + Redis (mevcut backend), PostgreSQL migration (`shared/db/migrations/032_*.sql`), pytest (bu planda bootstrap edilir), Next.js frontend (atama/envanter UI).

**Spec:** `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (status: `spec-approved`). Karar statüsünde spec esastır; snapshot gövdesindeki `[AÇIK]` ifadeleri 51 kapanış için bayattır.

## Global Constraints

- **Byte-exact koruma (spec §1.3, §5.1):** paketsiz markada modele giden prompt parçalarında TEK BAYT fark = RED. Karşılaştırma `cmp` düzeyi; normalize/whitespace/anlam toleransı yok. Fixture, enjeksiyon değişikliklerinden ÖNCE dondurulur (Task 6-7); Task 8'den itibaren her task'ın son adımı tam sweep koşar.
- **Yan-yana basım yasağı (spec §4.1):** aktif paket varken kök `SECTOR_GUIDANCE` bloğu hiçbir yüzeyde paketle birlikte basılmaz — paket YERİNE geçer (fikir önerme ucu dahil).
- **Karar uydurma yasağı:** açık K-ID'lere bu plan sonuç yazmaz — "Karar Kapıları" bölümündeki davranış bağlayıcıdır.
- **İlke 9:** ölçülmemiş hiçbir değer (token maliyeti, ≤5 tavanı, tur süresi, K-11 örneklem/eşik) kabul kriteri/eşik/kapı yapılmaz.
- **Test'te canlı LLM/fal.ai çağrısı YASAK** (stokastiklik + kredi israfı yasağı): Anthropic istemcisi monkeypatch ile kesilir; fal.ai hiç çağrılmaz.
- **Mevcut konvansiyonlar:** asyncpg jsonb codec (`json.dumps` + `::jsonb` cast kullanma); sahiplik kontrolü 404; router'da statik path dinamikten önce; migration'lar `shared/db/migrations/` altında numaralı.
- **Test DB:** testler `127.0.0.1:5433`'teki PostgreSQL'de **`otomaix_test`** adlı atılabilir veritabanına koşar; canlı `otomaix` veritabanına test yazımı YASAK.
- **Dokunulmazlar (spec §17.2):** `brands.sector` TEXT canlı girdi — değiştirilmez; trend katmanı değiştirilmez (yalnız doğrulanır); 22 legacy şablonun statüsü bu işte ele alınmaz.

## Karar Kapıları (açık K-ID'ler — bu planın davranışı)

| K-ID | Konu | Bu planın davranışı |
|---|---|---|
| K-02 | Video hareket dili (3 seçenek) | **Bekletilir.** Hareket enjeksiyonu YAPILMAZ; `_MOTION_PROMPTS` havuzu paketsiz VE paketli yolda aynen korunur (Katman-1 fixture'ı pinler). `content.video_kodlar` iç alan adları da K-02'ye bağlı → doğrulayıcı v1 iç yapıyı opak doğrular (Task 8). Karar kapanınca `schema_version` artışı + ayrı iş. |
| K-06 | Legacy kısa video ucu akıbeti | **Bekletilir; fixture bugünkü davranışı dondurur** (bozuk-boş `SECTOR_GUIDANCE` sonucu dahil — spec §5.2/8: fixture'a koşulsuz girer, K-06 yalnız beklenen değeri belirler). Uç düzeltilmez. |
| K-15 (a) | Eksik alan ↔ tüm-yol-düşer sınırı | **Bekletilir.** Çözümleyici yalnız spec'in bağladığı davranışı kurar: paket okunamıyor/şema-geçersiz → TÜM yol mevcut yola düşer (alan-düzeyi atlama dalı YAZILMAZ). |
| K-110 | Paket tarafında `run_id` zorunluluğu | **Bekletilir.** `sector_packages.run_id` nullable kalır; NOT NULL kısıtı karar kapanınca ayrı migration. |
| K-94 | Onay anında base-sürüm geçersizlik KURALI | **Mekanizma kurulur, kural bekletilir.** `ActivationGateEvidence.expected_active_version` OPSİYONELDİR: dolu gelirse uyuşmazlık geçişi reddeder (yetenek); alanın onay akışında ZORUNLU olup olmayacağı K-94'ün kendisidir — Plan 2 onay yüzeyi, karar kapanınca bağlar. |
| K-11, K-12, K-13 | Katman-2 örneklem/eşik, maliyet, tavan | Plan 1'e girmez (pilot/Plan 2 ölçüm kalemleri); hiçbiri kapı yapılmaz. |
| K-41, K-42, K-23 vb. motor/onay-yüzeyi kararları | Plan 2 alanı — bu planda hiçbir görev bunlara dokunmaz. |

> **[SONRADAN EKLENDİ — 2026-08-24; spec eksik yazıldığı için, plan da eksiği miras aldı]**
> Yukarıdaki tabloda **K-02 "Bekletilir"** diye işlenmiştir. Bu satır spec'in "açık" kaydına
> dayanıyordu; spec-input'a dönüldüğünde kaydın eksik taşındığı görüldü
> (`docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md`, karar kartı satır 2533):
>
> - Input K-02 için **A şıkkını ÖNERİR** — *"paket `video_kodlar`'ından sektöre özgü hareket
>   havuzu; paketsizde mevcut liste aynen kalır"* — gerekçesi *"paketsiz üretimde modele giden
>   prompt parçaları değişmez ve **ek model çağrısı doğmaz**"*.
> - Kararın sahibi **teknik sahiptir**; ürün sahibi **yalnız A elenirse** devreye girer.
> - Çözüm yolu **"spec içinde teknik olarak çözülür"**; *"paketsiz prompt değişmeden havuz
>   beslenebiliyorsa **(A) seçenek tartışması düşer**"*.
> - Input K-02'yi ayrıca **"spec'te özellikle çözülmesi gereken teknik konular"** listesinin
>   2. maddesi olarak sayar (satır 3103).
>
> Ayrıca **K-113** ("hareket havuzu boşsa ne olacak" — input satır 2576, K-02'den AYRI
> seçilebilir) ne spec'e ne bu plana taşınmıştır.
>
> **Sonuç:** planın "bekletilir" hükmü yanlış bir zemine dayanıyor — K-02 spec sonrasına
> devredilecek bir ürün kararı değil, spec içinde kapanacak teknik bir kalemdi. Bu blok
> yalnız EKSİĞİ KAYDEDER; tablodaki hüküm değiştirilmemiştir ve K-02'nin nasıl kapanacağı
> ayrı bir karar turunun konusudur. Kapanış, aşağıdaki Task 8 ve Task 11 notlarını da
> yürürlüğe sokar.

> **[KARAR KAPANDI — 2026-08-24, Eray onayı]** Tablodaki **K-02 "Bekletilir"** hükmü
> YÜRÜRLÜKTEN KALKTI (satır tarihsel kayıt olarak durur). Yürürlükteki hüküm spec §11.5'in
> karar bloğudur: **K-02 = A (seçici modelde) · K-113 = A**. Özet:
>
> - Hareket havuzu paketin `video_kodlar.hareket` listesinden gelir, sektöre özeldir.
> - Seçimi **caption aşamasındaki MEVCUT model çağrısı** yapar — ayrı çağrı açılmaz
>   (ölçüldü: kısa video ucu script'siz istek kabul etmiyor, caption çağrısı zaten zorunlu).
> - İstemcinin döndürdüğü hareket metni sunucuda **havuz üyeliğine karşı doğrulanır**;
>   üye değilse aynı havuzdan belirleyici seçime düşülür.
> - Havuz boşsa bugünkü `_MOTION_PROMPTS` listesine düşülür (K-113 = A).
> - Paketsiz yolda hiçbir şey değişmez; Katman-1 byte-exact korunur.
> - Alan adları: `video_kodlar.hareket` · `video_kodlar.sahne`; **ikisi de listedir**.
>
> Bu kapanış üç işi yürürlüğe sokar: Task 8 doğrulayıcı düzeltmesi · Task 11'in hareket
> ayağıyla birlikte yazılması · Plan 2 brief hattının iki havuzu da üretmesi.

## Plan'ın bağladığı teknik kararlar (İlke 8: review zinciri doğrular; Eray'a FYI)

1. **K-07 damga temsili = iki kolon + BİLEŞİK FK + OPAK sunucu-kayıtlı üretim-anı taşıma:** `posts.package_id UUID NULL` + `posts.package_version INT NULL`; çift, `(package_id, package_version) REFERENCES social.sector_packages(id, version) MATCH FULL` bileşik FK'sıyla bağlanır (`sector_packages`e `UNIQUE (id, version)` eklenir). MATCH FULL yarım-NULL çifti ve satırla eşleşmeyen sürümü DB düzeyinde reddeder; paketsiz üretimde her ikisi NULL. **Atıf sözleşmesi (güven sınırı dahil):** damga, İÇERİĞİ ÜRETEN çağrının (caption / kısa-video stage-1) çözümlediği paketi taşır. Üretim iki aşamalı olduğundan taşıma İSTEMCİDEN GEÇER ama ham çift ASLA istemciye emanet edilmez — paket yolundaki üretici çağrı `social.generation_stamps` satırı yazar (`id uuid · brand_id · package_id · package_version · created_at · consumed_at timestamptz NULL`; tablo **migration 032'de** kurulur — Task 10 bu tabloya Task 12'den ÖNCE muhtaçtır, sıralama bu yüzden 032) ve yanıtta yalnız OPAK `generation_id` döner (paketsizde null). Kalıcı-kayıt isteği `generation_id`'yi geri getirir; sunucu damgayı **ATOMİK ve TEK-KULLANIMLIK tüketir** — post-yaratma transaction'ı içinde `consumed_at IS NULL` koşullu güncelleme; dönen satırın `brand_id`'si isteğin doğrulanmış markasıyla eşleşmeli — ve kayıtlı çifti AYNEN yazar (yeniden çözümleme YOK). Geçersiz/yabancı/başka-markaya-ait VEYA daha önce TÜKETİLMİŞ (replay) `generation_id` → damga yazılmaz (NULL) + `stamp_invalid` olayı; üretim bloklanmaz — sahte veya yeniden-kullanılmış damga hiçbir koşulda yazılmaz. Kayıt anında aktif paket değişmişse geçerli damga yine yazılır + `stamp_stale_at_persist` olayı. **Damganın iddia sözleşmesi (F17 — Eray kararı 2026-08-23, risk kabulü):** damga "post'un İLK içeriğini bu üretim oturumu üretti" atfıdır (**edited lineage**) — kullanıcı caption'ı kaydetmeden önce düzenleyebildiği için bayt-bayt içerik kanıtı İDDİA EDİLMEZ ve içerik-özeti bağlaması KURULMAZ (meşru düzenlemeyi reddederdi). Kalan boşluk: marka sahibinin kendi KULLANILMAMIŞ makbuzunu kendi başka içeriğine takabilmesi — yalnız o markanın kendi analitiğini yanıltır; solo işletim + 2 marka gerçeğinde KABUL EDİLEN RİSK. Yeniden açılma koşulu: müşteri sayısı / ürünleşme artışı.
2. **K-08 (a) `sector_research_artifacts.sector_slug` = serbest TEXT (FK değil):** ham kanıt katmanı, sektör satırının varlığından bağımsız yaşayabilmeli (araştırma satır açılmadan koşulabilir); katmanlar arası bağ zaten `run_id`.
3. **K-08 (b) kısıt katmanı = DB (trigger):** `brands.sub_sector_id` yalnız `parent_sector_id IS NOT NULL` satırı kabul eder — CHECK subquery yapamadığından BEFORE INSERT/UPDATE tetikleyicisi. Uygulama katmanı ek doğrulama yapar ama garanti DB'dedir (spec §3.2 hükmü: kısıt Faz 1'de kurulur).
4. **Önbellek hükmü (spec §10.4) = paket okuması Faz 1'de önbelleklenMEZ:** paketli yolda +1 DB sorgusu kabul edilir (doğrulanmadı etiketli maliyet; pilot ölçüm kalemi). Böylece aktivasyon-invalidasyon sınıfı hiç doğmaz; "anahtar sürümlü önbellek" ancak ölçüm gerektirirse ayrı iş.
5. **Katman-1 yakalama mekanizması = Anthropic istemci kesişimi:** fixture'lar, üretim kod yolunun `client.messages.create(...)`'e geçirdiği gerçek `system` + `messages` argümanlarından üretilir (monkeypatch; test-özel prompt kurulumu YASAK — spec §5.1). K-20=A: düzenek genel amaçlı kurulur, Marka DNA işi aynı harness'ı fixture seti ekleyerek kullanır — ikinci altyapı yok.
6. **Bildirim kanalları (K-45 mekanizması) = transactional outbox + versiyonlu n8n workflow:** (a) yönetici → `social.admin_events` OUTBOX tablosu (kalıcı kayıt = K-44 işareti; kolonlar: `id uuid` · `kind` · `payload jsonb` · `idempotency_key UNIQUE` · `delivery_state ('pending','sending','sent','failed')` · `lease_expires_at timestamptz NULL` · `attempt_count` · `created_at`); olay, tetikleyen iş transaction'ıyla BİRLİKTE commit edilir; Telegram iletimi commit SONRASI dispatch (sınırlı yeniden deneme: 3; sonrası `failed` — polling'le görünür kalır; idempotency key n8n tarafında dedupe girdisi). `sending` bir KİRA durumudur: `lease_expires_at` ile sınırlı; süresi dolmuş `sending` satırı yeniden claim edilebilir (crash-sonrası askıda-kalma yok). **Deneme muhasebesi (F19): CLAIM = kalıcı teslim denemesidir** — `attempt_count` claim transaction'ında atomik artar (finalize'da değil); crash/kira-dolumu deneme bütçesini TÜKETİR; `attempt_count >= 3` satır artık claim edilemez. **Süpürücü uygunluk kuralı (F20): aktif kira ASLA süpürülmez** — `pending` + tükenmiş bütçe hemen `failed`; `sending` + tükenmiş bütçe YALNIZ `lease_expires_at < now()` ise `failed` (üçüncü deneme canlıyken başarılı finalize `sent` kazanır). Fiziksel gönderim sayısı her koşulda sınırlı. Teslim hedefi en-az-bir-kez; "her olay" (K-56) = her olay outbox satırı. DB'nin KENDİSİ erişilemezken doğan `package_read_error` için bağımsız best-effort kanal `logger.error`'dur — belgeli sınır. (b) n8n iletimi VERSİYONLU artefakttır: `shared/n8n-workflows/sector-package-admin-events.json` (repo kuralı) + webhook payload sözleşmesi (event id · kind · payload · contract_version). (c) marka sahibi → `GET /brands/{brand_id}/package-status` + frontend panel bandı (K-45 sabit DEVRE-DIŞI metni; durum modeli Task 14). **K-45 geri-dönüş ("bakım tamamlandı") mesajının TESLİMİ Plan 2'dedir (F23 kapanışı — Eray yol seçimi 2026-08-24):** metin ve karar korunur; tetiği (reaktivasyon) yalnız Plan 2 komut ailesinden koşulabildiğinden doğal evi orası. Plan 2 teslim kalemi: geri-dönüş bandı + markanın bakım-dönemine maruziyet kanıtı (atama-geçmişi/`sub_sector_assigned_at` benzeri — Plan 2 migration'ı); Plan 1'in yaşam-döngüsü olay kaydı (Task 12) bu türetimin veri tabanını zaten üretir. Yüzey seçimi spec'te açıkça "plan işi".
7. **Aday küme teslimi (K-115/K-116 mekanizma ayağı — spec §7.2 "plan işidir"):** öneri çağrısına teslim = aday liste `analyze-website` prompt'una kapalı liste olarak gömülür + dönüş doğrulaması listede-veya-boş; açılır listeye teslim = `GET /sectors/sub-sector-candidates` endpoint'i (canlı sorgu, kopya tutulmaz).
8. **K-101/K-102 atomiklik = tek DB transaction'ı (spec §10.3'ün açık bıraktığı işlem kararlarının TEKNİK bağlaması):** aktivasyon ve rollback iki-adım geçişi tek transaction'da koşar — dayanak: R-17 taze ampirik kanıtı (Task 3 ölçümü) + sıra zorlayıcısının zaten DB olması (spec §10.1). Transaction sınırı İlke 8 kapsamında teknik-seviye seçimdir; K-101/K-102 farklı kapanırsa değişen yalnız `_apply_status_transition` sınırıdır (dar refactor — arayüz imzaları değişmez). **Yaşam-döngüsü OLAY KAYDI aynı transaction'ın İÇİNDEDİR (F24):** durum geçişi ile `log_package_event` yazımı birlikte commit/rollback olur — olaysız geçiş de geçişsiz olay da mümkün değildir. Spec'in "atomiklik sağlanmazsa pencere emniyetli + loglanır" hükmü fallback olarak korunur.

## Plan 2'ye teslim edilen arayüzler (KANONİK protokol — tek liste; görevler buna atıf yapar, imza TEKRARLAMAZ; Task 16 madde madde doğrular)

- Migration 032 şeması (iki tablo + kolonlar + garantiler) — Plan 2 koşusu yalnız `draft` yazar ve BUNU YALNIZ `insert_draft` üzerinden yapar (K-135 yazma-yüzeyi kuralının kod karşılığı; doğrudan SQL yazımı Plan 2'de yasak).
- `app/services/sector_packages.py::normalize_special_day_key(name: str) -> str` — K-01b tek modül (yazım + okuma aynı fonksiyon).
- `app/services/sector_packages.py::validate_package_content(content: dict, *, banned_brand_names: list[str], holiday_keys: set[str]) -> ValidationResult` — yazım kapısı.
- `app/services/sector_packages.py::insert_draft(db, *, sector_id, content, schema_version, run_id=None, actor) -> uuid` — doğrulayıcı-arkalı TEK draft yazıcısı.
- `app/services/sector_packages.py::activate_package(db, *, package_id, evidence: ActivationGateEvidence, actor)` / `rollback_package(db, *, sector_id, to_version, evidence: RollbackGateEvidence, actor)` / `deactivate_package(db, *, package_id, actor)` — durum geçişleri. Ham geçiş transaction'ı ÖZELDİR (`_apply_status_transition`); public API kendi kapı-kanıtı olmadan geçiş YAPMAZ — aktivasyon `ActivationGateEvidence`, rollback AYRI `RollbackGateEvidence` (yönetici onayı zorunlu) ister (Task 13 — K-71/K-28'in Plan-1 ayağı; K-103 yetkilendirme TEKNİĞİ ayrıca açık).
- `app/services/notifications.py::record_admin_event(db, *, kind, payload, idempotency_key) -> uuid` — transactional outbox (Task 14); K-26 vade bildirimi (Plan 2 tur takibi) aynı altyapıyı çağırır.
- Katman-1 harness (`tests/prompt_regression/`) — Plan 2 her turda yeniden koşturur.
- **[SONRADAN EKLENDİ — 2026-08-24; K-02 kapanışının Plan 2 ayağı]** Brief/sentez hattı
  `video_kodlar` için **İKİ HAVUZ** üretir: `hareket` ve `sahne`, ikisi de liste. Tek
  elemanlı havuz sözleşmeyi teknik olarak karşılar ama ürün amacını karşılamaz — o sektörün
  her videosu aynı tipte çıkar (spec §3.4 notu). Asgari eleman sayısı brief biçim
  sözleşmesinin işidir ve **ölçülmemiş bir sayı kapı yapılmaz** (İlke 9). Task 16 bu kalemi
  arayüz-sözleşme testinde doğrular.

> Bu bölüm imzaların TEK kanonik evidir. Bir görev metniyle bu liste çelişirse liste esastır; Task 16 arayüz-sözleşme testi her fonksiyonu belgelenen argümanlarla import edip çağırır.

---

### Task 1: Test altyapısı bootstrap (pytest + test DB)

**Files:**
- Create: `apps/social/backend/tests/__init__.py`, `apps/social/backend/tests/conftest.py`, `apps/social/backend/pytest.ini`
- Modify: `apps/social/backend/requirements.txt` (pytest, pytest-asyncio ekle)

**Interfaces:**
- Produces: pytest fixture'ları `db` (asyncpg bağlantısı, `otomaix_test` veritabanı, function-scope transaction rollback) ve `test_db_setup` (session-scope: `otomaix_test`'i yaratır, `shared/db/migrations/*.sql` dosyalarını numara sırasıyla psql ile uygular). Sonraki TÜM görevler bu fixture'ları tüketir.

**Bağlayıcı invariantlar:**
- Migration uygulayıcı dosya listesini GLOB ile alır (hardcoded liste değil — `run-migrations.sh:18`'deki bayat-liste hatası test altyapısında tekrarlanmaz).
- `DATABASE_URL` test içinde `otomaix_test`'e zorlanır; canlı `otomaix` adına bağlantı kuran test altyapısı reddedilir (conftest guard).

**Steps:**
- [ ] **Step 1:** Failing test yaz: `tests/test_infra.py::test_db_fixture_connects_and_sees_social_schema` — `db` fixture'ından `SELECT 1` + `social.sectors` tablosunun varlığı. Kanıtladığı: migration zinciri test DB'de uçtan uca koşuyor.
- [ ] **Step 2:** Koş: `cd apps/social/backend && python -m pytest tests/test_infra.py -v` — Beklenen: FAIL/ERROR (fixture yok).
- [ ] **Step 3:** conftest + pytest.ini + requirements güncellemesini yaz (asyncio_mode=auto; migration glob uygulayıcı).
- [ ] **Step 4:** Koş: aynı komut — Beklenen: PASS.
- [ ] **Step 5:** Commit: `test: bootstrap pytest infrastructure with migration-applied test db`

### Task 2: Migration 032 — tablolar, kolonlar, DB garantileri

**Files:**
- Create: `shared/db/migrations/032_sector_packages.sql`
- Test: `apps/social/backend/tests/test_migration_032.py`

**Interfaces:**
- Produces (şema sözleşmesi — Plan 2 dahil tüm tüketiciler için):
  - `social.sector_research_artifacts`: `id uuid PK` · `run_id text NOT NULL` · `sector_slug text NOT NULL` (K-08a: FK değil) · `kind text NOT NULL CHECK (kind IN ('research','review','synthesis'))` · `source text NOT NULL` (K-138) · `brief_ref text NULL` · `content_md text NOT NULL` · `created_at timestamptz DEFAULT now()` · indeks `(sector_slug, run_id)` · **salt-ekleme tetikleyicisi** (UPDATE/DELETE → RAISE EXCEPTION).
  - `social.sector_packages`: `id uuid PK` · `sector_id uuid NOT NULL REFERENCES social.sectors(id)` · `version int NOT NULL` · `status text NOT NULL CHECK (status IN ('draft','active','archived'))` · `schema_version int NOT NULL` · `content jsonb NOT NULL` · `decision_log jsonb NOT NULL DEFAULT '[]'` · `run_id text NULL` (K-110 açık) · `created_at` · `activated_at timestamptz NULL` · UNIQUE `(sector_id, version)` · **UNIQUE `(id, version)`** (bileşik damga FK'sının hedefi) · kısmi benzersiz indeks `(sector_id) WHERE status='active'` · salt-ekleme tetikleyicisi BİLİNÇLİ YOK (spec §3.3).
  - `brands.sub_sector_id uuid NULL REFERENCES social.sectors(id)` + **K-08b tetikleyicisi**: atanan satırın `parent_sector_id IS NOT NULL` olması zorunlu; `sector_packages.sector_id` için de aynı alt-sektör zorunluluğu (spec §3.3 "FK → alt-sektör satırı").
  - **Reparenting yasağı (K-08b'nin ayna ayağı):** `social.sectors.parent_sector_id` DEĞİŞİKLİĞİ Faz 1'de tetikleyiciyle tümden reddedilir (INSERT serbest, mevcut satırda parent güncellemesi yasak) — aksi hâlde geçerli yazımlardan sonra alt satır köke çevrilip invariant sessizce çökerdi.
  - `posts.package_id uuid NULL` + `posts.package_version int NULL` + **bileşik FK:** `FOREIGN KEY (package_id, package_version) REFERENCES social.sector_packages(id, version) MATCH FULL` — yarım-NULL çift ve satır-uyumsuz sürüm DB düzeyinde reddedilir (K-07 bağlaması).
  - `social.generation_stamps`: `id uuid PK` · `brand_id uuid NOT NULL REFERENCES social.brands(id) ON DELETE CASCADE` (F18: marka silme sözleşmesi korunur — mevcut `delete_brand` doğrudan siler, damga satırı markayla birlikte gider; ara-tablo verisi, süresiz-saklama rejimine TABİ DEĞİL) · `package_id uuid NOT NULL` · `package_version int NOT NULL` · `(package_id, package_version)` bileşik FK (MATCH FULL değil — ikisi NOT NULL) · `created_at` · `consumed_at timestamptz NULL` (tek-kullanım işareti — bağlanan teknik karar 1; tüketim davranışı Task 12).

**Bağlayıcı invariantlar:** deterministik kabul (spec §14.1): (1) artifacts UPDATE/DELETE istisna fırlatır; (2) INSERT başarılı + `run_id` ile sorgulanabilir; (3) sektör başına ikinci `active` indeks hatası; (4) `(sector_id, version)` ihlali hata; (5) `sub_sector_id`'ye kök satır yazımı reddedilir; (6) `sub_sector_id` NULL kalabilir, geri doldurma yok.

**Steps:**
- [ ] **Step 1:** Failing testler: `test_artifacts_append_only_update_raises` · `test_artifacts_append_only_delete_raises` · `test_artifacts_insert_and_query_by_run_id` · `test_packages_single_active_partial_index` · `test_packages_version_unique` · `test_sub_sector_id_rejects_root_sector` · `test_sub_sector_id_accepts_child_and_null` · `test_package_sector_id_rejects_root` · `test_stamp_both_null_accepted` · `test_stamp_exact_pair_accepted` · `test_stamp_half_null_rejected` · `test_stamp_mismatched_version_rejected` · `test_parent_sector_id_update_rejected` · `test_generation_stamps_schema_and_composite_fk` · `test_brand_delete_cascades_stamps_consumed_and_unconsumed` (F18: damgalı marka silinebilir kalır; workspace→brand cascade zinciri de doğrulanır). (Alt-sektör satırı test içinde INSERT edilir — canlı seed değil.)
- [ ] **Step 2:** Koş: `python -m pytest tests/test_migration_032.py -v` — Beklenen: FAIL (tablolar yok; conftest glob 032'yi henüz bulamaz → önce boş dosya değil, testin ERROR vermesi doğal).
- [ ] **Step 3:** `032_sector_packages.sql` yaz (idempotent: `IF NOT EXISTS` desenleri; tetikleyici fonksiyonlar `social` şemasında; migration 019 stiliyle uyumlu).
- [ ] **Step 4:** Koş: aynı komut — Beklenen: 15 PASS.
- [ ] **Step 5:** Commit: `feat(db): migration 032 — sector packages, research artifacts, sub_sector_id, package stamp`

### Task 3: Migration dağıtım gerçeği + geri alma + atomiklik ölçümü

**Files:**
- Modify: `shared/local-deployment/migrations/run-migrations.sh`
- Create: `shared/db/migrations/rollback/032_down.sql`
- Test: `apps/social/backend/tests/test_migration_032_rollback.py`

**Bağlayıcı invariantlar:**
- **Runner sözleşmesi:** dosya listesi KANONİK dizinden glob'lanır — `SCRIPT_DIR`'den türetilen repo-köküne göre `shared/db/migrations/[0-9]*.sql` (yerel kopya dizini `shared/local-deployment/migrations/*.sql` KAYNAK DEĞİLDİR — bugün 011'de kalmış bayat kopyalardır, kaldırılmaları ayrı temizlik); `docker compose` çağrısı açık `-f "$LOCAL_DEPLOY_DIR/docker-compose.yml"` ile; her psql çağrısı `-v ON_ERROR_STOP=1` ile — SQL hatası sıfır-dışı çıkış üretir, kısmi şema "başarılı" raporlanamaz.
- **Rollback sözleşmesi (F4 tahkimi — veri-varken-REDDET modeli):** `032_down.sql` önce PREFLIGHT koşar: `sector_packages` VEYA `sector_research_artifacts` satır içeriyorsa HİÇBİR değişiklik yapmadan hata ile DURur (süresiz-saklama K-140/141 verisi script'le imha edilmez; canlıda yol forward-fix migration'dır). Boş-veri yolunda sıra: (1) `posts` damga kolonları + bileşik FK kaldırılır → (2) `generation_stamps` + `sector_packages` + `sector_research_artifacts` tabloları düşürülür → (3) `brands.sub_sector_id` bağları boşaltılır + kolon kaldırılır → (4) YALNIZ bu iş açtığı alt-sektör satırları silinir (kök seed'e dokunulmaz) → (5) tetikleyici/indeks/fonksiyonlar kaldırılır. Spec §6.2'nin üçlü sırası bu dizinin (3)-(5) çekirdeğidir; paket-FK gerçeği spec sırasının ÖNÜNE (1)-(2)'yi zorunlu kılar — sıra genişletmesi spec'le çelişmez, onu çalışır kılar.
- R-17 ampirik ölçümü (spec §10.3): tek transaction'da `archived←active` + `active←draft` iki-adım geçişi kısmi indeks altında BAŞARILI; ters sıra indeks ihlaliyle REDDEDİLİR.
- Prod dağıtım manuel adımı görünür: 032 canlıya elle psql (`-v ON_ERROR_STOP=1`) ile uygulanır (backend image migration koşmaz — ölçüldü); Task 16 "manuel adımlar" listesine girer.

**Steps:**
- [ ] **Step 1:** Failing testler: `test_two_step_activation_in_single_transaction_succeeds` · `test_wrong_order_activation_rejected_by_partial_index` · `test_rollback_refuses_when_package_data_exists` (alt sektör + marka bağı + paket + damgalı post kur; down → hata + HİÇBİR nesne düşmemiş) · `test_rollback_clean_path_full_teardown` (veri boşken down → 032 nesneleri tamamen kalkar, kök seed durur) · `test_runner_glob_covers_canonical_dir_in_order` · `test_runner_stops_on_sql_error` (geçersiz SQL enjekte → sıfır-dışı çıkış + kısmi 032 nesnesi yok).
- [ ] **Step 2:** Koş: `python -m pytest tests/test_migration_032_rollback.py -v` — Beklenen: FAIL.
- [ ] **Step 3:** `032_down.sql` + `run-migrations.sh` değişikliklerini yaz.
- [ ] **Step 4:** Koş: testler PASS + runner'ı hem repo kökünden hem `shared/local-deployment/` içinden taze DB'ye karşı çalıştır — 001→032 sırası doğrulanır.
- [ ] **Step 5:** Commit: `feat(db): canonical-glob migration runner + guarded 032 rollback + activation atomicity proof`

### Task 4: Kök kova korumaları (R-01 / R-02) + trend bağışıklık doğrulaması

**Files:**
- Modify: `apps/social/backend/app/services/sector_resolver.py` (sorguya `WHERE parent_sector_id IS NULL`; `_CACHE_KEY` → `..._v3`)
- Modify: `apps/social/backend/app/routers/sectors.py` (sorguya kök filtresi; `_CACHE_KEY` → `...:list:v2`)
- Test: `apps/social/backend/tests/test_taxonomy_guards.py`

**Seam pinleri:** `sector_resolver.py::resolve_sector` (slug haritası sorgusu + kısmi-eşleşme dalı — kısmi eşleşme de yalnız kök haritada gezdiği için filtre tek noktadan yeter) · `sectors.py::list_sectors` · `trends/layer_a.py::run_nightly_sweep` (zaten `parent_sector_id IS NULL` — İŞ YOK, yalnız test).

**Bağlayıcı invariantlar:** alt-sektör satırı varken (a) çözücü hiçbir markayı alt-sektöre çözmez (R-01); (b) `GET /sectors` alt satırı listelemez (R-02 — 3 frontend tüketicisi: `onboarding/page.tsx`, `markalar/page.tsx`, `marka-ayarlari/page.tsx` aynı listeyi görmeye devam eder); (c) trend sweep sorgusu alt satırı görmez. Cache key sürümleri eski (filtresiz) önbelleklenmiş değeri devre dışı bırakır.

**Steps:**
- [ ] **Step 1:** Failing testler: `test_resolver_ignores_sub_sector_rows` (alt satır ekle; slug'ı ve kısmi-eşleşme varyantını çözücüye ver → kök/`genel` döner, ASLA alt satır) · `test_sectors_endpoint_excludes_sub_sectors` · `test_trend_sweep_query_root_only`.
- [ ] **Step 2:** Koş: `python -m pytest tests/test_taxonomy_guards.py -v` — Beklenen: FAIL (bugün filtre yok — çözücü tüm satırları alıyor, taze doğrulandı).
- [ ] **Step 3:** İki filtreyi + cache key sürümlerini uygula.
- [ ] **Step 4:** Koş: PASS.
- [ ] **Step 5:** Commit: `feat(sectors): root-level guards for resolver and sectors list (R-01/R-02)`

### Task 5: Veri/API regresyon kümesi + marka kök-sektör tam sweep

**Files:**
- Create: `apps/social/backend/tests/test_data_api_regression.py`
- Create: `apps/social/backend/scripts/sector_sweep.py` (re-runnable operasyonel sweep — canlıda da koşulabilir, read-only)

**Bağlayıcı invariantlar (spec §5.3 — ölçüt alan-bazlı eşitlik, byte değil):**
- `GET /sectors` kök listesi, alt-sektör satırı ekleme öncesi/sonrası alan-bazlı AYNI döner.
- Mevcut markaların `(brand_id, sector_id)` eşlemeleri alt satır eklemeden önce/sonra birebir aynı (TAM sweep — spot yasak; test DB'de tüm markalar, canlıda script tüm markaları tarar).
- Paketsiz üretim kaydında `package_id IS NULL AND package_version IS NULL`.
- `sector_sweep.py` çıktısı deterministik rapor (marka sayısı + fark listesi; fark=0 beklenir) — Plan 2 satır-açma adımı öncesi/sonrası da aynı script koşulur.

**Steps:**
- [ ] **Step 1:** Failing testler: `test_sectors_list_unchanged_after_sub_sector_insert` · `test_brand_sector_mappings_full_sweep_unchanged` · `test_unpackaged_post_has_no_package_stamp` · `test_sector_sweep_readonly_and_deterministic` (script test DB'ye açık `DATABASE_URL` ile koşar — ortamdan miras almaz; aynı durumda iki koşum aynı rapor; yazma girişimi yok — read-only rol ile kanıtlanır).
- [ ] **Step 2:** Koş → FAIL (script/test yok).
- [ ] **Step 3:** Testleri geçir + `sector_sweep.py` yaz (asyncpg, `DATABASE_URL` parametreli, yalnız SELECT).
- [ ] **Step 4:** Koş: PASS + `python scripts/sector_sweep.py --dry-run` test DB'ye karşı fark=0 raporu.
- [ ] **Step 5:** Commit: `test: data/api regression set + full brand sector sweep script`

### Task 6: Katman-1 yakalama altyapısı + caption/fikir yüzey fixture'ları

**Files:**
- Create: `apps/social/backend/tests/prompt_regression/__init__.py`, `apps/social/backend/tests/prompt_regression/capture.py`, `apps/social/backend/tests/prompt_regression/conftest.py`, `apps/social/backend/tests/prompt_regression/test_caption_surfaces.py`
- Create: `apps/social/backend/tests/prompt_regression/fixtures/` (dondurulmuş `.txt` dosyaları — üretilen adlar varyasyon matrisinden türetilir, ör. `caption__single__no_special_day.txt`)

**Interfaces:**
- Produces: `capture.py::capture_anthropic_calls(monkeypatch) -> list[CapturedCall]` — `anthropic.Anthropic` örneğinin `messages.create` çağrısını keser; `CapturedCall.rendered: str` = `system` blokları + `messages` içerik blokları deterministik ayraçlarla birleştirilmiş TAM metin. Fixture karşılaştırması `rendered.encode() == fixture_bytes` (byte-exact). Deterministik sabit yanıt döndürür (geçerli JSON) — üretim yolu kırılmadan akar.
- Produces: `conftest.py::frozen_brand_fixtures` — sabit marka/brand_kit/template/product/platform girdileri (fixture determinizmi bu sabit girdilere dayanır; girdi seti dosyada versiyonlanır).

**Seam pinleri (üretimin kendi kod yolu — test-özel prompt kurulumu YASAK):** `caption_generator.py::generate_captions` (Tier 1 `prompt_builder.build_system_prompt` + Tier 2 `build_brand_context` + Tier 3 `build_dynamic_content` + `_build_output_format_instruction` — görsel director çıktı talimatı ve carousel dalı BURADA) · `ai.py::suggest_ideas` (Tier 2 sektör rehberi bloğu).

**Varyasyon matrisi (bu task'ın kapsamı):** caption tekli × (özel günlü / günsüz) · caption carousel dalı (K-15b: `is_carousel` çıktı-biçim varyasyonu) · fikir önerme. Sektörlü marka girdisi `SECTOR_GUIDANCE` İÇEREN slug ile kurulur (yerine-geçme ancak bugün basılan blokla kanıtlanır).

**Bağlayıcı invariantlar:** fixture üretimi ve doğrulaması AYNI capture yolundan geçer (tek fark: `--update-fixtures` benzeri açık bayrakla dondurma); dondurma commit'inden sonra fixture dosyası değişikliği = kırmızı alarm; harness Marka DNA işinin de tüketeceği genel arayüzdür (K-20).

**Steps:**
- [ ] **Step 1:** Failing test: `test_caption_single_no_special_day_matches_fixture` (fixture henüz yok → FAIL) + capture altyapısı testi `test_capture_intercepts_and_renders_deterministically` (aynı girdiyle iki koşum → aynı bayt).
- [ ] **Step 2:** Koş: `python -m pytest tests/prompt_regression/test_caption_surfaces.py -v` — Beklenen: FAIL.
- [ ] **Step 3:** `capture.py` + conftest'i yaz; fixture'ları dondur (`PROMPT_REGRESSION_UPDATE=1 python -m pytest tests/prompt_regression/ -v`); dondurulan dosyaları gözle incele (paket izi YOK, bugünkü davranış).
- [ ] **Step 4:** Koş (bayraksız): tüm caption/fikir varyantları PASS (byte-exact).
- [ ] **Step 5:** Commit: `test(katman1): prompt capture harness + frozen caption/idea fixtures`

### Task 7: Katman-1 kısa video + legacy yüzeyleri — fixture seti tamamlanır (FREEZE kapısı)

**Files:**
- Create: `apps/social/backend/tests/prompt_regression/test_short_video_surfaces.py`, `.../test_motion_pool.py`, `.../test_legacy_short_video.py` (+ fixtures)

**Seam pinleri:** `short_video.py::_build_still_prompt` (iki mod: `image_edit_mode` True/False — meta-prompt'un Claude'a giden TAM metni capture ile) · `short_video.py::generate_script` (sector_guidance parametreli script istemi) · `short_video.py::_MOTION_PROMPTS` + `_pick_motion_prompt` (havuz içeriği byte-pin + seçimin havuzdan geldiği davranış testi) · `posts.py::generate_short_video` (legacy uç: `sector_slug = brand["sector"]` display-name ile `SECTOR_GUIDANCE.get` → bugün BOŞ — bozuk-boş davranış AYNEN dondurulur, K-06 kapısı).

**Varyasyon matrisi:** kısa video durağan kare × (metinden-görsele / ürün referanslı) × (ürünlü / ürünsüz) · script (sektör rehberli marka girdisiyle) · legacy uç script istemi.

**Bağlayıcı invariantlar:** bu task'ın kapanışı = **tam sweep FREEZE**: `python -m pytest tests/prompt_regression/ -v` tüm yüzeylerde yeşil olmadan sonraki HİÇBİR göreve geçilmez (spec §5.1 sıra hükmü). Bu noktadan sonra her task'ın son adımı bu komutu yeniden koşar.

**Steps:**
- [ ] **Step 1:** Failing testler: `test_still_prompt_text_to_image_mode_matches_fixture` · `test_still_prompt_product_edit_mode_matches_fixture` · `test_script_request_matches_fixture` · `test_motion_pool_bytes_pinned` · `test_motion_pick_draws_from_pool` · `test_legacy_short_video_guidance_is_empty_today`.
- [ ] **Step 2:** Koş → FAIL.
- [ ] **Step 3:** Fixture'ları dondur; gözle incele.
- [ ] **Step 4:** TAM sweep koş: `python -m pytest tests/prompt_regression/ -v` — Beklenen: TÜMÜ PASS.
- [ ] **Step 5:** Commit: `test(katman1): short-video + legacy fixtures — full surface set frozen`

### Task 8: Paket erişim katmanı — normalize modülü + doğrulayıcı + çözümleyici

**Files:**
- Create: `apps/social/backend/app/services/sector_packages.py`
- Test: `apps/social/backend/tests/test_sector_packages_service.py`

**Interfaces (Produces — ilk ikisi kanonik teslim listesinde; `resolve_package_context` runtime-içi):**
- `normalize_special_day_key(name: str) -> str` — K-01b TEK modül; `social.public_holidays.name_tr` üzerinden normalize (Türkçe karakter + boşluk indirgeme, `sector_resolver._normalize_slug` ile AYNI kural setine pin'lenmiş ayrı fonksiyon — davranışı test eşitler). Yazım tarafı (doğrulayıcı) ve okuma tarafı (çözümleyici) bu fonksiyonu import eder; ikinci kopya yazılamaz.
- `validate_package_content(content: dict, *, banned_brand_names: list[str], holiday_keys: set[str]) -> ValidationResult` — spec §3.4 kapalı küme: sekiz alan + `ozel_gun`; `ozel_gun` anahtarları `holiday_keys`'e karşı (K-01b yazım ayağı); `içerik-önerilmez` özel temsili geçerli boş sayılır (K-120); marka adı içeren metin reddedilir (K-15 üçüncü bileşen); `video_kodlar` v1'de opak iki-alt-yapı kontrolü (K-02 kapısı); toplam ~6.000 karakter tavanı UYARI üretir, RED üretmez (tavan tasarım hedefi — kapı değil, İlke 9).
- `resolve_package_context(db, brand: dict) -> SectorPackageContext | None` — üç adım (spec §4.2): `sub_sector_id` boş → None; dolu → `status='active'` tek satır sorgusu; yok/bozuk → None + **log**: bayat/eksik atama olayı (`logger.warning` + Task 12'deki olay kaydına bağlanır). `draft`/`archived` HİÇ okunmaz. Önbelleksiz (bağlanan teknik karar 4). İstisna yutulur → None (üretim bloklanmaz — güvenli geri düşüş).

**Bağlayıcı invariantlar:** çözümleyici hatası hiçbir üretim akışını kırmaz; K-15(a) alan-düzeyi atlama dalı YOK (karar kapısı); `SectorPackageContext` alanları: `package_id`, `version`, `content`, `sub_sector_slug`.

**Steps:**
- [ ] **Step 1:** Failing testler: `test_normalize_key_matches_writer_and_reader` · `test_validator_rejects_unknown_field` · `test_validator_rejects_unknown_special_day_key` · `test_validator_accepts_icerik_onerilmez` · `test_validator_rejects_brand_name_text` · `test_validator_size_warning_not_rejection` · `test_resolver_returns_none_without_assignment` · `test_resolver_returns_context_for_active` · `test_resolver_none_for_archived_with_stale_log` · `test_resolver_swallows_db_error_returns_none`.
- [ ] **Step 2:** Koş → FAIL.
- [ ] **Step 3:** Modülü yaz.
- [ ] **Step 4:** Koş: PASS + tam sweep (`tests/prompt_regression/`) yeşil — bu task üretim prompt yoluna DOKUNMAZ, sweep bunu kanıtlar.
- [ ] **Step 5:** Commit: `feat(packages): access layer — normalize module, content validator, package resolver`

> **[SONRADAN EKLENDİ — 2026-08-24; spec eksik yazıldığı için]** Task 8 uygulanırken
> doğrulayıcı `video_kodlar`'ın iki alt yapısının her birini **tek bir dolu metin** olarak
> denetledi (K-02 açık sayıldığı için "opak doğrulama" böyle yorumlandı). Input ise alanı
> **iki alt LİSTE / havuz** olarak yazar (satır 817 · 1717 · 485 — ayrıntı spec §3.4'e eklenen
> notta). **Ölçüm (2026-08-24, taze):** `{"hareket": ["a","b","c"], "sahne": ["d","e"]}` bugünkü
> kapıdan GEÇMİYOR — `video_kodlar['hareket'] metin değil: list`. Yani alternatif taşıyan meşru
> bir paket bugün yazılamaz. K-02 kapandığında bu kapı liste şeklini kabul edecek biçimde
> düzeltilmelidir; düzeltme Task 8'in kapsamına geri döner.
>
> **[GÜNCELLEME — 2026-08-24: K-02 kapandı]** Düzeltme artık yürürlüktedir. Kapı
> `video_kodlar`'ı TAM İKİ anahtarla (`hareket` · `sahne`) ve her ikisini **boş olmayan
> metin listesi** olarak doğrular; öğeler dolu metin olmalıdır. Adlar bağlandığı için
> "opak iki alt yapı" doğrulaması yerini adlı sözleşmeye bırakır.

### Task 9: Kanal envanteri — `brand_kit.channels` + deterministik filtre

**Files:**
- Modify: `apps/social/backend/app/services/sector_packages.py` (filtre fonksiyonu), `apps/social/backend/app/routers/brands.py` (channels doğrulaması — mevcut `update_brand_kit` deep-merge yolu kullanılır, yeni kolon YOK), `apps/social/backend/app/models/schemas.py` (`BrandKitUpdate`'e tipli `channels` alanı — Pydantic bilinmeyen alanı DÜŞÜRÜR, şemasız alan router'a hiç ulaşmaz)
- Test: `apps/social/backend/tests/test_channel_inventory.py`

**Interfaces:**
- Produces: `filter_channel_dependent(items: list[dict], channels: dict | None) -> list[dict]` — `[kanal-bağımlı: X]` etiketli kalıp yalnız `channels[X] is True` ise geçer; `channels` yok/boş → etiketli kalıp ATLANIR (muhafazakâr — spec §12.2); etiketsiz kalıp her zaman geçer.
- Anahtar uzayı KAPALI sabit: `whatsapp_hatti · fiziksel_magaza · randevu_sistemi · eticaret_sitesi` — modül sabiti `CHANNEL_KEYS`; `update_brand_kit` bu uzay dışındaki channels anahtarını reddeder.

**Bağlayıcı invariantlar:** filtre deterministiktir (LLM'siz); Task 10'daki CTA basımı bu filtreden geçer; K-04 talimatının son cümlesi ikinci savunma hattı olarak kalır.

**Steps:**
- [ ] **Step 1:** Failing testler: `test_filter_drops_tagged_without_channel` · `test_filter_passes_tagged_with_channel_true` · `test_filter_conservative_when_channels_missing` · `test_untagged_always_passes` · `test_brand_kit_rejects_unknown_channel_key` · `test_brand_kit_channels_roundtrip_via_api` (API'den yaz + geri oku — şema alanının varlığını uçtan uca kanıtlar; Pydantic sessiz-düşürme sınıfına pozitif kontrol).
- [ ] **Step 2:** Koş → FAIL.
- [ ] **Step 3:** Uygula.
- [ ] **Step 4:** Koş: PASS + TAM sweep YEŞİL (üretim prompt yoluna dokunulmadı).
- [ ] **Step 5:** Commit: `feat(channels): closed-key brand channel inventory + deterministic CTA filter`

### Task 10: Tek-kapı enjeksiyon — caption + fikir önerme (Tier 2 yerine-geçme + Tier 3 özel gün)

**Files:**
- Modify: `apps/social/backend/app/core/prompt_builder.py` (`build_brand_context` paket dalı; `build_dynamic_content` `ozel_gun` paket dalı)
- Modify: `apps/social/backend/app/core/caption_generator.py`, `apps/social/backend/app/routers/posts.py`, `apps/social/backend/app/routers/ai.py` (çözümleyici çağrısı + context geçişi)
- Modify: `apps/social/backend/app/models/schemas.py` (caption/stage-1 YANIT şemalarına OPAK `generation_id` alanı — K-07 taşıma sözleşmesinin üretici ucu; ham paket çifti istemciye dönmez)
- Test: `apps/social/backend/tests/prompt_regression/test_packaged_caption.py`

**Bağlayıcı invariantlar:**
- **Tek kapı:** paket dalına giriş YALNIZ `resolve_package_context` sonucuna bakar; yüzeylerde ikinci bir koşul yazılamaz.
- **Yerine-geçme:** context doluysa `SECTOR_GUIDANCE` bloğu basılmaz, yerine paket bloğu + başında K-04 sabit kullanım talimatı (spec §4.5 metni birebir; "2-3" değeri talimat metninin parçası, eşik değil). Aynı kural `ai.py::suggest_ideas` Tier 2 bloğuna (yan-yana yasağının fikir ucu ayağı).
- **Tier 3 özel gün:** kullanıcı özel gün seçtiyse VE pakette `normalize_special_day_key` eşleşmesi varsa dönem kalıpları bloğa eklenir (mevcut blok YAPISI değişmez); eşleşmezse SESSİZ DÜŞME + zorunlu log (spec §11.1). `anma`/`kutlama` kısıt satırları (spec §11.3; K-119: yasak kullanıcı isteğini geçersiz kılar — talimat metnine yazılır).
- **Kanal filtresi çağrısı:** `[kanal-bağımlı: X]` etiketli CTA kalıpları Task 9'daki `filter_channel_dependent`'ten geçirilerek basılır.
- **Damga taşıma (üretici ucu — bağlanan teknik karar 1):** paketli caption üretimi `social.generation_stamps` satırı yazar ve yanıtta yalnız OPAK `generation_id` döner (paketsizde null); istemci bu kimliği kalıcı-kayıt isteğine aynen geri verir (tüketici ucu + sahiplik doğrulaması Task 12).
- **Katman-1:** paketsiz fixture'lar byte-exact YEŞİL kalır (tek kapının `None` dalı hiçbir yüzeyde iz bırakmaz).
- **Paketli yapısal kontroller (spec §5.4):** paket bloğu VAR · kök rehber YOK · özel gün bloğu yalnız eşleşince · `anma` satış-dili yasağı kullanıcı isteğini geçersiz kılar (K-119).

**Steps:**
- [ ] **Step 1:** Failing testler: `test_packaged_caption_replaces_sector_guidance` (paket bloğu var + `SEKTÖR REHBERİ` başlığı yok) · `test_packaged_idea_prompt_replaces_guidance` · `test_usage_instruction_prefixes_package_block` · `test_special_day_match_injects_period_block` · `test_special_day_mismatch_silent_fallthrough_with_log` · `test_packaged_caption_cta_respects_channel_filter` · `test_anma_sales_ban_overrides_user_request` (K-119: satış isteyen user_prompt'la bile `anma` kısıt satırı basılır ve satış-dili yasağı talimatta üstündür) · `test_packaged_caption_response_carries_generation_id` · `test_unpackaged_caption_response_generation_id_null` · `test_unpackaged_fixtures_still_byte_exact` (tam sweep alt kümesi).
- [ ] **Step 2:** Koş → FAIL.
- [ ] **Step 3:** Enjeksiyonu uygula (paket bloğu düzeni: `content` alanlarından deterministik metin üretimi — alan sırası sabit; blok üretici fonksiyon `sector_packages.py::render_package_block(context, *, surface: str) -> str`).
- [ ] **Step 4:** Koş: yeni testler PASS + TAM sweep `tests/prompt_regression/` YEŞİL.
- [ ] **Step 5:** Commit: `feat(injection): package block replaces sector guidance on caption + idea surfaces`

### Task 11: Tek-kapı enjeksiyon — görsel director + kısa video durağan kare (iki mod)

**Files:**
- Modify: `apps/social/backend/app/core/caption_generator.py` (`_build_output_format_instruction` sektör görsel dili + özel gün görsel vurgusu)
- Modify: `apps/social/backend/app/services/short_video.py` (`_build_still_prompt` iki modda paket sahne dili), `apps/social/backend/app/routers/posts.py` (context geçişi)
- Test: `apps/social/backend/tests/prompt_regression/test_packaged_visual_video.py`

**Bağlayıcı invariantlar:**
- Görsel director talimatına `gorsel_kodlar` (EN) eklenir; eşleşen özel günde `gorsel_vurgu` koşullu eklenir (spec §4.3); dağarcık EK BAĞLAMDIR, geçersiz-kılıcı değil (tek istisna `anma` satış-dili — Task 10'da bağlandı).
- Kısa video durağan kare: `video_kodlar`ın SAHNE alt yapısı İKİ modda da (metinden-görsele + ürün referanslı) eklenir — tek moda uygulama yarım ayrışma (spec §4.3).
- **Hareket ayağı DOKUNULMAZ:** `_MOTION_PROMPTS` havuzu ve `_pick_motion_prompt` paketli yolda da aynen (K-02 karar kapısı); motion fixture'ları değişmeden yeşil.
- Legacy uç (`posts.py::generate_short_video`) paket yoluna BAĞLANMAZ (K-06 açık; bugünkü davranış korunur — fixture kanıtlar).
- Paketsiz tam sweep YEŞİL.

**Steps:**
- [ ] **Step 1:** Failing testler: `test_visual_director_includes_gorsel_kodlar` · `test_visual_special_day_vurgu_only_on_match` · `test_still_prompt_scene_language_in_both_modes` · `test_motion_pool_untouched_on_packaged_path` · `test_legacy_endpoint_not_wired_to_package`.
- [ ] **Step 2:** Koş → FAIL.
- [ ] **Step 3:** Uygula (`render_package_block(surface='visual'|'video_scene')` dalları).
- [ ] **Step 4:** Koş: PASS + TAM sweep YEŞİL.
- [ ] **Step 5:** Commit: `feat(injection): sector visual/scene language on image director + short-video stills`

> **[SONRADAN EKLENDİ — 2026-08-24; spec eksik yazıldığı için]** Task 11'in
> *"Hareket ayağı DOKUNULMAZ"* invariantı K-02'nin "bekletilir" hükmünden türetilmişti.
> Yukarıdaki K-02 notuna göre o hüküm eksik bir zemine dayanıyor. Ek olarak iki şey bu
> görevi doğrudan etkiler:
>
> - **Sahne ayağının kaynağı belirsiz kalmıştı.** Task 11 *"`video_kodlar`'ın SAHNE alt
>   yapısı"* der ama iki alt yapının hangisinin sahne olduğu K-02'ye bağlı olduğu için
>   yürütme sırasında seçilemez — yürütme 2026-08-24'te tam bu noktada durdu. Input sahne
>   yüzeyini kesin yazar (satır 2768): durağan kare istemi paketin **sahne kodlarını** alır,
>   **iki modda da**; hareket ayrı yüzeydir.
> - **Hareket havuzunun mekanizması input'ta tarif edilmiştir** (satır 485): *"paket yolunda
>   sektör havuzundan, mevcut yolda bugünkü sabit listeden"* — değişen kaynaktır, seçici
>   değil. Paketsiz yolda `_MOTION_PROMPTS` byte-exact korunur (input satır 3103).
>
> K-02 kapandığında Task 11 hareket ayağını da kapsayacak biçimde yeniden yazılır; bu not
> yalnız eksiği kaydeder, görevin mevcut metnini değiştirmez.
>
> **[GÜNCELLEME — 2026-08-24: K-02 kapandı]** Task 11'in kapsamı şu üç bağlayıcı invariantla
> GENİŞLER (görevin mevcut maddeleri geçerliliğini korur, yalnız *"Hareket ayağı
> DOKUNULMAZ"* satırı yürürlükten kalkar):
>
> 1. **Sahne:** `video_kodlar.sahne` havuzu durağan kare istemine İKİ modda da girer
>    (metinden-görsele + ürün referanslı). Kullanım talimatı (K-04) bloğun başındadır, yani
>    model havuzdan seçer, uydurmaz.
> 2. **Hareket:** paketli yolda seçim `video_kodlar.hareket` havuzundan yapılır ve seçimi
>    caption aşamasındaki mevcut model çağrısı verir. Sunucu, istemciden dönen değeri
>    **havuz üyeliğine karşı doğrular**; üye değilse/eksikse aynı havuzdan belirleyici
>    seçime düşer. Havuz boşsa `_MOTION_PROMPTS`'a düşülür (K-113 = A).
> 3. **Paketsiz yol dokunulmaz:** `_MOTION_PROMPTS` havuzu ve bugünkü seçim yolu paketsiz
>    markada byte-exact korunur; `short_video__motion_pool` fixture'ı bunu pinler.

### Task 12: K-07 damga yazımı + gözlemlenebilirlik log çekirdeği

**Files:**
- Modify: `apps/social/backend/app/routers/posts.py` (kalıcı-kayıt uçları `generation_id` doğrulayıp kayıtlı damgayı yazar), `apps/social/backend/app/models/schemas.py` (kalıcı-kayıt İSTEK şemalarına `generation_id` — K-07 taşıma sözleşmesinin tüketici ucu)
- Modify: `apps/social/frontend/components/templates/CaptionEditor.tsx` (`CaptionData`'ya `generation_id`) ve `apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx` (caption yanıtındaki `generation_id`'yi sonraki generate/stage-1 isteklerine aynen geçirir)
- Create: `apps/social/backend/app/services/package_events.py` (`log_package_event(db, *, event_type, sector_id=None, brand_id=None, package_id=None, from_version=None, to_version=None, actor=None, detail=None)` → `social.package_events` tablosu; `033_package_events.sql`) — `generation_stamps` tablosu 032'de ZATEN kuruldu (Task 2; sıralama gereği).
  **Olay kapsam sözleşmesi (F21):** iki kapsam sınıfı, fonksiyon içinde doğrulanır — (a) MARKA-kapsamlı olaylar (`mismatch_fallthrough` · `stale_assignment_fallback` · `stamp_missing` · `stamp_invalid` · `stamp_stale_at_persist` · `package_read_error`): `brand_id` ZORUNLU; (b) PAKET-kapsamlı yaşam-döngüsü olayları (`activation` · `rollback` · `deactivation`): `brand_id` OPSİYONEL (ilk aktivasyon marka atamasından önce meşru; geçiş sıfır/çok markayı etkileyebilir — fan-out YAPILMAZ, tek paket-kapsamlı satır yazılır), `sector_id` + `package_id` + `actor` ZORUNLU; **sürüm alanları OLAY-TÜRÜNE ÖZGÜ (F22 — sınır geçişleri sentinelsiz/uydurma-değersiz temsil edilir, fonksiyon doğrular):** `activation` → `to_version` zorunlu, `from_version` yalnız İLK aktivasyonda NULL (yerine-geçme aktivasyonunda zorunlu); `rollback` → `from_version` (arşivlenen kaynak) + `to_version` (geri getirilen hedef) zorunlu, `package_id` = geri getirilen HEDEF sürümün satırı (kimlik belirsizliği yok); `deactivation` → `from_version` zorunlu, `to_version` NULL. Çelişkili kombinasyon reddedilir.
- Test: `apps/social/backend/tests/test_package_stamp_and_events.py`

**Bağlayıcı invariantlar (spec §14.4 zorunlu ortak çekirdek — runtime kalemleri):**
- **Damga = SUNUCU-KAYITLI, TEK-KULLANIMLIK taşınan değer (bağlanan teknik karar 1):** kalıcı-kayıt ucu istekteki `generation_id`'yi post-yaratma transaction'ı İÇİNDE atomik tüketir (`consumed_at IS NULL` + doğrulanmış marka koşullu güncelleme; kazanan tek istek olur) ve dönen kayıtlı çifti AYNEN yazar — kayıt anında yeniden çözümleme YOK. Geçersiz/yabancı/başka-marka VEYA tüketilmiş (aynı-marka replay dahil) `generation_id` → damga NULL + `stamp_invalid` olayı (sahte/yeniden-kullanılmış damga asla yazılmaz; üretim bloklanmaz). İstek `generation_id`'siz + marka paket-yolundaysa `stamp_missing` olayı + NULL. Taşınan damganın paketi kayıt anında artık aktif değilse damga yine yazılır + `stamp_stale_at_persist` (provenans dürüst).
- Olay türleri kapalı başlangıç kümesi: `mismatch_fallthrough` · `package_read_error` · `stale_assignment_fallback` · `stamp_missing` · `stamp_invalid` · `stamp_stale_at_persist` · `activation` · `rollback` · `deactivation` (kim·ne zaman·hangi sürümler). Hassas veri loglanmaz; paket içeriği log'a tam basılmaz. Task 8-11'deki `logger.*` çağrıları bu kalıcı olay kaydına bağlanır.
- Paketli post kaydı damga taşır; geçmiş postlara geriye dönük yazım YOK (K-39).

**Steps:**
- [ ] **Step 1:** Failing testler: `test_persist_writes_recorded_stamp_verbatim` · `test_deactivation_between_stages_keeps_producing_stamp_and_logs_stale` (aşamalar arası deaktivasyon: geçerli generation_id → özgün çift + stale olayı) · `test_forged_generation_id_writes_null_and_alerts` · `test_cross_brand_generation_id_rejected` · `test_same_brand_replay_of_consumed_id_rejected` · `test_concurrent_persists_with_same_id_single_winner` (atomik tüketim: iki eşzamanlı kayıt → tek damga, diğeri NULL+olay) · `test_old_version_stamp_replay_to_new_post_rejected` · `test_unpackaged_post_stamp_null` · `test_missing_generation_id_on_packaged_brand_logs_event` · `test_stale_assignment_event_recorded` · `test_mismatch_event_recorded` · `test_brand_scoped_event_requires_brand_id` · `test_lifecycle_event_valid_without_brand` (F21: atanmış marka yokken ilk aktivasyon olayı yazılabilir) · `test_lifecycle_event_requires_sector_package_actor` · `test_activation_event_first_allows_null_from_version` · `test_activation_event_replacement_requires_from_version` · `test_rollback_event_requires_source_and_target_versions` · `test_deactivation_event_requires_from_null_to` · `test_lifecycle_event_rejects_contradictory_shape` (F22 şekil doğrulaması) · `test_event_detail_excludes_package_content`.
- [ ] **Step 2:** Koş → FAIL.
- [ ] **Step 3:** `033_package_events.sql` + servis + yazım noktaları + frontend damga geçişini uygula.
- [ ] **Step 4:** Koş: PASS + TAM sweep YEŞİL + `cd apps/social/frontend && npx next build` hatasız.
- [ ] **Step 5:** Commit: `feat(observability): package stamp on posts + persistent package event log`

### Task 13: Yaşam döngüsü servis fonksiyonları (aktivasyon / rollback / deaktivasyon)

**Files:**
- Modify: `apps/social/backend/app/services/sector_packages.py`
- Test: `apps/social/backend/tests/test_package_lifecycle.py`

**Interfaces (Produces — imzalar kanonik "Plan 2'ye teslim edilen arayüzler" listesinde; bu planda HTTP ucu AÇILMAZ):**
- `ActivationGateEvidence` (dataclass) — alanlar: `activation_eligible: bool` · `open_questions_count: int` (K-71: 0 olmalı) · `katman1_passed: bool` · `checklist_approved: bool` · `expected_active_version: int | None` (OPSİYONEL base-sürüm kanıtı: dolu gelirse geçiş anındaki gerçek aktif sürümle eşleşmeli, uyuşmazlık red; None = kontrol yok — zorunluluk kuralı K-94 AÇIK, Karar Kapıları tablosuna bakın).
- `activate_package(db, *, package_id, evidence, actor)` — kanıt alanlarından HERHANGİ biri sağlanmazsa `GateNotSatisfied` ile REDDEDER (fail-closed, mekanik kontrol); geçen kanıtla ham geçişi çağırır. Ham iki-adım transaction'ı `_apply_status_transition` ÖZEL fonksiyonundadır ve modül dışına verilmez — public yüzeyden kanıtsız geçiş YOLU YOKTUR. (K-103'ün konusu olan ÇAĞIRANIN KİMLİĞİNİN doğrulanması AÇIK kalır — bu arayüz kanıt-taşıma sözleşmesidir, kimlik katmanı değil; sınır dürüstçe budur.)
- `RollbackGateEvidence` (AYRI dataclass — aktivasyon kanıtıyla PAYLAŞILMAZ) — alanlar: `manager_approved: bool` (yönetici rollback onayı — spec §2.3 "aktivasyon/ret/rollback onayı"; zorunlu) · `katman1_passed: bool`. Aktivasyon alanları (eligible/açık-soru/checklist) rollback'te YER ALMAZ — acil rollback, adayın aktivasyon kapılarından bağımsızdır.
- `rollback_package(db, *, sector_id, to_version, evidence: RollbackGateEvidence, actor)` — hedef-sürüm kanıtı fonksiyon İÇİNDE doğrulanır: `to_version` o sektörde var + `archived` durumda olmalı (yoksa red); önceki sürüm hiç yoksa (ilk paket) hata rollback'i DEĞİL deaktivasyonu işaret eder (spec §13.3). Aynı sıra disiplini.
- `deactivate_package(db, *, package_id, actor)` — K-38 acil geri çekme: kanıt İSTEMEZ (acil kol; olay logu zorunlu).
- `insert_draft(db, *, sector_id, content, schema_version, run_id=None, actor) -> uuid` — doğrulayıcı GEÇMEDEN yazım yok (spec §3.6); `version` = son + 1.

**Bağlayıcı invariantlar:** `blocked`/motor koşusunun `active` yapamaması iki katmanla korunur: (1) ham geçiş özel — public yol kanıt ister; (2) kanıtta `activation_eligible=False` → red (K-28'in Plan-1 ayağı; K-103 kimlik-zorlama tekniği karar kapısı). Ters sıra DB tarafından reddedilir (Task 3 kanıtı); `draft`/`archived` runtime'da okunmaz (Task 8 kanıtı) → aktivasyon penceresi emniyetli. **Geçiş+olay atomikliği (F24):** her yaşam-döngüsü geçişinde `log_package_event` yazımı `_apply_status_transition` ile AYNI transaction'dadır — olay yazımı başarısızsa geçiş rollback olur, geçiş başarısızsa olay kalmaz (bağlanan teknik karar 8'in olay ayağı).

**Steps:**
- [ ] **Step 1:** Failing testler: `test_insert_draft_requires_valid_content` · `test_activate_archives_previous_then_activates` · `test_first_activation_single_step` · `test_activate_rejects_not_eligible` · `test_activate_rejects_open_questions` (K-71) · `test_activate_rejects_failed_katman1` · `test_activate_rejects_missing_checklist` · `test_activate_rejects_stale_base_version_when_provided` · `test_activate_allows_missing_base_version_while_k94_open` · `test_raw_transition_not_publicly_exported` · `test_rollback_restores_previous_version` · `test_rollback_rejects_without_manager_approval` · `test_rollback_allowed_while_candidate_activation_gates_fail` (aktivasyon kapıları rollback'i bloklamaz) · `test_rollback_rejects_nonexistent_or_non_archived_target` · `test_first_package_rollback_error_points_to_deactivation` · `test_deactivate_without_new_version_no_evidence_needed` · `test_lifecycle_events_recorded` · `test_event_insert_failure_rolls_back_transition` (F24: olay yazımı patlarsa durum değişmemiş kalır) · `test_transition_failure_leaves_no_event` (F24: geçiş patlarsa sahte olay kalmaz).
- [ ] **Step 2:** Koş → FAIL.
- [ ] **Step 3:** Uygula.
- [ ] **Step 4:** Koş: PASS + TAM sweep YEŞİL.
- [ ] **Step 5:** Commit: `feat(lifecycle): package activation/rollback/deactivation services`

### Task 14: Bildirim mekanizması (K-45 devre-dışı ayağı + K-56 olay-bazlı + K-44 işaret; K-45 geri-dönüş teslimi Plan 2'de)

**Files:**
- Create: `apps/social/backend/app/services/notifications.py`, `shared/db/migrations/034_admin_events.sql`, `shared/n8n-workflows/sector-package-admin-events.json` (sanitize edilmiş export — repo kuralı: her workflow değişikliği JSON olarak versiyonlanır)
- Modify: `apps/social/backend/app/routers/brands.py` (`GET /brands/{brand_id}/package-status`), `apps/social/backend/app/routers/internal.py` (`POST /internal/admin-events/dispatch-pending` — X-Internal-Key korumalı; mevcut stale-job sweeper `/internal/posts/fail-stale` deseninin birebir eşi)
- Modify: `apps/social/frontend/app/(dashboard)/marka-ayarlari/page.tsx` (panel bandı)
- Test: `apps/social/backend/tests/test_notifications.py`

**Interfaces:**
- `record_admin_event(db, *, kind, payload, idempotency_key) -> uuid` — OUTBOX yazımı: satır, tetikleyen iş transaction'ıyla BİRLİKTE commit edilir (`delivery_state='pending'`); webhook gönderimi commit SONRASI ayrı dispatch adımıdır (bağlanan teknik karar 6: 3 deneme → `failed`, idempotency key ile dedupe, en-az-bir-kez hedefi). Crash pencereleri tanımlı: commit-öncesi crash = olay yok (iş de yok — tutarlı); commit-sonrası-gönderim-öncesi crash = satır `pending` kalır, dispatcher süpürür.
- **Dispatch sahibi (çalıştırılabilir — F8 bağlaması):** `notifications.py::dispatch_pending_admin_events(db) -> DispatchReport` tek dispatch fonksiyonudur. Kira protokolü ÜÇ adım: (1) **claim** — KISA transaction: `FOR UPDATE SKIP LOCKED` ile aday satırları seç (`pending` VEYA `lease_expires_at < now()` olan `sending`; her iki durumda `attempt_count < 3` ŞARTI), `delivery_state='sending'` + `lease_expires_at = now() + kira süresi` + **`attempt_count++`** yaz, commit (claim = kalıcı deneme; eşzamanlı iki dispatcher aynı satırı asla alamaz); (2) **send** — transaction DIŞINDA n8n webhook çağrısı; (3) **finalize** — durum+kira korumalı güncelleme (bayat işçi finalize edemez): başarıda `sent`, hatada `pending`e geri (bütçe zaten claim'de düştü). Süpürücü, `sent` olamamış tükenmiş-bütçeli satırları kalıcı `failed`e çeker — F20 uygunluk kuralıyla: `pending` hemen, `sending` yalnız kirası dolmuşsa; aktif kira asla terminalleştirilmez. Gönderim-sonrası-finalize-öncesi crash → kira dolar → kalan bütçe varsa yeniden gönderim (en-az-bir-kez; payload'daki `event_id` alıcı tarafın dedupe anahtarı), bütçe bittiyse `failed` — sınırsız gönderim mümkün değil. İki tetikleyici: (a) hızlı yol — olayı yazan istek commit SONRASI dispatch'i best-effort çağırır; (b) kurtarma yolu — versiyonlu n8n SCHEDULE'ı (aynı `sector-package-admin-events.json` artefaktının schedule dalı, mevcut Auto-Posting Scheduler deseni) periyodik olarak `POST /internal/admin-events/dispatch-pending`'i çağırır → restart/crash sonrası hiçbir satır (pending YA DA süresi dolmuş sending) sahipsiz kalmaz. `sent` satır asla yeniden gönderilmez.
- Webhook payload sözleşmesi (n8n workflow JSON'ıyla birlikte versiyonlu): `{event_id, kind, payload, contract_version}`.
- `GET /brands/{brand_id}/package-status` → `{mode: 'packaged'|'unpackaged'|'maintenance', message: str|null}` — `assert_brand_owned` ZORUNLU; yanıt yalnız durum+mesaj taşır, paket içeriği asla sızmaz. `maintenance` = bayat atama (dolu `sub_sector_id`, aktif paket yok); mesajı K-45 SABİT devre-dışı metni: "Bakım çalışmaları nedeniyle gönderileriniz genel modda üretilmektedir. En kısa sürede sektöre özel gönderi moduna geçilecektir.".
- **`recovered` modu + geri-dönüş mesajı BU PLANDA YOK (F23 kapanışı — Eray yol seçimi 2026-08-24):** tetiği (reaktivasyon) yalnız Plan 2 komut ailesinden koşulabildiği için teslimi Plan 2'dedir; geri-dönüş sabit metni ("Bakım çalışması tamamlandı, sektöre özel gönderi modu kullanıma açıldı.") ve K-45 kararı KORUNUR. Plan 2 kalemi, markanın bakım-dönemine gerçek maruziyetini kanıtlayan atama-geçmişi mekanizmasını da içerir (bağlanan teknik karar 6'daki devir kaydı). Bu endpoint'in durum modeli Plan 2'de `recovered` ile GENİŞLETİLEBİLİR şekilde bırakılır (kapalı enum değil, string mode — yeni mod eklemek şema kırmaz).
- K-56 bağlaması: `stale_assignment_fallback` · `package_read_error` · `mismatch_fallthrough` olayları (Task 12) HER OLUŞTA outbox satırı üretir — eşik/oran YOK (olay-bazlı, spec §14.4).

**Bağlayıcı invariantlar:** bildirim/dispatch başarısızlığı üretimi ASLA bloklamaz; `package_read_error` DB-erişilemez alt-durumunda tek kanal `logger.error` (belgeli sınır — bağlanan teknik karar 6); durum modeli `package_events` + `admin_events`'ten türetilir, ayrı state kolonu açılmaz.

**Steps:**
- [ ] **Step 1:** Failing testler: `test_admin_event_committed_with_business_transaction` (iş transaction'ı rollback olursa olay da yok) · `test_admin_event_every_occurrence_no_threshold` · `test_package_read_error_triggers_admin_event` · `test_dispatch_after_commit_with_bounded_retry` · `test_duplicate_dispatch_deduped_by_idempotency_key` · `test_pending_events_reswept_via_internal_endpoint_after_crash` (crash simülasyonu: pending satır bırak → internal endpoint çağrısı → sent/failed'e geçiş) · `test_schema_accepts_sending_state_and_lease` · `test_crash_after_claim_expired_lease_reclaimed` (claim sonrası crash: süresi dolmuş `sending` satırı sonraki dispatch'te yeniden claim edilir) · `test_crash_after_send_before_finalize_redelivers_with_same_event_id` (en-az-bir-kez + dedupe anahtarı korunur) · `test_attempt_budget_consumed_at_claim_bounded_sends` (F19: art arda 3 claim/crash penceresi → toplam gönderim ≤3 + kalıcı `failed`) · `test_exhausted_row_not_claimable` · `test_stale_worker_cannot_finalize` · `test_active_lease_not_reclaimed` · `test_sweeper_spares_active_third_lease_and_finalize_wins` (F20: 3. deneme canlıyken sweep → satır `sending` kalır, başarılı finalize `sent` yazar) · `test_sweeper_fails_exhausted_only_after_lease_expiry` · `test_concurrent_dispatchers_single_delivery` (SKIP LOCKED kirası: iki eşzamanlı dispatch → tek gönderim) · `test_sent_row_never_redispatched` · `test_internal_endpoint_requires_internal_key` · `test_package_status_requires_ownership` · `test_package_status_maintenance_message_exact` · `test_package_status_packaged_and_unpackaged` · `test_notification_failure_does_not_block`.
- [ ] **Step 2:** Koş → FAIL.
- [ ] **Step 3:** Uygula (backend + n8n workflow JSON'ı + frontend bandı; band metni backend'den gelir, frontend'e sabit yazılmaz).
- [ ] **Step 4:** Koş: PASS + TAM sweep YEŞİL + `cd apps/social/frontend && npx next build` hatasız. (Canlı n8n importu + tek-Telegram-teslimi smoke'u MANUEL ADIM — Task 16 listesinde.)
- [ ] **Step 5:** Commit: `feat(notifications): transactional outbox + versioned n8n workflow + maintenance messaging (K-45/K-56/K-44)`

### Task 15: Atama akışı — aday küme, öneri, teyit UI

**Files:**
- Modify: `apps/social/backend/app/routers/sectors.py` (`GET /sectors/sub-sector-candidates`), `apps/social/backend/app/routers/ai.py` (`analyze_website` alt-sektör öneri alanı), `apps/social/backend/app/routers/brands.py` (`sub_sector_id` yazımı — create/update payload alanı)
- Modify: `apps/social/backend/app/models/schemas.py` (`BrandCreate`/`BrandUpdate`/`BrandOut`'a `sub_sector_id`; `analyze-website` yanıt şemasına öneri alanı — Pydantic şemasız alanı sessizce düşürür, şema değişikliği zorunlu)
- Modify: `apps/social/frontend/app/(onboarding)/onboarding/page.tsx`, `apps/social/frontend/app/(dashboard)/marka-ayarlari/page.tsx` (alt-tip teyit bileşeni — mevcut sektör seçiminin YANINDA; K-19)
- Test: `apps/social/backend/tests/test_assignment_flow.py`

**Bağlayıcı invariantlar:**
- Aday küme = spec §7.2 kanonik sorgu: `parent_sector_id IS NOT NULL` VE `status='active'` paketi olan satırlar; CANLI sorgudan (kopya/görünüm yok); önbelleksiz.
- Model önerisi kapalı doğrulama: `analyze_website` dönüşündeki alt-sektör alanı aday kümede DEĞİLSE veya serbest metinse → alan boş sayılır (üçüncü dönüş biçimi yok — spec §7.1); web sitesiz geri düşüş aynı kısıt.
- `sub_sector_id` yazımı: doluysa K-08b tetikleyicisi korur (kök satır 4xx'e çevrilir); boşaltma serbest; boş liste → UI bileşeni boş/pasif (aday yoksa öneri yok).
- Üretim akışına SORU EKLENMEZ (sürtünme yasağı) — üretim yolu aday kümesini hiç okumaz.
- Kanal envanteri doldurma UI'ı aynı ayarlar yüzeyine eklenir (4 kapalı anahtar; Task 9 doğrulaması backend'de).

**Steps:**
- [ ] **Step 1:** Failing testler: `test_candidates_only_active_packaged_sub_sectors` · `test_candidates_live_query_reflects_deactivation` · `test_empty_candidate_set_returns_empty_list` · `test_analyze_website_suggestion_must_be_in_candidates` (aday-dışı/serbest-metin öneri → alan boş; boş aday kümesinde öneri her zaman boş) · `test_brand_create_and_update_sub_sector_roundtrip_via_api` (yaz + geri oku — şema alanı uçtan uca) · `test_brand_update_rejects_root_as_sub_sector` · `test_generation_path_never_queries_candidates`.
- [ ] **Step 2:** Koş → FAIL.
- [ ] **Step 3:** Backend'i uygula; frontend teyit bileşeni + channels alanlarını ekle.
- [ ] **Step 4:** Koş: PASS + TAM sweep YEŞİL + `npx next build` hatasız.
- [ ] **Step 5:** MANUEL UI doğrulaması (frontend test altyapısı yok — dürüst sınır): lokal ortamda onayla/değiştir/boşalt üçlüsü + boş-aday pasif hâli + channels doldurma gözle doğrulanır; sonuç Task 16 raporuna "manuel doğrulandı / doğrulanamadı" olarak İŞLENİR (mutlaklık iddiası yok).
- [ ] **Step 6:** Commit: `feat(assignment): sub-sector candidate set, suggestion validation, confirm UI`

### Task 16: Kapanış — final sweep + kabul eşlemesi + Plan 2 arayüz teslimi

**Files:**
- Create: `docs/active/sektor-bilgi-paketi/PLAN1-KAPANIS.md` (kabul eşleme raporu — aktif katman içinde, spec değişmez)
- Create: `apps/social/backend/tests/test_plan2_interface_contract.py` (kanonik teslim listesinin çağrılabilirlik kanıtı)

**Steps:**
- [ ] **Step 1:** TAM test koşusu: `cd apps/social/backend && python -m pytest tests/ -v` — Beklenen: TÜMÜ PASS (Katman-1 + veri/API + iş kuralı + yaşam döngüsü + bildirim + atama).
- [ ] **Step 2:** `python scripts/sector_sweep.py --dry-run` — fark=0.
- [ ] **Step 3:** Kabul eşleme raporunu yaz: spec §14.1 deterministik çekirdek maddeleri → kanıtlayan test adı; §14.2 iş-kuralı senaryoları (Plan 1 kapsamındakiler) → test adı; kapsam DIŞI kalanlar (motor testleri, Katman-2, K-71 açık-soru DURUMUNUN üretimi — mekanik red kapısının kendisi Task 13 `test_activate_rejects_open_questions` ile Plan 1'de kanıtlanır —, kişisel-veri doğrulaması, **K-45 geri-dönüş bildirimi — recovered bandı + atama-geçmişi kanıtı, F23 devri**) → "Plan 2 / pilot" etiketiyle listelenir; KABUL EDİLEN RİSKLER açıkça yazılır (F17 edited-lineage sınırı — Eray 2026-08-23 — dahil) — mutlaklık iddiası YOK (İlke 3).
- [ ] **Step 4:** Kanonik arayüz protokolünü doğrula: arayüz-sözleşme testi (`tests/test_plan2_interface_contract.py`) "Plan 2'ye teslim edilen arayüzler" listesindeki HER fonksiyonu belgelenen argümanlarla import edip çağırır (holiday_keys dahil; geçerli bir `insert_draft` + kanıtlı `activate_package` zinciri uçtan uca). MANUEL ADIMLAR bölümü: (1) canlıda 032/033/034 psql ile (`-v ON_ERROR_STOP=1`) uygulanır; (2) `shared/n8n-workflows/sector-package-admin-events.json` n8n'e import edilir + aktive edilir + sentetik olayla TEK Telegram teslimi smoke'u koşulur; (3) Task 15 manuel UI doğrulama sonucu işlenir; (4) alt-sektör satırı AÇILMAZ (pilot/Plan 2 — korumalar hazır).
- [ ] **Step 5:** Commit: `docs: plan-1 closure report — acceptance mapping + plan-2 interface handoff`

---

## Self-Review notları (yazım sonrası kontrol edildi)

- Spec §13.2 sıra eşlemesi: adım 1→Task 2-3 · adım 2→Task 2/5 · adım 3→Task 4 · adım 4→bilinçli DIŞARIDA (satır açma pilot/Plan 2; korumalar + sweep mekanizması hazır) · adım 5→Task 5 · adım 6→Task 6-7 · adım 7→Task 8-13 · adım 8→Task 5/16.
- Katman-1 freeze (Task 7) enjeksiyon görevlerinden (10-11) ÖNCE — spec §5.1 sıra hükmü korunur; Task 8-9 üretim prompt yoluna dokunmaz ve sweep'le kanıtlar.
- Açık K-ID'lere sonuç yazılmadı; bağlanan 7 teknik karar İlke 8 kapsamında review zincirine sunulur.
