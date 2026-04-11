'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  TrendingUp,
  RefreshCw,
  Wand2,
  Loader2,
  Newspaper,
  Search,
  Zap,
} from 'lucide-react'
import { useRouter } from 'next/navigation'

// ─── Types ──────────────────────────────────────────────────────────────────

interface Trend {
  title: string
  source: string
  relevance_score: number
  content_opportunity: string
  suggested_prompt: string
}

type SourceFilter = 'Tümü' | 'Haber' | 'Google Trends' | 'Genel'

// ─── Helpers ────────────────────────────────────────────────────────────────

function SourceIcon({ source }: { source: string }) {
  if (source === 'Google Trends')
    return <Search className="w-3.5 h-3.5" />
  if (source === 'Genel')
    return <Zap className="w-3.5 h-3.5" />
  return <Newspaper className="w-3.5 h-3.5" />
}

function relevanceColor(score: number) {
  if (score >= 85) return 'bg-green-100 text-green-700 border-green-200'
  if (score >= 70) return 'bg-yellow-100 text-yellow-700 border-yellow-200'
  return 'bg-gray-100 text-gray-600 border-gray-200'
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default function TrendlerPage() {
  const currentBrand = useAppStore((s) => s.currentBrand)
  const router = useRouter()

  const [trends, setTrends] = useState<Trend[]>([])
  const [sector, setSector] = useState('')
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [filter, setFilter] = useState<SourceFilter>('Tümü')
  const [creatingIndex, setCreatingIndex] = useState<number | null>(null)

  async function loadTrends() {
    if (!currentBrand?.id) return
    setLoading(true)
    try {
      const res = await api.get<{ sector: string; trends: Trend[] }>(
        `/trends?brand_id=${currentBrand.id}`
      )
      if (res.success && res.data) {
        setTrends(res.data.trends || [])
        setSector(res.data.sector || '')
      }
    } catch {
      toast.error('Trendler yüklenemedi')
    } finally {
      setLoading(false)
    }
  }

  async function handleRefresh() {
    if (!currentBrand?.id) return
    setRefreshing(true)
    try {
      const res = await api.post<{ sector: string; trends: Trend[] }>(
        `/trends/refresh?brand_id=${currentBrand.id}`,
        {}
      )
      if (res.success && res.data) {
        setTrends(res.data.trends || [])
        setSector(res.data.sector || '')
        toast.success('Trendler güncellendi')
      }
    } catch {
      toast.error('Güncelleme başarısız')
    } finally {
      setRefreshing(false)
    }
  }

  async function handleCreatePost(trend: Trend, index: number) {
    if (!currentBrand?.id) return
    setCreatingIndex(index)
    try {
      const res = await api.post<{ post_id: string }>(
        `/trends/${index}/create-post`,
        {
          brand_id: currentBrand.id,
          suggested_prompt: trend.suggested_prompt,
          content_type: 'image',
          aspect_ratio: '1:1',
          platforms: [],
        }
      )
      if (res.success && res.data?.post_id) {
        toast.success('İçerik oluşturuluyor...')
        router.push('/icerik-kutuphanesi')
      } else {
        toast.error('İçerik oluşturulamadı')
      }
    } catch {
      toast.error('Bir hata oluştu')
    } finally {
      setCreatingIndex(null)
    }
  }

  useEffect(() => {
    loadTrends()
  }, [currentBrand?.id])

  const FILTERS: SourceFilter[] = ['Tümü', 'Haber', 'Google Trends', 'Genel']

  const filtered =
    filter === 'Tümü'
      ? trends
      : trends.filter((t) => t.source === filter || t.source.includes(filter))

  if (!currentBrand) {
    return (
      <div className="p-8 flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <TrendingUp className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">Önce bir marka seçin.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-blue-600" />
            Trendler
          </h1>
          {sector && (
            <p className="text-gray-500 text-sm mt-1">
              <span className="font-medium capitalize">{sector}</span> sektöründeki güncel trendler
            </p>
          )}
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleRefresh}
          disabled={refreshing}
          className="gap-2"
        >
          {refreshing ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <RefreshCw className="w-4 h-4" />
          )}
          Yenile
        </Button>
      </div>

      {/* Filtreler */}
      <div className="flex gap-2 mb-6">
        {FILTERS.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium border transition-colors ${
              filter === f
                ? 'bg-blue-600 text-white border-blue-600'
                : 'bg-white text-gray-600 border-gray-200 hover:border-gray-300'
            }`}
          >
            {f}
          </button>
        ))}
      </div>

      {/* İçerik */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
        </div>
      ) : filtered.length === 0 ? (
        <Card>
          <CardContent className="py-16 text-center">
            <TrendingUp className="w-10 h-10 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">Bu filtre için trend bulunamadı.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {filtered.map((trend, i) => (
            <Card
              key={i}
              className="hover:shadow-md transition-shadow border-gray-200"
            >
              <CardContent className="p-5">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    {/* Başlık ve kaynak */}
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                      <h3 className="font-semibold text-gray-900 text-sm">{trend.title}</h3>
                      <span className="flex items-center gap-1 text-xs text-gray-400 bg-gray-50 border border-gray-100 px-2 py-0.5 rounded-full">
                        <SourceIcon source={trend.source} />
                        {trend.source}
                      </span>
                      <span
                        className={`text-xs font-medium px-2 py-0.5 rounded-full border ${relevanceColor(
                          trend.relevance_score
                        )}`}
                      >
                        %{trend.relevance_score} uyum
                      </span>
                    </div>

                    {/* İçerik fırsatı */}
                    <p className="text-sm text-gray-600 mb-3">
                      {trend.content_opportunity}
                    </p>

                    {/* Öneri prompt */}
                    <div className="bg-gray-50 border border-gray-100 rounded-lg px-3 py-2">
                      <p className="text-xs text-gray-400 mb-1 font-medium uppercase tracking-wide">
                        Önerilen Prompt
                      </p>
                      <p className="text-xs text-gray-600 leading-relaxed">
                        {trend.suggested_prompt}
                      </p>
                    </div>
                  </div>

                  {/* Aksiyon */}
                  <Button
                    size="sm"
                    onClick={() => handleCreatePost(trend, i)}
                    disabled={creatingIndex === i}
                    className="shrink-0 gap-1.5"
                  >
                    {creatingIndex === i ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Wand2 className="w-3.5 h-3.5" />
                    )}
                    İçerik Üret
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Bilgi notu */}
      {!loading && trends.length > 0 && (
        <p className="text-xs text-gray-400 text-center mt-6">
          Trendler 6 saatte bir güncellenir. Son güncelleme için "Yenile" butonunu kullanın.
        </p>
      )}
    </div>
  )
}
