---
title: Sektör Bilgi Paketi Sistemi — Runtime Çekirdek + Araştırma Hattı Sözleşmeleri
status: superseded
superseded-note: kaynak spec superseded (2026-08-23, Eray karari); yeni spec docs/specs/2026-08-21-sektor-bilgi-paketi.md tamamlaninca yeni plan sifirdan yazilir, bu plan dikkate alinmaz
date: 2026-07-12
source_spec: docs/specs/2026-07-11-sektor-bilgi-paketi.md
source_spec_unapproved_override: false
noisy_review_override: false
unresolved_high_severity_override: false
codex_plan_review_status: approved
codex_plan_review_iterations: 8
codex_plan_targeted_fixes: 5
codex_plan_review_log: docs/reviews/codex/2026-07-12-sektor-bilgi-paketi-plan.md
---

# Sektör Bilgi Paketi — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.
>
> **P2 çıktı sözleşmesi:** Bu plan karar/invariant/arayüz/test-listesi katmanındadır. Task'lar
> tam fonksiyon gövdesi İÇERMEZ (≤5 satır kritik kesit istisnası); kod mekaniği execute-time
> TDD'nin işidir. Test adları + kanıtladıkları davranış bağlayıcıdır.

**Goal:** Alt-sektör düzeyinde sürümlü "sektör bilgi paketleri"ni runtime çekirdeğiyle kurmak:
veri modeli + trigger kilitleri, taksonomi korumaları, tek-kapı enjeksiyon, K6 byte-exact
regresyon kapısı, K7 sürüm damgası, atama akışı ve elle kuyumculuk pilotu.

**Architecture:** Spec §14 faz-hattı birebir (Faz 0→4). Önce güvenlik ağı (Tier-1 satırı + K6
golden baseline), sonra DB katmanı (migration 032 + 6 invariant ailesi trigger'la), sonra
tek-kapı modülü üzerinden 7 yüzeye koşullu enjeksiyon + K7 damga (release-gate: tek artım),
sonra atama (LLM önerir/kullanıcı teyit eder), en sonda manuel pilot koreografisi.

**Tech Stack:** FastAPI + asyncpg + Pydantic v2 (backend), PostgreSQL 16 (PL/pgSQL trigger'lar),
pytest (+pytest-asyncio yalnız DB testleri), Docker (throwaway test Postgres), Next.js frontend.

## Global Constraints (spec'ten — her task'a örtük dahil)

- **Komut konvansiyonu (cwd sözleşmesi):** Bu plandaki TÜM `.venv/bin/...`, `npm run build`
  dışı backend ve pytest komutları **cwd = `apps/social/backend`** varsayar (repo kökünden:
  `cd apps/social/backend && <komut>`); `npm` komutları cwd = `apps/social/frontend`. T6
  migration runner'ı `shared/db/migrations` dizinini cwd'den DEĞİL, `pathlib` ile dosya
  konumundan repo köküne çıkarak çözer (her cwd'den çalışır) ve uyguladığı dizini loglar.

- **K6 Katman-1:** paketsiz/atamasız markada LLM'e giden TÜM prompt metinleri **byte-exact
  değişmez**; kanıt `golden == üretilen string` (normalize/whitespace/anlam toleransı YOK),
  koşum tek komut: `.venv/bin/pytest tests/regression/ -q` (tekrar-çalıştırılabilir).
  **Kapsam netleştirmesi:** K6 mühür kümesi = §6.2 içerik-üretim yüzeyleri + Tier-1 (s0).
  `analyze-website` İÇERİK-üretim yüzeyi DEĞİL (marka-öncesi analiz ucu) ve spec §5 prompt'una
  aday listesi eklenmesini AÇIKÇA ister — bu bilinçli değişiklik K6-dışıdır, kendi hedefli
  regresyonuyla korunur (T27: aday listesi boşken bugünkü prompt'la byte-eşit → aktif paket
  yokken canlı davranış birebir).
- **Yerine-geçme:** paket bloğu ile SECTOR_GUIDANCE **yan yana basılmaz**.
- Paket her yüzeyde **EK BAĞLAM**; tek geçersiz-kılıcı istisna §7 anma/kutlama kısıtı (K3).
- `brands.sector` TEXT ve `brands.sector_id` (kök kova) anlamı **dokunulmaz**; alt-sektör yalnız
  `brands.sub_sector_id`.
- Draft paket normal üretim yoluna **sızmaz**; preview yalnız operatör-iç yol (§6.1 a/b/c).
- TÜM draft/artefakt DB yazımı tek kapı: `apps/social/backend/scripts/import_sector_package.py`
  (Pydantic doğrulayıcı script'in içinde); doğrudan SQL yazımı desteklenmez.
- **RELEASE GATE:** paket bağlamıyla üretebilen HİÇBİR artım, K7 damga persistence'ı olmadan
  deploy edilemez (Faz 2 tek deploy artımı).
- Migration: `shared/db/migrations/032_sector_packages.sql` **tek dosya**, forward-only additive
  (repo konvansiyonu; down migration konvansiyonu yok).
- Golden dosya değişikliği = bilinçli davranış değişikliği → **ayrı commit + gerekçe**.
- Komut ailesi (`/sektor-paket-guncelle`) bu plana **girmez** (evi:
  `docs/plans/<tarih>-sektor-paket-komut-ailesi.md`, runtime + ilk elle tur SONRASI).
- Legacy `/posts/generate-short-video` (posts.py:846-847) paket enjeksiyonu **almaz**;
  bozuk-boş davranış korunur (K6 fixture kanıtlar).

## Dosya Haritası

**Yeni:**
| Path | Sorumluluk |
|---|---|
| `apps/social/backend/requirements-dev.txt` | pytest ailesi (pin-at-install) |
| `apps/social/backend/pytest.ini` | testpaths + `db` marker + default `-m "not db"` |
| `apps/social/backend/tests/regression/conftest.py` | K6 dondurulmuş fixture'lar (DB'siz) |
| `apps/social/backend/tests/regression/capture_golden.py` | golden üretim scripti (bilinçli güncelleme ritüeli) |
| `apps/social/backend/tests/regression/test_k6_surfaces.py` | yüzey #1-#8 byte-exact + paketli kanıt testleri |
| `apps/social/backend/tests/regression/golden/*.txt` | commit'li golden dosyaları |
| `apps/social/backend/tests/db/conftest.py` | throwaway Docker PG16 + migration runner (`db` marker) |
| `apps/social/backend/tests/db/test_migration_032.py` | 6 invariant ailesi trigger testleri (§15-1) |
| `apps/social/backend/tests/db/test_taxonomy_guards.py` | /sectors + resolver + trend koruma testleri |
| `apps/social/backend/tests/db/test_package_pipeline.py` | import/load/preview/aktivasyon DB testleri |
| `apps/social/backend/tests/db/test_k7_stamp_integration.py` | K7 damga persist entegrasyon testleri (mocked LLM/fal — release-gate kanıtı) |
| `apps/social/backend/app/core/holiday_keys.py` | `normalize_holiday_key` TEK fonksiyon (§7, üç tüketici) |
| `apps/social/backend/app/models/sector_package.py` | `SectorPackageContentV1` + decision_log şeması (§3.3) |
| `apps/social/backend/app/core/sector_package_context.py` | tek kapı: load + tüketici API (§6.1) |
| `apps/social/backend/scripts/import_sector_package.py` | tek public draft+artefakt import kapısı (§3.3/§11) |
| `apps/social/backend/scripts/activate_sector_package.py` | aktivasyon/rollback tek-transaction operatör aracı (§3.2) |
| `apps/social/backend/scripts/add_sub_sector.py` | alt-sektör satırı ekleme aracı (Faz 4) |
| `apps/social/backend/scripts/assign_sub_sector.py` | marka→alt-sektör operatör ataması (pilot/elle atama — draft döneminde UI aday listesi bilinçli boş) |
| `shared/db/migrations/032_sector_packages.sql` | iki tablo + trigger'lar + indeksler + 2 kolon (T10'da TEK commit — F20) |
| `apps/social/frontend/scripts/check-k7-echo.mjs` | K7 echo statik sözleşme kontrolü (F19) |

**Değişen:** `app/core/prompt_builder.py` (Tier-1 satırı; #1/#3/#4), `app/core/caption_generator.py`
(#2), `app/services/short_video.py` (#5/#6/#7 + damga), `app/routers/ai.py` (#4 çağrısı + Faz 3),
`app/routers/sectors.py` (+cache key), `app/services/sector_resolver.py` (+cache key),
`app/routers/brands.py`, `app/routers/posts.py` (damga), `app/routers/internal.py` (preview ucu),
`app/models/schemas.py`, `apps/social/backend/CLAUDE.md`, frontend:
`apps/social/frontend/app/(onboarding)/onboarding/page.tsx`,
`apps/social/frontend/app/(dashboard)/markalar/page.tsx`,
`apps/social/frontend/app/(dashboard)/marka-ayarlari/page.tsx` (+ frontend API client dosyası).

## Plan-Düzeyi Karar Kayıtları (spec'in açık bıraktığı noktalar — bu planda bağlanır)

| # | Karar | Gerekçe |
|---|---|---|
| D1 | **Redis cache key bump:** `sectors.py` `_CACHE_KEY` → `"otomaix:social:sectors:list:v2"`; `sector_resolver.py` `_CACHE_KEY` → `"otomaix:social:sector_slug_map_v3"` | Filtre değişimi eski cache'le 1 saate kadar filtresiz veri servis eder; spec anmıyor, invariant ihlali penceresi kapanır |
| D2 | **Test ortamı:** backend `.venv` + `requirements.txt` + `requirements-dev.txt`; DB testleri throwaway Docker PG16 — imaj `pgvector/pgvector:pg16` (001 `CREATE EXTENSION vector` ister; stok `postgres:16` pgvector içermez — 2026-07-12 doğrulu), port 127.0.0.1:5439, migrations 001→032 sırayla; fallback (ampirik blokaj çıkarsa): lokal 5433'ten `pg_dump --schema-only` baseline + pgvector'lü boş DB'ye ayrı sequential-apply kontrolü | Canlı/lokal 5433'e yazma YOK; prod-yolu birebir reprodüksiyon; test imajı extension-eşdeğer olmalı |
| D3 | **K6 default koşumu DB'siz:** `pytest.ini` `addopts = -m "not db"`; DB testleri açıkça `-m db` ile | K6 hızlı + docker'sız koşulabilir kalır |
| D4 | **K6 fixture felsefesi:** sentetik dondurulmuş girdiler (katalogdan bağımsız `Template` instance'ı, sabit brand/brand_kit/product/special_day); paketsiz fixture `sector_slug="e-ticaret-perakende"` (gerçek SECTOR_GUIDANCE anahtarı — o metin de mühürlenen yüzeyin parçası). DNA-boş profil (c) şimdilik paketsiz (a) ile özdeş alias — DNA spec'i gelince ayrışır (bağlantı noktası 2) | Katalog verisi drift'i K6'yı kırmamalı; SECTOR_GUIDANCE kod-içi metin olduğundan mühürlenir |
| D5 | **Preview mekanizması:** üretim pipeline fonksiyonlarına `preview_package_id: UUID \| None = None` parametresi; kullanıcı route'larının request şemalarına alan EKLENMEZ; tek giriş `POST /internal/posts/generate-preview` (X-Internal-Key korumalı, internal.py) | §6.1-a yapısal sağlanır: kullanıcı-erişilebilir API yüzeyinde preview girdisi fiziksel yok |
| D6 | **normalize_holiday_key evi:** `app/core/holiday_keys.py` (bağımsız modül) | üç tüketici (runtime lookup, Pydantic validator, ileride komut ailesi EK-J) import döngüsüz paylaşır |
| D7 | **Aktivasyon aracı:** `scripts/activate_sector_package.py` (`activate` / `rollback` alt-komutları, §3.2 tek-transaction sırası) | Operatör elle SQL yazmaz; sıra hatası fiziksel imkânsız (kısmi indeks) ama araç UX + kayıt sağlar |
| D8 | **Damga persist kanıtı = mocked-boundary entegrasyon testleri (release-gate şartı):** üretim akışları dış servis sınırları mock'lanarak (Anthropic/fal/R2/TTS — kredi yakılmaz) throwaway test DB'sine karşı UÇTAN koşulur; `posts.sector_package_id` yazımı otomatik assert edilir (paketli → id, paketsiz → NULL, preview → draft id). Faz 4 pilotu CANLI teyittir, birincil kanıt değil. (İlk taslakta pilot'a ertelenmişti — Codex Turn 2 F2 bulgusuyla release-gate kanıtına yükseltildi) | Grep + DB trigger'ları uygulama-katmanı persist sözleşmesini KANITLAMAZ; damgasız paket-üretim penceresi release-gate ihlali olurdu |
| D9 | **Ekstraksiyon neutrality kanıt sınırı (dürüst etiket):** Faz 0 taşımaları (suggest-ideas, director) mekanik satır-taşıma + diff-review ile doğrulanır; K6'nın kanıtladığı şey ekstraksiyon-SONRASI fazların değişmezliğidir (baseline ekstraksiyon sonrası mühürlenir — spec §10.2 sırası) | Ekstraksiyon-öncesi kod import edilemez (inline); çift-capture kurmak YAGNI |
| D10 | **suggest-sub-sector ucu:** web-sitesiz marka akışı için `POST /ai/suggest-sub-sector` (ayrı hafif uç, aynı aday-liste + server-side doğrulama yardımcılarını paylaşır) | Spec "aynı çağrı ailesi, aynı doğrulama" der; analyze-website sözleşmesini şişirmez |

---

# FAZ 0 — Güvenlik Ağı (Tier-1 satırı → K6 baseline)

### Task 1: Tier 1 hiyerarşi satırı (§9 — kabul edilmiş tek seferlik global değişiklik)

**Files:**
- Modify: `apps/social/backend/app/core/prompt_builder.py:111-113` (`_SYSTEM_RULES` içindeki "MARKA TONU ÖNCELİKLİDİR" bloğu)

**Interfaces:**
- Produces: `_SYSTEM_RULES` yeni hiyerarşi metni — sonraki tüm golden'lar bu metni içerir.

**Bağlayıcı içerik (spec §9 birebir):** mevcut 3 satırlık blok, şu hiyerarşiyi kuran blokla
DEĞİŞTİRİLİR: **marka DNA'sı/tonu > sektör paketi/rehberi > platform tonu**; çatışmada üstteki
kazanır; sektör paketi/rehberi markaya EK bağlamdır, marka kimliğini geçersiz kılamaz; platform
tonu en alttaki uyarlama katmanıdır. (DNA terimi, DNA alanları gelene dek boş kümeye işaret
eder — satır metni DNA spec'inde DEĞİŞMEZ; ikinci dokunuş gerekmemesi başarı kriteri 7.)

- [ ] **Step 1:** Bloğu yaz (yalnız 111-113 aralığı; `_SYSTEM_RULES` başka satırına dokunma).
- [ ] **Step 2:** Doğrula: `python3 -c "from app.core import prompt_builder; print('marka DNA' in prompt_builder._SYSTEM_RULES)"` (cwd: `apps/social/backend`) → `True`; `git diff --stat` yalnız 1 dosya.
- [ ] **Step 3:** Commit (tek başına — spec §10.2-1): `feat(social-backend): expand tier-1 tone rule to DNA>package>platform hierarchy`

**Dürüst etiket:** Bu commit davranış-nötr İDDİA EDİLMEZ (kabul edilmiş global prompt
değişikliği). K6 baseline bundan SONRA mühürlenir. İsteğe bağlı ek gözlem (operatör isterse,
K6'dan ayrı): eski/yeni sistem prompt'uyla küçük caption korpusu — bu plana görev olarak GİRMEZ.

### Task 2: pytest bootstrap (test altyapısı sıfırdan)

**Files:**
- Create: `apps/social/backend/requirements-dev.txt`, `apps/social/backend/pytest.ini`,
  `apps/social/backend/tests/regression/__init__.py` yerine boş dizin + `tests/db/` dizini
  (pytest package-mode kullanılmaz; conftest yeterli)

**Interfaces:**
- Produces: `.venv/bin/pytest` koşulabilir; `db` marker'ı; default koşum DB'siz (D3).

- [ ] **Step 1:** `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt` (cwd:
  `apps/social/backend`). Beklenen: temiz kurulum (fal-client/asyncpg dahil).
- [ ] **Step 2:** `.venv/bin/pip install pytest pytest-asyncio` → `.venv/bin/pip freeze | grep -E "^pytest" > requirements-dev.txt` (pin-at-install; sürüm plan yazımında sabitlenmez).
- [ ] **Step 3:** `pytest.ini` yaz — içerik sözleşmesi: `testpaths = tests`; `addopts = -m "not db"`;
  `markers = db: throwaway Docker Postgres gerektirir (K6 koşumundan ayrı)`.
- [ ] **Step 4:** Doğrula: `.venv/bin/pytest --collect-only -q` → `no tests ran` (temiz exit 5 kabul);
  `.venv/bin/python -c "import app.core.prompt_builder, app.core.caption_generator, app.services.short_video"` → sessiz (Settings env'siz import-güvenli — config.py tüm alanlar default'lu).
- [ ] **Step 5:** Commit: `chore(social-backend): bootstrap pytest infra (venv, dev reqs, db marker)`

### Task 3: suggest-ideas Tier-2 kurulumunu saf fonksiyona çıkar (yüzey #4 ön şartı)

**Files:**
- Modify: `apps/social/backend/app/core/prompt_builder.py` (yeni fonksiyon),
  `apps/social/backend/app/routers/ai.py:263-291` (inline blok → çağrı)

**Interfaces:**
- Produces: `build_suggest_ideas_brand_context(brand: dict, brand_kit: dict, template: Template | None) -> str`
  (prompt_builder'da public; ai.py:264-291'deki `brand_context_parts` inşasının birebir taşınması —
  marka satırları + SECTOR_GUIDANCE dalı + şablon dalı DAHİL).
- Consumes: ai.py mevcut yerel değişkenleri (`colors_str`, `tonality`, `hashtags` türetimleri
  fonksiyon İÇİNE taşınır; girdi yalnız `brand`, `brand_kit`, `template`).

- [ ] **Step 1:** Fonksiyonu prompt_builder'a mekanik taşı (satırlar aynen; string'lerde tek
  karakter değişiklik YOK); ai.py'de inline bloğu çağrıyla değiştir.
- [ ] **Step 2:** Doğrula (davranış-nötr, D9): `git diff` gözden geçir — taşınan string literal'ler
  birebir; `.venv/bin/python -c "from app.core.prompt_builder import build_suggest_ideas_brand_context"` sessiz.
- [ ] **Step 3:** Commit: `refactor(social-backend): extract suggest-ideas brand context builder`

### Task 4: Kısa video director prompt kurulumunu saf fonksiyona çıkar (yüzey #5/#6 ön şartı)

**Files:**
- Modify: `apps/social/backend/app/services/short_video.py` (~110-231: context_parts +
  framing blokları + iki modun system_prompt inşası)

**Interfaces:**
- Produces: `build_director_prompt(*, image_edit_mode: bool, user_brief: str | None, brand_name: str | None, brand_description: str | None, sector: str | None, product_info: str | None, product_doc_context: str | None, topic: str | None, color_str: str | None) -> tuple[str, str]`
  → `(system_prompt, context)`; Anthropic çağrısı ve fallback DIŞARIDA kalır (mevcut fonksiyon
  bu builder'ı çağırır).

- [ ] **Step 1:** Builder'ı mekanik çıkar (iki mod tek fonksiyonda, `image_edit_mode` dalı korunur;
  string literal'lere dokunma); çağıran director fonksiyonu builder'ı kullanacak şekilde bağla.
- [ ] **Step 2:** Doğrula: `git diff` — literal'ler birebir; import smoke sessiz.
- [ ] **Step 3:** Commit: `refactor(social-backend): extract short-video director prompt builder`

### Task 5: K6 iskeleti + paketsiz golden baseline (yüzey #1-#8)

**Files:**
- Create: `tests/regression/conftest.py`, `tests/regression/capture_golden.py`,
  `tests/regression/test_k6_surfaces.py`, `tests/regression/golden/` (backend kökü altında)

**Interfaces:**
- Consumes: `build_brand_context`, `build_dynamic_content`, `build_suggest_ideas_brand_context`
  (T3), `build_director_prompt` (T4), `caption_generator._build_output_format_instruction`,
  `short_video._MOTION_PROMPTS`, `templates_data.SECTOR_GUIDANCE`.
- Produces: dondurulmuş fixture sabitleri (`FROZEN_BRAND`, `FROZEN_BRAND_KIT`, `FROZEN_TEMPLATE`
  [sentetik `models.templates.Template`], `FROZEN_PRODUCT`, `FROZEN_SPECIAL_DAY`) — Faz 2 paketli
  testleri AYNI fixture'ları kullanır; golden dosya adlandırma: `golden/s{N}_{yuzey}__paketsiz.txt`.

**Yüzey → çağrı haritası (kapsam = §6.2 TAMAMI + Tier-1 global mühür):**
| # | Golden | Çağrı |
|---|---|---|
| 0 | `s0_system_prompt__paketsiz.txt` | `build_system_prompt()[0]["text"]` (Tier-1 `_SYSTEM_RULES` — §6.2'de değil ama "LLM'e giden TÜM metin" kapsamında; §10.2 baseline'ı kabul edilmiş Tier-1 değişikliğinin SONRASINI mühürler — sonraki fazlarda kazara Tier-1 dokunuşu K6'dan kaçamaz) |
| 1 | `s1_tier2__paketsiz.txt` | `build_brand_context(FROZEN_BRAND, FROZEN_BRAND_KIT, FROZEN_TEMPLATE)` |
| 2 | `s2_output_format__paketsiz.txt` | `_build_output_format_instruction(...)` (sabit argümanlar conftest'te dondurulur) |
| 3 | `s3_dynamic_specialday__paketsiz.txt` | `build_dynamic_content(..., special_day=FROZEN_SPECIAL_DAY)` |
| 4 | `s4_suggest_ideas__paketsiz.txt` | `build_suggest_ideas_brand_context(...)` |
| 5 | `s5_director_t2i__paketsiz.txt` | `build_director_prompt(image_edit_mode=False, ...)` (iki eleman `\n===SPLIT===\n` ile birleştirilir) |
| 6 | `s6_director_edit__paketsiz.txt` | `build_director_prompt(image_edit_mode=True, ...)` |
| 7 | `s7_motion_pool__paketsiz.txt` | `"\n".join(short_video._MOTION_PROMPTS)` (havuz-düzeyi, §8) |
| 8 | `s8_legacy_lookup` (golden'sız assert) | `SECTOR_GUIDANCE.get(FROZEN_BRAND["sector"], "") == ""` (display-name anahtarsızlığı = bozuk-boş sabitleme) |

- [ ] **Step 1 (RED):** `test_k6_surfaces.py` testlerini yaz — her yüzey için
  `test_s{N}_<yuzey>_paketsiz_golden_exact` (byte-exact `==` assert; fark halinde repr diff;
  s0 dahil: `test_s0_system_prompt_paketsiz_golden_exact`) +
  `test_s8_legacy_display_name_lookup_empty`. Koş: `.venv/bin/pytest tests/regression/ -q` →
  **FAIL** (golden dosyaları yok).
- [ ] **Step 2 (baseline):** `capture_golden.py` yaz (her yüzeyi fixture'larla çağırır, golden/
  altına yazar; yalnız bilinçli güncellemede elle koşulur) ve koş:
  `.venv/bin/python -m tests.regression.capture_golden` → 8 golden dosyası (s0-s7).
- [ ] **Step 3 (GREEN):** `.venv/bin/pytest tests/regression/ -q` → `9 passed` (8 golden + legacy).
- [ ] **Step 4:** Commit (golden'lar dahil — baseline mührü):
  `test(social-backend): K6 harness + packageless golden baseline (surfaces 1-8)`

---

# FAZ 1 — Migration 032 + Taksonomi Korumaları

### Task 6: DB test altyapısı (throwaway Postgres + migration runner)

**Files:**
- Create: `apps/social/backend/tests/db/conftest.py`

**Interfaces:**
- Produces: `db_conn` async fixture (asyncpg; her test modülü için taze DB, migrations 001→
  mevcut-son sırayla uygulanmış); `apply_migrations(conn_params, upto: str)` yardımcı;
  marker: tüm tests/db testleri `pytestmark = pytest.mark.db`.

**Mekanizma (D2):** session-scoped fixture `docker run --rm -d --name otomaix-test-pg -e
POSTGRES_HOST_AUTH_METHOD=trust -p 127.0.0.1:5439:5432 pgvector/pgvector:pg16` başlatır
(throwaway container — parolasız trust auth, lokal port'a bağlı; pgvector'lü imaj: 001
`CREATE EXTENSION "vector"` gerektirir, pgcrypto contrib'de zaten var), hazır-bekler,
migration dizinini **`pathlib` ile conftest konumundan repo köküne çıkarak** çözer
(`shared/db/migrations` — cwd'den bağımsız; çözülen dizin loglanır) ve `*.sql` dosyalarını
**dosya adı sırasıyla** uygular, teardown'da container'ı durdurur. **Ampirik doğrulama görevi:** 001→031'in boş PG16'ya temiz uygulandığı BU task'ta
kanıtlanır; blokaj çıkarsa fallback D2 (schema-only dump baseline) uygulanır ve conftest
docstring'ine gerekçe yazılır.

- [ ] **Step 1 (RED):** `tests/db/test_migration_032.py` içine smoke test yaz:
  `test_migrations_apply_clean_through_031` (031 sonrası `social.sectors`/`social.brands`/
  `social.posts` tabloları var + `sectors.parent_sector_id` kolonu var). Koş:
  `.venv/bin/pytest tests/db/ -q -m db` → **FAIL/ERROR** (conftest yok).
- [ ] **Step 2 (GREEN):** conftest'i yaz; koş → `1 passed`.
- [ ] **Step 3:** Commit: `test(social-backend): disposable Postgres fixture + migration runner`

### Task 7: Migration 032 — tablolar, indeksler, kolonlar, append-only

**Files:**
- Create: `shared/db/migrations/032_sector_packages.sql` (bölüm 1)
- Test: `apps/social/backend/tests/db/test_migration_032.py`

**Bağlayıcı DDL sözleşmesi (spec §3.1/§3.2/§3.4 birebir):** `social.sector_research_artifacts`
(kolonlar + `kind` CHECK + `(sector_slug, run_id)` indeksi + **BEFORE UPDATE OR DELETE →
RAISE** trigger'ı; `sector_slug` FK'sız — bilinçli); `social.sector_packages` (kolonlar +
`UNIQUE (sector_id, version)` + kısmi unique indeks `one_active_package_per_sector
WHERE status='active'` + `run_id NOT NULL`); `brands.sub_sector_id UUID NULL REFERENCES
social.sectors(id)`; `posts.sector_package_id UUID NULL REFERENCES social.sector_packages(id)`
(ON DELETE default NO ACTION).

- [ ] **Step 1 (RED):** Test listesi (hepsi `test_migration_032.py`):
  - `test_artifacts_update_raises`, `test_artifacts_delete_raises` (append-only)
  - `test_artifacts_queryable_by_run_id` (indeksli sorgu döner)
  - `test_package_run_id_not_null_rejected`
  - `test_second_active_package_rejected` (kısmi unique)
  - `test_new_columns_exist` (`brands.sub_sector_id`, `posts.sector_package_id`)
  Koş → **FAIL** (032 yok).
- [ ] **Step 2 (GREEN):** 032 bölüm 1'i yaz; koş → hepsi PASS.
- [ ] **Step 3:** **Commit YOK (F20 — bilinçli istisna):** 032 forward-only migration'dır ve
  runner dosya adıyla uygular — KISMİ halde tarihe geçerse ara-commit'ten yapılan bir apply
  yarı-korumalı şema kurar. TDD döngüsü (RED→GREEN) her bölümde lokal koşulur; dosya + tüm
  testler T10 sonunda TEK commit'le girer.

### Task 8: Migration 032 — subtype kilidi (ortak trigger fonksiyonu)

**Files:**
- Modify: `shared/db/migrations/032_sector_packages.sql` (bölüm 2 — aynı dosyaya eklenir)
- Test: `tests/db/test_migration_032.py`

**Bağlayıcı invariant (§3.2/§3.4):** TEK trigger fonksiyonu; işaret edilen `sectors` satırının
`parent_sector_id`si NULL ise RAISE. İki bağlama noktası: `sector_packages.sector_id`
(BEFORE INSERT/UPDATE) ve `brands.sub_sector_id` (BEFORE INSERT/UPDATE, yalnız kolon doluysa).

- [ ] **Step 1 (RED):** `test_root_sector_package_insert_raises`,
  `test_sub_sector_package_insert_ok`, `test_brand_sub_sector_root_assignment_raises`,
  `test_brand_sub_sector_valid_assignment_ok` → FAIL.
- [ ] **Step 2 (GREEN):** Bölüm 2'yi yaz; koş → PASS. (Test DB'sinde alt-sektör fixture satırı:
  conftest yardımcıyla `sectors`'a parent'lı satır insert'i — testler arası paylaşılır.)
- [ ] **Step 3:** **Commit YOK** (F20 — T7 Step 3 notu; tek commit T10'da).

### Task 9: Migration 032 — durum makinesi + donmuşluk + damga-donması + silme

**Files:**
- Modify: `shared/db/migrations/032_sector_packages.sql` (bölüm 3)
- Test: `tests/db/test_migration_032.py`

**Bağlayıcı invariantlar (§3.2 birebir):**
- Durum makinesi TAM liste: `draft→active`, `draft→archived`, `active→archived`,
  `archived→active`; başka geçiş RAISE. `→active` geçişinde `activated_at = now()` set.
- Donmuşluk (a): `status != 'draft'` satırda `content/version/schema_version/sector_id/
  decision_log/run_id` değişimi RAISE (yalnız status + activated_at geçişi serbest).
- Damga-donması (b): `posts.sector_package_id`'den REFERANSLANAN satırda (draft dahil) aynı
  içerik alanları değişimi RAISE (EXISTS kontrolü).
- Silme: yalnız `status='draft'` VE referanssız satır silinebilir (trigger draft-only; FK
  referanslıyı zaten korur).

- [ ] **Step 1 (RED):** Test listesi:
  - `test_transition_draft_to_active_ok`, `test_transition_draft_to_archived_ok`,
    `test_transition_active_to_archived_ok`, `test_transition_archived_to_active_ok`
  - `test_transition_archived_to_draft_raises`, `test_transition_active_to_draft_raises`
  - `test_nondraft_content_update_raises` (6 donmuş alan parametrize)
  - `test_referenced_draft_content_update_raises` + `test_unreferenced_draft_editable` (damga-donması)
  - `test_nondraft_delete_raises`, `test_referenced_draft_delete_raises`, `test_unreferenced_draft_delete_ok`
  Koş → FAIL.
- [ ] **Step 2 (GREEN):** Bölüm 3'ü yaz; koş → PASS.
- [ ] **Step 3:** **Commit YOK** (F20 — tek commit T10'da).

### Task 10: Migration 032 — provenance kilidi + yayın kilidi + rollback zinciri

**Files:**
- Modify: `shared/db/migrations/032_sector_packages.sql` (bölüm 4 — dosya bu task'ta TAMAMLANIR)
- Test: `tests/db/test_migration_032.py`

**Bağlayıcı invariantlar (§3.2/§3.4 birebir):**
- Aktivasyon-provenance: HER `→active` geçişi, paketin `(sector, run_id)` çifti için
  `sector_research_artifacts`'ta ≥1 `kind='synthesis'` satırı şart (sektör eşleşmesi
  `sectors.slug` JOIN'iyle); yoksa RAISE.
- Yayın kilidi (`posts` trigger'ı): kapsam `BEFORE INSERT OR UPDATE OF status,
  sector_package_id`; `sector_package_id` DOLU satır yayın-durum kümesinde
  (`publishing`/`published`/`partially_published`) OLUŞURKEN, o kümeye GEÇERKEN veya damga
  DEĞİŞİRKEN paket `active` değilse RAISE.
- Rollback tek akış: önce aktif→archived, sonra hedef arşivli→active (tek transaction; kısmi
  indeks sırayı zorlar); içerik alanlarına dokunulmaz.

- [ ] **Step 1 (RED):** Test listesi:
  - `test_activation_without_synthesis_raises`, `test_activation_with_synthesis_ok`
  - `test_publish_transition_with_draft_stamp_raises` (3 yayın status'u parametrize, UPDATE yolu)
  - `test_publish_insert_with_draft_stamp_raises` (3 status parametrize, INSERT yolu)
  - `test_published_post_restamp_to_draft_raises` (UPDATE OF sector_package_id yolu)
  - `test_publish_after_activation_ok` (aynı post, paket aktive edilince yayınlanır)
  - `test_v2_activation_then_rollback_single_active_each_step` (v1 aktif → v2 aktive [v1
    archived] → v1'e rollback; her adımda `COUNT(*) WHERE status='active'` = 1; rollback'te
    provenance yeniden geçer — artifacts append-only)
  Koş → FAIL.
- [ ] **Step 2 (GREEN):** Bölüm 4'ü yaz; koş → tests/db TÜMÜ PASS.
- [ ] **Step 3:** K6 koş: `.venv/bin/pytest tests/regression/ -q` → `9 passed` (golden değişmedi —
  migration prompt yüzeyine dokunmaz, kanıtla).
- [ ] **Step 4:** **TEK commit (F20 — 032 ancak TAM invariant setiyle tarihe geçer):** dosya +
  T7-T10 test dosyaları birlikte: `feat(db): migration 032 — sector packages (complete invariant set)`

### Task 11: `GET /sectors` kök filtresi + cache key bump

**Files:**
- Modify: `apps/social/backend/app/routers/sectors.py:16` (`_CACHE_KEY`) + `:27-33` (sorgu)
- Test: `tests/db/test_taxonomy_guards.py`

**Bağlayıcı değişiklik:** sorguya `WHERE parent_sector_id IS NULL`; `_CACHE_KEY` →
`"otomaix:social:sectors:list:v2"` (D1). Response şeması DEĞİŞMEZ.

- [ ] **Step 1 (RED):** `test_sectors_endpoint_returns_only_roots` (alt-sektör satırı ekliyken
  uç yalnız kök döner — sorgu fonksiyonu test DB bağlantısıyla; cache katmanı test'te bypass/fake)
  → FAIL.
- [ ] **Step 2 (GREEN):** Filtre + key bump; koş → PASS. K6 koş → `9 passed`.
- [ ] **Step 3:** Commit: `feat(social-backend): root-only /sectors + cache key bump`

### Task 12: `sector_resolver` kök filtresi + cache key bump + trend sabitleme

**Files:**
- Modify: `apps/social/backend/app/services/sector_resolver.py:19` (`_CACHE_KEY`) + `:59` (sorgu)
- Test: `tests/db/test_taxonomy_guards.py`

**Bağlayıcı değişiklik:** harita sorgusuna `WHERE parent_sector_id IS NULL`; `_CACHE_KEY` →
`"otomaix:social:sector_slug_map_v3"` (D1). Kısmi-eşleşme mantığına dokunulmaz.

- [ ] **Step 1 (RED):** Testler:
  - `test_resolver_maps_kuyumculuk_to_root_bucket_with_sub_sector_present` (alt-sektör
    "kuyumculuk" satırı DB'de VARKEN `resolve_sector(db, "Kuyumculuk")` kök kovaya döner —
    spec §4-2 regresyonu)
  - `test_trend_sweep_query_excludes_sub_sectors` (layer_a.py:261-264 sorgusu alt-sektör
    satırını döndürmez — mevcut bağışıklık test ile sabitlenir, İŞ YOK)
  Koş → resolver testi FAIL (bugün tüm satırlar haritada).
- [ ] **Step 2 (GREEN):** Filtre + key bump; koş → PASS. K6 → `9 passed`.
- [ ] **Step 3:** Commit: `feat(social-backend): root-only sector resolver map + trend guard test`

### Task 13: Faz 1 kapanışı — deploy checkpoint [MANUEL ADIM İÇERİR]

- [ ] **Step 1:** Tam doğrulama: `.venv/bin/pytest tests/db/ -q -m db` → tümü PASS;
  `.venv/bin/pytest tests/regression/ -q` → `9 passed`.
- [ ] **Step 2 [MANUEL — Eray onayı]:** Canlıya migration 032 uygulaması (psql ile; Coolify
  container ya da 5433 yazma-yetkili bağlantı). **F20 kapısı: apply YALNIZ T10'un tek-commit'i
  tarihte varken yapılır (kısmi 032 hiçbir zaman tarihe girmediğinden ara-commit apply'ı
  fiziksel imkânsız).** Sıra güvencesi: 032 additive — kod deploy'undan
  ÖNCE uygulanır; alt-sektör SATIRI bu fazda EKLENMEZ (satır yaratımı yalnız Faz 4 pilotta,
  filtreler canlıdayken).
- [ ] **Step 3 [MANUEL]:** Backend deploy (Coolify) — filtreler + cache key bump canlıya çıkar.
- [ ] **Step 4:** `apps/social/backend/CLAUDE.md` migration listesine 028-032 satırlarını ekle
  (spec §16 bakım notu). Commit: `docs(social-backend): update migration list through 032`

---

# FAZ 2 — Tek Kapı + Yüzey Enjeksiyonları + K7 (RELEASE GATE: tek deploy artımı)

### Task 14: `normalize_holiday_key` (K1 — TEK fonksiyon)

**Files:**
- Create: `apps/social/backend/app/core/holiday_keys.py`
- Test: `apps/social/backend/tests/regression/test_holiday_keys.py` (DB'siz — K6 koşumunda döner)

**Interfaces:**
- Produces: `normalize_holiday_key(name_tr: str) -> str`; `HOLIDAY_KEY_EXCEPTIONS: dict[str, str]`
  (kod sabiti, BOŞ başlar).

**Bağlayıcı davranış (spec §7 örnekleri birebir test olur):**
1. Gün-eki kırpma: `"Ramazan Bayramı 2. Gün"` → `"ramazan-bayrami"`;
   `"Kurban Bayramı Arife"` → `"kurban-bayrami"`.
2. Türkçe-güvenli slugify: `"Ulusal Egemenlik ve Çocuk Bayramı"` →
   `"ulusal-egemenlik-ve-cocuk-bayrami"`.
3. İstisna sözlüğü boş; idempotens: `normalize_holiday_key(normalize_holiday_key(x)) ==
   normalize_holiday_key(x)`.

- [ ] **Step 1 (RED):** `test_day_suffix_stripped` (arife + "N. Gün" parametrize),
  `test_turkish_slugify_long_official_names`, `test_idempotent_on_own_output` → FAIL.
- [ ] **Step 2 (GREEN):** Fonksiyonu yaz; `.venv/bin/pytest tests/regression/test_holiday_keys.py -q` → PASS.
- [ ] **Step 3:** Commit: `feat(social-backend): normalize_holiday_key single source (K1)`

### Task 15: `SectorPackageContentV1` Pydantic modeli (§3.3)

**Files:**
- Create: `apps/social/backend/app/models/sector_package.py`
- Test: `tests/regression/test_sector_package_model.py` (DB'siz)

**Interfaces:**
- Produces: `SectorPackageContentV1` (alanlar §3.3 JSON şeması birebir: `kapsam`, `ton_ve_dil`,
  `cta_kaliplari[{kalip,tur,gerekce}]`, `kanca_kaliplari[str]`, `gorsel_kodlar`,
  `video_kodlar{hareket[str], sahne[str]}`, `takvim_temalari[str]`,
  `yasaklar_ve_hassasiyetler[str]`, `ozel_gun{slug→{tur,mesaj_ekseni,kanca[],cta[],gorsel_vurgu}}`);
  `DecisionLogEntry` (`alan,kalip,karar[koru|guncelle|cikar|ekle|kirp],gerekce,kanit`);
  `SCHEMA_VERSION = 1`; toplam tavan sabiti `MAX_CONTENT_CHARS = 6000`.
- Consumes: `normalize_holiday_key` (T14) — `ozel_gun` anahtar idempotens validator'ı.

**Bağlayıcı doğrulama kuralları:** `ozel_gun` her anahtar için
`normalize_holiday_key(anahtar) == anahtar` değilse ValidationError; `ozel_gun[*].tur ∈
{kutlama, anma, ticari-firsat, karma}`; content bütünü (JSON serileştirilmiş) > 6000 karakter
ise ValidationError (alan-başı hedef doğrulanmaz — yalnız toplam + yapı).

- [ ] **Step 1 (RED):** `test_valid_content_accepted` (geçerli örnek content),
  `test_non_normalized_ozel_gun_key_rejected`, `test_invalid_tur_rejected`,
  `test_total_char_cap_rejected`, `test_decision_log_entry_schema` → FAIL.
- [ ] **Step 2 (GREEN):** Modeli yaz; koş → PASS.
- [ ] **Step 3:** Commit: `feat(social-backend): sector package content schema v1 (Pydantic)`

### Task 16: `import_sector_package.py` — tek public draft+artefakt kapısı (§3.3/§11)

**Files:**
- Create: `apps/social/backend/scripts/import_sector_package.py`
- Test: `tests/db/test_package_pipeline.py`

**Interfaces:**
- Produces: CLI — `python scripts/import_sector_package.py --sector-slug X --run-id Y
  --content-json path.json [--decision-log path.json] [--artifacts-dir <MUTLAK-yol>/research-runs/Y]
  [--source-map DOSYA=ARAÇ ...] [--brief-ref "brief.md@<git-hash|tarih>"] [--database-url ...]`
  (artifacts-dir MUTLAK verilir — artefaktlar repo DIŞI, cwd-göreli çözüm yanlış yere gider; F28).
  Davranış: (1) varsa artifacts-dir'deki `KAYNAK-*.md` / `denetci-*-raporu.md` /
  `birlesik-taslak.md` dosyalarını kind eşlemesiyle (`research`/`review`/`synthesis`)
  `sector_research_artifacts`'a ekler; (2) content'i `SectorPackageContentV1`'den geçirir;
  (3) `version = mevcut max+1` ile `status='draft'` paket satırı insert eder. Çekirdek mantık
  test-çağrılabilir fonksiyonda:
  `import_draft(conn, *, sector_slug, run_id, content_dict, decision_log, ...) -> UUID`.
- **`--source-map` sözleşmesi (spec §3.1: `source` gerçek araç adı taşır, körlük DB yazımında
  biter):** tekrarlanabilir `--source-map <dosya-kökü>=<araç>`; artifacts-dir'de MEVCUT her
  `KAYNAK-N.md` için zorunlu eşleme (`gemini|claude|chatgpt`), her `denetci-N-raporu.md` için
  zorunlu eşleme (`claude-code|codex`); `birlesik-taslak.md` → `kind='synthesis'`,
  `source='claude-code'` SABİT (eşleme istemez, verilirse hata). Bilinmeyen dosya-kökü / mevcut
  dosyaya eksik eşleme / kind'e izinsiz araç değeri → hata, HİÇBİR satır yazılmaz (all-or-nothing
  tek transaction).
- Consumes: T15 modeli, T7-T10 şeması.

- [ ] **Step 1 (RED):** `test_import_draft_happy_path` (draft satırı + artifacts satırları oluşur;
  source değerleri source-map'ten), `test_import_invalid_ozel_gun_key_rejected` (başarı kriteri
  4'ün script yarısı), `test_import_over_cap_rejected`, `test_import_unknown_sector_slug_fails`,
  `test_import_root_sector_slug_fails` (subtype kilidi script'ten de tetiklenir),
  `test_import_missing_source_map_rejected` (mevcut KAYNAK dosyasına eşleme yok → hata, hiçbir
  satır yazılmaz), `test_import_invalid_source_value_rejected` (kind'e izinsiz araç değeri) → FAIL.
- [ ] **Step 2 (GREEN):** Script'i yaz; koş → PASS.
- [ ] **Step 3:** Commit: `feat(social-backend): import_sector_package draft gate script`

### Task 17: Tek kapı — `load_sector_package_context` + preview kuralları (§6.1)

**Files:**
- Create: `apps/social/backend/app/core/sector_package_context.py`
- Test: `tests/db/test_package_pipeline.py`

**Interfaces:**
- Produces: `SectorPackageContext` (pydantic/dataclass: `package_id: UUID`, `version: int`,
  `sector_slug: str`, `content: SectorPackageContentV1`);
  `async load_sector_package_context(db, brand: dict, preview_package_id: UUID | None = None)
  -> SectorPackageContext | None` — üretim isteği başına TEK sorgu
  (`brands.sub_sector_id` → aktif paket JOIN `sectors.slug`).
- Consumes: T15 modeli.

**Bağlayıcı preview invariantları (§6.1 a/b/c):** (a) parametre yalnız iç çağrıdan gelir —
kullanıcı route şemalarında alan YOK (D5, T24'te bağlanır); (b) parametresiz davranış birebir
normal yol (draft DB'de dururken None); (c) preview paketi yalnız
`sector_packages.sector_id == brand.sub_sector_id` ise yüklenir; eşleşmezse VEYA
`sub_sector_id` boşsa `ValueError` (yükleme yok — yanlış-sektör önizleme + yanlış K7 damgası
fiziksel kapalı). Preview draft VE active paketi yükleyebilir; content her yüklemede
Pydantic'ten geçer.

- [ ] **Step 1 (RED):** Testler:
  - `test_load_returns_none_without_sub_sector` (sub_sector_id NULL → None)
  - `test_load_returns_none_with_sub_sector_but_no_active_package` (draft DB'de dururken —
    başarı kriteri 5'in DB yarısı / draft izolasyonu)
  - `test_load_returns_context_with_active_package` (alan doğrulukları: version/slug/content)
  - `test_preview_loads_draft_when_sector_matches`
  - `test_preview_rejects_sector_mismatch`, `test_preview_rejects_unassigned_brand` (§6.1-c)
  → FAIL.
- [ ] **Step 2 (GREEN):** Modülü yaz; koş → PASS.
- [ ] **Step 3:** Commit: `feat(social-backend): sector package single-gate context loader`

### Task 18: Tüketici API — dört blok üretici (§6.3/§6.4/§7/§8)

**Files:**
- Modify: `apps/social/backend/app/core/sector_package_context.py`
- Test: `tests/regression/test_package_blocks.py` (DB'siz — sabit `SectorPackageContext`
  fixture'ıyla) + `tests/regression/golden/` paketli blok golden'ları

**Interfaces:**
- Produces: `tier2_block(ctx) -> str`; `special_day_block(ctx, holiday_name_tr: str) -> str | None`;
  `visual_language_line(ctx, *, style: Literal["caption", "director"], holiday_name_tr: str | None = None) -> str`
  (TEK imza — T21 `style="caption"`, T22 `style="director"` [+ opsiyonel holiday] bu imzayı
  tüketir); `motion_pool(ctx) -> list[str]`;
  conftest'e `FROZEN_PACKAGE_CONTENT` + `FROZEN_CTX` eklenir (Faz 2 yüzey testleri paylaşır).

**Bağlayıcı şablonlar:**
- `tier2_block`: §6.3 şablonu BİREBİR — başlık `--- SEKTÖR PAKETİ ({sector_slug}, sürüm
  {version}) ---`, ardından KOD SABİTİ kullanım talimatı (4 madde: en fazla 2-3 öğe; emin
  değilsen kullanma; ürün/marka gerçeğiyle çelişeni kullanma; bilinmeyen kanal/hizmet önerme),
  ardından alan satırları (`Kapsam/Ton ve dil/CTA kalıpları [kalip (tur): gerekce]/Kanca
  kalıpları/Takvim temaları/Yasaklar ve hassasiyetler`). `gorsel_kodlar`/`video_kodlar`/
  `ozel_gun` bu bloğa GİRMEZ.
- `special_day_block`: `normalize_holiday_key(holiday_name_tr)` ile `content.ozel_gun` lookup;
  YOKSA `None` + `logger.info` (sessiz düşme görünür — spec §7); VARSA §7 K3 şablonu birebir
  (başlık `--- SEKTÖR PAKETİ DÖNEM KALIPLARI ({dönem adı}) ---`; kullanım satırı; `Tür:`;
  kutlama/anma ise SATIŞ ÇAĞRISI YASAK + kategori-ton-üstünlüğü cümlesi; anma ise ek mizah/
  promosyon kapalı cümlesi; mesaj ekseni/kanca/cta satırları).
- `visual_language_line`: caption varyantı (`style="caption"`) `SEKTÖR GÖRSEL DİLİ (bu
  dağarcıktan içeriğe uyanı seç, listeyi tamamlama): {gorsel_kodlar}`; director varyantı
  (`style="director"`) `Sector visual language: {gorsel_kodlar}` (+ `holiday_name_tr` verilmiş
  ve eşleşmişse `{gorsel_vurgu}` aynı satır ailesinde) — Produces'taki TEK imza.
- `motion_pool`: `ctx.content.video_kodlar.hareket` listesi döner (K2-a; seçim mekaniği
  değişmez — `random.choice` çağıran taraf).

- [ ] **Step 1 (RED):** `test_tier2_block_golden_exact` (yeni golden
  `p_tier2_block__paketli.txt`), `test_special_day_block_golden_exact`
  (`p_specialday_block__paketli.txt`; kutlama-tür fixture), `test_special_day_block_none_plus_log_on_miss`
  (caplog ile), `test_special_day_anma_variant_contains_ban_lines`,
  `test_visual_line_caption_variant`, `test_visual_line_director_variant_with_holiday`,
  `test_motion_pool_returns_package_hareket_list` → FAIL (fonksiyonlar yok).
- [ ] **Step 2 (GREEN — implementasyon ÖNCE):** Dört fonksiyonu yaz; golden'lı testler hâlâ
  FAIL (golden dosyaları yok), golden'sız testler PASS.
- [ ] **Step 3 (capture — üretim API'sinden):** capture_golden'a paketli blok üreticilerini ekle
  + koş (yeni golden'lar GERÇEK fonksiyonlardan üretilir — geçici/ad-hoc koddan golden YASAK).
- [ ] **Step 4 (PASS):** `.venv/bin/pytest tests/regression/ -q` → tümü PASS (paketsiz
  golden'lar DEĞİŞMEDEN).
- [ ] **Step 5:** Commit: `feat(social-backend): package block builders (tier2, special-day, visual, motion)`

### Task 19: Yüzey #1 — Caption Tier 2 (`build_brand_context` paket dalı)

**Files:**
- Modify: `apps/social/backend/app/core/prompt_builder.py:185-254` (`build_brand_context`)
- Modify: `apps/social/backend/app/core/caption_generator.py:85-110` (`generate_captions`
  imzasına `package_ctx` parametresi + `:110` çağrısına geçirme — `build_brand_context`'in
  TEK çağıranı burası, doğrulandı 2026-07-12)
- Modify: `apps/social/backend/app/routers/posts.py:189-269` (`generate_caption` route'u —
  ctx'in yüklendiği yer: `db` burada; istek başına TEK `load_sector_package_context` çağrısı)
- Test: `tests/regression/test_k6_surfaces.py`

**Interfaces:**
- Produces: `build_brand_context(brand, brand_kit, template, package_ctx: SectorPackageContext | None = None) -> str`
  — `package_ctx` doluysa SECTOR_GUIDANCE dalı YERİNE `tier2_block(package_ctx)`;
  `None` iken çıktı BYTE-EXACT bugünkü. `generate_captions(..., package_ctx: SectorPackageContext | None = None)`
  — route'tan tek taşıma parametresi (T21 yüzeyleri de AYNI parametreden türetir; ikinci
  yükleme noktası açılmaz).
- **generate_caption response sözleşmesi (K7 echo-token'ın kaynağı — T23):** response'a
  `sector_package_id: str | null` eklenir (caption'ı üreten ctx'in id'si; paketsizde null).
  Üretim anı BU istektir — post kaydı ayrı istekte açıldığından damga bu değerden taşınır
  (T23 sözleşmesi). Üretici-taraf davranışının testleri T23 entegrasyon dosyasındadır
  (`test_generate_caption_returns_*` — tüketici matrisi tek başına yeterli kanıt DEĞİL).
- Consumes: T17 loader, T18 `tier2_block`.

- [ ] **Step 1 (RED):** `test_s1_tier2_paketli_contains_block_and_no_sector_guidance`
  (paketli fixture: `--- SEKTÖR PAKETİ` var VE `--- SEKTÖR REHBERİ` YOK — yerine-geçme kanıtı
  (b)) → FAIL.
- [ ] **Step 2 (GREEN):** Dalı yaz + çağrı yollarına ctx threading (caption akışında TEK yükleme,
  istek başına — §6.1). Koş: `.venv/bin/pytest tests/regression/ -q` → tümü PASS
  (**s1 paketsiz golden değişmeden** — İSPAT).
- [ ] **Step 3:** Commit: `feat(social-backend): surface #1 tier-2 package block injection`

### Task 20: Yüzey #4 — suggest-ideas paket dalı

**Files:**
- Modify: `apps/social/backend/app/core/prompt_builder.py` (`build_suggest_ideas_brand_context`),
  `apps/social/backend/app/routers/ai.py` (suggest-ideas akışında ctx yükleme)
- Test: `tests/regression/test_k6_surfaces.py`

**Interfaces:**
- Produces: `build_suggest_ideas_brand_context(brand, brand_kit, template, package_ctx=None) -> str`
  (T3 imzasına parametre; doluysa SECTOR_GUIDANCE dalı yerine `tier2_block`).

- [ ] **Step 1 (RED):** `test_s4_suggest_ideas_paketli_block_no_guidance` → FAIL.
- [ ] **Step 2 (GREEN):** Dal + ai.py ctx yükleme; K6 → tümü PASS (s4 paketsiz golden değişmeden).
- [ ] **Step 3:** Commit: `feat(social-backend): surface #4 suggest-ideas package injection`

### Task 21: Yüzey #2 + #3 — caption görsel kural satırı + özel gün paket bloğu

**Files:**
- Modify: `apps/social/backend/app/core/caption_generator.py` (`_build_output_format_instruction`
  ~353-359 bloğuna koşullu `SEKTÖR GÖRSEL DİLİ` satırı) ve
  `apps/social/backend/app/core/prompt_builder.py` (`build_dynamic_content` 327-344 ÖZEL GÜN
  bloğuna koşullu paket dönem-kalıpları ekleme)
- Test: `tests/regression/test_k6_surfaces.py`

**Interfaces:**
- Produces: `_build_output_format_instruction(..., sector_visual_line: str | None = None)`
  (satır, image_prompt KATİ KURALLAR bloğuna eklenir);
  `build_dynamic_content(..., package_special_day_block: str | None = None)` — doluysa mevcut
  ÖZEL GÜN BAĞLAMI bloğunun İÇİNE/ardına dönem kalıpları (K3: kategori ton satırı BASILMAYA
  DEVAM eder, paket kısıtı blokta açıkça üstün — metin `special_day_block`'tan gelir).
  Çağıran taraf = `generate_captions` (caption_generator.py:85 — T19'da eklenen `package_ctx`
  parametresinden satır/bloğu T18 üreticileriyle kurar); bu iki fonksiyon ctx'e DEĞİL hazır
  string'e bağlanır (tek kapı ilkesi: yüzeyler yalnız tüketici API çıktısı taşır).

- [ ] **Step 1 (RED):** `test_s2_output_format_paketli_contains_visual_line`,
  `test_s3_dynamic_paketli_contains_period_block_and_tone_hint_still_present` (K3: hem
  `_SPECIAL_DAY_TONE_HINTS` satırı hem paket kısıtı — birlikte) → FAIL.
- [ ] **Step 2 (GREEN):** İki parametre + threading; K6 → tümü PASS (s2/s3 paketsiz golden
  değişmeden — `None` default'lar byte-exact korur).
- [ ] **Step 3:** Commit: `feat(social-backend): surfaces #2 #3 visual line + special-day package block`

### Task 22: Yüzey #5/#6/#7 — director satırı + motion havuzu

**Files:**
- Modify: `apps/social/backend/app/services/short_video.py` (`build_director_prompt`
  imzasına `sector_visual_line: str | None = None`; `_pick_motion_prompt(pool: list[str] | None = None)`;
  pipeline'da ctx yükleme + threading)
- Test: `tests/regression/test_k6_surfaces.py`

**Bağlayıcı davranış:** `sector_visual_line` doluysa İKİ modda da Industry satırının yanına
eklenir (§6.4 director varyantı). `_pick_motion_prompt(pool=None)` → `random.choice(pool or
_MOTION_PROMPTS)`; paketli markada pipeline `motion_pool(ctx)` geçirir, paketsizde
`_MOTION_PROMPTS` BYTE-EXACT aynen (K2-a; K6 karşılaştırması havuz düzeyi).

- [ ] **Step 1 (RED):** `test_s5_director_t2i_paketli_contains_sector_line`,
  `test_s6_director_edit_paketli_contains_sector_line`,
  `test_s5_s6_director_special_day_includes_gorsel_vurgu` (özel-gün eşleşmişse `gorsel_vurgu`
  director satırında — spec §6.4; F22),
  `test_s7_motion_pool_packaged_uses_package_list`,
  `test_s7_motion_prompts_constant_unchanged` (havuz sabiti golden'la eq — paketsiz yol) → FAIL.
- **Özel-gün threading (F22→F26, ZORUNLU):** video + özel-gün kombinasyonu UI'da MEVCUT
  (icerik-olustur `effectiveContentType === 'video'` yolu — 2026-07-12 Codex-doğrulu) →
  `special_day_name`/`special_day_category` stage1 payload'ında ZORUNLU taşınır (alanlar
  `ShortVideoGenerate` şemasında ZATEN mevcut; frontend video dalına T29'da eklenir) →
  pipeline `visual_language_line(ctx, style="director", holiday_name_tr=...)` çağrısına ulaşır.
- [ ] **Step 2 (GREEN):** Parametreler + pipeline threading; K6 → tümü PASS (s5/s6/s7 paketsiz
  golden değişmeden).
- [ ] **Step 3:** Commit: `feat(social-backend): surfaces #5-#7 director line + motion pool`

### Task 23: K7 damga persist (üretim yollarında `posts.sector_package_id`)

**Files:**
- Modify: `apps/social/backend/app/routers/posts.py` — `generate_post` (:276, INSERT :392) ve
  `create_post` (:546, INSERT :556; görev başında akış doğrulanır — LLM üretim bağlamı
  taşımıyorsa ctx de damga da YOK, task notuna yazılır),
  `apps/social/backend/app/services/short_video.py` — pipeline INSERT'leri (:665, :944)
- Test: kapsam doğrulama grep'i + tests/db (trigger etkileşimi zaten T10'da)

**Bağlayıcı kural (§10.4) — damga SEMANTİĞİ (F24 kalibrasyonu):** damga, **üretim isteği
anında markada yürürlükte olan paket sürümünün** kaydıdır (version-governance). İçerik-bütünlüğü
İDDİASI TAŞIMAZ ve taşıyamazdı: caption, CaptionEditor ile serbestçe düzenlenebilir (ürün
özelliği) — "bu metni kesin bu paket üretti" garantisini hiçbir damga tasarımı veremez; spec
§3.2-b'nin mutlaklığı PAKET tarafındadır (damganın işaret ettiği paket İÇERİĞİ donmuş ve daima
denetlenebilir). Eşitlik kuralının verdiği garanti: **yanlış-sürüm / yabancı-sektör / draft
damgası fiziksel imkânsız** + üretim-anı paketi == insert-anı paketi.
**Echo + eşitlik-reddi sözleşmesi** (kripto-token'sız):
ctx'in tüketildiği İLK istek (caption-first'te `generate_caption`) response'unda
`sector_package_id` döner (T19); post kaydını açan istek (`PostGenerate` şemasına opsiyonel
`sector_package_id: UUID | null`) bu değeri GERİ taşır; server INSERT anında ctx'i KENDİSİ
yükler ve **yalnız eşitlikte** persist eder:
- echo null ∧ ctx None → damga NULL (bugünkü paketsiz yol, birebir);
- echo null ∧ ctx VAR → **409** (bayat istemci — "sayfayı yenile / caption'ı yeniden üret");
- echo dolu ∧ ctx None → **422** (paketsiz markaya echo);
- echo dolu ∧ echo ≠ ctx.package_id → **409** "paket sürümü değişti — caption'ı yeniden üret"
  (eski sürüm, yabancı sektör, uydurma id: HEPSİ bu dala düşer — kabul edilen tek değer
  sunucunun kendi güncel gerçeği olduğundan **yanlış-sürüm damgası** fiziksel imkânsız);
- echo dolu ∧ echo == ctx.package_id → damga = o id (üretim-anı ve insert-anı paketi AYNI —
  yalan damga penceresi kapalı).
**Matris kapsamı (content-type ayrımı — F14) ve TEK YÜRÜTME NOKTASI (F21):** 5-dal matris
YALNIZ paket-bağlamı tüketen üretimden türeyen isteklere uygulanır (caption-first zinciri:
image/carousel/special_day + kısa-video stage1). **Yapısal kural:** matris, `generate_post` /
stage1 route'larının GİRİŞİNDE, content_type dallanmasından ÖNCE TEK noktada uygulanır (quote
muafiyeti o noktadaki content_type kontrolü) — tip-başına dalda ayrı enforcement YAZILMAZ,
tip-başına bypass yapısal olarak imkânsız. **Quote ctx TÜKETMEZ** (caption-first'ten geçmez,
§6.2 tablosunda değil) → matris-DIŞI: echo alanı yok sayılır, damga NULL (paketli markada
quote üretimi etkilenmez). Content-type kapsam listesi T23 kapsam adımındaki akış haritasıyla
doğrulanır; quote'un ctx tükettiği çıkarsa caption-first zincirine bağlanır (muafiyet düşer).
**Dürüst etki:** aktivasyon sonrası eski caption'la post açmak 409'a düşer → kullanıcı caption'ı
yeniden üretir (küçük kota maliyeti; aktivasyon ~3 ayda bir — kabul edilen sürtünme; yeni
sürümün içeriği yeni pakete damgalanır, K7 doğruluğu mutlak kalır). Tek-istek akışlar (preview
internal ucu) doğrudan ctx.package_id yazar (eşitlik kuralı gerekmez).
**Kısa-video stage-split — PUBLIC alan bağlaması (F11):** `ShortVideoGenerate` (stage1 request
şeması, `app/models/schemas.py`; execute'ta ad birebir doğrulanır) opsiyonel
`sector_package_id: UUID | null` alır; stage1 route'u ÜRETİME GİRMEDEN yukarıdaki 5-dal
eşitlik-reddi matrisini AYNEN uygular; damga, post satırını YARATAN istekte yazılır (kota
Stage 1'de düştüğünden satır beklenen olarak stage1'de açılır — akış haritası T22 kapsam
adımında doğrulanır, satır stage2'de açılıyorsa damga-yazımı oraya kayar ve echo stage2
payload'ında da taşınır); stage2 aynı post satırı üzerinden ilerlediği sürece yeni echo
GEREKMEZ (damga satırda). Frontend taşıma: T29 (captionData → stage1 payload).
**Kapsam-DIŞI (2026-07-12 doğrulu — ctx yüklemeyen yollar):** `internal.py:165` (autoposting
trigger — yalnız fal image, `build_brand_context` çağırmıyor), `avatar.py:160`, `trends.py:353`,
legacy #8.

- [ ] **Step 1 (kapsam):** `grep -rn "load_sector_package_context" app/` ×
  `grep -rn "INSERT INTO social.posts" app/` kesişimini yukarıdaki listeye karşı DOĞRULA
  (yeni kesişim çıkarsa task notuna ekle); her kesişim noktasına damga threading ekle.
- [ ] **Step 2 (RED — K7 entegrasyon testleri, D8):** `tests/db/test_k7_stamp_integration.py`
  yaz — mekanizma: throwaway test DB'sine workspace/brand/paket fixture satırları; FastAPI
  dependency override (`get_current_user`, `get_db`) + dış-servis sınırlarında monkeypatch
  (`generate_captions` sabit dict, fal `generate_image`/video sabit job-id, storage/TTS no-op);
  gerçek route/pipeline kodu uçtan koşar, dış çağrı YOK. Testler:
  - `test_generate_caption_returns_sector_package_id_for_active_package` (ÜRETİCİ taraf:
    caption yanıtı paketli markada alanı DÖNDÜRÜR — F16; alan yoksa paketli üretim 409'da
    kilitlenirdi)
  - `test_generate_caption_returns_null_without_package` (paketsiz markada alan null)
  - `test_generate_post_stamps_on_echo_equality` (echo == güncel aktif → damga yazılır)
  - `test_caption_first_race_rejected_409` (v1 aktifken caption [echo=v1] → v2 aktive edilir →
    generate_post → **409**, damga YAZILMAZ — yalan-damga penceresi kapalı; F4+F8 kanıtı)
  - `test_generate_post_rejects_forged_or_foreign_echo_409` (yabancı sektör paketi + uydurma
    UUID parametrize → 409)
  - `test_generate_post_rejects_echo_for_packageless_brand_422` (sub_sector boş + echo dolu)
  - `test_generate_post_rejects_stale_client_409` (aktif paket varken echo null)
  - `test_generate_post_leaves_null_without_package` (echo null + paketsiz marka → kolon NULL)
  - `test_quote_generation_unaffected_by_package` (paketli marka + quote, echo YOK → 200,
    damga NULL — matris quote'a uygulanmaz; F14 muafiyet kanıtı)
  - `test_stamp_persists_across_content_types` (image/carousel/special_day parametrize —
    echo-eşitlikli üretimde damga her tipte yazılır; F21 tip-kapsam kanıtı)
  - `test_short_video_pipeline_writes_stamp` + `test_short_video_packageless_null`
  - `test_short_video_stage1_race_rejected_409` (v1 caption [echo=v1] → v2 aktive →
    stage1(echo=v1) → **409**, üretim başlamaz, damga yazılmaz)
  - `test_create_post_stamp_scope_matches_task_note` (create_post ctx taşımıyorsa NULL kanıtı)
  Koş: `.venv/bin/pytest tests/db/test_k7_stamp_integration.py -q -m db` → **FAIL**.
- [ ] **Step 3 (GREEN):** Damga threading'i tamamla; koş → PASS. K6 → tümü PASS; tests/db →
  tümü PASS. (Faz 4 pilotu kriter-4 CANLI teyidi olarak kalır — birincil kanıt bu testlerdir.)
- [ ] **Step 4:** Commit: `feat(social-backend): K7 package version stamp on generation inserts`

### Task 24: Preview üretim ucu (operatör-iç yol — D5)

**Files:**
- Modify: `apps/social/backend/app/routers/internal.py` (yeni uç), `app/models/schemas.py`
  (request şeması), üretim pipeline imzaları (`preview_package_id` threading)
- Test: `tests/db/test_package_pipeline.py`

**Interfaces:**
- Produces: `POST /internal/posts/generate-preview` (X-Internal-Key korumalı) — body **gerçek
  üretim şemalarını saran ince zarf** (F27 — spec §10.3 "draft, GERÇEK üretim yolunda
  değerlendirilir" şartının API karşılığı):
  `{package_id: UUID, mode: "image" | "short_video", payload: PostGenerate | ShortVideoGenerate}`
  — `payload` üretim ucunun request gövdesiyle AYNI tip (template_fields/platforms/special_day/
  product/voice vb. TÜM üretim girdileri taşınabilir; preview'a özel ayrı daraltılmış şema
  YAZILMAZ); davranış: normal üretim pipeline'ını `preview_package_id=package_id` ile çağırır
  (payload'daki echo alanı preview'da yok sayılır — tek-istek yol); dönen post draft-damgalıdır
  (yayın kilidi T10 gereği yayın-dışı).
- **Scheduler ön-filtresi (spec §3.4 "Scheduler sorgusuna ek ön-filtre plan detayı" —
  defense-in-depth; asıl kilit DB'de):** `internal.py` `get_scheduled_due_posts` (:200-227)
  sorgusuna koşul eklenir: `sector_package_id IS NULL` VEYA işaret edilen paket `active` —
  draft-damgalı scheduled post n8n publisher'a HİÇ verilmez (trigger reddi gürültüsü yerine
  kaynakta filtre; `shared/n8n-workflows/` tarafına dokunulmaz). **Görünürlük (F13 bağlantısı):**
  ön-filtrenin DIŞLADIĞI due-post sayısı/id'leri `logger.info` ile loglanır — non-active
  damgalı kuyruk sessizce kaybolmaz (aktivasyon ön-kontrolü T34'te; bu log ikinci gözdür).
- **Yapısal invariant (§6.1-a):** kullanıcı route'larının (posts.py, ai.py) request şemalarına
  preview alanı EKLENMEZ — yalnız internal uç + pipeline iç parametresi.

- [ ] **Step 1 (RED):** `test_preview_endpoint_requires_internal_key` (401/403 without key),
  `test_user_generate_schemas_have_no_preview_field` (schemas.py modellerinde
  `preview_package_id` alanı YOK — yapısal assert),
  `test_preview_endpoint_generates_draft_stamped_post` (T23 mock altyapısıyla: uç draft paketle
  üretir, dönen post `sector_package_id == draft id` — auth-shape'ten öte davranış kanıtı),
  `test_preview_forwards_production_fields` (payload zarfı template_fields/special_day_name/
  product_id [image] ve voice/special_day_name [short_video] alanlarını pipeline'a AYNEN
  iletir — F27 temsiliyet kanıtı),
  `test_scheduled_due_excludes_draft_stamped` (draft-damgalı scheduled post listede YOK),
  `test_scheduled_due_includes_active_stamped_and_null` (aktif-damgalı + damgasız girer) → FAIL.
- [ ] **Step 2 (GREEN):** Uç + threading + scheduled-due ön-filtresi; koş → PASS.
- [ ] **Step 3:** Commit: `feat(social-backend): internal-only preview generation endpoint`

### Task 25: Faz 2 kapanışı — RELEASE GATE checkpoint [MANUEL ADIM İÇERİR]

- [ ] **Step 1:** Tam koşum: `.venv/bin/pytest tests/regression/ -q` (paketsiz golden'lar Faz 0
  baseline'ıyla BYTE-EXACT — `git diff --stat tests/regression/golden/` BOŞ) +
  `.venv/bin/pytest tests/db/ -q -m db` → tümü PASS. **K7 entegrasyon testleri (T23 Step 2,
  `test_k7_stamp_integration.py`) PASS olmadan deploy YOK — release-gate'in makine-kanıtı budur.**
- [ ] **Step 2:** Draft-izolasyon kanıtı (başarı kriteri 5): `test_load_returns_none_...` (T17)
  + paketsiz golden seti = draft DB'de dururken hiçbir yüzey değişmedi — kanıt zinciri commit
  mesajına yazılır.
- [ ] **Step 3 [MANUEL — Eray onayı]:** Faz 2 deploy TEK ARTIM (yüzeyler + damga + preview ucu
  birlikte — release gate). Paket/atama henüz yok → canlı davranış değişmez (kolon NULL yolu).
- [ ] **Step 4:** Commit: `test(social-backend): phase-2 closure — K6 full pass + draft isolation`

---

# FAZ 3 — Atama Akışı (LLM önerir, kullanıcı teyit eder — §5)

### Task 26: `GET /sectors/sub-sectors` amaca özel uç

**Files:**
- Modify: `apps/social/backend/app/routers/sectors.py`
- Test: `tests/db/test_taxonomy_guards.py`

**Interfaces:**
- Produces: `GET /sectors/sub-sectors?active_package=true` → `[{id, slug, display_name,
  parent_sector_id}]`; `active_package=true` → yalnız aktif paketi olan alt-sektörler;
  parametresiz → tüm alt-sektörler. Cache'siz (aktif paket değişimi aktivasyonla — TTL cache
  eski aday listesi gösterir; D1 sınıfı riski baştan kapat). Route sırası: statik path — mevcut
  router'da dinamik path yok, yine de `""` route'undan ÖNCE deklare edilir (konvansiyon).
- **Invariant (§4 koruma-1):** kök liste ucu `GET /sectors` SAF kalır — bu uç ayrı.
- **Aday politikası bilinçli aktif-paket-only (spec §5):** kullanıcı UI'ının aday listesi
  yalnız aktif paketli alt-sektörleri gösterir. Draft dönemindeki pilot/elle atama bu uçtan
  GEÇMEZ — operatör scriptiyle yapılır (T33 `assign_sub_sector.py`; spec §5 "Mevcut 2 marka
  elle atanır" hükmünün mekanizması). UI, draft görünürlüğü için genişletilmez.

- [ ] **Step 1 (RED):** `test_sub_sectors_endpoint_filters_by_active_package` (aktif paketli
  alt-sektör döner, paketsiz alt-sektör dönmez), `test_sub_sectors_endpoint_excludes_roots` → FAIL.
- [ ] **Step 2 (GREEN):** Uç; koş → PASS. K6 → tümü PASS.
- [ ] **Step 3:** Commit: `feat(social-backend): sub-sectors purpose endpoint (active_package filter)`

### Task 27: analyze-website `sub_sector` + suggest-sub-sector kardeş ucu

**Files:**
- Modify: `apps/social/backend/app/routers/ai.py:26-89` (analyze-website) + yeni uç
- Test: `tests/regression/test_sub_sector_validation.py` (saf doğrulama) +
  `tests/db/test_taxonomy_guards.py` (aday sorgusu)

**Interfaces:**
- Produces:
  - analyze-website response'una opsiyonel `sub_sector: str | null` (slug); prompt'a aday
    listesi gömülür (aday sorgu: aktif paketi olan alt-sektörler — T26 ile aynı SQL yardımcı
    fonksiyonda paylaşılır: `async fetch_assignable_sub_sectors(db) -> list[dict]`).
  - `build_analyze_website_prompt(site_text: str, candidates: list[str]) -> tuple[str, str]`
    — (system, user) saf inşa fonksiyonu; **aday listesi BOŞKEN çıktı bugünkü prompt'la
    BYTE-EŞİT** (K6-dışı bilinçli değişikliğin geçiş güvencesi: aktif paket yokken — Faz 3
    deploy anı — canlı analyze-website davranışı birebir korunur).
  - `validate_sub_sector_suggestion(suggestion: str | None, candidates: list[str]) -> str | None`
    — saf fonksiyon: aday listesinde yoksa `None` (halüsinasyon kapısı — server-side).
  - `POST /ai/suggest-sub-sector` — body `{brand_id}`; kök sektör + marka adı/açıklamasından
    aynı aday-liste + aynı doğrulama ile öneri (web-sitesiz akış, D10).
- **Invariant (§5):** içerik üretim akışına SORU EKLENMEZ — bu uçlar yalnız onboarding/ayarlar.

- [ ] **Step 1 (RED):** `test_validate_sub_sector_in_candidates_passes`,
  `test_validate_sub_sector_not_in_candidates_nulled`,
  `test_validate_sub_sector_none_passthrough`,
  `test_analyze_website_prompt_byte_equal_today_when_no_candidates` (beklenen string testte
  sabit — bugünkü ai.py:52-64 metinleri birebir),
  `test_analyze_website_prompt_embeds_candidates_when_present`,
  `test_fetch_assignable_sub_sectors_only_active_package` → FAIL.
- [ ] **Step 2 (GREEN):** Yardımcılar + iki uç (analyze-website'a `db` dependency eklenir; LLM
  dönüşü doğrulamadan geçirilir); koş → PASS. K6 → tümü PASS (analyze-website K6 yüzeyi DEĞİL —
  §6.2 tablosunda yok; golden eklenmez).
- [ ] **Step 3:** Commit: `feat(social-backend): sub-sector suggestion (analyze-website + sibling endpoint)`

### Task 28: brands create/update `sub_sector_id` + app-level 422

**Files:**
- Modify: `apps/social/backend/app/routers/brands.py` (create :32-45, update :107-113, GET
  :66-68 JOIN'ine sub_sector alanları), `app/models/schemas.py`
- Test: `tests/db/test_taxonomy_guards.py`

**Interfaces:**
- Produces: brand create/update body'sinde opsiyonel `sub_sector_id: UUID | null`; app-level
  doğrulama: işaret edilen satır kök (parent NULL) ise **422** (DB kilidi T8 zaten fiziksel
  koruyor — bu katman UX geri bildirimi); GET brand response'unda `sub_sector_id` +
  `sub_sector_slug` (LEFT JOIN).
- **Invariant:** `brands.sector` TEXT + `sector_id` yazım yolu (resolve_sector dual-write)
  DEĞİŞMEZ.

- [ ] **Step 1 (RED):** `test_brand_update_sub_sector_root_returns_422`,
  `test_brand_update_sub_sector_valid_persists`, `test_brand_get_includes_sub_sector_fields`,
  `test_brand_update_sub_sector_null_clears` → FAIL.
- [ ] **Step 2 (GREEN):** Alan + doğrulama + JOIN; koş → PASS. K6 → tümü PASS.
- [ ] **Step 3:** Commit: `feat(social-backend): brand sub_sector_id assignment with 422 guard`

### Task 29: Frontend — API client + tip eklentileri

**Files:**
- Create: `apps/social/frontend/lib/api/sectors.ts` (repo per-domain API modül deseni —
  `lib/api/` altında products/templates kardeşleri gibi)
- Modify: brand create/update payload tipinin yaşadığı yer (`lib/api.ts` brand fonksiyonları)
- Modify: `apps/social/frontend/components/templates/CaptionEditor.tsx` — `CaptionData`
  tipine `sector_package_id?: string | null` alanı; **tüm onChange/spread yolları alanı
  KORUR** (F17 — kaybolan alan = aktivasyon sonrası 409 kilidi)
- Modify: `apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx` —
  handleGenerateCaption response→captionData + iki üretim payload'ına taşıma (aşağıdaki not)
- Create: `apps/social/frontend/scripts/check-k7-echo.mjs` — **statik K7-echo sözleşme
  kontrolü** (F19+F21+F26; bağımlılıksız node scripti): şu **5 görünüm noktasını** obje-literal
  düzeyinde doğrular (yalnız dosyada kelime-varlığı DEĞİL — ilgili `setCaptionData(...)` ve
  payload obje-literal'lerinin alanı içerdiği parse edilir; içermeyen nokta → exit 1):
  (1) `CaptionEditor.tsx` CaptionData'da `sector_package_id`, (2) icerik-olustur'da caption
  response→captionData eşlemesinde, (3) `/posts/generate` payload inşasında, (4)
  `/posts/generate-short-video-stage1` payload inşasında `sector_package_id`, (5) AYNI stage1
  payload'ında `special_day_name` + `special_day_category` (video özel-gün taşıması — T22). **Dürüst kalıntı:** statik
  yapı kontrolüdür (çalışan-davranış testi değil — repo'da frontend test runner'ı yok, kurmak
  bu planda YAGNI); editor-onChange korunum davranışı ve uçtan-uca taşıma KANITLANMAMIŞ kalır,
  canlı teyit Faz 4 aktivasyon-sonrası ilk gerçek üretimde (T35). **Operatör kararı
  (2026-07-12, Turn-10 DUR raporu):** bu kalıntı tradeoff olarak AÇIKÇA kabul edildi —
  frontend davranışsal test altyapısı kurulmayacak; gerekçe: aktivasyon yalnız Faz 4 pilotta,
  ilk üretimler operatörün elinde, alan kaybı anında görünür 409 üretir.

**Not:** analyze-website çağrıları bugün sayfa bileşenlerinde inline
(`app/(onboarding)/onboarding/page.tsx`, `app/(dashboard)/marka-ayarlari/page.tsx` —
2026-07-12 doğrulu); dönüş tipindeki `sub_sector` kullanımı T30/T31'de o sayfalarda işlenir.

**Interfaces:**
- Produces: `getSubSectors(activePackage?: boolean)` (T26 ucu), `suggestSubSector(brandId)`
  (T27 ucu) — `lib/api/sectors.ts`; brand payload'ında `sub_sector_id?: string | null`.
- **K7 echo taşıma (T23 sözleşmesinin frontend ayağı):**
  `apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx` — generate_caption
  response'undaki `sector_package_id` caption state'ine (captionData tipi) alınır ve İKİ üretim
  çağrısına da AYNEN geçirilir: (a) generate_post payload'ı (görsel/carousel), (b)
  `/posts/generate-short-video-stage1` payload'ı (kısa video — T23 stage-split bağlaması).
  Pass-through; frontend değer üretmez/yorumlamaz. Video dalında `special_day_name`/
  `special_day_category` stage1 payload'ına ZORUNLU eklenir (F26 — T22 threading'inin frontend
  ayağı; check-k7-echo.mjs bu iki alanı stage1 payload'ında 5. görünüm noktası olarak doğrular).
  **Sıra kısıtı:** bu threading Faz 4
  aktivasyonundan ÖNCE canlıda olmalı (Faz 3 deploy'u bunu karşılar; arada aktif paket yok →
  race penceresi zaten kapalı).

- [ ] **Step 1:** Client fonksiyonları + tipler + icerik-olustur echo pass-through +
  check-k7-echo.mjs; doğrula: `npm run build` hatasız **VE** `node scripts/check-k7-echo.mjs`
  → exit 0 (**5 görünüm noktası** mevcut — stage1 `special_day_name`/`special_day_category`
  çifti dahil).
- [ ] **Step 2:** Commit: `feat(social-frontend): sub-sector API client + K7 echo pass-through`

### Task 30: Frontend — onboarding teyit bileşeni

**Files:**
- Modify: `apps/social/frontend/app/(onboarding)/onboarding/page.tsx` (sektör alanı civarı —
  spec çıpası :129)

**Bağlayıcı UX (§5):** analyze-website dönüşünde `sub_sector` doluysa alt-sektör açılır listesi
**önceden seçili** gösterilir; kullanıcı değiştirir veya boşaltır ("Alt-sektör yok" seçeneği);
aday listesi `getSubSectors(true)`'dan; boş aday listesinde bileşen HİÇ render edilmez.
Kayıtta `sub_sector_id` payload'a girer.

- [ ] **Step 1:** Bileşen + akış; doğrula: `npm run build` hatasız.
- [ ] **Step 2 [MANUEL]:** UI smoke (dev server): web siteli akışta öneri önceden seçili; boşaltma
  çalışıyor; alt-sektörsüz kayıt bugünkü gibi.
- [ ] **Step 3:** Commit: `feat(social-frontend): onboarding sub-sector confirm dropdown`

### Task 31: Frontend — markalar + marka-ayarları teyit bileşeni

**Files:**
- Modify: `apps/social/frontend/app/(dashboard)/markalar/page.tsx` (yeni marka akışı — çıpa :56),
  `apps/social/frontend/app/(dashboard)/marka-ayarlari/page.tsx` (ayar formu — çıpa :434)

**Bağlayıcı UX:** T30 ile aynı bileşen deseni (paylaşılan küçük bileşen `SubSectorSelect` —
frontend components dizininde); marka-ayarlarında mevcut `sub_sector_id` gösterilir +
`suggestSubSector` ile öneri butonu (web-sitesiz marka akışı).

- [ ] **Step 1:** İki sayfa + paylaşılan bileşen; `npm run build` hatasız.
- [ ] **Step 2 [MANUEL]:** UI smoke: ayarlar sayfası mevcut atamayı gösteriyor + aday listesi
  aktif-paketli sektörlerle sınırlı (draft döneminde boş dropdown = doğru davranış; pilot
  ataması T33 scriptiyle — UI değil).
- [ ] **Step 3:** Commit: `feat(social-frontend): brand pages sub-sector assignment`
- [ ] **Step 4 [MANUEL — Eray onayı]:** Faz 3 deploy (backend + frontend).

---

# FAZ 4 — Kuyumculuk Pilotu (elle resmî tur — çoğunluk MANUEL)

### Task 32: Hakem-sentez görev dosyası v1.2 → v1.3 (EK-K girdisi) [REPO-DIŞI]

**Files:**
- Modify: `/root/otomaix-sosyal-medya-arastirmasi/hakem-sentez-gorevi.md` (repo DIŞI — git
  commit'i YOK)

**Bağlayıcı değişiklik (spec §11):** girdi listesine **EK-K = markanın kök sektörünün
SECTOR_GUIDANCE metni** eklenir (yerine-geçme nüans-kaybı önlemi: damıtma kök rehberi girdi
alır); sürüm damgası v1.2 → v1.3. EK-J tanımı zaten `public_holidays` güncel `name_tr`+`category`
dökümü — değişmez, kontrol edilir.

- [ ] **Step 1:** Dosyayı güncelle; doğrula: dosyada `v1.3` + `EK-K` geçiyor; EK-K açıklaması
  normalize/anahtar sözleşmesiyle (T14) tutarlı.
- [ ] **Step 2:** Bu planın HANDOFF/rapor notuna "v1.3 işlendi (repo-dışı)" satırı düş.

### Task 33: Alt-sektör satırı + pilot marka ataması (operatör script yolu)

**Files:**
- Create: `apps/social/backend/scripts/add_sub_sector.py`,
  `apps/social/backend/scripts/assign_sub_sector.py`
- Test: `tests/db/test_taxonomy_guards.py`

**Interfaces:**
- Produces: CLI `python scripts/add_sub_sector.py --slug kuyumculuk --display-name Kuyumculuk
  --parent-slug e-ticaret-perakende [--keywords ...] [--database-url ...]`; **idempotens =
  durum-doğrulamalı** (F15): insert `ON CONFLICT (slug) DO NOTHING` sonrası satır FETCH edilir
  ve istenen kontratla karşılaştırılır — mevcut satırın `parent_sector_id`si istenen parent'a
  eşit değilse (kök satır dahil) veya display_name uyuşmuyorsa **yüksek sesle HATA** (sessiz
  "başarılı" yok); kök-parent doğrulaması (parent kendisi alt-sektörse hata).
- Produces: CLI `python scripts/assign_sub_sector.py --brand-id <UUID> --sub-sector-slug
  kuyumculuk [--clear] [--database-url ...]` — marka→alt-sektör operatör ataması; **draft
  döneminde UI aday listesi bilinçli boş olduğundan pilot ataması BU scriptle yapılır**
  (T26 notu; DB subtype kilidi kök-slug'ı zaten fiziksel reddeder, script net hata mesajı verir).

- [ ] **Step 1 (RED):** `test_add_sub_sector_creates_child_row`,
  `test_add_sub_sector_idempotent_same_state`,
  `test_add_sub_sector_fails_on_existing_slug_wrong_parent`,
  `test_add_sub_sector_fails_on_existing_root_slug`,
  `test_add_sub_sector_rejects_child_parent`,
  `test_assign_script_sets_brand_sub_sector`, `test_assign_script_rejects_root_slug`,
  `test_assign_script_clear_nulls_column` → FAIL.
- [ ] **Step 2 (GREEN):** İki script; koş → PASS. Commit:
  `feat(social-backend): sub-sector add/assign operator scripts`
- [ ] **Step 3 [MANUEL — Eray onayı]:** Canlıda koş (kuyumculuk satırı) → doğrula:
  `GET /sectors` hâlâ yalnız kök döner (koruma-1 canlı kanıtı); resolver "Kuyumculuk" markasını
  kök kovada tutuyor (koruma-2).
- [ ] **Step 4 [MANUEL]:** Pilot markasına atama `assign_sub_sector.py` ile (§10.3 ön şartı —
  preview sektör-eşleşme kilidi için zorunlu; UI ataması aktivasyon SONRASI doğal akış olarak
  T31'de zaten mevcut).

### Task 34: Aktivasyon/rollback operatör aracı

**Files:**
- Create: `apps/social/backend/scripts/activate_sector_package.py`
- Test: `tests/db/test_package_pipeline.py`

**Interfaces:**
- Produces: CLI — `activate <package_id>` (tek transaction: varsa mevcut aktif → `archived`,
  hedef → `active`; §3.2 sırası) ve `rollback --sector-slug X --to-version N` (aynı mekanik,
  hedef arşivli sürüm). Provenance/durum-makinesi ihlallerinde DB hatası kullanıcıya net mesajla
  yansıtılır (trigger'lar asıl kilit — script UX katmanı, D7).
- **Aktivasyon ön-kontrolü (kuyruk + in-flight koruması — F13/F18):** `activate`/`rollback`,
  arşivlenecek paket(ler)e damgalı şu post'ları archive'dan ÖNCE sorgular:
  **BLOK kümesi** = `generating`/`awaiting_approval`/`ready`/`scheduled` **+ `publishing`**
  (in-flight yayın: tamamlanması beklenir — retry/`failed→publishing` yolları arşiv sonrası
  kilitleneceğinden sürüm değişimi yayın ortasında yapılmaz); **RAPOR-ama-bloklamaz** =
  `partially_published` (içerik zaten kullanıcı-görünür; kalan-platform retry'ının arşiv
  sonrası kilitleneceği raporda açıkça yazılır). Varsa DEFAULT davranış BLOK + liste raporu;
  `--force` ile bilinçli devam (stdout'a audit satırı; kalan post'lar yayın kilidine takılır ve
  T24 ön-filtresi onları n8n'e vermez — ön-filtre dışladıklarını `logger.info` ile LOGLAR,
  sessiz kaybolma yok [T24'e bağlanır]). Yayın kilidi DB kontratı DEĞİŞMEZ (spec §3.4 mutlak
  kalır) — pencere operatör kararına bağlanır. **Atomiklik (F23):** ön-kontrol + archive +
  activate TEK transaction'da koşar ve blok-sorgusu commit'ten HEMEN ÖNCE bir kez daha
  koşulur — arada yeni eşleşen satır çıktıysa transaction ABORT (yeniden dene raporuyla).
  **Belgeli kalıntı:** READ COMMITTED altında mikro-pencere teorik olarak kalır; güvence ağı
  çift katman (yayın kilidi + T24 log'lu ön-filtre) — kayıp sessiz olamaz.

- [ ] **Step 1 (RED):** `test_activate_script_archives_current_then_activates`,
  `test_activate_script_fails_without_synthesis`,
  `test_rollback_script_restores_target_version_single_active`,
  `test_activate_blocks_when_queued_posts_reference_previous_active`,
  `test_activate_blocks_when_publishing_posts_reference_previous_active`,
  `test_activate_reports_partially_published_without_blocking`,
  `test_activate_aborts_if_queued_post_appears_before_commit` (ikinci bağlantıdan pre-check
  sonrası schedule insert → commit-öncesi yeniden-kontrol ABORT eder; F23),
  `test_activate_force_proceeds_and_reports_queued` → FAIL.
- [ ] **Step 2 (GREEN):** Script; koş → PASS.
- [ ] **Step 3:** Commit: `feat(social-backend): package activation/rollback operator script`

### Task 35: Resmî kuyumculuk turu — koreografi + Katman-2 kör değerlendirme [MANUEL]

**Files:**
- Create: yok (koşu artefaktları repo-DIŞI: `research-runs/<run_id>/`)

**Koreografi (spec §11 B-süreci birebir — her adım kanıt bırakır):**
- [ ] **A [MANUEL]:** 3 bağımsız Deep Research → `research-runs/kuyumculuk-2026q3/KAYNAK-1/2/3.md`
  (kör adlandırma dosya adında; araç eşlemesi YALNIZ operatörde).
- [ ] **0 [MANUEL]:** brief-doctor mekanik kontrol → `brief-doctor-raporu.md` (EK-E).
- [ ] **1/1' [MANUEL]:** Denetçi-1 (Claude Code) + Denetçi-2 (Codex) bağımsız/kör →
  `denetci-1/2-raporu.md`; Denetçi-2 web erişimi İLK koşuda doğrulanır (yoksa raporda belirtir).
- [ ] **2-3 [MANUEL]:** Sentez (v1.3 görev dosyasıyla — EK-H/I/J/K girdileri) →
  `birlesik-taslak.md` + draft JSON + decision_log + açık sorular + onay özeti (İLK bölüm:
  çıkarılanlar listesi — evrimsel model).
- [ ] **Import:** `python scripts/import_sector_package.py --sector-slug kuyumculuk --run-id
  kuyumculuk-2026q3 --content-json birlesik-taslak-content.json --decision-log decision-log.json
  --artifacts-dir /root/otomaix-sosyal-medya-arastirmasi/research-runs/kuyumculuk-2026q3
  (MUTLAK yol — artefaktlar repo DIŞI, cwd-göreli yol backend altında yanlış yere çözülür; F28)
  --source-map KAYNAK-1=gemini --source-map
  KAYNAK-2=claude --source-map KAYNAK-3=chatgpt --source-map denetci-1=claude-code --source-map
  denetci-2=codex` (eşlemeler ŞABLON — gerçek araç eşlemesi operatörün elindeki kör kayda göre;
  `birlesik-taslak.md` otomatik synthesis/claude-code) → draft + 3 research + 2 review + 1
  synthesis satırı (başarı kriteri 4 artefakt kümesi).
- [ ] **Preview üretimleri:** `POST /internal/posts/generate-preview` ile içerik tipi başına 3-5
  çift (paketli draft ↔ paketsiz aynı ürün sınıfı; kısa video 1-2 çift — maliyet sınırlı);
  eşleştirme `posts.sector_package_id` (draft id) üzerinden.
- [ ] **Katman-2 [MANUEL — Eray]:** kör değerlendirme — "hangisi kuyumcu postu?" ayrımı
  gözlenebilir mi; sonuç aktivasyon onayının girdisi (§10.3).
- [ ] **Aktivasyon [MANUEL — Eray onayı]:** `python scripts/activate_sector_package.py activate
  <draft_id>` → önizlenen draft aktifleşir; önceki preview post'ları yayınlanabilir hale gelir
  (T10 `test_publish_after_activation_ok` canlı karşılığı).
- [ ] **Kanıt toplama (başarı kriterleri 3/4/5):** paketli post `sector_package_id` dolu;
  paketsiz post NULL; yanlış-sektör/atamasız preview REDDİ canlıda bir kez denenir (hata
  beklenir); sonuçlar bu planın kapanış raporuna yazılır.

### Task 36: Bakım kapanışı — takvim + dokümantasyon [MANUEL ADIM İÇERİR]

- [ ] **Step 1 [MANUEL — K1 operatör kararı]:** Takvime 10 Kasım (anma), 24 Kasım Öğretmenler
  Günü, okula dönüş dönemi: `social.public_holidays` 2026 kayıtları INSERT + n8n "Türkiye
  Takvimi" yıllık cron'una (ID `tTk1VroTh4AS8lxI`) kalıcı işleme. Paket anahtar sözleşmesi buna
  BAĞIMLI DEĞİL (eşleşmeyen dönem sessiz+log düşer) — bakım maddesi bloklamaz.
- [ ] **Step 2:** Final tam koşum: `.venv/bin/pytest tests/regression/ -q` + `.venv/bin/pytest
  tests/db/ -q -m db` → tümü PASS; `git diff --stat tests/regression/golden/` → paketsiz
  golden'larda Faz 0'dan bu yana SIFIR değişiklik (başarı kriteri 7 kanıtı).
- [ ] **Step 3:** Commit: `docs(social-backend): sector package rollout closure notes`

---

## Deploy / Rollback Stratejisi (özet)

| Artım | İçerik | Sıra | Geri dönüş |
|---|---|---|---|
| Faz 1 | migration 032 (additive) + filtreler + cache bump | migration → kod deploy | kod: Coolify önceki imaj; DB: forward-only (additive, veri yazımı yok) |
| Faz 2 | yüzeyler + damga + preview ucu (TEK artım — release gate) | Faz 1 canlıda olmalı | kod rollback yeterli (paket/atama yokken davranış zaten nötr — K6 kanıtı) |
| Faz 3 | atama uçları + frontend (K7 echo pass-through dahil) | Faz 2 sonrası | kod rollback; `sub_sector_id` dolu kalabilir (ctx yüklemesi aktif paket ister — zararsız) |
| Faz 4 | veri (alt-sektör satırı, draft, aktivasyon) | Faz 3 canlıda (echo threading DAHİL — aktivasyon öncesi şart) + filtreler doğrulanmış | paket rollback = `archived→active` durum geçişi (T34); acil durumda markanın `sub_sector_id`i NULL'lanır (anında paketsiz yol) |

## Riskler ve İzleme

1. **001→031 boş DB'ye uygulanamazsa** (T6 ampirik): fallback D2 devreye girer — conftest
   docstring'ine gerekçe, plana targeted-fix işlenir.
2. **Golden kırılganlığı:** SECTOR_GUIDANCE/şablon metni bilinçli değişirse golden ritüeli
   (capture + ayrı commit + gerekçe) — sessiz güncelleme YASAK (Global Constraints).
3. **Cache bump atlanırsa:** 1 saate kadar eski liste/harita — D1 task'ları key bump'ı filtreyle
   AYNI commit'te zorlar.
4. **Trigger yanlış-gevşek:** T7-T10 testleri spec §15-1 listesinin BİREBİR karşılığı; eksik
   test = eksik kanıt sayılır (consistency sweep kontrol eder).
5. **Preview sızıntısı:** T24 yapısal assert (`schemas.py`'de alan yok) + T17-b draft-izolasyon
   testi + K6 draft-fixture kanıtı — üç katman.

## Kapsam Dışı (spec §13 birebir — evleriyle)

Marka-DNA sistemi (kendi spec seansı); marka kanal envanteri (DNA G1); komut ailesi mekanizması
(`docs/plans/<tarih>-sektor-paket-komut-ailesi.md` — runtime + ilk elle tur SONRASI); platform
kazıma / pgvector örnek havuzu / C süreci / etkileşim kanıt döngüsü / paket satışı / trend
zenginleştirme (Faz 2 listesi); legacy kısa-video düzeltmesi; Yılbaşı kategori düzeltmesi.

## Self-Review Kaydı (writing-plans şablon gereği)

- **Spec kapsama:** §3→T7-T10/T15-T16; §4→T11-T12+T33; §5→T26-T31; §6→T17-T22+T24; §7→T14+T18/T21;
  §8→T22; §9→T1; §10→T5/T25/T35 (K6) + T23 (K7); §11→T16/T32/T35; §12 kararları→ilgili task'lara
  gömülü (K1→T14/T36, K2→T22, K3→T18/T21, K6→T5, K7→T23); §14 sırası→faz yapısı; §15→test
  listeleri (kriter madde-madde T7-T10/T12/T17/T24/T35); §16→T13-4 + dokunulmazlar Global
  Constraints'te.
- **Placeholder taraması:** "TBD/TODO/implement later" yok; tüm path'ler tam; imzalar açık.
- **Tip/imza tutarlılığı:** `SectorPackageContext` (T17) tüketicileri T18-T24'te aynı adla;
  `build_suggest_ideas_brand_context` T3→T20 aynı imza ailesi; golden adları T5↔T18-T22 tutarlı.
- **B-hafif kontrolü:** kanıtlanmamış hard-gate arkası detay-planlanmadı — komut ailesi bilinçli
  ayrı planda; Faz 4 yalnız koreografi/checklist (üretim kalitesine bağlı kırılgan otomasyon yok).
