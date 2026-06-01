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
- **Secret-scan pattern listesi eksik (CODEX-CALL-PROTOCOL preflight, canonical blok) — RESOLVED (2026-06-01, closure sonrası aile-hardening).** Önce ertelenmişti; aynı gün kullanıcı onayıyla 5-way fix uygulandı. Genişletilen pattern: `.env*`, `id_rsa`/`id_*` (SSH), `*.p12`/`*.pfx`/`*.jks`, `*service-account*.json`/`*creds*.json`, `.pgpass`/`.netrc`/`.git-credentials`/`.npmrc`, `.aws/` **+ açık-uçlu kural** ("liste örnek — sır görünen HERHANGİ dosya dahil"). Canonical `spec-claude-codex` blok edit → mekanik 5-way propagation. Doğrulama: Check A 5-way md5 yeni eşit değer `c7b5976c...` (66→68 satır), Check B 8 token korundu, BEGIN/END=1×5. **Aktivasyon: Claude Code restart** (komut dosyaları repo-dışı). Vault Invariant #12 güncellendi.
  Mevcut liste: `.env`, `*.key`, `*.pem`, `credentials*`, `secrets/`. Yakalanmayanlar: `.env.local`/`.env.production`, `id_rsa`/`id_ed25519` (SSH, uzantısız), `*.json` GCP service-account, `*.p12`/`*.pfx`/`*.jks`, `.npmrc`/`.pgpass`/`.netrc`/`.git-credentials`, `.aws/credentials`.
  Hafifletici: (a) warning-only preflight, hard-block değil; (b) sır prompt'a gömülmüyor — Codex `--cwd` ile Read edebilir ama prompt'a eklenmiyor; (c) Codex read-only sandbox.
  **Scope notu (İlke 6 blast-radius):** Bu blok **canonical, 5 komutta byte-identical** (spec/write-plan/execute/simplify/review). Düzeltmek = 5-way mekanik propagation + Check A re-run. **Pre-existing** (bu task'tan önce yazıldı), bu review-task'a özgü değil — aile-geneli defense-in-depth. Otomatik geniş düzeltme başlatılmadı; kullanıcı kararı: (a) şimdi 5-way fix, (b) ayrı aile-hardening pass'e ertele.

## Düşük
- **Pinli worktree committed secret'leri Codex'e açar (Adım 3, komut:209).** Worktree `HEAD_SHA`'da → repo'ya commit edilmiş sır (varsa) `--cwd $REVIEW_WT` ile Codex Read erişiminde. Kasıtlı tasarım (committed-only review); secret-scan preflight kapsamaya çalışıyor ama yukarıdaki Orta pattern-eksikliği burada da geçerli. Dosyada hardcoded token/key YOK (doğrulandı). → Orta ile aynı kök; onunla birlikte ele alınır.
- **`$SCOPE` tırnaksız kullanımı (Adım 4b, komut:270-271) — sorun yok (doğrulandı).** `SCOPE="--base $BASE_SHA"`; `BASE_SHA` = `git rev-parse --verify` çıktısı (temiz 40-hex, kullanıcı-türevi değil). Tırnaksızlık `--base`/`<sha>` word-split için kasıtlı+gerekli. Injection yüzeyi yok.

## Kapatılan / False Positive
- yok (Yüksek bu oturum fix'lendi; Orta+ilgili Düşük karar bekliyor; `$SCOPE` Düşük zaten sorun-değil olarak doğrulandı)

## Sonuç
- 🔴 0, 🟠 0 (1 bulundu → FIXED), 🟡 1 (→ RESOLVED, closure sonrası 5-way fix), 🟢 1 (Orta ile aynı kök → o da kapandı) + 1 sorun-değil. **Açık bulgu: 0.**
- Prompt-injection savunması: sağlam (VERİ-değil-talimat notu her iki hakem prompt'unda + CODEX-CALL-PROTOCOL'de; read-only sandbox + verbatim + disposition ledger + kullanıcı-onaylı commit katmanları)
- Path traversal: kapalı (SLUG sanitize `[a-z0-9-]`, `..` segment imkansız — canlı test)
- Deploy/closure engeli: yok (Yüksek kapandı). Orta defense-in-depth, bloke değil.
