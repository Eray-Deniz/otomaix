"""Phase 7 — Sektör-Spesifik Şablon Sistemi Pydantic modelleri.

Alan isimleri **camelCase** (frontend TypeScript ile birebir eşleşir).
Şablon tanımları `app/core/templates_data.py` içinde, frontend'e `GET /templates`
endpoint'i üzerinden JSON olarak sunulur.
"""
from typing import Literal, Optional

from pydantic import BaseModel, Field


class TemplateFormField(BaseModel):
    id: str
    label: str
    type: Literal["text", "textarea", "number", "select", "multi-select", "url"]
    placeholder: Optional[str] = None
    helpText: Optional[str] = None
    required: bool = False
    defaultValue: Optional[str | int | float] = None
    validation: Optional[dict] = None
    options: Optional[list[dict]] = None
    suffix: Optional[str] = None
    group: Optional[str] = None


class PlatformOverride(BaseModel):
    captionStyle: Optional[Literal["long", "medium", "short"]] = None
    maxHashtags: Optional[int] = None
    toneAdjustment: Optional[str] = None
    useFirstComment: Optional[bool] = None
    additionalGuidance: Optional[str] = None


class TemplateOutput(BaseModel):
    aspectRatioSuggestion: Optional[Literal["1:1", "4:5", "9:16", "2:3"]] = None
    slideCount: Optional[dict] = None  # {min, max, default}


class TemplatePromptExample(BaseModel):
    input: dict
    output: dict


class TemplatePrompt(BaseModel):
    guidance: str
    examples: Optional[list[TemplatePromptExample]] = None
    priority: list[str] = Field(
        default_factory=lambda: ["form_fields", "brand_kit", "rag_docs"]
    )


class TemplateDefaults(BaseModel):
    suggestedCTAs: list[str] = Field(default_factory=list)
    suggestedHashtags: list[str] = Field(default_factory=list)
    disclaimer: Optional[str] = None


class Template(BaseModel):
    id: str
    version: int = 1
    name: str
    description: str
    icon: str
    sectors: list[str]
    contentTypes: list[str]
    status: Literal["active", "deprecated"] = "active"
    formFields: list[TemplateFormField] = Field(default_factory=list)
    output: TemplateOutput = Field(default_factory=TemplateOutput)
    prompt: TemplatePrompt
    defaults: TemplateDefaults = Field(default_factory=TemplateDefaults)
    platformOverrides: Optional[dict[str, PlatformOverride]] = None
    tags: Optional[list[str]] = None
    order: Optional[int] = None
