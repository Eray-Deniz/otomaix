'use client'

import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { cn } from '@/lib/utils'
import type { CaptionData } from './CaptionEditor'

interface CaptionPreviewProps {
  data: CaptionData
  platforms: string[]
  onEdit?: () => void
}

const PLATFORM_LABELS: Record<string, string> = {
  instagram: 'Instagram',
  linkedin: 'LinkedIn',
  twitter: 'Twitter / X',
  facebook: 'Facebook',
  tiktok: 'TikTok',
  threads: 'Threads',
  pinterest: 'Pinterest',
  bluesky: 'Bluesky',
  youtube: 'YouTube',
}

export function CaptionPreview({ data, platforms, onEdit }: CaptionPreviewProps) {
  const tabs = platforms.length > 0 ? ['default', ...platforms] : ['default']
  const [activeTab, setActiveTab] = useState(tabs[0])

  const activeCaption =
    activeTab === 'default'
      ? data.default_caption
      : data.platform_captions[activeTab]?.caption ?? data.default_caption

  const activeFirstComment =
    activeTab !== 'default'
      ? data.platform_captions[activeTab]?.first_comment
      : undefined

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <Label className="text-sm">Gönderi Metni</Label>
        {onEdit && (
          <button
            onClick={onEdit}
            className="text-xs text-blue-500 hover:underline"
          >
            ← Metni düzenle
          </button>
        )}
      </div>

      {tabs.length > 1 && (
        <div className="flex gap-1 border-b border-gray-200 overflow-x-auto">
          {tabs.map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={cn(
                'px-3 py-2 text-xs font-medium whitespace-nowrap border-b-2 transition-colors',
                activeTab === tab
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              )}
            >
              {tab === 'default' ? 'Varsayılan' : PLATFORM_LABELS[tab] || tab}
            </button>
          ))}
        </div>
      )}

      <div className="p-3 bg-gray-50 border border-gray-200 rounded-md">
        <p className="text-sm text-gray-700 whitespace-pre-wrap">
          {activeCaption || '(boş)'}
        </p>
      </div>

      {activeFirstComment !== undefined && activeFirstComment.trim() !== '' && (
        <div className="space-y-1.5">
          <Label className="text-xs text-gray-500">İlk Yorum (hashtag bloğu)</Label>
          <div className="p-3 bg-blue-50 border border-blue-200 rounded-md">
            <p className="text-sm text-blue-900 whitespace-pre-wrap">
              {activeFirstComment}
            </p>
          </div>
        </div>
      )}

      {activeTab === 'default' && data.hashtags.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {data.hashtags.map((tag) => (
            <Badge key={tag} variant="secondary" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>
      )}
    </div>
  )
}
