# Active Tasks

- **brief-sozlesmesi-kaynak-bolumu-makine-okunur** — Araştırma sözleşmesinin çıktı biçimini makine-okunur kesinliğe getirme (dış sözleşme metni + denetçi metni + pin + mekanik kapı). Durum: `docs/active/brief-sozlesmesi-kaynak-bolumu-makine-okunur/TASK.md`
- **sektor-bilgi-paketi-plan2** — Sektör bilgi paketini üreten ve aktive eden işletim hattı (Plan 2, 20 görev). Durum ve sıradaki adım: `docs/active/sektor-bilgi-paketi-plan2/TASK.md`

## Proposed (spun-off)

- **brief-sozlesmesi-kaynak-bolumu-makine-okunur** — GÖREVE DÖNÜŞTÜ 2026-09-07; artık
  kendi dosyası var, gövde ORADA yaşar (iki yerde birden değil):
  `docs/active/brief-sozlesmesi-kaynak-bolumu-makine-okunur/TASK.md`. Yukarıdaki aktif
  listede de görünür.

- **plan2-ek-bagimlilik-hukmu-ad-kumesi** (proposed, TASARIM KARARI — yürütücü çözemez;
  TETİKLİ) — Plan 2'nin bağlayıcı arayüz eki, yaşam döngüsü modülünün kimlik modülünden
  **yalnız kanonik hash adını** kullanmasını şart koşuyor. Ölçüldü (2026-08-31): modül
  gerçekte **üç** ad kullanıyor — kanonik hash artı karar günlüğünün şema kapısı ve birim
  bütünlüğü kontrolü. İkisi de `insert_draft`'ın içinde koşuyor ve ekin kendi hükmü "ikinci
  bir kural YAZILMAZ" dediği için kopyalanamıyorlar.
  **Yürütmede kapatıldı sanılmasın:** import BİÇİMİ hükme çevrildi (o ayak kapandı ve
  yapısal kapı üretilmiş matrisle bunu zorluyor), **ad kümesi ayağı AÇIK**.
  **Neden yürütücü kapatamaz:** kapanışın iki yolu var ve ikisi de tasarım kararıdır —
  (a) ek hükmü ölçülen gerçeğe göre revize edilir (üç ada izin verilir, gerekçesiyle),
  (b) şema kapısı yaşam döngüsünden çıkarılıp başka bir yere taşınır (bu, Plan 1'in yazım
  kapısı mimarisini değiştirir). Yürütücü bağlayıcı ek metnini yeniden yazmaz.
  **Dürüst etiket: çözülmedi + park edildi; sapma kodda, testte ve commit mesajında etiketli.
  "Ele alındı" DEĞİL.**
  **Tetik:** Task 8 dispatch'i — ek, o göreve bir yapısal test sözü veriyor ve o testin
  hangi hükme karşı koşacağı bu kararla belirlenir. Task 8'e gelinmeden karara bağlanmazsa
  görev orada durur.
  **İKİNCİ KANIT (2026-09-06, checkpoint 4):** ek, kanonik kimlik kapısını
  `sector_package_lifecycle._require_actor` diye SATIR NUMARASIYLA adlandırıyor; olay yazıcısının
  da aynı kapıyı kullanması gerekince tanım `package_events.require_actor`a taşındı — ölçüldü ki
  ters yönde ikinci bir import DÖNGÜdür (`ImportError`). Ad ve davranış aynı, ikinci kural kopyası
  yazılmadı; **sapan şey tanımın YERİ.** Yani ekin bu bölgesi kodla ikinci kez uyumsuz.

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
  **O ÖLÇÜM YAPILDI (2026-09-07, n8n çalıştırma geçmişinden):** CRM-4 ve CRM-5'in günlük turları
  3·4·5·6 Eylül'de **dördü de `success`** döndü. Yani host düzeltmesi artık dolaylı değil
  doğrudan kanıtlı; bu ayak KAPANDI. **Dikkat:** `success` "Telegram gitti" demek DEĞİLDİR —
  koşum büyük olasılıkla koşul dalında durdu (müşteri verisi yok).
  **Yeniden açılma koşulu:** CRM'in bütün olarak ele alınacağı tur.

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

- **n8n-workflow-sir-hijyeni** (KAPANDI 2026-09-06 — iki ayak da çözüldü; ÜÇÜNCÜ ayak
  ayrıldı, aşağıya bakınız) — Task 5 yürütülürken üstüne denk gelindi; Task 5'in ürünü DEĞİLDİ.
  **(a) Çıplak Telegram bot token'ı — ÇÖZÜLDÜ.** Token operatör tarafından döndürüldü (BotFather),
  eskisi ölçüldü: `401 Unauthorized`. Sekiz yer (`crm-automations.json` 7 düğüm ·
  `turkey-calendar-update.json` 1 düğüm) `telegramApi` credential'ına bağlandı — yönetici
  workflow'unun zaten kullandığı desen. Commit `dadb343`.
  **(b) Kaçışsız tarih enterpolasyonu — ÇÖZÜLDÜ.** `${h.year}` ve `${h.date}` artık
  `Number(...)` / `escape(...)` ile giriyor; aynı commit.
  **Sınıf kapısı kondu:** `test_no_workflow_file_carries_a_bare_secret` (dizin geneli üretilmiş
  matris) + `test_calendar_sql_escapes_every_interpolated_feed_value` (her enterpolasyon).
  İkisi de mutasyonla sınandı. Test tabanı 963 → 965.
  **KALAN AYAK DA KAPANDI (2026-09-07, Eray onayıyla): canlıya import EDİLDİ.** Yedi workflow
  (CRM-1..6 + Türkiye Takvimi) n8n API'siyle güncellendi; yükleme gövdesi yalnız `nodes` +
  `connections` taşıdı, `settings` ve `name` canlıdan korundu. **Ölçüldü (yükleme sonrası, tek
  tek):** çıplak token **0** · `telegramApi` credential'ı bağlı · yedisi de `active=True`.
  **Yüklemeden ÖNCE ölçülen iki depo kusuru düzeltildi (`9a46948`), yoksa import canlıyı
  bozardı:** (a) depo dosyası canlıda var OLMAYAN bir Postgres credential kimliğine (`id=1`)
  işaret ediyordu — dört CRM workflow'unun veritabanı düğümü credential'sız kalırdı;
  (b) CRM-3'ün webhook yolu depoda yarım kalmıştı (canlıda alert doğru/reminder yanlış, depoda
  tam tersi). İki sınıf kapısı eklendi (`624e0b3`): tek postgres credential kimliği · webhook
  yükünün sarmalayıcı anahtardan okunması.
  **ÖLÇÜLMEYEN, dürüstçe:** `telegramApi` credential'ının canlı token taşıyıp taşımadığı.
  Hiçbir koşum Telegram düğümüne ULAŞMADI (CRM'de gerçek müşteri verisi yok), dolayısıyla
  "bildirimler artık gidiyor" İDDİA EDİLMİYOR — yalnız "ölü token artık hiçbir workflow'da yok".
  **Kapsam sınırı, dürüstçe:** yeni tarama kapısı YALNIZ `shared/n8n-workflows/` klasörüne bakar.
  `docs/archive/CLAUDE_crm_pre_cleanup.md` şu anki ağaçta aynı (artık ölü) token'ı taşıyor ve
  kapı onu görmez. Zararsız ama duruyor.

- **telegram-credential-live-token-unverified** (proposed, doğrulama borcu; TETİKLİ —
  CANLI bir zinciri ilgilendiriyor) — n8n'in `Telegram account` credential'ı
  (`VMbwUuFB8BzVhxEz`) **canlı bir token taşıyor mu, ÖLÇÜLMEDİ.** Token 2026-09-06'da
  operatör tarafından BotFather'da döndürüldü ve eskisinin öldüğü doğrulandı (`401`), ama
  n8n credential'ının YENİ tokenla güncellenip güncellenmediği hiçbir yerde ölçülmedi.
  **Neden bugün kapatılamadı:** yükleme sonrası hiçbir koşum Telegram düğümüne ULAŞMADI —
  CRM'de gerçek müşteri verisi yok, tetiklenen tek workflow (sektör paketi yönetici olayları)
  her beş dakikada süpürme dalında dönüyor ve gönderecek olay bulamıyor. `success` durumu
  "Telegram gitti" demek DEĞİLDİR.
  **Neden önemli:** bu credential'ı **canlı** sektör paketi yönetici bildirim zinciri de
  kullanıyor. Token ölüyse o zincir de sessizdir ve kimse haberdar olmaz — bu, zaten kayıtlı
  olan `n8n-credential-host-drift` uyarısızlık sınıfının aynısıdır.
  **Kendi maddesi VAR, çünkü bir kez kaybolmuştu benzeri:** `sector-package-assignment-ui-
  live-verification` kalemi, evi olan madde kapanırken beraberinde silinmişti. Bu kalem
  kapanan `n8n-workflow-sir-hijyeni` maddesinin içinde bırakılsaydı aynı şey olurdu.
  **Nasıl ölçülür (bir dakikalık iş):** yönetici olay ucuna (`sector-package-admin-events`,
  `headerAuth` + `.env`deki `N8N_ADMIN_EVENT_SECRET`) tek bir test olayı gönder; Telegram
  mesajı Eray'ın telefonuna düşerse credential canlıdır. Yan etkisi: bir yönetici olay satırı
  ve bir Telegram mesajı.
  **Dürüst etiket: doğrulanmadı + ölçüm yolu belli.** "Çalışıyor" DEĞİL.
  **Tetik:** sıradaki oturumun başı (bir dakikalık iş, Eray onayıyla), VEYA yönetici bildirim
  zincirine dokunan bir sonraki görev (Task 16), hangisi önce gelirse.

- **crm-webhooks-unauthenticated-sql-interpolation** (proposed, GÜVENLİK; canlı uç KAPATILDI,
  onarım AÇIK — tetikli) — CRM webhook'ları (`crm/new-customer` · `crm/plan-upgrade` ·
  `crm/payment-failed`) **kimlik doğrulaması taşımıyordu** ve `crm/payment-failed`'ın arkasındaki
  Postgres düğümü gelen `account_id`'yi SQL metnine **düz metin olarak gömüyor**:
  `INSERT INTO crm.account_tags (...) VALUES ('{{ $json.body.account_id }}', ...)`. Tırnak içeren
  bir değer bu ifadeden çıkabilir — yani uç, uygulamanın Postgres hesabıyla serbest SQL
  çalıştırmaya açıktı ve o hesap `social` şemasını da görüyor.
  **ÖNCEDEN VAR OLAN yüzey, 2026-09-07 partisinin ürünü DEĞİL:** canlı workflow zaten çalışan
  credential'ı taşıyordu (ölçüldü, yükleme öncesi) ve SQL düğümü depo ile canlıda bayt-aynıydı.
  Checkpoint 5 hakemi bunu high olarak gösterdi, kontrolör canlıda doğruladı.
  **Ölçüldü (2026-09-07, salt-okunur prob):** üç uç da herkese açık cevap veriyordu
  (`GET` → "bu webhook GET için kayıtlı değil, POST mu demek istediniz?").
  Karşılaştırma: `sector-package-admin-events` `headerAuth` taşıyor — doğru desen projede zaten var.
  **YAPILAN (Eray kararı 2026-09-07): üç workflow canlıda PASİFE ALINDI.** Doğrulandı: üçü de
  `active=False` ve `POST` artık `404` dönüyor. İşlevsel kayıp YOK — n8n çalıştırma geçmişinde
  bu üç workflow'un **sıfır** koşumu var.
  **AÇIK KALAN — çözülmedi:** gerçek onarım (header auth credential'ı + parametreli sorgu +
  backend'in `billing.py` çağrısına başlığı eklemesi). Pasifleştirme bir **kapatmadır**,
  düzeltme değil.
  **Ev / tetik:** CRM'in bütün olarak ele alınacağı tur — CRM yeniden aktive edilmeden ÖNCE bu
  üç kalem yapılmak ZORUNDA; aksi hâlde aktive etmek ucu geri açar.

- **telegram-approval-token-in-query-string** (proposed, güvenlik; TETİKLİ — bugün aktif borç
  DEĞİL) — `telegram-content-approval.json` onay/ret düğmelerinin adresini kurarken müşterinin
  kendi bot şifresini **URL sorgu parametresine** gömüyor
  (`.../webhook/tg-approve?post_id=...&bot_token=<şifre>&chat_id=...`); `telegram-onayla.json` ve
  `telegram-reddet.json` onu `query.bot_token` olarak okuyor (ölçüldü 2026-09-06).
  **Sınıf farkı:** bu, yukarıdaki (a) maddesiyle aynı şey DEĞİL — şifre depoda değil
  veritabanında (doğru yer), ama mesajın içindeki bağlantıda dolaşıyor. Mesajı gören/ileten
  okuyabilir; ara sunucu ve n8n çalıştırma kayıtlarına düşer.
  **Alternatif biliniyor:** bağlantı yalnız `post_id` taşır, workflow şifreyi veritabanından
  kendisi okur.
  **Dürüst etiket: çözülmedi + park edildi.** Bugün acil değil çünkü bu akış gerçek müşteride
  koşmuyor — ama "koşmuyor" ölçülmüş bir sayı değil, bugünkü kullanım biçiminin sonucu.
  **Yeniden açılma koşulu / tetik:** onay akışına dokunan bir sonraki iş VEYA canlıya gerçek
  müşteri alınmadan önce.

- **repo-public-exposed-live-credentials** (proposed, GÜVENLİK — EN YÜKSEK ÖNCELİK; Eray sırayı
  bilerek seçti: önce Plan 2 bitecek) — Telegram token'ı ararken geçmiş tarandı ve asıl bulgu
  çıktı: **`apps/social/backend/.env` deponun İLK commit'inde var** (`37da813`, 2026-04-08); aynı
  gün `7829f7f` ile kaldırılmış ama git geçmişinde duruyor. **Depo 2026-04-08'den beri public**
  (ölçüldü: kimlik doğrulamasız GitHub API 200).
  **Ölçüldü (2026-09-06, değerler ekrana basılmadan özet karşılaştırmasıyla) — bu anahtarlar
  geçmiştekiyle BUGÜN AYNI, yani canlı:** `SUPABASE_SERVICE_KEY` (tüm satır güvenliğini atlar) ·
  `R2_SECRET_ACCESS_KEY` + `R2_ACCESS_KEY_ID` (tüm müşteri medyası okunur/silinir) · `FAL_KEY`
  (para harcanabilir) · `UPLOAD_POST_API_KEY` (müşteri sosyal hesaplarına paylaşım) ·
  `REDIS_URL` (şifre içeriyor). `DATABASE_URL` değişmiş.
  **Kullanılıp kullanılmadığı ÖLÇÜLEMEDİ** — fork 0 · yıldız 0 · izleyen 0 (ölçüldü), ama public
  GitHub'ı tarayan otomatik sır avcıları var. "Kullanılmadı" iddia EDİLMİYOR.
  **Depoyu private yapmak yetmez** — 5 aylık ifşayı geri almaz; tek gerçek çözüm anahtarları
  yenilemek. Private yapmak ileriye dönük korumadır ve Eray bunu yapacak.
  **Yanlış alarm elendi:** `apps/crm/.next/.../601.js` içindeki `sk-...` eşleşmeleri CSS değişken
  adları (`sk-image-linear-from-pos`), sır değil.
  **Ev VERİLDİ (tarihli): Plan 2 yürütmesi bittiği AN, ilk iş.** Sıra: Supabase servis anahtarı →
  R2 → fal.ai (+ fatura geçmişi taraması) → Upload-Post → Redis. Her yenileme `.env` ve
  Coolify'daki karşılığının güncellenmesini de ister.
  **Dürüst etiket: çözülmedi + ev verildi + tarihi Plan 2'nin bitişine bağlı. "Ele alındı" DEĞİL.**

- **migration-atomicity-outside-035** (proposed, dağıtım dayanıklılığı; **EVSİZ — uydurma ev
  VERİLMEDİ**) — Task 5 kapanışında ölçüldü: `035_holiday_periods.sql` artık desteklenen HER
  çağrı biçiminde atomik (kalıcı olan her şey tek `DO` deyiminde), ama **bu özelliği taşıyan
  tek migration dosyası o.** Diğerlerinin hepsi çok deyimli — ölçüldü: `032_sector_packages.sql`
  üst düzeyde 24 DDL taşıyor — ve **çıplak elle `psql -f` altında yarıda kalabilir**; hata
  sonrası psql `ON_ERROR_STOP` olmadan devam ettiği için çıkış kodu `0` bile dönebilir.
  **Bugün zararsız, çünkü ölçüldü:** onaylı koşum yolu `shared/local-deployment/migrations/
  run-migrations.sh` her migration'ı `--single-transaction` ile sarıyor (satır 206) ve
  `-v ON_ERROR_STOP=1` taşıyor. Yani risk yalnız **betiği atlayıp komutu elle yazan** yolda.
  **Neden Task 5'e sıkıştırılmadı:** kapsam tek dosya değil, dağıtım politikası + runner —
  35 migration'ı tek tek atomik yapmak ya da runner'ı tek meşru yol ilan edip elle koşumu
  kapatmak ayrı bir karardır. Reflekssel olarak Task 18'e yapıştırmak sahte ev olurdu:
  Task 18 kendi dosya kapsamıyla dağıtım runbook'unu yazıyor, 35 migration'ı yeniden
  yazmıyor.
  **Dürüst etiket: çözülmedi + park edildi, EVİ YOK. "Ele alındı" DEĞİL.**
  **Yeniden açılma koşulu:** (a) onaylı koşum yolu sarmalayıcısız hâle gelirse, VEYA
  (b) elle uygulanmış bir migration bir olayda kök sebep çıkarsa — o zaman ilk bakılacak
  yer bu kalemdir.

- **migration-ddl-object-identity-class** (KAPANDI 2026-09-07 — sınıf beş dosyada da kapatıldı) — Bir migration, katalog nesnesini yalnız ADIYLA arayıp koşulsuz
  yazarsa (`CREATE OR REPLACE FUNCTION`) ya da düşürürse (`DROP TRIGGER IF EXISTS`), aynı adı
  taşıyan **YABANCI** bir nesneyi sessizce devralır: fonksiyon kimliği korunduğu için ona bağlı
  başka bir tetikleyici ANINDA bizim gövdemizi çalıştırmaya başlar. Kapalı manifest bunu
  yakalayamaz — ezme işleminden SONRAKİ durumu okur.
  **Nereden çıktı:** Codex checkpoint 4, tur 2 (high). Kontrolör doğruladı ve sınıfı adlandırdı:
  aynı disiplin KISITLAR için zaten uygulanıyordu (036'nın KAPI 2 / KAPI 3'ü); açık kalan
  fonksiyon/tetikleyici VARYANTIYDI.
  **Kapatıldığı yer:** `036_package_runs.sql` (KAPI 4) ve `rollback/036_down.sql` (ayna kapı) —
  yalnız o iki dosya.
  **AÇIK KALAN — ölçüldü (uygulayıcı taraması, kavramdan türetilmiş desen, 2026-09-06):** beş
  dosya sınıfı hâlâ taşıyor — `001_initial_social.sql` · `023_brands_updated_at.sql` ·
  `026_brand_products.sql` · `032_sector_packages.sql` · `rollback/032_down.sql`. 032'nin
  `pg_get_triggerdef` kullanımı YAZIMDAN SONRAKİ manifesttir, yani tam da bu sınıfın kör noktası.
  **Bugün neden acil değil:** kayan/kirlenmiş bir şema gerektiriyor ve hiçbir şey henüz gerçek
  bir ortama uygulanmadı. Ama "uygulanmadı" bir güvence değil, yalnız bugünkü durum.
  **KAPANDI (2026-09-07, `9c69547` + `122867d`; test tabanı `c62e74a`).** Beş dosyanın hepsine
  kapı kondu. Kanonik sabitler elle yazılmadı: 032'nin fonksiyon gövdeleri dosyanın kendi
  metninden, tetikleyici tanımları dosyanın KENDİ `$verify$` bloğundan, geri alma kapsamı da
  down dosyasının kendi `DROP` satırlarından türetildi.
  **Sınıf kapatıldı, varyant değil:** yeni test modülü dosya listesini de nesne listesini de
  KAVRAMDAN türetir — kapısız bir migration eklendiği an kırmızı düşer. Mutasyon kolu kapının
  varlığını değil ETKİSİNİ ölçüyor ve zararın iki biçimini ayırıyor: fonksiyonu YAZAN dosya
  yabancı gövdeyi ezer; ona yalnız BAĞLANAN dosya (023 · 026) kendi tetikleyicisini yabancı
  gövdeye bağlar.
  **Kalan sınır, dürüstçe:** kapı SIFIR argümanlı adı denetler (farklı imzalı aşırı yükleme
  kapsam dışı, gerekçesi yazılı); `rollback/032_down`'da kapı `DROP TABLE` satırlarından SONRA
  gelir (tek transaction olduğu için ret hiçbir adımı kalıcı bırakmaz, ama sıra "en başta"
  değildir); çıplak `psql -f` altında `ON_ERROR_STOP` yoksa erken deyimler kalıcı olabilir —
  o ayrı bir parked kalem (`migration-atomicity-outside-035`).
  Taze ölçüm: tam takım **1493 passed in 548.28s**, exit 0 (taban 1452, düşmedi).

<!-- Son kapanan: codex-review-scope-contract → done 2026-06-04, arşiv docs/task-archive/2026/06/ -->

