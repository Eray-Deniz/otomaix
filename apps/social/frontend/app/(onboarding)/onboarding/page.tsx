'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { analytics } from '@/lib/analytics'

// ─── Types ────────────────────────────────────────────────────────────────────

type Step = 1 | 2 | 3 | 4 | 5 | 6 | 7

interface BrandData {
  name: string
  description: string
  websiteUrl: string
  sector: string
  colors: string[]
  tonality: string
}

interface OnboardingState {
  websiteUrl: string
  brand: BrandData
  userType: string
  goals: string[]
  connectedPlatforms: string[]
  previewPosts: string[]
}

// ─── Constants ────────────────────────────────────────────────────────────────

interface Sector {
  id: string
  slug: string
  display_name: string
}

const USER_TYPES = [
  { key: 'small_business', label: 'Küçük İşletme', icon: '🏪', desc: '1-10 çalışan' },
  { key: 'agency', label: 'Ajans', icon: '🏢', desc: 'Birden fazla müşteri yönetimi' },
  { key: 'freelancer', label: 'Serbest Çalışan', icon: '💼', desc: 'Bağımsız profesyonel' },
  { key: 'enterprise', label: 'Orta/Büyük Şirket', icon: '🏭', desc: '50+ çalışan' },
]

const GOALS = [
  'Daha fazla takipçi kazanmak',
  'Daha fazla müşteri çekmek',
  'Marka bilinirliğini artırmak',
  'Ürün/hizmet tanıtımı yapmak',
  'Topluluk oluşturmak',
  'Rakiplerden öne çıkmak',
]

const PLATFORMS = [
  { key: 'instagram', label: 'Instagram', color: '#E1306C' },
  { key: 'tiktok', label: 'TikTok', color: '#000000' },
  { key: 'linkedin', label: 'LinkedIn', color: '#0A66C2' },
  { key: 'facebook', label: 'Facebook', color: '#1877F2' },
  { key: 'youtube', label: 'YouTube', color: '#FF0000' },
  { key: 'twitter', label: 'X (Twitter)', color: '#000000' },
]

const STEP_LABELS = [
  'Hoş Geldiniz',
  'Web Siteniz',
  'Marka Bilgileri',
  'Kullanıcı Tipi',
  'Hedefler',
  'Platformlar',
  'Hazır!',
]

// ─── Step Indicator ───────────────────────────────────────────────────────────

function StepIndicator({ current, total }: { current: Step; total: number }) {
  return (
    <div className="flex items-center gap-2 mb-8">
      {Array.from({ length: total }, (_, i) => i + 1).map((s) => (
        <div key={s} className="flex items-center gap-2">
          <div
            className={`w-2.5 h-2.5 rounded-full transition-all duration-300 ${
              s < current
                ? 'bg-emerald-500'
                : s === current
                ? 'bg-emerald-400 ring-2 ring-emerald-400/30 w-3.5 h-3.5'
                : 'bg-slate-700'
            }`}
          />
          {s < total && (
            <div className={`w-6 h-px ${s < current ? 'bg-emerald-500' : 'bg-slate-700'}`} />
          )}
        </div>
      ))}
      <span className="text-slate-400 text-xs ml-2">
        {current}/{total} — {STEP_LABELS[current - 1]}
      </span>
    </div>
  )
}

// ─── Card wrapper ─────────────────────────────────────────────────────────────

function Card({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div
      className={`w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl p-8 shadow-2xl ${className}`}
    >
      {children}
    </div>
  )
}

// ─── Main Component ───────────────────────────────────────────────────────────

export default function OnboardingPage() {
  const router = useRouter()
  const { currentWorkspace } = useAppStore()

  const [step, setStep] = useState<Step>(1)
  const [analyzing, setAnalyzing] = useState(false)
  const [creating, setCreating] = useState(false)
  const [sectors, setSectors] = useState<Sector[]>([])

  useEffect(() => { analytics.onboardingStarted() }, []) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    api.get<Sector[]>('/sectors').then((res) => {
      if (res.success && res.data) setSectors(res.data)
    })
  }, [])

  const [state, setState] = useState<OnboardingState>({
    websiteUrl: '',
    brand: {
      name: '',
      description: '',
      websiteUrl: '',
      sector: '',
      colors: ['#3B82F6', '#10B981', '#F59E0B'],
      tonality: 'professional',
    },
    userType: '',
    goals: [],
    connectedPlatforms: [],
    previewPosts: [],
  })

  function next() {
    analytics.onboardingStepCompleted(step)
    setStep((s) => Math.min(s + 1, 7) as Step)
  }

  function back() {
    setStep((s) => Math.max(s - 1, 1) as Step)
  }

  function updateBrand(patch: Partial<BrandData>) {
    setState((prev) => ({ ...prev, brand: { ...prev.brand, ...patch } }))
  }

  function toggleGoal(goal: string) {
    setState((prev) => ({
      ...prev,
      goals: prev.goals.includes(goal)
        ? prev.goals.filter((g) => g !== goal)
        : [...prev.goals, goal],
    }))
  }

  function togglePlatform(key: string) {
    setState((prev) => ({
      ...prev,
      connectedPlatforms: prev.connectedPlatforms.includes(key)
        ? prev.connectedPlatforms.filter((p) => p !== key)
        : [...prev.connectedPlatforms, key],
    }))
  }

  // Step 2 — Analyze website
  async function analyzeWebsite() {
    if (!state.websiteUrl.trim()) return
    setAnalyzing(true)
    try {
      const res = await api.post<{
        name: string
        description: string
        sector: string
        colors: string[]
        tonality: string
      }>('/ai/analyze-website', { url: state.websiteUrl })

      if (res.success && res.data) {
        updateBrand({
          name: res.data.name || state.brand.name,
          description: res.data.description || state.brand.description,
          sector: res.data.sector || state.brand.sector,
          colors: res.data.colors?.length ? res.data.colors : state.brand.colors,
          tonality: res.data.tonality || state.brand.tonality,
          websiteUrl: state.websiteUrl,
        })
        toast.success('Marka bilgileri otomatik dolduruldu')
        next()
      } else {
        toast.error('Analiz başarısız, bilgileri manuel girin')
        next()
      }
    } catch {
      toast.error('Web sitesine ulaşılamadı')
      next()
    } finally {
      setAnalyzing(false)
    }
  }

  // Final step — create brand and finish
  async function finishOnboarding() {
    if (!currentWorkspace?.id) {
      toast.error('Çalışma alanı bulunamadı')
      return
    }
    setCreating(true)
    try {
      const res = await api.post<{ id: string }>('/brands', {
        workspace_id: currentWorkspace.id,
        name: state.brand.name || 'Yeni Marka',
        description: state.brand.description || null,
        website_url: state.brand.websiteUrl || null,
        sector: state.brand.sector || null,
      })

      if (res.success && res.data?.id) {
        // Save brand kit
        await api.patch(`/brands/${res.data.id}/kit`, {
          colors: state.brand.colors,
          tonality: state.brand.tonality,
        })
        analytics.onboardingCompleted()
        toast.success('Markanız oluşturuldu!')
        router.push('/dashboard')
      } else if (res.error === 'plan_limit_reached' && res.plan_limit) {
        toast.error(res.plan_limit.message)
      } else {
        toast.error(res.error || 'Marka oluşturulamadı')
      }
    } catch {
      toast.error('Bir hata oluştu')
    } finally {
      setCreating(false)
    }
  }

  // ─── Step renders ────────────────────────────────────────────────────────────

  if (step === 1) {
    return (
      <Card>
        <StepIndicator current={1} total={7} />
        <div className="text-center">
          <div className="w-16 h-16 rounded-2xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center mx-auto mb-6">
            <span className="text-3xl">👋</span>
          </div>
          <h1 className="text-2xl font-bold text-white mb-3">Otomaix&apos;e Hoş Geldiniz!</h1>
          <p className="text-slate-400 mb-8 leading-relaxed">
            Markanızı birlikte kuralım. Bu kısa kurulum wizard&apos;ı size özel içerik üretim deneyimi
            oluşturacak. Sadece birkaç dakikanızı alacak.
          </p>
          <div className="grid grid-cols-3 gap-3 mb-8">
            {[
              { icon: '🎨', label: 'Marka kimliği' },
              { icon: '🤖', label: 'AI içerik üretimi' },
              { icon: '📅', label: 'Otomatik zamanlama' },
            ].map((item) => (
              <div key={item.label} className="bg-slate-800 rounded-xl p-3 text-center">
                <div className="text-2xl mb-1">{item.icon}</div>
                <div className="text-slate-300 text-xs">{item.label}</div>
              </div>
            ))}
          </div>
          <button
            onClick={next}
            className="w-full bg-emerald-500 hover:bg-emerald-400 text-white font-semibold py-3 rounded-xl transition-colors"
          >
            Başlayalım →
          </button>
        </div>
      </Card>
    )
  }

  if (step === 2) {
    return (
      <Card>
        <StepIndicator current={2} total={7} />
        <h2 className="text-xl font-bold text-white mb-2">Web Siteniz</h2>
        <p className="text-slate-400 text-sm mb-6">
          Web sitenizi girin, marka bilgilerinizi otomatik dolduralım.
        </p>

        <div className="mb-6">
          <label className="block text-slate-300 text-sm font-medium mb-2">Web Sitesi URL</label>
          <div className="flex gap-2">
            <input
              type="url"
              placeholder="https://example.com"
              value={state.websiteUrl}
              onChange={(e) => setState((prev) => ({ ...prev, websiteUrl: e.target.value }))}
              onKeyDown={(e) => e.key === 'Enter' && analyzeWebsite()}
              className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
            />
            <button
              onClick={analyzeWebsite}
              disabled={analyzing || !state.websiteUrl.trim()}
              className="bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium px-5 py-3 rounded-xl transition-colors whitespace-nowrap flex items-center gap-2"
            >
              {analyzing ? (
                <>
                  <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Analiz ediliyor...
                </>
              ) : (
                'Analiz Et'
              )}
            </button>
          </div>
          {analyzing && (
            <p className="text-emerald-400 text-xs mt-2 flex items-center gap-1">
              <svg className="animate-spin h-3 w-3" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Markanız analiz ediliyor...
            </p>
          )}
        </div>

        <div className="flex gap-3">
          <button
            onClick={back}
            className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium py-3 rounded-xl transition-colors"
          >
            ← Geri
          </button>
          <button
            onClick={next}
            className="flex-1 text-slate-400 hover:text-white text-sm py-3 rounded-xl transition-colors"
          >
            Şimdilik Geç →
          </button>
        </div>
      </Card>
    )
  }

  if (step === 3) {
    return (
      <Card className="max-w-xl">
        <StepIndicator current={3} total={7} />
        <h2 className="text-xl font-bold text-white mb-2">Marka Bilgileri</h2>
        <p className="text-slate-400 text-sm mb-6">
          {state.brand.name ? 'Web sitenizden doldurulan bilgileri kontrol edin.' : 'Marka bilgilerinizi girin.'}
        </p>

        <div className="space-y-4">
          <div>
            <label className="block text-slate-300 text-sm font-medium mb-1.5">Marka Adı *</label>
            <input
              type="text"
              placeholder="Markanızın adı"
              value={state.brand.name}
              onChange={(e) => updateBrand({ name: e.target.value })}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-slate-300 text-sm font-medium mb-1.5">Açıklama</label>
            <textarea
              placeholder="Markanızı kısaca tanımlayın..."
              value={state.brand.description}
              onChange={(e) => updateBrand({ description: e.target.value })}
              rows={3}
              className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors resize-none"
            />
          </div>

          <div>
            <label className="block text-slate-300 text-sm font-medium mb-1.5">Sektör</label>
            <div className="grid grid-cols-3 gap-2">
              {sectors.map((s) => {
                const selected =
                  state.brand.sector === s.slug || state.brand.sector === s.display_name
                return (
                  <button
                    key={s.slug}
                    onClick={() => updateBrand({ sector: s.display_name })}
                    className={`py-2 px-3 rounded-lg text-sm font-medium transition-colors ${
                      selected
                        ? 'bg-emerald-500/20 border border-emerald-500 text-emerald-400'
                        : 'bg-slate-800 border border-slate-700 text-slate-300 hover:border-slate-600'
                    }`}
                  >
                    {s.display_name}
                  </button>
                )
              })}
            </div>
          </div>

          {/* Colors preview */}
          {state.brand.colors.length > 0 && (
            <div>
              <label className="block text-slate-300 text-sm font-medium mb-1.5">Marka Renkleri</label>
              <div className="flex gap-2">
                {state.brand.colors.map((color, i) => (
                  <div key={i} className="flex items-center gap-1.5">
                    <div
                      className="w-8 h-8 rounded-lg border border-slate-600"
                      style={{ backgroundColor: color }}
                    />
                    <span className="text-slate-400 text-xs font-mono">{color}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="flex gap-3 mt-6">
          <button
            onClick={back}
            className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium py-3 rounded-xl transition-colors"
          >
            ← Geri
          </button>
          <button
            onClick={next}
            disabled={!state.brand.name.trim()}
            className="flex-1 bg-emerald-500 hover:bg-emerald-400 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-colors"
          >
            Devam →
          </button>
        </div>
      </Card>
    )
  }

  if (step === 4) {
    return (
      <Card>
        <StepIndicator current={4} total={7} />
        <h2 className="text-xl font-bold text-white mb-2">Sizi Tanıyalım</h2>
        <p className="text-slate-400 text-sm mb-6">Hangisi sizi en iyi tanımlar?</p>

        <div className="grid grid-cols-2 gap-3 mb-6">
          {USER_TYPES.map((type) => (
            <button
              key={type.key}
              onClick={() => setState((prev) => ({ ...prev, userType: type.key }))}
              className={`p-4 rounded-xl border text-left transition-all ${
                state.userType === type.key
                  ? 'bg-emerald-500/10 border-emerald-500 ring-1 ring-emerald-500/30'
                  : 'bg-slate-800 border-slate-700 hover:border-slate-600'
              }`}
            >
              <div className="text-2xl mb-2">{type.icon}</div>
              <div className="text-white font-medium text-sm">{type.label}</div>
              <div className="text-slate-400 text-xs mt-0.5">{type.desc}</div>
            </button>
          ))}
        </div>

        <div className="flex gap-3">
          <button
            onClick={back}
            className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium py-3 rounded-xl transition-colors"
          >
            ← Geri
          </button>
          {state.userType ? (
            <button
              onClick={next}
              className="flex-1 bg-emerald-500 hover:bg-emerald-400 text-white font-semibold py-3 rounded-xl transition-colors"
            >
              Devam →
            </button>
          ) : (
            <button
              onClick={next}
              className="flex-1 text-slate-400 hover:text-white text-sm py-3 rounded-xl transition-colors"
            >
              Daha Sonra Atla →
            </button>
          )}
        </div>
      </Card>
    )
  }

  if (step === 5) {
    return (
      <Card>
        <StepIndicator current={5} total={7} />
        <h2 className="text-xl font-bold text-white mb-2">Sosyal Medya Hedefleriniz</h2>
        <p className="text-slate-400 text-sm mb-6">
          Önümüzdeki 30 günde ne yapmak istiyorsunuz? (Birden fazla seçebilirsiniz)
        </p>

        <div className="space-y-2 mb-6">
          {GOALS.map((goal) => {
            const selected = state.goals.includes(goal)
            return (
              <button
                key={goal}
                onClick={() => toggleGoal(goal)}
                className={`w-full flex items-center gap-3 p-3.5 rounded-xl border text-left transition-all ${
                  selected
                    ? 'bg-emerald-500/10 border-emerald-500 text-emerald-300'
                    : 'bg-slate-800 border-slate-700 text-slate-300 hover:border-slate-600'
                }`}
              >
                <div
                  className={`w-5 h-5 rounded-md border flex items-center justify-center flex-shrink-0 transition-colors ${
                    selected ? 'bg-emerald-500 border-emerald-500' : 'border-slate-600'
                  }`}
                >
                  {selected && (
                    <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </div>
                <span className="text-sm font-medium">{goal}</span>
              </button>
            )
          })}
        </div>

        <div className="flex gap-3">
          <button
            onClick={back}
            className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium py-3 rounded-xl transition-colors"
          >
            ← Geri
          </button>
          <button
            onClick={next}
            className="flex-1 bg-emerald-500 hover:bg-emerald-400 text-white font-semibold py-3 rounded-xl transition-colors"
          >
            Devam →
          </button>
        </div>
      </Card>
    )
  }

  if (step === 6) {
    return (
      <Card className="max-w-xl">
        <StepIndicator current={6} total={7} />
        <h2 className="text-xl font-bold text-white mb-2">Platform Bağlantısı</h2>
        <p className="text-slate-400 text-sm mb-6">
          Hangi platformlarda paylaşım yapıyorsunuz? (İlerleyen adımda bağlantı yapacaksınız)
        </p>

        <div className="grid grid-cols-2 gap-3 mb-4">
          {PLATFORMS.map((p) => {
            const selected = state.connectedPlatforms.includes(p.key)
            return (
              <button
                key={p.key}
                onClick={() => togglePlatform(p.key)}
                className={`flex items-center gap-3 p-4 rounded-xl border transition-all ${
                  selected
                    ? 'bg-slate-700 border-slate-500 ring-1 ring-slate-400/20'
                    : 'bg-slate-800 border-slate-700 hover:border-slate-600'
                }`}
              >
                <div
                  className="w-8 h-8 rounded-lg flex items-center justify-center text-white text-xs font-bold flex-shrink-0"
                  style={{ backgroundColor: p.color === '#000000' ? '#1a1a1a' : p.color }}
                >
                  {p.label[0]}
                </div>
                <span className="text-white text-sm font-medium">{p.label}</span>
                {selected && (
                  <svg className="w-4 h-4 text-emerald-400 ml-auto flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
                  </svg>
                )}
              </button>
            )
          })}
        </div>

        <p className="text-slate-500 text-xs text-center mb-6">
          Platform bağlantısı Marka Ayarları &gt; Sosyal Hesaplar bölümünden yapılabilir.
        </p>

        <div className="flex gap-3">
          <button
            onClick={back}
            className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium py-3 rounded-xl transition-colors"
          >
            ← Geri
          </button>
          <button
            onClick={next}
            className="flex-1 bg-emerald-500 hover:bg-emerald-400 text-white font-semibold py-3 rounded-xl transition-colors"
          >
            {state.connectedPlatforms.length > 0 ? 'Devam →' : 'Şimdilik Geç →'}
          </button>
        </div>
      </Card>
    )
  }

  // Step 7 — Done!
  return (
    <Card className="max-w-xl">
      <StepIndicator current={7} total={7} />

      <div className="text-center mb-8">
        <div className="text-5xl mb-4">🎉</div>
        <h2 className="text-2xl font-bold text-white mb-3">Her Şey Hazır!</h2>
        <p className="text-slate-400 leading-relaxed">
          <strong className="text-white">{state.brand.name || 'Markanız'}</strong> başarıyla oluşturuldu.
          Şimdi AI destekli içerik üretmeye başlayabilirsiniz.
        </p>
      </div>

      {/* Summary */}
      <div className="bg-slate-800 rounded-xl p-4 mb-6 space-y-2.5">
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-400">Marka Adı</span>
          <span className="text-white font-medium">{state.brand.name || '—'}</span>
        </div>
        {state.brand.sector && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">Sektör</span>
            <span className="text-white font-medium">
              {sectors.find((s) => s.slug === state.brand.sector || s.display_name === state.brand.sector)?.display_name || state.brand.sector}
            </span>
          </div>
        )}
        {USER_TYPES.find((t) => t.key === state.userType) && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">Kullanıcı Tipi</span>
            <span className="text-white font-medium">
              {USER_TYPES.find((t) => t.key === state.userType)?.label}
            </span>
          </div>
        )}
        {state.goals.length > 0 && (
          <div className="flex items-start justify-between text-sm">
            <span className="text-slate-400">Hedefler</span>
            <span className="text-white font-medium text-right max-w-[60%]">
              {state.goals.length} hedef seçildi
            </span>
          </div>
        )}
        {state.connectedPlatforms.length > 0 && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">Platformlar</span>
            <span className="text-white font-medium">{state.connectedPlatforms.length} platform</span>
          </div>
        )}
        {state.brand.colors.length > 0 && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">Marka Renkleri</span>
            <div className="flex gap-1">
              {state.brand.colors.slice(0, 3).map((c, i) => (
                <div
                  key={i}
                  className="w-5 h-5 rounded-full border border-slate-600"
                  style={{ backgroundColor: c }}
                />
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Suggested first steps */}
      <div className="mb-6">
        <p className="text-slate-400 text-xs font-medium mb-3 uppercase tracking-wider">Başlangıç için öneriler</p>
        <div className="space-y-2">
          {[
            { icon: '🎨', text: 'Marka kimliğinizi tamamlayın', href: '/marka-ayarlari' },
            { icon: '✨', text: 'İlk içeriğinizi oluşturun', href: '/icerik-olustur' },
            { icon: '📅', text: 'Otomatik yayın kurun', href: '/otomatik-yayin' },
          ].map((item) => (
            <div key={item.href} className="flex items-center gap-3 bg-slate-800/50 rounded-lg p-3">
              <span className="text-lg">{item.icon}</span>
              <span className="text-slate-300 text-sm">{item.text}</span>
            </div>
          ))}
        </div>
      </div>

      <button
        onClick={finishOnboarding}
        disabled={creating}
        className="w-full bg-emerald-500 hover:bg-emerald-400 disabled:opacity-60 text-white font-semibold py-3.5 rounded-xl transition-colors flex items-center justify-center gap-2"
      >
        {creating ? (
          <>
            <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Oluşturuluyor...
          </>
        ) : (
          'Dashboard\'a Git →'
        )}
      </button>

      <button
        onClick={back}
        className="w-full mt-2 text-slate-500 hover:text-slate-400 text-sm py-2 transition-colors"
      >
        ← Geri Dön
      </button>
    </Card>
  )
}
