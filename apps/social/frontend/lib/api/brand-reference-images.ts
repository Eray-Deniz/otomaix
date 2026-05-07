// Sprint 3 (Özel Gün) — Marka referans görseli API client
// Backend endpoints:
//   POST   /brand-reference-images           (multipart upload; brand_id, file, label?, save_to_library)
//   GET    /brand-reference-images?brand_id= (list)
//   DELETE /brand-reference-images/{id}      (delete + R2 cleanup)

import { api, type ApiResponse } from '@/lib/api'

export interface BrandReferenceImage {
  id: string
  brand_id: string
  image_url: string
  image_key: string
  label: string | null
  mime_type: string | null
  size_kb: number | null
  created_at: string
}

interface ReferenceImagesListResponse {
  items: BrandReferenceImage[]
  count: number
  max: number
}

interface TemporaryUploadResponse {
  image_url: string
  image_key: string
  saved: false
}

export async function fetchReferenceImages(
  brandId: string
): Promise<ApiResponse<ReferenceImagesListResponse>> {
  const query = new URLSearchParams({ brand_id: brandId })
  return api.get<ReferenceImagesListResponse>(`/brand-reference-images?${query.toString()}`)
}

/** Kütüphaneye kaydederek yükler (DB + R2). */
export async function uploadReferenceImageToLibrary(
  brandId: string,
  file: File,
  label?: string
): Promise<ApiResponse<BrandReferenceImage>> {
  const form = new FormData()
  form.append('brand_id', brandId)
  form.append('file', file)
  form.append('save_to_library', 'true')
  if (label) form.append('label', label)
  return api.upload<BrandReferenceImage>('/brand-reference-images', form)
}

/** Tek seferlik yükler — yalnız R2'ye yazılır, DB kayıt yok. */
export async function uploadReferenceImageTemporary(
  brandId: string,
  file: File
): Promise<ApiResponse<TemporaryUploadResponse>> {
  const form = new FormData()
  form.append('brand_id', brandId)
  form.append('file', file)
  form.append('save_to_library', 'false')
  return api.upload<TemporaryUploadResponse>('/brand-reference-images', form)
}

export async function deleteReferenceImage(
  refId: string
): Promise<ApiResponse<{ deleted: boolean }>> {
  return api.delete<{ deleted: boolean }>(`/brand-reference-images/${refId}`)
}
