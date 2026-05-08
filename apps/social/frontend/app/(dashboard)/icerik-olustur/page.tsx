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
import { Loader2, Wand2, RefreshCw, Calendar, Send, X, Lightbulb, FileText, Package, Wrench, Star, ChevronDown } from 'lucide-react'
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
import { SceneReferencePicker, type SelectedSceneReference } from '@/components/SceneReferencePicker'
import { getPref, setPref } from '@/lib/preferences'

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
type Step = 1 | 2 | 3 | 4
type TemplateMode = 'template' | 'free'
type TemplatePhase = 'pick' | 'form' | 'caption'

// Phase 8 Sprint 2 — Görsel tipi için varsayılan şablon.
// `contentType='image'` + "Devam Et" tıklanınca otomatik seçilir; şablon grid'i gösterilmez.
const DEFAULT_IMAGE_TEMPLATE_ID = 'genel-gorsel-sablon'
const DEFAULT_CAROUSEL_TEMPLATE_ID = 'carousel-genel-sablon'
const DEFAULT_VIDEO_TEMPLATE_ID = 'shortvideo-genel-sablon'

// Özel Gün format → şablon ID mapping (Sprint 2). Format seçildiğinde otomatik fetch + select edilir.
type SpecialDayFormat = 'image' | 'carousel' | 'video'
const SPECIAL_DAY_TEMPLATE_IDS: Record<SpecialDayFormat, string> = {
  image: 'ozelgun-gorsel-sablon',
  carousel: 'ozelgun-carousel-sablon',
  video: 'ozelgun-shortvideo-sablon',
}
const SPECIAL_DAY_TEMPLATE_ID_SET = new Set(Object.values(SPECIAL_DAY_TEMPLATE_IDS))

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
  // Kısa video
  script?: string
  audio_url?: string
  still_image_url?: string
  duration_estimate?: number
  template_fields?: Record<string, unknown>
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
  { id: 'video' as ContentType, label: 'Kısa Video', icon: '🎬' },
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

function StepIndicator({ step, contentType }: { step: Step; contentType: ContentType }) {
  const steps = contentType === 'video'
    ? [
        { n: 1, label: 'Tip Seçimi' },
        { n: 2, label: 'İçerik Detayları' },
        { n: 3, label: 'Önizleme & Onay' },
        { n: 4, label: 'Sonuç' },
      ]
    : [
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

// ─── Accordion block (Step 2 — genel-gorsel-sablon) ─────────────────────────

interface AccordionBlockProps {
  icon: string
  title: string
  summary?: string | null
  isOpen: boolean
  onToggle: () => void
  children: React.ReactNode
}

function AccordionBlock({ icon, title, summary, isOpen, onToggle, children }: AccordionBlockProps) {
  return (
    <div className="rounded-xl border border-gray-200 overflow-hidden bg-white">
      <button
        type="button"
        onClick={onToggle}
        className="w-full flex items-center justify-between gap-3 px-4 py-3 hover:bg-gray-50 transition-colors text-left"
      >
        <div className="flex items-center gap-2 min-w-0 flex-1">
          <span className="text-base flex-shrink-0">{icon}</span>
          <span className="text-sm font-medium text-gray-800 flex-shrink-0">{title}</span>
          {summary && !isOpen && (
            <span className="text-xs text-gray-400 truncate">· {summary}</span>
          )}
        </div>
        <ChevronDown
          className={cn(
            'w-4 h-4 text-gray-400 flex-shrink-0 transition-transform',
            isOpen && 'rotate-180'
          )}
        />
      </button>
      {isOpen && (
        <div className="px-4 py-4 border-t border-gray-100 space-y-4">
          {children}
        </div>
      )}
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
  // Çoklu görsel Sprint 3 — kullanıcının seçtiği ürün görselleri ve carousel
  // dağıtım modu. selectedProductImageIds default = ürünün tüm görsel ID'leri
  // (selectedProduct değişince reset edilir, aşağıdaki useEffect).
  const [selectedProductImageIds, setSelectedProductImageIds] = useState<string[]>([])
  const [carouselImageMode, setCarouselImageMode] = useState<'auto' | 'primary_only'>('auto')
  // Sprint 3 (Özel Gün) — Marka referans görseli (Nano Banana 2 edit ref'i, genel mod)
  const [selectedSceneReference, setSelectedSceneReference] = useState<SelectedSceneReference | null>(null)

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

  // Genel-gorsel-sablon akordeon (Step 2) — sadece bu şablonda kullanılır.
  // Default: Konu (group2) açık. Mount sonrası persist'ten override edilir.
  const [accordion, setAccordion] = useState({
    group1: false,
    group2: true,
    group3: false,
    group4: false,
  })
  const toggleAccordion = useCallback((g: 'group1' | 'group2' | 'group3' | 'group4') => {
    setAccordion((s) => ({ ...s, [g]: !s[g] }))
  }, [])

  // Kısa video — Step 2
  const [script, setScript] = useState('')
  const [voices, setVoices] = useState<TurkishVoice[]>([])
  const [selectedVoice, setSelectedVoice] = useState('qSeXEcewz7tA0Q0qk9fH')
  const [durationEstimate, setDurationEstimate] = useState<number | null>(null)
  // Intro/outro pozisyonu (video için) — none/start/end/both
  const [introPosition, setIntroPosition] = useState<string>('none')
  const [subtitleEnabled, setSubtitleEnabled] = useState(true)
  const [brandHasIntro, setBrandHasIntro] = useState(false)

  // Özel Gün — Step 2
  const [holidays, setHolidays] = useState<Holiday[]>([])
  const [selectedHoliday, setSelectedHoliday] = useState<Holiday | null>(null)
  // Sprint 2 — özel gün için format seçici (görsel/carousel/video). null = henüz seçilmedi.
  const [specialDayFormat, setSpecialDayFormat] = useState<SpecialDayFormat | null>(null)

  // Backend'e gönderilen / branching için kullanılan etkin içerik tipi.
  // Özel gün modunda specialDayFormat (henüz seçilmemişse 'image' fallback olarak — UI'da format zorunlu).
  const effectiveContentType: ContentType = contentType === 'special_day'
    ? (specialDayFormat ?? 'image')
    : contentType

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

  // Kısa video Stage 1/2 — onay sayfasında düzenleme yapıldı mı (banner için)
  const [stage1Edited, setStage1Edited] = useState(false)
  const [approving, setApproving] = useState(false)
  const [rejecting, setRejecting] = useState(false)

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
    // Stage 1 sonrası onay bekliyor — Stage 2 tetiklenene kadar polling yapma
    if (generatedPost.status === 'awaiting_approval') return
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
          template_fields: res.data!.template_fields ?? prev.template_fields,
        } : prev)
      } else if (res.success && res.data?.status === 'failed') {
        toast.error('Görsel üretilemedi — farklı bir en-boy oranı veya açıklama ile tekrar dene')
        setGeneratedPost(prev => prev ? { ...prev, status: 'failed' } : prev)
      } else if (!cancelled) {
        if (res.success && res.data) {
          setGeneratedPost(prev => prev ? {
            ...prev,
            slides: res.data!.slides ?? prev.slides,
            template_fields: res.data!.template_fields ?? prev.template_fields,
          } : prev)
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
    setSelectedSceneReference(null)
    setSelectedDocIds([])
    setCaptionData(null)
  }, [imageSubType])

  // Ürün değişince ürünün ilk 3 görselini default seçili yap (Sprint 3.5).
  // Nano Banana 2 sweet spot 3 görsel; daha fazlası kompozisyon riski.
  // Backend images dizisini is_primary + position sırasına göre döner, yani
  // slice(0,3) ana görsel + sıradaki 2 pozisyonu seçer. Tek görselli ürünlerde
  // yine de tek elemanlı liste; UI bölümü bu durumda gizli.
  useEffect(() => {
    if (selectedProduct) {
      setSelectedProductImageIds(selectedProduct.images.slice(0, 3).map((img) => img.id))
    } else {
      setSelectedProductImageIds([])
    }
    setCarouselImageMode('auto')
    // selectedProduct.id ile yetiniyoruz; full object referansındaki değişimleri (images
    // re-fetch vb.) dahil etmek selection'ı durup durup resetler.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedProduct?.id])

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

  // Platform seçimi: marka değişince persist'ten yükle (yoksa default ['instagram'])
  useEffect(() => {
    if (!currentBrand?.id) return
    const stored = getPref<string[] | null>(`platforms_${currentBrand.id}`, null)
    if (stored && Array.isArray(stored) && stored.length > 0) {
      setPlatforms(stored)
    } else {
      setPlatforms(['instagram'])
    }
  }, [currentBrand?.id])

  // Platform seçimi: değişince persist et (per marka).
  // Önemli: dep'te currentBrand?.id YOK — marka geçişini read effect ele alır;
  // eklersek henüz read tetiklenmeden ESKİ marka'nın platforms'u YENİ marka'nın anahtarına yazılıyor.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (!currentBrand?.id) return
    setPref(`platforms_${currentBrand.id}`, platforms)
  }, [platforms])

  useEffect(() => {
    async function fetchVoices() {
      const res = await api.get<TurkishVoice[]>('/posts/voices/turkish')
      if (res.success && res.data) setVoices(res.data)
    }
    fetchVoices()
  }, [])

  // TTS sesi: voices yüklendikten sonra persist'ten oku (listede varsa kullan)
  useEffect(() => {
    if (voices.length === 0) return
    const stored = getPref<string | null>('tts_voice', null)
    if (stored && voices.some((v) => v.id === stored)) {
      setSelectedVoice(stored)
    }
  }, [voices])

  // TTS sesi: değişince persist (global, brand'den bağımsız)
  useEffect(() => {
    if (selectedVoice) setPref('tts_voice', selectedVoice)
  }, [selectedVoice])

  // Akordeon: mount'ta persist'ten yükle (genel-gorsel-sablon)
  useEffect(() => {
    const stored = getPref<{ group1?: boolean; group2?: boolean; group3?: boolean; group4?: boolean } | null>(
      'accordion_genel_gorsel',
      null,
    )
    if (stored && typeof stored === 'object') {
      setAccordion({
        group1: Boolean(stored.group1),
        group2: stored.group2 == null ? true : Boolean(stored.group2),
        group3: Boolean(stored.group3),
        group4: Boolean(stored.group4),
      })
    }
  }, [])

  // Akordeon: değişince persist. İlk mount'ta default değerin persist'i ezmesini
  // önlemek için ilk write skip edilir (read effect'in stored'u yüklemesi için zaman tanır).
  const accordionWriteSkip = useRef(true)
  useEffect(() => {
    if (accordionWriteSkip.current) {
      accordionWriteSkip.current = false
      return
    }
    setPref('accordion_genel_gorsel', accordion)
  }, [accordion])

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
    const supported = effectiveContentType === 'video'
      ? mediaModels?.short_video_background.supported_ratios
      : mediaModels?.image.supported_ratios
    if (!supported) return ASPECT_RATIOS
    const supportedSet = new Set(supported)
    return ASPECT_RATIOS.filter((ar) => supportedSet.has(ar.id))
  }, [effectiveContentType, mediaModels])

  // Aspect ratio: persist'ten oku (per içerik tipi). Kullanıcının son tercihi
  // şablon önerisinden ve fallback'ten önceliklidir; desteklenmiyorsa fallback.
  // Önemli: dependency'de aspectRatio YOK — write effect ile oscillation olmaması için
  // sadece contentType / availableAspectRatios değişince çalışır. Mevcut aspectRatio
  // değerini setter functional form ile okuyoruz.
  useEffect(() => {
    if (availableAspectRatios.length === 0) return
    const stored = getPref<string | null>(`aspect_${contentType}`, null)
    if (stored && availableAspectRatios.some((ar) => ar.id === stored)) {
      setAspectRatio(stored)
      return
    }
    setAspectRatio((curr) => {
      if (availableAspectRatios.some((ar) => ar.id === curr)) return curr
      return availableAspectRatios[0].id
    })
  }, [availableAspectRatios, contentType])

  // Aspect ratio: kullanıcı seçimini persist et (per içerik tipi).
  // Önemli: dep'te contentType YOK — contentType geçişini read effect ele alır;
  // eklersek henüz read tetiklenmeden ESKİ aspectRatio yeni contentType'ın anahtarına yazılıyor.
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    if (aspectRatio) setPref(`aspect_${contentType}`, aspectRatio)
  }, [aspectRatio])

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

    if (contentType === 'special_day') {
      if (!specialDayFormat) {
        toast.error('Lütfen önce format seçin (Görsel / Carousel / Kısa Video)')
        return
      }
      if (!selectedHoliday) {
        toast.error('Lütfen bir özel gün seçin')
        return
      }
    }
    if (contentType === 'quote' && !quoteText.trim()) {
      toast.error('Lütfen alıntı metnini girin')
      return
    }
    // Image/carousel/video (özel gün + bu format'lar dahil): caption üretilmiş olmalı (Akış C unified)
    if (['image', 'carousel', 'video'].includes(effectiveContentType)) {
      if (!captionData) {
        toast.error('Önce gönderi metnini üretin')
        return
      }
    }
    if (effectiveContentType === 'video' && !script.trim()) {
      toast.error('Lütfen bir script girin veya üretin')
      return
    }

    analytics.contentCreationStarted(contentType)
    if (selectedDocIds.length > 0) analytics.documentReferenceUsed(selectedDocIds.length)
    const genStart = Date.now()
    setGenerating(true)
    setStep(3)

    if (effectiveContentType === 'video') {
      // Kısa video Stage 1 — TTS + Nano Banana 2 still (kota burada düşer)
      // Stage 2 (Wan I2V) kullanıcı önizlemeyi onayladıktan sonra ayrı endpoint ile tetiklenir.
      const isTemplateMode = mode === 'template' && selectedTemplate
      const videoTemplateFields = {
        ...(isTemplateMode ? templateFields : {}),
        subtitle_enabled: subtitleEnabled,
      }
      // Stage 1 tatil bağlamından bağımsız: caption_generator (Akış C) image_prompt'u tatil tonunda
      // üretir; Stage 1 still bu image_prompt'la çalışır. Ekstra special_day alanları yollamaya gerek yok.
      const res = await api.post<GeneratedPost>('/posts/generate-short-video-stage1', {
        brand_id: currentBrand.id,
        prompt: prompt.trim() || captionData!.image_prompt || '',
        script: script.trim(),
        voice: selectedVoice,
        document_ids: selectedDocIds,
        aspect_ratio: aspectRatio,
        platforms,
        template_id: isTemplateMode ? selectedTemplate.id : null,
        template_fields: videoTemplateFields,
        platform_captions: captionData!.platform_captions,
        intro_position: introPosition,
        product_id: selectedProduct?.id ?? null,
        product_image_ids: selectedProductImageIds.length > 0 ? selectedProductImageIds : null,
        visual_brief: prompt.trim(),
        scene_reference_image_url: imageSubType === 'general' ? selectedSceneReference?.image_url ?? null : null,
      })
      setGenerating(false)
      if (res.success && res.data) {
        analytics.contentGenerated(contentType, Math.round((Date.now() - genStart) / 1000))
        setGeneratedPost({ ...res.data, status: 'awaiting_approval' })
        setCaption(captionData!.default_caption || '')
        setHashtags(captionData!.hashtags.length ? captionData!.hashtags : [])
        setStage1Edited(false)
        // Step 3 = Önizleme & Onay (video için yeni adım)
        setStep(3)
        toast.success('Ses ve sahne hazır — önizleyip onaylayın')
      } else if (!res.success && res.error === 'rate_limit') {
        setStep(2)
        toast.error(`Saatlik limit aşıldı. ${res.retry_after ?? 60} saniye sonra tekrar deneyin.`)
      } else if (!res.success && res.error === 'plan_limit_reached' && res.plan_limit) {
        setStep(2)
        setUpgradeMessage(res.plan_limit.message)
      } else {
        setStep(2)
        toast.error('Önizleme üretilemedi: ' + (res.error ?? 'Bilinmeyen hata'))
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
      // Özel gün + image/carousel da bu yola düşer (effectiveContentType='image'|'carousel').
      const isTemplateMode = mode === 'template' && selectedTemplate
      const isCarousel = effectiveContentType === 'carousel' && captionData!.image_prompts && captionData!.image_prompts.length > 0
      const res = await api.post<GeneratedPost>('/posts/generate', {
        brand_id: currentBrand.id,
        content_type: effectiveContentType,
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
        product_image_ids: selectedProductImageIds.length > 0 ? selectedProductImageIds : null,
        ...(effectiveContentType === 'carousel' ? { carousel_image_mode: carouselImageMode } : {}),
        special_day_name: contentType === 'special_day' ? selectedHoliday?.name_tr ?? null : null,
        special_day_category: contentType === 'special_day' ? selectedHoliday?.category ?? null : null,
        scene_reference_image_url: imageSubType === 'general' ? selectedSceneReference?.image_url ?? null : null,
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

    // Video + Genel akış: "Bu video ne anlatsın?" zorunlu (ürün modunda opsiyonel — backend ürün adını kullanır)
    if (effectiveContentType === 'video' && imageSubType === 'general' && !prompt.trim()) {
      toast.error('Lütfen "Bu video ne anlatsın?" alanını doldurun')
      return
    }

    // Özel gün modunda tatil seçilmiş olmalı (caption tatil tonunda yazılacak)
    if (contentType === 'special_day' && !selectedHoliday) {
      toast.error('Lütfen önce bir özel gün seçin')
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
      product_image_ids: selectedProductImageIds.length > 0 ? selectedProductImageIds : null,
      content_type: effectiveContentType,
      voice: effectiveContentType === 'video' ? selectedVoice : undefined,
      special_day_name: contentType === 'special_day' ? selectedHoliday?.name_tr ?? null : null,
      special_day_category: contentType === 'special_day' ? selectedHoliday?.category ?? null : null,
      scene_reference_image_url: imageSubType === 'general' ? selectedSceneReference?.image_url ?? null : null,
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
      toast.success(effectiveContentType === 'video'
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

  // Kısa video Stage 2: kullanıcı Stage 1 önizlemesini onayladı → Wan I2V tetikle
  async function handleApproveShortVideo() {
    if (!generatedPost?.post_id || approving) return
    setApproving(true)
    const res = await api.post<{ post_id: string; fal_job_id: string; status: string }>(
      `/posts/${generatedPost.post_id}/approve-short-video`,
      {}
    )
    setApproving(false)
    if (res.success && res.data) {
      // Status='generating' → mevcut polling useEffect Wan I2V çıktısını çekecek
      setGeneratedPost((prev) => prev ? { ...prev, status: 'generating' } : prev)
      setStep(4)
      toast.success('Video üretiliyor — bu 1-3 dakika sürebilir')
    } else if (!res.success && res.error === 'rate_limit') {
      toast.error(`Saatlik limit aşıldı. ${res.retry_after ?? 60} saniye sonra tekrar deneyin.`)
    } else {
      toast.error('Onaylanamadı: ' + ((!res.success && res.error) || 'Bilinmeyen hata'))
    }
  }

  // Kısa video reject: post DB'den silinir, R2 audio temizlenir, kota refund YOK
  async function handleRejectShortVideo() {
    if (rejecting) return
    if (!generatedPost?.post_id) {
      // Henüz Stage 1 başlamadıysa direkt geri dön
      setStep(2)
      return
    }
    setRejecting(true)
    const res = await api.post(`/posts/${generatedPost.post_id}/reject-short-video`, {})
    setRejecting(false)
    if (res.success) {
      toast.message('Üretim iptal edildi (kota geri verilmedi)')
    } else {
      toast.error('İptal edilemedi: ' + (res.error ?? 'Bilinmeyen hata'))
    }
    setGeneratedPost(null)
    setStage1Edited(false)
    setStep(2)
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
    setStage1Edited(false)
    setSpecialDayFormat(null)
    setSelectedSceneReference(null)
    // Akordeon durumu kullanıcı tercihi olarak kalır (persist edildiği için reset etme)
  }

  // Template seçim handler
  function handleSelectTemplate(template: Template) {
    setSelectedTemplate(template)
    // Default değerlerle pre-fill et:
    // - Her form field'ın template'teki defaultValue'su
    // - cta_url özel: marka website_url'i varsa o kullanılır (defaultValue override edilir)
    const defaults: Record<string, unknown> = {}
    for (const f of template.formFields) {
      if (f.defaultValue !== undefined && f.defaultValue !== null && f.defaultValue !== '') {
        defaults[f.id] = f.defaultValue
      }
    }
    if (currentBrand?.website_url && template.formFields.some((f) => f.id === 'cta_url')) {
      defaults['cta_url'] = currentBrand.website_url
    }
    setTemplateFields(defaults)
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

      <StepIndicator step={step} contentType={effectiveContentType} />

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
                    setSpecialDayFormat(null)
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
            {contentType === 'special_day' && specialDayFormat && (
              <Badge variant="secondary">
                {specialDayFormat === 'image' ? '🖼️ Görsel' : specialDayFormat === 'carousel' ? '📱 Carousel' : '🎬 Kısa Video'}
              </Badge>
            )}
            {selectedTemplate && ['image', 'carousel', 'video'].includes(effectiveContentType) && selectedTemplate.id !== DEFAULT_IMAGE_TEMPLATE_ID && selectedTemplate.id !== DEFAULT_CAROUSEL_TEMPLATE_ID && selectedTemplate.id !== DEFAULT_VIDEO_TEMPLATE_ID && !SPECIAL_DAY_TEMPLATE_ID_SET.has(selectedTemplate.id) && (
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

          {/* Özel Gün — format seçici + alt tip + tatil seçici (Sprint 2) */}
          {contentType === 'special_day' && (
            <div className="space-y-5">
              {/* Format segmented control */}
              <div className="space-y-2">
                <Label>Format Seçimi</Label>
                <div className="grid grid-cols-3 gap-2">
                  {([
                    { id: 'image' as SpecialDayFormat, label: 'Görsel', icon: '🖼️' },
                    { id: 'carousel' as SpecialDayFormat, label: 'Carousel', icon: '📱' },
                    { id: 'video' as SpecialDayFormat, label: 'Kısa Video', icon: '🎬' },
                  ]).map((f) => (
                    <button
                      key={f.id}
                      onClick={async () => {
                        if (specialDayFormat === f.id) return
                        setSpecialDayFormat(f.id)
                        setMode('template')
                        setSelectedTemplate(null)
                        setTemplateFields({})
                        setImageTextFields(null)
                        setCaptionData(null)
                        setPhase('form')
                        setLoadingDefaultTemplate(true)
                        try {
                          const tpl = await fetchTemplateById(SPECIAL_DAY_TEMPLATE_IDS[f.id])
                          if (tpl) {
                            handleSelectTemplate(tpl)
                          } else {
                            toast.error('Özel gün şablonu yüklenemedi.')
                          }
                        } finally {
                          setLoadingDefaultTemplate(false)
                        }
                      }}
                      className={cn(
                        'flex flex-col items-center gap-1 p-3 rounded-xl border-2 transition-all',
                        specialDayFormat === f.id
                          ? 'border-amber-500 bg-amber-50'
                          : 'border-gray-200 hover:border-amber-300 hover:bg-amber-50/30'
                      )}
                    >
                      <span className="text-xl">{f.icon}</span>
                      <span className="text-xs font-medium text-gray-700">{f.label}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Alt tip seçici (genel/ürün) — format seçildikten sonra görünür */}
              {specialDayFormat && (
                <div className="space-y-2">
                  <Label>İçerik Türü</Label>
                  <div className="grid grid-cols-2 gap-3">
                    {([
                      {
                        id: 'general' as ImageSubType,
                        label: specialDayFormat === 'video' ? 'Genel Video' : 'Genel İçerik',
                        desc: 'Tatilin anlamı + marka tonu',
                        icon: specialDayFormat === 'video' ? '🎬' : '🖼️',
                      },
                      {
                        id: 'product' as ImageSubType,
                        label: 'Ürün / Hizmet',
                        desc: 'Tatil bağlamında ürün/hizmet öne çıkarılır',
                        icon: '📦',
                      },
                    ]).map((sub) => (
                      <button
                        key={sub.id}
                        onClick={() => setImageSubType(sub.id)}
                        className={cn(
                          'flex flex-col items-start gap-1 p-3 rounded-xl border-2 text-left transition-all',
                          imageSubType === sub.id
                            ? 'border-amber-500 bg-amber-50'
                            : 'border-gray-200 hover:border-amber-300 hover:bg-amber-50/30'
                        )}
                      >
                        <span className="text-lg">{sub.icon}</span>
                        <span className="text-sm font-medium text-gray-800">{sub.label}</span>
                        <span className="text-xs text-gray-500 leading-snug">{sub.desc}</span>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Tatil seçici — format seçildikten sonra görünür */}
              {specialDayFormat && (
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
                          onClick={() => {
                            if (isPast) return
                            setSelectedHoliday(h)
                            // Tatil adını şablonun holiday_name field'ına otomatik yansıt.
                            // Kullanıcı sonradan üzerine yazabilir; farklı tatil seçilirse yenilenir.
                            setTemplateFields((prev) => ({ ...prev, holiday_name: h.name_tr }))
                          }}
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
                      <button
                        onClick={() => {
                          setSelectedHoliday(null)
                          setTemplateFields((prev) => {
                            const next = { ...prev }
                            delete next.holiday_name
                            return next
                          })
                        }}
                        className="ml-auto text-xs text-amber-600 hover:underline"
                      >
                        Temizle
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Sahne için referans görsel — özel gün + genel mod, tatil seçicinin hemen altında */}
              {specialDayFormat && imageSubType === 'general' && currentBrand?.id && (
                <SceneReferencePicker
                  brandId={currentBrand.id}
                  value={selectedSceneReference}
                  onChange={setSelectedSceneReference}
                />
              )}
            </div>
          )}

          {/* Varsayılan şablon fetch edilirken loader */}
          {(effectiveContentType === 'image' || effectiveContentType === 'carousel' || effectiveContentType === 'video') && loadingDefaultTemplate && (
            <div className="flex items-center justify-center py-12 text-gray-500 gap-3">
              <Loader2 className="w-5 h-5 animate-spin" />
              <span className="text-sm">
                {contentType === 'special_day' ? 'Özel gün şablonu yükleniyor...' : effectiveContentType === 'carousel' ? 'Carousel şablonu yükleniyor...' : effectiveContentType === 'video' ? 'Video şablonu yükleniyor...' : 'Varsayılan görsel şablonu yükleniyor...'}
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

          {/* Phase 7: phase=form — dinamik form + aspect/platform/docs + "Caption Üret"
              NOT: genel-gorsel-sablon akordeon yapıya geçti (aşağıda ayrı blok). */}
          {['image', 'carousel', 'video'].includes(effectiveContentType) && mode === 'template' && phase === 'form' && selectedTemplate && selectedTemplate.id !== DEFAULT_IMAGE_TEMPLATE_ID && (
            <div className="space-y-5">
              {selectedTemplate.id !== DEFAULT_IMAGE_TEMPLATE_ID && selectedTemplate.id !== DEFAULT_CAROUSEL_TEMPLATE_ID && selectedTemplate.id !== DEFAULT_VIDEO_TEMPLATE_ID && !SPECIAL_DAY_TEMPLATE_ID_SET.has(selectedTemplate.id) && (
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
                            // Video modunda backend Stage 1'de template_fields'i otomatik
                            // inject ediyor (ana_konu = product.name); frontend auto-fill yapmaz.
                            // Image/Carousel'de template form alanlarına yansıtmaya devam et.
                            if (effectiveContentType !== 'video') {
                              setTemplateFields((prev) => ({
                                ...prev,
                                ana_konu: p.name,
                                one_cikan_ozellik: p.description ?? '',
                              }))
                            }
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

              {/* Çoklu görsel Sprint 3 — ürün için kullanılacak görselleri seç.
                  Sadece ürün modu + birden fazla görseli olan ürün varsa görünür. */}
              {imageSubType === 'product' && selectedProduct && selectedProduct.images.length > 1 && (
                <div className="space-y-2">
                  <Label>
                    Hangi görseller kullanılsın?{' '}
                    <span className="font-normal text-gray-400">
                      ({selectedProductImageIds.length}/{Math.min(3, selectedProduct.images.length)})
                    </span>
                  </Label>
                  <p className="text-xs text-gray-500">
                    Seçilen görseller AI&apos;a referans olarak gönderilir. En iyi çıktı kalitesi için en fazla 3 görsel seçin. Farklı açılar (ön/yan/kullanım) sahneyi güçlendirir; renk varyantlarını karıştırmayın.
                  </p>
                  <div className="grid grid-cols-4 gap-2">
                    {selectedProduct.images.map((img) => {
                      const selected = selectedProductImageIds.includes(img.id)
                      return (
                        <button
                          key={img.id}
                          type="button"
                          onClick={() => {
                            setSelectedProductImageIds((prev) => {
                              if (prev.includes(img.id)) {
                                if (prev.length === 1) {
                                  toast.error('En az 1 görsel seçili olmalı')
                                  return prev
                                }
                                return prev.filter((id) => id !== img.id)
                              }
                              if (prev.length >= 3) {
                                toast.error('En fazla 3 görsel seçebilirsiniz')
                                return prev
                              }
                              return [...prev, img.id]
                            })
                          }}
                          className={cn(
                            'relative block w-full aspect-square rounded-lg overflow-hidden border-2 transition-all',
                            selected
                              ? 'border-blue-500 ring-2 ring-blue-200'
                              : 'border-gray-200 hover:border-blue-300 opacity-60 hover:opacity-100'
                          )}
                          title={img.label ?? (img.is_primary ? 'Ana görsel' : 'Görsel')}
                        >
                          {/* eslint-disable-next-line @next/next/no-img-element */}
                          <img
                            src={img.image_url}
                            alt={img.label ?? 'Ürün görseli'}
                            className="w-full h-full object-cover"
                          />
                          {img.is_primary && (
                            <span className="absolute top-1 left-1 bg-amber-400 text-white rounded-full p-0.5">
                              <Star className="w-3 h-3" fill="currentColor" />
                            </span>
                          )}
                          {selected && (
                            <span className="absolute top-1 right-1 bg-blue-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold">
                              ✓
                            </span>
                          )}
                        </button>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Çoklu görsel Sprint 3 — carousel modunda görsel dağıtım kontrolü. */}
              {effectiveContentType === 'carousel' && selectedProduct && selectedProductImageIds.length > 1 && (
                <div className="space-y-2">
                  <Label>Görsel Dağılımı</Label>
                  <div className="flex rounded-xl border border-gray-200 bg-gray-50 p-1">
                    <button
                      type="button"
                      onClick={() => setCarouselImageMode('auto')}
                      className={cn(
                        'flex-1 rounded-lg px-3 py-2 text-sm font-medium transition-all',
                        carouselImageMode === 'auto'
                          ? 'bg-white text-gray-900 shadow-sm'
                          : 'text-gray-500 hover:text-gray-700'
                      )}
                    >
                      Otomatik dağıt
                    </button>
                    <button
                      type="button"
                      onClick={() => setCarouselImageMode('primary_only')}
                      className={cn(
                        'flex-1 rounded-lg px-3 py-2 text-sm font-medium transition-all',
                        carouselImageMode === 'primary_only'
                          ? 'bg-white text-gray-900 shadow-sm'
                          : 'text-gray-500 hover:text-gray-700'
                      )}
                    >
                      Hepsi ana görsel
                    </button>
                  </div>
                  <p className="text-xs text-gray-500">
                    {carouselImageMode === 'auto'
                      ? 'Slide\'lar seçili görseller arasında sırayla dağıtılır.'
                      : 'Tüm slide\'larda ana görsel kullanılır.'}
                  </p>
                </div>
              )}

              {/* İstek/yönlendirme alanı — video modunda "Bu video ne anlatsın?" varyantı.
                  DynamicForm'dan ÖNCE (Yönlendirme grubunun üstünde) — kullanıcı önce
                  serbest tarifi yazsın, sonra cta gibi yapısal alanları doldursun. */}
              <div className="space-y-1.5">
                <Label>
                  {effectiveContentType === 'video' ? (
                    <>
                      Bu video ne anlatsın?{' '}
                      <span className="font-normal text-gray-400">
                        ({imageSubType === 'general' ? 'zorunlu' : 'opsiyonel'})
                      </span>
                    </>
                  ) : (
                    <>
                      Tasarım ve içerik için istekleriniz{' '}
                      <span className="font-normal text-gray-400">(opsiyonel)</span>
                    </>
                  )}
                </Label>
                <Textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder={
                    effectiveContentType === 'video'
                      ? imageSubType === 'general'
                        ? 'Örn: "Sabah meditasyonu zihni nasıl temizler 30 saniyede anlat", "5 adımda evden iş kurma ipuçları"'
                        : 'Örn: "Bu ürünün indirim kampanyasını vurgula", "kullanım anlarını öne çıkar" (boş bırakırsanız ürün adı ve açıklaması kullanılır)'
                      : 'Örn: "Tenis kıyafetli bir kadın spor ayakkabıyı giyerken göster", "gönderi metninde %20 indirim vurgusu olsun", "stüdyo yerine plaj arka planı"'
                  }
                  rows={3}
                  className="resize-none"
                />
                <p className="text-xs text-gray-500">
                  {effectiveContentType === 'video'
                    ? imageSubType === 'general'
                      ? 'Video script\'i ve gönderi metni buradaki anlatımdan üretilir.'
                      : 'Boş bırakırsanız ürünün adı ve açıklaması temel alınır.'
                    : 'Yazdıklarınız şablon varsayılanlarını geçersiz kılar — hem görsel hem metin buradaki isteklere göre şekillenir.'}
                </p>
              </div>

              {/* Sahne için referans görsel — özel gün dışı genel modlar; prompt textarea'sının hemen altında */}
              {contentType !== 'special_day' && imageSubType === 'general' && currentBrand?.id && ['image', 'carousel', 'video'].includes(effectiveContentType) && (
                <SceneReferencePicker
                  brandId={currentBrand.id}
                  value={selectedSceneReference}
                  onChange={setSelectedSceneReference}
                />
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
              {effectiveContentType !== 'video' && (currentBrand?.logo_light_url || currentBrand?.logo_dark_url) && (
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
              {effectiveContentType === 'video' && (
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
              {effectiveContentType === 'video' && (
                <div className="space-y-1.5">
                  <Label className="text-sm">Ses Seçimi</Label>
                  <div className="flex flex-wrap gap-2">
                    {(voices.length > 0
                      ? voices
                      : [
                          { id: 'qSeXEcewz7tA0Q0qk9fH', name: 'Buse (Kadın)', gender: 'female' },
                          { id: 'EST9Ui6982FZPSi7gCHi', name: 'Zeynep (Kadın)', gender: 'female' },
                          { id: 'kPzsL2i3teMYv0FxEYQ6', name: 'Eylül (Kadın)', gender: 'female' },
                          { id: 'IuRRIAcbQK5AQk1XevPj', name: 'Emre (Erkek)', gender: 'male' },
                          { id: 'ctoYieZ4J7WwcdhujpMq', name: 'Kaan (Erkek)', gender: 'male' },
                          { id: 'UgBBYS2sOqTuMpoF3BR0', name: 'Ahmet (Erkek)', gender: 'male' },
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

              {/* Video: Altyazı toggle */}
              {effectiveContentType === 'video' && (
                <div className="flex items-center justify-between">
                  <Label className="text-sm">Altyazı (Subtitle)</Label>
                  <button
                    onClick={() => setSubtitleEnabled(!subtitleEnabled)}
                    className={cn(
                      'relative inline-flex h-5 w-9 items-center rounded-full transition-colors',
                      subtitleEnabled ? 'bg-purple-600' : 'bg-gray-300'
                    )}
                  >
                    <span
                      className={cn(
                        'inline-block h-3.5 w-3.5 rounded-full bg-white transition-transform',
                        subtitleEnabled ? 'translate-x-[18px]' : 'translate-x-[3px]'
                      )}
                    />
                  </button>
                </div>
              )}

              <Button
                onClick={handleGenerateCaption}
                className="w-full gap-2"
                disabled={loadingCaption}
              >
                {loadingCaption ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
                {effectiveContentType === 'video' ? 'Gönderi Metni ve Script Üret' : 'Gönderi Metni Üret'}
              </Button>
            </div>
          )}

          {/* genel-gorsel-sablon — 4 katlanabilir blokla yeniden düzenlenmiş Step 2 layout */}
          {effectiveContentType === 'image' && mode === 'template' && phase === 'form' && selectedTemplate && selectedTemplate.id === DEFAULT_IMAGE_TEMPLATE_ID && (
            <div className="space-y-3">
              {/* ── Group-1: Görsel Kaynakları ─────────────────────────────── */}
              <AccordionBlock
                icon="📦"
                title="Görsel Kaynakları"
                summary={(() => {
                  if (imageSubType === 'product') {
                    if (!selectedProduct) return 'ürün seçilmedi'
                    return `${selectedProduct.name} · ${selectedProductImageIds.length} görsel`
                  }
                  return selectedSceneReference ? 'sahne referansı var' : 'sahne referansı yok'
                })()}
                isOpen={accordion.group1}
                onToggle={() => toggleAccordion('group1')}
              >
                {/* Ürün/Hizmet seçici */}
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

                {/* Çoklu görsel seçici */}
                {imageSubType === 'product' && selectedProduct && selectedProduct.images.length > 1 && (
                  <div className="space-y-2">
                    <Label>
                      Hangi görseller kullanılsın?{' '}
                      <span className="font-normal text-gray-400">
                        ({selectedProductImageIds.length}/{Math.min(3, selectedProduct.images.length)})
                      </span>
                    </Label>
                    <p className="text-xs text-gray-500">
                      Seçilen görseller AI&apos;a referans olarak gönderilir. En iyi çıktı kalitesi için en fazla 3 görsel seçin. Farklı açılar (ön/yan/kullanım) sahneyi güçlendirir; renk varyantlarını karıştırmayın.
                    </p>
                    <div className="grid grid-cols-4 gap-2">
                      {selectedProduct.images.map((img) => {
                        const selected = selectedProductImageIds.includes(img.id)
                        return (
                          <button
                            key={img.id}
                            type="button"
                            onClick={() => {
                              setSelectedProductImageIds((prev) => {
                                if (prev.includes(img.id)) {
                                  if (prev.length === 1) {
                                    toast.error('En az 1 görsel seçili olmalı')
                                    return prev
                                  }
                                  return prev.filter((id) => id !== img.id)
                                }
                                if (prev.length >= 3) {
                                  toast.error('En fazla 3 görsel seçebilirsiniz')
                                  return prev
                                }
                                return [...prev, img.id]
                              })
                            }}
                            className={cn(
                              'relative block w-full aspect-square rounded-lg overflow-hidden border-2 transition-all',
                              selected
                                ? 'border-blue-500 ring-2 ring-blue-200'
                                : 'border-gray-200 hover:border-blue-300 opacity-60 hover:opacity-100'
                            )}
                            title={img.label ?? (img.is_primary ? 'Ana görsel' : 'Görsel')}
                          >
                            {/* eslint-disable-next-line @next/next/no-img-element */}
                            <img
                              src={img.image_url}
                              alt={img.label ?? 'Ürün görseli'}
                              className="w-full h-full object-cover"
                            />
                            {img.is_primary && (
                              <span className="absolute top-1 left-1 bg-amber-400 text-white rounded-full p-0.5">
                                <Star className="w-3 h-3" fill="currentColor" />
                              </span>
                            )}
                            {selected && (
                              <span className="absolute top-1 right-1 bg-blue-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold">
                                ✓
                              </span>
                            )}
                          </button>
                        )
                      })}
                    </div>
                  </div>
                )}

                {/* Sahne referans görseli — genel mod */}
                {imageSubType === 'general' && currentBrand?.id && (
                  <SceneReferencePicker
                    brandId={currentBrand.id}
                    value={selectedSceneReference}
                    onChange={setSelectedSceneReference}
                  />
                )}
              </AccordionBlock>

              {/* ── Group-2: Konu (default açık) ───────────────────────────── */}
              <AccordionBlock
                icon="📝"
                title="Konu"
                summary={(() => {
                  const ak = String(templateFields.ana_konu ?? '').trim()
                  if (!ak) return 'henüz doldurulmadı'
                  return ak.length > 40 ? ak.slice(0, 40) + '…' : ak
                })()}
                isOpen={accordion.group2}
                onToggle={() => toggleAccordion('group2')}
              >
                {/* Tasarım ve içerik için istekleriniz */}
                <div className="space-y-1.5">
                  <Label>
                    Tasarım ve içerik için istekleriniz{' '}
                    <span className="font-normal text-gray-400">(opsiyonel)</span>
                  </Label>
                  <Textarea
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder='Örn: "Tenis kıyafetli bir kadın spor ayakkabıyı giyerken göster", "gönderi metninde %20 indirim vurgusu olsun", "stüdyo yerine plaj arka planı"'
                    rows={3}
                    className="resize-none"
                  />
                  <p className="text-xs text-gray-500">
                    Yazdıklarınız şablon varsayılanlarını geçersiz kılar — hem görsel hem metin buradaki isteklere göre şekillenir.
                  </p>
                </div>

                <DynamicForm
                  template={selectedTemplate}
                  values={templateFields}
                  onChange={(id, v) =>
                    setTemplateFields((prev) => ({ ...prev, [id]: v }))
                  }
                  imageTextFields={imageTextFields ?? undefined}
                  onImageTextFieldsChange={setImageTextFields}
                  groupFilter="Konu"
                />

                {/* Dokümandan bağlam — sadece genel mod */}
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
              </AccordionBlock>

              {/* ── Group-3: Yönlendirme & Logo ─────────────────────────────── */}
              <AccordionBlock
                icon="🎯"
                title="Yönlendirme & Logo"
                summary={(() => {
                  const cta = String(templateFields.cta_url ?? '').trim()
                  const ctaLabel = cta ? 'Link var' : 'Link yok'
                  const hasLogo = currentBrand?.logo_light_url || currentBrand?.logo_dark_url
                  const logoLabel = hasLogo ? (useLogoOverlay ? 'Logo açık' : 'Logo kapalı') : null
                  return logoLabel ? `${ctaLabel} · ${logoLabel}` : ctaLabel
                })()}
                isOpen={accordion.group3}
                onToggle={() => toggleAccordion('group3')}
              >
                <DynamicForm
                  template={selectedTemplate}
                  values={templateFields}
                  onChange={(id, v) =>
                    setTemplateFields((prev) => ({ ...prev, [id]: v }))
                  }
                  groupFilter="Yönlendirme"
                />

                {/* Logo filigran toggle */}
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
              </AccordionBlock>

              {/* ── Group-4: Yayın ─────────────────────────────────────────── */}
              <AccordionBlock
                icon="📤"
                title="Yayın"
                summary={(() => {
                  const first = platforms[0]
                  const firstLabel = first ? (PLATFORMS.find((p) => p.id === first)?.label ?? first) : null
                  const more = platforms.length > 1 ? ` +${platforms.length - 1}` : ''
                  const platformLabel = firstLabel ? `${firstLabel}${more}` : 'platform yok'
                  return `${platformLabel} · ${aspectRatio}`
                })()}
                isOpen={accordion.group4}
                onToggle={() => toggleAccordion('group4')}
              >
                {/* En-Boy Oranı */}
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
              </AccordionBlock>

              <Button
                onClick={handleGenerateCaption}
                className="w-full gap-2"
                disabled={loadingCaption}
              >
                {loadingCaption ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
                Gönderi Metni Üret
              </Button>
            </div>
          )}

          {/* Phase 7: phase=caption — caption düzenle + "Görseli/Videoyu Üret" (template veya free) */}
          {['image', 'carousel', 'video'].includes(effectiveContentType) && phase === 'caption' && captionData && (
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
              {effectiveContentType === 'video' && (
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
                  effectiveContentType === 'video'
                    ? !script.trim()
                    : effectiveContentType === 'carousel'
                    ? !(captionData.image_prompts && captionData.image_prompts.length > 0)
                    : !captionData.image_prompt.trim()
                )}
              >
                <Wand2 className="w-4 h-4" />
                {effectiveContentType === 'video' ? 'Videoyu Üret' : effectiveContentType === 'carousel' ? 'Slide Görsellerini Üret' : 'Görseli Üret'}
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

          {/* Klasik akış — sadece quote (özel gün artık Akış C unified flow'a geçti) */}
          {contentType === 'quote' && (
          <>
          {/* Alıntı — quote input */}
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

          {/* İçerik Üret butonu */}
          <Button
            onClick={handleGenerate}
            className="w-full gap-2"
            disabled={!quoteText.trim()}
          >
            <Wand2 className="w-4 h-4" />
            İçerik Üret
          </Button>
          </>
          )}
        </div>
      )}

      {/* ── STEP 3 (VIDEO): Önizleme & Onay — Stage 1 sonucu, Wan I2V'den önce ── */}
      {step === 3 && effectiveContentType === 'video' && (
        <div className="space-y-5">
          <div className="flex items-center justify-between">
            <button
              onClick={handleRejectShortVideo}
              disabled={generating || approving || rejecting}
              className="text-xs text-blue-500 hover:underline disabled:text-gray-300"
            >
              ← Geri Dön & Yeniden Üret
            </button>
            <button onClick={resetWizard} className="text-xs text-gray-400 hover:text-gray-600">
              Yeni İçerik Oluştur
            </button>
          </div>

          {/* Stage 1 hâlâ üretim aşamasında */}
          {generating && (
            <div className="flex flex-col items-center justify-center py-16 gap-4">
              <div className="w-16 h-16 rounded-2xl bg-purple-100 flex items-center justify-center">
                <Loader2 className="w-8 h-8 animate-spin text-purple-600" />
              </div>
              <p className="text-gray-700 font-medium">Ses ve sahne hazırlanıyor...</p>
              <p className="text-sm text-gray-400 text-center px-4">
                Seslendirme ve ön sahne görseli üretiliyor — yaklaşık 15-25 saniye sürebilir.
                Onaylamadıkça video render edilmez.
              </p>
            </div>
          )}

          {/* Stage 1 hazır — caption + script + audio + still önizleme */}
          {!generating && generatedPost && generatedPost.status === 'awaiting_approval' && (
            <div className="space-y-5">
              {stage1Edited && (
                <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
                  <strong className="font-semibold">Düzenleme yapıldı.</strong>{' '}
                  Yeni ses ve görselin üretilmesi için &quot;Geri Dön &amp; Yeniden Üret&quot;e
                  basmanız gerekir. Aksi halde aşağıdaki ses/görsel ile devam edilir.
                </div>
              )}

              {/* Still image önizleme */}
              {generatedPost.still_image_url && (
                <div className="rounded-2xl overflow-hidden bg-gradient-to-br from-purple-50 to-violet-100 border border-purple-200">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={generatedPost.still_image_url}
                    alt="Sahne önizlemesi"
                    className="w-full max-h-80 object-contain"
                  />
                  <div className="px-4 py-2 bg-white/60 border-t border-purple-200 text-xs text-purple-700">
                    🎬 Bu görsel video sunumunda animasyona dönüşür
                  </div>
                </div>
              )}

              {/* Audio player */}
              {generatedPost.audio_url && (
                <div className="rounded-xl border border-purple-200 bg-white p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <Label className="text-sm text-purple-800">Seslendirme Önizlemesi</Label>
                    {generatedPost.duration_estimate && (
                      <span className="text-xs text-purple-500">
                        ~{generatedPost.duration_estimate} saniye
                      </span>
                    )}
                  </div>
                  <audio src={generatedPost.audio_url} controls className="w-full h-10" />
                </div>
              )}

              {/* Caption editor (Stage 1'de düzenleme banner tetikler) */}
              {captionData && (
                <CaptionEditor
                  data={captionData}
                  platforms={platforms}
                  onChange={(d) => {
                    setCaptionData(d)
                    setStage1Edited(true)
                  }}
                />
              )}

              {/* Script düzenleme */}
              <div className="space-y-3 p-4 bg-purple-50 border border-purple-200 rounded-xl">
                <div>
                  <Label className="text-purple-800">Video Script</Label>
                  <p className="text-xs text-purple-500 mt-0.5">
                    Sesin okuduğu metin — düzenleme yaparsanız yeni ses üretilmez (Geri Dön gerekir)
                  </p>
                </div>
                <Textarea
                  value={script}
                  onChange={(e) => {
                    setScript(e.target.value)
                    setStage1Edited(true)
                  }}
                  rows={5}
                  className="resize-none bg-white text-sm"
                />
              </div>

              {/* Action buttons */}
              <div className="flex gap-3 pt-2">
                <Button
                  variant="outline"
                  className="flex-1 gap-2"
                  onClick={handleRejectShortVideo}
                  disabled={approving || rejecting}
                >
                  {rejecting ? <Loader2 className="w-4 h-4 animate-spin" /> : <X className="w-4 h-4" />}
                  Geri Dön & Yeniden Üret
                </Button>
                <Button
                  className="flex-1 gap-2"
                  onClick={handleApproveShortVideo}
                  disabled={approving || rejecting}
                >
                  {approving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
                  Onayla & Videoyu Üret
                </Button>
              </div>
              <p className="text-xs text-gray-400 text-center">
                &quot;Geri Dön&quot; tuşu önizlemeyi siler ve sizi içerik detaylarına geri gönderir.
                Kullanılan kota geri verilmez.
              </p>
            </div>
          )}
        </div>
      )}

      {/* ── STEP 3 (NON-VIDEO) veya STEP 4 (VIDEO): Final Önizleme ───────── */}
      {((step === 3 && effectiveContentType !== 'video') || step === 4) && (
        <div className="space-y-5">
          <div className="flex items-center justify-between">
            {/* Video Step 4'te post zaten render ediliyor — geri dönüş resetWizard ile */}
            {effectiveContentType === 'video' ? (
              <span />
            ) : (
              <button
                onClick={() => { setStep(2); setGeneratedPost(null); setCaption(''); setHashtags([]) }}
                className="text-xs text-blue-500 hover:underline"
              >
                ← Geri
              </button>
            )}
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
                  effectiveContentType === 'video' ? 'bg-purple-100' : 'bg-blue-100'
                )}>
                  <Loader2 className={cn(
                    'w-8 h-8 animate-spin',
                    effectiveContentType === 'video' ? 'text-purple-600' : 'text-blue-600'
                  )} />
                </div>
              </div>
              <p className="text-gray-700 font-medium">
                {contentType === 'special_day' ? `${selectedHoliday?.name_tr} içeriği üretiliyor...` :
                 effectiveContentType === 'video' ? 'Video üretiliyor...' :
                 contentType === 'quote' ? 'Alıntı kartı üretiliyor...' :
                 effectiveContentType === 'carousel' ? 'Carousel slide görselleri üretiliyor...' :
                 'İçeriğiniz üretiliyor...'}
              </p>
              <p className="text-sm text-gray-400">
                {effectiveContentType === 'video'
                  ? 'Script ve ses oluşturuluyor, arka plan videosu hazırlanıyor...'
                  : effectiveContentType === 'carousel'
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
              {effectiveContentType === 'video' ? (
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
                    <div className="flex flex-col items-center justify-center py-12 gap-4">
                      <div className="w-14 h-14 rounded-xl bg-purple-200 flex items-center justify-center">
                        <Loader2 className="w-7 h-7 text-purple-600 animate-spin" />
                      </div>
                      {(() => {
                        const stage = generatedPost.template_fields?.generation_stage || 'generating'
                        const stages = [
                          { key: 'script_done', label: 'Script üretildi' },
                          { key: 'tts_done', label: 'Seslendirme tamamlandı' },
                          { key: 'generating_video', label: 'Video hazırlanıyor...' },
                        ]
                        const currentIdx = stages.findIndex(s => s.key === stage)
                        return (
                          <div className="flex flex-col items-center gap-2">
                            <div className="flex items-center gap-2">
                              {stages.map((s, i) => {
                                const done = i <= currentIdx && currentIdx >= 0
                                const active = i === currentIdx
                                return (
                                  <div key={s.key} className="flex items-center gap-1.5">
                                    <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold ${done ? 'bg-purple-600 text-white' : 'bg-purple-100 text-purple-400'}`}>
                                      {done ? '✓' : i + 1}
                                    </div>
                                    <span className={`text-xs ${active ? 'text-purple-700 font-medium' : done ? 'text-purple-500' : 'text-purple-300'}`}>{s.label}</span>
                                    {i < stages.length - 1 && <span className="text-purple-200 mx-1">→</span>}
                                  </div>
                                )
                              })}
                            </div>
                            <p className="text-xs text-purple-500 mt-1">Bu 1-3 dakika sürebilir</p>
                          </div>
                        )
                      })()}
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
              ) : effectiveContentType === 'carousel' && generatedPost.slides && generatedPost.slides.length > 0 ? (
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
