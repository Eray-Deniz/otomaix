---
task: sektor-bilgi-paketi-plan2
written: 2026-09-09
---

> ⚠️ YÜRÜTME AÇIK (başlangıç: 2026-09-09 08:49) — bu anlatı yürütme öncesine aittir; güncel durum
> TASK.md "Notes For Claude" + git defterinden okunur, çelişkide onlar esastır.

# Resume From

**Sıradaki iş: Task 10.** Önündeki test matrisi ön koşulu 2026-09-09'da KAPANDI (`458661b`);
ölçümleri ve kabul edilmiş riskleri `TASK.md`'nin "ÖN KOŞUL" bölümünde.

**Komut:** `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam**.

**KAYIT TASK.md + bu dosya + git defteridir. BAŞKA DEFTER YOK.** (`.superpowers/sdd/.../progress.md`
bu projenin yapısının parçası DEĞİLDİR; gitignore'lu, commit'e girmez, yeni oturum onu okumaz.)

**Yürütme durumu:** kip alt-ajanlı · başlangıç çapası `a806e29` · defter penceresi `a806e29` ·
**`cp_count: 3`** · **`last_checkpoint_ref: 2b468e8d`** — BİLEREK ilerletilmedi (fail-safe:
sonraki checkpoint Task 7 + Task 8 + düzeltmeleri yeniden kapsar). Bu bir TEKRAR'dır,
incelenmemiş yığın DEĞİL: o aralıkta bağımsız hakemin görmediği kod/test commit'leri
`a488769` ve **`458661b`**'dir.

**Dal:** `feat/sektor-bilgi-paketi-plan2`, merge EDİLMEDİ. Son commit `git log -1` ile,
uzağa fark `git rev-list --left-right --count origin/feat/sektor-bilgi-paketi-plan2...HEAD`
ile ÖLÇÜLÜR — bu satıra sha da sayı da yazılmaz, drift eder.

**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: son commit **`7964ed6`**,
pin manifesti buna bağlı. Bu oturumda dokunulmadı.

## Bu oturum ne yaptı — tek cümle

Test kümesinin 704 saniyesi aşama aşama ölçüldü, yavaşlığın matris değil fixture kurulumu
olduğu çıktı, üç kaldıraç (şablon veritabanı · not önbelleği · 3-yollu kapsama dizisi) indi
ve küme mutasyon kanıtıyla birlikte **286 saniyeye** düştü.

## HAKEM TURUNU KURARKEN — BEŞ ALAN, ÇAĞRIDAN ÖNCE BAS

1. **`PROMPT` yüklendi mi** — dosyayı yazmak YETMEZ (`PROMPT=$(cat -- "$CODEX_PROMPT_FILE")`).
2. **`REQUIRED_CURRENT_FILES` SATIR SATIR mı** — boşlukla ayırırsan tek uydurma yol olur.
3. **Taban SHA 40 karakter mi** — kısa SHA uzak dal adı sanılır.
4. **`CODEX_LOG` yazılabilir mi** — yoksa çağrı fail-closed reddedilir.
5. **Sır tarayıcısı kabulü SONEK ile eşleşir** — substrat dizini prefix'iyle (`$WT/$relpath`),
   canlı depo yoluyla DEĞİL; çağrıdan ÖNCE pozitif + negatif kontrol bas.

**KUM HAVUZU KABULÜ HER OTURUMDA YENİDEN ONAY İSTER.** Sır tarayıcısı yanlış alarmla dosya
dışlıyor; 2026-09-08'de beş dosya için kabul alındı (gerçek kimlik bilgisi taşıyan hiçbiri
kabul edilmedi, kalan 50 dosya gizli kaldı). Kalıcı düzeltme DÜŞÜRÜLDÜ (çözülmedi +
kapsam-dışı-by-design); yeniden açılma koşulu: elle kabul yolu kapanırsa, ya da bir turda
dosyaların TEK gizlenme sebebi bu yanlış alarm olur ve tekrarlarsa.

## Sıradaki dispatch'te ÖNDEN bildirilecekler

1. **`markdown-it-py` bir ÜRETİM bağımlılığıdır** (pinli `4.2.0`), canlıya dağıtılmadı.
   **Ev: Task 18, Step 3.**
2. **Migration `036` YERİNDE düzenlendi**, kabul edilmiş risk. Bu dal merge edilene kadar
   yerinde düzenleme serbest; **merge sonrası her değişiklik yeni numaralı migration ister.**
3. **Task 8 üç yüzeyi Task 15'e bağlı bıraktı** (jeton tüketimi koşmuyor · aktivasyon yükü
   yediye değil altıya varıyor · onay anlık görüntüsünün üretim yazıcısı yok, Task 14).
   Bağlayıcı: `expected_no_active` eklendiği gün `test_evidence_payload_key_set_is_closed`
   KIRMIZI olur ve elle güncellenir. `acik_sorular` YALNIZ `list`/`tuple` üretmeli (R-F).
4. **Yol sıra numaraları KONUMSAL** — karşılaştıran her tüketici kimliğe anahtarlar, yola asla.
   Task 12, 13 dispatch'lerine taşınır.
5. **Task 11 planda "Arayüz eki bağlar" satırını TAŞIMIYOR** — o kontrol ELLE yapılmalı.
6. **Yeni matris eklerken kap çarpımını değil AYIRT EDEN EKSENİ büyüt.** Artık ölçülmüş bir
   deseni var: çit ekseni tam çarpımdan (3240) 3-yollu kapsama dizisine (280) indi ve dört
   mutasyonun hepsinde kırmızı kaldı. Yeni eksen yazarken aynı biçimi kullan.
7. **Ekin revizyon kaydı ALTI hüküm taşıyor (R-A…R-F)** — ezberden uygulama, bölümü OKU.

## Her görev dispatch'inde ZORUNLU olarak taşınacaklar

1. Arayüz eki **bağlayıcıdır**; ilgili hükümler brief'e **harfiyen kopyalanır**.
2. Test komutu sanal ortam aktifleştirilerek koşar.
3. **Taban 3458** (2026-09-09'dan itibaren); bu sayı düşmeyecek. Önceki taban 6341/6416'ydı ve
   "düşmeyecek" diyordu; `458661b` ile BİLİNÇLE 3458'e indi (tam çarpım → kapsama dizisi).
   Düşüş silme değil tekrar temizliğidir ve kapsama kapısıyla kanıtlanır.
4. `Exec-Kind` **sınıflandırıcıya** karşı seçilir: yalnız `tests/` dokunan commit `red-only`,
   yalnız üretim `green-only`, ikisi `code`. `.sql` çalıştırılabilir sınıfa GİRMEZ.
5. `Exec-*` bloğu mesajın SON PARAGRAFI, co-author trailer'ları **aynı paragrafta**.
6. **Commit başlığı ≤72 karakter** — `git log -1 --format=%s | wc -c` ile SAY.
7. **`Exec-Task` id'sini yazmadan ÖNCE defterde ARA** — iki FARKLI iş aynı adı taşımasın.
8. Her commit'ten SONRA defter kapısı koşulur (`ec_ledger_view … --post-window`, rc=0).
9. Uygulayıcı kendi alt-ajanını çağırmaz. **`docs/active/` altına yazmaz.**
10. Codex çağrılarına tam 40 karakterlik SHA verilir.
11. Kapanış **üretilmiş matrisle** kanıtlanır, matris **mutasyonla** sınanır, **boş-küme
    kontrol kolu** eklenir.
12. **Gönderilen düzyazıya sayı yazma** — ya üreten komutu yanına koy, ya "doğrulanmadı" etiketle.
13. **Tarama deseni KAVRAMDAN türetilir**, bulunan örneklerden değil.
14. **Kontrolörün tam test kümesi, veritabanına dokunan bir alt-ajanla ASLA üst üste binmez.**
15. Bir düzeltme, DEĞİŞTİRDİĞİ yapıyı okuyan testleri bayatlatabilir — eski test dosyasını
    yeni modüle karşı koştur.
16. Kimlik kapısı ya kanonik değerle TAM eşleşir ya da kümeyi ÜRETEN yapıdan türer.
17. Canlıya hiçbir n8n dosyası körlemesine yüklenmez.
18. **Hakem/kontrolör önerisi ADAYDIR.** Bu görevde ölçümde yanlış çıkan öneri sayısı **dokuz**.
19. **Kendi probunu da sorgula.** Bu görevde prob **on bir** kez yanılttı (bu oturumda bir kez:
    hücre kimliği addan ayrıştırıldı, `c-tablolu` gövdesindeki tire boyutları kaydırdı ve
    kapsama dizisi 280 yerine 500 çıktı).
20. **KAPANIŞ SAYIYLA DEĞİL MESAJ KÜMESİ FARKIYLA KANITLANIR.**
21. **Üç tur aynı ekseni getiriyorsa dördüncü nokta-düzeltmesi AÇMA.**
22. **Bir KURAL beşinci kez kandırılıyorsa kural yazmayı bırak, DEĞİŞMEZ kur.**
23. **Beyan bayatlarsa beyan olmamaktan kötüdür** — her ilan edilen açığa TRIPWIRE.
24. **ORACLE İMPLEMENTASYONDAN BAĞIMSIZ OLMALI.**
25. **ÇAKILI SAYILARI TEK GEÇİŞTE ÖLÇ.**
26. **PROB KENDİ ÖLÇTÜĞÜ AİLEYE DARALTILMALI.**
27. **İNCELEME TURU BÖLÜNÜR** (A = üretim dosyaları, B = test dosyaları), **görevin kendisi
    BÖLÜNMEZ** (2026-09-08 Eray kararı): plan görevi tek parça dispatch edilir, inceleme aynı
    aralık üzerinden iki turda koşar.
28. **TESTLER KODDAN SONRA YAZILDIYSA KAPANIŞ ÖLÇÜTÜ MUTASYON KANITIDIR** — her yeni test için
    "şunu bozdum → şu test kırmızı oldu" satırı istenir; kanıtsız kalem kapatılmış SAYILMAZ.
29. **SÜRE TAHMİNİ VERİRKEN ELDEKİ ÖLÇÜMÜ KULLAN.** Tam test takımı artık **~286 saniye**
    (2026-09-09 öncesi ~715s'ti); Codex turu 8-9 dk; uygulayıcı turu 15-36 dk.
30. **İSKELET ÖNCE — HER TESTİN KENDİ KIRMIZISI AYRI ÖLÇÜLÜR.** Brief'e **işin sırası** olarak
    yazılır: (1) boş iskelet (`raise NotImplementedError`), (2) her test tek tek koşulup kendi
    kırmızısı ölçülür, (3) sonra gövdeler. **Modül yokken alınan tek `ImportError` kırmızı
    SAYILMAZ.** Task 7, 8 ve 9'un üçünde de hakem aynı sınıfı buldu; brief'e cümle eklemek üç
    kez denendi ve yetmedi, o yüzden bu bir SIRA kuralıdır.
31. **KAPSAMI VAKA SAYISIYLA DEĞİL ÖLÇÜLMÜŞ SÜRE PAYIYLA KUR** (2026-09-09'da öğrenildi).
    `--durations=0` ile aşama dökümü al; setup/call/teardown ayrı toplanır.

# Verification

**Bu oturumda koşulan komutlar ve TAZE çıktıları (hepsi kontrolörün kendi koşumları):**

- `python -m pytest tests/ -q --durations=0` → **6416 passed in 704.37s**, exit 0 (ÖNCE,
  `4831015`). Bu, devir notunun "tam küme koşmadı" açık kalemini de kapattı.
- `python -m pytest tests/ -q --durations=15` → **3458 passed in 286.36s**, exit 0 (SONRA,
  `458661b`), temiz ağaçta.
- Aşama payları (ÖNCE): setup **355.0s** · call 317.1s · teardown 21.7s. 128 setup ≥1.5s,
  ortalama 2.56s.
- Şablon veritabanı: drop+create 0.15s + 36 migration 2.39s = **2.54s** ↔ TEMPLATE klonu **0.24s**.
- Önbellek: çit testleri 115.48s → 79.30s; 18011 `bd.run` çağrısının **8154'ü** tekrar (%45.3).
- Kapsama dizisi: 3240 → **280 hücre**; `test_brief_doctor.py` 155.5s → **38.8s**.
- **Mutasyon kanıtı, küçültmeden ÖNCE alındı:** maske söküldü 696 → 59 · tur9 540 → 48 ·
  tur10 396 → 35 · tur12 0 → 0 (tam matris de yakalamıyor).
- **Bağımsız mutasyon:** üretimdeki `_cit_maskesi` hep-`False` yapıldı → **279 test kırmızı**;
  geri alındı, `git diff` ile üretim modülünün temizliği doğrulandı.
- `ec_ledger_view a806e29… /root/otomaix - --post-window` → **rc=0**, iki commit'te de.

**Denenmemiş / doğrulanmamış — dürüst liste:**

- **`458661b` ve `a488769` bağımsız hakem GÖRMEDİ.** Bu oturumda hiç hakem turu koşulmadı.
- **Dört/beş boyutun aynı anda tuttuğu çit hatası kapsam dışı** — kabul edilmiş risk;
  yeniden açılma koşulu ve tek satırlık düzeltmesi (`_KAPSAMA_DERECESI`) dosyada.
- **"Vacuous'luk ayıraç biçiminden bağımsızdır" iddiası DÜŞÜRÜLDÜ** (park değil): küçültülmüş
  kümede iddiayı sınayan grup sayısı ölçüldü ve **0**. Yeniden açılma koşulu dosyada.
- **Şablon veritabanı paralel koşumda (pytest-xdist) denenmedi** — bu proje paralel koşmuyor.
- **Önbellek anahtarının sınırı:** `bd`den iki kat derine inen bir mock yazılırsa tripwire
  testi kırılır (kasıtlı); üç kat derin mock kapsam dışıdır.
- **`markdown-it-py` canlıya dağıtılmadı**; Docker imajı yeniden kurulmadı.
- **CRM webhook onarımı YAPILMADI** — yalnız kapatıldı (değişmedi).
- **`telegramApi` credential'ının canlı token taşıdığı DOĞRULANMADI** (değişmedi).
- PG 18.3 dışında sürüm denenmedi. Canlıya migration dağıtılmadı; pilot koşulmadı.
- Task 10–20 hiç yazılmadı.

# Risks

- **EN YÜKSEK (işletim) — kimlik doğrulamasız CRM webhook'ları onarılmadı, yalnız KAPATILDI.**
- **`last_checkpoint_ref` ilerletilmedi** — fail-safe; sonraki checkpoint kapsamı büyük olacak,
  üretim ↔ test ekseninde bölünerek koşulmalı.
- **Migration `036` yerinde düzenlendi** — kabul edilmiş risk, koşulu yukarıda.
- **Katı Bölüm C biçimi yanlış-pozitif üretebilir ve bu ÖLÇÜLMEDİ** (ilk gerçek ölçüm Task 19 Step 5).
- **Ayrıştırıcı sınırı sonlu (100)** — DÜŞÜRÜLDÜ, park edilmedi.
- **Checkpoint 6 `approve` ile DEĞİL, override ile kapandı.**
- **KABUL EDİLMİŞ RİSK (M3) — commit geçmişi tek-commit TDD modeline uymuyor.** Mutasyon kanıtı
  yalnız B turunda düzeltilen testler ve `458661b` için var; Task 8'in kalan test kütlesi için YOK.
- **EVSİZ PARK — atomiklik sınıfı depo GENELİ** (değişmedi).
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`).

# Notes For Claude/Codex

- **Hakem turlarını Claude koşar — SORMA.** Eray'ın kalıcı kuralı.
- **Turun gerçekten koştuğunu ÖLÇ, verdict'e bakma:** `grep -c '^\[codex\] Running command'`;
  ~1 ise onay sahtedir.
- **Uzun Codex turlarını arka planda koştur** — ön planda kabuk 10 dakikada keser.
- **Hakem raporunu doğrulanmamış iddia say**, ama hakem kalitesi düştü diye de VARSAYMA — ölç.
- **Kendi inisiyatifini de hakemin bulgusu gibi ölç.**
- **Alt-ajan model alanını HİÇ GEÇME.** Çıplak takma ad hook tarafından reddediliyor.
- **Spec değil, spec-input kanoniktir.**
- **Eray'a teknik cümle onaylatma** — karar sorularını sade dille sor; bu oturumda öyle yapıldı
  ve işe yaradı (kapalı DB ad kümesine üçüncü ad ekleme kararı).
- **TEHDİT MODELİNİ ÖNDEN SÖYLE.** Girdi araştırma çıktısıdır — ÖZENSİZ olabilir, SALDIRGAN değil.
- **Bu dosya ROLLING'dir** — her oturumda BAŞTAN yazılır, tarihçe biriktirmez; karar izi
  `TASK.md`'nin Decisions Log'una gider.
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz.
