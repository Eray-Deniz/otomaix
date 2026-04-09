'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useRef, useState, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from '@/components/ui/sheet'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { ContentCard, type Post } from '@/components/content/ContentCard'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { Loader2, SlidersHorizontal, X, Send, Calendar, RefreshCw } from 'lucide-react'
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

function PostDetailModal({ post, open, onClose }: { post: Post | null; open: boolean; onClose: () => void }) {
  if (!post) return null

  const imageUrl = post.output_url ?? post.thumbnail_url

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-base">İçerik Detayı</DialogTitle>
        </DialogHeader>

        <div className="grid grid-cols-2 gap-4">
          {/* Preview */}
          <div className="rounded-xl overflow-hidden bg-gray-50 border border-gray-100">
            {imageUrl ? (
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
              <Badge variant="secondary">{post.status}</Badge>
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
                <p className="text-sm text-gray-700">{post.platforms.join(', ')}</p>
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

        {/* Actions */}
        <div className="flex gap-2 pt-2 border-t border-gray-100">
          <Button variant="outline" size="sm" className="gap-1.5">
            <RefreshCw className="w-3.5 h-3.5" /> Yeniden Üret
          </Button>
          <Button variant="outline" size="sm" className="gap-1.5">
            <Calendar className="w-3.5 h-3.5" /> Zamanla
          </Button>
          <Button size="sm" className="gap-1.5 ml-auto">
            <Send className="w-3.5 h-3.5" /> Şimdi Yayınla
          </Button>
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
      />
    </div>
  )
}
