---
task: sektor-bilgi-paketi-plan2
written: 2026-09-10
---

# Resume From

> ⚠️ YÜRÜTME AÇIK (başlangıç: 2026-09-10 oturumu) — bu anlatı yürütme öncesine aittir;
> güncel durum TASK.md "Notes For Claude" + git defterinden okunur, çelişkide onlar esastır.


**Sıradaki iş: Task 15** (draft yazımı · yerinde güncelleme K-106 · aktivasyon zinciri ·
yetki zorlaması K-103). Task 14 indi ve **checkpoint 11 `approve` ile kapandı**.

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

Task 14 uçtan uca yapıldı: onay yüzeyi kuruldu (kilitli koşudan basılan değişmez görüntü,
sinyal sıralaması, onay/ret olayı), motorun bulguya üreticisini yazması eklendi, dört Codex
turu koştu ve iki yüksek + iki orta + bir düşük bulgunun hepsi karara bağlandı.

# Verification

**Bu oturumda koşulan komutlar ve TAZE çıktıları (hepsi kontrolörün kendi koşumları):**

- `python -m pytest tests/ -q` → **4002 passed in 314.46s**, exit 0 (SON, `576569e`).
  Ara koşumlar: 3969 · 3992 · 3998. Taban 3931 → **+71 test**.
- **Mutasyon ölçümü: OTUZ kapının OTUZU** ayrı ayrı susturuldu, her biri hedef testini kırdı
  (rc=0; tek `SAHTE-YEŞİL` ya da `DESEN-YOK` yok). Betik: `mutasyon.py` (oturum scratchpad'i;
  kalıcı değil).
- **Canlı veritabanı sorgusu:** `social.sector_package_runs` tablosu **YOK** (036 dağıtılmadı).
  Görüntü şemasının sürüm 1'de kalmasının gerekçesi bu ölçümdür — varsayım değil.
- **Dört Codex turu KOŞTU** (`run_codex_scan`, base-review). Koşum sayıları stderr'den ölçüldü:
  40 · 22 · 30 · 32 komut. **`[codex]` işaretleri `$CODEX_LOG`'a DEĞİL stderr'e akar.**
- Beş bulgunun beşi **kontrolörün KENDİ probuyla** doğrulandı — ezberden kabul edilmedi.
- Defter kapısı altı commit'in altısında da `rc=0`.

**Denenmemiş / doğrulanmamış — dürüst liste:**

- **Uçtan uca CLI koşumu YAPILMADI.** Motor ve onay yüzeyi gerçek bir koşuda hiç çağrılmadı;
  tüm ölçümler fixture ile. İlk gerçek ölçüm Task 19.
- **Denetçi web erişim probu YOK** — üretim hattı hâlâ koşamaz (K-14 kapısı her turu bloke eder).
- **`ruff` bu ortamda kurulu değil** — lint hiç koşmadı. Pyright de koşulmadı.
- **CRM webhook onarımı YAPILMADI.** Canlıya migration dağıtılmadı; pilot koşulmadı.
- Task 15-20 hiç yazılmadı.
- **Mutasyon matrisinin kapsam sınırı:** `test_post_freeze_column_drift_refuses_decision`'ın
  kolon listesi ELLE yazılıdır ve çekirdeği besleyen TÜM kolonları kapsadığı mekanik olarak
  kanıtlanmamıştır. Kanıtlanan şey: yeni bir çekirdek alanı
  `test_snapshot_core_field_set_is_closed`'u kırar ve kapsam sorusunu zorunlu kılar.

# Risks

- **EN YÜKSEK (işletim) — kimlik doğrulamasız CRM webhook'ları onarılmadı, yalnız KAPATILDI.**
- **Üretim hattı hâlâ koşamaz:** denetçi web probu yok.
- **Atıf ADAYA bağlı DEĞİL** — sentezin `D1#<no>` atfı, o kararın yetkilendirdiği ADAYA değil
  ALAN düzeyine bağlı. Sözleşme revizyonu ister; evi açık
  (`docs/active/denetci-atif-aday-kimligi/`), sert son tarih Task 19.
- **`BulguIzi`'nin dördüncü alanı arayüz ekinde sahipsiz** (bu oturumun ürünü) — Open Problems'da,
  evi arayüz eki revizyonu.
- **Sözleşme penceresi Task 19'da KAPANIYOR.** Bekleyen sözleşme işi: atıf-aday kimliği +
  `BulguIzi` alan sahipliği + K-126 resmîlik ayağı + K-03 kategori ayağı.
- **Paket satırı kayma penceresi FAIL-CLOSED, KAPALI DEĞİL.** Onay yolu paketin sektörünü ve
  taslak durumunu kilitli okur; pencere kapatılamaz çünkü satır ancak okunarak öğrenilir. Kalıcı
  çözüm `sector-package-sector-id-immutability` (tetikli, ev kayıtlı); tetiği bu işle kurulmadı.
- **Migration `036` yerinde düzenlendi** — kabul edilmiş risk.
- **Katı Bölüm C biçimi yanlış-pozitif üretebilir ve ÖLÇÜLMEDİ** (ilk gerçek ölçüm Task 19).
- **KABUL EDİLMİŞ RİSK (M3) — commit geçmişi tek-commit TDD modeline uymuyor.**
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`).
- **EVSİZ PARK — atomiklik sınıfı depo GENELİ** (değişmedi).

# Notes For Claude/Codex

**Süreç ağırlığı — Eray'ın talimatları, BAĞLAYICI:**
1. **Hakem bulgularından YALNIZ critical/high düzeltilir**; orta/düşük RAPORLANIR ve devam edilir.
   **İSTİSNANIN İSTİSNASI ÖLÇÜLDÜ:** gerileme kontrolörün KENDİ ürünüyse ve iş üç satırsa
   devredilmez (bu oturumda F3 böyle kapatıldı). Kural büyük/riskli işleri sınırlar.
2. Mutasyon kanıtı yalnız **YENİ** kapıya istenir; kanıtlanmış kapı tekrar ölçülmez.
3. İnceleme turu üretim/test diye **BÖLÜNMEZ** — tek tur.
4. Düzeltme brief'leri **KISA**.
5. **Aynı eksen üst üste turlarda varyant üretiyorsa yamamayı bırak**, çerçeve teşhisiyle
   kullanıcıya git. **Bu oturumda uygulandı:** F2 üç turda üç varyant verdi; üçüncüde durup
   Eray'a gidildi ("ev desenini uygula, bir tur daha" kararı geldi ve tur kapandı).

**Her görev dispatch'inde ZORUNLU:**
1. Arayüz eki **bağlayıcıdır**; ilgili hükümler brief'e **harfiyen kopyalanır**. Çelişkide ÖLÇ.
   **Ekin kendisi bu oturumda GÜNCELLENMEDİ** ve bir kalem borç bıraktı (Open Problems).
2. **Ek, sır tarayıcısı tarafından tarama kökünden DIŞLANIYOR.** Ayrıca
   `tests/test_auditor_orchestration.py` · `tests/test_plan2_interface_contract.py` ·
   `sector_pipeline/runs.py` de dışlanıyor. **Dördü de HEAD git nesnesinden OKUNABİLİYOR** —
   dört turda dördü de bunu beyan etti. Hakeme gidecekse dışlanma coverage'da BEYAN EDİLİR.
3. Test komutu sanal ortam aktifleştirilerek koşar (`source .venv/bin/activate`).
4. **Taban 4002** (2026-09-10 kapanışından itibaren).
5. `Exec-Kind` **sınıflandırıcıya** göre seçilir. `Exec-*` bloğu mesajın SON PARAGRAFI.
6. **Commit başlığı ≤72 karakter** — `git log -1 --format=%s | wc -c` ile SAY.
   **Bu oturumda bir kez İHLAL EDİLDİ** (75 karakter) ve push öncesi `--amend` ile düzeltildi.
7. `Exec-Task` id'sini yazmadan ÖNCE defterde ARA — **pencere içinde**.
8. Her commit'ten SONRA defter kapısı koşulur (`ec_ledger_view … --post-window`, rc=0).
9. Uygulayıcı kendi alt-ajanını çağırmaz. **`docs/active/` altına yazmaz.**
10. **İSKELET ÖNCE — her testin kendi kırmızısı ayrı ölçülür.** Kendi kırmızısı OLMAYAN test
    dürüstçe öyle raporlanır. **Task 14'te DÖRT test böyleydi:** iki yapısal imza testi,
    K-98 tetikleyicisinin pozitif kontrolü ve `..._exposes_no_evidence_constructor` (hakem
    dördüncüyü yakaladı; ilk beyan ÜÇ diyordu).
11. **Kapanış üretilmiş matrisle** kanıtlanır, **boş-küme kontrol kolu** eklenir.
12. **Gönderilen düzyazıya sayı yazma** — ya üreten komutu yanına koy, ya "doğrulanmadı" etiketle.
13. **Hakem/kontrolör önerisi ADAYDIR** — dosyayı açmadan tekrarlanmaz.
14. **Kontrolörün tam test kümesi, veritabanına dokunan bir alt-ajanla ASLA üst üste binmez.**
15. Canlıya hiçbir n8n dosyası körlemesine yüklenmez.

**Task 15'in dispatch'ine ZORUNLU kalemler:**
- **Kanıtın TEK kurulum yeri `writeback.activate_from_snapshot`'ın içidir** (R8). `approval`
  modülü `ActivationGateEvidence` KURMAZ, import ETMEZ — yapısal test bunu pinliyor.
- **K-94 taban durumu için DOĞRUDAN test de gerekir:** "ikisi birden ya da hiçbiri yapım
  hatasıdır" ayağı, aktivasyon-yolu testleriyle İKAME EDİLMEZ (bu oturumun F5 düzeltmesi).
- **Onay anlık görüntüsünün üretim yazıcısı Task 14'te İNDİ** — Task 15 onu tüketir, yeniden
  kurmaz. Görüntü `paket_id`/`sektor_id` taşır ve karar `snapshot_sha`'ya bağlıdır.
- **Kilit sırası koşu → paket.** Aktivasyon yolu da koşu kilidiyle başlamalı; ters sıra onay
  yoluyla deadlock üretir (hakem turu 4 bu sırayı doğruladı).
- Task 8 üç yüzeyi Task 15'e bağlı bıraktı: jeton tüketimi koşmuyor · aktivasyon yükü yediye
  değil altıya varıyor. Bağlayıcı: `expected_no_active` eklendiği gün
  `test_evidence_payload_key_set_is_closed` KIRMIZI olur ve elle güncellenir.
- **Yol sıra numaraları KONUMSAL** — karşılaştıran her tüketici kimliğe anahtarlar, yola asla.

**Codex çağrısı kurarken — çağrıdan ÖNCE bas:**
1. `COMPANION` **ve** `PROMPT` **çağıran kabukta** kurulu mu (kabuk durumu taşınmaz).
2. `REQUIRED_CURRENT_FILES` SATIR SATIR mı — ve **dışlanan dosya var mı**.
3. Taban SHA 40 karakter mi. `CODEX_LOG` yazılabilir mi.
4. **Turun koştuğunu STDERR'den ölç:** `grep -c '^\[codex\] Running command'` **çağrının stderr
   çıktısında** — `$CODEX_LOG`'da DEĞİL.
5. **Uzun turları arka planda koştur** — ön planda kabuk 10 dakikada keser. `CSS_CALL_TIMEOUT`
   1200s dört turda da YETTİ (ölçülen süre ~8-12 dk).
6. **Kota sınırı gerçek bir dal ve BU OTURUMDA YAŞANDI.** Belirtisi: `rc=1` + stderr'de
   `You've hit your usage limit` + **kesik çıktı**. Kesik çıktı `approve` YAZABİLİR: bu oturumda
   yazdı ve SAYILMADI (9 komut, metin GELECEK zamanlı — karar değil giriş anlatısı).
   **Üç şeyi birden kontrol et: `rc` · koşum sayısı · son cümlenin karar mı anlatı mı olduğu.**
7. **Mutasyon probunun kendi deseni bayatlar.** Kod değişince `DESEN-YOK` gelir; bu PROB hatasıdır,
   `SAHTE-YEŞİL` ise GERÇEK boşluktur. İkisini karıştırmak yanlış rapor üretir (bu oturumda iki
   kez `DESEN-YOK` alındı ve kapılar sağlamdı).

**Sır tarayıcısı yanlış alarmı (her oturumda yeniden onay ister).** Substrat şunları dışlıyor:
`tests/test_auditor_orchestration.py` · arayüz eki · `tests/test_plan2_interface_contract.py` ·
`sector_pipeline/runs.py` · `docs/tools/codex-scan-substrate-harness.sh`. Hepsi yanlış alarm.

**EVİ OLAN, TAŞINAN KALEMLER — rolling yeniden yazımda DÜŞÜRÜLMESİN:**
- **`markdown-it-py` bir ÜRETİM bağımlılığıdır** (pinli `4.2.0`), canlıya dağıtılmadı.
  **Ev: Task 18, Step 3.**
- **Yol sıra numaraları KONUMSAL.** **Ev: Task 15.**
- **K-126 tek-kaynak istisnası KAPALI** — resmîlik ölçütü tipli taşınmadığı için motor onu
  açamıyor. **Ev: arayüz eki revizyonu + denetçi sözleşmesi.**
- **K-03'ün kategori ayağı UYGULANMADI.** **Ev: arayüz eki revizyonu.**
- **`BulguIzi` dördüncü alanının sahipliği.** **Ev: arayüz eki revizyonu** (bu oturumun ürünü).
- **Task 10'un TEST dosyaları bağımsız hakem GÖRMEDİ.** **Ev: Adım 11 final inceleme.**
- **Denetçi web probunun üretim sahibi Task 16'dır.**
- **Atıf ADAYA bağlanmalı.** **Ev: `docs/active/denetci-atif-aday-kimligi/` · son tarih Task 19.**
- **`sector_packages.sector_id` değişmezliği.** **Ev: `sector-package-sector-id-immutability`
  (CURRENT.md, tetikli).** Tetik koşulu "Plan 2 bu kolona YAZICI eklerse" — Task 14 eklemedi;
  **Task 15 aktivasyon yolunu yazarken bu koşul YENİDEN sınanmalı.**

**EVSİZ KALEM YOK.**

- **Eray'a teknik cümle onaylatma** — karar sorularını sade dille, proje-lokal kod referansı
  OLMADAN sor. Bu oturumda iki karar sorusu bu biçimde soruldu ve ikisi de yanıtlandı.
- **TEHDİT MODELİNİ ÖNDEN SÖYLE.** Girdi araştırma çıktısıdır — ÖZENSİZ olabilir, SALDIRGAN
  değil. Dört turda da prompt'a konuldu ve bulguların hepsi doğru katmandan geldi.
- **Bu dosya ROLLING'dir** — her oturumda BAŞTAN yazılır; karar izi `TASK.md` Decisions Log'una gider.
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz (bu yazım hariç).
