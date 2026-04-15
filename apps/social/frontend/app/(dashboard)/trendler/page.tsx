'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useState } from 'react'
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

  // Personal (Layer B)
  const [personalTrends, setPersonalTrends] = useState<Trend[]>([])
  const [personalQuota, setPersonalQuota] = useState<Quota | null>(null)
  const [personalLoading, setPersonalLoading] = useState(false)
  const [personalRan, setPersonalRan] = useState(false)

  // Monthly Report (Layer C)
  const [reports, setReports] = useState<SectorReport[]>([])
  const [reportsLoading, setReportsLoading] = useState(false)
  const [generatingReport, setGeneratingReport] = useState(false)

  // ─── Layer A — Sektör ───────────────────────────────────────────────────
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

  // ─── Layer B — Kişisel ─────────────────────────────────────────────────
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
        toast.success(`${res.data.trends.length} kişisel trend bulundu`)
      } else if (res.error === 'quota_exceeded' && res.plan_limit) {
        toast.error(res.plan_limit.message)
      } else {
        toast.error(res.error || 'Kişisel trend aranamadı')
      }
    } catch {
      toast.error('Kişisel trend hatası')
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
        // 2 saniye sonra listeyi yenile
        setTimeout(() => loadReports(), 2000)
      } else if (res.error === 'quota_exceeded' && res.plan_limit) {
        toast.error(res.plan_limit.message)
      } else if (res.error === 'plan_locked') {
        toast.error('Bu özellik Pro ve üzeri planlara özeldir.')
        router.push('/fiyatlandirma')
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
  function handleCreatePost(trend: Trend, _index: number) {
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
    if (activeTab === 'monthly') loadReports()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentBrand?.id, activeTab])

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
    { key: 'sector', label: 'Sektör Trendleri', icon: TrendingUp, desc: '6 saatte bir güncellenir · ücretsiz' },
    { key: 'personal', label: 'Kişisel Arama', icon: Sparkles, desc: 'Markanıza özel canlı arama · aylık kota' },
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
          <div className="flex items-center justify-between mb-4">
            {sector && (
              <p className="text-gray-500 text-sm">
                <span className="font-medium capitalize">{sector}</span> sektörü · 6 saatlik önbellek
              </p>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={refreshing}
              className="gap-2"
            >
              {refreshing ? <Loader2 className="w-4 h-4 animate-spin" /> : <RefreshCw className="w-4 h-4" />}
              Yenile
            </Button>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
            </div>
          ) : trends.length === 0 ? (
            <Card>
              <CardContent className="py-16 text-center">
                <TrendingUp className="w-10 h-10 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">Henüz trend yok. &quot;Yenile&quot; ile taze veri çek.</p>
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
                  <h3 className="font-semibold text-gray-900 mb-1">Markanıza Özel Kişisel Arama</h3>
                  <p className="text-sm text-gray-600 mb-3">
                    Google araması + AI sentezi ile markanızın anahtar kelimelerine özel canlı trendler.
                    Sektör trendlerinin aksine, bu arama sadece sizin markanıza çalışır.
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
                    {personalRan ? 'Yeniden Ara' : 'Kişisel Trendleri Ara'}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {personalLoading ? (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-8 h-8 text-purple-500 animate-spin" />
            </div>
          ) : personalRan && personalTrends.length === 0 ? (
            <Card>
              <CardContent className="py-16 text-center">
                <Sparkles className="w-10 h-10 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">Kişisel trend bulunamadı.</p>
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
                    Sektöre özel kaynaklardan toplanan ham veriler Claude AI ile sentezlenir.
                    12 trend, içerik fırsatı önerileri ve prompt önerileri dahil PDF olarak üretilir.
                    Pro ve üzeri planlara özeldir.
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
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={loadReports}
                        className="gap-1.5 shrink-0"
                      >
                        <RefreshCw className="w-3.5 h-3.5" />
                        Yenile
                      </Button>
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
