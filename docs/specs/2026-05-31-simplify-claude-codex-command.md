---
title: simplify-claude-codex.md komut tasarımı
status: spec-approved
date: 2026-05-31
tags: [slash-command, claude-codex-family, refactor, code-quality, drift-contract]
codex_review_status: approved
codex_review_iterations: 3
codex_targeted_fixes: 13
unresolved_high_severity_override: false
codex_review_log: docs/reviews/codex/2026-05-31-simplify-claude-codex-command.md
---

# simplify-claude-codex.md — Tasarım Spec

## Hedef

`~/.claude/commands/simplify-claude-codex.md` adında yeni custom slash command. Mevcut tek-aktörlü `~/.claude/commands/simplify.md` (Claude scan + Claude fix, 130 satır) **claude-codex ailesine** (spec-claude-codex / write-plan-claude-codex / execute-plan-claude-codex) entegre edilir.

**Rol modeli:** Claude basitleştirme adaylarını seçer ve fix uygular; Codex iki noktada review eder — opsiyonel pre-scan (`task --fresh`) + zorunlu final adversarial review (`adversarial-review`). Codex hiçbir dosyaya yazmaz.

**Sonraki adım zinciri:** `/execute-plan-claude-codex` sonrası `/simplify-claude-codex` → `/review` → `/security-review` → closure (`/finish-branch`).

## İnvariant (komutun ana sözleşmesi)

> Codex final simplification review çalışmadan ve unresolved critical/high bulgular çözülmeden veya açık override edilmeden commit önerilmez.

Bu invariant Adım 11 commit gate'te zorla uygulanır. Push gate YOKTUR — push hiç sorulmaz.

## Mimari Yön: Y1/A (onaylandı)

**Seçilen:** Execute-plan-style küçük kuzen + eski simplify scanner kategorilerini selective reuse. Y1/A her iki perspektifte (Claude + Codex pre-scoping, [`docs/reviews/codex/2026-05-31-simplify-claude-codex-command.md`](../reviews/codex/2026-05-31-simplify-claude-codex-command.md)) önerildi.

**Reddedilen alternatifler:**

- **Y2/B — Minimal Codex graft on existing simplify** (`<DROPPED_ALT>`): Mevcut simplify gövdesini koru, sonuna Codex final + commit-gate sok. Reddedilme gerekçesi tradeoff tablosuyla (M1 düzeltmesi — sayısal "100-150 satır" argümanı önceki versiyonda zayıftı, Codex'in pre-scoping kritiği haklıydı):

  | Boyut | Y1/A (seçilen) | Y2/B (reddedilen) |
  |---|---|---|
  | Drift sözleşmesi yükü | 4-way (yeni `simplify-claude-codex` bloğu birebir kopya) | Yine 4-way zorunlu (`CODEX-CALL-PROTOCOL` graft gövdesine eklenmeli; aksi halde final review companion sözleşmesi dışında çalışır = invariant ihlali) |
  | Komut sayısı kullanıcı yüzünde | 1 (`simplify-claude-codex`) + stub | 1 (`/simplify` yaşar, içeride mode/guard) |
  | Migration deneyimi | Kullanıcı eski refleksle `/simplify` yazar → stub görür → yeni komuta geçer (bir defalık friction) | Kullanıcı eski refleksle `/simplify` yazar → eski isim ama farklı davranış (sessiz behavior change, sürpriz) |
  | Uzun vadeli bakım | Bir komut + 3 ayna güncellemesi senkron | İki ayrı kod yolu (eski simplify gövdesi + graft sandviç) — refine PR'larında ikisinde de aynı değişiklik gerekir |
  | Critical/high guard tutarlılığı | Aile pattern'ı birebir (execute-plan ile aynı) | Mevcut simplify state-loose; guard mantığını gövdeye sokmak retrofit (Codex pre-scoping risk #1: "loose state, loose scope accounting") |

  **Kalitatif karar:** 100-150 satır sayısal kazanç önemsiz; asıl mesele **sessiz behavior change'in sürprizi** vs **bir defalık stub friction**. Stub yaklaşımı kullanıcıya açık sinyal verir; graft sessizce davranış değiştirir. Aile tutarlılığı kayıp olduğunda refine PR'ları her komuta ayrı uyarlanır — drift riski **daha yüksektir**, daha düşük değil (Codex'in M1 endişesi ters yönden geçerli).

- **Y3/C — Wrapper/orkestratör:** `simplify.md` yaşar, `simplify-claude-codex` onu Codex sandwich'le sarar. Reddedildi çünkü deprecation stratejisinden sapma (iki komut yan yana yaşar) + drift sözleşmesi iki dosyalı sandviçte kaygan.

## 11 Adımlık Akış

```
1.  Scope belirle (arg | git diff | origin/main..HEAD | son 5 commit kullanıcı seçimi)
2.  Test suite preflight (komut + test dosyası varlığı tespit)
3.  Claude ön tarama (5 kategori + scope dışı dosyalar read-only context)
4.  Mode seçimi: Standard (Recommended) / Light + log dosyası setup (mkdir + ATTEMPT counter; ayrıntı Adım 4.5)
5.  (Yalnız Standard) Codex pre-scan — task --fresh; hibrit prompt
6.  Sentez + risk yükseltme + kullanıcı onayı sınıfa göre
7.  Fix uygulama (Claude yazar; Codex yazmaz; her fix veya mantıksal fix batch sonrası ilgili scoped verification çalışır)
8.  Final tests (full/declared test suite taze çalışır; PASS iddiası çıktı okunduktan sonra)
9.  Codex final adversarial review — adversarial-review $SCOPE; 8 maddelik prompt
10. Critical/high guard (Düzelt / Override / Durdur)
11. Commit gate + final rapor (Şablon A/B1/B2); push YOK; sonraki adım /review
```

**Adım 0 YOK:** Active context read atlandı. Simplify lifecycle/state yönetmiyor (resume kavramı yok); `docs/active/` okumak gürültü.

## Codex Çağrı Noktaları

| Adım | Çağrı | Amaç | Cadence |
|---|---|---|---|
| **5** | `task --fresh` | Hibrit pre-scan: 5 kategori + Other; DO_NOT_APPLY vetolar; CANDIDATE unlisted bağımsız adaylar | Yalnız Standard mode'da |
| **9** | `adversarial-review $SCOPE` | Final execution review — 8 madde + cross-file + new-file kontrolü | Her iki mode'da ZORUNLU |

Her iki çağrı ortak `CODEX-CALL-PROTOCOL` bloğunu izler (canonical = `spec-claude-codex`; bkz. Drift Sözleşmesi).

## Mode Davranışı (Adım 4)

| Mode | Adım 5 (pre-scan) | Adım 9 (final review) | Tahmini latency |
|---|---|---|---|
| **Standard (default — Recommended)** | Codex pre-scan çalışır | Codex final review zorunlu | 2 Codex turu |
| **Light** | Atla | Codex final review zorunlu | 1 Codex turu |

`AskUserQuestion` ile 2 seçenek. Standard default çünkü:
- Aile tutarlılığı (execute-plan da Standard cadence default)
- Review-gated invariant pre-scan'in adversarial değerini hesaba katıyor (Codex'in `DO_NOT_APPLY` sinyali default kazanılır)
- Light opt-in olarak hızlı yol kullanıcıdadır

Final review her iki mode'da zorunlu — review-gated invariant orada korunur.

## Adım 1: Scope Belirleme

Argüman varsa onu kullan (dosya yolu, dosya listesi, dizin). Yoksa default sıralama:

1. Uncommitted değişiklik varsa: `git diff` (working tree)
2. Yoksa: `git diff origin/main..HEAD` (branch'in yaptığı değişiklikler)
3. O da yoksa: son 5 commit (`git log --oneline -5` göster, kullanıcıya `AskUserQuestion` ile sor)

Kapsamı net göster:
> "Şu kapsam taranacak: <açıklama>. <X> dosya, <Y> satır değişmiş. Onay?"

`<SCOPE_FILES>` listesi sakla — Adım 3 tarama ve Adım 7 fix kapsamı buna göre.

**Initial dirty-tree flag (zorunlu — H2 bulgusu):** Adım 1 sonu `<INITIAL_TREE_DIRTY>` boolean'ını sakla:
```bash
[ -n "$(git status --short)" ] && INITIAL_TREE_DIRTY=true || INITIAL_TREE_DIRTY=false
```
Bu flag Adım 9 scope kararını ve Adım 11 no-fixes-applied rapor varyantını belirler — Adım 1 sonunda hesaplanmazsa dirty initial + no-fixes durumunda Codex final review hatalı atlanır, kullanıcı yalan "no changes" raporu alır (H2).

Ayrıca `<INITIAL_DIRTY_FILE_COUNT>` da sakla (rapor için): `git status --short | wc -l`.

## Adım 2: Test Suite Preflight

Fix'lere başlamadan önce test altyapısını tespit et:

- `package.json` `scripts.test` field
- `pyproject.toml` / `pytest.ini` / `tox.ini`
- `Makefile` `test` target
- Test dosyası sayısını grep'le (`*.test.*`, `*_test.go`, `test_*.py`, `*.spec.*`, vs.)

İki sonuç:

- **Test komutu + test dosyası VAR** → `<TEST_SUITE_PRESENT> = true`; normal akış. Adım 8 full suite çalıştırır.
- **Test komutu YOK veya test dosyası 0** → `<TEST_SUITE_PRESENT> = false`; üç downstream etkisi:
  1. Adım 7 fix sonrası "PASS" iddiası YASAK — sadece "lint/format OK, otomatik test doğrulaması yok" raporu
  2. Adım 6 sentez aşamasında high-risk adaylar **default block** (named override şartı)
  3. Adım 11 final rapor `verification: no automated tests` satırı + `high-risk-no-tests override: true|false`

## Adım 3: Claude Ön Tarama (5 Kategori)

`<SCOPE_FILES>`'i 5 kategori altında tara. Scope dışı dosyalar **read-only context** olarak okunabilir (cross-file DRY tespiti için) ama **değiştirilemez**.

### A) DRY (Tekrar eden bloklar)

- 3+ satırı geçen tekrarlar (aynı/çok benzer mantık)
- Copy-paste with minor changes
- Birden fazla yerde aynı magic value/literal

Kural: 3 benzer satır TAMAM. 4+ veya ısrarlı tekrar → soyutla.

### B) YAGNI (Erken soyutlama)

- Tek yerden çağrılan generic factory/helper
- "İleride lazım olabilir" parametreleri
- Kullanılmayan abstraction layer'ları
- Aşırı esnek tip tanımları

Kural: Soyutlama 3. tekrarda gelir, 1. yazımda değil.

### C) Naming (İsimlendirme)

- Tek harfli değişkenler (loop counter dışı)
- `process()`, `handle()`, `data`, `info` gibi muğlak adlar
- Dosya adı içeriği yansıtmıyor
- Proje convention'ından (Türkçe/İngilizce) sapma

### D) File size (Dosya boyutu)

- 500+ satır → inceleme şart
- 1000+ satır → bölme önerisi
- 1500+ satır → bölme zorunlu

### E) Dead/debug code (Ölü/gereksiz kod)

- Hiç çağrılmayan fonksiyonlar (grep ile doğrula)
- Yorum satırına alınmış eski kod
- 3+ aydır duran "TODO" → ya yap ya sil
- Kullanılmayan import'lar
- `console.log`, `print`, debug çıktıları

**Cross-file bulgular:** Scope dışı dosyalarda tespit edilen DRY/YAGNI'ler `<NOTED_EXTERNAL>` listesinde tutulur — Adım 11 raporunda ayrı bölümde gösterilir, **fix UYGULANMAZ**.

Her aday için minimum:
- `id` (kategori-N format, örn. `DRY-1`, `YAGNI-2`)
- kategori
- risk sınıfı (low/medium/high) — geçici, sentezde değişebilir
- kısa açıklama
- etkilenen dosya(lar)

## Adım 4: Mode Seçimi

`AskUserQuestion` ile iki seçenek (Standard ilk = Recommended). Sonuç `<MODE> ∈ {standard, light}`.

## Adım 4.5: Log Dosyası Setup (F6 düzeltmesi — chain integrity operasyonel kapı)

Adım 5 (pre-scan) veya Adım 9 (final review) hangisinin önce çalıştığından bağımsız olarak, **ilk Codex çağrısından önce** zorunlu setup:

```bash
mkdir -p docs/reviews/codex

DATE=$(date +%Y-%m-%d)
LOG_DIR=docs/reviews/codex
LOG_PREFIX="${LOG_DIR}/${DATE}-simplify-${SCOPE_SLUG}"

# Mevcut ATTEMPT dosyalarını say (glob safety: hiç dosya yoksa 0 döndürmek için):
ATTEMPT=$(ls ${LOG_PREFIX}-*.md 2>/dev/null | wc -l)
ATTEMPT=$((ATTEMPT + 1))

LOG_FILE="${LOG_PREFIX}-${ATTEMPT}.md"

# Log dosyasını yarat (ATTEMPT > 1 ise previous-attempt link ile başlat)
if [ "$ATTEMPT" -gt 1 ]; then
  PREV_ATTEMPT=$((ATTEMPT - 1))
  cat > "$LOG_FILE" <<EOF
Previous attempt: ${LOG_PREFIX}-${PREV_ATTEMPT}.md

---

# Codex Review Log — simplify-claude-codex run

Scope: <SCOPE_FILES>
Mode: <standard|light>
Initial tree state: clean | dirty (<INITIAL_DIRTY_FILE_COUNT> files)

EOF
else
  cat > "$LOG_FILE" <<EOF
# Codex Review Log — simplify-claude-codex run

Scope: <SCOPE_FILES>
Mode: <standard|light>
Initial tree state: clean | dirty (<INITIAL_DIRTY_FILE_COUNT> files)

EOF
fi

# Bundan sonra Adım 5 ve Adım 9 turn başlıklarını bu dosyaya append eder
```

Bu adım sayesinde:
- `docs/reviews/codex` klasörü mevcut olmadığında ilk append hatası alınmaz
- `<ATTEMPT>` deterministik hesaplanır (race condition normal kullanımda yok — tek kullanıcı, tek run)
- ATTEMPT > 1 ise previous-attempt link ilk Codex turn başlığından önce yazılı durumda — audit zincirinin ilk halkası garanti
- Log dosyası başlığı standart (scope, mode, initial tree state) — turn'ler eklendikçe context kaybolmaz

`<LOG_FILE>` değişkeni sakla; Adım 5, 9 turn append'leri ve Adım 10 override audit + Adım 11 rapor path'i hepsi buraya işaret eder.

## Adım 5: Codex Pre-scan (Yalnız Standard)

Light mode'da bu adım atlanır.

Standard mode'da `CODEX-CALL-PROTOCOL` ile `task --fresh` çağrılır. Codex'e Claude'un Adım 3 aday listesi + hibrit format kuralı verilir.

### Pre-scan Prompt Kuralı (Hibrit)

Codex'e iletilecek instructions:

- **Sınıflandırma:** 5 kategori kullan — `DRY` | `YAGNI` | `Naming` | `FileSize` | `DeadOrDebugCode`
- **Other bucket:** 5 kategoriye sığmayan ama simplification açısından önemli risk/aday → `Other` etiketi
- **Canonical token format (zorunlu, tüm akışta tek isim):** Aday `<id>` Adım 3'te atanan format: `<KATEGORI>-N` (örn. `DRY-1`, `YAGNI-2`, `OTHER-1`). Tüm token referansları (Adım 5 prompt, Adım 6 sentez, Adım 7 onay, raporlar) **birebir aynı `<id>`** kullanır — drift = sessiz veto kaybı.
- **Veto (DO_NOT_APPLY):** Claude'un listesindeki bir adaya itiraz için:
  ```
  DO_NOT_APPLY: <id>
  reason: <one-line reason>
  unless: <condition or none>
  ```
  `<id>` = Adım 3 aday id'siyle birebir aynı (örn. `DRY-1`). Format ihlali (örn. `DRY 1` boşluklu, `dry-1` lower-case, `DRY-` eksik N, vs.) **default block** olarak işlenir — Adım 6 sentez kuralı F.
- **Bağımsız aday (CANDIDATE):** Codex Claude listesinde olmayan bir aday görürse:
  ```
  CANDIDATE: unlisted:<short-title>
  category: <DRY|YAGNI|Naming|FileSize|DeadOrDebugCode|Other>
  risk: <low|medium|high>
  rationale: <one-line>
  ```
- **Veto + bilinmeyen aday:** Eğer veto Claude listesinde olmayan bir item için ise: `DO_NOT_APPLY: unlisted:<short-title>` formatı kabul edilir; Claude bunu sentez aşamasında ayrı risk olarak gösterir.

**Max:** 5 aday + 5 veto + 5 unlisted CANDIDATE.

Pre-scan stdout verbatim kullanıcıya gösterilir + `docs/reviews/codex/<DATE>-simplify-<SCOPE_SLUG>-<ATTEMPT>.md` altına `## Pre-scan Turn — <timestamp>` başlığıyla append edilir.

## Adım 6: Sentez + Risk Yükseltme + Onay

Claude'un Adım 3 adayları + Codex'in Adım 5 çıktısı birleştirilir. Sentez kuralları:

### Kural A: Eşleşme + onay

Claude'da var, Codex'te `DO_NOT_APPLY` yok → kategori birleşir (Codex'in farklı kategorize ettiği aday Codex etiketi kazanır), risk sınıfı en yüksek olan kalır.

### Kural B: Codex `DO_NOT_APPLY: <id>`

`<id>` Adım 3 canonical format (`<KATEGORI>-N`, örn. `DRY-1`) ile birebir eşleşmelidir. Eşleşen Claude adayı **otomatik high-risk-blocked** statüsüne yükselir:
- Codex'in `reason` + `unless` alanları verbatim gösterilir
- Per-item explicit onay olmadan UYGULANMAZ (toplu high-risk onayı bu adayı kapsamaz; ayrı per-item gerekir)
- Kullanıcı `unless` koşulunu sağladığını doğrularsa veya açıkça "yine de yap" derse uygulanır; aksi halde aday `dropped: codex-veto` olarak rapor edilir

### Kural C: Codex `DO_NOT_APPLY: unlisted:<short-title>`

Claude listesinde olmayan ama Codex'in itiraz ettiği item. Bu rapor sırasında **ayrı bir risk satırı** olarak gösterilir:
- Claude bu item'ı kendi taramasında atlamış olabilir, veya
- Codex yanlış pozitif veriyor olabilir

Kullanıcıya açıkça sun: "Codex şuna itiraz ediyor ama Claude bu adayı tespit etmemiş — `<unless>` koşulu varsa belki gerçek değil; karar senin." Aday uygulamaya **girmez**; bilgi olarak rapor satırı.

### Kural D: Codex `CANDIDATE: unlisted:<...>`

Codex'in bağımsız önerisi. Claude bunu kendi 5 kategorisinden birine **best-fit** olarak eşler (veya `Other` bucket'a koyar). Risk sınıfı Codex'in verdiği. Normal sınıf-bazlı onay döngüsüne girer.

### Risk Sınıfı → Onay Döngüsü

| Sınıf | Davranış |
|---|---|
| **low** | Direkt uygulanabilir (Kural B/C ile high'a yükseltilmemişse). Toplu onay `AskUserQuestion` ile (örn. "8 low-risk fix uygulayayım mı?"). |
| **medium** | Plan göster, tek onay: "Şu medium-risk fix'leri uygulayacağım: <liste>. Onay?" |
| **high** | Tek tek onay (per-item). Codex `DO_NOT_APPLY` ile gelen high-risk-blocked'lar **ekstra explicit** — Codex gerekçesi yanında. |

### Kural F: Malformed veya Unknown `<id>` — Default Block

Codex `DO_NOT_APPLY: <id>` üretir ama `<id>` Adım 3 canonical format'a uymuyorsa (boşluk, lower-case, eksik N, vs.) **veya** Adım 3 listesinde olmayan bir id'ye işaret ediyorsa (ve `unlisted:` prefix'i yok):

- Veto **ignore EDİLMEZ** — silent veto kaybı yasak (H1 bulgusu).
- Kullanıcıya açık uyarı: "Codex `DO_NOT_APPLY: <ham-string>` verdi, ama bu Adım 3 listesinde eşleşmedi (`<format-sebebi>`). Codex'in `reason`'ı: `<...>`. Kararını ver: hangi adaya bağlamak istersin, yoksa bilgi olarak göster + uygulamaya alma?"
- `AskUserQuestion` 3 seçenek:
  - **Manuel eşle** → kullanıcı `<id>` seçer (Adım 3 listesinden), Kural B aktif olur
  - **Bilgi göster, uygulama** → Kural C gibi davran (bağımsız risk satırı, aday uygulanmaz)
  - **Yoksay** → audit log'a `malformed-veto-ignored: <ham-string>; reason: <gerekçe>` satırı, akış devam (ignore yine yapılır AMA explicit kullanıcı kararıyla)
- Default seçim YOK — kullanıcı seçmeli.

Bu kural Codex'in token üretimindeki nondeterminism'i (model temperature, prompt drift) sessiz veto kaybına çevirmez.

### Test-suite-yok Override (Kural E)

`<TEST_SUITE_PRESENT> = false` ise:

- **Low ve medium adaylar:** Normal akış (test güvenlik ağı yok ama risk düşük)
- **High adaylar:** **Default block.** Kullanıcı **named override** ile geçer:
  > "Test yok. Şu adı belirtilen yüksek-risk fix'i otomatik doğrulama olmadan onaylıyorum: `<aday-id>`."
- **Toplu "continue anyway" yasak.** Her high-risk aday için ayrı named override.
- Override edilen aday'lar rapor `high-risk-no-tests override: <id-listesi>` satırında listelenir.

### Test Rewrite Scope (Kural F)

Adım 7 fix uygulamasında testlere dokunma kuralı:

- **Mekanik update (default OK):** Prod tarafı rename/extract olunca testlerdeki import path, type, helper isim referansları otomatik propagate edilir. Test mantığı (assertion, fixture davranışı, setup akışı) değişmez.
- **Assertion/fixture/setup değişikliği:** **Otomatik high-risk** + per-item explicit onay. Mekanik update kapsamında gizlice geçemez. Kullanıcıya açıkça: "Bu fix `<test-dosyası>` içinde assertion/fixture'a dokunuyor — high-risk olarak onaylıyor musun?"

### Sentez Onayı

Tüm adaylar sınıflandırılıp Kural A-F işletildikten sonra kullanıcıya konsolide rapor:

```
Sentez sonucu:
- Low fix'ler (toplu): N adet — <kısa liste>
- Medium fix'ler (plan + onay): M adet — <kısa liste>
- High fix'ler (tek tek onay): K adet — <kısa liste>
- Codex DO_NOT_APPLY (blocked-until-explicit): J adet
- Codex unlisted veto (bilgi): L adet
- Test-no override gereken: P adet

Devam edelim mi?
```

## Adım 7: Fix Uygulama

Claude yazar. Codex yazmaz. Uygulama sırası: **low → medium → high**. Per-sınıf akış:

- **Low (toplu):** Her fix uygulanır. Mantıksal batch sonu (örn. tüm ölü import'lar veya tüm rename'ler tamamlandığında) **scoped verification** çalıştırılır: etkilenen dosyalara odaklı lint + format + (varsa) ilgili test alt-kümesi. FAIL → otomatik undo, kullanıcıya raporla.
- **Medium (plan-onay sonrası):** Plan'da listelenen tüm fix'ler uygulanır, sonunda scoped verification.
- **High (tek tek):** Her fix sonrası scoped verification + kullanıcı onayı ("Bu çalıştı, sıradakine geçelim mi?").

**Scoped verification ≠ full test suite.** Sadece etkilenen alanın hızlı kontrolü:
- Lint (varsa proje config'i)
- Format check
- Test alt-kümesi (etkilenen dosyalar için, varsa otomatik mapping)

**FAIL davranışı:** Otomatik ilerleme YOK. Kullanıcıya kararı bırak:
- Fix'i geri al (undo) ve sıradakine geç
- Fix'i geri al ve dur
- Manuel düzelt (kullanıcı veya Claude), tekrar dene

`<TEST_SUITE_PRESENT> = false` durumunda scoped verification "lint + format only" düşer; "PASS" iddiası yapılmaz.

Adım 7 sonu: tüm onaylanan adaylar uygulanmıştır (ya da explicit drop edilmiştir).

## Adım 8: Final Tests

Full/declared test suite **taze** çalışır:
- Plan/proje config'inde belirtilmiş test komutu (örn. `npm test`, `pytest`, `cargo test`)
- Çıktı okunup PASS/FAIL doğrulanır
- "PASS" iddiası **yalnız çıktı okunduktan sonra** yapılır

`<TEST_SUITE_PRESENT> = false` ise bu adım atlanır; rapor `final tests: not-run (no test suite detected)` der.

FAIL → Adım 7 sorun yönetimi modeline geri dön (fix geri al / manuel düzelt / dur). Final review'a (Adım 9) FAIL ile geçilmez.

## Adım 9: Codex Final Adversarial Review (Zorunlu — koşullu skip)

Komutun **review-gated invariantının asıl kapısı**.

### Pre-flight: FIXES_APPLIED Gate (F1 düzeltmesi — H2 operasyonel kapı)

Adım 9 entry'sinde **ilk** kontrol — scope hesabından ÖNCE:

```bash
if [ "${FIXES_APPLIED:-0}" -eq 0 ]; then
  # Bu simplify çağrısı hiçbir aday uygulamadı.
  # Codex final review YAPILMAZ (review edecek bu run'ın değişikliği yok).
  # Doğrudan Adım 11 No-fixes-applied edge case raporlamasına atla.
  # Variant seçimi: <INITIAL_TREE_DIRTY>'e göre Adım 11 Variant A veya B.
  goto step_11_no_fixes_variant
fi
```

`<FIXES_APPLIED>` Adım 7 sonu Claude tarafından tutulur (her uygulanan aday sayılır; toplu low-batch'te low_applied_count++, medium plan'da medium_applied_count++, high'da high_applied_count++; toplam = `<FIXES_APPLIED>`).

**Bu gate kritik:** Mevcut `git status --short` kontrolü dirty initial + no fixes durumunda yanlış pozitif verir (pre-existing dirty'yi simplify'ın değişikliği sanır). Gate'i FIXES_APPLIED'a bağlamak operasyonel kararı simplify'ın kendi state'ine bağlar, git'in işine değil.

### Scope Hazırla (yalnız FIXES_APPLIED > 0 dalı)

```bash
# Buraya yalnız <FIXES_APPLIED> > 0 ile gelinir; mutlaka uncommitted simplify değişikliği var
SCOPE="--scope working-tree"
```

Working-tree default — simplify tüm fix'leri Adım 11 commit'ine kadar uncommitted tutar; final Codex review **her zaman working-tree diff'i** üzerinde çalışır. Pre-existing commit'lere bakmaz (`HEAD~1` veya benzeri base ref **kullanılmaz** — execute-plan'daki `execute_start_ref` mantığı simplify'da YOK, çünkü resume yok).

**Pre-existing dirty + fixes-applied durumu:** Working-tree diff'i hem pre-existing dirty hem simplify'ın eklediği fix'leri içerir; Codex ikisini birlikte görür. Bu Codex'in işi (bağlam zaten karışık); rapor'da pre-existing dirty file count `<INITIAL_DIRTY_FILE_COUNT>` ayrı satır olarak gösterilir (kullanıcı simplify-fix vs pre-existing'i ayırt edebilsin).

### No-fixes-applied Edge Case (iki alt-varyant — H2 düzeltmesi)

Adım 6 sentezi sonrası **hiçbir aday uygulanmamışsa** (kullanıcı onay vermedi, codex-veto, user-drop, test-no-block — toplamda `<FIXES_APPLIED> = 0`): `<INITIAL_TREE_DIRTY>`'e göre iki ayrı rapor varyantı.

#### Varyant A — Initial clean + no fixes applied

Repo initial olarak clean'di, kullanıcı simplify çalıştırdı, hiçbir aday uygulanmadı. Working-tree hâlâ clean → review edilecek bir şey yok.

```
Simplification complete — no fixes applied (initial tree was clean).
- Scope: <SCOPE_FILES>
- Mode: <standard|light>
- Initial tree state: clean
- Candidates considered: <N> (low: <X>, medium: <Y>, high: <Z>)
- Outcome: dropped <N> (codex-veto: <A>, user-drop: <B>, test-no-block: <C>)
- Pre-scan Codex review: ran (standard) | skipped (light)
- Final Codex review: not-run (no working-tree changes to review; review-gated invariant satisfied — no commit needed)
- Commit: NOT performed (nothing to commit)
- Noted external (cross-file DRY/YAGNI): <NOTED_EXTERNAL> | none
- Sonraki adım: /review  (mevcut HEAD üzerinde; bu simplify çağrısı no-op idi)
```

#### Varyant B — Initial dirty + no fixes applied (H2 ana düzeltme noktası)

Repo initial olarak dirty idi (kullanıcı simplify'ı uncommitted değişiklikler üzerinde çağırdı), hiçbir simplify adayı uygulanmadı. **Working-tree hâlâ dirty** — ama bu dirty state simplify'a ait DEĞİL, kullanıcının önceki işidir.

```
Simplification complete — no simplification fixes applied; existing uncommitted changes unchanged.
- Scope: <SCOPE_FILES>
- Mode: <standard|light>
- Initial tree state: dirty (<INITIAL_DIRTY_FILE_COUNT> uncommitted files; pre-existing, NOT produced by this simplify run)
- Candidates considered: <N> (low: <X>, medium: <Y>, high: <Z>)
- Outcome: dropped <N> (codex-veto: <A>, user-drop: <B>, test-no-block: <C>)
- Pre-scan Codex review: ran (standard) | skipped (light)
- Final Codex review: not-run (this simplify run produced no changes; pre-existing dirty state was NOT reviewed by this command)
- Commit: NOT performed (this simplify run has nothing to commit)
- Noted external (cross-file DRY/YAGNI): <NOTED_EXTERNAL> | none
- Sonraki adım: pre-existing dirty değişiklikleri kullanıcı manuel ele alır (/commit veya /review); bu simplify çağrısı no-op idi
```

**Önemli ayrım:** Varyant B'de Codex final review **simplify'ın kendi değişiklikleri** üzerinde çalışmaz çünkü simplify değişiklik üretmedi. Pre-existing dirty diff'i Codex'in görmesi review-gated invariant kapsamı DIŞINDADIR — o değişiklikler simplify-claude-codex tarafından oluşturulmadı, dolayısıyla "simplify commit'i" için gate yok. Kullanıcı pre-existing değişiklikleri ayrı bir review/commit akışıyla ele almalı.

Bu Şablon A'nın özel hali (varyantları) — Codex final review çalışmasa da invariant ihlal değil (review-gated invariant "simplify commit'i varsa simplify review'ı olmalı" der; commit yoksa kapı tetiklenmez). Varyant B raporu pre-existing dirty'yi **gizlemez**, açıkça işaretler — yalan beyan önlenir.

### Codex Final Review Çağrısı (CODEX-CALL-PROTOCOL ile)

`<CALL> = adversarial-review $SCOPE`. Prompt 8 maddelik:

```
Challenge this simplification batch as a whole. Read CURRENT content of changed files
directly; use git diff to see what was actually changed.

Assess:
1. Semantic regression: did any behavior change? (the goal was simplification, not feature change)
2. Real simplification: is each fix actually simpler than what it replaced, or just shorter/rearranged?
3. Over-abstraction (YAGNI): was abstraction added that has only one caller or only hypothetical future use?
4. Public API break: did renames, signature changes, or removed exports break callers outside scope?
5. Test sufficiency: do existing tests still cover the changed paths? Were any tests deleted or mechanically updated in a way that lost coverage?
6. Referential integrity: paths, names, imports, flags — all correct? (the file-system kind of correctness)
7. Complexity pushed elsewhere: did a "simplification" just move complexity to another file/function/abstraction layer? Mask it as cleanup?
8. New helpers: if any new file or helper was created by extract-refactor, does it have 2+ real callers, is its name/API surface justified, or is it premature abstraction?

Cross-file scope check:
- The command was scoped to <SCOPE_FILES>. Did any fix touch files outside this scope?
- Were DRY/YAGNI patterns outside scope noted but not fixed?

Categorize findings: critical | high | medium | low. Focus on the working-tree diff.
```

### Çıktı

Companion stdout verbatim kullanıcıya gösterilir + `docs/reviews/codex/<DATE>-simplify-<SCOPE_SLUG>-<ATTEMPT>.md` altına `## Final Review Turn — <timestamp>` başlığıyla append.

### Degradation

CODEX-CALL-PROTOCOL'ün 3 seçeneği (Claude-only / Tekrar dene / Durdur). Claude-only seçilirse → **commit ÜRETİLMEZ**; Adım 10 review-not-run dalını izler; Adım 11 Şablon B1.

## Adım 10: Critical/High Guard

Final Codex review çalıştıysa:

**Critical/high YOK** (medium/low veya bulgu yok):
- Adım 11 commit gate'e geç (Düzelt opsiyonel — kullanıcı medium/low için ek revizyon istiyorsa Adım 7'ye dön)

**Unresolved critical/high VAR:**

Normal "commit" sunulmaz. 3 seçenek (`AskUserQuestion`):

- **Düzelt** → Adım 7'ye dön (mini-batch fix; sonra Adım 8 + Adım 9 tekrar). Sayaç tutulmaz (execute-plan'la tutarlı).
- **Risk kabulüyle override (Recommended değil):**
  1. `docs/reviews/codex/<DATE>-simplify-<SCOPE_SLUG>-<ATTEMPT>.md` log'una (F5 düzeltmesi — bu turn'ün gerçek log dosyası, traceability'yi korur) explicit audit satırı: `YYYY-MM-DD HH:MM — UNRESOLVED OVERRIDE: <gerekçe>; accepted findings: [<critical: ...>; <high: ...>]`
  2. Commit mesajına `override-note: simplify with unresolved <count> critical/<count> high findings — see <DATE>-simplify-<SCOPE_SLUG>-<ATTEMPT>.md` satırı (path birebir Adım 9 final log dosyasıyla aynı)
  3. Adım 11 Şablon A raporu `Unresolved critical/high:` satırında bulguları **açıkça** listeler
  4. `unresolved_high_severity_override: true`
- **Durdur** → commit yok; Şablon B2; tüm uncommitted fix'ler working-tree'de kalır (kullanıcı manuel inceleyebilir).

**Final Codex review çalışmadıysa (degradation):** review yok → **commit ÜRETİLMEZ**. `AskUserQuestion`:
- *Codex'i tekrar dene (Recommended)* → Adım 9
- *Durdur* → Şablon B1

## Adım 11: Commit Gate + Final Rapor

### Commit Gate (Adım 10 onay sonrası)

Şartlar AND:
1. Final tests PASS (veya `<TEST_SUITE_PRESENT> = false` ile "not-run" notu)
2. Final Codex review **çalıştı** ve durumu:
   - `approved` (critical/high yok), VEYA
   - `override` (`unresolved_high_severity_override: true` + audit log + commit mesajı notu)

İki şart sağlanırsa kullanıcıya:
> "Simplification tamam. Commit edelim mi?
> Mesaj: `refactor: simplify <scope-özet> — DRY/YAGNI cleanup`
> <override notu varsa: `+ override-note: ...`>"

- **Onay** → commit (Conventional Commits `refactor:` prefix; **push YOK**)
- **Ret** → fix'ler working-tree'de kalır; commit yok; kullanıcı manuel müdahale edebilir

### Final Rapor — 3 Şablon

#### Şablon A — Completed

```
Simplification complete — commit done | pending.
- Scope: <SCOPE_FILES>; <X> dosya, <Y> satır
- Mode: <standard|light>
- Test suite: present | absent
- Initial tree state: clean | dirty (<INITIAL_DIRTY_FILE_COUNT> pre-existing uncommitted files)
- Adaylar: low <N> applied, medium <M> applied, high <K> applied, dropped <D> (codex-veto: <D1>, user-drop: <D2>)
- Test-no override (named): <id-listesi> | none
- Fixed inside scope: <kategori bazlı özet liste>
- Noted external (not fixed): <NOTED_EXTERNAL>  (cross-file DRY/YAGNI; bilgi)
- Intentionally deferred: <deferred-listesi>  (yeni dosyalar dahil — "new file <X> can be simplified in a later pass")
- Verification (test-suite-aware — M2 düzeltmesi):
  - test_suite_present=true → "Scoped verification (per-batch): tests <PASS|FAIL özet>, lint/format OK" + "Final tests: PASS"
  - test_suite_present=false → "Scoped checks (per-batch): lint/format OK; tests not-run (no suite detected)" + "Final tests: not-run (no test suite)" (PASS kelimesi YASAK)
- Pre-scan Codex review: ran (standard) | skipped (light)
- Final Codex review: approved | override
- Unresolved high-severity override: false | true
- Unresolved critical/high: none | <başlık1; başlık2; ...>
- Codex review log: docs/reviews/codex/<DATE>-simplify-<SCOPE_SLUG>-<ATTEMPT>.md
- Sonraki adım: /review
```

#### Şablon B1 — Final review not-run

```
Simplification draft — final Codex review did not run (<sebep: degradation|companion-missing|timeout|user-stop-pre-scan|user-stop-synthesis|user-stop-after-test-fail>).
- Scope: <SCOPE_FILES>
- Mode: <standard|light>
- Test suite: present | absent
- Final tests: <ran-PASS | not-run-no-suite | not-run-skipped-due-to-stop>
  - "PASS" kelimesi YALNIZ Adım 8 fiilen çalışıp çıktısı okunduysa kullanılır
  - **`ran-FAIL` durumu B1'e ulaşmaz** — Adım 8 FAIL Adım 7 sorun yönetimine döner; orada (a) düzelt + tekrar dene, (b) durdur (TASK Open Problems'a değil, bu komutta yalnız working-tree'de kalır + B1 sebebi `user-stop-after-test-fail`) seçenekleri vardır. B1'e geliş yolu yalnız "final review'a hiç gelinmeyen stop'lar" (degradation, pre-scan stop, sentez stop, test-fail-stop).
- Adaylar: <durum özeti — kaç tanesi uygulanmadan kaldı, working-tree'de ne var>
- Final Codex review: not-run (<sebep>)
- Commit: NOT performed (review-gated invariant)
- Working-tree state: <X uncommitted dosya — bu çağrıda uygulanan fix'ler + pre-existing dirty (varsa) AYRIK görünür yapılmalı>
- Previous Codex review log (this attempt): docs/reviews/codex/<DATE>-simplify-<SCOPE_SLUG>-<ATTEMPT>.md
- Sonraki adım: /simplify-claude-codex <SCOPE>  (run-from-scratch; previous review context yeni log dosyasından önce link olarak korunur; "resume" DEĞİL — yeni çağrı sıfırdan başlar, working-tree state'ini "uncommitted scope" olarak normal tarar)
```

#### Şablon B2 — Final review ran, stopped

```
Simplification draft — final Codex review ran, user stopped at guard.
- Scope: <SCOPE_FILES>
- Mode: <standard|light>
- Test suite: present | absent
- Final tests:
  - test_suite_present=true → "PASS" (Adım 8 çıktısı okundu) | "FAIL" (Adım 9'a gelinmez normalde)
  - test_suite_present=false → "not-run (no test suite detected)" — "PASS" kelimesi YASAK (F2 düzeltmesi — M2 sweep B2'ye de uygulanır)
- Pre-scan Codex review: ran (standard) | skipped (light)
- Final Codex review: ran, stopped
- Unresolved critical/high: <başlık1; başlık2; ...>  (final log'undan; bulgu yoksa "none")
- Commit: NOT performed
- Working-tree state: <X uncommitted dosya — bu çağrıda uygulanan fix'ler + pre-existing dirty (varsa) AYRIK görünür yapılmalı>
- Previous Codex review log (this attempt): docs/reviews/codex/<DATE>-simplify-<SCOPE_SLUG>-<ATTEMPT>.md
- Sonraki adım: /simplify-claude-codex <SCOPE>  (run-from-scratch; previous review context yeni log dosyasından önce link olarak korunur; "resume" DEĞİL — düzelt veya yeniden review için sıfırdan başla)
```

### B1 / B2 Çıkışlarında Sonraki Adım Kuralları

- **B1 / B2'de ÖNERME:** `/review`, `/security-review`, `/finish-branch`, `/execute-plan-claude-codex`.
- **B1 / B2'de YALNIZ ÖNER:** `/simplify-claude-codex <SCOPE>` (run-from-scratch; resume DEĞİL — bkz. Implementation Notes "Resume davranışı"). Yeni çağrı önceki log dosyasını **link olarak** korur (yeni log dosyasının başına `Previous attempt: docs/reviews/codex/...` satırı eklenir); audit trail kaybolmaz ama yarım state yok.
- **Şablon A'da ÖNER:** `/review` (sonra zincir `/security-review` → closure).

Review-gated invariant rapor seviyesinde de korunur.

### `Unresolved critical/high:` Satırı Zorunlu

- Şablon A + bulgu yok → `none`
- Şablon A + `unresolved_high_severity_override: true` → liste zorunlu (override edilenler açıkça)
- Şablon B1 → `not-evaluated (Codex review skipped: <sebep>)`
- Şablon B2 → final review log'undan listele

## Mevcut simplify.md'den Korunan

- 5 kategori tarama modeli (DRY/YAGNI/Naming/FileSize/DeadOrDebugCode)
- 3 risk sınıflaması (low/medium/high) ve uygulama akışı
- Test komutu + test dosyası varlığı preflight kuralları
- Test yoksa kesin "PASS" iddiası yasak
- Push yapmama
- Sonraki adım /review önerisi

## Değişecek Dosyalar (atomik tek tur)

1. `~/.claude/commands/simplify-claude-codex.md` — **yeni** (~500 satır tahmin)
2. `~/.claude/commands/simplify.md` — **stub:**
   ```
   ---
   description: [DEPRECATED] use /simplify-claude-codex
   ---
   Bu komut /simplify-claude-codex ile değiştirildi (Codex pre-scan + final review + commit gate).
   ```
3. `~/.claude/commands/spec-claude-codex.md` — Sözleşme Notları drift-check 4-way güncelleme
4. `~/.claude/commands/write-plan-claude-codex.md` — aynı güncelleme
5. `~/.claude/commands/execute-plan-claude-codex.md` — aynı güncelleme + Adım 16 Şablon A "Sonraki adım: /simplify" → "/simplify-claude-codex" + tüm diğer "/simplify" referansları "/simplify-claude-codex"

## Drift Sözleşmesi (4-way)

`CODEX-CALL-PROTOCOL` bloğu canonical = `spec-claude-codex`; aşağıdaki 4 komutta **birebir aynı**:
- `spec-claude-codex.md` (canonical)
- `write-plan-claude-codex.md` (ayna)
- `execute-plan-claude-codex.md` (ayna)
- `simplify-claude-codex.md` (yeni ayna)

**Check A (4-way):** `awk` ile her dosyadan BEGIN/END marker'ları arasındaki blok çıkarılır; üç diff'in **hepsi 0** olmalı:
- `spec vs write-plan diff=0`
- `spec vs execute diff=0`
- `spec vs simplify diff=0`

**Check B (tripwire):** çıkarılan bloklarda şu token'lar **dört dosyada** mevcut olmalı:
`codex-companion.mjs`, `git rev-parse`, `AGENTS.md`, `timeout 480s`, `124`, 3 degradation seçeneği (`Claude-only devam et`, `Tekrar dene`, `Komutu durdur`).

**"biri değişirse diğeri de"** referansı 4 komutu sayar.

## Decisions Log (Resolved Sorular — Brainstorm Çıktısı)

| # | Soru | Karar | Gerekçe |
|---|---|---|---|
| 1 | Mode default ne olmalı? | **Standard (Recommended)** | Aile tutarlılığı + review-gated invariant pre-scan adversarial değerini default kazanır; Light opt-in |
| 2 | Idempotency contract var mı? | **Fırsatçı (no contract)** | "Mutlaklık iddiası yasak" + Codex nondeterminism gerçeği; Şablon A "Fixed/Noted/Deferred" üçlüsü dürüst rapor verir |
| 3 | Test rewrite scope? | **Mekanik update default; assertion/fixture/setup high-risk + per-item explicit onay** | Test güvenlik ağı korunmalı; mekanik = derleme/import seviyesi zorunlu yansıma; mantık değişikliği gizlice giremez |
| 4 | Yeni dosya aynı run scope? | **Girmez; final review 3 sıkı madde + deferred raporu** | Fırsatçı kontrat (Soru 2) ile tutarlı; rescan loop karmaşası yok; final review yeni helper kalitesini denetler |
| 5 | "Yapma" sinyali formatı? | **Yapılandırılmış: `DO_NOT_APPLY: <id>` + `reason:` + `unless:` + `unlisted:` fallback** | Parse hatası sıfır; nüanslı veto (`unless:`) korunur; sessiz veto kaybı önlenir |
| 6 | Codex pre-scan prompt scope'u? | **Hibrit: 5 kategori + Other + `CANDIDATE: unlisted:` bağımsız aday + `DO_NOT_APPLY` veto** | Ortak terminoloji sentez kolaylığı + Codex'in adversarial bağımsızlık değeri korunur |
| 7 | Verification timing (Adım 7)? | **Scoped per batch (lint/format/test-subset); Adım 8 full suite finalde taze** | "Her fix sonrası full suite" overkill; kullanıcı düzeltmesi |
| 8 | Mimari yön? | **Y1/A — execute-plan-style mirror + selective reuse from old simplify** | İki perspektif aynı yöne işaret etti; Codex "treat as small execution workflow" |
| 9 | Codex 1. tur bulguları adresleme | **H1 token canonical + Kural F malformed-block; H2 initial-dirty-tree flag + iki varyant rapor; H3 "resume" dili kaldırıldı + previous-log link; M1 Y2/B tradeoff tablosu kalitatif gerekçeyle; M2 verification etiketi test-suite-aware** | Hepsi targeted fix (mimari/lifecycle değişmiyor); Codex review log'unda turn 1 detay |
| 10 | Codex 2. tur bulguları adresleme | **F1 Adım 9 FIXES_APPLIED early-exit gate (H2 operasyonel kapı); F2 B2 + B1 test-suite-aware Final tests etiketi (M2 sweep tamamlandı); F3 log filename ATTEMPT counter + previous-attempt link mekanizması; F4 sayaç netliği (codex_targeted_fixes = bireysel fix sayısı, codex_review_iterations = Codex turn sayısı)** | Hepsi targeted; Codex 2. tur log'unda detay |
| 11 | Codex 3. tur bulguları adresleme | **F5 override audit path -<ATTEMPT>.md kullanır + commit override-note path birebir; F6 Adım 4.5 log dosyası explicit setup adımı (mkdir + ATTEMPT + previous-attempt link ilk satır); F7 B1 ran-FAIL state kaldırıldı + user-stop-after-test-fail sebebi eklendi** | Turn 3: critical/high YOK (ilk temiz tur); 3 medium/low mekanik düzeltme |

## Open Problems

(Codex turn 4 review sonrası eklenir — turn 3 sonrası critical/high YOK; medium/low'lar adreslendi.)

## Out-of-Scope

- `/review`, `/security-review`, `/finish-branch` komutlarının kendi davranışları (zincirde sonraki adımlar)
- Vault promotion (closure P1)
- Active task layer integration (komut active layer'a YAZMAZ; CURRENT.md/TASK.md/HANDOFF.md hiç dokunulmaz)
- Çoklu dil (multi-language) özel scanner kuralları — proje neyse o
- Eski simplify.md'nin 5 kategori scope kararlarının yeniden tartışılması (korundu)
- Push otomasyonu (push hiç sorulmaz, kullanıcı manuel)
- Iteration-limit kavramı (execute-plan'da olmadığı gibi simplify'da da yok — Düzelt döngüsü tetiklenirse sayaç tutulmaz)

## Implementation Notes

### Boyut tahmini

~500 satır (execute-plan'ın 935'i ile spec'in 707'si arası). Brainstorm'da "boyut kullanım kaçışına yol açar mı" endişesi tartışıldı; Y2/B alternatifinin de pratikte 350-400 satır olacağı gerekçesiyle Y1/A seçildi.

### CODEX-CALL-PROTOCOL bloğu

`spec-claude-codex.md`'den **birebir kopyala**. `<STEP_A>` = Adım 5 pre-scan (`<CALL> = task --fresh`), `<STEP_B>` = Adım 9 final review (`<CALL> = adversarial-review $SCOPE`).

### Log dosyası adı (F3 düzeltmesi — chain integrity)

`docs/reviews/codex/<DATE>-simplify-<SCOPE_SLUG>-<ATTEMPT>.md`

- `<DATE>` = YYYY-MM-DD (bugün)
- `<SCOPE_SLUG>` scope tanımından türetilir:
  - Argüman dosya/dizinse: dosya/dizin slug'ı
  - `git diff` ise: `working-tree`
  - `origin/main..HEAD` ise: branch adı
  - Son 5 commit ise: `recent-5-commits`
- `<ATTEMPT>` = aynı `<DATE>-simplify-<SCOPE_SLUG>` prefix'iyle bugün mevcut dosya sayısı + 1 (monotonic counter):
  ```bash
  ATTEMPT=$(ls docs/reviews/codex/${DATE}-simplify-${SCOPE_SLUG}-*.md 2>/dev/null | wc -l)
  ATTEMPT=$((ATTEMPT + 1))
  ```
- B1/B2 sonrası kullanıcı `/simplify-claude-codex <SAME_SCOPE>` çalıştırırsa: yeni log dosyası ATTEMPT+1 olur; yeni dosyanın **ilk satırı** önceki ATTEMPT'in path'ine link:
  ```markdown
  Previous attempt: docs/reviews/codex/<DATE>-simplify-<SCOPE_SLUG>-<PREV_ATTEMPT>.md

  ---
  ```
- Çoklu run zinciri (örn. 3 ardışık B1 sonrası 4. çağrı):
  - Attempt 4 log dosyası ilk satırı `Previous attempt: ...-3.md`'ye link
  - Attempt 3 zaten attempt 2'ye link
  - Zincir geriye doğru izlenebilir — audit trail tam korunur

Bu mekanizma B1/B2 "Previous Codex review log" linklerinin gerçek path'e çözülmesini garanti eder; deterministik path drift YOK.

### Resume davranışı

Simplify'da resume kavramı YOKTUR. Kullanıcı B1/B2 çıkışı sonrası tekrar `/simplify-claude-codex <SCOPE>` çağırırsa **sıfırdan başlar** — komut working-tree state'ini tarar, yarım kalan fix'ler "uncommitted değişiklik" olarak normal scope tespitine girer. Execute-plan'daki gibi `execute_start_ref` tutulmaz, mode/cadence state'i yazılmaz.

---

**Sonraki adım:** `/write-plan-claude-codex docs/specs/2026-05-31-simplify-claude-codex-command.md`
