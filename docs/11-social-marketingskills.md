# Phase 11 — Marketing Skills Prompt Entegrasyonu ✅ TAMAMLANDI (2026-04-24)

**Doküman sürümü:** v2.0 (tamamlandı)
**Kapsam:** Otomaix Social `/icerik-olustur` — Claude prompt'larına 4 yüksek öncelikli marketing skill entegrasyonu
**Hedef dosya konumu:** `~/otomaix/docs/11-social-marketingskills.md`
**Hazırlayan:** Claude (Anthropic) — `/root/marketingskills/skills/` altındaki SKILL.md dosyalarının analizi + mevcut `prompt_builder.py` ve `templates_data.py` yapısı baz alınarak
**Gerçekleşen süre:** 2 gün (2026-04-23 — 2026-04-24)

### Tamamlanma Özeti

| Sprint | İçerik | Commit | Durum |
|--------|--------|--------|-------|
| Sprint 1 | Hook + Copywriting + Platform ton → Tier 1 | `e3aedca` | ✅ |
| Sprint 1 hotfix | SOMUTLUK/YASAK sıkılaştırma (4 iterasyon) | `481f662`→`e46a351` | ✅ |
| Sprint 1 polish | Model Opus 4.6, hook kaldırma, LinkedIn medium | `ab3572e` | ✅ |
| Sprint 2 | Psikoloji prensipleri (5→3) → Tier 1 | `eaaf47d`, `32979b8`, `702377a` | ✅ |
| Sprint 3 | 7 görsel açı → genel-gorsel-sablon guidance | `d7296db` | ✅ |

**Plandan sapmalar:**
- **Model:** claude-opus-4-7 → claude-opus-4-6 (4.6 talimat izlemede daha disiplinli, fabrication riski düşük)
- **HOOK KURALI kaldırıldı:** Zorunlu 4 kategori Claude'u formülsel açılışlara sıkıştırıyordu
- **LinkedIn:** long → medium (200-500 kelime gereksiz uzundu)
- **JTBD prensibi kaldırıldı:** Bilgi yokken "hangi işi çözdüğünü yaz" talimatı fabrication'a yol açtı ("doğrudan üreticiden sunuyoruz" uydurması)
- **HYPERBOLIC DISCOUNTING kaldırıldı:** "hemen/bu hafta" anlık fayda vurgusu kargo/iade/garanti süresi uydurmasına yol açtı
- **Kalan psikoloji prensipleri:** 3 (Somutluk, Loss Aversion, Social Proof)

---

## 0. Session Başlangıç Talimatı (Claude Code için)

**DİKKAT:** Phase 11 üzerinde çalışmaya başlamadan önce bu bölümü tamamen uygula. Atla YOK.

### Zorunlu okuma sırası

Her Claude Code session'ının başında şu dosyaları **SIRAYLA** oku:

1. `~/otomaix/docs/00-platform-mimari.md` — Platform genel mimarisi
2. `~/otomaix/docs/marketingskills.md` — Skills analiz raporu (yüksek/orta/düşük öncelik ayrımı)
3. `~/otomaix/docs/11-social-marketingskills.md` — **Bu doküman, baştan sona**
4. `~/otomaix/apps/social/backend/CLAUDE.md` — Backend son durum changelog'u
5. `~/otomaix/apps/social/frontend/CLAUDE.md` — Frontend son durum changelog'u

Skill kaynak dosyaları (sadece gerekince spot okuma — referans için):
- `/root/marketingskills/skills/social-content/SKILL.md` — hook formülleri, platform stratejisi
- `/root/marketingskills/skills/copywriting/SKILL.md` — yazım kuralları, CTA formülü
- `/root/marketingskills/skills/marketing-psychology/SKILL.md` — psikoloji prensipleri
- `/root/marketingskills/skills/ad-creative/SKILL.md` — 7 görsel açı kategorisi

### Durum tespiti ve raporlama

Dosyaları okuduktan sonra kullanıcıya şu formatta rapor ver:

```
Son durum: Phase 11 Sprint X
Tamamlanan: <somut maddelerle — CLAUDE.md girdilerinden>
Sonraki iş: <bir sonraki sprint veya yarım kalan adım>

Onay verirseniz devam edeceğim.
```

**Onay almadan kod yazma.** Kullanıcı "devam" veya eşdeğer onay verene kadar bekle.

### Çalışma kuralları (her session'da geçerli)

`feedback_calisma_kurallari.md` memory girdisindeki 6 zorunlu kural + `feedback_concise_responses.md` (tekrar yok) bu phase'de de geçerli.

Ek kural — bu phase'e özel:

- **İngilizce → Türkçe çevirisi mekanik olmayacak.** Skill dosyaları İngilizce; Tier 1'e eklerken kelime kelime çevirme, doğal Türkçe karşılıkları elle yaz. Detay: §3.2.
- **Her sprint sonrası canlı A/B gözlem.** Eski prompt ile üretilmiş son 2-3 post'u örnek al, yeni prompt'la aynı girdilerle yeniden üretip Claude çıktısını kıyasla. Somut fark yoksa sprint sonuçsuz kabul edilir — deploy'a geçilmez.

---

## 1. Kapsam ve Strateji

### 1.1 Problem Tanımı

Mevcut `_SYSTEM_RULES` (Tier 1) ~20 satır, ~200 token. İçeriği: dil kuralı, kullanıcı isteği öncelik, uydurma yasağı, JSON format talimatı. **İçerik stratejisi yok.** Claude'a "ton + format" söyleniyor, "nasıl yazılacak" söylenmiyor. Sonuç:

- **Hook tutarsız** — her caption farklı bir stil/girişle başlıyor, "scroll durdurma" gücü düşük
- **Özellik saydırma** — "SporXL rahat tabanlıdır, kaliteli malzemedendir" tipi cümle sık çıkıyor (fayda dili değil)
- **Soyut iddialar** — "kalite", "premium", "modern", "inovatif" gibi belirsiz sözler kontrolsüz kullanılıyor
- **Platform tonları benzeşik** — PLATFORM_DEFAULTS `captionStyle: short/medium/long` + hashtag sayısı verir; üslup/yapı farkı yok (LinkedIn ile Twitter aynı tonda kısa/uzun)
- **Görsel açısı tek tip** — `genel-gorsel-sablon` + Tier 3'teki image_prompt kuralları Claude'u `Professional product photography, clean studio background` formülüne itiyor → her içerik aynı stüdyo estetiği

Ayrıca Tier 1 şu an ~200 token olduğu için Anthropic'in minimum cache eşiğinin (Opus için ~1024 token) altında kalıyor — **cache_control bayrağı set edilmiş ama cache'lenmiyor.** Bu da ek bir kazanım alanı.

### 1.2 Seçilen Strateji: B Yolu — Prompt Entegrasyonu

`marketingskills.md` analizinde iki yol belirlenmişti:

- **A — Geliştirici tarafı:** `~/.claude/skills/` kurulum, Claude Code Otomaix'in kendi pazarlama/geliştirme kararları için kullanır.
- **B — Kullanıcı tarafı:** Skill içerikleri `prompt_builder.py` ve `templates_data.py`'a gömülür, Otomaix kullanıcılarının ürettiği içeriklerin kalitesi artar.

Phase 11 **yalnızca B yolu**. A yolu (CRO, SEO, Satış skill'leri) ayrı bir iş, bu phase kapsamında değil.

### 1.3 Kapsanan Skill'ler

| Skill | Kategori | Hedef dosya | Tier |
|-------|----------|-------------|------|
| **social-content** | İçerik | `prompt_builder.py` `_SYSTEM_RULES` | Tier 1 |
| **copywriting** | Kopya | `prompt_builder.py` `_SYSTEM_RULES` | Tier 1 |
| **marketing-psychology** | Strateji | `prompt_builder.py` `_SYSTEM_RULES` (seçme prensipler) | Tier 1 |
| **ad-creative** | Görsel | `templates_data.py` → `genel-gorsel-sablon.prompt.guidance` | Tier 2 |

### 1.4 Kapsam Dışı — YAPILMAYACAKLAR

| İş | Neden | Yönlendirme |
|----|-------|-------------|
| marketing-ideas skill'i `/ai/suggest-ideas`'a entegrasyon | Orta öncelik, `marketingskills.md`'de referans olarak tutulmuş | Phase 12 veya ileriki sprint |
| copy-editing self-review adımı Tier 3'e | Ek Claude çağrısı maliyeti + latency, ROI belirsiz | Veri bazlı karar için canlı test sonrası değerlendir |
| customer-research → marka onboarding | UX değişikliği gerekiyor, scope farklı | Ayrı UI phase'i |
| launch-strategy → yeni "Lansman" şablonu | Yeni template + form field tasarımı gerekiyor | Phase 9 desenli ayrı sprint |
| A yolu — Claude Code skill kurulumu | Otomaix geliştirme workflow'u, kullanıcı içeriği değil | Kullanıcı ayrı istediğinde |

### 1.5 Bozulmayacak Mevcut Akışlar

- **Tier 2 `build_brand_context`** — marka adı, renkler (HEX zorunluluk), sektör guidance, şablon guidance, disclaimer — dokunulmuyor (yalnızca `genel-gorsel-sablon` şablonunun kendi guidance'ı değişiyor, bu Tier 2'nin şablon bloğuna gider)
- **Tier 3 `build_dynamic_content`** — kullanıcı isteği, ürün bağlamı, yapısal veriler, RAG, öncelik sırası, platform talimatı — hiç dokunulmuyor
- **`_build_output_format_instruction` (caption_generator.py)** — JSON şeması + image_prompt 6 katı kural — hiç dokunulmuyor
- **PLATFORM_DEFAULTS** — 9 platform × captionStyle/maxHashtags/useFirstComment — dokunulmuyor (Sprint 2'de ton eklentisi bu yapının üstüne Tier 1'den gelecek, override değil)
- **`/ai/suggest-ideas`** — Phase 11 kapsamında değil
- **`/ai/analyze-website`, `/ai/generate-script`** — hiç dokunulmaz
- **Diğer şablonlar** (şu an devre dışı; `eticaret-urun-karti`, sağlık/hukuk/emlak şablonları vb.) — `guidance` metinleri dokunulmaz, yalnızca aktif olan `genel-gorsel-sablon` Sprint 3'te güncellenir

### 1.6 Ölçüm Stratejisi

**Bu phase'de KPI hedefi koymuyoruz.** Engagement/CTR metriği henüz Otomaix'te ölçülmüyor (analytics event'leri var ama backend agrege dashboard yok). Ölçüm:

- **Kalitatif:** Her sprint sonrası kullanıcı aynı input'larla (ör. MyGoodShoes + SporXL 79 TL) eski ve yeni prompt çıktısını yan yana karşılaştırır. Somut fark görünüyorsa sprint kabul.
- **Prompt caching metriği:** Sprint 1 sonrası Tier 1 boyu ~1500 token'a çıkacak, Anthropic cache eşiğini aşacak → `cache_read_input_tokens` > 0 görünmeli (şu an muhtemelen 0 veya düşük). Sentry/log ile doğrulanır.

---

## 2. Mimari Kararlar

### 2.1 Değişiklik Noktası — Tier Haritası

| İçerik | Mevcut | Yeni (Phase 11) | Etki |
|--------|--------|-----------------|------|
| Dil kuralı | Tier 1 | Tier 1 (değişmiyor) | — |
| Kullanıcı isteği öncelik | Tier 1 | Tier 1 (değişmiyor) | — |
| Uydurma yasağı | Tier 1 | Tier 1 (değişmiyor) | — |
| JSON format | Tier 1 | Tier 1 (değişmiyor) | — |
| **Hook formülleri (4 kategori)** | YOK | Tier 1 (yeni) | Sprint 1 |
| **Copywriting yazım kuralları** | YOK | Tier 1 (yeni) | Sprint 1 |
| **Platform ton stratejisi** | YOK (yalnızca `captionStyle` uzunluk) | Tier 1 (yeni) | Sprint 1 |
| **Psikoloji prensipleri (4-5 seçme)** | YOK | Tier 1 (yeni) | Sprint 2 |
| **7 görsel açı kategorisi** | YOK | Tier 2 — `genel-gorsel-sablon.guidance` | Sprint 3 |
| Marka renkleri + HEX zorunluluk | Tier 2 | Tier 2 (değişmiyor) | — |
| Disclaimer otomasyonu | Tier 2 | Tier 2 (değişmiyor) | — |
| image_prompt 6 katı kural | `_build_output_format_instruction` | (değişmiyor) | — |

### 2.2 Cache Davranışı

**Sprint 1 sonrası tek seferlik global invalidation:** Tier 1 `_SYSTEM_RULES` değişince tüm markaların cache'i invalidate olur. İlk çağrı cache miss (write cost 1.25x), sonrakiler cache hit (read cost 0.1x). Beklenen davranış, riski yok.

**Tier 1 token bütçesi:**
- Şu an: ~200 token (cache eşiği altında, cache'lenmiyor)
- Sprint 1 sonrası: ~1050 token (hook + copywriting + platform ton)
- Sprint 2 sonrası: ~1550 token (+ psikoloji prensipleri ve uygulama kuralı)
- Tamamı cache'in üst eşiği dahilinde

**Tier 2 `genel-gorsel-sablon.guidance`:**
- Sprint 3 öncesi: ~350 token (mevcut görsel yönergesi + caption formülü + CTA kuralı)
- Sprint 3 sonrası: ~650 token (+7 görsel açı kategorisi + seçme talimatı)
- Tier 2 zaten marka bilgileri + sektör guidance ile birlikte genelde 1500-3000 token, bu artış kritik değil

### 2.3 Tekrar Riski (önceki faz dersi)

Tier 3'teki `_build_output_format_instruction` zaten "marka adı yasak, ürün adı yasak, Türkçe metin yasak, logo yasak" diyor. Sprint 3'te `genel-gorsel-sablon.guidance`'a 7 açı eklerken bu kuralları tekrar yazma — yalnızca açı seçimi ve her açının sahne/kompozisyon karşılığını ekle. Overlap kontrolü Sprint 3 planında.

### 2.4 Çeviri Stratejisi

Skill dosyaları İngilizce. "Çeviri" işi tek seferliktir ve **kod yazma anında** (bu planı Tier 1'e eklerken) yapılır — **runtime'da hiçbir çeviri olmaz**.

**Akışın dil haritası — Runtime:**
| Katman | Dil |
|--------|-----|
| Kullanıcının "Tasarım ve içerik için istekleriniz" input'u | Türkçe |
| Tier 1 (`_SYSTEM_RULES`) | Türkçe (bu planla yazılacak) |
| Tier 2 (`build_brand_context` — marka + sektör + şablon guidance) | Türkçe (mevcut) |
| Tier 3 (`build_dynamic_content` — yapısal veriler, RAG) | Türkçe (mevcut) |
| Claude yanıtı: caption, hashtag | Türkçe |
| Claude yanıtı: image_prompt | İngilizce (fal.ai modeli için — mevcut davranış) |

Hiçbir yerde "çevir" talimatı yok. Akış baştan sona Türkçe.

**Kod yazma anındaki çeviri disiplini:**

Skill dosyalarındaki İngilizce formülleri Tier 1'e koyarken iki yol var:

**❌ Yanlış yol — Claude'a çeviri bırakmak:**
```
Hook formülleri:
- "Unpopular opinion: [X]"
- "Hot take: [X]"
Bunları Türkçeye çevirip kullan.
```
Bu yaklaşımda Claude her çağrıda farklı çeviri üretir ("Popüler olmayan bir fikir", "Sıcak görüş" gibi kulağa yapay gelen karşılıklar). Tutarsız ve robotik.

**✅ Doğru yol — Tier 1'e elle oturtulmuş Türkçe kalıplar:**
```
Hook — Aykırı kategori, Türkçe kalıplar:
- "Açık konuşayım: [yaygın görüşe ters iddia]"
- "Kimsenin söylemediği şu: ..."
- "[Popüler tavsiye] yanlış. Sebebi şu: ..."
```
Tier 1 doğal Türkçe ile yazılır. Claude çeviri yapmaz, doğrudan kullanır.

**Üç çeviri riski (bu plan yazılırken dikkat edilecek):**

1. **Motamot çeviri yapay** — "Unpopular opinion: X" → "Popüler olmayan bir fikir: X" (robotik). Karşılık: "Açık konuşayım: X".
2. **Kültürel ton farkı** — ABD marketing'i agresif/özgüvenli, TR KOBİ izleyicisinde aynı ton kibirli durabilir. "Crush your competition" → "rakipleri ez" değil, "farkı ortaya koy".
3. **Cümle yapısı/ritim** — İngilizce verb-first punch Türkçede SOV yapısıyla kaybolur. "Stop doing X" → "X yapmayı bırak" düşük enerji. Türkçenin kendi hook kalıpları kullanılır: soru ile başlat, şaşırtıcı rakam, doğrudan hitap.

Tüm bu kararlar **bu planı uygulayan sprint'lerde kod yazılırken** verilir — runtime kararı değil.

### 2.5 Esneklik — Kategori Bazlı Formül, Kopya Değil

Hook ve görsel açı formülleri Claude'a "kategori + mantık" olarak verilir, "kelime kelime kopyala" olarak değil. Örnek:

**Yanlış yaklaşım (robotikleşir):**
> "Aşağıdaki 4 formülden birini AYNEN kullan: 1) 'X hakkında yanılmışım...' 2) 'Popüler olmayan fikir: ...'"

**Doğru yaklaşım (esin menüsü):**
> "Caption'ın ilk cümlesi 4 hook kategorisinden birine uymalı: Merak / Hikaye / Fayda / Aykırı. Her kategoride Türkçe örnek kalıplar aşağıda — **kelime kelime kopyalama**, markanın tonuna ve doğal Türkçeye uygun kendi cümleni kur."

---

## 3. Skill-to-Prompt Mapping

### 3.1 social-content → Tier 1 (Sprint 1)

**Kaynak:** `/root/marketingskills/skills/social-content/SKILL.md`

**Alınacak:**
- **Hook formülleri** [ref:social-content — Hook Formulas] (4 kategori × 2-3 Türkçe örnek kalıp): Merak (curiosity), Hikaye (story), Fayda (value), Aykırı (contrarian)
- **Platform ton rehberi** [ref:social-content — Platform Quick Reference + references/platforms.md] (9 platform için üslup/yapı farkı — `captionStyle` uzunluk/hashtag sayısı PLATFORM_DEFAULTS'ta zaten var, bu ton katmanıdır). Not: Skill 5 platform kapsıyor; YouTube, Threads, Pinterest, Bluesky kendi eklememiz.

**Alınmayacak:**
- "Content pillars framework", "Weekly planning template", "Engagement strategy" — bunlar kullanıcı kendi içerik stratejisi için lazım, AI prompt'a yazmak anlamsız
- "Analytics & optimization", "Reverse engineering viral content" — kapsam dışı

**Eklenecek Tier 1 bloğu (taslak — §4.2'de tam metni):**

```
📣 CAPTION HOOK (ilk cümle) — 4 kategoriden birine uymalı
Merak | Hikaye | Fayda | Aykırı
Kategorileri esin menüsü olarak kullan, örnek kalıpları kelime kelime kopyalama.
```

### 3.2 copywriting → Tier 1 (Sprint 1)

**Kaynak:** `/root/marketingskills/skills/copywriting/SKILL.md`

**Alınacak — yazım kuralları** [ref:copywriting — Core Principles + Writing Style + CTA Formula]:
- **Benefits over features** — özellik değil fayda dili
- **Specificity over vagueness** — "kalite/premium/modern" gibi soyut kelime yasağı, somut detay zorunluluğu
- **Active voice** — aktif cümle yapısı
- **Customer language** — marka/jargon dili yerine müşteri dili
- **CTA formülü** — `[Eylem] + [Ne Alacak] + [Opsiyonel ek bilgi]`

**Alınmayacak:**
- "Page Structure Framework" (Above the fold / Core sections) — landing page için, sosyal medya caption'a uymaz
- "Page-Specific Guidance" (Homepage/Landing/Pricing) — kapsam dışı
- "Honest over sensational" — zaten mevcut "YASAK: uydurma istatistik" kuralı kapsıyor

### 3.3 marketing-psychology → Tier 1 (Sprint 2)

**Kaynak:** `/root/marketingskills/skills/marketing-psychology/SKILL.md`

**Seçme — 5 prensip** [ref:marketing-psychology — Foundational + Buyers Psychology + Influencing Behavior]:

| Prensip | Neden seçildi | Caption'a etkisi |
|---------|---------------|------------------|
| **Jobs to Be Done** | Özellik → fayda geçişini destekler (copywriting'in yanında güçlendirici) | "Ürünün özelliği şu" → "Bu ürünün çözdüğü iş şu" |
| **Specificity** | Copywriting'deki "vague yasağı"nın psikolojik gerekçesi; rakam/outcome zorunluluğu | "İyi sonuç alırsın" → "İlk hafta 3 sipariş artışı" |
| **Loss Aversion** | Türk KOBİ izleyicisinde yüksek etki; scarcity/urgency motoru | "Dene" → "Kaçırma — bu ayın son 3 koltuğu" |
| **Social Proof** | Brand autorite + güven inşası; sayı/testimonial vurgusu | Sayısal sosyal kanıt (müşteri sayısı, yıldız, yıl) |
| **Hyperbolic Discounting** | Anlık fayda vurgusu; "6 ay sonra ROI" değil "bugün başla" | CTA metinlerinin zaman ufku kısalır |

**Alınmayacak (çoğu prensip):**
- **First Principles, Inversion, Occam's Razor, Pareto, Local/Global Optima** — strateji/meta-düşünme modelleri, prompt'a yazmak Claude'un kendi çıkarım sürecini şişirir, caption kalitesini artırmaz
- **AIDA, BJ Fogg, EAST, COM-B, Hick's Law** — framework'ler; prompt'ta referans vermek yerine *sonuçlarını* (tek net CTA, düşük friksyon) yazım kuralları olarak Sprint 1'de zaten eklemiş olacağız
- **Pricing psychology** — fiyatlandırma kararı kullanıcının, AI'ın değil
- **Sunk Cost, Endowment, IKEA Effect, Zero-Price, Default Effect** — pazarlama uygulaması var ama caption düzeyinde zayıf etki

**Gerekçe — sadece 4-5 prensip:** Tier 1 şişirmesin. Her prensip ~50-80 token. 5 prensip ~300-400 token; 15 prensip ~1500+ token olur ve Claude "prensip listesini tamamlama" tuzağına düşer (her prensibi caption'a tek tek sokmaya çalışır → yapay).

**Seçim mantığı (kısaltılmış B yaklaşımı):** Claude bu 5 prensibi her caption'da uygulamaz. Runtime'da `user_prompt` + `template_id` + `template_fields` girdilerine bakarak içerik türünü sınıflandırır, Tier 1'deki "PSİKOLOJİ UYGULAMA KURALI" bloğundaki 2 dallanmaya göre (satış/promosyon vs. bilgi/hikaye) prensipleri seçer. Emin değilse hiçbir prensip sokmaz — hook + copywriting kuralları tek başına yeterli. Detay: §4.2.2 prompt bloğu.

**Neden B yaklaşımı (ve neden kısaltılmış):** Claude'u tamamen serbest bırakmak (yaklaşım A) tutarsız seçime yol açar — aynı şablon + aynı marka için farklı çağrılarda farklı prensip karışımı çıkar. Uzun eşleme tablosu (tam yaklaşım B) ise Claude'u "tablo tamamlama" tuzağına iter — e-ticaret gördüğünde her posta Loss Aversion sıkıştırır, sahte scarcity riski doğar. 2 dallanma + "emin değilsen sokma" çıkışı bu iki tuzağın arasında orta yol.

### 3.4 ad-creative → Tier 2 (Sprint 3)

**Kaynak:** `/root/marketingskills/skills/ad-creative/SKILL.md`

**Alınacak** [ref:ad-creative — Define Your Angles]:

7 açı kategorisi + her açının görsel karşılığı (sahne/kompozisyon ipucu):

| # | Açı | Türkçe karşılık | Görsel sahne örneği |
|---|-----|-----------------|---------------------|
| 1 | Pain point | Sorun vurgusu | Öncesi sahne — problemi görselleştir |
| 2 | Outcome | Sonuç vurgusu | Sonrası / dönüşüm anı |
| 3 | Social proof | Sosyal kanıt | Kullanıcı grubu / topluluk / sayısal göstergeler |
| 4 | Curiosity | Merak uyandırma | Kapalı/örtük sahne, detay yakın plan |
| 5 | Urgency | Aciliyet | Zamana bağlı gösterge, sınırlı sunum sahnesi |
| 6 | Identity | Kimlik vurgusu | Hedef kitleye özel ortam (örn. ofis çalışanı, yoga stüdyosu) |
| 7 | Contrarian | Aykırı yaklaşım | Beklenmedik/ters sahne kurgusu |

**Alınmayacak:**
- Platform specs (Google Ads 30 char, Meta 125 char vb.) — Otomaix Upload-Post kullanıyor, sosyal medya platform limitleri PLATFORM_DEFAULTS'ta zaten handle ediliyor
- "Iterating from Performance Data" bölümü — performans datası henüz Otomaix'te yok
- "Bulk CSV output", "Generative tools comparison" — kapsam dışı
- Platform spec tabloları — irrelevant

**Alınmama gerekçesi — çoğu skill'i alma:** ad-creative paid reklam yazımı için tasarlanmış, biz organik sosyal medya caption'ı üretiyoruz. Tek değerli parça 7 angle framework'ü; gerisi irrelevant.

---

## 4. Sprint Detayları

### Sprint 1 — social-content + copywriting → Tier 1

**Süre:** 0.5-1 iş günü
**Değişen dosya:** `apps/social/backend/app/core/prompt_builder.py` (yalnızca)
**Değişen fonksiyon:** `_SYSTEM_RULES` sabiti

#### 4.1.1 Değişiklik Kapsamı

`_SYSTEM_RULES` içine 3 yeni bölüm eklenecek (mevcut bölümler korunur):
1. **HOOK KURALI** [ref:social-content — Hook Formulas] — 4 kategori + Türkçe örnek kalıplar
2. **YAZIM KURALI** [ref:copywriting — Core Principles + Writing Style + CTA Formula] — fayda dili, somutluk, aktif ses, CTA formülü
3. **PLATFORM TON REHBERİ** [ref:social-content — Platform Quick Reference + references/platforms.md] — 9 platform için üslup/yapı farkı (PLATFORM_DEFAULTS hard kuralları üzerine soft katman). 4 ekstra platform (YouTube, Threads, Pinterest, Bluesky) skill kapsamı dışı.

Mevcut bölümler (değişmiyor):
- DİL KURALI (Türkçe zorunluluk)
- KULLANICI İSTEĞİ öncelik
- YASAK (uydurma istatistik)
- ÇIKTI FORMATI (JSON)

#### 4.1.2 Eski Prompt (mevcut `_SYSTEM_RULES`)

```
Sen Türk KOBİ'lerine sosyal medya içeriği üreten bir uzmansın.

DİL KURALI (çok önemli): Yanıtın tamamen Türkçe olmalı.
İngilizce veya yabancı kökenli terimler kullanma. Yaygın Türkçe karşılıkları
kullan: 'content creator' yerine 'içerik üretici', 'caption' yerine 'başlık',
'engagement' yerine 'etkileşim', 'story' yerine 'hikaye', 'reel' yerine
'kısa video'. Marka adları ve platform isimleri orijinal kalabilir.

⚠️ KULLANICI İSTEĞİ HER ZAMAN ÖNCELİKLİDİR: ...

YASAK: Gerçekliği olmayan sayısal iddialar ('%300 artış', '30 saatten 2 saate')
uydurma — sadece somut özellik ve faydalardan bahset.

ÇIKTI FORMATI: Her zaman JSON döndür. ...
```

#### 4.1.3 Yeni Prompt (Sprint 1 sonrası `_SYSTEM_RULES`)

```
Sen Türk KOBİ'lerine sosyal medya içeriği üreten bir uzmansın.

[DİL KURALI — mevcut, aynen korunur]

[KULLANICI İSTEĞİ ÖNCELİK — mevcut, aynen korunur]

📣 CAPTION HOOK KURALI (ilk cümle için — zorunlu) [ref:social-content — Hook Formulas]
Caption'ın ilk cümlesi aşağıdaki 4 kategoriden birine uymalı. Bu kategoriler
birer esin menüsü — örnek kalıpları kelime kelime kopyalama, markanın tonuna
ve doğal Türkçe'ye uygun kendi cümleni kur.

1. MERAK (curiosity) — okuru "neden?" sorusuna iter
   Türkçe örnek kalıplar:
   - "Çoğu [sektör] şunu bilmez: ..."
   - "[Yaygın inanç] diye bilirdik, aslında ..."
   - "Şaşırtıcı ama: ..."
   Amaç: alışılmış bir varsayımı çürütmek veya beklenmedik bir detay paylaşmak.

2. HİKAYE (story) — küçük bir sahne kurar, okuyucuyu içine çeker
   Türkçe örnek kalıplar:
   - "Geçen hafta bir müşterimiz ..."
   - "3 yıl önce [durum]. Bugün [değişim]."
   - "Bir cuma akşamı bize şu soru geldi: ..."
   Amaç: somut bir an / karakter / dönüşüm üzerinden bağ kurmak.

3. FAYDA (value) — somut bir sonuç vaat eder
   Türkçe örnek kalıplar:
   - "[Outcome]'a ulaşmanın 3 yolu: ..."
   - "[Pain] olmadan [outcome]:"
   - "[X] yapmayı bırak, bunu yap:"
   Amaç: okurun almayı umduğu pratik değeri açık etmek.

4. AYKIRI (contrarian) — yaygın tavsiyeye karşı çıkar
   Türkçe örnek kalıplar:
   - "Açık konuşayım: [yaygın görüşe ters iddia]"
   - "[Popüler tavsiye] yanlış. Sebebi şu:"
   - "Kimsenin söylemediği şu: ..."
   Amaç: dikkat çekmek + düşünmeye sevk etmek. Sansasyon olmasın.

⚠️ Hook kategorisi marka tonuyla uyumlu olmalı. Profesyonel/kurumsal tonda
"Aykırı" seçerken saldırgan değil, gözlem tonunda yaz. Samimi/eğlenceli tonda
"Hikaye" küçük bir anektod olabilir.

✍️ YAZIM KURALI (caption gövdesi + CTA için — zorunlu) [ref:copywriting — Core Principles + Writing Style + CTA Formula]

1. FAYDA > ÖZELLİK (Jobs to Be Done prensibi)
   Ürün/hizmetin özelliğini değil, o özelliğin müşteriye *ne kazandırdığını* yaz.
   ❌ "SporXL rahat tabanlıdır, kaliteli malzemedendir."
   ✅ "Gün boyu ayakta kalanlar için — akşama yorgun gelmeyen taban."

2. SOMUTLUK > SOYUTLUK
   "Kalite", "premium", "modern", "inovatif", "en iyi" gibi belirsiz sözler
   KULLANMA. Yerine somut detay koy.
   ❌ "Kaliteli malzemeyle üretildi."
   ✅ "24 saat sonra şeklini koruyan süet iç astar."

   Rakam varsa ekle, ama UYDURMA (zaten yasak). Gerçek rakam yoksa
   spesifik durum/özellik kullan.

3. AKTİF SES > EDİLGEN SES
   ❌ "Raporlar otomatik oluşturulur."
   ✅ "Raporları sen tetiklersin, biz oluştururuz."

4. MÜŞTERİ DİLİ > MARKA JARGONU
   Müşterinin gerçek hayatta kullandığı kelimeleri kullan. Marka içinde
   kullanılan teknik terimleri dışarıda kullanma.
   ❌ "Optimize edilmiş tabanlar sayesinde..."
   ✅ "Ayak ağrısı çekenler için..."

5. CTA FORMÜLÜ
   Yapı: [Eylem Fiili] + [Ne Alacak] + [Opsiyonel Ek Bilgi]
   ❌ "Öğren", "İncele", "Tıkla"
   ✅ "Kataloğu İndir", "Ücretsiz Deneyin", "Koltuğunu Ayır (son 3 kaldı)"

📱 PLATFORM TON REHBERİ (üslup/yapı — PLATFORM_DEFAULTS üzerine soft katman) [ref:social-content — Platform Quick Reference + references/platforms.md] (YouTube, Threads, Pinterest, Bluesky skill kapsamı dışı — kendi eklememiz)

PLATFORM_DEFAULTS caption uzunluğu + hashtag sayısı + first_comment kuralını
belirler (hard kural). Bu blok her platformun üslup/yapı tonunu verir:

- INSTAGRAM: görsel hikaye taşıyıcı. Hook görseli destekler, emoji uygun.
  Caption gövdesi duygusal tonda olabilir. Hashtag'ler first_comment'e.

- LINKEDIN: B2B, düşünce liderliği. Hook veriye/gözleme dayalı. Emoji az.
  Paragraf yapısı (kısa satırlar arası boşluk). "Biz/firmamız" değil
  "sektör/pratik" perspektifi.

- TWITTER/X: punch-first. Tek vurucu cümle. İronik/doğrudan ton kabul.
  Thread olacaksa ilk tweet standalone çalışmalı.

- TIKTOK: native, genç, samimi. Hook ilk 2 saniyeyi taşıyacak merak/şaşırtıcı
  olay. Emoji serbest. Resmi/kurumsal dil yasak.

- FACEBOOK: topluluk/yerel işletme tonu. Hook samimi, hikaye merkezli.
  Paragraf uzun olabilir, sohbet tonu.

- YOUTUBE: video tamamlayıcı. Caption kısa açıklama + timestamps benzeri
  yapılandırma. Tıklatma değil, tamamlama vurgusu.

- THREADS: kısa, günlük sohbet. Instagram'a paralel ama daha informal.

- PINTEREST: keşfedilebilirlik odaklı. Hook arama sorgusuna cevap
  niteliğinde. "Nasıl [X]" / "[X] fikirleri" gibi.

- BLUESKY: erken evre topluluk, minimal. Kısa vurucu. Gereksiz hashtag yasak.

⚠️ MARKA TON'U ÖNCELİKLİDİR
Platform ton'u, brand_kit.tonality'ye EK katmandır — override DEĞİLDİR.
Kurumsal tonlu bir marka TikTok'ta bile kurumsal kalır, yalnızca platformun
yapısına (hook süresi, paragraf uzunluğu, emoji kullanımı) uyarlar.
Çatışma durumunda marka tonu kazanır.

[YASAK — mevcut, aynen korunur]

[ÇIKTI FORMATI — mevcut, aynen korunur]
```

#### 4.1.4 Somut Karşılaştırma — Aynı Girdi Farklı Prompt

**Girdi:**
- Marka: MyGoodShoes
- Şablon: `genel-gorsel-sablon`
- `ana_konu`: SporXL spor ayakkabı
- `one_cikan_ozellik`: rahat taban, hafif, 79 TL

**Eski prompt beklenen çıktı (gözlemlenen tip):**
```
SporXL ile tanışın! Rahat tabanı ve hafif yapısıyla günlük kullanım için
mükemmel bir seçim. Kaliteli malzemeyle üretilen bu modern ayakkabı, tarzınıza
şıklık katacak. Sadece 79 TL! 💚 #sporayakkabı #moda
```

**Yeni prompt beklenen çıktı (Sprint 1 sonrası):**
```
Gün sonunda ayaklarınız neden yoruluyor biliyor musunuz?

Çoğu günlük ayakkabı, uzun saatler ayakta kalmak için tasarlanmıyor. SporXL
farklı: hafif yapısı ve destek veren tabanı ile 8 saat üstü ayakta duranlar
için yapıldı.

79 TL — ayağına uygun numarayı profilimizdeki linkten seç.
```

**Karşılaştırma:**
| Boyut | Eski | Yeni |
|-------|------|------|
| Hook | Yok (jenerik "tanışın" girişi) | Curiosity (soru + pain point) |
| Fayda dili | "Kaliteli/modern" soyut | "8 saat üstü ayakta duranlar için" somut |
| Aktif ses | "Üretilen" (edilgen) | "Destek veren" (etken) |
| CTA | "Sadece 79 TL!" jenerik | "Profilimizdeki linkten seç" aksiyon fiili |

#### 4.1.5 Etki Analizi

- **Risk:** Düşük — tek dosya (`prompt_builder.py`), tek sabit (`_SYSTEM_RULES`). Davranış değişikliği Claude çıktısında görülür, kod path'i değişmez.
- **Cache invalidation:** Tek seferlik global — tüm marka + şablon kombinasyonları için ilk çağrı cache miss, sonrası hit.
- **Backward compat:** Tam — caller'lar (caption_generator) etkilenmez, response şeması değişmez.
- **Token maliyeti:** ~550 token Tier 1 artışı. Cache hit durumunda çağrı başı ~$0.0008. Miss durumunda (ilk çağrı) ~$0.01.

#### 4.1.6 Canlı Test Kriterleri

Kullanıcı onayı sonrası deploy → 4 kontrol senaryosu:

1. **E-ticaret markası + ürün tanıtımı** — MyGoodShoes + `genel-gorsel-sablon` + ana_konu "SporXL spor ayakkabı" + one_cikan_ozellik "rahat taban, hafif, 79 TL"
   - Caption ilk cümlesi 4 hook kategorisinden birine uyuyor mu?
   - Caption gövdesinde "kalite/premium" vs somut detay oranı?
   - CTA `[Eylem]+[Ne Alacak]` formülüne uyuyor mu?
2. **Hizmet markası + hizmet tanıtımı** — Bir kuaför/klinik markası + `genel-gorsel-sablon` + ana_konu "saç bakım hizmeti"
   - Hook hikaye/fayda kategorisinde mi?
   - Özellik sayma yerine fayda dili var mı?
3. **Bilgi/eğitim içeriği** — Herhangi bir marka + `genel-gorsel-sablon` + ana_konu "diş fırçalamanın doğru tekniği" + user_prompt "eğitici içerik"
   - Satış dili sızıntısı var mı? (bu içerik tipi için olmamalı)
   - Hook kategorisi eğitici tona uygun mu (aykırı/sansasyon değil)
4. **Platform farklılaşması** — Aynı marka + `genel-gorsel-sablon` + aynı user_prompt ile LinkedIn + Twitter + Instagram seçilerek tek üretim
   - Üç platform caption'ı aynı metnin kopyası mı, yoksa her biri ton/yapı olarak gerçekten farklı mı? (LinkedIn paragraflı/gözlem tonu, Twitter punch-first, Instagram görsel-destekleyici)
   - Hook kategorisi platform'a göre uygun seçilmiş mi?
   - Marka tonuyla çatışma var mı?

Her senaryo için eski vs yeni çıktı kullanıcıya göster. **Somut fark yoksa** Sprint 1 sonuçsuz — Sprint 2'ye geçilmez, önce neden etkisiz olduğu araştırılır.

#### 4.1.6b Canlı Test Sonuçları (2026-04-23)

**Test ürünü:** MyGoodShoes / TrendShoe Topuklu Ayakkabı ("Şık, gösterişli, topuklu kadın ayakkabısı")

**Sprint 1 ilk deploy (`e3aedca`) sorunları:**
- Claude ürüne ait olmayan özellikler uydurdu: "ergonomik iç taban", "ortopedik dolgu", "8 saat ayakta", fabricated müşteri yorumu
- Görsel kalitesi düştü: full-body fashion shot → diz altı crop, olası erkek anatomisi
- **Kök neden:** SOMUTLUK kuralı "vague olma" dedi ama "bilgi yoksa uydur" demek istemedi; caption_generator kural #5 her durumda close-up zorladı

**Hotfix iterasyonları (4 commit, `481f662`→`e46a351`):**
1. SOMUTLUK kaçış klozu + YASAK fabrication maddeleri
2. Dolaylı fayda iddiası da yasak kapsamına
3. Ürün-bağımsız kurallar + LinkedIn ton sıkılaştırma + kurgusal otorite yasağı + hashtag kapsamı
4. Tüm örnekler soyut kalıplara çevrildi (spesifik ürün örneği yok)

**Hotfix sonrası durum:**
- ✅ Görsel: full-body fashion shot, doğru cinsiyet, dengeli kompozisyon
- ✅ Blatant fabrication kalktı (teknik özellik uydurma)
- ✅ Twitter/Instagram: sade, dürüst, etkili
- ⚠️ LinkedIn/YouTube: hâlâ dolaylı uydurma (konfor iddiası, tasarım süreci hikayesi, sektör gözlemi)
- ⚠️ Hashtag: bilgide olmayan özellik sızdırıyor (#şıkverahat, #herAdımdaKonfor)

**Açık sorun — Sprint 2'ye geçmeden çözülmeli:**
YASAK kuralları negatif ("yapma") ama Claude bilgi azken ne yapacağını bilmiyor → uzun formatlarda (LinkedIn, YouTube) boşluğu dolgu cümlesiyle dolduruyor. Çözüm adayları:
- (A) Tier 3 dynamic content'e YASAK tekrarı (son gördüğü talimat en etkili)
- (B) Pozitif talimat: "bilgi azsa içerik kısa kalsın, dolgu yazma"

**Sprint 1 polish (2026-04-24) — 3 karar:**
1. **Model:** claude-opus-4-7 → claude-opus-4-6. Opus 4.6 constraint-heavy görevlerde daha disiplinli, YASAK kurallarına daha literal uyuyor. Canlı test: fabrication riski belirgin şekilde düştü.
2. **HOOK KURALI kaldırıldı:** Zorunlu 4 kategori (Merak/Hikaye/Fayda/Aykırı) Claude'u formülsel açılışlara sıkıştırıyordu. Kaldırılınca daha doğal, çeşitli açılışlar.
3. **LinkedIn:** `long` (200-500 kelime) → `medium` (50-150 kelime). Profesyonel ton PLATFORM TON REHBERİ'nde korunuyor.

Bu 3 değişiklik hotfix'teki açık sorunları (LinkedIn/YouTube dolgu) büyük ölçüde çözdü — model disiplini + kısa format = dolgu alanı daraldı.
- Her iki yaklaşım birlikte uygulanmalı

#### 4.1.7 Rollback

```bash
git revert <sprint-1-commit-hash>
git push
```

Tier 1 eski haline döner. Cache yeniden invalidate olur. Sprint 2 henüz deploy edilmediyse anlık etki — kullanıcı bir sonraki post üretiminde eski davranışı görür.

---

### Sprint 2 — marketing-psychology → Tier 1

**Süre:** 0.5-1 iş günü
**Değişen dosya:** `apps/social/backend/app/core/prompt_builder.py` (yalnızca)
**Değişen fonksiyon:** `_SYSTEM_RULES` sabiti (Sprint 1 eklemeleri korunur, üstüne eklenir)

#### 4.2.1 Değişiklik Kapsamı

Sprint 1'in üstüne 1 blok eklenir:
- **PSİKOLOJİ PRENSİPLERİ** [ref:marketing-psychology — Foundational + Buyers Psychology + Influencing Behavior] (seçme 5 prensip)
- **PSİKOLOJİ UYGULAMA KURALI** [skill dışı — kendi eklememiz] (2 dallanma eşleme — §3.3'te gerekçesi)

Platform ton bloğu Sprint 1'e taşındı (skill bütünlüğü için — social-content'in tek sprint'te bir arada kalması mantıklı).

#### 4.2.2 Yeni Eklemeler (Sprint 2)

**PSİKOLOJİ BLOKU (5 seçme prensip + uygulama kuralı):**

```
🧠 PSİKOLOJİ PRENSİPLERİ (caption stratejisi için) [ref:marketing-psychology — Foundational + Buyers Psychology + Influencing Behavior]

Aşağıdaki prensipler caption'ın *yapısına* yön verir. Hepsini her post'ta
kullanma — içerik türüne ve kullanıcı isteğine uygun olanları seç.

1. JOBS TO BE DONE
   Müşteri ürünü satın almıyor, bir "işi" yapması için kiralıyor.
   Matkap alan kişi matkap değil, DELİK istiyor.
   Uygulama: Ürünün ne olduğunu değil, hangi işi çözdüğünü yaz.

2. SOMUTLUK (Specificity)
   Soyut iddia inandırıcı değil, somut detay inandırıcıdır.
   "İyi sonuç" değil, "ilk hafta 3 yeni sipariş".
   Uygulama: Her vaadin arkasında spesifik durum/rakam/zaman olmalı.
   Gerçek değilse kullanma (YASAK kuralı hatırlatması).

3. LOSS AVERSION (kayıp duyarlılığı)
   İnsanlar 100 TL kazanmaktan çok, 100 TL kaybetmekten korkar.
   Uygulama: Kullanıcının "kaçırma" tarafını göster — ama SAHTE scarcity
   yaratma (gerçek stok/süre yoksa kullanma, YASAK).
   ✅ "Bu hafta sonu sipariş verenler pazartesi elinde." (gerçek kargo süresi)
   ❌ "Son 3 ürün!" (stoktan emin değilse)

4. SOCIAL PROOF
   İnsanlar ne yapacağını, başkalarının ne yaptığına bakarak anlar.
   Uygulama: Sayı/topluluk/referans varsa caption'a doğal şekilde yerleştir.
   ✅ "300+ işletmenin tercih ettiği sistem"
   ❌ "Herkes bizi tercih ediyor" (soyut)

5. HYPERBOLIC DISCOUNTING (anlık fayda önyargısı)
   İnsan "6 ay sonra ROI" yerine "bugün başla"yı tercih eder.
   Uygulama: Fayda zaman ufku kısa olsun — "hemen", "bu hafta", "ilk siparişte".

🎯 PSİKOLOJİ UYGULAMA KURALI (hangi prensibi ne zaman kullan) [skill dışı — kendi eklememiz, gerekçe: §3.3 kısaltılmış B yaklaşımı]

- SATIŞ/PROMOSYON ODAKLI post (ürün kartı, kampanya, indirim):
  Specificity zorunlu — soyut iddia ("kalite", "premium") yasak, somut
  detay/durum gerekli.
  Loss Aversion + Social Proof yalnızca GERÇEK sayı/stok/süre varsa kullan.
  Sahte scarcity yaratma (veri yoksa bu prensipleri sokma).

- BİLGİ/HİKAYE/KURUMSAL post (hakkımızda, ekip, biliyor muydunuz, alıntı):
  JTBD çerçevesi uygula — "ürünümüz şu özelliklere sahip" değil, "müşterinin
  çözdüğü iş şu" perspektifi.
  Satış dili ve scarcity kesinlikle sokma — içeriğin doğal tonunu bozar.

- İçerik türünü kullanıcı isteği (user_prompt) + şablon adı + yapısal
  verilerden çıkar.

- Emin değilsen HİÇBİR PRENSİP SOKMA — caption'ı doğal akışa bırak.
  Hook ve yazım kuralları (Tier 1'de zaten tanımlı) tek başına yeterli.
```

#### 4.2.3 Eski Prompt → Yeni Prompt (Sprint 2)

Sprint 1 sonrası Tier 1 ~1050 token. Sprint 2 eklemesi ile ~1550 token. Fark: psikoloji prensipleri + uygulama kuralı bloğu.

**Somut karşılaştırma — Satış/promosyon postu (Loss Aversion + Hyperbolic Discounting devrede):**

Marka: MyGoodShoes | Şablon: `genel-gorsel-sablon` | ana_konu: "SporXL spor ayakkabı" | user_prompt: "Sezon sonu kampanyası, stoklar sınırlı" (kullanıcı gerçek stok bilgisi veriyor)

**Sprint 1 sonrası çıktı (sadece hook + copywriting, psikoloji yok):**
```
Gün boyu ayakta kalanlar için SporXL.

8 saat üstü ayakta duranlar için tasarlandı — hafif yapısı ve destek veren
tabanı ile. Sezon sonu fiyatı 79 TL.

Ücretsiz kargo için profilimizdeki linkten inceleyin.
```

**Sprint 2 sonrası çıktı (psikoloji devrede — satış/promosyon branch):**
```
Gün sonunda ayaklarınız neden yoruluyor biliyor musunuz?

Çoğu günlük ayakkabı, uzun saatler ayakta kalmak için tasarlanmıyor. SporXL
farklı: 8 saat üstü taşıyan hafif taban.

Sezon sonu fiyatı 79 TL — stoklar bu hafta sonunda yenilenecek, tüm renkler
mevcutken profilimizdeki linkten bak.
```

**Karşılaştırma:**
| Boyut | Sprint 1 sonrası | Sprint 2 sonrası |
|-------|-----------------|------------------|
| Hook | Fayda kategorisi — statik başlık | Merak kategorisi — soru açılışı |
| JTBD | Yok belirgin | "8 saat üstü taşıyan" — açık iş tanımı |
| Specificity | "8 saat" var | "8 saat" + "bu hafta sonu" zaman netliği |
| Loss Aversion | Yok | "stoklar bu hafta sonunda yenilenecek" — **gerçek veriye dayalı** |
| Hyperbolic Discounting | Yok (zaman ufku açık) | "tüm renkler mevcutken" — anlık fayda vurgusu |

**Kontra örnek — Bilgi/hikaye postu (psikoloji uygulama kuralı "sokma" branch'i):**

Marka: Bir diş kliniği | Şablon: `genel-gorsel-sablon` | ana_konu: "Diş fırçalamanın doğru tekniği" | user_prompt: "eğitici içerik"

**Sprint 2 sonrası çıktı (psikoloji bloğu var ama uygulama kuralı "bilgi postu → sokma" dedi):**
```
Biliyor muydunuz — diş fırçalarken yatay hareket diş eti çekilmesinin
en büyük sebebi?

Doğru teknik: 45 derece açıyla diş etine yönelt, dairesel hareketlerle
iki dakika fırçala. Üst üste iki hafta uygulayınca diş eti hassasiyetinde
fark hissedersin.

Detaylı teknik için diş hekiminize danışın.
```

Dikkat: Bu caption'da Loss Aversion, Hyperbolic Discounting, Social Proof YOK. Sadece Specificity (45 derece, 2 dakika, 2 hafta) + JTBD (diş eti çekilmesini önleme) var — bilgi postunun doğal akışı korundu. Psikoloji Uygulama Kuralı'nın "bilgi/hikaye — satış dili sokma" branch'i devrede.

#### 4.2.4 Etki + Risk

- **Risk:** Düşük-orta — psikoloji prensipleri "fazla uygulanma" riski taşır (Claude her caption'a 5 prensibin hepsini sokmaya çalışır, yapay olur). Mitigasyon: Psikoloji Uygulama Kuralı 2 dallanma + "emin değilsen sokma" çıkışı.
- **Sahte scarcity riski:** Loss Aversion kötüye kullanılırsa Claude "son 3 kaldı" uydurabilir. 3 katmanlı disiplin: YASAK bloğu + Loss Aversion bloğundaki "gerçek stok/süre yoksa kullanma" + Uygulama Kuralı "sadece gerçek veri varsa". Canlı testte kontrol edilecek (§4.2.5).
- **Cache invalidation:** Sprint 1 sonrası oturmuş cache Sprint 2 deploy'unda yeniden invalidate — tek seferlik cost.

#### 4.2.5 Canlı Test Kriterleri

Sprint 2 testi psikoloji katmanına odaklanır. Platform farklılaşması Sprint 1'de test edildi, burada tekrar edilmez (regresyon spot-check yeterli).

1. **Satış/promosyon post — tam psikoloji kombinasyonu**
   MyGoodShoes + `genel-gorsel-sablon` + ana_konu "SporXL" + user_prompt "sezon sonu kampanyası, stoklar sınırlı" → caption'da Specificity + Loss Aversion + Hyperbolic Discounting doğal şekilde kullanılmış mı? Yapay dizilim (her prensibi mekanik olarak sokma) var mı?
2. **Bilgi/hikaye post — psikoloji "sokma" branch kontrolü**
   Diş kliniği / eğitim markası + `genel-gorsel-sablon` + ana_konu "diş fırçalamanın doğru tekniği" + user_prompt "eğitici içerik" → caption'da "hemen al", "bu hafta başla", "son X kaldı" gibi satış dili SIZINTISI var mı? Varsa Psikoloji Uygulama Kuralı yetersiz — sıkılaştırılmalı.
3. **Sahte scarcity kontrolü**
   Kullanıcı brief'inde zaman/stok/müşteri sayısı belirtmediği bir satış postu üret. Caption'da "son X kaldı", "bu hafta sonu son gün", "sadece N müşteri kaldı" gibi uydurma rakam/süre var mı? Varsa Tier 1 Loss Aversion bloğu sıkılaştırılmalı.
4. **Psikoloji aşırı kullanım kontrolü**
   Tek postta 5 prensip de mekanik olarak tek tek saydırılıyor mu? ("Bu ürünün çözdüğü iş X. Tam olarak Y özelliği. 300 işletme seçti. Son 3 gün. Hemen al.") Varsa prompt'ta "hepsini birden kullanma" vurgusu yetersiz, örnek caption ile desteklenmeli.

---

### Sprint 3 — ad-creative → Tier 2 (`genel-gorsel-sablon.guidance`)

**Süre:** 0.5 iş günü
**Değişen dosya:** `apps/social/backend/app/core/templates_data.py` (yalnızca)
**Değişen alan:** `TEMPLATES["genel-gorsel-sablon"].prompt.guidance`

#### 4.3.1 Değişiklik Kapsamı

`genel-gorsel-sablon` şablonunun `prompt.guidance` metnine 7 görsel açı kategorisi + her açının sahne/kompozisyon karşılığı + açı seçim talimatı eklenir. Mevcut guidance'ın diğer kısımları (marka renkleri HEX zorunluluğu, logo/rozet yasağı, CTA kuralı) korunur.

**Önemli:** Diğer şablonlar (şu an devre dışı) bu değişiklikten etkilenmez. Aktif olan tek şablon `genel-gorsel-sablon` — 7 açı bu şablona ekleniyor.

#### 4.3.2 Eski Guidance (`templates_data.py`'daki mevcut metin — spot kontrol gerekir)

```
(Sprint 3 öncesi Read ile doğrula; aşağıdaki tahmini içerik)

Genel bir sosyal medya görseli üret. Marka renklerini (HEX kodları ile)
kullan. Logo/rozet/metin tarif etme — watermark post-process'te eklenecek.
Beige/off-white/stüdyo stokları yasak. Caption formülü: Hook → Özellik → CTA.
CTA kuralı: IG/TikTok için 'profilimizdeki link' + first_comment URL,
LinkedIn/FB/TW için direkt URL caption'a.
```

#### 4.3.3 Yeni Guidance (Sprint 3 sonrası)

```
Genel amaçlı sosyal medya görseli. Aşağıdaki kurallar sırayla uygulanır:

🎨 GÖRSEL AÇI KATEGORİSİ (seçim zorunlu) [ref:ad-creative — Define Your Angles]

image_prompt'u yazmadan önce içeriğin hangi açıdan hikaye anlattığına karar
ver. 7 kategori var, bir tanesini seç:

1. SORUN VURGUSU (pain point)
   Hikaye: problemi görselleştir — öncesi sahne, yorgunluk, engel.
   Sahne örneği: "Close-up of tired feet at the end of a long workday,
   soft evening light, muted tones."

2. SONUÇ VURGUSU (outcome)
   Hikaye: dönüşüm/başarı anı — sonrası sahnesi.
   Sahne örneği: "A runner crossing a city finish line at golden hour,
   energetic posture, clean composition."

3. SOSYAL KANIT (social proof)
   Hikaye: topluluk/grup — ortak kullanım.
   Sahne örneği: "A group of commuters wearing similar shoes at a subway
   station, candid shot, urban morning light."

4. MERAK UYANDIRMA (curiosity)
   Hikaye: örtük/kısmi gösterim — detay yakın plan.
   Sahne örneği: "Extreme close-up of running shoe sole showing unique
   tread pattern, macro lens, studio lighting."

5. ACİLİYET (urgency)
   Hikaye: zamana bağlı gösterge — sınırlı sahne.
   Sahne örneği: "Product display with subtle countdown context — empty
   shelves behind a single remaining pair, warm spotlight."

6. KİMLİK VURGUSU (identity)
   Hikaye: hedef kitleye özel ortam — "Bu senin için" mesajı.
   Sahne örneği: "A nurse in hospital scrubs tying shoe laces before
   shift, clean clinical background, documentary feel."

7. AYKIRI YAKLAŞIM (contrarian)
   Hikaye: beklenmedik/ters sahne.
   Sahne örneği: "Running shoes in an unexpected formal office setting,
   shot like a portrait, dramatic light."

⚠️ AÇI SEÇİMİ KURALI
- Kullanıcı isteği (user_prompt) hangi açıyı çağrıştırıyorsa o seçilir.
- Kullanıcı isteği net değilse: şablon alanlarından ana_konu'nun tonuna
  bakarak seç (satış ağırlıklı → outcome/urgency; hikaye ağırlıklı →
  identity/curiosity).
- Aynı açıyı sürekli seçme tuzağına düşme — özellikle "outcome" ve
  "social proof" stüdyo estetiğine itiyor. Çeşitlilik için diğer 5
  açıyı da kullan.

🎨 MARKA RENKLERİ
[Mevcut kural aynen korunur: HEX zorunluluğu, beige/off-white yasak]

⛔ YASAKLAR
[Mevcut yasaklar aynen korunur: logo, rozet, metin katmanı, Türkçe,
marka/ürün adı]

✍️ CAPTION FORMÜLÜ
Hook (Tier 1 kuralına göre 4 kategoriden biri) → Özelliğin Faydası →
CTA (formül: [Eylem]+[Ne Alacak])

🔗 CTA KURALI (platform'a göre)
- Instagram/TikTok: "profilimizdeki link" + first_comment'te URL
- LinkedIn/Facebook/Twitter: direkt URL caption'a
```

#### 4.3.4 Somut Karşılaştırma — Aynı Girdi

**Girdi:**
- Marka: MyGoodShoes
- Şablon: `genel-gorsel-sablon`
- `ana_konu`: "Yeni sezon koleksiyonumuz"
- `one_cikan_ozellik`: (boş)

**Eski prompt'un image_prompt çıktısı (tipik — "clean studio" tuzağı):**
```
Professional product photography of athletic running sneakers, clean studio
background in #4A1A5C purple, soft diffused lighting from the left,
premium materials texture visible on upper mesh. No text, no logos, no overlays.
```

**Yeni prompt'un image_prompt çıktısı (açı: "identity"):**
```
A young commuter in casual weekend outfit sitting on subway stairs, laces
her new running sneakers before a morning walk. Shot from a low angle,
natural morning light, candid lifestyle composition. The environment uses
muted urban tones with accent lighting in #4A1A5C purple from a nearby
storefront reflection. Documentary feel, shallow depth of field.
No text, no logos, no overlays.
```

**Karşılaştırma:**
| Boyut | Eski | Yeni |
|-------|------|------|
| Sahne | Stüdyo product shot | Lifestyle (identity açısı) |
| Öykü | Ürün tek öznede | Kullanıcı + ürün + bağlam |
| Marka rengi | Yüzey rengi olarak | Aksan ışık olarak (doğal) |
| Çeşitlilik | Her içerik aynı stüdyo | 7 farklı açı seçeneği |

#### 4.3.5 Etki + Risk

- **Risk:** Düşük — tek şablonun guidance'ı, etki yalnızca `genel-gorsel-sablon` kullanan post'larda.
- **Tekrar kontrolü:** Tier 3'teki `_build_output_format_instruction`'daki 6 image_prompt kuralı (marka adı yasak, Türkçe yasak vb.) bu sprint'te tekrar yazılmıyor. Yeni guidance bloğu yalnızca **açı seçimi + sahne örnekleri**. Overlap yok.
- **Diğer 21 şablona etki:** Yok. Onların kendi guidance'ları aynen kalır.
- **Token maliyeti:** ~300 token Tier 2 artışı (sadece bu şablonu seçen post'larda). Tier 2 cache marka+şablon+sektör bazlı olduğundan, yalnızca `genel-gorsel-sablon` için ilk çağrı miss.

#### 4.3.6 Canlı Test Kriterleri

1. **MyGoodShoes + genel-gorsel-sablon + "yeni sezon koleksiyonumuz"** — 3 ardışık üretim yap. Üçü de aynı açıyı seçmemeli (pattern: her defasında outcome/studio)
2. **Hizmet markası + genel-gorsel-sablon + "hizmet tanıtımı"** — identity veya pain-point açısı beklenir (outcome zayıf kalır)
3. **Sağlık sektörü** (şablonu bilerek `genel-gorsel-sablon` seç — test için) — contrarian/aykırı açı seçmemeli (sektöre uymaz)

#### 4.3.7 Rollback

```bash
git revert <sprint-3-commit-hash>
git push
```

`genel-gorsel-sablon.guidance` eski haline döner. Diğer şablonlar zaten dokunulmadı.

---

## 5. Cache Etki Analizi (tüm sprint'ler toplu)

| Sprint | Tier 1 Δ token | Tier 2 Δ token | Cache durumu sonrası |
|--------|---------------|----------------|----------------------|
| Sprint 1 | +850 (toplam ~1050) — hook + copywriting + platform ton | — | Cache eşiğinin üstünde, güvenli cache'leniyor |
| Sprint 2 | +500 (toplam ~1550) — psikoloji + uygulama kuralı | — | Cache güvenli |
| Sprint 3 | — | +300 (yalnızca bir şablon) | Tier 2 zaten cache'leniyordu, artış marjinal |

**Phase 11 toplamı:**
- Tier 1 boyu: ~200 → ~1550 token (7-8x artış, cache threshold'u aşar)
- Sprint başı cache invalidation × 3 = 3 kez tüm markalarda ilk çağrı miss
- Sonraki çağrılar cache hit → %90 indirim (Opus read cost)
- Net maliyet: İlk 48 saatte bir miktar cache write ek cost, sonrası net kazanç

---

## 6. Risk Envanteri

| Risk | Olasılık | Etki | Mitigasyon |
|------|----------|------|------------|
| Hook formüllerinin robotik kullanılması | Orta | Orta | "Esin menüsü, kelime kelime kopyalama" talimatı Tier 1'de |
| Psikoloji prensiplerinin hepsinin her caption'a sokulması | Orta | Yüksek | "Hepsini her post'ta kullanma, içeriğe uygun olanı seç" talimatı |
| Platform ton bloğunun PLATFORM_DEFAULTS ile çatışması | Düşük | Düşük | Hard kural PLATFORM_DEFAULTS (uzunluk/hashtag), soft rehber Tier 1 ton; boyutlar ayrı |
| Motamot çeviri nedeniyle yapay Türkçe ("Popüler olmayan fikir") | Düşük | Orta | Tier 1'e yalnızca elle yazılmış doğal TR kalıplar konulacak |
| 7 açının her yerde stüdyo'ya düşmesi (eski davranış dönüşü) | Orta | Düşük | Sprint 3 test senaryosunda 3 ardışık üretim kontrolü |
| Tier 1 şişmesiyle Claude'un "kural tamamlama" davranışı | Düşük | Orta | Her blokta "çatışma durumunda user_prompt öncelikli" hatırlatması |
| Disclaimer/HEX zorunluluk gibi Tier 2 kurallarının bozulması | Düşük | Yüksek | Sprint 1-2-3 Tier 2'ye dokunmuyor; Sprint 3 yalnızca `genel-gorsel-sablon` guidance — disclaimer o şablonda zaten yok |
| Cache maliyeti ilk deploy sonrası ani yükseliş | Düşük | Düşük | Anthropic cache write 1.25x — tek seferlik, <$1 beklenir |

---

## 7. Uygulama Sırası ve Kullanıcı Onay Noktaları

```
Sprint 1 plan → kullanıcı onayı → kod → AST parse → commit onayı → push
    → canlı test (3 senaryo) → kullanıcı test onayı → Sprint 2'ye geç

Sprint 2 plan → kullanıcı onayı → kod → AST parse → commit onayı → push
    → canlı test (3 senaryo) → kullanıcı test onayı → Sprint 3'e geç

Sprint 3 plan → kullanıcı onayı → kod → AST parse → commit onayı → push
    → canlı test (3 senaryo) → kullanıcı test onayı → Phase 11 KAPANDI

Phase kapanışı:
- backend/CLAUDE.md: Phase 11 kapanış girdisi (Sprint 1-2-3 özeti)
- 11-social-marketingskills.md: üstüne "✅ PHASE 11 COMPLETE" bloğu
```

**Canlı test onayı alınmadan bir sonraki sprint'e geçilmez.** Bu `feedback_calisma_kurallari.md`'daki 6. kural.

---

## 8. Appendix A — CLAUDE.md Girdi Template

### A.1 Backend CLAUDE.md Girdisi (Sprint 1 örnek)

```markdown
## YYYY-MM-DD — Phase 11 Sprint 1: Hook + Copywriting kuralları Tier 1'e ✅

**Dosya:**
- app/core/prompt_builder.py (değişti — `_SYSTEM_RULES` genişletildi)

**Değişiklikler:**
- `_SYSTEM_RULES`'a CAPTION HOOK KURALI eklendi (4 kategori + Türkçe örnek kalıplar — social-content skill'i)
- `_SYSTEM_RULES`'a YAZIM KURALI eklendi (fayda>özellik, somutluk>soyutluk, aktif ses, müşteri dili, CTA formülü — copywriting skill'i)
- Mevcut bölümler (DİL KURALI, USER ÖNCELİK, YASAK, ÇIKTI FORMATI) korundu

**Prompt boyu değişimi:**
- Tier 1: ~200 → ~750 token
- Cache eşiği: sınır değerde, cache hit gözlemlenmeli

**Test sonuçları:**
- [ ] E-ticaret markası + genel-gorsel-sablon + ürün tanıtımı → hook + fayda dili ✅
- [ ] Hizmet markası + genel-gorsel-sablon + hizmet tanıtımı → hook + fayda dili ✅
- [ ] Platform farklılaşması (LinkedIn/Twitter/Instagram) → farklı ton ✅

**Commit:** <hash>

**Sonraki sprint:** Sprint 2 — Psikoloji prensipleri + platform ton
```

### A.2 Phase Kapanış Girdisi

```markdown
## YYYY-MM-DD — Phase 11 TAMAMLANDI ✅

**Sprint 1-2-3 özeti:**
- Sprint 1: Hook + copywriting kuralları → Tier 1
- Sprint 2: Psikoloji prensipleri + platform ton → Tier 1
- Sprint 3: 7 görsel açı → genel-gorsel-sablon guidance

**Tier 1 son boyu:** ~1250 token (Anthropic cache eşiğinin üstünde)

**Ölçüm:**
- Kalitatif: eski vs yeni prompt karşılaştırmalarında somut fark
- Cache: prod log'da cache_read_input_tokens değerleri arttı

**Commit'ler:** <sprint 1 hash>, <sprint 2 hash>, <sprint 3 hash>
```

---

## 9. Appendix B — Commit Message Formatı

```
feat: Phase 11 Sprint 1 — Hook + copywriting + platform ton Tier 1'e (social-content + copywriting)
feat: Phase 11 Sprint 2 — Psikoloji prensipleri Tier 1'e (marketing-psychology)
feat: Phase 11 Sprint 3 — 7 görsel açı genel-gorsel-sablon guidance'a (ad-creative)
docs: Phase 11 TAMAMLANDI — CLAUDE.md kapanış girdisi
```

Commit öncesi her zaman kullanıcı onayı, push sonrası canlı test talimatı verilir.

---

## 10. Belirsizlik Durumunda

Bu belgede açıkça karar verilmemiş bir nokta çıkarsa Claude Code'un yaklaşımı:

1. Kod yazmadan önce kullanıcıya sor
2. Hangi dosyada karar verilecek, hangi alternatifleri düşünüyor — açıkça belirt
3. Varsayım yapma — sor, sonra uygula
4. Cevap aldıktan sonra ilgili sprint'in CLAUDE.md girdisine kararı ekle

---

**Belge sonu.**

**Hazırlanma tarihi:** 2026-04-23
**Sürüm:** v1.0 (taslak, kullanıcı onayı bekliyor)
**Kapsam:** Otomaix Social — 4 yüksek öncelikli marketing skill'inin `prompt_builder.py` ve `templates_data.py`'a entegrasyonu
**Toplam:** 3 sprint, ~2-3 iş günü
