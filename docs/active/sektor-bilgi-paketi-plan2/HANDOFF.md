---
task: sektor-bilgi-paketi-plan2
written: 2026-08-31
---

> ⚠️ YÜRÜTME AÇIK — bu anlatı **checkpoint 2 kapandıktan sonra, Task 5'ten önce** yazıldı.
> Güncel durum TASK.md + yürütme defteri + git defterinden okunur; çelişkide onlar esastır.

# Resume From

**Task 4 KAPANDI. Checkpoint 2 KAPANDI (hakem `approve`). Açık döngü YOK.
Sıradaki iş Task 5** (migration 035 — takvim dönem desteği + üç takvim kalemi).

**AMA Task 5 doğrudan dispatch EDİLMEZ — önce Eray'a sorulur.** Beklenen kararlar:
takvim satırlarının **yılı · kategorisi · kanonik adı**, "okula dönüş" tarihleri. Bunlar
ürün kararıdır, kod okuma gerektirmez; İlke 8 gereği Eray-seviyesinde sorulur. Task 19 da
dört operatör kararı bekliyor (o görevе gelindiğinde).

Komut: `/execute-plan-claude-codex docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md`
→ resume dalı: TASK.md `active`, yürütme durumu dolu, **(a) devam** seçilir.

**ÖNCE OKU — kanonik ilerleme burada, bu dosyada DEĞİL:**
`.superpowers/sdd/2026-08-27-sektor-bilgi-paketi-plan2/progress.md`
Bağlam kaybolursa **defter + `git log`** esastır, anlatı değil.

**Yürütme durumu (TASK.md "Execution State"):** kip alt-ajanlı · başlangıç çapası `a806e29` ·
defter penceresi `a806e29` · **`cp_count: 2`** · **`last_checkpoint_ref: a6e053f`**
(checkpoint 2 kapanışında mutasyon protokolüyle ilerletildi).

**Dal:** `feat/sektor-bilgi-paketi-plan2`. **Push EDİLMEDİ** — uzak dal hâlâ `a806e29`'da.
**Dış sözleşme deposu** `/root/otomaix-sosyal-medya-arastirmasi`: `master`, HEAD
**`6d5d90db9537b516413d31f091b4d475526bcb73`**, temiz, uzak deposu yok.

**Yedek etiket `backup/pre-footer-fix-20260830`** commit etiketi yeniden yazımının geri dönüş
yoludur. Silinme koşulu TASK.md'de yazılı.

**Her görev dispatch'inde ZORUNLU olarak taşınacaklar:**
1. Arayüz eki **bağlayıcıdır**. Uygulayıcı brief'e ekin ilgili hükümleri **harfiyen
   kopyalanmış** gider — plan metni yetmez, "eki oku" demek de yetmez.
2. Test komutu **sanal ortam aktifleştirilerek** koşar (aşağıda Verification).
3. **Taban 921**; bu sayı düşmeyecek. (745 → 758 → 914 → 921.)
4. **`Exec-Kind` sınıflandırıcıya karşı seçilir, uzantıya karşı DEĞİL.** Altı değer:
   `code` · `red-only` · `green-only` · `docs-only` · `migration` · `merge`.
   `shared/contracts/*.json` çalıştırılabilir sayılır.
5. **`Exec-*` bloğu mesajın SON PARAGRAFI olmalı**, `Co-Authored-By` / `Claude-Session`
   **aynı paragrafın içinde** — araya boş satır girerse defter kapısı `rc=4` verir.
6. **Her commit'ten SONRA defter kapısı koşulur** — finalde değil.
7. Test önce yazılır, **kırmızı düştüğü gözle görülür**, kırmızı çıktı rapora yazılır.
8. Uygulayıcı **kendi alt-ajanını çağırmaz**; review kontrolörden gelir.
9. **Codex çağrılarına tam 40 karakterlik SHA verilir.** Kısa SHA `rc=2` üretir.
10. **Dış depo değişikliği hakeme prompt'a GÖMÜLEREK gider.** Codex sandbox'ı
    `/root/otomaix-sosyal-medya-arastirmasi`'ya erişemez; sözleşmeye dokunan her turda diff
    prompt'un sonuna veri olarak eklenir ve kapsam beyanında adı geçer. (Bu tur ölçüldü:
    26 KB, tek argüman sınırı 131 KB.)
11. **Kapanış elle seçilmiş örnekle DEĞİL, ÜRETİLMİŞ matrisle kanıtlanır.** Bu oturumda tam
    bu yüzden bir tur kaybedildi (aşağıda, Risks).

**Devir pointer'ları:** TASK.md'nin "Task 3'ün doğurduğu evler" bölümü —
Task 6 · Task 9 · Task 11 · Task 12 · Task 13 · Task 15 · Task 18 dispatch'lerinde taşınır.
**Task 9 ayrıca ekin M1 hükmünü devralır:** beş çıktı bölümü anahtarı pinlenmiş denetçi
sözleşmesinden **ÖLÇÜLEREK** doldurulur, uydurulmaz; iki kapı testi Task 9'un malıdır.
Ayrıca Task 9 ilk iş olarak pin doğrulamasını çağırır — pin v2 değilse görev DURUR.

# Verification

**Koşulan komutlar ve TAZE çıktıları (2026-08-31, hepsi kontrolörün kendi koşumları):**
- `cd apps/social/backend && source .venv/bin/activate && python -m pytest tests/ -q`
  → **921 passed in 108.91s**. Seyir: 745 (giriş) → 745 (Task 4) → 758 (düzeltme 1)
  → 914 (düzeltme 2) → 921 (düzeltme 3). Hiç düşmedi.
- `ec_ledger_view a806e29… /root/otomaix - --post-window` → **rc=0** (her commit'ten sonra).
- **Pin doğruluğu:** manifest üç dosyanın disk `sha256sum` çıktısıyla birebir; dış depo
  HEAD == pinlenen commit. Kapı kümesi DÖRT kaldı (R14).
- **Modül çıkarımının SADAKATİ ölçüldü:** kaynak modülden kaybolan 27 üst düzey adın **27'si**
  yaprakta bayt-aynı; kalan 35 adın hiçbiri değişmemiş (AST kaynak-parça karşılaştırması).
  Kaybolan 8 ad özel; hiçbiri eski modül üzerinden anılmıyor.
- **Hash kayması:** 19 eski-biçim girdi (büyük tamsayılar dâhil) → **0 kayma**. Pinlenen
  özetler yerinde (`7fe8362b…`, `397fc667…`).
- **İstisna tipi sözleşmesi:** üretilmiş ret matrisi (9 sınıf × 6 kapsayıcı = 60 hücre),
  hepsi `TypeError`. Basamak sınırı üstü de artık sözleşmeye uyuyor; **süreç sınırı
  YÜKSELTİLMEDİ** (kaynak taraması: `sys.set_int_max_str_digits` yalnız "neden çağırmıyoruz"
  açıklamasında geçiyor).
- **Yapısal kapının AYIRT EDİCİLİĞİ ÜRETİLMİŞ MATRİSLE ölçüldü:** 44 hücrelik import
  sözdizimi çarpımı; ayrıca kontrolörün bağımsız mutasyonları — kimlik modülünde 5 biçimin
  5'i, yaşam döngüsünde 4 biçimin hepsi yakalandı; mutasyonsuz kod hâlâ geçiyor. Gerçek
  dosyalar `cmp` ile bayt-aynı geri yüklendi, `git status` temiz.
- **Beş çıktı bölümü:** `grep -cE '^[0-9]\) ' hakem-denetci-gorevi.md` → **5**.
- **Kapalı bayrak kümesi:** 8 üye; `muhtemel-uydurma` içinde YOK.
- **Ölü SHA taraması:** squash edilen commit ve amend öncesi dış SHA hiçbir yerde anılmıyor.

**Denenmemiş / doğrulanmamış senaryolar — dürüst liste:**
- **Düzeltme turu 3 (`a6e053f`) bağımsız yargı GÖRMEDİ.** Ev uydurulmadı: final incelemenin
  tabanı `a806e29` olduğu için bu commit onun aralığına ZATEN giriyor. Bu kapsanma yolu bu
  oturumda bir kez ölçümle işledi (Task 3'ün düzeltme turu 3'ü checkpoint 2 tarafından
  kapsandı ve yeni kusur çıkmadı) — tahmin değil, görülmüş yol.
- **Sözleşme metninin bir denetçi oturumunda fiilen beş bölümlü ve tamlık kurallı çıktı
  ürettireceği doğrulanmadı** — ancak gerçek koşumla ölçülür (Task 11/19).
- **Task 8'in ileride yazılacak modülünün temiz import edeceği doğrulanmadı**; yalnız kanonik
  hash'in ekin bağladığı biçimi kabul ettiği ölçüldü. Modül henüz yok.
- **Farklı basamak-sınırı ayarına sahip ortamda koşulmadı.** Test eşiği koddan okuduğu için
  taşınabilir olması BEKLENİR; fiilen sınanmadı. Ölçümler yalnız Python 3.12.3'te.
- **Task 5–20 hiç yazılmadı.**
- `git` ikilisi olmayan ortamda ve git ortam değişkenleri ezildiğinde pin davranışı
  ölçülmedi — evi Task 18 Step 8b.
- Canlıya hiçbir şey dağıtılmadı, hiçbir migration uygulanmadı, pilot koşulmadı.
- **Dal push EDİLMEDİ.**

# Risks

- **KAPANMAMIŞ AYAK (dürüst etiket):** ekin bağımlılık hükmünün "kullanılan TEK ad
  `identity.canonical_sha`" ayağı kapanmadı — yaşam döngüsü kimlik modülünden üç adı
  kullanıyor. İmport BİÇİMİ hükme çevrildi, ad kümesi AÇIK. **Kapanması ek belgesinin
  revizyonunu ister; o tasarım katmanının işidir** — yürütücü bağlayıcı metni yeniden yazmaz.
  Kodda, testte ve commit mesajında etiketli. **"Ele alındı" DEĞİL.**
- **KABUL EDİLMİŞ RİSK (checkpoint 2, low):** `a34d3f6`'nın `green-only` etiketi tarihsel
  olarak yanlış; o commit sıra değişikliğini testsiz indirdi, ayırt edici test bir sonraki
  commit'te geldi. HEAD kapsanıyor ama bu aralık için "her commit'te TDD" iddiası YAPILAMAZ.
  Düzeltilmiyor: geçmiş değişmez, ikinci commit yeniden yazımı (ilki altı commit'e mal oldu)
  düzelttiğinden büyük bedel çıkarır.
- **KONTROLÖRÜN KENDİ ÖLÇÜM PROBU İKİ KEZ SONUCU KİRLETTİ — en taze ders.** Birincisi:
  mutasyonu dosyanın açıklama metnine enjekte etti (orada import cümlesi düz yazı olarak
  anılıyordu), mutasyon inert kaldı ve kapı "kaçırıyor" gibi göründü. İkincisi: ölçüm satırı
  basamak sayısını yazdırmak için bir işlem çağırdı ve **ölçmek istediği hatayı probun kendisi
  fırlattı**, sonuç "düzeltme çalışmıyor" gibi göründü. İkisinde de ilk okuma "uygulayıcı
  yanlış söylüyor"du ve ikisi de YANLIŞTI. **Ders: ölçüm disiplini ölçümün KENDİSİNE de
  uygulanır** — bir prob beklenmedik sonuç verdiğinde önce probu sorgula, sonra iddiayı.
- **Düzeltme turu 1'in İKİ ölçümü YETERSİZ çıktı ve bunu bir sonraki tur gösterdi:**
  (a) hash örneklemi hiç büyük tamsayı taşımıyordu — tam da kayan sınıf oydu; (b) ayırt
  edicilik ölçümü elle seçilmiş TEK bir mutlak import'a bakıyordu — göreceli ve dolaylı
  biçimler kapıdan sessizce geçiyordu. İkisi de yanlış güven verdi. **Kapanış üretilmiş
  matrisle kanıtlanmalı; tek örnek kanıt değildir.**
- **Aynı sınıf Task 3'te üç tur üst üste tekrarladı:** düzeltme metninin KENDİ içinde
  ölçülmemiş atıf. Bu oturumun uygulayıcıları kendi atıflarını denetledi ve birkaçını ilk
  yazımda yanlış bulup düzeltti — sınıf canlı, her turda atıf denetimi koşulmalı.
- **KABUL EDİLMİŞ RİSK (arayüz eki):** "annotation çalışma zamanı zorlaması değildir"
  sınıfının kalıntısı ve kimlik karşılaştırmalarındaki hoşgörülü normalleştirme. Statik
  çözümleyici bunun iki örneğini "erişilemez kod" diye işaretliyor (kimlik modülünde iki
  çalışma zamanı koruması); hakem bunları çalışma zamanı kusuru SAYMADI. Üçüncü uyarı
  (`__dataclass_params__`) araç eksiği — hakem de aynı yargıya vardı.
- **KABUL EDİLMİŞ RİSK (checkpoint 1):** `test_external_repo_gitignores_run_folder` git ortam
  değişkenleriyle sahte bir depoya yönlendirilebilir. Üretim pin yolu etkilenmiyor.
  Evi Task 18 Step 8b.
- **KABUL EDİLMİŞ RİSK:** dış deponun içinde dışarıyı gösteren sembolik bağ ele alınmıyor;
  kapatmak ekin R14 hükmünün yasakladığı beşinci kapıyı gerektirir. **"Ele alındı" DEĞİL.**
- **Kapalı izin listelerinin sürtünme bedeli (dürüst kayıt):** yaprağın meşru bir yedinci adı
  eklendiğinde kimlik kapısı DÜŞER, çünkü karşılaştırma tam eşitliktir. Sözleşme testi için
  kasıtlıdır, ama bedeli var — gizlenmiyor.
- **Plan, hakem görmeden onaylanmıştı** (`approved-by-iteration-limit`). Arayüz eki 8 çelişki
  + 12 boşluğu kapattı ama **Plan 1 alanındaki kart geçişi hâlâ taranmadı**.
- **Codex maliyeti:** bu oturumda **3** Codex çağrısı (checkpoint 2 + iki kapanış-doğrulama
  turu). Final için **≥3 tur rezerve** kalmalı; oturum tavanı 8.

# Notes For Claude/Codex

- **Hakem turlarını Claude koşar — SORMA.** Eray'ın kalıcı kuralı.
- **Kontrolör düzeltme YAPMAZ.** Tek istisna `docs/active/` — kontrolörün kendi yüzeyi.
  Bu oturumda hakemin bir high'ı tam olarak orada çıktı ve kontrolör kendisi kapattı.
- **Hakemin severity'si bağlayıcı DEĞİL, ölçüm bağlayıcı.** Bu oturumda bir medium high'a
  yükseldi (kendi ürettiğimiz gerileme + bağlayıcı hüküm ihlali), bir high ölçülen
  erişilemezlik yüzünden evine geri kondu, bir medium ise "gerileme mi fazla-geniş iddia mı"
  ayrımı ölçüldükten sonra dar bir dürüstlük düzeltmesine indi.
- **Kendi ürettiğin medium'u park etme.** Politikanın medium-advisory izni ÖNCEDEN VAR OLAN
  borç içindir; gerileme bu yürütmenin ürünüyse düzeltilir.
- **Modül taşımasında sadakat İDDİA EDİLMEZ, ÖLÇÜLÜR.**
- **Spec değil, spec-input kanoniktir.**
- **Uygulayıcı raporunu doğrulanmamış iddia say** — ama iyi uygulayıcı kendi kusurunu bildirir:
  bu oturumdakiler kapatamadıkları ayağı gizlemedi, bağlayıcı ek metnini kendi başlarına
  yeniden yazmaya kalkmadı, ve kapsam dışı gördüklerini dokunmadan bildirdi.
- Diskte bekleyen düzeltme YOK; her iki çalışma ağacı da temiz.
