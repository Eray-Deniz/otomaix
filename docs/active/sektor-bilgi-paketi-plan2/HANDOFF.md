---
task: sektor-bilgi-paketi-plan2
written: 2026-09-08
---

# Resume From

> ## ÖNCE BU — Task 10 BEKLİYOR (Eray kararı, 2026-09-08)
>
> Sıradaki iş Task 10 DEĞİL. Önce test matrisi küçültülür — kaydı ayrı klasörde değil,
> **`TASK.md`'nin "ÖN KOŞUL — Task 10'dan ÖNCE" bölümündedir.**
> Ölçüm: arka uç kümesi **6380 vaka / 715 saniye**; bunun **4414'ü** tek dosyada
> (`tests/test_brief_doctor.py`), **3240'ı TEK fonksiyonda** (`test_kod_citi_ekseni` =
> kümenin **%51'i**). Kıyas: Plan 1 kapanışında küme **577 vaka / 105 saniye**ydi.
> Her hakem turu, her düzeltme turu ve her doğrulama bu çarpımı baştan koşuyor.
> Eray'ın gerekçesi: bu şekilde test olmaz, bu şekilde plan bitmez.
> **Kapanış ölçütü vaka sayısı DEĞİL, mutasyon kanıtıdır** — küçültmeden önce kırmızı olan
> her mutasyon sonra da kırmızı kalmalı.


**Sıradaki iş: Task 9.** Task 8'in checkpoint'i bu oturumda KAPANDI — önceki oturumun kotaya
takılıp açık bıraktığı iki tur da koştu, ikisi de bulgu üretti, hepsi kapatıldı.

**Komut:** `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam**.

**KAYIT TASK.md + bu dosya + git defteridir. BAŞKA DEFTER YOK.**

> **KALDIRILAN İŞARETÇİ (2026-09-08).** Bu satır 2026-09-08'e kadar
> `.superpowers/sdd/.../progress.md`'yi "önce oku, kanonik ilerleme orada" diye gösteriyordu ve
> bir oturum açılışını yanlış yönlendirdi. O dizini Superpowers'ın `subagent-driven-development`
> skill'i kendi kendine yazar; `.superpowers/sdd/.gitignore` içeriği `*` olduğu için hiçbir
> zaman commit'e girmez ve geçmiş kayıtlarda görünmez. **Bu projenin task-handoff yapısının
> parçası DEĞİLDİR ve devir-teslimde işaretçisi olmaz.** Yeni oturum onu okumaz.

**Yürütme durumu:** kip alt-ajanlı · başlangıç çapası `a806e29` · defter penceresi `a806e29` ·
**`cp_count: 3`** · **`last_checkpoint_ref: 2b468e8d`**.

> **BİLEREK İLERLETİLMEDİ.** §8.6 mutasyon protokolü yalnız Clean/Accepted-risk dallarında
> koşar. Son bağımsız hakem verdict'i `needs-attention`'dı; blokeri (B5) kapatıldı ama
> bağımsız yeniden-doğrulama GÖRMEDİ (aşağıda, kabul edilmiş risk). Fail-safe yön: sonraki
> checkpoint'in tabanı `2b468e8d` KALIR ve Task 7 + Task 8 + bütün düzeltmeleri kendiliğinden
> yeniden kapsar.

**Dal:** `feat/sektor-bilgi-paketi-plan2`. Son commit için `git log -1` — bu satıra sha
YAZILMAZ, drift eder. **Bu dal uzağa PUSH EDİLDİ** — uzak uç `3c41b24` (2026-09-07 22:47).
Ondan sonraki commit'ler gönderilmedi; farkı `git rev-list --left-right --count
origin/feat/sektor-bilgi-paketi-plan2...HEAD` ile ÖLÇ — bu satıra sayı yazılmaz, drift eder.
**DÜZELTME 2026-09-08:** bu satır "hiç push edilmedi" diyordu; ölçüm aksini gösterdi.

**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: son commit **`7964ed6`**,
pin manifesti bu commit'e bağlı. **Bu oturumda dokunulmadı.**

## Bu oturum ne yaptı — tek cümle

Task 8'in iki açık doğrulama turu koştu (kapanış + test tarafı), toplam beş yeni bulgu çıktı,
hepsi ölçümle doğrulanıp kapatıldı; bir kontrolör inisiyatifi (B5) hedefini tutturamadı ve
sistemik-sınıf kuralıyla durdurulup dürüst etiketine indirildi.

## HAKEM TURUNU KURARKEN — DÖRT ALAN, ÇAĞRIDAN ÖNCE BAS

Bu oturumda çağrı kurulumu ilk denemede YANLIŞTI ve tur iptal edildi. Çağrı fence'inin ilk
satırları dördünü de bassın, sonra çağır:

1. **`PROMPT` yüklendi mi** — dosyayı yazmak YETMEZ (`PROMPT=$(cat -- "$CODEX_PROMPT_FILE")`);
   `echo "${#PROMPT} bayt"`.
2. **`REQUIRED_CURRENT_FILES` SATIR SATIR mı** — boşlukla ayırırsan tek uydurma yol olur.
3. **Taban SHA 40 karakter mi** — kısa SHA uzak dal adı sanılır.
4. **`CODEX_LOG` yazılabilir mi** — yoksa çağrı fail-closed reddedilir.

**BEŞİNCİ ALAN — BU OTURUMDA ÖĞRENİLDİ, ATLAMA.** Sır tarayıcısı kabulü **substrat dizini
prefix'iyle** çağrılır (`$WT/$relpath`), canlı depo yoluyla DEĞİL. Kabulü `/root/otomaix/`
prefix'ine göre yazarsan sessizce hiçbir şey yapmaz ve dosyalar yine gizlenir. **SONEK
eşleştir** ve çağrıdan ÖNCE pozitif + negatif kontrol bas (kabul edilenler geçiyor mu, kabul
listesinde OLMAYAN gerçek sır dosyası hâlâ dışlanıyor mu).

## KUM HAVUZU KABULÜ — HER TURDA YENİDEN KURULUR (kalıcı değil)

Sır tarayıcısı, incelenecek dosyaları yanlış alarmla dışlıyor. **Eray 2026-09-08'de bu
oturumun turları için kabulü onayladı.** Ölçüldü: 497 izlenen dosyanın 55'i içerik taramasıyla
dışlanıyor; bunların **beşi** inceleme için zorunlu — ana koşu servisi (kayıtlardan sildiği
anahtar adlarının yasak listesini içeriyor), bağlayıcı ek ve üç test dosyası (`provenance_token=`
parametre adı; bir tanesinde kayıt-temizleme testleri için KASTEN uydurulmuş sahte anahtarlar).
**Gerçek kimlik bilgisi taşıyan hiçbiri kabul edilmedi**; kalan 50 dosya gizli kaldı ve her
turda negatif kontrolle doğrulandı. **Kalıcı değildir; her yeni oturumda YENİDEN ONAY ister.**

**Kalıcı düzeltme DÜŞÜRÜLDÜ — park edilmedi (2026-09-08 kararı, Eray).** Dürüst etiket:
*çözülmedi + kapsam-dışı-by-design.* Yeniden açılma koşulu: (a) elle kabul yolu kapanırsa,
ya da (b) bir turda dosyaların TEK gizlenme sebebi bu yanlış alarm olursa ve bu tekrarlarsa.

## Sıradaki dispatch'te ÖNDEN bildirilecekler

1. **`markdown-it-py` bir ÜRETİM bağımlılığıdır** (`requirements.txt`, pinli `4.2.0`);
   canlıya dağıtılmadı. **Ev: Task 18, Step 3.**
2. **Migration `036` YERİNDE düzenlendi, kabul edilmiş risk.** Bağlayıcı koşul: **bu dal merge
   edilene kadar** yerinde düzenleme serbest; **merge sonrası her değişiklik yeni numaralı
   migration ister.** Öncül ölçüldü: 036'yı uygulamış ortam YOK.
3. **Task 8 üç yüzeyi Task 15'e bağlı bıraktı:** jeton tüketimi hiçbir yerde koşmuyor;
   aktivasyon yükünün anahtar kümesi ekin bağladığı yediye değil altıya varıyor; onay anlık
   görüntüsünün ÜRETİM YAZICISI YOK (Task 14).
   **YENİ — Task 15 için bağlayıcı:** `expected_no_active` eklendiği gün
   `test_evidence_payload_key_set_is_closed` KIRMIZI olur ve ELLE güncellenmesi gerekir. Bu
   artık belgeli bir kapıdır, sürpriz değil (B2 turunda docstring'i gerçeğe indirildi).
   **Ayrıca:** onay anlık görüntüsü yazıcısı yazılırken `acik_sorular` YALNIZ `list`/`tuple`
   üretmelidir — R-F bunu bağlar.
4. **Yol sıra numaraları KONUMSAL** — sürümler arası karşılaştıran her tüketici kimliğe
   anahtarlamalı, yola ASLA. Task 9, 12, 13 dispatch'lerine taşınır.
5. **Task 7 ve Task 11 planda "Arayüz eki bağlar" satırını TAŞIMIYOR** (20 görevin 18'inde
   var). **Task 11'de bu kontrol ELLE yapılmalı.**
6. **Girdi kapısının ve koşu servisinin test dosyaları büyük** — yeni matris eklerken kap
   çarpımını değil **ayırt eden ekseni** büyüt.
7. **Ekin revizyon kaydı artık ALTI hüküm taşıyor (R-A…R-F)** — ezberden uygulama, revizyon
   bölümünü OKU. R-F kanıt alanlarının şekil kapısını bağlar.

## Her görev dispatch'inde ZORUNLU olarak taşınacaklar

1. Arayüz eki **bağlayıcıdır**; ilgili hükümler brief'e **harfiyen kopyalanır**.
2. Test komutu sanal ortam aktifleştirilerek koşar (aşağıda Verification).
3. **Taban 6341**; bu sayı düşmeyecek.
4. `Exec-Kind` **sınıflandırıcıya** karşı seçilir. `.sql` çalıştırılabilir sınıfa GİRMEZ.
5. `Exec-*` bloğu mesajın SON PARAGRAFI, co-author trailer'ları **aynı paragrafta**.
6. **Commit başlığı ≤72 karakter** — `git log -1 --format=%s | wc -c` ile SAY.
7. **`Exec-Task` id'sini brief'e yazmadan ÖNCE defterde ARA.** Bu oturumda kontrolör
   `T8-fix2`'yi ikinci kez kullandırdı; iki farklı iş aynı adı taşıyor, geri alınamaz.
8. Her commit'ten SONRA defter kapısı koşulur.
9. Uygulayıcı kendi alt-ajanını çağırmaz. **`docs/active/` altına yazmaz.**
10. Codex çağrılarına tam 40 karakterlik SHA verilir.
11. Kapanış **üretilmiş matrisle** kanıtlanır, matris **mutasyonla** sınanır, **boş-küme
    kontrol kolu** eklenir.
12. **Gönderilen düzyazıya sayı yazma** — ya üreten komutu yanına koy, ya "doğrulanmadı" etiketle.
13. **Tarama deseni KAVRAMDAN türetilir**, bulunan örneklerden değil.
14. **Kontrolörün tam test kümesi, veritabanına dokunan bir alt-ajanla ASLA üst üste binmez.**
15. Bir düzeltme, DEĞİŞTİRDİĞİ yapıyı okuyan testleri bayatlatabilir — her turda eski test
    dosyasını yeni modüle karşı koştur.
16. Kimlik kapısı ya kanonik değerle TAM eşleşmeli ya da kümeyi ÜRETEN yapıdan türemeli.
17. Canlıya hiçbir n8n dosyası körlemesine yüklenmez.
18. **Hakem/kontrolör önerisi ADAYDIR.** Bu görevde ölçümde yanlış çıkan öneri/teşhis sayısı
    **dokuz** (bu oturumda yeni yanlış çıkan YOK — B turunun dört bulgusunun dördü de doğrulandı).
19. **Kendi probunu da sorgula.** Bu görevde prob **on** kez yanıltmıştı.
20. **KAPANIŞ SAYIYLA DEĞİL MESAJ KÜMESİ FARKIYLA KANITLANIR.**
21. **Üç tur aynı ekseni getiriyorsa dördüncü nokta-düzeltmesi AÇMA.** Bu oturumda ATEŞLEDİ
    (B1 → B5 → B5'in çözünürlüğü) ve döngü gerçekten durduruldu.
22. **Bir KURAL beşinci kez kandırılıyorsa kural yazmayı bırak, DEĞİŞMEZ kur.**
23. **Beyan bayatlarsa beyan olmamaktan kötüdür** — her ilan edilen açığa TRIPWIRE.
24. **ORACLE İMPLEMENTASYONDAN BAĞIMSIZ OLMALI.** Bu oturumda B2 tam olarak bu yüzden açıldı.
25. **ÇAKILI SAYILARI TEK GEÇİŞTE ÖLÇ.**
26. **PROB KENDİ ÖLÇTÜĞÜ AİLEYE DARALTILMALI.**
27. **İNCELEME TURU DA BÖLÜNÜR.** Bölme ekseni **dosya türüdür** (üretim ↔ test), commit
    aralığı DEĞİL. Bu oturumda çalıştı: B turu üretim turunun göremediği dört bulgu çıkardı.
    **GÖREVİN KENDİSİ BÖLÜNMEZ (2026-09-08 Eray kararı):** plan görevi TEK PARÇA dispatch
    edilir, inceleme aynı aralık üzerinden iki turda koşar (A = üretim dosyaları, B = test
    dosyaları). Aralık bölünmediği için iki turun arasına bulgu düşmez. TASK.md'deki
    "alt parçalar hâlinde dispatch" paragrafı DARALTILDI — kural değil, ölçüm kaydıdır.
28. **TESTLER KODDAN SONRA YAZILDIYSA KAPANIŞ ÖLÇÜTÜ MUTASYON KANITIDIR** — her yeni test için
    "şunu bozdum → şu test kırmızı oldu" satırı istenir; kanıtsız kalem kapatılmış SAYILMAZ.
30. **İSKELET ÖNCE — HER TESTİN KENDİ KIRMIZISI AYRI ÖLÇÜLÜR.** Uygulayıcı brief'inde
    **işin sırası** olarak yazılır, tavsiye olarak değil: (1) modül boş iskelet kurulur
    (fonksiyon ve tip adları var, gövdeler `raise NotImplementedError`), (2) her test yazılır
    ve **tek tek** koşulup kendi kırmızısı ölçülür, (3) sonra gövdeler yazılır.
    **Modül yokken alınan tek `ImportError` kırmızı SAYILMAZ** — o, N testi birden kapsayan
    TEK ölçümdür ve hiçbir testin ayırt ettiğini kanıtlamaz.
    **Neden bu madde var (ölçüldü, üç görev):** Task 7, 8 ve 9'un üçünde de testler tek toplu
    kırmızıyla yazıldı ve üçünde de hakem AYNI sınıfı buldu — *tespit edemediği garantiyi
    onaylayan test*. Task 9'da bu sınıf B turunun DÖRT yüksek bulgusunun tamamıydı: sırayı
    kapılamayan sıra testi · üç eşlemeden birini sınayan takma-ad testi · hangi aracın
    yoklandığını iddia etmeyen ön kontrol testi · yalnız bir alanı sınayan tip testi.
    Üç kez tekrarlayan kusur olağan değil, **düzeltilmemiş** demektir; brief'e cümle eklemek
    üç kez denendi ve üçünde de yetmedi, o yüzden bu bir SIRA kuralıdır.

29. **SÜRE TAHMİNİ VERİRKEN ELDEKİ ÖLÇÜMÜ KULLAN.** Tam test takımı **tek koşumda ~715 saniye**;
    bunu içeren hiçbir tur "15 dakika" olamaz. Bu oturumda ölçüm elde varken yanlış tahmin
    verildi ve Eray haklı olarak itiraz etti.

# Task 9 — durum (2026-09-08 kapanışı)

Task 9 indi (`f95cff5`), iki hakem turu koştu (A = üretim, B = test), **yedi yüksek + iki orta**
bulgu çıktı, düzeltme turu `4831015` ile indi. Kontrolörün ölçümü, bulgu başına:

| # | bulgu | durum | kontrolörün ölçümü |
|---|---|---|---|
| F1 | eşleme konumsal, "ölçülemez" deniyordu | **KAPANDI** | `auditors.py:517,524` — `icerik_ozeti != canonical_sha(sources[i])` ve boş özet reddediliyor |
| F2 | pin sonrası ikinci okuma (TOCTOU) | **KAPANDI** | `contracts.require_pinned_text` tek okur+doğrular; `auditors.py`'da `read_text` KALMADI |
| F3 | URL sayısı raporun kendi beyanından | **ÇÖZÜLMEDİ + EVİ VAR** | iddia gerçeğe indirildi (`auditors.py:636-644`); ev **Task 10** — imza değişikliği ek revizyonu ister |
| F4 | K-137 mutlak garanti dili | **KAPANDI** (iddia daraltıldı) | garanti cümlesi ölçülen kümeye indirildi |
| B1 | sıra kapısının ayırt eden testi yok | **KAPANDI** | `test_validate_report_rejects_swapped_section_order` |
| B2 | takma-ad testi üç eşlemenin birini sınıyor | **KAPANDI** | `test_packet_ref_does_not_alias_the_caller_mapping`, alan başına parametrize |
| B3 | kimlik taraması sonlu liste | **KAPANDI** (iddia daraltıldı + küme türetildi) | `test_packet_excludes_every_identity_named_by_pin_or_config`; docstring semantik-olumsuzlama gerekçesini taşıyor |
| B4 | prob argümanı yok sayılıyor | **KAPANDI** | `assert prob.cagrilar == [ARAC]`, iki dalda birden |
| B5 | tip iddiası tek alanı sınıyor | **KAPANDI** | `test_audit_report_rejects_a_foreign_row_in_each_sequence_field` |

**Hedef test dosyası: `75 passed in 0.62s`** (Task 9 sonrası 39'du).

# Verification

**Koşulan komutlar ve TAZE çıktıları (2026-09-08, hepsi kontrolörün KENDİ koşumları):**

- `cd apps/social/backend && source .venv/bin/activate && python -m pytest tests/ -q`
  → dört kez koştu: **6336** (Task 8 + F1 şekil kapısı) · **6340** (B turu düzeltmeleri) ·
  **6341** (B5 kapısı) · **6341 passed in 715.20s** (son, açıklama düzeltmesinden sonra).
  Hepsi exit 0, temiz ağaçta. Seyir: 5913 → 6165 → 6191 → 6336 → 6340 → **6341**.
  **Hiçbir test silinmedi.**
- `ec_ledger_view a806e29… /root/otomaix - --post-window` → **rc=0**, her commit'ten sonra.
- **Kontrolörün BAĞIMSIZ mutasyon koşumları (uygulayıcının raporu devralınmadı):**
  (a) yürütücünün `except` kolu `except Exception` yapıldı → B3'ün yeni testi KIRMIZI
  (`DID NOT RAISE`), eski taksonomi testi YEŞİL kaldı; (b) `runs.py`'ye kilit alan sahte bir
  fonksiyon eklendi → B5 kapısı KIRMIZI; (c) `build_rollback_plan` ve `mint_evidence_token`
  kilit satırları SİLİNDİ → ilgili üç test dosyasının **558 testi de YEŞİL kaldı** (B1'in
  öncülünün ölçümü). Üçünde de mutasyon geri alındı, ağaç temiz doğrulandı.
- **F1'in öncülü ölçüldü:** geçici prob — `""`, `{}`, `set()`, `()` → `open_questions_count=0`
  ve `checklist_approved=True`; `int`/`bool`/`None`/`float` → alan-dışı `TypeError`. Prob
  koşuldu ve SİLİNDİ.
- **Codex turları (hepsi araç-çağrısı sayısıyla doğrulandı, verdict'e güvenilmedi):**
  kapanış-2 **21 çağrı / 9 dk** (1 yüksek) · kapanış-3 **28 çağrı / 9 dk** (`approve`, bulgu
  yok) · B turu **26 çağrı / 8 dk** (3 yüksek + 1 orta) · B-kapanış **13 çağrı / 8 dk**
  (1 yüksek). Bir tur kurulum hatası yüzünden başlar başlamaz iptal edildi.

**Denenmemiş / doğrulanmamış senaryolar — dürüst liste:**

- **`4831015` ÜSTÜNDE TAM TEST KÜMESİ KOŞMADI.** Eray koşturmayı durdurdu (2026-09-08). Ölçülen
  tek şey hedef dosyadır (75 passed). **Kalan 6300+ vakanın bu commit'le yeşil kaldığı
  DOĞRULANMADI** — yeni oturumun ilk mekanik işi budur.
- **`4831015` için MUTASYON KANITI ALINMADI.** Uygulayıcı raporunu yazmadan durduruldu; brief
  her kalem için "şunu bozdum → şu test kırmızı" satırı istiyordu, o satırlar YOK. Testlerin
  VARLIĞI kontrolörce ölçüldü, **ayırt ettikleri ölçülmedi**.
- **`4831015` bağımsız hakem GÖRMEDİ** — kapanış-doğrulama turu koşulmadı.
- **`auditors.py`'da erişilemez-kod uyarıları görülmüştü** (tip analizi, üç satır); düzeltme
  sonrası tekrar ÖLÇÜLMEDİ. Erişilemez kapı = sessiz fail-open adayı.

- **`a488769` (B5 açıklama düzeltmesi) bağımsız hakem GÖRMEDİ.** Kabul edilmiş risk; gerekçe
  ve kapısı TASK.md'de. Kontrolör metni kodla karşılaştırarak doğruladı, hakem doğrulamadı.
- **B5 kapısının iki bilinen kör noktası KAPATILMADI ve bu bilinçlidir:** (a) zaten beyan
  edilmiş bir fonksiyona eklenen İKİNCİ kilit çağrısı görünmez; (b) korunan-yol değerleri
  çözülmeyen test ADLARIDIR — adı geçen test silinse kapı yeşil kalır. İkisi de artık
  docstring'de adıyla yazılı. **Yeniden açılma koşulu:** bu kör noktalardan biri gerçek bir
  gerilemeye yol açarsa, ya da `mint_evidence_token`'a ikinci bir doğrudan çağıran eklenirse
  (istisna gerekçesi o gün bayatlar).
- **`build_rollback_plan` ve `mint_evidence_token` kilitleri için davranışsal test YOK.**
  Ölçüldü ve gerekçesi kapının verisinde yazılı: biri iki satır önce ürettiği uuid4 üzerine
  kilitleniyor (çekişme yapısal olarak imkânsız), öteki zaten kilitli çağırandan geliyor.
- **F3'ün karşılaştır-ve-yaz'ı GERÇEK eşzamanlılıkla sınanmadı.**
- **F4'ün kapısı işbirlikçidir, kum havuzu değildir** — işlem açıp ortada commit'leyen bir
  çağıranı yakalayamaz.
- **F1'in uçtan uca aktivasyon yolu doğrulanamaz** — bağlı olduğu iki yazıcı da yazılmadı
  (anlık görüntü üreticisi Task 14, aktivasyon kapısı Task 15).
- **`markdown-it-py` canlıya dağıtılmadı**; Docker imajı yeniden kurulmadı.
- **`telegramApi` credential'ının canlı token taşıdığı DOĞRULANMADI** (değişmedi).
- **CRM webhook onarımı YAPILMADI** — yalnız kapatıldı (değişmedi).
- PG 18.3 dışında sürüm denenmedi. Canlıya hiçbir migration dağıtılmadı; pilot koşulmadı.
  Dal `3c41b24`'e kadar **PUSH EDİLDİ**, sonrası gönderilmedi; **merge EDİLMEDİ.**
- Task 9–20 hiç yazılmadı.

# Risks

- **`last_checkpoint_ref` ilerletilmedi** — fail-safe yön, gerekçesi yukarıda. Sonraki
  checkpoint Task 7 + Task 8 + bütün düzeltmeleri **YENİDEN** kapsayacak; kapsamı büyük olacak,
  **bölünerek dispatch edilmeli** (üretim ↔ test ekseni).
  **Bu bir TEKRAR'dır, incelenmemiş yığın DEĞİL** — ölçüldü 2026-09-08 (TASK.md'nin checkpoint
  kayıtları): checkpoint 6 zaten `2b468e8d` tabanıyla koştu (sekiz Codex turu; Task 7 incelendi),
  Task 8 ise dört tur gördü (kapanış-2 taban `a21d2c9` · kapanış-3 · B turu taban `3c41b24` ·
  B-kapanış). Bu aralıkta bağımsız hakemin görmediği KOD/TEST commit'i tektir: **`a488769`**
  (ölçüldü: `git show --stat` → yalnız `tests/test_pipeline_runs.py`). Ondan sonraki
  **`65fb649`** de hakem görmedi ama BELGE-YALNIZDIR (TASK.md + HANDOFF.md).
  Kapsamı "incelenmemiş" diye okuyan bir dispatch, yapılmış işi baştan inceletir.
- **Migration `036` yerinde düzenlendi** — kabul edilmiş risk, koşulu yukarıda.
- **Katı Bölüm C biçimi yanlış-pozitif üretebilir ve bu ÖLÇÜLMEDİ** (değişmedi; ilk gerçek
  ölçüm Task 19 Step 5).
- **Ayrıştırıcı sınırı sonlu (100) — DÜŞÜRÜLDÜ, park EDİLMEDİ** (değişmedi).
- **Checkpoint 6 `approve` ile DEĞİL, override ile kapandı** (değişmedi).
- **EN YÜKSEK (işletim) — kimlik doğrulamasız CRM webhook'ları onarılmadı, yalnız KAPATILDI.**
- **KABUL EDİLMİŞ RİSK (M3) — commit geçmişi tek-commit TDD modeline uymuyor.** Task 8 bunu
  büyütmüştü; **B turu bunu ölçtü ve karşılığını kurdu** (mutasyon kanıtı). Risk küçüldü ama
  yok olmadı: mutasyon kanıtı yalnız B turunda düzeltilen testler için var, Task 8'in kalan
  test kütlesi için YOK.
- **EVSİZ PARK — atomiklik sınıfı depo GENELİ** (değişmedi).
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`).

# Notes For Claude/Codex

- **Hakem turlarını Claude koşar — SORMA.** Eray'ın kalıcı kuralı.
- **Turun gerçekten koştuğunu ÖLÇ, verdict'e bakma.** `grep -c '^\[codex\] Running command'`;
  ~1 ise onay sahtedir. Bu oturumda dört turun dördü de 13-28 çağrı yaptı.
- **Sır tarayıcısı kabulünü SONEK ile eşleştir** (yukarıda, beşinci alan) ve pozitif+negatif
  kontrol bas.
- **İNCELEMELER BÖLÜNÜR** — bu oturumda B turu ayrı koşuldu ve dört bulgu çıkardı; tek parça
  koşsaydı görülmezdi.
- **Hakem raporunu doğrulanmamış iddia say** — ama bu oturumda dördü de doğrulandı; hakem
  kalitesi düştü diye VARSAYMA, her seferinde ölç.
- **Kendi inisiyatifini de hakemin bulgusu gibi ölç.** B5 kontrolörün kendi fikriydi, "sınıfı
  kapatır" diye sunuldu, kapatmadı ve fazladan bir tur doğurdu.
- **Alt-ajan model alanını HİÇ GEÇME.** Çıplak takma ad hook tarafından reddediliyor.
- **Spec değil, spec-input kanoniktir.**
- **Eray'a teknik cümle onaylatma.** Bu oturumda karar soruları (kum havuzu kabulü, B5'in
  akıbeti) sade dille soruldu ve işe yaradı.
- **TEHDİT MODELİNİ ÖNDEN SÖYLE.** Girdi araştırma çıktısıdır — ÖZENSİZ olabilir, SALDIRGAN
  değil. Bu cümle prompt'a konduğunda hakemler severity'yi doğru kalibre etti.
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz.
