---
title: Sektör Bilgi Paketi Sistemi — Runtime Çekirdek + Araştırma Hattı Sözleşmeleri
status: superseded
superseded-by: docs/specs/2026-08-21-sektor-bilgi-paketi.md
superseded-date: 2026-08-23
date: 2026-07-11
tags: [social-backend, social-frontend, sector-packages, prompt-injection, taxonomy, regression-gate, migrations]
codex_review_status: approved
codex_review_iterations: 7
codex_targeted_fixes: 2
unresolved_high_severity_override: false
codex_review_log: docs/reviews/codex/2026-07-11-sektor-bilgi-paketi.md
---

# Sektör Bilgi Paketi Sistemi — Spec

> ⚠️ **SUPERSEDED (2026-08-23, Eray kararı):** Bu spec geçersizdir. Yerine geçen spec
> `docs/specs/2026-08-21-sektor-bilgi-paketi.md` — tamamen sentez girdisinden
> (`docs/research/2026-08-21-sektor-bilgi-paketi-spec-input.md`) yazılır; bu belge
> yeni spec'in yazımında DİKKATE ALINMAZ.

## 1. Özet ve hedef

**Problem (doğrulanmış kök neden):** Sektörler arası içerik ayrışmıyor. Sektör
katmanının çözünürlüğü düşük ("Kuyumculuk" 12 kök kovada karşılıksız → `genel`e
düşüyor) ve derinliği yetersiz (SECTOR_GUIDANCE caption-yönelimli; görsel kod,
sektörel CTA, özel gün kalıbı yok; görsel director'a sektör tek satır gidiyor).

**Hedef:** Alt-sektör düzeyinde, araştırma+hakemlik hattından geçmiş, SÜRÜMLÜ
"sektör bilgi paketleri"; caption ve görsel/video üretim prompt'larına koşullu
enjeksiyon.

**İşlevsel kapı (başarı ölçütü — K6 iki-katman protokolü, §10):**
- Katman-1 (zorunlu, otomatik, ücretsiz): paketsiz/atamasız markada LLM'e giden
  TÜM prompt metinleri **byte-exact değişmez** — tekrar-çalıştırılabilir
  regresyonla kanıtlanır.
- Katman-2 (operatör onay girdisi): paketli/paketsiz gerçek üretim yan yana
  KÖR değerlendirmede sektörel ayrışma gözlenebilir.

**Girdi dokümanı:** `/root/otomaix-sosyal-medya-arastirmasi/sektor-paket-mimari-karar-dokumani.md`
(2026-07-11'de canlı kod + DB'ye karşı doğrulanmış; K1-K7 karar gündemi bu
seansta kapatıldı — §12). Bu spec, dokümanın ONAYLI kararlarını devralır,
K1-K7'yi bağlar ve marka-DNA sisteminin İKİ bağlantı noktasını (§9, §10.1)
karara bağlar. Marka-DNA'nın kendisi AYRI spec'tir (kapsam dışı).

## 2. Tasarım yönü (Adım 3 sentezi — onaylı)

**Runtime-çekirdek + tek-kapı bağlam sözleşmesi.** Bu spec şunları TAM
çözünürlükte bağlar: veri modeli + migration, taksonomi korumaları, atama
akışı, enjeksiyon kuralları (tek kapı), K1-K7 kararları, Tier 1 hiyerarşi
satırı, K6 ortak regresyon altyapısı, K7 sürüm damgası. Araştırma-hakemlik
komut ailesinin (/sektor-paket-guncelle vb.) MEKANİZMASI bu spec'te YAZILMAZ —
değişmez sözleşmeleri §11'de bağlanır, koreografisi adlandırılmış eve devredilir:
`docs/plans/<tarih>-sektor-paket-komut-ailesi.md` (runtime uygulaması + ilk
elle hakem turu SONRASI ayrı /write-plan-claude-codex seansı).

Elenen alternatifler: tam vertical slice (komut ailesi mekanizması dahil tek
spec — spec/plan şişer, ilk canlı değer gecikir) ve saf soyutlamasız runtime
(her yüzeye tek tek dokunuş — marka-DNA'da aynı yüzeylere ikinci kez dokunulur,
ortak K6 koşumu zayıflar).

## 3. Veri modeli

### 3.1 `social.sector_research_artifacts` (YENİ — ham katman)

Araç başına satır; denetçi/sentez çıktıları aynı tabloda; **salt-ekleme DB
seviyesinde zorlanır** (uygulama disiplinine bırakılmaz).

```sql
CREATE TABLE social.sector_research_artifacts (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id       TEXT NOT NULL,               -- ör. 'kuyumculuk-2026q3'
    sector_slug  TEXT NOT NULL,               -- FK YOK (bilinçli, aşağıda)
    kind         TEXT NOT NULL CHECK (kind IN ('research','review','synthesis')),
    source       TEXT NOT NULL,               -- research: 'gemini'|'claude'|'chatgpt'
                                              -- review: 'claude-code'|'codex'; synthesis: 'claude-code'
    brief_ref    TEXT,                        -- brief dosyası + git hash/tarih
    content_md   TEXT NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX ON social.sector_research_artifacts (sector_slug, run_id);
-- Salt-ekleme: BEFORE UPDATE OR DELETE → RAISE EXCEPTION (trigger)
```

Kararlar:
- **`sector_slug` FK'sız** (girdi dokümanındaki açık soru burada kapanır):
  ham katman taksonomiden bağımsız append-only log'dur — araştırma, alt-sektör
  satırı yaratılmadan ÖNCE koşulabilir. Bütünlük paket katmanında zorlanır
  (`sector_packages.sector_id` FK'lı).
- **`source` gerçek araç adı taşır.** Kör adlandırma (KAYNAK-1/2/3) DOSYA
  katmanının disiplinidir ve süreç boyunca korunur (§11); DB arşiv yazımı
  sentez/karar SONRASI olduğundan körlük görevini tamamlamıştır — araç kimliği
  arşive açık yazılır (Faz 2 araç-kalite analizi için; eşleme insert anında
  operatörden gelir).
- Embedding kolonu YOK (bilinçli — deterministik erişim; örnek havuzu Faz 2).

### 3.2 `social.sector_packages` (YENİ — sürümlü paket katmanı)

```sql
CREATE TABLE social.sector_packages (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sector_id      UUID NOT NULL REFERENCES social.sectors(id),  -- alt-sektör satırı
    version        INT  NOT NULL,
    status         TEXT NOT NULL DEFAULT 'draft'
                     CHECK (status IN ('draft','active','archived')),
    schema_version INT  NOT NULL DEFAULT 1,
    content        JSONB NOT NULL,
    decision_log   JSONB NOT NULL DEFAULT '[]',
    run_id         TEXT NOT NULL,              -- sector_research_artifacts bağı (provenance; §3.2 kilidi)
    created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    activated_at   TIMESTAMPTZ,
    UNIQUE (sector_id, version)
);
CREATE UNIQUE INDEX one_active_package_per_sector
    ON social.sector_packages (sector_id) WHERE status = 'active';
```

Invariantlar (DB seviyesinde zorlanır — trigger):
- **Tek aktif sürüm:** kısmi unique indeks (yukarıda) — iki aktif fiziksel imkânsız.
- **Alt-sektör kilidi (subtype koruması):** `sector_id` yalnız `parent_sector_id`si
  DOLU (alt-sektör) sektör satırına işaret edebilir — BEFORE INSERT/UPDATE
  trigger'ı, işaret edilen satır kök (parent NULL) ise RAISE eder. Kök sektöre
  paket fiziksel imkânsız; elle/script draft insert'leri de kapsanır. Aynı
  trigger fonksiyonu `brands.sub_sector_id` için de kullanılır (§3.4) — düz FK
  bu subtype ayrımını encode edemez, kilit DB'dedir.
- **Donmuşluk (iki kural):** (a) `status != 'draft'` satırda `content` /
  `version` / `schema_version` / `sector_id` / `decision_log` / `run_id`
  DEĞİŞTİRİLEMEZ (BEFORE UPDATE trigger — yalnız `status` ve `activated_at`
  geçişine izin); (b) **damga-donması:** `posts.sector_package_id` tarafından
  REFERANSLANAN satırda — statüsü ne olursa olsun, draft dahil — aynı içerik
  alanları DEĞİŞTİRİLEMEZ (trigger'da EXISTS kontrolü). Önizlenmiş draft'ı
  düzeltmenin yolu YENİ draft sürümü açmaktır (`version`++; evrimsel model
  zaten budur). K7 garantisi böylece mutlaktır: damga varsa, işaret ettiği
  içerik post'u üreten içeriğin TA KENDİSİDİR.
- **Silme:** yalnız `status='draft'` VE `posts`'tan referanssız satır
  silinebilir — trigger draft-only'yi zorlar; FK (NO ACTION) referanslı satırı
  doğal korur. Önizlenmiş (K7 damgalı) draft SİLİNMEZ; reddi `draft → archived`
  geçişiyle yapılır (kanıt zinciri korunur).
- **Durum makinesi (TEK tanım — izinli geçişler tam liste):**
  - `draft → active` — aktivasyon (yalnız operatör, §11; tek transaction'da
    varsa mevcut aktif ÖNCE archived edilir — kısmi indeks gereği draft→active
    ancak aktif satır kalmadığında commit olur); `activated_at = now()`.
  - `draft → archived` — operatör reddi (önizlenmiş/vazgeçilen aday;
    `activated_at` set edilmez).
  - `active → archived` — yeni sürüm aktivasyonunun veya rollback'in ilk adımı.
  - `archived → active` — YALNIZ operatör rollback geçişi; `activated_at`
    yeniden `now()` set edilir.
  - Başka geçiş YOKTUR (`archived→draft`, `active→draft` trigger'da reddedilir).
  **Rollback tek akış (tek transaction):** önce aktif sürümü `archived` yap,
  SONRA hedef (arşivli) sürümü `active` yap — kısmi indeks bu sırayı zorlar.
  Donmuşluk invariantı statüden bağımsız işler: rollback içerik alanlarına
  DOKUNMAZ, yalnız status/activated_at geçer.
- **Aktivasyon-provenance kilidi:** HER `→ active` geçişinde trigger, paketin
  `(sector, run_id)` çifti için `sector_research_artifacts`'ta EN AZ BİR
  `kind='synthesis'` satırının varlığını şart koşar (sektör eşleşmesi
  `sectors.slug` JOIN'iyle; artifacts append-only olduğundan rollback'te de
  daima geçer). Kanıtsız içerik blobu aktive edilemez. **Dürüst sınır:** DB
  minimumu bilinçli olarak synthesis-varlığıdır — tam hat disiplini (3 araç +
  2 denetçi + sentez) §11 sözleşmesinin ve komut ailesinin işidir; acil
  tur-dışı güncellemede de en az sentez kaydı zorunlu kalır.
- Salt-ekleme trigger'ı bu tabloya BİLİNÇLİ konmaz (status geçişleri meşru UPDATE).

### 3.3 `content` şeması ve Pydantic doğrulaması

`content` tek JSONB; alan şeması `schema_version=1`:

```json
{
  "kapsam": "<TR metin>",
  "ton_ve_dil": "<TR metin>",
  "cta_kaliplari": [{"kalip": "...", "tur": "bilgi/satış", "gerekce": "..."}],
  "kanca_kaliplari": ["..."],
  "gorsel_kodlar": "<EN anahtar ifadeler>",
  "video_kodlar": {"hareket": ["<EN, loop-uygun>"], "sahne": ["<EN>"]},
  "takvim_temalari": ["..."],
  "yasaklar_ve_hassasiyetler": ["..."],
  "ozel_gun": {
    "<normalize-slug>": {"tur": "kutlama|anma|ticari-firsat|karma",
      "mesaj_ekseni": "...", "kanca": ["..."], "cta": ["..."],
      "gorsel_vurgu": "<EN>"}
  }
}
```

- **Doğrulayıcı Pydantic modelidir** (backend konvansiyonu; "betik" değil) ve
  **draft yazım anında zorunludur.** Dürüst sınır: bu uygulama-katmanı
  korumasıdır, fiziksel DB kilidi değil (DB-level JSON şema doğrulaması
  bilinçli kurulmaz). Sözleşme: TÜM onaylı yazım yolları doğrulayıcıdan geçer —
  komut ailesi (ileride) ve elle pilot dahil her draft yazımı TEK repo-sahipli
  giriş noktasından yapılır:
  **`apps/social/backend/scripts/import_sector_package.py`** (tek public
  draft-import komutu; doğrulayıcı script'in içinde; gerçekleştirimi plan işi —
  AD burada bağlayıcı). Doğrudan SQL ile `content` yazımı DESTEKLENMEZ; komut
  ailesi insert mantığını KOPYALAMAZ, bu script'i çağırır.
- `video_kodlar` İKİ alt liste taşır (K2 kararı; hakem-sentez v1.2 zaten böyle
  üretiyor: 6a hareket / 6b sahne).
- `ozel_gun` anahtar kuralı: her anahtar normalize-idempotent olmalı —
  `normalize_holiday_key(anahtar) == anahtar` (§7'deki TEK fonksiyon; çift
  gerçek yasağı). Değilse doğrulama hatası.
- **Toplam tavan:** content bütünü ~6.000 karakter (≈2K token) — doğrulayıcıda
  üst sınır (alan-başı hedefler sentez görevinin işi, doğrulayıcı yalnız
  toplamı ve yapıyı zorlar).
- `decision_log` satır şeması: `{"alan", "kalip", "karar": "koru|guncelle|cikar|ekle|kirp",
  "gerekce", "kanit"}` — kanıt formatı `D1#<satır>` / `D2#<satır>` / `KAYNAK-N` / URL.

### 3.4 Mevcut tablolara eklemeler

- `brands.sub_sector_id UUID NULL REFERENCES social.sectors(id)` — dolu → paket
  yolu; boş → bugünkü yol. İKİ katman koruma: DB-level subtype kilidi (§3.2'deki
  trigger fonksiyonu — hangi yazım yolundan gelirse gelsin yalnız
  `parent_sector_id`si DOLU satır kabul) + app-level 422 (UX geri bildirimi).
  `brands.sector_id` ANLAMINI KORUR (kök kova) — dokunulmaz.
- `posts.sector_package_id UUID NULL REFERENCES social.sector_packages(id)` —
  K7 damgası (§10.4). ON DELETE davranışı: default NO ACTION (bilinçli —
  damga, referansladığı paket satırını silinmez kılar; §3.2 silme kuralı).
  **Yayın kilidi:** `sector_package_id` DOLU bir post, işaret ettiği paket o an
  `active` DEĞİLSE yayınlanamaz — `posts` trigger'ı `BEFORE INSERT OR UPDATE
  OF status, sector_package_id` kapsamındadır: satır yayın anlamı taşıyan bir
  status'la (`publishing`/`published`/`partially_published` — tam yayın-durum
  kümesi) OLUŞTURULURKEN, o kümeye GEÇERKEN veya damga alanı DEĞİŞTİRİLİRKEN
  `sector_package_id` doluysa paket statüsü kontrol edilir; `active` değilse
  RAISE. Zaten-published INSERT ve yayınlanmış post'un damgasını draft'a
  yönlendirme bypass'ları da böylece kapalıdır. n8n scheduler + manuel yayın
  dahil TÜM yollar bu kapsamdan geçer →
  preview (draft-damgalı) post fiziksel yayın-dışıdır; paket aktive edilirse
  aynı damga meşrulaşır (aday onaylanmıştır). Scheduler sorgusuna ek ön-filtre
  plan detayı (defense-in-depth); asıl kilit DB'de.
  Paketsiz üretimde kolon NULL kalır (INSERT'te hiç set edilmez). `version`
  ayrı kolon olarak TUTULMAZ: paket satırları sürümün kendisidir ve aktivasyon
  sonrası donmuştur (§3.2) — versiyon JOIN'le türetilir, tek doğruluk kaynağı
  korunur. (Girdi dokümanının "template_fields mi ayrı kolon mu" sorusu böyle
  kapanır: ayrı kolon, tek FK.)

**Migration:** `shared/db/migrations/032_sector_packages.sql` — tek dosya:
iki tablo + trigger'lar + indeksler + `brands.sub_sector_id` +
`posts.sector_package_id`. (Sıradaki numara 032 — canlıda son migration 031;
girdi dokümanındaki "001-030" bilgisi eskimişti.) Adlandırma karışıklığı notu:
mevcut `sector_reports` ve `sector_trend_cache` tablolarıyla karıştırılmamalı.

## 4. Taksonomi: alt-sektörler `social.sectors` içinde (A′) + üç koruma

Alt-sektörler AYRI tablo değil; `sectors`'a `parent_sector_id` DOLU yeni
satırlar (kolon şemada var, bugün 12 kök satırda hepsi NULL). Örn. kuyumculuk
→ parent: e-ticaret-perakende; marka-patent → parent: hizmet.

Korumalar (ZORUNLU işler + regresyon testleri):
1. **`GET /sectors` filtresi** (sectors.py:27-33, bugün filtresiz): `WHERE
   parent_sector_id IS NULL` — kayıt/ayar ekranı açılır listesine alt-sektör
   sızmaz. Tek liste ucu; tüketen 3 frontend sayfası (onboarding, markalar,
   marka-ayarları) tek noktadan kapanır. Alt-sektör verisi frontend'e ayrı,
   amaca özel uçla gider (§5).
2. **`sector_resolver` kök-seviye filtresi** (sector_resolver.py:59, bugün TÜM
   satırları haritalıyor): alt-sektör satırı eklendiği an "Kuyumculuk" yazan
   markanın `sector_id`si TAM eşleşmeyle alt-sektöre çözülür → "brands.sector_id
   = kök kova" invariantı bozulur. Haritaya `parent_sector_id IS NULL` filtresi
   + regresyon testi ("alt-sektör satırı varken 'Kuyumculuk' kök kovaya çözülür").
3. **Trend sistemi:** Layer A zaten `parent_sector_id IS NULL` ile çekiyor
   (layer_a.py:263) — bağışık, İŞ YOK; `sector_trend_cache`e alt-sektör satırı
   girmez (mevcut davranış korunur, test ile sabitlenir).

## 5. Marka → alt-sektör atama (C kararı: LLM önerir, kullanıcı teyit eder)

- `POST /ai/analyze-website` (ai.py:26-89; JSON `{name, description, sector,
  colors, tonality}`) sözleşmesine opsiyonel `sub_sector` alanı eklenir. Aday
  listesi = YALNIZ aktif paketi olan alt-sektörler (sorgudan gelir, prompt'a
  gömülür); model listeden seçer VEYA boş döner. **Server-side doğrulama:**
  dönüş aday listesinde değilse `null`a düşürülür (serbest metin/halüsinasyon
  kapısı kapalı).
- Öneri, marka oluşturma (onboarding) ve marka-ayarları ekranında önceden
  seçili açılır liste olarak gösterilir; kullanıcı değiştirir veya boşaltır.
  Aday listesi frontend'e amaca özel uçtan verilir (örn.
  `GET /sectors/sub-sectors?active_package=true` — ad/yerleşim plan işi;
  invariant: kök liste ucu §4 koruma-1 filtresiyle SAF kalır).
- Web sitesi olmayan marka: kök sektör + marka adı/açıklamasından aday önerisi
  (aynı çağrı ailesi, aynı doğrulama, yine kullanıcı teyitli).
- **İçerik üretim akışına SORU EKLENMEZ** (sürtünme yasağı).
- Mevcut 2 marka elle atanır; toplu geriye dönük atama KURULMAZ.
- Frontend teyit bileşeninin yerleşimi/UX → implementation plan (aday sayfalar:
  onboarding/page.tsx:129, markalar/page.tsx:56, marka-ayarlari/page.tsx:434).

## 6. Enjeksiyon — tek kapı sözleşmesi

### 6.1 Tek kapı (context provider)

Yeni modül `apps/social/backend/app/core/sector_package_context.py`:

- `load_sector_package_context(brand, preview_package_id=None) ->
  SectorPackageContext | None` — üretim isteği başına TEK sorgu:
  `brands.sub_sector_id` → `sector_packages` (`status='active'`); yoksa/boşsa
  `None`.
- **Operatör-only preview modu (Katman-2'nin ön şartı):** `preview_package_id`
  verilirse o paket `draft` statüsünde de yüklenir — draft, AKTİVASYONDAN ÖNCE
  gerçek üretim yolunda değerlendirilebilir (§10.3). Üç invariant:
  (a) preview girişi kullanıcı-erişilebilir API yüzeyinden AYARLANAMAZ —
  yalnız operatör-iç yol (internal-korumalı; mekanizma plan işi);
  (b) parametre verilmediğinde davranış birebir normal yol — draft paket DB'de
  dururken bile hiçbir yüzeye sızmaz (K6 fixture'ı bunu ayrıca kanıtlar);
  (c) **sektör eşleşme şartı:** preview YALNIZ `sector_packages.sector_id ==
  brand.sub_sector_id` olan paketi yükler — eşleşmiyorsa VEYA markanın
  `sub_sector_id`si boşsa RED (yükleme yok, hata; önce §5 ataması yapılır).
  Yanlış markayla yanlış sektörün paketinin önizlenmesi — ve K7'nin yanlış
  kanıt damgalaması — fiziksel olarak kapalıdır.
  Preview üretimlerinde K7 damgası draft paketin id'sini taşır (Katman-2 örnek
  eşleştirmesi buradan). Preview post'ları YAYINLANAMAZ — iddia değil, DB
  invariantı: §3.4 yayın kilidi draft-damgalı post'un yayın-durum kümesine
  (`publishing`/`published`/`partially_published`) her geçişini VE o kümede
  doğrudan oluşturulmasını trigger'la reddeder (scheduler dahil; INSERT +
  UPDATE kapsamı). Reddedilen draft SİLİNMEZ,
  `archived`a çekilir (§3.2 — damga kanıt zinciri korunur; silme yalnız hiç
  önizlenmemiş/referanssız draft'ta).
- `SectorPackageContext` = `{package_id, version, sector_slug, content}`
  (doğrulanmış Pydantic content).
- Tüketici API'si (yüzeyler yalnız bunları çağırır; imza ayrıntıları plan işi):
  - `tier2_block(ctx) -> str` — §6.3 bloğu (metin alanları)
  - `special_day_block(ctx, holiday_name_tr) -> str | None` — §7 (eşleşmezse
    None + log)
  - `visual_language_line(ctx) -> str` — görsel kodlar satırı (§6.4)
  - `motion_pool(ctx) -> list[str]` — §8 (hareket havuzu)
- **Değişmezlik invariantı:** `ctx is None` iken HİÇBİR tüketici yüzeyde tek
  karakter değişmez (K6 Katman-1 bunu kanıtlar).
- **DNA bağlantısı:** marka-DNA alanları ileride AYNI kapıya (bu modüle) eklenir;
  yüzeylere ikinci kez dokunulmaz, ikinci altyapı kurulmaz.
- Önbellek: ek mekanizma YOK — paket marka başına sabit metindir, ancak sürüm
  aktivasyonunda değişir; Tier 2 Anthropic prompt cache davranışı aynen
  (içerik değişince doğal miss). Maliyet notu: paket ~1,2-1,5K token; üretim
  başına ~1 cent; zayıf marka bağlamını Opus cache eşiğinin (4096 token)
  üstüne taşıyıp Tier 2 cache'ini açabilir (lehte yan etki).

### 6.2 Yüzey haritası (kapsam TAM listesi — K6 yüzey tamlığının kaynağı)

| # | Yüzey | Çıpa (2026-07-11 doğrulu) | Paketli davranış | Paketsiz |
|---|---|---|---|---|
| 1 | Caption Tier 2 | prompt_builder.build_brand_context 232-235 | SECTOR_GUIDANCE dalı YERİNE §6.3 bloğu | AYNEN |
| 2 | Caption Tier 3 görsel kuralları | caption_generator._build_output_format_instruction 353-359 | `SEKTÖR GÖRSEL DİLİ` satırı eklenir (§6.4) | AYNEN |
| 3 | Özel gün bloğu (Tier 3) | prompt_builder ÖZEL GÜN BAĞLAMI | dönem kalıpları eklenir (§7) | AYNEN |
| 4 | suggest-ideas | ai.py:275-277 | SECTOR_GUIDANCE dalı YERİNE §6.3 bloğu | AYNEN |
| 5 | Kısa video director — text-to-image modu | short_video.py 128-129 (Industry satırı) + 206-231 | `Sector visual language: {...}` satırı | AYNEN |
| 6 | Kısa video director — image-edit modu | short_video.py 187-204 | AYNI satır (İKİ moda da) | AYNEN |
| 7 | Motion havuzu | short_video.py 263-277 `_MOTION_PROMPTS` | havuz = paket `video_kodlar.hareket` (§8) | 7'li liste AYNEN |
| 8 | Legacy `/posts/generate-short-video` | posts.py:846-847 | KAPSAM DIŞI (aşağıda) | AYNEN (bozuk-boş) |

**Yerine-geçme kuralı:** paket bloğu ile SECTOR_GUIDANCE YAN YANA BASILMAZ
(çelişen talimat riski: kök e-ticaret "aciliyet yaratabilirsin" der, kuyumcu
paketi yasaklar). Kök rehber nüansı damıtma aşamasında korunur (sentez görevi
kök rehberi girdi alır — §11 EK'leri).

**Legacy yol kararı (onaylı):** #8 bugün ZATEN sessizce bozuk (rehberi slug
yerine görünen adla arıyor → hep boş; frontend çağırmıyor). Paket enjeksiyonu
ALMAZ; mevcut bozuk-boş davranış bilinçli korunur ve K6 Katman-1 fixture'ı
"değişmedi"yi kanıtlar. Düzeltme/kaldırma ayrı bakım maddesi.

### 6.3 Tier 2 paket bloğu şablonu (K4+K5 koruma talimatı dahil)

```
--- SEKTÖR PAKETİ ({sector_slug}, sürüm {version}) ---
[KULLANIM TALİMATI — bu blok EK BAĞLAM'dır, görev listesi değil:
- Dağarcıktan içeriğe uyan EN FAZLA 2-3 öğe seç; listeyi tamamlamaya çalışma.
- Emin değilsen hiçbirini kullanma — içeriği doğal akışına bırak.
- Ürün bilgisiyle veya marka gerçeğiyle çelişen kalıbı kullanma.
- Markanın sahip olduğunu BİLMEDİĞİN kanalı/hizmeti önerme (WhatsApp, mağaza,
  randevu, e-ticaret vb.).]
Kapsam: {kapsam}
Ton ve dil: {ton_ve_dil}
CTA kalıpları: {cta_kaliplari — kalip (tur): gerekce}
Kanca kalıpları: {kanca_kaliplari}
Takvim temaları: {takvim_temalari}
Yasaklar ve hassasiyetler: {yasaklar_ve_hassasiyetler}
```

- Kullanım talimatı **koda aittir** (sabit metin, paket içeriğinden bağımsız,
  her sürümde aynı) — K4 "listeyi tamamlama" tuzağı + K5 marka-gerçeği filtresi
  (Faz 1 çözümü). Kaynak vaka: psikoloji prensipleri fabrication'ı
  (prompt_builder 115-153'teki mevcut "hepsini kullanma / emin değilsen sokma"
  deseni — aynı dil ailesi kullanılır).
- `gorsel_kodlar` ve `video_kodlar` Tier 2 bloğuna GİRMEZ (görsel/video
  yüzeylerine gider — §6.4, §8; çift enjeksiyon ve blok şişmesi önlenir).
- `ozel_gun` Tier 2'ye GİRMEZ (Tier 3 koşullu — §7).
- Paket her yüzeyde **EK BAĞLAM'dır, geçersiz kılıcı DEĞİL** — kullanıcı isteği
  önceliği (Tier 1) ve şablon yönergeleriyle çatışmaz. TEK istisna: §7 anma/
  kutlama kısıtı.

### 6.4 Görsel dil satırı (iki tüketici)

- Caption director (Tier 3 "image_prompt KATİ KURALLAR" bloğuna ek):
  `SEKTÖR GÖRSEL DİLİ (bu dağarcıktan içeriğe uyanı seç, listeyi tamamlama):
  {gorsel_kodlar}`
- Kısa video director (İKİ modda da, Industry satırının yanına):
  `Sector visual language: {gorsel_kodlar}` (+ özel gün eşleşmişse
  `{ozel_gun.gorsel_vurgu}` aynı satır ailesinde)

## 7. Özel gün kalıpları (K1 + K3 — kararlar bağlandı)

**Mekanizma:** üretimde özel gün seçiliyse (`selectedHoliday.name_tr`,
kaynak `social.public_holidays` — bugün yalnız 2026, 22 kayıt)
`content.ozel_gun[normalize_holiday_key(name_tr)]` okunur; varsa mevcut ÖZEL
GÜN BAĞLAMI bloğuna dönem kalıpları eklenir; **yoksa sessiz düşme + LOG**
(`logger.info` — sessiz regresyon görünür kalır; AYRI eşleme tablosu KURULMAZ).

**K1 — normalize sözleşmesi (TEK fonksiyon, üç tüketici):**
`normalize_holiday_key(name_tr) -> slug`:
1. Gün-eki kırpma: `"... Arife" / "... N. Gün"` → bayram kökü
   ("Ramazan Bayramı 2. Gün" → "ramazan-bayrami"; "Kurban Bayramı Arife" →
   "kurban-bayrami") — gün-bazlı takvim satırları tek dönem içeriğine düşer.
2. Türkçe-güvenli slugify (resmi uzun adlar korunur: "Ulusal Egemenlik ve
   Çocuk Bayramı" → "ulusal-egemenlik-ve-cocuk-bayrami").
3. Dar istisna sözlüğü (kod sabiti; BOŞ başlar — gerçek çakışma çıktıkça dolar).
Kesin regex/işaretler implementation plan işi; davranış ve örnekler burada
bağlayıcı. Üç tüketici AYNI fonksiyonu kullanır (çift gerçek yasağı):
(a) runtime lookup, (b) Pydantic doğrulayıcı (anahtar normalize-idempotent),
(c) sentez görevi EK-J kontrolü (§11).

**K1 operatör kararı (2026-07-11, onaylı):** takvime 10 Kasım (anma), 24 Kasım
Öğretmenler Günü ve okula dönüş dönemi EKLENİR — n8n "Türkiye Takvimi" yıllık
cron'una (ID `tTk1VroTh4AS8lxI`) işlenmesi runtime planında bakım maddesi.
Paket anahtar sözleşmesi takvim genişlemesine BAĞIMLI DEĞİLDİR (eşleşmeyen
dönem zaten sessiz+log düşer).

**K3 — tür etiketi politikası (onaylı: PAKET KAZANIR):** sistemin kategori ton
satırı (`_SPECIAL_DAY_TONE_HINTS`, national/religious/commercial) basılmaya
DEVAM eder; gün paketle eşleşmişse paket `tur` kısıtı blokta AÇIKÇA üstün ilan
edilir. Blok şablonu:

```
--- SEKTÖR PAKETİ DÖNEM KALIPLARI ({dönem adı}) ---
[Kullanım: uyan 1-2 kalıbı seç; listeyi tamamlama; marka gerçeğiyle çelişeni alma.]
Tür: {tur}
{tur ∈ (kutlama, anma) ise: "BU DÖNEMDE SATIŞ ÇAĞRISI KULLANMA — kutlama/saygı
çerçevesinde kal. Bu kısıt, yukarıdaki kategori ton önerisiyle çelişirse BU
kısıt geçerlidir."}
{tur = anma ise ek: "Mizah ve promosyon dili tamamen kapalı."}
Mesaj ekseni: {mesaj_ekseni}
Kanca kalıpları: {kanca}
CTA / kutlama kalıpları: {cta}
```

- `gorsel_vurgu` görsel yüzeye gider (§6.4).
- Anma/kutlama kısıtı, paketin **tek geçersiz-kılıcı** olduğu yerdir (K3).
- Bakım notu: Yılbaşı DB'de "national" kategorili (mevcut tutarsızlık) —
  düzeltmesi ayrı bakım maddesi, bu spec'in işi değil.

## 8. Video hareket dili (K2 — onaylı: Faz 1, seçenek a)

- Paketli markada `_pick_motion_prompt()` seçimi `content.video_kodlar.hareket`
  havuzundan yapılır; **paketsiz markada mevcut 7'li `_MOTION_PROMPTS` listesi
  BYTE-EXACT aynen kalır** (mekanik aynı — `random.choice`; yalnız havuz koşullu).
- `video_kodlar.sahne` listesi director yüzeyindeki görsel dil satırına katkı
  verir (still sahne çeşitliliği); hareket listesi YALNIZ motion havuzuna gider
  (Claude director'dan geçmez — Wan'a giden motion_prompt yüzeyi ayrıdır,
  short_video.py 263-277).
- K6 Katman-1 motion karşılaştırması HAVUZ DÜZEYİNDEDİR (rastgele seçim değil,
  havuz içeriği karşılaştırılır — §10.1).

## 9. Tier 1 hiyerarşi satırı (marka-DNA bağlantı noktası 1 — TEK SEFERDE)

`_SYSTEM_RULES` içindeki mevcut "MARKA TONU ÖNCELİKLİDİR" bloğu
(prompt_builder.py:111-113) TEK SEFERDE şu hiyerarşiye genişletilir:

> **marka DNA'sı/tonu > sektör paketi/rehberi > platform tonu.**
> Çatışma durumunda daha üstteki kazanır. (Sektör paketi/rehberi markaya EK
> bağlamdır; markanın kendi tonunu/kimliğini geçersiz kılamaz. Platform tonu
> en alttaki uyarlama katmanıdır.)

- **Dürüst etiket:** bu satırın İLK yazımı, KABUL EDİLMİŞ tek seferlik GLOBAL
  prompt değişikliğidir — tüm markaların Tier 1 metni değişir ve LLM davranışı
  bundan etkilenebilir (DNA alanları boşken bile). "Davranış-nötr" İDDİA
  EDİLMEZ; K6'nın kanıtladığı şey bu değişiklik DEĞİL, ondan SONRAKİ fazların
  (paket sisteminin) paketsiz markaya dokunmadığıdır. (Kullanıcının şartının
  doğru kapsamı: TEK yazım + DNA gelince İKİNCİ deploy/dokunuş gerekmemesi —
  ikisi de korunuyor; hiyerarşinin DNA terimi, DNA alanları gelene dek boş
  kümeye işaret eder, satır metni değişmeden kalır.)
- Tier 1 değişikliği cache'li sistem prompt'unu değiştirir → tek seferlik
  global cache yenilenmesi (bilinen, ucuz davranış). İsteğe bağlı ek kanıt
  (operatör isterse, K6'dan AYRI bir kerelik gözlem): eski/yeni sistem
  prompt'uyla küçük sabit caption korpusu yan yana koşulup nitel fark
  kaydedilebilir (yalnız caption LLM'i — görsel üretim yok, maliyet birkaç cent).
- **Sıralama zorunluluğu:** bu satır Faz 0'da, K6 golden baseline'ından ÖNCE
  yazılır (§10.2) — baseline kabul edilmiş değişikliğin SONRASINI mühürler;
  byte-exact standardına normalize/whitelist toleransı AÇILMAZ.

## 10. K6 işlevsel kapı (iki katman) + K7 damga

### 10.1 Katman-1 — prompt-düzeyi byte-exact regresyon (ortak altyapı)

**Neden prompt düzeyi:** LLM çıktısı stokastik (temperature=1.0, seed yok) —
çıktı farkının kaynağı (paket mi rastgelelik mi) ayırt edilemez; görsel/video
üretimiyle test fal.ai kredisi yakar. Determinizm LLM'e GİDEN metinlerde aranır.

**Ev:** `apps/social/backend/tests/regression/` — pytest + golden dosyalar
(`golden/` altında, repo'da commit'li). Koşum: tek komut
(`pytest tests/regression/ -q`), **tekrar-çalıştırılabilir + byte-exact**
(golden == üretilen string; normalize/whitespace/anlam toleransı YOK).

**Fixture matrisi × yüzey kapsamı:** sabit marka/şablon/ürün/özel-gün
fixture'ları (DB'siz — prompt kurucu fonksiyonlar saf girdilerle çağrılır);
üç marka profili: (a) paketsiz, (b) paketli (sabit örnek paket content'i),
(c) DNA-boş (bugün paketsizle özdeş; marka-DNA spec'i geldiğinde DNA-dolu
fixture AYNI koşuma eklenir — **bağlantı noktası 2: ikinci altyapı kurulmaz**).
Kapsanan yüzeyler = §6.2 tablosunun TAMAMI (#1-#8; #7 havuz-düzeyi liste
karşılaştırması; #8 legacy yol "değişmedi" fixture'ı). suggest-ideas prompt
kurulumu bugün ai.py içinde inline — harness'ta yakalanabilir olması için
kurulumun fonksiyona çıkarılması plan işidir (davranış değişmez, K6 kanıtlar).

**Kanıt kuralları:**
- (a) paketsiz fixture çıktıları == golden (byte-exact) → "paketsiz markada
  bit-değişmezlik" kanıtı;
- (b) paketli fixture çıktılarında paket bloğu/satırı/havuzu MEVCUT ve
  SECTOR_GUIDANCE YOK (yerine-geçme kanıtı);
- (c) golden dosya değişikliği = bilinçli davranış değişikliği → ayrı commit +
  gerekçe (golden'lar sessizce güncellenemez).

### 10.2 Baseline sıralaması (Faz 0)

1. Tier 1 hiyerarşi satırı yazılır (§9) — tek başına, kendi commit'i.
2. Harness iskeleti + paketsiz golden baseline O KODDAN üretilip commit edilir.
3. Sonraki TÜM fazlar (migration; tek kapı + enjeksiyon + damga; atama; pilot)
   paketsiz golden'ları DEĞİŞTİRMEDEN geçmek zorundadır.

### 10.3 Katman-2 — kör örneklem (operatör onay girdisi)

Az sayıda GERÇEK üretim: aynı ürün sınıfı, paketli/paketsiz yan yana; içerik
tipi başına 3-5 çift (caption+görsel; kısa video pilotta 1-2 çift — maliyet
bilinçli ve sınırlı). **Paketli taraf, aday DRAFT sürümüyle §6.1 preview modu
üzerinden üretilir** — draft aktivasyondan ÖNCE, gerçek üretim yolunda test
edilir; normal markalar draft'ı asla görmez. Ön şart: pilot markasına
alt-sektör ataması yapılmış olmalı (§6.1 sektör-eşleşme şartı — preview
yanlış sektörün paketini yüklemez). Operatör (Eray) kör değerlendirir:
"hangisi kuyumcu postu?" ayrımı gözlenebilir mi? Sonuç aktivasyon onayının
girdisidir (§11). Kuyumcu/ayakkabıcı çapraz üretim karşılaştırması da bu
örnekleme girer (İşlevsel kapı tanımı).

### 10.4 K7 — paket sürüm damgası

Üretim anında `posts.sector_package_id` yazılır (aktif paketin satır id'si =
sürümün kendisi; preview'da draft id — §3.4 yayın kilidi bu post'ları paket
aktive edilene dek yayın-dışı tutar). Damga-donması (§3.2-b): damgalanan satır
— draft dahil — içerik-donmuştur; önizleme ile aktivasyon arasında içerik
DEĞİŞEMEZ, damga daima post'u üreten içeriği gösterir. Paketsiz üretimde alan
HİÇ yazılmaz (NULL). Kullanım:
Katman-2 örnek eşleştirme, kötü çıktının sürüme izlenmesi, Faz 2 kanıt döngüsü
(etkileşim ↔ paket kalitesi) için geriye dönük temel. Maliyet ~sıfır; şimdi
atlanırsa Faz 2'de telafisi yok.

## 11. Araştırma → hakemlik → yazım süreci (değişmez sözleşmeler; mekanizma AYRI planda)

Periyot 3 ay; araştırma MANUEL (3 arayüzden Deep Research). Akış (B süreci):

```
ADIM A  [MANUEL] 3 bağımsız Deep Research koşusu → KAYNAK-1/2/3.md
        (research-runs/<run_id>/ altına; kör adlandırma dosya adında başlar)
ADIM 0  brief-doctor (mekanik kontrol, LLM YOK; 3 KAYNAK dosyası üzerinde —
        elenen/eksik kaynak EK-E raporunda belgelenir, kalanlarla devam)
ADIM 1  Denetçi-1 (Claude Code) — yapılandırılmış iddia tablosu ┐ bağımsız,
ADIM 1' Denetçi-2 (Codex)       — aynı format                   ┘ kör
ADIM 2  Sentez — alan alan hizalama + evrimsel kararlar
ADIM 3  draft JSON + decision_log + açık sorular + onay özeti
ADIM 4  [OPERATÖR] onay → aktivasyon (tek transaction, §3.2 sırası:
        varsa mevcut aktifi archived yap → draft'ı active yap)
```

Bu spec'in BAĞLADIĞI değişmezler (komut ailesi bunlara uyar):
- **Dosya sözleşmesi:** koşu başına `research-runs/<run_id>/` (repo DIŞI,
  araştırma klasöründe): `brief.md` (=EK-A) + `KAYNAK-1/2/3.md` (kör; araç
  eşlemesi süreç boyunca YALNIZ operatörde, dosya adında araç yok) +
  `brief-doctor-raporu.md` (EK-E) + `denetci-1/2-raporu.md` (EK-F/G) +
  `birlesik-taslak.md`.
- **Görev dosyaları sözleşmedir:** `_SABLON.md` (güncel) + `hakem-denetci-gorevi.md`
  v1.1 + `hakem-sentez-gorevi.md` v1.2. EK bağları: EK-H = aktif paket content;
  EK-I = decision_log'lardan karar='cikar' satırları; **EK-J = `public_holidays`
  güncel `name_tr`+`category` dökümü** (ozel_gun anahtarlarının tek doğruluk
  kaynağı; §7 normalize fonksiyonuyla birlikte çalışır); **EK-K = markanın kök
  sektörünün SECTOR_GUIDANCE metni** (yerine-geçme kuralının nüans-kaybı önlemi:
  damıtma kök rehberi girdi alır — girdi dokümanı 5.1 onaylı kararı. NOT:
  hakem-sentez v1.2 girdi listesinde EK-K henüz yok → ilk resmî turdan önce
  görev dosyasına işlenir, v1.2→v1.3).
- **Evrimsel model:** yeni sürüm = aktif paket + yeni araştırma + kalıp-başına
  açık karar; "yeni araştırmada geçmiyor" TEK BAŞINA çıkarma gerekçesi DEĞİL —
  **çıkarma pozitif kanıt ister**; onay özetinin İLK bölümü çıkarılanlar listesi;
  geri-ekleme çelişkileri açık soruya düşer (arşiv güvenceleri: girdi dokümanı §7).
- **DB disiplini:** hat DB'ye YALNIZ `draft` yazar; `active` geçişi YALNIZ
  operatör; durum makinesi ve rollback §3.2. Draft, üretime YALNIZ §6.1
  operatör-only preview moduyla girebilir (Katman-2 değerlendirmesi için);
  normal yol yalnız `active` yükler. Tur-DIŞI acil güncelleme (mevzuat) aynı
  draft→active mekanizmasıyla her an koşulabilir — ayrı mekanizma YOK.
- **Kör adlandırma** dosya adında başlar ve hakemlik süreci boyunca korunur;
  DB arşiv yazımı karar-sonrası olduğundan araç kimliği orada açıktır (§3.1).
- **Denetçi-2 (Codex) web erişimi** ilk koşuda doğrulanır; yoksa görev metnindeki
  "yapamıyorsan raporda belirt" kuralı devrede (sentez URL-kanıt ağırlığını buna
  göre ayarlar — v1.2'de mevcut).
- **İlk resmî kuyumculuk turu ELLE koşulur** (görev dosyalarıyla, komutsuz);
  koşu artefaktları (research/review/synthesis, `run_id` altında) ve draft
  DB'ye YALNIZ `apps/social/backend/scripts/import_sector_package.py` ile
  yazılır (Pydantic doğrulayıcı script'in içinde — §3.3 sözleşmesi; doğrudan
  SQL yazımı desteklenmez;
  aktivasyon-provenance kilidi §3.2 sentez kaydını arar — artefaktlar en geç
  aktivasyondan önce, doğal akışta draft'la birlikte yazılır). Komut ailesi bu
  deneyimden SONRA planlanır — ev:
  `docs/plans/<tarih>-sektor-paket-komut-ailesi.md`.

Eski Kaynak-1/2/3 çıktılarının yeniden üretimi BİLİNÇLİ olarak spec+uygulama
sonrasına, resmî tur öncesine ertelendi (girdi dokümanı KARAR notu; en pahalı
manuel adım sözleşmeler donunca TEK SEFER koşulur). Eski dosyalar silinmez
(ham-katman kaydı + brief-doctor test verisi).

## 12. Operatör kararları (2026-07-11 bu seansta verildi — kayıt)

| Karar | Sonuç |
|---|---|
| K1-takvim | 10 Kasım + Öğretmenler Günü + okula dönüş takvime EKLENİR (n8n cron güncellemesi bakım maddesi) |
| K3 çakışma | PAKET `tur` kazanır; kategori satırı basılmaya devam, paket kısıtı blokta açıkça üstün |
| K2 hareket | Faz 1'de, seçenek (a): paketli→paket havuzu, paketsiz→7'li aynen |
| Gümüş kuyumculuk | Pakete GİRER |
| Kasım indirim dönemi | Pakete GİRMEZ (ileride kampanya içerik türüne) |
| Kampanya-aciliyet istisnası | EKLENMEZ (sistem prompt'u sahte-kıtlık yasağı sınırı çiziyor) |
| Kültürel sahne eklentisi | Faz 2 (kaynaklarda yok, üretim gerektirir) |
| Faz 1 aktif paket tavanı | ≤5 — OPERASYONEL pilot hedefi, DB/uygulama zorlaması YOK (bilinçli; ilk turda tur-başına süre ölçülüp revize edilir — sert invariant değil) |
| Komut ailesi mekanizması | AYRI plan (runtime + ilk elle tur sonrası) |
| Legacy generate-short-video | Kapsam dışı + açık not (§6.2 #8) |

## 13. Kapsam dışı (bilinçli — evleriyle)

- Marka-DNA sisteminin kendisi (alan seti, çıkarım, banned_words) — evi:
  `marka-dna-mimari-karar-dokumani.md` → kendi spec seansı. Bu spec yalnız iki
  bağlantı noktasını bağladı (§9, §10.1).
- Marka kanal envanteri (K5 tam çözümü) — evi: marka-DNA G1 (5. alan adayı).
- Sosyal platform kazıma (tarayıcı ajanı; hukuki değerlendirmeyle), pgvector
  örnek havuzu, tam otomatik araştırma (C süreci), müşteri etkileşim kanıt
  döngüsü, paket satışı (hukuki görüş eşiği), trend sorgularının alt-sektör
  anahtar kelimeleriyle zenginleştirilmesi — Faz 2 listesi (girdi dokümanı).
- Legacy kısa-video yolunun düzeltilmesi/kaldırılması — ayrı bakım maddesi.
- Takvim veri düzeltmeleri (Yılbaşı kategori) — ayrı bakım maddesi.

## 14. Uygulama sırası (fazlar — plan detaylandırır)

```
Faz 0  Tier 1 hiyerarşi satırı (tek commit) → K6 harness iskeleti
       → paketsiz golden baseline (§10.2)
Faz 1  Migration 032 + taksonomi korumaları (resolver + /sectors filtreleri)
       + regresyon testleri  [golden'lar değişmeden PASS]
Faz 2  Tek kapı modülü + yüzey enjeksiyonları (#1-#7) + K7 damga yazımı
       (paket-bağlamlı üretim yolunda persist — üretimle AYNI fazda) +
       paketli fixture golden'ları  [paketsiz golden'lar değişmeden PASS]
       [RELEASE GATE: paket bağlamıyla üretebilen HİÇBİR artım, damga
       persistence'ı olmadan deploy edilemez — damgasız paket-üretim
       penceresi yasak]
Faz 3  Atama: analyze-website alanı + sub-sectors ucu + frontend teyit
Faz 4  Pilot: kuyumculuk ELLE resmî hakem turu (repo-dışı) → alt-sektör
       satırı + pilot marka ataması → artefakt + draft insert → PREVIEW
       modunda Katman-2 kör değerlendirme (§6.1/§10.3) → operatör aktivasyonu
(sonrası, ayrı plan: komut ailesi /sektor-paket-guncelle)
```

## 15. Uçtan uca başarı kriterleri

1. Migration sonrası: artifacts UPDATE/DELETE hata fırlatır; koşu artefaktları
   `run_id` altında sorgulanabilir; sektör başına ikinci `active` paket indeks
   hatasıyla reddedilir; non-draft `content` UPDATE hata fırlatır; non-draft
   DELETE hata fırlatır; `posts` referanslı draft DELETE hata fırlatır; KÖK
   sektöre paket insert'i ve kök sektörlü `sub_sector_id` ataması hata fırlatır
   (subtype kilidi); `run_id`siz paket insert'i reddedilir (NOT NULL); synthesis
   artefaktı olmayan `(sector, run_id)` için `→ active` geçişi hata fırlatır
   (provenance kilidi); `posts` referanslı paketin (draft dahil) içerik UPDATE'i
   hata fırlatır, referanssız draft düzenlenebilir (damga-donması §3.2-b);
   v1 aktifken v2 aktivasyonu (§3.2 tek-transaction sırası) başarılı, ardından
   v1'e rollback başarılı — her adımda tek aktif satır.
2. Alt-sektör satırları ekliyken: `GET /sectors` yalnız kök döner;
   `sector_resolver` "Kuyumculuk"u kök kovaya çözer (regresyon testleri).
3. K6 Katman-1 PASS: paketsiz fixture'lar golden'larla byte-exact (§6.2
   yüzeylerinin TAMAMI); paketli fixture'da blok/satır/havuz mevcut +
   SECTOR_GUIDANCE yok.
4. Kuyumculuk pilotu: elle tur → artefakt + draft (`import_sector_package.py`
   üzerinden, Pydantic'ten geçer; script geçersiz `ozel_gun` anahtarını /
   tavan aşımını reddeder — test) →
   PREVIEW modunda Katman-2 kör değerlendirmede ayrışma gözlenir → aktivasyon;
   paketli post'ta `sector_package_id` dolu (preview'da draft id), paketsiz
   post'ta NULL. Yanlış-sektör veya atamasız-marka preview çağrısı REDDEDİLİR
   (§6.1-c testi). Draft-damgalı post'un yayın geçişi — `publishing`,
   `published` VE `partially_published` her biri ayrı denenerek — hata
   fırlatır; aynı üç status'la doğrudan INSERT ve yayınlanmış post'un
   damgasını draft pakete yönlendirme (UPDATE OF sector_package_id) de hata
   fırlatır; paket aktive edildikten SONRA aynı post yayınlanabilir (§3.4
   yayın kilidi testi).
   Normal tur artefakt kümesi: `(sector, run_id)` altında 3 `research` +
   2 `review` + 1 `synthesis` satırı (kaynak elemesi EK-E'de, acil-tur küçük
   kümesi decision_log'da belgeli — DB minimumu synthesis, §3.2).
5. **Draft izolasyonu:** DB'de draft paket DURURKEN, preview parametresi
   olmadan üretilen tüm prompt'lar paketsiz golden'larla byte-exact (draft
   hiçbir yüzeye sızmaz).
6. suggest-ideas paketli markada paket bloğuyla, paketsizde bugünkü rehberle
   çalışır (fikir/üretim tutarlılığı).
7. Tier 1 satırı tek seferde yazılmış (kabul edilmiş global değişiklik, kendi
   commit'i); Faz 0 baseline'ı SONRASI hiçbir faz paketsiz golden'ları
   değiştirmedi (paket sisteminin paketsiz markaya dokunmadığının kanıtı);
   marka-DNA spec'i geldiğinde Tier 1'e yeni dokunuş gerekmedi.

## 16. Bakım notları (bu işte DOKUNULMAZ)

- `brands.sector` TEXT kolonu — CANLI taşıyıcı (video director Industry satırı,
  suggest-ideas, rakip analizi, legacy yollar; 7+ okuma noktası). Bu iş
  dokunmaz; "TEXT+UUID çift-yazımı ne zaman tekilleşir" ayrı bakım sorusu.
- Yılbaşı `category='national'` tutarsızlığı; LinkedIn `long` drift'i (yalnız
  legacy şablonlarda, üretim etkisi sıfır); 22 legacy şablonun `active` duruşu
  (startup validation'ı `status=="active"` zorluyor — deprecated işaretleme
  assert değişikliği ister).
- Backend CLAUDE.md migration listesi 027'de kalmış (canlı: 031) — uygulama
  sırasında güncellenir.
