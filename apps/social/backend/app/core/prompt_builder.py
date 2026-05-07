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
    "linkedin":  {"captionStyle": "medium", "maxHashtags": 5,  "useFirstComment": False},
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
sıralamasını GEÇERSİZ KILAR. Kullanıcı özel bir sahne/ortam/stil tarif
ediyorsa şablon default'larını bırak ve kullanıcının istediği sahneyi
(model, sahne, kompozisyon, arka plan) image_prompt'a AYNEN yansıt.
Kullanıcı özellikle belirtmediği sürece şablon default'larına uy;
belirttiğinde kullanıcı kazanır.

✍️ YAZIM KURALI (caption gövdesi + CTA için — zorunlu)

⚠️ ÖN KOŞUL: Aşağıdaki kuralları uygularken SADECE sana verilen ürün
bilgisini (ad, açıklama, etiketler) kullan. Bilgide olmayan özellik, fayda
veya iddia icat etme — kuralları uygulamak için bilgi uydurmak da yasak.

1. FAYDA > ÖZELLİK
   Ürün/hizmetin özelliğini değil, o özelliğin müşteriye ne kazandırdığını yaz.
   AMA: Sadece ürün bilgisinde OLAN özelliklerden fayda çıkar.
   ❌ "[teknik özelliği listeleme]"
   ✅ "[o özellik müşterinin hayatında neyi değiştiriyor]"

2. SOMUTLUK > SOYUTLUK
   "Kalite", "premium", "modern", "inovatif", "en iyi" gibi belirsiz sözler
   KULLANMA. Yerine ürün bilgisindeki somut detayı koy.
   ❌ "[belirsiz övgü: kaliteli, premium, en iyi]"
   ✅ "[bilgide geçen spesifik özellik veya ölçü]"
   ⚠️ Somut detay ürün bilgisinde YOKSA uydurma. Belirsiz sözden kaçınmak
   için bilgi icat etmek de yasak. Bilgi azsa içerik kısa kalsın.

3. AKTİF SES > EDİLGEN SES
   ❌ "[edilgen: yapılır, oluşturulur, gönderilir]"
   ✅ "[etken: yap, oluştur, gönder — özneyi belirt]"

4. MÜŞTERİ DİLİ > MARKA JARGONU
   Müşterinin gerçek hayatta kullandığı kelimeleri kullan.
   ❌ "[teknik/jargon ifade: optimize, ergonomik, entegre]"
   ✅ "[müşterinin aynı şeyi anlatırken kullanacağı günlük dil]"

5. CTA FORMÜLÜ: [Eylem Fiili] + [Ne Alacak] + [Opsiyonel Ek Bilgi]
   ❌ "Öğren", "İncele", "Tıkla"
   ✅ "Kataloğu İndir", "Ücretsiz Deneyin", "Koltuğunu Ayır (son 3 kaldı)"

📱 PLATFORM TON REHBERİ
PLATFORM_DEFAULTS caption uzunluğu + hashtag sayısı + first_comment kuralını
belirler. Bu blok her platformun üslup/yapı tonunu verir:

- INSTAGRAM: görsel hikaye taşıyıcı. Hook görseli destekler, emoji uygun.
  Caption gövdesi duygusal tonda olabilir. Hashtag'ler first_comment'e.
- LINKEDIN: B2B, profesyonel ton. Hook veriye/gözleme dayalı — AMA gözlem
  uydurma, sektör araştırması/veri/trend icat etme. Paragraf yapısı (kısa
  satırlar arası boşluk). Ürün hakkında verilmeyen bilgiyi "tasarım sürecimiz",
  "perakende gözlemimiz", "tüketici araştırmamız" gibi kaynaksız otoriteyle
  sunma. Emoji az.
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

🧠 PSİKOLOJİ PRENSİPLERİ (caption stratejisi için)

Aşağıdaki prensipler caption'ın yapısına yön verir. Hepsini her post'ta
kullanma — içerik türüne ve kullanıcı isteğine uygun olanları seç.

1. SOMUTLUK (Specificity)
   Soyut iddia inandırıcı değil, somut detay inandırıcıdır.
   "İyi sonuç" değil, "ilk hafta 3 yeni sipariş".
   Uygulama: Her vaadin arkasında spesifik durum/rakam/zaman olmalı.
   Gerçek değilse kullanma (YASAK kuralı hatırlatması).

2. LOSS AVERSION (kayıp duyarlılığı)
   İnsanlar 100 TL kazanmaktan çok, 100 TL kaybetmekten korkar.
   Uygulama: Kullanıcının "kaçırma" tarafını göster — ama SAHTE scarcity
   yaratma (gerçek stok/süre yoksa kullanma, YASAK).
   ✅ "Bu hafta sonu sipariş verenler pazartesi elinde." (gerçek kargo süresi)
   ❌ "Son 3 ürün!" (stoktan emin değilse)

3. SOCIAL PROOF
   İnsanlar ne yapacağını, başkalarının ne yaptığına bakarak anlar.
   Uygulama: Sayı/topluluk/referans varsa caption'a doğal şekilde yerleştir.
   ✅ "300+ işletmenin tercih ettiği sistem"
   ❌ "Herkes bizi tercih ediyor" (soyut)

🎯 PSİKOLOJİ UYGULAMA KURALI (hangi prensibi ne zaman kullan)

- SATIŞ/PROMOSYON ODAKLI post (ürün kartı, kampanya, indirim):
  Specificity zorunlu — soyut iddia yasak, somut detay/durum gerekli.
  Loss Aversion + Social Proof yalnızca GERÇEK sayı/stok/süre varsa kullan.
  Sahte scarcity yaratma (veri yoksa bu prensipleri sokma).

- BİLGİ/HİKAYE/KURUMSAL post (hakkımızda, ekip, biliyor muydunuz, alıntı):
  Satış dili ve scarcity kesinlikle sokma — içeriğin doğal tonunu bozar.

- İçerik türünü kullanıcı isteği (user_prompt) + şablon adı + yapısal
  verilerden çıkar.

- Emin değilsen HİÇBİR PRENSİP SOKMA — caption'ı doğal akışa bırak.
  Yazım kuralları ve platform ton rehberi tek başına yeterli.

YASAK — ÜRÜN BİLGİSİNDE OLMAYAN HİÇBİR ŞEYİ İCAT ETME:
- Sayısal iddia uydurma ('%300 artış', '30 saatten 2 saate').
- Teknik özellik icat etme (malzeme, menşei, üretim tekniği, bileşen).
- Dolaylı fayda/konfor/performans iddiası icat etme (dayanıklılık, rahatlık,
  verimlilik, hız — ürün bilgisinde açıkça belirtilmemişse yazma).
- Hayali müşteri hikayesi/yorumu uydurma (fabricated testimonial yasak).
- Sertifika, ödül, test sonucu, menşei bilgisi icat etme.
KURAL: Sana verilen ürün bilgisini (ad, açıklama, etiketler) tek doğruluk
kaynağı olarak al. Bu bilgide olmayan hiçbir iddiayı yazma — ne teknik ne
duygusal ne sektörel. "Tasarladık/gözlemledik/araştırdık" gibi kurgusal
otorite cümleleri de yasak. Bu kural caption, hashtag ve image_prompt
dahil TÜM çıktılar için geçerli — hashtag'lere bile ürün bilgisinde
olmayan özellik sızdırma. İçerik kısa kalsa bile dürüst kalsın.

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


_SPECIAL_DAY_CATEGORY_TR = {
    "national": "milli/ulusal",
    "religious": "dini",
    "commercial": "ticari/duygusal",
}

_SPECIAL_DAY_TONE_HINTS = {
    "national": (
        "Ton: vatan/gurur/birlik. Markanın bu güne saygısı esas. "
        "Tarihi figür için uydurma alıntı/söz YASAK. "
        "Aşırı slogan zinciri, dolu duygu sömürüsü kullanma."
    ),
    "religious": (
        "Ton: saygı + samimi dilek. 'Bayramınız mübarek olsun' ailesi uygun. "
        "Dini açıklama/hüküm yapma, mezhep/yorum tartışmasına girme."
    ),
    "commercial": (
        "Ton: duygu + kişisel bağlantı. Promosyon/satış dili YASAK. "
        "İndirim/kampanya cümlesi sokma — yönlendirme sadece kullanıcı "
        "cta_url doldurduysa caption'ın son satırına gelir."
    ),
}


def build_dynamic_content(
    template: Template | None,
    template_fields: dict | None,
    user_prompt: str | None,
    rag_context: str | None,
    platforms: list[str] | None,
    product: dict | None = None,
    special_day: dict | None = None,
    subject_reference_provided: bool = False,
) -> str:
    """Tier 3 — dynamic content (not cached).

    `special_day`: {"name": "Anneler Günü", "category": "commercial"} formatında.
    Doluysa caption + image_prompt'ı tatil tonuna yönlendiren ayrı bir blok eklenir.

    `subject_reference_provided`: True ise kullanıcı bir referans görsel yüklemiş
    (Atatürk fotoğrafı, kurucu portre vb.) → Nano Banana 2 edit ref'i olacak.
    image_prompt merkezdeki kişiyi/objeyi tarif ETMEMELI; sahnenin etrafını,
    ışığı, atmosferi, ek figürleri tarif etmeli — model image input'tan kişiyi
    zaten görüyor, prompt'ta tarif kafa karıştırır ve identity drift yaratır.
    """
    parts: list[str] = []

    if subject_reference_provided:
        parts.append("=== REFERANS GÖRSEL BAĞLAMI (image_prompt için kritik kural) ===")
        parts.append(
            "Kullanıcı sahneye yerleştirilecek bir referans görsel (kişi/obje) yükledi. "
            "Görsel üretimi Nano Banana 2 edit ile yapılacak — model bu referans "
            "görseli zaten girdi olarak alıyor."
        )
        parts.append(
            "image_prompt YAZIMINDA KURAL:\n"
            "- Merkezdeki kişiyi/objeyi 'the reference subject' veya 'the person in "
            "the photo' olarak bırak; YÜZ, KIYAFET, FİZİKSEL ÖZELLİK TARİF ETME.\n"
            "- Sahnenin etrafını tarif et: ışık, atmosfer, arka plan, etrafındaki "
            "kişi/obje, kompozisyon, kamera açısı, ruh hali.\n"
            "- 'Atatürk', 'kurucu' gibi spesifik isimleri prompt'a yazma — model image "
            "input'tan zaten tanıyor; prompt'ta isim aynı kişinin farklı bir versiyonunu "
            "üretmesine yol açabilir.\n"
            "- Örnek doğru: 'the reference subject standing in front of a large Turkish "
            "flag at golden hour, surrounded by attentive young people in soft focus'.\n"
            "- Örnek YANLIŞ: 'Atatürk in his iconic kalpak chatting with students' "
            "(yüz tarif edildi → drift riski)."
        )
        parts.append("=== REFERANS GÖRSEL BAĞLAMI SONU ===\n")

    if special_day and special_day.get("name"):
        name = special_day["name"]
        category = special_day.get("category") or ""
        category_tr = _SPECIAL_DAY_CATEGORY_TR.get(category, category or "genel")
        tone_hint = _SPECIAL_DAY_TONE_HINTS.get(category, "")
        parts.append("=== ÖZEL GÜN BAĞLAMI (caption + image_prompt için yön verici) ===")
        parts.append(f"Tatil/özel gün: {name}")
        parts.append(f"Kategori: {category_tr}")
        if tone_hint:
            parts.append(tone_hint)
        parts.append(
            "Bu içerik bir kutlama/tebrik postudur — ürün satış formülü uygulanmaz. "
            "Caption tatilin duygusal anlamını taşımalı, marka kimliği saygıyla "
            "sezdirilmeli. image_prompt tatilin sembolizmini + marka renklerini "
            "birleştirmeli (ürünü değil, tatil atmosferini görselleştir — ürün "
            "modunda image-edit zaten ürünü sahneye yerleştirir)."
        )
        parts.append("=== ÖZEL GÜN BAĞLAMI SONU ===\n")

    if user_prompt:
        parts.append(
            "=== KULLANICI İSTEĞİ (EN YÜKSEK ÖNCELİK — ŞABLON DEFAULT'LARINI GEÇERSİZ KILAR) ==="
        )
        parts.append(user_prompt)
        parts.append("=== KULLANICI İSTEĞİ SONU ===\n")

    # Ürün adı/açıklama/etiketler — template'in formFields listesinde ana_konu yoksa
    # (ör. kısa video genel şablonu — sadeleştirme amacıyla bu alanlar kaldırıldı)
    # Claude'a ayrı bir ÜRÜN BİLGİSİ bloğu üzerinden iletilir. Image/carousel template'lerinde
    # ana_konu field'ı duruyor → frontend pre-fill üzerinden YAPISAL VERİLER'de gider, burası skip.
    if product:
        template_field_ids = {f.id for f in template.formFields} if template else set()
        if "ana_konu" not in template_field_ids:
            parts.append("=== ÜRÜN/HİZMET BİLGİSİ ===")
            if product.get("name"):
                parts.append(f"Ad: {product['name']}")
            if product.get("description"):
                parts.append(f"Açıklama: {product['description']}")
            tags = product.get("tags") or []
            if isinstance(tags, list) and tags:
                parts.append(f"Etiketler: {', '.join(str(t) for t in tags)}")
            parts.append("=== ÜRÜN BİLGİSİ SONU ===\n")

        if product.get("image_url"):
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
