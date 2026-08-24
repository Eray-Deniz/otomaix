---
title: Sektör Bilgi Paketi Sistemi — Spec (sentez-temelli)
status: spec-approved
date: 2026-08-23
approved: 2026-08-23 (Eray; 45/45 ürün kararı tek tek kapatıldıktan sonra)
codex_review_status: approved
codex_review_iterations: 3
codex_review_findings: "11 bulgu (8 yuksek, 3 orta) + 1 tur-2 regresyonu; tumu cozuldu; tur-3 SHIP"
codex_review_log: docs/reviews/codex/2026-08-23-sektor-bilgi-paketi-spec.md
supersedes: docs/specs/2026-07-11-sektor-bilgi-paketi.md
input: docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md (kaynak commit c380e37, sha f056988d…)
tags: [social-backend, social-frontend, sector-packages, prompt-injection, taxonomy, regression-gate, policy-engine, migrations]
---

# Sektör Bilgi Paketi Sistemi — Spec

> **Girdi ve karar uzayı:** Bu spec YALNIZ sentez girdisinden yazılır
> (`docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md`); eski spec/plan
> (2026-07-11/12) superseded'dir ve dikkate alınmaz (Eray kararı, 2026-08-23).
> `K-xx` / `R-xx` ID'leri sentez Bölüm 17/18 uzayıdır; kanonik karar kayıtları
> snapshot Ek B'dedir. Açık kararlar karar uydurmadan K-ID atfıyla taşınır.

## Yazım yöntemi (asıl evi bu dosya — HANDOFF'tan taşındı, Eray onayı 2026-08-21)

1. **Parçalı yazım:** her bölüm için spec-input'un ilgili bölümü + snapshot Bölüm 17'nin ilgili
   kararları okunur; ~570 KB girdi (taze ölçüm: 569.814 bayt, 2026-08-21 snapshot)
   hiçbir adımda tek geçişte açılmaz.
2. **Kopyalama değil atıf:** kanonik ayrıntı spec-input'ta kalır; spec uygulanabilir
   sözleşmeleri damıtır, açık kararlara K-ID ile atıf yapar.
3. **Bağımlılığın taşıyıcısı K-ID'dir:** çok bölümü etkileyen karar her bölümde AYNI
   K-ID ile görünür, tanımı tek yerde yaşar.
4. **Sözleşmeler tek bölümde tanımlanır**, diğerleri atıf yapar; yazım sırası bağımlılık
   yönünde (önce veri + sözleşmeler, sonra tüketen akışlar).
5. **Her bölüm sonunda mekanik tutarlılık taraması** (K-ID / alan adı / enum grep'i —
   iskelet ve önceki bölümlerle karşılaştırma).
6. **Final bütünlük turu + tam dosya Codex adversarial review** — yazım parçalı,
   DENETİM BÜTÜNDÜR; bu tur atlanamaz.

## Kapanış durumu (spec'i şekillendiren kararlar)

- **K-22 = A** — politika motoru Faz 1'de (Eray, 2026-08-21).
- **K-27 = A** — yönetici turu Claude Code komut ailesinden; **taze ölçüm 2026-08-23:
  aile bugün YOK → kurulumu bu işin kapsamına girer.**
- **K-30 = A** — aktivasyon Faz 1'de, kullanım sinyali beklenmez (risk kabulü).
- **K-05 = B** — kanal envanteri Faz 1'de bu işte; Marka DNA sınırı bu spec'te çizilir.
- **K-20 = A** — Katman-1 düzeneği Marka DNA işiyle ortak (kaynak hükmü:
  "ikinci altyapı kurulmaz", DNA karar belgesi md. 7).
- **K-21 = C** — "22 sektör hedefi" kaynaksız sayı, düşürüldü (2026-08-23 iz sürümü:
  ifade ilk kez 2026-08-11 ek-analizde; ölçülmüş gerçekler 12 kök sektör · 22 legacy
  şablon · 22 takvim kaydı). Ölçek gerekçesi ölçülmüş sayılara dayanır; ≤5 Faz 1
  tavanı TAHMİN etiketiyle kalır, kapı yapılmaz (K-13).

## İskelet (bölümler + tek cümlelik sorumluluk)

| # | Bölüm | Sorumluluğu (tek cümle) | Ana girdi (snapshot) |
|---|-------|--------------------------|----------------------|
| 1 | Özet ve hedef | Problem (sektörel ayrışmama), hedef ve iki katmanlı başarı ölçütü (Katman-1 byte-exact değişmezlik · Katman-2 kör değerlendirme) bağlanır | §1, §2 |
| 2 | Kapsam ve fazlar | Kapsam içi/dışı sınır; bu iş = Faz 1 (+pilot), Faz 2 kalemleri evleriyle dışarıda; dört kapalı kararın kapsam yerleşimi (motor+envanter+aktivasyon Faz 1'de, komut ailesi kurulur) | §3, Ek B |
| 3 | Veri mimarisi | İki yeni tablo (ham artefakt salt-ekleme · paket sürümlü), `brands.sub_sector_id`, migration 032, kimlik/durum/sürüm alanları, karar günlüğü, damga veri yeri (K-07) | §6 |
| 4 | Çekirdek sözleşmeler | Tek-kapı enjeksiyon, blok şablonu + kullanım talimatı (K-04), özel gün anahtar sözleşmesi (K-01b), öncelik hiyerarşisi (DNA>paket; yasak kelime mutlak), yan-yana basım yasağı | §4, §10.2, §11 |
| 5 | Katman-1 doğrulama düzeneği | Prompt yakalama + byte-exact regresyon; yüzey kümesi ÖLÇÜMLE kapalı (caption[+carousel dalı] · görsel · kısa video 2 mod · fikir önerme · legacy); Marka DNA ile ortak koşum (K-20=A) | §13.3, §2.3 |
| 6 | Taksonomi korumaları | Alt-sektör satırlarının kök invariantını bozmaması: çözücü kök filtresi (R-01), sektör listesi filtresi (R-02), trend katmanı bağışıklığının korunması | §3.1, §21.1 |
| 7 | Atama akışı | LLM önerir + kullanıcı teyit eder; kapalı aday listesi; teyit bileşeni onboarding + marka ayarlarında (K-19 kapandı) | §9 |
| 8 | Araştırma→hakemlik→sentez hattı | Üretim hattının değişmez sözleşmeleri (körlük, denetçi karar vermez, salt-ekleme, çıkarma pozitif kanıt ister) ve sözleşme drift'lerinin kapanışı | §7.1–7.6, §14 |
| 9 | Politika motoru (Faz 1) | Kural seti, kararsız davranışı (K-23), eşik kalibrasyonu pilotta (K-24), günlük aktör alanı (K-25), kuru mod (K-133), `active`e dokunamaz (K-28) | §7.7, §19.6–19.8 |
| 10 | Yaşam döngüsü ve aktivasyon | draft→active geçişi yalnız yönetici; atomiklik (R-17); rollback; önbellek tazeleme AÇIK ADIM (K-109 — ölçüldü: kendiliğinden tazeleme yok, 1 saat TTL) | §8, §10.5 |
| 11 | Koşullu akışlar | Özel gün akışı (anma bugünkü takvimle tetiklenemez — taze ölçüm; K-01a), tür etiketi çakışması (K-03: paket kazanır), hareket dili (K-02), tur dışı acil güncelleme | §11 |
| 12 | Kanal envanteri (K-05=B) | Envanterin veri yeri + marka gerçeği filtresi; Marka DNA işiyle sınır çizgisi | §5.3, §12 |
| 13 | Komut ailesi (K-27=A) | Yönetici turunun Claude Code komut koreografisi; aile SIFIRDAN kurulur (taze ölçüm: yok); yetki ayrımı (R-24) | §14, §15 |
| 14 | Doğrulama ve kabul | Kabul matrisi; ölçülmemiş değerler kapı YAPILMAZ (token maliyeti, ≤5 tavanı, tur süresi — İlke 9); güvenlik testleri (K-10 prompt-injection savunması) | §13 |
| 15 | Pilot (kuyumculuk) | Elle resmî tur; ölçüm hedefleri: yöneticinin tur başına gerçek süresi (ölçek gerekçesinin ölçümü), Katman-2 kör değerlendirme | §16 |
| 16 | Riskler | Snapshot §18'den bu spec kapsamına düşen riskler + izleme sinyalleri | §18 |
| 17 | Kapsam dışı ve dokunulmazlar | Kapsam-dışılar evleriyle; dokunulmazlar: `brands.sector` TEXT, SECTOR_GUIDANCE yan-yana yasağı; legacy kısa video yolunun akıbeti (K-06 — açık ürün kararı, sessiz bırakılmaz) | §3.2, §16.1 |

## Bağımlılık haritası (yazım sırası bu yönde)

```
3 (veri) ──► 4 (sözleşmeler) ──► 5 (Katman-1)
   │              │                  │
   ▼              ▼                  ▼
6 (taksonomi)  8 (hat) ──► 9 (motor) ──► 10 (yaşam döngüsü)
   │              │                        │
   ▼              ▼                        ▼
7 (atama)     11 (koşullu)             13 (komut ailesi)
                  │                        │
                  ▼                        ▼
12 (envanter) ─► 14 (doğrulama) ──► 15 (pilot) ──► 16-17 (risk/kapsam dışı)
```

- Bölüm 1–2 çerçevedir, en başta yazılır; 3→4→5 zinciri sözleşme temelini kurar,
  diğer her bölüm bunlara atıf yapar.
- Çapraz-kesen kararlar (her göründüğü bölümde aynı ID): K-01b (4, 8, 11) ·
  K-07 (3, 10) · K-20 (5, 14) · K-28 (9, 10) · K-06 (5, 17).

## Açık kararlar envanteri (spec'e K-ID atfıyla taşınacak)

Snapshot Bölüm 17 taze ölçümü (2026-08-21): 162 karar = 153 açık + 9 kapalı; bu spec'in
kapanışlarıyla (K-20, K-21) kalan açıklar ilgili bölümlerde K-ID atfıyla görünür.
Ürün kararı gerektiren noktada karar uydurulmaz (spec'e geçiş hükmü, snapshot Bölüm 20).

---

# 1. Özet ve hedef

*(Girdi: snapshot §1, §2. Kod/DB olguları 2026-08-23'te taze doğrulandı — aşağıda
"taze ölçüm" etiketiyle.)*

## 1.1 Problem

**Birinci problem — sektörel ayrışmama (mevcut sistem olgusu, taze doğrulandı):**
Marka bir kök sektör kovasına atanır (`brands.sector_id` → `social.sectors`; tabloda
12 kök satır — taze ölçüm 2026-08-23). Üç kök neden:

1. **Çözünürlük düşüklüğü** — alt sektör karşılığı yok; kuyumculuk geniş kovada eriyor
   veya `genel`e düşüyor (12 kökün hepsi `parent_sector_id = NULL` — taze ölçüm).
2. **Derinlik yetersizliği** — `SECTOR_GUIDANCE` caption yönelimli (12 anahtar — taze
   sayım); görsel kod, sektörel CTA, video hareket/sahne dili, özel gün kalıbı yok.
3. **Görsel yüzeye taşınmama** — sektör görsel/video prompt'una tek satır gidiyor
   (`short_video.py:129`, `Industry: {sector}` — taze doğrulandı).

Ayrışma eksikliğinin oranı/müşteri etkisi **ölçülmemiştir**; kanıt gözlem + kök-neden
taramasıdır.

**İkinci problem — hedef işletim modelinde bakım riski (mevcut olgu DEĞİL):** Paket
bakımı kalıp-başına insan kararı gerektirirse yük sektör × alan × kalıp × tur çarpımıyla
büyür. "İnsan eliyle aylar sürer" iddiası **ölçülmemiş tahmindir** ve hiçbir katmanda
kapı yapılmaz; pilotta yöneticinin tur başına gerçek süresi ölçülür. Ele alınma yönü:
kalıp-başına karar kontrolü **politika motoruna** devredilir (Bölüm 9); insan onayı
aktivasyonda toplanır (K-22=A) — ⚠️ K-23'ün bir seçeneği kararsız maddeleri yöneticiye
düşürür; o seçenek benimsenirse aktivasyonun yanında ikinci bir müdahale noktası
doğar (K-23 açık). Ölçek gerekçesinin sayısal dayanağı: **K-21=C
kapanışıyla "22 sektör" düşürüldü** (kaynaksız sayı — bkz. Kapanış durumu); ölçülmüş
gerçekler 12 kök sektör; Faz 1 tavanı ≤5 **tahmin etiketiyle** kalır (K-13).

## 1.2 Hedef

- **Ana hedef:** Paketli/paketsiz üretim yan yana konduğunda sektörel ayrışma
  gözlenebilir olmalı; **paketsiz markada modele giden mevcut prompt parçaları
  byte-exact değişmemeli.**
- **Kullanıcı değeri:** sektörüne ait hissettiren, mevzuat hassasiyetlerini ve özel
  günlerde kültürel uygunluğu hedefleyen içerik.
- **İş değeri:** sektörel bilgi sürümlü varlığa dönüşür; yeni sektör eklemek prompt
  cerrahisi değil veri işi olur; kalite regresyonları paket sürümüne izlenebilir
  (fiziksel temsil **K-07** — Bölüm 3'te bağlanır).
- **Teknik hedef:** mevcut Tier 1/2/3 yapısını koruyarak koşullu ve **geri alınabilir**
  bir bilgi katmanı eklemek. Önbellek tazeleme davranışı Bölüm 10'da bağlanır
  (**K-109**; taze ölçüm: bugünkü sektör önbelleği 1 saat TTL, kendiliğinden
  tazeleme yok).

**Paket nitelikleri (her desteklenen alt sektör için):** Türkiye pazarına uygun ·
kaynakları izlenebilir · iki bağımsız kör denetimden geçmiş · sürümlü ve geri
alınabilir · caption/fikir/görsel/video üretiminde kullanılabilir · özel günlerde
koşullu derinleşebilir.

## 1.3 Başarı ölçütleri — iki katman (birbirinin yerine geçmez)

- **Katman-1 — deterministik prompt kapısı (zorunlu, otomatik):** modele giden prompt
  parçaları yakalanır, değişiklik öncesi dondurulmuş fixture ile **byte-exact**
  karşılaştırılır. Karşılaştırılan LLM çıktısı değil, **modele gönderilen prompt
  metnidir** (üretim stokastik: `temperature=1.0`, seed yok). Düzenek Bölüm 5'te.
- **Katman-2 — çıktı-düzeyi kör örneklem:** paketli/paketsiz çıktılar kör
  değerlendirilir. **Operatör onayının girdisidir, otomatik kapı değildir.**
  Örneklem boyutu ve eşik **K-11 (a)/(b)** — pilot kanıtından sonra belirlenir.

**Deterministik kabul koşulları:**
1. Ham artefakt tablosunda `UPDATE`/`DELETE` hata fırlatır (salt-ekleme, DB seviyesi).
2. Sektör başına ikinci `active` paket kısmi benzersiz indeksle reddedilir.
3. Koşu artefaktları `run_id` altında sorgulanabilir.
4. Paketsiz markada tüm prompt yüzeylerinde fixture'a karşı byte-exact eşitlik
   (yüzey kümesi Bölüm 5'te ölçümle kapalı).

**Kesin başarısızlık durumları:**
- Paketsiz markanın prompt'unda fixture'a göre **tek bayt** fark.
- Paketli markada paket bloğu ile `SECTOR_GUIDANCE`'ın **birlikte basılması**
  (yan-yana yasağı — Bölüm 4).
- Alt-sektör satırı eklendikten sonra mevcut bir markanın `sector_id` değerinin
  değişmesi (R-01 — Bölüm 6).

**Kalite sinyali (kesin başarısızlık değil):** kör değerlendirmede ayrışmanın
gözlenmemesi aktivasyon kararında olumsuz sinyaldir; otomatik red eşiği K-11 (b)
kapanmadan tanımlanmaz.

**Ölçülmemiş ve kapıya çevrilmeyecek değerler (İlke 9):** Faz 1 paket tavanı (≤5,
K-13) · tur süresi · Katman-2 örneklem/eşiği (K-11) · paket token maliyeti (K-12,
iki uzlaştırılmamış tahmin) · "aylar sürer" iddiası. Hiçbiri kabul kriteri, eşik
veya ölçüm kapısı yapılmaz.

**Bilinçli izleme dışı:** paketin gerçek pazarlama etkisi (etkileşim/dönüşüm) Faz 2
kanıt döngüsünün işidir; Faz 1'de sürüm damgası bu yüzden zorunludur — damga olmadan
geçmiş üretim, paket sürümüyle geriye dönük ilişkilendirilemez.

---

# 2. Kapsam ve fazlar

*(Girdi: snapshot §3, Ek B. Bu iş = **Faz 1** + kuyumculuk pilotu; "Faz 2" burada
yalnız kapsam-dışı kalemlerin evi olarak geçer.)*

## 2.1 Kapsam içinde

**Veri ve taksonomi** *(Bölüm 3, 6'da bağlanır)*
- Alt sektörler **yeni tablo değil**, `social.sectors` içinde `parent_sector_id` ile
  (kolon mevcut ve 12 satırın hepsinde NULL — taze ölçüm 2026-08-23).
- `brands.sub_sector_id` (yeni, null olabilir FK) — paket yolunun anahtarı.
- `social.sector_research_artifacts` (ham katman, salt-ekleme) ve
  `social.sector_packages` (tek JSONB `content` + karar günlüğü;
  `draft`/`active`/`archived`).
- Migration numarası: **032'den başlar** (canlı düzen 001-031 — taze ölçüm; snapshot'ın
  "001-030" aktarımı bayatlamıştı, düzeltildi).

**Üretim hattı** *(Bölüm 8-9)*
- Araştırma brief'i + biçimsel eleme (`brief-doctor`) · iki bağımsız kör hakem denetimi ·
  alan bazlı evrimsel sentez ve `draft` üretimi.
- **Politika motoru (K-22=A — Faz 1):** girdisi sentez çıktısı + aktif paket +
  çıkarılanlar listesi; çıktısı uygulanmış karar seti + özet diff + koşu raporu.
  Kalıp kimliği sözleşmesi motorun **ön koşuludur** (**K-84** açık; biçimi K-151,
  üretimi K-152 — Bölüm 9'da bağlanır).
- Yönetici koşu yüzeyi **Claude Code komut ailesi** (K-27=A; taze ölçüm: aile bugün
  yok, kurulumu bu kapsamdadır — Bölüm 13).

**Enjeksiyon yüzeyleri** *(Bölüm 4-5)*
- Caption + fikir üretimine Tier 2 gövdesi olarak (mevcut `SECTOR_GUIDANCE` metninin
  **yerine**, yanına değil).
- Görsel ve kısa video bağlamına sektör görsel dili (kısa video iki mod).
- Özel gün kalıplarının Tier 3'te koşullu enjeksiyonu (K-01b anahtar sözleşmesi).

**İzlenebilirlik ve doğrulama** *(Bölüm 5, 14)*
- Post ↔ paket sürümü bağı (fiziksel temsil K-07).
- Katman-1 prompt kapısı + Katman-2 kör örneklem (K-20=A: düzenek Marka DNA işiyle ortak).

**Kanal envanteri (K-05=B — Faz 1)** *(Bölüm 12)*: `[kanal-bağımlı: X]` kalıplar için
kullanım-talimatı önlemi korunur; deterministik filtrenin envantere bağlanışı ve Marka
DNA sınırı Bölüm 12'de çizilir.

**Pilot** *(Bölüm 15)*: kuyumculuk — paket üretimi + kapı testi + tur süresi ölçümü.

## 2.2 Kapsam dışında (evleriyle)

| Kalem | Ev / yeniden ele alma koşulu |
|---|---|
| Sosyal platformlardan otomatik veri toplama (tarayıcı ajanı) | Hukuki görüş alındığında |
| Marka örnek postlarının otomatik toplanması | Marka DNA karar dokümanı, Faz 2 |
| pgvector / embedding örnek havuzu | Few-shot ihtiyacı ölçülürse (Faz 2) |
| Araştırma **girdi toplamanın** otomasyonu (KAYNAK-1/2/3 elde kalır) | Tur maliyeti ölçüldükten sonra. ⚠️ *Karar kontrolü* kapsam DIŞI değildir — motor kapsamdadır |
| Müşteri etkileşim verisiyle kanıt döngüsü | Faz 2; ön koşulu K-07 damgasının Faz 1'de kurulması |
| Paketlerin ürünleştirilip satılması | Hukuki görüş eşiği |
| Kök trend sorgularının alt-sektör kelimeleriyle zenginleştirilmesi | Sektör karar dokümanı "Kapsam dışı (Faz 2)" listesi |
| Marka DNA alanları (`voice_profile` · `banned_words` · `target_audience` · `example_posts`) | Ayrı, onaylı Marka DNA işi (G1); kesişim: hiyerarşi (Bölüm 4) + kontrast referansı (Bölüm 12) |
| Bakım borçları: `brands.sector` TEXT tekilleştirme · LinkedIn `long` · 22 legacy şablonun `active` statüsü (sayı taze doğrulandı: 28 şablonun 22'si) | Bu işte **dokunulmaz** (snapshot Bölüm 17'ye kapsam kararı olarak taşınmış; ele alınma hedefi YOK — dürüst kayıt) |

## 2.3 Aktörler ve yetki özeti

- **Otomaix müşterisi:** paket bakımıyla İLGİSİZ; yalnız kendi markasının alt-sektörünü
  teyit eder (Bölüm 7). Üretim akışına **yeni soru eklenmez** (sürtünme yasağı).
- **Otomaix yöneticisi (koşu + aktivasyon):** turu koşar, KAYNAK-1/2/3 yükler, özet
  diff'e bakıp **aktivasyon/ret/rollback onayı** verir; kalıp-kalıp karar vermez;
  motoru atlayarak aktive edemez. ⚠️ K-23'ün yöneticiye-düşürme seçeneği benimsenirse
  kararsız maddeler ikinci müdahale noktası olur (K-23 açık). Tur periyodu **K-149 —
  KAPANDI (Eray, 2026-08-23): 6 ayla başlanır** (ilk tur ölçümüyle revize edilebilir);
  saklama **K-26 — kapandı: sektör başına alan + vade
  bildirimi** (13.3).
- **Denetçi-1/2 (yeni roller):** bağımsız, kör iddia denetimi; nihai paket kararı
  vermez. Denetçi-2 web erişimi + ön kontrol **K-14** (açık); paralel/sıralı yürütme
  **K-78** (açık), izolasyon + aynı-girdi teknik garantisi **K-79 — KAPANDI (Eray,
  2026-08-23): EVET, hafif** — komut ailesi aynı dosya setini iki izole oturuma
  vermeyi kod düzeyinde zorlar.
- **Sentez rolü:** alan-alan karar; adayı doğrudan aktive edemez.
- **Politika motoru:** karar setini uygular; `active`'e geçirme yetkisi YOKTUR (K-28).
- **Rol bölünmesi** (operasyon rolü ↔ ürün sahibi): **K-54 — KAPANDI (Eray,
  2026-08-23): BÖLÜNMEZ** — solo işletim, tek yönetici rolü; bağımsızlık iki kör
  denetçiden gelir. Ölçek gelince yeniden açılır. Yetki dağılımı Bölüm 13'te.

## 2.4 Varsayımlar ve kısıtlar (taze doğrulama durumlarıyla)

- `sectors.parent_sector_id` mevcut ve boş — **taze ölçüm 2026-08-23** (12 kök, 0 alt).
- `social` şemasında PK'lar uuid; migration düzeni 001-031 — **taze ölçüm** (032 sıradaki).
- Marka sayısı düşük: **2 marka — taze ölçüm**; markalar elle atanır, toplu geriye
  dönük atama başlangıç kapsamında değil.
- Paket token maliyeti ~1,2-2K token / ~1 cent — **ölçülmemiş, iki uzlaştırılmamış
  tahmin (K-12)**; kapı yapılmaz.
- Paketin Tier 2'yi önbellek eşiği üstüne taşıması — **ölçülmemiş öngörü**; tazeleme
  davranışı Bölüm 10'da (K-109).
- Araştırma elle ve maliyetli → sözleşmeler donmadan yeniden koşulmaz (**K-18**, kapalı).
- Hat doğrulaması canlı görsel üretimiyle YAPILMAZ — yerel/ucuz katmanla (kredi israfı
  yasağı).
- Görselde metin yasağı: kanonik biçim araştırma brief şablonunda; ölçüt öğenin
  **metin taşıması** (kapalı liste değil). Üretim hattının yasağı fiilen uyguladığı
  doğrulanmadı — Katman-2 gözlem kalemi.

---

# 3. Veri mimarisi

*(Girdi: snapshot §6. Şema taslakları `[TASLAK]` statüsünden uygulanabilir sözleşmeye
burada damıtılır; açık karara bağlı alanlar K-ID ile işaretli kalır, migration
kesinleştirmesi plan/execute işidir.)*

## 3.1 İki katman ilkesi

- **Ham kanıt katmanı** (`social.sector_research_artifacts`): araştırma/denetim/sentez
  çıktıları değiştirilmeden saklanır. **Salt-ekleme DB düzeyinde zorlanır** —
  `UPDATE`/`DELETE` tetikleyiciyle reddedilir; uygulama disiplinine bırakılmaz.
- **Türetilmiş paket katmanı** (`social.sector_packages`): sürümlü, durum taşıyan
  operasyonel paket. **Prompt'a giren tek şey budur.**
- Katmanlar arası bağ `run_id`'dir. ⚠️ Paket tarafında alanın **zorunlu kılınıp
  kılınmayacağı K-110'da açık** (provenans garantisi buna dayanır); sürüm-oluşturmayan
  koşuların kayıt yeri **K-93** (Bölüm 9.5).

## 3.2 Taksonomi kararları (kaynakta onaylı)

- Ayrı alt-sektör tablosu **kurulmaz**; alt sektörler `social.sectors`a
  `parent_sector_id` dolu satırlar olarak girer (taze ölçüm: kolon var, 12 satırın
  hepsi NULL).
- `brands.sector_id` **kök kova anlamını korur**; alt sektör bağı **ayrı ve null
  olabilir** `brands.sub_sector_id` ile taşınır (dolu → paket yolu, boş → mevcut yol).
- `brands.sector` (TEXT) **dokunulmaz canlı girdidir** (video director, fikir önerme,
  rakip analizi, legacy yollar okur); tekilleştirme kapsam dışı bakım borcu.
- ⚠️ `sub_sector_id`'nin **yalnız alt-sektör satırı kabul etmesi** FK ile kendiliğinden
  sağlanmaz (kök+alt aynı tabloda) — DB'de mi uygulamada mı zorlanacağı **K-08 (b)**.
  Kısıt yazılmazsa kök kova invariantı veri tarafında korunmasız kalır; spec hükmü:
  **K-08 (b) hangi katmanı seçerse seçsin, kısıt Faz 1'de kurulur** (kısıtsız bırakma
  seçenek değildir).

## 3.3 Tablo sözleşmeleri

**`social.sector_research_artifacts`** — alanlar: `id` (uuid PK) · `run_id` (metin,
zorunlu; koşu klasörü adıyla eşliği önerisi **K-17**) · `sector_slug` (zorunlu; FK mi
serbest metin mi **K-08 (a)**) · `kind` (`research` · `review` · `synthesis` — kapalı
küme; hepsi aynı tabloda, kaynakta onaylı) · `source` (üreten araç/rol; **kalıcı kayıt K-138 —
KAPANDI, Eray 2026-08-23: KAYDEDİLİR** — kanıt zinciri bilgi→rapor→araç→tarih uçtan
uca; körlük kayıtla değil erişimle korunur · okuma yetkisi K-139 — KAPANDI, Eray
2026-08-23: ham katman + eşlemeyi YALNIZ operatör/yönetici okur; denetçiye yapısal
kapalı (K-137), müşteriye kapalı (K-16 ile tutarlı)) ·
`brief_ref` (ops.) · `content_md` (zorunlu, değiştirilemez) · `created_at`.
Ek: `(sector_slug, run_id)` indeksi · salt-ekleme tetikleyicisi · **embedding kolonu
yok** (bilinçli — erişim deterministik).

**`social.sector_packages`** — alanlar: `id` (uuid PK) · `sector_id` (uuid FK →
**alt-sektör satırı**) · `version` (sektör içinde artan) · `status`
(`draft` · `active` · `archived` — kapalı küme) · `schema_version` (alan şemasının
sürümü; içerik sürümünden ayrı) · `content` (JSONB) · `decision_log` (JSONB, varsayılan
`[]`) · `run_id` (bkz. 3.1 açıklığı) · `created_at` · `activated_at` (yalnız aktive
edilmişte dolu).
**İki DB garantisi (kaynakta onaylı):** `(sector_id, version)` benzersiz + sektör
başına tek `active` (kısmi benzersiz indeks). Salt-ekleme tetikleyicisi bu tabloya
**bilinçli konmaz** — durum geçişleri meşru güncellemedir.

**Adlandırma uyarısı (taze doğrulandı):** şemada `sector_reports` ve
`sector_trend_cache` bugün mevcut — yeni tablo adları bunlarla karışmamalıdır.

## 3.4 `content` alan şeması

Brief çıktı sözleşmesiyle **aynı kapalı küme** (sekiz temel alan + `ozel_gun`);
şema değişimi `schema_version` ile taşınır:

| Alan | Tip | Kural (bağlayıcı) |
|---|---|---|
| `kapsam` | metin | Alt sektör tanımı + ürün/hizmet tipleri |
| `ton_ve_dil` | metin | Sektöre özgü güven/duygu unsurlarına bağlanır |
| `cta_kaliplari` | dizi {kalıp, tür, gerekçe} | `[kanal-bağımlı: X]` etiketi **taşınır, silinmez** — çalışma zamanı marka-gerçeği filtresi (Bölüm 12) buna dayanır |
| `kanca_kaliplari` | dizi | Dağarcıktır, formül değil |
| `gorsel_kodlar` | metin (EN) | Fiziksel çekim parametresi ve görsel-içi metin öğesi yasak |
| `video_kodlar` | iki alt yapı (EN) | Hareket ve sahne kodları **ayrı**; iki yüzeye gider; nihai alan adları **K-02** |
| `takvim_temalari` | dizi | Yıllık ritim özeti; dönem ayrıntısı `ozel_gun`da |
| `yasaklar_ve_hassasiyetler` | dizi | Mevzuat maddeleri **yürürlük tarihiyle** |
| `ozel_gun` | nesne {anahtar: {tür, mesaj ekseni, kanca, cta, görsel vurgu}} | Anahtarlar **sistem takvimine karşı doğrulanır** (K-01b); uydurma anahtar üretilmez; karşılıksız dönem pakete girmez, günlüğe notlanır; paket+özel gün **atomik sürümlenir** |

> **[SONRADAN EKLENDİ — 2026-08-24; spec eksik yazıldığı için]** Tablodaki `video_kodlar`
> satırı "iki alt yapı" der ve **şeklin çoğulluğunu taşımaz**. Input aynı alanı iki ayrı
> yerde **liste/havuz** olarak yazar:
>
> - Brief çıktı sözleşmesi, GÖREV A (satır 817): *"`video_kodlar` sözleşmede **iki alt
>   listeye ayrılmıştır** — hareket kodları ve sahne kodları; ikisi üretim hattında farklı
>   yüzeylere gider."*
> - Hareket akışı, ek girdiler (satır 1717): *"Paketin video kodları alanının **hareket alt
>   listesi**; sahne alt listesi bu akışa değil durağan kare yüzeyine gider."*
> - Enjeksiyon bileşen tablosu (satır 485) hareket kaynağını **"sektör havuzu"** diye anar.
>
> "Havuz"un tekil bir cümleye indirgenmesi ürün düzeyinde bir kayıptır: sektöre özel olsa
> bile TEK hareket cümlesi, o sektörün her videosunu aynı tipte üretir. Çoğulluk bu yüzden
> biçimsel bir ayrıntı değil, alanın işlevinin parçasıdır. Alt yapıların **nihai adları**
> yine K-02'ye bağlıdır (input satır 3103: *"şablonun 6a/6b ayrımının nihai alan adlarına
> bağlanması"*).

Alan-başı karakter hedefleri ve ~6.000 karakter (≈2.000 token) toplam tavanı
**tasarım hedefidir, ölçüm değildir** (K-12'deki uzlaştırılmamış ikinci tahminle
birlikte); **kapı yapılmaz.** Asgari öğe sayıları brief biçim sözleşmesinde tanımlı
**sözleşme kurallarıdır** — mekanik elemenin girdisi (Bölüm 8).

## 3.5 `decision_log` sözleşmesi

- Satır = kalıp kararı: **alan · kalıp · karar · gerekçe · kanıt**.
- Karar enum'u **beş değerle kapalı**: `koru` · `guncelle` · `cikar` · `ekle` · `kirp`.
  Yalnız-özel-gün turunda taşınan temel alanlar da birer `koru` satırıdır — sessiz
  taşıma yok.
- ⚠️ **Yapısal açıklık (snapshot Bölüm 17'ye taşınmış):** karşılıksız-dönem notu ve reddedilen
  aday (K-87) beş değerli enum'da temsilsiz — çözüm (6. değer / ayrı not alanı /
  günlük-dışı kayıt) sentez görev sözleşmesi revizyonu gerektirir; resmî hakem turunu
  ilgilendirir.
- `cikar` kararında **pozitif kanıt satırı zorunlu** — "yeni araştırmada geçmiyor"
  tek başına gerekçe değil; kanıt yoksa kalıp korunur. **Kanıt yeterliliği eşiği —
  K-124 KAPANDI (Eray, 2026-08-23):** normal bilgi için en az 1 doğrulanmış kaynaklı
  kanıt satırı; mevzuat/güvenlik bilgisinde ek olarak iki denetçi mutabakatı —
  mutabakat yoksa çıkarma yapılmaz, madde açık soruya düşer. Eşik mekaniktir (biçim
  kontrolüyle denetlenebilir).
- `kanit` standart biçimli: denetçi satır referansı / ham kaynak referansı / URL.
  Denetçi satır numarası **değişmez satır kimliğidir** (denetçi sözleşmesinde yazılı).
- Aktör kaydı: satır-seviyesi aktör ayrımı + koşu-seviyesi motor sürüm damgası —
  **tamamlayıcı, hangisi/ikisi birden açık** (K-25 + K-97 — Bölüm 9.5).

## 3.6 Durum, sürüm, aktivasyon

- `draft` → `active` → `archived`; koşu DB'ye **yalnız `draft`** yazar; `content`
  doğrulayıcısı **yazımdan önce** koşar, reddederse yazım olmaz.
- **Aktivasyon sırası DB tarafından zorlanır:** tek-aktif kısmi indeks nedeniyle önce
  mevcut aktif **arşivlenir**, sonra yeni sürüm aktive edilir; yanlış sıra veriyi
  bozmaz, hata verir. Rollback aynı sırayla (Bölüm 10; atomiklik R-17).
- İdempotency: ham katmanda koşu kimliği + kaynak + tür üçlüsü önerisi; **aynı koşunun
  iki kez yüklenmesinin engellenmesi K-09** (orkestrasyon ayağı — zaman aşımı ve
  yeniden koşum kimliği — **K-82/K-83**, ayrı kararlar).
- **Üretim sürüm damgası:** paketli post, paket kimliği + sürümünü taşır; fiziksel
  temsil (ayrı kolon mu `posts` JSONB içinde mi) **K-07**. Paketsiz üretimde geçerli
  paket ilişkisi **bulunmaz** — byte-exact değişmezliğin veri karşılığı.

## 3.7 Saklama, gizlilik, erişim

- Ham katman ve paketler **kalıcı — K-140/K-141 KAPANDI (Eray, 2026-08-23):
  SÜRESİZ saklama** (silme kapısı açılmaz; salt-ekleme ve arşiv güvencesiyle tutarlı;
  yeniden bakış tetiği: hacim/KVKK sinyali). Aktive edilmemiş taslaklar **K-142 —
  KAPANDI (Eray, 2026-08-23): ayrı kural YOK, onlar da kalıcı** — tek saklama rejimi;
  **K-143 (taslak süresi) bu kapanışla hiç doğmaz.**
- "Kişisel veri içermez" beyanı **doğrulanmadı**; doğrulama spec'i bloklamaz ama
  **gerçek veri yazımı ve ilk aktivasyondan önce koşulur** (Bölüm 14'e kabul maddesi).
- Marka adı bayrağı taşıyan metin **pakete giremez** (kaynakta yazılı, ortak).
- Erişim: marka paketi yalnız **üretim çıktısı üzerinden dolaylı** tüketir; API'den
  okunabilirlik **K-16 — kapandı: iç kullanım + yönetici, müşteriye KAPALI** (Eray,
  2026-08-23); aktivasyon/rollback yetkilendirme modeli açık; `blocked`
  sonucun hiçbir uçtan aktive edilememesi **K-28'in sunucu tarafı uygulama ayağıdır**.

## 3.8 Migration sözleşmesi (032)

- Numara **032** (canlı düzen 001-031 — taze ölçüm); `shared/db/migrations/` altında.
- Kapsam: iki yeni tablo + `brands.sub_sector_id` + salt-ekleme tetikleyicisi +
  `(sector_id, version)` benzersizliği + tek-aktif kısmi indeks + K-08 (b) kısıtı
  (seçilen katmanda) + K-07 kararına göre posts damga temsili.
- PK'lar uuid (kaynak taslaklarındaki `BIGSERIAL` uyarlanır — kaynak bu düzeltme
  notunu kendisi taşır).

---

# 4. Çekirdek sözleşmeler (tek kapı)

*(Girdi: snapshot §4, §10. Bu bölüm çalışma zamanı davranış sözleşmelerini bağlar;
tüketen akışların ayrıntısı Bölüm 11'de.)*

## 4.1 Devreye girme ve yerine-geçme

- **Paket yolu koşulu (tek ve ortak):** `brands.sub_sector_id` dolu **VE** atanan alt
  sektörün `active` paketi var. Biri eksikse **mevcut yol** — değişiklik yok.
- **Ayrı feature flag yoktur:** paketin varlığı doğal bayraktır; geçiş veri tabanlıdır.
- **Byte-exact koruma:** paket yoluna girmeyen üretimde modele giden mevcut prompt
  parçaları **byte-exact değişmez** (yüzeyler: caption · görsel · kısa video · fikir
  önerme · legacy). Kanıt yeri Katman-1 (Bölüm 5).
- **Yan-yana basım yasağı:** aktif paket varken kök `SECTOR_GUIDANCE` bloğu paketle
  birlikte basılmaz — paket **yerine geçer**. Aynı kural **fikir önerme ucuna da**
  uygulanır; aksi hâlde öneri kök rehberle, üretim paketle konuşur (iki ses ayrışması).

## 4.2 Seçim ve yükleme

- Üç adım: marka yüklenirken `sub_sector_id` okunur → boşsa mevcut yol → doluysa
  `status='active'` paket okunur → yoksa mevcut yol.
- Sonuç **en fazla tek satırdır** — tek-aktif kısmi indeks DB düzeyinde garanti eder;
  "hangi aktif" belirsizliği çalışma zamanında oluşamaz. `draft`/`archived` çalışma
  zamanında **hiç okunmaz**.
- **Güvenli geri düşüş:** paket okunamıyorsa (`content` bozuk / sorgu hatası) tüm yol
  mevcut yola düşer; **üretim bloklanmaz**; paket-atanmış markada beklenmeyen eksiklik
  **gözlemlenebilir log** üretir.
- ⚠️ **K-15 (a) açık:** "alan eksikse yalnız o alan atlanır" dalı ile "paket okunamıyor
  → tüm yol düşer" dalının sınırı tanımsız (yazım-öncesi doğrulayıcı varken çalışma
  zamanında eksik alan zaten şema-dışıdır). Spec hükmü BEKLETİLİR — karar uydurulmaz;
  kaydı snapshot Bölüm 17'dedir (K-15 (a)).
- **Bayat atama:** arşivlenmiş paketli alt sektöre atanmış markada dolu alan tek başına
  paket yolu vermez → mevcut yola düşer (kapalı, emniyetli). Kayıt/işaretleme/bildirim
  Bölüm 7'nin açık kararları.

## 4.3 Enjeksiyon sırası (paket yoluna girildikten sonra)

```text
TIER 2  paket bloğu — kök rehberin YERİNE; bloğun başında kullanım talimatı (4.5)
TIER 3  özel gün seçili + pakette karşılığı var → dönem kalıpları;
        eşleşmezse SESSİZ DÜŞME + log (anahtar sözleşmesi 4.4)
GÖRSEL  caption director çıktı talimatına sektör görsel dili;
        eşleşen özel günde günün görsel vurgusu koşullu eklenir
VİDEO   durağan kare: İKİ modda da (metinden-görsele + ürün referanslı) — tek moda
        uygulamak yarım ayrışma; hareket: K-02 (üç seçenek — Bölüm 11)
SON     post kaydı paket kimliği+sürümüne bağlanır (K-07)
```

## 4.4 Özel gün anahtar sözleşmesi (K-01b — burada bağlanır; teknik sınıf)

- **Doğruluk kaynağı sistem takvimidir:** `social.public_holidays` (taze ölçüm
  2026-08-23: kolonlar `year·date·name_tr·name_en·category`; 2026 için 22 satır;
  kategoriler yalnız `religious·national·commercial`; yıllık n8n işi de yalnız bu üç
  kategoriyi yazar).
- **Anahtar = normalize edilmiş sistem gün adı.** Normalize fonksiyonu TEK modülde
  yaşar; **yazım tarafı** (sentez `content` doğrulayıcısı, `ozel_gun` anahtarlarını
  takvime karşı doğrular) ve **okuma tarafı** (çalışma zamanı gün eşleşmesi) **aynı
  fonksiyonu import eder** — iki ayrı normalize kopyası yazılamaz.
- Sistemde karşılığı olmayan dönem pakete giremez; karar günlüğüne notlanır (temsil
  açıklığı Bölüm 3.5). Uydurma anahtar üretilemez.
- **Taze ölçümün sonucu:** `anma` kategorisi bugünkü takvimde ve onu dolduran işte
  YOK → `anma` akışı bugünkü veriyle **tetiklenemez** (K-01a: takvime gün/kategori
  ekleme tur-dışı bir insan politika kararıdır, motor yalnız uygular). `anma`
  sözleşmesi Bölüm 11'de yazılır ama Faz 1 kabulünde test edilebilirliği bu veri
  gerçeğine bağlıdır — Bölüm 14'te işaretlenir.

## 4.5 Dağarcık kullanım talimatı (K-04 — kapalı, normatif)

Her enjeksiyon bloğunun başına sabit talimat yazılır:

> "Bu dağarcıktan içeriğe uyan 2-3 öğeyi seç; listeyi tamamlamaya çalışma; ürün veya
> marka bilgisiyle çelişen kalıbı kullanma; markanın sahip olduğunu bilmediğin kanalı
> veya hizmeti önerme."

Gerekçe: liste alanları modelde "listeyi tamamlama" refleksi tetikler — fabrication
yasağıyla çatışır. (Talimattaki "2-3" ölçülmemiş tasarım değeridir, eşik/kapı değil.) Son cümle kanal-bağımlı kalıplar için hafif önlemdir (K-05
envanter filtresiyle birlikte — Bölüm 12). Kesin prompt şablonu ve test fixture'ları
plan/execute işidir.

## 4.6 Öncelik hiyerarşisi

**Kesin uçlar (ortak, bağlayıcı):**
1. En üstte mutlak güvenlik + mevzuat + fabrication kuralları — paket geçersiz kılamaz.
2. Paket **markanın gerçeği değildir** — kullanıcının somut isteği ve gerçek ürün
   bilgisinin ALTINDA.
3. Marka DNA ↔ paket çatışırsa **DNA kazanır**; markaya özgü **yasak kelimeler**
   hiyerarşinin üstünde mutlak kısıttır.
4. En altta platform tonu + kök rehber (aktif pakette kök rehber zaten basılmaz).

**Ürün kararı uçları (ikisi de KAPANDI — Eray, 2026-08-23):**
- **K-118 — KAPANDI: kullanıcının somut isteği kazanır.** Ses/üslup
  profili yumuşak yönlendirmedir, sert kısıt değildir; markaya özgü yasak kelimeler
  (madde 3) mutlak kısıt olarak kalır.
- **K-119 — KAPANDI: `anma` satış-dili yasağı kullanıcı isteğini geçersiz kılar.**
  K-118 kuralının TEK istisnası budur; kültürel uygunluk ürünün değer vaadinin
  parçasıdır.

**Çift enjeksiyon yasağı:** sektör ortalaması pakette, markaya özgü sapma DNA'da;
aynı bilgi iki katmandan basılmaz; DNA çıkarımında aktif paket yalnız **kontrast
referansıdır** (Bölüm 12).

---

# 5. Katman-1 doğrulama düzeneği

*(Girdi: snapshot §13.3, §2.3, §10.4. K-20=A: düzenek Marka DNA işiyle ORTAK kurulur —
ikinci altyapı yok; DNA tarafının fixture kapsamı DNA işinin kendi kararıdır.)*

## 5.1 Düzenek sözleşmesi

- Modele giden prompt parçaları **üretimin kendi kod yolundan** yakalanır — test-özel
  ayrı bir prompt kurulumu YASAK (aksi hâlde kapı üretimi değil testi ölçer).
- Değişiklik **öncesi** dondurulmuş fixture ile **byte-exact** karşılaştırma
  (`cmp` düzeyi; normalize/whitespace/anlam toleransı yok). **Tek bayt fark = RED.**
- **Tekrar çalıştırılabilir regresyon** olarak kurulur — one-shot doğrulama değil.
- Canlı LLM/görsel üretim çağrısı YAPILMAZ (stokastiklik + kredi yasağı); kapı ücretsiz,
  otomatik, zorunludur.
- İlk fixture alınıp **tam sweep byte-exact geçmeden** enjeksiyon işine başlanmaz.
  ⚠️ **Sıra hükmünü bu spec bağlar** (Codex bulgusu üzerine netleştirildi): kaynak
  kurulum listesi çıpaları fixture'dan önce sayar, ama fixture tanımı "değişiklik
  öncesi dondurulmuş"tur — çelişkisiz tek sıra: önce düzenek + fixture, sonra
  enjeksiyon çıpaları (Bölüm 13.2 sırası buna göre).

## 5.2 Yüzey kümesi — ÖLÇÜMLE KAPALI (taze, 2026-08-23)

Paket yoluna girmeyen markada korunacak yüzeyler (çıpalar canlı koda karşı doğrulandı):

1. **Tier 1** sistem prompt'u.
2. **Tier 2** marka bağlamı (`prompt_builder.build_brand_context` + `SECTOR_GUIDANCE`).
3. **Tier 3** bağlam bloğu — özel günlü ve günsüz.
4. **Görsel director** çıktı biçimi talimatı.
5. **Kısa video durağan kare — iki mod ayrı ayrı** (metinden-görsele + ürün referanslı;
   `short_video.py` mod dalları).
6. **Hareket kodu havuzu ve seçim davranışı** (`_MOTION_PROMPTS`, 263-277).
7. **Fikir önerme ucu** (`ai.py:274-277` sektör rehberi bloğu).
8. **Legacy kısa video yolu** (`posts.py:805,846-847`) — listeye **koşulsuz** girer
   (kaynak gereksinimi); **K-06 yalnız fixture'ın beklenen değerini belirler**
   (düzeltilirse düzeltilmiş davranış, kapsam-dışı notlanırsa bugünkü davranış).
9. **Carousel dalı** — **K-15 (b) taze ölçümle kapandı:** carousel ayrı bir enjeksiyon
   yüzeyi DEĞİLDİR; caption üretiminin çıktı-biçim dalıdır
   (`caption_generator.py:184-315`, `is_carousel` dalları + slide prompt talimatı).
   Prompt metnini DEĞİŞTİRDİĞİ için fixture varyasyonu olarak Katman-1 kapsamındadır.

**Varyasyon matrisi:** paketsiz marka × (caption / görsel / carousel dalı / kısa video /
fikir önerme) × (özel günlü / günsüz) × (ürün referanslı / referanssız video modu).

## 5.3 Veri/API regresyon kümesi (Katman-1'le aynı zorunluluk, ayrı ölçüt)

Prompt metni olmayan üç deterministik kontrol — ölçütleri alan-bazlı eşitliktir:
- `GET /sectors` kök listesi filtre sonrası **aynen** dönüyor (3 frontend tüketicisi).
- Kök çözücünün mevcut marka eşlemeleri **değişmedi**.
- Trend katmanı alt-sektör satırlarına **bağışık**.
Ek iş-kuralı kontrolü: paketsiz üretimde geçerli paket ilişkisi **kurulmadı**
(biçim K-07'ye bağlı).

## 5.4 Paketli fixture'ın yapısal kontrolleri (deterministik — Katman-1)

Paket bloğu **var** · kök rehber **yok** · görsel dağarcığı **doğru yüzeyde** · özel
gün bloğu **yalnız eşleşince** · anma/kutlama kısıtları doğru yerde · hareket kodları
K-02 kararına göre paket havuzundan.

> **[SONRADAN EKLENDİ — 2026-08-24; spec eksik yazıldığı için]** Sahne kodlarının yüzeyi
> input'ta açıkça yazılıdır (satır 2768): *"**Video istenmişse** durağan kare istemi paketin
> **sahne kodlarını** alır — **iki modda da** (metinden görsele ve ürün referanslı düzenleme).
> ⚠️ **Hareket dili ayrı yüzeydir ve K-02'ye bağlıdır** ... **bu satır seçmez.**"*
> Yani sahne ayağı K-02'ye bağlı DEĞİLDİR (alan adı dışında); yalnız hareket ayağı bağlıdır.

---

# 6. Taksonomi korumaları

*(Girdi: snapshot §3.1/3.3, §13.1, §21.1. Kod çıpaları 2026-08-23'te taze doğrulandı.)*

## 6.1 Kök kova invariantı — üç koruma noktası

| Nokta | Bugünkü durum (taze) | İş |
|---|---|---|
| Sektör çözücü (`sector_resolver.py:59`) | Slug haritası TÜM satırları alıyor, kök filtresi yok | **Zorunlu:** sorguya kök-seviye filtresi + regresyon testi (R-01) |
| Sektör listesi ucu (`sectors.py:27-33`) | `GET /sectors` filtresiz | **Zorunlu:** kök-seviye filtresi + 3 tüketici sayfa regresyonu (R-02) |
| Trend katmanı (`layer_a.py:263`) | `WHERE parent_sector_id IS NULL` zaten var | **İş yok** — yalnız doğrulanır |

- Alt-sektör satırı eklendikten sonra **mevcut markaların kök sektör değerleri tam
  sweep'le** ekleme öncesiyle karşılaştırılır — **spot kontrol yeterli sayılmaz.**
- `brands.sub_sector_id`ye kök sektör kimliği yazılamaz — kısıt katmanı **K-08 (b)**;
  test beklenen sonucunu karar kapanınca alır (kısıtın kurulması Faz 1 zorunlusu,
  Bölüm 3.2).
- **Önbellek notu (taze ölçüm):** çözücü slug haritası ve sektör listesi 1 saat TTL'li
  Redis'te; filtre eklendikten sonra alt-sektör satırı eklemek kök listeyi değiştirmez,
  ek tazeleme gerekmez — paket aktivasyon tazelemesi ayrı konudur (Bölüm 10).

## 6.2 Migration geri alınabilirliği (sıra burada bağlanır)

Geri alma sırası: (1) `brands.sub_sector_id` bağları boşaltılır → (2) alt-sektör
satırları silinir → (3) kolon/indeks/tetikleyici kaldırılır. Alt-sektör satırı, ona
bağlı marka varken silinemez.

---

# 7. Atama akışı

*(Girdi: snapshot §9. Çekirdek kaynakta onaylı C kararı: **LLM önerir, kullanıcı
teyit eder.**)*

## 7.1 Akış sözleşmesi

```text
[Marka sahibi] → site analizi VEYA (web sitesiz) kök sektör + marka adı/açıklaması
      ↓
[Model: aday kümeden SEÇ veya BOŞ dön — serbest metin YASAK, üçüncü dönüş biçimi yok]
      ↓
[Ekran: önceden seçili açılır liste — onayla / değiştir / boşalt]
       ← yerleşim K-19 KAPANDI (Eray, 2026-08-23): onboarding + marka ayarları,
         mevcut sektör seçiminin yanında; yeni yüzey açılmaz
      ↓
[brands.sub_sector_id yazılır veya NULL kalır]
```

- Yüzeyler yalnız **marka oluşturma + marka ayarları**; içerik üretim akışına soru
  EKLENMEZ (sürtünme yasağı) — üretim yolu aday kümesini hiç okumaz.
- Son söz **kullanıcınındır**; operatörün elle ataması yetki değil, düşük hacmin
  operasyonel sonucudur (2 marka — taze ölçüm; toplu geriye dönük atama kapsam dışı).
- Öneri, mevcut site-analizi çağrısına eklenecek **yeni alanla** üretilir; web sitesiz
  geri düşüş aynı kısıtlarla (listeden, teyitli, serbest metin yok).

## 7.2 Aday kümesi — kanonik tanım (teknik, burada bağlanır)

**Aday kümesi = aktif paketi olan alt-sektör satırları:** `social.sectors`ta
`parent_sector_id IS NOT NULL` olup `social.sector_packages`ta `status='active'`
satırı bulunan sektörler. Küme **canlı sorgudan** türetilir (ayrı görünüm/kopya
tutulmaz — bayatlama sınıfı doğurmamak için). Bu tanım her iki teslim ayağının da
tek doğruluk kaynağıdır; **teslim mekanizmaları** ayrı seçilebilir ve plan işidir:
öneri çağrısına teslim **K-115**, açılır listeye teslim **K-116** (ikisi de açık).
Bölüm 6'daki kök-seviye filtresiyle **ters kümelerdir** — karıştırılmaz.

## 7.3 Boş değer ve kısıt bağımlılıkları

- Varsayılan **boştur**; boş alan = mevcut yol (byte-exact koruma, Bölüm 4.1).
- Dolu alan tek başına paket yolu vermez (aktif paket şartı — Bölüm 4.1).
- Alanın kök satır kabul etmemesi **K-08 (b)** kısıtına bağlı (Bölüm 3.2 hükmü:
  kısıt Faz 1'de kurulur).

## 7.4 Bayat atama (paketi arşivlenmiş alt sektör) — üç AYRI açık karar

Çalışma zamanı emniyetli (mevcut yola düşer — kapalı); açık olanlar: (1) kaydın
akıbeti — KORUNUR, boşaltılmaz (**K-43 — KAPANDI, Eray 2026-08-23**; paket geri
gelirse marka kendiliğinden tekrar paketli çalışır) · (2) bayat durum sistem içinde İŞARETLENİR — log/işaret
düzeyi (**K-44 — KAPANDI, Eray 2026-08-23**; zorunlu "atanmış-ama-paketsiz" log'uyla
aynı mekanizma) · (3) bildirim — **K-45 KAPANDI (Eray, 2026-08-23,
öneriden FARKLI ve geniş): ÇİFT YÖNLÜ bildirim kurulur.** (a) Bayat durum Otomaix
yöneticisine bildirilir (K-44 işaretinin üstüne aktif bildirim). (b) Marka sahibine
paket devre dışı kalınca mesaj: *"Bakım çalışmaları nedeniyle gönderileriniz genel
modda üretilmektedir. En kısa sürede sektöre özel gönderi moduna geçilecektir."*
(c) Paket yeniden aktive olunca marka sahibine mesaj: *"Bakım çalışması tamamlandı,
sektöre özel gönderi modu kullanıma açıldı."* Metinler Eray kararıyla sabit; bildirim
yüzeyinin seçimi (panel bandı vb.) teknik iş kalemi — plan işi. Bu karar Faz 1'e
bir bildirim mekanizması iş kalemi ekler. Deaktivasyon
kararıyla (K-38 — Bölüm 10) birlikte değerlendirildi. Yan sonuç: kullanıcı alanı
boşaltırsa aynı alt sektörü **yeniden seçemez** (listede yok).

## 7.5 Düzeltme ve izleme

- Yanlış atama: kullanıcı ayarlardan değiştirir/boşaltır; **sonraki üretim** yeni
  yola geçer — geriye dönük işlem yok.
- İzleme K-07 damgasına dayanır; yanlış atamayı **tespit eden** sinyal/metrik hiçbir
  katmanda tanımlı değil — düzeltme kullanıcının fark etmesine bağlı (risk kaydı
  Bölüm 16).
- Toplu atamanın yeniden ele alma tetikleyicisi (marka sayısı / elle atama yükü)
  **ölçülmemiş ve evsiz kapsam maddesidir** — dürüst kayıt: ev verilip verilmeyeceği
  kullanıcı kararı (snapshot Bölüm 17 kapsam kararı).

---

# 8. Araştırma → hakemlik → sentez hattı

*(Girdi: snapshot §7.1-7.6. Bu bölüm hattın DEĞİŞMEZ sözleşmelerini bağlar; görev
sözleşmelerinin kanonik metinleri kaynak depodadır — spec kopyalamaz, atıf yapar.)*

## 8.1 Hat ve koşu artefaktları

Akış: brief doldurulur (yalnız sektör bloğu; üç araca **aynı metin**) → üç bağımsız
araştırma koşusu (elle — bilinçli; birbirini görmez; kör adlandırma `KAYNAK-1/2/3`
**dosya adından itibaren**) → `brief-doctor` mekanik girdi kapısı → iki kör bağımsız
denetçi → sentez → (motor — Bölüm 9) → `draft` yazımı.

- Üç koşunun gerekçesi **mutabakat sinyalidir** (`3-3`/`2-3`/`tekil` sınıflaması buna
  dayanır); araç-düzeyi bağımsızlık ortak-mod hatasını dışlamaz — **ölçülmemiş sınır**,
  risk kaydı Bölüm 16.
- Koşu klasörü (brief + KAYNAK'lar + eleme raporu + 2 denetçi raporu + sentez taslağı)
  **öneridir — K-17**; motorlu modelde politika raporu + nihai aday da eklenir;
  yerleşimleri **K-95** (koşu kaydının yeri) ve **K-96** (motor-ezdiğinde özgün
  sentezin ayrı saklanma biçimi — kapanmazsa karar izi kaybı) — açık.
- Dosya çalışma kopyası, DB kalıcı kanıt katmanıdır (`run_id` altında, salt-ekleme).
- **K-18 (kapalı):** araştırma çıktıları spec + uygulama tamamlanıp sözleşmeler
  donduktan sonra, resmî hakem turundan hemen önce **tek seferde** yeniden üretilir.
  Eldeki eski çıktılar test verisi olarak saklanır, silinmez; aktif paket girdisi
  değildir.

## 8.2 Brief sözleşmesi (kanonik şablon kaynakta — bağlayıcı çekirdek)

- **GÖREV A:** sekiz temel alan (Bölüm 3.4 kümesiyle birebir; adlar yeniden
  adlandırılamaz). `video_kodlar` iki alt liste (hareket + sahne — farklı yüzeylere;
  nihai adlar K-02).
- **GÖREV B:** dönem seçimi (gerekçeli seç/ele/ekle; aday takvim başlangıçtır, kapalı
  değil) → tür etiketi (**dörtle kapalı, tek değerli, ASCII:** `kutlama` · `anma` ·
  `ticari-firsat` · `karma`; kararsızlıkta bile tek etiket + tereddüt gerekçeye) →
  dönem başına dört başlık (`mesaj_ekseni`·`kanca`·`cta` Türkçe, `gorsel_vurgu` EN).
- Mutlak kurallar (özet): yalnız kaynaklı bilgi, tahmin yok · kalıp düzeyinde yazım
  (marka cümlesi aynen alınmaz) · platform kazıma yasak · TR kaynak önceliği ·
  bağımlılık etiketleri eleme değil işaretleme · alt sınır var üst sınır yok (taşan
  değer EK BULGULAR'a) · görselde metin yasağı · güncellik/`[eski-kaynak]` · alan
  başına ≥2 bağımsız kaynak hedefi (ölçülmemiş tasarım hedefi — kapı değil),
  açılabilir tam URL · tek kaynaklı iddia işaretli.
- Çıktı **beş bölümle sabit** (A paket · B özel gün · C kaynak eşlemesi · D ek
  bulgular · E güven notu); fazladan bölüm YASAK — mekanik kapı kontrol eder.

## 8.3 Mekanik kapılar (LLM'siz, deterministik)

**(a) Girdi kapısı — `brief-doctor`:** denetimden önce koşar; çıktısı denetim görevi
ekidir. Sonuç tipleri `geçti`/`notlu geçti`/`elendi`; elenen kaynak denetim dışı,
denetçi sınıflandırma paydasını kalan kaynağa uyarlar. Adet alt sınırları (cta ≥5 ·
kanca ≥3 · görsel kod ≥20 · video kodu ≥10 · dönem ≥6; dönem başına kanca ≥2, cta ≥2,
gorsel_vurgu ≥5) **sözleşme kuralıdır, ölçülmüş eşik değil.** ⚠️ **İlke 9 uyum hükmü
(bu spec bağlar):** eleme/not eşlemesi (**K-88**) kapanana kadar bu ölçülmemiş sayılar
**tek başına eleme kapısı yapılmaz** — varsayılan davranış `notlu geçti`dir; eleme
yalnız sözleşmenin açıkça eleme saydığı kontrollere uygulanır (bugün: yok — tek açık
eşleme "40+ kelime alıntı → not"tur). Diğer açıklar: kontrol kümesinin sabitlenmesi
**K-89** · koşunun asgari kaynak tabanı **K-127 — KAPANDI (Eray, 2026-08-23): 2** —
bağımsız kaynak sayısı 1'e düşerse koşu durur ve yöneticiye bildirilir (mekanik alt
sınır: mutabakatın mümkün olduğu en küçük sayı) · `anma` "içerik önerilmez" dalı ↔
cta alt sınırı gerilimi **K-120 — KAPANDI (Eray, 2026-08-23): boş alanın özel
temsili** — sözleşmeye resmî `içerik-önerilmez` değeri eklenir; doluluk kontrolü bunu
"bilinçli boş" sayıp geçirir, diğer günlerde alt-sınır denetimi aynen sürer (brief
sözleşmesinin sonraki sürümüne girer).

**(b) Yazım kapısı — `content` doğrulayıcısı:** DB yazımından önce; şema + boyut
tavanı + özel gün anahtar doğrulaması (Bölüm 4.4); reddederse yazım olmaz.

## 8.4 Denetim sözleşmesi

- İki denetçi **aynı görev metni + aynı ekler + aynı koşu tarihi**, ayrı oturumlar,
  birbirini görmez; sözleşme araçlarıyla bağlar: **Denetçi-1 Claude Code, Denetçi-2
  Codex** (web erişimi + ön kontrol sorusu bu yüzden yalnız Denetçi-2'de — **K-14**;
  bildirim yükümlülüğü ve kanıt ağırlığı kuralı sözleşmede zaten var).
- **Denetçi karar vermez** — sınıflandırır (`3-3`/`2-3`/`tekil`/`çelişki`), bayraklar
  (sekiz bayrak, **kapalı küme**; `[kaynak-bağımlı]`, `[kanal-bağımlı: X]`,
  `[eski-kaynak]` denetçi tarafından da eklenir), önerir (`al`/`uyarla`/`alma`/
  `açık-soru`).
- URL örneklemi: kaynak başına 3 yüksek-etkili iddia; `DOĞRULANDI`/`KAYNAKTA YOK`/
  `URL AÇILMADI`; erişim yoksa "yapılamadı (ortam kısıtı)" — **doğrulamış gibi yazmak
  yasak**. ("Dokuz satır"ın sabit yazımı sözleşme-içi düzeltme kalemi — 8.7.)
- Çıktı **dört bölümle kapalı**; denetim tablosunun `no` sütunu **değişmez satır
  kimliğidir** — kanıt zinciri buna dayanır.
- `tekil` iddianın "muhtemel-uydurma" ayrımı **"güçlü kaynak" ölçütüne** bağlı —
  **K-123 KAPANDI (Eray, 2026-08-23): ölçüt TANIMLANIR**; çekirdek: kaynağın aslı
  (resmî/birincil — aktaran değil) + tarihli güncellik. Tam metin sözleşme
  revizyonunda (teknik iş kalemi).
- Orkestrasyon açıkları (snapshot Bölüm 17): bağlantı yöntemi **K-76** · yetki modeli
  **K-77 — KAPANDI (Eray, 2026-08-23): yeni model KURULMAZ, lokal tek kullanıcı**
  (mevcut CLI kimlikleri; bulut/ekip günü yeniden açılır) ·
  paralel/sıralı **K-78** · izolasyon + aynı-girdi teknik garantisi **K-79 — kapandı:
  evet, hafif garanti** ·
  tekrar-üretilebilirlik damgası **K-80 — kapandı: ZORUNLU** (model/sürüm/tarih/girdi
  özeti her artefakt satırında; Eray 2026-08-23) · biçim kontrolü otomasyonu **K-81 — kapandı:
  EVET** (mekanik yapı kontrolü, sentez öncesi; brief-doctor emsali; Eray 2026-08-23) · zaman
  aşımı/kısmi başarısızlık **K-82 — kapandı: koşu "tamamlanmadı" işaretlenir, dosya
  ezilmez; yeniden koşum yeni deneme kimliği alır** (Eray 2026-08-23; K-83'ü de
  karşılar) · yeniden koşum kimliği **K-83 — K-82 kapanışıyla bağlandı** · günlük
  sır-hijyeni **K-136 — kapandı: EVET** (günlük yazıcısına maskeleme süzgeci; olay izi
  korunur, sır hiçbir kopyaya girmez — hata mesajları dahil; Eray 2026-08-23) ·
  körlük sızıntısı **K-137 — kapandı: YAPISAL GARANTİ** (denetçiye giden pakette —
  dosya adı, talimat, rapor gövdesi — araç kimliği bulunmaz; anonimleştirme adımı kod
  düzeyinde; Eray 2026-08-23) · tek raporla sentez **K-150 —
  kapandı: ENGELLENİR** (iki geçerli rapor olmadan sentez başlamaz; eksik denetçi
  yeniden koşulur; Eray 2026-08-23).
- **Aktif paketin yeniden doğrulanması** (beş statülü ek görev: `supported` ·
  `not_observed` · `needs_update` · `contradicted` · `risk_unverified`) **bağlı karar
  kümesidir**: mutabakat kapısı **K-125** + sözleşme eki **K-100** — biri alınıp
  diğeri alınmazsa ya kapı girdisiz kalır ya denetçilere ölçülmemiş yük biner; kalıcı
  kalıp kimliğine (**K-84**; biçim **K-151**, üretim **K-152**) bağımlı. Bölüm 9'da
  motor kuralları bu kümeye bağlanır.

## 8.5 Sentez sözleşmesi

- **Girdiler:** brief · iki denetçi raporu · varsa aktif paket · son turların çıkarma
  kararları · sistem özel gün adları+kategorileri · gerektiğinde ham kaynak KESİTİ
  (bütünü asla) · **kök sektör rehberi** (onaylı 7. girdi — sözleşme listesinde henüz
  yok: **eklenene kadar resmî hakem turu bloklu**, 8.7).
- **Birleştirme birimi alandır** — sekiz alan + her özel gün dönemi tek tek; serbest
  metin birleştirme yok; her karar denetçi satırına/uyuşmazlık listesine izlenebilir.
- **Koşu modları:** tam (`A+B`) · `yalnız B` (temel alanlar alan-başına `koru` +
  "B-only" gerekçesiyle taşınır — sessiz taşıma yok) · ilk paket (her şey `ekle`
  evreninde, çıkarılanlar listesi boş).
- Karar akışı: uyumlu sınıf+öneri → kabul havuzu; uyumsuz → uyuşmazlık listesi; tek
  denetçinin gördüğü iddia otomatik açık soru DEĞİL (ham kaynağa bakılır). Havuz ×
  aktif paket → beş karar (uygulanma koşulları kaynakta; `cikar` pozitif kanıt şartı
  Bölüm 3.5).
- **Bayrak tüketimi** sözleşmede tanımlı (yedi bayrak; `[kopya-şüphesi]` tüketim
  satırı sözleşme düzeltmesi — 8.7). `[yerel-değil]` tekil istisnayı kapatır;
  `[eski-kaynak]` ekle eşiğinde dezavantajlı; `[kanal-bağımlı]` etiketiyle taşınır.
- **Geri-ekleme kontrolü:** çıkarılanlar listesiyle eşleşen aday "geri-ekleme
  önerisi"dir; eski gerekçe + yeni kanıt yan yana, çelişki açık soruya. Tespit kalıp
  METNİNE dayanır — metni değişmiş kalıp kaçabilir (kabul edilmiş zayıflık; kapatıcısı
  K-84).
- **Çıktılar (4):** aday JSON (şemaya birebir) · karar günlüğü · açık soru listesi
  (sözleşme değeri ≤10 — **ölçülmemiş tasarım değeri**; taşma davranışı **K-74**
  kapanmadan sınır zorlayıcı kesme kapısı yapılmaz, taşan maddeler düşürülmez) ·
  onay özeti. Açıklar: **K-74** (sentez taşması) ve **K-75** (denetçi ≤5 — aynı
  etiketle: kapanmadan kesme kapısı değil; ayrı sözleşme, ayrı karar) · reddedilen aday temsili **K-87** · eşleşmeyen dönem notu
  **K-108** · özet ↔ onay yüzeyi ilişkisi (tam liste mi eşik-üstü özet mi — K-42
  ile birlikte, Bölüm 9).
- **Rol hükmü revizyonu (koşulsuz gündem):** motor Faz 1'de olduğundan sentez artık
  karar mercii değil **aday değişiklik seti üreticisidir**; sentez sözleşmesinin rol
  hükmü revize edilir (8.7).

## 8.6 Boyutlandırma

Alan hedefleri ve ~6.000 karakter tavanı Bölüm 3.4'te (hedef, kapı değil). Limit
**iki bağımsız tetikleyicilidir**: yerel hedefi aşan alan kendi içinde kırpılır +
global tavan bütüne uygulanır. Hedeflerin toplamı tavanın üstünde (≥6 dönemde ~6.700
karakter) — tutarsızlık DEĞİL; iki tetikleyicinin birlikte çalıştığı koşullar gerçekçi,
bu yüzden **kırpma önceliği kararı etkili**: **K-121 — KAPANDI (Eray, 2026-08-23):
mevzuat-öncelikli ALTILI sıra benimsenir** — mevzuat/güvenlik en üstte korunur, asla
ilk kırpılan olmaz; yürürlükteki üçlü sıra terk edilir; churn koruması ("yeni-zayıf öğe salt
yeniliğiyle doğrulanmış kalıbı çıkaramaz") **K-122 — KAPANDI (Eray, 2026-08-23):
BENİMSENİR** (sentez sözleşmesine kural; çıkarma yalnız pozitif kanıtla — K-124
eşiğiyle birlikte işler). Sessiz-kayıp
güvencesinin statüsü HEDEF (**K-40 — kapandı**, garanti değil). Gerçek dağılım pilottan
ölçülür → **K-12** girdisi.

## 8.7 Resmî tur öncesi zorunlu sözleşme düzeltmeleri (drift kapanışları — yeni karar değil)

1. Sentez sözleşmesine **K-03 yansıması** (tür etiketi üstün; "açık soruya düşür"
   metni kalkar) — yansıyana kadar kuru koşum eski davranışı üretebilir.
2. Sentez girdi listesine **kök sektör rehberi** eklenir — eklenene kadar resmî tur
   BLOKLU.
3. `[kopya-şüphesi]` bayrak tüketim satırı eklenir (hüküm mevcut üst kuraldan belli).
4. Sentez sözleşmesinin **rol hükmü** motorlu modele revize edilir (K-22=A sonucu).
5. URL örneklem bölümündeki sabit "dokuz satır" yazımı koşullu ölçüme düzeltilir.

---

# 9. Politika motoru (K-22=A — Faz 1)

*(Girdi: snapshot §7.7-7.8, §4.5. Motor **kural motorudur, kalite yargısı değildir**;
Katman-2 kör değerlendirmeyi İKAME ETMEZ. Sentez ile aktivasyon arasına yerleşir.
Motor kavramı 2026-07-11 kaynaklarında yoktur — `[SEA-2026-08-11]` bileşeni; kuruluşu
sıfırdandır.)*

## 9.1 Girdiler

Sentez aday paketi + karar günlüğü · aktif paket + şema sürümü · son turların çıkarma
kararları · iki denetçi tablosu + URL örneklem sonuçları · mekanik eleme sonucu ·
sistem özel gün listesi · **politika yapılandırması** (bir kez konur, her turda
uygulanır) · otomatik kapı sonuçları. Denetçi tablolarının doğrudan girdiliği
mutabakat kapısına (**K-125**) bağlı; **prompt regresyonu açık karar DEĞİL, zorunlu
kapıdır** — geçmeden koşu `activation_eligible` olamaz.

## 9.2 Zorunlu kontroller (küme kapalı değil — kesin küme planda sabitlenir)

Şema+boyut · karar kapsamı (aktif paketteki her birim için tam bir sonuç) · yeni
kimlik benzersizliği · **kanıt** (`guncelle`/`cikar` kanıtsızsa uygulanmaz, kalıp
korunur) · mutabakat (**K-125**'e bağlı) · yeni öğe kuralı `2-3` — ⚠️ **statü
netleştirmesi (İlke 9 gerekçesiyle):** bu ampirik/ölçülmemiş bir eşik DEĞİL, kaynakta
onaylı karar matrisinin **yapısal çoğunluk kuralıdır** (üç bağımsız araştırmanın en az
ikisinde bulunma — her koşuda deterministik sayılır; "kaç kaynak" bir ölçüm iddiası
değil oylama tasarımıdır). Kaynak sözleşmesinde motordan bağımsız yürürlüktedir; motor
onu uygular, koymaz. Kuralın kendisinin değişmesi sentez sözleşmesi revizyonu ister —
bu spec'in yetkisinde değildir (tekil istisna yalnız güçlü-kaynaklı + bayraksız) · bayrak tüketimi · geri-ekleme çelişkisi · kategori
çakışması (**K-03 uygulanır:** paket türü üstün; "kararsız" dalı bu çatışma için
düşmüştür) · özel gün anahtarı · diff sayıları · değişim bariyeri (K-130'a bağlı) ·
regresyon kapısı · tek-aktif ön kontrolü.

## 9.3 Güvenli fallback

Yön bağlayıcı: motor belirsizliği **yeni içeriğin lehine yorumlamaz** — karar
veremediği yerde değişiklik yapmaz, mevcut kalıbı korur, durumu rapora yazar.
Deterministik varsayılan tablosunun benimsenmesi **K-23** (benimsenmezse kararsızlar
yöneticiye açık soru olarak düşebilir — ikinci insan müdahale noktası). Mevzuat/
güvenlik bloklaması **K-128** kapısının konusudur (alan listesi **K-129 — kapandı:
sabit liste**, 9.4); kapsam/
kimlik bütünlüğü bloklaması ise yapısal kontroldür (K-84'e bağlı), politika tercihi
değil. **Fallback sentez raporunu yerinde değiştirmez** — motor nihai adayı AYRI
üretir, reddettiklerini politika raporuna yazar; üçlünün saklanma biçimi **K-96**.

## 9.4 Bariyerler ve kuru mod (hepsi ayrı karar; hiçbiri eşik değeri taşımaz)

- Değişim büyüklüğü bariyeri **K-130** · ekleme/şişme bariyeri **K-131** · kararsızlık
  oranı bariyeri **K-132** — farklı şeyleri ölçerler, ayrı ayrı benimsenebilir.
- İlk paket koşusunda oran paydası sıfır → **mutlak limitlerle** kontrol.
- **Eşik ilkesi:** hiçbir sayısal eşik kanıtsız seçilmez — pilot dağılımıyla kalibre
  edilir, değerleri **K-24**'ün kapsamıdır (İlke 9'un motor karşılığı).
- **Kuru mod K-133** — yeni koşu kipi (sonuç, kayıt, gösterim sözleşmesi kendi başına);
  motorun fazından ayrı karar.
- Mutabakat kapısı benimsenirse iki kalem ayrıca kesinleşir: bloklayan alan listesi
  **K-129 — KAPANDI (Eray, 2026-08-23): SABİT** — yasaklar-ve-hassasiyetler alanının
  tamamı + mevzuat/tarih/sayı iddiası içeren tüm maddeler (mekanik, yorumsuz; spec
  revizyonuyla genişletilebilir) · tek-kaynak istisna sözleşmesi **K-126 — KAPANDI (Eray, 2026-08-23):
  TANIMLANIR** — istisna yalnız (1) kaynak resmî (K-123 ölçütü) + (2) en az bir
  denetçinin canlı URL doğrulaması (açıp içerik uyumunu kaydetmesi) birlikteyken çalışır.

## 9.5 Sonuç tipleri ve izlenebilirlik

- **Üç seviye karıştırılmaz:** koşu (`activation_eligible`·`no_change`·`blocked`) ·
  kalıp-kararı (`uygulandı`·`uygulanmadı (kanıt yetersiz)`·`motor kararsız`) · paket
  statüsü (`draft`/`active`/`archived`). `tur durduruldu`↔`blocked` birleştirmesi
  **K-90**.
- `no_change`/`blocked` koşularının kayıt yeri **K-93** · canonical içerik hash kuralı
  **K-92** · ilk koşuda `no_change` geçersizliği **K-91**.
- **K-28 (kapalı ilke):** motor `active`'e dokunamaz; `blocked` hiçbir uçtan aktive
  edilemez — sunucu tarafı zorlama tekniği **K-103** açık.
- Aktör alanı (karar satırında motor/insan ayrımı) **K-25** · motor sürüm+yapılandırma
  koşu damgası **K-97** — birlikte alınabilir; hiçbiri alınmazsa kötü sürümün kaynak
  teşhisi zorlaşır.

## 9.6 Onay yüzeyi (motorlu model — yürürlükte)

Yönetici kalıp listesi görmez; gördüğü: koşu sonucu (yalnız `activation_eligible`
onaylanabilir — otomatik aktivasyon değil) · alan-bazlı+toplam sayılar · değişim
oranları · çıkarılanlar (sayı + eşik-üstü; **eşik K-41 açık — ürün/risk kararı**) ·
son 4 turun çıkarılanlar özeti · kararsızlar + geri-ekleme çelişkileri · açık sorular
(≤10) · kapı sonuçları (Katman-1 deterministik + Katman-2 sinyal) · uyarılar · içerik
hash'leri (K-92) · motor koşu raporu.

Açıklar: sinyal-odaklı diff tasarımı **K-42** (ürün/risk) · gösterilen anlık görüntünün
değiştirilemezliği **K-98** · onay anında base-sürüm geçersizlik kuralı **K-94** (hash
gösterimi bunu İKAME ETMEZ) · açık-soruların kapanması aktivasyon ön koşuludur
(**K-71 — KAPANDI, Eray 2026-08-23: bloklar**; öneriden farklı seçim) · onay/ret olayının kimlik+zaman kaydı **K-99** · red sonrası taslağın
akıbeti **K-106** ve düzeltme turu **K-72 — KAPANDI (Eray, 2026-08-23): otomatik
BAŞLAMAZ, yeni koşuyu yönetici elle tetikler** (ret sebebine göre kısmi/tam/hiç) ·
rol bölünmesi **K-54 — kapandı:
bölünmez** (tek yönetici rolü). Sentez özetinin
tam-liste modeli ile bu yüzeyin özet modeli arasındaki sözleşme farkı 8.7/1
düzeltmesiyle birlikte ele alınır.

---

# 10. Yaşam döngüsü ve aktivasyon

*(Girdi: snapshot §8, §10.5. Durum kümesi ve tek-aktif garantisi Bölüm 3.6'da;
burada geçişler ve işletim davranışı.)*

## 10.1 Geçiş tablosu (bağlayıcı çekirdek)

- Koşu → `draft` (yalnız; doğrulayıcı geçtiyse; `version` = son + 1; run_id bağının
  zorunluluğu açık — Bölüm 3.1).
- Aktivasyon **iki adım, sıra zorunlu:** önceki `active` → `archived`, sonra `draft` →
  `active` (+`activated_at`). İlk pakette yalnız ikinci adım. Ters sıra indeks
  ihlaliyle REDDEDİLİR — sıra zorlayıcısı DB'dir.
- Rollback: kötü sürüm → `archived`, önceki iyi sürüm → `active` (aynı sıra
  disiplini). Geri alınan birim **paket sürümüdür, deploy değil** — kod dağıtımı
  gerekmez. Tetikleyici kümesi kapalı ilan edilmez; "paketsiz markada prompt farkı =
  pazarlıksız derhal geri al" tek hakem ölçütü olarak kayıtlı.
- Ham artefakt satırında geçiş yok — `UPDATE`/`DELETE` DB reddeder.

## 10.2 Aktivasyon ön koşulları

**(a) Ortak çekirdek (motorsuz zincirin de tamamı):** biçim doğrulayıcısı geçti ·
**Katman-1 prompt kapısı geçti** (onayın önünde) · yöneticinin tek-soru onayı.
**(b) Motorlu ek koşullar (yürürlükte):** koşu `activation_eligible` · karar kapsamı
tam · şema/kanıt/mutabakat/bariyer/regresyon kontrolleri (her biri kendi açık
kararıyla) · mevzuat/güvenlik bloklaması — **yalnız K-128=A seçilirse** (kapının
benimsenmesi K-128 AÇIK; benimsenirse alan listesi K-129 bağlanır — kapı bu spec'te
yürürlüğe konmaz) · kararsız maddeler ele alınmış — **nasıl** ele alınacağı K-23'e
bağlı (açık: güvenli varsayılan mı, yöneticiye açık soru mu).
**Katman-2 kapı olarak GİRMEZ** — koşulması ve sunulması ön koşul, sonucu kapı değil
(K-11 (b)).
**(c) K-71 — KAPANDI (Eray, 2026-08-23): açık soruların kapanması aktivasyon ÖN
KOŞULUDUR** — açık soru listesi boşalmadan aktivasyon yapılamaz (öneriden farklı seçim;
K-30 ile çelişmez: K-30 kullanım-sinyali beklememeyi düzenler, bu karar araştırma
sorularının kapanmasını).

## 10.3 Açık işlem kararları (ayrı ayrı seçilebilir)

Aktivasyon atomikliği **K-101** · rollback atomikliği **K-102** (tek hakem — ayrı
seçilebilir) · yetkilendirme modelinin sunucu zorlaması **K-103** · ara pencerede
başlayan üretimin sürüm bağı **K-104** · ara-pencere okuyucu testi **K-105 — kapandı:
ZORUNLU DEĞİL, isteğe bağlı plan kalemi** (pencere emniyetli: paketsiz yola düşer +
loglanır + K-56 anında uyarı; düşüş yolu ana testlerde kapsanıyor; Eray 2026-08-23) ·
base-sürüm geçersizlik kuralı **K-94** · red/düzeltme akışı **K-72 kapandı: düzeltme turu elle tetiklenir** / **K-106** (yerinde
güncellemede kontrollerin yeniden koşulup koşulmayacağı hiçbir katmanda tanımsız —
K-106'yla birlikte bağlanır) · **deaktivasyon K-38 — KAPANDI (Eray, 2026-08-23): yeni
sürümsüz geri çekme DESTEKLENİR** (marka paketsiz yola döner; rollback'ten AYRI; olay
loglanır) · geçmiş postların değişmezliği **K-39 — KAPANDI (Eray, 2026-08-23):
değişmez** (K-07'den ayrı). R-17 notu: atomiklik altyapıda bilinen engelsiz — **ampirik
doğrulanmadı**, plan T-görevinde throwaway testle ölçülür.

Atomiklik sağlanmazsa doğan paketsiz pencere **emniyetlidir** (veri kaybı yok) ama
loglanır (aktivasyon/rollback olay logu ortak zorunluluk — kim·ne zaman·hangi
sürümden hangisine).

## 10.4 Önbellek sözleşmesi (K-109 uzayı — taze ölçümle daraltıldı)

- Ortak çekirdek: paket gövdesi marka başına sabit metin, yalnız aktivasyonda değişir.
- **Taze ölçüm (2026-08-23):** uygulama katmanında sektör verisi Redis'te 1 saat
  TTL ile önbellekleniyor (`sectors` listesi + çözücü slug haritası); **aktivasyonun
  tetiklediği hiçbir geçersiz kılma yolu YOK** (invalidate çağıran sektör kodu 0
  isabet); marka önbelleğinin tetikleyicisi marka/kit güncellemesidir ve paket
  aktivasyonu marka satırına dokunmaz. → Snapshot'ın "ölçülmemiş" dediği olgu artık
  ölçüldü: **Konum B'nin birinci-katman dayanağı paket hâlini kapsamıyor.**
- **Spec hükmü (teknik):** paket okuma sorgusu uygulama katmanında önbelleklenecekse
  anahtar paket kimliği+sürümünü içerir VEYA aktivasyon ilgili anahtarı açıkça
  geçersiz kılar (`invalidate` altyapısı mevcut — `core/cache.py`). "Ek mekanizma
  gerekmez" varsayımı ancak paket okuması hiç önbelleklenmezse doğrudur; bu tasarım
  seçimi planda bağlanır. Model-tarafı istem önbelleği (ikinci katman) içerik
  değişince kendiliğinden ıskalar — ek iş yok.
- Paketsiz yolun önbellek anahtarı ve metni değişmez (Katman-1 ile aynı yön).
- Gecikme/yük hedefi hiçbir katmanda yok — **ölçülecek, eşik pilot sonrası**; paketli
  yolda +1 DB sorgusu / 0 ek model çağrısı iddiası doğrulanmadı etiketiyle taşınır.
  Maliyet ölçümü **K-12** (paket + Marka DNA toplam bütçesi, güncel model üzerinden).

## 10.5 Bilgi kaybı güvencesi (üç katman)

1. Yanlış çıkarma zorlaştırılır (pozitif kanıt şartı — Bölüm 3.5, 9.2).
2. Tetikleyiciler insan hafızasına dayanmaz (çıkarılanlar listesi her senteze girdi;
   geri-ekleme otomatik değil, açık soruya; onay yüzeyinde son 4 tur özeti).
3. **Sıfır-kayıp garantisi verilmez** — güvence "gözlemlenebilir değeri olan kalıp
   sessizce kaybolmaz"; statüsü **HEDEF'tir, bağlayıcı garanti değil** (**K-40 —
   KAPANDI, Eray 2026-08-23**; tur başına kanıt/kabul-kriteri yükü doğmaz). Tespit
   gücü kalıp kimliği kararına (**K-84**) doğrudan bağlı.

Geri getirme silmeyle değil **yeni sürümle**. Aktive edilmemiş taslakların saklama
kuralı **K-142 — kapandı: taslaklar da kalıcı, tek rejim** (K-143 doğmaz; arşiv
güvencesi hükmü değişmedi).

---

# 11. Koşullu akışlar

*(Girdi: snapshot §11. Kaynak katmanı belirleyicidir — dört tür etiketi, eşleşmezlik
kuralı ve acil güncelleme hükmü kaynakta yazılı.)*

## 11.1 Özel gün akışı (Tier 3)

- Tetikleyici: kullanıcı üretim ekranında özel gün seçer. Eşleşen günde dönem
  kalıpları bloğa eklenir (**blok yapısı değişmez**); eşleşmezse **sessiz düşme +
  zorunlu log**.
- Anahtar sözleşmesi Bölüm 4.4'te bağlandı (K-01b'nin normalize/tek-modül çözümü).
  Dört veri sorunu geçerli (taze doğrulandı): gün-bazlı ayrı satırlar · resmî uzun
  adlar · sistem-ad ↔ brief-ad ayrışması · bazı aday dönemler takvimde hiç yok
  (10 Kasım · Öğretmenler Günü · okula dönüş — 2026 setinde yok, taze ölçüm).
- **Özelliğin ön koşulu yalnız K-01b'nin çözümüdür** (K-03 ayağı kapandı); bu spec
  4.4'teki sözleşmeyle çözümü veriyor — kalan iş plan/execute.

## 11.2 Tür etiketi ↔ kategori çakışması (K-03 — kapalı)

Gün eşleşti + pakette tür etiketi var → **paket türü üretim davranışında üstündür**;
takvim kategorisi korunur (günün kimliği/doğrulaması için) ve kategori bloğu basılmaya
devam eder; çatışma karar günlüğüne yazılır. Kapsam DAR: yalnız tür↔kategori — mevzuat
çatışması, kapsam tercihi ve motor kararsızlıkları etkilenmez (K-23 kapanmaz).
Sözleşme yansıması 8.7/1. **Etiketsiz gün davranışı K-15 (a) kapsamında — açık;
normatifleştirilmez.**

**Miras veri tutarsızlığı (K-47 — açık kapsam kararı):** Yılbaşı takvimde `national`,
prompt örneklerinde ticari anlatılıyor; düzeltilip düzeltilmeyeceği **K-47**'de açık —
ev vermek kullanıcı kararı.

## 11.3 `anma`/`kutlama` kısıtı

İkisinde de CTA yerine **kutlama-saygı kalıbı** + "satış çağrısı kullanma" satırı;
`anma`da ek içerik kısıtı (yalnız saygı çerçevesi VEYA "içerik önerilmez").
Kullanıcı-isteği karşısındaki geçersiz-kılma yetkisi **K-119 — KAPANDI (Eray,
2026-08-23): yasak kullanıcı isteğini geçersiz kılar** (Bölüm 4.6; K-118'in tek istisnası).
**Test edilebilirlik (taze ölçüm):** `anma` bugünkü takvim verisiyle gerçek günle
tetiklenemez; akış **fixture üzerinden test edilir** — K-01a (takvime gün ekleme,
operatör kararı) yalnız gerçek-gün gösterimini belirler, testin varlığını değil.
K-01a alınırsa yıllık n8n takvim işine de işlenmesi gerekir (iş bugün yalnız üç
kategori yazıyor — taze ölçüm).

## 11.4 Görsel/video dağarcığı akışı

Dağarcık caption director talimatına + kısa video durağan karesine (iki modda)
eklenir; görsel vurgu yalnız gün eşleşince. **Dağarcık ek bağlamdır, geçersiz-kılıcı
değil** (tek istisna: 11.3 `anma` satış-dili yasağı — K-119 kapandı, geçersiz-kılıcı). Blok-varlığı Katman-1 (deterministik);
alt-küme kullanımı + kanal uygunluğu Katman-2 sinyali (eşik K-11 (b)).

## 11.5 Video hareket dili (K-02 — açık, üç seçenek)

Bugün (taze doğrulandı): hareket director'dan geçmez, `_MOTION_PROMPTS` sabit
havuzundan rastgele seçilir; `Industry` satırı yalnız durağan kareyi etkiler.
Seçenekler: (a) paketli markada paket havuzu / paketsizde mevcut liste aynen
(kaynak önerisi) · (b) hareketi modele ürettir (ek çağrı — maliyet+gecikme) ·
(c) sonraki faza bırak, video kodları yalnız durağan kareye. Havuzlar birlikte
KULLANILMAZ. Paketsiz üretimde mevcut havuz byte-exact korunur (Katman-1 çekirdeği).
(a) seçilirse boş-havuz fallback'i (mevcut listeye düşüş — tek hakem) ayrıca bağlanır.

> **[SONRADAN EKLENDİ — 2026-08-24; spec eksik yazıldığı için]** Yukarıdaki üç seçenek
> spec-input'tan taşınırken kararın **öneri · sahip · çözüm yolu** ayakları DÜŞTÜ ve
> ayrı bir karar kalemi (**K-113**) hiç taşınmadı. Bu blok o eksiği kapatır; yukarıdaki
> metin değiştirilmemiştir.
>
> **K-02'nin input'taki tam kaydı** (`docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md`
> satır 2533, karar kartı):
>
> - **Öneri: A** — *"her iki kaynak katmanı da aynı yönü gösterir. Gerekçe: paketsiz
>   üretimde modele giden prompt parçaları değişmez ve ek model çağrısı doğmaz."*
> - **Sahip:** *"Teknik sahip (mekanizma) · Ürün sahibi (maliyet/kapsam ayağı — **yalnız
>   (A) elenirse**)."* Yani K-02 ürün sahibine varsayılan olarak GİTMEZ.
> - **Çözüm yolu:** *"**Spec içinde teknik olarak çözülür** — önce mevcut hareket
>   listesinin enjeksiyon noktası taze doğrulanır. Paketsiz prompt değişmeden havuz
>   beslenebiliyorsa **(A) seçenek tartışması düşer**; beslenemiyorsa ek model maliyeti ↔
>   kapsam daraltması tercihi kullanıcıya çıkar."*
>
> Input aynı kararı "**Spec'te özellikle çözülmesi gereken teknik konular**" listesinin
> 2. maddesi olarak da sayar (satır 3103): *"Hareket havuzunun paketten seçilmesi ve paket
> yoluna girmeyen üretimde mevcut hareket listesinin **byte-exact** kalması; şablonun
> **6a/6b** ayrımının nihai alan adlarına bağlanması."* Yani K-02, spec yazımından sonraya
> bırakılacak bir kalem olarak DEĞİL, spec içinde kapanacak bir kalem olarak devredilmiştir.
>
> **Mekanizma input'ta zaten tarif edilmiş** (satır 485, enjeksiyon bileşen tablosu):
> *"Motion havuzu seçici — paket yolunda **sektör havuzundan**, mevcut yolda **bugünkü
> sabit listeden**."* Yani değişen **kaynaktır**, seçicinin kendisi değil; bu, A'nın
> "ek model çağrısı doğmaz" gerekçesinin karşılığıdır.
>
> **K-113 — ayrı karar kalemi** (input satır 2576; bu spec'e HİÇ taşınmamıştı):
> *"Hareket havuzu boşsa ne olacak? A) Mevcut listeye geri düşülür / B) Farklı bir davranış
> tanımlanır. **[AÇIK]** — tek katmanda ele alınmıştır. **K-02'den ayrı seçilebilir:** havuz
> yolu benimsense bile boş havuz dalı ayrıca karara bağlanmalıdır. Sahip: teknik sahip.
> **Spec içinde teknik olarak çözülür** — geri düşüş yolu tanımıdır."*
> Yukarıdaki paragrafın "(a) seçilirse boş-havuz fallback'i ... ayrıca bağlanır" cümlesi
> bu kalemi ima ediyordu ama **K-ID'siz** taşımıştı; kimliği burada geri konur.

## 11.6 Tur dışı acil güncelleme

Ayrı mekanizma YOK: aynı `draft → active` zinciri her an koşulabilir; acillik **onay
kapısını ve sıra kuralını kaldırmaz**; motorlu ön koşul zinciri geçerli. **K-73 —
KAPANDI (Eray, 2026-08-23): tam araştırma turu ZORUNLU DEĞİL** — elle düzeltilmiş
dar taslak dalı açık; şartları: (1) değişikliğin doğrulanmış resmî kaynak kanıtı,
(2) iki denetçinin yalnız o değişiklik üzerinde hızlı doğrulaması. Onay kapısı ve
sürümleme aynen işler (K-22'den ayrı karar). Kabul senaryosu beklentisi: mevzuat değişikliğinde
iki-tarihli yazım (sürüm mekaniğinin ilk gerçek kullanımı — ölçülmemiş beklenti).

---

# 12. Kanal envanteri (K-05=B) ve Marka DNA sınırı

*(Girdi: snapshot §12, §5.3. K-05=B kapanışı envanter tasarımını bu spec'in gündemine
koydu — tasarım burada bağlanır.)*

## 12.1 Sistem sınırı (bağlayıcı ilkeler)

- İki sistem iki soru: paket = "bu sektörde nasıl konuşulur/görünür"; DNA = "bu marka
  ortalamadan nasıl ayrılır". Sapma DNA'da, ortalama pakette; **aynı bilgi iki
  katmandan basılmaz**; paketteki genel bilgi DNA'ya kopyalanmaz; DNA çıkarımında
  aktif paket **yalnız kontrast referansı**.
- DNA alanlarının dolu olması bu sistemin ön koşulu DEĞİLDİR (boş alan enjekte
  edilmez).
- İki sistem **aynı Tier 2 bloğunu ve aynı token bütçesini** paylaşır
  (`build_brand_context`); toplam bütçe ölçümü **K-12**.
- DNA verisinin motora girdi olup olmayacağı **K-52 — açık kullanıcı kararı** (veri
  sahipliği sınırı; K-22'ye indirgenemez).

## 12.2 Envanter tasarımı (burada bağlanır — teknik sözleşme)

- **Veri yeri:** `brands.brand_kit` JSONB içinde `channels` alanı (mevcut brand_kit
  deep-merge güncelleme yolu kullanılır — yeni kolon/tablo açılmaz). Marka DNA
  G1'deki `channels` alan adayının EVİ artık burasıdır; DNA işi bu alanı **yeniden
  kurmaz, tüketir** (sınır çizgisi).
- **Anahtar uzayı KAPALIDIR** ve `[kanal-bağımlı: X]` etiketinin X uzayıyla birebir
  aynıdır: `whatsapp_hatti` · `fiziksel_magaza` · `randevu_sistemi` ·
  `eticaret_sitesi` (brief sözleşmesindeki dört sınıf). Uzayın kapalılığı brief/denetçi
  sözleşmesine işlenir — **8.7 düzeltme listesine 6. kalem** (serbest X değeri
  deterministik filtreyi imkânsız kılar).
- **Çalışma zamanı filtresi (deterministik):** `[kanal-bağımlı: X]` etiketli kalıp,
  markanın envanterinde X doğrulanmadıkça **enjekte edilmez**. Envanter alanı hiç
  yoksa (doldurulmamış marka) filtre **muhafazakâr davranır: etiketli kalıp atlanır**
  — kullanım talimatının son satırı (K-04) ikinci savunma hattı olarak korunur.
- Doldurma akışı (UI/onboarding yerleşimi) plan işidir; üretim akışına soru eklenmez
  (sürtünme yasağı burada da geçerli — doldurma yalnız ayarlar/kurulum yüzeyinde).

## 12.3 Veri sahipliği (bağlayıcı işaretler)

- Özel gün adları: **sistem takvimi kazanır**; pakete kopya liste yazılmaz, yalnız
  anahtar referansı.
- Sektör bilgisi: paket varsa **tek kaynak pakettir** (yan-yana yasak).
- Marka sesi: **DNA kazanır**; yasak kelimeler mutlak kısıt.
- Gerçek marka/firma adı geçen metin pakete giremez — kural yürürlükte; **otomatik
  denetimi teknik iş kalemidir** (K-15 üçüncü bileşen — yazım kapısına eklenir,
  Bölüm 14).
- Uzun/zengin marka bilgisi doküman+RAG katmanının işidir; ne pakete ne DNA'ya.
- Takvim erişilemezse özel gün bloğunun davranışı **açık karar** (tek hakem hükmü
  normatifleştirilmez); paket erişilemezse mevcut yol (Bölüm 4.2).
- Geçmiş postlar geriye dönük DEĞİŞMEZ (**K-39 — KAPANDI, Eray 2026-08-23**; K-07'den
  ayrı) — post kaydı üretim anının kanıtıdır, damganın kanıt değeri korunur; Bölüm
  10.3'te kayıtlı.
- Paket içeriğinin API üzerinden okunabilirliği **K-16 — KAPANDI (Eray, 2026-08-23):
  iç kullanım + yönetici; müşteriye KAPALI** (müşteri paketi üretim çıktıları üzerinden
  yaşar; müşteri sayısı artınca pazarlama yüzü olarak yeniden değerlendirilebilir).

---

# 13. İşletim: komut ailesi, yordamlar, roller

*(Girdi: snapshot §14, §15. K-27=A: yönetici koşu yüzeyi = Claude Code komut ailesi;
panel geliştirilmez. **Taze ölçüm 2026-08-23: aile bugün YOK** — kurulum bu işin
kapsamı ve maliyetidir.)*

## 13.1 Komut ailesinin sorumluluk alanı (kurulacak)

Koşu tetikleme (sektör seç + `run_id` aç) · ek toplama (brief + KAYNAK-1/2/3 +
eleme raporu — kör adlandırma dosya adında korunarak) · `brief-doctor` koşumu ·
iki denetçi oturumunun orkestrasyonu (Denetçi-1 Claude Code · Denetçi-2 Codex;
bağlantı yöntemi **K-76**, yetki **K-77 — kapandı: model kurulmaz, lokal tek
kullanıcı**, paralel/sıralı **K-78**, izolasyon
garantisi **K-79 — kapandı: evet**) · sentez koşumu · motor koşumu · onay yüzeyinin sunumu ·
aktivasyon/rollback işlemi. Codex'in aktif katman/vault yazma yasağı burada da
geçerlidir (mevcut çalışma sözleşmesi).

## 13.2 Kurulum yordamı (bir kez — sıra bağlayıcı)

1. Şema değişiklikleri (migration 032 — Bölüm 3.8; K-08 (b) kısıtı dahil).
2. Veri/migration deterministik kontrolleri (Bölüm 14).
3. **Kök kova korumaları ÖNCE** — çözücü + liste ucu filtreleri ve regresyon
   testleri; koruma kurulmadan alt-sektör satırı AÇILMAZ (çözücü bugün tüm satırları
   alıyor — taze doğrulandı; korumasız satır invariantı bozar).
4. Alt-sektör satırlarının açılması (pilot kapsamı).
5. Marka kök-sektör tam sweep'i (spot yetmez).
6. **Katman-1 düzeneği + dondurulmuş fixture** (K-20=A: DNA ile ortak kurulur) —
   fixture, enjeksiyon değişikliklerinden ÖNCE alınır ve tam sweep byte-exact
   geçmeden hatta devam YOK (sıra hükmü Bölüm 5.1'de bu spec'çe bağlandı).
7. Enjeksiyon çıpalarının bağlanması + kullanım talimatı + sürüm damgası (K-07) —
   her artımda Katman-1 yeniden koşulur.
8. Veri/API regresyon kümesi (Bölüm 5.3 — teknik iş kalemi).

## 13.3 Koşu yordamları

- **İlk paket koşusu:** brief iki görevle (A+B — yalnız-B ilk pakette geçersiz) →
  üç araç elle → klasör (K-17) → mekanik kapı → iki kör denetçi → sentez (hepsi
  `ekle` evreni) → motor → yazım kapısı → `draft` → Katman-1 + Katman-2 → onay →
  aktivasyon (ilk pakette yalnız ikinci adım) → markalara öneri/teyit → ilk üretim
  gözlemi.
- **Periyodik tur:** periyot değeri **K-149 — KAPANDI (Eray, 2026-08-23): 6 ayla
  başlanır** (ilk tur süresi ölçülünce revize edilebilir; acil mevzuat tur-dışı kolla
  karşılanır); saklama **K-26 — KAPANDI (Eray,
  2026-08-23): alan SEKTÖR BAŞINA kurulur** (Faz 1'de tek değer: 6 ay) **+ VADE
  BİLDİRİMİ:** periyodu dolan paket için yöneticiye bildirim (K-45 yönetici-bildirim
  mekanizmasıyla aynı altyapı; Faz 1 iş kalemi — elle vade takibi kalmaz); aynı zincir + aktif paket ve geçmiş çıkarmalar senteze girdi; her turda Katman-1
  yeniden koşulur; tur süresi İLK TURDA ÖLÇÜLÜR (K-13 revizyon girdisi — kapı değil).
- **Kısmi güncelleme:** (a) yalnız-özel-gün turu (sözleşmede yazılı; taşınan alanlara
  `koru` satırı zorunlu) · (b) tek dönem/alan düzeltmesi — 11.6'nın açık kararına
  bağlı; kısmi sürümde değişmeyen alanların günlükte temsili **K-107** (teknik —
  kaynak belge kendi içinde kararsız).
- **Olay müdahalesi:** sinyaller (Katman-1 kırmızı — en güçlü · eşleşmezlik log
  yığılması · kötü içerik → damga üzerinden sürüm tespiti · yanlış sektör çözümü).
  İlk güvenli aksiyon paket geri çekme; **ilk pakette rollback uygulanamaz** (önceki
  sürüm yok) — tek çıkış deaktivasyon; deaktivasyon desteklenen geçiştir (**K-38
  kapandı** — Bölüm 10.3), prosedür kesinleşti. Paketsiz markada tek bayt
  fark → pazarlıksız geri alma.

## 13.4 İşletime hazırlık kontrol listesi (taze sayım: 20 madde — snapshot §14 tablosu atıfla)

Maddelerin içeriği kendi bölümlerindeki statüsünü korur. **İki kullanıcı kararı
KAPANDI (Eray, 2026-08-23):** (a) liste ilk aktivasyon öncesi KAPIDIR — komut ailesi
maddeleri otomatik ön-kontrolle işaretler, yöneticiye özet + TEK onay düşer
(**K-69**) · (b) işaretleme sorumlusu operatördür — solo işletimde Eray (**K-70**;
K-54 bölünmez kararıyla tutarlı).

## 13.5 Roller (bağlayıcı çekirdek — tam tablo snapshot §15)

- **Yönetici/operatör:** brief sektör bloğu + üç araştırmayı elle koşma + tur
  tetikleme + özet inceleme + **aktivasyon/ret/rollback onayı**. Kalıp-kalıp
  sentezlemez; motoru atlayamaz. ⚠️ K-23'ün yöneticiye-düşürme seçeneği benimsenirse
  kararsız maddeler ikinci müdahale noktası olur (K-23 açık — "yalnız aktivasyon"
  hükmü o karara koşulludur).
- **Denetçiler:** karar vermez. **Sentez:** karar üretir ama motorlu modelde aday
  set üreticisidir (rol hükmü revizyonu 8.7/4); `active` yapamaz. **Motor:** kural
  sınırında uygular; `active` yapamaz (K-28). **Müşteri:** yalnız kendi atamasını
  teyit eder; bakımı görmez/tetikleyemez/onaylayamaz.
- **Teknik sahip:** rol zorunlu ve kurulumda fiilen kullanılıyor; **atama açık**
  (tek hakem önerisi: Claude Code hattı + adversarial review — korunur).
- **Yetki seviyesi ayrımı NORMATİF** (İlke 8'in proje karşılığı): operatöre ürün
  seviyesi sorulur; şema/imza/algoritma doğruluğu inceleme zincirinin işi — kullanıcı
  onayına çevrilmez. İnceleme raporlarının saklanması teknik iş kalemi (ham katmanın
  `review` türüyle KARIŞTIRILMAZ — o denetçi çıktısıdır).
- **Açık rol kararları** (kullanıcı seviyesi — snapshot Bölüm 17): bilgilendirme
  hedefi · bulgu kabul yetkisi · FYI yüzey bağı. İşaretleme sorumlusu KAPANDI
  (K-70 = operatör — 13.4); alarm sorumlusu KAPANDI (K-56 kapanışıyla: uyarı hedefi
  ve sorumlusu yönetici — 14.4). **Rol bölünmesi K-54 — KAPANDI (Eray, 2026-08-23): bölünmez** (solo
  işletim; ölçek gelince yeniden açılır). **"Faz 1'de hukuk onayı gerekmez" — KAPANDI (K-144, Eray
  2026-08-23): benimsendi, risk kabulü** (yalnız kamuya açık kaynak derlemesi; hukuk
  eşiği gerektiren ürünleştirme + platform kazıma kapsam dışı — kapsama girerse
  yeniden açılır).

---

# 14. Doğrulama ve kabul

*(Girdi: snapshot §13. **Bu bölüm eşik üretmez** — ölçülmemiş hiçbir değer kabul
kriteri/eşik/kapı yapılmaz; bazı yerlerde eşiğin konulup konulmayacağı da açıktır.)*

## 14.1 Deterministik çekirdek (kaynakta karara bağlı — dördü uçtan uca kriter)

1. Ham artefakt `UPDATE`/`DELETE` → istisna. 2. `INSERT` başarılı, `run_id` altında
sorgulanabilir. 3. İkinci `active` → indeks hatası. 4. Yazım-öncesi şema+boyut
doğrulaması. Ek: `(sector_id, version)` ihlali hata verir · `sub_sector_id` NULL
kalabilir · geri doldurma yok · migration geri alınabilir (sıra Bölüm 6.2'de
bağlandı) · marka kök-sektör tam sweep'i (spot yetmez).

## 14.2 Test katmanları

- **Katman-1:** Bölüm 5 sözleşmesi (yüzey kümesi ölçümle kapalı; tek bayt = RED;
  re-runnable).
- **Veri/API regresyonu:** Bölüm 5.3 üçlüsü — alan-bazlı eşitlik ölçütü (katman
  ataması teknik tutarlılık işi, kullanıcı kararı değil).
- **İş kuralı senaryoları:** yerine-geçme (draft paket → mevcut yol sınırı dahil) ·
  yan-yana yasağı (aktivasyon geçiş anı dahil) · özel gün eşleşme/eşleşmezlik+log ·
  `anma` kısıtı (fixture ile — 11.3; K-119 kapandı: yasak kullanıcı-isteğini de geçersiz
  kılar, beklenen sonuç buna göre) · aday liste
  kapalılığı (boş liste → boş dönüş) · sürtünmesizlik (üretimde soru yok) · K-04
  talimat varlığı · K-05 etiket korunumu + filtre davranışı (12.2) · sürüm ilişkisi
  var/yok · tek-aktif.
- **Motor testleri (Faz 1):** snapshot §13.2(b)'nin maddeleri (taze sayım: 13) —
  her biri kendi açık
  kararına bağlı olanlar işaretli; motor testleri semantik doğruluğu YENİDEN ÜRETMEZ.
- **Katman-2:** içerik tipi başına küçük örneklem (boyut K-11 (a)); kör protokol +
  çapraz sektör testi; rubrik (ayrışma · dağarcık seçimi · kanal uygunluğu · mevzuat ·
  anma/kutlama sızıntısı); **geçme eşiği YOK** — eşiğin konulup konulmayacağı
  K-11 (b).

## 14.3 Güvenlik ve gizlilik

- Kapanmış sınırlar test edilir: müşteri bakım akışını görmez/tetikleyemez/onaylayamaz ·
  motor `active` yapamaz (ilke) · aday listede serbest metin reddedilir · **paket
  tablolarına yazma yalnız operatörün koşu yüzeyinden yapılır (K-135 — KAPANDI, Eray
  2026-08-23: bağlayıcı kural)** — ikinci yazma yüzeyi (panel düzenleme vb.) ancak
  açık kural değişikliğiyle açılabilir; denetim zinciri atlanamaz.
- Açık olanlar test edilemez hâlde bekler: aktivasyon yetkilendirme modeli · K-28
  sunucu zorlaması (K-103). (K-16 ve ham katman okuma yetkisi K-139 kapandı —
  müşteriye kapalı / yalnız operatör; test edilir sınıra geçerler.)
- "Kişisel veri içermez" doğrulaması **gerçek veri yazımı + ilk aktivasyondan önce**
  koşulur (Bölüm 3.7).
- Marka-adı kuralının otomatik denetimi yazım kapısına eklenir (K-15 üçüncü bileşen —
  teknik iş kalemi).
- **Prompt enjeksiyonu savunması (K-10 — KAPANDI, Eray 2026-08-23: Faz 1'de
  KURULMAZ, bilinçli risk kabulü):** araştırma çıktısı dış web kaynaklı LLM
  üretimidir → pakete dolaylı talimat sızabilir; mevcut üç adım (mekanik kapı ·
  iki denetçi · onay) hiçbiri buna ÖZEL değil. Risk kaydında AÇIK tutulur (Bölüm 16
  R-09); yeniden açılma tetiği: paket sayısı/kaynak çeşitliliği artışı.
- Kötüye kullanım (kendini yanlış alt sektöre atama): kontrol önerilmemiş, risk
  kaydında ("düşük" etkisi ölçülmemiş tek-hakem değerlendirmesi).

## 14.4 Gözlemlenebilirlik (log kümesi kapalı değil)

Zorunlu ortak çekirdek: eşleşmezlik log'u · kullanılan paket kimlik+sürümü · okuma/
doğrulama hatası + düşüş · aktivasyon/rollback olayı (kim·ne zaman·hangi sürümler) ·
paketsiz-düşen atanmış marka · koşu artefakt kimlikleri · yazım kapısı red kayıtları.
Motor olayları Faz 1'de eklenir. Hassas veri loglanmaz; paket içeriği log'a tam
basılmaz. Metrikler: paketli/paketsiz sayısı · eşleşme oranı · sürüm başına üretim
(K-07'ye bağlı) · **tur süresi (ölçüm kalemi, kapı değil)** · motor metrikleri.
**Alarm — K-56 KAPANDI (Eray, 2026-08-23, öneriden FARKLI): OLAY-BAZLI ANINDA UYARI
Faz 1'de kurulur** — sektörel modda üretilmesi gereken post paketsiz üretildiğinde
(okuma hatası · eşleşmezlik · bayat atama düşüşü) yöneticiye derhal bildirim; K-45/K-26
yönetici-bildirim mekanizmasıyla aynı altyapı. Eşik/oran alarmı DEĞİL — her olay tek
başına uyarı üretir, ölçülecek sınır yok (İlke 9 çatışmaz). Oran-bazlı alarm ayrıca
istenirse pilot ölçümü sonrası ayrı karar. Uyarı hedefi/sorumlusu: yönetici (solo işletim).
İzlenebilirlik zinciri: post → paket sürümü → karar → kanıt (üç eşdeğer dal: denetçi
satırı / ham kaynak / URL — denetçi satırı zorunlu ara halka DEĞİL).

## 14.5 Kabul matrisi

Snapshot §13.7 matrisi (taze sayım 2026-08-23: 33 satır) bu spec'in kabul çerçevesidir — atıfla bağlanır;
Katman-2 satırlarında "zorunlu" = koşulması+sunulması, sonucu kapı değil. Satır
açılamayan iki senaryo (takvim erişilemezliği · ara-pencere sürüm bağı) kararları
kapanınca eklenir — beklenen sonuç uydurulmaz. Bu spec'in eklediği düzeltme:
carousel satırları K-15 (b) kapanışıyla caption dalı varyasyonu olarak fixture
kümesine girer (Bölüm 5.2/9).

---

# 15. Pilot (kuyumculuk)

*(Girdi: snapshot §16.)*

## 15.1 Kapsam ve mevcut durum

- **Alan:** kuyumculuk alt sektörü — altın/pırlanta/gümüş/değerli taşlı takı
  perakendesi + kişiye özel tasarım/ölçülendirme/bakım-onarım; **saat hariç**.
  Brief'in araştırma kapsamı ≠ paketin kapsamı (gümüşün pakete girişi K-04a).
- **Elde olan:** temel paket için üç bağımsız araç araştırması (ilk-sürüm brief'le;
  düzen farkı ihlal DEĞİL — kaynak kaydı korunur) · özel gün brief'i hazır, koşu
  bekliyor · **gayriresmî** ön hakem turu koşuldu — resmî tur DEĞİL. Resmî zincir
  (hakemlik → sentez → draft → kapı → aktivasyon) **tamamlanmamış sayılır.**
- Pilotun içerik/mevzuat bulguları (yetki belgesi zorunluluğu · emsal ceza · 10 gün
  fiyat penceresi, yürürlük 2026-08-01 — **geçti**) doğrulanmamış aktarımdır; yeri
  resmî denetim turudur. Ham çıktıların eskimesi K-18 kaydına girer.
- **Taze ölçüm (2026-08-23):** kayıtlı iki marka Otomaix (yazılım/teknoloji) ve
  MyGoodShoes (ayakkabı/e-ticaret) — **ikisi de kuyumcu DEĞİL**. Ölçüm
  **K-29'un öncülünü** doğrular (uygun kayıtlı kuyumcu marka yok); **K-29 — KAPANDI
  (Eray, 2026-08-23): A — pilot kontrollü TEST MARKASIYLA koşulur** (kurgu kuyumcu
  markası açılır; B seçeneği kuyumcu-olmayan markalarla anlamlı çıktı üretmezdi).
  "Gerçek kuyumcu beklenir" seçeneği kanonik uzayda YOKTUR — eklenecekse ayrı ürün
  kararı gerekir.

## 15.2 Pilot kararları ve ölçümleri

- **Dört operatör kararı (K-04a–d — K-04'le karıştırılmaz; DB yazımından önce
  kapanmalı):** gümüş girsin mi (öneri: girsin) · kasım indirim dönemi (öneri:
  girmesin; ad eşleşmesi K-01b) · kampanya-aciliyet istisnası (öneri: eklenmesin) ·
  kültürel sahne eklentisi (öneri: Faz 2; Faz 1'e alınırsa kaynaksız-üretim yasağıyla
  çatışma ayrıca çözülmeli).
- **Pilot kararları:** kontrollü test markası — **K-29=A ile KAPANDI (Eray,
  2026-08-23; test markası kurulumu Faz 4 iş kalemi)** ·
  sinyalsiz ilerleme risk kabulü **K-30=A ile kapandı** (aktivasyon beklemez) ·
  pilot bitişi — **K-31 KAPANDI (Eray, 2026-08-23): ÖN KOŞUL MODELİ, takvim süresi
  tanımlanmaz** (süre değeri hiçbir katmanda yok — uydurulmadı; genişleme şart
  listesi K-32…K-37 kapı kararlarında netleşir).
- **Pilotun ölçüm yükümlülükleri:** yöneticinin tur başına gerçek süresi (K-13
  revizyonu + motor ölçek gerekçesinin ölçümü — K-21=C sonrası tek meşru dayanak) ·
  Katman-2 kör örneklem (boyut K-11 (a) — pilot karar evreninde) · gerçek alan
  dağılımı (K-12 girdisi) · motor kalibrasyon karşılaştırma verisi (motorun kararları
  × insan yargısı — her fazda gerekir; artefakt katmanının yeterliliği kabul
  sözleşmesi kalemi).
- **İptal ölçütü:** paketsiz markada herhangi bir Katman-1 regresyonu (deterministik).
  Kör-değerlendirme ayırt-edilememesi İPTAL ÖLÇÜTÜ YAPILMAZ (örtülü eşik üretirdi) —
  olumsuz kalite sinyalidir, K-11 (b) kapanmadan eşik yok.

## 15.3 Genişleme (pilot sonrası)

Beş önerilen genişleme kapısı — **kapı kimlikleri K-32…K-36, her biri ayrı açık
karar** (kapı sorusu "X kapı olsun mu"dur; X'in içeriği ayrı kararlardır ve yeniden
açılmaz): **K-32** Katman-1 tüm yüzeylerde yeşil kapısı · **K-33** ilk tur süresi
ölçülmüş kapısı · **K-34** K-01b-kapanmış kapısı (K-01b sözleşmesi bu spec'te
bağlandı — kapı sorusu ayrı) · **K-35** K-02-kapanmış kapısı · **K-36** atama akışı
gerçek kullanıcıyla denenmiş kapısı. + **K-37** kalibrasyon kanıtı kapısı (ölçeğe
geçiş şartı olması — ürün/risk kararı; kabul sözleşmesi ayrı teknik kalem). Pilotun kapsamadıkları:
hizmet sektörleri (görsel kod yaklaşımı bilinmiyor) · web sitesiz atama · aynı kökte
iki alt sektör · gerçek trafik · `anma` gerçek-gün akışı (K-01a).

---

# 16. Riskler

*(Girdi: snapshot §18 — risk kaydı (taze sayım: R-01…R-35, 35 satır) bu spec'e ATIFLA
bağlanır; kopyalanmaz.
Okuma kuralları korunur: D/O/Y dereceleri ölçülmemiş tek-hakem değerlendirmesidir,
kapıya çevrilmez; tespit hücresi alarm katmanını benimsemez; açık karara bağlı
kontrol öneri statüsündedir.)*

Bu spec'in kapsamına doğrudan giren çekirdek: **R-01/R-02** (kök kova — Bölüm 6
zorunlu işi) · **R-03** (yerine-geçme delinmesi — üç tüketici kapsaması) · **R-04**
(anahtar eşleşmezliği — Bölüm 4.4 sözleşmesi) · **R-06/R-07** (liste-tamamlama +
kanal ihlali — K-04 talimatı + 12.2 filtresi) · **R-08** (paketsiz regresyon —
Katman-1; derhal geri al) · **R-09** (prompt enjeksiyonu — K-10 kapandı: Faz 1'de özel
savunma yok, bilinçli risk kabulü; tespit tanımsız kalır, risk satırı açık) · **R-12** (mevzuat eskimesi — tur dışı kol) · **R-15/R-16/R-23** (ölçek/
bütçe — tümü ölçüm kalemi, kapı değil) · **R-17** (yarım aktivasyon — 10.3) ·
**R-19/R-20/R-21/R-22** (motor riskleri — bariyerler+kuru mod+K-42 açık kararlarına
bağlı) · **R-25...R-35** (tek-hakem satırları — kendi açık kararlarıyla).

**Sekiz sahiplik kararı** (R-25 · R-29...R-35 satırlarının sahibi — ayrı ayrı, kullanıcı
seviyesi) ve **R-35 doğrulama kalemi** (kişisel veri — gerçek veri yazımı/aktivasyon
öncesi) kararlar envanterine (KARAR-KAPANIS-LISTESI + snapshot Bölüm 17) taşınır. Risk kaydının periyodik gözden geçirme
ritmi bu spec'te de AÇILMAZ (dürüst etiket: kaynağı yok; yeniden açılma koşulu —
işletim yordamına gözden geçirme adımı eklenirse).

---

# 17. Kapsam dışı ve dokunulmazlar

## 17.1 Kapsam dışı

Bölüm 2.2 tablosu (evleriyle). Ek: pilotun kapsamadıkları (15.3) ve risk-ritmi kalemi
(Bölüm 16).

## 17.2 Dokunulmazlar (bu işte değiştirilemez)

- `brands.sector` TEXT — canlı girdi (video director · fikir önerme · rakip analizi ·
  legacy); tekilleştirme kapsam dışı bakım borcu.
- `SECTOR_GUIDANCE` **yan-yana basım yasağı** (paket yerine geçer; yasağın ihlali
  kesin başarısızlık — Bölüm 1.3).
- Trend katmanı — alt-sektör satırlarına dokunulmaz, zaten bağışık (taze doğrulandı).
- Legacy `/posts/generate-short-video` — **K-06 açık ürün kararı: ya düzeltilir ya
  açıkça kapsam-dışı notlanır, SESSİZ BIRAKILMAZ.** Bugünkü ölçüm: yol bozuk-boş
  (görünen adla arıyor), ön yüz çağırmıyor; Katman-1 fixture'ına koşulsuz girer,
  K-06 yalnız beklenen değeri belirler.
- 22 legacy şablonun `active` statüsü ve platform-uzunluk sürüklenmesi — bakım borcu,
  bu işte dokunulmaz (beş bakım kalemi beş ayrı karar; hiçbiri birleştirilmedi).
- Yılbaşı kategori tutarsızlığı — pakete miras kalır; evsiz kapsam maddesi (11.2).

## 17.3 Karar envanteri kapanış notu

Bu spec'in kendisinin kapattıkları (kanıt-tabanlı): **K-20=A** (kaynak hükmü) ·
**K-21=C** (kaynaksız sayı düşürüldü) · **K-15 (b)** (carousel — taze ölçüm) ·
**K-01b sözleşmesi** (Bölüm 4.4 — teknik sınıf) · **aday küme kanonik tanımı**
(Bölüm 7.2) · **kanal envanteri tasarımı** (Bölüm 12.2) · **migration geri alma
sırası** (Bölüm 6.2) · **önbellek hükmü** (Bölüm 10.4 — taze ölçümle). Dört kullanıcı
kapanışı (K-22 · K-27 · K-30 · K-05) yerlerine işlendi. Kalan tüm açık kararlar
K-ID atfıyla ilgili bölümlerde taşınır; karar uydurulmadı. Ölçülmemiş hiçbir değer
kapı yapılmadı (İlke 9). Snapshot Bölüm 17 final sweep'i (ID'siz açıkların numaralanması)
sentez deposunun işidir, bu spec'in değil.
