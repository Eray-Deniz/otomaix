# Handoff

## Context
- Task: Auto-Fix Review Policy — claude-codex aile geneli
- Linked spec: docs/specs/2026-06-03-auto-fix-review-policy.md
- Linked plan: docs/plans/2026-06-03-auto-fix-review-policy.md
- Branch: main
- Last updated: 2026-06-04

## Current State
- Summary: Execution tamamlandı + **`/review-claude-codex` çalıştı (çift hakem)**. Review **sistemik bulgu** verdi: AUTO-FIX politikası prose'da vardı ama prosedüre bağlanmamıştı. Kullanıcı "düzelt" dedi → 6 komut dosyasının prosedürleri (guard'lar/Mode A/Manuel-mod notları/reviewer Adım 8/chain-advance gate+matris+cross-ref) düzeltildi → **5 Codex re-review turunda yakınsadı → approve/clean**. drift-check A/B/C/D PASS. status `waiting-review`.
- Blocked: hayır

## Resume From
- Start here: **`/finish-branch-claude-codex` (closure)** — review + security chain temiz, engel yok
- Relevant files: ~/.claude/commands/{spec,write-plan,execute-plan,simplify,review,security-review,finish-branch}-claude-codex.md (repo-DIŞı, review-fix ile yeniden düzenlendi); docs/tools/claude-codex-drift-check.sh (repo-İÇİ, Check D commit'li)
- Next command: /security-review-claude-codex
- Review raporu: docs/reviews/2026-06-04-auto-fix-review-policy.md
- Codex re-review log (R1-R5): docs/reviews/codex/2026-06-04-review-auto-fix-review-policy-1.md
- Codex execute log (önceki): docs/reviews/codex/2026-06-04-auto-fix-review-policy-execute.md

## Verification
- full_test_suite (drift-check A 7-way + B + C 4-way + D 4-way + S-1): **PASS** (EXIT=0); Check A md5 c7b5976c, Check C md5 0174e562, Check D block md5 9a3ebf71 (4-way byte-identical)
- pre_execution_codex_review: **ran** (env drift yok)
- checkpoint_codex_reviews: **ran 2/2** (Standard); CP1 clean; CP2 2 high (medium pass-through) → tur-4+ Codex çözüm önerisi → option b thread → **4 turda converged** (6-tavan altında, override YOK)
- final_codex_execution_review: **approved** (implementation temiz; 2 active-layer finding [HANDOFF stale + TASK overlay] bu Adım 15 update'iyle kapandı)
- final_unresolved_high_severity_override: false
- unresolved_critical_high: **none**
- markdown smoke: 6 dosya frontmatter_delims=2 + even code fences
- fixture regression (re-runnable): positive PASS + negative-1 (marker break) FAIL/EXIT=1 + negative-2 (F7 bypass) caught
- scenario trace: 9/9 tutarlı
- **review_cycle (2026-06-04 `/review-claude-codex`):** çift hakem (Codex + fresh Claude subagent). Sistemik prose-declared-not-wired gap (Codex high; subagent kaçırdı). Kullanıcı "düzelt" → 6 komut prosedürü hizalandı → **Codex re-review R1-R5: R5 verdict approve/clean**; her fix sonrası drift-check PASS; deterministik exhaustive süpürme temiz ("serbest"/"otomatik döngü değil"/"kullanıcı seçer"). AUTO-FIX bloğu byte-identical (md5 9a3ebf71) korundu.
- **review-fix pre-fix backup:** `~/.claude/command-backups/*.bak-20260604T084344Z` (6 dosya; karşılaştırma için).
- **security_review (2026-06-04 `/security-review-claude-codex`):** çift hakem, coverage_mode=diff. Task delta güvenlik-temiz (otonomi carve-out push/merge/state/vault/override'ı insan kapısı + 6-tavan/cap=10 backstop arkasında tutuyor; otonom commit→push tırmanması kapalı). Codex pre-existing **SR-1** buldu (security-review export teardown `rm -rf "$(dirname)"` + guard'sız mktemp → `rm -rf /` riski; delta-DIŞı). Kullanıcı "hardening" → mktemp `|| exit` + explicit parent (dirname kaldırıldı) ile security-review + review'da kapatıldı; **Codex re-review SR-1 RESOLVED**; drift-check PASS; fonksiyonel test (rm hedefi=parent, asla /). SR-2 (F9) kabul, SR-3 (env) not. SR-1 pre-fix yedek: `*.bak-20260604T095430Z`.
- branch_pushed: **no** (push hiç sorulmadı/yapılmadı). Repo'da commit bekleyen: önceki Check D `58cb02e` + review/security raporları + codex logları + TASK/HANDOFF güncellemeleri.

## Risks
- F9 residual (bilinçli tripwire): `check_reviewer_forbidden` wrapped-prose continuation'ı yakalamıyor. Reviewer prose F9 yazım kuralıyla yazıldı (hard-block satırı self-contained critical/high, medium ayrı advisory). Kapsayan katmanlar: REPLACE-not-append + manual scenario trace + execution Codex review (hepsi yapıldı, temiz).
- Komut dosyaları repo-DIŞı → repo commit yalnız drift-check.sh Check D'yi kapsar. Komut değişiklikleri ~/.claude/command-backups/*.bak-20260604T065456Z ile yedeklendi.

## Notes For Claude
- next: /review-claude-codex → /security-review-claude-codex → closure (/finish-branch-claude-codex)
- **/review + /security SCOPE UYARISI (kritik):** Asıl deliverable 6 komut dosyası **repo-DIŞı** (`~/.claude/commands/*-claude-codex.md`). Committed diff (execute_start_ref 00acbfa..HEAD) YALNIZ `docs/tools/claude-codex-drift-check.sh` (Check D) + active-layer docs içerir — komut dosyaları diff'e GİRMEZ. Reviewer salt committed-diff'e güvenirse asıl işi kaçırır. Çözüm: review substratına komut dosyalarını açıkça dahil et (execution'daki Codex review'larında `~/.claude/commands/*.md → $WT/claude-commands/` kopyalandı, `--cwd` oraya verildi; HOME secret sızıntısını önler). Karşılaştırma için yedek: `~/.claude/command-backups/*.bak-20260604T065456Z` (execution ÖNCESİ hali).
- **/simplify-claude-codex ATLA:** bu deliverable'lara uygulanmaz (kasıtlı byte-identical duplikasyon; established convention — bkz. memory `claude-codex-command-execution`). Doğrudan /review.
- **Regresyon kapısı:** `bash $(git rev-parse --show-toplevel)/docs/tools/claude-codex-drift-check.sh` (A 7-way + B + C 4-way + D 4-way + S-1) → PASS beklenir. Review öncesi taze koştur.
- execute_completed: 2026-06-04 08:05
- branch_pushed: no
- **Plan-ötesi genişleme (kayıt):** medium=fix-required, plan Task 5'in "guard binding"inden derindi → gate/enum/report/override/refine/invariant/checklist'e de threadlendi (Codex tur-4+ haritası, design option b: çözülemeyen medium → 6-tavan DUR, override medium'u listeler). Executor=C/H/M; design-doc=critical/high/claude-confirmed technical-medium (tradeoff-medium user-decision).
- **awk apostrophe fix:** plan'ın literal `check_reviewer_forbidden` awk'ı içinde Türkçe apostrophe (chain-advance'i/false-positive'i) bash tek-tırnağını kırıyordu → awk-içi yorumlardan kaldırıldı (drift-check.sh byte-contracted DEĞİL).
- Vault'a yazılabilecek kalıcı karar: Auto-Fix Policy davranışı (P1'de promote — /commit veya closure'da)

## Notes For Codex
- Review ederken: byte-identical AUTO-FIX block (md5 9a3ebf71, 4-way) + Check A (c7b5976c, 7-way) + Check C (0174e562, 4-way) DOKUNULMADI — reviewer'da prose-only, fix-komutlarında thread marker DIŞI
- Bilinen riskler: F9 residual (tripwire kabul, daha fazla prose-regex epicycle ÖNERME)
- Dokunmaması gereken: CODEX-CALL-PROTOCOL + CODEX-SCAN-SUBSTRATE blokları
