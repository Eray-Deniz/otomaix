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
AUTO_FIX_EXPECTED=(spec write-plan execute-plan simplify)
REVIEWER_EXPECTED=(review security-review)

REVIEW_SCOPE_EXPECTED=(spec write-plan execute-plan simplify review security-review finish-branch)
REVIEW_SCOPE_BEGIN='<!-- CODEX-REVIEW-SCOPE-CONTRACT:BEGIN'
REVIEW_SCOPE_END='<!-- CODEX-REVIEW-SCOPE-CONTRACT:END'
REVIEW_SCOPE_TOKENS=(
  'Pinned target'
  'Requirement sources'
  'Dependency scope'
  'Command-policy external-files'
  'Coverage statement'
  'fix recommendation'
  'context-only overlay'
)

PROTO_BEGIN='<!-- CODEX-CALL-PROTOCOL:BEGIN'
PROTO_END='<!-- CODEX-CALL-PROTOCOL:END'
SUBSTRATE_BEGIN='# CODEX-SCAN-SUBSTRATE:BEGIN'
SUBSTRATE_END='# CODEX-SCAN-SUBSTRATE:END'
AUTOFIX_BEGIN='<!-- AUTO-FIX-REVIEW-POLICY:BEGIN'
AUTOFIX_END='<!-- AUTO-FIX-REVIEW-POLICY:END'

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
          # Trigger YALNIZ "hard-block" (gate terimi). "chain-advance bloke etmez" gibi disclaimer
          # ifadeleri tetiklemez (F7 false-positive onler). Yazim kurali: hard-block satiri yalniz
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

check_expected_blocks "Check D AUTO-FIX-REVIEW-POLICY" "$AUTOFIX_BEGIN" "$AUTOFIX_END" "autofix" "${AUTO_FIX_EXPECTED[@]}"
check_unexpected_markers "Check D AUTO-FIX-REVIEW-POLICY" "$AUTOFIX_BEGIN" "${AUTO_FIX_EXPECTED[@]}"
check_tokens "Check D AUTO-FIX-REVIEW-POLICY" "autofix" "${AUTOFIX_TOKENS[@]}"
check_reviewer_tokens "Check D reviewer" "${REVIEWER_TOKENS[@]}"
check_reviewer_forbidden "Check D reviewer"

check_s1_literal_regression

check_expected_blocks "Check E CODEX-REVIEW-SCOPE-CONTRACT" "$REVIEW_SCOPE_BEGIN" "$REVIEW_SCOPE_END" "revscope" "${REVIEW_SCOPE_EXPECTED[@]}"
check_unexpected_markers "Check E CODEX-REVIEW-SCOPE-CONTRACT" "$REVIEW_SCOPE_BEGIN" "${REVIEW_SCOPE_EXPECTED[@]}"
check_tokens "Check E CODEX-REVIEW-SCOPE-CONTRACT" "revscope" "${REVIEW_SCOPE_TOKENS[@]}"

if [ "$FAIL" -eq 0 ]; then
  say "PASS: claude-codex drift check clean"
  exit 0
fi

say "FAILURES=$FAIL"
exit 1
