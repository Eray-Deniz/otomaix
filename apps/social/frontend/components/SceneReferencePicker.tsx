'use client'

// Sprint 3 (Özel Gün) — Marka referans görsel seçici.
// Akış C form içinde imageSubType='general' modunda görünür.
// Kütüphane listesi + yeni yükle (saveToLibrary toggle + zorunlu telif onay).

import { useEffect, useState } from 'react'
import Image from 'next/image'
import { Loader2, Upload, X, ImageIcon, Trash2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'
import {
  fetchReferenceImages,
  uploadReferenceImageToLibrary,
  uploadReferenceImageTemporary,
  deleteReferenceImage,
  type BrandReferenceImage,
} from '@/lib/api/brand-reference-images'

export interface SelectedSceneReference {
  id: string | null   // null → tek seferlik upload (kütüphaneye kaydedilmedi)
  image_url: string
  label: string | null
}

interface Props {
  brandId: string
  value: SelectedSceneReference | null
  onChange: (ref: SelectedSceneReference | null) => void
}

export function SceneReferencePicker({ brandId, value, onChange }: Props) {
  const [items, setItems] = useState<BrandReferenceImage[]>([])
  const [maxLimit, setMaxLimit] = useState<number>(20)
  const [loading, setLoading] = useState(false)
  const [showUpload, setShowUpload] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const [label, setLabel] = useState('')
  const [saveToLibrary, setSaveToLibrary] = useState(true)
  const [termsAccepted, setTermsAccepted] = useState(false)
  const [uploading, setUploading] = useState(false)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    fetchReferenceImages(brandId).then((res) => {
      if (cancelled) return
      if (res.success && res.data) {
        setItems(res.data.items)
        setMaxLimit(res.data.max)
      }
      setLoading(false)
    })
    return () => { cancelled = true }
  }, [brandId])

  function resetUploadForm() {
    setFile(null)
    setLabel('')
    setSaveToLibrary(true)
    setTermsAccepted(false)
    setShowUpload(false)
  }

  async function handleUpload() {
    if (!file) {
      toast.error('Lütfen bir görsel seçin')
      return
    }
    if (!termsAccepted) {
      toast.error('Devam etmek için telif onayı zorunludur')
      return
    }
    if (saveToLibrary && items.length >= maxLimit) {
      toast.error(`Marka başına en fazla ${maxLimit} referans görsel saklayabilirsiniz. Önce eski görselleri silin veya kütüphaneye kaydetmeden devam edin.`)
      return
    }
    setUploading(true)
    if (saveToLibrary) {
      const res = await uploadReferenceImageToLibrary(brandId, file, label.trim() || undefined)
      setUploading(false)
      if (res.success && res.data) {
        setItems((prev) => [res.data!, ...prev])
        onChange({ id: res.data.id, image_url: res.data.image_url, label: res.data.label })
        toast.success('Görsel kütüphaneye eklendi ve seçildi')
        resetUploadForm()
      } else {
        toast.error(res.success ? 'Yükleme başarısız' : (res.error || 'Yükleme başarısız'))
      }
    } else {
      const res = await uploadReferenceImageTemporary(brandId, file)
      setUploading(false)
      if (res.success && res.data) {
        onChange({ id: null, image_url: res.data.image_url, label: label.trim() || null })
        toast.success('Görsel bu içerik için seçildi (kütüphaneye kaydedilmedi)')
        resetUploadForm()
      } else {
        toast.error(res.success ? 'Yükleme başarısız' : (res.error || 'Yükleme başarısız'))
      }
    }
  }

  async function handleDelete(refId: string) {
    if (!confirm('Bu referans görseli silmek istediğinize emin misiniz?')) return
    const res = await deleteReferenceImage(refId)
    if (res.success) {
      setItems((prev) => prev.filter((i) => i.id !== refId))
      if (value?.id === refId) onChange(null)
      toast.message('Referans görsel silindi')
    } else {
      toast.error('Silinemedi: ' + (res.error || 'Bilinmeyen hata'))
    }
  }

  return (
    <div className="space-y-2">
      <Label>
        Sahne için referans görsel{' '}
        <span className="font-normal text-gray-400">(opsiyonel)</span>
      </Label>
      <p className="text-xs text-gray-500">
        Yüklediğiniz fotoğraf (örn. Atatürk portresi, kurucu görseli) yüz korunarak yeni bir kompozisyona yerleştirilir.
      </p>

      {/* Seçili gösterim */}
      {value && (
        <div className="flex items-center gap-3 rounded-xl border border-amber-300 bg-amber-50 px-3 py-2.5">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={value.image_url} alt={value.label ?? 'Seçili referans'} className="w-12 h-12 rounded-lg object-cover" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-amber-900 truncate">
              {value.label ?? 'Seçili referans görsel'}
            </p>
            <p className="text-xs text-amber-700">
              {value.id ? 'Kütüphaneden seçildi' : 'Tek seferlik (kaydedilmedi)'}
            </p>
          </div>
          <button
            type="button"
            onClick={() => onChange(null)}
            className="text-amber-700 hover:text-amber-900"
            aria-label="Seçimi kaldır"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Kütüphane grid */}
      {loading ? (
        <div className="flex items-center gap-2 py-3 text-gray-400 text-sm">
          <Loader2 className="w-4 h-4 animate-spin" />
          Kütüphane yükleniyor...
        </div>
      ) : items.length > 0 ? (
        <div>
          <p className="text-xs text-gray-500 mb-1.5">Kütüphane</p>
          <div className="grid grid-cols-4 gap-2">
            {items.map((it) => {
              const selected = value?.id === it.id
              return (
                <div key={it.id} className="relative group">
                  <button
                    type="button"
                    onClick={() => onChange({ id: it.id, image_url: it.image_url, label: it.label })}
                    className={cn(
                      'block w-full aspect-square rounded-lg overflow-hidden border-2 transition-all',
                      selected ? 'border-amber-500 ring-2 ring-amber-200' : 'border-gray-200 hover:border-amber-300'
                    )}
                    title={it.label ?? 'Etiketsiz'}
                  >
                    <Image
                      src={it.image_url}
                      alt={it.label ?? 'Referans görsel'}
                      width={120}
                      height={120}
                      className="w-full h-full object-cover"
                    />
                  </button>
                  <button
                    type="button"
                    onClick={() => handleDelete(it.id)}
                    className="absolute top-1 right-1 bg-white/80 hover:bg-white text-gray-500 hover:text-red-600 rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
                    aria-label="Sil"
                  >
                    <Trash2 className="w-3 h-3" />
                  </button>
                  {it.label && (
                    <p className="text-[10px] text-gray-500 mt-0.5 truncate">{it.label}</p>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      ) : (
        <div className="rounded-xl border border-dashed border-gray-200 px-3 py-4 text-center text-xs text-gray-400">
          <ImageIcon className="w-5 h-5 mx-auto mb-1 opacity-50" />
          Henüz referans görsel yok
        </div>
      )}

      {/* Yeni yükle */}
      {!showUpload ? (
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => setShowUpload(true)}
          className="gap-2 w-full"
        >
          <Upload className="w-4 h-4" />
          Yeni referans görsel yükle
        </Button>
      ) : (
        <div className="space-y-3 rounded-xl border border-gray-200 bg-gray-50 p-3">
          <div className="flex items-center justify-between">
            <Label className="text-sm">Yeni Görsel Yükle</Label>
            <button
              type="button"
              onClick={resetUploadForm}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <input
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            className="block w-full text-xs text-gray-700 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-medium file:bg-white file:text-gray-700 file:border file:border-gray-300 hover:file:bg-gray-50"
          />

          <div className="space-y-1.5">
            <Label className="text-xs">Etiket <span className="font-normal text-gray-400">(opsiyonel)</span></Label>
            <input
              type="text"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              placeholder="Atatürk 1923 portre, kurucu fotoğrafı, ..."
              maxLength={80}
              className="w-full text-sm px-3 py-1.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500/20 focus:border-amber-400 bg-white"
            />
          </div>

          <div className="flex items-center justify-between rounded-lg bg-white border border-gray-200 px-3 py-2">
            <div className="flex flex-col gap-0.5">
              <Label className="text-sm font-medium text-gray-800 cursor-pointer">Marka kütüphanesine kaydet</Label>
              <span className="text-xs text-gray-500">İleride tekrar kullanmak için</span>
            </div>
            <Switch checked={saveToLibrary} onCheckedChange={setSaveToLibrary} />
          </div>

          <label className="flex items-start gap-2 text-xs text-gray-700 cursor-pointer">
            <input
              type="checkbox"
              checked={termsAccepted}
              onChange={(e) => setTermsAccepted(e.target.checked)}
              className="mt-0.5"
            />
            <span>
              <strong>Telif onayı (zorunlu):</strong> Yüklediğim görselin haklarına sahip olduğumu veya bu kullanım için izin aldığımı onaylıyorum.
            </span>
          </label>

          <Button
            type="button"
            onClick={handleUpload}
            disabled={uploading || !file || !termsAccepted}
            className="w-full gap-2"
            size="sm"
          >
            {uploading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
            Yükle ve Seç
          </Button>
        </div>
      )}
    </div>
  )
}
