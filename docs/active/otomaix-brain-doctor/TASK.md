---
title: Otomaix Brain Doctor v1
status: waiting-review
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

Tüm kalite zinciri tamam. 38 unittest PASS. /simplify: 3 DRY helper. /review: 0 Critical, 1 Important (kapatıldı), 4 Minor (v1.1). /security-review: 0 Kritik, 1 Yüksek ReDoS + 1 Orta symlink (kapatıldı), kalanlar v1.1 (Open Problems). `/finish-branch` → B (PR): `feat/brain-doctor` origin'e push edildi (24 commit), `status=waiting-review`. PR review feedback'i ele alındı: slash command `.gitignore` istisnasıyla tracked yapıldı, test stdout sızıntısı + HANDOFF staleness düzeltildi. PR URL ile manuel açılacak. Merge sonrası `/finish-branch` A → full closure + archive.

# Open Problems

v1.1 hardening (security review ertelenenleri — tek-kullanıcılı yerel araç için düşük öncelik):
- [ ] `read_pages` üst boyut sınırı (büyük dosya bellek koruması) — vault dış auto-import gelirse gerekli (en büyük gerçek dosya şu an 20KB)
- [ ] `render_markdown` detail/page escape (rapor bir trust boundary değil ama markdown enjeksiyonu temizliği)

# Decisions Log

- agentic-os/nexus-ai-memory yeni mimari değil, vault bakım otomasyonu referansı → Vault: [[decisions/2026-05-21-memory-os-eval-brain-doctor]]
- v1 yapısal-only; `--fix` v1.1'e, sektör-pack/LangGraph ertelendi (spec §2/§12)
- Default rapor repo'ya yazılır, vault'a değil; vault-output guard (Codex Turn-2 düzeltmesi)
- `--json` stdout saf JSON, özet stderr'e (Codex plan-review düzeltmesi)
- Slash command `.claude/commands/brain-doctor.md` PR review'da `.gitignore` istisnasıyla tracked yapıldı (`.claude/*` + `!/.claude/commands/`); root `settings.local.json` ve nested `apps/**/.claude/` ignore'da kaldı. `/brain-doctor` artık merge/clone sonrası geliyor.
- /review bulgusu (🟡 index ambiguous-yutma): check_index sadece broken'ı emit ediyordu, ambiguous sessizce yutuluyordu → `elif status=="ambiguous"` dalı + test eklendi (spec §7 "ambiguous=error" index için de geçerli). Review log: `docs/reviews/2026-05-21-otomaix-brain-doctor.md`
