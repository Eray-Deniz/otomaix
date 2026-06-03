---
title: Auto-Fix Review Policy — claude-codex aile geneli
status: spec-approved
date: 2026-06-03
tags: [claude-codex, workflow, review-policy, drift-contract, auto-fix]
codex_review_status: approved
codex_review_iterations: 1
codex_targeted_fixes: 2
unresolved_high_severity_override: false
codex_review_log: docs/reviews/codex/2026-06-03-auto-fix-review-policy.md
---

# Auto-Fix Review Policy — claude-codex aile geneli

## Amaç / Problem

claude-codex komutları test edilirken tekrar eden bir friction tespit edildi: Codex bir
bulgu buluyor, ana Claude da aynı bulguyu doğruluyor — **iki perspektif net hemfikir**
olmasına rağmen komut her fix için ayrı kullanıcı onayı bekliyor. Bu, net-hemfikir
bulgularda gereksiz tıkanma yaratıyor.

İstenen: iki perspektif hemfikirse critical/high/medium bulgular kullanıcı onayı
beklemeden düzeltilsin; kullanıcı yalnızca (a) fix döngüsü tıkandığında ve (b)
durum-değiştiren operasyonlarda devreye girsin.

Bu spec, Claude + Codex çift-perspektif tartışmasıyla **3 tur (T1/T2/T3) adversarial
review** sonucu yakınsadı; convergence geçmişi aşağıda "Karar geçmişi"nde özetlenir.

## Karar Özeti (Decision Summary)

1. **Tetik:** `claude-confirmed Codex finding` (Codex buldu + Claude doğruladı +
   severity ∈ {critical, high, medium}) → kullanıcı onayı olmadan otomatik fix.
2. **Sert tavan:** otonom döngü sonsuz değil — cluster-key başına 6-tur tavanı **+ session
   global cap=10** (oscillation backstop), sonra kullanıcıya rapor + karar.
3. **Operasyonel carve-out:** otonomi yalnız *review-bulgusu düzeltme döngüsüne* hapsedilir
   (kod + spec/plan artifact dahil); hard insan-kapıları **push/merge/discard/branch silme +
   state/lifecycle + vault + override**. Executor local commit'leri mevcut task-başı cadence'i
   miras alır (yeni commit otonomisi yok; gate = push). Bkz. "Commit nüansı".
4. **medium tür-bazlı:** executor/security'de fix-required; spec/write-plan'da yalnız
   "teknik bug" sınıfıysa fix-required, tasarım-tradeoff ise kullanıcıya.
5. **low:** 3-tur bütçesi içinde düzeltilir, sonra audit-ignore.
6. **Kapsam:** execute-plan, simplify (yürütücü); spec, write-plan (tasarım-doc); review,
   security-review (report-only — yalnız vocab + chain-gate). finish-branch **kapsam dışı**.
7. **Mimari:** yeni byte-identical `AUTO-FIX-REVIEW-POLICY` marker bloğu (4 fix-yapan
   komut) + reviewer-side prose + drift-check Check D.

## Politika: "Auto-Fix Review Policy"

### Tetik koşulu (her komutta aynı)
Kanonik ad: **`claude-confirmed Codex finding`**. Bir bulgu yalnız şu üçü birlikte
sağlanırsa otomatik düzeltilir:
- **Codex** bulguyu üretti, **VE**
- **Claude** aynı bulguyu doğruladı, **VE**
- severity ∈ {critical, high, medium} (medium için aşağıdaki nüans).

Doğrulamanın kaynağı arketipe göre değişir: execute/simplify/spec/write-plan'da **ana
Claude'un validasyonu** yeter; review/security gibi çift-hakemli akışlarda bunun alt türü
**`both-agree`** (fresh Claude reviewer + Codex aynı bulguda).

Claude doğrulamazsa → **otomatik fix YOK.** Bulgu disposition ledger'da
`single-source` / `rejected` / `needs-human` kalır (mevcut ledger mekaniği korunur).

### Tur yapısı ve sert tavan (critical/high/medium)
- **Tur 1–3:** Claude kendi fix yaklaşımıyla düzeltir → verify → Codex re-review.
- **Tur 4+:** Codex çağrısı bulgunun yanında **zorunlu yapılandırılmış çözüm önerisi**
  döner: `root cause / minimal fix strategy / etkilenen dosya·fonksiyonlar / verification
  komutu / yanlışsa risk / fallback`. Claude değerlendirip uygular (kullanıcı onayı yok).
  *Codex read-only kalır — yalnız metin önerir, dosya YAZMAZ; uygulayan Claude.*
- **Tur 6 tavanı:** Aynı **finding-cluster / root-cause** 6 fix/review turu sonunda hâlâ
  kapanmıyorsa **otonom döngü DURUR.** Claude kullanıcıya somut rapor verir: kalan
  bulgular / kaç tur denendi / uygulanan fix'ler / Codex çözüm önerileri / neden kapanmadı
  (olası oscillation) / önerilen sonraki adım. Bundan sonrası kullanıcı kararı:
  **devam / kapsam daralt / manuel düzelt / blocked**.
  *Override sıradan bir seçenek gibi sunulmaz: yalnız ilgili komutun **mevcut explicit
  override kapısından** geçer (execute/simplify/spec/write-plan:
  `unresolved_high_severity_override`; security: ayrı ve ağır `security-risk override`).
  Otomatik önerilen yol değildir.*
- **"max review 3 geçersiz" anlamı:** "3'te otomatik approve etme" — *sonsuz döngü değil.*

### Cluster ledger + global cap (Codex T4 #2 — tavanı deterministik yapan kural)
"finding-cluster" subjektif kalmasın diye **deterministik ledger**:
- **finding-id:** Her bulgu ilk göründüğünde stabil bir id alır (artımlı: `F1, F2, …`).
- **cluster-key:** Normalize edilmiş **(etkilenen invariant/path/anchor)** — aynı dosya:satır
  veya aynı adlandırılmış invariant'a değen bulgular aynı cluster. Sentez ledger'ı (review'ın
  mevcut disposition ledger'ı) bu eşlemeyi tutar.
- **6-tur sayacı cluster-key başına.** Bir bulgu kapanıp **aynı cluster-key ile yeniden
  açılırsa** (reopen) → prior sayacı **miras alır** (sıfırlamaz). Gerçekten yeni bir
  cluster-key turn 1'den başlar.
- **Reopen = oscillation sinyali:** Kapanmış bir cluster-key 2. kez yeniden açılırsa →
  non-convergence kabul → o cluster için DUR + kullanıcı raporu (severity'den bağımsız).
- **Session-level global cap (asıl backstop):** Tek komut çalışmasında **toplam auto-fix
  turu** için global tavan = **10** (cluster split/merge ne olursa olsun). Global cap dolunca
  → tüm otonom döngü DURUR → kullanıcı raporu. Bu, cluster reclassification ile tavanı
  atlatan oscillation'a karşı kesin sınırdır.

### Low bulgular
- Fix/review turu ≤ 3 ise Claude low bulguları da düzeltir.
- 4. turdan itibaren kalan low → **audit-trail'e yazılır + göz ardı edilir**; komut
  kullanıcı onayı olmadan normal akışına devam eder.

### Medium nüansı (tür-bazlı)
- **execute-plan / simplify / security-review** (uygulama·güvenlik bağlamı): medium =
  **fix-required** (tavan altında).
- **spec / write-plan** (tasarım dokümanı): medium yalnız Claude bunu *"teknik
  tutarlılık/uygulanabilirlik bug'ı"* diye sınıflarsa fix-required. *Tasarım
  tercihi/tradeoff* ise iteration-limit (3) sonrası kullanıcı kararına bırakılır —
  tasarım niyeti kullanıcınındır.
- **Zorunlu açık sınıflandırma + kriterler (Codex T4 #4):** spec/write-plan'da Claude **her
  medium bulguyu raporda açıkça etiketler** + **bir-satır gerekçe** yazar:
  - **`technical-medium → auto-fix-required`:** invariant/schema/path/komut-adı/sıralama
    çelişkisi, eksik/yanlış cross-reference, uygulamayı bloke eden under-spec mekanik.
    (Örn: "rollback sırası tanımsız", "X komutu Y flag'ini desteklemiyor ama spec öyle diyor".)
  - **`tradeoff-medium → iteration-limit / user decision`:** ürün kapsamı, risk iştahı, UX
    tercihi, "hangi yaklaşım daha iyi" tasarım tercihi.
  - **Belirsizse default = `tradeoff-medium`** (kullanıcı kararına bırak) — şüphede tasarım
    niyetini gasp etme. Etiketsiz medium bırakılamaz.

### Carve-out (otonomi KAPSAM DIŞI — insan-kapısı korunur)
Şunlar fix döngüsü değil, operasyonel/state kapılarıdır ve **onay ister**:
vault/memory yazımı · active layer TASK.md/HANDOFF.md mutation · task status/lifecycle
değişimi · **push / merge / discard / branch·worktree silme** · security-risk override ·
dual-review override.

**Commit nüansı (Codex T4 #1):** "commit" mutlak insan-kapısı DEĞİLDİR — execute-plan
zaten task-başı `RED-GREEN-REFACTOR-COMMIT` ile **otonom local commit** atar (mevcut tasarım;
gate olan **push**'tur, Adım 14). Auto-fix döngüsü bu mevcut cadence'i **aynen miras alır,
yeni commit otonomisi EKLEMEZ** — fix'ler normal task işi gibi commit'lenir. Hard insan-kapıları:
**push / merge / discard / branch silme + state/lifecycle transition + vault + override**.
Report-only komutlarda (review/security/simplify-final) mevcut commit gate'i değişmez.

## Komut bazlı uygulama

| Komut | Arketip | Değişiklik |
|---|---|---|
| **execute-plan** | yürütücü | Adım 8.5 (checkpoint guard) + Adım 12 (final guard): "critical/high → kullanıcı seçer" yerine **C/H/M claude-confirmed → otonom mini-batch fix döngüsü** (Adım 7 RED-GREEN-REFACTOR). Tur≥4 Codex çözüm önerisi, tur 6 tavanı. low 4. turda audit-ignore. "Iteration-limit yok" korunur. Adım 9'daki **"3 başarısız deneme" (per-task TDD breaker) ayrı kavram — DOKUNULMAZ.** |
| **simplify** | yürütücü | Adım 10 final guard: C/H/M claude-confirmed → kullanıcı onayı olmadan mini-batch fix döngüsü. Tavan + Codex çözümü + low audit-ignore aynı. "Iteration-limit yok" korunur. |
| **spec** | tasarım-doc | Adım 7 karar dalı: C/H (+teknik-bug medium) → onay beklemeden spec-edit fix döngüsü, kapanana/tavan'a kadar. `approved-by-iteration-limit` artık yalnız **low + tradeoff-medium** için. medium artık iteration-limit ile sessizce geçilemez (tasarım-tradeoff istisnası hariç). |
| **write-plan** | tasarım-doc | spec ile aynı; Adım 14 refine loop + Adım 11 sayaç semantiği. medium plan bulgusu (teknik) fix-required; tradeoff-medium + low → `approved-by-iteration-limit`. |
| **review** | report-only | **Kod yazmaz — fix döngüsü EKLENMEZ.** Değişen: (1) disposition dili `medium/low: not düş` → **C/H/M = fix-required** (raporda + handoff'a yazılır); (2) chain-advance **hard-block eşiği critical/high'da kalır** (bugünküyle aynı); medium **advisory** — fix-required işaretlenir + Open Problems'a yazılır ama tek başına chain'i ÖLÜ-bloke etmez (fixer yok). Fiili düzeltme handoff contract ile executor'da (aşağıya bkz.). |
| **security-review** | report-only | review ile aynı + güvenlik: medium fix-required (evidence_gap ≥ medium taban). İki-katmanlı chain gate hard-block **critical/high**'da (security-risk override) + dual-review ekseni — bugünküyle aynı; medium advisory + handoff. **security-risk override AYRI kalır** (override = "bulgu doğru, riski kabul ediyorum" — fix değil). |
| **finish-branch** | danışma | **Kapsam DIŞI.** Severity sözlüğü bilerek yasak (`closure-blocker/warning/note`, STEP_B kullanılmaz). Severity politikası enjekte etmek closure-audit tasarımını bozar. (Olası gelecek: "closure-blocker 3 turdan sonra Codex çözümü" — *ayrı* tasarlanır, bu işte değil.) |

### Report-only → executor handoff contract (Codex T4 #3 + T6)
Reviewer'lar kod yazmaz; C/H/M `fix-required` bulguları nasıl çözülür, ölü gate kalmasın diye.
**"advisory" tek bir şey demektir: reviewer'ın chain-advance kapısını hard-bloke etmez — fix
gerekliliğini KALDIRMAZ.** Medium reviewer'da `fix-required` raporlanır; executor onu tükettiğinde
de **fix-required** (executor medium kuralı, tavan altında). İki kontrat değil, tek kontrat:
medium fix gerekli AMA reviewer-chain'i ölü-bloke etmez.
- **Yazım:** Reviewer (review/security) C/H/M bulgularını **finding-id + cluster-key** ile
  TASK.md `# Open Problems`'a + HANDOFF `## Notes For Claude`'a yazar (mevcut Adım 8 mekanizması;
  kullanıcı onaylı — carve-out gereği active-layer yazımı onay ister).
- **Tüketen executor:** Sonraki `/execute-plan-claude-codex` (veya hedefli `/simplify-claude-codex`)
  bu Open Problems item'larını girdi alır; Auto-Fix döngüsü orada (executor arketipi) işler.
- **Re-review girişi:** Fix sonrası reviewer yeniden çalıştırılır (`/review-claude-codex` resume);
  aynı cluster-key kapandıysa gate temizlenir.
- **Closure kriteri:** Reviewer chain-advance hard-block yalnız **critical/high**; bunlar
  re-review'da kapanınca chain ilerler. Medium reviewer-chain'i hard-bloke etmez ama
  **executor'da fix-required** (executor medium kuralı, tavan altında) — opsiyonel/preferred
  DEĞİL. Yani medium görünür + handoff'a yazılır + executor'da düzeltilir; sadece reviewer→
  next-reviewer geçişini durdurmaz.
- **İnsan-kapısı:** Open Problems yazımı + executor tetiği + chain ilerletme kullanıcı kararı.

## Uygulama mimarisi

Aile **byte-identical drift contract** kültürüne sahip (7-way `CODEX-CALL-PROTOCOL`,
4-way `CODEX-SCAN-SUBSTRATE`). Aynı deseni izle:

1. **Yeni ortak marker bloğu** `<!-- AUTO-FIX-REVIEW-POLICY:BEGIN ... END -->` — yalnız
   **evrensel** kuralları içerir (tetik koşulu, carve-out, severity anlamı, tur yapısı
   1–3/4+/6-tavan, **cluster ledger: finding-id + cluster-key + reopen-inherit + 2.-reopen-DUR
   + session global cap=10**, Codex çözüm-öneri formatı, low-budget). Bu ledger+cap **bloğun
   ZORUNLU parçası** — turn-1 ceiling-determinizm fix'inin backstop'u; bloğun dışında bırakılıp
   drift'ten kaçamaz. **Byte-identical** kopyalanır: execute-plan, simplify, spec, write-plan
   (4 fix-yapan komut). `<STEP_A>/<STEP_B>` benzeri **per-command binding prose** ile her komut
   bunu kendi guard adımına + medium nüansına bağlar.
2. **Reviewer-side değişikliği** (review, security-review): fix döngüsü yok → byte-identical
   blok değil, küçük **disposition + chain-gate** prose düzenlemesi. **Drift-check token
   kontrolü eklenir** (Check D ile aynı liste): review+security'de `fix-required`,
   `medium advisory`, `chain-gate`, `report-only` + 4-seviye vokabüler (`critical`/`high`/
   `medium`/`low`) mevcut; **hard-block dili yalnız `critical/high`** (token `medium advisory`
   bunu garantiler — medium hard-block İMA EDİLMEZ).
3. **finish-branch**: dokunulmaz (opsiyonel 1 satır "kapsam dışı" notu).
4. **`CODEX-CALL-PROTOCOL` + `CODEX-SCAN-SUBSTRATE` blokları DEĞİŞMEZ** — bu politika
   marker DIŞINDA. Check A/B/C tetiklenmez.

### Kritik dosyalar
- `~/.claude/commands/{execute-plan,simplify,spec,write-plan,review,security-review}-claude-codex.md`
  (6 dosya; repo-DIŞI deliverable). `finish-branch-claude-codex.md` opsiyonel 1-satır not.
- `~/.claude/command-backups/<cmd>.md.bak-<TS>` — her düzenlemeden önce yedek.
- `docs/tools/claude-codex-drift-check.sh` — **yeni Check D**: AUTO-FIX-REVIEW-POLICY bloğu
  4 komutta byte-identical (`check_expected_blocks` + `check_unexpected_markers` +
  `check_tokens` yeniden kullan; `PROTO_EXPECTED` desenini taklit et). **Tripwire token'lar
  backstop'u zorunlu kılar:** `claude-confirmed`, `cluster-key`, `finding-id`,
  `global cap`, `reopen`, `6-tavan` (4 komutta mevcut olmalı — yoksa backstop atlanmış demektir).
  **+ reviewer token check** (review+security, architecture #2 ile AYNI liste): `fix-required`,
  `medium advisory`, `chain-gate`, `report-only` + 4-seviye vokabüler (`critical`/`high`/
  `medium`/`low`) — `medium advisory` token'ı medium hard-block'u İMA ETMEYEN dili garantiler.
- `docs/specs/2026-06-03-auto-fix-review-policy.md` — bu spec.
- `docs/active/<slug>/TASK.md` + `HANDOFF.md` — yalnız manuel task tracking; Auto-Fix Policy
  bu dosyalara otomatik mutation YAPMAZ.

## Reddedilen alternatifler

- **Medium her yerde tavansız fix-required (Codex T1 önerisi):** Reddedildi → spec/write-plan
  tasarım dokümanı; oradaki medium çoğu zaman yargı/tradeoff bulgusu, kod bug'ı değil.
  Tavansız oto-çözüm = model, kullanıcının tasarım kararını gasp eder. Tür-bazlı medium +
  iteration-limit escape ile çözüldü (Claude T1 pushback → Codex T2 onayı).
- **Hiç tavan yok ("kapanana kadar dön"):** Reddedildi → oscillation/non-convergence +
  sessiz Codex maliyeti. 6-tur tavanı + kullanıcı raporu eklendi (Claude pushback → Codex
  T3 onayı). cwd-secret-hardening (14 turlu pişmanlık) dersinin doğrudan uygulaması.
- **review/security'ye kod-yazan fix loop ekle:** Reddedildi → pinned-worktree +
  docs-only-commit invariant'ını bozar. Reviewer report-only kalır; yalnız vocab + chain-gate.
- **Override'ı 6-tur sonrası sıradan seçenek yap:** Reddedildi → override ağır karar;
  yalnız mevcut explicit override kapısından geçer (Codex T3).

## Kapsam dışı (out-of-scope)
- finish-branch'e severity politikası enjekte etmek.
- review/security'nin kod yazması.
- **Heuristik/semantik** oscillation tespiti (bulguların anlamca benzerliğini ölçme) —
  ilk sürümde değil. (Deterministik **reopen-counting** — aynı cluster-key'in yeniden açılması
  — IN: cluster ledger'da var; bu heuristik değil, key-eşitliği.)
- State/lifecycle mutation'larının otomatikleşmesi (carve-out gereği).

## Verification
1. **Byte-identical:** `claude-codex-drift-check.sh` → Check A/B/C hâlâ PASS + yeni Check D
   PASS (4 komutta cmp-eşit, beklenmeyen marker yok, tripwire token'lar mevcut; reviewer
   token check). Re-runnable + byte-for-byte cmp (normalize toleransı yok).
2. **Smoke (load+parse):** Her düzenlenen komut Markdown parse oluyor, frontmatter bozulmadı.
3. **Senaryo yürüyüşü (prose trace, her komut için):** C/H/M claude-confirmed → onaysız fix
   → re-review; Claude doğrulamayan → fix yok, ledger needs-human; 6 tur → DUR + rapor;
   low 4. tur → audit-ignore; global cap=10 → DUR; carve-out: **push/state-mutation** hâlâ
   onay (executor local commit mevcut cadence); spec/write-plan tradeoff-medium →
   iteration-limit, teknik-medium → fix-required; review/security kod yazmıyor,
   vocab=fix-required + **chain-gate hard-block C/H'de; medium advisory + handoff/Open Problems**.
4. **finish-branch dokunulmadı** (severity sözlüğü yok).

## Karar geçmişi (Claude+Codex convergence)
- **T1 (Codex sentez):** carve-out + single-source gate + Codex çözüm-öneri formatı önerdi;
  medium'u her yerde tavansız fix-required istedi.
- **T1 (Claude pushback):** sert tavan + medium tür-bazlı (spec/write-plan istisnası).
- **T2 (Codex):** sayaç finding-cluster bazlı olmalı; spec/write-plan medium sınıflandırması
  rapora yazılmalı; reviewer drift token check; tavanı + tür-bazlı medium'u onayladı.
- **T3 (Codex):** terim `claude-confirmed Codex finding` (both-agree alt tür); carve-out
  ifadesi "review-bulgusu düzeltme döngüsü"; override yalnız explicit kapıdan. Onay verdi.
- **T4 (Codex, bu spec üzerinde adversarial review):** 3 high + 1 medium — (1) execute-plan
  commit carve-out çelişkisi → commit nüansı eklendi (executor task-başı commit'ler, push
  gate); (2) per-cluster tavan deterministik değil → cluster ledger (finding-id/cluster-key/
  reopen-inherit) + session global cap=10 eklendi; (3) reviewer chain-gate ölü-gate riski →
  handoff contract + hard-block eşiği critical/high (medium advisory); (4) medium kriteri yok
  → technical/tradeoff testleri + örnek + default=tradeoff eklendi. Hepsi claude-confirmed,
  Auto-Fix Policy ile onaysız düzeltildi (iter=1).
