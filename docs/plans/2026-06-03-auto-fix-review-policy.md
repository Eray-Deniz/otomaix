---
title: Auto-Fix Review Policy — claude-codex aile geneli
status: plan-approved
date: 2026-06-03
source_spec: docs/specs/2026-06-03-auto-fix-review-policy.md
source_spec_unapproved_override: false
noisy_review_override: false
unresolved_high_severity_override: true
codex_plan_review_status: approved-by-iteration-limit
codex_plan_review_iterations: 3
codex_plan_targeted_fixes: 0
codex_plan_review_log: docs/reviews/codex/2026-06-03-auto-fix-review-policy-plan.md
---

# Auto-Fix Review Policy Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** claude-codex fix-yapan komutlarına (spec, write-plan, execute-plan, simplify) `claude-confirmed` C/H/M bulgular için kullanıcı-onaysız otonom fix döngüsü ekle (6-tur tavan + global cap=10 backstop), reviewer komutlarını (review, security) report-only disposition/chain-gate diliyle hizala, ve hepsini `claude-codex-drift-check.sh` Check D byte-identical kontratıyla kilitle.

**Architecture:** Yeni `<!-- AUTO-FIX-REVIEW-POLICY:BEGIN ... END -->` marker bloğu **canonical = spec-claude-codex** olarak yazılır, oradan **byte-for-byte awk-extract + insert** ile write-plan/execute-plan/simplify'a kopyalanır (mevcut 7-way `CODEX-CALL-PROTOCOL` + 4-way `CODEX-SCAN-SUBSTRATE` drift kültürünün aynısı). Her komut bloğu kendi guard adımına **per-command binding prose** ile bağlar. review/security blok ALMAZ — yalnız prose disposition + chain-gate düzenlemesi. `claude-codex-drift-check.sh`'e Check D eklenir (4-way `cmp` + tripwire token + reviewer token check), TDD: önce Check D (RED) → blok yayılınca (GREEN).

**Tech Stack:** Markdown (repo-DIŞI komut dosyaları `~/.claude/commands/`), Bash (`claude-codex-drift-check.sh`, repo-İÇİ tek test harness), `awk`/`cmp`/`grep -F` (byte-identical doğrulama). Geleneksel repo test dosyası YOK — drift-check script'i tek otomatik regresyon kapısıdır; ek olarak prose senaryo trace + markdown smoke parse.

**Deliverable konum notu (KRİTİK — her task için geçerli):**
- 6 komut dosyası repo-DIŞI: `~/.claude/commands/{spec,write-plan,execute-plan,simplify,review,security-review}-claude-codex.md` → **git'e commit EDİLMEZ** (versiyon kontrolü dışı).
- Yedek: `~/.claude/command-backups/<cmd>-claude-codex.md.bak-<TS>` (loader `.bak`'ı komut sanmasın diye kardeş klasör; bkz. memory `command-backups-location`).
- Repo-İÇİ tek değişen kod: `docs/tools/claude-codex-drift-check.sh` (Check D) → **bu commit'lenir**.
- Bu plan dosyası: `docs/plans/2026-06-03-auto-fix-review-policy.md` (commit'i bu komutun Adım 17'sinde, execution'da değil).

**Repo-path konvansiyonu (worktree-safe — Codex F1 fix):** Aşağıdaki bash bloklarında `/root/otomaix`
HARD-CODE EDİLMEZ. Executor bir git worktree'de çalışırsa absolute path **ana checkout'u** hedefler,
worktree'yi değil → Check D yanlış ağaca karşı koşar / yanlış ağaca commit eder. Her drift-check &
commit bloğu başında `REPO=$(git rev-parse --show-toplevel)` tanımlanır ve `"$REPO/docs/tools/..."`
kullanılır. `~/.claude/commands/` ve `~/.claude/command-backups/` HOME-absolute kalır (komutlar
genuinely global, per-checkout değil). Task 1 Step 2 erken assertion ile doğru checkout'u doğrular.

---

## File Structure

| Dosya | Sorumluluk | Repo? | Değişiklik |
|---|---|---|---|
| `~/.claude/commands/spec-claude-codex.md` | tasarım-doc fix-komutu (canonical block kaynağı) | DIŞ | AUTO-FIX blok (canonical) + Adım 7 binding prose |
| `~/.claude/commands/write-plan-claude-codex.md` | tasarım-doc fix-komutu | DIŞ | AUTO-FIX blok (byte-copy) + Adım 13/14 binding prose |
| `~/.claude/commands/execute-plan-claude-codex.md` | yürütücü fix-komutu | DIŞ | AUTO-FIX blok (byte-copy) + Adım 8.5/12 binding prose |
| `~/.claude/commands/simplify-claude-codex.md` | yürütücü fix-komutu | DIŞ | AUTO-FIX blok (byte-copy) + Adım 10 binding prose |
| `~/.claude/commands/review-claude-codex.md` | report-only reviewer | DIŞ | Adım 5/9 prose: disposition C/H/M=fix-required + chain-gate + reviewer token'lar |
| `~/.claude/commands/security-review-claude-codex.md` | report-only reviewer | DIŞ | Adım 5/9 prose (review ile aynı) + güvenlik floor + security-risk override AYRI |
| `~/.claude/commands/finish-branch-claude-codex.md` | danışma (kapsam DIŞI) | DIŞ | Opsiyonel 1-satır "kapsam dışı" notu (blok YOK) |
| `docs/tools/claude-codex-drift-check.sh` | drift regresyon harness | **İÇ** | Check D (4-way block + tripwire + reviewer token check) |

---

## Canonical AUTO-FIX-REVIEW-POLICY Block (referans — Task 3'te birebir kullanılır)

Bu, 4 fix-komutuna **byte-identical** giren marker bloğudur. Task 3 bunu `spec-claude-codex.md`'ye yazar; Task 4 awk ile çıkarıp diğer 3'e kopyalar. **Aşağıdaki metin tam ve nihaidir — placeholder yok.** Tripwire token'lar (Check D): `claude-confirmed`, `cluster-key`, `finding-id`, `global cap`, `reopen`, `6-tavan` — hepsi blokta literal mevcut.

````markdown
<!-- AUTO-FIX-REVIEW-POLICY:BEGIN (canonical: spec-claude-codex; 4-way byte-identical: spec/write-plan/execute-plan/simplify — biri değişirse diğerleri de; drift-check Check D) -->
> **Auto-Fix Review Policy (aile ortak — fix-yapan komutlar).** Bu blok yalnız **evrensel**
> kuralları taşır; her komut kendi guard adımına + medium nüansına **binding prose** ile bağlar.
> Reviewer komutları (review/security) bu bloğu İÇERMEZ (report-only — yalnız prose disposition).

### Tetik: `claude-confirmed Codex finding`
Bir bulgu yalnız şu üçü **birlikte** sağlanırsa kullanıcı onayı beklemeden otomatik düzeltilir:
1. **Codex** bulguyu üretti, **VE**
2. **Claude** aynı bulguyu doğruladı — çift-hakemli akışta alt-tür **`both-agree`** (fresh Claude
   reviewer + Codex aynı bulguda), tek-Claude akışında ana Claude validasyonu, **VE**
3. severity ∈ {critical, high, medium} (medium için aşağıdaki tür-bazlı nüans).

Claude doğrulamazsa → **otomatik fix YOK.** Bulgu disposition ledger'da `single-source` /
`rejected` / `needs-human` kalır (mevcut ledger mekaniği korunur).

### Severity anlamı
- **critical / high:** her zaman fix-required (tavan altında).
- **medium:** tür-bazlı (her komutun binding prose'una bağlanır) — uygulama/güvenlik
  bağlamında fix-required; tasarım-doc bağlamında `technical-medium → fix-required`,
  `tradeoff-medium → iteration-limit / kullanıcı kararı` (belirsizse default = tradeoff-medium,
  tasarım niyetini gasp etme).
- **low:** fix/review turu ≤ 3 ise düzeltilir; 4. turdan itibaren kalan low →
  **audit-trail'e yazılır + göz ardı edilir**, komut kullanıcı onayı olmadan normal akışına devam eder.

### Tur yapısı ve sert tavan — `6-tavan` (critical/high/medium)
- **Tur 1–3:** Claude kendi fix yaklaşımıyla düzeltir → verify → Codex re-review.
- **Tur 4+:** Codex çağrısı bulgunun yanında **zorunlu yapılandırılmış çözüm önerisi** döner:
  `root cause / minimal fix strategy / etkilenen dosya·fonksiyonlar / verification komutu /
  yanlışsa risk / fallback`. Claude değerlendirip uygular (kullanıcı onayı yok). *Codex
  read-only kalır — yalnız metin önerir, dosya YAZMAZ; uygulayan Claude.*
- **Tur 6 tavanı (cluster-key başına `6-tavan`):** aynı **cluster-key / root-cause** 6 fix/review
  turu sonunda hâlâ kapanmıyorsa **otonom döngü DURUR** → kullanıcıya somut rapor (kalan bulgular /
  kaç tur denendi / uygulanan fix'ler / Codex çözüm önerileri / neden kapanmadı: olası oscillation /
  önerilen sonraki adım). Sonrası kullanıcı kararı: **devam / kapsam daralt / manuel düzelt /
  blocked**. *"max review 3 geçersiz" = "3'te otomatik approve etme", sonsuz döngü değildir.*

### Cluster ledger + global cap (tavanı deterministik yapan backstop — ZORUNLU, bloktan çıkarılamaz)
- **finding-id:** her bulgu ilk göründüğünde stabil artımlı id alır (`F1, F2, …`).
- **cluster-key:** normalize edilmiş **(etkilenen invariant / path / anchor)** — aynı dosya:satır
  veya aynı adlandırılmış invariant'a değen bulgular aynı cluster. Sentez/disposition ledger'ı bu
  eşlemeyi tutar.
- **6-tur sayacı cluster-key başına.** Bir bulgu kapanıp **aynı cluster-key ile yeniden açılırsa**
  (reopen) → prior sayacı **miras alır** (sıfırlamaz). Gerçekten yeni bir cluster-key turn 1'den başlar.
- **Reopen = oscillation sinyali:** kapanmış bir cluster-key **2. kez** yeniden açılırsa (reopen) →
  non-convergence kabul → o cluster için DUR + kullanıcı raporu (severity'den bağımsız).
- **Session global cap = 10 (asıl backstop):** tek komut çalışmasında **toplam auto-fix turu** için
  global tavan = `global cap=10` (cluster split/merge ne olursa olsun). Global cap dolunca → tüm
  otonom döngü DURUR → kullanıcı raporu. Cluster reclassification ile tavanı atlatan oscillation'a
  karşı kesin sınır.

### Carve-out (otonomi KAPSAM DIŞI — insan-kapısı korunur)
Şunlar fix döngüsü değil; **onay ister**: vault/memory yazımı · active layer TASK.md/HANDOFF.md
mutation · task status/lifecycle değişimi · **push / merge / discard / branch·worktree silme** ·
security-risk override · dual-review override. **Commit nüansı:** yürütücü (execute-plan) zaten
task-başı RED-GREEN-REFACTOR-COMMIT ile **otonom local commit** atar (mevcut tasarım; gate olan
**push**'tur). Auto-fix döngüsü bu cadence'i **aynen miras alır, yeni commit otonomisi EKLEMEZ** —
fix'ler normal task işi gibi commit'lenir. Override sıradan bir seçenek değildir — yalnız ilgili
komutun **mevcut explicit override kapısından** geçer (otomatik önerilen yol değildir).
<!-- AUTO-FIX-REVIEW-POLICY:END -->
````

---

## Task 1: Backups + drift-check baseline (RED zemini)

**Files:**
- Create: `~/.claude/command-backups/<cmd>-claude-codex.md.bak-<TS>` (7 dosya)
- Read-only: `docs/tools/claude-codex-drift-check.sh`

- [ ] **Step 1: Tüm dokunulacak komut dosyalarının zaman damgalı yedeğini al**

```bash
TS=$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p ~/.claude/command-backups
for c in spec write-plan execute-plan simplify review security-review finish-branch; do
  cp -p ~/.claude/commands/$c-claude-codex.md \
        ~/.claude/command-backups/$c-claude-codex.md.bak-$TS
done
ls -1 ~/.claude/command-backups/*.bak-$TS
```
Expected: 7 satır listelenir (her komut için bir `.bak-<TS>`).

- [ ] **Step 2: Mevcut drift-check baseline'ını çalıştır + yakala**

```bash
REPO=$(git rev-parse --show-toplevel) || { echo "not in a git repo"; exit 1; }
# Erken assertion: doğru checkout (drift-check + spec mevcut)
[ -f "$REPO/docs/tools/claude-codex-drift-check.sh" ] && [ -f "$REPO/docs/specs/2026-06-03-auto-fix-review-policy.md" ] \
  || { echo "WRONG CHECKOUT: $REPO beklenen dosyaları içermiyor"; exit 1; }
bash "$REPO/docs/tools/claude-codex-drift-check.sh"; echo "EXIT=$?"
```
Expected: `PASS: claude-codex drift check clean` + `EXIT=0`. (Check A/B/C şu an temiz — Check D henüz yok.) Bu çıktıyı not al; Task sonunda A/B/C'nin hâlâ PASS olduğunu doğrulamak için referans.

- [ ] **Step 3: AUTO-FIX marker'larının HİÇBİR komutta olmadığını doğrula**

```bash
grep -l "AUTO-FIX-REVIEW-POLICY" ~/.claude/commands/*-claude-codex.md 2>/dev/null \
  && echo "UNEXPECTED: marker already present" || echo "OK: no auto-fix markers yet"
```
Expected: `OK: no auto-fix markers yet`. (Temiz RED zemini.)

---

## Task 2: Check D'yi drift-check.sh'e ekle (TEST — RED)

**Files:**
- Modify: `docs/tools/claude-codex-drift-check.sh`

TDD: testi önce yaz, RED gör (markerlar 4 komutta yok + reviewer token'lar yok). Mevcut `check_expected_blocks` / `check_unexpected_markers` / `check_tokens` fonksiyonları **yeniden kullanılır**; yalnız Check D için yeni `check_reviewer_tokens` fonksiyonu + manifest sabitleri + çağrılar eklenir.

- [ ] **Step 1: Check D manifest sabitlerini ekle**

`PROTO_EXPECTED` / `SUBSTRATE_EXPECTED` tanımlarının hemen altına (mevcut `SUBSTRATE_EXPECTED=(...)` satırından sonra) ekle:

```bash
AUTO_FIX_EXPECTED=(spec write-plan execute-plan simplify)
REVIEWER_EXPECTED=(review security-review)

AUTOFIX_BEGIN='<!-- AUTO-FIX-REVIEW-POLICY:BEGIN'
AUTOFIX_END='<!-- AUTO-FIX-REVIEW-POLICY:END'
```

- [ ] **Step 2: Check D token listelerini ekle**

`SUBSTRATE_TOKENS=(...)` dizisinin kapanış parantezinden sonra ekle:

```bash
# Check D block tripwire tokens (spec decision: backstop must live INSIDE the block).
AUTOFIX_TOKENS=(
  'claude-confirmed'
  'cluster-key'
  'finding-id'
  'global cap'
  'reopen'
  '6-tavan'
)

# Check D reviewer-side tokens (review + security-review; same list as spec architecture #2).
# 'medium advisory' guarantees medium is NOT implied as a hard-block.
REVIEWER_TOKENS=(
  'fix-required'
  'medium advisory'
  'chain-gate'
  'report-only'
  'critical'
  'high'
  'medium'
  'low'
)
```

- [ ] **Step 3: `check_reviewer_tokens` fonksiyonunu ekle**

Mevcut `check_tokens()` fonksiyonunun kapanış `}`'inden sonra ekle (reviewer dosyalarında marker bloğu YOK → token'lar tüm dosyaya karşı grep'lenir):

```bash
check_reviewer_tokens() {
  local label="$1"; shift
  local tokens=("$@")
  local slug file token missing

  say "--- $label reviewer tokens ---"
  for slug in "${REVIEWER_EXPECTED[@]}"; do
    file=$(cmd_path "$slug")
    if [ ! -f "$file" ]; then
      fail "$label missing reviewer file: $file"
      continue
    fi
    missing=0
    for token in "${tokens[@]}"; do
      if ! grep -qF -- "$token" "$file"; then
        fail "$label missing reviewer token in $slug: $token"
        missing=1
      fi
    done
    [ "$missing" -eq 0 ] && ok "$label reviewer tokens present: $slug"
  done
}

check_reviewer_forbidden() {
  # Negatif kapı (Codex F2/F5/F7): pozitif `medium advisory` token'ı medium'un hard-block OLMADIĞINI
  # KANITLAMAZ. ENUMERATION-SCOPED (advisory-exclusion DEĞİL — o bypass edilebilirdi: eski
  # `hard-block: critical/high/medium` + yakına appendlenen `medium advisory` pencereyi temizler).
  # Mantık: bir chain hard-block satırı için (a) SATIRIN KENDİSİ medium/C/H/M içeriyorsa ihlal;
  # (b) satırın hemen ardından gelen ARDIŞIK LİSTE enumerasyonu (lead-blank atlanır; ilk prose/
  # trailing-blank'te durulur) bir `medium` öğesi içeriyorsa ihlal. Ayrı bir prose cümlesindeki
  # `medium advisory` TARANMAZ (liste öğesi değil → false-positive yok, bypass yok). POSIX
  # `tolower()` (Medium/MEDIUM) + `C/H/M` (boşluklu `C / H / M` dahil) normalize. Spec invariant:
  # chain hard-block enumerasyonu YALNIZ critical/high.
  #
  # KAPSAM (Codex F9 + kullanıcı kararı 2026-06-03): bu bir TRIPWIRE'dır, tam ispat DEĞİL. Yakalar:
  # (a) inline hard-block satırında medium/C/H/M; (b) hard-block altındaki ardışık LİSTE öğesinde
  # medium. YAKALAMAZ: hard-block satırını takip eden WRAPPED PROSE continuation'da medium (örn.
  # `hard-block:` + sonraki prose satırı `critical/high/medium`). Residual BİLİNÇLİ — prose'u tarayan
  # her heuristik ya bypass edilir ya kanonik prose'a false-positive verir (medium'u hard-block
  # yakınında meşru tartışan disclaimer'lar; F5/F7/F9 arms-race'i ampirik kanıt). Negatif check
  # spec-ÖTESİdir (spec POZİTİF reviewer token check ister — o tam geçer). Residual'ı şu KATMANLAR
  # kapsar: Task 6 REPLACE-not-append (eski enumerasyon silinir) + manual scenario trace (Task 8
  # Step 3) + execution'da Codex'in gerçek reviewer-edit review'ı. Yazım kuralı: hard-block satırı
  # self-contained "hard-block ... critical/high" olsun, medium ayrı `advisory` cümlesinde.
  local label="$1"
  local slug file bad
  say "--- $label reviewer forbidden (medium-as-hard-block; enumeration-scoped TRIPWIRE) ---"
  for slug in "${REVIEWER_EXPECTED[@]}"; do
    file=$(cmd_path "$slug")
    if [ ! -f "$file" ]; then
      fail "$label missing reviewer file: $file"
      continue
    fi
    bad=$(awk '
      { raw[NR]=$0; low[NR]=tolower($0) }
      END{
        for(i=1;i<=NR;i++){
          # Trigger YALNIZ "hard-block" (gate terimi). "chain-advance'i bloke etmez" gibi disclaimer
          # ifadeleri tetiklemez (F7 false-positive'i önler). Yazım kuralı: hard-block satırı yalnız
          # critical/high enumere eder; medium ayrı `advisory` cümlesinde, "hard-block" kelimesiyle
          # aynı satırda DEĞİL.
          if(low[i] !~ /hard-?block/) continue
          line=low[i]; gsub(/ *\/ */,"/",line); gsub(/c\/h\/m/,"medium",line)
          if(line ~ /medium/){ print "L" i " inline: " raw[i]; continue }
          started=0
          for(j=i+1;j<=NR;j++){
            if(low[j] ~ /^[[:space:]>]*$/){ if(started) break; else continue }
            if(low[j] ~ /^[[:space:]>]*[-*+][[:space:]]/ || low[j] ~ /^[[:space:]>]*[0-9]+\.[[:space:]]/){
              started=1; item=low[j]; gsub(/ *\/ */,"/",item); gsub(/c\/h\/m/,"medium",item)
              if(item ~ /medium/){ print "L" j " bullet<-L" i ": " raw[j]; break }
            } else break
          }
        }
      }' "$file")
    if [ -n "$bad" ]; then
      fail "$label medium-as-hard-block phrasing in $slug: $bad"
    else
      ok "$label no medium hard-block phrasing: $slug"
    fi
  done
}
```

- [ ] **Step 4: Check D çağrılarını ekle**

`check_s1_literal_regression` çağrısının HEMEN ÖNÜNE (mevcut `check_tokens "Check C ..." ...` bloğundan sonra, `check_s1_literal_regression` satırından önce) ekle:

```bash
check_expected_blocks "Check D AUTO-FIX-REVIEW-POLICY" "$AUTOFIX_BEGIN" "$AUTOFIX_END" "autofix" "${AUTO_FIX_EXPECTED[@]}"
check_unexpected_markers "Check D AUTO-FIX-REVIEW-POLICY" "$AUTOFIX_BEGIN" "${AUTO_FIX_EXPECTED[@]}"
check_tokens "Check D AUTO-FIX-REVIEW-POLICY" "autofix" "${AUTOFIX_TOKENS[@]}"
check_reviewer_tokens "Check D reviewer" "${REVIEWER_TOKENS[@]}"
check_reviewer_forbidden "Check D reviewer"
```

- [ ] **Step 5: Bash syntax doğrula**

```bash
REPO=$(git rev-parse --show-toplevel); bash -n "$REPO/docs/tools/claude-codex-drift-check.sh" && echo "SYNTAX_OK"
```
Expected: `SYNTAX_OK`.

- [ ] **Step 6: Check D'yi RED gör (testin başarısızlığını doğrula)**

```bash
REPO=$(git rev-parse --show-toplevel); bash "$REPO/docs/tools/claude-codex-drift-check.sh"; echo "EXIT=$?"
```
Expected: `FAILURES=` > 0, `EXIT=1`. Hata satırları: `Check D AUTO-FIX-REVIEW-POLICY marker count for spec: begin=0 end=0` (4 komut için) + `Check D reviewer missing reviewer token in review: medium advisory` (vb.). **Check A/B/C satırları hâlâ `ok:`/`PASS` mantığında olmalı** (yalnız Check D + reviewer FAIL ediyor). Bu beklenen RED.

---

## Task 3: Canonical AUTO-FIX bloğunu spec-claude-codex.md'ye yaz

**Files:**
- Modify: `~/.claude/commands/spec-claude-codex.md`

- [ ] **Step 1: Insertion anchor'ı bul**

```bash
grep -n "CODEX-CALL-PROTOCOL:END\|^## Adım 0: Active Context Read" ~/.claude/commands/spec-claude-codex.md
```
Expected: `<!-- CODEX-CALL-PROTOCOL:END -->` satırı + `## Adım 0: Active Context Read (koşullu)` satırı. Blok, protokol bloğunun downstream notundan SONRA, **`## Adım 0` satırının hemen ÖNÜNE** yeni bir `## Auto-Fix Review Policy (aile ortak)` bölümü olarak eklenir.

- [ ] **Step 2: Bloğu ekle (Edit tool)**

`## Adım 0: Active Context Read (koşullu)` satırının hemen önüne aşağıdaki bölümü ekle. Marker bloğu içeriği bu plandaki **"Canonical AUTO-FIX-REVIEW-POLICY Block"** ile **birebir aynı** olmalı (kopyala, yeniden yazma):

```markdown
## Auto-Fix Review Policy (aile ortak)

<!-- AUTO-FIX-REVIEW-POLICY:BEGIN (canonical: spec-claude-codex; 4-way byte-identical: spec/write-plan/execute-plan/simplify — biri değişirse diğerleri de; drift-check Check D) -->
> **Auto-Fix Review Policy (aile ortak — fix-yapan komutlar).** Bu blok yalnız **evrensel**
> kuralları taşır; her komut kendi guard adımına + medium nüansına **binding prose** ile bağlar.
> Reviewer komutları (review/security) bu bloğu İÇERMEZ (report-only — yalnız prose disposition).

### Tetik: `claude-confirmed Codex finding`
Bir bulgu yalnız şu üçü **birlikte** sağlanırsa kullanıcı onayı beklemeden otomatik düzeltilir:
1. **Codex** bulguyu üretti, **VE**
2. **Claude** aynı bulguyu doğruladı — çift-hakemli akışta alt-tür **`both-agree`** (fresh Claude
   reviewer + Codex aynı bulguda), tek-Claude akışında ana Claude validasyonu, **VE**
3. severity ∈ {critical, high, medium} (medium için aşağıdaki tür-bazlı nüans).

Claude doğrulamazsa → **otomatik fix YOK.** Bulgu disposition ledger'da `single-source` /
`rejected` / `needs-human` kalır (mevcut ledger mekaniği korunur).

### Severity anlamı
- **critical / high:** her zaman fix-required (tavan altında).
- **medium:** tür-bazlı (her komutun binding prose'una bağlanır) — uygulama/güvenlik
  bağlamında fix-required; tasarım-doc bağlamında `technical-medium → fix-required`,
  `tradeoff-medium → iteration-limit / kullanıcı kararı` (belirsizse default = tradeoff-medium,
  tasarım niyetini gasp etme).
- **low:** fix/review turu ≤ 3 ise düzeltilir; 4. turdan itibaren kalan low →
  **audit-trail'e yazılır + göz ardı edilir**, komut kullanıcı onayı olmadan normal akışına devam eder.

### Tur yapısı ve sert tavan — `6-tavan` (critical/high/medium)
- **Tur 1–3:** Claude kendi fix yaklaşımıyla düzeltir → verify → Codex re-review.
- **Tur 4+:** Codex çağrısı bulgunun yanında **zorunlu yapılandırılmış çözüm önerisi** döner:
  `root cause / minimal fix strategy / etkilenen dosya·fonksiyonlar / verification komutu /
  yanlışsa risk / fallback`. Claude değerlendirip uygular (kullanıcı onayı yok). *Codex
  read-only kalır — yalnız metin önerir, dosya YAZMAZ; uygulayan Claude.*
- **Tur 6 tavanı (cluster-key başına `6-tavan`):** aynı **cluster-key / root-cause** 6 fix/review
  turu sonunda hâlâ kapanmıyorsa **otonom döngü DURUR** → kullanıcıya somut rapor (kalan bulgular /
  kaç tur denendi / uygulanan fix'ler / Codex çözüm önerileri / neden kapanmadı: olası oscillation /
  önerilen sonraki adım). Sonrası kullanıcı kararı: **devam / kapsam daralt / manuel düzelt /
  blocked**. *"max review 3 geçersiz" = "3'te otomatik approve etme", sonsuz döngü değildir.*

### Cluster ledger + global cap (tavanı deterministik yapan backstop — ZORUNLU, bloktan çıkarılamaz)
- **finding-id:** her bulgu ilk göründüğünde stabil artımlı id alır (`F1, F2, …`).
- **cluster-key:** normalize edilmiş **(etkilenen invariant / path / anchor)** — aynı dosya:satır
  veya aynı adlandırılmış invariant'a değen bulgular aynı cluster. Sentez/disposition ledger'ı bu
  eşlemeyi tutar.
- **6-tur sayacı cluster-key başına.** Bir bulgu kapanıp **aynı cluster-key ile yeniden açılırsa**
  (reopen) → prior sayacı **miras alır** (sıfırlamaz). Gerçekten yeni bir cluster-key turn 1'den başlar.
- **Reopen = oscillation sinyali:** kapanmış bir cluster-key **2. kez** yeniden açılırsa (reopen) →
  non-convergence kabul → o cluster için DUR + kullanıcı raporu (severity'den bağımsız).
- **Session global cap = 10 (asıl backstop):** tek komut çalışmasında **toplam auto-fix turu** için
  global tavan = `global cap=10` (cluster split/merge ne olursa olsun). Global cap dolunca → tüm
  otonom döngü DURUR → kullanıcı raporu. Cluster reclassification ile tavanı atlatan oscillation'a
  karşı kesin sınır.

### Carve-out (otonomi KAPSAM DIŞI — insan-kapısı korunur)
Şunlar fix döngüsü değil; **onay ister**: vault/memory yazımı · active layer TASK.md/HANDOFF.md
mutation · task status/lifecycle değişimi · **push / merge / discard / branch·worktree silme** ·
security-risk override · dual-review override. **Commit nüansı:** yürütücü (execute-plan) zaten
task-başı RED-GREEN-REFACTOR-COMMIT ile **otonom local commit** atar (mevcut tasarım; gate olan
**push**'tur). Auto-fix döngüsü bu cadence'i **aynen miras alır, yeni commit otonomisi EKLEMEZ** —
fix'ler normal task işi gibi commit'lenir. Override sıradan bir seçenek değildir — yalnız ilgili
komutun **mevcut explicit override kapısından** geçer (otomatik önerilen yol değildir).
<!-- AUTO-FIX-REVIEW-POLICY:END -->

```

- [ ] **Step 3: Marker sayısı + token kontrolü (lokal)**

```bash
f=~/.claude/commands/spec-claude-codex.md
echo "BEGIN=$(grep -cF 'AUTO-FIX-REVIEW-POLICY:BEGIN' "$f") END=$(grep -cF 'AUTO-FIX-REVIEW-POLICY:END' "$f")"
for t in claude-confirmed cluster-key finding-id 'global cap' reopen 6-tavan; do
  grep -qF -- "$t" "$f" && echo "ok:$t" || echo "MISSING:$t"
done
```
Expected: `BEGIN=1 END=1` + 6 satır `ok:<token>` (hiç `MISSING` yok).

- [ ] **Step 4: Drift-check — hâlâ RED ama spec artık 1/4**

```bash
REPO=$(git rev-parse --show-toplevel)
bash "$REPO/docs/tools/claude-codex-drift-check.sh" 2>&1 | grep -E "Check D|block present|marker count"; echo "---"
bash "$REPO/docs/tools/claude-codex-drift-check.sh" >/dev/null 2>&1; echo "EXIT=$?"
```
Expected: `Check D ... block present: spec` görünür; write-plan/execute-plan/simplify hâlâ `marker count ... begin=0 end=0` → `EXIT=1` (RED devam). Beklenen.

---

## Task 4: Bloğu byte-for-byte 3 komuta kopyala (write-plan, execute-plan, simplify)

**Files:**
- Modify: `~/.claude/commands/{write-plan,execute-plan,simplify}-claude-codex.md`

Hand-retype YASAK — drift riski. spec'ten awk ile çıkar, hedef komutlara aynı anchor mantığıyla yerleştir.

- [ ] **Step 1: Canonical bloğu spec'ten çıkar (BEGIN..END dahil)**

```bash
SRC=~/.claude/commands/spec-claude-codex.md
BLK=$(mktemp /tmp/autofix-block.XXXXXX.md)
awk '
  index($0, "<!-- AUTO-FIX-REVIEW-POLICY:BEGIN") { inb=1 }
  inb { print }
  index($0, "<!-- AUTO-FIX-REVIEW-POLICY:END") { inb=0 }
' "$SRC" > "$BLK"
echo "BLK=$BLK lines=$(wc -l < "$BLK")"
head -1 "$BLK"; tail -1 "$BLK"
```
Expected: `lines` ~ 52, ilk satır `<!-- AUTO-FIX-REVIEW-POLICY:BEGIN ...`, son satır `<!-- AUTO-FIX-REVIEW-POLICY:END -->`. Bu `$BLK` dosyası 3 hedefe aynen girer.

- [ ] **Step 2: Her hedef komutta insertion anchor'ını belirle**

```bash
for c in write-plan execute-plan simplify; do
  echo "== $c =="
  grep -nE "^## Adım 0:|^## Adım 1:" ~/.claude/commands/$c-claude-codex.md | head -1
done
```
Expected: write-plan + execute-plan → `## Adım 0:` (blok bunun önüne); simplify → `## Adım 1:` (blok bunun önüne — simplify'da Adım 0 yok). Anchor = ilgili komutta protokol bölümünden sonraki **ilk `## Adım` başlığı**.

- [ ] **Step 3: Bloğu 3 komuta yerleştir**

Her hedef için: Step 2'de bulunan ilk `## Adım` başlık satırının HEMEN ÖNÜNE şunu ekle — `## Auto-Fix Review Policy (aile ortak)` başlığı + bir boş satır + `$BLK` içeriği (BEGIN..END birebir) + bir boş satır. Edit tool ile, `old_string` = ilk `## Adım` başlık satırı, `new_string` = (yeni bölüm + "\n\n" + orijinal başlık).

`$BLK` içeriğini birebir kullan; karakterine dokunma. (Pratikte: `$BLK` dosyasını oku, içeriğini `## Auto-Fix Review Policy (aile ortak)\n\n<BLK içeriği>\n\n` formatında Edit `new_string`'ine göm, ardından orijinal `## Adım` başlığını ekle.)

- [ ] **Step 4: 4-way byte-identical doğrula (extract + cmp)**

```bash
T=$(mktemp -d /tmp/autofix-cmp.XXXXXX)
for c in spec write-plan execute-plan simplify; do
  awk '
    index($0, "<!-- AUTO-FIX-REVIEW-POLICY:BEGIN") { inb=1 }
    inb { print }
    index($0, "<!-- AUTO-FIX-REVIEW-POLICY:END") { inb=0 }
  ' ~/.claude/commands/$c-claude-codex.md > "$T/$c.block"
done
REF="$T/spec.block"
rc=0
for c in write-plan execute-plan simplify; do
  cmp -s "$REF" "$T/$c.block" && echo "ok:cmp $c==spec" || { echo "DRIFT:$c"; rc=1; }
done
echo "md5: $(md5sum "$REF" | awk '{print $1}')"; echo "RC=$rc"
```
Expected: 3 satır `ok:cmp <c>==spec`, `RC=0`. **Tek bir `DRIFT` bile çıkarsa** Step 3'ü `$BLK`'den yeniden uygula (normalize/whitespace toleransı YOK).

- [ ] **Step 5: Drift-check Check D block kısmı GREEN**

```bash
REPO=$(git rev-parse --show-toplevel); bash "$REPO/docs/tools/claude-codex-drift-check.sh" 2>&1 | grep -E "Check D AUTO-FIX|byte drift|tokens present: (spec|write-plan|execute-plan|simplify)"
```
Expected: 4 komut için `block present` + `tokens present`, hiç `byte drift` yok. (reviewer-token-check hâlâ FAIL — Task 6'da çözülür.)

---

## Task 5: Per-command binding prose (4 fix-komutu)

**Files:**
- Modify: `~/.claude/commands/{spec,write-plan,execute-plan,simplify}-claude-codex.md`

Binding prose marker bloğunun DIŞINDADIR (byte-identical'i bozmaz). Her komutun mevcut guard adımına Auto-Fix Policy'yi bağlar. **Her edit'te: önce ilgili Adım'ı Read et, mevcut "critical/high → kullanıcı seçer" dilini bul, aşağıdaki binding ile değiştir/genişlet.**

- [ ] **Step 1: execute-plan — Adım 8.5 + Adım 12 binding**

`~/.claude/commands/execute-plan-claude-codex.md`, `### 8.5 Critical/high guard` ve `## Adım 12: Karar — Critical/High Guard` adımlarına ekle (mevcut critical/high guard dilinin yanına, onu değiştirerek):

```markdown
> **Auto-Fix Review Policy binding (bkz. "## Auto-Fix Review Policy" bloğu).** Bu guard'da
> "critical/high → kullanıcı seçer" yerine: **C/H/M `claude-confirmed` bulgular → kullanıcı
> onayı beklemeden Adım 7 RED-GREEN-REFACTOR mini-batch fix döngüsü** (executor arketipi: medium
> = fix-required). Tur≥4'te Codex çağrısı yapılandırılmış çözüm önerisi döner; cluster-key başına
> `6-tavan` + session `global cap=10` dolunca otonom döngü DURUR + kullanıcı raporu. low 4. turdan
> sonra audit-ignore. **Adım 9'daki "3 başarısız deneme" (per-task TDD breaker) AYRI kavramdır —
> DOKUNULMAZ, 6-tavan ile karıştırılmaz.** "Iteration-limit yok" invariantı korunur. Carve-out:
> push/state/override hâlâ insan-kapısı; executor local commit'leri mevcut task-başı cadence'i miras alır.
```

- [ ] **Step 2: simplify — Adım 10 binding**

`~/.claude/commands/simplify-claude-codex.md`, `## Adım 10: Critical/High Guard` adımına ekle:

```markdown
> **Auto-Fix Review Policy binding (bkz. "## Auto-Fix Review Policy" bloğu).** Unresolved C/H/M
> `claude-confirmed` bulgular → kullanıcı onayı beklemeden mini-batch fix döngüsü (executor arketipi:
> medium = fix-required). Tur≥4 Codex çözüm önerisi; cluster-key `6-tavan` + `global cap=10` →
> DUR + rapor. low 4. turdan sonra audit-ignore. "Iteration-limit yok" invariantı korunur. Carve-out:
> commit gate (final review etti + unresolved C/H yok VEYA override) değişmez; push sorulmaz.
```

- [ ] **Step 3: spec — Adım 7 binding**

`~/.claude/commands/spec-claude-codex.md`, `## Adım 7: Karar — Onayla / Güncelle` (ve `### Critical/high guard`) adımına ekle:

```markdown
> **Auto-Fix Review Policy binding (bkz. "## Auto-Fix Review Policy" bloğu).** C/H (+`technical-medium`)
> `claude-confirmed` bulgular → onay beklemeden spec-edit fix döngüsü, kapanana/`6-tavan`'a/`global cap=10`'a
> kadar (Mode A refine). **Zorunlu sınıflandırma:** her medium raporda açıkça `technical-medium →
> fix-required` veya `tradeoff-medium → user decision` etiketlenir + bir-satır gerekçe; belirsizse
> default = `tradeoff-medium`. `approved-by-iteration-limit` artık YALNIZ **low + tradeoff-medium**
> için (technical-medium iteration-limit ile sessizce geçilemez). Carve-out: vault/active-layer/override
> hâlâ insan-kapısı.
```

- [ ] **Step 4: write-plan — Adım 13/14 binding**

`~/.claude/commands/write-plan-claude-codex.md`, `## Adım 13: Karar` + `## Adım 14: Refine Loop` adımlarına ekle (spec ile simetrik):

```markdown
> **Auto-Fix Review Policy binding (bkz. "## Auto-Fix Review Policy" bloğu).** C/H (+`technical-medium`)
> `claude-confirmed` plan bulgusu → onay beklemeden Adım 14 Mode A refine fix döngüsü, kapanana/`6-tavan`/
> `global cap=10`'a kadar. Zorunlu medium sınıflandırma (`technical-medium → fix-required` vs
> `tradeoff-medium → user decision`, belirsizse default tradeoff). `approved-by-iteration-limit`
> YALNIZ low + tradeoff-medium. Adım 11 sayaç semantiği (full plan iteration) korunur. Carve-out:
> active-layer/override insan-kapısı.
```

- [ ] **Step 5: Drift-check — binding prose bloğu bozmadı**

```bash
REPO=$(git rev-parse --show-toplevel); bash "$REPO/docs/tools/claude-codex-drift-check.sh" 2>&1 | grep -E "Check D AUTO-FIX|byte drift"
```
Expected: hâlâ 4 komut `block present` + `tokens present`, **hiç `byte drift` yok** (binding prose marker DIŞINDA olduğu için extract değişmez). reviewer-token-check hâlâ FAIL (Task 6).

---

## Task 6: Reviewer prose (review + security-review) + reviewer token'lar

**Files:**
- Modify: `~/.claude/commands/{review,security-review}-claude-codex.md`

Reviewer'lar kod YAZMAZ → marker bloğu YOK. Yalnız disposition + chain-gate dili + handoff contract. Check D bu task'tan sonra GREEN olmalı — İKİ kapı: (1) `REVIEWER_TOKENS` (8 token) mevcut: `fix-required`, `medium advisory`, `chain-gate`, `report-only`, `critical`, `high`, `medium`, `low` (son 4 zaten vokabülerde; ilk 4 bu task'ta eklenir); (2) `check_reviewer_forbidden` PASS — hard-block satırında/altındaki bullet'ta medium'u tetikleyici sayan ifade YOK. Pozitif token tek başına yeterli değildir (Codex F2): chain-gate REPLACE edilir, eski medium-block dili kalmaz.

> **Negatif check = TRIPWIRE, tam ispat değil (Codex F9 + kullanıcı kararı 2026-06-03).** Spec yalnız
> POZİTİF reviewer token check ister; negatif `check_reviewer_forbidden` spec-ötesi bir tripwire'dır.
> Mechanical stale enumerasyonları (inline hard-block-satırı + bullet liste) yakalar; **wrapped-prose
> continuation'ı (`hard-block:` + sonraki prose satırı `…/medium`) YAKALAMAZ** — bu residual prose-regex
> arms-race'inin (F5/F7/F9) çözümsüzlüğünden bilinçli kabul edildi. Residual'ı şu katmanlar kapsar:
> **bu task'ın REPLACE-not-append disiplini** (eski enumerasyon silinir) + **manual scenario trace**
> (Task 8 Step 3) + **execution'da Codex'in gerçek reviewer-edit review'ı**. Yazım kuralı (executor'a):
> hard-block satırı self-contained `hard-block … critical/high` olsun; medium daima ayrı `advisory`
> cümlesinde, "hard-block" kelimesiyle aynı satırda DEĞİL.

- [ ] **Step 1: review — Adım 5 disposition dili**

`~/.claude/commands/review-claude-codex.md`, `## Adım 5: Sentez` (disposition ledger maddesi) + `## Adım 7: Kayıt` bölümüne ekle:

```markdown
> **Auto-Fix Review Policy (report-only reviewer).** Bu komut **kod yazmaz — fix döngüsü EKLENMEZ.**
> Disposition: `both-agree` C/H/M bulgular = **fix-required** (sentez raporunda yazılır). **TASK.md
> `# Open Problems` / HANDOFF `## Notes For Claude` yazımı YALNIZ mevcut açık kullanıcı onay
> kapısından geçer (Adım 8 mekanizması; carve-out — active-layer mutation insan-kapısı); onay
> yoksa bulgular stdout + review-log'da kalır, otomatik mutation YOK.** Fiili düzeltme handoff
> contract ile executor'da (`/execute-plan-claude-codex` veya hedefli `/simplify-claude-codex`)
> yapılır — orada Auto-Fix döngüsü işler. Re-review: fix sonrası `/review-claude-codex` resume;
> aynı cluster-key kapanınca gate temizlenir.
```

- [ ] **Step 2: review — Adım 9 chain-gate dili**

`## Adım 9: Docs Commit Gate` → `### Chain-advance gate` bölümünde: **append DEĞİL — REPLACE (Codex F2).**
Önce mevcut chain-advance hard-block cümlesini Read et; severity hard-block enumerasyonunda `medium`
geçen bir ifade varsa KALDIR — yalnız `critical/high` kalmalı. Eski cümleyi aşağıdaki kanonik blokla
değiştir (böylece pozitif token + eski medium-block dili AYNI ANDA bulunamaz; `check_reviewer_forbidden`
bunu zorlar):

**Yazım kuralı (Codex F7):** "hard-block" kelimesi YALNIZ critical/high'ı enumere eden satırda
geçsin; medium aynı satırda OLMASIN (medium ayrı `advisory` cümlesinde). `check_reviewer_forbidden`
bir hard-block satırının kendisinde/altındaki bullet'ta medium görürse FAIL eder.

```markdown
> **chain-gate eşiği (Auto-Fix Review Policy):** chain-advance hard-block YALNIZ **critical/high**'da
> (bugünküyle aynı; enumerasyon yalnız critical/high). **medium advisory** — fix-required işaretlenir
> + (onayla) Open Problems'a yazılır AMA tek başına chain-advance'i bloke ETMEZ (reviewer'da fixer
> yok). Yani medium, chain gate'ini ölü-bloke etmez; executor'da fix-required olarak tüketilir (tek
> kontrat: fix gerekli ama reviewer-chain'i ölü-bloke etmez).
```

- [ ] **Step 3: security-review — Adım 5 + Adım 9 dili (review ile aynı + güvenlik nüansı)**

`~/.claude/commands/security-review-claude-codex.md`, `## Adım 5: Güvenlik Sentezi`'ne ekle; `## Adım 9: ... İki Katmanlı Chain Gate`'te ise **append DEĞİL — REPLACE (Codex F2):** mevcut hard-block enumerasyonunda `medium` geçen ifade varsa kaldır (yalnız critical/high kalsın), eski cümleyi aşağıdaki kanonik blokla değiştir:

```markdown
> **Auto-Fix Review Policy (report-only güvenlik reviewer).** Kod yazmaz — fix döngüsü EKLENMEZ.
> Disposition: `both-agree` C/H/M = **fix-required** (sentez raporunda); medium fix-required
> (evidence_gap ≥ medium taban). **TASK.md `# Open Problems` / HANDOFF yazımı YALNIZ mevcut açık
> kullanıcı onay kapısından geçer (Adım 8; carve-out — active-layer mutation insan-kapısı); onay
> yoksa stdout + review-log'da kalır, otomatik mutation YOK.** chain-gate hard-block YALNIZ
> **critical/high** (security-risk override). **medium advisory** — fix-required + (onayla) Open
> Problems ama tek başına chain'i ölü-bloke etmez; executor'da fix-required tüketilir. **security-risk
> override AYRI kalır** (override = "bulgu doğru, riski kabul ediyorum" — fix değil; dual-review
> override'dan da ayrı).
```

- [ ] **Step 4: reviewer token'ları doğrula**

```bash
for f in review security-review; do
  echo "== $f =="
  # Pozitif: 8 token mevcut
  for t in fix-required 'medium advisory' chain-gate report-only critical high medium low; do
    grep -qF -- "$t" ~/.claude/commands/$f-claude-codex.md && echo "ok:$t" || echo "MISSING:$t"
  done
  # Negatif (Codex F2/F5/F7): enumeration-scoped — hard-block satırının KENDİSİ veya ardışık liste
  # öğesi medium/C/H/M içeriyor mu? (check_reviewer_forbidden'ın erken aynası — aynı mantık; ayrı
  # prose'daki `medium advisory` taranmaz → bypass yok)
  bad=$(awk '
    { raw[NR]=$0; low[NR]=tolower($0) }
    END{ for(i=1;i<=NR;i++){
      if(low[i] !~ /hard-?block/) continue
      line=low[i]; gsub(/ *\/ */,"/",line); gsub(/c\/h\/m/,"medium",line)
      if(line ~ /medium/){ print "L" i " inline: " raw[i]; continue }
      started=0
      for(j=i+1;j<=NR;j++){
        if(low[j] ~ /^[[:space:]>]*$/){ if(started) break; else continue }
        if(low[j] ~ /^[[:space:]>]*[-*+][[:space:]]/ || low[j] ~ /^[[:space:]>]*[0-9]+\.[[:space:]]/){
          started=1; item=low[j]; gsub(/ *\/ */,"/",item); gsub(/c\/h\/m/,"medium",item)
          if(item ~ /medium/){ print "L" j " bullet<-L" i ": " raw[j]; break }
        } else break
      } } }' ~/.claude/commands/$f-claude-codex.md)
  [ -z "$bad" ] && echo "ok:no-medium-hard-block" || echo "FORBIDDEN: $bad"
done
```
Expected: her komut için 8 satır `ok:<token>` + `ok:no-medium-hard-block`, hiç `MISSING`/`FORBIDDEN` yok. (Bu, `check_reviewer_forbidden`'ın Task 6 aşamasındaki erken aynası — medium'un hard-block tetikleyicisi olmadığını GERÇEKTEN doğrular, yalnız pozitif token varlığına güvenmez.)

- [ ] **Step 5: marker'ın reviewer'lara SIZMADIĞINI doğrula**

```bash
grep -l "AUTO-FIX-REVIEW-POLICY:BEGIN" ~/.claude/commands/{review,security-review,finish-branch}-claude-codex.md 2>/dev/null \
  && echo "UNEXPECTED marker leak" || echo "OK: reviewers/finish-branch have no auto-fix block"
```
Expected: `OK: reviewers/finish-branch have no auto-fix block`.

---

## Task 7: finish-branch kapsam-dışı notu (opsiyonel, 1 satır)

**Files:**
- Modify: `~/.claude/commands/finish-branch-claude-codex.md`

- [ ] **Step 1: Sözleşme Notları'na 1 satır ekle**

`~/.claude/commands/finish-branch-claude-codex.md` Sözleşme Notları (veya İnvariant) bölümüne ekle:

```markdown
- **Auto-Fix Review Policy kapsam DIŞI:** Bu komut severity sözlüğünü (`closure-blocker/warning/note`,
  STEP_B'siz) bilerek kullanır; C/H/M auto-fix politikası enjekte EDİLMEZ (closure-audit danışmadır,
  gate değil). AUTO-FIX-REVIEW-POLICY bloğu bu dosyada YOKTUR.
```

- [ ] **Step 2: Marker yokluğunu doğrula (zaten Task 6 Step 5'te kapsandı, teyit)**

```bash
grep -cF "AUTO-FIX-REVIEW-POLICY:BEGIN" ~/.claude/commands/finish-branch-claude-codex.md
```
Expected: `0`.

---

## Task 8: Final verify (A/B/C/D PASS) + smoke + senaryo trace + commit

**Files:**
- Read-only: tüm düzenlenen komut dosyaları
- Modify (commit edilir): `docs/tools/claude-codex-drift-check.sh` (zaten Task 2'de yazıldı)

- [ ] **Step 1: Tam drift-check — Check A/B/C/D hepsi PASS**

```bash
REPO=$(git rev-parse --show-toplevel); bash "$REPO/docs/tools/claude-codex-drift-check.sh"; echo "EXIT=$?"
```
Expected: `PASS: claude-codex drift check clean` + `EXIT=0`. (Check A 7-way + Check B + Check C 4-way + Check D 4-way block + reviewer token + S-1 literal — hepsi `ok`/PASS.)

- [ ] **Step 2: Smoke — markdown frontmatter + code-fence bütünlüğü (6 dosya)**

```bash
for c in spec write-plan execute-plan simplify review security-review; do
  f=~/.claude/commands/$c-claude-codex.md
  fm=$(awk 'NR==1 && $0=="---"{f++} NR>1 && $0=="---"{f++; exit} END{print f+0}' "$f")
  fences=$(grep -cE '^```' "$f")
  echo "$c: frontmatter_delims=$fm code_fences=$fences"
done
```
Expected: her komut `frontmatter_delims=2` (frontmatter bozulmamış) ve `code_fences` ÇİFT sayı (fence'ler dengeli). Tek sayı veya `frontmatter_delims<2` → bozuk parse, düzelt.

- [ ] **Step 3: Senaryo trace (prose — her komut için yürüyüş; çıktı yok, doğrulama)**

Aşağıdaki senaryoların her komutun yeni dilinde tutarlı izlendiğini prose ile doğrula. **Trace çıktısı default olarak stdout'a + review log'a (`docs/reviews/codex/2026-06-03-auto-fix-review-policy-plan.md`) yazılır.** TASK.md/HANDOFF.md'ye YALNIZ açık kullanıcı onayıyla işlenir — active-layer mutation carve-out gereği insan-kapısıdır (otomatik yazma YOK; bu execution sırasında zaten aktif task yok, CURRENT.md boş):
1. **C/H/M `claude-confirmed` → onaysız fix → re-review** (execute/simplify/spec/write-plan).
2. **Claude doğrulamayan bulgu → fix YOK**, ledger `needs-human`/`single-source`.
3. **6 tur aynı cluster-key → DUR + rapor**; **2. reopen → DUR**.
4. **low 4. tur → audit-ignore**.
5. **global cap=10 → DUR + rapor**.
6. **Carve-out:** push/state-mutation/vault/override hâlâ onay; executor local commit mevcut cadence.
7. **spec/write-plan:** `tradeoff-medium → iteration-limit`, `technical-medium → fix-required`.
8. **review/security:** kod yazmıyor, vocab = fix-required, **chain hard-block C/H'de; medium advisory + handoff/Open Problems**; security-risk override ayrı.
9. **finish-branch:** dokunulmadı, severity sözlüğü değişmedi.

- [ ] **Step 4: Behavioral smoke — drift-check fixture testi (re-runnable regresyon)**

Check D'yi izole bir fixture komut diziniğe karşı GERÇEKTEN çalıştır (`CLAUDE_CODEX_COMMAND_DIR` override; drift-check satır 13 destekliyor). Pozitif (temiz fixture → PASS) + negatif (bozuk blok → FAIL) — re-runnable regresyon, gerçek komut dizinine DOKUNMAZ.

```bash
REPO=$(git rev-parse --show-toplevel)
FX=$(mktemp -d /tmp/drift-d-fixture.XXXXXX)
cp ~/.claude/commands/*-claude-codex.md "$FX"/      # tüm aile (manifest + non-manifest) — tam dizin
# --- Pozitif: temiz fixture Check A/B/C/D PASS etmeli ---
CLAUDE_CODEX_COMMAND_DIR="$FX" bash "$REPO/docs/tools/claude-codex-drift-check.sh" >/dev/null 2>&1
echo "POSITIVE_EXIT=$?  (expect 0)"
# --- Negatif: beklenen 4 komuttan birinde AUTO-FIX blok marker'ını boz → Check D marker-count FAIL ---
sed -i '0,/AUTO-FIX-REVIEW-POLICY:BEGIN/s//AUTO-FIX-REVIEW-POLICY-BROKEN:BEGIN/' "$FX/simplify-claude-codex.md"
CLAUDE_CODEX_COMMAND_DIR="$FX" bash "$REPO/docs/tools/claude-codex-drift-check.sh" 2>&1 \
  | grep -E "Check D AUTO-FIX.*(marker count|byte drift).*simplify" && echo "NEG_FAIL_LINE_SEEN"
CLAUDE_CODEX_COMMAND_DIR="$FX" bash "$REPO/docs/tools/claude-codex-drift-check.sh" >/dev/null 2>&1
echo "NEGATIVE_EXIT=$?  (expect 1)"
# --- Negatif 2 (Codex F7): reviewer'a stale `hard-block: C/H/M` + yakına `medium advisory` enjekte
#     et → check_reviewer_forbidden FAIL etmeli (advisory-bypass kapalı; enumeration-scoped) ---
cp ~/.claude/commands/review-claude-codex.md "$FX/review-claude-codex.md"   # temiz kopya geri al
printf '\n### Chain-advance gate (stale)\nchain-advance hard-block: critical/high/medium blocked\n(stale). **medium advisory** — newly appended.\n' >> "$FX/review-claude-codex.md"
CLAUDE_CODEX_COMMAND_DIR="$FX" bash "$REPO/docs/tools/claude-codex-drift-check.sh" 2>&1 \
  | grep -E "Check D reviewer.*medium-as-hard-block.*review" && echo "F7_BYPASS_CAUGHT"
rm -rf "$FX"
```
Expected: `POSITIVE_EXIT=0`, `Check D AUTO-FIX ... simplify` FAIL satırı + `NEG_FAIL_LINE_SEEN`, `NEGATIVE_EXIT=1`, ve **`Check D reviewer ... medium-as-hard-block ... review` FAIL satırı + `F7_BYPASS_CAUGHT`** (enumeration-scoped check stale medium-hard-block'u yakına eklenen `medium advisory`'e RAĞMEN yakalar). Check D wiring + marker-count + reviewer-forbidden kapılarının drift'i re-runnable yakaladığını kanıtlar.

- [ ] **Step 5: drift-check.sh'i commit'le (repo-içi tek deliverable)**

```bash
REPO=$(git rev-parse --show-toplevel); cd "$REPO"
git add docs/tools/claude-codex-drift-check.sh
git status --short
git commit -m "test: add claude-codex drift-check Check D (auto-fix-review-policy 4-way + reviewer tokens)"
```
Expected: yalnız `docs/tools/claude-codex-drift-check.sh` staged + commit oluşur. **Push YOK.** (Komut dosyaları repo-DIŞı olduğu için commit'e girmez — bu beklenen.)

- [ ] **Step 6: Final doğrulama — temiz tree + drift PASS tekrar**

"Tam temiz tree" ASSERT ETME (Codex F6): plan dosyası + Codex review log + senaryo trace bilinen
untracked doc artefaktları olarak kalabilir (plan zaten `/write-plan` Adım 17'de commit'lenir; review
log/trace ayrı). Doğru kriter: commit sonrası **beklenmeyen TRACKED/staged değişiklik YOK** — untracked
doc'lara izin var.

```bash
REPO=$(git rev-parse --show-toplevel); cd "$REPO"
staged=$(git diff --cached --name-only)        # commit sonrası staged kalmamalı
modified=$(git diff --name-only)               # tracked dosyada unstaged modifikasyon olmamalı
echo "staged=[$staged]"; echo "modified=[$modified]"
{ [ -z "$staged" ] && [ -z "$modified" ]; } && echo "ok:no-tracked-pending" || echo "UNEXPECTED tracked change"
echo "--- untracked (yalnız bilinen doc artefaktları beklenir: plan / review-log / trace) ---"
git status --short --untracked-files=all | grep '^??' || echo "(none)"
bash "$REPO/docs/tools/claude-codex-drift-check.sh"; echo "EXIT=$?"
```
Expected: `ok:no-tracked-pending` (staged + modified ikisi de boş), untracked listesi yalnız bilinen
doc path'leri (`docs/reviews/codex/...-plan.md` ve varsa trace; plan Adım 17'de commit'lendiyse listede
olmaz), drift-check `PASS` + `EXIT=0`. Untracked doc'lar fail SEBEBİ DEĞİL — yalnız beklenmeyen tracked
değişiklik fail'dir.

---

## Self-Review (writing-plans — spec'e karşı)

**Spec coverage:**
- Tetik `claude-confirmed` → Block (Task 3) + binding (Task 5) ✓
- 6-tavan + cluster ledger + global cap=10 → Block (Task 3, ZORUNLU içerik) ✓
- Carve-out + commit nüansı → Block (Task 3) ✓
- medium tür-bazlı (technical/tradeoff) → Block + spec/write-plan binding (Task 5 Step 3/4) ✓
- low budget (≤3, 4.+ audit-ignore) → Block ✓
- Komut bazlı: execute/simplify (Task 5 Step 1/2), spec/write-plan (Task 5 Step 3/4), review/security (Task 6), finish-branch DIŞı (Task 7) ✓
- Mimari: byte-identical block 4-way (Task 3/4) + reviewer prose (Task 6) + Check D (Task 2) ✓
- Verification: drift A/B/C/D + smoke + scenario trace (Task 8) ✓

**Placeholder scan:** Block metni + Check D kodu tam; binding/reviewer prose tam metin. "read-then-edit" yönergeleri anchor + tam insert metni içerir (placeholder değil). ✓

**Type/anchor consistency:** Tripwire token'lar Block ↔ Check D arası eşleşiyor (`claude-confirmed`/`cluster-key`/`finding-id`/`global cap`/`6-tavan`/`reopen`); reviewer token'lar (8) Task 6 prose ↔ Check D `REVIEWER_TOKENS` eşleşiyor; negatif `check_reviewer_forbidden` regex disclaimer dilini (`advisory`/`İMA EDİLMEZ`/`ölü-bloke`/`YALNIZ`) hariç tutar → Task 6 kanonik prose ile uyumlu (false-positive yok). Insertion anchor'ları (`## Adım 0` / `## Adım 1` / guard adım başlıkları) grep ile doğrulandı. ✓

**Codex plan review fix'leri (Turn 1 — 2 high + 2 medium, hepsi claude-confirmed, çözüldü):**
- **F1 (high)** worktree-safe `$REPO=$(git rev-parse --show-toplevel)` + erken assertion → tüm drift-check/commit blokları (hard-coded `/root/otomaix` kaldırıldı). ✓
- **F2 (high)** reviewer negatif kapı `check_reviewer_forbidden` (Task 2) + chain-gate REPLACE-not-append (Task 6 Step 2/3) → pozitif `medium advisory` token'ı tek başına medium'un hard-block olmadığını kanıtlamıyordu; artık negatif kontrol + eski metni kaldırma zorunlu. ✓
- **F3 (medium)** Task 8 Step 4 gerçek re-runnable regresyon (`CLAUDE_CODEX_COMMAND_DIR=fixture` pozitif+negatif, `NEGATIVE_EXIT=1` assert). ✓
- **F4 (medium)** Task 8 Step 3 senaryo trace default stdout/review-log; TASK/HANDOFF YALNIZ açık onayla (carve-out). ✓

**Codex plan review Turn 2 fix'leri (1 high + 1 medium, claude-confirmed, çözüldü):**
- **F5 (high)** `check_reviewer_forbidden` line-local → **windowed** (5-satır pencere, çok-satırlı bullet enumerasyonu yakalar) + POSIX `tolower()` (Medium/MEDIUM) + `C/H/M` (boşluklu dahil) normalize + `advisory` ASCII exclusion. 5 fixture ile ampirik doğrulandı (canonical temiz / multiline+CHM+capital-Medium flag / sadece-CH temiz). ✓
- **F6 (medium)** Task 8 Step 6 "tam temiz tree" assert'i kaldırıldı → **beklenmeyen tracked/staged değişiklik yok** kriteri; untracked doc artefaktlarına (plan/review-log/trace) izin. ✓

**Codex plan review Turn 3 fix'leri (1 high + 1 medium, claude-confirmed, çözüldü):**
- **F7 (high)** advisory-exclusion bypass edilebilirdi (eski `hard-block: C/H/M` + yakına `medium advisory`). → **enumeration-scoped** check: hard-block satırının KENDİSİ veya altındaki ardışık liste öğesi medium içerirse FAIL; ayrı prose'daki `medium advisory` taranmaz. Trigger `hard-?block`-only (disclaimer FP'si önlendi). Kanonik prose "hard-block" ile "medium"u aynı satıra koymama kuralıyla yeniden yazıldı. 8 case ampirik doğrulandı (gerçek review+security prose clean; inline/multiline/bullet/spaced-CHM + F7-bypass flag; only-CH + alakasız temiz). Task 8 Step 4'e F7 bypass fixture testi eklendi (`F7_BYPASS_CAUGHT`). ✓
- **F8 (medium)** Reviewer insert prose'una (review Step 1 + security Step 3) Open Problems/HANDOFF yazımının **açık kullanıcı onay kapısı** (Adım 8; carve-out) yinelendi; onay yoksa stdout/review-log'da kalır. ✓

**Codex plan review Turn 4 (1 high — F9; kullanıcı kararıyla DOKÜMANTE residual):**
- **F9 (high)** Negatif check wrapped-prose continuation'ı (`hard-block:` + sonraki prose satırı `…/medium`) yakalamıyor. Bu, reviewer-negatif-check'in 3. ardışık regex-bypass'ı (F5/F7/F9) → **prose'dan semantik negatif kanıtlama yakınsamıyor**. Negatif check spec-ötesi gold-plating (spec POZİTİF check ister, o geçer). **Kullanıcı kararı (2026-06-03):** check'i TRIPWIRE olarak kabul + residual'ı belgele (mechanical inline+bullet yakalanır; wrapped-prose REPLACE-not-append + manual trace + execution Codex review ile kapsanır). Plan → `approved-by-iteration-limit`; `unresolved_high_severity_override: true` (şeffaflık — tripwire eksikliği bilinçli kabul; audit log + final rapor listeler).
