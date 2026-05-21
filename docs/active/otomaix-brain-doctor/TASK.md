---
title: Otomaix Brain Doctor v1
status: active
started: 2026-05-21
last-touched: 2026-05-21
blocked-by: null
---

# Goal

`otomaix-brain` vault'unun yapısal sağlığını denetleyen, sıfır-bağımlılık, vault'a karşı read-only tek-dosya Python CLI (`tooling/brain-doctor/brain_doctor.py`) üret. 16 yapısal kontrol (link/frontmatter/stale/conflict/index/orphan), config-driven, md+json rapor. **Başarı:** plan 14 task TDD ile tamamlanır; gerçek vault'ta smoke run vault'u değiştirmeden bilinen bulguları raporlar (exit 0/1/2 doğru).

# References

- Spec: `docs/specs/2026-05-21-otomaix-brain-doctor.md` (spec-approved)
- Plan: `docs/plans/2026-05-21-otomaix-brain-doctor.md`
- Codex review log: `docs/reviews/codex/2026-05-21-otomaix-brain-doctor.md` (4 turn → approve)
- Review: _(yok)_

# Current Status

Implementasyon + /simplify + /review tamam. 36 unittest PASS (`feat/brain-doctor`). Gerçek vault smoke geçti (vault değişmedi, exit 1). /simplify: 3 DRY helper. /review (bağımsız subagent): 0 Critical, 1 Important (index ambiguous-yutma) → TDD ile kapatıldı, 4 Minor → v1.1'e not. `status=active`. Sıradaki: `/security-review` → `/finish-branch`. Push kullanıcı onayı bekliyor.

# Open Problems

_(yok)_

# Decisions Log

- agentic-os/nexus-ai-memory yeni mimari değil, vault bakım otomasyonu referansı → Vault: [[decisions/2026-05-21-memory-os-eval-brain-doctor]]
- v1 yapısal-only; `--fix` v1.1'e, sektör-pack/LangGraph ertelendi (spec §2/§12)
- Default rapor repo'ya yazılır, vault'a değil; vault-output guard (Codex Turn-2 düzeltmesi)
- `--json` stdout saf JSON, özet stderr'e (Codex plan-review düzeltmesi)
- Slash command `.claude/commands/brain-doctor.md` diskte var ama repo `.claude/`'yi ignore ettiği için tracked değil — force-add kararı kullanıcıya bırakıldı (untracked bırakmak default)
- /review bulgusu (🟡 index ambiguous-yutma): check_index sadece broken'ı emit ediyordu, ambiguous sessizce yutuluyordu → `elif status=="ambiguous"` dalı + test eklendi (spec §7 "ambiguous=error" index için de geçerli). Review log: `docs/reviews/2026-05-21-otomaix-brain-doctor.md`
