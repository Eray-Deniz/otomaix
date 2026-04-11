'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import { Suspense } from 'react'
import { api } from '@/lib/api'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import {
  CreditCard,
  Loader2,
  TrendingUp,
  Layers,
  ImageIcon,
  ExternalLink,
  CheckCircle,
} from 'lucide-react'
import Link from 'next/link'

// ─── Types ──────────────────────────────────────────────────────────────────

interface Subscription {
  id: string
  plan_id: string
  status: string
  current_period_end: string | null
}

interface PlanLimits {
  plan_id: string
  max_brands: number | null
  max_posts_per_month: number | null
  can_use_video: boolean
  can_use_avatar: boolean
}

interface BillingData {
  plan_id: string
  subscription: Subscription | null
  limits: PlanLimits
  usage: {
    posts_this_month: number
    brands: number
  }
  upgrade_url: string
}

const PLAN_LABELS: Record<string, string> = {
  free: 'Ücretsiz',
  starter: 'Starter',
  pro: 'Pro',
  business: 'Business',
  agency: 'Agency',
}

const STATUS_LABELS: Record<string, { label: string; color: string }> = {
  active:    { label: 'Aktif', color: 'bg-green-100 text-green-700' },
  trialing:  { label: 'Deneme', color: 'bg-blue-100 text-blue-700' },
  past_due:  { label: 'Ödeme Bekliyor', color: 'bg-yellow-100 text-yellow-700' },
  cancelled: { label: 'İptal Edildi', color: 'bg-red-100 text-red-700' },
}

function UsageBar({ used, max, label }: { used: number; max: number | null; label: string }) {
  const pct = max ? Math.min((used / max) * 100, 100) : 0
  const isUnlimited = max === null

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-600">{label}</span>
        <span className="font-medium text-gray-800">
          {isUnlimited ? `${used} / Sınırsız` : `${used} / ${max}`}
        </span>
      </div>
      {!isUnlimited && (
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${
              pct >= 90 ? 'bg-red-500' : pct >= 70 ? 'bg-yellow-500' : 'bg-blue-500'
            }`}
            style={{ width: `${pct}%` }}
          />
        </div>
      )}
    </div>
  )
}

// ─── Inner page (needs useSearchParams) ─────────────────────────────────────

function FaturalandirmaInner() {
  const searchParams = useSearchParams()
  const [billing, setBilling] = useState<BillingData | null>(null)
  const [loading, setLoading] = useState(true)
  const [portalLoading, setPortalLoading] = useState(false)

  useEffect(() => {
    if (searchParams.get('success') === '1') {
      toast.success('Aboneliğiniz başarıyla oluşturuldu!')
    }
  }, [])

  useEffect(() => {
    api.get<BillingData>('/billing/current').then((res) => {
      if (res.success && res.data) setBilling(res.data)
      setLoading(false)
    })
  }, [])

  async function handlePortal() {
    setPortalLoading(true)
    try {
      const res = await api.post<{ portal_url: string }>('/billing/portal', {})
      if (res.success && res.data?.portal_url) {
        window.open(res.data.portal_url, '_blank')
      } else {
        toast.error(res.error || 'Portal açılamadı')
      }
    } catch {
      toast.error('Bir hata oluştu')
    } finally {
      setPortalLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    )
  }

  if (!billing) {
    return (
      <div className="p-8 text-center">
        <p className="text-gray-500">Abonelik bilgisi yüklenemedi.</p>
      </div>
    )
  }

  const { plan_id, subscription, limits, usage } = billing
  const planLabel = PLAN_LABELS[plan_id] || plan_id
  const statusInfo = subscription
    ? STATUS_LABELS[subscription.status] || { label: subscription.status, color: 'bg-gray-100 text-gray-600' }
    : null

  const periodEnd = subscription?.current_period_end
    ? new Date(subscription.current_period_end).toLocaleDateString('tr-TR', {
        day: 'numeric', month: 'long', year: 'numeric',
      })
    : null

  return (
    <div className="p-8 max-w-3xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
        <CreditCard className="w-6 h-6 text-blue-600" />
        Faturalandırma
      </h1>

      {/* Mevcut plan kartı */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-semibold text-gray-600 uppercase tracking-wide">
            Mevcut Plan
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-white" />
              </div>
              <div>
                <p className="font-bold text-lg text-gray-900">{planLabel}</p>
                {periodEnd && (
                  <p className="text-xs text-gray-400">Yenileme: {periodEnd}</p>
                )}
              </div>
            </div>
            <div className="flex items-center gap-2">
              {statusInfo && (
                <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${statusInfo.color}`}>
                  {statusInfo.label}
                </span>
              )}
            </div>
          </div>

          <div className="flex gap-2 pt-1">
            <Link href="/fiyatlandirma">
              <Button size="sm" className="gap-1.5">
                <TrendingUp className="w-3.5 h-3.5" />
                Plan Yükselt
              </Button>
            </Link>
            {subscription && (
              <Button
                size="sm"
                variant="outline"
                onClick={handlePortal}
                disabled={portalLoading}
                className="gap-1.5"
              >
                {portalLoading ? (
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                ) : (
                  <ExternalLink className="w-3.5 h-3.5" />
                )}
                Faturalar & Yönetim
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Kullanım istatistikleri */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-semibold text-gray-600 uppercase tracking-wide">
            Bu Ay Kullanım
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <UsageBar
            used={usage.posts_this_month}
            max={limits.max_posts_per_month}
            label="İçerik Üretimi"
          />
          <UsageBar
            used={usage.brands}
            max={limits.max_brands}
            label="Aktif Marka"
          />
        </CardContent>
      </Card>

      {/* Plan özellikleri */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-sm font-semibold text-gray-600 uppercase tracking-wide">
            Plan Özellikleri
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-3">
            {[
              {
                label: 'Video Üretimi',
                icon: <ImageIcon className="w-4 h-4" />,
                active: limits.can_use_video,
              },
              {
                label: 'AI Avatar',
                icon: <Layers className="w-4 h-4" />,
                active: limits.can_use_avatar,
              },
            ].map((feat) => (
              <div
                key={feat.label}
                className={`flex items-center gap-2.5 p-3 rounded-lg border ${
                  feat.active
                    ? 'border-green-200 bg-green-50 text-green-700'
                    : 'border-gray-100 bg-gray-50 text-gray-400'
                }`}
              >
                {feat.active ? (
                  <CheckCircle className="w-4 h-4 shrink-0" />
                ) : (
                  <div className="w-4 h-4 shrink-0 rounded-full border-2 border-current opacity-40" />
                )}
                <span className="text-sm font-medium">{feat.label}</span>
                {!feat.active && (
                  <Link href="/fiyatlandirma" className="ml-auto text-xs text-blue-600 hover:underline">
                    Yükselt
                  </Link>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// ─── Page wrapper (Suspense for useSearchParams) ─────────────────────────────

export default function FaturalandirmaPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    }>
      <FaturalandirmaInner />
    </Suspense>
  )
}
