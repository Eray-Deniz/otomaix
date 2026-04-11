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

export type ApiResponse<T> =
  | { success: true; data: T; error?: never; retry_after?: never }
  | { success: false; data?: never; error: string; retry_after?: number }

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<ApiResponse<T>> {
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

  return res.json()
}

async function apiUpload<T>(
  path: string,
  formData: FormData
): Promise<ApiResponse<T>> {
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

  return res.json()
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
