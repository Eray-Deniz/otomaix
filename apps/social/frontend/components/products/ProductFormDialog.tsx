'use client'

import { useEffect, useRef, useState } from 'react'
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
import {
  Loader2,
  X,
  Upload,
  Package,
  Wrench,
  FileText,
  Trash2,
  Star,
  Plus,
  GripVertical,
} from 'lucide-react'
import {
  createProduct,
  updateProduct,
  uploadProductImage,
  uploadProductDocument,
  fetchProductImages,
  deleteProductImage,
  setProductImagePrimary,
  reorderProductImages,
} from '@/lib/api/products'
import type { Product, ProductImage, ProductType } from '@/lib/products.types'
import { cn } from '@/lib/utils'

const IMAGE_ACCEPT = 'image/jpeg,image/png,image/webp'
const MAX_IMAGE_BYTES = 10 * 1024 * 1024
const MAX_IMAGES_PER_PRODUCT = 5
const DOC_ACCEPT = '.pdf,.doc,.docx,.xls,.xlsx,.txt'
const MAX_DOC_BYTES = 50 * 1024 * 1024

// Henüz upload edilmemiş görseller (yeni ürün modunda biriktirilir).
interface PendingImage {
  tempId: string
  file: File
  blobUrl: string
  isPrimary: boolean
}

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
  const [highlight, setHighlight] = useState('')
  const [tags, setTags] = useState<string[]>([])
  const [tagInput, setTagInput] = useState('')
  const [isActive, setIsActive] = useState(true)

  // Sprint 1 (Çoklu Görsel) — multi-image state.
  // Edit modunda: existingImages DB'den fetch edilir, her aksiyon (sil/primary/reorder)
  // anlık API çağrısıyla DB'yi günceller; pendingImages save'de toplu upload edilir.
  // Yeni ürün modunda: yalnız pendingImages biriktirilir, save'de ürün yaratıldıktan
  // sonra sırasıyla upload edilir.
  const [existingImages, setExistingImages] = useState<ProductImage[]>([])
  const [pendingImages, setPendingImages] = useState<PendingImage[]>([])
  const [imageActionBusy, setImageActionBusy] = useState(false)

  const [pendingDocs, setPendingDocs] = useState<File[]>([])
  const [saving, setSaving] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const docInputRef = useRef<HTMLInputElement>(null)
  const dragSrcKey = useRef<string | null>(null)

  // Toplam görsel sayısı (limit kontrolü için).
  const totalImages = existingImages.length + pendingImages.length

  useEffect(() => {
    if (!open) return
    if (product) {
      setType(product.type)
      setName(product.name)
      setDescription(product.description ?? '')
      setHighlight(product.highlight ?? '')
      setTags(product.tags ?? [])
      setIsActive(product.is_active)
      // Backend listeden gelen images alanını kullan; yoksa /images endpoint'inden çek.
      if (product.images && product.images.length > 0) {
        setExistingImages(product.images)
      } else if (product.id) {
        // Eski response (geri uyumluluk) veya boş ürün — endpoint'ten kesin liste al.
        void refreshExistingImages(product.id)
      } else {
        setExistingImages([])
      }
    } else {
      setType('product')
      setName('')
      setDescription('')
      setHighlight('')
      setTags([])
      setIsActive(true)
      setExistingImages([])
    }
    setTagInput('')
    setPendingImages([])
    setPendingDocs([])
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open, product])

  // Pending görsellerin blob URL'lerini cleanup et (modal kapanınca veya re-init'te).
  useEffect(() => {
    return () => {
      pendingImages.forEach((p) => URL.revokeObjectURL(p.blobUrl))
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open])

  async function refreshExistingImages(productId: string) {
    const res = await fetchProductImages(productId)
    if (res.success && res.data) {
      setExistingImages(res.data.items)
    }
  }

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

  function handleImageSelect(file: File) {
    if (!IMAGE_ACCEPT.split(',').includes(file.type)) {
      toast.error('Sadece JPG, PNG veya WebP kabul edilir')
      return
    }
    if (file.size > MAX_IMAGE_BYTES) {
      toast.error(`"${file.name}" 10 MB sınırını aşıyor`)
      return
    }
    if (totalImages >= MAX_IMAGES_PER_PRODUCT) {
      toast.error(`En fazla ${MAX_IMAGES_PER_PRODUCT} görsel yükleyebilirsiniz`)
      return
    }
    const tempId = `p_${Math.random().toString(36).slice(2, 10)}`
    const blobUrl = URL.createObjectURL(file)
    // İlk görselse otomatik primary (backend'de de aynı mantık var; yeni ürün modunda
    // upload sırasında ilk yüklenen primary olur).
    const isPrimary = totalImages === 0
    setPendingImages((prev) => [...prev, { tempId, file, blobUrl, isPrimary }])
  }

  function removePendingImage(tempId: string) {
    setPendingImages((prev) => {
      const target = prev.find((p) => p.tempId === tempId)
      if (target) URL.revokeObjectURL(target.blobUrl)
      const filtered = prev.filter((p) => p.tempId !== tempId)
      // Primary kaldırılıyorsa, kalan ilk pending'i (yoksa ilk existing'i) primary yap.
      if (target?.isPrimary && filtered.length > 0) {
        filtered[0].isPrimary = true
      } else if (target?.isPrimary && existingImages.length > 0) {
        // Existing varken pending primary kaldırıldı — existing zaten kendi primary'sini taşır
      }
      return filtered
    })
  }

  function setPendingPrimary(tempId: string) {
    setPendingImages((prev) =>
      prev.map((p) => ({ ...p, isPrimary: p.tempId === tempId }))
    )
    // Existing primary'yi pending devraldı; existing tarafında primary "kaybedilmiş" görünür.
    // Save sırasında pending upload edildikten sonra PATCH /primary çağrılır.
    setExistingImages((prev) => prev.map((e) => ({ ...e, is_primary: false })))
  }

  async function handleDeleteExisting(image: ProductImage) {
    if (!product) return
    setImageActionBusy(true)
    try {
      const res = await deleteProductImage(product.id, image.id)
      if (!res.success) {
        toast.error(res.error || 'Görsel silinemedi')
        return
      }
      // Backend cascade: ana görselse bir sonrakini primary yapar — yeniden fetch et.
      await refreshExistingImages(product.id)
      toast.success('Görsel silindi')
    } finally {
      setImageActionBusy(false)
    }
  }

  async function handleSetExistingPrimary(image: ProductImage) {
    if (!product || image.is_primary) return
    setImageActionBusy(true)
    try {
      const res = await setProductImagePrimary(product.id, image.id)
      if (!res.success) {
        toast.error(res.error || 'Ana görsel değiştirilemedi')
        return
      }
      await refreshExistingImages(product.id)
      // Pending tarafında primary varsa, o da artık primary değil (existing devraldı).
      setPendingImages((prev) => prev.map((p) => ({ ...p, isPrimary: false })))
    } finally {
      setImageActionBusy(false)
    }
  }

  async function commitReorder(newExistingOrder: ProductImage[]) {
    if (!product) return
    setExistingImages(newExistingOrder)
    setImageActionBusy(true)
    try {
      const res = await reorderProductImages(
        product.id,
        newExistingOrder.map((i) => i.id)
      )
      if (!res.success) {
        toast.error(res.error || 'Sıra kaydedilemedi')
        // Rollback yerine yeniden fetch (state divergence riski)
        await refreshExistingImages(product.id)
      }
    } finally {
      setImageActionBusy(false)
    }
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

  // Drag-drop: existing görseller arasında native HTML5 DnD ile sıralama.
  // Pending görseller upload edilmeden sıralanmaz (upload sırasıyla position 0..N alır).
  function onDragStart(key: string) {
    dragSrcKey.current = key
  }

  function onDragOver(e: React.DragEvent) {
    e.preventDefault()
  }

  function onDropOnExisting(targetId: string) {
    const srcKey = dragSrcKey.current
    dragSrcKey.current = null
    if (!srcKey || !srcKey.startsWith('e:')) return
    const srcId = srcKey.slice(2)
    if (srcId === targetId) return
    const arr = [...existingImages]
    const fromIdx = arr.findIndex((i) => i.id === srcId)
    const toIdx = arr.findIndex((i) => i.id === targetId)
    if (fromIdx < 0 || toIdx < 0) return
    const [moved] = arr.splice(fromIdx, 1)
    arr.splice(toIdx, 0, moved)
    void commitReorder(arr)
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
          highlight: highlight.trim() || null,
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
          highlight: highlight.trim() || null,
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

      // Pending görselleri yükle (sırayla — backend her POST'ta position bir sonraki).
      // Yeni ürün modunda ilk yüklenen otomatik primary; eğer kullanıcı pending tarafından
      // farklı bir tile'ı primary işaretlediyse, upload sonrası PATCH /primary ile düzeltilir.
      const uploadedPending: { tempId: string; image: ProductImage }[] = []
      for (const p of pendingImages) {
        const imgRes = await uploadProductImage(productId, p.file)
        if (!imgRes.success || !imgRes.data) {
          toast.error(imgRes.error || `"${p.file.name}" yüklenemedi`)
          continue
        }
        uploadedPending.push({ tempId: p.tempId, image: imgRes.data })
      }

      // Pending arasında "primary" işaretli olan varsa ve o, ilk yüklenen değilse,
      // upload bittikten sonra PATCH /primary ile düzelt.
      const primaryPending = pendingImages.find((p) => p.isPrimary)
      if (primaryPending) {
        const uploadedMatch = uploadedPending.find((u) => u.tempId === primaryPending.tempId)
        if (uploadedMatch && !uploadedMatch.image.is_primary) {
          await setProductImagePrimary(productId, uploadedMatch.image.id)
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
              placeholder="Teknik bilgiler, malzemeler, ölçüler, kullanım detayları..."
              rows={3}
            />
            <p className="text-xs text-gray-500">
              Sadece AI bağlamına gider, görsele basılmaz. Hammadde/ölçü gibi teknik
              detayları buraya yazabilirsiniz.
            </p>
          </div>

          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <Label>
                Öne Çıkan Vurgu
                <span className="ml-1 font-normal text-gray-400">(opsiyonel)</span>
              </Label>
              <span
                className={cn(
                  'text-xs',
                  highlight.length > 60 ? 'text-red-500' : 'text-gray-400'
                )}
              >
                {highlight.length}/60
              </span>
            </div>
            <Input
              value={highlight}
              onChange={(e) => setHighlight(e.target.value.slice(0, 60))}
              placeholder="örn. Konfor ve şıklık bir arada"
              maxLength={60}
            />
            <p className="text-xs text-gray-500">
              Kısa pazarlama mesajı. Görselde ve caption&apos;da öne çıkar. Boş
              bırakırsanız ürün adı kullanılır.
            </p>
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

          {/* Sprint 1 — Çoklu görsel grid */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between">
              <Label>
                Görseller (opsiyonel)
                <span className="ml-1 font-normal text-gray-400">
                  {totalImages}/{MAX_IMAGES_PER_PRODUCT}
                </span>
              </Label>
              {totalImages > 1 && (
                <span className="text-xs text-gray-400">
                  ★ ana görsel · sürükle-bırak ile sırala
                </span>
              )}
            </div>

            <div className="grid grid-cols-3 gap-2">
              {/* Mevcut görseller (drag-drop sıralanabilir, anlık aksiyonlar) */}
              {existingImages.map((img) => (
                <div
                  key={`e:${img.id}`}
                  draggable={isEdit && !imageActionBusy}
                  onDragStart={() => onDragStart(`e:${img.id}`)}
                  onDragOver={onDragOver}
                  onDrop={() => onDropOnExisting(img.id)}
                  className="group relative aspect-square rounded-xl border border-gray-200 overflow-hidden bg-gray-50"
                >
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img
                    src={img.image_url}
                    alt={img.label ?? 'Ürün görseli'}
                    className="w-full h-full object-cover"
                  />
                  {img.is_primary && (
                    <div className="absolute top-1 left-1 px-1.5 py-0.5 rounded-md bg-amber-400 text-white text-[10px] font-semibold flex items-center gap-0.5">
                      <Star className="w-3 h-3 fill-current" />
                      Ana
                    </div>
                  )}
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors flex items-end justify-end p-1.5 gap-1 opacity-0 group-hover:opacity-100">
                    {!img.is_primary && (
                      <button
                        type="button"
                        onClick={() => handleSetExistingPrimary(img)}
                        disabled={imageActionBusy}
                        className="w-7 h-7 rounded-full bg-white shadow-sm flex items-center justify-center text-amber-500 hover:bg-amber-50"
                        title="Ana görsel yap"
                      >
                        <Star className="w-3.5 h-3.5" />
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => handleDeleteExisting(img)}
                      disabled={imageActionBusy}
                      className="w-7 h-7 rounded-full bg-white shadow-sm flex items-center justify-center text-red-500 hover:bg-red-50"
                      title="Sil"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  {existingImages.length > 1 && (
                    <div className="absolute bottom-1 left-1 w-5 h-5 rounded bg-white/90 flex items-center justify-center text-gray-400">
                      <GripVertical className="w-3 h-3" />
                    </div>
                  )}
                </div>
              ))}

              {/* Pending (yüklenmemiş) görseller — yeni ürün modunda veya edit modunda yeni ek */}
              {pendingImages.map((p) => (
                <div
                  key={`p:${p.tempId}`}
                  className="group relative aspect-square rounded-xl border border-blue-200 overflow-hidden bg-blue-50/30"
                >
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img src={p.blobUrl} alt="Yüklenecek görsel" className="w-full h-full object-cover" />
                  {p.isPrimary && (
                    <div className="absolute top-1 left-1 px-1.5 py-0.5 rounded-md bg-amber-400 text-white text-[10px] font-semibold flex items-center gap-0.5">
                      <Star className="w-3 h-3 fill-current" />
                      Ana
                    </div>
                  )}
                  <div className="absolute top-1 right-1 px-1.5 py-0.5 rounded-md bg-blue-500 text-white text-[10px] font-semibold">
                    yeni
                  </div>
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition-colors flex items-end justify-end p-1.5 gap-1 opacity-0 group-hover:opacity-100">
                    {!p.isPrimary && (
                      <button
                        type="button"
                        onClick={() => setPendingPrimary(p.tempId)}
                        className="w-7 h-7 rounded-full bg-white shadow-sm flex items-center justify-center text-amber-500 hover:bg-amber-50"
                        title="Ana görsel yap"
                      >
                        <Star className="w-3.5 h-3.5" />
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => removePendingImage(p.tempId)}
                      className="w-7 h-7 rounded-full bg-white shadow-sm flex items-center justify-center text-red-500 hover:bg-red-50"
                      title="Kaldır"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}

              {/* Ekle tile — limit aşılmadıysa görünür */}
              {totalImages < MAX_IMAGES_PER_PRODUCT && (
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="aspect-square rounded-xl border-2 border-dashed border-gray-200 flex flex-col items-center justify-center gap-1 text-gray-400 hover:border-blue-400 hover:bg-blue-50/30 transition-colors"
                >
                  <Plus className="w-5 h-5" />
                  <span className="text-xs">Ekle</span>
                </button>
              )}
            </div>

            {totalImages === 0 && (
              <p className="text-xs text-gray-400">JPG, PNG veya WebP · Maks. 10 MB · En fazla {MAX_IMAGES_PER_PRODUCT} görsel</p>
            )}
            {totalImages > 0 && totalImages >= MAX_IMAGES_PER_PRODUCT && (
              <p className="text-xs text-amber-600">Maksimum görsel sayısına ulaşıldı.</p>
            )}

            <input
              ref={fileInputRef}
              type="file"
              accept={IMAGE_ACCEPT}
              multiple
              className="hidden"
              onChange={(e) => {
                const files = Array.from(e.target.files ?? [])
                files.forEach(handleImageSelect)
                e.target.value = ''
              }}
            />
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
          <Button onClick={handleSave} disabled={saving || imageActionBusy}>
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

