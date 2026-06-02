---
title: claude-codex ailesi — Codex --cwd untracked-secret exposure hardening
status: proposed
proposed: 2026-06-02
last-touched: 2026-06-02
blocked-by: null
---

# Goal

claude-codex komut ailesinde **4 komutun** (spec / write-plan / execute-plan / simplify) Codex çağrısını `--cwd "$PROJECT_ROOT"` (canlı repo) ile yapması → working-tree'deki **untracked `.env`/secret harici modele (Codex) okunabilir**. Tek mitigasyon warning-based secret-preflight; `--cwd` prompt-talimatından bağımsız read erişimi verir. Bu süreç-içkin riski (canonical blok template'i + override yokluğu) bir tasarım kararıyla kapat.

# References

- **Keşif:** finish-branch-claude-codex security review (2026-06-02, dual) → bulgu **S-1**. Rapor: `docs/security-reviews/2026-06-02-finish-branch-claude-codex.md`; fix commit `d7a80c7` (yalnız finish-branch izole edildi).
- **İzole eden örüntüler (referans çözüm):**
  - `review-claude-codex` → pinli worktree `$REVIEW_WT` (committed-only)
  - `security-review-claude-codex` → git'siz export (full/path, hard) + worktree (diff, best-effort)
  - `finish-branch-claude-codex` → git'siz export (mainline/detached) — S-1 fix deseni
- Drift contract: CODEX-CALL-PROTOCOL bloğu byte-identical (md5 `c7b5976c`); **call-site `--cwd` override marker DIŞINDA** (Check A bozulmaz).

# Current Status

**proposed — başlanmadı.** finish-branch-claude-codex security review'ında (İlke 6 blast-radius) keşfedildi; finish-branch izole edildi, aile-geneli ayrı task'a alındı (kullanıcı kararı A, 2026-06-02).

# Open Problems

- **S-1 (family-wide):** spec / write-plan / execute-plan / simplify → Codex `--cwd "$PROJECT_ROOT"` (canlı). Untracked secret (örn. `backend/.env`) harici modele sızabilir; preflight yalnız uyarır.
- **Zorluk:** Bu 4 komut **working-tree (uncommitted) iş**i review/scope eder — committed-only pinli substrat (review/security-review/finish-branch deseni) DOĞRUDAN uygulanamaz; uncommitted'ı dahil eden bir izolasyon gerekir.

# Decisions Log

- **Henüz karar yok.** 3 aday yön (security review'da çıkarıldı):
  - **(a) Preflight'ı hard-exclude'a çevir** (S-3 deseni) — secret-pattern path'leri context'ten fiziksel çıkar; ama `--cwd` hâlâ canlı kök → tam kapatmaz (tek başına yetersiz).
  - **(b) Working-tree izolasyon substratı** — dirty tree'yi `.git` + secret'sız temp-dir'e kopyala (`rsync`/`cp` + secret rm + symlink sweep), `--cwd <tmp>`. Tam kapatır ama 4 komutta substrat tasarımı + drift-uyumlu prose gerektirir (büyük kapsam → muhtemelen `/spec-claude-codex`).
  - **(c) Kabul + belgele** — kullanıcı her çağrıda secret uyarısı görüyor; riski açıkça belgele, izolasyon ekleme.
- **Kapsam notu:** 4 komut + olası canonical-blok etkisi → kapsamlı; başlanırsa `/spec-claude-codex` → `/write-plan-claude-codex` akışı uygun (tek-dosya quick-fix değil).
