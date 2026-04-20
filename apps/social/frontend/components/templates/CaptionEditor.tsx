'use client'

import { useState } from 'react'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
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

const INLINE_HASHTAG_PLATFORMS = new Set([
  'linkedin',
  'twitter',
  'tiktok',
  'youtube',
  'pinterest',
  'bluesky',
])

function normalizeTag(raw: string): string {
  const trimmed = raw.trim().replace(/\s+/g, '')
  if (!trimmed) return ''
  return '#' + trimmed.replace(/^#+/, '')
}

export function CaptionEditor({ data, platforms, onChange }: CaptionEditorProps) {
  const tabs = platforms.length > 0 ? ['default', ...platforms] : ['default']
  const [activeTab, setActiveTab] = useState(tabs[0])
  const [hashtagInput, setHashtagInput] = useState('')

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

  function updateHashtags(hashtags: string[]) {
    onChange({ ...data, hashtags })
  }

  function commitHashtagInput() {
    const raw = hashtagInput
    if (!raw.trim()) return
    const parts = raw
      .split(/[,;\n\t\s]+/)
      .map(normalizeTag)
      .filter(Boolean)
    if (parts.length === 0) {
      setHashtagInput('')
      return
    }
    const existing = new Set(data.hashtags.map((h) => h.toLowerCase()))
    const next = [...data.hashtags]
    for (const p of parts) {
      if (!existing.has(p.toLowerCase())) {
        next.push(p)
        existing.add(p.toLowerCase())
      }
    }
    updateHashtags(next)
    setHashtagInput('')
  }

  function removeHashtag(tag: string) {
    updateHashtags(data.hashtags.filter((h) => h !== tag))
  }

  const showHashtagEditor =
    activeTab === 'default' || INLINE_HASHTAG_PLATFORMS.has(activeTab)

  return (
    <div className="space-y-5">
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

      {showHashtagEditor && (
        <div className="space-y-1.5">
          <Label className="text-sm">Hashtag'ler</Label>
          <p className="text-xs text-gray-400">
            {activeTab === 'default'
              ? 'Tüm platformlar için önerilen hashtag listesi.'
              : `${PLATFORM_LABELS[activeTab] || activeTab} gönderi metnine eklenecek hashtag'ler.`}
          </p>
          <div className="flex gap-2">
            <Input
              value={hashtagInput}
              onChange={(e) => setHashtagInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ',') {
                  e.preventDefault()
                  commitHashtagInput()
                }
              }}
              onBlur={() => {
                if (hashtagInput.trim()) commitHashtagInput()
              }}
              placeholder="hashtag ekle (Enter veya virgül)"
              className="text-sm"
            />
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={commitHashtagInput}
              disabled={!hashtagInput.trim()}
            >
              Ekle
            </Button>
          </div>
          <div className="flex flex-wrap gap-1.5 min-h-[32px] pt-1">
            {data.hashtags.length === 0 ? (
              <span className="text-xs text-gray-400">Henüz hashtag yok.</span>
            ) : (
              data.hashtags.map((tag) => (
                <Badge key={tag} variant="secondary" className="text-xs gap-1 pr-1">
                  <span>{tag}</span>
                  <button
                    onClick={() => removeHashtag(tag)}
                    className="text-gray-400 hover:text-red-500 ml-0.5"
                    aria-label={`${tag} kaldır`}
                  >
                    ✕
                  </button>
                </Badge>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  )
}
