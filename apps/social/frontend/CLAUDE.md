# Social Frontend — CLAUDE.md

> **🚧 Phase 12 — Carousel İçerik Üretimi (başladı: 2026-04-27).**
> `/icerik-olustur` carousel (çoklu slide) içerik üretimi. Slide bazlı image_prompts dizisi, multi-image fal.ai pipeline, carousel UI.
> Detaylı plan: `~/otomaix/docs/12-social-carousel.md`
> **İlerleme:** Sprint 1 ✅ (backend) · Sprint 2 ✅ (backend) · Sprint 3 ✅ (frontend) · Sprint 3 bugfix ✅ · Sprint 3 carousel slider ✅ · Sprint 3 carousel sizing ✅

> **✅ Phase 9 — Ürün/Hizmet Kütüphanesi + Image-Edit Pipeline (tamamlandı: 2026-04-22).**

> **✅ Phase 7 — Sektör-Spesifik Şablon Sistemi TAMAMLANDI (2026-04-19).**

## 2026-04-28 — Aspect ratio etiketleri + Pinterest platform eklenmesi ✅

**Değişen dosyalar (4):**

| Dosya | Değişiklik |
|-------|-----------|
| `app/(dashboard)/icerik-olustur/page.tsx` | `ASPECT_RATIOS` desc alanları format-bazlı etiketlere güncellendi + `PLATFORMS`'a Pinterest eklendi |
| `app/(dashboard)/icerik-kutuphanesi/page.tsx` | `PLATFORM_OPTIONS` filtre listesine Pinterest eklendi |
| `app/(dashboard)/otomatik-yayin/page.tsx` | `PLATFORMS` listesine Pinterest eklendi |
| `app/(dashboard)/dashboard/page.tsx` | `PLATFORMS` listesine Pinterest eklendi (SVG ikon + `text-red-600` / `bg-red-50`) |

**Aspect ratio etiket değişikliği (`icerik-olustur`):**
- 1:1 → "Kare (Instagram/Facebook/LinkedIn)" (eski: "Instagram")
- 9:16 → "Dikey (Reels/Stories/TikTok)" (eski: "Reels / TikTok")
- 4:5 → "Portre (Instagram/Facebook Feed)" (eski: "Instagram Dikey")
- 2:3 → "Uzun Dikey (Pinterest)" (eski: "Pinterest")
- 16:9 → "Yatay (YouTube/LinkedIn)" (eski: "YouTube")

**Pinterest platform desteği:**
- 4 sayfadaki platform seçim listelerine Pinterest eklendi
- Backend `PLATFORM_DEFAULTS` zaten Pinterest destekliyordu (`captionStyle: "medium", maxHashtags: 10, useFirstComment: false`)
- `ContentCard.tsx` `PLATFORM_ICONS` zaten `pinterest: 'PT'` içeriyordu
- `CaptionEditor.tsx` ve `CaptionPreview.tsx` zaten Pinterest label ve inline hashtag desteği içeriyordu
- **Kısıt:** `upload_post.py`'de Pinterest yayınlama desteği yok — içerik üretilebilir ama otomatik yayınlanamaz

**Etki analizi:**
- Risk: sıfır — additive değişiklikler, mevcut akışlar etkilenmedi
- TypeScript compile temiz

## 2026-04-28 — Phase 12 Sprint 3: Carousel önizleme boyutu büyütme ✅

**Sorun (canlı test):** Detay modal'da carousel önizleme görseli tekli image post'lara kıyasla çok küçük görünüyordu. `aspect-square` constraint + küçük thumbnail'ler sorunun kaynağıydı.

**Değişen dosya:** `app/(dashboard)/icerik-kutuphanesi/page.tsx` (PostDetailModal carousel slider bölümü)

**Değişiklikler:**
- Büyük önizleme: `width={400} height={400}` → `width={500} height={500}`, `aspect-square` sınıfı kaldırıldı, `object-contain` korundu (tekli image ile aynı davranış)
- Loader placeholder: `aspect-square` → `aspect-[4/5]` (daha uzun oran, carousel'e uygun)
- Nav okları: `p-1` → `p-1.5`, ikon boyutu `w-4 h-4` → `w-5 h-5`
- Thumbnail'ler: `w-12 h-12` → `w-14 h-14`, gap `gap-1 p-1.5` → `gap-1.5 p-2`, border radius `rounded` → `rounded-md`, Image boyutları `width={48} height={48}` → `width={56} height={56}`

**Etki analizi:**
- Risk: sıfır — sadece boyut/spacing CSS değişiklikleri
- Tekli image/video önizleme etkilenmedi (ayrı branch)
- TypeScript compile temiz (`tsc --noEmit` exit 0)

## 2026-04-28 — Phase 12 Sprint 3: Carousel slider preview (detay modal) ✅

**Sorun (canlı test):** Detay modal'da carousel görselleri sadece küçük 2×2 grid olarak görünüyordu, kaydırarak büyük önizleme yapılamıyordu. Kullanıcı hangi slide'ın nasıl göründüğünü net göremiyordu.

**Değişen dosya:** `app/(dashboard)/icerik-kutuphanesi/page.tsx` (PostDetailModal)

**Değişiklikler:**
- Yeni state: `activeSlideIndex` — seçili slide indeksi, modal açıldığında 0'a reset
- 2×2 grid kaldırıldı, yerine tam carousel slider eklendi:
  - **Büyük önizleme**: aktif slide'ın görseli (veya generating spinner'ı)
  - **Sol/sağ ok navigasyonu**: `ChevronLeft`/`ChevronRight` ikonları, ilk/son slide'da disabled
  - **Slide counter**: "2 / 5" formatında gösterge
  - **Per-slide download butonu**: aktif slide'ın `image_url`'ini yeni sekmede açar
  - **Thumbnail strip**: tüm slide'lar yatay sırada, aktif slide `ring-2 ring-blue-500` ile vurgulu, tıklanınca `activeSlideIndex` güncellenir
- IIFE pattern: JSX içinde `(() => { ... })()` ile `sorted` slides ve `current` slide hesaplanır
- Import eklendi: `ChevronLeft`, `ChevronRight`, `Download` (lucide-react)
- ESLint fix: `CarouselSlide` type import kaldırıldı (IIFE içinde TypeScript infer ediyor, Coolify build'de `no-unused-vars` hatası veriyordu)

**Etki analizi:**
- Risk: düşük — carousel branch yalnızca `content_type === 'carousel' && slides.length > 0` koşulunda devreye giriyor
- Tekli image/video önizleme aynen korundu (else branch)
- TypeScript compile temiz (`tsc --noEmit` exit 0)

## 2026-04-28 — Phase 12 Sprint 3 bugfix: Carousel görsel bug'ları (3 bug) ✅

**Sorunlar (canlı test):**
1. Tüm carousel slide'ları aynı görseli gösteriyor (R2 path collision)
2. İçerik Kütüphanesi carousel'i tek görsel olarak gösteriyor (carousel-aware UI eksik)
3. İndirme butonu önizlemeden farklı görsel gösteriyor (Bug 1'in sonucu)

**Değişen dosyalar (3):**

| Dosya | Değişiklik |
|-------|-----------|
| `components/content/ContentCard.tsx` | `CarouselSlide` interface + `Post.slides` alanı + `Layers` ikon import + carousel badge (slide sayısı) |
| `app/(dashboard)/icerik-kutuphanesi/page.tsx` | `CarouselSlide` import + PostDetailModal'da carousel slide grid (2 sütun, sıralı, numara badge + spinner/görsel) |
| Backend: `media_processor.py` + `webhooks.py` | `slide_order` parametresi eklendi — R2 path collision fix (detay: backend/CLAUDE.md) |

**Bug 1 — R2 path collision (backend):**
- `add_logo_overlay` ve `add_text_overlay` sabit R2 path kullanıyordu → slide'lar birbirini eziyordu
- Fix: `slide_order: int | None = None` parametresi → `{post_id}_slide_{N}_logo.jpg` / `{post_id}_slide_{N}_text.jpg`
- `_handle_carousel_slide` → `apply_brand_processing(slide_order=slide_order)` geçildi
- Tekli image post'lar `slide_order=None` default ile eski path'i korur (backward compat)

**Bug 2 — Carousel-aware kütüphane UI (frontend):**
- `ContentCard.tsx`: `CarouselSlide` interface eklendi, `Post` tipine `slides?: CarouselSlide[]` eklendi
- `ContentCard.tsx`: Carousel badge — sağ üst köşede `Layers` ikon + slide sayısı (siyah yarı-saydam arka plan)
- `icerik-kutuphanesi/page.tsx`: PostDetailModal önizleme alanı carousel-aware:
  - `content_type === 'carousel' && slides.length > 0` → 2 sütunlu grid, her slide sıralı
  - Her slide: numara badge (sol üst, siyah daire) + görsel veya spinner (bekleyen)
  - Tekli image/video önizleme aynen korundu (else branch)

**Bug 3 — İndirme farklı görsel (Bug 1'in sonucu):**
- Kök neden Bug 1 ile aynı: R2 path collision nedeniyle `output_url` (ilk slide) yanlış görseli gösteriyordu
- Bug 1 fix sonrası her slide benzersiz R2 URL'ine sahip → `output_url` doğru slide 1 görseline işaret ediyor

**Etki analizi:**
- Risk: düşük — carousel branch yalnızca `content_type === 'carousel'` koşulunda devreye giriyor
- Tekli görsel, video, özel gün, alıntı akışları değişmedi
- TypeScript compile temiz (`tsc --noEmit` exit 0)
- Migration gerekmez

## 2026-04-28 — Phase 12 Sprint 3: Carousel UI (frontend) ✅

**Değişen dosyalar (2):**

| Dosya | Değişiklik |
|-------|-----------|
| `components/templates/CaptionEditor.tsx` | `CaptionData` interface'ine `image_prompts?: string[]` eklendi |
| `app/(dashboard)/icerik-olustur/page.tsx` | Carousel UI akışı (aşağıda detay) |

**Step 1 — İçerik tipi + alt tip seçici:**
- `contentType === 'carousel'` seçildiğinde image ile aynı `imageSubType` seçici gösterilir: "Genel Görsel İçerik" / "Ürün/Hizmet İçeriği"
- "Devam Et" → `carousel-genel-sablon` auto-load (`DEFAULT_CAROUSEL_TEMPLATE_ID` sabiti, image pattern'i ile aynı)

**Step 2 — Form + caption:**
- `carousel-genel-sablon` template'inin `slide_count` select field'ı (2-10) `DynamicForm` tarafından otomatik render — ek form kodu yok
- Ürün/Hizmet seçici carousel modunda da çalışır (mevcut `imageSubType === 'product'` guard'ı `['image', 'carousel']` bloğu içinde)
- `handleGenerateCaption` response'undan `image_prompts` dizisi `captionData`'ya alınır
- "Slide Görsellerini Üret" butonu: carousel'de `image_prompts` dizi kontrolü, image'da mevcut `image_prompt.trim()` kontrolü
- `handleGenerate` payload: carousel ise `image_prompts` dizisi gönderilir, `image_prompt` null olur

**Step 3 — Slide grid preview:**
- `CarouselSlide` interface: `{order, image_url, image_prompt, fal_job_id}`
- `GeneratedPost`'a `slides?: CarouselSlide[]` + `slide_count?: number` eklendi
- Carousel post'larda 3 sütunlu slide grid: her slide numara badge + spinner (bekleyen) / görsel (hazır)
- Progress bar: "X/Y hazır" rozeti + yüzde çubuğu (tüm slide'lar tamamlanınca yeşil)
- Polling: her 3s'de `slides` JSONB okunur, slide bazlı progress güncellenir
- Generating mesajı: "Carousel slide görselleri üretiliyor..." + "X slide paralel üretiliyor, bu biraz sürebilir"

**Etki analizi:**
- Risk: düşük — carousel branch yalnızca `contentType === 'carousel'` koşulunda devreye giriyor
- Tekli görsel (image) akışı birebir korundu, video/özel gün/alıntı akışları değişmedi
- TypeScript compile temiz (`tsc --noEmit` exit 0)
- Migration gerekmez

## 2026-04-27 — Trendler Sektör sekmesi UI yeniden yazımı ✅

**Dosya:** `app/(dashboard)/trendler/page.tsx`

**Sorun:** Sektör Trendleri sekmesi basit bir "Yenile" butonuyla sayfa yüklendiğinde otomatik API çağrısı yapıyordu. Uygulama geliştirme aşamasında olduğu için her yüklemede gereksiz API kredisi harcanıyordu. Ayrıca Marka Trendleri sekmesindeki pattern'den (kart + "Son arama" tarihi + loading state) farklıydı.

**Değişiklikler:**
- n8n nightly sweep cron (`jnjxwCmu7OMVRvwn`) deaktive edildi (günlük API israfı durduruldu)
- Backend `GET /trends` response'una `fetched_at` alanı eklendi (zaten DB'den okunuyordu ama response'a dahil edilmiyordu)
- Sektör sekmesi Marka Trendleri pattern'ine göre yeniden yazıldı:
  - Mavi gradient kart (`border-blue-100 bg-gradient-to-br from-blue-50 to-white`) + TrendingUp ikonu + sektör açıklaması
  - Buton: `trends.length > 0 ? 'Yeniden Ara' : 'Sektör Trendlerini Ara'`
  - "Son arama: {formatDateTR(sectorFetchedAt)}" tarihi gösterimi
  - Refresh sırasında: spinner + "Trendler analiz ediliyor, lütfen bekleyin..." loading mesajı
  - Boş state: "Henüz trend araması yapılmadı" mesajı
- Tab açıklaması güncellendi: "6 saatte bir güncellenir · ücretsiz" → "Sektörünüze özel trend analizi · ücretsiz"

**Etki analizi:**
- Risk: düşük — API sözleşmesi değişmedi, sadece UI pattern değişti
- Sayfa yüklendiğinde `loadTrends()` hâlâ cache'den okur (ucuz), pahalı `handleRefresh()` yalnızca kullanıcı butonuna tıklayınca çalışır
- TypeScript compile temiz
> `/icerik-olustur` sayfasının 3 genel kategorisi → 22 sektör-spesifik şablona dönüştü. Detaylı plan: `~/otomaix/docs/07-social-template-system.md`.
> **İlerleme:** Sprint 1 ✅ · Sprint 2 ✅ · Sprint 3 ✅ · Sprint 4 ✅ · Sprint 5 ✅ · Sprint 5 polish ✅ · Sprint 6 ✅ · Sprint 7 (dynamic aspect selector) ✅ — **Phase 7 tamamlandı**

## 2026-04-22 — Phase 9 Sprint 9A+9B: /icerik-olustur Ürün/Hizmet Entegrasyonu ✅

**Kapsam:** `/icerik-olustur` wizard'ına Ürün/Hizmet İçeriği akışı eklendi. Backend (Sprint 6+7) zaten hazırdı; bu sprint saf frontend değişikliği.

**Değişen dosya:** `app/(dashboard)/icerik-olustur/page.tsx`

**Sprint 9A — Step 1 alt tip seçici:**
- `imageSubType: 'general' | 'product'` state (default: `'general'`)
- Görsel seçilince altında 2 kart: **Genel Görsel İçerik** (text-to-image) / **Ürün/Hizmet İçeriği** (image-to-image)
- contentType değişince + `resetWizard`'da `imageSubType` → `'general'` sıfırlanır
- "Devam Et" her iki yolda `genel-gorsel-sablon` yükler (değişmez)

**Sprint 9B — Step 2 ürün seçici + otomatik doldurma + API:**
- Yeni state: `availableProducts`, `selectedProduct`, `loadingProducts`
- `imageSubType === 'product'` + `currentBrand.id` değişince `GET /products?brand_id=...&active=true` çekilir
- `imageSubType` değişince `selectedProduct`, `selectedDocIds`, `captionData` sıfırlanır
- Step 2 `phase=form` + `imageSubType=product` → `<DynamicForm>` üstüne **Ürün Seç** kart listesi (görsel thumbnail, ad, tür ikonu)
- Ürün seçilince: `templateFields['ana_konu'] = product.name`, `templateFields['one_cikan_ozellik'] = product.description ?? ''` (override edilebilir pre-fill)
- Aktif ürün yoksa "Marka Ayarları → Ürün/Hizmet" linkiyle yönlendirme
- **Dokümanlardan Bağlam Ekle** bölümü `imageSubType === 'general'` iken görünür, `'product'`ta gizlenir
- `handleGenerateCaption`: `product_id: selectedProduct?.id ?? null` eklendi
- `handleGenerate` (image/carousel bloğu): `product_id: selectedProduct?.id ?? null` eklendi

**Backend davranışı (değişmedi):**
- `product_id` set + ürünün `image_url`'i var → fal.ai `nano-banana-2/edit` (image-to-image)
- `product_id` set + `image_url` yok → FLUX text-to-image fallback
- Ürün RAG dokümanları caption-gen'de otomatik merge edilir (Sprint 7)

**Etki analizi:**
- Risk: düşük — `imageSubType` default `'general'`, mevcut Genel Görsel akışı birebir aynı
- TypeScript compile temiz

**Doğrulama:**
- ✅ Sprint 9A canlı test: alt tip seçici çalışıyor
- ⏳ Sprint 9B canlı test (deploy sonrası)

## 2026-04-21 — Phase 9 Sprint 8: Marka Ayarları → Ürün/Hizmet Kütüphanesi UI ✅

**Kapsam:** `/marka-ayarlari`'na 7. sekme "Ürün/Hizmet" eklendi. Phase 9 backend CRUD endpoint'leri (`/products`, `/product-documents`) UI üzerinden expose edildi. Kart grid, create/edit dialog, per-product dokümanlar dialog, plan kota rozeti + 402 paywall akışı mevcut pattern'lerle uyumlu.

**Yeni dosyalar:**
- `lib/products.types.ts` — `Product`, `ProductDocument`, `ProductCreatePayload`, `ProductUpdatePayload`, `ProductType` tipleri (backend şemasıyla birebir)
- `lib/api/products.ts` — 9 API helper'ı: `fetchProducts`, `fetchProduct`, `createProduct`, `updateProduct`, `deleteProduct`, `uploadProductImage`, `fetchProductDocuments`, `uploadProductDocument`, `deleteProductDocument`. Hepsi `ApiResponse<T>` döndürür (402 `plan_limit` + 429 `retry_after` handling için).
- `components/products/ProductsTab.tsx` — ana tab: 2 chip grubu (tür + aktif filtresi), kota rozeti ("8/10 ürün" — `GET /billing/current` → `usage.products_per_brand[brandId]` + `limits.max_products_per_brand`), "+ Yeni Ekle" butonu, 3-kolon kart grid. Her kart: görsel (yoksa Package/Wrench ikonu), ad, açıklama (2 satır), etiketler (ilk 3), doküman sayısı butonu (Dialog açar), Düzenle, Sil.
- `components/products/ProductFormDialog.tsx` — create + edit ortak. Tür seçici (Package/Wrench iki buton, edit'te disabled), ad, açıklama, TagInput (`/[,;\n\t]+/` paste split + case-insensitive dedup), görsel yükleme (10MB / JPEG/PNG/WebP), aktif switch'i. Create başarılıysa ayrı `POST /products/{id}/image` çağrısı.
- `components/products/ProductDocumentsDialog.tsx` — per-product doküman listesi (RAG chunk/raw/işleniyor rozetleri), upload (50MB / PDF/DOCX/XLSX/TXT), sil (confirm).

**Modifiye dosya:**
- `app/(dashboard)/marka-ayarlari/page.tsx` — `ProductsTab` import'u + 7. `TabsTrigger value="urun-hizmet"` (Dokümanlar ile AI Avatar arası) + `TabsContent` bloğu (kısa açıklama + `<ProductsTab brandId={brand.id} />`).

**UX:**
- Kota dolduğunda "+ Yeni Ekle" tıklanınca UpgradeModal açılır (ağa istek atmadan), backend yine de 402 döndürürse aynı modal fallback olarak çıkar
- Tür oluşturulduktan sonra değiştirilemez (backend assertion) — edit dialog'unda tür seçici disabled
- Doküman upload optimistic (UI listesi anında güncellenir) + RAG chunk sayısı badge'le gösterilir
- Sil işlemleri `confirm()` ile guard edilir, backend cascade R2 cleanup yapar

**Tasarım kararları:**
- 3 komponent yapıldı (tab + form dialog + docs dialog) — marka-ayarları sayfası 1337 satırlık monolit olduğu için inline yerine ayrıştırıldı
- Quota rozeti her create sonrası + silme sonrası re-fetch (`loadQuota()`) — ürün listesi zaten küçük
- `fetchProducts` filter state değişince re-fetch (useCallback + useEffect), pagination yok (liste küçük)
- `ApiResponse<T>` döndürmeyi koruduk — `UpgradeModal` için `res.plan_limit` gerekli

**Etki analizi:**
- Risk: düşük — yalnızca additive (yeni sekme + yeni komponentler), mevcut tab'lar değişmedi
- TypeScript compile temiz (`tsc --noEmit` exit 0)

**Doğrulama:**
- ✅ TypeScript compile temiz
- ⏳ Canlı test (deploy sonrası):
  - Marka Ayarları → "Ürün/Hizmet" sekmesi görünmeli, boş state'te "+ Yeni Ekle" butonu ve "Henüz ürün eklenmedi" mesajı
  - Yeni ürün ekle → form doldur + görsel yükle → kart grid'e eklenmeli, kota "1/10"a çıkmalı
  - Ürüne doküman ekle → "1 doküman" sayacı güncellenmeli
  - Kota tavan (Starter plan, 10 ürün) aşıldığında UpgradeModal
  - Backend 30/hr rate limit tetiklenirse toast (`res.retry_after` saniye)

**Sonraki:** Sprint 9 — `/icerik-olustur` wizard'ında ürün/hizmet seçici (mevcut template form'a ürün picker entegrasyonu, image-edit pipeline tetikleme). Bu sprint büyük ve user'ın bilinçli kickoff'u gerekiyor — memory'de hatırlatıcı mevcut.

## 2026-04-22 — Phase 9 Sprint 8 polish: marka seçimi kalıcılığı + form iyileştirmeleri ✅

**Sorunlar (canlı test):**
1. Sayfa refresh veya farklı sayfaya gidip dönüldüğünde seçili marka sıfırlanıyor, `auth/init` her zaman `brands[0]`'ı (ilk oluşturulan marka) seçiyordu. Kullanıcı MyGoodShoes seçiliyken ürün ekleyip refresh yapınca Otomaix'e düşüyor, eklediği ürünü bulamıyordu.
2. `ProductFormDialog`'da doküman yükleme alanı yoktu — ürün oluşturduktan sonra ayrı bir dialog açmak gerekiyordu.
3. Görsel önizlemede `next/image` blob URL'yi production'da sunucudan fetch etmeye çalışıp kırık önizleme üretiyordu.
4. Aktif switch'in label'ı her zaman "Aktif" yazıyordu (pasif yapıldığında da).
5. Tab isimleri netleştirilmedi: "Dokümanlar" → "Marka Dokümanları", "Ürün/Hizmet" → "Ürün/Hizmet Dokümanları".

**Değişen dosyalar (3):**

**`lib/store.ts`:**
- `switchBrand(brand)` artık seçilen brand ID'yi `localStorage.setItem('otomaix_selected_brand_id', brand.id)` ile kaydediyor.

**`app/(dashboard)/layout.tsx`:**
- `doInit` içinde, brand listesi yüklenince `stillValid` false olduğunda önce `localStorage.getItem('otomaix_selected_brand_id')` okunuyor, brands listesinde varsa o marka seçiliyor, yoksa `brands[0]` fallback.

**`components/products/ProductFormDialog.tsx`:**
- `pendingDocs: File[]` state eklendi — birden fazla doküman kuyruğa alınabilir.
- Görsel upload alanının altına **Ürün/Hizmet Dokümanları** upload bölümü eklendi (PDF/Word/Excel, maks 50MB). Seçilen dosyalar liste halinde gösterilir, × ile kaldırılabilir. Marka dokümanları sekmesindeki aynı pattern kullanıldı.
- `handleSave` akışı: ürün oluştur → görsel yükle → dokümanları sırayla yükle (`uploadProductDocument`). Herhangi bir doküman yüklenemezse dosya adıyla ayrı toast, diğerleri devam eder.
- Aktif/Pasif label dinamik: switch'in durumuna göre "Aktif" (siyah) veya "Pasif" (gri) yazıyor.
- Blob URL önizlemesi `<Image>` → `<img>` tag'ine çevrildi (blob URL'ler Next.js image optimization'ı geçemez); kaydedilmiş R2 URL'ler hâlâ `<Image>` kullanıyor.
- `pendingDocs` form açılışında sıfırlanıyor.

**`app/(dashboard)/marka-ayarlari/page.tsx`:**
- `TabsTrigger value="dokumanlar"` → "Marka Dokümanları"
- `TabsTrigger value="urun-hizmet"` → "Ürün/Hizmet Dokümanları"

**Etki analizi:**
- Risk: düşük — localStorage key çakışması yok (`otomaix_selected_brand_id`); brand silinmişse fallback `brands[0]` devreye giriyor.
- TypeScript compile temiz (`tsc --noEmit` exit 0).

**Doğrulama:**
- ✅ Canlı test: brand switching bug giderildi, daha önce görünmeyen ürünler artık doğru brand seçilince görünüyor.
- ✅ TypeScript compile temiz.
- ⏳ Doküman upload formdan test edilmeli: yeni ürün ekle + doküman seç → ürün oluşturulunca doküman da yüklenmeli.

## 2026-04-20 — 3 kalan "caption" stringi "gönderi metni"ne çevrildi ✅

**Sorun:** 2026-04-18 Phase 7 Sprint 5 polish'inde tüm kullanıcı-yönelik "Caption" stringleri "Gönderi Metni"ne çevrilmişti, ancak canlı testte `/icerik-olustur` sayfasında hâlâ 3 yerde "caption" kelimesi görünüyordu. Kullanıcı "bu sayfadaki caption ne demek?" diye sordu — terim KOBİ kitlesi için net değil.

**Çözüm (3 dosya, 3 satır):**
- `app/(dashboard)/icerik-olustur/page.tsx:945` — "Tasarım ve içerik için istekleriniz" textarea placeholder: `"caption'da %20 indirim vurgusu olsun"` → `"gönderi metninde %20 indirim vurgusu olsun"`
- `components/templates/DynamicForm.tsx:52` — disclaimer kartı altındaki yardım metni: `"Bu metin caption sonuna otomatik olarak eklenecek."` → `"Bu metin gönderi metninin sonuna otomatik olarak eklenecek."`
- `components/templates/CaptionEditor.tsx:184` — hashtag editörü hint'i: `"... caption'ına eklenecek hashtag'ler."` → `"... gönderi metnine eklenecek hashtag'ler."`

**Değişmeden kalanlar (bilinçli):** `captionData`, `setCaption`, `handleGenerateCaption`, `CaptionEditor`, `CaptionData`, `platform_captions`, `default_caption` — internal state/type/fonksiyon isimleri, kullanıcıya görünmez. Ayrıca component dosya adları (CaptionEditor.tsx, CaptionPreview.tsx) da kod seviyesi, kullanıcı terminolojisi değil.

**Etki analizi:**
- Risk: sıfır — yalnızca text rename, state/payload/API sözleşmesi etkilenmedi
- TypeScript compile temiz

## 2026-04-20 — CaptionEditor hashtag editörü geri getirildi (inline platformlar için) ✅

**Sorun:** Önceki commit'te (badge listesi asimetriktir gerekçesiyle) CaptionEditor'dan tüm hashtag gösterimi kaldırılmıştı. Canlı testte kullanıcı fark etti: IG sekmesinde first_comment textarea olduğu için hashtag görünüyor, ama LinkedIn/Twitter/TikTok/YouTube/Pinterest/Bluesky sekmelerinde (`useFirstComment=false` — hashtag caption gövdesinde inline olmalı) hashtag HİÇ GÖRÜNMÜYORDU. Claude bu platformlar için caption'a hashtag her zaman eklemediği için kullanıcı manuel kontrol/düzenleme imkanı kaybetmişti.

**Çözüm (`components/templates/CaptionEditor.tsx`):**
- `Input`, `Button`, `Badge` import'ları geri eklendi
- `INLINE_HASHTAG_PLATFORMS = Set(['linkedin','twitter','tiktok','youtube','pinterest','bluesky'])` sabiti
- `normalizeTag(raw)` helper'ı: trim, whitespace sıkıştırma, prefix `#` idempotent normalizasyon
- `commitHashtagInput()`: `split(/[,;\n\t\s]+/)` ile çoklu parse, case-insensitive dedup
- `removeHashtag(tag)`: ✕ butonuyla silme
- `showHashtagEditor = activeTab === 'default' || INLINE_HASHTAG_PLATFORMS.has(activeTab)` — koşullu render
- IG/FB/Threads sekmelerinde editör GİZLİ (first_comment textarea zaten var, asimetri yok)

**UX:**
- Varsayılan sekmesinde: tüm platformlar için ortak hashtag listesi (her platforma kopyalanır)
- LinkedIn/Twitter/TikTok/YouTube/Pinterest/Bluesky: caption gövdesine eklenecek hashtag listesi + Input + Ekle butonu
- IG/FB/Threads: yalnızca first_comment textarea görünür — hashtag editörü yok

**Ek fix (aynı commit sonrası hotfix):** `"Hashtag'ler"` JSX text node'u `react/no-unescaped-entities` ESLint hatası verdi, production build kırıldı. `Hashtag&apos;ler` olarak escape edildi.

**Etki analizi:**
- Risk: sıfır — `captionData.hashtags` array'i zaten mevcuttu, backend hâlâ okuyor
- TypeScript + lint temiz

## 2026-04-20 — CaptionEditor hashtag badge listesi kaldırıldı (UX asimetri fix) ✅

**Sorun (canlı test):** Step 2 `CaptionEditor` Instagram sekmesinde hashtag'ler üç farklı yerde görünüyordu:
1. Düzenlenebilir caption textarea (serbest edit)
2. Düzenlenebilir "İlk Yorum (hashtag bloğu)" textarea (IG/FB/Threads'te first_comment)
3. **Düzenlenemez rozetli hashtag listesi** (sadece ✕ ile tek tek silinebiliyor, ekleme yok)

Üçüncü alan asimetrik ve kafa karıştırıcıydı — salt görünüm/silme aracı. Caption + first_comment textarea'larda aynı hashtag'ler zaten serbest düzenlenebiliyordu.

**Çözüm (tek dosya):** `components/templates/CaptionEditor.tsx`:
- `import { Badge } from '@/components/ui/badge'` kaldırıldı
- `updateHashtags(hashtags)` helper kaldırıldı
- Alt kısımdaki "Hashtag'ler" başlıklı badge list bloğu (ikon + ✕ butonu + boş state mesajı ~20 satır) tamamen silindi

**Kalan yapı:** Platform tab stripi + caption textarea + (IG/FB/Threads için) first_comment textarea. `CaptionData.hashtags: string[]` tipi korundu — backend hâlâ bu alanı alıyor, değişmedi.

**Etki analizi:**
- Risk: sıfır — state/payload değişmedi, sadece salt-görünüm UI elemanı çıktı
- Backward compat: `captionData.hashtags` alanı diğer komponentlerde (CaptionPreview, handleGenerate payload) kullanılmaya devam ediyor

**Doğrulama:**
- ✅ TypeScript compile temiz
- ⏳ Canlı test: Step 2 Instagram sekmesinde yalnızca caption + İlk Yorum textarea'ları görünmeli; hashtag rozetli satır olmamalı

## 2026-04-20 — Phase 8 Sprint 2 polish: default template UI cleanup (canlı test feedback) ✅

**Canlı test feedback (4 madde):**
1. İçerik detayları sekmesinde görünen "← Başka şablon seç" linki default template için mantıksız (tek şablon varsa geri dönülecek grid yok)
2. "Görsel" tip rozeti ile "Görsel Şablonu" template rozeti iki ayrı label, duplikasyon
3. Hashtag kaynağı belirsiz (kullanıcı sordu — bkz. "Hashtag kaynağı" açıklaması aşağıda)
4. Logo sağ alt köşede çok küçük, zar zor görünüyor (screenshot `/root/otomaix/screenshots/ai-gorsel.jpg`)

**Çözüm 1 & 2 (frontend, tek dosya):** `app/(dashboard)/icerik-olustur/page.tsx`:
- "🖼️ Görsel Şablonu" badge'i render koşuluna `&& selectedTemplate.id !== DEFAULT_IMAGE_TEMPLATE_ID` eklendi — default template'te gizli.
- "← Başka şablon seç" butonu `{selectedTemplate.id !== DEFAULT_IMAGE_TEMPLATE_ID && (...)}` conditional ile sarmalandı — default template'te gizli.

**Çözüm 4 (backend, bkz. backend/CLAUDE.md):** `media_processor.add_logo_overlay` `Image.thumbnail` → active `Image.resize` — küçük logoları %20'ye **büyütür**.

**Hashtag kaynağı açıklaması (kullanıcıya):** Hashtag'ler Claude Opus 4.7 caption generator tarafından üretiliyor. Kaynak verisi:
- `brand_kit.hashtags` — Marka Ayarları → Marka Kimliği sekmesinde tanımladığın sabit marka hashtag'leri
- Sektör bağlamı (brand.sector_slug → SECTOR_GUIDANCE)
- Konu bağlamı (şablon form field'ları + user_prompt)
Claude bu üçünü harmanlayıp Instagram için ≤15, LinkedIn için ≤5, Twitter için ≤2 hashtag öneriyor (PLATFORM_DEFAULTS). Önizlemedeki hashtag badge'leri bu kaynaktan geliyor.

**Doğrulama:**
- ✅ TypeScript compile temiz (`tsc --noEmit` exit 0)
- ⏳ Canlı test: `/icerik-olustur` → Görsel → Devam Et → "Görsel Şablonu" badge'i ve "Başka şablon seç" linki görünmemeli; üretim sonrası logo belirgin boyutta olmalı

## 2026-04-20 — Phase 8 Sprint 2: Görsel için varsayılan şablon auto-select ✅

**Sorun:** Kullanıcı "Görsel → Devam et" akışında her seferinde sektör + genel şablon grid'ine düşüyordu. 22 şablonun çoğu sektör-spesifik olduğundan çoğu brand sadece 8 genel şablon görüyor, seçim yorucu. Aynı zamanda serbest mod'a gitmek caption-first + overlay + CTA yönlendirme disiplinini kaybettiriyordu. Karar: görsel için tek bir genel amaçlı varsayılan şablon (`genel-gorsel-sablon`) otomatik açılsın, grid atlansın.

**Çözüm (tek dosya):** `app/(dashboard)/icerik-olustur/page.tsx`:

- Yeni sabit: `const DEFAULT_IMAGE_TEMPLATE_ID = 'genel-gorsel-sablon'`
- Yeni state: `loadingDefaultTemplate: boolean` — async template fetch sırasında "Devam Et" butonunu disable edip spinner gösterir.
- Import: `fetchTemplateById` from `@/lib/api/templates`
- "Devam Et" butonu image type için yeniden yazıldı — async handler:
  1. `setStep(2)` + `setMode('template')` + `setLoadingDefaultTemplate(true)`
  2. `await fetchTemplateById(DEFAULT_IMAGE_TEMPLATE_ID)`
  3. Başarılıysa `handleSelectTemplate(tpl)` (state: selectedTemplate + imageTextFields + phase='form' + aspect uygulanır)
  4. Şablon null dönerse → `setPhase('pick')` + toast "Varsayılan şablon yüklenemedi, şablon listesi gösteriliyor." (graceful fallback — TemplateGrid devreye girer)
  5. `finally` → `setLoadingDefaultTemplate(false)`
- Carousel type için eski davranış korundu: `setPhase('pick')` + `setMode('template')` → TemplateGrid render edilir.
- Video/ÖzelGün/Alıntı akışları değişmedi (bu tipler `mode`/`phase` state'i kullanmaz).
- Step 2 render'da yeni loader bloğu eklendi (`contentType === 'image' && loadingDefaultTemplate`): merkezi spinner + "Varsayılan görsel şablonu yükleniyor..." metni.
- TemplateGrid render condition'u `&& !loadingDefaultTemplate` ile gate edildi (fetch sırasında grid flicker yaşanmasın).

**UX akışı:**
- **Eski:** Görsel seç → Devam Et → (şablon grid) → Şablon seç → Form + CTA + Gönderi Metni Üret
- **Yeni:** Görsel seç → Devam Et → (kısa yükleme spinner) → doğrudan Form (ana konu + öne çıkan özellik + URL + CTA metni) + Gönderi Metni Üret

**Mevcut UI elemanları birebir korundu** (kullanıcı isterdi "altyapıyı değiştirmeden aynı altyapıda tıpkı ürün kartı gibi"):
- "Tasarım ve içerik için istekleriniz" textarea (prompt state)
- Aspect ratio seçici
- Platform chip'leri
- Logo filigran switch
- Dokümanlar picker
- Görselde vurgulanacak alanlar kartı (imageTextOverlay switch)
- "Gönderi Metni Üret" butonu

**Etki analizi:**
- Risk: düşük — sadece "Devam Et" davranışı değişti, mevcut state akışı (handleSelectTemplate → phase='form') birebir kullanılıyor.
- Backward compat: carousel hâlâ grid'e düşer; image için şablon fetch başarısız olursa (404/500) otomatik fallback TemplateGrid (toast uyarısı ile).
- Backend assertion 22 → 23 bump gerektirir (detay: backend/CLAUDE.md).

**Doğrulama:**
- ✅ TypeScript compile temiz (`tsc --noEmit` exit 0)
- ⏳ Canlı test: Görsel seç → Devam Et → spinner (kısa) → form açılmalı; carousel seçildiğinde eski grid davranışı, video/özel gün/alıntı eski akış.

## 2026-04-20 — Phase 8 Sprint 1 Part 3: Template image text overlay (frontend) ✅

**Sorun:** AI görsel üretimi Türkçe karakterleri doğru render edemiyor — FLUX'a "SporXL 79 TL" yazdırmak risk. Ama ürün kartı / alıntı gibi şablonlarda "görselin üstünde fiyat/ürün adı metni" kullanıcı beklentisi. Backend Pillow ile post-process text overlay çözümü geliştiriliyor (detay: backend/CLAUDE.md), frontend bunu kullanıcıya expose etmeli.

**Çözüm (3 dosya):**

- **`lib/templates.types.ts`** — `ImageTextOverlaySpec` interface eklendi (`fields: string[]`, `position?: "top-left"|"top-right"|"bottom-left"|"bottom-right"`). `Template.imageTextOverlay?: ImageTextOverlaySpec`.

- **`components/templates/CaptionEditor.tsx`** — Step 2'deki "Görsel Prompt (İngilizce)" textarea tamamen kaldırıldı (AI'ın dinamik ürettiği İngilizce prompt son kullanıcı için yanıltıcıydı, düzenlendiğinde yanlış sonuçlara yol açıyordu). `CaptionData.image_prompt` tipi korundu (backend hâlâ bu alanı alıyor), `updateImagePrompt` fonksiyonu ileride advanced mode için dosyada bırakıldı.

- **`components/templates/DynamicForm.tsx`** — Şablonun `imageTextOverlay` alanı tanımlıysa ve `onImageTextFieldsChange` prop'u geldiyse form altında mavi arka planlı "Görselde vurgulanacak alanlar (opsiyonel)" kartı render ediliyor. Her alan toggle-style button (checkbox-backed): `activeOverlayFields` state = `imageTextFields ?? overlaySpec.fields`. Kullanıcı tıklayınca `onImageTextFieldsChange(next)` çağrılır — parent component 3-state override pattern'i saklar (`null` = template default, `[]` = hepsi kapalı, `[...]` = açık subset).

- **`app/(dashboard)/icerik-olustur/page.tsx`**:
  - Yeni state: `imageTextFields: string[] | null` (null default = template default).
  - `handleSelectTemplate(template)` → `setImageTextFields(template.imageTextOverlay?.fields ?? null)` (şablona göre başlangıç).
  - `resetWizard()`, `handleFreeFormMode()`, `handleBackToPick()`, contentType değişim handler'ı → `setImageTextFields(null)` reset.
  - `<DynamicForm>`'a `imageTextFields={imageTextFields ?? undefined}` + `onImageTextFieldsChange={setImageTextFields}` props geçildi.
  - `handleGenerate()` image/carousel payload'a `image_text_fields: imageTextFields` eklendi.

**UX:**
- MyGoodShoes + Ürün Kartı seçilince: "product_name" + "price" alanları form'da normal input olarak doldurulur, en altta mavi kartta iki buton ✓ olarak işaretli — kullanıcı istemezse (`+` tıklayarak) kapatabilir.
- Diğer şablonlarda (şu an 21 şablon) `imageTextOverlay` tanımlı olmadığından kart hiç görünmez — backward compat.

**Etki analizi:**
- Risk: sıfır — `imageTextOverlay` tanımlı olmayan template'lerde tüm UI+payload aynen eski davranış.
- TypeScript compile temiz (`tsc --noEmit` exit 0).

**Doğrulama:**
- ✅ TypeScript compile temiz
- ⏳ Canlı test: MyGoodShoes + Ürün Kartı → form'un en altında mavi kart + 2 toggle buton (product_name, price) görünmeli; her biri kapatılabilmeli; üretim sonrası görselde sol alt köşede "SporXL" + "79 TL" basılmalı

## 2026-04-20 — `/icerik-olustur` Step 3'te platform-sekmeli metin önizlemesi ✅

**Sorun:** Step 3'te görselin altında sadece "Varsayılan" gönderi metni görünüyordu. Kullanıcı 3 platform seçmişse (IG + LinkedIn + Twitter) her platforma özel metinlerin gerçekten gidip gitmediğini göremiyor, Varsayılan'ın tüm platformlara aynen gittiğini sanıyordu. Oysa backend her platforma `platform_captions[platform].caption` ve (IG/FB/Threads için) `first_comment` alanını ayrı gönderiyor.

**Çözüm:** Yeni `components/templates/CaptionPreview.tsx` bileşeni — Step 2'deki `CaptionEditor`'un read-only ikizi. Aynı tab stripi (Varsayılan + platform sekmeleri), her sekmede o platforma yayınlanacak gerçek caption, IG/FB/Threads sekmelerinde "İlk Yorum (hashtag bloğu)" bloğu (mavi background — kullanıcı hashtag'lerin ayrı bir yorum olarak gideceğini görsün). Varsayılan sekmesinde hashtag badge listesi.

**Değişen dosyalar (2):**
- `components/templates/CaptionPreview.tsx` (yeni, ~100 satır): `CaptionData` + `platforms[]` + opsiyonel `onEdit` callback alır; tab state lokal; tüm alanlar read-only (Textarea yerine `<p>` ile display).
- `app/(dashboard)/icerik-olustur/page.tsx`: Step 3'teki `captionData ? (<read-only card>) : (<editor>)` bloğundaki read-only kart `<CaptionPreview data={captionData} platforms={platforms} onEdit={() => { setStep(2); setPhase('caption') }} />` ile değiştirildi. Video/special_day/quote akışları için (`captionData` null) eski editable kısım aynen korundu.

**UX:**
- Kullanıcı Step 3'te görselin altındaki sekmelere tıklayarak "Instagram sekmesinde ne gidecek? LinkedIn'de ne gidecek?" görebiliyor
- Instagram sekmesinde caption gövdesi + "İlk Yorum" kutucuğu ayrı ayrı — hashtag'lerin neden caption'dan ayrı olduğu net
- "← Metni düzenle" linki hala var, Step 2 CaptionEditor'a geri dönüyor

**Etki analizi:**
- Risk: sıfır — salt görünüm eklemesi, state/payload/API çağrısı değişmedi
- Backward compat: video/special_day/quote için `captionData === null` branch'i değişmedi, eski editable UI korundu

**Doğrulama:**
- ✅ TypeScript compile temiz (`tsc --noEmit` exit 0)
- ⏳ Canlı test: 3 platform seçip şablon mode'da içerik üret → Step 3'te görselin altında 4 sekme (Varsayılan + 3 platform); IG sekmesinde İlk Yorum kutusu görünmeli

## 2026-04-20 — `/icerik-olustur` "Ek Talimat" → "Tasarım ve içerik için istekleriniz" rename ✅

**Sorun:** Şablon mode'unda formun altında yer alan "Ek Talimat (opsiyonel)" alanı iki soruna yol açıyordu: (1) isim belirsizdi — kullanıcı buraya kısa not mu, brief mi, stil mi yazacağını bilemiyordu; (2) placeholder "şablonun ürettiği metne eklemek istediğiniz..." diyordu, bu yüzden kullanıcılar buranın sadece caption'a küçük ek yapıldığını sanıyordu. Oysa backend bu metni hem caption hem image_prompt için kullanıyordu, ayrıca şablon default'larıyla çatışırsa user_prompt geride kalıyordu (canlı test: "Tenis elbiseli bir kadın üzerinde spor ayakkabı göster" yazıldı, Claude prompt'a ekledi ama "focus on the sneakers" template default'u yüzünden FLUX tight crop yaptı).

**Çözüm (tek dosya):** `app/(dashboard)/icerik-olustur/page.tsx` (şablon mode formundaki alan):
- Label: "Ek Talimat (opsiyonel)" → "Tasarım ve içerik için istekleriniz (opsiyonel)"
- Placeholder güncellendi (görsel + caption hem örnekleri): `Örn: "Tenis kıyafetli bir kadın spor ayakkabıyı giyerken göster", "caption'da %20 indirim vurgusu olsun", "stüdyo yerine plaj arka planı"`
- Rows 2 → 3 (daha fazla brief girilsin)
- Altına yardım metni eklendi: "Yazdıklarınız şablon varsayılanlarını geçersiz kılar — hem görsel hem metin buradaki isteklere göre şekillenir."

Serbest mod'daki "İçerik Açıklaması & Tasarım Tercihleri" alanı zaten açıktı, dokunulmadı.

**Backend ile birlikte çalışan değişiklik:** `prompt_builder.py` sistem prompt'una "KULLANICI İSTEĞİ HER ZAMAN ÖNCELİKLİDİR" kuralı eklendi + Tier 3 dynamic content sıralaması user_prompt'u en tepeye aldı + template priority array'ine `user_prompt` zorla eklendi. Detay: backend/CLAUDE.md.

**Etki analizi:**
- Risk: sıfır — sadece UX metin değişikliği, state/payload adı (`prompt`) aynı kaldı, API sözleşmesi değişmedi
- Backward compat: yok — tamamen rename, eski "Ek Talimat" stringi kullanıcıya hiçbir yerde görünmeyecek

**Doğrulama:**
- ✅ TypeScript compile temiz (`tsc --noEmit` exit 0)
- ⏳ Canlı test: şablon formunda alan yeni ismiyle görünmeli, kullanıcı "tenis elbiseli kadın göster" yazdığında AI görselde model+elbise+ayakkabı gelmeli (crop olmamalı)

## 2026-04-20 — Phase 8 Sprint 1 Part 2: Per-post logo filigran switch (icerik-olustur) ✅

**Sorun:** Kullanıcı haklı olarak "görsel üretimlerinde logo kullan veya kullanma tercihini kullanıcıya sorduk mu?" diye sordu. `/icerik-olustur`'da logo filigranı tercihi yoktu — kullanıcı istisna yapmak için önce `/marka-ayarlari`'ne gidip marka default'unu değiştirmek zorundaydı.

**Çözüm:** `/icerik-olustur` sayfasında aspect ratio'nun altında "Logo filigranı bas" switch'i. Marka default'u `brand_kit.logo_overlay.enabled`'tan okunur, kullanıcı bu post için override edebilir. Backend `social.posts.use_logo_overlay` tri-state kolonu ile saklar (NULL = marka default'una uy, true/false = override). Detay backend/CLAUDE.md'de.

**Değişen dosya:** `app/(dashboard)/icerik-olustur/page.tsx`

- Yeni state: `useLogoOverlay: boolean | null` — null default (marka default'u yüklenmeden switch görünmez).
- `currentBrand?.id` değiştiğinde `GET /brands/{id}` çağrısıyla `brand_kit.logo_overlay.enabled` okunur → switch başlangıç değeri.
- Switch UI iki yerde (aspect ratio bloğunun hemen altında): template mode (`phase='form' + selectedTemplate`) ve free-form mode (`mode='free' + phase='form'`).
- Koşullu render: yalnızca `currentBrand.logo_light_url || logo_dark_url` varsa gösterilir (logo yoksa filigran anlamsız).
- Video/özel gün/alıntı akışlarında switch YOK — bu tipler için logo overlay pipeline'ı devreye girmez.
- `handleGenerate` payload'ına `use_logo_overlay: useLogoOverlay` eklendi (image/carousel akışları).

**Import eklendi:** `import { Switch } from '@/components/ui/switch'`.

**Etki analizi:**
- Risk: düşük — switch sadece logo'su olan markalarda görünür, payload alanı opsiyonel (backward compat).
- UX: kullanıcı artık marka ayarlarına gitmeden tek bir post için filigranı açıp kapatabilir. Marka default'u değişmez.

**Doğrulama:**
- ✅ TypeScript compile temiz (`tsc --noEmit` exit 0)
- ⏳ Canlı test (backend Part 1 + Part 2 birlikte):
  - Marka default = false → switch kapalı başlar, üretim logosuz
  - Switch açıp üret → o post'a logo basılır, marka ayarı değişmez
  - Tersi senaryo: default true, switch kapat → o post logosuz
  - Logo olmayan marka → switch hiç görünmez

## 2026-04-19 — Markalar "Düzenle" butonu yanlış markayı yüklüyordu (kritik bug fix) ✅

**Sorun (kullanıcı raporu):** `/markalar` sayfasında MyGoodShoes kartına tıklayıp aktif hale getirdikten sonra "Düzenle" butonuna basılınca sidebar'daki aktif marka otomatik Otomaix'e geri dönüyor; marka-ayarlari sayfası yanlış markayı (Otomaix'i) düzenliyor. Bu yüzden kullanıcının daha önce "iki marka için birden update etti" dediği olayın gerçek nedeni ortaya çıktı — MyGoodShoes'a yüklediğini sandığı medyalar aslında Otomaix'e gidiyordu.

**İlk fix denemesi (başarısız — commit 7ae1a43):** `switchBrand(brand)` çağrısı `<Link onClick>`'ten `<Button onClick>`'e taşındı (stopPropagation + switchBrand aynı callback'te). Teori: Zustand state update sync olduğu için Link navigasyonundan önce currentBrand doğru markaya set olur. **Çalışmadı.** Kullanıcı yine Otomaix'e dönüyordu.

**Gerçek kök neden:** `stopPropagation()` React synthetic event bubbling'ini durdurur ama `<a>` tag'inin **browser-level default navigation**'ını engellemez. Button onClick'inde `switchBrand(brand)` çağrılıyordu ama Link'in `<a>` tag'i tarayıcı seviyesinde navigation'ı tetikliyordu — sıralama belirsizdi. Bazı durumlarda Link navigation önce tamamlanıyor, sonra state güncelleniyor → ama layout `auth/init` çağrısı ve/veya component mount sırası nedeniyle currentBrand eski değere dönüyordu.

**İkinci fix (çalışan — uncommitted'dan committed):** `<Link>` wrapper tamamen kaldırıldı, yerine `useRouter().push()` kullanıldı. Tek bir onClick callback:
```tsx
onClick={(e) => {
  e.stopPropagation()
  switchBrand(brand)
  router.push('/marka-ayarlari')
}}
```
Böylece `switchBrand` sync çalışır → `currentBrand` store'da doğru markaya set olur → hemen ardından `router.push()` programatik navigation → yeni sayfa doğru `currentBrand` ile mount olur. Event ordering ambiguity yok.

**Öğrenilen ders:** `<Link>` içine `<Button>` koyup stopPropagation ile parent `<Card onClick>` çakışmasını çözmek yerine, navigation'ı **tamamen explicit** (router.push) yapmak daha güvenli. Özellikle tıklama öncesi global state update şart ise.

**Etki:** 
- Logo/intro video upload bug'ı açıklandı — kullanıcı MyGoodShoes'a yüklediğini sanıyordu, aslında Otomaix'e yüklüyordu. DB'deki iki brand'in aynı dosyaları barındırması bunun sonucu (fiziken ayrı path'ler ama aynı içerik, çünkü kullanıcı ikinci seferinde sidebar'dan direkt MyGoodShoes seçip yeniden yükledi).
- Bu bug'ın diğer sayfalarda tekrar etmediği doğrulandı: `BrandSwitcher.tsx` tek onClick kullanıyor, layout `auth/init`'te `stillValid` guard'ı ile mevcut currentBrand'ı koruyor.

**Temizlik önerisi (yapılmadı, kullanıcı karar verecek):** Kullanıcı isterse Otomaix'e yanlışlıkla yüklenen logolar/intro video kaldırılabilir; yeni eklenen DELETE endpoint'leri + UI butonları ile bu mümkün.

## 2026-04-19 — Marka Ayarları medya kaldırma butonu (logo + intro video) ✅

**Sorun:** `/marka-ayarlari` → Görseller sekmesinde logo veya intro video yüklenince **kaldırma seçeneği yoktu**. Kullanıcı sadece üzerine yeni dosya yükleyerek değiştirebiliyordu; mevcut medyayı tamamen kaldırma imkanı yoktu.

**Çözüm:** `FileUploadArea` bileşenine `onRemove` (opsiyonel) + `removing` prop'ları eklendi. Preview durumunda sağ üst köşede küçük ✕ butonu gösterilir; tıklandığında `confirm()` + `DELETE` endpoint çağrısı + optimistic state update (ilgili URL field'ı `null`).

**Değişen dosya:** `app/(dashboard)/marka-ayarlari/page.tsx`
- `FileUploadArea` bileşeni: `onRemove?: () => void` + `removing?: boolean` prop'ları. Preview varsa (önce video/image, sonra) absolute sağ üstte 7x7 rounded ✕ butonu. `e.stopPropagation()` ile upload click'ine düşmesi engellendi.
- Yeni state: `removingLogo: 'light' | 'dark' | null`, `removingVideo: boolean`
- `handleLogoRemove(variant)`: `confirm()` → `api.delete('/brands/{id}/logo?variant=...')` → başarılıysa ilgili `logo_*_url` field'ını NULL yap
- `handleVideoRemove()`: aynı pattern, `intro_video_url` NULL
- Logo Filigran switch'i zaten `disabled={!brand.logo_light_url && !brand.logo_dark_url}` — logo silinince otomatik kapanır (state senkron)
- Video Pozisyonu Select'i `{brand.intro_video_url && ...}` conditional — video silinince otomatik gizlenir

**Backward compat:** Eski `handleLogoUpload` / `handleVideoUpload` imzaları değişmedi, sadece yeni handler'lar eklendi.

**Not (kullanıcı endişesi):** "İki marka için birden update etti mi?" — DB check'te iki marka (Otomaix + MyGoodShoes) ayrı `brand_id`, ayrı R2 path'ler, ayrı `updated_at` timestamp'leri (18:39:24 vs 18:53:33). Backend doğru — iki ayrı upload. Aynı içerik yüklendiyse UI'da aynı görünür ama fiziken ayrılar.

## 2026-04-19 — Marka Ayarları UX polish + Select.Value slug fix ✅

**Kapsam:** `/marka-ayarlari` sayfasındaki 6 UX sorunu giderildi. Tek dosya değişiklik: `app/(dashboard)/marka-ayarlari/page.tsx`. Backend Migration 023 + jsonb double-encode fix'i ile birlikte canlı testte karşılaşılan problemler kapandı.

**Değişiklikler:**

1. **TagInput refactor (Marka Kimliği → Hashtagler + Serbest Etiketler):**
   - Layout ters çevrildi: Input + "Ekle" butonu artık etiket listesinin ÜSTÜNDE, etiket container'ı altta (min-h 64px + boş state mesajı)
   - `add()` → `input.split(/[,;\n\t]+/)` ile çoklu değer parse, her parça ayrı badge
   - `normalize()` helper'ı: trim, whitespace sıkıştırma, prefix (`#`) idempotent normalizasyon (`##tag` → `#tag`)
   - Case-insensitive dedup (`lower()` karşılaştırma)
   - `onPaste` handler: virgül/newline/tab içeren paste otomatik split
   - `onBlur`: input'ta açık kalmış metin varsa auto-commit
   - `onKeyDown`: Enter + virgül + noktalı virgül hepsi trigger

2. **"Sosyal Medya Hesabı" → "Instagram Kullanıcı Adı":**
   - Label değişti, placeholder `@mygoodshoes`
   - `onBlur` handler: boşluk temizleme + `@` prefix idempotent (`@@user` → `@user`)
   - Altında yardım metni: "Başına @ işareti otomatik eklenir."

3. **Dokümanlar tab açıklama cleanup:**
   - "Küçük dosyalar doğrudan, büyük dosyalar parçalanarak (RAG) AI'a aktarılır." teknik cümlesi kaldırıldı (son kullanıcı için gürültü). İlk cümle korundu.

4. **Logo Filigran hardening:**
   - Açıklama zenginleştirildi: "AI görsel üretildikten sonra, köşeye marka logonu otomatik yerleştirir (watermark). Konum ve opaklık aşağıdan ayarlanır."
   - Logo yoksa (`!brand.logo_light_url && !brand.logo_dark_url`) → Switch `disabled` + amber uyarı metni
   - Toggle `checked` prop'u logo zorunluluğunu da kontrol ediyor (logo silinirse otomatik kapanır)

5. **Select.Value slug gösterimi bug fix (3 yer):**
   - `@base-ui/react` Select primitive'i `SelectValue` children olmadan raw `value` (slug) render ediyor
   - Sector Select'indeki mevcut pattern (`{(value: string) => labels[value]}`) üç diğer Select'e de uygulandı:
     - **Ton / Üslup** (TONALITIES lookup): `professional` → `Profesyonel`, `friendly` → `Samimi`, vb.
     - **Logo Filigran Konum** (OVERLAY_POSITIONS): `top-left` → `Sol Üst`, vb.
     - **Video Pozisyonu** (inline map): `start` → `Başında`, `end` → `Sonunda`, `both` → `Her İkisi`
   - **Not:** Video Pozisyonu backend tarafında aktif kullanılıyor — `media_processor.apply_brand_processing()` → `add_intro_video(position=...)` FFmpeg merging için. Sayfadan kaldırılmadı, sadece görünüm düzeltildi.

**Etki analizi:**
- Risk: sıfır — UI refactor + görünüm düzeltmesi, API sözleşmesi veya state değişmedi
- TagInput değişiklikleri mevcut hashtag/serbest etiket verilerini etkilemez (dedup+normalize yeni paste/edit sırasında devreye girer, mevcut saklı etiketler aynı kalır)

**Sonraki:** Canlı test (tarayıcı hard refresh gerekli). Phase 8 planlaması kullanıcı yönlendirecek.

## 2026-04-19 — Phase 7 Sprint 7 Faz 2g: Dynamic aspect selector (media-models) ✅

**Kapsam:** `/icerik-olustur` aspect ratio seçici artık backend'ten gelen model registry'ye göre dinamik filtrelenir. Backend'de env var ile model değişirse (Sprint 7 Faz 1-2f adapter refactor'u, detay: backend/CLAUDE.md) frontend otomatik uyumlanır — yeni deploy gerekmez, 1 saatlik HTTP cache sonrası güncel liste gelir.

**Yeni dosya:** `lib/api/media-models.ts`
- `fetchActiveMediaModels()` → `GET /media-models/active` (public, JWT'siz, 1hr Cache-Control)
- `ActiveMediaModels` interface: 4 modalite (`image`, `video`, `image_to_video`, `faceless_background`), her biri `{key, model_id, supported_ratios}`
- `image_to_video.supported_ratios` daima `null` — çıktı oranı input image'den türer, aspect yok

**Modifiye dosya:** `app/(dashboard)/icerik-olustur/page.tsx`
- `useMemo` import'u eklendi
- `AspectRatio` tipi: literal union → `string` (curated `ASPECT_RATIOS` hâlâ label+icon kaynağı, sadece tip sınırı gevşetildi)
- Yeni state: `mediaModels: ActiveMediaModels | null`, mount'ta fetch
- Yeni memoized `availableAspectRatios`: contentType'a göre modaliteyi seçer (image/carousel → `image.supported_ratios`, video → `faceless_background.supported_ratios`), curated `ASPECT_RATIOS` listesini bu set'e göre filtreler. `mediaModels` henüz yüklenmemişse tüm curated list gösterilir (graceful fallback).
- Yeni reset effect: `contentType` değişince mevcut seçili `aspectRatio` artık desteklenmiyorsa `availableAspectRatios[0].id`'ye otomatik sıfırlanır
- 3 render bloğu (şablon form, serbest mod form, legacy video/special_day/quote) `ASPECT_RATIOS.map` → `availableAspectRatios.map`

**UX etkisi:**
- Image/carousel contentType: FLUX.2 Pro destekli 7 ratio ile curated listenin intersection'ı → 4 buton (1:1, 9:16, 4:5, 2:3)
- Video contentType: Hunyuan Video destekli 4 ratio ile intersection → 3 buton (1:1, 9:16, 4:5). 16:9 backend destekliyor ama curated listede yok (polish backlog — memory kaydı var).
- contentType geçişinde (ör. image seçili + aspect `2:3` → sonra video seç) aspect otomatik desteklenen ilk değere sıfırlanır, kullanıcı deneyim engellenmez

**Faz 3 (load test):** Locust senaryolarına `/media-models/active`, `/templates`, `/posts/generate-caption` eklendi — detay: backend/CLAUDE.md.

**Doğrulama:**
- ✅ TypeScript compile temiz (`tsc --noEmit` exit 0)
- ✅ Canlı `GET /media-models/active` → HTTP 200 + Cache-Control header (2026-04-19 curl testi)
- ⏳ Tarayıcı testi: `/icerik-olustur` video ↔ image geçişinde aspect butonları dinamik değişmeli (hard refresh — Ctrl+Shift+R)

**Sonraki:** Phase 7 kapandı. Minör polish backlog: `ASPECT_RATIOS` curated listesine `16:9` eklemek (Hunyuan video için YouTube oranı). Sonraki büyük iş kalemi text-to-video / image-to-video UI entegrasyonu (Sprint 7 backend adapter altyapısını kullanacak yeni faz).

## 2026-04-18 — Phase 7 Sprint 5 polish — "Gönderi Metni" rename + Step 3 cleanup ✅

**Sorunlar:**
1. Kullanıcı-yönelik "Caption" terimi Türkçe KOBİ kitlesi için anlaşılır değildi ("Başlık" da yanıltıcı — caption başlık değil, gönderi açıklamasıdır)
2. Step 2 (`phase='caption'`, `CaptionEditor`) platform-spesifik `platform_captions` JSONB'yi düzenliyor; Step 3 ise flat `caption` TEXT kolonunu ayrı düzenletiyordu — kullanıcı Step 3'te edit yapsa platform_captions güncellenmiyor, iki ayrı doğrulama yeri = tutarsızlık + kullanıcı kafa karışıklığı

**Çözüm 1 — "Gönderi Metni" rename:** Tüm kullanıcı-yönelik "Caption" stringleri (buton, label, toast, placeholder) `Gönderi Metni`'ne çevrildi. İnternal state/type/API field adları (caption, captionData, CaptionEditor, CaptionData, handleGenerateCaption vb.) korundu — sadece UI terminolojisi.

**Çözüm 2 — Step 3 read-only preview (captionData varsa):**
- `captionData` null değilse (image/carousel Akış C akışı): Step 3'te gönderi metni textarea + hashtag editör yerine **read-only preview kartı** + **← Metni düzenle** linki gösterilir → link `setStep(2); setPhase('caption')` ile CaptionEditor'a geri götürür
- `captionData` null ise (video/special_day/quote): eski editable caption + hashtag editör UI korunur

**Değişen dosyalar:**
- `components/templates/CaptionEditor.tsx`: tüm label/placeholder'lar "Caption" → "Gönderi Metni"
- `app/(dashboard)/icerik-olustur/page.tsx`:
  - Toast: "Önce caption üretin" → "Önce gönderi metnini üretin"
  - Toast: "Caption hazır..." → "Gönderi metni hazır..."
  - Toast: "Caption üretilemedi..." → "Gönderi metni üretilemedi..."
  - Toast: "Caption kaydedilemedi..." → "Gönderi metni kaydedilemedi..."
  - Buton: "Caption Üret" → "Gönderi Metni Üret" (hem şablon hem serbest mod form'u)
  - Link: "Caption'ı yeniden üret" → "Metni yeniden üret"
  - Step 3: caption editor conditional — `{captionData ? <ReadOnlyPreview/> : <EditableCaption/>}` (read-only'de `setStep(2); setPhase('caption')` ile geri dönüş)

**UX etkisi:** Image/carousel akışında kullanıcı metni yalnızca Step 2'de düzenliyor; Step 3 sadece görsel preview + metin özeti (read-only) + aksiyon butonları. Video/özel gün/alıntı için Step 3 editör davranışı değişmedi.

## 2026-04-18 — Phase 7 Sprint 5 polish — Akış C unified (Option B) ✅

**Sorun:** Sprint 5 sonrası canlı testte fark edildi — "Şablonsuz devam et" (serbest mod) tıklanınca kullanıcı tek-tıkta görsel üretiyordu, caption yalnızca Step 3'te görünüyordu. Bu, şablon modundaki caption-first UX ile tutarsızdı (şablon modu: form → Caption Üret → düzenle → Görsel Üret).

**Çözüm (Option B — unified caption-first):** Serbest mod da Akış C'yi kullansın — `/posts/generate-caption` endpoint'i `template_id=null` ile çağrılır, caption önce gösterilir, sonra görsel üretilir.

**Değişen dosyalar:**
- `app/(dashboard)/icerik-olustur/page.tsx`:
  - `handleFreeFormMode()` artık `phase='form'`'a geçiyor (önceden 'pick'te kalıyordu)
  - `handleGenerateCaption()` her iki modu destekliyor — şablon modunda required field kontrolü, serbest modda prompt zorunlu, her iki durumda da `/posts/generate-caption` çağrısı
  - `handleGenerate()` image/carousel dalı: `captionData` artık her iki modda zorunlu, `image_prompt` + `platform_captions` her zaman captionData'dan alınır
  - Yeni JSX bloğu: `mode === 'free' && phase === 'form'` — prompt textarea + fikir öner + aspect + platforms + docs + "Caption Üret" butonu
  - `phase === 'caption'` bloğu artık template+free ortak — "Formu düzenle"/"Açıklamayı düzenle" etiketi mode'a göre
  - Klasik akış condition'ı daraltıldı: artık sadece `!['image', 'carousel'].includes(contentType)` (video/special_day/quote) — image/carousel her zaman caption-first'e zorlanır
- `apps/social/backend/app/routers/posts.py`:
  - `generate_post()` içindeki `elif payload.template_id and payload.image_prompt:` → `elif payload.image_prompt:` olarak gevşetildi — `image_prompt` varsa (şablon olsun olmasın) legacy `_build_image_prompt()` bypass edilir

**UX etkisi:**
- Serbest mod akışı: Tip seç → Şablonsuz devam et → **prompt yaz + Caption Üret** → **düzenle** → **Görseli Üret** → Step 3
- Şablon modu akışı (değişmedi): Tip seç → Şablon seç → form doldur + Caption Üret → düzenle → Görseli Üret → Step 3
- Video/özel gün/alıntı: eski tek-tık akış korundu (caption bunlar için anlamlı değil)

**Backward compat:**
- Autoposting n8n workflow (`/internal/autoposting/trigger`) `image_prompt` göndermez → legacy `_build_image_prompt()` devrede kalır
- Trends → "İçerik Üret" query param prefill (`prompt`, `type`, `aspect`) — serbest mod+`phase='form'`'a düşer, kullanıcı prompt'u görür + "Caption Üret" ile ilerler

**Test planı (deploy sonrası):**
1. Serbest mod (image): Şablonsuz devam → prompt yaz → Caption Üret → platform sekmelerinde caption'lar → image_prompt düzenle → Görseli Üret → Step 3 önizleme
2. Serbest mod (carousel): aynı akış
3. Şablon modu: regresyon yok (Sprint 5'te test edilen tüm akış korunmalı)
4. Video: Script Üret → İçerik Üret tek-tık (değişmedi)
5. Özel Gün/Alıntı: tek-tık akış (değişmedi)

## 2026-04-18 — Phase 7 Sprint 5 — /icerik-olustur wizard refactor (Akış C UI) ✅

**Kapsam:** `/icerik-olustur` wizard 3-fazlı Akış C UI'ına geçti. Step 1'deki 3 genel kategori (ürün/hizmet/kurumsal) kaldırıldı. Image/carousel için yeni akış: `phase=pick` (şablon grid) → `phase=form` (dinamik form) → `phase=caption` (caption+image_prompt düzenle) → Görsel üret → Step 3 preview. Video/special_day/quote akışları **aynen korundu**. Serbest içerik escape hatch'i var (`mode='free'`).

**Yeni bileşenler (4):**
- `components/templates/TemplateCard.tsx` — tek kart: icon + name + description + disclaimer rozeti + selected state
- `components/templates/TemplateGrid.tsx` — `fetchTemplates()` ile sektör+contentType filtresi, "Sektörünüze Özel" + "Genel Şablonlar" ayrı grid, "Şablonsuz devam et" escape butonu
- `components/templates/DynamicForm.tsx` — 6 field tipi (text/textarea/number/select/multi-select/url) + `field.group` bazlı gruplandırma + `validation` (min/max/minLength/maxLength) + disclaimer banner (template.defaults.disclaimer varsa)
- `components/templates/CaptionEditor.tsx` — platform sekmeli caption editörü ("Varsayılan" tab + platform tab'ları), `first_comment` alanı (useFirstComment varsa), hashtag editor, image_prompt edit textarea (İngilizce)

**Modifiye dosyalar (3):**
- `lib/store.ts` — `Brand` interface'ine `sector_slug`, `sector_display_name` eklendi (auth/init zaten dönüyordu)
- `lib/analytics.ts` — 6 yeni event: `templateSelected`, `templateFormSubmitted`, `templateCaptionGenerated`, `templateCaptionEdited`, `templateImageGenerated`, `templateAbandoned(phase)`
- `app/(dashboard)/icerik-olustur/page.tsx` — major refactor:
  - `CONTENT_CATEGORIES` + `ContentCategory` tipi + `category` state kaldırıldı
  - Yeni state: `mode: 'template'|'free'`, `phase: 'pick'|'form'|'caption'`, `selectedTemplate`, `templateFields`, `captionData`, `loadingCaption`
  - `handleGenerateCaption()` → `POST /posts/generate-caption` → `captionData` set edip `phase='caption'`'a geçer; required field kontrolü var, rate_limit/plan_limit error handling var
  - `handleGenerate()` template modda `template_id + template_fields + platform_captions + image_prompt` payload; legacy modda prompt-based
  - `handleSelectTemplate()` template seçiminde aspect ratio önerisini otomatik uygular (`template.output.aspectRatioSuggestion`)
  - `handleBackToPick()` + `handleFreeFormMode()` navigation helper'ları
  - Content type değişince template state (`selectedTemplate`, `templateFields`, `captionData`, `phase`, `mode`) sıfırlanır
  - `resetWizard()` template state'leri de temizler
  - `/ai/suggest-ideas` çağrısı artık `template_id` + `template_fields` gönderiyor (backend Sprint 3'te bunu destekliyordu)

**Preserved (backward compat):**
- Video (`contentType='video'`): script editor + voice seçimi + `/posts/generate-faceless-video` çağrısı aynen çalışıyor
- Özel Gün (`contentType='special_day'`): tatil seçici aynen; template'siz
- Alıntı (`contentType='quote'`): quote text + author; template'siz
- Image/carousel + `mode='free'`: mevcut prompt textarea akışı (kategori seçimsiz, template'siz)
- Trends → "İçerik Üret" query-param prefill akışı etkilenmedi (prompt+type+aspect param'ları hâlâ çalışıyor)

**Edge case'ler:**
- Zorunlu form alanı boşsa `handleGenerateCaption` toast ile uyarır
- `image_prompt` boşsa "Görseli Üret" butonu disabled
- Disclaimer banner `DynamicForm`'da şablon seçildikten sonra görünür; backend zaten caption sonuna otomatik ekliyor

**Risk & rollback:** Eski `POST /posts/generate` sözleşmesi geriye dönük çalışıyor (`template_id=null` legacy path). Frontend Tip Seçimi ekranında template kullanmak isteyen de istemeyen de devam edebilir. Rollback: tek dosya revert (icerik-olustur/page.tsx + 4 yeni bileşen delete) yeterli.

**Test planı (deploy sonrası canlı):**
1. E-Ticaret brand + image → "Sektörünüze Özel" altında MyGoodShoes şablonları (Ürün Kartı vs.) görünmeli
2. Ürün Kartı seç → form alanları çıkmalı → form doldur → "Caption Üret" → platform sekmelerinde Instagram/LinkedIn captions → image_prompt düzenle → "Görseli Üret" → Step 3
3. Sağlık brand + image → Biliyor Muydunuz? seç → form altında "⚠ Otomatik Disclaimer" banner → caption sonunda disclaimer otomatik eklenmiş olmalı
4. Serbest İçerik escape → şablonsuz prompt akışı çalışmalı
5. Video/special_day/quote → regresyon yok
6. Trends → "İçerik Üret" → query-param prefill hâlâ çalışmalı

**Sonraki:** Sprint 6 — Platform-spesifik publishing (per-platform caption'ları Upload-Post'a gönderirken doğru platform'a doğru caption yollanmalı).

## 2026-04-18 — Phase 7 Sprint 4 (Backend) — Caption endpoint + Akış C ✅

**Sprint 4 tamamen backend çalışması** (frontend dokunulmadı). Backend detayları: `apps/social/backend/CLAUDE.md` → "2026-04-18 — Phase 7 Sprint 4".

**Özet:** Yeni `POST /posts/generate-caption` endpoint'i Claude Opus 4.7 ile platform-spesifik caption + image_prompt + hashtag üretir. `POST /posts/generate` Akış C için güncellendi — caption endpoint'in ürettiği `image_prompt` + `platform_captions` payload'a gelirse legacy prompt inşası bypass edilir, caption/hashtags kolonlarına backward-fill yapılır.

**Frontend etkisi:** Henüz yok — Sprint 5'te `/icerik-olustur` wizard Akış C'ye geçecek (Önce caption önizle → sonra görsel üret). Şu an mevcut frontend akışı eski `POST /posts/generate` tek-çağrı şeklinde çalışmaya devam eder.

**Sonraki (frontend):** Sprint 5 — wizard refactor (şablon grid + dinamik form + caption preview ekranı).

## 2026-04-18 — Phase 7 Sprint 3 (Backend) — Prompt building refactor ✅

**Sprint 3 tamamen backend çalışması** (frontend dokunulmadı). Backend detayları: `apps/social/backend/CLAUDE.md` → "2026-04-18 — Phase 7 Sprint 3".

**Özet:** Prompt inşa mantığı `app/core/prompt_builder.py`'ye taşındı — 3-katman (system/brand/dynamic) + cache stratejisi. `posts.py` fal.ai image prompt akışı ve `ai.py` suggest-ideas akışı artık `template_id` varsa SECTOR_GUIDANCE + şablon guidance + yapısal form verileri enjekte ediyor.

**Frontend etkisi:** Hâlâ yok — `/icerik-olustur` wizard Sprint 4 (caption endpoint) ve Sprint 5 (wizard refactor)'a kadar legacy `content_category` akışıyla çalışmaya devam eder.

**Sonraki (frontend):** Sprint 5 — `/icerik-olustur` Step 2 şablon grid + dinamik form, sector filtering, template auto-prompt build.


> **Phase 6 — Trend Sistemi Yenileme (2026-04-16).**
> `/trendler` sayfası üç katmanlı yeni mimari için yeniden yazıldı (Layer A sektör paylaşımlı / Layer B Serper.dev+Haiku kişisel / Layer C Pro+ PDF rapor). Detaylı teknik plan: `~/otomaix/docs/06-social-trends-phase6.md`. Genel özet PDF: `~/otomaix/docs/otomaix_trends_update.pdf`.
> **İlerleme:** Sprint 1 ✅ · Sprint 2 ✅ · Sprint 3 ✅ · Sprint 4 ✅ · Sprint 5 ✅ · Sprint 6 ✅ — **Phase 6 tamamlandı**

## 2026-04-18 — Phase 7 Sprint 2: TypeScript Interface + Templates API Client ✅

**Kapsam:** Backend Sprint 2 ile senkron frontend artifact'leri — tip tanımları + API client. UI entegrasyonu Sprint 3'te (wizard refactor).

**Yeni dosyalar:**
- `lib/templates.types.ts` — **spec §3.1 birebir camelCase** interface'leri:
  - `Template`, `TemplateFormField`, `PlatformOverride`, `TemplateOutput`, `TemplatePromptExample`, `TemplatePrompt`, `TemplateDefaults`
  - Backend Pydantic `app/models/templates.py` ile birebir eşleşir (JSON transport düzeyinde hiç dönüştürme yok)
  - `TemplateFormField.type` union: `"text" | "textarea" | "number" | "select" | "multi-select" | "url"`
  - `platformOverrides`: 8 platform (instagram, linkedin, twitter, facebook, tiktok, threads, pinterest, bluesky)
- `lib/api/templates.ts` — API client helper'ları:
  - `fetchTemplates({ sector?, contentType? }): Promise<Template[]>` — `GET /templates?sector=X&content_type=Y`
  - `fetchTemplateById(id): Promise<Template | null>` — `GET /templates/{id}`
  - Mevcut `api.get()` wrapper kullanılır → otomatik auth header + error handling
  - Backend'in 1 saatlik HTTP cache'i (`Cache-Control: public, max-age=3600`) browser seviyesinde etkin

**Kullanım (Sprint 3'te aktif olacak):**
```typescript
import { fetchTemplates } from '@/lib/api/templates'
const templates = await fetchTemplates({
  sector: brand.sector_slug,      // "e-ticaret-perakende" vb.
  contentType: selectedType,       // "image" | "carousel"
})
// templates artık sektöre özel + genel (sectors=["*"]) şablonların birleşimi
```

**Etki analizi:**
- Risk: sıfır (yeni dosyalar, hiçbir mevcut sayfayı değiştirmedi)
- Eski `/icerik-olustur/page.tsx` hâlâ kategori bazlı akışla çalışır — Sprint 3'te refactor edilecek
- `lib/store.ts` `Brand.sector_slug` zaten Sprint 1'de eklenmişti (auth/init response'undan geliyor)

**Sonraki:** Sprint 3 — `icerik-olustur/page.tsx` Step 1/2 wizard refactor: 3 kategori butonu → şablon grid + dinamik form. `page.tsx` mount'ta `fetchTemplates()` çağırır, içerik tipi + marka sektörüyle filtreler.

## 2026-04-16 — İçerik Oluştur: 5 UX iyileştirmesi ✅

**Dosya:** `app/(dashboard)/icerik-olustur/page.tsx`

**Değişiklikler:**
1. **Video en-boy oranı seçici** — `!['video', 'special_day', 'quote']` filtresinden `video` çıkarıldı. Backend `generate-faceless-video` zaten `aspect_ratio` parametresi alıyordu, varsayılan 1:1 yerine kullanıcı seçebilir.
2. **Video "Bana fikir öner"** — Aynı filtreden `video` çıkarıldı. `fetchIdeas()` zaten `content_type: contentType` gönderiyor, backend video tipini destekliyor.
3. **Geçmiş özel günler disabled** — `isPast` olan tatil butonlarına `disabled` prop + `cursor-not-allowed` eklendi, `onClick` guard'ı eklendi.
4. **"Yeniden Üret" guard** — `disabled` koşuluna `|| !generatedPost?.output_url` eklendi. Output hazır olmadan regenerate tetiklenemez.
5. **Step 3→2 state temizliği** — Geri butonuna `setGeneratedPost(null)`, `setCaption('')`, `setHashtags([])` resetleri eklendi. Eski üretim state'i ile karışma riski ortadan kalktı.

## 2026-04-16 — Trends: Layer B son arama sonuçları cache'den yüklenme ✅

**Dosya:** `app/(dashboard)/trendler/page.tsx`

**Sorun:** "Kişisel Arama" sekmesi açıldığında her zaman boş state gösteriliyordu. Backend `brand_trend_cache`'e son aramayı kaydediyordu ama frontend bunu hiç okumuyordu.

**Çözüm:**
- `loadPersonalCache()` fonksiyonu eklendi — `GET /trends/personal?brand_id=` ile son cache'i okur
- `useEffect` tab geçişinde `personal` sekmesi için `loadPersonalCache()` çağrılır
- `personalFetchedAt` state: son arama tarihi gösterimi ("Son arama: 16.04.2026 14:30")
- `personalCacheLoading` state: cache yüklenirken spinner gösterimi
- Yeni arama yapıldığında `personalFetchedAt` güncellenir

## 2026-04-16 — Trends: Layer C rapor polling ✅

**Dosya:** `app/(dashboard)/trendler/page.tsx`

**Sorun:** `POST /trends/monthly-report` 202 döndükten sonra rapor durumu otomatik kontrol edilmiyordu. Kullanıcı raporun hazır olup olmadığını görmek için manuel "Yenile" butonuna basmak zorundaydı.

**Çözüm:**
- `useEffect` polling: `reports` içinde `status === 'generating'` olan rapor varsa 5sn'de bir `GET /trends/reports` çağrısı yapılır, `monthly` sekmesinden çıkınca interval temizlenir
- Durum geçişi toast: `generating` → `ready` olduğunda "Rapor hazır! PDF indirilebilir.", `failed` olduğunda hata mesajı toast ile gösterilir
- `prevGeneratingIdsRef` (useRef) ile önceki generating ID'leri takip edilir, yeni fetch sonucunda artık generating olmayan ID'ler için toast tetiklenir
- `generateReport()` içindeki `setTimeout(() => loadReports(), 2000)` kaldırıldı, yerine direkt `loadReports()` çağrısı — polling effect zaten devreye girer
- "Üretiliyor" satırındaki manuel "Yenile" butonu kaldırıldı, yerine "Otomatik kontrol ediliyor..." spinner göstergesi eklendi
- Aynı pattern: rakip analizi (B-5) polling ile tutarlı

**Backend değişiklik:** Yok — `GET /trends/reports` zaten `status` alanını döndürüyordu.

## 2026-04-16 — Phase 6 Sprint 6: PostHog trend event'leri ✅

**analytics.ts** — 5 yeni helper eklendi:
- `trendLayerAViewed(sector)` — Sektör Trendleri sekmesi yüklendiğinde
- `trendLayerBTriggered(sector)` — Kişisel arama başarılı olduğunda
- `trendLayerCGenerated(sector)` — Aylık rapor tetiklendiğinde
- `trendQuotaExhausted(layer)` — Kota aşıldığında (402)
- `trendPaywallShown(layer, currentPlan)` — Paywall gösterildiğinde

**trendler/page.tsx** — capture çağrıları eklendi:
- `loadTrends()` başarılı → `trendLayerAViewed`
- `runPersonalSearch()` başarılı → `trendLayerBTriggered`; 402 → `trendQuotaExhausted` + `trendPaywallShown`
- `generateReport()` başarılı → `trendLayerCGenerated`; 402 → `trendQuotaExhausted` + `trendPaywallShown`

## 2026-04-16 — Phase 6 Sprint 5: `/trendler` üç sekmeli yeniden yazım ✅

**Dosya:** `app/(dashboard)/trendler/page.tsx` (562 satır, tamamen yeniden yazıldı)

**Üç sekme:**
- **Sektör Trendleri (Layer A):** `GET /trends?brand_id=` → paylaşımlı cache, trend kartları grid, yenile butonu
- **Kişisel Arama (Layer B):** `POST /trends/personal?brand_id=` → kota göstergesi ("5/10 kullanıldı"), "Kişisel Trendleri Ara" butonu
- **Aylık Rapor (Layer C):** `POST /trends/monthly-report` → 202, rapor listesi (ready/generating/failed rozetleri), PDF indirme, "Yeni Rapor Üret" butonu

**Trend kartları:** title, source badge, relevance bar, summary, content_opportunity, suggested prompt, "İçerik Üret" butonu

**Paywall:** Backend 402 → toast mesajı + `/fiyatlandirma` yönlendirmesi

**Fix (2026-04-16):** Error handling uyumsuzluğu düzeltildi — `res.error === 'quota_exceeded'` ve `res.error === 'plan_locked'` kontrolleri kaldırıldı, yerine `res.plan_limit` objesi kontrolüne geçildi. Backend'in döndüğü Türkçe mesajlar (`plan_limit.message`) artık doğru gösteriliyor, `upgrade_url` ile dinamik yönlendirme yapılıyor.

## 2026-04-14 — F-1: Dashboard "Yayın Serisi" kartı kaldırıldı

Analiz raporundaki F-1'in son parçası. Stats kartları (Bu Ay Üretilen, Yayınlanan, Bağlı Platform) zaten canlı API verisine bağlıydı (önceki oturum); tek kalan hardcoded blok "Yayın Serisi" (Posting Streak) kartıydı. 7 günlük grid'in ilk 3'ü sabit mavi, kalanı gri, "3 gün serisi" yazısı da sabit — backend'de streak hesaplayan hiçbir servis/endpoint yok. Tüm kullanıcılara aynı yanıltıcı görünüm.

**Fix:** `dashboard/page.tsx` içinden Posting Streak Card JSX bloğu (27 satır) + kullanılmayan `DAYS` sabiti silindi. İleride gerçek streak servisi yazılırsa (örn. `/posts/stats/summary` endpoint'ine `current_streak` + `last_7_days[]` eklenerek) yeniden eklenebilir.

Bu commit ile analiz raporundaki tüm uygulanabilir F-* maddeleri (F-1 → F-5) kapandı.

## Proje Amacı
Otomaix Social uygulamasının Next.js 14 frontend'i. app.otomaix.com'da çalışır.

## 2026-04-14 — Marka Kimliği "Başlık/Alt Başlık Fontu" alanları kaldırıldı (ölü kod)

Backend audit: `fal_ai._build_image_prompt()`, `media_processor.apply_brand_processing()`, `faceless_video.generate_script()` ve diğer tüm görsel/video pipeline'ları `brand_kit.colors`, `brand_kit.tonality`, `brand_kit.logo_overlay`, `brand_kit.intro_video`'yu okuyor ama `brand_kit.fonts.*` alanları **hiçbir yerde kullanılmıyor**. Kullanıcı font seçiminin içeriğe hiçbir etkisi yoktu — yanıltıcı UX.

`marka-ayarlari/page.tsx`'den kaldırıldı:
- `BrandKit.fonts` tipi + `FontEntry` interface
- `FONT_FAMILIES` sabiti + `makeFontEntry` helper + `FontPatch` tipi
- `DEFAULT_BRAND_KIT.fonts`, `deepMergeKit` içindeki fonts merge
- UI'daki "Başlık Fontu" ve "Alt Başlık Fontu" 3'lü Select grid blokları

DB'deki mevcut `brand_kit.fonts` JSONB anahtarları olduğu gibi kalır (backend okumuyor, bir sonraki save'de `fonts` alanı içermeyen yeni kit yazılacağı için kaybolabilir — sorun değil, ölü veri).

## 2026-04-14 — Tabs bileşeni layout bug fix (marka-ayarlari görünüm sorunu)

Kullanıcı screenshot'la raporladı: `/marka-ayarlari` sayfasında sekmeler (Marka Bilgileri, Marka Kimliği, Görseller…) dikey olarak ortada, içerik sağda dar bir şeritte render oluyordu.

**Kök neden:** `components/ui/tabs.tsx` Tailwind data-attribute variant'larını köşeli parantez syntax'ı olmadan yazıyordu:
- `data-horizontal:flex-col` (yanlış) → `data-[orientation=horizontal]:flex-col` (doğru)
- `group-data-horizontal/tabs:*` / `group-data-vertical/tabs:*` → `group-data-[orientation=horizontal]/tabs:*` / `group-data-[orientation=vertical]/tabs:*`

Tailwind bu invalid class'ları hiçbir şeye eşleştirmediği için Tabs root'u varsayılan `flex-row`'da kalıp TabsList sola, TabsContent sağa yerleşiyordu.

**Fix:** 4 konumda (Tabs root, tabsListVariants, TabsTrigger ana class, TabsTrigger `after:` bloğu) bracketed syntax'a çevrildi. Tabs yalnızca `marka-ayarlari`'nde kullanılıyor — başka sayfayı etkilemedi. Typecheck temiz.

## 2026-04-14 — F-4 + F-5: Marka Ayarları web analizi + İçerik Oluştur ölü kod temizliği

Analiz raporundaki P1 maddeleri:

### F-5 — `icerik-olustur/page.tsx` "Yakında" rozet ölü kodu
`CONTENT_TYPES` dizisindeki tüm tipler `active: true` idi ama Step 1 render'da hala `!type.active` dalı ("Yakında" badge + disabled styling) duruyordu. Hiçbir yerde tetiklenmeyen ölü kod.
- `CONTENT_TYPES` üzerinden `active: true` alanı kaldırıldı
- `<button>` render'ı sadeleştirildi: `disabled={!type.active}`, "Yakında" span'i, `!type.active && opacity-50` class dalı, `type.active ? ... : ...` ternary'leri silindi
- Davranışsal değişiklik yok — sadece ölü kod temizliği

### F-4 — Marka Ayarları "Otomatik Doldur" butonu işlevselleştirildi
`marka-ayarlari/page.tsx` Web Sitesi input'unun yanındaki buton daha önce `toast.info('Web sitesi analizi yakında')` döndürüyordu. Onboarding (`(onboarding)/onboarding/page.tsx`) aynı `POST /ai/analyze-website` çağrısını yapıyordu — kod kopyalandı ve adapt edildi.

- `analyzingWebsite` state eklendi
- `analyzeWebsite()` handler'ı: `brand.website_url` alanını `POST /ai/analyze-website`'e gönderir; response'tan gelen `name/description/sector`'ı `updateBrand()` ile, `colors/tonality`'yi `updateKit()` ile deep-merge'ler. Mevcut `scheduleSave` debounce'u otomatik kaydetmeyi halleder.
- Buton `onClick={analyzeWebsite}` + `disabled={analyzingWebsite}`, loading state'inde "Analiz ediliyor..." gösterir
- Yalnızca response'ta dolu gelen alanları update eder (boş string'le mevcut veriyi silmez)

## 2026-04-14 — Dashboard stats + ContentCard hover butonları fix

Kullanıcı raporladı: (1) `icerik-kutuphanesi` kartlarındaki hover butonları çalışmıyor, (2) dashboard "Bu Ay Üretilen" ve "Yayınlanan" kartları 1 içerik yayınlanmış olmasına rağmen 0 gösteriyor.

**Dashboard stats** (`dashboard/page.tsx`):
- `stats` state eklendi: `{ generated_this_month, published_total }`
- `useEffect` `/posts/stats/summary?brand_id=...` çağırıyor, kart başlıklarındaki hardcoded `0`'lar gerçek değerlerle değişti.
- Backend tarafında yeni endpoint: `GET /posts/stats/summary` — `date_trunc('month', now())` ile ay başı filtresi + `status='published'` count.

**ContentCard hover butonları** (`components/content/ContentCard.tsx`):
- "Zamanla" ve "Daha Fazla" butonları daha önce `onClick` handler'ı olmayan stub'lardı.
- Her ikisi de artık `onClick(post)` çağırıyor → kartın detay modalı açılıyor (modal'da zamanlama picker'ı ve tüm aksiyonlar mevcut).
- "İndir" ve "Yayınla" zaten çalışıyordu — onlara dokunulmadı.

## 2026-04-14 — F-2 rev-3: Publish butonları yarış koşulu fix

Canlı test: tek "Şimdi Yayınla" tıklamasına Instagram 4 post yayınladı. Sebep: `useState` tabanlı `publishing` guard'ı async — React state update tamamlanmadan önce gelen ikinci click geçip yeni HTTP isteği fırlatıyor. Hızlı birkaç tıklama (veya kullanıcı mashlaması) birden çok publish çağrısına dönüşüyor.

Fix: tüm publish handler'larına `useRef` tabanlı **senkron** guard eklendi:
- `icerik-kutuphanesi/page.tsx` — `publishingRef` (modal), `publishInFlightRef: Set<string>` (kart hover butonu için per-post kilit)
- `icerik-olustur/page.tsx` — `publishingRef`
- `takvim/page.tsx` — `publishingRef`
- `STATUS_LABEL` sözlüklerine yeni `'publishing'` durumu eklendi → "Yayınlanıyor"

Backend tarafında asıl düzeltme `publish_post` içinde `SELECT FOR UPDATE` + intermediate `status='publishing'` ile idempotency. Frontend guard'ları UX (spinner görünsün, buton disabled olsun) için, backend guard ise veri bütünlüğü için.

## 2026-04-14 — F-2 rev-2: Upload-Post backend refactor (frontend değişmedi)

Mevcut F-2 frontend'i (dashboard + marka-ayarlari) hiçbir değişiklik gerektirmedi — aynı API sözleşmesi (`GET /social/oauth-link`, `GET /social/accounts`) korundu. Semantik değişiklik sadece backend'de:
- `oauth-link` response'u artık Upload-Post'un kendi `access_url`'sini içeriyor (`https://app.upload-post.com/connect?token=...`). Bu URL `window.open()` ile popup olarak açılıyor, kullanıcı bağlama işlemini Upload-Post arayüzünde tamamlıyor, işlem bitince `redirect_url` ile `marka-ayarlari?tab=sosyal&connected=1`'e geri dönüyor.
- `accounts` endpoint'i her çağrıda Upload-Post'tan sync yapıyor — dashboard açılınca veya sosyal sekmesi açılınca güncel durum görünüyor (cache gecikmesi yok).

## 2026-04-14 — F-2: Dashboard "Bağla" butonları + marka-ayarlari OAuth fix

### dashboard/page.tsx
- `PLATFORMS` dizisine `key` alanı eklendi (`instagram`, `tiktok`, `linkedin`).
- `connectedPlatforms: string[]` state + `useEffect` ile `GET /social/accounts?brand_id=...` çağrılıyor — aktif marka değişince yeniden yüklenir.
- "Bağla" butonu artık `handleConnectPlatform()` çağırır → `GET /social/oauth-link?brand_id=...&platform=...` → `window.open(url, '_blank', 'noopener')`.
- Bağlı platformlar için buton "Bağlı ✓" (secondary variant); değilse "Bağla" (outline). Loading'de spinner.
- "Bağlı Platform" stat kartı artık `connectedPlatforms.length` gösterir (önceden hardcoded 0).

### marka-ayarlari/page.tsx
- **KRİTİK FIX**: `connectSocialAccount()` `brand_id` parametresini gönderiyordu — backend `oauth_link` endpoint'i `brand_id`'yi zorunlu UUID query param olarak istediği için her çağrı 422 dönüyordu (özellik tamamen kırıktı).
- Şimdi `?brand_id=${brand.id}&platform=${platform}` formatında gönderiliyor; `noopener` flag eklendi.
- Yeni state: `connectedAccounts`, `connectingPlatform`. Sosyal sekmesi açıldığında `GET /social/accounts` çağrılır.
- Bağlı platformlar için yeşil ✓ + `account_name` gösterilir; buton "Hesabı Bağla" yerine "Yeniden Bağla" yazar.
- Loading state'i butonda spinner ile gösterilir.

## 2026-04-14 — F-3: İçerik Oluştur Step 3 butonları aktive edildi

`icerik-olustur/page.tsx` Step 3'te daha önce stub olan iki buton artık çalışıyor:
- **Şimdi Yayınla** → `persistCaption()` (PATCH /posts/{id}) → `POST /posts/{id}/publish` → `/icerik-kutuphanesi`'ne yönlendir
- **Takvime Ekle** → custom date dialog (datetime-local input) → caption kaydet → `PATCH /calendar/schedule/{id}` → `/takvim`'e yönlendir
- Buton state'leri: `publishing`, `scheduling`, `showScheduleDialog`, `scheduleAt`. Hepsi loading spinner ile disable olur. `output_url` yokken her iki buton disable.
- Plan limit dönerse `UpgradeModal` gösterilir (publish endpoint'i de check_plan_limit'e tabi değil ama yine de güvenlik için).
- Geçmiş tarih validasyonu client-side yapılıyor; backend zaten `assert_post_owned` ile sahiplik kontrolü yapıyor.
- `useRouter` import'u eklendi (`next/navigation`).

## 2026-04-14 — Plan limit (HTTP 402) handling

`lib/api.ts` HTTP 402 yanıtlarını artık özel olarak yakalıyor:
- Backend'in `detail: { error, message, upgrade_url, current_plan }` objesi `ApiResponse.plan_limit` alanına mapleniyor.
- `ApiResponse<T>` discriminated union'a `plan_limit?: PlanLimitInfo` eklendi.
- Daha önce `body.detail` bir obje olduğunda string concat → `"[object Object]"` yazıyordu. Yeni `extractErrorMessage()` helper'ı obje detail'lerden `message` alanını çıkarır.

Paywall modal entegrasyonu yapılan sayfalar:
- `markalar/page.tsx` — yeni marka oluştururken brand limit aşımında `UpgradeModal`
- `marka-ayarlari/page.tsx` — avatar oluştururken avatar limit aşımında `UpgradeModal`
- `icerik-olustur/page.tsx` — image/video/special_day/quote üretirken post/video limit aşımında `UpgradeModal` (4 dalın hepsi)
- `trendler/page.tsx`, `dashboard/page.tsx` — trend kartından içerik üretirken plan_limit toast mesajı
- `onboarding/page.tsx` — first brand create için plan_limit toast (genelde isabet etmez)

`UpgradeModal` zaten mevcuttu (`components/billing/UpgradeModal.tsx`).

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
- Deploy: Coolify (servis adı: otomaix-social-frontend)
- URL: https://app.otomaix.com

## Bağımlılıklar
- Backend API: https://api.otomaix.com
- Supabase Auth: JWT authentication
- Cloudflare R2: assets.otomaix.com

## Gerekli .env.local Değişkenleri
```
NEXT_PUBLIC_SUPABASE_URL=https://sqplkkivtkfyozrvnybe.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...  ← Dolu ✅
NEXT_PUBLIC_API_URL=https://api.otomaix.com
NEXT_PUBLIC_ASSETS_URL=https://assets.otomaix.com
```

## Tamamlanan İşler

### Phase 1
- [x] Next.js 14 projesi kuruldu
  - shadcn/ui (base-nova theme) + Tailwind CSS
  - Zustand store (user, currentWorkspace, currentBrand)
  - Supabase auth (Google OAuth + email/password)
  - 250px sabit sidebar layout + SidebarNav (Türkçe route'lar)
  - Dashboard iskelet sayfası
  - Dockerfile (multi-stage, standalone output)
  - middleware.ts (auth koruması — sonradan kaldırıldı, layout'a taşındı)
  - `app/auth/callback/page.tsx` — Google OAuth callback handler

### Phase 2
- [x] Adım 1b — Marka Ayarları (`/marka-ayarlari`)
  - 5 sekme: Marka Bilgileri, Marka Kimliği, Görseller, Sosyal Hesaplar, Dokümanlar
  - Debounce otomatik kaydetme (1.5s) + "Kaydedildi ✓" göstergesi
  - Renk seçici, font seçici (letterCase), hashtag tag-input
  - Logo upload (light/dark) + intro video upload → R2
  - Sonner toast provider entegre edildi
  - **OAuth callback handling**: `useSearchParams` ile `?connected=platform` ve `?error=...` query parametreleri işlenir
    - Başarılı bağlantı → success toast + "sosyal" sekmesine otomatik geçiş
    - Hata → error toast
    - URL `window.history.replaceState` ile temizlenir
    - `<Tabs value={activeTab} onValueChange={setActiveTab}>` (controlled)

- [x] Adım 2b — İçerik Oluşturma Wizard (`/icerik-olustur`)
  - 3 adımlı React state machine (URL değişmez)
  - Adım 1: 5 içerik tipi kartı (tümü aktif), kategori seçimi (special_day/quote için gizlenir)
    - `image`, `carousel`, `video` → mevcut pipeline
    - `special_day` → `/calendar/holidays` API'den tatil listesi, kullanıcı seçer
    - `quote` → alıntı metni + opsiyonel yazar alanı
  - Adım 2 sıralaması: En-Boy Oranı → Platformlar → Dokümanlar → İçerik Açıklaması → Bana Fikir Öner → İçerik Üret
  - Adım 2 (type'a göre farklı UI):
    - `image`/`carousel`: En-Boy Oranı + Platformlar + Dokümanlar + İçerik Açıklaması + "Bana fikir öner" (3 öneri)
    - `video`: İçerik Açıklaması + Script editörü + ses seçimi (mor tema)
    - `special_day`: Tatil grid (scrollable, geçmiş tatiller soluk) + opsiyonel not alanı (sarı tema)
    - `quote`: Alıntı textarea + yazar inputu (mor tema)
  - "Kendi metnini ekle" toggle kaldırıldı — tek alan: İçerik Açıklaması
  - **"Bana fikir öner"**: `POST /ai/suggest-ideas` → sabit **3 öneri** döner
    - Gönderilen bağlam: `content_type`, `content_category`, `prompt`, `document_ids`, `platforms`
    - Backend RAG ile seçili doküman içeriğini de prompt'a dahil eder
    - İçerik tipine özel talimat: video için senaryo fikirleri, görsel için tasarım fikirleri vb.
  - Adım 3: Üretim animasyonu, görsel önizleme, caption + hashtag editörü, eylem butonları
  - **Validasyon**: `special_day` → selectedHoliday zorunlu; `quote` → quoteText zorunlu; diğerleri → prompt zorunlu
  - **State**: `holidays[]`, `selectedHoliday`, `quoteText`, `quoteAuthor` eklendi
  - **Backend**: `POST /posts/generate` → `content_type: 'special_day' | 'quote'` ile çağrılır

- [x] Adım 3 — İçerik Kütüphanesi (`/icerik-kutuphanesi`)
  - ContentCard bileşeni (`components/content/ContentCard.tsx`)
    - `onPublish` prop: hover "Yayınla" butonunu bağlar → `POST /posts/{id}/publish`
  - CSS columns masonry grid (3 sütun)
  - IntersectionObserver ile infinite scroll
  - Filter Sheet (sağdan, tip/durum/platform)
  - Post detail Dialog
    - "Şimdi Yayınla" → `POST /posts/{id}/publish` (loading state, toast, status güncelleme)
    - "Onay İste" → `POST /posts/{id}/request-approval` (loading state, toast, status → 'reviewing')
    - Butonlar sadece ready/failed/rejected durumlarında aktif
  - Freemium watermark + "Filigranı Kaldır" CTA

- [x] Adım 4 — İçerik Takvimi (`/takvim`)
  - FullCalendar (dayGrid + timeGrid + interaction, Türkçe locale)
  - Aylık / Haftalık toggle
  - Durum renkleri + legend (milli tatil mor, dini bayram amber)
  - Tatil gösterimi: **her tatil için 2 event** ekleniyor
    - `holiday-bg-{date}`: `display:'background'` → renkli arka plan (milli: #7C3AED, dini: #F59E0B)
    - `holiday-label-{date}`: transparent event → `extendedProps.isHolidayLabel: true` → isim yazısı
    - ⚠️ `display:'background'` event başlık gösteremiyor — bu yüzden ayrı label event şart
    - `globals.css` → `.fc-bg-event { opacity: 0.5 }` (0.25 çok düşüktü, görünmüyordu)
  - Drag & drop → PATCH /calendar/schedule
  - Geçmiş tarih koruması + yeni içerik dialog
  - Post detay modal
    - "Şimdi Yayınla" → `POST /posts/{id}/publish` (loading, toast, event rengi güncelleme)
    - "Onay İste" → `POST /posts/{id}/request-approval` (loading, toast)

- [x] Adım 5b — Otomatik Yayın Wizard (`/otomatik-yayin`)
  - Config yoksa setup CTA, varsa Summary Dashboard
  - 4 adımlı wizard: Konular → Platformlar → Program → Özet
  - "Bana konu öner" AI butonu (Claude'dan 5 öneri)
  - Sıklık seçimi + saat dilimi picker
  - Telegram onay toggle + **müşteriye özel** Bot Token + Chat ID alanları
    - @BotFather kurulum talimatları (token için)
    - @userinfobot yönlendirmesi (chat ID için)
    - Her müşteri kendi botunu kullanır (global token yok)
  - Aktif/Pasif toggle, sonraki yayın listesi
  - `AutopostingConfig` interface: `telegram_bot_token` + `telegram_chat_id` alanları eklendi
  - `handleSave` → her iki alan API'ye gönderilir

- [x] Adım 7 — Onboarding Akışı (`/onboarding`)
  - `app/(onboarding)/layout.tsx` — koyu tam ekran layout, header logo
  - `app/(onboarding)/onboarding/page.tsx` — 7 adımlı wizard
    - Adım 1: Hoş Geldiniz kartı (3 özellik özeti)
    - Adım 2: Web Sitesi URL → `POST /ai/analyze-website` → otomatik doldur
    - Adım 3: Marka bilgileri formu (isim, açıklama, sektör, renk önizleme)
    - Adım 4: Kullanıcı tipi (Küçük İşletme / Ajans / Serbest Çalışan / Kurumsal)
    - Adım 5: Sosyal medya hedefleri (çoklu seçim)
    - Adım 6: Platform seçimi (bağlantı daha sonra)
    - Adım 7: Özet + `POST /brands` + `PATCH /brands/{id}/kit` → `/dashboard`
  - middleware.ts → artık no-op (sadece `NextResponse.next()` döner)
  - `StepIndicator` bileşeni (nokta + çizgi + label)

## Tamamlanan Deploy Adımları
- [x] Migration 002 çalıştırıldı (`002_autoposting.sql`)
- [x] Coolify deploy yapıldı (frontend + backend)

### Phase 3

#### Tamamlanan
- [x] Adım 1 — Doküman yönetimi UI
  - `app/(dashboard)/marka-ayarlari/page.tsx` → Dokümanlar sekmesi tamamen işlevsel
    - Upload (drag/click), dosya tipi kısıtı (.pdf,.doc,.docx,.xls,.xlsx,.txt)
    - Yüklenen doküman listesi (isim, boyut, RAG mod gösterimi)
    - Silme butonu + confirm dialog
  - `app/(dashboard)/icerik-olustur/page.tsx` → Step 2'de "Dokümanlardan Bağlam Ekle" bölümü
    - Markanın dokümanları listelenir, çoklu seçim mümkün
    - `selectedDocIds` → `document_ids` olarak API'ye gönderilir
  - `BrandDocument` interface eklendi (her iki sayfada)

- [x] Adım 2b — Faceless Video frontend
  - `app/(dashboard)/icerik-olustur/page.tsx` içinde "Video (Faceless)" kartı aktif edildi
  - Step 2'de video kartı seçildiğinde mor tema ile script editörü + ses seçici gösteriliyor
    - "Script Üret" butonu → `POST /ai/generate-script`
    - Script textarea (düzenlenebilir)
    - Ses seçici (`GET /posts/voices/turkish`) — default Emel (Kadın)
    - Süre tahmini göstergesi
  - Step 3'te video için ayrı önizleme:
    - Video player (output_url hazırsa) veya render-loading state
    - Script gösterimi + ses dosyası `<audio>` player
  - `TurkishVoice`, `GeneratedPost` interface'leri genişletildi
  - Video generate → `POST /posts/generate-faceless-video`

- [x] Adım 3b — AI Avatar frontend
  - `app/(dashboard)/marka-ayarlari/page.tsx` → yeni "AI Avatar" sekmesi (6. sekme)
    - Aktif avatar özet kartı (isim, tip, preview + "Video Üret" butonu)
    - Kendi avatarı: dashed upload area → `POST /avatar/create` (multipart)
    - Hazır avatarlar grid (2×4): `GET /avatar/stock` → kart tıkla → `POST /avatar/select-stock`
    - Seçili avatar üzerinde violet check işareti
  - `StockAvatar`, `ActiveAvatar` interface'leri eklendi
  - `BrandKit.avatar` alanı eklendi

- [x] Adım 4b — Rakip analizi frontend
  - `app/(dashboard)/rakip-analizi/page.tsx` oluşturuldu
    - Sol kolon: rakip kartları listesi (yenile + sil butonları)
    - Sağ kolon: analiz detay paneli (Instagram metrikleri, PieChart, web analizi)
    - "Rakip Ekle" modal → `POST /competitors`
    - "Özet Rapor" butonu → `GET /competitors/report/summary`
    - AI rapor kartı (fırsatlar + öneriler)
    - recharts PieChart (içerik dağılımı)
  - `recharts` paketi eklendi (`package.json`)

- [x] Adım 5b — Trend Analizi Frontend
  - `app/(dashboard)/trendler/page.tsx` — tam trendler sayfası
    - Kaynak filtresi (Tümü / Haber / Google Trends / Genel)
    - Trend kartları (başlık, kaynak, uyum skoru, içerik fırsatı, öneri prompt)
    - "İçerik Üret" butonu → `/trends/{index}/create-post` → kütüphaneye yönlendir
    - "Yenile" butonu → `/trends/refresh`
  - Dashboard'a "Bu Hafta Sektörünüzde Trendler" widget eklendi
    - Top 5 trend listesi, hover'da "İçerik Üret" butonu
    - "Tüm Trendler →" linki
  - SidebarNav'a "Trendler" linki eklendi (TrendingUp ikonu)

- [x] Adım 6b — Logo Overlay + Intro Video UI
  - Marka Ayarları → Görseller sekmesi zaten tamamdı:
    - Logo Filigran toggle + konum seçici + opaklık slider
    - Intro/Outro video yükleme + pozisyon seçici (Başında/Sonunda/Her İkisi)
  - Backend işleme otomatik (fal.ai webhook'ta)

- [x] Adım 7b — Paddle Ödeme Frontend
  - `app/(dashboard)/fiyatlandirma/page.tsx` — 4 plan kartı (Starter/Pro/Business/Agency)
    - Mevcut plan vurgusu, "En Popüler" badge
    - "Planı Seç" → `/billing/checkout` → Paddle'a yönlendir
  - `app/(dashboard)/faturalandirma/page.tsx`
    - Mevcut plan + durum + yenileme tarihi
    - Kullanım progress bar'ları (içerik + marka)
    - "Faturalar & Yönetim" → Paddle customer portal
    - Plan özellikleri (video/avatar aktif mi)
  - `components/billing/UpgradeModal.tsx` — 402 hatalarında gösterilecek modal
  - SidebarNav'a "Faturalandırma" linki eklendi (CreditCard ikonu)

- [x] Adım 8b — Çoklu Marka Brand Switcher
  - `lib/store.ts` → `brands[]`, `setBrands()`, `switchBrand()` eklendi; tipler export edildi
  - `app/(dashboard)/layout.tsx` → `/auth/init` ile tek çağrıda user+workspace+brands yüklendi
    - `currentBrand` otomatik olarak ilk markaya set edilir
  - `components/layout/BrandSwitcher.tsx` — sidebar dropdown bileşeni
    - Logo/avatar + marka adı + sektör gösterimi
    - Tüm markaları listeler, aktif olanı işaretler
    - "Yeni Marka Ekle" → `/markalar` sayfasına yönlendirir
  - `components/layout/Sidebar.tsx` → BrandSwitcher logo ile nav arasına eklendi
  - `app/(dashboard)/markalar/page.tsx` — marka yönetim sayfası
    - Grid görünüm, aktif marka vurgusu
    - "Yeni Marka Ekle" modal (isim, sektör, açıklama)
    - "Düzenle" → marka ayarlarına; "Sil" → confirm modal
  - SidebarNav'a "Markalar" (Building2) linki eklendi

### Phase 4

#### Tamamlanan
- [x] Adım 1b — Self-Serve Onboarding Frontend
  - `app/page.tsx` — Tam public landing page (unauthenticated)
    - Sticky header: logo + nav + "Giriş Yap" + "Ücretsiz Dene" CTA'ları
    - Hero: "Türk KOBİ'ler için AI Sosyal Medya Otomasyonu" + 14 gün ücretsiz badge
    - 6 özellik kartı (AI Görsel, Faceless Video, AI Avatar, Otomatik Yayın, Rakip Analizi, Trend Takibi)
    - İstatistik bandı (10K+ içerik, 500+ marka, 4.9★, 6 saat tasarruf)
    - 4 plan kartı (Starter/Pro/Business/Agency), "En Popüler" badge
    - Footer + final CTA bölümü
  - `app/(auth)/kayit/page.tsx` — Kayıt sayfası
    - Google OAuth (primary) + email/şifre formu
    - Email doğrulama bekle ekranı (success state)
    - "Zaten hesabınız var mı? Giriş yapın" linki
  - `components/layout/Sidebar.tsx` — Trial banner eklendi
    - `trial_ends_at` varsa "🎁 Deneme: X gün kaldı" banner gösteriliyor
    - Tıklanınca `/fiyatlandirma`'ya yönlendiriyor
    - `TrialBanner` bileşeni: kalan gün hesaplama + 0'a düşünce gizlenme
  - `lib/store.ts` — `User.trial_ends_at?: string | null` eklendi
  - `app/(onboarding)/onboarding/page.tsx` — Adım 4'e "Daha Sonra Atla" eklendi
    - Kullanıcı tipi seçilmediyse "Daha Sonra Atla →" butonu gösteriliyor
    - Seçim yapılınca normal "Devam →" butonu çıkıyor

- [x] Adım 2b — PostHog Analytics Frontend
  - `posthog-js` paketi kuruldu
  - `lib/analytics.ts` — typed event wrapper (identify/reset + 20+ typed helper, no-op key yoksa)
  - `components/providers/PostHogProvider.tsx` — PostHog init + `usePathname` pageview tracking
  - `components/providers/Providers.tsx` — PostHogProvider ile sarmalandı
  - `app/(dashboard)/layout.tsx` — `/auth/init` sonrası `posthog.identify(userId, {email, plan})`
  - `components/layout/Sidebar.tsx` — logout'ta `posthog.reset()`
  - Eventler eklenen sayfalar:
    - `fiyatlandirma/page.tsx`: `pricing_page_viewed`, `plan_selected`, `checkout_started`
    - `takvim/page.tsx`: `calendar_opened`
    - `trendler/page.tsx`: `trend_post_created`
    - `icerik-olustur/page.tsx`: `content_creation_started`, `idea_suggestion_used`, `document_reference_used`, `content_generated`
    - `onboarding/page.tsx`: `onboarding_started`, `onboarding_step_completed`, `onboarding_completed`
  - Env değişkeni: `NEXT_PUBLIC_POSTHOG_KEY`, `NEXT_PUBLIC_POSTHOG_HOST`

- [x] Adım 3b — Sentry Error Monitoring (frontend)
  - `@sentry/nextjs@8.55.1` kuruldu
  - `sentry.client.config.ts` — client init (replay entegrasyonu dahil, %5 session / %100 error)
  - `sentry.server.config.ts` — server-side init
  - `sentry.edge.config.ts` — edge runtime init
  - `instrumentation.ts` — Next.js 14 register() hook → server/edge init
  - `next.config.mjs` — `withSentryConfig` wrapper (source map upload kapalı)
  - `app/(dashboard)/layout.tsx` — `/auth/init` sonrası `Sentry.setUser({id, email})`
  - Env değişkeni: `NEXT_PUBLIC_SENTRY_DSN`

- [x] Adım 4b — Redis Cache ve Rate Limiting (frontend)
  - `lib/api.ts` → HTTP 429 yakalanıyor: `{ success: false, error: 'rate_limit', retry_after: N }`
  - `lib/api.ts` → `apiFetch` ve `apiUpload` try-catch ile sarmalandı — `TypeError: Failed to fetch` artık `{ success: false, error: message }` döndürür (sayfa donmaz)
  - `lib/api.ts` → `!res.ok` kontrolü eklendi — 401/403/500 vb. HTTP hataları da `success: false` olarak döner
  - `ApiResponse<T>` discriminated union tipi export edildi
  - `icerik-olustur/page.tsx` → rate_limit hatasında adım 2'ye geri döner + kaç saniye bekleyeceğini söyleyen toast
  - `icerik-olustur/page.tsx` → doküman bölümü her zaman gösterilir; yüklü belge yoksa Marka Ayarları → Dokümanlar linkine yönlendiren mesaj gösterilir

- [x] Adım 6 — Crisp Chat Entegrasyonu
  - `components/providers/CrispProvider.tsx` — Crisp script yükleme (vanilla JS, ekstra paket yok)
    - Türkçe locale, violet tema rengi, sağ alt köşe
    - `crispIdentify(user)` — login sonrası kimlik gönderir (email, nickname, plan, brands_count)
    - `crispReset()` — logout'ta oturum sıfırlar
  - `components/providers/Providers.tsx` — CrispProvider eklendi
  - `app/(dashboard)/layout.tsx` — `/auth/init` sonrası `crispIdentify()` çağrısı
  - `components/layout/Sidebar.tsx` — logout'ta `crispReset()` çağrısı
  - `app/globals.css` — mobilde (< 768px) Crisp widget gizlendi
  - Env değişkeni: `NEXT_PUBLIC_CRISP_WEBSITE_ID`

- [x] Adım 7 — Performance Optimizasyonu
  - DB pool min_size=5 / max_size=20
  - /health endpoint DB + Redis kontrol
  - 011_performance_indexes.sql — posts/chunks/trend_cache CONCURRENTLY index'ler
  - FullCalendar + recharts → next/dynamic lazy loading (ayrı chunk)
  - FullCalendar ref: CalendarApi ref (dynamic component compat)

- [x] Adım 8 — Load Testing
  - `shared/load-tests/locustfile.py` — 6 senaryo, JWT/HealthOnly modları
  - Smoke test geçti: /health 5ms, /billing/plans 5ms, 0 hata

### Phase 4 Tamamlandı ✅

## Mevcut Durum
- Social Frontend: **Tüm fazlar tamamlandı** (Phase 1–4) ✅
- CRM Admin Paneli: **Tüm adımlar tamamlandı** (Adım 1–8) ✅
  - https://crm.otomaix.com canlıda
  - Social frontend'de yapılacak iş yok

## Paket Listesi (önemli)
- `@fullcalendar/react` + daygrid + timegrid + interaction + core
- `sonner` (toast)
- `@base-ui/react` (shadcn base-nova — Select, Sheet, Dialog, vb.)

## Teknik Notlar
- `@base-ui/react` Select `onValueChange` → `string | null` döner
  → `onSelect(v, fn)` helper kullanılıyor (`null` filtreler)
- BrandKit `case` alanı TypeScript keyword çakışması nedeniyle `letterCase` olarak yeniden adlandırıldı
  → Backend JSONB'deki eski `case` değerleri deepMerge'de her ikisi de okunuyor
- `api.patch()` ve `api.upload()` (multipart) `lib/api.ts`'e eklendi
- FullCalendar CSS override'ları `app/globals.css`'e eklendi

## Önemli Kararlar
- Tüm tarihler UTC olarak saklanır
- App Router kullanılıyor (Next.js 14)
- Türkçe varsayılan dil
- next-intl kurulmadı (tr.json manuel yönetiliyor — basit tutmak için)
- Supabase client SSR'da no-op, yalnızca client-side çalışıyor
- Supabase session **localStorage**'da tutulur (cookie değil) → middleware'den okunamaz
  - Auth koruması `app/(dashboard)/layout.tsx`'te `onAuthStateChange` ile yapılır
    - `getSession()` **kullanılmıyor** — Google OAuth hash fragment işlenmeden önce null dönebilir (race condition)
    - `onAuthStateChange` mount anında `INITIAL_SESSION` event'ı ile hemen tetiklenir; session varsa `/auth/init` çağrılır, yoksa `/login`'e yönlendirir
  - Google OAuth sonrası `/auth/callback` sayfası `onAuthStateChange` ile session'ı bekler, sonra `/dashboard`'a yönlendirir
  - `login/page.tsx`'te `redirectTo: window.location.origin + '/auth/callback'` kullanılır
- SSR hydration: `new Date()` / `Date.now()` komponent body'sinde kullanılmaz, `useEffect` içinde `useState` ile alınır
  - `getGreeting()` (dashboard/page.tsx) ve `TrialBanner` (Sidebar.tsx) bu kurala göre düzenlendi
- Tiptap yerine Textarea kullanıldı (caption editörü) — daha az bağımlılık
