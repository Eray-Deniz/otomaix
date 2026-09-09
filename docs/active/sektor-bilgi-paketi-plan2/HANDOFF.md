---
task: sektor-bilgi-paketi-plan2
written: 2026-09-09
---

# Resume From

**Sıradaki iş: Task 12** (politika motoru — zorunlu kontroller + K-112 takvim erişilemezliği).
Task 11 indi ve checkpoint 8 kapandı.

**Komut:** `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam**.

**KAYIT TASK.md + bu dosya + git defteridir. BAŞKA DEFTER YOK.**

**Yürütme durumu:** kip **`inline`** (Task 11'de Eray talebiyle değişti; Task 1-10 alt-ajanlıydı)
· başlangıç çapası `a806e29` · defter penceresi `a806e29` · **`cp_count: 5`** ·
**`last_checkpoint_ref: a44d9ec`** — §8.6 mutasyon protokolüyle bu oturumda ilerletildi.

**Dal:** `feat/sektor-bilgi-paketi-plan2`, merge EDİLMEDİ. Uzak dal VAR; ölçüldü (2026-09-09,
Task 11 öncesi): `git rev-list --left-right --count origin/<dal>...HEAD` → `0 11`. Task 11'in
commit'leri sonra indi, yani gönderilmemiş sayı ARTTI — taze ölçüm o komutla alınır.

**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: son commit `7964ed6`.
Bu oturumda dokunulmadı; pin kapısı sentez sözleşmesini okurken geçti.

## Bu oturum ne yaptı — tek cümle

Task 11 (sentez koşumu + çıktı doğrulayıcı) inline yazıldı; iki hakem turunda altı yüksek
bulgunun beşi kapatıldı, altıncısı sahiplik kalemi olarak Task 16'ya yeniden evlendirildi,
iki orta kabul edilmiş riske alındı; test tabanı 3595 → 3649.

# Verification

**Bu oturumda koşulan komutlar ve TAZE çıktıları (hepsi kontrolörün kendi koşumları):**

- `python -m pytest tests/ -q` → **3649 passed in 299.03s**, exit 0 (SON, `a44d9ec`, temiz ağaç).
  Ara koşumlar: 3633 (rename sonrası ara hâl) · 3635 (`0f39d0c`).
- `python -m pytest tests/test_synthesis.py -q` → 32 failed / 1 passed (iskelet, `0f4a20c`) →
  40 passed (`0f39d0c`) → **54 passed** (`a44d9ec`).
- `ec_ledger_view a806e29… /root/otomaix - --post-window` → **rc=0**, her commit'ten sonra.
- `ec_classify_diff` → `0f4a20c` RISKY · `0f39d0c` RISKY → `ec_should_checkpoint 1 4 9` →
  `RUN_RISK`.
- İki Codex turu, ikisi de `run_codex_scan` ile, taban `3af4331`; ham çıktılar `$CODEX_LOG`'da
  byte-exact. Turların gerçekten koştuğu `grep -c '^\[codex\] Running command'` ile ölçüldü
  (19 ve 12; ~1 olsaydı çağrı hiç kurulmamış olurdu).
- `Path('/tmp/dest') / '/tmp/kacak'` → `/tmp/kacak` — F1'in gerçekliği kontrolörün KENDİ
  probuyla ölçüldü, hakemin iddiası olduğu gibi kabul edilmedi.
- `grep -rn 'run_audit_round(' --include='*.py'` (test dışı) → yalnız tanım; `synthesis.run(`
  → üretim çağıranı YOK. F5'in yeniden evlendirilmesi bu ölçüme dayanır.

**Denenmemiş / doğrulanmamış — dürüst liste:**

- **Uçtan uca CLI koşumu YAPILMADI.** Sentez aracı hiç gerçekten çağrılmadı; tüm koşumlar sahte
  runner ile. "Bu argv gerçekten aday paket üretir" DOĞRULANMADI (ücretli model çağrısı gerekir).
- **Denetçi web erişim probu YOK** — üretim hattı hâlâ koşamaz (bkz. TASK.md Open Problems).
- **`kanit` alanının `#<no>` kolu hiç çözülmüyor.** Gerçek denetçi çıktısında bu biçimin ne
  sıklıkta geçtiği ÖLÇÜLMEDİ; yanlış-pozitif oranı bilinmiyor. İlk gerçek ölçüm Task 19'da.
- **Reddedilen çıkarmanın metin/özel-gün kolu ve sentez eşzamanlılığı** kabul edilmiş risk;
  ikisi de mutasyonla kırmızıya döndürülmedi çünkü fix yazılmadı.
- **`ruff` bu ortamda kurulu değil** — lint hiç koşmadı. Pyright de koşulmadı.
- **CRM webhook onarımı YAPILMADI** (değişmedi). Canlıya migration dağıtılmadı; pilot koşulmadı.
- Task 12-20 hiç yazılmadı.

# Risks

- **EN YÜKSEK (işletim) — kimlik doğrulamasız CRM webhook'ları onarılmadı, yalnız KAPATILDI.**
- **Üretim hattı hâlâ koşamaz:** denetçi web probu yok, K-14 kapısı her turu bloke ediyor.
- **Migration `036` yerinde düzenlendi** — kabul edilmiş risk; merge sonrası her değişiklik
  yeni numaralı migration ister.
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
   **Tur-yönetimi kuralları C/H'yi kullanıcıya taşımanın bahanesi DEĞİLDİR.**

**Her görev dispatch'inde ZORUNLU:**
1. Arayüz eki **bağlayıcıdır**; ilgili hükümler brief'e **harfiyen kopyalanır**.
   **Ek şu an kodun ARKASINDA** — Task 10 `PacketRef`/`run_audit_round`'a alan ekledi, Task 11
   `synthesis.run`'a `dest` ekledi ve `SynthesisResult`'ı tanımladı; eke DOKUNULMADI.
   Çelişkide ÖLÇ, ezberden uygulama.
2. Test komutu sanal ortam aktifleştirilerek koşar (`source .venv/bin/activate`).
3. **Taban 3649** (2026-09-09'dan itibaren).
4. `Exec-Kind` **sınıflandırıcıya** göre seçilir (yalnız `tests/` → `red-only`, yalnız üretim →
   `green-only`, ikisi → `code`, çalıştırılabilir path yok → `docs-only`). `.sql` çalıştırılabilir
   sınıfa GİRMEZ. `Exec-*` bloğu mesajın SON PARAGRAFI, co-author trailer'ları aynı paragrafta.
5. **Commit başlığı ≤72 karakter** — `git log -1 --format=%s | wc -c` ile SAY.
6. `Exec-Task` id'sini yazmadan ÖNCE defterde ARA.
7. Her commit'ten SONRA defter kapısı koşulur (`ec_ledger_view … --post-window`, rc=0).
8. Uygulayıcı kendi alt-ajanını çağırmaz. **`docs/active/` altına yazmaz.**
9. **İSKELET ÖNCE — her testin kendi kırmızısı ayrı ölçülür.**
10. **Kapanış üretilmiş matrisle** kanıtlanır, **boş-küme kontrol kolu** eklenir. Task 11'de bu
    kural kontrolörün KENDİ tarayıcısındaki deliği yakaladı — elle seçilmiş örnek yakalamazdı.
11. **Gönderilen düzyazıya sayı yazma** — ya üreten komutu yanına koy, ya "doğrulanmadı" etiketle.
12. **Hakem/kontrolör önerisi ADAYDIR** — dosyayı açmadan tekrarlanmaz. Task 11'de hakemin altı
    yüksek bulgusundan beşi ölçümle DOĞRULANDI, biri (F5) ölçümle REDDEDİLDİ ve yeniden
    evlendirildi. İkisini de ölçüm ayırdı, ezber değil.
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
  Task 11 bunu koda geçirdi (`_geri_koy` hash eşitliğine bakar, yola değil).
  **Ev: Task 12 ve Task 13 dispatch'leri.**
- **Task 10'un TEST dosyaları bağımsız hakem GÖRMEDİ.** **Ev: Adım 11 final inceleme** —
  tabanı `a806e29` olduğu için oraya kendiliğinden girer.
- **Denetçi web probunun üretim sahibi Task 16'dır** (bu oturumda yeniden evlendirildi).

**Task 12'nin dispatch'ine ZORUNLU kalemler:**
- `EngineInputs` **arayüz eki R5'te TAM ALAN LİSTESİYLE bağlıdır** — harfiyen kopyala.
  `sentez: SynthesisResult` alanı artık gerçek bir tipe işaret ediyor.
- **`SynthesisResult.aday_json` DONMUŞTUR.** Şemaya ya da JSON'a verilecekken
  `identity.cozulmus` ile çözülür; `dict()` YETMEZ (iç içe listeler demettir ve yazım kapısı
  `isinstance(..., list)` sorar).
- `denetci_envanterleri` tipi `ValidatedAuditPair`'dır; ham `AuditReport` demeti REDDEDİLİR.
- K-71: sentezin açık soruları aktivasyonu BLOKLAR (`acik_soru` bulgusu → `blocked`).

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
Üçü de yanlış alarm, gerçek kimlik bilgisi YOK.

- **Eray'a teknik cümle onaylatma** — karar sorularını sade dille sor, proje-lokal kod referansı
  OLMADAN.
- **TEHDİT MODELİNİ ÖNDEN SÖYLE.** Girdi araştırma çıktısıdır — ÖZENSİZ olabilir, SALDIRGAN
  değil. Task 11'de bu cümle hakem prompt'una konuldu ve bulguların hepsi doğru katmandan geldi.
- **Bu dosya ROLLING'dir** — her oturumda BAŞTAN yazılır; karar izi `TASK.md` Decisions Log'una gider.
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz.
