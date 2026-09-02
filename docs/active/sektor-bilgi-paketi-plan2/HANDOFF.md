---
task: sektor-bilgi-paketi-plan2
written: 2026-09-02
---

> ⚠️ YÜRÜTME AÇIK — bu anlatı **Task 5'in dördüncü düzeltme turundan sonra, görev KAPANMADAN**
> yazıldı. Güncel durum TASK.md + yürütme defteri + git defterinden okunur; çelişkide onlar esastır.

# Resume From

**Task 5 KAPANMADI.** Kod indi, çalışıyor, test tabanı 921 → 950 çıktı — ama görev-başı hakem
zinciri dört tur sürdü ve hâlâ açık bulgu var. Üstelik bir zorunlu kapı hiç koşulmadı.

**Sonraki oturumun İLK işi, tartışmasız: Task 5 için Codex checkpoint turu.**

Ölçüldü (2026-09-02): Task 5'in on iki commit'inin **onu riskli sınıfta** — dokuz `RISKY`,
bir `UNKNOWN` (`389d5e0`) — ve kadans kararı `ec_should_checkpoint 1 2 9` → **`RUN_RISK`**.
Protokol gereği ilk riskli commit'te (`16a8ab1`) Codex karşıt-hakem turu koşmalıydı. Kontrolör
dört turluk SDD hakem zincirini koştu ve kadans kararını hiç çalıştırmadı.
**Bu ikisi birbirinin yerine geçmez** — SDD hakemi taze bir Claude alt-ajanı, checkpoint ise
Codex, yani bağımsız ikinci model. Task 5 dört tur aynı aileden inceleme gördü, bağımsız
modelden sıfır. Dürüst etiket: *kapı koşulmadı; feragat edilmedi, kararla atlanmadı — kaçırıldı.*

Koşum: `§8.2` ile taban `ec_state_base_ref` (bugün `a6e053f`), sonra `§8.4`
`run_codex_scan "base-review" adversarial-review --base <taban>`. Kapanışta `§8.6` mutasyon
protokolü `last_checkpoint_ref` + `cp_count`'u ilerletir — **ikisi aynı commit'te**.

**Sonra: Task 5'in son turu (tur 5/5).** Tavan beştir, dörtte kalındı. Bir tur daha varsa o
SON turdur; sonrasında açık kalan bulgular dispatch edilmez, **kontrolör karara bağlar**.
Açık bulgular aşağıda "Risks" altında tek tek yazılı.

Komut: `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam**.

**ÖNCE OKU — kanonik ilerleme burada, bu dosyada DEĞİL:**
`.superpowers/sdd/2026-08-27-sektor-bilgi-paketi-plan2/progress.md`
Task 5'in dört turu, her turun ölçümleri, verilen tüm `Ruling:` satırları ve kontrolörün kendi
hataları orada. **Bu dosya git'e girmiyor** — kaybolursa git defteri ve commit mesajları esastır.

**Yürütme durumu:** kip alt-ajanlı · başlangıç çapası `a806e29` · defter penceresi `a806e29` ·
**`cp_count: 2`** · **`last_checkpoint_ref: a6e053f`** (Task 5 boyunca ilerlemedi — checkpoint
koşmadığı için ilerlememesi doğru).

**Dal:** `feat/sektor-bilgi-paketi-plan2`, HEAD **`468be6a`**. **Push EDİLMEDİ.**
**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: `master`, HEAD
`6d5d90db9537b516413d31f091b4d475526bcb73`, temiz. Task 5 ona dokunmadı.

**Yedek etiket `backup/pre-footer-fix-20260830`** duruyor; silinme koşulu TASK.md'de.

**Her görev dispatch'inde ZORUNLU olarak taşınacaklar** (önceki oturumdan devam, sayılar taze):
1. Arayüz eki **bağlayıcıdır**; ilgili hükümler brief'e **harfiyen kopyalanır**.
2. Test komutu sanal ortam aktifleştirilerek koşar (aşağıda Verification).
3. **Taban 950**; bu sayı düşmeyecek. (921 → 936 → 939 → 943 → 947 → 950.)
4. `Exec-Kind` **sınıflandırıcıya** karşı seçilir. `.sql` çalıştırılabilir sınıfa GİRMEZ —
   SQL-only commit `migration` alır (kapısız kind), `code` alırsa impl kümesi boş kalır ve düşer.
5. `Exec-*` bloğu mesajın SON PARAGRAFI, `Co-Authored-By` / `Claude-Session` **aynı paragrafta**.
6. **Commit başlığı ≤72 karakter** — bu oturumda bir commit 88 karakterle indi ve amend gerekti.
7. Her commit'ten SONRA defter kapısı koşulur.
8. Uygulayıcı kendi alt-ajanını çağırmaz.
9. Codex çağrılarına tam 40 karakterlik SHA verilir.
10. Kapanış elle seçilmiş örnekle değil **üretilmiş matrisle** kanıtlanır — ve bu oturum bir
    adım daha öğretti: **matris de mutasyonla sınanır.** Üretilmiş olması yetmiyor.

**Devir pointer'ları — Task 5'in doğurduğu evler:**
- **Task 6:** `035_down.sql`'in `\set ON_ERROR_STOP on` ayarını çağıran psql oturumuna sızdırması
  (`032_down.sql`'den devralındı, davranışı sıkılaştırıyor). Task 6 sıradaki geri alma
  dosyalarını (`033_down.sql`, `034_down.sql`) yazan görev — konvansiyon orada benimsenir ya da
  kapsanır.
- **Task 18:** (a) `get_holidays` yıl başına 24 saat önbellekliyor, yazımda geçersizleştirme yok
  → dağıtım sonrası önyüz bir güne kadar `end_date`siz yanıt alabilir. (b) Migration'lar kendi
  transaction'ını mı sahiplensin sorusu — tek ulaşılabilir ret yolunda sarmalanmamış `up` yarım
  uygulanmış kalıyor. İkisi de dağıtım/geri alma sırası kararıdır; (b) Task 6'ya giden kalemle
  aynı aileden, tek kararda ele alınabilir.
- Önceki oturumdan devam: Task 9 · Task 11 · Task 12 · Task 13 · Task 15 · Task 18 pointer'ları
  TASK.md "Task 3'ün doğurduğu evler" bölümünde.

# Verification

**Koşulan komutlar ve TAZE çıktıları (2026-09-02, hepsi kontrolörün kendi koşumları):**
- `cd apps/social/backend && source .venv/bin/activate && python -m pytest tests/ -q`
  → **950 passed in 197.45s**. Seyir: 921 (giriş) → 936 (ana iniş) → 939 (tur 1) → 943 (tur 2)
  → 947 (tur 3) → 950 (tur 4). Hiç düşmedi; her tur ayrı ölçüldü.
- `ec_ledger_view a806e29… /root/otomaix - --post-window` → **rc=0**, her commit'ten sonra.
  Task 5'in on iki satırının hepsi etiketli.
- **Risk sınıflandırması:** on iki commit → 2 LOW, 9 RISKY, 1 UNKNOWN.
  `ec_should_checkpoint 1 2 9` → **RUN_RISK** (kapı borcu, yukarıda).
- **Commit başlığı uzunlukları:** on ikisi de ölçüldü; tek ihlal (`164fb09`, 88 karakter)
  amend'lendi → `fc1df7f`, 54 karakter.
- **Seed değerleri:** hakem dört yüzeyde bayt-aynı doğruladı — migration seed bloğu, geri alma
  silme bloğu, geri alma kalıntı denetimi, test sabitleri. Ayrıca üretici workflow.
- **Canlı takvim tablosu:** 22 satır, hepsi 2026; kategori kümesi `{national, religious,
  commercial}`; üç yeni tarihin **hiçbiri dolu değil** (anahtar çakışması yok).
- **İsim ayrımı:** `m035_seed_up` / `m035_seed_down`; her dosyada kardeşinin adı tam bir kez ve
  ikisi de yorum satırı — çalışan SQL'de sıfır çapraz referans.
- **Sızıntı taraması:** aynı Telegram bot token'ı **iki** workflow dosyasında (`grep` ile).

**Denenmemiş / doğrulanmamış senaryolar — dürüst liste:**
- **Task 5 hiçbir bağımsız MODEL görmedi.** Dört tur da taze Claude alt-ajanıydı; Codex sıfır.
- **Tur 4'ün düzeltmesi hakem gördü ama tur 5 yapılmadı** — açık bulgular kapanmadı.
- **Kanıt aracının kendisi hâlâ eksik:** hakemin uydurduğu iki mutasyon (doğrulama bloğundaki
  niteliksiz okumalar · beş daldan `CASCADE` kaldırma) suite tamamen yeşilken gerçek kusur geri
  getiriyor. Yani "sınıf kapandı" **kanıtlanmadı**.
- **İki migration dosyasında yanlış bir "ölçüldü" iddiası duruyor** (yabancı tablo dalı).
  Hakem aynı sunucuda çürüttü: FDW eklentileri mevcut, `pg_temp`'te yabancı tablo yaratılabiliyor.
  Doğru ölçüm "şu an FDW sunucu nesnesi yok"tu — kurulumun değil, veritabanının o anki içeriğinin
  özelliği. Sevk edilen SQL'in içinde duruyor, raporda değil.
- **Hücre sayısı iddiaları bayat:** Grid A 96 → 24'e indi, üç yerde hâlâ "96 hücre" yazıyor
  (ikisi sevk edilen SQL yorumu).
- Canlıya hiçbir şey dağıtılmadı, **035 hiçbir gerçek ortama uygulanmadı**, pilot koşulmadı.
- **Dal push EDİLMEDİ.**
- Task 6–20 hiç yazılmadı.

# Risks

- **AÇIK BULGU (tur 5'in konusu) — kanıt aracı hâlâ gösterildiğine ayarlı.** Talep ettiğim üç
  mutasyon artık kırmızı düşüyor ve dal varlığı + fiil doğruluğu falsifiye edilebilir durumda.
  Ama hakemin **kendi uydurduğu** iki mutasyon kaçıyor:
  (B) yalnız `DO $verify_035$` bloğundaki manifest okumalarını niteliksiz bırakmak → `26 passed`,
  ama canlıda güvenlik kapısı kalıcı tabloyu okuyup uydurma şikâyetle düşüyor; mevcut pin sadece
  **yazma** yolunu ölçüyor.
  (C) `'r'` dışındaki beş daldan `CASCADE` kaldırmak → `26 passed`, ama bileşik-tür squatter'ı
  fail-open şeklini birebir geri getiriyor; bağımlı-nesne ekseni tek hücre (`'r'`) hâlinde.
- **AÇIK BULGU — İlke 9 ihlali sevk edilen dosyada.** Yukarıda yazılı yabancı-tablo iddiası.
  Bu, bu projenin en çok kovaladığı sınıfın ta kendisi ve rapor katmanında değil SQL'de.
- **AÇIK BULGU (Minor) — iddia sapması:** hücre sayısı (3 yer) ve geri alma dosyasındaki tür
  listesi (yabancı tabloyu sayıyor, bölümlenmiş tablo ile bileşik türü saymıyor).
- **KABUL EDİLMİŞ RİSK (kontrolör kararı):** tek ulaşılabilir ret yolunda sarmalanmamış `up`
  yarım uygulanmış kalıyor. Üretim koşturucusu ölçülerek fail-closed. Evi Task 18.
  **"Ele alındı" DEĞİL.**
- **KABUL EDİLMİŞ RİSK:** `'f'` dalının kaldırılması, FDW'li bir ortamda önceden ele alınan bir
  türü rette bırakıyor. Yön fail-closed, ama gerekçesi çürütülen ölçüme dayanıyor — tur 5'te
  gerekçe ya düzeltilir ya dal geri gelir.
- **KABUL EDİLMİŞ RİSK:** `CASCADE` bizim rezerve ismimiz üzerine kurulmuş bağımlı nesneyi sessizce
  düşürüyor. Hakem ölçtü: PostgreSQL'in kendi temp temizliği aynı nesneyi zaten yok ediyor, yani
  koruma başka türlü hayatta kalacak bir şeyi yok etmiyor.
- **KONTROLÖRÜN ÜÇ YANLIŞ ÖNERİSİ — en taze ders.** Bu oturumda uygulayıcıya ilettiğim üç çözüm
  önerisinin üçü de ölçümde yanlış çıktı ve uygulayıcı üçünü de gerekçesiyle reddetti:
  (1) hakemin `DROP TABLE IF EXISTS pg_temp…` önerisi her oturumda gürültü basıp az önce
  sabitlenen anlamlı uyarıyı gömecekti; (2) `SET LOCAL` transaction dışında hiçbir şey yapmıyor,
  yani tam da onarılan çıplak yolda sabitlemeyi düşürecekti; (3) "ret hücreleri sıfır dışı çıkış
  kodu doğrulasın" talebim psql'i sabitlemek olurdu, migration'ı değil.
  **Ders: dispatch'e taşınan öneri test edilmemiş bir iddiadır — aday olarak etiketle, cevap
  olarak değil.**
- **Kontrolörün kanıt şartnamesi kusurluydu.** Sınıf kapanışı için matris dayattım ve matrisin
  girdilerini kendi elimle seçtim; seçtiğim her tür korumanın zaten tanıdığı türdü ve "iki isim
  farklı" özelliğini doğrulayan hücre hiç istemedim. Hollow proof benim şartnamemin ürünü.
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`); Plan 1 alanındaki kart
  geçişi hâlâ taranmadı.
- **Codex maliyeti:** bu oturumda **sıfır** Codex çağrısı yapıldı. Final için ≥3 tur rezerve
  kuralı yerinde; oturum tavanı 8.

# Notes For Claude/Codex

- **Hakem turlarını Claude koşar — SORMA.** Eray'ın kalıcı kuralı.
- **Kontrolör düzeltme YAPMAZ.** Bu oturumda iki istisna kullanıldı ve ikisi de gerekçesiyle
  deftere yazıldı: (a) 88 karakterlik commit başlığının amend'lenmesi — kod taşımıyor, hakem aynı
  diff'i görüyor; (b) rapordaki bayat SHA'nın düzeltilmesi — o bayatlığı amend'im yaratmıştı.
- **Hakemin severity'si bağlayıcı DEĞİL, ölçüm bağlayıcı.** Bu oturumda bir Minor Important'a
  yükseltildi (`client_min_messages`: hakem Minor demişti, kendi ölçümü sıradan bir üretim
  sertleştirmesinin düzeltmeyi tamamen sustureceğini gösteriyordu).
- **Kendi ürettiğin gerilemeyi park etme.** Medium-advisory izni ÖNCEDEN VAR OLAN borç içindir.
  Bu oturumda iki gerileme bu kuralla döngüye alındı (`ON COMMIT DROP` fail-open'ı ve
  niteliksiz manifest okumaları).
- **Uygulayıcı raporunu doğrulanmamış iddia say** — ama bu uygulayıcı iyiydi: kendi kusurunu
  bildirdi, benim üç yanlış önerimi ölçümle reddetti, bir kalemi "tahmin etmektense sen karara
  bağla" diye bana bıraktı, ve kaldırdığı bir dalın "yetenek kaybı gibi okunduğunu" kendisi
  söyledi. Aynı uygulayıcıyı sürdürmek (tur 4-5'te taze uygulayıcı kuralına rağmen) bu yüzden
  seçildi; gerekçe defterde.
- **Alt-ajan model alanını HİÇ GEÇME.** `model: opus` gibi çıplak takma ad hook tarafından
  reddediliyor (hangi sürüme çözüleceği harness'e ait, sessiz düşürme koruması). Alan
  geçilmezse config varsayılanı miras alınıyor.
- **Spec değil, spec-input kanoniktir.**
- Diskte bekleyen düzeltme YOK; çalışma ağacı temiz.
