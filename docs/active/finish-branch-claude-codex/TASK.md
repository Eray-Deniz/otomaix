---
title: finish-branch-claude-codex komutu
status: waiting-review
started: 2026-06-02
last-touched: 2026-06-02
blocked-by: null
---

# Goal

Mevcut tek-aktörlü `/finish-branch`'i claude-codex ailesine entegre eden `~/.claude/commands/finish-branch-claude-codex.md` komutunu oluştur: tek Codex `task --fresh` **advisory closure-readiness audit** (gate DEĞİL); aile drift contract'ını 6-way → 7-way büyüt; eski `/finish-branch`'i deprecated stub'a indirge. Başarı kriteri: 7-way Check A/B geçer, mevcut finish-branch closure matrix bozulmadan korunur, section-scoped fidelity gates PASS, restart sonrası komut yüklenir.

# References

- Spec: `docs/specs/2026-06-02-finish-branch-claude-codex-command.md` (spec-approved, Codex 4 tur)
- Plan: `docs/plans/2026-06-02-finish-branch-claude-codex-command.md` (plan-approved, Codex 4 tur)
- Review: _(yok — execution sonrası)_

# Current Status

**waiting-review — execution + simplify + review tamamlandı (2026-06-02).** Execution: 8 task uygulandı, final Codex review approved. `/simplify-claude-codex`: **no-op** (repo-dışı markdown deliverable, kod yok; tekrar = kasıtlı drift contract). `/review-claude-codex` (dual: fresh Claude subagent + Codex): 0 critical, 1 high + 4 medium + 3 low bulgu — **8'inin HEPSİ düzeltildi** (hepsi marker bloğu DIŞINDA). Deliverable artık 326 satır + spec scope-notasyonu parity. Re-doğrulanan: 7-way Check A tek md5 `c7b5976c` (drift contract bozulmadı) + Check B 8/8 + frontmatter parse OK. Sıradaki: `/security-review-claude-codex` → closure. Test-EDİLMEYEN: gerçek closure-audit davranışı (restart + canlı branch ister).

# Open Problems

_(yok — spec + plan review'larında tüm critical/high çözüldü)_

# Decisions Log

- Topoloji: tek Codex `task --fresh` **advisory** closure-readiness audit (kod/güvenlik review DEĞİL — zincirde yapıldı); fresh Claude subagent YOK (review'ın iki-hakem modeli overkill)
- Advisory ilkesinin TEK istisnası: *"closure-blocker is not a gate, except it upgrades destructive discard confirmation text"* — yalnız D=sil'de `discard despite closure blockers` upgrade
- İki-fazlı blocker: Codex aksiyon-nötr facts emit → Claude seçilen aksiyona göre Adım 8'de reclassify
- Mode-aware: normal (pinli worktree @ HEAD_SHA) / mainline (worktree yok + HEAD guard) / detached; deterministik git mode-detection (belirsiz → DUR, sor)
- Pinned-target tüm outward/destructive ops: push `${HEAD_SHA}:branch`, merge `${HEAD_SHA}`, **D=sil old-value-bound** `git update-ref -d refs/heads/<branch> $HEAD_SHA`; SCAN_ROOT=$WT (normal) / $PROJECT_ROOT (mainline), Codex `--cwd $SCAN_ROOT`
- Evidence range-containment: `report_HEAD==audit_HEAD` AND `report_BASE` ⊑ `audit_BASE` → coverage-uncertain
- Implementation: hibrit (finish-branch closure semantics base + security-review repo-external delivery scaffold); topoloji security-review'dan KOPYALANMAZ
- Drift contract 6-way → 7-way (execute Task 5 sibling bump + closure'da vault decision doc genişlet)
- **Review (2026-06-02, dual) bulguları + fix'leri** — rapor `docs/reviews/2026-06-02-finish-branch-claude-codex.md`; hepsi düzeltildi:
  - HIGH: remote branch silme `HEAD_SHA`'a bağlı değildi (komutun kendi pinned-target invariant'ını çiğniyordu) → lease-bound `git push --force-with-lease=...:$HEAD_SHA origin :refs/heads/<branch>`
  - MED: `BASE_SHA` tanımsız sembol → `audit_BASE` deterministik türetim (`merge-base origin/$DEFAULT HEAD_SHA`); detached branch-adı `check-ref-format` validation; normal merge push `MERGE_SHA`'a pin; degradation wording canonical AskUserQuestion'a bağlandı
  - LOW: cwd override clarity callout; mainline `origin/main`→`origin/$DEFAULT`; log-path slug kaynağı belirtildi
  - Hakemler-arası ayrışma: Claude shell-safety "temiz" dedi, Codex 3 high buldu → X-3 gerçek high, X-2 medium'a, X-1 low'a uzlaştırıldı (çift-hakem değeri)
  - Tümü marker bloğu DIŞINDA → drift contract byte-identity korundu (re-verified `c7b5976c`)
