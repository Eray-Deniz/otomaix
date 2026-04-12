'use client'

import { useState } from 'react'
import { addTag } from '@/app/customer-actions'

export function MarkChurnRisk({ accountId }: { accountId: string }) {
  const [loading, setLoading] = useState(false)
  const [done, setDone] = useState(false)

  const handleClick = async () => {
    setLoading(true)
    await addTag(accountId, 'Churn Riski', 'Sistem')
    setDone(true)
    setLoading(false)
  }

  if (done) return <span className="text-xs text-orange-600">✓ Etiketlendi</span>

  return (
    <button
      onClick={handleClick}
      disabled={loading}
      className="text-xs text-orange-600 hover:underline disabled:opacity-50"
    >
      {loading ? 'Ekleniyor...' : 'Churn Riski Ekle'}
    </button>
  )
}
