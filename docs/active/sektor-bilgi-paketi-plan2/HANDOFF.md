---
task: sektor-bilgi-paketi-plan2
written: 2026-09-11
---

# Resume From

**Sıradaki iş: DIŞ SÖZLEŞME TURU — üç borç TEK revizyonda.** Task 18'den ÖNCE gelir
(Eray kararı 2026-09-11). Tam gövde `TASK.md` `# Open Problems`'ın ilk kaleminde.

**Neden tek tur:** üçü de aynı sınıftan — *sözleşme bugün taşımadığı bir KİMLİĞİ taşımadıkça
kod onu uyduramaz.* Ayrı ayrı kapatmak sözleşme-turu makinesini (dış depo commit → pin →
kod uyarlaması → hakem turu) üç kez çalıştırmak demek.

**Neden ŞİMDİ:** pencere bugün BEDELSİZ — araştırmalar bu biçimde henüz ÜRETİLMEDİ. Pilot
(Task 19) araştırma ürettiği an kapanır ve aynı değişiklik BÜTÜN araştırmaları ikinci kez
ürettirir. Uyarı sözleşmenin kendi commit mesajında yazılı (`12beec1`).

**Üç kalem:**
1. Bölüm C dönem satırı **kanonik sistem anahtarı** taşımalı (bugün günlük dil ↔ sistem adı
   köprüsü yok; ölçüldü: 15 aday adın yalnız 4'ü eşleşiyor). Bedeli: bu kapanana kadar
   Görev B eklemelerinin pratikte tamamı reddedilir.
2. URL örneklem satırı **iddia numarası** taşımalı (`K<kaynak>#<iddia>`); K-126'nın ikinci
   ayağı bugün kaynak düzeyinde ve beyan edildiğinden zayıf.
3. **Üçüncü not sınıfı** yetkilendirilmeli; K-03 çatışması bu yüzden karar günlüğüne
   yazılamıyor ve bugün hiçbir operatör yüzeyine ulaşmıyor (N2).

**İlk komut — tabanı gör:**
`cd apps/social/backend && .venv/bin/python -m pytest tests/ -q` → beklenen `4335 passed`.

**Task 18 (ön-pilot dağıtım) BUNDAN SONRA.** Canlıya girme kararı hâlâ Eray'da.

**Dal:** `feat/sektor-bilgi-paketi-plan2`. Push durumu buraya YAZILMAZ, ölç:
`git rev-list --left-right --count origin/feat/sektor-bilgi-paketi-plan2...HEAD`.
**Yürütme durumu:** kip `inline` · başlangıç çapası `a806e29` · defter penceresi `a806e29`.

**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi` @ `12beec1`; pin monorepo'da
`4636847`. Üç dosyanın sha256'sı pinle byte-eşit (hakem turunda iki kez ayrı ayrı doğrulandı).

## Bu oturum ne yaptı — tek cümle

Dış sözleşmenin kod uyarlaması altı kalemde yazıldı, iki dual hakem turundan geçti (attempt-1 +
kapanış) ve kod içinde kapanabilen her bulgu kapatıldı; kapanamayan üç ayak tek bir sözleşme
turuna EV olarak taşındı.

# Verification

**Bu oturumda koşulan komutlar ve TAZE çıktıları (hepsi kontrolörün kendi koşumları):**

- `.venv/bin/python -m pytest tests/ -q` → **SON koşum: 4335 passed, exit 0**, 316 s.
  Ara koşumlar: 4301 · 4306 · 4307 · 4323 · 4333. Taban 4252 passed + 2 failed
  (iki sapma alarmı) → **+83 test, kırmızılar kapandı.**
  **Sanal ortam `.venv/bin/python`'dır**; çıplak `python` bu kabukta YOKTUR.
- **Mutasyon — toplam ON SEKİZ yeni kapı ayrı ayrı susturuldu.** İlk partide 8/8 kırıldı;
  düzeltme partisinde 7/7; kapanış partisinde 3/3. **İKİ kez sağ kalan oldu ve ikisi de
  gerçek boşluktu:** (a) biçim kapısının boş-hücre kolu — test yalnız sütun adını arıyordu ve
  tutarlılık mesajı da o adı taşıyor; (b) F2'nin ikinci katmanı — birinci katman ayaktayken
  erişilemiyordu. İkisi de düzeltilip yeniden ölçüldü.
- **İki DUAL hakem turu** (fresh Claude subagent + Codex), ikisi de pinli worktree'de:
  attempt-1 → 1 critical + 4 high + 2 medium + 3 low; kapanış → yeni critical YOK,
  7 yeni bulgu (Codex rc=0/49 koşum · alt-hakem 58 araç çağrısı).
- **Canlı yerel veritabanı sorguları:** `social.public_holidays` kategori dağılımı
  (`religious` 9 · `national` 8 · `commercial` 5) ve 22 `name_tr` değeri;
  `normalize_special_day_key` çıktıları tek tek ölçüldü.
- **Defter kapısı** her commit'ten sonra koşuldu → `rc=0` (üç kez).

**Denenmemiş / doğrulanmamış — dürüst liste:**

- **Uçtan uca CLI koşumu YAPILMADI.** Tüm ölçümler fixture ile; ilk gerçek koşum Task 19.
- **Yeni sözleşme biçiminde üretilmiş gerçek araştırma çıktısı YOK** — yeni sütunların
  araçlar tarafından düzgün doldurulup doldurulmayacağı ÖLÇÜLMEDİ. İlk ölçüm Task 19 Step 5.
- **Kapanış partisinin kendisini bağımsız hakem GÖRMEDİ** (attempt-3 koşmadı).
- **Review defteri (ledger locator) KURULMADI** — sözleşme aynılığı hash'le değil kurulum
  gereğiyle taşındı. Sonraki turlarda kurulmalı.
- **`ruff` ve `pyright` bu ortamda YOK, koşmadı.**
- **CRM webhook onarımı YAPILMADI.** Canlıya migration dağıtılmadı; pilot koşulmadı.
- Task 18-20 hiç yazılmadı.

# Risks

- **EN YÜKSEK (işlevsel) — Görev B eklemeleri bugün PRATİKTE TAMAMEN reddediliyor.**
  Fail-closed ve teşhis dürüst, ama pilot bu hâliyle koşarsa paketin özel gün yarısı boş gelir.
  Ev: sözleşme turu kalem 1.
- **K-126 istisnası AÇIK ama ikinci ayağı ZAYIF** — URL doğrulaması iddiaya değil kaynağa bağlı.
  Ev: sözleşme turu kalem 2.
- **K-03 çatışması hiçbir operatör yüzeyine ULAŞMIYOR** — kayıt yalnız denetim içindir
  (Eray kararı B: geçici tüketici eklenmedi). Ev: sözleşme turu kalem 3.
- **EN YÜKSEK (işletim) — kimlik doğrulamasız CRM webhook'ları onarılmadı, yalnız KAPATILDI.**
  Ev: `crm-webhooks-unauthenticated-sql-interpolation` (CURRENT.md, tetikli).
- **F1'in kapanmayan yarısı:** `attest_readiness` prob SONUÇLARINI görmez; gerçek kapı
  CLI'dadır ve "başka üretim çağıranı yok" iddiası testle pinli. Adı konmuş sınır (R9).
- **Üretim hattı hâlâ koşamaz:** denetçi-2'nin web erişimi yok (araç gerçeği, kod değil).
- **Yeni sözleşme sütunları araçlar tarafından doldurulacak** — biçim disiplini ölçülmedi;
  katı biçim yanlış-pozitif üretebilir. İlk ölçüm Task 19.
- **Mekanik kapı raporunun artefakt türü şemada YOK.** EV: Task 18 şema ayağı.
- **Köken jetonunun kalanı AÇIK.** Ev: Task 18 dağıtım listesi, M-1 ve M-2.
- **Kilit sözleşmesi KAYNAKTAKİ kilitleri modeller**, veritabanının ZORLADIKLARINI değil.
- **`recovered` sorgusu bakım penceresini TAM modellemiyor** (kabul edilmiş risk).
- **Genel `ValueError` yakalama teşhisi yanlış yöne çekiyor** (kabul edilmiş risk).
- **Taslağı kimin yazdırdığı KAYITLI DEĞİL — KAPSAM DIŞI** (Eray kararı 2026-09-10).
- **Paket satırı kayma penceresi FAIL-CLOSED, KAPALI DEĞİL.**
- **Migration `036` yerinde düzenlendi** — kabul edilmiş risk.
- **KABUL EDİLMİŞ RİSK (M3) — commit geçmişi tek-commit TDD modeline uymuyor.**
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`).

# Notes For Claude/Codex

**HAKEM TURUNDAN GELEN — BİR SONRAKİ OTURUMUN GİRDİSİ (2026-09-11):**

Dış sözleşmenin kod uyarlaması indi ve **iki dual hakem turundan** geçti (attempt-1 + kapanış).
On adlandırılmış bulgunun yedisi tam kapandı, biri davranış ayağıyla kapandı; kapanış turunda
doğan yedi yeni bulgunun altısı kapandı. **Hiçbir bulgu gerilemedi; contract-widening talep
edilmedi.** Raporlar: `docs/reviews/2026-09-11-feat-sektor-bilgi-paketi-plan2.md` ve
`…-closure.md`.

**SIRADAKİ İŞ: DIŞ SÖZLEŞME TURU — üç borç TEK revizyonda** (Eray kararı). Tam gövde TASK.md
`# Open Problems`'ın ilk kaleminde; özet: Bölüm C dönem satırı kanonik sistem anahtarı taşımalı ·
URL örneklem satırı iddia numarası taşımalı · üçüncü not sınıfı yetkilendirilmeli.
**Pencere BEDELSİZ ama kapanıyor:** pilot araştırma ürettiği an aynı değişiklik bütün
araştırmaları ikinci kez ürettirir.

**EVSİZ KALEM: YOK — oturum kapanışında tek tek tarandı (2026-09-11).**
Bu oturumda doğan/ertelenen dört kalemin dördüne de GERÇEK ev verildi:
1. **Üç sözleşme borcu** (F3 · F4 · F1 günlük ayağı) → `TASK.md` `# Open Problems` kalem 1;
   tetik **Task 18'den ÖNCE**, pencere pilot araştırma üretimiyle kapanıyor.
2. **N2** (çatışma operatöre ulaşmıyor) → aynı sözleşme turunun 3. kalemi; Eray kararı B yazılı.
3. **Kapanış partisini bağımsız hakem görmedi (attempt-3 koşmadı)** → **EV: dalın FİNAL
   incelemesi** (plan Adım 11 / `finish-branch` kapanış denetimi). Taban `execute_start_ref`
   = `a806e29` ve ÖLÇÜLDÜ: bu taban bugünkü commit'lerin HEPSİNİ kapsıyor (230 commit).
   Yani kalem kendiliğinden o turun kapsamına giriyor — söz değil, mekanik.
4. **Review defteri (ledger locator) kurulmadı** → **EV: bir sonraki `/review-claude-codex`
   turunun Adım 1'i.** Bu turda atlandı ve sonucu şu oldu: kapanış turu sözleşme aynılığını
   HASH'le değil kurulum gereğiyle taşıdı. Sonraki tur defteri kurmazsa aynı boşluk sürer.

**Bu turun kalıcı dersleri — bir sonraki dispatch'e:**
1. **`run_checks` yeşil, `decide()` kırmızı olabilir.** F1 tam buydu: not üretiliyordu ama son
   montaj kapısı reddediyordu ve sonuç `blocked` oluyordu. Yeni bir günlük satırı sınıfı
   eklerken testi UÇTAN UCA koş; emsali aynı dosyada duruyordu ve uygulanmamıştı.
2. **Kapalı bir kümeye değer eklemek YETMEZ — damgayı da ilerlet.** `ENGINE_VERSION` iki commit
   boyunca sabit kaldı; aynı damgayı taşıyan iki koşu farklı kurallarla karar veriyordu. Damga
   artık kural yüzeyine test'le bağlı.
3. **Tek noktayı düzeltince KARDEŞ SİTELERİ süpür.** Aynı iddiayı yapan modül beyanı, arayüz eki
   satırı ve kontrol açıklaması bu turda üç kez geride kaldı.
4. **Savunma derinliği ölçülmemişse yoktur.** F2'nin ikinci katmanı ilk mutasyon koşumunda SAĞ
   KALDI — birinci katman ayaktayken erişilemiyordu. Ayrı bir yardımcıya çıkarılıp bağımsız
   ölçüldü.
5. **Fixture çakışması kusuru maskeler.** F3'ün pozitif testi `Sevgililer Günü` kullanıyordu —
   iki ad uzayında da aynı yazılan dört addan biri. İki adın AYRIŞTIĞI vaka hiç test edilmemişti.
6. **Kapanış turunda review defteri (ledger locator) KURULMADI** — sözleşme aynılığı hash'le
   değil kurulum gereğiyle taşındı. Sonraki turlarda defter kurulmalı.

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
