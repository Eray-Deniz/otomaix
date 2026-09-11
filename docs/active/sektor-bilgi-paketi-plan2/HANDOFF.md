---
task: sektor-bilgi-paketi-plan2
written: 2026-09-11
---

# Resume From

**Sıradaki iş: DIŞ SÖZLEŞMENİN KOD UYARLAMASI.** Task 18'den ÖNCE gelir — sözleşme ilerledi,
kod ilerlemedi ve **ağaçta iki kırmızı test var** (bilinçli; aşağıda).

**İlk komut — kırmızıyı gör, listeyi oradan al:**
`cd apps/social/backend && .venv/bin/python -m pytest tests/ -q`
Beklenen: `4252 passed, 2 failed`. Düşen ikisi sapma alarmıdır ve uyarlanacak iki noktanın
adını söyler:
- `test_auditor_packaging.py::test_denetim_basligi_matches_pinned_contract_header`
- `test_brief_doctor.py::test_bolum_c_sabitleri_pinlenmis_sablondan_okunur`

**Uyarlama listesi (hiçbiri yazılmadı):**
1. `brief_doctor` — Bölüm C başlığı artık YEDİ sütun (`no` eklendi). Bugün yalnız yapısal
   sözleşme doğrulanıyor; **satır düzeyinde `no` + `alan/dönem` okunmalı** ki motor iddianın
   varlığını ve alanını doğrulayabilsin. **UYARI (ölçüldü):** sabiti değiştirmek
   `test_brief_doctor.py`'yi TOPLAMA aşamasında kırıyor — fixture satırları indeksle kuruluyor.
2. `auditors.validate_report` — denetim tablosu artık DOKUZ sütun (`kaynak-iddialari` eklendi);
   `_DENETIM_BASLIK_HUCRELERI` güncellenmeli ve sütun TİPLİ okunmalı. Ayrıca KAYNAK PROFİLİ
   düz yazıdan TABLOYA döndü (`kaynak | resmi | not`) — yeni bir tipli okuyucu ister.
3. Motor — `_alan_bagi_var` yerine **iddia bağı**: `ekle` kararının `kaynak_iddia`'sı, atıf
   yapılan denetçi satırının `kaynak-iddialari`'nda geçmeli VE araştırma raporunda o numara
   gerçekten olmalı (alanı da örtüşmeli).
4. **K-126 resmîlik ayağı** — `resmi` sütunu motorun tek-kaynak istisnası kapısına bağlanmalı.
5. **K-03 kategori ayağı** — DIŞ SÖZLEŞMEYE DOKUNMAZ. Kategori `social.public_holidays.category`
   kolonunda (ölçüldü); eksik olan onu `EngineInputs`'a taşımak = **R5 alan kümesi değişikliği**,
   yani arayüz eki revizyonu ister.
6. Arayüz eki R5 güncellemesi + yeni tiplerin sözleşmesi.

**Task 18 (ön-pilot dağıtım) BUNDAN SONRA.** Eray 2026-09-11'de canlıya bu oturumda
GİRMEME kararı verdi; o görevin senin elini gerektiren adımları önden listelenmiştir
(kalite kapısı · canlı migration · arka uç+CLI dağıtımı · n8n import · DB rol yetkisi).

**Dal:** `feat/sektor-bilgi-paketi-plan2`. Push durumu buraya YAZILMAZ, ölç:
`git rev-list --left-right --count origin/feat/sektor-bilgi-paketi-plan2...HEAD`.
**Yürütme durumu:** kip `inline` · başlangıç çapası `a806e29` · defter penceresi `a806e29`.
`cp_count` ve `last_checkpoint_ref` TASK.md'nin `Execution State` bölümündedir — KOPYALANMAZ.

**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: **BU OTURUMDA DEĞİŞTİ**
(`12beec1`). Pin monorepo'da `4636847` ile yenilendi.

## Bu oturum ne yaptı — tek cümle

Arayüz eki sekiz noktada koddan geride kalmıştı ve düzeltildi; F1 (onayın kanıta bağlanması)
Eray kararıyla fail-closed kapandı; dış araştırma sözleşmesi atıfı araştırma iddiasının
numarasına kadar bağlayacak biçimde revize edilip pinlendi — kod uyarlaması AÇIK.

# Verification

**Bu oturumda koşulan komutlar ve TAZE çıktıları (hepsi kontrolörün kendi koşumları):**

- `.venv/bin/python -m pytest tests/ -q` → **SON koşum: 4252 passed, 2 failed**, 320 s.
  Ara koşumlar: 4250 · 4252 · 4254 (hepsi exit 0, pin yenilenmeden ÖNCE).
  Taban 4234 → **+20 test** (F1). İki kırmızı pin yenilemesinin BİLİNÇLİ sonucudur.
  **Sanal ortam `.venv/bin/python`'dır**; çıplak `python` bu kabukta YOKTUR.
- **Ek↔kod sapma taraması** — ekin `python` bloklarında beyan ettiği **65 yüzey (32 blok)**
  kodla imza ve alan kümesi düzeyinde karşılaştırıldı. Fix'ten SONRA yeniden koştu:
  **kalan fark 0**. Betiğin ilk sürümü GÜRÜLTÜLÜYDÜ (docstring'den kelime topluyordu, 14
  aday); her aday tek tek dosyadan doğrulandı, 5'i gerçek çıktı.
- **Mutasyon: DOKUZ yeni kapı ayrı ayrı susturuldu, DOKUZU da hedef testini KIRDI.**
- **Canlı yerel veritabanı sorguları (çıkarım değil, ölçüm):**
  `sector_research_artifacts` → `..._append_only` tetikleyicisi `BEFORE DELETE OR UPDATE`
  (satır DÜŞEMEZ) · `sector_package_runs` tablosu yerelde **YOK** (036 hiçbir yere
  uygulanmadı) · `social.public_holidays.category` kolonu VAR.
- **Defter kapısı** her commit'ten sonra koşuldu → `rc=0` (dört kez).

**Denenmemiş / doğrulanmamış — dürüst liste:**

- **Kod uyarlaması HİÇ yazılmadı** (yukarıdaki altı kalem). İki kırmızı test bunun alarmıdır.
- **Uçtan uca CLI koşumu YAPILMADI.** Tüm ölçümler fixture ile; ilk gerçek koşum Task 19.
- **Yeni sözleşme biçiminde üretilmiş gerçek araştırma çıktısı YOK** — yeni sütunların
  araçlar tarafından düzgün doldurulup doldurulmayacağı ÖLÇÜLMEDİ. İlk ölçüm Task 19 Step 5.
- **Sözleşme revizyonunu BAĞIMSIZ HAKEM GÖRMEDİ.** Eray "hafif yol: sonunda tek hakem turu"
  dedi; o tur **HENÜZ KOŞMADI**. Kod uyarlamasıyla BİRLİKTE koşacak.
- **Arayüz eki revizyonunun (R-G1…R-G9) hakem turu da KOŞMADI** — aynı turda.
- **Taramanın DÜZ YAZI kolu kapsanmadı**; ekte düz yazıda beyan edilen yüzeyler için
  "sapma yok" İDDİA EDİLMEZ.
- **`ruff` ve `pyright` bu ortamda koşmadı.**
- **CRM webhook onarımı YAPILMADI.** Canlıya migration dağıtılmadı; pilot koşulmadı.
- Task 18-20 hiç yazılmadı.

# Risks

- **AĞAÇ KIRMIZI (bilinçli, EN YÜKSEK).** İki sapma alarmı düşüyor; kapanışı bir sonraki
  oturumun ilk işidir. Yarım uyarlama (sütunu ayrıştırıp TÜKETMEMEK) bundan DAHA kötüdür.
- **EN YÜKSEK (işletim) — kimlik doğrulamasız CRM webhook'ları onarılmadı, yalnız KAPATILDI.**
  Ev: `crm-webhooks-unauthenticated-sql-interpolation` (CURRENT.md, tetikli).
- **F1'in kapanmayan yarısı:** `attest_readiness` prob SONUÇLARINI görmez; gerçek kapı
  CLI'dadır ve "başka üretim çağıranı yok" iddiası artık testle pinli. Kapanış DEĞİL,
  adı konmuş sınır (R9 yasağı yüzünden).
- **Üretim hattı hâlâ koşamaz:** denetçi-2'nin web erişimi yok (araç gerçeği, kod değil).
- **Yeni sözleşme sütunları araçlar tarafından doldurulacak** — biçim disiplini ölçülmedi;
  katı biçim yanlış-pozitif üretebilir. İlk ölçüm Task 19.
- **Mekanik kapı raporunun artefakt türü şemada YOK** — `brief-doctor` alt komutu ham
  artefakt yazımında DÜŞER. **EV: Task 18 şema ayağı.**
- **Köken jetonunun kalanı AÇIK.** Ev: Task 18 dağıtım listesi, M-1 ve M-2.
- **Kilit sözleşmesi KAYNAKTAKİ kilitleri modeller**, veritabanının ZORLADIKLARINI değil.
- **`recovered` sorgusu bakım penceresini TAM modellemiyor** (kabul edilmiş risk).
- **Genel `ValueError` yakalama teşhisi yanlış yöne çekiyor** (kabul edilmiş risk).
- **Taslağı kimin yazdırdığı KAYITLI DEĞİL — KAPSAM DIŞI** (Eray kararı 2026-09-10);
  Task 20 kapanış belgesine bu etiketle girer.
- **Paket satırı kayma penceresi FAIL-CLOSED, KAPALI DEĞİL.** Tetik Task 17'de yeniden
  ölçüldü ve tutmadı.
- **Migration `036` yerinde düzenlendi** — kabul edilmiş risk.
- **KABUL EDİLMİŞ RİSK (M3) — commit geçmişi tek-commit TDD modeline uymuyor.**
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`).

# Notes For Claude/Codex

**Süreç ağırlığı — Eray'ın talimatları, BAĞLAYICI:**
1. **Hakem bulgularından YALNIZ critical/high düzeltilir**; orta/düşük RAPORLANIR.
   **İSTİSNANIN İSTİSNASI:** gerileme kontrolörün KENDİ ürünüyse düzeltilir.
2. Mutasyon kanıtı yalnız **YENİ** kapıya istenir.
3. İnceleme turu üretim/test diye **BÖLÜNMEZ** — tek tur.
4. Düzeltme brief'leri **KISA**.
5. **Aynı eksen üst üste turlarda varyant üretiyorsa yamamayı bırak**, çerçeve teşhisiyle
   kullanıcıya git. Bu oturumda atıf bağında aynen uygulandı ve Eray "tam bağ" dedi.

**BU OTURUMUN ANA DERSLERİ — bir sonraki dispatch'e ZORUNLU:**

1. **PROBUN KENDİSİ ÖLÇÜMÜ KİRLETEBİLİR.** Sapma taramasının ilk sürümü docstring'den
   kelime toplayıp 14 "sapma" üretti; gerçek sayı 5'ti. **Her aday dosyadan tek tek
   doğrulandı.** Üretilmiş listeye ham hâliyle güvenme.
2. **AÇIK SORUNUN TARİF ETTİĞİ ARIZA ÖLÇÜLMEDEN KABUL EDİLMEZ.** F1'in kaydı "onaydan sonra
   DÜŞEN satır" diyordu; canlı ölçüm o yolun veritabanı düzeyinde KAPALI olduğunu gösterdi.
   Gerçek açık başka yerdeydi (koşu satırının sekiz kolonu). Kapıyı yanlış yere kurmaktan
   yalnız ölçüm kurtardı.
3. **KAPSAMI, KORUNAN YARIYA DEĞİL AÇIK YARIYA GÖRE KUR.** Yalnız artefaktları kapsayan bir
   parmak izi, zaten en korunaklı yarıyı kapatıp korunmayanı açık bırakacaktı.
4. **ELLE LİSTE TUTMA, ÜRETİLMİŞ KÜME KUR.** Kanıt kolonları probların kaynağından AST ile
   türetilir; dedektörün kendi pozitif kontrolü de vardır (hiç okuma bulunmazsa test düşer).
5. **TEK UÇLU BAĞ KENDİNİ ONAYLAR.** Atıf bağı iki uçlu kuruldu çünkü iki beyanı da aynı
   model yazıyor; üçüncü taraf (mekanik ayrıştırıcı) olmadan zincir kapanmaz.
6. **FIXTURE'LAR İMKÂNSIZ BİR SIRAYI KODLAYABİLİR.** Hazırlık tasdiki yönetici onayından
   ÖNCE yazılıyordu; üretimde ulaşılamaz bir sıraydı ve yalnız kapı olmadığı için
   görünmüyordu. Yeni bir kapı eklerken kırılan fixture'a "testi düzelt" diye bakma —
   önce "bu sıra üretimde mümkün mü" diye sor.
7. **YARIM UYARLAMA, KIRMIZI ALARMDAN DAHA KÖTÜDÜR.** Sütunu ayrıştırıp tüketmemek sessiz
   bir ara durum yaratırdı. Kırmızı bırakıldı ve commit mesajında AÇIKÇA yazıldı.
8. **Exec footer'ın iki mekanik kuralı** — `Exec-Kind` uzantıya değil YOL KÜMESİNE bakılarak
   seçilir (`green-only` = tests kümesi BOŞ); `Exec-*` bloğu mesajın SON paragrafıdır.
9. **Commit başlığı ≤72 karakter** — `git log -1 --format=%s | wc -c` ile SAY.
10. `Exec-Task` id'sini yazmadan ÖNCE defterde ARA — **pencere içinde**.
11. Her commit'ten SONRA defter kapısı koşulur (`ec_ledger_view … --post-window`, rc=0).
12. Uygulayıcı kendi alt-ajanını çağırmaz.
13. **Gönderilen düzyazıya sayı yazma** — ya üreten komutu yanına koy, ya "doğrulanmadı"
    etiketle. Bu oturumda bir kez ihlal edildi ("bir ay" yazıldı, gerçek bir gündü) ve
    aynı turda düzeltildi.
14. Canlıya hiçbir n8n dosyası körlemesine yüklenmez.

**Codex çağrısı kurarken — çağrıdan ÖNCE bas:**
1. `COMPANION` **ve** `PROMPT` **çağıran kabukta** kurulu mu (kabuk durumu taşınmaz).
2. `REQUIRED_CURRENT_FILES` SATIR SATIR mı — ve **dışlanan dosya var mı**.
3. Taban SHA 40 karakter mi. `CODEX_LOG` yazılabilir mi.
4. **Turun koştuğunu STDERR'den ölç:** `grep -c '^\[codex\] Running command'` çağrının
   stderr çıktısında — `$CODEX_LOG`'da DEĞİL.
5. **Uzun turları arka planda koştur.** `CSS_CALL_TIMEOUT` 1200s yetti.
   Bekleme döngüsünü `codex-companion.mjs` ile eşleştir.
6. **Kota sınırı gerçek bir daldır.** Üçünü birden kontrol et: `rc` · koşum sayısı · son
   cümlenin karar mı anlatı mı olduğu.
7. **TEHDİT MODELİNİ ÖNDEN SÖYLE.**

**Sır tarayıcısı yanlış alarmı (her oturumda yeniden onay ister).** Substrat 60'tan fazla
dosyayı dışlıyor; hakem kapsam beyanını AÇIKÇA yapmalı. Beyan yoksa turun kapsamı eksiktir.

**EVİ OLAN, TAŞINAN KALEMLER — rolling yeniden yazımda DÜŞÜRÜLMESİN:**
- **Dış sözleşmenin KOD uyarlaması (YENİ).** **Ev: bir sonraki oturumun İLK İŞİ.**
- **Sözleşme + arayüz eki revizyonunun HAKEM TURU (YENİ).** **Ev: kod uyarlamasıyla
  AYNI tur** (Eray'ın "hafif yol" kararının ikinci yarısı — henüz ödenmedi).
- **K-126 resmîlik ayağının MOTOR tarafı.** **Ev: kod uyarlaması.**
- **K-03 kategori ayağı** (dış sözleşmeye dokunmaz; `EngineInputs` R5 değişikliği).
  **Ev: kod uyarlaması + arayüz eki.**
- **`markdown-it-py` bir ÜRETİM bağımlılığıdır** (pinli `4.2.0`), canlıya dağıtılmadı.
  **Ev: Task 18, Step 3.**
- **Mekanik kapı raporunun artefakt türü.** **Ev: Task 18 şema ayağı.**
- **Task 10'un TEST dosyaları bağımsız hakem GÖRMEDİ.** **Ev: Adım 11 final inceleme.**
- **Web probunun CANLI olumlu ölçümü.** **Ev: Task 19.**
- **Katı Bölüm C biçiminin yanlış-pozitif oranı ÖLÇÜLMEDİ.** **Ev: Task 19 Step 5.**
- **n8n hata bildiriminin sentetik arıza ile teslim ölçümü.** **Ev: Task 18.**
- **Ayrı veritabanı rolü (jeton kalanı).** **Ev: Task 18, M-1 + M-2.**
- **`sector_packages.sector_id` değişmezliği.** **Ev:
  `sector-package-sector-id-immutability` (CURRENT.md, tetikli).**
- **Kilit sözleşmesinin örtük-kenar sınırı — DÜŞÜRÜLDÜ, park EDİLMEDİ.** Yeniden açılma
  koşulu test dosyasının başında yazılı.
- **Taslak yazarı atfı — KAPSAM DIŞI, düşürüldü.** Task 20 kapanış belgesine bu etiketle girer.
- **Atomiklik sınıfı — DÜŞÜRÜLDÜ** (kapsam-dışı-by-design). Yeniden açılma koşulu: onaylı
  koşum yolu DIŞINDA bir migration uygulama yolu doğarsa.
- **`denetim`/`sentez`/`motor` davranış testi — DÜŞÜRÜLDÜ, park EDİLMEDİ.** Yeniden açılma
  koşulu: o gövdeler değişirse ya da Task 19'un ilk gerçek koşumu orada kusur gösterirse.
- **Ek↔kod sapmasının DÜZ YAZI kolu — DÜŞÜRÜLDÜ, park EDİLMEDİ (YENİ).** Dürüst etiket:
  serbest metinden imza çıkaran bir kapı yanlış-pozitif ile kaçırma arasında salınır
  (semantik-negatif sınıfı). **Yeniden açılma koşulu:** ekin bağlayıcı yüzeyleri "yalnız kod
  bloğunda beyan edilir, düz yazı yalnız ATIF yapar" kuralına bağlanırsa — o zaman üretilmiş
  kapı yazılabilir hâle gelir.

**EVSİZ KALEM: YOK.** Bu oturumda doğan dört yeni kalemin dördüne de ev verildi (kod
uyarlaması · hakem turu · K-126 motor ayağı · K-03 kategori ayağı); düşürülen tek kalemin
(düz yazı kolu) yeniden açılma koşulu yazılı.

- **Eray'a teknik cümle onaylatma** — karar soruları sade dille, proje-lokal kod referansı
  OLMADAN sorulur. Bu oturumda üç karar sorusu soruldu; üçü de sade dilde, ölçülmüş bedelli
  ve önerili sunuldu (F1 mekanizması · tur şekli · atıf bağının sıkılığı).
- **Bu dosya ROLLING'dir** — her oturumda BAŞTAN yazılır; karar izi `TASK.md` Decisions Log'una gider.
- Diskte bekleyen düzeltme YOK; çalışma ağacı bu yazım dışında temiz.
