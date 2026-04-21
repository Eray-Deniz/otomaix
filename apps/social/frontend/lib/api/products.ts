// Phase 9 — Sprint 8: /products + /product-documents API client
// Backend endpoints:
//   POST   /products                          (create; 30/hr rate limit; 402 plan_limit)
//   GET    /products?brand_id=&type=&active=  (list)
//   GET    /products/{id}                     (detail)
//   PATCH  /products/{id}                     (update; type immutable)
//   DELETE /products/{id}                     (hard delete + R2 cleanup)
//   POST   /products/{id}/image               (multipart image upload, max 10MB)
//   POST   /product-documents                 (multipart doc upload; product_id + file)
//   GET    /product-documents?product_id=     (list)
//   GET    /product-documents/{id}            (detail)
//   DELETE /product-documents/{id}            (cascade chunks + R2 cleanup)

import * as Sentry from '@sentry/nextjs'
import { api, type ApiResponse } from '@/lib/api'
import type {
  Product,
  ProductCreatePayload,
  ProductDocument,
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

export async function uploadProductImage(
  productId: string,
  file: File
): Promise<ApiResponse<Product>> {
  const form = new FormData()
  form.append('file', file)
  return api.upload<Product>(`/products/${productId}/image`, form)
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
