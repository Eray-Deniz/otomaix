'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { createSupabaseClient } from '@/lib/supabase'
import { useAppStore, Brand, Workspace, User } from '@/lib/store'
import { api } from '@/lib/api'
import { Sidebar } from '@/components/layout/Sidebar'

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
  const { setUser, setCurrentWorkspace, setBrands, setCurrentBrand, currentBrand } = useAppStore()

  useEffect(() => {
    const supabase = createSupabaseClient()

    async function checkAuth() {
      const { data } = await supabase.auth.getSession()
      if (!data.session) {
        router.push('/login')
        return
      }

      const res = await api.get<InitData>('/auth/init')
      if (res.success && res.data) {
        const { user, workspace, brands } = res.data
        setUser(user)
        setCurrentWorkspace(workspace)
        setBrands(brands)
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
