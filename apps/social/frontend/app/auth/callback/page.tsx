'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { createSupabaseClient } from '@/lib/supabase'

export default function AuthCallbackPage() {
  const router = useRouter()

  useEffect(() => {
    const supabase = createSupabaseClient()

    // Hash fragment işlenince SIGNED_IN eventi tetiklenir
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (session) {
        router.replace('/dashboard')
      }
    })

    // Zaten oturum açıksa direkt yönlendir
    supabase.auth.getSession().then(({ data }) => {
      if (data.session) {
        router.replace('/dashboard')
      }
    })

    return () => subscription.unsubscribe()
  }, [router])

  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
        <p className="text-sm text-gray-500">Giriş yapılıyor...</p>
      </div>
    </div>
  )
}
