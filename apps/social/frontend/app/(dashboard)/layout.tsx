'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import * as Sentry from '@sentry/nextjs'
import { createSupabaseClient } from '@/lib/supabase'
import { useAppStore, Brand, Workspace, User } from '@/lib/store'
import { Sidebar } from '@/components/layout/Sidebar'
import { analytics } from '@/lib/analytics'
import { crispIdentify } from '@/components/providers/CrispProvider'

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
    let initDone = false

    async function doInit(token: string) {
      if (initDone) return
      initDone = true

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'https://api.otomaix.com'
      const raw = await fetch(`${apiUrl}/auth/init`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })
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
        Sentry.setUser({ id: user.id, email: user.email })
        crispIdentify({
          id: user.id,
          email: user.email,
          name: user.name,
          plan_id: user.plan_id,
          brands_count: brands.length,
        })
        const current = useAppStore.getState().currentBrand
        const stillValid = current && brands.some((b) => b.id === current.id)
        if (!stillValid && brands.length > 0) {
          setCurrentBrand(brands[0])
        }
      }
    }

    // onAuthStateChange mevcut session varsa mount anında INITIAL_SESSION ile ateşlenir,
    // Google OAuth sonrası için de SIGNED_IN ile çalışır — getSession() race condition'ı olmaz.
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!session) {
        router.push('/login')
      } else {
        doInit(session.access_token)
      }
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
