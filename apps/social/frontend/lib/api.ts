import { createSupabaseClient } from './supabase'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api.otomaix.com'

async function getAuthHeader(): Promise<Record<string, string>> {
  try {
    const supabase = createSupabaseClient()
    const { data } = await supabase.auth.getSession()
    if (!data.session?.access_token) return {}
    return { Authorization: `Bearer ${data.session.access_token}` }
  } catch {
    return {}
  }
}

export interface PlanLimitInfo {
  message: string
  upgrade_url: string
  current_plan: string
}

export type ApiResponse<T> =
  | { success: true; data: T; error?: never; retry_after?: never; plan_limit?: never }
  | {
      success: false
      data?: never
      error: string
      retry_after?: number
      plan_limit?: PlanLimitInfo
    }

function extractErrorMessage(detail: unknown, fallback: string): string {
  if (!detail) return fallback
  if (typeof detail === 'string') return detail
  if (typeof detail === 'object' && detail !== null) {
    const obj = detail as Record<string, unknown>
    if (typeof obj.message === 'string') return obj.message
    if (typeof obj.detail === 'string') return obj.detail
  }
  return fallback
}

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
  try {
    const authHeader = await getAuthHeader()
    const res = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...authHeader,
        ...options.headers,
      },
    })

    if (res.status === 429) {
      const body = await res.json().catch(() => ({}))
      const detail = body.detail || {}
      return {
        success: false,
        error: 'rate_limit',
        retry_after: detail.retry_after ?? 60,
      }
    }

    if (res.status === 402) {
      const body = await res.json().catch(() => ({}))
      const detail = body.detail || {}
      const message =
        typeof detail === 'object' && detail.message
          ? detail.message
          : 'Plan limitine ulaştınız.'
      return {
        success: false,
        error: 'plan_limit_reached',
        plan_limit: {
          message,
          upgrade_url: detail.upgrade_url || '/fiyatlandirma',
          current_plan: detail.current_plan || 'starter',
        },
      }
    }

    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      return {
        success: false,
        error: extractErrorMessage(body.detail, `HTTP ${res.status}`),
      }
    }

    return res.json()
  } catch (err) {
    const msg = err instanceof Error ? err.message : 'Bağlantı hatası'
    return { success: false, error: msg }
  }
}

async function apiUpload<T>(
  path: string,
  formData: FormData
): Promise<ApiResponse<T>> {
  try {
    const authHeader = await getAuthHeader()
    const res = await fetch(`${API_URL}${path}`, {
      method: 'POST',
      headers: authHeader,
      body: formData,
    })

    if (res.status === 429) {
      const body = await res.json().catch(() => ({}))
      const detail = body.detail || {}
      return {
        success: false,
        error: 'rate_limit',
        retry_after: detail.retry_after ?? 60,
      }
    }

    if (res.status === 402) {
      const body = await res.json().catch(() => ({}))
      const detail = body.detail || {}
      const message =
        typeof detail === 'object' && detail.message
          ? detail.message
          : 'Plan limitine ulaştınız.'
      return {
        success: false,
        error: 'plan_limit_reached',
        plan_limit: {
          message,
          upgrade_url: detail.upgrade_url || '/fiyatlandirma',
          current_plan: detail.current_plan || 'starter',
        },
      }
    }

    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      return {
        success: false,
        error: extractErrorMessage(body.detail, `HTTP ${res.status}`),
      }
    }

    return res.json()
  } catch (err) {
    const msg = err instanceof Error ? err.message : 'Bağlantı hatası'
    return { success: false, error: msg }
  }
}

export const api = {
  get: <T>(path: string) => apiFetch<T>(path),
  post: <T>(path: string, body: unknown) =>
    apiFetch<T>(path, { method: 'POST', body: JSON.stringify(body) }),
  patch: <T>(path: string, body: unknown) =>
    apiFetch<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),
  put: <T>(path: string, body: unknown) =>
    apiFetch<T>(path, { method: 'PUT', body: JSON.stringify(body) }),
  delete: <T>(path: string) => apiFetch<T>(path, { method: 'DELETE' }),
  upload: <T>(path: string, formData: FormData) => apiUpload<T>(path, formData),
}
