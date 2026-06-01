# Handoff

## Context
- Task: security-review-claude-codex komutu
- Linked spec: docs/specs/2026-06-01-security-review-claude-codex-command.md
- Linked plan: docs/plans/2026-06-01-security-review-claude-codex-command.md
- Branch: main
- Last updated: 2026-06-01

## Current State
- Summary: Spec + plan onaylandı (spec 4 Codex turu, plan 5 turu — bulgular tamamen doğrulama-gate hardening'iydi, plan yapısı baştan sağlamdı). Execution başlamadı.
- Blocked: hayır

## Resume From
- Start here: `/execute-plan-claude-codex docs/plans/2026-06-01-security-review-claude-codex-command.md`
- Relevant files: `~/.claude/commands/{spec,write-plan,execute-plan,simplify,review}-claude-codex.md` (drift block kaynağı + 6-way bump), `security-review.md` (deprecate stub), `review-claude-codex.md` (scaffold şablonu), `init.md` (chain-ref)
- Next command: `/execute-plan-claude-codex`

## Verification
- Passed: spec dual review (Turn 4 approve, no material findings), plan review (Turn 5 — PA-1/2/3 + tüm gate'ler resolved)
- Failed: yok
- Not run: execution doğrulamaları (6-way Check A/B sha256, chain sweep rg --pcre2, frontmatter smoke) — execute-time

## Risks
- CODEX-CALL-PROTOCOL bloğu byte-identical kalmalı (marker DIŞI prose bump; mekanik `awk` kopya, elle yazma YOK)
- Chain-ref sweep TÜM aktif `/security-review` referanslarını kapsamalı (deprecated/tarihsel etiketleri KORU)
- Mode-aware cwd override (`$SCAN_ROOT`) blok DIŞINDA; gerçek `node "$COMPANION"` invocation `$SCAN_ROOT` kullanmalı, asla `$PROJECT_ROOT`
- Deliverable repo-DIŞI (`~/.claude/commands/`): audit commit docs-only; restart-to-activate; /finish-branch main üstünde

## Notes For Claude
- Codex'in özellikle dikkat çektiği bulgular: secret-exclusion worktree'de `git show` ile sızıyor → git'siz export şart (spec Turn-1 #2); verification gate'leri section-scoped + shape-specific olmalı (plan Turn 3-5)
- Claude'un sonraki session'da işlemesi gereken şeyler: `/execute-plan-claude-codex` ile plan task'larını doğrulama-güdümlü uygula (Check A/B + smoke = "test")
- Vault'a yazılması gerekebilecek kalıcı kararlar: 6-way drift contract pattern (decision doc `2026-05-26-...hardening` genişlet — closure P1, ZORUNLU)
- Spec/plan güncellemesi gerektiren noktalar: yok (onaylı)
- Kullanıcıdan karar bekleyen konular: yok

## Notes For Codex
- Codex'in review ederken özellikle bakması gereken alanlar: 6-way blok byte-identical, mode-aware binding fidelity, secret-exclusion export hard-removal + symlink sweep
- Bilinen riskler: chain-ref eksik sweep, blok drift
- Dokunmaması gereken alanlar: active layer, vault (Codex YAZMAZ)
- Önce okunması gereken dosyalar: spec + plan + `review-claude-codex.md`
