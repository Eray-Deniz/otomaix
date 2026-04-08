# 02 — Social Uygulaması: Phase 2 — Temel Özellikler
> **Süre:** Ay 2–3  
> **Ön koşul:** `01-social-phase1.md` tamamlanmış ve kontrol listesi ✅  
> **Hedef:** Kullanıcının gerçekten kullanabileceği ilk sürüm — içerik üretimi, takvim, brand kit, auto posting

---

## Bu Phase'de Ne Yapılıyor?

Phase 2 sonunda elimizde şunlar olacak:
- İçerik oluşturma wizard'ı (Image + Carousel ile başlıyoruz)
- FullCalendar entegrasyonu — içerik takvimi, drag & drop
- Türkiye takvimi — milli/dini bayramlar otomatik işaretleniyor
- Brand Kit kurulumu — logo, renkler, font, sosyal hesap bağlama
- Content Library — masonry grid, infinite scroll, filtreler
- Auto Posting wizard — 4 adımlı yapılandırma
- Telegram onay workflow'u — içerik yayından önce onaylanıyor
- İlk pilot müşteri alınabilir

---

## Adım 1: Brand Kit Sayfası

**Ne yapılıyor:** Kullanıcı markasını tanımlıyor. Bu bilgiler sonraki tüm içerik üretimlerinde AI prompt'una inject edilir.

**Claude Code session:** `~/otomaix/apps/social/frontend/`

### 1a. Backend — Brand Kit endpoint'leri

**Claude Code'a ver (backend session'ında):**
```
Add brand kit endpoints to app/routers/brands.py:

GET /brands → list all brands for current workspace
POST /brands → create new brand
GET /brands/{brand_id} → get brand with brand_kit details
PATCH /brands/{brand_id}/kit → update brand_kit JSONB field

The brand_kit JSONB structure is:
{
  "colors": ["#hex1", "#hex2", "#hex3"],   // min 3 required
  "fonts": {
    "title": {"family": "Inter", "weight": "700", "case": "none"},
    "subtitle": {"family": "Inter", "weight": "400", "case": "none"}
  },
  "social_handle": "@handle",
  "hashtags": ["#tag1", "#tag2"],
  "tonality": "professional",  // professional/friendly/fun/informative
  "timezone": "Europe/Istanbul",
  "voiceover": "tr-TR-EmelNeural",  // Azure TTS voice
  "avatar": null,
  "logo_overlay": {"enabled": false, "position": "bottom-right", "opacity": 0.8},
  "intro_video": {"position": "start"}  // start/end/both
}

Also add:
POST /brands/{brand_id}/logo → upload logo (light/dark variant) to R2
POST /brands/{brand_id}/intro-video → upload intro video to R2
```

### 1b. Frontend — Brand Kit sayfası

**Claude Code'a ver (frontend session'ında):**
```
Create the Brand Kit page at app/(dashboard)/marka-ayarlari/page.tsx

The page has tabs using shadcn Tabs component:
Tab 1: Marka Bilgileri
  - Brand name input
  - Description textarea
  - Website URL input + "Web sitesinden otomatik doldur" button (calls scraping API)
  - Sector select (Turkish sectors: Tekstil, Gıda, İnşaat, Turizm, 
    Perakende, Teknoloji, Sağlık, Eğitim, Finans, Hizmet, Diğer)
  - Save button

Tab 2: Marka Kimliği
  - Color picker: minimum 3 brand colors (show warning if less than 3)
  - Font selector for title and subtitle
  - Tonality select: Samimi, Profesyonel, Eğlenceli, Bilgilendirici
  - Social handle input
  - Hashtags input (tag input component)

Tab 3: Görseller
  - Logo upload (light background version) → preview
  - Logo upload (dark background version) → preview
  - Logo overlay toggle + position selector (4 quadrants)
  - Intro video upload → preview player
  - Intro video position: Başında, Sonunda, Her İkisi

Tab 4: Sosyal Hesaplar
  - For each platform (Instagram, TikTok, LinkedIn, Facebook, YouTube, Twitter, Pinterest):
    - Show connection status (connected/disconnected)
    - "Hesabı Bağla" button → calls GET /social/oauth-link?platform=X → opens URL
    - Show connected account name if connected

Tab 5: Dokümanlar
  - Upload area (drag & drop) for PDF, Word, Excel, images
  - Category selector for each upload: Ürün, Hizmet, Kurumsal, Fiyat Listesi, Diğer
  - Description input
  - List of uploaded documents with delete option

All forms auto-save with debounce (1.5 seconds after last change).
Show a "Kaydedildi ✓" indicator after save.
```

---

## Adım 2: İçerik Oluşturma Wizard'ı

**Ne yapılıyor:** Kullanıcının AI ile içerik ürettiği ana ekran. Phase 2'de Image ve Carousel ile başlıyoruz.

**Claude Code session:** `~/otomaix/apps/social/frontend/`

### 2a. Backend — İçerik üretim endpoint'leri

**Claude Code'a ver (backend session'ında):**
```
Add content generation endpoints to app/routers/posts.py:

POST /posts/generate
  Request body:
  {
    "brand_id": "uuid",
    "content_type": "image",  // image or carousel
    "content_category": "product",  // product/service/corporate
    "prompt": "user's text prompt",
    "user_text": "optional fixed text to include",
    "document_ids": ["uuid"],  // optional: use these docs as context
    "aspect_ratio": "1:1",  // 1:1 / 9:16 / 4:5 / 2:3
    "platforms": ["instagram", "tiktok"]
  }
  
  Steps:
  1. Create post record in DB with status='generating'
  2. Fetch brand_kit from brands table
  3. Build enhanced prompt: combine user prompt + brand_kit colors/tonality + document content (if any)
  4. Call fal.ai service to start generation
  5. Save fal_job_id to post record
  6. Return: {"post_id": "uuid", "status": "generating"}

GET /posts?brand_id=uuid&status=X&page=1&limit=20
  Returns paginated posts list with thumbnail URLs

GET /posts/{post_id}
  Returns full post details

POST /posts/{post_id}/regenerate
  Triggers a new fal.ai generation for an existing post

Also add:
POST /ai/suggest-ideas
  Request: {"brand_id": "uuid", "content_category": "product", "count": 3}
  Uses Claude API to generate 3 content ideas based on brand_kit and sector
  Returns: {"ideas": ["idea1", "idea2", "idea3"]}
```

### 2b. Frontend — İçerik oluşturma sayfası

**Claude Code'a ver (frontend session'ında):**
```
Create content creation page at app/(dashboard)/icerik-olustur/page.tsx

Step 1 — İçerik Tipi Seçimi:
  Grid of content type cards (for Phase 2, show 5 types):
  - Görsel (Image) — active
  - Carousel — active  
  - Video (Faceless) — "Yakında" badge, disabled
  - Özel Gün — "Yakında" badge, disabled
  - Alıntı (Quote) — "Yakında" badge, disabled
  
  Below the grid: content category tabs
  - Ürün Tanıtımı / Hizmet Tanıtımı / Firma Tanıtımı

Step 2 — İçerik Detayları (shown after type is selected):
  - Prompt textarea: "İçeriğinizi açıklayın..."
  - "Bana fikir öner" button → calls POST /ai/suggest-ideas → shows 3 clickable ideas
  - Optional: "Doküman kullan" toggle → shows document selector from brand docs
  - Optional: "Kendi metnini ekle" toggle → shows textarea for fixed text
  - Aspect ratio selector: platform icons as visual guide (1:1=Instagram, 9:16=Reels, etc.)
  - Platform multi-select checkboxes

Step 3 — Üretim ve Önizleme:
  - "İçerik Üret" button → POST /posts/generate
  - While generating: animated loading state ("İçeriğiniz üretiliyor...")
  - After generation: show produced image/carousel
  - Caption editor (Tiptap) — AI-generated caption, user can edit
  - Hashtag display — from brand_kit, user can add/remove
  - Action buttons: "Takvime Ekle", "Şimdi Yayınla", "Yeniden Üret"

Use React state machine for the 3-step flow (not URL-based routing).
Show a step indicator at the top.
```

---

## Adım 3: Content Library

**Ne yapılıyor:** Üretilen tüm içeriklerin görüntülendiği kütüphane sayfası.

**Claude Code session:** `~/otomaix/apps/social/frontend/`

**Claude Code'a ver:**
```
Create Content Library page at app/(dashboard)/icerik-kutuphanesi/page.tsx

Layout:
- Top bar: Tab filters (Tümü / Görsel / Video / Carousel) + Filter button
- Main: 3-column masonry grid of content cards

Content Card component (components/content/ContentCard.tsx):
- Thumbnail image (aspect ratio preserved)
- Status badge: Taslak/Üretiliyor/Hazır/Zamanlandı/Yayınlandı/Başarısız
- Platform icons row (which platforms it was published to)
- Hover state: shows action bar (İndir / Yayınla / Zamanla / Daha Fazla)
- Click: opens detail modal/sheet

Infinite scroll:
- Use IntersectionObserver on a sentinel div at the bottom
- Load next page when sentinel is visible
- Call GET /posts?brand_id=X&page=N&limit=20

Filter Sheet (shadcn Sheet from right, 400px wide):
- Date range picker
- Content type multi-select
- Status multi-select
- Platform filter

Status color system:
- Taslak: gray
- Üretiliyor: blue (animated pulse)
- Hazır: green
- Zamanlandı: blue
- Yayınlandı: emerald
- Başarısız: red

Also implement a "Freemium Watermark" overlay for free plan users:
- Semi-transparent Otomaix watermark on generated images
- "Filigranı Kaldır" yellow button → upgrade CTA
```

---

## Adım 4: İçerik Takvimi

**Ne yapılıyor:** FullCalendar entegrasyonu — kullanıcı içeriklerini takvimde planlıyor.

**Claude Code session:** `~/otomaix/apps/social/frontend/`

### 4a. Backend — Takvim endpoint'leri

**Claude Code'a ver (backend session'ında):**
```
Add calendar endpoints to app/routers/posts.py:

GET /calendar/posts?brand_id=uuid&start=2026-01-01&end=2026-01-31
  Returns posts in date range with: id, title (first 30 chars of caption), 
  scheduled_at, status, thumbnail_url, platforms

PATCH /posts/{post_id}/schedule
  Request: {"scheduled_at": "2026-04-15T14:00:00Z"}
  Updates scheduled_at and status to 'scheduled'

GET /calendar/holidays?year=2026
  Returns Turkish public holidays from public_holidays table

POST /posts/{post_id}/publish-now
  Immediately publishes a post via Upload-Post.com
```

### 4b. Frontend — Takvim sayfası

**Claude Code'a ver (frontend session'ında):**
```
Create Calendar page at app/(dashboard)/takvim/page.tsx

Install: @fullcalendar/react @fullcalendar/daygrid @fullcalendar/timegrid @fullcalendar/interaction

FullCalendar configuration:
- Initial view: dayGridMonth (monthly)
- Toggle between dayGridMonth and timeGridWeek
- Locale: tr (Turkish month/day names)
- Timezone: user's brand timezone (Europe/Istanbul default)

Event display:
- Each post as a colored event dot + thumbnail preview
- Status colors:
  - Zamanlandı: #4183FF (blue)
  - Başarısız: #FF8198 (red/pink)  
  - Yayınlandı: #01D3A0 (emerald)
  - Reddedildi: #000000 (black)
  - İncelemede: #FFA500 (orange)
  - Üretiliyor: #8B5CF6 (purple, animated)

Turkish public holidays:
- Fetch from GET /calendar/holidays?year=current
- Display as background events with a subtle highlight
- Show holiday name as tooltip

Interactions:
- Click on empty future date → opens "Yeni İçerik Oluştur" sheet with that date pre-filled
- Click on past date → show "Geçmiş tarihe içerik eklenemez" toast
- Drag event to new date → PATCH /posts/{post_id}/schedule with new date
- Click on event → opens post detail modal

Event modal:
- Post thumbnail
- Caption preview
- Platform icons
- Status
- Action buttons: Şimdi Yayınla / Yeniden Zamanla / Düzenle / Sil
```

### 4c. n8n — Türkiye Takvimi Otomasyonu

**Claude Code'a ver (herhangi bir session, n8n-mcp kurulu):**
```
Create an n8n workflow called "Türkiye Takvimi Güncelleme" using the n8n MCP tool.

Workflow trigger: Schedule - runs on January 1st of each year (cron: 0 0 1 1 *)

Steps:
1. HTTP Request node: fetch Turkish public holidays from a reliable API
   (try: https://date.nager.at/api/v3/PublicHolidays/{year}/TR)
   
2. Code node: transform the response to our format
   {year, date, name_tr, name_en, category}
   Map categories: National → national, Religious → religious
   
3. Also add these manually to the data (they may not be in the API):
   - Ramazan Bayramı (dates vary yearly — fetch separately)
   - Kurban Bayramı (dates vary yearly)
   - Special commercial days: Sevgililer Günü (Feb 14), 
     Anneler Günü (2nd Sunday of May), Babalar Günü (3rd Sunday of June),
     Black Friday (4th Friday of November)

4. PostgreSQL node: upsert into social.public_holidays
   INSERT ... ON CONFLICT (year, date) DO UPDATE SET name_tr=...

5. Telegram node: send completion notification
   "✅ {year} yılı Türkiye takvimi güncellendi. {count} özel gün eklendi."

Export the workflow JSON to ~/otomaix/shared/n8n-workflows/turkey-calendar-update.json
```

---

## Adım 5: Auto Posting Wizard

**Ne yapılıyor:** Kullanıcı otomatik yayın programı kuruyor. 4 adımlı wizard.

**Claude Code session:** `~/otomaix/apps/social/frontend/`

### 5a. Backend — Auto posting endpoint'leri

**Claude Code'a ver (backend session'ında):**
```
Create auto posting configuration endpoints in app/routers/autoposting.py:

Table needed (add to migration):
CREATE TABLE social.autoposting_configs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID REFERENCES social.brands(id) ON DELETE CASCADE,
  is_enabled BOOLEAN DEFAULT false,
  frequency TEXT,  -- daily/3x_weekly/weekly
  time_slots JSONB,  -- [{"day": "monday", "time": "10:00"}, ...]
  content_types TEXT[],  -- image/video/carousel
  content_categories TEXT[],  -- product/service/corporate
  topics TEXT[],  -- user-defined content topics
  platforms TEXT[],
  telegram_approval BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

Endpoints:
GET /autoposting/config?brand_id=uuid → get current config
POST /autoposting/config → create/update config
POST /autoposting/toggle?brand_id=uuid → enable/disable
GET /autoposting/upcoming?brand_id=uuid → next 5 scheduled posts
```

### 5b. Frontend — Auto posting sayfası

**Claude Code'a ver (frontend session'ında):**
```
Create Auto Posting page at app/(dashboard)/otomatik-yayin/page.tsx

If no config exists: Show "Otomatik Yayın Kur" button → opens wizard

Wizard (4 steps, use shadcn Dialog or full-page flow):

Step 1 — Konular:
  - Title: "Ne hakkında paylaşım yapmak istiyorsunuz?"
  - Minimum 3 topic inputs (tag input style)
  - "Bana konu öner" AI button → generates 5 topic suggestions based on sector
  - Show suggested topics as clickable chips

Step 2 — Platformlar:
  - Title: "Hangi platformlarda yayınlansın?"
  - Connected platforms shown as selectable cards with platform logo
  - Unconnected platforms shown grayed out with "Bağla" link

Step 3 — Program:
  - Frequency: Günde 1 / Haftada 3 / Haftada 1
  - Time slot picker (based on frequency)
  - Content type toggles: Görsel / Carousel / Video
  - Telegram onayı toggle: "Yayından önce Telegram'dan onay al"
  - If Telegram toggle on: show bot link + instructions

Step 4 — Özet:
  - Show all configured settings
  - "Otomatik Yayını Başlat" button → POST /autoposting/config + toggle enable

Summary Dashboard (when config exists):
- Status card: Aktif/Pasif with toggle
- Frequency, time slots, platforms display
- "Bir Sonraki Otomatik Yayınlar" list (next 3-5)
- "Ayarları Düzenle" button
```

### 5c. n8n — Auto Posting Workflow

**Claude Code'a ver:**
```
Create an n8n workflow called "Auto Posting Scheduler" using n8n MCP.

Workflow trigger: Schedule - every 30 minutes

Steps:
1. PostgreSQL node: fetch all enabled autoposting configs
   SELECT ac.*, b.brand_kit, b.id as brand_id 
   FROM social.autoposting_configs ac
   JOIN social.brands b ON b.id = ac.brand_id
   WHERE ac.is_enabled = true

2. Code node: for each config, check if current time matches any time slot
   (considering timezone from brand_kit.timezone)

3. If time matches: HTTP Request to POST https://api.otomaix.com/posts/generate
   with a randomly selected topic from config.topics
   and a randomly selected content_type from config.content_types

4. If telegram_approval is true:
   Telegram node: send post preview image + caption
   "🆕 Yeni içerik hazır! Onaylıyor musunuz?\n[caption]\n\n✅ Onayla  ❌ Reddet  🔄 Yeniden Üret"
   Wait for response (use webhook or poll)
   
5. If approved (or no approval needed):
   HTTP Request to POST https://api.otomaix.com/posts/{post_id}/publish-now

6. Update post status in PostgreSQL

Export to ~/otomaix/shared/n8n-workflows/auto-posting-scheduler.json
```

---

## Adım 6: Telegram Onay Workflow'u

**Ne yapılıyor:** İçerik yayına gitmeden önce Telegram'dan onay alınıyor. Bu Otomaix'in özgün özelliklerinden biri.

**Claude Code'a ver:**
```
Create an n8n workflow called "Telegram İçerik Onay" using n8n MCP.

This workflow handles the approval flow for content before publishing.

Workflow trigger: Webhook (POST /webhook/telegram-approval-request)
Called by: auto-posting workflow and manual "Onay İste" button in UI

Input payload: {post_id, brand_id, image_url, caption, platforms, telegram_chat_id}

Steps:
1. Fetch post details from PostgreSQL

2. Telegram node: send message with inline keyboard
   Message: 
   "📱 *Yeni İçerik Onayı*\n\n{caption}\n\nPlatformlar: {platforms}\n\nOnaylıyor musunuz?"
   
   Inline keyboard buttons:
   [✅ Onayla] [❌ Reddet] [🔄 Yeniden Üret]
   Also send the post image as a photo message

3. Wait for callback (Telegram inline button response)

4. If "Onayla":
   - Update post status to 'scheduled' or publish immediately
   - Telegram: "✅ İçerik onaylandı ve yayına alınıyor."

5. If "Reddet":
   - Update post status to 'rejected'
   - Telegram: "❌ İçerik reddedildi."

6. If "Yeniden Üret":
   - Call POST /posts/{post_id}/regenerate
   - Send new preview for approval (loop back to step 2)

Export to ~/otomaix/shared/n8n-workflows/telegram-content-approval.json
```

---

## Adım 7: Onboarding Akışı

**Ne yapılıyor:** Yeni kullanıcı ilk girişte markasını kuruyor. 5-7 adımlı sadeleştirilmiş wizard.

**Claude Code session:** `~/otomaix/apps/social/frontend/`

**Claude Code'a ver:**
```
Create onboarding flow at app/(onboarding)/layout.tsx and pages.

Show onboarding if: user is authenticated but has no brand.

Steps (7 steps, full-screen wizard):

Step 1 — Hoş Geldiniz
  "Otomaix'e hoş geldiniz! Markanızı birlikte kuralım."
  "Başlayalım" button

Step 2 — Web Siteniz
  "Web sitenizi girin, gerisini biz halledelim"
  URL input + "Analiz Et" button
  Loading state: "Markanız analiz ediliyor..."
  Auto-fill: brand name, description, colors (call backend scraping service)

Step 3 — Marka Bilgileri (pre-filled from step 2, user confirms)
  - Brand name
  - Description  
  - Sector selection (Turkish sector list)

Step 4 — Kullanıcı Tipi
  Cards: Küçük İşletme / Ajans / Serbest Çalışan / Orta Ölçekli Şirket

Step 5 — Sosyal Medya Hedefleri
  "Önümüzdeki 30 günde ne yapmak istiyorsunuz?"
  Multi-select: Daha fazla takipçi / Daha fazla müşteri / Marka bilinirliği / ...

Step 6 — Platform Bağlantısı
  "Hangi platformlarda paylaşım yapıyorsunuz?"
  Show platform cards with "Bağla" buttons (Upload-Post.com OAuth)
  "Şimdilik Geç" option available

Step 7 — Hazır!
  Show 3 ready-made content previews generated from their brand info
  "İçerikleriniz Hazır! 🎉"
  "Dashboard'a Git" button

After onboarding: redirect to /dashboard
```

---

## Phase 2 Tamamlanma Kontrol Listesi

Phase 3'e geçmeden önce bunların hepsi ✅ olmalı:

- [ ] Brand Kit sayfası çalışıyor (5 sekme)
- [ ] Logo ve intro video upload ediliyor, R2'ye kaydediliyor
- [ ] Sosyal hesap bağlama (Upload-Post.com OAuth) çalışıyor
- [ ] İçerik oluşturma wizard'ı çalışıyor (Image + Carousel)
- [ ] "Bana fikir öner" AI butonu çalışıyor
- [ ] fal.ai görsel üretimi uçtan uca çalışıyor
- [ ] Content Library masonry grid ve infinite scroll çalışıyor
- [ ] İçerik takvimi (FullCalendar) çalışıyor
- [ ] Takvimde drag & drop ile zamanlama çalışıyor
- [ ] Türkiye takvimi n8n workflow'u çalışıyor, bayramlar görünüyor
- [ ] Auto Posting wizard 4 adımı tamamlanıyor
- [ ] Auto Posting n8n scheduler çalışıyor
- [ ] Telegram onay workflow'u çalışıyor
- [ ] Onboarding akışı çalışıyor
- [ ] İlk pilot müşteri test etti

---

*Tamamlandı mı? → `03-social-phase3.md` ile devam et*
