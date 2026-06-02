---
title: claude-codex ailesi — Codex --cwd untracked-secret exposure hardening (CODEX-SCAN-SUBSTRATE / sanitized-fetch-clone)
status: draft
date: 2026-06-02
tags: [security, claude-codex, codex, drift-contract, scan-substrate]
codex_review_status: pending
codex_review_iterations: 3
codex_targeted_fixes: 4
unresolved_high_severity_override: false
codex_review_log: docs/reviews/codex/2026-06-02-claude-codex-cwd-secret-hardening.md
---

# Özet

claude-codex ailesinde **4 komut** — `spec-claude-codex`, `write-plan-claude-codex`,
`execute-plan-claude-codex`, `simplify-claude-codex` — Codex companion'ını `--cwd "$PROJECT_ROOT"`
(canlı repo kökü) ile çağırıyor → harici modele (Codex) working-tree'deki **gitignored/untracked
secret'lara** (örn. `apps/social/backend/.env`) Read-tool erişimi. Tek mevcut azaltma warning-based
preflight — `--cwd` prompt'tan bağımsız olduğu için gerçek kapatma değil.

Bu spec riski **tek substrat** ile kapatır: **sanitized fetch clone** (`CODEX-SCAN-SUBSTRATE`). Temp
dizinde boş repo açılır, canlı repo'dan **yalnız gerekli objeler** (current HEAD + base/default ref)
fetch edilir, sonra **sanitize** edilir (remote kaldır, `.git/logs` sil, reflog kapat). Sonuç: Codex'in
`--cwd`'si gördüğü dizinde **`.env` yok, stash yok, diğer-branch yok, config-credential yok, reflog
yok**; ama ref/history korunduğu için companion'ın `--base`/auto review'ı çalışır. Çağrının güncel
uncommitted artefakta ihtiyacı varsa (`REQUIRED_CURRENT_FILES`) **index-preserving overlay** uygulanır
(staged/unstaged/untracked ayrımı korunur).

> **Tasarım evrimi (Codex adversarial review + ampirik doğrulama):**
> - **Iter 0 (sentetik working-tree):** Turn 1 critical — execute-plan `--base`'i kırdı.
> - **Iter 1 (iki substrat):** Turn 4 high — sentetik clean spec/write-plan `--base`/auto'yu da kırdı.
> - **Iter 2 (tek worktree+overlay):** Turn 5 high — paylaşılan `.git` stash/config/secret-ref kanalı açtı.
> - **Iter 3 (sanitized fetch clone) — BU SÜRÜM:** Codex **ayrı oturumda gerçek companion git-context'ine
>   karşı çalıştırarak** doğruladı. Worktree ampirik olarak yapısal-zayıf çıktı (credential/stash/secret-ref
>   worktree'den okundu). Sanitized fetch clone: `--base`/auto çalışıyor + `.env`/stash/secret-branch/credential
>   yok. **Mekanizma artık prose-çıkarım değil, çalıştırılmış kanıt.** (OP-1/2/3 çözüldü; OP-4 = fail-closed
>   harness implementasyon öncesi açık.)

Keşif: `finish-branch-claude-codex` security review (2026-06-02), bulgu **S-1**
(`docs/security-reviews/2026-06-02-finish-branch-claude-codex.md`). Codex yakaladı, Claude kaçırdı.

# Problem (S-1)

- **Kök neden (süreç-içkin):** canonical CODEX-CALL-PROTOCOL template'i `--cwd "$PROJECT_ROOT"` kullanıyor
  (spec-claude-codex.md satır 86 vb.); `PROJECT_ROOT` satır 54'te `git rev-parse --show-toplevel` ile canlı
  köke set ediliyor. Bu 4 komut override etmiyor.
- **Etki:** Codex `--cwd` ile canlı working-tree'deki her dosyaya Read-tool erişimi. Bu repoda
  `apps/social/backend/.env` mevcut + gitignored/untracked → **gerçek leak.**
- **Birincil vektör (doğrulanmış):** Companion gitignored `.env`'i auto-inline ETMİYOR
  (`collectWorkingTreeContext` → `ls-files --others --exclude-standard`); birincil vektör Codex'in `--cwd`
  altında `.env`'i **kendi Read tool'uyla autonom okuması.** Substrat bunu kapatır: `.env` substrat dizininde yok.

# Kapsam

**Dahil (4 komut — hepsi tek `CODEX-SCAN-SUBSTRATE`'i kullanır):**

| Komut | Codex çağrıları | Substrat girdileri |
|---|---|---|
| `spec-claude-codex` | Adım 2 (`task --fresh`), Adım 6 (`adversarial-review`) | REQUIRED_CURRENT_FILES=SPEC_PATH; Adım 6 dirty→working-tree, clean→base |
| `write-plan-claude-codex` | ön-analiz (`task --fresh`, current SPEC_PATH okur), plan review | task-fresh: SPEC_PATH; review: PLAN_PATH + base/working-tree |
| `execute-plan-claude-codex` | Adım 6 (`task --fresh`, current PLAN_PATH), Adım 8/11 (`adversarial-review --base $BASE_REF`) | task-fresh: PLAN_PATH; review: BASE_REF (committed-range) |
| `simplify-claude-codex` | pre-scan (`task --fresh`), final review | komutun okuduğu güncel dosyalar; review working-tree |

**Hariç (zaten izole — DEĞİŞTİRİLMEZ):** review (`$REVIEW_WT`), security-review (git'siz export), finish-branch (git'siz export).

# Tasarım Kararları (kilitli — Iter 3, Codex ampirik)

1. **Yön: sanitized fetch clone.** Temp boş repo + canlı repo'dan yalnız HEAD+base/default ref fetch +
   sanitize (remote kaldır, `.git/logs` sil, `core.logAllRefUpdates=false`). **worktree REDDEDİLDİ**
   (ampirik: paylaşılan `.git`'ten credential/stash/secret-ref okundu). **vanilla clone REDDEDİLDİ**
   (tüm branch/objeleri taşır). **sentetik-git REDDEDİLDİ** (ref-kaybı → `--base` kırılır). Sanitized
   fetch: hem ref-korur (--base/auto) hem secret-kanallarını kapatır.
2. **İki overlay modu (SCOPE değil; Turn7#1).** `OVERLAY_WORKTREE=1` (working-tree review) → **tüm** tracked/staged
   dirty overlay (required temizken başka dirty kaçmasın — Bulgu 2). `OVERLAY_REQUIRED_ONLY=1` (task --fresh) →
   **pathspec-limited**, yalnız `REQUIRED_CURRENT_FILES` (alakasız dirty tracked secret-scan'siz substrate'a girmez).
   base/auto review → overlay yok. Untracked her iki modda allow-list + secret-scan. (Turn 5 high#2: SCOPE'a
   bağlamak task-fresh'te stale artefakt veriyordu; Turn 7 high#1: tüm-dirty task-fresh için fazla genişti.)
3. **Overlay yöntemi: index-preserving + fail-closed producer.** Tracked staged/unstaged patch'leri **temp
   dosyaya materyalize** edilir (`git diff > $p || return 1`; pipe DEĞİL — Bulgu 3), `[ -s ]` ise `git apply`.
   Untracked: allow-list + secret-scan + `cp -P`. Staged/unstaged/untracked ayrımı korunur (ampirik 1/1/1).
4. **Base ref: call-site EXACT formda verir, substrate aynı isimle kurar.** `refs/*` aynen · `origin/main` →
   `refs/remotes/origin/main` · diğer named → `refs/heads/*` · SHA → ref yaratma, SHA aynen (Bulgu 1+4+Turn7#2).
   Auto-scope default branch'i call-site LIVE repo'da çözer (substrate re-guess etmez — Bulgu 5).
5. **Drift: tek `CODEX-SCAN-SUBSTRATE` bloğu + 4-way Check C.** CODEX-CALL-PROTOCOL'ün İÇİNE konamaz (7-way
   ortak). Marker'sız prose reddedildi.

# CODEX-SCAN-SUBSTRATE bloğu (tek canonical, 4 komut)

İşaretli, 4 komutta byte-identical, Check C ile enforce. CODEX-CALL-PROTOCOL'den **ayrı**, onun
**DIŞINDA**. Her Codex çağrısından **önce** çalışır. Fail-closed (her kritik adım `|| return 1`; global
`set -e` YOK — caller kirliliği). **Caller shell'de** çalışır (`$()` DEĞİL → `SCAN_WT_DIRS` mutasyonu
persist eder); sonucu `SCAN_ROOT` global'ine yazar.

Girdiler: `REQUIRED_CURRENT_FILES` (newline-sep; çağrının güncel ihtiyaç duyduğu dosyalar; untracked allow-list +
required-only modda tracked pathspec) · **iki overlay modundan biri:** `OVERLAY_WORKTREE=1` (working-tree review →
**tüm** tracked/staged dirty; Bulgu 2) **veya** `OVERLAY_REQUIRED_ONLY=1` (task --fresh → **yalnız** REQUIRED,
pathspec-limited; alakasız dirty girmez — Turn7#1) · `BASE_REF` (opsiyonel; `--base` review için — **call-site
EXACT formda** verir; auto'da default branch call-site'ta çözülür).

> **Reçete kaynağı:** Codex ampirik doğrulaması (2026-06-02, ayrı oturum) — gerçek companion git-context'ine
> (`resolveReviewTarget`/`collectReviewContext`/`getWorkingTreeState`) karşı çalıştırıldı. **`@execution-pin`
> işaretli satırlar** Codex'in tam spec'lemediği plumbing — implementasyon harness'ı ampirik kesinleştirir.

```bash
# CODEX-SCAN-SUBSTRATE:BEGIN (canonical: <bu spec>; biri değişirse diğerleri de — Check C 4-way)
build_scan_substrate() {
  SCAN_ROOT=""                                   # girişte temizle → fail'de stale reuse YOK
  local PROJECT_ROOT HEAD_SHA WT DEFAULT_REF r f
  PROJECT_ROOT=$(git rev-parse --show-toplevel) || return 1
  HEAD_SHA=$(git rev-parse --verify HEAD) || return 1
  WT=$(mktemp -d "${TMPDIR:-/tmp}/css.XXXXXX") || return 1
  SCAN_WT_DIRS+=("$WT")                          # caller shell'de birikir → tek EXIT trap temizler

  # 1. Boş repo + reflog kapalı (sanitize)
  git -C "$WT" init -q || return 1
  git -C "$WT" config core.logAllRefUpdates false || return 1

  # 2. Live repo'dan YALNIZ gerekli objeler: current HEAD (+ base/default ref). TÜM branch/stash/config DEĞİL.
  #    `git fetch <path> <sha>` o commit + ancestry'sini getirir; stash/diğer-branch/config GELMEZ.
  git -C "$WT" fetch -q --no-tags "$PROJECT_ROOT" "$HEAD_SHA" || return 1
  git -C "$WT" checkout -q --detach "$HEAD_SHA" || return 1
  # base ref'i companion için kur. Call-site BASE_REF'i EXACT formda verir (named ref veya SHA); auto-scope'ta
  # call-site default branch'i LIVE repo'da resolveReviewTarget mantığıyla önceden çözer → substrate RE-GUESS ETMEZ
  # (Bulgu 5). Companion BASE_REF'i hangi isimle alacaksa substrate'ta aynı isim resolvable olmalı (Bulgu 1).
  if [ -n "${BASE_REF:-}" ]; then
    git -C "$WT" fetch -q --no-tags "$PROJECT_ROOT" "$BASE_REF" || return 1
    if [ "$(git -C "$PROJECT_ROOT" rev-parse --verify -q "${BASE_REF}^{commit}" 2>/dev/null)" = "$BASE_REF" ]; then
      : # BASE_REF zaten SHA → obje fetch edildi, companion'a --base <sha> aynen verilir; REF YARATILMAZ (Bulgu 4)
    else
      case "$BASE_REF" in                          # named ref → EXACT namespace (Bulgu 1 + Turn7#2)
        refs/*)   git -C "$WT" update-ref "$BASE_REF"               FETCH_HEAD || return 1 ;;  # full ref aynen
        origin/*) git -C "$WT" update-ref "refs/remotes/$BASE_REF"  FETCH_HEAD || return 1 ;;
        *)        git -C "$WT" update-ref "refs/heads/$BASE_REF"    FETCH_HEAD || return 1 ;;
      esac
    fi
  fi  # @execution-pin: SHA-vs-ref tespiti + namespace eşleme harness'ta kesinleşir

  # 3. Sanitize: remote + reflog kalıntısı yok (S-1: credential/reflog/origin.url kanalı kapanır)
  git -C "$WT" remote remove origin 2>/dev/null || true     # fetch-from-path remote yaratmaz; defensive
  rm -rf -- "$WT/.git/logs" || return 1

  # 4. Overlay — İKİ MOD (Turn7#1): OVERLAY_WORKTREE=1 → TÜM tracked dirty (YALNIZ adversarial-review --scope working-tree);
  #    OVERLAY_REQUIRED_ONLY=1 → pathspec-limited, YALNIZ REQUIRED_CURRENT_FILES (task --fresh; alakasız dirty substrate'a girmez).
  if [ -n "${OVERLAY_WORKTREE:-}" ] || [ -n "${OVERLAY_REQUIRED_ONLY:-}" ]; then
    local -a PATHSPEC=()                          # worktree → boş (tümü); required-only → REQUIRED dosyaları
    if [ -z "${OVERLAY_WORKTREE:-}" ]; then
      while IFS= read -r f; do [ -n "$f" ] && PATHSPEC+=("$f"); done <<< "${REQUIRED_CURRENT_FILES:-}"
    fi
    # Tracked staged+unstaged INDEX-PRESERVING. Producer MATERYALİZE (pipe fail-closed DEĞİL — Bulgu 3): boş=no-op, hata=return 1.
    local sp up; sp=$(mktemp "${TMPDIR:-/tmp}/css-sp.XXXXXX") || return 1; SCAN_WT_DIRS+=("$sp")
    up=$(mktemp "${TMPDIR:-/tmp}/css-up.XXXXXX") || return 1; SCAN_WT_DIRS+=("$up")
    git -C "$PROJECT_ROOT" diff --cached --binary HEAD -- "${PATHSPEC[@]}" > "$sp" || return 1   # staged (worktree: tümü; required: pathspec)
    git -C "$PROJECT_ROOT" diff --binary           -- "${PATHSPEC[@]}" > "$up" || return 1       # unstaged
    if [ -s "$sp" ]; then git -C "$WT" apply --index --whitespace=nowarn "$sp" || return 1; fi
    if [ -s "$up" ]; then git -C "$WT" apply         --whitespace=nowarn "$up" || return 1; fi
    # Untracked: YALNIZ allow-list (REQUIRED ∩ untracked-others) + içerik secret-scan + cp -P (her iki mod).
    while IFS= read -r f; do
      [ -z "$f" ] && continue
      git -C "$PROJECT_ROOT" ls-files --others --exclude-standard -- "$f" | grep -Fxq -- "$f" || continue
      _css_secret_scan "$PROJECT_ROOT/$f" || { echo "CSS: secret içerik, DIŞLANDI: $f" >&2; continue; }
      _css_copy_safe "$PROJECT_ROOT" "$WT" "$f" || return 1
    done <<< "${REQUIRED_CURRENT_FILES:-}"
    # symlink sweep (overlay sonrası $WT-dışına çözülen symlink'leri sil)
    local symlist; symlist=$(mktemp "${TMPDIR:-/tmp}/css-syml.XXXXXX") || return 1; SCAN_WT_DIRS+=("$symlist")
    find "$WT" -type l -print0 > "$symlist" || return 1
    local l tgt; while IFS= read -r -d '' l; do
      tgt=$(readlink -f -- "$l" 2>/dev/null || echo ""); case "$tgt/" in "$WT"/*) : ;; *) rm -f -- "$l" || return 1 ;; esac
    done < "$symlist"
  fi

  SCAN_ROOT="$WT"                                  # YALNIZ tüm adımlar geçince
}

_css_copy_safe() { # $1=src_root $2=dst_root $3=relpath ; symlink DEREF ETMEZ; repo-dışına çözülürse atla
  local src="$1/$3" dst="$2/$3" rp
  if [ -L "$src" ]; then rp=$(readlink -f -- "$src" 2>/dev/null || echo "")
    case "$rp/" in "$1"/*) : ;; *) echo "CSS: symlink repo-dışına, atlandı: $3" >&2; return 0 ;; esac; fi
  mkdir -p -- "$(dirname -- "$dst")" || return 1; cp -P -- "$src" "$dst" || return 1
}
_css_secret_scan() { # $1=abs path ; içerik-bazlı; eşleşirse non-zero = dışla
  ! grep -Eq -- '(BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16}|secret[_-]?key|api[_-]?key|password[[:space:]]*=|token[[:space:]]*=|postgres://[^ ]*:[^ ]*@)' "$1" 2>/dev/null
}
# CODEX-SCAN-SUBSTRATE:END
```

Çağrı tarafı (CODEX-CALL-PROTOCOL marker'ının DIŞINDA):

```bash
SCAN_WT_DIRS=(); trap 'for d in "${SCAN_WT_DIRS[@]:-}"; do [ -n "$d" ] && rm -rf -- "$d"; done' EXIT  # komut başında BİR kez
# Çağrı türüne göre (komut zaten biliyor) — overlay modlarından BİRİ:
REQUIRED_CURRENT_FILES="$SPEC_PATH"      # çağrının güncel ihtiyacı (write-plan→SPEC_PATH; execute-plan→PLAN_PATH; simplify→okunan)
OVERLAY_WORKTREE= ; OVERLAY_REQUIRED_ONLY=
case "$CALL_KIND" in
  worktree-review)  OVERLAY_WORKTREE=1 ;;        # adversarial-review --scope working-tree → TÜM dirty
  task-fresh)       OVERLAY_REQUIRED_ONLY=1 ;;   # task --fresh → yalnız REQUIRED (alakasız dirty girmez — Turn7#1)
  base-review)      : ;;                          # adversarial-review --base/auto → overlay yok, sadece committed checkout
esac
# BASE_REF: call-site companion'ın BU çağrı için kullanacağı base'i LIVE repo'da çözüp EXACT formda verir (Bulgu 1+5):
#   --base review → USER_BASE_REF (named/full ref veya SHA, aynen) · auto → live repo default branch · working-tree/task-fresh → boş
BASE_REF="${RESOLVED_BASE:-}"            # @execution-pin: call-site base-resolution (live repo'da deterministik)
if ! build_scan_substrate; then          # $() YOK → SCAN_WT_DIRS persist; fallthrough YOK
  <CODEX-CALL-PROTOCOL degradation: Claude-only / retry / abort — Codex çağrısı YAPILMAZ>
fi
# build_scan_substrate $SCAN_ROOT set etti → CODEX-CALL-PROTOCOL --cwd "$PROJECT_ROOT" burada --cwd "$SCAN_ROOT"'a override edilir.
# companion'a BASE_REF aynen geçilir (--base "$BASE_REF") → substrate'taki exact ref/SHA ile resolve eder.
```

> **Cleanup:** `SCAN_WT_DIRS` tüm temp dizinlerini biriktirir; tek EXIT trap `rm -rf` (clone'lar
> worktree değil, plain dir → `git worktree remove` gerekmez). `build_scan_substrate` caller shell'de
> (`$()` değil) → array mutasyonu persist eder.

# Call-site override (canonical blok DIŞINDA — drift contract korunur)

Her komut, kendi Codex call-site adımında (CODEX-CALL-PROTOCOL marker'ının **dışında**): substratı kur,
template'in `--cwd "$PROJECT_ROOT"`'unu **`--cwd "$SCAN_ROOT"`'a override et** (finish-branch satır 238
deseni). Canonical blok **literal metni değişmez** (`$PROJECT_ROOT` yazılı kalır) → Check A/B 7-way
(`c7b5976c`) **bozulmaz.**

# Verification (Codex ampirik — 2026-06-02)

Codex throwaway repo (base+feature commit · unstaged+staged+untracked · ignored `.env` · config credential
· 2 stash · secret branch) + gerçek companion git-context yolu ile çalıştırdı:
- **Sanitized clean clone:** `--base main` doğru diff · base'siz auto doğru diff · `.env` yok · stash 0 ·
  secret-branch yok · `remote.origin.url` boş · `.git/logs` yok · `merge-base HEAD main` çalışıyor.
- **Sanitized dirty clone:** `--scope working-tree` dirty doğru · index-preserving overlay → 1 staged/1 unstaged/
  1 untracked korundu · `.env` içeriği yok.
- **Worktree (reddedildi):** `.env` fiziksel yok ama common gitdir'den `config` credential + `stash list=2`
  + secret-branch ref OKUNDU → yapısal zayıf.
- **Koşulmadı:** tam adversarial-review app-server/model çağrısı (git-context yolu yeterli kanıt); + OP-4 (aşağı).

# Drift Contract

- **Check A/B (mevcut, 7-way):** CODEX-CALL-PROTOCOL `c7b5976c` — değişmez.
- **Check C (yeni, 4-way):** `CODEX-SCAN-SUBSTRATE` 4 komutta byte-identical; 3 diff=0. Tripwire token'lar
  (blokta birebir geçen substring'ler): `init -q`, `fetch -q --no-tags`, `core.logAllRefUpdates false`,
  `remote remove origin`, `.git/logs`, `apply --index`, `OVERLAY_WORKTREE`, `OVERLAY_REQUIRED_ONLY`,
  `_css_copy_safe`, `cp -P`, `_css_secret_scan`, `REQUIRED_CURRENT_FILES`, `SCAN_WT_DIRS`.

# OP-4 — Açık (fail-closed harness, implementasyon öncesi)

Codex'in ampirik turu OP-1/2/3'ü + T7-T10'u doğruladı; **T1-T6 fail-closed/failure-injection KOŞULMADI.**
Implementasyon (execute-plan TDD) öncesi ayrı harness ile:
| # | Test |
|---|---|
| T1 | overlay NUL/path-with-space; index-preserving M/D/A/R/staged/unstaged ayrımı |
| T2 | producer/fetch/apply hatası → `build_scan_substrate` non-zero, `SCAN_ROOT` boş |
| T3 | stale guard: 1. OK + 2. fail → `SCAN_ROOT` boş, eski reuse yok |
| T4 | çoklu çağrı sonrası EXIT → `/tmp/css.*` kalmaz |
| T5 | symlink exfil `notes.txt -> .env` → `cp -P` + sweep → secret yok |
| T6 | allow-list secret-içerik → `_css_secret_scan` dışlar |
| T7-T10 | (Codex koştu) base/auto/working-tree diff doğruluğu + secret yokluğu ✓ |
| T11 | task --fresh (OVERLAY_REQUIRED_ONLY): PLAN_PATH uncommitted + alakasız `secrets.txt` tracked dirty → substrate'ta PLAN_PATH VAR, `secrets.txt` YOK (Turn7#1) |
| T12 | base-ref namespace: `origin/main` · `refs/remotes/origin/main` · `main` · `<sha>` → hepsi resolve; SHA'da ref yaratılmaz (Turn7#2) |

`@execution-pin` satırları (default-ref tespiti, fetch/update-ref ref-plumbing, `git apply` flag'leri) da
harness'ta ampirik kesinleştirilir.

# Out of Scope

- Diğer 3 izole komutun substratını değiştirmek.
- CODEX-CALL-PROTOCOL canonical bloğunu değiştirmek (override prose ile).
- Committed secret: fetch HEAD ancestry'sini getirir → committed secret (varsa) substratta olur (best-effort,
  committed-secret caveat). Bu repoda yok (S-1 ledger temiz).

# Riskler

- **`@execution-pin` plumbing:** default-ref tespiti + fetch/update-ref + `git apply` edge'leri Codex'çe tam
  spec'lenmedi; harness kesinleştirmeli (yoksa auto-scope veya apply kırılabilir).
- **İçerik secret-scan tamlığı:** pattern listesi örnek; allow-list birincil kapı.
- **Performans:** per-call `git init`+fetch; execute-plan çok-çağrılı → birikir; gözlemle.
- **Yeni drift yüzeyi:** 4-way Check C drift-check tooling'e eklenmeli.
