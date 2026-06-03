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

t2(){ echo "[T2] fail-closed: geçersiz BASE_REF fetch hatası";
  local FIX; FIX=$(mkfix)
  REQUIRED_CURRENT_FILES=""; OVERLAY_WORKTREE=""; OVERLAY_REQUIRED_ONLY=""; BASE_REF="nonexistent-ref-xyz"
  _build_in "$FIX"; local rc=$?
  [ "$rc" -ne 0 ] && _ok "T2 non-zero rc ($rc)" || _no "T2 rc=0 (fail-closed değil)"
  [ -z "$SCAN_ROOT" ] && _ok "T2 SCAN_ROOT boş" || _no "T2 SCAN_ROOT set ($SCAN_ROOT)"
}

t3(){ echo "[T3] stale guard";
  local FIX; FIX=$(mkfix)
  REQUIRED_CURRENT_FILES=""; OVERLAY_WORKTREE=""; OVERLAY_REQUIRED_ONLY=""; BASE_REF=""
  _build_in "$FIX"
  local first="$SCAN_ROOT"; [ -n "$first" ] && _ok "T3 ilk çağrı SCAN_ROOT set" || _no "T3 ilk çağrı boş"
  BASE_REF="bad-ref-2"
  _build_in "$FIX"
  [ -z "$SCAN_ROOT" ] && _ok "T3 fail sonrası SCAN_ROOT boş (stale yok)" || _no "T3 stale reuse: $SCAN_ROOT"
}

t4(){ echo "[T4] cleanup";
  local FIX; FIX=$(mkfix)
  REQUIRED_CURRENT_FILES=""; OVERLAY_WORKTREE=""; OVERLAY_REQUIRED_ONLY=""; BASE_REF=""
  _build_in "$FIX"
  local d="$SCAN_ROOT"; [ -d "$d" ] && _ok "T4 substrate var" || _no "T4 substrate yok"
  # call-site trap mantığını simüle et:
  for x in "${SCAN_WT_DIRS[@]:-}"; do [ -n "$x" ] && rm -rf -- "$x"; done; SCAN_WT_DIRS=()
  [ ! -d "$d" ] && _ok "T4 trap sonrası substrate silindi" || _no "T4 substrate kaldı: $d"
}

t5(){ echo "[T5] symlink exfil";
  local FIX; FIX=$(mkfix)
  ( cd "$FIX"; ln -s .env notes.txt )                          # untracked symlink → .env
  REQUIRED_CURRENT_FILES=$'notes.txt'; OVERLAY_WORKTREE=1; OVERLAY_REQUIRED_ONLY=""; BASE_REF=""
  _build_in "$FIX" || { _no "T5 build başarısız"; return; }
  # notes.txt ya kopyalanmadı ya da dangling symlink → topsecret içeriği substrate'ta OLMAMALI
  if grep -rqI topsecret "$SCAN_ROOT" 2>/dev/null; then _no "T5 secret sızdı"; else _ok "T5 secret yok"; fi
  [ ! -e "$SCAN_ROOT/.env" ] && _ok "T5 .env yok" || _no "T5 .env sızdı"
}

t6(){ echo "[T6] secret-content exclusion";
  local FIX; FIX=$(mkfix)
  printf 'api_key=abcd1234\n' > "$FIX/conf.txt"                # untracked, secret-içerik
  REQUIRED_CURRENT_FILES=$'conf.txt'; OVERLAY_WORKTREE=1; OVERLAY_REQUIRED_ONLY=""; BASE_REF=""
  _build_in "$FIX" || { _no "T6 build başarısız"; return; }
  [ ! -e "$SCAN_ROOT/conf.txt" ] && _ok "T6 secret dosya dışlandı" || _no "T6 secret dosya sızdı"
}

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

t_clean; t_dirty; t1; t2; t3; t4; t5; t6; t11; t12; t13; t_callsite
echo "PASS=$PASS FAIL=$FAIL"; [ "$FAIL" -eq 0 ] || exit 1
