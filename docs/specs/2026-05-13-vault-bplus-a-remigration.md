# Vault B+A Re-migration — Faz I Spec

**Tarih:** 2026-05-13
**Faz konumlanması:** Otomaix Brain Faz 1 implementation planının devamı — yeni "Faz I — Re-migration" bölümü.
**Plan dosyası:** Mevcut `docs/plans/2026-05-12-otomaix-brain-faz1-impl.md` içine yeni bölüm olarak eklenecek.

---

## 1. Bağlam ve motivasyon

### Bulgu — Phase 6 attribution hatası

2026-05-13 cold session test query sırasında ortaya çıktı: vault sayfası `apps/social/architecture/history/phase-6-trend-sistemi.md` üç Layer'ın (A/B/C) içerik atamalarını yanlış yapmış.

Orijinal kaynak (`docs/_archive/06-social-trends-phase6.md`):
- Layer A: Ücretsiz gece taraması, 7 kaynak (Google News + Trends + YouTube + Reddit + trends24.in + Pinterest Trends + TCMB EVDS)
- Layer B: Kullanıcı tetikli kişiselleştirme (Serper.dev + Claude Haiku, ~$0.005/tetik)
- Layer C: Aylık Apify raporu (11 aktör, WeasyPrint PDF, ~$0.55/rapor)

Vault sayfasında:
- Layer A: "RSS + pytrends evrimi" (yanlış — pytrends kaldırılmıştı)
- Layer B: "Sektör + sosyal medya, Apify scraping" (yanlış — bu Layer C'nin işi)
- Layer C: "Kişiselleşmiş, brand context + Claude" (yanlış — bu Layer B'nin işi)

3 Layer'ın 3'ü de yanlış. Tesadüf değil — **sistemik özet hatası**.

### Root cause

Faz 1 migration sürecinde her sayfa:
1. Kaynak dosya okundu (510 satır)
2. Tek seferde özet yazıldı
3. Commit edildi

**Doğrulama adımı yoktu.** LLM özet yazarken kendi mantığını kaynağa dayatabilir, sonra "doğru görünüyor" diye onaylar (motivated reasoning). Yazan da LLM, doğrulayan da aynı LLM = aynı bias.

### Etki ve risk

- Vault 115 sayfa, hepsi aynı tek-pass süreçle migrate edildi
- Phase 6 hatası kanıtlanmış; başka sayfalarda da olabilir (kanıtlanmadı ama mümkün)
- Vault "canonical" iddiası şu an doğrulanmamış varsayım
- Cold session bir sayfaya güvenip yanlış bilgi üretirse vault'un compound knowledge değeri zehirlenir

### Karar

**Karpathy pattern korunarak**, hata vektörünü yapısal olarak daraltan ve doğrulama adımı ekleyen sistematik re-migration: **B+A pipeline'lı tier-based yeniden yazım**.

Alternatif yaklaşımlar (reddedildi):
- **Saf C (pointer-only):** Vault'u özetleme yapmayan kaynak dizinine indirgemek hatayı sıfırlar ama Karpathy compound knowledge değerini öldürür. Faz 2 Hermes yatırımı anlamsızlaşır.
- **Hibrit C:** Risk-yüksek sayfaları pointer-only yapmak. Karpathy bütünlüğünü 8-10 sayfada kırar; ~1-2 hatalı sayfa azaltma karşılığı değmez.
- **Spot-check sampling:** Önce 14 sayfa rastgele kontrol edip hata oranını ölçmek. Kullanıcı tercihi: 2 saat kayba değmez, doğrudan sistematik düzeltme.

---

## 2. Tasarım özeti

**B (Build):** Yüksek riskli sayfaları parçalı yaz, attribution-prone bilgi için verbatim quote-back zorunlu. Hata vektörünü yapısal olarak daralt.

**A (Audit):** Her sayfa için **fresh-context subagent** spawn et — kaynak + vault sayfasını yan yana okur, severity-tier'lı diff raporu döner. Yazan-LLM ≠ doğrulayan-LLM.

**Risk-orantılı kapsam:**

| Tier | ~Sayfa | Mekanizma | Gerekçe |
|---|---|---|---|
| **HIGH** | 15 | B + A | Uzun özet, attribution-prone, Phase 6 tipi hata riski yüksek |
| **MID** | 23 | Sadece A | Orta uzunluk, mevcut sayfayı doğrula; mismatch varsa düzelt |
| **LOW** | 77 | Skip | Kısa kararlar, kaynak zaten kompakt, hata riski düşük |

**Toplam:** 115 sayfa = 15 + 23 + 77

**Süre tahmini:** 10-15 saat (hazırlık 1.5 + Phase 6 Task 1 1 + HIGH B+A 5-8 + MID A 3-5 + cold test 30 dk).

---

## 3. Tier ayrımı — somut sayfa listesi

### HIGH (15 sayfa — B + A baştan yaz)

| # | Sayfa | Kaynak |
|---|---|---|
| 1 | `apps/social/architecture/history/phase-6-trend-sistemi.md` | `docs/_archive/06-social-trends-phase6.md` |
| 2 | `apps/social/architecture/history/phase-1-altyapi-kurulumu.md` | `docs/_archive/01-social-phase1.md` |
| 3 | `apps/social/architecture/history/phase-2-temel-ozellikler.md` | `docs/_archive/02-social-phase2.md` |
| 4 | `apps/social/architecture/history/phase-3-gelismis-ozellikler.md` | `docs/_archive/03-social-phase3.md` |
| 5 | `apps/social/architecture/history/phase-4-saas-hazirlik.md` | `docs/_archive/04-social-phase4.md` |
| 6 | `apps/social/architecture/template-system-design.md` | `docs/_archive/07-social-template-system.md` (Bölüm 2) |
| 7-12 | `apps/social/templates/{genel-gorsel,carousel-genel,shortvideo-genel,ozelgun-gorsel,ozelgun-carousel,ozelgun-shortvideo}-sablon.md` | `docs/_archive/07-social-template-system.md` (Bölüm 3) |
| 13 | `apps/social/pipeline/carousel.md` | `docs/_archive/12-social-carousel.md` |
| 14 | `apps/social/architecture/carousel-design.md` | `docs/_archive/12-social-carousel.md` |
| 15 | `apps/social/architecture/marketingskills-entegrasyon.md` | `docs/_archive/11-social-marketingskills.md` |

### MID (23 sayfa — sadece A doğrulama, B yapılmaz)

**Kaynak: `00-platform-mimari.md` (7 sayfa)**
- `cross-project/infrastructure/{platform-overview,monorepo-yapisi,coolify-deploy,tech-stack,claudemd-template}.md`
- `cross-project/databases/postgres-multi-app-pattern.md`
- `cross-project/integrations/n8n.md`

**Kaynak: `11-social-marketingskills.md` (6 copywriting)**
- `cross-project/copywriting/{somutluk-kurali,loss-aversion,social-proof,gorsel-aci-7-kategori,hook-formulleri-yasak-karari,jtbd-neden-kaldirildi}.md`

**Kaynak: `07-social-template-system.md` Bölüm 4 (6 vendor)**
- `cross-project/vendors/{fal-ai-models,nano-banana,wan,kling,elevenlabs,anthropic-claude}.md`

**Kaynak: `05-crm-admin.md` (4 CRM)**
- `apps/crm/architecture/{admin-yapisi,n8n-entegrasyon,auth-akisi,deploy}.md`

### LOW (77 sayfa — skip)

- 72 `decisions/*.md` (memory'den geldi, kaynak satırlık kısa, atama riski düşük)
- 1 `apps/social/templates/deprecated/22-sektor-sablonlari-terk-karari.md`
- 1 `sources/research/2026-04-marketing-skills-analizi.md` (frozen verbatim kopya)
- 3 yeni: `cross-project/infrastructure/claude-code-workflow.md` + 2 economics stub (zaten doğrulanmış / yapısal)

---

## 4. B süreci — parçalı yazma (HIGH için)

### Atom: Section seviyesi (`## başlık`)

Her vault sayfası section section yazılır. Bir section bitmeden bir sonrakine geçilmez.

### Quote-back disiplini — hibrit

#### Attribution-prone bilgiler (verbatim quote zorunlu)

Tanım: aşağıdaki bilgi kategorileri attribution-prone sayılır:
- Numaralı/harfli listelerin atamaları (Layer A/B/C içeriği, Phase X sırası, vendor → model eşlemesi, kategori → değer eşlemesi)
- Sayısal değerler (fiyat, kota, eşik, satır sayısı, gün, tarih)
- Model/vendor/SKU/API adları (özel isim niteliğinde)
- Karar verilen seçenek vs reddedilen alternatif
- Kronolojik/numaralı sıra bilgisi

Format:

```markdown
## Üç katmanlı yeni mimari

> **Kaynak alıntı** (`@docs/_archive/06-social-trends-phase6.md:139-158`):
> Layer A: 7 kaynak paralel (Google News, Google Trends, YouTube, Reddit,
>   trends24.in, Pinterest Trends, TCMB EVDS)
> Layer B: Kullanıcı tetikli, Serper.dev + Claude Haiku, ~$0.005/tetik
> Layer C: Pro+ aylık rapor, Apify 11 aktör, WeasyPrint PDF, ~$0.55/rapor

- **Layer A** — Gece taraması, 7 kaynak paralel (yukarıdaki liste), $0/ay
- **Layer B** — Kullanıcı tetikli kişiselleştirme, Serper.dev + Claude Haiku
- **Layer C** — Aylık rapor, Apify 11 aktör (TikTok, Instagram, Twitter, vb.), PDF üretimi
```

Quote bloğu sayfa içinde kalır (auditable). Vault hacmini ~%20-30 artırır ama doğrulanabilirlik karşılığında kabul edilir.

#### Diğer içerik (line-number referans yeter)

Açıklayıcı / gerekçe / arka plan metni için verbatim quote yerine satır aralığı referansı:

```markdown
## Problem (önceki durum)

> Kaynak: `@docs/_archive/06-social-trends-phase6.md:42-78`

Mevcut `trend_analyzer.py` 3 gazete RSS + pytrends kullanıyordu. Sektör-bazlı
6 saatlik cache aynı sektördeki tüm kullanıcılara aynı 6 sonucu sunuyordu.
pytrends 429 hatası sürekli rate-limit'e takılıyordu.
```

Section yazılırken o satır aralığı yeniden okunur, ama quote yapıştırılmaz.

### B akışı (her section için)

```
1. Kaynak section'ı oku (satır aralığı)
2. Vault sayfasına section başlığını yaz
3. Attribution-prone içerik varsa → verbatim quote bloğu ekle
4. Diğer içerik için → line-number referans satırı ekle
5. Açıklayıcı paragraf / bullet'ları yaz (kaynağı görünür tutarak)
6. Bir sonraki section'a geç
```

Sayfa tamamlandığında frontmatter'a `verification-status: b-written` set edilir.

---

## 5. A süreci — subagent doğrulama

### Subagent tipi

**`general-purpose`** — Read + Bash + Grep tüm tools mevcut. Cross-file consistency check için uygun.

(Explore agent dökümanında "cross-file consistency checks" için önerilmiyor; bu iş tam o kategori.)

### Subagent prompt template

```
Görev: Vault sayfasını kaynak dosya ile karşılaştır, attribution hatası ara.

Sayfa: {{vault_page_path}}
Kaynak: {{source_file_path}}
Tier: {{HIGH | MID}}

Attribution-prone kategoriler:
- Numaralı/harfli listelerin atamaları (Layer A/B/C içeriği, Phase X sırası, vendor → model eşlemesi)
- Sayısal değerler (fiyat, kota, eşik)
- Model/vendor/SKU/API adları
- Karar verilen seçenek vs reddedilen alternatif
- Kronolojik/numaralı sıra bilgisi

Adımlar:
1. Kaynak dosyayı oku (tamamı)
2. Vault sayfasını oku (tamamı)
3. Sayfadaki her attribution-prone iddia için kaynakta eşleşme ara
4. Mismatch bul → severity belirle:
   - critical = attribution hatası (atama/sıra/sayı/model yanlış)
   - minor = yazım, eksik wikilink, kelime farkı, eksik referans
   - cosmetic = frontmatter alanı eksik, başlık tutarsızlığı, format
5. Mismatch raporu çıkar

Çıktı format (markdown):
- "OK — sayfa kaynakla tutarlı" eğer hiç mismatch yoksa
- Aksi halde numbered list:
  1. **[critical]** <kısa başlık>
     - Vault iddia: "..."
     - Kaynak (satır N): "..."
     - Tutarsızlık: <açıklama>
  2. **[minor]** ...

Sadece raporla, sayfayı DÜZELTME, vault'a YAZMA.
```

### Maliyet

- 38 sayfa (15 HIGH + 23 MID) × ortalama 45 sn = ~30 dk toplam subagent süresi
- Subagent çağrı maliyeti standart Agent tool ücretinde

### Paralelleştirme (opsiyonel optimizasyon)

MID-tier (sadece A) için aynı anda 3-4 subagent paralel dispatch edilebilir (Agent tool tek mesajda multiple tool call). HIGH için seri (B yazımı serial, ardından A) — çünkü B benim contextimde, paralelize edilemez. Spec'te default seri; pratikte gerekirse uygulanır.

---

## 6. Mismatch handling — severity-tier protokolü

Subagent raporu döner. Ben kategorize edip aşağıdaki tabloya göre işlerim:

| Severity | Tanım | İşlem | Onay gerekli mi? |
|---|---|---|---|
| **Critical** | Attribution hatası: Layer/sıra/sayısal/model atama yanlış | Dur, kullanıcıya özet + düzeltme önerisi sun → onay → düzelt | **Evet** |
| **Minor** | Yazım, eksik wikilink, kelime farkı, eksik referans | Otomatik düzelt | Hayır, log entry'sinde "X sayfa: N minor düzeltme" |
| **Cosmetic** | Frontmatter alanı, başlık tutarsızlığı, format | Otomatik düzelt | Hayır, sessiz |

### Critical handling akışı

1. Subagent raporunda `[critical]` flag'i bulundu
2. Sayfa frontmatter'ında `verification-status: conflict` set edilir
3. Kullanıcıya özet:
   ```
   ⚠️ Critical mismatch: <sayfa>
   - Vault iddia: "..."
   - Kaynak: "..."
   - Önerim: <düzeltme önerisi>
   - Onay? [e/h]
   ```
4. Onay → düzelt, `verification-status: a-verified`
5. Red / alternative → kullanıcı ile birlikte çözüm
6. Çözülemeyen critical → `verification-status: conflict` kalır, faz çıkış kriterinde flag bekler

### Minor & cosmetic kümülasyon

Bir sayfada N minor + M cosmetic varsa: hepsini tek seferde düzelt, commit message'a sayı yaz, log.md entry'sine ekle. Sayfa başına tek commit.

---

## 7. State tracking — frontmatter alanı

### Yeni alan: `verification-status`

Mevcut frontmatter şeması:

```yaml
---
title: ...
type: vendor | decision | template | concept | research | policy | runbook | history
status: active | superseded | draft | stub | completed
last-verified: 2026-05-13
verification-status: unverified | b-written | a-verified | conflict
sources:
  - ...
tags: [...]
---
```

### Değerler

| Değer | Anlam | Set eden |
|---|---|---|
| `unverified` | Re-migration henüz yapılmadı (default) | Hazırlık batch script |
| `b-written` | B parçalı yazıldı, A bekliyor (HIGH için ara state) | B sürecinin sonu |
| `a-verified` | B+A geçti (HIGH) veya sadece A doğruladı (MID); sayfa onaylı | A sürecinin başarılı sonu |
| `conflict` | Critical mismatch, kullanıcı kararı bekliyor | Subagent raporunda critical bulunduğunda |

### Mevcut sayfalara default ekleme

Hazırlık aşamasında 115 sayfaya `verification-status: unverified` batch script ile eklenir (bash/sed ile YAML frontmatter'a yeni satır insert). Faz tamamlandıktan sonra `unverified` kalanlar = LOW kategorisi (skip kararı; bilinçli, audit-edilmemiş).

### Schema CLAUDE.md güncellemesi

Vault `CLAUDE.md`'nin "Sayfa konvansiyonları → Frontmatter" bölümüne aşağıdaki ekleme:

```markdown
### Verification status (Faz I'den sonra)

`verification-status` alanı sayfanın doğrulama durumunu işaretler:
- `unverified` — re-migration yapılmadı, audit edilmemiş
- `b-written` — B parçalı yazıldı, A bekliyor
- `a-verified` — kaynakla yan yana doğrulandı (Faz I — Re-migration kapsamında)
- `conflict` — critical mismatch bulundu, kullanıcı kararı bekliyor

Re-migration süreci: bkz `docs/specs/2026-05-13-vault-bplus-a-remigration.md`.
```

---

## 8. Hazırlık + işlem sırası

### Hazırlık (faz başlamadan, ~1.5 saat)

| Adım | İş | Çıktı |
|---|---|---|
| H1 | Vault `CLAUDE.md` güncelle: `verification-status` alanı tanımı + B+A süreç özeti + subagent protokol bilgisi | Vault commit `vault: add verification-status to schema` |
| H2 | Batch frontmatter ekleme — 115 sayfaya `verification-status: unverified` ekle (sed/python script) | Vault commit `vault: batch unverified frontmatter (115 pages)` |

### Faz I işlem sırası (hibrit risk + kaynak gruplama)

| Task | Kaynak | Sayfa | Tier | Süre | Mekanizma |
|---|---|---|---|---|---|
| **Task 1** | `06-social-trends-phase6.md` | 1 (Phase 6) | HIGH | ~1 saat | B+A (pipeline test + bilinen hata düzeltmesi) |
| **Task 2** | `07-social-template-system.md` Bölüm 2+3 | 7 (design + 6 templates) | HIGH | ~3-4 saat | B+A |
| **Task 3** | `01/02/03/04-social-phase*.md` | 4 (Phase 1, 2, 3, 4) | HIGH | ~2-3 saat | B+A |
| **Task 4** | `12-social-carousel.md` + `11-social-marketingskills.md` (architecture) | 3 (2 carousel + 1 marketingskills-entegrasyon) | HIGH | ~1.5 saat | B+A |
| **Task 5** | `00-platform-mimari.md` | 7 | MID | ~1 saat | sadece A |
| **Task 6** | `11-social-marketingskills.md` (copywriting) | 6 | MID | ~45 dk | sadece A |
| **Task 7** | `07-social-template-system.md` Bölüm 4 (vendors) | 6 | MID | ~45 dk | sadece A |
| **Task 8** | `05-crm-admin.md` | 4 | MID | ~30 dk | sadece A |
| **Task 9** | Cold test (3 random HIGH) | 3 sample | — | ~30 dk | yeni session test query |

Toplam: ~10-15 saat (hazırlık 1.5 + 8 task 9-12 + cold test 0.5).

### Task içi akış

**HIGH task (B+A):**
1. Kaynak dosyayı aç, vault sayfasını sil (gerekirse) ya da overwrite et
2. Section section B süreci (her section için quote + paraphrase)
3. Sayfa frontmatter'ına `verification-status: b-written`
4. Subagent dispatch → A doğrulama
5. Subagent raporu → severity-tier protokolü (kullanıcı kararı gerekirse iste)
6. `verification-status: a-verified` (veya conflict)
7. Vault commit (kaynak başına 1 commit, multiple sayfa içerebilir)

**MID task (sadece A):**
1. Subagent dispatch (kaynak + sayfa)
2. Rapor → severity-tier protokolü
3. Mismatch varsa düzelt (Section 6 protokolüne göre)
4. `verification-status: a-verified`
5. Vault commit

---

## 9. Çıkış kriteri

### Mekanik kriter

```bash
# Hiç unverified / b-written / conflict kalmamalı (HIGH + MID kapsamında)
for path in apps/social/architecture/history apps/social/templates \
            apps/social/architecture/template-system-design.md \
            apps/social/architecture/carousel-design.md \
            apps/social/architecture/marketingskills-entegrasyon.md \
            apps/social/pipeline/carousel.md \
            cross-project/infrastructure cross-project/databases \
            cross-project/integrations cross-project/copywriting \
            cross-project/vendors apps/crm/architecture; do
  grep -rL "verification-status: a-verified" /root/otomaix-brain/$path
done
# Boş dönmeli

# Hiç conflict kalmamalı (tüm vault)
grep -r "verification-status: conflict" /root/otomaix-brain/
# Boş dönmeli
```

### Spot cold test

3 random HIGH sayfa seç (preferably değişik kaynak dosyalardan):
- Örnek seçim: 1 phase report + 1 template + 1 architecture sayfası

Her biri için sayfada cevabı olan ama doğrudan başlık olmayan soru hazırla. Örnek:
- *"Carousel slide'ları overlay konumlandırması nasıl belirleniyor?"* (carousel-design'da var)
- *"Hangi Phase'de Paddle entegrasyonu yapıldı?"* (phase-3 veya phase-4'te)
- *"Özel gün video şablonunda hangi I2V modeli kullanılıyor?"* (ozelgun-shortvideo-sablon'da)

**Yeni Claude Code oturumu** aç (gerçek cold), soruyu sor.

**Cevap kriterleri:**
- ✅ Vault'tan geldi (Read tool ile vault sayfası okundu)
- ✅ Cevap `[[wikilink]]` citation içeriyor
- ✅ İçerik kaynakla (orijinal _archive dosyasıyla) tutarlı — attribution doğru

**Sonuç matrisi:**

| Sonuç | Yorum | Aksiyon |
|---|---|---|
| 3/3 doğru | Vault güvenilir | Faz I ✅ |
| 2/3 doğru | Bir kaçak hata var | Bulunan hata düzeltilir, 2 yeni random ile re-test |
| ≤1/3 doğru | Sistemik problem hâlâ var | Faz I tekrar açılır, root cause analizi |

### Final adımlar (çıkış kriteri sağlandıktan sonra)

1. Vault commit: `vault: faz-I re-migration complete (NN pages verified)`
2. `log.md` entry: `## [YYYY-MM-DD HH:MM] re-migrate | Faz I tamamlandı` + özet
3. Plan dosyası Implementation Progress tablosunda Faz I ✅
4. Memory `project_otomaix_brain_phases.md` güncelle: Faz 1 + Faz I durumu

---

## 10. Plan dosyası yapısı

Mevcut `docs/plans/2026-05-12-otomaix-brain-faz1-impl.md` dosyasına yeni bölüm eklenir:

```
[mevcut Faz 1 içeriği — Task 1-25]

---

# Faz I — B+A Re-migration

## Implementation Progress (Faz I)
| Phase | Tasks | Durum |
|---|---|---|
| Hazırlık | H1, H2 | (sıradaki) |
| HIGH-tier | T1-T4 | |
| MID-tier | T5-T8 | |
| Verification | T9 (cold test) | |

## Hazırlık
### H1: Vault CLAUDE.md schema update
### H2: Batch frontmatter ekleme

## Task 1: Phase 6 (B+A pipeline test + bilinen hata düzeltmesi)
## Task 2: 07-template-system Bölüm 2+3 (7 HIGH)
## Task 3: Phase 1, 2, 3, 4 reports (4 HIGH)
## Task 4: Carousel + marketingskills-entegrasyon (3 HIGH)
## Task 5: 00-platform-mimari (7 MID)
## Task 6: 11-marketingskills copywriting (6 MID)
## Task 7: 07-template-system vendors (6 MID)
## Task 8: 05-crm-admin (4 MID)
## Task 9: Spot cold test (3 random HIGH)
```

Her task'ın step-step alt detayları `/write-plan` ile yazılır (her step için pre-check + action + post-check verification).

### Commit stratejisi

| Operasyon | Commit |
|---|---|
| H1: Schema update | `vault: add verification-status field to schema (Faz I prep)` |
| H2: Batch frontmatter | `vault: batch verification-status: unverified to 115 pages` |
| Task N: kaynak grubu re-migrate | `vault: re-migrate <kaynak> (N pages B+A / sadece A)` |
| Critical mismatch düzeltme | `vault: fix critical mismatch in <sayfa> (Faz I task N)` |
| Cold test sonucu | log.md entry, commit yok (sonuç pozitifse) |
| Faz I bitişi | `vault: faz-I re-migration complete (38 pages verified)` |

Otomaix repo commit'leri:
- Faz I başlangıcında: `docs: add Faz I (B+A re-migration) plan` (spec + plan güncellemesi)
- Faz I bitişinde: `docs: mark Faz I complete in implementation plan`

---

## 11. Risk değerlendirmesi

### Mekanizmanın hatasız olmama olasılığı

Subagent de LLM — %100 hata yakalama garanti değil. Beklenen yakalama oranı:

- **Critical attribution hatası:** ~%90 yakalama (Phase 6 tipi hata kaynak yan yana okundukça yakalanır)
- **Minor:** ~%70 yakalama (subagent attribution-prone listede olmayan ufak farklılıkları kaçırabilir)
- **Cosmetic:** ~%50 yakalama (kapsam dışı)

**Kalıcı hata oranı tahmini:** Faz I sonrası ~%5 (Faz 1 öncesi ~%30 tahmini). Cold test bu kalanı sample ile yakalar.

### Faz I'in kaçıracağı şeyler

- LOW kategorisinde audit edilmeyen 77 sayfa — kararsız ama düşük risk (kaynak zaten kısa, atama hatası fırsatı az)
- Frontend/backend code referansları (vault sayfaları "şu kod şurada" diyor → kod değişirse vault stale) — bu Faz I kapsamında **değil**, periyodik lint'in işi

### Faz I sırasında çıkabilecek bilinmeyenler

- Bazı HIGH sayfaların gerçek hata yoğunluğu bilinmiyor → süre tahmini ±%50 sapabilir
- Critical mismatch sayısı belirsiz → kullanıcı onay yükü 30 dk veya 2 saat olabilir
- Subagent rapor formatına uyum bazen aksayabilir → ben her raporu parse etmeli, format dışı çıktı varsa subagent'a re-prompt

### Önlemler

- Her task sonunda log.md entry — yarım kalırsa nerede kalındığı net
- `verification-status` frontmatter alanı = sayfa-bazlı state, grep ile filtre çalışır
- Cold test (Task 9) sistemik problem var mı son kez yoklar
- Faz başlamadan bu spec gözden geçirilir; spec değişikliği = re-spec, plan değişikliği = re-plan

---

## 12. Out of scope

Faz I'in **kapsam dışı** olduğu konular:

- **Yeni sayfa yazma** — Faz I sadece mevcut sayfa düzeltmesi
- **LOW kategorisi (77 sayfa)** — bilinçli olarak skip
- **Periyodik lint operasyonu** — Karpathy schema'sında haftalık iş, faz dışı
- **Code → vault sync** — Otomaix repo'sundaki kod değişiklikleri vault'a otomatik yansımaz, ayrı sistem (ileride)
- **Hermes / inbox** — Faz 2 işi
- **Faz I sonrası periyodik re-verification** — yapılırsa ileride yeni faz olarak

---

## 13. Sonraki adım

Spec onayı sonrası: `/write-plan` invoke → mevcut plan dosyasının sonuna Faz I bölümü eklenir, her task step-by-step expand edilir.
