# Codex Security Review Log — security-review-claude-codex (finish-branch-claude-codex deliverable)

Target: ~/.claude/commands/finish-branch-claude-codex.md (repo-external command spec, 326 lines, review-fixed)
coverage_mode: path-equivalent (repo-external whole-file audit) — Codex via `task --fresh --cwd <contained-tmp>` (diff mode N/A; security-review own precedent)
Threat model (adapted to a CLI command spec): shell/command injection, secret handling, prompt-injection hardening, destructive git ops. N/A: multi-tenant/auth/IDOR/rate-limit-cost (not a runtime service).

## Review Turn — 2026-06-02 (task --fresh, exit 0, contained temp-dir cwd)

```
[codex] Starting Codex task thread.
[codex] Thread ready (019e88e9-0547-7663-93dd-c8fc94d559ad).
[codex] Turn started (019e88e9-0697-7f80-b9d0-bf5074a43176).
[codex] Assistant message captured: Bu incelemeyi salt-okunur yapacağım. Önce hedef spec ve canonical protokol dosyasını satır nu...
[codex] Running command: /bin/bash -lc 'pwd && rg --files'
[codex] Command completed: /bin/bash -lc 'pwd && rg --files' (exit 0)
[codex] Running command: /bin/bash -lc 'nl -ba finish-branch-claude-codex.md'
[codex] Command completed: /bin/bash -lc 'nl -ba finish-branch-claude-codex.md' (exit 0)
[codex] Running command: /bin/bash -lc 'nl -ba AGENTS.md'
[codex] Command completed: /bin/bash -lc 'nl -ba AGENTS.md' (exit 0)
[codex] Running command: /bin/bash -lc 'nl -ba spec-claude-codex-CANONICAL.md'
[codex] Command completed: /bin/bash -lc 'nl -ba spec-claude-codex-CANONICAL.md' (exit 0)
[codex] Assistant message captured: Hedef spec’in ana akışını ve canonical CODEX-CALL-PROTOCOL kopyasını okudum. Şimdi özellikle ...
[codex] Running command: /bin/bash -lc 'rg -n "(api[_-]?key|secret|token|password|BEGIN .*PRIVATE|AKIA|sk-|ghp_|github...
[codex] Command completed: /bin/bash -lc 'rg -n "(api[_-]?key|secret|token|password|BEGIN .*PRIVATE|AKIA|sk-|ghp_|github... (exit 0)
[codex] Running command: /bin/bash -lc 'rg -n "git (checkout|switch|push|branch|update-ref|merge|worktree|ls-files|dif...
[codex] Command completed: /bin/bash -lc 'rg -n "git (checkout|switch|push|branch|update-ref|merge|worktree|ls-files|dif... (exit 0)
[codex] Assistant message captured: **Findings** **High — Secret exposure to external model via `--cwd` is not closed** [file](/t...
[codex] Turn completed.
**Findings**

**High — Secret exposure to external model via `--cwd` is not closed**  
[file](/tmp/fbcc-secrev-input/finish-branch-claude-codex.md:104), [file](/tmp/fbcc-secrev-input/finish-branch-claude-codex.md:109), [file](/tmp/fbcc-secrev-input/finish-branch-claude-codex.md:222)  
The spec says secret files should not be added to the prompt, but also acknowledges Codex gets repo read access via `--cwd`. In finish-branch, `--cwd "$SCAN_ROOT"` points either to a pinned git worktree or the live project root. That means tracked secrets, missed secret patterns, and tracked symlinks that point outside the repo can still be read by the external model even if the prompt excludes them. The current control is warning/suggestion based, not containment.

Concrete fix: run Codex only in a contained, git-free, sanitized export directory. Build it from the pinned SHA, remove `.git`, reject or delete all symlinks, and hard-abort or require explicit user opt-in if tracked/changed paths match secret patterns. Then call `task --fresh --cwd "$SANITIZED_SCAN_ROOT"`. Do not pass the live repo or git worktree as Codex cwd.

**High — Unquoted/unvalidated branch and default refs in destructive/outward shell commands allow command/argument injection**  
[file](/tmp/fbcc-secrev-input/finish-branch-claude-codex.md:163), [file](/tmp/fbcc-secrev-input/finish-branch-claude-codex.md:164), [file](/tmp/fbcc-secrev-input/finish-branch-claude-codex.md:262), [file](/tmp/fbcc-secrev-input/finish-branch-claude-codex.md:264), [file](/tmp/fbcc-secrev-input/finish-branch-claude-codex.md:269)  
`CUR` and `DEFAULT` are repo-derived, but the spec later shows commands such as `git checkout <default>`, `git push origin ${HEAD_SHA}:refs/heads/<branch>`, `git branch -d <branch>`, `git update-ref -d refs/heads/<branch> $HEAD_SHA`, and the `--force-with-lease=refs/heads/<branch>:$HEAD_SHA` delete lease without mandatory quoting/validation. Git refnames can contain shell-significant characters, so a malicious local branch/default ref name can become shell injection if implemented literally from the spec.

Concrete fix: after deriving `CUR` and `DEFAULT`, validate both with `git check-ref-format --branch "$name"` and reject names starting with `-` or differing from their normalized form. Use quoted variables everywhere and `--` where the command supports it, e.g. `git switch -- "$DEFAULT"`, `git branch -d -- "$CUR"`, `git push origin "$HEAD_SHA:refs/heads/$CUR"`, `git update-ref -d "refs/heads/$CUR" "$HEAD_SHA"`, and `git push --force-with-lease="refs/heads/$CUR:$HEAD_SHA" origin ":refs/heads/$CUR"`.

**Medium — Secret preflight is warning-based and pattern-incomplete for prompt evidence**  
[file](/tmp/fbcc-secrev-input/finish-branch-claude-codex.md:104), [file](/tmp/fbcc-secrev-input/finish-branch-claude-codex.md:216), [file](/tmp/fbcc-secrev-input/finish-branch-claude-codex.md:222)  
The exact range diff snapshot is embedded into the prompt, but the secret preflight says “warn once + suggest excluding.” For an external model call, warning-only is insufficient if the diff includes `.env`, private keys, service account material, cloud configs, tokens, or other missed secret-like paths. The listed patterns are explicitly examples, so this remains an evidence gap and a practical leak path.

Concrete fix: make secret detection a hard preflight gate for prompt evidence. If changed/read paths match secret patterns or entropy/token scanners, omit those files from evidence and show only path-level metadata, or stop unless the user explicitly chooses `--no-audit`/redacted audit. Never include secret-file diffs in `PROMPT`.

**Medium — Forced worktree removal can destroy unaudited local work**  
[file](/tmp/fbcc-secrev-input/finish-branch-claude-codex.md:187), [file](/tmp/fbcc-secrev-input/finish-branch-claude-codex.md:262), [file](/tmp/fbcc-secrev-input/finish-branch-claude-codex.md:269)  
The spec says to clean extra worktrees and later uses `git worktree remove --force <path>`. It does not require checking each worktree for uncommitted or untracked work before forced removal. That can delete unaudited local changes unrelated to the pinned `HEAD_SHA`.

Concrete fix: before any `worktree remove --force`, run `git -C "$WT_PATH" status --porcelain=v1 --untracked-files=all`. If non-empty, stop and show the path list; require the user to clean/stash/commit or type a stronger explicit confirmation naming the worktree path.

**Clean / acceptable**

Command injection: the quoted heredoc pattern is correct. `PROMPT=$(cat <<'CODEX_PROMPT_EOF' ...)` prevents `$()`, backtick, `${...}`, and variable expansion inside prompt content, and `"$PROMPT"` is passed as a single argument.

`$SCOPE`: clean for this command because finish-branch binds only `<STEP_A> = task --fresh`; the canonical unquoted `$SCOPE` path is declared unused here.

Prompt injection: defense is present. The spec marks embedded file/diff content as data, not instructions, requires Codex output to be shown verbatim, and keeps commit/approve/destructive actions user-approved.

Destructive git binding: pinned `HEAD_SHA`, pre/post HEAD guards, local `update-ref -d ... $HEAD_SHA`, and remote delete `--force-with-lease=refs/heads/<branch>:$HEAD_SHA` are conceptually safe against deleting a ref that moved after audit, assuming the quoting/ref-validation fix above is applied.

Hardcoded secrets: none found by pattern scan.

N/A — not a runtime service: multi-tenant isolation, auth, authz, IDOR, rate limiting, and cost controls.
```
