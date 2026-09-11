---
task: sektor-bilgi-paketi-plan2
written: 2026-09-11
---

# Resume From

**Sıradaki iş: Task 18** (ön-pilot dağıtım — şema · arka uç · CLI · adaptör · workflow'lar).
Task 17 indi ve **checkpoint 14 `approve` ile kapandı** (beş hakem turu).

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

**Task 18 CANLI SİSTEME dokunur** (migration dağıtımı · üretim bağımlılığı · n8n yüklemesi).
Eray 2026-09-11'de oraya bu oturumda GİRMEME kararı verdi. Açılışta ilk iş, o görevin hangi
adımlarının onun elini gerektirdiğini ÖNDEN listelemektir — adım adım onay istemek değil.

## Bu oturum ne yaptı — tek cümle

Task 17 (işletime hazırlık kontrol listesi kapısı) uçtan uca yazıldı ve beş hakem turuyla
kapandı; ayrıca dispatch sırasında ölçülen, hattı ilk gerçek koşumda düşürecek bir artefakt
türü kusurunun iki ayağı kapatıldı.

# Verification

**Bu oturumda koşulan komutlar ve TAZE çıktıları (hepsi kontrolörün kendi koşumları):**

- `.venv/bin/python -m pytest tests/ -q` → **4234 passed**, exit 0 (SON, `4a9d98f`).
  Ara koşumlar: 4152 · 4160 · 4174 · 4175 · 4228 · 4234. Taban 4134 → **+100 test**.
  **Sanal ortam `.venv/bin/python`'dır**; çıplak `python` bu kabukta YOKTUR, `python3` ise
  bağımlılıkları görmez (`fastapi` bulunamaz) — ilk koşumda buna takıldım.
- **Beş Codex turu KOŞTU** (`run_codex_scan`, base-review). Koşum sayıları **stderr'den**
  ölçüldü: **28 · 27 · 26 · 29 · 22**. Beşi de `rc=0` ve kesintisiz. Son tur
  `verdict: approve`, **bulgu YOK**.
- **Mutasyon:** bu oturumda AÇILAN her yeni kapı ayrı ayrı susturuldu ve hedef testini kırdı
  (17 mutasyon; hepsi KIRILDI). **Biri ilk yazımda SAHTE YEŞİLDİ** ve mutasyonla yakalandı —
  ayrıntı aşağıda, Notes 2.
- **Canlı yerel veritabanına sorgu:** `sector_research_artifacts_kind_check` tanımı okundu
  (`research` · `review` · `synthesis`) — artefakt türü kusurunun kanıtı budur, çıkarım değil.
- **Defter kapısı** her commit'ten sonra koşuldu: `ec_ledger_view a806e29 … --post-window`
  → `rc=0`.
- **Tetik koşulu YENİDEN ölçüldü:** `sector_packages` tablosuna YAZIM arandı
  (`grep -E "(INSERT INTO|UPDATE) social\.sector_packages"` — `readiness.py` + CLI) → **boş**;
  `sector-package-sector-id-immutability` tetiği hâlâ KAPALI.

**Denenmemiş / doğrulanmamış — dürüst liste:**

- **Uçtan uca CLI koşumu YAPILMADI.** Tüm ölçümler fixture ile; ilk gerçek koşum Task 19.
- **`hazirlik-onayla` canlıda hiç koşmadı** — yazdığı tasdiği aktivasyonun okuduğu ZİNCİR uçtan
  uca sınanmadı; iki uç ayrı ayrı testli.
- **Eşzamanlılık DAVRANIŞSAL olarak ölçülmedi.** Onay yolundaki kilit ve tazelik kapısı YAPISAL
  testlerle bağlandı; iki bağlantılı gerçek yarış testi YAZILMADI — hakem bunu F1'in kapanış
  koşulu olarak istiyor.
- **Web probunun OLUMLU yolu CANLI koşulmadı.** İlk canlı ölçüm Task 19.
- **`denetim` / `sentez` / `motor` gövdelerinin DAVRANIŞ testi YOK** (planın Step 1 listesi
  istemiyor — düşürüldü, aşağıda).
- **`ruff` ve `pyright` bu ortamda koşmadı.**
- **CRM webhook onarımı YAPILMADI.** Canlıya migration dağıtılmadı; pilot koşulmadı.
- Task 18-20 hiç yazılmadı.

# Risks

- **EN YÜKSEK (işletim) — kimlik doğrulamasız CRM webhook'ları onarılmadı, yalnız KAPATILDI.**
  Ev: `crm-webhooks-unauthenticated-sql-interpolation` — CURRENT.md'de `proposed`, tetikli.
- **Hazırlık onayı mühürlenmiş kanıt kümesine bağlı DEĞİL (checkpoint 14 · F1, yüksek).**
  Daraltıldı (tek işlem + satır kilidi + yazım öncesi taze parmak izi); KAPANMADI. Onaydan
  SONRA düşen bir artefakt satırı damgayı hâlâ geçerli gösterir ve `runs.attest_readiness`
  prob sonuçlarını görmez. **EV: arayüz eki revizyonu · son tarih Task 19.** Tam kaydı
  TASK.md Open Problems'ta.
- **Üretim hattı hâlâ koşamaz:** denetçi-2'nin web erişimi yok (araç gerçeği, kod değil).
- **Bağlayıcı ek İKİ noktada KODLA IRAKSIYOR:** AÇIK-2 (`geri-al` kaldırıldı) ve
  `readiness.evaluate` imzası. İkisi de kayıtlı, ikisinin de evi arayüz eki revizyonu.
- **Mekanik kapı raporunun artefakt türü şemada YOK** — `brief-doctor` alt komutu ham artefakt
  yazımında DÜŞER. **EV: Task 18 şema ayağı** (Eray kararı 2026-09-11).
- **Köken jetonunun kalanı AÇIK.** Ev: Task 18 dağıtım listesi, M-1 ve M-2.
- **Kilit sözleşmesi KAYNAKTAKİ kilitleri modeller, veritabanının ZORLADIKLARINI değil.**
  Yeniden açılma koşulu `tests/test_lock_anchor_contract.py` başında yazılı.
- **`recovered` sorgusu bakım penceresini TAM modellemiyor** (kabul edilmiş risk).
- **Genel `ValueError` yakalama teşhisi yanlış yöne çekiyor** (kabul edilmiş risk).
- **Taslağı kimin yazdırdığı KAYITLI DEĞİL — KAPSAM DIŞI** (Eray kararı, 2026-09-10);
  Task 20 kapanış belgesine bu etiketle girer.
- **Atıf ADAYA bağlı DEĞİL.** Ev: `docs/active/denetci-atif-aday-kimligi/`, son tarih Task 19.
- **Sözleşme penceresi Task 19'da KAPANIYOR.** Bekleyen: atıf-aday kimliği · `BulguIzi` alan
  sahipliği · K-126 resmîlik ayağı · K-03 kategori ayağı · AÇIK-2 · **F1 · `evaluate` imzası**.
- **Paket satırı kayma penceresi FAIL-CLOSED, KAPALI DEĞİL.** Tetik bu oturumda yeniden ölçüldü
  ve tutmadı (yukarıda, Verification).
- **Migration `036` yerinde düzenlendi** — kabul edilmiş risk.
- **KABUL EDİLMİŞ RİSK (M3) — commit geçmişi tek-commit TDD modeline uymuyor.**
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`).

# Notes For Claude/Codex

**Süreç ağırlığı — Eray'ın talimatları, BAĞLAYICI:**
1. **Hakem bulgularından YALNIZ critical/high düzeltilir**; orta/düşük RAPORLANIR.
   **İSTİSNANIN İSTİSNASI:** gerileme kontrolörün KENDİ ürünüyse düzeltilir — bu oturumda İKİ
   orta bu kuralla düzeltildi (ikisi de bu turda benim açtığım kusurdu).
2. Mutasyon kanıtı yalnız **YENİ** kapıya istenir.
3. İnceleme turu üretim/test diye **BÖLÜNMEZ** — tek tur.
4. Düzeltme brief'leri **KISA**.
5. **Aynı eksen üst üste turlarda varyant üretiyorsa yamamayı bırak**, çerçeve teşhisiyle
   kullanıcıya git. **Bu oturumda uygulandı ve DOĞRUYDU:** F1 iki turda aynı ekseni gösterince
   üçüncü spot-fix açılmadı, Eray'a çerçeve götürüldü, o "daralt + tarihli ev" dedi.

**BU OTURUMUN ANA DERSLERİ — Task 18 dispatch'ine ZORUNLU:**

1. **KAYNAĞI OKUMADAN TASARIM SORUSU SORMA — bu kez UYULDU.** Task 17'ye girmeden spec girdisi
   (§13.4 tablosu), spec, plan, bağlayıcı ek ve mevcut `readiness_items` okundu; ekin Task 17'yi
   yeniden yazan bölümü (R9/H5) plandan ÖNCE geldi ve `readiness.attest` yüzeyinin SİLİNMİŞ
   olduğu oradan görüldü. Plan metnine güvenip yazsaydım olmayan bir yüzeyi üretecektim.
2. **MUTASYON SAHTE YEŞİLİ YAKALAR.** Bu oturumda bir kez yakalandı: `sinyal` maddesinin kapıyı
   kapatmadığını iddia eden test koşu üzerinden ölçüyordu; bugünkü tek sinyal maddesi `elle`
   olduğu için durumu hiç `gecmedi` olamıyor, yani sınıf filtresi KODDAN TAMAMEN SİLİNSE BİLE
   test geçiyordu. Test, özelliği SINAYABİLEN yere (raporun kendi kapısına) taşındı.
   **KURAL: yeni kapıyı yazdıktan sonra sustur ve testin gerçekten kırıldığını GÖR.**
3. **Kural yazma, DEĞİŞMEZ kur.** Artefakt türü kapısı önce bir test taraması olarak yazıldı;
   hakem taramanın kör noktalarını (takma ad · `**kwargs`) gösterdi. Çözüm taramayı büyütmek
   DEĞİL, kuralı yazıcının içine koymaktı. Aynı desen tip kapılarında da uygulandı: doğrulama
   okuyucuya değil veri sınıfının `__post_init__`'ine kondu.
4. **Kapanışı elle seçilmiş örnekle değil ÜRETİLMİŞ matrisle kanıtla.** Sözleşme tipleri için
   59 vakalık matris (her alan × her yanlış tip + `str` alt sınıfı + eşitlik taklidi) yazıldı.
5. **ÖLÇMEDEN "YOK" DEME.** Bu oturumda iddia edilen her yokluk komutla ölçüldü: canlı kısıt
   tanımı, tasarım belgelerinde artefakt türü taksonomisinin yokluğu, `sector_packages`
   tetiğinin kapalılığı.
6. **Kapsam dışına çıkacaksan ÖNDEN görünür sor.** Bu oturumda bir kez gerekti (artefakt türü
   kusuru Task 16'nın ürünü) — sorulunca Eray iki ayağı şimdi, üçüncüyü Task 18'e dedi.
7. **Exec footer'ın iki mekanik kuralı** — `Exec-Kind` uzantıya değil YOL KÜMESİNE bakılarak
   seçilir; `Exec-*` bloğu mesajın SON paragrafıdır. Bu oturumda ihlal YOK.
8. **Commit başlığı ≤72 karakter** — `git log -1 --format=%s | wc -c` ile SAY.
9. `Exec-Task` id'sini yazmadan ÖNCE defterde ARA — **pencere içinde**.
10. Her commit'ten SONRA defter kapısı koşulur (`ec_ledger_view … --post-window`, rc=0).
11. Uygulayıcı kendi alt-ajanını çağırmaz.
12. **İSKELET ÖNCE — her testin kendi kırmızısı ayrı ölçülür.** Uygulandı: modül ve komut
    iskeleti kuruldu, 8 test kendi kırmızısını verdi, 4'ü iskeletin gerçek parçası olduğu için
    yeşil geldi ve raporda öyle söylendi.
13. **Gönderilen düzyazıya sayı yazma** — ya üreten komutu yanına koy, ya "doğrulanmadı" etiketle.
14. **Hakem/kontrolör önerisi ADAYDIR** — dosyayı açmadan tekrarlanmaz. Beş bulgunun beşi de
    kontrolörün KENDİ probuyla doğrulandı; ikisi canlı ölçümle.
15. **`geri-al` KALDIRILDI** — komut sessizce geri eklenirse kapanmamış yarış da geri gelir.
16. Canlıya hiçbir n8n dosyası körlemesine yüklenmez.
17. **Beş turun beşi de kusur buldu.** Bu zincirde "muhtemelen temizdir" varsayımı bugüne dek
    hep yanlış çıktı; kapanış turunu atlama önerisi getirirken bunu hatırla.

**Codex çağrısı kurarken — çağrıdan ÖNCE bas:**
1. `COMPANION` **ve** `PROMPT` **çağıran kabukta** kurulu mu (kabuk durumu taşınmaz).
2. `REQUIRED_CURRENT_FILES` SATIR SATIR mı — ve **dışlanan dosya var mı**.
3. Taban SHA 40 karakter mi. `CODEX_LOG` yazılabilir mi.
4. **Turun koştuğunu STDERR'den ölç:** `grep -c '^\[codex\] Running command'` **çağrının stderr
   çıktısında** — `$CODEX_LOG`'da DEĞİL.
5. **Uzun turları arka planda koştur.** `CSS_CALL_TIMEOUT` 1200s beş turda da YETTİ.
   **Bekleme döngüsünü `codex-companion.mjs` ile eşleştir**; betiğin adıyla `pgrep` yaparsan
   beklemenin KENDİ komut satırı eşleşir ve döngü hiç bitmez (bu oturumda bir kez oldu).
6. **Kota sınırı gerçek bir daldır.** Üçünü birden kontrol et: `rc` · koşum sayısı · son cümlenin
   karar mı anlatı mı olduğu.
7. **TEHDİT MODELİNİ ÖNDEN SÖYLE.** Beş turda da prompt'a konuldu.

**Sır tarayıcısı yanlış alarmı (her oturumda yeniden onay ister).** Substrat 60'tan fazla dosyayı
dışlıyor; bu oturumda **`runs.py` · `writeback.py` · `test_pipeline_runs.py` ·
`test_pipeline_writeback.py` · bağlayıcı ek** de dışarıdaydı. Hepsi yanlış alarm; hakem onları
HEAD git nesnelerinden okudu ve kapsam beyanında AÇIKÇA söyledi. Beyan yoksa turun kapsamı
eksiktir — kontrol et.

**EVİ OLAN, TAŞINAN KALEMLER — rolling yeniden yazımda DÜŞÜRÜLMESİN:**
- **`markdown-it-py` bir ÜRETİM bağımlılığıdır** (pinli `4.2.0`), canlıya dağıtılmadı.
  **Ev: Task 18, Step 3.**
- **Mekanik kapı raporunun artefakt türü (YENİ).** **Ev: Task 18 şema ayağı.**
- **K-126 tek-kaynak istisnası KAPALI.** **Ev: arayüz eki revizyonu.**
- **K-03'ün kategori ayağı UYGULANMADI.** **Ev: arayüz eki revizyonu.**
- **`BulguIzi` dördüncü alanının sahipliği.** **Ev: arayüz eki revizyonu.**
- **AÇIK-2 uzlaştırması.** **Ev: arayüz eki revizyonu · son tarih Task 19.**
- **`readiness.evaluate` imza ıraksaması (YENİ).** **Ev: arayüz eki revizyonu · son tarih Task 19.**
- **F1 — onay ↔ mühürlenmiş kanıt bağı (YENİ).** **Ev: arayüz eki revizyonu · son tarih Task 19.**
- **Task 10'un TEST dosyaları bağımsız hakem GÖRMEDİ.** **Ev: Adım 11 final inceleme.**
- **Web probunun CANLI olumlu ölçümü.** **Ev: Task 19.**
- **n8n hata bildiriminin sentetik arıza ile teslim ölçümü.** **Ev: Task 18.**
- **Atıf ADAYA bağlanmalı.** **Ev: `docs/active/denetci-atif-aday-kimligi/` · son tarih Task 19.**
- **Ayrı veritabanı rolü (jeton kalanı).** **Ev: Task 18, M-1 + M-2.**
- **`sector_packages.sector_id` değişmezliği.** **Ev: `sector-package-sector-id-immutability`
  (CURRENT.md, tetikli).** Tetik koşulu Task 17'de YENİDEN ölçüldü ve tutmadı.
- **Katı Bölüm C biçimi yanlış-pozitif üretebilir ve ÖLÇÜLMEDİ.** **Ev: Task 19.**
- **Kilit sözleşmesinin örtük-kenar sınırı — DÜŞÜRÜLDÜ, park EDİLMEDİ.** Yeniden açılma koşulu
  test dosyasının başında yazılı.
- **Taslak yazarı atfı — KAPSAM DIŞI, düşürüldü.** **Task 20 kapanış belgesine bu etiketle girer.**
- **Atomiklik sınıfı — DÜŞÜRÜLDÜ** (kapsam-dışı-by-design). Yeniden açılma koşulu: onaylı koşum
  yolu DIŞINDA bir migration uygulama yolu doğarsa.
- **`denetim`/`sentez`/`motor` davranış testi — DÜŞÜRÜLDÜ, park EDİLMEDİ.** Yeniden açılma
  koşulu: o gövdeler değişirse ya da Task 19'un ilk gerçek koşumu orada kusur gösterirse.
- **Eşzamanlılık DAVRANIŞ testi (iki bağlantılı yarış) — DÜŞÜRÜLDÜ, park EDİLMEDİ (YENİ).**
  Dürüst etiket: F1'in kapanış koşuludur ve F1'in evi arayüz eki revizyonudur; testi ondan ÖNCE
  yazmak, henüz kararı verilmemiş bir mekanizmayı kilitlemek olurdu. **Yeniden açılma koşulu:**
  F1 kararı verildiğinde, aynı partide.

**EVSİZ KALEM: YOK.** Geçen oturumun tek evsiz kalemi (arşivdeki bot token'ı) 2026-09-11'de
kapandı: zaten döndürülmüş bir token'ın ölü dizisiydi. Bu oturumda doğan üç yeni kalemin üçüne
de TARİHLİ ev verildi (Task 18 · Task 19 · Task 19).

- **Eray'a teknik cümle onaylatma** — karar sorularını sade dille, proje-lokal kod referansı
  OLMADAN sor. Bu oturumda üç karar sorusu soruldu; üçü de sade dilde, ölçülmüş bedelli ve
  önerili sunuldu.
- **Bu dosya ROLLING'dir** — her oturumda BAŞTAN yazılır; karar izi `TASK.md` Decisions Log'una gider.
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz (bu yazım hariç).
