'use client'

import Image from 'next/image'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { Download, Send, Calendar, MoreHorizontal, Loader2 } from 'lucide-react'

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Post {
  id: string
  content_type: string
  content_category: string | null
  status: string
  prompt: string | null
  output_url: string | null
  thumbnail_url: string | null
  caption: string | null
  hashtags: string[] | null
  aspect_ratio: string | null
  platforms: string[] | null
  scheduled_at: string | null
  published_at: string | null
  created_at: string
}

// ─── Status config ─────────────────────────────────────────────────────────────

const STATUS_CONFIG: Record<string, { label: string; className: string; pulse?: boolean }> = {
  draft:      { label: 'Taslak',      className: 'bg-gray-100 text-gray-600' },
  generating: { label: 'Üretiliyor',  className: 'bg-blue-100 text-blue-700', pulse: true },
  ready:      { label: 'Hazır',       className: 'bg-green-100 text-green-700' },
  scheduled:  { label: 'Zamanlandı', className: 'bg-blue-100 text-blue-700' },
  published:  { label: 'Yayınlandı', className: 'bg-emerald-100 text-emerald-700' },
  failed:     { label: 'Başarısız',   className: 'bg-red-100 text-red-700' },
}

const PLATFORM_ICONS: Record<string, string> = {
  instagram: 'IG',
  tiktok: 'TK',
  linkedin: 'LN',
  facebook: 'FB',
  youtube: 'YT',
  twitter: 'TW',
  pinterest: 'PT',
}

// ─── Component ────────────────────────────────────────────────────────────────

interface ContentCardProps {
  post: Post
  onClick: (post: Post) => void
  onPublish?: (post: Post) => void
  showWatermark?: boolean
}

export function ContentCard({ post, onClick, onPublish, showWatermark = false }: ContentCardProps) {
  const [hovered, setHovered] = useState(false)
  const status = STATUS_CONFIG[post.status] ?? { label: post.status, className: 'bg-gray-100 text-gray-600' }
  const imageUrl = post.thumbnail_url ?? post.output_url

  return (
    <div
      className="relative rounded-xl overflow-hidden border border-gray-100 bg-white shadow-sm hover:shadow-md transition-all cursor-pointer group"
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={() => onClick(post)}
    >
      {/* Image area */}
      <div className="relative bg-gray-50 w-full">
        {imageUrl ? (
          <Image
            src={imageUrl}
            alt={post.prompt ?? 'İçerik'}
            width={400}
            height={400}
            className="w-full object-cover"
            style={{ aspectRatio: post.aspect_ratio?.replace(':', '/') ?? '1/1' }}
          />
        ) : (
          <div
            className="w-full flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100"
            style={{ aspectRatio: post.aspect_ratio?.replace(':', '/') ?? '1/1' }}
          >
            {post.status === 'generating' ? (
              <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
            ) : (
              <span className="text-3xl">🖼️</span>
            )}
          </div>
        )}

        {/* Freemium watermark */}
        {showWatermark && imageUrl && (
          <div className="absolute inset-0 flex items-end justify-center pb-4 pointer-events-none">
            <div className="bg-black/40 text-white text-[10px] font-bold px-2 py-0.5 rounded tracking-widest">
              OTOMAIX
            </div>
          </div>
        )}

        {/* Hover action bar */}
        {hovered && (
          <div
            className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 to-transparent p-3 flex gap-2"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              title="İndir"
              className="flex-1 flex items-center justify-center gap-1 text-white text-xs bg-white/20 hover:bg-white/30 rounded-lg py-1.5 transition-colors"
              onClick={() => post.output_url && window.open(post.output_url, '_blank')}
            >
              <Download className="w-3 h-3" /> İndir
            </button>
            <button
              title="Yayınla"
              className="flex-1 flex items-center justify-center gap-1 text-white text-xs bg-white/20 hover:bg-white/30 rounded-lg py-1.5 transition-colors"
              onClick={() => onPublish?.(post)}
            >
              <Send className="w-3 h-3" /> Yayınla
            </button>
            <button
              title="Zamanla"
              className="flex-1 flex items-center justify-center gap-1 text-white text-xs bg-white/20 hover:bg-white/30 rounded-lg py-1.5 transition-colors"
              onClick={() => onClick(post)}
            >
              <Calendar className="w-3 h-3" /> Zamanla
            </button>
            <button
              title="Daha Fazla"
              className="flex items-center justify-center text-white bg-white/20 hover:bg-white/30 rounded-lg px-2 py-1.5 transition-colors"
              onClick={() => onClick(post)}
            >
              <MoreHorizontal className="w-3 h-3" />
            </button>
          </div>
        )}
      </div>

      {/* Card footer */}
      <div className="p-2.5 space-y-1.5">
        {/* Status + platforms row */}
        <div className="flex items-center justify-between gap-2">
          <span className={cn(
            'text-[10px] font-semibold px-2 py-0.5 rounded-full',
            status.className,
            status.pulse && 'animate-pulse'
          )}>
            {status.label}
          </span>
          <div className="flex gap-1">
            {(post.platforms ?? []).slice(0, 3).map((p) => (
              <span
                key={p}
                className="text-[9px] font-bold px-1 py-0.5 bg-gray-100 text-gray-500 rounded"
              >
                {PLATFORM_ICONS[p] ?? p.slice(0, 2).toUpperCase()}
              </span>
            ))}
          </div>
        </div>

        {/* Caption preview */}
        {post.caption && (
          <p className="text-xs text-gray-500 line-clamp-2 leading-relaxed">
            {post.caption}
          </p>
        )}

        {/* Date */}
        <p className="text-[10px] text-gray-300">
          {new Date(post.created_at).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' })}
        </p>
      </div>

      {/* Freemium upgrade CTA */}
      {showWatermark && (
        <div className="px-2.5 pb-2.5">
          <Button
            size="sm"
            className="w-full text-xs bg-amber-400 hover:bg-amber-500 text-amber-900 h-7"
            onClick={(e) => { e.stopPropagation(); }}
          >
            Filigranı Kaldır
          </Button>
        </div>
      )}
    </div>
  )
}
