---
title: security-review-claude-codex.md komut tasarımı
status: plan-approved
date: 2026-06-01
source_spec: docs/specs/2026-06-01-security-review-claude-codex-command.md
source_spec_unapproved_override: false
noisy_review_override: false
unresolved_high_severity_override: false
codex_plan_review_status: approved
codex_plan_review_iterations: 0
codex_plan_targeted_fixes: 5
codex_plan_review_log: docs/reviews/codex/2026-06-01-security-review-claude-codex-command-plan.md
---

# security-review-claude-codex.md Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eski tek-aktörlü `/security-review`'ı claude-codex ailesine entegre eden yeni `~/.claude/commands/security-review-claude-codex.md` komutunu oluştur; aile drift contract'ını 5-way → 6-way büyüt; chain referanslarını süpür; eski komutu deprecate et.

**Architecture:** S1 (review-sibling scaffold + spec graft): `review-claude-codex.md`'nin kanıtlanmış yapısını (reviewer-status matrisi, disposition ledger, docs-gate, active-layer) baz al, onaylanmış spec'in security delta'larını (mode-aware Codex binding, `$SCAN_ROOT` izolasyon substratı, git'siz export + fiziksel secret-exclusion, coverage_gap→Şablon D, iki-katmanlı chain gate) graft et. **CODEX-CALL-PROTOCOL bloğu `spec-claude-codex.md`'den `awk` ile mekanik çıkarılıp byte-identical kopyalanır — elle YAZILMAZ.** Doğrulama-güdümlü: prose komut için "test" = drift Check A (6-way sha256 eşitliği) + Check B (tripwire token × 6) + stale-ref/prose grep + frontmatter parse smoke.

**Content source-of-truth:** Onaylanmış spec (`docs/specs/2026-06-01-security-review-claude-codex-command.md`) komut içeriğinin **bölüm-bölüm blueprint'idir**; her komut Adım'ı aynı-adlı spec Adım'ını gerçekler. Plan'ın katma değeri: mekanik adımlar (blok extraction/paste, prose bump, ref sweep, deprecate) + ordering + her task'ın doğrulama kapısı. İçerik spec'ten çevrilir (re-paste edilmez — duplikasyon + sapma riski).

**Tech Stack:** Markdown slash command (`~/.claude/commands/`, repo DIŞI); `awk`/`sha256sum`/`rg --pcre2`/`ruby -ryaml` doğrulama; git (yalnız docs commit).

**Deliverable gerçeği (memory `project-claude-codex-command-execution`):** Komut dosyaları repo DIŞI (`~/.claude/commands/`) → git'e commit EDİLMEZ; audit commit **docs-only** (codex logs + active layer). Smoke = load + frontmatter parse; tam invoke **Claude Code restart** ister. `/simplify` markdown'a N/A. `/finish-branch` `main` üstünde. Backup: `~/.claude/commands/*.bak-<ts>`.

---

## File Structure

- **Create:** `~/.claude/commands/security-review-claude-codex.md` (~520-580 satır; yeni komut)
- **Modify (drift prose 5→6, marker bloğuna DOKUNMA):** `~/.claude/commands/spec-claude-codex.md`, `write-plan-claude-codex.md`, `execute-plan-claude-codex.md`, `simplify-claude-codex.md`, `review-claude-codex.md`
- **Modify (chain-ref sweep `/security-review`→`/security-review-claude-codex`):** `execute-plan-claude-codex.md`, `simplify-claude-codex.md`, `review-claude-codex.md`, `init.md`
- **Rewrite (stub):** `~/.claude/commands/security-review.md`
- **Temp:** `/tmp/codex-call-protocol.md` (canonical blok extraction), `~/.claude/commands/*.bak-<ts>` (backuplar)
- **Committed docs (execute-time):** `docs/reviews/codex/*-execute.md` (execution review log), `docs/active/<slug>/` (TASK+HANDOFF)

---

## Task 1: Backup + Canonical Block Extraction + Baseline Drift

**Files:**
- Temp: `/tmp/codex-call-protocol.md`, `~/.claude/commands/*.bak-<ts>`

- [ ] **Step 1: Backup edilecek 6 dosyayı yedekle**

```bash
TS=$(date +%Y%m%d-%H%M%S)
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex review-claude-codex security-review; do
  cp ~/.claude/commands/$f.md ~/.claude/commands/$f.md.bak-$TS
done
ls ~/.claude/commands/*.bak-$TS
```
Expected: 6 `.bak-<ts>` dosyası listelenir (rollback için).

- [ ] **Step 2: Canonical CODEX-CALL-PROTOCOL bloğunu çıkar**

```bash
awk '/CODEX-CALL-PROTOCOL:BEGIN/{p=1} p{print} /CODEX-CALL-PROTOCOL:END/{p=0}' \
  ~/.claude/commands/spec-claude-codex.md > /tmp/codex-call-protocol.md
wc -l /tmp/codex-call-protocol.md && sha256sum /tmp/codex-call-protocol.md
```
Expected: blok satır sayısı > 0; bir hash kaydet (`<CANONICAL_HASH>`).

- [ ] **Step 3: Baseline — mevcut 5 sibling'in bloğu zaten eşit mi (test ZEMİNİ)**

```bash
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex review-claude-codex; do
  awk '/CODEX-CALL-PROTOCOL:BEGIN/{p=1} p{print} /CODEX-CALL-PROTOCOL:END/{p=0}' ~/.claude/commands/$f.md | sha256sum
done | sort -u
```
Expected: **tek satır hash** (5 blok zaten byte-identical; Codex doğruladı `1de3547...`). Birden fazla satır çıkarsa DUR — zemin bozuk, önce mevcut drift'i araştır.

- [ ] **Step 4: Commit yok** (temp + backup; repo-dışı). Devam.

---

## Task 2: Yeni Komut Scaffold — Frontmatter → Mimari → Akış → Mode Fork

**Files:**
- Create: `~/.claude/commands/security-review-claude-codex.md`

Spec bölüm karşılığı: **Görev / İnvariant / Mimari Yön / Çekirdek Fark / Adım Akışı** (spec satır ~9-72).

- [ ] **Step 1: Doğrulama testini önce tanımla (fail beklenir)**

```bash
test -f ~/.claude/commands/security-review-claude-codex.md && echo EXISTS || echo MISSING
```
Expected: `MISSING` (henüz yok).

- [ ] **Step 2: Dosyayı oluştur — frontmatter + üst yapı**

İçerik spec'ten çevrilir (S1: review-claude-codex format + spec security delta'ları). Bu task'ta yazılacaklar:
- **Frontmatter:** `description` (iki bağımsız güvenlik hakemi + sentez; mode-aware; iki-katmanlı gate), `argument-hint: [--full | --diff [BASE_REF] | <path>...]`.
- **## Görev:** topoloji (iki bağımsız güvenlik hakemi + ana Claude sentez), rol modeli (review ile aynı, aileden fark), sonraki adım zinciri (`… → /review-claude-codex → /security-review-claude-codex → /finish-branch`).
- **## İnvariant:** docs-gate (kod yazmaz, tek artefakt rapor, push YOK) + **iki-katmanlı güvenlik chain gate** (security-risk + dual-review ayrı override; non-directive ton).
- **## Mimari Yön:** çift bağımsız güvenlik hakemi; reddedilen `<DROPPED_ALT>` (modernize-in-place, iki-aşamalı rollout, Codex meta-review).
- **## Çekirdek Fark — Mode-Aware Codex Binding:** spec'teki mod→STEP tablosu (diff→STEP_B, full/path→STEP_A) + binding-yeniliği notu (her iki STEP, mode-bağımlı; blok byte-identical).
- **## Adım Akışı (9 adım):** spec'teki 9-adım özeti (Adım 0 YOK notu dahil).

- [ ] **Step 3: Frontmatter parse smoke**

```bash
ruby -ryaml -e 'd=YAML.load(File.read(ARGV[0]).split(/^---$/)[1]); abort("FAIL") unless d.is_a?(Hash) && d["argument-hint"]' ~/.claude/commands/security-review-claude-codex.md && echo PASS
```
Expected: `PASS` (frontmatter geçerli + argument-hint var).

- [ ] **Step 4: Yapısal grep**

```bash
rg -c 'coverage_mode|İki BAĞIMSIZ güvenlik hakemi|İKİ KATMANLI chain gate|STEP_A|STEP_B' ~/.claude/commands/security-review-claude-codex.md
```
Expected: > 0 (mode tablosu + topoloji + gate + STEP referansları mevcut).

- [ ] **Step 5: Commit yok** (repo-dışı dosya). Devam.

---

## Task 3: CODEX-CALL-PROTOCOL Bloğu — Byte-Identical Mekanik Insert + Binding

**Files:**
- Modify: `~/.claude/commands/security-review-claude-codex.md`

Spec bölüm karşılığı: **Codex Çağrı Noktaları + Codex Çağrı Protokolü** (spec satır ~75-92).

- [ ] **Step 1: Codex Çağrı Noktaları tablosu + binding'i yaz**

`## Codex Çağrı Noktaları` (mod→çağrı→STEP tablosu) + `## Codex Çağrı Protokolü (ortak)` başlığı + binding notu:
> Binding (security-review-claude-codex): `<STEP_A>` (`task --fresh`) = Adım 4b full/path · `<STEP_B>` (`adversarial-review $SCOPE`) = Adım 4b diff. Blok canonical = spec-claude-codex ile byte-identical (drift-check 6-way). Bloğu değiştirirsen 5 aynayı da senkronla.

- [ ] **Step 2: Bloğu /tmp'den MEKANİK yapıştır (elle YAZMA)**

`/tmp/codex-call-protocol.md` içeriğini (BEGIN/END marker'lar dahil) Codex Çağrı Protokolü başlığının altına aynen ekle. **Elle düzenleme YOK** — Codex Turn-1 #1: cwd override blok DIŞINDA (Adım 4b), blok `--cwd "$PROJECT_ROOT"` ile kalır.

- [ ] **Step 3: TEST — yeni dosyanın bloğu canonical ile byte-identical mi**

```bash
awk '/CODEX-CALL-PROTOCOL:BEGIN/{p=1} p{print} /CODEX-CALL-PROTOCOL:END/{p=0}' \
  ~/.claude/commands/security-review-claude-codex.md | sha256sum
sha256sum /tmp/codex-call-protocol.md
```
Expected: **iki hash EŞİT** (`<CANONICAL_HASH>`). Eşit değilse → bloğu yeniden /tmp'den yapıştır (elle düzeltme YASAK).

- [ ] **Step 4: Commit yok.** Devam.

---

## Task 4: Adım 1-3 — Scope/CLI + Dirty-Tree + İzolasyon/Secret/coverage_gap

**Files:**
- Modify: `~/.claude/commands/security-review-claude-codex.md`

Spec bölüm karşılığı: **Adım 1 (CLI+coverage_mode+path-confinement) / Adım 2 (dirty-tree) / Adım 3 (izolasyon substratı + secret preflight + coverage_gap)** (spec satır ~95-260).

- [ ] **Step 1: Adım 1-3'ü yaz (spec'ten çeviri)**

Kritik delta'ları **birebir** taşı:
- **Adım 1:** CLI parse (`--full|--diff [BASE_REF]|<path>...`); **fail-closed mod-karışım reddi**; diff 3-ref terminolojisi; **path-confinement allowlist** (`git ls-files -z` ile token→dosya **expand-then-confine-each-file**; in-scope symlink-escape reddi; PATH_SET = NUL-safe array); `$ARGUMENTS` injection kuralı.
- **Adım 2:** dirty-tree bildirimi; untracked-not-reviewed notu.
- **Adım 3:** `<SECURITY_CONTEXT>`; log setup (`docs/security-reviews/codex/<DATE>-secreview-<SLUG>-<ATTEMPT>.md`); **izolasyon substratı** (diff→worktree, full/path→`git archive HEAD_SHA` git'siz export); **secret preflight 3-yol** (full/path hard `rm` from export + metadata manifest; diff feed-exclusion best-effort + git-show vektörü notu); **post-export symlink sweep** (`$SCAN_ROOT` confinement, NUL-safe `find -print0`); **coverage_gap** (sweep+rm SONRASI `$SCAN_ROOT`'ta fiilen var olan dosyalardan recompute; path fail-closed).

- [ ] **Step 2: TEST — her güvenlik mekanizması için ZORUNLU fail-closed gate (Codex plan-review PA-2; broad grep YETERSİZ)**

```bash
F=~/.claude/commands/security-review-claude-codex.md
# Section-scoped (Codex PA-2 Turn-3): secret/izolasyon gate'leri Adım 3 bölümüne scope'lanır —
# whole-file grep cross-section false-pass yaratıyordu (örn. 'Komutu dur' protokol bloğundaki
# 'Komutu durdur'u yakalıyordu; 'rm -f --' symlink-sweep'i yakalayıp secret-removal'ı kanıtlamıyordu).
A1=$(awk '/^## Adım 1:/{p=1} /^## Adım 2:/{p=0} p' "$F")
A3=$(awk '/^## Adım 3:/{p=1} /^## Adım 4:/{p=0} p' "$F")
fail=0
ns(){ printf '%s' "$3" | grep -qiE "$1" || { echo "EKSİK(scoped): $2"; fail=1; }; }
# Adım 1 CLI mod-karışım fail-closed reddi — A1-scoped + shape-specific (Codex PA Turn-4:
# whole-file 'fail-closed' Adım 3 path/coverage metninden false-pass alıyordu; CLI parser
# path+--full / path+--diff / --full+--diff reddini atlasa bile geçebiliyordu).
ns 'path.*--full'                 'CLI fail-closed: path+--full reddi'         "$A1"
ns 'path.*--diff'                 'CLI fail-closed: path+--diff reddi'         "$A1"
ns '--full.*--diff'               'CLI fail-closed: --full+--diff reddi'       "$A1"
ns 'hata.*STOP|STOP.*hata'        'CLI mod-karışım reddi → hata + STOP (zorunlu; bare fail-closed kabul edilmez)' "$A1"
ns 'expand-then-confine'          'path-confinement token→dosya açılım'        "$A1"
ns 'NUL-safe'                     'PATH_SET NUL-safe array'                    "$A1"
ns 'git archive'                  'git-free export substratı'                  "$A3"
ns 'EXPORT_DIR'                   'export binding ($EXPORT_DIR)'               "$A3"
ns 'find.*-type l.*-print0'       'post-export symlink sweep (NUL-safe)'       "$A3"
ns 'fiilen var olan'              'coverage_gap post-sweep/rm recompute'       "$A3"
ns 'Şablon D'                     'coverage_gap → metadata-only terminal'      "$A3"
ns 'Exclude from Codex'           'secret 3-yol (a) exclude'                   "$A3"
ns 'risk-accept'                  'secret 3-yol (b) risk-accept'               "$A3"
ns '\(c\) [Ss]top'                'secret 3-yol (c) Stop seçeneği'             "$A3"
ns 'export tree.*fiziksel'        'hard exclusion = export fiziksel rm (sweep DEĞİL)' "$A3"
ns 'matched-pattern.*line-count'  'metadata manifest field shape'             "$A3"
ns 'DEĞER YOK'                    'value-free manifest (değer içermez)'        "$A3"
ns 'git-show'                     'diff-mode best-effort git-show caveat'      "$A3"
ns 'Hard exclusion İMKANSIZ'      'diff-mode asimetri (hard exclusion yalnız export)' "$A3"
[ "$fail" -eq 0 ] && echo "Task4 gates PASS" || echo "Task4 gates FAIL"
```
Expected: `Task4 gates PASS` (her güvenlik mekanizması spec'ten yazıldı). Herhangi `EKSİK` → o mekanizmayı spec Adım 1-3'ten ekle, tekrar koş. (Bu gate'ler spec vokabülerine sabitli — tek broad grep'in atladığı mekanizma kaybını kapatır.)

- [ ] **Step 3: TEST — yasak iddia (worktree'de hard exclusion) yok**

```bash
rg -n 'worktree.*hard exclusion|fiziksel rm.*worktree' ~/.claude/commands/security-review-claude-codex.md && echo "BULUNDU-DÜZELT" || echo "TEMİZ"
```
Expected: `TEMİZ` (hard exclusion yalnız export'a atfedilmeli — Codex Turn-1 #2).

- [ ] **Step 4: Commit yok.** Devam.

---

## Task 5: Adım 4-6 — İki Hakem (mode-aware) + Sentez + Push-back

**Files:**
- Modify: `~/.claude/commands/security-review-claude-codex.md`

Spec bölüm karşılığı: **Adım 4 (iki bağımsız hakem + reviewer-status matrisi) / Adım 5 (güvenlik sentezi) / Adım 6 (push-back)** (spec satır ~240-370).

- [ ] **Step 1: Adım 4-6'yı yaz (spec'ten çeviri)**

- **Adım 4:** güvenlik kategori checklist'i (6 grup); 4a fresh subagent (general-purpose); 4b Codex **mode-aware** (diff→`adversarial-review --base $BASE_SHA --cwd "$SCAN_ROOT"` + post-call HEAD assertion; full/path→`task --fresh --cwd "$SCAN_ROOT"`); **cwd override notu** (blok byte-identical, Adım 4b override; acceptance check); full-mode breadth honesty; reviewer-status matrisi + **coverage_gap pre-matris guard** (coverage_gap=true → Şablon D terminal; matris yalnız coverage_gap=false'ta).
- **Adım 5:** severity normalize + **güvenlik floors** (evidence_gap≥medium; auth-bypass/tenant-leak/real-secret/RCE/SQLi→critical/high); agreement-signal; disposition ledger; değer maskeleme.
- **Adım 6:** push-back **TEMKİNLİ** (false positive kabul, false negative değil); hakemler-arası uzlaştırma.

- [ ] **Step 2: TEST — matris + floors + guard**

```bash
rg -c 'Reviewer-status matrisi|coverage_gap.*pre-matris|evidence_gap.*medium|TEMKİNLİ|both-agree|disposition ledger' ~/.claude/commands/security-review-claude-codex.md
```
Expected: ≥ 5 eşleşme (matris, pre-matris guard, floor, push-back, agreement-signal, ledger).

- [ ] **Step 3: TEST — cwd override SCAN_ROOT (Codex plan-review PA-1; ZORUNLU hard gate)**

Adım 4b'nin **gerçek Codex call'u** marker bloğu DIŞINDA `$SCAN_ROOT` kullanmalı; blok-dışı gerçek `$PROJECT_ROOT` invocation OLMAMALI (canonical `--cwd "$PROJECT_ROOT"` yalnız marker bloğu İÇİNDE + binding prose açıklamasında kalır):

```bash
F=~/.claude/commands/security-review-claude-codex.md
NB=$(awk '/CODEX-CALL-PROTOCOL:BEGIN/{p=1;next} /CODEX-CALL-PROTOCOL:END/{p=0;next} !p' "$F")
ok=1
printf '%s' "$NB" | grep -qE 'node "\$COMPANION".*adversarial-review.*--cwd "\$SCAN_ROOT"' || { echo "EKSİK: diff STEP_B GERÇEK node invocation --cwd \$SCAN_ROOT"; ok=0; }
printf '%s' "$NB" | grep -qE 'node "\$COMPANION".*task --fresh.*--cwd "\$SCAN_ROOT"'        || { echo "EKSİK: full/path STEP_A GERÇEK node invocation --cwd \$SCAN_ROOT"; ok=0; }
printf '%s' "$NB" | grep -nE 'node "\$COMPANION".*--cwd "\$PROJECT_ROOT"' && { echo "FAIL: blok-DIŞI gerçek PROJECT_ROOT invocation"; ok=0; }
[ "$ok" -eq 1 ] && echo "cwd-override PASS" || echo "cwd-override FAIL"
```
Expected: `cwd-override PASS`. **Pozitif check'ler gerçek `node "$COMPANION"` invocation satırına anchor'lı (Codex PA-1 Turn-2)** — Çekirdek Fark'taki binding *açıklaması* (`diff→adversarial-review … --cwd "$SCAN_ROOT"` gibi prose) tek başına geçiremez; Adım 4b'de gerçek `node "$COMPANION" … --cwd "$SCAN_ROOT"` call satırı şart. Blok-dışı gerçek `$PROJECT_ROOT` invocation YOK.

- [ ] **Step 4: Commit yok.** Devam.

---

## Task 6: Adım 7-9 — Kayıt + Active Layer + Commit/İki-Katmanlı Gate/Şablonlar/Teardown

**Files:**
- Modify: `~/.claude/commands/security-review-claude-codex.md`

Spec bölüm karşılığı: **Adım 7 (rapor) / Adım 8 (active layer) / Adım 9 (commit + iki-katmanlı chain gate + Şablon A/B/C/D + teardown)** (spec satır ~370-510).

- [ ] **Step 1: Adım 7-9'u yaz (spec'ten çeviri)**

- **Adım 7:** sentez raporu template (`docs/security-reviews/<DATE>-<SLUG>.md`); coverage_mode/codex_breadth/coverage_gap/secret-exclusion/scan-substrate alanları; ledger; Claude raw appendix; Codex raw link.
- **Adım 8:** active layer (critical+high → Open Problems + Notes For Claude, kullanıcı onayı, Codex yazmaz).
- **Adım 9:** **0. no-review branch** → **0.5 coverage-gap → Şablon D** → commit (arşiv, `git add -- <paths>`, push YOK) → **iki-katmanlı chain gate** (security-risk override + dual-review override, asla birleşmez, non-directive ton) → **Şablon A/B/C/D** → **izolasyon teardown** (diff worktree remove / full-path `rm -rf` export; EN SON).

- [ ] **Step 2: TEST — 4 şablon + iki override + non-directive**

```bash
rg -c '#### Şablon [ABCD]' ~/.claude/commands/security-review-claude-codex.md     # = 4 beklenir
rg -c 'security-risk override|dual-review override|non-directive|izolasyon teardown' ~/.claude/commands/security-review-claude-codex.md
```
Expected: ilk komut **4**; ikinci > 0 (iki override + non-directive + teardown).

- [ ] **Step 3: Commit yok.** Devam.

---

## Task 7: Sözleşme/Drift/Decisions/Out-of-Scope (6-way prose ile)

**Files:**
- Modify: `~/.claude/commands/security-review-claude-codex.md`

Spec bölüm karşılığı: **Değişecek Dosyalar / Drift Sözleşmesi / Sözleşme Notları / Decisions Log / Out-of-Scope / Implementation Notes** (spec satır ~525+).

- [ ] **Step 1: Sözleşme bölümlerini yaz**

- **Drift Sözleşmesi (6-way):** 6 komut listesi (security-review-claude-codex dahil); Check A (5 diff hepsi 0); Check B ("altı dosyada" 8 token); "biri değişirse diğeri de" = 6 komut; mode→STEP binding (her iki STEP).
- **Sözleşme Notları:** manuel mod, docs-gate, Codex araç ayrımı, companion path (dinamik `find`), active-task sahipliği (değiştirmez), Codex read-only, vault closure'a.

- [ ] **Step 2: TEST — 6-way prose, "beş/5" kalıntısı yok**

```bash
rg -c '6-way|altı dosya|6 komut' ~/.claude/commands/security-review-claude-codex.md            # > 0
rg -n '5-way|beş dosya|beş komut|5 komut' ~/.claude/commands/security-review-claude-codex.md && echo "KALINTI-DÜZELT" || echo "TEMİZ"
```
Expected: birinci > 0; ikinci `TEMİZ`.

- [ ] **Step 3: Commit yok.** Devam.

---

## Task 8: 6-Way Drift Verify (yeni dosya dahil) — Check A + Check B

**Files:** (doğrulama — değişiklik yok)

- [ ] **Step 1: Check A — 6 dosyanın bloğu byte-identical**

```bash
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex review-claude-codex security-review-claude-codex; do
  awk '/CODEX-CALL-PROTOCOL:BEGIN/{p=1} p{print} /CODEX-CALL-PROTOCOL:END/{p=0}' ~/.claude/commands/$f.md | sha256sum
done | sort -u
```
Expected: **tek satır hash** = `<CANONICAL_HASH>`. Birden fazla → yeni dosyanın bloğu drift'li (Task 3 Step 3'e dön, /tmp'den yeniden yapıştır).

- [ ] **Step 2: Check B — tripwire token'ları 6 dosyada**

```bash
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex review-claude-codex security-review-claude-codex; do
  blk=$(awk '/CODEX-CALL-PROTOCOL:BEGIN/{p=1} p{print} /CODEX-CALL-PROTOCOL:END/{p=0}' ~/.claude/commands/$f.md)
  for t in 'codex-companion.mjs' 'git rev-parse' 'AGENTS.md' 'timeout 480s' '124' 'Claude-only devam et' 'Tekrar dene' 'Komutu durdur'; do
    printf '%s' "$blk" | grep -qF "$t" || echo "EKSİK: $f → $t"
  done
done; echo "Check B bitti"
```
Expected: hiç `EKSİK` satırı yok → "Check B bitti".

- [ ] **Step 3: Commit yok.** Devam.

---

## Task 9: 5 Mevcut Sibling'de Mekanik 6-Way Prose Bump (marker bloğuna DOKUNMA)

**Files:**
- Modify: `spec-claude-codex.md`, `write-plan-claude-codex.md`, `execute-plan-claude-codex.md`, `simplify-claude-codex.md`, `review-claude-codex.md` (hepsi marker DIŞI)

- [ ] **Step 1: Her dosyada "5→6" prose güncelle (marker bloğunun DIŞINDA)**

Her dosyada: "5-way"→"6-way", "beş dosya(da)"→"altı dosya(da)", "5/beş komut(ta/u)"→"6/altı komut", Check A matrisine `spec vs security-review diff=0` ekle, aile listesine `security-review-claude-codex.md (ayna)` ekle. **Marker bloğunun (`BEGIN`..`END`) İÇİNE dokunma** — Check A'yı kırar.

- [ ] **Step 2: TEST — blok hâlâ byte-identical (hiçbir bloğa dokunulmadı)**

```bash
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex review-claude-codex security-review-claude-codex; do
  awk '/CODEX-CALL-PROTOCOL:BEGIN/{p=1} p{print} /CODEX-CALL-PROTOCOL:END/{p=0}' ~/.claude/commands/$f.md | sha256sum
done | sort -u
```
Expected: **tek satır hash** = `<CANONICAL_HASH>` (prose bump bloğa sızmadı).

- [ ] **Step 3: TEST — stale "5/beş" prose kalmadı (6 dosya)**

```bash
rg -n '5-way|beş dosya|beş komut|5 komut|beş komutta|5 komutta' ~/.claude/commands/{spec,write-plan,execute-plan,simplify,review,security-review}-claude-codex.md && echo "KALINTI-DÜZELT" || echo "TEMİZ"
```
Expected: `TEMİZ` (tarihsel "5-way → 6-way geçiş" anlatımları hariç — onlar geçişi tarif eder, kalıntı değil; gözle ayırt et).

- [ ] **Step 4: Commit yok** (repo-dışı). Devam.

---

## Task 10: Chain-Ref Sweep `/security-review` → `/security-review-claude-codex`

**Files:**
- Modify: `execute-plan-claude-codex.md`, `simplify-claude-codex.md`, `review-claude-codex.md`, `init.md`

- [ ] **Step 1: Mevcut aktif referansları bul**

```bash
rg --pcre2 -n '/security-review(?!-claude-codex)' ~/.claude/commands/{execute-plan-claude-codex,simplify-claude-codex,review-claude-codex,init}.md
```
Beklenen: review'da ~8, execute'ta birkaç, simplify'da birkaç, init'te 1 (spec Değişecek Dosyalar #5-8 ile karşılaştır).

- [ ] **Step 2: Aktif zincir referanslarını REPLACE et**

Her aktif "sonraki adım / chain / auto" `/security-review` referansını `/security-review-claude-codex` yap. **KORU:** tarihsel/aile-listesi etiketleri ve deprecated stub referansları (varsa "eski /security-review (deprecated)" gibi). Hit-by-hit incele (memory: "aile rename'inde TÜM zincir referanslarını süpür, ama deprecated/tarihsel etiketleri koru").

- [ ] **Step 3: TEST — aktif referans kalmadı**

```bash
rg --pcre2 -n '/security-review(?!-claude-codex)' ~/.claude/commands/{execute-plan-claude-codex,simplify-claude-codex,review-claude-codex,init}.md
```
Expected: **boş** (veya yalnız bilinçli korunan deprecated/tarihsel etiketler — her kalanı gerekçesiyle doğrula).

- [ ] **Step 4: Commit yok.** Devam.

---

## Task 11: Eski `security-review.md` → Deprecated Stub

**Files:**
- Rewrite: `~/.claude/commands/security-review.md`

- [ ] **Step 1: Stub içeriğini yaz**

Frontmatter `description: "[DEPRECATED] use /security-review-claude-codex"` + kısa gövde: neden deprecate (çift bağımsız hakem + mode-aware Codex + iki-katmanlı gate); kullanıcı `/security-review-claude-codex` çağırmalı. (Pattern: mevcut `review.md`/`simplify.md` deprecated stub'ları.)

- [ ] **Step 2: TEST — stub parse + DEPRECATED işareti**

```bash
ruby -ryaml -e 'd=YAML.load(File.read(ARGV[0]).split(/^---$/)[1]); abort("FAIL") unless d.is_a?(Hash) && d["description"]=~/DEPRECATED/' ~/.claude/commands/security-review.md && echo PASS
```
Expected: `PASS`.

- [ ] **Step 3: Commit yok.** Devam.

---

## Task 12: Tam Doğrulama Pass + Smoke

**Files:** (doğrulama)

- [ ] **Step 1: Tüm doğrulama bloklarını koş**

```bash
# (a) 6-way Check A
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex review-claude-codex security-review-claude-codex; do
  awk '/CODEX-CALL-PROTOCOL:BEGIN/{p=1} p{print} /CODEX-CALL-PROTOCOL:END/{p=0}' ~/.claude/commands/$f.md | sha256sum; done | sort -u
# (b) stale chain refs
rg --pcre2 -n '/security-review(?!-claude-codex)' ~/.claude/commands/{execute-plan-claude-codex,simplify-claude-codex,review-claude-codex,init}.md
# (c) stale drift prose
rg -n '5-way|beş dosya|beş komut|5 komut' ~/.claude/commands/{spec,write-plan,execute-plan,simplify,review,security-review}-claude-codex.md
# (d) frontmatter smoke (yeni + stub)
ruby -ryaml -e 'ARGV.each{|f| d=YAML.load(File.read(f).split(/^---$/)[1]); puts "#{f}: #{d.is_a?(Hash)}"}' ~/.claude/commands/security-review-claude-codex.md ~/.claude/commands/security-review.md
# (e) Check B — tripwire token × 6 FRESH + fail-closed (Codex plan-review PA-3; Task 8 değil, son pass'te tekrar)
b_fail=0
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex review-claude-codex security-review-claude-codex; do
  blk=$(awk '/CODEX-CALL-PROTOCOL:BEGIN/{p=1} p{print} /CODEX-CALL-PROTOCOL:END/{p=0}' ~/.claude/commands/$f.md)
  for t in 'codex-companion.mjs' 'git rev-parse' 'AGENTS.md' 'timeout 480s' '124' 'Claude-only devam et' 'Tekrar dene' 'Komutu durdur'; do
    printf '%s' "$blk" | grep -qF "$t" || { echo "EKSİK: $f → $t"; b_fail=1; }
  done
done
[ "$b_fail" -eq 0 ] && echo "Check B PASS" || echo "Check B FAIL"
```
Expected: (a) tek hash; (b) boş/korunan; (c) boş/tarihsel; (d) iki dosya `true`; (e) `Check B PASS` (hiç `EKSİK` yok — fail-closed). Audit log'a yazılan Check B sonucu artık **bu fresh pass'ten** gelir (Task 8 değil).

- [ ] **Step 2: Sonuçları execute log'a yaz**

Check A/B + sweep + smoke sonuçlarını `docs/reviews/codex/2026-06-01-security-review-claude-codex-command-execute.md`'ye kaydet (final review öncesi — memory: deferred-commit tuzağı; gate sonuçlarını log'a yaz).

- [ ] **Step 3: Commit yok** (audit commit Task 13). Devam.

---

## Task 13: Audit Commit (docs-only) + Restart Notu

**Files:**
- Commit: `docs/active/<SLUG>/` (Adım 18'de yaratıldıysa), `docs/reviews/codex/2026-06-01-security-review-claude-codex-command-execute.md`

- [ ] **Step 1: Yalnız docs stage et (komut dosyaları repo-DIŞI, commit EDİLMEZ)**

```bash
git add -- docs/active docs/reviews/codex/2026-06-01-security-review-claude-codex-command-execute.md
git status --short    # yalnız docs/ görünmeli; ~/.claude/commands/* GÖRÜNMEZ (repo dışı)
```
Expected: yalnız `docs/` altı staged.

- [ ] **Step 2: Commit (docs: prefix, push YOK)**

```bash
git commit -m "docs: security-review-claude-codex command build (docs audit; command files external)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

- [ ] **Step 3: Restart notu**

Kullanıcıya bildir: `/security-review-claude-codex` **Claude Code restart sonrası** skill listesinde görünür/aktiftir (smoke load+parse geçti, tam invoke restart ister). Backup'lar `~/.claude/commands/*.bak-<ts>` — rollback gerekirse geri kopyala.

---

## Task 14: Vault Promotion Reminder (closure P1 — execution KAPSAMINDA DEĞİL)

**Files:** (yalnız hatırlatma — execution'da YAPILMAZ)

- [ ] **Step 1: Closure hatırlatması**

`/finish-branch` closure'da (execution'da DEĞİL): vault decision doc `decisions/2026-05-26-...hardening`'i 5-komut → **6-komut** pattern'e genişlet + `claude-code-workflow`/`codex-entegrasyonu`/`index`/`log` güncelle, `otomaix-brain-private` commit+push. **Codex vault'a YAZMAZ.** (memory: closure'da vault promotion zorunlu — "tooling kararı, vault'a girmez" YANLIŞ.)

---

## Self-Review Notu (plan yazımı sonrası)

- **Spec coverage:** Spec'in her Adım'ı (1-9) + Drift + Decisions bir task'a eşleşiyor (Task 2-7 komut içeriği, Task 8-12 drift/sweep/deprecate/verify). ✓
- **Placeholder:** Komut içerik task'ları spec-section mapping + per-task grep verification taşır (prose deliverable; spec content blueprint). Mekanik task'lar (extraction/bump/sweep) tam komut içerir. ✓
- **Type/isim tutarlılığı:** `$SCAN_ROOT`/`$EXPORT_DIR`/`$REVIEW_WT`/`<CANONICAL_HASH>`/coverage_mode/Şablon A-D isimleri spec ile birebir. ✓

---

**Sonraki adım:** `/execute-plan-claude-codex docs/plans/2026-06-01-security-review-claude-codex-command.md`
