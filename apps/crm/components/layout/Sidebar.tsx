'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { logout } from '@/app/actions'
import {
  LayoutDashboard,
  Users,
  AlertTriangle,
  BarChart3,
  Bell,
  LogOut,
} from 'lucide-react'

const navItems = [
  { href: '/', label: 'Genel Bakış', icon: LayoutDashboard },
  { href: '/musteriler', label: 'Müşteriler', icon: Users },
  { href: '/operasyon', label: 'Operasyon', icon: AlertTriangle },
  { href: '/raporlar', label: 'Raporlar', icon: BarChart3 },
  { href: '/bildirimler', label: 'Bildirimler', icon: Bell },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside
      className="fixed left-0 top-0 h-full flex flex-col"
      style={{ width: 200, background: '#1a1a2e', borderRight: '1px solid #2a2a4a' }}
    >
      {/* Logo */}
      <div className="px-4 py-5 border-b border-[#2a2a4a]">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 bg-blue-500 rounded-md flex items-center justify-center flex-shrink-0">
            <span className="text-white font-bold text-xs">O</span>
          </div>
          <div>
            <div className="text-white font-semibold text-sm leading-none">Otomaix</div>
            <div className="text-[#4a5568] text-[10px] mt-0.5">CRM Admin</div>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-4 space-y-0.5">
        {navItems.map(({ href, label, icon: Icon }) => {
          const isActive =
            href === '/' ? pathname === '/' : pathname.startsWith(href)

          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors ${
                isActive
                  ? 'bg-[#0f3460] text-white'
                  : 'text-[#a8b2d8] hover:bg-[#16213e] hover:text-white'
              }`}
            >
              <Icon size={15} className="flex-shrink-0" />
              {label}
            </Link>
          )
        })}
      </nav>

      {/* Logout */}
      <div className="px-2 py-4 border-t border-[#2a2a4a]">
        <form action={logout}>
          <button
            type="submit"
            className="flex items-center gap-2.5 w-full px-3 py-2 rounded-lg text-sm text-[#a8b2d8] hover:bg-[#16213e] hover:text-white transition-colors"
          >
            <LogOut size={15} />
            Çıkış Yap
          </button>
        </form>
      </div>
    </aside>
  )
}
