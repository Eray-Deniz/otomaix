export type ProductType = "product" | "service"

export interface Product {
  id: string
  brand_id: string
  type: ProductType
  name: string
  description: string | null
  tags: string[]
  image_url: string | null
  image_key: string | null
  is_active: boolean
  created_at: string
  updated_at: string
  document_count: number
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
