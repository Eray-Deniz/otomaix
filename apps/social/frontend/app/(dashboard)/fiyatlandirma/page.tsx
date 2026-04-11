'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Check, Loader2, Zap } from 'lucide-react'

// ─── Types ──────────────────────────────────────────────────────────────────

interface Plan {
  id: string
  name: string
  price_try: number
  max_brands: number | null
  max_posts_per_month: number | null
  max_storage_gb: number
  can_use_video: boolean
  can_use_avatar: boolean
  features: string[]
  popular?: boolean
}

interface BillingInfo {
  plan_id: string
}

// ─── Page ────────────────────────────────────────────────────────────────────

export default function FiyatlandirmaPage() {
  const [plans, setPlans] = useState<Plan[]>([])
  const [currentPlanId, setCurrentPlanId] = useState<string>('starter')
  const [loadingPlan, setLoadingPlan] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function load() {
      const [plansRes, billingRes] = await Promise.all([
        api.get<Plan[]>('/billing/plans'),
        api.get<BillingInfo>('/billing/current'),
      ])
      if (plansRes.success && plansRes.data) setPlans(plansRes.data)
      if (billingRes.success && billingRes.data) setCurrentPlanId(billingRes.data.plan_id)
      setLoading(false)
    }
    load()
  }, [])

  async function handleSelectPlan(planId: string) {
    if (planId === currentPlanId) return
    setLoadingPlan(planId)
    try {
      const res = await api.post<{ checkout_url: string }>('/billing/checkout', { plan_id: planId })
      if (res.success && res.data?.checkout_url) {
        window.location.href = res.data.checkout_url
      } else {
        toast.error(res.error || 'Ödeme sayfası açılamadı')
      }
    } catch {
      toast.error('Bir hata oluştu')
    } finally {
      setLoadingPlan(null)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    )
  }

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Planınızı Seçin</h1>
        <p className="text-gray-500">İhtiyacınıza göre büyüyen esnek planlar</p>
      </div>

      <div className="grid grid-cols-4 gap-4">
        {plans.map((plan) => {
          const isCurrent = plan.id === currentPlanId
          const isLoading = loadingPlan === plan.id

          return (
            <Card
              key={plan.id}
              className={`relative flex flex-col transition-shadow ${
                plan.popular
                  ? 'border-blue-500 border-2 shadow-lg shadow-blue-50'
                  : 'border-gray-200'
              } ${isCurrent ? 'bg-blue-50/30' : ''}`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <Badge className="bg-blue-600 text-white text-xs px-3 py-0.5 shadow">
                    En Popüler
                  </Badge>
                </div>
              )}

              <CardHeader className="pb-3 pt-5">
                <CardTitle className="text-lg font-bold text-gray-900">{plan.name}</CardTitle>
                <div className="mt-2">
                  <span className="text-3xl font-extrabold text-gray-900">
                    ₺{plan.price_try.toLocaleString('tr-TR')}
                  </span>
                  <span className="text-sm text-gray-400 ml-1">/ay</span>
                </div>
              </CardHeader>

              <CardContent className="flex-1 flex flex-col gap-4">
                <ul className="space-y-2 flex-1">
                  {plan.features.map((f, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-gray-600">
                      <Check className="w-4 h-4 text-green-500 mt-0.5 shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>

                <Button
                  className={`w-full mt-2 ${
                    plan.popular && !isCurrent
                      ? 'bg-blue-600 hover:bg-blue-700'
                      : ''
                  }`}
                  variant={isCurrent ? 'outline' : plan.popular ? 'default' : 'outline'}
                  disabled={isCurrent || isLoading}
                  onClick={() => handleSelectPlan(plan.id)}
                >
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : isCurrent ? (
                    <span className="flex items-center gap-1.5">
                      <Check className="w-4 h-4" /> Mevcut Plan
                    </span>
                  ) : (
                    <span className="flex items-center gap-1.5">
                      <Zap className="w-4 h-4" /> Planı Seç
                    </span>
                  )}
                </Button>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <p className="text-center text-xs text-gray-400 mt-8">
        Tüm planlar KDV hariçtir. İstediğiniz zaman iptal edebilirsiniz.
        Sorularınız için{' '}
        <a href="mailto:destek@otomaix.com" className="underline hover:text-gray-600">
          destek@otomaix.com
        </a>
      </p>
    </div>
  )
}
