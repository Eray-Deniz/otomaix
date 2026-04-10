'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useRef, useState, useCallback } from 'react'
import { useSearchParams } from 'next/navigation'
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
import { Loader2, X, Upload, Check, FileText, Trash2, User, Video } from 'lucide-react'

// ─── Types ────────────────────────────────────────────────────────────────────

interface StockAvatar {
  avatar_id: string
  avatar_name: string
  gender: string
  preview_url: string
  preview_image_url: string
}

interface ActiveAvatar {
  type: 'custom' | 'stock'
  avatar_id: string
  preview_url: string
  name: string
}

interface BrandDocument {
  id: string
  brand_id: string
  name: string
  file_url: string
  file_type: string | null
  category: string | null
  description: string | null
  file_size_kb: number | null
  has_raw_text: boolean
  chunk_count: number
  created_at: string
}

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
  avatar?: ActiveAvatar
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
  const searchParams = useSearchParams()

  const [brand, setBrand] = useState<Brand | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState(false)
  const [uploadingLogo, setUploadingLogo] = useState<'light' | 'dark' | null>(null)
  const [uploadingVideo, setUploadingVideo] = useState(false)
  const [activeTab, setActiveTab] = useState(() => searchParams.get('tab') ?? 'bilgiler')
  const [documents, setDocuments] = useState<BrandDocument[]>([])
  const [loadingDocs, setLoadingDocs] = useState(false)
  const [uploadingDoc, setUploadingDoc] = useState(false)
  const [deletingDocId, setDeletingDocId] = useState<string | null>(null)
  const docInputRef = useRef<HTMLInputElement>(null)

  // Avatar state
  const [stockAvatars, setStockAvatars] = useState<StockAvatar[]>([])
  const [loadingAvatars, setLoadingAvatars] = useState(false)
  const [creatingAvatar, setCreatingAvatar] = useState(false)
  const [selectingAvatarId, setSelectingAvatarId] = useState<string | null>(null)
  const avatarPhotoRef = useRef<HTMLInputElement>(null)

  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Handle OAuth callback result (?connected=platform or ?error=...)
  useEffect(() => {
    const connected = searchParams.get('connected')
    const error = searchParams.get('error')
    if (connected) {
      toast.success(`${connected} hesabı başarıyla bağlandı!`)
      setActiveTab('sosyal')
      // Clean up URL without reload
      window.history.replaceState({}, '', '/marka-ayarlari')
    } else if (error) {
      const msgs: Record<string, string> = {
        invalid_state: 'Güvenlik doğrulaması başarısız. Lütfen tekrar deneyin.',
        missing_params: 'Bağlantı parametreleri eksik. Lütfen tekrar deneyin.',
      }
      toast.error(msgs[error] ?? 'Hesap bağlantısı başarısız.')
      setActiveTab('sosyal')
      window.history.replaceState({}, '', '/marka-ayarlari')
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

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

  async function loadDocuments(brandId: string) {
    setLoadingDocs(true)
    const res = await api.get<BrandDocument[]>(`/documents?brand_id=${brandId}`)
    if (res.success && res.data) setDocuments(res.data)
    setLoadingDocs(false)
  }

  useEffect(() => {
    if (activeTab === 'dokumanlar' && brand?.id) {
      loadDocuments(brand.id)
    }
  }, [activeTab, brand?.id]) // eslint-disable-line react-hooks/exhaustive-deps

  async function handleDocumentUpload(file: File) {
    if (!brand?.id) return
    setUploadingDoc(true)
    const fd = new FormData()
    fd.append('file', file)
    fd.append('brand_id', brand.id)
    fd.append('name', file.name)
    const res = await api.upload<BrandDocument>('/documents', fd)
    if (res.success && res.data) {
      setDocuments((prev) => [res.data!, ...prev])
      toast.success(`"${file.name}" yüklendi ve işlendi`)
    } else {
      toast.error('Doküman yüklenemedi')
    }
    setUploadingDoc(false)
  }

  async function handleDocumentDelete(docId: string, docName: string) {
    if (!confirm(`"${docName}" dokümanını silmek istediğinize emin misiniz?`)) return
    setDeletingDocId(docId)
    const res = await api.delete(`/documents/${docId}`)
    if (res.success) {
      setDocuments((prev) => prev.filter((d) => d.id !== docId))
      toast.success('Doküman silindi')
    } else {
      toast.error('Doküman silinemedi')
    }
    setDeletingDocId(null)
  }

  // Avatar sekmesi açıldığında stok avatarları yükle
  useEffect(() => {
    if (activeTab === 'avatar') {
      setLoadingAvatars(true)
      api.get<StockAvatar[]>('/avatar/stock').then((res) => {
        if (res.success && res.data) setStockAvatars(res.data)
        setLoadingAvatars(false)
      })
    }
  }, [activeTab])

  async function handleAvatarPhotoUpload(file: File) {
    if (!brand?.id) return
    setCreatingAvatar(true)
    const fd = new FormData()
    fd.append('file', file)
    fd.append('brand_id', brand.id)
    fd.append('name', file.name.replace(/\.[^.]+$/, ''))
    const res = await api.upload<ActiveAvatar>('/avatar/create', fd)
    if (res.success && res.data) {
      setBrand((prev) => prev ? {
        ...prev,
        brand_kit: { ...prev.brand_kit, avatar: res.data as unknown as ActiveAvatar }
      } : prev)
      toast.success('Avatar oluşturuldu! HeyGen işlemi tamamlandığında kullanıma hazır olacak.')
    } else {
      toast.error((res.error as string) || 'Avatar oluşturulamadı')
    }
    setCreatingAvatar(false)
  }

  async function handleSelectStockAvatar(av: StockAvatar) {
    if (!brand?.id) return
    setSelectingAvatarId(av.avatar_id)
    const res = await api.post<ActiveAvatar>('/avatar/select-stock', {
      brand_id: brand.id,
      avatar_id: av.avatar_id,
      avatar_name: av.avatar_name,
      preview_url: av.preview_url || av.preview_image_url,
    })
    if (res.success && res.data) {
      setBrand((prev) => prev ? {
        ...prev,
        brand_kit: { ...prev.brand_kit, avatar: res.data as unknown as ActiveAvatar }
      } : prev)
      toast.success(`"${av.avatar_name}" avatarı seçildi`)
    } else {
      toast.error('Avatar seçilemedi')
    }
    setSelectingAvatarId(null)
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

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-6 flex-wrap">
          <TabsTrigger value="bilgiler">Marka Bilgileri</TabsTrigger>
          <TabsTrigger value="kimlik">Marka Kimliği</TabsTrigger>
          <TabsTrigger value="gorseller">Görseller</TabsTrigger>
          <TabsTrigger value="sosyal">Sosyal Hesaplar</TabsTrigger>
          <TabsTrigger value="dokumanlar">Dokümanlar</TabsTrigger>
          <TabsTrigger value="avatar">AI Avatar</TabsTrigger>
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
            Yüklediğiniz dokümanlar (PDF, Word, Excel) içerik üretiminde bağlam olarak kullanılır.
            Küçük dosyalar doğrudan, büyük dosyalar parçalanarak (RAG) AI&apos;a aktarılır.
          </p>

          {/* Upload area */}
          <div
            className="border-2 border-dashed border-gray-200 rounded-xl p-8 flex flex-col items-center justify-center gap-3 cursor-pointer hover:border-blue-400 hover:bg-blue-50/30 transition-colors"
            onClick={() => !uploadingDoc && docInputRef.current?.click()}
          >
            {uploadingDoc ? (
              <>
                <Loader2 className="w-7 h-7 animate-spin text-blue-500" />
                <p className="text-sm text-blue-600">Yükleniyor ve işleniyor...</p>
              </>
            ) : (
              <>
                <Upload className="w-7 h-7 text-gray-400" />
                <p className="text-sm text-gray-500">PDF, Word veya Excel yükleyin</p>
                <p className="text-xs text-gray-400">Maks. 50 MB</p>
              </>
            )}
            <input
              ref={docInputRef}
              type="file"
              accept=".pdf,.doc,.docx,.xls,.xlsx,.txt"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) { handleDocumentUpload(file); e.target.value = '' }
              }}
            />
          </div>

          {/* Document list */}
          {loadingDocs ? (
            <div className="flex justify-center py-6">
              <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
            </div>
          ) : documents.length === 0 ? (
            <div className="text-center text-sm text-gray-400 py-8">
              Henüz doküman yüklenmedi.
            </div>
          ) : (
            <div className="space-y-2">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-xl hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="w-9 h-9 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0">
                      <FileText className="w-4 h-4 text-blue-500" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-gray-800 truncate">{doc.name}</p>
                      <p className="text-xs text-gray-400">
                        {doc.file_size_kb ? `${doc.file_size_kb} KB` : '—'}
                        {doc.has_raw_text && ' · Tam metin'}
                        {doc.chunk_count > 0 && ` · ${doc.chunk_count} parça (RAG)`}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDocumentDelete(doc.id, doc.name)}
                    className="ml-3 p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-md transition-colors flex-shrink-0"
                    disabled={deletingDocId === doc.id}
                    title="Sil"
                  >
                    {deletingDocId === doc.id
                      ? <Loader2 className="w-4 h-4 animate-spin" />
                      : <Trash2 className="w-4 h-4" />
                    }
                  </button>
                </div>
              ))}
            </div>
          )}
        </TabsContent>

        {/* ── Tab 6: AI Avatar ──────────────────────────────────────────────── */}
        <TabsContent value="avatar" className="space-y-6">
          <p className="text-sm text-gray-500">
            AI avatar ile video içeriklerinizde gerçekçi bir konuşmacı kullanın.
            Kendi fotoğrafınızdan avatar oluşturun veya hazır avatarlardan seçin.
          </p>

          {/* Aktif avatar gösterimi */}
          {kit.avatar && (
            <div className="p-4 border border-violet-200 bg-violet-50 rounded-xl flex items-center gap-4">
              <div className="w-14 h-14 rounded-xl bg-violet-200 flex items-center justify-center overflow-hidden flex-shrink-0">
                {kit.avatar.preview_url ? (
                  <Image
                    src={kit.avatar.preview_url}
                    alt={kit.avatar.name}
                    width={56}
                    height={56}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <User className="w-6 h-6 text-violet-600" />
                )}
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold text-violet-800">{kit.avatar.name}</p>
                <p className="text-xs text-violet-500">
                  {kit.avatar.type === 'custom' ? 'Kişisel avatar' : 'Hazır avatar'} · Aktif
                </p>
              </div>
              <Button
                size="sm"
                variant="outline"
                className="border-violet-300 text-violet-700 hover:bg-violet-100 gap-1.5 flex-shrink-0"
                onClick={() => toast.info('İçerik Oluştur → Video sekmesinden avatar ile video üretebilirsiniz')}
              >
                <Video className="w-3.5 h-3.5" />
                Video Üret
              </Button>
            </div>
          )}

          {/* Kendi avatarını oluştur */}
          <div className="space-y-3">
            <div>
              <Label className="text-base">Kendi Avatarınız</Label>
              <p className="text-xs text-gray-500 mt-0.5">
                Yüz net görünen, düz arka planlı bir fotoğraf yükleyin. HeyGen ile işlenir (~1-2 dk).
              </p>
            </div>
            <div
              className="border-2 border-dashed border-violet-200 rounded-xl p-8 flex flex-col items-center justify-center gap-3 cursor-pointer hover:border-violet-400 hover:bg-violet-50/50 transition-colors"
              onClick={() => !creatingAvatar && avatarPhotoRef.current?.click()}
            >
              {creatingAvatar ? (
                <>
                  <Loader2 className="w-7 h-7 animate-spin text-violet-500" />
                  <p className="text-sm text-violet-600">Avatar oluşturuluyor...</p>
                </>
              ) : (
                <>
                  <User className="w-7 h-7 text-gray-400" />
                  <p className="text-sm text-gray-500">Fotoğraf yükle</p>
                  <p className="text-xs text-gray-400">JPG, PNG veya WebP · Maks. 10 MB</p>
                </>
              )}
              <input
                ref={avatarPhotoRef}
                type="file"
                accept=".jpg,.jpeg,.png,.webp"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) { handleAvatarPhotoUpload(file); e.target.value = '' }
                }}
              />
            </div>
          </div>

          {/* Hazır avatarlar */}
          <div className="space-y-3">
            <Label className="text-base">Hazır Avatarlar</Label>
            {loadingAvatars ? (
              <div className="flex justify-center py-8">
                <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
              </div>
            ) : stockAvatars.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-6">
                Avatar listesi yüklenemedi. HEYGEN_API_KEY gerekli.
              </p>
            ) : (
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
                {stockAvatars.map((av) => {
                  const isActive = kit.avatar?.avatar_id === av.avatar_id
                  return (
                    <button
                      key={av.avatar_id}
                      onClick={() => !isActive && handleSelectStockAvatar(av)}
                      disabled={selectingAvatarId === av.avatar_id}
                      className={`relative rounded-xl overflow-hidden border-2 transition-all aspect-square flex flex-col items-center justify-center gap-1 p-3 ${
                        isActive
                          ? 'border-violet-500 bg-violet-50'
                          : 'border-gray-200 hover:border-violet-300 hover:bg-violet-50/30'
                      }`}
                    >
                      {selectingAvatarId === av.avatar_id ? (
                        <Loader2 className="w-6 h-6 animate-spin text-violet-500" />
                      ) : av.preview_image_url ? (
                        <Image
                          src={av.preview_image_url}
                          alt={av.avatar_name}
                          width={80}
                          height={80}
                          className="w-14 h-14 rounded-full object-cover"
                        />
                      ) : (
                        <div className="w-14 h-14 rounded-full bg-gray-100 flex items-center justify-center">
                          <User className="w-6 h-6 text-gray-400" />
                        </div>
                      )}
                      <span className="text-xs font-medium text-gray-700 text-center leading-tight">
                        {av.avatar_name}
                      </span>
                      <span className="text-[10px] text-gray-400">
                        {av.gender === 'female' ? 'Kadın' : 'Erkek'}
                      </span>
                      {isActive && (
                        <div className="absolute top-1.5 right-1.5 w-5 h-5 bg-violet-500 rounded-full flex items-center justify-center">
                          <Check className="w-3 h-3 text-white" />
                        </div>
                      )}
                    </button>
                  )
                })}
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
