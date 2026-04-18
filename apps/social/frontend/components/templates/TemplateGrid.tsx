'use client'

import { useEffect, useState } from 'react'
import { Loader2, PenLine } from 'lucide-react'
import { fetchTemplates } from '@/lib/api/templates'
import type { Template } from '@/lib/templates.types'
import { TemplateCard } from './TemplateCard'

interface TemplateGridProps {
  sectorSlug?: string | null
  contentType: string
  selectedId?: string | null
  onSelect: (template: Template) => void
  onFreeForm: () => void
}

export function TemplateGrid({
  sectorSlug,
  contentType,
  selectedId,
  onSelect,
  onFreeForm,
}: TemplateGridProps) {
  const [templates, setTemplates] = useState<Template[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    async function load() {
      setLoading(true)
      const res = await fetchTemplates({
        sector: sectorSlug ?? undefined,
        contentType,
      })
      if (!cancelled) {
        setTemplates(res)
        setLoading(false)
      }
    }
    load()
    return () => { cancelled = true }
  }, [sectorSlug, contentType])

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
      </div>
    )
  }

  // Sektör şablonları ve genel (sectors=["*"]) ayrımı
  const sectorTemplates = templates.filter(
    (t) => sectorSlug && t.sectors.includes(sectorSlug)
  )
  const genericTemplates = templates.filter((t) => t.sectors.includes('*'))

  // Sort by order if present
  const sortByOrder = (a: Template, b: Template) =>
    (a.order ?? 999) - (b.order ?? 999)
  sectorTemplates.sort(sortByOrder)
  genericTemplates.sort(sortByOrder)

  return (
    <div className="space-y-5">
      {sectorTemplates.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <p className="text-sm font-semibold text-gray-700">Sektörünüze Özel Şablonlar</p>
            <span className="text-xs text-gray-400">({sectorTemplates.length})</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {sectorTemplates.map((t) => (
              <TemplateCard
                key={t.id}
                template={t}
                selected={selectedId === t.id}
                onClick={() => onSelect(t)}
              />
            ))}
          </div>
        </div>
      )}

      {genericTemplates.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3 mt-2">
            <p className="text-sm font-semibold text-gray-700">Genel Şablonlar</p>
            <span className="text-xs text-gray-400">({genericTemplates.length})</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {genericTemplates.map((t) => (
              <TemplateCard
                key={t.id}
                template={t}
                selected={selectedId === t.id}
                onClick={() => onSelect(t)}
              />
            ))}
          </div>
        </div>
      )}

      {templates.length === 0 && (
        <p className="text-sm text-gray-500 py-8 text-center">
          Bu içerik tipi için şablon bulunamadı.
        </p>
      )}

      <div className="border-t border-gray-100 pt-4">
        <button
          onClick={onFreeForm}
          className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl border border-dashed border-gray-300 text-sm text-gray-600 hover:border-blue-400 hover:text-blue-600 hover:bg-blue-50/30 transition-colors"
        >
          <PenLine className="w-4 h-4" />
          Şablonsuz devam et — serbest içerik yaz
        </button>
      </div>
    </div>
  )
}
