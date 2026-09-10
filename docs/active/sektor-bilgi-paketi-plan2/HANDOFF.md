---
task: sektor-bilgi-paketi-plan2
written: 2026-09-10
---

> ⚠️ YÜRÜTME AÇIK (başlangıç: 2026-08-30 11:36) — bu anlatı yürütme öncesine aittir; güncel durum TASK.md "Notes For Claude" + git defterinden okunur, çelişkide onlar esastır.

# Resume From

**Sıradaki iş: Task 14** (onay yüzeyi — değişmez anlık görüntü · sinyal sıralaması · onay olayı).
Task 13 indi ve checkpoint 10 kapandı. Araya giren yan görev
`denetci-denetim-tablosu-tipli-okuma` **BİTTİ** (2026-09-10).

**Komut:** `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam**.

**KAYIT TASK.md + bu dosya + git defteridir. BAŞKA DEFTER YOK.**

**Yürütme durumu:** kip **`inline`** · başlangıç çapası `a806e29` · defter penceresi `a806e29`.
**`cp_count` ve `last_checkpoint_ref` TASK.md'nin `Execution State` bölümündedir — buraya
KOPYALANMAZ.**

**Dal:** `feat/sektor-bilgi-paketi-plan2`. **Bu oturumun commit'leri PUSH EDİLMEDİ** — sayı
buraya YAZILMAZ, ölç: `git rev-list --left-right --count origin/feat/sektor-bilgi-paketi-plan2...HEAD`.
**Uç SHA'sı buraya YAZILMAZ.** (Oturum başında önceki 6 commit push EDİLDİ, Eray onayıyla.)

**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: **BU OTURUMDA DEĞİŞTİ** —
`31a4656`, iki sözleşme dosyası + damga. Uzak deposu YOK, yerel. Pin
(`shared/contracts/research-contracts.pin.json`) aynı turda güncellendi.

## Bu oturum ne yaptı — tek cümle

Yan görev `denetci-denetim-tablosu-tipli-okuma` uçtan uca yapıldı: sözleşme yapısallaştırıldı,
denetim tablosu tipli okunur oldu, motorun çoğunluk kapısı düz yazıdan saymayı bıraktı, koşu
bağı kuruldu; iki bağımsız hakem turu koştu ve sekiz bulgunun yedisi kapatıldı.

# Verification

**Bu oturumda koşulan komutlar ve TAZE çıktıları (hepsi kontrolörün kendi koşumları):**

- `python -m pytest tests/ -q` → **3931 passed in 297.25s**, exit 0 (SON, `9a603be`).
  Ara koşumlar: 3909 · 3916 (koşu bağı) · 3925 (`2c429b9`) · 3929 (`4408dbe`).
  Taban 3876 → **+55 test**.
- **Mutasyon ölçümü: YİRMİ ALTI yeni kapının YİRMİ ALTISI** ayrı ayrı susturuldu, her biri hedef
  testini kırdı. Betik: `mutasyon.py` (oturum scratchpad'i; kalıcı değil).
- **Prob düzeltmesi (ölçüldü):** ilk mutasyon koşumu DÖRT kapıyı sahte YEŞİL gösterdi. Sebep
  Python bayt kodu önbelleği: her mutasyon aynı dosya BOYUTUNU üretiyor ve aynı saniye içinde
  yazılanlar öncekinin `.pyc`'sini kullanıyordu. Prob `__pycache__` silme + değişken dolgu ile
  düzeltildi. **Bu sınıf bir dahaki mutasyon koşumunda da geçerlidir.**
- İki Codex turu KOŞTU (`run_codex_scan`, base-review). Turların gerçekten koştuğu
  **stderr'den** ölçüldü (21 · 28 komut). **`[codex]` işaretleri `$CODEX_LOG`'a DEĞİL stderr'e
  akar** — koşum sayısını logda aramak 0 verir ve turu "hiç koşmadı" sanırsın.
- Sekiz bulgunun sekizi **kontrolörün KENDİ probuyla** doğrulandı — ezberden kabul edilmedi.
- Defter kapısı üç commit'in üçünde de rc=0.

**Denenmemiş / doğrulanmamış — dürüst liste:**

- **SON commit (`9a603be`) bağımsız hakem GÖRMEDİ.** Kapanış turu `4408dbe` tabanındaydı;
  sonraki iki düzeltme (bayrak katlaması + bayat belge) ondan sonra indi. Aralığı Adım 11'in
  koşulsuz final incelemesi kapsayacak.
- **Uçtan uca CLI koşumu YAPILMADI.** Motor gerçek bir koşuda hiç çağrılmadı; tüm ölçümler
  fixture ile. İlk gerçek ölçüm Task 19.
- **Kapanış turunun YÜKSEK bulgusunun kalan ayağı KAPANMADI** (atıf ADAYA bağlı değil, ALAN
  düzeyinde). Evi açık: `docs/active/denetci-atif-aday-kimligi/`.
- **İki düşük bulgu ÖNCE bırakılıp SONRA kapatıldı** (Eray itirazı): bayat docstring +
  bayrak yazım katlaması. İkincisi Task 12'den beri var olan bir körlüktü ve `[marka-adı]`
  bayrağını etkisiz kılıyordu.
- **Denetçi web erişim probu YOK** — üretim hattı hâlâ koşamaz (K-14 kapısı her turu bloke eder).
- **`ruff` bu ortamda kurulu değil** — lint hiç koşmadı. Pyright de koşulmadı.
- **CRM webhook onarımı YAPILMADI.** Canlıya migration dağıtılmadı; pilot koşulmadı.
- Task 14-20 hiç yazılmadı.

# Risks

- **EN YÜKSEK (işletim) — kimlik doğrulamasız CRM webhook'ları onarılmadı, yalnız KAPATILDI.**
- **Üretim hattı hâlâ koşamaz:** denetçi web probu yok.
- **Atıf ADAYA bağlı DEĞİL** — aynı alanın herhangi bir denetçi satırı herhangi bir adayı
  yetkilendirebiliyor. Sözleşme revizyonu ister; evi açık, sert son tarih Task 19.
- **Sözleşme penceresi Task 19'da KAPANIYOR.** Pilottan sonra sözleşme değişikliği araştırmaları
  ikinci kez ürettirir. Bekleyen sözleşme işi: atıf-aday kimliği.
- **Migration `036` yerinde düzenlendi** — kabul edilmiş risk.
- **Katı Bölüm C biçimi yanlış-pozitif üretebilir ve ÖLÇÜLMEDİ** (ilk gerçek ölçüm Task 19).
- **KABUL EDİLMİŞ RİSK (M3) — commit geçmişi tek-commit TDD modeline uymuyor.**
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`).
- **EVSİZ PARK — atomiklik sınıfı depo GENELİ** (değişmedi).

# Notes For Claude/Codex

**Süreç ağırlığı — Eray'ın talimatları, BAĞLAYICI:**
1. **(2026-09-10, YENİ ve ÜSTÜN)** Hakem bulgularından **YALNIZ critical/high düzeltilir**;
   orta/düşük RAPORLANIR ve devam edilir. Bu, "gerileme kontrolörün kendi ürünüyse
   `accepted_risk` yoktur" istisnasının ÜSTÜNE gelir — çelişkide **severity yönetir.**
2. Mutasyon kanıtı yalnız **YENİ** kapıya istenir; kanıtlanmış kapı tekrar ölçülmez.
3. İnceleme turu üretim/test diye **BÖLÜNMEZ** — tek tur.
4. Düzeltme brief'leri **KISA**.
5. Aynı eksen üst üste turlarda varyant üretiyorsa **yamamayı bırak**, çerçeve teşhisiyle
   kullanıcıya git. **Bu oturumda uygulandı:** atıf-aday bağı üç turda üç varyant verdi;
   üçüncüde durup ayrı göreve ev verildi.

**Her görev dispatch'inde ZORUNLU:**
1. Arayüz eki **bağlayıcıdır**; ilgili hükümler brief'e **harfiyen kopyalanır**. Ek bu oturumda
   GÜNCELLENDİ (AuditRow · denetim_tablosu · kaynak_seti_sha · koşu bağı · atıf-aday bağı ·
   yetkili sayı · yedi sebep). Çelişkide ÖLÇ.
2. **Ek, sır tarayıcısı tarafından tarama kökünden DIŞLANIYOR.** Ayrıca `test_auditor_
   orchestration.py` de dışlanıyor — birinci hakem turu o dosyayı GÖRMEDİ, kapanış turu HEAD
   git nesnesinden okuyabildiğini beyan etti. Hakeme gidecekse dışlanma coverage'da BEYAN EDİLİR.
3. Test komutu sanal ortam aktifleştirilerek koşar (`source .venv/bin/activate`).
4. **Taban 3931** (2026-09-10'dan itibaren).
5. `Exec-Kind` **sınıflandırıcıya** göre seçilir. `Exec-*` bloğu mesajın SON PARAGRAFI.
6. **Commit başlığı ≤72 karakter** — `git log -1 --format=%s | wc -c` ile SAY.
7. `Exec-Task` id'sini yazmadan ÖNCE defterde ARA — **pencere içinde**.
8. Her commit'ten SONRA defter kapısı koşulur (`ec_ledger_view … --post-window`, rc=0).
9. Uygulayıcı kendi alt-ajanını çağırmaz. **`docs/active/` altına yazmaz.**
10. **İSKELET ÖNCE — her testin kendi kırmızısı ayrı ölçülür.** Kendi kırmızısı OLMAYAN test
    dürüstçe öyle raporlanır.
11. **Kapanış üretilmiş matrisle** kanıtlanır, **boş-küme kontrol kolu** eklenir.
12. **Gönderilen düzyazıya sayı yazma** — ya üreten komutu yanına koy, ya "doğrulanmadı" etiketle.
13. **Hakem/kontrolör önerisi ADAYDIR** — dosyayı açmadan tekrarlanmaz.
14. **Kontrolörün tam test kümesi, veritabanına dokunan bir alt-ajanla ASLA üst üste binmez.**
15. Canlıya hiçbir n8n dosyası körlemesine yüklenmez.

**Task 14'ün dispatch'ine ZORUNLU kalemler:**
- Onay yüzeyi `decide`'ın `EngineResult`'ını TÜKETİR ama kanıtı ÇAĞIRANDAN ALMAZ (R8):
  veritabanından okunur, ikinci bir kurucu YOKTUR.
- `EngineResult` alan kümesi KAPALI (on bir alan); `final_candidate`/`final_decision_log`/iki sha
  **birlikte dolar, birlikte boşalır**.
- **Onay anlık görüntüsünün üretim yazıcısı Task 14'tür.**
- `approval.to_activation_evidence` **SİLİNDİ** — modülde `ActivationGateEvidence` KURULMAZ.

**Codex çağrısı kurarken — çağrıdan ÖNCE bas:**
1. `COMPANION` **ve** `PROMPT` **çağıran kabukta** kurulu mu (kabuk durumu taşınmaz).
2. `REQUIRED_CURRENT_FILES` SATIR SATIR mı — ve **dışlanan dosya var mı**.
3. Taban SHA 40 karakter mi. `CODEX_LOG` yazılabilir mi.
4. **Turun koştuğunu STDERR'den ölç:** `grep -c '^\[codex\] Running command'` **çağrının stderr
   çıktısında** — `$CODEX_LOG`'da DEĞİL. Log'da aramak her zaman 0 verir ve turu "hiç koşmadı"
   sanırsın; bu oturumda böyle bir yanlış ölçüm yapıldı ve düzeltildi.
5. **Uzun turları arka planda koştur** — ön planda kabuk 10 dakikada keser. `CSS_CALL_TIMEOUT`
   1200s bu oturumda iki turda da YETTİ (ölçülen süre ~8-12 dk).
6. **Kota sınırı gerçek bir dal:** çıktı "Codex did not return valid structured JSON" +
   usage-limit metni olur. Verdict YOKTUR.

**Sır tarayıcısı yanlış alarmı (her oturumda yeniden onay ister).** Substrat şunları dışlıyor:
`tests/test_auditor_orchestration.py` · arayüz eki · `tests/test_plan2_interface_contract.py` ·
ve `sector_pipeline/runs.py`. Hepsi yanlış alarm, gerçek kimlik bilgisi YOK.

**EVİ OLAN, TAŞINAN KALEMLER — rolling yeniden yazımda DÜŞÜRÜLMESİN:**
- **`markdown-it-py` bir ÜRETİM bağımlılığıdır** (pinli `4.2.0`), canlıya dağıtılmadı.
  **Ev: Task 18, Step 3.**
- **Task 8 üç yüzeyi Task 15'e bağlı bıraktı** — jeton tüketimi koşmuyor · aktivasyon yükü
  yediye değil altıya varıyor · onay anlık görüntüsünün üretim yazıcısı yok (o Task 14).
  Bağlayıcı: `expected_no_active` eklendiği gün `test_evidence_payload_key_set_is_closed`
  KIRMIZI olur ve elle güncellenir. **Ev: Task 14 + Task 15.**
- **Yol sıra numaraları KONUMSAL** — karşılaştıran her tüketici kimliğe anahtarlar, yola asla.
  **Ev: Task 14 + Task 15.**
- **K-126 tek-kaynak istisnası KAPALI** — resmîlik ölçütü tipli taşınmadığı için motor onu
  açamıyor. **Ev: arayüz eki revizyonu + denetçi sözleşmesi.**
- **K-03'ün kategori ayağı UYGULANMADI.** **Ev: arayüz eki revizyonu.**
- **Task 10'un TEST dosyaları bağımsız hakem GÖRMEDİ.** **Ev: Adım 11 final inceleme.**
- **Denetçi web probunun üretim sahibi Task 16'dır.**
- **Atıf ADAYA bağlanmalı** (kapanış turu, yüksek — kalan ayak).
  **Ev: `docs/active/denetci-atif-aday-kimligi/` · sert son tarih Task 19.**

**EVSİZ KALEM YOK.** (2026-09-10 kapanışında iki düşük bulgu "karar Eray'ın" diye buraya
yazılmıştı; Eray haklı olarak itiraz etti — ikisi de kontrolörün işiydi ve kapatıldı:
bayrak yazım katlaması + bayat docstring. Ders: küçük ve kapsamı belli bir düzeltmeyi
"severity kuralı" diye kullanıcıya taşımak kuralın amacı DEĞİLDİR; kural büyük/riskli işleri
sınırlar, üç satırlık kendi hatanı devretmeyi değil.)

- **Eray'a teknik cümle onaylatma** — karar sorularını sade dille, proje-lokal kod referansı
  OLMADAN sor. Bu oturumda iki karar sorusu bu biçimde soruldu ve ikisi de yanıtlandı.
- **TEHDİT MODELİNİ ÖNDEN SÖYLE.** Girdi araştırma çıktısıdır — ÖZENSİZ olabilir, SALDIRGAN
  değil. İki hakem turunda da prompt'a konuldu ve bulguların hepsi doğru katmandan geldi.
- **Bu dosya ROLLING'dir** — her oturumda BAŞTAN yazılır; karar izi `TASK.md` Decisions Log'una gider.
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz (bu yazım hariç).
