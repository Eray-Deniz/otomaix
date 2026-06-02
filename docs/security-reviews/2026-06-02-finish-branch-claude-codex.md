# Security Review (dual): finish-branch-claude-codex komutu — 2026-06-02

coverage_mode: path-equivalent (repo-external whole-file audit; diff modu N/A — git diff görmez)
- Scope: `~/.claude/commands/finish-branch-claude-codex.md` (326→344 satır, review+security-fix'li) @ doğrudan dosya okuma
Reviewers: fresh Claude subagent (general-purpose) + Codex `task --fresh` (contained temp-dir cwd)
dual-review: true (claude_status: ran; codex_status: ran)
codex_breadth: best-effort (whole-file task --fresh)
coverage_gap: false (ham kod incelendi)
Scan substrate: contained temp-dir export (komut + canonical sibling + AGENTS.md); ~/.ssh ~/.aws erişilemez
Secret exclusion: none (gerçek secret değeri yok — yalnız secret-pattern dökümantasyon kelimeleri)
Threat model: CLI command spec — shell/command injection, secret handling, prompt-injection, destructive git ops. N/A: multi-tenant/auth/IDOR/rate-limit-cost (runtime servis değil).

## Both-agree / doğrulanmış (temiz)
- **Destructive git ops GÜVENLİ** [both-agree]: Claude subagent **ampirik test etti** (yanlış old-value → `update-ref -d` reddetti; remote diverge → `--force-with-lease` `! [rejected] (stale info)` ile reddetti, audit-edilmemiş iş korundu); Codex "conceptually safe" dedi. → review'da eklenen lease-bound silme doğrulandı.
- **Prompt-injection savunması** mevcut + yeterli (data-not-instructions + verbatim + user-approved + advisory blast-radius sınırı) [both-agree].
- **Hardcoded secret yok** [both-agree].
- **N/A:** multi-tenant/auth/IDOR/rate-limit — runtime servis değil [both-agree].

## Critical
_(yok)_

## High → DÜZELTİLDİ
- **S-1: Secret exposure to external model via `--cwd`** [single-source: codex] — **FIXED**
  mainline/detached modda `SCAN_ROOT=$PROJECT_ROOT` (canlı repo) idi → Codex `task --fresh --cwd` ile **untracked `.env`/secret dahil** her dosyaya read erişimi (harici model). Bu projede `backend/.env` var + mainline bu komutun en sık modu → gerçek leak. Codex yakaladı, Claude (prompt-preflight'a odaklı) kaçırdı — **dual-review değeri.**
  **Fix:** mainline/detached artık `git archive HEAD_SHA` ile **git'siz export** kullanıyor (`.git` yok → git-show geri-okuma yok; untracked dosya yok) + post-export symlink sweep. normal-mode worktree committed-only (untracked yok); committed-secret-via-`.git` best-effort olarak belgelendi (security-review diff-modu asimetrisiyle aynı).

## Medium → HEPSİ DÜZELTİLDİ
- **S-2: CUR/DEFAULT quoting/validation** [single-source: codex; uzlaştırıldı] — **FIXED**
  Codex "command-injection" dedi ama **abartı** (git refname kuralları space/glob yasaklar, değişken-genişletme metachar re-parse etmez — Claude haklı, ampirik doğruladı). Gerçek kalıntı: **flag-injection** (`-`-prefix ref) + defense-in-depth.
  **Fix:** Adım 1'de CUR/DEFAULT `git check-ref-format --branch` + leading-dash reddi; Adım 8'e ref-geçiş kuralı (tırnaklı + `--` separator: `git switch -- "$DEFAULT"`, `git push --force-with-lease="refs/heads/$CUR:$HEAD_SHA" origin ":refs/heads/$CUR"` vb.).
- **S-3: Prompt'a gömülen evidence diff secret taşıyabilir** [single-source: codex] — **FIXED**
  Audit, range-diff snapshot'ını Codex prompt'una gömüyordu; secret-preflight warning-based idi.
  **Fix:** Adım 5.3 evidence — secret-pattern eşleşen path'ler prompt'tan **hard-exclude**; yalnız `path|pattern|line-count` metadata, DEĞER harici modele gitmez.
- **S-4: `git worktree remove --force` dirty-check'siz** [single-source: codex] — **FIXED**
  Adım 4 "ekstra worktree temizle" pre-existing kullanıcı worktree'sinde uncommitted işi yok edebilirdi.
  **Fix:** force-remove öncesi `git -C <path> status --porcelain` dirty-check; uncommitted/untracked → DUR + onay.

## Low
_(yok)_

## Disposition Ledger
| id | source | raw sev | final sev | disposition | gerekçe |
|----|--------|---------|-----------|-------------|---------|
| S-1 secret-exposure --cwd | codex | high | **high** | kept + FIXED | mainline/detached PROJECT_ROOT untracked exposure teyit; git'siz export'a geçildi |
| S-2 ref quoting/validation | codex | high | **medium** | downgraded + FIXED | command-injection overstated (refname rules); flag-injection gerçek → check-ref-format + `--` |
| S-3 prompt-evidence secret | codex | medium | **medium** | kept + FIXED | injected diff hard-exclude eklendi |
| S-4 worktree force-remove | codex | medium | **medium** | kept + FIXED | dirty-check guard eklendi |
| destructive ops binding | both | clean | clean | kept | Claude ampirik + Codex conceptual [both-agree] |
| prompt-injection defense | both | clean | clean | kept | [both-agree] |
| hardcoded secrets | both | clean | clean | kept | pattern scan temiz [both-agree] |

## Sonuç
- Açık (devam): 0 — **4 bulgu (1 high + 3 medium) bu oturumda düzeltildi**
- Hakemler-arası ayrışma: Claude 0 bulgu (yıkıcı ops'ı ampirik doğruladı, secret-management'ı prompt-preflight çerçevesinde temiz gördü); Codex `--cwd` geniş yüzeyine bakıp S-1'i yakaladı → dual-review tam değer verdi.
- **Tüm fix'ler CODEX-CALL-PROTOCOL marker bloğu DIŞINDA** → drift contract re-verified `c7b5976c` (7/7).

## Deploy/Finish Gate
- security-risk: **clean** (0 critical/high açık — 1 high düzeltildi)
- dual-review: **complete** (her iki hakem çalıştı)
- coverage: best-effort (whole-file audit; ham kod incelendi, coverage_gap yok)

## Raw Claude Reviewer Output (appendix)
```
critical/high/medium/low: Sorun bulunmadı (4 aktif yüzey temiz).
Ampirik doğrulandı (git 2.43.0): update-ref -d old-value binding (yanlış → reddetti, doğru → atomik sildi);
--force-with-lease=ref:sha empty-refspec remote-delete (remote audited SHA → sildi; diverge → rejected stale info, korundu);
quoted-heredoc literal-tutma ($()/backtick/${} substitution ateşlenmedi); check-ref-format --branch + tırnaklı geçiş.
$SCOPE flag-injection: bu komutta STEP_B/$SCOPE kullanılmıyor → inert.
Secret-mgmt: prompt-preflight yeterli; hardcoded yok. Prompt-injection savunması mevcut. N/A: auth/multi-tenant/IDOR/rate-limit.
NOT: Claude --cwd geniş dosya-erişim yüzeyini (S-1) bulgu olarak işaretlemedi — Codex yakaladı.
```

## Codex raw review
docs/security-reviews/codex/2026-06-02-secreview-finish-branch-claude-codex-1.md
