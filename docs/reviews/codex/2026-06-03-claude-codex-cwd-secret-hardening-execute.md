# Codex Execution Review Log — claude-codex-cwd-secret-hardening

Plan: `docs/plans/2026-06-02-claude-codex-cwd-secret-hardening.md`
Execution: `/execute-plan-claude-codex` (inline + standard cadence)
Codex `--cwd` exposure: kullanıcı-kabul (canlı `/root/otomaix`; backend/.env + frontend/.env.local açık — bu task kapatana dek).

---

## Pre-Execution Turn — 2026-06-03 06:58 UTC

Research only; dosya değiştirmedim.

**Environment Drift**
1. Invalidating repo drift bulmadım. HEAD `e5b1f64` ve son 20 committe plan varsayımlarını bozan path rename/removal, dependency/env shift veya migration benzeri değişiklik görünmüyor.
2. Plan/review artefaktları repo içinde hâlâ untracked: `docs/plans/...cwd-secret-hardening.md`, `docs/reviews/codex/...plan.md`; active task dosyaları modified. Bu plan execution’ın current dirty worktree içeriğine bağlı olduğunu gösteriyor.
3. `docs/tools/codex-scan-substrate-harness.sh` henüz yok; bu planla uyumlu, Task 2’de yaratılacak. `git 2.43.0`, `bash 5.2`, `awk`, `md5sum`, `cmp` mevcut.

**First-Batch Prereq Items**
1. Task 1 backup ve Check A hedefleri `~/.claude/commands/*-claude-codex.md` repo dışında; bu oturumda doğrulamadım. İlk batch başlamadan 4 backup + 7-way `c7b5976c9513391909310883c40575c3` baseline mutlaka taze koşulmalı.
2. Check A referansı `c7b5976c` commit değil md5/pin; commit gibi resolve olmuyor. Komutlar md5 extraction üzerinden çalışmalı.
3. Plan `/tmp/css-canonical.sh` ve harness scratch state’e güvenmemeyi söylüyor; repo’da harness yok, yani Task 2’nin canonical block + real git fixture harness üretimi sıfırdan yapılmalı.

---

## Checkpoint Turn 1 — 2026-06-03 07:25 UTC

Batch 1 (Task 1 baseline, Task 2 harness, Task 3 byte-identical embed). Scope: `--scope working-tree` (`--cwd /root/otomaix`, exposure kullanıcı-kabul).

```
# Codex Adversarial Review
Target: working tree diff
Verdict: needs-attention

No-ship for evidence quality: Check A/Check C look intact, but the 33/33 harness overclaims fail-closed call-site coverage. I could not rerun the harness in this read-only sandbox because mktemp failed before extraction.

Findings:
- [high] T14 proves only a synthetic wrapper, not the command call-sites that can leak cwd (docs/tools/codex-scan-substrate-harness.sh:190-194)
  The harness defines its own idealized `_css_callsite` and asserts fake companion call counts against that local function. That does not exercise any real markdown call-site or extracted command-file wiring, so the 33/33 result can pass while a future or existing command call-site still falls through to Codex after substrate/base failure. This is the same high-cost S-1 path the plan was meant to close; counting T14 as empirical wrapper evidence is padded unless it is tied to the real command text.
  Recommendation: Do not count T14 as shipping evidence until Task 4 adds executable per-command wrapper checks. Add a post-wiring test that parses or invokes each of the four actual command call-site snippets with a fake companion and asserts substrate-fail/unresolved-base produce zero invocations.
- [medium] Fixture cleanup is broken because mkfix runs in command substitutions (docs/tools/codex-scan-substrate-harness.sh:29-38)
  `mkfix` appends fixture dirs to `CLEAN_DIRS`, but every caller uses `FIX=$(mkfix)`, which runs the function in a subshell; the `CLEAN_DIRS+=` mutation is lost in the parent. The EXIT trap therefore cleans substrate dirs but not the throwaway fixture repos, including synthetic `.env` files. This undermines the re-runnable harness claim and leaves secret-like test material behind after repeated runs.
  Recommendation: Avoid command substitution for stateful fixture creation. Have `mkfix` assign to a global/output variable in the caller shell, or explicitly register returned fixture paths in the parent after each call; add a cleanup assertion that no `cssfix.*` fixture dirs remain.

Next steps:
- Fix T14 so fail-closed call-site evidence comes from the real command wiring, not a local mirror.
- Fix fixture cleanup and rerun the harness in a writable environment.
- Then rerun Check A 7-way, Check C 4-way cmp/tripwire, and the harness against the embedded block.
```

**Claude doğrulaması (8.5 öncesi):**
- Finding 2 (medium) — KESİN. TMPDIR=`/tmp/claude-0`'da 47 leaked fixture dizini (her birinde sahte `.env`). Kontrollü probe: `FIX=$(mkfix)` subshell → parent `CLEAN_DIRS`=0, EXIT trap fixture'ları temizlemiyor.
- Finding 1 (high) — GEÇERLI. T14 harness-local `_css_callsite` aynasını test ediyor, gerçek embedded wiring'i değil. Substrate bloğu Check C ile byte-identical + harness davranış-doğrulu; call-site wiring yalnız grep-doğrulu (asimetri). Karar: Adım 8.5 guard'da kullanıcıya sunuldu → DÜZELTİLDİ (run_codex_scan/css_resolve_base canonical, T13/T14 sourced; commit d317fc3).

---

## Final Execution Turn — 2026-06-03 09:15 UTC

Scope: `--base e5b1f644..HEAD` (clean committed tree; tek dirty = active-layer task-tracking). `--cwd /root/otomaix` (exposure kullanıcı-kabul). Codex `$HOME/.claude/commands/` komut dosyalarını + harness'ı doğrudan okudu.

```
# Codex Adversarial Review
Target: branch diff against e5b1f644...
Verdict: needs-attention

No-ship: the substrate block itself is byte-identical and static checks show the old live-repo cwd only inside CODEX-CALL-PROTOCOL, but the concrete command call-sites still instruct using that protocol instead of explicitly invoking the new wrapper. S-1 closure depends on a late prose override being honored, not on unambiguous per-call-site wiring.

- [high] Concrete Codex call-sites still point at the old protocol path (spec-claude-codex.md:400-413)
  The active call-site text still says to run `Codex Çağrı Protokolü`, while the protocol's concrete invocation remains `timeout 480s node "$COMPANION" <CALL> --cwd "$PROJECT_ROOT" "$PROMPT"`. The new run_codex_scan wrapper is only a later generic contract section; this call-site does not set CALL_KIND/REQUIRED_CURRENT_FILES/RESOLVED_BASE or call run_codex_scan. In these markdown command files the prose IS the executable wiring; a missed override routes Codex back to the live repo and reopens untracked-secret exposure.
  Rec: rewrite each concrete call-site to show the exact run_codex_scan invocation, OR change the canonical protocol's single concrete invocation to delegate to run_codex_scan (BLOCKED: protocol is frozen 7-way, shared w/ 3 non-substrate commands).
- [medium] Secret allow-list scan misses common uppercase env keys (_css_secret_scan, block)
  Scan is case-sensitive; `OPENAI_API_KEY=`, `SECRET_KEY=`, `PASSWORD=`, `TOKEN=` slip through and get copied into substrate. T6 only covers lowercase api_key. (Mitigated for gitignored .env which is excluded earlier by ls-files --exclude-standard; matters for untracked non-ignored allow-listed files.)
  Rec: make scan case-insensitive (grep -Ei) + add uppercase harness cases.
```

**Claude doğrulaması (Adım 12 öncesi):**
- Finding 1 (high) — KESİN. spec Adım 6 (satır 400-414) okundu: `<CALL> = adversarial-review $SCOPE` + protokol; `run_codex_scan`/`CALL_KIND`/`REQUIRED_CURRENT_FILES` YOK. S-1 kapanışı uzak addendum'a bağımlı → kırılgan. Task 4 wiring eksikti (referans-bölümü ≠ per-call-site wiring). İlke 1.
- Finding 2 (medium) — KESİN. `_css_secret_scan` regex case-sensitive (`-i` yok); uppercase env-key'ler kaçar. T6 yalnız lowercase. Gitignored `.env` için mitigated (ls-files --exclude-standard önce eler), ama untracked-non-ignored allow-list dosyaları için açık.
- Karar: Adım 12 guard → kullanıcıya sunuldu.

---
