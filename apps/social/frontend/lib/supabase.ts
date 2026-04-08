import { createClient, type SupabaseClient } from '@supabase/supabase-js'

let _client: SupabaseClient | null = null

export function createSupabaseClient(): SupabaseClient {
  // During SSR/build, return a no-op placeholder to avoid key validation errors.
  // Real auth calls happen only on the client side (inside effects/handlers).
  if (typeof window === 'undefined') {
    return {
      auth: {
        getSession: async () => ({ data: { session: null }, error: null }),
        signInWithOAuth: async () => ({ data: null, error: null }),
        signInWithPassword: async () => ({ data: null, error: null }),
        signOut: async () => ({ error: null }),
        onAuthStateChange: () => ({ data: { subscription: { unsubscribe: () => {} } } }),
      },
    } as unknown as SupabaseClient
  }

  if (_client) return _client

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL!
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!

  _client = createClient(supabaseUrl, supabaseAnonKey, {
    auth: {
      persistSession: true,
      autoRefreshToken: true,
    },
  })

  return _client
}
