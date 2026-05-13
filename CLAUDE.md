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
