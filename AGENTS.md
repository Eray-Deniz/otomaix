# AGENTS.md

> Bu dosyanın marker'lı bloğu `/sync-agents-md` komutu tarafından
> Codex'in CLAUDE.md damıtması ile üretilir. Marker dışına manuel
> içerik ekleyebilirsin — korunur.

<!-- BEGIN CODEX-DISTILLED -->
> Bu içerik Codex CLI için /root/otomaix/CLAUDE.md'den damıtılmıştır.

## Proje Özeti

Otomaix, ortak altyapı üzerinde çalışan AI otomasyon uygulamalarının monorepo’sudur.

## Bilgi Kaynakları

Mimari, karar, vendor veya geçmiş bilgisi sorularında önce `/root/otomaix-brain/index.md` kontrol edilmelidir.

İlgili wiki sayfası bulunup okunmalı ve yanıtlarda `[[wikilink]]` citation kullanılmalıdır.

Vault’ta bilgi yoksa veya güncel değilse şu sıra izlenir:

1. Kod
2. Memory
3. `docs/_archive/`

Vault canonical kaynaktır. Eski mimari dokümanlar, including `docs/00-platform-mimari.md`, arşivlenmiştir.

## Uygulama Bazlı Kurallar

Aşağıdaki uygulamaların kendi `CLAUDE.md` dosyaları vardır:

- `apps/social/backend`
- `apps/social/frontend`
- `apps/crm`

Bu dizinlerde çalışırken ilgili uygulamanın proje talimatları ayrıca okunmalı ve uygulanmalıdır.

## Proje Talimat Dosyalarında Drift Koruması

`CLAUDE.md` türü proje talimat dosyaları yalnızca şu bilgileri içermelidir:

- Proje yapısı
- Ortam bilgileri
- Deploy bilgileri
- Konvansiyonlar

Kayıtların canonical yerleri:

- Sprint geçmişi: git commit’leri
- Kararlar: `/root/otomaix-brain/decisions/`
- Aktif çalışma durumu: task sistemi
- Changelog: oluşturulmaz

## Çapraz Uygulama Kuralları

- CRM, `social` schema’sını yalnızca okuyabilir; yazamaz.
- Frontend ile Backend arasındaki tek API gateway `api.otomaix.com` adresidir.
- CRM, PostgreSQL’e doğrudan bağlanır; CRM için API katmanı yoktur.
- Migration dosyaları `shared/db/migrations/` altında numaralandırılmış sırayla tutulur.
- n8n workflow değişiklikleri `shared/n8n-workflows/` altına JSON export olarak eklenir.

## Aktif Task Katmanı

Canlı task durumu ve oturumlar arası devir teslim için repo içindeki aktif task katmanı kullanılır.

Ayrıntılı tanım:

- `docs/specs/2026-05-19-claude-codex-aktif-katman.md`

Path konvansiyonları:

- `docs/active/CURRENT.md`: aktif task pointer’ı
- `docs/active/<slug>/TASK.md`: canonical task durumu, kararlar ve açık problemler
- `docs/active/<slug>/HANDOFF.md`: rolling session-boundary devir teslim
- `docs/task-archive/YYYY/MM/<slug>/`: tamamlanan task arşivi

Canonical içerik ayrımı:

- Status, Decisions Log ve Open Problems: `TASK.md`
- Verification, Risks ve Notes For Claude/Codex: `HANDOFF.md`
- Kalıcı mimari kararlar: Vault içindeki `decisions/`

Task durum geçişleri manuel `TASK.md` düzenlemeleriyle yapılır; otomatik state mutation yoktur.

## Codex Yetki Sınırı

Codex, Active Task Layer dosyalarına yazmaz.

Bulgular, analizler ve öneriler stdout veya kullanıcı yanıtı olarak döndürülür. Gerekiyorsa başka bir yetkili aktör bunları `HANDOFF.md` içine işler.

## Oturum Başlangıç Protokolü

Her kullanıcı sorusu veya görevi için:

1. `docs/active/CURRENT.md` okunur.
2. Listelenen task’lardan kullanıcı talebiyle ilgili olan seçilir.
3. Tek ilgili aktif task varsa otomatik seçilebilir.
4. Birden fazla ilgili task varsa kullanıcıdan seçim istenir.
5. Hiçbir task ilgili değilse aktif task katmanı atlanır.
6. Seçilen task’ın `TASK.md` ve `HANDOFF.md` dosyaları okunur.
7. Vault sorgusu gerekiyorsa `/root/otomaix-brain/index.md` ve ilgili wiki sayfaları okunur.
8. Ardından yanıt verilir veya istenen işlem gerçekleştirilir.
<!-- END CODEX-DISTILLED -->
