---
title: Sektör Bilgi Paketi — Runtime Çekirdek Uygulaması
status: waiting-review
started: 2026-07-12
last-touched: 2026-08-26
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

**2026-08-26 (on dokuzuncu oturum) — REVIEW ZİNCİRİ BİTTİ: `/security-review-claude-codex`
üç turla koştu, güvenlik kapısı TEMİZ. Durum `waiting-review` olarak KALIYOR.
Sıradaki: `sector-packages-mandatory-split` → `/finish-branch-claude-codex`.**

Üç tur, her turunda iki bağımsız hakem (fresh Claude subagent + Codex `adversarial-review`),
hiçbirinde degradasyon yok. `completed_evaluations=3`, `consecutive_degraded=0`.
Rapor: `docs/security-reviews/2026-08-26-feat-sektor-bilgi-paketi.md` (başındaki düzeltme
banner'ı ÖNCE okunmalı).

**Attempt-1'in üç yüksek bulgusundan ikisi gerçekti ve düzeltildi:**
- **SSRF** — kullanıcının verdiği URL iki yüzeyde de doğrudan `httpx`'e gidiyordu; şema ön eki
  dışında kontrol yoktu, yönlendirmeler kör izleniyordu. Ortak bir kapı kuruldu: şema/port
  allowlist'i, çözülen HER adres için pozitif `is_global` koşulu, yönlendirmenin elle ve her
  adımda yeniden doğrulanarak izlenmesi, bağlantının doğrulanan IP'ye sabitlenmesi. Sonraki
  turlar üç eksik daha buldu (taşıyıcı-NAT aralığı geçiyordu · bayt sınırı indirmeyi değil
  sonucu kesiyordu · sıkıştırılmış gövde sınırı ~128× aşıyordu) — hepsi kapatıldı, kapanış
  75 kombinasyonluk ÜRETİLMİŞ matrisle kanıtlandı.
- **Kiracı kapsamı** — doküman ve ürün erişimi çağıranın doğrulanmış markasına bağlandı; kapsam
  yardımcının İÇİNDE ve parametre zorunlu (unutan çağıran sızdırmaz, `TypeError` alır). Kapanış
  turu ürün GÖRSELİ ayağının açık kaldığını buldu; o da kapatıldı, uçlar yabancı ürünü 404'lüyor.

**Üçüncü bulgu GERÇEK DEĞİLDİ ve geri alındı** (`15692c1`) — ayrıntı ve kök neden Open Problems'ta.

Test: **657 passed** (oturum başı 580). Her düzeltmenin mutasyon kontrolü var; SSRF kapısı ayrıca
canlı internete karşı pozitif/negatif sondalandı.

# Open Problems

- **[KAPANDI — BULGU DEĞİLDİ, premis çürütüldü 2026-08-26] "Kullanıcı metni paket içeriğini
  modelden çektirebilir" iddiası.** Paket metni müşteriden gizli DEĞİLDİR: paket üretimi besler,
  müşteri çıkan post'u görüp onaylar. Müşteriden gizli olan **ham araştırma katmanı** (K-139:
  "ham katman + eşlemeyi YALNIZ operatör/yönetici okur") ve yönetici işlemleridir. K-16'nın
  "API'den okunabilirlik: müşteriye KAPALI" hükmü, müşteriye paket listeleyen bir UÇ olup
  olmadığını karara bağlar — "paketten türeyen hiçbir metin müşteriye ulaşmaz" DEMEZ.
  **Kök neden bende:** gizlilik iddiasını iki hakeme verdiğim ORTAK BAĞLAM metnine doğrulamadan
  yazdım; ikisi de onu sorgulamak yerine ona karşı doğrulama yaptı, bu yüzden uyuşmaları bağımsız
  teyit sayılmaz (ortak-mod artefaktı). Komutun kendi kuralı bunu yasaklıyordu, atladım.
  Düzeltmesi `15692c1` ile GERİ ALINDI; üç dosya bayt-bayt eski hâlinde (`cmp` ile doğrulandı),
  kısa video dosyasının sahne bloğu da birebir aynı. Kapanış turunun bu soydan gelen üç bulgusu
  (N3 · N4 · N5) aynı sebeple düştü — `rejected`, `accepted_risk` DEĞİL.
  **Kalıcı not:** memory `project_sector_package_confidentiality` +
  `feedback_no_role_claims_in_reviewer_context`.

- **[KAPANDI 2026-08-26 — `b4f9e17` + `c5dcc5a`, kapanış turu teyitli] Doküman kimlikleri marka
  kapsamına bağlı değildi → kiracılar arası RAG ifşası.** `document_processor.py::get_document_context`
  sorguyu `WHERE id IN (...)` ile kuruyor, `brand_id` filtresi YOK; çağıranlar `assert_brand_owned`
  ile MARKAYI doğruluyor ama `payload.document_ids`'i doğrulamadan geçiriyor. Başka kiracının doküman
  UUID'sini bilen kimliği doğrulanmış kullanıcı, o dokümanın `raw_text`'ini kendi üretim bağlamına
  enjekte edip modelden geri okutabilir. `get_product_document_context` (satır 318-337) aynı sınıfta.
  **Ölçüldü:** dosya bu dalda hiç değişmedi (`git diff --stat 5a9d5d4..7a2a180 --` boş), taban da aynı
  çağrıyı yapıyordu → devralınan borç. Doğru örnek aynı depoda: `documents.py:79-99`. Fix yönü:
  doğrulanmış `brand_id`'yi zorunlu parametre yap + `AND brand_id = $2` + dönen küme istenenden
  farklıysa tüm isteği 404 ile reddet (fail-closed). Çağrı yerleri: `ai.py:428`, `posts.py:115/301/305/936/1053`.
  Regresyon testi BUGÜN YOK. Ayrıntı: security review S2.

- **[KAPANDI 2026-08-26 — `b15ab6e` + `c5dcc5a`, kapanış turu teyitli] `POST /ai/analyze-website`
  kimlik doğrulanmış SSRF'e açıktı.** İki hakem de bağımsız buldu. `payload.url` yalnız şema ön ekiyle
  kabul ediliyor; host allow-list'i, DNS çözümlemesi sonrası özel-IP reddi (RFC1918 · loopback ·
  `169.254.169.254`) ve port kısıtı yok, üstelik `follow_redirects=True`. Yanıtın ilk 8.000 karakteri
  modele veriliyor ve model onu özetleyip çağırana döndürüyor → kör değil, içerik sızdıran SSRF.
  **Ölçüldü:** savunmasız satırlar taban commit'te birebir aynı (`git show 5a9d5d4:.../ai.py`) →
  devralınan; dal fonksiyona dokundu, açığı açmadı. Kardeş yüzey `competitor_analyzer.py:31` aynı
  desende (gövdesi okunmadı — ÇIKARIM). Fix yönü: ortak SSRF-güvenli çekici — yönlendirmeyi elle ve
  her adımda yeniden doğrulayarak izle, çözülen HER adresi özel-aralık kontrolünden geçir, bağlantıyı
  doğrulanan IP'ye pinle. Ayrıntı: security review S1.

- **[YENİ, review 2026-08-26 — `accepted_risk`, ama BU PARTİNİN ürünü] `resolve_sector`'ün
  dönüş sözleşmesi değişti, çağıranlar tam güncellenmedi.** Fonksiyon artık `tuple | None`
  değil `tuple` dönüyor ve taksonomi bozukken `TaxonomyUnavailableError` fırlatıyor — ama
  `brands.py`'deki iki çağıranın hiçbiri yakalamıyor ve `main.py`'de handler yok, dolayısıyla
  müşteri jenerik 500 görüyor (beklenen: 503). Ayrıca `brands.py:122`'de artık ulaşılamayan bir
  geri-düşüş dalı kaldı ve okuyucuya "None dönebilir" diyor. Ölçüldü (grep + kod okuması).
  Review politikası orta bulguyu fix-required saymadığı için düzeltilmedi; devralınan borç
  DEĞİL, bu dalın ürünü olduğu için burada görünür kalıyor.

- **[YENİ, review 2026-08-26 — `accepted_risk`] `schema_version` kolonu hiçbir yerde okunmuyor.**
  Çalışma zamanı doğrulayıcısı kapalı alan kümesini sert uyguluyor ve `schema_version`'ı hiç
  görmüyor; bir şema artışı tüm eski paketleri sessizce devre dışı bırakır (paketli markalar
  paketsiz yola düşer, üretim durmaz, kimse fark etmez). Spec §3.4'ün "şema değişimi
  `schema_version` ile taşınır" hükmünün kod karşılığı yok. Plan 2 şemayı hiç artırmayacaksa
  en azından kolonun kullanılmadığı belgelenmeli.

- **[YENİ, review 2026-08-26 — `accepted_risk`] K-04 kullanım talimatı üç metne ayrışmış.**
  Normatif Türkçe metin yalnız caption/fikir yüzeylerinde birebir basılıyor; görsel ve
  durağan-kare yüzeylerinde iki ayrı serbest İngilizce parafraz var, `_enrich_with_scene`'de
  ise hiç yok. Spec §4.5 "HER enjeksiyon bloğunun başına" diyor. Tam olarak K-01b'de kapatılan
  ayrışma sınıfı.


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

- **2026-08-26 — n8n tarafı canlıya kuruldu (credential + pasif workflow):**
  `Otomaix Admin Event Key` credential'ı import edildi (kimlik `otomaixAdminEvtKey`, dosyanın
  beklediğiyle birebir); workflow `sectorPkgAdminEv` olarak import edildi ve **`active=false`**
  (ölçüldü — hiçbir tetikleyici koşmuyor). Dört credential atıfı da isimle çözüldü.
  **Dosyaya sabit `id` eklendi:** id'siz import n8n CLI tarafından reddediliyordu, yani artefakt
  canlıya hiç giremiyordu; sabit id tekrar import'u da idempotent yapar. Regresyon + mutasyon
  kontrolü eklendi (660 test).
  **Backend env'i agent yapamaz:** Coolify env değerlerini Laravel `Crypt` ile şifreli tutuyor
  ve API token tanımlı değil — UI işi. **Aktivasyon deploy'a bağlı:** kurtarma adımının çağırdığı
  uç canlıda henüz yok, erken aktivasyon 5 dakikada bir 404 üretir.

- **2026-08-26 — Migration 032/033/034 CANLIYA UYGULANDI (Eray talimatı):**
  Üçü de `rc=0`, dosya başına tek transaction. Uygulama öncesi yedek alındı ve okunabilirliği
  doğrulandı (`otomaix-pre-032-20260826-185643.dump`). **Uygulama sonrası ölçüldü:** mevcut veri
  değişmedi (2 marka · 81 post · 12 sektör, geri doldurma yok), beş tetikleyici kurulu, dört
  negatif kontrol reddedildi, eski backend'in yazımları hâlâ geçiyor. Ayrıntı: HANDOFF.
  **Not:** canlıda hâlâ alt sektör yok — şema hazır, veri Plan 2'nin işi.

- **2026-08-26 — PR #2 açıldı** (`feat/sektor-bilgi-paketi` → `main`, HEAD `d8a6d5d`):
  https://github.com/Eray-Deniz/otomaix/pull/2 · task `waiting-review` olarak kalır.

- **2026-08-26 (yirminci oturum) — Dal kapanışı = PR yolu (Eray, `/finish-branch-claude-codex`):**
  Closure-audit iki blocker buldu. Birincisi kapatıldı: 130 commit yalnız bu makinedeydi, PR yolu
  uzak ref üretiyor. **İkincisi AÇIK ve PR review'ının işi:** zincir raporları kapanış aralığını
  kapsamıyor — güvenlik kapanışından (`b15ab6e`) sonraki 10 commit'in İKİSİ KOD (`39f283d` modül
  bölmesi, `3561231` n8n credential bağlaması) ve hiçbir hakem görmedi.
  **Task `waiting-review` KALIR, arşivlenmez, vault promotion YAPILMAZ** (B yolunun matrisi).
  `.ledger-index/` izlenmeye alındı — 25 baytlık locator, oturumlar arası defter sürekliliğinin
  tek dayanağı; yok sayılsa mekanizma amacını kaybederdi (teknik karar, İlke 8).

- **2026-08-26 (yirminci oturum) — n8n workflow'u gerçek altyapıya bağlandı (Eray onaylı):**
  `sector-package-admin-events.json` Telegram token'ını ve chat id'sini `$env`'den okuyordu.
  **ÖLÇÜLDÜ:** canlı n8n `N8N_BLOCK_ENV_ACCESS_IN_NODE=true` ile koşuyor — node içinden ortam
  değişkeni okumak KAPALI. Yani dosya import edilse canlıda HİÇ çalışamazdı. Hiçbir hakem
  yakalayamazdı: review zinciri n8n'in içine bakmadı, artefakt canlıya bakılmadan yazılmıştı.
  **Düzeltme:** Telegram düğümü `n8n-nodes-base.telegram` (tv 1.2) + mevcut `Telegram account`
  credential'ı; chat id yeni bir Postgres düğümüyle `social.workspaces`'ten okunuyor (mevcut
  `Postgres account` credential'ı). **Eray kararı:** ayrı admin botu kurulmadı, mevcut bot +
  mevcut chat kullanılıyor — bugün 2 markalık sistemde ikinci kanalın karşılığı yok.
  **Sır depoya GİRMEDİ:** token n8n'in şifreli credential deposunda kalır (kardeş
  `turkey-calendar-update.json` canlı bot token'ını depoda taşıyor — ayrı temizlik borcu).
  **Sınıf kapatıldı:** iki regresyon eklendi (`$env` yasağı + yer tutucu credential id yasağı),
  ikisi de mutasyonla pozitif kontrol edildi.

- **2026-08-26 (yirminci oturum) — Canlı durum ÖLÇÜLDÜ; migration uygulanmadı:**
  Bu makine canlının kendisi (Coolify + n8n + veritabanı burada). Canlı DB: 2 marka · 81 post ·
  12 sektör — **hepsi kök, tek alt sektör yok**, yani paket sistemi bugün bağlanacak bir şey
  bulamaz. Üç migration canlı verinin birebir kopyasında prova edildi: üçü de rc=0, idempotent,
  mevcut veri bozulmadı, canlıda koşan eski backend'in (`3e1617e`) yazımları etkilenmedi,
  kapılar iki yönde de doğrulandı. Tam yedek: `/root/otomaix-db-backups/otomaix-pre-032-*.dump`.
  **Canlıya yazma adımını izin katmanı reddetti** — uygulama Eray'a kaldı, komut HANDOFF'ta.

- **2026-08-26 (yirminci oturum) — Yaşam döngüsü AYRI modüle taşındı:**
  `sector_packages.py` 1804 satırdı ve zorunlu bölme eşiğinin üstündeydi. Yaşam döngüsü bölümü
  (`LifecycleError`'dan `deactivate_package`'a) `app/services/sector_package_lifecycle.py`'ye
  taşındı; kalan dosya 1310 satır, yeni modül 524 satır. **Ayrım noktası taze ölçüldü:** üst
  yarıdan yaşam döngüsü adlarına tek atıf yok (yalnız kendi başlık yorumunda); yaşam döngüsü
  üst yarıdan sadece `normalize_special_day_key` + `validate_package_content` + `log_package_event`
  okuyor. Bağımlılık tek yönlü. **Gerekçe yalnız satır sayısı değil sözleşme farkı:** erişim
  katmanı çalışma zamanında asla üretimi bloklamaz (hata → `None` + log), yaşam döngüsü ise
  fail-closed'dur. İki zıt sözleşme aynı dosyada okuyucuyu yanıltıyordu.
  **Gövdenin kalanı bölünMEDİ:** doğrulayıcı ileri, basım geri atıf yapıyor — üçüncü bir
  "ortak ilkeller" modülü ister, yani yapı değil dağılma olurdu.
  **Plan 2 arayüz listesi güncellendi** (`docs/plans/2026-08-23-...` YOL DÜZELTMESİ maddesi):
  imzalar değişmedi, yalnız içe aktarma yolu.

- **2026-08-26 (on yedinci oturum) — Basitleştirme kapsamı = yalnız üretim kodu (Eray):**
  testler, migration'lar ve dokümanlar tarama dışında bırakıldı. Gerekçe: test dosyasına dokunmak
  komutun kendi kuralıyla otomatik yüksek riske çıkıyor ve bayt-değişmezlik kapısını riske atıyor;
  migration'lar canlıya hiç uygulanmadı ve testlerle bayt düzeyinde pinli.

- **2026-08-26 (on yedinci oturum) — Prompt bloğu tekrarı ORTAKLAŞTIRILMADI (Eray, Codex vetosu
  kabul):** iki modüldeki aynı dal tek yere indirilmedi. **Eray'ın gerekçesi:** kod, üretilen metnin
  baytını sabitleyen kapının tam ortasında ve hakem ilgili dosyayı göremediği için "birleştirme
  güvenli" diyemedi; riski şimdi almak yerine tekrar review zincirine taşınır.
  **Dürüst etiket: çözülmedi, bilinçle bırakıldı** — tekrarın kendisi duruyor.

- **2026-08-26 (on yedinci oturum) — 1785 satırlık dosya ŞİMDİ BÖLÜNMEDİ (Eray):** zorunlu bölme
  eşiği aşılmış ve tek yönlü temiz bir ayrım noktası ÖLÇÜLDÜ (yaşam döngüsü bölümü, ~490 satır),
  ama bölme review zincirinden sonraya bırakıldı. **Eray'ın gerekçesi:** 490 satırlık taşıma hemen
  ardından gelecek iki review komutunun önüne büyük ve gürültülü bir değişim koyar, hakemler asıl
  işi değil taşımayı okur. **Dürüst etiket: çözülmedi + park edildi.** Hakem bunu ayrı bir orta
  bulgu olarak işaretledi ("tetik ev değildir"); bu yüzden `CURRENT.md`'de gerçek bir madde açıldı.

- **2026-08-26 (on yedinci oturum) — Hakem üç dosyayı okuyamayınca değişiklik prompt'a gömüldü
  (Eray):** komutun ilan ettiği çağrı biçiminden SAPILDI. **Eray'ın gerekçesi:** alternatif
  "denetimi hiç koşturma + commit atma" idi; denetimin gerçekten koşması ve commit'in bir hakem
  görüşüne dayanması tercih edildi. **Bedeli kayda geçti:** o üç dosyanın çevresindeki değişmemiş
  kod denetlenmedi.

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
