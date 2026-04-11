'use client'

import { useEffect, useState } from 'react'
import { SidebarNav } from './SidebarNav'
import { BrandSwitcher } from './BrandSwitcher'
import { createSupabaseClient } from '@/lib/supabase'
import { useRouter } from 'next/navigation'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { useAppStore } from '@/lib/store'
import { LogOut } from 'lucide-react'
import Link from 'next/link'
import { analytics } from '@/lib/analytics'

function TrialBanner({ trialEndsAt }: { trialEndsAt: string }) {
  // Date.now() must run client-side only — avoid SSR/hydration mismatch
  const [daysLeft, setDaysLeft] = useState<number | null>(null)
  useEffect(() => {
    setDaysLeft(Math.max(
      0,
      Math.ceil((new Date(trialEndsAt).getTime() - Date.now()) / (1000 * 60 * 60 * 24))
    ))
  }, [trialEndsAt])
  if (daysLeft === null || daysLeft <= 0) return null
  return (
    <Link
      href="/fiyatlandirma"
      className="mx-3 mb-2 flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-lg px-3 py-2 hover:bg-amber-100 transition-colors"
    >
      <span className="text-base">🎁</span>
      <div className="min-w-0">
        <p className="text-xs font-semibold text-amber-800 leading-tight">
          Deneme: {daysLeft} gün kaldı
        </p>
        <p className="text-xs text-amber-600 leading-tight">Plan seç →</p>
      </div>
    </Link>
  )
}

export function Sidebar() {
  const router = useRouter()
  const user = useAppStore((s) => s.user)

  async function handleLogout() {
    analytics.reset()
    const supabase = createSupabaseClient()
    await supabase.auth.signOut()
    router.push('/login')
  }

  return (
    <aside className="w-[250px] flex-shrink-0 h-screen flex flex-col bg-white border-r border-gray-100 shadow-sm fixed left-0 top-0">
      {/* Logo */}
      <div className="px-5 py-4 border-b border-gray-100">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">O</span>
          </div>
          <div>
            <span className="font-bold text-gray-900 text-sm">Otomaix</span>
            <span className="block text-xs text-gray-400">Social</span>
          </div>
        </div>
      </div>

      {/* Brand Switcher */}
      <BrandSwitcher />

      {/* Trial Banner */}
      {user?.trial_ends_at && <TrialBanner trialEndsAt={user.trial_ends_at} />}

      {/* Nav */}
      <SidebarNav />

      {/* User */}
      <div className="px-3 py-4 border-t border-gray-100">
        <div className="flex items-center gap-3 px-3 py-2">
          <Avatar className="w-8 h-8">
            <AvatarFallback className="text-xs bg-blue-100 text-blue-700">
              {user?.name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || 'U'}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {user?.name || user?.email || 'Kullanıcı'}
            </p>
            <p className="text-xs text-gray-400 truncate">{user?.email}</p>
          </div>
          <button
            onClick={handleLogout}
            className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-md transition-colors"
            title="Çıkış Yap"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  )
}
