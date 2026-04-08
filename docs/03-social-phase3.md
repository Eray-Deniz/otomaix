# 03 — Social Uygulaması: Phase 3 — Gelişmiş Özellikler
> **Süre:** Ay 3–4  
> **Ön koşul:** `02-social-phase2.md` tamamlanmış ve kontrol listesi ✅  
> **Hedef:** Predis.ai'dan ayrışan özgün özellikler — Türkçe video, doküman RAG, rakip analizi, ödeme sistemi

---

## Bu Phase'de Ne Yapılıyor?

Phase 3 sonunda elimizde şunlar olacak:
- Doküman yükleme ve RAG tabanlı içerik üretimi (pgvector)
- Türkçe Faceless Video — TTS + fal.ai
- AI Avatar entegrasyonu (HeyGen veya D-ID)
- Rakip analizi modülü
- Trend analizi modülü
- Logo overlay ve intro video ekleme
- Paddle ödeme ve abonelik sistemi
- Çoklu marka yönetimi (brand switcher)

---

## Adım 1: Doküman RAG Sistemi

**Ne yapılıyor:** Kullanıcı ürün kataloğu, fiyat listesi gibi dokümanları yükliyor. İçerik üretirken AI bu dokümanları okuyarak içeriğe özel bilgileri dahil ediyor.

### 1a. Backend — Doküman işleme pipeline

**Claude Code'a ver (backend session'ında):**
```
Create a document processing service in app/services/document_processor.py

When a document is uploaded:
1. Save file to R2: brands/{brand_id}/documents/{doc_id}_{filename}.{ext}
2. Extract text content:
   - PDF: use pypdf2 or pdfminer
   - Word (.docx): use python-docx
   - Excel (.xlsx): use openpyxl
   - Images: return file URL (handled differently in generation)
3. If document text < 8000 tokens: store full text in brand_documents.raw_text column
4. If document text >= 8000 tokens: 
   - Split into chunks (512 tokens, 50 token overlap)
   - Generate embeddings using OpenAI text-embedding-3-small (or fal.ai embedding model)
   - Store chunks + embeddings in brand_document_chunks table (with pgvector)

Add this table to migration (002_document_chunks.sql):
CREATE TABLE social.brand_document_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID REFERENCES social.brand_documents(id) ON DELETE CASCADE,
  brand_id UUID REFERENCES social.brands(id) ON DELETE CASCADE,
  chunk_index INTEGER,
  content TEXT,
  embedding vector(1536),
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX ON social.brand_document_chunks USING ivfflat (embedding vector_cosine_ops);

Also add raw_text TEXT column to brand_documents table.

Add endpoints to app/routers/documents.py:
POST /documents/upload → upload + process document
GET /documents?brand_id=uuid → list documents
DELETE /documents/{doc_id} → delete document + R2 file + chunks
```

### 1b. Backend — RAG entegrasyonu: içerik üretiminde doküman kullanımı

**Claude Code'a ver (backend session'ında):**
```
Update the content generation logic in app/routers/posts.py to support document-based generation.

When post.document_ids is not empty:
1. For each document_id:
   a. If raw_text exists (small doc): include full text in prompt
   b. If chunks exist (large doc): 
      - Generate embedding of the user's prompt
      - Run vector similarity search:
        SELECT content FROM social.brand_document_chunks
        WHERE document_id = $1
        ORDER BY embedding <=> $prompt_embedding
        LIMIT 5
      - Include top 5 relevant chunks in prompt

Build the final prompt structure:
---
Sen Türk KOBİ'lerine sosyal medya içeriği üreten bir uzmansın.

Marka Bilgileri:
- İsim: {brand_name}
- Sektör: {sector}
- Ton: {tonality}
- Renkler: {colors}
- Hashtag'ler: {hashtags}

{if document_context:}
Referans Doküman İçeriği:
{document_context}
{endif}

{if user_text:}
Mutlaka kullanılacak metin:
{user_text}
{endif}

Görev: {user_prompt}

Platform: {platforms}
Boyut: {aspect_ratio}

Lütfen üret:
1. Görsel için kısa tasarım açıklaması (İngilizce, fal.ai için)
2. Caption (Türkçe, {tonality} tonda)
3. Hashtag önerileri
---

Return JSON: {"image_prompt": "...", "caption": "...", "hashtags": [...]}
```

---

## Adım 2: Türkçe Faceless Video

**Ne yapılıyor:** Kullanıcı prompt giriyor → AI Türkçe script yazıyor → TTS ile seslendirilip video üretiliyor.

### 2a. Backend — Faceless video pipeline

**Claude Code'a ver (backend session'ında):**
```
Create faceless video generation pipeline in app/services/faceless_video.py

Pipeline steps:
1. generate_script(prompt, brand_kit) → Turkish script text
   - Call Claude API with prompt + brand context
   - Generate a 30-60 second script (Turkish)
   - Return: {"script": "Türkçe metin...", "duration_estimate": 45}

2. text_to_speech(script_text, voice) → audio_url
   - Use Azure Cognitive Services TTS (or ElevenLabs as alternative)
   - Default voice: tr-TR-EmelNeural (female) or tr-TR-AhmetNeural (male)
   - Save audio to R2: brands/{brand_id}/posts/audio/{post_id}.mp3
   - Return R2 audio URL

3. generate_video_with_audio(image_prompt, audio_url, duration) → video_url
   - Use fal.ai to generate background video/images
   - Combine with audio (n8n FFmpeg or fal.ai video model)
   - Return final video URL

Add endpoint: POST /posts/generate-faceless-video
  Request: {brand_id, prompt, voice, document_ids, aspect_ratio, platforms}
  Steps: script → TTS → video → save to R2 → return post_id

Add voice options endpoint: GET /voices/turkish
  Returns: [{id: "tr-TR-EmelNeural", name: "Emel (Kadın)", preview_url: "..."}]
```

### 2b. Frontend — Faceless Video sekmesi

**Claude Code'a ver (frontend session'ında):**
```
Add Faceless Video to the content creation page.

Activate the "Video (Faceless)" card in the content type grid.

Faceless video specific step 2:
- Script editor: show AI-generated Turkish script (editable textarea)
- "Script Üret" button → calls script generation endpoint
- Voice selector: dropdown with Türkçe voice options + preview button
- Duration estimate display
- Aspect ratio selector (9:16 recommended for faceless video)

Step 3 (production):
- Show video generation progress (longer than images, show estimated time)
- After generation: video preview player
- Caption and hashtag editing same as image flow
```

---

## Adım 3: AI Avatar (UGC Video)

**Ne yapılıyor:** Kullanıcının fotoğrafından AI avatar oluşturuluyor veya hazır stok avatar seçiliyor. Video içeriklerinde bu avatar konuşuyor.

### 3a. Backend — Avatar entegrasyonu

**Claude Code'a ver (backend session'ında):**
```
Create avatar service in app/services/avatar.py

Support two modes:

Mode A: HeyGen API (primary)
1. create_avatar_from_photo(photo_url, name) → avatar_id
   - POST https://api.heygen.com/v2/photo_avatar
   - Save avatar_id to brand_kit.avatar field

2. generate_ugc_video(avatar_id, script, voice) → video_url
   - POST https://api.heygen.com/v2/video/generate
   - Uses the saved avatar with the Turkish script
   - Returns video URL (async, poll for completion)

Mode B: Stock avatar (fallback)
1. GET /avatars/stock → list available stock AI avators from HeyGen
   (HeyGen provides a library of pre-made avatars)

Add to brand_kit JSON: "avatar": {"type": "custom/stock", "avatar_id": "...", "preview_url": "..."}

Add endpoints:
POST /avatar/create → create from user photo
GET /avatar/stock → list stock avatars
POST /posts/generate-ugc → generate UGC video with avatar
```

### 3b. Frontend — Avatar kurulumu (Brand Kit Tab)

**Claude Code'a ver (frontend session'ında):**
```
Add Avatar tab to Brand Kit page.

Tab: AI Avatar
  Section 1: Kendi Avatarınız
    - "Fotoğraf Yükle" button
    - Instructions: "Yüz net görünen, düz arka planlı bir fotoğraf yükleyin"
    - After upload: "Avatar Oluştur" button → loading → avatar preview
    - Once created: show avatar preview + "Bu Avatarı Kullan" button

  Section 2: Hazır Avatarlar
    - Grid of stock avatar thumbnails (from GET /avatar/stock)
    - Click to select + preview
    
  Active avatar display:
    - Show currently selected avatar
    - "Avatar ile Video Oluştur" quick action button
```

---

## Adım 4: Rakip Analizi Modülü

**Ne yapılıyor:** Kullanıcı rakip sosyal medya hesaplarını ekliyor, sistem analiz raporu üretiyor.

### 4a. Backend — Rakip analizi

**Claude Code'a ver (backend session'ında):**
```
Create competitor analysis module.

Add tables (migration 003_competitor_analysis.sql):
CREATE TABLE social.competitor_analyses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_id UUID REFERENCES social.brands(id) ON DELETE CASCADE,
  competitor_name TEXT NOT NULL,
  instagram_handle TEXT,
  tiktok_handle TEXT,
  website_url TEXT,
  last_analyzed_at TIMESTAMPTZ,
  analysis_data JSONB,  -- stores the full analysis result
  created_at TIMESTAMPTZ DEFAULT now()
);

Create app/services/competitor_analyzer.py:

1. analyze_instagram(handle) → analysis_data
   - Use a third-party Instagram scraping API (e.g., Apify, RapidAPI Instagram)
   - Fetch: posting frequency, engagement rate, content types, top hashtags, 
     best performing posts, posting times
   - Return structured analysis JSON

2. analyze_website(url) → website_analysis
   - Use httpx to fetch the page
   - Extract: meta description, key services, pricing hints, content themes
   - Use Claude API to summarize competitor's positioning

3. generate_competitor_report(analyses) → report
   - Use Claude API to synthesize findings
   - Output: competitor strengths, gaps to exploit, content opportunities

Add endpoints:
POST /competitors → add new competitor + trigger analysis
GET /competitors?brand_id=uuid → list competitors with last analysis
GET /competitors/{id}/analysis → full analysis data
POST /competitors/{id}/refresh → re-run analysis
POST /competitors/{id}/create-post → generate post inspired by competitor analysis
```

### 4b. Frontend — Rakip analizi sayfası

**Claude Code'a ver (frontend session'ında):**
```
Create Competitor Analysis page at app/(dashboard)/rakip-analizi/page.tsx

Gating: if no social account connected → show lock screen
  "Bu özelliği kullanmak için en az bir sosyal medya hesabı bağlamanız gerekiyor"
  "Hesap Bağla" button

Main page:
  - "Rakip Ekle" button → modal: name, Instagram handle, TikTok handle, website URL
  - List of added competitors (cards)
  - Each card: competitor name, logo (fetched), "Analizi Gör" button, "Yenile" button

Analysis detail page:
  - Posting frequency chart (recharts BarChart - posts per week)
  - Engagement rate display
  - Content type breakdown (pie chart)
  - Top hashtags word cloud
  - Best posting times heatmap
  - "Bu Analizden İçerik Üret" button → pre-fills content creation wizard
  
Also show: "Haftalık Rakip Raporu" - summary of changes since last week
```

### 4c. n8n — Haftalık Rakip Raporu

**Claude Code'a ver:**
```
Create n8n workflow "Haftalık Rakip Raporu" using n8n MCP.

Trigger: Schedule - every Monday at 09:00 (Europe/Istanbul)

Steps:
1. PostgreSQL: fetch all competitor_analyses where last_analyzed_at < 7 days ago
2. For each competitor: call POST /competitors/{id}/refresh
3. After all refreshes: generate summary report via Claude API
4. Email report to brand account owner
5. Telegram notification: "📊 Haftalık rakip raporu hazır. App'te görüntüleyin."

Export to ~/otomaix/shared/n8n-workflows/weekly-competitor-report.json
```

---

## Adım 5: Trend Analizi Modülü

**Ne yapılıyor:** Kullanıcının sektörüne göre Türkiye'deki güncel trendler takip ediliyor.

**Claude Code'a ver (backend session'ında):**
```
Create trend analysis service in app/services/trend_analyzer.py

Data sources:
1. Google Trends (via pytrends library)
   - Fetch trending topics for user's sector keywords
   - Region: TR, timeframe: last 7 days

2. Twitter/X trending topics for Turkey
   - Use Twitter API v2 (WOEID for Turkey: 23424969)

3. Turkish news RSS feeds
   - Fetch and parse: hurriyet.com.tr/rss, milliyet.com.tr/rss
   - Filter by sector relevance using keyword matching

Process:
- Combine all sources, deduplicate
- Use Claude API to rank relevance for the user's sector
- Generate "Bu hafta sektörünüzde trend: [topic]" summaries

Add table:
CREATE TABLE social.trend_cache (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sector TEXT NOT NULL,
  trends JSONB,
  fetched_at TIMESTAMPTZ DEFAULT now()
);

Endpoints:
GET /trends?brand_id=uuid → get current trends for brand's sector
POST /trends/{trend_id}/create-post → create post based on this trend
```

**Claude Code'a ver (frontend session'ında):**
```
Add Trend Analysis section to Dashboard page.

Add a "Bu Hafta Sektörünüzde Trendler" card widget to the dashboard.

Shows:
- Top 5 trending topics for the brand's sector
- Each topic: trend name + "İçerik Üret" quick action button
- "Tüm Trendleri Gör" link → full trends page

Create full trends page at app/(dashboard)/trendler/page.tsx:
- Weekly trend cards with engagement potential indicator
- Filter by: Tümü / Sosyal Medya / Haberler / Google
- "Bu Trende Göre İçerik Üret" button on each card
- "Trend Ayarları" → add custom keywords to track
```

---

## Adım 6: Logo Overlay ve Intro Video İşleme

**Ne yapılıyor:** AI ürettiği görsele marka logosu ekleniyor, videolara intro/outro ekleniyor.

### 6a. Backend — Görsel işleme

**Claude Code'a ver (backend session'ında):**
```
Create image/video processing service in app/services/media_processor.py

1. add_logo_overlay(image_url, logo_url, position, opacity) → processed_image_url
   - Download image from R2
   - Download logo from R2
   - Use Pillow library to composite logo onto image
   - Position options: top-left, top-right, bottom-left, bottom-right
   - Apply opacity (0.0 to 1.0)
   - Upload result to R2: brands/{brand_id}/posts/generated/{post_id}_watermarked.jpg
   - Return new URL

2. add_intro_video(main_video_url, intro_url, position) → merged_video_url
   - Download both videos from R2
   - Use FFmpeg (subprocess) to concatenate:
     - "start": intro + main video
     - "end": main video + intro (as outro)
     - "both": intro + main video + intro
   - Upload result to R2: brands/{brand_id}/posts/generated/{post_id}_final.mp4
   
Update post generation flow:
After fal.ai callback:
1. Copy file to R2 (already done)
2. If brand_kit.logo_overlay.enabled: apply logo overlay
3. If content_type is video AND brand_kit.intro_video: add intro video
4. Save final URL to posts.output_url
```

---

## Adım 7: Paddle Ödeme Entegrasyonu

**Ne yapılıyor:** Abonelik sistemi kurulumu. Kullanıcılar plan seçiyor, ödeme yapıyor.

### 7a. Backend — Paddle webhook ve abonelik

**Claude Code'a ver (backend session'ında):**
```
Implement Paddle subscription management.

Add tables (migration 004_subscriptions.sql):
CREATE TABLE social.subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID REFERENCES social.accounts(id),
  paddle_subscription_id TEXT UNIQUE,
  paddle_customer_id TEXT,
  plan_id TEXT,  -- starter/pro/business/agency
  status TEXT,   -- active/cancelled/past_due/trialing
  current_period_end TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

Plan limits table:
CREATE TABLE social.plan_limits (
  plan_id TEXT PRIMARY KEY,
  max_brands INTEGER,
  max_posts_per_month INTEGER,
  max_storage_gb INTEGER,
  can_use_video BOOLEAN DEFAULT false,
  can_use_avatar BOOLEAN DEFAULT false
);

INSERT INTO social.plan_limits VALUES
  ('starter', 1, 50, 1, false, false),
  ('pro', 3, 200, 5, true, false),
  ('business', 10, NULL, 20, true, true),
  ('agency', NULL, NULL, 50, true, true);

Endpoints in app/routers/billing.py:
POST /billing/checkout → create Paddle checkout session (return checkout URL)
POST /webhooks/paddle → handle Paddle webhooks
  - subscription.created → update subscription in DB
  - subscription.updated → update plan/status
  - subscription.cancelled → mark as cancelled
GET /billing/current → current subscription info + usage stats

Create a plan_check middleware:
- Before content generation: check if account is within plan limits
- If limit reached: return HTTP 402 with {"error": "plan_limit_reached", "upgrade_url": "..."}
```

### 7b. Frontend — Ödeme sayfaları

**Claude Code'a ver (frontend session'ında):**
```
Create pricing and billing pages.

Pricing page at app/(dashboard)/fiyatlandirma/page.tsx:
- 4 plan cards side by side:
  Starter (₺499/ay): 1 marka, 50 içerik, 2 platform
  Pro (₺999/ay): 3 marka, 200 içerik, 5 platform, Video
  Business (₺2,499/ay): 10 marka, Sınırsız, 10 platform, Video + Avatar
  Agency (₺4,999/ay): Sınırsız marka, Sınırsız, Sınırsız
- Current plan highlighted
- "Planı Seç" button → calls POST /billing/checkout → redirect to Paddle

Billing page at app/(dashboard)/faturalandirma/page.tsx:
- Current plan + renewal date
- Usage stats: Bu ay kullanılan / limit
- "Plan Yükselt" button
- Invoice history (from Paddle)

Upgrade prompts (shown when plan limit hit):
- Modal: "Bu özellik Pro planında mevcut"
- "Planı Yükselt" CTA button
```

---

## Adım 8: Çoklu Marka Yönetimi (Brand Switcher)

**Ne yapılıyor:** Kullanıcı birden fazla marka yönetebiliyor. Sidebar'da marka değiştirilebiliyor.

**Claude Code'a ver (frontend session'ında):**
```
Implement multi-brand switching in the sidebar.

Update Sidebar.tsx:
- Top section: Brand selector dropdown (shadcn Popover)
- Shows: current brand name + logo
- Dropdown: list all brands in current workspace
- "+ Yeni Marka Ekle" option at bottom of dropdown (if within plan limit)
- Click brand → setCurrentBrand in Zustand → reload page data

Update Zustand store:
- Add brands: Brand[] to store
- Add switchBrand(brandId) action → updates currentBrand, fetches new data

Add brand management page at app/(dashboard)/markalar/page.tsx:
- Grid of brand cards
- Each card: logo, name, connected platforms count, posts this month
- "Düzenle" → brand kit page for that brand
- "Sil" → confirmation modal (soft delete)
- "Yeni Marka Ekle" button (check plan limit first)

URL pattern: all dashboard pages should read currentBrand from Zustand store
(not from URL params, for simplicity at this phase)
```

---

## Phase 3 Tamamlanma Kontrol Listesi

Phase 4'e geçmeden önce bunların hepsi ✅ olmalı:

- [ ] Doküman yükleme çalışıyor (PDF, Word, Excel)
- [ ] Küçük dokümanlar direkt prompt'a ekleniyor
- [ ] Büyük dokümanlar chunklara bölünüp pgvector'a kaydediliyor
- [ ] RAG tabanlı içerik üretimi çalışıyor
- [ ] Faceless video pipeline çalışıyor (script → TTS → video)
- [ ] Türkçe TTS sesi çalışıyor
- [ ] HeyGen/D-ID avatar entegrasyonu çalışıyor
- [ ] Rakip ekleme ve analiz çalışıyor
- [ ] Haftalık rakip raporu n8n workflow'u çalışıyor
- [ ] Trend analizi dashboard widget'ı çalışıyor
- [ ] Logo overlay görsellere ekleniyor
- [ ] Intro video birleştirme FFmpeg ile çalışıyor
- [ ] Paddle checkout akışı çalışıyor
- [ ] Paddle webhook'ları aboneliği güncelliyor
- [ ] Plan limiti aşılınca upgrade prompt gösteriliyor
- [ ] Çoklu marka switcher çalışıyor

---

*Tamamlandı mı? → `04-social-phase4.md` ile devam et*
