# Active Tasks

- `sektor-bilgi-paketi/` — sektör bilgi paketi runtime çekirdeği (Plan 1; dal `feat/sektor-bilgi-paketi`)

## Proposed (spun-off)
- **s1-substrate-tracked-secret-scan** (proposed, güvenlik/defense-in-depth) — `CODEX-SCAN-SUBSTRATE` (byte-locked 4-way) tracked-dirty diff'i secret-scan ETMİYOR (yalnız untracked REQUIRED taranıyor; `git apply` execute-plan:1228-1231 vs `_css_secret_scan` 1233-1238). Dar (committed içerik zaten in-scope; yalnız tracked-dosyada-uncommitted-secret) ama düzeltmeli. Detay + structured fix: security-review **SF1** (`docs/security-reviews/2026-06-04-codex-review-scope-contract.md`). Kapsam: substrate bloğu (4 dosya) + `codex-scan-substrate-harness.sh` tracked-secret fixture.

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

- **sector-packages-mandatory-split** (proposed, kod sağlığı; TETİKLİ) —
  `social/backend/app/services/sector_packages.py` 1804 satır ve zorunlu bölme eşiğinin
  üstünde. **Ayrım noktası ÖLÇÜLDÜ:** yaşam döngüsü bölümü (`LifecycleError`'dan
  `deactivate_package`'a, ~490 satır) tek yönlü bağımlıdır — dosyanın üst kısmındaki hiçbir
  şey o adlara atıf yapmıyor (`head -1295 | grep` ile ölçüldü, çıktı boş). Geri kalan gövde
  çift yönlü bağlı: doğrulayıcı ileri, basım geri atıf yapıyor; onu bölmek üçüncü bir
  "ortak ilkeller" modülü ister, yani yapı değil dağılma olurdu. Üretim tarafında dosya dışı
  çağıran YOK; üç test dosyası yaşam döngüsü adlarını içe aktarıyor.
  **Neden şimdi yapılmadı (Eray, 2026-08-26):** 490 satırlık taşıma, hemen ardından gelecek
  iki review komutunun önüne büyük ve gürültülü bir değişim koyar; hakemler asıl işi değil
  taşımayı okur. **Dürüst etiket: çözülmedi + park edildi.** Basitleştirme turunun hakemi
  bunu ayrı bir orta bulgu olarak işaretledi ("tetik ev değildir") — bu madde o bulgunun evi.
  **Tetik: review zinciri (`/review-claude-codex` → `/security-review-claude-codex`) bittikten
  sonra, dal kapanışından ÖNCE.**

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

