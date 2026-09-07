---
task: sektor-bilgi-paketi-plan2
written: 2026-09-07
---

# Resume From

**Sıradaki iş — sırayla:**

1. **Sözleşme görevinin 4. AYAĞI** (`docs/active/brief-sozlesmesi-kaynak-bolumu-makine-okunur/`).
   Diğer üç ayak indi. Kalan: mekanik kapının Bölüm C ailesini **olumsuz çıkarımdan olumlu
   yapısal sözleşmeye** çevirmek. Sözleşme artık sabit sütunlu tablo istiyor, dolayısıyla kapı
   "bu bir eşleme DEĞİL" çıkarımı yapmak yerine sütun sayısı · hücre doluluğu · adres biçimi
   doğrulayabilir. **Kapanınca Task 7'nin "makineyle DOĞRULANMADI" kapsam beyanı KALKMALI**
   (`brief_doctor.py` modül docstring'i) — kalkmazsa beyan bayatlar.
2. **Task 8 — koşu ve artefakt servisi** (plan satır 981).
3. Task 9.

Komut: `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam**.

**ÖNCE OKU — kanonik ilerleme burada DEĞİL:**
`.superpowers/sdd/2026-08-27-sektor-bilgi-paketi-plan2/progress.md` (git'e girmiyor).

**Yürütme durumu:** kip alt-ajanlı · başlangıç çapası `a806e29` · defter penceresi `a806e29` ·
**`cp_count: 3`** · **`last_checkpoint_ref: 2b468e8d`**.

> **BİLEREK İLERLETİLMEDİ** (değişmedi). Checkpoint 6 override ile kapandı; §8.6 mutasyon
> protokolü yalnız Clean/Accepted-risk dallarında koşar. Sonuç fail-safe: sonraki checkpoint'in
> tabanı `2b468e8d` KALIR ve Task 7'nin bütün commit'lerini kendiliğinden yeniden kapsar.

**Dal:** `feat/sektor-bilgi-paketi-plan2`. Son commit **`cad705c`**. Uzak **`091dc03`**'te —
bu oturumun dört commit'i **push EDİLMEDİ**. Ağaç temiz.

**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: son commit **`7964ed6`**,
monorepo pin manifesti bu commit'e bağlı.

## Bu oturum ne yaptı — tek cümle

Çit maskesi elle yazılmış CommonMark yaklaşımı olmaktan çıkıp **grameri koşturur** hâle geldi
(`markdown-it-py`), ve araştırma sözleşmesinin çıktı formatı **makine-okunur kesinliğe** çevrildi.

## Sıradaki dispatch'te ÖNDEN bildirilecekler

1. **YENİ — `markdown-it-py` artık bir ÜRETİM bağımlılığıdır** (`requirements.txt`, pinli
   `4.2.0`, saf Python, tek bağımlılığı `mdurl`). Docker imajı yeniden kurulmalı; **canlıya
   dağıtılmadı.**
2. **YENİ — ayrıştırıcı sınırı SONLUDUR ve ilan edilmiştir.** `maxNesting=100`. 100 kattan derin
   iç içe yapı aynı sınıfı yeniden açar. Bu bir tripwire ile ölçülüyor (`sinir + 50`
   derinliğinde açığın GERÇEKTEN göründüğü doğrulanıyor); sınırı sessizce yükseltirsen test
   kırılır. Değer 1000 DENENDİ ve GERİ ALINDI — o eşikte `RecursionError` çıkıyordu.
3. **YENİ — bu oturumun dört commit'i bağımsız hakem GÖRMEDİ** (`4d107e8` · `4167401` ·
   `868f50a` · `cad705c`). Tur 11 `4167401`'e kadar inceledi ve `cad705c` onun bulgusunun
   düzeltmesidir. **Ev uydurulmadı:** final incelemenin tabanı `a806e29` olduğu için hepsi
   oraya kendiliğinden girer.
4. **Ek metni kodla uyumsuz, İKİ yerde** (değişmedi): R12(a2)(d) amende edildi; aktör kapısının
   tanım yeri ekin gösterdiği modül değil.
5. **Ekin kendi içinde çelişkisi:** ayak (d) düzyazısı `BEFORE UPDATE OR DELETE`, bağlayıcı SQL
   bloğu `BEFORE UPDATE`. **Evi Task 8.**
6. **Onay mührü yüklemi:** dolu → BOŞ reddediliyor, yeniden mühürleme BİLEREK açık. Task 8'de
   ek metniyle karşılaştırılmalı.
7. **Kimlik kapıları migration dosyalarının BAŞINDA** — yeni migration yazılırken kapı ilk üst
   düzey DDL'den ÖNCE konmalı.
8. **Task 7 ve Task 11 planda "Arayüz eki bağlar" satırını TAŞIMIYOR** (20 görevin 18'inde var).
   **Task 11'de bu kontrol ELLE yapılmalı.**
9. **Task 8/9/12 girdi kapısının tiplerini tüketecek.** Bugün depoda o tiplere modül ve kendi
   testi dışında **hiçbir atıf yok**. Task 8 ilk tüketiciyi eklerse TASK.md Open Problems'taki
   tetikli kalemler yeniden değerlendirilmeli.
10. **Substrat kapsam kaybı:** Codex kum havuzu `api_key=<ifade>` desenli üretim dosyalarını,
    aktif katman dosyalarını ve bağlayıcı eki dışlıyor; hakem tam test kümesini yeniden
    koşamıyor ve bunu her turda kendisi yazıyor.
11. **Girdi kapısının test dosyası büyük** — 3850 test. Yeni matris eklerken disiplin aynı:
    **kap çarpımını büyütme, ayırt eden ekseni büyüt.** Bu oturumda `dört boşluk` bağlamı
    ÇIKARILDI (gerçek bir çit bağlamı değildi) ve kazanılan yer sınır problarına harcandı.

## Her görev dispatch'inde ZORUNLU olarak taşınacaklar

1. Arayüz eki **bağlayıcıdır**; ilgili hükümler brief'e **harfiyen kopyalanır**.
2. Test komutu sanal ortam aktifleştirilerek koşar (aşağıda Verification).
3. **Taban 5349**; bu sayı düşmeyecek. (5665'ten düşüş `dört boşluk` bağlamının matristen
   ÇIKARILMASIDIR — davranış iddiası kaybı DEĞİL; ölçüldü, girintili kod bloğu maskeye AYRI
   olarak dahil.)
4. `Exec-Kind` **sınıflandırıcıya** karşı seçilir. `.sql` çalıştırılabilir sınıfa GİRMEZ.
5. `Exec-*` bloğu mesajın SON PARAGRAFI, co-author trailer'ları **aynı paragrafta**.
6. **Commit başlığı ≤72 karakter** — `git log -1 --format=%s | wc -c` ile SAY.
7. Her commit'ten SONRA defter kapısı koşulur.
8. Uygulayıcı kendi alt-ajanını çağırmaz. **`docs/active/` altına yazmaz.**
9. Codex çağrılarına tam 40 karakterlik SHA verilir.
10. Kapanış **üretilmiş matrisle** kanıtlanır, matris **mutasyonla** sınanır, **boş-küme kontrol
    kolu** eklenir.
11. **Gönderilen düzyazıya sayı yazma** — ya üreten komutu yanına koy, ya "doğrulanmadı" etiketle.
12. **Tarama deseni KAVRAMDAN türetilir**, bulunan örneklerden değil.
13. **Kontrolörün tam test kümesi, veritabanına dokunan bir alt-ajanla ASLA üst üste binmez.**
14. Bir düzeltme, DEĞİŞTİRDİĞİ yapıyı okuyan testleri bayatlatabilir — her turda eski test
    dosyasını yeni modüle karşı koştur.
15. Kimlik kapısı ya kanonik değerle TAM eşleşmeli ya da kümeyi ÜRETEN yapıdan türemeli.
16. Canlıya hiçbir n8n dosyası körlemesine yüklenmez.
17. **Hakem/kontrolör önerisi ADAYDIR.** Bu görevde ölçümde yanlış çıkan öneri/teşhis sayısı
    **sekiz** (bu oturumda ikisi: tur 10'un beş varyantından ikisi yanlış-pozitifti).
18. **Kendi probunu da sorgula** — bu görevde prob YEDİ kez yanılttı, bu oturumda ÜÇÜ.
    **YENİ VE EN ÖNEMLİSİ:** üçü de İNANDIRICI sonuç verdi, yani sürprize bağlı kural onları
    yakalayamaz. **Prob kanıt sayılmadan ÖNCE, probun ne ürettiğini ÖLÇÜLEN SİSTEME DEĞİL
    OTORİTEYE sor** (`md.render(doc)` · token dökümü). Bu adım her seferinde beş saniyede kesin
    cevabı verdi ve her seferinde en sona bırakılmıştı.
19. **KAPANIŞ SAYIYLA DEĞİL MESAJ KÜMESİ FARKIYLA KANITLANIR.**
20. **Üç tur aynı ekseni getiriyorsa dördüncü nokta-düzeltmesi AÇMA.** Sınıfı adlandır, üretilmiş
    matrisle kapat; kapanmıyorsa **çerçeve teşhisiyle Eray'a git**. Bu oturumda tam olarak bu
    yapıldı ve işe yaradı (üç seçenekli teşhis → A → sınıf yapıyla kapandı).
21. **Bir KURAL beşinci kez kandırılıyorsa kural yazmayı bırak, DEĞİŞMEZ kur** — ve değişmez de
    kandırılıyorsa **GRAMERİ KOŞTUR**. Bu oturumun dersi: dış gramer modelleyen guardrail'de
    çalıştırılabilir ground-truth ZORUNLUDUR (protokolün M6 hükmü); yoksa matrisin kör noktası
    kendi hayal gücün kadardır.
22. **Beyan bayatlarsa beyan olmamaktan kötüdür** — ilan edilen her açık için o açığın gerçekten
    var olduğunu ölçen bir TRIPWIRE.
23. **YENİ — ORACLE İMPLEMENTASYONDAN BAĞIMSIZ OLMALI.** Beklenti ölçülen fonksiyonu okursa,
    o fonksiyonu değiştiren her mutasyon beklentiyi de kaydırır ve mutasyon kolları SESSİZCE
    yeşile döner. Ölçüldü ve düzeltildi (`_gramer_maskesi` doğrudan `bd._MD`'yi okur).
24. **YENİ — ÇAKILI SAYILARI TEK GEÇİŞTE ÖLÇ.** Ayrıştırıcıyı değiştirmek 2700 hücrelik
    matrisin on bir çakılı sayısını ve dört mutasyon kolunun beklentisini birden geçersiz
    kıldı. Teker teker ölçmek her adımda iki dakikalık bir test koşumuna mal oldu ve saatler
    yedi. **Hepsini tek ölçüm betiğiyle çıkar, tek seferde yaz.**

# Verification

**Koşulan komutlar ve TAZE çıktıları (2026-09-07 ikinci oturum, hepsi kontrolörün KENDİ koşumları):**

- `cd apps/social/backend && source .venv/bin/activate && python -m pytest tests/ -q`
  → **5349 passed in 669.10s**, exit 0, temiz ağaçta, HEAD `cad705c`'de.
  Seyir: … 5002 → 5665 → **5349**. 5665 → 5349 düşüşü **`dört boşluk` bağlamının
  ÇIKARILMASIDIR**; hiç test silinmedi, hiçbir davranış iddiası kaybolmadı.
- `ec_ledger_view a806e29… /root/otomaix - --post-window` → **rc=0**, her commit'ten sonra.
- **Sözleşme pini:** `pytest tests/test_contract_pin.py` → 32 passed, yeni sürüme bağlı.
- **Codex çağrısı: 3** (tur 9 · 10 · 11). Tur 9/10 `rc=0`; **tur 11 `rc=1` — çıktı KESİLDİ**
  (düzyazıda bulguyu anlatıyor ama yapılandırılmış `Findings` bölümü boş). Bulgu yine de
  kontrolör tarafından doğrulandı ve düzeltildi. Ham çıktı log'da.
- **Kontrolörün bulgu doğrulaması:** üç turun HER bulgusu kendi probuyla yeniden ölçüldü;
  **iki bulgu yanlış-pozitif çıktı** ve düzeltilmedi, KAYDEDİLDİ (görünürlük kontrol koluna
  taşındı ki bir sonraki tur onları yeniden "kaçış" diye açmasın).
- **Düzeltmenin kendi yan etkisi ÖLÇÜLDÜ:** eski modül `git show 7244ea0:…` ile çıkarıldı ve
  390 hücrelik çarpımda yan yana koşuldu. Yeni sürüm 24 hücrede not kaldırıyor; hepsi eski
  sürümün belgeyi yanlışlıkla yutmasından doğan **yanlış pozitiflerdi**. Gerçek notu kaybeden
  hücre: eski sürümde 40, yeni sürümde 0.
- **Sınır ölçümü:** iç içe derinlik 9 kapalı / 11 açıktı; düzeltmeden sonra 9·11·25·60·99
  kapalı. Derinlik 500/2000/5000 çökmüyor. Derinlik-400 belgesi 0.17 sn.

**Denenmemiş / doğrulanmamış senaryolar — dürüst liste:**

- **Bu oturumun dört commit'i bağımsız hakem GÖRMEDİ** (yukarıda; evi var).
- **Ayrıştırıcı sınırı SONLU** — 100 kattan derin iç içe yapıda sınıf yeniden açılır. İlan
  edildi, tripwire'lı, **çözülmedi**.
- **`markdown-it-py` canlıya dağıtılmadı**; Docker imajı yeniden kurulmadı. Bağımlılığın
  üretim ortamında davranışı DOĞRULANMADI.
- **Sözleşmenin YENİ biçiminde üretilmiş gerçek araştırma çıktısı YOK** (dış depodaki dosyalar
  2026-07-11 tarihli). Araçların tabloyu ne kadar düzgün ürettiği ve yanlış-pozitif oranı
  **ÖLÇÜLMEDİ**; ilk gerçek ölçüm Task 19 Step 5'te doğacak.
- **Bölüm C kapısı HENÜZ olumlu sözleşmeye çevrilmedi** (4. ayak) — sözleşme tabloyu istiyor
  ama kapı hâlâ eski vekille bakıyor. **"Makineyle doğrulanmadı" beyanı hâlâ YERİNDE ve doğru.**
- **Bölüm C'nin üçlü yapısı makineyle DOĞRULANMIYOR** — ilan edildi, onarılmadı, evi 4. ayak.
- **`telegramApi` credential'ının canlı token taşıdığı DOĞRULANMADI** (değişmedi).
- **CRM webhook onarımı YAPILMADI** — yalnız kapatıldı (değişmedi).
- PG 18.3 dışında sürüm denenmedi; çok-oturumlu eşzamanlılık denenmedi.
- Canlıya hiçbir migration dağıtılmadı; pilot koşulmadı. **Dal push EDİLMEDİ.**
- Task 8–20 hiç yazılmadı.

# Risks

- **YENİ — üretim bağımlılığı eklendi ve canlıda denenmedi.** `markdown-it-py==4.2.0`. Deploy
  öncesi imaj yeniden kurulmalı; kurulmazsa `brief_doctor` import'ta patlar.
- **YENİ — ayrıştırıcı sınırı sonlu (100).** Gerçekçi araştırma çıktısında erişilemez ama
  ÇÖZÜLMEDİ. `RecursionError` yolu fail-closed bağlandı (savunma katmanı, testi var).
- **Checkpoint 6 `approve` ile DEĞİL, override ile kapandı** (değişmedi). `cp_count`
  ilerletilmedi.
- **Sözleşme görevi YARIM** — üç ayak indi, dördüncüsü açık. Yuva hâlâ **Task 9'dan ÖNCE**:
  Task 9/10 denetçi katmanını kurar ve sözleşmeye atıf yapar.
- **EN YÜKSEK — kimlik doğrulamasız CRM webhook'ları onarılmadı, yalnız KAPATILDI** (değişmedi).
- **KABUL EDİLMİŞ RİSK (M3) — commit geçmişi tek-commit TDD modeline uymuyor** (değişmedi).
- **EVSİZ PARK — atomiklik sınıfı depo GENELİ** (değişmedi).
- **KABUL EDİLMİŞ RİSK — `ON_ERROR_STOP` ret yolunda geri konamıyor** (değişmedi).
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`).

# Notes For Claude/Codex

- **Hakem turlarını Claude koşar — SORMA.** Eray'ın kalıcı kuralı.
- **ZİNCİRİ DURDURMA KARARINI ERAY'A GÖTÜR.** Bu oturumun en pahalı süreç hatası: üç hakem turu
  koşuldu ve durma kararı hiç önüne konmadı. Eray haklı olarak "bir bulguyu düzeltmek kaç saat
  sürüyor" diye sordu. Kural zaten yazılıydı (`feedback_severity_gates_process_weight`) ve
  ateşlenmedi — çünkü **durum-tetikli** bir kuraldır ve not olarak ateşlenmez.
- **TEHDİT MODELİNİ ÖNDEN SÖYLE.** Bu kapı Gemini/Claude/ChatGPT araştırma çıktısı okuyor —
  girdisi ÖZENSİZ olabilir, SALDIRGAN değil. "11 kat iç içe liste" gerçekçi bir arıza biçimi
  değildir. Bu üç tur önce söylenseydi zincir orada biterdi.
- **Prob otoriteye sorulmadan kanıt sayılmaz** (madde 18) — bu oturumun en pahalı teknik dersi.
- **Hakem raporunu doğrulanmamış iddia say.**
- **Alt-ajan model alanını HİÇ GEÇME.** Çıplak takma ad hook tarafından reddediliyor.
- **Spec değil, spec-input kanoniktir.**
- **Eray'a teknik cümle onaylatma** — ama SEVİYE kararını (medium mu high mı) ONA SOR: bu
  oturumda etiket tartışması doğru yere gitti ve otonom düzeltme döngüsünü açan şey o oldu.
- **Hafıza kararı AÇIK:** Eray, durum-tetikli kuralları hafızaya yazmanın **yanlış kapanış**
  ürettiğini söyledi (not yazılınca konu "ele alınmış" görünüyor ama hiç ateşlenmiyor).
  Eylem-tetikli notlar bu oturumda ALTI kez ateşlendi ve iş gördü; durum-tetikli olanlar ÜÇ kez
  ateşlenmedi. **Karar verilmedi:** kapı komutun içine mi kurulacak (`checkpoint_codex_reviews_ran`
  sayacının yanına), yoksa bu sınıf hiç yazılmayacak mı. Yeni oturum bunu gündemine alsın.
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz.
