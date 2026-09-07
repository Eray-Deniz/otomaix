---
task: sektor-bilgi-paketi-plan2
written: 2026-09-07
---

# Resume From

**Sıradaki iş: Task 8 — koşu ve artefakt servisi (plan satır 981).**
Sözleşme görevi KAPANDI ve listeden çıktı; Task 8'in önünde başka bir iş yok.

> **TASK 8 BAŞLAMADI — ölçüldü (2026-09-07), çünkü kayıt aksini ima ediyordu.** Sözleşme
> görevinin metni yuvayı *"Task 8 bittikten SONRA"* diye tarif ediyor ve bu, Task 8'in bitmiş
> olduğu izlenimini veriyor. Ölçüm: `sector_pipeline/runs.py` **YOK** ·
> `tests/test_pipeline_runs.py` **YOK** · SDD defterinde `task-8-brief.md` **YOK** ·
> pencerede `Exec-Task: T8` etiketli commit sayısı **0**. Sözleşme görevi ilan edilen
> yuvadan ERKEN bitti; bağlayıcı olan "Task 9'dan ÖNCE" koşulu korundu.

**AMA Task 8 dispatch'i BİR KARAR KAPISIYLA açılıyor — yürütücü onu çözemez.**
Yeni oturum önce o kararı Eray'a götürmeli, sonra `/execute-plan-claude-codex` koşmalı.
Karar verilmeden dispatch edilirse görev orada durur (bağlayıcı ek, Task 8'e bir yapısal test
sözü veriyor ve o testin hangi hükme karşı koşacağı bu kararla belirlenir).

**Komut:** `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam**.

**ÖNCE OKU — kanonik ilerleme burada DEĞİL:**
`.superpowers/sdd/2026-08-27-sektor-bilgi-paketi-plan2/progress.md` (git'e girmiyor).

**Yürütme durumu:** kip alt-ajanlı · başlangıç çapası `a806e29` · defter penceresi `a806e29` ·
**`cp_count: 3`** · **`last_checkpoint_ref: 2b468e8d`**.

> **BİLEREK İLERLETİLMEDİ** (değişmedi). Checkpoint 6 override ile kapandı; §8.6 mutasyon
> protokolü yalnız Clean/Accepted-risk dallarında koşar. Sonuç fail-safe: sonraki checkpoint'in
> tabanı `2b468e8d` KALIR ve Task 7'nin bütün commit'lerini kendiliğinden yeniden kapsar.

**Dal:** `feat/sektor-bilgi-paketi-plan2`. Son commit için `git log -1` — bu satıra sha
YAZILMAZ, drift eder. **Bu oturumun commit'leri uzağa PUSH EDİLMEDİ** (kaç tane olduğu `git log origin/HEAD..HEAD`
ile sayılır — bu satıra yazılmaz, drift eder).

**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: son commit **`7964ed6`**,
monorepo pin manifesti bu commit'e bağlı. **Bu oturumda dokunulmadı.**

## Bu oturum ne yaptı — tek cümle

Sözleşme görevinin son (4.) ayağı indi: Bölüm C kapısı olumsuz çıkarımdan **olumlu yapısal
sözleşmeye** geçti, bayat "makineyle DOĞRULANMADI" beyanı üç yerden de kalktı.

## TASK 8 DISPATCH'İNDEN ÖNCE KARARA BAĞLANACAKLAR (hepsi ekin metnine ait)

1. **Ad kümesi hükmü — ÖLÇÜM DÜZELTİLDİ, kayıt bayattı.** Ek, yaşam döngüsü modülünün kimlik
   modülünden **yalnız kanonik hash adını** kullanmasını şart koşuyor. CURRENT.md'deki kalem
   "modül gerçekte ÜÇ ad kullanıyor" diyordu. **Taze ölçüm (2026-09-07):
   `sector_package_lifecycle.py` İKİ ad kullanıyor — `identity.validate_decision_log` ve
   `identity.check_unit_integrity` — ve `identity.canonical_sha`'yı HİÇ ÇAĞIRMIYOR.** Modülde
   645 satırda tek bir hash hesabı yok (`grep -in "sha\|hash"` → yalnız docstring satırı).
   Yani ek yalnız "fazla ad var" diye değil, **dayandığı varsayım yüzünden de** kodla uyumsuz.
   İki kapanış yolu var, ikisi de tasarım kararı: (a) ek hükmü ölçülen gerçeğe göre revize
   edilir, (b) şema kapısı yaşam döngüsünden çıkarılıp başka yere taşınır (Plan 1'in yazım
   kapısı mimarisini değiştirir).
2. **Ekin kendi içinde çelişkisi:** ayak (d) düzyazısı `BEFORE UPDATE OR DELETE`, hemen
   altındaki bağlayıcı SQL bloğu `BEFORE UPDATE` (ek satır 2654 ↔ 2674). Hangisi bağlar?
3. **Onay mührü yüklemi:** dolu → BOŞ reddediliyor, yeniden mühürleme BİLEREK açık; ek metniyle
   karşılaştırılmalı.
4. **Ek metni kodla uyumsuz, İKİ yerde** (değişmedi): R12(a2)(d) amende edildi; aktör kapısının
   tanım yeri ekin gösterdiği modül değil (`package_events.require_actor`).

## Sıradaki dispatch'te ÖNDEN bildirilecekler

1. **`markdown-it-py` bir ÜRETİM bağımlılığıdır** (`requirements.txt`, pinli `4.2.0`).
   Docker imajı yeniden kurulmalı; **canlıya dağıtılmadı.**
   **EV VERİLDİ (2026-09-07 kapanış taraması): Task 18, Step 3** — *"Arka ucu ve CLI'yi
   dağıt"*. Evsiz risk değil, zamanlanmış bir adımın girdisi.
2. **Ayrıştırıcı sınırı SONLUDUR ve ilan edilmiştir.** `maxNesting=100`, tripwire'lı.
3. **Bağımsız hakem BU OTURUMUN commit'lerini GÖRMEDİ** — `c73c102` (docs) · `854373d` (kod) ·
   `f98a392` (docs) · `ae9111c` (docs). Önceki oturumdan da incelenmemiş olanlar: `868f50a` ·
   `cad705c` · `c5795d5`. **Ev uydurulmadı:** final incelemenin tabanı `a806e29` olduğu için
   hepsi oraya kendiliğinden girer.
4. **Kimlik kapıları migration dosyalarının BAŞINDA** — yeni migration yazılırken kapı ilk üst
   düzey DDL'den ÖNCE konmalı.
5. **Task 7 ve Task 11 planda "Arayüz eki bağlar" satırını TAŞIMIYOR** (20 görevin 18'inde var).
   **Task 11'de bu kontrol ELLE yapılmalı.**
6. **Task 8/9/12 girdi kapısının tiplerini tüketecek.** Bugün depoda o tiplere modül ve kendi
   testi dışında **hiçbir atıf yok**. Task 8 ilk tüketiciyi eklerse TASK.md Open Problems'taki
   tetikli kalemler yeniden değerlendirilmeli.
7. **Substrat kapsam kaybı:** Codex kum havuzu `api_key=<ifade>` desenli üretim dosyalarını,
   aktif katman dosyalarını ve bağlayıcı eki dışlıyor; hakem tam test kümesini yeniden
   koşamıyor ve bunu her turda kendisi yazıyor.
8. **Girdi kapısının test dosyası büyüdü** — 5013 → 5230 satır, **taban 5913 test**. Yeni matris
   eklerken disiplin aynı: kap çarpımını büyütme, **ayırt eden ekseni** büyüt.
9. **YENİ — Bölüm C artık SABİT SÜTUNLU TABLODUR.** Bölüm C'ye dokunan her prob/fixture bunu
   bilmeli. Bu oturumda İKİ prob tam da bu yüzden kirlenmişti (aşağıda).

## Her görev dispatch'inde ZORUNLU olarak taşınacaklar

1. Arayüz eki **bağlayıcıdır**; ilgili hükümler brief'e **harfiyen kopyalanır**.
2. Test komutu sanal ortam aktifleştirilerek koşar (aşağıda Verification).
3. **Taban 5913**; bu sayı düşmeyecek.
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
    **sekiz** (bu oturumda yeni yanlış çıkmadı — hakem hiç koşmadı).
18. **Kendi probunu da sorgula.** Bu görevde prob **DOKUZ** kez yanıltmıştı; bu oturumda İKİ
    kez daha (aşağıda) — toplam dokuz. Prob kanıt sayılmadan ÖNCE **probun ne ölçtüğünü
    OTORİTEYE sor**, ölçülen sisteme değil.
19. **KAPANIŞ SAYIYLA DEĞİL MESAJ KÜMESİ FARKIYLA KANITLANIR.**
20. **Üç tur aynı ekseni getiriyorsa dördüncü nokta-düzeltmesi AÇMA.** Sınıfı adlandır, üretilmiş
    matrisle kapat; kapanmıyorsa **çerçeve teşhisiyle Eray'a git**.
21. **Bir KURAL beşinci kez kandırılıyorsa kural yazmayı bırak, DEĞİŞMEZ kur** — değişmez de
    kandırılıyorsa **GRAMERİ KOŞTUR**. **Bu oturumun eki:** gramer de yetmiyorsa kök çözüm
    KODDA değil **SÖZLEŞMEDE** olabilir. Bölüm C tam olarak öyle kapandı — üç tur regex
    sertleştirmesi yakınsamamıştı, sözleşme biçimi dayatınca kapı tek turda kapandı.
22. **Beyan bayatlarsa beyan olmamaktan kötüdür** — ilan edilen her açık için o açığın gerçekten
    var olduğunu ölçen bir TRIPWIRE. **Bu oturumda tripwire İŞE YARADI:** kaçış kapanınca test
    kırıldı ve beyanı güncellemek ZORUNLU oldu.
23. **ORACLE İMPLEMENTASYONDAN BAĞIMSIZ OLMALI.**
24. **ÇAKILI SAYILARI TEK GEÇİŞTE ÖLÇ.** Bu oturumda dokuz sayı tek betikle çıkarıldı ve tek
    seferde yazıldı; geçen oturum aynı işi teker teker yapıp saatler yemişti.
25. **YENİ — PROB KENDİ ÖLÇTÜĞÜ AİLEYE DARALTILMALI.** Belge geneline uygulanan bir bozma
    prob'u, yeni bir yapı doğduğunda sessizce başka bir ailenin notunu ölçmeye başlar.

# Verification

**Koşulan komutlar ve TAZE çıktıları (2026-09-07 üçüncü oturum, hepsi kontrolörün KENDİ
koşumları):**

- `cd apps/social/backend && source .venv/bin/activate && python -m pytest tests/ -q`
  → **5913 passed in 697.50s**, exit 0, temiz ağaçta.
  Seyir: … 5002 → 5665 → 5349 → **5913**. Artış +564 = **540 yeni çit hücresi** (altıncı gövde
  `c-tablolu`) + **24 yeni Bölüm C testi**. Hiçbir test silinmedi.
- `ec_ledger_view a806e29… /root/otomaix - --post-window` → **rc=0**, her commit'ten sonra (3 kez).
- **Kaçış kapandı, mesaj KÜMESİ farkıyla:** `- Düz yazı, devamı https://example.com/kaynak`
  → önce `gecti / 0 not`, şimdi `notlu-gecti / 1 not`. Kaçışı ilan eden TRIPWIRE testi
  ateşlendi ve artık TERSİNİ ölçüyor.
- **Düzeltmenin kendi yan etkisi ÖLÇÜLDÜ:** eski modül `git show HEAD:` ile çıkarıldı, 24
  hücrede yan yana koşuldu. Eski sürümün not ürettiği **tek** hücrede yeni sürüm susuyor ve o
  hücre **TEMİZ kaynaktır** — eski kapı sözleşmenin KENDİ başlık satırını yanlışlıyordu.
  Kaybedilen tek şey bir **yanlış pozitif**.
- **İKİ PROB KİRLENMESİ bulundu ve düzeltildi:** `tablo_sutunlarini_boz` ve
  `gerekce_tablosunu_boz` bütün belgeye uygulanıyordu; Bölüm C tabloya çevrilince aynı prob iki
  ailenin notunu karıştırdı (ölçüldü: `_tablo_sekli_ihlalleri` sökülünce `sütun` izi Bölüm C'nin
  notundan geliyordu). İkisi de Bölüm B'ye daraltıldı.
- **Ad kümesi ölçümü TAZE koşuldu:** `sector_package_lifecycle.py` → `identity` modülünden İKİ
  ad, `canonical_sha` HİÇ YOK, dosyada hiç hash hesabı yok (645 satır).
- **Codex çağrısı: 0.** Bu oturumda hiçbir hakem turu koşulmadı.

**Denenmemiş / doğrulanmamış senaryolar — dürüst liste:**

- **Bu oturumun commit'lerini bağımsız hakem GÖRMEDİ** — `c73c102` · `854373d` · `f98a392` ·
  `ae9111c`. Önceki oturumdan `868f50a` · `cad705c` · `c5795d5` de görülmemişti. Hepsinin evi
  var: final incelemenin tabanı `a806e29`.
- **BÜTÜNLÜK kontrolü sözleşmenin yazılı harfinden bir adım ÖNDE** — sözleşme her alan için
  kaynak satırını kelimesi kelimesine ZORUNLU kılmıyor ("en az 2 bağımsız kaynak HEDEFLE").
  Bugün hiçbir kontrol ELEMEDİĞİ için bedel gürültüdür. **Eray veto ederse geri alınır:** tek
  fonksiyon (`_c_kapsama_ihlalleri`) ve kendi mutasyon kolu var.
- **Sözleşmenin YENİ biçiminde üretilmiş gerçek araştırma çıktısı YOK.** Araçların tabloyu ne
  kadar düzgün ürettiği ve **katı biçimin yanlış-pozitif oranı ÖLÇÜLMEDİ**; ilk gerçek ölçüm
  Task 19 Step 5'te doğacak.
- **Ayrıştırıcı sınırı SONLU** (100). İlan edildi, tripwire'lı, **çözülmedi**.
- **`markdown-it-py` canlıya dağıtılmadı**; Docker imajı yeniden kurulmadı.
- **`telegramApi` credential'ının canlı token taşıdığı DOĞRULANMADI** (değişmedi).
- **CRM webhook onarımı YAPILMADI** — yalnız kapatıldı (değişmedi).
- PG 18.3 dışında sürüm denenmedi; çok-oturumlu eşzamanlılık denenmedi.
- Canlıya hiçbir migration dağıtılmadı; pilot koşulmadı. Dal **PUSH EDİLMEDİ** (bu oturumun
  commit'leri yerelde), merge EDİLMEDİ, canlıya hiçbir şey dağıtılmadı.
- Task 8–20 hiç yazılmadı.

# Risks

- **EN YÜKSEK — Task 8 dispatch'i KARAR KAPISIYLA açılıyor** (yukarıda dört kalem). Karar
  verilmeden dispatch edilirse görev orada durur ya da yürütücü ekin metnini kendi başına
  yorumlar — ikincisi ekin bağlayıcılığını fiilen kaldırır.
- **Üretim bağımlılığı eklendi ve canlıda denenmedi.** `markdown-it-py==4.2.0`. İmaj yeniden
  kurulmazsa `brief_doctor` import'ta patlar. **Ev: Task 18 Step 3** (arka ucun dağıtımı).
- **Ayrıştırıcı sınırı sonlu (100) — DÜŞÜRÜLDÜ, park EDİLMEDİ (2026-09-07 kapanış taraması).**
  Dürüst etiket: **çözülmedi + kapsam-dışı-by-design.** Gerekçe tehdit modelidir: bu kapı
  Gemini/Claude/ChatGPT araştırma çıktısı okur — girdi ÖZENSİZ olabilir, SALDIRGAN değil; 100
  kat iç içe yapı gerçekçi bir arıza biçimi değil. `RecursionError` yolu fail-closed bağlı ve
  sınırın gerçekten var olduğunu ölçen bir tripwire var, yani beyan bayatlayamaz.
  **Yeniden açılma koşulu:** (a) girdi kaynağı değişir ve düşmanca metin kabul eden bir yüzey
  doğarsa, (b) gerçek araştırma çıktısında sınıra yaklaşan bir belge ÖLÇÜLÜRSE (ilk gerçek
  ölçüm Task 19 Step 5).
- **Katı Bölüm C biçimi yanlış-pozitif üretebilir ve bu ÖLÇÜLMEDİ.** Task 19 Step 5 sözleşmeyi
  ilk kez gerçek çıktıyla sınayacak; tablo düzgün üretilmezse sözleşme metni revize edilir ve
  pin + kapı ÜÇÜNCÜ kez dokunur.
- **Checkpoint 6 `approve` ile DEĞİL, override ile kapandı** (değişmedi). `cp_count`
  ilerletilmedi.
- **EN YÜKSEK (işletim) — kimlik doğrulamasız CRM webhook'ları onarılmadı, yalnız KAPATILDI.**
- **KABUL EDİLMİŞ RİSK (M3) — commit geçmişi tek-commit TDD modeline uymuyor** (değişmedi).
- **EVSİZ PARK — atomiklik sınıfı depo GENELİ** (değişmedi).
- **KABUL EDİLMİŞ RİSK — `ON_ERROR_STOP` ret yolunda geri konamıyor** (değişmedi).
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`).

# Notes For Claude/Codex

- **Hakem turlarını Claude koşar — SORMA.** Eray'ın kalıcı kuralı.
- **ZİNCİRİ DURDURMA KARARINI ERAY'A GÖTÜR.** Durum-tetikli kural; not olarak ateşlenmiyor.
- **TEHDİT MODELİNİ ÖNDEN SÖYLE.** Girdi araştırma çıktısıdır — ÖZENSİZ olabilir, SALDIRGAN değil.
- **Prob otoriteye sorulmadan kanıt sayılmaz** — ve prob KENDİ ölçtüğü aileye daraltılmalı.
- **Hakem raporunu doğrulanmamış iddia say.**
- **Alt-ajan model alanını HİÇ GEÇME.** Çıplak takma ad hook tarafından reddediliyor.
- **Spec değil, spec-input kanoniktir.**
- **Eray'a teknik cümle onaylatma** — ama SEVİYE kararını (medium mu high mı) ONA SOR.
- **Hafıza kararı — bu HANDOFF'tan ÇIKARILDI (2026-09-07 kapanış taraması).** "Yeni oturum
  gündemine alsın" zamanlanmamış bir sözdü ve her devirde taşınıyordu. Gövdesi artık
  `docs/active/CURRENT.md` → Proposed bölümünde, dürüst etiketi ve yeniden açılma koşuluyla
  duruyor (`durum-tetikli-kural-kapisi`). Burada tekrarlanmaz.
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz.
