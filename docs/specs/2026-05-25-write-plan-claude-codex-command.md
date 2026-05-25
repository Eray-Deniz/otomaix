---
title: /write-plan-claude-codex komutu — çift-perspektif implementation planı
status: spec-approved
date: 2026-05-25
tags: [workflow, slash-command, codex, claude-codex, planning]
codex_review_status: approved-by-iteration-limit
codex_review_iterations: 3
codex_targeted_fixes: 2
codex_review_log: docs/reviews/codex/2026-05-25-write-plan-claude-codex-command.md
---

# `/write-plan-claude-codex` — Spec

## 1. Problem & Çekirdek Karar

Mevcut `/write-plan` ince bir orkestratör: `superpowers:writing-plans` skill'ini
sarmalıyor, proje-özel path/commit disiplini + active-task hatırlatması ekliyor.
Ama tek-perspektifli (yalnız Claude), **review-gate'siz**, sayaçsız, resume-safe
değil ve en kritik: upstream `/spec-claude-codex`'in `spec-approved` garantisini
**downstream'de doğrulamıyor** — onaysız bir spec'ten sessizce plan yazabiliyor.

**Çekirdek karar:** `/write-plan-claude-codex` adında yeni bir canonical komut yaz;
`/spec-claude-codex` ile **aynı felsefe ve sağlamlık barında** olsun:

> önce bağımsız Codex katkısı → Claude sentezi → kullanıcı karar kapısı →
> en sonda Codex adversarial review → metadata'lı approval.

Fark: girdi **onaylanmış spec**, çıktı **implementation planı** (tasarım/spec değil).
Eski `/write-plan` silinmez, `[DEPRECATED]` stub'a çevrilir (`/plan-claude-codex`
modelindeki gibi — referans bütünlüğü için korunur).

### Üç net tasarım kararı

1. **Referans sweep aynı iş paketinde.** Canlı yüzeylerde `/write-plan →
   /write-plan-claude-codex`. Tarihli kayıt dokümanlarına dokunulmaz. Eski komut stub.
2. **Unapproved-spec override kalıcı yazılır.** Plan frontmatter'ında
   `source_spec_unapproved_override: true|false` + audit izinde (uçucu raporda değil).
3. **Subagent/Inline execute seçeneği korunur.** Komut plan yazınca durur;
   `/execute-plan` otomatik başlamaz.

## 2. Authoring Yaklaşımı (C — hybrid) ve Drift Enforcement

Üç aday değerlendirildi:
- **A. Saf duplike monolith** — runtime self-contained ama ~80 satır protokol drift'i görünmez.
- **B. Ortak protokol dosyası (extract-shared)** — en az drift ama slash command'larda gerçek
  include/import **yok**; "başka dosyayı aç" hatırlamasına bağımlı → "sessizce kırılma"
  sağlamlık barını deler. **Elendi.**
- **C. Hybrid: gömülü protokol + canonical-source marker + makine-kontrollü drift-check**
  — **SEÇİLDİ.**

> **Elenen alternatif (`<DROPPED_ALT>`):** B (extract-shared) + saf-A (drift-guard'sız
> duplike). Adversarial review'da "yön doğru muydu" sorgulaması bunlara karşı yapılır.

### Drift enforcement (Codex Bulgu 1, turn 1-4)

0. **Canonical normalizasyon (in-scope prerequisite — Codex Bulgu 1, turn 4):** Bu
   marker'lar `~/.claude/commands/spec-claude-codex.md`'de **henüz yok** (rg ile doğrulandı:
   protokol içeriği var, marker yok). Yeni komut yaratılmadan **ÖNCE**, canonical'ın protokol
   çekirdeği aynı `CODEX-CALL-PROTOCOL:BEGIN/END` marker'larıyla (placeholder-form) sarılır.
   Bu, sweep iş paketinin **zorunlu bir adımıdır** (Bölüm 8) — ad hoc/scope-dışı edit değil.
   **Acceptance:** Check A'dan önce canonical extraction **boş olmayan** blok döndürmeli;
   boşsa drift-check çalıştırılamaz (önce normalize et).
1. **Delimited, placeholder'lı ortak çekirdek blok.** Codex Çağrı Protokolü'nün
   *operasyonel çekirdeği* her iki komutta da `<CALL>`/`<STEP_A>`/`<STEP_B>`
   placeholder'larıyla yazılır → byte-identical olur. İşaretleyici:
   ```
   <!-- CODEX-CALL-PROTOCOL:BEGIN (canonical: spec-claude-codex; biri değişirse diğeri de) -->
   ...ortak çekirdek (placeholder'lı)...
   <!-- CODEX-CALL-PROTOCOL:END -->
   ```
2. **Extraction (somut komut):**
   `awk '/CODEX-CALL-PROTOCOL:BEGIN/{f=1} f{print} /CODEX-CALL-PROTOCOL:END/{f=0}' <dosya>`
3. **Check A — DIRECTIONAL drift (birincil güvence):** yeni komuttan çıkarılan blok,
   **canonical** = `~/.claude/commands/spec-claude-codex.md`'nin **canlı** bloğuna karşı
   `diff` → **fark 0**. Yön var (simetrik değil): doğruluk canonical'dan **miras alınır**.
   diff=0 ise blok, çalışan/kanıtlanmış canonical ile birebir aynıdır → operasyonel doğru.
4. **Check B — secondary tripwire:** çıkarılan blok şu token'ları içermeli (kazara
   yarım-paste'i diff'ten önce yakalar): `codex-companion.mjs`, `git rev-parse`,
   `AGENTS.md`, `timeout 480s`, `exit 124`, 3 degradation seçeneği.
5. **"Senkronize-yanlışlık" sınırı (Codex Bulgu 1'e kısmi yanıt):** Check A directional
   olduğu için "iki kopya da yanlış" durumu ancak **canonical'ın kendisi bozulursa**
   olur — bu `/spec-claude-codex`'in kendi spec'i + consistency checklist'inin
   sorumluluğudur (bu komutun kapsamı dışı). Full protokol gövdesini bu spec'e gömmek
   **üçüncü bir drift yüzeyi** yaratırdı; bu yüzden kabul edilmedi. Token'ların yapısal
   (parse-edilen) doğrulaması ileride CI hook'u olabilir (Bölüm 12, out-of-scope).

## 3. Akış (0–19)

```
0.  Active context read (koşullu — docs/active/ varsa, read-only)
1.  Spec'i bul ve oku (arg <SPEC_PATH> veya docs/specs/ en yeni)
2.  Spec approval metadata doğrula (katı; değilse explicit override)
3.  Resume kontrolü (discovery: legacy-önce, sonra pair-validation; approved reopen atomik)
4.  Overkill ön-kontrol (tam akış mı; değilse manuel writing-plans öner + çık)
5.  Claude implementation ön-analizi (Codex'ten önce sabitle)
6.  Codex implementation strategy/risk/task-order (Codex Çağrı Protokolü)
7.  Claude öneri + steelman + <DROPPED_ALT>
8.  Kullanıcı yön seçer / sentezi onaylar
9.  superpowers:writing-plans ile plan draft
10. Plan frontmatter + review metadata ekle
11. Claude consistency sweep (Codex öncesi)
12. Codex adversarial plan review (Codex Çağrı Protokolü; stdout verbatim + log append)
13. Karar: onayla → 15 / güncelle → 14 / durdur
14. Refine loop (critical/high özet; medium/low audit; max 3 full plan iteration)
15. Final consistency sweep
16. Finalizasyon (status: plan-approved)
17. Commit onayı (push YOK)
18. Commit sonrası active task yaratma sorusu (status=proposed; template fallback)
19. Subagent/Inline execute seçeneği + final rapor (→ /execute-plan <PLAN_PATH>)

(Codex çağrıları — Adım 6, 12 — "Codex Çağrı Protokolü"nü izler.)
```

### Adım detayları (kritik olanlar)

- **Adım 2 — Approval doğrulama (katı):** `status: spec-approved` **ve**
  `codex_review_status: approved|approved-by-iteration-limit` ise → `false`, devam.
  Uymuyorsa `AskUserQuestion`: *Override et* (frontmatter `true` + audit satırı) /
  *Durdur* (önce `/spec-claude-codex`).
- **Adım 4 — Overkill ön-kontrol (komut artefakt ÜRETMEZ; Codex Bulgu 2, turn 3):**
  Spec küçük/mekanikse kullanıcıya sor (otomatik atlama YOK). Hafif yol seçilirse komut
  **artefakt üretmeden çıkar** ve önerir: *"Bu spec küçük — `superpowers:writing-plans`'i
  doğrudan kendin çalıştır (review-gate'siz hızlı plan), ya da tam akışa devam et."*
  Böylece bu komuttan çıkan **her plan tam review'dan geçer** (review-gated invariant
  kırılmaz); deprecated `/write-plan`'a yönlendirme veya komut-içi review'sız artefakt yok.
  (`/spec-claude-codex`'in overkill kapısıyla aynı desen: vazgeç → öner + çık.)
- **Adım 5 — Claude ön-analizi (8-12 satır):** 2-3 implementation stratejisi, task
  ordering/bağımlılıklar, test/migration/deploy/rollback sıcak noktaları, 1-2 soru.
  **Perspektif bağımsızlığı:** Codex'ten önce sabitlenir, sonra revize edilmez.
- **Adım 6 — `<CALL> = task --fresh`:** `--write` olmadan read-only sandbox; `--cwd
  $PROJECT_ROOT` ile AGENTS.md otomatik.
- **Adım 12 — `<CALL> = adversarial-review $SCOPE`:** plan-özel checklist (Bölüm 7);
  `<DROPPED_ALT>`'a karşı "yön doğru muydu".

## 4. Codex'in Açtığı Riskler — Formalize Çözümler

- **R1 / G15 + review izolasyonu (Codex Bulgu 6, turn 1+2):** Review (Adım 12)
  commit'ten (Adım 17) **önce** → normal akışta plan uncommitted → `--scope working-tree`.
  Resume istisnası: commit'lenmiş `plan-draft` → clean ağaç → base/ref iste.
  - **Birincil mekanizma:** prompt `<PLAN_PATH>` içeriğini **doğrudan okutur** (scope ikincil).
  - **İzolasyon kapısı:** `git status --short` çok sayıda **alakasız** dirty dosya
    gösterirse `AskUserQuestion`: *(a)* plan'ı (+review log) önce commit'le, base ref'e
    karşı **izole** review (önerilen); *(b)* gürültülü devam.
  - **Noisy'den approval kalıcı işaretlenir:** (b) seçilirse `plan-approved` **ancak**
    kullanıcı açıkça onaylar + frontmatter `noisy_review_override: true` + audit satırı
    yazılırsa üretilir. Onsuz noisy working-tree'den `plan-approved` YOK.
- **R3 (override sessiz bypass olmasın):** Override → frontmatter flag **+ final rapor +
  audit log**: "spec planlama anında `<status>`/`<codex_review_status>` idi, kullanıcı override etti".
- **Q2 (onaylı spec — katı):** Yalnız `spec-approved` + `approved|approved-by-iteration-limit`.
  Eski/prose/frontmatter'sız → onaysız → override yolu.
- **Q3 (vault closure):** Repo/global komut + Claude-owned vault güncellemesi tek paket;
  vault ayrı **zorunlu closure adımı** (Codex yazamaz). Komut "done" sayılmadan vault güncel.

## 5. State Machine, Metadata, Sayaç, Resume

### Plan frontmatter (komutun ÜRETTİĞİ çıktının şeması)

```yaml
---
title: <başlık>
status: plan-draft
date: YYYY-MM-DD
source_spec: docs/specs/YYYY-MM-DD-<slug>.md
source_spec_unapproved_override: false
noisy_review_override: false           # true ise: gürültülü working-tree'den approve edildi (Bölüm 4)
codex_plan_review_status: pending      # pending | approved | approved-by-iteration-limit
codex_plan_review_iterations: 0
codex_plan_targeted_fixes: 0
codex_plan_review_log: docs/reviews/codex/YYYY-MM-DD-<slug>-plan.md
---
```

Final: `status: plan-approved`, `codex_plan_review_status: approved` (veya `approved-by-iteration-limit`).

> `-plan` suffix'i review log'da spec review log'uyla çakışmayı önler.

### İzinli / yasak çiftler (status, codex_plan_review_status)

İzinli: `plan-draft+pending`, `plan-approved+approved`, `plan-approved+approved-by-iteration-limit`.
**Yasak:** `plan-approved+pending` (review'sız approval) ve diğer tüm kombinasyonlar.
Reopen **atomik**: `plan-approved → plan-draft+pending` aynı anda.

> Komut **review-gate'siz artefakt üretmez** (Adım 4 hafif yol artık çıkış önerir, plan yazmaz)
> → `not-run` gibi review'sız bir state'e gerek kalmadı; state machine sade tutuldu.

### Sayaç modeli (source-of-truth = frontmatter, resume-safe)

- `codex_plan_review_iterations` (full plan iteration) — task yapısı/sıra/strateji/
  kapsam değişikliği. **Limit 3.** Resume'da elle aşılmış olabilir → `>=3` (== değil).
- `codex_plan_targeted_fixes` (targeted fix) — yalnız path/komut/wording/frontmatter.
- İkisine de dokunan → full plan iteration (conservative).

### Resume discovery algoritması (Adım 3 — Codex Bulgu 3, turn 1-3)

1. **Aday tara:** `docs/plans/*.md`; her dosyanın `source_spec`'ini oku.
2. **Eşleştir:** birincil `source_spec == <SPEC_PATH>`; ikincil slug.
3. **Legacy tespiti (pair-validation'dan ÖNCE — Codex Bulgu 3, turn 3):** adayda
   `codex_plan_review_status` / `codex_plan_review_iterations` alanları **yoksa** → `legacy`
   (eski `/write-plan` çıktısı). Sessiz devralma YOK; kullanıcıya sor, onayda **atomik
   migration** hedefi: `status: plan-draft`, `codex_plan_review_status: pending`,
   `codex_plan_review_iterations: 0`, `codex_plan_targeted_fixes: 0`,
   `codex_plan_review_log: docs/reviews/codex/<date>-<slug>-plan.md`. Migration sonrası resumable.
4. **Pair-validation (yalnız NON-legacy adaylar):** (status, codex_plan_review_status)
   çiftini izinli kümeye karşı doğrula. **Yasak çift** (örn. `plan-approved+pending`,
   `plan-draft+approved`) → resumable SAYMA; blokla + kullanıcıdan **açık atomik onarım** al.
5. **Sınıflandır (geçerli çiftler):**
   - `plan-draft+pending` → **resumable** (sayaçlar frontmatter'dan).
   - `plan-approved+approved(-by-iteration-limit)` → kullanıcı onayıyla **atomik reopen**.
6. **Çoklu eşleşme:** numbered list, kullanıcı seçer.
7. **Eşleşme yok:** yeni plan akışı.

## 6. Degradation (Codex Çağrı Protokolü downstream)

- **Adım 6 (ön-analiz) çökerse → Claude-only:** tek perspektif; steelman/`<DROPPED_ALT>` atlanır.
- **Adım 12 (review) çökerse → Claude-only:** review yok → **`plan-approved` ÜRETİLMEZ**.
  Adım 13: *Codex'i tekrar dene* / *durdur* (plan `plan-draft+pending` kalır).

## 7. Consistency Checklist (plan-özel; Adım 11 + Adım 15)

**Genel (her zaman):**
- Plan spec kararlarını kapsıyor mu, **yalnızca** onları mı (scope creep yok)?
- Görevler 2-5 dk, sıra/bağımlılık doğru mu?
- Her görevde tam dosya yolu + tam kod; placeholder ("TBD", "// implement here") yok mu?
- TDD gerçek mi (test önce, fail, sonra kod)? Her görev sonunda commit noktası + test komutu?
- Path/komut/flag/dosya adları birebir doğru mu? (referans bütünlüğü)
- (status, codex_plan_review_status) çifti izinli mi?
- `source_spec` doğru mu? `source_spec_unapproved_override` / `noisy_review_override`
  Adım 2 / Bölüm 4 kararlarıyla tutarlı mı?
- **Drift-check: `CODEX-CALL-PROTOCOL` Check A (directional diff=0) + Check B (token tripwire) geçiyor mu? (Bölüm 2)**

**Koşullu (migration/deploy/rollback/manuel-adım varsa):**
- Migration sırası + geri-alma (down)? Deploy + rollback? Manuel adımlar (env/secret/backfill) işaretli mi?
- Codex çağrıları preflight/timeout/degradation izliyor mu?

## 8. Blast-Radius / Occurrence-Level Sweep (Codex Bulgu 4)

Sınıflar: `live` (güncelle), `stub`, `dated` (dokunma), `example` (dokunma).

> **Satır numarası YOK** (drift eder). Envanter 2026-05-25 itibarıyla; implementasyonda **re-grep**.

| Dosya | Occurrence bağlamı | Sınıf | Aksiyon |
|---|---|---|---|
| `~/.claude/commands/spec-claude-codex.md` | desc; "Final rapor (+ /write-plan)"; "/write-plan'a ait"; "Sonraki adım: /write-plan <SPEC>" | live | → yeni |
| `~/.claude/commands/spec-claude-codex.md` | "otomatik write-plan önerisi görmezden gel" (writing-plans **skill** zinciri) | example | **dokunma** (İlke 1) |
| `~/.claude/commands/brainstorm.md` | worktree önerisi; "/write-plan ile devam"; "Sıradaki: /write-plan" | live | → yeni |
| `~/.claude/commands/handoff.md` | "Önce /write-plan ile task yarat" | live | → yeni |
| `~/.claude/commands/plan-claude-codex.md` | "Spec final olduktan sonra: /write-plan" | live | → yeni |
| `~/.claude/CLAUDE.md` | komut listesi, workflow diyagramı, path konvansiyonu, "/brainstorm → /write-plan" | live | → yeni |
| `/root/otomaix/CLAUDE.md` | "/write-plan sonu → TASK + HANDOFF" | live | → yeni |
| vault `cross-project/infrastructure/claude-code-workflow.md` | komut tablosu, workflow sırası, path, örnekler (~6) | live | → yeni (**Claude yazar**) |
| `~/.claude/commands/write-plan.md` | komutun kendisi | stub | `[DEPRECATED]` |
| `~/.claude/commands/sync-agents-md.md` | EXCLUDE-list örneği | example | **dokunma** |
| vault `codex-entegrasyonu.md` | EXCLUDE-list örneği | example | **dokunma** |
| tarihli `docs/specs\|plans\|reviews/*`, vault `decisions/2026-05-19-*` | tarihli kayıt | dated | **dokunma** |

**Acceptance:** her tutulan `/write-plan` occurrence'ı için sınıf + gerekçe belgelenir;
`live` sınıfından geriye `/write-plan` kalmaz (re-grep ile doğrula).

> **Ek (Bölüm 2 prerequisite):** `spec-claude-codex.md` bu pakette ayrıca protokol
> `CODEX-CALL-PROTOCOL:BEGIN/END` marker normalizasyonu alır (canonical'ı drift-check'e
> hazır hale getirir). Bu, `/write-plan` sweep'inden ayrı ama aynı iş paketinde.

## 9. Out-of-Scope

- `/execute-plan` **değişmez** — yalnız üretilen plan'ı tüketir. (Bu komuttan çıkan her plan
  zaten `plan-approved` olduğundan ek bir execute-gate gerekmez — hafif/review'sız artefakt üretilmez.)
- Active-task template şeması **değişmez** (yeni komut kullanır + fallback).
- `/spec-claude-codex` **davranışı** değişmez — yalnız `/write-plan` referansları güncellenir.
- Vault `decisions/` yeniden yazılmaz; Codex vault yazma yetkisi açılmaz.
- Otomatik CI drift-check hook'u (Bölüm 2 check'i elle/acceptance; CI gelecekte).

## 10. Sözleşme Notları

- **Manuel mod:** Her aşamada (2, 4, 8, 13, 17, 18) kullanıcı kararı. Sayaç 3'ten sonra zorla manuel.
- **Review-gated approval:** `plan-approved` = Codex review etti. Hafif/review'sız plan
  bu komuttan çıkmaz (Adım 4 çıkış önerir). Degradation'da final üretilmez.
- **Active task sahipliği:** Yaratım bu komuta ait. Status=proposed; template fallback korunur.
- **Codex araç ayrımı:** Adım 6 `task --fresh` (read-only); Adım 12 `adversarial-review`
  (read-only hardcoded). İkisi de foreground + dış `timeout 480s` (background DEĞİL).
- **Companion path:** dinamik `find`.
- **Drift enforcement:** `CODEX-CALL-PROTOCOL` Check A (directional) + Check B (Bölüm 2).
- **Vault promotion bu komutta YAPILMAZ** — `/commit` veya closure'a bırakılır.

## 11. Bootstrap Closure (Codex Bulgu 5)

Bu komutu hayata geçiren ilk plan ("bootstrap plan") emekliye ayrılan zayıf yoldan
(review-gate'siz) üretilmesin:

1. Bootstrap plan eski `/write-plan` (henüz fonksiyonel) **veya** elle yazılır.
2. **Elle sertleştirme (zorunlu):** yeni plan frontmatter'ı uygulanır; bir kerelik
   Codex adversarial plan review; audit log; spec onayı kontrolü. Bootstrap artefaktı da review-gated olur.
3. **Stub'a çevirme sırası:** `/write-plan` → stub **ancak bootstrap plan `plan-approved`
   olduktan sonra** (replacement'ın planı review-gated olmadan zayıf yol kaldırılmaz).
4. Tek-seferlik istisna; sonraki tüm planlar `/write-plan-claude-codex` ile.

## 12. Açık Problemler / Bilinmezler

- **Drift CI:** Bölüm 2 Check A/B disiplini acceptance kuralı; token'ların **yapısal**
  (parse-edilen) doğrulaması + otomatik CI hook bu spec dışı (gelecek iyileştirme).
- **Canonical koruması:** Check A directional olduğu için doğruluk `/spec-claude-codex`'in
  bloğundan miras alınır; o bloğun doğruluğu o komutun kendi spec'i + checklist'ine emanet.
