# Security Review: review-claude-codex komutu — 2026-06-01

Kapsam: `~/.claude/commands/review-claude-codex.md` (~518 satır, repo-DIŞI markdown slash-command) + canonical CODEX-CALL-PROTOCOL (5-way ortak blok)
Reviewer: fresh subagent (general-purpose)
Bağlam: pre-closure (claude-codex aile komut ailesi; deliverable repo-dışı, restart ile aktif)
Tehdit modeli: **uyarlanmış** — shell/command injection (gömülü bash), secret'ın harici Codex modeline sızması, prompt-injection (review edilen içerik). SaaS web kategorileri (SQL/multi-tenant/IDOR/auth/CORS/cookie/CSRF/SSRF/rate-limit/file-upload) **N/A** (markdown talimat dosyası, execution surface yok).

## Kritik
- yok

## Yüksek
- **`BASE_REF="$ARGUMENTS"` literal-substitution quote-break (Adım 1, komut:153 + spec:96) — FIXED (bu oturum).**
  `$ARGUMENTS` Claude Code tarafından komut gövdesine literal metin olarak gömülüyor. Argüman `"; echo X #` gibi çift-tırnak içerirse satır quote'tan kaçıyor ve enjekte komut `git rev-parse --verify` guard'ından (sonraki satır) ÖNCE, aynı satırda çalışıyor → guard yakalamıyor. Subagent canlı shell testiyle doğruladı. Self-inflicted (kullanıcı kendi komutuna kötücül argüman vermeli; harici saldırgan yok) → kritik değil, yüksek.
  **NOT:** bu satır bu oturumdaki `$ARG`→`$ARGUMENTS` review-fix'inin yan ürünüydü (eski `${ARG:-...}` `$ARG` tanımsız olduğu için inject etmiyordu, sadece default'a düşüyordu). Kardeş komutlar `$ARGUMENTS`'i yalnız prose'da kullanıyor → onlarda yok (blast-radius: spec:96 + komut:151 yalnız).
  **FIX:** raw `$ARGUMENTS` shell atamasından çıkarıldı; kardeş pattern'e geçildi — prose + "git ref asla `" \` $ ; | &` veya boşluk içermez → böyle argümanı gömmeden reddet (STOP)". Doğrulama: raw atama 0, Check A 5-way md5 intact (`2503b639...`), spec↔komut Adım 1 mirror diff=0.

## Orta
- **Secret-scan pattern listesi eksik (CODEX-CALL-PROTOCOL preflight, canonical blok satır ~86-89) — KARAR: ERTELENDİ (2026-06-01, kullanıcı).** → Ayrı aile-hardening pass'inde (5-way) ele alınacak. Pre-existing + aile-geneli + warning-only defense-in-depth olduğu için bu review-task closure'ını bloke etmez. **Takip:** gelecekte canonical CODEX-CALL-PROTOCOL'ü hardening eden bir task açıldığında bu bulgu girdi olmalı (genişletme önerisi aşağıda).
  Mevcut liste: `.env`, `*.key`, `*.pem`, `credentials*`, `secrets/`. Yakalanmayanlar: `.env.local`/`.env.production`, `id_rsa`/`id_ed25519` (SSH, uzantısız), `*.json` GCP service-account, `*.p12`/`*.pfx`/`*.jks`, `.npmrc`/`.pgpass`/`.netrc`/`.git-credentials`, `.aws/credentials`.
  Hafifletici: (a) warning-only preflight, hard-block değil; (b) sır prompt'a gömülmüyor — Codex `--cwd` ile Read edebilir ama prompt'a eklenmiyor; (c) Codex read-only sandbox.
  **Scope notu (İlke 6 blast-radius):** Bu blok **canonical, 5 komutta byte-identical** (spec/write-plan/execute/simplify/review). Düzeltmek = 5-way mekanik propagation + Check A re-run. **Pre-existing** (bu task'tan önce yazıldı), bu review-task'a özgü değil — aile-geneli defense-in-depth. Otomatik geniş düzeltme başlatılmadı; kullanıcı kararı: (a) şimdi 5-way fix, (b) ayrı aile-hardening pass'e ertele.

## Düşük
- **Pinli worktree committed secret'leri Codex'e açar (Adım 3, komut:209).** Worktree `HEAD_SHA`'da → repo'ya commit edilmiş sır (varsa) `--cwd $REVIEW_WT` ile Codex Read erişiminde. Kasıtlı tasarım (committed-only review); secret-scan preflight kapsamaya çalışıyor ama yukarıdaki Orta pattern-eksikliği burada da geçerli. Dosyada hardcoded token/key YOK (doğrulandı). → Orta ile aynı kök; onunla birlikte ele alınır.
- **`$SCOPE` tırnaksız kullanımı (Adım 4b, komut:270-271) — sorun yok (doğrulandı).** `SCOPE="--base $BASE_SHA"`; `BASE_SHA` = `git rev-parse --verify` çıktısı (temiz 40-hex, kullanıcı-türevi değil). Tırnaksızlık `--base`/`<sha>` word-split için kasıtlı+gerekli. Injection yüzeyi yok.

## Kapatılan / False Positive
- yok (Yüksek bu oturum fix'lendi; Orta+ilgili Düşük karar bekliyor; `$SCOPE` Düşük zaten sorun-değil olarak doğrulandı)

## Sonuç
- 🔴 0, 🟠 0 (1 bulundu → FIXED), 🟡 1 (karar bekliyor — canonical 5-way blok), 🟢 1 actionable (Orta ile aynı kök) + 1 sorun-değil
- Prompt-injection savunması: sağlam (VERİ-değil-talimat notu her iki hakem prompt'unda + CODEX-CALL-PROTOCOL'de; read-only sandbox + verbatim + disposition ledger + kullanıcı-onaylı commit katmanları)
- Path traversal: kapalı (SLUG sanitize `[a-z0-9-]`, `..` segment imkansız — canlı test)
- Deploy/closure engeli: yok (Yüksek kapandı). Orta defense-in-depth, bloke değil.
