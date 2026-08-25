---
title: Sektör Bilgi Paketi — Runtime Çekirdek Uygulaması
status: active
started: 2026-07-12
last-touched: 2026-08-25
blocked-by: null
source_plan: docs/plans/2026-08-23-sektor-bilgi-paketi.md
---

# Goal

Onaylı plana göre sektör bilgi paketi runtime çekirdeğini kurmak: Tier-1 hiyerarşi satırı +
K6 byte-exact golden kapısı (Faz 0), migration 032 + taksonomi korumaları (Faz 1), tek-kapı
enjeksiyon + K7 damga + preview (Faz 2), atama akışı (Faz 3), elle kuyumculuk pilotu (Faz 4).
Başarı ölçütü: spec §15 kriterleri — özellikle paketsiz markada prompt'ların bit-değişmezliği
(K6) ve pilotta kör değerlendirmede sektörel ayrışma.

# References

- Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md` (`spec-approved`)
- Plan: `docs/plans/2026-08-23-sektor-bilgi-paketi.md` (Plan 1/2 runtime çekirdeği, `plan-approved`)
- Review: `docs/reviews/codex/2026-08-23-sektor-bilgi-paketi-plan.md` (7 tur; approved)
- Superseded: `docs/specs/2026-07-11-...` + `docs/plans/2026-07-12-...` (2026-08-23 Eray kararı)

# Execution State

- execute_mode: subagent-driven
- execute_started: 2026-08-24 07:05
- execute_start_ref: 5a9d5d4220d0a58db84dc23f274199491d91216b
- ledger_window_ref: 5a9d5d4220d0a58db84dc23f274199491d91216b
- execute_review_log: /root/.claude/logs/otomaix--ffc87809/2026-08-24-feat-sektor-bilgi-paketi-execute.md
- execute_branch: feat/sektor-bilgi-paketi
- last_checkpoint_ref: 926e7c6865b147c298b347948b0eeaba9e6c81ee
- cp_count: 13
  <!-- Checkpoint 13: üç tur; tur 3 `approve`, bulgu YOK -> §8.6 Clean dalı.
       Tur 1: iki high + bir medium. Tur 2: üçü de kapalı doğrulandı, bir YENİ
       high (F4) çıktı ve o da düzeltmenin KENDİ yan etkisiydi (serileştirme
       çapasını sektör satırına taşımak yeni bir pencere açtı). Tur 3: F4 kapalı,
       bulgu yok. Medium advisory SAYILMADI — sıra bağımlılığını bu parti getirdi.
       Ayrıntı: Codex defteri, 2026-08-25 12:29 / 12:45 / 12:56 çağrıları.
       Checkpoint 12: beş tur; tur 3'ten itibaren `approve`. §8.6 3. dal
       (Accepted-risk devamı) ateşlendi — kalan tek medium önceden var olan
       bir borçtur ve evi CURRENT.md'dedir. Ayrıntı: Codex defterindeki
       "Checkpoint 12 disposition".
       Checkpoint 11 iki oturuma yayıldı: on birinci oturumda dört tur koştu ve
       APPROVE ALMADI, bu yüzden ref checkpoint 10'da bırakılmıştı. On ikinci
       oturumda tur 5 (yeni kök neden: model-patlaması yedek dalı) ve tur 6
       (approve, bulgu yok) koştu; §8.6 Clean dalı ateşlendi ve ref/sayaç
       birlikte ilerledi. -->

# Current Status

**2026-08-25 (on ikinci oturum, ikinci yarı) — TASK 12 BİTTİ, CHECKPOINT 12 KAPANDI.**
Beş tur; tur 3'ten itibaren `approve`. Tur 1'in dört high bulgusunun dördü de bağımsız
sondajla doğrulandı ve düzeltildi. `pytest tests/ -q` → **405 passed**; donmuş prompt +
migration kapıları → **131 passed**; `npx next build` → exit=0. Çalışma alanı temiz, push YOK.

**Task 12 bitti:** damga tüketimi (atomik, tek kullanımlık) iki kalıcı-kayıt ucunda da
bağlandı; `social.package_events` + `log_package_event` kuruldu; Task 8-11'in geçici
logları kalıcı olaya bağlandı; istemci makbuzu caption yanıtından iki isteğe de taşıyor.

**Turların anlattığı hikâye — iki kez aynı ders.** İlk düzeltmelerimin İKİSİ de (F3, F4)
varyantı kapatıp sınıfı açık bıraktı: F3'te elle kurduğum indeks imzası eksikti (aynı adda
UNIQUE bir indeks kapıdan geçiyordu — ölçüldü), F4'te sırayı kaydırdım ama geçişi atomik
yapmadım. İkisi de ikinci turda TAM ölçüye bağlanarak kapandı: `pg_get_indexdef` (kanonik
tanımın tamamı) ve tek transaction'da onaya-açılma + damga.

**Medium'lar advisory sayılmadı — çünkü bu partinin kendi gerilemeleriydi.** M1 (süpürücü
kararını geri alma) ve M2'nin tur-4 varyantı (geç webhook başarısı arayüze ulaşmıyor)
düzeltildi; M1 için pozitif kontrol koşuldu (kapı kaldırılınca test düşüyor).

**M2 residual KABUL EDİLEN RİSK ve gerekçesi ÖLÇÜLDÜ.** Üç turda üç varyant geldi; ortak
yan, istemcide cevaplanamayan bir soruyu ("bu satır daha değişecek mi") yüklemle çözmeye
çalışmaktı. Altıncı yama açılmadı. Ölçüldü ki sınırsız yoklama bu partinin ürünü DEĞİL:
`0c19d83` sürümünde de terminal başarısız satır sonsuza kadar yoklanıyordu (üstelik kart
yanlış durum gösteriyordu). Yük aynı, görünürlük arttı. Gerçek çözüm arka uçtan türetilmiş
bir uzlaştırma sinyalidir ve o, Eray'ın park ettiği ürün kararının içindedir.

**2026-08-25 (on ikinci oturum) — CHECKPOINT 11 KAPANDI (approve, bulgu yok). Devralınan tek
açık kapı kapatıldı; Task 1–11 bitti, sıradaki Task 12.**
`pytest tests/ -q` → **345 passed** (oturum başında 296). Donmuş prompt kapısı → **121 passed**
(oturum başında 72; devralınan HANDOFF 71 diyordu — son düzeltme bir test daha eklemişti).
Çalışma alanı temiz, **push YOK**.

**F3 beşinci kez geldi ve BAŞKA bir eksendeydi.** Önceki dört tur tek bir yüklem etrafında
dönüyordu ("kalıp zaten var mı") ve o yüklem tur 4'te silinerek kapanmıştı. Tur 5'in kök nedeni
bozulmuş bağımlılık yoluydu: Anthropic çağrısı patladığında `_build_still_prompt` yalnız
marka/sektör/renk taşıyan genel bir yedek metin üretiyor, havuz hiç girmiyordu — ölçüldü,
`_resolve_still_prompt`'un dört dalının DÖRDÜNDE de. Video başarıyla üretiliyor, paketli marka
sektörel sinyalini sessizce kaybediyordu.

**Düzeltme (`0c19d83`) sınıf düzeyinde kuruldu.** Kural: model çağrısı YAPMAYAN her durağan-kare
yolu havuzdan bir kalıp ekler; model çağrısı YAPAN her yol havuzu bağlamda taşır. Bu iki küme
çıkışların TAMAMIDIR (hakem de aynı sayımı bağımsız yaptı). Kapanış elle seçilmiş örnekle değil
ÜRETİLMİŞ matrisle kanıtlandı: mod × kullanıcı isteği × istem dili (12 dal) × model
ayakta/düşük = 24 hücre, hem paketli hem paketsiz tarafta. Düzeltmeden önce 12 model-düşük
hücrenin 11'i kırmızıydı (12.'si zaten zenginleştirme yolundan geçen İngilizce dalı).

**Süreç dersi (Eray itirazı, kayda değer).** Beş tur aynı maddenin beş kez açılması DEĞİL, aynı
sözün beş ayrı çıkıştan delinmesiydi; ama beş tura çıkması hakemin değil yürütmenin hatasıdır.
Her turda bulunan delik yamandı, "bu sözün kaç çıkışı var, hepsini say" sorusu beşinci tura
kadar sorulmadı. Hakem delta bakar — tam haritayı çıkarmak yürütmenin işidir. Turlar daralarak
geliyorsa yamalamayı bırakıp çıkış uzayını saymak KURAL hâline getirildi.

**2026-08-24 (on birinci oturum) — PLAN 1 YÜRÜTME AÇIK; Task 10 ve 11 yazıldı, Task 8 revize
edildi, K-02 ve K-113 KAPANDI. Checkpoint 11 KAPANMADI.**
`pytest tests/ -q` → **296 passed** (oturum başında 232). Donmuş prompt kapısı → **71 passed**.
`npx next build` → geçti (bu daldaki ilk frontend derlemesi). Çalışma alanı temiz, **push YOK**.

**Task 10 bitti (tek-kapı enjeksiyon — caption + fikir önerme).** Paket bloğu kök sektör
rehberinin yerine geçiyor; özel günde dönem kalıpları mevcut bloğun içine giriyor; CTA'lar Task
9'un kanal filtresinden geçiyor; paketli üretim opak `generation_id` döndürüyor.
**Checkpoint 10: iki tur, approve.** Tur 1'de üç high + bir medium; dördü de sondajla doğrulandı.
İkisi benim kendi hatamdı ve ikisi de ancak yol/güven sınırına bakınca görünüyordu: (a) damga
yardımcısını dekoratör ile işleyicinin ARASINA koymuşum, FastAPI rotayı ona bağlamış, caption ucu
HTTP'den erişilemez hâle gelmişti; (b) damga, paketin ÇÖZÜLMÜŞ olmasına bakıyordu, dönen içeriğin
o paketle üretildiğine değil — model patlayınca yedek çıktı paket damgası alıyordu (sahte soyağacı).

**Spec eksikliği kapatıldı (Eray talebi).** Spec, spec-input'tan yazılırken K-02'nin **öneri ·
sahip · çözüm yolu** ayaklarını düşürmüş, **K-113'ü hiç taşımamıştı**. İki commit bunu yalnız
EKLEYEREK kapattı (108 satır eklendi, **0 satır silindi** — `git diff --stat` ile doğrulandı);
her blok `[SONRADAN EKLENDİ]` etiketi taşıyor. Bu, yürütmenin Task 11'de tam olarak neden
durduğunu da açıklıyor: "iki alt yapıdan hangisi sahne" sorusunun yazılı cevabı yoktu.

**K-02 = A ve K-113 = A KAPANDI (Eray onayı).** Hareket dili paketin sektörel havuzundan gelir;
seçimi caption aşamasındaki MEVCUT model çağrısı yapar (ölçüldü: kısa video ucu script'siz istek
kabul etmiyor, yani o çağrı zaten zorunlu → ek çağrı doğmuyor); istemciden dönen değer sunucuda
havuz üyeliğine karşı doğrulanır; havuz boşsa bugünkü listeye düşülür. Alan adları bağlandı
(`video_kodlar.hareket` · `.sahne`), **ikisi de LİSTE**.

**Task 8 revize edildi.** Yazdığım kapı `video_kodlar`'ın parçalarını tek cümle sanıyordu ve
adları serbest bırakıyordu; ölçüldü, alternatif taşıyan meşru bir paket yazılamıyordu. Kapı artık
adlı ve çoğul sözleşmeyi zorluyor.

**Task 11 yazıldı ama CHECKPOINT 11 KAPANMADI.** Görsel dil, sahne havuzu (iki modda da) ve
hareket havuzu bağlandı; legacy uç bilinçle bağlanmadı (K-06). **Dört tur koşuldu; F1 ve F2
kapandı, F3 dört kez geri geldi ve son düzeltmesi HAKEMDEN GEÇMEDİ** (ayrıntı Open Problems).

**Önceki durum (2026-08-24, onuncu oturum) — 16 task'ın 9'u bitti.**
Bu oturumda YALNIZ Task 9 (kanal envanteri) yürütüldü — ama checkpoint'i altı tura yayıldı.
`pytest tests/ -q` → **232 passed** (oturum başında 185). Donmuş prompt kapısı → **25 passed**.
Çalışma alanı temiz, **push YOK**. Devralınan açık kapı YOKTU; bu oturum da açık kapı DEVRETMİYOR.

**Task 9 bitti (kanal envanteri + deterministik CTA filtresi).** `[kanal-bağımlı: X]` etiketli
CTA kalıpları markanın envanterine karşı deterministik olarak eleniyor; envanter yok/boş/bozuk
ya da değer tam `True` değilse kalıp ATLANIYOR (spec §12.2 muhafazakârlık hükmü). Anahtar uzayı
kapalı ve kapalılık, çağıranın kit içeriği verebildiği HER yüzeyde zorlanıyor — yüzey kümesinin
tamlığı yapısal (AST) taramayla ölçülüyor.

**Checkpoint 9: ALTI TUR, tavan-aşımı (Eray oturum başında izin verdi; audit `ceiling-exceed`).**
Yedi bulgunun yedisi de bağımsız sondajla DOĞRULANDI — hiçbiri sondaj koşmadan kabul veya
reddedilmedi. Beşi high, ikisi medium.

**Turların anlattığı asıl hikâye: yamalama üç tur boyunca yakınsamadı.** Bulgular tek eksende
daralarak geldi — tipografik/görünmez karakter (tur 1) → eksik ayıraç (tur 2) → ayırıcı sınıfı
(tur 3) → yanlış yazılmış bayrak adı (tur 4). Kök sebep her turda aynıydı: kapı serbest metinden
*"bu bir etiket DEĞİLDİR"* i kanıtlamaya çalışıyordu. Bu tür bir kapı yakınsamaz; her tur ya bir
bypass ya bir yanlış-pozitif üretir. Tur 3 ve tur 4'te döngü sınıf-teşhisiyle DURDURULDU ve Eray'a
soruldu (bkz. Decisions Log).

**Çözüm tahminden KAPSAMAYA taşındı ve dayanağı spec'ten TÜRETİLDİ, uydurulmadı.** §8.4 bayrak
kümesini "sekiz bayrak, kapalı" diye bağlıyor ama sekizini saymıyor; §8.5 eksik parçayı veriyor —
sekizin YEDİSİ sentez sırasında tüketilir, yalnız kanal bayrağı "etiketiyle taşınır"; §3.4 aynı
hükmü alan tablosunda tekrarlıyor. Yani paket İÇERİĞİNDE geçebilecek bayrak kümesi tek kalemlik.
Kural: CTA öğesi içindeki her köşeli ayraç kanal bayrağının kurallı biçimi olmak zorunda. Yanlış
yazım, birleşik yazım, eksik/iç içe ayraç, sentezde tüketilmesi gereken bir bayrağın sızması —
hepsi TEK kuralla düşüyor. Açık bir K-ID kapatılmadı.

**Tur 5 iki YENİ sınıf getirdi ve ikisi de benim düzeltmelerimin yan etkisiydi.** (a) Birleştirmeyi
sunucuya taşırken çift kodlanmış kit satırının ele alınmasını düşürmüşüm: ölçüldü, tek alanlık bir
güncelleme mevcut TÜM kit alanlarını siliyordu. (b) Ayraç kuralını içeriğin tamamına uygulamıştım:
görsel yönergedeki zararsız bir notasyon paketin TAMAMINI devre dışı bırakıyordu. İkisi de
düzeltildi. **Ders: düzeltmenin kendi yan etkisini ölçmek düzeltmenin parçasıdır.**

**Eşzamanlılık sınıfı da kapandı.** `brand_kit` artık hiçbir yolda okunup geri yazılmıyor;
üç yazıcı da tek bir sunucu-taraflı birleştirme ifadesinden geçiyor. Ölçüldü: düzeltmeden önce
dört eşzamanlı yazımın ÜÇÜ kayboluyordu.

**İnceleme bütçesi bu oturumda TÜKENDİ.** Altı tur koşuldu (tavan 8, en az 3'ü finale rezerve);
tur 6 Eray kararıyla rezervden fonlandı. Task 10 ara inceleme olmadan yürütülmemeli — bütçe
oturum başına sıfırlandığı için TAZE OTURUM gerekiyor.

**Önceki durum (2026-08-24, dokuzuncu oturum) — 16 task'ın 8'i bitti (planın yarısı).**
Bu oturumda Task 7 ve Task 8 yürütüldü (inline; review/checkpoint kapıları normal koştu).
`pytest tests/ -q` → **185 passed**. Türetilmiş defter rc=0, çalışma alanı temiz, **push YOK**.
Devralınan açık kapı YOKTU ve bu oturum da açık kapı DEVRETMİYOR.

**Task 7 bitti — KATMAN-1 FREEZE KAPISI KAPALI.** Dokuz fixture donduruldu: durağan kare tam
matriste (metinden-görsele / ürün-edit × ürünlü / ürünsüz — dördü de, çünkü ürün odak bloğu
ikisinin "veya"sından çıkıyor), script istemi rehberli ve rehbersiz, kamera hareketi havuzu içerik
ve sıra olarak. Legacy uç KENDİ router yolundan donduruldu: sektör rehberini marka satırının
görünen adıyla ("Teknoloji") slug anahtarlı tabloda arıyor, yani rehber her markada boş — bozukluk
düzeltilmedi, K-06'nın istediği gibi aynen donduruldu. Yalnız dış dünya (ElevenLabs, fal.ai)
kesildi. Ölçülen yan gerçek: `generate_script`'e bugün hiçbir üretim çağrısı dolu sektör rehberi
geçmiyor (`/ai/generate-script` parametreyi hiç geçmiyor). Caption/fikir yüzeyleri ayrı, slug'ı
doğru kullanan yoldan rehberi alıyor.

Harness Task 7'nin ilk adımında fail-closed yapıldı (devralınan öneri): kayıpsız temsil
edilemeyen girdi artık REDDEDİLİYOR. Task 6'nın dört fixture'ı bayt-aynı kaldı — mevcut kanıt
bozulmadı.

**Checkpoint 7: tek tur `approve`, kritik/yüksek YOK.** İki orta bulgu `accepted_risk`
YAZILMADI, FIX edildi (gerekçe review log'unda): biri commit mesajındaki bir iddiayı çürütüyordu,
ikisi de dakikalar önce yazılmış test kodundaydı. Re-review turu açılmadı.

**Task 8 bitti (paket erişim katmanı).** `sector_packages.py`: tek normalize modülü (K-01b),
içerik doğrulayıcı (yazımdan önceki kapı — REDDEDER), paket çözümleyici (çalışma zamanı — asla
reddetmez, `None` + log ile düşer). Bilinçle kapı YAPILMAYAN iki şey: ~6.000 karakter tavanı
UYARI (ölçülmemiş tasarım hedefi, İlke 9) ve `video_kodlar` alan adları serbest (K-02 açık —
yalnız iki-alt-yapı sayısı bağlandı). K-15(a) alan-düzeyi atlama dalı bilinçle YOK.

**Checkpoint 8: DÖRT TUR, tur 4'te `approve`.** Tur 1 üç yüksek + bir orta verdi; dördü de
bağımsız sondajla doğrulandı (kabul edilmedi, ölçüldü): yazım kapısı kabın tipine bakıp geçiyordu
(`[None]`, `["   "]`, `{"a": False}` kabul ediliyordu), çözümleyici `content={}` dâhil her sözlüğü
geçerli sayıyordu, marka adı taraması Türkçe'ye kördü. Tur 2 iki yeni şey getirdi: F3 kapanmamıştı
ve **F5 — önceki commit mesajımdaki "bağlam kurulumu emniyet sınırına taşındı" iddiası YANLIŞTI**
(taşınmamıştı; düzeltildi ve commit'te açıkça yazıldı).

**Tur 3'ün süreç kararı (kayda değer).** F3'te üç tur üst üste aynı eksenin daha dar bir varyantı
geldi: Türkçe büyük harf → ayrışık Unicode → `İ`.lower()'ın ürettiği görünmez birleşen işaret.
Dördüncü nokta yaması yerine SINIF kapatıldı — katlama artık tüm birleşen işaretleri atarak
bitiyor. Kanıt da biçim değiştirdi: elle seçilmiş örnek yerine ÜRETİLMİŞ MATRİS (8 marka × tüm
yazımlar = 277 çift, kaçan 0). Elle seçilmiş örnekler zaten üç turdur deliği açık tutan şeydi.

**Mutasyon disiplini.** 23 kabul dalı tek tek devre dışı bırakıldı; ilk taramada üç dalın bekçisi
yoktu ve Codex bunu orta bulgu olarak yakaladı — haklıydı, taramam yardımcı-fonksiyon düzeyindeydi,
dal düzeyinde değil. Şimdi hepsinin bekçisi var.

**`cp_count` = 8 = TAVAN.** Sıradaki riskli task (Task 9) tavan-aşımı kararına düşecek; Eray bu
oturumda review'lara ve tavan aşımına açık izin verdi.

**Önceki durum (2026-08-24, sekizinci oturum) — PLAN 1 YÜRÜTME AÇIK; 16 task'ın 6'sı bitti.**
Bu oturumda Task 5 ve Task 6 yürütüldü (inline; review/checkpoint kapıları normal koştu).
`pytest tests/ -q` → **78 passed**. Türetilmiş defter rc=0, çalışma alanı temiz, **push YOK**.

**Task 4'ün devralınan açık kapısı KAPANDI.** Oturum, geçen oturumdan doğrulanmamış devralınan
`afc8daf` (fail-closed taksonomi kapısı) ile başladı. Checkpoint 5'in ilk turu onu kapanış turu
titizliğiyle inceledi ve KAPALI buldu: çözümleyicinin her çağıranı taranmış, `create_brand` ve
`update_brand` yazımdan önce istisnayı bekliyor ve yutmuyor, `resolve_sector_id` aynı kapıya
bağlanıyor. Devralınan tek borç buydu.

**Task 5 bitti (veri/API regresyon kümesi + marka kök-sektör tam sweep).** Dört regresyon testi
bugünkü invariantı pinliyor: alt sektör satırı eklemek `GET /sectors` çıktısını ve HİÇBİR markanın
kök sektörünü değiştirmiyor (TAM sweep — örneklem değil), hiçbir üretim yolu damga kolonu yazmıyor
(yedi `INSERT INTO social.posts` noktasının hepsi yapısal olarak tarandı). `scripts/sector_sweep.py`
canlıda da koşulabilen salt-okunur operasyonel sweep.

**Checkpoint 5: BEŞ TUR, `approve` ALINMADAN kullanıcı kararıyla kapatıldı (override).** Bulgu
kümesi tek bir eksene oturdu — sweep'in taban dosyasına ne kadar güvenebileceği — ve her tur bir
öncekinden dar bir varyant açtı: (1) rapor yalnız "kök bağlı mı" diyordu, kökten köke kayma
görünmüyordu; (2) yarıda kesilmiş taban eksik markaları ihlal-olmayan `added` sayıyordu;
(3) taban hangi veritabanından geldiğini taşımıyordu; (4) veritabanı-içi kimliği fiziksel kopya
aynen taşıyor; (5) bağlantı ucu METİNDEN okunuyordu, oysa asyncpg `PGPORT`/`?host=` yollarını da
dikkate alır. **Beşinin beşi de düzeltildi ve beşi de pozitif kontrollü.** Rapor artık tam eşleme
listesi taşıyor, `--baseline` çift çift karşılaştırıyor, taban kendi beyanına karşı doğrulanıyor,
kimlik hem kanonik bağlantı dizesinden hem sunucunun KENDİ bildirdiği uçtan besleniyor, belirsiz
dize bağlanmadan reddediliyor, yakalanmayan istisna rc=2 veriyor (rc=1 "fark bulundu" demek —
karışırdı) ve parola hiçbir akışa sızmıyor (ölçüldü).

İki öneri BİLİNÇLİ REDDEDİLDİ, gerekçesi script'in kendi belgesinde yazılı: (a) tabanın geçmişte
doğru olduğunu kanıtlayan imzalı özet — taban geçmiş bir durumdur, araç geçmişi doğrulayamaz;
imzasız özet yalnız kazara kesilmeyi yakalar, onu da satır sayısı zaten yakalıyor; (b) dışarıdan
sağlanan kimlik — provisioning hikâyesi ister, bağlantı ucu aynı girdiyi bedava kapatıyor.
Kalıntı ve yeniden açılma koşulu (taban dosyaları güvenilmeyen bir kanaldan taşınırsa) modül
belgesinde. Override audit satırı execute review log'unda.

**Task 6 bitti (Katman-1 yakalama altyapısı + caption/fikir fixture'ları).** `capture.py` Claude'a
giden çağrıyı kesip TAM prompt'u (model + sistem blokları + mesaj blokları + önbellek sınırları)
deterministik metne çeviriyor. Test kendi prompt'unu KURMUYOR — üretimin kendi kod yolu koşuyor,
yalnız ağ ucu kesiliyor. Dört fixture donduruldu: tekli caption (özel günlü/günsüz), carousel dalı
(K-15b), fikir yüzeyi. Dondurma yalnız `PROMPT_REGRESSION_UPDATE=1` ile yapılıyor; bayraksız
koşumda kırmızı test kendini yeşile boyayamıyor. İki sessiz-yeşil tuzağı kapatıldı: caption yolu
anahtar yoksa, fikir yolu HER istisnada sessizce fallback'e düşüyor — ikisinde de "çağrı gerçekten
yapıldı mı" ayrıca doğrulanıyor. Fixture'lar gözle incelendi: paket izi YOK, sektör rehberi
dördünde de basılı (paketin ileride yerine geçeceği blok), üç katmanlı önbellek sınırı görünür,
özel gün varyantı yalnız kendi bloğuyla ayrışıyor.

**Checkpoint 6 koştu → `verdict: approve`, kritik/yüksek bulgu YOK.** İki orta bulgu
`accepted_risk` (HANDOFF Risks). Codex ayrıca harness'ın her iki üretim import biçimini de
gerçekten yakaladığını ve tam-bir-çağrı iddiasının sessiz fallback'i imkânsız kıldığını doğruladı.

**Süreç notu (kayda değer).** Checkpoint 5 tek bir dosyada beş tur döndü ve kullanıcı haklı olarak
"daha kaç review gerekecek" diye sordu. Dördüncü turda tavan kuralı gereği durup rapor edildi, ama
"ucuz kapanış" önerisiyle döngü bir tur daha uzatıldı — o öneri geri görüşte hatalıydı. Ders:
tavanda DURMAK kuralın kendisidir, ucuz düzeltme varlığı onu geçersiz kılmaz.

**Önceki durum (2026-08-24, yedinci oturum) — 16 task'ın 3'ü bitti (Task 3 + Task 4).**
Ayrıntı: Task 3 migration dağıtım/geri alma/atomiklik, Task 4 kök kova korumaları; checkpoint 3
dört turda `approve`, checkpoint 4 tek tur `needs-attention` + kapanış turu açılamadı (bu oturumda
kapandı). `Exec-Kind` etiket düzeltmesi için geçmiş yeniden yazıldı (`backup/pre-t3-kind-fix`).

**Önceki durum (2026-08-24, altıncı oturum) — 16 task'ın 2'si bitti.**
`/execute-plan-claude-codex` başlatıldı: dal `feat/sektor-bilgi-paketi`, mod
subagent-driven, `execute_start_ref = 5a9d5d4`. Task 1 (pytest altyapısı +
atılabilir `otomaix_test` veritabanı) ve Task 2 (migration 032) bitti; 39 test
PASS. İki checkpoint koştu, ikisi de `verdict: approve` ile kapandı: checkpoint 1'de
bir yüksek bulgu (yıkıcı test-DB işlemi yalnız veritabanı ADINI doğruluyordu, sunucu
ucunu değil) tek turda, checkpoint 2'de bir yüksek bulgu (migration idempotentliği
isim-eşitliğine dayanıyordu → garanti sessizce eksik kalabilirdi) üç turda kapandı.
Beş orta/düşük bulgu `accepted_risk` olarak kayıtlı (HANDOFF Risks). Bir footer
etiketi hatası defteri kırmıştı; Eray onayıyla geçmiş yeniden yazılarak düzeltildi
(içerik bayt-aynı, emniyet etiketi `backup/pre-footer-fix`). **9 commit local,
push YOK.** Sıradaki iş: Task 3.

**Önceki durum (2026-08-24, beşinci oturum) — PLAN 1 ONAYLANDI (`plan-approved`, Tur 7 `verdict: approve`).**
Eray yol seçimi: "sadeleştir + fix" — F23 kaldırmayla kapandı (recovered bandı + K-45
geri-dönüş teslimi Plan 2'ye; atama-geçmişi kanıtı Plan 2 kalemi; metin/karar korunur),
F22 (olay-türüne özgü sürüm şekilleri) + F24 (geçiş+olay tek transaction) mekanik fix.
Tur 7 kapanış-doğrulaması: F22/F23/F24 CONFIRMED, yeni bulgu YOK. 24/24 bulgu kapalı
(23 fix/devir + F17 Eray risk-kabulü). EXECUTE-NOTES kozmetikleri uygulandı. Repo
HİS-özet review log yazıldı (`docs/reviews/codex/2026-08-23-sektor-bilgi-paketi-plan.md`).
Commit onayı Eray'da; sonrası `/execute-plan-claude-codex`.

**Önceki durum (2026-08-23, dördüncü oturum):** Plan 1 yazıldı, 6 Codex review turu
koştu; 3 açık high bulgu + YOL SEÇİMİ Eray kararı bekliyordu; oturum Eray talebiyle o
noktada kapatıldı. Kapsam kararı: 2 planlı staged split (Eray) — Plan 1 = runtime çekirdeği
(bu oturumda yazıldı: `docs/plans/2026-08-23-sektor-bilgi-paketi.md`, 16 task,
status `plan-draft`, **COMMIT EDİLMEDİ — working tree'de untracked**), Plan 2 =
işletim hattı (hat/motor/komut ailesi/pilot; açık K-84 ailesi kapanınca).
Review: 24 bulgu (F1-F24), 21'i kapandı (19 fix+CONFIRMED · F17 Eray risk-kabulü:
damga = edited-lineage atfı · F20/F21 tur-6 CONFIRMED). **Açık: F22 (yaşam-döngüsü
olay şekilleri sınır durumları) · F23 (recovered bandı atama-geçmişi kanıtı) ·
F24 (geçiş+olay atomikliği)** — üçünün de Codex yapılandırılmış çözümü review
log'unda. Sıradaki adım SEÇİM: (1) sadeleştir+fix (geri-dönüş bandı Plan 2'ye →
F23 yok olur; önerilen) / (2) üçünü düzelt / (3) durdur — Eray henüz SEÇMEDİ;
yeni oturum bu sorudan başlar. Süreç notu: oturum sonunda belirsiz-mesajı onay
sayma ihlali yaşandı (Eray yakaladı; plan dosyasına dokunulmadan durduruldu).

**Önceki durum (üçüncü oturum):** Kayıt üçlemesi: liste Durum sütunu dolu +
spec K-ID satırları "KAPANDI" statüsünde (kardeş-site sweep'li) + Decisions Log
altında tam döküm. Öneriden farklı 3 karar: K-71 (açık sorular aktivasyonu BLOKLAR),
K-45 (çift yönlü bakım bildirimi — Faz 1'e bildirim mekanizması iş kalemi eklendi),
K-56 (olay-bazlı anında uyarı — eşik değil). K-26 genişlemeli kapandı (vade
bildirimi eklendi). **Spec ONAYLANDI (Eray, aynı oturum)** — frontmatter
`spec-approved`. **Üçüncü oturum (aynı gün): sentez deposu sweep borcu kapsam
daraltmasıyla kapatıldı** — tam geriye dönük sweep İPTAL (Eray), yerine kaynak
belgeye statü notu + snapshot yeniden eşitleme. Sırada: `/write-plan-claude-codex`
ile sıfırdan plan.

**Önceki durum (aynı gün, ilk oturum):** Spec yazıldı, Codex review 3 tur SHIP
(11+1 bulgu çözüldü; log: `docs/reviews/codex/2026-08-23-sektor-bilgi-paketi-spec.md`).
Eski spec/plan superseded. Spec: `docs/specs/2026-08-21-sektor-bilgi-paketi.md`
(status: reviewed-pending-user-approval).

**2026-08-21 güncellemesi:** İki hakem mimari belgesinin sentezi tamamlandı ve kanonik girdi
snapshot olarak alındı (`docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md`).
**Aynı gün ikinci oturum:** sentez commit'lerinin Codex denetimi koşuldu (4 bulgu: 2 yüksek,
2 orta); iki yüksek bulgu (bayat karar statüleri + K-05 kapsam tersliği) 4 commit'lik gövde
sweep'iyle giderildi ve 4 turlu Codex kapanış-doğrulaması **CONFIRMED** ile kapandı; snapshot
yeni kaynak commit `c380e37` üzerinden yeniden alındı (bayt-özdeşlik sha ile doğrulandı).
**Sıradaki iş: yeni spec'in yazımı** (`docs/specs/2026-08-21-sektor-bilgi-paketi.md`) —
seans sırası ve yöntem HANDOFF.md'de. Eski spec/plan sentezden habersizdir; ilişkileri
(devralma / supersede) spec seansında netleşecek, durum geçişi Eray'ındır.

# Open Problems

- **[AÇIK KALEM — evi VAR, tetiği Eray verdi] Süpürücünün "başarısız"ı ile webhook'un
  "hazır"ı çelişiyor.** Süpürücü `generating`i 10 dakikada `failed` yapıyor; `fal_webhook`
  tek görsel/video satırını `fal_job_id` ile bulup durum kapısı OLMADAN sonradan `ready`
  yazabiliyor. Arka uçta `failed` TERMİNAL DEĞİL. **10 dakikanın ölçülmüş dayanağı yok** —
  vault kararı gerekçeyi "webhook kaybı güvenlik ağı" diye yazıyor, model süresi ölçümüne
  ya da sağlayıcı belgesine dayanmıyor (kayıt `verification-status: unverified`).
  Bu oturumda YALNIZ arayüz arka uçla tutarlı hâle getirildi (`532825e`); sözleşme
  ÇÖZÜLMEDİ. **Dürüst etiket: çözülmedi + evi var.**
  Ev: `docs/active/CURRENT.md` → `stale-sweeper-vs-late-webhook-terminality`.
  **Tetik (Eray, 2026-08-25): sektör bilgi paketi işi TAMAMEN bittikten sonra** — fal.ai
  model değişikliği de o döneme planlı, eşik gerçek model süreleriyle birlikte ölçülmeli.
  Kapsam dışı olduğu için Task 12'de çözülmedi; `/finish-branch-claude-codex` kapanışında
  yeniden görünür kılınmalı.

- **[DÜZELTME — kayda geçiyor] `76b4a15` commit mesajında ölçülmemiş bir iddia var.**
  Mesaj "çöken bir stage-1 eskiden hayalet bir `awaiting_approval` olarak kalırdı" diyor.
  YANLIŞ: süpürücü `awaiting_approval`ı zaten 2 saatte topluyordu (`internal.py` okundu).
  Gerçek fark 2 saat → 10 dakika. Commit geçmişi yeniden yazılmadı çünkü inceleme tabanı
  kayardı; düzeltme burada ve `T12-fix3` mesajında yaşıyor.

- **[KAPANDI 2026-08-25] Task 11'in checkpoint'i kapandı.** Devralınan açık kapı buydu.
  Tur 5 yeni bir kök neden buldu (model-patlaması yedek dalı havuzu taşımıyordu — bağımsız
  sondajla doğrulandı, dört dalın dördünde), `0c19d83` ile sınıf düzeyinde kapatıldı; tur 6
  `approve`, bulgu yok. §8.6 Clean dalı ateşlendi, `last_checkpoint_ref` + `cp_count` birlikte
  ilerledi. F1 ve F2 zaten tur 2'de kapalı doğrulanmıştı.

- **[Ders — kayda değer, borç DEĞİL] Bu eksende BEŞ tur, beş kök neden.** Son üçünün ortak yanı:
  serbest metinden *"bu zaten yeterli mi / bu girdi güvenilir mi"* sorusunu cevaplamaya çalışan bir
  yüklem. Böyle bir yüklem yakınsamıyor; her tur bir öncekinden dar bir vaka açıyor. Çıkış her
  seferinde yüklemi silmek ya da tek ortak ölçüye bağlamak oldu. Yeni oturumda aynı desen görülürse
  (turlar daralarak geliyorsa) yamalamayı bırakıp sınıfı kapatmak gerekir.


- **CTA öğesi içinde serbest köşeli ayraç kullanılamaz (Plan 2'ye teslim edilen içerik kısıtı,
  checkpoint 9).** Kanal bayrağının bozuk yazımını kapatan kural, CTA öğesindeki HER ayracı bayrak
  sayar; dolayısıyla `[bkz. kaynak 3]` gibi zararsız bir notasyon CTA içinde REDDEDİLİR (CTA
  DIŞINDA serbesttir — ölçüldü). Bu, sentez motorunun çıktı biçimini bağlayan bir içerik kısıtıdır.
  **Dürüst etiket: çözülmedi, bilinçli tercih.** Gerçek evi denetçi/brief sözleşmesidir (spec §8.7
  "resmî tur öncesi zorunlu sözleşme düzeltmeleri" listesi — tarihli kapısı var: resmî tur öncesi).
  Plan 2'ye teslim kalemi olarak Task 16'da doğrulanmalı. Yeniden açılma: motor çıktısı meşru
  şekilde CTA içinde ayraç kullanmak zorunda kalırsa. Codex tur 6'da bunu tekrar açtı; tek yeni
  unsuru ("mevcut satırları süpür") ÖLÇÜLDÜ ve boş çıktı — canlıda `social.sector_packages` tablosu
  henüz YOK.
- **`brand_kit` anahtarı artık silinemez, yalnız üzerine yazılabilir (checkpoint 9, kabul edilen
  risk).** Eşzamanlı yazımda veri kaybını kapatmak için üç yazıcı da sunucu-taraflı birleştirmeye
  geçti; bedeli, tam belge göndererek bir anahtarı düşürme yolunun kapanmasıdır. Ölçüldü: frontend
  bu yüzeyi hiç kullanmıyor ve depoda kit anahtarı silen bir kod yolu YOK. **Dürüst etiket:
  çözülmedi, bedeli bilinçle kabul edildi.** Yeniden açılma: bir kit anahtarını gerçekten silme
  ihtiyacı doğarsa — o zaman sessiz tam-belge yazımı değil, açık ve belgeli bir silme sözleşmesi
  gerekir.

- **Sweep tabanının kökeni — belgeli kalıntı (checkpoint 5, kullanıcı kararıyla kapatıldı).**
  `scripts/sector_sweep.py` tabanı kanonik bağlantı dizesine + küme kimliğine + sunucunun kendi
  bildirdiği uca bağlar. Bunun ötesi (elle düzenlenmiş, sayaçları da güncellenmiş taban; aynı uçta
  duran bir kopya) yalnız imzalı özet veya dışarıdan sağlanan kimlikle kapanır; ikisi de salt-okunur
  bir işletim raporu için orantısız bulundu. Gerekçe + yeniden açılma koşulu (taban dosyaları
  güvenilmeyen bir kanaldan taşınırsa) modül belgesinde YAZILI. Evi: Adım 11 final execution review
  (`checkpoint_overrides` listesi üzerinden yeniden değerlendirilir).
- **On-prem paketi PostgreSQL 16'ya sabitli, migration 032 PG18 istiyor (Eray risk kabulü,
  2026-08-24).** `shared/local-deployment/docker-compose.yml` `pgvector/pgvector:pg16` imajını
  pinliyor; 032'nin fail-closed doğrulama bloğu `pg_constraint.conenforced` okuyor ve bu kolon
  PG16'da YOK (ölçüldü: 16.13 sunucusunda `count(*) = 0`). On-prem `setup.sh` zinciri 032'de
  gürültülü hatayla durur. Canlı sistem PG18, etkilenmiyor. Eray: "canlı sistem test aşamasında,
  önemli değil" → **ÇÖZÜLMEDİ + park edildi**. Yeniden açılma: on-prem paketi gerçekten
  kurulacaksa. Seçenekler: (a) imajı 18'e çek (veri taşıma gerekir), (b) 032 doğrulamasını
  sürüm-duyarlı yap, (c) statü notuyla bırak.
- **Geri alma ile ileri 032 arasında çapraz serileştirme yok (residual, checkpoint 3).**
  `032_down.sql` kendi invariantını kapatıyor, ama ileri koşan bir 032 uygulamasıyla ORTAK kilit
  yok. Tam serileştirme 032'nin de aynı advisory lock'u almasını gerektirir — 032 onaylı bir Task 2
  artefaktı, o task'ın dosya kümesi dışında. Bugünkü hâlde ulaşılabilir veri-kaybı yolu YOK.
  Yeniden açılma: 032 ileri uygulaması ile geri alma aynı anda koşabilecek bir işletim düzeni
  doğarsa (birden çok operatör / otomatik dağıtım). Evi: Task 16 kapanış listesi.
- Spec'in ~45 kapanış metninin bağımsız kapanış-sweep'i Eray kararıyla ATLANDI (2026-08-23) —
  kısmi hafifletme: 6 Codex plan-review turu spec'i tekrar tekrar okudu, K-ID çelişkisi
  raporlamadı. Yeniden açılma: spec kapanış metinlerinden şüphe doğarsa.
- Sentez deposu denetiminin iki orta bulgusu (commit mesajında yanlış K/R-ID sayımı; snapshot
  Ek C'deki etiketsiz "beş prompt yüzeyi" sayısı) **DÜŞÜRÜLDÜ** — evi olan spec seansı tamamlandı.
  Yeniden açılma: arşiv belgesi ileride yeniden canlı girdi olursa.

# Decisions Log

- **2026-08-24 (on birinci oturum) — Spec eksikliğinin kapatılma biçimi (Eray):** spec ve planda
  HİÇBİR ŞEY SİLİNMEYECEK; eksik kayıtlar ilgili maddelerin ALTINA, "eksik yazıldığı için sonradan
  eklendi" notuyla eklenecek. Uygulandı ve mekanik olarak doğrulandı (108 satır eklendi, 0 silindi).

- **2026-08-24 (on birinci oturum) — K-02 = A, seçici modelde (Eray):** hareket dili paketin
  sektörel havuzundan gelir; havuzda birkaç alternatif bulunur; seçimi model yapar.
  **Eray'ın gerekçesi:** tek cümle o sektörün her videosunu aynı tipte üretir; ayrıca "bu video
  mücevher yakın çekimi anlatıyorsa yavaş yörünge seç" ayrımına ancak model karar verebilir, kodda
  kural yazmak seçenek patlamasına gider — ki bu, paketin ortadan kaldırmak için var olduğu prompt
  cerrahisine dönmektir (spec §1.2).
  **Maliyet ayağı ölçüldü:** kısa video ucu script'siz istek kabul etmiyor, yani caption model
  çağrısı o akışta ZATEN zorunlu; seçim o çağrının çıktısına alan olarak bindiği için ek çağrı
  doğmuyor. Input'un A'yı önerme gerekçesi ("ek model çağrısı doğmaz") böylece korunuyor.

- **2026-08-24 (on birinci oturum) — K-113 = A (Eray onayı):** hareket havuzu boşsa bugünkü sabit
  listeye düşülür. Input bu dalın "yalnız tek hakemde" geçtiğini işaretlemişti; karara bağlandı.

- **2026-08-24 (on birinci oturum) — Checkpoint 11 için rezerveden bir tur (Eray):** checkpoint
  payı tükendikten sonra finale ayrılmış rezerveden bir tur fonlandı (audit: `checkpoint-cap-reserve`).
  O tur da yeni bir varyant buldu; beşinci tur taze oturuma bırakıldı.


> ⚠️ Aşağıdaki `K-xx` ID'leri sentez belgesinin (snapshot Bölüm 17) uzayıdır — eski spec'in
> `K1–K7` gündemiyle karıştırılmaz. Kanonik kapanış kayıtları snapshot **Ek B**'dedir.

- **2026-08-19 — Spec'e geçiş hükmü (Eray):** "Spec yazımı başlayabilir; Bölüm 17'deki ürün
  kararları ilgili sözleşme kesinleşmeden kapatılmalıdır." Karar uydurulmaz; açık karar K-ID
  atfıyla taşınır.
- **2026-08-21 — K-22 = A (Eray):** politika motoru Faz 1'e girer. Belge önerisi (B) TERSİYDİ;
  motor kararları (K-23 · K-24 · K-25 · K-133) Faz 1 spec gündemine girdi.
- **2026-08-21 — K-27 = A (Eray):** yönetici turu Claude Code komut ailesinden koşulur; panel
  geliştirilmez. Komut ailesinin varlığı doğrulanmadı — spec seansında ölçülür.
- **2026-08-21 — K-30 = A (Eray):** gerçek kullanım sinyali beklenmez; aktivasyon Faz 1'de
  (risk kabulü). K-29'dan bağımsız.
- **2026-08-21 — K-05 = B (Eray):** kanal envanteri Faz 1'de kurulur. Belge önerisi (A)
  TERSİYDİ; Marka DNA işiyle sınır spec'te çizilecek.
- **2026-08-23 — Supersede (Eray):** yeni spec TAMAMEN sentez spec-input'undan yazılır; eski
  spec (2026-07-11) ve eski plan (2026-07-12) dikkate ALINMAZ. İkisi de `superseded` işaretlendi.
  Ölçülen çelişki kaydı: politika motoru eski planda yok (K-22=A ile çelişir), kanal envanteri
  eski spec/planda açıkça kapsam dışıydı (K-05=B ile çelişir). Yeni spec sonrası plan sıfırdan.
- **2026-08-23 — Spec-içi teknik kapanışlar (İlke 8: review zinciri doğrular, Eray
  onayı gerekmez):** K-15 (b) = carousel ayrı yüzey değil, caption dalı (taze kod
  ölçümü) · K-01b anahtar sözleşmesi bağlandı (tek normalize modülü, ortak kod yolu) ·
  aday küme kanonik sorgu tanımı · kanal envanteri tasarımı (brand_kit.channels,
  kapalı 4'lü anahtar uzayı, muhafazakâr filtre) · migration rollback sırası ·
  önbellek hükmü (aktivasyon ya anahtara sürüm koyar ya açık invalidate — taze ölçüm:
  bugün kendiliğinden tazeleme yok). Tümü spec Bölüm 17.3'te listeli; Codex review
  sınayacak.
- **2026-08-23 — K-20 = A (kaynak-kanıtlı kapanış):** Katman-1 düzeneği Marka DNA işiyle
  ORTAK; DNA karar belgesi md. 7 hükmü birebir: "iki sistem aynı regresyon koşumunu paylaşır,
  ikinci altyapı kurulmaz" (`marka-dna-mimari-karar-dokumani.md:265-267`). Sentezin açık
  bıraktığı "bağlayıcılık" formalitesi kaynak hükmüyle kapandı. Eray vetosuna açık sunuldu.
- **2026-08-23 — K-21 = C (kaynaksız sayı, düşürüldü):** "22 sektör hedefi" ifadesinin tüm
  araştırma deposunda izi sürüldü — ilk kez 2026-08-11 sonradan-eklenen analiz katmanında
  beliriyor; öncesinde hiçbir kaynak/iş belgesinde/kodda yok (grep tüm depo). Taze ölçümler:
  12 kök sektör (DB) · 22 legacy şablon (templates_data.py: 28 şablonun 22'si) · 22 takvim
  kaydı (2026) — Ç-37 sayı-çakışması hipoteziyle uyumlu. Sonuç: ölçek gerekçesi 22'ye
  dayandırılmaz; 12 kök sektör ölçülmüş gerçek, ≤5 Faz 1 tavanı tahmin etiketiyle kalır
  (kapı yapılmaz), gerçek ölçek pilotta tur süresiyle ölçülür. Eray vetosuna açık sunuldu.
- **2026-08-23 — Karar kapanış turu (Eray, tek tek):** K-118 = kullanıcının somut isteği
  kazanır (ses profili yumuşak yönlendirme; yasak kelimeler mutlak kısıt kalır — öneri kabul) ·
  K-119 = anma satış-dili yasağı kullanıcı isteğini geçersiz kılar; K-118'in TEK istisnası
  (öneri kabul) · K-38 = yeni sürümsüz geri çekme (deaktivasyon) desteklenir; marka paketsiz
  yola döner, olay loglanır (öneri kabul) · **K-71 = BLOKLAR (öneriden FARKLI):** açık
  sorular kapanmadan aktivasyon yapılamaz; K-30 ile çelişmez (K-30 kullanım-sinyali,
  K-71 araştırma-sorusu düzenler) · K-10 = prompt-injection'a özel savunma Faz 1'de
  KURULMAZ (bilinçli risk kabulü; R-09 risk kaydı açık; yeniden açılma: paket/kaynak
  çeşitliliği artınca — öneri kabul) · K-144 = Faz 1'de ayrı hukuk onayı gerekmez (risk
  kabulü; ürünleştirme/platform-kazıma kapsama girerse yeniden açılır — öneri kabul) ·
  K-29 = A: pilot kontrollü TEST MARKASIYLA koşulur (kayıtlı iki marka kuyumcu değil;
  test markası kurulumu Faz 4 iş kalemi — öneri kabul) · K-149 = tur periyodu 6 ayla
  başlar (ilk tur süresi ölçülünce revize edilebilir; acil mevzuat tur-dışı kol —
  öneri kabul) · K-39 = geçmiş post kayıtları geriye dönük DEĞİŞMEZ (damganın kanıt
  değeri korunur — öneri kabul) · K-40 = "değerli bilgi sessizce kaybolmaz" HEDEF'tir,
  bağlayıcı garanti değil (tur başına kanıt yükü doğmaz — öneri kabul) · K-43 = bayat
  atama kaydı KORUNUR (paket geri gelirse marka kendiliğinden paketli çalışır — öneri
  kabul) · K-44 = bayat durum sistem içinde işaretlenir, log/işaret düzeyi (öneri kabul) ·
  **K-45 = ÇİFT YÖNLÜ bildirim (öneriden FARKLI, geniş):** yöneticiye aktif bildirim +
  marka sahibine devre-dışı mesajı ("Bakım çalışmaları nedeniyle gönderileriniz genel
  modda üretilmektedir...") + geri-dönüş mesajı ("Bakım çalışması tamamlandı, sektöre
  özel gönderi modu kullanıma açıldı") — metinler sabit, yüzey seçimi plan işi; Faz 1'e
  bildirim mekanizması iş kalemi eklendi · K-54 = yönetici rolü BÖLÜNMEZ (solo işletim;
  ölçek gelince yeniden açılır — öneri kabul) · K-69 = 20 maddelik hazırlık listesi ilk
  aktivasyon öncesi KAPI; otomatik ön-kontrol + tek onay; K-70 sorumlusu = operatör
  (öneri kabul) · **K-26 = sektör başına periyot alanı + VADE BİLDİRİMİ (öneri +
  genişleme):** vadesi dolan paket yöneticiye bildirilir (K-45 mekanizmasıyla aynı
  altyapı; Faz 1 iş kalemi) — Eray sorusu üzerine ölçüldü: spec'te vade uyarısı yoktu,
  bu kararla eklendi · K-72 = taslak reddi otomatik düzeltme turu BAŞLATMAZ; yeni koşuyu
  yönetici elle tetikler (öneri kabul) · K-73 = acil güncellemede tam tur ZORUNLU DEĞİL;
  şart: resmî kaynak kanıtı + iki denetçinin dar hızlı doğrulaması; onay kapısı kalkmaz
  (öneri kabul) · **K-56 = OLAY-BAZLI anında uyarı Faz 1'de kurulur (öneriden FARKLI,
  Eray yeniden çerçeveledi):** eşik/oran alarmı değil — sektörel modda üretilmesi gereken
  post paketsiz üretilirse yöneticiye derhal bildirim (K-45/K-26 mekanizmasıyla aynı
  altyapı); alarm sorumlusu = yönetici (rol sorusu da kapandı) · K-77 = denetim için
  yeni kimlik/yetki modeli kurulmaz, lokal tek kullanıcı (öneri kabul) · K-79 = denetçi
  izolasyonu + aynı-girdi hafif teknik garanti: komut ailesi kod düzeyinde zorlar
  (öneri kabul) · K-80 = tekrar-üretilebilirlik damgası ZORUNLU (model/sürüm/tarih/girdi
  özeti her artefaktta — öneri kabul) · K-81 = denetçi çıktısına otomatik biçim kontrolü
  EVET (mekanik, sentez öncesi — öneri kabul) · K-150 = tek geçerli raporla sentez
  ENGELLENİR; eksik denetçi yeniden koşulur (öneri kabul) · K-82 = yarım koşu
  "tamamlanmadı" işaretlenir, dosya ezilmez; yeniden koşum yeni deneme kimliği alır
  (K-83'ü de kapatır — öneri kabul) · K-105 = ara-pencere okuyucu testi zorunlu DEĞİL,
  isteğe bağlı plan kalemi (pencere emniyetli + K-56 uyarısı — öneri kabul) · K-120 =
  çelişki "boş alanın özel temsili" ile çözülür: sözleşmeye resmî `içerik-önerilmez`
  değeri; kontrol bilinçli-boşu geçirir (öneri kabul) · K-121 = kırpma sırası
  mevzuat-öncelikli ALTILI sıra; mevzuat/güvenlik asla ilk kırpılan olmaz (öneri kabul) ·
  K-122 = churn koruması BENİMSENİR: yeni-zayıf öğe sırf yeniliğiyle doğrulanmışı
  çıkaramaz (öneri kabul) · K-123 = "güçlü kaynak" TANIMLANIR; çekirdek: kaynağın aslı
  (resmî/birincil) + tarihli güncellik; tam metin sözleşme revizyonu (öneri kabul) ·
  K-124 = çıkarma kanıt eşiği: normal bilgide ≥1 doğrulanmış kanıt satırı;
  mevzuat/güvenlikte + iki denetçi mutabakatı, yoksa açık soruya düşer (öneri kabul) ·
  K-126 = tek-resmî-kaynak istisnası TANIMLANIR: resmî kaynak (K-123) + en az bir
  denetçinin canlı URL doğrulaması (öneri kabul) · K-127 = asgari kaynak tabanı 2;
  1'e düşerse koşu durur, karar yöneticide (öneri kabul) · K-129 = mevzuat/güvenlik
  alan listesi SABİT: yasaklar-ve-hassasiyetler tamamı + mevzuat/tarih/sayı içeren tüm
  iddialar (öneri kabul) · K-135 = paketlere yazma yalnız operatör + koşu yüzeyi —
  bağlayıcı kural; ikinci yazma yüzeyi ancak açık kural değişikliğiyle (öneri kabul) ·
  K-136 = günlüklerde sır tutulmaz; günlük yazıcısına maskeleme süzgeci, hata mesajları
  dahil (öneri kabul) · K-137 = araç kimliği denetçi ortamına sızmaz — yapısal garanti,
  anonimleştirme kod düzeyinde (öneri kabul) · K-16 = paket içeriği iç kullanım +
  yönetici; müşteriye KAPALI (öneri kabul) · K-138 = araç↔rapor eşlemesi kalıcı
  KAYDEDİLİR; körlük erişimle korunur (öneri kabul) · K-139 = ham katman + eşlemeyi
  yalnız operatör/yönetici okur (öneri kabul) · K-140/K-141 = ham katman + paket
  sürümleri SÜRESİZ saklanır; yeniden bakış: hacim/KVKK sinyali (öneri kabul) · K-142 =
  taslaklara ayrı saklama kuralı YOK, onlar da kalıcı; K-143 hiç doğmaz (öneri kabul) ·
  K-31 = pilot bitişi ÖN KOŞUL modeliyle; takvim süresi tanımlanmaz, şartlar K-32…K-37'de
  (öneri kabul) · K-19 = alt sektör teyit bileşeni onboarding + marka ayarlarında,
  mevcut sektör seçiminin yanında; yeni yüzey yok (öneri kabul). **TUR TAMAMLANDI:
  45/45 karar kapandı** — 41 öneri kabul (2'si genişlemeli: K-26 vade bildirimi,
  K-69+K-70), 3 öneriden farklı (K-71 bloklar · K-45 çift yönlü bildirim · K-56
  olay-bazlı anında uyarı), 1 öneri+yeniden-çerçeveleme (K-56'da eşik→olay). Ek
  kapanışlar: K-70, K-83, K-143 (bağlı kararlar kendiliğinden çözüldü) ve K-57
  (alarm sorumlusu = yönetici; K-56 kapanışının "rol sorusu da kapandı" hükmüyle —
  sweep hazırlığında tespit edilip 2026-08-23 üçüncü oturumda bu listeye eklendi).
- **2026-08-23 — Spec ONAYLANDI (Eray):** karar turu kapanışının ardından frontmatter
  `reviewed-pending-user-approval` → `spec-approved`. Plan `/write-plan-claude-codex`
  ile SIFIRDAN yazılacak (eski plan superseded).
- **2026-08-23 (dördüncü oturum) — Plan yapısı: 2 planlı staged split (Eray):** Plan 1 =
  runtime çekirdeği ("paketi TÜKETEN her şey"), Plan 2 = işletim hattı ("paketi ÜRETEN ve
  AKTİVE EDEN her şey"); tek arayüz DB sözleşmesi + kanonik teslim listesi. Gerekçe: motor
  ön-koşul kararları (K-84/K-151/K-152) açıkken detay-plan karar uydururdu.
- **2026-08-23 (dördüncü oturum) — F17 risk kabulü (Eray):** K-07 damgası "üretim-oturumu
  atfı"dır (edited lineage) — bayt-bayt içerik kanıtı iddia edilmez (caption düzenlenebilir);
  aynı-marka kullanılmamış makbuz ikamesi kabul edilen risk; yeniden açılma: müşteri
  sayısı/ürünleşme artışı. Plana işlendi (bağlanan teknik karar 1).
- **2026-08-23 (dördüncü oturum) — Plan-içi teknik bağlamalar (İlke 8, review zinciri
  sınadı):** K-07 bileşik FK + opak generation_id · K-08a TEXT · K-08b DB trigger +
  reparenting yasağı · paket okuması önbelleksiz · Katman-1 = Anthropic istemci kesişimi ·
  bildirim = transactional outbox + versiyonlu n8n workflow · K-101/K-102 tek-transaction
  (dar-refactor fallback'li) · K-94 mekanizma-var-kural-açık (opsiyonel alan).
- **2026-08-23 — Sentez deposu sweep borcu KAPSAM DARALTMASIYLA kapandı (Eray):**
  kapanan kararların kanonik kaynağa (araştırma deposu, Bölüm 17 + Ek B + gövde)
  geriye dönük işlenmesi İPTAL — spec onaylandıktan sonra arşiv belgesini yeniden
  yazmak (51 satır + ~30 kalan gövde düzenlemesi + ~47 Ek B kaydı + Codex doğrulama
  turu) risk/fayda dengesini aşıyor; "süreç ağırlığı ≈ risk ağırlığı". Başlanan
  düzenlemeler (51 satır + ~35 gövde) commit edilmeden geri alındı; baseline sha
  doğrulandı. Yerine: kaynak belgeye statü notu (belge başı + Bölüm 17 başlığı —
  51 kapanışın ID listesi + "çelişkide spec esastır" hükmü) + snapshot yeniden
  eşitleme. Yeniden açılma koşulu: arşiv belgesi ileride yeniden canlı girdi olursa.
- **2026-08-24 — Yol seçimi: "sadeleştir + fix" (Eray) + Plan 1 ONAYI:** F23'ün konusu
  (recovered bandı + K-45 geri-dönüş mesajının teslimi) Plan 2'ye taşındı — gerekçe:
  tetiği (reaktivasyon) yalnız Plan 2 komut ailesinden koşulabilir, Plan 1 ömründe
  recovered durumu hiç doğamaz; K-45 kararı ve sabit metinler KORUNUR, Plan 2 kalemi
  atama-geçmişi kanıtını da içerir. F22 = olay-türüne özgü sürüm şekilleri (sentinelsiz),
  F24 = olay kaydı geçişle aynı transaction. Tur 7 approve → `plan-approved`.
- **2026-08-24 (altıncı oturum) — Yürütme başlangıç kararları (Eray):** yürütme ayrı dalda
  (`feat/sektor-bilgi-paketi`) koşar — main temiz kalır, kapanış `/finish-branch-claude-codex`
  kararına bırakılır · mod subagent-driven (16 task'lık planda bağlam korunması) · Python ortamı
  **izole venv** (`apps/social/backend/.venv`), sistem Python'ına dokunulmaz. Gerekçe ölçüldü:
  requirements.txt'i sisteme kurmak, sistemde daha yeni sürümü bulunan **11 paketi geri sürüme**
  düşürüyordu (Pillow 12.2→11.2, weasyprint 68→63, uvicorn 0.51→0.30 vb.); canlı backend zaten
  Docker konteynerinde kendi Python'ıyla koşuyor, yani sistem paketleri canlıyı beslemiyor.
- **2026-08-24 (yedinci oturum) — Task 3 inline koşuldu (Eray talebi):** "bu oturumda
  task'ları subagent olarak değil, inline yaz". Execution State'teki `execute_mode`
  DEĞİŞTİRİLMEDİ (subagent-driven kayıt olarak kalır; Task 1-2'yi doğru anlatıyor) —
  inline yalnız bu oturumun çalışma biçimidir. **Kapsam düzeltmesi (Eray, aynı oturum):**
  "inline" YALNIZ task yazımını kapsar; review/checkpoint kapıları normal koşar. İlk
  yorumum bunu yanlışlıkla review'lara da genişletmişti — Eray düzeltti, checkpoint 3
  aynı oturumda koştu (4 tur, approve).
- **2026-08-24 (altıncı oturum) — Geçmiş yeniden yazımı (Eray onaylı):** `9ed5902` commit'i
  `Exec-Kind: code` etiketiyle inmişti ama yalnız `tests/` altına dokunuyordu → türetilmiş
  defter MECH-FAIL veriyor, Adım 11.0 mekanik kapısını ve push'u bloklyordu. Etiket `red-only`'ye
  çevrildi, sonraki 5 commit replay edildi; **dosya içerikleri bayt-aynı** doğrulandı. Kök neden:
  alt-oturum talimatında etiketi ben dikte ettim, commit'in path kümesine bakmadan. Emniyet
  etiketi `backup/pre-footer-fix` (`/finish-branch` sonrası silinir).
- **2026-08-21 — Denetim + sweep (Eray: "yüksek bulguları giderelim" + commit onayı):**
  Codex denetiminin iki yüksek bulgusu sentez deposunda giderildi (commit'ler
  `8e298eb → c380e37`); dört kapanışın statü/kapsam izleri gövdeye işlendi, karar-durumu
  ölçümü tazelendi (162 = 153 açık + 9 kapalı). Kapanış 4 turlu Codex doğrulamasıyla
  CONFIRMED. Orta bulgular bilinçli açık bırakıldı (Open Problems'ta).
