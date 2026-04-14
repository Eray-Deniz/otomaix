# Social Backend — CLAUDE.md

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
REDIS_URL=redis://localhost:6379
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
