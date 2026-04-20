'use client'

import { useState } from 'react'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

export interface PlatformCaption {
  caption: string
  first_comment?: string
}

export interface CaptionData {
  default_caption: string
  platform_captions: Record<string, PlatformCaption>
  image_prompt: string
  hashtags: string[]
}

interface CaptionEditorProps {
  data: CaptionData
  platforms: string[]
  onChange: (data: CaptionData) => void
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

export function CaptionEditor({ data, platforms, onChange }: CaptionEditorProps) {
  const tabs = platforms.length > 0 ? ['default', ...platforms] : ['default']
  const [activeTab, setActiveTab] = useState(tabs[0])

  function updateDefault(caption: string) {
    onChange({ ...data, default_caption: caption })
  }

  function updatePlatform(platform: string, partial: Partial<PlatformCaption>) {
    const existing = data.platform_captions[platform] || { caption: '' }
    onChange({
      ...data,
      platform_captions: {
        ...data.platform_captions,
        [platform]: { ...existing, ...partial },
      },
    })
  }

  function updateImagePrompt(prompt: string) {
    onChange({ ...data, image_prompt: prompt })
  }

  function updateHashtags(hashtags: string[]) {
    onChange({ ...data, hashtags })
  }

  return (
    <div className="space-y-5">
      {/* Platform tab strip */}
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

      {/* Gönderi metni alanı */}
      {activeTab === 'default' ? (
        <div className="space-y-1.5">
          <Label className="text-sm">Varsayılan Gönderi Metni</Label>
          <p className="text-xs text-gray-400">Platform-özel gönderi metni yoksa kullanılır.</p>
          <Textarea
            value={data.default_caption}
            onChange={(e) => updateDefault(e.target.value)}
            placeholder="Gönderi metni..."
            rows={5}
            className="resize-none text-sm"
          />
        </div>
      ) : (
        <div className="space-y-3">
          <div className="space-y-1.5">
            <Label className="text-sm">
              {PLATFORM_LABELS[activeTab] || activeTab} Gönderi Metni
            </Label>
            <Textarea
              value={data.platform_captions[activeTab]?.caption ?? ''}
              onChange={(e) => updatePlatform(activeTab, { caption: e.target.value })}
              placeholder="Platform-özel gönderi metni..."
              rows={5}
              className="resize-none text-sm"
            />
          </div>

          {data.platform_captions[activeTab]?.first_comment !== undefined && (
            <div className="space-y-1.5">
              <Label className="text-sm">İlk Yorum (hashtag bloğu)</Label>
              <p className="text-xs text-gray-400">
                Gönderi metninden ayrı olarak yayınlanacak ilk yorum metni.
              </p>
              <Textarea
                value={data.platform_captions[activeTab].first_comment ?? ''}
                onChange={(e) =>
                  updatePlatform(activeTab, { first_comment: e.target.value })
                }
                placeholder="#hashtag1 #hashtag2 ..."
                rows={3}
                className="resize-none text-sm"
              />
            </div>
          )}
        </div>
      )}

      {/* Hashtag editor */}
      <div className="space-y-2">
        <Label className="text-sm">Hashtag&apos;ler</Label>
        <div className="flex flex-wrap gap-1.5 p-2 border border-gray-200 rounded-md bg-gray-50 min-h-[36px]">
          {data.hashtags.map((tag) => (
            <Badge key={tag} variant="secondary" className="gap-1 text-xs">
              {tag}
              <button
                type="button"
                onClick={() => updateHashtags(data.hashtags.filter((h) => h !== tag))}
                className="text-gray-500 hover:text-gray-800"
              >
                ×
              </button>
            </Badge>
          ))}
          {data.hashtags.length === 0 && (
            <span className="text-xs text-gray-400 px-1">Henüz hashtag yok</span>
          )}
        </div>
      </div>

    </div>
  )
}
