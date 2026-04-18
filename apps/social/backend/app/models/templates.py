"""Phase 7 — Sektör-Spesifik Şablon Sistemi Pydantic modelleri.

Şablonlar backend'de `app/core/templates_data.py` içinde tanımlıdır.
`GET /templates` bu modelleri JSON olarak frontend'e döndürür.
"""
from typing import Literal

from pydantic import BaseModel, Field


FieldType = Literal["text", "number", "textarea", "select", "date", "boolean"]
ContentType = Literal["image", "carousel", "video", "special_day", "quote"]


class TemplateFormField(BaseModel):
    id: str
    label: str
    type: FieldType
    placeholder: str | None = None
    required: bool = False
    options: list[dict] | None = None
    suffix: str | None = None
    help_text: str | None = None
    max_length: int | None = None


class PlatformOverride(BaseModel):
    """Platform-özel caption/hashtag override (ör. LinkedIn daha uzun)."""
    platform: str
    max_chars: int | None = None
    tone_hint: str | None = None
    hashtag_count: int | None = None


class TemplateOutput(BaseModel):
    """Şablonun ürettiği çıktı yapısı (caption/image formatı)."""
    caption_max_chars: int = 2200
    hashtag_count_min: int = 3
    hashtag_count_max: int = 8
    platform_overrides: list[PlatformOverride] = Field(default_factory=list)


class TemplatePromptExample(BaseModel):
    """Few-shot örneği — Claude'a gösterilecek örnek çıktı."""
    input_summary: str
    caption: str
    hashtags: list[str]


class TemplatePrompt(BaseModel):
    """Şablonun prompt mühendisliği verisi."""
    guidance: str
    tone_rules: list[str] = Field(default_factory=list)
    must_include: list[str] = Field(default_factory=list)
    must_avoid: list[str] = Field(default_factory=list)
    examples: list[TemplatePromptExample] = Field(default_factory=list)


class TemplateDefaults(BaseModel):
    """Şablon seçildiğinde önerilen varsayılan değerler."""
    ctas: list[str] = Field(default_factory=list)
    hashtags: list[str] = Field(default_factory=list)
    aspect_ratio: str = "1:1"
    platforms: list[str] = Field(default_factory=list)
    disclaimer: str | None = None


class Template(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    sectors: list[str]           # ["e-ticaret-perakende"] veya ["*"] = tüm sektörler
    content_types: list[ContentType]
    form_fields: list[TemplateFormField]
    prompt: TemplatePrompt
    defaults: TemplateDefaults
    output: TemplateOutput = Field(default_factory=TemplateOutput)
    version: str = "1.0"
