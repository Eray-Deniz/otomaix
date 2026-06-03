# Codex Adversarial Review — auto-fix-review-policy

## Turn 1 — 2026-06-03

Target: working tree (spec doc okutuldu doğrudan)
Verdict: needs-attention

No-ship: the spec still has implementation-breaking ambiguity around counters, reviewer handoff, and the execute-plan commit carve-out.

Findings:
- [high] execute-plan auto-fix loop can violate the human-gated commit carve-out (spec:108)
  execute-plan Adım 7 = RED-GREEN-REFACTOR-COMMIT; auto-fix routed through it can commit
  a confirmed finding without a distinct user approval → carve-out ("commit human-gated")
  contradiction; checkpoint/state refs can advance before a human gate.
  Rec: commit-suppressed RED-GREEN-REFACTOR variant or explicit per-fix/batch commit gate.
- [high] per-cluster ceiling not deterministically implementable (spec:68-79)
  "same finding-cluster/root-cause" + "new findings start fresh" with no stable cluster key,
  merge/split/reopen rule, or global cap → oscillation evades ceiling (fix A reopens B,
  reviewer renames B → restarts turn 1). Oscillation detection is out-of-scope → ceiling
  becomes judgment, not a hard stop.
  Rec: deterministic cluster identity + ledger (finding-id, normalized invariant/path,
  merge/split, reopened inherits prior count) + session-level global maximum.
- [high] review/security chain gates can block without a fixing path (spec:112-113)
  Reviewers report-only; "unresolved C/H/M blocks chain advance" but only "fiili düzeltme
  executor'da olur" — no defined consuming executor, finding-id carry, re-review trigger, or
  closure criterion → dead gate (medium fix-required blocks /security-review with no fixer).
  Rec: explicit report-only → executor handoff contract (command, metadata, re-review entry,
  closure criteria, what stays human-gated).
- [medium] technical-medium vs tradeoff-medium reintroduces approval ambiguity (spec:87-96)
  No decision criteria beyond "technical consistency/applicability bug" vs "design
  preference/tradeoff"; boundary = exactly where adversarial findings sit → Claude can
  auto-edit user-owned design by labeling "technical", or pass real blockers as "tradeoff".
  Rec: classification tests + examples (invariant/schema/path/command/ordering = technical;
  scope/risk/UX = tradeoff) + one-line rationale + default ambiguous → user decision.

Next steps: execute-plan commit suppression; deterministic cluster ledger + reviewer handoff;
tighten medium classification with examples + default.

### Claude disposition (Adım 7)
Tüm 4 bulgu **claude-confirmed**. Auto-Fix Review Policy gereği (claude-confirmed C/H/M,
spec'te technical) onaysız fix → re-review. Full design iteration (substantive) → iter=1.

---

## Turn 2 — 2026-06-03 (re-review)

Target: working tree (revised spec)
Verdict: needs-attention

3 high — hepsi turn-1 fix'lerinin **eksik propagasyonu** (reopen, aynı cluster-key):
- [high] Commit carve-out hâlâ Decision Summary + Verification trace'le çelişiyor (spec:35-37)
  → gövde düzeltildi ama özet/verification "commit human-gated" diyor.
- [high] Verification hâlâ medium'u reviewer chain hard-block yapıyor (spec:213-217)
  → tablo "C/H hard-block, medium advisory" ama verification "C/H/M'de bloke" diyor (dead-gate).
- [high] Global cap ortak implementation kontratında değil (spec:160-162)
  → marker içeriği listesi + Check D global-cap/ledger'ı içermiyor → backstop drift'ten kaçabilir.

Next: 3 çelişen bölümü düzelt + targeted prose sweep.

### Claude disposition (Adım 7, turn 2)
3 bulgu **claude-confirmed** (cluster-key reopen: hepsi turn-1 cluster'larının propagasyon
eksiği → prior sayaç miras, turn 2). Consistency-propagation (targeted) → targeted_fixes=1.
Bu sefer tam grep-sweep yapıldı (commit/chain-gate/global-cap tüm geçişler). → re-review turn 3.

---

## Turn 3 — 2026-06-03 (re-review)

Target: working tree
Verdict: needs-attention

1 high — yeni çelişki (reviewer-handoff cluster, turn 3):
- [high] Report-only medium aynı anda hem fix-required hem "fix-preferred" (spec:143-154)
  → handoff closure'da medium "executor'da fix-preferred" demiş; ama medium-nüansı "fix-required"
  diyor. İki uyumsuz kontrat → confirmed security medium opsiyonel kalabilir.

### Claude disposition (Adım 7, turn 3)
**claude-confirmed.** Çözüm: "advisory" = yalnız reviewer-chain'i hard-bloke etmez; medium
yine **fix-required** (executor'da, tavan altında) — "fix-preferred" kelimesi kaldırıldı.
Ek proaktif: reviewer token listesi (architecture #2 ↔ Check D) eşitlendi. targeted_fixes=2.
Reviewer-handoff cluster artık 3. turunda (turn 4'te tekrar açılırsa → Codex çözüm önerisi modu).
→ re-review turn 4 (verify; henüz approve alınmadı).

---

## Turn 4 — 2026-06-03 (verification)

Target: working tree
**Verdict: approve** — No material findings.

"Current spec is internally consistent on the medium contract across command table, handoff
contract, medium nuance, Verification, and Check D; no remaining high+ implementation-breaking
contradiction is supported by the live text."

### Claude disposition (Adım 7/10)
Clean approve → critical/high yok, iter=1 (<3) → Onayla → Adım 9 final sweep (temiz) → Adım 10
finalize: `status: spec-approved`, `codex_review_status: approved`. Convergence: 4→3→1→0 bulgu.

---
