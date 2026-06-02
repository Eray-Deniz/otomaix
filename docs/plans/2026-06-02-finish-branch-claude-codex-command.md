---
title: finish-branch-claude-codex.md — Implementation Plan
status: plan-approved
date: 2026-06-02
source_spec: docs/specs/2026-06-02-finish-branch-claude-codex-command.md
source_spec_unapproved_override: false
noisy_review_override: false
unresolved_high_severity_override: false
codex_plan_review_status: approved
codex_plan_review_iterations: 1
codex_plan_targeted_fixes: 3
codex_plan_review_log: docs/reviews/codex/2026-06-02-finish-branch-claude-codex-command-plan.md
---

# finish-branch-claude-codex.md Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `~/.claude/commands/finish-branch-claude-codex.md` komutunu oluştur — mevcut `/finish-branch`'i claude-codex ailesine entegre eden advisory closure-readiness audit; aile drift contract'ını 6-way → 7-way büyüt; eski `/finish-branch`'i deprecated stub'a indirge.

**Architecture:** Hibrit — finish-branch'in mevcut 8-adımlık closure semantics'i (task-layer matrix, Adım6→7 sıra disiplini, detached dalları) **davranışsal baz**; security-review-claude-codex'in repo-external **delivery scaffold'u** (backup → canonical extract → byte-identical insert → 7-way drift verify → chain sweep → stub → smoke → docs-only audit commit). Codex rolü advisory closure-audit (gate DEĞİL); topoloji security-review'dan KOPYALANMAZ (dual-review/gated sızması yasak).

**Tech Stack:** Markdown komut dosyası (repo-dışı `~/.claude/commands/`); doğrulama bash (`awk`/`md5sum`/`python3` frontmatter parse); `codex-companion.mjs` (CODEX-CALL-PROTOCOL). Deliverable repo-dışı → smoke = load+parse + hash + sweep; gerçek invoke restart ister.

**Kaynak referansları:** Spec `docs/specs/2026-06-02-finish-branch-claude-codex-command.md` (canonical kararlar); pattern `docs/plans/2026-06-01-security-review-claude-codex-command.md` (repo-external delivery); baz davranış `~/.claude/commands/finish-branch.md`; canonical blok `~/.claude/commands/spec-claude-codex.md`.

---

## File Structure

**Repo-dışı (deliverable — commit EDİLMEZ):**
- Create: `~/.claude/commands/finish-branch-claude-codex.md` (yeni komut)
- Modify: `~/.claude/commands/{spec,write-plan,execute-plan,simplify,review,security-review}-claude-codex.md` (6 sibling — 7-way binding prose bump, marker DIŞI)
- Modify: `~/.claude/commands/init.md` (chain-ref sweep kapsamı — Codex)
- Rewrite: `~/.claude/commands/finish-branch.md` → deprecated stub
- Backup: `~/.claude/commands/*.bak-<ts>` (tüm dokunulanlar)

**Repo-içi (commit edilir — docs-only audit):**
- `docs/reviews/codex/2026-06-02-finish-branch-claude-codex-command-plan.md` (bu plan'ın Codex review log'u)
- Audit commit: docs-only (komut dosyaları repo-dışı)

---

## Task 1: Baseline — backup + canonical extract + 6-way intact teyit

**Files:**
- Backup: `~/.claude/commands/*.bak-<ts>`
- Read: `~/.claude/commands/spec-claude-codex.md` (canonical CODEX-CALL-PROTOCOL kaynağı)

- [ ] **Step 1: Backup tüm dokunulacak komut dosyaları**

```bash
TS=$(date +%Y%m%d-%H%M%S)
for f in spec write-plan execute-plan simplify review security-review finish-branch; do
  cp ~/.claude/commands/$f-claude-codex.md ~/.claude/commands/$f-claude-codex.md.bak-$TS 2>/dev/null
done
cp ~/.claude/commands/finish-branch.md ~/.claude/commands/finish-branch.md.bak-$TS
cp ~/.claude/commands/init.md ~/.claude/commands/init.md.bak-$TS
ls ~/.claude/commands/*.bak-$TS | wc -l
```
Expected: 8 (6 `*-claude-codex` sibling: spec/write-plan/execute-plan/simplify/review/security-review + `finish-branch.md` + `init.md`).

- [ ] **Step 2: Canonical CODEX-CALL-PROTOCOL bloğunu extract et (marker-aware awk)**

```bash
awk '/<!-- CODEX-CALL-PROTOCOL:BEGIN/,/<!-- CODEX-CALL-PROTOCOL:END -->/' \
  ~/.claude/commands/spec-claude-codex.md > /tmp/codex-call-protocol.block
wc -l /tmp/codex-call-protocol.block
md5sum /tmp/codex-call-protocol.block | cut -d' ' -f1
```
Expected: 68 satır; md5 `c7b5976c9513391909310883c40575c3`.

- [ ] **Step 3: Mevcut 6-way intact mı doğrula (7. eklemeden ÖNCE — baseline drift varsa DUR)**

```bash
for f in spec write-plan execute-plan simplify review security-review; do
  awk '/<!-- CODEX-CALL-PROTOCOL:BEGIN/,/<!-- CODEX-CALL-PROTOCOL:END -->/' \
    ~/.claude/commands/$f-claude-codex.md | md5sum | cut -d' ' -f1
done | sort -u | wc -l
```
Expected: `1` (6 dosya tek md5 = `c7b5976c...`). **Değilse DUR** — baseline aile zaten drift'li, önce o düzeltilmeli.

---

## Task 2: Komut gövdesi — frontmatter + görev + advisory invariant + 9-adım iskelet

**Files:**
- Create: `~/.claude/commands/finish-branch-claude-codex.md`

- [ ] **Step 1: Frontmatter + Görev + Aileden-Fark bölümü yaz**

Frontmatter:
```yaml
---
description: "Advisory closure-readiness audit ile branch kapanışı (merge/PR/tut/sil); tek Codex task --fresh closure-audit — gate DEĞİL; mode-aware (normal/mainline/detached); eski /finish-branch'in claude-codex aile eşi (drift-check 7-way)"
argument-hint: "[--no-audit]"
---
```
Görev: spec §Hedef + §Aileden-Fark özeti (lifecycle orchestration, Codex = closure-readiness audit, kod/güvenlik review DEĞİL).

- [ ] **Step 2: İnvariant bölümü — advisory + tek istisna (spec'ten birebir)**

İki blockquote: (a) "GATE değil, advisory; Codex degrade kapanışı bloke etmez; chain-advance gate UYGULANMAZ (aileden bilinçli sapma)"; (b) tek istisna invariant'ı **birebir**: *"closure-blocker is not a gate, except it upgrades destructive discard confirmation text."* + iki-fazlı blocker türetme (aksiyon-nötr facts → Adım 8 reclassify).

- [ ] **Step 3: 9-adım akış iskeleti (finish-branch 8 adım KORUNUR + audit)**

Akış listesi (spec §Adım Akışı): 1 mod-tespit+CLI, 2 test, 3 skill, 4 worktree+izolasyon, **5 ★Codex closure-audit (YENİ)**, 6 seçenek-sun (facts enjekte), 7 task-layer closure matrix, 8 branch-op (reclassify + D=sil upgrade), 9 bitiş. Sıra disiplini notu: Adım 7 (task closure) Adım 8 (branch-op) ÖNCE.

- [ ] **Step 4: Frontmatter parse smoke**

```bash
python3 -c "
import re
t=open('/root/.claude/commands/finish-branch-claude-codex.md').read()
m=re.match(r'^---\n(.*?)\n---\n', t, re.S); assert m, 'NO frontmatter'
print('frontmatter PARSE OK')"
```
Expected: `frontmatter PARSE OK`.

---

## Task 3: CODEX-CALL-PROTOCOL byte-identical insert

**Files:**
- Modify: `~/.claude/commands/finish-branch-claude-codex.md`

- [ ] **Step 1: Codex Çağrı Noktası tablosu + binding metni (marker DIŞI)**

Tablo: Adım 5 | `task --fresh` (STEP_A) | closure-readiness audit (advisory) | default açık (degradation → akış devam). Binding: "bu komut yalnız `<STEP_A>`'yı kullanır; `<STEP_B>` (`adversarial-review`) canonical blokta tanımlı ama KULLANILMAZ (superset). Drift-check 7-way: bloğu değiştirirsen canonical + 6 ayna senkronla."

- [ ] **Step 2: Bloğu Task 1'in temp dosyasından byte-identical yapıştır (hand-edit YOK)**

```bash
# Binding satırından sonra, marker-keyed mekanik insert. Blok /tmp/codex-call-protocol.block'tan.
# (Execution: editor/awk ile binding sonrası konuma temp block içeriği aynen eklenir.)
```
Marker satırları (`<!-- ...BEGIN -->` / `<!-- ...END -->`) ve aradaki 68 satır AYNEN. Prose'da literal marker token'ı YOK (extraction'ı kirletmesin).

- [ ] **Step 3: Blok md5 == canonical doğrula**

```bash
awk '/<!-- CODEX-CALL-PROTOCOL:BEGIN/,/<!-- CODEX-CALL-PROTOCOL:END -->/' \
  ~/.claude/commands/finish-branch-claude-codex.md | md5sum | cut -d' ' -f1
```
Expected: `c7b5976c9513391909310883c40575c3` (canonical ile birebir).

---

## Task 4: finish-branch security mechanics — prose (spec fidelity)

**Files:**
- Modify: `~/.claude/commands/finish-branch-claude-codex.md`

Spec'in güvenlik mekaniğini komut prose'una **eksiksiz** indir (Codex riski #3: prose→command fidelity). Her alt-madde spec'in ilgili Kararı/Adımı ile birebir:

- [ ] **Step 1: Adım 1 — deterministik mod tespiti (spec Adım 1)**

```bash
CUR=$(git branch --show-current)
DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
# CUR boş/HEAD → detached; CUR==DEFAULT → mainline; CUR!=DEFAULT isimli → normal
# Belirsizlik (origin/HEAD yok/stale, rename, upstream yok) → AskUserQuestion (inference YASAK)
# --no-audit → AUDIT_ENABLED=false
```

- [ ] **Step 2: Adım 4-5 — mode-aware izolasyon + HEAD pin + Codex closure-audit**

**SCAN_ROOT binding (Codex live-root audit'i engelleyen kritik bağ — T3 high):**
- normal → `git worktree add --detach "$WT" "$HEAD_SHA"` (worktree **HEAD_SHA'da** pinli), `SCAN_ROOT="$WT"`
- mainline → worktree yok, `SCAN_ROOT="$PROJECT_ROOT"` + `HEAD_SHA` pin + post-call/pre-op guard
- detached → dar kapsam

**Codex daima `--cwd "$SCAN_ROOT"`** ile çağrılır → normal mode'da pinli worktree audit edilir (live root DEĞİL); mainline'da proje kökü. Adım 5: HEAD pin → evidence topla (range diff snapshot + range-containment) → Codex `task --fresh --cwd "$SCAN_ROOT"` closure-only prompt → aksiyon-nötr facts → log → post-call HEAD guard (`git rev-parse HEAD == $HEAD_SHA`, değişmişse invalidate+recompute).

- [ ] **Step 3: Adım 5 — evidence range-containment (spec Karar 4)**

`report_HEAD == audit_HEAD` **AND** `git merge-base --is-ancestor report_BASE audit_BASE`; SHA eksik/karşılaştırılamaz → coverage-uncertain. Fallback (rapor SHA yok) → mtime/commit-history heuristik. Claude toplar, Codex yorumlar.

- [ ] **Step 4: Adım 5 — closure vocab + negative instruction (scope-creep guardrail)**

Codex prompt: `closure-blocker / closure-warning / closure-note` (severity YASAK) + negative "do NOT hunt code-quality/security bugs" + mevcut review/security rapor yolları + exact range diff snapshot ("yalnız bu range üzerinde rapor ver") + reduced-value notu (mainline/detached).

- [ ] **Step 5: Adım 8 — pinned-target binding + old-value-bound discard + two-phase reclassify (spec Karar 3 + Adım 8)**

push `git push origin ${HEAD_SHA}:refs/heads/<default-branch>`; merge `git merge ${HEAD_SHA}`; **D=sil `git update-ref -d refs/heads/<branch> $HEAD_SHA`** (branch -D DEĞİL); diverge → abort+recompute. Two-phase: facts × seçilen-aksiyon → blocker/warning; D=sil + reclassified-blocker → `discard despite closure blockers` upgrade; degrade+D=sil → defansif retry/uyarı.

- [ ] **Step 6: Adım 6-7-9 + Sözleşme + Out-of-Scope (closure matrix korunur)**

Adım 6 seçenek-sun (facts enjekte); Adım 7 task-layer closure matrix (A/D full+archive, B waiting-review, C no-op — finish-branch'ten aynen); Adım 9 bitiş raporu. Sözleşme Notları (advisory-only sapma, scope-creep guardrail, Codex read-only, mevcut davranış korunur). Out-of-Scope (spec'ten).

- [ ] **Step 7: Section-scoped fidelity gates (broad grep DEĞİL — Codex T1 high)**

Her kritik mekanik **kendi bölümünde** mi? Whole-file count yanlış-PASS verir (token drift-prose/invariant-tekrarında geçebilir). Bölüm çıkar + concrete predicate assert; herhangi biri FAIL → task FAIL (final smoke'tan ÖNCE):

```bash
CMD=~/.claude/commands/finish-branch-claude-codex.md
fail=0
# Adım 1 — deterministik mode-detection + ambiguity stop-and-ask
s1=$(awk '/### Adım 1:/,/### Adım [2-9]:/' "$CMD")
echo "$s1" | grep -q "symbolic-ref refs/remotes/origin/HEAD" || { echo "FAIL: mode-detect predicate"; fail=1; }
echo "$s1" | grep -qiE "belirsiz|AskUserQuestion" || { echo "FAIL: mode ambiguity stop"; fail=1; }
# Adım 4 — mode-aware izolasyon: worktree@HEAD_SHA + SCAN_ROOT binding (Codex T3 high — live-root audit engeli)
s4=$(awk '/### Adım 4:/,/### Adım 5:/' "$CMD")
echo "$s4" | grep -qE 'worktree add --detach.*HEAD_SHA' || { echo "FAIL: worktree pinned AT HEAD_SHA"; fail=1; }
echo "$s4" | grep -qE 'SCAN_ROOT=.*WT' || { echo "FAIL: normal-mode SCAN_ROOT=\$WT (pinli worktree kullanılır)"; fail=1; }
echo "$s4" | grep -qE 'SCAN_ROOT=.*PROJECT_ROOT' || { echo "FAIL: mainline-mode SCAN_ROOT=\$PROJECT_ROOT branch"; fail=1; }
# Adım 5 — Codex --cwd binding + range-containment + EXECUTABLE HEAD guard + vocab + negative
s5=$(awk '/### Adım 5:/,/### Adım [6-9]:/' "$CMD")
echo "$s5" | grep -q "task --fresh" || { echo "FAIL: STEP_A binding"; fail=1; }
echo "$s5" | grep -qE 'cwd.*SCAN_ROOT' || { echo "FAIL: Codex --cwd SCAN_ROOT (live-root audit engeli)"; fail=1; }
echo "$s5" | grep -q "report_HEAD == audit_HEAD" || { echo "FAIL: range-containment HEAD eq"; fail=1; }
echo "$s5" | grep -q "merge-base --is-ancestor" || { echo "FAIL: range-containment ancestry"; fail=1; }
echo "$s5" | grep -qE "rev-parse HEAD.*HEAD_SHA|HEAD == .*HEAD_SHA" || { echo "FAIL: executable HEAD guard (prose 'pin' yetmez)"; fail=1; }
echo "$s5" | grep -qE "closure-blocker|closure-warning|closure-note" || { echo "FAIL: closure vocab"; fail=1; }
echo "$s5" | grep -qiE "do NOT hunt|kod kalitesi.*ARAMA" || { echo "FAIL: scope-creep negative"; fail=1; }
# Adım 8 — pinned-target + old-value discard + reclassify + upgrade text
s8=$(awk '/### Adım 8:/,/### Adım 9:/' "$CMD")
echo "$s8" | grep -q 'update-ref -d refs/heads' || { echo "FAIL: old-value discard"; fail=1; }
echo "$s8" | grep -qE '\$\{?HEAD_SHA\}?:refs/heads|push.*HEAD_SHA' || { echo "FAIL: pinned push refspec"; fail=1; }
echo "$s8" | grep -q "discard despite closure blockers" || { echo "FAIL: upgraded discard text"; fail=1; }
echo "$s8" | grep -qiE "reclassif|aksiyon-nötr|seçilen aksiyon" || { echo "FAIL: two-phase reclassify"; fail=1; }
[ "$fail" = 0 ] && echo "ALL SECTION GATES PASS" || echo "SECTION GATES FAILED — task incomplete"
```
Expected: `ALL SECTION GATES PASS`. Herhangi bir FAIL → ilgili mekanik komut metnine eksik inmiş → düzelt + tekrar koş (final smoke'tan önce).

---

## Task 5: 6→7 sibling drift prose bump (marker DIŞI, mekanik)

**Files:**
- Modify: 6 sibling `*-claude-codex.md` (Drift Sözleşmesi + binding prose: "6-way → 7-way", finish-branch ayna ekle)

- [ ] **Step 1: Her sibling'de drift prose'u 7-way'e bump et (marker DIŞINDA)**

Her dosyada: "Drift Sözleşmesi (6-way)" → "(7-way)"; ayna listesine `finish-branch-claude-codex.md` ekle; "altı komut"/"6-way" → "yedi komut"/"7-way"; Check A diff sayısı 5→6; "biri değişirse diğeri de" 6→7. **CODEX-CALL-PROTOCOL bloğunun KENDİSİNE dokunma** (byte-identical kalmalı).

- [ ] **Step 2: Blok byte-identity korundu mu (bump marker'a sızmadı)**

```bash
for f in spec write-plan execute-plan simplify review security-review finish-branch; do
  awk '/<!-- CODEX-CALL-PROTOCOL:BEGIN/,/<!-- CODEX-CALL-PROTOCOL:END -->/' \
    ~/.claude/commands/$f-claude-codex.md | md5sum | cut -d' ' -f1
done | sort -u
```
Expected: tek satır `c7b5976c9513391909310883c40575c3` (7 dosya, blok değişmedi).

---

## Task 6: Chain-ref sweep (siblings + init.md)

**Files:**
- Modify: live `/finish-branch` chain-target referansı taşıyan dosyalar

- [ ] **Step 1: Aktif `/finish-branch` chain referanslarını bul**

```bash
grep -nE "/finish-branch([^-]|$)" ~/.claude/commands/*.md | grep -viE "deprecated|eski|stub|finish-branch-claude"
```
Beklenen hit'ler: review/security-review "Sonraki adım/closure (`/finish-branch`)" + init.md + workflow şemaları.

- [ ] **Step 2: Live chain-target'ları `/finish-branch-claude-codex`'e güncelle**

Yalnız **aktif workflow chain** referansları (örn. "closure: `/finish-branch`" → "`/finish-branch-claude-codex`"). **Deprecated/tarihsel/örnek etiketleri KORU** (hit-by-hit gerekçe — Codex).

- [ ] **Step 3: Sweep temiz mi (kalan aktif eski-ref yok)**

```bash
grep -nE "/finish-branch([^-]|$)" ~/.claude/commands/*.md | grep -viE "deprecated|eski|stub|finish-branch-claude|tarihsel|örnek"
```
Expected: boş (veya yalnız kasıtlı-korunan tarihsel hit'ler, gerekçeli).

---

## Task 7: Eski /finish-branch → deprecated stub

**Files:**
- Rewrite: `~/.claude/commands/finish-branch.md`

- [ ] **Step 1: Stub yaz (security-review.md deprecated pattern'i)**

İçerik: "DEPRECATED → use `/finish-branch-claude-codex`" + 1-2 satır gerekçe (claude-codex ailesi, advisory closure-audit) + eski davranışın kaldırıldığı notu. Frontmatter `description: "[DEPRECATED] use /finish-branch-claude-codex"`.

- [ ] **Step 2: Stub frontmatter parse**

```bash
python3 -c "import re; t=open('/root/.claude/commands/finish-branch.md').read(); assert re.match(r'^---\n.*?\n---\n', t, re.S); print('stub OK')"
```
Expected: `stub OK`.

---

## Task 8: Doğrulama suite + docs-only audit commit

**Files:**
- Create: docs audit (repo-içi); komut dosyaları repo-dışı (commit edilmez)

- [ ] **Step 1: 7-way Check A (hash) + Check B (tripwire ×7)**

```bash
echo "--- Check A (7-way, tek md5) ---"
for f in spec write-plan execute-plan simplify review security-review finish-branch; do
  awk '/<!-- CODEX-CALL-PROTOCOL:BEGIN/,/<!-- CODEX-CALL-PROTOCOL:END -->/' \
    ~/.claude/commands/$f-claude-codex.md | md5sum | cut -d' ' -f1
done | sort -u
echo "--- Check B (her token 7 dosyada) ---"
for tok in "codex-companion.mjs" "git rev-parse" "AGENTS.md" "timeout 480s" "124" "Claude-only devam et" "Tekrar dene" "Komutu durdur"; do
  n=$(for f in spec write-plan execute-plan simplify review security-review finish-branch; do
    awk '/<!-- CODEX-CALL-PROTOCOL:BEGIN/,/<!-- CODEX-CALL-PROTOCOL:END -->/' ~/.claude/commands/$f-claude-codex.md | grep -cF "$tok"; done | grep -c '^[1-9]')
  echo "$n/7  $tok"
done
```
Expected: Check A tek `c7b5976c...`; Check B her token `7/7`.

- [ ] **Step 2: Stale-prose sweep (eski 6-way / aile sayısı kalmadı mı)**

```bash
grep -lnE "6-way|altı komut|6 komut" ~/.claude/commands/*-claude-codex.md
```
Expected: boş (tüm aktif prose 7-way). Tarihsel/log referansı varsa gerekçeli korunur.

- [ ] **Step 3: Load+parse smoke (tüm dokunulanlar)**

```bash
for f in finish-branch-claude-codex spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex review-claude-codex security-review-claude-codex finish-branch init; do
  python3 -c "import re,sys; t=open('/root/.claude/commands/$f.md').read(); sys.exit(0 if re.match(r'^---\n.*?\n---\n',t,re.S) else 1)" && echo "OK $f" || echo "FAIL $f"
done
```
Expected: tümü `OK`.

- [ ] **Step 4: Docs-only audit commit — explicit allowlist (`git add docs/` YASAK — Codex T1 medium)**

```bash
cd /root/otomaix
EXPECTED=$(printf '%s\n' \
  docs/specs/2026-06-02-finish-branch-claude-codex-command.md \
  docs/plans/2026-06-02-finish-branch-claude-codex-command.md \
  docs/reviews/codex/2026-06-02-finish-branch-claude-codex-command.md \
  docs/reviews/codex/2026-06-02-finish-branch-claude-codex-command-plan.md | sort)
git reset -q                       # önceki stale staged index'i temizle (Codex T2 medium: index zaten kirli olabilir)
git add -- \
  docs/specs/2026-06-02-finish-branch-claude-codex-command.md \
  docs/plans/2026-06-02-finish-branch-claude-codex-command.md \
  docs/reviews/codex/2026-06-02-finish-branch-claude-codex-command.md \
  docs/reviews/codex/2026-06-02-finish-branch-claude-codex-command-plan.md
# HARD allowlist gate (fail-closed) — print-only DEĞİL: fark varsa commit YAPMA
STAGED=$(git diff --cached --name-only | sort)
[ "$STAGED" = "$EXPECTED" ] || { echo "FAIL: staged set beklenenle eşleşmiyor — commit DURDU:"; diff <(echo "$EXPECTED") <(echo "$STAGED"); exit 1; }
git commit -m "docs: finish-branch-claude-codex command build (docs audit; command files external)"
```
Expected: `STAGED == EXPECTED` (yalnız 4 dosya); fark → `exit 1`, commit yapılmaz. **Push YOK** (closure'a ait). Restart sonrası `/finish-branch-claude-codex` aktif (smoke geçti; gerçek invoke restart ister).

- [ ] **Step 5: Final rapor — doğrulanan vs test-edilmeyen ayrımı**

Raporla: ✅ doğrulanan (7-way hash, Check B, frontmatter parse, chain sweep, stale sweep) + ⏳ test-edilmeyen (gerçek closure-audit davranışı — restart + canlı branch ister). Backup rollback yolu: `*.bak-<ts>`.

---

## Self-Review (writing-plans)

**Spec coverage:** Advisory invariant + discard istisnası (Task 2 S2) · mode-detection (Task 4 S1) · mode-aware izolasyon + HEAD guard (Task 4 S2) · range-containment (Task 4 S3) · closure vocab + negative (Task 4 S4) · pinned-target + old-value discard + two-phase (Task 4 S5) · closure matrix korunur (Task 4 S6) · 7-way drift (Task 1/3/5/8) · chain sweep (Task 6) · deprecated stub (Task 7) · repo-external delivery (Task 8). ✓ Tüm spec Kararları/Adımları bir task'a maplenmiş.

**Placeholder scan:** Kod step'leri tam bash/komut içerir; uzun prose bölümleri spec'in ilgili Kararına birebir referanslı (komut metninin tam 600+ satırı execution'da yazılır — bu plan yapı + kritik mekanik snippet'leri verir, security-review plan pattern'i). Verification step'leri tam komut + expected çıktı.

**Type consistency:** md5 `c7b5976c` Task 1/3/5/8'de tutarlı; HEAD_SHA/audit_BASE/report_BASE isimleri Task 4 boyunca tutarlı; closure vocab (`closure-blocker/warning/note`) Task 2/4'te tutarlı.
