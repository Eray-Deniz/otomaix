---
title: Sektör paketi — zorunlu kurallar, türe göre seçim, gönderi türü (uygulama planı)
status: plan-approved
date: 2026-09-25
source_spec: docs/specs/2026-09-25-paket-zorunlu-kurallar-ve-gonderi-turu.md
source_spec_unapproved_override: false
noisy_review_override: false
unresolved_high_severity_override: true
codex_plan_review_status: approved
codex_plan_review_iterations: 0
codex_plan_review_log: ~/.claude/logs/otomaix--ffc87809/2026-09-25-paket-zorunlu-kurallar-ve-gonderi-turu-plan.md
---

# Sektör paketi — zorunlu kurallar, türe göre seçim, gönderi türü — Uygulama Planı

> **Yürütücüler için:** bu plan `/execute-plan-claude-codex` ile yürütülür (görev başına TDD + checkpoint).
> **Skill zinciri override:** `finishing-a-development-branch`, `using-git-worktrees` ve otomatik execute
> zinciri UYGULANMAZ. Adımlar `- [ ]` ile izlenir.
> **Plan katmanı (P2):** karar · invariant · arayüz imzası · test adı + ne kanıtladığı · komut · kabul.
> Fonksiyon gövdesi YOKTUR; mekanik yürütmenin işidir.

**Amaç:** Sektör paketinin kuralları modele bağlayıcı olarak gitsin (zorunlu blok), kalıplar gönderi türüne göre
seçilsin (seçmeli dağarcık), model her basılan kural için karar beyan etsin (`kural_uyumu`) ve kullanıcı gönderiyi
onaylarken çiğnenen kuralı görsün (K-A'nın bağlayıcı koşulu). Paketin 2. sürümü yeni tam koşuyla üretilip sınavdan
geçtikten sonra etkinleşsin.

**Mimari:** Katmanlı, şema-önce. (1) Paket şeması sürüme duyarlı olur; canlıdaki 1. sürüm okunmaya devam eder.
(2) Render işlevleri basılan metinle birlikte basılan bağlayıcı kural haritasını (`Z*`, `G*`) döner; başlık çağrısı
bu haritayı tutar, modelin beyanını ona karşı deterministik bir kapıdan geçirir. (3) Beyan gönderi satırına yazılır;
tek bir biçimleyici onu arayüze ve Telegram onay mesajına basar. Paketsiz yol bayt-bayt aynı kalır.

**Teknoloji:** FastAPI + asyncpg (Python 3, pytest), PostgreSQL (`social` şeması, numaralı migration'lar),
Next.js 14 (frontend, test koşucusu YOK — `lint` + `build`), n8n (Telegram onay akışı), Anthropic API
(`claude-opus-4-6`, başlık üretimi), sektör paketi işletim hattı CLI'si (`scripts/sector_pipeline_cli.py`).

**Spec:** `docs/specs/2026-09-25-paket-zorunlu-kurallar-ve-gonderi-turu.md` (spec-approved, Codex 5 tur).
Bağlam: `docs/active/sektor-bilgi-paketi-plan2/TASK.md` (Open Problems madde 0) · yürütülen hat planı
`docs/plans/2026-08-27-sektor-bilgi-paketi-plan2.md` + arayüz eki · dağıtım runbook'u `docs/plans/PLAN2-DAGITIM-RUNBOOK.md`.

## Global Constraints (spec'ten birebir)

- Paketsiz yol bayt-bayt aynı: `tests/prompt_regression/fixtures/` altındaki mevcut 13 dosya DEĞİŞMEZ (yeni paketli
  golden'lar eklenebilir); Tier 1 `_SYSTEM_RULES` DEĞİŞMEZ.
- Tür sözlüğü `gonderi_turu ∈ {satis, hizmet, bilgi, kutlama, anma}`. Gün kaydı eşlemesi: `ticari-firsat→satis` ·
  `karma→satis` · `kutlama→kutlama` · `anma→anma`. Etiketsiz kanca `satis` sayılır.
- `kural_uyumu` kararı kapalı küme: `uyuldu` · `istek-geregi-cignendi` (+ isteğin tetikleyen parçası + üretilen cümle) ·
  `uygulanamadi` (+ neden). Bağlayıcı küme = o çağrıda BASILAN her bağlayıcı kural (`Z*` + `G*`).
- Kapı (deterministik): (i) basılan kimliklerin TAMAMI var, (ii) bilinmeyen kimlik yok, (iii) karar kapalı kümeden,
  (iv) `uyuldu` dışındaki her kararın kanıt alanları dolu — biri düşerse üretim GEÇERSİZ.
- Tek öncelik sırası: kullanıcının açık isteği > gerçek ürün bilgisi = marka DNA'sı (yasak kelimeler dâhil) >
  paket zorunlu kuralları > genel yazım/teknik-spec kuralları > şablon varsayılanları. Öncelik satırının metni spec §3.3-A'dan BİREBİR.
- CTA kaynak sırası: kullanıcı isteği > gün kaydı CTA'sı (tür izin veriyorsa) > paket CTA'sı (tür + kanal) >
  şablonun "link yoksa yönlendirme satırı ekleme" kuralı > hiç (şablon kuralı yalnız link satırı için).
- Gönderi satırı: `gonderi_turu TEXT NULL` · `kural_uyumu JSONB NOT NULL DEFAULT '[]'`. Damga tablosu
  (`social.generation_stamps`) DEĞİŞMEZ (032'nin kapalı kolon imzası). Paketsiz üretimde `kural_uyumu = []`.
  Kapıdan geçmiş beyan makbuz kimliğiyle sunucuda ayrı tabloda tutulur ve kayıtta oradan kopyalanır (D5 — spec §3.8
  "iki şema değişikliği" sayımından gerekçeli SAPMA; damga tablosu yine değişmez).
- Şema sürümü: 1 = bugünkü dokuz alan; 2 = dokuz + `sektor_gercekleri` (liste alanı; boş olmayan liste,
  `içerik-önerilmez` kabul). Mevcut dokuz alanın adı ve tipi DEĞİŞMEZ.
- Sıra: şema-2 okuyucusu canlıda olmadan 2. sürüm ETKİNLEŞMEZ. Geri dönüş: spec §3.9 tabanı (şema-2 okuyucusu) bu
  planın kısıtıyla (D7) YÜKSELİR — dönüş hedefi ya canlıya alınan sürüm (Task 21) ya da bu planın öncesi olabilir;
  ara commit'ler YASAK hedeftir; paketli yol açıkken plan öncesine dönmeden önce paket `deaktive-et` ile indirilir ve
  yayımlanmamış paketli gönderi kalmaz (D7). Tabanın altı sessiz değildir (`package_read_error` → yönetici bildirimi).
- K-119 satırları kaldırılır; kutlama/anma varsayılanı ("satış çağrısı kullanma") kullanıcı açıkça istemedikçe sürer.
- Kullanıcıya tür seçtirilmez; şablon ızgarası açılmaz; sektör şablonu yok (K-F).
- Ücretli her koşudan önce tutar + Eray'ın AÇIK onayı. Ölçülmüş: sentez 1,77–2,09 USD/koşu ve denetim 18,5–21,5 dk
  (TASK Current Status, 2026-09-23 iki canlı koşu), Katman-2 0,273 USD (TASK, `kosu-23e19d03` aktivasyon kaydı);
  sınav tekrarı ≈1,6 USD (**tahmin** — spec §4: 25 Eylül koşusu 40 çağrı 1,5781 USD).
- Push, `main`'e birleştirme, canlı migration, Coolify dağıtımı, n8n canlı değişikliği, paket onayı/etkinleştirmesi:
  her biri Eray'ın ayrı onayıyla. Coolify dağıtımı elle (Eray düğmeye basar).
- n8n: depo JSON'u körlemesine import edilmez; canlı düğümle düğüm bazında karşılaştırılır, yalnız değişen düğüm yüklenir, geri okunarak doğrulanır.

## Review Focus (spec'in ima ettiği ama görev testlerinin kolayca kaçıracağı beş durum)

1. **Paketli marka + pakette kaydı olmayan özel gün + ürün yok** (bugün 1. sürümde 18 Mart böyle) → tür `None`,
   kaynak `model`; hiçbir `G*` basılmaz; kapı yalnız `Z*` kümesini ister; takvimin bugünkü gün satırı sürer.
   Test: Task 9 `test_day_without_package_entry_keeps_calendar_line_and_prints_no_g_ids`.
2. **Model çıktısı bozuk/kesik ya da model hiç yanıt vermiyor** (JSON onarılır ama `kural_uyumu` eksik/yarım; API
   anahtarı yok; çağrı istisna atıyor) → paketli yolda açık hata, yedek (fallback) metin DÖNMEZ, makbuz yazılmaz.
   Test: Task 10 `test_packaged_failures_never_fall_back_generated`.
3. **Kullanıcı başlığı düzenleyip kaydeder** → beyan üretim anındaki metne aittir; kayıt reddedilmez, gösterim
   bunu söyler. Test: Task 14 `test_disclosure_labels_generation_time`.
4. **Karttan tek tıkla yayın, çiğnenen kural var** → onay penceresi beyanı gösterir; iptal → yayın isteği HİÇ gitmez.
   Doğrulama: Task 15 elle akış kontrolü (frontend'de test koşucusu yok — beyan edildi).
5. **Telegram fotoğraflı onay + uzun beyan + Markdown özel karakterli başlık + çok platform + uzun video bağlantısı**
   → hiçbir mesaj sınırı aşmaz; `uyuldu` dışı kararlı HER kural adıyla, onay düğmeli mesajda ya da ondan önce görünür
   (sayaç YOK). Test: Task 14 `test_telegram_messages_name_every_rule_before_buttons_generated`.

---

## Plan düzeyi kararlar (teknik; Codex review'ı sınar)

- **D1 — İki aşama, tek plan; sıra.** Aşama A (Task 1–17) kodu yerelde bitirir. Aşama B (Task 18–22):
  ölçüt dosyası → yeni tam koşu → 2. sürüm taslağı → sınav → canlıya alma → etkinleştirme. İşletim hattı CLI'si
  çalışma ağacından koşar (TASK: "CLI çalışma ağacından koşar"), sınav aracı `generate_captions`'ı yerelden çağırır →
  koşu ve sınav dağıtım GEREKTİRMEZ. **2. sürüm TASLAĞI dağıtımdan önce yazılır:** üretimdeki paket okuyucularının
  hepsi yalnız `status = 'active'` satırı okur — `app/services/sector_packages.py::resolve_package_context`,
  `app/routers/brands.py` (paket modu sorgusu), `app/routers/sectors.py::_SUB_SECTOR_CANDIDATES_SQL` (grep
  `FROM social.sector_packages`, bu oturum) — taslak onlara görünmez. Spec §3.9'un "önce kod, sonra yazımı/aktivasyonu" sırası bu yüzden AKTİVASYON için bağlayıcı okunur;
  aktivasyon (Task 22) canlıya almadan (Task 21) SONRADIR. Alternatif (önce canlıya al, sonra koş) reddedildi:
  sınav tasarımı düzeltme isterse ikinci bir canlıya alma gerekirdi; bugün pakete atanmış marka 0 (ölçüldü) olduğu
  için erken dağıtımın getirisi yok.
- **D2 — Şema sürümü değişmez olarak kurulur.** Yaprak modülde (`app/services/sector_content_schema.py`)
  `SCHEMA_FIELDS: Mapping[int, frozenset[str]]`, `CURRENT_SCHEMA_VERSION = 2`; `structural_errors(content, *,
  schema_version: int)` **varsayılansız, anahtar-yalnız** → her çağrı yeri sürümü açıkça seçer (saklı paket →
  satırın sürümü; yeni aday → güncel sürüm). Sınıf kapanışı ayrıca AST tabanlı üretilmiş çağrı-yeri testiyle
  (Task 3). Reddedilen: sürümü içerikten çıkarmak — 1. sürüm satırına sızan onuncu alanı 2. sürüm sayar, kapalı
  kümeyi deler.
- **D3 — Tek çağrı bağlamı, tek kaynak.** Render işlevleri `RenderedRules(text, rules)` döner; `rules` basım
  sırasıyla `(kimlik, kural metni)` çiftleridir. Bağlayıcı bir satır ancak kimlik atayan tek yardımcıdan geçerek
  basılır. `generate_captions` iki katmanın haritalarının birleşimini tutar; kapı bu birleşime karşı koşar.
  Reddedilen: ayrı bir "kimlik kümesini türet" işlevi — basan ve denetleyen iki ölçü olurdu (K-01b sınıfı).
- **D4 — Katman yerleşimi.** Zorunlu blok Tier 2'de (marka + paket sürümü + hizmet listesi + kanallara sabit →
  önbellek anahtarı korunur). Tür satırı, seçmeli dağarcık ve özel gün satırları Tier 3'te (türe bağlı).
- **D5 — Beyan sunucuda, makbuzla saklanır (Codex Tur 1 F3 sonrası).** Metin `/posts/generate-caption`'da üretilir,
  gönderi `/posts/generate` ve `/posts/generate-short-video-stage1`'de kaydedilir. Kapı başlık çağrısında koşar
  (kimlik tamlığı yalnız orada bilinir); kapıdan geçen beyan (`gonderi_turu`, zenginleştirilmiş `kural_uyumu`,
  varsa `tur_degisikligi`) makbuzla AYNI transaction'da yeni `social.generation_rule_reports` tablosuna yazılır
  (anahtar = makbuz kimliği). Kayıtta makbuz tüketilince beyan bu tablodan okunup gönderi satırına KOPYALANIR;
  istemci beyan TAŞIMAZ (yanıttaki `kural_ifsa` yalnız gösterim içindir). Böylece kısmi/eksik beyan kayda ulaşamaz.
  **Spec sapması (teknik, gerekçeli):** spec §3.8 "İKİ şema değişikliği" sayar; bu, üçüncü bir veritabanı nesnesi
  ekler. §3.12'nin "damga tablosu değişmez" hükmü KORUNUR: ayrı tablo, yabancı anahtar YOK (037 emsali —
  `generation_stamps`'e bağımlı kısıt 032'nin geri alma yolunu durdururdu; `generation_stamps`'e kolon eklemek
  032'nin kapalı kolon imzasını — `032_sector_packages.sql`, "generation_stamps kolon imzası" — bozardı).
  Reddedilen: istemci taşıması + şekil denetimi (kısmi kaybı göremez — Tur 1 F3), HMAC imzalı beyan (yeni sır
  yönetimi + Coolify'da elle adım; saklamanın sağladığını daha pahalıya sağlar).
- **D6 — Paketli yolda yedek metin YOK (Tur 1 F6).** Paketli çağrıda HER başarısızlık — API anahtarı yok, model
  çağrısı istisnası, ayrıştırma hatası, kapı düşüşü, makbuz/beyan yazım hatası — `PackagedGenerationError` olur;
  uç 502 + Türkçe ileti döner, makbuz ve beyan satırı yazılmaz. Paketsiz yolun bugünkü yedeği (kullanıcı isteğini
  yankılayan metin) bayt-bayt aynı kalır. Otomatik yeniden deneme YOK (her deneme ücretli; düşme sıklığı sınavda
  ölçülür).
- **D7 — Veri katmanı değişmezi.** `CHECK (package_id IS NULL OR jsonb_array_length(kural_uyumu) > 0)`. Bugün
  paketli gönderi 0/81, makbuz 0, atanmış marka 0 (ölçüldü, 2026-09-25 bu oturum, `psql` salt-okuma:
  `SELECT count(*) FILTER (WHERE package_id IS NOT NULL), count(*) FROM social.posts` → `0|81`;
  `SELECT count(*) FROM social.generation_stamps` → `0`; `SELECT count(*) FROM social.brands WHERE sub_sector_id
  IS NOT NULL` → `0`) → kısıt mevcut satırı ihlal etmez; migration yine de önce sayar ve ihlal varsa DURUR.
  **Geri dönüşe etkisi (Tur 1 F2):** 038 uygulandıktan sonra paketli gönderi yazıp beyan yazmayan HER kod sürümü
  (bu planın ara commit'leri; paketli yol açıksa bu planın öncesi de) paketli kaydı kısıtla reddettirir. Bu yüzden
  dönüş hedefi = Task 21'de canlıya alınan sürüm; daha eskiye dönmek gerekirse ÖNCE aktif paket `deaktive-et` (K-38)
  ile indirilir (markalar paketsiz yola düşer, `package_id` boş kalır), sonra kod geri alınır. 038 geri alması yalnız
  beyan verisi yoksa mümkündür. **Tur 2 N1:** ifşa bilmeyen (plan öncesi) arayüz ve n8n, önceden kaydedilmiş paketli
  gönderilerin beyanını göstermez; bu yüzden plan öncesine dönüş ek bir kapıya bağlıdır — `SELECT count(*) FROM
  social.posts WHERE package_id IS NOT NULL AND status <> 'published'` sıfır olmalı; değilse bu gönderiler ifşa bilen
  sürümde sonuçlandırılır (yayın ya da ret, Eray kararıyla), sonra dönülür.
- **D8 — İfşa (Tur 1 F7, Tur 2 N2/N3 sonrası).** Tek biçimleyici (`app/services/rule_disclosure.py`): arayüz için
  tam satırlar + Telegram için SIRALI mesaj listesi. Telegram tarafının tamamı (başlık önizlemesi, platformlar, tür,
  video bağlantısı, ifşa, Markdown kaçışı) backend'de kurulur; n8n listeyi SIRAYLA gönderir, kendisi biçimlemez.
  **Telegram invariantı:** onay düğmeleri YALNIZ listenin son mesajındadır; `istek-geregi-cignendi` ya da
  `uygulanamadi` kararlı HER kural, adıyla (kural metni; gerekirse kısaltılmış ama adı taşıyan başı) düğmeli mesajda
  ya da ondan ÖNCEKİ bir mesajda görünür — sayaca indirgeme YOK (spec §3.12 "kural adıyla gösterilir"); her mesaj
  kendi Telegram sınırında (fotoğraf açıklaması / metin — belge değerleri). Gösterim yüzeyleri: sihirbazın metin
  adımı, önizleme, kısa video "Önizleme & Onay" adımı, kütüphane ayrıntı penceresi, takvim penceresi, Telegram.
  Ayrıntı görünümü açılmadan yayın/zamanlama/onaya gönderme başlatan HER tek tık eylemi, `uyuldu` dışı kararlı
  (çiğnenen YA DA uygulanamayan) bir kural varsa önce beyan penceresini açar. Beyan "üretim anındaki metne aittir"
  etiketiyle gösterilir; metin düzenleme takibi YOKTUR (kapsam dışı).
- **D9 — Notun saymadığı kardeş satır.** Ticari gün ton ipucu (`app/core/prompt_builder.py::_SPECIAL_DAY_TONE_HINTS`
  `"commercial"`: "Promosyon/satış dili YASAK…") madde 6'daki "kutlama postudur" satırıyla AYNI sınıftır: paketli
  yolda tür `satis`/`hizmet`/`bilgi` iken satış yasağı cümleleri basılmaz (ton cümlesi ve `cta_url` link kuralı
  kalır). Kapatılmazsa Black Friday düzeltmesi yarım kalır.
- **D10 — Paketli çağrıda `max_tokens` tavanı 4096.** Tavan, ölçüm iddiası DEĞİL. Ölçülen: 25 Eylül sınavı paketli
  çıktı 472–717 jeton (ort. 594; tek platform; `olcum/sonuc-sinav/b-sonuc.json` `usage.output`, 20 çağrı) — beyan
  (en çok ~16 satır, **tahmin**) ve çok platform bunu artırır. Paketsiz çağrı 2048'de kalır. Gerçek kullanım sınavda
  (Task 20) ölçülür.
- **D11 — Fikir yüzeyi.** İki blok basılır, beyan İSTENMEZ (fikir yayınlanmaz; seçilen fikir başlık çağrısında
  kapıdan geçer). Zorunlu bloğun beyan cümlesi yüzeye göre basılır.
- **D12 — Şema-2 içerik gramerleri (yaprakta, yazım kapısında denetlenir).** Kanca tür etiketi: öğe sonunda
  `(tür: <değer>)`, değer tür sözlüğünden; etiketsiz = `satis`. `ton_ve_dil` satır satır okunur: her satır bir
  kural; `ton (yumuşak):` önekli satır yumuşak yönlendirmedir (K-118), kimlik almaz. Tek paragraf (1. sürüm) =
  tek kural.
- **D13 — Paketli markada makbuz zorunlu (Tur 1 F1).** Bugün `sector_packages.py::resolve_persist_stamp` makbuzsuz
  ya da geçersiz makbuzlu isteği olay yazıp `(None, None)` ile geçirir ("üretim bloklanmaz", K-07). K-A'nın koşulu
  (spec §3.12) bunu paketli yolda kapatır: makbuz BEKLENEN içerik türünde (`receipt_expected`) ve markanın aktif
  paketi OKUNABİLİRKEN makbuz yoksa/geçersizse/tüketilmişse kayıt REDDEDİLİR (422, gönderi satırı doğmaz, olay yine
  yazılır — geri alınan transaction'ın DIŞINDA). "Okunabilir" ölçüsü okuyucuyla TEKTİR (`resolve_package_context`'in
  satır doğrulaması ortak saf yardımcıya çıkarılır; K-01b). Paket okunamıyorsa (okuyucu da paketsiz yola düşer)
  makbuzsuz kayıt bugünkü gibi geçer. Makbuz beklenmeyen içerik türü (`RECEIPTLESS_CONTENT_TYPES` — alıntı) ve
  metni kullanıcının yazdığı elle oluşturma ucu (`posts.py::create_post`) kapsam dışıdır: model metni yoktur.
  **Sınıfın tamamı (grep, bu oturum):** `generate_captions`'ın tek çağıranı `posts.py::generate_caption`; makbuzu
  tüketen iki uç `posts.py::generate_post` ve `short_video.py::run_short_video_stage1` — ikisi de Task 13'te. Diğer
  gönderi yazan yerler (`internal.py::trigger_autopost`, `avatar.py`, `trends.py`, `short_video.py` eski akışı,
  `posts.py::create_post`) başlık modelini paketle çağırmaz.
- **D14 — Tür değişikliği beyanı (Tur 1 F4).** Spec §3.2: gün kaydının türünü model değiştiremez, **kullanıcı isteği
  hariç** (K-A); ürün modunda istek anlatım/bilgi istiyorsa `bilgi`'ye çevrilir "ve çevirdiğini yaz". Çıktıda
  `gonderi_turu` koddan çözülen türden (`gun_kaydi`, `urun_varsayilan`) FARKLIYSA `tur_degisikligi =
  {istek_parcasi}` zorunludur; yoksa kapı düşer. Tutarlılık: gün türü `kutlama`/`anma` iken çıktı türü `satis` ise
  `G-satis-yok` satırı `istek-geregi-cignendi` olmak ZORUNDADIR. Kaynak `model` iken beş değerden biri, beyansız.

## Yürütme kuralları (her görevde geçerli)

- **İskelet önce, her testin kendi kırmızısı:** (1) modül/işlev iskeleti (`raise NotImplementedError`), (2) her test
  tek tek koşulup KENDİ kırmızısı görülür — modül yokken alınan toplu `ImportError` kırmızı SAYILMAZ, (3) gövde.
- **Mutasyon kanıtı yalnız YENİ kapıya:** her yeni kapı için ≥1 mutasyon (kapıyı söküp testin kırmızıya döndüğünü
  gör), dosya yedeğiyle geri al (`git checkout` commit'lenmemiş testi siler).
- **Üretilmiş matris:** "her X kimlik alır / her yol denetlenir" türü iddia `itertools.product` ile üretilen
  kümeyle kanıtlanır, elle seçilmiş örnekle değil.
- **Test komutu:** `cd apps/social/backend && .venv/bin/python -m pytest <yol> -q` (tam takımı alt-ajan test
  koşarken eşzamanlı başlatma — veritabanı paylaşılıyor).

## Dosya haritası

| Dosya | Sorumluluk | Görev |
|---|---|---|
| `app/services/sector_content_schema.py` | sürüme göre alan kümeleri, yapısal kapı, iki gramer | 1 |
| `app/services/sector_packages.py` | okuyucu + yazım kapısı sürüme göre; `resolve_post_type`; iki blok; gün satırları; kapı işlevleri | 2, 5–8, 10 |
| `app/services/sector_package_lifecycle.py` | `insert_draft` sürümü yazım kapısına geçirir | 2 |
| `app/services/sector_pipeline/{identity,engine,operator_decisions,synthesis,writeback}.py` + `scripts/sector_pipeline_cli.py` | pipeline şema-2 | 3 |
| `shared/contracts/research-contracts.pin.json` + dış depo `/root/otomaix-sosyal-medya-arastirmasi` | sözleşme + pin | 4 |
| `app/core/prompt_builder.py` | iki katman, tür satırı, ürün `Tür:` satırı, gün/ton satırları | 9 |
| `app/core/caption_generator.py` | kural haritası birleşimi, çıktı sözleşmesi, kapı, hata yolu | 9, 10 |
| `app/routers/posts.py` | ürün türü + hizmet listesi okuma; hata eşlemesi; makbuz + beyan saklama; kayıtta kopyalama; ifşa alanları | 9, 10, 13, 14 |
| `app/routers/ai.py` | fikir yüzeyi iki blok | 11 |
| `shared/db/migrations/038_posts_rule_compliance.sql` + `rollback/038_down.sql` | iki kolon + kısıtlar + beyan tablosu | 12 |
| `app/services/short_video.py` | stage-1 sonlandırmasında beyan kopyası | 13 |
| `app/services/rule_disclosure.py` (yeni) | tam ifşa + Telegram son metinleri | 14 |
| `app/routers/{calendar,internal}.py` | ifşa alanları | 14 |
| `apps/social/frontend/components/content/RuleDisclosure.tsx` (yeni) + sihirbaz/kütüphane/takvim sayfaları + `CaptionEditor` tipi | gösterim + kart yayın kapısı | 15 |
| `shared/n8n-workflows/telegram-content-approval.json` | "Mesaj Hazırla" düğümü | 16 |
| `docs/plans/PLAN2-DAGITIM-RUNBOOK.md` | 038 adımı, taban satırı, n8n adımı | 17 |
| `docs/active/sektor-bilgi-paketi-plan2/olcum/*` | `KALIBRASYON-2.md`, ölçüm aracı | 18, 20 |

---

# Aşama A — Kod (yerel; canlıya alma Aşama B'nin içinde)

### Task 1: Şema sürümüne duyarlı yaprak modül

**Amaç:** Alan kümesini satırın şema sürümüne bağlamak (spec §3.9) ve şema-2'nin iki içerik gramerini (D12) tek yerde tanımlamak.

**Dosyalar:**
- Modify: `apps/social/backend/app/services/sector_content_schema.py`
- Test: `apps/social/backend/tests/test_sector_content_schema_versions.py` (yeni)

**Arayüz (Produces):**
- `SCHEMA_FIELDS: Mapping[int, frozenset[str]]` — `1`: bugünkü dokuz alan; `2`: dokuz + `"sektor_gercekleri"`.
- `CURRENT_SCHEMA_VERSION: int = 2`; `POST_TYPES: tuple[str, ...] = ("satis", "hizmet", "bilgi", "kutlama", "anma")`.
- `LIST_FIELDS` güncel (şema-2) liste alanlarını taşır (`sektor_gercekleri` dâhil); `TEXT_FIELDS` değişmez.
- `structural_errors(content: Any, *, schema_version: int) -> list[str]` — anahtar-yalnız, VARSAYILANSIZ.
- `hook_type(item: str) -> tuple[str, str]` — `(kalıp metni, tür)`; etiketsiz → `satis`.
- `split_tone_lines(text: str) -> tuple[tuple[str, ...], tuple[str, ...]]` — `(kural satırları, yumuşak satırlar)`.

**Bağlayıcı invariantlar (seam: `sector_content_schema.py::structural_errors` ve `::_check_closed_field_set`):**
- Kapalı küme kontrolü `SCHEMA_FIELDS[schema_version]` ile yapılır; bilinmeyen sürüm → hata metni (istisna değil).
- 1. sürüm içerik 1. sürüm kuralıyla geçerli, 2. sürüm kuralıyla GEÇERSİZ (eksik alan); tersi de.
- `sektor_gercekleri` boş liste → hata; `["içerik-önerilmez"]` → geçerli (K-120).
- Kanca etiket değeri tür sözlüğü dışındaysa → yapısal hata (yalnız şema-2'de denetlenir; 1. sürüm içerikte etiket yok).
- Yaprak kuralı korunur: modül hiçbir `app.*` modülü import etmez (`tests/test_plan2_interface_contract.py::test_the_leaf_is_actually_a_leaf`).

**Testler (her biri kendi kırmızısıyla):**
- `test_schema_fields_closed_sets_per_version` — iki küme tam olarak beklenen alanlar; v2 = v1 ∪ {sektor_gercekleri}.
- `test_structural_errors_requires_explicit_schema_version` — anahtarsız çağrı `TypeError`.
- `test_v1_content_valid_v1_invalid_v2_and_reverse` — iki yönlü ayrım.
- `test_unknown_schema_version_is_an_error_not_a_pass` — `schema_version=3` hata listesi döner.
- `test_sektor_gercekleri_empty_rejected_deliberately_empty_accepted`.
- `test_hook_type_grammar_generated_matrix` — `itertools.product(etiket var/yok, değer ∈ POST_TYPES ∪ {bilinmeyen}, boşluk varyantları)`; geçerli değer döner, bilinmeyen değer yapısal hata üretir.
- `test_split_tone_lines_single_paragraph_is_one_rule` + `test_split_tone_lines_soft_prefix`.

**Adımlar:**
- [ ] İskelet (yeni adlar `NotImplementedError`). `structural_errors` imzası değişince KIRILAN çağrı yerleri ve testler BEKLENEN kırmızıdır: listele, Task 2/3'e devret (Task 3'ün atomik commit'ine kadar takım yeşil DEĞİLDİR; bu görevin kendi testleri ayrıca koşar).
- [ ] Testleri tek tek yaz, her birinin kırmızısını gör.
- [ ] Gövdeleri yaz; `pytest tests/test_sector_content_schema_versions.py -q` → PASS.
- [ ] Mutasyon: kapalı küme kontrolünü sürümden bağımsız yap → `test_v1_content_valid_v1_invalid_v2_and_reverse` kırmızı.
- [ ] Commit YOK — aşağıdaki işaret.

**Not:** İmza değişikliği bu görevde çağrı yerlerini kırar; Task 2 ve Task 3 AYNI oturumda ardından gelir. Korumasız
ara commit yasağı gereği bu görevin işi Task 3'ün atomik commit'inde iner.

**status:** merged-into T3

**Kabul:** yeni test dosyası PASS; yaprak testi PASS.

### Task 2: Saklı paket okunur ve yazılır — sürüme göre

**Amaç:** Okuyucu ve yazım kapısı satırın şema sürümüyle denetler; canlı 1. sürüm paket yeni kodla okunur; geri dönüş tabanı ölçülür (spec §3.9, §4).

**Dosyalar:**
- Modify: `apps/social/backend/app/services/sector_packages.py` (`validate_package_content`, `resolve_package_context`)
- Modify: `apps/social/backend/app/services/sector_package_lifecycle.py` (`insert_draft` → yazım kapısı çağrısı)
- Test: `apps/social/backend/tests/test_package_schema_versions_io.py` (yeni)

**Arayüz:**
- Consumes: `structural_errors(content, *, schema_version)` (Task 1).
- Produces: `validate_package_content(content, *, schema_version: int, banned_brand_names, holiday_keys) -> ValidationResult`.
  `resolve_package_context(db, brand)` imzası DEĞİŞMEZ; sorgusu `p.schema_version`'ı da seçer. `SectorPackageContext` DEĞİŞMEZ.

**Bağlayıcı invariantlar:**
- `sector_packages.py::resolve_package_context` satırın kendi `schema_version`'ıyla doğrular; doğrulama düşerse
  bugünkü yol aynen: paketsiz yol + `package_read_error` olayı (`reason: structural`).
- `sector_package_lifecycle.py::insert_draft` aldığı `schema_version`'ı yazım kapısına geçirir (içerik ↔ sürüm
  uyuşmazlığı taslağa YAZILAMAZ — bugün eşleştirilmiyor, Codex ön-analizi).
- `package_read_error ∈ ADMIN_NOTIFIED_EVENTS` (`app/services/package_events.py`) — taban altının sessiz olmadığı buna dayanır.

**Testler:**
- `test_live_v1_row_reads_under_new_code` — şema-1 satırı (bugünkü dokuz alan) → bağlam döner, olay YOK.
- `test_v2_row_reads_under_new_code` — şema-2 satırı → bağlam döner.
- `test_v2_content_under_v1_rules_falls_back_with_read_error` — geri dönüş tabanı kanıtı (spec §4): `schema_version=1`
  satırında `sektor_gercekleri` → `None` + `package_read_error` olayı yazılır; olay türü `ADMIN_NOTIFIED_EVENTS` içinde.
- `test_insert_draft_rejects_content_schema_mismatch_generated` — `itertools.product(içerik ∈ {v1, v2}, sürüm ∈ {1, 2})`: uyuşmayan iki kombinasyon reddedilir, uyuşan ikisi yazılır.
- Mevcut `tests/test_package_lifecycle.py` ve `tests/test_sector_packages_service.py` çağrıları yeni anahtarla güncellenir; davranış testleri aynen geçer.

**Adımlar:**
- [ ] Testleri tek tek yaz → kırmızı.
- [ ] `resolve_package_context` sorgusu + doğrulama; `validate_package_content` + `insert_draft` geçişi.
- [ ] `pytest tests/test_package_schema_versions_io.py tests/test_package_lifecycle.py tests/test_sector_packages_service.py tests/test_package_stamp_and_events.py -q` → PASS.
- [ ] Mutasyon: okuyucuda sürümü sabit `CURRENT_SCHEMA_VERSION` yap → `test_live_v1_row_reads_under_new_code` kırmızı.
- [ ] Commit YOK — Task 1 ile aynı gerekçe; iş Task 3'ün atomik commit'inde iner.

**status:** merged-into T3

**Kabul:** dört yeni test PASS; mevcut paket testleri PASS.

### Task 3: Pipeline şema-2 ile yazar — çağrı-yeri matrisi

**Amaç:** Yeni adaylar güncel sürümle (2), saklı aktif paket kendi sürümüyle denetlenir; taslak `schema_version = 2` yazılır; hiçbir çağrı yeri sürümü sessizce varsaymaz.

**Dosyalar:**
- Modify: `app/services/sector_pipeline/identity.py` (`decision_units`, `check_unit_integrity`; açılış hükmündeki "`schema_version` ARTIRILMAZ" cümlesi spec 2026-09-25 §3.9'a atıfla değiştirilir)
- Modify: `app/services/sector_pipeline/engine.py` (`_sema_ve_boyut`, nihai yazım kapısı `structural_errors(nihai, …)`)
- Modify: `app/services/sector_pipeline/operator_decisions.py` (`uygula` içindeki kapılar)
- Modify: `app/services/sector_pipeline/synthesis.py` (aday doğrulayıcısı)
- Modify: `app/services/sector_pipeline/writeback.py` (`SCHEMA_SURUMU = 2`; docstring spec §3.9'a atıfla)
- Modify: `scripts/sector_pipeline_cli.py` (`_aktif_paket` → `decision_units(..., schema_version=satir["schema_version"])`)
- Test: `tests/test_schema_version_call_sites.py` (yeni) + mevcut `tests/test_unit_identity.py`, `tests/test_operator_decisions.py`, `tests/test_policy_engine_checks.py`, `tests/test_synthesis.py`, `tests/test_pipeline_writeback.py`, `tests/test_pipeline_cli.py`, `tests/test_plan2_interface_contract.py` güncellemeleri

**Arayüz:**
- Produces: `identity.decision_units(content, decision_log, *, schema_version: int)`; `identity.check_unit_integrity(content, decision_log, *, schema_version: int)`.

**Bağlayıcı invariantlar (sınıflandırma tablosu görevin commit mesajına yazılır):**
- Saklı paket (DB satırı) → satırın sürümü: `scripts/sector_pipeline_cli.py::_aktif_paket`, `sector_packages.py::resolve_package_context`, `sector_package_lifecycle.py::insert_draft`.
- Yeni aday → `CURRENT_SCHEMA_VERSION`: `engine.py::_sema_ve_boyut`, engine nihai kapısı, `operator_decisions.py::uygula`, `synthesis.py` aday doğrulaması.
- Operatör yolu `sektor_gercekleri`'ni `LIST_FIELDS` üzerinden tanır: `ekle` (alan adayda varsa) ve `degistir` (ör. `içerik-önerilmez` birimi); alan adayda YOKSA `ekle` reddedilir (aday zaten güncel şemayla yapısal kapıdan geçmek zorunda — eksik alan motorda yapısal sebep olur, operatör yolu açılmaz).
- Sentez eki (EK-L) alan listelerini yapraktan üretir → güncel şema kendiliğinden görünür (`synthesis.py` EK-L işlevi değişmez).

**Testler:**
- `test_every_schema_gate_call_passes_explicit_version` — AST ile `app/` + `scripts/` altındaki HER `structural_errors(`, `decision_units(`, `check_unit_integrity(`, `validate_package_content(` çağrısı `schema_version=` anahtarını taşır; çağrı listesi KAVRAMDAN (ad kümesi) türetilir, dosya listesi `rglob`'dan.
- `test_active_v1_package_units_under_v2_code` — CLI `_aktif_paket` bir v1 satırından birim görüntüsü üretir (hata yok).
- `test_operator_ekle_degistir_cikar_sektor_gercekleri_on_v2_candidate` (üç işlem; `cikar` son öğeyi düşürürse yapısal kapı boş listeyi reddeder) + `test_operator_ekle_missing_new_field_rejected`.
- `test_writeback_writes_schema_version_2`.
- `test_plan2_interface_contract.py` içinde şema-1'i sabitleyen pin varsa yeni hükümle güncellenir (değişen pinler commit mesajında listelenir).

**Adımlar:**
- [ ] Çağrı yerlerini `grep -rn "structural_errors(\|decision_units(\|check_unit_integrity(\|validate_package_content(" app scripts` ile say, tabloyu yaz.
- [ ] AST testi → kırmızı (Task 1 sonrası anahtarsız çağrılar var).
- [ ] Her çağrı yerini sınıfına göre güncelle; kalan testleri yaz → kırmızı → yeşil.
- [ ] `pytest tests/test_schema_version_call_sites.py tests/test_unit_identity.py tests/test_operator_decisions.py tests/test_policy_engine_checks.py tests/test_policy_engine_outcome.py tests/test_synthesis.py tests/test_pipeline_writeback.py tests/test_pipeline_cli.py tests/test_pipeline_runs.py tests/test_plan2_interface_contract.py -q` → PASS.
- [ ] Mutasyon: CLI `_aktif_paket`'te sürümü `CURRENT_SCHEMA_VERSION` yap → `test_active_v1_package_units_under_v2_code` kırmızı.
- [ ] Commit (Task 1–3 tek atomik commit; mesaj gövdesinde çağrı-yeri sınıflandırma tablosu): `feat(sektor): read packages by their schema version, write schema 2`

**Kabul:** AST testi PASS; Task 1–3 testleri + listelenen mevcut dosyalar PASS.

### Task 4: Dış depo sözleşmeleri ve pin

**Amaç:** Sentez/denetçi sözleşmesi ve şablon `sektor_gercekleri` alanını ve kanca tür etiketini tanır (spec §3.9: "sentez sözleşmesi ve şablon aynı adı alır (dış depo commit + pin)").

**Dosyalar:**
- Modify (dış depo `/root/otomaix-sosyal-medya-arastirmasi`): `_SABLON.md`, `hakem-sentez-gorevi.md`, `hakem-denetci-gorevi.md` (alan listesinin geçtiği yerler — pinli üç dosyanın üçü de bugün `yasaklar_ve_hassasiyetler`'i anıyor; ölçüm: `grep -ln yasaklar_ve_hassasiyetler /root/otomaix-sosyal-medya-arastirmasi/*.md`)
- Modify: `shared/contracts/research-contracts.pin.json` (commit + üç sha256)
- Test: `apps/social/backend/tests/test_contract_pin.py` (mevcut)

**Bağlayıcı invariantlar:**
- `sektor_gercekleri` = kaynaklı sektör doğruları; kaynaksız doğru EKLENMEZ (TASK madde 11a); zorunlu blokta basılır.
- Kanca öğesi isteğe bağlı `(tür: <değer>)` soneki taşır (D12); etiketsiz = `satis`.
- Pin dışı dosyalar (mimari notlar vb.) bu görevde değişmez.

**Adımlar:**
- [ ] Üç dosyada değişikliği yaz; dış depoda commit (`docs(contracts): add sektor_gercekleri and the hook type tag`).
- [ ] Pin'i yeni commit + sha256'larla güncelle.
- [ ] `pytest tests/test_contract_pin.py -q` → PASS; CLI pin kapısı: `.venv/bin/python scripts/sector_pipeline_cli.py --help` (pin okunur, hata yok).
- [ ] Commit: `chore(contracts): move the pin to the schema-2 research contracts`

**Kabul:** pin testi PASS; dış depo commit sha'sı pin'de.

### Task 5: Gönderi türü çözümleme

**Amaç:** Türü koddan çözmek (spec §3.1, §3.2, K-G).

**Dosyalar:**
- Modify: `apps/social/backend/app/services/sector_packages.py`
- Test: `apps/social/backend/tests/test_post_type_resolution.py` (yeni)

**Arayüz (Produces):**
- `@dataclass(frozen=True) class PostTypeResolution: tur: str | None; kaynak: Literal["gun_kaydi", "urun_varsayilan", "model"]`
- `resolve_post_type(day_entry: Mapping | None, product: Mapping | None) -> PostTypeResolution`
- `DAY_TYPE_TO_POST_TYPE: Mapping[str, str]` (katlanmış anahtarlar).

**Bağlayıcı invariantlar:**
- Öncelik: eşleşen gün kaydı > ürün kaydı > model. Gün kaydı `match_special_day` ile bulunur (tek eşleşme ölçüsü, K-01b) — çağıran geçirir.
- `product.type`: `product→satis`, `service→hizmet`. `brand_products.type` kolonu var (ölçüldü); ürün sözlüğünde `type` yoksa `ValueError` (sessiz varsayılan YOK — çağıran türü okumak zorunda).
- Eşlemede olmayan gün türü → `ValueError` (içerik kusuru sessizce `model`e düşmez). Canlı 1. sürümdeki değerler: `karma` 9 · `kutlama` 2 · `ticari-firsat` 5 — hepsi eşlemede (ölçüm, bu oturum: `SELECT e.value->>'tur', count(*) FROM social.sector_packages p, jsonb_each(p.content->'ozel_gun') e WHERE p.status='active' GROUP BY 1`).

**Testler:**
- `test_resolution_matrix_generated` — `itertools.product(gün ∈ {None, ticari-firsat, karma, kutlama, anma}, ürün ∈ {None, product, service})`: 15 kombinasyonun her biri beklenen `(tur, kaynak)`.
- `test_unknown_day_type_raises` · `test_product_without_type_raises` · `test_day_type_folding` (büyük harf/Türkçe harf varyantları).

**Adımlar:** iskelet → testler tek tek kırmızı → gövde → `pytest tests/test_post_type_resolution.py -q` PASS → mutasyon (öncelik sırasını ters çevir → matris kırmızı) → commit `feat(sektor): resolve the post type in code`.

**Kabul:** matris 15/15; hata testleri PASS.

### Task 6: Zorunlu blok ve `Z*` kimlikleri

**Amaç:** Paketin kurallarını genel yazım kurallarının üstünde, kullanıcı isteği/ürün bilgisi/marka DNA'sının altında tek blokta basmak (spec §3.3-A, §3.11).

**Dosyalar:**
- Modify: `apps/social/backend/app/services/sector_packages.py` (YENİ işlev eklenir; eski `render_package_block` +
  `USAGE_INSTRUCTION` son çağıranı değişene kadar DURUR — kaldırma Task 11'de; ara commit'ler yeşil kalır)
- Test: `apps/social/backend/tests/test_mandatory_block.py` (yeni)

**Arayüz (Produces):**
- `@dataclass(frozen=True) class RenderedRules: text: str; rules: tuple[tuple[str, str], ...]`
- `render_mandatory_block(context: SectorPackageContext, *, surface: Literal["caption", "idea"], channels: Any, services: Sequence[str]) -> RenderedRules`

**Bağlayıcı invariantlar (seam: `sector_packages.py::render_mandatory_block`):**
- Başlık `--- SEKTÖR PAKETİ · ZORUNLU KURALLAR (<alt sektör>) ---`. Basım sırası: kapsam + kapsam kuralı (spec
  §3.3-A metni: kapsam dışı üründe paketin kalıpları uygulanmaz; `kural_uyumu`'nda bu kuralın satırına `uygulanamadi`
  + neden "ürün kapsam dışı: <ürün>") → `ton_ve_dil`
  kural satırları (`split_tone_lines`; yumuşak satırlar "Ton (yumuşak yönlendirme)" etiketiyle, kimliksiz) →
  `sektor_gercekleri` (varsa) → `yasaklar_ve_hassasiyetler` → "ürün veya marka bilgisiyle çelişen kalıbı kullanma" →
  "markanın sahip olmadığı kanalı VEYA HİZMETİ önerme" + kanal listesi satırı + hizmet listesi satırı (olgu, kimliksiz)
  → öncelik satırı (spec §3.3-A birebir, kimliksiz) → tek öncelik sırası satırı.
- Her bağlayıcı satır `Z<n>: <kural>` biçiminde, `n` basım sırasıyla 1'den; bağlayıcı satır yalnız kimlik atayan tek
  yardımcıdan geçerek basılır. `içerik-önerilmez` öğesi kural olarak BASILMAZ.
- Beyan cümlesi ("…`kural_uyumu`'nda 'istek gereği çiğnendi' diye işaretle") ve kapsam kuralının beyan kısmı yalnız
  `surface="caption"`'da; `idea` yüzeyinde kurallar basılır, beyan cümlesi basılmaz (D11).
- Aynı girdi → aynı bayt (Katman-1 deterministikliği).

**Testler:**
- `test_every_binding_line_has_exactly_one_id_generated` — `itertools.product(ton ∈ {tek paragraf, satırlı+yumuşak}, sektor_gercekleri ∈ {yok, içerik-önerilmez, 2 öğe}, yasaklar ∈ {içerik-önerilmez, 5 öğe}, hizmet ∈ {[], [2 hizmet]}, kanal ∈ {None, {}, tam})`: metindeki `Z*` kimlikleri == `rules` anahtarları; her kural metni `rules`ta; kimliksiz bağlayıcı satır yok.
- `test_priority_line_verbatim_and_order` — öncelik satırı birebir; ürün bilgisi + marka DNA'sı paketin ÜSTÜNDE (N1).
- `test_idea_surface_omits_declaration_sentence` · `test_deliberately_empty_items_are_not_rules` · `test_mandatory_block_byte_stable`.
- `test_scope_rule_and_channel_service_lines_only_in_mandatory_block` — kapsam kuralı + kanal/hizmet listesi satırları yalnız bu blokta (spec §4 Birim).

**Adımlar:** iskelet → testler tek tek kırmızı → gövde → `pytest tests/test_mandatory_block.py tests/prompt_regression/ -q` PASS → mutasyon (bir satırı kimlik yardımcısını atlayarak bas → üretilmiş matris kırmızı) → commit `feat(sektor): render the package rules as a mandatory block with ids`.

**Kabul:** matris PASS; mevcut istem testleri değişmeden PASS (yeni işlev henüz çağrılmıyor).

### Task 7: Seçmeli dağarcık — türe göre süzgeç

**Amaç:** Kanca/CTA/takvim temalarını türe ve kanala göre, "en fazla BİR" talimatıyla basmak (spec §3.3-B, §3.5).

**Dosyalar:**
- Modify: `apps/social/backend/app/services/sector_packages.py`
- Test: `apps/social/backend/tests/test_optional_block.py` (yeni)

**Arayüz (Produces):** `render_optional_block(context: SectorPackageContext, *, surface: Literal["caption", "idea"], post_type: PostTypeResolution, channels: Any) -> str`

**Bağlayıcı invariantlar (seam: `sector_packages.py::render_optional_block`; kanal süzgeci `filter_channel_dependent` DEĞİŞMEZ):**
- Tür çağrıdan önce biliniyorsa (`gun_kaydi`, `urun_varsayilan`) havuz KODDA süzülür; `urun_varsayilan`da varsayılan
  türün havuzu + `bilgi` havuzu (etiketli) basılır, `kutlama/anma` havuzları basılmaz; `model` kaynağında (ve `idea`
  yüzeyinde) havuz tür etiketleriyle basılır, süzgeç talimatladır.
- Seçim talimatı spec §3.3-B metnidir ("en fazla BİR … uyan yoksa hiç … Listeyi tamamlamaya çalışma"); `kutlama`/`anma`'da CTA havuzu basılmaz.
- CTA kaynak sırası satırı (Global Constraints) paketli blokta basılır.
- `takvim_temalari` olduğu gibi basılır (kopya temizliği içerik işidir — Task 19).

**Testler:**
- `test_type_filter_matrix_generated` — `itertools.product(kaynak ∈ {gun_kaydi, urun_varsayilan, model}, tür ∈ POST_TYPES, kanca etiketleri, CTA türleri, kanal kümeleri)`: basılan her öğe kurala uyar, uymayan hiçbiri basılmaz.
- `test_no_cta_pool_for_kutlama_anma` · `test_selection_instruction_at_most_one` · `test_cta_order_line_present`.

**Adımlar:** iskelet → testler → gövde → `pytest tests/test_optional_block.py -q` PASS → mutasyon (`urun_varsayilan`da `bilgi` havuzunu düşür → matris kırmızı) → commit `feat(sektor): filter the hook and cta pool by post type`.

**Kabul:** matris PASS.

### Task 8: Özel gün kuralları `G*` kimlikleriyle (render)

**Amaç:** Gün kaydının yuvalarını ayrı yetkiyle basan yeni render işlevi; K-119 ve K-03 satırları ve "Tür (paket)" satırı yeni işlevde YOK (spec §3.4).

**Dosyalar:**
- Modify: `apps/social/backend/app/services/sector_packages.py` (YENİ `render_special_day_rules`; eski `render_special_day_lines` tek çağıranı değişene kadar DURUR — kaldırma Task 9'da)
- Test: `apps/social/backend/tests/test_special_day_rules.py` (yeni)

**Arayüz (Produces):** `render_special_day_rules(context: SectorPackageContext, day_name: str | None, channels: Any, *, post_type: PostTypeResolution) -> RenderedRules` — eşleşme yüklemi `match_special_day` (tek ölçü, DEĞİŞMEZ); eşleşme yoksa `RenderedRules("", ())` + bugünkü uyarı log'u.

**Bağlayıcı invariantlar (seam: `sector_packages.py::render_special_day_rules`):**
- Kimlikler spec §3.4'teki adlarla: `G-mesaj` ("Bu gün için geçerli kural:" başlığıyla `mesaj_ekseni`, her gün türünde) ·
  `G-satis-yok` ("CTA yerine kutlama-saygı kalıbı; satış çağrısı kullanma" — kutlama ve anma) · `G-anma-cerceve`
  (yalnız anma). `kanca`/`cta` seçmeli ("en fazla bir", kanal süzgeci `filter_channel_dependent` aynı), kimliksiz.
- Kutlama/anma'da "Kullanıcı açıkça satış/kampanya isterse isteğe uy ve bu kuralı `kural_uyumu`'nda `istek-geregi-cignendi` diye işaretle." satırı basılır.
- Render'ın bastığı bağlayıcı satırların TAMAMI kimlikli; yeni bir bağlayıcı satır kimlik almadan basılamaz.

**Testler:**
- `test_special_day_binding_lines_ids_generated` — `itertools.product(gün türü ∈ {ticari-firsat, karma, kutlama, anma}, cta ∈ {var, yok, kanal-bağımlı}, kanal kümeleri)`: basılan bağlayıcı satırlar == `rules`.
- `test_k119_k03_and_type_lines_absent` · `test_mesaj_ekseni_under_rule_heading` · `test_unmatched_day_renders_nothing_and_logs`.

**Adımlar:** iskelet → testler tek tek kırmızı → gövde → `pytest tests/test_special_day_rules.py tests/prompt_regression/ -q` PASS → mutasyon (`G-anma-cerceve` satırını kimliksiz bas → matris kırmızı) → commit `feat(sektor): render special-day rules with ids`.

**Kabul:** matris PASS; mevcut istem testleri değişmeden PASS (yeni işlev henüz çağrılmıyor).

### Task 9: İstem kurucu entegrasyonu — iki katman, gün satırları, tür satırı, ürün türü, hizmet listesi

**Amaç:** Blokları katmanlarına yerleştirmek, özel gün bloğunu yeni işleve geçirmek, takvim ve ton satırlarını türe
göre basmak ve basılan kural haritasını tek çağrı bağlamında toplamak (D3, D4, D9; spec §3.4 madde 6, §3.6).

**Dosyalar:**
- Modify: `apps/social/backend/app/core/prompt_builder.py` (`build_brand_context`, `build_dynamic_content` — özel gün dalı ve `_SPECIAL_DAY_TONE_HINTS` kullanımı dâhil)
- Modify: `apps/social/backend/app/core/caption_generator.py` (`generate_captions` istem kısmı: `resolve_post_type` çağrısı, kural haritası birleşimi)
- Modify: `apps/social/backend/app/services/sector_packages.py` (eski `render_special_day_lines` KALDIRILIR — tek çağıranı bu görevde değişir)
- Modify: `apps/social/backend/app/routers/posts.py` (`generate_caption`: ürün sorgusu `type` alanını seçer; hizmet listesi `brand_products WHERE brand_id = $1 AND type = 'service' AND is_active` — kolonlar ölçüldü: `information_schema.columns` `brand_products` → `type text`, `is_active boolean default true`)
- Test: `tests/prompt_regression/test_packaged_caption.py` (güncelleme) + yeni paketli golden'lar `tests/prompt_regression/fixtures/caption__packaged__{single,product,special_day}.txt` + `tests/test_special_day_rules.py` (takvim/ton satırı testleri)

**Arayüz:**
- Consumes: Task 5–8 işlevleri.
- Produces: `build_brand_context(brand, brand_kit, template, package_context=None, *, services: Sequence[str] = ()) -> RenderedRules` ·
  `build_dynamic_content(..., package_context=None, channels=None, *, post_type: PostTypeResolution | None = None) -> RenderedRules` ·
  `generate_captions(..., package_context=None, *, services: Sequence[str] = ())` — içeride `printed_rules: dict[str, str]` (iki katmanın birleşimi) ve `post_type: PostTypeResolution`.

**Bağlayıcı invariantlar (seam: `prompt_builder.py::build_brand_context`, `::build_dynamic_content`; `caption_generator.py::generate_captions`):**
- Paketsiz dönüş `RenderedRules(text=<bugünkü bayt>, rules=())` — metin DEĞİŞMEZ (mevcut 13 golden).
- Paketli: Tier 2 = zorunlu blok (kök rehberin YERİNE, yan-yana basım yasağı sürer); Tier 3 = özel gün bloğu
  (`render_special_day_rules`) → tür satırı ("Gönderi türü: X" / "Varsayılan tür: X; istek açıkça anlatım/bilgi
  istiyorsa `bilgi`'ye çevir" / "Gönderi türünü belirle ve yaz") → seçmeli dağarcık → kullanıcı isteği → ürün bloğu.
- Özel gün dalının takvim satırı paketli yolda türe göre: `kutlama/anma` → bugünkü "kutlama/tebrik postudur" satırı;
  `satis` → "gün bağlamı, satış serbest" satırı; `hizmet/bilgi` → gün bağlamı satırı (satış çağrısı zorunlu değil);
  tür `None` (günün paket kaydı yok) → bugünkü satır kalır.
- D9: paketli yolda tür `satis/hizmet/bilgi` iken `commercial` ton ipucunun satış yasağı cümleleri basılmaz; ton cümlesi ve `cta_url` link kuralı kalır.
- Ürün bloğunda `Tür: ürün | hizmet` yalnız paketli yolda; `ana_konu` şablon dalında ürün bloğu atlanıyorsa paketli yolda tek satır `Ürün/hizmet türü: …` yine basılır.
- Birleşimde kimlik çakışması olamaz (`Z*` ve `G-*` ad alanları ayrık) — çakışma `ValueError`.

**Testler:**
- `test_packaged_prompt_golden_{single,product,special_day}` — yeni paketli golden'lar (ilk üretimde fark İNCELENİR, commit mesajında özetlenir).
- `test_printed_rules_equal_union_of_layers` · `test_product_type_line_only_on_packaged_path_both_template_branches` · `test_services_line_lists_active_services_only`.
- `test_calendar_line_by_type_packaged_generated` (tür × kaynak → beklenen satır) · `test_commercial_tone_hint_sales_ban_only_dropped_for_packaged_non_celebration_types`.
- `test_day_without_package_entry_keeps_calendar_line_and_prints_no_g_ids` (Review Focus 1).
- Mevcut `test_packaged_caption.py` başlık testleri yeni tasarıma göre: K-119 testi TERSİNE döner (satır yok + `G-satis-yok` basılı); başlık yüzeyinde K-04 metni yok. Fikir testi Task 11'e kadar değişmez.
- `pytest tests/prompt_regression/ -q` → paketsiz golden'lar değişmeden PASS.

**Adımlar:** testler → kırmızı → entegrasyon → PASS → mutasyon (Tier 3 kural haritasını birleşime ekleme → `test_printed_rules_equal_union_of_layers` kırmızı) → commit `feat(sektor): place both package blocks and collect printed rules`.

**Kabul:** `pytest tests/prompt_regression/ tests/test_special_day_rules.py -q` PASS; `git diff --stat tests/prompt_regression/fixtures` yalnız yeni paketli dosyaları gösterir.

### Task 10: Çıktı sözleşmesi ve `kural_uyumu` kapısı

**Amaç:** Modelden `gonderi_turu` + kural başına beyan istemek, beyanı deterministik kapıdan geçirmek ve paketli
yolda hiçbir başarısızlığı yedek metne düşürmemek (spec §3.2, §3.12; D6, D10, D14). Beyanın SAKLANMASI Task 13'tedir
(tablo Task 12'de doğar).

**Dosyalar:**
- Modify: `apps/social/backend/app/core/caption_generator.py` (`_build_output_format_instruction`, `generate_captions`: anahtar yok dalı, model çağrısı, ayrıştırma sonrası)
- Modify: `apps/social/backend/app/services/sector_packages.py` (kapı işlevleri)
- Modify: `apps/social/backend/app/routers/posts.py` (`generate_caption`: `PackagedGenerationError` → 502; iç anahtarı `pop` eder)
- Test: `apps/social/backend/tests/test_rule_compliance_gate.py` (yeni) + `tests/prompt_regression/test_packaged_caption.py`

**Arayüz (Produces):**
- `class PackagedGenerationError(RuntimeError)` · `class PackageComplianceError(PackagedGenerationError)`
- `check_rule_compliance(report: Any, printed: Mapping[str, str]) -> list[str]`
- `check_post_type(value: Any, change: Any, resolution: PostTypeResolution, report: Sequence[Mapping]) -> list[str]` (D14 kuralları)
- `enrich_rule_report(report: list[dict], printed: Mapping[str, str]) -> list[dict]` — her satıra `kural` = basılan metin (modelin yazdığı kural metni YOK SAYILIR).
- Beyan satırı şeması: `uyuldu` → `{kimlik, karar}`; `istek-geregi-cignendi` → `{kimlik, karar, istek_parcasi, uretilen_cumle}`; `uygulanamadi` → `{kimlik, karar, neden}`; zenginleştirme sonrası + `kural`. Tür değişikliği: `tur_degisikligi = {istek_parcasi}` ya da yok.
- `RULE_REPORT_KEY = "_rule_report"` — `generate_captions` sonucuna konan İÇ anahtar (`PACKAGE_APPLIED_KEY` deseni; yanıt sözleşmesinin parçası DEĞİL): `{gonderi_turu, kural_uyumu, tur_degisikligi}`.

**Bağlayıcı invariantlar (seam: `caption_generator.py::generate_captions`):**
- Paketli çıktı formatı `gonderi_turu`, `kural_uyumu`, gerektiğinde `tur_degisikligi` alanlarını ve BEKLENEN kimlik listesinin tamamını basar; paketsiz çıktı formatı bayt-bayt aynı.
- Tür kapısı (D14): `gun_kaydi`/`urun_varsayilan` → çözülen türden farklı değer ancak `tur_degisikligi` ile; `urun_varsayilan`'da `bilgi` spec'in adlandırdığı istisnadır ve o da beyanlıdır; gün türü `kutlama`/`anma` + çıktı `satis` → `G-satis-yok` = `istek-geregi-cignendi` zorunlu; `model` → `POST_TYPES`, beyansız.
- Paketli yolda (`package_context is not None`) API anahtarı yokluğu, model istisnası, ayrıştırma hatası ve kapı düşüşü `PackagedGenerationError` olur; genel `except` yedeği paketli yolda ÇALIŞMAZ; `PACKAGE_APPLIED_KEY` ve `RULE_REPORT_KEY` konmaz → makbuz yazılmaz; uç 502 + "Gönderi metni paket kurallarına göre üretilemedi; tekrar deneyin." Paketsiz yolun yedek davranışı bayt-bayt aynı.
- Paketli çağrıda `max_tokens=4096`, paketsiz 2048 (D10).

**Testler:**
- `test_gate_rejects_generated_defect_matrix` — `itertools.product(kusur ∈ {eksik `Z` kimliği, eksik `G` kimliği (özel günlü paketli üretim), bilinmeyen kimlik, çift kimlik, karar dışı değer, kanıt eksik (karar başına), fazladan anahtar, satır nesne değil, liste değil})` → her biri reddedilir; eksiksiz geçerli beyan kabul edilir.
- `test_post_type_gate_matrix_generated` — `itertools.product(kaynak, çözülen tür, çıktı türü ∈ POST_TYPES, tur_degisikligi ∈ {var, yok}, G-satis-yok kararı)` → D14'e göre kabul/ret; anma günü + satış isteği uçtan uca kabul (tür `satis`, `G-satis-yok` = `istek-geregi-cignendi`).
- `test_packaged_failures_never_fall_back_generated` (Review Focus 2) — `itertools.product(hata ∈ {anahtar yok, model istisnası, bozuk JSON, kesik beyan, kapı düşüşü})` → uç 502, yanıtta yedek metin YOK, `generation_stamps` satır sayısı değişmez.
- `test_paketsiz_fallback_unchanged` — paketsiz yolda aynı hatalar bugünkü yedeği döndürür (bayt-bayt).
- `test_rule_text_comes_from_printed_map_not_model` · `test_paketsiz_output_format_and_response_unchanged` (Katman-1 golden + yanıt anahtar kümesi).
- Taklit kuralı: model taklidi gerçek `anthropic.messages.create` imzasına uyar (`tests/prompt_regression/capture.py` deseni).

**Adımlar:** iskelet → testler tek tek kırmızı → gövde → `pytest tests/test_rule_compliance_gate.py tests/prompt_regression/ tests/test_package_stamp_and_events.py -q` PASS → mutasyon (kapı (i)'yi sök → matris kırmızı; paketli yolda yedeği aç → Review Focus 2 testi kırmızı) → commit `feat(sektor): require a per-rule compliance report and gate it`.

**Kabul:** iki matris PASS; paketsiz golden'lar, yanıt ve yedek davranışı değişmedi.

### Task 11: Fikir yüzeyi — iki blok, beyansız

**Amaç:** Fikir önerisinde de zorunlu kurallar ve etiketli dağarcık basılsın (spec §3.11 yüzey "fikir"; D11).

**Dosyalar:**
- Modify: `apps/social/backend/app/routers/ai.py` (`suggest_ideas` paketli dalı; hizmet listesi sorgusu)
- Modify: `apps/social/backend/app/services/sector_packages.py` (eski `render_package_block` + `USAGE_INSTRUCTION` KALDIRILIR — son çağıran bu görevde değişir; K-04 atıflı yorumlar tarihçe cümlesiyle)
- Test: `tests/prompt_regression/test_packaged_caption.py::test_packaged_idea_prompt_replaces_guidance` (güncelleme) + `test_idea_surface_two_blocks_no_declaration` + `test_k04_usage_instruction_absent_everywhere` (yeni)

**Bağlayıcı invariantlar (seam: `ai.py::suggest_ideas`):** paketli dal Tier 2'ye `render_mandatory_block(surface="idea")` + `render_optional_block(surface="idea", post_type=PostTypeResolution(None, "model"))` basar; fikir JSON sözleşmesi DEĞİŞMEZ; kapı YOK; paketsiz golden `ideas__default.txt` değişmez. `grep -rn "render_package_block\|USAGE_INSTRUCTION" app tests scripts` → 0 satır.

**Adımlar:** testler → kırmızı → değişiklik + kaldırma → `pytest tests/prompt_regression/ tests/test_mandatory_block.py tests/test_optional_block.py -q` PASS → commit `feat(sektor): print both package blocks on the idea surface`.

**Kabul:** fikir testleri PASS; paketsiz fikir golden'ı değişmedi; eski işlev ve K-04 metni depoda yok.

### Task 12: Migration 038 — gönderi satırına tür ve beyan; makbuz beyan tablosu

**Amaç:** `posts` tablosuna iki kolon + paketli⇒beyan değişmezi (spec §3.12; D7) ve kapıdan geçmiş beyanın makbuzla saklandığı tablo (D5).

**Dosyalar:**
- Create: `shared/db/migrations/038_posts_rule_compliance.sql`
- Create: `shared/db/migrations/rollback/038_down.sql`
- Test: `apps/social/backend/tests/test_migration_038.py` (yeni)

**Bağlayıcı invariantlar (037/032 ev deseni):**
- `posts`: `ADD COLUMN IF NOT EXISTS gonderi_turu TEXT NULL` + adlı `CHECK (gonderi_turu IS NULL OR gonderi_turu IN (<POST_TYPES>))`;
  `ADD COLUMN IF NOT EXISTS kural_uyumu JSONB NOT NULL DEFAULT '[]'` + adlı `CHECK (jsonb_typeof(kural_uyumu) = 'array')`;
  adlı `CHECK (package_id IS NULL OR jsonb_array_length(kural_uyumu) > 0)`.
- `social.generation_rule_reports`: `generation_id UUID PRIMARY KEY` (makbuz kimliği; `generation_stamps`'e yabancı
  anahtar YOK — 037 emsali), `brand_id UUID NOT NULL REFERENCES social.brands(id) ON DELETE CASCADE` (Tur 2 N4: marka
  silinince kullanıcı metni taşıyan beyan da gider — `generation_stamps` ve `posts` ile aynı yaşam döngüsü),
  `gonderi_turu TEXT NOT NULL` (+ `POST_TYPES` CHECK), `kural_uyumu JSONB NOT NULL` (+ dizi ve boş-olmama CHECK),
  `tur_degisikligi JSONB NULL`, `claimed_post_id UUID NULL` (Tur 2 F5: kısa video sahipliği; yabancı anahtar YOK),
  `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`.
- Kısıt eklemeden ÖNCE ihlal eden satır sayılır; > 0 ise migration DURUR (fail-closed; bugün 0 — ölçüldü, D7).
- `IF NOT EXISTS` var olanı değiştirmez → sonra kolon imzası, tablo imzası + kısıt tanımları DOĞRULANIR (032 "taşıyıcı sözleşme" deseni); yabancı imza → DUR.
- Kendi `BEGIN/COMMIT`ini taşımaz (runner `--single-transaction`). Fonksiyon/tetikleyici YAZMAZ (nesne kimliği kapısının kapsamı dışında kalır; `tests/test_migration_object_identity.py` yine koşar).
- Geri alma: herhangi bir gönderide `gonderi_turu IS NOT NULL` ya da boş olmayan `kural_uyumu` varsa YA DA beyan tablosunda satır varsa DURUR (beyan onay kanıtıdır); yoksa tablo, kısıtlar ve kolonlar düşer.

**Testler:** `test_038_applies_and_reapplies_idempotently` · `test_038_refuses_foreign_column_or_table_signature` · `test_038_refuses_when_violating_rows_exist` · `test_038_check_rejects_packaged_post_without_report` · `test_038_check_rejects_non_array_report` · `test_038_report_table_rejects_empty_report_and_unknown_type` · `test_038_report_rows_cascade_with_brand_delete` · `test_038_rollback_refuses_with_evidence_in_posts_or_report_table` · `test_038_rollback_clean_when_empty`.

**Adımlar:** testler → kırmızı → iki dosya → `pytest tests/test_migration_038.py tests/test_migration_object_identity.py tests/test_migration_032.py tests/test_migration_032_rollback.py -q` PASS (032 kapalı imzası ve geri alma yolu yeni tablodan etkilenmez) → commit `feat(db): add the post type and rule compliance columns (038)`.

**Kabul:** dokuz test PASS; nesne kimliği ve 032 testleri PASS.

### Task 13: Beyanın saklanması ve kalıcı kayıt — makbuz zorunlu, kısa videoda sahiplik

**Amaç:** Kapıdan geçen beyanı makbuzla saklamak, kayıtta gönderi satırına kopyalamak; paketli markada makbuzsuz ya
da geçersiz makbuzlu kaydı reddetmek; kısa videoda reddi pahalı işlerden ÖNCE vermek (D5, D6, D13; Tur 1 F1/F3/F5).

**Dosyalar:**
- Modify: `apps/social/backend/app/routers/posts.py` (`_write_generation_stamp` → makbuz + beyan tek transaction; `generate_caption`; `generate_post`; `generate_short_video_stage1` → 422 eşlemesi)
- Modify: `apps/social/backend/app/services/sector_packages.py` (`resolve_persist_stamp` sözleşmesi; ortak okunabilirlik yüklemi; `claim_receipt_for_post` / `release_receipt_claim`)
- Modify: `apps/social/backend/app/services/short_video.py` (`run_short_video_stage1` sonlandırma transaction'ı)
- Test: `apps/social/backend/tests/test_rule_report_persist.py` (yeni) + `tests/test_package_stamp_and_events.py` (güncelleme)

**Arayüz (Produces):**
- `@dataclass(frozen=True) class PersistStamp: package_id: UUID | None; package_version: int | None; gonderi_turu: str | None; kural_uyumu: list[dict]`
- `resolve_persist_stamp(db, brand, generation_id, *, receipt_expected: bool = True, claimant_post_id: UUID | None = None) -> PersistStamp` — paketli markada makbuz yok/geçersiz/tüketilmiş → `StampRequiredError(ValueError)` (D13); geçerli makbuz → beyan `generation_rule_reports`'tan okunur. **Makbuz tüketiminin TEK geçidi (Tur 3 X1):** tüketim, beyan satırının sahipliğiyle AYNI koşullu işlemde doğrulanır — `claimant_post_id` yoksa `claimed_post_id IS NULL` şartı, varsa `claimed_post_id = claimant_post_id` şartı; tutmazsa `StampRequiredError`, makbuz yanmaz. Her tüketici (bugün iki: `posts.py::generate_post`, `short_video.py::run_short_video_stage1`) bu fonksiyondan geçer; sahiplik denetimi tüketiciye özel YAZILMAZ.
- `active_package_is_readable(db, sub_sector_id) -> bool` — `resolve_package_context` ile AYNI satır doğrulama yardımcısını kullanır, olay YAZMAZ.
- `claim_receipt_for_post(db, brand, generation_id, post_id) -> None` — kısa video: makbuz geçerli + tüketilmemiş + markaya ait + beyan satırı var + `claimed_post_id IS NULL` koşullu güncellemesiyle beyan satırını bu gönderiye ayırır; aksi hâlde `StampRequiredError`. `release_receipt_claim(db, generation_id, post_id) -> None` — başarısızlık yolunda sahipliği bırakır.

**Bağlayıcı invariantlar:**
- `posts.py::_write_generation_stamp`: paketli üretimde makbuz + beyan satırı AYNI transaction'da yazılır; biri yazılamazsa
  ikisi de yok ve başlık ucu 502 döner (D6 — paketli metin ancak geçerli makbuzla döner). Paketsiz üretimde bugünkü davranış.
- `posts.py::generate_post`: kayıt transaction'ında makbuz tüketilir, beyan satırı okunur ve gönderi satırına KOPYALANIR;
  istemcinin yolladığı hiçbir beyan alanı kabul EDİLMEZ (istek şeması değişmez). `StampRequiredError` → 422 + Türkçe
  ileti ("Metin doğrulanmış paket makbuzu olmadan kaydedilemez; metni yeniden üretin."); transaction geri alınır,
  `stamp_missing`/`stamp_invalid` olayı transaction DIŞINDA yazılır.
- `short_video.py::run_short_video_stage1` (paketli yol): gönderi satırını açan transaction AYNI anda
  `claim_receipt_for_post` ile beyan satırını bu gönderiye ayırır — ses (TTS) ve durağan görsel çağrılarından ÖNCE.
  Sahiplik alınamazsa (makbuz yok/geçersiz/tüketilmiş ya da başka istek almış) transaction geri alınır, 422, hiçbir
  yan etki yok (Tur 1 F5 + Tur 2 F5: eşzamanlı aynı-makbuz isteklerinde yalnız kazanan pahalı işi başlatır).
  Başarısızlık yolunda `release_receipt_claim` sahipliği bırakır (aynı makbuzla yeniden deneme mümkün); süreç
  çökerse sahiplik kalır ve kullanıcı metni yeniden üretir (fail-closed, belgeli). Sonlandırma transaction'ı makbuzu
  `resolve_persist_stamp(..., claimant_post_id=bu gönderi)` ile tüketir (sahiplik şartı tek geçitte), beyanı kopyalar
  (bugünkü CAS deseni korunur). Normal kayıt (`generate_post`) sahiplenilmiş bir makbuzu TÜKETEMEZ (Tur 3 X1) —
  422, kısa videonun işi sürer. Paketsiz yol DEĞİŞMEZ.
- DB kısıtı (Task 12) son savunma hattıdır; uygulama kapısı önce koşar.
- **Serileştirme invariantı (Tur 4 X2 — Eray kararı 2026-09-25: "Kuralı yaz, kilidi koda bırak"):** aynı makbuz için
  TÜM tüketiciler (normal kayıt; kısa video sahipliği ve sonlandırması) TEK bir serileştirme noktasında sıralanır;
  makbuzu en fazla bir gönderi sahiplenir/tüketir; kaybeden istek hiçbir ücretli yan etki (TTS, durağan görsel,
  fal.ai) başlamadan 422 alır. **Mekanizma yürütmede kurulur, kod incelemesi sınar** (yukarıdaki arayüz adları yol
  göstericidir). **Bilinen tuzak:** sahiplik ve tüketim FARKLI satırlarda koşullu güncellemeyle yapılırsa PostgreSQL
  READ COMMITTED altında iki işlem birbirini beklemez ve ikisi de başarılı olur — ortak satır ya da kilit şarttır.

**Testler:**
- `test_same_receipt_race_real_db_single_winner` (Tur 4 X2, ZORUNLU — taklitle DEĞİL, gerçek veritabanında): normal
  kayıt ile kısa video sahipliğini iki ayrı bağlantıda, commit ÖNCESİ bir bariyerde karşı karşıya getir; tek kazanan,
  makbuz durumu ve TTS/durağan görsel/fal.ai çağrı sayısı (kaybeden için 0) birlikte doğrulanır; iki sıra da
  (önce normal kayıt / önce kısa video) koşulur.
- `test_caption_stores_receipt_and_report_atomically` · `test_caption_returns_502_when_report_write_fails_no_receipt`.
- `test_generate_copies_stored_report_ignores_client_fields`.
- `test_persist_receipt_matrix_generated` — `itertools.product(makbuz ∈ {yok, geçerli, geçersiz, tüketilmiş, başka marka}, paket ∈ {yok, okunabilir, okunamaz}, içerik türü ∈ {image, quote})` → yalnız "okunabilir paket + makbuz beklenir + makbuz geçerli değil" hücreleri 422 (gönderi satırı yok, olay yazılmış); diğerleri bugünkü davranış.
- `test_short_video_rejects_before_side_effects` — eksik makbuzda TTS/durağan görsel taklitleri HİÇ çağrılmaz, post satırı yok.
- `test_short_video_concurrent_same_receipt_only_winner_runs_side_effects` — aynı makbuzla iki eşzamanlı istek: taklit TTS/durağan görsel yalnız bir kez çağrılır, kaybeden 422.
- `test_receipt_claim_respected_by_every_consumer_generated` (Tur 3 X1) — `itertools.product(tüketici ∈ {generate_post, stage-1 sonlandırma}, sahiplik ∈ {yok, bu gönderi, başka gönderi}, makbuz ∈ {tüketilmemiş, tüketilmiş})` → yalnız "sahiplik yok + normal kayıt" ve "sahiplik bu gönderi + sonlandırma" hücreleri (tüketilmemiş makbuzla) kabul; diğerleri 422, makbuz yanmaz. Tüketici listesi `grep -rn "resolve_persist_stamp(" app` ile KODDAN sayılır; yeni tüketici eklenirse test kırmızı olur.
- `test_normal_save_cannot_consume_short_video_claimed_receipt` — kısa video sahiplik aldıktan sonra aynı makbuzla `/posts/generate` → 422; kısa video sonlandırması başarılı.
- `test_short_video_failure_releases_claim_and_retry_succeeds` · `test_short_video_stage1_persists_report`.

**Adımlar:** testler → kırmızı → değişiklik → `pytest tests/test_rule_report_persist.py tests/test_package_stamp_and_events.py tests/test_rule_compliance_gate.py -q` PASS → mutasyon (okunabilirlik koşulunu `True` sabitle → matriste okunamaz-paket hücreleri kırmızı; sahiplik koşulunu (`claimed_post_id IS NULL`) sök → eşzamanlılık testi kırmızı; `resolve_persist_stamp`'tan sahiplik şartını sök → tüketici matrisi kırmızı) → commit `feat(posts): store the rule report with the receipt and copy it on save`.

**Kabul:** testler PASS; `resolve_persist_stamp`'ın eski "üretim bloklanmaz" belge cümlesi D13'e göre güncellendi.

### Task 14: İfşa biçimleyici ve API alanları

**Amaç:** Beyanın tek biçimle arayüze ve Telegram'a gitmesi; Telegram'da her kuralın adı onay düğmesinden önce, her mesaj kendi sınırında (spec §3.12; D8; Tur 1 F7, Tur 2 N2).

**Dosyalar:**
- Create: `apps/social/backend/app/services/rule_disclosure.py`
- Modify: `app/routers/posts.py` (başlık yanıtı + gönderi liste/ayrıntı yanıtları), `app/routers/calendar.py` (sorgu kolonları), `app/routers/internal.py` (`/internal/posts/{post_id}`)
- Test: `apps/social/backend/tests/test_rule_disclosure.py` (yeni)

**Arayüz (Produces):**
- `format_disclosure(kural_uyumu: Sequence[Mapping]) -> list[str]` — boş liste → `[]`; hepsi `uyuldu` → `["Paket kurallarına uyuldu."]`; diğerleri kural metniyle + kanıtla; ilk satır "Üretim anındaki beyan" etiketi.
- `build_telegram_messages(post: Mapping) -> list[TelegramMessage]` — `TelegramMessage(method: Literal["sendPhoto", "sendMessage"], text: str, photo_url: str | None, buttons: bool)`: SIRALI liste; onay düğmeleri YALNIZ son mesajda (`buttons=True`). Bugünkü n8n mesajının TÜM parçaları (başlık önizlemesi, platformlar, tür, video bağlantısı) + ifşa, Telegram Markdown kaçışıyla. İfşa fotoğraf açıklamasına sığmıyorsa fotoğraf düğmesiz gider, ifşa bir ya da daha çok metin mesajına bölünür, düğmeler sonuncuda.
- Yanıt alanları: `kural_ifsa: list[str]` + `gonderi_turu` (başlık yanıtı — beyan `RULE_REPORT_KEY`'den; gönderi listesi/ayrıntısı ve takvim — satırdan); `/internal/posts/{id}` ek olarak `telegram_mesajlari` (liste).

**Bağlayıcı invariantlar (seam: `rule_disclosure.py::build_telegram_messages`):** biçimleyici TEK yerdir; arayüz
ve n8n kendileri biçimlemez. `uyuldu` dışı kararlı HER kural, adıyla (kural metni; uzunsa adı taşıyan baş kısmı),
düğmeli mesajda ya da ondan ÖNCEKİ bir mesajda görünür — sayaç YOK. Her mesajın uzunluğu SON metin üzerinde ölçülür
(kaçış + tüm değişken parçalar eklendikten sonra): fotoğraf açıklaması ≤ 1024, metin ≤ 4096 — Telegram Bot API
belgesindeki değerler, bu oturumda ÖLÇÜLMEDİ; Task 21 dumanında gerçek gönderimle ölçülür. Paketsiz gönderide liste
tek mesajdır ve bugünkü n8n metninin içeriğini taşır (kaçış düzeltmesi hariç).

**Testler:** `test_disclosure_lines_matrix` (karar kombinasyonları) · `test_disclosure_labels_generation_time` (Review Focus 3) ·
`test_telegram_messages_name_every_rule_before_buttons_generated` (Review Focus 5: `itertools.product(kural sayısı 0..17, kural metni 10..400, karar karışımı, başlık Markdown özel karakterli/uzun, platform sayısı 1..9, video bağlantısı yok/uzun, içerik türü görsel/video)` → her mesaj sınırda; düğme yalnız sonda; `uyuldu` dışı her kuralın kimliği ve adı düğmeli mesajda ya da öncesinde; Markdown dengeli) ·
`test_calendar_and_list_carry_disclosure` · `test_internal_post_includes_telegram_messages`.

**Adımlar:** iskelet → testler → gövde → `pytest tests/test_rule_disclosure.py -q` PASS → mutasyon (son kural satırını düşür → isimlendirme testi kırmızı; düğmeyi ilk mesaja koy → sıra testi kırmızı; kaçışı sök → Markdown dengesi kırmızı) → commit `feat(posts): format the rule disclosure once for all surfaces`.

**Kabul:** testler PASS.

### Task 15: Arayüz — beyan gösterimi ve tek tık yayın kapısı

**Amaç:** Kullanıcı gönderiyi onaylarken beyanı görsün (spec §3.12 "gösterilmesi bu notun invariantıdır"; D8).

**Dosyalar:**
- Create: `apps/social/frontend/components/content/RuleDisclosure.tsx`
- Modify: `apps/social/frontend/components/templates/CaptionEditor.tsx` (`CaptionData`: `gonderi_turu`, `kural_ifsa` — yalnız gösterim)
- Modify: `apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx` (başlık yanıtındaki ifşayı sakla; metin adımı + önizleme + kısa video "Önizleme & Onay" adımında göster; kayıt isteklerine beyan EKLENMEZ — sunucu makbuzdan kopyalar, D5; makbuzsuz kayıt reddinin 422 iletisi mevcut hata yolundan gösterilir)
- Modify: `apps/social/frontend/components/content/ContentCard.tsx` (`Post` tipi: `kural_ifsa`, `gonderi_turu`)
- Modify: `apps/social/frontend/app/(dashboard)/icerik-kutuphanesi/page.tsx` (`PostDetailModal` gösterimi; `handlePublishFromCard` ve ayrıntı görünümü açmadan yayın/zamanlama/onaya gönderme başlatan diğer kart eylemleri: `uyuldu` dışı kararlı kural varsa beyan penceresi)
- Modify: `apps/social/frontend/app/(dashboard)/takvim/page.tsx` (pencere gösterimi + tip)

**Bağlayıcı invariantlar:** paketsiz gönderide (boş `kural_ifsa`) hiçbir şey görünmez; hepsi `uyuldu` → tek satırlık nötr bilgi;
çiğnenen/uygulanamayan varsa uyarı biçimi. Ayrıntı görünümü açılmadan yayın/zamanlama/onaya gönderme başlatan HER
tek tık eyleminde, `istek-geregi-cignendi` YA DA `uygulanamadi` kararlı bir kural varsa (Tur 2 N3) önce beyan penceresi
açılır; iptal → istek GİTMEZ. Eylem kümesi sayfa kodundan sayılır ve commit mesajına yazılır (kütüphane kartı, takvim
hızlı eylemleri, sihirbaz sonuç adımı).
Metinler günlük Türkçe (müşteri yüzeyi).

**Doğrulama (frontend'de test koşucusu yok — beyan edildi):**
- `cd apps/social/frontend && npm run lint && npm run build` → hatasız.
- Elle akış (yerel): paketli taklit yanıtla sihirbaz → metin adımında beyan · kütüphanede pencere · karttan yayın (a) çiğnenen kurallı, (b) YALNIZ `uygulanamadi` içeren gönderide → ikisinde de beyan penceresi → iptal (ağ sekmesinde istek yok) · takvim penceresi. Ekran görüntüsü `docs/active/sektor-bilgi-paketi-plan2/olcum/` altına.

**Adımlar:**
- [ ] Bileşen + tipler; sayfa değişiklikleri.
- [ ] `npm run lint && npm run build` → hatasız.
- [ ] Elle akış kontrolü; ekran görüntüleri.
- [ ] Commit `feat(frontend): show the rule disclosure at every approval point`.

**Kabul:** lint + build temiz; elle akışın altı durumu kayıtlı; tek tık eylem kümesi commit mesajında.

### Task 16: Telegram onay mesajı (n8n, depo tarafı)

**Amaç:** Telegram'dan onay veren kullanıcı beyanı görsün (spec §3.12).

**Dosyalar:**
- Modify: `shared/n8n-workflows/telegram-content-approval.json` ("Mesaj Hazırla" düğümü; "İçerik Tipi?" anahtarı + iki gönderim düğümü yerine SIRAYI koruyan tek gönderim düğümü)
- Create: `shared/n8n-workflows/tests/telegram_message_dry_run.mjs` (düğüm kodunu taklit `$input`/`$()` ile koşturan kuru deneme)

**Bağlayıcı invariantlar:** "Mesaj Hazırla" backend'in kurduğu `post.telegram_mesajlari` listesini (Task 14) SIRAYLA
öğe olarak döndürür; tek gönderim düğümü her öğeyi kendi yöntemiyle (`sendPhoto`/`sendMessage`) gönderir, onay
düğmelerini yalnız `buttons=true` öğeye ekler; düğüm kendisi biçimlemez, kesmez. Sıra korunur (anahtar dallarına
bölmek sırayı garanti etmez — bu yüzden tek düğüm). Alan yoksa (eski backend) bugünkü tek mesajı bugünkü yöntemle
kurar — geri dönüş uyumu. Webhook, "Post Detayı Al" ve bağlantıların geri kalanı değişmez.

**Adımlar:**
- [ ] Düğümleri değiştir; kuru deneme: `node shared/n8n-workflows/tests/telegram_message_dry_run.mjs` → dört örnek (paketsiz, hepsi uyuldu, 5 çiğnenen, ifşası fotoğrafa sığmayan 17 kural) + alanı olmayan eski yanıt; gönderilecek mesaj sırası, yöntemi, uzunluğu ve düğmenin hangi mesajda olduğu basılır.
- [ ] Commit `feat(n8n): add the rule disclosure to the Telegram approval message`.
- Canlı yükleme Task 21'de.

**Kabul:** kuru deneme beş örnekte beklenen sırayı ve yöntemi üretir; düğme her örnekte yalnız son mesajda; alan yokken bugünkü mesaj.

### Task 17: Tam takım, Katman-1 süpürmesi, istem boyutu, runbook

**Amaç:** Aşama A'nın kapanış kapısı.

**Dosyalar:**
- Modify: `docs/plans/PLAN2-DAGITIM-RUNBOOK.md` (038 uygulama adımı · şema-2 geri dönüş tabanı satırı · n8n düğüm adımı · dağıtım sırası: migration → backend → frontend → n8n)
- Modify: `apps/social/backend/app/services/sector_packages.py` ve `prompt_builder.py` içinde kalan K-119/K-03 atıflı yorumlar (tarihçe cümlesiyle)

**Adımlar:**
- [ ] `cd apps/social/backend && .venv/bin/python -m pytest -q` → hata/başarısızlık sayısı raporlanır (0 beklenir).
- [ ] `pytest tests/prompt_regression/ -q` + `git diff --stat 4c374c6 -- tests/prompt_regression/fixtures` (plan öncesi son commit) → yalnız yeni paketli golden'lar.
- [ ] İstem boyutu: paketli blok bugün 2.681–3.330 karakter (ölçüldü, TASK 2026-09-23 aktivasyon kaydı) → yeni iki blok + tür satırı aynı sınav senaryolarında `olcum_a.py` ile ölçülür, rapora yazılır (kapı DEĞİL).
- [ ] Runbook satırlarını yaz; geri dönüş kuralı (D7, Tur 1 F2): "038 uygulandıktan sonra kod dönüş hedefi YALNIZ
  (a) Task 21'de canlıya alınan sürüm ya da (b) bu planın öncesidir; bu planın ara commit'leri hedef OLAMAZ (2. sürümü
  okur ama beyan yazmaz → paketli kayıt DB kısıtıyla reddedilir). (b)'ye dönmeden önce: (1) `SELECT count(*) FROM
  social.posts WHERE package_id IS NOT NULL AND status <> 'published'` sıfır olmalı — değilse bu gönderiler ifşa bilen
  sürümde sonuçlandırılır (Tur 2 N1: plan öncesi arayüz/n8n beyanı göstermez); (2) aktif paket `deaktive-et` (K-38)
  ile indirilir; plan öncesi kod 2. sürümü okuyamaz → paketsiz yol + `package_read_error` + yönetici bildirimi. 038
  geri alması yalnız beyan verisi yoksa." Canlıya alınan sürümün sha'sı Task 21'de satıra yazılır.
- [ ] Commit `docs(runbook): add migration 038, the schema-2 floor and the n8n step`.

**Kabul:** tam takım 0 başarısız; paketsiz golden'lar değişmedi; runbook satırları yazıldı.

---

# Aşama B — Paketin 2. sürümü, sınav, canlıya alma, etkinleştirme

> Her ücretli adımdan önce tutar + Eray'ın AÇIK onayı. Her DUR noktasında Eray'a dönülür; otomatik devam YOK.

### Task 18: `KALIBRASYON-2.md` ve ölçüm aracı (sınavdan ÖNCE sabitlenir)

**Amaç:** Yeni ölçütü sınavdan önce ayrı dosyada sabitlemek (spec §4 (b), §5); eski ölçüt değişmeden yan yana.

**Dosyalar:**
- Create: `docs/active/sektor-bilgi-paketi-plan2/olcum/KALIBRASYON-2.md`
- Modify: `docs/active/sektor-bilgi-paketi-plan2/olcum/olcum_a.py`, `olcum_b.py`, `hakem_girdi.py`, `olcum_rapor.py`
- Create: `docs/active/sektor-bilgi-paketi-plan2/olcum/senaryolar-n1.json`

**İçerik (bağlayıcı):**
- Eşik (spec §4): hakem ≥15/20 paketli VE (b)'de kritik hata 0 VE **sessiz ihlal 0**; (a) `KALIBRASYON.md` DEĞİŞMEDEN yan yana (karşılaştırma metriği, kapı değil).
- Sınıflama: istekten gelen ihlal `istek-geregi-cignendi` ile işaretliyse hata DEĞİL; `uyuldu` denmişse **sessiz ihlal**; modelin kendi ihlali her durumda hata; **kapısı düşen paketli senaryo = başarısız senaryo** (sessiz atlama yok) ve kapı düşme sayısı ayrı satır.
- Kör hakem beyanı GÖRMEDEN ihlal arar; karşılaştırma sonradan yapılır.
- Ek ölçütler: `gonderi_turu` senaryo amacıyla uyuşma · kanca/CTA kalıbı türe göre · gramaj çelişkisi 0 · N1 senaryoları (`senaryolar-n1.json`, ürün bilgisi ve marka yasak kelimesiyle çatışan paket kuralı; sayısı dosyada sabit, 20'lik eşiğe GİRMEZ).
- Sınav `genel-gorsel-sablon` şablonuyla koşulur (spec §5 — §3.5'i ölçer).
- Senaryo ürünlerine `type` sabitlenir (bugün yok — ölçüm: `senaryolar-sinav.json` 19 ürünlü senaryonun ürün anahtarları yalnız `{description, name}`): S02 (ölçü/onarım), S14 (takı temizliği), S15 (eski altın alımı) → `service`; diğer ürünlü senaryolar → `product`.
- Maliyet tahmini dosyada, **tahmin** etiketiyle.

**Adımlar:**
- [ ] Dosyayı yaz; araçları güncelle (paket kimliği argüman olur; hizmet/kanal geçer; beyan ve tür `RULE_REPORT_KEY`'den kaydedilir; `PackagedGenerationError` yakalanıp senaryo başarısız sayılır, alt türü — kapı düşüşü / model hatası — ayrı satırda).
- [ ] Ücretsiz duman: `olcum_a.py` (model çağrısı YOK) 20 senaryoda istemi yakalar → iki blok + tür satırı + beklenen kimlik listesi her paketli istemde var.
- [ ] Eray'a özet (sade dil): eşik, sınıflama, tür sabitlemesi. İtiraz yoksa sabit.
- [ ] Commit `docs(active): fix the second exam calibration before the exam`.

**Kabul:** dosya commit'li; duman temiz.

### Task 19: Yeni tam koşu, operatör kararları, 2. sürüm taslağı

**Amaç:** Paketin 2. sürümünü hattın kendisiyle üretmek (Eray kararı 2026-09-25: "Yeni tam koşu").

**Ön koşul:** Task 1–17 commit'li (CLI çalışma ağacından yeni kodla koşar); pin Task 4'te taşındı.

**Adımlar (her komut `/sektor-paket` üzerinden):**
- [ ] Maliyet bildirimi + Eray onayı (ölçülmüş: denetim 18,5–21,5 dk; sentez 1,77–2,09 USD).
- [ ] `tur-ac` → `brief-doctor` → `denetim` → `sentez` → `katman1` (tasdik, actor eray) → `motor`.
- [ ] **DUR-1:** motor sonucu `blocked` ve tek sebep `acik-soru-var` DEĞİLSE (ör. `activation_eligible`, `no_change`, yapısal sebep) → operatör yolu açılmaz (`operator_decisions.py::uygula`); Eray'a rapor. Yol: aktif pakete araştırmasız düzeltme yeni bir tasarım işidir (spec yeniden açılır).
- [ ] Açık sorular Eray'a senaryolu sorulur (K-134 biçimi; öneri verilmez, sentezin eğilimi etiketli).
- [ ] Karar dosyası: Eray'ın cevapları + spec §3.7 işlemleri — `ekle ozel_gun` anma ×3 (18 Mart · 10 Kasım · 15 Temmuz; beş yuva, `cta = içerik-önerilmez`; anahtarlar takvimde — ölçüldü) · `sektor_gercekleri` ("22 ayar saf değildir; saf altın 24 ayardır" + raporlarda kaynaklı olan doğrular; `içerik-önerilmez` birimi varsa `degistir`) · `ekle kanca_kaliplari` tür etiketli (hizmet: onarım/ölçü/taklas/bakım · bilgi: kararma/ayar/taş bakımı · kutlama) · `degistir ton_ve_dil` (üç kural satırı + `ton (yumuşak):` satırları) · `cikar takvim_temalari` ×4 (Sevgililer · Anneler · Babalar · Yılbaşı). Anma günleri Eray'la kesinleşir (spec K-C).
- [ ] `operator-karar` → `yazim` → taslak (`schema_version = 2`). Taslak kimliği TASK'a yazılır.
- [ ] Onay yüzeyi özetinde 1. sürüme göre değişen HER birim Eray'a gösterilir (koşu, operatör işlemleri dışında da değişiklik yapmış olabilir).
- [ ] Commit (TASK + karar dosyası kaydı) `docs(active): record the second-version run and its operator decisions`.

**Bilinen sınır:** operatör işlemi bir açık sorunun cevabına bağlanmak zorunda; §3.7 işlemleri en ilgili sorunun cevabına eklenir ve cevap metni "tasarım notu 2026-09-25 §3.7" atfını taşır (denetim izinde görünür).

**Kabul:** `schema_version = 2` taslak var; karar kaydı `sector_run_operator_decisions`'ta.

### Task 20: Sınav tekrarı ve sonuç raporu

**Amaç:** Tasarımın sonucu ölçmek; eşik `KALIBRASYON-2.md`.

**Adımlar:**
- [ ] Tutar bildirimi (**tahmin** ≈1,6 USD + N1 senaryoları) + Eray onayı.
- [ ] A (ücretsiz) + B (ücretli) taslak paket kimliğiyle; Codex kör hakem; Eray kör okuma (C).
- [ ] `SONUC-sinav-2-<tarih>.md`: iki ölçüt yan yana · sessiz ihlal · kapı düşme sayısı · tür uyuşması · çıktı jetonu dağılımı (D10 ölçümü) · maliyet (ölçülen).
- [ ] **DUR-2:** eşik geçmezse Eray'a dön; sessiz ihlal > 0 → spec §5 bağımsız ihlal denetimi (ev: sınav sonucu değerlendirmesi); `gonderi_turu` hatası → spec §5 tür seçtirme yolu (aynı ev).
- [ ] Commit `docs(active): record the second exam and its verdict`.

**Kabul:** rapor commit'li; karar Eray'da.

### Task 21: Canlıya alma kapısı

**Amaç:** Kod, migration, frontend ve n8n'i canlıya almak — etkinleştirmeden ÖNCE (Global Constraints sırası).

**Ön koşul:** Task 20 geçti (DUR-2 yok). Bu görev Eray'ın kararlarıyla ilerler: dal review'ı (`/review-claude-codex`, `/security-review-claude-codex` — yürütücü bunları kendisi başlatmaz, Eray'a döner) · `main`'e birleştirme onayı.

**Adımlar:**
- [ ] Eray onayıyla `main`'e birleştirme + push.
- [ ] Canlı migration 038 (runbook adımı; önce ihlal sayımı; `--single-transaction`).
- [ ] Coolify: backend + frontend dağıtımı (Eray düğmeye basar).
- [ ] n8n: canlı "Telegram İçerik Onay" iş akışını API'den oku → depo JSON'uyla düğüm bazında karşılaştır (Task 16 dışı fark varsa DUR, Eray'a sor) → yalnız Task 16'nın değiştirdiği düğümleri ve bağlantıları yükle → geri oku, doğrula.
- [ ] Duman: canlı 1. sürüm paket okunuyor (`resolve_package_context` → bağlam, olay yok); paketsiz bir üretim bugünküyle aynı yol; Telegram'a paketli taklit bir onay dizisi (Eray onayıyla, test sohbeti) → her mesaj Telegram'ca kabul edildi (belge sınırlarının ölçümü), her kural adı düğmeli mesajdan önce ya da onda görünür.
- [ ] Runbook + TASK: canlıya alınan sürümün sha'sı (dönüş hedefi (a)) + dağıtım zamanı.
- [ ] Geri dönüş provası (Tur 1 F2 + Tur 2 N1 doğrulaması, yerel klon veritabanı): 038 + paketli beyanlı bir gönderi varken
  (a) canlıya alınan sürümle başlık → kayıt → onay dizisi akışı çalışır; (b) plan öncesine dönüş kapısı sorgusu
  (`SELECT count(*) FROM social.posts WHERE package_id IS NOT NULL AND status <> 'published'`) yayımlanmamış paketli
  gönderiyi SAYAR ve dönüş DURUR; gönderi ifşa bilen sürümde sonuçlandırılıp `deaktive-et` yapılınca sorgu 0 olur,
  plan öncesi kodla yeni kayıt paketsiz yoldan geçer.
- [ ] Commit (runbook dönüş hedefi sha'sı + TASK dağıtım kaydı) `docs(runbook): record the deployed release as the rollback target`.

**Kabul:** migration canlıda; iki servis dağıtıldı; n8n düğümü geri okundu; duman temiz.

### Task 22: 2. sürüm etkinleştirme zinciri

**Amaç:** Taslağı hattın kapılarından geçirip etkinleştirmek; md-18'i 2. sürümde koşmak (TASK: "md-18 — EV: paketin 2. sürümü").

**Adımlar (her biri Eray'ın ayrı onayıyla):**
- [ ] `katman2` (kör örneklem; ölçülmüş 0,273 USD) → `hazirlik-onayla` → `onay` → `aktive-et`.
- [ ] md-18 ("Aktivasyon ve geri alma prosedürü test edildi" — `app/services/sector_pipeline/readiness_items.py`): iki sürüm
  varken olay akışıyla (`olay-plani` → `olay-onayla` → `olay-geri-al`; `runs.py` → `sector_package_lifecycle.py::rollback_package`)
  1. sürüme geri al, sonra aynı akışla 2. sürüme dön. `deaktive-et` bu denemede KULLANILMAZ: tek yönlüdür
  (`deactivate_package` aktif paketi arşivler, geri getirmez) ve sektörü paketsiz bırakırdı.
- [ ] TASK + HANDOFF: 2. sürüm etkin; marka ataması KENDİ evinde kalır (Task 19 Step 11, Eray'ın video üretim sistemi değişikliğinden sonra) — bu plan atama YAPMAZ.
- [ ] Commit `docs(active): record the activation of the second package version`.

**Kabul:** `status='active'`, `schema_version=2` satırı; md-18 sonucu TASK'ta.

---

## Kapsam dışı (evli ya da koşullu düşürülmüş)

- **Kullanıcıya tür seçtirme** — ev: Task 20 sonucu (spec §5).
- **Bağımsız ihlal denetimi** (onay öncesi ikinci model çağrısı) — ev: Task 20 sonucu, sessiz ihlal > 0 ise (spec §5).
- **Beyanın düzenleme sonrası tazelenmesi** — DÜŞÜRÜLDÜ (koşullu): beyan üretim anındaki metne aittir ve öyle etiketlenir (D8).
  Yeniden açılma koşulu: kullanıcı düzenlemesinin paket kuralını ihlal ettiği bir vaka pilotta görülürse.
- **Otomatik yayın (autoposting)** — konu değil: başlık modelini çağırmıyor, yalnız görsel üretiyor
  (`app/routers/internal.py::trigger_autopost`); canlıda yapılandırma 0 (ölçüldü).
- **Marka ataması + md-17** — ev: Task 19 Step 11 (hat planı), Eray'ın video sistemi değişikliğinden sonra.
- **Kök perakende rehberi susuyor (madde 12)** — ev: Plan 2 kapanışı (mevcut).
- **Takvime yeni gün (K-01a)** — tetikli (spec §5).
- **HMAC imzalı beyan** — D5'te gerekçeyle reddedildi (sunucu tarafı saklama aynı güvenceyi yeni sır olmadan verir).
- **Elle oluşturma ucu (`posts.py::create_post`)** — konu değil: model metni yoktur, metni kullanıcı yazar (D13).

## Riskler

- Model kimlik listesini eksik döndürebilir → üretim geçersiz (açık hata). Sıklık ÖLÇÜLMEDİ; sınavda "kapı düşme sayısı" satırı ölçer.
- D13 kullanıcıya görünür bir davranış değişikliğidir: makbuzu kaybolan (ör. sayfa yenilenen) paketli metin kaydedilemez,
  yeniden üretilmesi gerekir (422 iletisi). Bugün pakete atanmış marka 0 olduğu için canlı etkisi yok; atamadan sonra
  sıklık ölçülmedi.
- Yeni koşu 1. sürümdeki onaylı içeriği de değiştirebilir → Task 19 onay özetinde her değişen birim Eray'a gösterilir.
- Koşu açık soruyla durmayabilir → DUR-1.
- Telegram açıklama sınırı belge değeriyle kuruldu (ölçülmedi) → Task 21 dumanında gerçek gönderimle ölçülür.
- K-A kalan riski (spec §6): kullanıcı ifşaya rağmen onaylar; beyan modelindir ("uyuldu" yanlış olabilir) → sessiz ihlal kapısı.

## Codex plan review kayıtları

Ham çıktı: `codex_plan_review_log` (bu makinede). Ön-analiz (Adım 6, `task --fresh`, 19:04–19:08 UTC) ve Tur 1'in
girdisi: substratın dışladığı yedi dosyanın kesitleri prompta VERİ olarak eklendi (34.127 bayt; sır taraması temiz).

**Tur 1 (2026-09-25 19:35–19:41 UTC, `adversarial-review --scope working-tree`, 40 komut): needs-attention** —
1 critical · 4 high · 2 medium, hepsi contract-level; Claude hepsini kodla doğruladı.

| F | Ağırlık | Başlık | Doğrulama | Disposition |
|---|---|---|---|---|
| F1 | critical | Makbuz düşürülerek ifşa atlanıyor | doğru — `resolve_persist_stamp` makbuzsuzda `(None, None)` döner | fixed → D13, Task 13 (`StampRequiredError`, kayıt matrisi) |
| F2 | high | Geri dönüş tabanı 038 ile uyumsuz | doğru — ara commit'ler 2. sürümü okur, beyan yazmaz; D7 kısıtı reddeder | fixed → Global Constraints, D7, Task 17 runbook kuralı, Task 21 provası |
| F3 | high | Kısmi beyan kaybı kayıtta görünmüyor | doğru — istemci taşıması tamlığı ölçemez | fixed → D5 (makbuz beyan tablosu, istemci taşımaz), Task 12, Task 13 |
| F4 | high | Özel gün tür kapısı açık isteği reddediyor | doğru — spec §3.2 "istek hariç" | fixed → D14, Task 10 tür kapısı matrisi |
| F5 | high | Kısa video reddi pahalı işlerden sonra | doğru — sonlandırma TTS/durağan görselden sonra | fixed → Task 13 yan etkisiz ön kontrol + sonlandırmada yeniden doğrulama |
| F6 | medium | Paketli yolda yedek metin 200 döner | doğru — anahtar yok / model istisnası dalları | fixed → D6, Task 10 |
| F7 | medium | Telegram sınırı son mesajda ölçülmüyor | doğru — n8n platform/URL ekliyor | fixed → D8, Task 14 (son metinler backend'de), Task 16 |

EXECUTE-NOTE (Task 1 adımı ile imza notu çelişkisi) → plan metninde düzeltildi. Claude'un kendi düzeltmesi:
Task 22 md-18 olay akışıyla geri alma (`deaktive-et` tek yönlü). Sıra değişikliği: beyanın saklanması Task 10'dan
Task 13'e taşındı (tablo Task 12'de doğar).

**Tur 2 (2026-09-25 19:53–19:58 UTC, kapanış doğrulama + derin geçiş, 56 komut): needs-attention** — F1 · F2 · F3 ·
F4 · F6 · F7 KAPALI (hakem teyidi); F5 dar hâliyle açık; 3 yeni high + 1 medium. Claude beşini de doğruladı.

| F | Ağırlık | Başlık | Doğrulama | Disposition |
|---|---|---|---|---|
| F5 | high | Eşzamanlı aynı-makbuz kısa video isteğinde kaybeden pahalı işten sonra reddediliyor | doğru — sihirbazda yalnız durum tabanlı çift tık koruması var (`setGenerating(true)`), ref kilidi yok | fixed → Task 12 `claimed_post_id`, Task 13 `claim_receipt_for_post` (gönderi satırıyla aynı transaction, dış çağrılardan önce) + eşzamanlılık testi |
| N1 | high | Plan öncesine dönüş, kayıtlı paketli gönderilerin ifşasını kaldırır | doğru — eski arayüz/n8n beyanı göstermez | fixed → D7, Global Constraints, Task 17 runbook kapısı (yayımlanmamış paketli gönderi = 0), Task 21 provası |
| N2 | high | Telegram sayacı kural adını gizliyor | doğru — spec §3.12 "kural adıyla"; sayaç Tur 1 düzeltmesinin yan etkisi | fixed → D8 Telegram invariantı, Task 14 sıralı mesaj listesi, Task 16 sırayı koruyan tek gönderim düğümü |
| N3 | high | Tek tık yayın `uygulanamadi`yı göstermeden ilerliyor | doğru — kapı yalnız "çiğnenen"e bağlıydı | fixed → D8, Task 15 (`uyuldu` dışı her karar; tek tık eylem kümesi sayılır) |
| N4 | medium | Beyan tablosu marka silinince yetim veri bırakıyor | doğru — `brands.py` silmesi posts/stamps'i CASCADE ile siler, yeni tablo bağsızdı | fixed → Task 12 `brand_id` + `ON DELETE CASCADE` (makbuza FK yine YOK) + test |

**Tur 3 (2026-09-25 20:05–20:09 UTC, kapanış doğrulama, 29 komut): needs-attention** — F5 · N1 · N2 · N3 · N4 KAPALI
(hakem teyidi); kapalılardan yeniden açılan YOK; 1 yeni high.

| F | Ağırlık | Başlık | Doğrulama | Disposition |
|---|---|---|---|---|
| X1 | high | Normal kayıt, kısa videonun sahiplendiği makbuzu tüketebilir | doğru — sahiplik yalnız kısa video tüketicisinde denetleniyordu | fixed → Task 13: sahiplik şartı makbuz tüketiminin TEK geçidinde (`resolve_persist_stamp(..., claimant_post_id)`); tüketici × sahiplik matrisi, tüketici listesi koddan |

Çerçeve sorusu (3. tur kuralı): F5 → X1 aynı kümenin (makbuz eşzamanlılığı) üçüncü turudur. Kök neden tekti — sahiplik
denetimi tüketici başına yazılıyordu; çerçeve onu kapatabilir: denetim tüm tüketicilerin geçtiği tek fonksiyona
taşındı (varyant yaması değil, sınıf kapanışı). EXECUTE-DEVİR: eşzamanlılık matrisini başarısızlık/sahiplik bırakma
hücreleriyle genişlet (Codex Tur 3 EXECUTE-NOTES).

**Tur 4 (2026-09-25 20:11–20:13 UTC, kapanış doğrulama, 14 komut): needs-attention** — X1 KAPALI (hakem teyidi);
1 yeni high.

| F | Ağırlık | Başlık | Doğrulama | Disposition |
|---|---|---|---|---|
| X2 | high | Sahiplik ve tüketim ortak sıralama garantisi taşımıyor | doğru — farklı satırlarda koşullu güncelleme READ COMMITTED altında birbirini beklemez | **kapsam daraltıldı (Eray kararı):** Task 13 serileştirme invariantı + bilinen tuzak + ZORUNLU gerçek veritabanı yarış testi; mekanizma Task 13 yürütme checkpoint'inde kapanır. **Plan düzeyinde hakem teyidi YOK** (Eray: tur uzatılmadı). |

**4-tavan DUR (2026-09-25):** "makbuz eşzamanlılığı" kümesi dört turda kapanmadı (F5 → F5 dar → X1 → X2). DUR raporu
yargısı: dizi DARALIYORDU (aynı seam derinleşiyor), saçılmıyordu. Eray'ın seçimi: **"Kuralı yaz, kilidi koda bırak"**
(seçenekler: devam + 1 tur / kuralı yaz, kilidi koda bırak / durdur). Karar sonrası doğrulama turu KOŞULMADI (Auto-Fix
politikası: karar-sonrası reflekssel re-review yasak). EXECUTE-DEVİR: yarış testinde normal kayıt ve kısa video
sahipliğini commit öncesi karşı karşıya getir; tek kazananı, makbuz durumunu ve TTS/görsel çağrı sayısını birlikte
doğrula (Codex Tur 4 EXECUTE-NOTES).

**Zincir özeti:** ön-analiz + 4 review turu (19:04–19:08 · 19:35–19:41 · 19:53–19:58 · 20:05–20:09 · 20:11–20:13 UTC).
Bulgu (kayıt tablosundan sayıldı): 13 ayrı bulgu — 1 critical (F1) · 9 high (F2, F3, F4, F5, N1, N2, N3, X1, X2) ·
3 medium (F6, F7, N4) · 0 low; F5 iki turda aynı kimlikle sürdü. Kapanan: 12 (hakem teyitli); kapsamı daraltılan: 1
(X2, hakem teyitsiz). Yeniden açılan kapalı bulgu: 0.
