# Handoff

## Context
- Task: Otomaix Brain Doctor v1
- Linked spec: docs/specs/2026-05-21-otomaix-brain-doctor.md
- Linked plan: docs/plans/2026-05-21-otomaix-brain-doctor.md
- Branch: feat/brain-doctor (origin'e push edildi, waiting-review)
- Last updated: 2026-05-21

## Current State
- Summary: Tüm kalite zinciri tamam (execute-plan + simplify + review + security-review), 38 unittest PASS. `/finish-branch` → B (PR) seçildi: `feat/brain-doctor` origin'e push edildi (20 commit), `status: waiting-review`. PR `gh` olmadığı için URL ile manuel açılacak.
- Blocked: hayır — review bekleniyor

## Resume From
- Start here: PR oluşturulduktan sonra review feedback'i bekle. Merge edilince `/finish-branch` tekrar (A=merge → full closure + archive). Reddedilirse D (cancelled).
- Relevant files: `tooling/brain-doctor/brain_doctor.py`, `test_brain_doctor.py`, `brain_doctor.config.json`
- Next command: PR aç → `https://github.com/Eray-Deniz/otomaix/compare/main...feat/brain-doctor?expand=1`
- Açık iş: slash command `.claude/commands/brain-doctor.md` untracked (repo `.claude/` ignore) — PR'a dahil DEĞİL; istenirse `git add -f`. v1.1 hardening: TASK.md Open Problems (bellek-cap, md-escape).

## Verification
- /security-review (bağımsız subagent + Claude ampirik doğrulama): 0 Kritik, 1 Yüksek (ReDoS → KAPATILDI: regex `{1,512}` sınırı), 1 Orta (symlink okuma → KAPATILDI: is_symlink skip), 1 Orta (bellek) + 1 Düşük (md escape) → ERTELENDİ v1.1 (Open Problems). Reviewer'ın ReDoS fix önerisi yanlıştı, doğru fix ampirik bulundu. Log: `docs/security-reviews/2026-05-21-otomaix-brain-doctor.md`
- /review (bağımsız subagent): 0 Critical, 1 Important (index ambiguous → KAPATILDI), 4 Minor (v1.1). Log: `docs/reviews/2026-05-21-otomaix-brain-doctor.md`
- /simplify: 3 DRY helper (`_severity_counts`, `_is_under_glob_base`, `_exempt_files`), davranış birebir korundu
- Passed: 38 unittest PASS (her task RED→GREEN, scaffold + review-fix + 2 security test dahil); gerçek vault smoke (124 sayfa, exit 1, 28 bulgu — tüm adımlarda birebir aynı) — vault read-only doğrulandı; rapor repo'ya (`reports/`, gitignored)
- Smoke bulguları (TOOL DOĞRU çalışıyor, bunlar gerçek vault sorunları): 18 broken_wikilink (çoğu vault sayfalarının memory-slug'larına `[[project_special_day_redesign]]` gibi link vermesi — vault'ta o isimde sayfa yok), 4 unresolved_conflicts (AGENTS.md, CLAUDE.md, marketingskills-entegrasyon, ozelgun-gorsel-sablon), 1 frontmatter_missing_field, 3 deprecated_visibility, 2 stub
- Failed: -
- Not run: PR henüz GitHub'da oluşturulmadı (gh CLI yok → prefilled URL verildi, manuel açılacak)

## Risks
- `default_stale_days=45` ve `page_not_in_index` yanlış-pozitifleri ilk gerçek raporla kalibre edilecek (spec §11) — ilk smoke'ta stale/page_not_in_index hiç çıkmadı, kalibrasyon için ek veri gerekebilir
- check_conflicts exempt_files'ı dikkate almıyor → AGENTS.md/CLAUDE.md gibi meta dosyalar conflict flagleniyor; spec gereği (conflict tüm sayfalara) ama kullanıcı bunları muaf tutmak isteyebilir (config kalibrasyonu)
- frontmatter parser stdlib minimal — beklenmedik YAML edge-case'lerde gözden geçirilebilir

## Notes For Claude
- `.claude/commands/brain-doctor.md` diskte var, repo `.claude/`'yi ignore ediyor → tracked değil. Force-add (`git add -f`) kullanıcı kararı; default untracked
- Codex'in dikkat çektiği iki nokta da implementasyonda doğrulandı: link resolution path-before-basename (Task 5, 6 test PASS); `--json` stdout saf JSON (Task 13 `test_json_stdout_is_pure_json` PASS)
- Sıradaki session: PR merge sonrası `/finish-branch` A (full closure + archive); reddedilirse D (cancelled)
- Vault'a yazılması gerekebilecek kalıcı kararlar: yok (implementasyonda sürpriz çıkmadı)
- Spec/plan güncellemesi gerektiren noktalar: §11 açık noktalar (stale/page_not_in_index kalibrasyonu) ilk rapordan sonra hâlâ açık; PR review: slash command spec/plan ile tutarlı hale getirilmeli (force-add veya "local-only" notu)
- Kullanıcıdan karar bekleyen konular: slash command tracking (force-add vs spec/plan "local-only" düzeltmesi); config kalibrasyonu (conflict exempt)

## Notes For Codex
- Review ederken özellikle: link resolution (spec §7) ve vault-output guard (§8) implementasyonu doğru mu
- Bilinen riskler: stale eşik kalibrasyonu, frontmatter parser edge-case
- Dokunmaması gereken alanlar: `/root/otomaix-brain` (read-only), active layer + vault yazma YOK (AGENTS)
- Önce okunması gereken dosyalar: `docs/specs/2026-05-21-otomaix-brain-doctor.md`, `docs/plans/2026-05-21-otomaix-brain-doctor.md`
