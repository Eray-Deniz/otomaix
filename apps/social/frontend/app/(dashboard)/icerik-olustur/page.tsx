'use client'

export const dynamic = 'force-dynamic'

import { useState, useCallback, useEffect, useMemo, useRef, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { toast } from 'sonner'
import { analytics } from '@/lib/analytics'
import { Loader2, Wand2, RefreshCw, Calendar, Send, X, Lightbulb, FileText, Package, Wrench } from 'lucide-react'
import Image from 'next/image'
import { cn } from '@/lib/utils'
import { UpgradeModal } from '@/components/billing/UpgradeModal'
import { TemplateGrid } from '@/components/templates/TemplateGrid'
import { DynamicForm } from '@/components/templates/DynamicForm'
import { CaptionEditor, type CaptionData } from '@/components/templates/CaptionEditor'
import { CaptionPreview } from '@/components/templates/CaptionPreview'
import { fetchActiveMediaModels, type ActiveMediaModels } from '@/lib/api/media-models'
import { fetchTemplateById } from '@/lib/api/templates'
import type { Template } from '@/lib/templates.types'
import { fetchProducts } from '@/lib/api/products'
import type { Product } from '@/lib/products.types'

// ─── Types ────────────────────────────────────────────────────────────────────

interface BrandDocument {
  id: string
  name: string
  file_type: string | null
  file_size_kb: number | null
}

interface TurkishVoice {
  id: string
  name: string
  gender: string
}

type ContentType = 'image' | 'carousel' | 'video' | 'special_day' | 'quote'
type AspectRatio = string
type Step = 1 | 2 | 3
type TemplateMode = 'template' | 'free'
type TemplatePhase = 'pick' | 'form' | 'caption'

// Phase 8 Sprint 2 — Görsel tipi için varsayılan şablon.
// `contentType='image'` + "Devam Et" tıklanınca otomatik seçilir; şablon grid'i gösterilmez.
const DEFAULT_IMAGE_TEMPLATE_ID = 'genel-gorsel-sablon'
const DEFAULT_CAROUSEL_TEMPLATE_ID = 'carousel-genel-sablon'
const DEFAULT_VIDEO_TEMPLATE_ID = 'facelessvideo-genel-sablon'

interface CarouselSlide {
  order: number
  image_url: string | null
  image_prompt: string
  fal_job_id: string | null
}

interface GeneratedPost {
  post_id: string
  status: string
  output_url?: string
  caption?: string
  hashtags?: string[]
  slides?: CarouselSlide[]
  slide_count?: number
  // Faceless video
  script?: string
  audio_url?: string
  duration_estimate?: number
}

interface Holiday {
  date: string
  name_tr: string
  category: string
}

// ─── Constants ────────────────────────────────────────────────────────────────

const CONTENT_TYPES = [
  { id: 'image' as ContentType, label: 'Görsel', icon: '🖼️' },
  { id: 'carousel' as ContentType, label: 'Carousel', icon: '📱' },
  { id: 'video' as ContentType, label: 'Video (Faceless)', icon: '🎬' },
  { id: 'special_day' as ContentType, label: 'Özel Gün', icon: '🎉' },
  { id: 'quote' as ContentType, label: 'Alıntı', icon: '💬' },
]

const ASPECT_RATIOS: { id: AspectRatio; label: string; desc: string; icon: string }[] = [
  { id: '1:1', label: '1:1', desc: 'Kare (Tüm Platformlar)', icon: '⬜' },
  { id: '9:16', label: '9:16', desc: 'Dikey (Reels/Stories/TikTok)', icon: '📱' },
  { id: '4:5', label: '4:5', desc: 'Portre (Instagram/Facebook Feed)', icon: '🖼️' },
  { id: '2:3', label: '2:3', desc: 'Uzun Dikey (Pinterest)', icon: '📌' },
  { id: '16:9', label: '16:9', desc: 'Yatay (YouTube/LinkedIn)', icon: '📺' },
]

const PLATFORMS = [
  { id: 'instagram', label: 'Instagram' },
  { id: 'tiktok', label: 'TikTok' },
  { id: 'linkedin', label: 'LinkedIn' },
  { id: 'facebook', label: 'Facebook' },
  { id: 'youtube', label: 'YouTube' },
  { id: 'twitter', label: 'Twitter / X' },
  { id: 'pinterest', label: 'Pinterest' },
]

// ─── Step indicator ───────────────────────────────────────────────────────────

function StepIndicator({ step }: { step: Step }) {
  const steps = [
    { n: 1, label: 'Tip Seçimi' },
    { n: 2, label: 'İçerik Detayları' },
    { n: 3, label: 'Önizleme' },
  ]
  return (
    <div className="flex items-center gap-2 mb-8">
      {steps.map((s, i) => (
        <div key={s.n} className="flex items-center gap-2">
          <div className={cn(
            'w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors',
            step === s.n ? 'bg-blue-600 text-white' :
            step > s.n ? 'bg-blue-100 text-blue-700' :
            'bg-gray-100 text-gray-400'
          )}>
            {step > s.n ? '✓' : s.n}
          </div>
          <span className={cn(
            'text-sm',
            step >= s.n ? 'text-gray-800 font-medium' : 'text-gray-400'
          )}>
            {s.label}
          </span>
          {i < steps.length - 1 && (
            <div className={cn('w-8 h-px mx-1', step > s.n ? 'bg-blue-300' : 'bg-gray-200')} />
          )}
        </div>
      ))}
    </div>
  )
}

// ─── Main page ─────────────────────────────────────────────────────────────────

export default function IcerikOlusturPage() {
  return (
    <Suspense fallback={<div className="p-8 text-gray-400 text-sm">Yükleniyor...</div>}>
      <IcerikOlusturInner />
    </Suspense>
  )
}

function IcerikOlusturInner() {
  const currentBrand = useAppStore((s) => s.currentBrand)
  const router = useRouter()
  const searchParams = useSearchParams()

  // Step state
  const [step, setStep] = useState<Step>(1)

  // Step 1
  const [contentType, setContentType] = useState<ContentType>('image')
  // Phase 9 Sprint 9 — Görsel alt tipi: genel text-to-image veya ürün/hizmet image-to-image
  type ImageSubType = 'general' | 'product'
  const [imageSubType, setImageSubType] = useState<ImageSubType>('general')
  // Phase 9 Sprint 9B — Ürün/Hizmet seçici
  const [availableProducts, setAvailableProducts] = useState<Product[]>([])
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const [loadingProducts, setLoadingProducts] = useState(false)

  // Phase 7 — Template system (image/carousel)
  const [mode, setMode] = useState<TemplateMode>('template')
  const [phase, setPhase] = useState<TemplatePhase>('pick')
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null)
  const [templateFields, setTemplateFields] = useState<Record<string, unknown>>({})
  // Phase 8 Sprint 1 Part 3 — Template image text overlay per-post override.
  // null = template.imageTextOverlay default'u kullanılır; []/dolu liste ise override.
  const [imageTextFields, setImageTextFields] = useState<string[] | null>(null)
  const [captionData, setCaptionData] = useState<CaptionData | null>(null)
  const [loadingCaption, setLoadingCaption] = useState(false)
  const [loadingDefaultTemplate, setLoadingDefaultTemplate] = useState(false)

  // Step 2
  const [prompt, setPrompt] = useState('')
  const [ideas, setIdeas] = useState<string[]>([])
  const [loadingIdeas, setLoadingIdeas] = useState(false)
  const [aspectRatio, setAspectRatio] = useState<AspectRatio>('1:1')
  const [mediaModels, setMediaModels] = useState<ActiveMediaModels | null>(null)
  const [platforms, setPlatforms] = useState<string[]>(['instagram'])
  const [availableDocs, setAvailableDocs] = useState<BrandDocument[]>([])
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([])
  // Phase 8 Sprint 1 — per-post logo overlay override. null = marka varsayılanına uy,
  // true/false = bu post için açıkça override et.
  const [useLogoOverlay, setUseLogoOverlay] = useState<boolean | null>(null)

  // Faceless video — Step 2
  const [script, setScript] = useState('')
  const [voices, setVoices] = useState<TurkishVoice[]>([])
  const [selectedVoice, setSelectedVoice] = useState('ctoYieZ4J7WwcdhujpMq')
  const [durationEstimate, setDurationEstimate] = useState<number | null>(null)
  // Intro/outro pozisyonu (video için) — none/start/end/both
  const [introPosition, setIntroPosition] = useState<string>('none')
  const [brandHasIntro, setBrandHasIntro] = useState(false)

  // Özel Gün — Step 2
  const [holidays, setHolidays] = useState<Holiday[]>([])
  const [selectedHoliday, setSelectedHoliday] = useState<Holiday | null>(null)

  // Alıntı — Step 2
  const [quoteText, setQuoteText] = useState('')
  const [quoteAuthor, setQuoteAuthor] = useState('')

  // Step 3
  const [generating, setGenerating] = useState(false)
  const [upgradeMessage, setUpgradeMessage] = useState<string | null>(null)
  const [generatedPost, setGeneratedPost] = useState<GeneratedPost | null>(null)
  const [caption, setCaption] = useState('')
  const [hashtags, setHashtags] = useState<string[]>([])
  const [newHashtag, setNewHashtag] = useState('')
  const [publishing, setPublishing] = useState(false)
  const publishingRef = useRef(false)
  const [scheduling, setScheduling] = useState(false)
  const [showScheduleDialog, setShowScheduleDialog] = useState(false)
  const [scheduleAt, setScheduleAt] = useState('')

  // Query-param prefill (ör. trendler sayfasından "İçerik Üret" butonu)
  useEffect(() => {
    const qPrompt = searchParams?.get('prompt')
    const qType = searchParams?.get('type') as ContentType | null
    const qAspect = searchParams?.get('aspect') as AspectRatio | null
    if (!qPrompt && !qType) return
    if (qPrompt) setPrompt(qPrompt)
    if (qType && CONTENT_TYPES.some((t) => t.id === qType)) setContentType(qType)
    if (qAspect && ASPECT_RATIOS.some((r) => r.id === qAspect)) setAspectRatio(qAspect)
    setStep(2)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Görsel/Carousel hazır olana kadar polling
  useEffect(() => {
    if (!generatedPost?.post_id || generatedPost.output_url || generatedPost.status === 'failed') return
    let cancelled = false
    const poll = async () => {
      if (cancelled) return
      const res = await api.get<GeneratedPost>(`/posts/${generatedPost.post_id}`)
      if (cancelled) return
      if (res.success && res.data?.output_url) {
        setGeneratedPost(prev => prev ? {
          ...prev,
          output_url: res.data!.output_url,
          status: 'ready',
          slides: res.data!.slides ?? prev.slides,
        } : prev)
      } else if (res.success && res.data?.status === 'failed') {
        toast.error('Görsel üretilemedi — farklı bir en-boy oranı veya açıklama ile tekrar dene')
        setGeneratedPost(prev => prev ? { ...prev, status: 'failed' } : prev)
      } else if (!cancelled) {
        if (res.success && res.data?.slides) {
          setGeneratedPost(prev => prev ? { ...prev, slides: res.data!.slides } : prev)
        }
        setTimeout(poll, 3000)
      }
    }
    const timer = setTimeout(poll, 3000)
    return () => { cancelled = true; clearTimeout(timer) }
  }, [generatedPost?.post_id, generatedPost?.output_url, generatedPost?.status])

  // ── Fetch brand documents & voices ──────────────────────────────────────────

  useEffect(() => {
    async function fetchDocs() {
      if (!currentBrand?.id) return
      const res = await api.get<BrandDocument[]>(`/documents?brand_id=${currentBrand.id}`)
      if (res.success && res.data) setAvailableDocs(res.data)
    }
    fetchDocs()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentBrand?.id])

  // Phase 9 Sprint 9B — Aktif ürünleri çek (ürün/hizmet modu seçilince)
  useEffect(() => {
    if (!currentBrand?.id || imageSubType !== 'product') return
    let cancelled = false
    setLoadingProducts(true)
    fetchProducts(currentBrand.id, { active: true }).then((res) => {
      if (cancelled) return
      setAvailableProducts(res.success && res.data ? res.data.products : [])
      setLoadingProducts(false)
    })
    return () => { cancelled = true }
  }, [currentBrand?.id, imageSubType])

  // imageSubType değişince ilgili state'leri sıfırla
  useEffect(() => {
    setSelectedProduct(null)
    setSelectedDocIds([])
    setCaptionData(null)
  }, [imageSubType])

  // Marka değişince logo filigran varsayılanını çek (brand_kit.logo_overlay.enabled).
  // useLogoOverlay null ise marka default'u kullanılır, switch UI bu değere göre başlangıç alır.
  useEffect(() => {
    async function fetchBrandKit() {
      if (!currentBrand?.id) return
      const res = await api.get<{ brand_kit?: Record<string, unknown> | null; intro_video_url?: string | null }>(`/brands/${currentBrand.id}`)
      if (res.success && res.data) {
        const kit = res.data.brand_kit || {}
        const rawOverlay = kit['logo_overlay']
        const overlay = (rawOverlay && typeof rawOverlay === 'object') ? (rawOverlay as Record<string, unknown>) : {}
        setUseLogoOverlay(Boolean(overlay.enabled))
        setBrandHasIntro(Boolean(res.data.intro_video_url))
      }
    }
    fetchBrandKit()
  }, [currentBrand?.id])

  useEffect(() => {
    async function fetchVoices() {
      const res = await api.get<TurkishVoice[]>('/posts/voices/turkish')
      if (res.success && res.data) setVoices(res.data)
    }
    fetchVoices()
  }, [])

  useEffect(() => {
    async function fetchHolidays() {
      const year = new Date().getFullYear()
      const res = await api.get<Holiday[]>(`/calendar/holidays?year=${year}`)
      if (res.success && res.data) setHolidays(res.data)
    }
    fetchHolidays()
  }, [])

  useEffect(() => {
    fetchActiveMediaModels().then((m) => { if (m) setMediaModels(m) })
  }, [])

  const availableAspectRatios = useMemo(() => {
    const supported = contentType === 'video'
      ? mediaModels?.faceless_background.supported_ratios
      : mediaModels?.image.supported_ratios
    if (!supported) return ASPECT_RATIOS
    const supportedSet = new Set(supported)
    return ASPECT_RATIOS.filter((ar) => supportedSet.has(ar.id))
  }, [contentType, mediaModels])

  useEffect(() => {
    if (availableAspectRatios.length === 0) return
    if (!availableAspectRatios.some((ar) => ar.id === aspectRatio)) {
      setAspectRatio(availableAspectRatios[0].id)
    }
  }, [availableAspectRatios, aspectRatio])

  function toggleDoc(id: string) {
    setSelectedDocIds((prev) =>
      prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id]
    )
  }

  // ── Step 2 helpers ──────────────────────────────────────────────────────────

  const fetchIdeas = useCallback(async () => {
    if (!currentBrand?.id) { toast.error('Önce bir marka seçin'); return }
    analytics.ideaSuggestionUsed()
    setLoadingIdeas(true)
    const res = await api.post<{ ideas: string[] }>('/ai/suggest-ideas', {
      brand_id: currentBrand.id,
      content_type: contentType,
      template_id: selectedTemplate?.id ?? null,
      template_fields: selectedTemplate ? templateFields : null,
      prompt: prompt.trim() || null,
      document_ids: selectedDocIds.length > 0 ? selectedDocIds : null,
      platforms: platforms.length > 0 ? platforms : null,
      count: 5,
    })
    if (res.success && res.data?.ideas) {
      setIdeas(res.data.ideas)
    } else if (!res.success && res.error === 'rate_limit') {
      toast.error(`Çok fazla istek. ${res.retry_after ?? 60} saniye sonra tekrar deneyin.`)
    } else {
      toast.error('Fikirler alınamadı — lütfen tekrar deneyin')
    }
    setLoadingIdeas(false)
  }, [currentBrand?.id, contentType, platforms, prompt, selectedDocIds, selectedTemplate, templateFields])

  function togglePlatform(id: string) {
    setPlatforms((prev) =>
      prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]
    )
  }

  // ── Step 3: Generate ────────────────────────────────────────────────────────

  async function handleGenerate() {
    if (!currentBrand?.id) { toast.error('Önce bir marka seçin'); return }

    if (contentType === 'special_day' && !selectedHoliday) {
      toast.error('Lütfen bir özel gün seçin')
      return
    }
    if (contentType === 'quote' && !quoteText.trim()) {
      toast.error('Lütfen alıntı metnini girin')
      return
    }
    // Image/carousel/video: caption üretilmiş olmalı (Akış C unified)
    if (['image', 'carousel', 'video'].includes(contentType)) {
      if (!captionData) {
        toast.error('Önce gönderi metnini üretin')
        return
      }
    }
    if (contentType === 'video' && !script.trim()) {
      toast.error('Lütfen bir script girin veya üretin')
      return
    }

    analytics.contentCreationStarted(contentType)
    if (selectedDocIds.length > 0) analytics.documentReferenceUsed(selectedDocIds.length)
    const genStart = Date.now()
    setGenerating(true)
    setStep(3)

    if (contentType === 'video') {
      // Faceless video pipeline — şablon tabanlı
      const isTemplateMode = mode === 'template' && selectedTemplate
      const res = await api.post<GeneratedPost>('/posts/generate-faceless-video', {
        brand_id: currentBrand.id,
        prompt: prompt.trim() || captionData!.image_prompt || '',
        script: script.trim(),
        voice: selectedVoice,
        document_ids: selectedDocIds,
        aspect_ratio: aspectRatio,
        platforms,
        template_id: isTemplateMode ? selectedTemplate.id : null,
        template_fields: isTemplateMode ? templateFields : null,
        platform_captions: captionData!.platform_captions,
        intro_position: introPosition,
        product_id: selectedProduct?.id ?? null,
      })
      setGenerating(false)
      if (res.success && res.data) {
        analytics.contentGenerated(contentType, Math.round((Date.now() - genStart) / 1000))
        setGeneratedPost(res.data)
        setCaption(captionData!.default_caption || '')
        setHashtags(captionData!.hashtags.length ? captionData!.hashtags : [])
        toast.success('Video üretimi başlatıldı!')
      } else if (!res.success && res.error === 'rate_limit') {
        setStep(2)
        toast.error(`Saatlik limit aşıldı. ${res.retry_after ?? 60} saniye sonra tekrar deneyin.`)
      } else if (!res.success && res.error === 'plan_limit_reached' && res.plan_limit) {
        setStep(2)
        setUpgradeMessage(res.plan_limit.message)
      } else {
        toast.error('Video üretilemedi: ' + (res.error ?? 'Bilinmeyen hata'))
      }
    } else if (contentType === 'special_day') {
      const res = await api.post<GeneratedPost>('/posts/generate', {
        brand_id: currentBrand.id,
        content_type: 'special_day',
        special_day_name: selectedHoliday!.name_tr,
        special_day_category: selectedHoliday!.category,
        prompt: prompt.trim() || null,
        aspect_ratio: aspectRatio,
        platforms,
      })
      setGenerating(false)
      if (res.success && res.data) {
        analytics.contentGenerated(contentType, Math.round((Date.now() - genStart) / 1000))
        setGeneratedPost(res.data)
        setCaption(res.data.caption ?? '')
        setHashtags(res.data.hashtags ?? [])
        toast.success('Özel gün içeriği üretiliyor!')
      } else if (!res.success && res.error === 'rate_limit') {
        setStep(2)
        toast.error(`Saatlik limit aşıldı. ${res.retry_after ?? 60} saniye sonra tekrar deneyin.`)
      } else if (!res.success && res.error === 'plan_limit_reached' && res.plan_limit) {
        setStep(2)
        setUpgradeMessage(res.plan_limit.message)
      } else {
        toast.error('İçerik üretilemedi: ' + (res.error ?? 'Bilinmeyen hata'))
      }
    } else if (contentType === 'quote') {
      const res = await api.post<GeneratedPost>('/posts/generate', {
        brand_id: currentBrand.id,
        content_type: 'quote',
        quote_text: quoteText.trim(),
        quote_author: quoteAuthor.trim() || null,
        aspect_ratio: aspectRatio,
        platforms,
      })
      setGenerating(false)
      if (res.success && res.data) {
        analytics.contentGenerated(contentType, Math.round((Date.now() - genStart) / 1000))
        setGeneratedPost(res.data)
        setCaption(res.data.caption ?? '')
        setHashtags(res.data.hashtags ?? [])
        toast.success('Alıntı görseli üretiliyor!')
      } else if (!res.success && res.error === 'rate_limit') {
        setStep(2)
        toast.error(`Saatlik limit aşıldı. ${res.retry_after ?? 60} saniye sonra tekrar deneyin.`)
      } else if (!res.success && res.error === 'plan_limit_reached' && res.plan_limit) {
        setStep(2)
        setUpgradeMessage(res.plan_limit.message)
      } else {
        toast.error('İçerik üretilemedi: ' + (res.error ?? 'Bilinmeyen hata'))
      }
    } else {
      // Image / Carousel pipeline — Phase 7 unified Akış C (template veya free mod)
      const isTemplateMode = mode === 'template' && selectedTemplate
      const isCarousel = contentType === 'carousel' && captionData!.image_prompts && captionData!.image_prompts.length > 0
      const res = await api.post<GeneratedPost>('/posts/generate', {
        brand_id: currentBrand.id,
        content_type: contentType,
        content_category: null,
        prompt: null,
        user_text: null,
        document_ids: selectedDocIds,
        aspect_ratio: aspectRatio,
        platforms,
        template_id: isTemplateMode ? selectedTemplate.id : null,
        template_fields: isTemplateMode ? templateFields : null,
        platform_captions: captionData!.platform_captions,
        image_prompt: isCarousel ? null : captionData!.image_prompt,
        image_prompts: isCarousel ? captionData!.image_prompts : null,
        use_logo_overlay: useLogoOverlay,
        image_text_fields: imageTextFields,
        product_id: selectedProduct?.id ?? null,
      })
      setGenerating(false)
      if (res.success && res.data) {
        analytics.contentGenerated(contentType, Math.round((Date.now() - genStart) / 1000))
        if (isTemplateMode && selectedTemplate) {
          analytics.templateImageGenerated(
            selectedTemplate.id,
            Math.round((Date.now() - genStart) / 1000)
          )
        }
        setGeneratedPost(res.data)
        setCaption(captionData!.default_caption || res.data.caption || '')
        setHashtags(captionData!.hashtags.length ? captionData!.hashtags : res.data.hashtags ?? [])
        toast.success(isCarousel
          ? `${res.data.slide_count ?? captionData!.image_prompts?.length ?? 0} slide üretimi başlatıldı!`
          : 'İçerik üretimi başlatıldı!'
        )
      } else if (!res.success && res.error === 'rate_limit') {
        setStep(2)
        toast.error(`Saatlik limit aşıldı. ${res.retry_after ?? 60} saniye sonra tekrar deneyin.`)
      } else if (!res.success && res.error === 'plan_limit_reached' && res.plan_limit) {
        setStep(2)
        setUpgradeMessage(res.plan_limit.message)
      } else {
        toast.error('İçerik üretilemedi: ' + (res.error ?? 'Bilinmeyen hata'))
      }
    }
  }

  // Phase 7 — Caption üret (Akış C, hem şablon hem serbest mod)
  async function handleGenerateCaption() {
    if (!currentBrand?.id) return

    // Şablon modunda required field kontrolü
    if (mode === 'template' && selectedTemplate) {
      const missing = selectedTemplate.formFields
        .filter((f) => f.required)
        .filter((f) => {
          const v = templateFields[f.id]
          return v == null || v === '' || (Array.isArray(v) && v.length === 0)
        })
      if (missing.length > 0) {
        toast.error(`Zorunlu alan: ${missing.map((f) => f.label).join(', ')}`)
        return
      }
      analytics.templateFormSubmitted(selectedTemplate.id, Object.keys(templateFields).length)
    }

    // Serbest modda prompt zorunlu
    if (mode === 'free' && !prompt.trim()) {
      toast.error('Lütfen bir içerik açıklaması girin')
      return
    }

    setLoadingCaption(true)
    const genStart = Date.now()
    const res = await api.post<CaptionData & { script?: string; duration_estimate?: number }>('/posts/generate-caption', {
      brand_id: currentBrand.id,
      template_id: selectedTemplate?.id ?? null,
      template_fields: selectedTemplate ? templateFields : null,
      user_prompt: prompt.trim() || null,
      document_ids: selectedDocIds,
      platforms,
      product_id: selectedProduct?.id ?? null,
      content_type: contentType,
      voice: contentType === 'video' ? selectedVoice : undefined,
    })
    setLoadingCaption(false)
    if (res.success && res.data) {
      if (selectedTemplate) {
        analytics.templateCaptionGenerated(
          selectedTemplate.id,
          Math.round((Date.now() - genStart) / 1000)
        )
      }
      setCaptionData({
        default_caption: res.data.default_caption ?? '',
        platform_captions: res.data.platform_captions ?? {},
        image_prompt: res.data.image_prompt ?? '',
        image_prompts: res.data.image_prompts,
        hashtags: res.data.hashtags ?? [],
        ...(res.data.script ? { script: res.data.script } : {}),
      })
      if (res.data.script) setScript(res.data.script)
      if (res.data.duration_estimate) setDurationEstimate(res.data.duration_estimate)
      setPhase('caption')
      toast.success(contentType === 'video'
        ? 'Gönderi metni ve script hazır — düzenleyip videoyu üretin'
        : 'Gönderi metni hazır — düzenleyip görseli üretin'
      )
    } else if (!res.success && res.error === 'rate_limit') {
      toast.error(`Saatlik limit aşıldı. ${res.retry_after ?? 60} saniye sonra tekrar deneyin.`)
    } else if (!res.success && res.error === 'plan_limit_reached' && res.plan_limit) {
      setUpgradeMessage(res.plan_limit.message)
    } else {
      toast.error('Gönderi metni üretilemedi: ' + ((!res.success && res.error) || 'Bilinmeyen hata'))
    }
  }

  async function handleRegenerate() {
    if (!generatedPost?.post_id) return
    setGenerating(true)
    const res = await api.post<GeneratedPost>(`/posts/${generatedPost.post_id}/regenerate`, {})
    setGenerating(false)
    if (res.success) {
      toast.success('Yeniden üretim başlatıldı')
    } else {
      toast.error('Yeniden üretim başlatılamadı')
    }
  }

  async function persistCaption(): Promise<boolean> {
    if (!generatedPost?.post_id) return false
    const res = await api.patch(`/posts/${generatedPost.post_id}`, {
      caption: caption || null,
      hashtags,
    })
    if (!res.success) {
      toast.error('Gönderi metni kaydedilemedi: ' + (res.error ?? 'Bilinmeyen hata'))
      return false
    }
    return true
  }

  async function handlePublish() {
    if (!generatedPost?.post_id) return
    if (publishingRef.current) return
    if (!generatedPost.output_url) {
      toast.error('İçerik henüz hazır değil')
      return
    }
    publishingRef.current = true
    setPublishing(true)
    try {
      const ok = await persistCaption()
      if (!ok) return
      const res = await api.post(`/posts/${generatedPost.post_id}/publish`, {})
      if (res.success) {
        toast.success('İçerik yayınlandı!')
        router.push('/icerik-kutuphanesi')
      } else if (res.error === 'plan_limit_reached' && res.plan_limit) {
        setUpgradeMessage(res.plan_limit.message)
      } else {
        toast.error('Yayınlanamadı: ' + (res.error ?? 'Bilinmeyen hata'))
      }
    } finally {
      setPublishing(false)
      publishingRef.current = false
    }
  }

  function openScheduleDialog() {
    if (!generatedPost?.output_url) {
      toast.error('İçerik henüz hazır değil')
      return
    }
    // Default: 1 saat sonrası, datetime-local formatı (YYYY-MM-DDTHH:mm, lokal saat)
    const d = new Date(Date.now() + 60 * 60 * 1000)
    const pad = (n: number) => String(n).padStart(2, '0')
    const local = `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`
    setScheduleAt(local)
    setShowScheduleDialog(true)
  }

  async function handleSchedule() {
    if (!generatedPost?.post_id || scheduling) return
    if (!scheduleAt) {
      toast.error('Lütfen bir tarih seçin')
      return
    }
    const when = new Date(scheduleAt)
    if (Number.isNaN(when.getTime()) || when.getTime() <= Date.now()) {
      toast.error('Geçmiş bir tarih seçemezsiniz')
      return
    }
    setScheduling(true)
    try {
      const ok = await persistCaption()
      if (!ok) return
      const res = await api.patch(`/calendar/schedule/${generatedPost.post_id}`, {
        scheduled_at: when.toISOString(),
      })
      if (res.success) {
        toast.success('İçerik takvime eklendi')
        setShowScheduleDialog(false)
        router.push('/takvim')
      } else {
        toast.error('Takvime eklenemedi: ' + (res.error ?? 'Bilinmeyen hata'))
      }
    } finally {
      setScheduling(false)
    }
  }

  function addHashtag() {
    const tag = newHashtag.trim()
    if (!tag) return
    const formatted = tag.startsWith('#') ? tag : '#' + tag
    if (!hashtags.includes(formatted)) setHashtags([...hashtags, formatted])
    setNewHashtag('')
  }

  function resetWizard() {
    setStep(1)
    setPrompt('')
    setIdeas([])
    setGeneratedPost(null)
    setCaption('')
    setHashtags([])
    setSelectedDocIds([])
    setScript('')
    setDurationEstimate(null)
    setSelectedHoliday(null)
    setQuoteText('')
    setQuoteAuthor('')
    setMode('template')
    setPhase('pick')
    setSelectedTemplate(null)
    setTemplateFields({})
    setImageTextFields(null)
    setCaptionData(null)
    setImageSubType('general')
    setSelectedProduct(null)
    setAvailableProducts([])
    setIntroPosition('none')
  }

  // Template seçim handler
  function handleSelectTemplate(template: Template) {
    setSelectedTemplate(template)
    setTemplateFields({})
    setImageTextFields(template.imageTextOverlay?.fields ?? null)
    setCaptionData(null)
    setPhase('form')
    // Aspect ratio önerisini uygula
    if (template.output.aspectRatioSuggestion) {
      setAspectRatio(template.output.aspectRatioSuggestion)
    }
    analytics.templateSelected(template.id, currentBrand?.sector_slug, contentType)
  }

  function handleFreeFormMode() {
    setMode('free')
    setSelectedTemplate(null)
    setTemplateFields({})
    setImageTextFields(null)
    setCaptionData(null)
    setPhase('form')
  }

  function handleBackToPick() {
    if (selectedTemplate && phase !== 'pick') {
      analytics.templateAbandoned(selectedTemplate.id, phase)
    }
    setPhase('pick')
    setSelectedTemplate(null)
    setTemplateFields({})
    setImageTextFields(null)
    setCaptionData(null)
    setMode('template')
  }

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <div className="p-8 max-w-3xl mx-auto">
      {upgradeMessage && (
        <UpgradeModal
          message={upgradeMessage}
          onClose={() => setUpgradeMessage(null)}
        />
      )}
      {showScheduleDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm mx-4 p-6 relative">
            <button
              onClick={() => setShowScheduleDialog(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
              aria-label="Kapat"
            >
              <X className="w-5 h-5" />
            </button>
            <div className="flex items-center justify-center w-12 h-12 bg-blue-50 rounded-xl mb-4 mx-auto">
              <Calendar className="w-6 h-6 text-blue-600" />
            </div>
            <h2 className="text-lg font-bold text-gray-900 text-center mb-2">
              Takvime Ekle
            </h2>
            <p className="text-sm text-gray-500 text-center mb-4">
              İçeriğin yayınlanacağı tarih ve saati seçin.
            </p>
            <Label className="text-xs text-gray-600">Yayın Tarihi</Label>
            <input
              type="datetime-local"
              value={scheduleAt}
              onChange={(e) => setScheduleAt(e.target.value)}
              className="w-full mt-1 mb-4 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <div className="flex gap-2">
              <Button
                variant="ghost"
                className="flex-1"
                onClick={() => setShowScheduleDialog(false)}
              >
                İptal
              </Button>
              <Button
                className="flex-1 gap-2"
                onClick={handleSchedule}
                disabled={scheduling}
              >
                {scheduling ? <Loader2 className="w-4 h-4 animate-spin" /> : <Calendar className="w-4 h-4" />}
                Planla
              </Button>
            </div>
          </div>
        </div>
      )}
      <div className="mb-6">
        <h1 className="text-xl font-bold text-gray-900">İçerik Oluştur</h1>
        <p className="text-sm text-gray-500 mt-0.5">AI ile sosyal medya içeriği üretin</p>
      </div>

      <StepIndicator step={step} />

      {/* ── STEP 1: Tip Seçimi ────────────────────────────────────────────── */}
      {step === 1 && (
        <div className="space-y-6">
          {/* Content type cards */}
          <div>
            <p className="text-sm font-medium text-gray-700 mb-3">İçerik Tipi</p>
            <div className="grid grid-cols-5 gap-3">
              {CONTENT_TYPES.map((type) => (
                <button
                  key={type.id}
                  onClick={() => {
                    const newType = type.id as ContentType
                    setContentType(newType)
                    // Tip değişince template state'i sıfırla
                    setSelectedTemplate(null)
                    setTemplateFields({})
                    setImageTextFields(null)
                    setCaptionData(null)
                    setPhase('pick')
                    setMode('template')
                    setImageSubType('general')
                  }}
                  className={cn(
                    'flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all cursor-pointer',
                    contentType === type.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300 hover:bg-blue-50/30'
                  )}
                >
                  <span className="text-2xl">{type.icon}</span>
                  <span className="text-xs font-medium text-gray-700 text-center leading-tight">
                    {type.label}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Alt tip seçici — Görsel/Carousel/Video */}
          {(contentType === 'image' || contentType === 'carousel' || contentType === 'video') && (
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-700">
                {contentType === 'video' ? 'Video İçerik Türü' : 'Görsel İçerik Türü'}
              </p>
              <div className="grid grid-cols-2 gap-3">
                {(contentType === 'video'
                  ? [
                      {
                        id: 'general' as ImageSubType,
                        label: 'Genel Video',
                        desc: 'Soyut/ambient arka plan ile AI sesli video',
                        icon: '🎬',
                      },
                      {
                        id: 'product' as ImageSubType,
                        label: 'Ürün / Hizmet Videosu',
                        desc: 'Ürün görseli üzerinden tanıtım videosu',
                        icon: '📦',
                      },
                    ]
                  : [
                      {
                        id: 'general' as ImageSubType,
                        label: 'Genel Görsel İçerik',
                        desc: 'Herhangi bir konu için AI görsel üret',
                        icon: '🖼️',
                      },
                      {
                        id: 'product' as ImageSubType,
                        label: 'Ürün / Hizmet İçeriği',
                        desc: 'Ürün görseli üzerinden yeni görsel oluştur',
                        icon: '📦',
                      },
                    ]
                ).map((sub) => (
                  <button
                    key={sub.id}
                    onClick={() => setImageSubType(sub.id)}
                    className={cn(
                      'flex flex-col items-start gap-1 p-4 rounded-xl border-2 text-left transition-all',
                      imageSubType === sub.id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-blue-300 hover:bg-blue-50/30'
                    )}
                  >
                    <span className="text-xl">{sub.icon}</span>
                    <span className="text-sm font-medium text-gray-800">{sub.label}</span>
                    <span className="text-xs text-gray-500 leading-snug">{sub.desc}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          <Button
            onClick={async () => {
              if (contentType === 'image' || contentType === 'carousel' || contentType === 'video') {
                const templateId = contentType === 'carousel'
                  ? DEFAULT_CAROUSEL_TEMPLATE_ID
                  : contentType === 'video'
                  ? DEFAULT_VIDEO_TEMPLATE_ID
                  : DEFAULT_IMAGE_TEMPLATE_ID
                setStep(2)
                setMode('template')
                setLoadingDefaultTemplate(true)
                try {
                  const tpl = await fetchTemplateById(templateId)
                  if (tpl) {
                    handleSelectTemplate(tpl)
                  } else {
                    setPhase('pick')
                    toast.error('Varsayılan şablon yüklenemedi, şablon listesi gösteriliyor.')
                  }
                } finally {
                  setLoadingDefaultTemplate(false)
                }
                return
              }
              setStep(2)
            }}
            disabled={loadingDefaultTemplate}
            className="w-full"
          >
            {loadingDefaultTemplate ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Şablon yükleniyor...
              </>
            ) : (
              <>Devam Et →</>
            )}
          </Button>
        </div>
      )}

      {/* ── STEP 2: İçerik Detayları ─────────────────────────────────────── */}
      {step === 2 && (
        <div className="space-y-5">
          {/* Summary badge */}
          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="secondary">
              {CONTENT_TYPES.find((t) => t.id === contentType)?.icon}{' '}
              {CONTENT_TYPES.find((t) => t.id === contentType)?.label}
            </Badge>
            {selectedTemplate && ['image', 'carousel', 'video'].includes(contentType) && selectedTemplate.id !== DEFAULT_IMAGE_TEMPLATE_ID && selectedTemplate.id !== DEFAULT_CAROUSEL_TEMPLATE_ID && selectedTemplate.id !== DEFAULT_VIDEO_TEMPLATE_ID && (
              <Badge variant="secondary">
                {selectedTemplate.icon} {selectedTemplate.name}
              </Badge>
            )}
            {['image', 'carousel'].includes(contentType) && mode === 'free' && (
              <Badge variant="secondary">✏️ Serbest İçerik</Badge>
            )}
            <button onClick={() => setStep(1)} className="text-xs text-blue-500 hover:underline ml-auto">
              ← Geri
            </button>
          </div>

          {/* Varsayılan şablon fetch edilirken loader */}
          {(contentType === 'image' || contentType === 'carousel' || contentType === 'video') && loadingDefaultTemplate && (
            <div className="flex items-center justify-center py-12 text-gray-500 gap-3">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span className="text-sm">
                {contentType === 'carousel' ? 'Carousel şablonu yükleniyor...' : contentType === 'video' ? 'Video şablonu yükleniyor...' : 'Varsayılan görsel şablonu yükleniyor...'}
              </span>
            </div>
          )}

          {/* ── Phase 7: Template phase=pick — carousel için şablon grid, image fallback ── */}
          {['image', 'carousel'].includes(contentType) && mode === 'template' && phase === 'pick' && !loadingDefaultTemplate && (
            <TemplateGrid
              sectorSlug={currentBrand?.sector_slug}
              contentType={contentType}
              selectedId={selectedTemplate?.id}
              onSelect={handleSelectTemplate}
              onFreeForm={handleFreeFormMode}
            />
          )}

          {/* Phase 7: phase=form — dinamik form + aspect/platform/docs + "Caption Üret" */}
          {['image', 'carousel', 'video'].includes(contentType) && mode === 'template' && phase === 'form' && selectedTemplate && (
            <div className="space-y-5">
              {selectedTemplate.id !== DEFAULT_IMAGE_TEMPLATE_ID && selectedTemplate.id !== DEFAULT_CAROUSEL_TEMPLATE_ID && selectedTemplate.id !== DEFAULT_VIDEO_TEMPLATE_ID && (
                <button
                  onClick={handleBackToPick}
                  className="text-xs text-blue-500 hover:underline"
                >
                  ← Başka şablon seç
                </button>
              )}

              {/* Phase 9 Sprint 9B — Ürün/Hizmet seçici (imageSubType=product) */}
              {imageSubType === 'product' && (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-gray-700">
                    Ürün / Hizmet Seç
                    <span className="ml-1 font-normal text-gray-400">(zorunlu)</span>
                  </p>
                  {loadingProducts ? (
                    <div className="flex items-center gap-2 py-4 text-gray-400 text-sm">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Ürünler yükleniyor...
                    </div>
                  ) : availableProducts.length === 0 ? (
                    <div className="rounded-xl border border-dashed border-gray-200 p-4 text-center text-sm text-gray-500">
                      Henüz aktif ürün/hizmet yok.{' '}
                      <a href="/marka-ayarlari?tab=urun-hizmet" className="text-blue-500 hover:underline">
                        Marka Ayarları → Ürün/Hizmet
                      </a>{' '}
                      sayfasından ekleyebilirsiniz.
                    </div>
                  ) : (
                    <div className="flex flex-col gap-2 max-h-64 overflow-y-auto pr-1">
                      {availableProducts.map((p) => (
                        <button
                          key={p.id}
                          type="button"
                          onClick={() => {
                            setSelectedProduct(p)
                            setTemplateFields((prev) => ({
                              ...prev,
                              ana_konu: p.name,
                              one_cikan_ozellik: p.description ?? '',
                            }))
                          }}
                          className={cn(
                            'flex items-center gap-3 rounded-xl border px-3 py-2.5 text-left transition-colors',
                            selectedProduct?.id === p.id
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 hover:border-blue-300 hover:bg-blue-50/30'
                          )}
                        >
                          {p.image_url ? (
                            // eslint-disable-next-line @next/next/no-img-element
                            <img
                              src={p.image_url}
                              alt={p.name}
                              className="w-10 h-10 rounded-lg object-cover flex-shrink-0"
                            />
                          ) : (
                            <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
                              {p.type === 'service'
                                ? <Wrench className="w-4 h-4 text-gray-400" />
                                : <Package className="w-4 h-4 text-gray-400" />}
                            </div>
                          )}
                          <div className="min-w-0 flex-1">
                            <p className="text-sm font-medium text-gray-800 truncate">{p.name}</p>
                            {p.description && (
                              <p className="text-xs text-gray-500 truncate">{p.description}</p>
                            )}
                          </div>
                          {selectedProduct?.id === p.id && (
                            <span className="text-blue-600 text-xs flex-shrink-0">✓</span>
                          )}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}

              <DynamicForm
                template={selectedTemplate}
                values={templateFields}
                onChange={(id, v) =>
                  setTemplateFields((prev) => ({ ...prev, [id]: v }))
                }
                imageTextFields={imageTextFields ?? undefined}
                onImageTextFieldsChange={setImageTextFields}
              />

              {/* Tasarım ve içerik için istekleriniz — CTA'dan (şablon sonu) hemen sonra */}
              <div className="space-y-1.5">
                <Label>
                  Tasarım ve içerik için istekleriniz{' '}
                  <span className="font-normal text-gray-400">(opsiyonel)</span>
                </Label>
                <Textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder={'Örn: "Tenis kıyafetli bir kadın spor ayakkabıyı giyerken göster", "gönderi metninde %20 indirim vurgusu olsun", "stüdyo yerine plaj arka planı"'}
                  rows={3}
                  className="resize-none"
                />
                <p className="text-xs text-gray-500">
                  Yazdıklarınız şablon varsayılanlarını geçersiz kılar — hem görsel
                  hem metin buradaki isteklere göre şekillenir.
                </p>
              </div>

              {/* Aspect ratio */}
              <div className="space-y-2">
                <Label>En-Boy Oranı</Label>
                <div className="grid grid-cols-5 gap-2">
                  {availableAspectRatios.map((ar) => (
                    <button
                      key={ar.id}
                      onClick={() => setAspectRatio(ar.id)}
                      className={cn(
                        'flex flex-col items-center gap-1.5 p-3 rounded-xl border-2 text-center transition-all',
                        aspectRatio === ar.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-blue-300'
                      )}
                    >
                      <span className="text-xl">{ar.icon}</span>
                      <span className="text-xs font-bold text-gray-800">{ar.label}</span>
                      <span className="text-[10px] text-gray-400">{ar.desc}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Logo filigran override — video hariç */}
              {contentType !== 'video' && (currentBrand?.logo_light_url || currentBrand?.logo_dark_url) && (
                <div className="flex items-center justify-between rounded-xl border border-gray-200 bg-gray-50 px-4 py-3">
                  <div className="flex flex-col gap-0.5">
                    <Label className="text-sm font-medium text-gray-800 cursor-pointer">Logo filigranı bas</Label>
                    <span className="text-xs text-gray-500">Bu içerikte marka logosu köşeye yerleştirilsin mi?</span>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className={`text-xs font-medium ${useLogoOverlay ? 'text-purple-700' : 'text-gray-400'}`}>
                      {useLogoOverlay ? 'Açık' : 'Kapalı'}
                    </span>
                    <Switch
                      checked={Boolean(useLogoOverlay)}
                      onCheckedChange={(v) => setUseLogoOverlay(v)}
                    />
                  </div>
                </div>
              )}

              {/* Intro/Outro pozisyon seçici — sadece video */}
              {contentType === 'video' && (
                <div className="space-y-2">
                  <Label>Intro / Outro Video Pozisyonu</Label>
                  {!brandHasIntro ? (
                    <div className="rounded-xl border border-dashed border-gray-200 p-4 text-center text-sm text-gray-500">
                      Intro video yüklenmemiş.{' '}
                      <a href="/marka-ayarlari?tab=gorseller" className="text-blue-500 hover:underline">
                        Marka Ayarları → Görseller
                      </a>{' '}
                      sayfasından yükleyebilirsiniz.
                    </div>
                  ) : (
                    <div className="grid grid-cols-4 gap-2">
                      {([
                        { value: 'none', label: 'Kullanma' },
                        { value: 'start', label: 'Başında' },
                        { value: 'end', label: 'Sonunda' },
                        { value: 'both', label: 'Her İkisi' },
                      ]).map((opt) => (
                        <button
                          key={opt.value}
                          onClick={() => setIntroPosition(opt.value)}
                          className={cn(
                            'px-3 py-2 rounded-xl border-2 text-center text-sm font-medium transition-all',
                            introPosition === opt.value
                              ? 'border-purple-500 bg-purple-50 text-purple-700'
                              : 'border-gray-200 text-gray-600 hover:border-purple-300'
                          )}
                        >
                          {opt.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Platformlar */}
              <div className="space-y-2">
                <Label>Platformlar</Label>
                <div className="flex flex-wrap gap-2">
                  {PLATFORMS.map((p) => (
                    <button
                      key={p.id}
                      onClick={() => togglePlatform(p.id)}
                      className={cn(
                        'px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors',
                        platforms.includes(p.id)
                          ? 'bg-blue-600 text-white border-blue-600'
                          : 'border-gray-200 text-gray-600 hover:border-blue-300'
                      )}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Dokümanlar — sadece Genel Görsel modunda göster */}
              {imageSubType === 'general' && availableDocs.length > 0 && (
                <div className="space-y-2">
                  <Label>Dokümanlardan Bağlam Ekle <span className="font-normal text-gray-400">(opsiyonel)</span></Label>
                  <div className="flex flex-col gap-1.5">
                    {availableDocs.map((doc) => (
                      <button
                        key={doc.id}
                        onClick={() => toggleDoc(doc.id)}
                        className={cn(
                          'flex items-center gap-2.5 px-3 py-2.5 rounded-lg border text-left text-sm transition-colors',
                          selectedDocIds.includes(doc.id)
                            ? 'border-blue-500 bg-blue-50 text-blue-800'
                            : 'border-gray-200 text-gray-600 hover:border-blue-300'
                        )}
                      >
                        <FileText className="w-4 h-4 flex-shrink-0" />
                        <span className="truncate">{doc.name}</span>
                        {selectedDocIds.includes(doc.id) && (
                          <span className="ml-auto text-blue-600 text-xs">✓</span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Video: Ses seçimi */}
              {contentType === 'video' && (
                <div className="space-y-1.5">
                  <Label className="text-sm">Ses Seçimi</Label>
                  <div className="flex flex-wrap gap-2">
                    {(voices.length > 0
                      ? voices
                      : [
                          { id: 'ctoYieZ4J7WwcdhujpMq', name: 'Kaan (Erkek)', gender: 'male' },
                          { id: 'EST9Ui6982FZPSi7gCHi', name: 'Buse (Kadın)', gender: 'female' },
                          { id: 'qSeXEcewz7tA0Q0qk9fH', name: 'Zeynep (Kadın)', gender: 'female' },
                        ]
                    ).map((v) => (
                      <button
                        key={v.id}
                        onClick={() => setSelectedVoice(v.id)}
                        className={cn(
                          'px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors',
                          selectedVoice === v.id
                            ? 'bg-purple-600 text-white border-purple-600'
                            : 'border-purple-200 text-purple-700 hover:border-purple-400'
                        )}
                      >
                        {v.gender === 'female' ? '👩' : '👨'} {v.name}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <Button
                onClick={handleGenerateCaption}
                className="w-full gap-2"
                disabled={loadingCaption}
              >
                {loadingCaption ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
                {contentType === 'video' ? 'Gönderi Metni ve Script Üret' : 'Gönderi Metni Üret'}
              </Button>
            </div>
          )}

          {/* Phase 7: phase=caption — caption düzenle + "Görseli/Videoyu Üret" (template veya free) */}
          {['image', 'carousel', 'video'].includes(contentType) && phase === 'caption' && captionData && (
            <div className="space-y-5">
              <div className="flex items-center justify-between">
                <button
                  onClick={() => setPhase('form')}
                  className="text-xs text-blue-500 hover:underline"
                >
                  ← {mode === 'template' ? 'Formu düzenle' : 'Açıklamayı düzenle'}
                </button>
                <button
                  onClick={handleGenerateCaption}
                  disabled={loadingCaption}
                  className="text-xs text-gray-500 hover:text-gray-700 gap-1 flex items-center"
                >
                  {loadingCaption ? <Loader2 className="w-3 h-3 animate-spin" /> : <RefreshCw className="w-3 h-3" />}
                  Metni yeniden üret
                </button>
              </div>

              <CaptionEditor
                data={captionData}
                platforms={platforms}
                onChange={(d) => {
                  setCaptionData(d)
                  if (selectedTemplate) analytics.templateCaptionEdited(selectedTemplate.id)
                }}
              />

              {/* Video: Script düzenleme */}
              {contentType === 'video' && (
                <div className="space-y-3 p-4 bg-purple-50 border border-purple-200 rounded-xl">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label className="text-purple-800">Video Script</Label>
                      <p className="text-xs text-purple-500 mt-0.5">Voiceover olarak okunacak metin — düzenleyebilirsiniz</p>
                    </div>
                  </div>
                  <Textarea
                    value={script}
                    onChange={(e) => setScript(e.target.value)}
                    rows={5}
                    className="resize-none bg-white text-sm"
                  />
                  {durationEstimate && (
                    <p className="text-xs text-purple-600">
                      Tahmini süre: ~{durationEstimate} saniye
                    </p>
                  )}
                </div>
              )}

              <Button
                onClick={handleGenerate}
                className="w-full gap-2"
                disabled={generating || (
                  contentType === 'video'
                    ? !script.trim()
                    : contentType === 'carousel'
                    ? !(captionData.image_prompts && captionData.image_prompts.length > 0)
                    : !captionData.image_prompt.trim()
                )}
              >
                <Wand2 className="w-4 h-4" />
                {contentType === 'video' ? 'Videoyu Üret' : contentType === 'carousel' ? 'Slide Görsellerini Üret' : 'Görseli Üret'}
              </Button>
            </div>
          )}

          {/* Serbest mod + phase=form: prompt + aspect/platforms/docs + "Caption Üret" */}
          {['image', 'carousel'].includes(contentType) && mode === 'free' && phase === 'form' && (
            <div className="space-y-5">
              <button
                onClick={handleBackToPick}
                className="text-xs text-blue-500 hover:underline"
              >
                ← Şablon seçimine dön
              </button>

              <div className="space-y-1.5">
                <Label>İçerik Açıklaması & Tasarım Tercihleri</Label>
                <Textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="İçerik hakkında iletmek istediğiniz detayları buraya yazabilirsiniz..."
                  rows={4}
                  className="resize-none"
                />
              </div>

              <div className="space-y-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={fetchIdeas}
                  disabled={loadingIdeas}
                  className="gap-2"
                >
                  {loadingIdeas ? <Loader2 className="w-4 h-4 animate-spin" /> : <Lightbulb className="w-4 h-4" />}
                  Bana fikir öner
                </Button>
                {ideas.length > 0 && (
                  <div className="flex flex-col gap-2 mt-2">
                    {ideas.map((idea, i) => (
                      <button
                        key={i}
                        onClick={() => setPrompt(idea)}
                        className="text-left text-sm px-3 py-2 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg text-blue-800 transition-colors"
                      >
                        💡 {idea}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <div className="space-y-2">
                <Label>En-Boy Oranı</Label>
                <div className="grid grid-cols-5 gap-2">
                  {availableAspectRatios.map((ar) => (
                    <button
                      key={ar.id}
                      onClick={() => setAspectRatio(ar.id)}
                      className={cn(
                        'flex flex-col items-center gap-1.5 p-3 rounded-xl border-2 text-center transition-all',
                        aspectRatio === ar.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-blue-300'
                      )}
                    >
                      <span className="text-xl">{ar.icon}</span>
                      <span className="text-xs font-bold text-gray-800">{ar.label}</span>
                      <span className="text-[10px] text-gray-400">{ar.desc}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Logo filigran override — Phase 8 Sprint 1 */}
              {(currentBrand?.logo_light_url || currentBrand?.logo_dark_url) && (
                <div className="flex items-center justify-between rounded-xl border border-gray-200 bg-gray-50 px-4 py-3">
                  <div className="flex flex-col gap-0.5">
                    <Label className="text-sm font-medium text-gray-800 cursor-pointer">Logo filigranı bas</Label>
                    <span className="text-xs text-gray-500">Bu içerikte marka logosu köşeye yerleştirilsin mi?</span>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className={`text-xs font-medium ${useLogoOverlay ? 'text-purple-700' : 'text-gray-400'}`}>
                      {useLogoOverlay ? 'Açık' : 'Kapalı'}
                    </span>
                    <Switch
                      checked={Boolean(useLogoOverlay)}
                      onCheckedChange={(v) => setUseLogoOverlay(v)}
                    />
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <Label>Platformlar</Label>
                <div className="flex flex-wrap gap-2">
                  {PLATFORMS.map((p) => (
                    <button
                      key={p.id}
                      onClick={() => togglePlatform(p.id)}
                      className={cn(
                        'px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors',
                        platforms.includes(p.id)
                          ? 'bg-blue-600 text-white border-blue-600'
                          : 'border-gray-200 text-gray-600 hover:border-blue-300'
                      )}
                    >
                      {p.label}
                    </button>
                  ))}
                </div>
              </div>

              {availableDocs.length > 0 && (
                <div className="space-y-2">
                  <Label>Dokümanlardan Bağlam Ekle <span className="font-normal text-gray-400">(opsiyonel)</span></Label>
                  <div className="flex flex-col gap-1.5">
                    {availableDocs.map((doc) => (
                      <button
                        key={doc.id}
                        onClick={() => toggleDoc(doc.id)}
                        className={cn(
                          'flex items-center gap-2.5 px-3 py-2.5 rounded-lg border text-left text-sm transition-colors',
                          selectedDocIds.includes(doc.id)
                            ? 'border-blue-500 bg-blue-50 text-blue-800'
                            : 'border-gray-200 text-gray-600 hover:border-blue-300'
                        )}
                      >
                        <FileText className="w-4 h-4 flex-shrink-0" />
                        <span className="truncate">{doc.name}</span>
                        {selectedDocIds.includes(doc.id) && (
                          <span className="ml-auto text-blue-600 text-xs">✓</span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <Button
                onClick={handleGenerateCaption}
                className="w-full gap-2"
                disabled={loadingCaption || !prompt.trim()}
              >
                {loadingCaption ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
                Gönderi Metni Üret
              </Button>
            </div>
          )}

          {/* Klasik akış — sadece special_day/quote */}
          {!['image', 'carousel', 'video'].includes(contentType) && (
          <>
          {/* Özel Gün — tatil seçici */}
          {contentType === 'special_day' && (
            <div className="space-y-3 p-4 bg-amber-50 border border-amber-200 rounded-xl">
              <div>
                <Label className="text-amber-800">Özel Gün Seçin</Label>
                <p className="text-xs text-amber-600 mt-0.5">Bu yıla ait milli, dini ve ticari özel günler</p>
              </div>
              <div className="flex flex-col gap-1.5 max-h-52 overflow-y-auto pr-1">
                {holidays.length === 0 && (
                  <p className="text-sm text-amber-600">Tatil listesi yükleniyor...</p>
                )}
                {holidays.map((h) => {
                  const dateStr = new Date(h.date).toLocaleDateString('tr-TR', { day: 'numeric', month: 'long' })
                  const categoryLabel = h.category === 'national' ? '🇹🇷' : h.category === 'religious' ? '🌙' : '🎊'
                  const isPast = new Date(h.date) < new Date()
                  return (
                    <button
                      key={h.date}
                      disabled={isPast}
                      onClick={() => { if (!isPast) setSelectedHoliday(h) }}
                      className={cn(
                        'flex items-center gap-3 px-3 py-2.5 rounded-lg border text-left text-sm transition-colors',
                        selectedHoliday?.date === h.date
                          ? 'border-amber-500 bg-amber-100 text-amber-900'
                          : isPast
                          ? 'border-gray-100 bg-gray-50 text-gray-400 opacity-60 cursor-not-allowed'
                          : 'border-amber-200 text-amber-800 hover:border-amber-400 hover:bg-amber-50'
                      )}
                    >
                      <span className="text-base">{categoryLabel}</span>
                      <span className="flex-1 font-medium">{h.name_tr}</span>
                      <span className="text-xs opacity-70 flex-shrink-0">{dateStr}</span>
                    </button>
                  )
                })}
              </div>
              {selectedHoliday && (
                <div className="flex items-center gap-2 pt-1">
                  <span className="text-xs font-medium text-amber-800">Seçildi:</span>
                  <span className="text-xs bg-amber-200 text-amber-900 px-2 py-0.5 rounded-full">{selectedHoliday.name_tr}</span>
                  <button onClick={() => setSelectedHoliday(null)} className="ml-auto text-xs text-amber-600 hover:underline">Temizle</button>
                </div>
              )}
            </div>
          )}

          {/* Alıntı — quote input */}
          {contentType === 'quote' && (
            <div className="space-y-3 p-4 bg-violet-50 border border-violet-200 rounded-xl">
              <div>
                <Label className="text-violet-800">Alıntı Metni</Label>
                <p className="text-xs text-violet-500 mt-0.5">Görselde yer almasını istediğiniz söz veya cümle</p>
              </div>
              <Textarea
                value={quoteText}
                onChange={(e) => setQuoteText(e.target.value)}
                placeholder="Başarı, hazırlık ile fırsatın buluştuğu andır..."
                rows={3}
                className="resize-none bg-white text-sm"
              />
              <div className="space-y-1.5">
                <Label className="text-sm text-violet-700">Kaynak / Yazar <span className="font-normal text-violet-400">(opsiyonel)</span></Label>
                <input
                  type="text"
                  value={quoteAuthor}
                  onChange={(e) => setQuoteAuthor(e.target.value)}
                  placeholder="Atatürk, Einstein, anonim..."
                  className="w-full text-sm px-3 py-2 border border-violet-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-violet-500/20 focus:border-violet-400 bg-white"
                />
              </div>
            </div>
          )}

          {/* 1. En-Boy Oranı — special_day/quote için gösterilmez */}
          {!['special_day', 'quote'].includes(contentType) && (
          <div className="space-y-2">
            <Label>En-Boy Oranı</Label>
            <div className="grid grid-cols-5 gap-2">
              {availableAspectRatios.map((ar) => (
                <button
                  key={ar.id}
                  onClick={() => setAspectRatio(ar.id)}
                  className={cn(
                    'flex flex-col items-center gap-1.5 p-3 rounded-xl border-2 text-center transition-all',
                    aspectRatio === ar.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-blue-300'
                  )}
                >
                  <span className="text-xl">{ar.icon}</span>
                  <span className="text-xs font-bold text-gray-800">{ar.label}</span>
                  <span className="text-[10px] text-gray-400">{ar.desc}</span>
                </button>
              ))}
            </div>
          </div>
          )}

          {/* 2. Platformlar */}
          <div className="space-y-2">
            <Label>Platformlar</Label>
            <div className="flex flex-wrap gap-2">
              {PLATFORMS.map((p) => (
                <button
                  key={p.id}
                  onClick={() => togglePlatform(p.id)}
                  className={cn(
                    'px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors',
                    platforms.includes(p.id)
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'border-gray-200 text-gray-600 hover:border-blue-300'
                  )}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          {/* 3. Dokümanlar — special_day ve quote için gereksiz */}
          {!['special_day', 'quote'].includes(contentType) && (
            <div className="space-y-2">
              <Label>Dokümanlardan Bağlam Ekle <span className="font-normal text-gray-400">(opsiyonel)</span></Label>
              <p className="text-xs text-gray-400">Ürün kataloğu, hizmet listesi veya referans belgesi yükleyin — AI içerik üretirken bu belgeleri baz alır.</p>
              {availableDocs.length === 0 ? (
                <p className="text-xs text-gray-400 px-1">
                  Henüz yüklü doküman yok.{' '}
                  <a href="/marka-ayarlari?tab=belgeler" className="text-blue-500 hover:underline">
                    Marka Ayarları → Dokümanlar
                  </a>
                  {' '}bölümünden ürün kataloğu, fiyat listesi vb. yükleyebilirsiniz.
                </p>
              ) : (
                <div className="flex flex-col gap-1.5">
                  {availableDocs.map((doc) => (
                    <button
                      key={doc.id}
                      onClick={() => toggleDoc(doc.id)}
                      className={cn(
                        'flex items-center gap-2.5 px-3 py-2.5 rounded-lg border text-left text-sm transition-colors',
                        selectedDocIds.includes(doc.id)
                          ? 'border-blue-500 bg-blue-50 text-blue-800'
                          : 'border-gray-200 text-gray-600 hover:border-blue-300'
                      )}
                    >
                      <FileText className="w-4 h-4 flex-shrink-0" />
                      <span className="truncate">{doc.name}</span>
                      {doc.file_size_kb && (
                        <span className="ml-auto text-xs text-gray-400 flex-shrink-0">{doc.file_size_kb} KB</span>
                      )}
                      {selectedDocIds.includes(doc.id) && (
                        <span className="text-blue-600 text-xs flex-shrink-0">✓</span>
                      )}
                    </button>
                  ))}
                  {selectedDocIds.length > 0 && (
                    <p className="text-xs text-blue-600">
                      {selectedDocIds.length} doküman seçildi — AI içerik üretirken bu belgeleri referans alacak
                    </p>
                  )}
                </div>
              )}
            </div>
          )}

          {/* 4. Bana fikir öner — special_day/quote hariç tüm tipler */}
          {!['special_day', 'quote'].includes(contentType) && (
          <div className="space-y-2">
            <Button
              variant="outline"
              size="sm"
              onClick={fetchIdeas}
              disabled={loadingIdeas}
              className="gap-2"
            >
              {loadingIdeas ? <Loader2 className="w-4 h-4 animate-spin" /> : <Lightbulb className="w-4 h-4" />}
              Bana fikir öner
            </Button>
            {ideas.length > 0 && (
              <div className="flex flex-col gap-2 mt-2">
                {ideas.map((idea, i) => (
                  <button
                    key={i}
                    onClick={() => setPrompt(idea)}
                    className="text-left text-sm px-3 py-2 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg text-blue-800 transition-colors"
                  >
                    💡 {idea}
                  </button>
                ))}
              </div>
            )}
          </div>
          )}

          {/* 5 & 6. İçerik Açıklaması & Tasarım Tercihleri — görsel/carousel/special_day/video için */}
          {contentType !== 'quote' && (
          <div className="space-y-1.5">
            <Label>
              {contentType === 'special_day' ? 'Ek Not (opsiyonel)' : 'İçerik Açıklaması & Tasarım Tercihleri'}
            </Label>
            <Textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder={
                contentType === 'special_day'
                  ? 'Özel günle ilgili eklemek istediğiniz bir mesaj veya not...'
                  : 'İçerik hakkında iletmek istediğiniz detayları buraya yazabilirsiniz...'
              }
              rows={contentType === 'special_day' ? 2 : 4}
              className="resize-none"
            />
          </div>
          )}


          {/* 6. İçerik Üret butonu */}
          <Button
            onClick={handleGenerate}
            className="w-full gap-2"
            disabled={
              (contentType === 'special_day' && !selectedHoliday) ||
              (contentType === 'quote' && !quoteText.trim()) ||
              (!['special_day', 'quote'].includes(contentType) && !prompt.trim())
            }
          >
            <Wand2 className="w-4 h-4" />
            İçerik Üret
          </Button>
          </>
          )}
        </div>
      )}

      {/* ── STEP 3: Üretim & Önizleme ────────────────────────────────────── */}
      {step === 3 && (
        <div className="space-y-5">
          <div className="flex items-center justify-between">
            <button onClick={() => { setStep(2); setGeneratedPost(null); setCaption(''); setHashtags([]) }} className="text-xs text-blue-500 hover:underline">
              ← Geri
            </button>
            <button onClick={resetWizard} className="text-xs text-gray-400 hover:text-gray-600">
              Yeni İçerik Oluştur
            </button>
          </div>

          {/* Generation state */}
          {generating && (
            <div className="flex flex-col items-center justify-center py-16 gap-4">
              <div className="relative">
                <div className={cn(
                  'w-16 h-16 rounded-2xl flex items-center justify-center',
                  contentType === 'video' ? 'bg-purple-100' : 'bg-blue-100'
                )}>
                  <Loader2 className={cn(
                    'w-8 h-8 animate-spin',
                    contentType === 'video' ? 'text-purple-600' : 'text-blue-600'
                  )} />
                </div>
              </div>
              <p className="text-gray-700 font-medium">
                {contentType === 'video' ? 'Video üretiliyor...' :
                 contentType === 'special_day' ? `${selectedHoliday?.name_tr} içeriği üretiliyor...` :
                 contentType === 'quote' ? 'Alıntı kartı üretiliyor...' :
                 contentType === 'carousel' ? 'Carousel slide görselleri üretiliyor...' :
                 'İçeriğiniz üretiliyor...'}
              </p>
              <p className="text-sm text-gray-400">
                {contentType === 'video'
                  ? 'Script ve ses oluşturuluyor, arka plan videosu hazırlanıyor...'
                  : contentType === 'carousel'
                  ? `${captionData?.image_prompts?.length ?? 0} slide paralel üretiliyor, bu biraz sürebilir`
                  : 'Bu birkaç saniye sürebilir'
                }
              </p>
            </div>
          )}

          {/* Result */}
          {!generating && generatedPost && (
            <div className="space-y-5">
              {/* Video önizleme */}
              {contentType === 'video' ? (
                <div className="rounded-2xl overflow-hidden bg-gradient-to-br from-purple-50 to-violet-100 border border-purple-200">
                  {generatedPost.output_url ? (
                    <video
                      src={generatedPost.output_url}
                      controls
                      className="w-full max-h-80 object-contain"
                    />
                  ) : generatedPost.status === 'failed' ? (
                    <div className="flex flex-col items-center justify-center py-12 gap-3">
                      <div className="w-14 h-14 rounded-xl bg-red-100 flex items-center justify-center">
                        <X className="w-7 h-7 text-red-600" />
                      </div>
                      <p className="text-sm text-red-700 font-medium">Video üretilemedi</p>
                      <p className="text-xs text-red-500 text-center px-4">Farklı bir açıklama veya ayarla tekrar deneyin</p>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center py-12 gap-3">
                      <div className="w-14 h-14 rounded-xl bg-purple-200 flex items-center justify-center">
                        <Loader2 className="w-7 h-7 text-purple-600 animate-spin" />
                      </div>
                      <p className="text-sm text-purple-700 font-medium">Video render ediliyor...</p>
                      <p className="text-xs text-purple-500">Bu 1-3 dakika sürebilir</p>
                      <p className="text-xs text-purple-400">Post ID: {generatedPost.post_id.slice(0, 8)}...</p>
                    </div>
                  )}
                  {/* Script gösterimi */}
                  {script && (
                    <div className="p-4 border-t border-purple-200 bg-white/60">
                      <p className="text-xs font-medium text-purple-700 mb-1">Script</p>
                      <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{script}</p>
                      {durationEstimate && (
                        <p className="text-xs text-purple-500 mt-2">Tahmini süre: ~{durationEstimate} saniye</p>
                      )}
                    </div>
                  )}
                  {/* Ses dosyası */}
                  {generatedPost.audio_url && (
                    <div className="p-4 border-t border-purple-200 bg-white/60">
                      <p className="text-xs font-medium text-purple-700 mb-2">Ses Dosyası</p>
                      <audio src={generatedPost.audio_url} controls className="w-full h-10" />
                    </div>
                  )}
                </div>
              ) : contentType === 'carousel' && generatedPost.slides && generatedPost.slides.length > 0 ? (
                /* Carousel slide grid önizleme */
                <div className="space-y-3">
                  {(() => {
                    const slides = generatedPost.slides!
                    const completedCount = slides.filter(s => s.image_url).length
                    const totalCount = slides.length
                    return (
                      <>
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-gray-700">
                            Slide Görselleri
                          </p>
                          <span className={cn(
                            'text-xs font-medium px-2 py-0.5 rounded-full',
                            completedCount === totalCount
                              ? 'bg-green-100 text-green-700'
                              : 'bg-blue-100 text-blue-700'
                          )}>
                            {completedCount}/{totalCount} hazır
                          </span>
                        </div>
                        {completedCount < totalCount && (
                          <div className="w-full bg-gray-200 rounded-full h-1.5">
                            <div
                              className="bg-blue-500 h-1.5 rounded-full transition-all duration-500"
                              style={{ width: `${(completedCount / totalCount) * 100}%` }}
                            />
                          </div>
                        )}
                        <div className="grid grid-cols-3 gap-2">
                          {slides
                            .sort((a, b) => a.order - b.order)
                            .map((slide) => (
                            <div
                              key={slide.order}
                              className="relative rounded-xl overflow-hidden border border-gray-200 bg-gradient-to-br from-blue-50 to-indigo-50 aspect-square"
                            >
                              {slide.image_url ? (
                                <Image
                                  src={slide.image_url}
                                  alt={`Slide ${slide.order}`}
                                  width={400}
                                  height={400}
                                  className="w-full h-full object-cover"
                                />
                              ) : (
                                <div className="w-full h-full flex items-center justify-center">
                                  <Loader2 className="w-6 h-6 text-blue-400 animate-spin" />
                                </div>
                              )}
                              <div className="absolute top-1.5 left-1.5 bg-black/60 text-white text-[10px] font-bold w-5 h-5 rounded-full flex items-center justify-center">
                                {slide.order}
                              </div>
                            </div>
                          ))}
                        </div>
                      </>
                    )
                  })()}
                </div>
              ) : (
                /* Tekli görsel önizleme */
                <div className="rounded-2xl overflow-hidden bg-gradient-to-br from-blue-50 to-indigo-100 border border-blue-200">
                  {generatedPost.output_url ? (
                    <Image
                      src={generatedPost.output_url}
                      alt="Üretilen içerik"
                      width={800}
                      height={800}
                      className="w-full object-contain max-h-80"
                    />
                  ) : generatedPost.status === 'failed' ? (
                    <div className="flex flex-col items-center justify-center py-16 gap-3">
                      <div className="w-14 h-14 rounded-xl bg-red-100 flex items-center justify-center">
                        <X className="w-7 h-7 text-red-600" />
                      </div>
                      <p className="text-sm text-red-700 font-medium">Görsel üretilemedi</p>
                      <p className="text-xs text-red-500 text-center px-4">Farklı bir en-boy oranı veya açıklama ile tekrar deneyin</p>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center justify-center py-16 gap-3">
                      <div className="w-14 h-14 rounded-xl bg-blue-200 flex items-center justify-center">
                        <Loader2 className="w-7 h-7 text-blue-600 animate-spin" />
                      </div>
                      <p className="text-sm text-blue-700 font-medium">Görsel hazırlanıyor...</p>
                      <p className="text-xs text-blue-500">
                        Post ID: {generatedPost.post_id.slice(0, 8)}...
                      </p>
                    </div>
                  )}
                </div>
              )}

              {/* Gönderi metni + hashtag — captionData varsa platform sekmeli preview, yoksa editör */}
              {captionData ? (
                <CaptionPreview
                  data={captionData}
                  platforms={platforms}
                  onEdit={() => { setStep(2); setPhase('caption') }}
                />
              ) : (
                <>
                  <div className="space-y-1.5">
                    <Label>Gönderi Metni</Label>
                    <Textarea
                      value={caption}
                      onChange={(e) => setCaption(e.target.value)}
                      placeholder="Gönderi metnini buraya yazın veya AI tarafından üretilmiş metni düzenleyin..."
                      rows={4}
                      className="resize-none"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label>Hashtagler</Label>
                    <div className="flex flex-wrap gap-1.5 min-h-[36px] p-2 border border-gray-200 rounded-md bg-gray-50">
                      {hashtags.map((tag) => (
                        <Badge key={tag} variant="secondary" className="gap-1 text-xs">
                          {tag}
                          <button onClick={() => setHashtags(hashtags.filter((h) => h !== tag))}>
                            <X className="w-3 h-3" />
                          </button>
                        </Badge>
                      ))}
                      {hashtags.length === 0 && (
                        <span className="text-xs text-gray-400 px-1">Henüz hashtag yok</span>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        value={newHashtag}
                        onChange={(e) => setNewHashtag(e.target.value)}
                        onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addHashtag() } }}
                        placeholder="#hashtag ekle"
                        className="flex-1 text-sm px-3 py-1.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400"
                      />
                      <Button variant="outline" size="sm" onClick={addHashtag}>Ekle</Button>
                    </div>
                  </div>
                </>
              )}

              {/* Action buttons */}
              <div className="flex gap-3 pt-2">
                <Button
                  variant="outline"
                  className="flex-1 gap-2"
                  onClick={handleRegenerate}
                  disabled={generating || publishing || scheduling || !generatedPost?.output_url}
                >
                  <RefreshCw className="w-4 h-4" />
                  Yeniden Üret
                </Button>
                <Button
                  variant="outline"
                  className="flex-1 gap-2"
                  onClick={openScheduleDialog}
                  disabled={generating || publishing || scheduling || !generatedPost.output_url}
                >
                  <Calendar className="w-4 h-4" />
                  Takvime Ekle
                </Button>
                <Button
                  className="flex-1 gap-2"
                  onClick={handlePublish}
                  disabled={generating || publishing || scheduling || !generatedPost.output_url}
                >
                  {publishing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                  Şimdi Yayınla
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
