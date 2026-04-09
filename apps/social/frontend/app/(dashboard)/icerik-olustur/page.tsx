'use client'

export const dynamic = 'force-dynamic'

import { useState, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { toast } from 'sonner'
import { Loader2, Wand2, RefreshCw, Calendar, Send, X, Lightbulb } from 'lucide-react'
import Image from 'next/image'
import { cn } from '@/lib/utils'

// ─── Types ────────────────────────────────────────────────────────────────────

type ContentType = 'image' | 'carousel'
type ContentCategory = 'product' | 'service' | 'corporate'
type AspectRatio = '1:1' | '9:16' | '4:5' | '2:3'
type Step = 1 | 2 | 3

interface GeneratedPost {
  post_id: string
  status: string
  output_url?: string
  caption?: string
  hashtags?: string[]
}

// ─── Constants ────────────────────────────────────────────────────────────────

const CONTENT_TYPES = [
  { id: 'image' as ContentType, label: 'Görsel', icon: '🖼️', active: true },
  { id: 'carousel' as ContentType, label: 'Carousel', icon: '📱', active: true },
  { id: 'video' as ContentType & string, label: 'Video (Faceless)', icon: '🎬', active: false },
  { id: 'special' as ContentType & string, label: 'Özel Gün', icon: '🎉', active: false },
  { id: 'quote' as ContentType & string, label: 'Alıntı', icon: '💬', active: false },
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
  const [useOwnText, setUseOwnText] = useState(false)
  const [ownText, setOwnText] = useState('')
  const [aspectRatio, setAspectRatio] = useState<AspectRatio>('1:1')
  const [platforms, setPlatforms] = useState<string[]>(['instagram'])

  // Step 3
  const [generating, setGenerating] = useState(false)
  const [generatedPost, setGeneratedPost] = useState<GeneratedPost | null>(null)
  const [caption, setCaption] = useState('')
  const [hashtags, setHashtags] = useState<string[]>([])
  const [newHashtag, setNewHashtag] = useState('')

  // ── Step 2 helpers ──────────────────────────────────────────────────────────

  const fetchIdeas = useCallback(async () => {
    if (!currentBrand?.id) { toast.error('Önce bir marka seçin'); return }
    setLoadingIdeas(true)
    const res = await api.post<{ ideas: string[] }>('/ai/suggest-ideas', {
      brand_id: currentBrand.id,
      content_category: category,
      count: 3,
    })
    if (res.success && res.data?.ideas) {
      setIdeas(res.data.ideas)
    } else {
      toast.error('Fikirler alınamadı')
    }
    setLoadingIdeas(false)
  }, [currentBrand?.id, category])

  function togglePlatform(id: string) {
    setPlatforms((prev) =>
      prev.includes(id) ? prev.filter((p) => p !== id) : [...prev, id]
    )
  }

  // ── Step 3: Generate ────────────────────────────────────────────────────────

  async function handleGenerate() {
    if (!currentBrand?.id) { toast.error('Önce bir marka seçin'); return }
    if (!prompt.trim()) { toast.error('Lütfen bir prompt girin'); return }

    setGenerating(true)
    setStep(3)

    const res = await api.post<GeneratedPost>('/posts/generate', {
      brand_id: currentBrand.id,
      content_type: contentType,
      content_category: category,
      prompt: prompt.trim(),
      user_text: useOwnText ? ownText.trim() || null : null,
      aspect_ratio: aspectRatio,
      platforms,
    })

    setGenerating(false)

    if (res.success && res.data) {
      setGeneratedPost(res.data)
      setCaption(res.data.caption ?? '')
      setHashtags(res.data.hashtags ?? [])
      toast.success('İçerik üretimi başlatıldı!')
    } else {
      toast.error('İçerik üretilemedi: ' + (res.error ?? 'Bilinmeyen hata'))
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
    setUseOwnText(false)
    setOwnText('')
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

          {/* Category tabs */}
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

          {/* Prompt */}
          <div className="space-y-1.5">
            <Label>İçerik Açıklaması</Label>
            <Textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Ürününüzü, hedef kitlenizi veya iletmek istediğiniz mesajı açıklayın..."
              rows={4}
              className="resize-none"
            />
          </div>

          {/* Idea suggestions */}
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

          {/* Optional: own text */}
          <div className="space-y-2 p-3 bg-gray-50 rounded-xl">
            <div className="flex items-center justify-between">
              <Label className="font-normal text-sm">Kendi metnini ekle</Label>
              <Switch checked={useOwnText} onCheckedChange={setUseOwnText} />
            </div>
            {useOwnText && (
              <Textarea
                value={ownText}
                onChange={(e) => setOwnText(e.target.value)}
                placeholder="Görselde yer almasını istediğiniz sabit metin..."
                rows={2}
                className="resize-none bg-white"
              />
            )}
          </div>

          {/* Aspect ratio */}
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

          {/* Platforms */}
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

          <Button
            onClick={handleGenerate}
            className="w-full gap-2"
            disabled={!prompt.trim()}
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
                <div className="w-16 h-16 rounded-2xl bg-blue-100 flex items-center justify-center">
                  <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
                </div>
              </div>
              <p className="text-gray-700 font-medium">İçeriğiniz üretiliyor...</p>
              <p className="text-sm text-gray-400">Bu birkaç saniye sürebilir</p>
            </div>
          )}

          {/* Result */}
          {!generating && generatedPost && (
            <div className="space-y-5">
              {/* Image preview placeholder */}
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
