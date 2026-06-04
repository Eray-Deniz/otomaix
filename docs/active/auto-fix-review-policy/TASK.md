---
title: Auto-Fix Review Policy — claude-codex aile geneli
status: waiting-review   # proposed | active | blocked | waiting-review | done | archived | cancelled
started: 2026-06-03
last-touched: 2026-06-04
blocked-by: null
source_plan: docs/plans/2026-06-03-auto-fix-review-policy.md
---

# Goal

claude-codex fix-yapan komutlarına (spec, write-plan, execute-plan, simplify) `claude-confirmed` C/H/M bulgular için kullanıcı-onaysız otonom fix döngüsü ekle (6-tur tavan + global cap=10 backstop); reviewer komutlarını (review, security) report-only disposition/chain-gate diliyle hizala; hepsini `claude-codex-drift-check.sh` Check D (4-way byte-identical AUTO-FIX bloğu + reviewer token + negatif tripwire) ile kilitle. Başarı kriteri: Check A/B/C hâlâ PASS + yeni Check D PASS (byte-for-byte cmp), 6 komut markdown smoke parse, prose senaryo trace tutarlı.

# References

- Spec: `docs/specs/2026-06-03-auto-fix-review-policy.md` (spec-approved, Codex 4 tur)
- Plan: `docs/plans/2026-06-03-auto-fix-review-policy.md` (plan-approved / approved-by-iteration-limit, Codex 4 tur)
- Review: _(yok — execution sonrası /review-claude-codex + /security-review-claude-codex)_

# Current Status

`/review-claude-codex` çalıştı (2026-06-04, çift hakem) → **sistemik bulgu**: AUTO-FIX politikası prose'da ilan edilmiş ama prosedüre bağlanmamıştı (guard'lar/Adım 8/chain-gate hâlâ eski "kullanıcıya sor" davranışı). Kullanıcı "düzelt" dedi → 7+ yer + blast-radius düzeltildi → 5 Codex re-review turunda yakınsadı → **Codex verdict: approve/clean**; drift-check A/B/C/D PASS. Detay: `docs/reviews/2026-06-04-auto-fix-review-policy.md`.

`/security-review-claude-codex` de çalıştı (2026-06-04, çift hakem). **Task delta'sı güvenlik-temiz** (otonomi carve-out tehlikeli ops'ları insan kapısı + sert tavanlar arkasında tutuyor). Codex pre-existing bir `rm -rf /` riski buldu (SR-1, security-review'ın KENDİ teardown'ında, delta-dışı) → kullanıcı "hardening" dedi → mktemp guard + explicit parent (dirname YOK) ile kapatıldı (security-review + review); Codex re-review approve. Detay: `docs/security-reviews/2026-06-04-auto-fix-review-policy.md`.

Status `waiting-review`. **Sonraki: closure (`/finish-branch-claude-codex`)** — review + security chain temiz, engel yok. **Değişen deliverable:** komut dosyaları repo-DIŞı (pre-fix yedekler: review-cycle `*.bak-20260604T084344Z`, SR-1 hardening `*.bak-20260604T095430Z`). Repo commit bekleyen: review + security raporları + codex logları + TASK/HANDOFF (+ önceki Check D 58cb02e). push YOK.

# Notes For Claude

- execute_mode: inline
- checkpoint_cadence: standard
- execute_started: 2026-06-04 06:49
- execute_start_ref: 00acbfaa03671deb49f064aa06d4faf65c42f474

# Open Problems

- **[ÇÖZÜLDÜ — review fix] prose-declared-not-wired sistemik gap:** Execution AUTO-FIX bloğunu+binding'leri+medium enumerasyonlarını ekledi (Check D PASS) AMA asıl prosedürleri (executor guard 8.5/12/10, design-doc guard 7/13, Mode A refine, 4× "Manuel mod" notu, review chain-advance gate + status matrix + security cross-ref) eski "kullanıcıya sor / otomatik döngü değil / tek-eksen" davranışında bıraktı. `/review-claude-codex` (R1) yakaladı (Codex high; Claude subagent kaçırdı → sentezci fiili-satır tahkimi). 5 turda düzeltildi, Codex approve. **Ders (kayıt):** "medium=fix-required thread (execution'da çözüldü)" iddiası iyimserdi — medium enumerasyona threadlendi ama prosedür yapısı değişmemişti. `medium_fix_required_thread_depth` hafızasının tam tekrarı; gelecekte binding≠prosedür ayrı doğrulanmalı.
- **[kapandı] medium=fix-required thread (execution checkpoint):** Plan Task 5 dardı (yalnız "guard binding"); execution'da gate/enum/report/override threadlendi ama refine/contract-note/chain-gate prosedürleri atlandı (yukarıdaki review-fix bunu tamamladı).
- **F9 (bilinçli residual):** `check_reviewer_forbidden` wrapped-prose hard-block enumerasyonunu (`hard-block:` + sonraki prose satırı `…/medium`) yakalamıyor. Negatif check spec-ötesi tripwire; residual REPLACE-not-append + manual scenario trace + execution'da Codex reviewer-edit review ile kapsanır. Execution sırasında reviewer prose'u yazarken **hard-block satırı self-contained `hard-block … critical/high` olmalı, medium ayrı `advisory` cümlesinde**.

# Decisions Log

- 2026-06-03: Canonical block = `spec-claude-codex` (mevcut CODEX-CALL-PROTOCOL/SCAN-SUBSTRATE konvansiyonu, drift-check referans-[0]). Strateji: canonical-block-first + awk-extract byte-copy.
- 2026-06-03: Reviewer-negatif-check TRIPWIRE olarak kabul edildi (spec-ötesi gold-plating); F9 wrapped-prose residual dokümante (kullanıcı kararı). `unresolved_high_severity_override: true`.
- 2026-06-04: `/review-claude-codex` sistemik prose-declared-not-wired gap buldu; kullanıcı "düzelt" dedi (re-execution değil, hedefli fix). 6 komut dosyasının prosedürleri otonom döngüye / C/H/M handoff'a / iki-eksen chain-gate'e hizalandı. Codex 5-tur re-review → approve. Çözüm yöntemi: deterministik exhaustive süpürme + tur-bazlı Codex doğrulama (whack-a-mole yerine). drift-check byte-identical AUTO-FIX bloğu korundu.
- 2026-06-04: `/security-review-claude-codex` task delta'sını güvenlik-temiz buldu; pre-existing SR-1 (`rm -rf "$(dirname "$EXPORT_DIR")"` + guard'sız mktemp → `rm -rf /` riski, security-review'ın kendi teardown'ı) → kullanıcı "şimdi hardening" → mktemp `|| exit` guard + explicit parent var (dirname kaldırıldı) ile security-review + review'da kapatıldı; Codex re-review SR-1 RESOLVED. Mevcut `_css_secret_scan` guard pattern'iyle tutarlı.
