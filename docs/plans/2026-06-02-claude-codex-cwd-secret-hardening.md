---
title: claude-codex ailesi — Codex --cwd untracked-secret exposure hardening (CODEX-SCAN-SUBSTRATE)
status: plan-approved
date: 2026-06-02
source_spec: docs/specs/2026-06-02-claude-codex-cwd-secret-hardening.md
source_spec_unapproved_override: false
noisy_review_override: false
unresolved_high_severity_override: false
codex_plan_review_status: approved
codex_plan_review_iterations: 2
codex_plan_targeted_fixes: 0
codex_plan_review_log: docs/reviews/codex/2026-06-02-claude-codex-cwd-secret-hardening-plan.md
---

# claude-codex --cwd Secret Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 4 claude-codex komutunun (`spec` / `write-plan` / `execute-plan` / `simplify`) Codex çağrılarını canlı repo yerine **sanitized fetch clone** substratında çalıştırarak untracked `.env`/secret'ların Codex'e Read-tool ile sızmasını (S-1) kapatmak.

**Architecture:** Tek canonical `CODEX-SCAN-SUBSTRATE` bash bloğu (substrate fonksiyonları) 4 komut dosyasına **byte-identical** gömülür (yeni 4-way **Check C** drift kapısı), her komutun Codex call-site'ı substratı kurup `--cwd "$PROJECT_ROOT"` yerine `--cwd "$SCAN_ROOT"` kullanır. Mevcut **CODEX-CALL-PROTOCOL** bloğu (`c7b5976c`, 7-way) BYTE-IDENTICAL kalır — sadece call-site override prose'u eklenir. Substrate fonksiyonu **gerçek git fixture'larıyla re-runnable OP-4 harness** (T1-T6/T11/T12) ile doğrulanır.

**Tech Stack:** Markdown komut dosyaları (repo-DIŞI `~/.claude/commands/`); doğrulama + harness bash (`awk`/`md5sum`/`cmp`/gerçek `git` fixture); `codex-companion.mjs` (CODEX-CALL-PROTOCOL). Deliverable repo-dışı → repo commit = **docs + harness scripti** (komut dosyaları commit EDİLMEZ); gerçek invoke restart ister.

**Yön kararı (kullanıcı onaylı):** Sentez — harness-first TDD (gerçek git fixture) → doğrulanmış bloğu 4 dosyaya byte-identical göm → komut-başına call-site wiring (protokol dokunulmaz) → Check C 4-way (**byte-for-byte `cmp`** kapısı; normalize/whitespace/anlam toleransı YOK) + smoke. `@execution-pin` (OP-5) harness + call-site prose ile kapanır. Elenen: per-command vertical slice (blok drift riski).

---

## Checkpoint 1 Refinement (2026-06-03, execute Codex checkpoint review)

Execute checkpoint 1 Codex review'u 1 high + 1 medium döndürdü; ikisi de doğrulandı + düzeltildi (kullanıcı onaylı, Adım 8.5):
- **[high] T14 ayna → canonical fonksiyon:** Fail-closed call-site kararı artık canonical embedded fonksiyon **`run_codex_scan`** (CALL_KIND→overlay map + unresolved-base/substrate-fail → companion ÇAĞRILMAZ). Aynı sweep ile OP-5 base resolution da canonical **`css_resolve_base`**'e taşındı (sibling ayna). Harness T13/T14 artık **sourced gerçek fonksiyonu** test eder (ayna değil) → embedded reality byte (Check C) + davranış (harness) ikisiyle de doğrulu.
- **[medium] Fixture cleanup:** `mkfix` subshell-safe `FIXTRACK` kaydına geçti (`FIX=$(mkfix)` subshell'inden parent'a yansır); T15 leak-regression eklendi.

Etki: canonical blok 3→5 fonksiyon; tripwire 13→15 token (+`run_codex_scan`, +`css_resolve_base`); harness T1-T6/T11/T12 → T1-T6/T11-T15 (**37 PASS**). Call-site wiring (Task 4) **incelir**: per-command yalnız `REQUIRED_CURRENT_FILES`/`RESOLVED_BASE` set + `run_codex_scan "$CALL_KIND" <CALL>`. `css_resolve_base "$PROJECT_ROOT"` auto-base'i çözer. Log: `docs/reviews/codex/2026-06-03-claude-codex-cwd-secret-hardening-execute.md` (Checkpoint Turn 1). Aşağıdaki canonical blok + Task 4 wiring tablosu bu rafinajı yansıtır.

---

## File Structure

**Repo-içi (commit edilir):**
- Create: `docs/tools/codex-scan-substrate-harness.sh` — re-runnable OP-4 harness (T1-T6/T11/T12, gerçek git fixture).
- Modify: `docs/plans/2026-06-02-claude-codex-cwd-secret-hardening.md` (bu plan — metadata finalize).
- Create: `docs/reviews/codex/2026-06-02-claude-codex-cwd-secret-hardening-plan.md` (plan review log — komut Adım 12).

**Repo-DIŞI (deliverable — backup'lanır, edit edilir, git'e COMMIT EDİLMEZ):**
- `~/.claude/commands/spec-claude-codex.md`
- `~/.claude/commands/write-plan-claude-codex.md`
- `~/.claude/commands/execute-plan-claude-codex.md`
- `~/.claude/commands/simplify-claude-codex.md`

**Geçici (commit edilmez):**
- `/tmp/css-canonical.sh` — TDD sırasında canonical blok scratch'i (Task 2). Yeşil olunca Task 3'te 4 dosyaya gömülür.

---

## Canonical CODEX-SCAN-SUBSTRATE bloğu (tek kaynak — Task 2/3'te bire bir kullanılır)

Aşağıdaki blok **canonical metindir**: Task 2'de `/tmp/css-canonical.sh`'e yazılır, Task 3'te 4 komut dosyasına `# CODEX-SCAN-SUBSTRATE:BEGIN`/`:END` arası **byte-identical** gömülür. Spec satır 106-183'ten birebir; BEGIN satırının yorumu `<bu spec>` yerine 4-way için sabit metne çevrildi. **İç yorumlar dahil hiçbir karakter değişmez** (Check C `cmp` byte-for-byte).

```bash
# CODEX-SCAN-SUBSTRATE:BEGIN (4-way byte-identical; biri değişirse digerleri de — Check C)
build_scan_substrate() {
  SCAN_ROOT=""                                   # girişte temizle → fail'de stale reuse YOK
  local PROJECT_ROOT HEAD_SHA WT DEFAULT_REF r f
  PROJECT_ROOT=$(git rev-parse --show-toplevel) || return 1
  HEAD_SHA=$(git rev-parse --verify HEAD) || return 1
  WT=$(mktemp -d "${TMPDIR:-/tmp}/css.XXXXXX") || return 1
  SCAN_WT_DIRS+=("$WT")                          # caller shell'de birikir → tek EXIT trap temizler

  # 1. Bos repo + reflog kapali (sanitize)
  git -C "$WT" init -q || return 1
  git -C "$WT" config core.logAllRefUpdates false || return 1

  # 2. Live repo'dan YALNIZ gerekli objeler: current HEAD (+ base/default ref). TUM branch/stash/config DEGIL.
  #    `git fetch <path> <sha>` o commit + ancestry'sini getirir; stash/diger-branch/config GELMEZ.
  git -C "$WT" fetch -q --no-tags "$PROJECT_ROOT" "$HEAD_SHA" || return 1
  git -C "$WT" checkout -q --detach "$HEAD_SHA" || return 1
  # base ref'i companion icin kur. Call-site BASE_REF'i EXACT formda verir (named ref veya SHA); auto-scope'ta
  # call-site default branch'i LIVE repo'da resolveReviewTarget mantigiyla onceden cozer → substrate RE-GUESS ETMEZ
  # (Bulgu 5). Companion BASE_REF'i hangi isimle alacaksa substrate'ta ayni isim resolvable olmali (Bulgu 1).
  if [ -n "${BASE_REF:-}" ]; then
    git -C "$WT" fetch -q --no-tags "$PROJECT_ROOT" "$BASE_REF" || return 1
    if [ "$(git -C "$PROJECT_ROOT" rev-parse --verify -q "${BASE_REF}^{commit}" 2>/dev/null)" = "$BASE_REF" ]; then
      : # BASE_REF zaten SHA → obje fetch edildi, companion'a --base <sha> aynen verilir; REF YARATILMAZ (Bulgu 4)
    else
      case "$BASE_REF" in                          # named ref → EXACT namespace (Bulgu 1 + Turn7#2)
        refs/*)   git -C "$WT" update-ref "$BASE_REF"               FETCH_HEAD || return 1 ;;  # full ref aynen
        origin/*) git -C "$WT" update-ref "refs/remotes/$BASE_REF"  FETCH_HEAD || return 1 ;;
        *)        git -C "$WT" update-ref "refs/heads/$BASE_REF"    FETCH_HEAD || return 1 ;;
      esac
    fi
  fi  # @execution-pin: SHA-vs-ref tespiti + namespace esleme harness'ta kesinlesir

  # 3. Sanitize: remote + reflog kalintisi yok (S-1: credential/reflog/origin.url kanali kapanir)
  git -C "$WT" remote remove origin 2>/dev/null || true     # fetch-from-path remote yaratmaz; defensive
  rm -rf -- "$WT/.git/logs" || return 1

  # 4. Overlay — IKI MOD (Turn7#1): OVERLAY_WORKTREE=1 → TUM tracked dirty (YALNIZ adversarial-review --scope working-tree);
  #    OVERLAY_REQUIRED_ONLY=1 → pathspec-limited, YALNIZ REQUIRED_CURRENT_FILES (task --fresh; alakasiz dirty substrate'a girmez).
  if [ -n "${OVERLAY_WORKTREE:-}" ] || [ -n "${OVERLAY_REQUIRED_ONLY:-}" ]; then
    local -a PATHSPEC=()                          # worktree → bos (tumu); required-only → REQUIRED dosyalari
    if [ -z "${OVERLAY_WORKTREE:-}" ]; then
      while IFS= read -r f; do [ -n "$f" ] && PATHSPEC+=("$f"); done <<< "${REQUIRED_CURRENT_FILES:-}"
    fi
    # Tracked staged+unstaged INDEX-PRESERVING. Producer MATERYALIZE (pipe fail-closed DEGIL — Bulgu 3): bos=no-op, hata=return 1.
    local sp up; sp=$(mktemp "${TMPDIR:-/tmp}/css-sp.XXXXXX") || return 1; SCAN_WT_DIRS+=("$sp")
    up=$(mktemp "${TMPDIR:-/tmp}/css-up.XXXXXX") || return 1; SCAN_WT_DIRS+=("$up")
    git -C "$PROJECT_ROOT" diff --cached --binary HEAD -- "${PATHSPEC[@]}" > "$sp" || return 1   # staged (worktree: tumu; required: pathspec)
    git -C "$PROJECT_ROOT" diff --binary           -- "${PATHSPEC[@]}" > "$up" || return 1       # unstaged
    if [ -s "$sp" ]; then git -C "$WT" apply --index --whitespace=nowarn "$sp" || return 1; fi
    if [ -s "$up" ]; then git -C "$WT" apply         --whitespace=nowarn "$up" || return 1; fi
    # Untracked: YALNIZ allow-list (REQUIRED ∩ untracked-others) + icerik secret-scan + cp -P (her iki mod).
    while IFS= read -r f; do
      [ -z "$f" ] && continue
      git -C "$PROJECT_ROOT" ls-files --others --exclude-standard -- "$f" | grep -Fxq -- "$f" || continue
      _css_secret_scan "$PROJECT_ROOT/$f" || { echo "CSS: secret icerik, DISLANDI: $f" >&2; continue; }
      _css_copy_safe "$PROJECT_ROOT" "$WT" "$f" || return 1
    done <<< "${REQUIRED_CURRENT_FILES:-}"
    # symlink sweep (overlay sonrasi $WT-disina cozulen symlink'leri sil)
    local symlist; symlist=$(mktemp "${TMPDIR:-/tmp}/css-syml.XXXXXX") || return 1; SCAN_WT_DIRS+=("$symlist")
    find "$WT" -type l -print0 > "$symlist" || return 1
    local l tgt; while IFS= read -r -d '' l; do
      tgt=$(readlink -f -- "$l" 2>/dev/null || echo ""); case "$tgt/" in "$WT"/*) : ;; *) rm -f -- "$l" || return 1 ;; esac
    done < "$symlist"
  fi

  SCAN_ROOT="$WT"                                  # YALNIZ tum adimlar gecince
}

_css_copy_safe() { # $1=src_root $2=dst_root $3=relpath ; symlink DEREF ETMEZ; repo-disina cozulurse atla
  local src="$1/$3" dst="$2/$3" rp
  if [ -L "$src" ]; then rp=$(readlink -f -- "$src" 2>/dev/null || echo "")
    case "$rp/" in "$1"/*) : ;; *) echo "CSS: symlink repo-disina, atlandi: $3" >&2; return 0 ;; esac; fi
  mkdir -p -- "$(dirname -- "$dst")" || return 1; cp -P -- "$src" "$dst" || return 1
}
_css_secret_scan() { # $1=abs path ; icerik-bazli; eslesirse non-zero = disla
  ! grep -Eiq -- '(BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16}|secret[_-]?key|api[_-]?key|password[[:space:]]*=|token[[:space:]]*=|postgres://[^ ]*:[^ ]*@)' "$1" 2>/dev/null
}
css_resolve_base() { # $1=live repo path; echo EXACT base ref veya bos (fail-closed). USER_BASE_REF oncelikli.
  local r="$1" cand
  if [ -n "${USER_BASE_REF:-}" ]; then
    git -C "$r" rev-parse --verify -q "${USER_BASE_REF}^{commit}" >/dev/null 2>&1 || { echo ""; return 1; }
    echo "$USER_BASE_REF"; return 0
  fi
  cand=$(git -C "$r" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)
  if [ -z "$cand" ]; then
    for c in refs/remotes/origin/main refs/remotes/origin/master refs/remotes/origin/trunk \
             refs/heads/main refs/heads/master refs/heads/trunk; do
      git -C "$r" rev-parse --verify -q "${c}^{commit}" >/dev/null 2>&1 && { cand="$c"; break; }
    done
  fi
  if [ -n "$cand" ] && git -C "$r" rev-parse --verify -q "${cand}^{commit}" >/dev/null 2>&1; then echo "$cand"; else echo ""; fi
}
run_codex_scan() { # FAIL-CLOSED Codex cagrisi. $1=CALL_KIND; kalan args=<CALL> (task --fresh | adversarial-review [--base X]).
  local CALL_KIND="$1"; shift                       # companion YALNIZ tum kosullar gecince cagrilir
  OVERLAY_WORKTREE= ; OVERLAY_REQUIRED_ONLY=
  case "$CALL_KIND" in
    worktree-review)  OVERLAY_WORKTREE=1 ;;          # adversarial-review --scope working-tree -> TUM dirty
    task-fresh)       OVERLAY_REQUIRED_ONLY=1 ;;     # task --fresh -> yalniz REQUIRED (alakasiz dirty girmez)
    base-review)      : ;;                           # adversarial-review --base/auto -> overlay yok
  esac
  if [ "$CALL_KIND" = "base-review" ] && [ -z "${RESOLVED_BASE:-}" ]; then return 3; fi  # unresolved base -> NO call
  BASE_REF="${RESOLVED_BASE:-}"                      # task-fresh/worktree'de bos normal; base-review'da EXACT ref
  build_scan_substrate || return 2                   # substrate fail -> NO call (fail-closed; fallthrough YOK)
  timeout 480s node "$COMPANION" "$@" --cwd "$SCAN_ROOT" "$PROMPT"   # YALNIZ buraya gelince; --cwd SCAN_ROOT (S-1)
}
# CODEX-SCAN-SUBSTRATE:END
```

> **Not (marker hijyeni):** Yukarıdaki literal `BEGIN`/`END` satırları **yalnız** bu canonical blokta ve harness'ın awk pattern'inde geçer. Komut dosyalarının prose'unda (Sözleşme Notları Check C açıklaması dahil) literal marker token'ı YAZILMAZ — yoksa awk extraction kendini kirletir (CODEX-CALL-PROTOCOL ile aynı disiplin). Bu plan dosyası Check C hedefi DEĞİL, marker içermesi sorun değil.

---

## Call-site wiring şablonu (Task 4'te her komuta uyarlanır — CODEX-CALL-PROTOCOL DIŞINDA)

Her Codex call-site'ı, CODEX-CALL-PROTOCOL bloğunu izlemeden **önce** şunu yapar. Bu prose marker bloğunun DIŞINDADIR (drift contract korunur):

```bash
# (Komut başında BİR kez — trap + temizlik birikimi)
SCAN_WT_DIRS=(); trap 'for d in "${SCAN_WT_DIRS[@]:-}"; do [ -n "$d" ] && rm -rf -- "$d"; done' EXIT

# (Her Codex call-site'ında, CODEX-CALL-PROTOCOL'ün "2. Çağrı" adımından ÖNCE)
REQUIRED_CURRENT_FILES="<bu çağrının güncel ihtiyacı>"   # bkz. komut-başına tablo
OVERLAY_WORKTREE= ; OVERLAY_REQUIRED_ONLY=
case "$CALL_KIND" in
  worktree-review)  OVERLAY_WORKTREE=1 ;;        # adversarial-review --scope working-tree → TÜM dirty
  task-fresh)       OVERLAY_REQUIRED_ONLY=1 ;;   # task --fresh → yalnız REQUIRED (alakasız dirty girmez — Turn7#1)
  base-review)      : ;;                          # adversarial-review --base/auto → overlay yok, committed checkout
esac
# FAIL-CLOSED kontrol akışı (Codex Turn2 high#1 + med#2): companion YALNIZ tüm koşullar geçince çağrılır.
# (1) base-review'da RESOLVED_BASE çözülemediyse base'siz base-review YAPILMAZ → degrade, companion ÇAĞRILMAZ.
if [ "$CALL_KIND" = "base-review" ] && [ -z "${RESOLVED_BASE:-}" ]; then
  # → DEGRADATION: kullanıcıya base ref sor / HEAD-only review'a düş / abort. companion ÇAĞRILMAZ. (komutta return/continue)
  :
else
  BASE_REF="${RESOLVED_BASE:-}"          # task-fresh/worktree-review'da boş normal; base-review'da çözülmüş EXACT ref
  # (2) substrate kurulamazsa companion ÇAĞRILMAZ (fallthrough YOK — call YALNIZ success dalında, if-sonrası DEĞİL):
  if build_scan_substrate; then          # $() YOK → SCAN_WT_DIRS persist
    # companion gerçek invocation (grep-count değil) — YALNIZ SCAN_ROOT ile. CODEX-CALL-PROTOCOL preflight/
    # secret-scan adımları geçerli; YALNIZ --cwd hedefi SCAN_ROOT'a sabitlenir. Base <CALL> İÇİNDE ($SCOPE →
    # base-review'da "--base $BASE_REF"); ayrı --base EKLENMEZ. BASE_REF substratı kurdu (ref SCAN_ROOT'ta resolvable):
    timeout 480s node "$COMPANION" <CALL> --cwd "$SCAN_ROOT" "$PROMPT"
  else
    # → CODEX-CALL-PROTOCOL 3. Degradation (Claude-only / retry / abort); companion ÇAĞRILMAZ (fail-closed)
    :
  fi
fi
# (<CALL> = "task --fresh" | "adversarial-review $SCOPE"; $SCOPE base-review'da "--base $BASE_REF" içerir.)
```

> **S-1 invariant (Codex high#3):** Her gerçek Codex call-site'ı `--cwd "$SCAN_ROOT"` ile çağırır.
> `--cwd "$PROJECT_ROOT"` YALNIZ CODEX-CALL-PROTOCOL canonical bloğunun İÇİNDE (template örneği olarak)
> kalır — marker DIŞINDA hiçbir gerçek call-site `$PROJECT_ROOT`'a route etmez. Doğrulama grep-count değil,
> **extraction-based**: protokol bloğu çıkarıldıktan sonra kalan metinde `cwd "$PROJECT_ROOT"` = **0**
> (Task 4 Step 7). CODEX-CALL-PROTOCOL literal metni değişmez → Check A/B `c7b5976c` korunur.

**`RESOLVED_BASE` (OP-5 / @execution-pin) — auto-scope default branch çözümü (call-site, LIVE repo; FAIL-CLOSED):**

```bash
# Yalnız base-review auto-scope'ta gerekir. USER_BASE_REF verilmişse onu doğrula + EXACT formda kullan; yoksa default branch.
# USER_BASE_REF (kullanıcı-türevi) → tırnaksız kullanım ÖNCESİ doğrula (argument/flag injection):
if [ -n "${USER_BASE_REF:-}" ]; then
  git -C "$PROJECT_ROOT" rev-parse --verify -q "${USER_BASE_REF}^{commit}" >/dev/null 2>&1 || { echo "Geçersiz USER_BASE_REF; DUR" >&2; return 1; }
  RESOLVED_BASE="$USER_BASE_REF"
else
  # default branch — origin/HEAD → remote-tracking fallback → local fallback. Her aday rev-parse --verify ile commit'e çözülmeli.
  RESOLVED_BASE=""; cand=$(git -C "$PROJECT_ROOT" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)
  if [ -z "$cand" ]; then
    for c in refs/remotes/origin/main refs/remotes/origin/master refs/remotes/origin/trunk \
             refs/heads/main refs/heads/master refs/heads/trunk; do
      git -C "$PROJECT_ROOT" rev-parse --verify -q "${c}^{commit}" >/dev/null 2>&1 && { cand="$c"; break; }
    done
  fi
  if [ -n "$cand" ] && git -C "$PROJECT_ROOT" rev-parse --verify -q "${cand}^{commit}" >/dev/null 2>&1; then
    RESOLVED_BASE="$cand"
  else
    # FAIL-CLOSED: hiçbir aday commit'e çözülmedi → auto base review YAPMA (sessiz boş base ile substrate kurma);
    # kullanıcıya base ref sor veya base'siz (HEAD-only) review'a düş. RESOLVED_BASE boş bırakılırsa call-site bunu açıkça ele alır.
    RESOLVED_BASE=""; echo "CSS: default base çözülemedi — auto base review atlanıyor (kullanıcıya bildir)" >&2
  fi
fi
```

**Komut-başına call-site bağlama tablosu (Task 4):**

| Komut | Call-site | `CALL_KIND` | `REQUIRED_CURRENT_FILES` | `RESOLVED_BASE` |
|---|---|---|---|---|
| `spec-claude-codex` | Adım 2 `task --fresh` | `task-fresh` | `$SPEC_PATH` | (boş) |
| `spec-claude-codex` | Adım 6 `adversarial-review` | dirty→`worktree-review`, clean→`base-review` | `$SPEC_PATH` | dirty→boş; clean→`USER_BASE_REF` veya auto-default |
| `write-plan-claude-codex` | ön-analiz `task --fresh` | `task-fresh` | `$SPEC_PATH` | (boş) |
| `write-plan-claude-codex` | plan review `adversarial-review` | `$PLAN_PATH` dirty→`worktree-review`, clean→`base-review` | `$PLAN_PATH` | dirty→boş; clean→`USER_BASE_REF` veya auto-default |
| `execute-plan-claude-codex` | Adım 6 `task --fresh` | `task-fresh` | `$PLAN_PATH` | (boş) |
| `execute-plan-claude-codex` | Adım 8/11 `adversarial-review --base` | `base-review` | `$PLAN_PATH` | `$BASE_REF` (committed-range; komut zaten biliyor) |
| `simplify-claude-codex` | pre-scan `task --fresh` | `task-fresh` | komutun okuduğu güncel dosyalar (newline-sep) | (boş) |
| `simplify-claude-codex` | final review `adversarial-review` | `worktree-review` | komutun okuduğu güncel dosyalar | (boş; working-tree) |

---

## Task 1: Baseline — backup + Check A 7-way intact + clean-slate

**Files:**
- Read/backup: `~/.claude/commands/{spec,write-plan,execute-plan,simplify}-claude-codex.md`
- Read: tüm 7 `*-claude-codex` komut (Check A baseline)

- [ ] **Step 1: 4 hedef dosyayı backup'la**

```bash
TS=$(date +%Y%m%d-%H%M%S)
for f in spec write-plan execute-plan simplify; do
  cp -p ~/.claude/commands/$f-claude-codex.md ~/.claude/commands/$f-claude-codex.md.bak-$TS
done
ls ~/.claude/commands/*.bak-$TS | wc -l
```

Run: yukarıdaki blok.
Expected: `4` (4 backup oluştu). Rollback yolu: `*.bak-$TS`.

- [ ] **Step 2: CODEX-CALL-PROTOCOL 7-way baseline intact (c7b5976c) — dokunmadan ÖNCE**

```bash
for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex review-claude-codex security-review-claude-codex finish-branch-claude-codex; do
  awk '/<!-- CODEX-CALL-PROTOCOL:BEGIN/,/<!-- CODEX-CALL-PROTOCOL:END -->/' ~/.claude/commands/$f.md | md5sum
done | sort -u | tee /tmp/css-baseline-cap.md5 | wc -l
```

Run: yukarıdaki blok.
Expected: `1` (tek md5 = `c7b5976c9513391909310883c40575c3`). **Değilse DUR** — aile zaten drift'li, önce o düzeltilmeli (bu işin baseline'ı bozuk).

- [ ] **Step 3: Clean-slate teyit — hiçbir hedefte SUBSTRATE bloğu yok**

```bash
grep -lF 'CODEX-SCAN-SUBSTRATE:BEGIN' ~/.claude/commands/{spec,write-plan,execute-plan,simplify}-claude-codex.md 2>/dev/null | wc -l
```

Run: yukarıdaki blok.
Expected: `0` (henüz gömülmedi; resume ise farklı — o durumda Task 3 idempotent insert'e dikkat).

- [ ] **Step 4: Commit yok** — bu task salt baseline/backup; commit Task 2'de (harness) başlar.

---

## Task 2: OP-4 harness + canonical blok (TDD, gerçek git fixture)

**Files:**
- Create: `docs/tools/codex-scan-substrate-harness.sh`
- Create (geçici): `/tmp/css-canonical.sh`

> Bu task'ın özü: harness'ı **önce** yaz (T1-T6/T11/T12), canonical bloğu scratch'e koy, harness'ı çalıştır, **tüm testler geçene dek** bloğu (özellikle `@execution-pin` namespace/SHA dalları) düzelt. Markdown test edilemez; bash fonksiyonu edilir. Harness `cmp`-bazlı değil davranış-bazlıdır; Check C (byte) Task 3'te.

- [ ] **Step 1: Canonical bloğu scratch'e yaz**

`/tmp/css-canonical.sh` dosyasına, bu planın "Canonical CODEX-SCAN-SUBSTRATE bloğu" bölümündeki kod bloğunu (BEGIN..END satırları dahil) **birebir** yaz. (Execution: plan bloğunu kopyala-yapıştır; hiçbir karakter değişmez.)

Run: `bash -n /tmp/css-canonical.sh && grep -c 'CODEX-SCAN-SUBSTRATE:END' /tmp/css-canonical.sh`
Expected: syntax OK (hata yok) + `1`.

- [ ] **Step 2: Harness iskeleti + fixture builder (failing — fonksiyonlar henüz source edilmeden çağrılır)**

`docs/tools/codex-scan-substrate-harness.sh` oluştur:

```bash
#!/usr/bin/env bash
# OP-4 re-runnable harness — CODEX-SCAN-SUBSTRATE fail-closed/regression tests (T1-T6, T11, T12).
# Blok kaynağı: $CSS_BLOCK_FILE (TDD scratch) VEYA canonical komut dosyasından awk extraction (regression).
# Gerçek throwaway git fixture'lar kurar; her test izole; herhangi FAIL → exit 1.
set -u
PASS=0; FAIL=0
_ok(){ echo "  ok: $*"; PASS=$((PASS+1)); }
_no(){ echo "  FAIL: $*"; FAIL=$((FAIL+1)); }

# --- Blok kaynağı: scratch (dev) veya canonical command extraction (regression) ---
CANON_CMD="${CSS_CANON_CMD:-$HOME/.claude/commands/spec-claude-codex.md}"
BLOCK_FILE="${CSS_BLOCK_FILE:-}"
if [ -z "$BLOCK_FILE" ]; then
  BLOCK_FILE=$(mktemp)
  awk '/# CODEX-SCAN-SUBSTRATE:BEGIN/,/# CODEX-SCAN-SUBSTRATE:END/' "$CANON_CMD" > "$BLOCK_FILE"
fi
[ -s "$BLOCK_FILE" ] || { echo "FATAL: blok kaynağı boş ($BLOCK_FILE / $CANON_CMD)"; exit 2; }
SCAN_WT_DIRS=()
# shellcheck disable=SC1090
source "$BLOCK_FILE"
type build_scan_substrate >/dev/null 2>&1 || { echo "FATAL: build_scan_substrate tanımsız"; exit 2; }

CLEAN_DIRS=()
_cleanup(){ for d in "${SCAN_WT_DIRS[@]:-}" "${CLEAN_DIRS[@]:-}"; do [ -n "$d" ] && rm -rf -- "$d"; done; }
trap _cleanup EXIT

# Fixture: base+feature commit; ignored .env; opsiyonel staged/unstaged/untracked/symlink/secret/base-ref.
# Kullanım: FIX=$(mkfix); sonra istenen mutasyonlar eklenir.
mkfix(){
  local d; d=$(mktemp -d "${TMPDIR:-/tmp}/cssfix.XXXXXX"); CLEAN_DIRS+=("$d")
  git -C "$d" init -q
  git -C "$d" symbolic-ref HEAD refs/heads/main      # default-branch skew'a karşı deterministik (init -b main eşdeğeri, version-agnostik)
  git -C "$d" config user.email t@t; git -C "$d" config user.name t
  printf 'base\n' > "$d/tracked.txt"
  printf '.env\n' > "$d/.gitignore"
  printf 'SECRET=topsecret\n' > "$d/.env"            # gitignored secret
  git -C "$d" add tracked.txt .gitignore; git -C "$d" commit -qm base
  echo "$d"
}

# build_scan_substrate'i AYNI SHELL'de çalıştır (subshell DEĞİL): spec'in caller-shell state
# contract'ı (SCAN_ROOT + SCAN_WT_DIRS mutasyonu parent'a yansır) ancak böyle test edilir (Codex high#1).
_build_in(){ local OLD="$PWD"; cd "$1" || return 1; build_scan_substrate; local rc=$?; cd "$OLD" || return 1; return "$rc"; }

echo "BLOCK_FILE=$BLOCK_FILE"
```

Run: `bash docs/tools/codex-scan-substrate-harness.sh; echo "exit=$?"`
Expected (henüz test yok): `BLOCK_FILE=...` + `exit=0` (scratch source edildi, fonksiyon tanımlı). Eğer `CSS_BLOCK_FILE=/tmp/css-canonical.sh bash ...` ile çalıştırırsan scratch kullanılır.

- [ ] **Step 3: T7-T10 sağlık (Codex koştu — harness'ta da baz): clean clone + dirty overlay diff doğruluğu**

Harness'a ekle (fixture helper'ından sonra):

```bash
# --- T7/T8: clean clone (overlay yok) — HEAD checkout + base ref resolvable + .env yok + caller-state ---
t_clean(){ echo "[T7/T8] clean clone";
  local FIX; FIX=$(mkfix)
  git -C "$FIX" checkout -q -b feature; printf 'feat\n' >> "$FIX/tracked.txt"; git -C "$FIX" commit -qam feat
  local pre="${#SCAN_WT_DIRS[@]}"
  REQUIRED_CURRENT_FILES=""; OVERLAY_WORKTREE=""; OVERLAY_REQUIRED_ONLY=""; BASE_REF="main"
  _build_in "$FIX" || { _no "T7 build başarısız"; return; }
  [ -n "$SCAN_ROOT" ] && _ok "T7 SCAN_ROOT parent'ta set (caller-shell state)" || { _no "T7 SCAN_ROOT boş (subshell sızıntısı?)"; return; }
  [ "${#SCAN_WT_DIRS[@]}" -gt "$pre" ] && _ok "T7 SCAN_WT_DIRS parent'ta birikti (caller-shell state)" || _no "T7 SCAN_WT_DIRS birikmedi"
  [ ! -e "$SCAN_ROOT/.env" ] && _ok "T7 .env yok" || _no "T7 .env sızdı"
  git -C "$SCAN_ROOT" rev-parse --verify -q 'refs/heads/main^{commit}' >/dev/null && _ok "T8 base ref resolvable" || _no "T8 base ref yok"
  [ -z "$(git -C "$SCAN_ROOT" stash list 2>/dev/null)" ] && _ok "T8 stash yok" || _no "T8 stash sızdı"
  [ ! -d "$SCAN_ROOT/.git/logs" ] && _ok "T8 reflog yok" || _no "T8 reflog var"
}
# --- T9/T10: working-tree overlay — staged/unstaged/untracked korunur, .env yok ---
t_dirty(){ echo "[T9/T10] dirty overlay";
  local FIX; FIX=$(mkfix)
  printf 'staged\n' >> "$FIX/tracked.txt"; git -C "$FIX" add tracked.txt   # staged
  printf 'unstaged\n' >> "$FIX/tracked.txt"                                # unstaged
  printf 'newfile\n' > "$FIX/new.txt"                                      # untracked (allow-list'e konacak)
  REQUIRED_CURRENT_FILES=$'new.txt'; OVERLAY_WORKTREE=1; OVERLAY_REQUIRED_ONLY=""; BASE_REF=""
  _build_in "$FIX" || { _no "T9 build başarısız"; return; }
  grep -q staged "$SCAN_ROOT/tracked.txt" && grep -q unstaged "$SCAN_ROOT/tracked.txt" && _ok "T9 staged+unstaged uygulandı" || _no "T9 overlay eksik"
  [ -f "$SCAN_ROOT/new.txt" ] && _ok "T10 untracked korundu" || _no "T10 untracked yok"
  [ ! -e "$SCAN_ROOT/.env" ] && _ok "T10 .env yok" || _no "T10 .env sızdı"
}
```

Run: harness sonuna `t_clean; t_dirty; echo "PASS=$PASS FAIL=$FAIL"` ekleyip `CSS_BLOCK_FILE=/tmp/css-canonical.sh bash docs/tools/codex-scan-substrate-harness.sh`
Expected: T7-T10 tüm satırlar `ok:`, `FAIL=0`.

- [ ] **Step 4: T1 — index-preserving (path-with-space + staged/unstaged/untracked ayrımı)**

```bash
t1(){ echo "[T1] index-preserving + path-with-space";
  local FIX; FIX=$(mkfix)
  printf 'a\n' > "$FIX/with space.txt"; git -C "$FIX" add "with space.txt"; git -C "$FIX" commit -qm sp
  printf 'staged-mod\n' >> "$FIX/with space.txt"; git -C "$FIX" add "with space.txt"   # staged mod
  printf 'unstaged-mod\n' >> "$FIX/tracked.txt"                                        # unstaged mod
  printf 'u\n' > "$FIX/untr.txt"                                                       # untracked
  REQUIRED_CURRENT_FILES=$'untr.txt'; OVERLAY_WORKTREE=1; OVERLAY_REQUIRED_ONLY=""; BASE_REF=""
  _build_in "$FIX" || { _no "T1 build başarısız"; return; }
  grep -q staged-mod "$SCAN_ROOT/with space.txt" && _ok "T1 staged path-with-space" || _no "T1 staged eksik"
  grep -q unstaged-mod "$SCAN_ROOT/tracked.txt" && _ok "T1 unstaged" || _no "T1 unstaged eksik"
  # staged- liğin korunduğu: substrate index'inde 'with space.txt' staged görünmeli
  git -C "$SCAN_ROOT" diff --cached --name-only | grep -qx 'with space.txt' && _ok "T1 staged index korundu" || _no "T1 staged index kaybı"
  [ -f "$SCAN_ROOT/untr.txt" ] && _ok "T1 untracked" || _no "T1 untracked eksik"
}
```

Run: harness'a `t1` ekle, çalıştır (`CSS_BLOCK_FILE=/tmp/css-canonical.sh`).
Expected: T1 tüm satırlar `ok:`.

- [ ] **Step 5: T2 — producer/fetch hatası → non-zero + SCAN_ROOT boş (fail-closed)**

```bash
t2(){ echo "[T2] fail-closed: geçersiz BASE_REF fetch hatası";
  local FIX; FIX=$(mkfix)
  REQUIRED_CURRENT_FILES=""; OVERLAY_WORKTREE=""; OVERLAY_REQUIRED_ONLY=""; BASE_REF="nonexistent-ref-xyz"
  _build_in "$FIX"; local rc=$?
  [ "$rc" -ne 0 ] && _ok "T2 non-zero rc ($rc)" || _no "T2 rc=0 (fail-closed değil)"
  [ -z "$SCAN_ROOT" ] && _ok "T2 SCAN_ROOT boş" || _no "T2 SCAN_ROOT set ($SCAN_ROOT)"
}
```

Run: harness'a `t2` ekle, çalıştır.
Expected: T2 `ok:` (rc≠0 + SCAN_ROOT boş). **Not:** geçersiz ref'te `git fetch` non-zero döner → `|| return 1` tetiklenir.

- [ ] **Step 6: T3 — stale guard (1. OK, 2. fail → eski SCAN_ROOT reuse YOK)**

```bash
t3(){ echo "[T3] stale guard";
  local FIX; FIX=$(mkfix)
  REQUIRED_CURRENT_FILES=""; OVERLAY_WORKTREE=""; OVERLAY_REQUIRED_ONLY=""; BASE_REF=""
  _build_in "$FIX"
  local first="$SCAN_ROOT"; [ -n "$first" ] && _ok "T3 ilk çağrı SCAN_ROOT set" || _no "T3 ilk çağrı boş"
  BASE_REF="bad-ref-2"
  _build_in "$FIX"
  [ -z "$SCAN_ROOT" ] && _ok "T3 fail sonrası SCAN_ROOT boş (stale yok)" || _no "T3 stale reuse: $SCAN_ROOT"
}
```

Run: harness'a `t3` ekle, çalıştır.
Expected: T3 `ok:` (girişteki `SCAN_ROOT=""` stale'i önler).

- [ ] **Step 7: T4 — cleanup (EXIT trap → /tmp/css.* kalmaz)**

```bash
t4(){ echo "[T4] cleanup";
  local FIX; FIX=$(mkfix)
  REQUIRED_CURRENT_FILES=""; OVERLAY_WORKTREE=""; OVERLAY_REQUIRED_ONLY=""; BASE_REF=""
  _build_in "$FIX"
  local d="$SCAN_ROOT"; [ -d "$d" ] && _ok "T4 substrate var" || _no "T4 substrate yok"
  # call-site trap mantığını simüle et:
  for x in "${SCAN_WT_DIRS[@]:-}"; do [ -n "$x" ] && rm -rf -- "$x"; done; SCAN_WT_DIRS=()
  [ ! -d "$d" ] && _ok "T4 trap sonrası substrate silindi" || _no "T4 substrate kaldı: $d"
}
```

Run: harness'a `t4` ekle, çalıştır.
Expected: T4 `ok:`.

- [ ] **Step 8: T5 — symlink exfil (`notes.txt -> .env`) → secret yok**

```bash
t5(){ echo "[T5] symlink exfil";
  local FIX; FIX=$(mkfix)
  ( cd "$FIX"; ln -s .env notes.txt )                          # untracked symlink → .env
  REQUIRED_CURRENT_FILES=$'notes.txt'; OVERLAY_WORKTREE=1; OVERLAY_REQUIRED_ONLY=""; BASE_REF=""
  _build_in "$FIX" || { _no "T5 build başarısız"; return; }
  # notes.txt ya kopyalanmadı ya da dangling symlink → topsecret içeriği substrate'ta OLMAMALI
  if grep -rqI topsecret "$SCAN_ROOT" 2>/dev/null; then _no "T5 secret sızdı"; else _ok "T5 secret yok"; fi
  [ ! -e "$SCAN_ROOT/.env" ] && _ok "T5 .env yok" || _no "T5 .env sızdı"
}
```

Run: harness'a `t5` ekle, çalıştır.
Expected: T5 `ok:` (cp -P deref etmez + symlink sweep + .env substrate'ta yok).

- [ ] **Step 9: T6 — allow-list'te secret-içerik → _css_secret_scan dışlar**

```bash
t6(){ echo "[T6] secret-content exclusion";
  local FIX; FIX=$(mkfix)
  printf 'api_key=abcd1234\n' > "$FIX/conf.txt"                # untracked, secret-içerik
  REQUIRED_CURRENT_FILES=$'conf.txt'; OVERLAY_WORKTREE=1; OVERLAY_REQUIRED_ONLY=""; BASE_REF=""
  _build_in "$FIX" || { _no "T6 build başarısız"; return; }
  [ ! -e "$SCAN_ROOT/conf.txt" ] && _ok "T6 secret dosya dışlandı" || _no "T6 secret dosya sızdı"
}
```

Run: harness'a `t6` ekle, çalıştır.
Expected: T6 `ok:` (`api[_-]?key` pattern eşleşir → dışlanır).

- [ ] **Step 10: T11 — OVERLAY_REQUIRED_ONLY alakasız dirty tracked'ı dışlar (Turn7#1)**

```bash
t11(){ echo "[T11] required-only excludes unrelated dirty";
  local FIX; FIX=$(mkfix)
  printf 'orig\n' > "$FIX/secrets.txt"; git -C "$FIX" add secrets.txt; git -C "$FIX" commit -qm s
  printf 'DIRTY-SECRET\n' >> "$FIX/secrets.txt"                # alakasız tracked dirty
  printf 'plan body\n' > "$FIX/plan.md"                        # PLAN_PATH (untracked, required)
  REQUIRED_CURRENT_FILES=$'plan.md'; OVERLAY_WORKTREE=""; OVERLAY_REQUIRED_ONLY=1; BASE_REF=""
  _build_in "$FIX" || { _no "T11 build başarısız"; return; }
  [ -f "$SCAN_ROOT/plan.md" ] && _ok "T11 plan.md var" || _no "T11 plan.md yok"
  grep -q DIRTY-SECRET "$SCAN_ROOT/secrets.txt" 2>/dev/null && _no "T11 alakasız dirty sızdı" || _ok "T11 secrets.txt HEAD hali (dirty girmedi)"
}
```

Run: harness'a `t11` ekle, çalıştır.
Expected: T11 `ok:` (pathspec=plan.md → secrets.txt diff'i uygulanmaz; substrate'ta HEAD hali).

- [ ] **Step 11: T12 — base-ref namespace (origin/main · refs/remotes/... · main · SHA)**

```bash
t12(){ echo "[T12] base-ref namespace";
  local FIX; FIX=$(mkfix)
  git -C "$FIX" update-ref refs/remotes/origin/main HEAD      # remote-tracking ref
  git -C "$FIX" branch -q other HEAD                          # named branch
  local SHA; SHA=$(git -C "$FIX" rev-parse HEAD)
  for ref in origin/main refs/remotes/origin/main other "$SHA"; do
    REQUIRED_CURRENT_FILES=""; OVERLAY_WORKTREE=""; OVERLAY_REQUIRED_ONLY=""; BASE_REF="$ref"
    _build_in "$FIX" || { _no "T12 build başarısız ($ref)"; continue; }
    case "$ref" in
      origin/main)               git -C "$SCAN_ROOT" rev-parse --verify -q 'refs/remotes/origin/main^{commit}' >/dev/null && _ok "T12 origin/main" || _no "T12 origin/main resolve yok" ;;
      refs/remotes/origin/main)  git -C "$SCAN_ROOT" rev-parse --verify -q 'refs/remotes/origin/main^{commit}' >/dev/null && _ok "T12 full ref" || _no "T12 full ref resolve yok" ;;
      other)                     git -C "$SCAN_ROOT" rev-parse --verify -q 'refs/heads/other^{commit}' >/dev/null && _ok "T12 named" || _no "T12 named resolve yok" ;;
      *)                         # SHA → ref yaratılMAMALI (yeni heads/* yok), ama SHA resolvable
                                 git -C "$SCAN_ROOT" rev-parse --verify -q "$ref^{commit}" >/dev/null \
                                   && [ -z "$(git -C "$SCAN_ROOT" for-each-ref --format='%(refname)' "refs/heads/$ref" 2>/dev/null)" ] \
                                   && _ok "T12 SHA (ref yaratılmadı)" || _no "T12 SHA dalı" ;;
    esac
  done
}
```

Run: harness'a `t12` ekle (master runner Step 12b'de güncellenecek).
Expected: T12 tüm satırlar `ok:`.

- [ ] **Step 11b: T13 — OP-5 default base resolution fail-closed (origin/main var, local main + origin/HEAD YOK)**

Call-site RESOLVED_BASE mantığını (auto-default) ayna olarak harness'ta test et (call-site prose; canonical blok DIŞINDA → fonksiyon olarak doğrulanır):

```bash
_resolve_base(){ # $1=repo ; "RESOLVED_BASE (OP-5)" snippet'inin aynası (USER_BASE_REF'siz dal)
  local r="$1" cand
  cand=$(git -C "$r" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)
  if [ -z "$cand" ]; then
    for c in refs/remotes/origin/main refs/remotes/origin/master refs/remotes/origin/trunk refs/heads/main refs/heads/master refs/heads/trunk; do
      git -C "$r" rev-parse --verify -q "${c}^{commit}" >/dev/null 2>&1 && { cand="$c"; break; }
    done
  fi
  if [ -n "$cand" ] && git -C "$r" rev-parse --verify -q "${cand}^{commit}" >/dev/null 2>&1; then echo "$cand"; else echo ""; fi
}
t13(){ echo "[T13] OP-5 base resolution fail-closed";
  local FIX; FIX=$(mkfix)                                       # mkfix → HEAD=main (local main var)
  git -C "$FIX" update-ref refs/remotes/origin/main HEAD        # remote-tracking ref ekle
  git -C "$FIX" branch -m main mainline                         # local main'i kaldır (origin-HEAD da yok)
  local rb; rb=$(_resolve_base "$FIX")
  [ "$rb" = "refs/remotes/origin/main" ] && _ok "T13 origin/main fallback ($rb)" || _no "T13 yanlış base: '$rb'"
  # negative: tamamen base'siz repo → boş (fail-closed, hata değil)
  local BARE; BARE=$(mktemp -d "${TMPDIR:-/tmp}/cssbare.XXXXXX"); CLEAN_DIRS+=("$BARE")
  git -C "$BARE" init -q; git -C "$BARE" symbolic-ref HEAD refs/heads/zzz
  git -C "$BARE" config user.email t@t; git -C "$BARE" config user.name t
  printf 'x\n' > "$BARE/f"; git -C "$BARE" add f; git -C "$BARE" commit -qm x
  rb=$(_resolve_base "$BARE"); [ -z "$rb" ] && _ok "T13 base yok → boş (fail-closed)" || _no "T13 beklenmeyen base: '$rb'"
}
```

Run: harness'a `t13` ekle (master runner Step 12b'de).
Expected: T13 `ok:` (remote-tracking fallback + fail-closed boş).

- [ ] **Step 11d: T14 — call-site WRAPPER fail-closed (fake companion → companion çağrı sayısı)**

Codex Turn2 high#1 + med#2: substrate-fail veya unresolved-base'de companion **ÇAĞRILMAMALI**. build_scan_substrate'in non-zero dönmesi yetmez — call-site wrapper'ın invocation'ı bastırdığı ayrıca kanıtlanmalı. Fake `node` ile call sayısını ölç (wrapper "Call-site wiring şablonu" fail-closed akışının aynası):

```bash
_css_callsite(){ # call-site template control-flow AYNASI (fail-closed). $1=CALL_KIND
  local CALL_KIND="$1"
  if [ "$CALL_KIND" = "base-review" ] && [ -z "${RESOLVED_BASE:-}" ]; then return 0; fi   # unresolved base → degrade, NO call
  BASE_REF="${RESOLVED_BASE:-}"
  if build_scan_substrate; then node "$COMPANION" task --fresh --cwd "$SCAN_ROOT" "P"; fi   # call YALNIZ başarıda
}
t_callsite(){ echo "[T14] call-site fail-closed (fake companion)";
  local FIX OLD CALLS; FIX=$(mkfix); OLD="$PWD"; CALLS=$(mktemp); CLEAN_DIRS+=("$CALLS")
  node(){ echo x >> "$CALLS"; }; COMPANION="/dummy"          # fake companion: her çağrı bir satır
  cd "$FIX"
  REQUIRED_CURRENT_FILES=""; OVERLAY_WORKTREE=""; OVERLAY_REQUIRED_ONLY=""
  : > "$CALLS"; RESOLVED_BASE="bad-ref-zzz"; _css_callsite base-review     # (a) substrate fail (bad base fetch)
  [ ! -s "$CALLS" ] && _ok "T14a substrate fail → 0 companion call" || _no "T14a companion çağrıldı"
  : > "$CALLS"; RESOLVED_BASE=""; _css_callsite base-review               # (b) unresolved auto-base
  [ ! -s "$CALLS" ] && _ok "T14b unresolved base → 0 companion call" || _no "T14b companion çağrıldı"
  : > "$CALLS"; RESOLVED_BASE=""; _css_callsite task-fresh                # (c) success → 1 call
  [ "$(wc -l < "$CALLS")" -eq 1 ] && _ok "T14c success → 1 companion call" || _no "T14c çağrı sayısı $(wc -l < "$CALLS")"
  cd "$OLD"; unset -f node
}
```

Run: harness'a `t_callsite` ekle (master runner'a dahil).
Expected: T14a/b `0 call`, T14c `1 call` — hepsi `ok:`.

- [ ] **Step 11e: Master runner + tüm testler yeşil**

Harness sonuna ana satırı ekle:

```bash
t_clean; t_dirty; t1; t2; t3; t4; t5; t6; t11; t12; t13; t_callsite
echo "PASS=$PASS FAIL=$FAIL"; [ "$FAIL" -eq 0 ] || exit 1
```

Run: `CSS_BLOCK_FILE=/tmp/css-canonical.sh bash docs/tools/codex-scan-substrate-harness.sh; echo "rc=$?"`
Expected: TÜM testler `ok:`, `PASS=N FAIL=0`, `rc=0`. **Herhangi bir FAIL → bloğu (özellikle namespace/SHA `@execution-pin` dalını) veya fixture'ı düzelt + /tmp/css-canonical.sh güncelle + tekrar koş.** Bu loop OP-4'ün kapanmasıdır.

- [ ] **Step 12: Commit harness (canonical scratch ile yeşil)**

```bash
chmod +x docs/tools/codex-scan-substrate-harness.sh
git add docs/tools/codex-scan-substrate-harness.sh
git commit -m "test: add OP-4 re-runnable harness for CODEX-SCAN-SUBSTRATE"
```

Run: yukarıdaki blok.
Expected: commit oluştu. (Bu noktada blok henüz komut dosyalarında değil; harness scratch'ten doğrulandı.)

---

## Task 3: Bloğu 4 dosyaya byte-identical göm + Check C (cmp 4-way) + regression

**Files:**
- Modify: `~/.claude/commands/{spec,write-plan,execute-plan,simplify}-claude-codex.md`

- [ ] **Step 1: Her dosyaya canonical bloğu yerleştir (hand-edit YOK — scratch'ten yapıştır)**

Her 4 dosyada, "CODEX-CALL-PROTOCOL bloğunun DIŞINDA" uygun bir bölüme (yeni `## CODEX-SCAN-SUBSTRATE` başlığı altında, bir ```bash fence içine) `/tmp/css-canonical.sh`'in **tam içeriğini** (BEGIN..END) aynen ekle. Marker satırları + aradaki tüm satırlar AYNEN. Prose'da literal marker token'ı YOK.

(Execution: editor/awk ile aynı temp içerik 4 dosyaya eklenir; manuel retype YASAK.)

- [ ] **Step 2: Check C — 4 blok byte-for-byte cmp (SERT kapı)**

```bash
for f in spec write-plan execute-plan simplify; do
  awk '/# CODEX-SCAN-SUBSTRATE:BEGIN/,/# CODEX-SCAN-SUBSTRATE:END/' ~/.claude/commands/$f-claude-codex.md > /tmp/css-$f.block
done
# (a) tek md5 (byte hash):
md5sum /tmp/css-{spec,write-plan,execute-plan,simplify}.block | awk '{print $1}' | sort -u | tee /tmp/css-c.md5 | wc -l
# (b) pairwise cmp (byte-for-byte; normalize/whitespace YOK):
cmp -s /tmp/css-spec.block /tmp/css-write-plan.block && cmp -s /tmp/css-spec.block /tmp/css-execute-plan.block && cmp -s /tmp/css-spec.block /tmp/css-simplify.block && echo "CHECK-C-CMP: PASS" || echo "CHECK-C-CMP: FAIL"
# (c) scratch ile de birebir (gömme bozulmadı):
cmp -s /tmp/css-spec.block /tmp/css-canonical.sh && echo "MATCHES-CANONICAL: PASS" || echo "MATCHES-CANONICAL: FAIL"
```

Run: yukarıdaki blok.
Expected: (a) `1` (tek md5) · (b) `CHECK-C-CMP: PASS` · (c) `MATCHES-CANONICAL: PASS`. **Herhangi biri FAIL → iş bitmiş sayılmaz** (byte drift; normalize/whitespace/"anlam aynı" KABUL EDİLMEZ) → yeniden yapıştır.

- [ ] **Step 3: Check C tripwire token (spec Drift Contract listesi — her token 4 dosyada)**

```bash
TOKENS=('init -q' 'fetch -q --no-tags' 'core.logAllRefUpdates false' 'remote remove origin' '.git/logs' 'apply --index' 'OVERLAY_WORKTREE' 'OVERLAY_REQUIRED_ONLY' '_css_copy_safe' 'cp -P' '_css_secret_scan' 'REQUIRED_CURRENT_FILES' 'SCAN_WT_DIRS')
allok=1
for tok in "${TOKENS[@]}"; do
  n=0; for f in spec write-plan execute-plan simplify; do
    awk '/# CODEX-SCAN-SUBSTRATE:BEGIN/,/# CODEX-SCAN-SUBSTRATE:END/' ~/.claude/commands/$f-claude-codex.md | grep -cF "$tok" | grep -q '^0$' && continue; n=$((n+1)); done
  [ "$n" -eq 4 ] || { echo "TRIPWIRE FAIL: '$tok' yalnız $n/4"; allok=0; }
done
[ "$allok" -eq 1 ] && echo "CHECK-C-TRIPWIRE: PASS (13/13 token ×4)"
```

Run: yukarıdaki blok.
Expected: `CHECK-C-TRIPWIRE: PASS`.

- [ ] **Step 4: Regression — harness'ı GÖMÜLÜ bloktan (extraction) çalıştır**

```bash
CSS_CANON_CMD="$HOME/.claude/commands/spec-claude-codex.md" bash docs/tools/codex-scan-substrate-harness.sh; echo "exit=$?"
```

Run: yukarıdaki blok (artık `CSS_BLOCK_FILE` verilmiyor → harness komut dosyasından extract eder).
Expected: tüm testler `ok:`, `FAIL=0`, `exit=0`. Bu, gömülü kopyanın da geçtiğini kanıtlar (embedding corruption yakalanır).

- [ ] **Step 5: CODEX-CALL-PROTOCOL hâlâ intact (gömme onu bozmadı)**

```bash
for f in spec write-plan execute-plan simplify; do
  awk '/<!-- CODEX-CALL-PROTOCOL:BEGIN/,/<!-- CODEX-CALL-PROTOCOL:END -->/' ~/.claude/commands/$f-claude-codex.md | md5sum
done | sort -u
```

Run: yukarıdaki blok.
Expected: tek satır `c7b5976c9513391909310883c40575c3`.

- [ ] **Step 6: Commit yok** (komut dosyaları repo-dışı — git commit edilmez; ilerleme `*.bak` + smoke ile izlenir). Task 6 final raporu durumu yazar.

---

## Task 4: Per-command call-site wiring (CODEX-CALL-PROTOCOL DIŞINDA)

**Files:**
- Modify: `~/.claude/commands/{spec,write-plan,execute-plan,simplify}-claude-codex.md`

> Her komutta: (i) komut başına bir kez `SCAN_WT_DIRS=(); trap ... EXIT`; (ii) her Codex call-site'ına "Call-site wiring şablonu" + komut-başına tablodaki `CALL_KIND`/`REQUIRED_CURRENT_FILES`/`RESOLVED_BASE` bağlaması + `--cwd "$SCAN_ROOT"` override prose'u. **CODEX-CALL-PROTOCOL bloğunun KENDİSİNE dokunma.**

- [ ] **Step 1: `spec-claude-codex` — Adım 2 (task-fresh) + Adım 6 (dirty→worktree / clean→base)**

Call-site'ları bul:

```bash
grep -nE 'cwd "\$PROJECT_ROOT"' ~/.claude/commands/spec-claude-codex.md
```

Bunlardan **CODEX-CALL-PROTOCOL bloğu içindekini** (canonical, satır referansı `c7b5976c` bloğu) ATLA; yalnız gerçek call-site adımlarına (Adım 2, Adım 6) override prose'u ekle. Adım 2: `CALL_KIND=task-fresh`, `REQUIRED_CURRENT_FILES="$SPEC_PATH"`, `RESOLVED_BASE=` (boş). Adım 6: dirty ise `CALL_KIND=worktree-review` + `REQUIRED_CURRENT_FILES="$SPEC_PATH"`; clean ise `CALL_KIND=base-review` + `RESOLVED_BASE=`(USER_BASE_REF veya auto-default snippet).

Run: `grep -c 'cwd "\$SCAN_ROOT"' ~/.claude/commands/spec-claude-codex.md`
Expected: `>= 2` (en az 2 call-site override edildi).

- [ ] **Step 2: `write-plan-claude-codex` — ön-analiz (task-fresh) + plan review (PLAN_PATH dirty→worktree / clean→base)**

ön-analiz: `CALL_KIND=task-fresh`, `REQUIRED_CURRENT_FILES="$SPEC_PATH"`. Plan review: `$PLAN_PATH` dirty→`worktree-review`+`REQUIRED_CURRENT_FILES="$PLAN_PATH"`; clean→`base-review`+`RESOLVED_BASE`.

Run: `grep -c 'cwd "\$SCAN_ROOT"' ~/.claude/commands/write-plan-claude-codex.md`
Expected: `>= 2`.

- [ ] **Step 3: `execute-plan-claude-codex` — Adım 6 (task-fresh) + Adım 8/11 (base-review --base BASE_REF)**

Adım 6: `CALL_KIND=task-fresh`, `REQUIRED_CURRENT_FILES="$PLAN_PATH"`. Adım 8/11: `CALL_KIND=base-review`, `RESOLVED_BASE="$BASE_REF"` (komutun zaten bildiği committed-range base; substrate aynı isimle kurar → companion `--base "$BASE_REF"` resolve eder).

Run: `grep -c 'cwd "\$SCAN_ROOT"' ~/.claude/commands/execute-plan-claude-codex.md`
Expected: `>= 2` (Adım 6 + Adım 8/11; 8 ve 11 ayrıysa 3).

- [ ] **Step 4: `simplify-claude-codex` — pre-scan (task-fresh) + final review (worktree-review)**

pre-scan: `CALL_KIND=task-fresh`, `REQUIRED_CURRENT_FILES=`(okunan güncel dosyalar). final review: `CALL_KIND=worktree-review`, `REQUIRED_CURRENT_FILES=`(okunan dosyalar).

Run: `grep -c 'cwd "\$SCAN_ROOT"' ~/.claude/commands/simplify-claude-codex.md`
Expected: `>= 2`.

- [ ] **Step 5: trap setup her komutta bir kez var mı**

```bash
for f in spec write-plan execute-plan simplify; do
  printf '%-28s ' "$f"; grep -cF 'SCAN_WT_DIRS=(); trap' ~/.claude/commands/$f-claude-codex.md
done
```

Run: yukarıdaki blok.
Expected: her satır `1` (trap setup bir kez — birden fazlaysa override hatası).

- [ ] **Step 6: CODEX-CALL-PROTOCOL hâlâ c7b5976c (wiring onu bozmadı)**

```bash
for f in spec write-plan execute-plan simplify; do
  awk '/<!-- CODEX-CALL-PROTOCOL:BEGIN/,/<!-- CODEX-CALL-PROTOCOL:END -->/' ~/.claude/commands/$f-claude-codex.md | md5sum
done | sort -u
```

Run: yukarıdaki blok.
Expected: tek satır `c7b5976c9513391909310883c40575c3`. **Değilse DUR** — call-site wiring marker bloğuna sızmış.

- [ ] **Step 7: S-1 invariant (DECISIVE) — protokol bloğu DIŞINDA `$PROJECT_ROOT --cwd` = 0**

Step 1-4'teki `grep -c 'cwd "$SCAN_ROOT"'` yalnız **pozitif sinyaldir** (yorumla da artar — Codex high#3). Asıl kapı: CODEX-CALL-PROTOCOL bloğu çıkarıldıktan sonra kalan metinde hiçbir gerçek call-site `$PROJECT_ROOT`'a route etmemeli.

```bash
for f in spec write-plan execute-plan simplify; do
  P=~/.claude/commands/$f-claude-codex.md
  # protokol bloğunu (BEGIN..END dahil) HARİÇ tut, kalan metinde 'cwd "$PROJECT_ROOT"' say:
  outside=$(awk '/<!-- CODEX-CALL-PROTOCOL:BEGIN/{skip=1} !skip; /<!-- CODEX-CALL-PROTOCOL:END -->/{skip=0}' "$P" | grep -cF 'cwd "$PROJECT_ROOT"')
  printf '%-28s outside-block PROJECT_ROOT --cwd: %s\n' "$f" "$outside"
done
```

Run: yukarıdaki blok.
Expected: her satır `0`. **Herhangi biri >0 → DUR** — gerçek bir Codex call-site hâlâ canlı repo'ya route ediyor (S-1 açık). O call-site'ı `--cwd "$SCAN_ROOT"`'a çevir. (Pozitif teyit: Step 1-4 `$SCAN_ROOT` sayıları call-site sayısıyla tutarlı.)

---

## Task 5: Check C drift-contract docs (4 dosyanın Sözleşme Notları) + smoke

**Files:**
- Modify: `~/.claude/commands/{spec,write-plan,execute-plan,simplify}-claude-codex.md`

- [ ] **Step 1: Her dosyanın Sözleşme/Drift bölümüne Check C (4-way) açıklaması ekle**

Her 4 dosyaya (marker DIŞI prose) şu içeriği ekle — **literal marker token KULLANMA** ("CODEX-SCAN-SUBSTRATE bloğu" diye refer et):

> **Check C (4-way, CODEX-SCAN-SUBSTRATE):** CODEX-SCAN-SUBSTRATE bloğu 4 komutta (spec/write-plan/execute-plan/simplify) **byte-identical**. Doğrulama: her dosyadan blok awk ile çıkarılır, **byte-for-byte `cmp`** (4-way) + tek md5 + tripwire token (`init -q`, `fetch -q --no-tags`, `core.logAllRefUpdates false`, `remote remove origin`, `.git/logs`, `apply --index`, `OVERLAY_WORKTREE`, `OVERLAY_REQUIRED_ONLY`, `_css_copy_safe`, `cp -P`, `_css_secret_scan`, `REQUIRED_CURRENT_FILES`, `SCAN_WT_DIRS`). Normalize diff / whitespace toleransı / "anlam aynı" KABUL EDİLMEZ. Bloğu değiştirirsen 4 komutu da senkronla. Davranış regression'ı: `docs/tools/codex-scan-substrate-harness.sh` (OP-4 T1-T6/T11/T12). CODEX-CALL-PROTOCOL (`c7b5976c`, 7-way) bundan AYRIDIR — dokunulmaz.

```bash
for f in spec write-plan execute-plan simplify; do
  printf '%-28s ' "$f"; grep -cF 'Check C (4-way' ~/.claude/commands/$f-claude-codex.md
done
```

Run: yukarıdaki blok.
Expected: her satır `1`.

- [ ] **Step 2: Marker hijyeni — literal token yalnız gerçek blokta**

```bash
for f in spec write-plan execute-plan simplify; do
  printf '%-28s ' "$f"; grep -cF 'CODEX-SCAN-SUBSTRATE:BEGIN' ~/.claude/commands/$f-claude-codex.md
done
```

Run: yukarıdaki blok.
Expected: her satır `1` (BEGIN marker yalnız gerçek blokta; prose'a sızmadı → awk extraction temiz).

- [ ] **Step 3: Load+parse smoke (tüm 4 dosya)**

```bash
for f in spec write-plan execute-plan simplify; do
  P=~/.claude/commands/$f-claude-codex.md
  python3 - "$P" <<'PY'
import sys,re
t=open(sys.argv[1]).read()
assert t.startswith('---'), 'frontmatter yok'
fm=t.split('---',2)[1]
assert 'description:' in fm, 'description yok'
assert t.count('# CODEX-SCAN-SUBSTRATE:BEGIN')==1 and t.count('# CODEX-SCAN-SUBSTRATE:END')==1, 'substrate marker tek değil'
assert '<!-- CODEX-CALL-PROTOCOL:BEGIN' in t, 'call-protocol yok'
print('OK', sys.argv[1].split('/')[-1])
PY
done
```

Run: yukarıdaki blok.
Expected: 4 satır `OK ...`. (Frontmatter parse + marker tekliği + her iki protokol mevcut.)

---

## Task 6: Final doğrulama suite + commit (docs + harness)

**Files:**
- Modify: `docs/plans/2026-06-02-claude-codex-cwd-secret-hardening.md` (gerekirse), `docs/tools/codex-scan-substrate-harness.sh` (zaten commit'li)
- Commit: docs + harness (komut dosyaları repo-DIŞI → commit EDİLMEZ)

- [ ] **Step 1: Tam doğrulama suite (Check A 7-way + Check C 4-way cmp + tripwire + harness + smoke)**

```bash
failed=0
echo "--- Check A (CODEX-CALL-PROTOCOL 7-way) ---"
a=$(for f in spec-claude-codex write-plan-claude-codex execute-plan-claude-codex simplify-claude-codex review-claude-codex security-review-claude-codex finish-branch-claude-codex; do
  awk '/<!-- CODEX-CALL-PROTOCOL:BEGIN/,/<!-- CODEX-CALL-PROTOCOL:END -->/' ~/.claude/commands/$f.md | md5sum; done | sort -u)
{ [ "$(printf '%s\n' "$a" | wc -l)" -eq 1 ] && printf '%s' "$a" | grep -q c7b5976c9513391909310883c40575c3; } && echo "Check A: PASS" || { echo "Check A: FAIL"; printf '%s\n' "$a"; failed=1; }
echo "--- Check C (CODEX-SCAN-SUBSTRATE 4-way cmp byte-for-byte) ---"
for f in spec write-plan execute-plan simplify; do
  awk '/# CODEX-SCAN-SUBSTRATE:BEGIN/,/# CODEX-SCAN-SUBSTRATE:END/' ~/.claude/commands/$f-claude-codex.md > /tmp/cc-$f.block; done
if cmp -s /tmp/cc-spec.block /tmp/cc-write-plan.block && cmp -s /tmp/cc-spec.block /tmp/cc-execute-plan.block && cmp -s /tmp/cc-spec.block /tmp/cc-simplify.block; then echo "Check C cmp: PASS"; else echo "Check C cmp: FAIL"; failed=1; fi
[ "$(md5sum /tmp/cc-*.block | awk '{print $1}' | sort -u | wc -l)" -eq 1 ] && echo "Check C md5: PASS" || { echo "Check C md5: FAIL"; failed=1; }
echo "--- S-1 invariant (outside-block PROJECT_ROOT --cwd = 0) ---"
for f in spec write-plan execute-plan simplify; do
  o=$(awk '/<!-- CODEX-CALL-PROTOCOL:BEGIN/{skip=1} !skip; /<!-- CODEX-CALL-PROTOCOL:END -->/{skip=0}' ~/.claude/commands/$f-claude-codex.md | grep -cF 'cwd "$PROJECT_ROOT"')
  [ "$o" -eq 0 ] || { echo "S-1 FAIL: $f outside-block=$o"; failed=1; }
done; [ "$failed" -eq 0 ] && echo "S-1 invariant: PASS"
echo "--- OP-4 harness (gömülü bloktan) ---"
if bash docs/tools/codex-scan-substrate-harness.sh >/tmp/cc-harness.log 2>&1; then echo "harness: PASS"; else echo "harness: FAIL"; tail -5 /tmp/cc-harness.log; failed=1; fi
[ "$failed" -eq 0 ] && echo "ALL VERIFY PASS" || { echo "VERIFY FAILED — commit DURDU"; exit 1; }
```

Run: yukarıdaki blok.
Expected: `Check A: PASS` · `Check C cmp: PASS` + `Check C md5: PASS` · `S-1 invariant: PASS` · `harness: PASS` · `ALL VERIFY PASS` (rc 0). **Herhangi biri FAIL → `failed=1` → `exit 1` (commit DURUR; `tail` artık exit code'u maskeleyemez — Codex med#5).**

- [ ] **Step 2: Repo staged set yalnız docs + harness (komut dosyası sızıntısı yok)**

```bash
git add docs/plans/2026-06-02-claude-codex-cwd-secret-hardening.md docs/tools/codex-scan-substrate-harness.sh docs/reviews/codex/2026-06-02-claude-codex-cwd-secret-hardening-plan.md 2>/dev/null
git diff --cached --name-only | sort
```

Run: yukarıdaki blok.
Expected: yalnız `docs/...` yolları. `~/.claude/commands/...` veya `.bak-*` GÖRÜNMEMELİ (repo-dışı; zaten git'te değil). Beklenmeyen dosya → `git restore --staged <f>`.

- [ ] **Step 3: Commit (docs + harness; push YOK)**

```bash
git commit -m "feat: harden claude-codex Codex --cwd via CODEX-SCAN-SUBSTRATE (S-1)"
```

Run: yukarıdaki blok.
Expected: commit oluştu. **Push YAPMA** (closure'a ait). Komut dosyası değişiklikleri repo-dışı; restart sonrası 4 komut substratlı çalışır (gerçek invoke restart ister).

- [ ] **Step 4: Final rapor**

Raporla: ✅ doğrulanan (Check A 7-way intact, Check C 4-way cmp byte-identical, tripwire 13×4, OP-4 harness T1-T12 PASS, smoke load+parse ×4) + ⏳ test-edilmeyen (gerçek Codex invoke davranışı — restart + canlı çağrı ister; companion app-server model çağrısı). Rollback: `~/.claude/commands/*.bak-<ts>`.

---

## Self-Review (writing-plans)

**1. Spec coverage:**
- Kapsam 4 komut (spec/write-plan/execute-plan/simplify) → Task 3/4 hepsini kapsıyor. ✓
- `CODEX-SCAN-SUBSTRATE` tek canonical blok → Task 2 (author) + Task 3 (4-way embed). ✓
- İki overlay modu (OVERLAY_WORKTREE / OVERLAY_REQUIRED_ONLY) → blok + T9/T11; call-site `CALL_KIND` tablosu. ✓
- Index-preserving overlay → T1; base-ref namespace → T12; sanitize (remote/reflog) → T7/T8. ✓
- Drift Contract: Check A 7-way intact (Task 1/3/4/6) + Check C 4-way **cmp byte-for-byte** (Task 3/6) + tripwire (Task 3/6). ✓
- OP-4 T1-T6/T11/T12 → Task 2 harness, re-runnable (Task 3 Step 4 + Task 6). ✓
- OP-5 `@execution-pin` (base-resolution/SHA-vs-ref/default-branch) → call-site RESOLVED_BASE snippet + blok namespace + T12. ✓
- Out-of-scope (3 izole komut, CODEX-CALL-PROTOCOL içeriği) → dokunulmuyor (Task 4/6 intact guard). ✓
- Committed-secret caveat → blok HEAD ancestry fetch'i; spec'te best-effort; bu repoda yok. (Plan ek aksiyon gerektirmez.) ✓

**2. Placeholder scan:** Canonical blok + harness + Check komutları tam kod; "TBD"/"implement here" yok. Call-site wiring komut-içi konum prose ("uygun bölüme") — komut dosyaları büyük + repo-dışı; exact satır verilmedi (grep ile bulunuyor), ama `CALL_KIND`/`REQUIRED_CURRENT_FILES`/`RESOLVED_BASE` değerleri tabloyla tam. ✓

**3. Type consistency:** `SCAN_ROOT`/`SCAN_WT_DIRS`/`REQUIRED_CURRENT_FILES`/`OVERLAY_WORKTREE`/`OVERLAY_REQUIRED_ONLY`/`BASE_REF`/`RESOLVED_BASE`/`CALL_KIND` isimleri blok + call-site + harness boyunca tutarlı. md5 `c7b5976c9513391909310883c40575c3` Task 1/3/4/6'da tutarlı. Marker `# CODEX-SCAN-SUBSTRATE:BEGIN/END` + `<!-- CODEX-CALL-PROTOCOL:BEGIN/END -->` tutarlı. ✓

**Bilinen sınır (Codex review'a açık):** Call-site wiring exact insertion noktaları prose; execute-plan Adım 8/11 base-review tek mi iki mi call-site (komut yapısına bağlı) — Task 4 Step 3 `>=2` ile esnek. Harness fixture'ları temsilî (M/D/R rename ayrımı T1'de kısmi).
