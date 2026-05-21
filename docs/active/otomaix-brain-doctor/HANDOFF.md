# Handoff

## Context
- Task: Otomaix Brain Doctor v1
- Linked spec: docs/specs/2026-05-21-otomaix-brain-doctor.md
- Linked plan: docs/plans/2026-05-21-otomaix-brain-doctor.md
- Branch: main
- Last updated: 2026-05-21

## Current State
- Summary: Implementasyon + /simplify + /review + /security-review tamam — `feat/brain-doctor`, 38 unittest PASS, gerçek vault smoke geçti. Tüm kalite adımları bitti, sadece `/finish-branch` + push kaldı.
- Blocked: hayır

## Resume From
- Start here: `/finish-branch` (merge/PR/tut/sil)
- Relevant files: `tooling/brain-doctor/brain_doctor.py`, `test_brain_doctor.py`, `brain_doctor.config.json`
- Next command: `/finish-branch` (içinde push/merge kararı verilir)

## Verification
- /security-review (bağımsız subagent + Claude ampirik doğrulama): 0 Kritik, 1 Yüksek (ReDoS → KAPATILDI: regex `{1,512}` sınırı), 1 Orta (symlink okuma → KAPATILDI: is_symlink skip), 1 Orta (bellek) + 1 Düşük (md escape) → ERTELENDİ v1.1 (Open Problems). Reviewer'ın ReDoS fix önerisi yanlıştı, doğru fix ampirik bulundu. Log: `docs/security-reviews/2026-05-21-otomaix-brain-doctor.md`
- /review (bağımsız subagent): 0 Critical, 1 Important (index ambiguous → KAPATILDI), 4 Minor (v1.1). Log: `docs/reviews/2026-05-21-otomaix-brain-doctor.md`
- /simplify: 3 DRY helper (`_severity_counts`, `_is_under_glob_base`, `_exempt_files`), davranış birebir korundu
- Passed: 38 unittest PASS (her task RED→GREEN, scaffold + review-fix + 2 security test dahil); gerçek vault smoke (124 sayfa, exit 1, 28 bulgu — tüm adımlarda birebir aynı) — vault read-only doğrulandı; rapor repo'ya (`reports/`, gitignored)
- Smoke bulguları (TOOL DOĞRU çalışıyor, bunlar gerçek vault sorunları): 18 broken_wikilink (çoğu vault sayfalarının memory-slug'larına `[[project_special_day_redesign]]` gibi link vermesi — vault'ta o isimde sayfa yok), 4 unresolved_conflicts (AGENTS.md, CLAUDE.md, marketingskills-entegrasyon, ozelgun-gorsel-sablon), 1 frontmatter_missing_field, 3 deprecated_visibility, 2 stub
- Failed: -
- Not run: `/simplify`, `/review`, `/security-review`; push (onay bekliyor)

## Risks
- `default_stale_days=45` ve `page_not_in_index` yanlış-pozitifleri ilk gerçek raporla kalibre edilecek (spec §11) — ilk smoke'ta stale/page_not_in_index hiç çıkmadı, kalibrasyon için ek veri gerekebilir
- check_conflicts exempt_files'ı dikkate almıyor → AGENTS.md/CLAUDE.md gibi meta dosyalar conflict flagleniyor; spec gereği (conflict tüm sayfalara) ama kullanıcı bunları muaf tutmak isteyebilir (config kalibrasyonu)
- frontmatter parser stdlib minimal — beklenmedik YAML edge-case'lerde gözden geçirilebilir

## Notes For Claude
- `.claude/commands/brain-doctor.md` diskte var, repo `.claude/`'yi ignore ediyor → tracked değil. Force-add (`git add -f`) kullanıcı kararı; default untracked
- Codex'in dikkat çektiği iki nokta da implementasyonda doğrulandı: link resolution path-before-basename (Task 5, 6 test PASS); `--json` stdout saf JSON (Task 13 `test_json_stdout_is_pure_json` PASS)
- Sıradaki session: `/simplify` ile başla, sonra review zinciri, en son `/finish-branch`
- Vault'a yazılması gerekebilecek kalıcı kararlar: yok (implementasyonda sürpriz çıkmadı)
- Spec/plan güncellemesi gerektiren noktalar: §11 açık noktalar (stale/page_not_in_index kalibrasyonu) ilk rapordan sonra hâlâ açık
- Kullanıcıdan karar bekleyen konular: push onayı; slash command force-add; config kalibrasyonu (conflict exempt)

## Notes For Codex
- Review ederken özellikle: link resolution (spec §7) ve vault-output guard (§8) implementasyonu doğru mu
- Bilinen riskler: stale eşik kalibrasyonu, frontmatter parser edge-case
- Dokunmaması gereken alanlar: `/root/otomaix-brain` (read-only), active layer + vault yazma YOK (AGENTS)
- Önce okunması gereken dosyalar: `docs/specs/2026-05-21-otomaix-brain-doctor.md`, `docs/plans/2026-05-21-otomaix-brain-doctor.md`
