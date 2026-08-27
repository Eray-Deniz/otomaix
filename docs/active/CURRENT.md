# Active Tasks

- **sektor-bilgi-paketi-plan2** — Plan 2 işletim hattı; plan ONAYLI (20 görev, risk kabulüyle — son iki düzeltme partisi incelenmedi), sıradaki adım yürütme

## Proposed (spun-off)

- **sector-package-unreviewed-merge-surface** (proposed, review borcu; DÜŞÜRÜLDÜ — koşullu) —
  Plan 1 kapanışında iki kod commit'i **hiçbir bağımsız hakem görmeden** main'e girdi:
  `39f283d` (yaşam döngüsünün `sector_package_lifecycle.py`'ye taşınması) ve `3561231`
  (n8n workflow'unun credential'a bağlanması). Zincir raporları `bf9e080` ve `b15ab6e`'de
  duruyordu; sonraki 10 commit'in ikisi koddu. Eray merge kararını bunu bilerek verdi.
  **Neden yeniden review turu açılmıyor:** birincisi bayt-aynı bir taşıma (fark yalnız kasıtlı
  başlık satırı, `git show` ile ölçüldü) ve kapsülleme testi mutasyonla doğrulandı; ikincisi üç
  regresyonla bağlı, üçü de mutasyonla doğrulandı. Tek başına bir review zinciri koşturmak
  (iki hakem, üç tur) bu yüzeyin taşıdığı riskle orantısız.
  **Dürüst etiket: incelenmedi + bilinçle düşürüldü** — "incelendi" DEĞİL.
  **Yeniden açılma koşulu:** (a) yaşam döngüsü modülünde veya yönetici-olay workflow'unda bir
  kusur çıkarsa, ilk bakılacak yüzey bu iki commit'tir; (b) Plan 2 review zinciri tabanını
  `a11390d`'ye çekerse bu aralık kendiliğinden kapsanır.
  **Dikkat:** Plan 2 kendi aralığını inceler, bu commit'ler onun TABANINDA kalır — yani
  kendiliğinden kapsanmazlar.

- **n8n-credential-host-drift** (proposed; iki örnek DÜZELTİLDİ, sınıf TARANDI, geriye yalnız
  uyarısızlık kaldı) —
  n8n'in `Postgres account` credential'ı **sabit IP** (`10.0.1.8`) taşıyordu; veritabanı
  konteyneri yeniden başlayınca adres `10.0.1.9` oldu ve credential güncellenmedi.
  **Sessizce kırdığı iş (ölçüldü 2026-08-26):** CRM-4 Churn Taraması ve CRM-5 Deneme Bitiyor
  günlük turları **14'er kez** `Connection refused` ile düştü, sonuncusu o gün — kimse fark
  etmemişti. Sektör paketi teslim testi kazara ortaya çıkardı.
  **Düzeltildi:** host artık konteyner **ismi** (`wlg6ned4e72aty3pqhnxs0hg`) — IP değişse de
  bozulmaz. Doğrulandı: aynı credential'ı kullanan Postgres düğümü başarılı çalıştırmada koştu.
  **Sınıfın asıl zararı uyarısızlık:** günlük bir otomasyon iki hafta sessizce düşebiliyor ve
  kimse haberdar olmuyor. Sabit-IP taraması yapıldı (aşağıda), uyarı mekanizması hâlâ yok.
  **(a) Tarama YAPILDI — sınıfın kapsamı ölçüldü, n8n'in dışına taşmış:**
  - n8n credential'ları (2026-08-26, altı credential, çözülmüş değerler üzerinde): hiçbirinde
    sabit IP yok — ya adres alanı taşımıyorlar ya isim kullanıyorlar.
  - n8n workflow gövdeleri (2026-08-27 tekrar koşuldu, 18 workflow / 13 aktif): sabit IP taşıyan
    workflow YOK.
  - **İkinci kurban bulundu ve düzeltildi:** `crm.otomaix.com` uygulamasının kendi `DATABASE_URL`'ü
    de `10.0.1.8`'e bakıyordu. Uygulamanın kendi kütüphanesiyle ölçüldü: `ECONNREFUSED`. Adres
    Coolify katmanından konteyner ismine çevrildi (şifreleme bozulmadı, ham kayıt hâlâ şifreli),
    deploy tetiklendi, sonra tekrar ölçüldü: `BAĞLANDI ✓ accounts=1`, site HTTP 200.
  - **Kök tarih:** üç kopuşun üçü de 2026-08-11 15:06'da konteynerler yeniden başladığında oldu —
    Coolify SSH anahtarı olayıyla aynı an ([[reference_coolify_ssh_key]]).

  **(b) Bildirim HÂLÂ YOK — çözülmedi + park edildi.** Ölçüldü (2026-08-27): 18 workflow'un
  **hiçbirinde** `errorWorkflow` ayarı yok. Yani bugün de başarısız bir n8n turu kimseye
  ulaşmıyor; bu maddeyi doğuran sessizlik aynen duruyor.
  **Bugün neden hâlâ önemli:** bu kalem CRM yüzünden doğdu ama CRM'e ait değil — sektör paketi
  yönetici bildirim zinciri CANLI ve aynı sessizliğin altında koşuyor. Düşürülmüyor.
  **EV VERİLDİ (2026-08-27, plan onaylandı):** Plan 2 → **Task 16, Step 7 + 7b** —
  `n8n-error-notifier.json` yazılır ve `sector-package-admin-events.json`'a `errorWorkflow`
  olarak bağlanır, üç sözleşme testiyle birlikte.
  **Kapsam bilinçle DAR:** yalnız sektör paketi yönetici olay workflow'u. Kalan 17 workflow
  (CRM-4/CRM-5 dâhil) o turda da sessiz kalmaya devam eder — onların evi CRM turudur.
  **Tarih:** Task 16 koşana kadar yok; yürütme başlamadı.
  **(c) CRM ayağı DÜŞÜRÜLDÜ — Eray kararı 2026-08-27:** CRM henüz kullanılmıyor (Otomaix'in
  kendisi bitmedi) ve CRM bütün olarak ayrı bir turda ele alınacak. Dolayısıyla CRM-4/CRM-5
  turlarının bugün `success` dönmesini beklemek aktif borç DEĞİL. Bilinen durum kayda geçsin:
  düzeltme yapıldı ve tek dolaylı kanıtı var (aynı credential'ı kullanan Postgres düğümü
  başarılı bir çalıştırmada koştu, 2026-08-26) — **zamanlanmış turla doğrulanmadı.**
  **Yeniden açılma koşulu:** CRM'in bütün olarak ele alınacağı tur — ilk iş o iki günlük turun
  gerçekten koştuğunu ölçmektir.

- **sector-package-assignment-ui-live-verification** (proposed, doğrulama borcu; EVSİZ KALMIŞTI —
  şimdi ikiye bölündü) —
  Task 15'in **elle arayüz doğrulaması** (plandaki Step 5) ile öneri ucunun gerçek model
  çağrısıyla koşulması, Eray kararıyla "Plan 2 sonrası tek tura" ertelenmişti; evi
  `sector-package-live-activation` maddesiydi ve o madde 2026-08-26'da kapanırken bu kalem
  **beraberinde silindi** — hiçbir yerde kalmamıştı. Yeniden ev veriliyor.
  **Koşullar değişti:** frontend artık canlıda (image `6534051` = main, ölçüldü 2026-08-26 20:48),
  yani arayüz gözle görülebilir durumda. Ama canlıda **aday küme BOŞ** (ölçüldü 2026-08-27:
  alt sektör 0 · aktif paket 0 · atanmış marka 0).
  **(i) BUGÜN doğrulanabilir — Eray'ın gözü gerekir, ~10 dakika:** boş-aday hâlinde bileşenin
  pasif/boş görünmesi (planın bağlayıcı invariantı) + kanal envanteri alanlarının doldurulması.
  Marka ayarları ve onboarding sayfalarında.
  **(ii) Plan 2'ye kadar doğrulanamaz — ölçülmüş sebep:** onayla/değiştir/boşalt üçlüsü aday küme
  ister, öneri ucu ise boş aday kümesinde tanım gereği HER ZAMAN boş döner (Task 15 invariantı).
  Yani bugün gerçek model çağrısı yakmak hiçbir şey kanıtlamaz — yalnız para harcar.
  **Ev VERİLDİ (2026-08-27):** Plan 2 → **Task 19, Step 11** — ilk paket aktive edildikten
  hemen sonraki kabul adımı. Hem (i) hem (ii) aynı adımda: atama arayüzünün üçlüsü + öneri
  ucunun gerçek model çağrısıyla koşulması + boş-aday hâlinde bileşenin pasif görünmesi ve
  kanal envanteri alanları.
  **Plan ONAYLANDI (2026-08-27), ama tarih hâlâ YOK:** yürütme başlamadı, pilot koşulmadı.
  Dürüst etiket: *çözülmedi; evi var, tarihi pilot görevinin koşmasına bağlı.*

- **s1-substrate-tracked-secret-scan** (proposed, güvenlik/defense-in-depth) — `CODEX-SCAN-SUBSTRATE` (byte-locked 4-way) tracked-dirty diff'i secret-scan ETMİYOR (yalnız untracked REQUIRED taranıyor; `git apply` execute-plan:1228-1231 vs `_css_secret_scan` 1233-1238). Dar (committed içerik zaten in-scope; yalnız tracked-dosyada-uncommitted-secret) ama düzeltmeli. Detay + structured fix: security-review **SF1** (`docs/security-reviews/2026-06-04-codex-review-scope-contract.md`). Kapsam: substrate bloğu (4 dosya) + `codex-scan-substrate-harness.sh` tracked-secret fixture.
  **Yeniden açılma koşulu / tetik (2026-08-27'de eklendi — bu kalem tetiksiz kalmıştı):**
  substrat bloğuna dokunan bir sonraki iş; `codex-scan-substrate-preflight-guard` ve
  `codex-substrate-dirty-secret-excluded-file` ile **aynı pin'li blok**, üçü tek turda.

- **stale-sweeper-vs-late-webhook-terminality** (proposed, ürün kararı + arka uç tutarlılığı) —
  Süpürücü `generating`i **10 dakikada** `failed` yapıyor (`internal.py`
  `interval '10 minutes'`), ama `fal_webhook` tek görsel/video satırını
  `fal_job_id` ile bulup durum kapısı OLMADAN sonradan `ready` + `output_url`
  yazabiliyor. Yani arka uçta `failed` terminal DEĞİL; iki mekanizma aynı satır
  hakkında çelişebiliyor. **10 dakikanın ölçülmüş bir dayanağı YOK:** vault
  kararı ([[decisions/2026-03-25-stale-job-sweeper]]) gerekçeyi "webhook kaybı
  güvenlik ağı" diye yazıyor, model süresi ölçümüne ya da sağlayıcı belgesine
  dayanmıyor (kaydın kendisi `verification-status: unverified`).
  **Karar Eray'a ait:** geç gelen başarı kabul edilsin mi, yoksa eşikten sonrası
  kesin başarısız mı sayılsın — ve eşik hangi ölçüme dayansın.
  **Tetik (Eray, 2026-08-25): sektör bilgi paketi işi TAMAMEN bittikten sonra
  ele alınacak** (fal.ai model değişikliği de o dönemde planlanıyor; eşik o
  modellerin gerçek süreleriyle birlikte gözden geçirilmeli).
  Şimdilik yalnız arayüz arka uçla tutarlı hâle getirildi (`532825e`);
  sözleşmenin kendisi ÇÖZÜLMEDİ.

- **sector-package-sector-id-immutability** (proposed, veri bütünlüğü; TETİKLİ — bugün aktif borç DEĞİL) —
  `social.sector_packages.sector_id` yazımdan sonra değişmez değil. Yaşam döngüsü geçişleri
  (checkpoint 13 / F4) uyuşmazlıkta artık **fail-closed durur**, ama pencerenin kendisi
  kapanmadı: paket kilitlenmeden önce okunmak zorunda, dolayısıyla sektör kilidi ile hedef
  kilidi arasında bir yeniden-atama penceresi var. Kapanması kolonu değişmez kılan bir
  migration ister (tetikleyici ya da kısıt) ve Task 13'ün dosya kapsamı dışındaydı.
  **Ölçüldü:** depo genelinde bu kolonu güncelleyen üretim yolu YOK.
  **Yeniden açılma koşulu:** sektör yeniden-atama özelliği istenirse VEYA Plan 2 bu kolona
  bir yazıcı eklerse — o durumda migration ZORUNLU olur.
  Gövde: `docs/active/sektor-bilgi-paketi/HANDOFF.md` Risks + `_require_same_sector` docstring'i.

- **brand-settings-save-integrity** (proposed, ürün kalitesi + veri bütünlüğü; MÜŞTERİ yüzeyi) —
  Marka ayarları sayfası müşterinin kendi doldurduğu yüzeydir ve otomatik kaydetmesinin
  **dört açık kayıp yolu** var: (a) yazıp bekleme süresi dolmadan çıkma — istek HİÇ gitmez,
  uyarı yok (depoda tek bir "kaydedilmemiş değişiklik" koruması bulunmuyor, ölçüldü);
  (b) aynı sekmede sıra bozulması — iki istek aynı anda havada olabilir, eski olan sonra
  varırsa yeniyi ezer; (c) iki sekme/iki cihaz — sekmeler birbirini görmez; (d) "Kaydedildi"
  yazısı bekleyen iş varken de yanabilir.
  **Kapsam bir ÖZELLİK değil ALT SİSTEM:** kirli-durum modeli · akış başına kayıpsız kuyruk ·
  satırı değiştiren HER yolda sürüm koruması (marka · kimlik bilgileri · logo · tanıtım
  videosu · avatar) · taslağın yerel saklanması · dayanıklı çıkış gönderimi · durum-kodu bilen
  hata ayrımı (bugün ortak istemci HTTP durumunu düşürüyor, o yüzden çakışma ile ağ hatası
  ayırt edilemiyor).
  **Ölçüldü (2026-08-25):** bu alt sistemi tek turda elle yazma denemesi (Task 15b) BEŞ high
  bulgu üretti ve iki yolda geri aldığı hatadan kötüydü; geri alındı (`d9c4264`). Kök neden
  yöntemdi: önyüzde otomatik test altyapısı YOK, doğrulama "okundu + derlendi" ile yapıldı ve
  bu yöntem araya-girme hatalarını tanım gereği yakalayamaz.
  **Hazır duran parça:** sunucu tarafındaki koşullu yazım kapısı ve beş testi depoda UYKUDA
  (hiçbir çağıran sürüm göndermiyor) — bu işin giriş noktasıdır.
  **Ürün kararı önce gelir:** otomatik kaydetmeyi garantili hâle getirmek mi, yoksa sayfayı
  açık "Kaydet" düğmesine çevirip sınıfın çoğunu silmek mi. Eray 2026-08-25'te otomatik
  kaydetmeyi korumayı seçti; bu madde o zeminde açılır.
  **Yeniden açılma koşulu / tetik:** Plan 1 kapanışından (Task 16) sonra, canlıya müşteri
  alınmadan ÖNCE. Önyüz test altyapısı bu işin ön koşuludur — onsuz aynı yöntem hatası
  tekrarlanır.

- **sync-provider-calls-not-cancellable** (proposed, dayanıklılık; kod tabanı GENELİ desen) —
  Model çağrıları senkron istemciyle yapılıyor ve olay döngüsünün dışına alınsa bile
  **gerçekten kesilemiyor**: süre sınırı yalnız BEKLEMEYİ keser, çalışan çağrı iş parçacığını
  tutmaya devam eder. Sağlayıcı asılırsa kullanıcı zamanında hata alır ama işçi kapasitesi
  dolu kalır. Desen tek bir uca ait DEĞİL — başlık üretimi, kısa video, site analizi ve alt
  sektör önerisi aynı biçimde çağırıyor.
  **Bu partinin kusuru değil** (Task 15'in ürünü olan somut kusurlar — SDK'nın kendi yeniden
  deneme çarpanı, yanıt biçimi doğrulaması, önyüzün arızayı gizlemesi — `f17e248`'de kapatıldı).
  Tek uçta async istemciye geçmek onu evin geri kalanından ayırırdı; kararın kapsamı desenin
  kendisidir.
  **Yeniden açılma koşulu / tetik:** canlıya gerçek müşteri yükü alınmadan ÖNCE, ya da eşzamanlı
  kullanımda işçi doygunluğu gözlenirse. Bugün acil değil çünkü uçlar kota kapılı ve gerçek
  eşzamanlı yük yok — ama "yok" ölçülmüş bir sayı değil, bugünkü kullanım biçiminin sonucu.

- **codex-scan-substrate-preflight-guard** (proposed, araç güvenilirliği; global `~/.claude` işi) —
  `run_codex_scan` (`~/.claude/commands/blocks/codex-scan-substrate.sh`) `$COMPANION` ve
  `$PROMPT` değişkenlerini KULLANIR ama TANIMLAMAZ; ikisini de çağıran kurar. Kurulmazsa
  `node ""` koşar ve **sessizce yanlış davranır**: arka planda stdin hemen kapandığı için
  exit 0 + boş çıktı (rc=5 "sessiz başarı yok" kapısına düşer), ön planda stdin açık kaldığı
  için ASILI kalır (rc=124). Semptom "Codex bozuk" gibi görünür; kota, substrat ve timeout
  hipotezlerinin hepsi yanlış yöne çeker. **Ölçüldü (2026-08-25): yedi Codex çağrısı yaktı.**
  Düzeltme dar: fonksiyon başında `[ -n "${COMPANION:-}" ]` ve `[ -n "${PROMPT:-}" ]`
  fail-closed kapıları (mevcut `CODEX_LOG` kapısının birebir eşi — simetri zaten yazılı).
  **Dikkat:** blok T5 sha256 pin'lidir; değişiklik `command-blocks-maint.sh repin <aile>` +
  `verify` ritüeli ister ve 7 komutu birden etkiler.
  **Yeniden açılma koşulu / tetik (2026-08-27'de eklendi — bu kalem tetiksiz kalmıştı):**
  substrat bloğuna dokunan bir sonraki iş. Üç `~/.claude` kalemi
  (`s1-substrate-tracked-secret-scan` · bu · `codex-substrate-dirty-secret-excluded-file`)
  **aynı pin'li bloğa** dokunuyor — tek turda birlikte yapılırlar, ayrı ayrı repin ritüeli
  koşturmak israftır.

- **codex-substrate-dirty-secret-excluded-file** (proposed, araç güvenilirliği; global `~/.claude` işi) —
  Codex denetim ortamı, sır taraması dışladığı bir dosyada **kaydedilmemiş değişiklik** varsa
  **hiç kurulamıyor**: dosya kopyadan siliniyor, sonra overlay yamayı ona uygulamaya çalışıp
  `No such file or directory` ile düşüyor → **rc=2, Codex hiç çağrılmıyor.** Semptom "Codex
  bozuk" gibi görünür; stderr'de `[codex]` işareti hiç çıkmaz.
  **Kapsam dar değil:** tetikleyen desen içerik tarayıcısının zayıf ailesindeki
  `api_key=<ifade>` biçimi ve bu, model çağıran HER dosyayı dışlıyor — **ölçüldü (2026-08-26):**
  altı üretim dosyası, üçü o gün değişmişti. Değerler ayar referansı, sır literali değil;
  bloğun kendi yorumu bu sınıfı belgeli yanlış pozitif sayıyor.
  **Bugünkü çözüm bir SAPMA:** değişikliği hakeme düz metin olarak gömmek + çağrı biçimini
  değiştirmek + "hayalet silme satırlarını yoksay" talimatı eklemek. Çalışıyor ama komutun
  ilan ettiği biçim değil ve her seferinde kullanıcı onayı istiyor.
  **Temiz ağaçta sorun YOK** — taban-tabanlı denetim commit'lerden okur.
  **Yeniden açılma koşulu / tetik:** kirli ağaçta denetim gerektiren bir sonraki komut
  (`/simplify-claude-codex` tekrar koşarsa) VEYA `s1-substrate-tracked-secret-scan` maddesi
  ele alınırken — ikisi aynı bloğa dokunuyor, birlikte yapılmalı.
  **Dikkat:** blok sha256 pin'lidir; değişiklik `command-blocks-maint.sh repin` + `verify`
  ritüeli ister ve 7 komutu birden etkiler (aynı uyarı `codex-scan-substrate-preflight-guard`
  maddesinde de var).

<!-- Son kapanan: codex-review-scope-contract → done 2026-06-04, arşiv docs/task-archive/2026/06/ -->

