#!/usr/bin/env bash
# Drift checker for repo-external Claude command files.
#
# Scope: only $CLAUDE_CODEX_COMMAND_DIR/*-claude-codex.md command files.
# It intentionally does not police specs/plans; those are design/history
# artifacts and may contain older block snapshots.
#
# This catches byte drift and obvious S-1 regressions. It is not a replacement
# for the behavioral S-1 harness:
#   docs/tools/codex-scan-substrate-harness.sh
set -u

COMMAND_DIR="${CLAUDE_CODEX_COMMAND_DIR:-$HOME/.claude/commands}"
TMPDIR_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/claude-codex-drift.XXXXXX") || exit 2
trap 'rm -rf -- "$TMPDIR_ROOT"' EXIT

FAIL=0

PROTO_EXPECTED=(spec write-plan execute-plan simplify review security-review finish-branch)
SUBSTRATE_EXPECTED=(spec write-plan execute-plan simplify)

PROTO_BEGIN='<!-- CODEX-CALL-PROTOCOL:BEGIN'
PROTO_END='<!-- CODEX-CALL-PROTOCOL:END'
SUBSTRATE_BEGIN='# CODEX-SCAN-SUBSTRATE:BEGIN'
SUBSTRATE_END='# CODEX-SCAN-SUBSTRATE:END'

# Canonical Check B token set (decision Invariant #8 — keep in sync with the doc).
PROTO_TOKENS=(
  'codex-companion.mjs'
  'git rev-parse'
  'AGENTS.md'
  'timeout 480s'
  '124'
  'Claude-only devam et'
  'Tekrar dene'
  'Komutu durdur'
)

SUBSTRATE_TOKENS=(
  'init -q'
  'fetch -q --no-tags'
  'core.logAllRefUpdates false'
  'remote remove origin'
  '.git/logs'
  'apply --index'
  'OVERLAY_WORKTREE'
  'OVERLAY_REQUIRED_ONLY'
  '_css_copy_safe'
  'cp -P'
  '_css_secret_scan'
  'REQUIRED_CURRENT_FILES'
  'SCAN_WT_DIRS'
  'run_codex_scan'
  'css_resolve_base'
)

say() { printf '%s\n' "$*"; }
fail() { say "FAIL: $*"; FAIL=$((FAIL + 1)); }
ok() { say "ok: $*"; }

cmd_path() {
  printf '%s/%s-claude-codex.md' "$COMMAND_DIR" "$1"
}

contains_slug() {
  local needle="$1"; shift
  local x
  for x in "$@"; do
    [ "$x" = "$needle" ] && return 0
  done
  return 1
}

count_marker() {
  local file="$1" marker="$2"
  grep -cF -- "$marker" "$file" 2>/dev/null || true
}

extract_block() {
  local file="$1" begin="$2" end="$3" out="$4"
  awk -v begin="$begin" -v end="$end" '
    index($0, begin) { in_block=1 }
    in_block { print }
    index($0, end) { in_block=0 }
  ' "$file" > "$out"
}

check_expected_blocks() {
  local label="$1" begin="$2" end="$3" out_prefix="$4"; shift 4
  local expected=("$@")
  local first="" slug file out begin_count end_count

  say "--- $label expected files ---"
  for slug in "${expected[@]}"; do
    file=$(cmd_path "$slug")
    out="$TMPDIR_ROOT/$out_prefix-$slug.block"

    if [ ! -f "$file" ]; then
      fail "$label missing file: $file"
      continue
    fi

    begin_count=$(count_marker "$file" "$begin")
    end_count=$(count_marker "$file" "$end")
    if [ "$begin_count" -ne 1 ] || [ "$end_count" -ne 1 ]; then
      fail "$label marker count for $slug: begin=$begin_count end=$end_count"
      continue
    fi

    extract_block "$file" "$begin" "$end" "$out"
    if [ ! -s "$out" ]; then
      fail "$label empty extracted block: $slug"
      continue
    fi

    ok "$label block present: $slug"
    if [ -z "$first" ]; then
      first="$out"
    elif ! cmp -s "$first" "$out"; then
      fail "$label byte drift: $slug differs from ${expected[0]}"
    fi
  done

  if [ -n "$first" ]; then
    if command -v md5sum >/dev/null 2>&1; then
      say "$label md5 (report only): $(md5sum "$first" | awk '{print $1}')"
    else
      say "$label md5 (report only): md5sum not available"
    fi
  fi
}

check_unexpected_markers() {
  local label="$1" marker="$2"; shift 2
  local expected=("$@")
  local file base slug

  say "--- $label unexpected marker-bearing files ---"
  if [ ! -d "$COMMAND_DIR" ]; then
    fail "command dir missing: $COMMAND_DIR"
    return
  fi

  while IFS= read -r file; do
    [ -f "$file" ] || continue
    grep -qF -- "$marker" "$file" || continue
    base=${file##*/}
    slug=${base%-claude-codex.md}
    if ! contains_slug "$slug" "${expected[@]}"; then
      fail "$label unexpected marker in non-manifest file: $file"
    fi
  done < <(find "$COMMAND_DIR" -maxdepth 1 -type f -name '*-claude-codex.md' | sort)

  ok "$label unexpected marker scan complete"
}

check_tokens() {
  local label="$1" prefix="$2"; shift 2
  local tokens=("$@")
  local block token slug missing

  say "--- $label tripwire tokens ---"
  for block in "$TMPDIR_ROOT"/"$prefix"-*.block; do
    [ -f "$block" ] || continue
    slug=${block##*/}
    slug=${slug#"$prefix"-}
    slug=${slug%.block}
    missing=0
    for token in "${tokens[@]}"; do
      if ! grep -qF -- "$token" "$block"; then
        fail "$label missing token in $slug: $token"
        missing=1
      fi
    done
    [ "$missing" -eq 0 ] && ok "$label tokens present: $slug"
  done
}

check_s1_literal_regression() {
  local slug file hits directives

  say "--- S-1 literal regression signals ---"
  for slug in "${SUBSTRATE_EXPECTED[@]}"; do
    file=$(cmd_path "$slug")
    [ -f "$file" ] || { fail "S-1 missing file: $file"; continue; }

    hits=$(awk -v pbegin="$PROTO_BEGIN" -v pend="$PROTO_END" '
      index($0, pbegin) { in_proto=1; next }
      index($0, pend) { in_proto=0; next }
      !in_proto && /node "\$COMPANION"/ && /--cwd "\$PROJECT_ROOT"/ { count++ }
      END { print count + 0 }
    ' "$file")
    if [ "$hits" -ne 0 ]; then
      fail "S-1 literal live-repo invocation outside protocol in $slug: $hits"
    else
      ok "S-1 no literal live-repo node invocation outside protocol: $slug"
    fi

    directives=$(awk -v pbegin="$PROTO_BEGIN" -v pend="$PROTO_END" -v sbegin="$SUBSTRATE_BEGIN" -v send="$SUBSTRATE_END" '
      index($0, pbegin) { in_proto=1; next }
      index($0, pend) { in_proto=0; next }
      index($0, sbegin) { in_substrate=1; next }
      index($0, send) { in_substrate=0; next }
      !in_proto && !in_substrate && /run_codex_scan/ { count++ }
      END { print count + 0 }
    ' "$file")
    if [ "$directives" -lt 1 ]; then
      fail "S-1 positive signal missing outside canonical blocks: $slug has no run_codex_scan directive"
    else
      ok "S-1 run_codex_scan directive outside canonical blocks: $slug ($directives)"
    fi
  done
}

say "COMMAND_DIR=$COMMAND_DIR"

check_expected_blocks "Check A CODEX-CALL-PROTOCOL" "$PROTO_BEGIN" "$PROTO_END" "proto" "${PROTO_EXPECTED[@]}"
check_unexpected_markers "Check A CODEX-CALL-PROTOCOL" "$PROTO_BEGIN" "${PROTO_EXPECTED[@]}"
check_tokens "Check A CODEX-CALL-PROTOCOL" "proto" "${PROTO_TOKENS[@]}"

check_expected_blocks "Check C CODEX-SCAN-SUBSTRATE" "$SUBSTRATE_BEGIN" "$SUBSTRATE_END" "substrate" "${SUBSTRATE_EXPECTED[@]}"
check_unexpected_markers "Check C CODEX-SCAN-SUBSTRATE" "$SUBSTRATE_BEGIN" "${SUBSTRATE_EXPECTED[@]}"
check_tokens "Check C CODEX-SCAN-SUBSTRATE" "substrate" "${SUBSTRATE_TOKENS[@]}"

check_s1_literal_regression

if [ "$FAIL" -eq 0 ]; then
  say "PASS: claude-codex drift check clean"
  exit 0
fi

say "FAILURES=$FAIL"
exit 1
