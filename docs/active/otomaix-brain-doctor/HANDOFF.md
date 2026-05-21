# Handoff

## Context
- Task: Otomaix Brain Doctor v1
- Linked spec: docs/specs/2026-05-21-otomaix-brain-doctor.md
- Linked plan: docs/plans/2026-05-21-otomaix-brain-doctor.md
- Branch: main
- Last updated: 2026-05-21

## Current State
- Summary: Spec spec-approved + plan yazıldı/commit'lendi. Kod henüz yazılmadı.
- Blocked: hayır

## Resume From
- Start here: plan Task 1 (scaffold config + dataclasses + severity coverage guard)
- Relevant files: `tooling/brain-doctor/` (henüz yok), `docs/plans/2026-05-21-otomaix-brain-doctor.md`
- Next command: `/execute-plan docs/plans/2026-05-21-otomaix-brain-doctor.md`

## Verification
- Passed: spec 4-turn Codex review (approve); plan üstünde 2 Codex fix uygulandı (json stdout purity, header)
- Failed: -
- Not run: kod testleri (henüz kod yazılmadı)

## Risks
- `default_stale_days=45` ve `page_not_in_index` yanlış-pozitifleri ilk gerçek raporla kalibre edilecek (spec §11)
- frontmatter parser stdlib minimal — beklenmedik YAML edge-case'lerde gözden geçirilebilir

## Notes For Claude
- Codex'in özellikle dikkat çektiği bulgular: link resolution path-before-basename (plan Task 5 testleri kritik); `--json` stdout saf JSON (Task 13 `test_json_stdout_is_pure_json`)
- Claude'un sonraki session'da işlemesi gereken şeyler: `/execute-plan` ile Task 1'den başla, her task sonu commit
- Vault'a yazılması gerekebilecek kalıcı kararlar: implementasyon sırasında çıkarsa (şu an beklenmiyor)
- Spec/plan güncellemesi gerektiren noktalar: §11 açık noktalar ilk rapordan sonra kalibre
- Kullanıcıdan karar bekleyen konular: execution modu (subagent-driven vs inline)

## Notes For Codex
- Review ederken özellikle: link resolution (spec §7) ve vault-output guard (§8) implementasyonu doğru mu
- Bilinen riskler: stale eşik kalibrasyonu, frontmatter parser edge-case
- Dokunmaması gereken alanlar: `/root/otomaix-brain` (read-only), active layer + vault yazma YOK (AGENTS)
- Önce okunması gereken dosyalar: `docs/specs/2026-05-21-otomaix-brain-doctor.md`, `docs/plans/2026-05-21-otomaix-brain-doctor.md`
