# Handoff

## Context
- Task: claude-codex ailesi — Codex --cwd untracked-secret exposure hardening
- Status: **done** (2026-06-03) — deploy (restart) + closure-review koşuldu; S-1 canlıda KAPALI (gerçek companion smoke)
- Keşif: finish-branch-claude-codex security review (2026-06-02), bulgu S-1

## Current State
- **6 task uygulandı.** CODEX-SCAN-SUBSTRATE bloğu (5 fonksiyon) 4 komuta byte-identical gömüldü; her Codex çağrısı `run_codex_scan "$CALL_KIND" <CALL>` → `--cwd "$SCAN_ROOT"` (sanitized fetch clone). **S-1 kapandı** (working-tree `.env`/secret artık Codex'e gitmez).
- Repo commit'leri: `41fc582` harness · `d317fc3` harness-fix (T13/T14 sourced canonical) · `c9429e8` feat docs · `9a36d31` final-review fix (call-site wiring + case-insensitive secret-scan). **Push yok** (closure).
- Komut dosyaları repo-DIŞI (`~/.claude/commands/{spec,write-plan,execute-plan,simplify}-claude-codex.md`) → **restart ile aktif**. Backup: `~/.claude/commands/*.bak-20260603-070606`.
- Harness: `docs/tools/codex-scan-substrate-harness.sh` (T1-T6/T11-T15, **41/41**).

## Verification (execution — DÜRÜST, hepsi bu oturumda taze koşuldu)
- **Deterministik suite (PASS):** Check A 7-way `c7b5976c` intact · Check C 4-way byte-identical (`cmp`+md5) · tripwire 15×4 (`grep -Eiq`/`run_codex_scan`/`css_resolve_base` dahil) · S-1 invariant=0 (4 komut, protokol-dışı `--cwd "$PROJECT_ROOT"` yok) · OP-4 harness **41/41** gerçek git fixture · smoke ×4 (frontmatter+marker+protokol).
- **OP-4 KAPANDI:** T1-T6 (index-preserve, fail-closed, stale-guard, cleanup, symlink-exfil, secret-scan lower+UPPER) + T11/T12 (required-only/namespace) + **T13 (css_resolve_base) + T14 (run_codex_scan fail-closed) + T15 (subshell-safe cleanup)** — T13/T14 **sourced gerçek canonical fonksiyonu** test eder (ayna değil; checkpoint-1 high fix).
- **Codex review zinciri:** pre-exec (drift yok) → checkpoint-1 (1 high T14-ayna + 1 med cleanup → **düzeltildi** d317fc3) → final round-1 (1 high call-site wiring kırılgan + 1 med uppercase secret-scan → **düzeltildi** 9a36d31) → **final round-2 APPROVE** (Codex harness'ı kendisi koştu, 41/41; 9/9 call-site local directive; no material findings).
- **Önemli ders:** S-1 invariant grep'i fix-öncesi de 0'dı → finding 1'i yakalamadı; gerçek kapanış per-call-site local `run_codex_scan` direktifiyle sağlandı + Codex re-review ile doğrulandı (deterministik grep tek başına yetmedi).

## Resume From — KAPANDI (done, 2026-06-03)
Restart sonrası closure-review koşuldu (ağır dual-review ceremony reddedildi — 14 Codex turu yetti; gerekçe [[feedback_severity_gates_process_weight]]):
1. **Blast radius** (backup'a karşı diff): 4 komutta cerrahi-temiz (substrat + call-site + 2 `--cwd` açıklaması; iş akışı bozulmadı).
2. **Drift contract canlı:** Check A 7-way `c7b5976c` intact · Check C 4-way `0174e562` intact · harness **41/41** (canlı bloktan source).
3. **Drift fix:** stale "37 PASS" → "T1-T6/T11-T15 PASS" (4 komut, de-volatilize; Check C md5 değişmedi).
4. **Canlı smoke (gerçek companion 1.0.4):** `run_codex_scan task-fresh` rc=0 + `--cwd SCAN_ROOT`≠repo + planted secret 0 hit → **S-1 canlıda kapalı**.
- Geçici artefakt: `/tmp/css-live-smoke.sh` (smoke scratch). Repo gerçeği commit'lerde (41fc582/d317fc3/c9429e8/9a36d31) + 4 komut dosyasında.
- Kalan tek dış adım: **push + arşiv** (kullanıcı onayıyla bu oturumda).

## Risks
- **`@execution-pin` plumbing:** base-resolution (call-site, live repo), SHA-vs-ref tespiti, default-branch adayları (main/master/trunk/origin-HEAD) Codex'çe tam spec'lenmedi → harness kesinleştirmeli.
- İçerik secret-scan pattern listesi örnek (tam değil) — allow-list birincil kapı.
- Committed secret: fetch HEAD ancestry'sini getirir → committed secret (varsa) substratta olur (best-effort caveat; bu repoda yok).
- Performans: per-call `git init`+fetch; execute-plan çok-çağrılı → birikir.
- Yeni drift yüzeyi: 4-way Check C drift-check tooling'e eklenmeli.

## Notes For Codex
- **Açık iş:** OP-4 (T1-T6: NUL/path-space, producer/fetch/apply hata→fail-closed, stale SCAN_ROOT, cleanup, symlink exfil, secret-scan) + `@execution-pin` satırları — ampirik harness.
- **Kısıt:** `CODEX-CALL-PROTOCOL` bloğu (`c7b5976c`, 7-way) byte-identical KALMALI; substrat onun DIŞINDA, `--cwd "$SCAN_ROOT"` override prose talimatı.
- Codex active layer'a **YAZMAZ** — bulgu/öneriyi stdout döner, kullanıcı/Claude işler.

## Codex Empirical Resolution + Spec Review (özet — spec'e işlendi)
- **Mekanizma (Iter 3):** sanitized fetch clone — `git init` + live repo'dan yalnız HEAD+base/default fetch + `remote remove origin` + `.git/logs` sil + `core.logAllRefUpdates false`. Overlay: `OVERLAY_WORKTREE` (tüm tracked dirty) + `REQUIRED_CURRENT_FILES` (untracked allow-list); index-preserving (`git apply --index`).
- **Turn 6 fix'leri (spec'e işlendi):** base-ref EXACT namespace (`origin/main`→`refs/remotes/...`; SHA→ref yaratma); OVERLAY_WORKTREE tüm-dirty; patch temp-dosya materyalize + `[-s]` (fail-closed); default-branch call-site resolve.
- **Turn 7 fix'leri (spec'e işlendi):** iki overlay modu (OVERLAY_WORKTREE tüm-dirty / OVERLAY_REQUIRED_ONLY pathspec-limited task-fresh — alakasız dirty girmez); base-ref case'e `refs/*)` full-ref dalı; T11/T12 test; dead helper `_css_required_has_uncommitted` silindi.

## Notes For Claude
- **Ders:** Kabuk/git/harici-araç davranışı içeren spec işinde **ampirik doğrula** (throwaway kur + çalıştır), prose'da kalıp delikleri review'a bırakma. Iter 0-2'de bu atlandı → 5 tur yakınsamadı; Iter 3'te Codex ampirik koşunca tek seferde oturdu. Detay: [[feedback_empirical_validation_for_shell_specs]].
- Active-layer'ı flip'te grep-sweep et: bu drift **iki kez** Codex review'da yakalandı (Turn 6 #6 stale "TEST EDİLMEDİ"/Resume; Turn 7-followup #medium stale "review'a sokacak"/targeted_fixes:3). Decisions Log eklemek YETMEZ — Current Status + HANDOFF Context/Current State/Resume hepsi sweep edilmeli ([[feedback_sweep_sibling_sites]]).
- **Codex exposure (kullanıcı süreç notu, execution'da hâlâ geçerli):** Substrate canlı 4 komuta DEPLOY edilip restart yapılana dek Codex çağrıları `--cwd "$PROJECT_ROOT"` (sertleştirilmemiş) ile çalışır → repo'daki `.env`'i okuyabilir. Execution sırasında Codex çağrılarını minimumda tut VEYA prompt/dosya kapsamını sır içermeyecek şekilde (yalnız plan/spec/kod docs) sınırla. Bu görev bizzat o riski kapatıyor; kapanana kadar ironiyi tekrarlama.
