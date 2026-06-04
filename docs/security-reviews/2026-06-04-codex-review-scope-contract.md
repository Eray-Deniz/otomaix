# Security Review (dual): codex-review-scope-contract — 2026-06-04

coverage_mode: diff
- Review aralığı: REVIEW_BASE_SHA..HEAD_SHA — BASE_REF=`6735133` / BASE_SHA=`6735133` / HEAD_SHA=`2af5875` / merge-base=`6735133`
Reviewers: fresh Claude subagent (general-purpose) + Codex adversarial-review
dual-review: true  (claude_status: ran; codex_status: ran)
codex_breadth: full-diff
coverage_gap: false (ham kod incelendi — drift-check.sh + komut overlay)
Scan substrate: pinned worktree @ HEAD_SHA (clean) + context-only overlay of 7 `~/.claude/commands/*-claude-codex.md`; untracked files: not reviewed
Secret exclusion: none
secret-exposure-risk-accepted: false
Main tree at review: clean

**Scope notu:** Kapsam = claude-codex slash-command TOOLING'i (Otomaix web app'leri DEĞİL). Asıl güvenlik yüzeyi: `docs/tools/claude-codex-drift-check.sh` (bash) + komut dosyalarındaki gömülü bash (Codex çağrı protokolü, run_codex_scan substrate, secret-scan, path-confinement, teardown). Web kategorileri (auth/authz/multi-tenant/XSS/CORS/CSRF/SSRF/rate-limit) = **N/A** (web kodu yok).

## Bu task'ın kendi değişiklikleri: GÜVENLİK-TEMİZ
İki hakem de hemfikir: **Check E + F2/F3 + CODEX-REVIEW-SCOPE-CONTRACT block → yeni injection / secret-leak / unsafe-op YOK.** Subagent ampirik doğruladı: USER_BASE_REF validation (`git rev-parse --verify`) `--output=`/`-h`/`;touch`/`$(touch)` payload'larını reddetti; CODEX-CALL-PROTOCOL heredoc literal (`<<'EOF'`) → `$PROMPT` tek-arg, breakout yok; Check E bash'i dosya içeriğini yalnız `grep`/`awk`/`printf '%s'`'e veri olarak alıyor (eval/format-string yok, rm yok). Codex: "F2/F3 ... yeni command injection veya unsafe rm getirmiyor."

## Critical
- Yok.

## High (Codex-rated) — ikisi de bu task'ın getirdiği değil
- **SF1 [single-source: codex] — tracked-dirty dosyalar substrate secret-scan'i bypass edip Codex'e gidebilir.** `CODEX-SCAN-SUBSTRATE` (`build_scan_substrate`, byte-locked 4-way): satır 1228-1231 tracked staged+unstaged diff'i (`git diff --cached/--binary` → `git apply --index`) $WT'ye uyguluyor; satır 1233-1238 `_css_secret_scan`'i **yalnız untracked REQUIRED** dosyalara koşuyor → tracked-dirty diff taranmadan `--cwd $SCAN_ROOT` ile Codex'e gidiyor. **Doğrulama: GERÇEK.** **Bağlam (severity'yi düşürür):** (a) committed tracked içerik zaten tasarımca Codex'e gidiyor (base fetch-clone = review hedefi); SF1 yalnız *tracked dosyaya eklenmiş uncommitted secret* marjinal sızıntısı; (b) S-1'in asıl tehdidi (untracked gitignore'lu `.env`) zaten kapalı; (c) **pre-existing — byte-locked 4-way S-1 bloğu, bu task değil** (codex-review-scope-contract substrate'e dokunmadı). Codex high; **bu review'da medium** (dar + pre-existing) olarak değerlendirildi. → **Spun-off S-1 substrate-hardening follow-up'a** tahsis edildi (CURRENT.md). Structured fix (Codex): companion çağrısından önce seçili PATHSPEC'in tracked değişen dosyalarını enumerate et, secret-pattern eşleşmesinde fail-closed (metadata-only exclude / hard-stop), materialized tracked candidate'ları apply sonrası content-scan; `codex-scan-substrate-harness.sh`'e tracked-secret fixture ekle.
- **SF2 [Codex high / Claude low — both-agree: tavan var] — Check E overlay'i token-presence ile doğruluyor, executable guarded-copy ile değil** (`drift-check.sh:381-385`). Check E binding bölgesinde guard *kelimelerini* (`external-overlay`/`realpath`/`regular-file`/`secret-scan`/`context-only`) grep'liyor ama gerçek bir copy prosedürünü assert etmiyor. = `/review` F1'in güvenlik çerçevesi. **Dökümante kabul tavan** (drift NOTE 418-430 + Task-7 kararı "Overlay hâlâ prose guidance, mekanize değil"). Subagent bağımsız **low** verdi (gerekçe: yeni exposure path DEĞİL — overlay LLM tarafından kurulduğunda zaten `_css_secret_scan`/realpath/no-follow guard'larını reuse etmesi talimatlı). → **accepted, low** (düzeltme yok); istenirse hardening SF1 follow-up'ıyla birlikte.

## Medium / Low
- Medium: yok (SF1 medium-değerlendirildi ama Codex-raw high korunur — ledger'da görünür).
- Low: SF2 (yukarıda, accepted ceiling).

## Excluded secret-bearing paths (metadata-only)
- Yok (kapsamda secret-taşıyan dosya yok; `.env.example` template'leri diff/overlay dışı).

## Disposition Ledger
| id | source | raw sev | final sev | disposition | gerekçe |
|----|--------|---------|-----------|-------------|---------|
| SF1 | codex | high | medium | kept → spun-off S-1 follow-up + security-risk override (this task) | tracked-dirty diff secret-scan'siz (1228-1238 doğrulandı); dar (committed içerik zaten in-scope; yalnız tracked-dosyada-uncommitted-secret); pre-existing byte-locked S-1 blok |
| SF2 | codex | high | low | downgraded (accepted ceiling) | overlay token-presence ≠ executable copy; dökümante (drift NOTE + Task-7 "mekanize değil"); yeni exposure path yok |
| Cl-overlay | claude | low | low | merged-into SF2 | subagent aynı overlay-ceiling'i bağımsız low verdi (both-agree: tavan var) |

## Sonuç
- Kapatılan (accepted): **SF2** (dökümante tavan)
- Spun-off follow-up: **SF1** (S-1 substrate-hardening — CURRENT.md proposed)
- Bu task'ın değişiklikleri: **güvenlik-temiz** (iki hakem hemfikir, ampirik doğrulandı)
- Hakemler-arası çelişki: **yok** — SF2'de severity ayrışması (Codex high / Claude low), bulgunun varlığında both-agree; SF1 single-source codex (subagent substrate'in untracked/export eksenine baktı, tracked-dirty eksenine değil — tamamlayıcı, çelişki değil)

## Deploy/Finish Gate
- **security-risk: BLOCKED (2 Codex-rated high: SF1, SF2)** → **override: accepted by user** — gerekçe: high'ların ikisi de bu task'ın regression'ı DEĞİL; SF1 pre-existing S-1 substrate (byte-locked blok) → spun-off follow-up; SF2 dökümante kabul tavan. Bu task'ın kendi yüzeyi temiz.
- **dual-review: complete** (override gerekmez)
- **coverage: full-diff** (diff mode, her iki hakem ran)

## Raw Claude Reviewer Output (appendix)
> Bağımsız güvenlik reviewer (general-purpose). 4 kategori (embedded-bash injection / external-model secret-leak / unsafe file-ops / path-traversal) + ampirik doğrulama (drift-check koştu PASS; USER_BASE_REF'e flag+command injection payload'ları REJECTED; co-location awk boundary doğru; format-string `%n/%s` testi → eval yok).
>
> **(1) Embedded-bash injection:** Sorun bulunmadı. F2 DUR'u pre-existing USER_BASE_REF validation'dan SONRA; heredoc quoted → `$PROMPT` literal tek-arg; Check E user-input'u shell'e sokmuyor (marker/slug hardcoded REVIEW_SCOPE_SITES'tan; dosya içeriği yalnız grep/awk/printf'e veri).
> **(2) External-model secret-leak:** Sorun bulunmadı (new code); **1 low/accepted-ceiling** — command-policy external-overlay LLM'e prose direktif, standalone executable bash değil; Check E guard *kelimelerini* grep'liyor, gerçek copy prosedürünü değil. Yeni exposure path DEĞİL (overlay kurulduğunda `_css_secret_scan`/realpath/no-follow reuse talimatlı). Dökümante tavan (drift NOTE 418-430).
> **(3) Unsafe file-ops:** Sorun bulunmadı. Check E'de rm/computed-path-delete YOK; tek rm = pre-existing mktemp-guard'lı `trap rm -rf -- "$TMPDIR_ROOT" EXIT` (mktemp -d sonucu, asla boş/türetilmiş); eval/source/exec yok.
> **(4) Path-traversal/confinement:** Sorun bulunmadı. Confinement (realpath-under-SCAN_ROOT sweep, allowlist+regular-file) byte-locked substrate/export bloğunda, değişmemiş; Check E `find ... -name '*-claude-codex.md'` quoted; `$COMMAND_DIR` operator-controlled config.
> **Web kategorileri:** N/A (web kodu yok).
> **Özet:** C/H/M güvenlik bulgusu yok; 1 low/accepted-ceiling (overlay token-presence).

## Codex raw review
`docs/security-reviews/codex/2026-06-04-secreview-codex-review-scope-contract-1.md`
