from datetime import datetime
from typing import Any
from uuid import UUID

import logging

from pydantic import BaseModel, ConfigDict, Field, model_validator

logger = logging.getLogger(__name__)


# ─── Common response wrappers ───────────────────────────────────────────────

class OkResponse(BaseModel):
    success: bool = True
    data: Any = None


# ─── K-07 damga taşıma sözleşmesi — üretici ucu (plan Task 10) ──────────────

# İstemciye GİTMEYECEK paket kimlik alanları. Bunlar `social.generation_stamps`
# ve `social.posts` kolon adlarıdır — damganın kendisi sunucuda durur, istemci
# yalnız opak makbuz kimliğini taşır ve kalıcı-kayıt isteğinde geri verir.
#
# Küme `SectorPackageContext` alanlarından TÜRETİLMEDİ, bilinçle: o dataclass
# `content` ve `version` gibi genel adlar taşıyor ve caption yanıtına bir gün
# meşru bir `content`/`version` alanı eklenirse sessizce düşürülürdü. Burada
# kapatılan sınıf "paket kimlik ÇİFTİ"dir; çiftin taşındığı ad kümesi kapalıdır.
PACKAGE_IDENTITY_KEYS = frozenset({"package_id", "package_version"})


class CaptionGenerationOut(BaseModel):
    """Caption üretim yanıtı — ham paket çifti istemciye DÖNMEZ.

    `extra="allow"`: caption üreticisinin alan kümesi şablona göre değişir
    (tekli/carousel/video), bu şema onu daraltmaz. Daralttığı tek şey paket
    kimliğidir.

    Düşürme sessiz DEĞİLDİR (uyarı log'lanır) ama istisna da fırlatmaz: bir gün
    yanlışlıkla eklenen bir alan yüzünden tüm caption ucunun ölmesi, sözleşmeyi
    korumaktan daha pahalı bir sonuç olurdu. Deny-by-default yön korunur.
    """

    model_config = ConfigDict(extra="allow")

    generation_id: UUID | None = None

    @model_validator(mode="before")
    @classmethod
    def _drop_package_identity(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        leaked = PACKAGE_IDENTITY_KEYS & set(data)
        if not leaked:
            return data
        logger.warning(
            "caption yanıtından paket kimlik alanı düşürüldü: %s "
            "(K-07: istemci yalnız opak generation_id taşır)",
            sorted(leaked),
        )
        return {k: v for k, v in data.items() if k not in PACKAGE_IDENTITY_KEYS}


class ErrResponse(BaseModel):
    success: bool = False
    error: str


# ─── Auth ───────────────────────────────────────────────────────────────────

class UserMe(BaseModel):
    id: str
    email: str


# ─── Brand ──────────────────────────────────────────────────────────────────

class BrandCreate(BaseModel):
    workspace_id: UUID
    name: str
    description: str | None = None
    website_url: str | None = None
    sector: str | None = None
    # Alt sektör ataması (spec §7.3). Varsayılan BOŞtur — boş alan bugünkü
    # paketsiz yoldur. Şemada tipli durması şart: Pydantic şemada olmayan alanı
    # sessizce düşürür, yani alan burada yoksa istek router'a hiç ulaşmaz ve
    # kullanıcının teyit ettiği atama sessizce kaybolurdu.
    sub_sector_id: UUID | None = None


class BrandKitUpdate(BaseModel):
    colors: list[str] | None = None
    fonts: dict | None = None
    social_handle: str | None = None
    hashtags: list[str] | None = None
    tonality: str | None = None
    timezone: str | None = None
    voiceover: str | None = None
    logo_overlay: dict | None = None
    intro_video: dict | None = None
    # Kanal envanteri (spec §12.2). TİPLİ olması şart: Pydantic şemada olmayan
    # alanı sessizce DÜŞÜRÜR, yani alan burada yoksa istek router'a hiç ulaşmaz
    # ve yazım sessizce kaybolurdu. Anahtar uzayının kapalılığı router'daki
    # `_assert_valid_channels` kapısında zorlanır (kapalı küme: sector_packages).
    channels: dict | None = None


class BrandUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    website_url: str | None = None
    sector: str | None = None
    brand_kit: dict | None = None
    logo_light_url: str | None = None
    logo_dark_url: str | None = None
    intro_video_url: str | None = None
    is_active: bool | None = None
    # Atamayı BOŞALTMAK açıkça `null` göndermekle olur. Router bu alanı
    # `model_fields_set` ile okur: `exclude_none` serileştirmesi açık `null`'ı
    # düşürürdü ve kullanıcı yanlış atamasını hiçbir zaman geri alamazdı
    # (spec §7.5 düzeltme yolu).
    sub_sector_id: UUID | None = None
    # İstemcinin en son GÖRDÜĞÜ sürüm (satırın güncellenme anı). Doluysa yazım
    # koşullu olur: satır o sürümden ilerlemişse yazım REDDEDİLİR. Boş
    # bırakılabilir — sürüm göndermeyen çağıranlar bugünkü davranışı görür.
    #
    # Bu alan bir SÜTUN DEĞİLDİR; router onu güncellenecek alanlar kümesinden
    # ayıklar. Ayıklamazsa `exclude_none` onu yazılacak bir alan sanardı.
    expected_version: datetime | None = None


class BrandOut(BaseModel):
    id: UUID
    workspace_id: UUID
    name: str
    description: str | None
    website_url: str | None
    sector: str | None
    sector_id: UUID | None = None
    sub_sector_id: UUID | None = None
    sector_slug: str | None = None
    sector_display_name: str | None = None
    brand_kit: dict
    logo_light_url: str | None
    logo_dark_url: str | None
    intro_video_url: str | None
    is_active: bool
    created_at: datetime


# ─── Phase 6 — Trend Sistemi ────────────────────────────────────────────────

class SectorOut(BaseModel):
    id: UUID
    slug: str
    display_name: str
    parent_sector_id: UUID | None = None
    keywords: list[str]


class TrendItem(BaseModel):
    title: str
    source: str
    relevance_score: int
    summary: str | None = None
    content_opportunity: str | None = None
    suggested_prompt: str | None = None
    url: str | None = None


class TrendUsageOut(BaseModel):
    year_month: str
    layer_b_count: int
    layer_b_limit: int
    layer_c_count: int
    layer_c_limit: int


class SectorReportOut(BaseModel):
    id: UUID
    sector_id: UUID
    brand_id: UUID | None
    pdf_url: str | None
    status: str
    error_message: str | None
    generated_at: datetime


# ─── Phase 9 — Ürün/Hizmet Kütüphanesi ──────────────────────────────────────

class ProductCreate(BaseModel):
    brand_id: UUID
    type: str  # "product" | "service"
    name: str
    description: str | None = None
    highlight: str | None = Field(default=None, max_length=60)
    tags: list[str] = []
    is_active: bool = True


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    highlight: str | None = Field(default=None, max_length=60)
    tags: list[str] | None = None
    is_active: bool | None = None


class ProductImageOut(BaseModel):
    id: UUID
    product_id: UUID
    image_url: str
    image_key: str
    is_primary: bool
    position: int
    label: str | None = None
    mime_type: str | None = None
    size_kb: int | None = None
    created_at: datetime


class ProductOut(BaseModel):
    id: UUID
    brand_id: UUID
    type: str
    name: str
    description: str | None
    highlight: str | None = None
    tags: list[str]
    # Ana görsel (denormalize) — product_images tablosundaki is_primary=true satırın kopyası.
    image_url: str | None
    image_key: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    document_count: int = 0
    # Sprint 1 (Çoklu görsel) — ürünün tüm görselleri (position'a göre sıralı).
    images: list[ProductImageOut] = []


# ─── Post ───────────────────────────────────────────────────────────────────

class PostGenerate(BaseModel):
    brand_id: UUID
    # K-07 damga taşıma sözleşmesinin TÜKETİCİ ucu (plan Task 12). Üretici uç
    # (`/generate-caption`) opak makbuzu döndürür; istemci onu buraya AYNEN geri
    # verir. Ham paket çifti hiçbir yönde istemciye emanet edilmez.
    generation_id: UUID | None = None
    content_type: str  # image | carousel | special_day | quote
    content_category: str | None = None  # product | service | corporate (legacy, template_id yoksa kullanılır)
    prompt: str | None = None
    user_text: str | None = None
    document_ids: list[UUID] = []
    aspect_ratio: str = "1:1"
    platforms: list[str] = []
    # special_day
    special_day_name: str | None = None   # "Anneler Günü", "Ramazan Bayramı 1. Gün" vb.
    special_day_category: str | None = None  # national | religious | commercial
    # quote
    quote_text: str | None = None
    quote_author: str | None = None
    # Phase 7 — Sektör-Spesifik Şablon Sistemi
    template_id: str | None = None                       # templates_data.py'de tanımlı
    template_fields: dict | None = None                  # yapısal form verisi
    platform_captions: dict | None = None                # caption-gen endpoint çıktısı
    image_prompt: str | None = None                      # Akış C'de kullanıcı-editlenmiş görsel prompt'u
    image_prompts: list[str] | None = None               # Phase 12 — Carousel slide bazlı prompt dizisi
    # Phase 8 Sprint 1 — Per-post logo overlay override
    # NULL = brand_kit.logo_overlay.enabled'a uy, true/false = override
    use_logo_overlay: bool | None = None
    # Phase 8 Sprint 1 Part 3 — Template image text overlay per-post override.
    # NULL = template.imageTextOverlay.fields default'unu kullan; []/listte field yoksa
    # overlay basılmaz; dolu listte yalnızca listte geçen field'lar basılır.
    image_text_fields: list[str] | None = None
    # Phase 9 Sprint 6 — Ürün/Hizmet image-edit routing.
    # Set ise ve ürünün image_url'i varsa fal.ai nano-banana-2/edit tetiklenir.
    # Ürünün image_url'i yoksa FLUX text-to-image fallback (S4 kararı).
    product_id: UUID | None = None
    # Sprint 1 (Çoklu Ürün Görseli) — kullanıcının seçtiği ürün görselleri.
    # None/boş = ürünün ana görseli kullanılır (eski davranış, geriye dönük).
    # Doluysa: bu görsellerin URL'leri Nano Banana 2 edit'e ref olarak verilir
    # (max 5, fal sweet spot). Tek görsel modunda tüm seçilenler ref olur;
    # carousel modunda `carousel_image_mode`'a göre slide'lara dağıtılır.
    product_image_ids: list[UUID] | None = None
    # Sprint 1 (Çoklu Ürün Görseli) — carousel slide × görsel eşleme modu.
    # 'auto': edit_ref_urls round-robin (slide N → görsel N % len)
    # 'primary_only': tüm slide'lar ana görseli kullanır (eski davranışla aynı)
    # 'manual': Sprint 4'e ertelendi; şu an gelirse 'auto' fallback
    carousel_image_mode: str = "auto"
    # Sprint 3 (Özel Gün) — Marka referans görseli (Atatürk fotoğrafı, kurucu portre vb.)
    # Doluysa Nano Banana 2 edit yolu kullanılır; image_prompt sahne kompozisyonunu
    # tarif eder, merkezdeki kişi/objeyi 'the reference subject' olarak bırakır.
    # Yalnız `imageSubType='general'` modunda gönderilir; ürünle birlikte gelmez.
    scene_reference_image_url: str | None = None


class ShortVideoGenerate(BaseModel):
    brand_id: UUID
    # K-07 damga taşıma sözleşmesinin TÜKETİCİ ucu (plan Task 12) — kısa video
    # kalıcı kaydı stage-1'de doğar, makbuz oraya taşınır.
    generation_id: UUID | None = None
    prompt: str
    script: str = ""
    voice: str = "qSeXEcewz7tA0Q0qk9fH"
    document_ids: list[UUID] = []
    aspect_ratio: str = "9:16"
    platforms: list[str] = []
    template_id: str | None = None
    template_fields: dict | None = None
    platform_captions: dict | None = None
    intro_position: str = "none"
    product_id: UUID | None = None
    # Kullanıcının "Bu video ne anlatsın?" alanına yazdığı ham metin.
    # Boş ise sahne markaya/ürüne göre kurulur; doluysa sahne bu tarife göre üretilir
    # ve ürün resmi yerine FLUX still oluşturulur.
    visual_brief: str = ""
    # Özel gün modunda (ozelgun-shortvideo-sablon) doldurulur — caption_generator
    # tatil tonuna yönlendirme için kullanır.
    special_day_name: str | None = None
    special_day_category: str | None = None
    # K-02 = A: caption aşamasındaki model çağrısının seçtiği kamera hareketi.
    # İstemci TAŞIR, sunucu paketin havuzuna karşı DOĞRULAR (üye değilse
    # kullanılmaz) — serbest metin video üreticisine geçemez.
    motion_prompt: str | None = None
    # Sprint 3 — marka referans görseli (Stage 1 still'inde Nano Banana edit ref'i).
    # Doluysa scene_reference + brief senaryosu çalışır.
    scene_reference_image_url: str | None = None


class GenerateScriptRequest(BaseModel):
    brand_id: UUID
    prompt: str


class PostCreate(BaseModel):
    brand_id: UUID
    content_type: str
    content_category: str | None = None
    prompt: str | None = None
    user_text: str | None = None
    aspect_ratio: str = "1:1"
    platforms: list[str] = []
    scheduled_at: datetime | None = None


class PostUpdate(BaseModel):
    caption: str | None = None
    hashtags: list[str] | None = None


class PostOut(BaseModel):
    id: UUID
    brand_id: UUID
    content_type: str
    content_category: str | None
    status: str
    prompt: str | None
    user_text: str | None
    output_url: str | None
    thumbnail_url: str | None
    caption: str | None
    hashtags: list[str] | None
    aspect_ratio: str | None
    platforms: list[str] | None
    scheduled_at: datetime | None
    published_at: datetime | None
    fal_job_id: str | None
    created_at: datetime
    updated_at: datetime


# ─── Storage ────────────────────────────────────────────────────────────────

class PresignedUrlRequest(BaseModel):
    path: str
    content_type: str
    expires: int = 3600
