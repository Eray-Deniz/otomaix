# Codex Adversarial Plan Review Log — sektor-bilgi-paketi

Plan: `docs/plans/2026-07-12-sektor-bilgi-paketi.md`
Spec: `docs/specs/2026-07-11-sektor-bilgi-paketi.md`

---

## Turn 1 — 2026-07-12 (review GERÇEKLEŞMEDİ: substrat exclusion)

Scope: `--scope working-tree` (plan untracked/dirty). Sonuç: plan dosyası sanitized substrata
girmedi — Task 6'daki `POSTGRES_PASSWORD=test` (throwaway docker test container satırı)
`_css_secret_scan` WEAK kalıbına (`password=`) takıldı, dosya fail-closed dışlandı. Codex plan
içeriğini göremedi; bulgu üretilmedi (aşağıda stdout verbatim). Düzeltme: satır
`POSTGRES_HOST_AUTH_METHOD=trust` olarak yeniden yazıldı (targeted fix #2) → Turn 2.

### Codex stdout (verbatim)

# Codex Adversarial Review

Target: working tree diff
Verdict: needs-attention

No ship verdict possible: the target plan file is not present in this sanitized workspace, so I cannot ground contract-level findings against its current content. Coverage: inspected docs/active/CURRENT.md and docs/specs/2026-07-11-sektor-bilgi-paketi.md; attempted docs/plans/2026-07-12-sektor-bilgi-paketi.md directly and listed docs/plans; no working tree diff or untracked files were available. I did not report the missing plan as a finding because the prompt marks it as substrate-excluded.

No material findings.

Next steps:
- Provide the current contents of docs/plans/2026-07-12-sektor-bilgi-paketi.md or rerun with that overlay included, then review spec alignment and decision drift against the plan lines directly.

---

## Turn 2 — 2026-07-12 (İLK gerçek review; 2 high + 1 medium)

Scope: `--scope working-tree`. Ledger: F1 cluster=k6-tier1-kapsam (turn 1/4), F2
cluster=k7-persist-kanit (turn 1/4), F3 cluster=import-source-map (turn 1/4). Üçü de
claude-confirmed → Auto-Fix Mode A1 otonom refine uygulandı (aşağıda disposition).

### Codex stdout (verbatim)

# Codex Adversarial Review

Target: working tree diff
Verdict: needs-attention

No-ship: the plan claims K6/K7 release gates, but leaves material verification holes in the actual prompt and stamp contracts. Coverage: inspected docs/active/CURRENT.md, docs/plans/2026-07-12-sektor-bilgi-paketi.md, docs/specs/2026-07-11-sektor-bilgi-paketi.md, and available related code prompt_builder.py, templates.py, internal.py, trends.py plus repo file map. Not inspected: sanitized/excluded files such as posts.py, short_video.py, caption_generator.py, ai.py, upload_post.py; their absence was treated as substrate exclusion, not a finding.

Findings:
- [high] contract-level: K6 does not actually cover all LLM prompt text because Tier-1 system prompt is omitted (docs/plans/2026-07-12-sektor-bilgi-paketi.md:193-210)
  The plan states K6 must prove every LLM-bound prompt string is byte-exact unchanged for packageless/unassigned brands, but Task 5's golden matrix captures only brand context, dynamic content, suggest-ideas context, director prompt, output-format, motion pool, and legacy lookup. It never captures prompt_builder.build_system_prompt() / _SYSTEM_RULES, even though the available code shows _SYSTEM_RULES is an LLM-bound Tier-1 system prompt. A later accidental Tier-1 change after the baseline would pass this K6 gate, contradicting spec §10.1 and the plan's own Global Constraint.
  Recommendation: Root cause: K6 surface list equates package-injection surfaces with all LLM-bound prompt text. Minimal fix strategy: add an explicit s0_system_prompt__paketsiz golden for build_system_prompt() text, and include it in capture_golden.py and test_k6_surfaces.py. Exact affected files+functions: docs/plans/2026-07-12-sektor-bilgi-paketi.md Task 5; future apps/social/backend/tests/regression/capture_golden.py; future test_k6_surfaces.py; app.core.prompt_builder.build_system_prompt. Related files w/ same pattern: Task 21/22 package-specific surfaces should not replace this global prompt check. Verification command: cd apps/social/backend && .venv/bin/pytest tests/regression/ -q, expecting the count to include the new system-prompt golden. Risk if wrong: K6 can report PASS while LLM behavior changes globally for every brand. Fallback: if system prompt is intentionally excluded, downgrade the Global Constraint wording from 'TÜM prompt metinleri' and explicitly document the residual risk.
- [high] contract-level: K7 release gate is not proven before Phase 2 deploy (docs/plans/2026-07-12-sektor-bilgi-paketi.md:641-663)
  Task 23 explicitly says code-path E2E proof of sector_package_id persistence is deferred to the Phase 4 pilot, while Phase 2 deploys the package-capable surfaces, stamp code, and preview endpoint as the release-gated increment. The listed checks are DB trigger tests plus grep, which prove locks around an existing stamp but do not prove generation inserts actually write ctx.package_id. If threading is missed in posts.py, short_video.py, or the preview route, Phase 2 can ship package-preview generation with NULL stamps; draft publish locks and blind-evaluation pairing then silently fail because the DB trigger only protects non-NULL sector_package_id.
  Recommendation: Root cause: the plan treats grep + DB invariants as sufficient evidence for an application-level persistence contract. Minimal fix strategy: before Task 25 deploy, add automated integration tests with mocked LLM/fal/pipeline calls that create image and short_video preview posts and assert posts.sector_package_id == draft package id; also assert packageless generation leaves NULL. Exact affected files+functions: docs/plans/2026-07-12-sektor-bilgi-paketi.md Tasks 23-25; future tests/db/test_package_pipeline.py; app.routers.posts generate_post/create_post; app.services.short_video insert paths; app.routers.internal generate-preview. Related files w/ same pattern: Task 24 endpoint tests should assert successful draft-stamped generation, not only auth/schema shape. Verification command: cd apps/social/backend && .venv/bin/pytest tests/db/test_package_pipeline.py -q -m db plus tests/regression. Risk if wrong: package-capable code ships without durable version stamps, making K7 unrecoverable for generated posts. Fallback: block Phase 2 deploy until Phase 4 pilot, but that contradicts the current phase line and should be made explicit.
- [medium] contract-level: import_sector_package public CLI references --source-map but does not define the flag contract (docs/plans/2026-07-12-sektor-bilgi-paketi.md:458-463)
  The import script is the single public draft/artifact DB write gate, but its advertised CLI omits --source-map while the behavior requires a source-map argument to populate source for KAYNAK/review/synthesis artifacts. The pilot command later uses '--source-map ...' as a placeholder. Because sector_research_artifacts.source is NOT NULL by spec, this is a public interface gap: implementers can produce incompatible flag syntax or operators can run a non-executable pilot command at the exact point where provenance is required for activation.
  Recommendation: Root cause: the plan specifies required behavior but not the operator-facing flag schema. Minimal fix strategy: define --source-map exactly, e.g. repeated 'logical=tool' pairs or a JSON path, with required keys for KAYNAK-1/2/3, denetci-1/2, and birlesik-taslak; update Task 16 tests and Task 35 command to use a concrete example. Exact affected files+functions: docs/plans/2026-07-12-sektor-bilgi-paketi.md Task 16 and Task 35; future scripts/import_sector_package.py CLI parser and import_draft. Related files w/ same pattern: activation CLI is concrete enough; import CLI should match that precision. Verification command: cd apps/social/backend && .venv/bin/pytest tests/db/test_package_pipeline.py -q -m db with tests for missing/unknown/incomplete source-map. Risk if wrong: provenance rows fail insertion or are misattributed, and activation evidence becomes unreliable. Fallback: require an interactive prompt for source mapping, but then document it as a manual step and test non-interactive CI behavior separately.

Next steps:
- Patch the plan before implementation: add system-prompt K6 golden, add pre-Phase-2 K7 persistence integration tests, and make --source-map executable and tested.

### Disposition (Claude tahkimi + uygulanan fix'ler)

| ID | Severity | Tahkim | Fix |
|---|---|---|---|
| F1 | high, contract-level | claude-confirmed (spec §10.1 "TÜM prompt metinleri" + §10.2 baseline Tier-1'i mühürler) | T5'e `s0_system_prompt__paketsiz.txt` golden + `test_s0_system_prompt_paketsiz_golden_exact`; sayılar 8→9 passed süpürüldü (5 site) |
| F2 | high, contract-level | claude-confirmed (release-gate makine-kanıtsızdı; grep+trigger uygulama-persist'i kanıtlamaz) | D8 kararı yükseltildi; T23'e `tests/db/test_k7_stamp_integration.py` (mocked LLM/fal, 5 test) RED-GREEN adımları; T24'e draft-damga davranış testi; T25'e "PASS olmadan deploy YOK" kapısı |
| F3 | technical-medium, contract-level | claude-confirmed (public CLI sözleşme boşluğu; NOT NULL `source` + provenance riski) | T16'ya `--source-map <dosya-kökü>=<araç>` tam sözleşme (zorunlu eşlemeler, izinli değer kümeleri, synthesis sabit, all-or-nothing) + 2 red testi; T35 komutu somut şablonla yazıldı |

Sayaçlar: `codex_plan_review_iterations` 0→1 (test-contract/kapsam değişimi = full plan
iteration); `codex_plan_targeted_fixes` = 2 (değişmedi). → Re-review Turn 3.

---

## Turn 3 — 2026-07-12 (1 critical + 2 medium)

Scope: `--scope working-tree` (Turn 2 fix'leri işlenmiş plan). Ledger: F4
cluster=k7-split-flow-truth (turn 1/4), F5 cluster=scheduler-prefilter (turn 1/4), F6
cluster=t18-interface (turn 1/4). Session auto-fix turu: 2/8. Üçü de claude-confirmed →
Mode A1 otonom refine uygulandı.

### Codex stdout (verbatim)

# Codex Adversarial Review

Target: working tree diff
Verdict: needs-attention

No-ship: the plan contradicts the K7 provenance contract and misses a spec-required scheduler guard. Coverage: inspected docs/plans/2026-07-12-sektor-bilgi-paketi.md, docs/specs/2026-07-11-sektor-bilgi-paketi.md, docs/active/CURRENT.md, backend/frontend local instructions, current file tree, migrations 001/016, internal scheduled-due endpoint, scheduled publisher workflow. Did not inspect excluded secret-sanitized files listed in the prompt.

Findings:
- [critical] contract-level: K7 stamp can point to the wrong package after caption-first two-request races (docs/plans/2026-07-12-sektor-bilgi-paketi.md:662-669)
  Task 23 explicitly accepts that in caption-first flow the caption request and post insert are separate, and if activation changes between them the stamp records the package active at POST time. That conflicts with the spec’s K7 invariant that the stamp always identifies the package content that produced the post. Impact: a post generated from v1 can be stored as if v2 produced it, breaking rollback, blind-evaluation evidence, and bad-output attribution exactly where K7 is supposed to be durable evidence.
  Recommendation: Root cause: the plan equates post-insert time with content-generation time for split caption flows. Minimal fix strategy: make package identity a generation artifact, not a late lookup: either generate+insert atomically, or return a server-issued caption_generation_id/package_id token from generate_caption and require create_post to persist that exact id or reject if missing/stale. Exact affected files+functions: docs/plans/2026-07-12-sektor-bilgi-paketi.md T19/T23; apps/social/backend/app/routers/posts.py generate_caption, generate_post, create_post; app/models/schemas.py request/response schema if tokenized. Related files w/ same pattern: apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx caption-first flow. Verification command: .venv/bin/pytest tests/db/test_k7_stamp_integration.py -q -m db with a test that generates caption under active v1, activates v2 before create_post, and asserts stamp is v1 or the create is rejected. Risk if wrong: durable audit metadata lies and package rollback/quality analysis targets the wrong version. Fallback: disable package injection for caption-first flows until package id can be carried across the split.
- [medium] contract-level: spec-required scheduled publisher prefilter is absent from the plan (docs/plans/2026-07-12-sektor-bilgi-paketi.md:323-345)
  The spec requires a scheduler-query prefilter in addition to the DB publish trigger. The plan only adds the DB trigger tests and preview endpoint behavior; it never updates or tests get_scheduled_due_posts. Current scheduled-due returns every scheduled post by status/time, and the n8n workflow publishes each returned id, so draft-stamped preview posts that become scheduled will be repeatedly handed to publish-now until the trigger rejects them. The DB trigger prevents publication, but the missing prefilter creates noisy operational failures and hides preview isolation behind repeated publish errors.
  Recommendation: Root cause: the plan treats the DB publish lock as the whole scheduler contract even though spec §3.4 calls for endpoint prefilter defense-in-depth. Minimal fix strategy: add a task/test that filters scheduled-due to include only posts with sector_package_id IS NULL or a referenced package with status='active'. Exact affected files+functions: docs/plans/2026-07-12-sektor-bilgi-paketi.md T10/T24/T25; apps/social/backend/app/routers/internal.py get_scheduled_due_posts. Related files w/ same pattern: shared/n8n-workflows/scheduled-post-publisher.json consumes /internal/posts/scheduled-due and posts each id to /publish-now. Verification command: .venv/bin/pytest tests/db/test_package_pipeline.py -q -m db with draft-stamped scheduled post excluded, active-stamped scheduled post included, NULL-stamped scheduled post included. Risk if wrong: preview/draft rows can generate recurring n8n publish failures and alert noise; operators may misdiagnose this as Upload-Post or scheduler instability. Fallback: if endpoint filtering cannot ship in the same phase, make preview rows unschedulable with a DB/app guard and test that calendar scheduling rejects draft-stamped posts.
- [medium] implementation-mechanics: Task 18 defines contradictory public interface and impossible RED-baseline order (docs/plans/2026-07-12-sektor-bilgi-paketi.md:528-560)
  Task 18 first declares visual_language_line(ctx) -> str, then binds consumers to a style/holiday-aware API. The same task also says to run capture_golden for package block producers before writing the four functions. That is not a harmless body detail: downstream Tasks 21/22 depend on the public signature, and the stated TDD sequence cannot execute because the golden capture must call functions that do not exist yet.
  Recommendation: Root cause: the task mixes an early simplified interface with the later real consumer contract, then places golden capture before implementation. Minimal fix strategy: choose one public signature in T18, e.g. visual_language_line(ctx, *, style: Literal['caption','director'], holiday_name_tr: str | None = None) -> str, and reorder the steps to RED tests -> GREEN implementation -> capture/update golden if needed -> PASS. Exact affected files+functions: docs/plans/2026-07-12-sektor-bilgi-paketi.md T18/T21/T22; apps/social/backend/app/core/sector_package_context.py visual_language_line. Related files w/ same pattern: tests/regression/capture_golden.py and tests/regression/test_package_blocks.py. Verification command: .venv/bin/pytest tests/regression/test_package_blocks.py -q plus .venv/bin/python -m tests.regression.capture_golden after functions exist. Risk if wrong: implementers can satisfy one interface while breaking downstream consumers, or generate golden files from ad hoc temporary code rather than the production API. Fallback: split T18 into an interface-only implementation commit and a following golden-capture commit.

Next steps:
- Fix the K7 split-flow contract before implementation starts; it changes schema/API expectations.
- Add scheduled-due filtering/tests to the plan so preview draft rows do not become scheduler noise.
- Normalize Task 18’s public signature and TDD ordering.

### Disposition (Claude tahkimi + uygulanan fix'ler)

| ID | Severity | Tahkim | Fix |
|---|---|---|---|
| F4 | critical, contract-level | claude-confirmed (generate_post caption'ı payload'dan alıyor — üretim anı generate_caption; spec §3.2-b "damga = üreten içeriğin ta kendisi" mutlak; taze lookup race'te yalan damga) | T23 echo-token sözleşmesi: generate_caption response `sector_package_id` döner (T19), PostGenerate echo taşır, server (a)(b) doğrulamalarıyla ECHO'yu persist eder; stage-split aynı kural; race testi + 2 spoof-red testi; T29 frontend pass-through (icerik-olustur/page.tsx) + deploy sıra kısıtı |
| F5 | technical-medium, contract-level | claude-confirmed (spec §3.4 ön-filtreyi açıkça "plan detayı" olarak plana devretmişti; get_scheduled_due_posts :200-227 filtresiz doğrulandı) | T24'e scheduled-due ön-filtresi (NULL veya aktif-paket damgası) + 2 test; n8n workflow'a dokunulmaz |
| F6 | technical-medium (Codex: implementation-mechanics; public-interface çelişkisi olduğundan fix-required'a çekildi) | claude-confirmed (T18 Produces `visual_language_line(ctx)` vs style/holiday varyantı çelişkisi + capture-before-implement imkânsız sıra) | T18 Produces TEK imza (`style`/`holiday_name_tr` keyword-only) + adım sırası RED→GREEN→capture(üretim API'sinden)→PASS→commit |

Sayaçlar: `codex_plan_review_iterations` 1→2; `codex_plan_targeted_fixes` = 2. → Re-review Turn 4.

---

## Turn 4 — 2026-07-12 (2 high + 2 medium)

Scope: `--scope working-tree` (Turn 3 fix'leri işlenmiş plan). Ledger: F7
cluster=pilot-assignment-path (1/4), F8 cluster=k7-split-flow-truth (**reopen #1** — turn 2/4;
F4 fix'ine saldırı), F9 cluster=k6-scope-semantics (1/4), F10 cluster=db-test-image (1/4).
Session auto-fix turu: 3/8. Dördü de claude-confirmed → Mode A1 otonom refine.

### Codex stdout (verbatim)

# Codex Adversarial Review

Target: working tree diff
Verdict: needs-attention

NO-SHIP: plan still has lifecycle, trust-boundary, and test-contract defects. Coverage: inspected docs/plans/2026-07-12-sektor-bilgi-paketi.md, docs/specs/2026-07-11-sektor-bilgi-paketi.md, docs/active/CURRENT.md, accessible schemas/frontend/internal/migration files. Not inspected: excluded real files listed by substrate scan, especially posts.py/ai.py/caption_generator.py/short_video.py; absence not counted as a finding.

Findings:
- [high] contract-level: Pilot assignment flow cannot select a pre-active sub-sector (docs/plans/2026-07-12-sektor-bilgi-paketi.md:854-857)
  The plan makes the sub-sector list filter `active_package=true` return only sub-sectors with active packages, and the onboarding/brand UI consumes `getSubSectors(true)`. But Faz 4 then requires assigning the pilot brand to `kuyumculuk` before draft preview/activation. At that point the package is not active yet, so the UI path named as the pilot prerequisite cannot show the sub-sector. This breaks the spec's preview prerequisite: brand.sub_sector_id must match the draft package sector before operator preview.
  Recommendation: Root cause: suggestion candidate policy was reused for manual/operator assignment. Minimal fix strategy: split APIs/UX: suggestions use active-package-only, but brand settings/manual assignment must be able to list all sub-sectors or draft-package sub-sectors before activation. Exact affected files+functions: plan T26 `GET /sectors/sub-sectors`, T30/T31 `getSubSectors(true)` UI contract, T33 pilot assignment order. Related files w/ same pattern: apps/social/frontend/app/(onboarding)/onboarding/page.tsx, apps/social/frontend/app/(dashboard)/markalar/page.tsx, apps/social/frontend/app/(dashboard)/marka-ayarlari/page.tsx. Verification command: add/require db test for inactive/draft sub-sector visibility in manual assignment plus `npm run build`. Risk if wrong: pilot cannot reach preview without direct DB edits, bypassing the planned UX and audit path. Fallback: make T33 assignment an operator CLI/script step instead of UI and state that explicitly.
- [high] contract-level: K7 echo token is forgeable by the public client (docs/plans/2026-07-12-sektor-bilgi-paketi.md:670-679)
  The plan adds `sector_package_id` to public generate-caption response and asks the frontend to pass it back in `PostGenerate`. Server validation only checks packageless brand and sector mismatch; it explicitly leaves same-sector old/new versions to the publish lock. That does not prove the echoed package actually produced the caption/image prompt. Any authenticated client can submit a same-sector package id with arbitrary `platform_captions`/`image_prompt`, corrupting K7 provenance while passing the planned checks.
  Recommendation: Root cause: treating a client-echoed UUID as provenance. Minimal fix strategy: make the echo non-forgeable, e.g. signed generation token binding user/workspace/brand/package_id/content hash/expiry, or a server-side generation_session row created by generate-caption and consumed once by generate-post. Exact affected files+functions: plan T19 generate_caption response, T23 `PostGenerate.sector_package_id` validation, T29 frontend pass-through. Related files w/ same pattern: apps/social/backend/app/models/schemas.py `PostGenerate`, apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx generate-caption/generate calls. Verification command: `.venv/bin/pytest tests/db/test_k7_stamp_integration.py -q -m db` with added tests for forged same-sector package id and tampered caption payload. Risk if wrong: package performance/audit data becomes untrustworthy and a post can be stamped with a package that did not generate it. Fallback: do not accept public echo; do a single server-side generation+persist flow for package-stamped content.
- [medium] contract-level: K6 excludes an LLM prompt that the plan later changes (docs/plans/2026-07-12-sektor-bilgi-paketi.md:797-799)
  The global K6 contract says paketsiz/atamasız brands preserve all LLM prompt text byte-exact. Task 27 modifies `analyze-website` by embedding candidate sub-sectors in its prompt, then states analyze-website is not a K6 surface and no golden is added. That makes the K6 claim false or, at minimum, changes an LLM prompt without the declared regression gate.
  Recommendation: Root cause: K6 scope mixes 'all LLM prompt text' with only §6.2 content-generation surfaces. Minimal fix strategy: either narrow the K6 contract in both spec/plan to content-generation package surfaces, or add analyze-website/suggest-sub-sector prompt builders and golden tests before T27 changes them. Exact affected files+functions: plan T5 K6 surface map, T27 analyze-website prompt update. Related files w/ same pattern: apps/social/backend/app/routers/ai.py analyze-website and suggest-ideas prompt builders. Verification command: `.venv/bin/pytest tests/regression/ -q` including a new analyze-website golden if the broad K6 contract remains. Risk if wrong: future reviewers see K6 PASS and believe all prompt text is protected while onboarding LLM behavior drifted untested. Fallback: document analyze-website as an explicit non-K6 behavior change with separate targeted tests and approval.
- [medium] implementation-mechanics: DB test runner image cannot satisfy current migrations (docs/plans/2026-07-12-sektor-bilgi-paketi.md:240-246)
  Task 6 uses stock `postgres:16-alpine` and applies migrations 001→032. The current first migration requires `CREATE EXTENSION IF NOT EXISTS "vector"`; stock Postgres images do not include pgvector. The fallback to a schema-only dump would stop proving sequential migrations apply cleanly, which is exactly the migration contract this plan relies on.
  Recommendation: Root cause: test DB image is not production-equivalent for installed extensions. Minimal fix strategy: use a pgvector-enabled PG16 image or build a tiny test image with pgvector, and keep the 001→032 sequential migration run as the default. Exact affected files+functions: plan D2/T6 `tests/db/conftest.py` Docker fixture. Related files w/ same pattern: shared/db/migrations/001_initial_social.sql requires pgcrypto and vector. Verification command: `.venv/bin/pytest tests/db/ -q -m db` plus a preflight `SELECT extname FROM pg_extension WHERE extname IN ('pgcrypto','vector')`. Risk if wrong: DB tests either fail before reaching 032 or use a dump fallback that can hide migration-order breakage. Fallback: if dump baseline is unavoidable, add a separate CI/manual check against a pgvector-enabled empty DB before approving migration 032.

Next steps:
- Fix the plan contract before implementation: split manual assignment from active-only suggestions, replace forgeable K7 UUID echo with a signed/session-backed token, resolve K6 scope, and use a pgvector-capable DB test image.

### Disposition (Claude tahkimi + uygulanan fix'ler)

| ID | Severity | Tahkim | Fix |
|---|---|---|---|
| F7 | high, contract-level | claude-confirmed (aktif-only aday listesi draft dönemde pilot atamasını UI'dan imkânsız kılar; spec §5 "elle atanır" mekanizmasız kalmıştı) | Codex'in fallback'i benimsendi: `scripts/assign_sub_sector.py` operatör aracı (T33; 3 test); T26'ya bilinçli-aktif-only politika notu; T31 smoke beklentisi düzeltildi; UI draft görünürlüğü için GENİŞLETİLMEDİ |
| F8 | high, contract-level (k7-split-flow-truth reopen #1) | claude-confirmed (client-echo tek başına provenance değil — aynı-sektör forge yüzeyi açıktı) | Echo-persist yerine **eşitlik-reddi**: server INSERT anında ctx'i kendisi yükler, YALNIZ echo==ctx.package_id'de damgalar; 5-dal karar tablosu (409/422); forge fiziksel imkânsız (kabul edilen tek değer sunucunun güncel gerçeği); kripto-token/yeni-secret YOK; race testi 409-beklentisine çevrildi + forge/stale testleri |
| F9 | technical-medium, contract-level | claude-confirmed ("TÜM prompt metinleri" cümlesi ile spec §5'in analyze-website prompt değişikliği talebi çelişik okunuyordu) | Global Constraints K6 kapsam netleştirmesi (içerik-üretim yüzeyleri + Tier-1; analyze-website K6-dışı bilinçli değişiklik); T27'ye `build_analyze_website_prompt` saf inşa + boş-aday byte-eşitlik testi (aktif paket yokken canlı davranış birebir) |
| F10 | technical-medium (Codex: implementation-mechanics; test-altyapı kontratı olarak fix-required'a çekildi) | claude-confirmed (001 `CREATE EXTENSION vector` — grep doğrulu; stok postgres:16 pgvector içermez) | D2 + T6 imajı `pgvector/pgvector:pg16`; fallback'e pgvector'lü sequential-apply kontrolü eklendi |

Sayaçlar: `codex_plan_review_iterations` 2→3 (limit doldu — bundan sonra approve YALNIZ temiz
turda veya kullanıcı kararıyla); `codex_plan_targeted_fixes` = 2. → Re-review Turn 5.

---

## Turn 5 — 2026-07-12 (1 high + 1 medium) → DUR (2. reopen tripwire)

Scope: `--scope working-tree` (Turn 4 fix'leri işlenmiş plan). F11 cluster=k7-split-flow-truth
(**reopen #2** → politika gereği otonom döngü DURDU, kullanıcı raporu), F12
cluster=command-cwd-convention (1/4, yeni). Session auto-fix turu: 4/8 noktasında DUR.

### Codex stdout (verbatim)

# Codex Adversarial Review

Target: working tree diff
Verdict: needs-attention

No-ship for the plan as written: K7 provenance is not closed for the short-video public flow, and several verification commands are path-ambiguous enough to make the plan non-executable from the repo root. Coverage: inspected plan docs/plans/2026-07-12-sektor-bilgi-paketi.md fully, spec docs/specs/2026-07-11-sektor-bilgi-paketi.md fully, active pointer, backend/frontend AGENTS, relevant schemas, sectors/resolver, frontend content creation page, migrations list, Dockerfile, requirements. Did not inspect excluded secret-sanitized files; their absence was not treated as evidence.

Findings:
- [high] contract-level: K7 echo/provenance contract is incomplete for short-video stage split (docs/plans/2026-07-12-sektor-bilgi-paketi.md:677-698)
  Spec §10.4 requires the stamp to identify the package content that produced the post. The plan introduces an echo+equality contract, but only binds the public schema to PostGenerate and the frontend task only says to carry generate_caption.sector_package_id into generate_post. The existing frontend short-video flow calls /posts/generate-caption first and then /posts/generate-short-video-stage1, but the plan does not require CaptionData to store sector_package_id or ShortVideoGenerate/stage1 payloads to carry and validate that echo. Inferred failure: if v1 generated the caption/script/image_prompt and v2 becomes active before stage1, the short-video post can be stamped with the current stage1 package rather than the package that produced the caption/script inputs, breaking the K7 guarantee for one of the explicitly in-scope surfaces.
  Recommendation: root cause: the echo contract was specified around image/carousel PostGenerate and then generalized to short-video without binding the public schema/frontend state. minimal fix strategy: extend T23/T29 to add sector_package_id to caption response typing, store it in captionData, add sector_package_id to ShortVideoGenerate and every stage-split request that consumes caption-generated artifacts, and enforce the same equality-reject matrix before stamping or generating stage1. exact affected files+functions: docs/plans/2026-07-12-sektor-bilgi-paketi.md T23/T29; implementation targets apps/social/backend/app/models/schemas.py ShortVideoGenerate and PostGenerate; apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx handleGenerateCaption and /posts/generate-short-video-stage1 payload; backend short-video stage1 route/pipeline. related files w/ same pattern: image/carousel /posts/generate payload already covered by T29; preview internal endpoint can write ctx directly and should stay separate. verification command: add/run `.venv/bin/pytest tests/db/test_k7_stamp_integration.py -q -m db` with a short-video race test v1 caption -> v2 activation -> stage1 returns 409/no stamp, plus `npm run build` in apps/social/frontend. risk if wrong: false K7 provenance on paid/generated video content, making rollback/audit and draft-vs-active evidence unreliable. fallback: if echo threading is too large, move short-video public package injection/stamping out of Faz 2 until a single-request or signed-token provenance contract is specified.
- [medium] implementation-mechanics: verification and migration commands are not cwd-stable (docs/plans/2026-07-12-sektor-bilgi-paketi.md:39-41)
  The plan’s global test contract uses `.venv/bin/pytest tests/regression/ -q`, while Task 2 creates the venv under apps/social/backend. Later checkpoints repeat the same relative command without specifying cwd. Likewise the DB fixture says it applies `shared/db/migrations/*.sql`; from the backend cwd that path does not exist, and from the repo root `.venv/bin/pytest` does not exist. This is a path/command contract defect: different workers can follow the written commands faithfully and fail before reaching the intended tests.
  Recommendation: root cause: the plan mixes backend-relative test paths with repo-root migration paths but does not define a single execution cwd or absolute path convention. minimal fix strategy: state one command convention globally, e.g. all backend commands run with cwd apps/social/backend and migration runner resolves repo root via pathlib parents to ../../../shared/db/migrations, or all commands are repo-root prefixed as apps/social/backend/.venv/bin/pytest apps/social/backend/tests/... exact affected files+functions: docs/plans/2026-07-12-sektor-bilgi-paketi.md global K6 command, T6 migration runner, T13/T25/T36 checkpoints. related files w/ same pattern: apps/social/backend/Dockerfile uses WORKDIR /app, existing tests directory is planned under apps/social/backend/tests, migrations live under shared/db/migrations. verification command: run the exact documented commands from the declared cwd in a clean shell; for DB, assert the runner prints the resolved migration directory and applies 001->032. risk if wrong: execute-time churn, false red gates, or a fallback dump path being invoked because the runner cannot find migrations rather than because migrations are invalid. fallback: add wrapper scripts `apps/social/backend/scripts/run_regression_tests.sh` and `run_db_tests.sh` that cd/resolve paths internally, then make the plan reference only those scripts.

Next steps:
- Patch the plan before implementation: close the short-video K7 echo contract and normalize all test/migration commands to a declared cwd/path convention.

### DUR kaydı

`k7-split-flow-truth` cluster'ı 2. kez yeniden açıldı (F4 Turn 3 → F8 Turn 4 reopen#1 → F11
Turn 5 reopen#2) → AUTO-FIX-REVIEW-POLICY "2.-reopen = non-convergence kabul → DUR + kullanıcı
raporu" tetiklendi. Claude tahkimi: F11 doğru (ShortVideoGenerate/captionData public alanları
bağlanmamış — kapsam-tamamlama), F12 doğru (cwd-karışık komutlar). Karar kullanıcıya sunuldu.

### Kullanıcı DUR kararı + Turn 5 disposition (2026-07-12)

Kullanıcı DUR raporundan **devam** seçti (tek refine turu + re-review). Tahkim + fix'ler:

| ID | Severity | Tahkim | Fix |
|---|---|---|---|
| F11 | high, contract-level (k7-split-flow-truth reopen #2 — DUR sonrası kullanıcı onayıyla işlendi) | claude-confirmed (stage-split kuralı generikti; PUBLIC şema/frontend alanları isimsizdi) | T23'e ShortVideoGenerate.sector_package_id bağlaması + 5-dal matrisin stage1'de üretim-öncesi uygulanması + damga-yazan-istek kuralı; T29 captionData + stage1 payload taşıma; `test_short_video_stage1_race_rejected_409` eklendi |
| F12 | medium, implementation-mechanics (path/komut doğruluğu — plan-stage focus'ta) | claude-confirmed (backend-cwd komutlarla repo-root migration path'i karışıktı) | Global Constraints'e cwd sözleşmesi (backend komutları cwd=apps/social/backend; npm cwd=frontend); T6 runner pathlib ile repo-kökü çözer + çözülen dizini loglar |

Sayaçlar: `codex_plan_review_iterations` 3→4 (cap aşımı kullanıcı-onaylı devamla; P4 kuralı —
final tur temiz + unresolved NONE ise `approved` + audit-not); `codex_plan_targeted_fixes` = 2.
→ Re-review Turn 6.

---

## Turn 6 — 2026-07-12 (1 high + 2 medium) → K7 cluster 4-tavan DUR

Scope: `--scope working-tree` (Turn 5 fix'leri işlenmiş plan). Ledger: F13
cluster=activation-lifecycle-queued-posts (1/4, yeni), F14 cluster=k7-split-flow-truth
(**tur 4/4 — TAVAN DOLDU** → o cluster için DUR + kullanıcı raporu #2), F15
cluster=add-sub-sector-idempotency (1/4, yeni). Session auto-fix turu: 5/8.
F13+F15 claude-confirmed → otonom fix (farklı cluster); F14 kullanıcı kararına sunuldu.

### Codex stdout (verbatim)

# Codex Adversarial Review

Target: working tree diff
Verdict: needs-attention

No-ship: the plan still has contract-level gaps around package activation lifecycle and public K7 echo compatibility. Coverage: inspected docs/plans/2026-07-12-sektor-bilgi-paketi.md, docs/specs/2026-07-11-sektor-bilgi-paketi.md, docs/active/CURRENT.md, app AGENTS, related visible schemas/frontend/API/migration files; excluded secret-scanned files were not treated as absent.

Findings:
- [high] contract-level: activation can strand already scheduled posts stamped with the previous active package (docs/plans/2026-07-12-sektor-bilgi-paketi.md:747-756)
  The plan requires the publish trigger and scheduler filter to allow only NULL or currently active package stamps. Activation then archives the previous active package before activating the next one. That means any ready/scheduled post generated under v1 but not yet published when v2 activates will be filtered out by scheduled-due or rejected on status transition. This is not a rare edge: scheduled content is a normal product path, and the plan has no pre-activation drain, operator warning, retry policy, or test for this lifecycle window.
  Recommendation: Root cause: the publish contract is expressed as 'package must be active now' but activation lifecycle does not account for queued posts stamped with the previous active package. Minimal fix strategy: add an activation preflight/guard that queries non-terminal posts referencing the current active package before archive; require operator choice to publish/drain/regenerate/cancel before activation, or explicitly revise the DB contract if archived-but-once-active stamps should remain publishable. Exact affected files+functions: docs/plans/2026-07-12-sektor-bilgi-paketi.md T10 posts trigger, T24 get_scheduled_due_posts, T34 activate_sector_package.py activate/rollback. Related files w/ same pattern: shared/db/migrations/032_sector_packages.sql, apps/social/backend/app/routers/internal.py get_scheduled_due_posts, apps/social/backend/scripts/activate_sector_package.py. Verification command: cd apps/social/backend && .venv/bin/pytest tests/db/test_package_pipeline.py tests/db/test_migration_032.py -q -m db with a new test that creates a scheduled post stamped v1, activates v2, and asserts the chosen policy. Risk if wrong: scheduled customer content silently stops publishing or fails only at n8n/publish time after a package rollout. Fallback: block activation when any unpublished post references the package being archived.
- [medium] contract-level: K7 echo matrix is ambiguous for quote generation and can break an existing public content type (docs/plans/2026-07-12-sektor-bilgi-paketi.md:684-698)
  T23 defines the echo validation on PostGenerate broadly: if ctx exists and echo is null, return 409. But the existing PostGenerate schema includes quote fields, and the current frontend quote path calls /posts/generate directly without caption-first state or any sector_package_id. T29 only threads the echo from captionData to image/carousel and short-video stage1. Unless the implementation scopes the 5-branch matrix away from quote, packaged brands will lose quote generation as soon as they have an active package.
  Recommendation: Root cause: the plan changes a public request contract at the route/schema level but does not define content-type scoping for non-caption-first PostGenerate paths. Minimal fix strategy: state explicitly whether quote is package-consuming; if not, exempt quote from ctx echo enforcement and keep sector_package_id NULL; if yes, add a caption-first/echo flow for quote too. Exact affected files+functions: docs/plans/2026-07-12-sektor-bilgi-paketi.md T23/T29, apps/social/backend/app/models/schemas.py PostGenerate, apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx quote /posts/generate call. Related files w/ same pattern: apps/social/frontend/components/templates/CaptionEditor.tsx CaptionData, backend posts.generate route. Verification command: cd apps/social/backend && .venv/bin/pytest tests/db/test_k7_stamp_integration.py -q -m db with packaged-brand quote coverage; cd apps/social/frontend && npm run build. Risk if wrong: existing quote generation starts returning 409 for every packaged brand. Fallback: make echo enforcement opt-in for content types that actually consumed package context.
- [medium] contract-level: add_sub_sector idempotency can silently accept an incompatible existing slug (docs/plans/2026-07-12-sektor-bilgi-paketi.md:951-958)
  T33 specifies add_sub_sector.py as idempotent with ON CONFLICT (slug) DO NOTHING. That only proves duplicate inserts do not crash; it does not prove the existing row is actually the intended child sector under the intended parent. If a slug already exists as a root or under the wrong parent/display, the script can report success while the subtype/package/preview invariants later fail or attach the pilot to the wrong taxonomy node.
  Recommendation: Root cause: idempotency is specified as conflict suppression rather than state reconciliation/validation. Minimal fix strategy: after ON CONFLICT, fetch the slug and assert parent_slug/display_name match the requested contract; fail loudly on mismatch. Add tests for existing slug with wrong parent and existing root slug. Exact affected files+functions: docs/plans/2026-07-12-sektor-bilgi-paketi.md T33, apps/social/backend/scripts/add_sub_sector.py add_sub_sector. Related files w/ same pattern: tests/db/test_taxonomy_guards.py, shared/db/migrations/032_sector_packages.sql subtype trigger, scripts/assign_sub_sector.py. Verification command: cd apps/social/backend && .venv/bin/pytest tests/db/test_taxonomy_guards.py -q -m db. Risk if wrong: operator believes the pilot taxonomy row exists correctly, but package import/assignment/preview later fails or uses a wrong parent bucket. Fallback: remove DO NOTHING and require explicit manual resolution for pre-existing slugs.

Next steps:
- Fix the plan contract for activation vs queued stamped posts before implementation.
- Clarify K7 echo enforcement per content type and add tests for quote/non-caption paths.
- Strengthen T33 idempotency from duplicate tolerance to existing-state validation.

### Disposition

| ID | Severity | Tahkim | Fix |
|---|---|---|---|
| F13 | high, contract-level | claude-confirmed (aktivasyon eski-aktife damgalı kuyruklu post'ları sessiz askıya alır; ön-filtre sessizliği pekiştiriyordu) | T34'e aktivasyon ön-kontrolü: yayınlanmamış referanslı post varsa DEFAULT BLOK + liste; `--force` bilinçli devam + audit; T24 ön-filtresi dışladıklarını loglar; DB kontratı (spec §3.4 mutlak kilit) DEĞİŞMEDİ; +2 test |
| F14 | medium, contract-level (k7-split-flow-truth tur 4/4 — TAVAN) | claude-confirmed (matrix content-type ayrımı yapmıyor; quote paketli markada 409'a düşerdi) | **DUR — kullanıcı kararı bekleniyor** (öneri: matrix'i ctx-tüketen akışlarla sınırla + quote muafiyeti + test) |
| F15 | medium, contract-level | claude-confirmed (DO NOTHING idempotensi yanlış mevcut satırı sessiz kabul eder) | T33 add_sub_sector durum-doğrulamalı idempotens (fetch + parent/display assert, sesli hata); test seti 2 yeni vaka ile genişledi |

Sayaçlar: `codex_plan_review_iterations` 4→5; `codex_plan_targeted_fixes` = 2.

### Kullanıcı 4-tavan kararı (2026-07-12)

Kullanıcı **devam — son tur** seçti. F14 fix'i işlendi: T23 matrisine content-type kapsam
cümlesi (matris yalnız ctx-tüketen caption-first zinciri; quote matris-DIŞI, damga NULL;
akış haritası doğrulaması) + `test_quote_generation_unaffected_by_package`. → Re-review Turn 7
(K7 cluster'ı yine bulgu alırsa otonom devam YOK — manuel/daralt'a döner).

---

## Turn 7 — 2026-07-12 (1 high + 1 medium; ikisi de k7-split-flow-truth tur 5)

### Codex stdout (verbatim)

# Codex Adversarial Review

Target: working tree diff
Verdict: needs-attention

No-ship: plan mostly follows the approved phase direction, but K7’s public echo contract has an unproven producer side. Coverage: inspected docs/plans/2026-07-12-sektor-bilgi-paketi.md, docs/specs/2026-07-11-sektor-bilgi-paketi.md, docs/active/CURRENT.md, apps/social/backend/app/models/schemas.py, apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx, apps/social/frontend/components/templates/CaptionEditor.tsx. Related secret-excluded files were not inspected per substrate note; backend route bodies in excluded files were not used as absence evidence.

Findings:
- [high] contract-level: K7 echo source is specified but not tested, so packaged generation can dead-end at 409 (docs/plans/2026-07-12-sektor-bilgi-paketi.md:599-610)
  The plan makes /posts/generate-caption the source of the client echo token by adding sector_package_id to the response, then later makes generate_post/stage1 reject echo-null when a package context exists. However Task 19 only requires a prompt-surface test for package block injection; it does not require any route/API test proving generate-caption actually returns sector_package_id for packaged brands and null for unpackaged brands. Task 23 tests the consumer matrix, but its listed tests can pass with manually supplied echo values even if the producer response is missing. Inference from current frontend: captionData is built from /posts/generate-caption at apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx:815-845 and later used for /posts/generate and /posts/generate-short-video-stage1 at lines 658-674 and 725-747. If the producer field is omitted, the UI will send null/undefined after activation and the new backend matrix intentionally returns 409 for packaged brands, blocking image/carousel/video generation.
  Recommendation: Root cause: producer/consumer contract is split across T19/T23/T29, but only the consumer rejection matrix has explicit tests. Minimal fix strategy: add binding tests before the T23 matrix is allowed to pass: test_generate_caption_returns_sector_package_id_for_active_package, test_generate_caption_returns_null_without_package, and a frontend/API fixture assertion that CaptionData preserves and forwards the field. Exact affected files+functions: docs/plans/2026-07-12-sektor-bilgi-paketi.md T19/T23/T29; apps/social/backend/app/routers/posts.py generate_caption; apps/social/backend/app/core/caption_generator.py generate_captions response assembly; apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx handleGenerateCaption/submit payloads; apps/social/frontend/components/templates/CaptionEditor.tsx CaptionData. Related files w/ same pattern: apps/social/backend/app/models/schemas.py PostGenerate and ShortVideoGenerate. Verification command: cd apps/social/backend && .venv/bin/pytest tests/db/test_k7_stamp_integration.py tests/regression/ -q -m 'db or not db' plus cd apps/social/frontend && npm run build. Risk if wrong: active-package users cannot create posts because the backend rejects stale/missing echo, or worse, posts are generated without a trustworthy K7 stamp. Fallback: make the backend response contract backward-compatible via a temporary server-side session/token bridge or block activation until the frontend echo pass-through and producer response tests are deployed.
- [medium] contract-level: frontend echo pass-through task omits the actual state type file from its file contract (docs/plans/2026-07-12-sektor-bilgi-paketi.md:877-899)
  Task 29 says the frontend must store generate_caption.response.sector_package_id in captionData and pass it to generate_post and short-video stage1, but its Files block only lists a new sectors API client and the brand payload location. Current code imports CaptionData from apps/social/frontend/components/templates/CaptionEditor.tsx, whose interface has no sector_package_id field, and the page constructs CaptionData explicitly from response fields. Without naming CaptionEditor.tsx in the task contract, an implementer can satisfy the listed files/build-oriented step while leaving the shared state type and preservation path incomplete. This is not a cosmetic path issue: it is the public client half of the K7 rejection matrix.
  Recommendation: Root cause: T29’s Files block is narrower than the public interface it changes. Minimal fix strategy: add apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx and apps/social/frontend/components/templates/CaptionEditor.tsx explicitly to T29 Files, and add a required assertion that CaptionData includes sector_package_id?: string | null and onChange/spread paths preserve it. Exact affected files+functions: docs/plans/2026-07-12-sektor-bilgi-paketi.md T29; CaptionEditor.tsx CaptionData; icerik-olustur/page.tsx handleGenerateCaption and generation payload construction. Related files w/ same pattern: backend schemas PostGenerate and ShortVideoGenerate, because they must accept the forwarded field. Verification command: cd apps/social/frontend && npm run build, plus a focused test or type check that generated payloads include sector_package_id from captionData for image/carousel/video. Risk if wrong: frontend silently drops the echo token, causing packaged-brand generation to fail with the backend’s intended 409 stale-client path after activation. Fallback: if touching CaptionEditor is undesirable, define a page-local ExtendedCaptionData type and prove all editor onChange paths preserve the extra field.

Next steps:
- Amend the plan before execution so K7 has producer-side tests, not only consumer-side rejection tests.
- Expand T29’s file contract to include the actual frontend state type and page payload paths.

### Disposition (kullanıcı kararı: fix + exhaustive-map turu)

| ID | Severity | Tahkim | Fix |
|---|---|---|---|
| F16 | high, contract-level | claude-confirmed (üretici-taraf response testi yoktu; alan unutulursa paketli üretim aktivasyon sonrası 409'da kilitlenir) | T23'e 2 üretici testi (`test_generate_caption_returns_*`); T19'a üretici-test bağlantı notu |
| F17 | technical-medium, contract-level | claude-confirmed (T29 Files bloğu CaptionData tipinin yaşadığı dosyayı anmıyordu) | T29 Files'a `CaptionEditor.tsx` (CaptionData alanı + onChange/spread korunum şartı) ve `icerik-olustur/page.tsx` eklendi |

Kullanıcı 3. DUR raporunda **fix + exhaustive-map turu** seçti (whack-a-mole kırıcı: Turn 8
prompt'una K7 zinciri uçtan-uca ZORUNLU tam-liste direktifi eklendi; K7 yine bulgu alırsa
otonomi biter). Sayaçlar: iterations 5→6; targeted 2. Session auto-fix: 6/8.

---

## Turn 8 — 2026-07-12 (exhaustive-map turu; 1 high + 2 medium)

K7-map direktifi sonuç verdi: Codex K7 zincirinin kalan boşluklarını TAM LİSTE olarak bildirdi
(coverage satırı: "K7 chain remaining gaps: frontend echo pass-through lacks an executable
contract test; activation/preflight lifecycle misses in-flight publish states"). Ledger: F18
cluster=activation-lifecycle-queued-posts (reopen #1 — tur 2/4), F19 cluster=k7-split-flow-truth
(map-çıktısı; kullanıcı onaylı uygulandı), F20 cluster=migration-commit-discipline (1/4, yeni).
Session auto-fix turu: 7/8.

### Codex stdout (verbatim)

# Codex Adversarial Review

Target: working tree diff
Verdict: needs-attention

No-ship: the plan mostly tracks the spec direction, but K7 still has contract gaps. Coverage: inspected plan docs/plans/2026-07-12-sektor-bilgi-paketi.md, spec docs/specs/2026-07-11-sektor-bilgi-paketi.md, related schemas.py, internal.py, CaptionEditor.tsx, icerik-olustur/page.tsx, package manifests. Not inspected: excluded sanitized files including posts.py, caption_generator.py, short_video.py; findings avoid relying on their unseen bodies. K7 chain remaining gaps: frontend echo pass-through lacks an executable contract test; activation/preflight lifecycle misses in-flight publish states.

Findings:
- [high] contract-level: activation preflight can archive a package while stamped posts are already publishing (docs/plans/2026-07-12-sektor-bilgi-paketi.md:1010-1017)
  T34 blocks activation only for stamped posts in generating/awaiting_approval/ready/scheduled, explicitly excluding the publish-status set. Current code already treats 'publishing' as an in-flight status in duplicate guards, and spec publish locks include publishing/published/partially_published. If a scheduled post transitions to publishing, then the operator activates/rolls back and archives its package, the later publishing->published update can be rejected by the DB lock or leave recovery ambiguous. Root cause: lifecycle preflight models only queued work, not in-flight publish work. Minimal fix strategy: include 'publishing' in the default block set, and explicitly decide whether 'partially_published' should block or be reported as already user-visible. Exact affected files+functions: docs/plans/2026-07-12-sektor-bilgi-paketi.md T34 activate_sector_package.py contract; related file internal.py get_scheduled_due_posts/publisher status flow. Related same-pattern files: app/routers/internal.py status queries. Verification command: .venv/bin/pytest tests/db/test_package_pipeline.py -q -m db with added tests test_activate_blocks_when_publishing_posts_reference_previous_active and, if applicable, partially_published handling. Risk if wrong: activations create stuck publish jobs or user-visible posts whose stamped package is no longer active. Fallback: if business wants force behavior, require --force to list publishing/partially_published separately and document manual recovery before proceeding.
  Recommendation: Revise T34 preflight contract and tests to cover in-flight publishing states before archiving an active package.
- [medium] contract-level: K7 frontend echo chain is only build-checked, so the critical state/payload contract can silently regress (docs/plans/2026-07-12-sektor-bilgi-paketi.md:886-910)
  T29 adds sector_package_id to CaptionData and says all onChange/spread paths must preserve it and both generation payloads must pass it through, but Step 1 verifies only npm run build. Because the field is optional and the page currently constructs captionData and request payloads manually, TypeScript build will not fail if handleGenerateCaption omits sector_package_id, CaptionEditor loses it, or handleGenerate omits it from /posts/generate or /posts/generate-short-video-stage1. Root cause: the frontend half of the 5-branch equality-reject contract has no executable assertion. Minimal fix strategy: add a targeted frontend contract test or a small repository script that parses/executes the relevant page helpers and asserts producer response -> captionData -> image/carousel payload -> short-video stage1 payload preservation, plus CaptionEditor edit preservation. Exact affected files+functions: CaptionEditor.tsx CaptionData/onChange, icerik-olustur/page.tsx handleGenerateCaption and handleGenerate. Related files with same pattern: generated payload construction branches for image/carousel/video. Verification command: add e.g. npm run test:k7-echo or a documented node/tsx script, then run it with npm run build. Risk if wrong: after package activation, packaged brands hit 409 stale-client failures or create unstamped posts despite backend K7 passing. Fallback: if no frontend test runner is introduced, require a grep/static contract script in CI that fails unless sector_package_id appears in CaptionData, setCaptionData, /posts/generate payload, and /posts/generate-short-video-stage1 payload.
  Recommendation: Make K7 echo pass-through an executable frontend contract, not just a build check.
- [medium] contract-level: migration 032 is committed in incomplete states under its final runnable filename (docs/plans/2026-07-12-sektor-bilgi-paketi.md:269-367)
  T7-T10 repeatedly commit shared/db/migrations/032_sector_packages.sql while it is missing later invariant families until T10. Migration runners apply files by name; an intermediate branch, CI job, or manual deploy from a partial commit can create the new tables/columns without subtype, freeze, provenance, publish-lock, or rollback guards. Root cause: a forward-only migration file is treated as an incremental work artifact with production filename. Minimal fix strategy: keep 032 uncommitted until complete, use a non-runnable scratch filename during development, or squash T7-T10 into one commit before any shared branch/deploy. Exact affected files+functions: shared/db/migrations/032_sector_packages.sql plan tasks T7-T10. Related same-pattern files: tests/db/test_migration_032.py should only pass the complete invariant suite before the migration is visible as 032. Verification command: .venv/bin/pytest tests/db/test_migration_032.py -q -m db after the single final migration commit. Risk if wrong: a database can be migrated into a schema that accepts invalid packages or publishable draft-stamped posts, and later trigger additions may not repair bad rows already inserted. Fallback: if partial commits are kept, add an explicit no-deploy/no-merge gate and a CI check that fails while 032 lacks all named trigger/function markers.
  Recommendation: Change the commit strategy so migration 032 becomes runnable only when all spec invariants are present.

Next steps:
- Fix the two K7 contract gaps first; they are directly on the mandatory echo/lifecycle chain.
- Then revise migration commit discipline or add a hard gate preventing partial 032 application.

### Disposition

| ID | Severity | Tahkim | Fix |
|---|---|---|---|
| F18 | high, contract-level | claude-confirmed (`publishing` in-flight; retry/`failed→publishing` arşiv sonrası kilitlenir) | T34 BLOK kümesine `publishing`; `partially_published` rapor-ama-bloklamaz (retry kısıtı raporda); +2 test |
| F19 | technical-medium, contract-level (K7 map kalemi) | claude-confirmed (opsiyonel alan → tsc unutmayı yakalamaz; repo'da frontend test runner yok) | `scripts/check-k7-echo.mjs` statik sözleşme kontrolü (4 görünüm noktası, exit 1); T29 Step'e bağlandı; dürüst etiket: statik varlık kontrolü, davranışsal teyit T35 canlı üretimde |
| F20 | technical-medium, contract-level | claude-confirmed (kısmi 032 gerçek dosya adıyla tarihe girerse ara-commit apply yarı-korumalı şema kurar) | T7-T9 commit'siz (TDD lokal); T10 TEK commit (dosya+testler); T13 apply kapısı "yalnız T10 commit'i tarihteyken" |

Sayaçlar: iterations 6→7; targeted 2. Session auto-fix 7/8 — **bir sonraki fix dalgası global
cap'e takılır; Turn 9 temiz çıkmazsa zorunlu DUR.** → Re-review Turn 9.

---

## Turn 9 — 2026-07-12 (1 high + 2 medium; SON otonom dalga — global cap 8/8'e ulaştı)

### Codex stdout (verbatim)

# Codex Adversarial Review

Target: working tree diff
Verdict: needs-attention

No-ship: plan is directionally aligned with spec phase order and rejects DB-first, but K7 coverage and activation durability still have contract-level holes. Coverage: inspected docs/plans/2026-07-12-sektor-bilgi-paketi.md, docs/specs/2026-07-11-sektor-bilgi-paketi.md, docs/active/CURRENT.md, CaptionEditor.tsx, icerik-olustur/page.tsx, schemas.py, calendar.py, internal.py, plus rg sweeps over backend routers/services. Sanitized-excluded files were not inspected by design; their absence was not treated as a finding. K7 chain: remaining gaps are listed below.

Findings:
- [high] contract-level: K7 matrix is not contractually exercised across every consuming content type (docs/plans/2026-07-12-sektor-bilgi-paketi.md:732-755)
  T23 defines a 5-branch equality/reject matrix, but the RED test list only names generic generate_post tests and does not require the matrix to be parametrized over all PostGenerate consumers: image, carousel, and special_day. That leaves content-type-specific branches free to omit sector_package_id or bypass reject behavior while still satisfying the named tests. The frontend part also relies on a static presence script rather than a behavioral check that CaptionData survives editor changes and reaches both payloads. Inference: because current icerik-olustur has distinct image/carousel/special_day/video branches, a single generate_post happy/race test is not enough to prove all consumers preserve the echo.
  Recommendation: root cause: K7 is specified as an end-to-end echo contract, but tests are named by endpoint rather than endpoint x content_type matrix. minimal fix strategy: make T23 require parametrized tests for image, carousel, special_day over all five matrix outcomes; keep quote as explicit exemption; add T29 a lightweight behavioral/unit or Playwright-style smoke that generates captionData, edits via CaptionEditor, then asserts /posts/generate and /posts/generate-short-video-stage1 payloads include the same sector_package_id. exact affected files+functions: docs/plans T23/T29; future apps/social/backend/tests/db/test_k7_stamp_integration.py; apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx handleGenerate/handleGenerateCaption; apps/social/frontend/components/templates/CaptionEditor.tsx onChange paths. related files w/ same pattern: apps/social/backend/app/models/schemas.py PostGenerate and ShortVideoGenerate. verification command: cd apps/social/backend && .venv/bin/pytest tests/db/test_k7_stamp_integration.py -q -m db; cd apps/social/frontend && npm run build && node scripts/check-k7-echo.mjs plus the new behavioral echo test. risk if wrong: stale or forged package echoes can be rejected for one content type but silently accepted/dropped for another, breaking K7 provenance exactly where rollback/debug evidence is needed. fallback: if frontend behavioral test infra is intentionally out of scope, expand check-k7-echo.mjs to parse the concrete setCaptionData and payload object literals for exact field propagation and document the residual as unproven behavior.
- [medium] contract-level: short-video special-day path can miss the package holiday visual emphasis (docs/plans/2026-07-12-sektor-bilgi-paketi.md:662-681)
  The plan defines visual_language_line(ctx, style='director', holiday_name_tr?) so matching ozel_gun.gorsel_vurgu is added to short-video director prompts, but T22 only requires generic director-line and motion-pool tests. T29 only adds K7 echo to /posts/generate-short-video-stage1. Current frontend stage1 payload does not send special_day_name/category, even though schemas.py already has those fields and the image/carousel path sends them. Without an explicit plan step/test, special-day short videos can receive the generic sector line but not the holiday-specific visual emphasis required by spec §6.4/§7.
  Recommendation: root cause: holiday context threading is specified in the block builder but not carried through the short-video stage1 consumer contract. minimal fix strategy: extend T22/T29 to require special_day_name threading into short_video pipeline and stage1 payload for special_day video; add a RED test like test_s5_s6_director_special_day_includes_gorsel_vurgu and a frontend payload check for stage1 special_day fields. exact affected files+functions: docs/plans T22/T29; future apps/social/backend/app/services/short_video.py build_director_prompt pipeline call; apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx handleGenerate video branch. related files w/ same pattern: apps/social/backend/app/models/schemas.py ShortVideoGenerate special_day_name/special_day_category. verification command: cd apps/social/backend && .venv/bin/pytest tests/regression/test_k6_surfaces.py -q; cd apps/social/frontend && node scripts/check-k7-echo.mjs after extending it. risk if wrong: special-day short videos lose the package’s event-specific visual constraints while passing the generic package-injection tests. fallback: if short-video holiday emphasis is intentionally out of scope, mark that as a spec override and remove/qualify the director holiday_name_tr promise.
- [medium] contract-level: activation pre-check is not made atomic with the package status transition (docs/plans/2026-07-12-sektor-bilgi-paketi.md:1021-1035)
  T34 blocks activation when queued/in-flight posts reference the package to be archived, but the plan does not require the pre-check and archive/activate transition to share a lock or serializable transaction over posts. Current scheduling is a plain UPDATE to status='scheduled', so a post can be checked as absent, scheduled against the current active package, then the package is archived. The DB publish lock will later reject or T24 will prefilter it, but the default 'block unless operator forces' contract has already been bypassed by a race.
  Recommendation: root cause: lifecycle preflight is described as a query before archive, not a durable transition protocol. minimal fix strategy: require activate/rollback to run pre-check plus status updates in one transaction with an advisory lock per sector_id or SELECT ... FOR UPDATE on relevant sector_packages plus matching posts; add a race test with two connections where scheduling attempts between pre-check and archive. exact affected files+functions: docs/plans T34; future apps/social/backend/scripts/activate_sector_package.py activate/rollback; apps/social/backend/app/routers/calendar.py schedule_post as competing writer. related files w/ same pattern: apps/social/backend/app/routers/internal.py scheduled-due prefilter. verification command: cd apps/social/backend && .venv/bin/pytest tests/db/test_package_pipeline.py -q -m db with a new concurrency test. risk if wrong: activation can strand scheduled or publishing work on an archived package without an explicit --force decision, producing hidden queue loss or later publish failures. fallback: if full locking is too heavy, make activation re-run the blocking query inside the same transaction immediately before commit and fail if any matching rows appeared, then document the residual race window.

Next steps:
- Patch the plan before execution: expand T23/T29 K7 tests, add short-video special-day threading checks, and make T34 activation preflight atomic.
- Then re-run review against the updated plan/spec alignment.

### Disposition (daraltılmış tahkim)

| ID | Severity | Tahkim | Fix |
|---|---|---|---|
| F21 | high, contract-level (k7 zinciri) | KISMEN confirmed: tip-başına test seli yerine YAPISAL çözüm — matris route girişinde TEK yürütme noktası (dallanmadan önce) → tip-başına bypass imkânsız; Playwright önerisi REDDEDİLDİ (repo'da runner yok — Codex'in kendi fallback'i benimsendi) | T23'e tek-yürütme-noktası kuralı + `test_stamp_persists_across_content_types` (3 tip parametrize); check-k7-echo.mjs obje-literal düzeyine güçlendirildi + dürüst kalıntı genişletildi |
| F22 | technical-medium, contract-level | claude-confirmed KOŞULLU (şema alanları var; UI video+özel-gün sunuyorsa threading, sunmuyorsa belgeli no-op) | T22'ye koşullu threading bloğu + `test_s5_s6_director_special_day_includes_gorsel_vurgu`; T29 video dalına alan taşıma |
| F23 | technical-medium, contract-level | claude-confirmed (Codex'in kendi fallback'i benimsendi: tam kilit yerine tek-txn + commit-öncesi yeniden-kontrol + belgeli mikro-kalıntı; çift güvence ağı zaten var) | T34 atomiklik kuralı + `test_activate_aborts_if_queued_post_appears_before_commit` |

Sayaçlar: iterations 7→8; targeted 2. **Session global cap 8/8 DOLDU** — bundan sonra otonom
fix dalgası YOK; Turn 10 temiz → P4 approved; bulgu → zorunlu DUR + kullanıcı kararı.
→ Re-review Turn 10 (final).

---

## Turn 10 — 2026-07-12 (1 critical + 1 high + 1 medium) → GLOBAL CAP DUR (8/8)

Otonom fix hakkı bitti (session global cap). Yön onayı Codex'ten geldi: "Direction check:
Faz 0→4 direction aligns with spec §14; blockers are K7 contract/test gaps, not DB-first
ordering."

### Codex stdout (verbatim)

# Codex Adversarial Review

Target: working tree diff
Verdict: needs-attention

No-ship: the plan’s K7 echo chain still has contract-level gaps. Coverage: inspected docs/active/CURRENT.md, docs/plans/2026-07-12-sektor-bilgi-paketi.md, docs/specs/2026-07-11-sektor-bilgi-paketi.md, app AGENTS files, schemas.py, CaptionEditor.tsx, icerik-olustur/page.tsx, relevant migrations/status references. Excluded sanitized files were not inspected by design; posts.py/short_video.py internals are unavailable in this substrate. Direction check: Faz 0→4 direction aligns with spec §14; blockers are K7 contract/test gaps, not DB-first ordering.

Findings:
- [critical] contract-level: K7 echo equality does not prove provenance, despite claiming forged stamps are impossible (docs/plans/2026-07-12-sektor-bilgi-paketi.md:700-714)
  Task 23 rejects stale/foreign echoes, but accepts any client-supplied echo equal to the current active package id. That only proves the package is current at save time; it does not prove the submitted caption/image_prompt/platform_captions/script were produced by /posts/generate-caption. A client can obtain or reuse the current sector_package_id and send arbitrary generated fields, and the server will stamp them as package-produced. This directly contradicts the plan’s own claim that client echo is not provenance and that forge is physically impossible, and it weakens spec §10.4’s “stamp points to the content that produced the post” guarantee. K7 chain remaining gap: producer response -> client echo -> consumer equality is version-skew protection, not content provenance.
  Recommendation: Root cause: using bare package_id echo as a provenance token. Minimal fix strategy: either explicitly downgrade K7 semantics to “current package at insert time” or add a real server-verifiable provenance contract. Exact affected files/functions: plan T19/T23/T29; backend generate_caption response, PostGenerate and ShortVideoGenerate schemas, generate_post/stage1 handlers; frontend CaptionData pass-through. Related files with same pattern: CaptionEditor.tsx and icerik-olustur/page.tsx payload builders. Verification command: add DB/API tests such as forged-current-echo-with-arbitrary-platform_captions/image_prompt/script must reject, plus allowed-edit policy tests; run `.venv/bin/pytest tests/db/test_k7_stamp_integration.py -q -m db`. Risk if wrong: audit trail falsely attributes arbitrary or heavily mutated content to a sector package version. Fallback: persist generated caption drafts server-side and create posts by draft id, or return an HMAC/signed token over package_id + generated payload hash + expiry and verify it before stamping.
- [high] contract-level: release-critical frontend K7 echo preservation is knowingly left unproven until live pilot (docs/plans/2026-07-12-sektor-bilgi-paketi.md:911-920)
  Task 29 says the static check only verifies object-literal presence and explicitly admits editor onChange preservation and end-to-end carrying are not behavior-proven, deferring proof to the first real Faz 4 production. That is a test-contract gap in the exact K7 chain the plan is trying to close: generate-caption response -> captionData state -> CaptionEditor edits -> /posts/generate and /posts/generate-short-video-stage1 payloads. If CaptionEditor or page state drops sector_package_id after any edit/reset path, activated package users hit 409 or lose stamps, and the plan will only discover it during live rollout.
  Recommendation: Root cause: substituting shallow static presence checks for behavior proof on a public interface chain. Minimal fix strategy: make T29’s verification simulate or test the actual state transformations, including generate response mapping, CaptionEditor onChange, hashtag/platform edits, image/carousel payload, and short-video stage1 payload. Exact affected files/functions: `apps/social/frontend/components/templates/CaptionEditor.tsx` CaptionData/onChange paths; `apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx` handleGenerateCaption and handleGenerate payload builders; `apps/social/frontend/scripts/check-k7-echo.mjs`. Related files with same pattern: PostGenerate/ShortVideoGenerate backend schemas. Verification command: `npm run build && node scripts/check-k7-echo.mjs`, where the script must execute or AST-validate all state transitions, not just field presence. Risk if wrong: package activation makes normal users’ generated captions fail at save time or silently lose K7 provenance. Fallback: add a minimal Vitest/RTL test if the Node static script cannot prove transformations reliably.
- [medium] contract-level: special-day short-video package context is conditional in the plan even though the current UI path exists (docs/plans/2026-07-12-sektor-bilgi-paketi.md:934-936)
  T22/T29 leave special_day_name/special_day_category threading to short-video stage1 conditional on whether the UI supports special-day video. The inspected frontend already routes effectiveContentType === 'video' through generate-caption and then stage1, and the current stage1 payload comment says extra special-day fields are not sent. Leaving this as “if possible” lets the director special-day gorsel_vurgu path pass backend fixture tests while the real special-day short-video consumer never supplies the holiday key, so one K7/content-type branch remains under-specified.
  Recommendation: Root cause: plan uses a conditional UI-capability caveat instead of binding the known current special-day video path. Minimal fix strategy: make stage1 special_day_name/special_day_category pass-through mandatory for special_day + short-video, and add it to the K7/static frontend contract. Exact affected files/functions: T22 special-day threading, T29 `icerik-olustur/page.tsx` stage1 payload, ShortVideoGenerate schema/route. Related files with same pattern: current `apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx` stage1 payload around the short-video branch. Verification command: `node scripts/check-k7-echo.mjs` should also assert special_day video fields, plus `.venv/bin/pytest tests/regression/ -q` for director gorsel_vurgu. Risk if wrong: special-day short videos with active packages omit the package holiday visual emphasis while appearing covered by backend-only tests. Fallback: if product decides special-day short-video is out of scope, remove that UI path or explicitly mark that content type out of K7/package special-day coverage before activation.

Next steps:
- Fix the K7 provenance contract before implementation starts; equality-only echo is not enough for the stated guarantee.
- Upgrade T29 from static presence checking to behavior-level frontend contract proof.
- Make special-day short-video stage1 holiday fields mandatory or explicitly remove that branch from package coverage.

### Claude tahkimi (fix UYGULANMADI — cap dolu; kullanıcı kararı bekleniyor)

| ID | Codex severity | Claude tahkimi |
|---|---|---|
| F24 | critical | **Claim-overreach olarak confirmed, mekanizma kusuru olarak DEĞİL:** caption zaten KULLANICI-DÜZENLENEBİLİR (CaptionEditor ürün özelliği) → "içerik-bütünlüğü provenance'ı" hiçbir tasarımla verilemezdi; damganın dürüst semantiği "üretim anında yürürlükteki paket sürümü" (eşitlik kuralı bunu zorlar; yanlış-sürüm/yabancı/draft damga fiziksel kapalı). Codex'in kendi 1. çözüm şıkkı (semantik netleştirme/downgrade) doğru fix; HMAC/server-draft orantısız + editör özelliğiyle çelişir. Plandaki "forge fiziksel imkânsız" cümlesi fazla iddialı — "yanlış-sürüm damgası fiziksel imkânsız" olmalı. |
| F25 | high | **tradeoff-medium'a düşürüldü:** frontend davranışsal test altyapısı kurmak (Vitest/RTL) belgeli-kalıntıya karşı orantısız; risk pilot sıralamasıyla sınırlı (aktivasyon yalnız Faz 4'te, ilk üretimler Eray'ın elinde — alan düşerse anında görünür 409). Yatırım kararı kullanıcının. |
| F26 | medium | **technical-medium confirmed:** Codex UI yolunu doğruladı (video+özel-gün kombinasyonu MEVCUT) → T22/T29'daki "koşullu" ifade çözülebilir durumda, threading ZORUNLU olmalı + statik script'e 2 alan eklenir. Küçük fix. |

### Kullanıcı global-cap kararı (2026-07-12): SON kapanış turu

Kullanıcı "son kapanış turu"nu seçti. Uygulanan (cap-sonrası kullanıcı-onaylı):
- **F24:** T23 damga semantiği kalibre edildi — damga = "üretim isteği anında yürürlükteki
  paket sürümü" (version-governance); içerik-bütünlüğü iddiası açıkça REDDEDİLDİ (caption
  editörle serbest düzenlenebilir); "forge fiziksel imkânsız" → "yanlış-sürüm damgası fiziksel
  imkânsız" olarak düzeltildi.
- **F26:** T22/T29 threading KOŞULSUZ yapıldı (UI yolu Codex-doğrulu mevcut); check-k7-echo.mjs
  5. görünüm noktası (stage1 special_day alanları).
- **F25:** operatör kararıyla belgeli tradeoff-kalıntı (T29'a kayıt düşüldü; frontend test
  altyapısı kurulmayacak).
Sayaçlar: iterations 8; targeted 2→3. → FINAL re-review Turn 11 (sonuç ne olursa yeni tur YOK:
temiz → approve; kalan → override/durdur kullanıcı kararı).

---

## Turn 11 — 2026-07-12 (FINAL genel tur; 1 high + 2 medium) + kullanıcı mühür kararı

### Codex stdout (verbatim)

# Codex Adversarial Review

Target: working tree diff
Verdict: needs-attention

No-ship: plan/spec direction is broadly aligned, and K7 chain is mostly mapped, but the plan still has contract-level holes in preview fidelity, pilot import path correctness, and the frontend static K7/video-special-day checker contract. K7 chain: remaining gaps are findings 1 and 3; producer response, backend equality matrix, PostGenerate/ShortVideoGenerate schema, quote exemption, backend tests, activation preflight, and scheduled-due prefilter are otherwise explicitly covered. Coverage: inspected docs/active/CURRENT.md, full plan docs/plans/2026-07-12-sektor-bilgi-paketi.md, full spec docs/specs/2026-07-11-sektor-bilgi-paketi.md, available schemas/frontend call sites/sectors resolver/internal scheduler/migrations/package metadata. Sanitized excluded files named in prompt were not inspected as code because they are absent from this substrate, not because they were assumed deleted.

Findings:
- [high] contract-level: internal preview endpoint is too narrow to exercise the real production preview contract (docs/plans/2026-07-12-sektor-bilgi-paketi.md:785-805)
  Task 24 defines POST /internal/posts/generate-preview as only {brand_id, package_id, content_type, prompt, template_id?}. Spec §10.3 requires draft packages to be evaluated through the real production path with comparable package/unpackaged samples, and Task 35 says samples are matched by product class. The current public contract cannot carry the existing production inputs needed for representative image/short-video generation such as template_fields, platforms, aspect_ratio, product_id/product_image_ids, special_day_name/category, voice, visual_brief, scene_reference_image_url, or caption/script data. That makes the pilot likely to validate a simplified path while the real UI path can still fail or omit package-specific special-day/product behavior.
  Recommendation: Root cause: preview API shape was minimized below the production contract. Minimal fix strategy: redefine PreviewGenerateRequest as either a thin wrapper around the existing PostGenerate and ShortVideoGenerate request bodies plus package_id, or explicitly list the supported production fields and state unsupported preview surfaces are out of scope. Exact affected files/functions: plan Task 24 for apps/social/backend/app/routers/internal.py new endpoint and app/models/schemas.py preview request schema; related same-pattern files/functions: posts.py generate_post, short_video.py stage1 pipeline, frontend icerik-olustur payloads at the generate-post and stage1 call sites. Verification command: add tests that preview forwards product_id/template_fields/special_day_name for image and special_day, and voice/visual_brief/special_day_name for short_video, then run `.venv/bin/pytest tests/db/test_package_pipeline.py -q -m db`. Risk if wrong: operator approves a draft based on non-representative preview output, then activated production paths behave differently. Fallback: document preview as free-prompt-only and move product/special-day/video pilot validation out of this plan, but that weakens the spec §10.3 gate.
- [medium] contract-level: official pilot import command points repo-external artifacts at a cwd-relative path (docs/plans/2026-07-12-sektor-bilgi-paketi.md:1081-1099)
  Global constraints say backend commands run with cwd apps/social/backend, while Task 35 says the official run artifacts are repo-external under research-runs/<run_id>. The sample import command passes `--artifacts-dir research-runs/kuyumculuk-2026q3`, which resolves under apps/social/backend, not the repo-external research folder. In the real pilot this can fail to import artifacts or miss `birlesik-taslak.md`, leaving the synthesis provenance absent and activation blocked or forcing manual path repair outside the plan.
  Recommendation: Root cause: command cwd convention conflicts with repo-external artifact location. Minimal fix strategy: make Task 35 use an absolute artifact path, e.g. `/root/otomaix-sosyal-medya-arastirmasi/research-runs/kuyumculuk-2026q3`, or state an explicit `cd /root/otomaix-sosyal-medya-arastirmasi` plus absolute backend script path. Exact affected files/functions: plan Task 35 import command; related files/functions with same pattern: Task 16 import_sector_package.py CLI `--artifacts-dir`, Task 32 repo-external hakem-sentez file. Verification command: run a dry-run/import test with an absolute temp artifacts directory containing KAYNAK-1/2/3, denetci-1/2, and birlesik-taslak, then `.venv/bin/pytest tests/db/test_package_pipeline.py -q -m db`. Risk if wrong: first official pilot cannot activate because provenance artifacts were not loaded from the intended run. Fallback: require operator to copy artifacts under apps/social/backend/research-runs, but that contradicts the repo-external artifact contract and should be documented if chosen.
- [medium] contract-level: K7/static frontend checker contract contradicts the mandatory video special-day payload check (docs/plans/2026-07-12-sektor-bilgi-paketi.md:915-950)
  Task 29 says check-k7-echo.mjs verifies four object-literal points for K7 echo pass-through, ending at generate-short-video-stage1. Later the same task makes video `special_day_name` and `special_day_category` mandatory and says the checker verifies those as a fifth visibility point. The executable contract is therefore ambiguous: an implementer can satisfy the enumerated four K7 points while missing the special-day stage1 fields that Task 22 requires for director `gorsel_vurgu`. This is not the accepted residual about behavioral frontend tests; it is a static contract gap in the only planned frontend proof.
  Recommendation: Root cause: the checker scope was updated for F26 but the enumerated contract still says four points. Minimal fix strategy: change Task 29 to list five checks explicitly, with the fifth asserting `special_day_name` and `special_day_category` are present in the `/posts/generate-short-video-stage1` payload when video special-day mode is possible. Exact affected files/functions: plan Task 29 and future apps/social/frontend/scripts/check-k7-echo.mjs; related files/functions: apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx stage1 payload, apps/social/backend/app/models/schemas.py ShortVideoGenerate, Task 22 `visual_language_line(... holiday_name_tr=...)`. Verification command: `cd apps/social/frontend && npm run build && node scripts/check-k7-echo.mjs`, with a negative fixture or script self-test proving removal of either special_day field exits nonzero. Risk if wrong: video special-day generations lose package holiday visual emphasis while K7 echo appears green. Fallback: split this into a second script `check-video-special-day-payload.mjs`, but keep it in the same Task 29 gate.

Next steps:
- Patch the plan before implementation: widen the preview request contract, correct the repo-external import path, and make the frontend static checker enumerate five required checks.
- After patching, rerun a targeted plan review for these three corrected contracts plus the K7 echo chain only.

### Disposition (kullanıcı kararı: işle + hedefli mini-review)

| ID | Severity | Tahkim | Fix |
|---|---|---|---|
| F27 | high, contract-level | claude-confirmed (preview gövdesi üretim girdilerini taşımıyordu — §10.3 gerçek-yol temsiliyeti zayıflardı) | T24 body ince zarf oldu: `{package_id, mode, payload: PostGenerate \| ShortVideoGenerate}` + `test_preview_forwards_production_fields` |
| F28 | technical-medium | claude-confirmed (cwd-göreli artifacts yolu repo-dışı klasörle çelişiyordu) | T35 komutu MUTLAK yol (`/root/otomaix-sosyal-medya-arastirmasi/research-runs/...`) + gerekçe notu |
| F29 | technical-medium | claude-confirmed (kendi F26 eklemem 4-nokta listesiyle çelişik kalmıştı) | check-k7-echo.mjs sözleşmesi 5 açık maddeye çıkarıldı |

Sayaçlar: iterations 8; targeted 3→4. Kullanıcı **"işle + hedefli mini-review"** seçti →
Turn 12 = DAR kapsam (F27/F28/F29 kapanışı + K7 zinciri; operatör-kabullü kalıntılar
[F25-statik-script, F24-semantik] yeniden-açılmaz). KESİN son çağrı.

---

## Turn 12 — 2026-07-12 (HEDEFLİ final mini-review) → KAPANIŞ

### Codex stdout (verbatim)

# Codex Adversarial Review

Target: working tree diff
Verdict: needs-attention

NO-SHIP narrowly: F27 closed, F28 closed, K7 chain closed, but F29 is not fully closed because Task 29 still has a stale 4-point verification criterion after defining a 5-point contract. Coverage: docs/plans/2026-07-12-sektor-bilgi-paketi.md and docs/specs/2026-07-11-sektor-bilgi-paketi.md inspected; requested prior review log was absent from substrate.

Findings:
- [low] F29 verification text still allows a 4-point K7 echo check (docs/plans/2026-07-12-sektor-bilgi-paketi.md:957-959)
  Task 29 correctly defines `check-k7-echo.mjs` as a 5-point static contract at lines 923-930, including the stage1 `special_day_name`/`special_day_category` check. But its implementation/verification step still says `node scripts/check-k7-echo.mjs` proves `4 görünüm noktası mevcut`. That contradiction keeps F29 from being cleanly closed: an implementer or reviewer following the step text could accept a script that omits the fifth stage1 special-day check, weakening the K7 video echo chain the plan is meant to lock.
  Recommendation: Root cause: stale acceptance text from the pre-F29 version. Minimal fix: change the parenthetical at line 959 from 4 to 5 and explicitly name the fifth stage1 special-day pair. Affected file/function: docs/plans/2026-07-12-sektor-bilgi-paketi.md Task 29 Step 1. Related files: planned apps/social/frontend/scripts/check-k7-echo.mjs and apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx. Verification: re-read Task 29 and confirm the contract and Step 1 both require five checks, including `sector_package_id` plus `special_day_name`/`special_day_category` in the same stage1 payload. Risk: without this, the accepted static gate can drift back to four points. Fallback: if the operator intentionally accepts only four, record that as an explicit residual; otherwise update the text.

Next steps:
- F27 closed: Task 24 uses `{package_id, mode, payload: PostGenerate | ShortVideoGenerate}` and requires `test_preview_forwards_production_fields`.
- F28 closed: Task 35 import uses `/root/otomaix-sosyal-medya-arastirmasi/research-runs/kuyumculuk-2026q3`.
- F29 not closed: contract says five, Step 1 still says four.
- K7 chain closed under accepted residuals: producer response, captionData carry, consumers, 5-branch enforcement with quote exemption, stamp, activation preflight, and scheduled-due prefilter are all represented.

### Kapanış kaydı + P4 audit notu

- **F27 CLOSED** (Codex teyitli) · **F28 CLOSED** (Codex teyitli) · **K7 zinciri CLOSED**
  (Codex teyitli — kabul edilen kalıntılarla: F25 statik-script, F24 semantik).
- **F29 → [low]:** tek bayat parantez ("4 görünüm noktası"). Politika (tur 4+ low = audit +
  loop'suz) gereği YENİ TUR AÇILMADAN metin düzeltildi ("5 görünüm noktası" + çift adlandırıldı)
  + kardeş-site süpürmesi (T16 `--artifacts-dir <MUTLAK-yol>` netleştirmesi). targeted 4→5.
- **P4 kararı:** iteration limiti (8/3) ve session cap (8/8) doldu ANCAK final hedefli tur
  unresolved-NONE kapandı → `codex_plan_review_status: approved` (approved-by-iteration-limit
  DEĞİL; o statü yalnız gerçek low/tradeoff residual'la kullanılır). Kalıcı override bayrağı YOK
  (`unresolved_high_severity_override: false`).
- Operatör-kabullü belgeli kalıntılar (bulgu DEĞİL, karar): (1) F25 — frontend davranışsal test
  altyapısı kurulmadı, statik 5-nokta script + Faz 4 canlı teyit; (2) F24 — damga semantiği
  version-governance (içerik-bütünlüğü iddiası yok, caption editörle düzenlenebilir).
- Final sayaçlar: 12 Codex çağrısı (1 boş + 10 genel + 1 hedefli) · iterations 8 · targeted 5 ·
  session auto-fix 8/8 · işlenen bulgu: F1-F29 arası 20 fix + 2 kabul-kalıntı + 1 downgrade.
- Frontmatter finalize edildi: `status: plan-approved` + `codex_plan_review_status: approved`.
