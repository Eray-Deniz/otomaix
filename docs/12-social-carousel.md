# Phase 12 — Carousel İçerik Üretimi (başlangıç 2026-04-27)

**Doküman sürümü:** v1.0 (taslak, kullanıcı onayı bekliyor)
**Kapsam:** Otomaix Social `/icerik-olustur` — carousel (çoklu slide) içerik üretimi
**Hedef dosya konumu:** `~/otomaix/docs/12-social-carousel.md`
**Hazırlayan:** Claude (Anthropic) — mevcut `genel-gorsel-sablon`, `caption_generator.py`, `prompt_builder.py`, `11-social-marketingskills.md` analizi baz alınarak
**Tahmini süre:** 4 sprint, ~3-4 iş günü

---

## 0. Session Başlangıç Talimatı (Claude Code için)

**DİKKAT:** Phase 12 üzerinde çalışmaya başlamadan önce bu bölümü tamamen uygula.

### Zorunlu okuma sırası

Her Claude Code session'ının başında şu dosyaları **SIRAYLA** oku:

1. `~/otomaix/docs/12-social-carousel.md` — **Bu doküman, baştan sona**
2. `~/otomaix/apps/social/backend/CLAUDE.md` — Backend son durum changelog'u
3. `~/otomaix/apps/social/frontend/CLAUDE.md` — Frontend son durum changelog'u

### Durum tespiti ve raporlama

Dosyaları okuduktan sonra kullanıcıya şu formatta rapor ver:

```
Son durum: Phase 12 Sprint X
Tamamlanan: <somut maddelerle — CLAUDE.md girdilerinden>
Sonraki iş: <bir sonraki sprint veya yarım kalan adım>

Onay verirseniz devam edeceğim.
```

**Onay almadan kod yazma.** Kullanıcı "devam" veya eşdeğer onay verene kadar bekle.

### Çalışma kuralları (her session'da geçerli)

`feedback_calisma_kurallari.md` memory girdisindeki 6 zorunlu kural + `feedback_concise_responses.md` (tekrar yok) bu phase'de de geçerli.

---

## 1. Mevcut Durum Analizi

### 1.1 Problem Tanımı

`content_type='carousel'` frontend'de seçenek olarak var, backend'de `slides` JSONB kolonu mevcut (migration 022), ancak **gerçek carousel mantığı yok**. Carousel seçildiğinde tek görsel üretiliyor, slide yönetimi yok, çoklu görsel yayınlama yok. Tüm carousel altyapısı stub durumunda.

### 1.2 Mevcut Görsel Üretim Pipeline'ı (genel-gorsel-sablon)

**Şablon yapısı:**
- 4 form alanı: `ana_konu`, `one_cikan_ozellik`, `cta_url`, `cta_label`
- `contentTypes: ["image"]` — sadece tekli görsel
- `imageTextOverlay`: ana_konu + one_cikan_ozellik → Pillow ile görselin üstüne basılıyor
- 7 görsel açı kategorisi (sorun vurgusu, sonuç vurgusu, sosyal kanıt, merak, aciliyet, kimlik, aykırı)
- CTA kuralı: link varsa platforma göre davran (IG→profil linki, LinkedIn→direkt URL), yoksa yönlendirme yapma

**Akış C pipeline'ı (caption-first):**
1. Form doldur → `POST /posts/generate-caption` → Claude tek `image_prompt` + platform bazlı caption'lar üretir
2. Kullanıcı düzenler → `POST /posts/generate` → fal.ai FLUX'a tek çağrı → tek görsel
3. Webhook → logo overlay + text overlay → `output_url`

### 1.3 Genel vs Ürün/Hizmet Farkı

| | Genel Görsel İçerik | Ürün/Hizmet İçeriği |
|---|---|---|
| **Pre-fill** | Yok | `ana_konu = product.name`, `one_cikan_ozellik = product.description` |
| **product_id** | `null` | Seçilen ürünün ID'si |
| **Dokümanlar** | Marka dokümanları gösterilir | Gizli (ürün dokümanları backend'de otomatik merge) |
| **image_prompt kuralı** | Normal (sahne tarif et) | Ürün görseli varsa: "ürünü tarif etme, sadece sahne/ışık/kompozisyon tarif et" |
| **fal.ai modeli** | FLUX text-to-image | Ürün görseli varsa: nano-banana-2/edit (image-to-image), yoksa FLUX fallback |

### 1.4 Marketing Skills — Canlı Durum (Phase 11 sonrası)

- **Hook kuralı KALDIRILDI** — Claude'u formülsel açılışlara zorluyordu
- **JTBD ve Hyperbolic Discounting KALDIRILDI** — bilgi yokken fabrication'a yol açtı
- **Kalan 3 psikoloji prensibi:** Somutluk, Loss Aversion, Social Proof (+ 2 dallı uygulama kuralı: satış vs bilgi)
- **Model:** Opus 4.6 (constraint uyumu daha iyi)
- **LinkedIn:** medium (50-150 kelime)
- **YAZIM KURALI:** 5 madde (fayda>özellik, somutluk, aktif ses, müşteri dili, CTA formülü)
- **7 görsel açı kategorisi:** genel-gorsel-sablon guidance'ında — carousel'de her slide farklı açı seçimi kritik
- **6 image_prompt kuralı:** Marka adı yasak, ürün adı yasak, Türkçe metin yasak, logo yasak, kompozisyon rehberi, format önerisi

### 1.5 Carousel'de Ne Eksik?

Claude'un tek `image_prompt` ürettiği yerde **N adet slide bazlı image_prompt** üretmesi gerekiyor. Her slide farklı açı/kompozisyon/mesaj taşımalı. Mevcut pipeline'daki tüm kurallar (YAZIM KURALI, PSİKOLOJİ, YASAK, 6 image_prompt kuralı, CTA formülü, platform ton rehberi) carousel'de de aynen geçerli — sadece çıktı formatı ve görsel üretim çoklanacak.

---

## 2. Mimari Kararlar

### 2.1 Değişiklik Noktası — Dosya Haritası

| Dosya | Değişecek mi? | Sprint | Detay |
|-------|--------------|--------|-------|
| `templates_data.py` | Evet | 1 | Yeni `carousel-genel-sablon` template |
| `caption_generator.py` | Evet | 1 | Çıktı formatı: `image_prompt` → `image_prompts[]` (carousel dalı) |
| `prompt_builder.py` | Hayır | — | Tier 1/2/3 yapısı değişmez |
| `_SYSTEM_RULES` | Hayır | — | Tüm kurallar carousel için de geçerli |
| `posts.py` | Evet | 2 | Çoklu fal.ai çağrısı + slides JSONB yazımı |
| `webhooks.py` | Evet | 2 | Çoklu webhook handling + per-slide overlay |
| `fal_ai.py` | Hayır | — | Mevcut `generate_image` / `generate_image_edit` aynen kullanılacak |
| `media_processor.py` | Küçük | 2 | Per-slide overlay (mevcut fonksiyonlar slide bazlı çağrılacak) |
| `upload_post.py` | Evet | 4 | Çoklu görsel yayınlama |
| Frontend `icerik-olustur` | Evet | 3 | Slide sayısı seçici + slide grid preview |
| Migration | Hayır | — | `slides` JSONB zaten mevcut (migration 022) |

### 2.2 Bozulmayacak Mevcut Akışlar

- **Tekli görsel üretim** — `content_type='image'` akışı hiç dokunulmayacak
- **Tier 1 `_SYSTEM_RULES`** — tüm prompt kuralları carousel'de de geçerli, değişiklik yok
- **Tier 2 `build_brand_context`** — marka bilgileri, sektör guidance — dokunulmaz
- **Tier 3 `build_dynamic_content`** — kullanıcı isteği, ürün bağlamı — dokunulmaz
- **`_build_output_format_instruction` (caption_generator.py)** — 6 image_prompt kuralı her slide'a uygulanacak
- **PLATFORM_DEFAULTS** — caption uzunluk/hashtag kuralları carousel'de de aynı
- **Diğer şablonlar** — hiçbiri dokunulmaz
- **`/ai/suggest-ideas`, `/ai/analyze-website`, `/ai/generate-script`** — dokunulmaz

---

## 3. Sprint Detayları

### Sprint 1 — Backend: `carousel-genel-sablon` şablonu + caption generator carousel desteği

**Süre:** 0.5-1 iş günü
**Değişen dosyalar:**
- `apps/social/backend/app/core/templates_data.py`
- `apps/social/backend/app/core/caption_generator.py`

#### 3.1.1 Şablon Tanımı (`templates_data.py`)

- `id: "carousel-genel-sablon"`, `contentTypes: ["carousel"]`, `sectors: ["*"]`
- Aynı 4 form alanı: `ana_konu`, `one_cikan_ozellik`, `cta_url`, `cta_label`
- **Ek form alanı:** `slide_count` (select: 2-10, default 5)
- `imageTextOverlay`: carousel'de **yalnızca ilk ve son slide'a** text overlay uygulanacak (ara slide'lar sade kalacak)
- `prompt.guidance` — carousel'e özel slide dizisi rehberi:
  - **Slide 1 (Hook):** Dikkat çekici açılış — 7 görsel açı kategorisinden MERAK veya AYKIRI tercih et
  - **Slide 2-N-1 (Değer):** Her slide farklı açıdan konuyu işle — tekrar etme, her slide'da farklı açı kategorisi kullan
  - **Slide N (CTA):** Kapanış — aksiyon çağrısı, marka renkleriyle temiz arka plan

#### 3.1.2 Caption Generator Carousel Desteği (`caption_generator.py`)

`content_type='carousel'` geldiğinde çıktı formatı değişecek:

```json
{
  "default_caption": "...",
  "platform_captions": { ... },
  "image_prompts": ["slide1 prompt", "slide2 prompt", ...],
  "hashtags": [...]
}
```

- `image_prompt` (tekil) → `image_prompts` (dizi, slide_count kadar)
- Her slide prompt'unda 7 açı kategorisinden farklı biri seçilecek (çeşitlilik kuralı)
- Son slide prompt'u CTA odaklı: marka renkleri ağırlıklı, temiz kompozisyon
- 6 image_prompt kuralı (marka adı yasak, Türkçe yasak vb.) **her slide prompt'a** ayrı ayrı uygulanacak
- PSİKOLOJİ PRENSİPLERİ: Satış/promosyon carousel'de Specificity + Loss Aversion slide bazlı dağıtılacak (her slide'a zorlamadan)
- YASAK kuralı aynen geçerli — slide sayısı arttıkça fabrication riski artar, özellikle dikkat

**`_validate_templates()` assertion:** 23 → 24

#### 3.1.3 Etki Analizi

- **Risk:** Düşük — yeni şablon ekleme (mevcut şablonlar etkilenmez), caption_generator'da yeni dal ekleme (image dalı bozulmaz)
- **Cache invalidation:** Yalnızca carousel çağrılarında — mevcut image çağrıları etkilenmez
- **Backward compat:** Tam — caller'lar etkilenmez, image akışının response şeması değişmez

#### 3.1.4 Canlı Test Kriterleri

1. Backend'e `carousel-genel-sablon` şablonu sorgulanabiliyor mu? (`GET /templates?content_type=carousel`)
2. `POST /posts/generate-caption` — `content_type='carousel'`, `slide_count=5` ile çağrıldığında response'ta `image_prompts` dizisi 5 elemanlı mı?
3. Her slide prompt'u farklı açıdan mı yazılmış? (monoton stüdyo tekrarı yok mu?)
4. Fabrication kontrolü: prompt'larda uydurma ürün/marka detayı var mı?

---

### Sprint 2 — Backend: Çoklu görsel üretim + slides JSONB

**Süre:** 1-1.5 iş günü
**Değişen dosyalar:**
- `apps/social/backend/app/routers/posts.py`
- `apps/social/backend/app/routers/webhooks.py`
- `apps/social/backend/app/services/media_processor.py` (küçük)

#### 3.2.1 `posts.py` — generate_post carousel dalı

- `content_type='carousel'` + `image_prompts` (dizi) geldiğinde:
  - `slide_count` kadar paralel fal.ai çağrısı (`asyncio.gather`)
  - Her slide için ayrı `fal_job_id` takibi
- `PostGenerate` schema'ya: `image_prompts: list[str] | None` eklenmesi
- **Ürün/Hizmet akışı:** `product_id` set + ürün görseli varsa → her slide için `nano-banana-2/edit` (aynı referans görsel, farklı prompt); görseli yoksa → her slide için FLUX

#### 3.2.2 `webhooks.py` — carousel webhook handling

- Her slide görseli için ayrı webhook callback
- Tüm slide'lar tamamlandığında:
  - Her slide'a logo overlay uygula
  - İlk ve son slide'a text overlay uygula (şablon ayarına göre)
  - `slides` JSONB'yi doldur: `[{image_url, image_prompt, order}, ...]`
  - `output_url` = ilk slide'ın URL'si (kapak görseli / thumbnail)
  - `status = 'ready'`

#### 3.2.3 `slides` JSONB yapısı (migration 022'de kolon zaten var)

```json
[
  {"order": 1, "image_url": "https://...", "image_prompt": "...", "fal_job_id": "..."},
  {"order": 2, "image_url": "https://...", "image_prompt": "...", "fal_job_id": "..."}
]
```

#### 3.2.4 Etki Analizi

- **Risk:** Orta — paralel fal.ai çağrıları maliyet artışı (slide_count × çağrı başı ücret). Kullanıcı farkında olmalı.
- **fal.ai kredi kullanımı:** Her slide ayrı bir fal.ai çağrısı = 5 slide'lık carousel tekli görselin 5 katı maliyet
- **Webhook yarış durumu:** Slide'lar farklı zamanlarda tamamlanabilir — tüm slide'lar tamamlanana kadar post `generating` durumunda kalmalı

#### 3.2.5 Canlı Test Kriterleri

1. 5 slide'lık carousel üretimi başarıyla tamamlanıyor mu?
2. `slides` JSONB doğru dolmuş mu? (5 eleman, sıralı, her biri farklı image_url)
3. Logo overlay her slide'da var mı?
4. Text overlay yalnızca ilk ve son slide'da mı?
5. Ürün/Hizmet akışı: ürün görseli varsa image-edit modeli doğru kullanılıyor mu?

---

### Sprint 3 — Frontend: Carousel UI

**Süre:** 1-1.5 iş günü
**Değişen dosya:** `apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx`

#### 3.3.1 Step 1 — İçerik tipi seçimi

- `contentType === 'carousel'` seçildiğinde görsel ile aynı `imageSubType` seçici gösterilecek: "Genel Görsel İçerik" / "Ürün/Hizmet İçeriği"
- "Devam Et" → `carousel-genel-sablon` şablonu auto-load (image'daki `DEFAULT_IMAGE_TEMPLATE_ID` pattern'i)

#### 3.3.2 Step 2 — Form

- Aynı form alanları (ana_konu, one_cikan_ozellik, cta_url, cta_label) + **slide sayısı seçici** (2-10 dropdown)
- Ürün/Hizmet seçiliyse: ürün listesi + pre-fill (mevcut pattern aynen)
- "Gönderi Metni Üret" butonu → `handleGenerateCaption` — `slide_count` da gönderilecek
- Caption editor'da `image_prompts` dizisi gösterilecek (her slide için ayrı İngilizce prompt — advanced kullanıcılar düzenleyebilir, ilk aşamada gizli tutulabilir)

#### 3.3.3 Step 3 — Slide önizleme

- Tek görsel yerine **slide grid** (2-3 sütun, slide sırası numaralı)
- Her slide kartında: görsel + slide numarası
- "Görseli Üret" butonu → `handleGenerate` — `image_prompts` dizisi gönderilecek
- Üretim sırasında: "Slide 1/5 üretiliyor..." progress göstergesi
- Tüm slide'lar hazır olduğunda grid dolacak
- Platform sekmeli caption önizleme (mevcut `CaptionPreview` aynen)

#### 3.3.4 State değişiklikleri

- `slideCount: number` (default 5)
- `generatedSlides: {order: number, image_url: string}[]`
- Mevcut `captionData` → `image_prompts: string[]` dizisi desteği

#### 3.3.5 Etki Analizi

- **Risk:** Düşük — carousel UI yeni ekran/bileşen, mevcut image akışına dokunulmaz
- **Paylaşılan state:** `imageSubType`, `selectedProduct`, `loadingProducts` carousel için de kullanılacak — mevcut image akışındaki davranış korunmalı

#### 3.3.6 Canlı Test Kriterleri

1. Carousel seçildiğinde "Genel Görsel / Ürün/Hizmet" alt tip seçici çalışıyor mu?
2. Slide sayısı seçici doğru çalışıyor mu? (2-10 arası)
3. Caption üretimi sonrası her slide için ayrı prompt görünüyor mu?
4. Görsel üretimi sonrası slide grid doğru dolmuş mu?
5. Tekli görsel akışında regresyon var mı? (carousel eklenmesi image'ı bozmamalı)

---

### Sprint 4 — Yayınlama + Polish

**Süre:** 0.5-1 iş günü
**Değişen dosya:** `apps/social/backend/app/routers/upload_post.py`

#### 3.4.1 Upload-Post carousel entegrasyonu

- `content_type='carousel'` → `slides` JSONB'den tüm `image_url`'leri oku
- Upload-Post API `POST /upload_photos` endpoint'ine çoklu dosya gönder (multipart, birden fazla `media[]` parametresi)
- Platform desteği: Instagram carousel (çoklu görsel), Facebook album, LinkedIn carousel

#### 3.4.2 Polish (P2 — ilk sürümde opsiyonel)

- Slide sıralama (drag & drop)
- Tek slide yeniden üretme
- Slide silme/ekleme

#### 3.4.3 Canlı Test Kriterleri

1. Carousel post Instagram'a çoklu görsel olarak yayınlanabiliyor mu?
2. Facebook album olarak paylaşım çalışıyor mu?
3. Slide sırası yayınlama sırasında korunuyor mu?

---

## 4. Kapsam Dışı — YAPILMAYACAKLAR

| İş | Neden | Yönlendirme |
|----|-------|-------------|
| Video carousel / Reels carousel | Farklı pipeline (video üretim altyapısı yok) | Ayrı phase |
| Slide bazlı farklı caption | Platformlar tek caption destekliyor | Gerekirse ileride |
| Carousel şablonunda farklı aspect ratio per slide | Platformlar tek aspect ratio zorunlu | Yok |
| Drag & drop slide sıralama | Polish, ilk sürüm için gerekli değil | Sprint 4 P2 |
| Tek slide yeniden üretme | Polish | Sprint 4 P2 |

---

## 5. Uygulama Sırası ve Kullanıcı Onay Noktaları

```
Sprint 1 plan → kullanıcı onayı → kod → commit onayı → push
    → canlı test → kullanıcı test onayı → Sprint 2'ye geç

Sprint 2 plan → kullanıcı onayı → kod → commit onayı → push
    → canlı test → kullanıcı test onayı → Sprint 3'e geç

Sprint 3 plan → kullanıcı onayı → kod → commit onayı → push
    → canlı test → kullanıcı test onayı → Sprint 4'e geç

Sprint 4 plan → kullanıcı onayı → kod → commit onayı → push
    → canlı test → kullanıcı test onayı → Phase 12 KAPANDI

Phase kapanışı:
- backend/CLAUDE.md: Phase 12 kapanış girdisi
- frontend/CLAUDE.md: Phase 12 kapanış girdisi
- 12-social-carousel.md: üstüne "✅ PHASE 12 COMPLETE" bloğu
```

**Canlı test onayı alınmadan bir sonraki sprint'e geçilmez.**

---

## 6. Risk Envanteri

| Risk | Olasılık | Etki | Mitigasyon |
|------|----------|------|------------|
| fal.ai maliyet artışı (5x per carousel) | Kesin | Orta | Kullanıcıya slide sayısının maliyeti etkilediğini göster |
| Slide webhook yarış durumu | Orta | Yüksek | Tüm slide'lar tamamlanana kadar `generating` durumu koru |
| Fabrication riski (çok slide = çok prompt = daha fazla uydurma alanı) | Orta | Orta | YASAK kuralı her slide prompt'a uygulanacak, canlı testte kontrol |
| Monoton slide'lar (hepsi aynı açı) | Orta | Düşük | Guidance'ta çeşitlilik kuralı, her slide farklı açı kategorisi |
| Tekli görsel akışında regresyon | Düşük | Yüksek | Carousel dalı tamamen ayrı, image dalına dokunulmaz |
| Upload-Post carousel desteği platform sınırları | Orta | Orta | Platform bazlı test, Instagram max 10 slide |

---

## 7. Commit Message Formatı

```
feat: Phase 12 Sprint 1 — carousel-genel-sablon + caption generator carousel desteği
feat: Phase 12 Sprint 2 — çoklu görsel üretim + slides JSONB
feat: Phase 12 Sprint 3 — carousel UI (slide seçici + grid preview)
feat: Phase 12 Sprint 4 — carousel yayınlama + polish
docs: Phase 12 TAMAMLANDI — CLAUDE.md kapanış girdisi
```

---

**Belge sonu.**

**Hazırlanma tarihi:** 2026-04-27
**Sürüm:** v1.0 (taslak, kullanıcı onayı bekliyor)
**Kapsam:** Otomaix Social — carousel içerik üretimi (şablon + caption + çoklu görsel + UI + yayınlama)
**Toplam:** 4 sprint, ~3-4 iş günü
