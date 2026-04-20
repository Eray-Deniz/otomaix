// Phase 7 — Sprint 2: /templates API client
// Backend: GET /templates (public, 1hr cache), GET /templates/{id}
// Query params: sector, content_type
// Frontend ile birebir camelCase JSON transport.

import { api } from '@/lib/api'
import type { Template } from '@/lib/templates.types'

interface TemplatesListResponse {
  templates: Template[]
  version: string
  count: number
}

export async function fetchTemplates(params?: {
  sector?: string
  contentType?: string
}): Promise<Template[]> {
  const query = new URLSearchParams()
  if (params?.sector) query.set('sector', params.sector)
  if (params?.contentType) query.set('content_type', params.contentType)
  const queryString = query.toString()
  const path = `/templates${queryString ? `?${queryString}` : ''}`
  const res = await api.get<TemplatesListResponse>(path)
  return res.success ? res.data.templates : []
}

export async function fetchTemplateById(templateId: string): Promise<Template | null> {
  const res = await api.get<Template>(`/templates/${templateId}`)
  return res.success ? res.data : null
}
