# 06 — Social Uygulaması: Phase 6 — Trend Sistemi Yenileme
> **Süre:** ~3–4 hafta
> **Ön koşul:** Phase 1–4 tamamlanmış; Apify hesabı ve `APIFY_API_KEY` mevcut; Claude API erişimi aktif.
> **Hedef:** `/trendler` sayfasını yüzeysel RSS+pytrends mantığından çıkarıp üç katmanlı, sosyal-medya odaklı, kişiselleşmiş trend sistemine çevirmek.

---

## Bu Phase'de Ne Yapılıyor?

Mevcut `app/services/trend_analyzer.py` dosyası 3 gazete RSS'i + pytrends + sektör-bazlı 6 saatlik cache üzerine kurulu. Tüm aynı sektördeki kullanıcılar aynı 6 sonucu görüyor; pytrends 429 sonrası fallback'lara düşüyor; sosyal medya verisi (TikTok, Reddit, YouTube, Twitter, Instagram) hiç yok.

Phase 6 sonunda elimizde şunlar olacak:

- **Katman A** — her gece 06:00 Europe/Istanbul'da n8n tetiklemeli ücretsiz kaynak taraması (Google News, Google Trends, YouTube, Reddit, trends24.in, Pinterest Trends, TCMB EVDS) → sektör başına paylaşılan cache.
- **Katman B** — kullanıcı tetiklemeli, marka belgelerini (RAG) ve geçmiş postları girdi olarak alan **Serper.dev canlı Google araması + Claude Haiku sentezi** ile kişiselleştirilmiş trend araması. Aylık plana göre rate-limited.
- **Katman C** — yalnızca Pro ve üstü için **Apify** scraper'ları (TikTok Creative Center, Trendyol, Twitter trends) + Claude sentezi → R2'ye kaydedilen PDF aylık sektör raporu.
- **Hiyerarşik sektör tablosu** — `parent_sector_id` ile gelecekte alt sektör eklemek migration ile mümkün, kod değişikliği gerekmez.
- **Yenilenen `/trendler` sayfası** — üç katmanı tek arayüzde gösterir, plan-bazlı paywall ve kontör göstergesi içerir.

---

## Mimari Karar Kayıtları (ADR)

### ADR-1 — Tek ücretli scraper: Apify
**Karar:** Tüm scraping ihtiyaçları için sadece Apify kullanılacak. Bright Data, ScrapingBee, ScraperAPI vb. değerlendirildi; Apify (a) marketplace aktörleri TikTok CC dahil bizim tüm kullanım senaryolarımızı karşılıyor, (b) kullandıkça öde modeli düşük başlangıç maliyeti veriyor, (c) `APIFY_API_KEY` zaten mevcut (Phase 3 rakip analizi için eklenmişti).
**Sonuç:** `app/services/apify_client.py` tek noktada toplanır, hem rakip analizi hem trend Layer C bunu kullanır.

### ADR-2 — Serper.dev + Claude Haiku (Claude web_search yerine)
**Karar:** Layer B'de canlı Google araması **Serper.dev** üzerinden yapılır, ham sonuçlar Claude Haiku'ya sentez için verilir. Perplexity ve Claude'un yerel `web_search_20250305` aracı kullanılmaz.
**Sebep:** Claude `web_search` tetik başına ~$0.04–0.08 maliyetliydi (arama + sonuç okuma tokenleri); Anthropic fiyat değiştirirse veya arama sayısı beklenenden fazla olursa fatura 2-3x kayma riski vardı. Serper.dev $50/50.000 arama (~$0.001/arama) fiyatıyla **10x ucuz**, fatura öngörülebilir. Tavily, Brave, Perplexity alternatifleri değerlendirildi; Serper.dev ham Google sonuçlarıyla en ucuzu.
**Tazelik:** Serper.dev canlı Google araması — Claude web_search ile aynı canlılık penceresi (tetik anı). Layer A'nın 06:00 cache'inin ötesine geçer, öğleden sonra çıkan gelişmeleri görür.
**Dezavantaj:** Ek bir vendor (SERPER_API_KEY), ama API çok basit — tek HTTP call, SDK bile gerekmez.
**İleri iterasyon:** İlk 3 ay telemetri sonrası kullanıcılar Layer A cache'ini zaten yeterli buluyorsa (Layer B sonuçlarının Layer A'ya kıyasla ek değeri düşükse), "saf Claude, arama yok" moduna geçiş değerlendirilebilir — maliyet sıfıra yakın düşer.
**Sonuç:** `app/services/trends/serper_client.py` wrapper + `layer_b.py` içinde `search → synthesize` iki adım akış.

### ADR-3 — Kullanıcı tetiklemeli + nightly hibrit
**Karar:** Saf nightly (tüm kullanıcılara aynı veri) ve saf user-triggered (her tetik para harcar) yerine ikisini birleştir.
**Sebep:** Nightly free kaynaklar sıfır maliyetle her sabah dolu bir trend sayfası garanti eder; kullanıcı tetikli Serper.dev + Claude maliyeti yalnızca aktif kullanıcı için ödenir. Yeni piyasaya çıkış için minimum maliyet — maksimum değer.

### ADR-4 — Layer B aylık limit (5/10/20/50)
**Karar:** Starter 5 / Pro 10 / Business 20 / Agency 50 trend tetik / ay.
**Sebep:** Serper.dev'le tetik başı maliyet ~$0.005 (Serper ~$0.003 + Haiku ~$0.002) olduğu için 100 kullanıcılık maliyet ~$5-10/ay'a düşer. Limitler konservatif tutulur — yüksek talep gelirse kolayca yukarı çekilebilir, fatura riski düşük.
**Reset:** Takvim ayı (UTC), `accounts.id + month` üzerinden sayaç.

### ADR-5 — Layer C raporu yalnızca Pro+
**Karar:** Starter rapor üretemez (Pro'ya yükselt CTA). Pro 1 / Business 3 / Agency 10 rapor / ay.
**Sebep:** Apify maliyetli (~$0.30–0.50/rapor). Aynı zamanda net upgrade funnel mekanizması.

### ADR-6 — Sektörler hiyerarşik tablo
**Karar:** 11 sektörle başlanır ama `social.sectors` tablosu `parent_sector_id` kolonu ile hiyerarşik tasarlanır. Brands tablosu `sector` text yerine `sector_id UUID` referansı tutar (geri uyumluluk için eski text kolonu da bırakılır, dual-write).
**Sebep:** Gelecekte "e-ticaret > moda > spor giyim" gibi alt kırılımlar sadece migration ile eklenebilir; kod ve cache mantığı değişmez.

### ADR-7 — Cron 06:00 Europe/Istanbul
**Karar:** Layer A nightly cron 06:00 Istanbul (03:00 UTC).
**Sebep:** Kullanıcılar genelde 09:00'da panele girer; veri 3 saat öncesinden hazır olur. Kaynak siteler bu saatte düşük yük altında, rate limit sorunu minimum.

---

## Veritabanı Migrations

### `019_sectors_hierarchy.sql`
```sql
-- Hiyerarşik sektör tablosu
CREATE TABLE social.sectors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT UNIQUE NOT NULL,
  display_name TEXT NOT NULL,
  parent_sector_id UUID REFERENCES social.sectors(id) ON DELETE RESTRICT,
  keywords TEXT[] NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_sectors_parent ON social.sectors(parent_sector_id);
CREATE INDEX idx_sectors_slug ON social.sectors(slug);

-- 11 ana sektör seed
INSERT INTO social.sectors (slug, display_name, keywords) VALUES
  ('teknoloji',    'Teknoloji',    ARRAY['teknoloji','yazılım','yapay zeka','dijital','siber']),
  ('e-ticaret',    'E-Ticaret',    ARRAY['e-ticaret','online alışveriş','kargo','mağaza','satış']),
  ('yemek',        'Yemek & İçecek', ARRAY['restoran','yemek','mutfak','tarif','gastronomi']),
  ('saglik',       'Sağlık & Wellness', ARRAY['sağlık','hastane','ilaç','wellness','fitness']),
  ('egitim',       'Eğitim',       ARRAY['eğitim','üniversite','kurs','öğrenci','diploma']),
  ('moda',         'Moda & Stil',  ARRAY['moda','giyim','trend','stil','koleksiyon']),
  ('turizm',       'Turizm & Otelcilik', ARRAY['turizm','tatil','otel','seyahat','destinasyon']),
  ('finans',       'Finans',       ARRAY['finans','borsa','yatırım','döviz','ekonomi']),
  ('gayrimenkul',  'Gayrimenkul',  ARRAY['gayrimenkul','konut','inşaat','kira','tapu']),
  ('otomotiv',     'Otomotiv',     ARRAY['otomotiv','araç','elektrikli araç','trafik','galeri']),
  ('genel',        'Genel',        ARRAY['Türkiye','gündem','sosyal medya']);

-- Brands tablosuna sector_id kolonu (text sector kalır, geri uyumluluk)
ALTER TABLE social.brands ADD COLUMN sector_id UUID REFERENCES social.sectors(id);
CREATE INDEX idx_brands_sector_id ON social.brands(sector_id);

-- Mevcut text sector değerlerini map et
UPDATE social.brands SET sector_id = (
  SELECT id FROM social.sectors WHERE slug = lower(social.brands.sector) LIMIT 1
);
```

### `020_trend_layers.sql`
```sql
-- Layer A: Sektör paylaşımlı nightly cache
CREATE TABLE social.sector_trend_cache (
  sector_id UUID NOT NULL REFERENCES social.sectors(id) ON DELETE CASCADE,
  layer TEXT NOT NULL CHECK (layer IN ('A','C')),
  trends JSONB NOT NULL,
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  source_summary JSONB,
  PRIMARY KEY (sector_id, layer)
);

CREATE INDEX idx_sector_trend_cache_fetched ON social.sector_trend_cache(fetched_at);

-- Layer B: Marka-bazlı kişisel trend cache (kısa TTL)
CREATE TABLE social.brand_trend_cache (
  brand_id UUID PRIMARY KEY REFERENCES social.brands(id) ON DELETE CASCADE,
  trends JSONB NOT NULL,
  fetched_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  prompt_tokens INT,
  completion_tokens INT
);

-- Layer B & C kullanım sayaçları (aylık reset)
CREATE TABLE social.trend_usage (
  account_id UUID NOT NULL REFERENCES social.accounts(id) ON DELETE CASCADE,
  year_month TEXT NOT NULL, -- 'YYYY-MM'
  layer_b_count INT NOT NULL DEFAULT 0,
  layer_c_count INT NOT NULL DEFAULT 0,
  PRIMARY KEY (account_id, year_month)
);

-- Layer C raporlarının metadata + R2 path
CREATE TABLE social.sector_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id UUID NOT NULL REFERENCES social.accounts(id) ON DELETE CASCADE,
  brand_id UUID REFERENCES social.brands(id) ON DELETE SET NULL,
  sector_id UUID NOT NULL REFERENCES social.sectors(id),
  pdf_url TEXT NOT NULL,
  generated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  apify_cost_usd NUMERIC(10,4),
  claude_cost_usd NUMERIC(10,4)
);

CREATE INDEX idx_sector_reports_account ON social.sector_reports(account_id, generated_at DESC);

-- Eski tablo kalır (rollback için), yeni kod kullanmayacak
COMMENT ON TABLE social.trend_cache IS 'DEPRECATED — Phase 6 öncesi. Yeni kod sector_trend_cache ve brand_trend_cache kullanır.';
```

---

## Sprint Planı

### Sprint 1 — Şema + Sektör Modeli (2–3 gün)

**Görevler:**
1. `019_sectors_hierarchy.sql` ve `020_trend_layers.sql` migration'ları yaz, prod'a uygula.
2. `app/models/schemas.py` içine `SectorOut`, `TrendItem`, `TrendUsageOut`, `SectorReportOut` modelleri ekle.
3. `app/services/sector_resolver.py` — bir markanın `sector_id`'sini lazy-resolve eden helper (text sector → slug → id; eşleşme yoksa "genel").
4. Brands router create/update endpoint'lerinde `sector_id` dual-write (eski text alan da güncellenir).

**Çıktı:** Her markanın bir `sector_id`'si var; eski `sector` text alanı geriye uyumluluk için duruyor.

---

### Sprint 2 — Katman A: Nightly Free Sources (4–5 gün)

**Yeni dosya:** `app/services/trends/layer_a.py`

**Kaynak modülleri** (`app/services/trends/sources/`):
- `google_news.py` — `https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr` ve sektör keyword query'leri
- `google_trends.py` — pytrends `interest_over_time` + `related_queries` (TR geo); pytrends 429'larına karşı SerpApi trial fallback
- `youtube.py` — YouTube Data API v3, `videos?chart=mostPopular&regionCode=TR&videoCategoryId=...` (kategori → sektör mapping)
- `reddit.py` — `r/Turkey` + sektörel subreddit'ler, Atom RSS feed (`top.rss?t=day`)
- `trends24.py` — `https://trends24.in/turkey/` HTML scrape (Twitter/X trends, ücretsiz)
- `pinterest_trends.py` — `https://trends.pinterest.com/tr-tr/` HTML scrape (moda, yemek, hediye, ev dekor için kritik)
- `tcmb_evds.py` — `https://evds2.tcmb.gov.tr/service/evds/series=...` (USD/TL, faiz, enflasyon — finans sektörü)

**Toplam 7 Layer A kaynağı.** (Spotify ve Product Hunt 2026-04-15'te listeden kaldırıldı — Türk KOBİ sosyal medya trendleri için yeterli sinyal vermiyorlardı; maliyet/karmaşıklık mantıklı değildi.) Her kaynak kendi sektör filtresiyle çalışır (örn. Pinterest Trends yemek/moda/hediye'de devrede, finansta değil).

**Akış:**
```python
# layer_a.py
async def fetch_sector_layer_a(sector: dict) -> dict:
    """Bir sektör için tüm ücretsiz kaynakları paralel topla."""
    tasks = [
        google_news.fetch(sector["keywords"]),
        youtube.fetch_for_sector(sector["slug"]),
        reddit.fetch_for_sector(sector["slug"]),
        # ...
    ]
    raw = await asyncio.gather(*tasks, return_exceptions=True)
    consolidated = _flatten_and_dedupe(raw)
    summary = await _claude_summarize(consolidated, sector)
    return {"trends": summary, "source_summary": _source_counts(raw)}

async def run_nightly_sweep(db):
    """Tüm sektörleri tarayıp sector_trend_cache'e yaz."""
    sectors = await db.fetch("SELECT * FROM social.sectors WHERE parent_sector_id IS NULL")
    for sector in sectors:
        try:
            result = await fetch_sector_layer_a(dict(sector))
            await db.execute(
                """
                INSERT INTO social.sector_trend_cache (sector_id, layer, trends, source_summary, fetched_at)
                VALUES ($1, 'A', $2::jsonb, $3::jsonb, now())
                ON CONFLICT (sector_id, layer) DO UPDATE SET
                  trends = EXCLUDED.trends,
                  source_summary = EXCLUDED.source_summary,
                  fetched_at = now()
                """,
                sector["id"], json.dumps(result["trends"]), json.dumps(result["source_summary"]),
            )
        except Exception as e:
            sentry_sdk.capture_exception(e)
            continue
```

**Internal endpoint:** `POST /internal/trends/nightly-sweep` (X-Internal-Key korumalı) — n8n cron'u tetikler.

**n8n workflow:** `shared/n8n-workflows/trends-nightly-sweep.json`
- Cron: `0 6 * * *` Europe/Istanbul (3 UTC)
- HTTP Request → `POST https://api.otomaix.com/internal/trends/nightly-sweep`
- Hata durumunda Telegram bildirimi
- Aktif edilir

**Claude özet promptu:** Haiku 4.5, prompt cache aktif (system prompt sabit, sectors değişen kısım). Çıktı: 8 trend + her biri için `title`, `source`, `relevance_score`, `summary`, `content_opportunity`, `suggested_prompt`.

---

### Sprint 3 — Katman B: User-Triggered Personal Trends (3–4 gün)

**Yeni dosya:** `app/services/trends/layer_b.py`

**Akış:**
```python
async def fetch_personal_trends(brand_id: UUID, db) -> list[dict]:
    brand = await _load_brand_with_context(db, brand_id)
    rag_chunks = await _retrieve_brand_documents(db, brand_id, top_k=8)
    recent_posts = await _recent_posts_summary(db, brand_id, limit=10)

    # 1. Marka + RAG + geçmiş postlardan 3-5 arama sorgusu üret
    queries = _build_search_queries(brand, rag_chunks, recent_posts)

    # 2. Serper.dev ile canlı Google TR araması (paralel)
    search_tasks = [serper_client.search(q, gl="tr", hl="tr", num=10) for q in queries]
    raw_results = await asyncio.gather(*search_tasks, return_exceptions=True)
    flat_results = _flatten_and_dedupe(raw_results)

    # 3. Ham sonuçları Claude Haiku'ya sentez için ver (arama yok, sadece token)
    system = (
        "Sen Türk KOBİ'lere sosyal medya trend analizi sunan bir uzmansın. "
        "Sana verilen Google arama sonuçlarını ve marka bağlamını değerlendirerek "
        "markaya özgü 6-8 trend ve içerik fikri öner. Sadece JSON dizisi döndür."
    )
    user = _build_synthesis_prompt(brand, rag_chunks, recent_posts, flat_results)

    msg = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return _parse_trends_json(msg)
```

**`app/services/trends/serper_client.py`** — minimal wrapper:

```python
import httpx
from app.core.config import settings

async def search(query: str, gl: str = "tr", hl: str = "tr", num: int = 10) -> dict:
    """Serper.dev Google Search API — tek HTTP call."""
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": settings.SERPER_API_KEY, "Content-Type": "application/json"},
            json={"q": query, "gl": gl, "hl": hl, "num": num},
        )
        resp.raise_for_status()
        return resp.json()
```

**Tetik başı maliyet:** 3-5 Serper araması (~$0.003) + ~2000-3000 sentez tokeni (Haiku ~$0.002) = **~$0.005 / tetik**. 10 tetik = ~$0.05 / kullanıcı / ay.

**Rate limit:** `app/core/rate_limit.py:limiter` factory zaten var. Yeni `check_trend_quota(account_id, layer, db)` helper aylık sayaçtan kontrol eder ve 402 + `{error: "trend_quota_reached"}` döner.

**Plan limitleri** `billing.py:PLAN_LIMITS`'a eklenir:
```python
PLAN_LIMITS = {
    "starter":  {..., "trend_layer_b": 5,  "trend_layer_c": 0},
    "pro":      {..., "trend_layer_b": 10, "trend_layer_c": 1},
    "business": {..., "trend_layer_b": 20, "trend_layer_c": 3},
    "agency":   {..., "trend_layer_b": 50, "trend_layer_c": 10},
}
```

**Yeni endpoint:** `POST /trends/personal?brand_id=...`
- `assert_brand_owned`
- `check_trend_quota(account_id, "b", db)` → quota düşür
- `fetch_personal_trends(brand_id, db)`
- `brand_trend_cache`'e yaz, response'da döndür

---

### Sprint 4 — Katman C: Pro+ Monthly Sector Reports (4–5 gün)

**Yeni dosya:** `app/services/trends/layer_c.py` ve `app/services/apify_client.py`

**Apify aktörleri (11 adet — sektör bazında koşullu çalıştırılır):**

Genel sosyal medya (her raporda):
- `clockworks/free-tiktok-scraper` — TikTok hashtag/region popüler videolar
- `apify/instagram-scraper` — Instagram hashtag + reels trend
- `dtrungtin/twitter-trends-scraper` — Twitter Türkiye trendleri

E-ticaret (e-ticaret, moda, teknoloji sektörleri):
- `epctex/trendyol-scraper` — Trendyol kategori bestseller
- `epctex/hepsiburada-scraper` — Hepsiburada "çok satanlar"
- `epctex/n11-scraper` — N11 alt segment (community aktör, fallback)

Sektör-spesifik:
- `epctex/ciceksepeti-scraper` — özel gün/hediye sektörü
- `epctex/sahibinden-scraper` — gayrimenkul + otomotiv (kategori trend)
- `epctex/yemeksepeti-scraper` — yemek sektörü (popüler restoran/mutfak)
- `voyager/booking-scraper` — turizm (popüler destinasyon)
- `epctex/dolap-scraper` — moda 2. el (Letgo aktörü mevcut değil; Dolap tek kaynak)

**Sektör ↔ aktör routing** `layer_c.py:SECTOR_ACTOR_MAP` sabitinde:

```python
SECTOR_ACTOR_MAP = {
    "e-ticaret":   ["tiktok", "instagram", "twitter", "trendyol", "hepsiburada", "n11"],
    "moda":        ["tiktok", "instagram", "pinterest", "trendyol", "hepsiburada", "dolap"],
    "yemek":       ["tiktok", "instagram", "pinterest", "yemeksepeti"],
    "turizm":      ["tiktok", "instagram", "booking"],
    "gayrimenkul": ["twitter", "sahibinden"],
    "otomotiv":    ["tiktok", "instagram", "twitter", "sahibinden"],
    "teknoloji":   ["tiktok", "twitter", "hepsiburada", "trendyol"],
    "saglik":      ["tiktok", "instagram", "twitter"],
    "egitim":      ["tiktok", "instagram", "twitter"],
    "finans":      ["twitter"],
    "genel":       ["tiktok", "instagram", "twitter"],
}
```

Bu routing sayesinde her rapor yalnızca ilgili aktörleri çalıştırır — gereksiz Apify tüketimi önlenir. Örneğin **finans** raporu yalnızca Twitter aktörünü ($0.05) çalıştırır, **moda** raporu 6 aktörü (~$0.55).

```python
# apify_client.py
async def run_actor(actor_id: str, input_payload: dict, timeout: int = 300) -> list[dict]:
    """Apify aktörünü senkron çalıştır, dataset items döndür."""
    async with httpx.AsyncClient(timeout=timeout) as client:
        run = await client.post(
            f"https://api.apify.com/v2/acts/{actor_id}/runs?token={settings.APIFY_API_KEY}&waitForFinish={timeout}",
            json=input_payload,
        )
        dataset_id = run.json()["data"]["defaultDatasetId"]
        items = await client.get(
            f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={settings.APIFY_API_KEY}"
        )
        return items.json()
```

**PDF üretimi:** `weasyprint` (CRM ile aynı) — `app/services/pdf_renderer.py`. HTML template `templates/sector_report.html` (Jinja2). Üretilen PDF Cloudflare R2'ye `sector-reports/{account_id}/{report_id}.pdf` olarak yüklenir, `pdf_url` `assets.otomaix.com` üzerinden döner.

**Endpoint:** `POST /trends/monthly-report?brand_id=...`
- Plan kontrolü (Starter → 402 + upgrade_url)
- Quota kontrolü (`check_trend_quota("c")`)
- `BackgroundTasks.add_task(_generate_report_task, ...)` — uzun sürer, 202 döner
- `GET /trends/reports?brand_id=...` — geçmiş raporları listeler
- `GET /trends/reports/{id}` — tek rapor metadata + pdf_url

**`requirements.txt`:** `weasyprint==62.3` zaten kurulu olabilir, kontrol et.

---

### Sprint 5 — Frontend `/trendler` Yenileme (3–4 gün)

**Dosya:** `app/(dashboard)/trendler/page.tsx` (mevcut 285 satır tamamen yeniden yazılır)

**Tasarım:**
- **Üst bar:** Sektör adı + "Son güncelleme: X saat önce" (Layer A timestamp) + "Yenile" butonu (Layer A admin için) + "Bana Özel Bul" butonu (Layer B, kontör göstergeli: "5/10 kullanıldı")
- **Sekme/Tabs:** 
  - "Sektör Trendleri" (Layer A) — paylaşılan sonuçlar
  - "Bana Özel" (Layer B) — son tetikleme sonuçları
  - "Aylık Rapor" (Layer C) — Pro+ için PDF listesi + "Yeni Rapor Oluştur" butonu (Starter'da kilitli görünüm + paywall modal)
- **Trend kartları:** title, source rozeti (Google News / YouTube / Reddit / Claude / Apify), relevance bar, summary, content_opportunity, "İçerik Üret" butonu (mevcut `POST /trends/{trend_id}/create-post` benzeri endpoint'e gider — content_type seçimi modal'da).
- **Paywall modal:** Layer C'de Starter müşteri için "Pro'ya yükselt" CTA, fiyatlandırma sayfasına link.

**Yeni client component'ler:**
- `TrendQuotaBar.tsx` — kullanım/limit progress bar
- `TrendLayerTabs.tsx` — sekme yöneticisi
- `MonthlyReportList.tsx` — geçmiş raporlar tablosu, indir linkleri
- `GenerateReportButton.tsx` — Layer C tetikleyici

---

### Sprint 6 — Test, Telemetri, Canlıya Alma (2 gün)

**Görevler:**
1. PostHog event'leri: `trend_layer_a_viewed`, `trend_layer_b_triggered`, `trend_layer_c_generated`, `trend_quota_exhausted`, `trend_paywall_shown`.
2. Sentry: tüm Layer A kaynak fetcher'larında exception capture (one-source failure ≠ tüm pipeline fail).
3. Cost telemetry: `trend_usage` tablosuna her tetikte token sayıları + apify cost yazılır → `crm/raporlar` sayfasında bu ay trend maliyeti gösterilir.
4. Load test: Layer B endpoint'ine 50 eşzamanlı istek (locustfile genişletilir) → rate limit + quota davranışı doğrulanır.
5. Eski `trend_analyzer.py` deprecation: dosya silinmez ama içerik shim olarak yeni servise yönlendirilir; mevcut `GET /trends` endpoint Layer A cache'inden okur (geriye uyumluluk).
6. Coolify env: `APIFY_API_KEY` zaten var, kontrol. `YOUTUBE_API_KEY` ve `REDDIT_CLIENT_ID/SECRET` eklenecek.

---

## Endpoint Özeti

| Method | Path | Layer | Auth | Açıklama |
|--------|------|-------|------|----------|
| GET | `/trends?brand_id=` | A | JWT | Sektörün Layer A cache'i (sabah taranmış paylaşımlı veri) |
| POST | `/trends/personal?brand_id=` | B | JWT + quota | Serper.dev + Claude Haiku ile kişisel trend |
| POST | `/trends/monthly-report?brand_id=` | C | JWT + plan + quota | Apify + PDF rapor (BackgroundTasks) |
| GET | `/trends/reports?brand_id=` | C | JWT | Geçmiş raporlar listesi |
| GET | `/trends/reports/{id}` | C | JWT | Tek rapor metadata |
| GET | `/trends/usage?brand_id=` | B+C | JWT | Bu ay kullanılan / kalan kontör |
| POST | `/trends/{trend_id}/create-post` | A/B | JWT + post limit | İçerik üretimine bağla (mevcut endpoint güncellenir, content_type/aspect_ratio/platforms parametreleri zorunlu) |
| POST | `/internal/trends/nightly-sweep` | A | X-Internal-Key | n8n cron tetikleyici |

---

## Ortam Değişkenleri (yeni)

```
YOUTUBE_API_KEY=             # Layer A YouTube Data API v3
REDDIT_CLIENT_ID=            # Layer A Reddit OAuth
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=otomaix/1.0 by /u/otomaix
SERPAPI_KEY=                 # Layer A Google Trends fallback (pytrends 429 için, opsiyonel)
EVDS_API_KEY=                # Layer A TCMB EVDS (finans/insaat sektörleri)
SERPER_API_KEY=              # Layer B Serper.dev canlı Google araması ($50/50k = ~$0.001/arama)
APIFY_API_KEY=               # ZATEN VAR (Phase 3 rakip analizi)
TRENDS_LAYER_A_ENABLED=true  # kill switch
TRENDS_LAYER_C_ENABLED=true  # kill switch
```

(Pinterest Trends, trends24.in, Google News, TCMB EVDS — ek anahtar gerektirmez, HTML/RSS scrape veya public endpoint.)

---

## Sektör ↔ Kaynak Eşleşme Tablosu

Her sektörün hangi Layer A ve Layer C kaynaklarından beslendiği:

| Sektör | Layer A (ücretsiz, her gün) | Layer C (Apify, aylık rapor) |
|--------|------------------------------|-------------------------------|
| Teknoloji | Google News, Google Trends, YouTube, Reddit, trends24 | TikTok, Twitter, Hepsiburada, Trendyol |
| E-ticaret | Google News, Google Trends, YouTube, Reddit, trends24 | TikTok, Instagram, Twitter, Trendyol, Hepsiburada, N11 |
| Yemek | Google News, YouTube, Reddit, Pinterest Trends, trends24 | TikTok, Instagram, Pinterest (scrape), Yemeksepeti |
| Sağlık | Google News, YouTube, Reddit, trends24 | TikTok, Instagram, Twitter |
| Eğitim | Google News, YouTube, Reddit, trends24 | TikTok, Instagram, Twitter |
| Moda | Google News, Google Trends, YouTube, Pinterest Trends, trends24 | TikTok, Instagram, Trendyol, Hepsiburada, Dolap |
| Turizm | Google News, YouTube, Reddit, Pinterest Trends | TikTok, Instagram, Booking |
| Finans | Google News, Reddit, TCMB EVDS, trends24 | Twitter |
| Gayrimenkul | Google News, TCMB EVDS, trends24 | Twitter, Sahibinden |
| Otomotiv | Google News, YouTube, Reddit, trends24 | TikTok, Instagram, Twitter, Sahibinden |
| Genel | Google News, YouTube, Reddit, trends24 | TikTok, Instagram, Twitter |

Routing mantığı `layer_a.py:SECTOR_SOURCE_MAP` ve `layer_c.py:SECTOR_ACTOR_MAP` sabitlerinde tutulur. Kaynak ekleme/çıkarma sadece bu iki dict'i düzenlemeyi gerektirir.

---

## Maliyet Tahmini (Operasyon)

Katman B Serper.dev + Haiku'ya geçince tetik başı maliyet $0.04-0.08 → ~$0.005'e düştü (**~10x ucuz**). Katman C ise aktör sayısı arttığı için $0.25 → ~$0.55 / rapor seviyesine çıktı (her rapor ortalama 4–6 aktör çalıştırır).

| Ölçek | Layer A (sabit) | Layer B (Serper+Haiku) | Layer C (Apify) | Toplam / Ay |
|-------|-----------------|-------------------------|------------------|-------------|
| 100 kullanıcı | ~$5 | ~$5 | ~$80 | **~$90** |
| 500 kullanıcı | ~$5 | ~$25 | ~$220 | **~$250** |
| 2000 kullanıcı | ~$5 | ~$100 | ~$680 | **~$785** |

Layer B artık **toplam maliyetin en küçük kalemi**. Maliyetlerin ~%85'i Apify'a (Layer C sektör raporları), ~%10'u Claude Haiku'ya, ~%5'i Serper.dev'e gider. Layer A ücretsiz kaynaklardan beslendiği için sıfıra yakındır.

---

## Kontrol Listesi

- [x] Migration 019 + 020 prod'da çalıştırıldı (Sprint 1)
- [x] `social.sectors` 11 satır seed'lendi (Sprint 1)
- [x] Brands tablosu `sector_id` migration'la map edildi (Sprint 1)
- [x] Layer A 7 kaynak modülü yazıldı (Google News, Google Trends, YouTube, Reddit, trends24, Pinterest Trends, TCMB EVDS) (Sprint 2)
- [x] `POST /internal/trends/nightly-sweep` çalışır, n8n workflow aktif (Sprint 2)
- [x] Layer B `POST /trends/personal` + quota guard (Sprint 3)
- [x] Layer C Apify aktörleri entegre edildi + `SECTOR_ACTOR_MAP` routing (Sprint 4)
- [x] Layer C `POST /trends/monthly-report` + Apify + PDF + R2 upload (Sprint 4)
- [x] `GET /trends/reports` + `GET /trends/reports/{id}` endpoint'leri (Sprint 4)
- [x] Frontend `/trendler` üç sekmeli yeni tasarım (Sprint 5)
- [x] Paywall: Backend 402 → toast + `/fiyatlandirma` yönlendirmesi (Sprint 5, UpgradeModal yerine toast tercih edildi)
- [x] Frontend error handling fix: `plan_limit` objesi kontrolüne geçildi (2026-04-16)
- [x] PostHog event'leri eklendi (Sprint 6) — `analytics.ts`'e 5 yeni helper: `trendLayerAViewed`, `trendLayerBTriggered`, `trendLayerCGenerated`, `trendQuotaExhausted`, `trendPaywallShown`
- [x] Sentry tekil kaynak hataları — `layer_a.py:_run_source()` içine `sentry_sdk.capture_exception(e)` eklendi
- [x] CRM raporlar sayfasında trend maliyet kolonu (Sprint 6) — `social.trend_usage` sorgusu + 4 MetricCard + toplam maliyet
- [x] Eski `trend_analyzer.py` deprecation yorumu (Sprint 6) — dosya başına DEPRECATED docstring eklendi
- [x] Load test Layer B senaryosu (Sprint 6) — `locustfile.py`'a `POST /trends/personal` eklendi (weight=1, 402 success)
- [x] Frontend error handling fix — `plan_limit` objesi kontrolüne geçildi, ölü `plan_locked` dalı kaldırıldı
- [ ] Coolify env değişkenleri (YOUTUBE_API_KEY, EVDS_API_KEY, SERPER_API_KEY) eklendi (Sprint 6)
- [ ] Canlı smoke: her katmandan 1 başarılı çağrı log'lanmış (Sprint 6)

---

## Bir Sonraki Adım

Phase 6 planı kullanıcı tarafından onaylandıktan sonra **Sprint 1 — Migration ve sektör modeli** ile başla. Implementation öncesi kullanıcının "henüz mimari teknik döküm çıkarma birkaç sorum daha var" notu gereği ek soruları beklenecek; sorular yanıtlandıktan sonra bu doküman güncellenir, ardından kodlama başlar.
