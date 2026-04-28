'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useRef, useState, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { ContentCard, type Post, type PostPublication } from '@/components/content/ContentCard'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { toast } from 'sonner'
import { Loader2, SlidersHorizontal, X, Send, Calendar, RefreshCw, Bell, ChevronLeft, ChevronRight, Download } from 'lucide-react'
import { cn } from '@/lib/utils'
import Image from 'next/image'

// ─── Filter types ─────────────────────────────────────────────────────────────

interface Filters {
  contentType: string | null
  status: string | null
  platform: string | null
}

const CONTENT_TYPE_TABS = [
  { id: null, label: 'Tümü' },
  { id: 'image', label: 'Görsel' },
  { id: 'carousel', label: 'Carousel' },
  { id: 'video', label: 'Video' },
]

const STATUS_OPTIONS = [
  { id: 'draft', label: 'Taslak' },
  { id: 'generating', label: 'Üretiliyor' },
  { id: 'ready', label: 'Hazır' },
  { id: 'scheduled', label: 'Zamanlandı' },
  { id: 'published', label: 'Yayınlandı' },
  { id: 'failed', label: 'Başarısız' },
]

const PLATFORM_OPTIONS = [
  { id: 'instagram', label: 'Instagram' },
  { id: 'tiktok', label: 'TikTok' },
  { id: 'linkedin', label: 'LinkedIn' },
  { id: 'facebook', label: 'Facebook' },
  { id: 'youtube', label: 'YouTube' },
  { id: 'twitter', label: 'Twitter / X' },
]

// ─── Post detail modal ─────────────────────────────────────────────────────────

const STATUS_LABEL: Record<string, string> = {
  draft: 'Taslak', generating: 'Üretiliyor', ready: 'Hazır',
  scheduled: 'Zamanlandı', publishing: 'Yayınlanıyor', published: 'Yayınlandı',
  partially_published: 'Kısmen Yayınlandı',
  failed: 'Başarısız', reviewing: 'İncelemede', rejected: 'Reddedildi',
}

const PLATFORM_LABEL: Record<string, string> = {
  instagram: 'Instagram', tiktok: 'TikTok', linkedin: 'LinkedIn',
  facebook: 'Facebook', youtube: 'YouTube', twitter: 'Twitter / X',
}

function PostDetailModal({
  post,
  open,
  onClose,
  onPublished,
  onApprovalRequested,
  onRegenerated,
  onScheduled,
}: {
  post: Post | null
  open: boolean
  onClose: () => void
  onPublished: (postId: string) => void
  onApprovalRequested: (postId: string) => void
  onRegenerated: (postId: string) => void
  onScheduled: (postId: string) => void
}) {
  const [publishing, setPublishing] = useState(false)
  const [requesting, setRequesting] = useState(false)
  const [regenerating, setRegenerating] = useState(false)
  const [scheduling, setScheduling] = useState(false)
  const [showSchedulePicker, setShowSchedulePicker] = useState(false)
  const [scheduledAt, setScheduledAt] = useState('')
  const [publications, setPublications] = useState<PostPublication[]>([])
  const [retryingPlatform, setRetryingPlatform] = useState<string | null>(null)
  const [activeSlideIndex, setActiveSlideIndex] = useState(0)
  const publishingRef = useRef(false)

  // Modal açıldığında /posts/{id} ile güncel publications'ı çek
  useEffect(() => {
    if (!open || !post) { setPublications([]); setActiveSlideIndex(0); return }
    let cancelled = false
    api.get<Post>(`/posts/${post.id}`).then((res) => {
      if (!cancelled && res.success && res.data?.publications) {
        setPublications(res.data.publications)
      }
    })
    return () => { cancelled = true }
  }, [open, post])

  if (!post) return null

  const imageUrl = post.output_url ?? post.thumbnail_url
  const canAct = ['ready', 'failed', 'rejected'].includes(post.status)

  // datetime-local min: now + 5 minutes
  const minDateTime = new Date(Date.now() + 5 * 60 * 1000)
    .toISOString()
    .slice(0, 16)

  async function handlePublish() {
    if (publishingRef.current) return
    publishingRef.current = true
    setPublishing(true)
    try {
      const res = await api.post(`/posts/${post!.id}/publish`, {})
      if (res.success) {
        toast.success('İçerik yayınlanıyor')
        onPublished(post!.id)
        onClose()
      } else {
        toast.error(res.error ?? 'Yayınlama başarısız')
      }
    } finally {
      setPublishing(false)
      publishingRef.current = false
    }
  }

  async function handleRequestApproval() {
    setRequesting(true)
    const res = await api.post(`/posts/${post!.id}/request-approval`, {})
    setRequesting(false)
    if (res.success) {
      toast.success('Telegram\'a onay isteği gönderildi')
      onApprovalRequested(post!.id)
      onClose()
    } else {
      toast.error(res.error ?? 'Onay isteği gönderilemedi')
    }
  }

  async function handleRegenerate() {
    setRegenerating(true)
    const res = await api.post(`/posts/${post!.id}/regenerate`, {})
    setRegenerating(false)
    if (res.success) {
      toast.success('Yeniden üretim başlatıldı')
      onRegenerated(post!.id)
      onClose()
    } else {
      toast.error(res.error ?? 'Yeniden üretim başlatılamadı')
    }
  }

  async function handleRetryPlatform(platform: string) {
    if (retryingPlatform) return
    setRetryingPlatform(platform)
    const res = await api.post(`/posts/${post!.id}/retry?platform=${platform}`, {})
    setRetryingPlatform(null)
    if (res.success) {
      toast.success(`${PLATFORM_LABEL[platform] ?? platform} için yeniden denendi`)
      // Publications'ı tekrar çek
      const fresh = await api.get<Post>(`/posts/${post!.id}`)
      if (fresh.success && fresh.data?.publications) {
        setPublications(fresh.data.publications)
      }
    } else {
      toast.error(res.error ?? 'Yeniden deneme başarısız')
    }
  }

  async function handleSchedule() {
    if (!scheduledAt) return
    setScheduling(true)
    const res = await api.patch(`/calendar/schedule/${post!.id}`, {
      scheduled_at: new Date(scheduledAt).toISOString(),
    })
    setScheduling(false)
    if (res.success) {
      toast.success('İçerik zamanlandı')
      onScheduled(post!.id)
      onClose()
    } else {
      toast.error(res.error ?? 'Zamanlama başarısız')
    }
  }

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-base">İçerik Detayı</DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-2 gap-4">
          {/* Preview */}
          <div className="rounded-xl overflow-hidden bg-gray-50 border border-gray-100">
            {post.content_type === 'carousel' && post.slides && post.slides.length > 0 ? (() => {
              const sorted = [...post.slides].sort((a, b) => a.order - b.order)
              const current = sorted[activeSlideIndex] ?? sorted[0]
              return (
                <div className="flex flex-col">
                  {/* Big preview */}
                  <div className="relative bg-gray-100">
                    {current?.image_url ? (
                      <Image
                        src={current.image_url}
                        alt={`Slide ${current.order}`}
                        width={400}
                        height={400}
                        className="w-full object-contain aspect-square"
                      />
                    ) : (
                      <div className="w-full aspect-square flex items-center justify-center">
                        <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
                      </div>
                    )}
                    {/* Slide counter */}
                    <span className="absolute top-2 left-2 bg-black/60 text-white text-[10px] font-semibold px-2 py-0.5 rounded">
                      {activeSlideIndex + 1} / {sorted.length}
                    </span>
                    {/* Download current slide */}
                    {current?.image_url && (
                      <button
                        title="Bu slide'ı indir"
                        className="absolute top-2 right-2 bg-black/60 hover:bg-black/80 text-white p-1.5 rounded transition-colors"
                        onClick={(e) => { e.stopPropagation(); window.open(current.image_url!, '_blank') }}
                      >
                        <Download className="w-3.5 h-3.5" />
                      </button>
                    )}
                    {/* Nav arrows */}
                    {sorted.length > 1 && (
                      <>
                        <button
                          className="absolute left-1 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white rounded-full p-1 transition-colors"
                          onClick={(e) => { e.stopPropagation(); setActiveSlideIndex((i) => (i - 1 + sorted.length) % sorted.length) }}
                        >
                          <ChevronLeft className="w-4 h-4" />
                        </button>
                        <button
                          className="absolute right-1 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white rounded-full p-1 transition-colors"
                          onClick={(e) => { e.stopPropagation(); setActiveSlideIndex((i) => (i + 1) % sorted.length) }}
                        >
                          <ChevronRight className="w-4 h-4" />
                        </button>
                      </>
                    )}
                  </div>
                  {/* Thumbnail strip */}
                  <div className="flex gap-1 p-1.5 overflow-x-auto">
                    {sorted.map((slide, idx) => (
                      <button
                        key={slide.order}
                        className={cn(
                          'relative flex-shrink-0 w-12 h-12 rounded overflow-hidden border-2 transition-colors',
                          idx === activeSlideIndex ? 'border-blue-500' : 'border-transparent hover:border-gray-300'
                        )}
                        onClick={(e) => { e.stopPropagation(); setActiveSlideIndex(idx) }}
                      >
                        {slide.image_url ? (
                          <Image src={slide.image_url} alt={`Slide ${slide.order}`} width={48} height={48} className="w-full h-full object-cover" />
                        ) : (
                          <div className="w-full h-full bg-gray-200 flex items-center justify-center">
                            <Loader2 className="w-3 h-3 text-blue-400 animate-spin" />
                          </div>
                        )}
                        <span className="absolute bottom-0 right-0 bg-black/60 text-white text-[8px] font-bold px-1 rounded-tl">
                          {slide.order}
                        </span>
                      </button>
                    ))}
                  </div>
                </div>
              )
            })() : imageUrl ? (
              <Image
                src={imageUrl}
                alt="İçerik önizleme"
                width={400}
                height={400}
                className="w-full object-contain"
              />
            ) : (
              <div className="flex items-center justify-center h-48">
                {post.status === 'generating' ? (
                  <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
                ) : (
                  <span className="text-gray-300 text-sm">Görsel yok</span>
                )}
              </div>
            )}
          </div>

          {/* Details */}
          <div className="space-y-3">
            <div>
              <p className="text-xs text-gray-400 mb-1">Durum</p>
              <Badge variant="secondary">{STATUS_LABEL[post.status] ?? post.status}</Badge>
            </div>

            <div>
              <p className="text-xs text-gray-400 mb-1">Tip</p>
              <p className="text-sm text-gray-700 capitalize">{post.content_type}</p>
            </div>

            {post.caption && (
              <div>
                <p className="text-xs text-gray-400 mb-1">Açıklama</p>
                <p className="text-sm text-gray-700 leading-relaxed line-clamp-4">{post.caption}</p>
              </div>
            )}

            {post.hashtags && post.hashtags.length > 0 && (
              <div>
                <p className="text-xs text-gray-400 mb-1">Hashtagler</p>
                <div className="flex flex-wrap gap-1">
                  {post.hashtags.map((h) => (
                    <Badge key={h} variant="secondary" className="text-xs">{h}</Badge>
                  ))}
                </div>
              </div>
            )}

            {post.platforms && post.platforms.length > 0 && (
              <div>
                <p className="text-xs text-gray-400 mb-1">Platformlar</p>
                <div className="space-y-1.5">
                  {post.platforms.map((p) => {
                    const pub = publications.find((pb) => pb.platform === p)
                    const pubStatus = pub?.status ?? 'pending'
                    const color =
                      pubStatus === 'published' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                      pubStatus === 'failed'    ? 'bg-red-50 text-red-700 border-red-200' :
                      pubStatus === 'publishing' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                      'bg-gray-50 text-gray-600 border-gray-200'
                    const icon =
                      pubStatus === 'published' ? '✓' :
                      pubStatus === 'failed'    ? '✗' :
                      pubStatus === 'publishing' ? '⟳' : '○'
                    return (
                      <div
                        key={p}
                        className={cn('flex items-center justify-between gap-2 px-2 py-1 rounded-md border text-xs', color)}
                        title={pub?.error_message ?? ''}
                      >
                        <span className="flex items-center gap-1.5">
                          <span>{icon}</span>
                          {PLATFORM_LABEL[p] ?? p}
                        </span>
                        {pubStatus === 'failed' && (
                          <button
                            onClick={() => handleRetryPlatform(p)}
                            disabled={retryingPlatform === p}
                            className="text-[10px] px-1.5 py-0.5 rounded bg-red-100 hover:bg-red-200 text-red-700 disabled:opacity-50"
                          >
                            {retryingPlatform === p ? '...' : 'Yeniden Dene'}
                          </button>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            <div>
              <p className="text-xs text-gray-400 mb-1">Oluşturulma</p>
              <p className="text-sm text-gray-700">
                {new Date(post.created_at).toLocaleString('tr-TR')}
              </p>
            </div>
          </div>
        </div>

        {/* Schedule picker */}
        {showSchedulePicker && (
          <div className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg border border-gray-200">
            <input
              type="datetime-local"
              min={minDateTime}
              value={scheduledAt}
              onChange={(e) => setScheduledAt(e.target.value)}
              className="flex-1 text-sm border border-gray-200 rounded-md px-2 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <Button
              size="sm"
              disabled={!scheduledAt || scheduling}
              onClick={handleSchedule}
            >
              {scheduling ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Zamanla'}
            </Button>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setShowSchedulePicker(false)}
            >
              <X className="w-3.5 h-3.5" />
            </Button>
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-col gap-2 pt-2 border-t border-gray-100">
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              className="flex-1 gap-1.5"
              disabled={!canAct || regenerating}
              onClick={handleRegenerate}
            >
              {regenerating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RefreshCw className="w-3.5 h-3.5" />}
              Yeniden Üret
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="flex-1 gap-1.5"
              disabled={!canAct}
              onClick={() => setShowSchedulePicker((v) => !v)}
            >
              <Calendar className="w-3.5 h-3.5" /> Zamanla
            </Button>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              className="flex-1 gap-1.5"
              disabled={!canAct || requesting}
              onClick={handleRequestApproval}
            >
              {requesting ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Bell className="w-3.5 h-3.5" />}
              Onay İste
            </Button>
            <Button
              size="sm"
              className="flex-1 gap-1.5"
              disabled={!canAct || publishing}
              onClick={handlePublish}
            >
              {publishing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Send className="w-3.5 h-3.5" />}
              Şimdi Yayınla
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

// ─── Filter sheet ─────────────────────────────────────────────────────────────

function FilterSheet({
  filters,
  onChange,
}: {
  filters: Filters
  onChange: (f: Filters) => void
}) {
  const [local, setLocal] = useState<Filters>(filters)

  function apply() {
    onChange(local)
  }

  function reset() {
    const empty: Filters = { contentType: null, status: null, platform: null }
    setLocal(empty)
    onChange(empty)
  }

  const activeCount = [filters.contentType, filters.status, filters.platform].filter(Boolean).length

  return (
    <Sheet>
      <SheetTrigger className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
        <SlidersHorizontal className="w-4 h-4" />
        Filtrele
        {activeCount > 0 && (
          <span className="w-4 h-4 rounded-full bg-blue-600 text-white text-[10px] flex items-center justify-center">
            {activeCount}
          </span>
        )}
      </SheetTrigger>
      <SheetContent side="right" className="w-[400px]">
        <SheetHeader>
          <SheetTitle>Filtreler</SheetTitle>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          {/* Content type */}
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-700">İçerik Tipi</p>
            <div className="flex flex-wrap gap-2">
              {['image', 'carousel', 'video'].map((t) => (
                <button
                  key={t}
                  onClick={() => setLocal((p) => ({ ...p, contentType: p.contentType === t ? null : t }))}
                  className={cn(
                    'px-3 py-1.5 rounded-lg text-sm border transition-colors',
                    local.contentType === t
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'border-gray-200 text-gray-600 hover:border-blue-300'
                  )}
                >
                  {t === 'image' ? 'Görsel' : t === 'carousel' ? 'Carousel' : 'Video'}
                </button>
              ))}
            </div>
          </div>

          {/* Status */}
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-700">Durum</p>
            <div className="flex flex-wrap gap-2">
              {STATUS_OPTIONS.map((s) => (
                <button
                  key={s.id}
                  onClick={() => setLocal((p) => ({ ...p, status: p.status === s.id ? null : s.id }))}
                  className={cn(
                    'px-3 py-1.5 rounded-lg text-sm border transition-colors',
                    local.status === s.id
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'border-gray-200 text-gray-600 hover:border-blue-300'
                  )}
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>

          {/* Platform */}
          <div className="space-y-2">
            <p className="text-sm font-medium text-gray-700">Platform</p>
            <div className="flex flex-wrap gap-2">
              {PLATFORM_OPTIONS.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setLocal((prev) => ({ ...prev, platform: prev.platform === p.id ? null : p.id }))}
                  className={cn(
                    'px-3 py-1.5 rounded-lg text-sm border transition-colors',
                    local.platform === p.id
                      ? 'bg-blue-600 text-white border-blue-600'
                      : 'border-gray-200 text-gray-600 hover:border-blue-300'
                  )}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="absolute bottom-6 left-6 right-6 flex gap-3">
          <Button variant="outline" className="flex-1" onClick={reset}>Sıfırla</Button>
          <Button className="flex-1" onClick={apply}>Uygula</Button>
        </div>
      </SheetContent>
    </Sheet>
  )
}

// ─── Main page ─────────────────────────────────────────────────────────────────

export default function IcerikKutuphanesPage() {
  const currentBrand = useAppStore((s) => s.currentBrand)

  const [posts, setPosts] = useState<Post[]>([])
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)
  const [loading, setLoading] = useState(false)
  const [initialLoading, setInitialLoading] = useState(true)

  const [activeTab, setActiveTab] = useState<string | null>(null)
  const [filters, setFilters] = useState<Filters>({ contentType: null, status: null, platform: null })

  const [selectedPost, setSelectedPost] = useState<Post | null>(null)
  const [modalOpen, setModalOpen] = useState(false)

  const sentinelRef = useRef<HTMLDivElement>(null)
  const observerRef = useRef<IntersectionObserver | null>(null)

  // ── Data fetching ───────────────────────────────────────────────────────────

  const fetchPosts = useCallback(async (pageNum: number, reset = false) => {
    if (!currentBrand?.id) { setInitialLoading(false); return }

    setLoading(true)
    const params = new URLSearchParams({
      brand_id: currentBrand.id,
      page: String(pageNum),
      limit: '20',
    })
    const contentTypeFilter = activeTab ?? filters.contentType
    if (contentTypeFilter) params.set('content_type', contentTypeFilter)
    if (filters.status) params.set('status', filters.status)
    if (filters.platform) params.set('platform', filters.platform)

    const res = await api.get<{ items: Post[]; total: number; page: number; pages: number }>(
      `/posts?${params}`
    )

    if (res.success && res.data) {
      const { items, pages } = res.data
      setPosts((prev) => reset ? items : [...prev, ...items])
      setHasMore(pageNum < pages)
    }
    setLoading(false)
    setInitialLoading(false)
  }, [currentBrand?.id, activeTab, filters])

  // Reset and reload on filter/tab change
  useEffect(() => {
    setPage(1)
    setPosts([])
    setHasMore(true)
    setInitialLoading(true)
    fetchPosts(1, true)
  }, [currentBrand?.id, activeTab, filters]) // eslint-disable-line react-hooks/exhaustive-deps

  // Generating olan postlar için polling — output_url gelince otomatik güncelle
  useEffect(() => {
    const generatingIds = posts
      .filter((p) => p.status === 'generating' && !p.output_url)
      .map((p) => p.id)
    if (generatingIds.length === 0) return

    const interval = setInterval(async () => {
      const updates = await Promise.all(
        generatingIds.map((id) => api.get<Post>(`/posts/${id}`))
      )
      let changed = false
      updates.forEach((res) => {
        if (res.success && res.data?.output_url) {
          setPosts((prev) =>
            prev.map((p) => (p.id === res.data!.id ? { ...p, ...res.data } : p))
          )
          changed = true
        }
      })
      if (changed) clearInterval(interval)
    }, 3000)

    return () => clearInterval(interval)
  }, [posts])

  // Infinite scroll with IntersectionObserver
  useEffect(() => {
    if (observerRef.current) observerRef.current.disconnect()

    observerRef.current = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && hasMore && !loading) {
        const nextPage = page + 1
        setPage(nextPage)
        fetchPosts(nextPage)
      }
    }, { threshold: 0.1 })

    if (sentinelRef.current) observerRef.current.observe(sentinelRef.current)
    return () => observerRef.current?.disconnect()
  }, [hasMore, loading, page, fetchPosts])

  function handleCardClick(post: Post) {
    setSelectedPost(post)
    setModalOpen(true)
  }

  function handleFiltersChange(f: Filters) {
    setFilters(f)
  }

  function handlePublished(postId: string) {
    setPosts((prev) => prev.map((p) => p.id === postId ? { ...p, status: 'published' } : p))
  }

  function handleApprovalRequested(postId: string) {
    setPosts((prev) => prev.map((p) => p.id === postId ? { ...p, status: 'reviewing' } : p))
  }

  function handleRegenerated(postId: string) {
    setPosts((prev) => prev.map((p) => p.id === postId ? { ...p, status: 'generating', output_url: null } : p))
  }

  function handleScheduled(postId: string) {
    setPosts((prev) => prev.map((p) => p.id === postId ? { ...p, status: 'scheduled' } : p))
  }

  const publishInFlightRef = useRef<Set<string>>(new Set())

  async function handlePublishFromCard(post: Post) {
    if (publishInFlightRef.current.has(post.id)) return
    publishInFlightRef.current.add(post.id)
    try {
      const res = await api.post(`/posts/${post.id}/publish`, {})
      if (res.success) {
        toast.success('İçerik yayınlanıyor')
        handlePublished(post.id)
      } else {
        toast.error(res.error ?? 'Yayınlama başarısız')
      }
    } finally {
      publishInFlightRef.current.delete(post.id)
    }
  }

  const activeFilterCount = [filters.status, filters.platform].filter(Boolean).length

  // ── Render ──────────────────────────────────────────────────────────────────

  return (
    <div className="flex flex-col h-full">
      {/* Top bar */}
      <div className="flex items-center justify-between px-8 py-5 border-b border-gray-100 bg-white">
        <div className="flex items-center gap-1">
          {CONTENT_TYPE_TABS.map((tab) => (
            <button
              key={String(tab.id)}
              onClick={() => setActiveTab(tab.id)}
              className={cn(
                'px-4 py-1.5 rounded-lg text-sm font-medium transition-colors',
                activeTab === tab.id
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-500 hover:text-gray-800 hover:bg-gray-100'
              )}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2">
          {activeFilterCount > 0 && (
            <button
              onClick={() => setFilters({ contentType: null, status: null, platform: null })}
              className="text-xs text-gray-400 hover:text-gray-600 flex items-center gap-1"
            >
              <X className="w-3 h-3" /> Filtreleri temizle
            </button>
          )}
          <FilterSheet filters={filters} onChange={handleFiltersChange} />
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-8">
        {initialLoading ? (
          <div className="flex items-center justify-center h-48">
            <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
          </div>
        ) : posts.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-64 gap-3">
            <span className="text-4xl">📭</span>
            <p className="text-gray-500 font-medium">Henüz içerik yok</p>
            <p className="text-sm text-gray-400">İçerik Oluştur sayfasından ilk içeriğinizi üretin.</p>
          </div>
        ) : (
          <>
            {/* Masonry grid — CSS columns */}
            <div className="columns-3 gap-4 [column-fill:balance]">
              {posts.map((post) => (
                <div key={post.id} className="break-inside-avoid mb-4">
                  <ContentCard
                    post={post}
                    onClick={handleCardClick}
                    onPublish={handlePublishFromCard}
                    showWatermark={false}
                  />
                </div>
              ))}
            </div>

            {/* Infinite scroll sentinel */}
            <div ref={sentinelRef} className="h-8 flex items-center justify-center mt-4">
              {loading && !initialLoading && (
                <Loader2 className="w-5 h-5 animate-spin text-blue-400" />
              )}
              {!hasMore && posts.length > 0 && (
                <p className="text-xs text-gray-300">Tüm içerikler yüklendi</p>
              )}
            </div>
          </>
        )}
      </div>

      {/* Post detail modal */}
      <PostDetailModal
        post={selectedPost}
        open={modalOpen}
        onClose={() => { setModalOpen(false); setSelectedPost(null) }}
        onPublished={handlePublished}
        onApprovalRequested={handleApprovalRequested}
        onRegenerated={handleRegenerated}
        onScheduled={handleScheduled}
      />
    </div>
  )
}
