# Codex Security Review — codex-review-scope-contract (attempt 1)

coverage_mode: diff | Range: 67351331..2af5875 | --base 67351331 | --cwd $SCAN_ROOT (pinned worktree) | overlay: claude-commands/ (context-only)

## Review Turn — 2026-06-04T20:36:18Z

[codex] Starting Codex task thread.
[codex] Thread ready (019e9459-e7f3-7343-a207-b75b22918429).
[codex] Turn started (019e9459-e987-7330-a368-42fb9de08eae).
[codex] Assistant message captured: {"verdict":"needs-attention","summary":"Repository context is not yet inspected; starting rea...
[codex] Running command: /bin/bash -lc "sed -n '1,120p' docs/active/CURRENT.md"
[codex] Command completed: /bin/bash -lc "sed -n '1,120p' docs/active/CURRENT.md" (exit 0)
[codex] Running command: /bin/bash -lc 'git status --short && git diff --stat 67351331dce85dacd747b5f52259f02554518129...
[codex] Running command: /bin/bash -lc "pwd && rg --files -g 'AGENTS.md' -g 'docs/active/CURRENT.md' -g 'docs/active/*...
[codex] Command completed: /bin/bash -lc "pwd && rg --files -g 'AGENTS.md' -g 'docs/active/CURRENT.md' -g 'docs/active/*... (exit 0)
[codex] Command completed: /bin/bash -lc 'git status --short && git diff --stat 67351331dce85dacd747b5f52259f02554518129... (exit 0)
[codex] Assistant message captured: {"verdict":"needs-attention","summary":"Active task matches the requested review. I’m reading...
[codex] Running command: /bin/bash -lc "sed -n '1,220p' docs/active/codex-review-scope-contract/TASK.md"
[codex] Command completed: /bin/bash -lc "sed -n '1,220p' docs/active/codex-review-scope-contract/TASK.md" (exit 0)
[codex] Running command: /bin/bash -lc "sed -n '1,220p' docs/active/codex-review-scope-contract/HANDOFF.md"
[codex] Command completed: /bin/bash -lc "sed -n '1,220p' docs/active/codex-review-scope-contract/HANDOFF.md" (exit 0)
[codex] Running command: /bin/bash -lc 'git diff --unified=80 67351331dce85dacd747b5f52259f02554518129..HEAD -- docs/t...
[codex] Command completed: /bin/bash -lc 'git diff --unified=80 67351331dce85dacd747b5f52259f02554518129..HEAD -- docs/t... (exit 0)
[codex] Running command: /bin/bash -lc "nl -ba docs/tools/claude-codex-drift-check.sh | sed -n '1,260p'"
[codex] Command completed: /bin/bash -lc "nl -ba docs/tools/claude-codex-drift-check.sh | sed -n '1,260p'" (exit 0)
[codex] Running command: /bin/bash -lc "nl -ba docs/tools/claude-codex-drift-check.sh | sed -n '260,520p'"
[codex] Command completed: /bin/bash -lc "nl -ba docs/tools/claude-codex-drift-check.sh | sed -n '260,520p'" (exit 0)
[codex] Running command: /bin/bash -lc 'git diff --unified=60 67351331dce85dacd747b5f52259f02554518129..HEAD -- docs/r...
[codex] Command completed: /bin/bash -lc 'git diff --unified=60 67351331dce85dacd747b5f52259f02554518129..HEAD -- docs/r... (exit 0)
[codex] Running command: /bin/bash -lc "for f in claude-commands/*-claude-codex.md; do printf '%s\\n' \""'$f"; rg -n '...
[codex] Command completed: /bin/bash -lc "for f in claude-commands/*-claude-codex.md; do printf '%s\\n' \""'$f"; rg -n '... (exit 0)
[codex] Assistant message captured: {"verdict":"needs-attention","summary":"The overlay contains a prior accepted concern about p...
[codex] Running command: /bin/bash -lc "nl -ba claude-commands/spec-claude-codex.md | sed -n '880,1045p'"
[codex] Running command: /bin/bash -lc "nl -ba claude-commands/execute-plan-claude-codex.md | sed -n '470,545p;685,745...
[codex] Running command: /bin/bash -lc "nl -ba claude-commands/security-review-claude-codex.md | sed -n '1,460p'"
[codex] Running command: /bin/bash -lc "nl -ba claude-commands/review-claude-codex.md | sed -n '1,420p'"
[codex] Command completed: /bin/bash -lc "nl -ba claude-commands/review-claude-codex.md | sed -n '1,420p'" (exit 0)
[codex] Command completed: /bin/bash -lc "nl -ba claude-commands/spec-claude-codex.md | sed -n '880,1045p'" (exit 0)
[codex] Command completed: /bin/bash -lc "nl -ba claude-commands/execute-plan-claude-codex.md | sed -n '470,545p;685,745... (exit 0)
[codex] Command completed: /bin/bash -lc "nl -ba claude-commands/security-review-claude-codex.md | sed -n '1,460p'" (exit 0)
[codex] Running command: /bin/bash -lc "nl -ba claude-commands/security-review-claude-codex.md | sed -n '460,760p'"
[codex] Command completed: /bin/bash -lc "nl -ba claude-commands/security-review-claude-codex.md | sed -n '460,760p'" (exit 0)
[codex] Running command: /bin/bash -lc "nl -ba claude-commands/finish-branch-claude-codex.md | sed -n '230,305p;520,62...
[codex] Command completed: /bin/bash -lc "nl -ba claude-commands/finish-branch-claude-codex.md | sed -n '230,305p;520,62... (exit 0)
[codex] Running command: /bin/bash -lc 'rg -n "external-overlay|claude-commands/|context-only overlay|realpath under|s...
[codex] Command completed: /bin/bash -lc 'rg -n "external-overlay|claude-commands/|context-only overlay|realpath under|s... (exit 0)
[codex] Running command: /bin/bash -lc 'TMPDIR=/dev/shm CLAUDE_CODEX_COMMAND_DIR=$PWD/claude-commands bash docs/tools/...
[codex] Command completed: /bin/bash -lc 'TMPDIR=/dev/shm CLAUDE_CODEX_COMMAND_DIR=$PWD/claude-commands bash docs/tools/... (exit 0)
[codex] Assistant message captured: {"verdict":"needs-attention","summary":"No-ship: I found high-risk false-green paths in the s...
[codex] Turn completed.
# Codex Adversarial Review

Target: branch diff against 67351331dce85dacd747b5f52259f02554518129
Verdict: needs-attention

No-ship: I found high-risk false-green paths in the slash-command tooling. Coverage: inspected git diff 67351331dce85dacd747b5f52259f02554518129..HEAD, docs/tools/claude-codex-drift-check.sh, active TASK/HANDOFF, review logs, and all ./claude-commands/*-claude-codex.md as context-only overlay. Requirement files inspected: active task docs and review logs; spec/plan were only referenced via included task/review context, not fully re-read. Not inspected: runtime ~/.claude copies/backups, because the review target provides ./claude-commands overlay. Fresh check run: TMPDIR=/dev/shm CLAUDE_CODEX_COMMAND_DIR=$PWD/claude-commands bash docs/tools/claude-codex-drift-check.sh -> PASS. Critical clean; high has findings; medium/low clean. Web auth/authz/XSS/CORS/CSRF/SSRF/rate-limit categories are N/A for this slash-command tooling review. F2/F3 execute-plan edits appear to close dirty-DUR and linked-spec issues without introducing new command injection or unsafe rm, but the surrounding substrate still has secret-exposure gaps.

Findings:
- [high] Tracked dirty files bypass the substrate secret scan before being sent to Codex (claude-commands/execute-plan-claude-codex.md:1228-1237)
  The sanitized substrate applies tracked staged and unstaged diffs directly into $WT, then only runs _css_secret_scan for untracked allowlist files. In worktree-review mode PATHSPEC is empty, so any tracked dirty file is applied; in task-fresh mode the required tracked file is applied. Because run_codex_scan later invokes the external model with --cwd "$SCAN_ROOT", a tracked .env/credential file, or a tracked required doc containing a key/token, can reach Codex without the claimed fail-closed scan. The preflight warning is prose-only and does not protect this embedded bash path.
  Recommendation: Root cause: secret scanning is only wired to untracked copies, not tracked diff overlay. Minimal fix: before companion invocation, enumerate tracked files affected by the staged/unstaged patches for the selected PATHSPEC, reject or metadata-only exclude known secret path patterns, and content-scan materialized tracked candidates after apply; fail closed on matches instead of calling node. Affected files/functions: CODEX-SCAN-SUBSTRATE build_scan_substrate/_css_secret_scan/run_codex_scan in spec/write-plan/execute-plan/simplify. Related files: docs/tools/codex-scan-substrate-harness.sh should gain a tracked-secret fixture. Verification: create a tracked file containing a sentinel matching api[_-]?key, dirty it, run task-fresh and worktree-review harness paths, and assert node is not invoked and the file is absent or metadata-only. Risk: naive scanning of every repo file may create false positives or leak values in logs. Fallback: hard-stop when tracked changed paths match secret filename patterns and require user redaction before Codex.
- [high] Check E treats external-overlay safety as token presence, not an executable guarded copy procedure (docs/tools/claude-codex-drift-check.sh:381-385)
  The new Check E verifies that binding prose contains words such as external-overlay, realpath, regular-file, secret-scan, and context-only, but it does not assert that any call path actually enumerates and copies ~/.claude/commands/*-claude-codex.md into the scan root with those guards. The overlay promise is security-relevant: it is supposed to keep command-policy reviews from omitting repo-external slash commands while also preventing symlink/path/secret exposure. As written, drift-check can pass green with no overlay procedure, or with an unsafe ad hoc overlay outside the checked surface.
  Recommendation: Root cause: Check E validates declarative binding text instead of the procedure that enforces it. Minimal fix: add a reusable overlay helper for command-policy reviews that enumerates exact command filenames, verifies each source is a regular non-symlink file with realpath under ~/.claude/commands, runs the same secret scan before copy, copies no-follow into the declared context-only destination, and fails closed if required overlay files cannot be built. Affected files/functions: docs/tools/claude-codex-drift-check.sh::check_review_scope_binding plus review/security-review/finish-branch overlay call sites and run_codex_scan users in spec/write-plan/execute-plan/simplify. Related files: all ./claude-commands/*-claude-codex.md bindings that claim external-overlay. Verification: add a harness with a sentinel command file present only in the external overlay and assert the scan root contains claude-commands/<file> before node; add negative cases for symlink escape and secret-pattern content. Risk: always overlaying commands could pollute non-command reviews. Fallback: require an explicit command-policy mode flag and fail closed unless the guarded overlay is constructed and reported in coverage.

Next steps:
- Block shipping until tracked-diff secret scanning is enforced in the substrate helper and covered by a harness fixture.
- Replace token-only external-overlay assertions with a real guarded overlay procedure or fail-closed command-policy mode.
- Rerun drift-check plus targeted substrate/overlay harnesses after the fixes.

CODEX_EXIT=0
