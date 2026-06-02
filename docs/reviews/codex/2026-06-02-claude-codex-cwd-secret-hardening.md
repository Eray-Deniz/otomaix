# Codex Adversarial Review Log — claude-codex-cwd-secret-hardening

## Turn 1 — 2026-06-02 18:09 UTC

Target: working tree diff
Verdict: needs-attention

No-ship: the spec's substrate can either miss committed execution diffs or copy secrets into the temp repo, so the chosen design is not yet safe enough to implement.

Findings:
- [critical] Synthetic repo loses history needed by existing --base review paths (spec:95-101)
  execute-plan checkpoint/final use `--base $BASE_REF` on clean tree (TDD commits). Synthetic substrate (archive HEAD → single baseline) has no base ref → branch review fails at merge-base, or working-tree diff is empty (commits folded into baseline). Review gate silently weakened.
  Fix: support branch/base scopes explicitly — synthesize repo with required base commit + dirty overlay, or keep execute-plan base reviews on a separate mechanism. Per-call-site scope matrix.
- [high] Overlay cp follows symlinks before the sweep → secret exfiltration (spec:115-126)
  Plain `cp` derefs symlinks; untracked non-ignored symlink notes.txt -> backend/.env copied as regular file with secret content; `find -type l` sweep can't catch it (no longer a symlink).
  Fix: detect/resolve symlink targets before copy; fail-closed on escape; `cp -P` after target validation; verify no copied regular file came from a secret target.
- [high] Untracked-new "fail-closed" is path-blacklist + incomplete (spec:72-77)
  Copies every ls-files --others --exclude-standard path unless name matches small blacklist. Non-gitignored secret with neutral name (local-config.json, prod.token, private.envrc) slips through. Spec admits list is "example" → contradicts fail-closed claim. Core weakness vs dropped mirror C.
  Fix: don't call fail-closed unless allow-listed by command/output type; prefer scope-limited allow-list or per-file user approval + content classification.
- [medium] Build failures → partial SCAN_ROOT not fail-closed (spec:89-130)
  No `set -euo pipefail`, no per-op checks; while-loop failures masked; can set SCAN_ROOT=TMP with incomplete repo → Codex reviews truncated/stale diff.
  Fix: explicit fail-closed function, set -euo pipefail, NUL-safe loops, checked copies, post-build path-set verification before SCAN_ROOT.
- [medium] Repeated rebuilds leak temp dirs (trap tracks only latest TMP) (spec:92-93)
  execute-plan rebuilds multiple times/shell; each trap replaces prior, expands final TMP at exit → earlier temp repos (snapshots + untracked content) leak under /tmp.
  Fix: track all temp dirs / single cleanup trap, or clean each SCAN_ROOT right after its call; test no /tmp/wts.* remain.

Next steps: revise spec before implementation (execute-plan base-scope design + symlink/untracked secret gates); add empirical cases (committed exec diffs, symlink-to-secret, copy failures, repeated rebuild cleanup).

---

## Turn 2 — 2026-06-02 18:16 UTC

Target: working tree diff
Verdict: needs-attention (design direction fixed; executable bash gaps remain)

Findings:
- [high] WTS cleanup still leaks: build_wts called in $(...) command substitution → WTS_TMPDIRS+= lost in subshell → parent EXIT trap sees empty array → synthetic repos not removed. Reopens Turn 1 leak.
  Fix: don't return path via $() while mutating cleanup state; set caller global (printf -v / WTS_SCAN_ROOT), call as `build_wts || ...; SCAN_ROOT=$WTS_SCAN_ROOT`.
- [high] Substrate B not implementable: $HEAD_SHA undefined in revised spec; execute-plan only defines BASE_REF/execute_start_ref/SCOPE. + dirty-tree --scope working-tree branch left open.
  Fix: define HEAD_SHA=$(git rev-parse --verify HEAD) at each execute-plan review point; resolve dirty-tree branch (route to Substrate A or hard-stop/degrade) — remove open execution-time choice.
- [medium] Tracked-dirty parser mismatches `git diff -z --name-status`: -z emits NUL-separated FIELDS not tab records; `read -r -d '' st p new` puts status in st, leaves p empty → _wts_copy_safe gets empty relpath → copies repo root; with set -e Substrate A fails for ordinary modified files.
  Fix: parse NUL stream by status: read status token, then 1 path (M/A/D) or 2 paths (R/C). Tests for M/D/A/R/mode-only/space-paths.

Next steps: remove open execute-plan branch; make bash snippets empirically testable; verification cases for repeated WTS cleanup, tracked dirty overlay, execute-plan --base from detached worktree, dirty execute-plan.

---

## Turn 3 — 2026-06-02 18:25 UTC

Target: working tree diff
Verdict: needs-attention (design approved in interim; shell-robustness gaps remain)

Findings:
- [high] build_wts producer failures unchecked: `< <(git diff)`, `find -print0` process-subs + `git archive | tar` pipe mask producer failure → can set WTS_SCAN_ROOT with baseline only. R/C reads unchecked.
  Fix: git archive -o $TAR + separate tar -xf; materialize diff/find producers to temp files with || return 1; check every read.
- [high] Failed build_wts → stale WTS_SCAN_ROOT reuse: only set on success, never cleared; call-site `SCAN_ROOT=$WTS_SCAN_ROOT` after degradation could reuse prior snapshot.
  Fix: clear WTS_SCAN_ROOT at entry + on failure; call-site `if ! build_wts; then degrade; return; fi; SCAN_ROOT=...` no fallthrough.
- [medium] Substrate B per-call worktree trap overwrites across review points (same leak class as WTS).
  Fix: EPCC_WT_DIRS array + single trap once; mktemp || degradation before worktree add.

All three applied in revision (codex_targeted_fixes=2). Remaining shell-hardening delegated to execution TDD test matrix (T1-T10 in spec). Design direction stable since Turn 1 revision (two substrates).

---

## Turn 4 — 2026-06-02 18:30 UTC

Target: working tree diff
Verdict: needs-attention (Turn 3 fixes present + correct; NEW design high found)

Turn 3 fixes: confirmed present & correct (WTS_SCAN_ROOT entry-clear, no-fallthrough call-site, materialized producers, EPCC_WT_DIRS single trap).

Findings:
- [high] Substrate A breaks clean-tree branch/base review for spec/write-plan (spec:57-60)
  spec/write-plan use --scope working-tree ONLY when target dirty; when CLEAN they use --base $USER_BASE_REF or auto default-branch. Synthetic repo removes original refs/history → explicit base unresolved; empty-scope auto resolves against synthetic repo's own fresh commit → empty/wrong diff. Same class as Turn 1 execute-plan critical, now for spec/write-plan clean path. T1-T10 only test synthetic --scope working-tree.
  Fix: substrate choice PER call-site+scope, not per command — Substrate A only for explicit --scope working-tree; route clean --base/auto through a committed worktree that preserves refs/history. (Claude assessment: this points to UNIFYING on a single worktree+overlay substrate — see session decision.)

This is the third base/clean-scope failure (Turn 1 execute-plan, Turn 4 spec/write-plan) → synthetic-git approach structurally fights companion's ref-based review. Claude proposing pivot to single worktree+overlay substrate.

---

## Turn 5 — 2026-06-02 18:44 UTC (Option Y pivot review)

Verdict: needs-attention. Pivot fixes --base/ref breakage but new gaps:
- [high] Shared linked-worktree .git exposes common gitdir: stash (stash -u = untracked secrets), reflog, local .git/config (url credentials), other-branch objects — BROADER than the claimed committed-history caveat. Synthetic approach lacked this channel; pivot traded it for --base. Fix: sanitized git substrate (only HEAD/base objects+refs) OR explicit best-effort + preflight/stop for stash/reflog/config/extra-ref.
- [high] task --fresh (scope-less) calls lose current spec/plan: overlay keyed only on SCOPE; write-plan Step6 reads CURRENT SPEC_PATH, execute-plan Step6 reads CURRENT PLAN_PATH — if uncommitted, committed-only worktree has stale/no file → Codex analyzes wrong artifact silently. Fix: per-call substrate inputs (explicit required current files overlaid), not SCOPE-only.
- [medium] Overlay flattens staged→unstaged, staged-new→untracked (worktree index at HEAD) → companion loses staged/unstaged split. Fix: document+test flattening, or reproduce index.

---

## Turn 6 — (Option Z spec review, kullanıcı ayrı oturum)

Verdict: needs-attention / no-ship. Option Z doğru mimari yön; implementasyon öncesi 6 bulgu kapanmalı.
Ampirik: --base main geçti; --base origin/main "Not a valid object name" ile düştü.

- [high] #1 BASE_REF namespace: substrate refs/heads/main kuruyor, companion --base origin/main bekleyince düşüyor. Fix: exact namespace preserve (origin/main → refs/remotes/origin/main) veya call-site normalize.
- [high] #2 OVERLAY input: overlay yalnız REQUIRED_CURRENT_FILES uncommitted'sa çalışıyor → working-tree review tüm dirty'yi görmeli. Fix: OVERLAY_WORKTREE=1 (tüm tracked/staged dirty) + REQUIRED_CURRENT_FILES (untracked allow-list) ayrı inputlar.
- [high] #3 patch pipe fail-closed değil: git diff | git apply || return 1 sadece son komutu kontrol; producer fail → boş apply başarılı → eksik SCAN_ROOT. Fix: patch'i temp dosyaya materialize, [-s] kontrol, cleanup'a ekle, T2 doğrula.
- [med] #4 SHA BASE_REF gereksiz 40-hex branch ref yaratıyor (ambiguous). Fix: SHA ise ref yaratma, companion'a SHA aynen ver.
- [med] #5 default branch fallback yalnız main: companion main/master/trunk destekliyor. Fix: aynı adaylar VEYA (yeğlenen) call-site live repo'da base'i resolve edip exact ref olarak versin.
- [med] #6 active layer stale: HANDOFF "TEST EDİLMEDİ"/eski Resume From + TASK "PENDING: Option Z'ye güncelle" kalmış. Fix: sweep.

OP-1/2/3 mimari onaylı; bu 6 fix + OP-4 harness implementasyon öncesi.

---

## Turn 7 — (Option Z spec re-review, Turn-6-fix sonrası, kullanıcı ayrı oturum)

Verdict: needs-attention. 2 bulgu:
- [high] #1 task --fresh overlay fazla geniş: REQUIRED uncommitted'sa TÜM tracked dirty overlay ediliyor → task --fresh için alakasız dirty tracked dosyalar secret-scan'siz substrate'a girer. Fix: iki mod — OVERLAY_WORKTREE (tüm dirty, yalnız --scope working-tree) vs OVERLAY_REQUIRED_ONLY (yalnız REQUIRED, pathspec-limited diff `-- "$f"`). Test: PLAN_PATH uncommitted + alakasız secrets.txt tracked dirty → task-fresh substrate'ında PLAN_PATH var, secrets.txt yok.
- [med] #2 full ref namespace: BASE_REF=refs/remotes/origin/main veya refs/heads/main full-ref tanınmıyor → yanlış refs/heads/$BASE_REF path. Fix: case'e `refs/*) update-ref "$BASE_REF"` ekle. Test: origin/main, refs/remotes/origin/main, main, <sha> hepsi pass.

İkisi uygulandı (codex_targeted_fixes=4).

---
