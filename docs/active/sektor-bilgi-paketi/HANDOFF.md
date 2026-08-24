# Handoff

> ⚠️ YÜRÜTME AÇIK — bu anlatı oturum sonuna aittir; canlı yürütme durumu TASK.md
> "Execution State" + git defterinden okunur, çelişkide onlar esastır.

## Context
- Task: sektor-bilgi-paketi — Plan 1 yürütmesi açık (`/execute-plan-claude-codex` protokolü)
- Last updated: 2026-08-24 (yedinci oturum — Task 3 ve Task 4)
- Plan: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (`plan-approved`)
- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Dal: `feat/sektor-bilgi-paketi` (**upstream YOK — hiç push edilmedi**)
- Codex ham review log'u: `/root/.claude/logs/otomaix--ffc87809/2026-08-24-feat-sektor-bilgi-paketi-execute.md`

## Current State
- **Biten:** Task 1 (pytest altyapısı) · Task 2 (migration 032) · Task 3 (runner + geri alma +
  R-17 ölçümü) · Task 4 (R-01/R-02 kök kova korumaları). 16 task'ın 4'ü.
- **Mod:** Bu oturumda **inline** koşuldu (Eray talebi) — alt-oturum açılmadı.
  `execute_mode: subagent-driven` kaydı BİLEREK değiştirilmedi (Task 1-2'yi doğru anlatıyor).
  **inline YALNIZ task yazımını kapsar; review/checkpoint kapıları normal koşar.**
- **Checkpoint:** `cp_count: 4`. Checkpoint 3 (Task 3) dört turda `approve` + yakınsama
  kararı (A) ile kapandı. Checkpoint 4 (Task 4) bir tur koştu, `needs-attention` verdi,
  bulgusu düzeltildi ama **kapanış turu açılamadı** (aşağıda).
- **Ortam (yeni oturumda TEKRAR KURMA — duruyor):** `apps/social/backend/.venv`.
  Komut daima `.venv/bin/python`; makinede `python` komutu YOK.
- **Geçmiş iki kez yeniden yazıldı (ikisi de Eray onaylı, içerik bayt-aynı):**
  `backup/pre-footer-fix` (altıncı oturum) ve `backup/pre-t3-kind-fix` (bu oturum,
  `Exec-Kind: code` → `migration` etiket düzeltmesi).

## Resume From (sıra)
1. **Task 5** — `### Task 5: Veri/API regresyon kümesi + marka kök-sektör tam sweep`.
2. Sonra Task 6 → 16. **Task 7 bir FREEZE kapısıdır** (Katman-1 fixture seti tam yeşil
   olmadan Task 8'e geçilmez).
3. Yeni oturumun ilk Codex çağrısı checkpoint bütçesini sıfırdan başlatır — Task 4'ün açık
   kapanış doğrulaması (aşağıdaki Risks maddesi) oraya bindirilebilir.

## Verification (bu oturum)
- **Koşan komutlar / taze çıktı:**
  - `cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → **55 passed** (son
    koşum `afc8daf`'ten sonra).
  - `ec_ledger_view <execute_start_ref> <root> - --post-window` → **rc=0**, her satır etiketli.
  - psql bayrak ölçümü: hatalı SQL bayraksız **rc=0**, `-v ON_ERROR_STOP=1` ile **rc=3**.
  - `pg_constraint.conenforced` PostgreSQL **16.13**'te YOK (`count(*) = 0`); test/canlı 18.3.
  - `DO $$ BEGIN COMMIT; END $$;` → düz `psql -f` **rc=0**, `psql -1 -f` **rc=3**
    (geri almanın sarmalayıcı-kapısının dayanağı).
  - `git diff backup/pre-t3-kind-fix HEAD` → boş (etiket yeniden yazımı içerik değiştirmedi).
- **Pozitif kontrol disiplini:** bu oturumun DÖRT düzeltmesinin dördü de, düzeltmeden ÖNCEKİ
  sürüme karşı düşen bir testle kanıtlandı (yarış · yalıtım+sarmalama · eksik tablo ·
  fail-closed taksonomi). "Test yazdım, geçti" tek başına kanıt sayılmadı.
- **Codex:** checkpoint 3 → 4 tur, `approve`, yakınsama (A). checkpoint 4 → 1 tur,
  `needs-attention`, kapanış turu AÇILMADI.
- **DENENMEYEN / kapsanmayan:**
  - Canlıya (`otomaix`) hiçbir migration uygulanmadı — 032 canlı uygulaması manuel adım,
    Task 16 listesinde.
  - Frontend hiç çalıştırılmadı (`npx next build` koşmadı — ilk gerektiği yer Task 12).
  - Geri alma script'i GERÇEK `docker compose` yığınına karşı koşulmadı; runner testleri
    PATH'e konan sahte `docker` kabuğu üzerinden gerçek psql'e gidiyor.
  - PostgreSQL 18 dışında hiçbir sürümde test koşulmadı (16 yalnız tek kolon sorgusu için
    ayağa kaldırıldı).
  - `create_brand` / `update_brand` uçları bozuk taksonomiyle UÇTAN UCA denenmedi; yeni kapı
    yalnız çözümleyici seviyesinde sınandı (istisna yazımdan önce patlıyor — yapısal).

## Risks
- **[AÇIK KAPI — accepted_risk DEĞİL] Task 4 kapanış doğrulaması yapılmadı.** `afc8daf`
  (fail-closed taksonomi kapısı) hiçbir Codex turuyla doğrulanmadı; checkpoint bütçesi
  (`global cap − 3`) dolduğu için tur açılmadı ve Eray "oturumu kapat" dedi. Bugünkü kanıt
  yalnız pozitif kontrollü test. **Evi: yeni oturumun ilk checkpoint'i VEYA Adım 11 final
  execution review.** `last_checkpoint_ref` bu yüzden BİLEREK ilerletilmedi — Task 4
  commit'leri hâlâ kapsamda.
- **[medium, accepted_risk]** İki pytest oturumu aynı anda koşarsa biri diğerinin
  `otomaix_test`'ini DROP eder (kilit yok).
- **[medium, accepted_risk]** Migration keşfi tekrarlı numarayı reddetmiyor (`032_a` + `032_b`
  ikisi de 32 sayılır). Task 3 runner'ı numarasız dosyayı reddediyor ama tekrarlı numarayı
  reddetmiyor — bilinçli.
- **[medium, accepted_risk]** `db` fixture'ının testler-arası geri sarma garantisini kanıtlayan
  test yok.
- **[medium, accepted_risk]** `sector_research_artifacts` TRUNCATE korumasının regresyon testi yok.
- **[medium, accepted_risk]** Geri alma red testi iki korunan tabloyu AYNI anda dolduruyor;
  preflight'ın OR kapısının bir ayağı silinse test yine yeşil kalır.
- **[medium, accepted_risk — Eray kararı]** On-prem paketi PostgreSQL 16 imajını pinliyor,
  032 PG18 kolonu okuyor. Eray: "canlı sistem test aşamasında, önemli değil". **Dürüst etiket:
  ÇÖZÜLMEDİ + park edildi.** Yeniden açılma koşulu: on-prem paketi gerçekten kurulacaksa.
  Üç seçenek TASK.md Open Problems'ta.
- **[low, accepted_risk]** `idx_brands_sub_sector_id` planın Task 2 sözleşmesinde yazılı değil.
- **F17 (Eray risk-kabulü):** damga = edited-lineage atfı. **Yeniden açtırma.**
- **Residual (evi Task 16):** geri alma ile ileri 032 arasında ortak kilit yok; tam çözüm
  032'yi transactional yapmayı gerektirir (onaylı Task 2 artefaktı).
- **Temizlik borçları (evi: yürütme sonrası `/simplify-claude-codex`):** `test_migration_032.py`
  ve `test_infra.py`'de kullanılmayan `pytest` importu · `brands.py`'deki artık ulaşılamaz
  `resolved if resolved else (...)` dalı.
- **Etiketler (evi: `/finish-branch-claude-codex`):** `backup/pre-footer-fix` ve
  `backup/pre-t3-kind-fix` merge/PR kararından sonra silinir.

## Notes For Claude
- **`last_checkpoint_ref` TAM SHA olmalı (40 hane).** Kısa SHA yazınca Codex substratı
  `couldn't find remote ref` ile düşer; çağrı hiç yapılmaz (fail-closed, kota harcanmaz ama
  checkpoint de koşmaz). Bu oturumda bir kez oldu.
- **`Exec-Kind` etiketini yazmadan ÖNCE commit'in path kümesine BAK.** Defter `.sql`
  dosyasını "impl" SAYMAZ. Yani test + yalnız `.sql` = `migration`, `code` DEĞİL. `code`
  hem test hem impl kümesinin DOLU olmasını ister. Bu oturumda üç commit yanlış etiketlendi,
  defter kırıldı, geçmiş yeniden yazılarak düzeltildi — aynı hata iki oturum üst üste oldu.
- **Pozitif kontrolü atlama.** Her düzeltmede, yeni testi düzeltme ÖNCESİ sürüme karşı koştur
  (dosyayı geçici olarak `git show HEAD:<path>` ile geri al, testi koş, geri yükle). Bu
  oturumda dört kez yapıldı ve dördü de hatanın gerçekliğini kanıtladı.
- **Codex çağrılarında kapsamı daralt.** Prompt'ta hangi bölümlerin okunacağını AÇIKÇA yaz;
  uzun koşum gerekirse `CSS_CALL_TIMEOUT=1200s` + arka plan.
- **Yeniden açılan bir cluster yeni katman açarsa yakınsama kararı iste.** Checkpoint 3'te
  tur 3'te (B), tur 4'te (A) alındı ve küme kapandı. İşe yarıyor, tekrarla.
- **Kural zaten bağlıysa menü açma:** critical/high → sormadan düzelt; medium/low →
  `accepted_risk` yaz, devam et. AMA bütçe/rezerv sınırına gelindiyse yüksek bulguyu sessizce
  devretme — DUR ve Eray'a rapor et (bu oturumda tam olarak bu oldu).
- Push henüz hiç yapılmadı ve completion gate'e kadar yapılmayacak.

## Notes For Codex
- Kapsam daraltma prompt'ta veriliyor; sanitize substratta `.env`, `config.py` gibi dosyalar
  hariç tutuluyor — **yokluklarını bulgu sayma**.
- Sanitize substratta pytest/psql koşamıyorsun; runtime ölçümleri prompt'ta veriliyor, koda
  karşı doğrula.
- Dispositioned `accepted_risk` maddeleri **yeniden açma** (yukarıdaki Risks listesi).
  F17 Eray-tahkimli.
- Task 4'ün `afc8daf` commit'i HENÜZ kapanış doğrulaması görmedi — bir sonraki turda o
  öncelikli.
