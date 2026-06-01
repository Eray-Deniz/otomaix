---
title: review-claude-codex.md Implementation Plan
status: plan-approved
date: 2026-06-01
source_spec: docs/specs/2026-06-01-review-claude-codex-command.md
source_spec_unapproved_override: false
noisy_review_override: false
unresolved_high_severity_override: false
codex_plan_review_status: approved
codex_plan_review_iterations: 2
codex_plan_targeted_fixes: 5
codex_plan_review_log: docs/reviews/codex/2026-06-01-review-claude-codex-command-plan.md
---

# review-claude-codex Implementation Plan

> **For agentic workers:** Bu plan `/execute-plan-claude-codex` üzerinden uygulanmalıdır. Skill chain'in auto `finishing-a-development-branch`/`using-git-worktrees` önerileri ignore — akış: `/execute-plan-claude-codex` → `/simplify-claude-codex` → `/review-claude-codex` → `/security-review` → `/finish-branch`.

**Goal:** Spec `docs/specs/2026-06-01-review-claude-codex-command.md` (spec-approved) implement et — yeni custom slash command `~/.claude/commands/review-claude-codex.md` yarat (mevcut tek-aktörlü `/review`'ın claude-codex aile eşi: iki bağımsız hakem + sentez), aileyi 4-way → **5-way** drift contract'a taşı, `review.md`'yi deprecated stub'a çevir.

**Architecture:** Atomic-one-pass, **hybrid section-append** (Adım 6 Codex + Adım 5 Claude yakınsaması): spec bölümleri byte-near append; yalnız frontmatter/binding/stub self-referans freehand. **İki dosya kümesi:** (1) Global slash command dosyaları `~/.claude/commands/*.md` — bu repo'nun (`/root/otomaix`) DIŞINDA, repo commit'i DEĞİL; her kritik task öncesi `cp X /tmp/X.bak`, FAIL'de rollback. (2) Repo-local audit `docs/plans/...-command.md` + `docs/reviews/codex/...-command-plan.md` (+ spec orada) — normal repo commit (`docs:`). Canonical `CODEX-CALL-PROTOCOL` bloğu `spec-claude-codex.md`'den **byte-exact** kopyalanır (Task 3 erken); review yalnız `<STEP_B>`'yi kullanır ama blok bütün kopyalanır, `<STEP_A> unused` notu **marker DIŞINDA**. 5-way propagation yalnız yeni komut byte-exact doğrulandıktan SONRA (Task 12). `/review` → `/review-claude-codex` sweep hit-by-hit (Task 13, blind sed YASAK). review.md stub'a **en son** (Task 14). Final drift Check A (5-way: 4 diff=0) + Check B (8 token × 5 dosya) zorunlu (Task 15).

**Tech Stack:** Markdown frontmatter (YAML), bash (awk/grep/diff drift verification), git (worktree mekanizması spec içeriği; plan verification'ı normal git).

**Verification model:** Markdown slash command implementasyonu — production kod DEĞİL. Her task `tdd: skip`. Verification = drift Check A (5-way diff=0) + Check B (8 tripwire token × 5 dosya) + structural integrity (BEGIN/END marker count, frontmatter parse, Adım numaralandırma, canonical token tutarlılığı) + spec-section diff + best-effort runtime smoke (load+parse). Memory `project-claude-codex-command-execution`: deliverable repo-dışı, `/simplify` uygulanmaz, audit commit docs-only.

**Source-of-truth referansı:** Spec (`docs/specs/2026-06-01-review-claude-codex-command.md`) yetkili kaynak. "Spec Adım N'i birebir append et" diyen task'lar oraya yönlendirir (DRY). **Drift önleyici verification pattern (her append task sonunda zorunlu — bireysel task'larda inline tekrarlanmaz, bu blok referans alınır):**

```bash
SPEC=docs/specs/2026-06-01-review-claude-codex-command.md
CMD=~/.claude/commands/review-claude-codex.md
# Spec'ten ilgili Adım bölümünü ham metin çıkar:
sed -n '/^## Adım <N>:/,/^## Adım <NEXT>/{/^## Adım <NEXT>/!p}' "$SPEC" > /tmp/spec-section-<N>.txt
sed -n '/^## Adım <N>:/,/^## Adım <NEXT>/{/^## Adım <NEXT>/!p}' "$CMD"  > /tmp/cmd-section-<N>.txt
diff /tmp/spec-section-<N>.txt /tmp/cmd-section-<N>.txt
```

Diff manuel inspect — **kabul edilebilir fark:** yalnız self-referans terminoloji yumuşatma (`spec'in Adım X` → `Adım X`) veya path örneği. **Kabul edilemez:** kural eksikliği, sıra değişikliği, format zorunluluk gevşemesi, anlamsal paraphrase. Pure paraphrase YASAK.

---

## Task 1: Pre-flight Inventory ve Snapshot/Backup

**tdd: skip** (read-only inventory + /tmp backup; repo dosyası değişmiyor)

**Files (read only):**
- `~/.claude/commands/spec-claude-codex.md` (canonical CODEX-CALL-PROTOCOL + Sözleşme/Drift text)
- `~/.claude/commands/write-plan-claude-codex.md` (Drift text)
- `~/.claude/commands/execute-plan-claude-codex.md` (Drift text + `/review` references)
- `~/.claude/commands/simplify-claude-codex.md` (Drift text + `/review` references)
- `~/.claude/commands/review.md` (stub'lanacak eski komut — referans)
- `docs/specs/2026-06-01-review-claude-codex-command.md` (target spec)
- `docs/plans/2026-05-31-simplify-claude-codex-command.md` (yapı şablonu)

- [ ] **Step 1: BEGIN/END marker integrity on canonical**

Run: `grep -c "CODEX-CALL-PROTOCOL:BEGIN\|CODEX-CALL-PROTOCOL:END" ~/.claude/commands/spec-claude-codex.md`
Expected: `2` (1 BEGIN + 1 END). Aksi halde canonical kirli → plan durdur.

- [ ] **Step 2: Tripwire 8 token presence on canonical (extract + grep)**

Run:
```bash
awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' ~/.claude/commands/spec-claude-codex.md > /tmp/codex-call-protocol.snapshot
wc -l /tmp/codex-call-protocol.snapshot
for token in "codex-companion.mjs" "git rev-parse" "AGENTS.md" "timeout 480s" "124" "Claude-only devam et" "Tekrar dene" "Komutu durdur"; do
  echo "$token: $(grep -c -F "$token" /tmp/codex-call-protocol.snapshot)"
done
```
Expected: snapshot 40+ satır; her token ≥ 1. Sıfır olan varsa canonical kirli → durdur. (Snapshot audit içindir; Task 3 inline recompute eder — crash-safe.)

- [ ] **Step 3: Mevcut drift contract durumu (4-way text inventory — Task 12 katalog)**

Run:
```bash
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex; do
  echo "--- $f ---"
  grep -n "dört komut\|dört dosya\|4-way\|biri değişirse\|Check A\|Check B\|spec vs " ~/.claude/commands/$f.md | head -20
done
```
Expected: 4-way numeral/text katalog. Her dosyada drift section mevcut. Catalog'u not al — Task 12'de "dört"→"beş" + Check A matrisi (+1 diff) + Check B "5 dosya" için kullanılacak.

- [ ] **Step 4: `/review` references in execute + simplify (Task 13 katalog)**

Run (robust pattern — yalnız `/review-claude-codex`'i dışlar; `/security-review` İÇEREN satırları GİZLEMEZ — T1-1):
```bash
echo "--- execute-plan ---"; grep -nE "/review([^a-zA-Z0-9_/-]|$)" ~/.claude/commands/execute-plan-claude-codex.md
echo "--- simplify ---"; grep -nE "/review([^a-zA-Z0-9_/-]|$)" ~/.claude/commands/simplify-claude-codex.md
```
`/review([^a-zA-Z0-9_/-]|$)` bare `/review` komut token'ını (boşluk/paren/punct/satır-sonu ardından) yakalar. **Eşleşmeyenler:** `/review-claude-codex` (`-`), `/security-review` (`/review` substring'i yok), ve `/reviews` / `/reviewer` / `docs/reviews/...` path'leri (alnum/`/`/`_`/`-` continuation hariç — Codex T2-1 overmatch fix). **`grep -v "/security-review"` KULLANMA** — aktif zincir satırları (örn. "Sonraki adım: /review (sonra /security-review)") hem `/review` hem `/security-review` içerir; o satırı gizlersen düzeltilmesi gereken canlı referansı kaçırırsın (Codex T1-1). Her hit Task 13'te classify: active "sonraki adım/zincir" reference (→ replace) vs historical/decisions-log (→ keep).

- [ ] **Step 5: review.md eski içerik referansı**

Run: `head -20 ~/.claude/commands/review.md`
Expected: Eski tek-aktör review komutu (Superpowers requesting-code-review). Task 14 stub içeriği için "neden değişti" notu buradan.

- [ ] **Step 6: Backup repo-dışı 5 dosya (rollback path — repo commit korumuyor)**

Run:
```bash
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex review; do
  cp ~/.claude/commands/$f.md /tmp/$f.md.bak
done
ls -la /tmp/*.md.bak
```
Expected: 5 `.bak`, her biri non-zero. Rollback policy: Task 12/13/14'te FAIL → `cp /tmp/<name>.md.bak ~/.claude/commands/<name>.md`, ilgili task'a dön. Yeni `review-claude-codex.md` için backup yok (henüz yaratılmadı) → Task 11.5 FAIL'de rebuild-from-clean (Task 2'den).

- [ ] **Step 7: Yeni komut yokluğu + review.md eski hali teyidi**

Run:
```bash
[ -f ~/.claude/commands/review-claude-codex.md ] && echo "VAR (beklenmedik — resume?)" || echo "YOK (beklenen)"
grep -c "DEPRECATED" ~/.claude/commands/review.md
```
Expected: `review-claude-codex.md` YOK; review.md DEPRECATED içermiyor (`0`, henüz stub değil).

- [ ] **Step 8: No commit (inventory + /tmp backup only)**

---

## Task 2: review-claude-codex.md İskelet — Frontmatter + Görev + İnvariant + Mimari Yön + Akış + Codex Çağrı Noktaları + Teknik Kısıtlar

**tdd: skip**

**Files:**
- Create: `~/.claude/commands/review-claude-codex.md`
- Read: spec (Görev, İnvariant, Mimari Yön, 9 Adımlık Akış, Codex Çağrı Noktaları, Doğrulanmış Teknik Kısıtlar bölümleri)

- [ ] **Step 1: Frontmatter + Görev + İnvariant + Mimari Yön özeti**

Write to `~/.claude/commands/review-claude-codex.md`:
- Frontmatter: `description:` (örn. "İki bağımsız hakem [fresh Claude subagent + Codex adversarial-review] + sentez; eski /review'ın claude-codex aile eşi [custom, drift-check 5-way]") + `argument-hint: [BASE_REF]`.
- **Görev:** spec "Hedef" + "Rol modeli" özeti — iki bağımsız hakem, ana Claude sentez (kendi işini review etmez), kod-commit-gated DEĞİL (tek artefakt review raporu). Sonraki adım zinciri.
- **İnvariant:** spec "İnvariant" bölümünü birebir (docs-gate: arşiv ≠ gate; both-failed istisna Şablon C; single-reviewer chain-advance override; push YOK).
- **Mimari Yön özeti (1 paragraf):** çift bağımsız hakem; izolasyon = pinli worktree @ HEAD_SHA; severity 4-seviye ortak. (Spec'in tradeoff tablosu/dropped-alt KOMUTA GİRMEZ — o spec-only.)

- [ ] **Step 2: Akış Genel Bakış (9 adım) append**

Spec'in "9 Adımlık Akış" kod bloğunu birebir append et (9 satır + "Adım 0 YOK" notu).

- [ ] **Step 3: Codex Çağrı Noktaları tablosu append**

Spec'in "Codex Çağrı Noktaları" tablosunu (yalnız Adım 4b satırı) + altındaki "CODEX-CALL-PROTOCOL byte-exact kopya; STEP_A kullanılmaz" notunu birebir append et.

- [ ] **Step 4: Doğrulanmış Teknik Kısıtlar append**

Spec'in "Doğrulanmış Teknik Kısıtlar (codex-companion.mjs 1.0.4)" bölümünü birebir append et (4 madde: positionals→focusText, --base branch mode, --head yok → worktree, buildBranchComparison).

- [ ] **Step 5: Verify created**

Run: `grep -n "^## \|^# \|^description:" ~/.claude/commands/review-claude-codex.md | head -20`
Expected: frontmatter + Görev + İnvariant + Mimari Yön + Akış + Codex Çağrı Noktaları + Teknik Kısıtlar sıralı görünür.

- [ ] **Step 6: No commit**

---

## Task 3: Canonical CODEX-CALL-PROTOCOL Byte-Exact Kopya + Binding (STEP_A unused) + Downstream

**tdd: skip; CRITICAL — drift contract merkezi**

**Files:**
- Modify: `~/.claude/commands/review-claude-codex.md` (append after Teknik Kısıtlar)

- [ ] **Step 1: Binding/intro çerçevesini append (canonical bloğun ÖNÜ, marker DIŞI)**

Append (review-özgü binding):
````markdown

## Codex Çağrı Protokolü (Adım 4b)

Adım 4b'deki Codex çağrısı bu protokolü izler. Amaç: companion yoksa, Codex çöker/hata verir veya asılırsa komut **sessizce kırılmaz**.

> **Binding (review-claude-codex):** Tek çağrı noktası var. Eşleştirme:
> · `<STEP_B>` (`<CALL>` = `adversarial-review $SCOPE`) = **Adım 4b** (bağımsız ikinci hakem).
> · `<STEP_A>` (`<CALL>` = `task --fresh`) canonical protokolde TANIMLI ama **bu komutta KULLANILMAZ** (review'da pre-scan turu yok). Blok yine byte-identical kopyalanır (superset).
>
> Aşağıdaki `CODEX-CALL-PROTOCOL` bloğu **canonical** `spec-claude-codex` ile birebir aynıdır (drift-check 5-way: diff=0; bkz. Sözleşme Notları). Bloğu değiştirirsen canonical'ı, `write-plan-claude-codex`'i, `execute-plan-claude-codex`'i ve `simplify-claude-codex`'i de senkronla (5-way).

````
> **DİKKAT (Codex Adım 6 must-not-forget):** Yukarıdaki binding ve aşağıdaki downstream notu `<!-- CODEX-CALL-PROTOCOL:BEGIN -->` / `:END` marker'larının **DIŞINDA** kalmalı. STEP_A-unused cümlesi markerların içine sızarsa Check A byte-diff kırılır.

- [ ] **Step 2: Canonical bloğu byte-exact append (inline recompute — crash-safe)**

```bash
spec_markers=$(grep -c "CODEX-CALL-PROTOCOL:BEGIN\|CODEX-CALL-PROTOCOL:END" ~/.claude/commands/spec-claude-codex.md)
if [ "$spec_markers" -ne 2 ]; then echo "FAIL — spec marker count $spec_markers (≠2). Canonical kirli; durdur."; exit 1; fi
awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' ~/.claude/commands/spec-claude-codex.md >> ~/.claude/commands/review-claude-codex.md
echo "" >> ~/.claude/commands/review-claude-codex.md
```

- [ ] **Step 3: Downstream notunu append (canonical bloğun ARDI, marker DIŞI)**

Append:
````markdown

> **Downstream (review-claude-codex):** Adım 4b'de "Claude-only devam et" seçilirse → Codex hakem degrade; Adım 5 sentez yalnız subagent bulgularıyla; rapor Şablon B (`dual-review: false`, `codex_status` loglanır); chain-advance explicit override ister (Adım 9). (Reviewer-status matrisi Adım 4b'de tam tanımlı.)

````

- [ ] **Step 4: Byte-exact verification (CRITICAL gate)**

```bash
diff <(awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' ~/.claude/commands/spec-claude-codex.md) \
     <(awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' ~/.claude/commands/review-claude-codex.md)
echo "Exit: $?"
```
Expected: `Exit: 0`. FAIL → kopya bozuk, Task 3 baştan.

- [ ] **Step 5: Marker count + STEP_A-note placement guard**

```bash
grep -c "CODEX-CALL-PROTOCOL:BEGIN\|CODEX-CALL-PROTOCOL:END" ~/.claude/commands/review-claude-codex.md   # = 2 beklenir
# STEP_A-unused cümlesi marker bloğunun DIŞINDA mı? (blok içinde "kullanılmaz" geçmemeli)
awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' ~/.claude/commands/review-claude-codex.md | grep -c "KULLANILMAZ\|kullanılmaz"
```
Expected: marker count `2`; ikinci grep `0` (STEP_A notu blok dışında).

- [ ] **Step 6: No commit**

---

## Task 4: Adım 1 (Scope + Ref Terminolojisi) + Adım 2 (Dirty-Tree Bildirimi)

**tdd: skip**

**Files:**
- Modify: `~/.claude/commands/review-claude-codex.md`
- Read: spec (Adım 1, Adım 2)

- [ ] **Step 1: Adım 1 append**

Spec'in "Adım 1: Scope Belirleme + Ref Terminolojisi" bölümünü birebir append et (BASE_REF/BASE_SHA/HEAD_SHA/REVIEW_BASE_SHA tablosu + bash bloğu `git rev-parse --verify` + `git merge-base` + review aralığı gösterimi + `<SLUG>` türet+sanitize).

- [ ] **Step 2: Adım 2 append**

Spec'in "Adım 2: Dirty-Tree Bildirimi" bölümünü birebir append et (worktree-pinli olduğu için sızıntı yok notu + TREE_DIRTY/DIRTY_EXCLUDED_COUNT bash + 3-seçenek AskUserQuestion: commit-stash / bilerek-devam / durdur).

- [ ] **Step 3: Ref terminoloji + merge-base drift check**

```bash
grep -n "REVIEW_BASE_SHA\|merge-base\|rev-parse --verify\|\.\.\.HEAD\|\.\.HEAD" ~/.claude/commands/review-claude-codex.md
```
Expected: `REVIEW_BASE_SHA = git merge-base`; subagent için `REVIEW_BASE_SHA..HEAD_SHA` (iki uç pinli). Çıplak `BASE..HEAD` (iki-nokta, divergence riskli) YOK.

- [ ] **Step 4: Drift-prevention diff pattern (header bloğu) Adım 1, Adım 2 için koş** → kabul/red.

- [ ] **Step 5: No commit**

---

## Task 5: Adım 3 (Bağlam + Requirement Snapshot + Log Setup + Pinli Worktree)

**tdd: skip; CRITICAL — worktree mekanizması (precedent'siz) + requirement snapshot**

**Files:**
- Modify: `~/.claude/commands/review-claude-codex.md`
- Read: spec (Adım 3)

- [ ] **Step 1: Adım 3 append**

Spec'in "Adım 3: Bağlam Topla + Log Setup" bölümünü birebir append et. KRİTİK içerik (Codex must-not-forget):
- **Gereksinim snapshot'ı:** spec/plan tam metni → `<REQUIREMENT_SNAPSHOT>` → **iki hakem prompt'una birebir aynı gömülür** (özet DEĞİL); provenance (path/committed-dirty/hash) rapora.
- `git diff REVIEW_BASE_SHA..HEAD_SHA --stat` (ana repo, SHA mutlak).
- Log setup: `mkdir -p docs/reviews/codex` + DATE/LOG_PREFIX/ATTEMPT + CODEX_LOG dosya yaratımı (her durumda var olsun).
- **Pinli review worktree:** `REVIEW_WT="$(mktemp -d)/review-wt"; git worktree add --detach "$REVIEW_WT" "$HEAD_SHA"` + 5 madde (HEAD pin, temiz ağaç, AGENTS.md committed, **teardown ZORUNLU EN SON+abort**, raporlar ana repo'ya).

- [ ] **Step 2: Worktree + snapshot presence check**

```bash
grep -n "git worktree add --detach\|REVIEW_WT\|REQUIREMENT_SNAPSHOT\|mktemp" ~/.claude/commands/review-claude-codex.md
```
Expected: worktree add bash + REVIEW_WT + REQUIREMENT_SNAPSHOT tanımı görünür.

- [ ] **Step 3: Teardown timing notu var mı (precedent'siz — zayıflatılmasın)**

```bash
grep -n "EN SON\|terminal exit\|abort\|teardown" ~/.claude/commands/review-claude-codex.md
```
Expected: "teardown EN SON / terminal exit veya abort" notu Adım 3'te (kurulum) + Adım 9'da (icra) görünür (Adım 9 Task 9'da).

- [ ] **Step 4: Drift-prevention diff pattern Adım 3 için koş** → kabul/red.

- [ ] **Step 5: No commit**

---

## Task 6: Adım 4 (İki Bağımsız Hakem — 4a Subagent + 4b Codex + Reviewer-Status Matrisi)

**tdd: skip; CRITICAL — bağımsızlık invariant + precedent'siz reviewer-status matrisi**

**Files:**
- Modify: `~/.claude/commands/review-claude-codex.md`
- Read: spec (Adım 4 tümü)

- [ ] **Step 1: Adım 4 intro + 4a append**

Spec'in "Adım 4: İki Bağımsız Hakem" intro (BAĞIMSIZLIK invariant; paralel yalnız hız; reviewer-A çıktısı B'ye beslenmez; ikisi `$REVIEW_WT`'de) + "4a) Fresh Claude Subagent" (subagent type: code-reviewer tercih / general-purpose fallback persona aynı; **requesting-code-review skill YÜKLENMEZ** Decision 23; `git -C $REVIEW_WT diff REVIEW_BASE_SHA..HEAD_SHA`; subagent prompt — KAPSAM + KONTROL ET + severity 4-seviye + INJECTION HARDENING + `<REQUIREMENT_SNAPSHOT>`) bölümünü birebir append et.

- [ ] **Step 2: 4b Codex append**

Spec'in "4b) Codex Adversarial Review" bölümünü birebir append et (worktree HEAD pin açıklaması — eski pre-call guard race'i; SCOPE=`--base $BASE_SHA`; `--cwd $REVIEW_WT`; prompt `<REQUIREMENT_SNAPSHOT>` FULL embedded; stdout verbatim + $CODEX_LOG append; cannot-verify daraltma global-vs-finding-local; degradation → Şablon B + $CODEX_LOG'a degradation notu).

- [ ] **Step 3: Reviewer-status matrisi append (precedent'siz — Codex must-not-forget)**

Spec'in "Reviewer-status matrisi (Codex T2-3)" bölümünü birebir append et (4 satırlık tablo: dual/single-claude/single-codex/no-review; claude_status + codex_status; Claude subagent hatası dalı; single-reviewer simetrik muamele).

- [ ] **Step 4: Bağımsızlık + matris + snapshot drift check**

```bash
grep -n "BAĞIMSIZLIK\|reviewer-A çıktısını reviewer-B\|REQUIREMENT_SNAPSHOT\|requesting-code-review\|claude_status\|no-review" ~/.claude/commands/review-claude-codex.md
```
Expected: bağımsızlık invariant; her iki prompt'ta `<REQUIREMENT_SNAPSHOT>` (2 hit, identical); `requesting-code-review` YÜKLENMEZ notu; matris 4 durumu.

- [ ] **Step 5: Snapshot byte-identical iki prompt check (T3-1 koruması)**

```bash
grep -c "REQUIREMENT_SNAPSHOT" ~/.claude/commands/review-claude-codex.md
```
Expected: ≥ 3 (Adım 3 tanım + 4a prompt + 4b prompt). `<spec/plan özet>` gibi summary placeholder YOK:
```bash
grep -c "spec/plan özet\|<varsa içerik>" ~/.claude/commands/review-claude-codex.md
```
Expected: `0`.

- [ ] **Step 6: Drift-prevention diff pattern Adım 4 için koş** → kabul/red.

- [ ] **Step 7: No commit**

---

## Task 7: Adım 5 (Sentez + Disposition Ledger) + Adım 6 (Push-back)

**tdd: skip; CRITICAL — disposition ledger (precedent'siz, bağımsızlık koruması)**

**Files:**
- Modify: `~/.claude/commands/review-claude-codex.md`
- Read: spec (Adım 5, Adım 6)

- [ ] **Step 1: Adım 5 append**

Spec'in "Adım 5: Sentez (agreement-signal)" bölümünü birebir append et (6 madde: severity normalize + fallback only-off-script; dedupe; **agreement-signal both-agree/single-source**; severity uzlaştırma; dürüst REVIEW_BASE_SHA gösterimi; **disposition ledger** — her ham bulgu id/source/raw-sev/final-sev/disposition/gerekçe, sessiz drop yok + kategorize sunum + etiket).

- [ ] **Step 2: Adım 6 append**

Spec'in "Adım 6: Push-back Mantığı" bölümünü birebir append et (teknik dayanak / kapat / açık kal; hakemler-arası uzlaştırma).

- [ ] **Step 3: Ledger + agreement-signal presence check**

```bash
grep -n "agreement-signal\|both-agree\|single-source\|[Dd]isposition\|ledger\|sessiz drop" ~/.claude/commands/review-claude-codex.md
```
Expected: agreement-signal + both-agree/single-source + disposition ledger (id/source/disposition) + "sessiz drop yok".

- [ ] **Step 4: Drift-prevention diff pattern Adım 5, Adım 6 için koş** → kabul/red.

- [ ] **Step 5: No commit**

---

## Task 8: Adım 7 (Kayıt + Rapor Template + Ledger Section) + Adım 8 (Active Task Layer)

**tdd: skip**

**Files:**
- Modify: `~/.claude/commands/review-claude-codex.md`
- Read: spec (Adım 7, Adım 8)

- [ ] **Step 1: Adım 7 append**

Spec'in "Adım 7: Kayıt" bölümünü birebir append et (sentez raporu `docs/reviews/<DATE>-<SLUG>.md` template — başlık `# Review (<dual|single-reviewer: claude|codex>)` status-bağımlı; header dual-review + claude_status/codex_status + workspace pinned + main tree + requirement snapshot provenance; severity bölümleri etiketli; **Disposition Ledger tablosu**; Sonuç; Raw Claude appendix; Codex raw link + audit asimetrisi notu).

- [ ] **Step 2: Adım 8 append**

Spec'in "Adım 8: Active Task Layer Entegrasyonu" bölümünü birebir append et (CURRENT.md oku; critical+high → Open Problems [medium/low DEĞİL]; review özeti → HANDOFF Notes For Claude; **Codex YAZMAZ, Claude kullanıcı onayıyla + mini doğrulama**; status değiştirmez).

- [ ] **Step 3: Rapor başlığı status-bağımlı check (T4-1 koruması)**

```bash
grep -n "# Review (" ~/.claude/commands/review-claude-codex.md
```
Expected: `# Review (<dual | single-reviewer: claude|codex>)` — hardcoded `# Review (dual)` YOK.

- [ ] **Step 4: Disposition ledger tablosu raporda var mı**

```bash
grep -n "Disposition Ledger\|merged-into\|kept" ~/.claude/commands/review-claude-codex.md
```
Expected: rapor template'inde Disposition Ledger tablosu (id/source/disposition).

- [ ] **Step 5: Drift-prevention diff pattern Adım 7, Adım 8 için koş** → kabul/red.

- [ ] **Step 6: No commit**

---

## Task 9: Adım 9 (No-Review Branch + Commit + Chain-Advance + Teardown + Şablon A/B/C)

**tdd: skip; CRITICAL — precedent'siz no-review branch + chain-advance gate + teardown EN SON**

**Files:**
- Modify: `~/.claude/commands/review-claude-codex.md`
- Read: spec (Adım 9 tümü)

- [ ] **Step 1: Adım 9 append (TAM SIRA korunmalı)**

Spec'in "Adım 9: Docs Commit Gate + Final Rapor" bölümünü birebir append et — KRİTİK SIRA:
1. Teardown sıralaması notu (EN SON; retry worktree korur).
2. **"0. No-review branch"** (her iki hakem fail → İLK kontrol; sentez raporu YOK, commit YOK, $CODEX_LOG "both reviewers failed", Şablon C, teardown, chain BLOKE).
3. Commit (dual VEYA single — arşiv; `git add -- docs/reviews/<DATE>-<SLUG>.md "$CODEX_LOG"`; `git add -A` YASAK).
4. **Chain-advance gate** (dual → serbest; non-dual → explicit override; **her iki status** prompt'ta; başarısız hakemi tekrar dene → Codex fail 4b / Claude fail 4a).
5. Final Rapor 3 Şablon (A dual / B single-reviewer / C no-review).
6. **Worktree teardown EN SON** (terminal exit veya abort; orphan koruması).
7. Bitiş notu (auto /finish-branch YOK).

- [ ] **Step 2: Sıra doğrulama — no-review branch FIRST, teardown LAST**

```bash
grep -n "No-review branch\|### Commit\|Chain-advance gate\|teardown (EN SON\|Bitiş" ~/.claude/commands/review-claude-codex.md
```
Expected (satır sırası): No-review branch → Commit → Chain-advance gate → (Şablon A/B/C) → teardown EN SON → Bitiş. No-review commit'ten ÖNCE; teardown chain-advance'ten SONRA.

- [ ] **Step 3: Şablon A/B/C presence + başlık**

```bash
grep -n "#### Şablon" ~/.claude/commands/review-claude-codex.md
```
Expected: 3 başlık — A (Dual review), B (Single-reviewer), C (No-review).

- [ ] **Step 4: Chain-advance simetri check (T3-2 koruması)**

```bash
grep -n "claude_status: <\|codex_status: <\|Başarısız hakemi tekrar dene\|herhangi bir non-dual" ~/.claude/commands/review-claude-codex.md
```
Expected: gate her iki status'u gösterir; "herhangi bir non-dual" + başarısız hakemi tekrar dene (4a/4b). Yalnız Codex'e özgü dil YOK.

- [ ] **Step 5: git add scope check (Codex must-not-forget)**

```bash
grep -n "git add" ~/.claude/commands/review-claude-codex.md
```
Expected: yalnız `git add -- docs/reviews/<DATE>-<SLUG>.md "$CODEX_LOG"`; `git add -A`/`git add .` YOK; `git add ~/.claude` YOK.

- [ ] **Step 6: Drift-prevention diff pattern Adım 9 için koş** → kabul/red.

- [ ] **Step 7: No commit**

---

## Task 10: Sözleşme Notları + Drift Sözleşmesi (5-way) — yeni komutta

**tdd: skip**

**Files:**
- Modify: `~/.claude/commands/review-claude-codex.md`
- Read: spec (Drift Sözleşmesi 5-way) + simplify-claude-codex.md (Sözleşme Notları format paraleli)

- [ ] **Step 1: Sözleşme Notları append**

Yeni komut için Sözleşme Notları yaz (simplify formatına paralel, review-özgü):
- **Manuel mod:** her aşamada (Adım 1 scope, Adım 2 dirty, Adım 6 push-back, Adım 8 active, Adım 9 commit + chain-advance) kullanıcı kararı.
- **Docs-gate (kod commit-gate YOK):** review raporu tek artefakt; dual-review gate = her iki hakem; degrade'de single-reviewer rapor + chain-advance override; both-failed → Şablon C (commit yok).
- **Codex araç ayrımı:** Adım 4b `adversarial-review $SCOPE` (read-only sandbox; `--cwd $REVIEW_WT`); foreground + dış `timeout 480s`. `<STEP_A>` (task --fresh) bu komutta KULLANILMAZ.
- **Companion path:** dinamik `find`.
- **Drift enforcement (canonical = spec-claude-codex):** 5 komut + Check A 5-way + Check B 8 token × 5 dosya + "biri değişirse diğeri de" 5'i sayar.
- **Skill workflow override:** `superpowers:requesting-code-review` YÜKLENMEZ (Decision 23; orchestration komutun kendisi); yalnız code-reviewer agent personası 4a'da.
- **Active task:** Codex yazmaz; Claude kullanıcı onayıyla critical+high → Open Problems/HANDOFF; otomatik mutation yok.
- **Codex read-only:** bulgu stdout; Claude $CODEX_LOG veya rapora işler.
- **Vault promotion bu komutta YAPILMAZ.**

- [ ] **Step 2: Drift Sözleşmesi (5-way) append**

Spec'in "Drift Sözleşmesi (5-way)" bölümünü birebir append et (5 komut listesi; Check A 4 diff hepsi 0; Check B 8 token × 5 dosya; "biri değişirse" 5 komut; STEP_A kullanılmaz ama byte-identical kopya notu).

- [ ] **Step 3: 5-way + Check A/B presence (yeni komutta)**

```bash
grep -n "5-way\|beş komut\|beş dosya\|spec vs review\|Check A\|Check B" ~/.claude/commands/review-claude-codex.md
```
Expected: 5-way; Check A'da `spec vs review diff=0` dahil 4 diff; Check B "beş dosya".

- [ ] **Step 4: Marker count final (review-claude-codex)** — `grep -c "...BEGIN\|...END"` → `2`.

- [ ] **Step 5: Toplam satır sayısı** — `wc -l ~/.claude/commands/review-claude-codex.md` → ~460-520 (spec tahmini).

- [ ] **Step 6: No commit**

---

## Task 11: Spec Section Diff Verification Matrix (hard gate — Task 12 öncesi)

**tdd: skip; CRITICAL — bireysel task diff'lerinin konsolide hard-stop'u**

**Files:**
- Read: spec + `~/.claude/commands/review-claude-codex.md`
- Write: `/tmp/spec-sections/*.txt`, `/tmp/cmd-sections/*.txt` (geçici)

- [ ] **Step 1: Sed range matrix — her Adım için spec'ten + komuttan extract**

```bash
SPEC=docs/specs/2026-06-01-review-claude-codex-command.md
CMD=~/.claude/commands/review-claude-codex.md
mkdir -p /tmp/spec-sections /tmp/cmd-sections
declare -A RANGES=(
  ["adim-1"]='/^## Adım 1:/,/^## Adım 2:/'
  ["adim-2"]='/^## Adım 2:/,/^## Adım 3:/'
  ["adim-3"]='/^## Adım 3:/,/^## Adım 4:/'
  ["adim-4"]='/^## Adım 4:/,/^## Adım 5:/'
  ["adim-5"]='/^## Adım 5:/,/^## Adım 6:/'
  ["adim-6"]='/^## Adım 6:/,/^## Adım 7:/'
  ["adim-7"]='/^## Adım 7:/,/^## Adım 8:/'
  ["adim-8"]='/^## Adım 8:/,/^## Adım 9:/'
  ["adim-9"]='/^## Adım 9:/,/^## Değişecek\|^## Drift\|^## Sözleşme/'
)
for key in "${!RANGES[@]}"; do
  r="${RANGES[$key]}"
  sed -n "${r}{/^## Adım/!{/^## Değişecek/!{/^## Drift/!{/^## Sözleşme/!p}}}}" "$SPEC" > /tmp/spec-sections/$key.txt
  sed -n "${r}{/^## Adım/!{/^## Değişecek/!{/^## Drift/!{/^## Sözleşme/!p}}}}" "$CMD"  > /tmp/cmd-sections/$key.txt
done
ls -la /tmp/spec-sections /tmp/cmd-sections
```
Expected: her dizinde 9 dosya (Adım 1-9); eşit sayı. (Not: spec'te Adım'lar arasına Decisions/Out-of-scope GİRMEZ — onlar Adım 9 sonrası; komutta da o meta bölümler yok, yalnız Sözleşme/Drift var → range sonu guard'ları onları dışlar.)

- [ ] **Step 2: Per-section diff + manuel semantic inspect (full, no truncation)**

```bash
mkdir -p /tmp/section-diffs; > /tmp/section-diffs/_log.txt
for key in adim-1 adim-2 adim-3 adim-4 adim-5 adim-6 adim-7 adim-8 adim-9; do
  diff /tmp/spec-sections/$key.txt /tmp/cmd-sections/$key.txt > /tmp/section-diffs/$key.diff
  echo "$key: $(wc -l < /tmp/section-diffs/$key.diff) diff lines" | tee -a /tmp/section-diffs/_log.txt
done
```
Her `/tmp/section-diffs/<key>.diff` dosyasını **TAMAMEN** oku (`head` YASAK). Kabul: self-referans terminoloji / path örneği. Hard-stop: kural eksikliği, sıra değişikliği, format gevşemesi, paraphrase. Özellikle precedent'siz bölümler (adim-3 worktree, adim-4 matris, adim-5 ledger, adim-9 no-review/chain) byte-yakın olmalı.

Her bölüm için `_log.txt`'ye `accept | reject (sebep)` yaz.

- [ ] **Step 3: Hard stop — rebuild-from-clean (FAIL'de)**

Bir veya daha fazla bölüm reject ise: `rm ~/.claude/commands/review-claude-codex.md` → Task 2'den clean rebuild (Tasks 4-11 hepsi aynı dosyaya append; per-section rollback imkansız, cascade rebuild). Tümü accept ise: `echo "Spec section diff: ALL OK"` → Task 12.

- [ ] **Step 4: No commit**

---

## Task 12: 5-Way Drift Propagation — 4 Ayna Komut (spec/write-plan/execute/simplify)

**tdd: skip; CRITICAL — yalnız Task 11 geçtikten + yeni komut byte-exact doğrulandıktan SONRA (Codex ordering)**

**Files:**
- Modify: `~/.claude/commands/spec-claude-codex.md` (binding + Sözleşme/Drift)
- Modify: `~/.claude/commands/write-plan-claude-codex.md` (binding + Sözleşme/Drift)
- Modify: `~/.claude/commands/execute-plan-claude-codex.md` (Sözleşme/Drift)
- Modify: `~/.claude/commands/simplify-claude-codex.md` (binding + Sözleşme/Drift)

Source: Task 1 Step 3 katalog. Her dosyada "dört komut/dosya"→"beş", Check A matrisi +1 diff (`spec vs review`), Check B "dört dosyada"→"beş dosyada", "biri değişirse" 4→5, ayna listesine `review-claude-codex` eklenir. **Marker bloğunun İÇİ DEĞİŞMEZ.**

- [ ] **Step 0: Catalog hard-stop gate**

```bash
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex; do
  h=$(grep -c "dört\|4-way\|biri değişirse\|Check A\|Check B" ~/.claude/commands/$f.md)
  echo "$f: $h"; [ "$h" -eq 0 ] && { echo "CATALOG EMPTY in $f — STOP"; exit 1; }
done
echo "CATALOG OK"
```
Expected: `CATALOG OK`; her dosyada ≥1 hit.

- [ ] **Step 1: spec-claude-codex.md** — binding "`/write-plan...`, `/execute...`, `/simplify...` ile birebir" → `+ /review-claude-codex` (4-way→5-way); Drift section 4 komut→5, Check A 3 diff→4 (`spec vs review` ekle), Check B "dört"→"beş", "biri değişirse" 4→5.

- [ ] **Step 2: write-plan-claude-codex.md** — aynı 5-way güncelleme (binding + Drift). "dört komutta"→"beş komutta", Check A +`spec vs review`, Check B "beş dosya".

- [ ] **Step 3: execute-plan-claude-codex.md** — Sözleşme/Drift 5-way (binding + Check A/B). (`/review` sweep AYRI — Task 13.)

- [ ] **Step 4: simplify-claude-codex.md** — aynı 5-way güncelleme (binding + Drift; "dört"→"beş", Check A 4 diff, Check B 5 dosya, "biri değişirse" 5).

- [ ] **Step 5: Marker bloğu DOKUNULMADI teyidi (her 4 dosya)**

```bash
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex; do
  diff <(awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' /tmp/$f.md.bak) \
       <(awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' ~/.claude/commands/$f.md)
  echo "$f block diff exit: $?"
done
```
Expected: her dosya `exit: 0` (5-way text değişikliği marker DIŞINDA; blok değişmedi).

- [ ] **Step 6: "dört/beş" sweep teyidi**

```bash
grep -rn "dört komut\|dört dosya\|4-way\|3-way\|iki komut" ~/.claude/commands/spec-claude-codex.md ~/.claude/commands/write-plan-claude-codex.md ~/.claude/commands/execute-plan-claude-codex.md ~/.claude/commands/simplify-claude-codex.md
```
Expected: SIFIR stale "dört/4-way/3-way/iki komut" (hepsi "beş/5-way"e döndü). Kalan hit varsa hit-by-hit düzelt.

- [ ] **Step 7: No commit**

---

## Task 13: `/review` → `/review-claude-codex` Reference Sweep (execute + simplify, hit-by-hit)

**tdd: skip; CRITICAL — blind sed YASAK; historical hit'ler korunur**

**Files:**
- Modify: `~/.claude/commands/execute-plan-claude-codex.md`
- Modify: `~/.claude/commands/simplify-claude-codex.md`

- [ ] **Step 1: Hit listesi (robust pattern — T1-1; `/security-review` satırlarını GİZLEME)**

Önce regex truth-table doğrula (T2-1 — overmatch yok teyidi):
```bash
printf '%s\n' '/review' '/review (sonra /security-review)' '/review-claude-codex' '/security-review' 'docs/reviews/x.md' '/reviewer' '/reviews' | grep -nE "/review([^a-zA-Z0-9_/-]|$)"
# Beklenen MATCH: satır 1,2 yalnız (bare /review). NO-MATCH: /review-claude-codex, /security-review, docs/reviews, /reviewer, /reviews.
```
Sonra hit listesi:
```bash
for f in execute-plan-claude-codex simplify-claude-codex; do
  echo "--- $f ---"
  grep -nE "/review([^a-zA-Z0-9_/-]|$)" ~/.claude/commands/$f.md
done
```
Expected: TÜM bare `/review` hit'leri (zincir satırları dahil — `/security-review` içerse bile). `/review-claude-codex`, `/security-review`, `docs/reviews/...` path'leri eşleşmez. Her hit'i classify et:
- **Active "sonraki adım/zincir" reference** (örn. "Sonraki adım: /review", "/review (sonra /security-review → closure)") → bare `/review`'ı `/review-claude-codex`'e değiştir (satırdaki `/security-review` DOKUNULMAZ).
- **Historical/decisions-log/açıklama** (örn. "eski /review davranışı", geçmiş karar) → KORU (değiştirme).

- [ ] **Step 2: execute-plan-claude-codex hit-by-hit replace** — her active reference Edit ile tek tek; historical olanları atla. (Blind `sed -i` YASAK.)

- [ ] **Step 3: simplify-claude-codex hit-by-hit replace** — aynı; özellikle "Sonraki adım: /review" / "/review (sonra zincir /security-review)" → `/review-claude-codex`.

- [ ] **Step 4: Sweep doğrulama (aynı robust pattern)**

```bash
for f in execute-plan-claude-codex simplify-claude-codex; do
  echo "--- $f kalan bare /review (active olmamalı) ---"
  grep -nE "/review([^a-zA-Z0-9_/-]|$)" ~/.claude/commands/$f.md
done
```
Expected: kalan hit'ler YALNIZ bilinçli korunan historical reference'lar (Step 1'de classify edildi); active zincir reference'ı kalmamalı. Her kalan hit, Step 1'deki "keep" sınıfıyla bire bir eşleşmeli (yeni/atlanan yok). Liste audit için final rapora.

- [ ] **Step 5: No commit**

---

## Task 14: review.md → Deprecated Stub (EN SON — tüm gate'ler geçince)

**tdd: skip**

**Files:**
- Overwrite: `~/.claude/commands/review.md`

Önkoşul: Task 2-13 tamamlandı, Task 11 section-diff geçti, Task 12 5-way + marker-intact geçti, Task 13 sweep geçti.

- [ ] **Step 1: Stub yaz** (`~/.claude/commands/review.md` overwrite; description **quoted** — strict-YAML-safe, repo konvansiyonu 3/4 stub; unquoted `[..]` flow-sequence başlatıp parse'ı kırar):
```markdown
---
description: "[DEPRECATED] use /review-claude-codex"
---

Bu komut `/review-claude-codex` ile değiştirildi (iki bağımsız hakem: fresh Claude subagent + Codex adversarial-review, pinli worktree @ HEAD_SHA üzerinde; ana Claude sentez + agreement-signal + disposition ledger; drift-check 5-way).

**Neden değişti:** Tek-aktörlü fresh-subagent review modeli, claude-codex aile mimarisi (spec/write-plan/execute/simplify) yanında tutarsızdı; ikinci bağımsız (cross-model) hakem false-negative'i düşürür. Yeni komut aile pattern'ına entegre, 5-way drift contract'a tabi.

**Kullanım:** `/review-claude-codex [BASE_REF]` (boş: origin/main).
```

- [ ] **Step 2: Stub teyidi** — `grep -c "DEPRECATED" ~/.claude/commands/review.md` → `1`; `wc -l` küçük (~10).

- [ ] **Step 3: No commit**

---

## Task 15: Final Drift Verification (Check A 5-way + Check B) + Structural + Smoke + Commit

**tdd: skip; CRITICAL — atomik commit hard gate**

**Files:**
- Read-verify: 5 komut dosyası (`~/.claude/commands/*.md`)
- Commit: repo-local audit (`docs/plans/...`, `docs/reviews/codex/...`, spec zaten staged değil — ayrı)

- [ ] **Step 1: Check A — 5-way byte diff (4 diff hepsi 0)**

```bash
C=~/.claude/commands
ok=1
for mirror in write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex review-claude-codex; do
  diff <(awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' $C/spec-claude-codex.md) \
       <(awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' $C/$mirror.md) >/dev/null
  r=$?; echo "spec vs $mirror: exit $r"; [ "$r" -ne 0 ] && ok=0
done
[ "$ok" -eq 1 ] && echo "CHECK A 5-WAY: PASS" || echo "CHECK A: FAIL"
```
Expected: 4 diff `exit 0` + `CHECK A 5-WAY: PASS`. FAIL → ilgili dosyayı backup'tan restore + Task 3/12 tekrar.

- [ ] **Step 2: Check B — 8 tripwire token × 5 dosya**

```bash
C=~/.claude/commands
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex review-claude-codex; do
  blk=$(awk '/CODEX-CALL-PROTOCOL:BEGIN/,/CODEX-CALL-PROTOCOL:END/' $C/$f.md)
  miss=0
  for t in "codex-companion.mjs" "git rev-parse" "AGENTS.md" "timeout 480s" "124" "Claude-only devam et" "Tekrar dene" "Komutu durdur"; do
    echo "$blk" | grep -qF "$t" || { echo "$f MISSING: $t"; miss=1; }
  done
  [ "$miss" -eq 0 ] && echo "$f: 8/8 tokens OK"
done
```
Expected: her 5 dosya `8/8 tokens OK`.

- [ ] **Step 3: Marker count × 5 dosya**

```bash
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex review-claude-codex; do
  echo "$f: $(grep -c 'CODEX-CALL-PROTOCOL:BEGIN\|CODEX-CALL-PROTOCOL:END' ~/.claude/commands/$f.md)"
done
```
Expected: her dosya `2`.

- [ ] **Step 4: Pre-commit smoke gate (3-state — pass | not-run | fail-blocks; Codex T1-3)**

Frontmatter + structural parse **commit ÖNCESİ** (parse hatası commit'ten önce yakalanır):
```bash
CMD=~/.claude/commands/review-claude-codex.md
SMOKE=pass; REASON=""
head -1 "$CMD" | grep -qx -- "---" || { SMOKE=fail; REASON="frontmatter açılış '---' yok"; }
awk 'NR>1 && /^---$/{f=1} END{exit !f}' "$CMD" || { SMOKE=fail; REASON="$REASON; kapanış '---' yok"; }
grep -q "^description:" "$CMD" || { SMOKE=fail; REASON="$REASON; description: yok"; }
# Gerçek YAML frontmatter parse — presence DEĞİL valid parse (Codex pre-exec: unquoted [..] description strict YAML'da kırılır). Hem yeni komut hem stub:
for F in "$CMD" ~/.claude/commands/review.md; do
  awk 'f&&/^---$/{exit} /^---$/{f=1;next} f' "$F" | python3 -c "import sys,yaml; yaml.safe_load(sys.stdin.read())" 2>/dev/null || { SMOKE=fail; REASON="$REASON; $F frontmatter YAML parse hatası"; }
done
[ "$(grep -c '^## Adım [1-9]' "$CMD")" -ge 9 ] || { SMOKE=fail; REASON="$REASON; Adım <9"; }
[ "$(grep -c 'Şablon A\|Şablon B\|Şablon C\|reviewer-status\|[Dd]isposition\|No-review\|Chain-advance\|REQUIREMENT_SNAPSHOT\|git worktree add' "$CMD")" -ge 8 ] || { SMOKE=fail; REASON="$REASON; precedent'siz bölüm <8"; }
echo "SMOKE_PRECOMMIT=$SMOKE ${REASON:+($REASON)}"
```
- `SMOKE_PRECOMMIT=pass` → Step 5/6.
- `SMOKE_PRECOMMIT=fail` → **commit BLOKE**; ilgili task'a dön + düzelt; explicit override edilirse audit log'a `smoke-fail override: <reason>` + kullanıcı onayı (Recommended değil).
- **Runtime registration smoke** (komut `/review-claude-codex` skill listesinde görünür mü) repo-dışı olduğundan commit-öncesi YAPILAMAZ → `SMOKE_RUNTIME=not-run-pre-commit (restart sonrası teyit edilir)` (rapora; pre-commit gate yalnız load+parse+yapı, çalıştırma değil).

- [ ] **Step 5: `/review` sweep audit özeti**

```bash
for f in execute-plan-claude-codex simplify-claude-codex; do
  echo "--- $f korunan historical bare /review (varsa) ---"
  grep -nE "/review([^a-zA-Z0-9_/-]|$)" ~/.claude/commands/$f.md || echo "  (kalan bare /review yok)"
done
```
Expected: kalan hit'ler = bilinçli historical (Task 13 classify) veya boş. Rapora yaz.

- [ ] **Step 6: Audit commit — spec/spec-log dahil self-contained (Codex T1-2)**

Önkoşul: source spec + spec review log git'te olmalı (audit reproducibility — implementation auditi git'te olmayan spec'e referans veremez). Committed değilse bu audit commit'e dahil et:
```bash
cd /root/otomaix
SPEC=docs/specs/2026-06-01-review-claude-codex-command.md
SPEC_LOG=docs/reviews/codex/2026-06-01-review-claude-codex-command.md
PLAN=docs/plans/2026-06-01-review-claude-codex-command.md
PLAN_LOG=docs/reviews/codex/2026-06-01-review-claude-codex-command-plan.md
EXTRA=""
for x in "$SPEC" "$SPEC_LOG"; do
  git ls-files --error-unmatch "$x" >/dev/null 2>&1 || { echo "UNTRACKED → audit'e ekleniyor: $x"; EXTRA="$EXTRA $x"; }
done
git add -- "$PLAN" "$PLAN_LOG" $EXTRA
git status --short
```
Onay sonrası commit (`docs:` prefix; **push YOK**; `git add -A`/`git add .` YASAK — repo-dışı `~/.claude/commands/*.md` girmez). Mesaj: spec/log yeni eklendiyse `docs: add review-claude-codex spec + plan (implementation audit)`, zaten committed ise `docs: implement review-claude-codex command (plan execution audit)`. Komut dosyaları **Claude Code restart** ile aktif olur.

- [ ] **Step 7: Restart + smoke notu (rapora)**

Kullanıcıya: komut dosyaları repo-dışı → `/review-claude-codex` skill listesinde görünmesi için **Claude Code restart** gerekir. Restart sonrası smoke = load + frontmatter parse (skill listesinde kayıt).

---

## Verification Özet (plan geneli)

| Gate | Komut | Beklenen |
|---|---|---|
| Canonical byte-exact | Task 3 Step 4 | `diff exit 0` |
| Section diff matrix | Task 11 | tüm bölüm accept |
| Marker DOKUNULMADI (4 ayna) | Task 12 Step 5 | her `exit 0` |
| Check A 5-way | Task 15 Step 1 | `PASS` (4 diff=0) |
| Check B 8 token × 5 | Task 15 Step 2 | her `8/8` |
| Marker count × 5 | Task 15 Step 3 | her `2` |
| Precedent'siz bölümler smoke | Task 15 Step 4 | grep ≥ 8 |
| `/review` sweep | Task 13 Step 4 + Task 15 Step 5 | active reference kalmadı |

**Stop-the-line:** Herhangi bir CRITICAL gate FAIL → ilgili task'a dön (backup'tan restore veya rebuild-from-clean), düzelt, tekrar. Atomik commit yalnız tüm gate'ler geçince (Task 15).
