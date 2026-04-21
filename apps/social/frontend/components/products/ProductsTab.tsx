'use client'

import { useCallback, useEffect, useState } from 'react'
import Image from 'next/image'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { api } from '@/lib/api'
import { toast } from 'sonner'
import {
  Loader2,
  Plus,
  Pencil,
  FileText,
  Package,
  Wrench,
} from 'lucide-react'
import { UpgradeModal } from '@/components/billing/UpgradeModal'
import {
  fetchProducts,
  deleteProduct as deleteProductApi,
} from '@/lib/api/products'
import type { Product, ProductType } from '@/lib/products.types'
import { ProductFormDialog } from './ProductFormDialog'
import { ProductDocumentsDialog } from './ProductDocumentsDialog'

type TypeFilter = 'all' | ProductType
type ActiveFilter = 'all' | 'active' | 'inactive'

interface BillingCurrent {
  limits: { max_products_per_brand: number | null }
  usage: { products_per_brand: Record<string, number> }
}

export function ProductsTab({ brandId }: { brandId: string }) {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [typeFilter, setTypeFilter] = useState<TypeFilter>('all')
  const [activeFilter, setActiveFilter] = useState<ActiveFilter>('all')
  const [formOpen, setFormOpen] = useState(false)
  const [editing, setEditing] = useState<Product | null>(null)
  const [docsFor, setDocsFor] = useState<Product | null>(null)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const [upgradeMessage, setUpgradeMessage] = useState<string | null>(null)
  const [quota, setQuota] = useState<{ used: number; max: number | null } | null>(null)

  const loadProducts = useCallback(async () => {
    setLoading(true)
    const filters: { type?: ProductType; active?: boolean } = {}
    if (typeFilter !== 'all') filters.type = typeFilter
    if (activeFilter !== 'all') filters.active = activeFilter === 'active'
    const res = await fetchProducts(brandId, filters)
    if (res.success && res.data) {
      setProducts(res.data.products ?? [])
    } else {
      toast.error(res.error || 'Ürünler yüklenemedi')
    }
    setLoading(false)
  }, [brandId, typeFilter, activeFilter])

  const loadQuota = useCallback(async () => {
    const res = await api.get<BillingCurrent>('/billing/current')
    if (res.success && res.data) {
      const used = res.data.usage?.products_per_brand?.[brandId] ?? 0
      const max = res.data.limits?.max_products_per_brand ?? null
      setQuota({ used, max })
    }
  }, [brandId])

  useEffect(() => {
    loadProducts()
  }, [loadProducts])

  useEffect(() => {
    loadQuota()
  }, [loadQuota])

  async function handleDelete(product: Product) {
    if (!confirm(`"${product.name}" kalıcı olarak silinsin mi? Bu işlem geri alınamaz.`)) return
    setDeletingId(product.id)
    const res = await deleteProductApi(product.id)
    if (res.success) {
      toast.success('Ürün silindi')
      setProducts((prev) => prev.filter((p) => p.id !== product.id))
      loadQuota()
    } else {
      toast.error(res.error || 'Ürün silinemedi')
    }
    setDeletingId(null)
  }

  function handleCreateClick() {
    if (quota && quota.max !== null && quota.used >= quota.max) {
      setUpgradeMessage(
        `Bu markada en fazla ${quota.max} ürün/hizmet tanımlayabilirsiniz. Daha fazlası için planınızı yükseltin.`
      )
      return
    }
    setEditing(null)
    setFormOpen(true)
  }

  function handleEditClick(product: Product) {
    setEditing(product)
    setFormOpen(true)
  }

  function handleFormSaved() {
    setFormOpen(false)
    setEditing(null)
    loadProducts()
    loadQuota()
  }

  const quotaLabel = quota
    ? quota.max === null
      ? `${quota.used} / Sınırsız`
      : `${quota.used} / ${quota.max}`
    : null

  return (
    <div className="space-y-5">
      {upgradeMessage && (
        <UpgradeModal message={upgradeMessage} onClose={() => setUpgradeMessage(null)} />
      )}

      {/* Header: filters + quota + add button */}
      <div className="flex flex-wrap items-center gap-2">
        <div className="flex items-center gap-1.5">
          <FilterChip active={typeFilter === 'all'} onClick={() => setTypeFilter('all')}>
            Tümü
          </FilterChip>
          <FilterChip active={typeFilter === 'product'} onClick={() => setTypeFilter('product')}>
            Ürün
          </FilterChip>
          <FilterChip active={typeFilter === 'service'} onClick={() => setTypeFilter('service')}>
            Hizmet
          </FilterChip>
        </div>
        <div className="flex items-center gap-1.5">
          <FilterChip active={activeFilter === 'all'} onClick={() => setActiveFilter('all')}>
            Hepsi
          </FilterChip>
          <FilterChip active={activeFilter === 'active'} onClick={() => setActiveFilter('active')}>
            Aktif
          </FilterChip>
          <FilterChip
            active={activeFilter === 'inactive'}
            onClick={() => setActiveFilter('inactive')}
          >
            Pasif
          </FilterChip>
        </div>
        <div className="ml-auto flex items-center gap-3">
          {quotaLabel && (
            <Badge variant="secondary" className="text-xs">
              {quotaLabel} ürün
            </Badge>
          )}
          <Button size="sm" onClick={handleCreateClick} className="gap-1.5">
            <Plus className="w-4 h-4" />
            Yeni Ekle
          </Button>
        </div>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
        </div>
      ) : products.length === 0 ? (
        <div className="rounded-xl border border-dashed border-gray-200 p-10 text-center">
          <Package className="w-8 h-8 text-gray-300 mx-auto mb-3" />
          <p className="text-sm text-gray-500">
            Henüz ürün veya hizmet eklenmedi. İçeriklerde kullanmak için buradan ekleyin.
          </p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {products.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              deleting={deletingId === product.id}
              onEdit={() => handleEditClick(product)}
              onDelete={() => handleDelete(product)}
              onOpenDocs={() => setDocsFor(product)}
            />
          ))}
        </div>
      )}

      <ProductFormDialog
        open={formOpen}
        onOpenChange={setFormOpen}
        brandId={brandId}
        product={editing}
        onSaved={handleFormSaved}
        onPlanLimit={(message) => {
          setFormOpen(false)
          setUpgradeMessage(message)
        }}
      />

      <ProductDocumentsDialog
        open={docsFor !== null}
        onOpenChange={(open) => {
          if (!open) setDocsFor(null)
        }}
        product={docsFor}
        onChanged={loadProducts}
      />
    </div>
  )
}

function FilterChip({
  active,
  onClick,
  children,
}: {
  active: boolean
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`text-xs rounded-full px-3 py-1 border transition-colors ${
        active
          ? 'bg-blue-600 text-white border-blue-600'
          : 'bg-white text-gray-600 border-gray-200 hover:border-blue-300 hover:text-blue-600'
      }`}
    >
      {children}
    </button>
  )
}

function ProductCard({
  product,
  deleting,
  onEdit,
  onDelete,
  onOpenDocs,
}: {
  product: Product
  deleting: boolean
  onEdit: () => void
  onDelete: () => void
  onOpenDocs: () => void
}) {
  const TypeIcon = product.type === 'service' ? Wrench : Package
  return (
    <Card className="overflow-hidden">
      <div className="aspect-video bg-gray-50 relative flex items-center justify-center">
        {product.image_url ? (
          <Image
            src={product.image_url}
            alt={product.name}
            width={400}
            height={225}
            className="w-full h-full object-cover"
          />
        ) : (
          <TypeIcon className="w-10 h-10 text-gray-300" />
        )}
        {!product.is_active && (
          <Badge
            variant="secondary"
            className="absolute top-2 left-2 text-[10px] bg-gray-800/80 text-white border-0"
          >
            Pasif
          </Badge>
        )}
        <Badge
          variant="secondary"
          className="absolute top-2 right-2 text-[10px] bg-white/90 border-0"
        >
          {product.type === 'service' ? 'Hizmet' : 'Ürün'}
        </Badge>
      </div>
      <CardContent className="space-y-2 pt-2">
        <div>
          <p className="font-medium text-sm text-gray-900 truncate">{product.name}</p>
          {product.description && (
            <p className="text-xs text-gray-500 line-clamp-2 mt-0.5">{product.description}</p>
          )}
        </div>
        {(product.tags ?? []).length > 0 && (
          <div className="flex flex-wrap gap-1">
            {(product.tags ?? []).slice(0, 3).map((tag) => (
              <Badge key={tag} variant="secondary" className="text-[10px]">
                {tag}
              </Badge>
            ))}
            {(product.tags ?? []).length > 3 && (
              <span className="text-[10px] text-gray-400 self-center">
                +{(product.tags ?? []).length - 3}
              </span>
            )}
          </div>
        )}
        <div className="flex items-center justify-between pt-1">
          <button
            type="button"
            onClick={onOpenDocs}
            className="text-xs text-gray-500 hover:text-blue-600 flex items-center gap-1"
          >
            <FileText className="w-3.5 h-3.5" />
            {product.document_count} doküman
          </button>
          <div className="flex items-center gap-1">
            <Button size="sm" variant="ghost" className="h-7 px-2 text-xs gap-1" onClick={onEdit}>
              <Pencil className="w-3 h-3" />
              Düzenle
            </Button>
            <Button
              size="sm"
              variant="ghost"
              className="h-7 px-2 text-xs text-red-600 hover:text-red-700 hover:bg-red-50"
              onClick={onDelete}
              disabled={deleting}
            >
              {deleting ? <Loader2 className="w-3 h-3 animate-spin" /> : 'Sil'}
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
