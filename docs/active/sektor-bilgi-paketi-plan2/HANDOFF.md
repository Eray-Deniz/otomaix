---
task: sektor-bilgi-paketi-plan2
written: 2026-09-11
---

# Resume From

**Sıradaki iş: Task 17** (işletime hazırlık kontrol listesi kapısı — K-69/K-70).
Task 16 indi ve **checkpoint 13 `approve` ile kapandı** (dört hakem turu).

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

Task 16 (operatör komut ailesi, 19 alt komut + `recovered` müşteri bandı + n8n hata bildirimi)
uçtan uca yazıldı, dört hakem turu koştu, dört yüksek bulgunun dördü de kapandı ve zincir
`approve` ile bitti; kapanışın bedeli, **üç kez kendi testimin yanlış çıkması** oldu.

# Verification

**Bu oturumda koşulan komutlar ve TAZE çıktıları (hepsi kontrolörün kendi koşumları):**

- `python -m pytest tests/ -q` → **4134 passed**, exit 0 (SON, `086985a`).
  Ara koşumlar: 4124 · 4130 · 4131 · 4127 · 4133 · 4134. Taban 4085 → **+49 test**.
- **Dört Codex turu KOŞTU** (`run_codex_scan`, base-review). Koşum sayıları **stderr'den**
  ölçüldü: **44 · 41 · 28 · 38**. Dördü de `rc=0` ve kesintisiz. Son tur `verdict: approve`,
  **bulgu YOK**.
- **Mutasyon:** bu batch'te AÇILAN her yeni kapı ayrı ayrı susturuldu ve hedef testini kırdı.
  **ÜÇ kez yanlış çıktı ve üçü de düzeltildi** (ayrıntı aşağıda, Notes).
- **Referans taraması:** CLI'deki **79 modül atfı** çözüldü; tarama üç gerçek hata yakaladı
  (olmayan alan adı · yanlış tipte kapı girdisi · olmayan tablo adı).
- **Sözleşme pini** temiz ölçüldü (`contracts.require_pin`), pozitif kontrol testte.
- Defter kapısı her commit'te `rc=0`.

**Denenmemiş / doğrulanmamış — dürüst liste:**

- **Web probunun OLUMLU yolu CANLI koşulmadı.** Bugünkü denetçi-2 komut satırında web bayrağı
  YOK, dolayısıyla bugün beklenen sonuç `False`. İlk canlı ölçüm Task 19.
- **`denetim` / `sentez` / `motor` gövdelerinin DAVRANIŞ testi YOK** — planın Step 1 test
  listesi istemiyor. Onlar için yalnız statik referans taraması koştu.
- **Uçtan uca CLI koşumu YAPILMADI.** Tüm ölçümler fixture ile; ilk gerçek koşum Task 19.
- **n8n hata bildirimi canlıda sınanmadı** — sentetik arıza ile teslim gözlenmedi (Task 18).
- **`ruff` ve `pyright` bu ortamda koşmadı.**
- **CRM webhook onarımı YAPILMADI.** Canlıya migration dağıtılmadı; pilot koşulmadı.
- Task 17-20 hiç yazılmadı.

# Risks

- **EN YÜKSEK (işletim) — kimlik doğrulamasız CRM webhook'ları onarılmadı, yalnız KAPATILDI.**
  Ev: `crm-webhooks-unauthenticated-sql-interpolation` — CURRENT.md'de `proposed`, tetikli.
- **YENİ, EVİ YOK — arşiv dosyasında ÇIPLAK Telegram bot token'ı.** Ölçüldü bu oturumda:
  `docs/archive/CLAUDE_crm_pre_cleanup.md` gerçek bir bot token'ı taşıyor ve depo geçmişine
  yazılmış. Plan 2'nin kapsamı DIŞI. **Dürüst etiket: çözülmedi, evi YOK.** Eray'a bildirildi;
  ev kararı (ayrı task mı, sessiz kabul mü) verilmedi. **Süresiz evsiz park YASAK — bir sonraki
  oturumun açılışında karara bağlanmalı.**
- **Üretim hattı hâlâ koşamaz:** denetçi-2'nin web erişimi yok (araç gerçeği, kod değil).
  Prob artık dürüstçe ölçüyor ama ölçtüğü şey "erişim yok".
- **Bağlayıcı ek AÇIK-2 ile KOD IRAKSADI.** Ek hâlâ seçenek A'yı ("`geri-al` kalsın, olay
  kimliği istesin") yazıyor; kod komutu KALDIRDI (Eray kararı). Hakem bunu bloker SAYMADI ve
  ıraksamanın açıkça kaydedilmiş olmasını yeterli buldu. **Ev: arayüz eki revizyonu · son
  tarih Task 19** (sözleşme penceresi orada kapanıyor).
- **Köken jetonunun kalanı AÇIK.** API kimliği superuser ve tablo sahibi → `REVOKE` ile
  kapanmaz. **Ev: Task 18 dağıtım listesi, M-1 ve M-2.**
- **Kilit sözleşmesi KAYNAKTAKİ kilitleri modeller, veritabanının ZORLADIKLARINI değil.**
  Yeniden açılma koşulu `tests/test_lock_anchor_contract.py` başında yazılı.
- **`recovered` sorgusu bakım penceresini TAM modellemiyor** (hakem, orta → `accepted_risk`).
  Atama başlangıcı ile aktivasyon anını karşılaştırıyor; kesintisiz sürüm geçişi yapan bir
  marka da `recovered` görebilir. **Dürüst etiket: çözülmedi, kabul edildi.**
- **Genel `ValueError` yakalama teşhisi yanlış yöne çekiyor** (hakem, orta → `accepted_risk`).
- **Taslağı kimin yazdırdığı KAYITLI DEĞİL — KAPSAM DIŞI** (Eray kararı, 2026-09-10).
  Task 20 kapanış belgesine bu etiketle girer.
- **Atıf ADAYA bağlı DEĞİL.** Ev: `docs/active/denetci-atif-aday-kimligi/`, sert son tarih Task 19.
- **Sözleşme penceresi Task 19'da KAPANIYOR.** Bekleyen: atıf-aday kimliği · `BulguIzi` alan
  sahipliği · K-126 resmîlik ayağı · K-03 kategori ayağı · **AÇIK-2 uzlaştırması (YENİ)**.
- **Paket satırı kayma penceresi FAIL-CLOSED, KAPALI DEĞİL.** Kalıcı çözüm
  `sector-package-sector-id-immutability` (tetikli). **Task 16 o kolona YAZICI EKLEMEDİ** —
  tetik koşulu bu turda da ölçüldü (CLI o tabloya yalnız SELECT yapıyor) ve tutmadı.
- **Migration `036` yerinde düzenlendi** — kabul edilmiş risk.
- **KABUL EDİLMİŞ RİSK (M3) — commit geçmişi tek-commit TDD modeline uymuyor.**
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`).

# Notes For Claude/Codex

**Süreç ağırlığı — Eray'ın talimatları, BAĞLAYICI:**
1. **Hakem bulgularından YALNIZ critical/high düzeltilir**; orta/düşük RAPORLANIR ve devam edilir.
   **İSTİSNANIN İSTİSNASI:** gerileme kontrolörün KENDİ ürünüyse ve iş küçükse devredilmez.
   Bu oturumda bir kez uygulandı (`olay-onayla` sıfır damgada başarı dönüyordu).
2. Mutasyon kanıtı yalnız **YENİ** kapıya istenir.
3. İnceleme turu üretim/test diye **BÖLÜNMEZ** — tek tur.
4. Düzeltme brief'leri **KISA**.
5. **Aynı eksen üst üste turlarda varyant üretiyorsa yamamayı bırak**, çerçeve teşhisiyle
   kullanıcıya git. Bu oturumda uygulandı ve **YARISI YANLIŞTI** — aşağıya bak.

**BU OTURUMUN ANA DERSLERİ — Task 17 dispatch'ine ZORUNLU:**

1. **ÖLÇMEDEN "YOK" DEME. Bu oturumda İKİ KEZ yapıldı ve ikisini de Eray yakaladı.**
   (a) Adımlar arası devrin tasarımda olmadığını iddia edip karar turu açtım — **spec-input
   §7.5'te yazılıydı** ("dosya çalışma kopyası, veri tabanı kalıcı kanıt katmanı; komut ailesi
   ekleri bu yoldan toplar"). (b) "Depoda kanonik yönetici hedefi yok" dedim — **sekiz yerde
   kuruluydu**. İkisinde de tek bir yere bakıp yokluk ilan ettim.
   **KURAL: karar sorusu sormadan ÖNCE spec-input + spec + ek + mevcut benzer artefaktlar.**
2. **MUTASYON KAPININ VAR OLDUĞUNU KANITLAR, DOĞRU OLDUĞUNU DEĞİL.** Bu oturumda üç kez
   yakalandı: iki sahte-yeşil (test komşu kapının reddini kendi kapısının reddi sanıyordu) ve
   **bir yanlış beklenti** (sahte-yeşili kapatmak için yazdığım test HATALI davranışı kilitledi:
   `False` bekliyordu, oysa tüketici `False`'u "ölçülmüş erişimsizlik" sayıp muafiyet üretiyordu).
   **KURAL: iddiayı ÜRETİCİNİN dönüşünde değil TÜKETİCİNİN sözleşmesinde ölç.**
3. **Sızıntıyı kapatan fix yeteneği de kapatabilir.** Üç yüksek bulgunun üçünde de ilk
   düzeltmem "kaldır" oldu ve kapanış turu haklı olarak itiraz etti (prob olumlu yolu sildi,
   bildirici teslim yolunu sildi). **Fix'in kendi yan etkisini ölç.**
4. **Sınıfı kapat, varyantı değil.** Hata bildirimindeki tenant kusurunu ilk turda yalnız YENİ
   dosyada düzeltip kardeşini "önceden var olan borç" diye bıraktım; ikinci turda ikisi birden
   kapatıldı ve kapı SINIF düzeyine çıkarıldı (iki workflow'u da tarıyor). İlk karar yanlıştı.
5. **TASARIM BELGESİNDE OLMAYAN İŞE BAŞLAMA** — ama "yok" demeden ÖNCE 1. maddeyi uygula.
6. **Kapsam dışına çıkacaksan ÖNDEN görünür sor.** Bu oturumda bir kez gerekti (servis
   katmanına yazmak); sorulunca Eray daha ucuz bir yol seçti (komutu kaldır).
7. **Exec footer'ın iki mekanik kuralı** — `Exec-Kind` uzantıya değil YOL KÜMESİNE bakılarak
   seçilir; `Exec-*` bloğu mesajın SON paragrafıdır. Bu oturumda ihlal YOK.
8. **Commit başlığı ≤72 karakter** — `git log -1 --format=%s | wc -c` ile SAY.
9. `Exec-Task` id'sini yazmadan ÖNCE defterde ARA — **pencere içinde**.
10. Her commit'ten SONRA defter kapısı koşulur (`ec_ledger_view … --post-window`, rc=0).
11. Uygulayıcı kendi alt-ajanını çağırmaz.
12. **İSKELET ÖNCE — her testin kendi kırmızısı ayrı ölçülür.** Bu oturumda uygulandı: iskelet
    kuruldu, 24 test kendi kırmızısını verdi, 11'i (ayrıştırıcı/pin kapısı) iskeletin gerçek
    parçası olduğu için yeşildi. Üç regresyon kilidi kırmızısız geldi ve **mutasyonla** ayrıca
    kanıtlandı.
13. **Gönderilen düzyazıya sayı yazma** — ya üreten komutu yanına koy, ya "doğrulanmadı" etiketle.
14. **Hakem/kontrolör önerisi ADAYDIR** — dosyayı açmadan tekrarlanmaz. Bu oturumda beş yüksek
    bulgunun beşi de kontrolörün KENDİ probuyla doğrulandı; biri (yanlış paket geri alma)
    koşularak ölçüldü (`active → archived` görüldü).
15. **`geri-al` KALDIRILDI** — komut sessizce geri eklenirse kapanmamış yarış da geri gelir;
    karar kilidi testi var.
16. Canlıya hiçbir n8n dosyası körlemesine yüklenmez.

**Codex çağrısı kurarken — çağrıdan ÖNCE bas:**
1. `COMPANION` **ve** `PROMPT` **çağıran kabukta** kurulu mu (kabuk durumu taşınmaz).
2. `REQUIRED_CURRENT_FILES` SATIR SATIR mı — ve **dışlanan dosya var mı**.
3. Taban SHA 40 karakter mi. `CODEX_LOG` yazılabilir mi.
4. **Turun koştuğunu STDERR'den ölç:** `grep -c '^\[codex\] Running command'` **çağrının stderr
   çıktısında** — `$CODEX_LOG`'da DEĞİL.
5. **Uzun turları arka planda koştur.** `CSS_CALL_TIMEOUT` 1200s dört turda da YETTİ.
6. **Kota sınırı gerçek bir daldır.** Üçünü birden kontrol et: `rc` · koşum sayısı · son cümlenin
   karar mı anlatı mı olduğu. Bu oturumda dört turun dördü de `rc=0` ve kesintisizdi; son turun
   SON satırı bloklamayan bir öneriydi, `verdict` satırı gövdenin içindeydi.
7. **TEHDİT MODELİNİ ÖNDEN SÖYLE** — girdi araştırma çıktısıdır, ÖZENSİZ olabilir, SALDIRGAN
   değil. Dört turda da prompt'a konuldu.

**Sır tarayıcısı yanlış alarmı (her oturumda yeniden onay ister).** Substrat şunları dışlıyor:
`CURRENT.md` · backend `CLAUDE.md` · `runs.py` · `tests/test_auditor_orchestration.py` ·
arayüz eki · `tests/test_plan2_interface_contract.py` · `docs/tools/codex-scan-substrate-harness.sh`.
Hepsi yanlış alarm; HEAD git nesnesinden OKUNABİLİYOR ve hakem dördüncü turda dördünü de okuyup
beyan etti.

**EVİ OLAN, TAŞINAN KALEMLER — rolling yeniden yazımda DÜŞÜRÜLMESİN:**
- **`markdown-it-py` bir ÜRETİM bağımlılığıdır** (pinli `4.2.0`), canlıya dağıtılmadı.
  **Ev: Task 18, Step 3.**
- **K-126 tek-kaynak istisnası KAPALI.** **Ev: arayüz eki revizyonu + denetçi sözleşmesi.**
- **K-03'ün kategori ayağı UYGULANMADI.** **Ev: arayüz eki revizyonu.**
- **`BulguIzi` dördüncü alanının sahipliği.** **Ev: arayüz eki revizyonu.**
- **AÇIK-2 uzlaştırması (YENİ).** **Ev: arayüz eki revizyonu · son tarih Task 19.**
- **Task 10'un TEST dosyaları bağımsız hakem GÖRMEDİ.** **Ev: Adım 11 final inceleme.**
- **Web probunun CANLI olumlu ölçümü.** **Ev: Task 19.**
- **n8n hata bildiriminin sentetik arıza ile teslim ölçümü.** **Ev: Task 18.**
- **Atıf ADAYA bağlanmalı.** **Ev: `docs/active/denetci-atif-aday-kimligi/` · son tarih Task 19.**
- **Ayrı veritabanı rolü (jeton kalanı).** **Ev: Task 18, M-1 + M-2.**
- **`sector_packages.sector_id` değişmezliği.** **Ev: `sector-package-sector-id-immutability`
  (CURRENT.md, tetikli).** Tetik koşulu Task 16'da YENİDEN ölçüldü: CLI o tabloya yalnız SELECT
  yapıyor, tetik hâlâ kapalı.
- **Katı Bölüm C biçimi yanlış-pozitif üretebilir ve ÖLÇÜLMEDİ.** **Ev: Task 19.**
- **Kilit sözleşmesinin örtük-kenar sınırı — DÜŞÜRÜLDÜ, park EDİLMEDİ.** Yeniden açılma koşulu
  test dosyasının başında yazılı.
- **Taslak yazarı atfı — KAPSAM DIŞI, düşürüldü.** **Task 20 kapanış belgesine bu etiketle girer.**
- **Atomiklik sınıfı — DÜŞÜRÜLDÜ** (kapsam-dışı-by-design). Yeniden açılma koşulu: onaylı koşum
  yolu DIŞINDA bir migration uygulama yolu doğarsa.
- **`denetim`/`sentez`/`motor` davranış testi — DÜŞÜRÜLDÜ, park EDİLMEDİ.** Dürüst etiket:
  planın Step 1 test listesi bu testleri İSTEMİYOR; kapsam-dışı-by-design. **Yeniden açılma
  koşulu:** o gövdeler değişirse ya da Task 19'un ilk gerçek koşumu orada bir kusur gösterirse.

**EVSİZ KALEM: BİR TANE** — arşivdeki çıplak bot token'ı (yukarıda Risks'te). Bu oturumda
bulundu, Eray'a bildirildi, ev kararı VERİLMEDİ. **Bir sonraki oturum açılışında karara
bağlanmalı; süresiz evsiz park yasaktır.**

- **Eray'a teknik cümle onaylatma** — karar sorularını sade dille, proje-lokal kod referansı
  OLMADAN sor. Bu oturumda üç karar sorusu soruldu; üçü de sade dilde ve ölçülmüş bedelliydi.
  **Ama biri hiç sorulmamalıydı** (bkz. ders 1a) — soru sormadan önce kaynak okunmamıştı.
- **Bu dosya ROLLING'dir** — her oturumda BAŞTAN yazılır; karar izi `TASK.md` Decisions Log'una gider.
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz (bu yazım hariç).
