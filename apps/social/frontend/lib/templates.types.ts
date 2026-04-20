// Phase 7 — Sektör-Spesifik Şablon Sistemi TypeScript interface'leri.
// Backend Pydantic modelleriyle (app/models/templates.py) birebir eşleşir.
// Alan isimleri camelCase — JSON transport düzeyinde hiç dönüştürme yok.

export interface TemplateFormField {
  id: string
  label: string
  type: "text" | "textarea" | "number" | "select" | "multi-select" | "url"
  placeholder?: string
  helpText?: string
  required: boolean
  defaultValue?: string | number
  validation?: {
    min?: number
    max?: number
    minLength?: number
    maxLength?: number
    pattern?: string
  }
  options?: Array<{ value: string; label: string }>
  suffix?: string
  group?: string
}

export interface PlatformOverride {
  captionStyle?: "long" | "medium" | "short"
  maxHashtags?: number
  toneAdjustment?: string
  useFirstComment?: boolean
  additionalGuidance?: string
}

export interface TemplateOutput {
  aspectRatioSuggestion?: "1:1" | "4:5" | "9:16" | "2:3"
  slideCount?: { min: number; max: number; default: number }
}

export interface TemplatePromptExample {
  input: Record<string, unknown>
  output: { caption: string; imagePrompt?: string }
}

export interface TemplatePrompt {
  guidance: string
  examples?: TemplatePromptExample[]
  priority: string[]
}

export interface TemplateDefaults {
  suggestedCTAs: string[]
  suggestedHashtags: string[]
  disclaimer?: string
}

export interface ImageTextOverlaySpec {
  fields: string[]
  position?: "top-left" | "top-right" | "bottom-left" | "bottom-right"
}

export interface Template {
  id: string
  version: number
  name: string
  description: string
  icon: string
  sectors: string[]
  contentTypes: string[]
  status: "active" | "deprecated"
  formFields: TemplateFormField[]
  output: TemplateOutput
  prompt: TemplatePrompt
  defaults: TemplateDefaults
  platformOverrides?: {
    instagram?: PlatformOverride
    linkedin?: PlatformOverride
    twitter?: PlatformOverride
    facebook?: PlatformOverride
    tiktok?: PlatformOverride
    threads?: PlatformOverride
    pinterest?: PlatformOverride
    bluesky?: PlatformOverride
  }
  imageTextOverlay?: ImageTextOverlaySpec
  tags?: string[]
  order?: number
}
