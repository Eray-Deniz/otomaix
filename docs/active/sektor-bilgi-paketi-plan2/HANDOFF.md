---
task: sektor-bilgi-paketi-plan2
written: 2026-09-09
---

# Resume From

**Sıradaki iş: Task 11** (sentez koşumu + çıktı doğrulayıcı — pakete YAZMAZ).
Task 10 indi ve checkpoint 7 kapandı.

**Komut:** `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam**.

**KAYIT TASK.md + bu dosya + git defteridir. BAŞKA DEFTER YOK.**

**Yürütme durumu:** kip alt-ajanlı · başlangıç çapası `a806e29` · defter penceresi `a806e29` ·
**`cp_count: 4`** · **`last_checkpoint_ref: 3af4331`** — bu oturumda §8.6 mutasyon protokolüyle
İLERLETİLDİ. Yani Task 11'in checkpoint'i artık Task 1-10'u yeniden kapsamayacak; önceki
oturumlarda ilerletilmediği için her tur giderek büyüyen bir aralığı tekrar tarıyordu.

**Dal:** `feat/sektor-bilgi-paketi-plan2`, merge EDİLMEDİ, **push EDİLMEDİ**. Son commit
`git log -1` ile, uzağa fark `git rev-list --left-right --count origin/<dal>...HEAD` ile ÖLÇÜLÜR.

**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: son commit `7964ed6`.
Bu oturumda dokunulmadı.

## Bu oturum ne yaptı — tek cümle

Task 10 (iki kör denetçi orkestrasyonu) yazıldı, beş hakem turu ve beş düzeltme turuyla on bulgu
kapatıldı, iki bulgu gerekçeli olarak kabul edilmiş riske alındı; test tabanı 3458 → 3595.

# Verification

**Bu oturumda koşulan komutlar ve TAZE çıktıları (hepsi kontrolörün kendi koşumları):**

- `python -m pytest tests/ -q` → **3595 passed in 294.20s**, exit 0 (SON, `3af4331`, temiz ağaç).
  Ara koşumlar: 3502 (`df92c0b`) · 3529 (`29fd099`) · 3559 (`47cb0da`) · 3590 (`1588f89`) ·
  3593 (`4c868c6`).
- `ec_ledger_view a806e29… /root/otomaix - --post-window` → **rc=0**, her commit'ten sonra.
- `ec_classify_diff` → `0503bd0` RISKY · `df92c0b` RISKY → `ec_should_checkpoint` → `RUN_RISK`.
- Beş Codex turu, hepsi `run_codex_scan` ile, taban `f1f897c7fdef969dd131e44209d1f921b9ec7aec`;
  ham çıktılar `$CODEX_LOG`'da byte-exact.
- Yol kapısının `..` ve symlink'li ata kaçağı **kontrolörün kendi probuyla** ölçüldü
  (gerçek yüklem zinciriyle: `GEÇTİ`/`GEÇTİ`/`GEÇTİ`), sonra kapatıldı.

**Denenmemiş / doğrulanmamış — dürüst liste:**

- **`3af4331` bağımsız hakem GÖRMEDİ.** Round 5'in kısmi kapanışı; altıncı tur bilinçle
  AÇILMADI (sınıf kapanmıyor, bkz. TASK.md Decisions Log). Kapsamı Adım 11 finaline düşer.
- **Uçtan uca CLI koşumu YAPILMADI.** Bayrakların kurulu sürümde var olduğu ölçüldü; "bu argv
  gerçekten denetçi raporu üretir" doğrulanmadı (ücretli model çağrısı gerektirir).
- **Denetçi-2'nin web erişimi yok** — `codex exec`'te web arama bayrağı yok; `-c` ile açan
  yapılandırma anahtarı ÖLÇÜLMEDİ, ölçülmeden yazılmadı.
- **Muafiyet kapısı turdan erişilemez** — prob olmadığı için yalnız fonksiyon doğrudan
  çağrılarak ölçüldü.
- **Kardeş-ağaç karşılaştırması ve göreli-kök hücresi mutasyonla kırmızıya DÖNMEDİ** — kapsam
  olarak ilan edildi, kanıtlanmadı.
- **Kiralamanın atomikliği yerel dosya sistemi `mkdir`'ine dayanır** — NFS/ağ dosya sistemi
  denenmedi. İki gerçek işletim sistemi süreci de denenmedi (eşzamanlılık hücresi ikinci
  iş parçacığı kullanıyor).
- **Raporun kendi gövdesindeki araç kimliği** tur seviyesinde anonimleştirilmiyor — K-137
  pakete GİDEN baytı kapsıyor, GERİ GELEN raporu değil. Evi yok, uydurulmadı.
- **`ruff` bu ortamda kurulu değil** — lint hiç koşmadı.
- **CRM webhook onarımı YAPILMADI** (değişmedi). **`telegramApi` credential'ının canlı token
  taşıdığı DOĞRULANMADI** (değişmedi). Canlıya migration dağıtılmadı; pilot koşulmadı.
- Task 11-20 hiç yazılmadı.

# Risks

- **EN YÜKSEK (işletim) — kimlik doğrulamasız CRM webhook'ları onarılmadı, yalnız KAPATILDI.**
- **Migration `036` yerinde düzenlendi** — kabul edilmiş risk; merge sonrası her değişiklik
  yeni numaralı migration ister.
- **Katı Bölüm C biçimi yanlış-pozitif üretebilir ve bu ÖLÇÜLMEDİ** (ilk gerçek ölçüm Task 19 Step 5).
- **KABUL EDİLMİŞ RİSK (M3) — commit geçmişi tek-commit TDD modeline uymuyor.**
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`).
- **EVSİZ PARK — atomiklik sınıfı depo GENELİ** (değişmedi).

# Notes For Claude/Codex

**Süreç ağırlığı — Eray'ın 2026-09-09 talebi, BAĞLAYICI:**
1. Mutasyon kanıtı yalnız **YENİ** kapıya istenir; kanıtlanmış kapı tekrar ölçülmez.
2. İnceleme turu üretim/test diye **BÖLÜNMEZ** — tek tur. (Eski rule 27 kalktı.)
3. Düzeltme brief'leri **KISA**. Ölçüldü: uzun brief'li turlar 16-24 dk, kısa brief'li tur 7,4 dk.
4. Severity kuralı DEĞİŞMEDİ: `critical`/`high` kapatılır, `medium`/`low` `accepted_risk` alır.
   **Tur-yönetimi kuralları (sistemik-sınıf, tavan, oscillation) C/H'yi kullanıcıya taşımanın
   bahanesi DEĞİLDİR** — bu oturumda bir kez öyle kullanıldı ve Eray düzeltti.

**Her görev dispatch'inde ZORUNLU:**
1. Arayüz eki **bağlayıcıdır**; ilgili hükümler brief'e **harfiyen kopyalanır**.
   **Ek şu an kodun ARKASINDA** — Task 10 `PacketRef`'e alan, `run_audit_round`'a parametre
   ekledi ve eke dokunmadı. Çelişkide ÖLÇ, ezberden uygulama.
2. Test komutu sanal ortam aktifleştirilerek koşar (`source .venv/bin/activate`).
3. **Taban 3595** (2026-09-09'dan itibaren).
4. `Exec-Kind` **sınıflandırıcıya** göre seçilir (yalnız `tests/` → `red-only`, yalnız üretim →
   `green-only`, ikisi → `code`, çalıştırılabilir path yok → `docs-only`). `.sql` çalıştırılabilir
   sınıfa GİRMEZ. `Exec-*` bloğu mesajın SON PARAGRAFI, co-author trailer'ları aynı paragrafta.
5. **Commit başlığı ≤72 karakter** — `git log -1 --format=%s | wc -c` ile SAY.
6. `Exec-Task` id'sini yazmadan ÖNCE defterde ARA.
7. Her commit'ten SONRA defter kapısı koşulur (`ec_ledger_view … --post-window`, rc=0).
8. Uygulayıcı kendi alt-ajanını çağırmaz. **`docs/active/` altına yazmaz.**
9. **İSKELET ÖNCE — her testin kendi kırmızısı ayrı ölçülür.** Modül yokken alınan tek
   `ImportError` kırmızı SAYILMAZ.
10. **Kapanış üretilmiş matrisle** kanıtlanır, **boş-küme kontrol kolu** eklenir. Yeni eksen
    eklerken kap çarpımını değil AYIRT EDEN EKSENİ büyüt.
11. **Gönderilen düzyazıya sayı yazma** — ya üreten komutu yanına koy, ya "doğrulanmadı" etiketle.
12. **Hakem/kontrolör önerisi ADAYDIR** — dosyayı açmadan tekrarlanmaz. Bu görevde ölçümde
    yanlış çıkan öneri sayısı **dokuz**; kontrolörün KENDİ probu **on iki** kez yanılttı
    (bu oturumda bir kez: yol kapısını kodun kullanmadığı bir yüklemle ölçtüm).
13. **Kontrolörün tam test kümesi, veritabanına dokunan bir alt-ajanla ASLA üst üste binmez.**
14. Canlıya hiçbir n8n dosyası körlemesine yüklenmez.

**EVİ OLAN, TAŞINAN KALEMLER — rolling yeniden yazımda DÜŞÜRÜLMESİN:**
- **`markdown-it-py` bir ÜRETİM bağımlılığıdır** (pinli `4.2.0`), canlıya dağıtılmadı.
  **Ev: Task 18, Step 3.**
- **Task 8 üç yüzeyi Task 15'e bağlı bıraktı** — jeton tüketimi koşmuyor · aktivasyon yükü
  yediye değil altıya varıyor · onay anlık görüntüsünün üretim yazıcısı yok (o Task 14).
  Bağlayıcı: `expected_no_active` eklendiği gün `test_evidence_payload_key_set_is_closed`
  KIRMIZI olur ve elle güncellenir. **Ev: Task 14 + Task 15.**
- **Yol sıra numaraları KONUMSAL** — karşılaştıran her tüketici kimliğe anahtarlar, yola asla.
  **Ev: Task 12 ve Task 13 dispatch'leri.**
- **Task 10'un TEST dosyaları bağımsız hakem GÖRMEDİ** (2026-09-09'da doğdu). Bugünkü beş tur
  üretim/test diye bölünmüştü ve test tarafı hiç koşulmadı; `test_auditor_orchestration.py`
  (~1000 satır) hiç incelenmedi. **Ev: Adım 11 final inceleme** — tabanı `a806e29` olduğu için
  bu dosyalar oraya kendiliğinden girer. Uydurma ev değil, mevcut zorunlu kapı.

**Task 11'in dispatch'ine ZORUNLU kalemler:**
- **Denetçi web erişim probunu SAĞLA.** K-14 kapısı probsuz her turu bloke ediyor (doğru
  davranış). Task 11 `run_audit_round`'a gerçek prob geçirmeli, yoksa hat çalışmaz.
- **Kilit/bütünlük korumasının çağıran tarafı.** Task 10 paket başına kiralama ve koşum anı
  bayt bütünlüğü kurdu; TOCTOU penceresi daraltıldı ama kapanmadı (kabul edilmiş risk).
- **Task 11 planda "Arayüz eki bağlar" satırını TAŞIMIYOR** — o kontrol ELLE yapılır.
- Task 11 aynı `Runner` protokolünü kullanıyor (`sentez` aracı `ToolSpec`'te tanımlı).

**Codex çağrısı kurarken — çağrıdan ÖNCE bas:**
1. `PROMPT` yüklendi mi (`PROMPT=$(cat -- "$CODEX_PROMPT_FILE")`) — dosyayı yazmak YETMEZ.
2. `REQUIRED_CURRENT_FILES` SATIR SATIR mı.
3. Taban SHA 40 karakter mi.
4. `CODEX_LOG` yazılabilir mi.
5. Turun gerçekten koştuğunu ÖLÇ: `grep -c '^\[codex\] Running command'`; ~1 ise onay sahtedir.
6. **Uzun turları arka planda koştur** — ön planda kabuk 10 dakikada keser.

**Sır tarayıcısı yanlış alarmı (her oturumda yeniden onay ister).** Substrat şunları dışlıyor:
`tests/test_auditor_orchestration.py` (satır 438/920'de `api_key={sir}` — maskeleme TESTİNİN
kendi malzemesi), arayüz eki (`provenance_token=token` — değişken adı),
`tests/test_plan2_interface_contract.py` (`provenance_token=_KOKEN_JETONU` — sabit adı).
Üçü de yanlış alarm, gerçek kimlik bilgisi YOK. Test dosyalarını inceletmek gerekirse diff'i
prompt'a gömmek gerekir ve bunun kabulü Eray'a SORULUR.

- **Eray'a teknik cümle onaylatma** — karar sorularını sade dille sor, proje-lokal kod referansı
  (fonksiyon/alan adı, dosya yolu) OLMADAN.
- **TEHDİT MODELİNİ ÖNDEN SÖYLE.** Girdi araştırma çıktısıdır — ÖZENSİZ olabilir, SALDIRGAN değil.
- **Bu dosya ROLLING'dir** — her oturumda BAŞTAN yazılır; karar izi `TASK.md` Decisions Log'una gider.
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz.
