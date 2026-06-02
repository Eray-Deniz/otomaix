---
title: finish-branch-claude-codex.md — Tasarım Spec
status: spec-approved
date: 2026-06-02
tags: [claude-code, codex, slash-commands, finish-branch, closure-audit, claude-codex-family]
codex_review_status: approved
codex_review_iterations: 2
codex_targeted_fixes: 3
unresolved_high_severity_override: false
codex_review_log: docs/reviews/codex/2026-06-02-finish-branch-claude-codex-command.md
---

# finish-branch-claude-codex.md — Tasarım Spec

## Hedef

Mevcut tek-aktörlü `/finish-branch` (branch kapanış orkestrasyonu: merge / PR / tut / sil
+ aktif task-layer closure matrix + vault promotion) komutunu claude-codex ailesine entegre
eden `~/.claude/commands/finish-branch-claude-codex.md` komutunu oluştur. Codex'e **closure-readiness
audit** rolü verilir (kod/güvenlik review DEĞİL — o zincirde zaten `/review-claude-codex` +
`/security-review-claude-codex` ile yapıldı). Eski `/finish-branch` deprecated stub'a indirgenir;
aile drift contract'ı 6-way → 7-way büyür.

**Başarı kriteri:** mevcut finish-branch'in 8-adımlık kapanış akışı (closure matrix, Adım6→Adım7
sıra disiplini, detached HEAD dalları) **bozulmadan korunur**; üzerine advisory bir Codex closure-audit
adımı eklenir; 7-way drift Check A/B geçer; advisory/gate ayrımı + scope-creep guardrail prompt
seviyesinde sert yazılır; eski komut deprecated stub; restart sonrası komut yüklenir.

## Aileden Fark — neden review/security topolojisi DEĞİL

Aile üyelerinin hepsinin bir **iş-ürünü** var ve Codex onu inceliyor:

- spec/write-plan/execute/simplify → *Claude üretir, Codex adversarial review eder* (üretici + hakem)
- review/security-review → *iki bağımsız hakem + ana Claude sentez*

`/finish-branch` **lifecycle/orkestrasyon** komutudur — bir artefakt üretmez (spec/plan/kod/review
raporu gibi). Ortada Codex'in "review edeceği" bir Claude iş-ürünü yok. Bu yüzden Codex'in rolü
sıfırdan tanımlanır: **closure-readiness audit** — branch kapanışa hazır mı (review/security yapıldı
mı, açık problem var mı, vault promote adayı kaldı mı, commit hijyeni, merge/mainline/detached
riskleri). Bu, review/security-review'dan **farklı bir mercek**: onlar kod kalitesine/güvenliğe
bakar; bu komut *"kapanışa hazır mıyız"*a bakar.

## İnvariant (komutun ana sözleşmesi)

> **Bu komut bir GATE değil, advisory'dir.** Codex closure-audit yalnızca **risk sinyali** üretir;
> hiçbir A/B/C/D (merge/PR/tut/sil) dalını otomatik tetiklemez, bloke etmez. Kullanıcı audit'i
> gördükten sonra kapanış yolunu **kendi** seçer. Codex degrade olursa (companion yok / timeout /
> hata) kapanış **bloke edilmez** — "audit çalışmadı" notu düşülür, akış devam eder. Bu, aileden
> (review/security-review'ın chain-advance gate'inden) **bilinçli sapmadır**; çünkü finish-branch
> destructive (D=sil) ve outward-facing (push/PR) aksiyon içerir, Codex'in çalışmaması kullanıcıyı
> kendi branch'ini kapatmaktan alıkoymamalı.

> **Advisory ilkesinin TEK istisnası (zorunlu invariant):**
> *"closure-blocker is not a gate, except it upgrades destructive discard confirmation text."*
> Yani closure-blocker yalnız **D=sil** yolunda davranış değiştirir: standart `discard` onay metni,
> tespit edilmiş blocker varken `discard despite closure blockers`'a yükseltilir (muscle-memory
> `discard`'ı engeller). Diğer hiçbir yolda (A/B/C) ve closure-blocker dışındaki hiçbir durumda
> akış davranışı değişmez. Bu istisna **yalnız destructive yönde** ve **yalnız kanıtlanmış blocker**
> için geçerlidir (degrade/blocker-yok → standart `discard`).
>
> **İki-fazlı blocker türetme (Codex T1 high#2 — aksiyon-bağımlılık çözümü):** Audit seçimden ÖNCE
> çalıştığı için Codex **aksiyon-nötr facts** üretir (örn. `coverage-uncertain`, `unmerged commit`,
> `unpushed work`) — bunlar audit-zamanında blocker/warning olarak SABİTLENMEZ. Final
> closure-blocker/warning sınıflaması **kullanıcı aksiyonu seçtikten SONRA** Claude tarafından
> yapılır (Adım 8): `coverage-uncertain` / `unmerged` / `unpushed` gibi facts **D=sil** seçildiğinde
> Codex'in ilk etiketinden bağımsız **confirmation-blocker** olur. Yani upgrade, "audit-zamanı etiketi"ne
> değil, **"seçilen-aksiyon × fact" reclassification**'ına bağlıdır — aksiyon-bağımlı bir fact'in
> warning olarak emit edilip D=sil'de upgrade'i kaçırması yapısal olarak imkânsız.

## Mimari Yön — Tek Codex closure-readiness audit (onaylandı)

**Tek Codex pre-flight closure-audit.** Fresh Claude subagent YOK (review'ın çift-bağımsız-hakem
modeli burada overkill: closure kararı subjektif, ana Claude zaten closure state'i görüyor,
cross-model çeşitlilik değeri düşük). Reddedilen alternatifler:

- **Codex'i "Claude'un kapanış kararını review eden" yapmak** → ince değer (review edilecek iş-ürünü yok).
- **İki bağımsız hakem (review aynası)** → overkill (yukarıda).
- **STEP_B `adversarial-review --base` (normal/mainline simetri için)** → `<DROPPED_ALT>` (Codex T1
  medium#5 ile güçlendirildi): asıl decisive gerekçe **vokabüler kontrolü** — `adversarial-review`
  companion schema'sı `critical|high|medium|low` severity **zorlar**; closure-only vocab
  (`closure-blocker/warning/note`) bu schema üstünde prompt ile güvenilir override edilemez (fragile,
  scope-creep davet eder). STEP_A (`task --fresh`) serbest-form prompt → vocab tam kontrol. (Codex haklı
  olarak "adversarial-review da task-state'i `--cwd` ile Read edebilir" dedi → tek-diff sınırı decisive
  DEĞİL; gerekçe vokabülere kaydırıldı.) **Compensating control:** STEP_A diff-bound olmadığından, Claude
  Adım 5'te **exact range diff snapshot**'ı (scope `git diff` + commit listesi) evidence olarak enjekte
  eder + prompt "yalnız bu range üzerinde rapor ver" der. Bkz. Çekirdek Karar 1.

## Çekirdek Kararlar

### 1. Codex çağrı tipi = STEP_A `task --fresh` + Claude-computed scope/evidence

Codex çağrısı **her modda `<STEP_A>` (`task --fresh`)**. Gerekçe (decisive = vokabüler/schema kontrolü;
Mimari DROPPED_ALT ile hizalı):
- **Decisive — vokabüler/schema kontrolü:** `adversarial-review` companion schema'sı `critical|high|...`
  severity **zorlar** → closure-only vocab (`closure-blocker/warning/note`) override fragile + scope-creep
  davet eder; `task --fresh` serbest-form prompt → closure vocab tam kontrol. **Her iki çağrı da `--cwd`
  ile task-state'i (TASK/HANDOFF, `docs/reviews/`, `docs/security-reviews/`) Read edebilir — yani
  task-state körlüğü decisive DEĞİL; ayrım vokabülerdedir** (Codex T1 medium#5 ile hizalı; STEP_B'nin
  tam reddi: Mimari DROPPED_ALT).
- **Compensating control:** STEP_A diff-bound olmadığından Claude exact range diff snapshot'ı evidence
  olarak enjekte eder + "yalnız bu range üzerinde rapor ver" (Mimari DROPPED_ALT telafisi).

**Mode-aware scope'u Claude kendi hesaplar** (Codex'in çağrı tipinden ayrık), evidence olarak prompt'a
enjekte eder. Codex deterministik git işlemine (ancestry, merge-base) **güvenilmez** — Claude kendi
Bash'inde toplar, Codex yorumlar/sentezler:
- normal-branch → `merge-base(origin/$DEFAULT, HEAD_SHA)..HEAD_SHA`  (`$DEFAULT` = remote default branch)
- mainline → `origin/$DEFAULT..HEAD`
- detached → dar best-effort + ref-loss

Evidence'a **exact range diff snapshot** dahildir (scope'un `git diff` + commit listesi + `--stat`);
prompt Codex'e *"yalnız bu range üzerinde rapor ver"* der → STEP_A'nın diff-bound olmamasının
compensating control'ü (Mimari DROPPED_ALT telafisi).

### 2. Advisory + tek istisna (yukarıdaki İnvariant)

closure-blocker bile akışı durdurmaz. Tek davranış-değişikliği: D=sil confirmation upgrade.

### 3. Mode-aware izolasyon (review/security'den miras, sadeleştirilmiş)

Codex `task --fresh` **canlı HEAD** okur (companion `--head` almaz). Branch işlemleri (checkout main /
merge / branch delete) HEAD'i mutate eder → audit **branch işleminden ÖNCE** çalışmalı, ve:
- **normal-branch** → pinli worktree ZORUNLU (`git worktree add --detach $HEAD_SHA`; `--cwd $WT`).
  Audit branch-op'tan önce çalışsa da, izolasyon dirty-tree sızıntısını + canlı-HEAD race'ini kapatır.
- **mainline** → worktree GEREKSİZ ama **HEAD_SHA pre/post equality guard ŞART (Codex T1 high#3)**.
  finish-branch mainline'da HEAD mutate etmez (merge/checkout yok, yalnız push), AMA bu canlı-HEAD
  race'ini kapatmaz: başka terminal/hook/bg-tool Codex çalışırken (≤480s) veya evidence↔push arası
  commit/amend/rebase yapabilir → evidence/audit/pushed-HEAD diverge (outward push'ta tehlikeli).
  Çözüm: `--cwd $PROJECT_ROOT` + Adım 5 başında `HEAD_SHA` pin; Codex dönüşünde **ve** push/PR/destructive
  ÖNCESİ `git rev-parse HEAD == HEAD_SHA` kontrolü. Değişmişse audit **invalidate + recompute** —
  eski evidence ile push/PR/sil YASAK.
- **detached** → dar kapsam; worktree opsiyonel (HEAD zaten detached, audit sonrası kullanıcı kararı).

**Pinned-target binding (tüm modlar — Codex T2 high#2, TOCTOU):** Pre/post HEAD guard stale-evidence'ı
*tespit* eder ama check↔act penceresini kapatmaz (başka terminal/hook araya commit'leyebilir). Bu yüzden
outward/destructive op **pinned `HEAD_SHA`'yı hedefler**, live ref'i DEĞİL:
- mainline push → `git push origin ${HEAD_SHA}:refs/heads/<default-branch>` (live HEAD değil, audited SHA)
- normal-branch merge → `git merge ${HEAD_SHA}` (live feature-branch ref'i değil, audited commit)
- **D=sil (discard) → old-value-bound delete** (en yüksek-risk, irreversible — Codex T3 high#1):
  `git branch -D <branch>` (branch-name delete) DEĞİL; checkout sonrası
  `git update-ref -d refs/heads/<branch> $HEAD_SHA` (yalnız ref hâlâ audited `HEAD_SHA` ise atomik siler).
  Ref diverge ettiyse → abort + recompute (audited-olmayan commit silinmez). **detached** → branch yok,
  commit'ler zaten unreachable olur (mevcut ref-loss uyarısı geçerli).
- PR / branch metadata → pinned `HEAD_SHA` kaydedilir/kullanılır

Guard (tespit) + pinned-target (refspec) birlikte check-then-act penceresini kapatır. HEAD audited SHA'dan
saparsa: kullanıcıya bildir + recompute/onay — audited-olmayan commit sessizce push/merge edilmez.

### 4. Evidence aralık-kapsama (closure-uncertain sinyali)

"review + security-review yapıldı mı" sorusu **dosya-varlığı + aralık-kapsama** ile yanıtlanır
(yalın dosya-varlığı yetersiz — "hangi commit'e kadar?"u atlar):

- **Primary sinyal:** `docs/reviews/*-<slug>.md` + `docs/security-reviews/*-<slug>.md` mevcut mu;
  TASK.md `# Open Problems`'da çözülmemiş critical/high var mı.
- **Aralık-kapsama (iki katman):**
  - **(a) Kesin yol — range-containment, yalnız HEAD değil (Codex T1 high#1):** aile raporları
    başlığında `REVIEW_BASE_SHA..HEAD_SHA` taşır. **Hem `report_BASE` hem `report_HEAD` parse edilir.**
    Tam kapsama = `report_HEAD == audit_HEAD` **AND** `report_BASE`, `audit_BASE`'in atası-veya-eşiti
    (`git merge-base --is-ancestor report_BASE audit_BASE`). Yalnız HEAD eşitliği YETMEZ: `HEAD~1..HEAD`
    raporu `origin/main..HEAD` audit'ini sahte "kapsandı" yapardı (erken commit'ler review'sız). İki
    SHA'dan biri yoksa veya bazlar karşılaştırılamazsa → **coverage-uncertain**.
  - **(b) Fallback:** rapor SHA taşımıyorsa (yabancı/eski/manuel rapor) → rapor commit/mtime vs son
    commit listesi heuristiği → coverage-uncertain.
- **Commit mesajı kullanılmaz** (güvenilmez sinyal).
- Bu kontrolü **Claude toplar** (deterministik git), Codex'e evidence olarak enjekte eder (Karar 1
  ile tutarlı). coverage-uncertain bulgusu **aksiyondan bağımsız** üretilir — A=merge'de de değerli
  ("review-edilmemiş commit merge ediyorsun"); D=sil + blocker'da ekstra-onaya, A=merge'de warning'e dönüşür.

### 5. Çıktı vokabüleri (scope-creep guardrail)

Codex çıktısı **closure-specific** vokabüler kullanır — severity (`critical/high/medium/low`) **YASAK**
(o, review'ın dili; Codex'i kod-review moduna çeker):

- **`closure-blocker`** — kapanışı gerçekten riske atan: review/security hiç yapılmamış · çözülmemiş
  critical Open Problem · D=sil'de unmerged/unpushed değerli iş · coverage-uncertain + destructive aksiyon.
- **`closure-warning`** — dikkat: vault promote adayı promote edilmemiş · coverage-uncertain · rapor
  aralığı eksik · merge öncesi divergence.
- **`closure-note`** — bilgi: WIP-benzeri commit mesajı · alakasız/scope-dışı dosya.

### 6. Default açık + atlama koşulları

Audit **default açık** (değeri yüksek, özellikle D=sil'de). Atlanır **yalnız** iki explicit/kanıtlı durumda:
- `--no-audit` argümanı (kullanıcı bilinçli opt-out)
- Codex degrade (companion yok / timeout / hata) → "audit çalışmadı (<sebep>)" + akış devam

**Seçim-öncesi C-tahminiyle atlama YOK (Codex T2 high#1):** audit her zaman seçimden ÖNCE çalışır (Adım 5);
C(tut) gerçekten seçilse bile audit çalışmış olur (zararsız — C no-op, bulgular yalnız gösterilir). Tahmine
dayalı skip iki-fazlı reclassify'ı delerdi (kullanıcı sonradan D=sil seçerse facts hiç toplanmamış olur).

## Adım Akışı (9 adım — finish-branch'in 8 adımı KORUNUR + audit eklenir)

```
1. Branch durumu + MOD tespiti (normal / mainline / detached) + CLI parse (--no-audit)
2. Test suite doğrulaması (mevcut — değişmez)
3. Skill yükle: superpowers:finishing-a-development-branch (mevcut)
4. Worktree kontrolü + (audit açıksa) izolasyon substratı kurulumu (mode-aware: normal→pinli worktree)
5. ★ YENİ: Codex closure-readiness audit (advisory) — evidence topla (Claude) → task --fresh → closure vocab çıktı
6. Seçenekleri sun (audit FACTS enjekte: aksiyon-nötr — `coverage-uncertain`/`unmerged`/... ) — mevcut Adım 5
7. Aktif task layer closure matrix (A/D=full closure+archive; B=waiting-review; C=no-op) — mevcut Adım 6
8. Branch işlemini uygula (A/B/C/D) — mevcut Adım 7; seçilen aksiyona göre facts→blocker/warning RECLASSIFY;
   D=sil + blocker → confirmation upgrade (`discard despite closure blockers`)
9. Bitiş raporu (mevcut Adım 8 + audit özeti)
```

**Sıra disiplini korunur:** Adım 7 (task closure) Adım 8 (branch-op) ÖNCE çalışır (D=sil'de
`git checkout main` + branch ref silme — Adım 8 old-value-bound delete — task dosyalarına erişimi
kaybetmesin). Audit (Adım 5) tüm bu mutasyonlardan önce, izole substratta.

## Codex Çağrı Noktası

| Adım | Çağrı | Amaç | Cadence |
|---|---|---|---|
| **5** | `task --fresh` (STEP_A) | Tek closure-readiness audit (advisory); Claude-computed scope+evidence prompt'a gömülü | Default açık (degradation → "audit çalışmadı", akış devam) |

`CODEX-CALL-PROTOCOL` bloğu canonical = `spec-claude-codex`'ten **byte-identical** kopyalanır. Blok hem
`<STEP_A>` hem `<STEP_B>` tanımlar; **bu komut yalnız `<STEP_A>`'yı kullanır** — `<STEP_B>`
(`adversarial-review`) canonical protokolde tanımlı ama bu komutta KULLANILMAZ (superset; binding'de işaretli).

## Doğrulanmış Teknik Kısıtlar (codex-companion.mjs 1.0.4)

- **`task --fresh`** `--write` OLMADAN read-only sandbox'ta çalışır; `--cwd` ile repo'yu Read edebilir.
- **`--head` parametresi YOK** → Codex daima canlı HEAD okur → normal-branch modunda **pinli worktree**
  HEAD race'ini + dirty sızıntısını kapatır. mainline modunda HEAD mutate olmadığı için worktree gereksiz.
- **`--background` task'ta var ama** review'da değil; uniform dış `timeout 480s` (CODEX-CALL-PROTOCOL).
- `--cwd $SCAN_ROOT` (normal→worktree, mainline→PROJECT_ROOT) → `AGENTS.md` otomatik yüklenir.

## Adım Detayları (kritik olanlar)

### Adım 1: Mod tespiti + CLI parse

Mod **deterministik git predicate**'lerle belirlenir — "ayrı feature branch var mı" sezgisi veya
session-semantic YOK (Codex T1 medium#4):

```bash
CUR=$(git branch --show-current)                 # boş → detached
DEFAULT=$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@')
UPSTREAM=$(git rev-parse --abbrev-ref '@{u}' 2>/dev/null)   # boş → upstream yok
```
- `CUR` boş/`HEAD` → **detached**
- `CUR == DEFAULT` (current = remote default branch) → **mainline** (kapatılacak ayrı feature branch
  yok; yalnız upstream'e ahead commit'ler push edilir)
- `CUR != DEFAULT`, isimli branch → **normal-branch**
- **Belirsizlik → DUR, kullanıcıya sor (inference YASAK):** `origin/HEAD` yok/stale, default branch
  rename, `CUR` upstream'i yok → mod kesinleşmez → `AskUserQuestion` (normal/mainline/detached). Sezgiyle
  varsayma — misclassification mainline'da pinned-worktree'yi kaldırdığı için pahalı (high#3 ile birleşir).
- `--no-audit` argümanı → `AUDIT_ENABLED=false`.

`MODE ∈ {normal, mainline, detached}` Adım 4/5'e taşınır.

### Adım 5: Codex closure-readiness audit (advisory) — YENİ

1. **AUDIT_ENABLED=false** (`--no-audit`, explicit opt-out) **veya** Codex preflight fail (degrade) →
   audit atlanır, "closure-audit atlandı (<sebep>)" notu, Adım 6'ya geç. **Seçim-öncesi C-tahminiyle
   atlama YOK** (Codex T2 high#1) — audit hep seçimden önce çalışır (Karar 6).
2. **HEAD pin (her mod):** `HEAD_SHA=$(git rev-parse HEAD)`. normal → pinli worktree zaten `HEAD_SHA`'da;
   mainline → `--cwd $PROJECT_ROOT` + bu `HEAD_SHA` Codex dönüşünde + Adım 8 öncesi guard'lanır (high#3).
3. **Evidence topla (Claude, deterministik):** mode-aware scope SHA'ları (`audit_BASE`, `audit_HEAD`);
   **exact range diff snapshot** (`git diff` + commit listesi + `--stat`); review/security rapor varlığı +
   **range-containment** testi (Karar 4: `report_HEAD==audit_HEAD` AND `report_BASE` ⊑ `audit_BASE`);
   TASK.md Open Problems + Decisions Log "promote adayı" işareti; HANDOFF tutarlılığı.
4. **Codex çağrısı:** CODEX-CALL-PROTOCOL, `<CALL> = task --fresh`, `--cwd $SCAN_ROOT`. Prompt: closure-only
   talimat + closure vocab + negative instruction ("do NOT hunt code-quality/security bugs") + enjekte
   evidence (range diff snapshot dahil; "yalnız bu range üzerinde rapor ver") + mevcut review/security
   rapor yolları + mode + reduced-value notu (mainline/detached).
5. **Çıktı:** verbatim göster + `docs/reviews/codex/<DATE>-finish-branch-<SLUG>-<ATTEMPT>.md`'ye logla. Codex
   **aksiyon-nötr facts** üretir (`coverage-uncertain`, `unmerged`, `unpushed`, hijyen notları). Final
   `closure-blocker/warning/note` sınıflaması Adım 8'de seçilen aksiyona göre yapılır (İnvariant: iki-fazlı).
6. **Post-call HEAD guard (mainline/normal):** `git rev-parse HEAD == HEAD_SHA`? Değilse audit invalidate +
   evidence recompute (eski evidence ile ilerleme YASAK — high#3).

### Adım 6: Seçenekleri sun (audit enjekte)

Mevcut seçenek sunumu (normal: A/B/C/D; detached: B/C/D) + audit özeti başa eklenir:
> "Branch `<name>` kapanışa hazır. `<X>` commit, son test PASS.
> Codex closure-audit: `<N>` blocker, `<M>` warning, `<K>` note. [özet]
> Hangi yolu tercih edersin? A) merge B) PR C) tut D) sil"

### Adım 8: Branch işlemi — facts reclassify + D=sil confirmation upgrade

**Önce reclassify (iki-fazlı — Codex T1 high#2):** Adım 5'in **aksiyon-nötr facts**'ı seçilen aksiyona
göre final closure-blocker/warning'e dönüştürülür. D=sil seçildiyse `coverage-uncertain` / `unmerged` /
`unpushed` facts'ları **confirmation-blocker** olur (Codex'in audit-zamanı etiketinden bağımsız);
A=merge'de aynı facts **warning** (görünür, akış değişmez); B/C'de note/warning. Bu, aksiyon-bağımlı bir
fact'in warning emit edilip D=sil upgrade'ini kaçırmasını yapısal olarak engeller.

**Branch-op binding (Karar 3 pinned-target):** Tüm branch işlemleri (merge/push/PR **ve D=sil discard**)
audited `HEAD_SHA`'yı hedefler, live ref'i değil (TOCTOU kapanışı). D=sil **old-value-bound delete**
(`git update-ref -d refs/heads/<branch> $HEAD_SHA` — yalnız ref hâlâ audited SHA ise siler; `git branch -D`
DEĞİL). Pre-op HEAD guard sapma tespit ederse → bildir + recompute, audited-olmayan commit sessizce işlenmez.

D=sil yolunda, **reclassify sonrası closure-blocker varsa**:
1. Önce blocker özeti: "⚠️ Bu branch silinirse şu riskler kaybolabilir: `<blocker listesi>`"
2. Onay metni yükseltilir: standart `discard` yerine **tam olarak** `discard despite closure blockers` istenir.
3. Başka metin → DURDUR + tekrar sor.

**audit çalıştı, blocker yok** → standart `discard`. **audit ÇALIŞMADI + D=sil (Codex T2 high#1 defansif):**
`--no-audit` (bilinçli opt-out) → standart `discard` (sorumluluk kullanıcıda); Codex-degrade → blocker
kanıtlanamadı ama defansif: önce **audit retry öner**; retry de başarısızsa standart `discard` AMA belirgin
uyarı (*"⚠️ closure-audit yapılamadı — silmeden önce riskler kontrol EDİLMEDİ"*). Upgrade-metni zorlanmaz
(blocker kanıtı yok), uyarı görünür. A/B/C confirmation davranışını değiştirmez (reclassify yalnız warning üretir).

## Closure Audit Checklist (Codex'in baktığı — prompt'a gömülür)

- **Zincir bütünlüğü:** `/review-claude-codex` + `/security-review-claude-codex` yapıldı mı? (rapor
  varlığı + aralık-kapsama)
- **Açık problem:** TASK.md Open Problems'da çözülmemiş critical/high?
- **Vault promotion:** Decisions Log'da "promote adayı" işaretli ama vault'a girmemiş karar?
- **Commit hijyeni:** aralıkta WIP/stub/fixup commit, plan-kapsamı-dışı/alakasız dosya?
- **Task-layer tutarlılığı:** HANDOFF güncel mi, TASK status kapanışa uygun mu?
- **Mod riskleri:** normal→merge divergence/conflict; mainline→push-edilecek WIP (merge/branch N/A);
  detached→unpushed commit + ref-loss.

**NEGATIVE (sert):** Kod kalitesi, güvenlik açığı, mimari kritiği ARAMA — onlar zincirde yapıldı.
Yalnız kapanış-hazırlık sinyali üret. Çıktı `closure-blocker/warning/note` — severity YASAK.

## Sözleşme Notları

- **Advisory-only (aileden bilinçli sapma):** Bu komutta chain-advance gate **UYGULANMAZ**. Codex
  degrade → kapanış bloke edilmez. Tek davranış-istisnası: closure-blocker → D=sil confirmation upgrade
  (yukarıdaki invariant). Bu, review/security-review'ın gate modelinden kasıtlı farktır.
- **Scope-creep guardrail (prompt seviyesi):** closure vocab + negative instruction + mevcut review
  raporlarını input verme. Codex closure-audit asla kod/güvenlik review'a kaymaz.
- **Codex araç ayrımı:** Adım 5 → `task --fresh` (read-only, `--write` YOK). `<STEP_B>` canonical blokta
  tanımlı ama bu komutta KULLANILMAZ.
- **Codex read-only:** Codex vault/active-layer/rapor yazmaz. Vault promote adayını yalnız **sinyaller**;
  promote işini Claude+kullanıcı closure (Adım 7) sırasında yapar.
- **Mevcut finish-branch davranışı korunur:** closure matrix (A/D full closure+archive, B waiting-review,
  C no-op), Adım7→Adım8 sıra disiplini, detached HEAD dalları (A=merge yok, B/C/D + ref-loss), destructive
  discard onayı — hepsi aynen taşınır, audit + discard-upgrade üstüne eklenir.
- **Skill workflow override:** `superpowers:finishing-a-development-branch` yüklenir ama kendi
  default'ları (test komutu, seçenek metni) bu komutun adımlarına tabidir.
- **Companion path:** dinamik `find` (hardcoded sürüm yok).
- **Drift enforcement (canonical = spec-claude-codex):** CODEX-CALL-PROTOCOL bloğu **yedi komutta**
  byte-identical (aşağıdaki Drift Sözleşmesi).

## Drift Sözleşmesi (7-way)

`CODEX-CALL-PROTOCOL` bloğu canonical = `spec-claude-codex`; **7 komutta** birebir aynı:
- `spec-claude-codex.md` (canonical)
- `write-plan-claude-codex.md` (ayna)
- `execute-plan-claude-codex.md` (ayna)
- `simplify-claude-codex.md` (ayna)
- `review-claude-codex.md` (ayna)
- `security-review-claude-codex.md` (ayna)
- `finish-branch-claude-codex.md` (YENİ ayna)

**Check A (7-way):** `awk` ile her dosyadan BEGIN/END marker arası blok çıkarılır; altı diff'in
**hepsi 0** (`spec vs write-plan`, `spec vs execute`, `spec vs simplify`, `spec vs review`,
`spec vs security-review`, `spec vs finish-branch`). Pratik kısayol: yedi dosyanın blok md5'i eşit
(mevcut: `c7b5976c`, 68 satır — blok değişmez, yalnız ayna sayısı 6→7).

**Check B (tripwire):** çıkarılan bloklarda `codex-companion.mjs`, `git rev-parse`, `AGENTS.md`,
`timeout 480s`, `124`, 3 degradation seçeneği (`Claude-only devam et`, `Tekrar dene`, `Komutu durdur`)
**yedi dosyada** mevcut.

**"biri değişirse diğeri de"** referansı **7 komutu** sayar. finish-branch yalnız `<STEP_A>`'yı kullanır;
blok byte-identical kopyalanır (superset), binding'de `<STEP_B>` "bu komutta kullanılmaz" işaretlenir.
Refine: canonical tek yerde düzenlenir → marker-keyed mekanik propagation yedi dosyaya → Check A md5 +
Check B re-verify.

## Out of Scope

- **Codex'in kapanış kararı vermesi** — Codex advisory; merge/PR/tut/sil her zaman kullanıcı kararı.
- **Fresh Claude subagent (ikinci hakem)** — overkill; tek Codex audit yeterli.
- **Kod/güvenlik review tekrarı** — zincirde yapıldı; audit yalnız closure hijyeni.
- **Vault promotion'ın otomasyonu** — Codex sadece sinyal; promote Claude+kullanıcı (Adım 7).
- **chain-advance gate** — bilinçli yok (advisory).
- **CODEX-CALL-PROTOCOL bloğunun içeriği değişimi** — byte-identical kopya; içerik bu spec kapsamında değil.
