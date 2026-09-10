---
task: sektor-bilgi-paketi-plan2
written: 2026-09-10
---

# Resume From

**Sıradaki iş: Task 16** (komut ailesi — repo CLI + ince adaptörler + bildirim ayakları).
Task 15 indi ve **checkpoint 12 `approve` ile kapandı**.

**Komut:** `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam**.

**KAYIT TASK.md + bu dosya + git defteridir. BAŞKA DEFTER YOK.**

**Yürütme durumu:** kip **`inline`** · başlangıç çapası `a806e29` · defter penceresi `a806e29`.
**`cp_count` ve `last_checkpoint_ref` TASK.md'nin `Execution State` bölümündedir — buraya
KOPYALANMAZ.**

**Dal:** `feat/sektor-bilgi-paketi-plan2`. Push durumu buraya YAZILMAZ, ölç:
`git rev-list --left-right --count origin/feat/sektor-bilgi-paketi-plan2...HEAD`.
**Uç SHA'sı buraya YAZILMAZ.**

**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: bu oturumda DEĞİŞMEDİ.

## Bu oturum ne yaptı — tek cümle

Task 15 uçtan uca yapıldı (kanıtın veritabanından okunduğu taslak yazımı, yerinde güncelleme,
aktivasyon zinciri), dört hakem turu koştu, üç yüksek + üç orta bulgunun hepsi karara bağlandı,
ve iki tur üst üste kilit-sırası bulgusu verince varyant yamamak bırakılıp **tek sektör
çapasıyla sınıf kapatıldı**.

# Verification

**Bu oturumda koşulan komutlar ve TAZE çıktıları (hepsi kontrolörün kendi koşumları):**

- `python -m pytest tests/ -q` → **4085 passed in 310.25s**, exit 0 (SON, `2097390`).
  Ara koşumlar: 4066 · 4076 · 4075 · 4078 · 4085. Taban 4002 → **+83 test**.
- **Mutasyon: 38 kapının 38'i** ayrı ayrı susturuldu, her biri hedef testini kırdı.
  Betikler: `mutasyon.py` · `mutasyon2.py` · `mutasyon3.py` · `mutasyon4.py` (oturum
  scratchpad'i; kalıcı DEĞİL).
  **SEKİZ tur SAHTE-YEŞİL geldi ve hepsi ayrıştırıldı:** ikisi GERÇEK boşluktu ve düzeltildi
  (kanıtlanamayan kapı tek kapıya birleştirildi · görüntü kapısı sırasını ölçen kendi testini
  aldı); altısı PROB kusuruydu ve prob düzeltilip yeniden ölçüldü.
- **`prompt_regression` 124 passed** — tek bayt fark yok.
- **Dört Codex turu KOŞTU** (`run_codex_scan`, base-review). Koşum sayıları stderr'den ölçüldü:
  **38 · 48 · 21 · 30** komut. Son tur `verdict: approve`.
- **Canlı veritabanı ölçümü (K-103(b), Step 6):** API kimliği `otomaix`, **superuser VE tablo
  sahibi**. Rapor: `docs/research/2026-09-10-k103b-etkin-yetki-olcumu.md`.
- Defter kapısı her commit'te `rc=0`; bir kez `rc=2` verdi (yanlış `Exec-Kind`) ve
  `--amend` ile düzeltildi.

**Denenmemiş / doğrulanmamış — dürüst liste:**

- **Uçtan uca CLI koşumu YAPILMADI.** Yazım/güncelleme/aktivasyon gerçek bir koşuda hiç
  çağrılmadı; tüm ölçümler fixture ile. İlk gerçek ölçüm Task 19.
- **Kilitlenme YOKLUĞU davranışsal olarak ölçülmedi — YAPISAL ölçüldü.** Bilinçli: yokluğu
  koşarak kanıtlamak döngünün gerçekleşmesini ummayı gerektirir, kırmızısı zamanlamaya bağlı
  olurdu. Sınırı aşağıda, Risks'te.
- **Denetçi web erişim probu YOK** — üretim hattı hâlâ koşamaz (K-14 her turu bloke eder).
- **`ruff` ve `pyright` bu ortamda koşmadı.**
- **CRM webhook onarımı YAPILMADI.** Canlıya migration dağıtılmadı; pilot koşulmadı.
- Task 16-20 hiç yazılmadı.
- **K-103(b) ölçümünün iki ayağı KOŞULAMADI:** iki jeton tablosu canlıda YOK (036
  dağıtılmadı), yani kolon-bazlı yetki ve o iki tablonun negatif yazma denemesi ölçülmedi.

# Risks

- **EN YÜKSEK (işletim) — kimlik doğrulamasız CRM webhook'ları onarılmadı, yalnız KAPATILDI.**
- **Üretim hattı hâlâ koşamaz:** denetçi web probu yok.
- **Köken jetonunun kalanı AÇIK ve kapatıldığı İDDİA EDİLMEZ.** Ölçüldü: API kimliği superuser
  ve tablo sahibi, yani `REVOKE` ile kapanmaz — ayrı bir veritabanı rolü ister.
  **Ev: Task 18 dağıtım listesi, M-1 ve M-2** (araştırma raporunda adıyla yazılı).
- **Kilit sözleşmesi KAYNAKTAKİ kilitleri modeller, veritabanının ZORLADIKLARINI değil.**
  Yabancı anahtar taşıyan bir satır yazıldığında ebeveyn paket satırına örtük kilit alınır ve
  tarayıcı onu göremez. Bugün o kenarların TERSİ yok (bağımsız hakem, tur 4 izledi) ama bu
  ölçüm KOŞUM-ANLIKTIR. Sınır `tests/test_lock_anchor_contract.py` başında yazılı.
  **Yeniden açılma koşulu:** ters bir kenar eklenirse test yeşil kalırken üretimde döngü doğar.
- **Taslağı kimin yazdırdığı KAYITLI DEĞİL — KAPSAM DIŞI (Eray kararı, 2026-09-10).**
  Dürüst etiket: çözülmedi, "halledildi" değil. **Yeniden açılma koşulu:** ikinci bir operatör
  eklendiğinde ya da paket üretimine müşteri/dış taraf eriştiğinde. Task 20 kapanış belgesine
  bu etiketle yazılır (plan Task 20 Step 6'nın "düşürme" kolu).
- **Atıf ADAYA bağlı DEĞİL** — sentezin atfı ALAN düzeyinde. Ev açık
  (`docs/active/denetci-atif-aday-kimligi/`), sert son tarih Task 19.
- **`BulguIzi`'nin dördüncü alanı arayüz ekinde sahipsiz.** Ev: arayüz eki revizyonu.
- **Sözleşme penceresi Task 19'da KAPANIYOR.** Bekleyen: atıf-aday kimliği + `BulguIzi` alan
  sahipliği + K-126 resmîlik ayağı + K-03 kategori ayağı.
- **Paket satırı kayma penceresi FAIL-CLOSED, KAPALI DEĞİL.** Kalıcı çözüm
  `sector-package-sector-id-immutability` (tetikli, ev kayıtlı). **Task 15 o kolona YAZICI
  EKLEMEDİ** — tetik koşulu bu turda da sınandı ve tutmadı.
- **Migration `036` yerinde düzenlendi** — kabul edilmiş risk.
- **Katı Bölüm C biçimi yanlış-pozitif üretebilir ve ÖLÇÜLMEDİ** (ilk gerçek ölçüm Task 19).
- **KABUL EDİLMİŞ RİSK (M3) — commit geçmişi tek-commit TDD modeline uymuyor.**
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`).
- **EVSİZ PARK — atomiklik sınıfı depo GENELİ** (değişmedi).

# Notes For Claude/Codex

**Süreç ağırlığı — Eray'ın talimatları, BAĞLAYICI:**
1. **Hakem bulgularından YALNIZ critical/high düzeltilir**; orta/düşük RAPORLANIR ve devam
   edilir. **İSTİSNANIN İSTİSNASI:** gerileme kontrolörün KENDİ ürünüyse ve iş üç satırsa
   devredilmez. **Bu oturumda ÜÇ kez uygulandı** (tek-kazanan oracle · silinen regresyon
   kapısı · aşırı-iddia daraltması).
2. Mutasyon kanıtı yalnız **YENİ** kapıya istenir; kanıtlanmış kapı tekrar ölçülmez.
3. İnceleme turu üretim/test diye **BÖLÜNMEZ** — tek tur.
4. Düzeltme brief'leri **KISA**.
5. **Aynı eksen üst üste turlarda varyant üretiyorsa yamamayı bırak**, çerçeve teşhisiyle
   kullanıcıya git. **Bu oturumun ANA DERSİ:** kilit ekseni iki tur varyant verdi; üçüncü turda
   hakemden ÇERÇEVE teşhisi istendi, alındı, Eray karar verdi, çözüm tur 4'te doğrulandı.
   Prompt'a "üçüncü kez bulursan spot bulgu olarak RAPORLAMA, çerçeve teşhisi ver" yazmak işe
   yaradı — hakem tam da onu döndü.

**YENİ — bu oturumda öğrenilenler, Task 16 dispatch'ine ZORUNLU:**
1. **TASARIM BELGESİNDE OLMAYAN İŞE BAŞLAMA.** Bu oturumda aktif katmandaki bir nota dayanıp
   planda/spec'te/spec girdisinde HİÇ geçmeyen bir şema değişikliği denendi; migration
   zincirinin sürüm-farkında kabul tabloları onu (haklı olarak) reddetti ve iş bütünüyle geri
   alındı. **Yürütmeye başlamadan ÖNCE ölç:** bu kalem spec girdisinde/spec'te/planda geçiyor
   mu, planın öngördüğü migration numaraları neler.
2. **Kilit çapası artık BAĞLAYICI bir sözleşmedir.** Paket satırına dokunan yeni her yol,
   herhangi bir satır kilidinden ÖNCE sektör çapasını alır. Sözleşme
   `tests/test_lock_anchor_contract.py`'te sınıf düzeyinde tutulur; muafiyet eklemek
   GEREKÇESİYLE görünür olur.
3. **Kanıt yalnız fabrikadan gelir.** Task 16'nın komutları kanıtı ELLE KURMAZ; yazım yüzeyi
   üzerinden geçerler. Elle kurulan kanıt hiçbir geçişten geçmez (jeton kapısı).
4. **Aktivasyonun tek üretim yolu anlık görüntü üzerindendir.** Ham yaşam döngüsü çağrısı
   içerik mührünü kontrol ETMEZ; adaptörler o yolu KULLANMAZ.
5. **Yol sıra numaraları KONUMSAL** — karşılaştıran her tüketici kimliğe anahtarlar, yola asla.
   Task 15 sürümler arası yol karşılaştıran bir tüketici ÜRETMEDİ (ölçüldü: turlar arası tek
   çapraz tüketici çıkarma SAYAR, yol eşleştirmez).
6. **Exec footer'ın iki mekanik kuralı.** `Exec-Kind` uzantıya değil YOL KÜMESİNE bakılarak
   seçilir — **bu oturumda bir kez ihlal edildi** (`docs-only` seçildi ama üretim dosyası
   docstring'i de değişmişti), defter kapısı `rc=2` ile yakaladı, `--amend` ile düzeltildi.
7. **Commit başlığı ≤72 karakter** — `git log -1 --format=%s | wc -c` ile SAY.
8. `Exec-Task` id'sini yazmadan ÖNCE defterde ARA — **pencere içinde**.
9. Her commit'ten SONRA defter kapısı koşulur (`ec_ledger_view … --post-window`, rc=0).
10. Uygulayıcı kendi alt-ajanını çağırmaz. **`docs/active/` altına yazmaz.**
11. **İSKELET ÖNCE — her testin kendi kırmızısı ayrı ölçülür.** Task 15'te **BEŞ testin**
    kendi kırmızısı yoktu ve öyle raporlandı: üçü zaten doğru olan bir özelliği kilitleyen
    regresyon kilidi, ikisi mutasyonla ölçülen yapısal/pozitif kontrol.
12. **Kapanış üretilmiş matrisle** kanıtlanır, **boş-küme kontrol kolu** eklenir.
13. **Gönderilen düzyazıya sayı yazma** — ya üreten komutu yanına koy, ya "doğrulanmadı" etiketle.
14. **Hakem/kontrolör önerisi ADAYDIR** — dosyayı açmadan tekrarlanmaz. Bu oturumda dört
    yüksek bulgunun dördü de kontrolörün KENDİ probuyla doğrulandı; biri (eşli yükümlülük
    iddiası) ölçülünce YANLIŞ çıktı.
15. **Kontrolörün tam test kümesi, veritabanına dokunan bir alt-ajanla ASLA üst üste binmez.**
16. Canlıya hiçbir n8n dosyası körlemesine yüklenmez.
17. **`git checkout -- <dosya>` KAYDEDİLMEMİŞ İŞİ SİLER.** Bu oturumda bir mutasyon denemesini
    geri alırken commit edilmemiş bir düzeltmeyi yok etti ve yeniden yazmak gerekti.

**Codex çağrısı kurarken — çağrıdan ÖNCE bas:**
1. `COMPANION` **ve** `PROMPT` **çağıran kabukta** kurulu mu (kabuk durumu taşınmaz).
2. `REQUIRED_CURRENT_FILES` SATIR SATIR mı — ve **dışlanan dosya var mı**.
3. Taban SHA 40 karakter mi. `CODEX_LOG` yazılabilir mi.
4. **Turun koştuğunu STDERR'den ölç:** `grep -c '^\[codex\] Running command'` **çağrının stderr
   çıktısında** — `$CODEX_LOG`'da DEĞİL.
5. **Uzun turları arka planda koştur.** `CSS_CALL_TIMEOUT` 1200s dört turda da YETTİ.
6. **Kota sınırı gerçek bir daldır.** Belirtisi: `rc=1` + `You've hit your usage limit` + kesik
   çıktı. **Üç şeyi birden kontrol et: `rc` · koşum sayısı · son cümlenin karar mı anlatı mı
   olduğu.** Bu oturumda dört turun dördü de `rc=0` ve kesintisizdi.
7. **Mutasyon probunun kendi deseni bayatlar ve YANILTIR.** Bu oturumda ALTI SAHTE-YEŞİL prob
   kusuru çıktı: mutasyon "taşımak" yerine "silmek" olduğunda iddia boşaldı; tarayıcı yorum
   satırlarını kod saydı; bir fonksiyonun KENDİ adını gövdesinde görmeyi dokunuş saydı.
   **Sahte-yeşil gelince ÖNCE probu sorgula.**

**Sır tarayıcısı yanlış alarmı (her oturumda yeniden onay ister).** Substrat şunları dışlıyor:
`tests/test_auditor_orchestration.py` · arayüz eki · `tests/test_plan2_interface_contract.py` ·
`sector_pipeline/runs.py` · `docs/tools/codex-scan-substrate-harness.sh`. Hepsi yanlış alarm.
Dördü de HEAD git nesnesinden OKUNABİLİYOR — hakeme gidecekse dışlanma coverage'da BEYAN EDİLİR
(dört turda dördü de okudu ve beyan etti).

**EVİ OLAN, TAŞINAN KALEMLER — rolling yeniden yazımda DÜŞÜRÜLMESİN:**
- **`markdown-it-py` bir ÜRETİM bağımlılığıdır** (pinli `4.2.0`), canlıya dağıtılmadı.
  **Ev: Task 18, Step 3.**
- **K-126 tek-kaynak istisnası KAPALI.** **Ev: arayüz eki revizyonu + denetçi sözleşmesi.**
- **K-03'ün kategori ayağı UYGULANMADI.** **Ev: arayüz eki revizyonu.**
- **`BulguIzi` dördüncü alanının sahipliği.** **Ev: arayüz eki revizyonu.**
- **Task 10'un TEST dosyaları bağımsız hakem GÖRMEDİ.** **Ev: Adım 11 final inceleme.**
- **Denetçi web probunun üretim sahibi Task 16'dır.**
- **Atıf ADAYA bağlanmalı.** **Ev: `docs/active/denetci-atif-aday-kimligi/` · son tarih Task 19.**
- **Ayrı veritabanı rolü (jeton kalanı).** **Ev: Task 18, M-1 + M-2** — araştırma raporunda yazılı.
- **`sector_packages.sector_id` değişmezliği.** **Ev: `sector-package-sector-id-immutability`
  (CURRENT.md, tetikli).** Tetik koşulu Task 15'te YENİDEN sınandı: bu görev o kolona yazıcı
  EKLEMEDİ, tetik hâlâ kapalı.
- **Kilit sözleşmesinin örtük-kenar sınırı.** **Ev: yok — dürüst etiketle KALAN RİSK**, yeniden
  açılma koşulu test dosyasının başında yazılı.
- **Taslak yazarı atfı — KAPSAM DIŞI, düşürüldü.** Yeniden açılma koşulu yazılı. **Task 20
  kapanış belgesine bu etiketle girer.**

**EVSİZ KALEM YOK.**

- **Eray'a teknik cümle onaylatma** — karar sorularını sade dille, proje-lokal kod referansı
  OLMADAN sor. **Bu oturumda bir kez ihlal edildi** (tablo adı sızdı), İlke-8 kapısı yakaladı
  ve soru yeniden yazıldı.
- **Karar sorusundan ÖNCE kaynakları oku.** Bu oturumun en pahalı hatası: "şimdi mi sonra mı"
  diye sorarken **planda yeri olup olmadığına bakılmamıştı**; karar için gereken en önemli
  bilgi eksik verildi ve iş geri alınmak zorunda kaldı.
- **TEHDİT MODELİNİ ÖNDEN SÖYLE.** Girdi araştırma çıktısıdır — ÖZENSİZ olabilir, SALDIRGAN
  değil. Dört turda da prompt'a konuldu ve bulguların hepsi doğru katmandan geldi.
- **Bu dosya ROLLING'dir** — her oturumda BAŞTAN yazılır; karar izi `TASK.md` Decisions Log'una gider.
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz (bu yazım hariç).
