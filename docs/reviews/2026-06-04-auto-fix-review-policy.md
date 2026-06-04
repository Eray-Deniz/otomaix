# Review (dual): Auto-Fix Review Policy — 2026-06-04

Review aralığı: substrate baseline..head (auto-fix-review-policy deliverable)
- Deliverable: 7 komut dosyası (`~/.claude/commands/*-claude-codex.md`, repo-DIŞı) + `docs/tools/claude-codex-drift-check.sh` Check D (committed)
- Substrate: geçici git deposu (baseline = görev-öncesi backup `*.bak-20260604T065456Z` + `00acbfa:drift-check.sh`; head = güncel). Her iki hakem aynı aralığı bağımsız review etti.
Reviewers: fresh Claude subagent (general-purpose) + Codex adversarial-review
dual-review: true (claude_status: ran; codex_status: ran)
Requirement context (snapshot — byte-identical iki hakeme): spec md5 43f43c14, plan md5 88f9252e

## Hakemler-arası çelişki (ÖNEMLİ)
İki hakem güçlü ayrıştı:
- **Codex:** verdict `needs-attention` / "No-ship" — 4 high + 3 medium (guard'lar hâlâ manuel menü sunuyor, reviewer handoff'ları medium'u dışlıyor, Check D bypass).
- **Claude subagent:** critical/high YOK; 1 medium (F9), 2 low. Blok + binding'in spec'le eşleştiğini doğruladı ama **binding-vs-prosedür pinpoint kontrolünü yapmadı** → guard prosedürlerinin hâlâ eski davranışı uyguladığını kaçırdı.

**Sentezci (ana Claude) tahkimi:** Codex'in yapısal bulgularını fiili satırları okuyarak doğruladım — **geçerli**. Binding prose (görevde eklendi) yeni politikayı doğru ilan ediyor, ama her guard'ın hemen altındaki **prosedür adımları rewrite EDİLMEMİŞ** — hâlâ "kullanıcı seçer" menüsü (`AskUserQuestion`) sunuyor. Spec açıkça "kullanıcı seçer YERİNE otonom döngü" (REPLACE) diyordu; binding eklendi ama menü silinmedi → binding ile prosedür çelişiyor.

## Critical
Yok.

## High
- **H-1 [codex + adjudicator-verified; claude-subagent çeliştirdi] — SİSTEMİK: politika binding'de ilan edildi, prosedür hâlâ kullanıcı-onayına bağlı.** Görevin tüm amacı (claude-confirmed C/H/M'i onaysız otomatik düzeltmek) prosedürde uygulanmamış. Etkilenen guard'lar:
  - `execute-plan-claude-codex.md:523-528` (Adım 8.5) — binding (514-521) "onay beklemeden otonom döngü" der; prosedür "Düzelt / override / Durdur" menüsü sunar, "Düzelt" = `AskUserQuestion`'da seçilirse + "bulguları kullanıcıyla netleştir".
  - `execute-plan-claude-codex.md:709-714` (Adım 12) — aynı kalıp.
  - `simplify-claude-codex.md:623-627` (Adım 10) — aynı ("Düzelt" = user-selected).
  - `spec-claude-codex.md:551-554` (Adım 7) — "Spec'i güncelle / override / Durdur" menüsü (user-selected); binding (543-549) "onay beklemeden Mode A refine" der.
  - `write-plan-claude-codex.md:408-411` (Adım 13) — "Güncelle / override / Durdur" menüsü (user-selected).
  - Charitable okuma (binding governs → menü stop/override için): yine de prosedür **aktif çelişkili** — menü "unresolved C/H/M VAR" anında sunuluyor (cap sonrası değil); "Düzelt" cap-sonrası rapor seçeneği (devam/kapsam daralt/manuel/blocked) DEĞİL, fix giriş kapısı. Spec "REPLACE" istedi, "ekle" değil.
- **H-2 [codex + adjudicator-verified] — Reviewer Adım 8 handoff medium'u dışlıyor (yeni prose ile çelişik).**
  - `review-claude-codex.md:406` — "**critical + high** bulguları (medium/low DEĞİL)" hâlâ; ama yeni chain-gate prose (429-434) "medium → fix-required + (onayla) Open Problems'a yazılır" der. both-agree medium raporda advisory işaretlenir ama executor'a giden Open Problems'a ASLA ulaşmaz → handoff contract uygulanmaz.
  - `security-review-claude-codex.md:507` — aynı; özellikle riskli çünkü `evidence_gap` taban medium'a sabitlenmiş; güvenlik medium'ları auto-fix döngüsüne hiç ulaşmaz.
  - Spec handoff contract (spec:149-151) açıkça "Reviewer C/H/M bulgularını ... TASK.md Open Problems'a yazar" der — Adım 8 bununla çelişiyor.

## Medium
- **M-1 [both-agree: codex + claude-subagent] — Check D `check_reviewer_forbidden` wrapped-prose bypass'ı kanonik dosyalarda FİİLEN tetikleniyor** (`docs/tools/claude-codex-drift-check.sh:~267-276`). Hard-block satırını takip eden prose continuation (`> **medium advisory** ...`) bullet olmadığı için taranmıyor → gate sessizce PASS. Her iki hakem de ampirik doğruladı (stale `hard-block:` + sonraki satır `critical/high/medium` enjekte → gate violation üretmedi). **Bu bilinçli F9 residual** (spec'te dokümante, `unresolved_high_severity_override: true`); tripwire spec-ötesi gold-plating. Execution'ı bloke etmez AMA "tripwire medium-as-hard-block'u yakalar" güvencesi kanonik dosyalarda fiilen devre dışı — şeffaf olmalı.

## Low
- **L-1 [single-source: claude] — Yazım tutarsızlığı `arketibi` vs `arketipi`** (binding prose'larda karışık, ör. `execute-plan:516` vs `:706`). Kozmetik, davranış etkilenmiyor.

## Disposition Ledger
| id | source | raw sev | final sev | disposition | gerekçe |
|----|--------|---------|-----------|-------------|---------|
| X-1 | codex | high | high | merged-into H-1 | execute-plan 8.5 guard menü |
| X-2 | codex | high | high | merged-into H-1 | simplify 10 guard menü |
| X-5 | codex | medium | high | merged-into H-1 | spec 7 guard menü (sistemik kalıbın parçası → high) |
| X-6 | codex | medium | high | merged-into H-1 | write-plan 13 guard menü (sistemik) |
| X-3 | codex | high | high | merged-into H-2 | review Adım 8 medium dışlama |
| X-4 | codex | high | high | merged-into H-2 | security Adım 8 medium dışlama |
| X-7 | codex | medium | medium | merged-into M-1 | Check D wrapped-prose bypass |
| CS-1 | claude | medium | medium | kept (M-1) | F9 residual — X-7 ile both-agree |
| CS-2 | claude | low | low | kept (L-1) | arketibi/arketipi |
| CS-3 | claude | low/note | n/a | closed | global cap reviewer token'da yok = tasarım gereği doğru (reviewer fix-loop'u yok), defekt değil |

## Sonuç
- both-agree: 1 (M-1 / Check D bypass)
- single-source→adjudicator-verified: H-1, H-2 (Codex buldu, Claude subagent çeliştirdi, sentezci fiili satır okumasıyla doğruladı)
- single-source: L-1 (claude)
- Kapatılan (push-back/design): CS-3
- Açık (devam): H-1, H-2, M-1, L-1
- Hakemler-arası çelişki: H-1, H-2 (Codex high ↔ Claude subagent "yok") — sentezci Codex lehine tahkim etti.

## Net değerlendirme
Görevin çekirdek davranışı (claude-confirmed C/H/M → onaysız otomatik fix) **prosedüre bağlanmamış**. Execution; ortak bloğu, binding prose'ları ve medium-enumerasyonlarını ekledi (Check D PASS), ama her guard'ın altındaki **karar prosedürünü** "menü sun → kullanıcı seçerse düzelt" yapısından "otonom döngü çalıştır → yalnız cap'te menü" yapısına **rewrite etmedi**. Reviewer Adım 8 handoff'ları da medium'u hâlâ dışlıyor. TASK.md Open Problems'taki "medium=fix-required thread (execution'da çözüldü)" iddiası iyimserdi — medium enumerasyona threadlendi, ama prosedür yapısı değişmedi.

Bu, closure'a hazır DEĞİL. Karar kullanıcının: (a) re-execution (guard prosedürlerini gerçekten otonom döngüye çevir + reviewer Adım 8'i C/H/M yap) → status `active`; (b) bilinçli accept-as-is (binding governs okumasıyla, prosedür stale kabul) + Open Problems'a kaydet; (c) kapsam daralt.

## Raw Claude Reviewer Output (appendix)
critical: yok / high: yok
medium: F9 residual bypass kanonik dosyalarda fiilen tetikleniyor (security-review:536-537, review:430-431) — bilinçli dokümante, override true.
low: arketibi vs arketipi yazım; global cap reviewer token'da yok (tasarım gereği doğru).
[Pozitif doğrulamalar: Check D 4-way byte-identical + tripwire token'lar + reviewer token'lar PASS; blok kopyaları byte-identical; spec uyumu (tetik/6-tavan/cluster-key/global cap/carve-out/commit nüansı) blok-içi tutarlı; reviewer report-only + chain hard-block C/H + security override ayrı; finish-branch carve-out doğru; execute-plan TDD-breaker ayrı tutulmuş.]

## Codex raw review
docs/reviews/codex/2026-06-04-review-auto-fix-review-policy-1.md

---

## Fix Applied + Re-Review (kullanıcı kararı: düzelt) — CLEAN

Kullanıcı "düzelt (re-execution)" seçti. H-1/H-2 + alt katmanları düzeltildi; her fix sonrası Codex re-review (fix sonrası review'ı tekrar koştur disiplini). Yakınsama 5 turda:

| Tur | Bulgu | Fix | Sonuç |
|-----|-------|-----|-------|
| R1 | executor guard'lar (execute 8.5/12, simplify 10) + design-doc guard'lar (spec 7, write-plan 13) hâlâ menü; reviewer Adım 8 medium dışlıyor | guard prosedürleri → onaysız otonom döngü (override/Durdur DUR-raporu sonrasına taşındı); reviewer Adım 8 → C/H/M | 1-4 RESOLVED |
| R2 | Mode A refine içi hâlâ kullanıcıya soruyor | Mode A → A1 (otonom, sormaz) / A2 (kullanıcı-tetikli low/tradeoff) | finding 5 partial→ |
| R2+sweep | 4 komutun "Manuel mod" Sözleşme Notları "otomatik döngü değil/3-iter manuel" diyor | dördüne de Auto-Fix carve-out (deterministik süpürmem Codex'in scoped review'ının kaçırdığı execute/simplify'ı da yakaladı) | RESOLVED |
| R3 | review chain-advance gate sadece dual-review'a bakıyor (critical/high ekseni bağlanmamış) | review Adım 9 → iki-eksen AND gate (dual ∧ C/H-yok); C/H varsa hard-block + executor-fix/re-review veya explicit C/H override | RESOLVED |
| R4 | aynı gate'in matris (review:313) + security cross-ref (sec:22) encoding'leri stale | matris cell + security karşılaştırma notu iki-eksene hizalandı | RESOLVED |
| R5 | — | — | **Codex verdict: approve / ship-clean; no material findings** |

- **Blast-radius:** chain-advance ekseni 3 yerde kodluydu (Adım 9 bullet, template, status matrix) + security cross-ref. Hepsi hizalandı. "serbest" + "otomatik döngü değil" + "kullanıcı seçer" süpürmeleri temiz.
- **Doğrulama:** drift-check **PASS** (her fix sonrası; Codex de TMPDIR=/dev/shm ile bağımsız koşturdu → PASS). AUTO-FIX bloğu byte-identical korundu (md5 9a3ebf71); Check D reviewer token + medium-as-hard-block forbidden kapısı PASS (F9 yazım kuralına uyuldu).
- **Değişen deliverable:** 6 komut dosyası (repo-DIŞı). Pre-fix yedek: `~/.claude/command-backups/*.bak-20260604T084344Z`. Pre-task yedek: `*.bak-20260604T065456Z`.
- **Re-review logu:** `docs/reviews/codex/2026-06-04-review-auto-fix-review-policy-1.md` (R1-R5).

**Net sonuç:** Review bulguları (sistemik prose-declared-not-wired gap) düzeltildi + iki hakem (Codex approve + benim exhaustive deterministik süpürmem) temiz onayladı. Closure'a / `/security-review-claude-codex`'a hazır.
