# AGENTS.md

> Bu dosyanın marker'lı bloğu `/sync-agents-md` komutu tarafından
> Codex'in CLAUDE.md damıtması ile üretilir. Marker dışına manuel
> içerik ekleyebilirsin — korunur.

<!-- BEGIN CODEX-DISTILLED -->
> Bu icerik Codex CLI icin /root/otomaix/CLAUDE.md from distilled. Slash command, Skill tool gibi Claude-specific kurallar haric tutulmustur.

## Proje Ozeti

Otomaix, ortak altyapi ustunde calisan AI otomasyon uygulamalarinin monorepo'sudur.

## Bilgi Kaynagi Sirasi

Mimari, karar, vendor veya gecmis bilgi sorularinda once `/root/otomaix-brain/index.md` kontrol edilmelidir.

Ilgili wiki sayfasi bulunup oradan okunmali; cevaplarda `[[wikilink]]` citation kullanilmalidir.

Vault'ta bilgi yoksa veya guncel degilse sira:

1. Kod
2. Memory
3. `docs/_archive/`

Vault canonical kaynaktir. Eski `docs/00-platform-mimari.md` ve diger mimari dokumanlar arsive tasinmistir; mimari bilgi icin vault esas alinmalidir.

## App Bazli Kurallar

Her app'in kendi proje talimatlari vardir:

- `apps/social/backend`
- `apps/social/frontend`
- `apps/crm`

Bu dizinlerde calisilirken ilgili app'e ait ek kurallar dikkate alinmalidir.

## Dokumantasyon ve Drift Koruma

`CLAUDE.md` benzeri proje talimat dosyalari yalnizca su tur bilgileri icermelidir:

- Proje yapisi
- Env bilgisi
- Deploy bilgisi
- Konvansiyonlar

Bu dosyalara sprint logu, aktif is kaydi veya changelog eklenmemelidir.

Kayit yerleri:

- Sprint loglari: git commit
- Kararlar: `~/.claude/projects/-root-otomaix/memory/decisions_*.md`
- Aktif is: oturum ici task takibi
- Changelog: yazilmaz

## Capraz App Kurallari

- CRM, `social` schema'yi yalnizca okur; yazmaz.
- Frontend -> Backend iletisiminde tek API gateway kullanilir: `api.otomaix.com`.
- CRM -> PostgreSQL direkt baglanir; CRM icin API katmani yoktur.
- Migration dosyalari `shared/db/migrations/` altinda numaralandirilmis sirayla tutulur.
- n8n workflow degisiklikleri `shared/n8n-workflows/` altina JSON export olarak eklenir.

## Aktif Task Layer

Canli task state ve devir teslim icin repo overlay'i kullanilir.

Detay dokumani:

- `docs/specs/2026-05-19-claude-codex-aktif-katman.md`

Path konvensiyonu:

- `docs/active/CURRENT.md` — aktif task pointer'i; her zaman var olabilir, bos olabilir.
- `docs/active/<slug>/TASK.md` — canonical task state; status, decisions, open problems.
- `docs/active/<slug>/HANDOFF.md` — rolling session-boundary devir teslim.
- `docs/task-archive/YYYY/MM/<slug>/` — kapanmis task'lar; bitis tarihine gore.

Canonical ayrim:

- Status, Decisions Log, Open Problems -> `TASK.md`
- Verification, Risks, Notes For Claude/Codex -> `HANDOFF.md`
- Promote edilen mimari kararlar -> Vault `decisions/`

Tum task transition'lari manuel `TASK.md` edit ile yapilir. Otomatik state mutation yoktur.

## Codex Yetkisi

Codex, Active Task Layer'a yazmaz.

Bulgu, analiz veya oneriler stdout/yanit olarak donulur; gerekiyorsa Claude veya kullanici bunlari `HANDOFF.md` icindeki ilgili alana isler.

## Session Baslangic Protokolu

Bir kullanici sorusu veya task geldiginde:

1. `docs/active/CURRENT.md` oku.
2. Listelenen task'lardan kullanici sorusuyla alakali olani sec.
3. Tek aktif task varsa otomatik secilebilir.
4. Birden fazla alakali task varsa kullaniciya sor.
5. Hicbiri uymuyorsa active layer'i atla.
6. Secilen task icin `docs/active/<slug>/TASK.md` ve `docs/active/<slug>/HANDOFF.md` oku.
7. Vault sorgusu gerekiyorsa `/root/otomaix-brain/index.md` ve ilgili wiki sayfalarini oku.
8. Sonra cevap ver veya aksiyon al.
<!-- END CODEX-DISTILLED -->
