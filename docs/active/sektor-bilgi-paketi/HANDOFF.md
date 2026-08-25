# Handoff

> ⚠️ YÜRÜTME AÇIK — bu anlatı oturum sonuna aittir; canlı yürütme durumu TASK.md
> "Execution State" + git defterinden okunur, çelişkide onlar esastır.

## Context
- Task: sektor-bilgi-paketi — Plan 1 yürütmesi açık (`/execute-plan-claude-codex` protokolü)
- Last updated: 2026-08-25 (on beşinci oturum — Task 15 bitti, Task 15b geri alındı)
- Plan: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (`plan-approved`)
- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Spec girdisi: `docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md` — **karar sorusu
  çıkarsa ÖNCE buraya bak; spec bir özet, kanonik ayrıntı input'ta.**
- Dal: `feat/sektor-bilgi-paketi` (**upstream YOK — hiç push edilmedi**)
- Codex ham review log'u: `/root/.claude/logs/otomaix--ffc87809/2026-08-24-feat-sektor-bilgi-paketi-execute.md`

## Current State
- **Biten:** Task 1–15 (16'nın 15'i). **Açık kapı YOK.**
- **Checkpoint:** sayaç ve ref TASK.md "Execution State"ten okunur — burada TEKRARLANMAZ.
- **Mod:** inline. `execute_mode: subagent-driven` kaydı BİLEREK değiştirilmedi (Task 1-2'yi
  doğru anlatıyor). inline YALNIZ task yazımını kapsar; review/checkpoint kapıları normal koştu.
- **Tavan:** 8; sayaç tavanın ÜSTÜNDE, her riskli task `CEILING_RISK` dalına düşüyor. Eray bu
  oturumda tavan iznini AÇIKÇA verdi; **o izin BU OTURUMA aitti**, yeni oturumda tekrar sorulmalı.
- **Ortam (yeni oturumda TEKRAR KURMA — duruyor):** `apps/social/backend/.venv`.
  Komut daima `.venv/bin/python`; makinede `python` komutu YOK.

## Resume From (sıra)
1. **Task 16** — kapanış: tam sweep + kabul eşlemesi + Plan 2 arayüz teslimi + MANUEL adımlar.
   Manuel adımların listesi aşağıda "Risks" altında; hiçbiri bu oturumda yapılmadı.
2. **Task 16'nın manuel adımları KOŞULMAZ** — Eray kararıyla Plan 2 sonrasındaki tek
   doğrulama turuna devredildi. Task 16 yine yazılır (tam sweep · kabul eşlemesi · arayüz
   sözleşme testi), ama manuel adımlar "ertelendi + evi belli" diye kaydedilir, "yapıldı"
   diye DEĞİL.
3. **Task 8'den sonraki HER task'ın son adımı tam sweep'tir:**
   `.venv/bin/python -m pytest tests/prompt_regression/ -q` yeşil olmadan ilerlenmez.
4. Oturum başında tavan-aşımı için Eray'dan izin iste.
5. **Task 16'dan SONRA, canlıya müşteri alınmadan ÖNCE:** `CURRENT.md` →
   `brand-settings-save-integrity`. Bu madde bu oturumun ürünüdür ve ertelenmiş değil,
   **evi olan** bir iştir.

## Verification (bu oturum)

**Koşan komutlar / taze çıktı:**
- `cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → **538 passed**
  (oturum başında 502; Task 15 + düzeltmeler + Task 15b arka uç kapısı).
- `.venv/bin/python -m pytest tests/prompt_regression/ -q` → **121 passed**
  (byte-exact freeze kapısı; donmuş fixture'lar bayt DEĞİŞMEDİ).
- `cd apps/social/frontend && npx next build` → **başarılı** (geri alma sonrası taze koşuldu).
- Uygulama ayağa kalkıyor; `/sectors/sub-sector-candidates` kayıtlı ve rota sırası doğru.
- `command-blocks-maint.sh verify` → **PASS**.

**Pozitif kontroller (kapıların gerçekten ölçtüğünü kanıtlayanlar — hepsi taze):**
- Task 15 yazımında **7 mutasyon**, hepsi ilgili testi DÜŞÜRDÜ (aday sorgusunun aktif-paket
  şartı · kök filtresi · açık-null boşaltma · öneri tip kapısı · öneri listede-mi kapısı ·
  atanabilirlik ön-kontrolü · yapısal detektörün ayrım gücü).
- Düzeltme turlarında **7 mutasyon daha** (kota kapısı · girdi sınırı · sağlayıcı arızasının
  görünürlüğü · süre sınırı · boş-aday kısa devresi · kısıt-adı ayrımı · kapalı listenin
  prompta gömülmesi) — hepsi yakalandı.
- Task 15b arka uç kapısında **3 mutasyon**, hepsi yakalandı.
- **İki mutasyon HAYATTA KALDI ve ikisi de gerçek boşluk gösterdi:** biri benim no-op kurgu
  hatamdı, öteki boş-aday kısa devresinin amacının ÇIKTI değil "boşuna ücretli çağrı yakmamak"
  olduğunu ortaya çıkardı — o iddia ayrıca teste bağlandı.

**ÇÜRÜTÜLEN / DÜZELTİLEN VARSAYIMLAR (kayda değer):**
- "Tetikleyici `RaiseError` fırlatır" YANLIŞTI — `IntegrityConstraintViolationError` fırlatıyor;
  ilk yakalama kümem hiç çalışmayacaktı.
- "SQLSTATE sınıfı bizim kapımızı tanımlar" YANLIŞTI — aynı sınıfı çalışma alanı ve kök sektör
  yabancı anahtarları da üretiyor; kapı artık kısıt ADINA bakıyor.
- "Sürüm damgası testlerde ölçülebilir" YANLIŞTI — damga transaction'ın BAŞLANGIÇ anı, standart
  düzenek her şeyi tek transaction'da tuttuğu için damga hiç ilerlemiyor ve kapı SAHTE YEŞİL
  verirdi. Testler ayrı transaction'lara taşındı.
- **Premis düzeltmesi (Eray):** marka ayarları MÜŞTERİ yüzeyi; riski "tek operatör" ölçeğiyle
  küçültmek yanlıştı.

**Codex:** checkpoint 15 → **3 tur** (needs-attention; sistemik-sınıf DUR'u ateşlendi).
Task 15b checkpoint → **1 tur** (needs-attention; 5 high → geri alma).
Bir çağrı 480s'de timeout'a düştü; canlılık yoklaması companion'ın sağlam olduğunu gösterdi ve
protokolün öngördüğü tek tekrar 1200s ile koştu. Bir çağrı da kısaltılmış SHA yüzünden substratı
kuramadı (rc=2) — Codex hiç çağrılmadı; **taban ref'i daima TAM SHA ver.**

**DENENMEYEN / kapsanmayan:**
- **TÜM MANUEL DOĞRULAMALAR PLAN 2 SONRASINA ERTELENDİ (Eray kararı, 2026-08-25).**
  Kapsam: Task 15'in arayüz doğrulaması (onayla/değiştir/boşalt · boş-aday hâli · kanal
  doldurma · sitesiz öneri düğmesi) · canlı n8n importu ve gerçek Telegram teslimi ·
  gerçek arayüzde uçtan uca üretim. Ev: **Plan 2 bitiminde koşulacak tek doğrulama turu.**
  Bu erteleme Task 16'nın kabul eşlemesine AYNEN yazılır: Plan 1, arayüz yüzeyleri
  DOĞRULANMAMIŞ hâlde kapanır — "doğrulandı" diye kaydedilmez.
- Canlıya hiçbir migration uygulanmadı (032 · 033 · 034).
- Gerçek arayüzde tek bir üretim denenmedi; gerçek bir sektör paketi hiç yazılmadı.
- Öneri uçlarının hiçbiri GERÇEK model çağrısıyla koşulmadı (hepsi sahte istemciyle).
- Kota kapısı davranışsal ölçülmedi (Redis ister; ev kuralı Redis yokken zaten fail-open).
- `IS JSON OBJECT` ve `conenforced` yalnız PostgreSQL 18.3'te ölçüldü; PG16'da varlıkları
  BELGEYE dayanıyor.

## Risks

**Bilinçli tasarım kararları (bulgu SAYILMAZ):**
- Alt sektör YAZIM kapısı yalnız "alt sektör satırı mı" sorar; aktif paket şartı ARAMAZ.
  K-43 gereği paketi arşivlenen markanın ataması korunur, yani paketsiz alt sektör meşru bir
  kayıtlı değerdir. Aday kümesi neyin ÖNERİLECEĞİNİ belirler, neyin saklanabileceğini değil.
  Codex bunu genişletmek istedi; planın bağlayıcı invariantı yalnız tetikleyiciyi adlandırdığı
  için REDDEDİLDİ (tasarım değişikliği, yürütme kararı değil).
- Öneri ucunun kota kapısı Redis yokken fail-open'dır — ev kuralının belgeli kararı. Tek uç
  için ayrı politika uydurulmadı.
- Site analizi ucunun "model hatası → boş şablonla HTTP başarı" davranışı bu partiden ÖNCE de
  vardı ve değiştirilmedi; YENİ öneri ucunda aynı sınıf kapatıldı (arıza 503).
- Sunucudaki koşullu yazım kapısı ve 5 testi depoda UYKUDA — hiçbir çağıran sürüm göndermiyor,
  davranış Task 15 sonrasıyla aynı. Uyanmadan tek başına bir şey garanti ETMEZ.

**Açık kalemler — hepsinin evi VAR:**
- **[YENİ — bu oturumun ürünü]** Marka ayarları otomatik kaydetmesinin dört kayıp yolu açık.
  Ev: `CURRENT.md` → `brand-settings-save-integrity`. **Tetik: Task 16'dan sonra, canlıya
  müşteri alınmadan ÖNCE.** Önyüz test altyapısı bu işin ÖN KOŞULU.
- **[YENİ]** Senkron sağlayıcı çağrısı gerçekten kesilemiyor (süre sınırı yalnız beklemeyi
  keser). Kod tabanı GENELİ bir desen — caption, kısa video, site analizi hepsi aynı.
  Bu partinin kusuru değil; somut kusurları (yeniden deneme çarpanı, biçim doğrulaması,
  önyüzün arızayı gizlemesi) kapatıldı.
- **[Eray tetikledi]** Süpürücü ↔ geç webhook terminallik çelişkisi. Ev: `CURRENT.md`.
  Tetik: sektör bilgi paketi işi TAMAMEN bittikten sonra.
- **[çözülmedi + park edildi, TETİKLİ]** `sector_packages.sector_id` değişmez değil. Ev: `CURRENT.md`.
- **[TETİKLİ]** Migration 032/033'ün garanti blokları kolon/tablo imzası doğrulamıyor. Ev: `CURRENT.md`.
- **[Manuel adım — evi Task 16]** `N8N_ADMIN_EVENT_SECRET` canlıya kurulmalı · n8n'de header-auth
  kimlik bilgisi yaratılmalı ve workflow'daki yer tutucu değiştirilmeli ·
  `OTOMAIX_ADMIN_TELEGRAM_BOT_TOKEN` + `..._CHAT_ID` env'leri kurulmalı · workflow import edilip
  TEK Telegram teslimi smoke'u koşulmalı.
- **[Manuel adım — evi Task 16]** `apps/social/backend/.env.example`'a `N8N_ADMIN_EVENT_SECRET`
  satırı ELLE eklenmeli (sır-dosyası yazma kapısı agent'ı engelliyor).
- **[Manuel adım — evi Task 16]** Task 15'in UI doğrulaması.
- **[accepted_risk, checkpoint 12]** Kütüphane yoklaması terminal başarısız satırları sınırsız yokluyor.
- **[doğrulama boşluğu — evi: kuyumculuk pilotu]** Uçtan uca gerçek akış ölçümü.
- **[Plan 2 teslim kalemi]** Brief/sentez hattı `video_kodlar` için İKİ HAVUZ üretmeli.
- **[Plan 2 teslim kalemi]** `recovered` modu + geri-dönüş mesajı (F23 kapanışı).
- **[Residual — evi Task 16]** 033 ve 034 için geri alma script'i YOK (plan istemedi).
- **[Temizlik borçları — evi `/simplify-claude-codex`]** İki dosyada kullanılmayan `pytest`
  importu · `brands.py`'de kullanılmayan `BrandOut`.
- **[Etiketler — evi `/finish-branch-claude-codex`]** `backup/pre-footer-fix`,
  `backup/pre-t3-kind-fix` merge/PR kararından sonra silinir.

**Devralınan, değişmeyen kalemler:**
- `accepted_risk` (checkpoint 9): CTA içinde serbest köşeli ayraç yok · `brand_kit` anahtarı silinemez.
- Belgeli sınırlar (testle pinli, borç DEĞİL): ayraçsız kanal işareti yakalanmaz · tam genişlikli
  ayraçlı etiket tanınır ama basımdan çıkarılamaz.
- `accepted_risk` (test altyapısı): **eşzamanlı iki pytest oturumu `otomaix_test`'i düşürür**
  (bu oturumda bir kez tetiklendi — arka plan ve ön plan koşumu çakıştı, 9 hata verdi; tek
  koşumda 538 passed) · migration keşfi tekrarlı numarayı reddetmiyor · `db` fixture geri sarma
  testi yok · `sector_research_artifacts` TRUNCATE regresyonu yok.
- **[Eray risk kabulü]** On-prem PG16 ↔ 032'nin PG18 kolonu: çözülmedi + park edildi.
- **F17 (Eray):** damga = edited-lineage atfı. **Yeniden açtırma.**

## Notes For Claude

- **ÖLÇEMEDİĞİN YERE ELLE EŞZAMANLILIK KODU YAZMA.** Bu oturumun en pahalı dersi: önyüzde
  otomatik test altyapısı yok ve oraya elle bir eş güdüm katmanı yazıldı; doğrulama "okundu +
  derlendi" ile yapıldı. Beş high çıktı ve kod iki yolda düzelttiği hatadan kötüydü. Sıra ve
  araya-girme hataları okumayla görülmez. Ya ölçüm aracı önce kurulur, ya sınıfı silen bir
  tasarım seçilir.
- **ARAÇ TUZAĞI — tekrarlama.** `run_codex_scan` `$COMPANION` ve `$PROMPT` değişkenlerini
  KULLANIR ama TANIMLAMAZ; ikisini de çağıran kurar. Kurulmazsa `node ""` koşar: arka planda
  sessizce exit 0 + boş çıktı, ön planda ASILI kalır. stderr'de `[codex]` işareti YOKSA çağrı
  kurulmamıştır.
- **Taban ref'i daima TAM SHA ver.** Kısaltılmış SHA substrat kurulumunda `couldn't find remote
  ref` ile düşer (rc=2) ve Codex hiç çağrılmaz — bu oturumda bir kez oldu.
- **Codex 480s'de timeout verirse reflekssel degradation'a düşme:** önce 120s canlılık yoklaması,
  companion sağlamsa `CSS_CALL_TIMEOUT=1200s` ile BİR tekrar.
- **Mutasyonu geri alırken `git checkout <dosya>` KULLANMA** — dosyada commit edilmemiş iş varsa
  onu da siler. Bu oturumda bir dosyanın tüm değişikliklerini böyle kaybettim ve yeniden yazdım.
  Yedek kopya al, kopyadan geri yaz.
- **Codex'in "inferred / could not run" etiketli bulgusunu sonda koşmadan kabul etme.**
- **Aynı sınıf iki-üç tur üst üste çıkarsa yamamayı bırak** ve çerçeve-teşhisli raporu kullanıcıya
  götür. Bu oturumda tam olarak bu yapıldı ve doğru karar oradan çıktı.
- **Kendi düzeltmenin yan etkisini ölç.** Task 15b'de sürüm koruması eklenince marka satırını
  değiştiren DİĞER beş yol (logo, video, kimlik bilgileri, avatar) elimizdeki işareti bayatlatıp
  SAHTE çakışma üretecekti — yani düzeltme, düzelttiği hatadan beter olacaktı.
- **Yorumun kodun sahip olmadığı bir garantiyi iddia etmesine dikkat.** 15b'de "aynı akışın
  bekleyeni üstüne yazılır" yazılmıştı; kod akışları hiç ayırmıyordu. Yorumu yazarken değil,
  yazdıktan sonra koda karşı OKU.
