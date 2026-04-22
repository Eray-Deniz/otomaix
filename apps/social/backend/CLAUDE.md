# Social Backend — CLAUDE.md

> **🚧 Phase 9 — Ürün/Hizmet Kütüphanesi + Image-Edit Pipeline (başladı: 2026-04-21).**
> `/icerik-olustur` manuel akışına ürün/hizmet görseli tabanlı içerik üretimi eklenmesi. Marka seviyesinde `brand_products` kütüphanesi + ürüne bağlı RAG dokümanları + `nano-banana-pro/edit` image-edit adapter.
> **İlerleme:** Sprint 1 ✅ · Sprint 2 ✅ · Sprint 3 ✅ · Sprint 4 ✅ · Sprint 5 ✅ · Sprint 6 ✅ · Sprint 7 ✅ · Sprint 7 polish ✅ (prompt_builder sadeleştirme)
> Otomatik yayın entegrasyonu Phase 10'a ertelendi.

> **✅ Phase 7 — Sektör-Spesifik Şablon Sistemi TAMAMLANDI (2026-04-19).**
> `/icerik-olustur` sayfasının 3 genel kategorisi (Ürün/Hizmet/Kurumsal) → 22 sektör-spesifik şablona dönüştü.
> Detaylı plan: `~/otomaix/docs/07-social-template-system.md`.
> **İlerleme:** Sprint 1 ✅ · Sprint 2 ✅ · Sprint 3 ✅ · Sprint 4 ✅ · Sprint 5 polish ✅ · Sprint 6 ✅ · Sprint 6 hotfix (PLATFORM_DEFAULTS) ✅ · Sprint 6 hardening ✅ · Sprint 7 (media adapter refactor) ✅ — **Phase 7 tamamlandı**

## 2026-04-22 — Phase 9 Sprint 7 polish: prompt_builder ürün bağlamı sadeleştirme ✅

**Sorun:** Frontend Sprint 9B'de ürün seçilince `ana_konu = product.name` ve `one_cikan_ozellik = product.description` şablon alanlarına pre-fill yapılıyor. Bu alanlar `generate-caption` çağrısında "YAPISAL VERİLER" bloğu olarak Claude'a iletiliyor. Aynı zamanda Sprint 7'de eklenen "ÜRÜN/HİZMET BAĞLAMI" bloğu da ad/açıklama/etiketleri Claude'a yazıyordu — çifte tekrar.

**Değişen dosya:** `app/core/prompt_builder.py`

- **Kaldırıldı:** `build_dynamic_content` içindeki "=== ÜRÜN/HİZMET BAĞLAMI ===" bloğu (ad, açıklama, etiketler, "doğal dille geçir" talimatı)
- **Korundu:** `product.image_url` varsa image_prompt özel kuralı (`⚠️ image_prompt İÇİN ÖZEL KURAL`) — bu kural Claude'a ürünü tarif etmemesini, sahne/kompozisyon/ışık tarif etmesini söyler; image-edit kalitesi için kritik
- **Değişmedi:** RAG doküman fetch (`get_product_document_context`) — ürün dokümanları hâlâ bağlam olarak ekleniyor

**Sonuç:** Prompt artık şablon alanlarını, image-edit kuralını (varsa) ve ürün dokümanlarını alıyor; ad/açıklama tekrarı yok.

## 2026-04-21 — Phase 9 Sprint 7: Caption endpoint'e ürün bağlamı ✅

**Kapsam:** `POST /posts/generate-caption` artık opsiyonel `product_id` kabul eder. Set edilmişse ürünün (1) adı/açıklaması/tag'leri Tier 3 prompt'una "ÜRÜN/HİZMET BAĞLAMI" bloğu olarak enjekte edilir, (2) ürüne bağlı RAG dokümanları (Sprint 4 `get_product_document_context`) mevcut `document_ids` context'i ile birleşir, (3) ürünün görseli varsa image_prompt'a özel talimat eklenir — ürünün kendisi tarif edilmez (fal.ai image-edit modeli referans görselden alacak), sadece sahne/kompozisyon/ışık tarif edilir.

**Değişen dosyalar (3):**

| Dosya | Değişiklik |
|-------|-----------|
| `app/routers/posts.py` | `GenerateCaptionRequest.product_id: UUID \| None`; `generate_caption`: ürün fetch (brand_id guard) + 404 guard + `get_product_document_context` merge; `generate_captions(..., product=product)` |
| `app/core/caption_generator.py` | `generate_captions` opsiyonel `product` kwarg; `build_dynamic_content`'e geçirilir |
| `app/core/prompt_builder.py` | `build_dynamic_content` opsiyonel `product` kwarg; Tier 3'e "=== ÜRÜN/HİZMET BAĞLAMI ===" bloğu (user_prompt'tan sonra, yapısal verilerden önce); `image_url` varsa image-edit özel kuralı |

**Kararlar:**
- **Sahiplik:** `WHERE id=$1 AND brand_id=$2` (Sprint 6 pattern'i). `assert_brand_owned` zaten çalıştı — ekstra JOIN gereksiz.
- **RAG merge:** Brand docs ve product docs ayrı `get_*_document_context` çağrılarıyla çekilip `"\n\n---\n\n"` ile birleşir. İkisi de boşsa `rag_context=None` (mevcut davranış).
- **image_edit notu:** Yalnızca ürünün `image_url`'i varsa emit edilir. Görselsiz üründe FLUX text-to-image devreye gireceği için ürün tanımı normal tarif edilebilir — bu durumda ek kural basılmaz.
- **Caption içine ürün adı:** Prompt talimatı "doğal dille geçir, ezberci satış dili değil" — Claude'un tonaliteye uyumunu bozmasın.

**Etki analizi:**
- Risk: düşük — `product_id` opsiyonel, NULL'da akış birebir Sprint 4 davranışı
- Backward compat: tam (mevcut caller'lar yeni alan göndermedikçe etkilenmez)
- 3-tier cache: Tier 1 (system) + Tier 2 (brand_context) değişmedi → ürünlü/ürünsüz çağrılar Tier 1/2 cache hit'lerini paylaşır; yalnızca Tier 3 dynamic değişir (cache'siz zaten)
- `build_dynamic_content` tek caller (caption_generator) — imza değişikliği güvenli
- Migration gerekmez

**Doğrulama:**
- ✅ AST parse: `posts.py`, `caption_generator.py`, `prompt_builder.py` temiz
- ✅ `build_dynamic_content` grep: tek çağrı noktası (caption_generator:99), yeni kwarg güvenle geçildi
- ⏳ Canlı smoke test (deploy sonrası):
  - Görselli ürün + caption-gen → caption'da ürün adı doğal geçer, image_prompt ürünün kendisini tarif etmez (sadece sahne)
  - Görselsiz ürün + caption-gen → caption'da ürün adı geçer, image_prompt serbest tarif
  - `product_id=null` (mevcut akış) → regresyon yok
  - Farklı brand'in product_id → 404 "Ürün bulunamadı"

**Sonraki:** Sprint 8 — `/marka-ayarlari` frontend'e Ürün/Hizmet Kütüphanesi sekmesi (products CRUD + döküman yönetimi UI'sı).

## 2026-04-21 — Phase 9 Sprint 6: Image-edit routing (backend) ✅

**Kapsam:** `/icerik-olustur` post üretim endpoint'i artık `product_id` parametresini kabul eder. Ürünün `image_url`'i varsa fal.ai `nano-banana-2/edit` tetiklenir; yoksa mevcut FLUX text-to-image akışına düşer (S4 kararı). Yeni şablon yok, UI değişikliği yok — Sprint 5'te hazırlanan adapter altyapısını ilk tüketen sprint.

**Migration 027** (`shared/db/migrations/027_posts_product_id.sql`, prod'a uygulandı ✅):
```sql
ALTER TABLE social.posts
  ADD COLUMN IF NOT EXISTS product_id UUID NULL
  REFERENCES social.brand_products(id) ON DELETE SET NULL;
CREATE INDEX IF NOT EXISTS idx_posts_product_id
  ON social.posts(product_id) WHERE product_id IS NOT NULL;
```
`ON DELETE SET NULL` — ürün silindiğinde post kaydı kaybolmasın (görsel zaten R2'de üretilmiş).

**Değişen dosyalar (4):**

| Dosya | Değişiklik |
|-------|-----------|
| `app/models/schemas.py` | `PostGenerate.product_id: UUID \| None = None` eklendi |
| `app/core/security.py` | `assert_product_owned(db, user, product_id) -> dict` eklendi (5-level JOIN; products.py'deki local helper buraya taşındı — `assert_brand_owned` / `assert_post_owned` desenine uyum) |
| `app/routers/products.py` | Local `_assert_product_owned` silindi; security.py'den import edilen helper kullanılıyor (4 call site rename) |
| `app/routers/posts.py` | `generate_post`: `product_id` set ise `brand_products` fetch (brand_id guard'lı), INSERT'e `product_id` kolonu (15 → 16 value), fal.ai submit branch: `image_url` varsa `generate_image_edit(prompt, [image_url], brand_kit)`, yoksa `generate_image(prompt, aspect, brand_kit)` |

**Kararlar (mimari netleştirme):**
- **Şablon yok:** Kullanıcı onayı alındı — Sprint 6 sadece backend routing. Yeni `urun-hizmet-sablon` template'i ve wizard mode selector Sprint 9'a ertelendi.
- **Görsel opsiyonel (S4):** Ürünün `image_url`'i yoksa image-edit 400 döndürmek yerine FLUX text-to-image fallback. Kullanıcı ürün kütüphanesinde görsel yüklemeden de ürün-bağlamlı post üretebilir.
- **Overlay skip yok:** `imageTextOverlay` skip mantığı eklenmedi — mevcut `image_text_fields` mekanizması (Phase 8 Sprint 1 Part 3) zaten per-post kontrol sağlıyor.
- **Sahiplik kontrolü:** `product_id` için ayrı JOIN yerine `WHERE id=$1 AND brand_id=$2` kullanıldı — `assert_brand_owned` zaten çalışmış olduğu için `brand_id` güvenilir.

**Etki analizi:**
- Risk: düşük — `product_id` opsiyonel, NULL'da akış eski davranışla birebir
- Backward compat: N/A (yeni alan); INSERT kolon sayısı 15 → 16 ama değer `payload.product_id` yoksa None
- `ON DELETE SET NULL` sayesinde ürün silinince eski post'lar etkilenmez
- Migration additive; eski post'larda `product_id IS NULL`

**Doğrulama:**
- ✅ AST parse: `schemas.py`, `security.py`, `products.py`, `posts.py` sözdizimi temiz
- ✅ Migration 027 prod'a uygulandı (`\d social.posts` → `product_id` kolonu + partial index + FK cascade='SET NULL')
- ⏳ Canlı smoke test (deploy sonrası):
  - Ürün görseli olan bir `brand_products` kaydı ile `POST /posts/generate {product_id}` → post `generating`, webhook callback image-edit sonucu → `output_url` dolmalı
  - Görselsiz ürün (`image_url IS NULL`) ile aynı çağrı → FLUX text-to-image fallback, yine `ready`'ye gelmeli
  - Farklı brand'in `product_id`'si → 404 "Ürün bulunamadı"

**Sonraki:** Sprint 7 — caption endpoint'inin `product_id` bağlamını (ürün adı, açıklama, RAG dokümanları) prompt'a enjekte etmesi. `get_product_document_context()` helper'ı Sprint 4'te hazırlandı.

## 2026-04-21 — Coolify Redis servisi + REDIS_URL fix ✅

**Sorun:** Phase 4 Adım 4a'dan beri (Redis cache + rate-limit eklendi) backend'in `REDIS_URL` env'i Coolify'da hiç set edilmemişti; default `redis://localhost:6379` kullanılıyordu. Backend container içinde Redis yok → `get_redis().ping()` her çağrıda exception. `/health` sessizce `redis: error` raporluyordu; kimse fark etmemişti çünkü cache + rate-limit fail-open tasarlanmış (işlevsel kırılma yok, ama cache hit = 0, rate-limit de 0).

**Fix:**
- Coolify'da yeni Redis servisi: image `redis:7.2`, container `brxvzyj0yjtx77pcrbefgj0d`, internal DNS `brxvzyj0yjtx77pcrbefgj0d:6379`
- Backend `REDIS_URL` güncellendi: `redis://default:<pass>@brxvzyj0yjtx77pcrbefgj0d:6379/0`
- Backend redeploy → `/health` → `redis: ok` ✅ + `PING: True` doğrulandı

**Dikkat (Coolify tuzağı):** Redis servis form'undaki **Username** alanı yalnızca env label'ı (`REDIS_USERNAME`) olarak saklanıyor — Redis container'ına ACL user olarak **iletilmiyor**. `--requirepass` sadece `default` user'ın şifresini set eder. Bu yüzden `REDIS_URL`'de user kısmı **her zaman `default` veya boş** olmalı; `otomaix` gibi başka bir isim girilirse `AuthenticationError: invalid username-password pair` döner. `!` gibi özel karakterler şifrede varsa URL'de `%21` olarak URL-encoded kalmalı.

**Etki:** cache (brands 300s, holidays 86400s, avatar stock 3600s, JWT 300s) + rate-limit (posts/generate 20/sa, faceless 20/sa, suggest-ideas 30/sa, competitors 10/sa) + trends cache artık gerçekten devrede.

## 2026-04-21 — Phase 9 Sprint 5: Image-edit adapter altyapısı ✅

**Kapsam:** Phase 7 Sprint 7 media adapter registry'sine 5. modalite olarak `image_edit` eklendi. Ürün görseli + text prompt → düzenlenmiş görsel üretimi için fal.ai `nano-banana-2/edit` model adapter'ı. Caller wiring yok — Sprint 6 (`urun-hizmet-sablon` template'i) ve Sprint 9 (`/icerik-olustur` ürün mod wizard) bu altyapıyı tüketir.

**Değişen dosyalar (4):**

| Dosya | Değişiklik |
|-------|-----------|
| `app/core/config.py` | `IMAGE_EDIT_MODEL: str = "nano-banana-2-edit"` (default) |
| `app/services/media_adapters.py` | `ImageEditModelAdapter` Protocol + `NanoBananaV2EditAdapter` class + `IMAGE_EDIT_ADAPTERS` registry + `get_active_image_edit_adapter()` resolver |
| `app/services/fal_ai.py` | `_image_edit_adapter` modül-seviyesi resolve + `IMAGE_EDIT_MODEL` public export + `generate_image_edit(prompt, image_urls, brand_kit)` async wrapper |
| `app/routers/media_models.py` | `/media-models/active` response'a `image_edit: {key, model_id, supported_ratios: null}` eklendi |

**Adapter imzası:**
```python
class ImageEditModelAdapter(Protocol):
    model_id: str
    def build_args(self, prompt: str, image_urls: list[str]) -> dict[str, Any]: ...

class NanoBananaV2EditAdapter:
    model_id = "fal-ai/nano-banana-2/edit"
    def build_args(self, prompt, image_urls):
        if not image_urls:
            raise ValueError("image_urls boş olamaz — en az bir referans görsel gerekli")
        return {"prompt": prompt, "image_urls": image_urls}
```

**Kararlar (mimari netleştirme):**
- **i2v pattern'i (supported_ratios=None):** fal.ai `nano-banana-2/edit` snippet'inde `aspect_ratio` parametresi yok — çıktı input image'den türer (image-to-video ile aynı). Frontend aspect selector bu modalite için gizli kalacak (Sprint 9).
- **Çoklu referans görsel (`image_urls: list[str]`):** fal.ai çoklu input kabul ediyor. Adapter seviyesinde boş liste guard'ı dışında kısıt yok; caller (Sprint 6/9) ürün görseli + opsiyonel ek referans kombinasyonunu kendi kararına göre yönlendirir.
- **Brand prompt enrichment:** Mevcut `_build_image_prompt(prompt, brand_kit)` helper'ı (colors + style eklemesi) image_edit'te de kullanılır. Edit modelinde image_urls input dominant olduğu için marka renkleri prompt'ta pek etki etmeyebilir; tutarlılık adına paylaşım tercih edildi, sonradan Sprint 7/9 canlı testinde gözlem yapılabilir.
- **Caller wiring yok:** Adapter altyapı-only — `generate_image_edit()` wrapper'ı mevcut çağırıcısı olmayan scaffold (i2v `generate_video_from_image` aynı pattern'de). Sprint 6 (`urun-hizmet-sablon` Template spec'i) ve Sprint 9 (wizard) entegre edecek.

**Etki analizi:**
- Risk: sıfır — tamamen additive, mevcut 4 modalite adapter'ı dokunulmadı
- Backward compat: N/A (yeni modalite); `GET /media-models/active` response'a key eklenmesi frontend client'lar için opsiyonel (eski client key yoksa yokmuş gibi davranır)
- Migration gerekmez
- Env değiştiğinde (IMAGE_EDIT_MODEL) Coolify redeploy tetikler — adapter resolve modül import'unda yapılır (fail-fast)

**Doğrulama:**
- ✅ AST parse: 4 dosya temiz
- ✅ Canlı: `GET https://api.otomaix.com/media-models/active` → `data.image_edit = {key: "nano-banana-2-edit", model_id: "fal-ai/nano-banana-2/edit", supported_ratios: null}` (commit `08a43b0` deploy sonrası)
- ⏳ Gerçek edit çağrısı Sprint 6 (template `imageEditAdapter` alanı) + Sprint 9 (`/icerik-olustur` ürün mod) devreye girdiğinde test edilecek

**Sonraki:** Sprint 6 — Yeni template `urun-hizmet-sablon` + `_validate_templates()` assertion 23 → 24. Ürün kütüphanesi + image-edit pipeline'ını birleştiren ilk şablon; form fields (ürün seçimi, ana mesaj, stil yönergesi) + `imageEditAdapter: true` flag'i (yoksa default akış) + `defaults` (suggested CTA/hashtag) ile.

## 2026-04-21 — Phase 9 Sprint 4: Product Documents CRUD + RAG pipeline ✅

**Kapsam:** Ürüne bağlı doküman yükleme/listeleme/silme + mevcut RAG pipeline'ının (`document_processor.py`) ürün tablolarını da desteklemesi. Yeni dosya `app/routers/product_documents.py` (4 endpoint) + `document_processor.py` generalize (Seçenek A — `kind="brand"|"product"` kwarg). Sprint 7 caption entegrasyonu için hazır `get_product_document_context()` helper'ı şimdiden eklendi.

**Yeni dosya:** `app/routers/product_documents.py` (4 endpoint, ~175 satır):

| Method | Path | Guard |
|--------|------|-------|
| POST | `/product-documents` (multipart `product_id` + `file`) | `_assert_product_owned` (4-level JOIN) |
| GET | `/product-documents?product_id=` | `_assert_product_owned` |
| GET | `/product-documents/{doc_id}` | `_assert_doc_owned` (5-level JOIN) |
| DELETE | `/product-documents/{doc_id}` | `_assert_doc_owned` |

**`document_processor.py` generalization (Seçenek A):**
- `process_document(doc_id, brand_id, content, mime, db, *, kind="brand")` — `kind="product"` branch'i `social.product_documents` + `social.product_document_chunks` kullanır. `brand_id` artık `UUID | None` (product için None).
- `get_document_context(doc_ids, prompt, db, max_chars, *, kind="brand")` — `name_col` dallanması (`brand_documents.name` vs `product_documents.filename`), SELECT içinde `{name_col} AS name` ile alias.
- **Schema divergence:** `brand_document_chunks` içinde `brand_id` denorm kolonu var, `product_document_chunks`'ta yok (document_id → product_documents zinciri yeterli). INSERT branch'leri bu farkı handle ediyor.
- **Yeni helper** `get_product_document_context(product_ids, prompt, db)` — Sprint 7 caption-gen için: verilen product_id listesinden tüm doküman ID'lerini çeker, sonra `get_document_context(kind="product")` çağırır.

**Sahiplik zinciri** (5-level JOIN):
```
product_documents ⨝ brand_products ⨝ brands ⨝ workspace_members ⨝ accounts(JWT.sub)
```
Eşleşmezse 404 (varlık sızması önlenir — `assert_post_owned` deseni).

**R2 path:** `brands/{brand_id}/products/{product_id}/documents/{doc_id}_{filename}`. MAX 50MB (brand_documents ile aynı). Desteklenen MIME: PDF / Word / Excel / text (brand_documents ile aynı `ALLOWED_MIME_TYPES`).

**Response sanitization:** GET detayında `brand_id` (ownership leak hint) ve `raw_text` (MB ölçeğinde olabilir) response'tan pop'lanır. `has_raw_text: bool` + `chunk_count: int` meta alanları eklenir.

**Kararlar (mimari netleştirme):**
- **Generalize vs duplicate:** İlk iki seçenek (1: file'ı kopyala, 2: sadece import et ve duplicate INSERT yaz) yerine **Seçenek A** (generalize `process_document` with `kind` kwarg). Backward compat: `documents.py` mevcut çağrısı `kind` göndermediği için default `"brand"` ile çalışır.
- **Rate limit yok:** Upload/delete admin workload; Sprint 3 products CRUD'da da sadece create'e konuldu, docs akışında da hiç koymadık.
- **Chunk cascade:** DB FK (`product_documents → product_document_chunks ON DELETE CASCADE`). 527 chunk'lık büyük doküman silindiğinde orphan chunk kalmadığı canlı doğrulandı.
- **R2 cleanup best-effort:** DELETE sırasında `r2.delete(file_key)` try/except ile sarmalandı. R2 hatası DB kaydını geri getirmez.

**Etki analizi:**
- Risk: düşük — additive endpoint + mevcut `process_document` çağırıcısı değişmedi (default kwarg backward compat)
- Backward compat: N/A (yeni özellik)
- Migration gerekmez (026'da şema mevcut: `product_documents`, `product_document_chunks`)
- Import sırası `main.py`'de alphabetical korundu (posts → product_documents → products)

**Doğrulama (canlı smoke test, commit `cde8c85` prod deploy):**
- ✅ S1 Küçük TXT (3400 byte): `{mode:"raw", char_count:3400, chunk_count:0}` → HTTP 201
- ✅ S2 Büyük TXT (1.05MB, 972k char): `{mode:"chunks", chunk_count:527}` → HTTP 201
- ✅ S3 GET list: 2 doc, doğru `has_raw_text` + `chunk_count`
- ✅ S4 GET detay: `brand_id` + `raw_text` sanitize edildi
- ✅ S5 IDOR: yabancı doc_id + yabancı product_id → 404
- ✅ S6 DELETE cascade: 2 doc silindi, DB'de 0 orphan chunk doğrulandı (`SELECT COUNT(*) FROM product_document_chunks WHERE document_id IN (...)` → 0)
- ✅ S7 GET silinmiş doc → 404
- ✅ S8 List boş, product cleanup → DB'de 0 orphan product

**Sonraki:** Sprint 5 — `ImageEditModelAdapter` Protocol + `NanoBananaProEditAdapter` (image-edit akışı için ürün görseli input'u alan fal.ai adapter'ı, mevcut media_adapters.py altyapısına oturur).

## 2026-04-21 — Phase 9 Sprint 3: Products CRUD API (products.py) ✅

**Kapsam:** Marka ürün/hizmet kütüphanesi için CRUD endpoint'leri. `app/routers/products.py` (5 endpoint) + `schemas.py`'ye 3 Pydantic model + `main.py` router register. Sprint 2'de eklenen `check_product_quota` helper'ı ve migration 026 tabloları (`brand_products`, `product_documents`, `product_document_chunks`) kullanılıyor.

**Yeni dosya:** `app/routers/products.py` (5 endpoint):

| Method | Path | Guard | Rate limit |
|--------|------|-------|-----------|
| POST | `/products` | `assert_brand_owned` + `check_product_quota` | 30/saat |
| POST | `/products/{id}/image` | `_assert_product_owned` (inline JOIN) | — |
| GET | `/products?brand_id=&type=&active=` | `assert_brand_owned` | — |
| GET | `/products/{id}` | `_assert_product_owned` | — |
| PATCH | `/products/{id}` | `_assert_product_owned` | — |
| DELETE | `/products/{id}` | `_assert_product_owned` | — |

**Şemalar** (`app/models/schemas.py`):
- `ProductCreate` — `brand_id`, `type` ('product'|'service'), `name`, `description?`, `tags?=[]`, `is_active?=true`
- `ProductUpdate` — `name?`, `description?`, `tags?`, `is_active?` (**type immutable** — dönüşüm için yeni kayıt açılmalı)
- `ProductOut` — tüm kolonlar + `document_count` (LEFT JOIN subquery count)

**Kararlar (mimari netleştirme):**
- **Resim upload ayrı endpoint** (`POST /products/{id}/image`): create sırasında opsiyonel, multipart + JSON karışmasın. Yeni görsel yüklendiğinde eski R2 objesi silinir (best effort).
- **Hard delete**: DB cascade (products → documents → chunks) + R2 manuel cleanup (ürün görseli + tüm doküman dosyaları). Silme sırasında R2 hataları kaydı geri getirmez (log'a düşer, best effort).
- **Inline JOIN sahiplik** (`_assert_product_owned`): `brand_products ⨝ brands ⨝ workspace_members` → JWT.sub ile eşleşmezse 404 (varlık sızması önlenir — `assert_post_owned` deseni).
- **Rate limit yalnızca create'te**: PATCH/DELETE/GET/image upload sınırsız. Admin workload (toplu ürün güncellemesi) engellenmesin.
- **Cache yok**: Ürün listesi küçük, sık değişir. Cache invalidation karmaşıklığı değmez. `GET /billing/current` `products_per_brand` dict döndüğü için frontend ürün ekle/sil sonrası re-fetch eder (Sprint 8).

**R2 dosya yapısı:** `brands/{brand_id}/products/{product_id}.{ext}` (ext: jpg/png/webp). İzinli MIME: `image/jpeg|png|webp`, max 10MB.

**Etki analizi:**
- Risk: düşük — tamamen additive, mevcut endpoint/şema dokunulmadı
- Backward compat: N/A (yeni özellik)
- Migration gerekmez (026'da şema mevcut)
- `check_product_quota` HTTP 402 `plan_limit_reached` → frontend paywall modal'ı zaten bu detail yapısını bekliyor (B-1 pattern'i)

**Doğrulama:**
- ✅ AST parse: `products.py`, `schemas.py`, `main.py` sözdizimi temiz
- ⏳ Canlı smoke test (deploy sonrası):
  - `POST /products {brand_id, type:'product', name:'Test'}` → 201 + ürün dict
  - 11. ürün oluşturma denemesi → 402 `plan_limit_reached` (Pro plan 10 limit)
  - `POST /products/{id}/image` + JPEG → `image_url` dolu dönmeli
  - `GET /products?brand_id=...&type=service&active=true` → filtreli liste
  - `PATCH /products/{id} {name:'Updated'}` → güncellenmiş kayıt + `updated_at` trigger ile yeni zaman
  - `DELETE /products/{id}` → `{deleted:true, id}` + `GET` sonrasında 404

**Sonraki:** Sprint 4 — Product Documents CRUD (`app/routers/product_documents.py`): POST/GET/DELETE dokümanlar + raw_text + chunk/embed pipeline (mevcut `brand_documents` deseni, cascade delete otomatik).

## 2026-04-21 — Phase 9 Sprint 2: Plan quota entegrasyonu (billing.py) ✅

**Kapsam:** Marka başına ürün/hizmet kotası PLANS listesine işlendi, yeni `check_product_quota()` helper'ı eklendi, `GET /billing/current` response'una marka başına ürün sayacı ve maksimum limit eklendi. Tüm değişiklikler additive — mevcut kota akışları (`check_plan_limit`, `check_trend_quota`) değişmedi.

**Değişen dosya (tek):** `app/routers/billing.py`

**1. PLANS listesine `max_products_per_brand` alanı:**
| Plan | max_products_per_brand | features satırı |
|------|------------------------|-----------------|
| starter  | 10   | "10 ürün/hizmet" |
| pro      | 10   | "Marka başına 10 ürün/hizmet" |
| business | 10   | "Marka başına 10 ürün/hizmet" |
| agency   | None | "Sınırsız ürün/hizmet" |

Kullanıcı kararı: her plan marka başına 10 ürün (Starter 1 marka × 10 = 10, Pro 3 × 10 = 30, Business 10 × 10 = 100, Agency sınırsız). `is_active=false` ürünler sayımdan hariç.

**2. Yeni helper fonksiyonlar:**
- `_get_products_per_brand(account_id, db) -> dict[str, int]` — hesaba bağlı tüm aktif markalar için aktif ürün sayısı. Tek query (`brands ⨝ workspaces` + `LEFT JOIN brand_products` + `COUNT FILTER (WHERE is_active=true)`). Response: `{"<brand_id>": count, ...}`.
- `_get_plan_max_products(plan_id) -> int | None` — PLANS listesinden max'ı oku; bilinmeyen plan için fallback 10 (starter).
- `check_product_quota(account_id, brand_id, db) -> None` — HTTP 402 `plan_limit_reached` fırlatır; Agency (None) için kontrol atlanır. `check_plan_limit` deseninde, Sprint 3 products router'ında `POST /products` için kullanılacak.

**3. `GET /billing/current` response genişletildi:**
- `limits["max_products_per_brand"]` — plan limitinin frontend'de gösterimi için
- `usage["products_per_brand"]` — marka bazında sayaç dict (frontend marka ayarlarında "8/10 ürün kullanıldı" göstergesi için)

**Etki analizi:**
- Risk: düşük — PLANS değişikliği yalnızca field eklemesi (mevcut `id/name/price/...` okuyan kod etkilenmez)
- Backward compat: `max_products_per_brand` bilinmeyen plan için None değil 10 (fail-safe — sınırsız kaza önlemi)
- `plan_limits` DB tablosu yerine PLANS konstantı kullanıldı (TREND_QUOTAS pattern'i ile tutarlı, ayrı migration gereksiz)
- `GET /billing/current` response'a eklenen iki alan opsiyonel — eski frontend client'ları okumasa bile kırılmaz

**Doğrulama:**
- ✅ AST parse: `billing.py` sözdizimi temiz
- ⏳ Canlı smoke test (deploy sonrası):
  - `curl https://api.otomaix.com/billing/current` (JWT ile) → response'ta `limits.max_products_per_brand: 10` ve `usage.products_per_brand: {}` (henüz ürün yok) görünmeli
  - `GET /billing/plans` → tüm planlarda `max_products_per_brand` alanı görünmeli

**Sonraki:** Sprint 3 — Products CRUD API (`app/routers/products.py`): `POST /products` (30/saat rate limit + `assert_brand_owned` + `check_product_quota`), `GET /products?brand_id=`, `PATCH /products/{id}`, `DELETE /products/{id}`.

## 2026-04-21 — Phase 9 Sprint 1: brand_products DB migration (026) ✅

**Kapsam:** Ürün/hizmet kütüphanesi için veri tabanı iskeleti. Tamamen additive — mevcut tablolar değişmedi. Prod PostgreSQL'e uygulandı.

**Migration 026** (`shared/db/migrations/026_brand_products.sql`, prod'a uygulandı ✅):

**`social.brand_products`** — marka ürün/hizmet kütüphanesi:
- `id UUID PK`, `brand_id UUID FK → brands(id) ON DELETE CASCADE`
- `type TEXT CHECK IN ('product', 'service')` — ürün ve hizmet tek tabloda
- `name TEXT`, `description TEXT`, `tags TEXT[]`
- `image_url TEXT` (nullable — hizmet için opsiyonel), `image_key TEXT` (R2 object key)
- `is_active BOOLEAN DEFAULT true` — soft disable; quota sayımı sadece aktif ürünleri dahil eder
- Index: `idx_brand_products_brand_active` partial (WHERE is_active=true) — quota sorgusu için; `idx_brand_products_brand` genel listeleme için
- Trigger: `brand_products_updated_at` → `social.set_updated_at()` (migration 023 ile eklenen mevcut fonksiyon)

**`social.product_documents`** — ürüne bağlı dokümanlar (cascade delete):
- `id UUID PK`, `product_id UUID FK → brand_products(id) ON DELETE CASCADE`
- `filename`, `file_url`, `file_key`, `file_type`, `file_size BIGINT`, `raw_text TEXT` — mevcut `brand_documents` deseni ile aynı
- Tekil sahiplik (Seçenek A): bir doküman yalnızca bir ürüne bağlı; paylaşım için kullanıcı aynı dosyayı başka ürüne ayrıca yükler
- Index: `idx_product_documents_product(product_id, created_at DESC)`

**`social.product_document_chunks`** — RAG embedding chunks:
- `id UUID PK`, `document_id UUID FK → product_documents(id) ON DELETE CASCADE`
- `chunk_index INT`, `content TEXT`, `embedding vector(1536)` — `brand_document_chunks` ile tutarlı (OpenAI text-embedding-3-small)
- Index: `idx_product_chunks_document` btree + `idx_product_chunks_embedding` ivfflat (vector_cosine_ops, lists=100)
- ⚠️ ivfflat `lists=100` parametresi az data ile "low recall" uyarısı verir — üretim verisi arttıkça (>1000 satır) doğal şekilde iyileşir

**Cascade zinciri:** `brand sil → products sil → documents sil (R2 cleanup CRUD endpoint'inde) → chunks sil`

**Kararlar (mimari netleştirme — 2026-04-21 tartışma):**
- Ürün/hizmet tek tabloda `type` discriminator ile — ayrı tablo karmaşıklığı yerine kolon farkı
- Doküman sahipliği tekil (Seçenek A) — many-to-many yerine duplicate upload — cascade güvenli
- `is_active` quota'ya dahil değil — pasif ürünler depo gibi saklanabilir
- Plan quota (Sprint 2'de uygulanacak): Starter/Pro/Business = 10 ürün/marka, Agency = ∞
- Autoposting rotation + Telegram/mail onay akışları Phase 10'a ertelendi

**Etki analizi:**
- Risk: sıfır — additive, kullanıcı kodu henüz yok
- Rollback: `DROP TABLE ... CASCADE` zinciri güvenli (pilot veri yok)
- Mevcut `brand_documents` / `brand_document_chunks` akışları değişmedi

**Doğrulama:**
- ✅ `\d social.brand_products` → 11 kolon, 3 index (pk + 2), CHECK constraint, FK cascade, trigger
- ✅ `\d social.product_documents` → 9 kolon, 2 index, FK cascade
- ✅ `\d social.product_document_chunks` → 6 kolon, 3 index (btree + ivfflat + pk), FK cascade

**Sonraki:** Sprint 2 — `billing.py` `PLANS` listesine `max_products_per_brand` eklenmesi + `check_product_quota()` helper'ı + `GET /billing/current` ürün kullanım sayacı.

## 2026-04-20 — caption_generator json-repair + first_comment garantisi ✅

**Sorun 1 (Sentry):** Claude Opus 4.7 bazen bozuk JSON üretiyor (unquoted key, trailing comma → `JSONDecodeError: Expecting property name enclosed in double quotes: line 10 column 5`). `caption_generator.py:97` tek shot `json.loads(raw)` fail olunca `_fallback_response` devreye giriyordu.

**Sorun 2 (kullanıcı raporu):** IG/FB sekmelerinde "İlk Yorum (hashtag bloğu)" textarea tamamen kaybolmuştu. İki neden:
- Fallback response'ta `first_comment` field'ı hiç oluşturulmuyordu → frontend `platform_captions[p].first_comment !== undefined` koşulu false → textarea gizli
- Claude başarılı response'ta bile bazen `first_comment` atlıyor veya hashtag'leri caption gövdesine yazıyordu

**Çözüm (`app/core/caption_generator.py` + `requirements.txt`):**

1. **`json-repair==0.30.3`** kütüphanesi eklendi. `json.loads` fail olursa `json_repair.loads` recover eder. LLM çıktısı için yazılmış, unquoted key / trailing comma / smart quote / truncation hepsini temizler. Raw preview log'lanıyor (ilk 200 char) — gelecekteki tanı için.

2. **`_ensure_first_comment(data, template, platforms)`** post-process safeguard. useFirstComment=True platformlar (IG/FB/Threads) için:
   - `first_comment` yoksa/boşsa, caption'daki `#hashtag` regex'i (`re.compile(r'#[\wÇĞİÖŞÜçğıöşü]+', re.UNICODE)`) ile hashtag'ler çıkarılır, `first_comment`'e taşınır, caption body temizlenir
   - Hashtag yoksa en azından `first_comment: ""` set edilir → frontend textarea'sı her zaman görünür

3. **`_fallback_response(user_prompt, platforms, template=None)`** genişletildi. useFirstComment platformlar için `first_comment: ""` field'ı fallback'te de oluşturulur (template parametre opsiyonel, None gelirse PLATFORM_DEFAULTS'tan okuma yapılır).

**Etki analizi:**
- Risk: düşük — json-repair tek ek dependency, mevcut `json.loads` başarılı path'te çalışmaya devam eder (ilk deneme)
- Backward compat: tam — API response şekli değişmedi, sadece eksik field'lar dolduruluyor
- Performance: başarılı JSON'da json-repair çağrılmaz (ek maliyet yok); fail durumunda ~5-20ms recover

**Doğrulama:**
- ✅ AST parse temiz
- ✅ Regex semantic test (Türkçe karakterli hashtag, inline/sonda, boş caption) — `python3 -c` inline doğrulama
- ⏳ Canlı test: Claude bozuk JSON dönse bile caption gelmeli; IG/FB/Threads sekmelerinde first_comment textarea her zaman görünmeli (hashtag otomatik taşınmalı)

## 2026-04-20 — media_processor logo şeffaf padding trim + text word-wrap ✅

**Sorun (canlı test `ai-gorsel.jpg`):**
1. Sağ üst köşedeki logo görsel sınırından taşıyordu — "MyGoodShoes" yerine "MyGood..." görünüyor, sağ ucu kesik. Sebep: logo PNG'sinin içinde alpha=0 (şeffaf) kenar padding'i var. PIL resize bu padding'i de "logo içeriği" olarak sayıyor → gerçek görünür kısım sınırın dışına itiliyor.
2. Alt-sol text overlay auto-shrink min font'a inse bile tek satıra zorlanıp taşıyordu — "rahat, sade ve şık bir ayakkabı tercihiniz ise bu ayakkabıy..." son kelime kesik. Sebep: `add_text_overlay` auto-shrink sadece font size küçültüyor, **kelime bazında satır kırma yok**.

**Çözüm (tek dosya — `app/services/media_processor.py`):**

1. **`add_logo_overlay` — `logo.getbbox()` crop.** Logo açıldıktan ve RGBA'ya çevrildikten hemen sonra, resize öncesi:
   ```python
   trim_bbox = logo.getbbox()
   if trim_bbox:
       logo = logo.crop(trim_bbox)
   ```
   `getbbox()` alpha=0 kenarları (transparent padding) atar, logonun gerçek içerik bounding box'ını döner. Crop sonrası `logo.width/height` gerçek görünür boyutlardır; `target_w = bw * 0.20` scale'i doğru ölçüye uygulanır, köşe margin hesabı artık overflow yapmaz. Generic — her logoya uygulanır.

2. **`add_text_overlay` — word-wrap.** `_wrap(text, font, max_width)` inner fonksiyonu eklendi — `text.split()` kelimelere ayırır, `draw.textbbox` ile "current + ' ' + word" denemelerini yapar, `max_width` aşılırsa yeni satıra geçer. Auto-shrink loop'unda her `text_lines` entry'si `_wrap(line, font, usable_w)` ile çoklu segmente bölünür, her segment ayrı `rendered` entry olur. `rendered` tuple yapısı `(text, w, h, is_title)` olarak genişletildi (is_title flag'i title font'unu rendering'de korur).

**Etki analizi:**
- Risk: düşük — tek dosya, API imzaları değişmedi, her iki fonksiyon generic
- Performance: `getbbox()` ~1ms, `_wrap` worst case ~O(kelime sayısı × textbbox çağrısı) ~5-15ms
- Backward compat: tam — eski kısa metinler (ör. "SporXL" + "79 TL") ilk wrap denemesinde tek segment döner, davranış değişmez
- Ekstreme edge: tek kelime 40+ char (yapıştırılmış URL gibi) — wrap bölemez, auto-shrink min font'a iner, nihayetinde yine overlay sınırına sığmazsa en iyi efforttan sonra silik basılır

**Doğrulama:**
- ✅ AST parse temiz
- ✅ Canlı test: `ai-gorsel.jpg` yeni versiyonu — logo sağ üst köşede tam, text alt-sol 3 satıra düzgün sarmış, luminance doğru karar vermiş (koyu sokak zemini → beyaz fill + siyah stroke)

## 2026-04-20 — Logo-text çakışma + luminance-aware text rengi ✅

**Sorun (canlı test — `ai-gorsel.jpg`):** Mavi sneaker görselinin alt kısmında:
1. Kullanıcı marka ayarında logo konumunu `bottom-right` seçmiş; text overlay de `bottom-left` bölgesinde — ikisi aynı yatay şeride düşüyor, metnin sağ kenarı logonun sol kenarına değiyor / üst üste biniyordu.
2. Metin her durumda beyaz (`fill=(255,255,255)`, `stroke=(0,0,0)`). Açık arka plan (bej/beyaz sneaker, açık zemin) gelirse beyaz metin neredeyse görünmez.

Kullanıcı logo pozisyonunu default-override etmeyi reddetti — "logo pozisyonu marka ayarından kullanıcının tercihi, oraya dokunma." Yani çakışma çözümü text overlay tarafında yapılmalı.

**Çözüm:** İki bağımsız mekanik, ikisi de `media_processor.py` içinde:

**A) Logo bbox'ı text overlay'e taşıma:**
- `add_logo_overlay` dönüş tipi `str | None` → `tuple[str, tuple[int,int,int,int]] | None`. `(uploaded_url, (x, y, w, h))` döner.
- `apply_brand_processing` logo stage sonucundan `logo_bbox` tuple'ını ayıklar, sonraki `add_text_overlay` çağrısına `excluded_bbox=logo_bbox` olarak geçer.
- `add_text_overlay` yeni parametre `excluded_bbox: tuple[int,int,int,int] | None = None`. Logo ve text'in **aynı yatay şerit** (üst yarı vs alt yarı) olup olmadığını kontrol eder:
  ```python
  logo_in_bottom_half = (ey + eh/2) > (bh/2)
  same_strip = logo_in_bottom_half == is_bottom
  ```
  Aynı şeritteyseler, text bölgesi logonun dik bandından çıkacak şekilde daraltılır:
  - Text sağa hizalıysa (`is_right`) ve logo sol yarıdaysa → `text_left = max(text_left, ex+ew+pad)`
  - Text sola hizalıysa ve logo sağ yarıdaysa → `text_right = min(text_right, ex-pad)`
  - `usable_w = text_right - text_left` → auto-shrink loop'unun parametresi. Text daraltılmış bölgeye sığar, logo kesişmez.
- Farklı şeritteyseler (ör. logo üst-sağ, text alt-sol) hiçbir daraltma yapılmaz — eski davranış.

**B) Luminance-aware metin rengi:**
- Ölçüm fazı (auto-shrink) bittikten sonra text'in gerçekte basılacağı bbox hesaplanır (`x_start..x_start+max_w`, `y_start..y_start+total_h` + `pad=4`).
- `base.crop(sample_box).convert("L")` ile o bölgenin grayscale kopyası alınır, `ImageStat.Stat(...).mean[0] / 255.0` ile ortalama luminance bulunur.
- Eşik: `mean_lum > 0.5` → koyu metin (siyah fill, beyaz stroke); aksi halde eski davranış (beyaz fill, siyah stroke).
- `ImageStat` import'u `PIL` satırına eklendi.

**MVP scope:** Her iki fix tüm image post'larda devrede (şablon ayrımı yok). Brand kit'teki text overlay + logo overlay birbirini bilmiyordu; artık biliyor.

**Etki analizi:**
- Risk: düşük — `add_logo_overlay` dönüş tipi değişti ama tek caller (`apply_brand_processing`) güncellendi. Başka import yok (grep: media_processor'ın dışından çağrılmıyor).
- Logo None dönerse `logo_bbox` da None kalır, `add_text_overlay` eski davranışa fallback (bbox exclusion yok).
- Auto-shrink min font size koruması zaten var → daraltılmış bölge çok küçükse text en fazla `min_body_size`'a iner, taşmaz.
- Luminance sampling worst case 1024×~200px grayscale convert + ortalama = <20ms.

**Doğrulama:**
- ✅ AST parse temiz
- ⏳ Canlı test:
  - Logo bottom-right + text bottom-left → text sağa taşmayı kesmeli, logoya dokunmamalı
  - Açık arka plan (ör. beyaz/bej) → metin **siyah + beyaz stroke** çıkmalı (mevcut beyaz-on-beyaz görünmezlik giderilmeli)
  - Koyu arka plan (mevcut test — mavi sneaker) → metin **beyaz + siyah stroke** (mevcut davranış korunmalı)
  - Logo top-right + text bottom-left (farklı şerit) → bbox exclusion devrede değil, metin tam genişlikte

## 2026-04-20 — Text overlay auto-shrink (taşma koruması) ✅

**Sorun:** `add_text_overlay` sabit font size (`bw * 0.055`) + word-wrap yok. Uzun metinler (ör. 33-char ürün adı) 1024px görsele taşıyordu; sağ hizalı modda `x` negatife bile gidebiliyordu. `product_name` maxLength=50, `price` maxLength=12 → worst case ciddi taşma.

**Çözüm:** `add_text_overlay` içine **auto-shrink döngüsü** eklendi. Başlangıç `max_body_size = max(24, int(bw * 0.055))`; en geniş satır `usable_w = bw - 2*margin` alanını aşıyorsa font %10 küçültülüp yeniden ölçülür. Alt sınır `min_body_size = max(20, int(bw * 0.03))` — okunabilirlik eşiği. Title (satır 0) her zaman body'nin %25 üstünde → hiyerarşi korunur. Rendering loop'u değişmedi, sadece ölçüm fazı iteratif oldu.

**Örnek (1024px, margin 40):** 33-char title → başlangıç 56px'te ~1180px, usable 944px aşılıyor → 50px → 45px → 42px → sığar. Kullanıcı için şeffaf, görsel taşmadan üretiliyor.

**Edge case:** Tek kelime 40+ char (ör. yapıştırılmış URL) → min 20px'te bile taşabilir. Şimdilik "kalır" (taşan kenar crop'lanır değil, overlay'in kendisi görsel sınırları içinde çizildiği için silik görünüm). Ellipsis truncate canlı testte sorun çıkarsa eklenir.

**Etki analizi:**
- Risk: düşük — iteratif ölçüm, ek bir PIL draw yok (her iteration'da sadece `textbbox` çağrısı, gerçek `draw.text` tek kez çalışır)
- Performance: worst case 4-5 iteration × O(n) textbbox = <50ms; yine webhook post-process içinde, kullanıcı deneyimi etkilenmez
- Backward compat: kısa metinler (mevcut test case'i "SporXL" + "79 TL") ilk iteration'da exit → davranış aynı

**Doğrulama:**
- ✅ AST parse temiz
- ⏳ Canlı test: 30+ char ürün adı ile test → görselin sol alt köşesindeki metin görsel sınırları içinde tutulmalı, taşmamalı; fontlar mevcut kısa case'den biraz daha küçük ama net olmalı

## 2026-04-20 — Logo overlay boyutu düzeltmesi (canlı test feedback) ✅

**Sorun:** Canlı test (MyGoodShoes + Ürün Kartı) sonucunda sağ alt köşedeki logo çok küçük çıktı, zar zor görünüyor. Kök neden `app/services/media_processor.py:add_logo_overlay` fonksiyonunda `logo.thumbnail((max_w, max_h), Image.LANCZOS)` kullanılıyordu. PIL `thumbnail()` **sadece küçültür, büyütmez** — kullanıcının logo PNG'si zaten küçükse (ör. 200×50 px) olduğu gibi kalıyor, ana görselin %20'sine scale edilmiyordu.

**Çözüm:** `thumbnail` yerine aktif `Image.resize` — hedef genişlik `base.width * 0.20`, aspect ratio korunarak hem küçültür hem büyütür. Yüksek logo için `base.height * 0.20` üst sınırı ayrıca kontrol ediliyor (çok uzun dikdörtgen logo senaryosu için güvenlik).

```python
target_w = int(base.width * 0.20)
max_h = int(base.height * 0.20)
ratio = target_w / logo.width
target_h = int(logo.height * ratio)
if target_h > max_h:
    ratio = max_h / logo.height
    target_w = int(logo.width * ratio)
    target_h = max_h
logo = logo.resize((max(1, target_w), max(1, target_h)), Image.LANCZOS)
```

**Etki analizi:** Risk düşük — tek fonksiyon, tek caller (`apply_brand_processing`), imza değişmedi. Büyük logolar zaten küçültülüyordu (behavior korundu), küçük logolar artık büyütülüyor (bug fix).

**Doğrulama:**
- ✅ AST parse temiz
- ⏳ Canlı test: AI görsel üretiminden sonra logo sağ alt köşede belirgin boyutta (≈%20 görsel genişliği) olmalı, önceki testteki gibi zar zor görünmemeli

## 2026-04-20 — Phase 8 Sprint 2: Varsayılan görsel şablonu (`genel-gorsel-sablon`) ✅

**Kapsam:** `/icerik-olustur` "Görsel → Devam et" akışında şablon grid'i atlanıp tek bir genel amaçlı varsayılan şablon otomatik açılacak şekilde backend scaffolding. Kullanıcının uzun şablon listesine bakma zorunluluğu kalkıyor, serbest mod'a yakın ama caption-first pipeline + overlay + CTA yönlendirme disiplini korunuyor. Carousel/Video/ÖzelGün/Alıntı tipleri bu sprint'te dokunulmadı (kullanıcı kararı — test edilmemiş ekosistem).

**Değişen dosyalar (2):**

- `app/core/templates_data.py` — `TEMPLATES["genel-gorsel-sablon"]` entry (Genel section'da, `genel-hakkimizda`'dan önce, `order=1`):
  - `sectors=["*"]`, `contentTypes=["image"]`
  - Form alanları (4):
    - `ana_konu` (text, required, maxLength 120, group "Konu")
    - `one_cikan_ozellik` (text, optional, maxLength 200, group "Konu")
    - `cta_url` (url, optional, group "Yönlendirme")
    - `cta_label` (text, optional, defaultValue "Şimdi Keşfet", maxLength 40, group "Yönlendirme")
  - `imageTextOverlay=ImageTextOverlaySpec(fields=["ana_konu","one_cikan_ozellik"], position="bottom-left")` — Phase 8 Part 3 overlay pipeline'ı devrede
  - `output.aspectRatioSuggestion="1:1"`
  - `prompt.guidance` — görsel yönergesi (marka renkleri HEX, logo/rozet/metin yasak), caption formülü (Hook → Özellik → CTA), CTA kuralı platform'a göre (IG/TikTok → "profilimizdeki link" + first_comment URL, LinkedIn/FB/TW → direkt URL caption'a)
  - `prompt.priority=["form_fields", "brand_kit", "rag_docs"]`
  - `platformOverrides` yok — `PLATFORM_DEFAULTS` (prompt_builder.py) otomatik merge eder
- `app/main.py` — `_validate_templates()` assertion 22 → 23 (yoksa uygulama fail-fast boot etmez)

**Frontend etkisi:** `lib/api/templates.ts::fetchTemplateById` kullanılıyor; "Devam Et" butonu image type için async fetch + `handleSelectTemplate` ile direkt form'a düşüyor. Detay: frontend/CLAUDE.md.

**Etki analizi:**
- Risk: düşük — sadece additive template + assertion bump.
- Backward compat: carousel hâlâ `TemplateGrid`'e düşüyor (multi-template), legacy video/special_day/quote akışları değişmedi.
- `PLATFORM_DEFAULTS` her platform için varsayılan caption kuralı sağladığından, `platformOverrides` olmayan yeni şablon için de TikTok/LinkedIn/Twitter/Facebook/YouTube sekmelerinde dolu caption gelir.

**Doğrulama:**
- ✅ AST parse: `templates_data.py`, `main.py` sözdizimi temiz
- ✅ Regex count: `TEMPLATES[...]=Template(` → 23 entry
- ⏳ Canlı test: `/icerik-olustur` "Görsel" seç → "Devam Et" → şablon grid'i görünmeden doğrudan "Ana Konu + Öne Çıkan Özellik + Yönlendirme Linki + Çağrı Metni" form'u açılmalı. Caption-first pipeline (Gönderi Metni Üret → düzenle → Görseli Üret) çalışmalı, logo overlay + text overlay + brand kit uygulanmalı.

**Sonraki (kullanıcı onayıyla):** Canlı doğrulama → carousel/video/special_day/quote için default şablon genişletmesi (her biri için ayrı ID, aynı pattern).

## 2026-04-20 — Phase 8 Sprint 1 Part 3: Template image text overlay (PIL post-process) ✅

**Sorun:** FLUX Türkçe karakterleri güvenilir render edemiyor — image_prompt'a "SporXL 79 TL" yazdırmak risk (rastgele seçilen glyph'ler, bozuk harfler). E-ticaret ürün kartı, alıntı, infografik gibi "görselin üstünde metin olmalı" şablonları için caption'a bırakmak yetmiyor — insan görsel posta bakınca fiyatı/ürün adını direkt görsin istiyor.

**Çözüm:** AI görsel üretiminden SONRA Pillow (PIL) ile metin overlay uygulanıyor. Şablon sahibi hangi form alanlarının overlay basılacağını belirler (`imageTextOverlay.fields`), kullanıcı tercihine göre subset seçebilir (per-post override).

**MVP scope:** Sadece `eticaret-urun-karti` şablonu için aktif; `["product_name", "price"]` varsayılan, `bottom-left` pozisyon. Canlı doğrulamadan sonra diğer şablonlara genişletilir.

**Backend değişiklikler:**

- **Migration 025** (`shared/db/migrations/025_posts_image_text_fields.sql`, prod'a uygulandı ✅):
  ```sql
  ALTER TABLE social.posts
    ADD COLUMN IF NOT EXISTS image_text_fields TEXT[] DEFAULT NULL;
  ```
  NULL = template default'u (`imageTextOverlay.fields`); `[]` = kullanıcı hepsini kapattı (basma); `[...]` = açık subset.

- `app/models/templates.py` → `ImageTextOverlaySpec` Pydantic modeli + Template'e `imageTextOverlay: Optional[ImageTextOverlaySpec]`.
- `app/models/schemas.py` → `PostGenerate.image_text_fields: list[str] | None`.
- `app/core/templates_data.py` → `eticaret-urun-karti` Template'ine `ImageTextOverlaySpec(fields=["product_name", "price"], position="bottom-left")` eklendi.
- `app/services/media_processor.py`:
  - `_TEXT_OVERLAY_FONT_CANDIDATES` + `_load_overlay_font(size)` — DejaVu Sans Bold → Regular → PIL default fallback zinciri (`fonts-dejavu-core` Dockerfile'da kurulu).
  - `add_text_overlay(image_url, text_lines, position, post_id, brand_id)` — beyaz fill + 3px siyah stroke, ilk satır title (1.25x), diğerleri body. Font size `max(24, int(bw * 0.055))`, margin `max(24, int(bw * 0.04))` — görselin genişliğine göre scale eder. R2 path: `brands/{brand_id}/posts/generated/{post_id}_text.jpg`.
  - `apply_brand_processing()` imzası genişletildi: `text_overlay_lines: list[str] | None = None, text_overlay_position: str = "bottom-left"`. Logo overlay'den SONRA uygulanıyor (logo'lu görselin üzerine yazı basılır).
- `app/routers/webhooks.py`:
  - `post.template_id` ile template lookup → `imageTextOverlay` tanımlıysa effective fields belirle (`post.image_text_fields` NULL değilse override, değilse `spec.fields`).
  - `template_fields` JSON'ı parse et (defansif: hem dict hem str case).
  - `formFields`'ten suffix_map oluştur → her aktif field için `f"{val_str} {suffix}".strip()` ("79 TL") satırını derle.
  - Satırları `apply_brand_processing(text_overlay_lines=lines, text_overlay_position=spec.position)` ile pipeline'a geçir.
- `app/routers/posts.py` → `generate_post()` INSERT 14 → 15 kolon (`image_text_fields` + `$15` parametresi).

**Frontend değişiklikler:** `lib/templates.types.ts` + `components/templates/DynamicForm.tsx` (overlay field seçim kartı) + `app/(dashboard)/icerik-olustur/page.tsx` (state + payload). Detay: frontend/CLAUDE.md.

**Etki analizi:**
- Risk: düşük — opt-in. Template'inde `imageTextOverlay` tanımlı değilse hiç çalışmaz. Kullanıcı checkbox'ları kapatırsa (`[]`) sessiz geçer.
- Font fallback: DejaVu yoksa PIL default font devreye girer (çok küçük ve bitmap, Türkçe karakterler rendered olmayabilir). Prod Dockerfile `fonts-dejavu-core` kuruyor — problem olmaması bekleniyor.
- Backward compat: migrasyon öncesi post'larda `image_text_fields IS NULL` + template'inde `imageTextOverlay=None` → hiçbir değişiklik gözlenmez.

**Doğrulama:**
- ✅ AST parse temiz (Python), TypeScript compile temiz (`tsc --noEmit` exit 0)
- ✅ Migration 025 prod'a uygulandı (`social.posts.image_text_fields text[]`)
- ⏳ Canlı test: MyGoodShoes + Ürün Kartı → `product_name=SporXL`, `price=79` → üret → görselin sol alt köşesinde "SporXL" (büyük, title) + "79 TL" (küçük) beyaz + siyah stroke ile okunabilir olmalı

## 2026-04-20 — Görsel kalitesi + kullanıcı isteği önceliği (Phase 8 polish) ✅

**Sorunlar (canlı test, MyGoodShoes e-ticaret brand):**
1. AI görselde kendiliğinden "MyGoodShoes" logosu sağ üst köşeye basılıyor (biz zaten webhook post-process'inde gerçek logo ekliyoruz — FLUX hayal logo uydurmasın).
2. Ürünün üstünde/etrafında "SportXL" / "SporXL" metni yazı olarak render ediliyor (product_name prompt'a sızıyor).
3. "Rahat · Kaliteli · Şık" gibi Türkçe özellik metinleri görselde yazı olarak basılıyor (FLUX Türkçe kelime görürse yazıya döküyor).
4. Kullanıcı "ek talimat" alanına "tenis elbiseli bir kadın spor ayakkabı giyerken göster" yazdı, Claude prompt'a ekledi ama template default'u "focus on the sneakers" yüzünden FLUX tight crop yaptı — model+elbise cropped out.

**Çözüm (3 backend dosyası + 1 frontend dosyası):**

### A) `app/core/caption_generator.py` — image_prompt için katı kurallar
`_build_output_format_instruction()` çıktı formatı talimatına 6 maddelik kural bloğu eklendi:
1. **Marka adı YASAK** — product marka adı image_prompt'ta geçmesin (text-to-image modeli marka adını görsele metin olarak basıyor)
2. **Spesifik ürün adı YASAK** — "SporXL", "iPhone 15" gibi model adları yerine genel kategori kullan ("running sneakers", "smartphone")
3. **Türkçe metin YASAK** — "Rahat · Kaliteli · Şık" gibi kelimeleri tarif etme, özellikleri görsel ima ile ver (comfort → relaxed pose, quality → premium materials texture)
4. **Logo/rozet/metin katmanı YASAK** — "brand logo badge in corner", "feature badge", "text overlay" tarif etme; gerçek logo post-process'te ekleniyor
5. **Ürün odağı** — e-ticaret ürün kartlarında ana özne ürün (shoe product shot, close-up); lifestyle istenmiyorsa model tarif etme
6. **Format önerisi** — "Professional product photography of [generic category], [composition], clean studio background in [brand HEX], [lighting], [texture]. No text, no logos, no overlays."

Kurallar Tier 3'te (cache'siz) → yeni kural eklendiğinde anında devreye giriyor, cache invalidation gerekmiyor.

### B) `app/core/templates_data.py` — eticaret-urun-karti guidance cleanup
- Silindi: "marka logosu köşede, fiyat/indirim rozeti görünür konumda" (FLUX'a logo/rozet çizdiren ifade)
- Eklendi: "İnsan modeli, lifestyle sahnesi, elbise/kıyafet vurgusu KULLANMA — ürün küçükse (ayakkabı, takı, telefon vb.) yakın plan/hero angle kullan."
- Eklendi: "logo, marka rozeti, fiyat rozeti, özellik rozeti, metin katmanı veya yazı TARIF ETME"

### C) `app/core/prompt_builder.py` — kullanıcı isteği en yüksek öncelik
**Sistem prompt'a eklenen kural** (`_SYSTEM_RULES`):
> ⚠️ KULLANICI İSTEĞİ HER ZAMAN ÖNCELİKLİDİR: Prompt'ta "KULLANICI İSTEĞİ" başlığı altında gelen metin, şablon varsayılanlarını, sektör rehberini ve priority sıralamasını GEÇERSİZ KILAR. Kullanıcı "tenis elbiseli kadın göster" diyorsa ürün odaklı şablon default'unu bırak ve kullanıcının istediği sahneyi (model, sahne, kompozisyon, arka plan) image_prompt'a AYNEN yansıt.

**`build_dynamic_content()` yeniden sıralandı** — Tier 3 artık şu sırayı izliyor:
1. KULLANICI İSTEĞİ (EN YÜKSEK ÖNCELİK) — en tepede, belirgin header ile
2. YAPISAL VERİLER — önceki "EN YÜKSEK ÖNCELİK" etiketi kaldırıldı, artık user_prompt'un altında
3. REFERANS DOKÜMAN
4. ÖNCELİK SIRASI — template.prompt.priority listesinin başına zorla `user_prompt` eklenir, dup'lanırsa dedupe edilir

Önceden user_prompt alt sıradaydı ve "EK TALİMATI" gibi daha yumuşak bir etiketle geliyordu, bu yüzden Claude şablon default'larını ön plana çıkarıyordu. Yeni sıralama ve etiket user isteğini öncelikli zorluyor.

### D) Frontend — `/icerik-olustur` "Ek Talimat" rename
Detay: frontend/CLAUDE.md.

**Etki analizi:**
- Risk: düşük — sadece prompt üretimi etkilenir, API sözleşmesi değişmedi
- Tier 1 sistem prompt değişikliği cache invalidation gerektirir (ilk çağrı cache miss, sonrakiler hit) — beklenen davranış
- user_prompt zaten opsiyonel alan; boş olduğunda Tier 3 hiç user_prompt bloğu içermez (backward compat)

**Doğrulama:**
- ✅ AST parse: prompt_builder.py, caption_generator.py, templates_data.py sözdizimi temiz
- ⏳ Canlı test: MyGoodShoes + Ürün Kartı + "tenis elbiseli kadın spor ayakkabı giysin" → görselde model + elbise + ayakkabı görünmeli (crop olmamalı), üzerinde hayal logo/Türkçe metin olmamalı

## 2026-04-20 — Phase 8 Sprint 1 Part 2: Per-post logo filigran override ✅

**Sorun:** Marka-seviyesi `brand_kit.logo_overlay.enabled` tek doğru var — kullanıcı bir içerik için istisna yapmak isterse (örn. temiz mockup görseli, logosuz ürün fotoğrafı tarzı sonuç) önce marka ayarlarından filigranı kapatıp sonra geri açmak zorunda kalıyordu. Kullanıcı "görsel üretimlerinde logo kullan veya kullanma tercihini kullanıcıya sorduk mu?" diye haklı olarak sordu — cevap hayırdı.

**Çözüm:** `social.posts` tablosuna `use_logo_overlay BOOLEAN NULL` kolonu eklendi. NULL = marka default'una uy, true/false = bu post için açıkça override. `/icerik-olustur` sayfasında image/carousel akışlarında aspect ratio'nun altında "Logo filigranı bas" switch'i — marka default'unu değiştirmeden sadece o post için tercihi değiştirir.

**Backend değişiklikler:**

- **Migration 024** (`shared/db/migrations/024_posts_use_logo_overlay.sql`, prod'a uygulandı ✅):
  ```sql
  ALTER TABLE social.posts
    ADD COLUMN IF NOT EXISTS use_logo_overlay BOOLEAN DEFAULT NULL;
  ```

- `app/models/schemas.py` → `PostGenerate` modeline `use_logo_overlay: bool | None = None` eklendi.

- `app/routers/posts.py` → `generate_post()` INSERT'üne kolon eklendi ($14 parametresi).

- `app/routers/webhooks.py` → fal webhook brand_kit uygulama aşamasında post'un `use_logo_overlay` değeri okunuyor; NULL değilse `brand_kit` kopyası üzerinde `logo_overlay.enabled` alanı override ediliyor (orijinal brand_kit dict asla mutate edilmez — shallow copy + `{**existing_overlay, "enabled": ...}` ile nested dict de ayrı copy):
  ```python
  post_use_logo = post["use_logo_overlay"]
  if post_use_logo is not None:
      existing_overlay = brand_kit.get("logo_overlay") or {}
      brand_kit["logo_overlay"] = {**existing_overlay, "enabled": bool(post_use_logo)}
  ```

**Frontend değişiklikler (`/icerik-olustur/page.tsx`):**

- Yeni state: `useLogoOverlay: boolean | null` — null = marka varsayılanına uy.
- `currentBrand?.id` değişince `GET /brands/{id}` çağrısı ile `brand_kit.logo_overlay.enabled` okunur ve switch başlangıç değeri olarak set edilir.
- Switch UI iki yerde (aspect ratio'nun altında): template mode (`phase='form' + selectedTemplate`) ve free-form mode (`mode='free' + phase='form'`). Yalnızca `currentBrand?.logo_light_url || logo_dark_url` durumunda görünür (logo yoksa filigran anlamsız).
- Video/özel gün/alıntı akışlarında switch YOK (bu tipler için logo overlay pipeline'ı devreye girmez).
- `handleGenerate` image/carousel payload'ına `use_logo_overlay: useLogoOverlay` eklendi.

**Etki analizi:**
- Risk: düşük — kolon NULL default'lu, eski client'lar payload'da `use_logo_overlay` göndermezse veya null gönderirse marka default'u uygulanır (mevcut davranış korunur).
- Backward compat: `content_type='video' | 'special_day' | 'quote'` akışları değişmedi; legacy autoposting n8n trigger `use_logo_overlay` göndermiyor → NULL → marka default.
- `PATCH /brands/{id}/kit` ile marka-seviyesi `logo_overlay.enabled` değiştirildiğinde yalnızca sonraki default fetch'te görünür; mevcut üretilmiş post'lar zaten `use_logo_overlay` NULL kaydedildiği için yeni default'a uyarlar.

**Doğrulama:**
- ✅ AST parse (`schemas.py`, `posts.py`, `webhooks.py`) temiz
- ✅ TypeScript compile temiz (`tsc --noEmit` exit 0)
- ✅ Migration prod'da çalıştırıldı, kolon görünür (`\d social.posts`)
- ⏳ Canlı test (Sprint 1 Part 1 ile birlikte yapılacak):
  - Marka default = false → `/icerik-olustur` açıldığında switch kapalı başlar, üretim logosuz
  - Switch açıp üret → sadece o post'a logo basılır, marka ayarları değişmez
  - Tersi: marka default = true, switch kapatıp üret → o post logosuz, marka ayarı true kalır
  - Logo olmayan marka → switch hiç görünmez

## 2026-04-20 — Phase 8 Sprint 1: Logo varyant auto-selection + prompt improvements ✅

**Kapsam:** İki paralel problemi tek sprint'te çözdük — (a) fal.ai webhook'ta `logo_light_url` hardcoded kullanılıyor, koyu logo hiç devreye girmiyor (MyGoodShoes testinde açık arka planda beyaz logo üzerine beyaz logo basılıyordu); (b) `build_brand_context()` Tier 2'de `website_url` eksik ve image_prompt brand color enforcement yok (Claude marka renklerini yok sayıp beige/off-white studio renkleri kullanıyordu).

### A) Luminosity-based logo variant selection

**Değişen dosyalar (2):**

- `app/services/media_processor.py`:
  - `_compute_luminosity(bytes) -> float | None` — PIL ile `Image.convert("L")` (grayscale **kopya**) + `ImageStat.mean` → 0.0-1.0 arası ortalama parlaklık. **Orijinal bytes asla değiştirilmez** (grayscale sadece ölçüm için memory'de ayrı obje).
  - `_pick_logo_variant(bg_bytes, light_url, dark_url) -> str | None`:
    - Tek varyant varsa o döner (fallback)
    - Luminosity > 0.5 (açık arka plan) → `logo_dark_url`
    - Luminosity ≤ 0.5 (koyu arka plan) → `logo_light_url`
    - Hesaplama başarısızsa light fallback
  - `apply_brand_processing()` imzası değişti: `logo_url` param'ı → `logo_light_url` + `logo_dark_url` (iki ayrı param). Fonksiyon içinde arka plan httpx ile fetch edilir, `_pick_logo_variant()` ile varyant seçilir, sonra `add_logo_overlay()`'e chosen URL iletilir. Fetch başarısızsa `light or dark` fallback.

- `app/routers/webhooks.py`:
  - Brand SELECT query'sine `logo_dark_url` eklendi (önceden yalnızca `logo_light_url`)
  - `apply_brand_processing()` çağrısı iki URL'i de geçiyor

**Etki analizi:**
- Risk: düşük — tek caller (`webhooks.py`) imza değişikliğine uyumlu. Luminosity hesaplaması ek bir HTTP fetch (R2'den background image) gerektirir ama bu zaten `add_logo_overlay` içinde de yapılıyordu — net +1 fetch per post (R2 cache'li olduğu için marjinal maliyet).
- Backward compat: markanın tek bir logosu varsa (sadece light veya sadece dark) fallback devreye girer — davranış önceki state ile aynı.

### B) Prompt improvements — Tier 2 brand context

**Değişen dosya:** `app/core/prompt_builder.py` → `build_brand_context()`:

1. **website_url eklendi** (`brand.get("website_url")` varsa): "Marka web sitesi: {url}" satırı Tier 2'ye girer.

2. **GÖRSEL ÜRETİM KURALI bloğu** (colors set edilmişse): Claude'a image_prompt üretirken marka renklerini HEX kodları ile **zorunlu** kullanması söyleniyor. Beige / off-white / pastel / genel stüdyo tonları yasak. Örnek kalıp verildi ("background in {marka mor tonu #HEX}, accent lighting with {ikincil renk #HEX}").

**Caller analizi:**
- `generate-caption` endpoint (`posts.py:211`) zaten `SELECT b.*` kullanıyor → `website_url` otomatik available
- `_build_image_prompt` (posts.py) + `suggest_ideas` (ai.py) + `generate_script` (ai.py) `build_brand_context()` çağırmıyor → etkilenmedi
- Yalnızca `caption_generator.py:generate_captions` → `build_brand_context` akışı Tier 2 değişikliğinden faydalanır

**Not — `letterCase` atlandı:** Önceki analizde `letterCase` (eski `case`) eksik gibi görünüyordu; fakat 2026-04-14 commit'inde "Başlık/Alt Başlık Fontu ölü kod" temizliğinde `BrandKit.fonts` ile birlikte zaten silinmişti. Prompt'a ekleyecek alan yok.

### C) Frontend helper text (`marka-ayarlari/page.tsx`)

Görseller tab'ındaki iki logo upload alanının altına "Transparan arka planlı PNG yükleyin." açıklaması eklendi. Kullanıcıya logo yüklerken etrafında kutu olmayan bir PNG kullanması söyleniyor (luminosity detection transparent background'la birlikte en temiz sonucu verir, ama iki varyant yine gerekli — logo'nun **kendi** rengi arka planla çelişebilir).

**Doğrulama:**
- ✅ AST parse: `media_processor.py`, `webhooks.py`, `prompt_builder.py` sözdizimi temiz
- ⏳ Canlı test:
  - Açık arka planlı AI görsel üret → `logo_dark_url` seçilmeli (koyu logo basılmalı)
  - Koyu arka planlı AI görsel üret → `logo_light_url` seçilmeli (açık logo basılmalı)
  - Tek varyantlı marka (sadece light yüklü) → fallback davranışı (light her zaman seçilir)
  - Caption endpoint image_prompt'unda marka HEX kodları görünmeli (MyGoodShoes → mor tonlar, beige yerine)

**Sonraki:** Canlı testler sonrası intro/outro FFmpeg pipeline (FEATURE_SPEC_intro_outro.md → deferred Sprint 2) ve 16:9 curated aspect ratio polish.

## 2026-04-19 — Brand kit medya kaldırma endpoint'leri (logo + intro video DELETE) ✅

Canlı testte kullanıcı logoları/intro videoyu yükledi ama **kaldırma seçeneği yoktu** — yalnızca üzerine yeni dosya yükleyerek değiştirebiliyordu. İki yeni endpoint eklendi:

- `DELETE /brands/{id}/logo?variant=light|dark` — R2'den siler + ilgili DB kolonunu NULL yapar (`logo_light_url` veya `logo_dark_url`)
- `DELETE /brands/{id}/intro-video` — R2'den siler + `intro_video_url` NULL yapar

**Uygulama notları** (`app/routers/brands.py`):
- `assert_brand_owned` sahiplik kontrolü + 404 guard (brand yoksa)
- `_r2_path_from_url(url)` helper'ı public URL'den R2 object key çıkarır (R2_PUBLIC_URL prefix strip)
- R2 path çözülemezse silme atlanır ve sadece DB kolonu NULL yapılır (legacy/external URL edge case)
- `invalidate_pattern(f"otomaix:social:brands:{workspace_id}")` brand list cache'ini temizler
- `updated_at = now()` setlenir → brand list ve frontend state senkron kalır

**Risk:** düşük — salt additive, R2 delete zaten idempotent (`ClientError` yutuluyordu), DB UPDATE tek kolon.

## 2026-04-19 — Post-Phase 7 hotfix: brands.updated_at + jsonb double-encode fix ✅

Canlı testte iki ayrı Sentry hatası patladı:

### A) Migration 023 — `social.brands.updated_at` eksikti
`brands.py:187` (logo upload), `brands.py:215` (intro video upload) ve `brands.py:157` (kit update) üç UPDATE query'si `updated_at = now()` atıyor ama `social.brands` tablosu migration `001_initial_social.sql`'de **updated_at kolonu hiç oluşturulmamış**. Canlıda logo yükleme 500 veriyordu: `column "updated_at" of relation "brands" does not exist`.

**Fix** (`shared/db/migrations/023_brands_updated_at.sql`, prod'a uygulandı):
```sql
ALTER TABLE social.brands ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();
DROP TRIGGER IF EXISTS brands_updated_at ON social.brands;
CREATE TRIGGER brands_updated_at BEFORE UPDATE ON social.brands FOR EACH ROW EXECUTE FUNCTION social.set_updated_at();
```
`posts` tablosundaki mevcut `set_updated_at()` fonksiyonu yeniden kullanıldı.

### B) jsonb double-encode bug — `dict()` sequence ValueError
Kit update hatasından hemen sonra ikinci Sentry: `ValueError: dictionary update sequence element #0 has length 1; 2 is required` at `brands.py:153` → `existing = dict(row["brand_kit"]) if row["brand_kit"] else {}`. Sorun CLAUDE.md'deki **2026-04-14 asyncpg jsonb codec fix**'in uyarısının ihlali — *"Kritik: `json.dumps()` + `$N::jsonb` cast KULLANMA, dict/list'i doğrudan parametre olarak geç."*

**Kök neden:** `database.py`'de kayıtlı codec (`set_type_codec('jsonb', encoder=json.dumps, decoder=json.loads)`) asyncpg otomatik olarak çalıştırır. Üç callsite hâlâ elle `json.dumps()` ile parametre geçiyordu:
- `brands.py:160` — `update_brand_kit` UPDATE
- `avatar.py:142` — `create_avatar_from_photo` UPDATE
- `avatar.py:174` — `set_stock_avatar` UPDATE

`json.dumps(dict)` → codec tekrar `json.dumps(str)` → DB'de JSON-string olarak saklanıyor (`jsonb_typeof='string'`). Okumada decoder iç string'i döndürüyor, `dict(str)` → tek karakteri tuple beklediği için patlıyor.

**Fix (3 dosya):**
- `brands.py`: `import json` kaldırıldı (artık kullanılmıyor), satır 160 `json.dumps(merged)` → `merged` (dict direkt). Satır 153 `dict(row["brand_kit"])` → `parse_brand_kit(row["brand_kit"])` defansif okuma (legacy str satırları için).
- `avatar.py`: iki inline `import json` kaldırıldı, `json.dumps(existing_kit)` → `existing_kit`, `dict(row["brand_kit"])` → `parse_brand_kit(row["brand_kit"])`.
- `app/core/utils.py:parse_brand_kit` zaten str+dict ikisini de handle ediyor (B-7 refactor'ünden beri).

**Prod data repair** (tek seferlik):
```sql
UPDATE social.brands
   SET brand_kit = (brand_kit #>> '{}')::jsonb
 WHERE jsonb_typeof(brand_kit) = 'string';
-- 1 row affected, sonra tüm satırlar jsonb_typeof='object'
```

**Neden diğer jsonb kolonları etkilenmedi:** Auth/webhooks/trends router'ları `$N::jsonb` text cast kullandığı için codec encoder tetiklenmiyor (text parametresi server-side cast). Yalnızca bu üç callsite hem codec tetikliyor hem `json.dumps` yapıyordu — çift encoding çakışması.

**Etki analizi:**
- Risk: düşük — değişiklik yalnızca write path'te, read path'te savunmacı `parse_brand_kit` helper'ı mevcut str değerleri de handle eder.
- Backward compat: kit content değişmiyor, yalnızca saklama formatı düzeliyor.
- Önleme: ileride `brand_kit` dışı jsonb kolonlarına yazan yeni kod `json.dumps()` KULLANMAMALI — codec otomatik çalışır.

**Sonraki:** Doğrulama → kullanıcının `/marka-ayarlari` sayfasındaki kit patch'leri artık 500 yerine 200 dönmeli; Sentry'de bu iki issue tekrar etmemeli.

## 2026-04-19 — Phase 7 Sprint 7: Media adapter refactor + dynamic model registry ✅

**Kapsam:** fal.ai model-spesifik mantık `media_adapters.py`'ye taşındı — 4 modalite için Protocol tabanlı adapter pattern (image / video / image_to_video / faceless_background). Her modalite env var ile konfigüre edilir (`IMAGE_MODEL`, `VIDEO_MODEL`, `IMAGE_TO_VIDEO_MODEL`, `FACELESS_BACKGROUND_MODEL`), aktif adapter modül import'unda bir kez resolve edilir. Yeni model eklemek artık tek adapter sınıfı + registry'e tek satır kayıt — business kod değişmez.

**Yeni dosyalar:**
- `app/services/media_adapters.py` — 4 Protocol (`ImageModelAdapter`, `VideoModelAdapter`, `ImageToVideoModelAdapter`, `FacelessBackgroundAdapter`) + 4 adapter sınıfı (FluxV2ProAdapter, KlingV3ProAdapter, KlingV25TurboProAdapter, HunyuanVideoAdapter) + registry dict'leri + `get_active_*_adapter()` resolver'ları. Adapter `build_args(prompt, aspect_ratio, ...)` metoduyla fal.ai submit argümanlarını döndürür; geçersiz aspect'te ValueError fırlatır. Faceless için `_RESOLUTION_MAP` aspect → resolution literal ("720x1280") dönüşümü yapar.
- `app/routers/media_models.py` — `GET /media-models/active` public endpoint (JWT'siz, 1hr HTTP cache). 4 modalite için `{key, model_id, supported_ratios}` döndürür. `image_to_video.supported_ratios` her zaman None (çıktı oranı input image'den türer).

**Değişen dosyalar:**
- `app/core/config.py` — 4 model env var (default değerleri ile). Docstring: env değişince process restart gerekir, adapter resolve'ları modül import'unda cache'lenir.
- `app/services/fal_ai.py` — `generate_image` artık `_image_adapter.build_args()` çağırır, silent `.get(ratio, "square")` fallback kaldırıldı. `generate_video` + `generate_video_from_image` scaffold olarak korundu (aktif VideoModelAdapter ve ImageToVideoModelAdapter üzerinden — UI caller sonraki faz'da eklenecek). `_SIZE_MAP` artık adapter'ın içinde; `SUPPORTED_ASPECT_RATIOS` public sabit adapter'dan okunur.
- `app/services/faceless_video.py` — `FAL_VIDEO_MODEL` + `SUPPORTED_FACELESS_RATIOS` artık `_faceless_bg_adapter.model_id` ve `_faceless_bg_adapter.supported_ratios`'tan türer. `generate_background_video` adapter'ın `build_args`'ını kullanır.
- `app/routers/posts.py` — Faceless video endpoint'ine submit öncesi aspect validation eklendi: `payload.aspect_ratio not in SUPPORTED_FACELESS_RATIOS` → HTTP 400 + Türkçe mesaj (pipeline'a düşmeden). Aynı koruma image akışında Sprint 6 hardening'de eklenmişti.
- `app/main.py` — `media_models` router alphabetical sırada kaydedildi (documents ← media_models → posts).

**Adapter registry ve env akışı:**

| Env var | Default | Adapter sınıfı | Model ID |
|---------|---------|----------------|----------|
| `IMAGE_MODEL` | `flux-2-pro` | FluxV2ProAdapter | fal-ai/flux-2-pro |
| `VIDEO_MODEL` | `kling-v3-pro` | KlingV3ProAdapter | fal-ai/kling-video/v3/pro/text-to-video |
| `IMAGE_TO_VIDEO_MODEL` | `kling-v25-turbo-pro` | KlingV25TurboProAdapter | fal-ai/kling-video/v2.5-turbo/pro/image-to-video |
| `FACELESS_BACKGROUND_MODEL` | `hunyuan-video` | HunyuanVideoAdapter | fal-ai/hunyuan-video |

**Faz breakdown (her biri ayrı commit+push):**
- **Faz 1:** IMAGE_MODEL env + FluxV2ProAdapter — fal_ai.py image path'i adapter'a taşındı
- **Faz 2a:** `get_active_image_adapter()` + registry dict — text-to-video ve image-to-video için altyapı hazırlandı
- **Faz 2b:** VideoModelAdapter Protocol + KlingV3ProAdapter + VIDEO_ADAPTERS registry
- **Faz 2c:** ImageToVideoModelAdapter Protocol + KlingV25TurboProAdapter (imza farklı — aspect yok, image_url var)
- **Faz 2d:** FacelessBackgroundAdapter Protocol + HunyuanVideoAdapter — faceless_video.py refactor edildi
- **Faz 2e:** Submit-time aspect validation `posts.py:generate_faceless_video`'ya eklendi
- **Faz 2f:** `GET /media-models/active` endpoint + router kayıt
- **Faz 2g:** Frontend `lib/api/media-models.ts` + `/icerik-olustur` dynamic aspect selector (detay: frontend/CLAUDE.md)
- **Faz 3:** Locust senaryolarına `/media-models/active`, `/templates`, `/posts/generate-caption` eklendi — public endpoint cache hit validation ve caption rate limit (30/saat) testi için
- **Faz 4:** Bu docs güncellemesi

**Etki analizi:**
- Risk: düşük — adapter resolve modül import'unda yapılır, fallback default değerlerle ilk çağrı çalışır. Env geçerli registry key'i içermiyorsa ValueError fırlatır → uygulama başlamaz (fail-fast). Mevcut iş kodunun hiçbir çağrı noktası değişmedi; yalnızca dahili implementation adapter'a delege edildi.
- Backward compat: API sözleşmeleri değişmedi. Eski frontend client'ları `GET /media-models/active`'i kullanmadan da çalışmaya devam eder (aspect ratio'ları hardcoded olur ama geçersiz bir oran seçerse backend 400 döner — Sprint 6 hardening davranışı).
- Adapter scaffolding (`generate_video`, `generate_video_from_image`) kasıtlı olarak korundu — UI caller'ları ileriki text-to-video ve image-to-video faz'larında eklenecek. Silme, aktif kullanımı olmasa bile altyapı hazır tutuldu.

**Doğrulama (2026-04-19 canlı):**
- ✅ `curl https://api.otomaix.com/media-models/active` → HTTP 200, `Cache-Control: public, max-age=3600`, 4 modalite JSON (image/video/i2v/faceless)
- ✅ `curl https://api.otomaix.com/templates` → 22 şablon (Phase 7 Sprint 1/2 regresyon yok)
- ✅ `curl 'https://api.otomaix.com/templates?sector=saglik'` → 11 şablon (3 sağlık + 8 genel)
- ⏳ Frontend canlı test: `/icerik-olustur` aspect selector video/image contentType'larına göre farklı buton seti göstermeli (kullanıcı tarayıcıda doğrulayacak)

**Sonraki:** Phase 7 kapandı. Olası sonraki iş kalemi: text-to-video / image-to-video UI entegrasyonu (Sprint 7 adapter altyapısını kullanacak yeni UI faz'ı). 16:9 aspect ratio'nun frontend curated `ASPECT_RATIOS` listesine eklenmesi minör polish olarak beklemede.

## 2026-04-19 — Phase 7 Sprint 6 hardening: fal.ai error visibility + aspect ratio fix + stale-job sweeper ✅

**Sorun:** PLATFORM_DEFAULTS hotfix sonrası yapılan canlı testte `/icerik-olustur` Ürün Kartı akışında post 13+ dakika `generating` durumunda asılı kaldı (post id `33a83bce-233e-4d51-ae1d-94aff4864f9c`). Ne kullanıcıya hata gösterildi, ne Sentry'ye sinyal gitti, ne DB'de `failed` işaretlendi. Üç ayrı gap bir arada çalıştı:

1. **Yanlış aspect ratio literal'leri** (`fal_ai.py:_SIZE_MAP`): FLUX.2 Pro'nun desteklediği preset listesi `square_hd, square, portrait_4_3, portrait_16_9, landscape_4_3, landscape_16_9` ile sınırlı. `_SIZE_MAP` 3 geçersiz değer içeriyordu (`portrait_9_16`, `portrait_4_5`, `portrait_2_3`) → fal.ai queue API submit sırasında 422 validation error döndü, webhook yolu bu hatayı ayrı payload olarak ~13 ms içinde callback ediyor.
2. **Webhook error payload gözardı ediliyordu** (`webhooks.py:fal_webhook`): Error callback'inde `payload.images == []` olduğu için handler `{skipped: true, reason: "no images in payload"}` ile sessizce 200 OK dönüp çıkıyordu. Post `generating` durumunda kaldı, Sentry'ye hiçbir şey gitmedi.
3. **Stale-job güvenlik ağı yok:** fal.ai webhook tamamen kaybolursa / ulaşmazsa, post sonsuza dek `generating` kalıyor. Kullanıcı loader görüyor, terk ediyor.

**Çözüm (3 dosya):**

### A) `app/services/fal_ai.py` — FLUX.2 Pro presets + dict fallback
- `_SIZE_MAP` yeniden yazıldı: preset desteklenen oranlar için string literal, preset olmayan (`4:5`, `2:3`) için `{"width": W, "height": H}` dict formatı. FLUX.2 Pro `image_size: Union[ImageSize_dict, Literal]` kabul ediyor.
- `SUPPORTED_ASPECT_RATIOS: tuple[str, ...]` public sabit eklendi.
- `resolve_image_size(aspect_ratio)` fonksiyonu — bilinmeyen oranda `ValueError` fırlatır, `generate_image()` içinde silent `.get(ratio, "square")` fallback'i kaldırıldı (yanlış oranı belirsiz bir preset'e eşliyordu).

| En-boy oranı | FLUX.2 Pro image_size |
|--------------|----------------------|
| 1:1          | `square_hd`          |
| 9:16         | `portrait_16_9`      |
| 4:5          | `{width:1024, height:1280}` |
| 2:3          | `{width:1024, height:1536}` |
| 16:9         | `landscape_16_9`     |
| 4:3          | `landscape_4_3`      |
| 3:4          | `portrait_4_3`       |

### B) `app/routers/webhooks.py` — Error payload detection + Sentry
- Webhook artık `body.status == "ERROR"`, `payload.detail`, `payload.error` veya `images == []` durumlarında **error path**'e düşer.
- Error durumunda: `UPDATE social.posts SET status='failed'`, `sentry_sdk.set_context('fal_webhook_error', {...})` + `capture_message(level='error')`.
- Post bulunamayan (`fal_job_id` eşleşmiyor) webhook'lar artık Sentry'ye `warning` seviyesinde raporlanır (önceden sessizce skipped dönüyordu).

### C) `app/routers/posts.py` — Submit-time aspect ratio validation
- `SUPPORTED_ASPECT_RATIOS` import edildi.
- `POST /posts/generate` ve `POST /posts/{id}/regenerate` endpoint'lerine **submit öncesi** validation eklendi — geçersiz oranda HTTP 400 + Türkçe mesaj (`Desteklenmeyen en-boy oranı: 'xx'. Geçerli değerler: 1:1, 9:16, ...`).
- Böylece kullanıcı anında hata alır, fal.ai'ye submit bile edilmez, post DB'ye `generating` durumunda hiç girmez.

### D) `app/routers/internal.py` — Stale-job sweeper
- Yeni endpoint: `POST /internal/posts/fail-stale` (X-Internal-Key korumalı).
- `UPDATE ... WHERE status='generating' AND created_at < now() - interval '10 minutes' RETURNING *` — tek atomik UPDATE, her etkilenen satır için Sentry `capture_message(level='warning')` ve set_context (post_id, brand_id, fal_job_id, created_at).
- Response: `{failed_count, post_ids[]}`.
- Route sırası: `/posts/scheduled-due` ve `/posts/fail-stale` **daima** `/posts/{post_id}` dinamik route'undan önce deklare — aksi halde `"fail-stale"` string'i UUID parser'a düşer.

**Öneri (opsiyonel n8n cron, bu PR'de yok):** Her 10 dakikada bir `POST /internal/posts/fail-stale` çağıran yeni workflow. Sweeper idempotent ve asıl path'ten tamamen bağımsız — webhook kaybı senaryosunda devreye girer. İlk canlı doğrulamadan sonra eklenmesi düşünülebilir.

**Etki analizi:**
- Risk: düşük
  - Aspect `_SIZE_MAP` değişikliği: eski geçersiz literal'ler zaten fal.ai tarafından reddedildiği için bir şey kırılmıyor (production'da 4:5/2:3/9:16 seçen her kullanıcı zaten stuck post yaşıyordu).
  - Webhook error path: başarılı callback'ler aynı akışta devam ediyor (is_error=False durumu birebir eski mantık).
  - Submit validation: aspect_ratio `PostGenerate` şemasında zaten required TEXT field, default değer yok; frontend UI de geçerli preset'lerden seçim yaptırıyor. Production trafiği etkilenmez.
  - Stale sweeper: salt UPDATE, yalnızca webhook kaybolan senaryoda tetiklenir; normal akışta 0 satır.
- Backward compat: submit-time aspect validation legacy content_type akışları (special_day/quote/serbest) için de geçerli — bu akışlar zaten `1:1` gönderiyor, etkilenmez.
- Migration gerekmez — yalnızca kod değişikliği.

**Stuck post temizliği:** `33a83bce-...` DB'de manuel olarak `status='failed'` olarak işaretlendi. Post kütüphanede asılı kalmadı.

**Doğrulama:**
- ✅ AST parse: `fal_ai.py`, `webhooks.py`, `posts.py`, `internal.py` sözdizimi temiz
- ⏳ Canlı test (deploy sonrası):
  - `/icerik-olustur` Ürün Kartı + 4:5 aspect → post başarıyla üretilmeli, webhook `ready`'ye çekmeli
  - Geçersiz aspect (ör. direkt API'den `"5:4"` gönder) → HTTP 400 dönmeli
  - Fal.ai rate-limit / quota error simulasyonu (mümkünse) → post `failed`, Sentry'de error event görünmeli
  - `POST /internal/posts/fail-stale` manuel çağrı (X-Internal-Key ile) → stale post yoksa `{failed_count:0, post_ids:[]}` dönmeli

**Sonraki:** Sprint 7 — Test, cleanup, Phase 7 final dokümantasyon. Opsiyonel: 10 dakikada bir `fail-stale` çağıran n8n workflow'u.

## 2026-04-19 — Phase 7 Sprint 6 hotfix: PLATFORM_DEFAULTS ✅

**Sorun:** Canlı test (Ürün Kartı şablonu + 6 platform: IG, TikTok, LinkedIn, Twitter, Facebook, YouTube) sonrası TikTok/Facebook/YouTube sekmelerinde caption'lar boş geldi. Claude yalnızca şablonun `platformOverrides` dict'inde geçen platformlar için caption üretti (IG/LI/TW). Kök neden: 22 şablonun büyük çoğunluğu çoğu platform için `platformOverrides` tanımlamıyordu — özellikle TikTok/Threads/Bluesky hiçbir şablonda kural içermiyordu. `build_platform_instructions()` `if not override: continue` ile eksik platformlar için Claude'a kural göndermiyor, o yüzden de caption üretmiyordu.

**Çözüm (Seçenek D):** `prompt_builder.py`'ye merkezi **`PLATFORM_DEFAULTS`** dict eklendi — 9 platform için `captionStyle`, `maxHashtags`, `useFirstComment` varsayılanları. Template-level `platformOverrides` bu default'ların üzerine alan bazında merge edilir (sadece None olmayan alanlar override eder). Böylece şablonda hiç `platformOverrides` yoksa bile her seçili platform Claude'a gönderilen prompt'ta explicit kural olarak görünür.

**Platform varsayılanları** (`prompt_builder.py:PLATFORM_DEFAULTS`):
| Platform  | Style  | Max Hashtag | First Comment |
|-----------|--------|-------------|---------------|
| instagram | medium | 15          | ✓             |
| linkedin  | long   | 5           | ✗             |
| twitter   | short  | 2           | ✗             |
| facebook  | medium | 5           | ✓             |
| tiktok    | short  | 5           | ✗             |
| youtube   | medium | 8           | ✗             |
| threads   | short  | 5           | ✓             |
| pinterest | medium | 10          | ✗             |
| bluesky   | short  | 3           | ✗             |

**Değişen dosyalar (2):**
- `app/core/prompt_builder.py`:
  - `PLATFORM_DEFAULTS: dict[str, dict]` sabiti eklendi
  - `_resolve_platform_rules(platform, override)` yardımcı fonksiyonu eklendi — default + override merge
  - `build_dynamic_content()` içinde `if template and template.platformOverrides and platforms:` → `if platforms:` — şablon olsun olmasın her zaman platform talimatı üretilir (`overrides = template.platformOverrides if template else None`)
  - `build_platform_instructions(overrides, platforms)` yeniden yazıldı — `overrides` artık opsiyonel (`dict | None`), merged `rules_dict` üzerinden loop, `continue` sadece PLATFORM_DEFAULTS'ta olmayan bilinmeyen platformlar için
- `app/core/caption_generator.py`:
  - `_build_output_format_instruction()` → `has_platform_overrides` flag kaldırıldı; her platform için `useFirstComment` merge edilmiş rules'tan okunur → `first_comment` alanı sadece gerçekten kullanan platformların şemasına eklenir
  - `_resolve_platform_rules` import edildi

**Etki analizi:**
- Risk: düşük — template-level override varsa davranış aynen korunur (field bazlı merge, override fields win). Default'lar yalnızca şablonda override olmayan platformlar için devreye girer.
- Backward compat: `build_platform_instructions()` imzası `overrides: dict` → `overrides: dict | None`; caller'lardan sadece `build_dynamic_content` çağırıyor (dış kod etkilenmez).
- Caption endpoint 3-tier cache'i bozulmaz — PLATFORM_DEFAULTS tamamen Tier 3 (dynamic) içinde değerlendirilir, Tier 1/2 cache hit etkilenmez.

**Doğrulama:**
- ✅ AST parse: `prompt_builder.py`, `caption_generator.py` sözdizimi temiz
- ⏳ Canlı test (deploy sonrası):
  - Ürün Kartı (`eticaret-urun-karti`) + 6 platform (IG/TikTok/LI/TW/FB/YT) ile caption üret → **tüm 6 platform sekmesi dolu gelmeli**
  - IG first_comment alanı mevcut olmalı (default useFirstComment=True)
  - TikTok caption short formatta, ≤5 hashtag
  - LinkedIn long format, ≤5 hashtag
  - Sağlık şablonu (Biliyor Muydunuz?) → disclaimer hâlâ caption sonunda

**Sonraki:** Sprint 7 — Test, cleanup, duplicate temizlik, load test güncellemesi, Phase 7 final dokümantasyon.

## 2026-04-19 — Phase 7 Sprint 6: Platform-spesifik publishing ✅

**Kapsam:** Upload-Post entegrasyonu artık `posts.platform_captions` JSONB kolonunu okuyup her platforma kendi caption'ını gönderir. `first_comment` alanı destekleyen platformlar (Instagram, Facebook, Threads) için `{platform}_first_comment` form parametresi gönderilir. `platform_captions` NULL ise legacy `caption + hashtags` birleşik title mantığı aynen çalışır (backward compat).

**Değişen dosya (tek):** `app/services/upload_post.py`

- **`_publish_single_platform()` imzası:**
  - `first_comment: str | None = None` parametresi eklendi
  - `first_comment` varsa ve platform `instagram` / `facebook` / `threads` ise `{platform}_first_comment` form alanı olarak gönderilir (500 karakter truncate)
  - Diğer platformlarda (linkedin, twitter, tiktok, pinterest, bluesky) `first_comment` yok sayılır — Upload-Post desteklemiyor

- **`publish_post()` içinde per-platform caption routing:**
  - `post["platform_captions"]` JSONB okunuyor (asyncpg str döndürebilir → `json.loads` + `try/except`; dict'e değilse `{}`)
  - Beklenen şekil (Sprint 4'te `generate_post` tarafından yazılır):
    ```json
    {
      "default": "...",
      "platforms": {
        "instagram": {"caption": "...", "first_comment": "...", "hashtags": [...]},
        "linkedin": {"caption": "...", "hashtags": [...]}
      }
    }
    ```
  - Her platform için:
    - `platforms[<platform>].caption` varsa → `title_text` + `first_comment` oraya yazılır
    - Yoksa → `legacy_title = caption + " #h1 #h2 …"` (eski davranış)

**Etki analizi:**
- Risk: düşük — `platform_captions` NULL olan tüm eski ve template'siz postlar için legacy path birebir korundu (autoposting n8n, `special_day`, `quote`, serbest mod + image_prompt varsa bile caption/hashtags kolonlarına backward-fill var → `platform_captions` yine NULL kalabilir)
- JSONB parse hem `dict` hem `str` (asyncpg default) durumunu kapsıyor → codec ayarından bağımsız çalışır
- `first_comment` 500 karakter truncate — Instagram'ın ilk yorum limiti ~2200 ama güvenli tarafta kalındı; bu Sprint 7 load testinde yeniden değerlendirilebilir

**Upload-Post API notu:**
- `{platform}_first_comment` parametresi Upload-Post docs'ta destekleniyor ama canlıda henüz test edilmedi
- İlk canlı yayın sonrası Instagram hesabında ilk yorum olarak hashtag'lerin otomatik eklenip eklenmediği doğrulanmalı
- Çalışmazsa fallback plan (Sprint 7'de): `first_comment`'ı `title_text` sonuna `\n\n` ile ekle, `{platform}_first_comment` parametresini kaldır

**Doğrulama:**
- ✅ AST parse: `upload_post.py` sözdizimi temiz
- ⏳ Canlı test (deploy sonrası):
  - Template'li post (E-Ticaret Ürün Kartı, IG+LinkedIn seçili) yayınla → IG'de medium caption + first comment'te hashtag'ler, LinkedIn'de long caption, farklı ton
  - Sağlık şablonu (Biliyor Muydunuz?) yayınla → IG + LinkedIn caption'larının sonunda disclaimer var mı?
  - Template'siz legacy post (autoposting n8n trigger veya mevcut test postu) yayınla → eski `caption + hashtags` birleşik title aynen gitmeli
  - Retry (yalnızca başarısız platform) → `only_platforms` parametresiyle tek platform publish çalışmalı

**Sonraki:** Sprint 7 — Test, cleanup, duplicate temizlik (CATEGORY_TR vs.), load test güncellemesi, Phase 7 final dokümantasyon.

## 2026-04-18 — Phase 7 Sprint 5 polish — Akış C unified (Option B) ✅

**Tek backend değişikliği:** `app/routers/posts.py:generate_post()` içindeki Akış C bypass koşulu gevşetildi.

**Önce:** `elif payload.template_id and payload.image_prompt:` — caption endpoint üretilen `image_prompt` yalnızca `template_id` da set edilmişse bypass ediyordu.

**Sonra:** `elif payload.image_prompt:` — `image_prompt` varsa template olsun olmasın legacy `_build_image_prompt()` bypass edilir.

**Neden:** Frontend serbest modu (şablonsuz) da artık caption-first (Akış C) kullanıyor — `/posts/generate-caption` çağrısı `template_id=null` ile yapılıp `image_prompt` üretiliyor, sonra `/posts/generate` çağrısı yine `template_id=null` ama `image_prompt` dolu gidiyor. Eski koşul bu akışı yakalayamıyordu, legacy prompt builder devreye giriyordu.

**Etki analizi:**
- Risk: düşük — `image_prompt` opsiyonel alan, mevcut tek-tık akışlar (autoposting n8n, `special_day`, `quote`, legacy frontend) göndermiyor → eski path aynen çalışır
- `special_day`/`quote` branch'leri daha önce değerlendirildiği için o akışlar etkilenmez
- Caption endpoint zaten `template_id=None` durumunu destekliyor (Sprint 4'te `caption_generator.py` template=None'a `if template:` guard'larıyla graceful)

## 2026-04-18 — Phase 7 Sprint 4: Caption endpoint + Akış C ✅

**Kapsam:** Platform-spesifik caption + image_prompt + hashtag üreten yeni endpoint eklendi. `POST /posts/generate-caption` Claude Opus 4.7'ye 3-katman cache ile istek yapar (spec §4). `POST /posts/generate` Akış C için güncellendi — caption endpoint'in ürettiği `image_prompt` payload'a gelirse legacy `_build_image_prompt()` bypass edilir.

**Yeni dosyalar:**
- `app/core/caption_generator.py` — `generate_captions(brand, brand_kit, template, template_fields, user_prompt, rag_context, platforms)` Claude çağrısı:
  - `build_system_prompt()` Tier 1 + `build_brand_context()` Tier 2 (cache_control ephemeral) + `build_dynamic_content()` + `_build_output_format_instruction()` Tier 3
  - Model: `claude-opus-4-7`, `max_tokens=2048`, `temperature=1.0` (yaratıcı içerik → çeşitlilik)
  - Response parse: markdown code block strip + JSON load + default field doldurma (`default_caption`, `platform_captions`, `image_prompt`, `hashtags`)
  - **Disclaimer auto-append:** `template.defaults.disclaimer` varsa hem `default_caption` hem her platform caption'ının sonuna eklenir (idempotent — endswith kontrolü)
  - Cache loglama: `cache_read_input_tokens` + `cache_creation_input_tokens` + template.id
  - Fallback: `ANTHROPIC_API_KEY` yoksa veya Claude hatası → `_fallback_response(user_prompt, platforms)` döner (hata durumunda `error` field eklenir)
- `_build_output_format_instruction(template, platforms)` → platformOverrides varsa `useFirstComment` opsiyonunu da şemaya dahil eder

**Değişen dosyalar:**
- `app/routers/posts.py`:
  - Yeni `GenerateCaptionRequest` BaseModel (inline): `brand_id`, `template_id`, `template_fields`, `user_prompt`, `document_ids`, `platforms`
  - Yeni endpoint `POST /posts/generate-caption` (30/saat rate limit):
    - `assert_brand_owned` + sector JOIN'lü brand fetch + template lookup
    - `document_ids` varsa `get_document_context()` ile RAG
    - `generate_captions()` çağırır → `OkResponse(data=result)`
    - Invalid template_id → 400
  - `generate_post()` Akış C desteği:
    - `payload.template_id and payload.image_prompt` → enriched_prompt = payload.image_prompt (bypass)
    - `payload.platform_captions` varsa `caption` (TEXT) + `hashtags` (TEXT[]) kolonlarına backward-fill:
      - Beklenen şekil: `{"default": "...", "platforms": {"instagram": {"caption":"...", "hashtags":[...]}, "linkedin": {...}}}`
      - Fallback öncelik: `pc.default` → `platforms[ilk].caption` → `default_caption`
      - Hashtags: tüm platformlardaki hashtag'lerin unique union'ı
    - INSERT'e `caption` + `hashtags` kolonları eklendi (kolonlar zaten migration 001'den beri vardı)

**3-katman cache stratejisi (spec §4.1):**
- Tier 1 (system) → `cache_control: ephemeral` → DİL KURALI + JSON format + YASAK listesi
- Tier 2 (brand_context) → `cache_control: ephemeral` → marka + sektör + şablon guidance + disclaimer
- Tier 3 (dynamic) → cache yok → template_fields + user_prompt + RAG + output format

Aynı marka + aynı şablon için ardışık çağrılarda Tier 1 + 2 cache hit — Sentry log'larında `cache_read_input_tokens > 0` görünmeli.

**Etki analizi:**
- Risk: düşük — yeni endpoint additive, `generate_post` değişiklikleri backward-compat (frontend `platform_captions` göndermediği sürece yeni path tetiklenmez)
- Akış C frontend entegrasyonu Sprint 5'e kadar devrede değil (şu an mevcut frontend caption endpoint'i çağırmıyor)
- `special_day` / `quote` / autoposting n8n / legacy `content_category` akışları birebir korundu
- Migration gerekmez — `caption TEXT`, `hashtags TEXT[]` kolonları migration 001'den, `platform_captions JSONB` migration 022'den beri mevcut

**Doğrulama:**
- ✅ AST parse: `caption_generator.py`, `posts.py` sözdizimi temiz
- ✅ `prompt_builder` import'ları çalışır durumda (caption_generator doğrudan import ediyor)
- ✅ `posts.py` endpoint listesi: `generate_caption` + mevcut endpoint'ler
- ⏳ Canlı smoke test (deploy sonrası):
  - `POST /posts/generate-caption` Swagger UI'dan — eticaret-urun-karti + instagram/linkedin → 2 farklı caption şekli
  - Sağlık şablonu → caption sonunda disclaimer görünmeli
  - Invalid template_id → 400
  - İkinci çağrıda backend log'unda `cache_read_input_tokens > 0`

**Sonraki:** Sprint 5 — `/icerik-olustur` wizard refactor (template grid + dinamik form + Akış C UI).

## 2026-04-18 — Phase 7 Sprint 3: Prompt building refactor (template-aware + 3-tier caching) ✅

**Kapsam:** Prompt inşa mantığı tek bir ortak modüle (`prompt_builder.py`) taşındı. Posts (`_build_image_prompt`) ve AI suggest_ideas akışları `template_id` varsa şablon-aware Tier 2 (brand + sektör + şablon) / Tier 3 (yapısal form verileri + user prompt + RAG) üretir. Disclaimer auto-inject (sağlık şablonları), platform override instruction hazırlığı (Sprint 4 caption endpoint için) ve backward compat (`_build_prompt_with_rag_legacy`) korundu.

**Yeni dosyalar:**
- `app/core/prompt_builder.py` — spec §1478-1498 + §4 doğrultusunda 3-katman prompt builder:
  - `build_system_prompt()` → Tier 1: sabit kurallar (DİL, YASAK, JSON format), `cache_control: ephemeral`
  - `build_brand_context(brand, brand_kit, template)` → Tier 2: marka + sektör rehberi + şablon talimatı + önerilen CTA/hashtag + **ZORUNLU DISCLAIMER** (`template.defaults.disclaimer` varsa caption sonuna aynen eklenecek talimat)
  - `build_dynamic_content(template, template_fields, user_prompt, rag_context, platforms)` → Tier 3: yapısal form verileri (EN YÜKSEK ÖNCELİK), user prompt, RAG doküman, öncelik sırası (template.prompt.priority), platform-spesifik caption talimatları
  - `build_platform_instructions(overrides, platforms)` → spec §3.2 `PlatformOverride` alanlarını Claude'a talimat olarak çevirir (captionStyle → long/medium/short, maxHashtags, useFirstComment, toneAdjustment, additionalGuidance)

**Değişen dosyalar:**
- `app/routers/posts.py`:
  - `_build_prompt_with_rag` → `_build_prompt_with_rag_legacy` olarak yeniden adlandırıldı (birebir mantık korundu)
  - Yeni `_build_image_prompt(payload, brand, brand_kit, db)`: `template_id` varsa `get_template_by_id()` çeker; `image_prompt` override edilmişse aynen kullanır, yoksa `template.name + formFields değerleri` ile kısa bir fal.ai image prompt inşa eder. `template_id` yoksa legacy akış devreye girer (special_day, quote, serbest prompt).
  - `generate_post()`: `enriched_prompt = await _build_image_prompt(...)` — eski çağrı noktası değişmedi
  - **Not:** Caption üretimi (tam 3-tier prompt ile Claude çağrısı) Sprint 4'te eklenecek — Sprint 3'te sadece fal.ai image prompt template-aware oldu, caption hâlâ legacy fallback kullanıyor.
- `app/routers/ai.py`:
  - `SuggestIdeasRequest` → `template_id: str | None`, `template_fields: dict | None` alanları eklendi
  - `suggest_ideas()` brand query'si `social.sectors` JOIN ile `sector_slug` döndürür (Tier 2'ye SECTOR_GUIDANCE enjekte etmek için)
  - Template set ise: `category_guidance = ""` (legacy skip), Tier 2 brand_context'e SECTOR_GUIDANCE + `template.prompt.guidance` + `template.defaults.suggestedCTAs/Hashtags` eklenir
  - Template fields Tier 3 dynamic_text'e `=== YAPISAL VERİLER ===` bloğu olarak enjekte edilir
  - Template yoksa: mevcut `CATEGORY_GUIDANCE`/`CATEGORY_TR` akışı birebir korundu

**3-katman cache stratejisi (spec §4.1):**
| Katman | İçerik | Cache |
|--------|--------|-------|
| **Tier 1 — System** | Sabit kurallar + DİL KURALI + JSON format | `ephemeral` ✓ |
| **Tier 2 — Brand** | Marka + tonalite + renkler + SECTOR_GUIDANCE + şablon guidance + disclaimer | `ephemeral` ✓ |
| **Tier 3 — Dynamic** | Template fields + user prompt + RAG + platform rules | cache yok |

Aynı marka + şablon kombinasyonu için tekrarlı çağrılarda Tier 1 + Tier 2 cache hit → latency + token maliyeti düşüşü.

**Etki analizi:**
- Risk: düşük — `template_id=None` tüm akışları legacy path'e yönlendirir (posts, suggest_ideas)
- `special_day` / `quote` / video akışları değişmedi (sadece `image`/`carousel` + `template_id` aktifse yeni path)
- Autoposting (n8n `/internal/autoposting/trigger`) template_id gönderilmediği için etkilenmez
- `content_category` field tam geriye uyumlu — eski frontend hâlâ çalışır

**Doğrulama:**
- ✅ AST parse: `prompt_builder.py`, `posts.py`, `ai.py` sözdizimi temiz
- ✅ `SuggestIdeasRequest` template alanları pydantic şemasına eklendi (AST kontrol)
- ✅ `posts.py` fonksiyonları: `_build_image_prompt`, `_build_prompt_with_rag_legacy`, `_build_special_day_prompt`, `_build_quote_prompt` — dördü de mevcut
- ⏳ Canlı smoke test (deploy sonrası):
  - Image + template_id + template_fields → fal.ai prompt'unda şablon adı + form field değerleri görünmeli
  - AI suggest-ideas template_id ile → Claude'a giden prompt'ta SECTOR_GUIDANCE + template.prompt.guidance görünmeli
  - special_day/quote → eski akış birebir çalışmalı
  - template_id=null → legacy path (content_category dahil) aynen çalışmalı

**Sonraki:** Sprint 4 — Platform-spesifik caption endpoint (`POST /posts/{id}/captions/generate`) + Akış C (caption + görsel aynı anda). `prompt_builder.build_platform_instructions()` kullanılacak.

## 2026-04-18 — Phase 7 Sprint 2: Şablon Kataloğu + SECTOR_GUIDANCE ✅

**Kapsam:** Sprint 1'in boş iskelet `TEMPLATES` + `SECTOR_GUIDANCE` dict'leri **spec §2.1/§2.3** doğrultusunda dolduruldu. Tüm değişiklikler additive (ilk defa veri ekleniyor) → `/templates` endpoint'i artık 22 şablon döndürüyor (daha önce boş array).

**KRİTİK fix — `app/models/templates.py` camelCase rewrite:**
- Sprint 1 modeli snake_case alanlar kullanıyordu (`content_types`, `form_fields`, `help_text`, `max_length`, `suggested_ctas`…).
- Spec §3.2 **camelCase** zorunluluğu: `contentTypes`, `formFields`, `helpText`, `defaultValue`, `validation`, `captionStyle`, `maxHashtags`, `toneAdjustment`, `useFirstComment`, `additionalGuidance`, `aspectRatioSuggestion`, `slideCount`, `suggestedCTAs`, `suggestedHashtags`, `platformOverrides`.
- Breaking change yok (TEMPLATES boştu → endpoint response değişmedi). Frontend TypeScript interface (`lib/templates.types.ts`) camelCase'in birebir eşi.
- `TemplateFormField.type` enum'u `Literal["text", "textarea", "number", "select", "multi-select", "url"]` — spec §2.3 ile uyumlu.
- `PlatformOverride` 8 platform destekler (instagram, linkedin, twitter, facebook, tiktok, threads, pinterest, bluesky).

**`app/core/templates_data.py` doldurma:**
- **22 şablon** eklendi (spec §2.1 listesi birebir):
  - E-Ticaret (4): `eticaret-urun-karti`, `eticaret-kampanya-banner`, `eticaret-musteri-yorumu`, `eticaret-stok-sayaci`
  - Yemek/Gıda (3): `yemek-gunun-menusu`, `yemek-yeni-lezzet`, `yemek-tarif-karti`
  - Sağlık (3): `saglik-biliyor-muydunuz`, `saglik-tedavi-sureci`, `saglik-sss`
  - Hizmet (4): `hizmet-mevzuat-degisikligi`, `hizmet-son-tarih-hatirlatma`, `hizmet-karsilastirma-tablosu`, `hizmet-musavirlik-paketi`
  - Genel (`sectors=["*"]`, 8): `genel-hakkimizda`, `genel-ekip-tanitimi`, `genel-musteri-yorumu`, `genel-motivasyon`, `genel-is-ilani`, `genel-basari-hikayesi`, `genel-sektor-insight`, `genel-sss`
- **12 SECTOR_GUIDANCE entry** eklendi (spec §2.3): 4 detaylı (`e-ticaret-perakende`, `yemek-gida`, `saglik`, `hizmet` — 150-250 kelime) + 8 generic (`teknoloji`, `egitim`, `moda-tekstil`, `turizm`, `finans`, `insaat-gayrimenkul`, `otomotiv`, `genel` — ~50 kelime).
- Sağlık şablonları paylaşılan disclaimer sabitleri kullanır: `_SAGLIK_DISCLAIMER_LONG` / `_SAGLIK_DISCLAIMER_SHORT` → tek kaynaklı uyarı metni.
- `get_all_templates()` sıralaması: `(template.order or 999, template.name)` → frontend'de stabil gösterim.

**`app/main.py` startup validation:**
- `_validate_templates()` fonksiyonu eklendi, `lifespan()` context manager başında çalışır. Assertion'lar: `len(TEMPLATES) == 22`, her şablonun `id` dict key'iyle eşleşiyor, `status == "active"`, `sectors` ve `formFields` boş değil.
- Herhangi bir validation kırılırsa uygulama **başlamaz** (fail-fast) — prod'a bozuk şablon gitmesi imkânsız.
- Loglar: `"Phase 7 templates loaded: 22 templates, 12 sector guidance entries"`.

**Etki analizi:**
- Risk: düşük (API response şeması aynı, sadece content zenginleşti)
- Mevcut `/posts/generate` çağrıları `template_id=null` ile çalışmaya devam eder (Sprint 3'te prompt refactor)
- Backward compat: autoposting, special_day, quote, video akışları değişmedi
- Frontend etkileri: `GET /templates?sector=...` artık gerçek şablonlar döndürür — Sprint 3'te frontend wizard entegre edecek

**Doğrulama:**
- ✅ AST parse: `templates.py`, `templates_data.py`, `main.py` sözdizimi temiz
- ✅ Count doğrulaması: 22 TEMPLATES + 12 SECTOR_GUIDANCE keys (regex parse)
- ⏳ Canlı smoke test (deploy sonrası):
  - `curl https://api.otomaix.com/templates | jq '.data.count'` → Expected: 22
  - `curl 'https://api.otomaix.com/templates?sector=saglik' | jq '.data.count'` → Expected: 11 (3 sağlık + 8 genel)
  - `curl 'https://api.otomaix.com/templates?sector=e-ticaret-perakende' | jq '.data.count'` → Expected: 12 (4 e-ticaret + 8 genel)
  - `curl 'https://api.otomaix.com/templates?sector=teknoloji' | jq '.data.count'` → Expected: 8 (0 teknoloji + 8 genel wildcard)

**Sonraki:** Sprint 3 — `posts.py._build_prompt_with_rag()` refactor: `template_id` varsa `TEMPLATE_PROMPTS`'dan guidance çek + `template_fields` yapısal veriyi prompt'a enjekte et + disclaimer auto-inject. `ai.py.suggest_ideas` template-aware.

> **Phase 6 — Trend Sistemi Yenileme (2026-04-16).**
> Üç katmanlı trend mimarisi. Detaylı plan: `~/otomaix/docs/06-social-trends-phase6.md`.
> **ADR-2:** Layer B için Serper.dev + Claude Haiku kullanılıyor.
> **İlerleme:** Sprint 1 ✅ · Sprint 2 ✅ · Sprint 3 ✅ · Sprint 4 ✅ · Sprint 5 ✅ · Sprint 6 ✅ — **Phase 6 tamamlandı**

## 2026-04-18 — Phase 7 Sprint 1: Backend Şablon Altyapısı ✅

**Kapsam:** Şablon sistemi backend iskeleti — migration, modeller, endpoint, auth/init güncelleme. Tüm değişiklikler additive (NULL'lanabilir kolonlar, opsiyonel alanlar) → mevcut akışlar (special_day, quote, video, autoposting, serbest içerik) aynen çalışır.

**Migration 022_posts_template_fields.sql** (prod'a uygulandı ✅):
- `social.posts.template_id TEXT` — templates_data.py şablon ID'si; NULL = serbest/özel akış
- `social.posts.template_fields JSONB` — yapısal form verisi (ör. `{product_name, price}`)
- `social.posts.platform_captions JSONB` — platform-özel caption'lar (Sprint 4 caption-gen endpoint için)
- `social.posts.slides JSONB` — Sprint 6 v2 carousel scaffold (v1'de her zaman NULL)
- `idx_posts_template_id` partial index (WHERE template_id IS NOT NULL) — şablon bazlı analytics/filter için

**Yeni dosyalar:**
- `app/models/templates.py` — Pydantic modelleri: `Template`, `TemplateFormField`, `PlatformOverride`, `TemplateOutput`, `TemplatePromptExample`, `TemplatePrompt`, `TemplateDefaults`. FieldType union (text|number|textarea|select|date|boolean).
- `app/core/templates_data.py` — Tek doğruluk kaynağı. `TEMPLATES: dict[str, Template] = {}` ve `SECTOR_GUIDANCE: dict[str, str] = {}` Sprint 1'de boş iskelet, Sprint 2'de doldurulacak. Helper'lar: `get_all_templates(sector, content_type)` (sektör filtresi `"*"` genel şablonları otomatik dahil eder), `get_template_by_id()`, `get_sector_guidance()`.
- `app/routers/templates.py` — `GET /templates` + `GET /templates/{template_id}` endpoint'leri. Public (JWT gerekmez — hassas veri yok), 1 saat HTTP cache (`Cache-Control: public, max-age=3600`), query filtreleri: `?sector=...&content_type=...`.

**Değişen dosyalar:**
- `app/main.py` — `templates_router` kayıt eklendi (alphabetical: social ← templates → trends).
- `app/routers/auth.py` — `/auth/init` brands query'sine `LEFT JOIN social.sectors` eklendi. Response artık `sector_slug` ve `sector_display_name` döndürüyor → frontend şablon filtresi için. Eski `sector` TEXT kolonu korundu (backward compat).
- `app/models/schemas.py`:
  - `BrandOut` → `sector_slug: str | None`, `sector_display_name: str | None` opsiyonel alanlar eklendi.
  - `PostGenerate` → `template_id`, `template_fields`, `platform_captions`, `image_prompt` opsiyonel alanlar eklendi. `content_category` korundu (backward compat — autoposting n8n ve legacy akışlar için).
- `app/routers/posts.py` → `generate_post()` INSERT'ü yeni kolonları kabul ediyor. `template_id` set edilmişse `content_category` otomatik `NULL` atılıyor (legacy mantık karışmasın). Tam prompt refactor Sprint 3'te.

**Etki analizi:**
- Risk: düşük (sıfır breaking change)
- Mevcut `/posts/generate` çağrıları template alanları göndermeden çalışmaya devam eder
- Autoposting n8n workflow'u (`/internal/autoposting/trigger`) değişmedi → template_id=NULL yolunda normal akış
- `special_day` ve `quote` content_type'ları için template sistemi henüz devrede değil (Sprint 3'te karar)

**Doğrulama:**
- ✅ Migration uygulandı (`\d social.posts` → 4 yeni kolon + index görünür)
- ✅ AST parse: tüm değişen dosyalar sözdizimi doğru
- ⏳ Canlı smoke test: `GET /templates` → `{templates: [], version: "1.0", count: 0}`, `GET /auth/init` → brand'lerde `sector_slug` alanı

**Sonraki:** Sprint 2 — 22 şablon + 11 sektör rehberi `templates_data.py`'ye yazılacak.

## 2026-04-16 — LLM model yükseltme + Prompt Caching ✅

**Model değişikliği:** Tüm Anthropic çağrıları `claude-haiku-4-5-20251001` → `claude-opus-4-7` olarak güncellendi (10 çağrı noktası, 7 dosya).

**SDK yükseltme:** `anthropic==0.40.0` → `anthropic>=0.90.0,<1.0.0` (prompt caching GA desteği için).

**Prompt Caching uygulaması (3 katmanlı):**
- **Katman 1 — Sabit talimatlar (system):** Kurallar, JSON format şablonu, DİL KURALI, kaynak çeşitlilik kuralları `cache_control: {"type": "ephemeral"}` ile cache breakpoint. Tüm çağrılarda aynı prefix → cache hit.
- **Katman 2 — Marka/sektör bağlamı (user blok 1):** Marka ad��, sektör, açıklama, tonalite, renkler, hashtagler `cache_control: {"type": "ephemeral"}` ile cache breakpoint. Aynı marka için tekrarlanan çağrılarda hit.
- **Katman 3 — Dinamik veri (user blok 2):** Ham trend verileri, arama sonuçları, kullanıcı prompt'u. Cache'lenmez.

**Explicit breakpoint uygulanan dosyalar:**
- `layer_a.py` — Kurallar+JSON format system'e taşındı, `_SYSTEM_RULES` modül sabiti
- `layer_b.py` — `_SYSTEM_QUERY_BUILDER` + `_SYSTEM_SYNTHESIZER` modül sabitleri, her iki fonksiyonda system+marka breakpoint
- `layer_c.py` — Kurallar system'e taşındı, system+marka breakpoint
- `ai.py:suggest_ideas` — DİL KURALI system'e taşındı `_STATIC_RULES`, marka bağlamı user blok 1'e

**Top-level cache (küçük prompt'lar):** `ai.py:analyze_website`, `faceless_video.py`, `competitor_analyzer.py` (2 çağrı), `trend_analyzer.py` — `cache_control={"type": "ephemeral"}` top-level. 4096 token eşiği altındaysa SDK sessizce ignore eder.

**Cache loglama:** Layer A/B/C'de `cache_read_input_tokens` ve `cache_creation_input_tokens` loglanıyor.

**Opus 4.7 minimum cache token: 4096.** Kısa system prompt'lar tek başına cache'lenemez. Bu yüzden kurallar+format talimatları system'e taşınarak blok büyütüldü.

**Temperature kuralı (yaratıcı vs analitik çağrılar):**
- **Yaratıcı içerik üretimi → `temperature=1.0` + çeşitlilik prompt talimatı:** `ai.py:suggest_ideas`, `faceless_video.py:generate_script`. Kullanıcı her tıklamada farklı sonuç bekler.
- **Analitik/yapısal çıktı → temperature eklenmez (varsayılan):** `ai.py:analyze_website`, `competitor_analyzer.py` (2 çağrı), `layer_a/b/c.py`, `trend_analyzer.py`. Tutarlılık gerekir — aynı girdi her zaman aynı analiz sonucunu üretmeli.

## 2026-04-16 — Trends: Layer A Karma etiketi kaldırma + Google Trends artırma ✅

**Sorun:** Claude Haiku diversity kuralını tam uygulamadığında backend post-process fazlalık trendleri "Karma" olarak relabel ediyordu. Bu etiket kullanıcıya hiçbir bilgi vermiyordu. Google Trends `cat=t` filtresi TR'de az/hiç sonuç döndürüyordu.

**Değişiklikler:**
1. **`layer_a.py` prompt** — "Karma source yazma" kuralı eklendi, birleştirme durumunda en güçlü kaynağın etiketi kullanılacak. Olası source listesinden "Karma" çıkarıldı.
2. **`layer_a.py` post-process** — Karma relabel yerine: her kaynaktan score'a göre en iyi 3'ü al, sonra 8'e tamamlamak için overflow'dan yüksek score'luları ekle. Toplam 8 trend garanti.
3. **`google_trends.py`** — Kategori filtreli feed + fallback: önce sektöre özel `cat=` ile çek, 5'ten az gelirse genel TR feed'ini de ekle (dedupe ile). Toplam max 30.

## 2026-04-16 — Trends: Layer A kaynak çeşitlilik iyileştirmesi ✅

**Sorun:** Layer A trendlerinde Google News domine ediyordu (4 keyword x 10 haber = max 25 sonuç), Google Trends sektöre irrelevant genel TR trendleri döndüğü için Claude tarafından eleniyordu, Reddit source etiketi sub-spesifik (`Reddit/r/tech`) geldiği için Claude diversity kuralında parçalanıyordu.

**Değişiklikler:**
1. **`google_trends.py`** — Sektöre göre RSS kategori filtresi eklendi (`_SECTOR_CATEGORY` mapping: teknoloji→`t` Sci/Tech, finans→`b` Business, saglik→`m` Health). Kategori eşleşmeyen sektörler genel feed'i alır.
2. **`google_news.py`** — Per-keyword sonuç cap'i 10→6'ya düşürüldü. Toplam max 25→~18. Diğer kaynakların ağırlığı artar.
3. **`reddit.py`** — Source etiketi `Reddit/r/{sub}` → `Reddit` olarak sadeleştirildi. Claude diversity kuralı (max 3 per source) artık tüm Reddit sonuçlarını tek kaynak olarak sayar.

**Etki:** layer_a.py ve diğer kodlar değişmedi — source modüllerin `fetch(sector)` imzası ve çıktı formatı korundu.

## 2026-04-16 — Trends: Layer B son arama sonuçlarını cache'den oku ✅

**Dosya:** `app/routers/trends.py` — yeni `GET /trends/personal?brand_id=` endpoint'i

**Çözüm:** `brand_trend_cache` tablosundan son kişisel arama sonuçlarını okur. Response: `{ trends, count, fetched_at }`. Frontend "Kişisel Arama" sekmesi açıldığında bu endpoint çağrılır, son arama sonuçları + tarih gösterilir. Kullanıcı "Yeniden Ara" ile yeni arama tetikleyebilir.

**Not:** `GET /personal` route'u `POST /personal`'dan önce deklare edildi (aynı path, farklı method).

## 2026-04-16 — Trends: Layer C eski rapor temizleme (3 ay retention) ✅

**Dosyalar:**
- `app/services/trends/layer_c.py` — `cleanup_old_reports(db)` fonksiyonu eklendi
- `app/routers/internal.py` — `POST /internal/trends/nightly-sweep` endpoint'ine cleanup çağrısı eklendi

**Çözüm:**
- `cleanup_old_reports()`: `generated_at < now() - 3 months` olan `sector_reports` satırlarını DELETE eder, her birinin `pdf_url`'sinden R2 path çıkarıp R2'den de siler
- Nightly sweep (her gün 06:00 TR) sonunda otomatik çalışır — ayrı cron/workflow gerekmez
- Response'a `report_cleanup: { deleted, r2_errors }` eklenir

**Retention politikası:** 3 ay — trend raporları güncelliğini kaybettiği için daha eski raporlar gereksiz DB + R2 yükü oluşturur.

## 2026-04-16 — Phase 6 Sprint 6: Test, Telemetri, Canlıya Alma ✅

**Sentry tekil kaynak hataları:**
- `layer_a.py:_run_source()` içine `sentry_sdk.capture_exception(e)` eklendi — bireysel kaynak hataları (Google News, Reddit, YouTube vb.) artık Sentry'ye ayrı ayrı raporlanıyor (mevcut aggregate warning'e ek olarak).

**trend_analyzer.py deprecation:**
- Dosya başına DEPRECATED docstring eklendi. Yeni geliştirmeler `trends/layer_a.py`, `layer_b.py`, `layer_c.py` kullanacak.

**Load test Layer B senaryosu:**
- `shared/load-tests/locustfile.py`'a `POST /trends/personal` senaryosu eklendi (weight=1). HTTP 402 (kota) başarılı sayılır.

## 2026-04-16 — Phase 6 Sprint 5: Frontend `/trendler` yeniden yazım ✅

**Dosya:** `apps/social/frontend/app/(dashboard)/trendler/page.tsx` (562 satır, tamamen yeniden yazıldı)

**Üç sekmeli tasarım:**
- **Sektör Trendleri (Layer A):** `GET /trends?brand_id=` → sektör paylaşımlı cache, trend kartları, yenile butonu
- **Kişisel Arama (Layer B):** `POST /trends/personal?brand_id=` → Serper+Haiku, kota göstergesi ("5/10 kullanıldı"), "Kişisel Trendleri Ara" butonu
- **Aylık Rapor (Layer C):** `POST /trends/monthly-report?brand_id=` → 202 Accepted, rapor listesi (ready/generating/failed rozetleri), PDF indirme linki, "Yeni Rapor Üret" butonu

**Trend kartları:** title, source badge, relevance score bar, summary, content_opportunity, suggested prompt kutusu, "İçerik Üret" butonu

**Paywall:** Backend 402 → `plan_limit` objesi ile toast + `/fiyatlandirma` yönlendirmesi (UpgradeModal yerine toast tercih edildi — fonksiyonel kayıp yok)

**Fix (2026-04-16):** Frontend error handling uyumsuzluğu düzeltildi — `res.error === 'quota_exceeded'` yerine `res.plan_limit` kontrolüne geçildi. Eski `plan_locked` dalı kaldırıldı, backend'in döndüğü Türkçe mesajlar (`plan_limit.message`) artık doğru gösteriliyor.

## 2026-04-15 — Phase 6 Sprint 4: Layer C Apify + PDF rapor ✅

**Yeni dosyalar:**
- `app/services/trends/layer_c.py` (414 satır) — Apify aktör routing (`SECTOR_ACTOR_MAP`), paralel aktör çalıştırma, Claude Haiku ile 12 trend sentezi, Jinja2+weasyprint PDF render, R2 upload, maliyet tracking
- `app/services/apify_client.py` (62 satır) — `run_actor(actor_id, input_payload, timeout)` wrapper, `run-sync-get-dataset-items` endpoint'i
- `app/services/pdf_renderer.py` (21 satır) — `render_sector_report(data) -> bytes`, Jinja2 template + weasyprint
- `app/templates/sector_report.html` (78 satır) — A4 PDF template, 12 trend kartı, kaynak özeti, maliyet tablosu

**Apify aktörleri:** TikTok (`clockworks/free-tiktok-scraper`), Instagram (`apify/instagram-scraper`), Trendyol (`tyegen/trendyol-product-scraper`) + sektör-bazlı routing

**Endpoint'ler:**
- `POST /trends/monthly-report?brand_id=` → `check_trend_quota("layer_c")` → BackgroundTasks → 202 Accepted
- `GET /trends/reports?brand_id=` → son 20 rapor listesi (status, pdf_url, maliyet)
- `GET /trends/reports/{report_id}` → tek rapor detayı (sahiplik JOIN kontrolü)

**Dependency:** `weasyprint==63.1` + `pydyf==0.11.0` requirements.txt'e eklendi

## 2026-04-15 — Phase 6 Sprint 3: Layer B Serper.dev + Claude Haiku ✅

**Yeni dosyalar:**
- `app/services/trends/serper_client.py` — Serper.dev Google Search wrapper. `search(query, gl, hl, num)` + `extract_items(result)` helper'ı. SERPER_API_KEY yoksa ValueError.
- `app/services/trends/layer_b.py` — Kullanıcı tetiklemeli kişisel trend pipeline.
  - `_build_search_queries(brand, recent_posts)` — Claude Haiku ile 3-4 sorgu önerisi (fallback: sektör adı + son postlar)
  - Paralel Serper çağrıları → dedupe → Claude Haiku sentez (8 trend)
  - Token sayıları iade edilir (`_prompt_tokens`, `_completion_tokens` geçici olarak ilk item'a stash'lenir, endpoint'te okunup pop edilir)
  - `brand_trend_cache` upsert (`serper_queries` int + token kolonları)

**billing.py** — iki yeni helper:
- `TREND_QUOTAS` dict (ADR-4): Starter 5 / Pro 10 / Business 20 / Agency 50 Layer B; Pro+'ya Layer C kota eklendi (1/3/10)
- `check_trend_quota(account_id, layer, db)` → aylık sayaç kontrol, 402 `trend_quota_reached` veya `trend_quota_not_available`
- `increment_trend_usage(account_id, layer, cost_usd, db)` → `trend_usage` upsert (`layer_b_count` + `layer_b_cost_usd` toplama)

**trends.py** — yeni endpoint:
- `POST /trends/personal?brand_id=` → Layer B tetik. Akış: `assert_brand_owned` → `check_trend_quota('layer_b')` → `fetch_personal_trends` → maliyet hesapla (Serper $0.001 × çağrı + Haiku ($1/M input + $5/M output)) → `increment_trend_usage`
- `/personal` route'u `/{trend_index}/create-post`'tan ÖNCE deklare edildi (trend_index int parser'a düşmesin diye).

**Tamamlandı:**
- [x] SERPER_API_KEY Coolify env'e eklendi
- [x] Canlı smoke test: `/trends/personal` çağrısı başarılı, quota doğrulandı
- [x] Frontend `/trendler` sekmeli rewrite (Sprint 5 ✅)

**Backlog (düşük öncelik):**
- pytrends 429 debug, Pinterest selector, Claude synthesis timeout/rate-limit (9/12 sektörde fallback'e düşüyor)

## 2026-04-15 — Phase 6 Sprint 2: Layer A nightly sweep ✅

**Özet:** 9 ücretsiz kaynak + Claude Haiku orchestrator + n8n cron 06:00 TR. Canlı doğrulama (3. sweep sonrası):
- ✅ `jsonb_typeof(trends) = 'array'` — codec double-encode fix (codec + `::jsonb` cast çakışması) `database.py` jsonb codec sayesinde çözüldü. Kritik: `json.dumps()` + `$N::jsonb` cast KULLANMA, dict/list'i doğrudan parametre olarak geç.
- ✅ Reddit RSS (`top.rss?t=day`) — `.json` 403'lendiği için Atom feed parser'ı yazıldı. Sektör başına 10-20 başlık.
- ✅ trends24.in HTML scrape — regex esnetildi (`<ol[^>]*trend-card__list[^>]*>`, class attribute tırnaksız da eşleşir). Sektör başına 20 başlık.
- ✅ Google News RSS — 25 başlık/sektör, sabit çalışıyor.
- ⚠️ Claude synthesis — 12 sektörden yalnızca 3'ünde (egitim, moda-tekstil, yemek-gida) 8 trend döndü; geri kalan 9'unda fallback (n=1). Nedeni muhtemelen rate-limit / timeout. `run_in_executor` ile blocking çağrı loop'u bloklamasın diye taşındı ama sorun devam ediyor. **BACKLOG**.
- ❌ Google Trends (pytrends) — tüm sektörlerde 0. TR region'da 429 yiyor olabilir. **BACKLOG**.
- ❌ Pinterest Trends — target 6 sektörde bile 0. Selector kırık. **BACKLOG**.

**n8n workflow:** `Trends Nightly Sweep` (ID: `jnjxwCmu7OMVRvwn`), 2 node (schedule + HTTP sweep), cron `0 6 * * *` Europe/Istanbul, active. Hata bildirimi: Telegram yerine Sentry (`sentry_sdk.capture_message(level="warning")` — `layer_a.run_nightly_sweep` sonunda errors boş değilse tetiklenir).

**Internal endpoint:** `POST /internal/trends/nightly-sweep` (X-Internal-Key), `run_nightly_sweep(db)` çağırır.

**Backlog (Sprint 2 polish):**
- Layer A Claude synthesis timeout fix (9/12 fallback'e düşüyor)
- pytrends 429 — SerpAPI fallback düşünülebilir veya retry + backoff
- Pinterest Trends selector güncelleme
- YOUTUBE_API_KEY / PRODUCT_HUNT_TOKEN / EVDS_API_KEY / SPOTIFY env'e eklenmeli (opsiyonel — şu an 0 döndürüyorlar ama crash yok)

## 2026-04-15 — Phase 6 Sprint 1: Şema + Sektör Modeli ✅

**Kapsam:** Hiyerarşik sektör tablosu, üç katmanlı trend mimarisi için veri tabanı iskeleti, brands dual-write.

**Migration'lar (prod'da çalıştırıldı):**
- `019_sectors_hierarchy.sql` — `social.sectors` tablosu + 11 ana sektör seed (teknoloji, e-ticaret, yemek, saglik, egitim, moda, turizm, finans, gayrimenkul, otomotiv, genel). `social.brands.sector_id UUID` kolonu eklendi, mevcut 1 brand (`Otomaix`) text sector değerinden `teknoloji` slug'ına map edildi. `parent_sector_id` kolonu ile ileride alt sektör eklemek migration ile mümkün, kod değişmez.
- `020_trend_layers.sql` — 4 yeni tablo: `sector_trend_cache` (layer A/C paylaşımlı, PK sector_id+layer), `brand_trend_cache` (Layer B marka-bazlı), `trend_usage` (aylık kullanım sayaçları, account_id+year_month PK), `sector_reports` (Layer C PDF metadata + status/generating/ready/failed). Eski `social.trend_cache` tablosuna DEPRECATED yorumu eklendi — rollback için silinmedi.

**Yeni Python dosyaları:**
- `app/services/sector_resolver.py` — `resolve_sector_id(db, text)` helper. Türkçe karakter ASCII dönüşümü, boşluk → tire, cache (Redis 1 saat TTL). Eşleşme yoksa 'genel' sektörüne düşer. Kısmi eşleşme destekler ("Teknoloji ve Yazılım" → teknoloji).

**Değişen Python dosyaları (dual-write):**
- `app/routers/brands.py` — `create_brand` ve `update_brand` endpoint'leri artık `sector` TEXT yazarken `sector_id` UUID'yi de `resolve_sector_id` üzerinden set eder. Eski TEXT kolonu korunuyor — mevcut `ai.py`, `posts.py`, `trends.py`, `competitors.py` router'ları değişmeden çalışır (hepsi `brand["sector"]` TEXT okur).
- `app/models/schemas.py` — `BrandOut`'a `sector_id` opsiyonel alan eklendi. Phase 6 trend modelleri eklendi: `SectorOut`, `TrendItem`, `TrendUsageOut`, `SectorReportOut`.

**Etki analizi doğrulaması:**
- Mevcut kodun hiçbir yerinde `sector_id` okunmuyor → yalnızca yeni Layer A/B/C kodu kullanacak
- `sector` TEXT kolonu değişmedi, frontend/backend mevcut akışları etkilenmez
- Risk: sıfır (yeni kolon + idempotent migration)

**Doğrulama:** `SELECT slug, display_name FROM social.sectors` → 11 satır; mevcut `Otomaix` brand'i `sector='Teknoloji'` → `sector_id=310ee1b9-...` olarak map edildi.

## 2026-04-14 — N8N-9: Türkiye Takvimi workflow aktive

## 2026-04-14 — N8N-9: Türkiye Takvimi workflow aktive

Analiz raporundaki P2 bulgusu N8N-9. Workflow (`tTk1VroTh4AS8lxI`) daha önce kurulmuş, 2026 tatilleri `social.public_holidays` tablosunda zaten 22 satır olarak mevcut (manuel seed veya önceki test çalıştırması). Tek eksik: workflow `active: false` durumundaydı — cron `0 0 1 1 *` (her yıl 1 Ocak 00:00 Europe/Istanbul) inactive olduğu için 2027 1 Ocak'ta tetiklenmeyecek, 2027 tatilleri DB'ye hiç yüklenmeyecekti.

**Fix:** n8n public API `POST /workflows/{id}/activate` → `active: true`. Kod değişikliği yok, local JSON zaten güncel. `workflowPublishHistory` event `activated`. Kritik kontrol noktası: 2027-01-01 00:00 Istanbul tick'inde execution log'unda Telegram bildirimi "✅ 2027 yılı Türkiye takvimi güncellendi. N özel gün eklendi."

## 2026-04-14 — B-3: autoposting_configs telegram kolonları temizlik

Analiz raporundaki P2 bulgusu B-3. Telegram ayarları commit `58af268` ile workspace seviyesine taşınmış, eski `social.autoposting_configs.telegram_bot_token` / `telegram_chat_id` kolonları kod seviyesinde zaten kullanılmıyordu:

- `routers/internal.py:44` — `SELECT ac.*, ..., w.telegram_bot_token, w.telegram_chat_id` JOIN ile **workspaces** tablosundan okuyor (alias `w`), autoposting_configs değil.
- `routers/autoposting.py` — INSERT/UPDATE'lerde telegram alanları yok.
- Frontend — `ayarlar/page.tsx` `/settings` endpoint'ini (workspace) kullanıyor, `otomatik-yayin/page.tsx` hiç telegram referansı taşımıyor.

Migration 018 (`018_drop_autoposting_telegram_cols.sql`) prod'da çalıştırıldığında her iki kolon `DROP COLUMN IF EXISTS` NOTICE'ı ile "does not exist, skipping" döndü — yani kullanıcı workspace taşıma sırasında kolonları da düşürmüş. Migration yine de idempotent kayıt olarak repo'ya girdi (versiyon geçmişi).

## 2026-04-14 — P2 temizlik bloğu: B-6, B-7, B-8

Analiz raporundaki P2 temizlik maddelerinden üçü tek blokta halledildi. Hepsi düşük risk.

### B-7 — `_parse_brand_kit` helper ortaklaştırma
`routers/posts.py:30` ve `routers/ai.py:18` aynı `_parse_brand_kit(raw)` helper'ını satır satır aynı şekilde duplicate ediyordu. Yeni dosya `app/core/utils.py` oluşturuldu ve `parse_brand_kit()` buraya taşındı; her iki router `from app.core.utils import parse_brand_kit as _parse_brand_kit` ile import ediyor (mevcut underscore-prefixed çağrı noktalarını değiştirmemek için alias). 5 call site (posts.py'de 3, ai.py'de 2) değişmeden çalışıyor. Risk: sıfır — pure refactor.

### B-8 — `publish_post` router pre-check
`POST /posts/{id}/publish` endpoint'i doğrudan servise düşüyordu; `output_url` None veya status `draft`/`generating` durumunda servis ya ValueError fırlatıyor (FastAPI 500) ya da yanlış bir işleme girişiyordu. Router'a iki satır pre-check eklendi:
- `output_url` yoksa → 409 "Post içeriği henüz üretilmemiş"
- `status in ('draft','generating')` → 409 "Post henüz hazır değil"

`failed`, `ready`, `partially_published`, `rejected` izin verilen state'ler (retry use-case'i için). `published` ve `publishing` durumları servis içinde zaten idempotent şekilde ele alınıyor (F-2 rev-3'teki `SELECT FOR UPDATE` + short-circuit). `assert_post_owned` zaten post row'u dict döndüğü için ek DB query yapılmadı.

### B-6 — `trend_cache` UPSERT
İki call site (`routers/trends.py:refresh_trends` + `services/trend_analyzer.py:get_or_fetch_trends`) her çağrıda yeni INSERT yapıyordu, tabloda `UNIQUE(sector)` yoktu → her sector için duplicate satırlar birikiyordu. Okuma mantığı `ORDER BY fetched_at DESC LIMIT 1` ile en yenisini alıyordu, yani functionally çalışıyor ama tablo sonsuza kadar büyüyordu.

**Migration 017_trend_cache_unique.sql** (prod'da çalıştırıldı — 5 duplicate silindi, constraint eklendi ✅):
```sql
DELETE FROM social.trend_cache a USING social.trend_cache b
WHERE a.sector = b.sector AND a.fetched_at < b.fetched_at;
ALTER TABLE social.trend_cache ADD CONSTRAINT trend_cache_sector_unique UNIQUE (sector);
```

Her iki INSERT artık `ON CONFLICT (sector) DO UPDATE SET trends=EXCLUDED.trends, fetched_at=now()`. Okuma query'si değişmeden çalışıyor (artık her sector için tek row, `ORDER BY ... LIMIT 1` hâlâ doğru sonuç veriyor).

## 2026-04-14 — N8N-4: CRM-4 "Has Churn Risk?" IF tip hatası fix

Analiz raporundaki P0 bulgusu N8N-4'ün iki parçası vardı:

**Parça 1 — Postgres credential host (`::1` → `host.docker.internal`):** Doğrulama sırasında en son CRM-4 (execution #80, 15:09) ve CRM-5 (execution #56, 10:00) çalıştırmalarının **success** olduğu görüldü. Credential bu oturum öncesinde bir noktada düzeltilmiş (muhtemelen Coolify iç network DNS ayarı veya n8n UI'dan manuel) — ek eylem gerekmedi.

**Parça 2 — CRM-4 IF node tip hatası:** Execution #55'in hata mesajı `Wrong type: '0' is a string but was expecting a number [condition 0, item 0]`. Kök neden: Postgres `COUNT(*)` sonucu string olarak dönüyor (`{count: '0'}`), IF v2.2 node strict type validation ile number operator'a string besleyince fırlatıyor.

**Fix** (n8n REST API PUT `/workflows/os5XonE1TtptDPBC`, lokal kopya `shared/n8n-workflows/crm-automations.json` → CRM-4):
- `Has Churn Risk?` IF node'unda `conditions.options.typeValidation: "strict"` → `"loose"` (belt-and-suspenders)
- `conditions[0].leftValue`: `={{ $json.count }}` → `={{ Number($json.count) }}` (açık tip dönüşümü)

**Doğrulama:** Canlı PUT 200 döndü. Execution #80'de "Has Churn Risk?" node'u 0 item ile true branch'e hiç düşmediği için asıl test koşulu yarın 09:00 schedule trigger'da gerçek churn-risk kaydı varsa doğrulanacak.

## 2026-04-14 — N8N-5: Auto Posting Scheduler splitInBatches → Code map

Analiz raporundaki P0 bulgusu N8N-5 (Auto Posting Scheduler `Her Config İçin` splitInBatches loop kablolaması eksik — tek cycle'da sadece ilk config işleniyordu) çözüldü.

**Çözüm yaklaşımı:** N8N-7 (Scheduled Post Publisher) fix'inde öğrenilen Code map pattern'i uygulandı. splitInBatches v3'ün done/loop output indeks belirsizliğinden kaçınmak için, `splitInBatches` + `Rastgele Seçim` iki ayrı node'u tek bir Code node'da birleştirdik. Yeni `Her Config İçin` (code) node'u `$input.first().json.data.map(config => ({json: {...rastgele seçim}}))` ile her config'i ayrı item olarak açıyor, sonraki HTTP Request (`Post Üret`) ve IF (`Telegram Onayı Gerekli mi?`) n8n'in native item iteration'ı ile her item için sırayla çalışıyor.

**Değişiklikler** (n8n REST API PUT `/workflows/Nz4651wCfBHP4G9l`, lokal kopya `shared/n8n-workflows/auto-posting-scheduler.json`):
1. `split-configs` (type `n8n-nodes-base.splitInBatches`) → type `n8n-nodes-base.code` olarak değiştirildi, adı "Her Config İçin" korundu
2. `pick-random` (eski "Rastgele Seçim" Code node) tamamen kaldırıldı — mantığı yeni node'a taşındı
3. `Post Üret` ve `Telegram Onay Tetikle` body expression'larındaki `$('Rastgele Seçim').item.json.*` referansları `$('Her Config İçin').item.json.*` olarak güncellendi
4. `Telegram Onayı Gerekli mi?` IF node'unun leftValue'u aynı şekilde `$('Her Config İçin').item.json.telegram_approval`
5. Connections: `Config Var mı? true → Her Config İçin → Post Üret → ...` — doğrudan, splitInBatches loop-back yok
6. Workflow `active: true` korundu

**Doğrulama:** Update PUT 200 döndü, aktif state bozulmadı. Çoklu konfig testi için bir sonraki 30dk tick'te (veya n8n UI "Execute Workflow") execution log'unda `Her Config İçin` output'unda config sayısı kadar item görünmelidir. Due config yoksa `Config Yok` noOp branch'ine düşer (normal).

**Öğrenilen ders (tekrar):** n8n v1+ splitInBatches node'unu mümkünse tercih etme — Code node `$input.all().map()` veya `$input.first().json.data.map()` + native item iteration hem daha basit hem daha debuggable. N8N-7'de buna karar verilmişti, N8N-5 aynı pattern'i benimsedi.

## 2026-04-14 — asyncpg jsonb codec fix (uzun süredir var olan bug)

**Bulunan bug:** asyncpg default olarak jsonb kolonlarını **str** (JSON-encoded string) olarak döndürüyordu. Sonuç: `dict(row)["analysis_data"]` bir string'di, frontend'de `analysis_data?.website` her zaman undefined dönüyordu. Rakip analiz paneli sayfada hiç veri göstermiyordu (B-5 fix'i öncesinde de böyleydi — senkron path'te `competitor["analysis_data"] = analysis_data` doğrudan dict ile override edildiği için ilk ekleme anında fark edilmemişti).

**Fix (`app/core/database.py`):**
```python
async def _init_connection(conn):
    await conn.set_type_codec("jsonb", encoder=json.dumps, decoder=json.loads, schema="pg_catalog")
    await conn.set_type_codec("json",  encoder=json.dumps, decoder=json.loads, schema="pg_catalog")

_pool = await asyncpg.create_pool(..., init=_init_connection)
```

**Geriye uyumluluk:** Mevcut INSERT/UPDATE kodları `$N::jsonb` text cast ile çalıştığı için codec encoder tetiklenmez — text parametre olarak geçer, postgres server-side cast eder. Lokal test (backward compat + forward dict decode) ile doğrulandı:
- `fetchrow` sonrası `row['analysis_data']` → `dict` (önceden: str)
- `json.dumps(dict)` + `$1::jsonb` insert → hala çalışır

**Etkilenen endpoint'ler (hepsi artık dict dönecek):**
- `GET /competitors/{id}/analysis` — analiz paneli artık dolu dönecek
- `GET /competitors/report/summary` — `generate_competitor_report` artık hata vermeden çalışır (`(a.get("analysis_data") or {}).get("website", {})` dict üzerinde)
- `brand_kit` okuyan tüm router'lar (brands, posts, ai, webhooks, internal, trends) — mevcut `isinstance(raw, str)` guard'ları nedeniyle zaten dict/str ikisini de handle ediyordu, codec sonrası sadece dict branch'ı çalışacak (değişiklik yok)

## 2026-04-14 — B-5: Rakip analizi asenkron BackgroundTasks'a taşındı

Analiz raporundaki P1 bulgusu B-5 (`POST /competitors` 30+ sn senkron blokluyor, Cloudflare 504 + uvicorn worker tükenmesi riski) çözüldü.

**Migration 015_competitor_status.sql** (prod DB'de çalıştırıldı ✅):
- `social.competitor_analyses.status TEXT NOT NULL DEFAULT 'ready'` — `analyzing | ready | failed`
- `social.competitor_analyses.error_message TEXT` — hata mesajı (failed durumu için)
- `idx_competitor_analyses_status` partial index (WHERE status='analyzing') — bekleyen işler sorgusu için
- Mevcut satırlar default ile 'ready' kabul edilir (geriye uyumluluk)

**`competitors.py` refactor:**
- `_run_analysis_task(competitor_id)` modül seviyesinde async helper. Kendi pool bağlantısını `get_pool()` ile alır (request-scoped `db` yield bittiği için kullanılamaz). `run_full_analysis` başarıysa analysis_data+status='ready' UPDATE'i, exception durumunda status='failed'+error_message UPDATE'i.
- `POST /competitors` → status_code=202, `BackgroundTasks` dependency, INSERT status='analyzing', `background_tasks.add_task(_run_analysis_task, row_id)`, hemen row döner.
- `POST /{id}/refresh` → aynı pattern, eğer halihazırda 'analyzing' ise 409 Conflict.
- `GET /competitors` ve `GET /{id}/analysis` responselarına `status` ve `error_message` eklendi.

**Frontend (`rakip-analizi/page.tsx`):**
- `Competitor` tipine `status: CompetitorStatus` + `error_message` eklendi.
- Polling useEffect: `status='analyzing'` olan rakipler için 4sn'de bir `GET /{id}/analysis` çağrısı, sonuç gelince state update + seçili ise `selectedAnalysis` de güncellenir, toast (success/error) gösterilir.
- `handleRefresh` 202 sonrası lokalde status='analyzing' işaretler, polling effect devreye girer.
- Modal toast: "eklendi ve analiz başlatıldı" → "eklendi, analiz arka planda çalışıyor..."
- Kart rozetleri: `analyzing` → spinner + "Analiz ediliyor...", `failed` → destructive badge + error tooltip.

**Neden BackgroundTasks + polling, Celery/RQ değil:**
- Mevcut stack'te ayrı worker yok, Redis sadece cache/rate-limit için. FastAPI `BackgroundTasks` aynı event loop'ta request sonrası çalışır — tek uvicorn worker'da sorun yok.
- Uzun analiz (30-60 sn) worker'ı bloklamaz çünkü `run_full_analysis` zaten async (httpx + Anthropic SDK). Diğer istekler engelsiz akar.
- Eğer ilerde çok sayıda eşzamanlı analiz yapılırsa (şu an 10/saat rate limit var) Celery'ye geçiş düşünülür.

## 2026-04-14 — N8N-1: Telegram Onayla/Reddet credential migration

Analiz raporundaki P0 bulgusu N8N-1 (Telegram Onayla/Reddet runtime error) çözüldü.

**Bulunan kök neden:** Her iki workflow'daki HTTP Request node'ları (`Yayınla` ve `Reddet`) `X-Internal-Key` header'ını **hardcoded** tutuyordu ve bu değer N8N-2 fix'inden önceki dönemden kalan **truncated** (57 char, son 7 char eksik) versiyondu — tam olarak Coolify env truncation bug'ının kopyası. Üstüne `continueOnFail: true` her iki node'da da aktifti, böylece çağrılar 401 döndüğünde hata yutulup Telegram bildirimi + success HTML yanıtı yine de kullanıcıya gösteriliyordu. Net etki: Onayla butonuna basan kullanıcı "✅ İçerik onaylandı" mesajı alıyor ama post gerçekte hiç yayınlanmıyordu.

**Yapılan değişiklikler** (n8n REST API üzerinden, `/tmp/fix-telegram-wf.py`):
1. **Telegram Onayla** (`aQ8neGzs3PQp8DMl`) → `Yayınla` node:
   - `headerParameters.X-Internal-Key` silindi
   - `authentication: genericCredentialType`, `genericAuthType: httpHeaderAuth`, credential `Otomaix Internal API Key` (id `nFP1FbcwkIw8n9SS`)
   - `continueOnFail` kaldırıldı → backend hataları artık execution'da visible
2. **Telegram Reddet** (`9kp6bCFl0ys6TbVu`) → `Reddet` node: aynı migration (PATCH `/internal/posts/{id}/status`)
3. Local JSON kopyaları oluşturuldu:
   - `shared/n8n-workflows/telegram-onayla.json`
   - `shared/n8n-workflows/telegram-reddet.json`

**Doğrulama:**
- Reddet webhook'u gerçek `post_id` ile test edildi → execution #65 `success`, backend status PATCH 200 döndü, kullanıcıya ❌ HTML yanıtı gösterildi.
- Onayla webhook'u geçersiz UUID ile test edildi → execution #66 `error` (beklenen — continueOnFail kaldırıldığı için hata artık gizlenmiyor). Backend 500 dönüyor (publish-now endpoint'i non-existent post için 404 yerine 500 atıyor — bu ayrı bir backend iyileştirme konusu, N8N-1 scope'u dışında).
- Credential doğru çalışıyor: 500 dönmesi auth'un geçtiğini gösteriyor (yoksa 401 olurdu).

**Not:** Telegram bildirim node'larındaki `continueOnFail: true` korundu — bot token yanlışsa ana iş (yayın/reddet) yine de tamamlanmalı, sadece kullanıcıya Telegram mesajı gitmesin.

### N8N-1 rev-2: Telegram İçerik Onay workflow'u da aynı bug
İlk fix commit'inden sonra canlı testte kullanıcı "Onay iste" butonuna bastı, post `reviewing` oldu ama Telegram mesajı gelmedi. Execution #70 incelendiğinde **Telegram İçerik Onay** (`D49KNE35cONz2APb`) workflow'unda `Post Detayı Al` node'unun da **aynı truncated X-Internal-Key**'i hardcoded taşıdığı, backend'den 401 alıp `continueOnFail` ile fallback değerlere düştüğü bulundu (`image_url: null`, `caption: "Henüz caption üretilmedi"`). Ardından `Fotoğraf Gönder` Telegram API'sine null image_url yollayıp 400 "wrong remote file identifier" alıyordu — yine continueOnFail ile maskelenmişti ve üst seviye execution status `success` görünüyordu.

**Fix:** `Post Detayı Al` node'u aynı credential migration'ına tabi tutuldu (`Otomaix Internal API Key`), `continueOnFail` kaldırıldı. Local kopya: `shared/n8n-workflows/telegram-content-approval.json` güncellendi.

**Öğrenilen ders:** Bu workflow grubundaki (`aQ8neGzs3PQp8DMl`, `9kp6bCFl0ys6TbVu`, `D49KNE35cONz2APb`) TÜM HTTP Request node'larını tarayıp `/internal/*` çağrısı yapan her birini credential'a migrate etmek gerekir. İlk fix'te yalnızca 2 workflow tarandığı için 3.sü atlandı. İleride başka internal endpoint çağırıyor olursa aynı kontrol yapılmalı.

## 2026-04-14 — N8N-7: Scheduled Post Publisher workflow + internal route order fix

Analiz raporundaki P0 bulgusu N8N-7 (scheduled post publisher eksik) çözüldü.

### Backend fix: `internal.py` route sıralaması
`GET /internal/posts/{post_id}` rotası `GET /internal/posts/scheduled-due`'den önce tanımlıydı — FastAPI deklarasyon sırasına göre eşleştiği için `/internal/posts/scheduled-due` çağrısı `{post_id}` route'una düşüp `UUID("scheduled-due")` → ValueError → HTTP 500 veriyordu. Canlı test sırasında `curl` ile yakalandı.

**Fix:** İki rota swap edildi — `scheduled-due` artık `{post_id}` route'undan önce deklare. Docstring'e not eklendi ki gelecekte kimse yeniden taşımasın. Dashboard stats endpoint'inde (`posts.py:/stats/summary`) aynı tuzağa daha önce dikkat edilmişti, tutarlılık için internal router da aynı şekilde.

### Yeni n8n workflow: `Scheduled Post Publisher`
- **ID:** `u650xJO6TLoh1Wcb`
- **Dosya:** `shared/n8n-workflows/scheduled-post-publisher.json`
- **Trigger:** her 5 dakikada bir `scheduleTrigger`
- **Akış:**
  1. `Zamanı Gelen Postlar` → `GET https://api.otomaix.com/internal/posts/scheduled-due` (httpHeaderAuth credential `Otomaix Internal API Key`)
  2. `Post Var mı?` (IF: `data.length > 0`) → doluysa `Her Post İçin Item` Code node'una, boşsa `Post Yok` no-op'a
  3. `Her Post İçin Item` (Code node): `$input.first().json.data.map(p => ({json: p}))` → n8n native item iteration için array'i tek tek item'lara açar
  4. `Yayınla` → `POST https://api.otomaix.com/posts/{{ $json.post_id }}/publish-now` (aynı credential, boş JSON body) — n8n HTTP node her item için ayrı çağrı yapar
- **splitInBatches kullanılmıyor**: İlk denemede splitInBatches typeVersion 3'ün `done`/`loop` output indekslerini yanlış kabloladık → Code node `{}` boş output üretti → `Yayınla` URL'si `/posts//publish-now` oldu → 405. Çözüm: splitInBatches'i kaldırıp Code map + native item iteration kullandık. N8N-5'teki auto-posting-scheduler'da da aynı patterni uygulayacağız ilerleyen adımlarda.
- **Idempotency:** Backend `publish_post` servisi F-2 rev-3'te zaten `SELECT FOR UPDATE` + intermediate `status='publishing'` koruması ekledi. 5 dakikalık tick'ler sırasında aynı post birden fazla kez "due" listesinde çıkarsa bile tek bir gerçek Upload-Post çağrısı yapılır.

**Doğrulama (push sonrası Coolify redeploy bittikten sonra):**
- `curl -H "X-Internal-Key: ..." https://api.otomaix.com/internal/posts/scheduled-due` → HTTP 200 dönmeli (önceden 500)
- Workflow aktive edilmeli + manuel execution yeşil olmalı

## 2026-04-14 — N8N-2 + N8N-3: Auto Posting Scheduler fix + aktifleştirme

Analiz raporundaki P0 bulguları N8N-2 (workflow inaktif) ve N8N-3 (yanlış URL + hardcoded X-Internal-Key) çözüldü.

**Bulunan gerçek sebep:** Workflow'un mevcut URL'leri `http://178.104.7.200:8000/internal/...` ile **Coolify panel login sayfasını** hedefliyordu (Coolify UI 8000 portundan servis ediliyor, backend değil). Yani workflow hiçbir zaman çalışmamıştı. Önceden `api.otomaix.com` denendiğinde 401 alındığı için IP'ye döndürüldüğü kaydedilmiş, ancak 401'in gerçek nedeni Coolify'da `INTERNAL_API_KEY` env var'ının **7 karakter eksik** (truncated) paste edilmiş olmasıydı.

**Yapılan değişiklikler:**
1. Coolify `otomaix-social-backend` → `INTERNAL_API_KEY` tam 64 char değer ile güncellendi (kullanıcı tarafından), redeploy edildi.
2. Yeni n8n credential oluşturuldu: **`Otomaix Internal API Key`** (id: `nFP1FbcwkIw8n9SS`, type: `httpHeaderAuth`, name: `X-Internal-Key`).
3. Auto Posting Scheduler (`Nz4651wCfBHP4G9l`) workflow'unda iki HTTP Request node:
   - `Zamanı Gelen Configler` → `http://178.104.7.200:8000/...` → `https://api.otomaix.com/internal/autoposting/due`
   - `Post Üret` → `https://api.otomaix.com/internal/autoposting/trigger`
   - Her ikisinde de `headerParameters.X-Internal-Key` kaldırıldı; `authentication: genericCredentialType` + yeni credential referansı eklendi.
4. `Telegram Onay Tetikle` node URL'i `http://178.104.7.200:5678/webhook/...` → `https://n8n.otomaix.com/webhook/telegram-content-approval` (aynı n8n'e self-ref public URL üzerinden).
5. Workflow `active: true` yapıldı.
6. Lokal version-control kopyası güncellendi: `shared/n8n-workflows/auto-posting-scheduler.json`.

**Doğrulama:** `curl -H "X-Internal-Key: ..." https://api.otomaix.com/internal/autoposting/due` → `{"success":true,"data":[]}` HTTP 200.

**⏳ Hâlâ açık (aynı workflow'da bir sonraki adım):**
- **N8N-5** (P1) — `splitInBatches` loop kablolaması eksik. Şu an `Her Config İçin` → `Rastgele Seçim` var ama done branch'ı ve loop-back bağlantısı yok. Çoklu config aynı cycle'da işlenmez; sadece ilki. Otomatik yayın tek markalı müşteriler için bu halde çalışır, çok markalılar için **ayrı bir fix** gerekiyor.

## 2026-04-14 — Dashboard stats endpoint

Yeni endpoint: `GET /posts/stats/summary?brand_id=<uuid>` (`routers/posts.py`).

- `assert_brand_owned` ile korunur.
- Tek query: `COUNT(*) FILTER (WHERE created_at >= date_trunc('month', now()))` + `COUNT(*) FILTER (WHERE status='published')`.
- Response: `{ generated_this_month: int, published_total: int }`.
- Rota dynamic `/{post_id}` rotasından **önce** yerleştirildi, aksi halde `stats` string'i UUID parser'a düşerdi.
- Frontend dashboard'ın hardcoded `0` stat kartları için eklendi.

## 2026-04-14 — Teknik Analiz Raporu Fix'leri (rev-1)

### [F-2 rev-3] publish_post idempotency — çift yayın fix
Canlı test sırasında tek bir "Şimdi Yayınla" tıklamasında Instagram'a 4 post gittiği raporlandı. Kök neden: hem frontend hem backend tarafında yarış koşulu — `useState` tabanlı guard async olduğu için hızlı arka arkaya tıklamalar birden çok HTTP isteği geçiriyor, backend'de de aynı `post_id` için concurrency koruması yoktu.

**Backend fix** (`services/upload_post.py:publish_post`):
- `async with db.transaction()` + `SELECT ... FOR UPDATE` → aynı post_id için paralel çağrılar row-level lock ile serileştiriliyor
- Transaction içinde status kontrolü: `published` ise `{note: "already_published"}` döner, `publishing` ise `{note: "already_in_progress"}` döner
- Transaction içinde intermediate status: `UPDATE ... SET status = 'publishing'` — ikinci istek bu flag'i görünce kısa devre yapar
- Bu sayede backend artık tek kaynak olarak Upload-Post'a yalnızca 1 istek gönderiyor, diğerleri idempotent şekilde dönüyor

**Yeni post status**: `'publishing'` (transient). Yayın sırasında görünür, başarı sonrası `published`'a, hata durumunda `failed`'a geçer.

### [F-2 rev-2] Upload-Post.com entegrasyonu tamamen yeniden yazıldı
Test sırasında mevcut `upload_post.py` servisinin **hayal edilmiş** bir API şeması kullandığı fark edildi (`/v1/oauth/{platform}?token=...&state=...`) — Upload-Post.com'da böyle bir endpoint yok, tüm OAuth çağrıları 404 dönüyordu. Gerçek API (OpenAPI spec'ten doğrulandı):

- **Base URL**: `https://api.upload-post.com/api` (önceden yanlış: `/v1`)
- **Auth**: `Authorization: Apikey <key>` (önceden yanlış: HS256 JWT üretip Bearer)
- **Akış**: 1 marka = 1 Upload-Post profile
  1. `POST /uploadposts/users` → profile oluştur (idempotent, 409 = zaten var)
  2. `POST /uploadposts/users/generate-jwt` → `{username, redirect_url, platforms}` → `access_url` döner (48h, tek kullanımlık)
  3. Kullanıcı `access_url`'yi ziyaret → Upload-Post kendi arayüzünde OAuth'u halleder → `redirect_url`'ye yönlendirir (bizim `/social/callback` endpoint'ine artık gerek yok)
  4. `GET /uploadposts/users/{username}` → `social_accounts: { platform: {handle, display_name, ...} }`
  5. Yayın: `POST /upload` (video) veya `/upload_photos` (görsel) — multipart form, `user=profile_username`, `platform[]=...`

**Değişen dosyalar**:
- `app/services/upload_post.py` — tamamen yeniden yazıldı: `ensure_profile`, `generate_connect_url`, `fetch_social_accounts`, `sync_social_accounts`, `publish_post`. Yayın akışında R2'den medya indirilir ve multipart olarak Upload-Post'a yüklenir.
- `app/routers/social.py`:
  - `oauth_link` → `generate_connect_url()` çağırır, access_url döner
  - `GET /social/accounts` → Upload-Post'tan sync eder, `brand_social_accounts` cache'ine yazar, güncel listeyi döner
  - `/social/callback` → no-op redirect (eski bağlantılar 404 almasın diye bırakıldı)
- `app/routers/posts.py` — değişmedi, `publish_post(post_id, db)` imzası korundu → n8n `/posts/{id}/publish-now` ve frontend `/posts/{id}/publish` akışları şeffaf.

**DB**:
- Migration 014: `social.brands.upload_post_username TEXT` kolonu eklendi (1 marka = 1 profile eşleşmesi). Index: `idx_brands_upload_post_username`.
- `social.brand_social_accounts` artık sadece **cache** olarak kullanılıyor — `sync_social_accounts()` her çağrıda Upload-Post'tan taze veri çeker ve tabloya upsert yapar. `upload_post_token` kolonu ölü (kaldırılmadı, ilerideki cleanup için bırakıldı).

**Profile username formatı**: `brand_<uuid'nin tire silinmiş ilk 16 karakteri>` (örn. `brand_89e7d9666fcb4da1`). Upload-Post plan limitinde 10 profile = 10 markaya kadar destekler; büyürken plan upgrade gerekebilir (kod etkisi yok).

**Canlı smoke test yapıldı**: gerçek API key ile `POST /users`, `POST /users/generate-jwt`, `DELETE /users` 200 döndü, profile dönen JSON şeması beklenene uyuyor.

### [F-2 backend] /social router — sahiplik + hesap listeleme
- `app/routers/social.py:oauth_link` artık `db: asyncpg.Connection` dependency'si alır ve `assert_brand_owned(db, user, brand_id)` ile sahiplik kontrolü yapar (önceki halinde IDOR riski vardı: token sahibi başkasının `brand_id`'sini gönderip OAuth state JWT üretebiliyordu).
- Yeni endpoint: `GET /social/accounts?brand_id=...` → markaya bağlı **aktif** sosyal medya hesaplarını döner (`platform`, `account_name`, `connected_at`). `assert_brand_owned` ile korunur.
- Frontend dashboard "Bağla" butonları ve marka-ayarlari "Sosyal Hesaplar" sekmesi bu iki endpoint'i kullanır.
- `social.brand_social_accounts` tablosunda zaten `(brand_id, platform)` UNIQUE kısıtı var (migration 003), tekrar bağlamada upsert oluyor.

### [B-4] competitors.py — ölü UPDATE bloğu silindi
- `app/routers/competitors.py:add_competitor` içindeki ilk UPDATE (satır 62-71) tamamen kaldırıldı.
- `str(dict).replace("'", '"')` ile JSONB'ye yazmaya çalışan bu blok valid JSON üretmediği için tip hatası fırlatabiliyor ve ardından gelen doğru `json.dumps() + ::jsonb` UPDATE'ini engelliyordu.
- `import json` fonksiyon başına taşındı (tek doğru UPDATE kullanılıyor).
- Risk: yok — tamamen ölü kod silme.

### [F-3 backend] PATCH /posts/{post_id} eklendi
- Caption ve hashtags güncellemek için yeni endpoint (`app/routers/posts.py:update_post`).
- `assert_post_owned` ile sahiplik kontrolü; sadece `caption` ve `hashtags` alanlarını günceller (`PostUpdate` schema).
- İçerik Oluştur Step 3 butonları (Şimdi Yayınla / Takvime Ekle) yayınlamadan önce caption'ı bu endpoint ile DB'ye yazıyor.

### [B-1] Plan limit kontrolleri devreye alındı
- `app/routers/billing.py` içinde tanımlı olan `check_plan_limit(account_id, feature, db)` daha önce hiçbir endpoint'ten çağrılmıyordu — Starter müşteri sınırsız içerik/marka üretebiliyordu.
- Devreye alınan endpoint'ler:
  - `posts.py:generate_post` → `feature="post"` (aylık içerik limiti)
  - `posts.py:create_post` → `feature="post"`
  - `posts.py:generate_faceless_video` → `feature="video"` + `feature="post"`
  - `brands.py:create_brand` → `feature="brand"` (max marka)
  - `avatar.py:create_avatar` → `feature="avatar"`
  - `avatar.py:generate_ugc` → `feature="avatar"` + `feature="post"`
  - `trends.py:create_post_from_trend` → `feature="post"`
- Limit aşıldığında HTTP 402 + `{ error: "plan_limit_reached", message, upgrade_url, current_plan }` döner. Frontend'in mevcut paywall modalı bu detay yapısını bekliyor.
- `assert_brand_owned`/`assert_workspace_owned` çağrılarından **sonra** çalıştırıldı — yetkisiz kullanıcının başkasının limit sayısını artırması engellendi.
- `regenerate_post` ve `publish_*` limit kontrolünden muaf — yeniden üretim ve yayınlama yeni "post" sayılmıyor.
- Risk: orta — aktif ücretli aboneliği olmayan tüm Starter müşteriler 50 post/ay sınırına çarpacak; canlı testte mevcut kullanıcının `accounts.plan_id` değeri ve aylık post sayısı kontrol edilmeli.

### [B-2] Brand/Post/Workspace ownership dependency
- Daha önce çoğu endpoint sadece `get_current_user` ile token doğruluyor; başka bir hesabın `brand_id`/`post_id`/`workspace_id`'sini parametre olarak gönderen herkes erişebiliyordu (IDOR riski).
- `app/core/security.py` içine üç async helper eklendi:
  - `assert_workspace_owned(db, user, workspace_id)` → `social.workspace_members` üzerinden kontrol
  - `assert_brand_owned(db, user, brand_id)` → `brands ⨝ workspace_members`
  - `assert_post_owned(db, user, post_id)` → `posts ⨝ brands ⨝ workspace_members`, post dict döndürür
- Sahiplik zinciri: `JWT.sub == accounts.id → workspace_members.account_id → workspaces → brands → posts`.
- Uygulanan router'lar:
  - `brands.py` — create/list/get/update/delete/kit/logo/intro-video
  - `posts.py` — generate/create/list/regenerate/get/publish/generate-faceless-video (publish-now ve request-approval hariç; ilki X-Internal-Key, ikincisi zaten kontrollü)
  - `calendar.py` — get_calendar_posts, schedule_post
  - `trends.py` — get_trends, refresh_trends, create_post_from_trend
  - `competitors.py` — add/list/get_analysis/refresh/delete/report (competitor_id endpoint'leri için inline JOIN ile sahiplik kontrolü)
  - `autoposting.py` — get/upsert/toggle/upcoming
  - `documents.py` — upload/list/delete (delete inline JOIN)
  - `avatar.py` — create/select-stock/generate-ugc
- `internal.py` ve X-Internal-Key korumalı endpoint'ler değiştirilmedi (n8n için).
- Hata politikası: yetkisiz erişim 401 yerine 404 döner — varlık ifşası önlenir.
- Risk: orta — eski client'lar yanlış brand_id gönderiyorsa 404 alır. Live test ile doğrulanacak.

## Proje Amacı
Otomaix Social uygulamasının FastAPI backend'i. api.otomaix.com'da çalışır.

## Proje Kılavuzları (DEĞİŞTİRME)

Genel mimari: ~/otomaix/docs/00-platform-mimari.md
Phase 1: ~/otomaix/docs/01-social-phase1.md
Phase 2: ~/otomaix/docs/02-social-phase2.md
Phase 3: ~/otomaix/docs/03-social-phase3.md
Phase 4: ~/otomaix/docs/04-social-phase4.md
CRM: ~/otomaix/docs/05-crm-admin.md

Her session başında ~/otomaix/docs içerisindeki 00-platform-mimari.md dosyasını oku ve kaç numaralı fazda çalışıyorsan o faz numaralı md dosyasını da oku.

## VPS Bilgileri
- IP: 178.104.7.200
- Deploy: Coolify (servis adı: otomaix-social-backend)
- URL: https://api.otomaix.com

## Veritabanı
- Host: 127.0.0.1
- Port: 5433
- Database: otomaix
- User: otomaix

## Bağımlılıklar
- PostgreSQL: 127.0.0.1:5433
- Redis: internal
- n8n: https://n8n.otomaix.com
- fal.ai, Cloudflare R2, Upload-Post.com, Supabase Auth, Anthropic Claude

## fal.ai Model Seçimleri (`app/services/fal_ai.py`)
| Tip | Model ID |
|-----|----------|
| Görsel | `fal-ai/flux-2-pro` (FLUX.2 [pro]) |
| Text-to-video | `fal-ai/kling-video/v3/pro/text-to-video` (Kling 3.0 Pro) |
| Image-to-video | `fal-ai/kling-video/v2.5-turbo/pro/image-to-video` (Kling 2.5 Turbo Pro) |

## Gerekli .env Değişkenleri
```
DATABASE_URL=
REDIS_URL=redis://default:<pass>@<coolify-redis-hostname>:6379/0  ✅ Coolify Redis servisi zorunlu (localhost değil)
SUPABASE_URL=https://sqplkkivtkfyozrvnybe.supabase.co
SUPABASE_SERVICE_KEY=
FAL_KEY=
R2_ACCOUNT_ID=
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
R2_PUBLIC_URL=https://assets.otomaix.com
UPLOAD_POST_API_KEY=
ANTHROPIC_API_KEY=   ✅ Coolify'a eklendi
INTERNAL_API_KEY=    ✅ .env'de mevcut — Coolify'a da ekle, sonra redeploy!
```

Not: Telegram bot token ve chat ID artık .env'de tutulmuyor.
Her müşteri kendi bot token'ını Otomatik Yayın wizard'ına girer →
`social.autoposting_configs.telegram_bot_token` / `telegram_chat_id` kolonlarında saklanır.

## Tamamlanan İşler

### Phase 1
- [x] FastAPI proje yapısı kuruldu
  - app/main.py, core/, routers/, models/, services/ oluşturuldu
  - Supabase JWT middleware (JWKS tabanlı)
  - Cloudflare R2 storage abstraction
  - fal.ai async generation + webhook
  - Upload-Post.com OAuth + publish
  - Dockerfile + .dockerignore
- [x] Coolify deploy yapılandırması ✅
- [x] Test scripti: `~/otomaix/shared/test_phase1.sh`

### Phase 2
- [x] Adım 1a — Brand Kit endpoint'leri (`app/routers/brands.py`)
  - `PATCH /brands/{brand_id}/kit` → brand_kit JSONB deep merge
  - `POST /brands/{brand_id}/logo` → light/dark logo upload → R2
  - `POST /brands/{brand_id}/intro-video` → video upload → R2

- [x] Adım 2a — İçerik üretim endpoint'leri (`app/routers/posts.py`)
  - `POST /posts/generate` → post oluştur + fal.ai tetikle
    - Desteklenen `content_type`: `image` | `carousel` | `special_day` | `quote`
    - `special_day`: `special_day_name` + `special_day_category` alanları → `_build_special_day_prompt()` ile fal.ai prompt'u oluşturulur
    - `quote`: `quote_text` + `quote_author` (opsiyonel) alanları → `_build_quote_prompt()` ile prompt oluşturulur; `caption` response'da döner
    - `image`/`carousel`: RAG destekli `_build_prompt_with_rag()` (doküman context'i)
  - `POST /posts/{post_id}/regenerate` → yeniden üretim (JWT veya X-Internal-Key)
  - `POST /posts/{post_id}/publish` → yayınla (JWT)
  - `POST /posts/{post_id}/publish-now` → yayınla (X-Internal-Key, n8n için)
  - `POST /posts/{post_id}/request-approval` → Telegram onay akışı (JWT)
    - Autoposting config'den `telegram_chat_id` alır
    - Post status → 'reviewing'
    - n8n `/webhook/telegram-content-approval` tetikler (fire-and-forget)
    - Sadece ready/failed/rejected durumlar geçerli; config yoksa 400
  - `GET /posts` → sayfalama + filtre
  - **`PostGenerate` şeması** (`models/schemas.py`):
    - Temel: `brand_id`, `content_type`, `content_category`, `prompt`, `user_text`, `document_ids`, `aspect_ratio`, `platforms`
    - Özel Gün: `special_day_name: str | None`, `special_day_category: str | None`
    - Alıntı: `quote_text: str | None`, `quote_author: str | None`

- [x] AI endpoint'leri (`app/routers/ai.py`)
  - `POST /ai/suggest-ideas` → Claude Haiku ile **3 adet** içerik fikir önerisi
    - `SuggestIdeasRequest`: `brand_id`, `content_type`, `content_category`, `prompt`, `document_ids`, `platforms`, `count=3`
    - Prompt içeriği: marka adı/sektör + içerik tipi + kategori + platform + tonalite + hashtagler + kullanıcı prompt'u + RAG doküman bağlamı
    - İçerik tipine özel talimat: video → senaryo fikirleri, görsel → tasarım fikirleri vb.
    - API key yoksa fallback öneriler döner
  - `POST /ai/analyze-website` → Claude Haiku ile marka bilgisi çıkar

- [x] Takvim endpoint'leri (`app/routers/calendar.py`)
  - `GET /calendar/posts?brand_id&start&end`
  - `PATCH /calendar/schedule/{post_id}`
  - `GET /calendar/holidays?year`

- [x] Otomatik yayın endpoint'leri (`app/routers/autoposting.py`)
  - `GET /autoposting/config?brand_id`
  - `POST /autoposting/config` → telegram_bot_token + telegram_chat_id dahil
  - `POST /autoposting/toggle?brand_id`
  - `GET /autoposting/upcoming?brand_id`

- [x] Internal endpoint'leri (`app/routers/internal.py`) — X-Internal-Key korumalı, n8n için
  - `GET  /internal/autoposting/due` — timezone-aware, duplicate guard
  - `POST /internal/autoposting/trigger` — post üret + fal.ai tetikle
  - `GET  /internal/posts/{id}` — post detayı (JWT'siz)
  - `PATCH /internal/posts/{id}/status` — durum güncelle (rejected vb.)

- [x] OAuth Callback (`app/routers/social.py`)
  - `GET /social/oauth-link?brand_id&platform` → JWT link üret
  - `GET /social/callback?state&access_token&account_name`
    - State JWT doğrular, brand_social_accounts'a upsert yapar
    - Başarıda → `app.otomaix.com/marka-ayarlari?tab=sosyal&connected={platform}`

- [x] Servis kimlik doğrulaması (`app/core/security.py`)
  - `get_service_auth` dependency → X-Internal-Key header kontrolü
  - INTERNAL_API_KEY config'de tanımlı
  - **KRITIK:** JWT doğrulama `python-jose` yerine `PyJWT[crypto]==2.8.0` kullanıyor
    - Supabase ES256 (ECDSA) imzalı token'lar için `ECAlgorithm.from_jwk()` ile JWK→key dönüşümü
    - python-jose 3.3.0 EC JWK key formatını desteklemiyordu → "alg not allowed" hatası veriyordu
    - JWKS önbelleği 1 saatlik TTL ile (`_jwks_fetched_at` + `_JWKS_TTL`)

- [x] n8n Auto Posting Scheduler (ID: `Nz4651wCfBHP4G9l`)
  - Her 30dk schedule trigger
  - GET /internal/autoposting/due → zamanı gelen configler
  - Her config için rastgele topic/type/category seçer
  - POST /internal/autoposting/trigger → post üretir
  - Telegram onayı gerekiyorsa → 3dk bekler → Telegram Onay webhook'unu tetikler

- [x] n8n Telegram İçerik Onay (ID: `D49KNE35cONz2APb`)
  - Webhook trigger: `POST /webhook/telegram-content-approval`
  - 2dk bekler (fal.ai üretimi) → post detayını alır
  - Müşterinin kendi bot token'ı ile Telegram'a mesaj gönderir (HTTP Request, statik credential yok)
  - Inline keyboard: ✅ Onayla / ❌ Reddet / 🔄 Yeniden Üret
  - 24sa callback bekler → karara göre publish/reject/regenerate

## Migrations
- `001_initial_social.sql` — temel şema ✅
- `002_autoposting.sql` — autoposting_configs + public_holidays ✅
- `003_social_account_unique.sql` — brand_social_accounts UNIQUE(brand_id, platform) ✅
- `004_telegram_chat_id.sql` — autoposting_configs.telegram_chat_id ✅
- `005_telegram_bot_token.sql` — autoposting_configs.telegram_bot_token ✅
- `006_document_rag.sql` — brand_documents.raw_text + brand_document_chunks (pgvector) ✅
- `007_competitor_analysis.sql` — competitor_analyses tablosu ✅

## Router Kayıt Sırası (main.py)
```python
app.include_router(auth.router)
app.include_router(ai.router)
app.include_router(internal.router)
app.include_router(autoposting.router)
app.include_router(avatar.router)      # Phase 3 — eklendi
app.include_router(brands.router)
app.include_router(calendar.router)
app.include_router(competitors.router) # Phase 3 — eklendi
app.include_router(documents.router)   # Phase 3 — eklendi
app.include_router(posts.router)
app.include_router(storage.router)
app.include_router(social.router)
app.include_router(webhooks.router)
```

## n8n Workflow'ları
- **Auto Posting Scheduler** — ID: `Nz4651wCfBHP4G9l` | `shared/n8n-workflows/auto-posting-scheduler.json`
- **Telegram İçerik Onay** — ID: `D49KNE35cONz2APb` | webhook: `POST /webhook/telegram-content-approval`
- **Telegram Onayla** — ID: `aQ8neGzs3PQp8DMl` | webhook: `GET /webhook/tg-approve?post_id=&bot_token=&chat_id=`
- **Telegram Reddet** — ID: `9kp6bCFl0ys6TbVu` | webhook: `GET /webhook/tg-reject?post_id=&bot_token=&chat_id=`
- **Türkiye Takvimi Güncelleme** — ID: `tTk1VroTh4AS8lxI` | `shared/n8n-workflows/turkey-calendar-update.json`
  - Her yıl 1 Ocak 00:00'da çalışır (cron: `0 0 1 1 *`)
  - Kaynaklar: date.nager.at (milli tatiller) + api.aladhan.com (dini bayramlar — API key gereksiz)
  - Kapsar: 7 milli tatil + 18 Mart Çanakkale + Ramazan/Kurban (arife dahil) + Sevgililer/Anneler/Babalar/Black Friday
  - social.public_holidays tablosuna upsert yapar
  - ⚠️ n8n'de **inactive** — aktif etmek için n8n UI'dan "Activate" yap
  - ⚠️ İlk çalıştırma için n8n UI'dan "Test workflow" ile 2026 verilerini yükle
- Her ikisi de n8n'de mevcut ama **inactive** — aktif etmek için aşağıya bak.

## requirements.txt (önemli eklemeler)
```
anthropic==0.40.0
python-multipart==0.0.12
pypdf==4.3.1           # Phase 3 — PDF metin çıkarma
python-docx==1.1.2     # Phase 3 — Word metin çıkarma
openpyxl==3.1.5        # Phase 3 — Excel metin çıkarma
openai==1.57.0         # Phase 3 — RAG chunk embedding (opsiyonel, OPENAI_API_KEY gerekli)
PyJWT[crypto]==2.8.0   # ES256 JWK desteği — python-jose yerine kullanılıyor
```

## Phase 3

### Tamamlanan
- [x] Adım 1a — Doküman RAG Backend
  - `app/services/document_processor.py` → PDF/Word/Excel metin çıkarma + chunking
  - `app/routers/documents.py` → POST /documents, GET /documents, DELETE /documents/{id}
  - `shared/db/migrations/006_document_rag.sql` → brand_document_chunks + raw_text kolonu
  - config.py: OPENAI_API_KEY opsiyonel eklendi (varsa vektör embedding aktif olur)

- [x] Adım 1b — RAG entegrasyonu (posts.py)
  - `_build_prompt_with_rag()` helper → doküman bağlamını prompt'a enjekte eder
  - `get_document_context()` → küçük dokümanlar raw_text, büyükler chunk retrieval
  - document_ids artık posts tablosuna kaydediliyor

- [x] Adım 2a — Türkçe Faceless Video backend pipeline
  - `app/services/faceless_video.py`
    - `generate_script()` → Claude Haiku ile Türkçe script (30-60 sn, ~75-150 kelime)
    - `text_to_speech()` → Azure TTS REST API → R2'ye mp3 (AZURE_TTS_KEY yoksa atlanır)
    - `generate_background_video()` → fal-ai/hunyuan-video (async, webhook)
    - `run_faceless_video_pipeline()` → tam pipeline, post kaydı oluşturur
  - `POST /posts/generate-faceless-video` → brand_id, prompt, voice, aspect_ratio
  - `GET /posts/voices/turkish` → sabit Türkçe ses listesi
  - `POST /ai/generate-script` → sadece script üretimi (frontend'den çağrılır)
  - `config.py`: AZURE_TTS_KEY + AZURE_TTS_REGION eklendi

- [x] Adım 3a — AI Avatar backend (HeyGen entegrasyonu)
  - `app/services/avatar.py`
    - `list_stock_avatars()` → HeyGen avatarları (API yoksa fallback liste)
    - `create_avatar_from_photo()` → fotoğraf → R2 → HeyGen photo_avatar
    - `set_stock_avatar()` → brand_kit.avatar JSONB güncelle
    - `generate_ugc_video()` → HeyGen v2/video/generate (async)
    - `get_video_status()` → video üretim durumu sorgula
  - `app/routers/avatar.py`
    - `GET  /avatar/stock` → stok avatarlar
    - `POST /avatar/create` → fotoğraftan avatar (multipart)
    - `POST /avatar/select-stock` → stok avatar seç
    - `POST /avatar/generate-ugc` → UGC video üret + post kaydı oluştur
    - `GET  /avatar/video-status/{video_id}` → HeyGen durum sorgulama
  - `config.py`: HEYGEN_API_KEY eklendi (opsiyonel)

- [x] Adım 4a — Rakip analizi backend
  - `app/services/competitor_analyzer.py`
    - `analyze_website(url)` → httpx + Claude Haiku ile rakip site analizi
    - `analyze_instagram(handle)` → APIFY_API_KEY varsa gerçek, yoksa placeholder
    - `generate_competitor_report()` → Claude ile fırsat + öneri sentezi
    - `run_full_analysis()` → website + instagram birleşik pipeline
  - `app/routers/competitors.py`
    - `POST /competitors` → rakip ekle + hemen analiz et
    - `GET  /competitors?brand_id` → liste
    - `GET  /competitors/{id}/analysis` → detaylı analiz
    - `POST /competitors/{id}/refresh` → analizi yenile
    - `DELETE /competitors/{id}` → rakip sil
    - `GET  /competitors/report/summary?brand_id` → Claude sentez raporu
  - Migration: `007_competitor_analysis.sql` ✅
  - config.py: APIFY_API_KEY eklendi (opsiyonel)
  - n8n: `shared/n8n-workflows/weekly-competitor-report.json` oluşturuldu

- [x] Adım 5a — Trend Analizi Backend
  - `app/services/trend_analyzer.py`
    - Google Trends (pytrends, opsiyonel) → TR trendleri
    - Türk haber RSS feed'leri (Hürriyet, Milliyet, Sabah)
    - Claude Haiku ile sektör relevance sıralaması
    - 6 saatlik önbellekleme (`social.trend_cache`)
  - `app/routers/trends.py`
    - `GET  /trends?brand_id` → mevcut/önbellekli trendler
    - `POST /trends/refresh?brand_id` → önbelleği atlayarak taze veri
    - `POST /trends/{index}/create-post` → trend prompt'u ile fal.ai tetikle
  - Migration: `008_trend_cache.sql` ✅
  - requirements.txt: `pytrends==4.9.2` eklendi

- [x] Adım 6a — Logo Overlay + Intro Video Backend
  - `app/services/media_processor.py`
    - `add_logo_overlay()` → Pillow ile logo bindirme (konum + opaklık)
    - `add_intro_video()` → FFmpeg ile video birleştirme (start/end/both)
    - `apply_brand_processing()` → fal.ai callback'ten çağrılan ana pipeline
  - `app/routers/webhooks.py` güncellendi → üretim sonrası marka işleme
  - `Dockerfile` güncellendi → ffmpeg apt paketi eklendi
  - `requirements.txt`: `Pillow==11.2.1` eklendi

- [x] Adım 7a — Paddle Ödeme Backend
  - `app/routers/billing.py`
    - `GET  /billing/plans` → tüm planlar (auth gerekmez)
    - `GET  /billing/current` → abonelik + kullanım istatistikleri
    - `POST /billing/checkout` → Paddle checkout URL
    - `POST /billing/portal` → Paddle müşteri portal URL
    - `POST /webhooks/paddle` → subscription.created/updated/cancelled
    - `check_plan_limit()` → post/brand/video/avatar limit kontrolü (HTTP 402)
  - `config.py`: PADDLE_API_KEY + PADDLE_WEBHOOK_SECRET + APP_URL eklendi
  - Migration: `009_subscriptions.sql` ✅

- [x] Adım 8a — Auth Init Endpoint
  - `GET /auth/init` → tek çağrıda user + workspace + brands döndürür
    - Account yoksa oluşturur (ON CONFLICT)
    - Workspace yoksa oluşturur + workspace_members'a ekler
    - Aktif markalar listesi döner

## Phase 4

### Tamamlanan
- [x] Adım 1a — Self-Serve Onboarding Backend
  - `GET /auth/init` güncellendi → `trial_ends_at` alanı da döndürüyor
    - `account["trial_ends_at"].isoformat()` ile ISO string olarak frontend'e gönderilir
  - Migration: `010_trial_period.sql` ✅ (çalıştırıldı)
    - `social.accounts.trial_ends_at TIMESTAMPTZ` eklendi (default: `now() + 14 days`)

- [x] Adım 2a — PostHog Analytics Backend
  - `posthog==3.7.0` requirements.txt'e eklendi
  - `app/services/analytics.py` — server-side servis (no-op key yoksa, sessiz hata yakalama)
    - `capture(distinct_id, event, properties)` — genel event
    - `content_generation_failed`, `fal_api_latency`, `publishing_failed`
    - `document_processed`, `competitor_analysis_completed`
    - `subscription_created`, `subscription_cancelled`
  - `billing.py` → Paddle webhook'a `subscription_created/cancelled` çağrıları eklendi
  - `config.py`: `POSTHOG_API_KEY` + `POSTHOG_HOST` eklendi

- [x] Adım 3a — Sentry Error Monitoring (backend)
  - `sentry-sdk[fastapi]==2.19.2` requirements.txt'e eklendi
  - `app/main.py`: `sentry_sdk.init()` + `FastApiIntegration` + `StarletteIntegration` (SENTRY_DSN varsa aktif)
  - `config.py`: `SENTRY_DSN` + `ENVIRONMENT` eklendi
  - `routers/webhooks.py`: fal.ai pipeline hatalarında `capture_exception` + post `failed` durumuna alınır
  - `services/upload_post.py`: Upload-Post.com HTTP hata kodlarında `capture_message`
  - `routers/billing.py`: Paddle checkout/portal `httpx.RequestError` + webhook JSON parse hatalarında `capture_exception`

- [x] Adım 4a — Redis Cache ve Rate Limiting (backend)
  - `redis[hiredis]==5.0.8` requirements.txt'e güncellendi
  - `app/core/cache.py` → `get_cached / set_cached / invalidate / invalidate_pattern` yardımcıları
  - `app/core/rate_limit.py` → `limiter(max_req, window_sec)` dependency factory (fail-open)
  - `app/core/security.py` → JWT decode 300s Redis cache (`otomaix:social:user:{token_hash}`)
  - Rate limit uygulamaları:
    - `POST /posts/generate` → 20/saat
    - `POST /posts/generate-faceless-video` → 20/saat
    - `POST /ai/suggest-ideas` → 30/saat
    - `POST /competitors` → 10/saat
  - Cache uygulamaları (invalidation dahil):
    - `GET /brands` → 300s (`otomaix:social:brands:{workspace_id}`)
    - `GET /calendar/holidays` → 86400s (`otomaix:social:holidays:{year}`)
    - `GET /avatar/stock` → 3600s (`otomaix:social:avatar:stock`)

- [x] Adım 5 — Docker Compose local deployment paketi
  - `shared/local-deployment/docker-compose.yml` → frontend + backend + postgres(pgvector) + redis + n8n
  - `shared/local-deployment/.env.example` → tüm değişkenler açıklamalı
  - `shared/local-deployment/setup.sh` → Docker kontrol + .env hazırlama + migration + servis başlatma
  - `shared/local-deployment/migrations/` → 010 migration SQL + run-migrations.sh
  - `shared/local-deployment/README-local.md` → Türkçe kurulum + sorun giderme kılavuzu

- [x] Adım 6 — Crisp Chat Entegrasyonu (frontend — backend değişiklik yok)

- [x] Adım 7 — Performance Optimizasyonu
  - DB pool min_size=5 / max_size=20 (`database.py`)
  - /health endpoint DB + Redis kontrol (`main.py`)
  - 011_performance_indexes.sql — posts/trend_cache CONCURRENTLY index'ler

- [x] Adım 8 — Load Testing
  - `shared/load-tests/locustfile.py` — 6 senaryo, ağırlıklı görevler
  - `shared/load-tests/run-load-test.sh` — interactive/headless/local mod
  - Smoke test: /health 5ms, /billing/plans 5ms, 0 hata

### Phase 4 Tamamlandı ✅

## Mevcut Durum
- Social Backend: **Tüm fazlar tamamlandı** (Phase 1–4)
- CRM entegrasyonu tamamlandı ✅
- Coolify'da `N8N_BASE_URL=https://n8n.otomaix.com` eklendi → redeploy edildi ✅

## CRM Entegrasyonu (billing.py güncellemeleri)
- [x] `_notify_crm_n8n(path, payload)` — fire-and-forget n8n CRM webhook yardımcısı
- [x] `PLAN_ORDER` dict — plan yükseltme tespiti (starter=0, pro=1, business=2, agency=3)
- [x] `subscription.created` → `crm/new-customer` bildirimi
- [x] `subscription.updated` (yükseltme) → `crm/plan-upgrade` bildirimi
- [x] `subscription.payment_failed` + `transaction.payment_failed` → DB past_due + `crm/payment-failed`
- [x] `N8N_BASE_URL` config.py'e eklendi (default: https://n8n.otomaix.com)
