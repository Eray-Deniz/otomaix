'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useState } from 'react'
import { useAppStore } from '@/lib/store'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { api } from '@/lib/api'
import Link from 'next/link'
import { TrendingUp, ArrowRight, Loader2, Wand2, Check } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'

function getGreeting(name: string) {
  const hour = new Date().getHours()
  if (hour < 12) return `Günaydın, ${name}!`
  if (hour < 18) return `İyi günler, ${name}!`
  return `İyi akşamlar, ${name}!`
}

function InstagramIcon() {
  return (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
      <circle cx="12" cy="12" r="4" />
      <circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none" />
    </svg>
  )
}

const PLATFORMS = [
  { key: 'instagram', name: 'Instagram', icon: InstagramIcon, color: 'text-pink-500', bg: 'bg-pink-50' },
  { key: 'tiktok', name: 'TikTok', icon: () => (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
      <path d="M19.59 6.69a4.83 4.83 0 01-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 01-2.88 2.5 2.89 2.89 0 01-2.89-2.89 2.89 2.89 0 012.89-2.89c.28 0 .54.04.79.1V9.01a6.33 6.33 0 00-.79-.05 6.34 6.34 0 00-6.34 6.34 6.34 6.34 0 006.34 6.34 6.34 6.34 0 006.33-6.34V9.05a8.19 8.19 0 004.79 1.53V7.14a4.85 4.85 0 01-1.02-.45z" />
    </svg>
  ), color: 'text-gray-900', bg: 'bg-gray-100' },
  { key: 'linkedin', name: 'LinkedIn', icon: () => (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
      <path d="M16 8a6 6 0 016 6v7h-4v-7a2 2 0 00-2-2 2 2 0 00-2 2v7h-4v-7a6 6 0 016-6zM2 9h4v12H2z"/>
      <circle cx="4" cy="4" r="2"/>
    </svg>
  ), color: 'text-blue-700', bg: 'bg-blue-50' },
  { key: 'pinterest', name: 'Pinterest', icon: () => (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0a12 12 0 00-4.37 23.17c-.1-.94-.2-2.4.04-3.44l1.4-5.96s-.36-.72-.36-1.78c0-1.67.97-2.92 2.17-2.92 1.02 0 1.52.77 1.52 1.7 0 1.03-.66 2.58-1 4.01-.28 1.2.6 2.17 1.78 2.17 2.13 0 3.77-2.25 3.77-5.5 0-2.87-2.06-4.88-5.01-4.88-3.41 0-5.42 2.56-5.42 5.2 0 1.03.4 2.13.89 2.73a.36.36 0 01.08.34l-.33 1.36c-.05.22-.18.27-.4.16-1.5-.7-2.43-2.9-2.43-4.67 0-3.8 2.76-7.3 7.96-7.3 4.17 0 7.42 2.98 7.42 6.95 0 4.15-2.61 7.49-6.24 7.49-1.22 0-2.37-.63-2.76-1.38l-.75 2.86c-.27 1.04-1 2.35-1.5 3.15A12 12 0 0012 0z"/>
    </svg>
  ), color: 'text-red-600', bg: 'bg-red-50' },
]

interface Trend {
  title: string
  source: string
  relevance_score: number
  content_opportunity: string
  suggested_prompt: string
}

function TrendWidget() {
  const currentBrand = useAppStore((s) => s.currentBrand)
  const router = useRouter()
  const [trends, setTrends] = useState<Trend[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!currentBrand?.id) return
    setLoading(true)
    api.get<{ sector: string; trends: Trend[] }>(`/trends?brand_id=${currentBrand.id}`)
      .then((res) => {
        if (res.success && res.data) setTrends((res.data.trends || []).slice(0, 5))
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [currentBrand?.id])

  function handleCreate(trend: Trend) {
    if (!currentBrand?.id) return
    const params = new URLSearchParams({
      prompt: trend.suggested_prompt,
      type: 'image',
      aspect: '1:1',
    })
    router.push(`/icerik-olustur?${params.toString()}`)
  }

  if (!currentBrand) return null

  return (
    <Card className="mb-6">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-semibold text-gray-800 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-blue-600" />
            Günün Sektör Trendleri
          </CardTitle>
          <Link
            href="/trendler"
            className="text-xs text-blue-600 hover:underline flex items-center gap-1"
          >
            Tüm Trendler <ArrowRight className="w-3 h-3" />
          </Link>
        </div>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex items-center justify-center py-6">
            <Loader2 className="w-5 h-5 text-blue-500 animate-spin" />
          </div>
        ) : trends.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-4">Trend verisi yükleniyor...</p>
        ) : (
          <div className="space-y-2">
            {trends.map((trend, i) => (
              <div
                key={i}
                className="flex items-center justify-between gap-3 p-2.5 rounded-lg hover:bg-gray-50 group transition-colors"
              >
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-800 truncate">{trend.title}</p>
                  <p className="text-xs text-gray-400 truncate">{trend.content_opportunity}</p>
                </div>
                <button
                  onClick={() => handleCreate(trend)}
                  className="shrink-0 flex items-center gap-1.5 text-xs font-medium text-blue-600 hover:text-blue-700 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Wand2 className="w-3.5 h-3.5" />
                  İçerik Üret
                </button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default function DashboardPage() {
  const user = useAppStore((s) => s.user)
  const currentBrand = useAppStore((s) => s.currentBrand)
  const displayName = user?.name?.split(' ')[0] || user?.email?.split('@')[0] || 'Kullanıcı'
  // getGreeting uses new Date() — must run client-side only to avoid SSR/hydration mismatch
  const [greeting, setGreeting] = useState('')
  useEffect(() => { setGreeting(getGreeting(displayName)) }, [displayName])

  const [connectedPlatforms, setConnectedPlatforms] = useState<string[]>([])
  const [connectingPlatform, setConnectingPlatform] = useState<string | null>(null)
  const [stats, setStats] = useState<{ generated_this_month: number; published_total: number }>({
    generated_this_month: 0,
    published_total: 0,
  })

  useEffect(() => {
    if (!currentBrand?.id) return
    api.get<{ platform: string }[]>(`/social/accounts?brand_id=${currentBrand.id}`).then((res) => {
      if (res.success && res.data) {
        setConnectedPlatforms(res.data.map((a) => a.platform))
      }
    })
    api.get<{ generated_this_month: number; published_total: number }>(
      `/posts/stats/summary?brand_id=${currentBrand.id}`
    ).then((res) => {
      if (res.success && res.data) setStats(res.data)
    })
  }, [currentBrand?.id])

  async function handleConnectPlatform(platformKey: string) {
    if (!currentBrand?.id) {
      toast.error('Önce bir marka seçin')
      return
    }
    setConnectingPlatform(platformKey)
    const res = await api.get<{ url: string }>(
      `/social/oauth-link?brand_id=${currentBrand.id}&platform=${platformKey}`
    )
    if (res.success && res.data?.url) {
      window.open(res.data.url, '_blank', 'noopener')
    } else {
      toast.error('OAuth bağlantısı alınamadı')
    }
    setConnectingPlatform(null)
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Greeting */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">{greeting || `Merhaba, ${displayName}!`}</h1>
        <p className="text-gray-500 text-sm mt-1">Bugün ne yayınlamak istersiniz?</p>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Bu Ay Üretilen
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-gray-900">{stats.generated_this_month}</p>
            <p className="text-xs text-gray-400 mt-1">içerik</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Yayınlanan
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-gray-900">{stats.published_total}</p>
            <p className="text-xs text-gray-400 mt-1">içerik</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-xs font-medium text-gray-500 uppercase tracking-wide">
              Bağlı Platform
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-gray-900">{connectedPlatforms.length}</p>
            <p className="text-xs text-gray-400 mt-1">platform</p>
          </CardContent>
        </Card>
      </div>

      {/* Trend Widget */}
      <TrendWidget />

      {/* Connect Accounts */}
      <div>
        <h2 className="text-sm font-semibold text-gray-800 mb-3">Hesabınızı Bağlayın</h2>
        <p className="text-sm text-gray-500 mb-4">
          Sosyal medya hesaplarınızı bağlayarak içeriklerinizi otomatik yayınlayın.
        </p>
        <div className="grid grid-cols-3 gap-4">
          {PLATFORMS.map((platform) => {
            const Icon = platform.icon
            const isConnected = connectedPlatforms.includes(platform.key)
            const isConnecting = connectingPlatform === platform.key
            return (
              <Card key={platform.key} className="hover:shadow-md transition-shadow">
                <CardContent className="pt-6">
                  <div className="flex flex-col items-center gap-3">
                    <div className={`w-12 h-12 ${platform.bg} rounded-xl flex items-center justify-center`}>
                      <span className={platform.color}>
                        <Icon />
                      </span>
                    </div>
                    <p className="text-sm font-medium text-gray-800">{platform.name}</p>
                    <Button
                      size="sm"
                      variant={isConnected ? 'secondary' : 'outline'}
                      className="w-full text-xs"
                      onClick={() => handleConnectPlatform(platform.key)}
                      disabled={isConnecting || !currentBrand?.id}
                    >
                      {isConnecting ? (
                        <Loader2 className="w-3 h-3 animate-spin" />
                      ) : isConnected ? (
                        <span className="flex items-center gap-1">
                          <Check className="w-3 h-3" /> Bağlı
                        </span>
                      ) : (
                        'Bağla'
                      )}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </div>
    </div>
  )
}
