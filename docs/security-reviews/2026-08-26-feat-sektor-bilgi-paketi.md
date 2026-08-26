# Security Review (dual): sektör bilgi paketi Plan 1 runtime çekirdeği — 2026-08-26

> **SONRADAN DÜZELTİLDİ — bu raporu okurken ÖNCE oku.** Aşağıdaki **S3 bir bulgu DEĞİLDİR**;
> premisi çürütüldü (Eray, 2026-08-26). Paket metni müşteriden gizli değildir: paket üretimi
> besler ve müşteri çıkan post'u görüp onaylar. Müşteriden gizli olan **ham araştırma katmanı**
> (K-139: "yalnız operatör/yönetici okur") ve yönetici işlemleridir. K-16'nın "API'den
> okunabilirlik: müşteriye KAPALI" hükmü, müşteriye paket listeleyen bir UÇ olup olmadığını
> karara bağlar — "paketten türeyen hiçbir metin müşteriye ulaşmaz" demez.
> **Kök neden bu raporun kendisindedir:** gizlilik iddiası, orkestratörün iki hakeme verdiği
> ORTAK BAĞLAM metnine doğrulanmadan yazıldı; iki hakem de onu sorgulamak yerine ona karşı
> doğrulama yaptı. Bu yüzden S3'ün `[single-source]`/`[both-agree]` sinyali GEÇERSİZDİR —
> ortak-mod artefaktıdır. Düzeltmesi `15692c1` ile geri alındı, dosyalar bayt-bayt eski hâlinde.
> Kapanış turunun S3 soyundan gelen bulguları (N3 · N4 · N5) aynı sebeple düşer.
> Ayrıntı: bu belgenin sonundaki "Attempt-2 (kapanış turu)" bölümü.

coverage_mode: `diff`
- Review aralığı: `REVIEW_BASE_SHA..HEAD_SHA`
- BASE_REF: `main` | BASE_SHA: `5a9d5d4` | HEAD_SHA: `7a2a180` | REVIEW_BASE_SHA (merge-base): `5a9d5d4`
- Kapsam: 113 commit, 82 dosya, +23.264 / −338
- **Taban seçimi (sapma beyanı):** komutun varsayılanı `origin/main`'dir; o ref bu depoda yerel
  `main`'in **2 commit gerisinde**. Taban `main` seçildi — aksi hâlde bu dala ait olmayan iki commit
  kapsama girerdi. Aynı taban `/review-claude-codex`'in 2026-08-26 raporunda da kullanıldı (simetri).

Reviewers: fresh Claude subagent (`general-purpose`) + Codex `adversarial-review --base main`
dual-review: **true** (claude_status: ran; codex_status: ran)
codex_breadth: full-diff
review_confidence: full
coverage_gap: **false** (82 in-scope dosyanın hepsi ham hâliyle incelenebilirdi)
Scan substrate: pinned worktree @ `7a2a180` (temiz, detached); untracked files: not reviewed
Secret exclusion: **none** (kapsamda sır-taşıyan dosya yolu bulunmadı — filename-pattern taraması, 82 dosya)
secret-exposure-risk-accepted: false
Main tree at review: **clean** (0 uncommitted dosya)

## Ledger

- `review_target_id`: `security-review:feat-sektor-bilgi-paketi:5a9d5d4220d0a58db84dc23f274199491d91216b`
- `ledger_locator`: `task:sektor-bilgi-paketi`
- `pinned_contract_hash` (TAM 7-alan): `0f9a7629fc2fa17dd8fbd212492902ce7f1b495b2ac681cf07f6d72ac7b93fbe`
- `completed_evaluations`: 2 · `total_invocations`: 2 · `consecutive_degraded`: 0
- attempt-1 (dual) + attempt-2 closure (dual) — ikisi de koştu. Ayrıntı: belgenin sonundaki
  "Attempt-2 (kapanış turu)" bölümü. (Bu satır attempt-1 yazılırken "closure koşulmadı" diyordu;
  fix'ler AYNI oturumda indiği için P5 tetiği ateşlendi ve tur koşuldu.)

## Sözleşme sapmaları (beyan)

1. **480s → 1200s tekrar.** Codex'in ilk çağrısı `timeout 480s` altında `rc=124` verdi. Protokol
   burada "120s liveness-probe, companion sağlamsa 1200s ile BİR tekrar" ister. **Sentetik probe
   koşulmadı**; yerine ilk çağrının ham log'u kanıt olarak kullanıldı: companion thread'i açtı,
   28 alt-komut koşturdu, kesilme anına kadar hepsi `exit 0` döndü. Bu, probe'un ayırt etmek
   istediği "asılma vs uzun koşum" sorusunu doğrudan cevaplar. İkinci çağrı **byte-identical**
   prompt'la 1200s altında `rc=0` verdi. Sapma `$CODEX_LOG`'a da yazıldı.
2. **Codex bağımsızlığı — kirlenme riski (beyan).** Codex, orkestratör vermeden **kendi
   inisiyatifiyle** `docs/active/CURRENT.md` ve `docs/active/sektor-bilgi-paketi/TASK.md`'yi okudu
   (her iki çağrıda da; ölçüldü — ham log'un ilk komutları). Bu dosyalar bilinen-sorun listesi
   taşıyor. Sonuç: **F5 (kesilemeyen senkron sağlayıcı çağrısı) o listede zaten park edilmiş bir
   maddedir** ve Codex'in bulgusu bağımsız keşif olmayabilir. Diğer bulgular o listede yok.

## Critical

Yok.

## High

### S1 — `POST /ai/analyze-website` kimlik doğrulanmış SSRF'e açık `[both-agree]`

- **Yer:** `apps/social/backend/app/routers/ai.py:126-136`
- **Etiket:** **DEVRALINAN** — `git show 5a9d5d4:.../ai.py` ile ölçüldü, savunmasız satırlar taban
  commit'te birebir aynı. Bu dal fonksiyonu değiştirdi (yeni `db` bağımlılığı, prompt'a aday-sektör
  bloğu), yani bağımlılık kapsamı içinde; **gerileme bu dalın ürünü değil.**
- **Kök neden:** `payload.url` yalnız `http://`/`https://` ön ekiyle kabul ediliyor. Host allow-list'i,
  DNS çözümlemesi sonrası özel-IP reddi (RFC1918 · loopback · link-local `169.254.169.254`) ve port
  kısıtı YOK; üstelik `follow_redirects=True`, yani dışarıdaki bir sitenin 302'si iç ağa yönlendirebilir.
  Yanıtın ilk 8.000 karakteri modele veriliyor ve model onu `name`/`description`/`sector` olarak
  ÖZETLEYİP çağırana döndürüyor → kör SSRF değil, **özet düzeyinde içerik sızdıran** SSRF.
  Uç kimlik doğrulamalı, ama her kayıtlı kiracı çağırabilir.
- **Minimal fix:** (a) `follow_redirects=False` + en çok 2 yönlendirmeyi elle, her adımda yeniden
  doğrulayarak izle; (b) her adımda `socket.getaddrinfo` ile çözülen HER adresi
  `ipaddress.ip_address(...).is_private/is_loopback/is_link_local/is_reserved` kontrolünden geçir,
  biri bile özelse 422; (c) bağlantıyı doğrulanan IP'ye pinle (DNS-rebinding).
- **Etkilenen:** `ai.py::analyze_website`, `ai.py::AnalyzeWebsiteRequest`
- **Aynı desen:** `app/services/competitor_analyzer.py:31` (`follow_redirects=True`, URL yine
  kullanıcıdan) — gövdesi bu review'da OKUNMADI, aynı sınıfta olduğu ÇIKARIM.
  Önyüzdeki serbest URL girişleri: `marka-ayarlari/page.tsx::analyzeWebsite`, `onboarding/page.tsx`.
- **Doğrulama komutu:** `curl -s -X POST <api>/ai/analyze-website -H "Authorization: Bearer <JWT>"
  -d '{"url":"http://169.254.169.254/latest/meta-data/"}'` → 422 dışında bir yanıt açığı teyit eder;
  fix sonrası 422, `https://otomaix.com` çalışmaya devam etmeli.
- **Öneri yanlışsa risk:** IP tabanlı reddetme, iç ağdaki meşru bir müşteri sitesini (staging)
  analiz edilemez yapar.
- **Fallback:** dış çekimi çıkış-kısıtlı ayrı bir işçiye/proxy'ye taşı (iç ağa route yok).
- **evidence:** ÖLÇÜLDÜ (kod okuma + `git show` ile taban karşılaştırması). Canlı istek atılmadı.
- **evidence_confidence:** confirmed (yapı) · exploit canlıda denenmedi

### S2 — `document_ids` marka kapsamına bağlı değil → kiracılar arası RAG ifşası `[single-source: codex]`

- **Yer:** `apps/social/backend/app/services/document_processor.py:262-266`
- **Etiket:** **DEVRALINAN** — ölçüldü: `document_processor.py` bu dalda **hiç değişmedi**
  (`git diff --stat 5a9d5d4..7a2a180 --` boş) ve taban `ai.py`/`posts.py` zaten aynı çağrıyı yapıyordu.
- **Kök neden:** `get_document_context` sorguyu `WHERE id IN ($1,...)` ile kuruyor; **`brand_id`
  filtresi YOK**. Çağıranlar `assert_brand_owned(db, user, payload.brand_id)` ile *markanın*
  sahipliğini doğruluyor ama `payload.document_ids`'i doğrulamadan bu sorguya geçiriyor. Başka bir
  kiracının doküman UUID'sini bilen kimliği doğrulanmış bir kullanıcı, o dokümanın `raw_text`'ini
  kendi üretim isteğinin bağlamına enjekte edip modelden geri okutabilir. **UUID entropisi yetki değildir.**
  `get_product_document_context` (satır 318-337) aynı sınıfta: `WHERE product_id IN (...)`, marka filtresi yok.
- **Minimal fix:** `get_document_context`'e doğrulanmış `brand_id`'yi zorunlu parametre yap;
  `WHERE id = ANY($1) AND brand_id = $2` ile filtrele; dönen küme istenen kümeden farklıysa **tüm
  isteği 404 ile reddet** (fail-closed). Ürün yardımcısı sahip olunan ürün/marka üzerinden JOIN'lesin.
- **Etkilenen:** `document_processor.py::get_document_context`, `::get_product_document_context`;
  çağıranlar `ai.py::suggest_ideas:428`, `posts.py:115`, `posts.py:301`, `posts.py:305`,
  `posts.py:936`, `posts.py:1053`
- **Doğru örnek (aynı depoda):** `app/routers/documents.py:79-99` `brand_id` filtresini doğru kuruyor.
- **Doğrulama komutu:** iki kiracı + bir işaret dokümanı kur, sonra
  `cd apps/social/backend && .venv/bin/python -m pytest -q tests/ -k 'foreign_document or rag_ownership'`;
  404 beklenir, Anthropic çağrısı 0, işaret metni yakalanan prompt'ta bulunmamalı. **Bu test bugün YOK.**
- **Öneri yanlışsa risk:** geçerli+geçersiz karışık ID listesini reddetmek, bayat seçim taşıyan
  istemcileri kırabilir.
- **Fallback:** ham doküman-ID girdisini sunucu üretimi marka-kapsamlı seçim jetonuyla değiştir;
  ya da izolasyonu veritabanı (RLS) sınırında zorla.
- **evidence:** ÖLÇÜLDÜ — sorgu gövdesi okundu, çağıranların sahiplik kapıları okundu, dalın
  dosyaya dokunmadığı `git diff` ile doğrulandı.
- **evidence_confidence:** confirmed
- **Not:** Bu bulgu tek hakemden geldi (Codex). Orkestratör (Claude) yukarıdaki ölçümle **teyit etti**
  → Auto-Fix Policy'ye göre `fix-required`, `needs_human` değil.

### S3 — Kullanıcı metni, paket içeriğini modelden geri çektirebilir (K-16 sözleşmesinin yan kanalı) `[single-source: codex]`

- **Yer:** `apps/social/backend/app/core/prompt_builder.py:51-57` (`_SYSTEM_RULES`) +
  `apps/social/backend/app/core/caption_generator.py:145-173`
- **Etiket:** **BU DALIN ÜRÜNÜ.** Paket metnini prompt'a koyan da, K-16 gizlilik kuralını yazan da
  bu dal.
- **Kök neden — üç yapı taşı da ölçüldü:**
  1. Sistem prompt'u açıkça diyor ki: *"⚠️ KULLANICI İSTEĞİ HER ZAMAN ÖNCELİKLİDİR: … şablon
     varsayılanlarını, **sektör rehberini** ve priority sıralamasını GEÇERSİZ KILAR."*
     (`prompt_builder.py:51-57` — okundu.)
  2. Paket metni (`brand_context`) ile kullanıcının serbest metni (`dynamic_content` içindeki
     `user_prompt`) **AYNI `role: "user"` mesajının** iki bloğu (`caption_generator.py:145-173` —
     okundu). Veri/talimat sınırı yok.
  3. Ne prompt'ta bir gizlilik kuralı, ne de çıktıda paket ifadelerini eleyen bir filtre var
     (`grep -niE "gizli|confidential|reveal|ifşa" prompt_builder.py caption_generator.py
     sector_packages.py` → yalnız ilgisiz iki ürün-spec guardrail'i döndü).
- **Neden güvenlik bulgusu:** spec §3.7/K-16 (Eray, 2026-08-23) diyor ki *"marka paketi yalnız
  **üretim çıktısı üzerinden dolaylı** tüketir; API'den okunabilirlik: iç kullanım + yönetici,
  **müşteriye KAPALI**."* API yüzeyi bu kuralı uyguluyor; **prompt yüzeyi aynı kuralın kapatılmamış
  yan kanalı.** Kiracı sınırı AŞILMIYOR (müşteri kendi sektörünün paketini görür) — sızan şey
  Otomaix'in kendi tescilli içeriğidir.
- **Minimal fix:** gizliliği prompt cümlesine yükleme. (a) Paket bloğunu `role: "user"` yerine
  sistem/geliştirici katmanına taşı ve kullanıcı metnini açıkça *güvenilmeyen veri* olarak işaretle;
  (b) sistem kuralına "sektör rehberinin metnini asla tekrarlama/kodlama/listeleme" maddesi ekle;
  (c) üretim sonrası paket-özgü işaret ifadeleri için çıktı kontrolü koy; (d) caption ve fikir
  yüzeylerinin ikisine de düşman çıkarma testi yaz.
- **Etkilenen:** `prompt_builder.py::_SYSTEM_RULES`/`build_brand_context`/`build_dynamic_content`,
  `caption_generator.py::generate_captions`, `sector_packages.py::render_package_block`,
  `ai.py::suggest_ideas` (aynı birleştirme)
- **Doğrulama komutu:** işaret ifadeli bir paket + çıkarma prompt'uyla
  `cd apps/social/backend && .venv/bin/python -m pytest -q tests/prompt_regression/ -k 'confidential or exfiltration'`;
  yakalanan yanıtlarda işaret ifadesi görünmemeli. **Bu test bugün YOK.**
- **Öneri yanlışsa risk:** agresif sözcük filtresi meşru sektör dilini sansürler; ayrıca
  prompt-tabanlı savunma **olasılıksaldır**, kesin değil.
- **Fallback:** tescilli paket metnini kullanıcı-etkili LLM bağlamına HİÇ koyma — paketi önce
  sunucu tarafı seçicilere ya da hassas olmayan türetilmiş bir söz dağarcığına çevir.
- **evidence:** yapı **ÖLÇÜLDÜ** (üç taş da kod okumasıyla doğrulandı) · **sömürülebilirlik
  ÇIKARIM** — modelin gerçekten uyup uymadığı canlı model çağrısı gerektirir, bu review'da
  koşulmadı (salt-okunur + kredi harcamamak).
- **evidence_confidence:** yapı confirmed · exploit **partial** (doğrulanmadı)

## Medium

### S4 — İki ücretli uçta hız sınırı yok; yeni kardeş ucun yorumu bunun tersini iddia ediyor `[single-source: claude]`

- **Yer:** `ai.py:115` (`/analyze-website`) ve `ai.py:589` (`/generate-script`) — ikisinde de
  `dependencies` YOK. Karşılaştırma: bu dalın eklediği `ai.py:210` `limiter(20, 3600)` taşıyor ve
  yorumu *"20/saat — kardeş uçlarla aynı ev kuralı"* diyor.
- **Ölçüm (taze):** `grep -n -A6 '@router\.post' app/routers/ai.py` → dört uçtan yalnız 207 ve 368
  satırındakiler `limiter(` taşıyor; 115 ve 589 çıplak. **Yani "kardeş uçlarla aynı ev kuralı"
  iddiası yanlış — kardeşin kuralı yok.**
- **Etiket:** uçların limitersizliği **devralınan**; yanlış iddia eden yorum **bu dalın ürünü**.
- **Kök neden:** `/ai/analyze-website` her çağrıda (a) dış HTTP çekimi, (b) bir Anthropic
  `messages.create`, (c) bu daldan sonra bir DB sorgusu yapıyor; hiçbiri kota altında değil.
  Kimlik doğrulama maliyet koruması DEĞİLDİR.
- **Minimal fix:** iki uca da `dependencies=[Depends(limiter(20, 3600))]`; ayrıca
  `AnalyzeWebsiteRequest.url` için `Field(max_length=2048)`. Yanlış yorumu düzelt ya da kardeşi hizala.
- **evidence:** ÖLÇÜLDÜ (yukarıdaki grep, taze koşum) · **evidence_confidence:** confirmed

### S5 — Hız sınırı Redis kesintisinde fail-open; ücretli çağrı ayrıca kesilemiyor `[single-source: codex]`

- **Yer:** `apps/social/backend/app/core/rate_limit.py:63-66`
- **Ölçüm:** `except Exception: pass  # Redis unavailable → fail-open, don't block the request`
  (satır 64-66, okundu). Yani limiter eklemek bile Redis düşükken koruma vermez; **maliyet koruması
  tamamen Redis'in ayakta olmasına bağlı.**
- **Etiket:** **devralınan** (dosya bu dalda değişmedi); bu dalın yeni ücretli ucu (`suggest_sub_sector`)
  o fail-open limiter'ın arkasına konuyor.
- **Kök neden:** dayanıklı bir hesap kotası, IP limiti ya da sağlayıcı-eşzamanlılık sınırı yok;
  tek kapı availability'ye duyarlı bir Redis sayacı.
- **Minimal fix:** ücretli üretim için kesinti hâlinde **fail-closed** (ya da katı yerel acil bütçe);
  süreç-içi küçük bir token-bucket + sert eşzamanlılık tavanı.
- **Codex'in ikinci yarısı (kesilemeyen senkron sağlayıcı çağrısı):** bu, `CURRENT.md`'de
  `sync-provider-calls-not-cancellable` olarak **zaten park edilmiş** bir maddedir ve Codex o dosyayı
  okudu → bağımsız keşif sayılmaz (yukarıdaki kirlenme beyanı). Yeni bir ev açılmaz; mevcut evine gider.
- **evidence:** ÖLÇÜLDÜ (fail-open satırı) · **evidence_confidence:** confirmed

## Low

### S6 — Paket içeriğinin ham metni olay kaydına → n8n → Telegram'a taşınıyor `[single-source: claude]`

- **Yer:** `sector_packages.py:263/272/280` (`{text!r}` hata metnine ham gömülüyor) →
  `sector_packages.py:656` (`detail={"first_problem": problems[0][:200]}`) →
  `package_events.py::_notify_admin` → `admin_events.payload.detail` →
  `shared/n8n-workflows/sector-package-admin-events.json` (`Detay: ${detay}`) → Telegram.
- **Etiket:** **BU DALIN ÜRÜNÜ ve kendi yazdığı sözleşmeyi deliyor.**
  `033_package_events.sql:14` diyor ki *"Paket İÇERİĞİ buraya basılmaz; olay kaydı bir kopya
  deposu değildir"*; `package_events.py:113` aynı cümleyi tekrar ediyor. Uygulamada TUTMUYOR.
- **Kök neden:** `_validate_detail` pozitif bir sözleşme uyguluyor — "skaler ve ≤200 karakter" —
  ve bunu bilinçli olarak içerik yüklemi kurmuyor. `first_problem` tam da 200 karakterlik bir
  skaler metin olduğu için kapıdan geçiyor; içindeki paket prozası kapıya görünmüyor.
- **Minimal fix:** ham metin yerine **sınıfı** taşı —
  `detail={"reason": "structural", "problem_count": len(problems), "first_problem_class": problems[0].split(":", 1)[0][:80]}`.
  Tam metin zaten `logger.warning` ile operatörün log'unda duruyor; kaybolan teşhis yok.
- **evidence:** ÖLÇÜLDÜ (hakem A repro koşturdu; orkestratör üç ayağı da kod okumasıyla doğruladı:
  `{text!r}` gömme, `first_problem` kesme, n8n `Detay:` satırı) · **evidence_confidence:** confirmed

### S7 — `X-Internal-Key` karşılaştırması sabit-zamanlı değil `[single-source: claude]`

- **Yer:** `apps/social/backend/app/core/security.py:122` (`if x_internal_key != settings.INTERNAL_API_KEY:`)
- **Etiket:** **DEVRALINAN** — ölçüldü: `security.py` bu dalda değişmedi. Dal yalnız yeni bir ucu
  (`POST /internal/admin-events/dispatch-pending`, `internal.py:350`) bu kapının arkasına ekliyor.
- **İyi haber (ölçüldü):** anahtar tanımsızsa kapı **fail-closed** (503, `security.py:120-121`).
- **Minimal fix:** `hmac.compare_digest(x_internal_key or "", settings.INTERNAL_API_KEY)`
- **evidence:** ÖLÇÜLDÜ (kod + `git diff`) · **evidence_confidence:** confirmed

### S8 — Yönetici bildirimi eşiksiz: 1 kiracı isteği → 1 Telegram mesajı `[single-source: claude]`

- **Yer:** `package_events.py:59` (`ADMIN_NOTIFIED_EVENTS`), `:275`, `:324`
  (`idempotency_key=f"package_event:{event_id}"` → her olay YENİ satır)
- **Etiket:** **BU DALIN ÜRÜNÜ** (tasarım kararı K-56: "olay-bazlı, eşik YOK").
- **Kök neden:** `stale_assignment_fallback` / `mismatch_fallthrough`, kimliği doğrulanmış bir
  kiracının HER üretim isteğinde doğabilir; her olay bir outbox satırı, her satır bir Telegram
  mesajı. Üst sınır yalnız uç limitleri. Çok kiracıda operatörün bildirim kanalı boğulabilir ve
  gerçek uyarı gürültüde kaybolur.
- **Minimal fix:** pencere-bazlı tekilleştirme —
  `idempotency_key = f"package_event:{event_type}:{sector_id or brand_id}:{saat_kovası}"`
  (`ON CONFLICT DO NOTHING` zaten var). Denetim izi (`package_events`) tam kalır; kısılan yalnız bildirim.
- **Dikkat:** bu, K-56'nın ürün kararını DEĞİŞTİRİR → otonom uygulanmaz, Eray'ın kararıdır.
- **evidence:** OKUNDU (kod + n8n JSON). Canlı hacim ÖLÇÜLMEDİ; sayı iddia edilmiyor.
- **evidence_confidence:** confirmed (mekanizma) · hacim ölçülmedi

## Bulgu OLMADIĞI teyit edilen alanlar

Hakem A tarandı ve temiz buldu; rapor doldurmak için bulgu üretilmedi:

- **SQL injection:** diff'te eklenen TÜM SQL'de dize birleştirme yalnız sunucu sabitleriyle.
  `brands.py::update_brand`'in dinamik `SET` listesi pydantic alan adlarından türüyor;
  `core/utils.py::brand_kit_merge_sql` yalnız `$N` numarası enterpole ediyor. Değerlerin hepsi `$N`.
  Ölçüm: `git diff <aralık> -- 'apps/social/backend/app/**' | grep '^+' | grep -E 'f"|format\(' | grep -iE 'select|insert|update|delete'` → yalnız bu üç kalem.
- **Çok kiracılı izolasyon (bu dalın uçlarında):** dokunulan her üretim ucunda sahiplik kapısı
  yazımdan ÖNCE koşuyor — `posts.py:254/365/991`, `ai.py:383` (bu dalda EKLENDİ), `brands.py:117/203`.
  `resolve_persist_stamp` makbuzu `WHERE id=$1 AND brand_id=$2 AND consumed_at IS NULL` ile tüketiyor.
  **Ayrım:** S2 bu kapıların BAŞARISIZLIĞI değil, kapıların kapsamadığı ayrı bir parametredir.
- **İstemci→sunucu güven sınırı:** `short_video.strip_server_owned_fields` sunucu anahtarlarını
  koşulsuz ayıklıyor; `resolve_motion_prompt` serbest metni reddedip havuzdan seçiyor; legacy yol
  da `_pick_motion_prompt()`u doğrudan çağırıyor.
- **Sır yönetimi:** `N8N_ADMIN_EVENT_SECRET` fail-closed (`notifications.py:293-298` — sır boşsa
  çağrı hiç yapılmıyor); sır yalnız istek başlığında. `NEXT_PUBLIC_` ile sızan yeni değer yok.
  `scripts/sector_sweep.py` ham bağlantı dizesini basmıyor; `tests/conftest.py` parolayı `PGPASSWORD`'e koyuyor.
- **Kabuk script'i (`run-migrations.sh`):** komut enjeksiyonu yok, symlink ve symlink-zinciri reddi
  var, `ON_ERROR_STOP=1` + `--single-transaction`, dolu veritabanı kapısı fail-closed.
- **Migration'lar (032/033/034 + rollback):** `SECURITY DEFINER` fonksiyon YOK, `GRANT`/`ROLE`/`POLICY`
  değişikliği YOK; tetikleyiciler invoker haklarıyla ve şema-nitelikli. `032_down.sql` preflight'i
  veri varsa fail-closed reddediyor.
- **XSS:** frontend'de `dangerouslySetInnerHTML` / `innerHTML` / `eval(` HİÇ yok (`grep -rn`, ölçüldü).
- **n8n workflow:** webhook `authentication: headerAuth`; Code düğümlerinin JS gövdeleri
  `eval`/`Function`/dış çağrı içermiyor.
- **Alt sektör önerisinde prompt injection:** modelin çıktısı kapalı aday listesine tam-eşleşmeyle
  doğrulanıyor (`ai.py::_resolve_sub_sector_suggestion`); enjeksiyonun ulaşabileceği en kötü sonuç,
  kullanıcının KENDİ markası için geçerli-ama-farklı bir alt sektör. Zarar yüzeyi yok.

## Accepted risk (medium/low)

`autonomous_disposition_policy = ch-only-v1` gereği aşağıdakiler `accepted_risk` yazıldı
(`policy_accepted` event); fix DENENMEDİ, re-review AÇILMADI, zincir etkilenmedi:

| id | başlık | etiket |
|---|---|---|
| S4 | iki ücretli uçta hız sınırı yok + yanlış "kardeş kuralı" yorumu | devralınan uç + bu dalın yorumu |
| S5 | hız sınırı Redis kesintisinde fail-open | devralınan |
| S6 | paket ham metni olay kaydına→Telegram'a taşınıyor | **bu dalın ürünü — sözleşme ihlali** |
| S7 | `X-Internal-Key` sabit-zamanlı değil | devralınan |
| S8 | yönetici bildirimi eşiksiz | bu dalın ürünü (ürün kararı K-56) |

> **Politika sınırı, dürüstçe:** `ch-only-v1` medium/low'u otonom `accepted_risk` sayar. Bu izin
> ÖNCEDEN VAR OLAN borç içindir. **S6 bu tanıma girmiyor:** bu dalın kendi yazdığı sözleşmeyi
> (`033_package_events.sql:14`) delen, bu dalın ürettiği bir gerilemedir ve düzeltmesi tek satırdır.
> Politika onu bloke etmiyor, ama rapor onu "kabul edilmiş risk" diye gömmez — **düzeltme önerilir.**

## Unverified medium (evidence gap) — ilerleme kapısı

**none.** Hiçbir medium `evidence_confidence ∈ {partial, uncertain}` değil; ikisi de taze ölçümle
`confirmed`. D1(d) kapısı ateşlenmedi.

> S3'ün sömürülebilirlik ayağı `partial`'dır ama S3 bir **high**'dır — C/H yolundan işlenir,
> evidence-gap kapısından değil.

## Excluded secret-bearing paths (metadata-only)

none.

## Disposition Ledger

| id | source | raw sev | final sev | disposition | gerekçe |
|---|---|---|---|---|---|
| S1 | claude + codex | high / high | **high** | `open` → fix-required | both-agree; premis ölçümle doğrulandı (SSRF yapısı + taban karşılaştırması) |
| S2 | codex | high | **high** | `open` → fix-required | single-source AMA orkestratör ölçümüyle claude-confirmed → `needs_human` değil |
| S3 | codex | high | **high** | `open` → fix-required | yapı ölçüldü; sömürülebilirlik doğrulanmadı. **İndirme YAPILMADI** — raw high'ı medium'a indirmek gated `severity_downgrade` ister, onay yok → fail-closed, yüksek korunur |
| S4 | claude | medium | medium | `accepted_risk` (`policy_accepted`) | premis taze grep'le doğrulandı |
| S5 | codex | medium | medium | `accepted_risk` (`policy_accepted`) | fail-open satırı ölçüldü; kesilememe ayağı mevcut park maddesine gider |
| S6 | claude | low | low | `accepted_risk` (`policy_accepted`) | üç ayak da doğrulandı; politika dışı NOT düşüldü (bu dalın ürünü) |
| S7 | claude | low | low | `accepted_risk` (`policy_accepted`) | doğrulandı; kapı ayrıca fail-closed |
| S8 | claude | low | low | `accepted_risk` (`policy_accepted`) | mekanizma doğrulandı; ürün kararı Eray'ın |
| — | claude | — | — | `rejected` | "alt sektör öneri prompt injection" — hakem A kendi çürüttü, bulgu yazmadı (doğru) |
| — | claude | — | — | out-of-scope | `anthropic` SDK `cache_control` çağrı biçimi doğrulanamadı — güvenlik bulgusu değil, işlevsel soru işareti (`ai.py:177`, `ai.py:259`) |

## Sonuç

- Kapatılan (push-back): 0 (kullanıcı push-back'i bu raporda henüz işlenmedi)
- Açık (devam): 3 high + 5 accepted_risk
- Hakemler-arası çelişki: **none.** İki hakem çakışan bir iddiada bulunmadı; S1'de anlaştılar,
  geri kalanı ayrık keşiflerdi (Codex derinlemesine üç yapısal sınıf, Claude geniş yüzey taraması).

## Deploy/Finish Gate

- **security-risk: BLOCKED** — 0 critical / **3 high** (S1, S2, S3). Override yok.
- **dual-review: complete** — iki hakem de koştu. Override gerekmiyor.
- **coverage: full-diff** — coverage_gap yok.

**Precedence:** coverage-gap yok → security-risk ekseni devrede → dual ekseni temiz.
`/finish-branch-claude-codex` **önerilmez.** İlerleme için ya üç high düzeltilir (ardından bu
contract ile attempt-2 closure turu), ya da explicit **security-risk override** verilir
(`risk_acceptance` event; bulgular `needs_human` kalır, `fixed` OLMAZ).

## Kapsanmayan / denenmeyen

- **Canlı istek atılmadı.** SSRF'in (S1) ve paket çıkarımının (S3) gerçek sömürülebilirliği
  ölçülmedi — ikisi de yapısal kanıta dayanıyor.
- **Test çalıştırılmadı.** Bu review salt-okunur; mevcut 580 testin durumu bu oturumda yeniden
  ölçülmedi (son taze ölçüm: `/review-claude-codex`, 2026-08-26, `1e12af9`).
- **~15.000 satırlık test paketi** iki hakemde de satır satır okunmadı. `conftest.py` yıkıcı DB
  işlemleri için TAM okundu.
- **`032_sector_packages.sql`'in doğrulama bloğunun ikinci yarısı** (~satır 380-906) ve 033/034'ün
  doğrulama blokları satır satır okunmadı — salt-okunur katalog karşılaştırmaları, DDL üretmiyorlar.
- **`competitor_analyzer.py`, `webhooks.py`, `billing.py`** gövdeleri okunmadı (diff dışı); yalnız
  `get_service_auth` / `follow_redirects` açısından grep'lendi. S1'in kardeş yüzeyi olduğu ÇIKARIM.
- **`apps/crm/**`** bu diff'te hiç değişmedi.
- **Kod review'ının (2026-08-26) beş kapsama boşluğundan** bu review şunlara DEĞDİ:
  `onboarding/page.tsx` (S1 bağlamında), 034'ün DDL'i, n8n Code düğümlerinin JS gövdeleri,
  `rollback/032_down.sql` preflight'i. **Spec'in 7-17. bölümleri hâlâ hiçbir hakem tarafından
  okunmadı** — bu review'ın merceği güvenlik, spec-uyumu değil. O boşluk kapanışa taşınıyor.

**Prosedürel kapanış:** Tanımlı pas bütçesi tamamlandı (1 attempt; `total_invocations=1`,
`consecutive_degraded=0`); adlandırılmış kontroller çalıştı; ledger: `task:sektor-bilgi-paketi`
(`completed_evaluations=1`); kapsanan ve kapsanmayan alanlar yukarıda; residual'lar
`accepted_risk` tablosunda. **Exhaustiveness iddiası yok.**

## Ham kanıt — işaretçiler (bu makinede, bu kökten)

- Codex ham çıktısı: `/root/.claude/logs/otomaix--ffc87809/2026-08-26-secreview-feat-sektor-bilgi-paketi-1.md`
- Claude alt-hakem ham çıktısı: `/root/.claude/logs/otomaix--ffc87809/2026-08-26-secreview-feat-sektor-bilgi-paketi-1.claude.md`
  (secret değerleri maskeli)


---

# Attempt-2 (kapanış turu) — 2026-08-26

Üç yüksek bulgunun düzeltmeleri indikten SONRA koşuldu (P5 fix-kapanış tetiği). Dar kapsam:
sabit closure prompt'u, aynı pinli sözleşme, etki zarfı = {dokunulan dosyalar} ∪ {doğrudan
çağıranlar/çağrılanlar} ∪ {komşu testler} ∪ {dokunulan yüzeye bağlı config}.

- Kapsam: `7a2a180..b15ab6e` (13 dosya)
- Hakemler: fresh Claude subagent + Codex `adversarial-review` — **ikisi de koştu (dual)**
- `total_invocations`: 2 · `completed_evaluations`: 2 · `consecutive_degraded`: 0
- Ham kanıt: `2026-08-26-secreview-feat-sektor-bilgi-paketi-2.md` (Codex) ve `-2.claude.md` (Claude)

## Kapanış verdictleri

| Bulgu | Codex | Claude | Orkestratör ölçümü sonrası |
|---|---|---|---|
| S1 SSRF | still-open (bir adres sınıfı) | closed + iki yeni | **kapandı** (kapanışın bulduğu iki eksik düzeltildi) |
| S2 kiracı kapsamı | still-open (ürün görseli) | closed | **kapandı** (ürün görseli ayağı düzeltildi) |
| S3 paket gizliliği | still-open | still-open | **`rejected` — premis çürütüldü** (yukarıdaki banner) |

## Kapanışın bulduğu ve DÜZELTİLEN eksikler

- **Taşıyıcı-NAT aralığı (100.64.0.0/10) SSRF kapısından geçiyordu.** İki hakem de bağımsız buldu.
  Kapı yasak bayrakları TEK TEK sayıyordu; o aralık hiçbirine takılmıyor (`is_private` False,
  yalnız `is_global` False). Sayarak kurmak varyantı kapatır, sınıfı kapatmaz → pozitif
  `is_global` koşuluna geçildi. **İkinci ölçüm:** `is_global` de tek başına yetmiyor —
  `224.0.0.1` (multicast) için True döner; iki katman birlikte duruyor.
- **Bayt sınırı indirmeyi değil sonucu kesiyordu.** Gövdenin tamamı belleğe alınıp sonra
  dilimleniyordu; sınır bir bellek koruması DEĞİLDİ ve modül docstring'i sahip olmadığı bir
  kontrolü iddia ediyordu (İlke 9 ihlali, kapanış turu yakaladı). Akıtarak okumaya geçildi,
  sınırda duruluyor, yönlendirme gövdesi hiç okunmuyor.
- **S2'nin ürün görseli ayağı açıktı.** İki kısa video yolu da ürünü `WHERE id = $1` ile,
  kiracı filtresi olmadan okuyordu; üstelik doğrulanmamış ürün kimliği `posts` satırına da
  yazılıyordu. Okuma tek kapsamlı yardımcıya alındı, iki router ürün sahipliğini önden 404'lüyor.
- **[GERİ ALINDI]** Gizlilik kuralı kısa video durağan-kare çağrısına ulaşmıyordu (N4). Kural
  premisi çürütülünce bu da düştü.

## Kapanışın bulduğu, bulgu OLMAYANLAR

- **N3 · N4 · N5** — hepsi S3 soyundan (paket içeriğinin müşteriye ulaşması). Premis çürütüldü
  → `rejected`. `accepted_risk` ALMAZLAR: kabul edilecek bir risk değil, var olmayan bir bulgudur.
- **N6 (low, davranış değişikliği)** — bayat/silinmiş doküman kimliği artık üretimi 404 ile
  düşürüyor (eskiden sessizce atlanıyordu). Bu, S2 düzeltmesinin bilinçli fail-closed sonucudur:
  kısmi sonuç dönmek hangi kimliğin var olduğunu sızdırır. Hata mesajı JENERİK kalmalı.
  `accepted_risk`; müşteri yüzeyinde küçük bir UX pürüzü, evi dal kapanışı.

## Kapanış turunun teyit ettiği, gerileme OLMAYANLAR

- Paylaşılan yardımcının imza değişikliği: 6 çağıranın hepsi güncel, dışarıda çağıran yok,
  unutan çağıran `TypeError` alır (fail-closed). Test bunu pinliyor.
- Paketsiz markanın donmuş prompt'u bayt olarak DEĞİŞMEDİ (kapanış hakemi ayrıca ölçtü).
- Değiştirilen iki test hiçbir şeyi zayıflatmıyor (iki hakem de ayrı ayrı değerlendirdi);
  ikisi de S3 geri alınırken zaten eski hâline döndü.

## Kapanış SONRASI düzeltmelerin durumu — dürüst etiket

Kapanış turu `b15ab6e`'yi denetledi. Ondan sonra inen üç düzeltme (taşıyıcı-NAT · akıtarak okuma ·
ürün görseli, `c5dcc5a`) ve geri alma (`15692c1`) **bağımsız hakem GÖRMEDİ.** Ölçümleri var
(beş mutasyon kontrolü, canlı internette pozitif/negatif sonda, 625 test) ama bunlar mekanik
doğrulamadır ve bu depoda mekanik doğrulamanın bağımsız turun yerine geçmediği ölçülmüş bir
derstir. **Etiket: doğrulandı ama denetlenmedi.**

## Güncel Deploy/Finish Gate

- **security-risk: clean** — unresolved critical/high YOK. S1 ve S2 kapandı; S3 `rejected`.
- **dual-review: complete** — attempt-1 ve attempt-2'de dört hakem koşumu, degradasyon yok.
- **coverage: full-diff** — coverage_gap yok.
- **Açık kalem (kapanışta karar):** yukarıdaki "denetlenmedi" etiketi — üçüncü bir dar tur mu
  koşulacak, yoksa ölçümlerle kabul mü edilecek.
