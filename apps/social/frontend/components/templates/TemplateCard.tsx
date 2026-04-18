'use client'

import { cn } from '@/lib/utils'
import type { Template } from '@/lib/templates.types'

interface TemplateCardProps {
  template: Template
  selected?: boolean
  onClick: () => void
}

export function TemplateCard({ template, selected, onClick }: TemplateCardProps) {
  const hasDisclaimer = !!template.defaults.disclaimer

  return (
    <button
      onClick={onClick}
      className={cn(
        'flex flex-col items-start gap-2 p-4 rounded-xl border-2 text-left transition-all cursor-pointer h-full',
        selected
          ? 'border-blue-500 bg-blue-50 shadow-sm'
          : 'border-gray-200 hover:border-blue-300 hover:bg-blue-50/30'
      )}
    >
      <div className="flex items-center gap-2 w-full">
        <span className="text-2xl">{template.icon}</span>
        <span className="text-sm font-semibold text-gray-800 flex-1 leading-tight">
          {template.name}
        </span>
      </div>
      <p className="text-xs text-gray-500 leading-snug line-clamp-2">
        {template.description}
      </p>
      {hasDisclaimer && (
        <span className="text-[10px] text-amber-700 bg-amber-100 px-1.5 py-0.5 rounded">
          ⚠ Disclaimer
        </span>
      )}
    </button>
  )
}
