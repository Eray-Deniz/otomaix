---
title: /write-plan-claude-codex komutu — implementation planı
status: plan-approved
date: 2026-05-25
source_spec: docs/specs/2026-05-25-write-plan-claude-codex-command.md
source_spec_unapproved_override: false
noisy_review_override: false
codex_plan_review_status: approved
codex_plan_review_iterations: 1
codex_plan_targeted_fixes: 1
codex_plan_review_log: docs/reviews/codex/2026-05-25-write-plan-claude-codex-command-plan.md
---

# Implementation Planı — `/write-plan-claude-codex`

> **Bootstrap notu:** Bu, spec Bölüm 11'deki bootstrap planıdır. Doc/komut işi olduğu
> için klasik TDD (test-önce) uygulanmaz; her task'ın "doğrulama"sı bir **shell komutu +
> beklenen çıktı**dır (grep/diff/awk). Bu plan `plan-approved` olana kadar Task 4
> (stub'a çevirme) **çalıştırılmaz** (spec Bölüm 11.3).

## Önkoşullar

- Komut dosyaları `~/.claude/commands/` altında (otomaix repo'su DIŞINDA, global).
- Yeni komut restart sonrası yüklenir (slash command'lar başlangıçta taranır).
- Spec onaylı: `spec-approved` + `approved-by-iteration-limit`.

---

## Task 0: Canonical normalizasyon — `spec-claude-codex.md`'ye CODEX-CALL-PROTOCOL marker'ları

**Neden önce:** Yeni komutun drift Check A'sı, canonical'ın (`spec-claude-codex.md`)
marker'lı bloğuna diff atar. Marker'lar yoksa check çalışmaz (spec Bölüm 2, madde 0).

**Dosya:** `~/.claude/commands/spec-claude-codex.md`

**Adımlar:**
0. **Backup (rollback için ZORUNLU — Codex Bulgu 1):**
   `cp ~/.claude/commands/spec-claude-codex.md /tmp/spec-claude-codex.md.bak`
1. "Codex Çağrı Protokolü" bölümündeki **operasyonel çekirdeği** belirle: (a) Preflight
   bash bloğu, (b) "2. Çağrı (foreground + dış timeout)" bash bloğu, (c) "3. Degradation"
   3-yollu liste. Bu üçü iki komutta birebir aynı olacak parça.
2. Çekirdeğin başına `<!-- CODEX-CALL-PROTOCOL:BEGIN (canonical: spec-claude-codex; biri değişirse diğeri de) -->`,
   sonuna `<!-- CODEX-CALL-PROTOCOL:END -->` ekle.
3. Blok **içindeki** komuta-özel referansları placeholder'a çevir:
   - `<CALL>` yorum satırındaki "task --fresh (Adım 2)" / "adversarial-review $SCOPE (Adım 6)"
     örneklerini `<CALL>` (`<STEP_A>`) / `<CALL>` (`<STEP_B>`) placeholder'larına genelle.
4. Blok **dışına** (hemen üstüne) bir **binding tablosu** ekle:
   > Binding (spec-claude-codex): `<STEP_A>`=Adım 2 (`<CALL>`=task --fresh) · `<STEP_B>`=Adım 6 (`<CALL>`=adversarial-review $SCOPE)
5. Bölümün geri kalan prose'unu (degradation downstream'in Adım 3/7'ye referansı vs.)
   blok DIŞINDA bırak — bunlar komuta özel.

**Doğrulama (behavior-preservation + rollback — Codex Bulgu 1):**
```bash
F=~/.claude/commands/spec-claude-codex.md
# (a) tam olarak BİR marker blok
[ "$(grep -c 'CODEX-CALL-PROTOCOL:BEGIN' $F)" = 1 ] && [ "$(grep -c 'CODEX-CALL-PROTOCOL:END' $F)" = 1 ] && echo "OK: tek blok"
# (b) blok boş değil + token'lar yerinde
awk '/CODEX-CALL-PROTOCOL:BEGIN/{f=1} f{print} /CODEX-CALL-PROTOCOL:END/{f=0}' $F | tee /tmp/canon_block.txt | wc -l   # >0
for t in "codex-companion.mjs" "git rev-parse" "AGENTS.md" "timeout 480s" "exit 124"; do grep -q "$t" /tmp/canon_block.txt && echo "OK: $t" || echo "EKSİK: $t"; done
# (c) degradation 3 seçeneği korunmuş (blok içinde veya hemen sonrası)
for d in "Claude-only" "Tekrar dene" "durdur"; do grep -qi "$d" $F && echo "OK: $d" || echo "EKSİK: $d"; done
# (d) semantik korunmuş: binding tablosu Adım 2 + Adım 6, task --fresh + adversarial-review hâlâ var
grep -q "Adım 2" $F && grep -q "Adım 6" $F && echo "OK: step refs"
grep -q "task --fresh" $F && grep -q "adversarial-review" $F && echo "OK: çağrı türleri"
```
**Rollback:** Yukarıdakilerden biri EKSİK/FAIL ise:
`cp /tmp/spec-claude-codex.md.bak ~/.claude/commands/spec-claude-codex.md` (canonical'ı geri yükle), düzelt, tekrar dene.

**Commit noktası:** `docs(spec-claude-codex): add CODEX-CALL-PROTOCOL markers for drift-check`
(Not: bu dosya global `~/.claude/commands/` altında, otomaix repo'suna girmez — commit
sadece repo dosyaları için; global komut değişiklikleri repo dışı, ayrı not düşülür.)

---

## Task 1: `write-plan-claude-codex.md` komut dosyasını yaz

**Dosya (yeni):** `~/.claude/commands/write-plan-claude-codex.md`

**İçerik (spec'ten birebir):**
1. Frontmatter: `description` (çift-perspektif plan üretimi), `argument-hint: <SPEC_PATH>`.
2. **Görev** + **Akış Genel Bakış (0-19)** (spec Bölüm 3).
3. **Binding tablosu** (bu komut): `<STEP_A>`=Adım 6 (task --fresh) · `<STEP_B>`=Adım 12 (adversarial-review $SCOPE).
4. **CODEX-CALL-PROTOCOL bloğu**: Task 0'da canonical'a yazılan blokla **birebir aynı**
   (kopyala — `/tmp/canon_block.txt`'ten).
5. Adım 0-19 detayları (spec Bölüm 3 "Adım detayları" + Bölüm 4/6 davranışları).
6. State machine + frontmatter şeması (spec Bölüm 5): izinli/yasak çiftler, sayaç, resume
   discovery (legacy-önce → pair-validation → sınıflandır).
7. Consistency Checklist (spec Bölüm 7) — drift Check A/B maddesi dahil.
8. Sözleşme Notları (spec Bölüm 10) + drift enforcement (Bölüm 2) + bootstrap notu (Bölüm 11).
9. Overkill (Adım 4): artefakt üretmeden çıkış önerisi (deprecated /write-plan'a yönlendirme YOK).

**Doğrulama:**
```bash
test -f ~/.claude/commands/write-plan-claude-codex.md && echo "VAR"
grep -c "CODEX-CALL-PROTOCOL:BEGIN\|CODEX-CALL-PROTOCOL:END" ~/.claude/commands/write-plan-claude-codex.md
# beklenen: 2 (begin+end)
grep -c "not-run" ~/.claude/commands/write-plan-claude-codex.md
# beklenen: 0 (lightweight kaldırıldı)
```

**Commit noktası:** `feat(commands): add /write-plan-claude-codex` (global komut — repo dışı not).

---

## Task 2: Drift-check doğrulaması (Check A + Check B)

**Test (TDD analoğu — bu geçmeden Task 3'e geçme):**
```bash
# Check A — directional drift (diff=0)
awk '/CODEX-CALL-PROTOCOL:BEGIN/{f=1} f{print} /CODEX-CALL-PROTOCOL:END/{f=0}' ~/.claude/commands/spec-claude-codex.md > /tmp/a.txt
awk '/CODEX-CALL-PROTOCOL:BEGIN/{f=1} f{print} /CODEX-CALL-PROTOCOL:END/{f=0}' ~/.claude/commands/write-plan-claude-codex.md > /tmp/b.txt
diff /tmp/a.txt /tmp/b.txt && echo "CHECK A PASS (diff=0)"
# Check B — token tripwire (token'lar + spec'in istediği 3 degradation seçeneği — Codex Bulgu 2)
for t in "codex-companion.mjs" "git rev-parse" "AGENTS.md" "timeout 480s" "exit 124"; do
  grep -q "$t" /tmp/b.txt && echo "OK: $t" || echo "EKSİK: $t"
done
for d in "Claude-only" "Tekrar dene" "durdur"; do
  grep -qi "$d" /tmp/b.txt && echo "OK degradation: $d" || echo "EKSİK degradation: $d"
done
```
**Beklenen:** "CHECK A PASS" + tüm token + 3 degradation seçeneği "OK". Herhangi biri EKSİK
veya diff varsa Task 1'e dön, bloğu düzelt (degradation seçenekleri de byte-identical blokta olmalı).

---

## Task 3: Occurrence-level `/write-plan` sweep (7 canlı yüzey)

**Önce re-grep (spec Bölüm 8 — satır numaraları drift eder, taze al):**
```bash
grep -rn "/write-plan\b" ~/.claude/commands/ ~/.claude/CLAUDE.md /root/otomaix/CLAUDE.md \
  /root/otomaix-brain/cross-project/infrastructure/claude-code-workflow.md
```

**Her occurrence için sınıflandır + uygula (spec Bölüm 8 tablosu):**
- `live` → `/write-plan-claude-codex`'e çevir:
  - `spec-claude-codex.md` (desc, "Final rapor", "/write-plan'a ait", "Sonraki adım")
  - `brainstorm.md` (3 yer), `handoff.md` (1), `plan-claude-codex.md` (1)
  - `~/.claude/CLAUDE.md` (komut listesi, diyagram, path, "/brainstorm → /write-plan")
  - `/root/otomaix/CLAUDE.md` ("/write-plan sonu → TASK+HANDOFF")
  - vault `claude-code-workflow.md` (~6, **Claude yazar**)
- `example` → **dokunma:** `spec-claude-codex.md`'deki "otomatik write-plan önerisi" (skill zinciri),
  `sync-agents-md.md:exclude-list`, vault `codex-entegrasyonu.md:exclude-list`
- `dated` → **dokunma:** tarihli docs/specs|plans|reviews, vault decisions/2026-05-19

**Doğrulama (occurrence-level — Codex Bulgu 3):** Çıplak `/write-plan`'ı (yani
`-claude-codex` ile DEVAM ETMEYEN) PCRE negative-lookahead ile yakala; satır filtrelemesi
YOK (aynı satırda yeni komut olsa bile çıplak ref'i görür):
```bash
# Temiz form (eval/iç-içe tırnak YOK; $HOME — tilde quote içinde expand etmez):
grep -rnoP '/write-plan(?!-claude-codex)\b' \
  "$HOME/.claude/commands/spec-claude-codex.md" \
  "$HOME/.claude/commands/brainstorm.md" \
  "$HOME/.claude/commands/handoff.md" \
  "$HOME/.claude/commands/plan-claude-codex.md" \
  "$HOME/.claude/CLAUDE.md" \
  /root/otomaix/CLAUDE.md \
  /root/otomaix-brain/cross-project/infrastructure/claude-code-workflow.md
# beklenen: BOŞ. (live yüzeylerde çıplak /write-plan kalmadı.)
# Not: spec-claude-codex'teki "write-plan önerisi" (skill, slash YOK) zaten /write-plan'a uymaz.
# example dosyalar (sync-agents-md, codex-entegrasyonu) ve dated dosyalar bu listede DEĞİL → kasıtlı korunur.
```
**Kanıt (spec acceptance):** her tutulan `/write-plan` occurrence'ı için sınıf (live/example/
dated/stub) + gerekçe, yukarıdaki re-grep çıktısına dayanarak commit mesajında/raporda belgelenir.

**Commit noktası:** repo dosyaları (`/root/otomaix/CLAUDE.md`) → `docs: route /write-plan refs to /write-plan-claude-codex`.
Vault → ayrı (vault repo'su); global komutlar → repo dışı not.

---

## Task 4: `write-plan.md`'yi deprecated stub'a çevir (SADECE plan-approved sonrası)

> **Gate (spec Bölüm 11.3):** Bu task yalnız bu plan `plan-approved` olduktan sonra çalışır.

**Dosya:** `~/.claude/commands/write-plan.md` → tüm içerik:
```markdown
---
description: "[DEPRECATED] use /write-plan-claude-codex"
---
## Deprecated
Bu komut write-plan-claude-codex olarak yeniden adlandırıldı.
Yeni kullanım: /write-plan-claude-codex <SPEC_PATH>
Active task yaratımı artık yeni komutun sorumluluğunda. Plan final olunca: /execute-plan <PLAN_PATH>
Eski ad referans bütünlüğü için stub korunuyor. Silme.
```

**Doğrulama:**
```bash
grep -q "\[DEPRECATED\]" ~/.claude/commands/write-plan.md && echo "STUB OK"
grep -q "superpowers:writing-plans" ~/.claude/commands/write-plan.md && echo "HATA: hala eski içerik" || echo "eski içerik temiz"
```

---

## Task 5: Final doğrulama + closure

```bash
# 1) drift-check tekrar (Task 2)
# 2) tüm canlı /write-plan referansları temiz (Task 3 doğrulaması)
# 3) yeni komut + stub yerinde
ls ~/.claude/commands/write-plan-claude-codex.md ~/.claude/commands/write-plan.md
```

**Manuel adımlar (kullanıcıya bildir):**
- **Claude Code restart** — yeni `/write-plan-claude-codex` ancak restart sonrası görünür.
- **Vault closure (spec Q3):** `claude-code-workflow.md` güncellemesi vault repo'sunda;
  push kullanıcı onayıyla.
- **Repo commit'leri** kullanıcı onayıyla (push yok).

**Out-of-scope (spec Bölüm 9):** `/execute-plan` değişmez; template şeması değişmez;
`/spec-claude-codex` davranışı değişmez (yalnız /write-plan referansı + marker eklenir).
