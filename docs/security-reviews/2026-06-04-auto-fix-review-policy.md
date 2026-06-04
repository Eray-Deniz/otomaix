# Security Review (dual): auto-fix-review-policy — 2026-06-04

coverage_mode: diff
- Scope: substrate baseline..head (task delta: 7 komut + drift-check.sh Check D + review-cycle guard fix'leri)
- Substrate: geçici git repo (baseline = pre-task `*.bak-20260604T065456Z` + `00acbfa:drift-check.sh`; head = current-with-fixes). coverage_mode=diff.
Reviewers: fresh Claude subagent (general-purpose) + Codex adversarial-review
dual-review: true (claude_status: ran; codex_status: ran)
codex_breadth: full-diff
coverage_gap: false
Scan substrate: pinned git substrate @ head; untracked files: not reviewed
Secret exclusion: none (substrate sadece .md + .sh — secret-bearing dosya yok)
secret-exposure-risk-accepted: false

## Güvenlik yüzeyi (önemli kapsam notu)
Deliverable çoğunlukla markdown (LLM'in okuduğu slash-command prose). Saldırı yüzeyi: (1) komut dosyalarındaki gömülü bash, (2) drift-check.sh awk/bash, (3) auto-fix otonomi carve-out tasarımı. **Güvenlik-kritik gömülü bash (CODEX-CALL-PROTOCOL, secret preflight, path-confinement, teardown) bu task'ın delta'sında DEĞİŞMEDİ** — Codex ve subagent bağımsız doğruladı. Bu task'ın YENİ kodu: drift-check.sh Check D + prose procedure değişiklikleri.

## Critical
Yok.

## High
- **SR-1 [single-source: codex; PRE-EXISTING, bu task'ın delta'sı DEĞİL] — `rm -rf "$(dirname "$EXPORT_DIR")"` guard'sız mktemp ile `rm -rf /` riski** (`security-review-claude-codex.md:280` + teardown `:305`/`:603`). `EXPORT_DIR="$(mktemp -d)/secreview-export"` — `mktemp` boş dönerse `EXPORT_DIR=/secreview-export`, `dirname`=`/`, teardown `rm -rf /`. GNU rm `--preserve-root` ile reddeder ama agent-yürütülen destructive path implementation-specific korumaya güvenmemeli. **Severity tahkimi:** Codex high; ben **medium-high** (gerçek destructive-op gap AMA düşük olasılık: mktemp-fail + non-GNU-rm gerekir). **Blast-radius:** yalnız security-review'ın EXPORT teardown'ı gerçek tehlikeli; review/security worktree (`git worktree remove` safe-fail), finish-branch (`rm -rf "$EXPORT"` direct, boş→zararsız), css helper'ları (`|| return 1` guard'lı) güvenli. **Pre-existing:** security-review komutunun oluşturulduğu önceki task'tan; auto-fix-review-policy dokunmadı.

## Medium
- **SR-2 [both-agree: codex + claude] — Check D `check_reviewer_forbidden` wrapped-prose bypass** (`drift-check.sh:~240-279`). Negatif kapı `hard-block` + sonraki wrapped prose'daki medium'u yakalamıyor. **Bu dokümante + kullanıcı-kabul F9 residual** (yeni değil; kod-içi yorum + memory `semantic_negative_not_regexable`). Codex önerisi (yapısal exact-match key) doğru yön ama bilinçli reddedildi (tripwire kabul). Güvenlik açığı değil — kapsam sınırı.

## Low
- **SR-3 [single-source: claude] — `COMMAND_DIR` env-türevli** (`drift-check.sh:13`). `CLAUDE_CODEX_COMMAND_DIR` taramayı yönlendirir ama tüm kullanımlar quoted + `-F`/`--`; içerik yalnız veri; eval/exec yok. Sömürülemez (saldırgan-kontrollü env zaten daha geniş tehdit). Not amaçlı.

## Disposition Ledger
| id | source | raw sev | final sev | disposition | gerekçe |
|----|--------|---------|-----------|-------------|---------|
| SR-1 | codex | high | medium-high | kept (pre-existing, out-of-delta) | mktemp guard'sız + dirname→/ ; blast-radius yalnız security-review EXPORT |
| SR-2 | codex+claude | medium | medium | kept (documented F9, accepted) | both-agree; bilinçli tripwire residual |
| SR-3 | claude | low | low | kept | env note, sömürülemez |

## Sonuç
- both-agree: 1 (SR-2)
- single-source: SR-1 (codex), SR-3 (claude)
- Kapatılan (push-back): 0
- Açık: SR-1 (pre-existing, kullanıcı kararı), SR-2 (kabul), SR-3 (not)
- Hakemler-arası çelişki: SR-1 kapsam — subagent "delta-dışı, kapsam dışı" dedi; Codex tam dosyayı okuyup yakaladı. Sentezci: gerçek ama pre-existing → kullanıcıya görünür.

## Deploy/Finish Gate
- **security-risk (auto-fix-review-policy DELTA):** clean — bu task'ın değişiklikleri yeni critical/high/medium getirmiyor. Otonomi carve-out tüm tehlikeli ops'ları (push/merge/state/vault/override) insan kapısı + sert tavanlar (6-tavan/cap=10/2.-reopen) arkasında tutuyor; otonom commit→push tırmanması kapalı (push Adım 14 full-tests+review+approval AND'ine bağlı, değişmedi). drift-check awk veri-only (system() yok, dinamik regex yok).
- **PRE-EXISTING bulgu (SR-1):** security-review komutunun kendi teardown'ında destructive-op gap. Delta-dışı; kullanıcı kararı: şimdi hardening (küçük, deterministik) veya ayrı task.
- dual-review: complete
- coverage: full-diff

## Raw Claude Reviewer Output (appendix)
critical/high/medium: Sorun bulunmadı. low: COMMAND_DIR env note. Kapsam: güvenlik-kritik gömülü bash bu diff'te değişmedi; drift-check güvenli (eval yok, `--`/`-F` guard'lı, `set -u`, mktemp `|| exit 2` + trap); otonomi carve-out tehlikeli ops'ları insan kapısı arkasında tutuyor (byte-identical carve-out bloğu push/merge/discard/branch-silme/vault/active-layer/override sayıyor); 6-tavan+cap=10 backstop. Doğrulama: `bash -n` OK, drift-check PASS, awk bypass dokümante davranışla uyumlu. shellcheck yok (tek doğrulama boşluğu).

## Codex raw review
docs/security-reviews/codex/2026-06-04-secreview-auto-fix-review-policy-1.md

---

## SR-1 Fix Applied (kullanıcı kararı: şimdi hardening) — RESOLVED

Kullanıcı "şimdi hardening" seçti. mktemp/`rm -rf` destructive-op gap'i kapatıldı (security-review + review, blast-radius):
- `security-review:273/280` worktree+export: `X="$(mktemp -d)/..."` → `X_PARENT=$(mktemp -d "${TMPDIR:-/tmp}/...XXXXXX") || { echo "mktemp failed"; exit 1; }` + explicit `X="$X_PARENT/..."`.
- teardown `rm -rf "$(dirname "$EXPORT_DIR")"` → `rm -rf -- "$EXPORT_PARENT"` (explicit parent, **`dirname` YOK** → mktemp boş/başarısız olsa bile `rm -rf /` yapısal olarak imkansız; ayrıca `|| exit 1` zaten teardown'a ulaşmadan durur).
- `review:210` worktree aynı guard (teardown `git worktree remove` zaten safe-fail'di ama tutarlılık + parent temizliği eklendi).
- Pattern, dosyalardaki mevcut `_css_secret_scan` helper guard'ıyla (`mktemp -d ... || return 1`) tutarlı.

**Doğrulama:** drift-check **PASS** (edit'ler marker-blok DIŞI); `bash -n` syntax OK; fonksiyonel test (`rm -rf -- "$EXPORT_PARENT"` explicit parent → `/` dokunulmuyor); **Codex re-review: SR-1 RESOLVED, verdict approve, no material findings**. Pre-fix yedek: `*.bak-20260604T095430Z`.

## Final Deploy/Finish Gate (güncel)
- security-risk: **clean** (task delta temiz + SR-1 hardening uygulandı). dual-review: complete. coverage: full-diff.
- SR-2 (F9 drift gate residual): dokümante/kabul. SR-3 (COMMAND_DIR env): not, sömürülemez.
- **→ `/finish-branch-claude-codex` (closure) için engel yok.**
