# Phase 7 — Sektör-Spesifik Şablon Sistemi

**Doküman sürümü:** v1.1
**Kapsam:** Otomaix Social `/icerik-olustur` — sektör-spesifik şablon sistemi ile yeniden yapılandırma
**Hedef dosya konumu:** `~/otomaix/docs/07-social-template-system.md`
**Hazırlayan:** Claude (Anthropic) — gerçek kod analizi + kullanıcı kararları doğrultusunda
**Tahmini süre:** 7 sprint × 0.5-1.5 gün = ~8 iş günü

---

## 0. Session Başlangıç Talimatı (Claude Code için)

**DİKKAT:** Phase 7 üzerinde çalışmaya başlamadan önce bu bölümü tamamen uygula. Atla YOK.

### Zorunlu okuma sırası

Her Claude Code session'ının başında şu dosyaları **SIRAYLA** oku:

1. `~/otomaix/docs/00-platform-mimari.md` — Platform genel mimarisi
2. `~/otomaix/docs/07-social-template-system.md` — **Bu doküman, baştan sona**
3. `~/otomaix/apps/social/backend/CLAUDE.md` — Backend son durum changelog'u
4. `~/otomaix/apps/social/frontend/CLAUDE.md` — Frontend son durum changelog'u

### Durum tespiti ve raporlama

Dosyaları okuduktan sonra kullanıcıya şu formatta rapor ver:

```
Son durum: Phase 7 Sprint X
Tamamlanan: <somut maddelerle — CLAUDE.md girdilerinden>
Sonraki iş: <bir sonraki sprint veya yarım kalan adım>

Onay verirseniz devam edeceğim.
```

**Onay almadan kod yazma.** Kullanıcı "devam" veya eşdeğer onay verene kadar bekle.

### Çalışma kuralları (her session'da geçerli)

1. **Env bilgileri:** Tüm DB URL, API key gibi hassas bilgiler `backend/.env`, `frontend/.env`, `crm/.env` dosyalarında mevcut. Bu bilgileri asla kullanıcıya sormak zorunda kalma — dosyaları oku.

2. **Manuel onay:** Senin erişemediğin, kullanıcının elle yapması gereken işlemler varsa (DB migration çalıştırma, Coolify env değişikliği, API key eklemesi vb.) listele, onay bekle, onay verildikten sonra devam et.

3. **CLAUDE.md güncelleme:** Sprint tamamlandığında ilgili CLAUDE.md dosyasına **yeni tarih başlıklı girdi ekle.** Mevcut girdileri **ASLA silme.** Format Appendix A'da tanımlı.

4. **Commit ve push:** Kritik adımlar tamamlandığında commit için kullanıcıdan onay al. Commit mesajı formatı:
   ```
   feat: Phase 7 Sprint X — <özet>
   ```
   Onay sonrası:
   ```bash
   cd /root/otomaix
   git add .
   git commit -m "feat: Phase 7 Sprint X — <özet>"
   git push
   ```

5. **Canlı test:** Push sonrası kullanıcıya canlıda nasıl test etmesi gerektiğini tarif et. Test onayı almadan sonraki sprint'e geçme.

---

## 1. Kapsam ve Strateji

### 1.1 Problem Tanımı

Mevcut `/icerik-olustur` sayfası 3 genel kategori (Ürün / Hizmet / Kurumsal) kullanıyor. 12 sektöre hizmet veren bir platform için bu kategoriler çok yüzeysel kalıyor. Eksiklikler:

- Sektöre özel içerik formatları yok (örn. sağlık için "Biliyor Muydunuz?", e-ticaret için "Ürün Kartı")
- Yapısal form alanları yok — kullanıcı her post'ta sıfırdan prompt yazmak zorunda
- Sektörel CTA, hashtag, disclaimer otomasyonu yok
- Platform-spesifik caption optimizasyonu yok (IG 30 hashtag vs LinkedIn 5 hashtag)
- Claude'a sektörel context gitmiyor, üretim kalitesi ortalama

### 1.2 Seçilen Strateji: Seçenek A (Minimum Viable)

Alternatifler değerlendirildi, soft launch aşamasında olmak nedeniyle **minimum kapsam** seçildi:

| Seçenek | İçerik | Karar |
|---|---|---|
| A — Sadece image şablonları | 22 image şablonu, carousel yok, video şablonu yok | ✅ SEÇİLDİ |
| A+ — Disabled carousel kartları | 22 image + 6 coming_soon | ❌ Karmaşa yaratıyor |
| C — Carousel dahil | Multi-slayt + 28 şablon | ❌ Süre + risk |

**Gerekçe:** Soft launch kullanıcı verisi olmadan carousel önceliklendirmesi tahmini olur. Önce image şablonlarının gerçek kullanım desenini ölç, sonra veri-bazlı olarak carousel/video'ya yatırım yap.

### 1.3 Yeni Özellikler Özeti

Bu iterasyonda gelecek özellikler:

- **22 sektör-spesifik şablon** — E-Ticaret (4), Yemek (4), Sağlık (3), Prof. Hizmet (3), Genel (8)
- **Backend-driven şablon tanımları** — `GET /templates` endpoint, 1 saat cache
- **Dinamik form alanları** — her şablonun kendi structured input'ları
- **Akış C (caption-first)** — AI önce caption üretir, kullanıcı düzenler, sonra görsel üretilir
- **Platform-spesifik caption** — Instagram, LinkedIn, Twitter için ayrı caption'lar (Upload-Post'un mevcut per-platform çağrı mimarisi üzerinden)
- **Disclaimer otomasyonu** — sağlık/hukuk şablonlarında yasal uyarı caption sonuna eklenir
- **Telemetri event'leri** — şablon seçim/kullanım/abandon ölçümü

### 1.4 Kapsam Dışı — YAPILMAYACAKLAR

Bu iterasyonda **kesinlikle yapılmayacak** olanlar:

| Özellik | Neden ertelendi | Hedef sürüm |
|---|---|---|
| Carousel çoklu slayt üretimi | Süre + görsel tutarlılık riski | v2 |
| Coming_soon / "Yakında" kartları | Kullanıcı karmaşa yaratabilir | v2 ile doğrudan aktif |
| Video şablonları | Kalite + maliyet riski | v3 |
| Image-to-image pipeline | Ayrı fal.ai akışı | v2/v3 |
| URL scraping (Trendyol/HB) | Ayrı altyapı | v3 |
| Toplu içerik (Excel import) | İleri özellik | v3 |
| Alt-sektör sistemi | DB `parent_sector_id` var ama kullanılmıyor | v2+ ihtiyaç olursa |
| Otomatik yayın template entegrasyonu | Template'ler kullanıcı doldurmak için, AI değil | v2 (veri havuzu ile) |
| Geçmiş sayfası elden geçirme | Minimum değişiklik (template adı gösterme) | v2 |

### 1.5 Bozulmayacak Mevcut Akışlar

- `special_day` akışı — mevcut `_build_special_day_prompt` kullanmaya devam eder
- `quote` akışı — mevcut `_build_quote_prompt` kullanmaya devam eder
- `video` (faceless) akışı — tamamen dokunulmaz
- `/internal/autoposting/trigger` (n8n) — template sistemini kullanmaz, mevcut hardcoded `content_category='product'` akışı devam eder
- `/ai/suggest-ideas` — template_id null ise mevcut CATEGORY_GUIDANCE mantığı korunur
- `/ai/analyze-website`, `/ai/generate-script` — hiç dokunulmaz

---

## 2. Mimari Kararlar (Konsolide)

### 2.1 Backend-Driven Şablon Tanımları

**Karar:** Şablonlar backend'de tek kaynakta tutulur. Frontend `GET /templates` endpoint'inden çeker.

**Gerekçe:** Frontend + backend çift tanım = kaçınılmaz drift. Tek kaynak = tek gerçek + prompt güvenliği (client promptGuidance'ı manipüle edemez).

**Uygulama:**
- `backend/app/core/templates_data.py` — Python dict olarak tüm şablonlar (startup'ta belleğe yüklenir)
- `backend/app/routers/templates.py` — `GET /templates` endpoint
- HTTP cache: `Cache-Control: public, max-age=3600` (mevcut `/sectors` endpoint ile simetrik)
- Frontend session'da bir kez fetch eder, state'e koyar
- Query params: `?sector=<slug>&content_type=<type>` — server-side filter

**Endpoint response:**
```json
{
  "success": true,
  "data": {
    "templates": [
      { "id": "...", "version": 1, "name": "...", "...": "..." }
    ],
    "version": "1.0"
  }
}
```

### 2.2 Veritabanı Şeması

**Migration:** `shared/db/migrations/022_posts_template_fields.sql`

```sql
-- Phase 7 — template system columns
ALTER TABLE social.posts
  ADD COLUMN IF NOT EXISTS template_id TEXT,
  ADD COLUMN IF NOT EXISTS template_fields JSONB,
  ADD COLUMN IF NOT EXISTS platform_captions JSONB,
  ADD COLUMN IF NOT EXISTS slides JSONB;  -- v2 carousel scaffold, v1'de her zaman NULL

-- Index şablon analitiği ve filter için
CREATE INDEX IF NOT EXISTS idx_posts_template_id
  ON social.posts(template_id)
  WHERE template_id IS NOT NULL;
```

**Geriye uyumluluk:** Tüm kolonlar NULL'lanabilir. Eski postlar etkilenmez. `content_category` kolonu **silinmez** — autoposting ve backward compat için kalır.

### 2.3 Prompt Caching Stratejisi

Mevcut `ai.py:suggest_ideas` pattern'i birebir kopyalanır (3 katmanlı):

| Katman | İçerik | Cache |
|---|---|---|
| 1 — System | Sabit talimatlar (DİL KURALI, JSON format, yasaklar) | `cache_control: {"type": "ephemeral"}` ✅ |
| 2 — Brand context | Marka bilgisi + SECTOR_GUIDANCE + TEMPLATE_GUIDANCE | `cache_control: {"type": "ephemeral"}` ✅ |
| 3 — Dynamic | Template fields + user prompt + RAG docs | Cache yok |

**Kritik:** Sektör rehberi ve şablon guidance **Katman 2'de** (brand context ile). Aynı marka + şablon için tekrar çağrılarda cache hit sağlanır.

**Opus 4.7 min cache token: 4096.** Kısa promptlar cache'e yazılmaz. Tier 2'ye yeterli içerik konulması gerekir — marka + sektör + şablon guidance birleşince genelde 4K+ olur.

### 2.4 Veri Kaynağı Öncelik Sırası

Prompt'a enjekte edilen veriler çatışırsa bu sıraya göre işlenir:

```
1. Form alanları (structured, explicit)   ← EN YÜKSEK
2. Brand kit (logo, renk, ton)
3. RAG dokümanları (context, detay)
4. Sektör guidance (genel rehber)           ← EN DÜŞÜK
```

Template şemasında `prompt.priority` alanında tanımlıdır. Çoğu şablon yukarıdaki varsayılanı kullanır; nadir durumlarda şablon kendi sırasını belirtebilir (örn. "Müvekkil Yorumu" → rag_docs > form_fields).

Prompt'a açıkça yazılır: "Çatışma durumunda form alanlarına öncelik ver."

### 2.5 Akış C — Caption-First UX

**Karar:** Kullanıcı deneyimi şöyle akar:

```
1. Kullanıcı şablon formunu doldurur
2. [Önizle] tıklar
3. AI caption + image_prompt üretir (3-5 saniye) — GÖRSEL HENÜZ ÜRETİLMEDİ
4. Kullanıcı caption'ı görür, düzenler (platform-spesifik de düzenleyebilir)
5. [Görseli Üret] tıklar
6. Fal.ai görsel üretir (30-60 saniye, async)
7. Önizleme sayfası: caption + görsel hazır
8. [Yayınla]
```

**Gerekçe:**
- Kullanıcı caption kontrolü önemli (spesifik kullanıcı talebi)
- Görsel maliyeti (fal.ai $0.04/post) caption onaylanmadan harcanmaz
- Toplam süre paralel-dışı yaklaşımlardan uzun değil (~45s)

### 2.6 İki-Aşamalı Endpoint Yapısı

Akış C için yeni endpoint yapısı:

| Endpoint | Amaç | Yaklaşık süre | Cost |
|---|---|---|---|
| `POST /posts/generate-caption` | Claude call — caption + image_prompt + hashtags | 3-5s | ~$0.01 |
| `POST /posts/generate` (mevcut, değişecek) | Fal.ai call — görsel üretimi | 30-60s async | ~$0.04 |

Caption endpoint'i sonuç döndürdükten sonra frontend kullanıcıya düzenleme fırsatı verir. Kullanıcı "Generate Image" dediğinde ikinci endpoint çağrılır, post kaydı caption'larla birlikte oluşturulur.

### 2.7 Carousel v2 Scaffold

v1'de KULLANILMAYAN ama v2'de sorunsuz eklenmek için eklenen yapılar:

**Scaffold 1 — `posts.slides JSONB NULL` kolonu**
- v1'de her zaman NULL
- v2'de carousel slaytları JSON olarak yazılır
- Maliyet: Migration'a 1 satır

**Scaffold 2 — `_build_prompt(..., mode: str = "single")` parametresi**
- v1'de sadece `"single"` çalışır
- v2'de `"carousel"` implement edilir
- Maliyet: Fonksiyon imzasına tek parametre

**YAPILMAYACAK:** `generate_images() -> list[str]` imza değişikliği. Mevcut `generate_image() -> str` korunur. v2'de gerekirse ayrı fonksiyon eklenir, mevcut bozulmaz.

### 2.8 Sektör Filter Stratejisi

`brands.sector_id` (UUID FK) authoritative kabul edilir. Dual-write sistemi korunur (`brands.sector` TEXT kolonu legacy olarak kalır).

**JOIN sorgusu:**
```sql
SELECT b.*, s.slug as sector_slug, s.display_name as sector_display_name
FROM social.brands b
LEFT JOIN social.sectors s ON b.sector_id = s.id
WHERE b.id = $1
```

**Frontend filter mantığı:**
```typescript
const visibleTemplates = allTemplates.filter(template =>
  template.sectors.includes(brand.sector_slug)
  || template.sectors.includes("*")
)
```

### 2.9 Wildcard vs `genel` Sektörü

- `sectors: ["*"]` → **Tüm sektörlerde görünen şablon** (örn. Hakkımızda, Ekip Tanıtımı)
- `sectors: ["genel"]` → **KULLANILMAYACAK** — karmaşa yaratır. "Genel" sektörüne atanmış markalar sadece `"*"` şablonları görür.

### 2.10 Platform-Spesifik Publishing — Mevcut Kod Uyumu

**Önemli tespit:** Upload-Post entegrasyonu zaten per-platform çağrı yapıyor (`upload_post.py:publish_post` döngüsü → `_publish_single_platform` her platform için ayrı).

**Değişiklik:** `_publish_single_platform` mevcut `title_text: str` parametresini alıyor. Yeni mimariyi şöyle kuracağız:

- `posts.platform_captions JSONB` kolonu: `{"instagram": {"caption": "...", "first_comment": "..."}, "linkedin": {"caption": "..."}, ...}`
- `publish_post` her platform için bu JSONB'den ilgili caption'ı okur, `title_text` parametresine geçirir
- `platform_captions` NULL ise fallback: mevcut `post.caption + hashtags` birleştirme mantığı çalışır (backward compat)

Upload-Post API'nin `{platform}_title` parametrelerine gerek yoktur — zaten tek platform'lu çağrılar var.

### 2.11 Telemetri Event'leri

Frontend analytics event'leri (şablon etkinlik ölçümü için):

```typescript
track('template_selected', { template_id, sector_slug, content_type })
track('template_form_submitted', { template_id, fields_filled: string[] })
track('template_caption_generated', { template_id, platforms })
track('template_caption_edited', { template_id, platform_edited })
track('template_image_generated', { template_id, post_id })
track('template_published', { template_id, post_id, platforms })
track('template_abandoned', { template_id, step: 'form' | 'caption' | 'image' | 'publish' })
```

**Amaç:** 2-3 ay sonra veri bazlı şablon önceliklendirmesi. İyi şablon = çok üretilen + çok yayınlanan. Kötü performans gösteren şablonlar silinir/iyileştirilir.

---

## 3. Şablon Şeması

### 3.1 TypeScript Interface

`apps/social/frontend/lib/templates.types.ts`:

```typescript
export interface Template {
  // Kimlik
  id: string                    // "eticaret-urun-karti" — globally unique, snake-case, sektör prefix
  version: number               // 1, 2, 3... — breaking change'de artar
  name: string                  // Türkçe UI label
  description: string           // Tooltip / açıklama
  icon: string                  // Emoji (v1), sonra lucide icon adı

  // Kapsam
  sectors: string[]             // ["e-ticaret-perakende"] veya ["*"]
  contentTypes: string[]        // ["image"] — v1'de hep image
  status: "active" | "deprecated"

  // Form yapısı
  formFields: TemplateFormField[]

  // Çıktı config
  output: {
    aspectRatioSuggestion?: "1:1" | "4:5" | "9:16" | "2:3"
    slideCount?: { min: number; max: number; default: number }  // v2 scaffold
  }

  // AI prompt
  prompt: {
    guidance: string
    examples?: Array<{
      input: Record<string, any>
      output: { caption: string; imagePrompt?: string }
    }>
    priority: string[]
  }

  // Varsayılan çıktı bileşenleri
  defaults: {
    suggestedCTAs: string[]
    suggestedHashtags: string[]
    disclaimer?: string
  }

  // Platform-spesifik override
  platformOverrides?: {
    instagram?: PlatformOverride
    linkedin?: PlatformOverride
    twitter?: PlatformOverride
    facebook?: PlatformOverride
    tiktok?: PlatformOverride
    threads?: PlatformOverride
    pinterest?: PlatformOverride
    bluesky?: PlatformOverride
  }

  // Meta
  tags?: string[]
  order?: number
}

export interface TemplateFormField {
  id: string                    // snake_case — prompt'ta {product_name} olarak referans
  label: string                 // Türkçe UI
  type: "text" | "textarea" | "number" | "select" | "multi-select" | "url"
  placeholder?: string
  helpText?: string
  required: boolean
  defaultValue?: string | number
  validation?: {
    min?: number
    max?: number
    minLength?: number
    maxLength?: number
    pattern?: string
  }
  options?: Array<{ value: string; label: string }>
  suffix?: string
  group?: string                // "Ürün Bilgisi", "Fiyat", "Yayın"
}

export interface PlatformOverride {
  captionStyle?: "long" | "medium" | "short"
  maxHashtags?: number
  toneAdjustment?: string
  useFirstComment?: boolean
  additionalGuidance?: string
}
```

### 3.2 Pydantic Model (Backend)

`backend/app/models/templates.py`:

```python
from typing import Literal, Optional
from pydantic import BaseModel, Field

class TemplateFormField(BaseModel):
    id: str
    label: str
    type: Literal["text", "textarea", "number", "select", "multi-select", "url"]
    placeholder: Optional[str] = None
    helpText: Optional[str] = None
    required: bool = False
    defaultValue: Optional[str | int | float] = None
    validation: Optional[dict] = None
    options: Optional[list[dict]] = None
    suffix: Optional[str] = None
    group: Optional[str] = None

class PlatformOverride(BaseModel):
    captionStyle: Optional[Literal["long", "medium", "short"]] = None
    maxHashtags: Optional[int] = None
    toneAdjustment: Optional[str] = None
    useFirstComment: Optional[bool] = None
    additionalGuidance: Optional[str] = None

class TemplateOutput(BaseModel):
    aspectRatioSuggestion: Optional[Literal["1:1", "4:5", "9:16", "2:3"]] = None
    slideCount: Optional[dict] = None  # {min, max, default}

class TemplatePromptExample(BaseModel):
    input: dict
    output: dict

class TemplatePrompt(BaseModel):
    guidance: str
    examples: Optional[list[TemplatePromptExample]] = None
    priority: list[str] = Field(
        default_factory=lambda: ["form_fields", "brand_kit", "rag_docs"]
    )

class TemplateDefaults(BaseModel):
    suggestedCTAs: list[str] = Field(default_factory=list)
    suggestedHashtags: list[str] = Field(default_factory=list)
    disclaimer: Optional[str] = None

class Template(BaseModel):
    id: str
    version: int = 1
    name: str
    description: str
    icon: str
    sectors: list[str]
    contentTypes: list[str]
    status: Literal["active", "deprecated"] = "active"
    formFields: list[TemplateFormField] = Field(default_factory=list)
    output: TemplateOutput = Field(default_factory=TemplateOutput)
    prompt: TemplatePrompt
    defaults: TemplateDefaults = Field(default_factory=TemplateDefaults)
    platformOverrides: Optional[dict[str, PlatformOverride]] = None
    tags: Optional[list[str]] = None
    order: Optional[int] = None
```

### 3.3 Şema Kullanım Kuralları

- **`id`**: snake-case, sektör prefix zorunlu (`eticaret-`, `yemek-`, `saglik-`, `hizmet-`, `genel-`), globally unique, değiştirilemez (post'larda referans saklı)
- **`formFields[].id`**: snake_case (underscore), sabit tut (prompt interpolation)
- **`sectors`**: 12 sektör slug'ından biri veya `"*"` wildcard
- **`sectors: ["genel"]` KULLANMA** — karmaşa yaratır
- **`contentTypes`**: v1'de hep `["image"]`
- **`status`**: v1'de hep `"active"`, coming_soon yok

---

## 4. Upload-Post.com Entegrasyonu (Gerçek Kod Üzerinden)

### 4.1 Mevcut Mimari

Mevcut `upload_post.py` dosyası önemli bir özelliği zaten uygulamış: **her platforma ayrı API çağrısı yapılıyor.**

`publish_post()` → `platforms_to_publish` listesini döner, her biri için `_publish_single_platform()` çağırır. Her çağrıda tek `platform[]` + tek `title` parametresi.

Bu, Phase 7 için **iyi haber**: Upload-Post API'nin `{platform}_title` parametrelerine ihtiyacımız YOK. Zaten per-platform çağrı var.

### 4.2 Değişiklik: Per-Platform Caption Kullanımı

Mevcut `_publish_single_platform` signature'ı:

```python
async def _publish_single_platform(
    *, db, post_id, platform, username,
    is_video, media_bytes, media_mime, filename,
    title_text: str  # Bu parametre zaten per-platform alınabiliyor
) -> dict:
```

**Yeni akış (Sprint 6'da uygulanacak):**

```python
# publish_post() içinde:
platform_captions = post["platform_captions"] or {}

for platform in platforms_to_publish:
    # Platform-spesifik caption varsa onu kullan, yoksa fallback
    platform_cap = platform_captions.get(platform, {})
    if platform_cap and platform_cap.get("caption"):
        title_text = platform_cap["caption"]
        first_comment = platform_cap.get("first_comment")
    else:
        # Backward compat: eski caption + hashtags mantığı
        caption = post["caption"] or ""
        hashtags = post["hashtags"] or []
        title_text = caption + (" " + " ".join(f"#{h.lstrip('#')}" for h in hashtags) if hashtags else "")
        first_comment = None

    res = await _publish_single_platform(
        ...,
        title_text=title_text,
        first_comment=first_comment,
    )
```

**Notlar:**
- `platform_captions` JSONB NULL ise eski davranış aynen çalışır (template kullanmayan ve eski postlar)
- `{platform}_first_comment` parametreleri Upload-Post'ta destekleniyor ama canlıda test edilmemiş — Sprint 6'da doğrulanmalı
- Instagram için `useFirstComment: true` olan şablonlarda hashtag'ler caption'dan ayrılır, `first_comment` parametresine gider

### 4.3 Platform Limitleri (Referans)

v1'de tek görsel üretildiği için bu limitler bilgi amaçlıdır. v2 carousel geldiğinde pre-validation'da kullanılacak:

| Platform | Max görsel | Not |
|---|---|---|
| Instagram | 10 | Carousel otomatik |
| Threads | 10 | 10+ otomatik split |
| TikTok | Slideshow | `auto_add_music` opsiyonu |
| LinkedIn | Carousel | Document carousel ayrı |
| Facebook | Album | Caption sadece ilk görsele |
| Bluesky | 4 | En düşük limit |
| X (Twitter) | 4/tweet | 4+ auto-thread |
| Pinterest | Çoklu pin | - |

---

## 5. Sprint Tanımları

Her sprint bağımsız olarak uygulanır, commit edilir, test edilir. Sprint'ler arası bağımlılıklar dikkate alınarak sıralı gidilir.

---

### Sprint 1 — Backend Altyapı

**Hedef:** Template sisteminin temel altyapısını kur. Henüz şablon içeriği yok, sadece yapı.

**Tahmini süre:** 1 gün

**Ön koşul:** Yok (ilk sprint)

#### Dosya Listesi

**YENİ:**
- `shared/db/migrations/022_posts_template_fields.sql`
- `backend/app/core/templates_data.py` (boş dict başlatıcı)
- `backend/app/models/templates.py` (Pydantic modeller)
- `backend/app/routers/templates.py` (GET /templates endpoint)

**DEĞİŞEN:**
- `backend/app/main.py` — templates router kaydı
- `backend/app/routers/auth.py` — /init brands query'sine LEFT JOIN sectors + sector_slug
- `backend/app/models/schemas.py` — PostGenerate + BrandOut güncelleme
- `backend/app/routers/posts.py` — PostGenerate payload yeni field'ları kabul etsin (generate_post INSERT'i henüz kullanmaz, Sprint 3'te)

#### Adım Adım Uygulama

**1.1** Migration dosyası oluştur:

```sql
-- shared/db/migrations/022_posts_template_fields.sql

-- Phase 7 — Template system columns for social.posts
ALTER TABLE social.posts
  ADD COLUMN IF NOT EXISTS template_id TEXT,
  ADD COLUMN IF NOT EXISTS template_fields JSONB,
  ADD COLUMN IF NOT EXISTS platform_captions JSONB,
  ADD COLUMN IF NOT EXISTS slides JSONB;

-- Index for template analytics and filtering
CREATE INDEX IF NOT EXISTS idx_posts_template_id
  ON social.posts(template_id)
  WHERE template_id IS NOT NULL;

COMMENT ON COLUMN social.posts.template_id IS 'Phase 7 — template ID if post was created from a template';
COMMENT ON COLUMN social.posts.template_fields IS 'Phase 7 — structured form data (e.g., {product_name, price})';
COMMENT ON COLUMN social.posts.platform_captions IS 'Phase 7 — per-platform captions from caption-gen endpoint';
COMMENT ON COLUMN social.posts.slides IS 'Phase 7 scaffold — v2 carousel support, always NULL in v1';
```

**1.2** Pydantic modelleri `backend/app/models/templates.py` dosyasında tanımla (Bölüm 3.2'deki kod).

**1.3** `backend/app/core/templates_data.py` oluştur:

```python
"""Template definitions for Phase 7 — Sektör-Spesifik Şablon Sistemi.

Templates are the single source of truth. Loaded into memory at startup,
served via GET /templates endpoint. Frontend fetches and caches for 1 hour.

Sprint 1: Infrastructure setup — TEMPLATES dict is empty for now.
Sprint 2: 22 templates will be added here.
"""

from app.models.templates import Template

# Sprint 2'de doldurulacak — 22 şablon
TEMPLATES: dict[str, Template] = {}

# Sprint 2'de doldurulacak — sektör bazlı guidance
SECTOR_GUIDANCE: dict[str, str] = {}


def get_all_templates(
    sector: str | None = None,
    content_type: str | None = None,
) -> list[Template]:
    """Return filtered list of templates."""
    templates = list(TEMPLATES.values())

    if sector:
        templates = [
            t for t in templates
            if sector in t.sectors or "*" in t.sectors
        ]

    if content_type:
        templates = [
            t for t in templates
            if content_type in t.contentTypes
        ]

    templates.sort(key=lambda t: (t.order or 999, t.name))
    return templates


def get_template_by_id(template_id: str) -> Template | None:
    """Return template by id or None."""
    return TEMPLATES.get(template_id)
```

**1.4** `backend/app/routers/templates.py` oluştur:

```python
"""GET /templates endpoint — serves template definitions to frontend."""

from fastapi import APIRouter, Query, Response

from app.core.templates_data import get_all_templates
from app.models.schemas import OkResponse

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=OkResponse)
async def list_templates(
    response: Response,
    sector: str | None = Query(None, description="Filter by sector slug or '*'"),
    content_type: str | None = Query(None, description="Filter by content type"),
):
    """
    Return all active templates, optionally filtered by sector and/or content type.

    Cached 1 hour (matches /sectors endpoint pattern).
    """
    response.headers["Cache-Control"] = "public, max-age=3600"
    templates = get_all_templates(sector=sector, content_type=content_type)

    return OkResponse(
        data={
            "templates": [t.model_dump() for t in templates],
            "version": "1.0",
        }
    )
```

**1.5** `backend/app/main.py` dosyasına templates router kaydı ekle:

```python
from app.routers import templates as templates_router
app.include_router(templates_router.router)
```

**1.6** `backend/app/routers/auth.py` `/init` endpoint'indeki brands query'sini güncelle:

```python
# Eski (posts değişmez):
# brands = await db.fetch(
#     """SELECT id, name, sector, logo_light_url, logo_dark_url, is_active
#        FROM social.brands WHERE ...""",
# )

# Yeni:
brands = await db.fetch(
    """
    SELECT b.id, b.name, b.sector, b.sector_id,
           s.slug AS sector_slug, s.display_name AS sector_display_name,
           b.logo_light_url, b.logo_dark_url, b.is_active
    FROM social.brands b
    LEFT JOIN social.sectors s ON b.sector_id = s.id
    WHERE b.workspace_id = $1 AND b.is_active = true
    ORDER BY b.created_at
    """,
    workspace["id"],
)
```

**1.7** `backend/app/models/schemas.py` güncelle:

```python
# BrandOut'a ekle:
class BrandOut(BaseModel):
    # ... existing fields ...
    sector_slug: str | None = None         # Phase 7
    sector_display_name: str | None = None # Phase 7

# PostGenerate'e ekle:
class PostGenerate(BaseModel):
    # ... existing fields ...
    template_id: str | None = None          # Phase 7
    template_fields: dict | None = None     # Phase 7
    platform_captions: dict | None = None   # Phase 7 (Sprint 4'te doldurulacak)
    image_prompt: str | None = None         # Phase 7 (Sprint 4'ten gelecek)
```

**1.8** Posts INSERT'i yeni kolonları kabul edecek şekilde genişlet (Sprint 3'te tam refactor olacak, şimdilik minimum uyum — template_id ve template_fields payload'dan alınıp INSERT'e eklensin).

#### Manuel Adımlar (Kullanıcı için)

1. **Migration çalıştır:**
   ```bash
   cd /root/otomaix
   psql $DATABASE_URL -f shared/db/migrations/022_posts_template_fields.sql
   ```
   Çıktı kontrolü: `ALTER TABLE` ve `CREATE INDEX` mesajları görünmeli.

2. **Doğrulama query'si:**
   ```sql
   \d social.posts
   -- template_id, template_fields, platform_captions, slides kolonları görünmeli

   SELECT indexname FROM pg_indexes
   WHERE tablename = 'posts' AND schemaname = 'social';
   -- idx_posts_template_id görünmeli
   ```

#### Test Senaryoları

**Local smoke test (Claude Code tarafında):**
- Backend başlatıldığında import hatası olmamalı
- `GET /templates` endpoint 200 döner, `{"templates": [], "version": "1.0"}`
- `GET /templates?sector=e-ticaret-perakende` de boş array döner (şablon yok henüz)
- `GET /auth/init` çağrısında brands response'unda `sector_slug` field'ı mevcut olmalı

**Canlı test (kullanıcı tarafında):**

```bash
# 1. Templates endpoint
curl https://api.otomaix.com/templates
# Beklenen: {"success": true, "data": {"templates": [], "version": "1.0"}}

# 2. Auth init (JWT ile)
curl -H "Authorization: Bearer <JWT>" https://api.otomaix.com/auth/init
# Beklenen: brands[0].sector_slug alanı var
```

**DB kontrolü:**
```sql
SELECT column_name FROM information_schema.columns
WHERE table_schema='social' AND table_name='posts'
AND column_name IN ('template_id', 'template_fields', 'platform_captions', 'slides');
-- 4 satır dönmeli
```

#### CLAUDE.md Girdi Template'i

`~/otomaix/apps/social/backend/CLAUDE.md`'ye ekle (en üste):

```markdown
## YYYY-MM-DD — Phase 7 Sprint 1: Backend template altyapısı ✅

**Dosyalar:**
- shared/db/migrations/022_posts_template_fields.sql (YENİ)
- backend/app/core/templates_data.py (YENİ — boş dict, Sprint 2'de doldurulacak)
- backend/app/models/templates.py (YENİ — Template, TemplateFormField vb. Pydantic modeller)
- backend/app/routers/templates.py (YENİ — GET /templates endpoint)
- backend/app/main.py (değişti — templates router kaydı)
- backend/app/routers/auth.py (değişti — /init brands LEFT JOIN sectors)
- backend/app/models/schemas.py (değişti — BrandOut.sector_slug, PostGenerate.template_id/fields/captions)
- backend/app/routers/posts.py (değişti — INSERT yeni kolonları kabul ediyor)

**Değişiklikler:**
- social.posts tablosuna template_id TEXT, template_fields JSONB, platform_captions JSONB, slides JSONB NULL kolonları eklendi
- Index: idx_posts_template_id eklendi (WHERE template_id IS NOT NULL)
- GET /templates endpoint eklendi (1 saat cache, boş dönüyor — Sprint 2'de şablonlar eklenecek)
- /auth/init response'una brand.sector_slug, brand.sector_display_name eklendi (LEFT JOIN sectors)

**Manuel adımlar tamamlandı:**
- [x] Migration 022 VPS'te çalıştırıldı
- [x] DB kolonları doğrulandı

**Sonraki sprint:** Sprint 2 — 22 şablon + SECTOR_GUIDANCE doldurma
```

#### Commit Mesajı

```
feat: Phase 7 Sprint 1 — Backend template altyapısı (migration + GET /templates + sector_slug)
```

---

### Sprint 2 — Şablon Kataloğu ve Sektör Rehberleri

**Hedef:** 22 şablonu `templates_data.py`'ye ekle, SECTOR_GUIDANCE dict'ini doldur. Frontend types dosyasını oluştur.

**Tahmini süre:** 1 gün

**Ön koşul:** Sprint 1 tamamlandı

#### Dosya Listesi

**DEĞİŞEN:**
- `backend/app/core/templates_data.py` — 22 template + SECTOR_GUIDANCE ile dolu

**YENİ:**
- `apps/social/frontend/lib/templates.types.ts` — TypeScript interface'ler
- `apps/social/frontend/lib/api/templates.ts` — API client fonksiyonları

#### Adım Adım Uygulama

**2.1** `templates_data.py` dosyasına **Bölüm 6'daki 22 şablonu** Python dict formatında ekle.

Örnek bir şablon nasıl kodlanır (E-Ticaret Ürün Kartı):

```python
from app.models.templates import (
    Template, TemplateFormField, TemplateOutput,
    TemplatePrompt, TemplateDefaults, PlatformOverride,
)

TEMPLATES["eticaret-urun-karti"] = Template(
    id="eticaret-urun-karti",
    version=1,
    name="Ürün Kartı",
    description="Tek ürün için fiyat, indirim ve özellik vurgusu",
    icon="🛒",
    sectors=["e-ticaret-perakende"],
    contentTypes=["image"],
    status="active",
    formFields=[
        TemplateFormField(
            id="product_name",
            label="Ürün Adı",
            type="text",
            required=True,
            placeholder="örn. Apple iPhone 15 128GB",
            validation={"maxLength": 120},
            group="Ürün Bilgisi",
        ),
        TemplateFormField(
            id="price",
            label="Fiyat",
            type="number",
            required=True,
            suffix="TL",
            validation={"min": 0},
            group="Fiyat",
        ),
        TemplateFormField(
            id="old_price",
            label="Eski Fiyat",
            type="number",
            required=False,
            suffix="TL",
            helpText="Opsiyonel — indirim yüzdesi otomatik hesaplanır",
            group="Fiyat",
        ),
        TemplateFormField(
            id="key_feature",
            label="Öne Çıkan Özellik",
            type="text",
            required=False,
            placeholder="örn. A17 Pro çip, 48MP kamera",
            validation={"maxLength": 200},
            group="Ürün Bilgisi",
        ),
        TemplateFormField(
            id="cta",
            label="Çağrı (CTA)",
            type="select",
            required=True,
            defaultValue="Sepete ekle",
            options=[
                {"value": "Sepete ekle", "label": "Sepete ekle"},
                {"value": "Hemen al", "label": "Hemen al"},
                {"value": "Link bio'da", "label": "Link bio'da"},
                {"value": "Şimdi keşfet", "label": "Şimdi keşfet"},
            ],
            group="Yayın",
        ),
    ],
    output=TemplateOutput(aspectRatioSuggestion="4:5"),
    prompt=TemplatePrompt(
        guidance="""E-ticaret ürün kartı şablonu. Tek ürünü öne çıkaran
        statik sosyal medya görseli üretir.

        Görsel yönergesi: Stüdyo çekimi hissi, temiz arkaplan (marka renklerinden),
        ürün merkezde, fiyat/indirim rozeti görünür konumda, marka logosu köşede.
        Modern minimalist stil.

        Caption formülü: Hook (ürün adı + faydası) → Özellik vurgusu →
        Fiyat/indirim → CTA. Abartılı iddia kullanma ("dünyanın en iyisi" vb.).""",
        priority=["form_fields", "brand_kit", "rag_docs"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=["Sepete ekle", "Hemen al", "Link bio'da", "Şimdi keşfet"],
        suggestedHashtags=["indirim", "kampanya", "fırsat", "alışveriş"],
    ),
    platformOverrides={
        "instagram": PlatformOverride(
            captionStyle="medium",
            maxHashtags=15,
            useFirstComment=True,
        ),
        "linkedin": PlatformOverride(
            captionStyle="long",
            maxHashtags=5,
            toneAdjustment="Daha kurumsal, satış dili yumuşatılmış",
        ),
        "twitter": PlatformOverride(
            captionStyle="short",
            maxHashtags=2,
        ),
    },
    tags=["ürün", "fiyat", "indirim"],
    order=10,
)

# ... diğer 21 şablon
```

**ÖNEMLİ:**
- 22 şablonun tam spec'i Bölüm 6'da YAML formatında. Python'a çevirirken Pydantic model'lere uygun dönüştür
- Şablon ID'lerini **sabit tut, değiştirme** (post'larda referans saklı olacak)
- Her şablon için en az 2-4 form alanı olmalı
- `prompt.guidance` 100-400 kelime arası olmalı (Claude'a yeterli bağlam)

**2.2** `SECTOR_GUIDANCE` dict'ini doldur. Öncelikli 4 sektör için ~150-250 kelime, diğer 8 için generic ~50 kelime:

```python
SECTOR_GUIDANCE = {
    "e-ticaret-perakende": """E-Ticaret sektörü için içerik rehberi:

Ton: Enerjik, satış odaklı ama agresif değil. Aciliyet hissi yaratabilirsin
ama sahte urgency kullanma ("son 1 adet" abartısından kaçın).

Öne çıkarılacaklar: Fiyat avantajı, indirim yüzdesi, ürün özellikleri,
kullanıcı deneyimi. Sosyal kanıt (müşteri yorumu) güçlü etki yapar.

Platform öncelikleri: Instagram (görsel + hashtag), TikTok (trend'ler),
Facebook (yaşlı kitle), Pinterest (SEO + inspiration board).

Caption formülü: Hook → Ürün faydası → Fiyat/indirim → CTA

Yasaklar: Karşılaştırmalı reklam, rakip ismi, abartılı iddia
("dünyanın en iyisi"), garanti ifadesi.""",

    "yemek-gida": """Yemek & Gıda sektörü için içerik rehberi:

Ton: Davetkar, samimi, iştah açıcı. Yöresel dokunuşlar mümkünse kullan.
Profesyonel ama sıcak hissi korunmalı.

Öne çıkarılacaklar: Tat deneyimi (kremamsı, ferahlatıcı, baharatlı vb.),
taze malzemeler, şef imzası, atmosfer, zaman (öğle/akşam servisi).

Platform öncelikleri: Instagram (yemek fotoğrafı), TikTok (hazırlık
videoları), Facebook (lokal yerel), Pinterest (tarif arama).

Caption formülü: Duygu hook → Ürün/menü → Tat/hissi → Zaman/yer bilgisi → CTA

Yasaklar: Kalori/diyet iddiası (yasal sorun), "dünyanın en lezzetlisi"
absolut ifade, karşılaştırma.""",

    "saglik": """Sağlık sektörü için içerik rehberi:

Ton: Bilgilendirici, otorite ama anlaşılır. Güven verici. Korku/panik dili
kullanma. Tıbbi jargonu minimal tut.

Öne çıkarılacaklar: Uzmanlık, kanıta dayalı bilgi, hasta deneyimi (izin alınarak),
erken teşhis önemi, koruyucu sağlık.

Platform öncelikleri: Instagram (görsel eğitim), LinkedIn (B2B, akademik),
YouTube (uzun anlatım), Facebook (lokal kitle).

Caption formülü: Bilgi hook (istatistik/soru) → Açıklama → Önlem/öneri →
CTA → DISCLAIMER (otomatik eklenir)

Yasaklar: KESIN tanı koyma, ilaç dozajı tavsiyesi, "size iyileşme garantisi
veriyoruz" türü ifadeler, tıbbi etik ihlali, rakip klinik karşılaştırması.""",

    "hizmet": """Profesyonel Hizmet sektörü için içerik rehberi:

Ton: Profesyonel ama sıcak, yetkin, bilgece. Thought leadership. Otorite +
yardımsever dengeli.

Öne çıkarılacaklar: Uzmanlık alanı, sektörel deneyim, vaka çalışması
(anonimize), mevzuat bilgisi, süreç şeffaflığı, ekip yetkinliği.

Platform öncelikleri: LinkedIn (B2B, thought leadership), Instagram (brand
awareness), Twitter (hızlı sektör yorumu).

Caption formülü: İnsight/gözlem hook → Detay/değer bilgisi → Uygulama → CTA

Yasaklar: Müvekkil özel bilgisi (izin olmadan), kesin hukuki tavsiye,
rakip küçümseme, absolut iddia ("en iyi avukat"), garanti dili.""",

    # Diğer 8 sektör — generic guidance (kısa)
    "teknoloji": "Teknoloji: Yenilikçi, ileri görüşlü ton. İnovasyon, çözüm, kullanıcı kolaylığı öne çıkar. Jargon yığınından kaçın.",
    "egitim": "Eğitim: Motive edici, destekleyici ton. Öğrenci başarısı, eğitim kalitesi vurgusu. Garanti iddiası yasak.",
    "moda-tekstil": "Moda: Estetik, ilham verici ton. Koleksiyon, malzeme, stil hissi. Beden ayrımcılığından kaçın.",
    "turizm": "Turizm: Hayalci, davetkar ton. Destinasyon, deneyim vurgusu. Sahte fiyat/özellik iddiası yasak.",
    "finans": "Finans: Analitik, güven verici, şeffaf ton. Veri + uzmanlık. Yatırım garantisi, getiri vaadi YASAK (SPK).",
    "insaat-gayrimenkul": "İnşaat/GMM: Yatırım odaklı, güvenilir ton. Lokasyon, m², özellik vurgusu. Kesin değer artış vaadi yasak.",
    "otomotiv": "Otomotiv: Güçlü, dinamik ton. Performans, güvenlik, tasarım. Absolut iddia yasak.",
    "genel": "Genel: Markaya özel (brand kit'ten alınır). Sektör-spesifik guidance yok — form alanları yeterli.",
}
```

**2.3** Frontend types dosyasını oluştur: `apps/social/frontend/lib/templates.types.ts` (Bölüm 3.1'deki interface'ler).

**2.4** API client: `apps/social/frontend/lib/api/templates.ts`:

```typescript
import { api } from '@/lib/api'
import type { Template } from '@/lib/templates.types'

export async function fetchTemplates(params?: {
  sector?: string
  contentType?: string
}): Promise<Template[]> {
  const query = new URLSearchParams()
  if (params?.sector) query.set('sector', params.sector)
  if (params?.contentType) query.set('content_type', params.contentType)

  const queryString = query.toString()
  const url = `/templates${queryString ? `?${queryString}` : ''}`

  const response = await api.get(url)
  return response.data?.templates || []
}
```

**2.5** Startup validation ekle — `main.py` lifespan event'inde:

```python
@app.on_event("startup")
async def validate_templates():
    """Validate all templates on startup to catch config errors early."""
    from app.core.templates_data import TEMPLATES, SECTOR_GUIDANCE
    import logging

    logger = logging.getLogger(__name__)
    logger.info(f"Loaded {len(TEMPLATES)} templates")
    logger.info(f"Loaded {len(SECTOR_GUIDANCE)} sector guidance entries")

    assert len(TEMPLATES) == 22, f"Expected 22 templates, got {len(TEMPLATES)}"

    for template_id, template in TEMPLATES.items():
        assert template.id == template_id, f"ID mismatch: {template.id} vs {template_id}"
        assert template.status == "active", f"{template_id} not active"
        assert len(template.sectors) > 0, f"{template_id} has no sectors"
        assert len(template.formFields) > 0, f"{template_id} has no form fields"
```

#### Manuel Adımlar

Yok — tamamen kod değişikliği.

#### Test Senaryoları

**Local smoke test:**
- Backend startup hata vermez
- Startup loglarında "Loaded 22 templates" görünür
- `GET /templates` → 22 şablon döner
- `GET /templates?sector=e-ticaret-perakende` → 4 e-ticaret + 8 genel = 12 şablon
- `GET /templates?sector=saglik` → 3 sağlık + 8 genel = 11 şablon
- `GET /templates?sector=teknoloji` → sadece 8 genel şablon (teknoloji için spesifik yok)

**Canlı test:**

```bash
# 1. Toplam şablon sayısı
curl https://api.otomaix.com/templates | jq '.data.templates | length'
# Beklenen: 22

# 2. Sektör filter
curl 'https://api.otomaix.com/templates?sector=saglik' | jq '.data.templates | length'
# Beklenen: 11 (3 sağlık + 8 genel)

# 3. Tek şablon yapısı
curl 'https://api.otomaix.com/templates?sector=e-ticaret-perakende' | \
  jq '.data.templates[0] | {id, name, formFields: .formFields | length}'
# Beklenen: {id: "eticaret-urun-karti", name: "Ürün Kartı", formFields: 5}
```

#### CLAUDE.md Girdi Template'i

**`backend/CLAUDE.md`:**

```markdown
## YYYY-MM-DD — Phase 7 Sprint 2: 22 şablon + SECTOR_GUIDANCE ✅

**Dosyalar:**
- backend/app/core/templates_data.py (dolduruldu — 22 template + 12 sector guidance)
- backend/app/main.py (değişti — startup template validation eklendi)

**Değişiklikler:**
- 22 şablon tanımlandı: E-Ticaret (4), Yemek (4), Sağlık (3), Prof. Hizmet (3), Genel (8)
- SECTOR_GUIDANCE dict: 12 sektör için içerik rehberi (öncelikli 4 detaylı, diğer 8 generic)
- Startup validation: 22 şablon + ID eşleşmesi + status kontrolü

**Test sonuçları:**
- GET /templates → 22 şablon
- Sektör filter'ları doğru çalışıyor
- Şablon yapısı Pydantic validation'dan geçti

**Sonraki sprint:** Sprint 3 — Prompt building refactor (posts.py)
```

**`frontend/CLAUDE.md`:**

```markdown
## YYYY-MM-DD — Phase 7 Sprint 2: Frontend template types + API client ✅

**Dosyalar:**
- apps/social/frontend/lib/templates.types.ts (YENİ)
- apps/social/frontend/lib/api/templates.ts (YENİ)

**Değişiklikler:**
- TypeScript interface'ler backend Pydantic modellerle birebir uyumlu
- fetchTemplates(sector, contentType) helper fonksiyonu — Sprint 5'te kullanılacak
```

#### Commit Mesajı

```
feat: Phase 7 Sprint 2 — 22 şablon + SECTOR_GUIDANCE + frontend types
```

---

### Sprint 3 — Prompt Building Refactor

**Hedef:** `_build_prompt_with_rag()` fonksiyonunu template-aware hale getir. 3-katmanlı caching uygula. Sektör guidance + şablon guidance enjekte et.

**Tahmini süre:** 1.5 gün

**Ön koşul:** Sprint 2 tamamlandı

#### Dosya Listesi

**YENİ:**
- `backend/app/core/prompt_builder.py` — Prompt building logic ayrı modüle

**DEĞİŞEN:**
- `backend/app/routers/posts.py` — `_build_image_prompt` yeni, legacy korundu
- `backend/app/routers/ai.py` — `SuggestIdeasRequest` template_id/fields aldı

#### Adım Adım Uygulama

**3.1** `backend/app/core/prompt_builder.py` yeni dosyası:

```python
"""Phase 7 — Template-aware prompt builder.

Handles:
- Template guidance injection
- SECTOR_GUIDANCE injection
- Structured form field data
- Platform-specific caption instructions
- RAG document priority
- 3-tier prompt caching (Tier 1 system, Tier 2 brand context, Tier 3 dynamic)
"""

from app.core.templates_data import SECTOR_GUIDANCE
from app.models.templates import Template


# Tier 1 — Static system prompt (cached, same for all calls)
_SYSTEM_RULES = """Sen Turk KOBi'lerine sosyal medya icerigi ureten bir uzmansin.

DIL KURALI (cok onemli): Yanitin tamamen Turkce olmali.
Ingilizce veya yabanci kokenli terimler kullanma. Yaygin Turkce karsiliklari
kullan: 'content creator' yerine 'icerik uretici', 'caption' yerine 'baslik',
'engagement' yerine 'etkilesim', 'story' yerine 'hikaye', 'reel' yerine
'kisa video'. Marka adlari ve platform isimleri orijinal kalabilir.

YASAK: Gerceligi olmayan sayisal iddialar ('%300 artis', '30 saatten 2 saate')
uydurma -- sadece somut ozellik ve faydalardan bahset.

CIKTI FORMATI: Her zaman JSON dondur. Baska aciklama, preamble veya markdown
kullanma.
"""


def build_system_prompt() -> list[dict]:
    """Tier 1 — cached system prompt."""
    return [
        {
            "type": "text",
            "text": _SYSTEM_RULES,
            "cache_control": {"type": "ephemeral"},
        }
    ]


def build_brand_context(
    brand: dict,
    brand_kit: dict,
    template: Template | None,
) -> str:
    """Tier 2 — cached brand + sector + template context.

    This block is reused across calls for the same brand+template combo.
    Cache hit reduces latency and cost significantly.
    """
    parts = []

    # Brand info
    parts.append(f"Marka: {brand.get('name', '')}")
    if brand.get("description"):
        parts.append(f"Marka aciklamasi: {brand['description']}")

    tonality = brand_kit.get("tonality", "professional")
    parts.append(f"Marka tonu: {tonality}")

    colors = brand_kit.get("colors", [])
    if colors:
        colors_str = ", ".join(colors) if isinstance(colors, list) else str(colors)
        parts.append(f"Marka renkleri: {colors_str}")

    hashtags = brand_kit.get("hashtags", [])
    if hashtags:
        parts.append(f"Marka hashtagleri: {', '.join(hashtags[:5])}")

    # Sector guidance (if brand has sector)
    sector_slug = brand.get("sector_slug")
    if sector_slug and sector_slug in SECTOR_GUIDANCE:
        parts.append(f"\n--- SEKTÖR REHBERİ ({sector_slug}) ---")
        parts.append(SECTOR_GUIDANCE[sector_slug])

    # Template guidance
    if template:
        parts.append(f"\n--- ŞABLON TALİMATI ({template.name}) ---")
        parts.append(template.prompt.guidance)

        if template.defaults.suggestedCTAs:
            parts.append(f"Önerilen CTA'lar: {', '.join(template.defaults.suggestedCTAs)}")
        if template.defaults.suggestedHashtags:
            parts.append(f"Önerilen hashtagler: {', '.join(template.defaults.suggestedHashtags)}")

        # Disclaimer (MANDATORY if present)
        if template.defaults.disclaimer:
            parts.append(
                f"\n⚠️ ZORUNLU DISCLAIMER: Caption sonuna bu metni AYNEN ekle:\n"
                f'"{template.defaults.disclaimer}"'
            )

    return "\n".join(parts)


def build_dynamic_content(
    template: Template | None,
    template_fields: dict | None,
    user_prompt: str | None,
    rag_context: str | None,
    platforms: list[str],
) -> str:
    """Tier 3 — dynamic content (not cached)."""
    parts = []

    # Form fields (highest priority per template.prompt.priority)
    if template and template_fields:
        parts.append("=== YAPISAL VERİLER (EN YÜKSEK ÖNCELİK) ===")
        for field in template.formFields:
            value = template_fields.get(field.id)
            if value is not None and value != "":
                suffix = f" {field.suffix}" if field.suffix else ""
                parts.append(f"{field.label}: {value}{suffix}")
        parts.append("=== VERİ SONU ===\n")

    if user_prompt:
        parts.append(f"KULLANICI EK TALIMATI:\n{user_prompt}\n")

    if rag_context:
        parts.append(f"=== REFERANS DOKÜMAN ===\n{rag_context}\n=== DOKÜMAN SONU ===\n")

    if template:
        priority = template.prompt.priority
        parts.append(f"ÖNCELİK SIRASI (çatışma durumunda): {' > '.join(priority)}\n")

    if template and template.platformOverrides and platforms:
        parts.append(build_platform_instructions(template.platformOverrides, platforms))

    return "\n".join(parts)


# ⚠️ NOT (Sprint 6 hotfix — 2026-04-19): Aşağıdaki kod orijinal Sprint 3 spec'i.
# Gerçek implementasyon `PLATFORM_DEFAULTS` + merge mantığını kullanıyor — detay için
# Sprint 6 Hotfix bölümüne bak. Kısaca:
# - overrides `dict | None` olabilir (template yoksa None)
# - Her platform için `_resolve_platform_rules(platform, overrides.get(platform))`
#   çağrılır → PLATFORM_DEFAULTS + override merge sonucu kullanılır
# - `continue` sadece PLATFORM_DEFAULTS'ta olmayan bilinmeyen platformlar için
def build_platform_instructions(
    overrides: dict,
    platforms: list[str],
) -> str:
    """Build per-platform caption rules for Claude."""
    style_map = {
        "long": "200-500 kelime, profesyonel, detayli",
        "medium": "50-150 kelime, emoji kullanilabilir",
        "short": "40-100 karakter, vurucu, hook'lu",
    }

    parts = ["=== PLATFORM-SPESİFİK CAPTION'LAR ==="]
    parts.append(
        "Aşağıdaki her platform için AYRI caption üret. "
        "Response'da JSON formatında `platform_captions` objesi dön, "
        "her platform için ayrı key ile."
    )

    for platform in platforms:
        override = overrides.get(platform)
        if not override:
            continue

        rules = [f"\n{platform}:"]
        if override.captionStyle:
            rules.append(f"  Uzunluk: {style_map.get(override.captionStyle, 'medium')}")
        if override.maxHashtags:
            rules.append(f"  Max hashtag: {override.maxHashtags}")
        if override.useFirstComment:
            rules.append(
                f"  Hashtag'leri CAPTION'DAN AYIR, response'da "
                f"`{platform}.first_comment` key'inde dön"
            )
        if override.toneAdjustment:
            rules.append(f"  Ton ayarlama: {override.toneAdjustment}")
        if override.additionalGuidance:
            rules.append(f"  Ek talimat: {override.additionalGuidance}")

        parts.append("\n".join(rules))

    parts.append("\n=== PLATFORM BİTİŞ ===")
    return "\n".join(parts)
```

**3.2** `posts.py` içinde yeni `_build_image_prompt` fonksiyonu, eski mantık legacy olarak korunsun:

```python
# posts.py içinde:

from app.core.prompt_builder import (
    build_system_prompt,
    build_brand_context,
    build_dynamic_content,
)
from app.core.templates_data import get_template_by_id


async def _build_image_prompt(
    payload: PostGenerate,
    brand: dict,
    brand_kit: dict,
    db,
) -> str:
    """Build fal.ai image prompt.

    Template varsa: payload.image_prompt (caption endpoint'ten gelen) kullanılır.
    Template yoksa: legacy path — eski mantık çalışır.
    """
    if payload.template_id:
        template = get_template_by_id(payload.template_id)
        if not template:
            return payload.prompt or ""

        # Akış C'de caption endpoint image_prompt üretir, payload'a gelir
        if payload.image_prompt:
            return payload.image_prompt

        # Fallback: form_fields'tan basit image prompt inşa et
        parts = [f"{template.name} — sosyal medya görseli"]
        if payload.template_fields:
            for field in template.formFields:
                value = payload.template_fields.get(field.id)
                if value:
                    parts.append(f"{field.label}: {value}")
        return " ".join(parts)

    # Legacy path (no template)
    return await _build_prompt_with_rag_legacy(payload, brand, brand_kit, db)


async def _build_prompt_with_rag_legacy(
    payload: PostGenerate,
    brand: dict,
    brand_kit: dict,
    db,
) -> str:
    """Mevcut _build_prompt_with_rag fonksiyonunun birebir kopyası.

    Template olmayan akışlar için çalışmaya devam eder:
    - Serbest içerik (template_id=None, prompt var)
    - special_day, quote (zaten kendi fonksiyonlarını kullanıyor)
    - /internal/autoposting/trigger (zaten bu path'i kullanmıyor)
    """
    # ... mevcut posts.py:49-106 implementation buraya kopyalanır
    pass
```

**3.3** `generate_post` endpoint'inde prompt oluşturma kısmını güncelle:

```python
# generate_post içinde:

if payload.content_type == "special_day":
    enriched_prompt = _build_special_day_prompt(payload, brand, brand_kit)
elif payload.content_type == "quote":
    enriched_prompt = _build_quote_prompt(payload, dict(brand), brand_kit)
else:
    enriched_prompt = await _build_image_prompt(payload, brand, brand_kit, db)
```

**3.4** `ai.py` içindeki `suggest_ideas` fonksiyonunu template-aware hale getir:

```python
class SuggestIdeasRequest(BaseModel):
    brand_id: UUID
    content_type: str = "image"
    content_category: str = "product"
    prompt: str | None = None
    document_ids: list[UUID] | None = None
    platforms: list[str] | None = None
    count: int = 5
    # Phase 7
    template_id: str | None = None
    template_fields: dict | None = None
```

`suggest_ideas` fonksiyonu içinde:
- `payload.template_id` varsa → template guidance + SECTOR_GUIDANCE Tier 2 cache bloğuna ekle
- `payload.template_id` yoksa → mevcut CATEGORY_GUIDANCE mantığı korunur (backward compat)

#### Manuel Adımlar

Yok — tamamen kod değişikliği.

#### Test Senaryoları

**Local smoke test:**
- `posts.py` import hatası yok, backend başlatılıyor
- Special_day ve quote akışları hala çalışıyor (regresyon testi)
- Template ID olmadan `/posts/generate` → eski akış çalışıyor
- Template ID ile `/posts/generate` (image_prompt boşken) → basit image prompt üretir

**Canlı test — regresyon kontrolü:**

```
1. https://app.otomaix.com/icerik-olustur
2. "Özel Gün" seçeneği ile post üret (eski akış)
3. "Alıntı" seçeneği ile post üret
4. "Görsel" seçeneği + prompt (template olmadan)
5. Hepsi başarılı çalışmalı, hata yok
```

#### CLAUDE.md Girdi Template'i

```markdown
## YYYY-MM-DD — Phase 7 Sprint 3: Prompt building refactor ✅

**Dosyalar:**
- backend/app/core/prompt_builder.py (YENİ)
- backend/app/routers/posts.py (değişti — _build_image_prompt + _build_prompt_with_rag_legacy)
- backend/app/routers/ai.py (değişti — SuggestIdeasRequest template_id/fields aldı)

**Değişiklikler:**
- Prompt building logic ayrı modüle taşındı
- 3-katman structure: system (Tier 1) / brand_context (Tier 2) / dynamic (Tier 3)
- Template guidance + SECTOR_GUIDANCE Tier 2'de — cache hit için optimize
- Disclaimer ZORUNLU injection (sağlık/hukuk şablonlarında)
- Backward compat: _build_prompt_with_rag_legacy korundu

**Test sonuçları:**
- Regresyon: special_day + quote + serbest içerik hala çalışıyor
- Template path şimdilik sadece image prompt üretiyor (caption Sprint 4'te)

**Sonraki sprint:** Sprint 4 — Caption endpoint + Akış C
```

#### Commit Mesajı

```
feat: Phase 7 Sprint 3 — Prompt building refactor (template-aware + 3-tier caching)
```

---

### Sprint 4 — Caption Generation Endpoint + Akış C

**Hedef:** Yeni `POST /posts/generate-caption` endpoint'ini oluştur. Claude'dan platform-spesifik caption'lar al. `POST /posts/generate` endpoint'ini güncelle — caption'ları DB'ye yaz.

**Tahmini süre:** 1.5 gün

**Ön koşul:** Sprint 3 tamamlandı

#### Dosya Listesi

**YENİ:**
- `backend/app/core/caption_generator.py` — Claude çağrısı ve caption parsing

**DEĞİŞEN:**
- `backend/app/routers/posts.py` — Yeni `/posts/generate-caption` endpoint + `generate_post` güncelleme
- `backend/app/models/schemas.py` — `GenerateCaptionRequest`

#### Adım Adım Uygulama

**4.1** `backend/app/core/caption_generator.py` oluştur:

```python
"""Phase 7 — AI caption + image prompt generation.

Called from POST /posts/generate-caption.
Uses Claude with 3-tier prompt caching.

Returns structured response:
{
    "default_caption": "genel caption",
    "platform_captions": {
        "instagram": {"caption": "...", "first_comment": "..."},
        "linkedin": {"caption": "..."}
    },
    "image_prompt": "English image description for fal.ai",
    "hashtags": ["indirim", "kampanya"]
}
"""

import json
import logging
from typing import Any

import anthropic

from app.core.config import settings
from app.core.prompt_builder import (
    build_brand_context,
    build_dynamic_content,
    build_system_prompt,
)
from app.models.templates import Template

logger = logging.getLogger(__name__)


async def generate_captions(
    brand: dict,
    brand_kit: dict,
    template: Template | None,
    template_fields: dict | None,
    user_prompt: str | None,
    rag_context: str | None,
    platforms: list[str],
) -> dict[str, Any]:
    """Generate caption + image prompt + hashtags via Claude."""

    system_prompt = build_system_prompt()
    brand_context = build_brand_context(brand, brand_kit, template)
    dynamic_content = build_dynamic_content(
        template, template_fields, user_prompt, rag_context, platforms
    )

    output_format = _build_output_format_instruction(template, platforms)

    user_content = [
        {
            "type": "text",
            "text": brand_context,
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": dynamic_content + "\n\n" + output_format,
        },
    ]

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    try:
        message = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=2048,
            temperature=1.0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_content}],
        )

        # Log cache stats
        if hasattr(message, "usage"):
            cache_read = getattr(message.usage, "cache_read_input_tokens", 0)
            cache_create = getattr(message.usage, "cache_creation_input_tokens", 0)
            logger.info(
                f"Caption gen cache: read={cache_read}, create={cache_create}, "
                f"template={template.id if template else None}"
            )

        raw = message.content[0].text.strip()

        # Strip markdown code blocks
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        data = json.loads(raw)

        # Validate and fill missing fields
        data.setdefault("default_caption", "")
        data.setdefault("platform_captions", {})
        data.setdefault("image_prompt", "")
        data.setdefault("hashtags", [])

        # Append disclaimer if template has one
        if template and template.defaults.disclaimer:
            disclaimer = template.defaults.disclaimer
            if not data["default_caption"].endswith(disclaimer):
                data["default_caption"] += f"\n\n{disclaimer}"
            for platform, pcaption in data["platform_captions"].items():
                if isinstance(pcaption, dict) and "caption" in pcaption:
                    if not pcaption["caption"].endswith(disclaimer):
                        pcaption["caption"] += f"\n\n{disclaimer}"

        return data

    except Exception as e:
        logger.error(f"Caption generation failed: {e}", exc_info=True)
        return {
            "default_caption": user_prompt or "",
            "platform_captions": {p: {"caption": user_prompt or ""} for p in platforms},
            "image_prompt": user_prompt or "social media post image",
            "hashtags": [],
            "error": str(e),
        }


def _build_output_format_instruction(
    template: Template | None,
    platforms: list[str],
) -> str:
    """Instruct Claude on exact JSON output format."""

    has_platform_overrides = (
        template is not None
        and template.platformOverrides is not None
        and len(platforms) > 0
    )

    if has_platform_overrides:
        platform_schema = ", ".join([
            f'"{p}": {{"caption": "...", "first_comment": "..." (only if useFirstComment)}}'
            for p in platforms
        ])
    else:
        platform_schema = ", ".join([
            f'"{p}": {{"caption": "..."}}' for p in platforms
        ])

    return f"""ÇIKTI FORMATI (SADECE JSON, BAŞKA HİÇBİR ŞEY YAZMA):

{{
  "default_caption": "Genel caption — fallback olarak kullanılır",
  "platform_captions": {{
    {platform_schema}
  }},
  "image_prompt": "English visual description for image AI (fal.ai FLUX.2 Pro)",
  "hashtags": ["hashtag1", "hashtag2"]
}}

ÖNEMLİ: image_prompt İngilizce yazılmalı (AI model İngilizce prompt anlıyor).
Caption'lar ve hashtag'ler Türkçe olmalı.
"""
```

**4.2** `posts.py` içinde yeni endpoint:

```python
from pydantic import BaseModel


class GenerateCaptionRequest(BaseModel):
    brand_id: UUID
    template_id: str | None = None
    template_fields: dict | None = None
    user_prompt: str | None = None
    document_ids: list[UUID] = []
    platforms: list[str] = []


@router.post(
    "/generate-caption",
    response_model=OkResponse,
    dependencies=[Depends(limiter(30, 3600))],  # 30/saat
)
async def generate_caption(
    payload: GenerateCaptionRequest,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Generate AI caption + image_prompt + hashtags (Part of Akış C)."""
    from app.core.caption_generator import generate_captions
    from app.core.templates_data import get_template_by_id
    from app.services.document_processor import get_document_context

    await assert_brand_owned(db, user, payload.brand_id)

    brand = await db.fetchrow(
        """
        SELECT b.*, s.slug as sector_slug
        FROM social.brands b
        LEFT JOIN social.sectors s ON b.sector_id = s.id
        WHERE b.id = $1
        """,
        payload.brand_id,
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand_kit = _parse_brand_kit(brand["brand_kit"])

    template = None
    if payload.template_id:
        template = get_template_by_id(payload.template_id)
        if not template:
            raise HTTPException(
                status_code=400,
                detail=f"Template {payload.template_id} not found",
            )

    rag_context = None
    if payload.document_ids:
        base_query = payload.user_prompt or (
            template.name if template else "social media caption"
        )
        rag_context = await get_document_context(payload.document_ids, base_query, db)

    result = await generate_captions(
        brand=dict(brand),
        brand_kit=brand_kit,
        template=template,
        template_fields=payload.template_fields,
        user_prompt=payload.user_prompt,
        rag_context=rag_context,
        platforms=payload.platforms,
    )

    return OkResponse(data=result)
```

**4.3** `generate_post` endpoint'ini güncelle — caption'lar payload'ta varsa post kaydına yaz:

```python
@router.post("/generate", response_model=OkResponse, status_code=status.HTTP_201_CREATED)
async def generate_post(
    payload: PostGenerate,
    user: dict = Depends(get_current_user),
    db: asyncpg.Connection = Depends(get_db),
):
    """Create post + trigger fal.ai image generation."""
    await assert_brand_owned(db, user, payload.brand_id)
    await check_plan_limit(user["sub"], "post", db)

    brand = await db.fetchrow(
        """
        SELECT b.*, s.slug as sector_slug
        FROM social.brands b
        LEFT JOIN social.sectors s ON b.sector_id = s.id
        WHERE b.id = $1
        """,
        payload.brand_id,
    )
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")

    brand_kit = _parse_brand_kit(brand["brand_kit"])

    # Build image prompt
    if payload.content_type == "special_day":
        image_prompt = _build_special_day_prompt(payload, brand, brand_kit)
        default_caption = None
    elif payload.content_type == "quote":
        image_prompt = _build_quote_prompt(payload, dict(brand), brand_kit)
        author_part = f"\n\n-- {payload.quote_author}" if payload.quote_author else ""
        default_caption = f'"{payload.quote_text}"{author_part}' if payload.quote_text else None
    elif payload.template_id and payload.image_prompt:
        # Akış C — caption endpoint already gave us image_prompt
        image_prompt = payload.image_prompt
        default_caption = None
    else:
        # Legacy path
        image_prompt = await _build_prompt_with_rag_legacy(payload, brand, brand_kit, db)
        default_caption = None

    # Build caption + hashtags fields (backward compat)
    caption = None
    hashtags = None
    if payload.platform_captions:
        # Use default or first available platform caption
        pc = payload.platform_captions
        caption = pc.get("default") or default_caption
        if not caption and pc.get("platforms"):
            first_platform = next(iter(pc["platforms"].values()))
            if isinstance(first_platform, dict):
                caption = first_platform.get("caption")

        # Collect unique hashtags
        hashtag_set = set()
        for platform_data in (pc.get("platforms") or {}).values():
            if isinstance(platform_data, dict):
                for h in platform_data.get("hashtags", []):
                    hashtag_set.add(h)
        hashtags = list(hashtag_set) if hashtag_set else None
    elif default_caption:
        caption = default_caption

    row = await db.fetchrow(
        """
        INSERT INTO social.posts
            (brand_id, content_type, content_category, prompt, user_text,
             document_ids, aspect_ratio, platforms, status,
             template_id, template_fields, platform_captions,
             caption, hashtags)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'generating',
                $9, $10, $11, $12, $13)
        RETURNING *
        """,
        payload.brand_id,
        payload.content_type,
        payload.content_category,
        payload.prompt or payload.special_day_name or payload.quote_text,
        payload.user_text,
        [str(d) for d in payload.document_ids] if payload.document_ids else None,
        payload.aspect_ratio,
        payload.platforms,
        payload.template_id,
        payload.template_fields,
        payload.platform_captions,
        caption,
        hashtags,
    )
    post = dict(row)

    # Trigger fal.ai
    try:
        fal_job_id = await generate_image(image_prompt, payload.aspect_ratio, brand_kit)
        await db.execute(
            "UPDATE social.posts SET fal_job_id = $2 WHERE id = $1",
            post["id"],
            fal_job_id,
        )
        post["fal_job_id"] = fal_job_id
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(
            f"fal.ai generate_image failed for post {post['id']}: {e}",
            exc_info=True,
        )

    return OkResponse(data={
        "post_id": str(post["id"]),
        "status": "generating",
        "caption": caption,
    })
```

#### Manuel Adımlar

Yok.

#### Test Senaryoları

**Local smoke test:**
1. Caption endpoint → boş template field'larla çağır → generic caption döner
2. Caption endpoint → E-Ticaret Ürün Kartı + dolu fields → 3 platform için 3 farklı caption
3. Caption endpoint → Sağlık şablonu → caption sonunda disclaimer var
4. Caption endpoint → invalid template_id → 400 hatası
5. Generate endpoint → `platform_captions` ile çağır → DB'ye JSONB olarak saklandı

**Canlı test:**

```bash
# 1. Caption generation
curl -X POST https://api.otomaix.com/posts/generate-caption \
  -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{
    "brand_id": "<brand_uuid>",
    "template_id": "eticaret-urun-karti",
    "template_fields": {
      "product_name": "iPhone 15 Pro",
      "price": 64999,
      "old_price": 74999
    },
    "platforms": ["instagram", "linkedin"]
  }'

# Beklenen:
# - default_caption: Türkçe orta uzunluk
# - platform_captions.instagram.caption: medium, emoji'li
# - platform_captions.instagram.first_comment: hashtag'ler (useFirstComment)
# - platform_captions.linkedin.caption: long, profesyonel
# - image_prompt: İngilizce, ürün odaklı
# - hashtags: ["indirim", "kampanya", ...]

# 2. Sağlık disclaimer kontrolü
# template_id=saglik-biliyor-muydunuz
# Beklenen: default_caption ve platform_captions'ın sonunda:
# "Bu içerik genel bilgilendirme amaçlıdır ve tıbbi tavsiye yerine geçmez..."

# 3. Cache kontrolü (ikinci çağrı)
# Aynı brand + aynı template ile tekrar çağır
# Backend log'larda cache_read_input_tokens > 0 görünmeli
```

#### CLAUDE.md Girdi Template'i

```markdown
## YYYY-MM-DD — Phase 7 Sprint 4: Caption endpoint + Akış C ✅

**Dosyalar:**
- backend/app/core/caption_generator.py (YENİ — Claude caption generation)
- backend/app/routers/posts.py (değişti — /generate-caption + /generate)
- backend/app/models/schemas.py (değişti — GenerateCaptionRequest)

**Değişiklikler:**
- POST /posts/generate-caption endpoint: Claude → platform_captions + image_prompt + hashtags
- 3-katman caching: system (Tier 1) + brand+sector+template (Tier 2) + dynamic (Tier 3)
- Disclaimer otomatik injection (template.defaults.disclaimer varsa)
- Platform-spesifik caption rules: useFirstComment, captionStyle, maxHashtags
- POST /posts/generate: payload.platform_captions varsa DB'ye JSONB olarak yazar
- Cache logging: cache_read_input_tokens + cache_creation_input_tokens

**Test sonuçları:**
- Template-lı caption: 3 platforma 3 farklı caption çıkıyor
- Sağlık disclaimer otomatik ekleniyor
- Cache hit ikinci çağrıda görülüyor (cache_read > 0)
- Akış C tamamlandı: caption endpoint + generate endpoint arka arkaya çalışıyor

**Sonraki sprint:** Sprint 5 — Frontend wizard refactor
```

#### Commit Mesajı

```
feat: Phase 7 Sprint 4 — Caption endpoint + Akış C (AI caption + image_prompt + hashtags)
```

---

### Sprint 5 — Frontend Wizard Refactor

**Hedef:** `/icerik-olustur` sayfasını yeniden yapılandır. Template grid, dynamic form, Akış C UX ekle.

**Tahmini süre:** 1.5-2 gün (en karmaşık sprint)

**Ön koşul:** Sprint 4 tamamlandı

#### Dosya Listesi

**DEĞİŞEN:**
- `apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx` — Ana wizard refactor
- `apps/social/frontend/lib/store.ts` — Brand interface `sector_slug` eklendi
- `apps/social/frontend/lib/analytics.ts` — Template event'leri

**YENİ:**
- `apps/social/frontend/components/templates/TemplateGrid.tsx`
- `apps/social/frontend/components/templates/TemplateCard.tsx`
- `apps/social/frontend/components/templates/DynamicForm.tsx`
- `apps/social/frontend/components/templates/CaptionEditor.tsx`

#### Adım Adım Uygulama

**5.1** `store.ts` Brand interface'i güncelle:

```typescript
export interface Brand {
  id: string
  name: string
  sector?: string | null
  sector_slug?: string | null            // Phase 7
  sector_display_name?: string | null    // Phase 7
  logo_light_url?: string | null
  logo_dark_url?: string | null
  is_active?: boolean
}
```

**5.2** `lib/analytics.ts`'e template event'leri ekle:

```typescript
export const analytics = {
  // ... existing events ...

  templateSelected: (props: { template_id: string; sector_slug: string; content_type: string }) => {
    track('template_selected', props)
  },
  templateFormSubmitted: (props: { template_id: string; fields_filled: string[] }) => {
    track('template_form_submitted', props)
  },
  templateCaptionGenerated: (props: { template_id: string; platforms: string[] }) => {
    track('template_caption_generated', props)
  },
  templateCaptionEdited: (props: { template_id: string; platform_edited: string }) => {
    track('template_caption_edited', props)
  },
  templateImageGenerated: (props: { template_id: string; post_id: string }) => {
    track('template_image_generated', props)
  },
  templateAbandoned: (props: { template_id: string; step: 'form' | 'caption' | 'image' | 'publish' }) => {
    track('template_abandoned', props)
  },
}
```

**5.3** Template grid component: `components/templates/TemplateGrid.tsx`

```typescript
'use client'

import { useMemo } from 'react'
import { TemplateCard } from './TemplateCard'
import type { Template } from '@/lib/templates.types'

interface Props {
  templates: Template[]
  selectedId: string | null
  onSelect: (templateId: string) => void
  onFreeFormSelect: () => void
  brandSectorSlug: string | null
}

export function TemplateGrid({
  templates, selectedId, onSelect, onFreeFormSelect, brandSectorSlug
}: Props) {
  const { sectorTemplates, generalTemplates } = useMemo(() => {
    const sector: Template[] = []
    const general: Template[] = []

    for (const t of templates) {
      if (t.sectors.includes('*')) {
        general.push(t)
      } else {
        sector.push(t)
      }
    }

    return { sectorTemplates: sector, generalTemplates: general }
  }, [templates])

  return (
    <div className="space-y-6">
      {sectorTemplates.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-3">
            Sektörünüze özel şablonlar
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {sectorTemplates.map(t => (
              <TemplateCard
                key={t.id}
                template={t}
                selected={selectedId === t.id}
                onClick={() => onSelect(t.id)}
              />
            ))}
          </div>
        </div>
      )}

      {generalTemplates.length > 0 && (
        <div>
          <h3 className="text-sm font-medium text-gray-500 mb-3">
            Genel şablonlar
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {generalTemplates.map(t => (
              <TemplateCard
                key={t.id}
                template={t}
                selected={selectedId === t.id}
                onClick={() => onSelect(t.id)}
              />
            ))}
          </div>
        </div>
      )}

      <div className="pt-4 border-t border-gray-200">
        <button
          onClick={onFreeFormSelect}
          className="text-sm text-blue-600 hover:text-blue-700 hover:underline"
        >
          Uygun şablon yok mu? Serbest içerikle devam et →
        </button>
      </div>
    </div>
  )
}
```

**5.4** TemplateCard: `components/templates/TemplateCard.tsx`

```typescript
import type { Template } from '@/lib/templates.types'
import { cn } from '@/lib/utils'

interface Props {
  template: Template
  selected: boolean
  onClick: () => void
}

export function TemplateCard({ template, selected, onClick }: Props) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'p-4 rounded-lg border text-left transition-all',
        'hover:border-blue-400 hover:bg-blue-50/30',
        selected
          ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-500/20'
          : 'border-gray-200 bg-white'
      )}
    >
      <div className="text-2xl mb-2">{template.icon}</div>
      <div className={cn(
        'text-sm font-medium mb-1',
        selected ? 'text-blue-900' : 'text-gray-900'
      )}>
        {template.name}
      </div>
      <div className="text-xs text-gray-500 line-clamp-2">
        {template.description}
      </div>
    </button>
  )
}
```

**5.5** DynamicForm: `components/templates/DynamicForm.tsx`

```typescript
'use client'

import { useMemo } from 'react'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import type { Template, TemplateFormField } from '@/lib/templates.types'

interface Props {
  template: Template
  values: Record<string, string | number>
  onChange: (fieldId: string, value: string | number) => void
}

export function DynamicForm({ template, values, onChange }: Props) {
  const grouped = useMemo(() => {
    const groups = new Map<string, TemplateFormField[]>()
    for (const field of template.formFields) {
      const g = field.group || '_default'
      if (!groups.has(g)) groups.set(g, [])
      groups.get(g)!.push(field)
    }
    return Array.from(groups.entries())
  }, [template])

  return (
    <div className="space-y-6">
      {grouped.map(([groupName, fields]) => (
        <div key={groupName}>
          {groupName !== '_default' && (
            <h4 className="text-sm font-medium text-gray-700 mb-3">{groupName}</h4>
          )}
          <div className="space-y-3">
            {fields.map(field => (
              <FormField
                key={field.id}
                field={field}
                value={values[field.id]}
                onChange={(v) => onChange(field.id, v)}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  )
}

function FormField({
  field, value, onChange
}: {
  field: TemplateFormField
  value: string | number | undefined
  onChange: (v: string | number) => void
}) {
  const renderInput = () => {
    switch (field.type) {
      case 'textarea':
        return (
          <Textarea
            value={value as string || ''}
            onChange={(e) => onChange(e.target.value)}
            placeholder={field.placeholder}
            maxLength={field.validation?.maxLength}
            required={field.required}
          />
        )

      case 'number':
        return (
          <div className="relative">
            <Input
              type="number"
              value={value as number || ''}
              onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
              placeholder={field.placeholder}
              min={field.validation?.min}
              max={field.validation?.max}
              required={field.required}
            />
            {field.suffix && (
              <span className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-gray-500">
                {field.suffix}
              </span>
            )}
          </div>
        )

      case 'select':
        return (
          <select
            value={value as string || field.defaultValue as string || ''}
            onChange={(e) => onChange(e.target.value)}
            required={field.required}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          >
            {!field.required && <option value="">-- Seçiniz --</option>}
            {field.options?.map(opt => (
              <option key={opt.value} value={opt.value}>{opt.label}</option>
            ))}
          </select>
        )

      default:
        return (
          <Input
            type="text"
            value={value as string || ''}
            onChange={(e) => onChange(e.target.value)}
            placeholder={field.placeholder}
            maxLength={field.validation?.maxLength}
            required={field.required}
          />
        )
    }
  }

  return (
    <div>
      <Label className="text-sm">
        {field.label}
        {field.required && <span className="text-red-500 ml-1">*</span>}
      </Label>
      {renderInput()}
      {field.helpText && (
        <p className="text-xs text-gray-500 mt-1">{field.helpText}</p>
      )}
    </div>
  )
}
```

**5.6** CaptionEditor: `components/templates/CaptionEditor.tsx`

```typescript
'use client'

import { useState } from 'react'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'

interface PlatformCaption {
  caption: string
  first_comment?: string
}

interface Props {
  defaultCaption: string
  platformCaptions: Record<string, PlatformCaption>
  platforms: string[]
  onChange: (captions: { default: string; platforms: Record<string, PlatformCaption> }) => void
  onConfirm: () => void
  onRegenerate: () => void
}

export function CaptionEditor({
  defaultCaption, platformCaptions, platforms, onChange, onConfirm, onRegenerate
}: Props) {
  const [activeTab, setActiveTab] = useState<string>('default')
  const [local, setLocal] = useState({
    default: defaultCaption,
    platforms: platformCaptions,
  })

  const updateCaption = (platform: string, value: string) => {
    const newLocal = { ...local }
    if (platform === 'default') {
      newLocal.default = value
    } else {
      newLocal.platforms = {
        ...local.platforms,
        [platform]: { ...local.platforms[platform], caption: value },
      }
    }
    setLocal(newLocal)
    onChange(newLocal)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Caption önizleme</h3>
        <Button variant="ghost" size="sm" onClick={onRegenerate}>
          Yeniden üret
        </Button>
      </div>

      {/* Platform tabs */}
      <div className="flex gap-2 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('default')}
          className={activeTab === 'default'
            ? 'border-b-2 border-blue-500 px-3 py-2 text-sm'
            : 'px-3 py-2 text-sm text-gray-500'}
        >
          Varsayılan
        </button>
        {platforms.map(p => (
          <button
            key={p}
            onClick={() => setActiveTab(p)}
            className={activeTab === p
              ? 'border-b-2 border-blue-500 px-3 py-2 text-sm'
              : 'px-3 py-2 text-sm text-gray-500'}
          >
            {p.charAt(0).toUpperCase() + p.slice(1)}
          </button>
        ))}
      </div>

      <Textarea
        value={
          activeTab === 'default'
            ? local.default
            : local.platforms[activeTab]?.caption || ''
        }
        onChange={(e) => updateCaption(activeTab, e.target.value)}
        rows={8}
        className="font-sans"
      />

      {activeTab !== 'default' && local.platforms[activeTab]?.first_comment !== undefined && (
        <div>
          <Label className="text-xs text-gray-500">İlk yorum (hashtag'ler için)</Label>
          <Textarea
            value={local.platforms[activeTab].first_comment || ''}
            onChange={(e) => {
              const newLocal = { ...local }
              newLocal.platforms[activeTab] = {
                ...newLocal.platforms[activeTab],
                first_comment: e.target.value,
              }
              setLocal(newLocal)
              onChange(newLocal)
            }}
            rows={3}
            className="font-sans text-sm"
          />
        </div>
      )}

      <div className="flex justify-end pt-4">
        <Button onClick={onConfirm}>
          Görseli üret →
        </Button>
      </div>
    </div>
  )
}
```

**5.7** Ana sayfa refactor — `page.tsx` büyük değişiklik:

- `CONTENT_CATEGORIES` constant kaldırılır
- `category` state kaldırılır
- Yeni state: `selectedTemplate: Template | null`, `templateFields: Record<string, any>`, `captionData: CaptionResponse | null`, `mode: 'template' | 'free-form' | null`, `phase: 'form' | 'caption' | 'image'`
- Step 1: İçerik tipi seçimi — aynı kalır, `image` dışındakilerde eski davranış korunur
- Step 2: `image` için yeni akış:
  - Template grid → template seç
  - Dynamic form → fields doldur
  - [Önizle] → `POST /posts/generate-caption`
  - CaptionEditor → düzenle → [Görseli üret]
  - `POST /posts/generate` → önizleme sayfası
- Step 2: `carousel`, `video`, `special_day`, `quote` için eski akış korunur

Bu büyük bir component refactoru. Kodda test-as-you-go yaklaşımı kullan, her alt parçayı ayrı test et.

Önemli kod pattern'leri:

```typescript
// Template fetch (session'da bir kez)
const [templates, setTemplates] = useState<Template[]>([])
useEffect(() => {
  if (!currentBrand?.sector_slug) return
  fetchTemplates({ sector: currentBrand.sector_slug, contentType: 'image' })
    .then(setTemplates)
}, [currentBrand?.sector_slug])

// Template seçimi
const handleTemplateSelect = (templateId: string) => {
  const t = templates.find(x => x.id === templateId)
  if (!t) return
  setSelectedTemplate(t)
  setTemplateFields({})
  setMode('template')
  analytics.templateSelected({
    template_id: templateId,
    sector_slug: currentBrand?.sector_slug || '',
    content_type: 'image',
  })
  // Aspect ratio suggestion uygula
  if (t.output.aspectRatioSuggestion) {
    setAspectRatio(t.output.aspectRatioSuggestion)
  }
}

// Caption generation
const handleFormSubmit = async () => {
  if (!selectedTemplate) return
  setGeneratingCaption(true)
  try {
    const response = await api.post('/posts/generate-caption', {
      brand_id: currentBrand?.id,
      template_id: selectedTemplate.id,
      template_fields: templateFields,
      document_ids: selectedDocIds,
      platforms,
    })
    setCaptionData(response.data)
    setPhase('caption')
    analytics.templateCaptionGenerated({
      template_id: selectedTemplate.id,
      platforms,
    })
  } catch (err) {
    toast.error('Caption üretilemedi')
  } finally {
    setGeneratingCaption(false)
  }
}

// Image generation (after caption approved)
const handleImageGenerate = async () => {
  if (!captionData) return
  setGenerating(true)
  try {
    const response = await api.post('/posts/generate', {
      brand_id: currentBrand?.id,
      content_type: 'image',
      template_id: selectedTemplate?.id,
      template_fields: templateFields,
      platform_captions: editedCaptions,  // user-edited
      image_prompt: captionData.image_prompt,
      aspect_ratio: aspectRatio,
      platforms,
    })
    setGeneratedPost(response.data)
    setPhase('image')
    analytics.templateImageGenerated({
      template_id: selectedTemplate?.id || '',
      post_id: response.data.post_id,
    })
    // Polling başlasın görsel için
  } catch (err) {
    toast.error('Görsel üretilemedi')
  } finally {
    setGenerating(false)
  }
}
```

#### Manuel Adımlar

Yok.

#### Test Senaryoları

**Local smoke test:**
1. E-Ticaret brand ile `/icerik-olustur` aç
2. Görsel seç → 4 e-ticaret + 8 genel şablon (12 total)
3. Teknoloji brand ile aç → sadece 8 genel şablon
4. Sağlık brand ile Biliyor Muydunuz seç → form alanları render
5. Alanları doldur → [Önizle] → caption preview → içinde disclaimer var mı?
6. Platform tab'larında farklı caption'lar göründü mü?
7. Caption düzenle → [Görseli üret] → generate API çağrıldı mı?
8. Serbest içerik → eski akış çalışıyor mu?
9. Carousel/Video/Özel Gün/Alıntı → eski akış bozulmadı mı?

**Canlı test:**

```
1. app.otomaix.com/icerik-olustur aç
2. Her öncelikli sektör markasıyla test (E-Ticaret, Yemek, Sağlık, Prof. Hizmet):
   - Şablon grid'i doğru filtrelendi mi?
   - Form alanları doğru render?
   - Caption generation çalışıyor mu?
   - Platform tab'ları farklı caption gösteriyor mu?
3. Genel sektör markalarıyla test (Teknoloji, Moda, vs.):
   - 8 genel şablon mu görünüyor?
   - Akış sonuna kadar çalışıyor mu?
4. Regresyon testleri:
   - Özel Gün akışı eski gibi çalışıyor
   - Alıntı akışı eski gibi çalışıyor
   - Video (faceless) eski gibi çalışıyor
   - Serbest içerik akışı eski gibi çalışıyor
```

#### CLAUDE.md Girdi Template'i

```markdown
## YYYY-MM-DD — Phase 7 Sprint 5: Frontend wizard refactor ✅

**Dosyalar:**
- apps/social/frontend/app/(dashboard)/icerik-olustur/page.tsx (büyük refactor)
- apps/social/frontend/lib/store.ts (değişti — Brand.sector_slug)
- apps/social/frontend/lib/analytics.ts (değişti — 6 template event)
- apps/social/frontend/components/templates/TemplateGrid.tsx (YENİ)
- apps/social/frontend/components/templates/TemplateCard.tsx (YENİ)
- apps/social/frontend/components/templates/DynamicForm.tsx (YENİ)
- apps/social/frontend/components/templates/CaptionEditor.tsx (YENİ)

**Değişiklikler:**
- 3 kategori butonu (Ürün/Hizmet/Kurumsal) kaldırıldı
- Template grid: sektör-specific + genel şablonlar ayrı bölümlerde
- Dynamic form: formFields.group'a göre grup render
- Akış C: form → caption preview → caption edit → image generate
- Platform tab'ları: her platforma özel caption düzenlenebilir
- "Serbest İçerik" link'i alt kısımda, şablonsuz akış devam ediyor

**Test sonuçları:**
- E-Ticaret/Sağlık/Prof. Hizmet/Yemek: şablon filter doğru
- Teknoloji ve diğer sektörler: sadece 8 genel şablon
- Akış C tam çalışıyor: form → caption → edit → image → publish
- Regresyon: özel gün/alıntı/video/serbest içerik bozulmadı

**Sonraki sprint:** Sprint 6 — Platform-spesifik publishing
```

#### Commit Mesajı

```
feat: Phase 7 Sprint 5 — Frontend wizard refactor (template grid + dynamic form + Akış C)
```

---

### Sprint 6 — Platform-Spesifik Publishing

**Hedef:** `upload_post.py`'deki `publish_post` fonksiyonunu `posts.platform_captions` JSONB kolonunu okuyup her platforma özel caption göndermek için güncelle.

**Tahmini süre:** 0.5-1 gün

**Ön koşul:** Sprint 4 tamamlandı (Sprint 5 paralel olabilir)

#### Dosya Listesi

**DEĞİŞEN:**
- `backend/app/services/upload_post.py` — `publish_post` + `_publish_single_platform` güncelleme

#### Adım Adım Uygulama

**6.1** `_publish_single_platform` fonksiyonuna `first_comment` parametresi ekle:

```python
async def _publish_single_platform(
    *,
    db: asyncpg.Connection,
    post_id: UUID,
    platform: str,
    username: str,
    is_video: bool,
    media_bytes: bytes,
    media_mime: str,
    filename: str,
    title_text: str,
    first_comment: str | None = None,  # Phase 7 — IG/FB first comment
) -> dict:
    # ... existing validation and DB upsert ...

    form_data = [
        ("user", (None, username)),
        ("title", (None, title_text[:2200])),
        ("platform[]", (None, platform)),
    ]

    # Phase 7 — First comment for supported platforms
    if first_comment and platform in ("instagram", "facebook", "threads"):
        form_data.append((f"{platform}_first_comment", (None, first_comment[:500])))

    if is_video:
        form_data.append(("video", (filename, media_bytes, media_mime)))
        endpoint = f"{BASE_URL}/upload"
    else:
        form_data.append(("photos[]", (filename, media_bytes, media_mime)))
        endpoint = f"{BASE_URL}/upload_photos"

    # ... rest of existing logic (DB updates, response handling) ...
```

**6.2** `publish_post` fonksiyonunu güncelle:

```python
async def publish_post(
    post_id: UUID,
    db: asyncpg.Connection,
    only_platforms: list[str] | None = None,
) -> dict:
    # ... existing validation and setup ...

    # Phase 7 — per-platform captions
    platform_captions_raw = post["platform_captions"]
    if platform_captions_raw and isinstance(platform_captions_raw, str):
        import json as _json
        platform_captions_raw = _json.loads(platform_captions_raw)
    platform_captions = platform_captions_raw or {}

    # Fallback caption (Phase 7'den önce veya template'siz postlar için)
    legacy_caption = post["caption"] or ""
    legacy_hashtags = post["hashtags"] or []
    legacy_title = legacy_caption + (
        " " + " ".join(f"#{h.lstrip('#')}" for h in legacy_hashtags)
        if legacy_hashtags else ""
    )

    # ... download media etc ...

    results = []
    for platform in platforms_to_publish:
        # Phase 7 — platform-spesifik caption varsa onu kullan
        platform_data = platform_captions.get("platforms", {}).get(platform) if platform_captions else None

        if platform_data and isinstance(platform_data, dict) and platform_data.get("caption"):
            title_text = platform_data["caption"]
            first_comment = platform_data.get("first_comment")
        else:
            # Legacy fallback
            title_text = legacy_title
            first_comment = None

        res = await _publish_single_platform(
            db=db,
            post_id=post_id,
            platform=platform,
            username=username,
            is_video=is_video,
            media_bytes=media_bytes,
            media_mime=media_mime,
            filename=filename,
            title_text=title_text,
            first_comment=first_comment,  # Phase 7
        )
        results.append(res)

    # ... rest of existing logic ...
```

#### Manuel Adımlar

Yok.

#### Test Senaryoları

**Local test:**
1. Template'den post oluştur (Sprint 5 akışı) → platform_captions JSONB dolu
2. Post'u publish et → her platforma farklı caption gitmeli
3. Log'larda Upload-Post API request'leri incele:
   - Instagram request: `title` = IG caption, `instagram_first_comment` = hashtag'ler
   - LinkedIn request: `title` = LI caption (farklı, daha uzun)
4. Eski post (template_id=NULL, platform_captions=NULL) publish et → legacy caption mantığı çalışmalı

**Canlı test:**

```
1. Template ile post oluştur (Akış C): E-Ticaret Ürün Kartı
2. Caption'ları gözden geçir: IG, LinkedIn için farklı
3. Yayınla
4. Gerçek platformları kontrol et:
   - Instagram'da IG-specific caption görünüyor mu?
   - LinkedIn'de LI-specific caption görünüyor mu?
   - IG first comment'i: hashtag'ler orada mı?
5. Eski post (template'siz) yayınla → legacy davranış
```

**ÖNEMLİ NOT:** `{platform}_first_comment` parametresi Upload-Post'ta destekleniyor ama Phase 7 öncesi hiç test edilmemişti. Bu sprint'te **mutlaka canlıda doğrula** — eğer çalışmıyorsa alternatif çözüm: `first_comment` içeriğini caption sonuna ekleyerek platform-specific caption'a dahil et.

#### CLAUDE.md Girdi Template'i

```markdown
## YYYY-MM-DD — Phase 7 Sprint 6: Platform-spesifik publishing ✅

**Dosyalar:**
- backend/app/services/upload_post.py (değişti — publish_post + _publish_single_platform)

**Değişiklikler:**
- `_publish_single_platform`: first_comment parametresi eklendi (IG/FB/Threads)
- `publish_post`: post.platform_captions JSONB okunuyor, her platforma özel title
- Backward compat: platform_captions NULL ise legacy caption+hashtags mantığı

**Test sonuçları:**
- Template'li post: IG, LinkedIn, Twitter'a farklı caption gitti
- IG first comment: hashtag'ler doğru yere gitti
- Template'siz post: legacy akış bozulmadı

**Sonraki sprint:** Sprint 7 — Test & cleanup
```

#### Commit Mesajı

```
feat: Phase 7 Sprint 6 — Platform-spesifik publishing (Upload-Post per-platform captions)
```

---

#### Sprint 6 Hotfix — PLATFORM_DEFAULTS (2026-04-19, commit `b35a3ac`) ✅

**Bulunan sorun (canlı test sonrası):** Ürün Kartı (`eticaret-urun-karti`) şablonu + 6 platform (IG, TikTok, LI, Twitter, FB, YouTube) ile caption üretildiğinde **TikTok, Facebook, YouTube sekmeleri boş** geldi. Claude yalnızca şablonun `platformOverrides` dict'inde tanımlı 3 platform (IG/LI/TW) için caption üretiyor, diğerlerini atlıyordu.

**Kök neden:** `prompt_builder.py:build_platform_instructions()` satır 1314'teki kod (bu dokümanın spec kısmı) `if not override: continue` ile şablonda override olmayan platformlar için Claude'a hiç kural göndermiyordu. 22 şablonun büyük çoğunluğu çoğu platform için `platformOverrides` tanımlamıyordu (özellikle TikTok/Threads/Bluesky hiçbir şablonda yoktu).

**Çözüm (Seçenek D — merkezi PLATFORM_DEFAULTS):** `prompt_builder.py`'ye 9 platform için varsayılan caption kuralları eklendi. Template-level `platformOverrides` bu default'ların üzerine alan bazında merge edilir (sadece `None` olmayan alanlar override eder).

```python
# app/core/prompt_builder.py
PLATFORM_DEFAULTS: dict[str, dict] = {
    "instagram": {"captionStyle": "medium", "maxHashtags": 15, "useFirstComment": True},
    "linkedin":  {"captionStyle": "long",   "maxHashtags": 5,  "useFirstComment": False},
    "twitter":   {"captionStyle": "short",  "maxHashtags": 2,  "useFirstComment": False},
    "facebook":  {"captionStyle": "medium", "maxHashtags": 5,  "useFirstComment": True},
    "tiktok":    {"captionStyle": "short",  "maxHashtags": 5,  "useFirstComment": False},
    "youtube":   {"captionStyle": "medium", "maxHashtags": 8,  "useFirstComment": False},
    "threads":   {"captionStyle": "short",  "maxHashtags": 5,  "useFirstComment": True},
    "pinterest": {"captionStyle": "medium", "maxHashtags": 10, "useFirstComment": False},
    "bluesky":   {"captionStyle": "short",  "maxHashtags": 3,  "useFirstComment": False},
}
```

**Değişen dosyalar:**
- `app/core/prompt_builder.py`:
  - `PLATFORM_DEFAULTS` sabiti + `_resolve_platform_rules(platform, override)` yardımcısı eklendi
  - `build_dynamic_content()`: `if template and template.platformOverrides and platforms:` → `if platforms:` — şablon olsun olmasın her zaman platform talimatı üretilir
  - `build_platform_instructions(overrides, platforms)` imzası güncellendi (`overrides: dict | None`); `continue` sadece PLATFORM_DEFAULTS'ta olmayan bilinmeyen platformlar için
- `app/core/caption_generator.py`:
  - `_build_output_format_instruction()`'daki `has_platform_overrides` flag kaldırıldı; her platform için merged `useFirstComment` değerine göre JSON şemasına `first_comment` alanı dahil edilir
  - `_resolve_platform_rules` import edildi

**Spec etkisi (bu doküman):** Bu doküman içinde geçen `build_platform_instructions()` kod örnekleri (satır ~1314-1355) **stale** — gerçek implementasyon `PLATFORM_DEFAULTS` merge mantığını kullanıyor. İleride bu doküman revize edilirse kod örnekleri güncellenmeli.

**Commit:** `b35a3ac` — "fix: Phase 7 Sprint 6 hotfix — PLATFORM_DEFAULTS (tüm platformlar için default caption kuralları)"

---

### Sprint 7 — Test, Cleanup, Documentation

**Hedef:** Full smoke test, duplicate temizlik, dokümantasyon finalize.

**Tahmini süre:** 1 gün

**Ön koşul:** Sprint 6 tamamlandı

#### Adım Adım Uygulama

**7.1** Test postlarını temizle:

```sql
DELETE FROM social.post_publications;
DELETE FROM social.posts;
```

**7.2** CATEGORY_TR duplicate temizliği:

- `posts.py` içindeki `CATEGORY_TR` dict kaldır (artık template kullanan akışlarda kullanılmıyor)
- `ai.py` içindeki `CATEGORY_TR` ve `CATEGORY_GUIDANCE` **kalır** (legacy suggest_ideas path için)
- `posts.py`'de `_build_prompt_with_rag_legacy` için gerekiyorsa `ai.py`'den import et

**7.3** `ContentCard.tsx` minor update:

```typescript
// ContentCard.tsx
const categoryLabel = post.template_id
  ? getTemplateName(post.template_id)  // Template'ler store'dan fetch
  : post.content_category || 'İçerik'
```

**7.4** Load test güncelleme: `shared/load-tests/locustfile.py`
- `CONTENT_CATEGORIES` random seçimini template_id random seçimine çevir
- Eski load test path'i ayrı fonksiyonda tut, template load test için yeni fonksiyon ekle

**7.5** Full smoke test matrisi:

| # | Senaryo | Beklenen |
|---|---|---|
| 1 | E-Ticaret + Ürün Kartı + 3 platform | 3 farklı caption, 1 görsel |
| 2 | Sağlık + Biliyor Muydunuz | Caption'da disclaimer var |
| 3 | Prof. Hizmet + Son Tarih Hatırlatma | LinkedIn caption daha uzun |
| 4 | Yemek + Günün Menüsü | Instagram first comment'te hashtag'ler |
| 5 | Teknoloji (özel şablon yok) | 8 genel şablon, başka yok |
| 6 | Serbest içerik | Eski akış, eski davranış |
| 7 | Özel gün | Eski akış bozulmadı |
| 8 | Alıntı | Eski akış bozulmadı |
| 9 | Video (faceless) | Eski akış bozulmadı |
| 10 | Autoposting (n8n trigger) | Template'siz eski yol |

**7.6** Son dokümantasyon güncellemeleri:

- `~/otomaix/docs/07-social-template-system.md` → Phase 7 COMPLETE olarak işaretle (bu dosyaya ekle)
- `~/otomaix/docs/00-platform-mimari.md` → Phase 7 referansı ekle
- CLAUDE.md dosyaları → Phase 7 tamamlandı özet girdisi

#### Manuel Adımlar

1. Test postlarını silme SQL'ini çalıştır:
   ```bash
   psql $DATABASE_URL -c "DELETE FROM social.post_publications; DELETE FROM social.posts;"
   ```

2. Tüm smoke test senaryolarını canlıda çalıştır

#### CLAUDE.md Girdi Template'i

```markdown
## YYYY-MM-DD — Phase 7 Sprint 7: Test & cleanup + Phase 7 TAMAMLANDI ✅

**Dosyalar:**
- backend/app/routers/posts.py (temizlik — CATEGORY_TR local kopya kaldırıldı)
- apps/social/frontend/components/ContentCard.tsx (minor — template_id gösterimi)
- shared/load-tests/locustfile.py (güncelleme — template load test)

**Cleanup:**
- Test postları silindi (soft launch öncesi temiz slate)
- CATEGORY_TR duplicate: posts.py'den kaldırıldı, ai.py'de kaldı (legacy)

**Smoke test sonuçları (10/10 başarılı):**
- E-Ticaret + Ürün Kartı: 3 platform caption ✅
- Sağlık + disclaimer ✅
- Platform-spesifik caption'lar çalışıyor ✅
- IG first comment hashtag'leri doğru ✅
- Teknoloji (özel yok): 8 genel şablon ✅
- Regresyon: özel gün/alıntı/video/serbest/autoposting bozulmadı ✅

**Phase 7 ÖZETİ:**
- 22 şablon aktif (E-Ticaret 4, Yemek 4, Sağlık 3, Prof. Hizmet 3, Genel 8)
- Sektör-spesifik guidance: 4 öncelikli derinleştirilmiş, 8 jenerik
- Akış C tam implement: caption → edit → image
- Platform-spesifik caption: Instagram/LinkedIn/Twitter farklılaşıyor
- Disclaimer otomasyonu: sağlık şablonları
- Scaffold: posts.slides kolonu + _build_prompt mode parametresi (v2 hazırlığı)

**Sonraki adım:** Kullanıcı kabul testi — hangi şablonların kullanıldığı, hangi caption'ların düzenlendiği ölçülür. 2-3 ay sonra veri bazlı öncelik: carousel v2, video şablonları, alt-sektör sistemleri.
```

#### Commit Mesajı

```
feat: Phase 7 Sprint 7 — Test, cleanup + Phase 7 TAMAMLANDI
```

---

## 6. Şablon Kataloğu (22 Şablon)

Bu bölüm Sprint 2'de `templates_data.py`'ye Python dict olarak eklenecek 22 şablonu YAML formatında içerir. Python'a dönüşüm Sprint 2'nin görevidir.

### 6.1 E-Ticaret Şablonları (4)

#### 6.1.1 Ürün Kartı

```yaml
id: eticaret-urun-karti
version: 1
name: Ürün Kartı
description: Tek ürün için fiyat, indirim ve özellik vurgusu
icon: "🛒"
sectors: [e-ticaret-perakende]
contentTypes: [image]
status: active
order: 10

formFields:
  - id: product_name
    label: Ürün Adı
    type: text
    required: true
    placeholder: "örn. Apple iPhone 15 128GB"
    validation: { maxLength: 120 }
    group: "Ürün Bilgisi"
  - id: price
    label: Fiyat
    type: number
    required: true
    suffix: "TL"
    validation: { min: 0 }
    group: "Fiyat"
  - id: old_price
    label: Eski Fiyat
    type: number
    required: false
    suffix: "TL"
    helpText: "Opsiyonel — indirim yüzdesi otomatik hesaplanır"
    group: "Fiyat"
  - id: key_feature
    label: Öne Çıkan Özellik
    type: text
    required: false
    placeholder: "örn. A17 Pro çip, 48MP kamera"
    validation: { maxLength: 200 }
    group: "Ürün Bilgisi"
  - id: cta
    label: Çağrı (CTA)
    type: select
    required: true
    defaultValue: "Sepete ekle"
    options:
      - { value: "Sepete ekle", label: "Sepete ekle" }
      - { value: "Hemen al", label: "Hemen al" }
      - { value: "Link bio'da", label: "Link bio'da" }
      - { value: "Şimdi keşfet", label: "Şimdi keşfet" }
    group: "Yayın"

output:
  aspectRatioSuggestion: "4:5"

prompt:
  guidance: |
    E-ticaret ürün kartı şablonu. Tek ürünü öne çıkaran statik sosyal medya
    görseli üretir.

    Görsel yönergesi: Stüdyo çekimi hissi, temiz arkaplan (marka renklerinden),
    ürün merkezde, fiyat/indirim rozeti görünür konumda, marka logosu köşede.
    Modern minimalist stil.

    Caption formülü: Hook (ürün adı + faydası) → Özellik vurgusu →
    Fiyat/indirim → CTA. Abartılı iddia kullanma.
  priority: [form_fields, brand_kit, rag_docs]

defaults:
  suggestedCTAs: ["Sepete ekle", "Hemen al", "Link bio'da", "Şimdi keşfet"]
  suggestedHashtags: ["indirim", "kampanya", "fırsat", "alışveriş"]

platformOverrides:
  instagram:
    captionStyle: medium
    maxHashtags: 15
    useFirstComment: true
  linkedin:
    captionStyle: long
    maxHashtags: 5
    toneAdjustment: "Daha kurumsal, satış dili yumuşatılmış"
  twitter:
    captionStyle: short
    maxHashtags: 2

tags: [ürün, fiyat, indirim]
```

#### 6.1.2 Kampanya Banner

```yaml
id: eticaret-kampanya-banner
version: 1
name: Kampanya Banner
description: Mevsimsel/özel gün kampanyaları için
icon: "🎉"
sectors: [e-ticaret-perakende]
contentTypes: [image]
status: active
order: 20

formFields:
  - id: campaign_name
    label: Kampanya Adı
    type: text
    required: true
    placeholder: "örn. Ramazan İndirimi, Yaz Fırsatları"
    validation: { maxLength: 60 }
  - id: discount_percent
    label: İndirim Oranı
    type: number
    required: false
    suffix: "%"
    validation: { min: 1, max: 99 }
  - id: start_date
    label: Başlangıç
    type: text
    required: false
    placeholder: "örn. 15 Mart"
  - id: end_date
    label: Bitiş
    type: text
    required: false
    placeholder: "örn. 30 Mart"
  - id: coupon_code
    label: Kupon Kodu
    type: text
    required: false
    placeholder: "örn. YAZ2026"
    validation: { maxLength: 30 }

output:
  aspectRatioSuggestion: "1:1"

prompt:
  guidance: |
    E-ticaret kampanya banner'ı. Göz alıcı, enerjik bir kampanya duyurusu.

    Görsel yönergesi: Canlı renkler, büyük tipografi ile indirim oranı ve
    kampanya adı öne çıksın. Arka planda kampanyayla ilgili grafik/desenler
    (ör. Ramazan teması için hilal, yaz için güneş).

    Caption formülü: Kampanya hook → Fayda (ne kadar indirim) → Süre → CTA.
  priority: [form_fields, brand_kit]

defaults:
  suggestedCTAs: ["Fırsatları kaçırmayın", "Şimdi alışverişe başlayın"]
  suggestedHashtags: ["kampanya", "indirim", "fırsat"]

platformOverrides:
  instagram: { captionStyle: medium, maxHashtags: 15 }
  facebook: { captionStyle: medium, maxHashtags: 5 }
```

#### 6.1.3 Stok Sayacı

```yaml
id: eticaret-stok-sayaci
version: 1
name: Stok Sayacı
description: Sınırlı stok, aciliyet yaratan içerik
icon: "⏰"
sectors: [e-ticaret-perakende]
contentTypes: [image]
status: active
order: 30

formFields:
  - id: product_name
    label: Ürün Adı
    type: text
    required: true
    validation: { maxLength: 120 }
  - id: remaining_stock
    label: Kalan Stok
    type: number
    required: true
    suffix: "adet"
    validation: { min: 1 }
  - id: price
    label: Fiyat
    type: number
    required: true
    suffix: "TL"

output:
  aspectRatioSuggestion: "1:1"

prompt:
  guidance: |
    Sınırlı stok aciliyet içeriği. "Kaçırma" hissi yaratır ama sahte urgency
    kullanılmaz — gerçek stok bilgisi verilir.

    Görsel yönergesi: Ürün merkezde, "Son N adet!" rozeti dikkat çekici.
    Kırmızı/turuncu aksan rengi olabilir (aciliyet).

    Caption formülü: Aciliyet hook → Ürün → Stok bilgisi → CTA.
    Yasaklar: "Son 1 adet!" gibi sahte urgency (stok gerçekten öyle değilse).
  priority: [form_fields, brand_kit]

defaults:
  suggestedCTAs: ["Kaçırma", "Hemen al"]
  suggestedHashtags: ["sonstok", "sınırlı", "hızlı"]

platformOverrides:
  instagram: { captionStyle: short, maxHashtags: 10 }
```

#### 6.1.4 Kombin/Set Önerisi

```yaml
id: eticaret-kombin-set
version: 1
name: Kombin / Set Önerisi
description: Birbirini tamamlayan ürün seti
icon: "👗"
sectors: [e-ticaret-perakende]
contentTypes: [image]
status: active
order: 40

formFields:
  - id: set_theme
    label: Set Teması
    type: text
    required: true
    placeholder: "örn. Yaz Tatili Kombini, Ofis Şık"
    validation: { maxLength: 80 }
  - id: products
    label: Ürünler
    type: textarea
    required: true
    placeholder: "Her satıra bir ürün. Örn:\nElbise - 499 TL\nÇanta - 299 TL\nAyakkabı - 399 TL"
    validation: { maxLength: 500 }
  - id: total_price
    label: Toplam Fiyat
    type: number
    required: false
    suffix: "TL"

output:
  aspectRatioSuggestion: "4:5"

prompt:
  guidance: |
    Birden fazla ürünün bir araya getirildiği kombin/set önerisi görseli.

    Görsel yönergesi: Flat-lay veya grid düzende ürünler bir arada, uyumlu
    renkler, profesyonel styling. Set teması görselin başlığında.

    Caption formülü: Set teması hook → Ürünler listesi → Toplam fiyat → CTA.
  priority: [form_fields, brand_kit]

defaults:
  suggestedCTAs: ["Sete tıkla", "Tüm kombini incele"]
  suggestedHashtags: ["kombin", "set", "stil", "moda"]

platformOverrides:
  instagram: { captionStyle: medium, maxHashtags: 15 }
  pinterest: { captionStyle: medium, maxHashtags: 10 }
```

### 6.2 Yemek & Gıda Şablonları (4)

#### 6.2.1 Günün Menüsü

```yaml
id: yemek-gunun-menusu
version: 1
name: Günün Menüsü
description: Öğle/akşam menü duyurusu
icon: "🍽️"
sectors: [yemek-gida]
contentTypes: [image]
status: active
order: 50

formFields:
  - id: meal_type
    label: Öğün
    type: select
    required: true
    options:
      - { value: "kahvaltı", label: "Kahvaltı" }
      - { value: "öğle", label: "Öğle" }
      - { value: "akşam", label: "Akşam" }
    group: "Zaman"
  - id: main_dish
    label: Ana Yemek
    type: text
    required: true
    placeholder: "örn. Kuzu tandır, enginar dolması"
    validation: { maxLength: 120 }
    group: "Menü"
  - id: side_dish
    label: Yanında
    type: text
    required: false
    placeholder: "örn. Bulgur pilavı, cacık, salata"
    validation: { maxLength: 200 }
    group: "Menü"
  - id: price
    label: Menü Fiyatı
    type: number
    required: true
    suffix: "TL"
    group: "Fiyat"

output:
  aspectRatioSuggestion: "4:5"

prompt:
  guidance: |
    Restoran günün menüsü duyurusu. İştah açıcı görsel, sıcak ton.

    Görsel yönergesi: Yemeğin profesyonel food fotoğrafı, doğal aydınlatma,
    tahta/tabak üzerinde servis. Menü detayları görselde değil caption'da
    detaylandırılır.

    Caption formülü: Duygu hook (tat/aroma) → Menü detayları → Fiyat → CTA.
  priority: [form_fields, brand_kit]

defaults:
  suggestedCTAs: ["Rezervasyon için", "Masanızı ayırın"]
  suggestedHashtags: ["gününmenüsü", "yemek", "restoran", "tatlar"]

platformOverrides:
  instagram: { captionStyle: medium, maxHashtags: 15, useFirstComment: true }
  facebook: { captionStyle: medium, maxHashtags: 5 }
```

#### 6.2.2 Yeni Lezzet Tanıtımı

```yaml
id: yemek-yeni-lezzet
version: 1
name: Yeni Lezzet
description: Menüye eklenen yeni yemek tanıtımı
icon: "✨"
sectors: [yemek-gida]
contentTypes: [image]
status: active
order: 60

formFields:
  - id: dish_name
    label: Yemek Adı
    type: text
    required: true
    validation: { maxLength: 100 }
  - id: description
    label: Açıklama
    type: textarea
    required: true
    placeholder: "Malzemeler, hazırlık özelliği, tat notaları"
    validation: { maxLength: 400 }
  - id: price
    label: Fiyat
    type: number
    required: false
    suffix: "TL"

output:
  aspectRatioSuggestion: "1:1"

prompt:
  guidance: |
    Yeni menü öğesi tanıtımı. "Denemek zorundasın" hissi yaratır.

    Görsel yönergesi: Yemek close-up, detaylı doku görünümü. "YENİ" rozeti
    veya benzer bir işaret köşede. Atmosfer iştah açıcı.

    Caption formülü: Yenilik hook → Yemek açıklaması → Tat notaları → CTA.
  priority: [form_fields, brand_kit]

defaults:
  suggestedCTAs: ["Siz de deneyin", "Tadına bakın"]
  suggestedHashtags: ["yenilezzet", "yemek", "tadı", "şeftavsiyesi"]

platformOverrides:
  instagram: { captionStyle: medium, maxHashtags: 15 }
```

#### 6.2.3 Online Sipariş Yönlendirme

```yaml
id: yemek-online-siparis
version: 1
name: Online Sipariş
description: Yemeksepeti/Getir/Trendyol yönlendirmeli
icon: "🛵"
sectors: [yemek-gida]
contentTypes: [image]
status: active
order: 70

formFields:
  - id: platforms
    label: Hangi platformlarda?
    type: text
    required: true
    placeholder: "örn. Yemeksepeti, Getir, Trendyol Yemek"
    validation: { maxLength: 200 }
  - id: offer
    label: Özel Teklif
    type: text
    required: false
    placeholder: "örn. 200 TL üzeri ücretsiz teslimat"
    validation: { maxLength: 150 }

output:
  aspectRatioSuggestion: "1:1"

prompt:
  guidance: |
    Online sipariş platformlarına yönlendirme. Pratik ve hızlı mesaj.

    Görsel yönergesi: Yemek görseli + platform logoları üstte. Fast-casual
    stil, tüketici dostu.

    Caption formülü: Pratik hook → Platform listesi → Teklif (varsa) → CTA.
  priority: [form_fields, brand_kit]

defaults:
  suggestedCTAs: ["Sipariş verin", "Tıkla ve ye"]
  suggestedHashtags: ["onlinesiparis", "evdeyiyelim"]

platformOverrides:
  instagram: { captionStyle: short, maxHashtags: 10 }
```

#### 6.2.4 Happy Hour

```yaml
id: yemek-happy-hour
version: 1
name: Happy Hour
description: Belirli saatte geçerli indirim
icon: "🍹"
sectors: [yemek-gida]
contentTypes: [image]
status: active
order: 80

formFields:
  - id: time_range
    label: Saat Aralığı
    type: text
    required: true
    placeholder: "örn. 16:00 - 19:00"
    validation: { maxLength: 40 }
  - id: offer_detail
    label: Teklif Detayı
    type: textarea
    required: true
    placeholder: "örn. Kahve + tatlı = 100 TL, İkinci içecek bedava"
    validation: { maxLength: 300 }
  - id: days
    label: Geçerli Günler
    type: text
    required: false
    placeholder: "örn. Pzt-Cuma, Hafta içi"

output:
  aspectRatioSuggestion: "1:1"

prompt:
  guidance: |
    Happy Hour promosyonu. Eğlenceli, davetkar ton.

    Görsel yönergesi: İçecek/yemek ile birlikte saat görseli. Renkli
    arkaplan, "Happy Hour" tipografi büyük.

    Caption formülü: Davet hook → Saat aralığı → Teklif → CTA.
  priority: [form_fields, brand_kit]

defaults:
  suggestedCTAs: ["Uğrayın", "Kaçırmayın"]
  suggestedHashtags: ["happyhour", "indirim", "keyif"]
```

### 6.3 Sağlık Şablonları (3)

#### 6.3.1 Biliyor Muydunuz?

```yaml
id: saglik-biliyor-muydunuz
version: 1
name: Biliyor Muydunuz?
description: Eğitici sağlık bilgisi içeriği
icon: "💡"
sectors: [saglik]
contentTypes: [image]
status: active
order: 90

formFields:
  - id: topic
    label: Konu
    type: text
    required: true
    placeholder: "örn. Yüksek tansiyon, Diyabet, Hipertansiyon"
    validation: { maxLength: 80 }
  - id: fact
    label: Bilgi
    type: textarea
    required: true
    placeholder: "Kısa, şaşırtıcı veya az bilinen bir tıbbi gerçek"
    validation: { maxLength: 500 }
  - id: source
    label: Kaynak
    type: text
    required: false
    placeholder: "örn. WHO 2024 raporu, Dünya Sağlık Örgütü"

output:
  aspectRatioSuggestion: "1:1"

prompt:
  guidance: |
    Eğitici sağlık bilgi içeriği. Kanıta dayalı, güvenilir bilgi verme.

    Görsel yönergesi: Temiz, profesyonel görsel. Tıbbi/sağlık teması (stetoskop,
    kalp, anatomi çizimi vb.) ama korku yaratmayan. "Biliyor muydunuz?" soru
    işareti tipografi öne çıksın.

    Caption formülü: Merak hook ("Biliyor muydunuz?") → Tıbbi bilgi →
    Önlem/öneri → CTA → DISCLAIMER (otomatik).
  priority: [form_fields, rag_docs, brand_kit]

defaults:
  suggestedCTAs: ["Muayene için", "Uzmanla görüşün"]
  suggestedHashtags: ["sağlık", "bilgi", "önlem"]
  disclaimer: >
    Bu içerik genel bilgilendirme amaçlıdır ve tıbbi tavsiye yerine geçmez.
    Sağlık sorunlarınız için mutlaka uzman hekime danışın.

platformOverrides:
  instagram: { captionStyle: medium, maxHashtags: 10 }
  linkedin: { captionStyle: long, maxHashtags: 5 }
```

#### 6.3.2 Doktor Profili

```yaml
id: saglik-doktor-profili
version: 1
name: Doktor Profili
description: Klinik ekibinden bir uzmanı tanıtım
icon: "👨‍⚕️"
sectors: [saglik]
contentTypes: [image]
status: active
order: 100

formFields:
  - id: doctor_name
    label: Doktor Adı
    type: text
    required: true
    validation: { maxLength: 120 }
  - id: specialty
    label: Uzmanlık
    type: text
    required: true
    placeholder: "örn. Kardiyoloji, Dermatoloji"
    validation: { maxLength: 100 }
  - id: experience_years
    label: Deneyim
    type: number
    required: false
    suffix: "yıl"
    validation: { min: 1 }
  - id: key_focus
    label: Ana Odak Alanı
    type: textarea
    required: false
    placeholder: "örn. Kalp ritim bozuklukları, çocuk dermatolojisi"
    validation: { maxLength: 300 }

output:
  aspectRatioSuggestion: "4:5"

prompt:
  guidance: |
    Klinik uzman tanıtım kartı. Güven verici, profesyonel.

    Görsel yönergesi: Doktor çekiminin yapıldığı orijinal fotoğraf ya da
    gelirse beyaz önlükle profesyonel stüdyo çekimi stili. Arka plan sakin/
    beyaz. İsim + uzmanlık tipografi ile görselde.

    Caption formülü: Tanıtım hook → Uzmanlık + deneyim → Odak alanı →
    Randevu CTA → DISCLAIMER (otomatik).
  priority: [form_fields, brand_kit]

defaults:
  suggestedCTAs: ["Randevu al", "Uzmanımızla tanışın"]
  suggestedHashtags: ["uzman", "sağlık", "ekip"]
  disclaimer: >
    Bu içerik genel bilgilendirme amaçlıdır ve tıbbi tavsiye yerine geçmez.

platformOverrides:
  linkedin: { captionStyle: long, maxHashtags: 5 }
```

#### 6.3.3 SSS (Sıkça Sorulan)

```yaml
id: saglik-sss
version: 1
name: SSS (Sıkça Sorulan)
description: Hastaların sık sorduğu soruya cevap
icon: "❓"
sectors: [saglik]
contentTypes: [image]
status: active
order: 110

formFields:
  - id: question
    label: Soru
    type: text
    required: true
    placeholder: "örn. Grip aşısı yan etki yapar mı?"
    validation: { maxLength: 200 }
  - id: answer
    label: Yanıt
    type: textarea
    required: true
    placeholder: "Kısa, anlaşılır, kanıta dayalı yanıt"
    validation: { maxLength: 600 }

output:
  aspectRatioSuggestion: "1:1"

prompt:
  guidance: |
    Hasta sık sorulan sorusuna cevap. Güven verici, anlaşılır dil.

    Görsel yönergesi: Soru işareti veya söz balonu grafiği. Temiz, okunur
    tipografi. Soru büyük, yanıt alt kısmında kısa özet.

    Caption formülü: Soru tekrarı → Detaylı yanıt → Önlem/öneri → CTA
    → DISCLAIMER (otomatik).
  priority: [form_fields, rag_docs, brand_kit]

defaults:
  suggestedCTAs: ["Detaylı bilgi için", "Uzmanımızla görüşün"]
  suggestedHashtags: ["sss", "sağlık", "bilgi"]
  disclaimer: >
    Bu içerik genel bilgilendirme amaçlıdır ve tıbbi tavsiye yerine geçmez.
    Bireysel durumunuz için mutlaka hekiminize danışın.
```

### 6.4 Profesyonel Hizmet Şablonları (3)

#### 6.4.1 Son Tarih Hatırlatma

```yaml
id: hizmet-son-tarih-hatirlatma
version: 1
name: Son Tarih Hatırlatma
description: Vergi beyannamesi, başvuru son tarihi gibi
icon: "📅"
sectors: [hizmet]
contentTypes: [image]
status: active
order: 120

formFields:
  - id: deadline_type
    label: Hangi Son Tarih?
    type: text
    required: true
    placeholder: "örn. KDV beyannamesi, yıllık gelir vergisi"
    validation: { maxLength: 150 }
  - id: deadline_date
    label: Son Tarih
    type: text
    required: true
    placeholder: "örn. 26 Nisan 2026"
    validation: { maxLength: 50 }
  - id: consequence
    label: Geciktirilirse
    type: text
    required: false
    placeholder: "örn. Gecikme zammı %3, ceza riski"
    validation: { maxLength: 200 }

output:
  aspectRatioSuggestion: "1:1"

prompt:
  guidance: |
    Profesyonel hizmetten son tarih hatırlatma (muhasebe, hukuk, danışmanlık).
    Uyarıcı ama panik yaratmayan ton.

    Görsel yönergesi: Takvim/saat grafiği, belirgin tarih vurgusu. Sarı/kırmızı
    aksan (aciliyet) ama aşırı değil. Profesyonel, kurumsal stil.

    Caption formülü: Hatırlatma hook → Son tarih → Gecikme sonuçları →
    Nasıl yardımcı olunur → CTA.
  priority: [form_fields, brand_kit]

defaults:
  suggestedCTAs: ["Bizimle iletişime geçin", "Hızlıca halledelim"]
  suggestedHashtags: ["sontarih", "mevzuat", "profesyonel"]

platformOverrides:
  linkedin: { captionStyle: long, maxHashtags: 5, toneAdjustment: "Thought leadership tonunda, B2B" }
  instagram: { captionStyle: medium, maxHashtags: 10 }
```

#### 6.4.2 Uzman Tavsiyesi

```yaml
id: hizmet-uzman-tavsiyesi
version: 1
name: Uzman Tavsiyesi
description: Sektörel insight, mini rehber
icon: "💼"
sectors: [hizmet]
contentTypes: [image]
status: active
order: 130

formFields:
  - id: tip_title
    label: Tavsiye Başlığı
    type: text
    required: true
    placeholder: "örn. Yeni şirket kurarken 5 kritik karar"
    validation: { maxLength: 150 }
  - id: tip_detail
    label: Detay
    type: textarea
    required: true
    placeholder: "Mini rehber — 3-5 madde veya özet anlatım"
    validation: { maxLength: 800 }

output:
  aspectRatioSuggestion: "4:5"

prompt:
  guidance: |
    Profesyonel hizmet sektöründe thought leadership içerik. Kanıta dayalı,
    uzman görüşü hissi.

    Görsel yönergesi: Minimalist, bilgi görseli hissi. Başlık büyük, okunur
    tipografi. Marka renklerinde aksanlar. İconografi (takım, ışık ampulü vb.).

    Caption formülü: İnsight hook → Detay (maddeler halinde) → Uygulama
    önerisi → CTA.
  priority: [form_fields, brand_kit, rag_docs]

defaults:
  suggestedCTAs: ["Detaylar için iletişim", "Randevu oluşturun"]
  suggestedHashtags: ["profesyonel", "tavsiye", "uzman"]

platformOverrides:
  linkedin: { captionStyle: long, maxHashtags: 5 }
  instagram: { captionStyle: medium, maxHashtags: 10 }
```

#### 6.4.3 Ekip Uzmanlığı

```yaml
id: hizmet-ekip-uzmanligi
version: 1
name: Ekip Uzmanlığı
description: Firmanızın uzmanlık alanlarını öne çıkarın
icon: "👔"
sectors: [hizmet]
contentTypes: [image]
status: active
order: 140

formFields:
  - id: expertise_area
    label: Uzmanlık Alanı
    type: text
    required: true
    placeholder: "örn. Vergi hukuku, dijital dönüşüm danışmanlığı"
    validation: { maxLength: 150 }
  - id: years_experience
    label: Firma Deneyim Yılı
    type: number
    required: false
    suffix: "yıl"
  - id: client_count
    label: Hizmet Verilen Müvekkil Sayısı
    type: number
    required: false
    helpText: "Opsiyonel — 'yüzlerce' de yazabilirsiniz"
  - id: notable_cases
    label: Önemli Çalışmalar
    type: textarea
    required: false
    placeholder: "İsimsiz, özet (gizlilik için)"
    validation: { maxLength: 400 }

output:
  aspectRatioSuggestion: "1:1"

prompt:
  guidance: |
    Firma uzmanlık tanıtımı. Güven, yetkinlik, deneyim vurgusu.

    Görsel yönergesi: Profesyonel/kurumsal stil, ekip görseli veya sembolik
    görsel (ör. kalem+kağıt+danışmanlık), sakin arkaplan.

    Caption formülü: Uzmanlık hook → Deneyim/rakamlar → Örnek işler
    (anonimleştirilmiş) → CTA.
  priority: [form_fields, brand_kit]

defaults:
  suggestedCTAs: ["İletişim için", "Danışmanlık alın"]
  suggestedHashtags: ["uzmanlık", "profesyonel", "deneyim"]

platformOverrides:
  linkedin: { captionStyle: long, maxHashtags: 5 }
```

### 6.5 Genel Şablonlar (8) — Tüm Sektörlerde Aktif

#### 6.5.1 Hakkımızda

```yaml
id: genel-hakkimizda
version: 1
name: Hakkımızda
description: Marka hikayesi ve değerleri
icon: "🏢"
sectors: ["*"]
contentTypes: [image]
status: active
order: 200

formFields:
  - id: founding_year
    label: Kuruluş Yılı
    type: number
    required: false
  - id: mission
    label: Misyon / Amaç
    type: textarea
    required: true
    placeholder: "Markanızın varlık nedeni, ne yapmaya çalışıyor?"
    validation: { maxLength: 500 }
  - id: differentiator
    label: Bizi Farklı Kılan
    type: textarea
    required: false
    placeholder: "Rakiplerden ne ile ayrışıyorsunuz?"
    validation: { maxLength: 400 }

output:
  aspectRatioSuggestion: "4:5"

prompt:
  guidance: |
    Marka hikayesi/değer önermesi. İçten, samimi ton.

    Görsel yönergesi: Marka logosu merkezde veya ekip görseli. Sıcak renkler
    (brand kit'e göre). Profesyonel ama sıcak.

    Caption formülü: Hikaye hook → Misyon → Değerler/fark → CTA.
  priority: [form_fields, brand_kit]

defaults:
  suggestedCTAs: ["Bizi tanıyın", "Web sitesini ziyaret edin"]
  suggestedHashtags: ["markamız", "hikayemiz", "değerlerimiz"]
```

#### 6.5.2 Ekip Tanıtımı

```yaml
id: genel-ekip-tanitimi
version: 1
name: Ekip Tanıtımı
description: Ekipten bir üye spotlight'ı
icon: "👥"
sectors: ["*"]
contentTypes: [image]
status: active
order: 210

formFields:
  - id: member_name
    label: Ekip Üyesi Adı
    type: text
    required: true
    validation: { maxLength: 100 }
  - id: role
    label: Görevi
    type: text
    required: true
    validation: { maxLength: 100 }
  - id: years_with_us
    label: Kaç Yıldır Bizimle?
    type: number
    required: false
    suffix: "yıl"
  - id: personal_note
    label: Kişisel Not
    type: textarea
    required: false
    placeholder: "Ekip üyesinin sevdiği şey, katkısı, hobileri..."
    validation: { maxLength: 400 }

output:
  aspectRatioSuggestion: "1:1"

prompt:
  guidance: |
    Ekip üyesi tanıtımı. İnsan odaklı, sıcak ton. "Ekibimizin arkasındaki
    yüzler" hissi.

    Görsel yönergesi: Ekip üyesinin profesyonel fotoğrafı (varsa). Yoksa
    initials veya avatar kutu. Arka planda marka renklerinden aksan.

    Caption formülü: Tanıtım hook → Görev + deneyim → Kişisel not → Takdir
    mesajı (opsiyonel) → CTA.
  priority: [form_fields, brand_kit]

defaults:
  suggestedCTAs: ["Ekibimizi tanıyın"]
  suggestedHashtags: ["ekip", "meetteam", "ailemiz"]
```

#### 6.5.3 Müşteri Yorumu

```yaml
id: genel-musteri-yorumu
version: 1
name: Müşteri Yorumu
description: Test bul/yorum kartı — sosyal kanıt
icon: "💬"
sectors: ["*"]
contentTypes: [image]
status: active
order: 220

formFields:
  - id: customer_name
    label: Müşteri Adı
    type: text
    required: true
    helpText: "Sadece ad veya ad+baş harfi (gizlilik için)"
    validation: { maxLength: 80 }
  - id: review_text
    label: Yorum
    type: textarea
    required: true
    placeholder: "Müşterinin bıraktığı yorum (izin alınmış olmalı)"
    validation: { maxLength: 500 }
  - id: rating
    label: Puan
    type: select
    required: false
    options:
      - { value: "5", label: "⭐⭐⭐⭐⭐ (5)" }
      - { value: "4", label: "⭐⭐⭐⭐ (4)" }
  - id: customer_context
    label: Müşteri Bağlamı
    type: text
    required: false
    placeholder: "örn. İstanbul'dan, 2 yıldır müşteri"
    validation: { maxLength: 150 }

output:
  aspectRatioSuggestion: "1:1"

prompt:
  guidance: |
    Müşteri yorumu / testimonial kartı. Sosyal kanıt, güven inşası.

    Görsel yönergesi: Yorum metni görselde alıntı şeklinde (tırnak işareti
    büyük), müşteri adı alt kısımda. Temiz, profesyonel tasarım. Puan
    yıldızları (varsa) görselde.

    Caption formülü: Teşekkür hook → Yorumun özeti → Davet (siz de paylaşın) → CTA.
  priority: [rag_docs, form_fields, brand_kit]

defaults:
  suggestedCTAs: ["Siz de deneyim paylaşın", "Deneyiminizi bize yazın"]
  suggestedHashtags: ["müşteriyorumu", "teşekkürler", "mutlumüşteri"]
```

#### 6.5.4 Motivasyon / İlham

```yaml
id: genel-motivasyon
version: 1
name: Motivasyon
description: İlham verici söz, marka ile ilişkili
icon: "✨"
sectors: ["*"]
contentTypes: [image]
status: active
order: 230

formFields:
  - id: quote_text
    label: Söz / İlham
    type: textarea
    required: true
    validation: { maxLength: 400 }
  - id: quote_author
    label: Söz Sahibi
    type: text
    required: false
    placeholder: "örn. Atatürk, Steve Jobs, Anonim"

output:
  aspectRatioSuggestion: "1:1"

prompt:
  guidance: |
    Motivasyon/ilham kartı. Pazartesi sabahları veya haftasonu postları için.

    Görsel yönergesi: Söz görselde büyük tipografi ile merkeze, yazar altta.
    Sakin, ilham verici arka plan (nature, abstract, brand colors).

    Caption formülü: Söz (tekrar) → Kısa düşünme önerisi → Güzel bir haftanız
    olsun / iyi Pazartesi türü kapanış.
  priority: [form_fields, brand_kit]

defaults:
  suggestedCTAs: []
  suggestedHashtags: ["motivasyon", "ilham", "pazartesi"]
```

#### 6.5.5 Haftalık Özet

```yaml
id: genel-haftalik-ozet
version: 1
name: Haftalık Özet
description: Haftanın içerik özeti / haber bülteni
icon: "📰"
sectors: ["*"]
contentTypes: [image]
status: active
order: 240

formFields:
  - id: week_highlights
    label: Haftanın Öne Çıkanları
    type: textarea
    required: true
    placeholder: "3-5 madde halinde haftanın özeti"
    validation: { maxLength: 600 }

output:
  aspectRatioSuggestion: "4:5"

prompt:
  guidance: |
    Hafta sonu paylaşımı — haftanın özeti. Profesyonel ama samimi.

    Görsel yönergesi: Infografik stili, numaralı maddeler, temiz tipografi.

    Caption formülü: Hafta özet hook → Maddeler → İyi hafta sonları kapanış.
  priority: [form_fields, brand_kit]

defaults:
  suggestedCTAs: []
  suggestedHashtags: ["haftanınözeti", "cumartesi"]
```

#### 6.5.6 Kutlama / Tebrik

```yaml
id: genel-kutlama
version: 1
name: Kutlama / Tebrik
description: Başarı, yıldönümü, teşekkür içerikleri
icon: "🎊"
sectors: ["*"]
contentTypes: [image]
status: active
order: 250

formFields:
  - id: celebration_type
    label: Ne Kutlaniyor?
    type: text
    required: true
    placeholder: "örn. 5. yıldönümü, 1000. müşteri, ödül"
    validation: { maxLength: 150 }
  - id: achievement
    label: Başarı Detayı
    type: textarea
    required: true
    validation: { maxLength: 500 }
  - id: thanks_to
    label: Teşekkür
    type: text
    required: false
    placeholder: "örn. Müşterilerimize, ekibimize"

output:
  aspectRatioSuggestion: "1:1"

prompt:
  guidance: |
    Kutlama içeriği. Sıcak, içten, gururlu.

    Görsel yönergesi: Konfeti/şerit/balon görseli, canlı renkler. Kutlama
    yazısı büyük tipografi.

    Caption formülü: Duyuru hook → Detay → Teşekkür → Kutlama mesajı.
  priority: [form_fields, brand_kit]

defaults:
  suggestedCTAs: ["Siz de kutlayın"]
  suggestedHashtags: ["kutlama", "teşekkürler", "başarı"]
```

#### 6.5.7 Sosyal Kanıt

```yaml
id: genel-sosyal-kanit
version: 1
name: Sosyal Kanıt
description: Medya alıntısı, ödül, referans
icon: "🏆"
sectors: ["*"]
contentTypes: [image]
status: active
order: 260

formFields:
  - id: proof_type
    label: Kanıt Türü
    type: select
    required: true
    options:
      - { value: "medya", label: "Medya Alıntısı" }
      - { value: "ödül", label: "Ödül" }
      - { value: "referans", label: "Kurumsal Referans" }
      - { value: "sertifika", label: "Sertifika" }
  - id: source
    label: Kaynak
    type: text
    required: true
    placeholder: "örn. Hürriyet, TUGIAD, ISO, ... "
    validation: { maxLength: 150 }
  - id: detail
    label: Detay
    type: textarea
    required: true
    validation: { maxLength: 400 }

output:
  aspectRatioSuggestion: "1:1"

prompt:
  guidance: |
    Sosyal kanıt kartı. Güven inşası, markaya otorite katar.

    Görsel yönergesi: Kaynağın logosu (medya/kurum) öne çıksın. Ödül/sertifika
    ise ikonu belirgin. Sade, profesyonel.

    Caption formülü: Haberin hook → Detay → Teşekkür/alçakgönüllülük → CTA.
  priority: [form_fields, brand_kit]

defaults:
  suggestedCTAs: []
  suggestedHashtags: ["referans", "ödül", "başarı"]
```

#### 6.5.8 Çalışma Saatleri / İletişim

```yaml
id: genel-calisma-saatleri
version: 1
name: Çalışma Saatleri
description: Operasyonel bilgi duyurusu
icon: "🕐"
sectors: ["*"]
contentTypes: [image]
status: active
order: 270

formFields:
  - id: announcement_type
    label: Duyuru Tipi
    type: select
    required: true
    options:
      - { value: "saatler", label: "Normal çalışma saatleri" }
      - { value: "tatil", label: "Tatil günleri" }
      - { value: "özel", label: "Özel durum (taşınma, vb.)" }
  - id: detail
    label: Detay
    type: textarea
    required: true
    placeholder: "Saatler, tarihler, iletişim kanalları"
    validation: { maxLength: 500 }

output:
  aspectRatioSuggestion: "1:1"

prompt:
  guidance: |
    Operasyonel duyuru. Açık, pratik, bilgilendirici.

    Görsel yönergesi: Saat/takvim ikonu, okunabilir tipografi, marka renkleri.

    Caption formülü: Duyuru hook → Detay (saatler/tarihler) → İletişim kanalları.
  priority: [form_fields, brand_kit]

defaults:
  suggestedCTAs: ["Detaylı bilgi için"]
  suggestedHashtags: ["duyuru", "çalışmasaatleri"]
```

---

## 7. Prompt Guidance Yazım Formülü

Her şablonun `prompt.guidance` alanı Claude'a verilen talimatlardır. Yeni şablon eklenirken bu formülü takip et:

**7 adımlı yapı:**

1. **Şablonun amacı** (1 cümle): "E-ticaret ürün kartı şablonu. Tek ürünü öne çıkaran statik sosyal medya görseli üretir."

2. **Görsel yönergesi** (2-4 cümle):
   - Kompozisyon (ne merkez, ne arka plan)
   - Stil (stüdyo, flat-lay, lifestyle, minimalist vb.)
   - Renk ipucu (marka renklerine referans)
   - Tipografi notu (varsa — "fiyat büyük görünsün")

3. **Caption formülü** (1 satır): "Hook → Özellik → Fiyat → CTA" gibi basit bir akış.

4. **Yasaklar** (opsiyonel, 1-2 cümle): "Abartılı iddia kullanma", "Rakip ismi yazma", "Sahte urgency yaratma" vb.

5. **Disclaimer referansı** (sağlık/hukuk/finans için): "Caption sonuna defaults.disclaimer AYNEN eklenecek" notu.

6. **Tone ayarlamaları** (opsiyonel): Platform-spesifik override'lardan farklı olarak, şablonun genel ton kuralı.

7. **Priority override** (nadir): Varsayılan `[form_fields, brand_kit, rag_docs]` uymuyorsa farklı sıra belirt.

**Uzunluk:** 100-400 kelime. Daha kısa → Claude bağlamsız üretir. Daha uzun → cache boyutu büyür, maliyet artar.

**Dil:** Türkçe yaz. Claude hem talimatı hem üretimi Türkçe anlayacak/yapacak. İstisna: `image_prompt` İngilizce üretilmeli (fal.ai için) — bu kuralı output format'ta ayrıca belirt.

**Örnek — iyi guidance:**

> E-ticaret ürün kartı şablonu. Tek ürünü öne çıkaran statik görsel.
>
> Görsel yönergesi: Stüdyo çekimi hissi, temiz arkaplan (marka renklerinden), ürün merkezde, fiyat rozeti görünür konumda, marka logosu köşede. Modern minimalist.
>
> Caption formülü: Hook → Özellik → Fiyat → CTA.
>
> Abartılı iddia kullanma ("dünyanın en iyisi" vb.).

**Örnek — kötü guidance (ne yapma):**

> ❌ "Güzel bir ürün kartı yap."  — çok belirsiz
>
> ❌ "Apple, Nike, Samsung gibi markaları örnek al."  — rakip referansı, copyright riski
>
> ❌ 800 kelime uzun paragraf  — token cache maliyeti yüksek

---

## 8. Test Master Checklist

Sprint'ler arası birikimli test matrisi. Sprint X tamamlandıktan sonra sadece o sprint'in testleri değil, **önceki sprintlerin regresyon testleri de** çalıştırılmalı.

### 8.1 Cross-Sprint Regresyon Testleri (Her Sprint Sonunda)

| Test | Sprint 1 sonrası | Sprint 2 sonrası | Sprint 3 sonrası | Sprint 4 sonrası | Sprint 5 sonrası | Sprint 6 sonrası | Sprint 7 sonrası |
|---|---|---|---|---|---|---|---|
| Özel Gün post üretimi | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Alıntı post üretimi | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Video (faceless) akışı | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Serbest içerik (şablonsuz) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Autoposting (n8n trigger) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| GET /templates çalışıyor | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Şablon filter (sektör) | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Template-aware prompt | — | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| Caption endpoint | — | — | — | ✓ | ✓ | ✓ | ✓ |
| Akış C tam akış | — | — | — | — | ✓ | ✓ | ✓ |
| Platform-spesifik caption | — | — | — | — | — | ✓ | ✓ |

### 8.2 10 Senaryo Smoke Test (Sprint 7)

Sprint 7'de tam smoke test olarak çalıştırılacak:

1. **E-Ticaret + Ürün Kartı** → 3 platform, her biri farklı caption, 1 görsel
2. **Sağlık + Biliyor Muydunuz** → Caption sonunda disclaimer, IG + LinkedIn
3. **Prof. Hizmet + Son Tarih Hatırlatma** → LinkedIn daha uzun caption
4. **Yemek + Günün Menüsü** → Instagram first_comment'te hashtag'ler
5. **Teknoloji (özel şablon yok)** → 8 genel şablon, başka yok
6. **Serbest içerik** → Eski akış, form yok, direkt prompt
7. **Özel gün akışı** → Eski akış tamamen bozulmadı
8. **Alıntı akışı** → Eski akış tamamen bozulmadı
9. **Video (faceless)** → Tamamen dokunulmamış, çalışıyor
10. **Autoposting n8n trigger** → Template'siz, eski hardcoded path

### 8.3 Performans Kontrolü

**Beklenen latency:**

| İşlem | Beklenen süre | Ölçüm yöntemi |
|---|---|---|
| GET /templates (cold) | < 500ms | İlk çağrı, no cache |
| GET /templates (warm) | < 100ms | HTTP cache hit |
| POST /generate-caption (cold) | 3-6s | İlk brand+template kombinasyonu |
| POST /generate-caption (warm) | 2-4s | Aynı kombinasyon — cache hit |
| POST /generate | ~100ms | Fal.ai async start (görsel beklenmez) |
| Fal.ai render | 30-60s | Async, frontend polling |

**Cache hit doğrulama:**

Sprint 4 sonrası backend log'larda:
```
Caption gen cache: read=XXXX, create=YYYY, template=eticaret-urun-karti
```

İkinci çağrıda `read > 0` olmalı. Yoksa 3-tier cache yapısı düzgün kurulmamış.

### 8.4 DB Integrity Kontrolleri

Sprint 7 sonunda:

```sql
-- Template'lerin doğru kaydedildiğini kontrol
SELECT template_id, COUNT(*) FROM social.posts
WHERE template_id IS NOT NULL
GROUP BY template_id;

-- platform_captions JSONB yapısı
SELECT platform_captions FROM social.posts
WHERE platform_captions IS NOT NULL
LIMIT 3;
-- {"default": "...", "platforms": {"instagram": {...}}}

-- Orphan reference kontrolü (template silinirse vs.)
SELECT DISTINCT template_id FROM social.posts
WHERE template_id IS NOT NULL;
-- Hepsi templates_data.py'de tanımlı olmalı
```

---

## 9. Kapsam Dışı — Final Konsolide Liste

Bu iterasyonda **kesinlikle yapılmayacak**, sonraki sürümlere ertelenmiş işler:

### v2'ye ertelenenler (yakın gelecek, 2-3 ay)

- **Carousel multi-slayt** — Şu an scaffold var (`posts.slides` kolonu, `_build_prompt(mode=)` parametresi) ama implementasyon yok
- **Coming_soon kartları** — Template grid'de "yakında" etiketli disabled kartlar
- **Alt-sektör sistemi** — `sectors.parent_sector_id` kullanımı (DB mevcut)
- **Autoposting template entegrasyonu** — Veri havuzu altyapısıyla beraber
- **Geçmiş sayfası elden geçirme** — Sadece ContentCard minor update var
- **Image-to-image pipeline** — Kullanıcı kendi fotosunu yükleyip AI üzerinden varyasyon
- **URL scraping** — Trendyol/Hepsiburada/Amazon link'inden otomatik form doldurma

### v3'e ertelenenler (uzak gelecek)

- **Video şablonları** — Faceless akışı dışında sektör-specific video
- **Toplu içerik (bulk)** — Excel/CSV import ile çoklu post üretimi
- **Template editor UI** — Kullanıcıların kendi özel şablonlarını oluşturması
- **A/B test sistemi** — Aynı içeriğin 2 varyantı, performans karşılaştırması
- **Şablon marketplace** — Kullanıcılar arası template paylaşımı

### Hiç yapılmayacaklar (strateji gereği)

- **Rakip karşılaştırma içeriği** — Hukuki risk, marka itibarı
- **Absolut iddia üretimi** — "Dünyanın en iyisi" türü ifadeler
- **Finansal tahmin/garanti** — SPK uyumsuz
- **Medikal tanı/doz bilgisi** — Yasal yükümlülük
- **Kişiye özel hedefleme** — GDPR/KVKK riski

---

## 10. Rollback Stratejisi

Her sprint için **özel rollback planı.** Sprint canlıda sorun yaratırsa geri alma adımları:

### Sprint 1 Rollback

**Hızlı rollback (prefer):**
```bash
# Git rollback
cd /root/otomaix
git revert <sprint-1-commit-hash>
git push

# Kolon'ları silmeden bırak (eski app kolonları görmezden gelir)
```

**Tam rollback (gerekirse):**
```sql
-- Migration 022'yi geri al
DROP INDEX IF EXISTS social.idx_posts_template_id;
ALTER TABLE social.posts
  DROP COLUMN IF EXISTS template_id,
  DROP COLUMN IF EXISTS template_fields,
  DROP COLUMN IF EXISTS platform_captions,
  DROP COLUMN IF EXISTS slides;
```

### Sprint 2 Rollback

Kod-only değişiklik — sadece git revert yeter:

```bash
git revert <sprint-2-commit-hash>
git push
```

`GET /templates` tekrar boş dict döner, ama endpoint'in kendisi hata vermez.

### Sprint 3 Rollback

Kritik sprint — backward compat için `_build_prompt_with_rag_legacy` var. Sorun durumunda:

```bash
# Hızlı rollback
git revert <sprint-3-commit-hash>
git push

# Alternatif (code-level fallback):
# posts.py'de _build_image_prompt fonksiyonu template_id olsa bile
# geçici olarak sadece legacy path kullanabilir — kullanıcıya bilgi verilmeli
```

### Sprint 4 Rollback

Caption endpoint kapatılabilir — frontend Sprint 5'ten önce caption endpoint'i kullanmıyor (bağımsız):

```bash
git revert <sprint-4-commit-hash>
git push

# Frontend Sprint 5 henüz deploy edilmediyse, caption endpoint kaldırılması kullanıcıyı etkilemez
```

### Sprint 5 Rollback

**En kritik rollback.** Frontend kullanıcı akışı etkilenir. Rollback'te eski UI (3 kategori buton) geri gelir.

```bash
git revert <sprint-5-commit-hash>
cd /root/otomaix/apps/social/frontend
pnpm build && pnpm start  # Coolify otomatik rebuild de yapabilir
```

**Kısmi rollback:** Sadece sorun yaratan component'i disable et:
```typescript
// icerik-olustur/page.tsx
const USE_TEMPLATES = false  // Feature flag
// Eski UI'yi koru, template grid'i koşullu render et
```

### Sprint 6 Rollback

`publish_post` fallback mantığı zaten var — platform_captions NULL olarak işaretleyince legacy mantık çalışır:

```sql
-- Acil durum: tüm template post'ların platform_captions'ını legacy'e çevir
UPDATE social.posts
SET platform_captions = NULL
WHERE template_id IS NOT NULL AND status = 'generated';
```

Sonra kod rollback:
```bash
git revert <sprint-6-commit-hash>
git push
```

### Sprint 7 Rollback

Cleanup sprint — rollback minimum:

```bash
# Sadece dokümantasyon değişiklikleri geri alınır
git revert <sprint-7-commit-hash>
```

Test postları silindi, geri getirilemez (ama önemli değil).

### Ortak Rollback Kuralları

1. **Her sprint sonrası commit hash'ini CLAUDE.md'ye yaz** — rollback için kritik
2. **Rollback sonrası mutlaka smoke test** — özellikle regresyon senaryoları
3. **Rollback kararı = kullanıcı onayı** — Claude Code kendi başına rollback yapmaz
4. **Rollback sonrası incident log** — neden başarısız oldu, bir sonraki denemeden önce düzelt

---

## Appendix A — CLAUDE.md Girdi Formatı

Her sprint tamamlandığında ilgili `CLAUDE.md` dosyasına **yeni girdi eklenir**. Mevcut girdiler **asla silinmez.**

### A.1 Backend CLAUDE.md Girdi Template'i

```markdown
## YYYY-MM-DD — Phase 7 Sprint X: <Başlık> ✅

**Dosyalar:**
- <dosya yolu> (YENİ | değişti | silindi — kısa not)
- ...

**Değişiklikler:**
- <somut madde 1 — ne yapıldı, teknik detay>
- <somut madde 2>
- ...

**Manuel adımlar tamamlandı:**
- [x] <manuel adım 1>
- [x] <manuel adım 2>

**Test sonuçları:**
- <test 1> ✅
- <test 2> ✅

**Commit:** <commit hash>

**Sonraki sprint:** Sprint X+1 — <kısa başlık>
```

### A.2 Frontend CLAUDE.md Girdi Template'i

```markdown
## YYYY-MM-DD — Phase 7 Sprint X: <Başlık> ✅

**Dosyalar:**
- <frontend dosya yolu> (YENİ | değişti)

**Değişiklikler:**
- <UI değişikliği açıklaması>
- <component/hook/store eklemeleri>

**Test sonuçları:**
- <UI test senaryosu 1> ✅

**Commit:** <commit hash>
```

### A.3 Girdi Sırası

- **En üstte en yeni girdi** — reverse chronological
- **Mevcut girdileri silme** — platform tarihini korumak için
- Eğer CLAUDE.md çok uzun olursa (>2000 satır), eski girdiler ayrı arşiv dosyasına taşınabilir (`CLAUDE.md.archive-2025.md` gibi) — ama bu Phase 7 kapsam dışı

### A.4 Örnek Tamamlanmış Girdi

```markdown
## 2026-04-22 — Phase 7 Sprint 1: Backend template altyapısı ✅

**Dosyalar:**
- shared/db/migrations/022_posts_template_fields.sql (YENİ)
- backend/app/core/templates_data.py (YENİ — boş dict, Sprint 2'de doldurulacak)
- backend/app/models/templates.py (YENİ — Pydantic modeller)
- backend/app/routers/templates.py (YENİ — GET /templates endpoint)
- backend/app/main.py (değişti — templates router + startup validation)
- backend/app/routers/auth.py (değişti — /init brands LEFT JOIN sectors)
- backend/app/models/schemas.py (değişti — BrandOut.sector_slug eklendi)
- backend/app/routers/posts.py (değişti — PostGenerate yeni field'ları kabul ediyor)

**Değişiklikler:**
- social.posts tablosuna template_id TEXT, template_fields JSONB, platform_captions JSONB, slides JSONB NULL kolonları eklendi
- idx_posts_template_id index'i eklendi (WHERE template_id IS NOT NULL)
- GET /templates endpoint — 1 saat cache, boş dönüyor (Sprint 2'de dolacak)
- /auth/init response'una brand.sector_slug + brand.sector_display_name eklendi
- Startup'ta template validation (Sprint 2 için hazır)

**Manuel adımlar tamamlandı:**
- [x] Migration 022 VPS'te çalıştırıldı (psql komutu)
- [x] DB kolonları pgAdmin'den doğrulandı
- [x] Backend restart sonrası sağlık kontrolü başarılı

**Test sonuçları:**
- GET /templates → 200, {templates: [], version: "1.0"} ✅
- GET /auth/init → brand.sector_slug alanı mevcut ✅
- Regresyon: mevcut post üretimi hata vermiyor ✅

**Commit:** a3f7c21

**Sonraki sprint:** Sprint 2 — 22 şablon + SECTOR_GUIDANCE doldurma
```

---

## Appendix B — Commit Message Conventions

### B.1 Temel Format

```
<type>: Phase 7 Sprint X — <özet>
```

**Type seçenekleri:**

- `feat:` — Yeni özellik (çoğu sprint için)
- `fix:` — Bug fix (sprint içi hotfix gerekirse)
- `refactor:` — Kod refactor (büyük iç değişiklik, davranış aynı)
- `chore:` — Bağımlılık güncelleme, config değişikliği
- `docs:` — Sadece dokümantasyon (bu spec'in kendisi gibi)
- `test:` — Test ekleme (Sprint 7 load test güncellemesi)

### B.2 Sprint-Bazlı Commit Örnekleri

```
feat: Phase 7 Sprint 1 — Backend template altyapısı (migration + GET /templates + sector_slug)
feat: Phase 7 Sprint 2 — 22 şablon + SECTOR_GUIDANCE + frontend types
feat: Phase 7 Sprint 3 — Prompt building refactor (template-aware + 3-tier caching)
feat: Phase 7 Sprint 4 — Caption endpoint + Akış C (AI caption + image_prompt + hashtags)
feat: Phase 7 Sprint 5 — Frontend wizard refactor (template grid + dynamic form + Akış C)
feat: Phase 7 Sprint 6 — Platform-spesifik publishing (Upload-Post per-platform captions)
feat: Phase 7 Sprint 7 — Test, cleanup + Phase 7 TAMAMLANDI
```

### B.3 Phase 7 Dışı Commit Örnekleri

Phase 7 süresince **başka konular için commit gerekirse** (örn. acil bug fix, değişen bağımlılık), ayrı commit yapılmalı — Phase 7 commit'iyle karıştırılmamalı:

```
fix: Fal.ai webhook endpoint 502 hatası düzeltildi
chore: anthropic SDK 0.50.0'a güncellendi
docs: CLAUDE.md'de eski giriş düzeltildi
```

### B.4 Çok Satırlı Commit Mesajı (Opsiyonel)

Büyük sprintler için açıklayıcı gövde eklenebilir:

```
feat: Phase 7 Sprint 5 — Frontend wizard refactor (template grid + dynamic form + Akış C)

- 3 kategori butonu (Ürün/Hizmet/Kurumsal) kaldırıldı
- TemplateGrid/TemplateCard/DynamicForm/CaptionEditor componentleri eklendi
- page.tsx wizard akışı yeniden yapılandırıldı
- Akış C implement: form → caption preview → edit → image generate
- analytics.ts'e 6 template event'i eklendi
- store.ts Brand.sector_slug eklendi

Test: 10 smoke senaryosu yeşil.
Regresyon: özel gün / alıntı / video / serbest içerik bozulmadı.
```

### B.5 Commit Öncesi Onay

Claude Code commit yapmadan önce **mutlaka kullanıcı onayı alır.** Format:

```
Sprint X için hazırladığım commit:

feat: Phase 7 Sprint X — <özet>

Değişen dosyalar: N adet (<liste>)
Test: <özet>

Push edebilir miyim?
```

Kullanıcı "evet"/"push et"/"onay" dediğinde:
```bash
cd /root/otomaix
git add .
git commit -m "feat: Phase 7 Sprint X — <özet>"
git push
```

Push sonrası canlı test talimatı verilir, test onayı alınmadan sonraki sprint'e geçilmez.

---

## 11. Belirsizlik Durumunda

Bu belgede açıkça karar verilmemiş bir nokta çıkarsa Claude Code'un yaklaşımı:

1. **Kod yazmadan önce kullanıcıya sor**
2. Hangi dosyada karar verilecek, hangi alternatifler düşünüyor — açıkça belirt
3. Bu belgede yanıt yoksa kullanıcıdan yön al
4. **Varsayım yapma** — sor, sonra uygula
5. Cevap aldıktan sonra ilgili sprint'in CLAUDE.md girdisine kararı ekle (future reference)

---

**Belge sonu.**

**Hazırlanma tarihi:** Nisan 2026
**Sürüm:** v1.1
**Kapsam:** Otomaix Social `/icerik-olustur` — Phase 7 Sektör-Spesifik Şablon Sistemi
**Toplam:** 7 sprint, ~8 iş günü, 22 şablon, 4 öncelikli + 8 generic sektör guidance

**Sonraki güncelleme:** Phase 7 tamamlandıktan sonra kullanıcı verilerine dayalı v2 planlama belgesi (`08-template-system-v2.md`) hazırlanır.

