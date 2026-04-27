'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useRef, useState } from 'react'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import {
  TrendingUp,
  RefreshCw,
  Wand2,
  Loader2,
  Newspaper,
  Search,
  Zap,
  Sparkles,
  FileText,
  Download,
  Clock,
  CheckCircle2,
  XCircle,
} from 'lucide-react'
import { useRouter } from 'next/navigation'
import { analytics } from '@/lib/analytics'

// ─── Types ──────────────────────────────────────────────────────────────────

interface Trend {
  title: string
  source: string
  relevance_score: number
  content_opportunity: string
  suggested_prompt: string
  summary?: string
}

interface Quota {
  used: number
  limit: number
  remaining: number
  plan_id: string
}

interface SectorReport {
  id: string
  status: 'generating' | 'ready' | 'failed'
  pdf_url: string | null
  generated_at: string
  error_message: string | null
  apify_cost_usd: number | null
  claude_cost_usd: number | null
}

type TabKey = 'sector' | 'personal' | 'monthly'

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

function formatDateTR(iso: string) {
  try {
    return new Date(iso).toLocaleString('tr-TR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return iso
  }
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default function TrendlerPage() {
  const currentBrand = useAppStore((s) => s.currentBrand)
  const router = useRouter()

  const [activeTab, setActiveTab] = useState<TabKey>('sector')

  // Sector (Layer A)
  const [trends, setTrends] = useState<Trend[]>([])
  const [sector, setSector] = useState('')
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [sectorFetchedAt, setSectorFetchedAt] = useState<string | null>(null)

  // Personal (Layer B)
  const [personalTrends, setPersonalTrends] = useState<Trend[]>([])
  const [personalQuota, setPersonalQuota] = useState<Quota | null>(null)
  const [personalLoading, setPersonalLoading] = useState(false)
  const [personalRan, setPersonalRan] = useState(false)
  const [personalFetchedAt, setPersonalFetchedAt] = useState<string | null>(null)
  const [personalCacheLoading, setPersonalCacheLoading] = useState(false)

  // Monthly Report (Layer C)
  const [reports, setReports] = useState<SectorReport[]>([])
  const [reportsLoading, setReportsLoading] = useState(false)
  const [generatingReport, setGeneratingReport] = useState(false)
  const prevGeneratingIdsRef = useRef<Set<string>>(new Set())

  // ─── Layer A — Sektör ───────────────────────────────────────────────────
  async function loadTrends() {
    if (!currentBrand?.id) return
    setLoading(true)
    try {
      const res = await api.get<{ sector: string; trends: Trend[]; fetched_at: string | null }>(
        `/trends?brand_id=${currentBrand.id}`
      )
      if (res.success && res.data) {
        setTrends(res.data.trends || [])
        setSector(res.data.sector || '')
        setSectorFetchedAt(res.data.fetched_at || null)
        analytics.trendLayerAViewed(res.data.sector)
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
        setSectorFetchedAt(new Date().toISOString())
        toast.success('Trendler güncellendi')
      }
    } catch {
      toast.error('Güncelleme başarısız')
    } finally {
      setRefreshing(false)
    }
  }

  // ─── Layer B — Kişisel ─────────────────────────────────────────────────
  async function loadPersonalCache() {
    if (!currentBrand?.id) return
    setPersonalCacheLoading(true)
    try {
      const res = await api.get<{ trends: Trend[]; fetched_at: string | null }>(
        `/trends/personal?brand_id=${currentBrand.id}`
      )
      if (res.success && res.data && res.data.trends.length > 0) {
        setPersonalTrends(res.data.trends)
        setPersonalFetchedAt(res.data.fetched_at)
        setPersonalRan(true)
      }
    } catch {
      // sessiz — cache yoksa boş state gösterilir
    } finally {
      setPersonalCacheLoading(false)
    }
  }

  async function runPersonalSearch() {
    if (!currentBrand?.id) return
    setPersonalLoading(true)
    try {
      const res = await api.post<{
        trends: Trend[]
        queries: string[]
        raw_count: number
        quota: Quota
        cost_usd: number
      }>(`/trends/personal?brand_id=${currentBrand.id}`, {})
      if (res.success && res.data) {
        setPersonalTrends(res.data.trends || [])
        setPersonalQuota(res.data.quota)
        setPersonalRan(true)
        setPersonalFetchedAt(new Date().toISOString())
        toast.success(`${res.data.trends.length} kişisel trend bulundu`)
        analytics.trendLayerBTriggered(sector)
      } else if (res.plan_limit) {
        toast.error(res.plan_limit.message)
        analytics.trendQuotaExhausted('layer_b')
        analytics.trendPaywallShown('layer_b', res.plan_limit.current_plan)
      } else {
        toast.error(res.error || 'Marka trendi aranamadı')
      }
    } catch {
      toast.error('Marka trendi hatası')
    } finally {
      setPersonalLoading(false)
    }
  }

  // ─── Layer C — Aylık Rapor ─────────────────────────────────────────────
  async function loadReports() {
    if (!currentBrand?.id) return
    setReportsLoading(true)
    try {
      const res = await api.get<{ reports: SectorReport[] }>(
        `/trends/reports?brand_id=${currentBrand.id}`
      )
      if (res.success && res.data) {
        setReports(res.data.reports || [])
      }
    } catch {
      toast.error('Raporlar yüklenemedi')
    } finally {
      setReportsLoading(false)
    }
  }

  async function generateReport() {
    if (!currentBrand?.id) return
    setGeneratingReport(true)
    try {
      const res = await api.post<{ status: string; message: string; quota: Quota }>(
        `/trends/monthly-report?brand_id=${currentBrand.id}`,
        {}
      )
      if (res.success && res.data) {
        toast.success(res.data.message || 'Rapor üretiliyor')
        analytics.trendLayerCGenerated(sector)
        loadReports()
      } else if (res.plan_limit) {
        toast.error(res.plan_limit.message)
        analytics.trendQuotaExhausted('layer_c')
        analytics.trendPaywallShown('layer_c', res.plan_limit.current_plan)
        router.push(res.plan_limit.upgrade_url || '/fiyatlandirma')
      } else {
        toast.error(res.error || 'Rapor üretilemedi')
      }
    } catch {
      toast.error('Rapor üretim hatası')
    } finally {
      setGeneratingReport(false)
    }
  }

  // ─── Create post (trend → icerik-olustur wizard prefill) ───────────────
  function handleCreatePost(trend: Trend) {
    if (!currentBrand?.id) return
    analytics.trendPostCreated()
    const params = new URLSearchParams({
      prompt: trend.suggested_prompt,
      type: 'image',
      aspect: '1:1',
    })
    router.push(`/icerik-olustur?${params.toString()}`)
  }

  useEffect(() => {
    if (activeTab === 'sector') loadTrends()
    if (activeTab === 'personal') loadPersonalCache()
    if (activeTab === 'monthly') loadReports()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentBrand?.id, activeTab])

  // Layer C polling: "generating" rapor varsa 5sn'de bir kontrol et
  useEffect(() => {
    const generatingIds = new Set(
      reports.filter((r) => r.status === 'generating').map((r) => r.id)
    )

    // Durum geçişi: generating → ready/failed olan raporlar için toast göster
    for (const prevId of Array.from(prevGeneratingIdsRef.current)) {
      if (!generatingIds.has(prevId)) {
        const report = reports.find((r) => r.id === prevId)
        if (report?.status === 'ready') {
          toast.success('Rapor hazır! PDF indirilebilir.')
        } else if (report?.status === 'failed') {
          toast.error(report.error_message || 'Rapor üretimi başarısız oldu.')
        }
      }
    }
    prevGeneratingIdsRef.current = generatingIds

    if (generatingIds.size === 0 || activeTab !== 'monthly') return

    const interval = setInterval(() => {
      loadReports()
    }, 5000)

    return () => clearInterval(interval)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reports, activeTab])

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

  const TABS: { key: TabKey; label: string; icon: typeof TrendingUp; desc: string }[] = [
    { key: 'sector', label: 'Sektör Trendleri', icon: TrendingUp, desc: 'Sektörünüze özel trend analizi · ücretsiz' },
    { key: 'personal', label: 'Marka Trendleri', icon: Sparkles, desc: 'Markanıza özel canlı arama · aylık kota' },
    { key: 'monthly', label: 'Aylık Rapor', icon: FileText, desc: 'Pro+ · detaylı PDF rapor' },
  ]

  return (
    <div className="p-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-blue-600" />
          Trendler
        </h1>
        <p className="text-gray-500 text-sm mt-1">
          {currentBrand.name} için trend analizi
        </p>
      </div>

      {/* Tab switcher */}
      <div className="flex gap-2 mb-6 border-b border-gray-200">
        {TABS.map((tab) => {
          const Icon = tab.icon
          const active = activeTab === tab.key
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 -mb-px transition-colors ${
                active
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          )
        })}
      </div>

      {/* ─── Tab: Sektör ──────────────────────────────────────────────── */}
      {activeTab === 'sector' && (
        <div>
          <Card className="mb-6 border-blue-100 bg-gradient-to-br from-blue-50 to-white">
            <CardContent className="p-5">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center shrink-0">
                  <TrendingUp className="w-5 h-5 text-blue-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">Sektör Trendleri</h3>
                  <p className="text-sm text-gray-600 mb-3">
                    {sector ? (
                      <><span className="font-medium capitalize">{sector}</span> sektörüne özel trend analizi. Ücretsiz kaynaklar + AI sentezi ile sektörünüzdeki güncel trendleri keşfedin.</>
                    ) : (
                      <>Sektörünüze özel trend analizi. Ücretsiz kaynaklar + AI sentezi ile güncel trendleri keşfedin.</>
                    )}
                  </p>
                  <Button onClick={handleRefresh} disabled={refreshing} className="gap-2">
                    {refreshing ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Search className="w-4 h-4" />
                    )}
                    {trends.length > 0 ? 'Yeniden Ara' : 'Sektör Trendlerini Ara'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {sectorFetchedAt && trends.length > 0 && !refreshing && (
            <p className="text-xs text-gray-400 mb-3">
              Son arama: {formatDateTR(sectorFetchedAt)}
            </p>
          )}

          {loading || refreshing ? (
            <div className="flex flex-col items-center justify-center py-20 gap-3">
              <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
              {refreshing && (
                <p className="text-sm text-gray-500">Trendler analiz ediliyor, lütfen bekleyin...</p>
              )}
            </div>
          ) : trends.length === 0 ? (
            <Card>
              <CardContent className="py-16 text-center">
                <TrendingUp className="w-10 h-10 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">Henüz trend araması yapılmadı. Yukarıdaki butona tıklayarak sektör trendlerini keşfedin.</p>
              </CardContent>
            </Card>
          ) : (
            <TrendGrid trends={trends} onCreate={handleCreatePost} />
          )}
        </div>
      )}

      {/* ─── Tab: Kişisel ─────────────────────────────────────────────── */}
      {activeTab === 'personal' && (
        <div>
          <Card className="mb-6 border-purple-100 bg-gradient-to-br from-purple-50 to-white">
            <CardContent className="p-5">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center shrink-0">
                  <Sparkles className="w-5 h-5 text-purple-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">Marka Trendleri</h3>
                  <p className="text-sm text-gray-600 mb-3">
                    Google araması + AI sentezi ile markanızın anahtar kelimelerine özel canlı trendler.
                    Sektör trendlerinden farklı olarak, bu arama sadece sizin markanıza özel çalışır.
                  </p>
                  {personalQuota && (
                    <div className="flex items-center gap-3 text-xs text-gray-500 mb-3">
                      <span className="font-medium">
                        Kota: {personalQuota.used} / {personalQuota.limit} kullanıldı
                      </span>
                      <span className="text-gray-400">·</span>
                      <span className="capitalize">{personalQuota.plan_id} plan</span>
                    </div>
                  )}
                  <Button onClick={runPersonalSearch} disabled={personalLoading} className="gap-2">
                    {personalLoading ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Search className="w-4 h-4" />
                    )}
                    {personalRan ? 'Yeniden Ara' : 'Marka Trendlerini Ara'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {personalFetchedAt && personalTrends.length > 0 && !personalLoading && (
            <p className="text-xs text-gray-400 mb-3">
              Son arama: {formatDateTR(personalFetchedAt)}
            </p>
          )}

          {personalLoading || personalCacheLoading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
            </div>
          ) : personalRan && personalTrends.length === 0 ? (
            <Card>
              <CardContent className="py-16 text-center">
                <Sparkles className="w-10 h-10 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">Marka trendi bulunamadı.</p>
              </CardContent>
            </Card>
          ) : personalTrends.length > 0 ? (
            <TrendGrid trends={personalTrends} onCreate={handleCreatePost} />
          ) : null}
        </div>
      )}

      {/* ─── Tab: Aylık Rapor ─────────────────────────────────────────── */}
      {activeTab === 'monthly' && (
        <div>
          <Card className="mb-6 border-amber-100 bg-gradient-to-br from-amber-50 to-white">
            <CardContent className="p-5">
              <div className="flex items-start gap-4">
                <div className="w-10 h-10 rounded-lg bg-amber-100 flex items-center justify-center shrink-0">
                  <FileText className="w-5 h-5 text-amber-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">Aylık Sektör Trend Raporu</h3>
                  <p className="text-sm text-gray-600 mb-3">
                    Sektöre özel kaynaklardan toplanan ham veriler AI ile sentezlenir.
                    12 trend, içerik fırsatı önerileri ve prompt önerileri dahil PDF olarak üretilir.
                  </p>
                  <Button
                    onClick={generateReport}
                    disabled={generatingReport}
                    className="gap-2 bg-amber-600 hover:bg-amber-700"
                  >
                    {generatingReport ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <FileText className="w-4 h-4" />
                    )}
                    Yeni Rapor Üret
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
            Son Raporlar
          </h2>

          {reportsLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 text-amber-500 animate-spin" />
            </div>
          ) : reports.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <FileText className="w-10 h-10 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">Henüz rapor üretilmedi.</p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-3">
              {reports.map((r) => (
                <Card key={r.id}>
                  <CardContent className="p-4 flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center shrink-0">
                      {r.status === 'ready' && <CheckCircle2 className="w-5 h-5 text-green-600" />}
                      {r.status === 'generating' && <Clock className="w-5 h-5 text-amber-600 animate-pulse" />}
                      {r.status === 'failed' && <XCircle className="w-5 h-5 text-red-600" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-medium text-sm text-gray-900">
                          {formatDateTR(r.generated_at)}
                        </span>
                        <span
                          className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                            r.status === 'ready'
                              ? 'bg-green-100 text-green-700'
                              : r.status === 'generating'
                              ? 'bg-amber-100 text-amber-700'
                              : 'bg-red-100 text-red-700'
                          }`}
                        >
                          {r.status === 'ready' ? 'Hazır' : r.status === 'generating' ? 'Üretiliyor' : 'Başarısız'}
                        </span>
                      </div>
                      {r.status === 'failed' && r.error_message && (
                        <p className="text-xs text-red-600 truncate">{r.error_message}</p>
                      )}
                      {r.status === 'ready' && (r.apify_cost_usd || r.claude_cost_usd) && (
                        <p className="text-xs text-gray-400">
                          Maliyet: ${(Number(r.apify_cost_usd || 0) + Number(r.claude_cost_usd || 0)).toFixed(4)}
                        </p>
                      )}
                    </div>
                    {r.status === 'ready' && r.pdf_url && (
                      <a
                        href={r.pdf_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1.5 shrink-0 px-3 py-1.5 text-sm font-medium border border-gray-200 rounded-md hover:bg-gray-50 transition-colors"
                      >
                        <Download className="w-3.5 h-3.5" />
                        İndir
                      </a>
                    )}
                    {r.status === 'generating' && (
                      <span className="flex items-center gap-1.5 shrink-0 text-xs text-amber-600">
                        <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        Otomatik kontrol ediliyor...
                      </span>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

// ─── TrendGrid (shared between sector + personal tabs) ──────────────────────

function TrendGrid({
  trends,
  onCreate,
}: {
  trends: Trend[]
  onCreate: (t: Trend, i: number) => void
}) {
  return (
    <div className="grid gap-4">
      {trends.map((trend, i) => (
        <Card key={i} className="hover:shadow-md transition-shadow border-gray-200">
          <CardContent className="p-5">
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1 min-w-0">
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
                {trend.summary && (
                  <p className="text-xs text-gray-500 mb-2 italic">{trend.summary}</p>
                )}
                <p className="text-sm text-gray-600 mb-3">{trend.content_opportunity}</p>
                <div className="bg-gray-50 border border-gray-100 rounded-lg px-3 py-2">
                  <p className="text-xs text-gray-400 mb-1 font-medium uppercase tracking-wide">
                    Önerilen Prompt
                  </p>
                  <p className="text-xs text-gray-600 leading-relaxed">{trend.suggested_prompt}</p>
                </div>
              </div>
              <Button
                size="sm"
                onClick={() => onCreate(trend, i)}
                className="shrink-0 gap-1.5"
              >
                <Wand2 className="w-3.5 h-3.5" />
                İçerik Üret
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
