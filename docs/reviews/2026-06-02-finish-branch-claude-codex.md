# Review (dual): finish-branch-claude-codex komutu — 2026-06-02

Review hedefi: `~/.claude/commands/finish-branch-claude-codex.md` (323 satır, **repo-DIŞI** command spec)
- Uyarlanmış tehdit modeli: prose-fidelity + 7-way drift contract + shell-safety + iç tutarlılık (kod-diff değil, whole-file spec review)
- git aralığı `origin/main..HEAD` = yalnız docs-audit commit (`d285183`); asıl deliverable repo-dışı → dosya doğrudan okunarak review edildi
Reviewers: fresh Claude subagent (general-purpose, code-reviewer persona) + Codex `task --fresh` (contained temp-dir cwd)
dual-review: true (claude_status: ran; codex_status: ran)
Requirement context (snapshot): docs/specs/ + docs/plans/ 2026-06-02-finish-branch-claude-codex-command.md — committed, both approved
Drift contract: VERIFIED 7/7 byte-identical (md5 `c7b5976c9513391909310883c40575c3`, 68 satır) — iki hakem de bağımsız md5 ile doğruladı [both-agree]

## Critical
_(yok)_

## High
- **Remote branch silme `HEAD_SHA`'a bağlı değil — komutun kendi pinned-target invariant'ını ihlal eder.** [single-source: codex]
  `finish-branch-claude-codex.md:266` (Adım 8 D=sil). Local discard doğru şekilde old-value-bound (`git update-ref -d refs/heads/<branch> $HEAD_SHA` — ref divergence'da abort). Ama sonraki remote silme yalnız `git push origin --delete <branch>` — lease/HEAD_SHA bağı yok. Audit sonrası remote branch diverge ettiyse (biri push'ladıysa) bu **audit-edilmemiş remote işi siler**. Satır 257 açıkça "Tüm outward/destructive op audited HEAD_SHA'yı hedefler, live ref'i DEĞİL" diyor → remote silme bu invariant'tan kaçıyor. Düzeltme uygulanabilir: `git push --force-with-lease=<branch>:$HEAD_SHA origin :refs/heads/<branch>` veya silmeden önce remote ref'i `HEAD_SHA`'a karşı taze kontrol. Pratik risk çift-onayla (D=sil + "remote varsa sor") hafiflemiş ama invariant ihlali gerçek.

## Medium
- **`BASE_SHA` / `audit_BASE` tanımsız sembol (normal-mode audit scope).** [single-source: claude]
  `:36` + `:216`. normal-mode scope `merge-base(BASE_SHA, HEAD_SHA)..HEAD_SHA` yazılı ama `BASE_SHA` komutun hiçbir yerinde türetilmiyor — Adım 1 (`:163-165`) yalnız `CUR`/`DEFAULT`/`UPSTREAM` atıyor, Adım 4 (`:192-193`) yalnız `HEAD_SHA`/`PROJECT_ROOT`. Niyet muhtemelen `merge-base($DEFAULT, $HEAD_SHA)` ya da `$UPSTREAM` tabanlı; ama symbol tanımsız → normal-mode range diff snapshot + range-containment evidence'ı underspecified. (Spec'te de aynı boşluk → fidelity korunmuş ama alttaki tanım iki yerde de eksik.)
- **Kullanıcı-girdisi detached branch adı doğrulanmıyor (`check-ref-format`).** [single-source: codex; main-Claude ile daraltıldı]
  `:261` (detached B/PR + detached D). "önce branch adı iste → `git branch <branch> $HEAD_SHA`" — kullanıcı serbest metin giriyor ama `git check-ref-format --branch` ile valide edilmeden ref oluşturma/push refspec'ine giriyor. (Normal/mainline'daki `<branch>`/`<default>` zaten git-validated mevcut isimler → düşük risk; gerçek boşluk yalnız detached kullanıcı-girdisinde + genel quoting hijyeni.)
- **Normal local merge push'u `MERGE_SHA`'a pinlenmemiş.** [single-source: codex]
  `:259` (A=merge). Merge girdisi pinli (`git merge ${HEAD_SHA} --no-ff`) ama dışa push `git push origin <default>` üretilen merge commit'ine pinli değil. mainline push (`:260`) pinli (`${HEAD_SHA}:refs/heads/<default>`) — bu tutarsız. Merge + test + onay arasında default branch'e eşzamanlı commit/hook push kapsamını genişletebilir. Düzeltme: merge sonrası `MERGE_SHA=$(git rev-parse HEAD)` yakala → `git push origin ${MERGE_SHA}:refs/heads/<default>`.
- **Degradation wording'i iç tutarsız (auto-skip vs AskUserQuestion).** [single-source: codex]
  `:214` (Adım 5.1) "Codex preflight fail (degrade) → audit atlanır → Adım 6'ya geç" **otomatik atlama** gibi okunuyor; ama canonical CODEX-CALL-PROTOCOL (`:146`) "Otomatik karar YOK — AskUserQuestion (Claude-only / retry / stop)" diyor. `:79` advisory bağlamı reconcile ediyor ama Adım 5.1 + D=sil retry (`:267`) tek kurala bağlanmamış. Net hâli: degradation → canonical AskUserQuestion; "Claude-only" = audit'siz devam; D=sil retry uyarısını ekler.

## Low
- **Codex `--cwd` override'ı sibling'lerden daha az belirgin.** [single-source: codex; main-Claude downgrade]
  Codex bunu high verdi; ama override **mevcut** — `:82` binding (`--cwd $SCAN_ROOT`), `:75`, ve asıl çağrı talimatı `:219` (`--cwd "$SCAN_ROOT"`) açıkça belirtiyor. Canonical blok template `--cwd "$PROJECT_ROOT"` taşıyor (7-way byte-identity gereği), her sibling kendi call-site'ında override ediyor. Davranışsal kırılma yok → **low (clarity)**: `review-claude-codex.md:270` gibi açık "(`$PROJECT_ROOT` değil)" callout'u eklenebilir. (Claude bu boyutu "temiz" demişti; doğrulama: override var, ama vurgu siblings'ten zayıf.)
- **mainline scope `origin/main` hardcode.** [single-source: claude]
  `:37` + `:216` literal `origin/main..HEAD`, ama Adım 1 default branch'i dinamik türetiyor (`$DEFAULT`, `:164`). default `main` değilse (master/trunk) mainline audit-scope yanlış base alır. Push tarafı doğru (`<default-branch>` kullanıyor) — yalnız audit evidence-scope satırı dinamik DEFAULT ile tutarsız.
- **Log-path placeholder'ları prose-only.** [single-source: claude]
  `:220` `<DATE>`/`<SLUG>`/`<ATTEMPT>` somut bash türetimi olmadan; slug kaynağı (active task slug? branch adı?) belirtilmemiş. Kardeşler (`security-review:260-262`) bunları bash ile türetir. Kozmetik — log yolu deterministik değil, davranışsal risk yok.

## Disposition Ledger (her ham bulgu — sessiz drop yok)
| id | source | raw sev | final sev | disposition | gerekçe |
|----|--------|---------|-----------|-------------|---------|
| X-3 remote-delete unbound | codex | high | **high** | kept | dosyada teyit edildi (`:266`); `:257` invariant'ını ihlal ediyor |
| C-1 BASE_SHA undefined | claude | medium | **medium** | kept | Adım 1/4 derive'larında BASE_SHA yok (teyit) |
| X-2 detached branch-name validation | codex | high | **medium** | downgraded | normal/mainline isimler git-validated; gerçek boşluk yalnız detached user-input → scope daraltıldı |
| X-4 merge push not pinned | codex | medium | **medium** | kept | `:259` vs `:260` tutarsızlığı teyit |
| X-5 degradation wording | codex | medium | **medium** | kept | `:214` vs canonical `:146` wording çelişkisi teyit |
| X-1 cwd override clarity | codex | high | **low** | downgraded | override `:82/:75/:219`'da mevcut; davranışsal kırılma yok → clarity |
| C-2 mainline origin/main hardcode | claude | low | **low** | kept | `:37/:216` literal vs dinamik `$DEFAULT` (`:164`) |
| C-3 log-path placeholders | claude | low | **low** | kept | `:220` prose-only, slug kaynağı belirsiz |
| drift contract md5 7/7 | both | clean | clean | kept | iki hakem bağımsız md5 → `c7b5976c` [both-agree] |
| Check B token 7/7 | both | clean | clean | kept | 8 token × 7 dosya [both-agree] |
| advisory/gate topoloji | both | clean | clean | kept | tek istisna (D=sil upgrade) dışında gate sızması yok [both-agree] |
| closure matrix korunmuş | both | clean | clean | kept | A/D full+archive, B waiting-review, C no-op [both-agree] |
| frontmatter smoke | codex | clean | clean | kept | parse OK |

## Sonuç
- Kapatılan (push-back): 0 (kullanıcı push-back'i bekleniyor)
- Açık (devam): 1 high + 4 medium + 3 low
- Hakemler-arası çelişki: **shell-safety boyutu** — Claude "critical/high temiz" dedi, Codex 3 high buldu. Çözüm: X-3 gerçek high (remote-delete), X-2 medium'a daraltıldı (detached user-input), X-1 low'a indirildi (override mevcut). Codex outward-ops'a daha derin baktı; Claude pinned-target prose'una güvenip remote-delete + merge-push edge'ini kaçırdı. Çift-hakem değeri tam burada çıktı.
- **Önemli:** Tüm bulgular CODEX-CALL-PROTOCOL marker bloğunun DIŞINDA — düzeltme drift contract'ı (byte-identity) bozmaz.
- critical = 0 → chain-advance bloke değil; ama 1 high açık (kullanıcı /security-review-claude-codex öncesi düzeltmek isteyebilir).

## Raw Claude Reviewer Output (appendix)
```
Drift contract: Check A 7/7 md5 c7b5976c9513391909310883c40575c3 (68 satır) PASS; Check B 8 token 7/7 PASS; stale N-way yok PASS.
critical: temiz — yıkıcı/dışa-dönük ops doğru pinlenmiş (merge ${HEAD_SHA}, push ${HEAD_SHA}:refs/heads, D=sil old-value-bound update-ref); -D yerine update-ref; quoted-heredoc + $SCOPE rev-parse guard canonical'dan miras. Injection/yanlış-binding yok.
high: temiz — advisory/gate ayrımı sağlam (tek istisna D=sil upgrade); iki-fazlı blocker (Adım5 facts → Adım8 reclassify) doğru; mode detection deterministik + belirsizlik→DUR; 8-adım closure matrix + Adım7→Adım8 sıra disiplini korunmuş.
medium: BASE_SHA/audit_BASE tanımsız (normal-mode scope, :36/:216) — Adım4 yalnız HEAD_SHA/PROJECT_ROOT atıyor; review-claude-codex bunu somut türetir; spec'te de aynı eksik.
low(a): mainline origin/main hardcode (:37/:216) vs dinamik DEFAULT (:164) — master/trunk'ta yanlış base.
low(b): <DATE>/<SLUG>/<ATTEMPT> log-path placeholder prose-only (:220), slug kaynağı belirsiz — kozmetik.
Temiz: prose-fidelity (tüm spec/plan kararları inmiş, kırık step-ref yok), aile-konvansiyon (binding/degradation/Codex-readonly/active-layer/vault-deferred), topoloji (detached PR sırası, branch -d vs update-ref ayrımı, worktree cleanup).
```

## Codex raw review
docs/reviews/codex/2026-06-02-review-finish-branch-claude-codex-1.md
