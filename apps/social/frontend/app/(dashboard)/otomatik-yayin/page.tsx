'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useState, useCallback } from 'react'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { toast } from 'sonner'
import { Loader2, Zap, ChevronRight, Check, Lightbulb, MessageCircle } from 'lucide-react'
import { cn } from '@/lib/utils'

// ─── Types ────────────────────────────────────────────────────────────────────

interface AutopostingConfig {
  id: string
  brand_id: string
  is_enabled: boolean
  frequency: string
  time_slots: { day: string; time: string }[]
  content_types: string[]
  content_categories: string[]
  topics: string[]
  platforms: string[]
}

interface UpcomingPost {
  id: string
  content_type: string
  status: string
  thumbnail_url: string | null
  caption: string | null
  scheduled_at: string
}

type WizardStep = 1 | 2 | 3 | 4

// ─── Constants ────────────────────────────────────────────────────────────────

const FREQUENCIES = [
  { id: 'daily',      label: 'Günde 1',   desc: '7 içerik / hafta' },
  { id: '3x_weekly',  label: 'Haftada 3', desc: '3 içerik / hafta' },
  { id: 'weekly',     label: 'Haftada 1', desc: '1 içerik / hafta' },
]

const TIME_SLOTS_BY_FREQ: Record<string, { day: string; time: string }[]> = {
  daily: [
    { day: 'monday', time: '10:00' }, { day: 'tuesday', time: '10:00' },
    { day: 'wednesday', time: '10:00' }, { day: 'thursday', time: '10:00' },
    { day: 'friday', time: '10:00' }, { day: 'saturday', time: '10:00' },
    { day: 'sunday', time: '10:00' },
  ],
  '3x_weekly': [
    { day: 'monday', time: '10:00' }, { day: 'wednesday', time: '10:00' },
    { day: 'friday', time: '10:00' },
  ],
  weekly: [{ day: 'monday', time: '10:00' }],
}

const DAY_TR: Record<string, string> = {
  monday: 'Pzt', tuesday: 'Sal', wednesday: 'Çar',
  thursday: 'Per', friday: 'Cum', saturday: 'Cmt', sunday: 'Paz',
}

const DAY_TR_FULL: Record<string, string> = {
  monday: 'Pazartesi', tuesday: 'Salı', wednesday: 'Çarşamba',
  thursday: 'Perşembe', friday: 'Cuma', saturday: 'Cumartesi', sunday: 'Pazar',
}

const CONTENT_TYPES = [
  { id: 'image',    label: 'Görsel', icon: '🖼️' },
  { id: 'carousel', label: 'Carousel', icon: '📱' },
  { id: 'video',    label: 'Video', icon: '🎬' },
]

const PLATFORMS = [
  { id: 'instagram', label: 'Instagram' },
  { id: 'tiktok',    label: 'TikTok' },
  { id: 'linkedin',  label: 'LinkedIn' },
  { id: 'facebook',  label: 'Facebook' },
  { id: 'youtube',   label: 'YouTube' },
  { id: 'twitter',   label: 'Twitter / X' },
  { id: 'pinterest', label: 'Pinterest' },
]

const HOURS = Array.from({ length: 18 }, (_, i) => {
  const h = i + 6 // 06:00 → 23:00
  return `${String(h).padStart(2, '0')}:00`
})

// ─── Step indicator ───────────────────────────────────────────────────────────

function WizardStepIndicator({ step }: { step: WizardStep }) {
  const steps = ['Konular', 'Platformlar', 'Program', 'Özet']
  return (
    <div className="flex items-center gap-2 mb-8">
      {steps.map((label, i) => {
        const n = (i + 1) as WizardStep
        const done = step > n
        const active = step === n
        return (
          <div key={n} className="flex items-center gap-2">
            <div className={cn(
              'w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors',
              done   ? 'bg-blue-100 text-blue-700' :
              active ? 'bg-blue-600 text-white'    : 'bg-gray-100 text-gray-400'
            )}>
              {done ? <Check className="w-3.5 h-3.5" /> : n}
            </div>
            <span className={cn(
              'text-sm hidden sm:block',
              active ? 'text-gray-800 font-medium' : 'text-gray-400'
            )}>
              {label}
            </span>
            {i < steps.length - 1 && (
              <div className={cn('w-6 h-px mx-1', done ? 'bg-blue-300' : 'bg-gray-200')} />
            )}
          </div>
        )
      })}
    </div>
  )
}

// ─── Tag input ────────────────────────────────────────────────────────────────

function TopicInput({
  topics,
  onChange,
}: {
  topics: string[]
  onChange: (t: string[]) => void
}) {
  const [input, setInput] = useState('')

  function add(val: string) {
    const v = val.trim()
    if (!v || topics.includes(v)) return
    onChange([...topics, v])
    setInput('')
  }

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-2 min-h-[40px] p-2 border border-gray-200 rounded-lg bg-white">
        {topics.map((t) => (
          <Badge key={t} variant="secondary" className="gap-1 text-sm">
            {t}
            <button
              onClick={() => onChange(topics.filter((x) => x !== t))}
              className="ml-0.5 text-gray-400 hover:text-gray-700"
            >
              ×
            </button>
          </Badge>
        ))}
      </div>
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ',') { e.preventDefault(); add(input) }
          }}
          placeholder="Konu yazın, Enter ile ekleyin..."
          className="flex-1 text-sm px-3 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-400"
        />
        <Button variant="outline" size="sm" onClick={() => add(input)}>Ekle</Button>
      </div>
      {topics.length < 3 && (
        <p className="text-xs text-amber-600">En az 3 konu ekleyin.</p>
      )}
    </div>
  )
}

// ─── Summary dashboard ────────────────────────────────────────────────────────

function SummaryDashboard({
  config,
  upcoming,
  onToggle,
  onEdit,
  toggling,
}: {
  config: AutopostingConfig
  upcoming: UpcomingPost[]
  onToggle: () => void
  onEdit: () => void
  toggling: boolean
}) {
  const freq = FREQUENCIES.find((f) => f.id === config.frequency)

  return (
    <div className="space-y-5">
      {/* Status card */}
      <div className={cn(
        'flex items-center justify-between p-5 rounded-2xl border-2 transition-colors',
        config.is_enabled ? 'border-emerald-200 bg-emerald-50' : 'border-gray-200 bg-gray-50'
      )}>
        <div className="flex items-center gap-3">
          <div className={cn(
            'w-10 h-10 rounded-xl flex items-center justify-center',
            config.is_enabled ? 'bg-emerald-100' : 'bg-gray-200'
          )}>
            <Zap className={cn('w-5 h-5', config.is_enabled ? 'text-emerald-600' : 'text-gray-400')} />
          </div>
          <div>
            <p className="font-semibold text-gray-900">Otomatik Yayın</p>
            <p className={cn('text-sm', config.is_enabled ? 'text-emerald-600' : 'text-gray-400')}>
              {config.is_enabled ? 'Aktif' : 'Pasif'}
            </p>
          </div>
        </div>
        {toggling ? (
          <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
        ) : (
          <Switch checked={config.is_enabled} onCheckedChange={onToggle} />
        )}
      </div>

      {/* Config summary */}
      <div className="grid grid-cols-2 gap-4">
        <div className="p-4 bg-white border border-gray-100 rounded-xl space-y-1">
          <p className="text-xs text-gray-400 uppercase tracking-wide">Sıklık</p>
          <p className="font-semibold text-gray-800">{freq?.label ?? config.frequency}</p>
          <p className="text-xs text-gray-400">{freq?.desc}</p>
        </div>
        <div className="p-4 bg-white border border-gray-100 rounded-xl space-y-1">
          <p className="text-xs text-gray-400 uppercase tracking-wide">Platformlar</p>
          <p className="font-semibold text-gray-800">{config.platforms.length} platform</p>
          <p className="text-xs text-gray-400">{config.platforms.join(', ')}</p>
        </div>
        <div className="p-4 bg-white border border-gray-100 rounded-xl space-y-2 col-span-2">
          <p className="text-xs text-gray-400 uppercase tracking-wide">Zaman Dilimleri</p>
          <div className="flex flex-wrap gap-2">
            {config.time_slots.map((slot, i) => (
              <span key={i} className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded-lg">
                {DAY_TR_FULL[slot.day] ?? slot.day} {slot.time}
              </span>
            ))}
          </div>
        </div>
        <div className="p-4 bg-white border border-gray-100 rounded-xl space-y-2 col-span-2">
          <p className="text-xs text-gray-400 uppercase tracking-wide">Konular</p>
          <div className="flex flex-wrap gap-1.5">
            {config.topics.map((t) => (
              <Badge key={t} variant="secondary" className="text-xs">{t}</Badge>
            ))}
          </div>
        </div>
      </div>

      {/* Upcoming posts */}
      {upcoming.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-semibold text-gray-700">Bir Sonraki Otomatik Yayınlar</p>
          {upcoming.map((post) => (
            <div key={post.id} className="flex items-center gap-3 p-3 bg-white border border-gray-100 rounded-xl">
              <div className="w-10 h-10 bg-gray-100 rounded-lg flex items-center justify-center text-lg flex-shrink-0">
                {post.content_type === 'image' ? '🖼️' : post.content_type === 'carousel' ? '📱' : '🎬'}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-gray-700 truncate">{post.caption ?? post.content_type}</p>
                <p className="text-xs text-gray-400">
                  {new Date(post.scheduled_at).toLocaleString('tr-TR', {
                    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit'
                  })}
                </p>
              </div>
              <Badge variant="secondary" className="text-xs flex-shrink-0">Zamanlandı</Badge>
            </div>
          ))}
        </div>
      )}

      <Button variant="outline" className="w-full" onClick={onEdit}>
        Ayarları Düzenle
      </Button>
    </div>
  )
}

// ─── Main page ─────────────────────────────────────────────────────────────────

export default function OtomatikYayinPage() {
  const currentBrand = useAppStore((s) => s.currentBrand)

  const [loading, setLoading] = useState(true)
  const [config, setConfig] = useState<AutopostingConfig | null>(null)
  const [upcoming, setUpcoming] = useState<UpcomingPost[]>([])
  const [toggling, setToggling] = useState(false)

  // Wizard state
  const [wizardOpen, setWizardOpen] = useState(false)
  const [step, setStep] = useState<WizardStep>(1)
  const [saving, setSaving] = useState(false)
  const [loadingIdeas, setLoadingIdeas] = useState(false)
  const [suggestedTopics, setSuggestedTopics] = useState<string[]>([])

  // Wizard form
  const [topics, setTopics] = useState<string[]>([])
  const [platforms, setPlatforms] = useState<string[]>(['instagram'])
  const [frequency, setFrequency] = useState('3x_weekly')
  const [timeSlots, setTimeSlots] = useState(TIME_SLOTS_BY_FREQ['3x_weekly'])
  const [contentTypes, setContentTypes] = useState<string[]>(['image'])

  // ── Load config ──────────────────────────────────────────────────────────────

  const loadData = useCallback(async () => {
    if (!currentBrand?.id) { setLoading(false); return }
    const [cfgRes, upRes] = await Promise.all([
      api.get<AutopostingConfig>(`/autoposting/config?brand_id=${currentBrand.id}`),
      api.get<UpcomingPost[]>(`/autoposting/upcoming?brand_id=${currentBrand.id}`),
    ])
    if (cfgRes.success) setConfig(cfgRes.data ?? null)
    if (upRes.success && upRes.data) setUpcoming(upRes.data)
    setLoading(false)
  }, [currentBrand?.id])

  useEffect(() => { loadData() }, [loadData])

  // ── Open wizard (prefill if editing) ─────────────────────────────────────────

  function openWizard() {
    if (config) {
      setTopics(config.topics)
      setPlatforms(config.platforms)
      setFrequency(config.frequency)
      setTimeSlots(config.time_slots)
      setContentTypes(config.content_types)
    }
    setStep(1)
    setSuggestedTopics([])
    setWizardOpen(true)
  }

  // ── Suggest topics via AI ─────────────────────────────────────────────────────

  async function fetchTopicIdeas() {
    if (!currentBrand?.id) return
    setLoadingIdeas(true)
    const res = await api.post<{ ideas: string[] }>('/ai/suggest-ideas', {
      brand_id: currentBrand.id,
      content_category: 'product',
      count: 5,
    })
    if (res.success && res.data?.ideas) setSuggestedTopics(res.data.ideas)
    else toast.error('Konular alınamadı')
    setLoadingIdeas(false)
  }

  // ── Frequency change → reset slots ───────────────────────────────────────────

  function changeFrequency(f: string) {
    setFrequency(f)
    setTimeSlots(TIME_SLOTS_BY_FREQ[f] ?? [])
  }

  function updateSlotTime(idx: number, time: string) {
    setTimeSlots((prev) => prev.map((s, i) => i === idx ? { ...s, time } : s))
  }

  // ── Save config ───────────────────────────────────────────────────────────────

  async function handleSave() {
    if (!currentBrand?.id) return
    if (topics.length < 3) { toast.error('En az 3 konu gerekli'); return }
    if (platforms.length === 0) { toast.error('En az 1 platform seçin'); return }

    setSaving(true)
    const res = await api.post<AutopostingConfig>('/autoposting/config', {
      brand_id: currentBrand.id,
      frequency,
      time_slots: timeSlots,
      content_types: contentTypes,
      content_categories: ['product', 'service', 'corporate'],
      topics,
      platforms,
    })

    if (res.success && res.data) {
      // Auto-enable on first save
      if (!config) {
        await api.post(`/autoposting/toggle?brand_id=${currentBrand.id}`, {})
      }
      setConfig(res.data)
      setWizardOpen(false)
      toast.success('Otomatik yayın yapılandırıldı!')
      loadData()
    } else {
      toast.error('Kaydedilemedi')
    }
    setSaving(false)
  }

  // ── Toggle enable/disable ─────────────────────────────────────────────────────

  async function handleToggle() {
    if (!currentBrand?.id || !config) return
    setToggling(true)
    const res = await api.post<{ is_enabled: boolean }>(`/autoposting/toggle?brand_id=${currentBrand.id}`, {})
    if (res.success && res.data) {
      setConfig((prev) => prev ? { ...prev, is_enabled: res.data!.is_enabled } : prev)
      toast.success(res.data.is_enabled ? 'Otomatik yayın aktif' : 'Otomatik yayın durduruldu')
    }
    setToggling(false)
  }

  // ── Render ────────────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
      </div>
    )
  }

  // ── No config → show setup button ────────────────────────────────────────────

  if (!config && !wizardOpen) {
    return (
      <div className="p-8 max-w-xl mx-auto">
        <div className="flex flex-col items-center justify-center py-16 gap-5 text-center">
          <div className="w-16 h-16 bg-blue-50 rounded-2xl flex items-center justify-center">
            <Zap className="w-8 h-8 text-blue-500" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">Otomatik Yayın</h1>
            <p className="text-sm text-gray-500 mt-1 max-w-sm">
              Yapay zeka ile belirlediğiniz konularda otomatik içerik üretsin ve yayınlasın.
            </p>
          </div>
          <Button onClick={openWizard} size="lg" className="gap-2">
            <Zap className="w-4 h-4" />
            Otomatik Yayın Kur
          </Button>
        </div>
      </div>
    )
  }

  // ── Config exists → dashboard ─────────────────────────────────────────────────

  if (config && !wizardOpen) {
    return (
      <div className="p-8 max-w-2xl mx-auto">
        <div className="mb-6">
          <h1 className="text-xl font-bold text-gray-900">Otomatik Yayın</h1>
          <p className="text-sm text-gray-500 mt-0.5">AI otomatik içerik üretir ve yayınlar</p>
        </div>
        <SummaryDashboard
          config={config}
          upcoming={upcoming}
          onToggle={handleToggle}
          onEdit={openWizard}
          toggling={toggling}
        />
      </div>
    )
  }

  // ── Wizard ────────────────────────────────────────────────────────────────────

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-gray-900">Otomatik Yayın Kurulumu</h1>
        <button
          onClick={() => setWizardOpen(false)}
          className="text-sm text-gray-400 hover:text-gray-600"
        >
          İptal
        </button>
      </div>

      <WizardStepIndicator step={step} />

      {/* ── Step 1: Konular ─────────────────────────────────────────────────── */}
      {step === 1 && (
        <div className="space-y-5">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Ne hakkında paylaşım yapmak istiyorsunuz?</h2>
            <p className="text-sm text-gray-500 mt-1">Konular AI&apos;ın içerik üretirken kullanacağı rehberdir.</p>
          </div>

          <TopicInput topics={topics} onChange={setTopics} />

          {/* AI suggestions */}
          <div className="space-y-2">
            <Button
              variant="outline"
              size="sm"
              onClick={fetchTopicIdeas}
              disabled={loadingIdeas}
              className="gap-2"
            >
              {loadingIdeas ? <Loader2 className="w-4 h-4 animate-spin" /> : <Lightbulb className="w-4 h-4" />}
              Bana konu öner
            </Button>

            {suggestedTopics.length > 0 && (
              <div className="flex flex-wrap gap-2 mt-2">
                {suggestedTopics.map((t) => (
                  <button
                    key={t}
                    onClick={() => {
                      if (!topics.includes(t)) setTopics([...topics, t])
                    }}
                    className={cn(
                      'text-sm px-3 py-1.5 rounded-lg border transition-colors',
                      topics.includes(t)
                        ? 'bg-blue-600 text-white border-blue-600'
                        : 'border-blue-200 text-blue-700 bg-blue-50 hover:bg-blue-100'
                    )}
                  >
                    {topics.includes(t) ? <Check className="w-3 h-3 inline mr-1" /> : '+ '}{t}
                  </button>
                ))}
              </div>
            )}
          </div>

          <Button
            onClick={() => setStep(2)}
            disabled={topics.length < 3}
            className="w-full gap-2"
          >
            Devam Et <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      )}

      {/* ── Step 2: Platformlar ─────────────────────────────────────────────── */}
      {step === 2 && (
        <div className="space-y-5">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Hangi platformlarda yayınlansın?</h2>
            <p className="text-sm text-gray-500 mt-1">Birden fazla platform seçebilirsiniz.</p>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {PLATFORMS.map((p) => {
              const selected = platforms.includes(p.id)
              return (
                <button
                  key={p.id}
                  onClick={() => setPlatforms((prev) =>
                    selected ? prev.filter((x) => x !== p.id) : [...prev, p.id]
                  )}
                  className={cn(
                    'flex items-center gap-3 p-4 rounded-xl border-2 text-left transition-all',
                    selected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-300'
                  )}
                >
                  <div className={cn(
                    'w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm flex-shrink-0',
                    selected ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-500'
                  )}>
                    {p.label[0]}
                  </div>
                  <span className="text-sm font-medium text-gray-700">{p.label}</span>
                  {selected && <Check className="w-4 h-4 text-blue-600 ml-auto" />}
                </button>
              )
            })}
          </div>

          <div className="flex gap-3">
            <Button variant="outline" onClick={() => setStep(1)} className="flex-1">← Geri</Button>
            <Button
              onClick={() => setStep(3)}
              disabled={platforms.length === 0}
              className="flex-1 gap-2"
            >
              Devam Et <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}

      {/* ── Step 3: Program ─────────────────────────────────────────────────── */}
      {step === 3 && (
        <div className="space-y-6">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Yayın programı</h2>
            <p className="text-sm text-gray-500 mt-1">Ne sıklıkla ve hangi saatlerde yayınlansın?</p>
          </div>

          {/* Frequency */}
          <div className="space-y-2">
            <Label>Sıklık</Label>
            <div className="grid grid-cols-3 gap-3">
              {FREQUENCIES.map((f) => (
                <button
                  key={f.id}
                  onClick={() => changeFrequency(f.id)}
                  className={cn(
                    'flex flex-col items-center gap-1 p-4 rounded-xl border-2 text-center transition-all',
                    frequency === f.id ? 'border-blue-500 bg-blue-50' : 'border-gray-200 hover:border-blue-300'
                  )}
                >
                  <span className="text-sm font-bold text-gray-800">{f.label}</span>
                  <span className="text-xs text-gray-400">{f.desc}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Time slots */}
          <div className="space-y-2">
            <Label>Yayın Saatleri</Label>
            <div className="space-y-2">
              {timeSlots.map((slot, i) => (
                <div key={i} className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl">
                  <span className="text-sm font-medium text-gray-700 w-24">
                    {DAY_TR_FULL[slot.day] ?? slot.day}
                  </span>
                  <select
                    value={slot.time}
                    onChange={(e) => updateSlotTime(i, e.target.value)}
                    className="text-sm border border-gray-200 rounded-lg px-2 py-1 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                  >
                    {HOURS.map((h) => (
                      <option key={h} value={h}>{h}</option>
                    ))}
                  </select>
                </div>
              ))}
            </div>
          </div>

          {/* Content types */}
          <div className="space-y-2">
            <Label>İçerik Tipleri</Label>
            <div className="flex gap-2">
              {CONTENT_TYPES.map((ct) => {
                const selected = contentTypes.includes(ct.id)
                return (
                  <button
                    key={ct.id}
                    onClick={() => setContentTypes((prev) =>
                      selected && prev.length > 1
                        ? prev.filter((x) => x !== ct.id)
                        : selected ? prev : [...prev, ct.id]
                    )}
                    className={cn(
                      'flex items-center gap-2 px-4 py-2 rounded-xl border-2 text-sm transition-all',
                      selected ? 'border-blue-500 bg-blue-50 text-blue-700' : 'border-gray-200 text-gray-600 hover:border-blue-300'
                    )}
                  >
                    <span>{ct.icon}</span> {ct.label}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Telegram bilgisi */}
          <div className="flex items-start gap-3 p-4 bg-blue-50 border border-blue-200 rounded-xl">
            <MessageCircle className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-blue-700">
              İçerik onayı için Telegram bildirimleri{' '}
              <a href="/ayarlar" className="font-semibold underline">Ayarlar</a> sayfasından yapılandırılır.
            </p>
          </div>

          <div className="flex gap-3">
            <Button variant="outline" onClick={() => setStep(2)} className="flex-1">← Geri</Button>
            <Button onClick={() => setStep(4)} className="flex-1 gap-2">
              Devam Et <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}

      {/* ── Step 4: Özet ────────────────────────────────────────────────────── */}
      {step === 4 && (
        <div className="space-y-5">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Özet</h2>
            <p className="text-sm text-gray-500 mt-1">Ayarlarınızı gözden geçirin.</p>
          </div>

          <div className="space-y-3">
            {/* Topics */}
            <div className="p-4 bg-white border border-gray-100 rounded-xl space-y-2">
              <p className="text-xs text-gray-400 uppercase tracking-wide">Konular ({topics.length})</p>
              <div className="flex flex-wrap gap-1.5">
                {topics.map((t) => <Badge key={t} variant="secondary" className="text-xs">{t}</Badge>)}
              </div>
            </div>

            {/* Platforms */}
            <div className="p-4 bg-white border border-gray-100 rounded-xl space-y-2">
              <p className="text-xs text-gray-400 uppercase tracking-wide">Platformlar</p>
              <p className="text-sm font-medium text-gray-700">{platforms.join(', ')}</p>
            </div>

            {/* Schedule */}
            <div className="p-4 bg-white border border-gray-100 rounded-xl space-y-2">
              <p className="text-xs text-gray-400 uppercase tracking-wide">Program</p>
              <p className="text-sm font-medium text-gray-700">
                {FREQUENCIES.find((f) => f.id === frequency)?.label} — {timeSlots.map((s) => `${DAY_TR[s.day]} ${s.time}`).join(', ')}
              </p>
            </div>

            {/* Content types */}
            <div className="p-4 bg-white border border-gray-100 rounded-xl space-y-2">
              <p className="text-xs text-gray-400 uppercase tracking-wide">İçerik Tipleri</p>
              <p className="text-sm font-medium text-gray-700">
                {contentTypes.map((c) => CONTENT_TYPES.find((t) => t.id === c)?.label).join(', ')}
              </p>
            </div>

          </div>

          <div className="flex gap-3">
            <Button variant="outline" onClick={() => setStep(3)} className="flex-1">← Geri</Button>
            <Button onClick={handleSave} disabled={saving} className="flex-1 gap-2 bg-emerald-600 hover:bg-emerald-700">
              {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
              Otomatik Yayını Başlat
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
