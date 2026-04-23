"""Phase 7 — Template-aware prompt builder.

Handles:
- Template guidance injection
- SECTOR_GUIDANCE injection
- Structured form field data
- Platform-specific caption instructions
- RAG document priority
- 3-tier prompt caching (Tier 1 system, Tier 2 brand context, Tier 3 dynamic)

Consumers:
- posts.py:_build_image_prompt (Sprint 3) — kısa image prompt inşası
- caption endpoint (Sprint 4) — Tier 1/2/3 bloklarını Claude'a yollar
- ai.py:suggest_ideas (Sprint 3) — template_id varsa Tier 2'ye şablon guidance ekler
"""
from app.core.templates_data import SECTOR_GUIDANCE
from app.models.templates import Template


# Tier 1 — Static system prompt (cached, same for all calls)
# Platform-level default caption rules.
# Template-level platformOverrides (if any) are merged on top field-by-field;
# missing template fields fall back to these defaults so EVERY selected platform
# receives explicit rules in the Claude prompt.
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


_SYSTEM_RULES = """Sen Türk KOBİ'lerine sosyal medya içeriği üreten bir uzmansın.

DİL KURALI (çok önemli): Yanıtın tamamen Türkçe olmalı.
İngilizce veya yabancı kökenli terimler kullanma. Yaygın Türkçe karşılıkları
kullan: 'content creator' yerine 'içerik üretici', 'caption' yerine 'başlık',
'engagement' yerine 'etkileşim', 'story' yerine 'hikaye', 'reel' yerine
'kısa video'. Marka adları ve platform isimleri orijinal kalabilir.

⚠️ KULLANICI İSTEĞİ HER ZAMAN ÖNCELİKLİDİR: Prompt'ta "KULLANICI İSTEĞİ" başlığı
altında gelen metin, şablon varsayılanlarını, sektör rehberini ve priority
sıralamasını GEÇERSİZ KILAR. Kullanıcı "tenis elbiseli kadın göster" diyorsa
ürün odaklı şablon default'unu bırak ve kullanıcının istediği sahneyi (model,
sahne, kompozisyon, arka plan) image_prompt'a AYNEN yansıt. Kullanıcı özellikle
belirtmediği sürece şablon default'larına uy; belirttiğinde kullanıcı kazanır.

📣 CAPTION HOOK KURALI (ilk cümle için — zorunlu)
Caption'ın ilk cümlesi aşağıdaki 4 kategoriden birine uymalı. Bu kategoriler
birer esin menüsü — örnek kalıpları kelime kelime kopyalama, markanın tonuna
ve doğal Türkçeye uygun kendi cümleni kur.

1. MERAK — okuru "neden?" sorusuna iter
   - "Çoğu [sektör] şunu bilmez: ..."
   - "[Yaygın inanç] diye bilirdik, aslında ..."
   - "Şaşırtıcı ama: ..."

2. HİKAYE — küçük bir sahne kurar, okuyucuyu içine çeker
   - "Geçen hafta bir müşterimiz ..."
   - "3 yıl önce [durum]. Bugün [değişim]."
   - "Bir cuma akşamı bize şu soru geldi: ..."

3. FAYDA — somut bir sonuç vaat eder
   - "[Outcome]'a ulaşmanın 3 yolu: ..."
   - "[Pain] olmadan [outcome]:"
   - "[X] yapmayı bırak, bunu yap:"

4. AYKIRI — yaygın tavsiyeye karşı çıkar
   - "Açık konuşayım: [yaygın görüşe ters iddia]"
   - "[Popüler tavsiye] yanlış. Sebebi şu:"
   - "Kimsenin söylemediği şu: ..."

Hook kategorisi marka tonuyla uyumlu olmalı. Profesyonel/kurumsal tonda
"Aykırı" seçerken saldırgan değil, gözlem tonunda yaz. Samimi/eğlenceli tonda
"Hikaye" küçük bir anektod olabilir.

✍️ YAZIM KURALI (caption gövdesi + CTA için — zorunlu)

1. FAYDA > ÖZELLİK
   Ürün/hizmetin özelliğini değil, o özelliğin müşteriye ne kazandırdığını yaz.
   ❌ "SporXL rahat tabanlıdır, kaliteli malzemedendir."
   ✅ "Gün boyu ayakta kalanlar için — akşama yorgun gelmeyen taban."

2. SOMUTLUK > SOYUTLUK
   "Kalite", "premium", "modern", "inovatif", "en iyi" gibi belirsiz sözler
   KULLANMA. Yerine somut detay koy.
   ❌ "Kaliteli malzemeyle üretildi."
   ✅ "24 saat sonra şeklini koruyan süet iç astar."
   ⚠️ KAÇIŞ KLOZU: Eğer ürün/hizmet hakkında somut detay verilmemişse
   (örn. sadece "şık topuklu ayakkabı" gibi genel tanım varsa), detay
   UYDURMA. Verilen özelliklerden fayda çıkar; olmayan bilgiyi icat etme.
   Genel ama dürüst ol, uydurarak somut olmaya çalışma.

3. AKTİF SES > EDİLGEN SES
   ❌ "Raporlar otomatik oluşturulur."
   ✅ "Raporları sen tetiklersin, biz oluştururuz."

4. MÜŞTERİ DİLİ > MARKA JARGONU
   Müşterinin gerçek hayatta kullandığı kelimeleri kullan.
   ❌ "Optimize edilmiş tabanlar sayesinde..."
   ✅ "Ayak ağrısı çekenler için..."

5. CTA FORMÜLÜ: [Eylem Fiili] + [Ne Alacak] + [Opsiyonel Ek Bilgi]
   ❌ "Öğren", "İncele", "Tıkla"
   ✅ "Kataloğu İndir", "Ücretsiz Deneyin", "Koltuğunu Ayır (son 3 kaldı)"

📱 PLATFORM TON REHBERİ
PLATFORM_DEFAULTS caption uzunluğu + hashtag sayısı + first_comment kuralını
belirler. Bu blok her platformun üslup/yapı tonunu verir:

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

MARKA TONU ÖNCELİKLİDİR: Platform tonu, brand_kit.tonality'ye EK katmandır —
override DEĞİLDİR. Kurumsal tonlu bir marka TikTok'ta bile kurumsal kalır,
yalnızca platformun yapısına uyarlar. Çatışma durumunda marka tonu kazanır.

YASAK — ÜRÜN BİLGİSİNDE OLMAYAN HİÇBİR ŞEYİ İCAT ETME:
- Sayısal iddia uydurma ('%300 artış', '30 saatten 2 saate').
- Teknik özellik icat etme (malzeme, menşei, üretim tekniği, bileşen).
- Dolaylı fayda/konfor/performans iddiası icat etme (dayanıklılık, rahatlık,
  verimlilik, hız — ürün bilgisinde açıkça belirtilmemişse yazma).
- Hayali müşteri hikayesi/yorumu uydurma (fabricated testimonial yasak).
- Sertifika, ödül, test sonucu, menşei bilgisi icat etme.
KURAL: Sana verilen ürün bilgisini (ad, açıklama, etiketler) tek doğruluk
kaynağı olarak al. Bu bilgide olmayan hiçbir somut iddiayı yazma — ne teknik
ne duygusal. Genel ama dürüst ifadeler kullanabilirsin, uydurarak
zenginleştirmeye çalışma.

ÇIKTI FORMATI: Her zaman JSON döndür. Başka açıklama, preamble veya markdown
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
    parts: list[str] = []

    # Brand info
    brand_name = brand.get("name") or ""
    parts.append(f"Marka: {brand_name}")
    if brand.get("description"):
        parts.append(f"Marka açıklaması: {brand['description']}")
    if brand.get("website_url"):
        parts.append(f"Marka web sitesi: {brand['website_url']}")

    tonality = brand_kit.get("tonality") or "professional"
    parts.append(f"Marka tonu: {tonality}")

    colors = brand_kit.get("colors") or []
    if isinstance(colors, dict):
        colors_str = ", ".join(f"{k}: {v}" for k, v in colors.items() if v)
    elif isinstance(colors, list):
        colors_str = ", ".join(str(c) for c in colors if c)
    else:
        colors_str = str(colors)
    if colors_str:
        parts.append(f"Marka renkleri: {colors_str}")
        parts.append(
            "\n⚠️ GÖRSEL ÜRETİM KURALI (image_prompt için ZORUNLU): "
            "Üreteceğin image_prompt mutlaka yukarıdaki marka renklerini "
            "(HEX kodları ile) içermeli. Arka plan, yüzey, ışık tonları veya "
            "vurgu renkleri bu paletten seçilmeli. Beige, off-white, pastel "
            "veya genel stüdyo tonları kullanma — marka renklerini net şekilde "
            "belirt. Örnek kalıp: 'background in {marka mor tonu #HEX}, "
            "accent lighting with {ikincil renk #HEX}'."
        )

    hashtags = brand_kit.get("hashtags") or []
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
    platforms: list[str] | None,
    product: dict | None = None,
) -> str:
    """Tier 3 — dynamic content (not cached)."""
    parts: list[str] = []

    if user_prompt:
        parts.append(
            "=== KULLANICI İSTEĞİ (EN YÜKSEK ÖNCELİK — ŞABLON DEFAULT'LARINI GEÇERSİZ KILAR) ==="
        )
        parts.append(user_prompt)
        parts.append("=== KULLANICI İSTEĞİ SONU ===\n")

    # Ürün adı/açıklama/etiketler şablon alanlarına (ana_konu, one_cikan_ozellik)
    # frontend tarafından pre-fill edildiği için buraya yazılmaz — YAPISAL VERİLER
    # bloğundan zaten Claude'a ulaşıyor. Sadece image-edit akışı için özel kural gerekli.
    if product and product.get("image_url"):
        parts.append(
            "⚠️ image_prompt İÇİN ÖZEL KURAL: Bu içerikte ürünün mevcut "
            "görseli fal.ai image-edit modeline referans olarak iletilecek. "
            "Ürünün kendisini (şekil, renk, malzeme) image_prompt'ta YENİDEN "
            "TARİF ETME — model referans görselden alacak. Sadece sahne, "
            "kompozisyon, arka plan, ışık, atmosfer ve stil tarif et. "
            "Örnek kalıp: 'Place the product on [surface] in [environment], "
            "[lighting style], [mood/atmosphere], [composition notes].'"
        )

    if template and template_fields:
        parts.append("=== YAPISAL VERİLER ===")
        for field in template.formFields:
            value = template_fields.get(field.id)
            if value is not None and value != "":
                suffix = f" {field.suffix}" if field.suffix else ""
                parts.append(f"{field.label}: {value}{suffix}")
        parts.append("=== VERİ SONU ===\n")

    if rag_context:
        parts.append(f"=== REFERANS DOKÜMAN ===\n{rag_context}\n=== DOKÜMAN SONU ===\n")

    if template:
        priority = ["user_prompt", *[p for p in template.prompt.priority if p != "user_prompt"]]
        parts.append(
            f"ÖNCELİK SIRASI (çatışma durumunda — user_prompt her zaman en tepede): "
            f"{' > '.join(priority)}\n"
        )

    if platforms:
        overrides = template.platformOverrides if template else None
        parts.append(build_platform_instructions(overrides, platforms))

    return "\n".join(parts)


def _resolve_platform_rules(platform: str, override) -> dict:
    """Merge PLATFORM_DEFAULTS[platform] with optional template-level override.

    Template override fields that are None fall back to defaults.
    Platforms not in PLATFORM_DEFAULTS return an empty dict (caller should skip).
    """
    defaults = PLATFORM_DEFAULTS.get(platform, {})
    rules = dict(defaults)
    if override is None:
        return rules

    for key in ("captionStyle", "maxHashtags", "useFirstComment", "toneAdjustment", "additionalGuidance"):
        value = getattr(override, key, None)
        if value is not None:
            rules[key] = value
    return rules


def build_platform_instructions(
    overrides: dict | None,
    platforms: list[str],
) -> str:
    """Build per-platform caption rules for Claude.

    PLATFORM_DEFAULTS covers every supported platform; template-level overrides
    (if any) override specific fields. Emits rules for EVERY platform so Claude
    fills all `platform_captions` keys.
    """
    style_map = {
        "long": "200-500 kelime, profesyonel, detaylı",
        "medium": "50-150 kelime, emoji kullanılabilir",
        "short": "40-100 karakter, vurucu, hook'lu",
    }
    overrides = overrides or {}

    parts = ["=== PLATFORM-SPESİFİK CAPTION'LAR ==="]
    parts.append(
        "Aşağıdaki her platform için AYRI caption üret. "
        "Response'da JSON formatında `platform_captions` objesi dön, "
        "her platform için ayrı key ile."
    )

    for platform in platforms:
        rules_dict = _resolve_platform_rules(platform, overrides.get(platform))
        if not rules_dict:
            continue

        lines = [f"\n{platform}:"]
        caption_style = rules_dict.get("captionStyle")
        if caption_style:
            lines.append(f"  Uzunluk: {style_map.get(caption_style, caption_style)}")
        max_hashtags = rules_dict.get("maxHashtags")
        if max_hashtags:
            lines.append(f"  Max hashtag: {max_hashtags}")
        if rules_dict.get("useFirstComment"):
            lines.append(
                f"  Hashtag'leri CAPTION'DAN AYIR, response'da "
                f"`{platform}.first_comment` key'inde dön"
            )
        tone = rules_dict.get("toneAdjustment")
        if tone:
            lines.append(f"  Ton ayarlama: {tone}")
        extra = rules_dict.get("additionalGuidance")
        if extra:
            lines.append(f"  Ek talimat: {extra}")

        parts.append("\n".join(lines))

    parts.append("\n=== PLATFORM BİTİŞ ===")
    return "\n".join(parts)
