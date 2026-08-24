# Handoff

> ⚠️ YÜRÜTME AÇIK (başlangıç: 2026-08-24 07:05) — bu anlatı oturum sonuna aittir; canlı yürütme
> durumu TASK.md "Execution State" + git defterinden okunur, çelişkide onlar esastır.

## Context
- Task: sektor-bilgi-paketi — **faz: Plan 1 YÜRÜTME AÇIK (`/execute-plan-claude-codex`), 16 task'ın 2'si bitti**
- Last updated: 2026-08-24 (altıncı oturum — execute başlangıcı, Task 1-2)
- Plan: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (`plan-approved`)
- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Dal: `feat/sektor-bilgi-paketi` (main'den ayrıldı; **upstream YOK — hiç push edilmedi**)
- Execute ham review log'u: `/root/.claude/logs/otomaix--ffc87809/2026-08-24-feat-sektor-bilgi-paketi-execute.md`

## Current State
- **Mod:** subagent-driven (her task fresh alt-oturumda; ana oturum checkpoint + tahkim).
- **Biten:** Task 1 (pytest altyapısı + atılabilir `otomaix_test` DB) · Task 2 (migration 032).
- **HEAD:** `e3efbe9`; `execute_start_ref` (`5a9d5d4`) sonrası **9 commit**, hepsi local.
- **Checkpoint:** 2 koştu, ikisi de sonunda `verdict: approve`. `cp_count: 2`,
  `last_checkpoint_ref: b2d80c5…`.
- **Ortam kurulumu (yeni oturumda TEKRAR KURMA — duruyor):**
  `apps/social/backend/.venv` içinde requirements.txt + pytest 9.1.1 + pytest-asyncio 1.4.0.
  Sistem Python'ına **dokunulmadı** (ölçüldü: asyncpg 0.31.0 / Pillow 12.2.0 yerinde).
  Komut daima `.venv/bin/python` — makinede `python` komutu YOK, `python3` sistem Python'ı.
- **Geçmiş yeniden yazıldı (Eray onaylı, 2026-08-24):** `9ed5902` commit'i `Exec-Kind: code`
  taşıyordu ama yalnız `tests/` altına dokunuyordu → türetilmiş defter MECH-FAIL veriyordu
  (Adım 11.0 kapısını ve push'u bloklardı). `red-only`'ye çevrildi, sonraki 5 commit replay
  edildi, **dosya içerikleri bayt-aynı** (`git diff backup/pre-footer-fix HEAD` boş).
  Emniyet etiketi: `backup/pre-footer-fix` (eski uç `960af6b`).

## Resume From (sıra)
1. **Task 3** — `### Task 3: Migration dağıtım gerçeği + geri alma + atomiklik ölçümü`.
   Üç iş: (a) `shared/local-deployment/migrations/run-migrations.sh` elle yazılmış bayat
   listeyi (001–011'de kalmış) kanonik dizin glob'una çevirir + her psql çağrısına
   `-v ON_ERROR_STOP=1`; (b) `shared/db/migrations/rollback/032_down.sql` — veri varsa
   REDDEDEN preflight'lı geri alma; (c) R-17 ampirik ölçümü: iki adımlı aktivasyonun tek
   transaction'da geçtiği, ters sıranın kısmi indeksçe reddedildiği.
   **Task 3 (a) ayağı, Task 2'nin kalan sınırını da kapatır:** 032'nin fail-closed doğrulama
   bloğu ancak `-v ON_ERROR_STOP=1` ile sıfır-dışı çıkış üretir.
2. Sonra plan sırası: Task 4 → 16. Task 7 bir FREEZE kapısıdır (Katman-1 fixture seti tam
   yeşil olmadan Task 8'e geçilmez).

## Verification (bu oturum)
- **Koşan komutlar / taze çıktı:**
  - `cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → **39 passed** (son koşum
    geçmiş yeniden yazımından SONRA).
  - `ec_ledger_view <window> <root> - --post-window` → **rc=0**, 9 satırın hepsi etiketli
    (footer düzeltmesinden sonra; öncesinde rc=2 MECH-FAIL veriyordu).
  - `git diff backup/pre-footer-fix HEAD` → boş (yeniden yazım içerik değiştirmedi).
  - `command-blocks-maint.sh verify` → PASS (oturum başında).
  - Migration idempotentliği: 032 doğru şema üstüne ikinci kez uygulandı → `rc=0`.
  - Fail-closed oracle'ları (032 doğrulama bloğu): benzersiz-olmayan indeks · eksik UNIQUE ·
    eksik CHECK · geçersiz (invalid) indeks · `DISABLE TRIGGER ALL` · `NOT ENFORCED` → **hepsi rc=3**;
    temiz kurulum ve doğru-şema-üstüne-tekrar → **rc=0**.
- **Codex:** pre-execution drift taraması (rc=0, kayma yok) · checkpoint 1 (tur 1
  needs-attention → fix → tur 2 approve) · checkpoint 2 (tur 1 needs-attention → fix →
  tur 2 needs-attention/reopen → fix → tur 3 approve + yakınsama kararı (A)).
- **DENENMEYEN / kapsanmayan:**
  - Canlıya (`otomaix`) hiçbir migration uygulanmadı — 032/033/034 canlı uygulaması **manuel
    adım**, Task 16 listesinde.
  - Frontend hiç çalıştırılmadı (`npx next build` bu oturumda koşmadı — ilk gerektiği yer Task 12).
  - Eşzamanlı iki pytest oturumu denenmedi.
  - PostgreSQL 18 dışında hiçbir sürümde koşulmadı.
  - Task 3-16 hiç başlamadı.

## Risks (accepted_risk — Auto-Fix Policy: medium/low otonom düzeltilmez)
- **F2 [medium]** İki pytest oturumu aynı anda koşarsa biri diğerinin `otomaix_test`'ini
  DROP eder (kilit yok). Subagent-driven modda tek tek koşuluyor; risk düşük ama açık.
- **F3 [medium]** Migration keşfi tekrarlı/eksik numarayı reddetmiyor (`032_a` + `032_b`
  ikisi de 32 sayılır). Task 3'ün runner işi buna komşu — orada yeniden değerlendirilebilir.
- **F4 [medium]** `db` fixture'ının testler-arası geri sarma garantisi kanıtlayan testi yok.
- **F5 [medium]** `sector_research_artifacts` TRUNCATE koruması (plana ek, bildirildi) doğru
  kurulmuş ama regresyon testi yok. Codex teyit etti: doğru çalışıyor, Task 3'ün DROP TABLE
  geri almasını engellemiyor.
- **F6 [low]** `idx_brands_sub_sector_id` planın Task 2 sözleşmesinde yazılı değil; sapma
  olarak bildirilmeden eklendi.
- **F2-cp3 [medium]** On-prem kurulum paketi (`shared/local-deployment/docker-compose.yml`)
  PostgreSQL 16 imajını pinliyor; migration 032 PG18 kolonu (`pg_constraint.conenforced`)
  okuyor — ölçüldü: PG 16.13'te kolon YOK. On-prem `setup.sh` zinciri 032'de gürültülü
  hatayla durur. Eray kararı (2026-08-24): canlı sistem test aşamasında, şimdi çözülmeyecek.
  Detay + üç seçenek: TASK.md Open Problems.
- **F3-cp3 [medium]** `test_rollback_refuses_when_package_data_exists` iki korunan tabloyu
  AYNI anda dolduruyor; preflight'ın OR kapısının bir ayağı silinse test yine yeşil kalır.
  Uygulama şu an ikisini de sayıyor. Auto-Fix Policy: medium → `accepted_risk`.
- **F17** (önceki oturumdan, Eray risk-kabulü): damga = edited-lineage atfı. **Yeniden
  açtırma.**
- **Sürüm kırılganlığı (dürüst sınır, bulgu değil):** 032 doğrulama bloğu PG18 `conenforced`
  kolonunu ve `trig=4` iç-tetikleyici sayısını okur; başka majör sürümde **gürültülü** hata
  verir (sessiz geçiş değil). Canlı + test aynı 18.3 sunucusunda.
- Lint artıkları: `test_migration_032.py` ve `test_infra.py`'de kullanılmayan `pytest` importu.
  Evi: yürütme sonrası `/simplify-claude-codex`.
- `backup/pre-footer-fix` ve `backup/pre-t3-kind-fix` etiketleri: evi
  `/finish-branch-claude-codex` (merge/PR kararından sonra silinir).

## Notes For Claude
- **Alt-oturum talimatına HER SEFERİNDE planın "Global Constraints" bloğunu koy.** Bu oturumda
  koymadım ve Task 1'in yüksek bulgusu tam olarak oradan doğdu (plan `127.0.0.1:5433` diyordu,
  task-seviyesi invariant yalnız db adını söylüyordu, kod da yalnız adı kontrol etti).
- **`Exec-Kind` etiketini yazmadan ÖNCE commit'in path kümesine BAK.** `tests/` altındaki her
  şey test sayılır (`conftest.py` dahil). hepsi test → `red-only` · hepsi impl → `green-only` ·
  karışık → `code` · yalnız `.sql` → `migration` · yalnız docs → `docs-only`. Yanlış etiket
  defteri kırar ve Adım 11.0'ı bloklar; bu oturumda tam olarak bu oldu.
- **Kural zaten bağlıysa kullanıcıya menü açma.** critical/high → sormadan düzelt;
  medium/low → `accepted_risk` yaz, devam et. Bu oturumda iki kez menü açtım, Eray haklı
  olarak itiraz etti.
- **Codex çağrılarında kapsamı daralt.** Tam spec + tam plan okutmak 480 sn timeout'una
  çarpıyor (bir kez oldu). Prompt'ta hangi bölümlerin okunacağını açıkça yaz; uzun koşum
  gerekirse probe + `CSS_CALL_TIMEOUT=1200s` deseni (arka planda).
- Yeniden açılan bir cluster 3. turda da yeni bir katman açarsa **DUR ve çerçeve teşhisi ver**
  — F7'de tur 3'te Codex'ten açık yakınsama kararı istedim, (A) verdi ve kapandı.
- **`last_checkpoint_ref` TAM SHA olmalı (40 hane).** Kısa SHA yazınca Codex substratı
  `git fetch ... -- <sha>` adımında `couldn't find remote ref` ile düşer; çağrı hiç yapılmaz
  (fail-closed, rc=2 — kota harcanmaz ama checkpoint koşmaz). Bu oturumda bir kez oldu.
- Push henüz hiç yapılmadı ve completion gate'e kadar yapılmayacak.

## Notes For Codex
- Kapsam daraltma prompt'ta açıkça veriliyor; sanitize substratta `.env`, `config.py`,
  `caption_generator.py` gibi dosyalar hariç tutuluyor — **yokluklarını bulgu sayma**.
- Sanitize substratta pytest koşamıyorsun (venv yok + yazılabilir temp yok); runtime ölçümleri
  prompt'ta veriliyor, koda karşı doğrula.
- F2/F3/F4/F5/F6 dispositioned `accepted_risk` — **yeniden açma**. F17 kullanıcı-tahkimli.
