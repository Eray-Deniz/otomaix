# Handoff

> ⚠️ YÜRÜTME AÇIK — bu anlatı oturum sonuna aittir; canlı yürütme durumu TASK.md
> "Execution State" + git defterinden okunur, çelişkide onlar esastır.

## Context
- Task: sektor-bilgi-paketi — Plan 1 yürütmesi açık (`/execute-plan-claude-codex` protokolü)
- Last updated: 2026-08-24 (dokuzuncu oturum — Task 7 ve Task 8)
- Plan: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (`plan-approved`)
- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Dal: `feat/sektor-bilgi-paketi` (**upstream YOK — hiç push edilmedi**)
- Codex ham review log'u: `/root/.claude/logs/otomaix--ffc87809/2026-08-24-feat-sektor-bilgi-paketi-execute.md`

## Current State
- **Biten:** Task 1–6 (önceki oturumlar) · **Task 7** (Katman-1 kısa video + legacy fixture'ları —
  FREEZE kapısı) · **Task 8** (paket erişim katmanı). **16 task'ın 8'i — planın yarısı.**
- **Devralınan borç YOK, devreden borç YOK.** Bu oturum açık kapı bırakmıyor.
- **Mod:** inline (Eray talebi). `execute_mode: subagent-driven` kaydı BİLEREK değiştirilmedi
  (Task 1-2'yi doğru anlatıyor). inline YALNIZ task yazımını kapsar; review/checkpoint kapıları
  normal koştu.
- **Checkpoint:** `cp_count: 8` = **TAVAN**. Checkpoint 7 tek turda `approve`; checkpoint 8 dört
  turda `approve` (tur 1-3 `needs-attention`).
- **Ortam (yeni oturumda TEKRAR KURMA — duruyor):** `apps/social/backend/.venv`.
  Komut daima `.venv/bin/python`; makinede `python` komutu YOK.

## Resume From (sıra)
1. **Task 9** — `### Task 9: Kanal envanteri — brand_kit.channels + deterministik filtre`.
2. **Task 9 riskli sınıflanırsa checkpoint kararı TAVAN-AŞIMI dalına düşer** (`cp_count` 8 =
   ceiling). Eray bu oturumda açıkça izin verdi: *"tavanı geçsek codex review yapılması
   gerekiyorsa yap, ben izin veriyorum"*. Yine de aşımı **görünür şekilde bildir** — sessizce
   geçme; audit satırı `ceiling-exceed`.
3. Sonra Task 10 → 16. Task 10 (tek-kapı enjeksiyon) `sector_packages.resolve_package_context`'in
   İLK tüketicisidir — çözümleyicinin dönüş sözleşmesi (dört alan, `None` = paketsiz yol) orada
   sınanacak.
4. **Task 8'den sonraki HER task'ın son adımı tam sweep'tir:**
   `.venv/bin/python -m pytest tests/prompt_regression/ -q` yeşil olmadan ilerlenmez (Task 7
   freeze hükmü).

## Verification (bu oturum)
- **Koşan komutlar / taze çıktı:**
  - `cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → **185 passed**
    (oturum başında 78'di).
  - `.venv/bin/python -m pytest tests/prompt_regression/ -q` → **25 passed** (freeze kapısı).
  - `ec_ledger_view <execute_start_ref> <root> - --post-window` → **rc=0**, her satır etiketli.
  - Marka eşleşmesi kapanış matrisi: 8 marka × tüm yazımlar (küçük/büyük/başlık × NFC/NFD/NFKC/NFKD)
    çapraz → **277 çift, kaçan 0**; yanlış-pozitif kontrolü ("Ada" vs "mağazada") → tetiklenmiyor.
  - Mutasyon taraması: 23 kabul dalı tek tek kapatıldı, her biri için ≥1 test kırmızıya döndü.
  - Fixture alarmı: dondurulmuş dosyaya tek satır eklenince ilgili test kırmızı.
  - Dondurma bayrağı kapısı: `PROMPT_REGRESSION_UPDATE=1` ile süit KIRMIZI, bayraksız yeşil.
- **Pozitif kontrol disiplini:** her düzeltme, düzeltmeden ÖNCEKİ sürüme karşı düşen bir testle
  kanıtlandı. F5 (bağlam kurulumu) yapısal olarak da kanıtlandı — girintiye bakılmadı, AST
  gezilerek kurulumun `try` gövdesinde olduğu ölçüldü.
- **Codex:** checkpoint 7 → 1 tur `approve`. checkpoint 8 → 4 tur, tur 4 `approve`.
- **DENENMEYEN / kapsanmayan:**
  - Canlıya (`otomaix`) hiçbir migration uygulanmadı — 032 canlı uygulaması manuel adım, Task 16.
  - Frontend hiç çalıştırılmadı (`npx next build` koşmadı — ilk gerektiği yer Task 12).
  - `sector_packages` modülünün HİÇBİR tüketicisi yok — üretim yolu onu çağırmıyor (Task 10).
    Yani modül bugün canlı davranışı etkilemiyor; testlerin dışında koşmadı.
  - Fixture'lar caption/fikir/kısa video/legacy yüzeylerini kapsıyor; **görsel director'ın kendi
    ayrı bir yüzeyi varsa** o kapsanmadı — plan seam listesi bu dördünü sayıyor.
  - `capture.py` hâlâ metin olmayan blokla ÜRETİMDE sınanmadı (reddediyor, ama reddi tetikleyen
    gerçek bir üretim yüzeyi yok).
  - PostgreSQL 18 dışında hiçbir sürümde test koşulmadı.

## Risks
- **[dürüstlük notu — checkpoint 8, tur 4]** Tur 4 raporu önceki turlardan belirgin biçimde İNCE
  ve kanonik kapsam beyanını taşımıyor; metnin bir kısmı ölçüm-sürüyor tonunda kesilmiş görünüyor.
  Verdict satırı `approve`. **Kapanışın asıl kanıtı o rapor değil**, Claude'un 277-çift closure
  matrisi + mutasyon kontrolüdür. Tur 4 bunu çürütmedi ama tek başına güçlü onay sayılmaz.
  Evi: Adım 11 final execution review (orada yeniden bakılır).
- **[bilinçli tasarım — kod belgesinde yazılı]** Marka adı eşleşmesi SOL sınır arar, sağ taraf
  serbesttir (Türkçe eklemeli: "Altınbaş'tan", "Altınbaşlar"). Sonuç: kısa bir marka adı aynı
  zamanda sıradan bir sözcükse (ör. "Ada" → "adaya") paket REDDEDİLİR. Yazım kapısında
  yanlış-pozitif, yanlış-negatiften iyidir — operatör mesajı görür, sızan marka bilgisi kalıcıdır.
  Yeniden açılma: gerçek bir meşru paket bu yüzden bloklanırsa.
- **[bilinçli tasarım]** Katlama Türkçe dışı aksanları da düşürür (`é` → `e`). Eşleşmeyi
  genişletir, yani reddetme yönüne çalışır.
- **[gözlem, borç DEĞİL]** `sector_resolver._normalize_slug` bilinçle DEĞİŞTİRİLMEDİ (başka bir
  task'ın artefaktı). `.lower()`'ı tablodan ÖNCE uyguladığı için `İşçi Bayramı` → `i-sci-bayrami`
  gibi tuhaf görünen anahtarlar üretiyor. Tutarlıdır (tüm yazımlar aynı anahtara iner — ölçüldü),
  dolayısıyla K-01b ihlali YOK. Yeniden açılma: slug'ların insan-okunur olması gerekirse.
- **[medium, accepted_risk]** İki pytest oturumu aynı anda koşarsa biri diğerinin `otomaix_test`
  veritabanını DROP eder (kilit yok).
- **[medium, accepted_risk]** Migration keşfi tekrarlı numarayı reddetmiyor (`032_a` + `032_b`
  ikisi de 32 sayılır).
- **[medium, accepted_risk]** `db` fixture'ının testler-arası geri sarma garantisini kanıtlayan
  test yok.
- **[medium, accepted_risk]** `sector_research_artifacts` TRUNCATE korumasının regresyon testi yok.
- **[medium, accepted_risk]** Geri alma red testi iki korunan tabloyu AYNI anda dolduruyor;
  preflight'ın OR kapısının bir ayağı silinse test yine yeşil kalır.
- **[medium, accepted_risk — Eray kararı]** On-prem paketi PostgreSQL 16 imajını pinliyor, 032
  PG18 kolonu okuyor. **Dürüst etiket: ÇÖZÜLMEDİ + park edildi.** Ayrıntı TASK.md Open Problems.
- **[low, accepted_risk]** `idx_brands_sub_sector_id` planın Task 2 sözleşmesinde yazılı değil.
- **F17 (Eray risk-kabulü):** damga = edited-lineage atfı. **Yeniden açtırma.**
- **[checkpoint-override, checkpoint 5]** Sweep tabanının kökeni — TASK.md Open Problems'ta tam
  gerekçesiyle. Adım 11 final review'a `checkpoint_overrides` olarak taşınır.
- **Residual (evi Task 16):** geri alma ile ileri 032 arasında ortak kilit yok.
- **Temizlik borçları (evi: yürütme sonrası `/simplify-claude-codex`):** `test_migration_032.py` ve
  `test_infra.py`'de kullanılmayan `pytest` importu · `brands.py`'deki artık ulaşılamaz
  `resolved if resolved else (...)` dalı.
- **Etiketler (evi: `/finish-branch-claude-codex`):** `backup/pre-footer-fix` ve
  `backup/pre-t3-kind-fix` merge/PR kararından sonra silinir.

## Notes For Claude
- **Varyant yamalamayı bırak, SINIFI kapat.** Bu oturumun en pahalı dersi. F3'te üç tur üst üste
  aynı eksenin daha dar bir varyantı geldi. Üçüncü turda durup "bu bir varyant mı, bir sınıf mı"
  diye sormak gerekiyordu — sorulunca çözüm bir satır oldu. **Sinyal:** her tur bir öncekinden dar
  bir vaka açıyorsa yamalama yakınsamıyor demektir.
- **Elle seçilmiş örnek, kapanış kanıtı değildir.** Aynı vakada üç turdur yeşil olan testler elle
  seçilmiş vakalardı. Kapanışı üretilmiş matrisle kanıtla (biçim uzayını kodun kendisi üretsin),
  yoksa bir sonraki tur senin görmediğin biçimi bulur.
- **Kendi commit mesajındaki iddiayı da doğrula.** F5 tam olarak buydu: "kurulum emniyet sınırına
  taşındı" yazmıştım, taşınmamıştı. İddiayı YAZMADAN önce ölç; yapısal iddiaları AST ile ölç,
  girintiye bakma.
- **Codex'i olduğu gibi kabul etme, ama ciddiye al.** Bu oturumda 7 bulgunun 7'si de bağımsız
  sondajla DOĞRULANDI. Sondaj koşmadan ne kabul et ne reddet.
- **asyncpg jsonb codec açıkken `json.dumps` + `::jsonb` ÇİFT KODLAMA yapar.** Bu oturumda bir
  testi yanlış sebeple yeşil tutmuştu (satırda JSON *dizesi* vardı, test onu "bozuk içerik" sanıp
  geçiyordu). Proje konvansiyonu zaten yasaklıyor: dict'i doğrudan parametre geç.
- **`Exec-Kind` etiketini yazmadan ÖNCE commit'in path kümesine BAK.** Bu oturumda bir kez `docs`
  yazıldı, geçerli değer `docs-only`; defter MECH-FAIL verdi, tepe commit amend edilerek düzeltildi.
  Geçerli küme: `code|docs-only|migration|red-only|green-only|merge`. `tests/` altındaki HER ŞEY
  test sayılır — `capture.py` bile.
- **Codex çağrısı için `COMPANION` kurulmalı.** Bu oturumda ilk deneme `COMPANION: unbound
  variable` ile rc=1 döndü ve companion HİÇ çağrılmadı (fail-closed). Preflight:
  `COMPANION=$(find ~/.claude/plugins/cache/openai-codex -name codex-companion.mjs -type f | head -1)`.
  Prompt SHELL heredoc'uyla yazılmaz — SETUP fence + Write tool ile `$CODEX_LOG` türevli yola.
- **`last_checkpoint_ref` TAM SHA olmalı (40 hane).** Kısa SHA'da Codex substratı
  `couldn't find remote ref` ile düşer.
- **Kota kapısı `SOFT` derse:** sebebi oku. Bu oturumda sebep "ölçüm bayat (>900s)", kullanım
  %1.0'dı; protokolün tek-çağrı dalı "uyar + devam" diyor. Tükenme sebebiyse Eray'a sor.
- **Sır tarayıcısı çok dosya eliyor** — `short_video.py`, `posts.py`, `HANDOFF.md`,
  `test_data_api_regression.py`, `test_infra.py` dâhil. Codex'e "git nesnelerinden oku" diye
  AÇIKÇA söyle, yoksa üretim seam'lerini hiç görmez.

## Notes For Codex
- Kapsam daraltma prompt'ta veriliyor; sanitize substratta üretim dosyaları hariç tutuluyor —
  **yokluklarını bulgu sayma**, git nesnelerinden oku.
- Sanitize substratta pytest/psql koşamıyorsun; runtime ölçümleri prompt'ta veriliyor, koda karşı
  doğrula.
- Dispositioned `accepted_risk` maddeleri **yeniden açma** (yukarıdaki Risks listesi).
  F17 Eray-tahkimli.
- **Sweep tabanının kökeni (checkpoint 5 F1 kümesi) KAPALIDIR** — beş tur döndü, Eray kararıyla
  kapatıldı, iki mekanizma gerekçeli olarak reddedildi. Yeniden açma.
- **Task 8'in üç bilinçli tasarım kararını bulgu sayma:** ~6.000 karakter tavanı UYARI'dır (kapı
  değil) · `video_kodlar` alan adları K-02 açık olduğu için bağlanmadı (yalnız sayı bağlı) ·
  K-15(a) alan-düzeyi atlama dalı bilinçle YOK · marka eşleşmesinde sağ sınırın serbestliği ve
  ondan doğan yanlış-pozitif belgeli bir tercihtir.
