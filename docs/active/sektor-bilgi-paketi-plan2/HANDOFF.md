---
task: sektor-bilgi-paketi-plan2
written: 2026-08-31
---

> ⚠️ YÜRÜTME AÇIK — bu anlatı **Task 3 kapandıktan sonra, Task 4'ten önce** yazıldı. Güncel
> durum TASK.md + yürütme defteri + git defterinden okunur; çelişkide onlar esastır.

# Resume From

**Task 3 KAPANDI. Açık döngü YOK. Sıradaki iş Task 4** (sözleşme v2 — denetçi
yeniden-doğrulama envanteri + sentez kimlik taşıması).

Geçen oturumun tek açık döngüsü — düzeltme turu 2'nin yeniden incelemesi — bu oturumda
koşuldu, iki Important buldu, düzeltme turu 3 ile kapandı (`ad95846`).

Komut: `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam** seçilir.

**ÖNCE OKU — kanonik ilerleme burada, bu dosyada DEĞİL:**
`.superpowers/sdd/2026-08-27-sektor-bilgi-paketi-plan2/progress.md`
Her görevin commit aralığı, her hakem bulgusu, her kontrolör kararı ve gerekçesi orada.
Sonundaki **SHA eşlem tablosu** önemlidir: defterin eski kayıtları eski commit numaralarını
anıyor, çünkü onları silmek o commit'lerin var olduğu gerçeğini silerdi.
Bağlam kaybolursa **defter + `git log`** esastır, anlatı değil.

**Yürütme durumu (TASK.md "Execution State"):** kip alt-ajanlı · başlangıç çapası `a806e29` ·
defter penceresi `a806e29` · `cp_count: 1` · `last_checkpoint_ref: 72f5744`.

**Dal:** `feat/sektor-bilgi-paketi-plan2`. **Push EDİLMEDİ** — uzak dal hâlâ `a806e29`'da
(kaç commit önde olduğu `git log origin/feat/...^..HEAD` ile okunur; buraya yazılmaz, drift eder). **Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`:
`master`, HEAD `d901eb4`, temiz, uzak deposu yok.

**Yedek etiket `backup/pre-footer-fix-20260830`** commit etiketi yeniden yazımının geri dönüş
yoludur. Silinme koşulu TASK.md'de yazılı (dal merge edilince VEYA final inceleme temiz geçince).

**Her görev dispatch'inde ZORUNLU olarak taşınacaklar:**
1. Arayüz eki **bağlayıcıdır**. Uygulayıcı brief'e, ekin ilgili hükümleri **harfiyen
   kopyalanmış** olarak gider — plan metni tek başına yetmez, "eki oku" demek de yetmez.
2. Test komutu **sanal ortam aktifleştirilerek** koşar (aşağıda Verification).
3. **Taban 745**; bu sayı düşmeyecek.
4. **`Exec-Kind` sınıflandırıcıya karşı seçilir, uzantıya karşı DEĞİL.** Beyaz liste altı
   değerli: `code` · `red-only` · `green-only` · `docs-only` · `migration` · `merge`.
   `shared/contracts/*.json` çalıştırılabilir sayılır.
5. **`Exec-*` bloğu mesajın SON PARAGRAFI olmalı**, ve `Co-Authored-By` / `Claude-Session`
   satırları **aynı paragrafın içinde** durmalı — araya boş satır girerse defter kapısı
   `rc=4` verir. Bu oturumda bir kez oldu, amend ile düzeldi (ayrıntı defterde).
6. **Her commit'ten SONRA defter kapısı koşulur** — finalde değil. İki footer dersinin ikisi
   de bu kapıdan çıktı; geç fark edilen biri altı commit'lik yeniden yazıma mal olmuştu.
7. Test önce yazılır, **kırmızı düştüğü gözle görülür**, kırmızı çıktı rapora yazılır.
8. Uygulayıcı **kendi alt-ajanını çağırmaz**; review kontrolörden gelir.
9. **Codex çağrılarına tam 40 karakterlik SHA verilir.** Kısa SHA substrat kurulumunda `rc=2`
   üretir — Codex hiç çağrılmaz, tur boşa gider.

**Devir pointer'ları — hangi görev neyi devralıyor:** TASK.md'nin "Task 3'ün doğurduğu evler"
bölümü. Task 6 · Task 9 · Task 11 · Task 12 · Task 13 · Task 15 · Task 18 dispatch'lerinde
ilgili maddeler taşınır. **Task 4 ayrıca Task 2'den üç sözleşme kalemi devralır.**
**Task 6 bu oturumda bir kalem daha devraldı:** `033_down.sql` yok (aşağıda).

# Verification

**Koşulan komutlar ve TAZE çıktıları (2026-08-31, hepsi kontrolörün kendi koşumları —
hiçbiri uygulayıcının ya da hakemin sözüne dayanmıyor):**
- `cd apps/social/backend && source .venv/bin/activate && python -m pytest tests/ -q`
  → **745 passed in 108.50s**. Oturum seyri: 744 (giriş) → 745 (yeni regresyon testi).
- `ec_ledger_view a806e29… /root/otomaix - --post-window` → **rc=0**; T3-fix3 satırı
  `code` kind ile hem test hem impl yolu taşıyor.
- **Yeni testin AYIRT EDİCİLİĞİ ölçüldü, varlığı değil:** `411c767`'nin modülü `git show` ile
  takas edilip `test_insert_draft_logs_content_warnings_before_pair_gate` koşuldu →
  **1 failed** (`test_package_lifecycle.py:287`); dosya geri yüklendi ve `cmp` ile
  byte-aynı doğrulandı, `git status` temiz.
- **Üst-küme senaryosu ampirik koşuldu** (geçici test, sonra silindi): dokuz değere onuncu
  eklenmiş CHECK ile 033 yeniden uygulanınca **rc=3**, hata İKİ pinli beklentiden birden
  geldi (`033:114-119` ve `033:183-184`) ve şema kalıcı değişmedi.
- **Kolon yolu ampirik koşuldu:** `sector_packages`'a `created_by` eklenip 032 yeniden
  uygulanınca **rc=3**, düşen etiket `sector_packages kolon imzası` (`032:377`).
- **Atıf matrisi üretildi:** üç teslimat metnindeki (docstring + task-3-report +
  task-3-fix3-report) **47 atıf**, 0 aralık-dışı; bu turda yeni giren beş kritik atıf ayrıca
  içerik olarak kontrol edildi (satır gerçekten iddia edileni söylüyor mu).
- `ls shared/db/migrations/rollback/` → yalnız `032_down.sql`; `033_down.sql` YOK.

**Denenmemiş / doğrulanmamış senaryolar — dürüst liste:**
- **Düzeltme turu 3 bağımsız hakem GÖRMEDİ.** Kapanış kontrolör kararıdır; sınıf mekanik
  matrisle kapatıldı. Atıf aralığı + beş içerik kontrolü, her cümleyi anlam için yeniden
  okumakla AYNI ŞEY DEĞİLDİR.
- **Task 4–20 hiç yazılmadı.**
- **Sözleşme metinlerinin ÇALIŞMA ZAMANI tüketimi hiç ölçülmedi.** Sweep'in "var" yargıları
  metin varlığını ölçer, davranışı değil; ilk kuru koşumda (Task 11/19) görülür.
- `test_plan2_interface_contract.py`'nin `created_by` eklendiğinde FAIL ettiği **pytest
  üzerinden görülmedi** — oturum şemayı her koşumda yeniden kuruyor. Yerine testin kendi
  manifest çifti bozuk şemaya karşı koşuldu (`columns` yüzeyi eşit çıkmıyor). Bu sınır
  docstring'de ve raporda dürüst etiketiyle yazılı.
- `git` ikilisi olmayan ortamda ve git ortam değişkenleri ezildiğinde pin davranışı
  ölçülmedi — evi Task 18 Step 8b.
- Canlıya hiçbir şey dağıtılmadı, hiçbir migration uygulanmadı, pilot koşulmadı.
- **Dal push EDİLMEDİ.**

# Risks

- **Aynı sınıf üç tur üst üste tekrarladı:** düzeltme metninin KENDİ içinde ölçülmemiş atıf.
  Tur 1 kapattığı bulgunun sınıfından yeni bir Important açtı; tur 2 iki tane açtı. Bu, bu
  görevin en ısrarlı hata modu — **Task 4'ün düzeltme turlarında aynı şey beklenmeli.**
  Ucuz karşı önlem ölçüldü: atıf matrisini üretip koşmak (47 atıf, saniyeler).
- **Kontrolör de ölçmeden kabul edebiliyor** — geçen oturumda bir uygulayıcı iddiası ölçmeden
  karara yazıldı, yanlıştı. Bu oturumda tersi de görüldü: bir "yok" iddiasını dar bir grep'e
  dayanarak kurmak üzereydim, ikinci arama etiketin metinde DURDUĞUNU gösterdi. **Tek
  kontrolle "yok" deme.**
- **"Test yazılamaz" savunması bir kez ölçümle çürüdü.** "Şu an test yok" ile "test
  yazılamaz" aynı şey değil; TDD zaten yeni kırmızı yazmayı ister. Bir uygulayıcı bu ayrımı
  karıştırıp zorunlu kapıyı atladı.
- **KABUL EDİLMİŞ RİSK (arayüz eki, tur 3 sonrası):** "annotation çalışma zamanı zorlaması
  değildir" sınıfının kalıntısı ve kimlik karşılaştırmalarındaki hoşgörülü normalleştirme.
- **KABUL EDİLMİŞ RİSK (checkpoint 1):** `test_external_repo_gitignores_run_folder` git ortam
  değişkenleriyle sahte bir depoya yönlendirilebilir. Üretim pin yolu etkilenmiyor.
  Evi Task 18 Step 8b.
- **KABUL EDİLMİŞ RİSK:** dış deponun içinde dışarıyı gösteren sembolik bağ ele alınmıyor;
  kapatmak ekin R14 hükmünün yasakladığı beşinci kapıyı gerektirir. **"Ele alındı" DEĞİL.**
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`). Arayüz eki 8 çelişki
  + 12 boşluğu kapattı ama **Plan 1 alanındaki kart geçişi hâlâ taranmadı**.
- **Codex maliyeti:** bu oturumda **sıfır** Codex çağrısı yapıldı — iki tur da Claude
  alt-ajanıyla koşuldu (hakem + uygulayıcı). Checkpoint 2 henüz gelmedi.

# Notes For Claude/Codex

- **Hakem turlarını Claude koşar — SORMA.** Eray'ın kalıcı kuralı.
- **Kontrolör düzeltme YAPMAZ.** Tek istisna `docs/active/` — orası kontrolörün kendi yüzeyi.
- **Minor bulgular döngüye girmez** — ama aynı dosyaya dokunuyorlarsa turun içine alınırlar
  (maliyet sıfır tur), ve gerekçe deftere yazılır. Bu oturumda iki Minor böyle bindi.
- **Spec değil, spec-input kanoniktir.**
- **Uygulayıcı raporunu doğrulanmamış iddia say** — ama iyi uygulayıcı kendi kusurunu da
  bildirir: bu oturumdaki uygulayıcı, hakemin "ölçemedim" dediği kalemi ölçmeyi başardı,
  ölçemediği kırıntıyı dürüst etiketle bıraktı ve kapsam dışı iki şeyi görüp DOKUNMADAN
  bildirdi (biri gerçek bir eksikti: `033_down.sql`).
- **Yargı turu yerine mekanik kapanış ne zaman meşrudur:** turlar aynı eksenin dar
  varyantlarını bulmaya başladığında. O noktada kapanış elle seçilmiş örnekle değil
  ÜRETİLMİŞ matrisle kanıtlanır — ve bunun kontrolör kararı olduğu dürüstçe etiketlenir.
- Diskte bekleyen düzeltme YOK; her iki çalışma ağacı da temiz.
