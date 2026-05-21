---
title: Otomaix Brain Doctor v1 — Vault Sağlık Denetçisi
status: spec-approved
date: 2026-05-21
tags: [tooling, vault, brain-doctor, health-check]
codex_review_status: approved
codex_review_iterations: 2
codex_review_log: docs/reviews/codex/2026-05-21-otomaix-brain-doctor.md
---

# Otomaix Brain Doctor v1 — Vault Sağlık Denetçisi

## 1. Amaç & Bağlam

`otomaix-brain` vault'u (canonical bilgi kaynağı) bakımı şu an elle yapılıyor.
CLAUDE.md'nin 6 disiplin ilkesinin yarısı drift/verification üstüne — bu manuel
disiplini **deterministik bir araca** çeviriyoruz.

**Referans:** nexus-ai-memory'nin `engine/nexus_doctor.py`'si (saf stdlib wiki
health checker). **Sadece desen alınır**, kod birebir kopyalanmaz (Portekizce,
path/infra bağımlı). Otomaix'in gerçek frontmatter şemasına + Türkçe vault'a
uyarlanır.

**Bu V1.** Sektör bilgi tabanı doctor'ı (sector-pack ruleset) **aynı aracın**
sonraki dalgasıdır, bu spec'e dahil değil. Araç config-driven kurulur ki sektör
kuralları o şema doğunca eklenebilsin.

## 2. Kapsam

**v1 = SADECE yapısal denetim.** Markdown/frontmatter/link yapısı; semantik
içerik değil.

### v1 KAPSAM DIŞI (→ v2/v3)
- "vault X diyor, kod Y yapıyor" semantik drift
- kaynak attribution doğruluğu (sources gerçekten o iddiayı destekliyor mu)
- LLM ile claim-level contradiction
- sektör pack kalite değerlendirmesi
- caption/copywriting kalite skoru
- stub "doldurma tetiği karşılandı mı" tespiti (semantik → v2)

## 3. Mimari

- **Tek-dosya stdlib Python CLI** (`tooling/brain-doctor/brain_doctor.py`).
  Sıfır dış bağımlılık (sadece `argparse, json, re, pathlib, datetime`).
  Vektör DB / LLM **YOK**.
- **Config dosyası:** `tooling/brain-doctor/brain_doctor.config.json` — stale
  kuralları, zorunlu frontmatter, enum'lar, excludes, severity eşlemesi, eşikler
  **data olarak** burada durur. Sektör ruleset sonra aynı yapıya eklenir.
- **Vault'a karşı read-only.** Araç, denetlediği vault'a default'ta HİÇBİR ZAMAN yazmaz; v1'de `--fix` YOK. Rapor default'ta **repo'ya** yazılır (vault'a değil) — bkz §8.
- Kod yeri `tooling/` — Social/CRM runtime parçası değil, `apps/` altına konmaz.

### Neden tek-dosya (paket değil)
~11 kontrol için tek dosya + check fonksiyonları listesi yeterli; config-driven
olduğu için genişleme data düzeyinde karşılanıyor. Gerçekten büyürse pakete
refactor ucuz (YAGNI / code-restraint).

## 4. Gerçek Vault Verisi (grounded — 2026-05-21 taraması)

Kurallar gerçek **değer setlerine** oturur. ⚠️ Sayımlar **2026-05-21 snapshot'ı —
bilgilendirme amaçlı, implementation invariant DEĞİL** (vault büyür, sayım değişir;
güncel sayımı araç kendisi üretir). Stable invariant = enum **değer setleri** +
exempt dosyalar. Sayımlar frontmatter-parse ile alındı (gövdedeki örnek `key:`
satırları sayılmaz — grep şişmesinden kaçınıldı).

| Alan | Değer seti (invariant) | Snapshot (2026-05-21, bilgi) |
|---|---|---|
| `type` | decision, concept, vendor, template, history, research | 76 / 23 / 7 / 6 / 5 / 1 |
| `verification-status` | a-verified, unverified — ikisi de geçerli; **unverified hata DEĞİL** | 41 / 77 |
| `status` | active, completed, superseded, stub, frozen | 107 / 5 / 3 / 2 / 1 |
| frontmatter alanları | title, type, status, tags, sources, verification-status, last-verified (zorunlu); area (opsiyonel) | 118 frontmatter'lı / 123 toplam .md; last-verified: 117 |
| `sources: []` (boş) | — | 0 sayfa (kural şu an önleyici) |

**Frontmatter'sız dosyalar (exempt allowlist):**
`log.md`, `AGENTS.md`, `index.md`, `CLAUDE.md`, `inbox/README.md`

**Klasör taksonomisi:** `apps/{social,crm}`, `cross-project/{copywriting,
databases, economics, infrastructure, integrations, vendors}`, `decisions`,
`inbox`, `research`, `sources/research`. (history: `apps/social/architecture/history`)

## 5. Config Şeması (`brain_doctor.config.json`)

```json
{
  "vault_path": "/root/otomaix-brain",
  "default_report_dir": "tooling/brain-doctor/reports",
  "exclude_globs": ["_health/**", ".git/**", "**/assets/**", "**/.obsidian/**"],
  "exempt_files": ["log.md", "AGENTS.md", "index.md", "CLAUDE.md", "inbox/README.md"],

  "required_frontmatter": ["title", "type", "status", "tags", "sources", "verification-status", "last-verified"],
  "optional_frontmatter": ["area"],

  "enums": {
    "type": ["decision", "concept", "vendor", "template", "history", "research"],
    "status": ["active", "completed", "superseded", "stub", "frozen"],
    "verification-status": ["a-verified", "unverified"]
  },

  "stale_rules": [
    { "glob": "decisions/**", "stale_days": null },
    { "glob": "apps/social/architecture/history/**", "stale_days": null },
    { "glob": "cross-project/vendors/**", "stale_days": 30 },
    { "glob": "apps/social/templates/**", "stale_days": 30 },
    { "glob": "cross-project/infrastructure/**", "stale_days": 45 },
    { "glob": "cross-project/copywriting/**", "stale_days": 60 }
  ],
  "default_stale_days": 45,

  "min_content_chars": 100,

  "severity": {
    "broken_wikilink": "error",
    "broken_md_link": "error",
    "ambiguous_link": "error",
    "index_mismatch_missing_file": "error",
    "frontmatter_absent": "error",
    "frontmatter_missing_field": "warning",
    "invalid_enum_value": "warning",
    "stale": "warning",
    "unresolved_conflicts": "warning",
    "empty_or_short": "warning",
    "sources_missing": "warning",
    "sources_empty": "info",
    "page_not_in_index": "warning",
    "orphan": "info",
    "stub": "info",
    "deprecated_visibility": "info"
  }
}
```

**Stale çözümleme:** Yalnız `status: active` sayfalara uygulanır. İlk eşleşen
glob kazanır; `stale_days: null` → muaf; eşleşme yoksa `default_stale_days`.
`status` ∈ {superseded, completed, frozen, stub} → stale denetimi atlanır.

## 6. Kontroller (v1)

> **Kategori ID kuralı:** Aşağıdaki ID'ler `config.severity` anahtarlarıyla **birebir**
> aynıdır (tek kanonik isim seti). Test: emit edilen her kategorinin `config.severity`'de
> karşılığı olmalı — eksikse build fail (yanlış-negatif / exit-code kaçağı önlenir).

| # | Kategori ID | Severity | Kural |
|---|---|---|---|
| 1 | broken_wikilink | error | `[[hedef]]` vault sayfasına çözülmüyor |
| 2 | broken_md_link | error | İç markdown linki (`./x.md`, `../y`) çözülmüyor |
| 3 | ambiguous_link | error | Basename birden fazla sayfada → çözüm belirsiz (§7) |
| 4 | index_mismatch_missing_file | error | `index.md` var olmayan sayfaya atıf veriyor |
| 5 | page_not_in_index | warning | Sayfa var ama `index.md` kataloğunda yok |
| 6 | frontmatter_absent | error | Non-exempt sayfada frontmatter bloğu hiç yok |
| 7 | frontmatter_missing_field | warning | Zorunlu alan eksik (required_frontmatter) |
| 8 | invalid_enum_value | warning | type/status/verification-status enum dışı değer |
| 9 | stale | warning | active sayfa, last-verified eşiği aşmış (§5) |
| 10 | unresolved_conflicts | warning | "## ⚠️ Conflicts" başlığı + unresolved/çözülmedi metni (exempt_files hariç — meta dosyalar conflict kuralını anlatır, kendileri conflict değil) |
| 11 | empty_or_short | warning | Gövde (frontmatter sonrası) < min_content_chars |
| 12 | sources_missing | warning | sources alanı yok |
| 13 | sources_empty | info | sources var ama `[]` |
| 14 | stub | info | `status: stub` sayfaları listele |
| 15 | orphan | info | Hiç inbound link almayan sayfa (exempt + index/log hariç) |
| 16 | deprecated_visibility | info | superseded/deprecated sayfa index'te → "policy candidate" notu, hata değil |

## 7. Link Çözümleme Kuralları (Codex risk #2)

Kod blokları (``` ``` ` ```` ` ```) link çıkarımı öncesi temizlenir (false-positive önler).

**Kontrol edilen:**
- Obsidian `[[hedef]]`, `[[hedef|alias]]`, `[[hedef#anchor]]` — anchor/alias soyulur
- Markdown iç link `[text](path)` — path `/` veya `.md` içeriyorsa iç sayılır

**Çözümleme sırası (path-temelli denemeler basename fallback'ten ÖNCE):**
1. Exact vault-relative path (yazıldığı haliyle)
2. Exact path + `.md` ekli — **extensionless full-path linkler için** (vault `[[apps/crm/architecture/deploy]]` kullanıyor)
3. Source dizinine göre relatif (yazıldığı haliyle ve `.md` ekli)
4. **basename fallback YALNIZ path-ayracı (`/`) İÇERMEYEN hedefler için** ve sadece **benzersizse** geçerli; basename birden fazla sayfada → `ambiguous_link` (error)

**Path-qualified hedef (`/` içeren) 1-3 ile çözülmezse → `broken_wikilink`/`broken_md_link` (basename'e DÜŞÜRÜLMEZ).** *Gerekçe:* açık path açık path olarak doğrulanır; aksi halde typo'lu `[[apps/crm/wrong/deploy]]` başka bir `deploy.md`'ye sahte-çözülür (yanlış-negatif — aracın temel invariant'ı bozulur). `ambiguous_link` yalnız basename-only hedefler için. Tam-nitelikli link (`apps/crm/architecture/deploy`) 2. adımda exact+`.md` ile çözülür → yanlışlıkla ne ambiguous ne broken sayılır.

**ATLANIR (kırık link sayılmaz):**
- `http`/`https`/`mailto` (dış URL)
- Saf anchor (`#...`)
- **Kaynak-atıf ref'leri:** `@/...`, `@docs/...` ile başlayanlar — bunlar `sources`
  alanı + satır-içi citation'lar; vault sayfası DEĞİL, repo/arşiv dosyalarına işaret eder.

## 8. CLI Davranışı

```
brain-doctor [--vault PATH] [--config PATH] [--output-dir DIR] [--allow-vault-output] [--json] [--no-report] [--min-severity LEVEL]
```

- `--vault` default `/root/otomaix-brain`
- `--config` default `tooling/brain-doctor/brain_doctor.config.json`
- `--output-dir` default `tooling/brain-doctor/reports/` — **repo köküne göre çözülür** (config dosyası / git toplevel dizini), **cwd'ye göre DEĞİL**. Hangi dizinden çalışırsa çalışsın vault'a yazmaz.
- `--allow-vault-output` olmadan, çözülen çıktı yolu `vault_path` altına düşerse araç **reddeder** (vault-output guard). Vault'a yazma yalnız `--output-dir <vault>/_health --allow-vault-output` ile
- `--json` stdout'a JSON bas (dosya yazma)
- `--no-report` sadece konsol özeti, dosya yazma
- `--min-severity` filtre (error|warning|info)
- **`_health/` her zaman scan dışı** (doctor kendi raporunu denetlemesin)
- **v1'de `--fix` YOK** (read-only). Önce ilk rapor sınıflandırılır → güvenli fix kapsamı v1.1'de belirlenir.

**Exit code:** `0` = error yok | `1` = ≥1 error | `2` = tool/config/IO hatası.
(warning/info exit 0'ı bozmaz.)

**Codex write-boundary:** Default çıktı **repo'ya** gider (vault'a değil) → Codex
çalıştırması da güvenli, vault'a yazmaz. Repo'ya bile yazmak istemezse `--json`/
`--no-report` (stdout). Vault `_health`'e yazma yalnız açık `--output-dir` ile.

**Tetik:** manuel CLI + `/brain-doctor` slash command. Otomatik cadence (cron/n8n) → v2.

## 9. Çıktı Formatı

- **`report.md`** — insan için: kategoriye göre gruplu, severity ikonları (🔴 error,
  🟡 warning, 🔵 info), üst özet (toplam sayfa, error/warning/info sayısı, durum).
- **`report.json`** — makine için: `{generated, total_pages, issues: [{severity,
  category, page, detail, line?}]}`. CI/otomasyon ileride bunu okur.

## 10. Test Yaklaşımı

- **Unit:** her kontrol için küçük fixture vault (geçici tmp dizin) — kasıtlı kırık
  link / eksik frontmatter / enum-dışı değer / bayat tarih içeren mini sayfalar.
- **Smoke:** gerçek `/root/otomaix-brain` üstünde çalıştır, exit code + rapor üretimi
  doğrulanır (bilinen mevcut bulgularla — örn. çözülmemiş ⚠️ Conflicts sayfaları).
- Sıfır-bağımlılık iddiası **testlere de uygulanır** → testler stdlib `unittest` (`python -m unittest`); pytest gibi dış test-dep eklenmez (runtime ve test dep'i ayrı ama ikisi de stdlib).

## 11. Bilinen Açık Noktalar / Riskler (Codex Adım 6 için)

- `default_stale_days: 45` — glob'a girmeyen klasörler (databases, economics,
  integrations, research, sources, apps/social/architecture non-history) için
  makul mü? İlk rapordan sonra ayarlanabilir.
- `page_not_in_index` (warning): index.md tüm sayfaları katalogluyor mu, yoksa bazı
  alt sayfalar bilinçli mi dışarıda? Yanlış-pozitif riski — ilk raporla kalibre edilir.
- `index_mismatch_missing_file` parse: index.md hem `[[wikilink]]` hem backtick `\`path.md\``
  formatı kullanıyor olabilir (nexus'ta ikisi de vardı) — ikisi de taranmalı.
- `unresolved_conflicts` parse: "Status: unresolved" / "🔴 Not resolved" /
  "çözülmedi" varyantları — gerçek vault sayfalarından doğrulanmalı.
- Enum genişletilebilirliği: yeni `type`/`status` değeri config'e eklenene kadar
  warning üretir (bilinçli — typo yakalama).

## 12. Sonraki Adımlar (bu spec dışı)

- v1.1: güvenli `--fix` (sadece frontmatter iskeleti, dry-run zorunlu)
- v2: otomatik cadence, stub trigger tespiti, sektör-pack ruleset
- v3: semantik katman (kod-vault drift, contradiction) — ayrı spec
