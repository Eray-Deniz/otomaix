# Review: simplify-claude-codex komutu — 2026-05-31

BASE: 01f57b1 (repo docs-trail başlangıcı)
HEAD: 66abecf
Reviewer: superpowers:requesting-code-review (fresh subagent, general-purpose)

**Not:** Deliverable repo dışı (`~/.claude/commands/`). Review git-diff değil, 5 dosyanın
doğrudan okunması + drift contract'ın bağımsız ölçümü (md5/diff/grep) ile yapıldı.
Hedef dosyalar: `simplify-claude-codex.md` (ana), `simplify.md` (stub),
`spec-claude-codex.md` / `write-plan-claude-codex.md` / `execute-plan-claude-codex.md` (aynalar).

## Strengths (ölçülerek doğrulanmış)

- **Drift Check A byte-identical — reviewer'ın kendi ölçümüyle:** 4 dosyadaki canonical
  CODEX-CALL-PROTOCOL bloğu aynı md5 (`6b33f5bd191d570103b501dcef5fa4ec`), 45 satır, 3
  yönlü diff hepsi exit 0.
- **Check B 4/4 dosyada geçer:** 8 tripwire token (codex-companion.mjs, git rev-parse,
  AGENTS.md, timeout 480s, 124, 3 degradation seçeneği) hepsi blok içinde, dışına sızma yok.
- **Spec↔komut gövde sadakati exact:** 12 Adım section (1-11 + 4.5) diff = 0 satır.
- **`/simplify` sweep tam:** Çıplak `/simplify` referansı kalmadı; 7 next-step/chain/skill
  referansı `/simplify-claude-codex`'e dönmüş (canonical binding chain dahil).
- **Mirror'larda eski numeral yok:** iki/üç komut, 3-way, directional absent; write-plan +
  execute-plan Sözleşme Notları tam 4-way drift bullet taşıyor.
- **Commit-gate invariant'ta delik yok:** FIXES_APPLIED==0 gate scope/commit'ten önce;
  degradation tutarlı "commit ÜRETİLMEZ"; commit gate (tests PASS) AND (review ran:
  approved|override) gerektiriyor — review'sız/override'sız commit'e ulaşan path yok.
- **Token disiplini temiz:** stray `<candidate-id>`/`<claude-id>`/`DONT_APPLY` yok;
  canonical `<id>` + `DO_NOT_APPLY` tutarlı (12 occurrence).

## Critical

Yok. (Drift contract sağlam doğrulandı; eksik spec adımı yok; kopuk/yanıltıcı akış yok.)

## Important

1. **Çift "Kural F" etiketi + sıra dışı "Kural E"** — `simplify-claude-codex.md:314,328,338`
   - İki başlık "Kural F" etiketli (Malformed @314, Test Rewrite Scope @338); aralarında
     "Kural E" (@328). Adım 6 "Kural A-F işletildikten sonra" der → "Kural F" iki farklı
     kurala çözülüyor.
   - **Neden non-breaking:** Spec'ten (satır 305/319/329) byte-for-byte miras; Task 11.5
     diff=0 acceptance bunu tam böyle reprodüksiyonu ZORUNLU kıldı → komut onaylı spec'i
     doğru aynalıyor, implementasyon hatası değil.
   - **Fix:** Önce SPEC düzeyinde düzelt (Test Rewrite → "Kural G", E'yi F'den önceye al),
     sonra re-propagate. Sadece komutu elle düzeltme → spec'e karşı gerçek drift yaratır.
   - **Durum:** Zaten biliniyor — HANDOFF Risks `R-kuralF` (spec-refine adayı). Reviewer
     bağımsız teyit etti.

## Minor

1. **Canonical (spec-claude-codex) Sözleşme Notları'nda "Drift enforcement" bullet'ı yok** —
   diğer iki ayna (write-plan/execute) tam bullet aldı, canonical asimetrik. Plan Task 12
   Step 1 "spec-claude-codex Sözleşme Notları 'Drift enforcement' bölümü"ne edit yönlendirdi
   ama o section canonical'da hiç yoktu. Contract yine de canonical'ın binding satırında
   (line 42: `drift-check 4-way: 3 diff'in hepsi 0` + `diğer aynaları da senkronla`)
   belgeli — sadece nerede belgelendiği asimetrik. Fonksiyonel boşluk değil. **YENİ bulgu**
   (HANDOFF'ta yoktu). Fix (opsiyonel): simetri için canonical'a paralel bullet ekle.
2. **`goto step_11_no_fixes_variant` (`:408`) pseudo-code, eşleşen label yok** — Bash'te goto
   yok; LLM executor için illüstratif akış. Çevre yorumları niyeti açıklıyor, spec'ten
   verbatim miras (diff=0). Kabul edilebilir protokol nesri.
3. **Dosya 717 satır vs spec tahmini ~450-550** — defect değil; fark 45 satırlık canonical
   blok + verbatim spec-section reprodüksiyonu. Spec'in kendi "boyut kullanım kaçışı"
   kaygısı ~%40 aşıldı; not olarak.

## Sonuç

- **Verdict:** Merge'e hazır — **Evet**
- **Gerekçe:** En yüksek riskli öğe (drift contract) bağımsız ölçümle sağlam (Check A md5
  byte-identical, Check B 8/8, spec↔komut diff=0). Stub/sweep/mirror/commit-gate hepsi
  doğru. Tek Important (çift Kural F) onaylı spec'in sadık reprodüksiyonu — implementasyon
  defekti değil, spec-refine follow-up.
- **Kapatılan:** 0 (Critical yok)
- **Açık (devam):** Important #1 (R-kuralF) — spec-refine adayı, non-blocking. Minor #1 YENİ.
- **Push-back (reddedilen):** 0 — tüm bulgular ölçümle gerekçeli.

## Çözüm (2026-05-31, aynı oturum)

Kullanıcı "tüm bulguları düzelt" → review + security bulguları birlikte uygulandı:

- **Important #1 (R-kuralF):** Kural relabel E/F/G (malformed→E, test-suite→F, test-rewrite→G);
  spec doc + simplify command birebir; "Kural A-F"→"A-G"; collision çözüldü.
- **Minor #1:** spec-claude-codex Sözleşme Notları'na drift-enforcement bullet (write-plan/execute paritesi).
- Security tarafı (Yüksek #1-2, Orta #1-2): bkz. `docs/security-reviews/2026-05-31-simplify-claude-codex-command.md` Çözüm.

**Doğrulama:** Check A 4-way diff=0 (`2503b639`), Check B 8/8, body mirror diff=0, R-kuralF A-F=0.
DRIFT CONTRACT: OK. Komut dosyaları repo-dışı.

## Codex Re-Review (post-hardening, 2026-05-31)

Kullanıcı hardening pass sonrası Codex'e ayrı bir review yaptırdı (Codex `2503b639` halini gördü).
3 yeni bulgu — **üçü de gerçek koda karşı doğrulandı: geçerli (haklı), hepsi düzeltildi:**

- **#1 (Codex High → kalibrasyon Medium-High) — dar scope refactor commit'ine alakasız dirty sızması:**
  Final review koşulsuz `--scope working-tree`, commit gate hangi dosyanın stage edileceğini
  belirtmiyordu → dar-arg + pre-existing dirty senaryosunda alakasız değişiklik `refactor:`
  commit'ine bundle olabilirdi. **Fix (A — FIXED_FILES takibi):** Adım 7 her fix sonrası
  `<FIXED_FILES>` set'i (mekanik test-update dahil); Adım 9 review working-tree kalır ama prompt'a
  `<FIXED_FILES>`+`<INITIAL_DIRTY_FILE_COUNT>` açık (Codex dirty-leak kontrol eder); Adım 11 commit
  **yalnız** `git add -- <FIXED_FILES>` (`git add -A`/`. ` YASAK); rapor "Committed files" vs
  "Pre-existing dirty" ayrık. Commit kapsamı artık deterministik.
- **#2 (Medium) — `<SCOPE_SLUG>` operasyonel kullanımdan önce tanımlı değil:** türetme Impl Notes'ta
  gömülüydü, Adım 4.5 (slugify) ondan önce çalışıyordu → boş/yanlış slug riski (benim Orta#1 fix'imin
  açığa çıkardığı boşluk). **Fix:** türetme + slugify **Adım 1'e** taşındı (scope kararıyla aynı anda,
  boş→`scope` fallback); Adım 4.5 sadece kullanır; Impl Notes Adım 1'e yönlendirir.
- **#3 (Low) — B2 şablonu imkansız "Final tests: FAIL":** B2 = "review ran" (Adım 8 PASS gerektirir);
  FAIL Adım 9'a ulaşmaz. **Fix:** B2'den FAIL seçeneği kaldırıldı (B1 ile tutarlı).

**Doğrulama (taze):** Check A canonical 4-way diff=0 (dokunulmadı), bare `git add -A`/`git add .`
gerçek komut YOK (yalnız YASAK referansı), SCOPE_SLUG türetme Adım 1 (RAW_SLUG), B2 FAIL yok,
FIXED_FILES spec↔command 8=8, **body mirror tüm edit section'larda diff=0** (Adım 1/7/9 + Şablonlar).
Hepsi simplify-specific — canonical bloğa dokunmadı.
