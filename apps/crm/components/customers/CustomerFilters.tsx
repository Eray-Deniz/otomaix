'use client'

import { useRouter, usePathname } from 'next/navigation'
import { useCallback, useState } from 'react'
import { Search, X } from 'lucide-react'

interface FilterValues {
  plan?: string
  status?: string
  tag?: string
  login?: string
  q?: string
}

interface Props {
  initialValues: FilterValues
}

export function CustomerFilters({ initialValues }: Props) {
  const router = useRouter()
  const pathname = usePathname()
  const [values, setValues] = useState<FilterValues>(initialValues)

  const applyFilters = useCallback(
    (newValues: FilterValues) => {
      const params = new URLSearchParams()
      Object.entries(newValues).forEach(([k, v]) => {
        if (v && v !== 'all') params.set(k, v)
      })
      router.push(`${pathname}?${params.toString()}`)
    },
    [router, pathname]
  )

  const handleChange = (key: keyof FilterValues, value: string) => {
    const next = { ...values, [key]: value, page: undefined }
    setValues(next)
    if (key !== 'q') applyFilters(next)
  }

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    applyFilters(values)
  }

  const hasFilters = Object.entries(values).some(([, v]) => v && v !== 'all')

  return (
    <div className="bg-white rounded-xl p-3 border border-gray-100 shadow-sm flex flex-wrap gap-2 items-center">
      {/* Arama */}
      <form onSubmit={handleSearch} className="flex-1 min-w-48 relative">
        <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          value={values.q ?? ''}
          onChange={(e) => handleChange('q', e.target.value)}
          placeholder="Ad veya email ara..."
          className="w-full pl-7 pr-3 py-1.5 text-xs border border-gray-200 rounded-lg focus:outline-none focus:border-blue-400"
        />
      </form>

      <select
        value={values.plan ?? 'all'}
        onChange={(e) => handleChange('plan', e.target.value)}
        className="text-xs border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:border-blue-400 bg-white"
      >
        <option value="all">Tüm Planlar</option>
        <option value="starter">Starter</option>
        <option value="pro">Pro</option>
        <option value="business">Business</option>
        <option value="agency">Agency</option>
      </select>

      <select
        value={values.status ?? 'all'}
        onChange={(e) => handleChange('status', e.target.value)}
        className="text-xs border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:border-blue-400 bg-white"
      >
        <option value="all">Tüm Durumlar</option>
        <option value="active">Aktif</option>
        <option value="trialing">Deneme</option>
        <option value="past_due">Ödeme Sorunu</option>
        <option value="cancelled">İptal</option>
      </select>

      <select
        value={values.tag ?? 'all'}
        onChange={(e) => handleChange('tag', e.target.value)}
        className="text-xs border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:border-blue-400 bg-white"
      >
        <option value="all">Tüm Etiketler</option>
        <option value="VIP">VIP</option>
        <option value="Churn Riski">Churn Riski</option>
        <option value="Pilot">Pilot</option>
        <option value="Sorunlu">Sorunlu</option>
      </select>

      <select
        value={values.login ?? 'all'}
        onChange={(e) => handleChange('login', e.target.value)}
        className="text-xs border border-gray-200 rounded-lg px-2 py-1.5 focus:outline-none focus:border-blue-400 bg-white"
      >
        <option value="all">Tüm Zamanlar</option>
        <option value="7">Son 7 gün</option>
        <option value="30">7-30 gün</option>
        <option value="30plus">30+ gün</option>
      </select>

      {hasFilters && (
        <button
          onClick={() => {
            setValues({})
            router.push(pathname)
          }}
          className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700"
        >
          <X size={12} /> Temizle
        </button>
      )}
    </div>
  )
}
