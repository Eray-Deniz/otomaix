---
title: Claude–Codex Aktif Task Layer
status: spec-approved
date: 2026-05-19
tags: [tooling, workflow, claude, codex, brain]
---

# Claude–Codex Aktif Task Layer

## 1. Goal / Problem Statement

Otomaix'te Claude Code (canonical writer) ve Codex CLI (read-only reviewer)
birlikte çalışıyor. Şu an aralarında **devir teslim** ve **canlı task
state** için kalıcı bir mekanizma yok:

- `docs/plans/...md` statik — initial plan var, "hangi adımdayım, neye
  takıldım" yok.
- Oturum içi Task'lar ephemeral; yeni session açıldığında kaybolur.
- Codex'in conversation history aktarımı yok (`[[codex-entegrasyonu]]`).
- Açık problemler ve in-flight kararlar için kalıcı yer yok — sadece
  commit mesajı, kullanıcı kafası veya oturum içi Task.
- Codex session başlangıç protokolünde "active task varsa onu da oku"
  satırı yok.

Bu spec, bu boşlukları doldurmak için **aktif task layer** tasarlıyor.
Mevcut vault (`/root/otomaix-brain/`) ve slash command ekosistemi
korunur; üstüne hafif bir overlay eklenir.

**Out-of-scope:** Aşağıdaki tasarım kararları **bilinçli olarak**
yapılmadı (YAGNI):

- `issues.md` ayrı dosyası — Open Problems TASK.md içinde.
- Otomatik hook'lar — manuel mod felsefesi.
- Append-only journal mode — git zaten history sağlar.
- Branch-based discovery — CURRENT.md pointer daha esnek.
- Kapsamlı INDEX.md (archive için) — klasör yapısı yeterli.

## 2. Design Decisions Summary

| # | Karar |
|---|---|
| 1 | **Lokasyon:** A) Split — vault `/root/otomaix-brain/` (kalıcı) + repo `docs/active/` (geçici) |
| 2 | **Discovery:** `CURRENT.md` pointer (branch-agnostic) |
| 3 | **Task struct:** klasör per task — `TASK.md` + `HANDOFF.md` |
| 4 | **Archive:** `docs/task-archive/YYYY/MM/<slug>/` (bitiş tarihine göre) |
| 5 | **CURRENT.md:** liste + insan memo (status değil) |
| 6 | **TASK.md schema:** Lean + References (5 bölüm) |
| 7 | **Status set:** proposed \| active \| blocked \| waiting-review \| done \| archived \| cancelled |
| 8 | **HANDOFF.md schema:** rolling + 7 section |
| 9 | **Workflow integration:** Z hibrit — slash command'lere hatırlatma |
| 10 | **HANDOFF dokunma noktaları:** session-boundary, blocker, review, closure (/commit'te değil) |
| 11 | **/handoff komutu:** default Claude tek; `--with-codex` Codex read-only review |
| 12 | **Vault promotion:** P1 (Claude candidate listeler + kullanıcı seçer + Claude yazar) |
| 13 | **Promote heuristic:** mimari/workflow/path/vendor/cross-app/recurring → candidate |
| 14 | **Canonical ayrım:** Status & Decisions Log & Open Problems = TASK.md; Verification & Risks & Notes = HANDOFF.md |

## 3. File & Folder Layout

### Repo (`/root/otomaix/`)

```
docs/
├── active/                          # canlı task state
│   ├── CURRENT.md                   # pointer + insan memo (her zaman var)
│   ├── <task-slug>/
│   │   ├── TASK.md                  # goal, references, status, open problems, decisions
│   │   └── HANDOFF.md               # rolling session-boundary devir teslim
│   └── ...
│
├── task-archive/                    # kapanmış task'lar (bitiş tarihine göre)
│   └── YYYY/MM/<task-slug>/
│       ├── TASK.md
│       └── HANDOFF.md
│
├── specs/                           # mevcut — değişmez
├── plans/                           # mevcut — değişmez
├── reviews/                         # mevcut — değişmez
├── debug-logs/                      # mevcut — değişmez
└── security-reviews/                # mevcut — değişmez
```

### Vault (`/root/otomaix-brain/`)

Vault dokunulmaz. Sadece **vault promotion check** akışıyla yeni karar
sayfaları (`decisions/YYYY-MM-DD-<slug>.md`) veya mevcut sayfa
güncellemeleri eklenir; bu da kullanıcı onayıyla Claude tarafından yapılır.

### Canonical ayrım

| Konsept | Canonical yer | Diğer yerde |
|---|---|---|
| **Status** | TASK.md frontmatter | CURRENT.md'de YOK (memo'da "status değil" disiplini) |
| **Open Problems** | TASK.md `# Open Problems` | HANDOFF.md'de YOK |
| **Decisions Log** | TASK.md `# Decisions Log` | HANDOFF.md'de YOK; promote edilenler vault `decisions/`'a link |
| **Verification** | HANDOFF.md `## Verification` | TASK.md'de YOK |
| **Risks** | HANDOFF.md `## Risks` | TASK.md'de YOK (kalıcı risk olursa Decisions Log'a transfer) |
| **Session-boundary notes** | HANDOFF.md `## Notes For Claude/Codex` | TASK.md'de YOK |
| **Mimari kararlar** | Vault `decisions/<slug>.md` | TASK.md Decisions Log'da link |

## 4. Schemas

### 4.1 `CURRENT.md`

Her zaman var (boş bile olsa). Format:

```markdown
# Active Tasks

- `<task-slug>/` — kısa insan memo (status değil)
- `<task-slug>/` — kısa insan memo
```

Boş hal:

```markdown
# Active Tasks

_(no active tasks)_
```

**Memo kuralı** — burada tutulabilir:
- task slug (klasör adı)
- kısa insan memo
- "dokunma", "öncelik değil", "kullanıcı bekleniyor" gibi yönlendirme

**Burada tutulmaz:**
- status (proposed/active/blocked/...)
- progress yüzdesi
- current step
- verification sonucu
- open problems
- karar logu

### 4.2 `TASK.md` — Lean + References

```markdown
---
title: <task adı>
status: active            # proposed | active | blocked | waiting-review | done | archived | cancelled
started: YYYY-MM-DD
last-touched: YYYY-MM-DD
blocked-by: null          # null veya kısa açıklama
---

# Goal

<1-3 cümle: ne yapılacak + neden + başarı kriteri.
Constraint'ler ve scope burada eritilir.>

# References

- Spec: `docs/specs/YYYY-MM-DD-<slug>.md`
- Plan: `docs/plans/YYYY-MM-DD-<slug>.md`
- Review: `docs/reviews/YYYY-MM-DD-<slug>.md` veya _(yok)_

# Current Status

<şu an nereye geldim. Freeform; plan progress burada işlenebilir:>
**Plan progress:** 3/8 adım tamam — Adım 4 başlıyor: <konu>.

# Open Problems

<açık sorunlar, engelleyiciler. Yoksa: _(yok)_>
- [ ] <problem>
- [ ] <problem>

# Decisions Log

<karar + reddedilen alternatif + neden. Tam düşünce dökümü değil.
Vault'a promote edilenler `→ Vault: [[decisions/...]]` formatıyla
işaretlenir — `[[...]]` Obsidian wikilink sentaksı, repo markdown'da
render etmez ama "Vault:" prefix'i hedefin vault olduğunu netleştirir.>
- YYYY-MM-DD: <karar> — <kısa gerekçe>; alternatif: <X>, reddetme nedeni: <Y>
- YYYY-MM-DD: <karar> → Vault: `[[decisions/2026-05-19-x]]`
```

### 4.3 `HANDOFF.md` — Rolling, 7 bölüm

```markdown
# Handoff

## Context
- Task: <task adı>
- Linked spec: `docs/specs/...`
- Linked plan: `docs/plans/...`
- Branch: <main veya feature/xxx>
- Last updated: YYYY-MM-DD HH:MM

## Current State
- Summary: <şu an nereden devam edilecek — kısa özet, TASK.md'nin tam state'i değil>
- Blocked: <evet/hayır + tek satır neden>

## Resume From
- Start here: <hangi dosya/fonksiyon/komut>
- Relevant files:
  - <file path>
  - <file path>
- Next command: <önerilen sıradaki komut, örn. /execute-plan, /review>

## Verification
- Passed: <neyi doğruladık>
- Failed: <neyi denedik geçmedi>
- Not run: <neyi doğrulayamadık — sonraki session'ın işi>

## Risks
- <bu task'a özgü ama kalıcı olmayan risk; sonraki session dikkat etsin
  seviyesi. Kalıcı mimari riske dönüşürse TASK Decisions Log veya
  vault promotion candidate olur.>

## Notes For Claude
- Codex'in özellikle dikkat çektiği bulgular:
- Claude'un sonraki session'da işlemesi gereken şeyler:
- Vault'a yazılması gerekebilecek kalıcı kararlar:
- Spec/plan güncellemesi gerektiren noktalar:
- Kullanıcıdan karar bekleyen konular:

## Notes For Codex
- Codex'in review ederken özellikle bakması gereken alanlar:
- Bilinen riskler:
- Dokunmaması gereken alanlar:
- Önce okunması gereken dosyalar:
```

**Closure modu** — task `done` veya `cancelled` olduğunda HANDOFF.md
son kez güncellenir (closure summary) ve sonrasında archive'a taşınır.
Archive'a taşındıktan sonra dokunulmaz (artık active layer'da değil;
vault'a benzer şekilde donmuş geçmiş):
- `## Current State → Summary`: "Task ne ile bitti" yazılır
- `## Resume From → Next command`: "vault promotion yapıldı / loose end yok" veya kalan iş notu
- `## Verification`: final pass/fail
- Diğer bölümler relevant kalmazsa `_(yok)_`

Yani "overwrite durur" disiplini status değişikliğiyle değil, **archive
move'uyla** devreye girer (closure akışı için bkz. §8).

## 5. Status Lifecycle

### 5.1 State Set

| Status | Anlam |
|---|---|
| `proposed` | Task tanımlandı, plan var ama henüz başlamadı |
| `active` | Üzerinde çalışılıyor |
| `blocked` | Engelleyici var, beklemede |
| `waiting-review` | İş bitti, dış review/onay bekliyor (kullanıcı, Codex, otomatik check) |
| `done` | Tamamlandı, archive'a hazır |
| `archived` | Archive'a taşındı (terminal state) |
| `cancelled` | İptal edildi (terminal state) |

### 5.2 Transition Tablosu

| Transition | Trigger | TASK | HANDOFF |
|---|---|---|---|
| (yeni) → `proposed` | `/write-plan` sonu hatırlatma | yarat (status=proposed) | yarat (boş template) |
| `proposed` → `active` | `/execute-plan` başında hatırlatma | status=active | dokunmaz |
| (in-progress) | `/commit` içinde (her plan adımı) | Current Status, last-touched | **dokunmaz** |
| `active` → `blocked` | manuel (blocker farkedildiğinde) | status=blocked, Open Problems | Notes For Claude (gerekiyorsa) |
| `active` → `waiting-review` | manuel TASK.md edit **veya** `/finish-branch` PR seçimi | status=waiting-review | manuel'de dokunmaz; PR'da rolling update ("PR #N açıldı") |
| review aktivitesi (status değiştirmez) | `/review` veya `/handoff --with-codex` sonrası | high/critical → Open Problems | Notes For Claude (review özeti) |
| `waiting-review` → `done` | manuel | status=done | closure summary |
| `done` → `archived` | `/finish-branch` sonu hatırlatma | status=archived | son hali archive'a taşınır |
| → `cancelled` | manuel | status=cancelled | closure: "neden iptal" tek satır |
| session end | `/handoff` (manuel çağrı, her zaman) | dokunmaz | full güncelleme |

### 5.3 Manuel Mod Disiplini

Tüm transition'lar manuel TASK.md edit ile yapılabilir. Slash command
hatırlatmaları sadece "unuttum" durumunu azaltan friction-low onay
soruları (1 saniyelik y/n) — otomatik state mutation **yok**.

## 6. Slash Command Integration (Z Hibrit)

Mevcut komutlar **task aware** ama **task driven değil**. Her komut
standalone çalışmaya devam eder; task layer kullanılmayan projelerde
hatırlatma "no-op" olur (CURRENT.md boşsa atlanır).

### 6.1 Mevcut Komut Değişiklikleri

| Komut | Eklenen adım |
|---|---|
| `/brainstorm` | **Değişmez** — spec yazılır, task yaratma yok (her spec implementation'a gitmez) |
| `/write-plan` | Plan yazıldıktan sonra: *"Bu plan için `docs/active/<slug>/` altında TASK.md + boş HANDOFF.md yaratayım mı?"* (y/n) — onaylı ise yaratır, CURRENT.md'ye satır ekler |
| `/execute-plan` | Başlarken: CURRENT.md'de eşleşen task varsa *"TASK.md status'u 'active' yapayım mı?"* (y/n) |
| `/commit` | Adım eklenir: (a) *"TASK.md Current Status / last-touched güncelleyelim mi?"*, (b) **Vault promotion check** çalıştırılır (bkz. §7) |
| `/review` | Tamamlanınca: (a) high/critical bulgular *"TASK.md Open Problems'a işleyeyim mi?"*, (b) review özeti *"HANDOFF.md Notes For Claude'a işleyeyim mi?"*. Status değişimi yok — `waiting-review`'a geçiş kullanıcı manuel kararı. |
| `/finish-branch` | Seçime göre task layer adımı: **PR** → `waiting-review` + rolling HANDOFF (archive yok); **merge / sil** → full closure + vault promotion + archive; **tut** → no-op (bkz. §8) |
| `/debug`, `/simplify`, `/security-review`, `/init` | **Değişmez** — task layer'a dokunmaz (gerek olursa Decisions Log'a manuel not) |

### 6.2 Yeni Komutlar

| Komut | Davranış |
|---|---|
| `/handoff` | Claude tek başına HANDOFF.md full güncelleme yapar. Aktif task seçimi: CURRENT.md'de tek varsa otomatik; birden çoksa kullanıcıya sorar. |
| `/handoff --with-codex` | 1. Claude TASK.md + HANDOFF.md okur. 2. Codex'i read-only review için çağırır (`codex-companion task --fresh --wait --cwd /root/otomaix`). 3. Codex stdout bulguları kullanıcıya gösterir. 4. Onaylı bulguları Claude HANDOFF.md "Notes For Claude" bölümüne işler. |

**Codex çağrısı opsiyonel** — default Claude yazar; `--with-codex` flag
ile devreye girer. Otomatik Codex çağrısı **yok**.

## 7. Vault Promotion Check (P1)

### 7.1 Akış

`/commit` (incremental) veya `/finish-branch` (closure) sırasında:

1. Claude TASK.md `# Decisions Log` bölümünü okur
2. Her kararı iki gruba ayırır (heuristic, §7.2):
   - `promote-candidate`
   - `task-scope-only`
3. Promote adaylarını **numbered liste** olarak kullanıcıya gösterir
4. Kullanıcı seçer: *"1 ve 3 vault'a, 2 kalsın"*
5. Seçilenler için Claude hedef önerir:
   - Yeni ADR: `decisions/YYYY-MM-DD-<slug>.md`
   - Mevcut vault sayfası güncellemesi (örn. vendor)
   - Sentez sayfası: `research/YYYY-MM-DD-<slug>.md`
6. Kullanıcı onayı sonrası Claude vault'a yazar
7. Promote edilen karar TASK.md Decisions Log'da `→ Vault: [[decisions/...]]`
   formatıyla işaretlenir (vault wikilink; repo'da render etmez ama
   "Vault:" prefix'i hedefin vault olduğunu netleştirir)

### 7.2 Heuristic

**Promote candidate:**
- Mimari karar
- Workflow / agent responsibility değişikliği
- Path, schema, lifecycle, naming standardı
- Vendor / model / altyapı kararı
- Cross-app etkisi (social ↔ crm, shared/)
- Tekrar eden hata modu ve kalıcı çözüm
- Gelecekte başka task'larda kullanılacak sentez

**Task-scope-only:**
- Geçici progress
- Bu task'a özel implementation detayı
- Tek seferlik workaround
- Ham Codex çıktısı
- Sadece bu task'a ait test sonucu

Heuristic kesin değil — gri alanlarda son kararı kullanıcı verir.

### 7.3 Güvenlik Kuralları

- **Claude vault'a otomatik yazmaz.** Önce candidate listesi + hedef
  dosya önerisi gösterir, kullanıcı onayı sonrası yazar.
- **Codex vault'a yazmaz.** Codex sadece promotion candidate işaretleme
  önerebilir (`/handoff --with-codex` çıktısında); yazımı Claude yapar.
- Vault yazımı her zaman vault frontmatter disiplinine uyar — kurallar
  `/root/otomaix-brain/CLAUDE.md` ve `/root/otomaix-brain/AGENTS.md`'de
  (verification-status, sources, last-verified, type, status, tags vb.).

## 8. Closure Workflow

`/finish-branch` 4 seçeneğine göre task layer davranışı farklılaşır —
**hepsinde closure çalışmaz**, çünkü PR ve tut intermediate durumlardır:

| Seçim | Task layer davranışı |
|---|---|
| **merge** | Full closure + archive (aşağıdaki 8-step akış, `status: done`) |
| **sil** | Full closure + archive (aynı akış, `status: cancelled`) |
| **PR** | `status: waiting-review` + HANDOFF rolling güncelleme; **archive ETMEZ** (review sonrası iterasyon gelebilir) |
| **tut** | Hiç dokunmaz; TASK ve HANDOFF active kalır |

### 8.1 PR Seçiminde

PR açmak "task bitti" anlamına gelmez — review feedback, change request,
ek commit gelebilir. Bu durumda:

1. TASK.md `status: waiting-review`, `last-touched` bugün
2. HANDOFF.md güncellenir (rolling, closure değil) — Current State'e
   "PR #N açıldı, review bekleniyor" notu
3. **Archive yapılmaz**, vault promotion check çalışmaz
4. Kullanıcı PR sonrası `/finish-branch` tekrar çağırırsa: PR merge
   edildiyse **merge** seçeneğiyle full closure; reddedildiyse **sil**
   ile cancelled

Opsiyonel: kullanıcı ilk PR sırasında "PR sonrası otomatik kapatma" der
ise Claude işaretler — bu YAGNI bölgesi, başta yok.

### 8.2 Merge / Sil Sırası (Full Closure)

Tetiklendiğinde:

1. **TASK.md final güncellemesi**
   - `status: done` (merge) veya `cancelled` (sil)
   - `last-touched` bugün
   - `Current Status`: son özet
2. **HANDOFF.md closure summary**
   - `Current State → Summary`: task ne ile bitti
   - `Resume From → Next command`: vault promotion durumu / loose end notu
   - `Verification`: final pass/fail
3. **Vault promotion check (P1, §7)** çalıştırılır
4. Onaylı kalıcı kararlar vault'a yazılır
5. TASK.md Decisions Log vault linkleriyle güncellenir
6. **TASK.md frontmatter: `status: archived`** (move'dan **önce** —
   archive klasöründeki dosya zaten `archived` durumda olmalı)
7. `docs/active/<slug>/` → `docs/task-archive/YYYY/MM/<slug>/` taşınır
8. CURRENT.md'den satır silinir

**Sıra disiplini:** Status güncellemesi move'dan önce; aksi halde move
sonrası TASK.md path değişmiş halde frontmatter edit'lemek gerekir
(çalışır ama mantıksal olarak ters).

**Konumlandırma:** Closure adımı kullanıcı seçiminden **sonra**, branch
işleminden (git merge / git push / branch -d) **önce** çalışır.

## 9. Codex / Claude Session Start Protocol

Codex'in (ve Claude'un) yeni session başlangıcında task layer'ı tanıması
için protokol. **Bu protokol repo'ya ait** — `/root/otomaix/CLAUDE.md`'ye
yazılır; `/sync-agents-md project` ile `/root/otomaix/AGENTS.md`'ye
damıtılır. **Vault AGENTS.md'ye eklenmez** (vault AGENTS.md sadece
vault'taki read-only memory consumer kurallarını tutar; repo workflow'u
oraya gömülmez).

```markdown
## Aktif Task Layer — Session Başlangıç Protokolü

Bir kullanıcı sorusu/task geldiğinde:

1. `docs/active/CURRENT.md` oku (her zaman var; boş olabilir)
2. Listelenen task'lardan kullanıcı sorusuyla alakalı olanı seç
   - Tek aktif task varsa otomatik
   - Birden fazlaysa kullanıcıya sor
   - Hiçbiri uymuyorsa active layer'ı atla
3. Seçilen task için: `docs/active/<slug>/TASK.md` ve `HANDOFF.md` oku
4. Vault sorgusu gerekiyorsa: `/root/otomaix-brain/index.md` → ilgili
   wiki sayfaları
5. Cevap ver / aksiyon al
```

**Codex için ek kısıt:** active layer'a yazma yetkisi yok. Bulgu/öneriyi
stdout olarak döner; Claude HANDOFF.md "Notes For Claude"a işler.

## 10. Implementation Notes

Bu spec için ayrı bir `/write-plan` çalıştırılacak. Plan'ın kapsayacağı
implementation kalemleri:

### 10.1 Yeni Dosyalar

- `docs/active/CURRENT.md` (boş template — klasörü zaten "açar", `.gitkeep` gerekmez)
- `docs/task-archive/.gitkeep` (boş başlar; ilk archive'a kadar `.gitkeep` gerekli)
- `~/.claude/commands/handoff.md` (yeni slash command)
- `templates/TASK.md.template` (opsiyonel — `/write-plan` referans alır)
- `templates/HANDOFF.md.template` (opsiyonel)

### 10.2 Düzenlenecek Dosyalar

**Root CLAUDE.md (`/root/otomaix/CLAUDE.md`):**
- Path konvensiyonu listesine ekle:
  - `docs/active/<slug>/TASK.md` + `HANDOFF.md` — aktif task state
  - `docs/active/CURRENT.md` — pointer
  - `docs/task-archive/YYYY/MM/<slug>/` — kapanmış task state
- "Aktif task layer" alt-bölümü eklenir (kısa: ne için, nereye bak, lifecycle)
- §9 session başlangıç protokolü buraya yazılır

**Repo AGENTS.md (`/root/otomaix/AGENTS.md`):**
- CLAUDE.md güncellemesi sonrası `/sync-agents-md project` çağrılır
- Codex damıtma marker bloğu otomatik yenilenir — §9 protokolü
  AI-agnostic kısımları damıtılarak buraya gider
- **Vault AGENTS.md'ye dokunulmaz** (vault read-only memory consumer
  scope'unda kalır; repo workflow scope farklı)

**Global Claude/Codex kuralları (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`):**
- Bu spec'te değişiklik **gerekmiyor** — task layer Otomaix repo'suna
  özgü. Eğer başka projeler de bu pattern'i adapte ederse o zaman
  global'e taşıma değerlendirilir.

**Mevcut slash command'ler (`~/.claude/commands/*.md`):**
- `write-plan.md`, `execute-plan.md`, `commit.md`, `review.md`,
  `finish-branch.md` — §6.1'deki hatırlatma adımları eklenir
- Hatırlatmalar **conditional** — CURRENT.md boşsa veya kullanıcı
  no-op tercih ederse skip edilir

**Vault `cross-project/infrastructure/codex-entegrasyonu.md`:**
- Active task layer'a referans eklenir (yeni section veya inline link)
- "Conversation history aktarımı yok" notunun yanına: *"HANDOFF.md ile
  partial mitigation — bkz. `docs/active/<slug>/HANDOFF.md`"*

### 10.3 Test / Verification

- Bir dummy task ile end-to-end deneme:
  1. `/write-plan` → TASK.md + HANDOFF.md yaratılır
  2. `/execute-plan` → status=active
  3. `/commit` → TASK güncellenir, vault promotion check çalışır
  4. `/handoff` → HANDOFF full güncelleme
  5. `/handoff --with-codex` → Codex review, Notes For Claude'a işleme
  6. `/finish-branch` **merge** veya **sil** seçimiyle → closure → archive (PR seçilirse `waiting-review`'a geçiş + archive yok; tut seçilirse no-op)
- CURRENT.md boşsa hatırlatmaların skip edildiği doğrulanır
- Codex `--cwd /root/otomaix` ile çağrıldığında active layer'ı okuyabildiği doğrulanır

## 11. Out-of-Scope (Bilinçli Atlananlar)

| Konsept | Neden atlandı |
|---|---|
| `issues.md` ayrı dosyası | Open Problems TASK.md içinde yeterli; bakım yükü + drift riski |
| Otomatik PostToolUse hook | Manuel mod felsefesi; `[[codex-entegrasyonu]]`'da aynı muhakeme |
| HANDOFF append-only journal | git zaten append-only history sağlar; duplikasyon |
| Branch-based discovery | Main ağırlıklı çalışma + paralel task gerçeği; CURRENT.md daha esnek |
| INDEX.md (archive için) | Klasör yapısı yeterli; gerekirse sonraki iterasyonda |
| `Constraints` ayrı TASK.md bölümü | Goal'a 1-3 cümlede sığar; ayrı bölüm boş kalır |
| `Risks` ayrı TASK.md bölümü | Belirsiz risk → Open Problems, kalıcı risk → Decisions Log; HANDOFF.md'de session-scope Risks ayrı |
| `Branch` TASK.md frontmatter | CURRENT.md pointer branch-agnostic; gereksiz |
| Status duplikasyonu (CURRENT.md + TASK.md) | Drift kaynağı; sadece TASK.md canonical |
| `Decisions Since Last Handoff` HANDOFF.md bölümü | TASK.md Decisions Log canonical; rolling overwrite'da kararlar kaybolurdu |
| `Open Problems` HANDOFF.md bölümü | Aynı sebep — TASK.md canonical |
| Otomatik Codex çağrısı (her /handoff'ta) | Opt-in (`--with-codex` flag); maliyet + non-determinism |
| Otomatik vault yazımı | Manuel onay kapısı; Claude/Codex vault disiplini |

## 12. İlgili Belgeler

- `[[codex-entegrasyonu]]` — Codex CLI sync sistemi, AGENTS.md damıtması
- `docs/plans/2026-05-12-otomaix-brain-faz-plani.md` — vault faz planı
- `[[claude-code-workflow]]` — slash command ekosistemi
- `~/.claude/commands/plan-claude-codex.md` — mevcut Claude+Codex çift-perspektif tasarım pattern'i
- `~/.claude/commands/council.md` — Karpathy LLM Council pattern (multi-AI pressure-test)
- `/root/sonkonusmaozeti.md` — bu spec'in girdi seansı özeti
