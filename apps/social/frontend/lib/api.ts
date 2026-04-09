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

async function apiFetch<T>(
  path: string,
  options: RequestInit = {}
): Promise<{ success: boolean; data?: T; error?: string }> {
  const authHeader = await getAuthHeader()
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...authHeader,
      ...options.headers,
    },
  })
  return res.json()
}

async function apiUpload<T>(
  path: string,
  formData: FormData
): Promise<{ success: boolean; data?: T; error?: string }> {
  const authHeader = await getAuthHeader()
  const res = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: authHeader,
    body: formData,
  })
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
