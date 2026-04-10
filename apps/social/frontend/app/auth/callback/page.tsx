'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { createSupabaseClient } from '@/lib/supabase'

export default function AuthCallbackPage() {
  const router = useRouter()

  useEffect(() => {
    const supabase = createSupabaseClient()

    // Supabase hash fragment'taki token'ı işler ve session kurar
    supabase.auth.getSession().then(({ data }) => {
      if (data.session) {
        router.replace('/dashboard')
      } else {
        // Biraz bekleyip tekrar dene (hash işlenmesi zaman alabilir)
        setTimeout(async () => {
          const { data: retryData } = await supabase.auth.getSession()
          if (retryData.session) {
            router.replace('/dashboard')
          } else {
            router.replace('/login')
          }
        }, 500)
      }
    })
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
