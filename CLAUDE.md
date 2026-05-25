# Otomaix — CLAUDE.md

Otomaix, ortak altyapı üstünde çalışan AI otomasyon uygulamalarının monorepo'sudur.

**Bilgi sorgusu — önce vault:** Mimari, karar, vendor, geçmiş soruları geldiğinde önce `/root/otomaix-brain/index.md`'ye bak. İlgili wiki sayfasını bul, oradan oku, cevap verirken `[[wikilink]]` citation kullan. Vault'ta yoksa veya güncel değilse kod → memory → `docs/_archive/` sırasıyla geç. Vault canonical kaynaktır; eski `docs/00-platform-mimari.md` ve diğer mimari dokümanlar arşive taşındı, bilgi vault'ta.

Her app'in kendi `CLAUDE.md`'si vardır (`apps/social/backend`, `apps/social/frontend`, `apps/crm`) — o dizine dokunulduğunda otomatik yüklenir.

## Drift koruma (tüm CLAUDE.md'ler için)

CLAUDE.md dosyaları YALNIZCA: proje yapısı, env, deploy, konvansiyonlar.
- Sprint logları → git commit
- Kararlar → `~/.claude/projects/-root-otomaix/memory/decisions_*.md`
- Aktif iş → Tasks (oturum içi)
- Changelog YAZILMAZ

## Çapraz app kuralları

- CRM, `social` schema'yı **yalnızca okur**, yazmaz
- Frontend → Backend tek API gateway (`api.otomaix.com`); CRM → PostgreSQL **direkt** (API katmanı yok)
- Migration'lar `shared/db/migrations/` altında numaralandırılmış sırayla
- n8n workflow değişiklikleri `shared/n8n-workflows/` altına JSON export edilir

## Aktif Task Layer

Canlı task state ve devir teslim için repo overlay'i. Detaylar:
[`docs/specs/2026-05-19-claude-codex-aktif-katman.md`](docs/specs/2026-05-19-claude-codex-aktif-katman.md).

**Path konvensiyonu:**
- `docs/active/CURRENT.md` — aktif task pointer'ı (her zaman var)
- `docs/active/<slug>/TASK.md` — canonical task state (status, decisions, open problems)
- `docs/active/<slug>/HANDOFF.md` — rolling session-boundary devir teslim
- `docs/task-archive/YYYY/MM/<slug>/` — kapanmış task'lar (bitiş tarihine göre)

**Canonical ayrım:**
- **Status**, **Decisions Log**, **Open Problems** → TASK.md
- **Verification**, **Risks**, **Notes For Claude/Codex** → HANDOFF.md
- **Mimari kararlar** (promote edilenler) → Vault `decisions/`

**Manuel mod:** Tüm transition'lar (proposed → active → blocked → waiting-review → done → archived/cancelled) manuel TASK.md edit ile yapılır. Slash command hatırlatmaları sadece "unuttum" friction'ını azaltır — otomatik state mutation yok.

**Codex:** Active layer'a yazma yetkisi yok. Bulgu/öneriyi stdout olarak döner, Claude HANDOFF.md "Notes For Claude"a işler.

### Aktif Task Layer — Session Başlangıç Protokolü

Bir kullanıcı sorusu/task geldiğinde:

1. `docs/active/CURRENT.md` oku (her zaman var; boş olabilir)
2. Listelenen task'lardan kullanıcı sorusuyla alakalı olanı seç
   - Tek aktif task varsa otomatik
   - Birden fazlaysa kullanıcıya sor
   - Hiçbiri uymuyorsa active layer'ı atla
3. Seçilen task için: `docs/active/<slug>/TASK.md` ve `HANDOFF.md` oku
4. Vault sorgusu gerekiyorsa: `/root/otomaix-brain/index.md` → ilgili wiki sayfaları
5. Cevap ver / aksiyon al

### Yeni slash command

- `/handoff` — Claude tek başına HANDOFF.md yazar
- `/handoff --with-codex` — Codex read-only review çağrılır, Notes For Claude'a işlenir

### Mevcut slash command entegrasyonu (özet)

- `/write-plan-claude-codex` sonu → TASK + HANDOFF yaratma sorusu
- `/execute-plan` başı → status=active sorusu
- `/commit` → Current Status update + Vault promotion check (P1)
- `/review` → high/critical → Open Problems + Notes For Claude
- `/finish-branch` → seçime göre matrix (merge/sil = closure+archive, PR = waiting-review, tut = no-op)
