'use client'

import { useEffect, useRef, useState } from 'react'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { toast } from 'sonner'
import { Loader2, X, Upload, Package, Wrench, FileText, Trash2 } from 'lucide-react'
import {
  createProduct,
  updateProduct,
  uploadProductImage,
  uploadProductDocument,
} from '@/lib/api/products'
import type { Product, ProductType } from '@/lib/products.types'

const IMAGE_ACCEPT = 'image/jpeg,image/png,image/webp'
const MAX_IMAGE_BYTES = 10 * 1024 * 1024
const DOC_ACCEPT = '.pdf,.doc,.docx,.xls,.xlsx,.txt'
const MAX_DOC_BYTES = 50 * 1024 * 1024

interface Props {
  open: boolean
  onOpenChange: (open: boolean) => void
  brandId: string
  product: Product | null
  onSaved: () => void
  onPlanLimit: (message: string) => void
}

export function ProductFormDialog({
  open,
  onOpenChange,
  brandId,
  product,
  onSaved,
  onPlanLimit,
}: Props) {
  const isEdit = product !== null
  const [type, setType] = useState<ProductType>('product')
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [tags, setTags] = useState<string[]>([])
  const [tagInput, setTagInput] = useState('')
  const [isActive, setIsActive] = useState(true)
  const [pendingImage, setPendingImage] = useState<File | null>(null)
  const [pendingPreview, setPendingPreview] = useState<string | null>(null)
  const [pendingDocs, setPendingDocs] = useState<File[]>([])
  const [saving, setSaving] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const docInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!open) return
    if (product) {
      setType(product.type)
      setName(product.name)
      setDescription(product.description ?? '')
      setTags(product.tags ?? [])
      setIsActive(product.is_active)
    } else {
      setType('product')
      setName('')
      setDescription('')
      setTags([])
      setIsActive(true)
    }
    setTagInput('')
    setPendingImage(null)
    setPendingPreview(null)
    setPendingDocs([])
  }, [open, product])

  useEffect(() => {
    if (!pendingImage) {
      setPendingPreview(null)
      return
    }
    const url = URL.createObjectURL(pendingImage)
    setPendingPreview(url)
    return () => URL.revokeObjectURL(url)
  }, [pendingImage])

  function normalizeTag(raw: string): string | null {
    const val = raw.trim()
    if (!val) return null
    return val
  }

  function addTags(raws: string[]) {
    const lowerExisting = new Set(tags.map((t) => t.toLowerCase()))
    const next: string[] = []
    for (const raw of raws) {
      const tag = normalizeTag(raw)
      if (!tag) continue
      const key = tag.toLowerCase()
      if (lowerExisting.has(key)) continue
      lowerExisting.add(key)
      next.push(tag)
    }
    if (next.length) setTags([...tags, ...next])
  }

  function commitTagInput() {
    const parts = tagInput.split(/[,;\n\t]+/)
    addTags(parts)
    setTagInput('')
  }

  function handleFileSelect(file: File) {
    if (!IMAGE_ACCEPT.split(',').includes(file.type)) {
      toast.error('Sadece JPG, PNG veya WebP kabul edilir')
      return
    }
    if (file.size > MAX_IMAGE_BYTES) {
      toast.error('Dosya 10 MB sınırını aşıyor')
      return
    }
    setPendingImage(file)
  }

  function handleDocSelect(file: File) {
    if (file.size > MAX_DOC_BYTES) {
      toast.error('Doküman 50 MB sınırını aşıyor')
      return
    }
    setPendingDocs((prev) => [...prev, file])
  }

  function removeDoc(index: number) {
    setPendingDocs((prev) => prev.filter((_, i) => i !== index))
  }

  async function handleSave() {
    const trimmedName = name.trim()
    if (!trimmedName) {
      toast.error('Ad alanı zorunlu')
      return
    }
    setSaving(true)
    try {
      let productId: string
      if (isEdit && product) {
        const res = await updateProduct(product.id, {
          name: trimmedName,
          description: description.trim() || null,
          tags,
          is_active: isActive,
        })
        if (!res.success || !res.data) {
          toast.error(res.error || 'Ürün güncellenemedi')
          return
        }
        productId = res.data.id
      } else {
        const res = await createProduct({
          brand_id: brandId,
          type,
          name: trimmedName,
          description: description.trim() || null,
          tags,
          is_active: isActive,
        })
        if (!res.success || !res.data) {
          if (res.error === 'plan_limit_reached' && res.plan_limit) {
            onPlanLimit(res.plan_limit.message)
            return
          }
          if (res.error === 'rate_limit' && res.retry_after) {
            toast.error(`Çok hızlı. ${res.retry_after} sn sonra tekrar deneyin.`)
            return
          }
          toast.error(res.error || 'Ürün oluşturulamadı')
          return
        }
        productId = res.data.id
      }

      if (pendingImage) {
        const imgRes = await uploadProductImage(productId, pendingImage)
        if (!imgRes.success) {
          toast.error(imgRes.error || 'Görsel yüklenemedi (ürün kaydedildi)')
        }
      }

      for (const doc of pendingDocs) {
        const docRes = await uploadProductDocument(productId, doc)
        if (!docRes.success) {
          toast.error(`"${doc.name}" yüklenemedi`)
        }
      }

      toast.success(isEdit ? 'Ürün güncellendi' : 'Ürün eklendi')
      onSaved()
    } finally {
      setSaving(false)
    }
  }

  const currentImage = pendingPreview ?? product?.image_url ?? null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{isEdit ? 'Ürün/Hizmet Düzenle' : 'Yeni Ürün/Hizmet'}</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Type selector */}
          <div className="space-y-1.5">
            <Label>Tür</Label>
            <div className="grid grid-cols-2 gap-2">
              <TypeButton
                active={type === 'product'}
                disabled={isEdit}
                onClick={() => setType('product')}
                icon={<Package className="w-4 h-4" />}
                label="Ürün"
              />
              <TypeButton
                active={type === 'service'}
                disabled={isEdit}
                onClick={() => setType('service')}
                icon={<Wrench className="w-4 h-4" />}
                label="Hizmet"
              />
            </div>
            {isEdit && (
              <p className="text-xs text-gray-400">Tür oluşturulduktan sonra değiştirilemez.</p>
            )}
          </div>

          <div className="space-y-1.5">
            <Label>Ad</Label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={type === 'service' ? 'Örn: Web Sitesi Tasarımı' : 'Örn: SporXL Koşu Ayakkabısı'}
            />
          </div>

          <div className="space-y-1.5">
            <Label>Açıklama</Label>
            <Textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Ürün/hizmetin ayırt edici özellikleri, hedef kitle, fiyat..."
              rows={3}
            />
          </div>

          <div className="space-y-1.5">
            <Label>Etiketler</Label>
            <div className="flex gap-2">
              <Input
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                placeholder="kategori, özellik"
                className="text-sm"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ',' || e.key === ';') {
                    e.preventDefault()
                    commitTagInput()
                  }
                }}
                onPaste={(e) => {
                  const pasted = e.clipboardData.getData('text')
                  if (/[,;\n\t]/.test(pasted)) {
                    e.preventDefault()
                    addTags(pasted.split(/[,;\n\t]+/))
                  }
                }}
                onBlur={() => {
                  if (tagInput.trim()) commitTagInput()
                }}
              />
              <Button variant="outline" size="sm" onClick={commitTagInput}>
                Ekle
              </Button>
            </div>
            <div className="flex flex-wrap gap-1.5 min-h-[40px] p-2 border border-gray-200 rounded-md bg-white">
              {tags.length === 0 ? (
                <span className="text-xs text-gray-400 self-center">Henüz etiket yok</span>
              ) : (
                tags.map((t) => (
                  <Badge key={t} variant="secondary" className="gap-1 text-xs">
                    {t}
                    <button onClick={() => setTags(tags.filter((x) => x !== t))}>
                      <X className="w-3 h-3" />
                    </button>
                  </Badge>
                ))
              )}
            </div>
          </div>

          {/* Image upload */}
          <div className="space-y-1.5">
            <Label>Görsel (opsiyonel)</Label>
            <div
              className="relative border-2 border-dashed border-gray-200 rounded-xl p-4 flex flex-col items-center justify-center gap-2 cursor-pointer hover:border-blue-400 hover:bg-blue-50/30 transition-colors"
              onClick={() => fileInputRef.current?.click()}
            >
              {currentImage ? (
                <>
                  {pendingPreview ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={pendingPreview}
                      alt="Ürün görseli önizleme"
                      className="max-h-32 rounded-lg object-contain"
                    />
                  ) : (
                    <Image
                      src={currentImage}
                      alt="Ürün görseli"
                      width={200}
                      height={128}
                      className="max-h-32 rounded-lg object-contain"
                    />
                  )}
                  {pendingImage && (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation()
                        setPendingImage(null)
                      }}
                      className="absolute top-2 right-2 w-7 h-7 rounded-full bg-white border border-gray-200 shadow-sm flex items-center justify-center text-gray-600 hover:text-red-600"
                      aria-label="İptal"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </>
              ) : (
                <>
                  <Upload className="w-5 h-5 text-gray-400" />
                  <p className="text-sm text-gray-500">Dosya seç</p>
                  <p className="text-xs text-gray-400">JPG, PNG veya WebP · Maks. 10 MB</p>
                </>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept={IMAGE_ACCEPT}
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) {
                    handleFileSelect(file)
                    e.target.value = ''
                  }
                }}
              />
            </div>
          </div>

          {/* Document upload */}
          <div className="space-y-1.5">
            <Label>Ürün/Hizmet Dokümanları (opsiyonel)</Label>
            <div
              className="border-2 border-dashed border-gray-200 rounded-xl p-4 flex flex-col items-center justify-center gap-2 cursor-pointer hover:border-blue-400 hover:bg-blue-50/30 transition-colors"
              onClick={() => docInputRef.current?.click()}
            >
              <Upload className="w-5 h-5 text-gray-400" />
              <p className="text-sm text-gray-500">PDF, Word veya Excel yükleyin</p>
              <p className="text-xs text-gray-400">Maks. 50 MB · Birden fazla ekleyebilirsiniz</p>
              <input
                ref={docInputRef}
                type="file"
                accept={DOC_ACCEPT}
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) {
                    handleDocSelect(file)
                    e.target.value = ''
                  }
                }}
              />
            </div>
            {pendingDocs.length > 0 && (
              <div className="space-y-1.5 mt-2">
                {pendingDocs.map((doc, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between p-3 border border-gray-200 rounded-xl bg-gray-50"
                  >
                    <div className="flex items-center gap-2 min-w-0">
                      <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0">
                        <FileText className="w-4 h-4 text-blue-500" />
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-gray-800 truncate">{doc.name}</p>
                        <p className="text-xs text-gray-400">{(doc.size / 1024).toFixed(0)} KB</p>
                      </div>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeDoc(i)}
                      className="ml-2 p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-md transition-colors flex-shrink-0"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Active toggle */}
          <div className="flex items-center justify-between pt-1">
            <div>
              <Label className={isActive ? 'text-gray-900' : 'text-gray-400'}>
                {isActive ? 'Aktif' : 'Pasif'}
              </Label>
              <p className="text-xs text-gray-500">Pasif ürünler içerik üretiminde gösterilmez.</p>
            </div>
            <Switch checked={isActive} onCheckedChange={setIsActive} />
          </div>
        </div>

        <div className="flex justify-end gap-2 pt-2">
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={saving}>
            İptal
          </Button>
          <Button onClick={handleSave} disabled={saving}>
            {saving && <Loader2 className="w-4 h-4 animate-spin mr-1" />}
            {isEdit ? 'Kaydet' : 'Ekle'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

function TypeButton({
  active,
  disabled,
  onClick,
  icon,
  label,
}: {
  active: boolean
  disabled: boolean
  onClick: () => void
  icon: React.ReactNode
  label: string
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      disabled={disabled}
      className={`flex items-center justify-center gap-2 rounded-lg border p-3 text-sm transition-colors ${
        active
          ? 'border-blue-500 bg-blue-50 text-blue-700'
          : 'border-gray-200 bg-white text-gray-600 hover:border-blue-300'
      } ${disabled ? 'opacity-60 cursor-not-allowed' : 'cursor-pointer'}`}
    >
      {icon}
      {label}
    </button>
  )
}
