# Review (dual): codex-review-scope-contract — 2026-06-04

Review aralığı: REVIEW_BASE_SHA..HEAD_SHA
- BASE_REF: `6735133` (execute_start_ref) | BASE_SHA: `6735133` | HEAD_SHA: `1106cd4` | REVIEW_BASE_SHA (merge-base): `6735133` (divergence yok)
Reviewers: fresh Claude subagent (general-purpose, code-reviewer persona) + Codex adversarial-review
dual-review: true  (claude_status: ran; codex_status: ran)
Review workspace: pinned worktree @ HEAD_SHA (clean) + context-only overlay of 7 `~/.claude/commands/*-claude-codex.md`
Main tree at review: clean (0 uncommitted — sızıntı yok)
Requirement context (snapshot): `docs/specs/2026-06-04-codex-review-scope-contract.md` (committed, blob `3335d82`) + `docs/plans/2026-06-04-codex-review-scope-contract.md` (committed, blob `37b1c4e`) — iki hakeme byte-identical (worktree committed paths).

**Scope notu:** Bu task'ın esas çıktısı (7 komut dosyası) repo-DIŞı (versiyon kontrolünde değil); git diff yalnız `docs/tools/claude-codex-drift-check.sh` Check E (+133) + closure docs içerir. 7 komut dosyası context-only overlay olarak incelendi (reviewed-diff DEĞİL). `plan-claude-codex.md` deprecated alias — 7-way sete dahil değil.

## Critical
- Yok.

## High
- **F2 [single-source: codex] — execute-plan dirty review scope / CALL_KIND uyumsuzluğu (false-GREEN).** `execute-plan-claude-codex.md` checkpoint (Adım 8.2) + final (Adım 11): ağaç dirty ise `SCOPE="--scope working-tree"` ama çağrı her zaman `run_codex_scan "base-review"` (overlay yok → committed-only substrate). Dirty'de Codex temiz substrate review eder → uncommitted iş sessizce kaçar. **Doğrulama:** `run_codex_scan` satır 1278 `base-review) :` (overlay yok) + call-site tablosu CALL_KIND'i base-review'a sabitliyor. **Tetikleyici:** review gate'inde dirty tree (TDD tek-commit modelinde anormal); **kök:** pre-existing S-1 substrate (bu task değil — komşu satıra `FINAL_BASE_REF` dokundu). **→ DÜZELTİLDİ (Yol 2 / hard-DUR):** checkpoint+final artık dirty'de DUR (commit/stash + tekrar), SCOPE hep `--base` → base-review ile tutarlı, false-GREEN path yapısal olarak kapalı. **Codex re-review: CLOSED.**

## Medium
- **F3 [single-source: codex] — execute-plan binding/prompt linked spec'i atlıyor.** Spec satır 155: `execute-plan = PLAN_PATH + linked spec + TASK/HANDOFF`. Checkpoint binding (eski 514) linked spec'i atlıyordu; checkpoint prompt (530) linked spec+HANDOFF istemiyordu; final binding (721) doğru ama final prompt (737) linked spec istemiyordu. Bu, task'ın KENDİ invariant'ı (requirement-source explicit okutulacak) kendi komutunda ihlali. Check E generic token kontrol ettiği için yakalamadı; subagent generic wiring'i doğruladığı için kaçırdı. **→ DÜZELTİLDİ:** `linked spec (plan frontmatter source_spec)` checkpoint binding + checkpoint prompt + final prompt'a eklendi (515/532/739). **Codex re-review: CLOSED.**

## Low
- **L1 [single-source: claude] — "5 repo commit" türetilebilir/uçucu sayı** (`TASK.md`, `HANDOFF.md`). Per-SHA liste sabit/audit kaydı (kalsın); literal "5" sayısı drift eder (memory `feedback_no_volatile_values_in_docs`). → Closure'da TASK/HANDOFF güncellenirken giderilir.
- **F1 [single-source: codex] + L2 [single-source: claude] = kabul edilmiş dökümante tavan [both-agree: tavanın varlığında].** F1: overlay'i Check E token'la kontrol ediyor ama prosedür mekanize değil (Claude'un prose'u izleyip overlay'i yapmasına dayanıyor). L2: co-location call-token grep'i "binding bir invocation'dan önce gelir"i değil "bir mention'dan önce gelir"i kanıtlar. İkisi de aynı statik-tavan ailesi: **PROCEDURE/COMPLETENESS CORRECTNESS statik kanıtlanamaz** → drift-check NOTE (satır 418-430) + TASK Task-7 kararı (**"Overlay hâlâ prose guidance, mekanize değil"**) bunu açıkça kabul ediyor; per-command Codex /execute review'a tahsisli (bu oturumda fiilen çalıştı — F2/F3'ü o katman yakaladı). Yeni regression DEĞİL → düzeltme yok, kabul.

## Disposition Ledger (her ham bulgu — sessiz drop yok)
| id | source | raw sev | final sev | disposition | gerekçe |
|----|--------|---------|-----------|-------------|---------|
| C-L1 | claude | low | low | kept → closure'da fixed | uçucu commit sayısı; TASK/HANDOFF closure güncellemesinde giderilir |
| C-L2 | claude | low | low | closed (accepted-ceiling) | co-location token soft-proxy = dökümante COMPLETENESS CEILING; X-F1 tavan ailesiyle birleşik |
| X-F1 | codex | high | low | downgraded (accepted-ceiling) | overlay prosedürü prose-not-mechanized = dökümante PROCEDURE-CORRECTNESS tavanı (drift NOTE + Task-7 "mekanize değil"); regression değil |
| X-F2 | codex | high | high | kept → fixed (CLOSED) | doğrulanmış gerçek false-GREEN; Yol-2 hard-DUR ile düzeltildi; Codex re-review CLOSED |
| X-F3 | codex | medium | medium | kept → fixed (CLOSED) | spec L155'e karşı doğrulandı; linked spec 3 yere eklendi; Codex re-review CLOSED |

## Sonuç
- Kapatılan (fixed + Codex re-review CLOSED): **F2, F3**
- Kapatılan (accepted documented ceiling): **F1, L2**
- Closure'da giderilecek: **L1** (uçucu sayı)
- Hakemler-arası çelişki: **yok** — iki hakem FARKLI özellikleri inceledi (subagent Check E generic wiring token'larını = temiz; Codex spec-kaynak tamlığı + dirty-scope coupling'i = gap). Çelişki değil, tamamlayıcı. Çift-hakem değeri: cross-model çeşitlilik subagent'in kaçırdığı 2 gerçek gap'i yakaladı.
- **Mekanik doğrulama (fix sonrası):** drift-check A–E + binding + 8.6 `exit=0`; S-1 harness `PASS=41 FAIL=0`; stale-sweep (Tur 4+/Tur 1-3) = 0.

## Chain-advance
dual-review: true + unresolved critical/high: **none** (F2 fixed+closed) → `/security-review-claude-codex`'a geçiş **serbest** (Şablon A). Düzeltmeler repo-DIŞı execute-plan dosyasında (uncommitted, restart'ta aktif) — deliverable konvansiyonuyla tutarlı.

## Raw Claude Reviewer Output (appendix)

> Independent review of both layers (repo-internal Check E delta + repo-external command-file overlay). Spec/plan read in full; drift-check + S-1 harness run fresh; six bypass/false-GREEN tests against scratch copies.
>
> **critical:** temiz · **high:** temiz · **medium:** temiz
>
> **low:**
> - "5 repo commit" derivable/volatile count (`TASK.md:35`; sibling `HANDOFF.md`) — memory `feedback_no_volatile_values_in_docs`. Per-SHA list is stable; the literal count drifts.
> - Co-location call-token match is a soft proxy (`drift-check.sh:396`): `adversarial-review`/`task --fresh` are high-frequency prose tokens, so the gate proves "binding precedes *some* mention," not "*a real invocation*." Explicitly documented as the COMPLETENESS CEILING (NOTE 418-430), allocated to per-command Codex /execute review.
>
> **Key verifications (all PASS):** contract block 7-way byte-identical (absent from deprecated alias); binding≠procedure invariant holds at all 8 call sites (concrete pinned-ref, overlay guard terms, no placeholder, co-located before a genuine call whose prompt body asks coverage + 7-field rec); per-call-site `REVIEW_SCOPE_SITES` matrix (checkpoint=`$BASE_REF` + final=`$FINAL_BASE_REF`); AUTO-FIX 4-way byte-identical, "Her review turunda," references 7-field format without redefining; execute-plan 8.6 clean-path delimited region has zero user gate, DUR-path separate; Check E empirically catches un-wired prompt body, stray bindings, duplicate markers, placeholders, no false-positive on real content; security boundary (export overlay separate temp root) + finish-branch closure vocab wired. Gates reproducible (drift-check exit 0; S-1 41/0).
>
> _(Not: subagent execute-plan'ı "temiz" buldu çünkü Check E generic wiring token'larını doğruladı — F2/F3'ün incelediği spec-kaynak tamlığı + dirty-scope coupling eksenini probe etmedi. Çelişki değil; tamamlayıcı.)_

## Codex raw review
`docs/reviews/codex/2026-06-04-review-codex-review-scope-contract-1.md` (Review Turn + Re-review Turn [F2/F3 closure: approve])
