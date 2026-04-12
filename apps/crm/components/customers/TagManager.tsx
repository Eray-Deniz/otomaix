'use client'

import { useState } from 'react'
import { addTag, removeTag } from '@/app/customer-actions'
import { X } from 'lucide-react'

const ALL_TAGS = ['VIP', 'Churn Riski', 'Pilot', 'Agency', 'Sorunlu']

const TAG_COLORS: Record<string, string> = {
  VIP: 'bg-amber-100 text-amber-700',
  'Churn Riski': 'bg-orange-100 text-orange-700',
  Pilot: 'bg-cyan-100 text-cyan-700',
  Agency: 'bg-purple-100 text-purple-700',
  Sorunlu: 'bg-red-100 text-red-700',
}

interface Props {
  accountId: string
  currentTags: string[]
}

export function TagManager({ accountId, currentTags }: Props) {
  const [tags, setTags] = useState(currentTags)
  const [loading, setLoading] = useState<string | null>(null)

  const handleAdd = async (tag: string) => {
    if (tags.includes(tag)) return
    setLoading(tag)
    await addTag(accountId, tag, 'Eray')
    setTags(t => [...t, tag])
    setLoading(null)
  }

  const handleRemove = async (tag: string) => {
    setLoading(tag)
    await removeTag(accountId, tag)
    setTags(t => t.filter(x => x !== tag))
    setLoading(null)
  }

  return (
    <div className="space-y-3">
      {/* Mevcut etiketler */}
      {tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {tags.map((tag) => (
            <span
              key={tag}
              className={`badge ${TAG_COLORS[tag] ?? 'bg-gray-100 text-gray-600'} pr-1`}
            >
              {tag}
              <button
                onClick={() => handleRemove(tag)}
                disabled={loading === tag}
                className="ml-1 hover:opacity-70"
              >
                <X size={10} />
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Ekle */}
      <div className="flex flex-wrap gap-1">
        {ALL_TAGS.filter(t => !tags.includes(t)).map((tag) => (
          <button
            key={tag}
            onClick={() => handleAdd(tag)}
            disabled={loading === tag}
            className="text-[11px] px-2 py-1 border border-dashed border-gray-300 rounded-md text-gray-500 hover:border-gray-400 hover:text-gray-700 transition-colors disabled:opacity-50"
          >
            + {tag}
          </button>
        ))}
      </div>
    </div>
  )
}
