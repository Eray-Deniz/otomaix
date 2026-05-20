---
title: spec-claude-codex Komutu — plan-claude-codex rename + akış refactor
status: spec-approved
date: 2026-05-20
tags: [tooling, workflow, claude, codex, slash-command]
codex_review_status: approved
codex_review_iterations: 1
codex_review_log: docs/reviews/codex/2026-05-20-spec-claude-codex-command.md
---

# spec-claude-codex Komutu

## 1. Goal / Problem Statement

`/plan-claude-codex` komutu adıyla davranışı çelişiyor: "plan" diyor ama
aslında **spec/tasarım dokümanı** üretiyor; gerçek implementation planını
`/write-plan` yapıyor. Bu hem isimlendirmeyi yanlış yapıyor hem de
`/write-plan` ile rol ayrımını bulanıklaştırıyor. Ayrıca Claude–Codex
Aktif Task Layer (2026-05-19) canlıya alındı; komut bu katmanla henüz
entegre değil.

Bu spec iki şeyi tasarlar:

1. Komutu `spec-claude-codex` olarak yeniden adlandırma + eski adı
   deprecated stub olarak koruma (referans bütünlüğü).
2. Bu seansta kararlaştırılan akış delta'larını yeni canonical komuta
   işleme (active layer entegrasyonu, sayaç refactor'u, consistency
   sweep, frontmatter lifecycle, resume mantığı).

**Başarı kriteri:** `/spec-claude-codex <fikir>` çalışır; eski `/plan-claude-codex`
stub olarak yönlendirir; 8 dosyadaki 13 referansın hiçbiri dangling olmaz;
`rg plan-claude-codex` yalnızca kasıtlı kalan referansları (stub + donmuş
tarihi docs + vault) gösterir.

## 2. Karar Özeti

| # | Karar |
|---|---|
| 1 | **Rename + stub:** yeni canonical `spec-claude-codex.md`; eski `plan-claude-codex.md` silinmez, deprecated stub'a çevrilir |
| 2 | **Korunan mekanikler:** Codex çağrı pattern'i `plan-claude-codex.md` Adım 1b+3'ten korunur — **adversarial review scope seçimi hariç** (miras bug, §3 İstisna / Bulgu 2); gerisi yeniden yazılmaz (transcription drift önlemi) |
| 3 | **Active layer entegrasyonu:** Adım 0 koşullu active context read; Codex prompt'una active task özeti; Adım 11 active task hatırlatması |
| 4 | **Sayaç refactor:** `TURN` → `full_design_iteration_count` (yalnız temel tasarım değişiklikleri sayar) + ayrı `targeted_consistency_fix_count` |
| 5 | **Sayaç kaynağı:** frontmatter source-of-truth; girişte okunur (resume güvenli) |
| 6 | **Consistency sweep:** tek checklist, iki kullanım noktası (Codex öncesi + final onay öncesi) |
| 7 | **Frontmatter lifecycle:** draft'ta `status: draft` + `codex_review_*`; finalde `status: spec-approved` |
| 8 | **Codex log path:** `docs/reviews/codex/YYYY-MM-DD-<slug>.md` (tarih önekli, `docs/` geneliyle uniform) |
| 9 | **Sayım sınırı:** conservative — temel tasarıma dokunan bulgu wording'le başlasa bile `full_design_iteration` |
| 10 | **Vault promotion YOK:** bu komutta yapılmaz, `/commit` / closure P1 akışına bırakılır |
| 11 | **Tarihi docs dokunulmaz:** 2026-05-19 spec/plan o günün kaydı; stub onları geçerli tutar |
| 12 | **Vault güncellemesi ayrı, onaylı adım:** bu spec'in scope'u dışında (sadece referans) |

## 3. Korunan Mekanikler

Aşağıdakiler `~/.claude/commands/plan-claude-codex.md`'den korunur —
yeniden yazılmaz, kaynak dosyadan alınır (İlke 1: transcription drift
önlemi). **Bir istisna var:** adversarial review scope seçimi (bkz.
aşağıdaki İstisna notu / Bulgu 2):

- Dinamik `codex-companion.mjs` bulma (`find` ile, hardcoded sürüm yok;
  fallback `~/.claude` taraması)
- `node "$COMPANION" task --fresh --wait --cwd "$PROJECT_ROOT" "<prompt>"`
  (ön-scoping, read-only sandbox — `--write` YOK)
- Prompt **positional argüman** olarak verilir (`--prompt` flag'i değil)
- `--cwd "$PROJECT_ROOT"` (`git rev-parse --show-toplevel || pwd`) →
  proje kökündeki `AGENTS.md` otomatik yüklenir
- `node "$COMPANION" adversarial-review ...` (purpose-built, read-only
  hardcoded)
- Codex çıktısı **verbatim** gösterilir + audit log'a append edilir
- Manuel mod: her aşamada (1, 3, 7) kullanıcı kararı; otomatik döngü yok
- Skill chain override: `superpowers:brainstorming` içindeki auto-chain
  sub-skill'leri (`using-git-worktrees`, otomatik `write-plan`) görmezden
  gelinir; brainstorm yalnız spec üretimi için kullanılır

**Kaynak referansı:** `~/.claude/commands/plan-claude-codex.md` Adım 1b
(satır ~45-98) ve Adım 3 (satır ~159-204). Yeni dosyayı yazarken bu
blokları kopyala, sadece self-reference'ı (`/plan-claude-codex` →
`/spec-claude-codex`) değiştir.

**İstisna (miras bug düzeltmesi):** Adversarial review'ın **scope seçimi**
birebir korunmaz — kaynak mekanikteki `--base HEAD~1` sessiz fallback'i bir
bug'dır (Codex review Bulgu 2: HEAD~1, spec değişikliğinin tam da son
commit'te olduğunu varsayar; yanlış diff'i sessizce inceleyebilir). Yeni
komut bunun yerine spec içeriğini doğrudan review eder; bkz. Adım 6.

## 4. Akış

### Adım 0: Active Context Read (koşullu)

- `docs/active/CURRENT.md` yoksa veya boşsa (`_(no active tasks)_`) →
  sessizce atla.
- Varsa, **active-layer session-start protokolünü** izle:
  - Listede fikirle ilgili tek task varsa → otomatik seç
  - Birden fazla ilgili task varsa → kullanıcıya sor (numbered list)
  - Hiçbiri fikirle ilgili değilse → active layer'ı atla
- Seçilen task için `docs/active/<slug>/TASK.md` + `HANDOFF.md` oku.
- Bu dosyalar **sadece bağlam**; komut bunları değiştirmez.

### Adım 1: Fikri Teslim Al

`$ARGUMENTS` doluysa fikir olarak kullan. Boşsa sor:
> "Hangi fikir/özellik için tasarım istiyorsun? Tek-iki cümlelik özet ver."

`<IDEA>` olarak sakla.

### Adım 1.5: Giriş / Resume Kontrolü

Fikir alındıktan hemen sonra çalışır — slug henüz üretilmediği için
eşleştirme slug ile değil, **açık statü taraması + kullanıcı onayı** ile
yapılır. `docs/specs/` altında `status: draft` **veya**
`codex_review_status: pending` olan spec'leri tara:

- Açık spec(ler) varsa ve fikir bunlardan biriyle örtüşüyor olabilirse →
  başlıklarını listele, sor: "Bu fikir şunlardan birinin devamı mı, yoksa
  yeni mi?" Devam → seçilen `<SPEC_PATH>` ile çalış, sayaçları
  frontmatter'dan oku.
- Kullanıcı `status: spec-approved` bir spec'i devam ettirmek isterse →
  reopen **atomiktir** (Bulgu 3): "Bu spec approved. Review'ı yeniden açmak
  status'u `spec-approved → draft` geri çevirir. Onaylıyor musun?" diye tek
  onay sor.
  - Onaylanırsa **aynı atomik geçiş**: `status: spec-approved → draft` +
    `codex_review_status: approved|approved-by-iteration-limit → pending`.
    Yeni status icat edilmez; "approved + pending" çelişkili ara durumu
    **asla** oluşmaz.
  - Reddedilirse reopen yapılmaz; spec `spec-approved` kalır.
- Açık spec yok veya kullanıcı "yeni" derse → yeni akış (Adım 2).

### Adım 2: Ön-Scoping (Claude + Codex paralel)

- **Claude:** 2-3 çözüm yaklaşımı, en büyük 3 risk/bilinmez, brainstorm
  öncesi 3 kritik soru (8-12 satır).
- **Codex:** read-only companion task çağrısı (§3 Korunan Mekanikler).
  Prompt'a enjekte edilenler:
  - `IDEA`
  - **Active task özeti** (Adım 0'da bulunduysa — format §5.2):
  - Son Claude session kararları (max 5 bullet)
  - "AGENTS.md auto-loaded", "Do NOT modify files", "RESEARCH ONLY"
  - İstenen çıktı: alternatifler, riskler, netleştirme soruları

### Adım 3: Kullanıcı Yön Seçer

İki perspektif yan yana gösterilir. `AskUserQuestion`:
- Claude yaklaşımı / Codex yaklaşımı / sentez / yeniden çerçevele
- "Yeniden çerçevele" → Adım 1'e dön.

### Adım 4: Brainstorm ile Spec Draft

`Skill` tool ile `superpowers:brainstorming`, **yalnız spec üretimi** için.
Çıktı path'i (skill default override): `docs/specs/YYYY-MM-DD-<slug>.md`.

Draft frontmatter:
```yaml
---
title: <başlık>
status: draft
date: YYYY-MM-DD
tags: [...]
codex_review_status: pending
codex_review_iterations: 0
codex_review_log: docs/reviews/codex/YYYY-MM-DD-<slug>.md
---
```

`full_design_iteration_count = 0`, `targeted_consistency_fix_count = 0`
(frontmatter `codex_review_iterations` source-of-truth).

### Adım 5: Consistency Sweep (Codex öncesi)

§5 checklist'i çalıştır. Bulunan targeted fix'ler uygulanır,
`targeted_consistency_fix_count` artırılır. Temel tasarım sorunu çıkarsa
Adım 4'e (brainstorm refine) dönülür ve `full_design_iteration_count`
artar.

### Adım 6: Codex Adversarial Review

- **Birincil hedef: `<SPEC_PATH>` içeriği doğrudan.** Tek-spec review'da
  source-of-truth dosyanın kendisidir; prompt "Focus on <SPEC_PATH>" der ve
  Codex dosyayı read-only sandbox'ta okur (git diff'e bağımlı değil).
- Scope flag'i ikincil: `git status --short <SPEC_PATH>` uncommitted ise
  `--scope working-tree`. **`--base HEAD~1` sessiz varsayımı KULLANILMAZ**
  (Bulgu 2 — miras bug).
- Spec commit'li ve working-tree temizse: kullanıcıdan **açık base/ref**
  iste (örn. spec commit hash'i); inferans yapma. Kullanıcı vermezse dosya
  içeriği doğrudan (diff'siz) review edilir.
- `node "$COMPANION" adversarial-review` çağrısı (kaynak mekanik §3; **scope
  seçimi hariç** — bu nokta miras bug nedeniyle iyileştirildi, bkz. yukarı).
- Çıktı **verbatim** gösterilir + `docs/reviews/codex/YYYY-MM-DD-<slug>.md`
  içine turn başlığıyla append edilir.

### Adım 7: Karar — Onayla / Güncelle

`full_design_iteration_count < 3` ise iki seçenek:
- **Onayla** → Adım 9 (final sweep)
- **Spec'i güncelle** → critical/high bulgular özetlenir (medium/low audit
  log'da kalır), kullanıcı ek girdi verir, brainstorm refine, Adım 6'ya
  dön. Değişiklik temel tasarıma dokunuyorsa `full_design_iteration_count`
  artar (§5.1 sayım kuralı).

`full_design_iteration_count >= 3` ise (limit dolu — `==` değil `>=`:
resume'da elle değişmiş frontmatter sayacı 3'ü aşmış olabilir):
- **Onayla** → `codex_review_status: approved-by-iteration-limit`
- **Kabul etmem** → unresolved kararlar listelenir + yeni scoped
  `/spec-claude-codex` önerilir.

### Adım 8: (Sayaç — Adım 5/7'ye gömülü)

Sayaç mantığı ayrı adım değil; Adım 5 ve 7'de işletilir. Burada referans
için: bkz. §5.1.

### Adım 9: Final Consistency Sweep

§5 checklist'i tekrar çalıştır (onay öncesi zorunlu). Küçük düzeltmeler
uygulanır (`targeted_consistency_fix_count` artar). **Yeni temel karar
açılırsa** spec approve edilmez — kullanıcıya dönülür (Adım 7).

### Adım 10: Finalizasyon

Frontmatter:
```yaml
status: spec-approved
codex_review_status: approved        # veya approved-by-iteration-limit
codex_review_iterations: <full_design_iteration_count>
codex_review_log: docs/reviews/codex/YYYY-MM-DD-<slug>.md
```

### Adım 11: Active Task Hatırlatması

Adım 0'da ilgili active task bulunduysa:
> "Spec final kararlarını TASK.md Decisions Log / Open Problems'a
> işleyelim mi?"

- **Vault promotion bu komutta YAPILMAZ** — `/commit` veya closure P1
  akışına bırakılır.
- Yeni active task **yaratılmaz** — task yaratımı `/write-plan`'a aittir
  (active-layer spec §6.1).

### Adım 12: Final Rapor

```
Spec final.
- Path: docs/specs/YYYY-MM-DD-<slug>.md
- Codex review log: docs/reviews/codex/YYYY-MM-DD-<slug>.md
- Full design iterations: N/3
- Targeted consistency fixes: M
- Status: spec-approved
- Codex review status: approved | approved-by-iteration-limit
- Sonraki adım: /write-plan docs/specs/YYYY-MM-DD-<slug>.md
```

## 5. Consistency Checklist

### 5.1 Sayım Kuralı (conservative)

- **`full_design_iteration_count` artar:** değişiklik wording/path/
  frontmatter düzeltmesi gibi başlasa bile **schema, lifecycle, mimari
  model, komut entegrasyon stratejisi veya Claude/Codex/vault rol
  ayrımına** dokunuyorsa. Limit 3.
- **`targeted_consistency_fix_count` artar:** temel tasarım kararına
  dokunmayan net düzeltmeler (path, frontmatter, wording, wikilink/
  referans, çelişen cümle temizliği). Limiti yok; final raporda gösterilir.
- Sınır vakası kuralı: bir bulgu ikisine de dokunuyorsa → conservative,
  `full_design_iteration` sayılır.

### 5.2 Checklist (tek liste, iki kullanım noktası: Adım 5 + Adım 9)

**Genel (her zaman):**
- [ ] Summary / decisions / schema / lifecycle / implementation notes
      aynı kararları mı söylüyor? (iç tutarlılık)
- [ ] Path, komut, flag, dosya adları birebir doğru mu? (referans
      bütünlüğü)
- [ ] Repo / vault / global ayrımı doğru mu?
- [ ] Kullanıcı onayı gereken yerde otomatik işlem var mı?
- [ ] Out-of-scope, kararlarla çelişiyor mu?
- [ ] (status, codex_review_status) çifti izinli mi? İzinli:
      `draft+pending`, `spec-approved+approved`,
      `spec-approved+approved-by-iteration-limit`. Yasak:
      `spec-approved+pending` (çelişkili final / açık-review durumu — Bulgu 3).

**Koşullu (konu workflow / active-layer / agent-rol / vault entegrasyonu
ise — Claude konudan yargılar, şüphede çalıştır):**
- [ ] Codex read-only kuralı korunuyor mu?
- [ ] Active state vault'a konmuyor mu?
- [ ] TASK.md / HANDOFF.md canonical ayrımı karışıyor mu?
- [ ] CURRENT.md sadece pointer/memo mu (status değil)?

### 5.3 Active Task Özeti — Codex Prompt Formatı

Adım 2'de Codex prompt'una eklenir (aktif task yoksa blok hiç eklenmez),
max 5 bullet:
```
Active task (context only, do not modify):
- Task: <title> (<status>)
- Goal: <1 satır>
- Open Problems: <sayı> — <en kritik 1>
- Son kararlar: <Decisions Log'dan max 2 bullet>
```

## 6. Stub Tasarımı

`~/.claude/commands/plan-claude-codex.md` tamamen aşağıdakiyle değiştirilir
(mevcut içerik yeni dosyaya taşındıktan **sonra**):

```markdown
---
description: "[DEPRECATED] use /spec-claude-codex"
argument-hint: <fikir cümlesi>
---

## Deprecated

Bu komut `spec-claude-codex` olarak yeniden adlandırıldı.

Yeni kullanım:
`/spec-claude-codex <fikir>`

Bu komut spec/tasarım dokümanı üretir, implementation planı **değil**.
Spec final olduktan sonra: `/write-plan <SPEC_PATH>`

(Eski ad referans bütünlüğü için stub korunuyor — vault `sources:` ve
2026-05-19 tarihli dokümanlar buraya işaret ediyor. Silme.)
```

## 7. Blast-Radius & Uygulama Sırası

`rg plan-claude-codex` ile doğrulanan **8 dosya / 13 satır eşleşmesi**, 3
güven bölgesi (kaynak `plan-claude-codex.md`'nin 1 self-reference'ı hariç —
o, rename'le yeni dosyada düzeltilir):

| Bölge | Dosya:satır | İşlem |
|---|---|---|
| **Canlı komut** | `handoff.md:41,58` · `sync-agents-md.md:170` · `init.md:120,135` | Yeni ada güncelle |
| **Repo docs (donmuş)** | `plans/2026-05-19-...:93,311,328` · `specs/2026-05-19-...:514` | **Dokunma** (tarihi kayıt; stub geçerli tutar) |
| **Vault (canonical)** | `log.md:8` · `decisions/2026-05-19-...:64` · `codex-entegrasyonu.md:9,95` | **Ayrı onaylı adım** (bu spec scope dışı) |

Hiçbir referans komutu programatik **çağırmıyor** — hepsi doküman/pattern
anması. Fonksiyonel kırılma yok, sadece referans bütünlüğü riski.

### Uygulama sırası (plan'a gidecek)

1. Eski içerikten yeni `~/.claude/commands/spec-claude-codex.md` yaz
   (korunan mekanikler + §4 akış + §5 checklist + §6 lifecycle).
2. `plan-claude-codex.md`'yi §6 stub'ına çevir.
3. Canlı komut referanslarını güncelle: `handoff.md`, `sync-agents-md.md`,
   `init.md` + yeni dosyadaki self-reference.
4. Tarihi repo docs'a **dokunma**.
5. `rg plan-claude-codex` ile doğrula: yalnız stub + donmuş tarihi docs +
   vault kalmalı.
6. **Vault ayrı adım:** `codex-entegrasyonu.md` `sources:` → yeni dosya;
   `decisions/2026-05-19:64` workflow satırı → yeni ad; `log.md` tarihsel,
   dokunulmaz. `last-verified` bump + kullanıcı onayı; Codex vault'a yazmaz.

### Rollout Gate (Definition of Done)

Rename **"canonical rollout tamamlandı" sayılmaz** ta ki vault referansları
(`codex-entegrasyonu.md` canonical command referansı + `sources:`,
`decisions/2026-05-19:64` workflow satırı) güncellenip `last-verified` bump
ile **doğrulanana** kadar (Bulgu 1). CLAUDE.md "bilgi sorgusu önce vault"
der; vault eski adı canonical gösterdiği sürece rollout **partial**'dır.
Stub referans bütünlüğünü sağlar ama **canonical doğruluk için yeterli
sayılmaz**. O ana dek `/spec-claude-codex` "çalışan canonical"dır ama iş
**done değildir**: repo/komut ve vault ayrı commit'lerde yapılır, ama ikisi
de bitip doğrulanmadan task closure (`/finish-branch`) tetiklenmez.

## 8. Out-of-Scope

| Konsept | Neden |
|---|---|
| Vault yazımı | Komut implementasyon commit'inin **dışında**; fakat rollout closure gate'inin parçası (bkz. §7 Rollout Gate) — last-verified + referans bütünlüğü disiplini |
| Tarihi docs düzenleme | 2026-05-19 spec/plan o günün kaydı; geçmişi yeniden yazma |
| Aktif task layer cancelled-path test gap | Ayrı, ilgisiz iş |
| `/write-plan` veya diğer komutlarda değişiklik | Bu komut self-contained; rol ayrımı zaten net |

## 9. Test / Verification

- `/spec-claude-codex <dummy fikir>` → Adım 0-12 yürür, spec
  `docs/specs/` altına yazılır, Codex log `docs/reviews/codex/YYYY-MM-DD-`
  önekiyle oluşur.
- CURRENT.md boşken Adım 0 sessizce atlanır.
- Birden fazla active task varken Adım 0 kullanıcıya sorar.
- Yarım draft'a yeniden çağrı → resume sorusu; approved spec'e → reopen
  sorusu.
- `/plan-claude-codex` çağrısı → stub yönlendirmesi gösterir, akış
  yürütmez.
- `rg plan-claude-codex`: yalnız kasıtlı kalan referanslar (stub gövdesi +
  donmuş tarihi docs + vault).

## 10. İlgili Belgeler

- `~/.claude/commands/plan-claude-codex.md` — kaynak mekanik (rename
  öncesi son hali)
- `docs/specs/2026-05-19-claude-codex-aktif-katman.md` — active layer spec
  (session-start protokolü, vault promotion P1)
- `[[codex-entegrasyonu]]` — Codex CLI sync sistemi (vault, ayrı adımda
  güncellenecek)
- `~/.claude/commands/{write-plan,handoff,sync-agents-md,init}.md` — komşu
  komutlar
