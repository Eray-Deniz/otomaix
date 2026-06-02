# Handoff

## Context
- Task: claude-codex ailesi — Codex --cwd untracked-secret exposure hardening
- Status: **active** — spec Option Z (sanitized fetch clone), iteration 3; Codex spec review Turn 6+7 bulguları uygulandı
- Keşif: finish-branch-claude-codex security review (2026-06-02), bulgu S-1

## Current State
- Spec güncel: `docs/specs/2026-06-02-claude-codex-cwd-secret-hardening.md` (codex_review_iterations: 3, codex_targeted_fixes: 4).
- Mekanizma: **sanitized fetch clone** — Codex tarafından gerçek companion git-context'ine karşı ampirik doğrulandı.
- Codex spec review **Turn 6 (6 bulgu) + Turn 7 (2 bulgu) — hepsi uygulandı**: base-ref EXACT namespace (refs/*/origin/*/named/SHA), iki overlay modu (OVERLAY_WORKTREE / OVERLAY_REQUIRED_ONLY pathspec-limited), fail-closed materyalize patch, default-branch call-site resolve, active-layer sweep. T11/T12 test eklendi.
- **Açık:** OP-4 (T1-T6 fail-closed harness) + spec'teki `@execution-pin` plumbing → implementasyon (execute-plan TDD) öncesi.
- Working tree: spec + review log + active-layer untracked/değişik (commit'lenmedi).

## Verification (iterasyon bazlı — DÜRÜST)
- **Iter 0-2 (sentetik/worktree) — superseded:** mekanizma prose'da akıl yürütüldü, gerçek companion'a karşı KOŞULMADI; 5 review turu yakınsamadı (ders: [[feedback_empirical_validation_for_shell_specs]]).
- **2026-06-02 Codex empirical pass (Iter 3) — TEST EDİLDİ:** throwaway repo + gerçek companion git-context ile sanitized fetch clone doğrulandı → `--base`/auto diff doğru, `.env`/stash/secret-branch/credential yok; worktree ampirik yapısal-zayıf (reddedildi). index-preserving overlay → 1 staged/1 unstaged/1 untracked korundu. (OP-1/2/3 = T7-T10.)
- **Codex spec review (Turn 6+7) — TEST EDİLDİ:** Turn 6 `--base origin/main` namespace hatası → 6 bulgu; Turn 7 task-fresh overlay genişliği + full-ref namespace → 2 bulgu; hepsi uygulandı.
- **HÂLÂ KOŞULMADI:** OP-4 (T1-T6 fail-closed/failure-injection) + `@execution-pin` plumbing (base-resolution, SHA-vs-ref, default-branch adayları) — implementasyon harness'ı.

## Resume From (sıradaki)
Turn 7 re-review bulguları uygulandı; mekanizma tarafında açık no-ship yok. Sıradaki:
- **Implementasyon:** `/write-plan-claude-codex` → `/execute-plan-claude-codex` TDD — OP-4 (T1-T6 + T11/T12) harness + `@execution-pin` plumbing ampirik kapatılır.
- (Opsiyonel) Turn 7 fix'li spec'i Codex'e bir tur daha (temiz teyit) — kullanıcı isterse.
- İlk oku: spec "CODEX-SCAN-SUBSTRATE bloğu" + "OP-4" + review log Turn 7.

## Risks
- **`@execution-pin` plumbing:** base-resolution (call-site, live repo), SHA-vs-ref tespiti, default-branch adayları (main/master/trunk/origin-HEAD) Codex'çe tam spec'lenmedi → harness kesinleştirmeli.
- İçerik secret-scan pattern listesi örnek (tam değil) — allow-list birincil kapı.
- Committed secret: fetch HEAD ancestry'sini getirir → committed secret (varsa) substratta olur (best-effort caveat; bu repoda yok).
- Performans: per-call `git init`+fetch; execute-plan çok-çağrılı → birikir.
- Yeni drift yüzeyi: 4-way Check C drift-check tooling'e eklenmeli.

## Notes For Codex
- **Açık iş:** OP-4 (T1-T6: NUL/path-space, producer/fetch/apply hata→fail-closed, stale SCAN_ROOT, cleanup, symlink exfil, secret-scan) + `@execution-pin` satırları — ampirik harness.
- **Kısıt:** `CODEX-CALL-PROTOCOL` bloğu (`c7b5976c`, 7-way) byte-identical KALMALI; substrat onun DIŞINDA, `--cwd "$SCAN_ROOT"` override prose talimatı.
- Codex active layer'a **YAZMAZ** — bulgu/öneriyi stdout döner, kullanıcı/Claude işler.

## Codex Empirical Resolution + Spec Review (özet — spec'e işlendi)
- **Mekanizma (Iter 3):** sanitized fetch clone — `git init` + live repo'dan yalnız HEAD+base/default fetch + `remote remove origin` + `.git/logs` sil + `core.logAllRefUpdates false`. Overlay: `OVERLAY_WORKTREE` (tüm tracked dirty) + `REQUIRED_CURRENT_FILES` (untracked allow-list); index-preserving (`git apply --index`).
- **Turn 6 fix'leri (spec'e işlendi):** base-ref EXACT namespace (`origin/main`→`refs/remotes/...`; SHA→ref yaratma); OVERLAY_WORKTREE tüm-dirty; patch temp-dosya materyalize + `[-s]` (fail-closed); default-branch call-site resolve.
- **Turn 7 fix'leri (spec'e işlendi):** iki overlay modu (OVERLAY_WORKTREE tüm-dirty / OVERLAY_REQUIRED_ONLY pathspec-limited task-fresh — alakasız dirty girmez); base-ref case'e `refs/*)` full-ref dalı; T11/T12 test; dead helper `_css_required_has_uncommitted` silindi.

## Notes For Claude
- **Ders:** Kabuk/git/harici-araç davranışı içeren spec işinde **ampirik doğrula** (throwaway kur + çalıştır), prose'da kalıp delikleri review'a bırakma. Iter 0-2'de bu atlandı → 5 tur yakınsamadı; Iter 3'te Codex ampirik koşunca tek seferde oturdu. Detay: [[feedback_empirical_validation_for_shell_specs]].
- Active-layer'ı flip'te grep-sweep et: bu drift **iki kez** Codex review'da yakalandı (Turn 6 #6 stale "TEST EDİLMEDİ"/Resume; Turn 7-followup #medium stale "review'a sokacak"/targeted_fixes:3). Decisions Log eklemek YETMEZ — Current Status + HANDOFF Context/Current State/Resume hepsi sweep edilmeli ([[feedback_sweep_sibling_sites]]).
