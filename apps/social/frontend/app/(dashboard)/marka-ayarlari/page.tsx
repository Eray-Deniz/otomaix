'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useRef, useState, useCallback } from 'react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import Image from 'next/image'
import { api } from '@/lib/api'
import { useAppStore } from '@/lib/store'
import { toast } from 'sonner'
import { Loader2, X, Upload, Check } from 'lucide-react'

// ─── Types ────────────────────────────────────────────────────────────────────

interface FontEntry {
  family: string
  weight: string
  letterCase: string
}

interface BrandKit {
  colors: string[]
  fonts: {
    title: FontEntry
    subtitle: FontEntry
  }
  social_handle: string
  hashtags: string[]
  tonality: string
  timezone: string
  voiceover: string
  logo_overlay: { enabled: boolean; position: string; opacity: number }
  intro_video: { position: string }
}

interface Brand {
  id: string
  name: string
  description: string | null
  website_url: string | null
  sector: string | null
  brand_kit: BrandKit
  logo_light_url: string | null
  logo_dark_url: string | null
  intro_video_url: string | null
}

// ─── Constants ────────────────────────────────────────────────────────────────

const SECTORS = [
  'Tekstil', 'Gıda', 'İnşaat', 'Turizm', 'Perakende',
  'Teknoloji', 'Sağlık', 'Eğitim', 'Finans', 'Hizmet', 'Diğer',
]

const TONALITIES = [
  { value: 'professional', label: 'Profesyonel' },
  { value: 'friendly', label: 'Samimi' },
  { value: 'fun', label: 'Eğlenceli' },
  { value: 'informative', label: 'Bilgilendirici' },
]

const FONT_FAMILIES = ['Inter', 'Roboto', 'Poppins', 'Montserrat', 'Open Sans', 'Lato']

const PLATFORMS = [
  { key: 'instagram', label: 'Instagram' },
  { key: 'tiktok', label: 'TikTok' },
  { key: 'linkedin', label: 'LinkedIn' },
  { key: 'facebook', label: 'Facebook' },
  { key: 'youtube', label: 'YouTube' },
  { key: 'twitter', label: 'Twitter / X' },
  { key: 'pinterest', label: 'Pinterest' },
]

const OVERLAY_POSITIONS = [
  { value: 'top-left', label: 'Sol Üst' },
  { value: 'top-right', label: 'Sağ Üst' },
  { value: 'bottom-left', label: 'Sol Alt' },
  { value: 'bottom-right', label: 'Sağ Alt' },
]

const DEFAULT_BRAND_KIT: BrandKit = {
  colors: ['#1D4ED8', '#3B82F6', '#BFDBFE'],
  fonts: {
    title: { family: 'Inter', weight: '700', letterCase: 'none' },
    subtitle: { family: 'Inter', weight: '400', letterCase: 'none' },
  },
  social_handle: '',
  hashtags: [],
  tonality: 'professional',
  timezone: 'Europe/Istanbul',
  voiceover: 'tr-TR-EmelNeural',
  logo_overlay: { enabled: false, position: 'bottom-right', opacity: 0.8 },
  intro_video: { position: 'start' },
}

// ─── Save indicator ───────────────────────────────────────────────────────────

function SaveIndicator({ saving, saved }: { saving: boolean; saved: boolean }) {
  if (saving) return (
    <span className="flex items-center gap-1 text-xs text-gray-400">
      <Loader2 className="w-3 h-3 animate-spin" /> Kaydediliyor...
    </span>
  )
  if (saved) return (
    <span className="flex items-center gap-1 text-xs text-emerald-600">
      <Check className="w-3 h-3" /> Kaydedildi
    </span>
  )
  return null
}

// ─── Color Swatch ─────────────────────────────────────────────────────────────

function ColorPicker({
  colors,
  onChange,
}: {
  colors: string[]
  onChange: (colors: string[]) => void
}) {
  const [input, setInput] = useState('')

  function addColor() {
    const hex = input.trim()
    if (!/^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6})$/.test(hex)) return
    if (colors.includes(hex)) return
    onChange([...colors, hex])
    setInput('')
  }

  function removeColor(c: string) {
    onChange(colors.filter((x) => x !== c))
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {colors.map((c) => (
          <div key={c} className="relative group">
            <div
              className="w-10 h-10 rounded-lg border border-gray-200 shadow-sm cursor-pointer"
              style={{ backgroundColor: c }}
              title={c}
            />
            <button
              onClick={() => removeColor(c)}
              className="absolute -top-1.5 -right-1.5 w-4 h-4 bg-gray-700 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity"
            >
              <X className="w-2.5 h-2.5" />
            </button>
          </div>
        ))}
        <input
          type="color"
          className="w-10 h-10 rounded-lg border border-dashed border-gray-300 cursor-pointer p-0.5"
          value={input || '#000000'}
          onChange={(e) => {
            setInput(e.target.value)
            onChange([...colors.filter((c) => c !== input), e.target.value].slice(0, 10))
          }}
          title="Renk seç"
        />
      </div>
      <div className="flex gap-2">
        <Input
          placeholder="#1D4ED8"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="w-32 text-sm font-mono"
          onKeyDown={(e) => e.key === 'Enter' && addColor()}
        />
        <Button variant="outline" size="sm" onClick={addColor}>Ekle</Button>
      </div>
      {colors.length < 3 && (
        <p className="text-xs text-amber-600">En az 3 renk ekleyin.</p>
      )}
    </div>
  )
}

// ─── Tag input ────────────────────────────────────────────────────────────────

function TagInput({
  tags,
  onChange,
  placeholder,
  prefix,
}: {
  tags: string[]
  onChange: (tags: string[]) => void
  placeholder?: string
  prefix?: string
}) {
  const [input, setInput] = useState('')

  function add() {
    const val = input.trim()
    if (!val) return
    const tag = prefix ? (val.startsWith(prefix) ? val : prefix + val) : val
    if (!tags.includes(tag)) onChange([...tags, tag])
    setInput('')
  }

  return (
    <div className="space-y-2">
      <div className="flex flex-wrap gap-1.5 min-h-[36px] p-2 border border-gray-200 rounded-md bg-white">
        {tags.map((t) => (
          <Badge key={t} variant="secondary" className="gap-1 text-xs">
            {t}
            <button onClick={() => onChange(tags.filter((x) => x !== t))}>
              <X className="w-3 h-3" />
            </button>
          </Badge>
        ))}
      </div>
      <div className="flex gap-2">
        <Input
          placeholder={placeholder}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="text-sm"
          onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ',') { e.preventDefault(); add() } }}
        />
        <Button variant="outline" size="sm" onClick={add}>Ekle</Button>
      </div>
    </div>
  )
}

// ─── Upload area ───────────────────────────────────────────────────────────────

function FileUploadArea({
  label,
  accept,
  previewUrl,
  onUpload,
  loading,
  isVideo,
}: {
  label: string
  accept: string
  previewUrl: string | null
  onUpload: (file: File) => void
  loading: boolean
  isVideo?: boolean
}) {
  const inputRef = useRef<HTMLInputElement>(null)

  return (
    <div className="space-y-2">
      <Label className="text-sm text-gray-700">{label}</Label>
      <div
        className="border-2 border-dashed border-gray-200 rounded-xl p-6 flex flex-col items-center justify-center gap-3 cursor-pointer hover:border-blue-400 hover:bg-blue-50/30 transition-colors"
        onClick={() => inputRef.current?.click()}
      >
        {loading ? (
          <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
        ) : previewUrl ? (
          isVideo ? (
            <video src={previewUrl} className="max-h-32 rounded-lg" controls />
          ) : (
            <Image src={previewUrl} alt={label} width={200} height={128} className="max-h-32 rounded-lg object-contain" />
          )
        ) : (
          <>
            <Upload className="w-6 h-6 text-gray-400" />
            <p className="text-sm text-gray-500">Dosya seç veya buraya sürükle</p>
          </>
        )}
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0]
            if (file) onUpload(file)
          }}
        />
      </div>
    </div>
  )
}

// ─── Helpers ──────────────────────────────────────────────────────────────────

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function deepMergeKit(defaults: BrandKit, incoming: any): BrandKit {
  return {
    colors: incoming?.colors ?? defaults.colors,
    fonts: {
      title: {
        family: incoming?.fonts?.title?.family ?? defaults.fonts.title.family,
        weight: incoming?.fonts?.title?.weight ?? defaults.fonts.title.weight,
        letterCase: incoming?.fonts?.title?.letterCase ?? incoming?.fonts?.title?.case ?? defaults.fonts.title.letterCase,
      },
      subtitle: {
        family: incoming?.fonts?.subtitle?.family ?? defaults.fonts.subtitle.family,
        weight: incoming?.fonts?.subtitle?.weight ?? defaults.fonts.subtitle.weight,
        letterCase: incoming?.fonts?.subtitle?.letterCase ?? incoming?.fonts?.subtitle?.case ?? defaults.fonts.subtitle.letterCase,
      },
    },
    social_handle: incoming?.social_handle ?? defaults.social_handle,
    hashtags: incoming?.hashtags ?? defaults.hashtags,
    tonality: incoming?.tonality ?? defaults.tonality,
    timezone: incoming?.timezone ?? defaults.timezone,
    voiceover: incoming?.voiceover ?? defaults.voiceover,
    logo_overlay: {
      enabled: incoming?.logo_overlay?.enabled ?? defaults.logo_overlay.enabled,
      position: incoming?.logo_overlay?.position ?? defaults.logo_overlay.position,
      opacity: incoming?.logo_overlay?.opacity ?? defaults.logo_overlay.opacity,
    },
    intro_video: {
      position: incoming?.intro_video?.position ?? defaults.intro_video.position,
    },
  }
}

type FontPatch = { family?: string | null; weight?: string | null; letterCase?: string | null }

function makeFontEntry(existing: FontEntry, patch: FontPatch): FontEntry {
  return {
    family: patch.family ?? existing.family,
    weight: patch.weight ?? existing.weight,
    letterCase: patch.letterCase ?? existing.letterCase,
  }
}

/** Guard: base-ui Select passes string | null; skip update on null */
function onSelect(v: string | null, fn: (val: string) => void) {
  if (v !== null) fn(v)
}

// ─── Main page ─────────────────────────────────────────────────────────────────

export default function MarkaAyarlariPage() {
  const currentBrand = useAppStore((s) => s.currentBrand)

  const [brand, setBrand] = useState<Brand | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [uploadingLogo, setUploadingLogo] = useState<'light' | 'dark' | null>(null)
  const [uploadingVideo, setUploadingVideo] = useState(false)

  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Load brand
  useEffect(() => {
    async function load() {
      if (!currentBrand?.id) { setLoading(false); return }
      const res = await api.get<Brand>(`/brands/${currentBrand.id}`)
      if (res.success && res.data) {
        const b = res.data
        // Deep merge with defaults to eliminate nulls from JSONB
        b.brand_kit = deepMergeKit(DEFAULT_BRAND_KIT, b.brand_kit ?? {})
        setBrand(b)
      }
      setLoading(false)
    }
    load()
  }, [currentBrand?.id])

  // Debounced auto-save for brand info
  const scheduleSave = useCallback((updated: Brand) => {
    if (saveTimer.current) clearTimeout(saveTimer.current)
    saveTimer.current = setTimeout(async () => {
      if (!updated.id) return
      setSaving(true)
      setSaved(false)
      await api.patch(`/brands/${updated.id}`, {
        name: updated.name,
        description: updated.description,
        website_url: updated.website_url,
        sector: updated.sector,
      })
      setSaving(false)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    }, 1500)
  }, [])

  const scheduleKitSave = useCallback((kit: BrandKit, brandId: string) => {
    if (saveTimer.current) clearTimeout(saveTimer.current)
    saveTimer.current = setTimeout(async () => {
      setSaving(true)
      setSaved(false)
      await api.patch(`/brands/${brandId}/kit`, kit)
      setSaving(false)
      setSaved(true)
      setTimeout(() => setSaved(false), 2000)
    }, 1500)
  }, [])

  function updateBrand(fields: Partial<Brand>) {
    setBrand((prev) => {
      if (!prev) return prev
      const updated = { ...prev, ...fields }
      scheduleSave(updated)
      return updated
    })
  }

  function updateKit(fields: Partial<BrandKit>) {
    setBrand((prev) => {
      if (!prev) return prev
      const updated = { ...prev, brand_kit: { ...prev.brand_kit, ...fields } }
      scheduleKitSave(updated.brand_kit, prev.id)
      return updated
    })
  }

  async function handleLogoUpload(file: File, variant: 'light' | 'dark') {
    if (!brand?.id) return
    setUploadingLogo(variant)
    const fd = new FormData()
    fd.append('file', file)
    fd.append('variant', variant)
    const res = await api.upload<{ url: string }>(`/brands/${brand.id}/logo`, fd)
    if (res.success && res.data) {
      const urlField = variant === 'light' ? 'logo_light_url' : 'logo_dark_url'
      setBrand((prev) => prev ? { ...prev, [urlField]: res.data!.url } : prev)
      toast.success('Logo yüklendi')
    } else {
      toast.error('Logo yüklenemedi')
    }
    setUploadingLogo(null)
  }

  async function handleVideoUpload(file: File) {
    if (!brand?.id) return
    setUploadingVideo(true)
    const fd = new FormData()
    fd.append('file', file)
    const res = await api.upload<{ url: string }>(`/brands/${brand.id}/intro-video`, fd)
    if (res.success && res.data) {
      setBrand((prev) => prev ? { ...prev, intro_video_url: res.data!.url } : prev)
      toast.success('Intro video yüklendi')
    } else {
      toast.error('Video yüklenemedi')
    }
    setUploadingVideo(false)
  }

  async function connectSocialAccount(platform: string) {
    const res = await api.get<{ url: string }>(`/social/oauth-link?platform=${platform}`)
    if (res.success && res.data?.url) {
      window.open(res.data.url, '_blank')
    } else {
      toast.error('OAuth bağlantısı alınamadı')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
      </div>
    )
  }

  if (!brand) {
    return (
      <div className="p-8 max-w-3xl mx-auto">
        <p className="text-gray-500">Henüz bir marka seçilmedi.</p>
      </div>
    )
  }

  const kit = brand.brand_kit

  return (
    <div className="p-8 max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-xl font-bold text-gray-900">Marka Ayarları</h1>
          <p className="text-sm text-gray-500 mt-0.5">{brand.name}</p>
        </div>
        <SaveIndicator saving={saving} saved={saved} />
      </div>

      <Tabs defaultValue="bilgiler">
        <TabsList className="mb-6">
          <TabsTrigger value="bilgiler">Marka Bilgileri</TabsTrigger>
          <TabsTrigger value="kimlik">Marka Kimliği</TabsTrigger>
          <TabsTrigger value="gorseller">Görseller</TabsTrigger>
          <TabsTrigger value="sosyal">Sosyal Hesaplar</TabsTrigger>
          <TabsTrigger value="dokumanlar">Dokümanlar</TabsTrigger>
        </TabsList>

        {/* ── Tab 1: Marka Bilgileri ─────────────────────────────────────────── */}
        <TabsContent value="bilgiler" className="space-y-5">
          <div className="space-y-1.5">
            <Label>Marka Adı</Label>
            <Input
              value={brand.name}
              onChange={(e) => updateBrand({ name: e.target.value })}
              placeholder="Marka adı"
            />
          </div>

          <div className="space-y-1.5">
            <Label>Açıklama</Label>
            <Textarea
              value={brand.description ?? ''}
              onChange={(e) => updateBrand({ description: e.target.value })}
              placeholder="Markanızı kısaca açıklayın..."
              rows={3}
            />
          </div>

          <div className="space-y-1.5">
            <Label>Web Sitesi</Label>
            <div className="flex gap-2">
              <Input
                value={brand.website_url ?? ''}
                onChange={(e) => updateBrand({ website_url: e.target.value })}
                placeholder="https://example.com"
                type="url"
              />
              <Button
                variant="outline"
                className="whitespace-nowrap text-sm"
                onClick={() => toast.info('Web sitesi analizi yakında')}
              >
                Otomatik Doldur
              </Button>
            </div>
          </div>

          <div className="space-y-1.5">
            <Label>Sektör</Label>
            <Select
              value={brand.sector ?? ''}
              onValueChange={(v) => onSelect(v, (val) => updateBrand({ sector: val }))}
            >
              <SelectTrigger>
                <SelectValue placeholder="Sektör seç" />
              </SelectTrigger>
              <SelectContent>
                {SECTORS.map((s) => (
                  <SelectItem key={s} value={s}>{s}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </TabsContent>

        {/* ── Tab 2: Marka Kimliği ───────────────────────────────────────────── */}
        <TabsContent value="kimlik" className="space-y-6">
          <div className="space-y-2">
            <Label>Marka Renkleri</Label>
            <p className="text-xs text-gray-500">En az 3 renk ekleyin. Bu renkler üretilen içeriklerde kullanılır.</p>
            <ColorPicker
              colors={kit.colors ?? []}
              onChange={(colors) => updateKit({ colors })}
            />
          </div>

          <div className="space-y-3">
            <Label>Başlık Fontu</Label>
            <div className="grid grid-cols-3 gap-3">
              <div className="space-y-1">
                <p className="text-xs text-gray-500">Yazı Tipi</p>
                <Select
                  value={kit.fonts.title.family}
                  onValueChange={(v) => updateKit({ fonts: { ...kit.fonts, title: makeFontEntry(kit.fonts.title, { family: v }) } })}
                >
                  <SelectTrigger className="text-sm">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {FONT_FAMILIES.map((f) => <SelectItem key={f} value={f}>{f}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-gray-500">Kalınlık</p>
                <Select
                  value={kit.fonts.title.weight}
                  onValueChange={(v) => updateKit({ fonts: { ...kit.fonts, title: makeFontEntry(kit.fonts.title, { weight: v }) } })}
                >
                  <SelectTrigger className="text-sm">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="400">Normal</SelectItem>
                    <SelectItem value="600">Semibold</SelectItem>
                    <SelectItem value="700">Bold</SelectItem>
                    <SelectItem value="800">Extrabold</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-gray-500">Büyük Harf</p>
                <Select
                  value={kit.fonts.title.letterCase}
                  onValueChange={(v) => updateKit({ fonts: { ...kit.fonts, title: makeFontEntry(kit.fonts.title, { letterCase: v }) } })}
                >
                  <SelectTrigger className="text-sm">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Normal</SelectItem>
                    <SelectItem value="uppercase">BÜYÜK</SelectItem>
                    <SelectItem value="lowercase">küçük</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <Label>Alt Başlık Fontu</Label>
            <div className="grid grid-cols-3 gap-3">
              <div className="space-y-1">
                <p className="text-xs text-gray-500">Yazı Tipi</p>
                <Select
                  value={kit.fonts.subtitle.family}
                  onValueChange={(v) => updateKit({ fonts: { ...kit.fonts, subtitle: makeFontEntry(kit.fonts.subtitle, { family: v }) } })}
                >
                  <SelectTrigger className="text-sm">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {FONT_FAMILIES.map((f) => <SelectItem key={f} value={f}>{f}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-gray-500">Kalınlık</p>
                <Select
                  value={kit.fonts.subtitle.weight}
                  onValueChange={(v) => updateKit({ fonts: { ...kit.fonts, subtitle: makeFontEntry(kit.fonts.subtitle, { weight: v }) } })}
                >
                  <SelectTrigger className="text-sm">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="300">Light</SelectItem>
                    <SelectItem value="400">Normal</SelectItem>
                    <SelectItem value="600">Semibold</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-gray-500">Büyük Harf</p>
                <Select
                  value={kit.fonts.subtitle.letterCase}
                  onValueChange={(v) => updateKit({ fonts: { ...kit.fonts, subtitle: makeFontEntry(kit.fonts.subtitle, { letterCase: v }) } })}
                >
                  <SelectTrigger className="text-sm">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">Normal</SelectItem>
                    <SelectItem value="uppercase">BÜYÜK</SelectItem>
                    <SelectItem value="lowercase">küçük</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>

          <div className="space-y-1.5">
            <Label>Ton / Üslup</Label>
            <Select
              value={kit.tonality ?? 'professional'}
              onValueChange={(v) => onSelect(v, (val) => updateKit({ tonality: val }))}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {TONALITIES.map((t) => (
                  <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-1.5">
            <Label>Sosyal Medya Hesabı</Label>
            <Input
              value={kit.social_handle ?? ''}
              onChange={(e) => updateKit({ social_handle: e.target.value })}
              placeholder="@kullanici_adi"
            />
          </div>

          <div className="space-y-1.5">
            <Label>Hashtagler</Label>
            <p className="text-xs text-gray-500">Enter veya virgül ile ekleyin.</p>
            <TagInput
              tags={kit.hashtags ?? []}
              onChange={(hashtags) => updateKit({ hashtags })}
              placeholder="#hashtag"
              prefix="#"
            />
          </div>
        </TabsContent>

        {/* ── Tab 3: Görseller ──────────────────────────────────────────────── */}
        <TabsContent value="gorseller" className="space-y-6">
          <div className="grid grid-cols-2 gap-6">
            <FileUploadArea
              label="Logo (Açık Arka Plan)"
              accept="image/*"
              previewUrl={brand.logo_light_url}
              onUpload={(file) => handleLogoUpload(file, 'light')}
              loading={uploadingLogo === 'light'}
            />
            <FileUploadArea
              label="Logo (Koyu Arka Plan)"
              accept="image/*"
              previewUrl={brand.logo_dark_url}
              onUpload={(file) => handleLogoUpload(file, 'dark')}
              loading={uploadingLogo === 'dark'}
            />
          </div>

          <div className="space-y-3 p-4 border border-gray-200 rounded-xl">
            <div className="flex items-center justify-between">
              <div>
                <Label>Logo Filigran</Label>
                <p className="text-xs text-gray-500 mt-0.5">Üretilen içeriklere logo ekle</p>
              </div>
              <Switch
                checked={kit.logo_overlay?.enabled ?? false}
                onCheckedChange={(v) => updateKit({ logo_overlay: { ...kit.logo_overlay, enabled: v } })}
              />
            </div>
            {kit.logo_overlay?.enabled && (
              <div className="grid grid-cols-2 gap-3 pt-2 border-t border-gray-100">
                <div className="space-y-1">
                  <p className="text-xs text-gray-500">Konum</p>
                  <Select
                    value={kit.logo_overlay.position}
                    onValueChange={(v) => onSelect(v, (val) => updateKit({ logo_overlay: { ...kit.logo_overlay, position: val } }))}
                  >
                    <SelectTrigger className="text-sm">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {OVERLAY_POSITIONS.map((p) => (
                        <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1">
                  <p className="text-xs text-gray-500">Opaklık: {Math.round((kit.logo_overlay.opacity ?? 0.8) * 100)}%</p>
                  <input
                    type="range"
                    min={0.1}
                    max={1}
                    step={0.05}
                    value={kit.logo_overlay.opacity ?? 0.8}
                    onChange={(e) => updateKit({ logo_overlay: { ...kit.logo_overlay, opacity: parseFloat(e.target.value) } })}
                    className="w-full mt-2"
                  />
                </div>
              </div>
            )}
          </div>

          <FileUploadArea
            label="Intro / Outro Video"
            accept="video/*"
            previewUrl={brand.intro_video_url}
            onUpload={handleVideoUpload}
            loading={uploadingVideo}
            isVideo
          />

          {brand.intro_video_url && (
            <div className="space-y-1.5">
              <Label>Video Pozisyonu</Label>
              <Select
                value={kit.intro_video?.position ?? 'start'}
                onValueChange={(v) => onSelect(v, (val) => updateKit({ intro_video: { position: val } }))}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="start">Başında</SelectItem>
                  <SelectItem value="end">Sonunda</SelectItem>
                  <SelectItem value="both">Her İkisi</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}
        </TabsContent>

        {/* ── Tab 4: Sosyal Hesaplar ────────────────────────────────────────── */}
        <TabsContent value="sosyal" className="space-y-3">
          <p className="text-sm text-gray-500">
            Sosyal medya hesaplarınızı bağlayarak içerik otomatik olarak yayınlanabilir.
          </p>
          {PLATFORMS.map((platform) => (
            <div
              key={platform.key}
              className="flex items-center justify-between p-4 border border-gray-200 rounded-xl"
            >
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 bg-gray-100 rounded-lg flex items-center justify-center">
                  <span className="text-sm font-bold text-gray-600">
                    {platform.label[0]}
                  </span>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-800">{platform.label}</p>
                  <p className="text-xs text-gray-400">Bağlı değil</p>
                </div>
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={() => connectSocialAccount(platform.key)}
              >
                Hesabı Bağla
              </Button>
            </div>
          ))}
        </TabsContent>

        {/* ── Tab 5: Dokümanlar ─────────────────────────────────────────────── */}
        <TabsContent value="dokumanlar" className="space-y-4">
          <p className="text-sm text-gray-500">
            Yüklediğiniz dokümanlar içerik üretiminde bağlam olarak kullanılır.
          </p>
          <div
            className="border-2 border-dashed border-gray-200 rounded-xl p-10 flex flex-col items-center justify-center gap-3 cursor-pointer hover:border-blue-400 hover:bg-blue-50/30 transition-colors"
            onClick={() => toast.info('Doküman yükleme yakında aktif olacak')}
          >
            <Upload className="w-8 h-8 text-gray-400" />
            <p className="text-sm text-gray-500">PDF, Word, Excel veya görsel yükleyin</p>
            <p className="text-xs text-gray-400">Maks. 50 MB</p>
          </div>
          <div className="text-center text-sm text-gray-400 py-8">
            Henüz doküman yüklenmedi.
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
