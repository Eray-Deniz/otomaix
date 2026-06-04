---
title: Codex Review Scope Contract + Structured Recommendation + execute-plan 8.6 Auto-Continue
status: waiting-review     # proposed | active | blocked | waiting-review | done | archived | cancelled
started: 2026-06-04
last-touched: 2026-06-04
blocked-by: null
source_spec: docs/specs/2026-06-04-codex-review-scope-contract.md
source_plan: docs/plans/2026-06-04-codex-review-scope-contract.md
---

# Goal

claude-codex komut ailesine 7-way byte-identical `CODEX-REVIEW-SCOPE-CONTRACT` bloğu ekle (pinned
scope + per-command requirement-source binding + dependency scope + command-policy external-overlay +
coverage statement + her finding'e structured fix recommendation), yeni iki-katmanlı drift **Check E**
ile kilitle; AUTO-FIX'i **her turda** structured recommendation'a çevir (4-way); execute-plan
**Adım 8.6**'yı clean-checkpoint auto-continue'ya yeniden yaz. **Başarı kriteri:** Check A/B/C/D + yeni
Check E PASS (byte-lock + section-anchored marker hard-gates), stale "Tur 4+/max review 3" sweep=0,
7 komut smoke-parse, S-1 harness PASS, scenario trace tutarlı. **Ana invariant:** predecessor'ın
"binding≠procedure" hatasını tekrar etme — blok deklare edip prosedürü/prompt gövdesini wire'lamamak
yasak (Check E marker-anchored hard-gate bunu kanıtlar).

# References

- Spec: `docs/specs/2026-06-04-codex-review-scope-contract.md` — **spec-approved / codex_review_status: approved** (Codex 5 tur, F1-F6 çözüldü)
- Plan: `docs/plans/2026-06-04-codex-review-scope-contract.md` — **plan-approved / approved** (Codex plan-review 5 tur, P1-P8 çözüldü; finalize 2026-06-04)
- Codex review logları: `docs/reviews/codex/2026-06-04-codex-review-scope-contract.md` (spec, 5 tur) + `...-codex-review-scope-contract-plan.md` (plan, 5 tur)
- Review/Security: _(yok — execution sonrası /review-claude-codex + /security-review-claude-codex)_

# Current Status

**EXECUTION TAMAMLANDI → waiting-review.** `/execute-plan-claude-codex` (inline + standard) ile 8 task
TDD/RED-first uygulandı. 7 komut dosyası (deliverable, repo-DIŞı) düzenlendi: CODEX-REVIEW-SCOPE-CONTRACT
7-way blok + per-call-site REVIEW-SCOPE-BINDING + AUTO-FIX her-turda (4-way) + execute-plan 8.6 clean/DUR.
drift-check Check E (byte-lock + per-call-site binding + 8.6 clean-path) eklendi. **Repo commit'leri (main,
local — push YOK):** `a39d3c8` byte-lock · `be813c3` binding assertion · `96065b9` 8.6 assertion ·
`4b8681e` per-call-site model (final-review fix) · `0f2cefd` balance-guard comment + ceiling doc.

**Codex final execution review = approved** (4 tur: combined→2 bulgu → high base-wiring fix → table-fix →
round-4 approve). Mekanik: drift-check A–E PASS · S-1 41/0 · smoke 7/7 · stale-sweep=0. Çözülmemiş C/H/M yok.

**Deliverable repo-DIŞı → aktif olması için Claude Code RESTART gerekir.**

**`/review-claude-codex` TAMAMLANDI (2026-06-04, dual).** Fresh Claude subagent + Codex adversarial-review;
pinli worktree + 7-komut context-only overlay. Codex 2 gerçek bulgu yakaladı (subagent "temiz" demişti —
cross-model değer): **F2** (execute-plan dirty SCOPE↔CALL_KIND false-GREEN, high) → **Yol-2 hard-DUR ile
düzeltildi**; **F3** (execute-plan binding/prompt linked spec eksik, spec L155, medium) → **düzeltildi**
(linked spec 3 yere). İkisi de Codex re-review CLOSED. F1/L2 = dökümante kabul tavan (overlay prose-not-
mechanized; düzeltme yok). Fix'ler execute-plan'da (repo-DIŞı, uncommitted → restart'ta aktif). Re-verify:
drift-check A–E exit 0 · S-1 41/0 · stale 0. Rapor: `docs/reviews/2026-06-04-codex-review-scope-contract.md`.

**Sonraki adım:** `/security-review-claude-codex` (unresolved high yok → chain serbest) → closure (`done`
+ vault promotion P1). Güvenlik yüzeyi düşük (docs/tools + komut-prose) — security-review düşük-değer olabilir.

# Open Problems

- **[residual — static ceiling #1: procedure/ref-correctness]** Check E WIRING'i hard-gate'liyor
  (concrete token, section-anchored, no placeholder, co-located, prompt-body asks, 8.6 clean-no-gate).
  **Ref/procedure-correctness** statik kanıtlanamaz → Codex /execute review'a tahsis. **Bu oturumda
  fiilen tetiklendi:** Codex final review execute-plan'ın final-review base-wiring bug'ını yakaladı
  (`RESOLVED_BASE="$BASE_REF"` → `FINAL_BASE_REF`, 3 kardeş yerde: scope/binding/note + call-site table).
  Düzeltildi (commit `4b8681e` + external table fix). Katman çalıştı.
- **[residual — static ceiling #2: completeness]** Check E matristeki BİLİNEN call-site'ların binding'ini
  kanıtlar ama "hiç bağsız gated call YOK" (completeness) statik kanıtlanamaz — serbest prose'da gerçek
  çağrıyı tanım/tablo/yorumdan ayırmak arms-race. Codex (round 3) "defensible" dedi. drift-check'te
  COMPLETENESS CEILING note + balance-guard comment düzeltmesiyle dökümante edildi (commit `0f2cefd`);
  completeness Codex /execute review'a tahsis. REVIEW_SCOPE_SITES yeni gated call eklenince elle güncellenir.

# Decisions Log

- 2026-06-04: **A1 mimarisi** seçildi (kullanıcı explicit): yeni `CODEX-REVIEW-SCOPE-CONTRACT` 7-way
  byte-identical blok + yeni Check E. Red: A2 (mevcut blokları genişlet — CALL-PROTOCOL review-olmayan
  task --fresh'te de kullanılıyor, enforcement bölünür), A3 (prose-only — binding≠procedure riski).
- 2026-06-04: **3 kullanıcı refinement'ı** spec'e işlendi: (1) external-overlay secret-scan helper
  komut-bazlı (SCAN-SUBSTRATE taşıyan `_css_secret_scan` reuse; taşımayan reviewer eşdeğer guard) +
  reviewer overlay context-only işaretli; (2) `last_checkpoint_ref` DAR mechanical exemption (yalnız
  HANDOFF Verification.last_checkpoint_ref = POST_CP_HEAD; lifecycle/status/decision DEĞİL); (3)
  finish-branch advisory/report-only vocab (closure-blocker/warning/note; auto-fix'e dönüşmez).
- 2026-06-04: **Check E iki katmanlı** (kullanıcı onayı): byte-lock (7-way cmp + token) hard-gate +
  **marker-anchored section assertions** hard-gate (`REVIEW-SCOPE-BINDING:<slug>` region: concrete
  pinned-ref + overlay guard terms + asks + no-placeholder + co-location + prompt-body asks; delimited
  `8.6-CLEAN-PATH` no-user-gate). Prose/semantic → advisory-tripwire. Marker-anchoring, predecessor'ın
  "blok var ama prosedür eski" hatasının plan-seviyesinde tekrarını (Codex plan-review P1-P8) çözdü.
- 2026-06-04: **AUTO-FIX değişikliği:** "Tur 4+" → **her review turunda** structured recommendation;
  7-alan format yalnız CONTRACT bloğunda tanımlı, AUTO-FIX referans eder (format drift imkânsız). 4-way
  byte-identical korunur (Check D re-verify). Stale "Tur 4+/Tur 1-3" sweep (spec/write-plan 3'er,
  execute 6, simplify 4; reviewer'lar 0). "max review 3" yalnız AUTO-FIX bloğundaki "geçersiz" negation.
- 2026-06-04: **Commit boundary:** deliverable repo-DIŞı (`~/.claude/commands/*.md`, uncommitted);
  repo-içi committable = `docs/tools/claude-codex-drift-check.sh` + docs (spec/plan/review/active).
  `plan-claude-codex.md` (deprecated alias) 7-way sete DAHİL DEĞİL.
- 2026-06-04: **Plan finalize = `approved`** (kullanıcı onayı, "finalize as approved"). `iterations=4`
  (≥3) olmasına rağmen `approved-by-iteration-limit` DEĞİL — Codex turn 5 temiz approve verdi, 4 iterasyon
  fix-required otonom döngü kaynaklı (Auto-Fix policy: 3-limit fix-required'a uygulanmaz). unresolved
  critical/high = none. Ardından docs-only commit (push YOK).
- 2026-06-04: Vault promotion YAPILMADI — closure'a (P1) bırakıldı.
- 2026-06-04 (execution): Checkpoint Codex review'ları (standard cadence, her 3 task) **atlandı**; kullanıcı
  fark etti → tek combined final review (7 external dosya substrate'a overlay'li) çalıştırıldı. Ders:
  zorunlu review gate'i sessizce atlama (memory [[feedback_run_mandatory_review_gates]]).
- 2026-06-04 (execution): **Check E one-per-command → per-call-site matrix** (REVIEW_SCOPE_SITES). Codex
  final review execute-plan'ın iki adversarial-review call'ı (checkpoint 8.4 + final 11) olduğunu, yalnız
  final'in bağlı olduğunu + final binding'in ref'inin yanlış olduğunu yakaladı (false-GREEN). execute-plan
  artık checkpoint (`$BASE_REF`) + final (`$FINAL_BASE_REF`) iki ayrı binding taşır. Pre-scan task--fresh
  call'ları (research) kapsam dışı diye dökümante edildi.
- 2026-06-04 (execution): **finding-2 completeness ceiling KABUL** — call-site enumeration arms-race
  (semantik negatif), call-site-id marker boşluğu kaydırır. drift-check NOTE + balance-guard comment ile
  dökümante; completeness Codex /execute review'a tahsis (Codex round-3 "defensible" onayı). Memory
  [[feedback_semantic_negative_not_regexable]] + [[feedback_severity_gates_process_weight]].
- 2026-06-04 (post-review polish): **Task 7 binding'leri per-command somutlandı** (Codex follow-up bulgusu —
  düşük severity, prosedür-netliği, bug DEĞİL). command-policy satırına overlay destination eklendi:
  fix-komutlar → `$SCAN_ROOT/claude-commands/`, review → `$REVIEW_WT/claude-commands/`, security-review →
  `$SCAN_ROOT` (diff) + ayrı temp root (export), finish-branch → audit substrate + export temp root.
  Spec §3.4'e sadık. Check E token'ları korundu; drift-check + S-1 + stale-sweep re-verify PASS. Overlay
  hâlâ prose guidance (mekanize değil) — runtime davranışı değişmedi, gelecekteki command-policy review'a
  daha net talimat.
- 2026-06-04 (review): **`/review-claude-codex` dual** — Codex **F2** (execute-plan dirty SCOPE↔CALL_KIND
  false-GREEN, high) + **F3** (checkpoint/final binding+prompt linked spec eksik vs spec L155, medium)
  yakaladı (subagent kaçırmıştı — farklı eksen incelediler, çelişki değil). **F2 → Yol-2 (dirty'de hard-DUR,
  SCOPE hep --base)**, **F3 → linked spec 3 yere** ile düzeltildi; Codex re-review ikisini de **CLOSED**.
  **F1/L2** (overlay/co-location statik-tavan) kabul (düzeltme yok — drift NOTE + Task-7 "mekanize değil").
  Fix'ler execute-plan repo-DIŞı (restart'ta aktif). [[feedback_rerun_review_after_fix]] (fix sonrası
  re-review koşturuldu) + [[feedback_no_volatile_values_in_docs]] (L1 uçucu commit sayısı düzeltildi).

# Notes For Claude

**Execution state (execute-plan-claude-codex Adım 4 — kullanıcı onayıyla yazıldı):**
- execute_mode: inline
- checkpoint_cadence: standard
- execute_started: 2026-06-04 14:06
- execute_start_ref: 67351331dce85dacd747b5f52259f02554518129   # `git rev-parse HEAD` (execute öncesi); Adım 8.2 + Adım 11 base ref default'u
