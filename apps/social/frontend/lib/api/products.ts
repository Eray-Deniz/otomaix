// Phase 9 — Sprint 8: /products + /product-documents API client
// Sprint 1 (Çoklu Görsel) — yeni /products/{id}/images endpoint'leri
//
// Backend endpoints:
//   POST   /products                                (create; 30/hr rate limit; 402 plan_limit)
//   GET    /products?brand_id=&type=&active=        (list — response.products[].images: [])
//   GET    /products/{id}                           (detail — response.images: [])
//   PATCH  /products/{id}                           (update; type immutable)
//   DELETE /products/{id}                           (hard delete + R2 cleanup)
//   POST   /products/{id}/image                     (DEPRECATED — eski tek görsel, içerden senkron)
//   GET    /products/{id}/images                    (Sprint 1 — list)
//   POST   /products/{id}/images                    (Sprint 1 — upload, max 5)
//   DELETE /products/{id}/images/{image_id}         (Sprint 1 — sil + R2 cleanup)
//   PATCH  /products/{id}/images/{image_id}/primary (Sprint 1 — ana görsel değiştir)
//   PATCH  /products/{id}/images/reorder            (Sprint 1 — drag-drop sıra batch update)
//   POST   /product-documents                       (multipart doc upload; product_id + file)
//   GET    /product-documents?product_id=           (list)
//   GET    /product-documents/{id}                  (detail)
//   DELETE /product-documents/{id}                  (cascade chunks + R2 cleanup)

import * as Sentry from '@sentry/nextjs'
import { api, type ApiResponse } from '@/lib/api'
import type {
  Product,
  ProductCreatePayload,
  ProductDocument,
  ProductImage,
  ProductType,
  ProductUpdatePayload,
} from '@/lib/products.types'

interface ProductsListResponse {
  products: Product[]
  count: number
}

interface ProductDocumentsListResponse {
  documents: ProductDocument[]
  count: number
}

export async function fetchProducts(
  brandId: string,
  filters?: { type?: ProductType; active?: boolean }
): Promise<ApiResponse<ProductsListResponse>> {
  const query = new URLSearchParams({ brand_id: brandId })
  if (filters?.type) query.set('type', filters.type)
  if (filters?.active !== undefined) query.set('active', String(filters.active))
  const res = await api.get<ProductsListResponse>(`/products?${query.toString()}`)
  if (res.success && !Array.isArray((res.data as ProductsListResponse)?.products)) {
    Sentry.captureMessage('products list response shape mismatch', {
      level: 'error',
      extra: { endpoint: '/products', data: res.data },
    })
  }
  return res
}

export async function fetchProduct(productId: string): Promise<ApiResponse<Product>> {
  return api.get<Product>(`/products/${productId}`)
}

export async function createProduct(
  payload: ProductCreatePayload
): Promise<ApiResponse<Product>> {
  return api.post<Product>('/products', payload)
}

export async function updateProduct(
  productId: string,
  payload: ProductUpdatePayload
): Promise<ApiResponse<Product>> {
  return api.patch<Product>(`/products/${productId}`, payload)
}

export async function deleteProduct(
  productId: string
): Promise<ApiResponse<{ deleted: boolean; id: string }>> {
  return api.delete<{ deleted: boolean; id: string }>(`/products/${productId}`)
}

/**
 * @deprecated Sprint 1 — yeni `uploadProductImage` (çoklu görsel, /images endpoint'i) kullanın.
 * Bu fonksiyon eski tek görsel davranışı için kalır: çağrıldığında ürünün TÜM görsellerini
 * silip yenisini ana görsel olarak ekler. Geriye dönük uyumluluk için backend'de duruyor.
 */
export async function uploadProductImageLegacy(
  productId: string,
  file: File
): Promise<ApiResponse<Product>> {
  const form = new FormData()
  form.append('file', file)
  return api.upload<Product>(`/products/${productId}/image`, form)
}

// Sprint 1 (Çoklu Görsel) — yeni endpoint'ler

interface ProductImagesListResponse {
  items: ProductImage[]
  count: number
  max: number
}

export async function fetchProductImages(
  productId: string
): Promise<ApiResponse<ProductImagesListResponse>> {
  return api.get<ProductImagesListResponse>(`/products/${productId}/images`)
}

/** Yeni görsel ekle (max 5 — backend 422 dönerse limit aşıldı). İlk görsel otomatik ana görsel olur. */
export async function uploadProductImage(
  productId: string,
  file: File
): Promise<ApiResponse<ProductImage>> {
  const form = new FormData()
  form.append('file', file)
  return api.upload<ProductImage>(`/products/${productId}/images`, form)
}

export async function deleteProductImage(
  productId: string,
  imageId: string
): Promise<ApiResponse<{ deleted: boolean; id: string }>> {
  return api.delete<{ deleted: boolean; id: string }>(
    `/products/${productId}/images/${imageId}`
  )
}

export async function setProductImagePrimary(
  productId: string,
  imageId: string
): Promise<ApiResponse<{ updated: boolean; primary_id: string }>> {
  return api.patch<{ updated: boolean; primary_id: string }>(
    `/products/${productId}/images/${imageId}/primary`,
    {}
  )
}

export async function reorderProductImages(
  productId: string,
  imageIds: string[]
): Promise<ApiResponse<{ reordered: boolean; count: number }>> {
  return api.patch<{ reordered: boolean; count: number }>(
    `/products/${productId}/images/reorder`,
    { image_ids: imageIds }
  )
}

export async function fetchProductDocuments(
  productId: string
): Promise<ApiResponse<ProductDocumentsListResponse>> {
  const query = new URLSearchParams({ product_id: productId })
  const res = await api.get<ProductDocumentsListResponse>(
    `/product-documents?${query.toString()}`
  )
  if (res.success && !Array.isArray((res.data as ProductDocumentsListResponse)?.documents)) {
    Sentry.captureMessage('product-documents list response shape mismatch', {
      level: 'error',
      extra: { endpoint: '/product-documents', data: res.data },
    })
  }
  return res
}

export async function uploadProductDocument(
  productId: string,
  file: File
): Promise<ApiResponse<ProductDocument>> {
  const form = new FormData()
  form.append('product_id', productId)
  form.append('file', file)
  return api.upload<ProductDocument>('/product-documents', form)
}

export async function deleteProductDocument(
  documentId: string
): Promise<ApiResponse<{ deleted: boolean; id: string }>> {
  return api.delete<{ deleted: boolean; id: string }>(
    `/product-documents/${documentId}`
  )
}
