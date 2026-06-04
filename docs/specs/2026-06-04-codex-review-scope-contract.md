---
title: Codex Review Scope Contract + Structured Recommendation + execute-plan 8.6 Auto-Continue
status: spec-approved
date: 2026-06-04
tags: [claude-codex, drift-contract, review-scope, auto-fix, execute-plan]
codex_review_status: approved
codex_review_iterations: 2
codex_targeted_fixes: 2
unresolved_high_severity_override: false
codex_review_log: docs/reviews/codex/2026-06-04-codex-review-scope-contract.md
---

# Codex Review Scope Contract + Structured Recommendation + execute-plan 8.6 Auto-Continue

## 1. Bağlam ve problem

claude-codex komut ailesi, Codex review çağrılarını yedi komutta kullanır. Her komut
review'ı farklı topolojide tetikler (design/spec, plan, checkpoint/final execution,
simplification, çift-hakem code review, mode-aware security, closure audit). İki yapısal
boşluk var:

**A — Review scope sözleşmesi yok.** Codex'e "diff'i review et" demek yetmez. Şu an:
- Review hedefi deterministik pinli değil ("şu an HEAD neyse" review drift'i doğurur).
- Requirement kaynakları (spec/plan/TASK/HANDOFF/AGENTS) explicit verilmiyor.
- Changed-files dışı bağlı dosyalar (callers/callees/tests/config/schema/sibling command)
  keşfettirilmiyor.
- Codex'in **neyi incelediği/incelemediği** (coverage statement) raporlanmıyor → "Codex
  bağlama hakim oldu" iddiası fazla güçlü.
- Yapılandırılmış çözüm önerisi (root cause / minimal fix / verification / fallback) yalnız
  Auto-Fix döngüsünün **Tur 4+** turunda zorunlu — ilk 3 turda Codex'in root-cause/minimal-fix
  perspektifi geç geliyor.

**B — execute-plan checkpoint gereksiz kullanıcı kapısı.** `execute-plan-claude-codex`
Adım 8.6 her checkpoint sonunda — **temiz geçse bile** — kullanıcıya "Devam edelim mi?"
soruyor. Checkpoint temizliği zaten review gate'in olumlu sonucudur; bu onay gereksiz.

### Önceki task'ın dersi (tekrar etmemeli)

`auto-fix-review-policy` (kapandı 2026-06-04) `binding prose` ekledi ama **prosedür
branch'leri aynı davranışa bağlanmamıştı** → `/review-claude-codex` sistemik
"prose-declared-not-wired" gap'i yakaladı, 5 turda düzeltildi. Bu task'ın **ana invariantı**:
sözleşme yalnız prose olarak eklenmez; review prompt gövdeleri + ilgili prosedür branch'leri
**birlikte** rewire edilir. İki bağlı workstream tek planda yapılır (ayrı plan riski =
ortak contract değişip checkpoint prosedürünün eski "kullanıcıya sor" branch'lerini taşıması).

### Mevcut durum (grounding — execution delta'sı dar)

- `AUTO-FIX-REVIEW-POLICY` bloğu zaten **4-way byte-identical** (spec/write-plan/execute-plan/simplify),
  C/H/M `claude-confirmed` için otonom fix döngüsü + 6-tavan/global-cap=10/2.-reopen backstop'ları
  ile canlı (Check D).
- execute-plan **Adım 8.5** C/H/M otonom fix döngüsü **zaten wire'lı** (predecessor task); oradaki
  "Düzelt / override / durdur" menüsü çoktan kaldırılmış.
- Canlı kod delta'sı bu yüzden dar: (a) **8.6** hâlâ temiz checkpoint'te "Devam edelim mi?"
  soruyor, (b) structured recommendation yalnız **Tur 4+**, (c) **Review Scope Contract +
  coverage statement** hiçbir komutta YOK.

## 2. Kapsam (scope)

**Dahil:**
1. Yeni canonical blok **`CODEX-REVIEW-SCOPE-CONTRACT`** — 7 review-emitting komutta byte-identical;
   yeni drift **Check E**.
2. `AUTO-FIX-REVIEW-POLICY` 4-way davranış değişikliği: "Tur 4+ structured recommendation" →
   **her review turunda** structured recommendation; ailedeki tüm stale "Tur 4+" / "max review 3"
   ifadelerinin sweep'i.
3. `execute-plan-claude-codex` **Adım 8.6** clean-checkpoint auto-continue + `last_checkpoint_ref`
   dar mechanical exemption.

**Kapsam dışı (out-of-scope):**
- Yeni severity vokabüleri (mevcut critical/high/medium/low korunur).
- Codex'in dosya yazması (read-only invariant değişmez; Codex yalnız metin önerir).
- Otonomi carve-out'unun genişletilmesi (push/merge/discard/vault/active-layer/status/override
  insan-kapısı kalır; tek dar istisna §5.2 `last_checkpoint_ref`).
- 8.5 C/H/M otonom döngü mekaniği (zaten canlı; bu task yalnız "her tur structured rec"
  ifadesini onunla tutarlılaştırır + 8.6'yı ekler).
- `plan-claude-codex.md` (deprecated alias — aileye dahil değil).

## 3. Mimari kararlar

### 3.1 Sözleşme bloğu vs. binding ayrımı

Yeni blok **yalnız değişmez requirement'ları** taşır (byte-identical, 7-way, drift-locked).
Per-command **binding prose** (blok dışında) **değişkenleri** doldurur: primary artifact ne,
hangi requirement dosyaları, pinli ref nasıl hesaplanır, external dosyalar o komutun substrat'ına
nasıl girer, ve "finding/recommendation" vokabüleri o komutta neye eşlenir. **Binding sözleşmeyi
zayıflatamaz** — yalnız nasıl doldurulacağını söyler.

Bu ayrım ailenin kanıtlı mimarisidir: invariant yalnız byte-locked olunca hayatta kalır
(`CODEX-CALL-PROTOCOL` 7-way, `CODEX-SCAN-SUBSTRATE` 4-way, `AUTO-FIX-REVIEW-POLICY` 4-way).

**Neden ayrı blok (A1) — CALL-PROTOCOL'ü genişletmek (A2-extend) yerine (karar gerekçesi):**

| Seçenek | Lehte | Aleyhte | Karar |
|---|---|---|---|
| **A1: ayrı `CODEX-REVIEW-SCOPE-CONTRACT` (7-way)** | review-içeriği obligasyonları (coverage/structured-rec/scope) call-mekaniğinden ayrı tutulur; reviewer'lar dahil tek uniform sözleşme | 4. byte-identical blok → drift surface + bakım vergisi; iki 7-way blok bağımsız PASS verip blok call-site'tan uzakta kalabilir | **Seçildi** (co-location guard ile, §6) |
| A2-extend: kuralları `CODEX-CALL-PROTOCOL`'e göm | yeni blok yok | CALL-PROTOCOL **review-olmayan** `task --fresh` (ön-scoping) tarafından da kullanılıyor → review-içeriği kuralları oraya ait değil; `CODEX-SCAN-SUBSTRATE` de bilinçli olarak CALL-PROTOCOL içine konmadı (cwd-secret-hardening spec gerekçesi) — aynı ayrım | Red |
| A2-fold / A3-prose | en az churn | report-only reviewer'lar AUTO-FIX taşımıyor → enforcement bölünür; binding≠procedure tekrarı | Red |

Kullanıcı A1'i explicit seçti; bu tablo gerekçeyi kalıcılaştırır (Codex T1 F5). A1'in zayıf noktası
(blok ≠ call-site governance) §6 **co-location guard** ile kapatılır: Check E her komutun review-call
section'ında bloğun **fiilen Codex çağrısından önce** bulunduğunu doğrular.

### 3.2 `CODEX-REVIEW-SCOPE-CONTRACT` blok içeriği (değişmez requirement'lar)

Blok şu zorunlulukları, **komut-agnostik (generic) vokabülerle** taşır:

1. **Pinned target** — review aralığı Codex çağrısından **ÖNCE** somut SHA'lara çözülür
   (`base..HEAD` semi-dynamic bırakılmaz; HEAD fix'ler sırasında ilerlese de review pinli kalır).
2. **Requirement sources (per-command binding — blok yalnız zorunluluğu taşır):** Blok şunu
   mandate eder: *"Her review, requirement source set'ini **explicit declare eder** ve **CURRENT**
   içeriğini requirement olarak okur (implementation değil); set boşsa veya bir kaynak uygulanamazsa
   coverage statement'ta açıkça `not present` / `not applicable (intentional)` raporlar."* **Hangi
   kaynaklar** o komutun binding'inde tanımlanır (§3.3 tablosu) — blok **set'i hardcode etmez**.
   Bu, archetip farkını korur: review spec/plan'ı requirement snapshot alır; **security-review
   spec-alignment denetlemez → spec/plan/TASK/HANDOFF'u bilinçli `not applicable (intentional)`
   işaretler, bağımsızlığı bozulmaz** (Codex T1 F2).
3. **Dependency scope** — her değişen public function / API route / command branch / schema /
   migration / config contract için direct callers/callees + adjacent tests + sibling command
   files **finding/recommendation finalize edilmeden önce** incelenir.
4. **Command-policy external-files inclusion** — bkz. §3.4 (conditional).
5. **Coverage statement** (zorunlu) — files inspected / requirement files inspected / related
   files inspected / files not inspected and why.
6. **Structured fix recommendation — her finding için (severity fark etmez):** root cause /
   minimal fix strategy / exact affected files+functions / related files w/ same pattern /
   verification command / risk if recommendation wrong / fallback if minimal fix doesn't close.
   *Codex read-only kalır — yalnız metin önerir, dosya yazmaz.*

**Tek-kaynak format:** structured-rec 7-alan formatı **yalnız bu blokta** tanımlanır;
`AUTO-FIX-REVIEW-POLICY` onu **referans eder** (kendi içinde tekrar tanımlamaz) → iki blok
arası format drift'i imkansız.

### 3.3 İki enforcement katmanı (membership bilinçli non-uniform)

| Blok | Membership | Kapsam |
|---|---|---|
| `CODEX-REVIEW-SCOPE-CONTRACT` (yeni) | **7-way**: spec, write-plan, execute-plan, simplify, review, security-review, finish-branch | Her Codex review/audit çağrısı: pinned scope + coverage + structured-rec-per-finding |
| `AUTO-FIX-REVIEW-POLICY` (mevcut) | **4-way**: spec, write-plan, execute-plan, simplify | Yalnız fix-komutları: claude-confirmed C/H/M otonom fix döngüsü |
| `CODEX-SCAN-SUBSTRATE` (mevcut) | **4-way**: fix-komutları | Sanitized fetch-clone (`$SCAN_ROOT`) |
| `CODEX-CALL-PROTOCOL` (mevcut) | **7-way** | Preflight/timeout/degradation |

**"Structured recommendation per finding" — komuta göre binding:**
- **Fix-komutları (4):** recommendation otonom fix döngüsüne **beslenir** (Claude tahkim eder,
  uygular, verify eder, re-review).
- **Reviewer'lar (review/security):** recommendation **raporlanır** (Codex döner, Claude sentezde
  gösterir) — auto-fix YOK (report-only).
- **finish-branch (advisory closure audit):** "finding" vokabüleri **closure-blocker / warning /
  note**'a bind edilir; recommendation **advisory** raporlanır, **auto-fix'e dönüşmez**
  (finish-branch klasik review değil — gate değil, advisory audit). bkz. §3.6.

**Per-command requirement-source binding (§3.2 item 2'nin doldurulması — set blokta değil burada):**

| Komut | Requirement sources | Bilinçli N/A |
|---|---|---|
| spec | mevcut mimari/vault/kod referansları | — (spec implementation detayı uydurmaz) |
| write-plan | linked spec | — |
| execute-plan | PLAN_PATH + linked spec + TASK/HANDOFF | — |
| simplify | davranış baseline (public API/caller/test) | spec-alignment N/A |
| review | spec/plan requirement snapshot (identical iki hakeme) | — |
| **security-review** | güvenlik kategori checklist'i + proje güvenlik konteksti | **spec/plan/TASK/HANDOFF = not applicable (intentional)** — bağımsızlık korunur |
| finish-branch | review/security raporları + active-layer state + branch/closure state | — |

**Co-location invariant (Codex T1 F5 teknik kısmı):** Blok byte-identical olması yetmez —
her komutta `CODEX-REVIEW-SCOPE-CONTRACT` review-call section'ında, **Codex çağrısından önce**
bulunmalı (Check E co-location assertion, §6). Aksi halde iki 7-way blok bağımsız PASS verip
sözleşme fiilî call-site'ı yönetmeyebilir.

### 3.4 Judgment call #1 — external command files into substrate (conditional)

Sanitized scan dizinleri git repo'dan kurulur; komut dosyaları repo-DIŞı
(`~/.claude/commands/*-claude-codex.md`, untracked). İki ayrı izolasyon mekanizması var:
- **Fix-komutları:** `CODEX-SCAN-SUBSTRATE` → fetch-clone `$SCAN_ROOT`.
- **Reviewer'lar:** pinli `git worktree add --detach $HEAD_SHA` → `$REVIEW_WT` (security: mode-aware,
  worktree veya git'siz export).

**Çözüm — tek yeniden-kullanılabilir external-overlay guard (Codex T1 F3).** Dağınık per-command
prose YERİNE **tek contract**, blokta requirement olarak; mekanizma binding'de ama **aynı guard
sözleşmesi**:

**External-overlay guard sözleşmesi (her substrat için aynı invariant):**
1. **Allowlist (glob YALNIZ aday listesidir, trust boundary DEĞİL):** `~/.claude/commands/*-claude-codex.md`
   non-following glob ile enumere edilir.
2. **Source validation — kopyadan ÖNCE (Codex T2 F3):** her aday için (a) **regular file** olmalı
   (symlink/dizin/özel dosya **reddedilir + raporlanır**), (b) `realpath` **`~/.claude/commands/`
   altında kalmalı** (dışarı çözülen aday reddedilir). Glob path-eşleşmesi tek başına güven sağlamaz —
   `*-claude-codex.md` adlı bir symlink dış hedefe işaret edebilir. Bu, mevcut `_css_copy_safe`'in
   symlink kontrolüyle aynı sınıf, **commands dizinine anchor'lı**.
3. **İçerik secret-scan (validation'dan sonra, kopyadan ÖNCE):** komut `CODEX-SCAN-SUBSTRATE`
   taşıyorsa mevcut `_css_secret_scan` **reuse**; taşımıyorsa (reviewer) binding **aynı
   secret-exclusion contract'ını sağlayan eşdeğer guard** sağlar (helper'ın 7 komutta birebir
   aynı olduğu **varsayılmaz** — refinement 1). Secret görülen dosya **dışlanır + coverage'da raporlanır**.
4. **Kopya symlink-follow ETMEZ** + post-copy sweep (defense-in-depth): kopya regular-file içeriği
   olarak yapılır (symlink takip yok); ardından dest-dışına çözülen artık symlink kalmışsa silinir
   (mevcut SCAN-SUBSTRATE symlink-sweep ile aynı — ikincil katman).
5. **Context-only label:** overlay **her zaman** "context-only overlay — reviewed diff DEĞİL"
   olarak prompt + coverage'da işaretlenir (worktree de export de — yalnız worktree değil).
6. **Post-overlay coverage accounting:** overlay eklendikten sonra coverage statement overlay
   dosyalarını **context-only** olarak sayar, **reviewed-diff dışında** tutar; coverage_gap
   semantiği overlay'den **etkilenmez** (snapshot scope sabit kalır).

**Destinasyon mode-aware:**
- **Fix-komutları** (`$SCAN_ROOT`) ve **reviewer worktree** (`$REVIEW_WT`): overlay
  `<dir>/claude-commands/` alt-dizinine.
- **security-review git'siz export modu (full/path):** export snapshot **committed-HEAD saflığını
  korur** — canlı home-dir dosyaları export snapshot'ına **KONMAZ**. Command-policy gerekiyorsa
  overlay **ayrı, kendi sanitized temp root**'una kopyalanır (export snapshot'tan izole),
  context-only işaretli, secret-scan'li. Böylece "pinned committed snapshot" iddiası canlı state
  ile kirlenmez (Codex T1 F3 fallback benimsendi).
- **Conditional, always-on değil:** yalnız reviewed artifact command-policy ilgilendiriyorsa
  tetiklenir (aksi halde gereksiz kopya + gürültü).

### 3.5 Judgment call #2 — `last_checkpoint_ref` dar mechanical exemption (refinement 2)

8.6 auto-continue, `last_checkpoint_ref`'i HANDOFF.md'ye otomatik yazmayı gerektirir — ama
"active-layer HANDOFF.md mutation" insan-kapısı carve-out'tadır. **Çözüm — carve-out'tan tamamen
çıkarma; dar tanımla:**

> **Mechanical execution-state write only.** Scope = **yalnız** HANDOFF.md `Verification.last_checkpoint_ref`
> = post-checkpoint HEAD SHA. **Değil:** lifecycle/status mutation, Open Problems yazımı, decision
> mutation, başka herhangi bir HANDOFF/TASK alanı. Bu tek alan dışındaki tüm active-layer mutation'ları
> insan-kapısı kalır.

Bu exemption olmadan auto-continue imkansız; bu sınırla active-layer insan kapısı delinmez.
`execute_start_ref` + executor'ın otonom local commit'leriyle aynı "mechanical execution-state"
sınıfı.

**Mutation protokolü (Codex T1 F4 + T2 F4 — committed-vs-uncommitted + dirty-active-layer DUR):**
Clean checkpoint'te ağaç zaten temizdir (her task commit'li, execute-plan 451). Sıra:
0. **Pre-mutation guard (hard DUR — Codex T2 F4):** `git status --porcelain -- docs/active` **temiz**
   olmalı (bizim yazacağımız tek-alan patch dışında ilgisiz dirty active-layer edit YOK).
   **İlgisiz dirty varsa → hard DUR:** mutation YAPMA, commit YAPMA, auto-continue YAPMA → kullanıcıya
   rapor + sor (kullanıcı/oturum state'i mechanical write altında sessizce commit edilemez). Bu,
   "preserve unrelated dirty" ile "clean tree re-verify" çelişkisini kökten kapatır: ilgisiz dirty
   bir **beklenmeyen durum**dur, mechanical exemption'a değil insan-kapısına gider.
1. **Capture:** `POST_CP_HEAD = git rev-parse HEAD` (write'tan ÖNCE — bu batch'in son task commit'i).
2. **Read-modify-write yalnız tek alan:** HANDOFF.md `Verification.last_checkpoint_ref = POST_CP_HEAD`
   patch et (adım 1'de capture edilen tek canonical SHA); başka HİÇBİR HANDOFF/TASK alanına dokunma.
   Verification section yoksa ekle. (Adım 0 garantisi: docs/active temiz → yalnız bu patch stage'lenir,
   ilgisiz state commit'e karışamaz.)
3. **Ref semantiği (tek canonical SHA — Codex T3 F6):** `last_checkpoint_ref` = `POST_CP_HEAD`
   (bu batch'in son task commit'i). **Neden post-commit HEAD DEĞİL:** alan, kendisini commit'leyen
   docs commit'in içine yazılır → alan kendi commit SHA'sına eşit olamaz (circular). Bu yüzden
   canonical değer daima task HEAD'dir; exemption box + adım 1 + adım 2 hepsi `POST_CP_HEAD` der (tek semantik).
4. **Commit (mechanical docs commit):** active layer repo overlay'i (`docs/active/` tracked) →
   bu tek-alan write'ı **mechanical docs commit** olarak commit'le (executor'ın otonom local-commit
   cadence'i; **push hâlâ gate**). Bu, sonraki batch'in temiz ağaçta başlamasını ve dirty HANDOFF'un
   bir sonraki kod task commit'ine karışmamasını garanti eder. **Sonuç:** sonraki checkpoint base'i =
   `last_checkpoint_ref` = `POST_CP_HEAD`; sonraki diff `POST_CP_HEAD..newHEAD` bu **tek-satırlık
   mechanical docs commit'i de içerir** — bu bilinçli kabul: trivial bookkeeping değişikliği (Codex
   `last_checkpoint_ref` bump'ını flag etmez); "saf diff" yerine "dürüst, tek-canonical-SHA" tercih edildi.
5. **Re-verify:** `git status` temiz olduğunu doğrula → sonraki batch (Adım 7) **otomatik başlar**.

Ref **bir sonraki batch başlamadan ÖNCE** yazılır + commit'lenir (Codex Q3).

### 3.6 Judgment call #3 — finish-branch report-only/advisory vocab bind (refinement 3)

finish-branch klasik review değil, **advisory closure audit** (gate değil). Yine de Codex
audit-emitting set'e dahildir → `CODEX-REVIEW-SCOPE-CONTRACT` taşır. Binding:
- Blok generic "finding" → finish-branch'te **closure-blocker / warning / note** vokabülerine eşlenir.
- "Structured fix recommendation" → **advisory fix recommendation** olarak raporlanır;
  **auto-fix'e dönüşmez** (finish-branch `AUTO-FIX-REVIEW-POLICY` taşımıyor zaten).
- Coverage statement + pinned target (branch/closure state snapshot + pinned target refs) + external
  command-files inclusion (command-policy closure'larında) yine zorunlu.

## 4. AUTO-FIX-REVIEW-POLICY değişikliği (4-way) + stale sweep

### 4.1 Davranış değişikliği

`### Tur yapısı ve sert tavan` alt-bölümü yeniden yazılır:
- **Eski:** "Tur 1–3 Claude kendi yaklaşımıyla / Tur 4+ Codex structured recommendation."
- **Yeni:** **Her review turunda** Codex çağrısı bulgu + zorunlu structured fix recommendation
  döner (`CODEX-REVIEW-SCOPE-CONTRACT` garantisi; format orada tanımlı). Claude tahkim eder
  (gerçek root cause mı / doğru dosya·branch·invariant mı / minimal mi yoksa gereksiz refactor mı /
  aynı pattern sibling'larda var mı / carve-out'a giriyor mu / verification gerçekten kanıtlıyor mu),
  kapsam içi + doğruysa uygular (claude-confirmed C/H/M için kullanıcı onayı yok), verification'ı
  taze çalıştırır, Codex re-review ile kapanışı doğrular.
- **Sınırlar değişmez:** cluster-key başına 6-tavan, session global cap=10, 2.-reopen DUR.
  "max review 3 geçersiz" = "3'te otomatik approve etme", sonsuz döngü değil.

### 4.2 Stale sweep (anti-"binding≠procedure")

Aile-geneli sweep — şu stale ifadeler kalmayacak:
- `"Tur 4+"` / `"Tur 1–3"` structured-recommendation-timing ifadeleri (AUTO-FIX bloğu + her
  binding/guard/Mode-A prose).
- `"max review 3"` C/H/M bağlamında (geçerli sınır = 6-tavan/cap/reopen).

Sweep komutu (verification): `grep -rn 'Tur 4+\|Tur 1.3\|max review 3' ~/.claude/commands/*-claude-codex.md`
→ yalnız **bilinçli** (yeni anlam) eşleşmeler kalır; eski timing ifadeleri 0.

## 5. execute-plan Adım 8.6 yeniden yazımı (Workstream B)

### 5.1 Checkpoint decision matrix

| Checkpoint sonucu | Yeni davranış |
|---|---|
| Tests PASS + Codex approve + 0 bulgu + unresolved C/H/M yok + low yok | **Kullanıcıya sormadan** sonraki batch'e devam |
| Yalnız non-claude-confirmed / rejected / advisory bulgu | Audit'e yaz, kullanıcıya sormadan devam |
| Low bulgu, review_turn ≤ 3 | Otomatik düzelt + verify + Codex re-review |
| Low bulgu, review_turn ≥ 4 ve C/H/M yok | Audit'e yaz, göz ardı et, kullanıcıya sormadan devam |
| claude-confirmed critical/high/medium | Otomatik fix + verify + Codex re-review (mevcut 8.5 döngüsü) |
| C/H/M cluster 6-tavan doldu | Otonom döngü DUR → kullanıcıya rapor + karar |
| Session global cap=10 doldu | Otonom döngü DUR → kullanıcıya rapor + karar |
| Aynı cluster-key 2. kez reopen | Otonom döngü DUR → kullanıcıya rapor + karar |

Kullanıcıya **yalnız** gerçek DUR koşullarında sorulur: 6-tavan / global-cap / 2.-reopen /
Codex degradation (Claude-only/retry/stop) / action carve-out kapsamına girerse / **checkpoint'te
ilgisiz dirty `docs/active` edit** (§3.5 Adım 0 hard DUR). Carve-out korunur (vault/active-layer
(§5.2 dar istisna hariç)/status/push/merge/discard/override).

### 5.2 Clean-checkpoint auto-continue prosedürü

Eski 8.6 ("her durumda kullanıcıya rapor + 'Devam edelim mi?' + onay sonrası last_checkpoint_ref")
şu davranışla değişir:
- **Clean checkpoint** (yukarıdaki matrix satır 1) → kısa **bilgilendirme** raporu (onay sorusu YOK)
  → §3.5 mutation protokolü çalışır (Adım 0 pre-mutation guard: ilgisiz dirty `docs/active` varsa
  hard DUR → kullanıcıya sor; aksi halde capture `POST_CP_HEAD` → tek-alan RMW
  `last_checkpoint_ref = POST_CP_HEAD` → mechanical docs commit → `git status` temiz doğrula)
  → sonraki 3-task batch (Adım 7) **otomatik başlar**. (Ref = `POST_CP_HEAD`, task HEAD;
  commit-sonrası HEAD DEĞİL — §3.5 F6.)
- **Low ≤3** → fix/verify/re-review döngüsü; kapanınca clean'e döner (auto-continue).
- **Low ≥4 only** → audit-trail'e yaz + göz ardı + auto-continue (kullanıcıya "düzelteyim mi /
  devam mı?" sorulmaz).
- **C/H/M** → mevcut 8.5 otonom fix döngüsü (zaten wire'lı; bu task değiştirmez, yalnız
  "her tur structured rec" ifadesini onunla tutarlılaştırır).

Low bulgular **hiçbir DUR'u tetiklemez** (6-tavan/cap/reopen/override menüsü).

## 6. Drift / doğrulama

**Doğrulamanın dürüst sınırı (Codex T1 F1 — token presence ≠ wired procedure).** Tek başına
"blok byte-identical + token grep" predecessor'ın "prose-declared-not-wired" hatasını **tekrar
üretir**: blok PASS verirken call-path hâlâ pinned-SHA hesaplamayabilir, overlay kopyalamayabilir,
8.6 eski soruyu sorabilir. Bu yüzden doğrulama **katmanlı**; statik olarak kanıtlanamayan prosedür
semantiği açıkça residual kabul edilir (İlke 3 — mutlaklık iddiası yok).

**Katman 1 — Check E (byte-lock, deterministik):** `CODEX-REVIEW-SCOPE-CONTRACT` bloğu 7 komuttan
awk ile çıkarılır, **byte-for-byte `cmp`** (7-way; normalize/whitespace/anlam toleransı YOK) +
tek md5 + tripwire token'lar (pinned target / coverage statement / structured fix recommendation /
requirement sources / command-policy external-files / context-only overlay). Check A pattern'i ayna.

**Katman 2 — section-anchored procedure assertions (token-presence DEĞİL; Codex T1 F1).** Check E,
her komutun **review-call section'ına** yapısal assertion uygular (generic token grep değil):
- **Co-location:** `CODEX-REVIEW-SCOPE-CONTRACT` referansı review-call section'ında, **Codex çağrısı
  (`run_codex_scan`/companion invocation) satırından ÖNCE** bulunur (F5 teknik kısmı).
- **Pinned-ref-before-call:** o section'da Codex çağrısından önce somut ref/SHA ataması (`--base`/
  resolved-SHA/`$REVIEW_WT @ HEAD_SHA`) var.
- **execute-plan 8.6:** clean + low-only continuation path'inde `AskUserQuestion` **YOK** (assertion:
  8.6 clean dalında user-prompt token bulunmamalı).
- **command-policy overlay:** external-files binding taşıyan komutlarda overlay-setup adımı mevcut.
- **coverage + structured-rec ask:** review prompt gövdesi her ikisini ister.
Bu assertion'lar grep/awk ile **section-anchored** (dosya-geneli token değil) → "blok var ama
prosedür eski" durumu yakalanır.

**Katman 3 — Check A/B/C/D re-verify:** Check D (AUTO-FIX 4-way) every-turn edit sonrası byte-identical
PASS; Check A/B/C dokunulmadı, PASS kalmalı.

**Katman 4 — stale sweep** (§4.2): `grep` "Tur 4+" / "max review 3" → eski timing eşleşme 0.

**Katman 5 — scenario trace (ZORUNLU execution adımı, "prose" değil):** her senaryo komut dosyasının
**ilgili section'ına anchor'lanarak** trace edilir: clean→auto-continue · C/H/M→auto-fix loop ·
low ≤3→fix · low ≥4-only→audit-ignore-continue · 6-tavan/cap/reopen→user DUR · command-policy
review→external files context-only + coverage doğru · security export→overlay export snapshot'a
girmez (ayrı temp root).

**Katman 6 — execution sırasında per-command Codex review:** statik kanıtlanamayan semantik (R1
residual) execution'da her komut için Codex review ile kapsanır.

**Smoke:** 7 komut markdown smoke-parse (load + parse).

## 7. Acceptance criteria

- [ ] `CODEX-REVIEW-SCOPE-CONTRACT` bloğu 7 komutta byte-identical (Check E PASS).
- [ ] Blok şunları taşır: pinned target, requirement sources, dependency scope, command-policy
      external-files inclusion, coverage statement, structured-fix-recommendation-per-finding.
- [ ] Check E **section-anchored procedure assertions** (token-presence DEĞİL): her komutta
      co-location (blok Codex çağrısından önce) + pinned-ref-before-call + (execute-plan)
      8.6-clean-path-no-AskUserQuestion + command-policy overlay-setup + coverage/structured-rec ask.
- [ ] Requirement sources **per-command binding** (set blokta değil §3.3 tablosunda); security-review
      spec/plan/TASK/HANDOFF = `not applicable (intentional)`, bağımsızlık korunur.
- [ ] Related file inspection explicit (callers/callees/tests/config/schema/sibling command files).
- [ ] structured-rec 7-alan formatı yalnız sözleşme bloğunda tanımlı; AUTO-FIX onu referans eder.
- [ ] AUTO-FIX bloğu "her review turunda structured recommendation" (Tur 4+ timing kaldırıldı),
      4-way byte-identical (Check D PASS).
- [ ] Aile-geneli stale "Tur 4+" / "max review 3" (C/H/M) sweep'i = 0 eski eşleşme.
- [ ] C/H/M için geçerli sınır = 6-tavan / global cap=10 / 2.-reopen (max-review-3 referansı yok).
- [ ] external-files **tek guard sözleşmesi** (allowlist aday + **pre-copy source validation:
      regular-file + realpath under ~/.claude/commands/** + kopya-öncesi secret-scan + symlink-follow-yok
      + her zaman context-only label + post-overlay coverage accounting); conditional (command-policy
      mode); secret-scan helper komut-bazlı (reuse/eşdeğer); **security git'siz export modunda overlay
      export snapshot'a GİRMEZ — ayrı sanitized temp root**.
- [ ] `last_checkpoint_ref` exemption dar + **mutation protokolü** (Adım 0 pre-mutation guard:
      ilgisiz dirty docs/active → hard DUR → capture POST_CP_HEAD → ref=**POST_CP_HEAD (tek canonical
      SHA, task HEAD; post-commit HEAD DEĞİL — circular)** → tek-alan RMW → mechanical docs commit →
      git status temiz); lifecycle/status/Open-Problems/decision değil.
- [ ] execute-plan 8.6 clean-checkpoint kullanıcı onayı kaldırıldı; auto-continue + §3.5 protokolü.
- [ ] Low davranışı: ≤3 düzelt, ≥4 audit-ignore + auto-continue.
- [ ] finish-branch contract'ı advisory/report-only vocab'a bind (closure-blocker/warning/note;
      recommendation advisory; auto-fix'e dönüşmez).
- [ ] Check A/B/C/D + yeni Check E hepsi PASS; 7 komut smoke-parse; scenario trace tutarlı.

## 8. Açık problemler / riskler

- **R1 — binding≠procedure tekrarı:** Bloğu deklare edip prompt gövdelerini/branch'leri
  rewire etmemek predecessor'ın sistemik gap'ini tekrar üretir. **Azaltım (§6 katmanlı):** Check E
  **section-anchored procedure assertions** (token-presence değil) + stale sweep + zorunlu
  scenario trace + execution'da per-command Codex review. **Residual açık (İlke 3):** statik
  kanıtlanamayan prosedür semantiği execution Codex review'a bırakılır — sıfır risk iddia edilmez.
- **R2 — iki-mekanizma asimetrisi (çözüldü §3.4):** external-files inclusion fetch-clone
  (`$SCAN_ROOT`) / reviewer worktree (`$REVIEW_WT`) / security git'siz export için **tek guard
  sözleşmesi** + mode-aware destinasyon; export modunda overlay **export snapshot'a girmez** (ayrı
  sanitized temp root). Her binding'in guard'ı plan'da ayrı verify edilir.
- **R3 — Check E false-positive:** Blok **pozitif byte-identical kontrat** (semantic-negative
  değil) → `cmp` yakınsar; bypass↔false-positive ikilemi yok.
- **R4 — drift surface artışı:** 4. shared byte-identical blok her gelecek aile edit'inin
  bakım vergisini artırır (kabul edildi — invariant için byte-lock gerekçesi baskın).
- **R5 — AUTO-FIX/SCOPE-CONTRACT format coupling:** structured-rec formatı tek-kaynak (sözleşme
  bloğu); AUTO-FIX referans eder. Referans ifadesi yanlış yazılırsa iki blok ayrışır →
  Check D + Check E + tripwire birlikte yakalamalı.

## 9. Sonraki adım

`/write-plan-claude-codex docs/specs/2026-06-04-codex-review-scope-contract.md` — bu spec'ten
implementation planı (task'lar: Check E + blok yazımı + 7-way enjeksiyon + AUTO-FIX 4-way edit +
8.6 rewrite + sweep + scenario trace).
