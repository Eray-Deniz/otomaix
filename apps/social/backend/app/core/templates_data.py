"""Phase 7 — Sektör-Spesifik Şablon Tanımları (backend tek kaynak).

22 şablon (e-ticaret 4, yemek 4, sağlık 3, hizmet 3, genel 8) +
12 sektör guidance entry. Spec: `~/otomaix/docs/07-social-template-system.md` §6.

Frontend bu veriyi `GET /templates` üzerinden çeker ve 1 saat cache eder.
"""
from app.models.templates import (
    ImageTextOverlaySpec,
    PlatformOverride,
    Template,
    TemplateDefaults,
    TemplateFormField,
    TemplateOutput,
    TemplatePrompt,
)


# ─── Şablon kataloğu ────────────────────────────────────────────────────────

TEMPLATES: dict[str, Template] = {}


# ─── 6.1 E-Ticaret (4) ──────────────────────────────────────────────────────

TEMPLATES["eticaret-urun-karti"] = Template(
    id="eticaret-urun-karti",
    name="Ürün Kartı",
    description="Tek ürün için özellik vurgulu tanıtım",
    icon="🛒",
    sectors=["e-ticaret-perakende"],
    contentTypes=["image"],
    order=10,
    formFields=[
        TemplateFormField(id="product_name", label="Ürün Adı", type="text", required=True,
            placeholder="örn. Apple iPhone 15 128GB", validation={"maxLength": 120}, group="Ürün Bilgisi"),
        TemplateFormField(id="key_feature", label="Öne Çıkan Özellik", type="text", required=False,
            placeholder="örn. A17 Pro çip, 48MP kamera", validation={"maxLength": 200}, group="Ürün Bilgisi"),
        TemplateFormField(id="cta_url", label="Yönlendirme Linki (opsiyonel)", type="url", required=False,
            placeholder="https://... (ürün, kampanya veya site linki)",
            helpText="Gönderiyi gören kişiyi bir yere yönlendirmek isterseniz linki buraya yapıştırın. Boş bırakırsanız caption yönlendirme yapmaz.",
            group="Yönlendirme"),
        TemplateFormField(id="cta_label", label="Çağrı Metni", type="text", required=False,
            defaultValue="Şimdi Keşfet",
            placeholder="Şimdi Keşfet",
            validation={"maxLength": 40},
            helpText="Linkin üzerine yazılacak kısa çağrı metni. Örn: 'Şimdi Keşfet', 'İncele', 'Sipariş Ver'.",
            group="Yönlendirme"),
    ],
    output=TemplateOutput(aspectRatioSuggestion="4:5"),
    prompt=TemplatePrompt(
        guidance=(
            "E-ticaret ürün kartı şablonu. Tek ürünü öne çıkaran statik sosyal medya görseli üretir.\n\n"
            "Görsel yönergesi (image_prompt için): Saf ürün fotoğrafçılığı — ürün görselin ana öznesi ve "
            "en az %60'ı olmalı. Stüdyo çekimi, temiz arka plan (marka renklerinin HEX kodlarıyla), "
            "yumuşak ışık, yüksek detay. İnsan modeli, lifestyle sahnesi, elbise/kıyafet vurgusu KULLANMA — "
            "ürün küçükse (ayakkabı, takı, telefon vb.) yakın plan/hero angle kullan. "
            "image_prompt'ta logo, marka rozeti, özellik rozeti, metin katmanı veya yazı "
            "TARIF ETME — gerçek logo ve caption'lar post-process/platform tarafında ekleniyor.\n\n"
            "Caption formülü: Hook (ürün adı + faydası) → Özellik vurgusu → CTA. "
            "Abartılı iddia kullanma. Fiyat ve indirim bilgisi bu şablonda kullanılmaz.\n\n"
            "CTA (yönlendirme) kuralı:\n"
            "- Kullanıcı 'Yönlendirme Linki' doldurduysa: caption'ın son satırında çağrı metnini "
            "(cta_label) kullan ve platforma göre davran:\n"
            "  • Instagram/TikTok/Threads gibi caption-link'in tıklanmadığı platformlarda: "
            "caption son satırı '👉 {cta_label} — profilimizdeki linkten ulaşabilirsiniz' "
            "şeklinde olsun. useFirstComment aktifse URL'yi first_comment bloğuna düz metin "
            "olarak koy (kopyalanabilsin).\n"
            "  • LinkedIn/Facebook/Twitter/Pinterest gibi linkin tıklandığı platformlarda: "
            "caption son satırı '👉 {cta_label}: {cta_url}' şeklinde, URL'yi direkt caption'a yaz.\n"
            "- Kullanıcı link doldurmadıysa: yönlendirme satırı ekleme, caption ürün özellik "
            "vurgusu ile bitsin. Sahte bir 'link bio'da' satırı uydurma."
        ),
        priority=["form_fields", "brand_kit", "rag_docs"],
    ),
    defaults=TemplateDefaults(
        suggestedHashtags=["yenilik", "ürün", "keşfet", "alışveriş"],
    ),
    platformOverrides={
        "instagram": PlatformOverride(captionStyle="medium", maxHashtags=15, useFirstComment=True),
        "linkedin": PlatformOverride(captionStyle="long", maxHashtags=5,
            toneAdjustment="Daha kurumsal, satış dili yumuşatılmış"),
        "twitter": PlatformOverride(captionStyle="short", maxHashtags=2),
    },
    imageTextOverlay=ImageTextOverlaySpec(
        fields=["product_name", "key_feature"],
        position="bottom-left",
    ),
    tags=["ürün", "tanıtım", "keşfet"],
)


TEMPLATES["eticaret-kampanya-banner"] = Template(
    id="eticaret-kampanya-banner",
    name="Kampanya Banner",
    description="Mevsimsel/özel gün kampanyaları için",
    icon="🎉",
    sectors=["e-ticaret-perakende"],
    contentTypes=["image"],
    order=20,
    formFields=[
        TemplateFormField(id="campaign_name", label="Kampanya Adı", type="text", required=True,
            placeholder="örn. Ramazan İndirimi, Yaz Fırsatları", validation={"maxLength": 60}),
        TemplateFormField(id="discount_percent", label="İndirim Oranı", type="number", required=False,
            suffix="%", validation={"min": 1, "max": 99}),
        TemplateFormField(id="start_date", label="Başlangıç", type="text", required=False,
            placeholder="örn. 15 Mart"),
        TemplateFormField(id="end_date", label="Bitiş", type="text", required=False,
            placeholder="örn. 30 Mart"),
        TemplateFormField(id="coupon_code", label="Kupon Kodu", type="text", required=False,
            placeholder="örn. YAZ2026", validation={"maxLength": 30}),
    ],
    output=TemplateOutput(aspectRatioSuggestion="1:1"),
    prompt=TemplatePrompt(
        guidance=(
            "E-ticaret kampanya banner'ı. Göz alıcı, enerjik bir kampanya duyurusu.\n\n"
            "Görsel yönergesi: Canlı renkler, büyük tipografi ile indirim oranı ve "
            "kampanya adı öne çıksın. Arka planda kampanyayla ilgili grafik/desenler "
            "(ör. Ramazan teması için hilal, yaz için güneş).\n\n"
            "Caption formülü: Kampanya hook → Fayda (ne kadar indirim) → Süre → CTA."
        ),
        priority=["form_fields", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=["Fırsatları kaçırmayın", "Şimdi alışverişe başlayın"],
        suggestedHashtags=["kampanya", "indirim", "fırsat"],
    ),
    platformOverrides={
        "instagram": PlatformOverride(captionStyle="medium", maxHashtags=15),
        "facebook": PlatformOverride(captionStyle="medium", maxHashtags=5),
    },
)


TEMPLATES["eticaret-stok-sayaci"] = Template(
    id="eticaret-stok-sayaci",
    name="Stok Sayacı",
    description="Sınırlı stok, aciliyet yaratan içerik",
    icon="⏰",
    sectors=["e-ticaret-perakende"],
    contentTypes=["image"],
    order=30,
    formFields=[
        TemplateFormField(id="product_name", label="Ürün Adı", type="text", required=True,
            validation={"maxLength": 120}),
        TemplateFormField(id="remaining_stock", label="Kalan Stok", type="number", required=True,
            suffix="adet", validation={"min": 1}),
        TemplateFormField(id="price", label="Fiyat", type="number", required=False, suffix="TL",
            helpText="Opsiyonel — fiyat girmezseniz caption 'link bio'da', 'Detaylar için DM' gibi yumuşak yönlendirme kullanır."),
    ],
    output=TemplateOutput(aspectRatioSuggestion="1:1"),
    prompt=TemplatePrompt(
        guidance=(
            "Sınırlı stok aciliyet içeriği. 'Kaçırma' hissi yaratır ama sahte urgency "
            "kullanılmaz — gerçek stok bilgisi verilir.\n\n"
            "Görsel yönergesi: Ürün merkezde, 'Son N adet!' rozeti dikkat çekici. "
            "Kırmızı/turuncu aksan rengi olabilir (aciliyet).\n\n"
            "Caption formülü: Aciliyet hook → Ürün → Stok bilgisi → CTA. "
            "Yasaklar: 'Son 1 adet!' gibi sahte urgency (stok gerçekten öyle değilse).\n\n"
            "Fiyat yoksa: Caption'da fiyat satırını atla, sadece stok aciliyetine odaklan. "
            "CTA 'Hemen al' yerine 'Link bio'da', 'Detaylar için DM' gibi yumuşak yönlendirme kullan. "
            "Image prompt'unda fiyat rozeti yerine sadece 'Son N adet!' rozeti kalsın."
        ),
        priority=["form_fields", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=["Kaçırma", "Hemen al"],
        suggestedHashtags=["sonstok", "sınırlı", "hızlı"],
    ),
    platformOverrides={
        "instagram": PlatformOverride(captionStyle="short", maxHashtags=10),
    },
)


TEMPLATES["eticaret-kombin-set"] = Template(
    id="eticaret-kombin-set",
    name="Kombin / Set Önerisi",
    description="Birbirini tamamlayan ürün seti",
    icon="👗",
    sectors=["e-ticaret-perakende"],
    contentTypes=["image"],
    order=40,
    formFields=[
        TemplateFormField(id="set_theme", label="Set Teması", type="text", required=True,
            placeholder="örn. Yaz Tatili Kombini, Ofis Şık", validation={"maxLength": 80}),
        TemplateFormField(id="products", label="Ürünler", type="textarea", required=True,
            placeholder="Her satıra bir ürün. Örn:\nElbise - 499 TL\nÇanta - 299 TL\nAyakkabı - 399 TL",
            validation={"maxLength": 500}),
        TemplateFormField(id="total_price", label="Toplam Fiyat", type="number", required=False, suffix="TL"),
    ],
    output=TemplateOutput(aspectRatioSuggestion="4:5"),
    prompt=TemplatePrompt(
        guidance=(
            "Birden fazla ürünün bir araya getirildiği kombin/set önerisi görseli.\n\n"
            "Görsel yönergesi: Flat-lay veya grid düzende ürünler bir arada, uyumlu "
            "renkler, profesyonel styling. Set teması görselin başlığında.\n\n"
            "Caption formülü: Set teması hook → Ürünler listesi → Toplam fiyat → CTA."
        ),
        priority=["form_fields", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=["Sete tıkla", "Tüm kombini incele"],
        suggestedHashtags=["kombin", "set", "stil", "moda"],
    ),
    platformOverrides={
        "instagram": PlatformOverride(captionStyle="medium", maxHashtags=15),
        "pinterest": PlatformOverride(captionStyle="medium", maxHashtags=10),
    },
)


# ─── 6.2 Yemek & Gıda (4) ───────────────────────────────────────────────────

TEMPLATES["yemek-gunun-menusu"] = Template(
    id="yemek-gunun-menusu",
    name="Günün Menüsü",
    description="Öğle/akşam menü duyurusu",
    icon="🍽️",
    sectors=["yemek-gida"],
    contentTypes=["image"],
    order=50,
    formFields=[
        TemplateFormField(id="meal_type", label="Öğün", type="select", required=True,
            options=[
                {"value": "kahvaltı", "label": "Kahvaltı"},
                {"value": "öğle", "label": "Öğle"},
                {"value": "akşam", "label": "Akşam"},
            ], group="Zaman"),
        TemplateFormField(id="main_dish", label="Ana Yemek", type="text", required=True,
            placeholder="örn. Kuzu tandır, enginar dolması", validation={"maxLength": 120},
            group="Menü"),
        TemplateFormField(id="side_dish", label="Yanında", type="text", required=False,
            placeholder="örn. Bulgur pilavı, cacık, salata", validation={"maxLength": 200},
            group="Menü"),
        TemplateFormField(id="price", label="Menü Fiyatı", type="number", required=False,
            suffix="TL",
            helpText="Opsiyonel — fiyat girmezseniz caption 'link bio'da', 'Detaylar için DM' gibi yumuşak yönlendirme kullanır.",
            group="Fiyat"),
    ],
    output=TemplateOutput(aspectRatioSuggestion="4:5"),
    prompt=TemplatePrompt(
        guidance=(
            "Restoran günün menüsü duyurusu. İştah açıcı görsel, sıcak ton.\n\n"
            "Görsel yönergesi: Yemeğin profesyonel food fotoğrafı, doğal aydınlatma, "
            "tahta/tabak üzerinde servis. Menü detayları görselde değil caption'da "
            "detaylandırılır.\n\n"
            "Caption formülü: Duygu hook (tat/aroma) → Menü detayları → Fiyat → CTA.\n\n"
            "Fiyat yoksa: Caption'da fiyat satırını atla. CTA 'Rezervasyon için' yerine "
            "'Detaylar için DM', 'Link bio'da menü' gibi yumuşak yönlendirme kullan. "
            "Image prompt'unda fiyat etiketi isteme — yemek fotoğrafı ve sıcak atmosfer öne çıksın."
        ),
        priority=["form_fields", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=["Rezervasyon için", "Masanızı ayırın"],
        suggestedHashtags=["gününmenüsü", "yemek", "restoran", "tatlar"],
    ),
    platformOverrides={
        "instagram": PlatformOverride(captionStyle="medium", maxHashtags=15, useFirstComment=True),
        "facebook": PlatformOverride(captionStyle="medium", maxHashtags=5),
    },
)


TEMPLATES["yemek-yeni-lezzet"] = Template(
    id="yemek-yeni-lezzet",
    name="Yeni Lezzet",
    description="Menüye eklenen yeni yemek tanıtımı",
    icon="✨",
    sectors=["yemek-gida"],
    contentTypes=["image"],
    order=60,
    formFields=[
        TemplateFormField(id="dish_name", label="Yemek Adı", type="text", required=True,
            validation={"maxLength": 100}),
        TemplateFormField(id="description", label="Açıklama", type="textarea", required=True,
            placeholder="Malzemeler, hazırlık özelliği, tat notaları",
            validation={"maxLength": 400}),
        TemplateFormField(id="price", label="Fiyat", type="number", required=False, suffix="TL"),
    ],
    output=TemplateOutput(aspectRatioSuggestion="1:1"),
    prompt=TemplatePrompt(
        guidance=(
            "Yeni menü öğesi tanıtımı. 'Denemek zorundasın' hissi yaratır.\n\n"
            "Görsel yönergesi: Yemek close-up, detaylı doku görünümü. 'YENİ' rozeti "
            "veya benzer bir işaret köşede. Atmosfer iştah açıcı.\n\n"
            "Caption formülü: Yenilik hook → Yemek açıklaması → Tat notaları → CTA."
        ),
        priority=["form_fields", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=["Siz de deneyin", "Tadına bakın"],
        suggestedHashtags=["yenilezzet", "yemek", "tadı", "şeftavsiyesi"],
    ),
    platformOverrides={
        "instagram": PlatformOverride(captionStyle="medium", maxHashtags=15),
    },
)


TEMPLATES["yemek-online-siparis"] = Template(
    id="yemek-online-siparis",
    name="Online Sipariş",
    description="Yemeksepeti/Getir/Trendyol yönlendirmeli",
    icon="🛵",
    sectors=["yemek-gida"],
    contentTypes=["image"],
    order=70,
    formFields=[
        TemplateFormField(id="platforms", label="Hangi platformlarda?", type="text", required=True,
            placeholder="örn. Yemeksepeti, Getir, Trendyol Yemek",
            validation={"maxLength": 200}),
        TemplateFormField(id="offer", label="Özel Teklif", type="text", required=False,
            placeholder="örn. 200 TL üzeri ücretsiz teslimat",
            validation={"maxLength": 150}),
    ],
    output=TemplateOutput(aspectRatioSuggestion="1:1"),
    prompt=TemplatePrompt(
        guidance=(
            "Online sipariş platformlarına yönlendirme. Pratik ve hızlı mesaj.\n\n"
            "Görsel yönergesi: Yemek görseli + platform logoları üstte. Fast-casual "
            "stil, tüketici dostu.\n\n"
            "Caption formülü: Pratik hook → Platform listesi → Teklif (varsa) → CTA."
        ),
        priority=["form_fields", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=["Sipariş verin", "Tıkla ve ye"],
        suggestedHashtags=["onlinesiparis", "evdeyiyelim"],
    ),
    platformOverrides={
        "instagram": PlatformOverride(captionStyle="short", maxHashtags=10),
    },
)


TEMPLATES["yemek-happy-hour"] = Template(
    id="yemek-happy-hour",
    name="Happy Hour",
    description="Belirli saatte geçerli indirim",
    icon="🍹",
    sectors=["yemek-gida"],
    contentTypes=["image"],
    order=80,
    formFields=[
        TemplateFormField(id="time_range", label="Saat Aralığı", type="text", required=True,
            placeholder="örn. 16:00 - 19:00", validation={"maxLength": 40}),
        TemplateFormField(id="offer_detail", label="Teklif Detayı", type="textarea", required=True,
            placeholder="örn. Kahve + tatlı = 100 TL, İkinci içecek bedava",
            validation={"maxLength": 300}),
        TemplateFormField(id="days", label="Geçerli Günler", type="text", required=False,
            placeholder="örn. Pzt-Cuma, Hafta içi"),
    ],
    output=TemplateOutput(aspectRatioSuggestion="1:1"),
    prompt=TemplatePrompt(
        guidance=(
            "Happy Hour promosyonu. Eğlenceli, davetkar ton.\n\n"
            "Görsel yönergesi: İçecek/yemek ile birlikte saat görseli. Renkli "
            "arkaplan, 'Happy Hour' tipografi büyük.\n\n"
            "Caption formülü: Davet hook → Saat aralığı → Teklif → CTA."
        ),
        priority=["form_fields", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=["Uğrayın", "Kaçırmayın"],
        suggestedHashtags=["happyhour", "indirim", "keyif"],
    ),
)


# ─── 6.3 Sağlık (3) — disclaimer zorunlu ────────────────────────────────────

_SAGLIK_DISCLAIMER_LONG = (
    "Bu içerik genel bilgilendirme amaçlıdır ve tıbbi tavsiye yerine geçmez. "
    "Sağlık sorunlarınız için mutlaka uzman hekime danışın."
)
_SAGLIK_DISCLAIMER_SHORT = (
    "Bu içerik genel bilgilendirme amaçlıdır ve tıbbi tavsiye yerine geçmez."
)


TEMPLATES["saglik-biliyor-muydunuz"] = Template(
    id="saglik-biliyor-muydunuz",
    name="Biliyor Muydunuz?",
    description="Eğitici sağlık bilgisi içeriği",
    icon="💡",
    sectors=["saglik"],
    contentTypes=["image"],
    order=90,
    formFields=[
        TemplateFormField(id="topic", label="Konu", type="text", required=True,
            placeholder="örn. Yüksek tansiyon, Diyabet, Hipertansiyon",
            validation={"maxLength": 80}),
        TemplateFormField(id="fact", label="Bilgi", type="textarea", required=True,
            placeholder="Kısa, şaşırtıcı veya az bilinen bir tıbbi gerçek",
            validation={"maxLength": 500}),
        TemplateFormField(id="source", label="Kaynak", type="text", required=False,
            placeholder="örn. WHO 2024 raporu, Dünya Sağlık Örgütü"),
    ],
    output=TemplateOutput(aspectRatioSuggestion="1:1"),
    prompt=TemplatePrompt(
        guidance=(
            "Eğitici sağlık bilgi içeriği. Kanıta dayalı, güvenilir bilgi verme.\n\n"
            "Görsel yönergesi: Temiz, profesyonel görsel. Tıbbi/sağlık teması (stetoskop, "
            "kalp, anatomi çizimi vb.) ama korku yaratmayan. 'Biliyor muydunuz?' soru "
            "işareti tipografi öne çıksın.\n\n"
            "Caption formülü: Merak hook ('Biliyor muydunuz?') → Tıbbi bilgi → "
            "Önlem/öneri → CTA → DISCLAIMER (otomatik)."
        ),
        priority=["form_fields", "rag_docs", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=["Muayene için", "Uzmanla görüşün"],
        suggestedHashtags=["sağlık", "bilgi", "önlem"],
        disclaimer=_SAGLIK_DISCLAIMER_LONG,
    ),
    platformOverrides={
        "instagram": PlatformOverride(captionStyle="medium", maxHashtags=10),
        "linkedin": PlatformOverride(captionStyle="long", maxHashtags=5),
    },
)


TEMPLATES["saglik-doktor-profili"] = Template(
    id="saglik-doktor-profili",
    name="Doktor Profili",
    description="Klinik ekibinden bir uzmanı tanıtım",
    icon="👨‍⚕️",
    sectors=["saglik"],
    contentTypes=["image"],
    order=100,
    formFields=[
        TemplateFormField(id="doctor_name", label="Doktor Adı", type="text", required=True,
            validation={"maxLength": 120}),
        TemplateFormField(id="specialty", label="Uzmanlık", type="text", required=True,
            placeholder="örn. Kardiyoloji, Dermatoloji", validation={"maxLength": 100}),
        TemplateFormField(id="experience_years", label="Deneyim", type="number", required=False,
            suffix="yıl", validation={"min": 1}),
        TemplateFormField(id="key_focus", label="Ana Odak Alanı", type="textarea", required=False,
            placeholder="örn. Kalp ritim bozuklukları, çocuk dermatolojisi",
            validation={"maxLength": 300}),
    ],
    output=TemplateOutput(aspectRatioSuggestion="4:5"),
    prompt=TemplatePrompt(
        guidance=(
            "Klinik uzman tanıtım kartı. Güven verici, profesyonel.\n\n"
            "Görsel yönergesi: Doktor çekiminin yapıldığı orijinal fotoğraf ya da "
            "gelirse beyaz önlükle profesyonel stüdyo çekimi stili. Arka plan sakin/"
            "beyaz. İsim + uzmanlık tipografi ile görselde.\n\n"
            "Caption formülü: Tanıtım hook → Uzmanlık + deneyim → Odak alanı → "
            "Randevu CTA → DISCLAIMER (otomatik)."
        ),
        priority=["form_fields", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=["Randevu al", "Uzmanımızla tanışın"],
        suggestedHashtags=["uzman", "sağlık", "ekip"],
        disclaimer=_SAGLIK_DISCLAIMER_SHORT,
    ),
    platformOverrides={
        "linkedin": PlatformOverride(captionStyle="long", maxHashtags=5),
    },
)


TEMPLATES["saglik-sss"] = Template(
    id="saglik-sss",
    name="SSS (Sıkça Sorulan)",
    description="Hastaların sık sorduğu soruya cevap",
    icon="❓",
    sectors=["saglik"],
    contentTypes=["image"],
    order=110,
    formFields=[
        TemplateFormField(id="question", label="Soru", type="text", required=True,
            placeholder="örn. Grip aşısı yan etki yapar mı?",
            validation={"maxLength": 200}),
        TemplateFormField(id="answer", label="Yanıt", type="textarea", required=True,
            placeholder="Kısa, anlaşılır, kanıta dayalı yanıt",
            validation={"maxLength": 600}),
    ],
    output=TemplateOutput(aspectRatioSuggestion="1:1"),
    prompt=TemplatePrompt(
        guidance=(
            "Hasta sık sorulan sorusuna cevap. Güven verici, anlaşılır dil.\n\n"
            "Görsel yönergesi: Soru işareti veya söz balonu grafiği. Temiz, okunur "
            "tipografi. Soru büyük, yanıt alt kısmında kısa özet.\n\n"
            "Caption formülü: Soru tekrarı → Detaylı yanıt → Önlem/öneri → CTA "
            "→ DISCLAIMER (otomatik)."
        ),
        priority=["form_fields", "rag_docs", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=["Detaylı bilgi için", "Uzmanımızla görüşün"],
        suggestedHashtags=["sss", "sağlık", "bilgi"],
        disclaimer=(
            "Bu içerik genel bilgilendirme amaçlıdır ve tıbbi tavsiye yerine geçmez. "
            "Bireysel durumunuz için mutlaka hekiminize danışın."
        ),
    ),
)


# ─── 6.4 Profesyonel Hizmet (3) ─────────────────────────────────────────────

TEMPLATES["hizmet-son-tarih-hatirlatma"] = Template(
    id="hizmet-son-tarih-hatirlatma",
    name="Son Tarih Hatırlatma",
    description="Vergi beyannamesi, başvuru son tarihi gibi",
    icon="📅",
    sectors=["hizmet"],
    contentTypes=["image"],
    order=120,
    formFields=[
        TemplateFormField(id="deadline_type", label="Hangi Son Tarih?", type="text", required=True,
            placeholder="örn. KDV beyannamesi, yıllık gelir vergisi",
            validation={"maxLength": 150}),
        TemplateFormField(id="deadline_date", label="Son Tarih", type="text", required=True,
            placeholder="örn. 26 Nisan 2026", validation={"maxLength": 50}),
        TemplateFormField(id="consequence", label="Geciktirilirse", type="text", required=False,
            placeholder="örn. Gecikme zammı %3, ceza riski",
            validation={"maxLength": 200}),
    ],
    output=TemplateOutput(aspectRatioSuggestion="1:1"),
    prompt=TemplatePrompt(
        guidance=(
            "Profesyonel hizmetten son tarih hatırlatma (muhasebe, hukuk, danışmanlık). "
            "Uyarıcı ama panik yaratmayan ton.\n\n"
            "Görsel yönergesi: Takvim/saat grafiği, belirgin tarih vurgusu. Sarı/kırmızı "
            "aksan (aciliyet) ama aşırı değil. Profesyonel, kurumsal stil.\n\n"
            "Caption formülü: Hatırlatma hook → Son tarih → Gecikme sonuçları → "
            "Nasıl yardımcı olunur → CTA."
        ),
        priority=["form_fields", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=["Bizimle iletişime geçin", "Hızlıca halledelim"],
        suggestedHashtags=["sontarih", "mevzuat", "profesyonel"],
    ),
    platformOverrides={
        "linkedin": PlatformOverride(captionStyle="long", maxHashtags=5,
            toneAdjustment="Thought leadership tonunda, B2B"),
        "instagram": PlatformOverride(captionStyle="medium", maxHashtags=10),
    },
)


TEMPLATES["hizmet-uzman-tavsiyesi"] = Template(
    id="hizmet-uzman-tavsiyesi",
    name="Uzman Tavsiyesi",
    description="Sektörel insight, mini rehber",
    icon="💼",
    sectors=["hizmet"],
    contentTypes=["image"],
    order=130,
    formFields=[
        TemplateFormField(id="tip_title", label="Tavsiye Başlığı", type="text", required=True,
            placeholder="örn. Yeni şirket kurarken 5 kritik karar",
            validation={"maxLength": 150}),
        TemplateFormField(id="tip_detail", label="Detay", type="textarea", required=True,
            placeholder="Mini rehber — 3-5 madde veya özet anlatım",
            validation={"maxLength": 800}),
    ],
    output=TemplateOutput(aspectRatioSuggestion="4:5"),
    prompt=TemplatePrompt(
        guidance=(
            "Profesyonel hizmet sektöründe thought leadership içerik. Kanıta dayalı, "
            "uzman görüşü hissi.\n\n"
            "Görsel yönergesi: Minimalist, bilgi görseli hissi. Başlık büyük, okunur "
            "tipografi. Marka renklerinde aksanlar. İconografi (takım, ışık ampulü vb.).\n\n"
            "Caption formülü: İnsight hook → Detay (maddeler halinde) → Uygulama "
            "önerisi → CTA."
        ),
        priority=["form_fields", "brand_kit", "rag_docs"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=["Detaylar için iletişim", "Randevu oluşturun"],
        suggestedHashtags=["profesyonel", "tavsiye", "uzman"],
    ),
    platformOverrides={
        "linkedin": PlatformOverride(captionStyle="long", maxHashtags=5),
        "instagram": PlatformOverride(captionStyle="medium", maxHashtags=10),
    },
)


TEMPLATES["hizmet-ekip-uzmanligi"] = Template(
    id="hizmet-ekip-uzmanligi",
    name="Ekip Uzmanlığı",
    description="Firmanızın uzmanlık alanlarını öne çıkarın",
    icon="👔",
    sectors=["hizmet"],
    contentTypes=["image"],
    order=140,
    formFields=[
        TemplateFormField(id="expertise_area", label="Uzmanlık Alanı", type="text", required=True,
            placeholder="örn. Vergi hukuku, dijital dönüşüm danışmanlığı",
            validation={"maxLength": 150}),
        TemplateFormField(id="years_experience", label="Firma Deneyim Yılı", type="number",
            required=False, suffix="yıl"),
        TemplateFormField(id="client_count", label="Hizmet Verilen Müvekkil Sayısı",
            type="number", required=False,
            helpText="Opsiyonel — 'yüzlerce' de yazabilirsiniz"),
        TemplateFormField(id="notable_cases", label="Önemli Çalışmalar", type="textarea",
            required=False, placeholder="İsimsiz, özet (gizlilik için)",
            validation={"maxLength": 400}),
    ],
    output=TemplateOutput(aspectRatioSuggestion="1:1"),
    prompt=TemplatePrompt(
        guidance=(
            "Firma uzmanlık tanıtımı. Güven, yetkinlik, deneyim vurgusu.\n\n"
            "Görsel yönergesi: Profesyonel/kurumsal stil, ekip görseli veya sembolik "
            "görsel (ör. kalem+kağıt+danışmanlık), sakin arkaplan.\n\n"
            "Caption formülü: Uzmanlık hook → Deneyim/rakamlar → Örnek işler "
            "(anonimleştirilmiş) → CTA."
        ),
        priority=["form_fields", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=["İletişim için", "Danışmanlık alın"],
        suggestedHashtags=["uzmanlık", "profesyonel", "deneyim"],
    ),
    platformOverrides={
        "linkedin": PlatformOverride(captionStyle="long", maxHashtags=5),
    },
)


# ─── 6.5 Genel (9) — tüm sektörler için ─────────────────────────────────────

# Varsayılan görsel şablonu — `/icerik-olustur` "Görsel → Devam et" akışında
# otomatik seçilir. Şablon grid'i gösterilmez; kullanıcı doğrudan form'a düşer.
TEMPLATES["genel-gorsel-sablon"] = Template(
    id="genel-gorsel-sablon",
    name="Görsel Şablonu",
    description="Tek konu/ürün/hizmet için statik sosyal medya görseli",
    icon="🖼️",
    sectors=["*"],
    contentTypes=["image"],
    order=1,
    formFields=[
        TemplateFormField(id="ana_konu", label="Ana Konu / Ürün / Hizmet Adı", type="text", required=True,
            placeholder="örn. Yeni koleksiyon, sunduğunuz hizmet, kampanya konusu",
            validation={"maxLength": 120},
            group="Konu"),
        TemplateFormField(id="one_cikan_ozellik", label="Öne Çıkan Vurgu", type="text", required=False,
            placeholder="örn. Konfor ve şıklık bir arada",
            validation={"maxLength": 60},
            helpText="Görsele basılır, kısa pazarlama mesajı olarak yazın. Detaylı caption AI tarafından üretilir.",
            group="Konu"),
        TemplateFormField(id="cta_url", label="Yönlendirme Linki (opsiyonel)", type="url", required=False,
            placeholder="https://... (ürün, kampanya veya site linki)",
            helpText="Gönderiyi gören kişiyi bir yere yönlendirmek isterseniz linki buraya yapıştırın. Boş bırakırsanız caption yönlendirme yapmaz.",
            group="Yönlendirme"),
        TemplateFormField(id="cta_label", label="Çağrı Metni", type="text", required=False,
            defaultValue="Şimdi Keşfet",
            placeholder="Şimdi Keşfet",
            validation={"maxLength": 40},
            helpText="Linkin üzerine yazılacak kısa çağrı metni. Örn: 'Şimdi Keşfet', 'İncele', 'Sipariş Ver'.",
            group="Yönlendirme"),
    ],
    output=TemplateOutput(aspectRatioSuggestion="1:1"),
    prompt=TemplatePrompt(
        guidance=(
            "Genel amaçlı görsel şablonu. Tek bir konuyu/ürünü/hizmeti öne çıkaran "
            "statik sosyal medya görseli üretir.\n\n"
            "Görsel yönergesi (image_prompt için): Marka renklerini (HEX kodlarıyla) "
            "arka plan ve aksan olarak kullan. image_prompt'ta logo, marka rozeti, "
            "özellik rozeti, metin katmanı veya yazı TARIF ETME — gerçek logo ve "
            "caption'lar post-process/platform tarafında ekleniyor.\n\n"
            "🎨 GÖRSEL AÇI KATEGORİSİ (image_prompt yazmadan önce bir açı seç):\n"
            "1. SORUN VURGUSU — problemi görselleştir, öncesi sahnesi, zorluk anı\n"
            "2. SONUÇ VURGUSU — dönüşüm/başarı anı, sonrası sahnesi\n"
            "3. SOSYAL KANIT — topluluk/grup, ortak kullanım sahnesi\n"
            "4. MERAK UYANDIRMA — örtük/kısmi gösterim, detay yakın plan\n"
            "5. ACİLİYET — zamana bağlı gösterge, sınırlı sunum sahnesi\n"
            "6. KİMLİK VURGUSU — hedef kitleye özel ortam ('bu senin için' mesajı)\n"
            "7. AYKIRI YAKLAŞIM — beklenmedik/ters sahne kurgusu\n\n"
            "Açı seçimi kuralı: user_prompt hangi açıyı çağrıştırıyorsa onu seç. "
            "Net değilse ana_konu'nun tonuna bak (satış → sonuç/aciliyet, hikaye → "
            "kimlik/merak). Aynı açıyı sürekli seçme — çeşitlilik önemli.\n\n"
            "Caption formülü: Hook (ana konu + faydası) → Öne çıkan özellik vurgusu → CTA. "
            "Abartılı iddia kullanma.\n\n"
            "CTA (yönlendirme) kuralı:\n"
            "- Kullanıcı 'Yönlendirme Linki' doldurduysa: caption'ın son satırında çağrı metnini "
            "(cta_label) kullan ve platforma göre davran:\n"
            "  • Instagram/TikTok/Threads gibi caption-link'in tıklanmadığı platformlarda: "
            "caption son satırı '👉 {cta_label} — profilimizdeki linkten ulaşabilirsiniz' "
            "şeklinde olsun. useFirstComment aktifse URL'yi first_comment bloğuna düz metin "
            "olarak koy (kopyalanabilsin).\n"
            "  • LinkedIn/Facebook/Twitter/Pinterest gibi linkin tıklandığı platformlarda: "
            "caption son satırı '👉 {cta_label}: {cta_url}' şeklinde, URL'yi direkt caption'a yaz.\n"
            "- Kullanıcı link doldurmadıysa: yönlendirme satırı ekleme, caption ana konu "
            "vurgusu ile bitsin. Sahte bir 'link bio'da' satırı uydurma."
        ),
        priority=["form_fields", "brand_kit", "rag_docs"],
    ),
    defaults=TemplateDefaults(),
    imageTextOverlay=ImageTextOverlaySpec(
        fields=["ana_konu", "one_cikan_ozellik"],
        position="bottom-left",
    ),
    tags=["genel", "görsel"],
)


TEMPLATES["carousel-genel-sablon"] = Template(
    id="carousel-genel-sablon",
    name="Carousel Şablonu",
    description="Çoklu slide ile hikaye anlatan sosyal medya carousel içeriği",
    icon="🎠",
    sectors=["*"],
    contentTypes=["carousel"],
    order=2,
    formFields=[
        TemplateFormField(id="ana_konu", label="Ana Konu / Ürün / Hizmet Adı", type="text", required=True,
            placeholder="örn. Yeni koleksiyon, sunduğunuz hizmet, kampanya konusu",
            validation={"maxLength": 120},
            group="Konu"),
        TemplateFormField(id="one_cikan_ozellik", label="Öne Çıkan Vurgu", type="text", required=False,
            placeholder="örn. Konfor ve şıklık bir arada",
            validation={"maxLength": 60},
            helpText="Görsele basılır, kısa pazarlama mesajı olarak yazın. Detaylı caption AI tarafından üretilir.",
            group="Konu"),
        TemplateFormField(id="slide_count", label="Slide Sayısı", type="select", required=True,
            defaultValue="5",
            options=[
                {"value": "2", "label": "2 Slide"},
                {"value": "3", "label": "3 Slide"},
                {"value": "4", "label": "4 Slide"},
                {"value": "5", "label": "5 Slide"},
                {"value": "6", "label": "6 Slide"},
                {"value": "7", "label": "7 Slide"},
                {"value": "8", "label": "8 Slide"},
                {"value": "9", "label": "9 Slide"},
                {"value": "10", "label": "10 Slide"},
            ],
            group="Carousel"),
        TemplateFormField(id="cta_url", label="Yönlendirme Linki (opsiyonel)", type="url", required=False,
            placeholder="https://... (ürün, kampanya veya site linki)",
            helpText="Gönderiyi gören kişiyi bir yere yönlendirmek isterseniz linki buraya yapıştırın. Boş bırakırsanız caption yönlendirme yapmaz.",
            group="Yönlendirme"),
        TemplateFormField(id="cta_label", label="Çağrı Metni", type="text", required=False,
            defaultValue="Şimdi Keşfet",
            placeholder="Şimdi Keşfet",
            validation={"maxLength": 40},
            helpText="Linkin üzerine yazılacak kısa çağrı metni. Örn: 'Şimdi Keşfet', 'İncele', 'Sipariş Ver'.",
            group="Yönlendirme"),
    ],
    output=TemplateOutput(aspectRatioSuggestion="1:1"),
    prompt=TemplatePrompt(
        guidance=(
            "Carousel (çoklu slide) sosyal medya içeriği. Her slide farklı bir açıdan konuyu işler, "
            "birlikte tutarlı bir hikaye anlatır.\n\n"
            "🎠 CAROUSEL SLIDE DİZİSİ KURALI:\n"
            "- Slide 1 (HOOK): Dikkat çekici açılış. 7 görsel açı kategorisinden MERAK UYANDIRMA "
            "veya AYKIRI YAKLAŞIM tercih et. Kullanıcıyı kaydırmaya teşvik eden sahne.\n"
            "- Slide 2 — Slide N-1 (DEĞER): Her slide farklı açıdan konuyu işle. "
            "Tekrar etme — her slide'da farklı bir görsel açı kategorisi kullan. "
            "Slide dizisi boyunca bir anlatı oluştur (sorun → çözüm → sonuç gibi).\n"
            "- Slide N (CTA/KAPANIŞ): Aksiyon çağrısı. Marka renkleri ağırlıklı, "
            "temiz kompozisyon, karar anı sahnesi.\n\n"
            "🎨 GÖRSEL AÇI KATEGORİSİ (her slide için ayrı ayrı seç):\n"
            "1. SORUN VURGUSU — problemi görselleştir, öncesi sahnesi\n"
            "2. SONUÇ VURGUSU — dönüşüm/başarı anı, sonrası sahnesi\n"
            "3. SOSYAL KANIT — topluluk/grup, ortak kullanım sahnesi\n"
            "4. MERAK UYANDIRMA — örtük/kısmi gösterim, detay yakın plan\n"
            "5. ACİLİYET — zamana bağlı gösterge, sınırlı sunum sahnesi\n"
            "6. KİMLİK VURGUSU — hedef kitleye özel ortam\n"
            "7. AYKIRI YAKLAŞIM — beklenmedik/ters sahne kurgusu\n\n"
            "⚠️ ÇEŞİTLİLİK ZORUNLU: Aynı açıyı birden fazla slide'da kullanma. "
            "Özellikle 'SONUÇ VURGUSU' ve 'SOSYAL KANIT' stüdyo estetiğine iter — "
            "diğer açıları da kullan.\n\n"
            "Görsel yönergesi (tüm slide'lar için): Marka renklerini (HEX kodlarıyla) "
            "arka plan ve aksan olarak kullan. image_prompt'ta logo, marka rozeti, "
            "özellik rozeti, metin katmanı veya yazı TARIF ETME — gerçek logo ve "
            "caption'lar post-process/platform tarafında ekleniyor.\n\n"
            "Caption formülü: Hook (ana konu + faydası) → Öne çıkan özellik vurgusu → CTA. "
            "Caption TEK bir metin — slide bazlı ayrı caption yok, tüm carousel için "
            "bir caption yazılır.\n\n"
            "CTA (yönlendirme) kuralı:\n"
            "- Kullanıcı 'Yönlendirme Linki' doldurduysa: caption'ın son satırında çağrı metnini "
            "(cta_label) kullan ve platforma göre davran:\n"
            "  • Instagram/TikTok/Threads: '👉 {cta_label} — profilimizdeki linkten ulaşabilirsiniz'\n"
            "  • LinkedIn/Facebook/Twitter/Pinterest: '👉 {cta_label}: {cta_url}'\n"
            "- Kullanıcı link doldurmadıysa: yönlendirme satırı ekleme.\n\n"
            "🚫 YASAK — ÜRÜN BİLGİSİNDE OLMAYAN HİÇBİR ŞEYİ İCAT ETME:\n"
            "- Kargo süresi/ücreti icat etme ('ücretsiz kargo', '2 iş gününde kapınızda').\n"
            "- İade/garanti/değişim politikası icat etme ('30 gün koşulsuz iade').\n"
            "- Üretim süreci/menşei icat etme ('doğrudan üreticiden', 'el yapımı').\n"
            "- Sayısal iddia uydurma ('%300 artış', '10.000+ müşteri').\n"
            "- Teknik özellik icat etme (malzeme, bileşen, teknoloji).\n"
            "- Dolaylı fayda/konfor/performans iddiası icat etme (dayanıklılık, rahatlık,\n"
            "  verimlilik — bilgide açıkça belirtilmemişse yazma).\n"
            "- Hayali müşteri hikayesi/yorumu uydurma.\n"
            "- Sertifika, ödül, test sonucu icat etme.\n"
            "- Hashtag'lere bile bilgide olmayan özellik sızdırma "
            "('#şıkverahat', '#herAdımdaKonfor' gibi — bilgide yoksa yazma).\n"
            "KURAL: Sana verilen bilgiyi (ad, açıklama, etiketler) TEK doğruluk kaynağı\n"
            "olarak al. Bu bilgide olmayan hiçbir iddiayı yazma — ne teknik ne duygusal\n"
            "ne sektörel. 'Tasarladık/gözlemledik/araştırdık' gibi kurgusal otorite\n"
            "cümleleri de yasak. İçerik kısa kalsa bile dürüst kalsın."
        ),
        priority=["form_fields", "brand_kit", "rag_docs"],
    ),
    defaults=TemplateDefaults(),
    imageTextOverlay=ImageTextOverlaySpec(
        fields=["ana_konu", "one_cikan_ozellik"],
        position="bottom-left",
    ),
    tags=["genel", "carousel"],
)


TEMPLATES["shortvideo-genel-sablon"] = Template(
    id="shortvideo-genel-sablon",
    name="Kısa Video Şablonu",
    description="Tek konu/ürün/hizmet için AI sesli kısa video",
    icon="🎬",
    sectors=["*"],
    contentTypes=["video"],
    order=3,
    formFields=[
        TemplateFormField(id="cta_url", label="Yönlendirme Linki (opsiyonel)", type="url", required=False,
            placeholder="https://... (ürün, kampanya veya site linki)",
            helpText="Gönderiyi gören kişiyi bir yere yönlendirmek isterseniz linki buraya yapıştırın. Boş bırakırsanız caption yönlendirme yapmaz.",
            group="Yönlendirme"),
        TemplateFormField(id="cta_label", label="Çağrı Metni", type="text", required=False,
            defaultValue="Şimdi Keşfet",
            placeholder="Şimdi Keşfet",
            validation={"maxLength": 40},
            helpText="Linkin üzerine yazılacak kısa çağrı metni. Örn: 'Şimdi Keşfet', 'İncele', 'Sipariş Ver'.",
            group="Yönlendirme"),
    ],
    output=TemplateOutput(aspectRatioSuggestion="9:16"),
    prompt=TemplatePrompt(
        guidance=(
            "Kısa video şablonu. Tek bir konuyu/ürünü/hizmeti anlatan AI sesli "
            "kısa video üretir. Arka plan soyut/ambient sahnelerden oluşur.\n\n"
            "GİRDİ KAYNAĞI: Konu ve vurgular kullanıcının serbest metin alanından "
            "(user_prompt) gelir. Ürün seçilmişse product bağlamı (name, description, "
            "tags) ek olarak kullanılır.\n\n"
            "Bu şablon iki modda çalışır:\n\n"
            "🎬 GENEL VİDEO MODU:\n"
            "Soyut, ambient arka plan sahnesi üretilir. Ürün görseli üretme veya "
            "kullanma — kullanıcı açıkça istemedikçe ürün/obje odaklı sahne kurma. "
            "Doğa, şehir, tekstür, ışık oyunu, soyut hareket gibi atmosferik "
            "sahneler tercih et.\n\n"
            "📦 ÜRÜN/HİZMET VİDEO MODU:\n"
            "Ürünün gerçek fotoğrafı video arka planı olarak kullanılır. Still image "
            "prompt'u ürünü merkeze alan, stüdyo/lifestyle sahne olmalı. Ürün "
            "dokümanları varsa script'te ürün bilgilerini kullan.\n\n"
            "STILL IMAGE PROMPT (image_prompt için):\n"
            "- Marka renklerini (HEX kodlarıyla) arka plan ve aksan olarak kullan\n"
            "- Logo, metin katmanı, yazı TARIF ETME — bunlar post-process'te eklenir\n"
            "- Sahne hareketli video'ya uygun olmalı (kamera hareketi düşün)\n\n"
            "SCRIPT yönergesi:\n"
            "- Türkçe, 15-30 saniye arası voiceover script'i\n"
            "- Hook cümlesiyle başla (ilk 3 saniye kritik)\n"
            "- Kısa, net cümleler — TTS'in doğal okuyacağı yapıda\n"
            "- Abartılı iddia kullanma, bilgide olmayan şey uydurma\n\n"
            "CAPTION formülü: Hook (konu + faydası) → öne çıkan özellik/değer → CTA. "
            "Konu ve özellikleri user_prompt ve (varsa) product bağlamından çıkar. "
            "Caption video'nun altına yazılacak sosyal medya metnidir, script'ten "
            "farklıdır.\n\n"
            "CTA (yönlendirme) kuralı:\n"
            "- Kullanıcı 'Yönlendirme Linki' doldurduysa: caption'ın son satırında "
            "çağrı metnini (cta_label) kullan ve platforma göre davran:\n"
            "  • Instagram/TikTok/Threads: '👉 {cta_label} — profilimizdeki linkten "
            "ulaşabilirsiniz'\n"
            "  • LinkedIn/Facebook/Twitter/Pinterest: '👉 {cta_label}: {cta_url}'\n"
            "- Kullanıcı link doldurmadıysa: yönlendirme satırı ekleme."
        ),
        priority=["user_prompt", "product", "brand_kit", "rag_docs"],
    ),
    defaults=TemplateDefaults(),
    tags=["genel", "video"],
)


TEMPLATES["ozelgun-gorsel-sablon"] = Template(
    id="ozelgun-gorsel-sablon",
    name="Özel Gün Görseli",
    description="Tatil/özel gün için kutlama tonunda statik sosyal medya görseli",
    icon="🎉",
    sectors=["*"],
    contentTypes=["image"],
    order=4,
    formFields=[
        TemplateFormField(id="holiday_name", label="Tatil/Özel Gün Adı", type="text", required=True,
            placeholder="örn. Anneler Günü, 23 Nisan, Ramazan Bayramı",
            helpText="Tatil seçiciden otomatik doldurulur. Üzerine yazıp özelleştirebilirsiniz "
                     "(örn. 'Sevgili Anneme').",
            validation={"maxLength": 80},
            group="Tatil"),
        TemplateFormField(id="holiday_message", label="Özel Mesajınız (opsiyonel)", type="textarea", required=False,
            placeholder="Markanızın bu özel günde paylaşmak istediği mesaj, dilek veya hatıra...",
            helpText="Boş bırakırsanız caption tatilin genel anlamı + marka tonu üzerinden yazılır.",
            validation={"maxLength": 300},
            group="Tatil"),
        TemplateFormField(id="cta_url", label="Yönlendirme Linki (opsiyonel)", type="url", required=False,
            placeholder="https://... (kampanya, hediye seçimi, randevu linki)",
            helpText="Bu özel günle ilgili bir kampanya/sayfa varsa link buraya. Boş bırakırsanız "
                     "caption sadece kutlama/dilek mesajıyla biter.",
            group="Yönlendirme"),
        TemplateFormField(id="cta_label", label="Çağrı Metni (opsiyonel)", type="text", required=False,
            placeholder="örn. Hediye Seçimi, Kampanyayı İncele, Randevu Al",
            validation={"maxLength": 40},
            helpText="Yönlendirme linki doldurulduysa caption'da bu çağrı metni görünür.",
            group="Yönlendirme"),
    ],
    output=TemplateOutput(aspectRatioSuggestion="1:1"),
    prompt=TemplatePrompt(
        guidance=(
            "Özel gün/tatil için statik sosyal medya görseli. Caption ve görsel "
            "tatilin DUYGUSAL ANLAMINI taşımalı — ürün satışı/promosyon değil.\n\n"
            "📅 ÖZEL GÜN BAĞLAMI:\n"
            "Sana payload'da `special_day_name` (tatilin adı) ve `special_day_category` "
            "(national | religious | commercial) bilgisi gelir. Kategori caption tonunu "
            "belirler:\n"
            "- **national** (23 Nisan, 19 Mayıs, 29 Ekim, 30 Ağustos): vatan/gurur/birlik "
            "tonu. Aşırı slogan değil — markanın bu güne saygısını/katkısını anlat. "
            "Atatürk veya tarihi figür için uydurma alıntı/söz YASAK.\n"
            "- **religious** (Ramazan/Kurban Bayramı, Mevlid Kandili, Aşure): saygı + "
            "samimi dilek. 'Bayramınız mübarek olsun' tonu uygun. Dini açıklama "
            "yapma, hüküm verme.\n"
            "- **commercial** (Anneler Günü, Babalar Günü, Sevgililer Günü, Yeni Yıl): "
            "duygu + kişisel bağlantı. Kampanya/promosyon caption'ı YAZMA — hediye "
            "yönlendirmesi sadece kullanıcı `cta_url` doldurduysa son satıra eklenir.\n\n"
            "🎨 CAPTION FORMÜLÜ — TATİL FORMÜLÜ (ürün satışı formülü değil):\n"
            "1. HOOK: Tatilin duygusal anlamı veya gözlem (1-2 cümle). "
            "Örn. Anneler Günü için 'Bir annenin gözleri çocuğunu binlerce kişi "
            "arasında bulur.'\n"
            "2. KÖPRÜ: Markanın bu güne saygısı/dileği (1 cümle). "
            "Marka adı geçmek zorunda değil — ton önemli.\n"
            "3. KAPANIŞ: Kısa, samimi tebrik veya dilek. "
            "Örn. 'Sevgi dolu bir gün diliyoruz.' / 'Bayramınız mübarek olsun.'\n"
            "4. CTA (sadece kullanıcı `cta_url` doldurduysa): yumuşak yönlendirme. "
            "'Hediye seçiminizde size eşlik etmek isteriz' gibi — agresif satış değil.\n\n"
            "Kullanıcı `holiday_message` doldurduysa onu HOOK veya KÖPRÜ'ye organik "
            "şekilde entegre et — aynen kopyalama, marka tonuna uyarla.\n\n"
            "🚫 ÖZEL GÜN İÇİN YASAK:\n"
            "- Sahte istatistik/araştırma uydurma ('annelerin %87'si...').\n"
            "- Klişe slogan zinciri ('en güzel günler, en değerli anlar, en özel...').\n"
            "- Aşırı satış dili ('%50 indirim! Acele edin!').\n"
            "- Dini/milli günde dini/siyasi yorum.\n"
            "- Ürün özelliği listeleme (bu şablon ürün satışı için değil).\n"
            "- Tarihi figür için uydurma alıntı/söz.\n\n"
            "🖼️ GÖRSEL YÖNERGESİ (image_prompt için, İngilizce):\n"
            "Tatilin SEMBOLİZMİNİ + marka renklerini birleştir. Kategori başına "
            "atmosfer ipuçları:\n"
            "- **national**: Türk bayrağı renkleri (kırmızı + beyaz), gurur dolu fakat "
            "abartısız sahne. Tören/anma sahneleri kategori bağlamında uygun.\n"
            "- **religious**: warm light, traditional Turkish/Islamic patterns, "
            "calligraphy tarzı süsleme, hilal/yıldız yumuşak biçimde. İnsan figürü "
            "kullanılacaksa yüz detayı vurgulanmasın.\n"
            "- **commercial**: duygusal sahne. Anneler Günü → anne-çocuk silueti, "
            "çiçek; Sevgililer Günü → iki kişinin bağlantısı (eller, gölge); Yeni "
            "Yıl → ışık, yenilenme, doğa döngüsü.\n\n"
            "Marka rengini (HEX) arka plan veya aksan olarak entegre et — tatil "
            "renkleri hep dominant olmasın, marka kimliği sezilebilir kalsın.\n\n"
            "image_prompt'ta logo, marka rozeti veya yazı TARIF ETME — gerçek logo "
            "ve image text overlay (tatil başlığı) post-process'te eklenir.\n\n"
            "🎯 GÖRSEL AÇI KATEGORİSİ (image_prompt yazmadan önce bir açı seç):\n"
            "1. SEMBOLİK SAHNE — tatilin ikonik objesini öne çıkar (bayrak, çiçek, "
            "fener, mum)\n"
            "2. İNSAN ANI — bağlantı/dilek anı (sarılma, el tutuşma, yaşlı bir el)\n"
            "3. ATMOSFER — ışık/doku/renk üzerinden ruh hali (gün doğumu, sıcak ışık)\n"
            "4. KÜLTÜREL DETAY — Türkiye'ye özgü görsel öğe (motif, bayrak, "
            "geleneksel obje)\n\n"
            "Açı seçimi: kategori + holiday_message birlikte yön verir. Genel "
            "sahnede ATMOSFER veya SEMBOLİK SAHNE en güvenli; kişisel/duygusal "
            "ton İNSAN ANI'na götürür. Aynı açıyı her özel günde kullanma.\n\n"
            "CTA (caption sonu) kuralı:\n"
            "- `cta_url` boşsa: caption tebrik/dilek cümlesiyle biter, link satırı yok.\n"
            "- `cta_url` doluysa platforma göre:\n"
            "  • Instagram/TikTok/Threads: '🎁 {cta_label} — profilimizdeki linkten "
            "ulaşabilirsiniz' (useFirstComment aktifse URL first_comment'e)\n"
            "  • LinkedIn/Facebook/Twitter/Pinterest: '🎁 {cta_label}: {cta_url}'\n"
            "- Yumuşak emoji (🎁 🌷 🌙 🇹🇷) tatil tonuyla uyumlu kullanılabilir, abartma."
        ),
        priority=["form_fields", "brand_kit", "rag_docs"],
    ),
    defaults=TemplateDefaults(),
    imageTextOverlay=ImageTextOverlaySpec(
        fields=["holiday_name"],
        position="bottom-left",
    ),
    tags=["özel gün", "tatil", "görsel"],
)


TEMPLATES["ozelgun-carousel-sablon"] = Template(
    id="ozelgun-carousel-sablon",
    name="Özel Gün Carousel",
    description="Tatil/özel gün için çoklu slide kutlama hikayesi",
    icon="🎉",
    sectors=["*"],
    contentTypes=["carousel"],
    order=5,
    formFields=[
        TemplateFormField(id="holiday_name", label="Tatil/Özel Gün Adı", type="text", required=True,
            placeholder="örn. Anneler Günü, 23 Nisan, Ramazan Bayramı",
            helpText="Tatil seçiciden otomatik doldurulur. Üzerine yazıp özelleştirebilirsiniz.",
            validation={"maxLength": 80},
            group="Tatil"),
        TemplateFormField(id="holiday_message", label="Özel Mesajınız (opsiyonel)", type="textarea", required=False,
            placeholder="Bu özel günde paylaşmak istediğiniz mesaj, dilek veya hatıra...",
            helpText="Boş bırakırsanız carousel hikayesi tatilin genel anlamı + marka tonu üzerinden kurgulanır.",
            validation={"maxLength": 300},
            group="Tatil"),
        TemplateFormField(id="slide_count", label="Slide Sayısı", type="select", required=True,
            defaultValue="4",
            options=[
                {"value": "3", "label": "3 Slide"},
                {"value": "4", "label": "4 Slide"},
                {"value": "5", "label": "5 Slide"},
                {"value": "6", "label": "6 Slide"},
                {"value": "7", "label": "7 Slide"},
            ],
            helpText="Özel gün carousel'lerinde 3-5 slide önerilir — kısa, duygusal akış.",
            group="Carousel"),
        TemplateFormField(id="cta_url", label="Yönlendirme Linki (opsiyonel)", type="url", required=False,
            placeholder="https://... (kampanya, hediye seçimi, randevu linki)",
            helpText="Boş bırakırsanız caption sadece kutlama/dilek mesajıyla biter.",
            group="Yönlendirme"),
        TemplateFormField(id="cta_label", label="Çağrı Metni (opsiyonel)", type="text", required=False,
            placeholder="örn. Hediye Seçimi, Kampanyayı İncele, Randevu Al",
            validation={"maxLength": 40},
            group="Yönlendirme"),
    ],
    output=TemplateOutput(aspectRatioSuggestion="1:1"),
    prompt=TemplatePrompt(
        guidance=(
            "Özel gün/tatil carousel'i. Slide dizisi tatilin duygusal anlamını "
            "katmanlı olarak anlatır — ürün satış akışı değil, hikaye/dilek akışı.\n\n"
            "📅 ÖZEL GÜN BAĞLAMI:\n"
            "Sana payload'da `special_day_name` + `special_day_category` "
            "(national | religious | commercial) gelir. Kategori tonu belirler:\n"
            "- **national**: vatan/gurur/birlik. Tarihi figür için uydurma alıntı yasak.\n"
            "- **religious**: saygı + samimi dilek. Dini açıklama/hüküm yapma.\n"
            "- **commercial**: duygu + kişisel bağlantı. Promosyon değil.\n\n"
            "🎠 CAROUSEL SLIDE DİZİSİ — TATİL HİKAYESİ:\n"
            "- **Slide 1 (HOOK)**: Tatilin duygusal anlamına dair açılış sahnesi. "
            "Sembolik veya atmosferik. Kullanıcıyı kaydırmaya teşvik eden duygusal "
            "yakalama.\n"
            "- **Slide 2 — Slide N-1 (HİKAYE)**: Her slide tatilin başka bir yönünü "
            "işler. Olası açılar:\n"
            "  • Tarihi/kültürel anlamı (national/religious'ta uygun)\n"
            "  • İnsan/aile bağlantısı (commercial'da uygun)\n"
            "  • Markanın bu güne saygısı/dileği (gizli reklam değil — paylaşılan "
            "değer)\n"
            "  • Dilek/temenniler\n"
            "- **Slide N (KAPANIŞ)**: Samimi tebrik veya marka dileği. CTA varsa bu "
            "slide'da görsel olarak yumuşak çağrı (ör. açık kapı, uzanan el). CTA "
            "yoksa sadece tebrik atmosferi.\n\n"
            "⚠️ SLIDE TUTARLILIĞI: Tüm slide'lar **aynı görsel atmosferde** kalmalı "
            "(renk paleti, ışık tonu). Ürün carousel'lerindeki gibi farklı sahnelere "
            "atlama — tek bir tatil ruh hali boyunca akış.\n\n"
            "🎨 GÖRSEL AÇI KATEGORİSİ (her slide için ayrı seç):\n"
            "1. SEMBOLİK SAHNE — bayrak, çiçek, fener, mum, motif\n"
            "2. İNSAN ANI — sarılma, el, gözler, anılar\n"
            "3. ATMOSFER — ışık, doku, renk geçişi\n"
            "4. KÜLTÜREL DETAY — geleneksel motif, mekan, obje\n\n"
            "Aynı açıyı arka arkaya 2 slide'da kullanma — çeşitlilik akışı taşır.\n\n"
            "🖼️ GÖRSEL YÖNERGESİ (tüm slide'lar için, İngilizce):\n"
            "- Tatilin sembolizmi + marka renklerini birleştir.\n"
            "- Kategoriye göre atmosfer:\n"
            "  • national: Türk bayrağı renkleri, gurur dolu fakat abartısız\n"
            "  • religious: warm light, traditional patterns, calligraphy tarzı\n"
            "  • commercial: duygusal sahne (anne-çocuk, çift, doğa, ışık)\n"
            "- Logo, yazı, marka rozeti TARIF ETME (post-process'te eklenir).\n\n"
            "📝 CAPTION FORMÜLÜ:\n"
            "Caption TEK metin — slide bazlı ayrı caption yok, tüm carousel için "
            "bir caption. Yapı:\n"
            "1. HOOK: Tatilin duygusal anlamı (1-2 cümle)\n"
            "2. KÖPRÜ: Markanın bu güne saygısı/dileği\n"
            "3. KAPANIŞ: Samimi tebrik veya dilek\n"
            "4. CTA (sadece `cta_url` doluysa): yumuşak yönlendirme\n\n"
            "🚫 ÖZEL GÜN İÇİN YASAK:\n"
            "- Sahte istatistik ('annelerin %87'si...').\n"
            "- Klişe slogan zinciri.\n"
            "- Aşırı satış dili ('%50 indirim').\n"
            "- Dini/siyasi yorum.\n"
            "- Tarihi figür için uydurma alıntı.\n"
            "- Hashtag'lere yapay özellik sızdırma.\n\n"
            "CTA kuralı:\n"
            "- `cta_url` boşsa: caption tebrik cümlesiyle biter, link satırı yok.\n"
            "- `cta_url` doluysa platforma göre:\n"
            "  • Instagram/TikTok/Threads: '🎁 {cta_label} — profilimizdeki linkten "
            "ulaşabilirsiniz'\n"
            "  • LinkedIn/Facebook/Twitter/Pinterest: '🎁 {cta_label}: {cta_url}'"
        ),
        priority=["form_fields", "brand_kit", "rag_docs"],
    ),
    defaults=TemplateDefaults(),
    imageTextOverlay=ImageTextOverlaySpec(
        fields=["holiday_name"],
        position="bottom-left",
    ),
    tags=["özel gün", "tatil", "carousel"],
)


TEMPLATES["ozelgun-shortvideo-sablon"] = Template(
    id="ozelgun-shortvideo-sablon",
    name="Özel Gün Kısa Video",
    description="Tatil/özel gün için AI sesli kısa kutlama videosu",
    icon="🎉",
    sectors=["*"],
    contentTypes=["video"],
    order=6,
    formFields=[
        TemplateFormField(id="holiday_name", label="Tatil/Özel Gün Adı", type="text", required=True,
            placeholder="örn. Anneler Günü, 23 Nisan, Ramazan Bayramı",
            helpText="Tatil seçiciden otomatik doldurulur. Üzerine yazıp özelleştirebilirsiniz.",
            validation={"maxLength": 80},
            group="Tatil"),
        TemplateFormField(id="holiday_message", label="Özel Mesajınız (opsiyonel)", type="textarea", required=False,
            placeholder="Bu özel günde paylaşmak istediğiniz mesaj, dilek veya hatıra...",
            helpText="Boş bırakırsanız script tatilin genel anlamı + marka tonu üzerinden yazılır.",
            validation={"maxLength": 300},
            group="Tatil"),
        TemplateFormField(id="cta_url", label="Yönlendirme Linki (opsiyonel)", type="url", required=False,
            placeholder="https://... (kampanya, hediye seçimi, randevu linki)",
            helpText="Boş bırakırsanız caption sadece kutlama/dilek mesajıyla biter.",
            group="Yönlendirme"),
        TemplateFormField(id="cta_label", label="Çağrı Metni (opsiyonel)", type="text", required=False,
            placeholder="örn. Hediye Seçimi, Kampanyayı İncele, Randevu Al",
            validation={"maxLength": 40},
            group="Yönlendirme"),
    ],
    output=TemplateOutput(aspectRatioSuggestion="9:16"),
    prompt=TemplatePrompt(
        guidance=(
            "Özel gün/tatil kısa videosu. Voiceover script tatilin duygusal "
            "anlamını anlatır — ürün satışı/promosyon değil, kutlama/dilek tonu.\n\n"
            "📅 ÖZEL GÜN BAĞLAMI:\n"
            "Sana payload'da `special_day_name` + `special_day_category` "
            "(national | religious | commercial) gelir. Kategori tonu belirler:\n"
            "- **national**: vatan/gurur/birlik. Tarihi figür için uydurma alıntı yasak.\n"
            "- **religious**: saygı + samimi dilek. Dini açıklama/hüküm yapma.\n"
            "- **commercial**: duygu + kişisel bağlantı. Kampanya değil.\n\n"
            "🎙️ SCRIPT (TÜRKÇE VOICEOVER) — TATİL FORMÜLÜ:\n"
            "Yapı (15-25 saniye, ~32-55 kelime — özel gün'de kısa daha etkili):\n"
            "1. HOOK (ilk 3 saniye): Tatilin duygusal anlamı veya gözlem.\n"
            "2. ANLAM (orta): Markanın bu güne saygısı/dileği. 1-2 cümle.\n"
            "3. KAPANIŞ: Samimi tebrik. CTA varsa yumuşak yönlendirme.\n\n"
            "Kullanıcı `holiday_message` doldurduysa onu HOOK veya ANLAM'a organik "
            "şekilde entegre et — aynen kopyalama.\n\n"
            "⚠️ SCRIPT KURALLARI:\n"
            "- Türkçe, TTS'in doğal okuyacağı kısa cümleler.\n"
            "- Tarihi figür için uydurma alıntı/söz YASAK.\n"
            "- Dini/siyasi yorum yapma.\n"
            "- Sahte istatistik uydurma.\n"
            "- Aşırı satış dili kullanma.\n"
            "- Bilgide olmayan iddia uydurma.\n\n"
            "🖼️ STILL IMAGE PROMPT (image_prompt için, İngilizce):\n"
            "Sahne hareketli video'ya uygun olmalı (kamera hareketi düşün — slow "
            "push-in, gentle pan, atmospheric drift). Tatilin sembolizmi + marka "
            "renklerini birleştir.\n\n"
            "Kategori başına atmosfer:\n"
            "- **national**: Türk bayrağı renkleri, gurur dolu fakat abartısız sahne.\n"
            "- **religious**: warm light, traditional patterns, calligraphy süsleme.\n"
            "- **commercial**: duygusal sahne (anne-çocuk silueti, eller, çiçek, "
            "doğa, ışık).\n\n"
            "Marka rengini (HEX) arka plan veya aksan olarak entegre et — tatil "
            "renkleri hep dominant olmasın.\n\n"
            "image_prompt'ta logo, yazı, marka rozeti TARIF ETME — gerçek logo + "
            "altyazı post-process'te eklenir.\n\n"
            "🎯 GÖRSEL AÇI KATEGORİSİ (image_prompt için bir açı seç):\n"
            "1. SEMBOLİK SAHNE — bayrak, çiçek, fener, mum, motif\n"
            "2. İNSAN ANI — sarılma, el, gözler\n"
            "3. ATMOSFER — ışık, doku, renk geçişi\n"
            "4. KÜLTÜREL DETAY — geleneksel motif, mekan, obje\n\n"
            "📝 CAPTION FORMÜLÜ (script'ten ayrı, sosyal medya altyazısı):\n"
            "1. HOOK: Tatilin duygusal anlamı (1-2 cümle)\n"
            "2. KÖPRÜ: Markanın dileği\n"
            "3. KAPANIŞ: Samimi tebrik\n"
            "4. CTA (sadece `cta_url` doluysa): yumuşak yönlendirme\n\n"
            "Caption ve script aynı şeyi tekrar etmesin — script konuşulan voiceover, "
            "caption okunan sosyal medya metni. İkisi tatilin farklı yönlerine "
            "değinebilir.\n\n"
            "CTA kuralı:\n"
            "- `cta_url` boşsa: caption tebrik cümlesiyle biter, link satırı yok.\n"
            "- `cta_url` doluysa platforma göre:\n"
            "  • Instagram/TikTok/Threads: '🎁 {cta_label} — profilimizdeki linkten "
            "ulaşabilirsiniz'\n"
            "  • LinkedIn/Facebook/Twitter/Pinterest: '🎁 {cta_label}: {cta_url}'"
        ),
        priority=["form_fields", "brand_kit", "rag_docs"],
    ),
    defaults=TemplateDefaults(),
    tags=["özel gün", "tatil", "video"],
)


TEMPLATES["genel-hakkimizda"] = Template(
    id="genel-hakkimizda",
    name="Hakkımızda",
    description="Marka hikayesi ve değerleri",
    icon="🏢",
    sectors=["*"],
    contentTypes=["image"],
    order=200,
    formFields=[
        TemplateFormField(id="founding_year", label="Kuruluş Yılı", type="number", required=False),
        TemplateFormField(id="mission", label="Misyon / Amaç", type="textarea", required=True,
            placeholder="Markanızın varlık nedeni, ne yapmaya çalışıyor?",
            validation={"maxLength": 500}),
        TemplateFormField(id="differentiator", label="Bizi Farklı Kılan", type="textarea",
            required=False, placeholder="Rakiplerden ne ile ayrışıyorsunuz?",
            validation={"maxLength": 400}),
    ],
    output=TemplateOutput(aspectRatioSuggestion="4:5"),
    prompt=TemplatePrompt(
        guidance=(
            "Marka hikayesi/değer önermesi. İçten, samimi ton.\n\n"
            "Görsel yönergesi: Marka logosu merkezde veya ekip görseli. Sıcak renkler "
            "(brand kit'e göre). Profesyonel ama sıcak.\n\n"
            "Caption formülü: Hikaye hook → Misyon → Değerler/fark → CTA."
        ),
        priority=["form_fields", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=["Bizi tanıyın", "Web sitesini ziyaret edin"],
        suggestedHashtags=["markamız", "hikayemiz", "değerlerimiz"],
    ),
)


TEMPLATES["genel-ekip-tanitimi"] = Template(
    id="genel-ekip-tanitimi",
    name="Ekip Tanıtımı",
    description="Ekipten bir üye spotlight'ı",
    icon="👥",
    sectors=["*"],
    contentTypes=["image"],
    order=210,
    formFields=[
        TemplateFormField(id="member_name", label="Ekip Üyesi Adı", type="text", required=True,
            validation={"maxLength": 100}),
        TemplateFormField(id="role", label="Görevi", type="text", required=True,
            validation={"maxLength": 100}),
        TemplateFormField(id="years_with_us", label="Kaç Yıldır Bizimle?", type="number",
            required=False, suffix="yıl"),
        TemplateFormField(id="personal_note", label="Kişisel Not", type="textarea",
            required=False,
            placeholder="Ekip üyesinin sevdiği şey, katkısı, hobileri...",
            validation={"maxLength": 400}),
    ],
    output=TemplateOutput(aspectRatioSuggestion="1:1"),
    prompt=TemplatePrompt(
        guidance=(
            "Ekip üyesi tanıtımı. İnsan odaklı, sıcak ton. 'Ekibimizin arkasındaki "
            "yüzler' hissi.\n\n"
            "Görsel yönergesi: Ekip üyesinin profesyonel fotoğrafı (varsa). Yoksa "
            "initials veya avatar kutu. Arka planda marka renklerinden aksan.\n\n"
            "Caption formülü: Tanıtım hook → Görev + deneyim → Kişisel not → Takdir "
            "mesajı (opsiyonel) → CTA."
        ),
        priority=["form_fields", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=["Ekibimizi tanıyın"],
        suggestedHashtags=["ekip", "meetteam", "ailemiz"],
    ),
)


TEMPLATES["genel-musteri-yorumu"] = Template(
    id="genel-musteri-yorumu",
    name="Müşteri Yorumu",
    description="Test bul/yorum kartı — sosyal kanıt",
    icon="💬",
    sectors=["*"],
    contentTypes=["image"],
    order=220,
    formFields=[
        TemplateFormField(id="customer_name", label="Müşteri Adı", type="text", required=False,
            defaultValue="Müşterimiz",
            helpText="Opsiyonel — girmezseniz 'Müşterimiz' ifadesi kullanılır (anonim yorum için).",
            validation={"maxLength": 80}),
        TemplateFormField(id="review_text", label="Yorum", type="textarea", required=True,
            placeholder="Müşterinin bıraktığı yorum (izin alınmış olmalı)",
            validation={"maxLength": 500}),
        TemplateFormField(id="rating", label="Puan", type="select", required=False,
            options=[
                {"value": "5", "label": "⭐⭐⭐⭐⭐ (5)"},
                {"value": "4", "label": "⭐⭐⭐⭐ (4)"},
            ]),
        TemplateFormField(id="customer_context", label="Müşteri Bağlamı", type="text",
            required=False, placeholder="örn. İstanbul'dan, 2 yıldır müşteri",
            validation={"maxLength": 150}),
    ],
    output=TemplateOutput(aspectRatioSuggestion="1:1"),
    prompt=TemplatePrompt(
        guidance=(
            "Müşteri yorumu / testimonial kartı. Sosyal kanıt, güven inşası.\n\n"
            "Görsel yönergesi: Yorum metni görselde alıntı şeklinde (tırnak işareti "
            "büyük), müşteri adı alt kısımda. Temiz, profesyonel tasarım. Puan "
            "yıldızları (varsa) görselde.\n\n"
            "Caption formülü: Teşekkür hook → Yorumun özeti → Davet (siz de paylaşın) → CTA.\n\n"
            "Müşteri adı yoksa: 'Müşterimiz' ifadesini kullan (anonim yorum — gizlilik veya izin yok). "
            "Görsel altında ad yerine 'Mutlu müşterimizden' veya 'Bir müşterimiz' ifadesi geçsin. "
            "Caption'da kişiselleştirilmiş hitap ('Sevgili Ayşe Hanım...') kullanma."
        ),
        priority=["rag_docs", "form_fields", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=["Siz de deneyim paylaşın", "Deneyiminizi bize yazın"],
        suggestedHashtags=["müşteriyorumu", "teşekkürler", "mutlumüşteri"],
    ),
)


TEMPLATES["genel-motivasyon"] = Template(
    id="genel-motivasyon",
    name="Motivasyon",
    description="İlham verici söz, marka ile ilişkili",
    icon="✨",
    sectors=["*"],
    contentTypes=["image"],
    order=230,
    formFields=[
        TemplateFormField(id="quote_text", label="Söz / İlham", type="textarea", required=True,
            validation={"maxLength": 400}),
        TemplateFormField(id="quote_author", label="Söz Sahibi", type="text", required=False,
            placeholder="örn. Atatürk, Steve Jobs, Anonim"),
    ],
    output=TemplateOutput(aspectRatioSuggestion="1:1"),
    prompt=TemplatePrompt(
        guidance=(
            "Motivasyon/ilham kartı. Pazartesi sabahları veya haftasonu postları için.\n\n"
            "Görsel yönergesi: Söz görselde büyük tipografi ile merkeze, yazar altta. "
            "Sakin, ilham verici arka plan (nature, abstract, brand colors).\n\n"
            "Caption formülü: Söz (tekrar) → Kısa düşünme önerisi → Güzel bir haftanız "
            "olsun / iyi Pazartesi türü kapanış."
        ),
        priority=["form_fields", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=[],
        suggestedHashtags=["motivasyon", "ilham", "pazartesi"],
    ),
)


TEMPLATES["genel-haftalik-ozet"] = Template(
    id="genel-haftalik-ozet",
    name="Haftalık Özet",
    description="Haftanın içerik özeti / haber bülteni",
    icon="📰",
    sectors=["*"],
    contentTypes=["image"],
    order=240,
    formFields=[
        TemplateFormField(id="week_highlights", label="Haftanın Öne Çıkanları",
            type="textarea", required=True,
            placeholder="3-5 madde halinde haftanın özeti",
            validation={"maxLength": 600}),
    ],
    output=TemplateOutput(aspectRatioSuggestion="4:5"),
    prompt=TemplatePrompt(
        guidance=(
            "Hafta sonu paylaşımı — haftanın özeti. Profesyonel ama samimi.\n\n"
            "Görsel yönergesi: Infografik stili, numaralı maddeler, temiz tipografi.\n\n"
            "Caption formülü: Hafta özet hook → Maddeler → İyi hafta sonları kapanış."
        ),
        priority=["form_fields", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=[],
        suggestedHashtags=["haftanınözeti", "cumartesi"],
    ),
)


TEMPLATES["genel-kutlama"] = Template(
    id="genel-kutlama",
    name="Kutlama / Tebrik",
    description="Başarı, yıldönümü, teşekkür içerikleri",
    icon="🎊",
    sectors=["*"],
    contentTypes=["image"],
    order=250,
    formFields=[
        TemplateFormField(id="celebration_type", label="Ne Kutlaniyor?", type="text",
            required=True, placeholder="örn. 5. yıldönümü, 1000. müşteri, ödül",
            validation={"maxLength": 150}),
        TemplateFormField(id="achievement", label="Başarı Detayı", type="textarea",
            required=False, validation={"maxLength": 500},
            helpText="Opsiyonel — girmezseniz sadece celebration_type üzerinden caption üretilir."),
        TemplateFormField(id="thanks_to", label="Teşekkür", type="text", required=False,
            placeholder="örn. Müşterilerimize, ekibimize"),
    ],
    output=TemplateOutput(aspectRatioSuggestion="1:1"),
    prompt=TemplatePrompt(
        guidance=(
            "Kutlama içeriği. Sıcak, içten, gururlu.\n\n"
            "Görsel yönergesi: Konfeti/şerit/balon görseli, canlı renkler. Kutlama "
            "yazısı büyük tipografi.\n\n"
            "Caption formülü: Duyuru hook → Detay → Teşekkür → Kutlama mesajı.\n\n"
            "Başarı detayı yoksa: Sadece celebration_type üzerinden kısa, içten bir kutlama yaz. "
            "Uydurma detay ekleme (ör. '1000. müşteri' dendiyse 'İstanbul'dan Ayşe Hanım' gibi "
            "hayali isim/hikâye koyma). Caption 2-3 cümle olabilir, teşekkür kısmı korunur."
        ),
        priority=["form_fields", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=["Siz de kutlayın"],
        suggestedHashtags=["kutlama", "teşekkürler", "başarı"],
    ),
)


TEMPLATES["genel-sosyal-kanit"] = Template(
    id="genel-sosyal-kanit",
    name="Sosyal Kanıt",
    description="Medya alıntısı, ödül, referans",
    icon="🏆",
    sectors=["*"],
    contentTypes=["image"],
    order=260,
    formFields=[
        TemplateFormField(id="proof_type", label="Kanıt Türü", type="select", required=True,
            options=[
                {"value": "medya", "label": "Medya Alıntısı"},
                {"value": "ödül", "label": "Ödül"},
                {"value": "referans", "label": "Kurumsal Referans"},
                {"value": "sertifika", "label": "Sertifika"},
            ]),
        TemplateFormField(id="source", label="Kaynak", type="text", required=True,
            placeholder="örn. Hürriyet, TUGIAD, ISO, ...",
            validation={"maxLength": 150}),
        TemplateFormField(id="detail", label="Detay", type="textarea", required=True,
            validation={"maxLength": 400}),
    ],
    output=TemplateOutput(aspectRatioSuggestion="1:1"),
    prompt=TemplatePrompt(
        guidance=(
            "Sosyal kanıt kartı. Güven inşası, markaya otorite katar.\n\n"
            "Görsel yönergesi: Kaynağın logosu (medya/kurum) öne çıksın. Ödül/sertifika "
            "ise ikonu belirgin. Sade, profesyonel.\n\n"
            "Caption formülü: Haberin hook → Detay → Teşekkür/alçakgönüllülük → CTA."
        ),
        priority=["form_fields", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=[],
        suggestedHashtags=["referans", "ödül", "başarı"],
    ),
)


TEMPLATES["genel-calisma-saatleri"] = Template(
    id="genel-calisma-saatleri",
    name="Çalışma Saatleri",
    description="Operasyonel bilgi duyurusu",
    icon="🕐",
    sectors=["*"],
    contentTypes=["image"],
    order=270,
    formFields=[
        TemplateFormField(id="announcement_type", label="Duyuru Tipi", type="select",
            required=True,
            options=[
                {"value": "saatler", "label": "Normal çalışma saatleri"},
                {"value": "tatil", "label": "Tatil günleri"},
                {"value": "özel", "label": "Özel durum (taşınma, vb.)"},
            ]),
        TemplateFormField(id="detail", label="Detay", type="textarea", required=True,
            placeholder="Saatler, tarihler, iletişim kanalları",
            validation={"maxLength": 500}),
    ],
    output=TemplateOutput(aspectRatioSuggestion="1:1"),
    prompt=TemplatePrompt(
        guidance=(
            "Operasyonel duyuru. Açık, pratik, bilgilendirici.\n\n"
            "Görsel yönergesi: Saat/takvim ikonu, okunabilir tipografi, marka renkleri.\n\n"
            "Caption formülü: Duyuru hook → Detay (saatler/tarihler) → İletişim kanalları."
        ),
        priority=["form_fields", "brand_kit"],
    ),
    defaults=TemplateDefaults(
        suggestedCTAs=["Detaylı bilgi için"],
        suggestedHashtags=["duyuru", "çalışmasaatleri"],
    ),
)


# ─── Sektör rehberi (prompt enjeksiyonu için) ───────────────────────────────
# Anahtar: social.sectors.slug. 4 öncelikli sektör detaylı (~150-250 kelime),
# diğer 8 generic (~50 kelime). Toplam 12 entry.

SECTOR_GUIDANCE: dict[str, str] = {
    "e-ticaret-perakende": (
        "E-Ticaret sektörü için içerik rehberi:\n\n"
        "Ton: Enerjik, satış odaklı ama agresif değil. Aciliyet hissi yaratabilirsin "
        "ama sahte urgency kullanma ('son 1 adet' abartısından kaçın).\n\n"
        "Öne çıkarılacaklar: Fiyat avantajı, indirim yüzdesi, ürün özellikleri, "
        "kullanıcı deneyimi. Sosyal kanıt (müşteri yorumu) güçlü etki yapar.\n\n"
        "Platform öncelikleri: Instagram (görsel + hashtag), TikTok (trend'ler), "
        "Facebook (yaşlı kitle), Pinterest (SEO + inspiration board).\n\n"
        "Caption formülü: Hook → Ürün faydası → Fiyat/indirim → CTA\n\n"
        "Yasaklar: Karşılaştırmalı reklam, rakip ismi, abartılı iddia "
        "('dünyanın en iyisi'), garanti ifadesi."
    ),
    "yemek-gida": (
        "Yemek & Gıda sektörü için içerik rehberi:\n\n"
        "Ton: Davetkar, samimi, iştah açıcı. Yöresel dokunuşlar mümkünse kullan. "
        "Profesyonel ama sıcak hissi korunmalı.\n\n"
        "Öne çıkarılacaklar: Tat deneyimi (kremamsı, ferahlatıcı, baharatlı vb.), "
        "taze malzemeler, şef imzası, atmosfer, zaman (öğle/akşam servisi).\n\n"
        "Platform öncelikleri: Instagram (yemek fotoğrafı), TikTok (hazırlık "
        "videoları), Facebook (lokal yerel), Pinterest (tarif arama).\n\n"
        "Caption formülü: Duygu hook → Ürün/menü → Tat/hissi → Zaman/yer bilgisi → CTA\n\n"
        "Yasaklar: Kalori/diyet iddiası (yasal sorun), 'dünyanın en lezzetlisi' "
        "absolut ifade, karşılaştırma."
    ),
    "saglik": (
        "Sağlık sektörü için içerik rehberi:\n\n"
        "Ton: Bilgilendirici, otorite ama anlaşılır. Güven verici. Korku/panik dili "
        "kullanma. Tıbbi jargonu minimal tut.\n\n"
        "Öne çıkarılacaklar: Uzmanlık, kanıta dayalı bilgi, hasta deneyimi (izin alınarak), "
        "erken teşhis önemi, koruyucu sağlık.\n\n"
        "Platform öncelikleri: Instagram (görsel eğitim), LinkedIn (B2B, akademik), "
        "YouTube (uzun anlatım), Facebook (lokal kitle).\n\n"
        "Caption formülü: Bilgi hook (istatistik/soru) → Açıklama → Önlem/öneri → "
        "CTA → DISCLAIMER (otomatik eklenir)\n\n"
        "Yasaklar: KESIN tanı koyma, ilaç dozajı tavsiyesi, 'size iyileşme garantisi "
        "veriyoruz' türü ifadeler, tıbbi etik ihlali, rakip klinik karşılaştırması."
    ),
    "hizmet": (
        "Profesyonel Hizmet sektörü için içerik rehberi:\n\n"
        "Ton: Profesyonel ama sıcak, yetkin, bilgece. Thought leadership. Otorite + "
        "yardımsever dengeli.\n\n"
        "Öne çıkarılacaklar: Uzmanlık alanı, sektörel deneyim, vaka çalışması "
        "(anonimize), mevzuat bilgisi, süreç şeffaflığı, ekip yetkinliği.\n\n"
        "Platform öncelikleri: LinkedIn (B2B, thought leadership), Instagram (brand "
        "awareness), Twitter (hızlı sektör yorumu).\n\n"
        "Caption formülü: İnsight/gözlem hook → Detay/değer bilgisi → Uygulama → CTA\n\n"
        "Yasaklar: Müvekkil özel bilgisi (izin olmadan), kesin hukuki tavsiye, "
        "rakip küçümseme, absolut iddia ('en iyi avukat'), garanti dili."
    ),
    # Generic 8
    "teknoloji": (
        "Teknoloji: Yenilikçi, ileri görüşlü ton. İnovasyon, çözüm, kullanıcı "
        "kolaylığı öne çıkar. Jargon yığınından kaçın."
    ),
    "egitim": (
        "Eğitim: Motive edici, destekleyici ton. Öğrenci başarısı, eğitim kalitesi "
        "vurgusu. Garanti iddiası yasak."
    ),
    "moda-tekstil": (
        "Moda: Estetik, ilham verici ton. Koleksiyon, malzeme, stil hissi. Beden "
        "ayrımcılığından kaçın."
    ),
    "turizm": (
        "Turizm: Hayalci, davetkar ton. Destinasyon, deneyim vurgusu. Sahte "
        "fiyat/özellik iddiası yasak."
    ),
    "finans": (
        "Finans: Analitik, güven verici, şeffaf ton. Veri + uzmanlık. Yatırım "
        "garantisi, getiri vaadi YASAK (SPK)."
    ),
    "insaat-gayrimenkul": (
        "İnşaat/GMM: Yatırım odaklı, güvenilir ton. Lokasyon, m², özellik vurgusu. "
        "Kesin değer artış vaadi yasak."
    ),
    "otomotiv": (
        "Otomotiv: Güçlü, dinamik ton. Performans, güvenlik, tasarım. Absolut "
        "iddia yasak."
    ),
    "genel": (
        "Genel: Markaya özel (brand kit'ten alınır). Sektör-spesifik guidance yok — "
        "form alanları yeterli."
    ),
}


# ─── Helper fonksiyonlar ────────────────────────────────────────────────────

def get_all_templates(
    sector: str | None = None,
    content_type: str | None = None,
) -> list[Template]:
    """Tüm şablonları filtreleyerek döndürür.

    - sector=None → tüm şablonlar
    - sector="e-ticaret-perakende" → bu sektöre ait + `["*"]` (genel) şablonlar
    - content_type="image" → sadece bu içerik tipini destekleyen şablonlar
    """
    results: list[Template] = []
    for tpl in TEMPLATES.values():
        if sector is not None:
            if sector not in tpl.sectors and "*" not in tpl.sectors:
                continue
        if content_type is not None:
            if content_type not in tpl.contentTypes:
                continue
        results.append(tpl)
    results.sort(key=lambda t: (t.order or 999, t.name))
    return results


def get_template_by_id(template_id: str) -> Template | None:
    """Tekil şablon getir. Bulunamazsa None döner."""
    return TEMPLATES.get(template_id)


def get_sector_guidance(sector_slug: str | None) -> str:
    """Sektör rehberini getir. Eşleşme yoksa boş string döner (prompt'ta no-op)."""
    if not sector_slug:
        return ""
    return SECTOR_GUIDANCE.get(sector_slug, "")
