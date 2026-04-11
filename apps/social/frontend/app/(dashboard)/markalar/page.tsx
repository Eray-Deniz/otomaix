'use client'

export const dynamic = 'force-dynamic'

import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import { useAppStore, Brand } from '@/lib/store'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import {
  Building2,
  Plus,
  Pencil,
  Trash2,
  Loader2,
  Check,
} from 'lucide-react'
import Link from 'next/link'
import Image from 'next/image'

// ─── Types ──────────────────────────────────────────────────────────────────

interface BrandDetail extends Brand {
  description: string | null
  website_url: string | null
  sector: string | null
  created_at: string
}

const SECTORS = [
  'Tekstil', 'Gıda', 'İnşaat', 'Turizm', 'Perakende',
  'Teknoloji', 'Sağlık', 'Eğitim', 'Finans', 'Hizmet', 'Diğer',
]

// ─── Page ───���────────────────────────────────────────────────────────────────

export default function MarkalarlPage() {
  const { currentWorkspace, currentBrand, setBrands, switchBrand, brands } = useAppStore()

  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [deleteId, setDeleteId] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  const [form, setForm] = useState({ name: '', sector: '', description: '' })

  async function loadBrands() {
    if (!currentWorkspace?.id) return
    const res = await api.get<BrandDetail[]>(`/brands?workspace_id=${currentWorkspace.id}`)
    if (res.success && res.data) {
      setBrands(res.data)
    }
    setLoading(false)
  }

  useEffect(() => {
    loadBrands() // eslint-disable-line react-hooks/exhaustive-deps
  }, [currentWorkspace?.id])

  async function handleCreate() {
    if (!currentWorkspace?.id || !form.name.trim()) return
    setSaving(true)
    try {
      const res = await api.post<BrandDetail>('/brands', {
        workspace_id: currentWorkspace.id,
        name: form.name.trim(),
        sector: form.sector || null,
        description: form.description || null,
      })
      if (res.success && res.data) {
        toast.success('Marka oluşturuldu')
        setShowAdd(false)
        setForm({ name: '', sector: '', description: '' })
        await loadBrands()
        // Yeni markayı aktif yap
        switchBrand(res.data)
      } else {
        toast.error('Marka oluşturulamadı')
      }
    } catch {
      toast.error('Bir hata oluştu')
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete(brandId: string) {
    try {
      const { data: session } = await (await import('@/lib/supabase')).createSupabaseClient().auth.getSession()
      const token = session?.session?.access_token
      const delRes = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/brands/${brandId}`, {
        method: 'DELETE',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      })
      if (delRes.ok) {
        toast.success('Marka silindi')
        setDeleteId(null)
        await loadBrands()
        // Silinen marka aktifse başkasına geç
        if (currentBrand?.id === brandId) {
          const remaining = brands.filter((b) => b.id !== brandId)
          if (remaining.length > 0) switchBrand(remaining[0])
        }
      } else {
        toast.error('Silinemedi')
      }
    } catch {
      toast.error('Bir hata oluştu')
    }
  }

  const initials = (name: string) =>
    name.split(' ').slice(0, 2).map((w) => w[0]).join('').toUpperCase()

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="w-8 h-8 text-blue-500 animate-spin" />
      </div>
    )
  }

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Building2 className="w-6 h-6 text-blue-600" />
            Markalar
          </h1>
          <p className="text-gray-500 text-sm mt-1">{brands.length} aktif marka</p>
        </div>
        <Button
          onClick={() => setShowAdd(true)}
          disabled={!currentWorkspace?.id}
          title={!currentWorkspace?.id ? 'Çalışma alanı yükleniyor...' : undefined}
          className="gap-2"
        >
          <Plus className="w-4 h-4" />
          Yeni Marka
        </Button>
      </div>

      {/* Marka Grid */}
      {brands.length === 0 ? (
        <Card>
          <CardContent className="py-16 text-center">
            <Building2 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500 mb-4">Henüz marka eklenmemiş.</p>
            <Button onClick={() => setShowAdd(true)} className="gap-2">
              <Plus className="w-4 h-4" /> İlk Markayı Ekle
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-3 gap-4">
          {brands.map((brand) => {
            const isActive = currentBrand?.id === brand.id
            return (
              <Card
                key={brand.id}
                className={`relative hover:shadow-md transition-shadow cursor-pointer ${
                  isActive ? 'ring-2 ring-blue-500' : ''
                }`}
                onClick={() => switchBrand(brand)}
              >
                {isActive && (
                  <div className="absolute top-2 right-2 w-5 h-5 bg-blue-600 rounded-full flex items-center justify-center">
                    <Check className="w-3 h-3 text-white" />
                  </div>
                )}
                <CardContent className="pt-5 pb-4">
                  {/* Logo / Avatar */}
                  <div className="flex items-center gap-3 mb-4">
                    <div className="w-10 h-10 rounded-xl bg-blue-100 flex items-center justify-center overflow-hidden shrink-0">
                      {brand.logo_light_url ? (
                        <Image
                          src={brand.logo_light_url}
                          alt={brand.name}
                          width={40}
                          height={40}
                          className="object-contain"
                        />
                      ) : (
                        <span className="text-sm font-bold text-blue-600">
                          {initials(brand.name)}
                        </span>
                      )}
                    </div>
                    <div className="min-w-0">
                      <p className="font-semibold text-gray-900 truncate">{brand.name}</p>
                      {brand.sector && (
                        <p className="text-xs text-gray-400 capitalize">{brand.sector}</p>
                      )}
                    </div>
                  </div>

                  {/* Aksiyon butonları */}
                  <div className="flex gap-2">
                    <Link href="/marka-ayarlari" className="flex-1" onClick={() => switchBrand(brand)}>
                      <Button
                        size="sm"
                        variant="outline"
                        className="w-full gap-1.5 text-xs"
                        onClick={(e) => e.stopPropagation()}
                      >
                        <Pencil className="w-3 h-3" />
                        Düzenle
                      </Button>
                    </Link>
                    <Button
                      size="sm"
                      variant="outline"
                      className="px-2.5 text-red-500 hover:text-red-600 hover:bg-red-50 border-red-200"
                      onClick={(e) => {
                        e.stopPropagation()
                        setDeleteId(brand.id)
                      }}
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}

      {/* Yeni Marka Modalı */}
      {showAdd && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-md mx-4 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Yeni Marka Ekle</h2>
            <div className="space-y-4">
              <div className="space-y-1.5">
                <Label>Marka Adı *</Label>
                <Input
                  placeholder="Örn: Kahve Dünyası"
                  value={form.name}
                  onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                />
              </div>
              <div className="space-y-1.5">
                <Label>Sektör</Label>
                <select
                  className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                  value={form.sector}
                  onChange={(e) => setForm((p) => ({ ...p, sector: e.target.value }))}
                >
                  <option value="">Seçin (opsiyonel)</option>
                  {SECTORS.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>
              <div className="space-y-1.5">
                <Label>Açıklama</Label>
                <Input
                  placeholder="Kısa açıklama (opsiyonel)"
                  value={form.description}
                  onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
                />
              </div>
            </div>
            <div className="flex gap-2 mt-6">
              <Button
                className="flex-1"
                onClick={handleCreate}
                disabled={!form.name.trim() || saving || !currentWorkspace?.id}
              >
                {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Oluştur'}
              </Button>
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => { setShowAdd(false); setForm({ name: '', sector: '', description: '' }) }}
              >
                İptal
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Silme Onay Modalı */}
      {deleteId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white rounded-2xl shadow-xl w-full max-w-sm mx-4 p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-2">Markayı Sil</h2>
            <p className="text-sm text-gray-500 mb-6">
              Bu markayı ve tüm içeriklerini silmek istediğinizden emin misiniz? Bu işlem geri alınamaz.
            </p>
            <div className="flex gap-2">
              <Button
                variant="destructive"
                className="flex-1"
                onClick={() => handleDelete(deleteId)}
              >
                Sil
              </Button>
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => setDeleteId(null)}
              >
                İptal
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
