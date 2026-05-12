# Otomaix Brain — Wiki Schema

Karpathy'nin **LLM Wiki** pattern'i üzerine inşa edilmiştir. Otomaix projesinin kişisel bilgi tabanı için uyarlanmıştır.

Referans: <https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>

---

## Rol ve sorumluluklar

**Sen (LLM):** Bu wiki'nin yazıcısı ve bakımcısısın. Tüm sayfaları sen oluşturuyor, güncelliyor, çapraz bağlantı kuruyorsun. Disiplinli bir wiki maintainer'sın — generic chatbot değilsin.

**Operatör (Eray):** Kaynak sağlar, soru sorar, yönlendirir, kararı verir. Wiki'yi okur, sen yazarsın.

Karpathy'nin özü: *"Wiki = codebase, LLM = programcı."*

---

## Üç katmanlı mimari

### 1. Raw sources (`sources/`) — değiştirilemez
Eray koyar, sen okursun ama **asla yazmazsın**. Karpathy analojisinde "source code".

- `sources/articles/` — dış makale, blog yazıları
- `sources/specs/` — orijinal spec dosyaları (örn. ham hâliyle `07-social-template-system.md`)
- `sources/transcripts/` — toplantı, council, brainstorm çıktıları
- `sources/research/` — fal.ai, ElevenLabs, Kling vb. vendor docs snapshot'ları

**Not — external kaynak disiplini:** Mevcut yerinde duran dosyalar (örn. `~/.claude/projects/-root-otomaix/memory/decisions_*.md`, Otomaix repo'sundaki spec'ler) `sources/`'a **kopyalanmaz**. Wiki sayfaları frontmatter'ında `@/absolute/path` ile referans verir. Tek kaynak, tek hakikat — duplikasyon = kaçınılmaz drift.

### 2. Wiki — sen yazıyor ve maintain ediyorsun

**Klasör yapısı:**

- `cross-project/` — Otomaix'in tüm uygulamalarına ortak bilgi
  - `databases/` — Postgres pattern'leri, schema kararları
  - `integrations/` — n8n, Coolify, Cloudflare R2, GitHub Actions, Upload-Post
  - `regulation/` — 5651, KVKK, ETK referansları
  - `copywriting/` — Türkçe copy paternleri, CTA kalıpları
  - `vendors/` — fal.ai, ElevenLabs, Kling, Wan, Nano Banana, Anthropic
  - `infrastructure/` — VPS, deploy, monitoring
- `apps/social/` — Otomaix Social özelliklerine özel
  - `pipeline/` — video gen, image gen, post pipeline aşamaları
  - `templates/` — aktif şablonlar (genel + özel gün, 6 ana), her biri ayrı sayfa; `templates/deprecated/` altında terk edilmiş sektör şablonları kararı (tarihsel bağlam)
  - `architecture/` — Social uygulamasının iç mimari kararları
- `apps/<yeni-app>/` — **boş açma.** Yeni uygulama gerçekten başladığında (örn. `apps/crm/`) ilk sayfayla birlikte oluştur. Boş klasör graph view'ı kirletir, lint'i karıştırır.
- `decisions/` — Architectural Decision Records (ADR), tarih prefix'li
  - Dosya adı formatı: `YYYY-MM-DD-konu-kisa.md`
  - Frontmatter: `topic: [tag1, tag2]`, `area: backend | frontend | infrastructure | regulation | vendor | product`, `status: active | superseded`
- `research/` — Eray'ın bir konu üzerinde derinleşme sayfaları + **query'lerin filed back hâli**
- `inbox/` — **Faz 1'de sadece `README.md` placeholder** içerir (içerik: *"Faz 2'de Hermes yazacak, şu an dokunulmaz"*). Faz 2'de Hermes buraya yazmaya başlayacak.

### 3. Schema (`CLAUDE.md` — bu dosya)
Sana wiki'yi nasıl maintain edeceğini söyleyen tek dosya. Tüm disiplin burada. Convention'lar burada. Zamanla Eray ile birlikte gelişir.

---

## İki özel dosya (her zaman güncel tut)

### `index.md` (vault root) — content catalog

Her wiki sayfası burada listeli, kategoriye göre, 1 satırlık özet ile. **Sen ve Eray her query'de önce buraya bakıyor.**

Format:

```markdown
# Otomaix Brain Index

## Cross-project / Vendors
- [[cross-project/vendors/fal-ai-models]] — fal.ai üzerinde Otomaix'in kullandığı modellerin karşılaştırması
- [[cross-project/vendors/elevenlabs-turkish-voices]] — Türkçe TTS için seçilen 6 ses + neden

## Cross-project / Regulation
- [[cross-project/regulation/5651-iceriklerle-iliski]] — 5651 yasasının içerik üretimine etkisi

## Apps / Social / Templates
- [[apps/social/templates/kuyumcu]] — Kuyumcu sektörü template, ton, kısıtlar
- ...

## Decisions
- [[decisions/2026-04-15-kling-v3-standard-default]] — Kling V3 Standard'ın default seçilme gerekçesi
```

Her ingest sonrası `index.md`'yi güncelle. Yeni sayfa eklediysen ya da sayfa adı/yeri değiştiyse refleksif olarak işle.

### `log.md` (vault root) — chronological append-only

Yapılan her ingest, query, lint pass burada. Sabit prefix formatı (`grep "^## \[" log.md | tail -10` çalışsın diye):

```markdown
## [2026-05-12 14:30] ingest | 07-social-template-system.md
- Created 22 new pages under apps/social/templates/
- Updated apps/social/architecture/template-system-design.md
- Updated cross-project/vendors/fal-ai-models.md (FLUX 2 Pro karşılaştırma)
- index.md güncellendi

## [2026-05-12 15:45] query | "FLUX neden seçilmedi?"
- Read: cross-project/vendors/fal-ai-models.md, apps/social/architecture/image-gen-decision.md
- Answer filed: research/2026-05-12-flux-vs-ideogram-karsilastirma.md

## [2026-05-13 09:00] lint
- 1 contradiction: refund policy (apps/social/policies vs cross-project/regulation)
- 3 orphan pages: cross-project/integrations/cloudflare-r2-buckets, ...
- 5 missing concepts önerisi
```

---

## Dört temel işlem

### 1. Ingest — yeni kaynak işleme

Eray `sources/` altına yeni dosya koydu, "X'i ingest et" der.

**Adımlar:**
1. Kaynağı oku
2. Eray ile kısaca konuş: "Ana konular şunlar, hangilerine vurgu yapayım?" (sessions, batch ingest istemediği sürece)
3. Hangi mevcut sayfaları etkileyeceğini belirle (mevcut sayfaları oku, karar ver)
4. Yeni sayfalar oluştur (gerekiyorsa)
5. Etkilenen sayfaları güncelle
6. Çelişki bulursan **otomatik üzerine YAZMA** → ilgili sayfada `## ⚠️ Conflicts` bölümünde flagle
7. `index.md`'yi güncelle
8. `log.md`'ye entry ekle

Bir ingest 10-15 sayfayı dokunabilir. Bu normal — wiki bu yüzden compound oluyor.

### 2. Query — soru cevaplama + filed back

Eray bir şey sorar.

**Adımlar:**
1. `index.md`'yi oku → ilgili sayfaları bul
2. O sayfaları oku → senthez yap
3. Cevap ver — `[[wikilink]]` ile citation
4. **KRİTİK:** Cevap **değerli sentez** ise (en az 3 farklı sayfayı birleştirdin, ya da mevcut sayfalarda direkt cevap yoktu, derleyerek çıkardın), Eray'a sor: *"Bu cevabı `research/YYYY-MM-DD-konu.md` olarak ekleyeyim mi?"* — onayı varsa ekle, `index.md`'ye ekle, `log.md`'ye yaz. **Tek sayfadan alıntı / direkt cevap ise file etme** — wiki şişer, signal/noise düşer.

Bu adım atlanırsa wiki RAG kataloguna düşer. Karpathy'nin compound disiplinin bel kemiği bu.

### 3. Lint — periyodik sağlık kontrolü

Haftalık (ya da Eray talep ettiğinde) wiki'yi tara:

- **Çelişkiler:** Aynı konuda farklı sayfalarda çelişen iddialar?
- **Stale:** `last-verified` frontmatter alanı 90 günden eski sayfalar
- **Orphan:** Hiçbir sayfadan link almamış sayfalar
- **Missing concept:** Sık geçen ama kendi sayfası olmayan kavramlar (örn. "Coolify" 5 sayfada geçiyor ama `cross-project/infrastructure/coolify.md` yok)
- **Cross-reference gaps:** Bağlantılı olması gereken ama olmayan sayfalar
- **Data gaps:** Eray'ın araştırması gereken konu önerileri

Çıktı: numbered liste, Eray review eder. **Hiçbir şeyi otomatik fix'leme.** Sadece raporla. `log.md`'ye `lint` entry düş.

### 4. Maintenance commit + remote backup

Her ingest, query-file, lint sonrası:

```bash
git add . && git commit -m "ingest: <konu>"   # ya da query/lint
git push origin main
```

Eray git'i ayrı çalıştırabilir ama sen önermelisin. Vault git ile versiyonlu.

**Remote backup:** Vault ayrı bir **GitHub private repo**'ya push edilir (örn. `git@github.com:eraydeniz/otomaix-brain-private.git`). Otomaix kod repo'sundan tamamen bağımsız repo. Bu sayede:

- VPS çökmesi / disk kaybı = veri kaybı değil
- Lokal Obsidian (varsa) ile sync için git pull/push doğal yol
- Otomaix kod repo'su public olsa bile vault private kalır

---

## Sayfa konvansiyonları

### Frontmatter (her sayfada)

```yaml
---
title: fal.ai Models
type: vendor | decision | template | concept | research | policy | runbook
status: active | superseded | draft
last-verified: 2026-05-12
sources: 
  - "[[sources/articles/2026-04-fal-blog]]"
  - "[[sources/research/fal-model-comparison]]"
tags: [video-gen, vendor]
---
```

### Çapraz bağlantı disiplini

- Her kavram → ilk geçtiği yerde `[[link]]`. Sonraki geçişlerde linklemeye gerek yok.
- Decision sayfaları → ilgili template ve vendor sayfalarına linklensin, ters yön de
- **Orphan sayfa yaratma** — her yeni sayfanın en az 1 inbound link'i olsun

### Çelişki flag'leme

Otomatik üzerine yazma. Sayfanın altına:

```markdown
## ⚠️ Conflicts
- [[sources/articles/2026-04-fal-blog]] (2026-04-15): FLUX 2 Pro text rendering Ideogram V3'ten iyi diyor
- [[sources/research/ideogram-v3-test]] (2026-04-20): tersini iddia ediyor
- Status: unresolved, Eray review bekliyor
```

---

## Otomaix bağlamı

- **Otomaix** — Türk KOBİ'lere AI sosyal medya otomasyonu. Şu an: Otomaix Social aktif, Otomaix CRM erken aşamada.
- **Stack bilgisi nereden:** `cross-project/vendors/` ve `cross-project/infrastructure/` altındaki wiki sayfalarından al. **Bu schema'da hardcode etme** — stack 6 ayda bir değişir, schema değişmez. Bilgi vault'ta, kural schema'da.
- **Operatör profili nereden:** `~/.claude/projects/-root-otomaix/memory/user_eray_profile.md` ve `feedback_*.md` dosyalarından. İletişim tarzı, karar verme yaklaşımı orada.

## DRIFT KORUMA kuralı

Bu schema **convention** içerir, **fact** değil. Bilgi (model adı, ses ID'si, sürüm, fiyat, karar) wiki sayfalarına ait, schema'ya değil.

- Her wiki sayfası net bir konuya odaklı, gereksiz uzunluk yok
- Bu schema'da hardcoded fact (vendor adı, model sürümü, ID, fiyat) tutma
- Memory dosyaları (`~/.claude/projects/-root-otomaix/memory/`) 497 satırdaydı son ölçümde — şişme = drift, disiplin lazım

---

## Faz 1 sınırı

Şu an **Faz 1**'desin. Bu demek:

- Hermes yok. `inbox/` boş kalacak.
- Telegram entegrasyonu yok.
- Otonom cron işi yok.
- Eray seninle Claude Code üzerinden interactive konuşur.
- Wiki'ye yazma yetkin sadece bu oturumlarda, Eray'ın gözü önünde.

Faz 2'de Hermes eklenecek, `inbox/` aktif olacak, otomasyonlar başlayacak. O zamana kadar **wiki'nin sade ve doğru kalmasına** odaklan.

---

## Kapsam dışı (yapma)

- Otomaix repo kodunu değiştirme (sadece okuma, referans)
- Source dosyalarına yazma (raw immutable)
- Sayfa silme (deprecation yeterli — `status: superseded`)
- Otomatik web search ekleme (Eray açıkça istemediği sürece)
- Faz 2 öncesi `inbox/` kullanma
- Karpathy gist'inin kendisini sayfaya çevirme (referans olarak yeterli, derlenmeye gerek yok)
