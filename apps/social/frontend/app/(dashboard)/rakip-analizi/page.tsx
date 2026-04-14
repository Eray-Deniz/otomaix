'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { toast } from 'sonner'
import {
  Loader2, Plus, RefreshCw, Trash2, BarChart2,
  Globe, TrendingUp, Lightbulb,
} from 'lucide-react'

function InstagramIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
      <circle cx="12" cy="12" r="4" />
      <circle cx="17.5" cy="6.5" r="1" fill="currentColor" stroke="none" />
    </svg>
  )
}
import { cn } from '@/lib/utils'
import nextDynamic from 'next/dynamic'

// recharts sadece rakip-analizi sayfasında yüklensin — ayrı chunk
const CompetitorChart = nextDynamic(
  () => import('@/components/competitors/CompetitorChart').then((m) => ({ default: m.CompetitorChart })),
  { ssr: false, loading: () => <div className="h-[160px] animate-pulse bg-gray-100 rounded-lg" /> }
)

// ─── Types ────────────────────────────────────────────────────────────────────

type CompetitorStatus = 'analyzing' | 'ready' | 'failed'

interface Competitor {
  id: string
  brand_id: string
  competitor_name: string
  instagram_handle: string | null
  tiktok_handle: string | null
  website_url: string | null
  last_analyzed_at: string | null
  has_analysis: boolean
  status: CompetitorStatus
  error_message: string | null
  created_at: string
}

interface CompetitorAnalysis {
  id: string
  competitor_name: string
  analysis_data: {
    website?: {
      error?: string
      company_name?: string
      main_services?: string[]
      target_audience?: string
      content_themes?: string[]
      positioning?: string
      strengths?: string[]
      tone?: string
    }
    instagram?: {
      handle?: string
      source?: string
      note?: string
      followers?: number | null
      avg_likes?: number | null
      engagement_rate?: number | null
      posting_frequency_per_week?: number | null
      content_types?: { image?: number; video?: number; carousel?: number }
      top_hashtags?: string[]
    }
  } | null
}

interface CompetitorReport {
  summary: string
  opportunities: string[]
  content_gaps: string[]
  recommendations: string[]
}


// ─── Modal ────────────────────────────────────────────────────────────────────

function AddCompetitorModal({
  brandId,
  onClose,
  onAdded,
}: {
  brandId: string
  onClose: () => void
  onAdded: (c: Competitor) => void
}) {
  const [name, setName] = useState('')
  const [instagram, setInstagram] = useState('')
  const [website, setWebsite] = useState('')
  const [saving, setSaving] = useState(false)

  async function handleSubmit() {
    if (!name.trim()) { toast.error('Rakip adı zorunlu'); return }
    setSaving(true)
    const res = await api.post<Competitor>('/competitors', {
      brand_id: brandId,
      competitor_name: name.trim(),
      instagram_handle: instagram.trim() || null,
      website_url: website.trim() || null,
    })
    setSaving(false)
    if (res.success && res.data) {
      onAdded(res.data)
      toast.info(`"${name}" eklendi, analiz arka planda çalışıyor...`)
      onClose()
    } else {
      toast.error('Rakip eklenemedi')
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 p-6 space-y-4">
        <h2 className="text-lg font-bold text-gray-900">Rakip Ekle</h2>
        <p className="text-sm text-gray-500">
          Rakibin bilgilerini girin. Web sitesi ve/veya Instagram hesabı analiz edilecek.
        </p>

        <div className="space-y-1.5">
          <Label>Rakip Adı *</Label>
          <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="ABC Tekstil" />
        </div>

        <div className="space-y-1.5">
          <Label>Instagram Hesabı</Label>
          <Input
            value={instagram}
            onChange={(e) => setInstagram(e.target.value)}
            placeholder="@rakip_hesabi"
          />
        </div>

        <div className="space-y-1.5">
          <Label>Web Sitesi</Label>
          <Input
            value={website}
            onChange={(e) => setWebsite(e.target.value)}
            placeholder="https://rakip.com"
            type="url"
          />
        </div>

        <div className="flex gap-3 pt-2">
          <Button variant="outline" className="flex-1" onClick={onClose} disabled={saving}>
            İptal
          </Button>
          <Button className="flex-1 gap-2" onClick={handleSubmit} disabled={saving}>
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
            {saving ? 'Analiz Ediliyor...' : 'Ekle ve Analiz Et'}
          </Button>
        </div>
      </div>
    </div>
  )
}

// ─── Analiz detay paneli ──────────────────────────────────────────────────────

function AnalysisPanel({ competitor }: { competitor: CompetitorAnalysis }) {
  const data = competitor.analysis_data
  const web = data?.website
  const ig = data?.instagram

  const contentTypesData = ig?.content_types
    ? [
        { name: 'Görsel', value: ig.content_types.image ?? 0 },
        { name: 'Video', value: ig.content_types.video ?? 0 },
        { name: 'Carousel', value: ig.content_types.carousel ?? 0 },
      ].filter((d) => d.value > 0)
    : []

  return (
    <div className="space-y-6">
      {/* Instagram metrikleri */}
      {ig && (
        <div className="space-y-4">
          <h3 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
            <InstagramIcon className="w-4 h-4 text-pink-500" /> Instagram
            {ig.source === 'placeholder' && (
              <Badge variant="secondary" className="text-xs font-normal">Önizleme — Apify API gerekli</Badge>
            )}
          </h3>

          <div className="grid grid-cols-3 gap-3">
            {[
              { label: 'Takipçi', value: ig.followers?.toLocaleString('tr-TR') ?? '—' },
              { label: 'Ort. Beğeni', value: ig.avg_likes?.toLocaleString('tr-TR') ?? '—' },
              { label: 'Etkileşim', value: ig.engagement_rate ? `%${ig.engagement_rate}` : '—' },
            ].map((m) => (
              <div key={m.label} className="bg-pink-50 rounded-xl p-3 text-center">
                <p className="text-lg font-bold text-pink-700">{m.value}</p>
                <p className="text-xs text-pink-400">{m.label}</p>
              </div>
            ))}
          </div>

          <CompetitorChart data={contentTypesData} />

          {ig.top_hashtags && ig.top_hashtags.length > 0 && (
            <div>
              <p className="text-xs text-gray-500 mb-2">Popüler Hashtagler</p>
              <div className="flex flex-wrap gap-1.5">
                {ig.top_hashtags.map((tag) => (
                  <Badge key={tag} variant="secondary" className="text-xs">#{tag}</Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Website analizi */}
      {web && !web.error && (
        <div className="space-y-3">
          <h3 className="text-sm font-semibold text-gray-700 flex items-center gap-2">
            <Globe className="w-4 h-4 text-blue-500" /> Web Sitesi Analizi
          </h3>

          {web.positioning && (
            <div className="bg-blue-50 rounded-xl p-3">
              <p className="text-xs text-blue-500 mb-1">Konumlama</p>
              <p className="text-sm text-blue-800">{web.positioning}</p>
            </div>
          )}

          {web.strengths && web.strengths.length > 0 && (
            <div>
              <p className="text-xs text-gray-500 mb-1.5">Güçlü Yönler</p>
              <ul className="space-y-1">
                {web.strengths.map((s, i) => (
                  <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="text-green-500 mt-0.5">✓</span> {s}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {web.content_themes && web.content_themes.length > 0 && (
            <div>
              <p className="text-xs text-gray-500 mb-1.5">İçerik Temaları</p>
              <div className="flex flex-wrap gap-1.5">
                {web.content_themes.map((t) => (
                  <Badge key={t} variant="outline" className="text-xs">{t}</Badge>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {!ig && !web && (
        <p className="text-sm text-gray-400 text-center py-6">Henüz analiz verisi yok.</p>
      )}
    </div>
  )
}

// ─── Ana sayfa ────────────────────────────────────────────────────────────────

export default function RakipAnaliziPage() {
  const currentBrand = useAppStore((s) => s.currentBrand)

  const [competitors, setCompetitors] = useState<Competitor[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [selectedAnalysis, setSelectedAnalysis] = useState<CompetitorAnalysis | null>(null)
  const [loadingAnalysis, setLoadingAnalysis] = useState(false)
  const [refreshingId, setRefreshingId] = useState<string | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [report, setReport] = useState<CompetitorReport | null>(null)
  const [loadingReport, setLoadingReport] = useState(false)

  useEffect(() => {
    if (!currentBrand?.id) { setLoading(false); return }
    loadCompetitors()
  }, [currentBrand?.id]) // eslint-disable-line

  // Analiz tamamlanana kadar status='analyzing' olanları 4sn'de bir yokla
  useEffect(() => {
    const analyzingIds = competitors.filter((c) => c.status === 'analyzing').map((c) => c.id)
    if (analyzingIds.length === 0) return

    const intervalId = setInterval(async () => {
      await Promise.all(
        analyzingIds.map(async (id) => {
          const res = await api.get<CompetitorAnalysis & {
            status: CompetitorStatus
            error_message: string | null
            last_analyzed_at: string | null
          }>(`/competitors/${id}/analysis`)
          if (!res.success || !res.data) return
          const updated = res.data
          if (updated.status === 'analyzing') return

          setCompetitors((prev) =>
            prev.map((c) =>
              c.id === id
                ? {
                    ...c,
                    status: updated.status,
                    error_message: updated.error_message,
                    has_analysis: !!updated.analysis_data,
                    last_analyzed_at: updated.last_analyzed_at,
                  }
                : c
            )
          )
          if (updated.status === 'ready') {
            toast.success(`"${updated.competitor_name}" analizi tamamlandı`)
            if (selectedId === id) {
              setSelectedAnalysis({
                id: updated.id,
                competitor_name: updated.competitor_name,
                analysis_data: updated.analysis_data,
              })
            }
          } else if (updated.status === 'failed') {
            toast.error(
              `"${updated.competitor_name}" analizi başarısız: ${updated.error_message ?? 'bilinmeyen hata'}`
            )
          }
        })
      )
    }, 4000)

    return () => clearInterval(intervalId)
  }, [competitors, selectedId])

  async function loadCompetitors() {
    if (!currentBrand?.id) return
    setLoading(true)
    const res = await api.get<Competitor[]>(`/competitors?brand_id=${currentBrand.id}`)
    if (res.success && res.data) setCompetitors(res.data)
    setLoading(false)
  }

  async function handleViewAnalysis(id: string) {
    setSelectedId(id)
    setSelectedAnalysis(null)
    setLoadingAnalysis(true)
    const res = await api.get<CompetitorAnalysis>(`/competitors/${id}/analysis`)
    if (res.success && res.data) setSelectedAnalysis(res.data)
    setLoadingAnalysis(false)
  }

  async function handleRefresh(id: string) {
    setRefreshingId(id)
    const res = await api.post(`/competitors/${id}/refresh`, {})
    setRefreshingId(null)
    if (res.success) {
      toast.info('Analiz arka planda başlatıldı...')
      setCompetitors((prev) =>
        prev.map((c) => (c.id === id ? { ...c, status: 'analyzing', error_message: null } : c))
      )
      // Otomatik seç → polling tamamlanınca sağ panel kendiliğinden dolacak
      setSelectedId(id)
      setSelectedAnalysis(null)
    } else {
      toast.error('Analiz yenilenemedi')
    }
  }

  async function handleDelete(id: string, name: string) {
    if (!confirm(`"${name}" rakibini silmek istediğinize emin misiniz?`)) return
    setDeletingId(id)
    const res = await api.delete(`/competitors/${id}`)
    if (res.success) {
      setCompetitors((prev) => prev.filter((c) => c.id !== id))
      if (selectedId === id) { setSelectedId(null); setSelectedAnalysis(null) }
      toast.success('Rakip silindi')
    } else {
      toast.error('Silinemedi')
    }
    setDeletingId(null)
  }

  async function handleLoadReport() {
    if (!currentBrand?.id) return
    setLoadingReport(true)
    const res = await api.get<CompetitorReport>(`/competitors/report/summary?brand_id=${currentBrand.id}`)
    if (res.success && res.data) setReport(res.data)
    else toast.error('Rapor üretilemedi')
    setLoadingReport(false)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
      </div>
    )
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Rakip Analizi</h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Rakiplerinizi takip edin, fırsat ve içerik boşluklarını keşfedin
          </p>
        </div>
        <div className="flex gap-2">
          {competitors.length > 0 && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleLoadReport}
              disabled={loadingReport}
              className="gap-1.5"
            >
              {loadingReport
                ? <Loader2 className="w-4 h-4 animate-spin" />
                : <TrendingUp className="w-4 h-4" />
              }
              Özet Rapor
            </Button>
          )}
          <Button size="sm" onClick={() => setShowModal(true)} className="gap-1.5">
            <Plus className="w-4 h-4" /> Rakip Ekle
          </Button>
        </div>
      </div>

      {/* Özet rapor */}
      {report && (
        <div className="mb-6 p-5 bg-indigo-50 border border-indigo-200 rounded-2xl space-y-4">
          <div className="flex items-center gap-2">
            <Lightbulb className="w-5 h-5 text-indigo-600" />
            <h2 className="font-semibold text-indigo-800">AI Rekabet Raporu</h2>
          </div>
          <p className="text-sm text-indigo-700">{report.summary}</p>

          {report.opportunities.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-indigo-600 mb-1.5">Fırsatlar</p>
              <ul className="space-y-1">
                {report.opportunities.map((o, i) => (
                  <li key={i} className="text-sm text-indigo-800 flex items-start gap-2">
                    <span className="text-indigo-400 mt-0.5">→</span> {o}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {report.recommendations.length > 0 && (
            <div>
              <p className="text-xs font-semibold text-indigo-600 mb-1.5">Öneriler</p>
              <ul className="space-y-1">
                {report.recommendations.map((r, i) => (
                  <li key={i} className="text-sm text-indigo-800 flex items-start gap-2">
                    <span className="text-green-500 mt-0.5">✓</span> {r}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {competitors.length === 0 ? (
        /* Boş durum */
        <div className="flex flex-col items-center justify-center py-20 gap-4 text-center">
          <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center">
            <BarChart2 className="w-8 h-8 text-gray-400" />
          </div>
          <div>
            <p className="text-gray-700 font-medium">Henüz rakip eklenmedi</p>
            <p className="text-sm text-gray-400 mt-1">
              Rakiplerinizi ekleyin, AI web sitesi ve Instagram analizini otomatik yapar
            </p>
          </div>
          <Button onClick={() => setShowModal(true)} className="gap-2 mt-2">
            <Plus className="w-4 h-4" /> İlk Rakibi Ekle
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-6">
          {/* Sol — rakip listesi */}
          <div className="col-span-1 space-y-2">
            <p className="text-xs font-medium text-gray-500 uppercase tracking-wide px-1 mb-3">
              {competitors.length} Rakip
            </p>
            {competitors.map((c) => (
              <div
                key={c.id}
                className={cn(
                  'p-4 border rounded-xl cursor-pointer transition-all',
                  selectedId === c.id
                    ? 'border-blue-500 bg-blue-50 shadow-sm'
                    : 'border-gray-200 bg-white hover:border-blue-300 hover:bg-blue-50/30'
                )}
                onClick={() => handleViewAnalysis(c.id)}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0">
                    <p className="text-sm font-semibold text-gray-800 truncate">{c.competitor_name}</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {c.instagram_handle && (
                        <span className="text-[10px] text-pink-500 flex items-center gap-0.5">
                          <InstagramIcon className="w-2.5 h-2.5" /> {c.instagram_handle}
                        </span>
                      )}
                      {c.website_url && (
                        <span className="text-[10px] text-blue-500 flex items-center gap-0.5">
                          <Globe className="w-2.5 h-2.5" /> Web
                        </span>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-1 flex-shrink-0">
                    <button
                      onClick={(e) => { e.stopPropagation(); handleRefresh(c.id) }}
                      className="p-1 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded"
                      title="Analizi Yenile"
                      disabled={refreshingId === c.id}
                    >
                      {refreshingId === c.id
                        ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        : <RefreshCw className="w-3.5 h-3.5" />
                      }
                    </button>
                    <button
                      onClick={(e) => { e.stopPropagation(); handleDelete(c.id, c.competitor_name) }}
                      className="p-1 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded"
                      title="Sil"
                      disabled={deletingId === c.id}
                    >
                      {deletingId === c.id
                        ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                        : <Trash2 className="w-3.5 h-3.5" />
                      }
                    </button>
                  </div>
                </div>
                {c.last_analyzed_at && c.last_analyzed_at !== 'just_now' && (
                  <p className="text-[10px] text-gray-400 mt-2">
                    Son analiz: {new Date(c.last_analyzed_at).toLocaleDateString('tr-TR')}
                  </p>
                )}
                {c.status === 'analyzing' && (
                  <Badge variant="secondary" className="text-[10px] mt-2 gap-1">
                    <Loader2 className="w-2.5 h-2.5 animate-spin" />
                    Analiz ediliyor...
                  </Badge>
                )}
                {c.status === 'failed' && (
                  <Badge variant="destructive" className="text-[10px] mt-2" title={c.error_message ?? ''}>
                    Analiz başarısız
                  </Badge>
                )}
              </div>
            ))}
          </div>

          {/* Sağ — analiz detayı */}
          <div className="col-span-2">
            {(() => {
              const selectedCompetitor = competitors.find((c) => c.id === selectedId)
              if (!selectedId) {
                return (
                  <div className="flex flex-col items-center justify-center h-64 text-center gap-3 border-2 border-dashed border-gray-200 rounded-2xl">
                    <BarChart2 className="w-8 h-8 text-gray-300" />
                    <p className="text-sm text-gray-400">Sol taraftan bir rakip seçin</p>
                  </div>
                )
              }
              if (selectedCompetitor?.status === 'analyzing') {
                return (
                  <div className="flex flex-col items-center justify-center h-64 text-center gap-3 border-2 border-dashed border-blue-200 rounded-2xl bg-blue-50/30">
                    <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
                    <p className="text-sm text-blue-600 font-medium">Analiz yapılıyor...</p>
                    <p className="text-xs text-gray-500">Bu işlem 30-60 saniye sürebilir</p>
                  </div>
                )
              }
              if (selectedCompetitor?.status === 'failed') {
                return (
                  <div className="flex flex-col items-center justify-center h-64 text-center gap-3 border-2 border-dashed border-red-200 rounded-2xl bg-red-50/30">
                    <p className="text-sm text-red-600 font-medium">Analiz başarısız</p>
                    <p className="text-xs text-gray-500 max-w-md">{selectedCompetitor.error_message ?? 'Bilinmeyen hata'}</p>
                    <Button size="sm" variant="outline" onClick={() => handleRefresh(selectedId)}>Tekrar Dene</Button>
                  </div>
                )
              }
              if (loadingAnalysis) {
                return (
                  <div className="flex items-center justify-center h-64">
                    <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
                  </div>
                )
              }
              if (selectedAnalysis) {
                return (
              <div className="bg-white border border-gray-200 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-5">
                  <h2 className="font-bold text-gray-900">{selectedAnalysis.competitor_name}</h2>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleRefresh(selectedId)}
                    disabled={refreshingId === selectedId}
                    className="gap-1.5"
                  >
                    {refreshingId === selectedId
                      ? <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      : <RefreshCw className="w-3.5 h-3.5" />
                    }
                    Analizi Yenile
                  </Button>
                </div>
                <AnalysisPanel competitor={selectedAnalysis} />
              </div>
                )
              }
              return (
                <div className="flex flex-col items-center justify-center h-64 text-center gap-3">
                  <p className="text-sm text-gray-400">Analiz verisi yüklenemedi</p>
                </div>
              )
            })()}
          </div>
        </div>
      )}

      {/* Modal */}
      {showModal && currentBrand?.id && (
        <AddCompetitorModal
          brandId={currentBrand.id}
          onClose={() => setShowModal(false)}
          onAdded={(c) => setCompetitors((prev) => [c, ...prev])}
        />
      )}
    </div>
  )
}
