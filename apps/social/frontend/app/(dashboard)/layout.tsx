'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { createSupabaseClient } from '@/lib/supabase'
import { useAppStore, Brand, Workspace, User } from '@/lib/store'
import { Sidebar } from '@/components/layout/Sidebar'
import { analytics } from '@/lib/analytics'

interface InitData {
  user: User & { plan_id: string }
  workspace: Workspace
  brands: Brand[]
}

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const { setUser, setCurrentWorkspace, setBrands, setCurrentBrand } = useAppStore()

  useEffect(() => {
    const supabase = createSupabaseClient()

    async function checkAuth() {
      const { data } = await supabase.auth.getSession()
      if (!data.session?.access_token) {
        console.warn('[auth] No session found, redirecting to login')
        router.push('/login')
        return
      }

      console.log('[auth] Session found, token starts with:', data.session.access_token.slice(0, 20))

      // Token'ı direkt kullan — getAuthHeader'a güvenme (timing sorunu olabilir)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.otomaix.com'
      const raw = await fetch(`${apiUrl}/auth/init`, {
        headers: {
          Authorization: `Bearer ${data.session.access_token}`,
          'Content-Type': 'application/json',
        },
      })
      console.log('[auth] /auth/init status:', raw.status)
      const res: { success: boolean; data?: InitData } = await raw.json()
      if (res.success && res.data) {
        const { user, workspace, brands } = res.data
        setUser(user)
        setCurrentWorkspace(workspace)
        setBrands(brands)
        analytics.identify(user.id, {
          email: user.email,
          name: user.name,
          plan: user.plan_id || 'starter',
        })
        // currentBrand yoksa veya artık listede yoksa ilkini seç
        const current = useAppStore.getState().currentBrand
        const stillValid = current && brands.some((b) => b.id === current.id)
        if (!stillValid && brands.length > 0) {
          setCurrentBrand(brands[0])
        }
      }
    }

    checkAuth()

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event: unknown, session: unknown) => {
      if (!session) router.push('/login')  // eslint-disable-line
    })

    return () => subscription.unsubscribe()
  }, []) // eslint-disable-line

  return (
    <div className="flex min-h-screen bg-[#F6F7F9]">
      <Sidebar />
      <main className="ml-[250px] flex-1 overflow-y-auto min-h-screen">
        {children}
      </main>
    </div>
  )
}
