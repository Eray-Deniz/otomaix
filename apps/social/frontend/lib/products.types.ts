export type ProductType = "product" | "service"

// Sprint 1 (Çoklu Ürün Görseli) — ürünün her bir görseli için tek satır.
// is_primary=true olan satır brand_products.image_url ile denormalize senkron.
export interface ProductImage {
  id: string
  product_id: string
  image_url: string
  image_key: string
  is_primary: boolean
  position: number
  label: string | null
  mime_type: string | null
  size_kb: number | null
  created_at: string
}

export interface Product {
  id: string
  brand_id: string
  type: ProductType
  name: string
  description: string | null
  tags: string[]
  // Ana görsel (denormalize) — is_primary=true satırın kopyası; tek görsel
  // konumlarında (liste thumbnail vb.) kullanılır.
  image_url: string | null
  image_key: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  document_count: number
  // Sprint 1 — ürünün tüm görselleri (is_primary önce, sonra position'a göre).
  // Backend response'unda her zaman gelir (boş ürünlerde []).
  images: ProductImage[]
}

export interface ProductDocument {
  id: string
  product_id: string
  filename: string
  file_url: string
  file_key: string
  file_type: string | null
  file_size: number | null
  created_at: string
  has_raw_text: boolean
  chunk_count: number
}

export interface ProductCreatePayload {
  brand_id: string
  type: ProductType
  name: string
  description?: string | null
  tags?: string[]
  is_active?: boolean
}

export interface ProductUpdatePayload {
  name?: string
  description?: string | null
  tags?: string[]
  is_active?: boolean
}
