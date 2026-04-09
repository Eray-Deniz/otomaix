'use client'

export const dynamic = 'force-dynamic'

import { useRef, useState, useCallback } from 'react'
import FullCalendar from '@fullcalendar/react'
import dayGridPlugin from '@fullcalendar/daygrid'
import timeGridPlugin from '@fullcalendar/timegrid'
import interactionPlugin from '@fullcalendar/interaction'
import trLocale from '@fullcalendar/core/locales/tr'
import type { EventClickArg, EventDropArg, EventInput } from '@fullcalendar/core'
import type { DateClickArg } from '@fullcalendar/interaction'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import Image from 'next/image'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { toast } from 'sonner'
import { Send, Calendar, RefreshCw, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'

// ─── Types ────────────────────────────────────────────────────────────────────

interface CalendarPost {
  id: string
  title: string
  date: string | null
  status: string
  thumbnail_url: string | null
  platforms: string[]
  scheduled_at: string | null
  published_at: string | null
}

interface Holiday {
  date: string
  name_tr: string
  category: string
}

// ─── Status → FullCalendar color ─────────────────────────────────────────────

const STATUS_COLOR: Record<string, string> = {
  scheduled:  '#4183FF',
  failed:     '#FF8198',
  published:  '#01D3A0',
  rejected:   '#000000',
  reviewing:  '#FFA500',
  generating: '#8B5CF6',
  ready:      '#22C55E',
  draft:      '#9CA3AF',
}

const STATUS_LABEL: Record<string, string> = {
  scheduled:  'Zamanlandı',
  failed:     'Başarısız',
  published:  'Yayınlandı',
  rejected:   'Reddedildi',
  reviewing:  'İncelemede',
  generating: 'Üretiliyor',
  ready:      'Hazır',
  draft:      'Taslak',
}

// ─── Post event modal ─────────────────────────────────────────────────────────

function PostEventModal({
  post,
  open,
  onClose,
}: {
  post: CalendarPost | null
  open: boolean
  onClose: () => void
}) {
  if (!post) return null

  const statusLabel = STATUS_LABEL[post.status] ?? post.status
  const statusColor = STATUS_COLOR[post.status] ?? '#9CA3AF'

  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle className="text-sm">İçerik Detayı</DialogTitle>
        </DialogHeader>

        {/* Thumbnail */}
        <div className="rounded-xl overflow-hidden bg-gray-50 border border-gray-100">
          {post.thumbnail_url ? (
            <Image
              src={post.thumbnail_url}
              alt="İçerik"
              width={400}
              height={400}
              className="w-full object-contain max-h-48"
            />
          ) : (
            <div className="h-32 flex items-center justify-center">
              {post.status === 'generating' ? (
                <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
              ) : (
                <span className="text-3xl">🖼️</span>
              )}
            </div>
          )}
        </div>

        {/* Info */}
        <div className="space-y-2">
          {post.title && (
            <p className="text-sm text-gray-700 line-clamp-2">{post.title}</p>
          )}
          <div className="flex items-center gap-2">
            <span
              className="text-xs font-semibold px-2 py-0.5 rounded-full text-white"
              style={{ backgroundColor: statusColor }}
            >
              {statusLabel}
            </span>
            {post.platforms.length > 0 && (
              <span className="text-xs text-gray-400">{post.platforms.join(', ')}</span>
            )}
          </div>
          {(post.scheduled_at || post.published_at) && (
            <p className="text-xs text-gray-400">
              {post.scheduled_at
                ? `Zamanlandı: ${new Date(post.scheduled_at).toLocaleString('tr-TR')}`
                : `Yayınlandı: ${new Date(post.published_at!).toLocaleString('tr-TR')}`}
            </p>
          )}
        </div>

        {/* Actions */}
        <div className="grid grid-cols-2 gap-2 pt-1 border-t border-gray-100">
          <Button variant="outline" size="sm" className="gap-1.5 text-xs">
            <RefreshCw className="w-3.5 h-3.5" /> Yeniden Üret
          </Button>
          <Button variant="outline" size="sm" className="gap-1.5 text-xs">
            <Calendar className="w-3.5 h-3.5" /> Yeniden Zamanla
          </Button>
          <Button size="sm" className="gap-1.5 text-xs col-span-2">
            <Send className="w-3.5 h-3.5" /> Şimdi Yayınla
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

// ─── New content sheet (date pre-filled) ─────────────────────────────────────

function NewContentDialog({
  date,
  open,
  onClose,
}: {
  date: string | null
  open: boolean
  onClose: () => void
}) {
  return (
    <Dialog open={open} onOpenChange={(v) => !v && onClose()}>
      <DialogContent className="max-w-sm">
        <DialogHeader>
          <DialogTitle>Yeni İçerik</DialogTitle>
        </DialogHeader>
        <p className="text-sm text-gray-500">
          <span className="font-medium text-gray-800">
            {date ? new Date(date).toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' }) : ''}
          </span>{' '}
          tarihine içerik eklemek istiyor musunuz?
        </p>
        <div className="flex gap-2">
          <Button variant="outline" className="flex-1" onClick={onClose}>İptal</Button>
          <Button
            className="flex-1"
            onClick={() => {
              onClose()
              window.location.href = '/icerik-olustur'
            }}
          >
            İçerik Oluştur
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

// ─── Main page ─────────────────────────────────────────────────────────────────

export default function TakvimPage() {
  const currentBrand = useAppStore((s) => s.currentBrand)
  const calendarRef = useRef<InstanceType<typeof FullCalendar>>(null)

  const [view, setView] = useState<'dayGridMonth' | 'timeGridWeek'>('dayGridMonth')
  const [events, setEvents] = useState<EventInput[]>([])
  const [loading, setLoading] = useState(false)

  const [selectedPost, setSelectedPost] = useState<CalendarPost | null>(null)
  const [postModalOpen, setPostModalOpen] = useState(false)

  const [newContentDate, setNewContentDate] = useState<string | null>(null)
  const [newContentOpen, setNewContentOpen] = useState(false)

  // ── Fetch posts for date range ───────────────────────────────────────────────

  const fetchEvents = useCallback(async (start: Date, end: Date) => {
    if (!currentBrand?.id) return
    setLoading(true)

    const startStr = start.toISOString().split('T')[0]
    const endStr = end.toISOString().split('T')[0]

    const [postsRes, holidaysRes] = await Promise.all([
      api.get<CalendarPost[]>(`/calendar/posts?brand_id=${currentBrand.id}&start=${startStr}&end=${endStr}`),
      api.get<Holiday[]>(`/calendar/holidays?year=${start.getFullYear()}`),
    ])

    const postEvents: EventInput[] = []

    if (postsRes.success && postsRes.data) {
      for (const post of postsRes.data) {
        if (!post.date) continue
        postEvents.push({
          id: post.id,
          title: post.title || post.status,
          date: post.scheduled_at ?? post.date,
          backgroundColor: STATUS_COLOR[post.status] ?? '#9CA3AF',
          borderColor: 'transparent',
          textColor: '#ffffff',
          extendedProps: { post },
        })
      }
    }

    if (holidaysRes.success && holidaysRes.data) {
      for (const h of holidaysRes.data) {
        postEvents.push({
          id: `holiday-${h.date}`,
          title: h.name_tr,
          date: h.date,
          display: 'background',
          backgroundColor: h.category === 'religious' ? '#FEF3C7' : '#EDE9FE',
          classNames: ['holiday-event'],
        })
      }
    }

    setEvents(postEvents)
    setLoading(false)
  }, [currentBrand?.id])

  // ── Calendar event handlers ──────────────────────────────────────────────────

  function handleEventClick(info: EventClickArg) {
    const post = info.event.extendedProps?.post as CalendarPost | undefined
    if (!post) return
    setSelectedPost(post)
    setPostModalOpen(true)
  }

  function handleDateClick(info: DateClickArg) {
    const clicked = new Date(info.dateStr)
    const today = new Date()
    today.setHours(0, 0, 0, 0)

    if (clicked < today) {
      toast.warning('Geçmiş tarihe içerik eklenemez')
      return
    }

    setNewContentDate(info.dateStr)
    setNewContentOpen(true)
  }

  async function handleEventDrop(info: EventDropArg) {
    const post = info.event.extendedProps?.post as CalendarPost | undefined
    if (!post) { info.revert(); return }

    const newDate = info.event.start
    if (!newDate) { info.revert(); return }

    const today = new Date()
    today.setHours(0, 0, 0, 0)
    if (newDate < today) {
      toast.warning('Geçmiş tarihe zamanlanamaz')
      info.revert()
      return
    }

    const res = await api.patch(`/calendar/schedule/${post.id}`, {
      scheduled_at: newDate.toISOString(),
    })

    if (res.success) {
      toast.success('Zamanlama güncellendi')
    } else {
      toast.error('Zamanlama güncellenemedi')
      info.revert()
    }
  }

  // ── View toggle ──────────────────────────────────────────────────────────────

  function switchView(v: 'dayGridMonth' | 'timeGridWeek') {
    setView(v)
    calendarRef.current?.getApi().changeView(v)
  }

  // ── Render ───────────────────────────────────────────────────────────────────

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-8 py-5 border-b border-gray-100 bg-white">
        <h1 className="text-lg font-bold text-gray-900">İçerik Takvimi</h1>
        <div className="flex items-center gap-2">
          {loading && <Loader2 className="w-4 h-4 animate-spin text-blue-400" />}
          <div className="flex rounded-lg border border-gray-200 overflow-hidden">
            <button
              onClick={() => switchView('dayGridMonth')}
              className={cn(
                'px-3 py-1.5 text-sm transition-colors',
                view === 'dayGridMonth' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'
              )}
            >
              Aylık
            </button>
            <button
              onClick={() => switchView('timeGridWeek')}
              className={cn(
                'px-3 py-1.5 text-sm border-l border-gray-200 transition-colors',
                view === 'timeGridWeek' ? 'bg-blue-600 text-white' : 'text-gray-600 hover:bg-gray-50'
              )}
            >
              Haftalık
            </button>
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 px-8 py-2 bg-white border-b border-gray-100 flex-wrap">
        {Object.entries(STATUS_COLOR).slice(0, 6).map(([status, color]) => (
          <div key={status} className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: color }} />
            <span className="text-xs text-gray-500">{STATUS_LABEL[status]}</span>
          </div>
        ))}
        <div className="flex items-center gap-1.5">
          <div className="w-2.5 h-2.5 rounded-full bg-amber-100 border border-amber-300" />
          <span className="text-xs text-gray-500">Resmi Tatil</span>
        </div>
      </div>

      {/* Calendar */}
      <div className="flex-1 p-6 overflow-auto">
        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-4 calendar-wrapper">
          <FullCalendar
            ref={calendarRef}
            plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
            initialView={view}
            locale={trLocale}
            headerToolbar={{
              left: 'prev,next today',
              center: 'title',
              right: '',
            }}
            buttonText={{
              today: 'Bugün',
            }}
            events={events}
            editable={true}
            droppable={true}
            dateClick={handleDateClick}
            eventClick={handleEventClick}
            eventDrop={handleEventDrop}
            datesSet={(info) => fetchEvents(info.start, info.end)}
            height="auto"
            eventDisplay="block"
            dayMaxEvents={3}
            moreLinkText={(n) => `+${n} daha`}
            eventContent={(arg) => {
              if (arg.event.display === 'background') return null
              return (
                <div className="flex items-center gap-1 px-1.5 py-0.5 overflow-hidden">
                  <div
                    className="w-1.5 h-1.5 rounded-full flex-shrink-0"
                    style={{ backgroundColor: arg.event.backgroundColor }}
                  />
                  <span className="text-[11px] font-medium truncate leading-tight">
                    {arg.event.title}
                  </span>
                </div>
              )
            }}
          />
        </div>
      </div>

      {/* Post event modal */}
      <PostEventModal
        post={selectedPost}
        open={postModalOpen}
        onClose={() => { setPostModalOpen(false); setSelectedPost(null) }}
      />

      {/* New content dialog */}
      <NewContentDialog
        date={newContentDate}
        open={newContentOpen}
        onClose={() => setNewContentOpen(false)}
      />
    </div>
  )
}
