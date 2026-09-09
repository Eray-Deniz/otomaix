---
task: sektor-bilgi-paketi-plan2
written: 2026-09-09
---

# Resume From

**Sıradaki iş: Task 14** (onay yüzeyi — değişmez anlık görüntü · sinyal sıralaması · onay olayı).
Task 13 indi ve checkpoint 10 kapandı.

**Komut:** `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam**.

**KAYIT TASK.md + bu dosya + git defteridir. BAŞKA DEFTER YOK.**

**Yürütme durumu:** kip **`inline`** · başlangıç çapası `a806e29` · defter penceresi `a806e29`.
**`cp_count` ve `last_checkpoint_ref` TASK.md'nin `Execution State` bölümündedir — buraya
KOPYALANMAZ** (iki yerde tutulunca mutasyon protokolü yalnız birini ilerletiyor ve `ec_state_base_ref`
ıraksama görüp her checkpoint'i öldürüyor).

**Dal:** `feat/sektor-bilgi-paketi-plan2`, **merge EDİLMEDİ**. **Bu oturumun commit'leri PUSH
EDİLMEDİ** — Eray'a sorulmadı; sayı buraya YAZILMAZ, `git rev-list` ile ölçülür. **Uç SHA'sı buraya YAZILMAZ.** Taze ölçüm:
`git rev-list --left-right --count origin/feat/sektor-bilgi-paketi-plan2...HEAD`.

**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: bu oturumda DOKUNULMADI.

## Bu oturum ne yaptı — tek cümle

Task 13 (motorun sonuç katmanı — güvenli fallback · üç bariyer · sonuç tipleri) inline yazıldı;
üç hakem turunda beş yüksek + üç orta/düşük bulgunun sekizi de kapatıldı, kapanış turu Codex kota
sınırına takıldı; test tabanı 3774 → 3876.

# Verification

**Bu oturumda koşulan komutlar ve TAZE çıktıları (hepsi kontrolörün kendi koşumları):**

- `python -m pytest tests/ -q` → **3876 passed in 302.66s**, exit 0 (SON, `33bfae6`, temiz ağaç).
  Ara koşumlar: 3822 (`8b569a0`) · 3871 (`3365574`) · 3874 (`5d7c1ab`).
- Kırmızı ölçümü (Task 13 Step 2): **44 failed / 4 passed**. Geçen dördü Task 8'de inmiş TİP
  sözleşmesini pinler (kodu bu görevde doğmaz) — kendi kırmızıları YOKTUR ve bu dürüstçe böyle
  raporlandı.
- **Mutasyon ölçümü: ON yeni kapının ONU** ayrı ayrı susturuldu, her biri hedef testini kırdı
  (koru-kimlik uzlaşması · yaşayan-olmayan satırın korunması · çift bütünlük kapısı · donmuş
  değerin çözülmesi · kimliğe göre yerleştirme · birim başına tek kararsız · sebep önceliği ·
  ortak takvim yüklemi · geri-koyma sonrası takvim kapısı · kova tür kapısı).
- `ec_ledger_view a806e29… /root/otomaix - --post-window` → **rc=0**, T13 satırı `code`.
- `ec_classify_diff` → `8b569a0` RISKY → `ec_should_checkpoint 1 6 9` → `RUN_RISK`.
- Üç Codex turu KOŞTU (`run_codex_scan`, taban `692e4d9`), ham çıktılar `$CODEX_LOG`'da byte-exact.
  Turların gerçekten koştuğu `grep -c '^\[codex\] Running command'` ile ölçüldü (41 · 26 · 10).
- Sekiz bulgunun SEKİZİ **kontrolörün KENDİ probuyla** doğrulandı — ezberden kabul edilmedi.

**Denenmemiş / doğrulanmamış — dürüst liste:**

- **F8'in kapanışını bağımsız hakem GÖRMEDİ.** Tur 4 hiç koşmadı: Codex **kota sınırı**
  (sıfırlanma 20:34; koşum sayısı 0, rc=1). Eray "beklemeden devam" dedi. Kapanış kontrolörün
  ölçümüne dayanır; aralığı Adım 11'in koşulsuz final incelemesi kapsayacak.
- **Tur 3'ün `approve`'u GÜVENİLİR DEĞİLDİR** ve kapanış kanıtı sayılmadı: cümle ortasında kesildi
  (rc=1), başlattığı probu bitirmeden karar verdi. O probu kontrolör tamamladı — şüphe GERÇEKTİ
  (F8). Kayıtta bu tur "F7 kapalı" için kullanıldı, F8 için KULLANILMADI.
- **Uçtan uca CLI koşumu YAPILMADI.** Motor gerçek bir koşuda hiç çağrılmadı; tüm ölçümler
  fixture ile. Üretim çağıranı Task 16'da doğacak.
- **Denetçi web erişim probu YOK** — üretim hattı hâlâ koşamaz (K-14 kapısı her turu bloke eder).
- **`decide` gerçek denetçi/sentez çıktısıyla hiç sınanmadı.** İlk gerçek ölçüm Task 19'dur.
- **`ruff` bu ortamda kurulu değil** — lint hiç koşmadı. Pyright de koşulmadı.
- **CRM webhook onarımı YAPILMADI** (değişmedi). Canlıya migration dağıtılmadı; pilot koşulmadı.
- Task 14-20 hiç yazılmadı. **Bu oturumun commit'leri push EDİLMEDİ** (sıradaki oturumun
  ilk kararı).

# Risks

- **EN YÜKSEK (işletim) — kimlik doğrulamasız CRM webhook'ları onarılmadı, yalnız KAPATILDI.**
- **Üretim hattı hâlâ koşamaz:** denetçi web probu yok, K-14 kapısı her turu bloke ediyor.
- **Motor çoğunluğu düz yazıdan sayıyor** — sınıf ancak tipli okuma ile biter. Evi açık:
  `docs/active/denetci-denetim-tablosu-tipli-okuma/`. **Yuva: Task 13'ten SONRA, Task 16'dan
  ÖNCE — yani ŞİMDİ sırası geldi**; sert son tarih Task 19.
- **Bir hakem turu ölçümünü bitirmeden `approve` verebilir.** Bu oturumda oldu ve şüphesi
  gerçek çıktı. Kapanış kararı verdict'e DEĞİL, tamamlanmış ölçüme bakar.
- **Migration `036` yerinde düzenlendi** — kabul edilmiş risk; merge sonrası her değişiklik yeni
  numaralı migration ister.
- **Katı Bölüm C biçimi yanlış-pozitif üretebilir ve ÖLÇÜLMEDİ** (ilk gerçek ölçüm Task 19 Step 5).
- **KABUL EDİLMİŞ RİSK (M3) — commit geçmişi tek-commit TDD modeline uymuyor.**
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`).
- **EVSİZ PARK — atomiklik sınıfı depo GENELİ** (değişmedi).

# Notes For Claude/Codex

**Süreç ağırlığı — Eray'ın 2026-09-09 talebi, BAĞLAYICI:**
1. Mutasyon kanıtı yalnız **YENİ** kapıya istenir; kanıtlanmış kapı tekrar ölçülmez.
2. İnceleme turu üretim/test diye **BÖLÜNMEZ** — tek tur.
3. Düzeltme brief'leri **KISA**.
4. Severity kuralı: `critical`/`high` kapatılır, `medium`/`low` `accepted_risk` alır.
   **İSTİSNA (bu oturumda üç kez uygulandı):** gerileme KONTROLÖRÜN KENDİ ürünüyse `accepted_risk`
   yoktur — düzeltilir. İzin önceden var olan borç içindir.
5. Aynı eksen üst üste turlarda varyant üretiyorsa yamamayı bırak, tavanı bekleme — çerçeve
   teşhisiyle kullanıcıya git. **Bu oturumda uygulandı:** F8 varyant olarak yamanmadı, kova
   TÜRÜ sözleşmeye bağlanarak sınıf kapatıldı.

**Her görev dispatch'inde ZORUNLU:**
1. Arayüz eki **bağlayıcıdır**; ilgili hükümler brief'e **harfiyen kopyalanır**.
   **Ek şu an kodun ARKASINDA** — Task 12 `EngineInputs`'a üç kapı ekledi, Task 13 `decide`'ın
   dönüş şeklini ve `_eslesmeyen_ozel_gunler` imzasını değiştirdi; ek bunları BİLMİYOR.
   Çelişkide ÖLÇ.
2. **Ek, sır tarayıcısı tarafından tarama kökünden DIŞLANIYOR** (yanlış alarm). Hakeme gidecekse
   ilgili hükümler prompt'a VERBATIM gömülür ve dışlanma coverage'da beyan edilir.
3. Test komutu sanal ortam aktifleştirilerek koşar (`source .venv/bin/activate`). `python` YOK,
   `.venv` şart.
4. **Taban 3876** (2026-09-09'dan itibaren).
5. `Exec-Kind` **sınıflandırıcıya** göre seçilir. `Exec-*` bloğu mesajın SON PARAGRAFI.
6. **Commit başlığı ≤72 karakter** — `git log -1 --format=%s | wc -c` ile SAY.
7. `Exec-Task` id'sini yazmadan ÖNCE defterde ARA — **pencere içinde** (Plan 1'in `T13`'ü
   pencere DIŞINDA ve başka plana ait; grep tek başına yanıltır).
8. Her commit'ten SONRA defter kapısı koşulur (`ec_ledger_view … --post-window`, rc=0).
9. Uygulayıcı kendi alt-ajanını çağırmaz. **`docs/active/` altına yazmaz.**
10. **İSKELET ÖNCE — her testin kendi kırmızısı ayrı ölçülür.** Kendi kırmızısı OLMAYAN test
    (zaten inmiş sözleşmeyi pinleyen) dürüstçe öyle raporlanır, "geçti" diye sayılmaz.
11. **Kapanış üretilmiş matrisle** kanıtlanır, **boş-küme kontrol kolu** eklenir.
12. **Gönderilen düzyazıya sayı yazma** — ya üreten komutu yanına koy, ya "doğrulanmadı" etiketle.
    **SHA'yı ELLE YAZMA:** bu oturumda `last_checkpoint_ref`'in kuyruğu uydurulmuş, `rev-parse`
    ile yakalanmıştır. Yazdıktan sonra `git rev-parse --verify` ile DOĞRULA.
13. **Hakem/kontrolör önerisi ADAYDIR** — dosyayı açmadan tekrarlanmaz.
14. **Kontrolörün tam test kümesi, veritabanına dokunan bir alt-ajanla ASLA üst üste binmez.**
15. Canlıya hiçbir n8n dosyası körlemesine yüklenmez.

**Task 14'ün dispatch'ine ZORUNLU kalemler:**
- Onay yüzeyi `decide`'ın `EngineResult`'ını TÜKETİR ama kanıtı ÇAĞIRANDAN ALMAZ (arayüz eki R8):
  veritabanından okunur, ikinci bir kurucu YOKTUR.
- `EngineResult` alan kümesi KAPALI (on bir alan); `final_candidate`/`final_decision_log`/iki sha
  **birlikte dolar, birlikte boşalır** — `decide` bunları bozuk çiftte topluca `None` verir.
- **Onay anlık görüntüsünün üretim yazıcısı Task 14'tür** (Task 8 üç yüzeyi buraya bıraktı).
- `approval.to_activation_evidence` **SİLİNDİ** — modülde `ActivationGateEvidence` KURULMAZ,
  import bile edilmez (R8). Tek kurulum yeri Task 15'in `writeback.py`'ıdır.

**Yeni açılan görevin SIRASI GELDİ — Task 16'dan ÖNCE okunacak:**
`docs/active/denetci-denetim-tablosu-tipli-okuma/TASK.md` (proposed).

**EVİ OLAN, TAŞINAN KALEMLER — rolling yeniden yazımda DÜŞÜRÜLMESİN:**
- **`markdown-it-py` bir ÜRETİM bağımlılığıdır** (pinli `4.2.0`), canlıya dağıtılmadı.
  **Ev: Task 18, Step 3.**
- **Task 8 üç yüzeyi Task 15'e bağlı bıraktı** — jeton tüketimi koşmuyor · aktivasyon yükü
  yediye değil altıya varıyor · onay anlık görüntüsünün üretim yazıcısı yok (o Task 14).
  Bağlayıcı: `expected_no_active` eklendiği gün `test_evidence_payload_key_set_is_closed`
  KIRMIZI olur ve elle güncellenir. **Ev: Task 14 + Task 15.**
- **Yol sıra numaraları KONUMSAL** — karşılaştıran her tüketici kimliğe anahtarlar, yola asla.
  **Task 13'te UYGULANDI** (nihai günlük kimliğe göre yeniden numaralanır); tüketici tarafı
  **Ev: Task 14 + Task 15.**
- **K-126 tek-kaynak istisnası KAPALI** — resmîlik ölçütü tipli taşınmadığı için motor onu
  açamıyor. **Ev: arayüz eki revizyonu + denetçi sözleşmesi.**
- **K-03'ün kategori ayağı UYGULANMADI** — girdide anahtar→kategori eşlemesi yok; motor yalnız
  paket TÜR etiketi değişimini ölçer ve öyle adlandırır. **Ev: arayüz eki revizyonu.**
- **Task 10'un TEST dosyaları bağımsız hakem GÖRMEDİ** (biri Task 12'de görüldü).
  **Ev: Adım 11 final inceleme.**
- **Denetçi web probunun üretim sahibi Task 16'dır.**

**Codex çağrısı kurarken — çağrıdan ÖNCE bas:**
1. `COMPANION` **ve** `PROMPT` **çağıran kabukta** kurulu mu (kabuk durumu taşınmaz).
2. `REQUIRED_CURRENT_FILES` SATIR SATIR mı — ve **dışlanan dosya var mı** (arayüz eki dışlanıyor).
3. Taban SHA 40 karakter mi. `CODEX_LOG` yazılabilir mi.
4. Turun gerçekten koştuğunu ÖLÇ: `grep -c '^\[codex\] Running command'`; ~1 ise onay sahtedir.
   **0 ise tur HİÇ KOŞMADI** — bu oturumda kota sınırında böyle oldu ve çıktı yine "verdict"
   biçiminde geldi.
5. **Uzun turları arka planda koştur** — ön planda kabuk 10 dakikada keser. Dış zaman aşımı
   varsayılanı 480s'tir ve bu tura YETMEDİ (rc=124); canlılık probu geçtiyse `CSS_CALL_TIMEOUT`
   1200s ile BİR kez tekrarla.
6. **Kota sınırı gerçek bir dal:** çıktı "Codex did not return valid structured JSON" +
   usage-limit metni olur. Verdict YOKTUR; degradation menüsü işletilir.

**Sır tarayıcısı yanlış alarmı (her oturumda yeniden onay ister).** Substrat şunları dışlıyor:
`tests/test_auditor_orchestration.py` · arayüz eki · `tests/test_plan2_interface_contract.py`.
Üçü de yanlış alarm, gerçek kimlik bilgisi YOK.

- **Eray'a teknik cümle onaylatma** — karar sorularını sade dille, proje-lokal kod referansı
  OLMADAN sor.
- **TEHDİT MODELİNİ ÖNDEN SÖYLE.** Girdi araştırma çıktısıdır — ÖZENSİZ olabilir, SALDIRGAN
  değil. Bu oturumda prompt'a konuldu ve bulguların hepsi doğru katmandan geldi.
- **Bu dosya ROLLING'dir** — her oturumda BAŞTAN yazılır; karar izi `TASK.md` Decisions Log'una gider.
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz (bu yazım hariç).
