# Codex Plan Review Log — claude-codex-cwd-secret-hardening

Plan: `docs/plans/2026-06-02-claude-codex-cwd-secret-hardening.md`
Spec: `docs/specs/2026-06-02-claude-codex-cwd-secret-hardening.md`
Komut: `/write-plan-claude-codex` (Adım 12 adversarial-review, `--scope working-tree`)

---

## Turn 1 — 2026-06-02

Verdict: **needs-attention** · 3 high · 2 medium · EXIT=0

> Target: working tree diff
> Verdict: needs-attention
>
> No-ship: the plan’s main regression harness is structurally invalid, and the primary security fix still depends on weak prose-level call-site overrides with non-behavioral verification.
>
> Findings:
> - [high] Harness runs `build_scan_substrate` in subshells, so it cannot test the required caller-shell state contract (plan:300-306)
>   The spec requires `build_scan_substrate` to run in the caller shell so `SCAN_ROOT` and `SCAN_WT_DIRS` mutations persist. The planned harness wraps calls in `( cd "$FIX" ... build_scan_substrate )`, then asserts `SCAN_ROOT` in the parent shell. That will either fail spuriously on success paths, or worse, make stale-guard checks meaningless because parent `SCAN_ROOT` was never mutated by the child. This breaks OP-4 as a re-runnable regression gate and does not exercise the exact mechanism the command files rely on.
>   Recommendation: Rewrite harness calls to execute in the same shell, e.g. save `oldpwd=$PWD`, `cd "$FIX" || return`, call `build_scan_substrate`, then restore with `cd "$oldpwd"`. Add an explicit assertion that a successful call mutates parent `SCAN_ROOT` and appends to parent `SCAN_WT_DIRS`.
> - [high] T7/T8 assume a `main` branch that `mkfix` never creates (plan:278-308)
>   `mkfix` uses plain `git init -q` and commits once, but T7/T8 set `BASE_REF=main` and expect `refs/heads/main` to resolve in the substrate. Plain `git init` may create `master` depending on Git version/config (`init.defaultBranch`), so the harness can fail for environment reasons unrelated to the substrate. This undermines the plan’s stated harness-first TDD direction and can mask the real base-ref behavior under default-branch skew.
>   Recommendation: Make the fixture deterministic with `git -C "$d" init -q -b main` where supported, or immediately `git -C "$d" branch -M main` after the first commit. Also add a separate fixture for non-main defaults if OP-5 default-branch behavior is meant to be covered.
> - [high] Call-site override verification can pass without proving Codex is actually invoked with `--cwd "$SCAN_ROOT"` (plan:562-623)
>   The plan preserves CODEX-CALL-PROTOCOL byte-identically and relies on marker-external prose to override its literal `--cwd "$PROJECT_ROOT"`. Task 4 then verifies only by counting occurrences of the string `cwd "$SCAN_ROOT"`. Because these command files are LLM-followed markdown, a comment or instruction can satisfy the grep while the executable protocol snippet still says `timeout ... --cwd "$PROJECT_ROOT"`. That is the original S-1 exposure path, so this is a shipping blocker unless the plan proves the actual call instruction at every call-site is unambiguous and outside the marker block.
>   Recommendation: For each target command, add explicit marker-external call-site snippets that set substrate variables, call `build_scan_substrate`, and show the concrete `timeout 480s node "$COMPANION" ... --cwd "$SCAN_ROOT" ...` invocation. Replace grep-count checks with extraction checks that enumerate every real Codex call-site and fail if any call-site outside the protected canonical block still routes to `$PROJECT_ROOT`.
> - [medium] Auto base resolution can silently produce an empty base, leaving clean reviews without the intended ref in the substrate (plan:162-170)
>   The OP-5 snippet resolves `origin/HEAD`, then only local `refs/heads/{main,master,trunk}`. It does not fail closed if no candidate is found, and it does not try common remote-tracking refs when `origin/HEAD` is absent. In that case `BASE_REF` becomes empty, `build_scan_substrate` fetches only HEAD, and the companion’s auto/base review can run in a sanitized repo that lacks the intended default branch ref. That violates the spec’s requirement that auto-scope default branch be resolved in the live repo before substrate build.
>   Recommendation: Make auto base resolution fail closed when it cannot resolve a commit. Include remote-tracking fallbacks such as `refs/remotes/origin/{main,master,trunk}`, validate the final value with `rev-parse --verify`, and add a harness case where `origin/main` exists but local `main` and `origin/HEAD` do not.
> - [medium] Final suite prints harness failure but can still exit successfully (plan:687-703)
>   Task 6 wraps the harness as `bash ... && echo PASS || { echo FAIL; tail -5 ...; }`. If the harness fails, `tail` usually exits 0, so the overall copied command can still return success after printing `harness: FAIL`. The prose says commit must stop on any failure, but the verification command does not enforce that, creating a real risk that a failed OP-4 regression is missed during final commit workflow.
>   Recommendation: Track a `failed=0` flag across Check A, Check C, and harness, set it on any failure, and end the suite with `[ "$failed" -eq 0 ] || exit 1`. For the harness branch specifically, append `exit 1` after printing the log tail.
>
> Next steps:
> - Fix the harness shell-state issue before implementing any command-file changes.
> - Make branch/base fixtures deterministic and add the missing OP-5 remote-tracking fallback case.
> - Strengthen call-site wiring from grep/prose checks into explicit per-call executable markdown snippets plus extraction-based verification.

**Claude değerlendirmesi:** 5 bulgu da geçerli, false-positive yok. Hepsi Mode A refine ile uygulandı. 3 high + 2 medium → critical/high guard: normal "Onayla" sunulmaz; Güncelle seçildi. `codex_plan_review_iterations` 0→1.

**Uygulanan düzeltmeler:**
- high#1 (subshell) → `_build_in` same-shell helper; t_clean'e caller-state assertion (SCAN_ROOT + SCAN_WT_DIRS parent'ta).
- high#2 (main branch) → `mkfix` `symbolic-ref HEAD refs/heads/main` (version-agnostik deterministik).
- high#3 (call-site grep zayıf) → explicit invocation snippet (`--cwd "$SCAN_ROOT"`) + Task 4 Step 7 extraction-based DECISIVE gate (protokol DIŞINDA `$PROJECT_ROOT --cwd`=0) + final suite'e S-1 invariant.
- med#4 (auto base fail-open) → RESOLVED_BASE fail-closed + `refs/remotes/origin/*` fallback + `rev-parse --verify` + T13 harness case.
- med#5 (final suite exit 0) → `failed` flag + `exit 1`; harness branch fail'de exit 1.

**Claude ampirik doğrulama (Turn 1→2 arası, throwaway):** Düzeltilmiş harness + canonical blok gerçek git fixture'larıyla koşuldu → **30/30 assertion PASS, FAIL=0, rc=0** (T1-T13 + caller-shell state + fail-closed). Mekanizma prose değil, çalıştırılmış kanıt ([[feedback_empirical_validation_for_shell_specs]]). Ayrıca re-review öncesi self-catch: explicit snippet'teki ayrı `--base` `$SCOPE` ile çakışıyordu → kaldırıldı (base <CALL> içinde).

---

## Turn 2 — 2026-06-02 (re-review, fixes uygulandıktan sonra)

Verdict: **needs-attention** · 1 high · 1 medium · EXIT=0. Önceki 1/2/3/5 RESOLVED onaylandı; 4 kısmen.

> No-ship: the prior harness/default-branch/final-suite issues are materially addressed, but fail-closed call-site behavior is still not proven. The plan can still fall through into a Codex invocation after substrate or auto-base failure.
>
> - [high] Substrate failure path still falls through to the Codex invocation (plan:154-162). `if ! build_scan_substrate; then :; fi` sonrası `timeout ... --cwd "$SCAN_ROOT"` yine çalışır; build_scan_substrate SCAN_ROOT'u sıfırladığından companion boş cwd ile çağrılabilir. OP-4 fonksiyonun non-zero döndüğünü doğruluyor ama call-site wrapper'ın invocation'ı bastırdığını doğrulamıyor. Recommendation: `:` dalını gerçek non-fallthrough ile değiştir (return/exit/continue veya companion'ı atlayan degradation); fake companion ile failed build → 0 `node` invocation testi ekle.
> - [medium] Auto-base fail-closed empty RESOLVED_BASE'de duruyor ama review'ın atlandığını kanıtlamıyor (plan:189-194). Empty RESOLVED_BASE → `BASE_REF=""` → yine build + companion call. T13 yalnız resolver'ın boş döndüğünü test ediyor, companion çağrılmadığını değil. Recommendation: unresolved auto-base'i non-zero/flag yap, base-review call-site'ı build+companion ÖNCESİ abort/degrade etsin; T13'ü wrapper'a genişlet (unresolved → 0 invocation).
>
> Next steps: fix non-fallthrough control flow; extend harness to wrapper-level invariants; prior 1/2/5 resolved, 4 partial.

**Claude değerlendirmesi:** İkisi de geçerli — call-site control flow'u `:` placeholder bıraktığım için fail-open kaldı (high#1 fallthrough, med#2 base-review base'siz). Mode A refine, `codex_plan_review_iterations` 1→2.

**Uygulanan düzeltmeler:**
- high#1 → call-site template fail-closed if/else: companion call YALNIZ `if build_scan_substrate; then ... fi` success dalında (if-sonrası DEĞİL); fail dalı degradation (no call).
- med#2 → base-review'da `RESOLVED_BASE` boşsa ilk guard companion'ı atlar (base'siz base-review YOK). T14 wrapper testi eklendi.
- T14 (fake companion): substrate-fail → 0 call · unresolved-base → 0 call · success → 1 call.

**Claude ampirik doğrulama (Turn 2→3 arası):** Düzeltilmiş harness (T1-T14) gerçek git fixture + fake companion ile koşuldu → **33/33 assertion PASS, FAIL=0, rc=0.** Fail-closed control flow çalıştırılmış kanıt.

---

## Turn 3 — 2026-06-02 (re-review, call-site fail-closed sonrası)

Verdict: **approve** · No material findings · EXIT=0.

> Ship from this re-review scope: the Turn 2 fail-closed findings are resolved in the plan text, no new high/critical issue is supported. CODEX-CALL-PROTOCOL is still c7b5976c across all 7 command files, and Check C remains byte-for-byte cmp-based in the plan.
>
> No material findings.

**Sonuç:** Plan `plan-approved`. 2 full iteration (`codex_plan_review_iterations: 2`), 3 review turu. Çözülmemiş critical/high: **none**. Mekanizma + harness (T1-T14) ampirik doğrulandı (33/33 PASS).
