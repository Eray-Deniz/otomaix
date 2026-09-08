---
task: sektor-bilgi-paketi-plan2
written: 2026-09-08
---

# Resume From

**Sıradaki iş: Task 8'in İKİ hakem turu — ikisi de KOTA yüzünden koşamadı, kod tarafında
bekleyen düzeltme YOK.**

1. **Kapanış-doğrulama turu (round 2)** — taban `a21d2c92f9148236b9363a3338a42a9a217bc8b6`,
   delta = beş düzeltme commit'i. Prompt hazır ve kanonik: `~/.claude/tmp/` altındaki
   execute prompt dosyasına yeniden yazılır (aşağıdaki "bulgular defteri" ile birlikte).
2. **B turu — test tarafı incelemesi.** A turu yalnız üretim yüzeylerini inceledi; 235 yeni
   testi ve süpürülen iki mevcut test dosyasını **hiçbir hakem GÖRMEDİ**. Doğrulanacak
   iddialar: süpürme tam mı (C4) · yük anahtar kümesi gerçekten türetilmiş mi (C5) ·
   testler-koda-göre yazıldığı için boş implementasyona karşı geçen test var mı (C6).

**Bu ikisi bitmeden yürütme `waiting-review` OLAMAZ ve dal PUSH EDİLEMEZ.**

**Kota:** Codex 2026-09-08 ~12:00 UTC'de limite çarptı; companion'ın verdiği yeniden açılma
saati **1:33 PM**. Yeni oturum önce kotayı yoklasın.

> **SAHTE ONAY UYARISI — bu turda ölçüldü.** Kapanış turu `verdict: approve` yazan bir özet
> döndürdü ama **tek araç çağrısı** yaptı ve hemen ardından `Turn failed` ile düştü: o onay,
> modelin işe başlamadan yazdığı AÇILIŞ planıydı. Bir turu onay saymadan önce
> `grep -c '^\[codex\] Running command'` ile gerçekten çalıştığını ÖLÇ. Karşılaştırma:
> A turu 125 çağrı yaptı ve beş bulgu çıkardı.

**Komut:** `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam**.

**ÖNCE OKU — kanonik ilerleme burada DEĞİL:**
`.superpowers/sdd/2026-08-27-sektor-bilgi-paketi-plan2/progress.md` (git'e girmiyor).

**Yürütme durumu:** kip alt-ajanlı · başlangıç çapası `a806e29` · defter penceresi `a806e29` ·
**`cp_count: 3`** · **`last_checkpoint_ref: 2b468e8d`**.

> **BİLEREK İLERLETİLMEDİ.** §8.6 mutasyon protokolü yalnız Clean/Accepted-risk dallarında
> koşar; bu tur **Fix** dalıydı ve kapanış-doğrulaması yapılmadı. Sonuç fail-safe: sonraki
> checkpoint'in tabanı `2b468e8d` KALIR ve Task 7 + Task 8 + düzeltmelerin hepsini
> kendiliğinden yeniden kapsar.

**Dal:** `feat/sektor-bilgi-paketi-plan2`. Son commit için `git log -1` — bu satıra sha
YAZILMAZ, drift eder. **Bu oturumun commit'leri uzağa PUSH EDİLMEDİ** (sayısı
`git log @{u}..HEAD` ile sayılır; bu satıra yazılmaz).

**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: son commit **`7964ed6`**,
pin manifesti bu commit'e bağlı, hakem turunda çözülebilirliği doğrulandı.
**Bu oturumda dokunulmadı.**

## Bu oturum ne yaptı — tek cümle

Task 8 indi (koşu ve artefakt servisi), bağımsız hakem beş yüksek bulgu verdi, dördü ölçümle
doğrulanıp düzeltildi, biri öncülü çürütülerek reddedildi; iki doğrulama turu kotaya takıldı.

## HAKEM TURUNU KURARKEN — DÖRT ALAN, ÇAĞRIDAN ÖNCE BAS

Bu oturumda aynı sınıf **üç kez** ateşledi ve ~20 dakika yedi. Çağrı fence'inin ilk satırları
dördünü de bassın, sonra çağır:

1. **`PROMPT` yüklendi mi** — dosyayı yazmak YETMEZ (`PROMPT=$(cat -- "$CODEX_PROMPT_FILE")`);
   `echo "${#PROMPT} bayt"`. Kurulmazsa hakem yalnız substrat önsözünü görür ve "anladım"
   diye cevap verir — bu oturumda tam olarak bu oldu.
2. **`REQUIRED_CURRENT_FILES` SATIR SATIR mı** — boşlukla ayırırsan tek uydurma yol olur
   (`$'a\nb'` kullan).
3. **Taban SHA 40 karakter mi** — kısa SHA uzak dal adı sanılır, `couldn't find remote ref`.
4. **`CODEX_LOG` yazılabilir mi** — yoksa çağrı fail-closed reddedilir.

## KUM HAVUZU KABULÜ — HER TURDA YENİDEN KURULUR (kalıcı değil)

Sır tarayıcısı, incelenecek dosyaların çoğunu **yanlış alarmla** dışlıyor: ana servis modülü
gizlediği anahtar adlarını listelediği için, ek ve iki test dosyası ise bir parametre adı
(`...token=`) yüzünden. **Eray 2026-09-08'de bu koşum için kabulü onayladı.** Kabul, kabuk
içinde tarayıcı fonksiyonunun sarmalanmasıyla yapılır (yalnız beş yol kabul edilir, kalan her
dosyada tarayıcı aynen çalışır — bu oturumda 32 gerçek sır dosyası dışlanmaya devam etti).
**Kalıcı değildir; her yeni oturumda yeniden kurulur ve YENİDEN ONAY ister.**

**Kalıcı düzeltme DÜŞÜRÜLDÜ — park edilmedi (2026-09-08 kararı, Eray).** Dürüst etiket:
*çözülmedi + kapsam-dışı-by-design.* Gerekçe ölçüldü: tarayıcı kuralını düzeltmek beş
dosyadan üçünü kurtarır, **en kritik ikisi başka bir kuralla dışlandığı için elle kabul
ihtiyacı yine de kalır** — yani düzeltme ihtiyacı ortadan kaldırmıyor, küçültüyor.
**Yeniden açılma koşulu:** (a) elle kabul yolu kapanırsa, ya da (b) bir turda dosyaların TEK
gizlenme sebebi bu yanlış alarm olursa ve bu tekrarlarsa.

## Sıradaki dispatch'te ÖNDEN bildirilecekler

1. **`markdown-it-py` bir ÜRETİM bağımlılığıdır** (`requirements.txt`, pinli `4.2.0`);
   canlıya dağıtılmadı. **Ev: Task 18, Step 3** — evsiz risk değil.
2. **Migration `036` YERİNDE düzenlendi ve bu bilinçli bir kabul edilmiş risktir.**
   Bağlayıcı koşul: **bu dal merge edilene kadar** yerinde düzenleme serbest; **merge sonrası
   her değişiklik yeni numaralı migration ister.** Öncül ölçüldü: bugün 036'yı uygulamış
   ortam YOK.
3. **Task 8 üç yüzeyi Task 15'e bağlı bıraktı:** jeton tüketimi hiçbir yerde koşmuyor;
   aktivasyon yükünün anahtar kümesi ekin bağladığı yediye değil altıya varıyor (eksik ad
   Task 15'in kalemi, küme türetildiği için o inince kendiliğinden yediye çıkar); onay anlık
   görüntüsünün üretim yazıcısı yok (Task 14).
4. **Yol sıra numaraları KONUMSAL** — sürümler arası karşılaştıran her tüketici kimliğe
   anahtarlamalı, yola ASLA. Task 9, 12, 13 dispatch'lerine taşınır.
5. **Task 7 ve Task 11 planda "Arayüz eki bağlar" satırını TAŞIMIYOR** (20 görevin 18'inde
   var). **Task 11'de bu kontrol ELLE yapılmalı.**
6. **Girdi kapısının ve koşu servisinin test dosyaları büyük** — yeni matris eklerken kap
   çarpımını değil **ayırt eden ekseni** büyüt.
7. **Ekin revizyon kaydı artık BEŞ hüküm taşıyor (R-A…R-E)** — eski metni ezberden uygulama,
   revizyon bölümünü oku.

## Her görev dispatch'inde ZORUNLU olarak taşınacaklar

1. Arayüz eki **bağlayıcıdır**; ilgili hükümler brief'e **harfiyen kopyalanır**.
2. Test komutu sanal ortam aktifleştirilerek koşar (aşağıda Verification).
3. **Taban 6191**; bu sayı düşmeyecek.
4. `Exec-Kind` **sınıflandırıcıya** karşı seçilir. `.sql` çalıştırılabilir sınıfa GİRMEZ.
5. `Exec-*` bloğu mesajın SON PARAGRAFI, co-author trailer'ları **aynı paragrafta**.
6. **Commit başlığı ≤72 karakter** — `git log -1 --format=%s | wc -c` ile SAY.
7. Her commit'ten SONRA defter kapısı koşulur.
8. Uygulayıcı kendi alt-ajanını çağırmaz. **`docs/active/` altına yazmaz.**
9. Codex çağrılarına tam 40 karakterlik SHA verilir.
10. Kapanış **üretilmiş matrisle** kanıtlanır, matris **mutasyonla** sınanır, **boş-küme
    kontrol kolu** eklenir.
11. **Gönderilen düzyazıya sayı yazma** — ya üreten komutu yanına koy, ya "doğrulanmadı" etiketle.
12. **Tarama deseni KAVRAMDAN türetilir**, bulunan örneklerden değil.
13. **Kontrolörün tam test kümesi, veritabanına dokunan bir alt-ajanla ASLA üst üste binmez.**
14. Bir düzeltme, DEĞİŞTİRDİĞİ yapıyı okuyan testleri bayatlatabilir — her turda eski test
    dosyasını yeni modüle karşı koştur.
15. Kimlik kapısı ya kanonik değerle TAM eşleşmeli ya da kümeyi ÜRETEN yapıdan türemeli.
16. Canlıya hiçbir n8n dosyası körlemesine yüklenmez.
17. **Hakem/kontrolör önerisi ADAYDIR.** Bu görevde ölçümde yanlış çıkan öneri/teşhis sayısı
    **dokuz** — bu oturumda bir yeni: hakemin migration bulgusunun öncülü çürüdü.
18. **Kendi probunu da sorgula.** Bu görevde prob **on** kez yanıltmıştı; bu oturumda
    uygulayıcı kendi kirli probunu yakalayıp attı (işlem kapısı testi).
19. **KAPANIŞ SAYIYLA DEĞİL MESAJ KÜMESİ FARKIYLA KANITLANIR.**
20. **Üç tur aynı ekseni getiriyorsa dördüncü nokta-düzeltmesi AÇMA.**
21. **Bir KURAL beşinci kez kandırılıyorsa kural yazmayı bırak, DEĞİŞMEZ kur.**
22. **Beyan bayatlarsa beyan olmamaktan kötüdür** — her ilan edilen açığa TRIPWIRE.
23. **ORACLE İMPLEMENTASYONDAN BAĞIMSIZ OLMALI.**
24. **ÇAKILI SAYILARI TEK GEÇİŞTE ÖLÇ.**
25. **PROB KENDİ ÖLÇTÜĞÜ AİLEYE DARALTILMALI.**
26. **YENİ — İNCELEME TURU DA BÖLÜNÜR.** Tek pencerede rapor üretemeyecek kapsam AÇILMADAN
    bölünür; bölme ekseni **dosya türüdür** (üretim ↔ test), commit aralığı DEĞİL. Prompt'un
    başına "keşfi bütçele, raporu YAZ" ve öncelik sırası konur.

# Verification

**Koşulan komutlar ve TAZE çıktıları (2026-09-08, hepsi kontrolörün KENDİ koşumları):**

- `cd apps/social/backend && source .venv/bin/activate && python -m pytest tests/ -q`
  → Task 8 sonrası **6165 passed in 715.38s**; düzeltmeler sonrası **6191 passed in 719.77s**,
  ikisi de exit 0, temiz ağaçta. Seyir: 5913 → 6165 → **6191**. Hiçbir test silinmedi.
- `ec_ledger_view a806e29… /root/otomaix - --post-window` → **rc=0**, her commit'ten sonra.
- **Ek ↔ migration hizası bağımsız çıkarıldı:** ekin SQL bloğu ile `036`'nın kilitli alan
  kümesi ayrı ayrı ayrıştırılıp karşılaştırıldı → **EŞİT**; her ikisinde de DELETE kolu ve
  genişletilmiş tetikleyici var.
- **Hakem bulgularının öncülleri ölçüldü:** `activate_package` iki booleana olduğu gibi
  güveniyor (satır 815-826, jeton tüketimi yok) · anlık görüntü `None` iken açık soru sayısı
  0 yazılıyordu · `036` taban revizyonunda VARDI (`d1edd51`, 2026-09-06) · geliştirme
  veritabanında iki tablonun ikisi de YOK (`to_regclass` → NULL) · dal main'e merge EDİLMEMİŞ.
- **Import kenarı hâlâ kapalı:** yaşam döngüsü modülünün `sector_pipeline` importu TEK.
- **Codex turları:** ön-tarama 1 (kurulum hatası yüzünden ikinci kez koşuldu) · checkpoint
  tek-parça 1 (**zaman aşımı, rapor YOK**) · checkpoint A 1 (**5 yüksek bulgu**) ·
  kapanış 2 (**biri kısa-SHA ile hiç başlamadı, biri kotada düştü**).

**Denenmemiş / doğrulanmamış senaryolar — dürüst liste:**

- **Kapanış-doğrulama turu KOŞMADI** (kota). Dört düzeltmenin gerçekten kapandığı **bağımsız
  hakem tarafından doğrulanmadı**; kontrolörün kendi ölçümü ve testler var, hakem yok.
- **B turu KOŞMADI.** 235 yeni testi ve süpürülen iki mevcut test dosyasını hiçbir hakem
  görmedi.
- **F3'ün karşılaştır-ve-yaz'ı GERÇEK eşzamanlılıkla sınanmadı** — yüklem ardışık çağrılarla
  kanıtlandı; "kaybeden reddedilir" iddiası PostgreSQL satır kilidi semantiğine dayanıyor,
  ölçülmüş bir iç içe geçmeye değil.
- **F4'ün kapısı işbirlikçidir, kum havuzu değildir** — işlem açıp ortada commit'leyen bir
  çağıranı yakalayamaz; ölçülen tek şey otomatik-commit çağıranın artık veriye dokunmadan
  reddedildiğidir. Bugün erişilebilir bir istismar yolu BULUNAMADI (tek üretim çağıranı zaten
  işlem içindeydi).
- **F1'in uçtan uca aktivasyon yolu doğrulanamaz** — bağlı olduğu iki yazıcı da yazılmadı
  (anlık görüntü üreticisi Task 14, aktivasyon kapısı Task 15).
- **Yaşam döngüsü yardımcılarının ek listesini aşıp aşmadığı** — uygulayıcı "aşmıyor" dedi ve
  gerekçesini yazdı; bağımsız hakem bunu doğrulamadı, kontrolör de ölçmedi.
- **`markdown-it-py` canlıya dağıtılmadı**; Docker imajı yeniden kurulmadı.
- **`telegramApi` credential'ının canlı token taşıdığı DOĞRULANMADI** (değişmedi).
- **CRM webhook onarımı YAPILMADI** — yalnız kapatıldı (değişmedi).
- PG 18.3 dışında sürüm denenmedi. Canlıya hiçbir migration dağıtılmadı; pilot koşulmadı.
  Dal **PUSH EDİLMEDİ**, merge EDİLMEDİ.
- Task 9–20 hiç yazılmadı.

# Risks

- **EN YÜKSEK — dört düzeltme bağımsız doğrulama GÖRMEDİ.** Hepsi yüksek şiddetli güvenlik/
  bütünlük bulgusuydu ve kapanışları yalnız kontrolör ölçümüne dayanıyor. Kapanış turu yeni
  oturumun İLK işidir.
- **Sahte onay sınıfı ölçüldü:** kotada düşen bir tur, açılış planını `verdict: approve`
  olarak döndürebiliyor. Tur sayısını ölçmeden onay sayma.
- **Migration `036` yerinde düzenlendi** — kabul edilmiş risk, koşulu yukarıda. Koşul
  ihlal edilirse (merge sonrası yerinde düzenleme) dağıtılmış şema ile kod ayrışır.
- **Katı Bölüm C biçimi yanlış-pozitif üretebilir ve bu ÖLÇÜLMEDİ** (değişmedi; ilk gerçek
  ölçüm Task 19 Step 5).
- **Ayrıştırıcı sınırı sonlu (100) — DÜŞÜRÜLDÜ, park EDİLMEDİ** (değişmedi).
- **Checkpoint 6 `approve` ile DEĞİL, override ile kapandı** (değişmedi). `cp_count`
  ilerletilmedi ve bu tur da ilerletilmedi — fail-safe yön.
- **EN YÜKSEK (işletim) — kimlik doğrulamasız CRM webhook'ları onarılmadı, yalnız KAPATILDI.**
- **KABUL EDİLMİŞ RİSK (M3) — commit geçmişi tek-commit TDD modeline uymuyor.** Task 8 bunu
  kendi etiketiyle büyüttü: modüller önce, testler sonra yazıldı; Step-2 kırmızısı modüller
  kaldırılıp geri konarak üretildi. **B turunun C6 kalemi tam olarak bunu ölçecek.**
- **EVSİZ PARK — atomiklik sınıfı depo GENELİ** (değişmedi).
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`).

# Notes For Claude/Codex

- **Hakem turlarını Claude koşar — SORMA.** Eray'ın kalıcı kuralı.
- **Turun gerçekten koştuğunu ÖLÇ, verdict'e bakma.** Araç çağrısı sayısı ~1 ise onay sahtedir.
- **Hakem çağrısının dört alanını çağrıdan önce BAS** (yukarıda). Bu oturumda üç kez yanıldım.
- **İNCELEMELER DE BÖLÜNÜR** — tek parça tur bu oturumda rapor üretemeden zaman aşımına uğradı.
- **Prob otoriteye sorulmadan kanıt sayılmaz** — ve prob KENDİ ölçtüğü aileye daraltılmalı.
- **Hakem raporunu doğrulanmamış iddia say** — bu oturumda bir yüksek bulgunun ÖNCÜLÜ çürüdü.
- **Alt-ajan model alanını HİÇ GEÇME.** Çıplak takma ad hook tarafından reddediliyor.
- **Spec değil, spec-input kanoniktir.**
- **Eray'a teknik cümle onaylatma** — bu oturumda İlke-8 kapısı bir soruyu haklı olarak
  reddetti (seçeneklere dosya adı yazmıştım); soruyu kod referansı olmadan yeniden yaz.
- **TEHDİT MODELİNİ ÖNDEN SÖYLE.** Girdi araştırma çıktısıdır — ÖZENSİZ olabilir, SALDIRGAN değil.
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz.
