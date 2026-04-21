'use client'

import { useCallback, useEffect, useRef, useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { toast } from 'sonner'
import { Loader2, Upload, FileText, Trash2 } from 'lucide-react'
import {
  fetchProductDocuments,
  uploadProductDocument,
  deleteProductDocument,
} from '@/lib/api/products'
import type { Product, ProductDocument } from '@/lib/products.types'

const DOC_ACCEPT = '.pdf,.doc,.docx,.xls,.xlsx,.txt'
const MAX_DOC_BYTES = 50 * 1024 * 1024

interface Props {
  open: boolean
  onOpenChange: (open: boolean) => void
  product: Product | null
  onChanged: () => void
}

export function ProductDocumentsDialog({ open, onOpenChange, product, onChanged }: Props) {
  const [documents, setDocuments] = useState<ProductDocument[]>([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [deletingId, setDeletingId] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const loadDocs = useCallback(async () => {
    if (!product) return
    setLoading(true)
    const res = await fetchProductDocuments(product.id)
    if (res.success && res.data) {
      setDocuments(res.data.documents)
    } else {
      toast.error(res.error || 'Dokümanlar yüklenemedi')
    }
    setLoading(false)
  }, [product])

  useEffect(() => {
    if (open && product) loadDocs()
  }, [open, product, loadDocs])

  async function handleUpload(file: File) {
    if (!product) return
    if (file.size > MAX_DOC_BYTES) {
      toast.error('Dosya 50 MB sınırını aşıyor')
      return
    }
    setUploading(true)
    const res = await uploadProductDocument(product.id, file)
    if (res.success && res.data) {
      setDocuments((prev) => [res.data as ProductDocument, ...prev])
      toast.success('Doküman yüklendi')
      onChanged()
    } else {
      toast.error(res.error || 'Doküman yüklenemedi')
    }
    setUploading(false)
  }

  async function handleDelete(doc: ProductDocument) {
    if (!confirm(`"${doc.filename}" silinsin mi?`)) return
    setDeletingId(doc.id)
    const res = await deleteProductDocument(doc.id)
    if (res.success) {
      setDocuments((prev) => prev.filter((d) => d.id !== doc.id))
      toast.success('Doküman silindi')
      onChanged()
    } else {
      toast.error(res.error || 'Doküman silinemedi')
    }
    setDeletingId(null)
  }

  function formatSize(bytes: number | null): string {
    if (bytes === null) return '—'
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>
            {product ? `"${product.name}" Dokümanları` : 'Dokümanlar'}
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          {/* Upload area */}
          <div
            className="border-2 border-dashed border-gray-200 rounded-xl p-5 flex flex-col items-center justify-center gap-2 cursor-pointer hover:border-blue-400 hover:bg-blue-50/30 transition-colors"
            onClick={() => !uploading && fileInputRef.current?.click()}
          >
            {uploading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
                <p className="text-sm text-blue-600">Yükleniyor...</p>
              </>
            ) : (
              <>
                <Upload className="w-5 h-5 text-gray-400" />
                <p className="text-sm text-gray-500">Dosya seç veya buraya sürükle</p>
                <p className="text-xs text-gray-400">PDF, Word, Excel, TXT · Maks. 50 MB</p>
              </>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept={DOC_ACCEPT}
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0]
                if (file) {
                  handleUpload(file)
                  e.target.value = ''
                }
              }}
            />
          </div>

          <p className="text-xs text-gray-500">
            Dokümanlar RAG ile işlenir — içerikte bu ürün/hizmet kullanıldığında otomatik referans
            olur.
          </p>

          {/* Document list */}
          {loading ? (
            <div className="flex justify-center py-8">
              <Loader2 className="w-5 h-5 animate-spin text-gray-400" />
            </div>
          ) : documents.length === 0 ? (
            <p className="text-sm text-gray-400 text-center py-6">Henüz doküman yok</p>
          ) : (
            <div className="space-y-2">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg"
                >
                  <FileText className="w-4 h-4 text-gray-400 flex-shrink-0" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium text-gray-900 truncate">{doc.filename}</p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-xs text-gray-500">{formatSize(doc.file_size)}</span>
                      {doc.chunk_count > 0 ? (
                        <Badge variant="secondary" className="text-[10px] bg-emerald-50 text-emerald-700">
                          RAG · {doc.chunk_count} parça
                        </Badge>
                      ) : doc.has_raw_text ? (
                        <Badge variant="secondary" className="text-[10px]">
                          Hazır
                        </Badge>
                      ) : (
                        <Badge variant="secondary" className="text-[10px] bg-amber-50 text-amber-700">
                          İşleniyor
                        </Badge>
                      )}
                    </div>
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-8 w-8 p-0 text-gray-400 hover:text-red-600 hover:bg-red-50"
                    onClick={() => handleDelete(doc)}
                    disabled={deletingId === doc.id}
                  >
                    {deletingId === doc.id ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    ) : (
                      <Trash2 className="w-3.5 h-3.5" />
                    )}
                  </Button>
                </div>
              ))}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
