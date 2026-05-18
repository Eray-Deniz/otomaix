# AGENTS.md

> Bu dosyanın marker'lı bloğu `/sync-agents-md` komutu tarafından
> Codex'in CLAUDE.md damıtması ile üretilir. Marker dışına manuel
> içerik ekleyebilirsin — korunur.

<!-- BEGIN CODEX-DISTILLED -->
> Bu icerik Codex CLI icin /root/otomaix/CLAUDE.md'den damitilmistir.

## Proje Ozeti

Otomaix, ortak altyapi ustunde calisan AI otomasyon uygulamalarinin monorepo'sudur.

## Bilgi Kaynagi Sirasi

Mimari, karar, vendor veya gecmis bilgi sorularinda once `/root/otomaix-brain/index.md` kontrol edilmelidir.

Ilgili wiki sayfasi bulunup oradan okunmali; cevaplarda `[[wikilink]]` citation kullanilmalidir.

Vault'ta bilgi yoksa veya guncel degilse sira su sekildedir:

1. Kod
2. Memory
3. `docs/_archive/`

Vault canonical kaynaktir. Eski mimari dokumanlar, including `docs/00-platform-mimari.md`, arsive tasinmistir; mimari bilgi icin vault esas alinmalidir.

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

Bu dosyalara sprint logu, aktif is kaydi, karar gecmisi veya changelog eklenmemelidir.

Kayit yerleri:

- Sprint loglari: git commit
- Kararlar: memory karar dosyalari
- Aktif is: oturum ici task takibi
- Changelog: yazilmaz

## Capraz App Kurallari

- CRM, `social` schema'yi yalnizca okur; yazmaz.
- Frontend -> Backend iletisiminde tek API gateway kullanilir: `api.otomaix.com`.
- CRM -> PostgreSQL direkt baglanir; CRM icin API katmani yoktur.
- Migration dosyalari `shared/db/migrations/` altinda numaralandirilmis sirayla tutulur.
- n8n workflow degisiklikleri `shared/n8n-workflows/` altina JSON export olarak eklenir.
<!-- END CODEX-DISTILLED -->
