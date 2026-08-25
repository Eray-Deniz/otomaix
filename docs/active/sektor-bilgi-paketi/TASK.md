---
title: Sektör Bilgi Paketi — Runtime Çekirdek Uygulaması
status: waiting-review
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
- last_checkpoint_ref: a2f450507b2097477fbcd5f27149fc0895914793
- cp_count: 17
  <!-- Checkpoint 17 (Task 16 + dört fix): DÖRT tur. Tur 1 needs-attention
       (1 high + 2 medium): sözleşme testi "migration 032 şeması"nı iki tablo adına
       indirmişti, rapor tam kapsama iddia ediyordu. Tur 2 needs-attention: aynı eksenin
       yeni varyantı (PK/varsayılan/FK yok) -> yöntem DEĞİŞTİRİLDİ, seçilmiş özellik
       listesi yerine kataloğdan kapalı MANİFEST. Tur 3 needs-attention (2 high): manifest
       nesneleri kapatmıştı ama YÜZEY listesi hâlâ elle seçilmişti (UNLOGGED tablo
       geçerdi) -> 034'ün tablo-imzası standardı eklendi; ve F5: tur 2'de yazdığım sweep
       boru hattı sweep'in çıkış kodunu yutuyordu (kendi düzeltmemin açtığı delik,
       hakem buldu). Tur 4 APPROVE; tek medium (kontrol tablosu ona çıkmışken metin
       dokuz diyordu) belge düzeltmesiyle kapatıldı, beşinci tur AÇILMADI.
       Toplam 10 mutasyon pozitif kontrolü, hepsi de04ede'ye karşı taze ölçüldü.
       Tavan (8) AŞILDI: Eray bu oturumda izni açıkça verdi (RUN-anyway; ceiling-exceed).
       MECH-FAIL çözüldü: T15b* footer'ları S1 gramerine uymuyordu ve revert commit'i
       yanlış kind taşıyordu; Eray onayıyla mesaj-yeniden-yazımı yapıldı (ağaç hash'leri
       BİREBİR aynı doğrulandı; emniyet etiketi backup/pre-t15b-footer-fix).
       Checkpoint 16 (Task 15b): TEK tur, needs-attention -> DUR dalı ->
       kullanıcı kararı GERİ AL. Beş high, beşi de o turun ürünü ve beşi de
       kod okunarak doğrulandı (iki en ağırı: bekleyen iş için tek yuva ->
       marka ve kimlik yazımı birbirini siliyordu; başarısız HER yazım
       "çakışma" sayılıp kullanıcının taslağını yok ediyordu). Önyüz geri
       alındı (`d9c4264`), otomatik kaydetme Task 15 sonrası hâlinde kaldı.
       Sunucu tarafındaki koşullu yazım kapısı + 5 testi UYKUDA bırakıldı.
       Kök neden YÖNTEM: önyüzde otomatik test altyapısı yok, doğrulama
       "okundu + derlendi" ile yapıldı. Alt sistem CURRENT.md'de
       `brand-settings-save-integrity` olarak adlandırıldı (tetik: Task 16'dan
       sonra, canlıya müşteri alınmadan ÖNCE).
       Checkpoint 15: üç tur; DUR dalı → kullanıcı kararı KAPSAM DARALT.
       Tur 1: bir high + beş medium. Tur 2: F1-F6 kapalı doğrulandı, bir yeni
       high (yeni ücretli uçta kabul kontrolü yok) + iki medium; biri kendi
       düzeltmemin yan etkisiydi (zamanlayıcıları ayırınca "Kaydedildi"
       göstergesi ilk biten işlemde yanıyordu). Tur 3: F1-F6 yine kapalı, ama
       iki sınıf "sayarak kapanmaz" teşhisiyle geri geldi → sistemik-sınıf
       kuralı ateşlendi, tavan BEKLENMEDEN durduruldu.
       Kalan iki sınıf accepted_risk DEĞİL, adlandırılmış eve taşındı:
       otomatik-kaydetme bütünlüğü -> Task 15b (Task 16'dan ÖNCE);
       sağlayıcı çağrısının kesilememesi -> kod tabanı geneli desen, bu
       partinin kusuru değil. Somut kusurlar f17e248'de kapatıldı.
       Premis düzeltmesi (Eray): marka ayarları MÜŞTERİ yüzeyidir; riski
       "tek operatör" ölçeğiyle küçültmek yanlıştı.
       Ayrıntı: Codex defteri, 2026-08-25 checkpoint 15 disposition.
       Checkpoint 14: üç tur; tur 3 `approve`, bulgu YOK -> §8.6 Clean dalı.
       Tur 1: DÖRT high (kimliksiz webhook · teslimden önce onay · havuz
       tüketimi · migration kendi tablosunu doğrulamıyor). Tur 2: ilk üçü kapalı
       doğrulandı, F4 YENİDEN AÇILDI — kapı kolon imzasını görüyordu ama
       tablonun kendi katalog özelliklerini görmüyordu (UNLOGGED sonda rc=0 ile
       geçiyordu; Codex "çıkarım" diye işaretledi, kabul edilmeden ÖNCE ölçüldü).
       Tur 2 fix'i varyantı değil SINIFI kapattı (relkind/relpersistence/
       relispartition/rls/force_rls) ve kapanışı iki vakalık matrisle kanıtladı.
       Tur 3: bulgu yok. İki tur üst üste aynı sınıfa çarptığı için tur 3
       prompt'una "bu sınıfın dar bir varyantı daha çıkarsa yama kalemi olarak
       değil, sayarak-kapanmaz teşhisi olarak raporla" kısıtı yazıldı.
       Ayrıntı: Codex defteri, 2026-08-25 çağrıları.
       Checkpoint 13: üç tur; tur 3 `approve`, bulgu YOK -> §8.6 Clean dalı.
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

**2026-08-25 (on beşinci oturum) — TASK 15 BİTTİ. TASK 15b AÇILDI, DENETİMDE DÜŞTÜ, GERİ ALINDI.
Açık kapı YOK.**

**Task 15 (atama akışı) bitti.** Aday küme kanonik sorgudan (canlı, önbelleksiz) tek evde
üretiliyor; iki tüketici yüzeyi kapalı, üretim akışı kümeye hiç uğramıyor. Model önerisi kapalı
listeye karşı doğrulanıyor — üçüncü dönüş biçimi yok. `sub_sector_id` yazımı marka oluşturma ve
marka ayarlarında açık, boşaltma açık `null` ile. Web sitesiz geri düşüşün öneri ucu da eklendi
(spec §7.1'in denetimde fark edilen eksik ayağı).

Checkpoint 15 ÜÇ tur koştu: tur 1'de bir high + beş medium, tur 2'de F1-F6 kapalı + bir yeni
high + iki medium, tur 3'te iki sınıf "sayarak kapanmaz" teşhisiyle geri geldi. Sistemik-sınıf
kuralı ateşlendi, otonom döngü tavan beklenmeden durdu. Eray kararı: kaydetme bütünlüğü ayrı
görev (15b), sağlayıcı çağrısının kesilememesi kod tabanı geneli desen olarak kaydedildi.

**Task 15b (kaydetme bütünlüğü) yazıldı ve GERİ ALINDI.** Denetim beş high buldu; beşi de o
turun ürünüydü ve iki yolda kod, düzelttiği hatadan kötüydü. Eray kararı: önyüz geri alınır,
otomatik kaydetme bugünkü hâlinde kalır, alt sistem adlandırılmış iş olur.

**Premis düzeltmesi (Eray):** marka ayarları MÜŞTERİ yüzeyidir — abone kendi marka bilgisini
orada doldurur. Bulgu ciddiyetini "tek operatör / 2 marka" ölçeğiyle küçültmek YANLIŞTI; ölçüt
"müşteri kaydettiğini sanıp kaydetmemiş olabilir mi"dir.

**Yöntem dersi (kayda geçti):** otomatik test altyapısı olmayan bir dosyada elle eşzamanlılık
kodu yazıldı ve doğrulama "okundu + derlendi" ile yapıldı. Bu yöntem araya-girme hatalarını
tanım gereği yakalayamaz. Arka uçta mutasyonla ölçülen her şey sağlam çıktı; kırılan her şey
ölçülemeyen tarafta oldu.

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
- **2026-08-25 (on beşinci oturum) — Manuel doğrulamalar Plan 2 sonrasına ertelendi (Eray):**
  Task 15'in arayüz doğrulaması, canlı n8n importu + Telegram smoke'u ve gerçek uçtan uca üretim
  denemesi TEK bir doğrulama turunda, **Plan 2 bittikten sonra** koşulacak. Sonuç: Plan 1
  kapanış raporu arayüz yüzeyleri için "doğrulandı" İDDİA ETMEZ; erteleme evi ve tetiğiyle
  birlikte kaydedilir. Task 16 otomatik kapılarını (tam sweep, arayüz sözleşme testi) yine koşar.
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
