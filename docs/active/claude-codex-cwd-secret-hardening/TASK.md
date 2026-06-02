---
title: claude-codex ailesi — Codex --cwd untracked-secret exposure hardening
status: active
proposed: 2026-06-02
started: 2026-06-02
last-touched: 2026-06-02
blocked-by: null
---

# Goal

claude-codex komut ailesinde **4 komutun** (spec / write-plan / execute-plan / simplify) Codex çağrısını
`--cwd "$PROJECT_ROOT"` (canlı repo) ile yapması → working-tree'deki **untracked `.env`/secret harici
modele (Codex) okunabilir**. Bu süreç-içkin riski (canonical blok template'i + override yokluğu) bir
substrat izolasyonuyla kapat.

# References

- **Keşif:** finish-branch-claude-codex security review (2026-06-02, dual) → bulgu **S-1**.
  Rapor: `docs/security-reviews/2026-06-02-finish-branch-claude-codex.md`; fix `d7a80c7` (yalnız finish-branch).
- **Spec (spec-approved):** `docs/specs/2026-06-02-claude-codex-cwd-secret-hardening.md` (iteration 3, Option Z; codex_targeted_fixes: 4).
- **Codex review log (5 tur):** `docs/reviews/codex/2026-06-02-claude-codex-cwd-secret-hardening.md`.
- **İzole eden örüntüler (referans):** review → pinli worktree `$REVIEW_WT`; security-review → git'siz export;
  finish-branch → git'siz export (S-1 fix deseni).
- Drift contract: CODEX-CALL-PROTOCOL `c7b5976c` byte-identical (7-way), **call-site `--cwd` override marker DIŞINDA**.

# Current Status

**active — spec Option Z (sanitized fetch clone), iteration 3. Mekanizma Codex-ampirik doğrulanmış;
spec review Turn 6+7 (8 bulgu) uygulandı. Mekanizma tarafında açık no-ship yok. Sıradaki: OP-4/OP-5
harness + implementasyon (`/write-plan-claude-codex` → `/execute-plan-claude-codex`).**

- Spec güncel: `docs/specs/2026-06-02-claude-codex-cwd-secret-hardening.md` (codex_review_iterations: 3).
- Mekanizma Codex tarafından gerçek companion git-context'ine karşı çalıştırılarak çözüldü:
  **sanitized fetch clone** (OP-1), **REQUIRED_CURRENT_FILES** (OP-2), **index-preserving overlay** (OP-3).
- **Kalan:** OP-4 (T1-T6 + T11/T12 fail-closed harness) + OP-5 (`@execution-pin` plumbing) → implementasyon (execute-plan TDD) öncesi.
- **Sıradaki:** OP-4 (T1-T6 + T11/T12) harness + `@execution-pin` plumbing; ardından implementasyon (`/write-plan-claude-codex` → `/execute-plan-claude-codex`).
- Working tree: spec + review log + active-layer untracked/değişik (commit'lenmedi).

# Open Problems

- **OP-1 — Substrat mekanizması → ÇÖZÜLDÜ (Codex ampirik):** **sanitized fetch clone.** worktree+preflight
  ampirik olarak yapısal-zayıf (config credential + stash + secret-branch ref worktree'den okundu). Sanitized
  clone: yalnız HEAD + base/default ref fetch · `remote remove origin` · `.git/logs` temizle ·
  `core.logAllRefUpdates=false` → `--base`/auto çalışır, `.env`/stash/secret-branch yok.
- **OP-2 — task --fresh inputs → ÇÖZÜLDÜ:** overlay SCOPE'a değil **`REQUIRED_CURRENT_FILES`**'a bağlanır
  (spec/write-plan→SPEC_PATH, execute-plan→PLAN_PATH, simplify→okuduğu güncel dosyalar); uncommitted ise
  sanitized clone'a allow-list + secret-scan ile overlay.
- **OP-3 — staged/unstaged → ÇÖZÜLDÜ:** **index-preserving overlay** — `git diff --cached --binary HEAD |
  git apply --index` + `git diff --binary | git apply` + allow-list untracked copy (ampirik 1 staged/1 unstaged/
  1 untracked korundu). Flatten+belgele yerine bu.
- **OP-4 — AÇIK (fail-closed harness):** T7-T10 + OP-3 ampirik koşuldu; **T1-T6 koşulmadı** — NUL parser,
  producer failure, stale SCAN_ROOT, cleanup, symlink/secret-scan testleri ayrı harness ile, **implementasyon öncesi.**
- **OP-5 — AÇIK (`@execution-pin` plumbing):** base-resolution (call-site live repo), SHA-vs-ref tespiti,
  default-branch adayları (main/master/trunk/origin-HEAD) — Codex Turn 6 yön verdi, harness kesinleştirir.

# Decisions Log

- 2026-06-02: **Yön (b) izolasyon** seçildi (kullanıcı, Adım 3) — diğer 3 aile komutu zaten izole, (c) kabul tutarsızlık yaratırdı.
- 2026-06-02: **Substrat tasarım evrimi** (Codex review-driven, full_design_iteration=2):
  - Iter 0: 4 komutta uniform sentetik working-tree substratı → **Turn 1 critical**: execute-plan `--base`'i kırdı.
  - Iter 1: iki substrat (sentetik A working-tree + worktree B committed) → **Turn 4 high**: sentetik clean
    spec/write-plan `--base`/auto'yu da kırdı (`git init` ref-kaybı yapısal).
  - Iter 2: tek worktree+overlay substratı (CODEX-SCAN-SUBSTRATE) → **Turn 5 high**: paylaşılan `.git`
    stash/reflog/config kanalı.
  - **Önerilen (DOĞRULANMADI):** clone-tabanlı substrat (ayrı `.git` + korunan ref'ler) — Codex ampirik kuracak.
- 2026-06-02: **Untracked policy → allow-list** (blacklist değil; Turn 1 high — nötr-adlı secret kaçıyordu).
- 2026-06-02: **Drift → tek `CODEX-SCAN-SUBSTRATE` bloğu + 4-way Check C**; `CODEX-CALL-PROTOCOL` 7-way `c7b5976c` değişmez (substrat onun dışında, override prose).
- 2026-06-02: Bu repoda `.git`-kanal exposure **ölçüldü = sıfır** (config temiz, stash yok, tek branch) — yapısal kanal yine de var.
- 2026-06-02: **Iter 3 — Mekanizma ÇÖZÜLDÜ (Codex ampirik, ayrı oturum).** Throwaway repo (base+feature commit,
  unstaged+staged+untracked, ignored `.env`, config credential, 2 stash, secret branch) ile companion
  git-context yolu (`resolveReviewTarget`/`collectReviewContext`/`getWorkingTreeState`) çalıştırıldı:
  - **Karar: sanitized fetch clone** (vanilla clone değil, worktree değil). Worktree ampirik yapısal-zayıf
    (credential/stash/secret-ref okundu). Sanitize: HEAD+base ref fetch · remote remove · logs temizle · logAllRefUpdates=false.
  - OP-2: `REQUIRED_CURRENT_FILES` overlay. OP-3: index-preserving overlay (`git apply --index`).
  - OP-4: T1-T6 fail-closed harness implementasyon öncesi açık. (Tam adversarial-review model çağrısı koşulmadı; git-context yolu yeterli kanıt.)
- 2026-06-02: **Codex spec review (Turn 6) — 6 bulgu, hepsi uygulandı** (spec'e işlendi). `--base origin/main`
  namespace hatası ile düştü → düzeltmeler: base-ref EXACT namespace (origin/* → refs/remotes/*; SHA→ref yaratma),
  `OVERLAY_WORKTREE` (working-tree review tüm dirty), patch temp-materyalize + `[-s]` fail-closed, default-branch
  call-site resolve. Mimari (Option Z) onaylı; kalan: OP-4 + OP-5 (`@execution-pin`).
- 2026-06-02: **Codex spec re-review (Turn 7) — 2 bulgu, hepsi uygulandı.** (high) task-fresh overlay fazla
  genişti → iki mod: `OVERLAY_WORKTREE` (tüm dirty, --scope working-tree) vs `OVERLAY_REQUIRED_ONLY`
  (pathspec-limited, task-fresh; alakasız dirty girmez). (med) full-ref namespace → base-ref case'e `refs/*)` dalı.
  Test T11/T12 eklendi. `codex_targeted_fixes`=4.
