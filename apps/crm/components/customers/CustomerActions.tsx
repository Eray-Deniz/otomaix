'use client'

import { useState } from 'react'
import { changePlan } from '@/app/customer-actions'
import { PLAN_LABELS } from '@/lib/utils'

interface CustomerInfo {
  id: string
  email: string
  plan_id: string
  paddle_customer_id: string | null
}

export function CustomerActions({ customer }: { customer: CustomerInfo }) {
  const [loading, setLoading] = useState<string | null>(null)
  const [planModal, setPlanModal] = useState(false)
  const [selectedPlan, setSelectedPlan] = useState(customer.plan_id)

  const handleChangePlan = async () => {
    if (selectedPlan === customer.plan_id) return
    setLoading('plan')
    await changePlan(customer.id, selectedPlan)
    setLoading(null)
    setPlanModal(false)
    window.location.reload()
  }

  return (
    <div className="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-50">
        <h2 className="text-sm font-semibold text-gray-700">Hızlı Aksiyonlar</h2>
      </div>
      <div className="p-4 space-y-2">
        {/* Plan Değiştir */}
        <button
          onClick={() => setPlanModal(true)}
          className="w-full text-left text-xs px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg text-gray-700 transition-colors"
        >
          📋 Plan Değiştir
          <span className="ml-1 text-gray-400">
            ({PLAN_LABELS[customer.plan_id] ?? customer.plan_id})
          </span>
        </button>

        {/* Paddle Portal */}
        {customer.paddle_customer_id && (
          <a
            href={`https://vendors.paddle.com/customers/${customer.paddle_customer_id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex w-full text-left text-xs px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg text-gray-700 transition-colors"
          >
            💳 Paddle'da Görüntüle ↗
          </a>
        )}

        {/* Supabase şifre sıfırlama — API üzerinden */}
        <form action={async () => {
          const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/auth/reset-password`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: customer.email }),
          })
          alert(res.ok ? 'Şifre sıfırlama emaili gönderildi' : 'Gönderim başarısız')
        }}>
          <button
            type="submit"
            className="w-full text-left text-xs px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg text-gray-700 transition-colors"
          >
            🔑 Şifre Sıfırlama Gönder
          </button>
        </form>
      </div>

      {/* Plan Modal */}
      {planModal && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-5 w-72 shadow-xl">
            <h3 className="text-sm font-semibold text-gray-900 mb-4">Plan Değiştir</h3>
            <select
              value={selectedPlan}
              onChange={(e) => setSelectedPlan(e.target.value)}
              className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-400 mb-4"
            >
              {Object.entries(PLAN_LABELS).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
            <div className="flex gap-2">
              <button
                onClick={handleChangePlan}
                disabled={loading === 'plan' || selectedPlan === customer.plan_id}
                className="flex-1 text-xs bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white py-2 rounded-lg"
              >
                {loading === 'plan' ? 'Değiştiriliyor...' : 'Onayla'}
              </button>
              <button
                onClick={() => setPlanModal(false)}
                className="flex-1 text-xs border border-gray-200 text-gray-700 hover:bg-gray-50 py-2 rounded-lg"
              >
                İptal
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
