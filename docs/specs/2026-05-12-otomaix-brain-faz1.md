# Otomaix Brain Faz 1 — Vault Kurulumu Spec'i

**Tarih:** 2026-05-12
**Durum:** Onaylanmış spec, `/write-plan`'a hazır
**Branch:** main (feature branch açılmadı; spec doc düşük riskli, son 20 commit'in deseni main)
**Kapsamlı plan:** [`docs/plans/2026-05-12-otomaix-brain-faz-plani.md`](../plans/2026-05-12-otomaix-brain-faz-plani.md) (Faz 1 + Faz 2 roadmap)
**Schema:** [`docs/brain-CLAUDE.md`](../brain-CLAUDE.md) (vault'a kopyalanacak, 8 düzeltme yapılmış)

---

## 1. Bağlam ve hedef

Otomaix'in (bugün social, yarın crm + diğer apps) **ortak beyni**. Tek operatör (Eray) için, multi-tenant değil. Karpathy'nin LLM Wiki pattern'i üzerine kurulu — wiki = codebase, LLM = programcı.

**Faz 1'in hedefi:** Kalıcı bilgi katmanını (Obsidian wiki) ayağa kaldırıp 13 dosyalık ilk migration'ı tamamlamak. Hermes (Faz 2) yok — bu faz tamamen interactive (sen + Claude Code).

**Faz 2 (sonra):** Hermes Coolify deploy, Telegram bot, cron, dış dünya tarama. Bu spec'in dışında.

## 2. Mimari kararları

| # | Konu | Karar | Neden |
|---|---|---|---|
| 1 | **Vault konumu** | `/root/otomaix-brain/` (VPS, otomaix repo'sundan ayrı dizin) | Claude Code (bu session) doğrudan yazabilsin. |
| 2 | **Görüntüleme** | Mac/Windows'tan SSHFS mount + Obsidian | Graph view, backlinks, plugin ekosistemi en olgun yol. |
| 3 | **Versiyon** | Git → GitHub **private** repo (örn. `eraydeniz/otomaix-brain-private`) | Otomaix kod repo'sundan tamamen bağımsız. Public yapma. |
| 4 | **Schema** | `/root/otomaix-brain/CLAUDE.md` (düzeltilmiş `brain-CLAUDE.md`) | LLM her oturumda bu kuralları okuyup uyar. |
| 5 | **External kaynak** | **Memory dosyaları + repo dışı kaynaklar:** kopyalanmaz, `frontmatter.sources: ["@/absolute/path"]` ile link. **Repo içi raw research (örn. `marketingskills.md`):** olduğu gibi `sources/`'a kopyalanır, parçalanmaz, original silinir (canonical sources'ta). | Drift bombasını söndür ama immutable raw analizleri vault'a "frozen snapshot" olarak al. |
| 6 | **Canonical** | Migration sonrası vault canonical olur. Orijinaller `docs/_archive/`'e. | Tek hakikat. Drift yok. |
| 7 | **Update disiplini** | Yarı-otomatik. `/commit` skill'ine vault check eklenir. | Friction düşük, kayıp riski düşük. |

## 3. Klasör hiyerarşisi (top-level)

```
/root/otomaix-brain/
├── CLAUDE.md                     # vault schema (Claude Code uyar)
├── index.md                      # sayfa kataloğu, her ingest sonrası güncellenir
├── log.md                        # ingest/query/lint append-only log
├── cross-project/                # Otomaix umbrella bilgi (alt-klasörler ihtiyaç çıktıkça)
├── apps/social/                  # Otomaix Social-spesifik
│   ├── pipeline/
│   ├── templates/                # AKTİF: 6 ana şablon (genel + özel gün)
│   │   ├── genel-gorsel-sablon.md
│   │   ├── carousel-genel-sablon.md
│   │   ├── shortvideo-genel-sablon.md
│   │   ├── ozelgun-gorsel-sablon.md
│   │   ├── ozelgun-carousel-sablon.md
│   │   ├── ozelgun-shortvideo.md
│   │   └── deprecated/
│   │       └── 22-sektor-sablonlari-terk-karari.md
│   └── architecture/
│       └── history/              # 01-06 phase reports buraya
├── apps/crm/                     # 05-crm-admin migration'ında açılır
├── decisions/                    # ADR'lar, YYYY-MM-DD-konu.md
├── research/                     # derin araştırma + filed-back query cevapları
├── sources/                      # external snapshot'lar (frozen referanslar)
│   └── research/                 # marketingskills.md (analiz raporu) buraya
└── inbox/                        # Faz 2'de Hermes yazacak (şu an sadece README.md)
```

**YAGNI kuralı:** Alt-klasörler (örn. `cross-project/databases/`, `cross-project/vendors/`) migration sırasında **ihtiyaç çıktıkça** açılır, baştan boş açılmaz. Sadece içine sayfa konacak olan klasörler oluşturulur.

## 4. Migration kapsamı — 13 dosya

### Decisions (memory'den, link ile referans, kopyalanmaz)

1. `~/.claude/projects/-root-otomaix/memory/decisions_backend.md`
2. `~/.claude/projects/-root-otomaix/memory/decisions_frontend.md`
3. `~/.claude/projects/-root-otomaix/memory/decisions_crm.md`

Vault'taki `decisions/YYYY-MM-DD-*.md` sayfaları bu dosyalara frontmatter'da `@/absolute/path` link verir. Memory dosyaları yerinde kalır (auto-load değeri), içlerine **`> FROZEN snapshot — yeni kararlar: /root/otomaix-brain/decisions/`** notu eklenir.

### Otomaix docs/ root (numaralı + marketingskills)

| # | Dosya | Boyut | Migrate hedefi |
|---|---|---|---|
| 4 | `00-platform-mimari.md` | 6 KB | `cross-project/` ana sayfaları (databases, infrastructure, integrations) |
| 5 | `01-social-phase1.md` | 22 KB | `apps/social/architecture/history/phase-1-*.md` |
| 6 | `02-social-phase2.md` | 20 KB | `apps/social/architecture/history/phase-2-*.md` |
| 7 | `03-social-phase3.md` | 19 KB | `apps/social/architecture/history/phase-3-*.md` |
| 8 | `04-social-phase4.md` | 14 KB | `apps/social/architecture/history/phase-4-*.md` |
| 9 | `05-crm-admin.md` | 16 KB | `apps/crm/` (klasör burada açılır) |
| 10 | `06-social-trends-phase6.md` | 29 KB | `apps/social/architecture/history/phase-6-*.md` |
| 11 | `07-social-template-system.md` | **155 KB** | `apps/social/templates/*` (6 aktif şablon) + `apps/social/architecture/template-system-design.md` + `templates/deprecated/` (eski 22 sektör kararı) |
| 12 | `11-social-marketingskills.md` | 55 KB | `cross-project/copywriting/` (hook, psikoloji, görsel açı) + `apps/social/architecture/marketingskills-entegrasyon.md` |
| 13 | `12-social-carousel.md` | 18 KB | `apps/social/pipeline/carousel.md` + `apps/social/architecture/carousel-design.md` |

### Sources

| # | Dosya | Hedef |
|---|---|---|
| 14 | `marketingskills.md` (research, 9 KB) | `sources/research/2026-04-marketing-skills-analizi.md` (raw, immutable, frontmatter ile referanslanır) |

**Toplam:** 13 ana dosya + 1 raw source = ~370 KB markdown, tahmini ~250-400 wiki sayfası, **2-4 günlük yoğun ingestion işi**.

## 5. Migration sırası — 10 adım (kolaydan zora)

1. **Vault iskeleti:** `/root/otomaix-brain/` oluştur, `CLAUDE.md` (düzeltilmiş `brain-CLAUDE.md`'den kopya) yerleştir, `index.md` ve `log.md` boş başlat, top-level klasörleri aç (sadece kullanılacak olanlar), `git init`, initial commit.
2. **Decisions migration** (3 dosya, en yapılandırılmış, en hızlı kazanım). Her karar → `decisions/YYYY-MM-DD-*.md`, frontmatter'da memory dosyasına link.
3. **00-platform-mimari** → `cross-project/` ana sayfaları.
4. **11-marketingskills** → `cross-project/copywriting/` + `apps/social/architecture/marketingskills-entegrasyon.md`.
5. **12-carousel** → `apps/social/pipeline/carousel.md` + `apps/social/architecture/carousel-design.md`.
6. **07-template-system** (en uzun adım, 4-6 saat). **Dikkat:** eski 22-sektör kararı ile yeni 6-şablon mimarisini ayırt et. Aktif şablonlar `templates/*.md`, deprecated kısım `templates/deprecated/`.
7. **01-06 phase reports** → `apps/social/architecture/history/`.
8. **05-crm-admin** → `apps/crm/` klasörü burada açılır, ilk sayfalar.
9. **marketingskills.md** (research) → `sources/research/`.
10. **index.md** ve **log.md** doldurulur, final git commit + GitHub push.

Her ana adımdan sonra git commit (örn. `vault: decisions migrated`, `vault: 07-template-system migrated`).

## 6. Original'ların kaderi (canonical = vault)

Migration sonrası `/root/otomaix/docs/[migrated].md` → `/root/otomaix/docs/_archive/`'e **taşınır**. İçine `_archive/README.md`:

> Bu dosyalar `/root/otomaix-brain/` vault'una migrate edildi. Tek hakikat = vault. Burası tarihsel arşiv, dokunma. Yeni karar/güncelleme: vault.

`brain-CLAUDE.md` arşive girmez — bu schema vault'a kopyalandı, kaynağı orada yaşar.

`docs/_archive/`'e gitmeyenler (vault'a girmeyen + arşivlenmeyen):
- `claude-code-kullanim-kilavuzu.md` (kişisel kılavuz)
- `FEATURE_SPEC_intro_outro.md` (canlıya çıkmamış)
- `multi-shot-video-pipeline.md` (tasarım aşaması)
- `docs/specs/`, `docs/plans/`, `docs/debug-logs/`, `docs/reviews/`, `docs/council/` klasörleri (tarihsel iş kayıtları)

## 7. Update disiplini (yarı-otomatik)

**`/commit` skill'ine ekleme:** Commit oluşturulduktan sonra Claude Code şu soruyu sorar:

> "Bu commit'te kalıcı bir mimari karar / yeni vendor / yeni kural var mı? Vault'a yazılması gereken bir şey? (e/h)"

- **Evet:** Claude Code uygun vault sayfasını açar/günceller → ayrı commit (örn. `vault: stale-job sweeper kararı eklendi`)
- **Hayır:** atlanır, friction sıfır

İmplementasyon: `~/.claude/commands/commit.md` skill dosyasının sonuna 5-6 satır eklenecek. Bu Faz 1 implementation'ın son iş kalemi.

## 8. Backup & recovery

- Her vault commit sonrası: `git push origin main`
- Remote: GitHub private repo (`eraydeniz/otomaix-brain-private` benzeri, **kullanıcı oluşturacak**)
- VPS çökme senaryosu: yeni VPS'te `git clone` → vault tam recover
- Lokal Obsidian'da görme alternatifi: lokal makinede ikinci clone (git pull modeli, SSHFS yerine)

## 9. Faz 1 "bitti" kriteri (verification — kanıtla, iddia etme)

Aşağıdaki **8 maddenin hepsi** doğrulanmış olmalı:

1. Vault iskeleti `/root/otomaix-brain/`'de var, `git log` 1+ commit gösteriyor
2. 13 dosya migrate edildi → `find /root/otomaix-brain -name "*.md" -not -path "*/.git/*" | wc -l` → 250-400 sayfa aralığında (tahmin)
3. `index.md` ve `log.md` doldurulmuş, kalan boş satır yok
4. Mac/Windows'tan SSHFS mount + Obsidian açılıyor, graph view dolu görünüyor
5. GitHub private repo'ya push edildi, `git remote -v` doğru remote'u gösteriyor
6. `/commit` skill dosyası vault check sorusu içeriyor (kontrol: `grep "vault" ~/.claude/commands/commit.md`)
7. Test query: "FLUX neden seçilmedi" → Claude Code ilgili wiki sayfalarını referans gösteriyor
8. `/root/otomaix/docs/_archive/`'de migrate edilen dosyalar var + README açıklaması yerinde

## 10. Bilinen riskler / kabul edilen trade-off'lar

- **155 KB'lik 07-template-system parçalama** ingestion'ın en uzun adımı. Eski/yeni karar ayrımına dikkat (deprecated/ bunun için).
- **Phase reports (01-06) tarihsel değer mi yoksa gürültü mü** belirsiz — `apps/social/architecture/history/` altına atılıyor. Bir yıl sonra "değersizmiş" çıkarsa silinir.
- **SSHFS latency** Obsidian'ı yavaşlatabilir. Çok rahatsızsa ileride lokal git pull modeline geçilir.
- **Schema'da kalan stack info riski** — `brain-CLAUDE.md`'de düzelttik ama vault yaşadıkça başka drift'ler ortaya çıkabilir. Lint operasyonu periyodik kontrol noktası.

## 11. Açıkça Faz 1 kapsam DIŞI

- ❌ Hermes deploy (Faz 2)
- ❌ Telegram bot (Faz 2)
- ❌ `inbox/` aktif kullanım (Faz 2; şu an sadece `README.md` placeholder)
- ❌ Cron / scheduled işler (Faz 2)
- ❌ Skill self-improvement (Faz 2, deneme amaçlı)
- ❌ Otomatik dış dünya tarama (Faz 2)
- ❌ Lint otomasyonu (manual lint OK; otomatik değil)
- ❌ Diğer Otomaix dokümanları (`FEATURE_SPEC_intro_outro.md`, `multi-shot-video-pipeline.md` vb.) — Faz 1 dışı

## 12. Sıradaki adımlar

Spec onaylandıktan sonra:

1. `/write-plan` → bu spec'ten implementation planı çıkar (`docs/plans/2026-05-12-otomaix-brain-faz1-impl.md`)
2. Plan'a göre vault iskeleti kur + migration başlat (1-2 oturum)
3. Migration tamamlandıktan sonra `/commit` skill'i güncelle
4. Verification checklist (Bölüm 9) tek tek doğrula
5. Faz 1'i 1-2 hafta gerçek kullanım'da deneme
6. Sezgi olgunlaştıysa Faz 2 brainstorm'u
