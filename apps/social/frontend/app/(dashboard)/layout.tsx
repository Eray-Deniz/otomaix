'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { createSupabaseClient } from '@/lib/supabase'
import { useAppStore } from '@/lib/store'
import { api } from '@/lib/api'
import { Sidebar } from '@/components/layout/Sidebar'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const setUser = useAppStore((s) => s.setUser)

  useEffect(() => {
    const supabase = createSupabaseClient()

    async function checkAuth() {
      const { data } = await supabase.auth.getSession()
      if (!data.session) {
        router.push('/login')
        return
      }
      const res = await api.get<{ id: string; email: string; name: string }>('/auth/me')
      if (res.success && res.data) {
        setUser(res.data)
      }
    }

    checkAuth()

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event: unknown, session: unknown) => {
      if (!session) router.push('/login')  // eslint-disable-line
    })

    return () => subscription.unsubscribe()
  }, [router, setUser])

  return (
    <div className="flex min-h-screen bg-[#F6F7F9]">
      <Sidebar />
      <main className="ml-[250px] flex-1 overflow-y-auto min-h-screen">
        {children}
      </main>
    </div>
  )
}
