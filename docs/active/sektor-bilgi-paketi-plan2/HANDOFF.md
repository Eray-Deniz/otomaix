---
task: sektor-bilgi-paketi-plan2
written: 2026-08-27
---

# Resume From

**Plan 2'nin planını yazmaya başla.** Hazırlık bitti, karar turu kapandı; elde plan yazımı
için gereken her şey var.

İlk hamle: `/write-plan-claude-codex docs/specs/2026-08-21-sektor-bilgi-paketi.md` —
Plan 2 kapsamı (işletim hattı) için.

**Plan yazımına girmeden ÖNCE oku (sırayla):**
1. `docs/research/2026-08-27-plan2-karar-turu.md` — 13 kapanmış karar + planın bağlayacağı
   30 teknik kalem listesi
2. `docs/research/2026-08-27-spec-input-bosluk-raporu.md` — spec'in eksik taşıdıkları
3. `docs/plans/2026-08-23-sektor-bilgi-paketi.md` → "Plan 2'ye teslim edilen arayüzler"

**Resume ipucu:** `/write-plan-claude-codex`'in Adım 3 keşif algoritması Plan 1'i aynı
spec'e bağlı bulup "yeniden aç" dalına düşürür. **Düşme** — Plan 1 kapandı ve arşivde;
Plan 2 yeni plandır. Yeni dosya: `docs/plans/2026-08-<gün>-sektor-bilgi-paketi-plan2.md`
(Plan 1 ile aynı slug, farklı tarih ve `-plan2` eki — çakışma yok).

# Verification

**Koşulan komutlar ve taze çıktıları:**
- `sha256sum` + `tail -n +7 | sha256sum` → repodaki spec-input kopyası araştırma
  deposundaki asılla **bayt-özdeş** (`efe2170…b50b4d`). Doğrulandı 2026-08-27.
- §17 kart ayıklayıcı → **162/162 kart**, belgenin kendi alt bölüm sayılarına karşı
  doğrulandı (39+36+51+36). İlk sürüm 156 vermişti; harf ekli kimlikler (`K-01a`,
  `K-04a-d`, `K-01b`) desene uymuyordu, düzeltildi.
- Kimlik eşleştirme → 162 karttan **32'si spec'e hiç geçmemiş**. `K-04b/c/d` ilk sayımda
  eksik görünmüştü; spec `K-04a–d` aralık yazımı kullanıyor, kapsanıyorlar.
- Kapanış dedektörü → **pozitif kontrol koşuldu**: elle doğrulanmış 35 kapalı + 23 açık
  kimlikte **0 yanlış pozitif**, 3 yanlış negatif (K-69 · K-70 · K-144 — kapanış işareti
  kimlikten önce yazılmış), üçü elle istisna olarak eklendi.
- Codex ön-analizi → `run_codex_scan "task-fresh" task --fresh`, rc=0. Log:
  `~/.claude/logs/otomaix--ffc87809/2026-08-27-sektor-bilgi-paketi-plan2.md`

**Denenmemiş senaryolar:**
- Plan 1 bölümlerinin (spec §1-7, §10-12, §14, §16-17) **kart geçişi koşulmadı** — yalnız
  kimlik geçişi kapsadı. Yeniden açılma koşulu boşluk raporunda yazılı.
- Girdinin §17 dışındaki gövde metniyle spec arasında **karar-dışı içerik** karşılaştırması
  yapılmadı; tarama karar-kartı eksenlidir.
- **Hiçbir kod çalıştırılmadı, hiçbir test koşulmadı** — bu oturum tamamen doküman işiydi.

# Risks

- **Aynı sürüklenme plan yazımında tekrarlanabilir.** Spec eksik taşımış olabilir;
  bir sözleşme ayrıntısını spec'te bulamazsan **girdiye dön** — girdi kanonik.
- **Codex ön-analizinin iki uyarısı planda karşılanmalı:** (a) §8.7'nin beş sözleşme
  düzeltmesi aslında **en az altı** — spec §12.2 kanal anahtar uzayının dört değerle
  kapatılması eklenmeli; (b) 033/034 migration'larının down script'i yok, yeni
  migration'larda geri alma "git revert" değil.
- **Kapsam büyük ve tek planda yazılacak.** Yalın plan sözleşmesi disiplini kritik:
  operasyonel derinlik yazma, her ayrıntı review saldırı yüzeyi.
- Motor kuralları ilk kez canlı turda sınanacak (kuru mod kurulmayacak); kurtarma yolu
  K-145'in vaka bazlı geri alması.

# Notes For Claude/Codex

- **Karar sorusu sormadan önce spec-input + spec + kaynak sözleşme dosyalarını kontrol et.**
  Bu oturumda K-84 yanlış çerçevelendi ve iki tur boşa gitti; sonra soru listesi kartların
  "karar sahibi" sütunundan kuruldu, 21 çıktı — oysa "Spec'i bloklar mı?" sütununa
  bakılsaydı baştan 3 çıkacaktı.
- **Karar sorularının altına somut akış/senaryo düzeyinde mimari özet geç** (Eray talimatı).
- Codex'in reddedilen önerisi: kademeli bölme. **Kuralı korundu:** sentez tek başına DB'ye
  `draft` yazamaz; kanonik sıra sentez → motor → draft.
- Codex'in benimsenen önerileri: sözleşme dosyaları araştırma deposunda kalsın (kopya
  alınmasın, pin manifesti tutulsun); `~/.claude/commands/` yalnız ince adaptör olsun.
