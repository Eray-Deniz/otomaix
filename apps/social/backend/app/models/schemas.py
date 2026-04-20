from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


# ─── Common response wrappers ───────────────────────────────────────────────

class OkResponse(BaseModel):
    success: bool = True
    data: Any = None


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


class BrandOut(BaseModel):
    id: UUID
    workspace_id: UUID
    name: str
    description: str | None
    website_url: str | None
    sector: str | None
    sector_id: UUID | None = None
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


# ─── Post ───────────────────────────────────────────────────────────────────

class PostGenerate(BaseModel):
    brand_id: UUID
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
    # Phase 8 Sprint 1 — Per-post logo overlay override
    # NULL = brand_kit.logo_overlay.enabled'a uy, true/false = override
    use_logo_overlay: bool | None = None


class FacelessVideoGenerate(BaseModel):
    brand_id: UUID
    prompt: str
    voice: str = "tr-TR-EmelNeural"
    document_ids: list[UUID] = []
    aspect_ratio: str = "9:16"
    platforms: list[str] = []


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
