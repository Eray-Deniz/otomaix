'use client'

export const dynamic = 'force-dynamic'

import { useState, useCallback, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { toast } from 'sonner'
import { analytics } from '@/lib/analytics'
import { Loader2, Wand2, RefreshCw, Calendar, Send, X, Lightbulb, FileText } from 'lucide-react'
import Image from 'next/image'
import { cn } from '@/lib/utils'

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
type ContentCategory = 'product' | 'service' | 'corporate'
type AspectRatio = '1:1' | '9:16' | '4:5' | '2:3'
type Step = 1 | 2 | 3

interface GeneratedPost {
  post_id: string
  status: string
  output_url?: string
  caption?: string
  hashtags?: string[]
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
  { id: 'image' as ContentType, label: 'Görsel', icon: '🖼️', active: true },
  { id: 'carousel' as ContentType, label: 'Carousel', icon: '📱', active: true },
  { id: 'video' as ContentType, label: 'Video (Faceless)', icon: '🎬', active: true },
  { id: 'special_day' as ContentType, label: 'Özel Gün', icon: '🎉', active: true },
  { id: 'quote' as ContentType, label: 'Alıntı', icon: '💬', active: true },
]

const CONTENT_CATEGORIES: { id: ContentCategory; label: string }[] = [
  { id: 'product', label: 'Ürün Tanıtımı' },
  { id: 'service', label: 'Hizmet Tanıtımı' },
  { id: 'corporate', label: 'Firma Tanıtımı' },
]

const ASPECT_RATIOS: { id: AspectRatio; label: string; desc: string; icon: string }[] = [
  { id: '1:1', label: '1:1', desc: 'Instagram', icon: '⬜' },
  { id: '9:16', label: '9:16', desc: 'Reels / TikTok', icon: '📱' },
  { id: '4:5', label: '4:5', desc: 'Instagram Dikey', icon: '🖼️' },
  { id: '2:3', label: '2:3', desc: 'Pinterest', icon: '📌' },
]

const PLATFORMS = [
  { id: 'instagram', label: 'Instagram' },
  { id: 'tiktok', label: 'TikTok' },
  { id: 'linkedin', label: 'LinkedIn' },
  { id: 'facebook', label: 'Facebook' },
  { id: 'youtube', label: 'YouTube' },
  { id: 'twitter', label: 'Twitter / X' },
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
  const currentBrand = useAppStore((s) => s.currentBrand)

  // Step state
  const [step, setStep] = useState<Step>(1)

  // Step 1
  const [contentType, setContentType] = useState<ContentType>('image')
  const [category, setCategory] = useState<ContentCategory>('product')

  // Step 2
  const [prompt, setPrompt] = useState('')
  const [ideas, setIdeas] = useState<string[]>([])
  const [loadingIdeas, setLoadingIdeas] = useState(false)
  const [aspectRatio, setAspectRatio] = useState<AspectRatio>('1:1')
  const [platforms, setPlatforms] = useState<string[]>(['instagram'])
  const [availableDocs, setAvailableDocs] = useState<BrandDocument[]>([])
  const [selectedDocIds, setSelectedDocIds] = useState<string[]>([])

  // Faceless video — Step 2
  const [script, setScript] = useState('')
  const [loadingScript, setLoadingScript] = useState(false)
  const [voices, setVoices] = useState<TurkishVoice[]>([])
  const [selectedVoice, setSelectedVoice] = useState('tr-TR-EmelNeural')
  const [durationEstimate, setDurationEstimate] = useState<number | null>(null)

  // Özel Gün — Step 2
  const [holidays, setHolidays] = useState<Holiday[]>([])
  const [selectedHoliday, setSelectedHoliday] = useState<Holiday | null>(null)

  // Alıntı — Step 2
  const [quoteText, setQuoteText] = useState('')
  const [quoteAuthor, setQuoteAuthor] = useState('')

  // Step 3
  const [generating, setGenerating] = useState(false)
  const [generatedPost, setGeneratedPost] = useState<GeneratedPost | null>(null)
  const [caption, setCaption] = useState('')
  const [hashtags, setHashtags] = useState<string[]>([])
  const [newHashtag, setNewHashtag] = useState('')

  // ── Fetch brand documents & voices ──────────────────────────────────────────

  useEffect(() => {
    async function fetchDocs() {
      if (!currentBrand?.id) return
      const res = await api.get<BrandDocument[]>(`/documents?brand_id=${currentBrand.id}`)
      if (res.success && res.data) setAvailableDocs(res.data)
    }
    fetchDocs()
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

  function toggleDoc(id: string) {
    setSelectedDocIds((prev) =>
      prev.includes(id) ? prev.filter((d) => d !== id) : [...prev, id]
    )
  }

  async function handleGenerateScript() {
    if (!currentBrand?.id || !prompt.trim()) {
      toast.error('Önce bir konu girin')
      return
    }
    setLoadingScript(true)
    const res = await api.post<{ script: string; duration_estimate: number }>('/ai/generate-script', {
      brand_id: currentBrand.id,
      prompt: prompt.trim(),
    })
    if (res.success && res.data) {
      setScript(res.data.script)
      setDurationEstimate(res.data.duration_estimate)
    } else {
      toast.error('Script üretilemedi')
    }
    setLoadingScript(false)
  }

  // ── Step 2 helpers ──────────────────────────────────────────────────────────

  const fetchIdeas = useCallback(async () => {
    if (!currentBrand?.id) { toast.error('Önce bir marka seçin'); return }
    analytics.ideaSuggestionUsed()
    setLoadingIdeas(true)
    const res = await api.post<{ ideas: string[] }>('/ai/suggest-ideas', {
      brand_id: currentBrand.id,
      content_type: contentType,
      content_category: category,
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
  }, [currentBrand?.id, category, contentType, platforms, prompt, selectedDocIds])

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
    if (!['special_day', 'quote'].includes(contentType) && !prompt.trim()) {
      toast.error('Lütfen bir prompt girin')
      return
    }

    analytics.contentCreationStarted(contentType)
    if (selectedDocIds.length > 0) analytics.documentReferenceUsed(selectedDocIds.length)
    const genStart = Date.now()
    setGenerating(true)
    setStep(3)

    if (contentType === 'video') {
      // Faceless video pipeline
      const res = await api.post<GeneratedPost>('/posts/generate-faceless-video', {
        brand_id: currentBrand.id,
        prompt: prompt.trim(),
        voice: selectedVoice,
        document_ids: selectedDocIds,
        aspect_ratio: aspectRatio,
        platforms,
      })
      setGenerating(false)
      if (res.success && res.data) {
        analytics.contentGenerated(contentType, Math.round((Date.now() - genStart) / 1000))
        setGeneratedPost(res.data)
        setScript(res.data.script ?? '')
        setDurationEstimate(res.data.duration_estimate ?? null)
        toast.success('Video üretimi başlatıldı!')
      } else if (!res.success && res.error === 'rate_limit') {
        setStep(2)
        toast.error(`Saatlik limit aşıldı. ${res.retry_after ?? 60} saniye sonra tekrar deneyin.`)
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
      } else {
        toast.error('İçerik üretilemedi: ' + (res.error ?? 'Bilinmeyen hata'))
      }
    } else {
      // Image / Carousel pipeline
      const res = await api.post<GeneratedPost>('/posts/generate', {
        brand_id: currentBrand.id,
        content_type: contentType,
        content_category: category,
        prompt: prompt.trim(),
        user_text: null,
        document_ids: selectedDocIds,
        aspect_ratio: aspectRatio,
        platforms,
      })
      setGenerating(false)
      if (res.success && res.data) {
        analytics.contentGenerated(contentType, Math.round((Date.now() - genStart) / 1000))
        setGeneratedPost(res.data)
        setCaption(res.data.caption ?? '')
        setHashtags(res.data.hashtags ?? [])
        toast.success('İçerik üretimi başlatıldı!')
      } else if (!res.success && res.error === 'rate_limit') {
        setStep(2)
        toast.error(`Saatlik limit aşıldı. ${res.retry_after ?? 60} saniye sonra tekrar deneyin.`)
      } else {
        toast.error('İçerik üretilemedi: ' + (res.error ?? 'Bilinmeyen hata'))
      }
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
  }

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <div className="p-8 max-w-3xl mx-auto">
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
                  disabled={!type.active}
                  onClick={() => type.active && setContentType(type.id as ContentType)}
                  className={cn(
                    'relative flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all',
                    !type.active && 'opacity-50 cursor-not-allowed bg-gray-50',
                    type.active && contentType === type.id
                      ? 'border-blue-500 bg-blue-50'
                      : type.active
                      ? 'border-gray-200 hover:border-blue-300 hover:bg-blue-50/30 cursor-pointer'
                      : 'border-gray-100'
                  )}
                >
                  {!type.active && (
                    <span className="absolute -top-2 left-1/2 -translate-x-1/2 text-[10px] bg-gray-400 text-white px-1.5 py-0.5 rounded-full whitespace-nowrap">
                      Yakında
                    </span>
                  )}
                  <span className="text-2xl">{type.icon}</span>
                  <span className="text-xs font-medium text-gray-700 text-center leading-tight">
                    {type.label}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Category tabs — special_day ve quote için gösterilmez */}
          {!['special_day', 'quote'].includes(contentType) && (
          <div>
            <p className="text-sm font-medium text-gray-700 mb-3">İçerik Kategorisi</p>
            <div className="flex gap-2">
              {CONTENT_CATEGORIES.map((cat) => (
                <button
                  key={cat.id}
                  onClick={() => setCategory(cat.id)}
                  className={cn(
                    'px-4 py-2 rounded-lg text-sm font-medium border transition-colors',
                    category === cat.id
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'border-gray-200 text-gray-600 hover:border-blue-300'
                  )}
                >
                  {cat.label}
                </button>
              ))}
            </div>
          </div>
          )}

          <Button
            onClick={() => setStep(2)}
            className="w-full"
          >
            Devam Et →
          </Button>
        </div>
      )}

      {/* ── STEP 2: İçerik Detayları ─────────────────────────────────────── */}
      {step === 2 && (
        <div className="space-y-5">
          {/* Summary badge */}
          <div className="flex items-center gap-2">
            <Badge variant="secondary">
              {CONTENT_TYPES.find((t) => t.id === contentType)?.icon}{' '}
              {CONTENT_TYPES.find((t) => t.id === contentType)?.label}
            </Badge>
            <Badge variant="secondary">
              {CONTENT_CATEGORIES.find((c) => c.id === category)?.label}
            </Badge>
            <button onClick={() => setStep(1)} className="text-xs text-blue-500 hover:underline ml-auto">
              ← Geri
            </button>
          </div>

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
                      onClick={() => setSelectedHoliday(h)}
                      className={cn(
                        'flex items-center gap-3 px-3 py-2.5 rounded-lg border text-left text-sm transition-colors',
                        selectedHoliday?.date === h.date
                          ? 'border-amber-500 bg-amber-100 text-amber-900'
                          : isPast
                          ? 'border-gray-100 bg-gray-50 text-gray-400 opacity-60'
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

          {/* 1. En-Boy Oranı — video/special_day/quote için gösterilmez */}
          {!['video', 'special_day', 'quote'].includes(contentType) && (
          <div className="space-y-2">
            <Label>En-Boy Oranı</Label>
            <div className="grid grid-cols-4 gap-2">
              {ASPECT_RATIOS.map((ar) => (
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

          {/* 4. Bana fikir öner — sadece image/carousel için */}
          {!['video', 'special_day', 'quote'].includes(contentType) && (
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

          {/* Faceless video — script editörü ve ses seçimi */}
          {contentType === 'video' && (
            <div className="space-y-4 p-4 bg-purple-50 border border-purple-200 rounded-xl">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="text-purple-800">Video Script</Label>
                  <p className="text-xs text-purple-500 mt-0.5">AI Türkçe script üretir, düzenleyebilirsiniz</p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleGenerateScript}
                  disabled={loadingScript || !prompt.trim()}
                  className="gap-1.5 border-purple-300 text-purple-700 hover:bg-purple-100"
                >
                  {loadingScript
                    ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    : <Wand2 className="w-3.5 h-3.5" />
                  }
                  Script Üret
                </Button>
              </div>

              <Textarea
                value={script}
                onChange={(e) => setScript(e.target.value)}
                placeholder="Önce 'Script Üret' butonuna tıklayın ya da doğrudan yazın..."
                rows={5}
                className="resize-none bg-white text-sm"
              />

              {durationEstimate && (
                <p className="text-xs text-purple-600">
                  Tahmini süre: ~{durationEstimate} saniye
                </p>
              )}

              <div className="space-y-1.5">
                <Label className="text-sm text-purple-800">Ses Seçimi</Label>
                <div className="flex flex-wrap gap-2">
                  {(voices.length > 0
                    ? voices
                    : [
                        { id: 'tr-TR-EmelNeural', name: 'Emel (Kadın)', gender: 'female' },
                        { id: 'tr-TR-AhmetNeural', name: 'Ahmet (Erkek)', gender: 'male' },
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
        </div>
      )}

      {/* ── STEP 3: Üretim & Önizleme ────────────────────────────────────── */}
      {step === 3 && (
        <div className="space-y-5">
          <div className="flex items-center justify-between">
            <button onClick={() => setStep(2)} className="text-xs text-blue-500 hover:underline">
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
                 'İçeriğiniz üretiliyor...'}
              </p>
              <p className="text-sm text-gray-400">
                {contentType === 'video'
                  ? 'Script ve ses oluşturuluyor, arka plan videosu hazırlanıyor...'
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
              ) : (
                /* Görsel / Carousel önizleme */
                <div className="rounded-2xl overflow-hidden bg-gradient-to-br from-blue-50 to-indigo-100 border border-blue-200">
                  {generatedPost.output_url ? (
                    <Image
                      src={generatedPost.output_url}
                      alt="Üretilen içerik"
                      width={800}
                      height={800}
                      className="w-full object-contain max-h-80"
                    />
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

              {/* Caption editor */}
              <div className="space-y-1.5">
                <Label>Açıklama Metni</Label>
                <Textarea
                  value={caption}
                  onChange={(e) => setCaption(e.target.value)}
                  placeholder="İçerik açıklamasını buraya yazın veya AI tarafından üretilmiş metni düzenleyin..."
                  rows={4}
                  className="resize-none"
                />
              </div>

              {/* Hashtags */}
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

              {/* Action buttons */}
              <div className="flex gap-3 pt-2">
                <Button
                  variant="outline"
                  className="flex-1 gap-2"
                  onClick={handleRegenerate}
                >
                  <RefreshCw className="w-4 h-4" />
                  Yeniden Üret
                </Button>
                <Button
                  variant="outline"
                  className="flex-1 gap-2"
                  onClick={() => toast.info('Takvim özelliği yakında')}
                >
                  <Calendar className="w-4 h-4" />
                  Takvime Ekle
                </Button>
                <Button
                  className="flex-1 gap-2"
                  onClick={() => toast.info('Yayınlama özelliği yakında')}
                >
                  <Send className="w-4 h-4" />
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
